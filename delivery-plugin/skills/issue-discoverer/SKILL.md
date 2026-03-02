---
name: issue-discoverer
context: fork
description: コード走査中に発見したスコープ外の課題をIssue候補として構造化し、ユーザー承認後にGitHub Issueを起票する。「Issue候補を探して」「スコープ外の問題を報告して」「issue-discovererで走査して」とトリガー。
---

# Issue Discoverer

コード走査中に発見したスコープ外の課題（バグ・セキュリティ脆弱性・テスト不足・技術的負債）を
**候補化 → 承認 → 作成** の3段階パイプラインでGitHub Issueに変換する。

## Non-Goals

- 現タスクのスコープ内の問題修正（それは現タスクで直す）
- コードスタイルや命名規約の指摘（style カテゴリは除外）
- 既存Issueの管理・ステータス変更
- セキュリティ脆弱性の詳細を公開Issueに記載すること

## Input

```yaml
issue_discovery_input:
  scope: string            # 走査対象（例: "src/", "lib/auth/", "."）
  repo: string             # リポジトリ（例: "owner/repo"、省略時は現リポジトリ）
  categories:              # 探索カテゴリ（省略時は全カテゴリ）
    - security             # セキュリティ脆弱性
    - bug                  # 潜在バグ
    - missing_tests        # テスト不足
    - tech_debt            # 技術的負債
  batch_tech_debt: boolean # tech_debt を1つのIssueにまとめるか（デフォルト: true）
  project_number: number   # GitHub Project番号（オプション、起票後に追加）
```

### デフォルト動作

- `scope` 省略時: 現在の作業ディレクトリ全体
- `categories` 省略時: `[security, bug, missing_tests, tech_debt]`
- `batch_tech_debt: true` の場合、tech_debt カテゴリの候補を1 Issueにまとめる

## Output

```yaml
issue_discovery_report:
  candidates_found: number      # 発見した候補数
  candidates_approved: number   # ユーザーが承認した数
  issues_created:               # 作成したIssue一覧
    - number: number            # Issue番号
      title: string
      url: string
      category: string
      fingerprint: string       # 重複検出用ハッシュ
  issues_skipped:               # スキップされた候補
    - title: string
      reason: string            # "duplicate" | "user_rejected" | "below_threshold"
  security_advisories: number   # Security Advisory経路に回した数
```

## Processing Flow

### Stage 1: Candidate Discovery

スコープ内のコードを走査し、Issue候補を構造化する。

#### 1a. スコープ走査

対象ディレクトリのコードを読み、以下の観点で問題を発見する:

- **security**: 入力検証不足、認証/認可バイパス、機密情報露出、既知脆弱パターン
- **bug**: 未処理エラー、境界条件の不備、型不整合、リソースリーク
- **missing_tests**: クリティカルパスのテスト未作成、エラーパスの未テスト
- **tech_debt**: 非推奨API使用、TODO/FIXME/HACK コメント、重複コード

#### 1b. 候補の構造化

発見した問題ごとに以下の構造で候補を作成する:

```yaml
issue_candidate:
  category: string          # security | bug | missing_tests | tech_debt
  title: string             # Issue タイトル（簡潔・具体的）
  body: string              # 問題の説明、再現手順、影響範囲
  labels:                   # 自動付与ラベル
    - "ai-discovered"       # 必須ラベル
    - string                # カテゴリ別ラベル（bug, security 等）
  primary_file: string      # 主要な関連ファイルパス
  title_keywords: string[]  # タイトルから抽出したキーワード（正規化済み）
  security_signal: boolean  # セキュリティ関連か
  fingerprint: string       # 重複検出用ハッシュ（1c で生成）
```

#### 1c. Fingerprint 生成

各候補に対して重複検出用の fingerprint を生成する。

```
fingerprint = sha256(category + ":" + sorted(title_keywords).join(",") + ":" + primary_file)[:12]
```

詳細は references/fingerprint-spec.md を参照。

#### 1d. 閾値フィルタリング

カテゴリ別の閾値基準に基づき、ノイズとなる候補を除外する:

| カテゴリ | 閾値 |
|----------|------|
| security | 常に候補化（閾値なし） |
| bug | 実際の機能影響があるもののみ |
| missing_tests | クリティカルパス（決済・認証・データ永続化等）のみ |
| tech_debt | `batch_tech_debt: true` 時もフィルタリング適用後にバッチ化、個別の場合は中程度以上 |
| style | 常に除外（候補化しない） |

詳細は references/threshold-criteria.md を参照。

### Stage 2: Approve

候補の重複チェックとユーザー承認を行う。

#### 2a. 重複チェック

既存Issueとの重複を fingerprint とタイトル類似度で検出する:

```bash
gh issue list --repo <repo> --state open --limit 100 --json number,title,body
```

1. Issue body 内の `<!-- fingerprint: XXXXXXXXXXXX -->` を検索し、完全一致があれば重複と判定し `reason: "duplicate"` でスキップ
2. fingerprint 一致がない場合、タイトルの単語レベルJaccard類似度で判定（閾値: 70%）
3. 類似度70%以上の場合、重複候補としてユーザーに確認を求める（自動スキップはしない）

#### 2b. Security ルーティング

`security_signal: true` の候補は公開Issueに**してはならない**。

- ユーザーに Security Advisory 経路での報告を推奨する
- `gh api` で Security Advisory を作成するか、手動報告を案内する
- 公開 Issue への記載は禁止（情報漏洩防止）

#### 2c. ユーザー承認

残った候補をユーザーに提示し、AskUserQuestion で承認を求める:

各候補について以下を表示:
- カテゴリ、タイトル、概要、影響するファイル、fingerprint
- 推奨アクション（承認 / スキップ / 編集）

ユーザーが「スキップ」を選択した候補は `reason: "user_rejected"` でスキップする。

### Stage 3: Create

承認された候補をGitHub Issueとして起票する。

**前提条件**: `security_signal: true` の候補はこのステージに到達してはならない。
Stage 2b で Security Advisory 経路に振り分け済みであること。
万一到達した場合は処理を中止し、ユーザーにエラーを報告する。

#### 3a. Issue 作成

```bash
gh issue create \
  --repo <repo> \
  --title "<title>" \
  --body "<body>" \
  --label "ai-discovered" \
  --label "<category_label>"
```

Issue body の末尾に fingerprint を HTML コメントとして埋め込む:

```markdown
<!-- fingerprint: XXXXXXXXXXXX -->
```

#### 3b. Project 追加（オプション）

`project_number` が指定されている場合、作成した Issue を GitHub Project に追加する:

```bash
gh project item-add <project_number> --owner <owner> --url <issue_url>
```

#### 3c. レポート出力

全候補の処理結果を `issue_discovery_report` 形式で出力する。

## Guardrails

1. **承認ゲート必須**: ユーザー承認なしにIssueを作成してはならない（Stage 2c は省略不可）
2. **Security 隔離**: `security_signal: true` の候補は公開Issueに記載禁止
3. **重複防止**: fingerprint による既存Issue照合を必ず実行する
4. **ai-discovered ラベル必須**: 全ての作成Issueに `ai-discovered` ラベルを付与する
5. **スコープ外のみ**: 現タスクで修正すべき問題は候補化せず、直接修正する

## References

- references/threshold-criteria.md
- references/fingerprint-spec.md
