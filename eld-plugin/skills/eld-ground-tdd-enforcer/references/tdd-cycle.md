# TDDサイクル詳細ガイド

RED-GREEN-REFACTORサイクルの詳細な実践ガイド。

## TDDの本質

TDDは「テストを書く手法」ではなく、**設計手法**である。

### 従来の開発フロー

```
要件 → 設計 → 実装 → テスト → デバッグ
                    ↑ ここで問題が発覚
```

### TDDの開発フロー

```
要件 → テスト（期待動作の明示） → 実装 → リファクタリング
       ↑ 設計がここで明確になる
```

**利点**:
- 設計の問題が早期に発見される
- テストが仕様書として機能
- リファクタリングが安全

## REDフェーズ

### 目的

**失敗するテストを書く** = 期待する動作を明示する

### 手順

#### 1. Law/Termから期待動作を抽出

```yaml
Law: LAW-stock-non-negative (S0)
  内容: 在庫数は常に0以上
  違反時: 注文を拒否し、InsufficientStockErrorを投げる

期待動作:
  - 在庫5、注文10 → InsufficientStockError
  - 在庫5、注文5 → 成功、在庫0
  - 在庫5、注文3 → 成功、在庫2
```

#### 2. テストケースの命名

**Good**:
```python
def test_stock_cannot_be_negative():
    """在庫数がマイナスになる注文を拒否"""

def test_order_reduces_stock_by_quantity():
    """注文により在庫が注文数分減少"""

def test_order_with_exact_stock_succeeds():
    """在庫ちょうどの注文は成功"""
```

**Bad**:
```python
def test_stock():  # 何をテストするのか不明
def test_1():      # 意味がない
def test_order_processing():  # 抽象的
```

**命名規則**:
- `test_<動詞>_<条件>_<期待結果>()`
- docstringでLaw/Term IDを明記

#### 3. テストコードの構造（AAA パターン）

```python
def test_stock_cannot_be_negative():
    """LAW-stock-non-negative: 在庫数がマイナスになる注文を拒否"""

    # Arrange（準備）: テスト対象の状態を設定
    product = Product(id="P001", stock=5)
    order = Order(product_id="P001", quantity=10)

    # Act（実行）: テスト対象の操作を実行
    # Assert（検証）: 期待結果を検証
    with pytest.raises(InsufficientStockError) as exc_info:
        product.reserve_stock(order)

    # 追加の検証
    assert "insufficient stock" in str(exc_info.value).lower()
    assert product.stock == 5  # 在庫が変更されていない
```

#### 4. テスト実行 → RED確認

```bash
$ pytest test_stock.py::test_stock_cannot_be_negative

FAILED test_stock.py::test_stock_cannot_be_negative
AttributeError: 'Product' object has no attribute 'reserve_stock'
```

**RED状態のチェックポイント**:
- [ ] テストが失敗している
- [ ] エラーメッセージが期待通り
- [ ] 実装が存在しないことが原因

**警告サイン**:
- テストが即座に成功 → テストが機能していない
- 予期しないエラー → テストの前提が間違っている

### REDフェーズのアンチパターン

#### アンチパターン1: テストが抽象的

```python
# ❌ Bad
def test_order_works():
    product = Product(stock=10)
    order = Order(quantity=5)
    result = product.process(order)
    assert result  # 何を検証している？

# ✅ Good
def test_order_reduces_stock_by_quantity():
    product = Product(stock=10)
    order = Order(quantity=5)
    product.reserve_stock(order)
    assert product.stock == 5  # 具体的な期待値
```

#### アンチパターン2: 複数の概念を1つのテストに

```python
# ❌ Bad
def test_order_processing():
    # 在庫チェック
    # 決済処理
    # ステータス更新
    # 通知送信
    # すべてを1つのテストで

# ✅ Good
def test_order_checks_stock_availability():
    # 在庫チェックのみ

def test_order_processes_payment():
    # 決済処理のみ

def test_order_updates_status_on_success():
    # ステータス更新のみ
```

#### アンチパターン3: テストが実装に依存

```python
# ❌ Bad（内部実装に依存）
def test_stock_validation():
    product = Product(stock=5)
    assert product._validate_stock(10) == False  # privateメソッド

# ✅ Good（公開インターフェースで検証）
def test_insufficient_stock_raises_error():
    product = Product(stock=5)
    with pytest.raises(InsufficientStockError):
        product.reserve_stock(Order(quantity=10))
```

## GREENフェーズ

### 目的

**最小限の実装でテストを通す** = 過剰実装を避ける

### 手順

#### 1. 最も単純な実装

```python
# RED: test_stock_cannot_be_negative が失敗

# GREEN: 最小実装
class Product:
    def __init__(self, id: str, stock: int):
        self.id = id
        self.stock = stock

    def reserve_stock(self, order: Order):
        if order.quantity > self.stock:
            raise InsufficientStockError("Insufficient stock")
        self.stock -= order.quantity
```

**ポイント**:
- テストを通すだけのコード
- エラーメッセージは最小限
- 複雑なロジックは後回し

#### 2. テスト実行 → GREEN確認

```bash
$ pytest test_stock.py::test_stock_cannot_be_negative

PASSED test_stock.py::test_stock_cannot_be_negative
```

**GREEN状態のチェックポイント**:
- [ ] テストが成功している
- [ ] Law/Termの定義に忠実
- [ ] 過剰実装をしていない

#### 3. 追加のテストケース

GREEN状態になったら、次のテストケースへ:

```python
def test_order_with_sufficient_stock_reduces_stock():
    """LAW-stock-reduction: 注文により在庫が注文数分減少"""
    product = Product(id="P001", stock=10)
    order = Order(product_id="P001", quantity=3)

    product.reserve_stock(order)

    assert product.stock == 7

def test_order_with_exact_stock_empties_stock():
    """TERM-empty-stock: 在庫ちょうどの注文は在庫0になる"""
    product = Product(id="P001", stock=5)
    order = Order(product_id="P001", quantity=5)

    product.reserve_stock(order)

    assert product.stock == 0
```

### GREENフェーズのアンチパターン

#### アンチパターン1: 過剰実装（YAGNI違反）

```python
# ❌ Bad（テストにない機能を実装）
class Product:
    def reserve_stock(self, order: Order):
        # テストされていないロジック
        if self.is_discontinued:
            raise DiscontinuedProductError()

        # ロギング（テストされていない）
        logger.info(f"Reserving {order.quantity} units")

        # メトリクス（テストされていない）
        metrics.increment("stock.reserved")

        if order.quantity > self.stock:
            raise InsufficientStockError("Insufficient stock")
        self.stock -= order.quantity

# ✅ Good（テストを通すだけ）
class Product:
    def reserve_stock(self, order: Order):
        if order.quantity > self.stock:
            raise InsufficientStockError("Insufficient stock")
        self.stock -= order.quantity
```

#### アンチパターン2: ハードコード

```python
# ❌ Bad（特定のテストケースにハードコード）
def reserve_stock(self, order: Order):
    if order.quantity == 10:  # テストケースの値
        raise InsufficientStockError("Insufficient stock")
    self.stock -= order.quantity

# ✅ Good（一般化されたロジック）
def reserve_stock(self, order: Order):
    if order.quantity > self.stock:
        raise InsufficientStockError("Insufficient stock")
    self.stock -= order.quantity
```

## REFACTORフェーズ

### 目的

**動作を保ったまま、コード品質を改善** = テクニカルデットの返済

### 手順

#### 1. リファクタリング対象の特定

**チェックリスト**:
- [ ] 重複したコードがある
- [ ] マジックナンバー/マジックストリングがある
- [ ] 長すぎるメソッド（10行超）
- [ ] 意味不明な変数名
- [ ] 複雑な条件分岐

#### 2. リファクタリングの実施

**例1: マジックストリングの除去**

```python
# Before
def reserve_stock(self, order: Order):
    if order.quantity > self.stock:
        raise InsufficientStockError("Insufficient stock")
    self.stock -= order.quantity

# After
class Product:
    ERROR_MESSAGE_INSUFFICIENT_STOCK = "Insufficient stock: available={available}, required={required}"

    def reserve_stock(self, order: Order):
        if order.quantity > self.stock:
            raise InsufficientStockError(
                self.ERROR_MESSAGE_INSUFFICIENT_STOCK.format(
                    available=self.stock,
                    required=order.quantity
                )
            )
        self.stock -= order.quantity
```

**例2: メソッド抽出**

```python
# Before
def reserve_stock(self, order: Order):
    if order.quantity > self.stock:
        raise InsufficientStockError(
            f"Insufficient stock: available={self.stock}, required={order.quantity}"
        )
    self.stock -= order.quantity

# After
def reserve_stock(self, order: Order):
    self._validate_stock_availability(order.quantity)
    self._reduce_stock(order.quantity)

def _validate_stock_availability(self, quantity: int):
    if quantity > self.stock:
        raise InsufficientStockError(
            f"Insufficient stock: available={self.stock}, required={quantity}"
        )

def _reduce_stock(self, quantity: int):
    self.stock -= quantity
```

**例3: 不変性の導入**

```python
# Before
class Product:
    def __init__(self, stock: int):
        self.stock = stock

# After
class Product:
    def __init__(self, stock: int):
        if stock < 0:
            raise ValueError("Stock cannot be negative")
        self._stock = stock

    @property
    def stock(self) -> int:
        return self._stock

    def _reduce_stock(self, quantity: int):
        self._stock -= quantity  # 内部からのみ変更可能
```

#### 3. テスト実行 → GREEN維持確認

```bash
$ pytest test_stock.py

====== 3 passed in 0.05s ======
```

**チェックポイント**:
- [ ] すべてのテストが成功を維持
- [ ] 新しいバグを導入していない
- [ ] コードの意図が明確になった

### REFACTORフェーズのアンチパターン

#### アンチパターン1: リファクタリングと機能追加の混在

```python
# ❌ Bad（リファクタリング中に機能追加）
def reserve_stock(self, order: Order):
    # リファクタリング: メソッド抽出
    self._validate_stock_availability(order.quantity)

    # 機能追加（テストされていない）
    self._send_low_stock_alert()  # ← 新機能

    self._reduce_stock(order.quantity)

# ✅ Good（リファクタリングのみ）
def reserve_stock(self, order: Order):
    self._validate_stock_availability(order.quantity)
    self._reduce_stock(order.quantity)
```

**原則**: リファクタリングと機能追加は別のコミットで

#### アンチパターン2: 過剰な抽象化

```python
# ❌ Bad（1回しか使わないメソッドを抽象化）
def _create_error_message(self, available: int, required: int) -> str:
    return f"Insufficient stock: available={available}, required={required}"

def _validate_stock_availability(self, quantity: int):
    if quantity > self.stock:
        message = self._create_error_message(self.stock, quantity)
        raise InsufficientStockError(message)

# ✅ Good（適切な抽象化レベル）
def _validate_stock_availability(self, quantity: int):
    if quantity > self.stock:
        raise InsufficientStockError(
            f"Insufficient stock: available={self.stock}, required={quantity}"
        )
```

**原則**: 3回繰り返したら抽象化（Rule of Three）

## サイクルの反復

### 次のテストケースへ

GREEN状態になったら、次のテストケースへ:

```
1. test_stock_cannot_be_negative ✅
2. test_order_reduces_stock_by_quantity ← 次はこれ
3. test_order_with_exact_stock_succeeds
4. test_concurrent_orders_with_race_condition
...
```

### サイクル完了の判断

すべてのLaw/Termに対して:

- [ ] 正常系のテストが存在
- [ ] 異常系（違反時）のテストが存在
- [ ] 境界値のテストが存在
- [ ] Evidence Ladderの要件を満たす

## TDDサイクルの時間配分

### 理想的な配分

```
RED:      20-30%（テスト設計と作成）
GREEN:    40-50%（実装）
REFACTOR: 20-30%（品質改善）
```

### 時間制限

```yaml
1サイクルの目安:
  - 5-10分: 理想的
  - 10-20分: 許容範囲
  - 20分超: タスクが大きすぎる → 分解が必要
```

**長引く原因**:
- タスクが原子的でない
- 設計が複雑すぎる
- Law/Termの定義が曖昧

## 実践例: 全サイクル

### 例: LAW-stock-non-negative の実装

```
┌─ Cycle 1: 在庫不足エラー ─────────────┐
│ RED:   test_stock_cannot_be_negative │
│ GREEN: InsufficientStockError追加    │
│ REFACTOR: エラーメッセージ改善       │
└──────────────────────────────────────┘
         ↓ 3分経過
┌─ Cycle 2: 在庫減少 ───────────────────┐
│ RED:   test_order_reduces_stock      │
│ GREEN: stock -= quantity 追加        │
│ REFACTOR: _reduce_stock抽出          │
└──────────────────────────────────────┘
         ↓ 4分経過
┌─ Cycle 3: 境界値（在庫0） ────────────┐
│ RED:   test_order_with_exact_stock   │
│ GREEN: すでに動作（追加実装なし）    │
│ REFACTOR: バリデーション強化         │
└──────────────────────────────────────┘
         ↓ 2分経過

Total: 9分で完了 ✅
```

## まとめ

### TDD成功の鍵

1. **小さく始める**: 1つのLaw/Termに集中
2. **REDを確認**: テストが失敗することを確認
3. **最小実装**: 過剰実装を避ける
4. **継続的リファクタリング**: テクニカルデットを溜めない
5. **高速フィードバック**: 1サイクル5-10分

### TDD失敗のサイン

- [ ] テストが最初から成功
- [ ] 1サイクルが20分超
- [ ] リファクタリングをスキップ
- [ ] テストが実装に依存
- [ ] テストが抽象的
