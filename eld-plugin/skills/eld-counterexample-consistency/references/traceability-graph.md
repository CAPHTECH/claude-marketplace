# トレーサビリティグラフ

要件、仕様、テスト、コード、観測を、要件IDで一つのグラフとして扱う。

## ノード

| ID | 内容 | 例 |
|----|------|----|
| `REQ_i` | 要件原子 | `REQ-order-102` |
| `F_i` | 形式仕様 | TLA+、Alloy、SMT、LTL |
| `T_i` | 実行テスト | example test、property-based test、stateful test |
| `K_i` | コード内契約 | precondition、postcondition、invariant |
| `C_i` | 実装シンボル | 関数、API、イベント、状態機械 |
| `M_i` | 実行時監視 | trace rule、alert rule、dashboard query |

## 基本辺

```text
REQ_i ↔ F_i ↔ T_i ↔ K_i ↔ C_i ↔ M_i
```

各辺は、単なる参照ではなく「どの証拠で結んだか」を持つ。

## 最小マトリクス

```markdown
| req_id | formal_spec | tests | contracts | code_symbols | runtime_rules | gaps |
|--------|-------------|-------|-----------|--------------|---------------|------|
| REQ-order-102 | order_reservation.tla | test_order_reservation.py | reservation_count <= 1 | reserveInventory | trace rule 102 | MISSING_MUTATION |
```

## 変更影響の見方

- `C_i` が変わったのに `T_i` と `M_i` が変わらないなら、検査漏れ候補
- `REQ_i` が変わったのに `F_i` と `T_i` が変わらないなら、形式化漏れ候補
- `M_i` が存在しない高リスク要件は、運用整合性を主張しない

## 辺の証拠例

| Link | 必要な証拠 |
|------|------------|
| `REQ_i -> F_i` | 同じ制約を表す節、または相互含意の確認 |
| `REQ_i -> T_i` | 期待結果と禁止結果が要件欄に対応している |
| `REQ_i -> K_i` | 事前条件、事後条件、不変条件が要件に一致する |
| `REQ_i -> M_i` | trace または metric に要件IDと判定材料が載る |

## 欠落の扱い

欠落は「まだ証明できない」を意味する。矛盾より軽く見積もらず、独立した finding として残す。
