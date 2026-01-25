# CI/CD統合ガイド

TDD Enforcerをpre-commit hook、GitHub Actions、その他CI/CDパイプラインに統合する方法。

## Pre-commit Hook統合

### 基本設定

**.git/hooks/pre-commit**:
```bash
#!/bin/bash
# TDD Enforcer Pre-commit Hook

set -e

echo "🔍 TDD Enforcer: コミット前チェック開始..."

# 1. すべてのテストが成功しているか
echo "📝 テスト実行中..."
if ! pytest -v; then
    echo "❌ テストが失敗しています"
    echo "   すべてのテストを成功させてからコミットしてください"
    exit 1
fi

# 2. カバレッジチェック
echo "📊 カバレッジ確認中..."
if ! pytest --cov --cov-fail-under=80 --cov-report=term-missing; then
    echo "❌ カバレッジが基準未満です"
    echo "   80%以上のカバレッジが必要です"
    exit 1
fi

# 3. S0/S1 Law のテスト存在確認
echo "⚖️ Law Evidence確認中..."
if ! python scripts/evidence_check.py; then
    echo "❌ S0/S1 LawのテストがありませんExit exitit 1
fi

# 4. 変更ファイルに対応するテストファイル確認
echo "🧪 テストファイル確認中..."
changed_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' | grep -v '^tests/')
for file in $changed_files; do
    test_file=$(echo "$file" | sed 's/src/tests/' | sed 's/\.py$/test_&/')
    if [ ! -f "$test_file" ] && ! git diff --cached --name-only | grep -q "$test_file"; then
        echo "❌ テストファイルがありません: $test_file"
        echo "   $file の変更に対応するテストを追加してください"
        exit 1
    fi
done

echo "✅ TDD Enforcer: すべてのチェックに合格しました"
exit 0
```

### インストール

```bash
# hookを実行可能にする
chmod +x .git/hooks/pre-commit

# またはpre-commitツールを使用
pip install pre-commit

# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tdd-enforcer
        name: TDD Enforcer
        entry: python scripts/tdd_enforcer_check.py
        language: system
        pass_filenames: false
```

## GitHub Actions統合

### 基本ワークフロー

**.github/workflows/tdd-enforcer.yml**:
```yaml
name: TDD Enforcer

on:
  push:
    branches: [ main, develop, feature/* ]
  pull_request:
    branches: [ main, develop ]

jobs:
  tdd-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run TDD Enforcer
        run: |
          # テスト実行
          pytest --cov=src \
                 --cov-branch \
                 --cov-report=json \
                 --cov-report=term-missing \
                 --cov-fail-under=80

      - name: Check Evidence Ladder
        run: |
          python scripts/evidence_ladder_check.py \
            --coverage-file=coverage.json \
            --law-map=law-severity-map.yaml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.json
          fail_ci_if_error: true

      - name: Comment PR with coverage
        if: github.event_name == 'pull_request'
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ github.token }}
```

### ブランチ別の強制レベル

```yaml
# .github/workflows/tdd-enforcer.yml

jobs:
  tdd-check:
    runs-on: ubuntu-latest

    steps:
      - name: Determine enforcement level
        id: enforcement
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "level=0" >> $GITHUB_OUTPUT
            echo "require_100_for_s0=true" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == refs/heads/feature/* ]]; then
            echo "level=1" >> $GITHUB_OUTPUT
            echo "require_100_for_s0=false" >> $GITHUB_OUTPUT
          else
            echo "level=2" >> $GITHUB_OUTPUT
          fi

      - name: Run TDD Enforcer
        run: |
          python scripts/tdd_enforcer_check.py \
            --level=${{ steps.enforcement.outputs.level }} \
            --s0-coverage-100=${{ steps.enforcement.outputs.require_100_for_s0 }}
```

## evidence_ladder_check.py スクリプト

```python
#!/usr/bin/env python3
"""Evidence Ladder L1達成チェックスクリプト"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List

def load_coverage(coverage_file: Path) -> dict:
    """カバレッジレポートを読み込み"""
    with open(coverage_file) as f:
        return json.load(f)

def load_law_severity_map(map_file: Path) -> Dict[str, dict]:
    """Law Severity Mapを読み込み"""
    with open(map_file) as f:
        return yaml.safe_load(f)

def find_laws_for_file(file_path: str, law_map: dict) -> List[dict]:
    """ファイルに関連するLawを取得"""
    laws = []
    for law_id, law_data in law_map.items():
        if file_path in law_data.get("files", []):
            laws.append({
                "id": law_id,
                "severity": law_data["severity"],
                "files": law_data["files"]
            })
    return laws

def get_required_coverage(severity: int) -> int:
    """Severity別の必要カバレッジ"""
    return {
        0: 100,  # S0: 100%必須
        1: 80,   # S1: 80%必須
        2: 0,    # S2: 要件なし
    }.get(severity, 0)

def check_evidence_ladder(
    coverage_file: Path,
    law_map_file: Path,
    strict: bool = False
) -> bool:
    """Evidence Ladder L1達成チェック"""

    coverage = load_coverage(coverage_file)
    law_map = load_law_severity_map(law_map_file)

    errors = []
    warnings = []

    for file_path, file_cov in coverage["files"].items():
        laws = find_laws_for_file(file_path, law_map)

        if not laws:
            continue

        actual_coverage = file_cov["summary"]["percent_covered"]

        for law in laws:
            required_coverage = get_required_coverage(law["severity"])

            if actual_coverage < required_coverage:
                msg = (
                    f"{file_path}: {law['id']} (S{law['severity']}) "
                    f"requires {required_coverage}% coverage, "
                    f"but got {actual_coverage:.1f}%"
                )

                if law["severity"] in [0, 1]:
                    errors.append(f"❌ {msg}")
                else:
                    warnings.append(f"⚠️ {msg}")

    # 結果表示
    if errors:
        print("\n".join(errors))

    if warnings:
        print("\n".join(warnings))

    if not errors and not warnings:
        print("✅ All Evidence Ladder requirements met")
        return True
    elif errors:
        print(f"\n❌ {len(errors)} error(s) found")
        return False
    else:
        print(f"\n⚠️ {len(warnings)} warning(s) found")
        return not strict  # strictモードでは警告もエラー扱い

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-file", default="coverage.json")
    parser.add_argument("--law-map", default="law-severity-map.yaml")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    success = check_evidence_ladder(
        Path(args.coverage_file),
        Path(args.law_map),
        strict=args.strict
    )

    sys.exit(0 if success else 1)
```

## law-severity-map.yaml 例

```yaml
# Law Severity Map
# ファイルとLawの対応を定義

LAW-stock-non-negative:
  severity: 0  # S0: ビジネスクリティカル
  files:
    - src/inventory/product.py
    - src/inventory/stock_manager.py
  description: "在庫数は常に0以上"

LAW-no-double-payment:
  severity: 0
  files:
    - src/payment/processor.py
  description: "決済が二重実行されない"

LAW-password-min-length:
  severity: 1  # S1: 機能要件
  files:
    - src/auth/password.py
  description: "パスワードは8文字以上"

LAW-response-time-200ms:
  severity: 2  # S2: 品質要件
  files:
    - src/api/handlers.py
  description: "APIレスポンスは200ms以内"
```

## その他のCI/CDプラットフォーム

### GitLab CI

**.gitlab-ci.yml**:
```yaml
stages:
  - test

tdd-enforcer:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - pytest --cov --cov-fail-under=80 --cov-report=json
    - python scripts/evidence_ladder_check.py
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

### CircleCI

**.circleci/config.yml**:
```yaml
version: 2.1

jobs:
  test:
    docker:
      - image: cimg/python:3.10
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: pip install -r requirements.txt
      - run:
          name: Run tests with coverage
          command: pytest --cov --cov-report=json --cov-fail-under=80
      - run:
          name: Check Evidence Ladder
          command: python scripts/evidence_ladder_check.py
      - store_artifacts:
          path: coverage.json

workflows:
  test:
    jobs:
      - test
```

## まとめ

### CI/CD統合のベストプラクティス

1. **Pre-commit hookで早期検出**: ローカルでコミット前にチェック
2. **CIで厳格チェック**: mainブランチは最も厳格に
3. **ブランチ別の強制レベル**: feature/prototype は緩和
4. **カバレッジの可視化**: CodecovやCoverallsで進捗追跡
5. **自動化**: 手動チェックに頼らない

### チェックの階層

```
Local (Pre-commit hook):
  - 基本的なテスト実行
  - カバレッジ80%以上
  - 変更ファイルのテスト存在確認

CI (Pull Request):
  - すべてのテスト実行
  - カバレッジ詳細チェック
  - Evidence Ladder L1達成確認
  - ブランチカバレッジ確認

CI (Main branch):
  - S0 Law 100%カバレッジ必須
  - S1 Law 80%カバレッジ必須
  - すべてのLawのテスト存在確認
  - カバレッジ低下禁止
```
