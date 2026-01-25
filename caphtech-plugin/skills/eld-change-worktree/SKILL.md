---
name: eld-change-worktree
description: |
  高リスク変更時にgit worktreeで隔離環境を作成。
  eld-predict-impactでHigh/Critical判定された変更に対して安全な実験環境を提供。

  トリガー条件:
  - 「worktreeで隔離して」「安全な環境で試して」「実験的に変更して」
  - eld-predict-impactでHigh/Critical判定時の自動提案
  - 大規模リファクタリング、アーキテクチャ変更時
  - 「失敗しても大丈夫なように」
---

# ELD Change: Worktree

高リスク変更時にgit worktreeで隔離環境を作成し、安全な実験を可能にする。

## 核心原則

1. **隔離実験**: mainブランチを汚さずに変更を試せる
2. **リスク判定連携**: `/eld-predict-impact` の出力からリスクレベルを判定
3. **段階的統合**: 成功した変更のみをマージ
4. **自動クリーンアップ**: 実験終了後のworktree削除

## worktreeとは

Git worktreeは、同じリポジトリの複数のブランチを異なるディレクトリで同時に扱える機能。

**通常のブランチ切り替え**:
```
repo/
  ├── src/
  └── tests/

git checkout feature-branch  # 同じディレクトリ内でブランチ切り替え
```

**worktree使用時**:
```
repo/                    # main ブランチ
  ├── src/
  └── tests/

../repo-experiment/      # 隔離された実験環境（別ブランチ）
  ├── src/
  └── tests/
```

## 実行フロー

### Phase 1: リスクレベル判定

`/eld-predict-impact` の出力またはユーザー指定からリスクレベルを判定。

**リスクレベル分類**:
```yaml
Low:
  - 単一ファイルの小変更
  - 新規ファイル追加
  → worktree不要、通常のブランチで実行

Medium:
  - 複数ファイルの変更
  - 既存機能の拡張
  → worktree推奨

High:
  - API変更、インターフェース変更
  - 複数モジュールにまたがる変更
  → worktree必須

Critical:
  - アーキテクチャ変更
  - データ構造変更
  - 破壊的変更
  → worktree必須 + 追加の安全措置
```

詳細は `references/risk-assessment.md` を参照。

### Phase 2: worktree環境作成

リスクレベルがMedium以上の場合、worktree環境を作成。

**ブランチ命名規則**:
```
experiment/<feature-name>-<yyyymmdd>

例:
experiment/refactor-auth-20260125
experiment/api-breaking-change-20260125
```

**ディレクトリ配置**:
```
元のリポジトリの親ディレクトリ:
  repo/                           # mainブランチ（変更しない）
  repo-experiment-<feature>/      # 実験環境
```

**作成コマンド**:
```bash
# 1. ブランチ作成（まだ作成していない場合）
git branch experiment/refactor-auth-20260125

# 2. worktree追加
git worktree add ../repo-experiment-refactor-auth experiment/refactor-auth-20260125

# 3. 実験環境に移動
cd ../repo-experiment-refactor-auth
```

### Phase 3: 実験的変更の実行

隔離環境で自由に変更を試す。

**実験中のルール**:
```yaml
自由に変更可能:
  - コード変更
  - テスト追加
  - リファクタリング
  - 破壊的変更

安全網:
  - 元のリポジトリ（mainブランチ）は一切変更されない
  - いつでもworktreeを削除して元に戻せる
  - 並行して元のリポジトリで別作業も可能
```

**検証ステップ**:
```bash
# テスト実行
npm test

# ビルド確認
npm run build

# Evidence L1以上の検証
# TDD Enforcerによる検証
```

### Phase 4: 成功判定とマージ戦略選択

実験が成功した場合、マージ戦略を選択。

**マージ戦略**:
```yaml
Strategy 1: Cherry-pick（部分採用）
  用途: 一部のコミットのみを採用
  手順:
    1. 元のリポジトリに戻る
    2. git cherry-pick <commit-hash>
  例: 成功した変更の一部だけを取り込む

Strategy 2: Rebase（整形してマージ）
  用途: コミット履歴を整理してマージ
  手順:
    1. experiment ブランチを rebase
    2. git merge --ff-only experiment/xxx
  例: コミット履歴を綺麗にしたい場合

Strategy 3: Merge（全体採用）
  用途: すべての変更を取り込む
  手順:
    1. git merge experiment/xxx
  例: すべての変更が成功した場合
```

詳細は `references/merge-strategies.md` を参照。

### Phase 5: クリーンアップ

マージ完了後、worktreeとブランチを削除。

```bash
# 1. 元のリポジトリに戻る
cd ../repo

# 2. worktree削除
git worktree remove ../repo-experiment-refactor-auth

# 3. ブランチ削除（必要に応じて）
git branch -d experiment/refactor-auth-20260125

# 4. ディレクトリ確認
git worktree list  # worktreeが削除されたことを確認
```

## 統合例

### 例1: eld-predict-impactとの連携

```
User: APIのインターフェースを変更したい

Claude:
## Phase 1: Impact Prediction

/eld-predict-impact を実行します。

[Impact Analysis結果]
  Risk Level: High
  Affected: 15 files, 3 modules
  Causal Type: Interface Change

## Phase 2: Worktree提案

リスクレベルがHighのため、worktreeでの隔離実験を推奨します。

作業手順:
1. worktree環境作成: `experiment/api-change-20260125`
2. 隔離環境で変更実施
3. テスト実行で検証
4. 成功時にマージ戦略選択

worktree環境を作成しますか？
```

### 例2: 大規模リファクタリング

```
User: 認証システム全体をリファクタリングして

Claude:
## リスク判定

認証システムの全体リファクタリングは Critical レベルです。
worktree での隔離実験が必須です。

## worktree環境作成

[worktree作成コマンド実行]

## 段階的リファクタリング

隔離環境で以下を順次実施:
1. 型定義のリファクタリング（Evidence L0）
2. コアロジックのリファクタリング（Evidence L1）
3. API層のリファクタリング（Evidence L2）
4. 統合テストで検証

各ステップで検証を行い、失敗時はロールバック可能。
```

## worktree使用の判断基準

### worktreeを使うべき条件

- [ ] リスクレベルがMedium以上
- [ ] 複数ファイルにまたがる変更
- [ ] 破壊的変更の可能性
- [ ] ロールバックが頻繁に必要
- [ ] 並行して別作業を継続したい

### worktree不要な条件

- [ ] リスクレベルがLow
- [ ] 単一ファイルの小変更
- [ ] 新規ファイル追加のみ
- [ ] 確実に成功する変更

## worktreeのメリット

1. **安全性**: mainブランチを一切変更しない
2. **並行作業**: 元のリポジトリで別作業も可能
3. **高速ロールバック**: worktree削除で即座に元に戻る
4. **実験の自由度**: 失敗を恐れずに試せる
5. **段階的統合**: 成功した部分だけをマージ

## トラブルシューティング

### worktreeが削除できない

```bash
# 強制削除
git worktree remove --force ../repo-experiment-xxx

# または手動削除
rm -rf ../repo-experiment-xxx
git worktree prune
```

### ディスク容量不足

worktreeは物理的に別ディレクトリを作成するため、大規模リポジトリでは容量に注意。

**対策**:
- 不要なworktreeは即座に削除
- git worktree list で一覧確認
- 一時的にnode_modules等を.gitignore

## リファレンス

- `references/worktree-guide.md` - git worktree操作の詳細ガイド
- `references/merge-strategies.md` - マージ戦略の詳細
- `references/risk-assessment.md` - リスク判定基準

---

## 品質優先原則（Superpowers統合）

### 核心原則

1. **Epistemic Humility**: 推測を事実として扱わない。`unknown`と言う勇気を持つ
2. **Evidence First**: 結論ではなく因果と証拠を中心にする
3. **Minimal Change**: 最小単位で変更し、即時検証する
4. **Grounded Laws**: Lawは検証可能・観測可能でなければならない
5. **Source of Truth**: 真実は常に現在のコード。要約はインデックス

### 「速さより質」の実践

- 要件の曖昧さによる手戻りを根本から排除
- テストなし実装を許さない
- 観測不能な変更を防ぐ

---

## 完了条件

- [ ] 実験が成功または失敗の判定完了
- [ ] 成功時: マージ戦略を実行してmainに統合
- [ ] 失敗時: worktreeを削除して元に戻す
- [ ] worktree環境のクリーンアップ完了
- [ ] 元のリポジトリが正常な状態

---

## 停止条件

以下が発生したら即座に停止し、追加計測またはスコープ縮小：

- 予測と現実の継続的乖離（想定外テスト失敗3回以上）
- 観測不能な変更の増加（物差しで検証できない変更）
- ロールバック線の崩壊（戻せない変更の発生）
