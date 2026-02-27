# Risk Scoring（リスクスコアリング詳細）

リスク評価の因子、重み、計算方法。

## スコアリングモデル

### 因子定義

| 因子 | 重み | 説明 | 検出条件 |
|------|------|------|----------|
| `security_critical_path` | 25 | セキュリティクリティカルパス | 認証/認可/決済フロー上 |
| `data_write` | 20 | データ書き込み | DB/キャッシュへの書き込み |
| `public_interface_change` | 15 | 公開IF変更 | export/APIの変更 |
| `fanout_large` | 10 | 大きなファンアウト | caller数 > 5 |
| `low_test_coverage` | 15 | 低テストカバレッジ | カバレッジ < 50% |
| `unknowns_present` | 15 | 不確実性あり | 静的解析不可の経路 |

### 追加因子（オプション）

| 因子 | 重み | 説明 |
|------|------|------|
| `breaking_change` | 15 | 破壊的変更 |
| `migration_required` | 10 | マイグレーション必要 |
| `external_dependency_change` | 10 | 外部依存変更 |
| `config_change` | 5 | 設定変更 |
| `observability_gap` | 5 | 観測性の欠如 |

## スコア計算

### 基本計算

```
score = Σ (適用因子の contribution)
```

各因子は「適用されるかどうか」と「適用時の寄与度」を持つ。

### 適用判定

```yaml
factor: "security_critical_path"
applied: true/false
contribution: 0-25 (重みまで)
evidence:
  - "認証フロー上の変更"
```

### スコアからレベルへの変換

| score | level | 意味 |
|-------|-------|------|
| 70-100 | high | 慎重なレビューと追加テストが必須 |
| 40-69 | medium | 標準的なレビューとテスト |
| 0-39 | low | 軽量なレビューで可 |

## 計算例

### 例1: 認証機能のバグ修正

```yaml
applied_factors:
  - factor: "security_critical_path"
    contribution: 25
    evidence: ["ログイン処理の変更"]

  - factor: "data_write"
    contribution: 20
    evidence: ["セッションの書き込み"]

  - factor: "unknowns_present"
    contribution: 10
    evidence: ["DIコンテナ経由の呼び出し"]

score: 55
level: medium
```

### 例2: 公開API変更

```yaml
applied_factors:
  - factor: "public_interface_change"
    contribution: 15
    evidence: ["POST /api/users のレスポンス型変更"]

  - factor: "breaking_change"
    contribution: 15
    evidence: ["必須フィールドの追加"]

  - factor: "fanout_large"
    contribution: 10
    evidence: ["12箇所から呼び出し"]

score: 40
level: medium
```

### 例3: 軽微なUI修正

```yaml
applied_factors:
  - factor: "low_test_coverage"
    contribution: 5  # 部分適用
    evidence: ["該当コンポーネントのカバレッジ40%"]

score: 5
level: low
```

## リスクマトリクス

影響をhigh/medium/lowで集計:

```yaml
matrix:
  high: 2     # high影響の項目数
  medium: 5   # medium影響の項目数
  low: 12     # low影響の項目数
```

### マトリクスの解釈

| パターン | 解釈 |
|----------|------|
| high多い | 重点レビュー必須 |
| medium多い | 標準レビュー |
| low多い | 広範囲だが軽微 |

## 因子の重み調整

プロジェクト特性に応じて重み調整可能:

### 金融系プロジェクト

```yaml
scoring_model:
  factors:
    - factor: "security_critical_path"
      weight: 30  # 強化
    - factor: "data_write"
      weight: 25  # 強化
```

### 内部ツール

```yaml
scoring_model:
  factors:
    - factor: "security_critical_path"
      weight: 15  # 緩和
    - factor: "public_interface_change"
      weight: 5   # 緩和
```

## confidence（確度）の影響

不確実性が高い場合、スコアを「保守的」に評価:

```
if confidence < 0.5:
  # 不確実性が高い場合は高めに見積もる
  score = score * 1.2
  notes.add("不確実性が高いため保守的に評価")
```
