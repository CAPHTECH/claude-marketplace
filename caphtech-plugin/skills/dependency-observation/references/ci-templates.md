# CI設定テンプレート

## GitHub Actions

### Node.js

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Check lockfile exists
        run: test -f package-lock.json || (echo "❌ package-lock.json missing" && exit 1)

      - name: Clean install
        run: npm ci

      - name: Type check
        run: npm run typecheck

      - name: Lint
        run: npm run lint

      - name: Test
        run: npm test

      - name: Smoke test
        run: npm run test:smoke
```

### Python (Poetry)

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Check lockfile exists
        run: test -f poetry.lock || (echo "❌ poetry.lock missing" && exit 1)

      - name: Install Poetry
        run: pipx install poetry

      - name: Clean install
        run: |
          rm -rf .venv
          poetry install --no-interaction

      - name: Lint
        run: poetry run ruff check .

      - name: Type check
        run: poetry run mypy .

      - name: Test
        run: poetry run pytest

      - name: Smoke test
        run: poetry run pytest tests/smoke/
```

### Go

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.21'

      - name: Check go.sum exists
        run: test -f go.sum || (echo "❌ go.sum missing" && exit 1)

      - name: Verify dependencies
        run: go mod verify

      - name: Clean build
        run: |
          go clean -cache
          go build ./...

      - name: Lint
        uses: golangci/golangci-lint-action@v4

      - name: Test with race detector
        run: go test -race -v ./...
```

### Rust

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Check Cargo.lock exists
        run: test -f Cargo.lock || (echo "❌ Cargo.lock missing" && exit 1)

      - name: Clean build
        run: |
          cargo clean
          cargo build --locked

      - name: Lint
        run: cargo clippy -- -D warnings

      - name: Test
        run: cargo test

      - name: Audit
        run: cargo audit
```

## セキュリティスキャン

### Secret Scan (gitleaks)

```yaml
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 依存脆弱性スキャン

```yaml
  vulnerability-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Node.js
      - name: npm audit
        run: npm audit --audit-level=high

      # Python
      - name: pip-audit
        run: |
          pip install pip-audit
          pip-audit

      # Go
      - name: govulncheck
        run: |
          go install golang.org/x/vuln/cmd/govulncheck@latest
          govulncheck ./...
```

## スモークテストのパターン

```yaml
  smoke-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Wait for services
        run: |
          until pg_isready -h localhost -p 5432; do
            echo "Waiting for postgres..."
            sleep 2
          done

      - name: Run smoke tests
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/postgres
        run: npm run test:smoke
```
