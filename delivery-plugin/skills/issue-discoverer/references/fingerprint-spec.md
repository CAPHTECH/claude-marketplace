# Fingerprint Spec（重複検出ハッシュ仕様）

Issue候補の重複検出に使用する fingerprint の生成・照合仕様。

## 目的

同じ問題に対するIssueの重複起票を防止する。
fingerprint はIssue body にHTMLコメントとして埋め込まれ、
既存Issueとの照合に使用される。

## 生成手順

### Step 1: title_keywords の正規化

タイトルから意味のあるキーワードを抽出し、正規化する。

1. Unicode NFC 正規化を適用
2. ASCII 小文字化（日本語はそのまま保持）
3. ストップワードを除去（a, an, the, in, on, at, to, for, of, is, are, be）
4. ASCII 記号・句読点を除去（`[^a-z0-9]` にマッチするASCII文字を空白に置換。日本語文字はトークンとしてそのまま保持）
5. 空白で分割し、重複を除去
6. アルファベット順でソート

**例:**
```
タイトル: "Fix SQL injection in UserController.login()"
正規化後: ["fix", "injection", "login", "sql", "usercontroller"]
```

### Step 2: ハッシュ生成

以下のフォーマットで入力文字列を構築し、SHA-256ハッシュの先頭12文字（48bit）を取得する。

`primary_file` はリポジトリルートからの相対パス（先頭の `./` は除去、パス区切りは `/`）に正規化する。

```
input = category + ":" + sorted(title_keywords).join(",") + ":" + primary_file
fingerprint = sha256(input)[:12]
```

**例:**
```
input = "security:fix,injection,login,sql,usercontroller:src/controllers/UserController.ts"
fingerprint = "a3f2b1c84e91"
```

### Step 3: Issue body への埋め込み

Issue body の末尾にHTMLコメントとして埋め込む:

```markdown
<!-- fingerprint: a3f2b1c84e91 -->
```

この形式は GitHub のIssue表示では不可視だが、API経由で取得可能。

## 照合ルール

### 完全一致（fingerprint match）

```bash
gh issue list --repo <repo> --state open --limit 100 --json number,title,body
```

取得した各Issueのbodyから `<!-- fingerprint: XXXXXXXXXXXX -->` パターンを抽出し、
新規候補の fingerprint と比較する。完全一致があれば重複と判定。

**注意**: 100件を超えるオープンIssueがあるリポジトリでは `--limit 500` 等に増やして
照合範囲を広げる。ラベルによる絞り込みは手動起票Issueとの重複を見落とすため非推奨。

### タイトル類似度（fallback）

fingerprint が一致しない場合、タイトルの単語レベルJaccard類似度で判定する。

```
similarity = |title_keywords_A ∩ title_keywords_B| / |title_keywords_A ∪ title_keywords_B|
```

類似度が 70% 以上の場合、重複候補としてユーザーに確認を求める
（自動的にスキップはしない）。

## 限界

1. **primary_file のリネーム**: ファイルが移動・リネームされると fingerprint が変わり、重複検出できない
2. **タイトル表現の揺れ**: 同じ問題を大きく異なるタイトルで記述した場合、fingerprint もタイトル類似度も一致しない可能性がある
3. **100件制限**: `gh issue list` のデフォルト取得件数。大量のオープンIssueがあるリポジトリでは取りこぼす可能性がある
4. **クローズ済みIssue**: デフォルトではオープンIssueのみ照合する。再発防止には `--state all` の使用を検討する
