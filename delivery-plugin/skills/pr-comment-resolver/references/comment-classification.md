# PRコメント分類ルール

## コメント種別

### 取得対象

| 種別 | gh APIエンドポイント | 説明 |
|------|---------------------|------|
| Issue Comment | `repos/{owner}/{repo}/issues/{pr}/comments` | PR全体への一般コメント |
| Review Comment | `repos/{owner}/{repo}/pulls/{pr}/comments` | コード行へのインラインコメント |
| Review | `repos/{owner}/{repo}/pulls/{pr}/reviews` | レビュー本体（APPROVE/REQUEST_CHANGES等） |
| Review Body埋込 | （Reviewのbodyフィールド内） | CodeRabbit等がdiff範囲外コメントを埋め込む |

### 取得コマンド（ページネーション必須）

GitHub APIはデフォルト30件/ページ。`--paginate -F per_page=100` で全件取得する。

```bash
# 一般コメント
gh api --paginate -F per_page=100 repos/{owner}/{repo}/issues/{pr_number}/comments

# レビューコメント（インライン）
gh api --paginate -F per_page=100 repos/{owner}/{repo}/pulls/{pr_number}/comments

# レビュー本体（bodyフィールドの解析が必要）
gh api --paginate -F per_page=100 repos/{owner}/{repo}/pulls/{pr_number}/reviews

# レビューに紐づくコメント
gh api --paginate -F per_page=100 repos/{owner}/{repo}/pulls/{pr_number}/reviews/{review_id}/comments
```

### 解決済みスレッドの取得（GraphQL）

REST APIではスレッドの解決状態（resolved/unresolved）を取得できない。GraphQL APIを使用する。

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

`isResolved: true` のスレッドに属するコメントは収集対象から除外する。

## Bot検出

### CodeRabbit

- `user.login`: `"coderabbitai[bot]"`
- `user.type`: `"Bot"`
- レビューbodyに構造化セクション（Walkthrough、Summary等）を含む

### 他のレビューBot

| Bot | login | 特徴 |
|-----|-------|------|
| CodeRabbit | `coderabbitai[bot]` | Walkthrough + Outside diff range |
| Copilot | `copilot[bot]` | インラインコメント中心 |
| SonarCloud | `sonarcloud[bot]` | 品質ゲート結果 |

Bot由来のコメントも人間のコメントと同じ分類フローに流すが、`source` フィールドでBot名を記録する。

## CodeRabbitレビューbodyの解析

CodeRabbitのレビューbodyには以下の構造化セクションが含まれる。

### 対応が必要なセクション

#### Outside diff range comments

diff範囲外の指摘。インラインコメントとして投稿できないため、レビューbody内に埋め込まれる。

```html
<details>
<summary>⚠️ Outside diff range comments (N)</summary>

**src/config.py:42-45**: Consider adding validation for config values.

**src/utils.py:100**: This function could benefit from memoization.

</details>
```

**抽出手順:**
1. レビューbodyから `⚠️ Outside diff range` を含む `<details>` ブロックを検出
2. ブロック内の `**{filepath}:{line_or_range}**:` パターンを正規表現で抽出
3. 各エントリを通常コメントと同じ分類フローに流す
4. `source: "review_body_outside_diff"` で識別

**抽出正規表現:**
```
\*\*([^*]+?):(\d+(?:-\d+)?)\*\*:\s*(.+?)(?=\n\n\*\*|\n*</details>|\n*$)
```
- グループ1: ファイルパス
- グループ2: 行番号または範囲（例: `42` or `42-45`）
- グループ3: 指摘テキスト（複数行の場合あり）

### 対応不要なセクション（コンテキスト参照のみ）

| セクション | 識別パターン | 用途 |
|-----------|-------------|------|
| Walkthrough | `## Walkthrough` or `📝 Walkthrough` | 変更概要。分類不要 |
| Summary | `## Summary` | PR要約。分類不要 |
| Sequence diagram | ` ```mermaid` | フロー図。分類不要 |
| Review status | `## Review Status` or `✅`/`⚠️`/`❌` ステータス行 | 全体評価。分類不要 |

### CodeRabbitインラインコメントのラベル

CodeRabbitのインラインコメント（通常のReview Comment）にはラベルが付くことがある:

| ラベル | 分類への影響 |
|--------|-------------|
| `🔴 Actionable` | `must` or `should`（内容で判断） |
| `🟡 Nitpick` | `could` |
| ラベルなし | 通常の分類アルゴリズムで判定 |

## 分類カテゴリ

### 優先度別分類

| カテゴリ | 優先度 | キーワード例 | 対応要否 |
|----------|--------|-------------|---------|
| `must` | 1 (最高) | MUST, 必須, マージ前に, ブロッカー, セキュリティ, 脆弱性 | 必須 |
| `question` | 2 | ?, なぜ, どうして, 理由, 意図, 確認 | 回答必須 |
| `should` | 3 | SHOULD, 推奨, できれば, 〜した方が | 推奨 |
| `could` | 4 | COULD, あれば, 可能なら, 検討 | 任意 |
| `note` | 5 (最低) | LGTM, 良い, 参考, FYI, メモ | 不要 |
| `resolved` | - | (解決済みスレッド: GraphQLで検出) | 除外 |

### 分類アルゴリズム

```yaml
classification_rules:
  # 1. 明示的なプレフィックスを優先
  explicit_prefix:
    - pattern: "^(MUST|必須|ブロッカー)"
      category: must
    - pattern: "^(SHOULD|推奨)"
      category: should
    - pattern: "^(COULD|提案)"
      category: could
    - pattern: "^(NOTE|メモ|FYI)"
      category: note

  # 2. 内容からの推論
  content_inference:
    must:
      - "セキュリティ"
      - "脆弱性"
      - "インジェクション"
      - "XSS"
      - "認証"
      - "認可"
      - "データ破壊"
      - "マージ前に"
      - "修正必須"
    question:
      - "?"
      - "？"
      - "なぜ"
      - "どうして"
      - "理由は"
      - "意図は"
      - "確認したい"
    should:
      - "した方が良い"
      - "推奨"
      - "できれば"
      - "改善"
    could:
      - "あれば良い"
      - "検討"
      - "将来的に"
    note:
      - "LGTM"
      - "良いですね"
      - "参考"
      - "FYI"
      - "承認"

  # 3. レビュー状態からの推論
  review_state:
    APPROVED: note
    CHANGES_REQUESTED: must
    COMMENTED: question  # デフォルト
```

## 出力スキーマ

```yaml
comment_analysis:
  pr_ref: "owner/repo#123"
  total_comments: 15

  by_category:
    must: 2
    question: 3
    should: 4
    could: 2
    note: 4

  action_required:
    - id: "comment_123"
      category: must
      author: "@reviewer"
      source: "review_comment"
      body: "SQLインジェクションの可能性があります"
      file: "src/api/users.ts"
      line: 45
      action: "fix_code"

    - id: "comment_456"
      category: question
      author: "@reviewer"
      source: "issue_comment"
      body: "この設計の意図を教えてください"
      file: null
      line: null
      action: "reply_explanation"

    - id: "review_body_outside_diff_1"
      category: should
      author: "coderabbitai[bot]"
      source: "review_body_outside_diff"
      body: "Consider adding validation for config values."
      file: "src/config.py"
      line: "42-45"
      action: "fix_code"
```
