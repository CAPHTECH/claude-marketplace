# CI運用設定例

PBTをCI/CDパイプラインに組み込むための設定例。

## 目次

1. [運用規約](#運用規約)
2. [pytest設定](#pytest設定)
3. [GitHub Actions](#github-actions)
4. [その他のCIツール](#その他のciツール)
5. [モニタリング](#モニタリング)

---

## 運用規約

### 意地悪レベル別の運用

| タイミング | レベル | 時間予算 | seed |
|-----------|--------|----------|------|
| PR時 | L0-L2 | 30秒 | 固定 |
| 夜間 | L3-L5 | 10分 | ランダム |
| 週末 | L6-L8 | 1時間 | ランダム + コーパス |

### 失敗時の対応フロー

```
PR時の失敗:
  → 即座に修正（マージブロック）

夜間の失敗:
  → Issue作成 → 翌営業日に対応

週末の失敗:
  → Issue作成 + Slack通知 → 週明けに対応
```

---

## pytest設定

### conftest.py

```python
# tests/pbt/conftest.py
import os
import pytest
from hypothesis import settings, Verbosity, Phase, HealthCheck

# プロファイル定義
settings.register_profile(
    "pr",
    max_examples=50,
    deadline=500,
    suppress_health_check=[HealthCheck.too_slow],
)

settings.register_profile(
    "nightly",
    max_examples=200,
    deadline=5000,
    suppress_health_check=[HealthCheck.too_slow],
)

settings.register_profile(
    "weekly",
    max_examples=1000,
    deadline=None,
    phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target, Phase.shrink],
)

settings.register_profile(
    "debug",
    max_examples=10,
    verbosity=Verbosity.verbose,
)

# 環境変数からプロファイル選択
profile = os.getenv("HYPOTHESIS_PROFILE", "pr")
settings.load_profile(profile)


# マーカー登録
def pytest_configure(config):
    for level in range(9):
        config.addinivalue_line(
            "markers",
            f"level_{level}: PBT level {level} tests"
        )


# seed のログ出力
@pytest.fixture(autouse=True)
def log_hypothesis_seed(request):
    """各テストのseedをログに出力"""
    yield
    # Hypothesis が使用したseedは自動でログされる
```

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    level_0: L0 tests (small valid)
    level_1: L1 tests (boundary valid)
    level_2: L2 tests (near invalid)
    level_3: L3 tests (large size)
    level_4: L4 tests (pathological)
    level_5: L5 tests (stateful)
    level_6: L6 tests (concurrent)
    level_7: L7 tests (fault injection)
    level_8: L8 tests (coverage guided)

addopts =
    --strict-markers
    -v
```

### pyproject.toml (代替)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "level_0: L0 tests (small valid)",
    "level_1: L1 tests (boundary valid)",
    "level_2: L2 tests (near invalid)",
    "level_3: L3 tests (large size)",
    "level_4: L4 tests (pathological)",
    "level_5: L5 tests (stateful)",
    "level_6: L6 tests (concurrent)",
    "level_7: L7 tests (fault injection)",
    "level_8: L8 tests (coverage guided)",
]

[tool.hypothesis]
# Hypothesis 設定
deadline = 500
max_examples = 100
```

---

## GitHub Actions

### 基本設定

```yaml
# .github/workflows/pbt.yml
name: PBT Test Suite

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1-5'  # 平日2時（夜間）
    - cron: '0 4 * * 0'     # 日曜4時（週末）

env:
  PYTHON_VERSION: '3.11'

jobs:
  # PR時: L0-L2 (高速)
  pbt-pr:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt

      - name: Run L0-L2 PBT tests
        env:
          HYPOTHESIS_PROFILE: pr
        run: |
          pytest tests/pbt/ \
            -m "level_0 or level_1 or level_2" \
            --hypothesis-seed=42 \
            --junitxml=pbt-results.xml

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: pbt-pr-results
          path: pbt-results.xml

  # 夜間: L3-L5 (重い探索)
  pbt-nightly:
    if: github.event.schedule == '0 2 * * 1-5'
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements-test.txt

      - name: Run L3-L5 PBT tests
        env:
          HYPOTHESIS_PROFILE: nightly
        run: |
          pytest tests/pbt/ \
            -m "level_3 or level_4 or level_5" \
            --junitxml=pbt-nightly-results.xml

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: pbt-nightly-results
          path: pbt-nightly-results.xml

      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "🔴 PBT Nightly Failed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*PBT Nightly Tests Failed*\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run>"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

  # 週末: L6-L8 (徹底探索)
  pbt-weekly:
    if: github.event.schedule == '0 4 * * 0'
    runs-on: ubuntu-latest
    timeout-minutes: 120
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements-test.txt

      - name: Run L6-L8 PBT tests
        env:
          HYPOTHESIS_PROFILE: weekly
        run: |
          pytest tests/pbt/ \
            -m "level_6 or level_7 or level_8" \
            --junitxml=pbt-weekly-results.xml

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: pbt-weekly-results
          path: pbt-weekly-results.xml
          retention-days: 30
```

### 反例コーパスの自動更新

```yaml
# .github/workflows/pbt-corpus-update.yml
name: Update PBT Corpus

on:
  workflow_run:
    workflows: ["PBT Test Suite"]
    types: [completed]

jobs:
  update-corpus:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: pbt-results

      - name: Extract counterexamples
        run: |
          # JUnit XMLから反例を抽出するスクリプト
          python scripts/extract_counterexamples.py pbt-results.xml

      - name: Create PR with counterexamples
        uses: peter-evans/create-pull-request@v5
        with:
          title: "test: Add PBT counterexamples"
          body: |
            PBTで発見された反例を追加します。

            - 自動生成されたPRです
            - 反例の詳細はファイルを確認してください
          branch: pbt-counterexamples
          commit-message: "test: add PBT counterexamples [auto]"
```

---

## その他のCIツール

### CircleCI

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  pbt-pr:
    docker:
      - image: python:3.11
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: pip install -r requirements-test.txt
      - run:
          name: Run PBT L0-L2
          command: |
            HYPOTHESIS_PROFILE=pr pytest tests/pbt/ \
              -m "level_0 or level_1 or level_2"

  pbt-nightly:
    docker:
      - image: python:3.11
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: pip install -r requirements-test.txt
      - run:
          name: Run PBT L3-L5
          command: |
            HYPOTHESIS_PROFILE=nightly pytest tests/pbt/ \
              -m "level_3 or level_4 or level_5"

workflows:
  pr:
    jobs:
      - pbt-pr

  nightly:
    triggers:
      - schedule:
          cron: "0 2 * * *"
          filters:
            branches:
              only: main
    jobs:
      - pbt-nightly
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test

pbt-pr:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements-test.txt
    - HYPOTHESIS_PROFILE=pr pytest tests/pbt/ -m "level_0 or level_1 or level_2"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

pbt-nightly:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements-test.txt
    - HYPOTHESIS_PROFILE=nightly pytest tests/pbt/ -m "level_3 or level_4 or level_5"
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

---

## モニタリング

### テスト実行時間の追跡

```python
# tests/pbt/conftest.py
import time
import json
from pathlib import Path

@pytest.fixture(autouse=True)
def track_test_duration(request):
    start = time.time()
    yield
    duration = time.time() - start

    # メトリクス記録
    metrics_file = Path("pbt-metrics.jsonl")
    with open(metrics_file, "a") as f:
        json.dump({
            "test": request.node.name,
            "duration": duration,
            "timestamp": time.time(),
            "level": getattr(request.node.get_closest_marker("level_0"), "name", "unknown"),
        }, f)
        f.write("\n")
```

### assume比率の監視

```python
from hypothesis import event

@given(st.integers())
def test_with_assume_tracking(x):
    if x <= 0:
        event("filtered: non-positive")
        assume(x > 0)

    if x >= 100:
        event("filtered: too large")
        assume(x < 100)

    assert some_property(x)

# 実行後に統計を確認
# pytest --hypothesis-show-statistics
```

### ダッシュボード用メトリクス

```yaml
# Prometheus / Grafana 用メトリクス
# pbt_test_duration_seconds{level="L0", test="test_foo"} 0.5
# pbt_test_passed{level="L0", test="test_foo"} 1
# pbt_counterexamples_found{level="L1", law="LAW-xxx"} 2
```
