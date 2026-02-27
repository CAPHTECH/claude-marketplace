# マージ戦略ガイド

worktree実験成功後のマージ戦略（Cherry-pick/Rebase/Merge）の詳細ガイド。

## マージ戦略の選択

実験成功後、以下の基準でマージ戦略を選択:

```
成功の度合い           マージ戦略
────────────────────────────────────
一部のコミットのみ → Cherry-pick（部分採用）
全体だが整理したい → Rebase（整形してマージ）
全体そのまま       → Merge（全体採用）
```

## Strategy 1: Cherry-pick（部分採用）

### 用途

実験の一部のコミットだけを採用したい場合。

**例**:
- 実験中に5つのコミットを作成
- そのうち2つだけが成功
- 残り3つは失敗または不要

### 手順

```bash
# 1. worktree内でコミット履歴を確認
cd ../myproject-experiment
git log --oneline

# 出力例:
# abc1234 Add feature C (失敗)
# def5678 Add feature B (成功) ← これを採用
# ghi9012 Add feature A (成功) ← これを採用
# jkl3456 Initial experiment

# 2. 元のリポジトリ（mainブランチ）に戻る
cd ../myproject
git checkout main

# 3. 成功したコミットだけをcherry-pick
git cherry-pick ghi9012  # feature A
git cherry-pick def5678  # feature B

# 4. テスト実行で確認
npm test

# 5. プッシュ
git push origin main
```

### コンフリクト解決

cherry-pick中にコンフリクトが発生した場合:

```bash
# コンフリクト発生
git cherry-pick abc1234
# CONFLICT (content): Merge conflict in src/auth.ts

# 1. コンフリクトを手動解決
vim src/auth.ts

# 2. 解決後、ステージング
git add src/auth.ts

# 3. cherry-pick続行
git cherry-pick --continue

# または中止
git cherry-pick --abort
```

### 複数コミットの一括cherry-pick

```bash
# 範囲指定でcherry-pick
git cherry-pick abc1234..def5678

# または個別に列挙
git cherry-pick abc1234 def5678 ghi9012
```

### Cherry-pickのメリット・デメリット

**メリット**:
- 成功した変更だけを選択的に取り込める
- 失敗した変更は残さない
- 柔軟性が高い

**デメリット**:
- コミット履歴が重複する（元のコミットと新しいコミット）
- コンフリクト解決が必要な場合がある
- 手動で選択する必要がある

## Strategy 2: Rebase（整形してマージ）

### 用途

実験全体は成功したが、コミット履歴を整理してからマージしたい場合。

**例**:
- 実験中に10個の細かいコミットを作成
- すべて成功したが、履歴が汚い
- 3-4個の意味のあるコミットに整理したい

### 手順

```bash
# 1. worktree内でrebaseによる履歴整理
cd ../myproject-experiment
git checkout experiment/refactor-auth

# 2. インタラクティブrebaseで整理
git rebase -i main

# エディタが開く:
# pick abc1234 Add JWT type
# squash def5678 Fix typo in JWT
# squash ghi9012 Add JWT test
# pick jkl3456 Add token verification
# squash mno7890 Fix token verification bug
# ...

# 3. コミットメッセージを編集
# 4. rebase完了

# 5. 元のリポジトリに戻る
cd ../myproject
git checkout main

# 6. fast-forwardマージ
git merge --ff-only experiment/refactor-auth

# 7. プッシュ
git push origin main
```

### Rebaseのオプション

**インタラクティブrebase**:
```bash
git rebase -i main
```

**エディタで使えるコマンド**:
```
pick   : コミットをそのまま使う
reword : コミットメッセージを変更
edit   : コミットを編集
squash : 前のコミットに統合（メッセージは両方残す）
fixup  : 前のコミットに統合（メッセージは捨てる）
drop   : コミットを削除
```

### コンフリクト解決

rebase中にコンフリクトが発生した場合:

```bash
# コンフリクト発生
git rebase -i main
# CONFLICT (content): Merge conflict in src/auth.ts

# 1. コンフリクトを手動解決
vim src/auth.ts

# 2. 解決後、ステージング
git add src/auth.ts

# 3. rebase続行
git rebase --continue

# または中止
git rebase --abort
```

### Rebaseのメリット・デメリット

**メリット**:
- 綺麗なコミット履歴
- fast-forwardマージで履歴が一直線
- レビューしやすい

**デメリット**:
- rebaseは履歴を書き換える（共有ブランチでは注意）
- コンフリクト解決が複数回必要な場合がある
- インタラクティブrebaseの操作が必要

## Strategy 3: Merge（全体採用）

### 用途

実験全体が成功し、そのままマージしたい場合。

**例**:
- すべての変更が成功
- コミット履歴もそのままで問題ない
- 最も簡単な方法

### 手順

```bash
# 1. 元のリポジトリ（mainブランチ）に戻る
cd ../myproject
git checkout main

# 2. experiment ブランチをマージ
git merge experiment/refactor-auth

# 3. マージコミットが作成される
# （または fast-forward）

# 4. プッシュ
git push origin main
```

### マージのオプション

**通常のマージ（マージコミット作成）**:
```bash
git merge experiment/refactor-auth
```

**fast-forwardマージ（マージコミットなし）**:
```bash
git merge --ff-only experiment/refactor-auth
```

**squashマージ（1つのコミットに統合）**:
```bash
git merge --squash experiment/refactor-auth
git commit -m "Refactor authentication system"
```

### コンフリクト解決

merge中にコンフリクトが発生した場合:

```bash
# コンフリクト発生
git merge experiment/refactor-auth
# CONFLICT (content): Merge conflict in src/auth.ts

# 1. コンフリクトを手動解決
vim src/auth.ts

# 2. 解決後、ステージング
git add src/auth.ts

# 3. マージ完了
git commit

# または中止
git merge --abort
```

### Mergeのメリット・デメリット

**メリット**:
- 最も簡単
- 元の履歴がそのまま残る
- マージコミットで履歴が明確

**デメリット**:
- コミット履歴が複雑になる場合がある
- マージコミットが増える

## マージ戦略の比較表

| 戦略 | 用途 | 履歴 | 難易度 | 推奨度 |
|------|------|------|--------|--------|
| **Cherry-pick** | 一部採用 | 重複あり | 中 | 部分成功時 |
| **Rebase** | 整形してマージ | 綺麗 | 高 | 全体成功、履歴重視 |
| **Merge** | 全体採用 | 複雑化 | 低 | 全体成功、簡単に |

## 実践例

### 例1: 部分成功（Cherry-pick）

```bash
# 実験結果
# - feature A: 成功 (abc1234)
# - feature B: 成功 (def5678)
# - feature C: 失敗 (ghi9012)

cd ../myproject
git checkout main
git cherry-pick abc1234 def5678
npm test
git push
```

### 例2: 全体成功だがコミットが汚い（Rebase）

```bash
# 実験結果: 10個の細かいコミット
# → 3個の意味のあるコミットに整理

cd ../myproject-experiment
git rebase -i main
# (エディタでsquash/fixup)

cd ../myproject
git checkout main
git merge --ff-only experiment/refactor-auth
git push
```

### 例3: 全体成功（Merge）

```bash
# 実験結果: すべて成功、履歴も綺麗

cd ../myproject
git checkout main
git merge experiment/refactor-auth
git push
```

## マージ後のクリーンアップ

### worktreeとブランチの削除

```bash
# 1. worktree削除
git worktree remove ../myproject-experiment

# 2. ローカルブランチ削除
git branch -d experiment/refactor-auth

# 3. リモートブランチ削除（プッシュしていた場合）
git push origin --delete experiment/refactor-auth
```

### マージ失敗時のロールバック

```bash
# マージ中止
git merge --abort

# または、マージ後に取り消し
git reset --hard ORIG_HEAD
```

## トラブルシューティング

### cherry-pickが失敗する

**症状**: `error: could not apply abc1234...`

**原因**: コンフリクトまたは依存関係の問題

**対策**:
```bash
# 依存するコミットも一緒にcherry-pick
git cherry-pick abc1234 def5678

# またはrebaseを使用
```

### rebase中に迷子になった

**症状**: rebaseの途中でどこにいるか分からない

**対策**:
```bash
# 現在の状態確認
git status

# rebase中止
git rebase --abort

# 最初からやり直し
```

### マージ後にバグ発見

**症状**: マージ後にバグが見つかった

**対策**:
```bash
# 直近のマージを取り消し
git reset --hard HEAD~1

# または特定のコミットまで戻る
git reset --hard <commit-hash>
```

## ベストプラクティス

### 1. マージ前にテスト実行

```bash
# cherry-pick後
git cherry-pick abc1234
npm test  # ← 必須

# merge前
git merge experiment/refactor-auth
npm test  # ← 必須
```

### 2. 小さく頻繁にマージ

```bash
# Good: 成功した部分から順次マージ
git cherry-pick abc1234
npm test
git push

git cherry-pick def5678
npm test
git push

# Bad: すべて完了してから一度にマージ
```

### 3. マージコミットメッセージを明確に

```bash
# Good
git merge experiment/refactor-auth -m "Merge: Refactor authentication system

- Migrate from Basic Auth to JWT
- Add token refresh mechanism
- Improve session management

Related: #123"

# Bad
git merge experiment/refactor-auth
# (デフォルトメッセージのまま)
```

### 4. コンフリクトは慎重に解決

```bash
# コンフリクト発生時
git status  # 影響範囲を確認
git diff    # 差分を確認
vim <file>  # 慎重に解決
npm test    # 必ずテスト
```

## まとめ

### マージ戦略の選択フロー

```
実験成功？
  ├── No → worktree削除、元に戻る
  └── Yes
      ├── 一部のみ成功？
      │   └── Yes → Cherry-pick
      └── 全体成功
          ├── 履歴を整理したい？
          │   └── Yes → Rebase
          └── No → Merge
```

### 核心原則

1. **テストファースト**: マージ前に必ずテスト
2. **小さく頻繁に**: 成功した部分から順次マージ
3. **明確なメッセージ**: マージの意図を明記
4. **慎重なコンフリクト解決**: 影響範囲を確認
