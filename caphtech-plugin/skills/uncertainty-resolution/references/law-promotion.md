# Law昇格の詳細

## 昇格条件

仮説がLawに昇格するための全条件：

| 条件 | 説明 | 必須 |
|------|------|------|
| Validated | 観測タスクで検証済み | Yes |
| Reproducible | 複数回/セッションで再確認 | Yes |
| Impactful | ビジネス影響度 >= 3 | Yes |
| Enforceable | 検証・観測手段が定義可能 | Yes |
| Documented | 証拠が記録されている | Yes |

## Law Type判定

| 仮説の性質 | Law Type | 判定基準 |
|-----------|----------|---------|
| 常に成り立つべき条件 | Invariant | 状態に関する制約 |
| 操作の前提条件 | Pre | 入力に関する制約 |
| 操作の結果保証 | Post | 出力に関する制約 |
| 状況依存の判断規則 | Policy | 条件分岐を含む |

## Law Card生成テンプレート

```yaml
law_card_draft:
  id: LAW-<domain>-<name>
  type: <判定されたType>
  scope: <適用範囲>
  statement: <仮説を法則形式に変換>
  formal_ish: <疑似式>

  evidence:
    source: <証拠の出典>
    validation_method: <検証方法>
    confirmed_in: <確認セッション数>

  verification:
    test: <テスト案>
    runtime_check: <実行時チェック案>

  observability:
    telemetry: <メトリクス案>
    log_event: <イベント案>
```

## 変換パターン例

**仮説**: 「在庫更新は原子的に行う必要がある」

```markdown
## LAW-inv-atomic-update
- Type: Invariant
- Scope: inventory.updateStock
- Statement: 在庫更新は単一トランザクション内で完結し、中間状態が外部から観測されない
- Formal-ish: forall t: visible(stock(t)) in {before, after} (not intermediate)
```

**仮説**: 「VIPユーザーは在庫切れでも予約できる」

```markdown
## LAW-policy-vip-backorder
- Type: Policy
- Scope: order.create
- Statement: VIPユーザー（tier >= gold）は利用可能在庫を超えてバックオーダー可能
- Formal-ish: if (user.tier >= gold) then orderQty > available is allowed
```

## 昇格レポート形式

```markdown
# Uncertainty to Law Report

## 昇格候補

### U-001 -> LAW-inv-atomic-update (推奨: 昇格)

**元の仮説**: 在庫更新は原子的に行う必要がある
**検証状態**: Validated
**証拠**: 並行テストで競合条件を確認 (tests/concurrent.test.ts)
**影響度**: 4/5
**確認セッション**: 3回

**生成Law Card**:
- Type: Invariant
- Scope: inventory.updateStock
- Statement: 在庫更新は単一トランザクション内で完結
- Severity案: S1

**接地案**:
- Test: prop_atomic_update (PBT)
- Runtime: トランザクション境界アサーション
- Telemetry: law.inventory.atomic_update.*

-> `/lde-law-card` で正式化しますか？

### U-003 (昇格保留)

**元の仮説**: キャンセルは24時間以内のみ可能
**検証状態**: Partially Validated
**理由**: ビジネス要件の確認が必要（例外ケースの扱い）

-> 追加の観測タスクを作成しますか？
```

## pce-memory連携

昇格履歴の記録:
```
pce_memory_upsert:
  category: law_promotion
  content: |
    U-001 -> LAW-inv-atomic-update
    - 昇格日: 2024-12-21
    - 元仮説: 在庫更新は原子的に行う必要がある
    - 検証方法: 並行テスト
    - 証拠: tests/concurrent.test.ts
  tags: ["law-promotion", "uncertainty", "inventory"]
```

過去の昇格パターン参照:
```
pce_memory_activate:
  tags: ["law-promotion"]
```
