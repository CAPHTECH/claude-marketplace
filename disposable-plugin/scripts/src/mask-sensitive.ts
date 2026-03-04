/**
 * mask-sensitive.ts — Regex-based sensitive data masking
 *
 * Usage: node dist/mask-sensitive.mjs <input.json> [-o <output.json>]
 */
import { readFileSync, writeFileSync } from "node:fs";

interface MaskPattern {
  name: string;
  pattern: RegExp;
  category: string;
}

const PATTERNS: MaskPattern[] = [
  {
    name: "Bearer token",
    pattern: /Bearer\s+[^\s"',}]+/gi,
    category: "token",
  },
  {
    name: "API key parameter (double-quoted)",
    pattern: /(["']?(?:api_key|apikey|api-key|secret|token|password|passwd|auth)["']?\s*[:=]\s*")(?:[^"\\]|\\.)*(")/gi,
    category: "credential",
  },
  {
    name: "API key parameter (single-quoted)",
    pattern: /(["']?(?:api_key|apikey|api-key|secret|token|password|passwd|auth)["']?\s*[:=]\s*')(?:[^'\\]|\\.)*(')/gi,
    category: "credential",
  },
  {
    name: "API key parameter (unquoted)",
    pattern: /(["']?(?:api_key|apikey|api-key|secret|token|password|passwd|auth)["']?\s*[:=]\s*)[^\s"',}]+()/gi,
    category: "credential",
  },
  {
    name: "Connection string with credentials",
    pattern: /[a-z][a-z0-9+.-]{0,30}:\/\/[^:@]*:[^@]+@[^\s"',}]+/gi,
    category: "connection-string",
  },
  {
    name: "AWS access key",
    pattern: /AKIA[0-9A-Z]{16}/g,
    category: "aws-key",
  },
  {
    name: "Generic long secret (double-quoted)",
    pattern: /((?:SECRET|TOKEN|KEY|PASSWORD|CREDENTIAL)[_\s]*[=:]\s*")(?:[^"\\]|\\.){20,}(")/gi,
    category: "secret",
  },
  {
    name: "Generic long secret (single-quoted)",
    pattern: /((?:SECRET|TOKEN|KEY|PASSWORD|CREDENTIAL)[_\s]*[=:]\s*')(?:[^'\\]|\\.){20,}(')/gi,
    category: "secret",
  },
  {
    name: "Generic long secret (unquoted)",
    pattern: /((?:SECRET|TOKEN|KEY|PASSWORD|CREDENTIAL)[_\s]*[=:]\s*)[^\s"',}]{20,}()/gi,
    category: "secret",
  },
];

const EXACT_REDACTED = /^\[REDACTED:[a-z-]+\]$/;

/** Replace PEM private key blocks using indexOf-based linear scan (avoids regex ReDoS). */
function maskPemBlocks(text: string): { result: string; count: number } {
  const BEGIN = "-----BEGIN";
  const END_SUFFIX = "PRIVATE KEY-----";
  let result = "";
  let count = 0;
  let pos = 0;

  while (pos < text.length) {
    const beginIdx = text.indexOf(BEGIN, pos);
    if (beginIdx === -1) {
      result += text.slice(pos);
      break;
    }

    // Find the end of the BEGIN line (look for the closing -----)
    const beginLineEnd = text.indexOf("-----", beginIdx + BEGIN.length);
    if (beginLineEnd === -1 || !text.slice(beginIdx, beginLineEnd + 5).includes(END_SUFFIX)) {
      // Not a PRIVATE KEY begin marker — skip past BEGIN and continue
      result += text.slice(pos, beginIdx + BEGIN.length);
      pos = beginIdx + BEGIN.length;
      continue;
    }

    // Found a valid BEGIN PRIVATE KEY marker — search for matching END
    const afterBegin = beginLineEnd + 5;
    let searchFrom = afterBegin;
    let foundEnd = false;

    while (searchFrom < text.length) {
      const endMarker = text.indexOf("-----END", searchFrom);
      if (endMarker === -1) break;

      const endLineEnd = text.indexOf("-----", endMarker + 8);
      if (endLineEnd !== -1 && text.slice(endMarker, endLineEnd + 5).includes(END_SUFFIX)) {
        // Matching END PRIVATE KEY found
        result += text.slice(pos, beginIdx) + "[REDACTED:private-key]";
        count++;
        pos = endLineEnd + 5;
        foundEnd = true;
        break;
      }
      // Non-matching END — keep searching
      searchFrom = endMarker + 8;
    }

    if (!foundEnd) {
      // No matching END found — mask from BEGIN to end (security-conservative)
      result += text.slice(pos, beginIdx) + "[REDACTED:private-key]";
      count++;
      pos = text.length;
      break;
    }
  }

  return { result, count };
}

export function maskSensitive(text: string): { masked: string; redactionCount: number } {
  let redactionCount = 0;

  // Phase 1: PEM blocks (indexOf-based, O(n))
  const pem = maskPemBlocks(text);
  let masked = pem.result;
  redactionCount += pem.count;

  // Phase 2: Regex-based patterns
  for (const { pattern, category } of PATTERNS) {
    // Reset lastIndex for global regexes
    pattern.lastIndex = 0;
    masked = masked.replace(pattern, (...args) => {
      const fullMatch = args[0] as string;
      const groups = args.slice(1, -2).filter((g) => typeof g === "string");

      // Extract the value portion (what would be masked)
      let valuePart: string;
      if (groups.length >= 2) {
        // Remove prefix (group[0]) and suffix (group[last]) to get value
        valuePart = fullMatch.slice(groups[0].length);
        const suffix = groups[groups.length - 1];
        if (suffix) valuePart = valuePart.slice(0, -suffix.length);
      } else {
        valuePart = fullMatch;
      }

      // Skip only if the value is exactly a prior REDACTED marker (not mixed with real data)
      if (EXACT_REDACTED.test(valuePart)) {
        return fullMatch;
      }

      redactionCount++;
      if (groups.length >= 2) {
        return `${groups[0]}[REDACTED:${category}]${groups[groups.length - 1]}`;
      }
      return `[REDACTED:${category}]`;
    });
  }

  return { masked, redactionCount };
}

export function maskJsonFile(inputPath: string, outputPath?: string): {
  redactionCount: number;
  outputPath: string;
} {
  const content = readFileSync(inputPath, "utf-8");
  const { masked, redactionCount } = maskSensitive(content);
  const out = outputPath ?? inputPath;
  writeFileSync(out, masked);
  return { redactionCount, outputPath: out };
}

// --- CLI ---

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error("Usage: mask-sensitive <input.json> [-o <output.json>] [--in-place]");
    process.exit(1);
  }

  const inputPath = args[0];
  const inPlace = args.includes("--in-place");
  const outputIdx = args.indexOf("-o");
  if (outputIdx >= 0 && (outputIdx + 1 >= args.length || args[outputIdx + 1].startsWith("-"))) {
    console.error("Error: -o requires an output path argument");
    process.exit(1);
  }
  const outputPath = outputIdx >= 0
    ? args[outputIdx + 1]
    : inPlace
      ? undefined  // in-place overwrites input
      : /\.\w+$/.test(inputPath)
        ? inputPath.replace(/(\.\w+)$/, ".masked$1")  // foo.json → foo.masked.json
        : inputPath + ".masked";                        // foo → foo.masked

  try {
    const result = maskJsonFile(inputPath, outputPath);
    console.log(`Masked ${result.redactionCount} sensitive value(s) → ${result.outputPath}`);
  } catch (e) {
    console.error(`Error: ${e instanceof Error ? e.message : e}`);
    process.exit(1);
  }
}

const isMain = process.argv[1]?.endsWith("mask-sensitive.mjs") || process.argv[1]?.endsWith("mask-sensitive.ts");
if (isMain) main();
