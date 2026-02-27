---
name: eld-record
context: fork
description: PCE Context Delta の収集・検証・構造化・知識移転を一貫実行する。意思決定/バグ解決/パターン発見の記録、プロジェクト知識のpce-memory登録、CLAUDE.md/ADR整理、引き継ぎ資料作成に使う。トリガー:「記録して」「知識を整理して」「引き継ぎ資料を作って」「プロジェクト情報を収集して」
---

# ELD Record

Context Deltaの収集から知識移転まで、4フェーズで開発知識を永続化する。

## Phase 1: Context Delta 収集

### 1-A. 開発プロセス知見の収集

作業中の重要な判断・発見を以下の形式で抽出する。

**意思決定:**
```yaml
decision:
  what: 何を決定したか
  why: なぜその選択をしたか
  alternatives: 検討した他の選択肢
  rejected_reasons: 却下した理由
  constraints: 効いた制約条件
  trade_offs: 受け入れたトレードオフ
```

**エラー解決策:**
```yaml
error_resolution:
  symptom: 症状・エラーメッセージ
  root_cause: 根本原因
  solution: 解決策
  prevention: 再発防止策
  related_files: 関連ファイル
```

**パターン発見:**
```yaml
pattern:
  name: パターン名
  context: 適用コンテキスト
  problem: 解決する問題
  solution: 解決方法
  consequences: 結果と影響
```

### 1-B. プロジェクト情報の体系的収集

プロジェクト構造をスキャンし、知識ベースを構築する。

1. プロジェクトスキャン:
   ```bash
   scripts/scan_project.py <project_path>
   ```

2. 発見した情報をunverifiedとしてobserve:
   ```
   observe(
     source_type="file",
     content="<extracted info>",
     source_id="<file_path>",
     ttl_days=7,
     boundary_class="public|internal",
     tags=["unverified", "<category>"]
   )
   ```

3. カテゴリ: `project-info`, `architecture`, `dependencies`, `api`, `config`

## Phase 2: 検証

### Codex CLIによるクロスバリデーション

収集した情報をCodex CLIで検証する。

```
mcp__codex-cli__codex(
  prompt="Verify this claim against the file content:
    Claim: <claim_text>
    File: <file_path>
    Content: <file_content>
    Respond: MATCH | MISMATCH | PARTIAL
    Reason: <brief explanation>"
)
```

| Codex結果 | アクション |
|-----------|-----------|
| MATCH | `observe(..., extract={mode: "single_claim_v0"})` で永続化 |
| PARTIAL | claim修正後、再検証 |
| MISMATCH | 破棄（ttl自然消滅） |

### ハッシュベース検証

```bash
scripts/validate_claims.py <project_path> --claims <claims.json>
```

結果に応じてfeedbackを送信:
```
feedback(claim_id, signal="helpful|outdated", score)
```

## Phase 3: 構造化・配置

収集・検証済みの知見を適切な場所に永続化する。

### 構造化の原則

1. **1記録 = 1関心事**: 粒度を適切に保つ
2. **検索可能性**: タグ/キーワードを付与
3. **文脈保持**: なぜそうなったかの経緯を含める
4. **鮮度管理**: 最終更新日を記録

### 出力先の選択

| 知見の種類 | 出力先 | 形式 |
|-----------|--------|------|
| 即時参照が必要 | pce-memory (upsert) | claim |
| アーキテクチャ決定 | docs/adr/ | ADR |
| プロジェクト共通原則 | ルートCLAUDE.md | Markdown |
| ドメイン固有ルール | フォルダCLAUDE.md | Markdown |

### pce-memory登録

```
upsert(
  text: "構造化された知識",
  kind: "fact|preference|task|policy_hint",
  scope: "session|project|principle",
  boundary_class: "public|internal|pii|secret",
  provenance: { at: ISO8601, actor: "claude", note: "..." }
)
```

### ADR形式

```markdown
# ADR-XXX: タイトル
## Status
Accepted | Deprecated | Superseded by ADR-YYY
## Context
決定が必要になった背景
## Decision
決定内容
## Consequences
結果と影響
```

## Phase 4: 知識移転

セッション間・メンバー間での知識の連続性を確保する。

### 移転対象

- **明示的知識**: ドキュメント化された設計判断、ADR、規約、API仕様
- **暗黙的知識**: 経緯、試行錯誤、却下した選択肢と理由、既知の問題と回避策
- **コンテキスト知識**: プロジェクト背景、技術的制約の由来、チームの慣習

### 引き継ぎドキュメント構造

```markdown
# Knowledge Transfer: [プロジェクト/機能名]

## 1. 現状サマリー
### 完了したこと
- [成果]

### 進行中
- [タスク]: [進捗%] [次のアクション]

### 未着手
- [タスク]: [優先度] [依存関係]

## 2. 重要な決定事項
| 決定 | 理由 | 日付 | 参照 |
|------|------|------|------|

## 3. 既知の問題と注意点
- [課題]: [回避策]

## 4. キーファイル
| ファイル | 役割 | 備考 |
|---------|------|------|

## 5. 次のアクション
1. [ ] [最優先タスク]
```

### 移転タイミング

| シーン | 実施内容 |
|--------|---------|
| セッション終了 | eld-record-compact でノート作成 |
| 担当者交代 | フル引き継ぎドキュメント |
| 新メンバー参加 | オンボーディング資料 |
| マイルストーン | 進捗サマリー |
| プロジェクト完了 | 振り返りと学びの記録 |

## 実行フロー

```
Collect (Phase 1)
  → observe(ttl=7, unverified)
    → Verify (Phase 2)
      → Codex cross-check + hash validation
        → Structure (Phase 3)
          → upsert / CLAUDE.md / ADR
            → Transfer (Phase 4)
              → 引き継ぎドキュメント生成
```

フェーズは必要に応じて個別実行も可能。ユーザーの要求に応じて適切なフェーズから開始する。

## References

- [pce-memory API仕様](references/pce_memory_api.md) - observe/upsert/activate/feedbackの全パラメータ。APIの詳細が必要な時に参照
- [引き継ぎドキュメント例](references/transfer_example.md) - Phase 4の具体的な出力例。初回の引き継ぎ作成時に参照

## Scripts

- `scripts/scan_project.py` - プロジェクト構造スキャン（Phase 1-B）
- `scripts/validate_claims.py` - ハッシュベースclaim検証（Phase 2）

## 品質原則

1. **Epistemic Humility**: 推測を事実として扱わない。`unknown`と言う勇気を持つ
2. **Evidence First**: 因果と証拠を中心にする
3. **Source of Truth**: 真実は常に現在のコード。要約はインデックス
4. **Minimal Change**: 最小単位で変更し、即時検証する
