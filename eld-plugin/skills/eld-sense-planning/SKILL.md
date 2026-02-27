---
name: eld-sense-planning
context: fork
description: タスクを親→子→孫に分解し、コンテキスト継承を設計し、並列実行を最適化する計画スキル。大きなタスクの実装計画・分解・並列化が必要な時に使う。
---

# ELD Sense: Planning

タスク分解→スコープ設計→並列化をワンセットで実行する。

## Phase 1: タスク分解

親→子→孫の3レベル以内でタスクを分解する。

### 分解原則

1. **3段階上限**: 親→子→孫
2. **単一責務**: 各タスクは1つの責務に集中
3. **独立性**: 可能な限り並列実行可能に
4. **境界明確**: 責務の重複・漏れを防ぐ
5. **原子性**: 末端タスクは5-10分で完了する原子タスクに

### 原子タスクの基準

原子タスク = 5-10分で完了する最小単位。以下をすべて満たすこと:

- 単一の概念変更（1つのシンボル/Law/Termに集中）
- 独立してテスト可能
- `git checkout` でロールバック可能
- Evidence Ladder L0以上で検証可能
- 1タスク = 1コミット

詳細とアンチパターンは [atomic-task-definition.md](references/atomic-task-definition.md) を参照（粒度判定に迷った時に読む）。

### 粒度目安

| サイズ | 時間 | 例 |
|--------|------|-----|
| 原子タスク | 5-10分 | 型定義追加、1関数の実装、1テスト追加 |
| 子タスク | 20-40分 | モジュール実装、API層実装 |
| 親タスク | 2-4時間 | 機能全体の実装 |

### Evidence付与

各タスクに以下を明示:

```yaml
task:
  name: <タスク名>
  level: L0 | L1 | L2 | L3 | L4
  verification: <検証方法>
  law_term: [<関連Law/Term ID>]
  time_estimate: <時間見積もり>
```

すべての原子タスクは最低1つのLawまたはTermに紐付ける。紐付けがなければ分解が不適切。

Evidence LadderとSeverity別要件の詳細は [evidence-requirement.md](references/evidence-requirement.md) を参照（Evidence計画時に読む）。

### 分解テンプレート

```markdown
# Task Decomposition: [親タスク名]

## Level 0: Root Task
**Goal**: [全体目標]
**Constraints**: [全体制約]
**Success Criteria**: [完了条件]

## Level 1: Major Components
### 1.1 [子タスク1]
- Goal: [目的]
- Boundary: [責務境界]
- Dependencies: [依存関係]
- Parallel: Yes/No
- Time Estimate: [時間見積もり]

## Level 2: Atomic Tasks
### 1.1.1 [原子タスク1]
- Goal: [目的]
- Evidence Level: L0/L1/L2/L3/L4
- Verification: [検証方法]
- Law/Term: [LAW-xxx, TERM-yyy]
- Time Estimate: 5-10min

## Context Inheritance Map
| From | To | Inherit | Return |
|------|-----|---------|--------|
| Root | 1.1 | [継承情報] | [戻す情報] |

## Evidence Summary
| Task | Level | Law/Term | Verification |
|------|-------|----------|--------------|
| 1.1.1 | L1 | LAW-xxx | ユニットテスト |
```

### 分解パターン

**機能分割**:
```
機能A実装
├── データ層
├── ビジネスロジック層
└── API層
```

**フェーズ分割**:
```
機能A実装
├── 設計フェーズ
├── 実装フェーズ
└── テストフェーズ
```

**ドメイン分割**:
```
Eコマース機能
├── 商品管理
├── カート管理
└── 決済処理
```

---

## Phase 2: スコープ設計

入れ子プロセス間のコンテキスト継承を設計する。

### 親→子へ渡すもの（最小コンテキスト）

```yaml
to_child:
  goal: 子タスクの目的（親目的との関係）
  constraints: 子に適用される制約のみ
  references: 必要な参照のみ（フルパス）
  boundary: 子の責務範囲の明確な境界
```

### 子→親へ戻すもの（要約+差分）

```yaml
from_child:
  summary: 成果の要約（3行以内）
  artifacts: 生成した成果物リスト
  decisions: 子が行った重要な決定
  issues: 発見した問題・懸念
  delta: 潜在プールへ追加すべき知見
```

### スコープ破綻の防止

| 問題 | 症状 | 対策 |
|------|------|------|
| 過剰継承 | 子がノイズで混乱 | 最小コンテキストに絞る |
| 過少継承 | 子が前提を誤認 | 必須参照を明示 |
| 境界曖昧 | 責務が重複・漏れ | boundary明確化 |
| 差分欠落 | 親が子の学びを失う | deltaを必須化 |

### Context最小化テクニック

1. **ファイル内容→パスのみ**: 子タスクが必要に応じて読み取る
2. **全内容→要約**: 100行を5行の要約に圧縮
3. **段階的読み込み**: 利用可能リソースのパスだけ渡し、子が必要分だけ読む

Context継承パターンの詳細（Broadcast/Pipeline/Scatter-Gather/Hierarchical）は [context-inheritance.md](references/context-inheritance.md) を参照（Task tool統合で設計に迷った時に読む）。

---

## Phase 3: 並列化

依存関係のないタスクを検出し、Task toolで並列実行する。

### 依存関係の4種類

1. **データ依存**: タスクBがタスクAの出力を入力として使用
2. **制御依存**: タスクBの実行条件がタスクAの結果に依存
3. **リソース依存**: 同一ファイルへの並行書き込み
4. **Evidence依存**: テスト作成が実装完了に依存

いずれの依存もなければ並列実行可能。

依存関係グラフ構築の詳細アルゴリズムは [dependency-analysis.md](references/dependency-analysis.md) を参照（依存判定に迷った時に読む）。

### 並列実行可能性の判定

```
task-1 (調査)
  ├→ task-2 (Law抽出)  ─┐
  └→ task-3 (Term抽出) ─┴→ task-4 (Link Map)
```

- task-2 と task-3: 並列実行可能（相互依存なし）
- task-4: task-2, task-3 の完了後に実行

### 並列度の目安

| タスクサイズ | 最大並列度 | 理由 |
|-------------|-----------|------|
| 調査・分析（5-10分） | 4-6 | Context継承が小さく統合が容易 |
| 実装（20-40分） | 2-3 | Context継承が中程度 |
| 複雑な実装（2-4時間） | 1-2 | Context継承が大きく統合が複雑 |

### Task Tool並列実行

1メッセージ内で複数Task toolを呼び出すことで真の並列実行を実現。

**各Task toolへ渡すContext設計**:
```yaml
prompt: |
  ## Task: [タスク名]
  ### Issue Contract
  - Goal: [目的]
  - Invariants: [制約]
  ### 調査対象
  - [ファイルパス]（内容は含めずパスのみ）
  ### リソース（必要に応じて読み取り）
  - [参照パス]
  ### 出力
  - [期待する出力形式]
```

### 結果統合

並列タスク完了後:
1. 各Task toolの出力を収集
2. 整合性チェック（Law/Term間の矛盾、Evidence不整合を検出）
3. Evidence統合
4. 失敗タスクは順次再試行、50%以上失敗なら並列中止

並列実行パターンと失敗処理の詳細は [parallel-patterns.md](references/parallel-patterns.md) を参照（失敗時の対応に迷った時に読む）。

### 停止条件

以下が発生したら並列実行を中止し、順次実行に切り替え:

- 並列タスクの50%以上が失敗
- Context window制約でTask tool実行不可
- 結果統合で解決不能な矛盾が発生

---

## 使用例

```
User: ユーザー認証システムを実装して

Claude:
# Planning: ユーザー認証システム

## Phase 1: タスク分解

### Level 0: Root Task
**Goal**: JWT認証による安全なユーザー認証
**Constraints**: OWASP準拠、既存DBスキーマ活用

### Level 1: Major Components
1.1 認証コア（30-40min, Parallel: Yes）
1.2 セッション管理（20-30min, Depends: 1.1）
1.3 APIエンドポイント（30-40min, Depends: 1.1, 1.2）

### Level 2: Atomic Tasks（1.1の例）
1.1.1 JWTペイロード型定義（5min, L0, TERM-jwt-payload）
1.1.2 トークン生成関数（8min, L1, LAW-token-expiry）
1.1.3 トークン検証関数（8min, L1, LAW-token-signature）

## Phase 2: スコープ設計

| From | To | Inherit | Return |
|------|-----|---------|--------|
| Root | 1.1 | ADR-003, セキュリティ要件 | トークン仕様 |
| 1.1 | 1.1.1 | JWTペイロード仕様 | 型定義ファイル |
| 1.1 | 1.1.2 | LAW-token-expiry | generateToken実装 |

## Phase 3: 並列化

### Wave 1（並列実行）
- 1.1.1 JWTペイロード型定義
- 1.1.2 トークン生成関数
- 1.1.3 トークン検証関数
→ 3タスクを同時にTask tool実行

### Wave 2（Wave 1完了後）
- 1.2 セッション管理

分解完了。Wave 1から開始しますか？
```

---

## 品質原則

1. **Epistemic Humility**: 推測を事実として扱わない
2. **Evidence First**: 結論ではなく因果と証拠を中心にする
3. **Minimal Change**: 最小単位で変更し即時検証する

### 完了の定義

- Evidence Ladder目標レベル達成
- Law/Termが接地している
- ロールバック可能な状態
