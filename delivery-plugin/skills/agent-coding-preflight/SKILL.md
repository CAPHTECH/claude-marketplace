---
name: agent-coding-preflight
context: fork
description: "AIエージェントのコーディング着手前に、要件・コンテキスト・境界・検証・観測のボトルネックを診断し、今すぐ解消できる前処理と解消アクション付きブリーフを生成する。Use when: 新しいタスク開始前、実装前の準備、着手前チェック、preflight、作業開始のボトルネックを解消したい時、詰まりを先に潰してから着手したい時。"
---

# Agent Coding Preflight

AIエージェントが実装に入る前に、着手を遅らせるボトルネックを薄く横断スキャンし、**今すぐ解消できるものだけ片付けてから着手可能性を上げる**。

## このスキルがやること

- 要件・コンテキスト・境界・検証・観測の5領域を診断する
- その場で片付く前処理だけ実施する
- 片付かない問題は既存スキルへ正しく接続する
- 最後に `ready` / `partial` / `blocked` のいずれかでブリーフを返す

## このスキルがやらないこと

- 大規模リファクタ
- 実装修正そのもの
- 長時間の調査
- 深い仕様交渉

## `ai-led-onboarding` との違い

| スキル | 主対象 | 完了条件 |
|---|---|---|
| `ai-led-onboarding` | 人間が最小スキーマを再構築できること | 人間の理解が成立している |
| `agent-coding-preflight` | AIエージェントが実装前の詰まりを減らせていること | AIが安全に着手しやすい状態になっている |

## Ready判定

| 状態 | 意味 |
|---|---|
| `ready` | 着手前ボトルネックが十分に潰れ、最初の検証・観測まで決まっている |
| `partial` | 着手できるが、残タスクや未解消の不確実性がある |
| `blocked` | いま着手すると誤実装や手戻りの確率が高い |

## ワークフロー

```
1. タスク契約の確立
2. 5領域スキャン
3. 即時解消パス
4. 深掘りルーティング
5. Ready判定
6. ブリーフ生成
```

### Step 1: タスク契約の確立

以下を3〜5項目で圧縮する。

- `goal`: 何を成立させたいか
- `success_criteria`: どうなれば完了か
- `constraints`: 期限、互換性、性能、セキュリティなど
- `entrypoints`: 最初に読む入口候補

入口が不明な場合は、まず source of truth 候補から逆引きして仮置きする。

### Step 2: 5領域スキャン

Step 2で [references/bottleneck-catalog.md](references/bottleneck-catalog.md) を読む。各領域ごとに次の3点を埋める。

- `bottleneck`: 何が詰まりか
- `evidence`: 何を根拠にそう言えるか
- `resolvable_now`: 今その場で薄く解消できるか

対象は以下の5領域に固定する。

1. 要件
2. コンテキスト
3. 境界
4. 検証
5. 観測

### Step 3: 即時解消パス

以下だけをその場で処理する。

- 仮定の明文化
- source of truth の確定
- 読む順番の確定
- 触る/触らない境界の明示
- 最小検証手順の決定
- 最低限の観測ポイントの決定

解消の基準は「15分前後で完了し、実装修正に踏み込まないこと」。

### Step 4: 深掘りルーティング

今すぐ解消できない項目だけ、主ボトルネックに応じて既存スキルへ接続する。

| 主ボトルネック | 接続先 |
|---|---|
| 要件の曖昧さ | `spec-observation`, `uncertainty-resolution` |
| 依存・影響範囲の不明 | `impact-analysis` |
| コードの読みにくさ | `ai-readability-analysis` |
| 検証不足 | `observation-minimum-set`, `boundary-observation` |
| 観測不足 | `operability-observation` |
| 依存の不安 | `dependency-observation` |
| セキュリティ懸念 | `security-observation` |
| 並行性懸念 | `concurrency-observation` |

### Step 5: Ready判定

以下のルールで判定する。

- `ready`: 5領域のうち致命的な未解消がなく、最初の検証と観測が決まっている
- `partial`: 着手は可能だが、1〜2領域に残件がある
- `blocked`: 要件、source of truth、境界、または検証のどれかが未確定で危険

### Step 6: ブリーフ生成

Step 6で [assets/preflight-brief.md](assets/preflight-brief.md) を使い、最終出力を1つにまとめる。

必須フィールド:

- `status`
- `goal`
- `success_criteria`
- `constraints`
- `resolved_now`
- `remaining_unknowns`
- `source_of_truth`
- `boundary_map`
- `validation_first_step`
- `observation_first_step`
- `recommended_followup_skills`

## ブリーフ生成ルール

- 長文の説明で安心させない
- 各項目は着手判断に必要な最小情報に絞る
- 未解消項目は隠さず `remaining_unknowns` に出す
- 根拠が弱いものには「仮置き」や「推定」を付ける
- 推奨スキルは多くても3つまでに絞る

## 出力の優先順位

1. いますぐ着手可否が分かる
2. 次に何を読めばよいか分かる
3. 最初の検証と観測が分かる
4. それでも足りない場合だけ追加スキルへ送る

## 使用例

### 入力例

「このバグ修正に入る前に preflight して。関連しそうなのは `src/auth/login.ts`。」

### 出力イメージ

```markdown
## Preflight Brief

- status: partial
- goal: 認証失敗時の誤判定を修正する

### resolved_now
- source of truth を `src/auth/login.ts` と関連テストへ確定
- 読む順番を login handler -> validator -> auth tests に固定
- 最小検証手順を既存認証テストの再実行に固定

### remaining_unknowns
- エラーコード契約が仕様書にない

### recommended_followup_skills
- spec-observation
```

## ガードレール

1. 実装修正に踏み込まない
2. 大規模調査を始めない
3. `ready` を甘く出さない
4. source of truth 未確定のまま着手を推さない
5. 既存スキルに丸投げせず、まず即時解消を試みる
