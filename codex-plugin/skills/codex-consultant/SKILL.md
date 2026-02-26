---
name: codex-consultant
context: fork
description: Codex CLI (OpenAI gpt-5.3-codex) に直接相談するスキル。設計判断・実装方針・コードレビュー・デバッグ方針など、別モデルの視点が欲しい時に使用する。「codexに相談」「codexに聞いて」「別の視点が欲しい」「セカンドオピニオン」「codexでレビュー」「codexとペアプロ」「codexとTDD」「codexでペアプログラミング」「ペアプロモード」「adversarial review」と言った時にトリガーする。
---

# Codex Consultant

Codex MCP (gpt-5.3-codex, reasoning: xhigh) に直接相談し、セカンドオピニオンを得る。

## モード選択ガイド

| 目的 | モード | 概要 |
|------|--------|------|
| 通常の実装作業 | [Mode A: Driver/Navigator](#mode-a-drivernavigator) | 一方が実装、他方がレビュー・指示 |
| 精度重視の実装 | [Mode B: Ping-Pong TDD](#mode-b-ping-pong-tdd) | テストと実装を交互に書く |
| セキュリティ・堅牢性 | [Mode C: Adversarial Review](#mode-c-adversarial-review) | 実装後に攻撃的テストで弱点を探す |
| 基本的な相談 | [基本相談](#基本相談) | 単発の質問・レビュー |

## 基本相談

### 使い方

`mcp__codex__codex` ツールを呼び出す:

```
mcp__codex__codex(
  prompt: "<質問・相談内容>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" }
)
```

### ファイルコンテキスト付き相談

Read ツールでファイル内容を取得し、prompt に埋め込む:

```
mcp__codex__codex(
  prompt: "以下のコードについて<質問>:\n\n<ファイル内容>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" },
  cwd: "<プロジェクトルート>"
)
```

### セッション継続（マルチターン）

同じトピックで深掘りする場合、前回の threadId を使って会話を継続:

```
# 初回: 新規セッション開始
mcp__codex__codex(
  prompt: "<初回の質問>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" }
)
# → レスポンスから threadId を取得

# 継続: threadId を指定して会話を再開
mcp__codex__codex-reply(
  threadId: "<取得したthreadId>",
  prompt: "<フォローアップの質問>"
)
```

### コードレビュー

git diff で差分を取得し、Codex に渡してレビューを依頼する:

```
# 1. Bash ツールで差分を取得
git diff              # 未コミットの変更
git diff main...HEAD  # 特定ブランチとの差分

# 2. 差分を Codex に渡してレビュー
mcp__codex__codex(
  prompt: "以下の差分をコードレビューしてください。設計上の問題点、バグの可能性、改善案を指摘してください。\n\n<diff出力>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" },
  cwd: "<プロジェクトルート>"
)

# カスタム観点でのレビュー
mcp__codex__codex(
  prompt: "セキュリティ脆弱性に注目して以下の差分をレビューしてください。\n\n<diff出力>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" },
  cwd: "<プロジェクトルート>"
)
```

### 自動実行モード

コード変更を伴う作業を Codex に依頼する場合:

```
mcp__codex__codex(
  prompt: "<変更指示>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" },
  cwd: "<プロジェクトルート>",
  sandbox: "workspace-write",
  approval-policy: "on-failure"
)
```

## ペアプログラミングモード

### Mode A: Driver/Navigator

一方が実装（Driver）、他方がレビュー・方向付け（Navigator）を担当する。

#### パターン1: Claude=Driver / Codex=Navigator（デフォルト）

Claudeが実装し、Codexがレビュー・改善提案する。

1. **Claudeが実装**: ユーザーの要件に基づきコードを書く
2. **Codexにレビュー依頼**:
```
mcp__codex__codex(
  prompt: "Navigatorとしてレビューしてください。以下の実装について:
- 設計上の問題点
- エッジケースの見落とし
- より良い代替案
を指摘してください。

ファイル: <パス>
要件: <要件の要約>

<実装コード>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" },
  cwd: "<プロジェクトルート>"
)
```
3. **Claudeがフィードバックを反映**: 指摘を取り込んで修正
4. **必要に応じて再レビュー**:
```
mcp__codex__codex-reply(
  threadId: "<前回のthreadId>",
  prompt: "修正しました。再レビューをお願いします。

<修正後のコード>"
)
```

#### パターン2: Codex=Driver / Claude=Navigator

Codexが実装し、Claudeがレビュー・方向付けする。

1. **Codexに実装依頼**:
```
mcp__codex__codex(
  prompt: "以下の要件を実装してください:

<要件の詳細>

制約:
- <技術的制約>
- <アーキテクチャの方針>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" },
  cwd: "<プロジェクトルート>",
  sandbox: "workspace-write",
  approval-policy: "on-failure"
)
```
2. **Claudeがレビュー**: 生成されたコードを読み、品質・設計を評価
3. **修正指示をCodexに送信**:
```
mcp__codex__codex-reply(
  threadId: "<前回のthreadId>",
  prompt: "以下の点を修正してください:
- <修正点1>
- <修正点2>"
)
```

### Mode B: Ping-Pong TDD

テストと実装を交互に書く。RED→GREEN→REFACTORサイクルを回す。

#### パターン1: Claude=テスト / Codex=実装（デフォルト）

1. **RED - Claudeがテストを書く**: 要件に基づき失敗するテストを作成
2. **GREEN - Codexに実装を依頼**:
```
mcp__codex__codex(
  prompt: "以下のテストを通す最小限の実装を書いてください。テスト以外の変更は不要です。

テストファイル: <パス>

<テストコード>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" },
  cwd: "<プロジェクトルート>",
  sandbox: "workspace-write",
  approval-policy: "on-failure"
)
```
3. **Claudeがテスト実行**: テストが通ることを確認
4. **REFACTOR - Claudeがリファクタリング**: 重複除去・設計改善
5. **次のRED**: Claudeが次のテストを追加し、ステップ2に戻る

#### パターン2: Codex=テスト / Claude=実装

1. **RED - Codexにテスト作成を依頼**:
```
mcp__codex__codex(
  prompt: "以下の要件に対するテストを書いてください。実装は書かないでください。

要件: <要件>
テストファイル: <テストファイルパス>
テストフレームワーク: <jest/vitest/pytest等>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" },
  cwd: "<プロジェクトルート>",
  sandbox: "workspace-write",
  approval-policy: "on-failure"
)
```
2. **GREEN - Claudeが実装**: テストを通す最小限のコードを書く
3. **テスト実行で確認**
4. **REFACTOR - Claudeがリファクタリング**
5. **次のRED**:
```
mcp__codex__codex-reply(
  threadId: "<前回のthreadId>",
  prompt: "テストが通りました。次の要件のテストを追加してください:
- <次の要件>"
)
```

### Mode C: Adversarial Review

実装後にCodexが攻撃的なテスト・レビューを行い、堅牢性を高める。

#### フロー

1. **Claudeが実装**: 通常通りコードを書く
2. **Codexに破壊テストを依頼**:
```
mcp__codex__codex(
  prompt: "以下のコードに対して攻撃的レビューを行ってください:

観点:
- 異常入力・境界値で壊れるケース
- セキュリティ脆弱性（インジェクション、認可漏れ等）
- 競合状態・デッドロックの可能性
- リソースリーク・メモリ問題
- エラーハンドリングの不備

具体的な攻撃ケース（入力例やシナリオ）を提示してください。

ファイル: <パス>

<実装コード>",
  model: "gpt-5.3-codex",
  config: { "model_reasoning_effort": "xhigh" },
  cwd: "<プロジェクトルート>"
)
```
3. **Claudeが修正**: 発見された脆弱性を修正
4. **再攻撃**:
```
mcp__codex__codex-reply(
  threadId: "<前回のthreadId>",
  prompt: "以下の修正を行いました。再度攻撃してください。新しい攻撃ベクトルも試してください。

<修正内容の要約>"
)
```
5. **収束まで繰り返し**: 新しい脆弱性が見つからなくなるまでループ

## 相談パターン

| パターン | プロンプト構成 |
|----------|--------------|
| 設計判断 | 要件 + 選択肢 + トレードオフの質問 |
| デバッグ | エラー内容 + 関連コード + 試したこと |
| コードレビュー | git diff + レビュー観点 |
| リファクタリング | 現状コード + 改善方針の相談 |
| アーキテクチャ | 現構造 + 要件変化 + 方針相談 |

## 固定パラメータ

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| model | `gpt-5.3-codex` | 常に指定 |
| config.model_reasoning_effort | `xhigh` | 常に指定 |
| cwd | プロジェクトルート | ファイルアクセスが必要な場合に指定 |
| sandbox | `workspace-write` | コード変更を伴う場合に使用 |
| approval-policy | `on-failure` | コード変更を伴う場合に使用 |

## 注意事項

- Codexの回答は参考意見として扱い、最終判断はClaudeが行う
- 大量のコードを渡す場合は要点を絞ってpromptを構成する
- `mcp__codex__codex-reply` で threadId を指定し、文脈を維持した深い議論が可能
- ペアプロモードでは各ラウンドの成果を要約してユーザーに報告する
