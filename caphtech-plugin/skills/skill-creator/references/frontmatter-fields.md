# Frontmatter Fields Reference

Claude Code SKILL.md の YAML frontmatter フィールド完全リファレンス。

## 必須フィールド

### name

スキルの識別子。ディレクトリ名と一致させる。

- 小文字・数字・ハイフンのみ（`[a-z0-9-]+`）
- 64文字以内
- 先頭・末尾のハイフン不可、連続ハイフン不可
- 動詞主導の短いフレーズを推奨（例: `deploy-app`, `review-code`）

```yaml
name: my-skill-name
```

### description

Claudeがスキル選択に使う唯一の判断材料。最重要フィールド。

- 1024文字以内
- XMLタグ（`<`, `>`）不可
- 単一行で記述（YAMLマルチライン `|` や `>` は使わない）
- **何をするか** + **いつ使うか** を必ず含める

```yaml
description: Claude Code用のSkillを新規作成・更新するためのガイド。「スキルを作成して」「skillを作って」と言われた時に使用する。
```

description記述の詳細ガイド → [description-craft.md](description-craft.md)

## オプションフィールド

### context

スキルの実行コンテキストを指定。

```yaml
context: fork
```

- `fork`: 隔離されたサブエージェントで実行。会話履歴にアクセスできない
- 省略（デフォルト）: メイン会話のインラインで実行

**fork を使う場面**: 複数ステップの独立ワークフロー、副作用のある操作、メイン会話を汚したくない分析タスク

**fork を避ける場面**: シンプルな一発タスク、会話履歴が必要、リアルタイム協働

### agent

`context: fork` と組み合わせて使用。サブエージェントのタイプを指定。

```yaml
context: fork
agent: Explore
```

利用可能な値: `Explore`, `Plan`, `general-purpose` 等

### disable-model-invocation

`true` に設定すると、Claudeの自動起動を防止。ユーザーが明示的に `/skill-name` で呼ぶ必要がある。

```yaml
disable-model-invocation: true
```

**使う場面**: deploy、commit 等の副作用を伴う操作。意図しない起動を防ぐ。

### user-invocable

`false` に設定すると `/` メニューから非表示になる。

```yaml
user-invocable: false
```

**使う場面**: 背景知識やガイドラインなど、コマンドとして呼ばれることを意図しないスキル。

### allowed-tools

スキルアクティブ時に許可なしで使えるツールをカンマ区切りで指定。

```yaml
allowed-tools: Read, Grep, Bash
```

### model

スキルアクティブ時に使用するモデルを指定。

```yaml
model: sonnet
```

利用可能な値: `sonnet`, `opus`, `haiku`

### argument-hint

`/skill-name` のオートコンプリートで表示される引数ヒント。

```yaml
argument-hint: "[issue-number]"
```

例: `/fix-issue 123` → `argument-hint: "[issue-number]"`

### hooks

スキルのライフサイクルにスコープされたフック。

## 文字列置換

SKILL.md本体で使える動的変数:

| 変数 | 説明 | 例 |
|------|------|-----|
| `$ARGUMENTS` | スキルに渡された全引数 | `/deploy staging` → `staging` |
| `$ARGUMENTS[N]` | N番目の引数（0始まり） | `/deploy staging us-east` → `$ARGUMENTS[0]` = `staging` |
| `$N` | `$ARGUMENTS[N]` の短縮形 | `$0` = 最初の引数 |
| `${CLAUDE_SESSION_ID}` | 現在のセッションID | ログ記録用 |

### 動的コンテキスト注入

`!`コマンド`` 構文でシェルコマンドの出力をスキル内容に前処理で注入できる。

## フィールド組み合わせ例

### 参照知識型スキル（自動起動OK）

```yaml
---
name: api-conventions
description: このコードベースのAPI設計パターン。API設計時やエンドポイント追加時に自動で参照される。
---
```

### コマンド型スキル（手動起動のみ）

```yaml
---
name: deploy
description: アプリケーションを本番環境にデプロイする。
disable-model-invocation: true
argument-hint: "[environment]"
allowed-tools: Read, Bash
---
```

### 独立分析型スキル（fork実行）

```yaml
---
name: deep-research
description: トピックを徹底的にリサーチする。「詳しく調べて」「深掘りして」と言われた時に使用。
context: fork
agent: Explore
---
```

### 背景知識型スキル（非表示）

```yaml
---
name: coding-standards
description: チームのコーディング規約。コード生成・レビュー時に自動参照される。
user-invocable: false
---
```
