---
name: pce-orchestrate
description: |
  PCE (Process-Context Engine) の統合オーケストレーションスキル。PCEサイクル全体を管理し、他のPCEスキルを適切なタイミングで起動する。

  トリガー条件:
  - 複雑なタスクを開始する時
  - 「PCEで進めて」
  - 「コンテキスト駆動で実装して」
  - プロジェクト全体を見渡す必要がある時
---

# PCE Orchestrate Skill

PCE循環全体を管理し、各スキルを適切に起動してプロセスを駆動する。

## PCE循環モデル

```
潜在プール → [Compile] → アクティブコンテキスト → [実行] → 成果物 → [Capture] → 潜在プール
     ↑                                                              ↓
     └──────────────────────── [Merge] ←───────────────────────────┘
```

## オーケストレーションフロー

### Phase 1: 準備 (Activation)
1. **pce-activation** でアクティブコンテキストを構築
2. Goal/Constraints/References/Expected Output を明確化
3. 必要なpce-memory参照を取得

### Phase 2: 分解 (Scope)
1. **pce-scope** でタスクを入れ子構造に分解
2. 各子タスクへの継承コンテキストを設計
3. 並列実行可能なタスクを特定

### Phase 3: 実行 (Execute)
1. 各タスクを実行（コード生成、分析、等）
2. 子タスクからの戻り値を収集
3. 問題発生時は即座に対応

### Phase 4: 評価 (Evaluate)
1. **pce-evaluate** で成果物を検証
2. 品質基準との整合性確認
3. 問題があれば修正ループへ

### Phase 5: 収集 (Collection)
1. **pce-collection** でContext Deltaを収集
2. 意思決定の痕跡を記録
3. パターン/アンチパターンを抽出

### Phase 6: 構造化 (Structuring)
1. **pce-structuring** で知識を永続化
2. 適切な出力先に配置
3. 既存知識との統合

### Phase 7: 圧縮 (Compact)
1. **pce-compact** で長期履歴を圧縮（必要時）
2. セッションノート作成
3. 次回への引き継ぎ準備

## スキル起動マトリクス

| 状況 | 起動するスキル |
|------|---------------|
| タスク開始時 | pce-activation |
| 複数人で分担 | pce-scope |
| 成果物完成時 | pce-evaluate → pce-collection |
| 知見が蓄積 | pce-structuring |
| セッション長期化 | pce-compact |

## 使用例

```
User: ユーザー管理機能をPCEで実装して

Claude:
## PCE Orchestration Start

### Phase 1: Activation
アクティブコンテキストを構築中...
- Goal: ユーザーCRUD + 権限管理
- Constraints: 既存認証と統合
- References: src/auth/, docs/adr/ADR-003.md

### Phase 2: Scope
タスク分解:
1. Userモデル拡張
2. CRUD API実装
3. 権限チェックミドルウェア
4. テスト作成

### Phase 3-4: Execute & Evaluate
[実装 → 評価を各タスクで実行]

### Phase 5-6: Collection & Structuring
収集した知見:
- 権限継承パターン → pce-memory
- API設計決定 → ADR-006作成

### Phase 7: Compact
セッションノートを作成しました。

PCE循環完了。
```
