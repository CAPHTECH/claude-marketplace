# CI/CD 統合ガイド

## GitHub Actions 設定

### 基本設定

```yaml
# .github/workflows/snapshot-tests.yml
name: Snapshot Tests

on:
  pull_request:
    paths:
      - '**/*.swift'
      - '**/*.xib'
      - '**/*.storyboard'
      - '**/Assets.xcassets/**'

jobs:
  snapshot-tests:
    runs-on: macos-14
    
    env:
      DEVELOPER_DIR: /Applications/Xcode_15.2.app/Contents/Developer
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          lfs: true  # 大きなスナップショットファイル用
      
      - name: Cache DerivedData
        uses: actions/cache@v4
        with:
          path: ~/Library/Developer/Xcode/DerivedData
          key: ${{ runner.os }}-derived-data-${{ hashFiles('**/*.swift') }}
          restore-keys: |
            ${{ runner.os }}-derived-data-
      
      - name: Run Snapshot Tests
        run: |
          set -o pipefail
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15,OS=17.2' \
            -only-testing:MyAppTests/SnapshotTests \
            -resultBundlePath TestResults.xcresult \
            | xcpretty --report junit --output test-results.xml
      
      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: |
            TestResults.xcresult
            test-results.xml
      
      - name: Upload Failed Snapshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: failed-snapshots
          path: |
            **/Snapshots/**/*
            **/testResults/**/*
            **/Failures/**/*
```

### 差分レポートの生成

```yaml
# .github/workflows/snapshot-diff-report.yml
name: Snapshot Diff Report

on:
  pull_request:

jobs:
  diff-report:
    runs-on: macos-14
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 差分比較に必要
      
      - name: Get Changed Files
        id: changed-files
        run: |
          CHANGED=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | grep -E '\.(swift|xib|storyboard)$' || true)
          echo "files=$CHANGED" >> $GITHUB_OUTPUT
      
      - name: Run Tests for Changed Files
        if: steps.changed-files.outputs.files != ''
        run: |
          # 変更されたファイルに関連するテストを特定して実行
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15,OS=17.2' \
            -only-testing:MyAppTests/SnapshotTests
      
      - name: Generate Diff Report
        if: failure()
        run: |
          # 差分画像を収集
          find . -name "*_diff.png" -o -name "*_failure.png" | while read file; do
            echo "::warning file=$file::Snapshot difference detected"
          done
      
      - name: Comment on PR
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const failedSnapshots = [];
            
            // 失敗したスナップショットを収集
            const files = fs.readdirSync('.', { recursive: true });
            for (const file of files) {
              if (file.endsWith('_failure.png')) {
                failedSnapshots.push(file);
              }
            }
            
            if (failedSnapshots.length > 0) {
              const body = `## Snapshot Test Failures
              
              The following snapshots have differences:
              ${failedSnapshots.map(f => `- \`${f}\``).join('\n')}
              
              Please review the artifacts for visual diff.`;
              
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: body
              });
            }
```

## スナップショット更新ワークフロー

### 手動更新

```yaml
# .github/workflows/update-snapshots.yml
name: Update Snapshots

on:
  workflow_dispatch:
    inputs:
      reason:
        description: 'Reason for updating snapshots'
        required: true
        type: string
      test_filter:
        description: 'Test filter (optional, e.g., ButtonSnapshotTests)'
        required: false
        type: string

jobs:
  update-snapshots:
    runs-on: macos-14
    
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Record Snapshots
        env:
          SNAPSHOT_RECORDING: "true"
        run: |
          TEST_FILTER="${{ github.event.inputs.test_filter }}"
          
          if [ -n "$TEST_FILTER" ]; then
            ONLY_TESTING="-only-testing:MyAppTests/SnapshotTests/$TEST_FILTER"
          else
            ONLY_TESTING="-only-testing:MyAppTests/SnapshotTests"
          fi
          
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15,OS=17.2' \
            $ONLY_TESTING || true
      
      - name: Commit Updated Snapshots
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          
          git add "*/__Snapshots__/*"
          
          if git diff --staged --quiet; then
            echo "No snapshot changes to commit"
          else
            git commit -m "Update snapshots: ${{ github.event.inputs.reason }}"
            git push
          fi
```

### PR ベースの更新

```yaml
# .github/workflows/snapshot-update-pr.yml
name: Create Snapshot Update PR

on:
  workflow_dispatch:
    inputs:
      base_branch:
        description: 'Base branch'
        required: true
        default: 'main'

jobs:
  create-update-pr:
    runs-on: macos-14
    
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.base_branch }}
      
      - name: Create Update Branch
        run: |
          BRANCH_NAME="snapshot-update-$(date +%Y%m%d-%H%M%S)"
          git checkout -b $BRANCH_NAME
          echo "BRANCH_NAME=$BRANCH_NAME" >> $GITHUB_ENV
      
      - name: Record All Snapshots
        env:
          SNAPSHOT_RECORDING: "true"
        run: |
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15,OS=17.2' \
            -only-testing:MyAppTests/SnapshotTests || true
      
      - name: Commit and Push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          
          git add "*/__Snapshots__/*"
          
          if git diff --staged --quiet; then
            echo "No changes"
            exit 0
          fi
          
          git commit -m "Update snapshots"
          git push -u origin ${{ env.BRANCH_NAME }}
      
      - name: Create Pull Request
        uses: actions/github-script@v7
        with:
          script: |
            const { data: pr } = await github.rest.pulls.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Update Snapshots',
              head: process.env.BRANCH_NAME,
              base: '${{ github.event.inputs.base_branch }}',
              body: `## Snapshot Update
              
              This PR updates snapshot images.
              
              ### Checklist
              - [ ] Review all snapshot changes
              - [ ] Verify changes are intentional
              - [ ] Approve if changes match design requirements`
            });
            
            console.log(`Created PR #${pr.number}`);
```

## 環境の固定

### シミュレータ設定

```yaml
jobs:
  test:
    runs-on: macos-14
    
    steps:
      - name: List Available Simulators
        run: xcrun simctl list devices available
      
      - name: Create Specific Simulator
        run: |
          # 特定のデバイスとOSバージョンを使用
          DEVICE_ID=$(xcrun simctl create "CI-iPhone15" \
            "com.apple.CoreSimulator.SimDeviceType.iPhone-15" \
            "com.apple.CoreSimulator.SimRuntime.iOS-17-2")
          echo "DEVICE_ID=$DEVICE_ID" >> $GITHUB_ENV
      
      - name: Boot Simulator
        run: |
          xcrun simctl boot ${{ env.DEVICE_ID }}
          xcrun simctl status_bar ${{ env.DEVICE_ID }} override \
            --time "9:41" \
            --batteryState charged \
            --batteryLevel 100
      
      - name: Run Tests
        run: |
          xcodebuild test \
            -scheme MyApp \
            -destination "id=${{ env.DEVICE_ID }}"
```

### 環境変数による制御

```swift
// テストコード内
extension XCTestCase {
    var isRecording: Bool {
        ProcessInfo.processInfo.environment["SNAPSHOT_RECORDING"] == "true"
    }
}

// ベーステストクラス
class SnapshotTestCase: XCTestCase {
    override func setUp() {
        super.setUp()
        
        if ProcessInfo.processInfo.environment["SNAPSHOT_RECORDING"] == "true" {
            isRecording = true
        }
    }
}
```

## Bitrise / CircleCI / Xcode Cloud

### Bitrise

```yaml
# bitrise.yml
workflows:
  snapshot-tests:
    steps:
      - activate-ssh-key:
          run_if: '{{getenv "SSH_RSA_PRIVATE_KEY" | ne ""}}'
      - git-clone: {}
      - cache-pull: {}
      - xcode-test:
          inputs:
            - scheme: MyApp
            - simulator_device: iPhone 15
            - simulator_os_version: "17.2"
            - xcodebuild_options: "-only-testing:MyAppTests/SnapshotTests"
      - cache-push:
          inputs:
            - cache_paths: |-
                ~/Library/Developer/Xcode/DerivedData
      - deploy-to-bitrise-io:
          inputs:
            - deploy_path: "$BITRISE_TEST_RESULT_DIR"
          run_if: always
```

### CircleCI

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  macos: circleci/macos@2

jobs:
  snapshot-tests:
    macos:
      xcode: "15.2.0"
    resource_class: macos.m1.medium.gen1
    
    steps:
      - checkout
      
      - restore_cache:
          keys:
            - v1-derived-data-{{ checksum "MyApp.xcodeproj/project.pbxproj" }}
            - v1-derived-data-
      
      - run:
          name: Run Snapshot Tests
          command: |
            xcodebuild test \
              -scheme MyApp \
              -destination 'platform=iOS Simulator,name=iPhone 15,OS=17.2' \
              -only-testing:MyAppTests/SnapshotTests
      
      - save_cache:
          key: v1-derived-data-{{ checksum "MyApp.xcodeproj/project.pbxproj" }}
          paths:
            - ~/Library/Developer/Xcode/DerivedData
      
      - store_artifacts:
          path: ~/Library/Developer/Xcode/DerivedData
          destination: derived-data

workflows:
  test:
    jobs:
      - snapshot-tests
```

### Xcode Cloud

```yaml
# ci_scripts/ci_post_xcodebuild.sh
#!/bin/bash

if [ "$CI_XCODEBUILD_ACTION" == "test-without-building" ]; then
    # テスト結果をアーティファクトとして保存
    cp -R "$CI_RESULT_BUNDLE_PATH" "$CI_ARCHIVE_PATH/"
    
    # 失敗したスナップショットを収集
    find "$CI_DERIVED_DATA_PATH" -name "*_failure.png" -exec cp {} "$CI_ARCHIVE_PATH/" \;
fi
```

## トラブルシューティング

### 問題1: CI と ローカルで結果が異なる

**解決策**:
```yaml
# 環境を完全に固定
- name: Setup Environment
  run: |
    # フォント設定
    defaults write -g AppleLanguages -array ja
    defaults write -g AppleLocale -string ja_JP
    
    # タイムゾーン
    sudo systemsetup -settimezone "Asia/Tokyo"
    
    # シミュレータリセット
    xcrun simctl shutdown all
    xcrun simctl erase all
```

### 問題2: テストが不安定

**解決策**:
```yaml
- name: Run Tests with Retry
  run: |
    MAX_RETRIES=3
    RETRY_COUNT=0
    
    until xcodebuild test ... || [ $RETRY_COUNT -ge $MAX_RETRIES ]; do
      RETRY_COUNT=$((RETRY_COUNT + 1))
      echo "Retry $RETRY_COUNT of $MAX_RETRIES"
      sleep 5
    done
```

### 問題3: スナップショットファイルが大きすぎる

**解決策**:
```yaml
# Git LFS を使用
- uses: actions/checkout@v4
  with:
    lfs: true

# または、スナップショットを別リポジトリで管理
- name: Checkout Snapshots
  uses: actions/checkout@v4
  with:
    repository: myorg/myapp-snapshots
    path: snapshots
```

### 問題4: テスト実行が遅い

**解決策**:
```yaml
# 並列実行
- name: Run Tests in Parallel
  run: |
    xcodebuild test \
      -parallel-testing-enabled YES \
      -maximum-parallel-testing-workers 4 \
      ...

# または、変更されたファイルに関連するテストのみ
- name: Get Changed Files
  run: |
    CHANGED_VIEWS=$(git diff --name-only origin/main | grep -E 'Views/.*\.swift$')
    # 関連するテストを特定
```

## ベストプラクティス

### 1. スナップショットの Git 管理

```gitattributes
# .gitattributes
*.png filter=lfs diff=lfs merge=lfs -text
*/__Snapshots__/** filter=lfs diff=lfs merge=lfs -text
```

### 2. PR での可視化

```yaml
- name: Upload Snapshots to PR
  if: failure()
  uses: actions/github-script@v7
  with:
    script: |
      // 失敗したスナップショットをPRコメントに追加
      // 差分画像をインライン表示
```

### 3. キャッシュ戦略

```yaml
- name: Cache Snapshots
  uses: actions/cache@v4
  with:
    path: |
      */__Snapshots__/**
    key: snapshots-${{ hashFiles('**/__Snapshots__/**') }}
```
