# 意地悪レベル（Generator Ladder）詳細

ジェネレータの「意地悪さ」を段階的に上げていく体系。
L0から始めてshrinkが効く状態を維持しながらL8まで進める。

## 目次

1. [意地悪さの4軸](#意地悪さの4軸)
2. [意地悪レベル一覧（L0-L8）](#意地悪レベル一覧l0-l8)
3. [各レベルの詳細](#各レベルの詳細)
4. [ジェネレータ実装例](#ジェネレータ実装例)
5. [CI運用規約](#ci運用規約)

---

## 意地悪さの4軸

### 1. 妥当性軸（Validity）

```
有効 → 境界ぎりぎり → ほぼ有効（一部欠損） → 完全無効
```

| レベル | 内容 | 例 |
|--------|------|-----|
| 有効 | 仕様通りの入力 | 正規のメールアドレス |
| 境界 | min/max/空/1要素 | 0文字、256文字ちょうど |
| ニア | 一部だけ不正 | @が2つ、ドメインなし |
| 無効 | 完全に不正 | ランダムバイナリ |

### 2. サイズ軸（Size/Complexity）

```
小 → 中 → 大 → 病的構造
```

| レベル | 内容 | 例 |
|--------|------|-----|
| 小 | 1-10要素 | [1, 2, 3] |
| 中 | 100-1000要素 | 中規模リスト |
| 大 | 10000+要素 | 巨大配列 |
| 病的 | 偏り/再帰/循環 | 全要素同一、深さ100のネスト |

### 3. 状態軸（State/History）

```
単発 → 短い操作列 → 長い操作列 → 競合・相互作用
```

| レベル | 内容 | 例 |
|--------|------|-----|
| 単発 | 1回の操作 | 単一API呼び出し |
| 短列 | 2-5回の操作 | login → action → logout |
| 長列 | 100+回の操作 | ランダムAPI呼び出し列 |
| 競合 | 同時・順序入替 | 2スレッドから同時書き込み |

### 4. 環境軸（Environment/Fault）

```
理想 → 部分失敗 → 遅延・中断 → カオス
```

| レベル | 内容 | 例 |
|--------|------|-----|
| 理想 | すべて正常動作 | ネットワーク正常 |
| 部分失敗 | 一部リソース失敗 | DBタイムアウト |
| 遅延 | 応答遅延・中断 | 5秒遅延、途中切断 |
| カオス | 複合障害 | 複数リソース同時障害 |

---

## 意地悪レベル一覧（L0-L8）

| Level | 名称 | 妥当性 | サイズ | 状態 | 環境 | CI運用 |
|-------|------|--------|--------|------|------|--------|
| **L0** | スモール・バリッド | 有効 | 小 | 単発 | 理想 | PR時 |
| **L1** | 境界バリッド | 境界 | 小 | 単発 | 理想 | PR時 |
| **L2** | ニア・インバリッド | ニア | 小 | 単発 | 理想 | PR時 |
| **L3** | サイズ増大 | 有効 | 大 | 単発 | 理想 | 夜間 |
| **L4** | 病的構造 | 有効 | 病的 | 単発 | 理想 | 夜間 |
| **L5** | 操作列 | 有効 | 中 | 長列 | 理想 | 夜間 |
| **L6** | 並行・タイミング | 有効 | 中 | 競合 | 理想 | 週末 |
| **L7** | 環境フォールト | 有効 | 中 | 短列 | 部分〜カオス | 週末 |
| **L8** | カバレッジ誘導 | 混合 | 混合 | 混合 | 混合 | 週末 |

---

## 各レベルの詳細

### L0: スモール・バリッド

**目的**: shrinkが効く状態を確保、基本的な正しさを検証

```python
# 特徴: 小さい、有効、単純
valid_small_int = st.integers(min_value=0, max_value=100)
valid_small_str = st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('L',)))
valid_small_list = st.lists(st.integers(), min_size=1, max_size=5)
```

**なぜ最初か**:
- 反例が見つかったときにshrinkが効きやすい
- デバッグが容易
- 実行時間が短い

### L1: 境界バリッド

**目的**: 境界値での正しさを検証

```python
# 特徴: 境界ちょうど、極端な有効値
boundary_int = st.sampled_from([0, 1, -1, MAX_INT, MIN_INT, MAX_INT - 1])
boundary_str = st.sampled_from(["", "a", "a" * 255, "a" * 256])  # 空、1文字、最大-1、最大
boundary_list = st.sampled_from([[], [0], list(range(MAX_SIZE))])

# Termの境界から導出
# TERM-age: 0-150
age_boundary = st.sampled_from([0, 1, 149, 150])
```

**典型的な境界**:
- 数値: 0, 1, -1, max, min, max-1, min+1
- 文字列: 空, 1文字, 最大長, 最大長-1, 最大長+1
- リスト: 空, 1要素, 最大要素数
- 日時: エポック, 年境界, 月末, 閏年

### L2: ニア・インバリッド

**目的**: ほぼ正しいが一部欠損したデータでの挙動

```python
# 特徴: 有効に近いが一部不正
near_invalid_email = st.one_of(
    st.just("user@"),           # ドメインなし
    st.just("@domain.com"),     # ユーザーなし
    st.just("user@@domain.com"), # @が2つ
    st.just("user@domain"),     # TLDなし
)

near_invalid_json = st.one_of(
    st.just('{"key": }'),       # 値なし
    st.just('{key: "value"}'),  # キーにクォートなし
    st.just('{"key": "value"'),  # 閉じ括弧なし
)

# オフバイワン
off_by_one = st.sampled_from([
    MAX_VALUE + 1,
    MIN_VALUE - 1,
    MAX_SIZE + 1,
])
```

### L3: サイズ増大

**目的**: 大きな入力での性能・メモリ問題を検出

```python
# 特徴: 有効だが巨大
large_int = st.integers(min_value=0, max_value=10**18)
large_str = st.text(min_size=10000, max_size=100000)
large_list = st.lists(st.integers(), min_size=10000, max_size=100000)

# ネスト構造
deep_nested = st.recursive(
    st.integers(),
    lambda inner: st.lists(inner, min_size=1, max_size=3),
    max_leaves=1000
)
```

**検出対象**:
- O(n²)アルゴリズム
- メモリ枯渇
- スタックオーバーフロー
- タイムアウト

### L4: 病的構造

**目的**: 偏った分布や特殊構造での問題を検出

```python
# 特徴: 極端に偏った構造
all_same = st.lists(st.just(0), min_size=1000, max_size=1000)
all_max = st.lists(st.just(MAX_INT), min_size=100)
alternating = st.builds(
    lambda n: [0, 1] * n,
    st.integers(min_value=100, max_value=1000)
)

# 循環参照風（JSONで表現できる範囲）
cyclic_like = st.fixed_dictionaries({
    'id': st.integers(),
    'parent_id': st.integers(),  # 自己参照の可能性
})

# ハッシュ衝突誘発
hash_collision = st.sampled_from([
    "Aa", "BB",  # Javaでハッシュ同一
    0, -0,       # 符号付きゼロ
])
```

### L5: 操作列

**目的**: ステートフルな操作の整合性を検証

```python
from hypothesis.stateful import RuleBasedStateMachine, rule

class APISequenceMachine(RuleBasedStateMachine):
    @rule()
    def create(self):
        self.client.create()

    @rule()
    def read(self):
        self.client.read()

    @rule()
    def update(self):
        self.client.update()

    @rule()
    def delete(self):
        self.client.delete()

# 操作列ジェネレータ
operations = st.lists(
    st.sampled_from(['create', 'read', 'update', 'delete']),
    min_size=10,
    max_size=100
)
```

### L6: 並行・タイミング

**目的**: 競合状態、データレース、順序依存を検出

```python
import asyncio
import concurrent.futures

# 並行実行テスト
@given(st.lists(st.integers(), min_size=2, max_size=10))
def test_concurrent_writes(values):
    cache = SharedCache()

    async def write(v):
        await cache.set("key", v)

    async def main():
        await asyncio.gather(*[write(v) for v in values])

    asyncio.run(main())
    # 最後の値が設定されているか、または整合性を検証
    assert cache.get("key") in values

# スレッド競合
def test_thread_safety():
    counter = AtomicCounter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(counter.increment) for _ in range(1000)]
        concurrent.futures.wait(futures)
    assert counter.value == 1000
```

### L7: 環境フォールト注入

**目的**: 外部依存の失敗時の挙動を検証

```python
# モック/スタブによる失敗注入
@given(st.sampled_from(['timeout', 'connection_error', '500', '503']))
def test_external_api_failure(failure_type):
    with mock.patch('requests.get') as mock_get:
        if failure_type == 'timeout':
            mock_get.side_effect = requests.Timeout()
        elif failure_type == 'connection_error':
            mock_get.side_effect = requests.ConnectionError()
        elif failure_type == '500':
            mock_get.return_value.status_code = 500
        elif failure_type == '503':
            mock_get.return_value.status_code = 503

        # フォールバック動作を検証
        result = fetch_with_fallback()
        assert result is not None  # フォールバックが機能

# ディスク容量不足シミュレーション
@given(st.binary(min_size=1000))
def test_disk_full(data):
    with mock.patch('builtins.open', side_effect=OSError(errno.ENOSPC, "No space")):
        result = write_with_retry(data)
        assert result.is_failure()
        assert "disk" in result.error.lower()
```

### L8: カバレッジ誘導

**目的**: 未到達のコードパスを狙った探索

```python
# Hypothesis のターゲット機能
from hypothesis import target

@given(st.integers(min_value=0, max_value=1000))
def test_with_coverage_target(x):
    result = complex_function(x)
    # カバレッジを誘導
    target(coverage_score(x), label="branch_coverage")

# 条件分岐を狙ったジェネレータ
branch_targeting = st.one_of(
    st.integers(min_value=0, max_value=10),      # if x < 10
    st.integers(min_value=10, max_value=100),    # elif x < 100
    st.integers(min_value=100, max_value=1000),  # elif x < 1000
    st.integers(min_value=1000),                 # else
)

# エラー経路を狙う
error_path_targeting = st.sampled_from([
    {"type": "normal"},
    {"type": "error", "code": "E001"},
    {"type": "error", "code": "E002"},
    {"type": "retry"},
    {"type": "timeout"},
])
```

---

## ジェネレータ実装例

### 汎用ジェネレータテンプレート

```python
# generators/base.py

def valid_generator(T, level: int):
    """レベルに応じた有効入力ジェネレータ"""
    if level == 0:
        return small_valid(T)
    elif level == 1:
        return boundary_valid(T)
    elif level <= 2:
        return near_invalid(T)
    elif level <= 4:
        return large_valid(T)
    else:
        return complex_valid(T)

# レベルごとのデコレータ
def level(n):
    def decorator(func):
        func._pbt_level = n
        return func
    return decorator

@level(0)
@given(valid_small_int)
def test_level_0_example(x):
    pass

@level(3)
@given(large_list)
def test_level_3_example(xs):
    pass
```

### ドメイン固有ジェネレータ例

```python
# generators/user.py

# TERM-user から導出
user_l0 = st.fixed_dictionaries({
    'name': st.text(min_size=1, max_size=10),
    'age': st.integers(min_value=0, max_value=100),
    'email': st.emails(),
})

user_l1 = st.one_of(
    st.fixed_dictionaries({'name': st.just(""), 'age': st.just(0), 'email': st.emails()}),
    st.fixed_dictionaries({'name': st.text(min_size=255, max_size=256), 'age': st.just(150), 'email': st.emails()}),
)

user_l2 = st.fixed_dictionaries({
    'name': st.text(),
    'age': st.integers(min_value=-1, max_value=151),  # 範囲外
    'email': st.text(),  # 不正なメール形式
})
```

---

## CI運用規約

### pytest マーカー設定

```python
# conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "level_0: L0 tests (small valid)")
    config.addinivalue_line("markers", "level_1: L1 tests (boundary)")
    config.addinivalue_line("markers", "level_2: L2 tests (near invalid)")
    config.addinivalue_line("markers", "level_3: L3 tests (large)")
    config.addinivalue_line("markers", "level_4: L4 tests (pathological)")
    config.addinivalue_line("markers", "level_5: L5 tests (stateful)")
    config.addinivalue_line("markers", "level_6: L6 tests (concurrent)")
    config.addinivalue_line("markers", "level_7: L7 tests (fault injection)")
    config.addinivalue_line("markers", "level_8: L8 tests (coverage guided)")
```

### GitHub Actions 設定例

```yaml
# .github/workflows/pbt.yml
name: PBT Test Suite

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # 毎日2時（夜間）
    - cron: '0 4 * * 0'  # 毎週日曜4時（週末）

jobs:
  pbt-pr:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run L0-L2 tests
        run: |
          pytest tests/pbt/ -m "level_0 or level_1 or level_2" \
            --hypothesis-seed=12345 \
            --hypothesis-deadline=500

  pbt-nightly:
    if: github.event.schedule == '0 2 * * *'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run L3-L5 tests
        run: |
          pytest tests/pbt/ -m "level_3 or level_4 or level_5" \
            --hypothesis-profile=ci \
            --hypothesis-deadline=5000

  pbt-weekly:
    if: github.event.schedule == '0 4 * * 0'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run L6-L8 tests
        run: |
          pytest tests/pbt/ -m "level_6 or level_7 or level_8" \
            --hypothesis-profile=thorough
```

### Hypothesis プロファイル設定

```python
# conftest.py
from hypothesis import settings, Verbosity, Phase

settings.register_profile("ci", max_examples=100, deadline=500)
settings.register_profile("nightly", max_examples=500, deadline=5000)
settings.register_profile("thorough", max_examples=1000, deadline=None, phases=[
    Phase.explicit, Phase.reuse, Phase.generate, Phase.target, Phase.shrink
])
settings.register_profile("debug", max_examples=10, verbosity=Verbosity.verbose)

settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "ci"))
```
