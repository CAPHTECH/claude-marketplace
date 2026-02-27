---
name: rpt-vision-workshop
context: fork
description: Radical Product Thinking (RPT) に基づき、ユーザーと対話的にプロダクトビジョン・戦略・優先順位・実行計画・文化設計を共創するワークショップスキル。「ビジョンを作りたい」「プロダクト戦略を整理したい」「RPTワークショップをしたい」「ミッションを定義したい」「プロダクトの方向性を決めたい」と言った時に使用する。
---

# RPT Vision Workshop

Radical Product Thinking (RPT) フレームワークに基づき、対話的にプロダクトのビジョン・戦略・優先順位・実行計画・文化を共創する。

## モード選択

ワークショップ開始時にユーザーへモードを確認する：

- **Full Workshop**: 全フェーズを順に実施（Kickoff → Vision → Strategy → Prioritization → Execution → Culture → Disease Check）
- **Focused**: 任意のフェーズのみ実施（例: 「ビジョンだけ作りたい」）
- **Review**: 既存のRPTドキュメントをレビューし改善提案

## ワークフロー概要

```
Phase 0: キックオフ
  ↓
Phase 1: Vision（Mad Libs）
  ↓
Phase 2: RDCL Strategy
  ↓
Phase 3: Vision vs Survival Prioritization
  ↓
Phase 4: OHL Execution Plan
  ↓
Phase 5: Culture Matrix
  ↓
Phase 6: Product Disease Check
  ↓
Output: ドキュメント生成
```

## Phase 0: キックオフ

プロダクトの現状把握とワークショップのゴール設定を行う。

**確認事項**:
- プロダクト名と概要（1-2文）
- 現在のフェーズ（構想段階 / 開発中 / 運用中）
- 今日のゴール（何を明確にしたいか）
- 時間枠の目安

**ポイント**:
- 既存のビジョンや戦略がある場合は共有を依頼
- チームの規模・役割も把握しておく

## Phase 1: Vision（Mad Libs）

RPTのMad Libsテンプレートに沿ってビジョンステートメントを共創する。詳細は [references/phase-playbook.md](references/phase-playbook.md) を参照。

**テンプレート**:
```
Today, when [対象者] want to [望ましい活動],
they have to [現在の解決策].
This is unacceptable, because [問題点].
We envision a world where [理想の状態].
We are bringing this world about through [アプローチ].
```

**4つの問い**（順に深掘り）:
1. 誰の世界を変えたいか？（対象者）
2. 現状の何が受け入れられないか？（問題の本質）
3. どんな世界を実現したいか？（理想像）
4. どうやって実現するか？（アプローチ）

質問の詳細は [references/question-bank.md](references/question-bank.md) を参照。

**進め方**:
- 1問ずつ順に深掘り（1ターン1-2問）
- 各回答を要約して確認
- 4問すべて回答後にテンプレートを組み立て、ユーザーと推敲

## Phase 2: RDCL Strategy

ビジョン実現のための戦略を4要素で整理する。詳細は [references/rdcl-guide.md](references/rdcl-guide.md) を参照。

**RDCL 4要素**（順番が重要）:
1. **Real Pain**: ユーザーが感じている真の痛み
2. **Design**: 痛みを解消するプロダクト設計
3. **Capabilities**: 設計を実現するための能力・リソース
4. **Logistics**: ユーザーに届ける仕組み（ビジネスモデル）

**進め方**:
- R→D→C→L の順に1要素ずつ掘り下げ
- 各要素で「主要決定」「根拠」「リスク」を明確化
- Phase 1のビジョンとの整合性を常にチェック

## Phase 3: Vision vs Survival Prioritization

現在の施策・機能をビジョン貢献度とサバイバル必要度で分類する。

**マトリクス**:
```
         Vision (高)
            │
   理想追求 │ 最優先
────────────┼────────────
   要検討   │ 当面必須
            │
         Vision (低)
    Survival (低)    Survival (高)
```

**進め方**:
- まず現在の主要施策・機能を列挙
- 各施策にVision(1-5)とSurvival(1-5)のスコアを付与
- 象限に配置し、優先順位を議論
- **Vision Debt警告**: Survival偏重の場合はリスクを指摘

## Phase 4: OHL Execution Plan

Phase 3で上位となった施策をOHL（Objectives → Hypotheses → Learnings）に分解する。

**フレーム**:
- **Objective**: 達成したい目標（ビジョンに紐づく）
- **Hypothesis**: 目標達成のための仮説（検証可能な形で記述）
- **Learning Signal**: 仮説が正しいと判断する指標
- **Timebox**: 検証期間
- **Owner**: 担当者

**進め方**:
- 上位3-5施策に絞って分解
- 仮説は「もし〜なら、〜が起きるはず」の形式
- 計測可能なLearning Signalを設定

## Phase 5: Culture Matrix

プロダクトチームの文化的慣行を可視化する。

**評価軸**:
- **充実度（1-5）**: その慣行がどれだけ健全に機能しているか
- **緊急度（1-5）**: 改善の緊急性

**代表的な慣行例**:
- コード品質基準、デプロイ頻度、意思決定プロセス、フィードバック文化、技術的負債の管理、ドキュメント文化

**進め方**:
- ユーザーにチームの主要慣行を列挙してもらう
- 各慣行の充実度と緊急度を評価
- 改善アクションを提案

## Phase 6: Product Disease Check

RPTの7つのProduct Disease（プロダクト疾病）についてリスク評価を行う。詳細は [references/disease-checks.md](references/disease-checks.md) を参照。

**7つの疾病**:
1. **Hero Syndrome** — 特定の人物・技術に依存
2. **Strategic Swelling** — 戦略が肥大化し焦点を失う
3. **Obsessive Sales Disorder** — 営業要望に振り回される
4. **Hypermetricemia** — 指標への過度な依存
5. **Locked-In Syndrome** — 技術的・組織的ロックイン
6. **Pivotitis** — 頻繁な方向転換
7. **Narcissus Complex** — 自社プロダクトへの過信

**進め方**:
- 各疾病の症状をユーザーに提示し該当確認
- リスクレベル（L/M/H）を判定
- 緩和策を提案

## Output: ドキュメント生成

ワークショップの成果をドキュメントとして出力する。

### 出力ファイル

```
rpt-output/
├── rpt-workshop-output.md     # Markdown版（人間向け）
└── rpt-workshop-output.yaml   # YAML版（機械可読）
```

### 生成手順

1. ユーザーに出力先ディレクトリを確認（デフォルト: `./rpt-output/`）
2. テンプレート（[assets/](assets/)）を使用してドキュメント生成
3. 生成後、ユーザーに確認・修正の機会を提供

**テンプレート参照**:
- [assets/rpt-workshop-output.md](assets/rpt-workshop-output.md)
- [assets/rpt-workshop-output.yaml](assets/rpt-workshop-output.yaml)

## 進行ルール

- 一度に質問を投げすぎない（1ターン1-2問）
- 各フェーズ終了時に要約を提示し合意を得てから次へ進む
- ユーザーの回答に矛盾があれば指摘する
- トレードオフは明示して選択を促す
- Focusedモードでもキックオフ（Phase 0）は省略しない
- 既存情報がある場合はレビューから始める

## 注意事項

- ビジョンやミッションに「正解」はない — ユーザーの意思を尊重し共創する
- 各フェーズの成果は次フェーズの入力となる — 一貫性を保つ
- 技術的判断は参考情報として提示し、最終判断はユーザーに委ねる
- Disease Checkの結果は脅すためではなく気づきを促すために使う
