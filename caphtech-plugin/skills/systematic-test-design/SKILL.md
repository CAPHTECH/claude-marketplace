---
name: systematic-test-design
description: |
  ユニットテストとPBT（Property-Based Testing）を組み合わせた体系的テスト設計スキル。
  「脳を使う場所」を原因推理から「プロパティとジェネレータの設計」へ移動させる。

  4つの成果物（ユニットテスト、プロパティカタログ、ジェネレータ群、反例コーパス）を固定し、
  意地悪レベル（L0-L8）を段階的に上げながら、反例を資産化して回帰テストに回収する。

  トリガー条件:
  - 「体系的にテスト設計して」「テストを設計して」
  - 「PBTでテスト設計して」「プロパティベーステストを書いて」
  - 「ユニットテストを設計して」「テストケースを作成して」
  - 「テストをもっと意地悪にして」「境界値を網羅して」
  - 「ジェネレータを設計して」「反例を資産化して」
  - 「テストの穴を探して」「プロパティカタログを作成して」
  - ELDのGroundフェーズでL1-L3テスト設計時
---

# Systematic Test Design

ユニットテストとPBT（Property-Based Testing）を組み合わせた**成果物ベース**のテスト設計スキル。
「脳を使う場所」を原因推理から**プロパティとジェネレータの設計**へ移動させる。

## 核心思想: ユニットテストとPBTの役割分担

| ユニットテスト | PBT |
|---------------|-----|
| **仕様の杭** | **仕様の周辺と盲点の探索** |
| 具体例で「これが正しい」を固定 | 例示しにくい入力空間を広く探索 |
| 期待値が明確なケース | 反例が出たらshrinkして理解可能に |
| 失敗したら即座に意味が分かる | 見つけた反例はユニットテストへ回収 |

**重要**: PBTが見つけた反例をユニットテストへ回収しないと、運用が"浪費"になる。

## ELDとの関係

```
ELD Loop: Sense → Model → Predict → Change → Ground → Record
                                              ↑
                      test-design-audit + systematic-test-design
                                              ↑
                      Law/Term → ユニットテスト + プロパティ → 反例回収
```

本スキルはELDのGroundフェーズで`/test-design-audit`と連携し、
Law/Termを**ユニットテスト**と**プロパティ**に変換する。

## 4つの成果物

| 成果物 | 役割 | ファイル |
|--------|------|----------|
| **ユニットテスト** | 仕様の杭（例ベース） | `tests/unit/` |
| **プロパティカタログ** | 探索の骨格（性質列挙） | `tests/pbt/properties.yaml` |
| **ジェネレータ群** | 探索のエンジン | `tests/pbt/generators/` |
| **反例コーパス** | 反例の資産化 | `tests/pbt/counterexamples/` |

## ワークフロー

```
Phase 1: Law/Termからテスト対象を特定
    ↓
Phase 2: ユニットテスト設計（典型例・境界例・回帰例）
    ↓
Phase 3: プロパティ分類（7カテゴリ）
    ↓
Phase 4: ジェネレータ設計（意地悪レベル）
    ↓
Phase 5: PBT実行＋反例収集
    ↓
Phase 6: 反例の回帰テスト化（ユニットテストへ回収）
    ↓
Phase 7: 意地悪レベル上昇（ループ）
```

---

## Phase 1: Law/Termからテスト対象を特定

ELDのLaw/Termをテスト対象として整理する。

### Law種別とテスト対応

| Law種別 | ユニットテスト | PBTプロパティ |
|---------|---------------|---------------|
| Invariant | 代表例で確認 | 不変条件プロパティ |
| Pre | 違反時の拒否を確認 | 堅牢性プロパティ |
| Post | 出力の正しさを確認 | 不変条件/参照モデル |
| Policy | ルール適用例を確認 | 代数的性質/メタモルフィック |

### Term要素とテスト対応

| Term要素 | ユニットテスト | PBTプロパティ |
|----------|---------------|---------------|
| 境界 | min/max/空の具体例 | 境界ジェネレータ |
| 観測写像 | encode/decode例 | ラウンドトリップ |
| 状態遷移 | 遷移パス具体例 | 状態機械プロパティ |

---

## Phase 2: ユニットテスト設計

ユニットテストは3種類に分類して設計する。

### 2-1. 典型例（Representative Examples）

**目的**: 仕様の「これが正しい」を杭として固定

```python
# LAW-auth-valid-credential の典型例
def test_login_success_with_valid_credentials():
    """正しい認証情報でログイン成功"""
    result = auth.login(username="valid_user", password="correct_password")
    assert result.success is True
    assert result.session_token is not None

def test_login_failure_with_wrong_password():
    """誤ったパスワードでログイン失敗"""
    result = auth.login(username="valid_user", password="wrong_password")
    assert result.success is False
    assert result.error_code == "INVALID_CREDENTIALS"
```

**選定基準**:
- 最も一般的なユースケース
- ドキュメントに記載されている例
- ユーザーが最初に試すであろう操作

### 2-2. 境界例（Boundary Examples）

**目的**: 境界条件での正しさを固定

```python
# TERM-password (8-256文字) の境界例
def test_password_min_length():
    """最小長（8文字）のパスワードは有効"""
    assert validate_password("a" * 8) is True

def test_password_max_length():
    """最大長（256文字）のパスワードは有効"""
    assert validate_password("a" * 256) is True

def test_password_too_short():
    """7文字のパスワードは無効"""
    with pytest.raises(ValidationError):
        validate_password("a" * 7)

def test_password_too_long():
    """257文字のパスワードは無効"""
    with pytest.raises(ValidationError):
        validate_password("a" * 257)
```

**選定基準**:
- Termで定義された境界値
- 0, 1, -1, max, min, max-1, min+1
- 空、1要素、最大要素数

### 2-3. 回帰例（Regression Examples）

**目的**: 過去のバグを再発防止

```python
# Issue #123 で発見されたバグの回帰テスト
def test_session_expiry_boundary_regression():
    """
    回帰テスト: セッション期限境界（Issue #123）

    発見日: 2024-01-15
    原因: 期限チェックで < ではなく <= を使用していた
    """
    token = create_token(expires_at=3600000)  # ちょうど1時間
    # 期限ちょうどは有効
    assert validate_token(token, at=3600000) is True
    # 期限1ms超過は無効
    assert validate_token(token, at=3600001) is False
```

**選定基準**:
- PBTで発見された反例（shrink後）
- 過去のバグ報告
- ヒヤリハット

---

## Phase 3: プロパティ分類（7カテゴリ）

PBTのプロパティを「型」で分類し、穴を減らす。

詳細は `references/property-catalog.md` を参照。

| # | 分類 | 定義 | 例 |
|---|------|------|-----|
| 1 | **不変条件** | 出力が満たすべき構造・制約 | 「残高は常に0以上」 |
| 2 | **代数的性質** | 冪等性・可換性・結合性 | `normalize(normalize(x)) == normalize(x)` |
| 3 | **ラウンドトリップ** | encode↔decode整合性 | `decode(encode(x)) == x` |
| 4 | **参照モデル** | 正しいが遅い実装との一致 | `fast_sort(x) == sorted(x)` |
| 5 | **メタモルフィック** | 入力変形時の出力変化 | 空白追加でパース結果不変 |
| 6 | **堅牢性** | 例外・エラーの一貫性 | クラッシュしない |
| 7 | **状態機械** | 操作列に対する整合性 | push→popで元に戻る |

### PBTプロパティ実装例

```python
# 1. 不変条件
@given(st.integers(min_value=0, max_value=1000000))
def test_balance_always_non_negative(amount):
    account = Account(balance=amount)
    assert account.balance >= 0

# 2. 代数的性質（冪等性）
@given(st.text())
def test_normalize_idempotent(s):
    assert normalize(normalize(s)) == normalize(s)

# 3. ラウンドトリップ
@given(st.from_type(PayloadSchema))
def test_json_roundtrip(payload):
    assert decode(encode(payload)) == payload

# 6. 堅牢性
@given(st.text())
def test_invalid_input_no_crash(s):
    try:
        parse(s)
    except ParseError:
        pass  # 期待される例外
```

---

## Phase 4: ジェネレータ設計（意地悪レベル）

詳細は `references/generator-ladder.md` を参照。

### 意地悪さの4軸

1. **妥当性軸**: 有効→無効→境界ぎりぎり
2. **サイズ軸**: 小→大→病的構造
3. **状態軸**: 単発→長い操作列→競合
4. **環境軸**: 理想→部分失敗→遅延・中断

### 意地悪レベル（L0-L8）

| Level | 内容 | CI運用 |
|-------|------|--------|
| **L0** | スモール・バリッド（小さい有効入力） | PR時 |
| **L1** | 境界バリッド（min/max/空/1要素） | PR時 |
| **L2** | ニア・インバリッド（ほぼ正しいが一部欠損） | PR時 |
| **L3** | サイズ増大（長文、巨大配列） | 夜間 |
| **L4** | 病的構造（偏った分布、循環参照風） | 夜間 |
| **L5** | 操作列（ランダムAPI呼び出し列） | 夜間 |
| **L6** | 並行・タイミング（同時実行、順序競合） | 週末 |
| **L7** | 環境フォールト注入（I/O失敗、権限失敗） | 週末 |
| **L8** | カバレッジ誘導（分布調整） | 週末 |

### ジェネレータテンプレート

```python
# L0: スモール・バリッド
valid_small = st.integers(min_value=0, max_value=100)

# L1: 境界バリッド
valid_boundary = st.sampled_from([0, 1, 99, 100, MIN_VALUE, MAX_VALUE])

# L2: ニア・インバリッド
near_invalid = st.one_of(
    st.just(-1),           # 境界ちょうど外
    st.just(101),
    st.text(min_size=0, max_size=0),  # 空
)
```

---

## Phase 5: PBT実行＋反例収集

### 実行コマンド

```bash
# PR時（L0-L2、短時間）
pytest tests/pbt/ -k "level_0 or level_1 or level_2" --hypothesis-seed=fixed

# 夜間（L3-L5、重い探索）
pytest tests/pbt/ -k "level_3 or level_4 or level_5" --hypothesis-seed=random
```

### 空疎プロパティ検出

**ルール**: assumeで80%以上捨てる場合は**失敗扱い**。ジェネレータを改善する。

---

## Phase 6: 反例の回帰テスト化

見つかった反例を即座に**ユニットテスト（回帰例）へ回収**する。

詳細は `references/counterexample-workflow.md` を参照。

### 回収プロセス

```
1. PBT失敗 → shrinkで最小反例取得
2. 最小反例をユニットテスト（回帰例）に追加
3. 反例コーパス（YAML）に記録
4. (任意) @example としてPBTにも戻す
```

### 反例コーパス形式

```yaml
# tests/pbt/counterexamples/auth.yaml
LAW-session-expiry:
  - description: "セッション有効期限切れの境界"
    input:
      token: "valid-token"
      timestamp: 3600001  # 1時間+1ms
    expected: SessionExpiredError
    discovered: "2024-01-15"
    test_file: "tests/unit/test_auth_regression.py::test_session_expiry_boundary"
```

---

## Phase 7: 運用ループ

### 1モジュールの標準ループ

```
1. ベースラインのユニットテスト（典型例・境界例を固定）
2. プロパティを1〜3個だけ定義（最初は少なく強く）
3. L0〜L2のジェネレータでPBT実行
4. 失敗したら：
   - shrinkして最小反例を得る
   - 回帰ユニットテストに落とす ← 重要！
   - 修正
5. 通ったら：
   - 意地悪レベルを1段上げる（L3→L4→…）
   - 必要ならプロパティ追加（増やしすぎない）
6. 定期的に：
   - 反例コーパスをseedとして固定
   - カバレッジ/失敗率/時間をモニタして分布調整
```

### CI運用規約

```yaml
PR時:
  unit_tests: 全実行
  pbt_levels: [L0, L1, L2]
  time_budget: 30秒
  seed: fixed

夜間:
  unit_tests: 全実行
  pbt_levels: [L3, L4, L5]
  time_budget: 10分
  seed: random

週末:
  unit_tests: 全実行
  pbt_levels: [L6, L7, L8]
  time_budget: 1時間
  seed: random + 反例コーパス
```

---

## ELD統合: Evidence Ladder対応

| テスト種別 | Evidence Ladder | 対応 |
|-----------|-----------------|------|
| ユニットテスト（典型例） | L1 | 基本動作確認 |
| ユニットテスト（境界例） | L1 | 境界条件確認 |
| PBT L0-L2 | L1 | プロパティ検証 |
| PBT L3-L5（状態機械） | L2 | 状態・操作列検証 |
| PBT L6-L7（並行・フォールト） | L3 | 環境・並行検証 |
| ユニットテスト（回帰例） | L1 | バグ再発防止 |

---

## テストディレクトリ構成

```
tests/
├── unit/
│   ├── test_auth.py              # 典型例・境界例
│   ├── test_auth_regression.py   # 回帰例（PBTから回収）
│   └── ...
├── pbt/
│   ├── properties.yaml           # プロパティカタログ
│   ├── conftest.py               # ジェネレータ共通設定
│   ├── generators/
│   │   ├── valid.py              # 有効入力ジェネレータ
│   │   ├── invalid.py            # 無効入力ジェネレータ
│   │   ├── boundary.py           # 境界ジェネレータ
│   │   └── state.py              # 状態遷移ジェネレータ
│   ├── test_properties.py        # プロパティテスト
│   └── counterexamples/          # 反例コーパス
│       └── seeds/                # シードファイル
└── integration/
```

---

## 楽観バイアス排除チェックリスト

| チェック | 対策 |
|----------|------|
| 典型例の不足 | Law/Termから漏れなく導出 |
| 境界例の不足 | Termの境界を網羅 |
| 空疎プロパティ | assume比率80%超で失敗扱い |
| 再現不能フレーク | seed必須ログ、固定seed併用 |
| 反例の放置 | 即座に回帰テスト化 |

---

## 完了条件

- [ ] 全S0/S1 Lawにユニットテスト（典型例）が存在
- [ ] 全Termの境界にユニットテスト（境界例）が存在
- [ ] プロパティカタログが7分類で整理されている
- [ ] 全S0/S1 Lawに対応するプロパティが存在
- [ ] ジェネレータがL0-L2まで設計されている
- [ ] assume比率が80%未満
- [ ] 反例が回帰テストに回収されている
- [ ] CI運用規約が設定されている

---

## 使用例

```
User: 認証機能のテストを体系的に設計して

Claude: 体系的テスト設計を開始します。

## Phase 1: Law/Termの特定

対象Law:
- LAW-session-valid (S0): セッショントークンは有効期限内で有効
- LAW-auth-idempotent (S1): 同じ認証情報で同じ結果

対象Term:
- TERM-token: JWT形式、256bit、1時間有効
- TERM-password: 8-256文字、英数字記号

## Phase 2: ユニットテスト設計

### 典型例
- test_login_success_with_valid_credentials
- test_login_failure_with_wrong_password
- test_logout_invalidates_session

### 境界例
- test_password_min_length_8_chars
- test_password_max_length_256_chars
- test_session_expiry_at_exactly_1_hour

## Phase 3: プロパティ分類

| プロパティ | 分類 | Law/Term |
|-----------|------|----------|
| セッション期限内で認証成功 | 不変条件 | LAW-session-valid |
| encode→decodeで復元 | ラウンドトリップ | TERM-token |
| 同一入力で同一結果 | 冪等性 | LAW-auth-idempotent |

## Phase 4: ジェネレータ設計

L0: valid_token, valid_credentials
L1: 期限ちょうど切れ、空文字トークン、最大長パスワード
L2: 署名不正JWT、期限1ms超過

テストコードを生成しますか？
```

---

## リファレンス

- `references/property-catalog.md` - プロパティ7分類の詳細
- `references/generator-ladder.md` - 意地悪レベルL0-L8の詳細
- `references/counterexample-workflow.md` - 反例回収ワークフロー
- `references/ci-config.md` - CI運用設定例

## 関連スキル

| スキル | 用途 |
|--------|------|
| `/test-design-audit` | テスト設計の全体フレームワーク（要求→テスト条件） |
| `/eld-ground-tdd-enforcer` | TDDサイクル強制 |
| `/eld-ground-check` | Law/Term接地検証 |
| `/boundary-observation` | 境界条件の観測 |
