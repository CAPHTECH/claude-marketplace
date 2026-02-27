# PRコメント分類ルール

## コメント種別

### 取得対象

| 種別 | gh APIエンドポイント | 説明 |
|------|---------------------|------|
| Issue Comment | `repos/{owner}/{repo}/issues/{pr}/comments` | PR全体への一般コメント |
| Review Comment | `repos/{owner}/{repo}/pulls/{pr}/comments` | コード行へのインラインコメント |
| Review | `repos/{owner}/{repo}/pulls/{pr}/reviews` | レビュー本体（APPROVE/REQUEST_CHANGES等） |

### 取得コマンド

```bash
# 一般コメント
gh api repos/{owner}/{repo}/issues/{pr_number}/comments

# レビューコメント（インライン）
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments

# レビュー本体
gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews

# レビューに紐づくコメント
gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews/{review_id}/comments
```

## 分類カテゴリ

### 優先度別分類

| カテゴリ | 優先度 | キーワード例 | 対応要否 |
|----------|--------|-------------|---------|
| `must` | 1 (最高) | MUST, 必須, マージ前に, ブロッカー, セキュリティ, 脆弱性 | 必須 |
| `question` | 2 | ?, なぜ, どうして, 理由, 意図, 確認 | 回答必須 |
| `should` | 3 | SHOULD, 推奨, できれば, 〜した方が | 推奨 |
| `could` | 4 | COULD, あれば, 可能なら, 検討 | 任意 |
| `note` | 5 (最低) | LGTM, 良い, 参考, FYI, メモ | 不要 |
| `resolved` | - | (解決済みスレッド) | 不要 |

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
      body: "SQLインジェクションの可能性があります"
      file: "src/api/users.ts"
      line: 45
      action: "fix_code"

    - id: "comment_456"
      category: question
      author: "@reviewer"
      body: "この設計の意図を教えてください"
      file: null
      line: null
      action: "reply_explanation"
```
