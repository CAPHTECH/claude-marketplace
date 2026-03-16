# 返信テンプレート

## 対応完了時の返信

### コード修正完了

```markdown
修正しました。 ✅

{修正内容の簡潔な説明}

commit: {commit_sha}
```

### 質問への回答

```markdown
{回答内容}

---
ご確認よろしくお願いします。
```

### 提案の採用

```markdown
ご提案ありがとうございます。採用しました。 ✅

{採用した内容の説明}

commit: {commit_sha}
```

### 提案の見送り

```markdown
ご提案ありがとうございます。

今回は以下の理由で見送りとさせてください：
- {理由1}
- {理由2}

{代替案があれば記載}
```

### 確認依頼

```markdown
ご指摘ありがとうございます。

{対応内容の説明}

お手数ですが、再度ご確認いただけますでしょうか。
```

### Outside diff range 指摘への一括対応報告

レビューbodyに埋め込まれたoutside diff rangeコメントへの返信用。
`gh pr review {pr_number} --comment` で投稿する。

```markdown
## Outside diff range 指摘への対応

| ファイル | 指摘 | 対応 | commit |
|---------|------|------|--------|
| {filepath}:{line} | {指摘の要約} | {修正済み/見送り} | {commit_sha or -} |

{見送りがある場合、理由を記載}
```

## gh CLIでの返信コマンド

### 一般コメントへの返信

```bash
gh pr comment {pr_number} --body "返信内容"
```

### レビューコメントへの返信（スレッド）

```bash
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies \
  -f body="返信内容"
```

### レビュー全体への返信

```bash
gh pr review {pr_number} --comment --body "返信内容"
```

## 返信のベストプラクティス

1. **簡潔に**: 長文は避け、要点を明確に
2. **根拠を示す**: 修正理由や設計意図を説明
3. **コミット参照**: 修正した場合はコミットSHAを記載
4. **感謝を伝える**: 指摘への感謝を忘れずに
5. **確認依頼**: 重要な修正後は再確認を依頼
