# 依存関係グラフ構築ガイド

タスク間の依存関係を正確に分析し、並列実行可能性を判定するための詳細ガイド。

## 依存関係の種類

### 1. データ依存（Data Dependency）

**定義**: タスクBがタスクAの出力を入力として使用する

**例**:
```yaml
task-A:
  name: "コードベース調査"
  output: ["調査レポート: src/auth/*の関数一覧"]

task-B:
  name: "Law候補抽出"
  depends_on: ["task-A"]
  input: ["調査レポート"]
  reason: "調査レポートがなければLaw抽出できない"
```

**並列実行**: **不可** → タスクAの完了後にタスクBを実行

**検出方法**:
```yaml
check:
  - task-B.input に task-A.output が含まれるか
  - task-B.depends_on に task-A.id が含まれるか
```

---

### 2. 制御依存（Control Dependency）

**定義**: タスクBの実行条件がタスクAの結果に依存する

**例**:
```yaml
task-A:
  name: "リスク判定"
  output: ["リスクレベル: High"]

task-B:
  name: "worktree作成"
  depends_on: ["task-A"]
  condition: "task-A.output.risk_level == 'High' or 'Critical'"
  reason: "リスクレベルがHigh/Criticalの場合のみ実行"
```

**並列実行**: **不可** → タスクAの結果判定後にタスクBを実行

**検出方法**:
```yaml
check:
  - task-B に condition フィールドがあり、task-A の結果を参照するか
  - task-B.depends_on に task-A.id が含まれるか
```

---

### 3. リソース依存（Resource Dependency）

**定義**: タスクAとBが同じリソースに書き込みを行う

**例**:
```yaml
task-A:
  name: "Law Card作成"
  output: ["law-catalog/LAW-001.yaml"]
  write_to: "law-catalog/"

task-B:
  name: "Law Card作成"
  output: ["law-catalog/LAW-002.yaml"]
  write_to: "law-catalog/"

conflict:
  type: "同一ディレクトリへの並行書き込み"
  risk: "ファイル競合、Git conflict"
```

**並列実行**: **条件付き可**
- ファイル名が異なれば並列実行可能（LAW-001 vs LAW-002）
- 同一ファイルへの書き込みは順次実行が必要

**検出方法**:
```yaml
check:
  - task-A.write_to と task-B.write_to が重複するか
  - task-A.output と task-B.output が同一ファイルか
```

---

### 4. Evidence依存（Evidence Dependency）

**定義**: タスクBのEvidence収集がタスクAのEvidence達成に依存する

**例**:
```yaml
task-A:
  name: "実装"
  evidence_level: L0
  output: ["実装コード"]

task-B:
  name: "ユニットテスト作成"
  evidence_level: L1
  depends_on: ["task-A"]
  reason: "実装コードがなければテストを書けない"
```

**並列実行**: **不可** → 実装→テストの順序は守る必要がある

**検出方法**:
```yaml
check:
  - task-B.evidence_level > task-A.evidence_level
  - task-B が task-A のコードをテスト対象とするか
```

---

## 依存関係グラフの構築

### ステップ1: タスクノードの抽出

`eld-sense-task-decomposition`の出力から全タスクを抽出。

**入力例**:
```yaml
tasks:
  - id: task-1
    name: "コードベース調査"
    depends_on: []
    input: []
    output: ["調査レポート"]

  - id: task-2
    name: "Law候補抽出"
    depends_on: ["task-1"]
    input: ["調査レポート"]
    output: ["Law候補リスト"]

  - id: task-3
    name: "Term候補抽出"
    depends_on: ["task-1"]
    input: ["調査レポート"]
    output: ["Term候補リスト"]

  - id: task-4
    name: "Link Map作成"
    depends_on: ["task-2", "task-3"]
    input: ["Law候補リスト", "Term候補リスト"]
    output: ["Link Map"]
```

**ノード抽出**:
```
ノード: task-1, task-2, task-3, task-4
```

---

### ステップ2: エッジの抽出

各タスクの`depends_on`フィールドからエッジを抽出。

**エッジ抽出**:
```
task-1 → task-2 (データ依存: 調査レポート)
task-1 → task-3 (データ依存: 調査レポート)
task-2 → task-4 (データ依存: Law候補リスト)
task-3 → task-4 (データ依存: Term候補リスト)
```

---

### ステップ3: グラフの可視化

```
         task-1 (調査)
           /        \
          /          \
    task-2 (Law)    task-3 (Term)
          \          /
           \        /
         task-4 (Link Map)
```

**グラフの特徴**:
- **菱形構造**: task-1 → (task-2, task-3) → task-4
- **並列実行可能**: task-2 と task-3（共通の依存元task-1のみ）
- **順次実行必須**: task-1 → task-4（task-4は2つの前提タスクあり）

---

### ステップ4: 並列実行可能性の判定

**アルゴリズム**:

```python
def can_run_in_parallel(task_a, task_b, graph):
    """2つのタスクが並列実行可能か判定"""

    # 1. データ依存チェック
    if has_data_dependency(task_a, task_b):
        return False

    # 2. 制御依存チェック
    if has_control_dependency(task_a, task_b):
        return False

    # 3. リソース依存チェック
    if has_resource_conflict(task_a, task_b):
        return False

    # 4. Evidence依存チェック
    if has_evidence_dependency(task_a, task_b):
        return False

    return True

def has_data_dependency(task_a, task_b):
    """データ依存があるか"""
    # task_b が task_a の出力を入力として使うか
    return (task_a.id in task_b.depends_on or
            any(out in task_b.input for out in task_a.output))

def has_control_dependency(task_a, task_b):
    """制御依存があるか"""
    # task_b の実行条件が task_a の結果に依存するか
    return (hasattr(task_b, 'condition') and
            task_a.id in task_b.condition)

def has_resource_conflict(task_a, task_b):
    """リソース競合があるか"""
    # 同一ファイル/ディレクトリへの書き込みがあるか
    return (task_a.write_to == task_b.write_to and
            any(out in task_b.output for out in task_a.output))

def has_evidence_dependency(task_a, task_b):
    """Evidence依存があるか"""
    # task_b が task_a のコードをテスト対象とするか
    return (task_b.evidence_level > task_a.evidence_level and
            task_a.id in task_b.depends_on)
```

**判定例**:

```python
# task-2 と task-3 の並列実行可能性
can_run_in_parallel(task_2, task_3, graph)
# → True (共通の依存元task-1のみ、相互依存なし)

# task-1 と task-2 の並列実行可能性
can_run_in_parallel(task_1, task_2, graph)
# → False (task-2 が task-1 の出力に依存)
```

---

## 並列実行セットの抽出

### レベルベース抽出

**定義**: 依存関係グラフのレベル（深さ）ごとにタスクをグループ化

**アルゴリズム**:

```python
def extract_parallel_sets(graph):
    """並列実行可能なタスクセットを抽出"""
    levels = []
    visited = set()

    # レベル0: 依存元がないタスク
    level_0 = [task for task in graph.nodes
               if len(task.depends_on) == 0]
    levels.append(level_0)
    visited.update(level_0)

    # レベル1以降: 前レベルのタスクのみに依存するタスク
    while True:
        prev_level = levels[-1]
        next_level = []

        for task in graph.nodes:
            if task in visited:
                continue

            # このタスクの依存元がすべて前レベルまでに含まれるか
            if all(dep in visited for dep in task.depends_on):
                next_level.append(task)

        if not next_level:
            break

        levels.append(next_level)
        visited.update(next_level)

    return levels
```

**適用例**:

```yaml
graph:
  - task-1 (調査)
  - task-2 (Law抽出) depends_on: [task-1]
  - task-3 (Term抽出) depends_on: [task-1]
  - task-4 (Link Map) depends_on: [task-2, task-3]

levels:
  level-0: [task-1]           # 並列実行セット1
  level-1: [task-2, task-3]   # 並列実行セット2
  level-2: [task-4]           # 並列実行セット3
```

**実行順序**:
```
1. level-0 を実行: task-1
2. task-1 完了後、level-1 を並列実行: task-2 || task-3
3. level-1 完了後、level-2 を実行: task-4
```

---

### 動的並列度調整

並列実行中にリソース制約や失敗が発生した場合、動的に並列度を調整。

**調整ルール**:

```yaml
initial_parallelism: 4  # 初期並列度

adjustment_triggers:
  - condition: "Memory usage > 80%"
    action: "並列度を半減"
    new_parallelism: 2

  - condition: "Task failure rate > 30%"
    action: "並列度を1に削減（順次実行）"
    new_parallelism: 1

  - condition: "Context window usage > 90%"
    action: "並列度を1に削減"
    new_parallelism: 1
```

**実装例**:

```python
def adjust_parallelism(current, stats):
    """並列度を動的調整"""
    if stats.memory_usage > 0.8:
        return max(1, current // 2)

    if stats.failure_rate > 0.3:
        return 1

    if stats.context_usage > 0.9:
        return 1

    return current
```

---

## 依存関係グラフの実例

### 例1: 新機能開発の調査フェーズ

```yaml
scenario: "ユーザー認証機能の調査"

tasks:
  - id: survey-1
    name: "既存認証コード調査"
    depends_on: []
    output: ["既存実装レポート"]

  - id: survey-2
    name: "認証関連テスト調査"
    depends_on: []
    output: ["テストカバレッジレポート"]

  - id: survey-3
    name: "外部依存ライブラリ調査"
    depends_on: []
    output: ["依存関係レポート"]

  - id: analysis-1
    name: "Law候補抽出"
    depends_on: ["survey-1", "survey-2"]
    input: ["既存実装レポート", "テストカバレッジレポート"]
    output: ["Law候補リスト"]

  - id: analysis-2
    name: "Term候補抽出"
    depends_on: ["survey-1"]
    input: ["既存実装レポート"]
    output: ["Term候補リスト"]

dependency_graph:
  level-0: [survey-1, survey-2, survey-3]  # 3タスク並列実行
  level-1: [analysis-1, analysis-2]         # 2タスク並列実行

time_estimate:
  sequential: 5タスク × 10分 = 50分
  parallel:
    - level-0: 10分（3タスク並列）
    - level-1: 10分（2タスク並列）
    - 合計: 20分（60%時間短縮）
```

---

### 例2: マイクロサービス並列実装

```yaml
scenario: "3つのマイクロサービスを並列実装"

tasks:
  - id: service-A
    name: "ユーザー認証サービス実装"
    depends_on: []
    write_to: "services/auth/"
    evidence_level: L1

  - id: service-B
    name: "商品カタログサービス実装"
    depends_on: []
    write_to: "services/catalog/"
    evidence_level: L1

  - id: service-C
    name: "注文処理サービス実装"
    depends_on: []
    write_to: "services/order/"
    evidence_level: L1

  - id: integration
    name: "サービス統合テスト"
    depends_on: ["service-A", "service-B", "service-C"]
    evidence_level: L2

dependency_graph:
  level-0: [service-A, service-B, service-C]  # 3サービス並列実装
  level-1: [integration]                       # 統合テスト

resource_independence:
  - 各サービスは独立したディレクトリに書き込み
  - 共有状態なし（独立したDB）
  - Evidence Levelも独立（それぞれL1達成）

time_estimate:
  sequential: 3サービス × 40分 + 統合20分 = 140分
  parallel:
    - level-0: 40分（3サービス並列）
    - level-1: 20分（統合テスト）
    - 合計: 60分（57%時間短縮）
```

---

## トラブルシューティング

### 循環依存の検出

**症状**: タスクAがタスクBに依存し、タスクBがタスクAに依存

**検出**:
```python
def detect_circular_dependency(graph):
    """循環依存を検出"""
    visited = set()
    stack = set()

    def dfs(task):
        if task in stack:
            return True  # 循環依存検出
        if task in visited:
            return False

        visited.add(task)
        stack.add(task)

        for dep in task.depends_on:
            if dfs(graph.get_task(dep)):
                return True

        stack.remove(task)
        return False

    for task in graph.nodes:
        if dfs(task):
            return True

    return False
```

**対策**: タスク分解を見直し、依存関係を一方向に整理

---

### 隠れた依存の検出

**症状**: `depends_on`に記載されていないが、実際には依存している

**例**:
```yaml
task-A:
  name: "設定ファイル更新"
  write_to: "config/app.yaml"

task-B:
  name: "アプリケーション起動"
  depends_on: []  # ← 本当は task-A に依存
  read_from: "config/app.yaml"
```

**検出**:
```python
def detect_hidden_dependency(task_a, task_b):
    """隠れた依存を検出"""
    # task_B が task_A の出力を読み取るか
    return any(out in task_b.read_from
               for out in task_a.write_to)
```

**対策**: `depends_on`を明示的に追加

---

## まとめ

### 依存関係グラフ構築の核心原則

1. **4種類の依存を漏れなく検出**: データ/制御/リソース/Evidence
2. **レベルベースで並列セット抽出**: 深さ優先で並列実行可能タスクをグループ化
3. **循環依存の排除**: タスク分解を見直し、一方向の依存関係に整理
4. **動的並列度調整**: リソース制約や失敗率に応じて並列度を削減

### 並列実行可能性の判定チェックリスト

- [ ] データ依存: task_B.input に task_A.output が含まれないか
- [ ] 制御依存: task_B の実行条件が task_A の結果に依存しないか
- [ ] リソース依存: 同一ファイル/ディレクトリへの書き込み競合がないか
- [ ] Evidence依存: task_B が task_A のコードをテスト対象としないか
- [ ] 循環依存: タスクグラフに循環がないか
