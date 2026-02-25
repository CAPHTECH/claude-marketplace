---
name: codex-consultant
context: fork
description: Codex CLI (OpenAI gpt-5.3-codex) に直接相談するスキル。設計判断・実装方針・コードレビュー・デバッグ方針など、別モデルの視点が欲しい時に使用する。「codexに相談」「codexに聞いて」「別の視点が欲しい」「セカンドオピニオン」「codexでレビュー」「codexとペアプロ」「codexとTDD」「codexでペアプログラミング」「ペアプロモード」「adversarial review」と言った時にトリガーする。
---

# Codex Consultant

Codex CLI (gpt-5.3-codex, reasoning: xhigh) に直接相談し、セカンドオピニオンを得る。

## モード選択ガイド

| 目的 | モード | 概要 |
|------|--------|------|
| 通常の実装作業 | [Mode A: Driver/Navigator](#mode-a-drivernavigator) | 一方が実装、他方がレビュー・指示 |
| 精度重視の実装 | [Mode B: Ping-Pong TDD](#mode-b-ping-pong-tdd) | テストと実装を交互に書く |
| セキュリティ・堅牢性 | [Mode C: Adversarial Review](#mode-c-adversarial-review) | 実装後に攻撃的テストで弱点を探す |
| 基本的な相談 | [基本相談](#基本相談) | 単発の質問・レビュー |

## 基本相談

### 使い方

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

## ペアプログラミングモード

### Mode A: Driver/Navigator

一方が実装（Driver）、他方がレビュー・方向付け（Navigator）を担当する。

#### パターン1: Claude=Driver / Codex=Navigator（デフォルト）

Claudeが実装し、Codexがレビュー・改善提案する。

1. **Claudeが実装**: ユーザーの要件に基づきコードを書く
2. **Codexにレビュー依頼**:
```bash
codex exec -m gpt-5.3-codex -c 'model_reasoning_effort="xhigh"' \
  "Navigatorとしてレビューしてください。以下の実装について:
- 設計上の問題点
- エッジケースの見落とし
- より良い代替案
を指摘してください。

ファイル: <パス>
要件: <要件の要約>

<実装コード>"
```
3. **Claudeがフィードバックを反映**: 指摘を取り込んで修正
4. **必要に応じて再レビュー**:
```bash
codex exec resume --last "修正しました。再レビューをお願いします。

<修正後のコード>"
```

#### パターン2: Codex=Driver / Claude=Navigator

Codexが実装し、Claudeがレビュー・方向付けする。

1. **Codexに実装依頼**:
```bash
codex exec -m gpt-5.3-codex --full-auto -C <project-dir> \
  "以下の要件を実装してください:

<要件の詳細>

制約:
- <技術的制約>
- <アーキテクチャの方針>"
```
2. **Claudeがレビュー**: 生成されたコードを読み、品質・設計を評価
3. **修正指示をCodexに送信**:
```bash
codex exec resume --last "以下の点を修正してください:
- <修正点1>
- <修正点2>"
```

### Mode B: Ping-Pong TDD

テストと実装を交互に書く。RED→GREEN→REFACTORサイクルを回す。

#### パターン1: Claude=テスト / Codex=実装（デフォルト）

1. **RED - Claudeがテストを書く**: 要件に基づき失敗するテストを作成
2. **GREEN - Codexに実装を依頼**:
```bash
codex exec -m gpt-5.3-codex --full-auto -C <project-dir> \
  "以下のテストを通す最小限の実装を書いてください。テスト以外の変更は不要です。

テストファイル: <パス>

$(cat <テストファイルパス>)"
```
3. **Claudeがテスト実行**: テストが通ることを確認
4. **REFACTOR - Claudeがリファクタリング**: 重複除去・設計改善
5. **次のRED**: Claudeが次のテストを追加し、ステップ2に戻る

#### パターン2: Codex=テスト / Claude=実装

1. **RED - Codexにテスト作成を依頼**:
```bash
codex exec -m gpt-5.3-codex --full-auto -C <project-dir> \
  "以下の要件に対するテストを書いてください。実装は書かないでください。

要件: <要件>
テストファイル: <テストファイルパス>
テストフレームワーク: <jest/vitest/pytest等>"
```
2. **GREEN - Claudeが実装**: テストを通す最小限のコードを書く
3. **テスト実行で確認**
4. **REFACTOR - Claudeがリファクタリング**
5. **次のRED**:
```bash
codex exec resume --last "テストが通りました。次の要件のテストを追加してください:
- <次の要件>"
```

### Mode C: Adversarial Review

実装後にCodexが攻撃的なテスト・レビューを行い、堅牢性を高める。

#### フロー

1. **Claudeが実装**: 通常通りコードを書く
2. **Codexに破壊テストを依頼**:
```bash
codex exec -m gpt-5.3-codex -c 'model_reasoning_effort="xhigh"' \
  "以下のコードに対して攻撃的レビューを行ってください:

観点:
- 異常入力・境界値で壊れるケース
- セキュリティ脆弱性（インジェクション、認可漏れ等）
- 競合状態・デッドロックの可能性
- リソースリーク・メモリ問題
- エラーハンドリングの不備

具体的な攻撃ケース（入力例やシナリオ）を提示してください。

ファイル: <パス>

<実装コード>"
```
3. **Claudeが修正**: 発見された脆弱性を修正
4. **再攻撃**:
```bash
codex exec resume --last "以下の修正を行いました。再度攻撃してください。新しい攻撃ベクトルも試してください。

<修正内容の要約>"
```
5. **収束まで繰り返し**: 新しい脆弱性が見つからなくなるまでループ

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
- ペアプロモードでは各ラウンドの成果を要約してユーザーに報告する
