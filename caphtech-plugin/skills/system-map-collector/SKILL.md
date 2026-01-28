---
name: system-map-collector
context: fork
description: |
  システムマップを収集・作成するスキル。コードベースを調査し、アーキテクチャ情報をYAML形式で出力する。

  使用タイミング:
  - 「システムマップを作成して」「アーキテクチャを調査して」
  - 「コンポーネント一覧を作成して」「依存関係を調べて」
  - 「データフローを整理して」「境界を特定して」
  - プロジェクトの全体像を把握したい時
---

# System Map Collector

コードベースを調査し、システムマップをYAML形式で作成する。

**重要**: 品質確保のため、一度に1項目のみ収集する。

## ワークフロー

```
1. 定義ファイル作成 → 2. 項目選択 → 3. 調査 → 4. YAML出力 → 5. 次の項目へ
```

## Phase 1: 定義ファイル作成

`system-map/definition.yaml` を作成。テンプレートは [references/definition-template.md](references/definition-template.md) を参照。

```bash
mkdir -p system-map
# definition.yaml を作成
```

## Phase 2: 項目収集

1. `system-map/definition.yaml` を読み込む
2. 未収集項目を確認し、1つ選択
3. Exploreエージェントまたはkiri MCPで調査
4. 結果を `system-map/{item-id}.yaml` に出力

### 調査方法

```
Task(subagent_type="Explore", prompt="...")
# または
context_bundle(goal="...")
deps_closure(path="...", direction="both")
```

### 出力形式

[references/output-schema.md](references/output-schema.md) を参照。

```yaml
id: components
name: コンポーネント一覧
collected_at: 2024-01-21T10:00:00+09:00
confidence: high
items:
  - id: comp-001
    name: ...
```

## Phase 3: 進捗管理

`system-map/progress.yaml` で進捗を管理:

```yaml
total_items: 14
completed: 3
items:
  - id: components
    status: completed
    file: components.yaml
  - id: dependencies
    status: in_progress
  - id: data-flow
    status: pending
```

## 注意事項

- 複数項目を同時に収集しない
- 既存の `system-map/*.yaml` を確認して重複を避ける
- 不明な点は推測せず「不明」と記載する
