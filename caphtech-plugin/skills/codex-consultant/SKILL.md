---
name: codex-consultant
context: fork
description: Codex CLI (OpenAI gpt-5.3-codex) に直接相談するスキル。設計判断・実装方針・コードレビュー・デバッグ方針など、別モデルの視点が欲しい時に使用する。「codexに相談」「codexに聞いて」「別の視点が欲しい」「セカンドオピニオン」「codexでレビュー」と言った時にトリガーする。
---

# Codex Consultant

Codex CLI (gpt-5.3-codex, reasoning: xhigh) に直接相談し、セカンドオピニオンを得る。

## 使い方

### 基本相談

Bash toolで `codex exec` を実行する:

```bash
codex exec -m gpt-5.3-codex -c 'model_reasoning_effort="xhigh"' "<質問・相談内容>"
```

### ファイルコンテキスト付き相談

ファイル内容をstdin経由でpromptに含める:

```bash
# 方法1: ヒアドキュメントで構成
codex exec -m gpt-5.3-codex -c 'model_reasoning_effort="xhigh"' "$(cat <<'EOF'
以下のコードについて<質問>:

$(cat path/to/file.ts)
EOF
)"

# 方法2: Read toolでファイル内容を取得し、promptに埋め込む
codex exec -m gpt-5.3-codex -c 'model_reasoning_effort="xhigh"' \
  "以下のコードについて<質問>:

<ファイル内容>"
```

### セッション継続（マルチターン）

同じトピックで深掘りする場合、resume で会話を継続:

```bash
# 初回: 通常のexec実行
codex exec -m gpt-5.3-codex -c 'model_reasoning_effort="xhigh"' "<初回の質問>"

# 継続: 直前のセッションを再開
codex exec resume --last "<フォローアップの質問>"
```

### コードレビュー

コードレビューには `codex review` サブコマンドを使用:

```bash
# 未コミットの変更をレビュー
codex review --uncommitted

# 特定ブランチとの差分レビュー
codex review --base main

# カスタムプロンプトでレビュー
codex review --base main "セキュリティ脆弱性に注目してレビューして"

# 特定コミットをレビュー
codex review --commit <SHA>
```

### 自動実行モード

コード変更を伴う作業を依頼する場合:

```bash
codex exec -m gpt-5.3-codex --full-auto -C /path/to/project "<変更指示>"
```

## 相談パターン

| パターン | プロンプト構成 |
|----------|--------------|
| 設計判断 | 要件 + 選択肢 + トレードオフの質問 |
| デバッグ | エラー内容 + 関連コード + 試したこと |
| コードレビュー | `codex review` or コード + レビュー観点 |
| リファクタリング | 現状コード + 改善方針の相談 |
| アーキテクチャ | 現構造 + 要件変化 + 方針相談 |

## 固定パラメータ

- **model**: `-m gpt-5.3-codex` (常に指定)
- **reasoning**: `-c 'model_reasoning_effort="xhigh"'` (常に指定)
- **作業ディレクトリ**: `-C <dir>` で必要に応じてプロジェクトルートを指定
- **自動実行**: `--full-auto` でコード変更を伴う場合に使用（sandboxed実行）

## 注意事項

- Codexの回答は参考意見として扱い、最終判断はClaudeが行う
- 大量のコードを渡す場合は要点を絞ってpromptを構成する
- `codex exec resume --last` で文脈を維持した深い議論が可能
- 出力をファイルに保存したい場合は `-o <file>` オプションを使用
