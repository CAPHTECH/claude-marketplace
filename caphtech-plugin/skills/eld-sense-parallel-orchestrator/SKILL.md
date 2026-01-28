---
name: eld-sense-parallel-orchestrator
context: fork
description: |
  依存関係のないタスクを自動検出し、並列実行を最適化。
  Task toolを活用し、Context継承を適切に管理。

  トリガー条件:
  - 「並列で実行して」「効率的に進めて」「同時に処理して」
  - タスク分解で独立タスクが複数検出された時
  - 大規模な調査・実装タスク時
  - 「並列実行可能なタスクを見つけて」
---

# ELD Sense: Parallel Orchestrator

依存関係のないタスクを自動検出し、並列実行を最適化するスキル。
Task toolを活用して、Context継承を適切に管理しながら効率的な並列処理を実現。

## 核心原則

1. **依存関係の正確な検出**: データ依存・制御依存を漏れなく分析
2. **Context継承の明示化**: 親→子（入力）、子→親（出力）を明確に設計
3. **最大並列度の制御**: リソース制約を考慮した現実的な並列度
4. **失敗の局所化**: 1タスクの失敗が全体を止めない設計
5. **Evidence First**: 並列実行でも証拠の完全性を保証

## 実行フロー

### Phase 1: 依存関係グラフ構築

`eld-sense-task-decomposition`の出力から依存関係グラフを自動構築。

**入力**:
```yaml
tasks:
  - id: task-1
    name: "コードベース調査"
    output: ["調査レポート"]
  - id: task-2
    name: "Law候補抽出"
    depends_on: ["task-1"]
    input: ["調査レポート"]
  - id: task-3
    name: "Term候補抽出"
    depends_on: ["task-1"]
    input: ["調査レポート"]
  - id: task-4
    name: "Link Map作成"
    depends_on: ["task-2", "task-3"]
    input: ["Law候補", "Term候補"]
```

**依存関係グラフ**:
```
task-1 (調査)
  ├→ task-2 (Law抽出)
  │    └→ task-4 (Link Map)
  └→ task-3 (Term抽出)
       └→ task-4 (Link Map)
```

**並列実行可能性の判定**:
- task-2 と task-3 は並列実行可能（共通の依存元task-1のみ）
- task-4 は task-2, task-3 の完了後に実行

詳細: [dependency-analysis.md](references/dependency-analysis.md)

---

### Phase 2: Context継承設計

各タスクの入出力を明示化し、親→子、子→親のContext継承を設計。

**Context継承の型**:

```yaml
parent_to_child:
  type: "input"
  content:
    - Issue Contract
    - 現状証拠（Sense結果）
    - Law/Term候補
    - 制約条件

child_to_parent:
  type: "output"
  content:
    - タスク結果（成功/失敗）
    - 生成物（Law Card/Term Card/Evidence等）
    - 発見した新事実
    - 次ステップへの推奨
```

**継承範囲の設計原則**:
- 必要最小限のContextのみ継承（context window節約）
- 大きなファイル内容は参照パスのみ渡す
- 証拠は必ず親に返す（Evidence First原則）

詳細: [context-inheritance.md](references/context-inheritance.md)

---

### Phase 3: 並列実行可能性判定

依存関係グラフから並列実行可能なタスクセットを抽出。

**並列化の条件**:
1. **データ独立**: 共有状態への書き込みがない
2. **制御独立**: 片方の結果が他方の実行に影響しない
3. **Evidence独立**: 異なるLaw/Termまたは異なるEvidence Levelを対象

**並列実行可能な例**:
```yaml
parallel_set_1:
  - task-2: Law候補抽出（src/auth/*を対象）
  - task-3: Term候補抽出（src/auth/*を対象）
  reason: "異なる観点（Law vs Term）で同じコードを分析"

parallel_set_2:
  - task-5: モジュールAの実装
  - task-6: モジュールBの実装
  reason: "独立したモジュール、共有状態なし"
```

**並列実行不可の例**:
```yaml
sequential_required:
  - task-1: コードベース調査
  - task-2: 調査結果に基づくLaw抽出
  reason: "task-2がtask-1の結果に依存（データ依存）"
```

---

### Phase 4: 最大並列度制御

リソース制約を考慮して現実的な並列度を決定。

**並列度の決定要因**:
1. **CPU/メモリ制約**: システムリソースの上限
2. **API Rate Limit**: 外部API呼び出しの制約
3. **Context Window制約**: Task tool実行時のcontext使用量
4. **認知負荷**: 結果統合の複雑さ

**並列度の目安**:
```yaml
small_tasks:      # 調査・分析タスク（5-10分）
  max_parallel: 4-6
  reason: "Context継承が小さい、統合が容易"

medium_tasks:     # 実装タスク（20-40分）
  max_parallel: 2-3
  reason: "Context継承が中程度、統合に注意が必要"

large_tasks:      # 複雑な実装（2-4時間）
  max_parallel: 1-2
  reason: "Context継承が大きい、統合が複雑"
```

**動的調整**:
並列実行中にリソース不足や失敗が発生した場合、並列度を自動削減。

---

### Phase 5: Task Tool統合

Claude CodeのTask toolで並列実行を実施。

**並列実行の実装パターン**:

```markdown
## 並列実行: Law/Term候補抽出

以下のタスクを並列実行します:
```

次に、複数のTask tool呼び出しを1メッセージで実行:

**Task 1: Law候補抽出**
- subagent_type: general-purpose
- prompt: "src/auth/*のコードからLaw候補を抽出。Issue Contract: [...]"

**Task 2: Term候補抽出**
- subagent_type: general-purpose
- prompt: "src/auth/*のコードからTerm候補を抽出。Issue Contract: [...]"

**Task 3: 影響範囲分析**
- subagent_type: Explore
- prompt: "src/auth/*の依存関係を調査。参照元モジュールをすべて列挙。"

**重要**: 1メッセージ内で複数Task toolを呼び出すことで真の並列実行を実現。

---

### Phase 6: 結果統合と検証

並列実行タスクの結果を統合し、整合性を検証。

**統合プロセス**:
1. **結果収集**: 各Task toolの出力を収集
2. **整合性チェック**: Law/Term間の矛盾、Evidence不整合を検出
3. **Evidence統合**: 各タスクのEvidenceを統合してEvidence Packに反映
4. **失敗処理**: 一部タスク失敗時の再実行またはスコープ縮小

**整合性チェック項目**:
```yaml
law_term_consistency:
  - Law ↔ Term の相互参照が成立しているか
  - 同じ概念に対する重複定義がないか
  - 用語の不一致（synonym/alias）はないか

evidence_consistency:
  - Evidence Levelの重複はないか
  - 必要なEvidenceが不足していないか
  - Evidenceの観測手段が実行可能か
```

**失敗時の対応**:
```yaml
partial_failure:
  strategy: "成功したタスクの結果を採用、失敗タスクは順次実行で再試行"

complete_failure:
  strategy: "並列実行を中止、順次実行に切り替え"

evidence_gap:
  strategy: "不足Evidenceを補完する追加タスクを生成"
```

詳細: [parallel-patterns.md](references/parallel-patterns.md)

---

## 並列実行パターン

### パターン1: 調査タスクの並列実行

**ユースケース**: 大規模コードベースの多角的調査

```yaml
scenario: "認証システムの全体像把握"
parallel_tasks:
  - task-1: "src/auth/* の関数定義調査（Grep）"
  - task-2: "src/auth/* のインポート関係調査（Grep）"
  - task-3: "src/auth/* のテストコード調査（Glob + Read）"
  - task-4: "src/auth/* の型定義調査（Grep）"

benefit: "4つの調査を並列実行で時間短縮（順次実行の25%の時間）"
```

---

### パターン2: Law/Term抽出の並列実行

**ユースケース**: 同じコードベースから異なる観点で抽出

```yaml
scenario: "新機能開発のLaw/Term同定"
parallel_tasks:
  - task-1: "Law候補抽出（不変条件/Pre/Post/Policy観点）"
  - task-2: "Term候補抽出（Entity/Value/Context/Boundary観点）"

dependency: "両タスクとも同じ調査結果を入力とする"
benefit: "2つの観点を並列処理で効率化"
```

---

### パターン3: 独立モジュールの並列実装

**ユースケース**: データ/制御依存のない複数モジュール実装

```yaml
scenario: "マイクロサービスの並列実装"
parallel_tasks:
  - task-1: "ユーザー認証サービスの実装"
  - task-2: "商品カタログサービスの実装"
  - task-3: "注文処理サービスの実装"

condition:
  - 各サービスは独立したDB/APIを持つ
  - 共有状態がない
  - Evidence Levelも独立（それぞれL1-L2達成）

benefit: "開発時間を1/3に短縮"
```

---

### パターン4: Evidence収集の並列実行

**ユースケース**: 異なるEvidence Levelの並行収集

```yaml
scenario: "S0 Lawの完全な接地"
parallel_tasks:
  - task-1: "L1 Evidence収集（ユニットテスト作成）"
  - task-2: "L2 Evidence収集（統合テストシナリオ設計）"
  - task-3: "L4 Evidence収集（Telemetry設定）"

dependency: "各Evidenceは独立して収集可能"
benefit: "Evidence Ladder達成を並列化"
```

---

## eld-sense-task-decompositionとの連携

`eld-sense-task-decomposition`で分解されたタスクを入力として受け取り、
並列実行可能性を自動判定。

**連携フロー**:

```
1. eld-sense-task-decomposition
   └→ タスク階層と依存関係を含むタスクツリー生成

2. eld-sense-parallel-orchestrator
   ├→ 依存関係グラフ構築
   ├→ 並列実行可能なタスクセット抽出
   ├→ Context継承設計
   └→ Task tool並列実行

3. 結果統合
   └→ 親タスクへの結果集約
```

**入力形式の期待**:

```yaml
tasks:
  - id: <task-id>
    name: <task-name>
    depends_on: [<task-id>, ...]  # 必須: 依存タスクID
    input: [<input-name>, ...]     # 必須: 入力データ
    output: [<output-name>, ...]   # 必須: 出力データ
    evidence_level: L0/L1/L2/L3/L4
    law_term: [<LAW-xxx>, <TERM-yyy>]
    time_estimate: <time>
```

---

## ELD統一ループへの統合

### Senseフェーズでの位置づけ

```
┌─ Sense ─────────────────────────────────────────┐
│ 1. eld-sense-activation                        │
│    └→ Active Contextを構築                     │
│                                                 │
│ 2. eld-sense-scope                             │
│    └→ タスクスコープを定義                      │
│                                                 │
│ 3. eld-sense-task-decomposition                │
│    └→ タスク階層に分解                          │
│                                                 │
│ 4. [NEW] eld-sense-parallel-orchestrator       │ ← ここ
│    └→ 並列実行可能性を判定し、効率的に調査実行  │
└─────────────────────────────────────────────────┘
```

**調査効率化の効果**:
- 順次実行: 4タスク × 10分 = 40分
- 並列実行: 4タスク並列 = 10分（75%時間短縮）

---

## リファレンス

- [dependency-analysis.md](references/dependency-analysis.md): 依存関係グラフ構築の詳細
- [context-inheritance.md](references/context-inheritance.md): Context継承設計パターン
- [parallel-patterns.md](references/parallel-patterns.md): 並列実行パターンと失敗処理

---

## 使用例

```
User: 認証システムの調査を効率的に進めて

Claude:
## ELD Sense Phase: 並列調査

認証システムを多角的に調査します。以下のタスクを並列実行:

### 並列実行タスク（4タスク同時）

**Task 1: 関数定義調査**
- 対象: src/auth/*
- ツール: Grep
- 出力: 全関数シグネチャ一覧

**Task 2: インポート関係調査**
- 対象: src/auth/*
- ツール: Grep
- 出力: 依存関係グラフ

**Task 3: テストコード調査**
- 対象: tests/auth/*
- ツール: Glob + Read
- 出力: テストカバレッジ状況

**Task 4: 型定義調査**
- 対象: src/auth/*
- ツール: Grep
- 出力: 型定義一覧

[Task toolを4つ並列実行]

### 結果統合

4タスクの結果を統合して調査レポートを作成...
```

---

## 品質優先原則（Superpowers統合）

### 核心原則

1. **Epistemic Humility**: 推測を事実として扱わない。`unknown`と言う勇気を持つ
2. **Evidence First**: 結論ではなく因果と証拠を中心にする
3. **Minimal Change**: 最小単位で変更し、即時検証する
4. **Grounded Laws**: Lawは検証可能・観測可能でなければならない
5. **Source of Truth**: 真実は常に現在のコード。要約はインデックス

### 「速さより質」の実践

- 要件の曖昧さによる手戻りを根本から排除
- テストなし実装を許さない
- 観測不能な変更を防ぐ

---

## 完了条件

- [ ] 依存関係グラフが正確に構築されている
- [ ] 並列実行可能なタスクセットが適切に抽出されている
- [ ] Context継承が明示的に設計されている
- [ ] Task tool並列実行が成功している
- [ ] 結果統合で整合性が保たれている
- [ ] Evidence Packに並列実行結果が反映されている

---

## 停止条件

以下が発生したら並列実行を中止し、順次実行に切り替え:

- 並列タスクの50%以上が失敗
- Context window制約でTask tool実行不可
- 結果統合で解決不能な矛盾が発生
- リソース不足で並列度が1に低下
