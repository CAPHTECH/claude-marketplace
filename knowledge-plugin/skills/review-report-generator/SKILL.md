---
name: review-report-generator
context: fork
argument-hint: "[chat|file|issue]"
description: アーキテクチャレビュー結果を意思決定用レポートに整形する。チャット報告・ファイル出力・GitHub Issue作成から出力形式を選択可能。「レビューレポートを作成して」「報告書を生成して」「意思決定用にまとめて」「Issueにして」と言われた時に使用。
---

# Review Report Generator

レビュー結果を意思決定に耐える形式のレポートに整形する。

**核心**: 網羅的な指摘より「意思決定に必要な形」を優先する。

## 前提条件

必須:
- `architecture-review/*/review.yaml` - architecture-reviewer の統合出力（findings + conflicts + prioritized_actions）

推奨:
- `system-map/invariants.yaml` - 不変条件

## 出力形式の選択

`$ARGUMENTS` で出力形式を決定する。未指定の場合は `chat` をデフォルトにする。

| 値 | 動作 | 用途 |
|----|------|------|
| `chat` | チャットで直接報告 | 素早い確認、口頭報告の下書き |
| `file` | ファイル群を生成 | チーム共有、ドキュメント保存 |
| `issue` | GitHub Issueを作成 | バックログ追加、タスク管理 |

判定ロジック:
1. `$ARGUMENTS` が `file` なら file 形式で出力する
2. `$ARGUMENTS` が `issue` なら issue 形式で出力する
3. それ以外（空・`chat`・不明な値）は chat 形式で出力する

## 形式1: chat（チャット報告）

チャットにMarkdownで直接報告する。ファイルは生成しない。

### 出力構成

1. **エグゼクティブサマリー** - 優先度別の件数テーブル
2. **P0/P1 詳細** - 各指摘の問題・推奨案・PR分割・受け入れ条件
3. **P2以下サマリー** - 件数と主要項目のタイトルのみ

### 出力例（サマリー部分）

```markdown
# アーキテクチャレビュー報告書

**レビュー日**: 2024-01-21
**対象**: order-service, payment-service, inventory-service

## サマリー

| カテゴリ | 件数 | 対応状況 |
|---------|------|---------|
| P0 (Blocker) | 2 | 即時対応必須 |
| P1 (Critical) | 3 | 今スプリント |
| P2 (High) | 5 | 次スプリント |
| P3/P4 | 8 | バックログ |
```

P0/P1の各指摘には以下を含める:
- 問題の概要と影響
- 対応案のテーブル（案・内容・工数・推奨マーク）
- PR分割（タイトル・スコープ・サイズ）
- 受け入れ条件（チェックリスト形式）
- ADR要否

## 形式2: file（ファイル出力）

`architecture-review/{timestamp}/report/` 配下にファイル群を生成する。

### ファイル構造

```
architecture-review/{timestamp}/
├── review.yaml        # architecture-reviewer の統合出力（既存）
└── report/            # 本スキルの出力
    ├── summary.md     # エグゼクティブサマリー
    ├── p0-blockers.md # P0詳細（全フィールド）
    ├── p1-critical.md # P1詳細（全フィールド）
    ├── p2-high.md     # P2詳細
    ├── backlog.md     # P3/P4
    └── adrs-needed.md # 必要なADR一覧
```

### 各ファイルの内容

| ファイル | 内容 |
|---------|------|
| summary.md | 件数テーブル + P0/P1の1行サマリー + 推奨アクション |
| p0-blockers.md | P0の全指摘。問題・根拠・対応案・PR分割・受け入れ条件 |
| p1-critical.md | P1の全指摘。p0-blockers.md と同形式 |
| p2-high.md | P2の全指摘。対応案は推奨のみ記載 |
| backlog.md | P3/P4。タイトル・スコープ・推奨案・工数の一覧表 |
| adrs-needed.md | ADRが必要な指摘のリスト。トピック・関連指摘・背景 |

### 用途別の推奨ファイル

| 用途 | 使うファイル |
|------|------------|
| ステークホルダー報告 | summary.md のみ |
| 開発チーム共有 | 全ファイル |
| PR作成 | p0-blockers.md + PR分割情報 |
| バックログ追加 | backlog.md をIssue化 |

## 形式3: issue（GitHub Issue作成）

`gh issue create` で指摘をGitHub Issueとして作成する。

### 作成ルール

| 優先度 | Issue数 | ラベル |
|-------|---------|--------|
| P0 | 指摘ごとに1つ | `architecture-review`, `P0-blocker` |
| P1 | 指摘ごとに1つ | `architecture-review`, `P1-critical` |
| P2以下 | まとめて1つ | `architecture-review` |

### P0/P1 個別Issueの内容

各Issueに以下を含める:
- タイトル: `[{priority}] {title}`
- 概要と影響範囲
- 発生条件
- 根拠（evidence）
- 対応案テーブル + 推奨
- PR分割
- 受け入れ条件（チェックリスト形式）
- ADR要否

詳細なテンプレートは [references/issue-template.md](references/issue-template.md) を参照。Issue本文のフォーマットとghコマンド例が記載されている。

### P2以下まとめIssue

1つのIssueに全P2以下の指摘をまとめる:
- タイトル: `[Architecture Review] P2以下の指摘事項まとめ（{件数}件）`
- P2は各指摘の概要・推奨案・工数を記載
- P3/P4はタイトルとスコープのみ

### 実行手順

1. review.yaml から全指摘を読み込む
2. 指摘を優先度でグルーピングする
3. P0の指摘から順に `gh issue create` を実行する
4. P1の指摘を同様に実行する
5. P2以下をまとめて1つのIssueを作成する
6. 作成したIssueのURL一覧をチャットに報告する

## 指摘の標準形式

各指摘は以下のフィールドを持つ。詳細なYAML例は [references/finding-format.md](references/finding-format.md) を参照。各フィールドの選択基準や算出方法が記載されている。

| フィールド | 必須 | 内容 |
|-----------|------|------|
| id | Yes | FINDING-001 形式の一意ID |
| title | Yes | 問題の端的な名称 |
| scope.type | Yes | component / interaction / crosscutting |
| scope.affected | Yes | 影響を受けるコンポーネント |
| failure_mode.description | Yes | 何が成立しなくなるか |
| failure_mode.impact | Yes | ユーザー・ビジネス・システムへの影響 |
| trigger_conditions | Yes | 発生条件のリスト |
| evidence | Yes | 根拠（source, field, value） |
| options | Yes | 対応案のリスト（id, action, pros, cons, effort） |
| priority.category | Yes | P0 / P1 / P2 / P3 / P4 |
| priority.score | Yes | severity x likelihood x detectability x quality_weight |
| priority.rationale | Yes | 優先度判断の理由 |
| implementation.recommended_option | Yes | 推奨する対応案のID |
| implementation.pr_breakdown | Yes | PR分割（タイトル, スコープ, サイズ） |
| implementation.adr_needed | Yes | ADR作成要否 |
| acceptance_criteria.tests | Yes | テスト条件 |
| acceptance_criteria.metrics | No | 定量メトリクス |
| acceptance_criteria.logs | No | ログ確認項目 |
| acceptance_criteria.contract | No | API契約の変更 |

## 注意事項

- **推測禁止**: evidence がない指摘はレポートに含めない
- **実行可能な形式**: 「問題がある」だけでなく「何をするか」まで書く
- **PR単位まで分割**: 「改善する」ではなく「このPRを作る」と具体化する
- **受け入れ条件の明示**: 完了判定ができる形で記載する
- **issue形式でのラベル**: 事前に `architecture-review`, `P0-blocker`, `P1-critical` ラベルが存在しない場合は `gh label create` で作成する
