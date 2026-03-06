#!/bin/bash
# secret-scan.sh - Scan for secret files without exposing their values
# Output: CSV format (path,type,modified,permissions,deny_rule_exists)
# IMPORTANT: This script NEVER outputs secret values

set -euo pipefail

INCLUDE_HOME=false
SETTINGS_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --include-home) INCLUDE_HOME=true; shift ;;
    --settings) SETTINGS_FILE="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--include-home] [--settings <path>]"
      echo "  --include-home  Also scan home directory credential stores"
      echo "  --settings      Path to .claude/settings.json for deny rule check"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Collect all settings files (Claude Code merges them hierarchically)
SETTINGS_FILES=()
if [ -n "$SETTINGS_FILE" ]; then
  SETTINGS_FILES+=("$SETTINGS_FILE")
else
  for candidate in .claude/settings.json .claude/settings.local.json; do
    if [ -f "$candidate" ]; then
      SETTINGS_FILES+=("$candidate")
    fi
  done
fi

# Get file modification date (portable: macOS + Linux)
get_mtime() {
  local file="$1"
  if stat -f "%Sm" -t "%Y-%m-%d" "$file" 2>/dev/null; then
    return
  fi
  stat -c "%y" "$file" 2>/dev/null | cut -d' ' -f1 || echo "unknown"
}

# Get file permissions (portable)
get_perms() {
  local file="$1"
  if stat -f "%Lp" "$file" 2>/dev/null; then
    return
  fi
  stat -c "%a" "$file" 2>/dev/null || echo "unknown"
}

# Check if a deny rule likely covers this path (Read-only check)
# Searches all collected settings files (hierarchical merge)
# Only reports "yes" if a Read(...) deny rule covers the file
check_deny_rule() {
  local filepath="$1"

  if [ ${#SETTINGS_FILES[@]} -eq 0 ]; then
    echo "no-settings"
    return
  fi

  # Use python3 for accurate deny rule matching
  # Pass settings files via arguments to avoid shell injection
  python3 - "$filepath" "${SETTINGS_FILES[@]}" <<'PYEOF'
import json, sys, fnmatch, os

filepath = sys.argv[1]
settings_files = sys.argv[2:]

# Collect all Read(...) deny rules
read_rules = []
for sf in settings_files:
    try:
        with open(sf) as f:
            d = json.load(f)
        for rule in d.get("permissions", {}).get("deny", []):
            if rule.startswith("Read(") and rule.endswith(")"):
                pattern = rule[5:-1]
                read_rules.append(pattern)
    except Exception:
        continue

if not read_rules:
    print("no-settings")
    sys.exit(0)

basename = os.path.basename(filepath)

# Normalize filepath: strip leading ./ for comparison
norm_filepath = filepath.lstrip("./")

for pattern in read_rules:
    norm_pattern = pattern.lstrip("./")
    # Direct fnmatch against basename, filepath, and normalized forms
    if fnmatch.fnmatch(basename, pattern):
        print("yes")
        sys.exit(0)
    if fnmatch.fnmatch(filepath, pattern):
        print("yes")
        sys.exit(0)
    if fnmatch.fnmatch(norm_filepath, norm_pattern):
        print("yes")
        sys.exit(0)
    # Handle ** glob patterns (e.g., **/.env, **/secrets/**)
    if "**" in pattern:
        # Strip leading **/ and match against filepath
        stripped = pattern.lstrip("*").lstrip("/")
        if fnmatch.fnmatch(filepath, "*/" + stripped) or fnmatch.fnmatch(filepath, "./" + stripped):
            print("yes")
            sys.exit(0)
        if fnmatch.fnmatch(basename, stripped):
            print("yes")
            sys.exit(0)
    # Handle ./ prefix patterns (e.g., ./.env)
    if pattern.startswith("./"):
        if fnmatch.fnmatch(filepath, pattern):
            print("yes")
            sys.exit(0)

print("no")
PYEOF
}

# Classify file type (uses full path for disambiguation)
classify_file() {
  local filepath="$1"
  local basename
  basename=$(basename "$filepath")
  local dirpath
  dirpath=$(dirname "$filepath")

  # Use full path context for ambiguous basenames
  case "$filepath" in
    */.ssh/config) echo "ssh-config"; return ;;
    */.ssh/id_*) echo "ssh-key"; return ;;
    */.aws/credentials) echo "aws-credentials"; return ;;
    */.aws/config) echo "aws-config"; return ;;
    */.config/gh/hosts.yml) echo "gh-config"; return ;;
    */.docker/config.json) echo "docker-config"; return ;;
    */.kube/config) echo "kube-config"; return ;;
  esac

  case "$basename" in
    .env|.env.*|*.env) echo "env-file" ;;
    *.pem) echo "pem-certificate" ;;
    *.p12|*.pfx) echo "pkcs12-keystore" ;;
    *.key) echo "private-key" ;;
    credentials.json) echo "cloud-credentials" ;;
    service-account*.json) echo "service-account" ;;
    .npmrc) echo "npm-config" ;;
    .netrc) echo "netrc" ;;
    .pypirc) echo "pypi-config" ;;
    secrets.yml|secrets.yaml) echo "config-secret" ;;
    id_rsa|id_ed25519|id_ecdsa|id_dsa) echo "ssh-key" ;;
    hosts.yml) echo "gh-config" ;;
    config.json) echo "docker-config" ;;
    *) echo "unknown" ;;
  esac
}

# Header
echo "path,type,modified,permissions,deny_rule_exists"

# Scan repository
if [ -d "." ]; then
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    mtime=$(get_mtime "$file")
    perms=$(get_perms "$file")
    ftype=$(classify_file "$file")
    deny=$(check_deny_rule "$file")
    echo "\"$file\",$ftype,$mtime,$perms,$deny"
  done < <(find . -maxdepth 4 \( \
    -name ".env" -o -name ".env.*" -o -name "*.env" \
    -o -name "*.pem" -o -name "*.p12" -o -name "*.pfx" -o -name "*.key" \
    -o -name "credentials.json" -o -name "service-account*.json" \
    -o -name ".npmrc" -o -name ".netrc" -o -name ".pypirc" \
    -o -name "secrets.yml" -o -name "secrets.yaml" \
  \) -not -path "./.git/*" -not -path "./node_modules/*" \
     -not -path "./.venv/*" -not -path "./vendor/*" \
     -not -path "./dist/*" -not -path "./build/*" 2>/dev/null | sort)
fi

# Scan home directory (opt-in only)
if [ "$INCLUDE_HOME" = true ]; then
  HOME_PATHS=(
    "$HOME/.ssh/id_rsa"
    "$HOME/.ssh/id_ed25519"
    "$HOME/.ssh/id_ecdsa"
    "$HOME/.ssh/config"
    "$HOME/.aws/credentials"
    "$HOME/.aws/config"
    "$HOME/.config/gh/hosts.yml"
    "$HOME/.docker/config.json"
    "$HOME/.npmrc"
    "$HOME/.netrc"
    "$HOME/.pypirc"
    "$HOME/.kube/config"
  )

  for file in "${HOME_PATHS[@]}"; do
    if [ -f "$file" ]; then
      mtime=$(get_mtime "$file")
      perms=$(get_perms "$file")
      ftype=$(classify_file "$file")
      deny=$(check_deny_rule "$file")
      echo "\"$file\",$ftype,$mtime,$perms,$deny"
    fi
  done
fi
