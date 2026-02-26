# Uncertainty Flags（不確実性フラグ標準語彙）

Issue分析時に検出する不確実性フラグの標準定義。

## フラグ一覧

### 情報欠落系

| フラグ | 説明 | 検出条件 |
|--------|------|----------|
| `missing_repro_steps` | 再現手順なし | 「手順」「ステップ」「操作」の記載がない |
| `missing_expected_vs_actual` | 期待/実際の記載なし | 「期待」「実際」「本来」「should」の記載がない |
| `missing_environment` | 環境情報なし | OS/ブラウザ/バージョン/環境の記載がない |
| `missing_logs` | ログ/エラー情報なし | スタックトレース/エラーメッセージがない |
| `missing_frequency` | 発生頻度不明 | 「常に」「時々」「一度だけ」等の記載がない |
| `missing_impact_breadth` | 影響範囲不明 | 影響ユーザー数/範囲の記載がない |
| `missing_timeline` | 発生時期不明 | いつから発生しているか不明 |

### 曖昧性系

| フラグ | 説明 | 検出条件 |
|--------|------|----------|
| `ambiguous_symptoms` | 症状が曖昧 | 「動かない」「おかしい」等の抽象的記述のみ |
| `ambiguous_scope` | 影響範囲が曖昧 | どの機能/画面/フローか特定できない |
| `conflicting_info` | 矛盾する情報 | 本文内で矛盾する記述がある |

### 調査必要系

| フラグ | 説明 | 検出条件 |
|--------|------|----------|
| `needs_reproduction` | 再現確認が必要 | 再現性が不確か、または再現条件が複雑 |
| `needs_clarification` | 報告者への確認が必要 | 記述が不十分で意図が読み取れない |
| `needs_log_analysis` | ログ分析が必要 | ログ取得後の分析が必要 |
| `needs_code_investigation` | コード調査が必要 | 原因特定にコード調査が必要 |

### 特殊系

| フラグ | 説明 | 検出条件 |
|--------|------|----------|
| `potential_duplicate` | 重複の可能性 | 類似Issueが存在する可能性 |
| `external_dependency` | 外部依存の可能性 | サードパーティ/外部サービス起因の可能性 |
| `intermittent` | 間欠的発生 | 再現が不安定 |

## フラグと次アクションの対応

| フラグ | 推奨 next_action |
|--------|------------------|
| `missing_repro_steps` | 再現手順の追加依頼を検討 |
| `missing_logs` | ログ取得依頼を検討 |
| `missing_environment` | 環境情報の追加依頼を検討 |
| `needs_clarification` | 報告者への質問を検討 |
| `potential_duplicate` | 既存Issue検索を実施 |
| 複数フラグ | `/uncertainty-resolution` |

## confidence への影響

```
base_confidence = 1.0

for flag in uncertainty_flags:
    if flag in information_missing_flags:
        confidence -= 0.10
    elif flag in ambiguity_flags:
        confidence -= 0.08
    elif flag in investigation_flags:
        confidence -= 0.05

confidence = max(confidence, 0.1)  # 最低値
```
