# PCE Memory API Reference

## Core Tools

### pce_memory_observe

Record temporary observation with auto-expiry.

```
observe(
  source_type: "chat" | "tool" | "file" | "http" | "system",
  content: string,
  source_id?: string,
  ttl_days?: number,        # default: 30
  boundary_class?: "public" | "internal" | "pii" | "secret",
  tags?: string[],
  extract?: { mode: "noop" | "single_claim_v0" }
)
```

**Extract modes:**
- `noop`: Keep as temporary observation
- `single_claim_v0`: Promote to permanent claim

### pce_memory_upsert

Register permanent knowledge claim.

```
upsert(
  text: string,
  kind: "fact" | "preference" | "task" | "policy_hint",
  scope: "session" | "project" | "principle",
  boundary_class: "public" | "internal" | "pii" | "secret",
  provenance: {
    at: ISO8601,
    actor?: string,
    note?: string,
    git?: { repo, commit, files, url }
  }
)
```

### pce_memory_activate

Retrieve relevant knowledge.

```
activate(
  scope: ["session" | "project" | "principle"],
  allow: string[],          # e.g., ["*"] or ["answer:task"]
  q?: string,               # search query
  top_k?: number            # max results (default: 10, max: 50)
)
```

### pce_memory_feedback

Report knowledge quality.

```
feedback(
  claim_id: string,
  signal: "helpful" | "harmful" | "outdated" | "duplicate",
  score?: number            # -1 to 1
)
```

## Provenance Best Practices

Always include file hash for verifiable claims:

```
provenance: {
  at: "2025-01-01T00:00:00Z",
  actor: "claude-opus",
  note: "Extracted from plugin.json",
  file_hash: "sha256:abc123...",
  source_file: "plugin.json"
}
```

## Boundary Classes

| Class | Description | Auto-redaction |
|-------|-------------|----------------|
| public | Safe to share | No |
| internal | Internal use | No |
| pii | Personal data | Yes (emails, etc.) |
| secret | Credentials | Yes |

## Tags Convention

- `unverified` - Initial observation, not yet validated
- `verified` - Cross-validated by second model
- `project-info` - Project metadata
- `architecture` - Code structure
- `dependencies` - Package dependencies
- `config` - Configuration files
- `api` - API definitions
