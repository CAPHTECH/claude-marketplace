# 反例回収ワークフロー

PBTで見つかった反例を資産化し、回帰テストに変換するプロセス。

## 目次

1. [反例回収の重要性](#反例回収の重要性)
2. [回収プロセス](#回収プロセス)
3. [反例コーパス形式](#反例コーパス形式)
4. [回帰テスト自動生成](#回帰テスト自動生成)
5. [seedの管理](#seedの管理)

---

## 反例回収の重要性

### なぜ回収が必要か

PBTで見つかった反例をそのままにすると：
- 次回実行で同じ反例が見つかる保証がない（乱数依存）
- デバッグの痕跡が残らない
- 回帰防止できない

### 資産化の効果

- **再現性**: 反例が確実に再現される
- **高速**: ユニットテストとして即座に実行
- **ドキュメント**: 「なぜこのテストがあるか」が明確
- **shrinkの恩恵**: 最小反例がそのまま保存される

---

## 回収プロセス

### Step 1: 反例の検出

```bash
$ pytest tests/pbt/test_auth.py -v
FAILED tests/pbt/test_auth.py::test_token_validation - Falsifying example:
    token='eyJ...',
    timestamp=3600001
```

### Step 2: shrinkで最小化

Hypothesisが自動でshrinkするが、手動で最小化することも可能:

```python
# shrink後の最小反例
# token: 'eyJ...' → 最小の有効JWT
# timestamp: 3600001 → 期限切れの最小値
```

### Step 3: 反例の記録

```yaml
# tests/pbt/counterexamples/auth.yaml に追記
LAW-session-expiry:
  - description: "セッション有効期限切れの境界（1ms超過）"
    input:
      token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      timestamp: 3600001
    expected: SessionExpiredError
    discovered: "2024-01-15"
    issue: "#123"  # 関連Issue（任意）
    law: LAW-session-expiry
    severity: S0
```

### Step 4: 回帰テスト生成

```python
# tests/unit/test_auth_regression.py
@pytest.mark.parametrize("case", load_counterexamples("auth.yaml", "LAW-session-expiry"))
def test_session_expiry_regression(case):
    """
    反例回帰テスト: セッション有効期限切れの境界
    発見日: 2024-01-15
    関連Law: LAW-session-expiry
    """
    with pytest.raises(SessionExpiredError):
        validate_session(token=case['input']['token'], timestamp=case['input']['timestamp'])
```

### Step 5: 修正と検証

```bash
# 回帰テストが失敗することを確認
$ pytest tests/unit/test_auth_regression.py -v
FAILED

# 修正後、回帰テストが成功
$ pytest tests/unit/test_auth_regression.py -v
PASSED

# PBTも再実行して他の反例がないことを確認
$ pytest tests/pbt/test_auth.py -v
PASSED
```

### Step 6: (任意) seedとしてPBTに戻す

```python
# tests/pbt/conftest.py
from hypothesis import example

# 反例をexampleとして明示
@example(token="eyJ...", timestamp=3600001)
@given(token=valid_jwt(), timestamp=st.integers())
def test_token_validation(token, timestamp):
    ...
```

---

## 反例コーパス形式

### ディレクトリ構成

```
tests/pbt/counterexamples/
├── auth.yaml           # 認証関連
├── payment.yaml        # 決済関連
├── inventory.yaml      # 在庫関連
└── seeds/
    ├── auth.json       # Hypothesis seed
    └── payment.json
```

### YAML形式

```yaml
# tests/pbt/counterexamples/auth.yaml

# Law別にグループ化
LAW-session-expiry:
  - description: "境界ちょうどで期限切れ"
    input:
      token: "valid-jwt-token"
      timestamp: 3600000  # 1時間ちょうど
    expected: "valid"  # または例外型名
    discovered: "2024-01-15"

  - description: "境界1ms超過で期限切れ"
    input:
      token: "valid-jwt-token"
      timestamp: 3600001
    expected: SessionExpiredError
    discovered: "2024-01-15"

LAW-auth-invalid-credential:
  - description: "空のパスワード"
    input:
      username: "valid_user"
      password: ""
    expected: InvalidCredentialError
    discovered: "2024-01-10"

# Term別にグループ化することも可能
TERM-jwt-token:
  - description: "不正な署名"
    input:
      token: "eyJ...invalid_signature"
    expected: InvalidTokenError
    discovered: "2024-01-12"
```

### メタデータ

| フィールド | 必須 | 説明 |
|-----------|------|------|
| description | ✅ | 反例の説明 |
| input | ✅ | 入力値（キー:値の辞書） |
| expected | ✅ | 期待結果（値または例外型名） |
| discovered | ✅ | 発見日（YYYY-MM-DD） |
| issue | - | 関連Issue番号 |
| law | - | 関連Law ID |
| term | - | 関連Term ID |
| severity | - | 深刻度（S0-S3） |
| notes | - | 補足説明 |

---

## 回帰テスト自動生成

### ローダー関数

```python
# tests/conftest.py
import yaml
from pathlib import Path

def load_counterexamples(filename: str, group: str = None) -> list:
    """反例コーパスをテストケースとしてロード"""
    path = Path(__file__).parent / "pbt" / "counterexamples" / filename
    with open(path) as f:
        data = yaml.safe_load(f)

    if group:
        return data.get(group, [])

    # 全グループをフラット化
    cases = []
    for group_name, group_cases in data.items():
        for case in group_cases:
            case['_group'] = group_name
            cases.append(case)
    return cases

def counterexample_id(case: dict) -> str:
    """テストIDを生成"""
    return f"{case.get('_group', 'unknown')}:{case['description'][:30]}"
```

### 自動生成テストテンプレート

```python
# tests/unit/test_auth_regression.py
import pytest
from tests.conftest import load_counterexamples, counterexample_id

# 反例からパラメトリックテストを生成
@pytest.mark.parametrize(
    "case",
    load_counterexamples("auth.yaml", "LAW-session-expiry"),
    ids=counterexample_id
)
def test_session_expiry_counterexamples(case):
    """
    LAW-session-expiry の反例回帰テスト

    PBTで発見された反例を回帰テストとして実行。
    各ケースの詳細は tests/pbt/counterexamples/auth.yaml を参照。
    """
    if case['expected'] == 'valid':
        result = validate_session(**case['input'])
        assert result is not None
    elif case['expected'] == 'SessionExpiredError':
        with pytest.raises(SessionExpiredError):
            validate_session(**case['input'])
    else:
        raise ValueError(f"Unknown expected: {case['expected']}")


# 汎用例外ハンドラー版
@pytest.mark.parametrize(
    "case",
    load_counterexamples("auth.yaml"),
    ids=counterexample_id
)
def test_auth_counterexamples_generic(case):
    expected = case['expected']

    # 例外が期待される場合
    if expected.endswith('Error') or expected.endswith('Exception'):
        exception_class = globals().get(expected) or getattr(__builtins__, expected, Exception)
        with pytest.raises(exception_class):
            call_function(**case['input'])
    else:
        # 正常値が期待される場合
        result = call_function(**case['input'])
        assert result == expected or str(result) == expected
```

---

## seedの管理

### Hypothesis のデータベース

Hypothesis は自動的に反例を `.hypothesis/` に保存する:

```
.hypothesis/
├── examples/
│   └── test_auth/
│       └── test_token_validation/
│           └── <hash>  # shrink済み反例
└── settings.json
```

### 明示的なseed保存

```python
# テスト実行時にseedをログ
@settings(database=None)  # 自動保存を無効化
@given(...)
def test_with_seed_logging(x):
    print(f"Seed: {hypothesis.seed}")  # ログに出力
    ...
```

### seed ファイル形式

```json
// tests/pbt/counterexamples/seeds/auth.json
{
  "test_token_validation": {
    "seeds": [
      {
        "seed": 12345,
        "discovered": "2024-01-15",
        "description": "セッション期限境界"
      }
    ]
  }
}
```

### CI での seed 活用

```yaml
# GitHub Actions
- name: Run PBT with fixed seeds
  run: |
    # 既知の反例seedを先に実行
    pytest tests/pbt/ --hypothesis-seed=12345

    # その後ランダム探索
    pytest tests/pbt/ --hypothesis-seed=random
```

---

## 反例回収チェックリスト

PBT実行後の必須アクション:

- [ ] 失敗した反例をshrinkで最小化
- [ ] `counterexamples/*.yaml` に記録
- [ ] 回帰テストが失敗することを確認
- [ ] 修正を実施
- [ ] 回帰テストが成功することを確認
- [ ] PBTを再実行して他の反例がないことを確認
- [ ] (任意) `@example` としてPBTに追加
- [ ] コミットメッセージに反例情報を含める

### コミットメッセージ例

```
fix(auth): セッション期限境界の検証を修正

- LAW-session-expiry: 3600001ms で期限切れ判定されない問題を修正
- 反例: token=valid, timestamp=3600001
- PBTで発見、回帰テスト追加済み

Closes #123
```
