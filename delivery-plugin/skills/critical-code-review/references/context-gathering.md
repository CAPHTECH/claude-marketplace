# Context Gathering Reference

Phase 1で収集するコンテキスト情報の詳細手順。

## 1. Diff取得

レビューターゲットに応じたdiff取得。

```bash
# PR
gh pr diff <number>

# ブランチdiff（コミット済みのみ）
git diff <base>...HEAD
# unstaged変更を含める場合は追加で:
# git diff

# 最近のコミット
git diff HEAD~1..HEAD

# ディレクトリ
git diff <base>...HEAD -- <directory>

# ファイル（unstaged含む）
git diff HEAD -- <file>
```

## 2. PR/Issue意図の理解

PRまたはIssueが存在する場合、変更の意図を把握する。

```bash
# PR情報
gh pr view <number> --json title,body,labels,milestone

# PR本文からIssue番号を抽出
gh pr view <number> --json body --jq '.body' | grep -oE '#[0-9]+'

# 関連Issue
gh issue view <issue_number> --json title,body,labels
```

抽出すべき情報:
- 変更の目的（バグ修正/機能追加/リファクタリング）
- 受入条件（あれば）
- 関連する制約・前提

## 3. 変更ファイルの依存グラフ

変更されたファイルのimport/export関係を把握する。

### 言語別import検出パターン

| 言語 | importパターン | コマンド例 |
|------|---------------|-----------|
| JS/TS | `import.*from`, `require(` | `grep -rn "import.*from\|require(" <file>` |
| Python | `import `, `from.*import` | `grep -rn "^import \|^from.*import" <file>` |
| Go | `import (`, `import "` | `grep -rn 'import' <file>` |
| Rust | `use `, `mod ` | `grep -rn "^use \|^mod " <file>` |
| Ruby | `require`, `require_relative` | `grep -rn "require\|require_relative" <file>` |
| Dart | `import '` | `grep -rn "import '" <file>` |

### Caller検出（逆依存）

変更されたファイルの公開シンボルを使用している箇所を検出する。

```bash
# 変更ファイルからexportされたシンボルを抽出
# そのシンボルをgrepで他ファイルから検索

# 例: TypeScript
grep -rn "from.*<changed-module>" --include="*.ts" --include="*.tsx" .
```

## 4. ファイル安定性（変更頻度）

頻繁に変更されるファイル（ホットスポット）を特定する。

```bash
# 過去90日の変更頻度
git log --since="90 days ago" --pretty=format: --name-only -- <file> | sort | uniq -c | sort -rn

# 変更されたファイルの最終変更者・日時
git log -1 --format="%an %ai" -- <file>

# 変更されたファイルのコミット数
git log --oneline -- <file> | wc -l
```

安定性の判断基準:
- **不安定**: 過去90日で10回以上変更 → レビュー重点対象
- **やや不安定**: 過去90日で5-9回変更 → 注意して確認
- **安定**: 過去90日で4回以下 → 変更の妥当性を特に確認

## 5. テストカバレッジ確認

変更ファイルに対応するテストの存在を確認する。

### テストファイル検出パターン

| 言語/FW | テストファイルパターン |
|---------|---------------------|
| JS/TS (Jest) | `*.test.ts`, `*.spec.ts`, `__tests__/*.ts` |
| Python (pytest) | `test_*.py`, `*_test.py`, `tests/` |
| Go | `*_test.go` |
| Rust | `#[cfg(test)]`（同一ファイル内）, `tests/` |
| Ruby (RSpec) | `spec/*_spec.rb` |
| Dart | `test/*_test.dart` |

```bash
# テストファイルの存在確認（JSの例）
# src/utils/auth.ts → src/utils/auth.test.ts or src/utils/__tests__/auth.test.ts

# テストの有無を一括確認
for f in <changed-files>; do
  test_file=$(echo "$f" | sed 's/\.ts$/.test.ts/')
  [ -f "$test_file" ] && echo "✓ $test_file" || echo "✗ No test for $f"
done
```

## 6. プロジェクトツール検出

利用可能なlinter/formatter/型チェッカーを検出する。Phase 2で使用する。

```bash
# package.json からスクリプト検出
cat package.json | grep -E '"(lint|format|typecheck|test|check)"'

# 設定ファイル検出
ls -1 .eslintrc* eslint.config* .prettierrc* tsconfig.json \
     pyproject.toml setup.cfg .flake8 .mypy.ini \
     .golangci.yml Cargo.toml .rubocop.yml \
     analysis_options.yaml 2>/dev/null
```

検出結果は `[tool-detection]` としてPhase 2に引き渡す。
