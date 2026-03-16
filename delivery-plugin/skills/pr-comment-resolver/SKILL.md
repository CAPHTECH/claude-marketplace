---
name: pr-comment-resolver
context: fork
description: PRコメント（レビュー/インライン/CodeRabbit outside diff range含む）を収集・分類し、優先順位に従って対応・返信を実行する
---

# PR Comment Resolver

PRコメントを収集・分類し、優先順位に従って対応を実行する。

## ワークフロー

```
1. Collect   → 全コメント取得
2. Classify  → カテゴリ分類（must/question/should/could/note）
3. Prioritize → 優先順位付け
4. Execute   → 対応実行（修正/回答）
5. Reply     → コメント返信
```

## Step 1: コメント収集

### 1-1. 基本情報取得

```bash
# PR情報取得
gh pr view {pr_number} --json number,title,body,author,state,headRefName

# リポジトリ情報
gh repo view --json owner,name
```

### 1-2. 全コメント取得（ページネーション必須）

GitHub APIはデフォルト30件しか返さない。`--paginate`で全件取得する。

```bash
# 一般コメント
gh api --paginate -F per_page=100 repos/{owner}/{repo}/issues/{pr_number}/comments

# レビューコメント（インライン）
gh api --paginate -F per_page=100 repos/{owner}/{repo}/pulls/{pr_number}/comments

# レビュー本体（body含む）
gh api --paginate -F per_page=100 repos/{owner}/{repo}/pulls/{pr_number}/reviews
```

> `--paginate`は複数ページのJSON配列を連結出力する。`--jq`と併用して必要フィールドのみ抽出すると扱いやすい。

### 1-3. 解決済みスレッドの除外

REST APIではスレッドの解決状態を取得できない。GraphQL APIを使用する。

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $pr: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $pr) {
        reviewThreads(first: 100) {
          nodes {
            isResolved
            comments(first: 100) {
              nodes { id databaseId body author { login } path line }
            }
          }
        }
      }
    }
  }
' -f owner="{owner}" -f repo="{repo}" -F pr={pr_number}
```

解決済み（`isResolved: true`）のスレッドに属するコメントは収集対象から除外する。

### 1-4. CodeRabbitレビューbodyの解析

CodeRabbit（`user.login == "coderabbitai[bot]"`）のレビューbodyには構造化セクションが含まれる。
レビューbodyから以下を抽出する。

#### Outside diff range comments の抽出

diff範囲外の指摘はインラインコメントではなく、レビューbody内に埋め込まれる:

```html
<details>
<summary>⚠️ Outside diff range comments (N)</summary>

**src/config.py:42-45**: Consider adding validation.

**src/utils.py:100**: This function could use memoization.

</details>
```

抽出パターン: `**{filepath}:{line_or_range}**:` の後に指摘テキストが続く。
これらは通常のコメントと同じ分類フロー（Step 2）に流す。`source: "review_body_outside_diff"` として識別する。

#### その他の構造化セクション（情報提供のみ）

以下のセクションは対応不要だが、コンテキスト理解に利用する:

| セクション | 用途 |
|-----------|------|
| Walkthrough | 変更概要。対応不要 |
| Summary | PR全体の要約。対応不要 |
| Sequence diagram | フロー可視化。対応不要 |

#### Actionable / Nitpick コメントの識別

CodeRabbitのインラインコメントには以下のラベルが付くことがある:

- `🔴 Actionable` — 修正が必要な指摘。`must` or `should` に分類
- `🟡 Nitpick` — スタイル・好みの指摘。`could` に分類

## Step 2: 分類

分類ルールの詳細は [references/comment-classification.md](references/comment-classification.md) 参照。

| カテゴリ | 優先度 | 対応 |
|----------|--------|------|
| `must` | 1 | 必須修正（セキュリティ、ブロッカー） |
| `question` | 2 | 回答必須 |
| `should` | 3 | 推奨修正 |
| `could` | 4 | 任意対応 |
| `note` | 5 | 対応不要 |

## Step 3: 優先順位付け

```yaml
priority_order:
  1. must（セキュリティ > データ整合性 > 機能）
  2. question（設計意図 > 実装詳細）
  3. should
  4. could
```

## Step 4: 対応実行

### 修正が必要な場合

1. 該当ファイルを読み取り
2. 指摘内容を理解
3. 修正を実施
4. テスト実行（該当する場合）
5. コミット

### 回答が必要な場合

1. 質問内容を理解
2. コードベースを調査
3. 回答を作成

## Step 5: 返信

返信テンプレートは [references/response-templates.md](references/response-templates.md) 参照。

```bash
# レビューコメントへの返信（スレッド内）
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies \
  -f body="修正しました。 ✅ commit: {sha}"

# 一般コメントへの返信
gh pr comment {pr_number} --body "回答内容"

# レビュー全体への返信（outside diff range対応報告等）
gh pr review {pr_number} --comment --body "回答内容"
```

### Outside diff range コメントへの返信

レビューbodyから抽出したコメントにはインラインで返信できない。
レビュー全体へのコメントとして、対応内容を一括報告する:

```markdown
## Outside diff range 指摘への対応

| ファイル | 指摘 | 対応 | commit |
|---------|------|------|--------|
| src/config.py:42-45 | バリデーション追加 | 修正済み | abc1234 |
| src/utils.py:100 | メモ化 | 見送り（理由: ...） | - |
```

## 出力形式

```yaml
pr_comment_resolution:
  pr_ref: "owner/repo#123"
  summary:
    total: 10
    resolved: 8
    pending: 2

  resolved:
    - id: "comment_123"
      category: must
      action: "コード修正"
      commit: "abc1234"
      reply_sent: true

    - id: "comment_456"
      category: question
      action: "回答"
      reply_sent: true

  pending:
    - id: "comment_789"
      category: should
      reason: "追加調査が必要"
      next_action: "設計確認後に対応"
```

## 使用例

```
User: PR #45 のコメントに対応して

Claude:
## PR Comment Resolver 実行中...

### Step 1: コメント収集
PR #45: "ユーザー検索API追加"
- 一般コメント: 2件
- レビューコメント: 5件
- レビュー: 1件（CHANGES_REQUESTED）

### Step 2: 分類結果

| # | カテゴリ | 作者 | 内容 |
|---|---------|------|------|
| 1 | must | @reviewer | SQLインジェクション対策 |
| 2 | question | @reviewer | この設計の意図は？ |
| 3 | should | @reviewer | ページネーション追加 |
| 4 | note | @reviewer | LGTM |

### Step 3: 対応中...

#### [1/3] must: SQLインジェクション対策
src/api/users.ts:45 を修正中...
✅ 修正完了 (commit: abc1234)
✅ 返信送信完了

#### [2/3] question: 設計意図の説明
回答を作成中...
✅ 返信送信完了

#### [3/3] should: ページネーション追加
src/api/users.ts を修正中...
✅ 修正完了 (commit: def5678)
✅ 返信送信完了

### 完了サマリー
- 対応完了: 3/3
- コミット: 2件
- 返信: 3件
```

## ガードレール

1. **セキュリティ指摘は最優先**: must/セキュリティは必ず最初に対応
2. **確認なしの大規模変更禁止**: 影響範囲が大きい場合はユーザーに確認
3. **テスト実行**: 修正後は関連テストを実行
4. **返信必須**: 対応した指摘には必ず返信
5. **解決済みスレッドは無視**: `isResolved: true` のスレッドは対応対象外
6. **最新レビュー優先**: 同一ファイル・行への複数指摘は最新のものを優先
