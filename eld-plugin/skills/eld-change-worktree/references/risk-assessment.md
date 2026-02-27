# リスク判定基準（Risk Assessment）

変更のリスクレベルを判定し、worktree使用の要否を決定する基準。

## リスクレベル分類

### Low Risk（低リスク）

**定義**: 局所的で影響範囲が限定的な変更

**特徴**:
- 単一ファイルの小変更
- 新規ファイル追加
- ドキュメント更新
- テストコード追加
- コメント追加・修正

**worktree要否**: **不要** → 通常のブランチで実行

**例**:
```
変更:
  - src/utils/date.ts に formatDate() 関数追加
  - tests/utils/date.test.ts に対応テスト追加

影響範囲:
  - 新規ファイルまたは単一ファイル
  - 他モジュールへの影響なし

リスク: Low → 通常のブランチで実行
```

---

### Medium Risk（中リスク）

**定義**: 複数ファイルにまたがるが、破壊的変更ではない

**特徴**:
- 複数ファイルの変更
- 既存機能の拡張
- 新規モジュール追加
- リファクタリング（小規模）

**worktree要否**: **推奨** → 隔離環境での実験を推奨

**例**:
```
変更:
  - src/auth/jwt.ts のトークン生成ロジック変更
  - src/auth/session.ts のセッション管理変更
  - tests/auth/*.test.ts のテスト更新

影響範囲:
  - authモジュール内の複数ファイル
  - 他モジュールからの参照あり（3-5箇所）

リスク: Medium → worktreeで隔離実験
```

---

### High Risk（高リスク）

**定義**: 広範囲に影響する変更または破壊的変更の可能性

**特徴**:
- APIインターフェース変更
- データ構造変更
- 複数モジュールにまたがる変更
- パフォーマンスに影響する変更
- セキュリティに関わる変更

**worktree要否**: **必須** → 隔離環境で慎重に実験

**例**:
```
変更:
  - src/api/auth.ts のAPIインターフェース変更
  - 15ファイルの呼び出し箇所を変更
  - src/types/user.ts の型定義変更

影響範囲:
  - 3つのモジュールにまたがる
  - 15箇所の変更が必要
  - 型変更による波及効果

リスク: High → worktree必須
```

---

### Critical Risk（クリティカル）

**定義**: システム全体に影響する大規模変更

**特徴**:
- アーキテクチャ変更
- データベーススキーマ変更
- 認証・認可システム変更
- フレームワーク・ライブラリのメジャーバージョンアップ
- ビルドシステム変更

**worktree要否**: **必須 + 追加安全措置** → 隔離 + 段階的実施

**例**:
```
変更:
  - Basic Auth → JWT 認証への全面移行
  - 50ファイル以上の変更
  - データベーステーブル追加
  - 既存APIの廃止

影響範囲:
  - システム全体
  - 全モジュールに影響
  - データ移行が必要

リスク: Critical → worktree + 段階的実施 + ロールバック計画
```

## eld-predict-impactとの連携

`/eld-predict-impact` の出力からリスクレベルを自動判定。

### Impact Analysisの出力例

```yaml
Causal Type: Interface Change
Affected:
  Files: 15
  Modules: 3
  Law/Term: [LAW-token-expiry, LAW-token-signature]
Ripple Effect: High
Rollback Complexity: Medium
```

### リスクレベル判定ルール

```yaml
Critical:
  条件:
    - Causal Type が "Architecture Change"
    - Affected Files が 50以上
    - Ripple Effect が "Critical"
    - データベーススキーマ変更を含む

High:
  条件:
    - Causal Type が "Interface Change"
    - Affected Files が 10-50
    - Affected Modules が 3以上
    - Ripple Effect が "High"

Medium:
  条件:
    - Causal Type が "Feature Addition" または "Refactoring"
    - Affected Files が 3-10
    - Affected Modules が 1-2
    - Ripple Effect が "Medium"

Low:
  条件:
    - Causal Type が "Bug Fix" または "Documentation"
    - Affected Files が 1-2
    - Affected Modules が 1
    - Ripple Effect が "Low"
```

### 自動判定の例

```
User: APIのレスポンス形式を変更したい

Claude:
## Step 1: Impact Analysis

/eld-predict-impact を実行します。

[結果]
Causal Type: Interface Change
Affected:
  Files: 12
  Modules: 2
Ripple Effect: High

## Step 2: Risk Assessment

リスクレベル: **High**

理由:
- Interface Change（破壊的変更）
- 12ファイルに影響
- Ripple Effect が High

## Step 3: Worktree提案

High リスクのため、worktreeでの隔離実験が必須です。
worktree環境を作成しますか？
```

## Law Severity別のリスク判定

Law Severityもリスク判定に影響。

### S0 Law（ビジネスクリティカル）

S0 Lawに影響する変更は自動的にリスク +1

```yaml
変更: 在庫管理ロジックの変更
Law: LAW-stock-non-negative (S0)

基本リスク: Medium
Law Severity補正: +1
最終リスク: High → worktree必須
```

### S1 Law（機能要件）

S1 Lawに影響する変更は基本リスクのまま

```yaml
変更: パスワードバリデーションの変更
Law: LAW-password-min-length (S1)

基本リスク: Low
Law Severity補正: なし
最終リスク: Low → worktree不要
```

### S2 Law（品質要件）

S2 Lawに影響する変更はリスクに影響なし

```yaml
変更: レスポンスタイムの最適化
Law: LAW-response-time-200ms (S2)

基本リスク: Medium
Law Severity補正: なし
最終リスク: Medium → worktree推奨
```

## リスク判定の実践例

### 例1: 関数追加（Low）

```yaml
変更内容:
  - src/utils/string.ts に capitalize() 関数追加
  - tests/utils/string.test.ts にテスト追加

影響範囲:
  - Files: 2
  - Modules: 1 (utils)
  - Ripple Effect: None

Law/Term:
  - なし

リスク判定:
  基本リスク: Low
  Law Severity補正: なし
  最終リスク: Low

判定: worktree不要、通常のブランチで実行
```

### 例2: 認証システムリファクタリング（High）

```yaml
変更内容:
  - src/auth/*.ts の全ファイルリファクタリング
  - JWTトークン生成ロジック変更
  - セッション管理ロジック変更

影響範囲:
  - Files: 8
  - Modules: 1 (auth)
  - Ripple Effect: Medium

Law/Term:
  - LAW-token-expiry (S0)
  - LAW-token-signature (S0)

リスク判定:
  基本リスク: Medium
  Law Severity補正: +1 (S0が2つ)
  最終リスク: High

判定: worktree必須
```

### 例3: API全面刷新（Critical）

```yaml
変更内容:
  - REST API → GraphQL 移行
  - 全APIエンドポイントの廃止
  - クライアントコードの全面書き換え

影響範囲:
  - Files: 60+
  - Modules: 全モジュール
  - Ripple Effect: Critical

Law/Term:
  - LAW-api-versioning (S0)
  - LAW-backward-compatibility (S0)

リスク判定:
  基本リスク: Critical
  Law Severity補正: +1
  最終リスク: Critical

判定: worktree必須 + 段階的実施 + ロールバック計画
```

## リスク軽減策

### Low → Medium のリスク軽減

```yaml
軽減策:
  - ユニットテスト追加（Evidence L1）
  - コードレビュー
  - 小さいPRに分割

効果: リスク Low 維持
```

### Medium → High のリスク軽減

```yaml
軽減策:
  - worktreeで隔離実験
  - 統合テスト追加（Evidence L2）
  - 段階的ロールアウト
  - Feature Flag使用

効果: リスク Medium に軽減
```

### High → Critical のリスク軽減

```yaml
軽減策:
  - worktreeで隔離実験
  - 失敗注入テスト（Evidence L3）
  - 本番Telemetry設定（Evidence L4）
  - カナリアデプロイ
  - 即座にロールバック可能な計画

効果: リスク High に軽減
```

### Critical のリスク軽減

```yaml
軽減策:
  - worktree必須
  - 全Evidence Ladder達成（L0-L4）
  - 段階的実施（フェーズ分割）
  - Blue-Green デプロイ
  - データベースバックアップ
  - ロールバック手順の文書化
  - ステージング環境での事前検証

効果: リスク High に軽減（それでも慎重に）
```

## リスク判定チェックリスト

### 影響範囲

- [ ] 変更するファイル数は？（1-2 / 3-10 / 10-50 / 50+）
- [ ] 影響するモジュール数は？（1 / 2 / 3+ / 全体）
- [ ] Ripple Effectは？（None / Low / Medium / High / Critical）

### 変更の性質

- [ ] Causal Typeは？（Bug Fix / Feature / Refactor / Interface / Architecture）
- [ ] 破壊的変更か？（No / Maybe / Yes）
- [ ] データ移行が必要か？（No / Yes）

### Law/Term

- [ ] S0 Lawに影響するか？（No / Yes → リスク+1）
- [ ] 複数のS0 Lawに影響するか？（No / Yes → さらにリスク+1）
- [ ] Lawの観測写像（テスト）は十分か？

### ロールバック

- [ ] ロールバック可能か？（Easy / Medium / Hard / Impossible）
- [ ] ロールバック時のデータ損失は？（None / Acceptable / Unacceptable）

## まとめ

### リスクレベル別の対応

| リスク | worktree | Evidence | その他 |
|--------|----------|----------|--------|
| **Low** | 不要 | L0-L1 | 通常のブランチ |
| **Medium** | 推奨 | L1-L2 | 隔離実験 |
| **High** | 必須 | L1-L3 | 段階的実施 |
| **Critical** | 必須 | L0-L4 | ロールバック計画 |

### リスク判定の核心原則

1. **Impact Analysisを活用**: `/eld-predict-impact` の出力を基準に
2. **Law Severityを考慮**: S0 Lawはリスク+1
3. **保守的に判断**: 迷ったらリスクを高めに見積もる
4. **段階的に軽減**: worktree + Evidence + 段階的実施
