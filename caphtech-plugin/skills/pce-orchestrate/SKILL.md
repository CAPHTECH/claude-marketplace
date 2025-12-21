---
name: pce-orchestrate
description: |
  PCE (Process-Context Engine) の統合オーケストレーションスキル。PCEサイクル全体を管理し、他のPCEスキルを適切なタイミングで起動する。
  LDE（Law-Driven Engineering）との統合により、Law駆動のコンテキスト管理も実現。

  トリガー条件:
  - 複雑なタスクを開始する時
  - 「PCEで進めて」
  - 「コンテキスト駆動で実装して」
  - プロジェクト全体を見渡す必要がある時
  - LDEプロジェクトでの開発ライフサイクル管理
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

## LDE統合フロー

LDEプロジェクトでは、PCE循環にLawフェーズを統合する：

```
PCE Phase          LDE Phase           統合スキル
─────────────────────────────────────────────────────
Activation    ←→   Phase A: Law同定    lde-law-discovery
Scope         ←→   Phase B: Lawカード  lde-law-card
Execute       ←→   Phase C-D: 接地実装  lde-grounding-check
Evaluate      ←→   Law検証             pce-evaluate (Law観点)
Collection    ←→   Phase E: 変更運用    pce-law-monitor
```

### LDE統合時の追加ステップ

1. **Phase 1拡張**: `/lde-law-discovery` で既存Law発見
2. **Phase 3拡張**: Law遵守チェックを実装に統合
3. **Phase 4拡張**: `/lde-grounding-check` でLaw接地検証
4. **Phase 5拡張**: `/pce-law-monitor` で違反パターン収集
5. **Phase 6拡張**: `/uncertainty-to-law` で新Law候補を構造化

詳細なLDE統合ワークフローは `/lde-pce-workflow` を参照。

## スキル起動マトリクス

| 状況 | 起動するスキル |
|------|---------------|
| タスク開始時 | pce-activation |
| 複数人で分担 | pce-scope |
| 成果物完成時 | pce-evaluate → pce-collection |
| 知見が蓄積 | pce-structuring |
| セッション長期化 | pce-compact |

### LDE統合時の追加マトリクス

| 状況 | 起動するスキル |
|------|---------------|
| Law発見が必要 | lde-law-discovery |
| 新Law定義時 | lde-law-card |
| PR前の接地確認 | lde-grounding-check |
| Law違反監視 | pce-law-monitor |
| 仮説のLaw化 | uncertainty-to-law |

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
