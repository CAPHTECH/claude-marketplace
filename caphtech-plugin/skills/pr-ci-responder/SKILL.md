---
name: pr-ci-responder
context: fork
description: |
  PRのCI失敗を自動診断・修正し、成功するまでリトライするスキル。
  GitHub Actionsの実際のログを取得し、エラーを構造化分類して優先順位順に修正する。

  トリガー条件:
  - 「CIを修正して」「CI直して」
  - 「PR #N のCIが落ちている」
  - PRのCI失敗を自動修正したい時
  - 「CIが通るまで直して」
  - 「/pr-ci-responder」
---

# PR CI Responder

CI失敗を診断・修正し、成功するまでリトライする。

## ワークフロー概要

```
Diagnose → Fix → Verify → Commit & Push → Wait → Evaluate
                                                    │
                                           成功 → 完了
                                           失敗 → エスカレーション判断
                                                    │
                                           継続 → Diagnose に戻る（最大5回）
                                           中断 → ユーザーに報告
```

## 制約

- **最大リトライ**: 5回
- **CI待機タイムアウト**: 最大10分（30秒間隔）
- **対応言語**: JS/TS, Python, Go, Flutter, Elixir
- **対応CI**: GitHub Actions のみ（非Actions検出時は即エスカレーション）

## Phase 1: Diagnose（診断）

失敗したCI runのログを取得し、エラーを分類する。

### ログ取得

```bash
# 1. PRのチェック状態を確認（主軸）
gh pr checks --json name,state,link

# 2. 失敗したcheckのリンクからrun_idを抽出
# link例: https://github.com/{owner}/{repo}/actions/runs/{run_id}/...

# 3. run_idが取れない場合のフォールバック
gh run list --branch $(git branch --show-current) --status failure --limit 5 --json databaseId,name,conclusion

# 4. 失敗ログを取得
gh run view {run_id} --log-failed
```

**重要**: `gh pr checks` のリンクからの run_id 抽出を主軸とする。`gh run list` はフォールバック。

### エラー分類

分類ルールの詳細は [references/error-classification.md](references/error-classification.md) 参照。

| カテゴリ | パターン | 優先度 |
|----------|---------|--------|
| `lint` | ESLint, Prettier, Ruff, golangci-lint, dart analyze (info/warning), mix format | 1（最高） |
| `type` | TypeScript TS\d+, mypy error, Dialyzer, dart analyze (error) | 2 |
| `build` | compile error, Module not found, import error, pub get failed, mix compile | 3 |
| `test` | FAIL, AssertionError, Expected/Received, ExUnit failure, test failed | 4 |
| `other` | 上記に該当しない | 5 |

## Phase 2: Fix（修正）

### 修正優先順位: lint → type → build → test

低優先度のエラーは高優先度の修正で解消されることが多いため、この順序を厳守する。

### 修正手順

1. 最も優先度の高いカテゴリから修正
2. 自動修正ツールがあれば最初に実行
3. 自動修正不可のものはコード編集
4. 1カテゴリ修正ごとにローカル検証

言語別修正アクションの詳細は [references/language-strategies.md](references/language-strategies.md) 参照。

## Phase 3: Verify（ローカル検証）

修正後、push前にローカルで検証可能なチェックを実行する。

```bash
# 言語・プロジェクトに応じて適切なコマンドを選択
# lint/format チェック
# 型チェック
# テスト実行
```

ローカル検証で失敗した場合は、push せずに修正を続ける。

## Phase 4: Commit & Push

```bash
# 修正ファイルのみステージング（-A は絶対に使わない）
git add {修正したファイル1} {修正したファイル2} ...

# コミットメッセージは修正内容を明記
git commit -m "fix(ci): lint自動修正 + テスト期待値修正"

# プッシュ
git push
```

## Phase 5: Wait（CI待機）

```bash
# CI完了待機ループ（最大10分、30秒間隔）
for i in $(seq 1 20); do
  result=$(gh pr checks --json name,state 2>/dev/null)
  # pending/in_progress が 0 件なら完了
  pending=$(echo "$result" | jq '[.[] | select(.state == "PENDING" or .state == "IN_PROGRESS")] | length')
  if [ "$pending" -eq 0 ]; then
    break
  fi
  sleep 30
done
```

## Phase 6: Evaluate（評価）

### 成功判定

全チェックが成功 → 完了報告を出力

### エスカレーション判断

エスカレーションルールの詳細は [references/escalation-rules.md](references/escalation-rules.md) 参照。

| 条件 | アクション |
|------|-----------|
| 全チェック成功 | 完了 |
| 同一エラー2回連続 | 中断 → エラー詳細を報告 |
| エラー数増加 | ロールバック提案 → ユーザー確認 |
| CI環境固有エラー | 中断 → 環境差異を報告 |
| 最大リトライ到達（5回） | 中断 → 対応サマリーを報告 |
| 非GitHub Actions CI | 即中断 → CI環境を報告 |

エスカレーション条件に該当しない場合 → Phase 1（Diagnose）に戻る。

## 出力形式

```yaml
ci_fix_result:
  pr_ref: "owner/repo#123"
  branch: "feature/xxx"
  status: "success" | "escalated" | "max_retries"

  attempts:
    - attempt: 1
      errors_found:
        - category: lint
          count: 3
          details: "ESLint: no-unused-vars (2), prettier (1)"
        - category: test
          count: 1
          details: "FAIL src/__tests__/user.test.ts - Expected 200, received 404"
      fixes_applied:
        - category: lint
          action: "npx eslint --fix ."
          files: ["src/api/users.ts", "src/utils/helpers.ts"]
        - category: test
          action: "テストの期待値を修正"
          files: ["src/__tests__/user.test.ts"]
      commit: "abc1234"
      ci_result: "success"

  summary:
    total_attempts: 1
    errors_fixed: 4
    files_modified: ["src/api/users.ts", "src/utils/helpers.ts", "src/__tests__/user.test.ts"]
    final_status: "All CI checks passed"
```

## ガードレール

1. **`git add -A` 禁止**: 修正したファイルのみをステージング。絶対に `git add -A` や `git add .` を使わない
2. **破壊的変更の回避**: テストカバレッジ低下、既存機能の破壊を避ける
3. **ローカル検証必須**: push前にローカルで検証可能なチェックを実行
4. **エスカレーション判断の厳守**: 同一エラー繰り返し・エラー増加時は即座に中断
5. **コミットメッセージの明確化**: 何を修正したかが分かるメッセージ

## 使用例

```
User: CIを修正して

Claude:
## CI修正開始

### Diagnose（Attempt 1/5）

失敗チェック:
- lint (ESLint): FAIL
- test (Jest): FAIL

エラー分類:
| # | カテゴリ | 詳細 |
|---|---------|------|
| 1 | lint | no-unused-vars: src/api/users.ts:12 |
| 2 | lint | prettier: src/utils/helpers.ts |
| 3 | test | FAIL: src/__tests__/user.test.ts - Expected 200, got 404 |

### Fix

#### [1/2] lint修正
→ `npx eslint --fix .` 実行
→ 2件の自動修正完了

#### [2/2] test修正
→ src/__tests__/user.test.ts:45 の期待値を修正

### Verify
→ eslint: PASS
→ jest: PASS

### Commit & Push
→ コミット: fix(ci): lint自動修正 + テスト期待値修正
→ プッシュ完了

### Wait
→ CI実行中... (30s)
→ CI実行中... (60s)
→ CI完了

### Evaluate
→ All 5 checks passed

CI修正が完了しました。1回のリトライで全チェックが成功しています。
```
