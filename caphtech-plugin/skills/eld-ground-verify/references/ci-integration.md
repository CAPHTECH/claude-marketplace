# CI/CD統合ガイド

eld-ground-verifyをCI/CDパイプラインに統合し、PR作成前の自動検証を実現する。

## GitHub Actions統合

### 基本ワークフロー

**.github/workflows/pre-completion-check.yml**:

```yaml
name: ELD Pre-Completion Check

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  pre-completion-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Run Pre-Completion Check
        id: check
        run: |
          bash scripts/pre-completion-check.sh
        continue-on-error: true

      - name: Comment PR (Success)
        if: steps.check.outcome == 'success'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✓ **PR READY**\n\nAll completion criteria are met. You can merge this PR.'
            })

      - name: Comment PR (Failure)
        if: steps.check.outcome == 'failure'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✗ **PR NOT READY**\n\nPre-completion check failed. Please review the logs and fix the errors.'
            })

      - name: Fail if check failed
        if: steps.check.outcome == 'failure'
        run: exit 1
```

---

### 詳細レポート付きワークフロー

**.github/workflows/pre-completion-detailed.yml**:

```yaml
name: ELD Pre-Completion Check (Detailed)

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  pre-completion-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Run Pre-Completion Check
        id: check
        run: |
          bash scripts/pre-completion-check.sh > check-result.txt 2>&1
          cat check-result.txt
        continue-on-error: true

      - name: Upload check result
        uses: actions/upload-artifact@v3
        with:
          name: pre-completion-check-result
          path: check-result.txt

      - name: Parse check result
        id: parse
        run: |
          ERRORS=$(grep -c "✗ ERROR" check-result.txt || echo 0)
          WARNINGS=$(grep -c "⚠ WARNING" check-result.txt || echo 0)

          echo "errors=$ERRORS" >> $GITHUB_OUTPUT
          echo "warnings=$WARNINGS" >> $GITHUB_OUTPUT

      - name: Comment PR with details
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const result = fs.readFileSync('check-result.txt', 'utf8');

            const errors = ${{ steps.parse.outputs.errors }};
            const warnings = ${{ steps.parse.outputs.warnings }};

            let status = '✓ **PR READY**';
            let message = 'All completion criteria are met.';

            if (errors > 0) {
              status = '✗ **PR NOT READY**';
              message = `Found ${errors} error(s) that must be fixed.`;
            } else if (warnings > 0) {
              message += `\n\n⚠ Found ${warnings} warning(s) - review recommended.`;
            }

            const body = `${status}\n\n${message}\n\n<details>\n<summary>Full Check Result</summary>\n\n\`\`\`\n${result}\n\`\`\`\n</details>`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            })

      - name: Fail if errors found
        if: steps.parse.outputs.errors > 0
        run: exit 1
```

---

## GitLab CI統合

**.gitlab-ci.yml**:

```yaml
pre-completion-check:
  stage: test
  script:
    - bash scripts/pre-completion-check.sh
  only:
    - merge_requests
  artifacts:
    when: always
    paths:
      - check-result.txt
    reports:
      junit: check-result.xml
```

---

## CircleCI統合

**.circleci/config.yml**:

```yaml
version: 2.1

jobs:
  pre-completion-check:
    docker:
      - image: cimg/base:stable
    steps:
      - checkout
      - run:
          name: Run Pre-Completion Check
          command: bash scripts/pre-completion-check.sh
      - store_artifacts:
          path: check-result.txt

workflows:
  pr-check:
    jobs:
      - pre-completion-check:
          filters:
            branches:
              only: /^pull\/.*/
```

---

## pre-commit hook統合

**.git/hooks/pre-commit**:

```bash
#!/bin/bash

echo "Running ELD Pre-Completion Check..."

if ! bash scripts/pre-completion-check.sh; then
    echo
    echo "Pre-completion check failed."
    echo "Fix the errors above or use 'git commit --no-verify' to skip this check."
    exit 1
fi

echo "Pre-completion check passed."
exit 0
```

**インストール**:

```bash
# hookをインストール
chmod +x scripts/pre-completion-check.sh
cp scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

## Status Check統合

### Required Status Checks設定

GitHub Settingsで、PR作成前の必須チェックとして設定:

1. Repository Settings → Branches
2. Branch protection rule for `main`
3. Require status checks to pass before merging
4. Select: `ELD Pre-Completion Check`

これにより、Pre-Completion Checkが通過しないとマージ不可能になる。

---

## 自動修正提案

### GitHub Actions with Suggestions

```yaml
name: ELD Pre-Completion Check with Suggestions

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  check-and-suggest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Check
        id: check
        run: bash scripts/pre-completion-check.sh > result.txt
        continue-on-error: true

      - name: Suggest Fixes
        if: steps.check.outcome == 'failure'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const result = fs.readFileSync('result.txt', 'utf8');

            let suggestions = [];

            if (result.includes('Orphan Law detected')) {
              suggestions.push('**Fix Law orphans**: Update link-map.yaml to reference all Laws');
            }

            if (result.includes('Evidence L1 missing')) {
              suggestions.push('**Add L1 Evidence**: Create unit tests for S0/S1 Laws');
            }

            if (result.includes('Test failure count')) {
              suggestions.push('**Reduce test failures**: Analyze failure patterns and update tests');
            }

            if (suggestions.length > 0) {
              const body = '## Suggested Fixes\n\n' + suggestions.map(s => `- ${s}`).join('\n');

              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: body
              });
            }
```

---

## Slack通知統合

### GitHub Actions + Slack

```yaml
- name: Notify Slack (Failure)
  if: steps.check.outcome == 'failure'
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "❌ PR Pre-Completion Check Failed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*PR*: <${{ github.event.pull_request.html_url }}|#${{ github.event.pull_request.number }}>\n*Author*: ${{ github.actor }}\n*Status*: Failed"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## カスタムチェックの追加

### 独自チェックスクリプトの統合

**scripts/custom-checks/security-check.sh**:

```bash
#!/bin/bash

echo "Running security check..."

# Check for hardcoded secrets
if grep -r "API_KEY\s*=\s*['\"]" src/; then
    echo "ERROR: Hardcoded API key detected"
    exit 1
fi

# Check for vulnerable dependencies
if npm audit --audit-level=high; then
    echo "SUCCESS: No high-severity vulnerabilities"
    exit 0
else
    echo "ERROR: High-severity vulnerabilities found"
    exit 1
fi
```

**pre-completion-check.sh への統合**:

```bash
# Phase 6: Custom Checks
echo "=== Phase 6: Custom Checks ==="
echo

if [ -d "scripts/custom-checks" ]; then
    for script in scripts/custom-checks/*.sh; do
        echo "Running: $(basename $script)"
        bash $script
        echo
    done
fi
```

---

## ベストプラクティス

### 1. 並列実行で高速化

```yaml
jobs:
  check-evidence-pack:
    runs-on: ubuntu-latest
    steps:
      - run: bash scripts/check-evidence-pack.sh

  check-orphan:
    runs-on: ubuntu-latest
    steps:
      - run: bash scripts/check-orphan.sh

  check-evidence-ladder:
    runs-on: ubuntu-latest
    steps:
      - run: bash scripts/check-evidence-ladder.sh

  aggregate:
    needs: [check-evidence-pack, check-orphan, check-evidence-ladder]
    runs-on: ubuntu-latest
    steps:
      - run: echo "All checks passed"
```

### 2. キャッシュで高速化

```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### 3. 段階的ロールアウト

```yaml
# 最初は warning のみ（失敗でもマージ可能）
- name: Run Check (Warning Only)
  run: bash scripts/pre-completion-check.sh || echo "Check failed but continuing"

# 2週間後に error に格上げ（失敗でマージ不可）
- name: Run Check (Blocking)
  run: bash scripts/pre-completion-check.sh
```

---

## トラブルシューティング

### CI/CDが常に失敗する

**原因**: Evidence Packディレクトリが存在しない

**対策**:
```yaml
- name: Create Evidence Pack directory
  run: mkdir -p evidence-pack/evidence
```

### タイムアウトする

**原因**: チェックが長時間実行される

**対策**:
```yaml
- name: Run Check
  timeout-minutes: 10
  run: bash scripts/pre-completion-check.sh
```

---

## まとめ

### CI/CD統合の核心原則

1. **自動化**: PR作成前に自動実行
2. **高速化**: 並列実行とキャッシュ
3. **可視化**: 結果をPRコメントで共有
4. **段階的導入**: warning → error への段階的移行
5. **カスタマイズ**: プロジェクト固有のチェック追加

すべてのCI/CDパイプラインで、Pre-Completion Checkを必須ステップとして組み込む。
