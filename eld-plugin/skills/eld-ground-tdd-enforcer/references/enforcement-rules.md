# 強制ルールと例外条件

TDD Enforcerが適用する強制ルールと、例外を許可する条件の詳細。

## 強制ルール一覧

### ルール1: RED状態の確認必須

**内容**: テスト作成後、必ず失敗することを確認する

**検証方法**:
```bash
# テスト作成
# → テスト実行
# → FAILED を確認
# → エラーメッセージが期待通りか確認
```

**違反検出**:
- テスト作成直後に即成功 → `⚠️ テストが機能していない可能性`
- 予期しないエラー → `⚠️ テストの前提が間違っている`

**強制アクション**:
- 実装開始を拒否
- テストの見直しを要求

### ルール2: Law Severity別 Evidence要件

**S0 Law（ビジネスクリティカル）**:
```yaml
必須Evidence:
  - L1（ユニットテスト）: 必須（正常系 + 違反時動作）
  - L2（統合テスト）: 必須
  - L4（本番Telemetry）: 必須
推奨Evidence:
  - L3（失敗注入）: 推奨

カバレッジ基準: 100%
```

**S1 Law（機能要件）**:
```yaml
必須Evidence:
  - L1（ユニットテスト）: 必須
推奨Evidence:
  - L2（統合テスト）: 推奨
  - L4（本番Telemetry）: 推奨

カバレッジ基準: 80%
```

**S2 Law（品質要件）**:
```yaml
推奨Evidence:
  - L1（ユニットテスト）: オプション
  - L4（本番Telemetry）: 推奨

カバレッジ基準: なし
```

**検証方法**:
```bash
# Phase 3 Implementation開始前
1. 対象Lawのリストアップ
2. 各LawのSeverity確認
3. 必要Evidenceの計画
4. L1テストが計画されているか確認

# 実装中
5. テスト作成→実装の順序遵守
6. カバレッジ計測

# コミット前
7. Evidence達成確認
```

### ルール3: テストなしコミット禁止

**内容**: コード変更に対応するテストが必須

**検出方法**:
```bash
# git diffでコード変更を検出
changed_files=$(git diff --name-only HEAD)

# 対応するテストファイルの存在確認
for file in $changed_files; do
  test_file=$(find_corresponding_test $file)
  if [ ! -f "$test_file" ]; then
    echo "❌ テストファイルが見つかりません: $file"
    exit 1
  fi

  # テストが更新されているか確認
  if ! git diff --name-only HEAD | grep -q "$test_file"; then
    echo "❌ テストが更新されていません: $test_file"
    exit 1
  fi
done
```

**例外**:
- ドキュメントのみの変更
- 設定ファイルのみの変更
- リファクタリング（既存テストで保護されている）

### ルール4: RED状態の時間制限

**時間制限**:
```yaml
0-5分:   正常（実装を続行）
5-15分:  警告（設計見直しを提案）
15分超:  停止（タスク分解が必要）
```

**検出方法**:
```python
# テスト実行時刻を記録
red_start_time = datetime.now()

# 実装中に定期的にチェック（例: 5分ごと）
elapsed = datetime.now() - red_start_time

if elapsed > timedelta(minutes=15):
    print("❌ RED状態が15分を超えました")
    print("タスクが大きすぎる可能性があります")
    print("より小さな単位に分解してください")
    sys.exit(1)
elif elapsed > timedelta(minutes=5):
    print("⚠️ RED状態が5分を超えました")
    print("設計の見直しを検討してください")
```

**停止時のアクション**:
1. 現在のタスクを原子化（5-10分単位）に分解
2. Law/Termの定義を再確認
3. より単純なテストケースから開始

### ルール5: カバレッジ基準

**基準**:
```yaml
S0 Law: 100%カバレッジ（ブランチカバレッジ含む）
S1 Law: 80%カバレッジ
S2 Law: 基準なし

全体: 前回コミットより低下禁止
```

**検証**:
```bash
# カバレッジ計測
pytest --cov --cov-report=term-missing

# 基準チェック
python scripts/coverage_check.py \
  --s0-threshold=100 \
  --s1-threshold=80 \
  --no-decrease
```

## 例外条件

### 例外1: プロトタイピング

**適用条件**:
- 技術検証・PoC
- 実験的実装
- スパイク（調査用コード）

**手続き**:
```bash
# コミットメッセージに明示
git commit -m "[prototype] JWT認証の技術検証

TDD Enforcer除外理由: ライブラリ選定のためのスパイク
本番マージ前に削除予定
"

# または設定ファイルで宣言
# .tdd-enforcer.yml
prototype_mode: true
prototype_branches:
  - spike/*
  - experiment/*
```

**制約**:
- mainブランチへのマージ前に必ずテスト追加
- prototype tagを除去するまでリリース禁止

### 例外2: S2 Law（品質要件）

**適用条件**:
- Severity S2のLaw
- パフォーマンス要件
- UX要件

**代替Evidence**:
- L4（本番Telemetry）で代替可能
- パフォーマンステストは統合テストで実施

**例**:
```yaml
LAW-response-time-200ms (S2):
  - L1: オプション（単体では意味がない）
  - L2: 推奨（統合テストで計測）
  - L4: 必須（APMで継続監視）
```

### 例外3: レガシーコード統合

**適用条件**:
- テストのない既存コードの修正
- サードパーティライブラリのラッパー

**対応方針**:
```yaml
段階的テスト追加:
  1. Characterization Test（既存動作の記録）
     - 現在の挙動をテストとして記録
     - リファクタリングの安全網

  2. 修正箇所のみテスト追加
     - 完全カバレッジは要求しない
     - 変更部分のみL1達成

  3. ボーイスカウトルール
     - 触った部分は前よりも良くする
     - テストカバレッジの漸進的向上
```

**例**:
```python
# Characterization Test
def test_legacy_calculate_total_current_behavior():
    """レガシーコードの現在の挙動を記録（仕様が不明）"""
    result = legacy_calculate_total(
        items=[Item(price=100), Item(price=200)],
        discount=0.1
    )
    # 現在の出力を記録（正しいかは不明だが、変更を検出できる）
    assert result == 270.0  # 実際の出力値

# 修正箇所のみテスト
def test_legacy_calculate_total_with_tax():
    """追加機能：消費税計算"""
    result = legacy_calculate_total(
        items=[Item(price=100)],
        discount=0,
        tax_rate=0.1  # 新規追加
    )
    assert result == 110.0
```

### 例外4: UIコンポーネント

**適用条件**:
- ビジュアルコンポーネント
- アニメーション
- レイアウト

**代替アプローチ**:
```yaml
スナップショットテスト:
  - コンポーネントのレンダリング結果を記録
  - 意図しない変更を検出

ビジュアルリグレッションテスト:
  - Percy, Chromatic等のツール
  - スクリーンショット比較

E2Eテスト:
  - Playwright, Cypress等
  - ユーザーシナリオで検証
```

**L1要件の緩和**:
- ロジック部分（状態管理、イベントハンドラ）はL1必須
- 見た目のみの部分はスナップショットテストで代替可

### 例外5: 外部依存の統合

**適用条件**:
- 外部APIとの統合
- データベース操作
- ファイルシステム操作

**対応方針**:
```yaml
L1（ユニットテスト）:
  - モック/スタブを使用
  - ビジネスロジックのみ検証

L2（統合テスト）:
  - テストダブル（FakeAPI等）を使用
  - 実際の外部依存は使わない

L3（E2Eテスト）:
  - 本物の外部依存を使用
  - CI環境でのみ実行
```

## 強制の緩和レベル

### Level 0: 完全強制（デフォルト）

```yaml
対象:
  - main, develop ブランチ
  - S0/S1 Law

ルール:
  - TDDサイクル厳守
  - テストなしコミット禁止
  - カバレッジ基準厳守
```

### Level 1: 部分緩和

```yaml
対象:
  - feature/* ブランチ
  - S2 Law

ルール:
  - TDDサイクル推奨（強制しない）
  - テストなしコミット警告（拒否しない）
  - カバレッジ低下のみ禁止
```

### Level 2: 最小限

```yaml
対象:
  - prototype/*, spike/* ブランチ
  - 個人実験ブランチ

ルール:
  - TDD不要
  - テストなしコミット許可
  - カバレッジ不問

制約:
  - mainへのマージ前にLevel 0を満たす
```

## 設定ファイル例

```yaml
# .tdd-enforcer.yml

# デフォルトレベル
default_level: 0  # 完全強制

# ブランチ別設定
branch_config:
  main:
    level: 0
    require_all_s0_s1_tests: true

  develop:
    level: 0
    require_all_s0_s1_tests: true

  feature/*:
    level: 1
    warn_on_missing_tests: true

  prototype/*:
    level: 2
    require_test_before_merge: true

# Severity別設定
severity_config:
  S0:
    l1_required: true
    l1_coverage: 100
    l2_required: true
    l4_required: true

  S1:
    l1_required: true
    l1_coverage: 80
    l2_recommended: true
    l4_recommended: true

  S2:
    l1_optional: true
    l4_recommended: true

# 除外パターン
exclude:
  - "migrations/*"
  - "scripts/*"
  - "docs/*"
  - "*.md"

# 時間制限
time_limits:
  red_warning: 300   # 5分
  red_stop: 900      # 15分
```

## まとめ

### 原則

1. **S0/S1はL1必須**: 妥協なし
2. **例外は明示的**: 設定ファイルまたはコミットメッセージで宣言
3. **段階的改善**: レガシーコードは漸進的にテスト追加
4. **本番前には厳格化**: mainマージ前にLevel 0を満たす

### 判断基準

```
TDD強制を緩和してよい条件:
  1. プロトタイピング中
  2. S2 Law
  3. レガシーコード（段階的改善中）
  4. UIコンポーネント（代替手段あり）

TDD強制を厳守すべき条件:
  1. S0/S1 Law
  2. main/developブランチ
  3. 本番リリース前
  4. クリティカルなビジネスロジック
```
