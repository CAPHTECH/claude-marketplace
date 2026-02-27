---
name: eld-record
context: fork
argument-hint: "record | compact | maintenance (default: record)"
description: |
  Context Delta の収集・検証・構造化・知識移転を一貫実行する。
  compact/maintenance サブモードで履歴圧縮・知識メンテナンスも統合。
  Context Engineering（3層メモリ + Claim Schema + 動的ポリシー）で
  知識の鮮度と信頼性を自動管理する。

  トリガー条件:
  - 「記録して」「知識を整理して」「引き継ぎ資料を作って」
  - 「コンテキストを圧縮して」「ノートを作成して」（compact）
  - 「メモリをメンテナンスして」「Claimを整理して」（maintenance）
---

# ELD Record

Context Delta の収集から知識移転まで、4フェーズで開発知識を永続化する。
compact/maintenance サブモードにより履歴圧縮・知識品質管理も統合。

## $ARGUMENTS

| サブモード | 説明 | 典型トリガー |
|-----------|------|-------------|
| `record` (default) | Phase 1-4: 収集 → 検証 → 構造化 → 移転 | 「記録して」「引き継ぎ資料を作って」 |
| `compact` | 履歴圧縮: 鮮度チェック → 動的アクション → 圧縮レポート | 「まとめて」「ノート作成」「コンテキスト圧縮」 |
| `maintenance` | 知識メンテナンス: 孤立検出 → 矛盾解決 → 品質スコア → FB統合 | 「メモリ整理」「Claim整理」「古いClaim削除」 |

## Context Engineering

### Claim Schema

すべての知識は Claim として構造化する。

```yaml
claim:
  id: "claim-<domain>-<short-name>"
  text: "主張内容"
  source:
    type: "code|test|log|human|inference"
    path: "ソースファイルパス（該当時）"
    hash: "sha256:..."           # ソース自動タグ用
    observed_at: "ISO8601"
  epistemic_status: "verified|inferred|unknown"
  ttl_days: 30                   # 鮮度管理
  boundary_class: "public|internal|pii|secret"
  tags: ["domain", "category"]
  confidence: 0.95               # 0.0-1.0
```

### 3層メモリモデル

| Layer | 内容 | 寿命 | scope | 更新頻度 |
|-------|------|------|-------|----------|
| **Working** | 現セッションの仮説・中間結果 | セッション終了まで | `session` | 高 |
| **Short-term** | 直近タスクの決定・発見 | TTL (7-30日) | `project` | 中 |
| **Long-term** | 検証済み原則・ADR・Law/Term | 無期限 | `principle` | 低 |

### 動的ポリシー (KEEP / SUMMARIZE / DISCARD)

各 Claim に対し、以下の基準で自動的にアクションを決定する。

| ポリシー | 条件 | アクション |
|----------|------|-----------|
| **KEEP** | verified + TTL内 + feedback positive | そのまま保持 |
| **SUMMARIZE** | TTL超過 but 参照頻度高 | 要約して Short-term → Long-term 昇格検討 |
| **DISCARD** | TTL超過 + feedback negative/なし + 参照なし | 削除候補としてマーク |

## Source Auto-Tagging

Claim 生成時にソース情報を自動付与する。

```
observe(content, source_type, source_id)
  → hash = sha256(file_content_at_source_id)
  → claim.source.hash = hash
  → claim.source.observed_at = now()
```

ソース変更検知時（hash不一致）、関連 Claim の epistemic_status を自動ダウングレード。

## Epistemic Auto-Downgrade

ソース変更や時間経過に基づき、Claim の信頼度を自動的に降格する。

| 現在の状態 | トリガー | 降格先 | 理由 |
|-----------|---------|--------|------|
| `verified` | ソースファイルの hash 変更 | `inferred` | 根拠コードが変更された |
| `verified` | TTL 超過 (>30日) | `inferred` | 鮮度劣化 |
| `inferred` | ソース削除 or 大幅変更 | `unknown` | 根拠消失 |
| `inferred` | TTL 超過 (>60日) | `unknown` | 長期未検証 |

降格発生時は Record Phase 2 の再検証フローにキューイングする。

## Phase 1: Context Delta 収集

### 1-A. 開発プロセス知見の収集

作業中の重要な判断・発見を Claim Schema に沿って抽出する。

**意思決定:**
```yaml
claim:
  id: "claim-decision-<topic>"
  text: "<what>を決定: <why>"
  source:
    type: "human"
    observed_at: "ISO8601"
  epistemic_status: "verified"
  tags: ["decision", "<domain>"]
  metadata:
    alternatives: ["検討した他の選択肢"]
    rejected_reasons: ["却下した理由"]
    constraints: ["効いた制約条件"]
    trade_offs: ["受け入れたトレードオフ"]
```

**エラー解決策:**
```yaml
claim:
  id: "claim-error-<symptom-key>"
  text: "<symptom> の根本原因は <root_cause>、解決策は <solution>"
  source:
    type: "log"
    path: "<related_file>"
    hash: "sha256:..."
    observed_at: "ISO8601"
  epistemic_status: "verified"
  tags: ["error-resolution", "<domain>"]
  metadata:
    prevention: "再発防止策"
```

**パターン発見:**
```yaml
claim:
  id: "claim-pattern-<name>"
  text: "<context> において <problem> を <solution> で解決するパターン"
  source:
    type: "inference"
    observed_at: "ISO8601"
  epistemic_status: "inferred"
  tags: ["pattern", "<domain>"]
  metadata:
    consequences: "結果と影響"
```

### 1-B. プロジェクト情報の体系的収集

プロジェクト構造をスキャンし、知識ベースを構築する。

1. プロジェクトスキャン:
   ```bash
   scripts/scan_project.py <project_path>
   ```

2. 発見した情報を Claim Schema で observe:
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
   Source Auto-Tagging により hash が自動付与される。

3. カテゴリ: `project-info`, `architecture`, `dependencies`, `api`, `config`

## Phase 2: 検証

### Codex CLIによるクロスバリデーション

収集した Claim を Codex CLI で検証する。

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
| MATCH | epistemic_status → `verified`、Long-term 昇格検討 |
| PARTIAL | Claim 修正後、再検証 |
| MISMATCH | DISCARD ポリシー適用 |

### ハッシュベース検証

```bash
scripts/validate_claims.py <project_path> --claims <claims.json>
```

結果に応じて feedback を送信:
```
feedback(claim_id, signal="helpful|outdated", score)
```

hash 不一致の Claim は Epistemic Auto-Downgrade を適用。

## Phase 3: 構造化・配置

収集・検証済みの知見を適切な場所に永続化する。

### 構造化の原則

1. **1記録 = 1関心事**: 粒度を適切に保つ
2. **検索可能性**: タグ/キーワードを付与
3. **文脈保持**: なぜそうなったかの経緯を含める
4. **鮮度管理**: TTL と source hash で自動管理

### 出力先の選択（3層メモリ対応）

| 知見の種類 | メモリ層 | 出力先 | 形式 |
|-----------|---------|--------|------|
| セッション中の仮説 | Working | pce-memory (session) | Claim |
| タスク固有の決定 | Short-term | pce-memory (project) | Claim |
| 検証済み原則・ADR | Long-term | pce-memory (principle) + docs/ | Claim + ADR |
| プロジェクト共通原則 | Long-term | ルートCLAUDE.md | Markdown |
| ドメイン固有ルール | Long-term | フォルダCLAUDE.md | Markdown |

### pce-memory 登録（Claim Schema準拠）

```
upsert(
  text: "構造化された知識",
  kind: "fact|preference|task|policy_hint",
  scope: "session|project|principle",
  boundary_class: "public|internal|pii|secret",
  content_hash: "sha256:...",
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
| セッション終了 | `compact` サブモードでノート作成 |
| 担当者交代 | フル引き継ぎドキュメント |
| 新メンバー参加 | オンボーディング資料 |
| マイルストーン | 進捗サマリー |
| プロジェクト完了 | 振り返りと学びの記録 |

## compact サブモード

長期・反復で膨らむ履歴を要約/圧縮して、継続可能な状態を維持する。

### 圧縮の原則

1. **連続性保持**: 判断の経緯を失わない
2. **最小化**: 必要最小限に絞る
3. **構造化**: 検索・参照しやすい形式
4. **差分明示**: 何が変わったかを明確に

### 実行フロー

```
1. 鮮度チェック
   → 全 Claim の TTL・hash を検査
   → Epistemic Auto-Downgrade 適用

2. 動的アクション適用
   → KEEP: そのまま保持
   → SUMMARIZE: 要約して層昇格検討
   → DISCARD: 削除候補マーク

3. 圧縮レポート生成
   → セッションノート or 進捗サマリー出力
```

### セッションノート

```markdown
# Session Note: [日付/タスク名]

## 達成したこと
- [成果1]

## 重要な決定
- [決定1]: [理由]

## 未解決・次回への引き継ぎ
- [ ] [TODO1]

## 参照すべきファイル
- [ファイル1]: [その役割]

## Claim 鮮度レポート
| ステータス | 件数 | アクション |
|-----------|------|-----------|
| KEEP | N | 保持 |
| SUMMARIZE | N | 要約済み |
| DISCARD | N | 削除済み |
```

### 進捗サマリー（長期プロジェクト用）

```markdown
# Progress: [プロジェクト名]

## Current State
[現在の状態を1-2文で]

## Completed Milestones
1. [マイルストーン1] - [日付]

## Active Context
- Goal: [現在の目標]
- Blockers: [阻害要因]
- Next: [次のアクション]
```

### 圧縮タイミング

| トリガー | アクション |
|---------|-----------|
| 50ターン経過 | セッションノート作成 |
| タスク完了 | 成果物と学びを記録 |
| セッション終了 | 次回用ノート作成 |
| 明示的依頼 | 即座に圧縮実行 |

## maintenance サブモード

pce-memory に保存された Claim の品質を維持・改善する。

### 実行フロー

```
1. 孤立検出 (Orphan Detection)
   → 参照されていない Claim を特定
   → Source が削除/移動されたClaim を検出

2. 矛盾解決 (Contradiction Resolution)
   → 矛盾する Claim ペアを検出
   → 正しい方を残し、誤りを SUPERSEDES で置換

3. 品質スコアリング (Quality Scoring)
   → 正確性・鮮度・重複率・矛盾数を計測
   → 健全性レポート出力

4. フィードバック統合 (Feedback Integration)
   → positive/negative/delete シグナル適用
   → Claim の昇格/降格/削除を実行
```

### 問題タイプと対応

| 問題タイプ | 緊急度 | 推奨アクション |
|-----------|--------|---------------|
| 不正確 (Incorrect) | 高 | 即時修正または削除 |
| 矛盾 (Contradictory) | 高 | 解決して片方を削除 |
| 古い (Outdated) | 中 | SUPERSEDES で置換または削除 |
| 重複 (Duplicate) | 中 | 統合して1つに |
| 不要 (Unnecessary) | 低 | 削除検討 |

### メンテナンスパターン

**パターン A: 単純削除**
```
pce_memory_feedback({
  claim_hash: "sha256:...",
  signal: "delete",
  note: "事実と異なる: <理由>"
})
```

**パターン B: 置換 (Supersede)**
```
# 1. 新しい Claim を作成
pce_memory_upsert({ text: "修正された主張", ... })

# 2. SUPERSEDES 関係を登録
pce_memory_upsert_relation({
  src_id: "claim-new", dst_id: "claim-old", type: "SUPERSEDES"
})

# 3. 古い Claim に negative feedback
pce_memory_feedback({ claim_hash: "sha256:...", signal: "negative" })
```

**パターン C: 統合 (Merge)**
重複する複数の Claim を1つに統合し、元の Claim すべてに SUPERSEDES 関係を設定。

**パターン D: 矛盾解決**
正しい Claim に positive feedback、誤った Claim に delete feedback。

### 品質指標

| 指標 | 良好 | 要注意 | 問題 |
|------|------|--------|------|
| 正確性 | 100% | 95-99% | <95% |
| 重複率 | 0% | 1-5% | >5% |
| 鮮度（30日以内更新） | >80% | 50-80% | <50% |
| 矛盾 | 0件 | 1-2件 | >2件 |

## 実行フロー（record サブモード）

```
Collect (Phase 1)
  → observe(Claim Schema, source auto-tag)
    → Verify (Phase 2)
      → Codex cross-check + hash validation
      → Epistemic Auto-Downgrade 適用
        → Structure (Phase 3)
          → 3層メモリへ配置 (KEEP/SUMMARIZE/DISCARD)
            → Transfer (Phase 4)
              → 引き継ぎドキュメント生成
```

フェーズは必要に応じて個別実行も可能。ユーザーの要求に応じて適切なフェーズから開始する。

## References

- [pce-memory API仕様](references/pce_memory_api.md) - observe/upsert/activate/feedbackの全パラメータ。APIの詳細が必要な時に参照
- [引き継ぎドキュメント例](references/transfer_example.md) - Phase 4の具体的な出力例。初回の引き継ぎ作成時に参照
- [Claim Schema仕様](../eld/references/claim-schema.md) - Claim の構造定義と検証ルール

## Scripts

- `scripts/scan_project.py` - プロジェクト構造スキャン（Phase 1-B）
- `scripts/validate_claims.py` - ハッシュベースclaim検証（Phase 2）

## 品質原則

1. **Epistemic Humility**: 推測を事実として扱わない。`unknown`と言う勇気を持つ
2. **Evidence First**: 因果と証拠を中心にする
3. **Source of Truth**: 真実は常に現在のコード。要約はインデックス
4. **Minimal Change**: 最小単位で変更し、即時検証する
5. **Auto-Downgrade**: ソース変更時は自動降格。鮮度は自分で守れない
