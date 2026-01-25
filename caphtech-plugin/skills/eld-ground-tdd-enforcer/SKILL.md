---
name: eld-ground-tdd-enforcer
description: |
  TDDサイクル（RED-GREEN-REFACTOR）を強制するスキル。
  Evidence Ladder L1（ユニットテスト）を最低条件として、テストなし実装を防止。

  トリガー条件:
  - 「TDDで進めて」「テストファーストで実装して」「テスト駆動で」
  - ELD Phase 3: Implementation中の各ステップで自動チェック
  - コミット前の自動検証（git-commit連携）
  - 「テストを先に書いて」
---

# ELD Ground: TDD Enforcer

TDDサイクル（RED-GREEN-REFACTOR）を**強制**し、Evidence Ladder L1（ユニットテスト）達成を保証するスキル。
テストなし実装を許さず、Law Severity別のEvidence要件を満たすまで次に進ませない。

## 核心原則

1. **Test First**: コード実装前に必ずテストを書く（RED状態からスタート）
2. **Evidence L1 Mandatory**: S0/S1 Lawは必ずユニットテストで検証
3. **No Test, No Commit**: テストが通らないコードはコミットしない
4. **Fail Fast**: RED状態が予想外に長引いたら停止し、設計を見直す

## TDDサイクル

### RED → GREEN → REFACTOR

```
┌─ RED ─────────────────────────────────┐
│ 1. テスト作成（失敗することを確認）  │
│    - Law/Term の観測写像をテスト化   │
│    - アサーションは具体的に          │
│    - 期待値を明示                    │
└──────────────────────────────────────┘
         ↓ テストが失敗（RED）
┌─ GREEN ───────────────────────────────┐
│ 2. 最小限の実装（テストが通る）      │
│    - テストを通すだけのコード        │
│    - 過剰な実装はしない              │
│    - まずGREENにする                 │
└──────────────────────────────────────┘
         ↓ テストが成功（GREEN）
┌─ REFACTOR ────────────────────────────┐
│ 3. リファクタリング（動作を保ったまま）│
│    - 重複削除                        │
│    - 名前の改善                      │
│    - 構造の最適化                    │
└──────────────────────────────────────┘
         ↓ テストが成功を維持
         ↓
    次のサイクルへ（新しいテストケース）
```

詳細は `references/tdd-cycle.md` を参照。

## 強制ルール

### ルール1: RED状態の確認

テスト作成後、必ず失敗することを確認:

```bash
# テスト作成
# → テスト実行
# → 失敗することを確認（期待通りのエラーメッセージ）
```

**違反検出**:
- テスト作成直後に即成功 → テストが機能していない可能性
- エラーメッセージが予期しない内容 → テストの前提が間違っている

### ルール2: Law Severity別のEvidence要件

```yaml
S0 Law（ビジネスクリティカル）:
  - L1（ユニットテスト）: 必須 - 違反時動作含む
  - L2（統合テスト）: 必須
  - L3（失敗注入）: 推奨
  - L4（本番Telemetry）: 必須

S1 Law（機能要件）:
  - L1（ユニットテスト）: 必須
  - L2（統合テスト）: 推奨
  - L4（本番Telemetry）: 推奨

S2 Law（品質要件）:
  - L1（ユニットテスト）: オプション
  - L4（本番Telemetry）: 推奨
```

**強制ポイント**:
- S0/S1 Lawは L1なしで実装不可
- テストが存在しない場合、実装開始を拒否

詳細は `references/evidence-ladder.md` を参照。

### ルール3: テストなしコミット禁止

```bash
# コミット前チェック
1. 変更されたコードに対応するテストが存在するか
2. すべてのテストが成功しているか
3. カバレッジが低下していないか
```

**検出方法**:
- Git diff でコード変更を検出
- 対応するテストファイルの有無を確認
- テストが追加/更新されていない場合、拒否

### ルール4: RED状態の時間制限

```yaml
RED状態の許容時間:
  - 5分以内: 正常（実装を続行）
  - 5-15分: 警告（設計の見直しを提案）
  - 15分超: 停止（タスクが大きすぎる。分解が必要）
```

**停止条件**:
- REDが長引く = 設計が複雑すぎる
- タスクを原子化（5-10分単位）に分解して再スタート

詳細は `references/enforcement-rules.md` を参照。

## 実行フロー

### Phase 1: Law/Term の Evidence要件確認

実装開始前に、Law/Termの Evidence要件を確認:

```yaml
対象 Law:
  LAW-xxx (Severity: S0):
    - Evidence要件: L1必須、L2必須、L4必須
    - 既存テスト: なし → テスト作成が必須

対象 Term:
  TERM-yyy (Type: Entity):
    - 観測写像: ID検証、状態遷移チェック
    - 既存テスト: なし → 観測写像のテストが必須
```

**チェックポイント**:
- [ ] S0/S1 Lawのすべてに対応するテストが計画されているか
- [ ] Termの観測写像がテスト可能か

### Phase 2: RED - テスト作成

Law/Termの観測写像をテストコードに変換:

```python
# 例: LAW-stock-non-negative (在庫数は常に0以上)

def test_stock_cannot_be_negative():
    """LAW-stock-non-negative: 在庫数がマイナスになる注文を拒否"""
    product = Product(stock=5)
    order = Order(quantity=10)

    # 期待: 在庫不足エラー
    with pytest.raises(InsufficientStockError) as exc_info:
        product.reserve_stock(order)

    # エラーメッセージ検証
    assert "insufficient stock" in str(exc_info.value).lower()
    # 在庫が変更されていないことを確認
    assert product.stock == 5
```

**チェックポイント**:
- [ ] Law/Termの定義から直接テストが導出されているか
- [ ] 違反時の挙動もテストされているか
- [ ] アサーションが具体的か（単なる `assert True` でないか）

テスト実行 → 失敗を確認（RED状態）

### Phase 3: GREEN - 最小実装

テストを通す最小限のコードを書く:

```python
class Product:
    def __init__(self, stock: int):
        self.stock = stock

    def reserve_stock(self, order: Order):
        if order.quantity > self.stock:
            raise InsufficientStockError(
                f"Insufficient stock: available={self.stock}, required={order.quantity}"
            )
        self.stock -= order.quantity
```

**チェックポイント**:
- [ ] テストが成功するか（GREEN状態）
- [ ] 過剰な実装をしていないか（YAGNIの原則）
- [ ] Law/Termの定義に忠実か

### Phase 4: REFACTOR - リファクタリング

動作を保ったまま、コード品質を改善:

```python
# リファクタリング例:
# - マジックナンバーの除去
# - 名前の改善
# - 重複の削除

class Product:
    def __init__(self, stock: int):
        if stock < 0:
            raise ValueError("Stock cannot be negative")
        self._stock = stock

    @property
    def stock(self) -> int:
        return self._stock

    def reserve_stock(self, order: Order):
        self._validate_stock_availability(order.quantity)
        self._stock -= order.quantity

    def _validate_stock_availability(self, quantity: int):
        if quantity > self._stock:
            raise InsufficientStockError(
                f"Insufficient stock: available={self._stock}, required={quantity}"
            )
```

**チェックポイント**:
- [ ] すべてのテストが成功を維持しているか
- [ ] コードの意図が明確になったか
- [ ] 新しいバグを導入していないか

### Phase 5: コミット前チェック

コミット前に Evidence Ladder 達成を確認:

```bash
# 自動チェックスクリプト
1. すべてのテストが成功しているか
2. S0/S1 Lawに対応するテストが存在するか
3. カバレッジが基準を満たしているか（S0: 100%, S1: 80%）
4. テストが追加/変更されているか
```

**拒否条件**:
- テストが失敗している
- S0/S1 Lawのテストが欠如
- カバレッジが低下

## git-commit 連携

`/git-commit` の前段階として自動実行:

```
実装完了
  ↓
TDD Enforcer チェック
  - Evidence L1 達成確認
  - テスト成功確認
  - カバレッジ確認
  ↓ OK
git-commit
  ↓
  コミット成功
```

**拒否時のメッセージ**:
```
❌ TDD Enforcer: コミット拒否

理由:
- LAW-stock-non-negative (S0) のテストが存在しません
- カバレッジが基準未満です: 現在 65%, 必要 80%

次のアクション:
1. test_stock_non_negative() を作成
2. テストを実行して成功を確認
3. 再度コミットを試行
```

## 例外条件

以下の場合、TDD強制を緩和:

### 例外1: プロトタイピング

```yaml
条件: 技術検証・実験的実装
対応:
  - TDDスキップを明示的に宣言
  - コミットメッセージに [prototype] タグ付与
  - 本番マージ前に必ずテスト追加
```

### 例外2: S2 Law（品質要件）

```yaml
条件: Severity S2 のLaw
対応:
  - L1は推奨だが必須ではない
  - L4（本番Telemetry）で代替可能
```

### 例外3: レガシーコード統合

```yaml
条件: テストのない既存コードの修正
対応:
  - 修正箇所のみテスト追加（完全カバレッジ不要）
  - Characterization Test（既存動作の記録）から開始
```

詳細は `references/enforcement-rules.md` を参照。

## CI/CD統合

### Pre-commit hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# TDD Enforcer チェック
python scripts/tdd_enforcer_check.py

if [ $? -ne 0 ]; then
  echo "❌ TDD Enforcer: テストまたはカバレッジ不足"
  exit 1
fi
```

### GitHub Actions

```yaml
name: TDD Enforcer

on: [pull_request]

jobs:
  tdd-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run TDD Enforcer
        run: |
          pytest --cov --cov-fail-under=80
          python scripts/evidence_ladder_check.py
```

詳細は `references/ci-integration.md` を参照。

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

以下をすべて満たしたら TDD Enforcer 完了:

- [ ] すべての S0/S1 Law に L1テストが存在
- [ ] すべてのテストが成功（GREEN状態）
- [ ] カバレッジが基準を満たす（S0: 100%, S1: 80%）
- [ ] Law違反時の動作もテストされている
- [ ] コミット可能状態

## リファレンス

- `references/tdd-cycle.md` - RED-GREEN-REFACTORサイクルの詳細
- `references/enforcement-rules.md` - 強制ルールと例外条件
- `references/evidence-ladder.md` - Evidence Ladder L1達成基準
- `references/ci-integration.md` - CI/CD統合ガイド

## 使用例

```
User: 在庫管理機能を実装して

Claude: 実装を開始する前に、TDD Enforcerで確認します。

## Evidence要件チェック

対象Law:
- LAW-stock-non-negative (S0): 在庫数は常に0以上
  - Evidence要件: L1必須、L2必須、L4必須
  - 現状: テストなし → 作成が必要

## TDDサイクル開始

### RED: テスト作成

まず、LAW-stock-non-negative のテストを書きます：

[テストコード作成]
[テスト実行 → 失敗を確認]

✅ RED状態を確認しました。

### GREEN: 最小実装

テストを通す最小限のコードを実装します：

[実装コード作成]
[テスト実行 → 成功を確認]

✅ GREEN状態になりました。

### REFACTOR: リファクタリング

コードを改善します：

[リファクタリング]
[テスト実行 → 成功を維持]

✅ REFACTOR完了。

## Evidence L1 達成確認
- LAW-stock-non-negative: テストあり ✅
- カバレッジ: 100% ✅

コミット可能です。
```

---

## 停止条件

以下が発生したら即座に停止し、追加計測またはスコープ縮小：

- 予測と現実の継続的乖離（想定外テスト失敗3回以上）
- 観測不能な変更の増加（物差しで検証できない変更）
- ロールバック線の崩壊（戻せない変更の発生）
