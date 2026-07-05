---
name: eld-change-worktree
context: fork
description: 高リスク変更時にgit worktreeで隔離環境を作成するスキル。eld-predict-lightでMedium以上と判定された変更に安全な実験環境を提供する。「worktreeで隔離して」「安全な環境で試して」「実験的に変更して」「失敗しても大丈夫なように」等で使用。大規模リファクタリングやアーキテクチャ変更時にも使う。
---

# ELD Change: Worktree

## ゲート

`/eld-predict-light` の判定でリスク **Medium以上（P1以上）** の変更は、git worktreeで隔離環境を作成してから実施する。Low（P0）はworktree不要、通常のブランチで直接実行する。

## 手順

1. ブランチ命名: `experiment/<feature-name>-<yyyymmdd>`（例: `experiment/refactor-auth-20260125`）
2. worktree作成:
   ```bash
   git branch experiment/<name>-<date>
   git worktree add ../repo-experiment-<name> experiment/<name>-<date>
   cd ../repo-experiment-<name>
   ```
3. 隔離環境で変更・テストを実施する。mainブランチは一切変更されない。
4. 成功したら `git merge experiment/<name>-<date>`（または必要な差分のみ cherry-pick）でマージする。

## クリーンアップ

```bash
cd ../repo && git worktree remove ../repo-experiment-<name> && git branch -d experiment/<name>-<date>
```
