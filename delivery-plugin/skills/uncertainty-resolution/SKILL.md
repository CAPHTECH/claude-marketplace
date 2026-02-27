---
name: uncertainty-resolution
context: fork
description: 不確実性を発見・台帳化し、優先順位付け・観測タスク化を経て、検証済み仮説をLaw（LDE）に昇格させる。使用タイミング: 不確実性/曖昧さ/未知/仮説/検証/調査/リスク/前提/優先順位/観測/意思決定の話題が出たとき、または検証結果のLaw化を求められたとき。
argument-hint: "register-only" で台帳作成まで、"full" でLaw昇格まで（デフォルト: full）
---

# Uncertainty Resolution

不確実性の発見からLaw昇格までを一貫して扱う。

## $ARGUMENTS

| 値 | 実行範囲 |
|---|---|
| `register-only` | Phase 1-2のみ（台帳作成+観測タスク化） |
| `full`（デフォルト） | Phase 1-3すべて（Law昇格まで） |

引数なしは `full` として扱う。

## Phase 1: 不確実性の発見・台帳化

### Step 1: 意思決定のフレーミング
1〜3行で明確化する:
- 決めたいこと（Decision）
- 期限（When）
- 失敗時の損失（Stakes）
- 制約（Constraints）

### Step 2: 不確実性の列挙
`assets/uncertainty-register.md` テンプレートを使い、まず10個まで項目化する。
足りない場合のみ増やす。抜け漏れチェックには [references/triage-questions.md](references/triage-questions.md) を使う（不確実性の洗い出し観点リスト）。

各項目を「〜は本当に成り立つか？」の疑問文に整える。
既に観測で答えが出ているものは事実として別枠へ移す。

### Step 3: 優先順位付け
各項目に1〜5でスコアを付ける。詳細基準は [references/scoring.md](references/scoring.md) を参照（Impact/Evidence/Urgency/Effortの各レベル定義）。

```
Priority = Impact x (6 - Evidence) x Urgency / Effort
```

上位N（通常3〜5）を選ぶ。

## Phase 2: 観測タスク化

### Step 4: 観測タスクへ変換
上位Nについて `assets/observation-task.md` テンプレートを使い、各タスクに必ず含める:
- Hypothesis（仮説）
- Method（現物/証拠/知識）
- Timebox（上限時間）
- Decision rule（採用/撤回の条件）
- Evidence artifact（ログ/スクショ/計測/テスト結果など）

観測方法の選択には [references/observation-methods.md](references/observation-methods.md) を参照（現物観測・証拠観測・知識観測の使い分け）。

### Step 5: 計画の検証と実行（高リスク時に推奨）
破壊的・大量の作業に繋がる場合:
1. `uncertainty_plan.json` を出力
2. `python scripts/validate_uncertainty_plan.py uncertainty_plan.json` で検証
3. エラーがあれば修正して再検証
4. OKなら実行に進む

### Step 6: クローズ
各項目を Validated / Rejected / Accepted に更新し、Evidenceを必ず残す。
意思決定が絡む場合は `assets/decision-record.md` テンプレートを使う。

`$ARGUMENTS` が `register-only` の場合はここで終了。

## Phase 3: Law昇格（LDE連携）

検証済み仮説をLaw-Driven EngineeringのLawに昇格させる。

### Step 7: 昇格候補の選定

Phase 2でValidatedになった仮説から、以下の全条件を満たすものを候補にする:
- 観測タスクで検証済み
- 複数回/セッションで再確認済み
- ビジネス影響度 >= 3
- 検証・観測手段が定義可能
- 証拠が記録されている

### Step 8: Law Card生成

候補ごとにLaw Type（Invariant / Pre / Post / Policy）を判定し、Law Card案を生成する。
テンプレート・判定基準・変換パターン例は [references/law-promotion.md](references/law-promotion.md) を参照（昇格条件の詳細、Law Type判定表、Law Cardテンプレート、変換例、レポート形式）。

### Step 9: レビュー・正式化

1. 生成されたLaw Card案を人間がレビュー
2. `/lde-law-card` で正式なLaw Cardとして作成
3. Law CatalogとGrounding Mapを更新
4. pce-memoryに昇格履歴を記録（連携方法は [references/law-promotion.md](references/law-promotion.md) を参照）

## Operating Principles
- 1項目 = 1つの不確実性（疑問文）に分解する
- スコアは「観測リソース配分」のために使う。絶対視しない
- 観測タスクは「結果が出たら意思決定が進む」形にする
- 時間がない場合は仮定を置いてRegisterに"仮定"として記録する
- 昇格保留の仮説には追加の観測タスクを提案する

## Assets
- `assets/uncertainty-register.md` - 台帳テンプレート
- `assets/uncertainty-card.md` - 個別項目の詳細テンプレート
- `assets/observation-task.md` - 観測タスクテンプレート
- `assets/decision-record.md` - 意思決定記録テンプレート

## Example

より詳しい例は [references/example.md](references/example.md) を参照（MVPでオフライン機能を入れるかの意思決定例）。

入力: 「この機能、ユーザーが本当に必要か分からない。技術的にも不安。どう進める？」

出力:
1. Decision/Constraints のフレーミング
2. Uncertainty Register（10件以内）
3. Top-3優先不確実性
4. 観測タスク（仮説/手順/判定/証拠/タイムボックス）
5. （full時）検証後、条件を満たす仮説のLaw Card案
