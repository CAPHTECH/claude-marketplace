# リサーチ手法カタログ

## 目次

1. [公式ドキュメント](#1-公式ドキュメント)
2. [GitHub リサーチ](#2-github-リサーチ)
3. [コミュニティ・Q&A](#3-コミュニティqa)
4. [パッケージレジストリ](#4-パッケージレジストリ)
5. [ソースコード読解](#5-ソースコード読解)
6. [Webサーチ](#6-webサーチ)
7. [再現実験](#7-再現実験)
8. [AI活用リサーチ](#8-ai活用リサーチ)
9. [コミュニティ直接問い合わせ](#9-コミュニティ直接問い合わせ)

---

## 1. 公式ドキュメント

**信頼度**: 高（一次情報）
**適した調査目的**: API仕様・使い方・設定方法・移行ガイド

### 探し方

```
1. <ライブラリ名> official docs site:docs.<ライブラリ名>.xxx で検索
2. README.md の Documentation / Links セクション
3. パッケージレジストリのリンク（npm/PyPI等のHomepageフィールド）
```

### 確認ポイント

- **バージョン選択**: ドキュメントサイト内でバージョンを切り替えて対象バージョンを確認
- **API Reference vs Guide**: APIリファレンスは仕様、Guideは使い方。両方を確認する
- **更新日・変更履歴**: ページ下部やChangelogリンクを確認

### よく使うセクション

| 目的 | セクション名の例 |
|------|----------------|
| API仕様 | API Reference / API Docs |
| 移行 | Migration Guide / Upgrade Guide |
| 設定 | Configuration / Options |
| はじめかた | Getting Started / Quick Start |
| 変更点 | Changelog / What's New / Release Notes |

---

## 2. GitHub リサーチ

**信頼度**: 高（一次情報・実際の開発者の声）
**適した調査目的**: バグ調査・最新情報・未公開の挙動・移行情報

### 2.1 Issues 検索

バグ・既知の問題・動作確認に最も有効。

```
GitHub検索クエリ例:
- repo:<owner>/<repo> <エラーメッセージ>
- repo:<owner>/<repo> is:issue is:open <症状>
- repo:<owner>/<repo> is:issue is:closed <症状> label:bug
```

**確認ポイント**:
- `is:closed` のIssueに「解決策」「回避策」がある
- Issue本文より**コメント欄**に解決策が書かれることが多い
- LinkedされているPRが実際の修正内容を示す

### 2.2 Releases / CHANGELOG

```
<owner>/<repo>/releases   → バージョンごとのリリースノート
<owner>/<repo>/blob/main/CHANGELOG.md
```

**確認ポイント**:
- Breaking Changes セクション
- 対象バージョン間の差分（v1.x → v2.x 等）

### 2.3 Pull Requests 検索

実装の詳細・設計判断・バグ修正の背景を知るために有効。

```
GitHub検索クエリ例:
- repo:<owner>/<repo> is:pr is:merged <機能名>
- repo:<owner>/<repo> is:pr fix <バグ症状>
```

### 2.4 Discussions

質問・設計議論・ユースケース相談。

```
<owner>/<repo>/discussions
```

### 2.5 ソースコード検索

```
# GitHub Code Search（github.com/search）
- repo:<owner>/<repo> <関数名/クラス名>  language:typescript
- org:<org名> <キーワード>
```

---

## 3. コミュニティ・Q&A

**信頼度**: 中（二次情報・ただし実践的な解決策が多い）
**適した調査目的**: エラー解決・ユースケース・回避策

### Stack Overflow

```
検索クエリ例:
- site:stackoverflow.com <ライブラリ名> <エラー文字列>
- [<ライブラリ名>] <症状>  (タグ検索)
```

**注意事項**:
- 回答の作成日を必ず確認（古い回答は現バージョンに合わない）
- スコアが高い回答でも古い場合がある → バージョンタグを確認
- Accepted Answer より **投票数が高い別回答** の方が現代的な解決策の場合がある

### Reddit

```
site:reddit.com/r/<サブレディット> <ライブラリ名> <症状>

主要サブレディット例:
- r/javascript, r/typescript, r/reactjs, r/node
- r/python, r/rust, r/golang
- r/devops, r/docker, r/kubernetes
```

### Discord / Slack コミュニティ

多くのOSSプロジェクトが公式Discordを持つ。過去ログを検索。

---

## 4. パッケージレジストリ

**信頼度**: 高（メタデータとして信頼性高い）
**適した調査目的**: バージョン確認・依存関係・リポジトリリンク

| エコシステム | レジストリURL |
|-------------|-------------|
| JavaScript/TypeScript | npmjs.com |
| Python | pypi.org |
| Rust | crates.io |
| Go | pkg.go.dev |
| Ruby | rubygems.org |
| Java/Kotlin | mvnrepository.com |
| Swift | swift.org/package-index |

### 確認ポイント

- **Versions タブ**: バージョン一覧・リリース日
- **Dependencies**: 依存ライブラリとそのバージョン制約
- **Homepage / Repository リンク**: 公式ドキュメントへのリンク
- **Weekly Downloads / Stars**: 活発さ・採用実績の目安

---

## 5. ソースコード読解

**信頼度**: 最高（一次情報の中でも最も正確）
**適した調査目的**: ドキュメントに載っていない挙動・エッジケース・内部動作

### アプローチ

```
1. エントリポイントを特定: index.ts / main.rs / __init__.py 等
2. 対象機能のコードを特定: 関数名・クラス名でgrep
3. テストコードを読む: tests/ __tests__/ spec/ - 仕様が記述されている
4. 型定義を読む: .d.ts / types.ts - インターフェース仕様
```

### テストコードが最も信頼できる仕様書

```bash
# テストファイルを確認
find . -name "*.test.ts" -o -name "*.spec.ts" | xargs grep "<機能名>"
```

### 変更履歴から挙動の変化を追う

```bash
git log --oneline --follow <ファイルパス>
git show <コミットハッシュ>
```

---

## 6. Webサーチ

**信頼度**: 中〜低（ソースに依存）
**適した調査目的**: 最新情報・ニッチな問題・日本語情報

### 効果的な検索クエリ

```
# エラー調査
"<エラーメッセージ>" <ライブラリ名> <バージョン>

# 最新情報
<ライブラリ名> 2025 <機能名>

# 移行
<ライブラリ名> migration v<旧バージョン> to v<新バージョン>

# ベストプラクティス
<ライブラリ名> best practices production 2025

# 比較
<ライブラリA> vs <ライブラリB> <用途> 2025
```

### 信頼できるソース（優先順）

1. 公式ブログ・ドキュメント
2. 著名な技術ブログ（開発元・コアコントリビュータ）
3. 技術メディア（Zenn・Qiita・Medium・dev.to）
4. 個人ブログ

### WebFetch ツール

URLが特定できたらClaudeのWebFetchツールで内容を取得・要約できる。

---

## 7. 再現実験

**信頼度**: 最高（実証に基づく）
**適した調査目的**: バグ確認・API動作確認・パフォーマンス検証

### 最小再現コードの作成

```
原則:
- 最小限のコードで問題を再現する
- 外部依存を排除する
- 1つの仮説を1つの実験で検証する
```

### 実験の記録

```markdown
### 実験 #1

**仮説**: <検証したいこと>
**コード**:
```<language>
<最小再現コード>
```
**結果**: <実際の出力>
**結論**: <仮説が正しいか・なぜそうなるか>
```

### サンドボックス環境

- **Node.js**: node -e "..." または RunKit
- **Python**: python -c "..." または Replit
- **ブラウザJS**: Browser DevTools Console
- **Docker**: `docker run --rm <image> <command>`

---

## 8. AI活用リサーチ

**信頼度**: 低〜中（必ず一次情報で検証が必要）
**適した調査目的**: 出発点の特定・概念の理解・検索クエリの生成

### 効果的な使い方

```
良い使い方:
- 「〇〇について調べたい。どのドキュメントを読むべきか？」
- 「このエラーメッセージの意味と調査の出発点を教えて」
- 「〇〇のAPIの概要を教えて（後で公式ドキュメントで検証する）」

悪い使い方:
- 「〇〇の最新バージョンの仕様を教えて」（カットオフ後の情報は不正確）
- AI回答をそのまま実装に使う（ハルシネーション注意）
```

### ハルシネーション対策

- AIが述べたAPIや関数名は必ず公式ドキュメントで確認
- 「このAPIは本当に存在するか？」を一次情報で検証
- バージョン番号・パラメータ名は特に検証が必要

---

## 9. コミュニティ直接問い合わせ

**信頼度**: 高（専門家の回答）
**適した調査目的**: 調査しても解決しない問題・設計相談

### 問い合わせ先

- GitHub Issues（バグ報告・質問）
- GitHub Discussions（設計相談・ユースケース）
- 公式Discord / Slack
- Stack Overflow（`<ライブラリ名>` タグで質問）

### 良い質問の書き方

```markdown
## 環境
- ライブラリバージョン: X.Y.Z
- OS: macOS 14 / Ubuntu 22.04
- 言語バージョン: Node.js 20.x

## 問題
<何をしようとしているか・何が起きているか>

## 再現コード
```<language>
<最小限の再現コード>
```

## 期待する動作
<こうなるはずだと思った理由>

## 実際の動作
<実際に起きていること・エラーメッセージ>

## 試したこと
- [試したこと1]
- [試したこと2]
```
