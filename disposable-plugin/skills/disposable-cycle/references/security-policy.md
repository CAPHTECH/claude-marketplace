# Security Policy

## Network Access

**All network access is PROHIBITED** during disposable cycles.

- No `curl`, `wget`, `fetch`, or HTTP client calls
- No package installation (`npm install`, `pub get`, etc.) during spike phase
- Dependencies must be pre-installed before cycle start
- Exception: Language-native package resolution from lockfile (e.g., `npm ci`)

## Secret Protection

### Detection
The following patterns are treated as secrets and must never appear in:
- Autopsy reports
- Distill specifications
- Metrics output
- Any `.disposable/` artifacts

Patterns (v1.0.0 implementation):
- Tokens: `Bearer <value>`
- Named credentials: key names `api_key`, `apikey`, `api-key`, `secret`, `token`, `password`, `passwd`, `auth` followed by `=` or `:`
- Connection strings: `scheme://[user]:[pass]@host` (scheme up to 30 chars)
- Private keys: `-----BEGIN ... PRIVATE KEY-----` blocks (including unterminated)
- AWS access keys: `AKIA` prefix + 16 alphanumeric chars
- Generic long secrets: `SECRET`, `TOKEN`, `KEY`, `PASSWORD`, `CREDENTIAL` followed by `=`/`:` and 20+ char value
- Planned for v1.1: GCP (`AIza...`) and Azure credential patterns, generic env-like long values

### Masking
Use `scripts/dist/mask-sensitive.mjs` to sanitize all output artifacts.
Masked values are replaced with `[REDACTED:{category}]`.

## File Scope Restrictions

### Allowed (read/write)
- Project source code within working directory
- `.disposable/` directory (state management)
- Temporary files in system temp directory

### Allowed (read-only)
- `package.json`, `pubspec.yaml`, lockfiles (dependency info)
- Configuration files (`.eslintrc`, `analysis_options.yaml`, etc.)
- Git history (for diff analysis)

### Prohibited
- Files outside project root (no `../` traversal)
- System files (`/etc/`, `/usr/`, `~/.ssh/`, etc.)
- Other users' home directories
- CI/CD configuration files (read-only exception for analysis)

## Sandbox Enforcement

- Spike phase: All generated code runs in isolated branch
- Autopsy phase: Analysis tools run read-only against spike output
- Distill phase: No code execution; specification output only

## Exception Process

Exceptions require explicit user confirmation per-session:
1. Skill presents the exception request with justification
2. User must approve via interactive prompt
3. Exception is logged in `.disposable/cycles/cycle_{N}/exceptions.json`
4. Exception scope is limited to the current cycle only
