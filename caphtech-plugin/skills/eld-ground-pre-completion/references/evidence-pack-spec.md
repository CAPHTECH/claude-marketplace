# Evidence Pack仕様

変更の正当性を証明する一式の証拠の標準フォーマット。PR本文の核心。

## Evidence Packの構成

```yaml
evidence-pack/
├── causal-map.md           # 因果マップ
├── impact-graph.yaml       # 影響範囲グラフ
├── changed-files.txt       # 変更ファイル一覧
├── irreversible-changes.txt # 不可逆的変更一覧
└── evidence/               # 証拠ディレクトリ
    ├── test-results.txt    # テスト結果
    ├── coverage-report.html # カバレッジレポート
    └── telemetry-config.yaml # Telemetry設定
```

---

## 1. 因果マップ (causal-map.md)

**目的**: 変更の因果関係を明確にする

**フォーマット**:

```markdown
# 因果マップ

## 変更の因果関係

### Why（なぜこの変更が必要か）
JWT認証への移行により、セキュリティを強化する。
現在のBasic認証では、パスワードが平文で送信されるリスクがある。

### What（何を変更するか）
- src/auth/legacy.ts のBasic認証を削除
- src/auth/jwt.ts のJWT認証を実装
- src/middleware/auth.ts を更新してJWT検証を追加

### How（どのように変更するか）
1. JWT生成ロジックを実装
2. JWT検証ロジックを実装
3. 既存APIエンドポイントを更新
4. テストを追加

## 影響範囲グラフ

### 直接影響
- src/auth/jwt.ts（新規作成）
- src/middleware/auth.ts（更新）
- src/auth/legacy.ts（削除）

### 間接影響
- tests/auth/*.test.ts（テスト更新）
- API clients（認証ヘッダー変更）

## データフロー

```
User → API Request → auth middleware → JWT verify → Route Handler
                          ↓
                    Token expiry check
                          ↓
                    Signature verification
```
```

---

## 2. 影響範囲グラフ (impact-graph.yaml)

**目的**: 変更の影響範囲を構造化して記録

**フォーマット**:

```yaml
changed_files:
  - path: src/auth/jwt.ts
    status: added
    lines_added: 120
    lines_deleted: 0

  - path: src/middleware/auth.ts
    status: modified
    lines_added: 45
    lines_deleted: 30

  - path: src/auth/legacy.ts
    status: deleted
    lines_added: 0
    lines_deleted: 80

dependencies:
  - module: jsonwebtoken
    version: "^9.0.0"
    type: production

  - module: src/config/jwt-config.ts
    type: internal

ripple_effect:
  level: High
  reason: "API認証方式の全面変更"
  affected_modules:
    - src/auth/*
    - src/middleware/*
    - tests/auth/*

  breaking_changes:
    - "Basic認証からJWT認証への変更（後方互換性なし）"
    - "認証ヘッダー形式の変更"
```

---

## 3. 証拠ディレクトリ (evidence/)

### 3.1 テスト結果 (test-results.txt)

**フォーマット**:

```
Test Suites: 10 passed, 10 total
Tests:       45 passed, 45 total
Snapshots:   0 total
Time:        12.456 s

Coverage:
  Statements   : 100% ( 120/120 )
  Branches     : 100% ( 45/45 )
  Functions    : 100% ( 30/30 )
  Lines        : 100% ( 115/115 )

✓ src/auth/jwt.test.ts
  ✓ JWT generation
    ✓ generates valid JWT token
    ✓ includes correct claims
    ✓ expires after 1 hour
  ✓ JWT verification
    ✓ verifies valid token
    ✓ rejects expired token
    ✓ rejects invalid signature
```

### 3.2 Telemetry設定 (telemetry-config.yaml)

**フォーマット**:

```yaml
metrics:
  - name: jwt_generation_total
    type: counter
    description: "Total number of JWT tokens generated"
    labels: [user_id, client_id]

  - name: jwt_verification_failures_total
    type: counter
    description: "Total number of JWT verification failures"
    labels: [reason]

  - name: token_expiry_violations_total
    type: counter
    description: "Total number of expired token usage attempts"
    labels: [user_id]

alerts:
  - name: HighJWTVerificationFailureRate
    condition: rate(jwt_verification_failures_total[5m]) > 10
    severity: warning
    message: "JWT verification failure rate is high"

  - name: TokenExpiryViolations
    condition: token_expiry_violations_total > 0
    severity: critical
    message: "Token expiry violation detected"
```

---

## 4. Law/Term整合性

### 4.1 Law Catalog

**ディレクトリ**: `law-catalog/`

**ファイル例**: `law-catalog/LAW-token-expiry.yaml`

```yaml
id: LAW-token-expiry
scope: S0
category: Invariant
statement: "アクセストークンは1時間で失効する"
rationale: "セキュリティリスクを最小化するため"

enforcement:
  - method: "JWT exp claimで有効期限を設定"
  - method: "検証時にexp claimをチェック"

violation_behavior:
  - "有効期限切れのトークンを拒否"
  - "401 Unauthorized を返す"

exceptions: []
```

### 4.2 Term Catalog

**ディレクトリ**: `term-catalog/`

**ファイル例**: `term-catalog/TERM-access-token.yaml`

```yaml
id: TERM-access-token
category: Value
definition: "JWT形式のアクセストークン"
purpose: "API認証とユーザー識別"

structure:
  format: "JWT (JSON Web Token)"
  claims:
    - sub: "User ID"
    - exp: "Expiration timestamp"
    - iat: "Issued at timestamp"

observation:
  - "HTTPヘッダー Authorization: Bearer <token>"
  - "JWT署名検証で真正性を確認"

boundary:
  min: "Header + Payload + Signature (最小100文字)"
  max: "4KB (HTTPヘッダー制限)"
```

### 4.3 Link Map

**ファイル**: `link-map.yaml`

```yaml
links:
  - law: LAW-token-expiry
    term: TERM-access-token
    relation: "LAW-token-expiry は TERM-access-token の exp claim で実現"

  - law: LAW-token-signature
    term: TERM-access-token
    relation: "LAW-token-signature は TERM-access-token の署名で保証"
```

### 4.4 Grounding Map

**ファイル**: `grounding-map.yaml`

```yaml
laws:
  - law: LAW-token-expiry
    severity: S0
    evidence:
      - level: L1
        verification: tests/auth/token-expiry.test.ts
        coverage: 100%

      - level: L2
        verification: tests/integration/auth-flow.test.ts
        scenario: "トークン有効期限切れ時の動作確認"

      - level: L4
        observation: src/observability/metrics.ts
        metric: token_expiry_violations_total
```

---

## 5. PR本文フォーマット

**テンプレート**:

```markdown
## Summary

JWT認証への移行。セキュリティ強化とトークンベース認証の実現。

## Evidence Pack

### 因果マップ

**Why**: Basic認証のセキュリティリスクを解消
**What**: JWT認証実装、Basic認証削除
**How**: 段階的移行、テストファースト

### 影響範囲

- 変更ファイル: 5 files (+120, -80)
- Ripple Effect: High (API認証方式の全面変更)
- Breaking Changes: あり（後方互換性なし）

### 証拠

- L1: ユニットテスト 45/45 passed (100% coverage)
- L2: 統合テスト 3/3 passed
- L4: Telemetry設定完了

### Law/Term整合性

- Law Cards: 3件 (LAW-token-expiry, LAW-token-signature, LAW-session-timeout)
- Term Cards: 2件 (TERM-access-token, TERM-refresh-token)
- Link Map: 孤立なし
- Grounding Map: すべてのS0 LawがL1/L2/L4達成

## Test Plan

- [x] ユニットテスト (100% coverage)
- [x] 統合テスト
- [x] Telemetry設定
- [ ] 本番環境でのカナリアテスト (リリース後)

## Rollback Plan

1. git revert <commit-sha>
2. 旧Basic認証エンドポイントを一時復活
3. クライアントを旧認証に切り戻し

🤖 Generated with Claude Code
```

---

## まとめ

### Evidence Packの核心要素

1. **因果マップ**: Why/What/Howの明確化
2. **影響範囲グラフ**: 変更の波及範囲の可視化
3. **証拠**: テスト結果とTelemetry設定
4. **Law/Term整合性**: Catalog + Link Map + Grounding Map

### 完全性の基準

- [ ] すべての構成要素が存在する
- [ ] 証拠が完全に揃っている
- [ ] Law/Termに孤立がない
- [ ] Evidence Ladder目標達成
- [ ] ロールバック可能

すべての基準を満たした時点で、PRが完成と判定。
