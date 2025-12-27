# 差分検出（Spec Drift Detection）

## 目的

コード変更によってspecのどの部分が無効になったか（または更新が必要か）を検出する。

継続性の観点では、spec生成よりもこの差分検出が重要。

## 基本原理

specの各断定には `evidence` （根拠リンク）が付いている。

```yaml
response:
  status: 200
  confidence: Verified
  evidence:
    file: src/api/users.ts
    line: 52-60
    symbol: getUserById
```

この根拠リンクが変更されたら、該当specは「要レビュー」になる。

## 手動比較ガイド

### Step 1: evidenceの抽出

specファイルからすべてのevidenceを抽出:

```bash
# YAMLからevidence抽出
grep -E "^\s+file:|^\s+line:|^\s+symbol:" specs/layer-a/*.yaml
```

### Step 2: 変更ファイルの特定

```bash
# 最新コミットの変更
git diff --name-only HEAD~1

# 特定範囲の変更
git diff --name-only <from-commit>..<to-commit>

# 未コミットの変更
git diff --name-only
```

### Step 3: 影響specの特定

```bash
# 変更ファイルに関連するspecを検索
changed_files=$(git diff --name-only HEAD~1)
for file in $changed_files; do
  echo "=== $file に関連するspec ==="
  grep -rl "file: $file" specs/
done
```

### Step 4: 詳細確認

影響があるspecについて、以下を確認:

1. 根拠の行番号がまだ有効か
2. 根拠のシンボルがまだ存在するか
3. 振る舞いが変わっていないか

## git連携スクリプト

### spec-drift-check.sh

```bash
#!/bin/bash
# spec-drift-check.sh - specの陳腐化を検出

SPEC_DIR="${1:-specs}"
BASE_COMMIT="${2:-HEAD~1}"

echo "=== Spec Drift Check ==="
echo "Base: $BASE_COMMIT"
echo "Spec Dir: $SPEC_DIR"
echo ""

# 変更されたファイルを取得
changed_files=$(git diff --name-only "$BASE_COMMIT")

if [ -z "$changed_files" ]; then
  echo "No changes detected."
  exit 0
fi

echo "Changed files:"
echo "$changed_files"
echo ""

# 影響を受けるspecを特定
affected_specs=""
for file in $changed_files; do
  matching_specs=$(grep -rl "file: .*$file" "$SPEC_DIR" 2>/dev/null)
  if [ -n "$matching_specs" ]; then
    affected_specs="$affected_specs$matching_specs"$'\n'
  fi
done

affected_specs=$(echo "$affected_specs" | sort | uniq | grep -v '^$')

if [ -z "$affected_specs" ]; then
  echo "No specs affected by these changes."
  exit 0
fi

echo "=== Affected Specs ==="
echo "$affected_specs"
echo ""

# 詳細レポート
echo "=== Detailed Report ==="
for spec in $affected_specs; do
  echo "--- $spec ---"
  # このspec内のevidenceを抽出
  grep -A2 "evidence:" "$spec" | grep "file:" | while read -r line; do
    ref_file=$(echo "$line" | sed 's/.*file: //' | tr -d '"')
    if echo "$changed_files" | grep -q "$ref_file"; then
      echo "  AFFECTED: $ref_file"
    fi
  done
done
```

### pre-commit hook

```bash
#!/bin/bash
# .git/hooks/pre-commit - コミット前にspec影響を警告

SPEC_DIR="specs"

# ステージされたファイル
staged_files=$(git diff --cached --name-only)

# 影響specを検索
affected=""
for file in $staged_files; do
  matching=$(grep -rl "file: .*$file" "$SPEC_DIR" 2>/dev/null)
  if [ -n "$matching" ]; then
    affected="$affected$matching"$'\n'
  fi
done

affected=$(echo "$affected" | sort | uniq | grep -v '^$')

if [ -n "$affected" ]; then
  echo "⚠️  Warning: The following specs may need updates:"
  echo "$affected"
  echo ""
  echo "Consider reviewing these specs after this commit."
  echo "To skip this check, use: git commit --no-verify"
fi

# 警告のみ、コミットはブロックしない
exit 0
```

## CI統合

### GitHub Actions例

```yaml
name: Spec Drift Check

on:
  pull_request:
    branches: [main]

jobs:
  check-spec-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check Spec Drift
        run: |
          # 変更ファイルを取得
          changed=$(git diff --name-only origin/main...HEAD)

          # 影響specを検出
          affected=""
          for file in $changed; do
            matching=$(grep -rl "file: .*$file" specs/ 2>/dev/null || true)
            affected="$affected$matching"
          done

          affected=$(echo "$affected" | sort | uniq | grep -v '^$')

          if [ -n "$affected" ]; then
            echo "::warning::The following specs may need updates:"
            echo "$affected"

            # PRにコメント（オプション）
            echo "AFFECTED_SPECS<<EOF" >> $GITHUB_ENV
            echo "$affected" >> $GITHUB_ENV
            echo "EOF" >> $GITHUB_ENV
          fi

      - name: Comment on PR
        if: env.AFFECTED_SPECS != ''
        uses: actions/github-script@v7
        with:
          script: |
            const affected = process.env.AFFECTED_SPECS;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## ⚠️ Spec Drift Warning\n\nThe following specs may need updates:\n\n\`\`\`\n${affected}\n\`\`\`\n\nPlease review these specs and update if necessary.`
            });
```

## 差分タイプ分類

### Type 1: 構造変更

ファイル移動・リネーム・削除

```
検出: evidenceのfileパスが存在しない
対応: specのevidence更新 or spec削除
```

### Type 2: 行番号ズレ

コード追加・削除による行番号変動

```
検出: evidenceの行番号でシンボルが見つからない
対応: 行番号の更新
```

### Type 3: シンボル変更

関数・クラス名の変更

```
検出: evidenceのsymbolが存在しない
対応: symbol名の更新 + 振る舞い確認
```

### Type 4: 振る舞い変更

ロジック変更

```
検出: 自動検出困難（人間レビュー必要）
対応: specの内容更新
```

## 優先度付け

すべてのspec影響を同等に扱わない。優先度を付ける:

| 優先度 | 条件 | 対応 |
|--------|------|------|
| P0 | 層A + Verified | 即座に確認・更新 |
| P1 | 層B + Observed | 次回リリース前に確認 |
| P2 | 層A + Observed | 週次で確認 |
| P3 | 層B + Assumed | 月次で確認 |
| P4 | 層C | 四半期で確認 |

## レポートフォーマット

```markdown
# Spec Drift Report

Date: 2024-01-15
Commit Range: abc123..def456

## Summary

- Total changed files: 15
- Affected specs: 8
- P0 (critical): 2
- P1 (high): 3
- P2 (medium): 2
- P3 (low): 1

## P0 - Critical

### specs/layer-a/users-api.yaml

- **Evidence**: src/api/users.ts:52-60
- **Change type**: Line number shift
- **Impact**: Response schema may have changed
- **Action required**: Verify response structure

## P1 - High

...
```
