---
name: lde-pce-workflow
description: |
  PCE（Process-Context Engine）とLDE（Law-Driven Engineering）を統合した開発ワークフロー。
  名辞抽象（Vocabulary）と関係抽象（Law）の相互拘束を維持しながら、
  Issue受付から実装・レビュー・運用までの開発ライフサイクル全体を管理する。
  使用タイミング: (1) 新機能開発を開始する時、(2) 「PCE-LDEで進めて」、
  (3) Issueから実装までを一貫して進めたい時、(4) Law駆動でコンテキスト管理したい時
---

# LDE-PCE Workflow

PCE循環とLDEフェーズ（A-F）を統合し、開発ライフサイクル全体を管理する。

## 統合モデル

```
Issue → [Phase 0] → [LDE Phase A-B] → [LDE Phase C-D] → [LDE Phase E-F] → 運用学習
              ↓              ↓                 ↓                 ↓            ↓
       不確実性解消    Vocabulary/Law同定   Card化/Link Map    接地/実装     監視/改善
              ↓              ↓                 ↓                 ↓            ↓
         pce-memory ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

## Phase 0: Issue解析（PCE Activation）

### 入力
- Issue（GitHub Issue/ファイルベースIssue）
- 関連するADR・ドキュメント

### プロセス
1. Issueから要件を抽出
2. `/resolving-uncertainty` で不確実性を特定
3. 仮説を立て、観測タスクで検証
4. 必要なVocabulary/Law候補を列挙

### 出力
- 明確化された要件
- 解消済み不確実性リスト
- Vocabulary候補リスト
- Law候補リスト

### 使用スキル
- `resolving-uncertainty`
- `pce-activation`

## Phase 1: Vocabulary/Law同定（LDE Phase A-B）

### LDE Phase A: Vocabulary同定（名辞抽象の初期固定）

1. **入力**: 要件、ドメイン知識、既存用語
2. **プロセス**:
   - `/lde-law-discovery` でコードベースから既存語彙を発見
   - 同義語と境界（どこで使う言葉か）を明確化
3. **出力**: Vocabulary Catalog v0
4. **完了条件**: 同義語と境界が書かれている

### LDE Phase B: Law同定（関係抽象の初期固定）

1. **入力**: 要件、障害履歴、監査要件、運用手順
2. **プロセス**:
   - "壊れると困る関係"からLawを書く（S0/S1優先）
   - `/lde-law-discovery` でコードベースから既存Lawを発見
3. **出力**: Law Catalog v0
4. **完了条件**: 主要な「壊れ方」がLawに紐づく

### pce-memory記録
- Vocabulary Catalog v0
- Law Catalog v0

### 使用スキル
- `lde-law-discovery`
- `pce-activation`

## Phase 2: Card化（LDE Phase C-D + PCE Execute）

### LDE Phase C: Law Card化（関係を仕様化）

1. `/lde-law-card` でLaw Card作成
   - Scope/例外/違反時動作を明確化
   - **Terms欄に参照するTermを明示**（必須）
2. `/lde-link-map` でLaw → Term参照を記録
3. 孤立Lawがないことを確認

### LDE Phase D: Term Card化（名辞を運用可能に固定）

1. `/lde-term-card` でTerm Card作成
   - 意味・境界・観測写像を明確化
   - **Related Lawsに関連Lawを明示**（S0/S1は必須）
2. `/lde-link-map` でTerm → Law逆引きを記録
3. 孤立S0/S1 Termがないことを確認

### 相互拘束チェック
```yaml
mutual_constraint_check:
  - all_laws_have_terms: true | false
  - all_s0s1_terms_have_laws: true | false
  - link_map_updated: true | false
```

### 使用スキル
- `lde-law-card`
- `lde-term-card`
- `lde-link-map`
- `pce-task-decomposition`

## Phase 3: 接地・実装（LDE Phase E-F）

### LDE Phase E: 接地（Grounding）

1. `/lde-grounding-check` で接地状況を検証
   - **Law**: 検証（Test/Runtime）+ 観測（Telemetry/Log）
   - **Term**: 観測フィールド + 境界での検証/正規化
2. 不足があれば追加

### 接地要件

| 対象 | 重要度 | 検証手段 | 観測手段 |
|------|--------|---------|---------|
| Law | S0 | **必須** (Test + Runtime) | **必須** (Telemetry全量) |
| Law | S1 | **必須** (Test or Runtime) | **必須** (Telemetry) |
| Term | S0/S1 | 境界での検証/正規化 | Observable Fields |

### LDE Phase F: 実装（Pure/IO分離）

1. Lawの中核はPure関数で実装
2. IO境界を集約
3. 違反分類（Bug/User/Exception/Data/Compliance）を統一

### Law遵守実装パターン

```typescript
// Pre条件
function reserveStock(orderId: OrderId, qty: Quantity): Result<Reservation, Error> {
  // LAW-pre-order-quantity: orderQty ≤ available
  // Terms: TERM-order-quantity, TERM-inventory-available
  if (qty > getAvailableStock()) {
    return Err(new InsufficientStockError());
  }
  // ...
}

// Invariant
class Inventory {
  // LAW-inv-available-balance: available = total - reserved
  // Terms: TERM-inventory-available, TERM-inventory-total, TERM-inventory-reserved
  private assertInvariant(): void {
    assert(this.available === this.total - this.reserved);
  }
}
```

### 使用スキル
- `lde-grounding-check`
- `pce-scope`
- `pce-evaluate`

## Phase 4: レビュー・統合（PCE Capture）

### プロセス
1. `/pce-pr-review` でLaw観点のレビュー
   - Law遵守チェック
   - Term境界検証チェック
   - Link Map整合性確認
2. `/lde-grounding-check` でCI/CD検証
3. `pce-collection` で知見収集
4. `pce-structuring` で永続化

### レビュー観点（名辞×関係統合）

| チェック項目 | 確認内容 |
|-------------|---------|
| Law遵守 | 新規/変更コードがLawに違反していないか |
| Term整合性 | Term定義と実装が一致しているか |
| 接地完了 | Law/TermにTest/Telemetryが設定されているか |
| 孤立なし | Link Mapで孤立がないか |
| 失敗パターン | 名辞インフレ/関係スープの兆候がないか |

### 使用スキル
- `pce-pr-review`
- `lde-grounding-check`
- `lde-link-map`
- `pce-collection`
- `pce-structuring`

## Phase 5: 運用・学習（PCE循環）

### プロセス
1. `/pce-law-monitor` で実行時Law/Term違反を監視
2. 違反パターンをpce-memoryに記録
3. `/uncertainty-to-law` で検証済み仮説をLaw化
4. Vocabulary/Law Catalog・Link Map更新
5. `pce-compact` でセッションノート作成

### フィードバックループ
```
本番違反検知 → pce-memory記録 → パターン分析 → Vocabulary/Law候補生成 → Catalog更新
```

### 使用スキル
- `pce-law-monitor`
- `uncertainty-to-law`
- `pce-compact`
- `pce-knowledge-transfer`

## クイックリファレンス

### Phase別スキル起動

| Phase | トリガー | LDE Phase | 起動スキル |
|-------|---------|-----------|-----------|
| 0 | Issue受付時 | - | resolving-uncertainty, pce-activation |
| 1 | 設計開始時 | A-B | lde-law-discovery |
| 2 | カード化時 | C-D | lde-law-card, lde-term-card, lde-link-map |
| 3 | 実装時 | E-F | lde-grounding-check, pce-evaluate |
| 4 | PR作成時 | - | pce-pr-review, pce-collection |
| 5 | マージ後 | - | pce-law-monitor, pce-compact |

### ワークフロー選択

| 状況 | 推奨ワークフロー |
|------|----------------|
| 新機能開発 | Phase 0-5 フル実行 |
| バグ修正 | Phase 3-4（影響Law/Termの確認含む） |
| リファクタリング | Phase 1-4（Vocabulary/Law変更影響分析含む） |
| 緊急対応 | Phase 3-4 簡略版 + 後追いVocabulary/Law整備 |

### トラック選択

| トラック | 対象 | Vocabulary/Law管理 |
|----------|------|-------------------|
| **Simple** | CRUD中心、低リスク | 重要なもののみCard化 |
| **Standard** | 状態整合が重要 | 主要なもの全てCard化 + Link Map必須 |
| **Complex** | ミッションクリティカル | 形式仕様 + Impact Graph |
