# Evidence付与ルール（Evidence Requirement）

タスク分解時に各タスクへEvidence Ladder要件を付与し、Law/Termの接地（Grounding）を計画する。

## Evidence Ladder（証拠の梯子）

Law/Termの正しさを証明する証拠の階層。

```
L4: 本番Telemetry ─ 実運用でのLaw違反検知
L3: 失敗注入 ────── 違反時動作の確認
L2: 統合テスト ──── 境界越えの因果
L1: ユニットテスト ─ Law/Termの観測写像の最小
L0: 静的整合 ────── 型/lint
```

## タスクへのEvidence付与ルール

### 必須情報

各タスク（特に原子タスク）には以下を明示:

```yaml
task:
  name: <タスク名>
  level: L0 | L1 | L2 | L3 | L4  # Evidence Ladderレベル
  verification: <検証方法の具体的記述>
  law_term: [<関連Law ID>, <関連Term ID>]
  time_estimate: <時間見積もり>
```

### Law/Term紐付けの必須化

**原則**: すべての原子タスクは、最低1つのLawまたはTermに紐付ける。

**理由**:
- Law/Termに紐付かないタスクは、何を検証しているか不明
- 技術的な変更も、何らかのTermに紐付く（例: TERM-build-artifact）
- 紐付けがない場合は、タスク分解が不適切と判断

**Good**:
```yaml
task:
  name: JWT型定義追加
  law_term: [TERM-jwt-payload]  # Termに紐付き
```

**Bad**:
```yaml
task:
  name: ファイル整理
  law_term: []  # 紐付けなし → 不適切
```

## Law Severity別のEvidence要件

### S0 Law（ビジネスクリティカル）

```yaml
Severity: S0
必須Evidence:
  - L1（ユニットテスト）: 必須 - 違反時動作含む
  - L2（統合テスト）: 必須
  - L4（本番Telemetry）: 必須
推奨Evidence:
  - L3（失敗注入）: 推奨

カバレッジ基準: 100%（ブランチカバレッジ含む）
```

**例: LAW-stock-non-negative (在庫数は常に0以上)**

```yaml
原子タスク:
  - 在庫チェック実装:
      level: L1
      verification: ユニットテスト（正常系+違反系+境界値）
      law_term: [LAW-stock-non-negative]

  - 在庫引当統合テスト:
      level: L2
      verification: 統合テスト（DBトランザクション含む）
      law_term: [LAW-stock-non-negative]

  - 在庫監視メトリクス:
      level: L4
      verification: Prometheusメトリクス追加
      law_term: [LAW-stock-non-negative]
```

### S1 Law（機能要件）

```yaml
Severity: S1
必須Evidence:
  - L1（ユニットテスト）: 必須
推奨Evidence:
  - L2（統合テスト）: 推奨
  - L4（本番Telemetry）: 推奨

カバレッジ基準: 80%以上
```

**例: LAW-password-min-length (パスワード8文字以上)**

```yaml
原子タスク:
  - パスワードバリデーション実装:
      level: L1
      verification: ユニットテスト（7文字拒否、8文字許可）
      law_term: [LAW-password-min-length]

  - パスワード変更API統合テスト（推奨）:
      level: L2
      verification: API統合テスト
      law_term: [LAW-password-min-length]
```

### S2 Law（品質要件）

```yaml
Severity: S2
推奨Evidence:
  - L1（ユニットテスト）: オプション
  - L4（本番Telemetry）: 推奨

カバレッジ基準: なし
```

**例: LAW-response-time-200ms (レスポンス200ms以内)**

```yaml
原子タスク:
  - レスポンスタイム監視（推奨）:
      level: L4
      verification: APM（New Relic/Datadog）設定
      law_term: [LAW-response-time-200ms]

  # L1は省略可能（単体では意味がない）
```

## Evidence Level別の要件詳細

### L0: 静的整合（型チェック、lint）

**検証内容**:
- 型チェック: tsc --noEmit
- Lint: eslint, prettier
- ビルド成功

**適用タスク**:
- 型定義追加
- インターフェース定義
- 設定ファイル更新

**例**:
```yaml
task:
  name: User型にemailフィールド追加
  level: L0
  verification: tsc型チェック通過
  law_term: [TERM-user-email]
  time_estimate: 5min
```

### L1: ユニットテスト

**検証内容**:
- 正常系テスト
- 異常系テスト（Law違反時の動作）
- 境界値テスト
- カバレッジ計測

**適用タスク**:
- 関数実装
- クラスメソッド実装
- ビジネスロジック

**例**:
```yaml
task:
  name: calculateDiscount() 実装
  level: L1
  verification: ユニットテスト（正常系+異常系+境界値）
  law_term: [LAW-discount-max-50]
  time_estimate: 8min

  tests:
    - 正常系: 20%割引 → 800円
    - 境界値: 50%割引（上限） → 500円
    - 異常系: 60%割引 → Error
```

### L2: 統合テスト

**検証内容**:
- モジュール間の相互作用
- 外部システムとの統合（モック使用）
- トランザクション境界のテスト

**適用タスク**:
- API実装
- データベース操作
- 複数モジュール連携

**例**:
```yaml
task:
  name: POST /orders API実装
  level: L2
  verification: API統合テスト（DB含む）
  law_term: [LAW-order-atomic, LAW-stock-reservation]
  time_estimate: 30min
```

### L3: 失敗注入テスト

**検証内容**:
- ネットワーク障害時の動作
- データベース障害時の動作
- Law違反時のエラーハンドリング

**適用タスク**:
- エラーハンドリング実装
- リトライ/フォールバック実装

**例**:
```yaml
task:
  name: 決済失敗時のリトライ実装
  level: L3
  verification: 失敗注入テスト（Chaos Engineering）
  law_term: [LAW-payment-idempotency]
  time_estimate: 40min
```

### L4: 本番Telemetry

**検証内容**:
- メトリクス収集（Prometheus/Datadog）
- ログ出力
- アラート設定
- Law違反の検知

**適用タスク**:
- 監視設定
- メトリクス追加
- アラート設定

**例**:
```yaml
task:
  name: 在庫マイナス検知メトリクス
  level: L4
  verification: Prometheusメトリクス + Alertmanager
  law_term: [LAW-stock-non-negative]
  time_estimate: 20min
```

## タスク分解時のEvidence計画

### ステップ1: Law/Termの洗い出し

親タスクから関連するLaw/Termをすべて列挙。

```yaml
親タスク: ユーザー認証システム実装

関連Law/Term:
  - LAW-token-expiry (S0): アクセストークンは1時間で失効
  - LAW-token-signature (S0): トークンは署名検証必須
  - LAW-refresh-validity (S1): リフレッシュトークンは7日間有効
  - TERM-jwt-payload (S1): JWTペイロード構造
  - TERM-authenticated-user (S1): 認証済みユーザー
```

### ステップ2: Law SeverityからEvidence要件を決定

Severity別に必要なEvidenceを決定。

```yaml
LAW-token-expiry (S0):
  必須: L1（ユニットテスト）、L2（統合テスト）、L4（Telemetry）

LAW-refresh-validity (S1):
  必須: L1（ユニットテスト）
  推奨: L2（統合テスト）

TERM-jwt-payload (S1):
  必須: L0（型チェック）
```

### ステップ3: 原子タスクへのEvidence付与

各原子タスクに具体的なEvidence要件を付与。

```yaml
原子タスク:
  1.1.1 JWTペイロード型定義:
    level: L0
    verification: tsc型チェック
    law_term: [TERM-jwt-payload]

  1.1.2 トークン生成実装:
    level: L1
    verification: ユニットテスト
    law_term: [LAW-token-expiry, LAW-token-signature]

  1.1.3 トークン検証実装:
    level: L1
    verification: ユニットテスト（期限切れ、改ざん検出）
    law_term: [LAW-token-expiry, LAW-token-signature]

  1.2.1 認証API統合テスト:
    level: L2
    verification: API統合テスト
    law_term: [LAW-token-expiry, LAW-token-signature]

  1.3.1 トークン失効監視:
    level: L4
    verification: Prometheusメトリクス
    law_term: [LAW-token-expiry]
```

## Evidence Summaryテンプレート

タスク分解完了時に、Evidence Summaryを作成。

```markdown
## Evidence Summary

| Task | Evidence Level | Law/Term | Verification | Status |
|------|----------------|----------|--------------|--------|
| 1.1.1 | L0 | TERM-jwt-payload | tsc型チェック | Planned |
| 1.1.2 | L1 | LAW-token-expiry, LAW-token-signature | ユニットテスト | Planned |
| 1.1.3 | L1 | LAW-token-expiry, LAW-token-signature | ユニットテスト | Planned |
| 1.2.1 | L2 | LAW-token-expiry, LAW-token-signature | 統合テスト | Planned |
| 1.3.1 | L4 | LAW-token-expiry | Prometheusメトリクス | Planned |

## Law/Term Coverage

| Law/Term | Severity | Required Evidence | Planned Evidence | Gap |
|----------|----------|-------------------|------------------|-----|
| LAW-token-expiry | S0 | L1, L2, L4 | L1, L2, L4 | ✅ None |
| LAW-token-signature | S0 | L1, L2, L4 | L1, L2 | ⚠️ L4 missing |
| LAW-refresh-validity | S1 | L1 | - | ❌ L1 missing |
| TERM-jwt-payload | S1 | L0 | L0 | ✅ None |
```

## Evidence不足への対処

### Gap検出

Evidence Summaryで不足を検出:

```yaml
LAW-token-signature (S0):
  Required: L1, L2, L4
  Planned: L1, L2
  Gap: L4 missing
```

### Gap解消

不足Evidenceに対応する原子タスクを追加:

```yaml
追加タスク:
  1.3.2 署名検証失敗メトリクス:
    level: L4
    verification: Prometheusメトリクス（signature_verification_failures）
    law_term: [LAW-token-signature]
    time_estimate: 15min
```

## アンチパターン

### ❌ アンチパターン1: Evidence Level不明

```yaml
# Bad
task:
  name: 認証機能実装
  verification: テスト  # 不明確
```

**修正**:
```yaml
# Good
task:
  name: トークン生成関数実装
  level: L1
  verification: ユニットテスト（正常系+異常系+境界値）
```

### ❌ アンチパターン2: Law/Term紐付けなし

```yaml
# Bad
task:
  name: ユーティリティ関数追加
  law_term: []  # 紐付けなし
```

**修正**:
```yaml
# Good
task:
  name: formatDate() ユーティリティ関数追加
  law_term: [TERM-iso8601-date]
  level: L1
  verification: ユニットテスト
```

### ❌ アンチパターン3: Severity無視

```yaml
# Bad: S0 Lawなのに L1のみ
task:
  name: 決済処理実装
  law_term: [LAW-no-double-payment]  # S0
  level: L1  # L2, L4が不足
```

**修正**:
```yaml
# Good: S0要件を満たす複数タスク
task1:
  name: 決済処理実装
  law_term: [LAW-no-double-payment]
  level: L1
  verification: ユニットテスト

task2:
  name: 決済API統合テスト
  law_term: [LAW-no-double-payment]
  level: L2
  verification: API統合テスト

task3:
  name: 二重決済検知メトリクス
  law_term: [LAW-no-double-payment]
  level: L4
  verification: Prometheusメトリクス
```

## まとめ

### Evidence付与の原則

1. **すべてのタスクにEvidence Level付与**
2. **Law/Term紐付けを必須化**
3. **Severity別の要件を遵守**
4. **Evidence Summaryで漏れチェック**
5. **Gap検出→追加タスク作成**

### Evidence付与の恩恵

- Law/Termの接地状況が可視化
- テスト不足の早期発見
- Severity別の優先順位明確化
- 実装完了の明確な定義
- CI/CDでの自動検証が可能
