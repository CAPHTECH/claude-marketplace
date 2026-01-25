# Evidence Ladder L1達成基準

ユニットテスト（Evidence Ladder L1）の達成基準と実践ガイド。

## Evidence Ladderとは

Law/Termの正しさを証明する証拠の階層。

```
L4: 本番Telemetry ─ 実運用でのLaw違反検知
L3: 失敗注入 ────── 違反時動作の確認
L2: 統合テスト ──── 境界越えの因果
L1: ユニットテスト ─ Law/Termの観測写像の最小 ← 本ガイドの対象
L0: 静的整合 ────── 型/lint（ここで完了扱いしない）
```

## L1達成の定義

### Law の L1達成基準

**必須要素**:
```yaml
1. 正常系テスト: Lawが満たされる場合の動作
2. 異常系テスト: Lawが破られる場合の動作（違反時挙動）
3. 境界値テスト: Law定義の境界での動作
```

**例: LAW-stock-non-negative**
```python
# 1. 正常系
def test_order_with_sufficient_stock_succeeds():
    """在庫十分な場合、注文成功"""
    product = Product(stock=10)
    product.reserve_stock(Order(quantity=5))
    assert product.stock == 5

# 2. 異常系（違反時挙動）
def test_order_with_insufficient_stock_raises_error():
    """在庫不足の場合、InsufficientStockError"""
    product = Product(stock=3)
    with pytest.raises(InsufficientStockError):
        product.reserve_stock(Order(quantity=5))
    assert product.stock == 3  # 在庫変更されていない

# 3. 境界値
def test_order_with_exact_stock_empties_stock():
    """在庫ちょうどの場合、在庫0"""
    product = Product(stock=5)
    product.reserve_stock(Order(quantity=5))
    assert product.stock == 0

def test_order_with_zero_quantity_keeps_stock():
    """注文0の場合、在庫変化なし"""
    product = Product(stock=5)
    product.reserve_stock(Order(quantity=0))
    assert product.stock == 5
```

### Term の L1達成基準

**必須要素**:
```yaml
1. 観測写像のテスト: Termの存在を確認する手段
2. 境界のテスト: Termの範囲・制約の確認
3. 型不変条件のテスト: Termの構造的制約
```

**例: TERM-authenticated-user**
```python
# 1. 観測写像
def test_authenticated_user_has_valid_token():
    """認証済みユーザーは有効なトークンを持つ"""
    user = AuthenticatedUser(token="valid_token_xxx")
    assert user.is_authenticated()
    assert user.token_expiry > datetime.now()

# 2. 境界
def test_expired_token_is_not_authenticated():
    """期限切れトークンは認証されていない"""
    user = User(token="expired_token_xxx")
    assert not user.is_authenticated()

# 3. 型不変条件
def test_authenticated_user_requires_non_empty_token():
    """認証済みユーザーはトークンが必須"""
    with pytest.raises(ValueError):
        AuthenticatedUser(token="")
```

## Law Severity別の要件

### S0 Law（ビジネスクリティカル）

**カバレッジ**: 100%（ブランチカバレッジ含む）

**必須テスト**:
```yaml
- 正常系: 全パターン
- 異常系: すべての違反ケース
- 境界値: 最小値/最大値/ゼロ/null
- エラーメッセージ: 内容の検証
- 状態不変性: 違反時に状態が変更されていないこと
```

**例**:
```python
# LAW-no-double-payment (S0): 決済が二重実行されない

def test_payment_succeeds_once():
    """正常系: 決済が1回だけ実行される"""
    order = Order(amount=1000)
    payment = Payment(order)

    result = payment.process()

    assert result.status == "success"
    assert payment.execution_count == 1

def test_payment_cannot_be_executed_twice():
    """異常系: 2回目の決済は拒否"""
    order = Order(amount=1000)
    payment = Payment(order)
    payment.process()  # 1回目

    with pytest.raises(AlreadyPaidError) as exc:
        payment.process()  # 2回目

    assert "already paid" in str(exc.value).lower()
    assert payment.execution_count == 1  # 状態不変

def test_payment_with_zero_amount_is_rejected():
    """境界値: 金額0は拒否"""
    order = Order(amount=0)
    payment = Payment(order)

    with pytest.raises(InvalidAmountError):
        payment.process()
```

### S1 Law（機能要件）

**カバレッジ**: 80%以上

**必須テスト**:
```yaml
- 正常系: 主要パターン
- 異常系: 主要な違反ケース
- 境界値: 最小値/最大値
```

**例**:
```python
# LAW-password-min-length (S1): パスワードは8文字以上

def test_valid_password_is_accepted():
    """正常系: 8文字以上のパスワード"""
    user = User(password="abcd1234")
    assert user.password_is_valid()

def test_short_password_is_rejected():
    """異常系: 7文字以下は拒否"""
    with pytest.raises(WeakPasswordError):
        User(password="abc123")

def test_exactly_8_chars_password_is_accepted():
    """境界値: ちょうど8文字"""
    user = User(password="abcd1234")
    assert user.password_is_valid()
```

### S2 Law（品質要件）

**カバレッジ**: 要件なし

**L1はオプション**: L4（本番Telemetry）で代替可

## カバレッジ計測

### ツール設定

**pytest-cov**:
```bash
# インストール
pip install pytest-cov

# 実行
pytest --cov=src --cov-report=term-missing --cov-report=html

# ブランチカバレッジ
pytest --cov=src --cov-branch --cov-report=term-missing
```

### カバレッジレポート解釈

```
---------- coverage: platform linux, python 3.10 ----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/product.py             25      2    92%   45-46
src/order.py               30      0   100%
-----------------------------------------------------
TOTAL                      55      2    96%
```

**チェックポイント**:
- S0 Law関連: 100%必須
- S1 Law関連: 80%以上必須
- Missing行の確認: 未テストの行を特定

### カバレッジ基準の自動チェック

```python
# scripts/coverage_check.py

import sys
import json
from pathlib import Path

def check_coverage(coverage_file: Path, law_severity_map: dict):
    """カバレッジが基準を満たすかチェック"""
    with open(coverage_file) as f:
        coverage = json.load(f)

    errors = []

    for file_path, file_cov in coverage["files"].items():
        # ファイルに対応するLawを取得
        laws = find_laws_for_file(file_path, law_severity_map)

        for law in laws:
            required_coverage = get_required_coverage(law["severity"])
            actual_coverage = file_cov["summary"]["percent_covered"]

            if actual_coverage < required_coverage:
                errors.append(
                    f"❌ {file_path}: {law['id']} (S{law['severity']}) "
                    f"requires {required_coverage}% coverage, "
                    f"but got {actual_coverage}%"
                )

    if errors:
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("✅ All coverage requirements met")

def get_required_coverage(severity: int) -> int:
    """Severity別の必要カバレッジ"""
    return {
        0: 100,  # S0
        1: 80,   # S1
        2: 0,    # S2（要件なし）
    }[severity]
```

## テストの品質チェックリスト

### 良いテストの条件

- [ ] **独立性**: 他のテストに依存しない
- [ ] **再現性**: 何度実行しても同じ結果
- [ ] **高速性**: 1テスト < 100ms
- [ ] **明確性**: テスト名で何を検証するか分かる
- [ ] **完全性**: Law/Termの定義を完全にカバー

### アンチパターン

**❌ テストが実装に依存**:
```python
# Bad: privateメソッドをテスト
def test_validate_stock_internal():
    assert product._validate_stock(5) == True

# Good: 公開インターフェースで検証
def test_sufficient_stock_allows_order():
    product.reserve_stock(Order(quantity=5))
    # 例外が投げられなければ成功
```

**❌ 複数の概念を1つのテストで**:
```python
# Bad: 複数のLawを1つのテストで
def test_order_processing():
    # 在庫チェック（LAW-stock-non-negative）
    # 決済処理（LAW-no-double-payment）
    # ステータス更新（LAW-status-transition）

# Good: Lawごとに分離
def test_order_checks_stock():
    # LAW-stock-non-negative のみ

def test_order_processes_payment_once():
    # LAW-no-double-payment のみ
```

**❌ 脆いアサーション**:
```python
# Bad: 具体的すぎるエラーメッセージ
assert str(exc.value) == "Insufficient stock: available=5, required=10"

# Good: 本質的な内容のみ検証
assert "insufficient stock" in str(exc.value).lower()
```

## CI統合

### GitHub Actions例

```yaml
name: Coverage Check

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest --cov=src \
                 --cov-branch \
                 --cov-report=json \
                 --cov-report=term-missing \
                 --cov-fail-under=80

      - name: Check S0/S1 Law coverage
        run: |
          python scripts/coverage_check.py \
            --coverage-file=coverage.json \
            --law-map=law-severity-map.yaml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
```

## まとめ

### L1達成の最低条件

**S0/S1 Law**:
1. 正常系・異常系・境界値のテストが存在
2. カバレッジ基準を満たす（S0: 100%, S1: 80%）
3. Law違反時の挙動もテストされている
4. すべてのテストが成功している

**Term**:
1. 観測写像のテストが存在
2. 境界のテストが存在
3. 型不変条件のテストが存在

### 次のステップ

L1達成後:
- L2（統合テスト）: 境界を越えた相互作用のテスト
- L3（失敗注入）: Law違反時の挙動テスト
- L4（本番Telemetry）: 実運用での監視
