---
name: main-merge-resolver
description: 現在の作業ブランチへ既定でmainを取り込み、必要ならコンフリクト解消まで進める。mainの取り込み、最新mainの反映、merge main、コンフリクト解消、resolve merge conflicts を依頼された時に使用する。
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "[base-branch]"
---

# Main Merge Resolver

現在の作業ブランチに既定で `main` を取り込み、必要なら安全にコンフリクトを解消する。

## ワークフロー

```
1. Preconditions
2. Resolve Merge Source
3. Merge
4. Resolve Conflicts or Escalate
5. Complete Merge
6. Validate & Report
7. Ask Before Push
```

## Step 1: Preconditions

最初に以下を確認する。

1. Git リポジトリ内で実行していること
2. 現在ブランチ名を取得できること
3. ベースブランチ名を決めること
   - 引数あり: その値を使う
   - 引数なし: `main`
4. 現在ブランチがベースブランチ自身ではないこと

```bash
git rev-parse --is-inside-work-tree
git branch --show-current
git status --porcelain
```

### dirty working tree

`git status --porcelain` が空でない場合は、マージを実行せずに止まる。

ユーザーに以下を簡潔に伝えて確認する:

- 未コミット変更があること
- そのままマージすると競合判断が難しくなること
- 先に commit / stash / discard のどれで進めるか確認が必要なこと

## Step 2: Resolve Merge Source

既定の取り込み元は `main`。引数があればそのブランチを使う。

### 優先順位

1. `origin` remote があり、`git fetch origin <base>` が成功したら `origin/<base>` を使う
2. `origin` remote が無く、ローカル `<base>` があるならそれを使う
3. `origin` remote はあるが fetch 失敗時は自動で続行せず、ユーザーに確認する
4. どちらも無ければユーザーに確認する

```bash
git remote get-url origin
git fetch origin "<base>"
git show-ref --verify --quiet "refs/remotes/origin/<base>"
git show-ref --verify --quiet "refs/heads/<base>"
```

### ルール

- `origin` remote がある場合は、`git fetch origin <base>` の成功を確認してから `origin/<base>` をマージ対象にする
- `origin` remote があるのに fetch が失敗した場合は、古い `origin/<base>` をそのまま使わない
- fetch 失敗時は、認証・ネットワーク・権限エラーの可能性を伝えて、再試行するかローカル `<base>` を使うかをユーザーに確認する
- `origin` remote が無い場合に限り、ローカル `<base>` があればそれを使う
- ベースブランチが見つからない場合は推測で作らず、ユーザーに確認する

## Step 3: Merge

マージ対象が決まったら通常の merge を実行する。

```bash
git merge --no-ff "<merge_source>"
```

### 成功時

- マージ結果を要約する
- 競合なしで完了したことを明示する
- 可能なら軽量検証へ進む

### 競合時

競合発生後は以下を収集する。

```bash
git status --short
git diff --name-only --diff-filter=U
git diff --ours -- <file>
git diff --theirs -- <file>
```

- 競合ファイル一覧
- どの種類の差分か
- 自動解消してよいかどうか

## Step 4: Resolve Conflicts or Escalate

### 自動解消してよいケース

意図が明白な機械的統合のみ自動で進める。

- import / export の単純併合
- 互いに独立した追記の共存
- コメントや並び順の明白な統合
- 同じ意味の重複宣言を片側へ整理するだけの解消

### 必ずユーザー確認するケース

次に該当したら、自動解消せず質問する。

- 同じロジックに対する異なる実装方針
- 仕様判断が必要な条件分岐、戻り値、例外処理
- lockfile、生成物、マイグレーション、設定ファイル、依存バージョンの競合
- 削除 vs 変更
- rename が絡む競合
- テスト期待値と実装変更のどちらを優先すべきか不明
- どちらの side を採るかで動作が変わるもの

### ユーザー確認時の出力

以下を短くまとめて質問する。

- 何が競合しているか
- 有力な解消案
- 推奨案

例:

```text
config/app.yml で設定値の競合があります。
- ours: feature 用の timeout=10
- theirs: main 側の timeout=30 と retry 設定追加
推奨: main 側の retry を残しつつ timeout の採用方針を確認
どちらを基準に解消しますか？
```

## Step 5: Complete Merge

競合解消後は、解消したファイルだけを stage してマージを完了する。

```bash
git add <resolved-file-1> <resolved-file-2>
git commit --no-edit
```

### ガードレール

- `git add -A` を使わない
- `git add .` を使わない
- 競合に関係ないファイルをまとめて stage しない
- merge commit が自動作成済みなら追加 commit を作らない
- 対話エディタ待ちになる `git commit` 単独実行を避ける

## Step 6: Validate & Report

### 検証

プロジェクト内から明確な検証コマンドがすぐ分かる場合だけ、軽量チェックを実行する。

例:

- 既知の lint / test / typecheck コマンド
- 変更範囲に対して短時間で終わる確認

明確なコマンドが即座に判別できない場合は、無理に推測実行しない。

### 完了報告

最後に以下を簡潔にまとめる。

- ベースブランチ
- 使用した merge source
- 競合の有無
- 解消したファイルと要点
- 実施した検証、または未検証であること
- 現在の状態が push 待ちかどうか

## Step 7: Ask Before Push

このスキルは `git push` を自動では実行しない。

push が必要な場合は、マージ完了後に必ずユーザーへ確認する。

例:

```text
ローカルでマージは完了しています。必要ならこの後 push できます。push しますか？
```

## 絶対に避ける操作

- `git reset --hard`
- `git checkout -- .`
- `git checkout -- <file>` を安易な競合解消に使う
- 無差別ステージング
- 不明点があるままの見切り発車での競合解消

## 使用例

```text
User: main をマージして

Claude:
1. 現在ブランチと working tree を確認
2. `origin/main` を fetch して merge source に採用
3. `git merge --no-ff origin/main` を実行
4. 競合なしなら結果を要約
5. push 前で停止し、必要なら確認する
```

```text
User: latest main を反映して、競合も見て

Claude:
1. `main` を既定ベースとして解決
2. 競合発生時はファイルごとの差分を確認
3. import の単純併合は自動解消
4. 仕様判断が必要な競合はユーザーへ質問
5. ローカルマージ完了後、push は確認待ちで止める
```
