# Git Worktree操作ガイド

git worktreeの詳細な操作方法とベストプラクティス。

## worktreeの基本

### worktreeとは

同じGitリポジトリの複数のブランチを異なるディレクトリで同時に扱える機能。

**通常のブランチ**:
```
作業ディレクトリは1つ
  ↓
git checkout で ブランチ切り替え
  ↓
ファイルが入れ替わる
```

**worktree**:
```
作業ディレクトリが複数
  ↓
各ディレクトリが異なるブランチ
  ↓
同時に複数ブランチで作業可能
```

### worktreeの仕組み

```
.git/ (共有)
  ├── objects/        # すべてのworktreeで共有
  ├── refs/           # すべてのworktreeで共有
  └── worktrees/      # worktree固有の情報
      ├── experiment-1/
      └── experiment-2/

repo/                 # mainブランチ (primary worktree)
  ├── .git/
  └── src/

../repo-experiment-1/ # experiment/feature-1 ブランチ
  ├── .git           # シンボリックリンク
  └── src/

../repo-experiment-2/ # experiment/feature-2 ブランチ
  ├── .git
  └── src/
```

## worktreeの作成

### 基本コマンド

```bash
git worktree add <path> <branch>
```

**例1: 既存ブランチをworktreeに**
```bash
# experiment/refactor ブランチが既に存在
git worktree add ../repo-refactor experiment/refactor
```

**例2: 新しいブランチを作成してworktreeに**
```bash
# -b オプションで新ブランチ作成
git worktree add -b experiment/new-feature ../repo-new-feature main
```

**例3: mainベースの一時worktree**
```bash
# ブランチ名を指定しない（自動生成）
git worktree add ../repo-temp
```

### ディレクトリ配置のベストプラクティス

**Good**: 元のリポジトリの親ディレクトリ
```
workspace/
  ├── myproject/                   # mainブランチ
  ├── myproject-experiment-auth/   # experiment/auth
  └── myproject-experiment-api/    # experiment/api
```

**Bad**: 元のリポジトリの内部
```
myproject/
  ├── src/
  ├── experiment-auth/  # NG: .gitignore が面倒
  └── experiment-api/
```

### 命名規則

**ブランチ命名**:
```
experiment/<feature-name>-<date>

例:
experiment/refactor-auth-20260125
experiment/api-v2-20260125
experiment/db-migration-20260125
```

**ディレクトリ命名**:
```
<repo-name>-experiment-<feature-name>

例:
myproject-experiment-refactor-auth
myproject-experiment-api-v2
```

## worktreeの操作

### worktree一覧表示

```bash
git worktree list
```

**出力例**:
```
/Users/user/workspace/myproject              abc1234 [main]
/Users/user/workspace/myproject-experiment   def5678 [experiment/refactor-auth]
```

### worktree間の移動

```bash
# worktree一覧確認
git worktree list

# 目的のディレクトリに移動
cd ../myproject-experiment

# 現在のブランチ確認
git branch --show-current
```

### worktree内での作業

worktree内では通常のgit操作がすべて可能:

```bash
# 変更を加える
vim src/auth/jwt.ts

# ステージング
git add src/auth/jwt.ts

# コミット
git commit -m "Refactor JWT generation"

# プッシュ（必要に応じて）
git push origin experiment/refactor-auth
```

### worktreeの削除

**方法1: 通常の削除**
```bash
# 元のリポジトリに戻る
cd ../myproject

# worktree削除
git worktree remove ../myproject-experiment
```

**方法2: 強制削除（変更が残っていても削除）**
```bash
git worktree remove --force ../myproject-experiment
```

**方法3: 手動削除後のクリーンアップ**
```bash
# ディレクトリを手動削除してしまった場合
rm -rf ../myproject-experiment

# worktree情報をクリーンアップ
git worktree prune
```

### ブランチの削除

worktree削除後、ブランチも不要なら削除:

```bash
# ローカルブランチ削除
git branch -d experiment/refactor-auth

# マージ済みでない場合は強制削除
git branch -D experiment/refactor-auth

# リモートブランチ削除
git push origin --delete experiment/refactor-auth
```

## worktree間でのデータ共有

### コミットの共有

すべてのworktreeは同じ.git/objects/を共有するため、コミットは自動的に共有される。

```bash
# worktree-1 でコミット
cd ../myproject-experiment-1
git commit -m "Add feature A"

# worktree-2 で即座に参照可能
cd ../myproject-experiment-2
git log experiment/feature-1  # コミットが見える
```

### ブランチのマージ

worktree間でブランチをマージ:

```bash
# mainブランチ（primary worktree）に戻る
cd ../myproject

# experiment/feature-1 をマージ
git merge experiment/feature-1
```

### cherry-pickでの部分取り込み

```bash
# mainブランチで作業
cd ../myproject

# experiment/feature-1 の特定コミットだけを取り込む
git cherry-pick abc1234
```

## トラブルシューティング

### worktreeが削除できない

**症状**: `fatal: 'xxx' is a main working tree`

**原因**: primary worktree（最初のworktree）は削除不可

**対策**: secondary worktreeのみ削除可能

---

**症状**: `fatal: 'xxx' contains modified or untracked files`

**原因**: worktree内に変更が残っている

**対策**:
```bash
# 変更を確認
cd ../myproject-experiment
git status

# 変更を保存したい場合
git stash

# または変更を破棄
git reset --hard HEAD
git clean -fd

# worktree削除
cd ../myproject
git worktree remove ../myproject-experiment
```

### ディレクトリを手動削除してしまった

**症状**: worktreeディレクトリを`rm -rf`で削除してしまった

**対策**:
```bash
# worktree情報をクリーンアップ
git worktree prune

# 確認
git worktree list
```

### .gitがシンボリックリンクになっている

**症状**: worktree内の`.git`がファイルになっている

**説明**: これは正常な動作。worktreeでは`.git`はファイルで、以下の内容:
```
gitdir: /path/to/repo/.git/worktrees/xxx
```

**対策**: 問題なし。正常な動作。

### ディスク容量不足

**症状**: worktreeを作成したらディスク容量が不足

**原因**: worktreeは物理的に別ディレクトリを作成するため、大規模リポジトリでは容量を消費

**対策**:
```bash
# 不要なworktreeを即座に削除
git worktree list
git worktree remove ../myproject-experiment-old

# node_modules等を除外
echo "node_modules/" >> .git/info/exclude

# ビルド成果物を除外
echo "dist/" >> .git/info/exclude
```

## ベストプラクティス

### 1. worktree名は明確に

**Good**:
```
myproject-experiment-refactor-auth
myproject-experiment-api-v2
```

**Bad**:
```
test1
tmp
experiment
```

### 2. 使い終わったら即座に削除

worktreeは一時的な作業環境として使用し、完了後は即座に削除:

```bash
# 実験完了後
cd ../myproject
git worktree remove ../myproject-experiment
git branch -d experiment/feature-1
```

### 3. worktree一覧を定期的に確認

```bash
# 不要なworktreeがないか確認
git worktree list

# 古いworktreeを削除
git worktree prune
```

### 4. ブランチ名とディレクトリ名を対応させる

```bash
# ブランチ: experiment/refactor-auth
# ディレクトリ: myproject-experiment-refactor-auth
git worktree add ../myproject-experiment-refactor-auth experiment/refactor-auth
```

### 5. mainブランチはprimary worktreeで

primary worktree（最初のworktree）は通常mainブランチにしておく:

```
myproject/                      # primary worktree (main)
myproject-experiment-*/         # secondary worktrees (experiments)
```

## 高度な使用例

### 並行レビュー

複数のPRを同時にレビュー:

```bash
# PR #123 をレビュー
git worktree add ../myproject-pr-123 pr/123
cd ../myproject-pr-123
npm test

# PR #124 を並行してレビュー
cd ../myproject
git worktree add ../myproject-pr-124 pr/124
cd ../myproject-pr-124
npm test

# 元の作業に戻る
cd ../myproject
```

### ホットフィックスと機能開発の並行作業

```bash
# 機能開発中
cd ../myproject
git checkout feature/new-ui

# 緊急バグ発見
git worktree add ../myproject-hotfix main
cd ../myproject-hotfix
git checkout -b hotfix/critical-bug

# バグ修正（機能開発を中断せずに）
vim src/payment/processor.ts
git commit -m "Fix critical payment bug"

# mainにマージ
git checkout main
git merge hotfix/critical-bug
git push

# 機能開発に戻る
cd ../myproject
# feature/new-ui がそのまま残っている
```

### ビルド成果物の比較

```bash
# 現在の実装
cd ../myproject
npm run build
ls -lh dist/

# 新しい実装
cd ../myproject-experiment
npm run build
ls -lh dist/

# バンドルサイズを比較
du -sh dist/
```

## まとめ

### worktreeを使うべき時

- [ ] 高リスクな変更（リファクタリング、アーキテクチャ変更）
- [ ] 複数の実験的変更を並行して試したい
- [ ] PRレビューを並行して行いたい
- [ ] ホットフィックスと機能開発を並行したい

### worktree使用のメリット

1. **安全性**: mainブランチを汚さない
2. **並行作業**: 複数ブランチで同時作業
3. **高速切り替え**: ブランチ切り替え不要
4. **実験の自由度**: 失敗を恐れずに試せる

### worktree使用の注意点

1. **ディスク容量**: 物理的に別ディレクトリが作成される
2. **削除忘れ**: 使い終わったら即座に削除
3. **混乱回避**: 明確な命名規則を守る
