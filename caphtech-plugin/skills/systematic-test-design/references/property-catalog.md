# プロパティカタログ詳細

PBTで使用するプロパティの7分類と、各分類の詳細・実装パターン。

## 目次

1. [不変条件（Invariants）](#1-不変条件invariants)
2. [代数的性質（Algebraic laws）](#2-代数的性質algebraic-laws)
3. [ラウンドトリップ（Round-trip）](#3-ラウンドトリップround-trip)
4. [参照モデル（Model/Differential）](#4-参照モデルmodeldifferential)
5. [メタモルフィック（Metamorphic）](#5-メタモルフィックmetamorphic)
6. [堅牢性（Robustness）](#6-堅牢性robustness)
7. [状態機械（Stateful）](#7-状態機械stateful)

---

## 1. 不変条件（Invariants）

**定義**: 出力が満たすべき構造・制約

### 適用シーン

- 出力の範囲制約（0以上、最大値以下）
- 構造制約（ソート済み、重複なし、非空）
- ビジネスルール（残高は負にならない）

### ELD Law対応

- Invariant Law → 不変条件プロパティ

### 実装パターン

```python
from hypothesis import given, strategies as st, assume

# パターン1: 範囲制約
@given(st.integers(min_value=0, max_value=1000000))
def test_output_in_range(x):
    result = process(x)
    assert 0 <= result <= MAX_OUTPUT

# パターン2: 構造制約
@given(st.lists(st.integers()))
def test_output_sorted(xs):
    result = sort_function(xs)
    assert result == sorted(result)
    assert len(result) == len(xs)  # 要素数保存

# パターン3: ビジネスルール（LAW-balance-non-negative）
@given(st.integers(min_value=0), st.integers(min_value=0))
def test_balance_never_negative(initial, withdrawal):
    account = Account(balance=initial)
    assume(withdrawal <= initial)  # 有効な引き出しのみ
    account.withdraw(withdrawal)
    assert account.balance >= 0
```

### よくある間違い

- `assert True` のような空疎なアサーション
- assumeで有効入力を絞りすぎる（80%超で失敗扱い）

---

## 2. 代数的性質（Algebraic laws）

**定義**: 操作の数学的整合性

### 適用シーン

- 正規化処理（冪等性）
- 順序無関係な処理（可換性）
- 連続操作（結合性）

### 種類

| 性質 | 定義 | 例 |
|------|------|-----|
| 冪等性 | f(f(x)) == f(x) | 正規化、フォーマット |
| 可換性 | f(a,b) == f(b,a) | 集合演算、最大/最小 |
| 結合性 | f(f(a,b),c) == f(a,f(b,c)) | 文字列連結、数値加算 |
| 分配性 | f(a, g(b,c)) == g(f(a,b), f(a,c)) | 乗算と加算 |
| 恒等元 | f(a, e) == a | 0との加算、1との乗算 |
| 逆元 | f(a, inv(a)) == e | 加算と減算 |

### 実装パターン

```python
# 冪等性
@given(st.text())
def test_normalize_idempotent(s):
    once = normalize(s)
    twice = normalize(once)
    assert once == twice

# 可換性
@given(st.integers(), st.integers())
def test_max_commutative(a, b):
    assert max_func(a, b) == max_func(b, a)

# 結合性
@given(st.text(), st.text(), st.text())
def test_concat_associative(a, b, c):
    left = concat(concat(a, b), c)
    right = concat(a, concat(b, c))
    assert left == right

# 恒等元
@given(st.lists(st.integers()))
def test_empty_list_identity(xs):
    assert merge(xs, []) == xs
    assert merge([], xs) == xs
```

---

## 3. ラウンドトリップ（Round-trip）

**定義**: エンコード↔デコード、シリアライズ↔デシリアライズの整合性

### 適用シーン

- JSON/XML/Protobufシリアライズ
- URLエンコード
- 暗号化/復号化
- 圧縮/展開

### ELD Term対応

- Termの観測写像 → ラウンドトリッププロパティ

### 実装パターン

```python
# 基本パターン
@given(st.from_type(DataClass))
def test_json_roundtrip(data):
    encoded = json.dumps(data.to_dict())
    decoded = DataClass.from_dict(json.loads(encoded))
    assert data == decoded

# 損失のあるラウンドトリップ（許容誤差あり）
@given(st.floats(allow_nan=False, allow_infinity=False))
def test_float_roundtrip_with_tolerance(x):
    encoded = format_float(x)
    decoded = parse_float(encoded)
    assert abs(x - decoded) < 1e-10  # 許容誤差

# 部分的ラウンドトリップ（一部情報損失許容）
@given(st.from_type(RichText))
def test_plaintext_roundtrip(rich):
    plain = to_plaintext(rich)
    recovered = from_plaintext(plain)
    # 装飾は失われるが、テキストは保存
    assert recovered.text == rich.text
```

### 注意点

- 浮動小数点の丸め誤差
- 同値性の定義（順序、空白、正規化）
- 情報損失がある場合の等価性

---

## 4. 参照モデル（Model/Differential）

**定義**: 簡単だが遅い正しさのモデルとの一致

### 適用シーン

- アルゴリズム最適化の検証
- 異なる実装間の整合性
- 外部ライブラリとの比較

### 実装パターン

```python
# 参照実装との比較
@given(st.lists(st.integers()))
def test_fast_sort_matches_stdlib(xs):
    assert fast_sort(xs) == sorted(xs)

# 差分テスト（2つの実装を比較）
@given(st.text())
def test_new_parser_matches_old(input_text):
    old_result = old_parser.parse(input_text)
    new_result = new_parser.parse(input_text)
    assert old_result == new_result

# シミュレーションモデル
@given(st.lists(st.tuples(st.text(), st.integers())))
def test_cache_matches_model(operations):
    cache = FastCache()
    model = {}  # シンプルなdict

    for key, value in operations:
        cache.put(key, value)
        model[key] = value

    for key in model:
        assert cache.get(key) == model[key]
```

### 注意点

- 参照モデルの正しさを前提としている
- 両者の同値性の定義が一致している必要

---

## 5. メタモルフィック（Metamorphic）

**定義**: 入力を変形したとき出力がどう変わるべきか

### 適用シーン

- オラクルが不明な場合（機械学習、検索）
- 入力の正規化
- 単調性の検証

### メタモルフィック関係の種類

| 関係 | 定義 | 例 |
|------|------|-----|
| 等価性 | 変形しても結果同じ | 空白追加、大文字小文字 |
| 単調性 | 入力増→出力増/減 | 価格上昇→需要減少 |
| 加法性 | f(a+b) == f(a) + f(b) | 線形関数 |
| 順序保存 | a < b → f(a) < f(b) | ソート関数 |

### 実装パターン

```python
# 等価性: 空白不変
@given(st.text())
def test_trim_invariant(s):
    assert parse(s) == parse(f"  {s}  ")
    assert parse(s) == parse(s.replace(" ", "  "))

# 単調性
@given(st.integers(min_value=1), st.integers(min_value=0))
def test_price_demand_monotonic(base_price, increase):
    demand_low = calculate_demand(base_price)
    demand_high = calculate_demand(base_price + increase)
    assert demand_low >= demand_high  # 価格上昇で需要減少

# 置換不変性
@given(st.lists(st.integers()), st.permutations(range(10)))
def test_set_operations_permutation_invariant(xs, perm):
    original = set_operation(xs)
    permuted = set_operation([xs[i] for i in perm if i < len(xs)])
    assert original == permuted
```

---

## 6. 堅牢性（Robustness）

**定義**: 例外・エラーの一貫性、壊れ方の規約

### 適用シーン

- 入力バリデーション
- エラーハンドリング
- リソース制限

### 実装パターン

```python
# クラッシュしない
@given(st.binary())
def test_no_crash_on_arbitrary_input(data):
    try:
        parse(data)
    except (ParseError, ValidationError):
        pass  # 期待される例外
    # 他の例外やクラッシュは失敗

# 一貫したエラー型
@given(st.text())
def test_consistent_error_type(s):
    try:
        validate(s)
    except ValidationError as e:
        assert hasattr(e, 'field')
        assert hasattr(e, 'message')

# タイムアウトしない（リソース制限）
@given(st.lists(st.integers(), max_size=10000))
@settings(deadline=timedelta(seconds=5))
def test_no_timeout(xs):
    result = process(xs)
    assert result is not None

# メモリリークしない
@given(st.lists(st.binary(max_size=1000), min_size=100))
def test_no_memory_leak(chunks):
    import tracemalloc
    tracemalloc.start()
    for chunk in chunks:
        process_chunk(chunk)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak < 100 * 1024 * 1024  # 100MB未満
```

---

## 7. 状態機械（Stateful）

**定義**: 操作列（シーケンス）に対する整合性

### 適用シーン

- ステートフルなAPI
- キャッシュ/ストレージ
- プロトコル実装
- UIの状態遷移

### ELD Law対応

- 状態遷移Law → 状態機械プロパティ

### 実装パターン（Hypothesis stateful）

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, precondition, invariant

class StackMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.stack = Stack()
        self.model = []  # 参照モデル

    @rule(value=st.integers())
    def push(self, value):
        self.stack.push(value)
        self.model.append(value)

    @precondition(lambda self: len(self.model) > 0)
    @rule()
    def pop(self):
        expected = self.model.pop()
        actual = self.stack.pop()
        assert actual == expected

    @invariant()
    def size_matches(self):
        assert len(self.stack) == len(self.model)

    @invariant()
    def top_matches(self):
        if self.model:
            assert self.stack.peek() == self.model[-1]

TestStack = StackMachine.TestCase
```

### 複雑な状態遷移

```python
class AuthStateMachine(RuleBasedStateMachine):
    States = Enum('States', ['ANONYMOUS', 'AUTHENTICATED', 'LOCKED'])

    def __init__(self):
        super().__init__()
        self.auth = AuthService()
        self.state = self.States.ANONYMOUS
        self.failed_attempts = 0

    @rule(credentials=st.from_type(Credentials))
    def login(self, credentials):
        try:
            self.auth.login(credentials)
            self.state = self.States.AUTHENTICATED
            self.failed_attempts = 0
        except AuthError:
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                self.state = self.States.LOCKED

    @precondition(lambda self: self.state == self.States.AUTHENTICATED)
    @rule()
    def logout(self):
        self.auth.logout()
        self.state = self.States.ANONYMOUS

    @invariant()
    def locked_prevents_login(self):
        if self.state == self.States.LOCKED:
            with pytest.raises(AccountLockedError):
                self.auth.login(any_credentials)
```

---

## プロパティ選択ガイド

### Law/Termからの導出

| ELD要素 | 推奨プロパティ |
|---------|---------------|
| Invariant Law | 不変条件 |
| Pre/Post Law | 堅牢性 + 不変条件 |
| Policy Law | 代数的性質 / メタモルフィック |
| Term境界 | 不変条件（範囲チェック） |
| Term観測写像 | ラウンドトリップ |
| 状態遷移Law | 状態機械 |

### 対象機能からの導出

| 機能タイプ | 推奨プロパティ |
|------------|---------------|
| シリアライズ | ラウンドトリップ |
| ソート/検索 | 不変条件 + 参照モデル |
| 正規化/フォーマット | 代数的性質（冪等性） |
| パーサー | 堅牢性 + ラウンドトリップ |
| キャッシュ/DB | 状態機械 |
| 暗号/ハッシュ | ラウンドトリップ + 不変条件 |
| ML推論 | メタモルフィック |
