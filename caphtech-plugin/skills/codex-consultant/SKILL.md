---
name: codex-consultant
context: fork
description: Codex CLI (OpenAI gpt-5.3-codex) にMCP経由で相談するスキル。設計判断・実装方針・コードレビュー・デバッグ方針など、別モデルの視点が欲しい時に使用する。「codexに相談」「codexに聞いて」「別の視点が欲しい」「セカンドオピニオン」「codexでレビュー」と言った時にトリガーする。
---

# Codex Consultant

Codex CLI (gpt-5.3-codex, reasoning: xhigh) にMCP経由で相談し、セカンドオピニオンを得る。

## 使い方

### 基本相談

```
mcp__codex-cli__codex(
  prompt="<質問・相談内容>",
  model="gpt-5.3-codex",
  reasoningEffort="xhigh"
)
```

### ファイルコンテキスト付き相談

ファイル内容を読み取ってからpromptに含める:

```
1. Read tool でファイル内容を取得
2. mcp__codex-cli__codex(
     prompt="以下のコードについて<質問>:\n\n```\n<ファイル内容>\n```",
     model="gpt-5.3-codex",
     reasoningEffort="xhigh"
   )
```

### セッション継続（マルチターン）

同じトピックで深掘りする場合、sessionIdで会話を継続:

```
# 初回: sessionIdなし → レスポンスからsessionIdを記録
mcp__codex-cli__codex(
  prompt="<初回の質問>",
  model="gpt-5.3-codex",
  reasoningEffort="xhigh"
)

# 継続: 前回のsessionIdを指定
mcp__codex-cli__codex(
  prompt="<フォローアップの質問>",
  sessionId="<前回のsessionId>"
)
```

### コードレビュー

コードレビューにはreviewツールを使用:

```
# 未コミットの変更をレビュー
mcp__codex-cli__review(
  uncommitted=true,
  model="gpt-5.3-codex"
)

# 特定ブランチとの差分レビュー
mcp__codex-cli__review(
  base="main",
  model="gpt-5.3-codex"
)

# カスタムプロンプトでレビュー
mcp__codex-cli__review(
  base="main",
  prompt="セキュリティ脆弱性に注目してレビューして",
  model="gpt-5.3-codex"
)
```

## 相談パターン

| パターン | プロンプト構成 |
|----------|--------------|
| 設計判断 | 要件 + 選択肢 + トレードオフの質問 |
| デバッグ | エラー内容 + 関連コード + 試したこと |
| コードレビュー | reviewツール or コード + レビュー観点 |
| リファクタリング | 現状コード + 改善方針の相談 |
| アーキテクチャ | 現構造 + 要件変化 + 方針相談 |

## 固定パラメータ

- **model**: `gpt-5.3-codex` (常に指定)
- **reasoningEffort**: `xhigh` (常に指定)
- workingDirectory: 必要に応じてプロジェクトルートを指定
- fullAuto: コード変更を伴う場合はtrue（sandboxed実行）

## 注意事項

- Codexの回答は参考意見として扱い、最終判断はClaudeが行う
- 大量のコードを渡す場合は要点を絞ってpromptを構成する
- sessionIdを使えば文脈を維持した深い議論が可能
