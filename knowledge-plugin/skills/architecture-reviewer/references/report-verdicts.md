# 判定基準（Report Verdicts）

各 finding に付与する `verdict` フィールドの判定基準を定義する。

## Verdict 値

| Verdict | 意味 | 条件 |
|---------|------|------|
| PASS | 設計と実装が一致 | evidence で確認済み、ギャップなし |
| WARN | 軽微なギャップまたは曖昧さ | リスクは低いが注意が必要 |
| FAIL | 矛盾、未実装、またはガードなし | 対応が必要 |

## 総合 Verdict（verification_summary 用）

| 総合 Verdict | 条件 |
|-------------|------|
| PASS | FAIL=0, WARN=0-2 |
| PASS_WITH_WARNINGS | FAIL=0, WARN=3+ |
| NEEDS_ATTENTION | FAIL=1-2（非クリティカル） |
| FAIL | FAIL=3+ または critical severity の FAIL が 1 つ以上 |

## finding への verdict 付与ルール

### PASS の条件

- 設計文書/コンポーネントカードの記述と実装コードが一致
- evidence（file:line, grep結果, コードスニペット）で裏付けられている
- ギャップや曖昧さがない

### WARN の条件

- 軽微な不一致が存在するが、重大なリスクにはならない
- 例: ドキュメントの記述が古いがコードは正しい
- 例: テストが存在するが網羅性が不十分

### FAIL の条件

- 設計と実装の間に明確な矛盾がある
- 必要な実装が欠落している
- セキュリティやデータ整合性に影響するギャップがある

## severity との関係

verdict と severity は独立した軸:

- `verdict: FAIL` + `severity: critical` → 即時対応（P0候補）
- `verdict: FAIL` + `severity: medium` → 計画的に対応（P2候補）
- `verdict: WARN` + `severity: high` → 注意が必要（P2-P3候補）
- `verdict: PASS` → 指摘なし（severity 不要）
