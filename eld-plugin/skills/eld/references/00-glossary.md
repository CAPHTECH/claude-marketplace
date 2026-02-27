# ELD統一語彙（Glossary）

Evidence-Loop Development v2.3で使用する統一概念の定義。

## 核心概念

### Evidence Pack（証拠パック）
変更の正当性を証明する一式の証拠。PRの中心は「結論」ではなく「因果と証拠」。

**構成要素**:
- 因果関係（Causality）: なぜこの変更が目的を達成するか
- 証拠の梯子（Evidence Ladder）: L0〜L4の段階的検証
- Evaluator Quality（E0〜E3）: 検証手段の品質
- Law/Term整合性チェック
- 影響範囲（Impact Graph）

### Epistemic Status（認識論的状態）
情報の確実性を明示するための3段階分類。

| Status | 意味 | 使用場面 |
|--------|------|----------|
| **verified** | コードまたはテストで確認済み | 根拠付きの回答 |
| **inferred** | 構造や慣習から推論 | パターンベースの判断 |
| **unknown** | 確認不能/要調査 | 正直な不明表明 |

**絶対ルール**: 推測を事実として扱わない。`unknown`を言う勇気を持つ。

**自動降格ルール（v2.3）**:
- `verified` → `inferred`: 出典ファイルが変更された場合（last_verified_atが古い）
- `inferred` → `unknown`: TTL超過した場合
- `unknown`は手動で再検証するまで昇格しない

**出典必須化（v2.3）**:
- `verified`は必ず`source`フィールド（file:line / test_name / commit_hash）を持つ
- `source`なしの`verified`は自動的に`inferred`に降格

### Source Auto-Tagging（出典自動タグ付け）
claimの出典を自動的にタグ付けする仕組み。

**タグ形式**:
- `file:<path>:<line>` - ソースコードの行
- `test:<test_name>` - テストケース名
- `commit:<hash>` - コミットハッシュ
- `review:<reviewer>` - レビュアー名

### Evidence Ladder（証拠の梯子）
証拠の強度を示す5段階。L0だけで完了扱いしない。

| Level | 内容 | 備考 |
|-------|------|------|
| L0 | 静的整合（型/lint） | **ここで完了扱いしない** |
| L1 | ユニットテスト | Law/Termの観測写像の最小 |
| L2 | 統合テスト・再現手順 | 境界越えの因果 |
| L3 | 失敗注入/フェイルセーフ | 違反時動作の確認 |
| L4 | 本番Telemetry | 実運用でのLaw違反検知 |

### Evaluator Quality（検証者品質）
検証手段の品質を示す4段階（v2.3新設）。

| Level | 内容 | 説明 |
|-------|------|------|
| E0 | テストなし/手動のみ | 再現性なし |
| E1 | テスト存在（カバレッジ不問） | 自動検証あり |
| E2 | changed-lines coverage ≥ 80% OR mutation score ≥ 60% | 品質保証あり |
| E3 | E2 + 独立レビュー(別担当/別AIモデル) + 汚染チェック記録 | 最高品質 |

**Severity↔E要件**:
- S0 + セキュリティ = E3必須
- S1 = E2必須
- S2-S3 = E1必須

### Impact Graph（影響グラフ）
変更の影響範囲を構造化した依存関係グラフ。

**構成要素**:
- シンボル依存（関数/クラス/型の呼び出し関係）
- 設定依存（環境変数/設定ファイルの参照）
- データ依存（DB/外部API/ファイル）
- 境界依存（入出力インターフェース）

**ツール**:
- `deps_closure`: コード依存関係
- `context_bundle`: ゴールベースの関連コード検索

### Predict-Light（予測ゲート）
変更の影響度を自動判定し、適切な検証深度を決定するゲート機構（v2.3新設）。

**P0/P1/P2段階**:
| Level | 判定条件 | 検証深度 |
|-------|----------|----------|
| P0 | P1/P2に該当しない | 3行要約のみ |
| P1 | 複数ファイル変更 / テスト未カバー領域 / 外部依存変更 | 影響リスト+停止条件 |
| P2 | 公開API変更 / DB変更 / 認証認可変更 / 課金ロジック変更 | フル影響分析+段階化計画 |

**ゲート方式**: Change前に自動判定。Manual overrideあり。週次監査で誤分類対応。

### Spec Gate（仕様ゲート）
Specフェーズで仕様の完全性を確認するゲート（v2.3新設）。

**判定基準**:
- Law/Term Cardが定義されている
- Link Mapが更新されている
- S0/S1のGrounding計画がある

---

## Law/Term概念

### Law（法則）
ビジネス上の「守るべき条件」を明文化したもの。

**分類**:
| Type | 説明 | 例 |
|------|------|-----|
| **Invariant** | 常に成り立つ不変条件 | 在庫 ≥ 0 |
| **Pre** | 操作の前提条件 | 注文量 > 0 |
| **Post** | 操作の事後条件 | 支払後に確認メール送信 |
| **Policy** | ビジネスルール | 返品は30日以内 |

**重要度（Severity）**:
- S0: Critical（違反=即障害）
- S1: High（違反=重大な不整合）
- S2: Medium（違反=軽微な不整合）
- S3: Low（違反=ベストプラクティス逸脱）

### Term（用語）
ドメインで使う語彙を運用可能に固定したもの。

**分類**:
| Type | 説明 | 例 |
|------|------|-----|
| **Entity** | 業務対象 | User, Order, Product |
| **Value** | 値オブジェクト | OrderQuantity, Email |
| **Context** | 使用文脈 | 認証済みユーザー |
| **Boundary** | 境界オブジェクト | APIリクエスト/レスポンス |

### Link Map（連結表）
Law ↔ Term の相互参照関係。孤立を防ぐ。

**ルール**:
- すべてのLawは参照するTermを持つ
- S0/S1のTermは関連Lawを最低1つ持つ
- 孤立したLaw/Termは警告対象

### Grounding（接地）
Lawを検証可能・観測可能にする仕組み。

| 種別 | 説明 | 例 |
|------|------|-----|
| **検証（Verification）** | テスト/実行時チェック | Unit Test, Runtime Assert |
| **観測（Observation）** | テレメトリ/ログ/イベント | Metrics, Log, Alert |

---

## Claim Schema（v2.3新設）

### Claim（主張）
知識ベースに保存される最小単位の主張。出典と鮮度を持つ。

```json
{
  "claim_id": "string",
  "content": "string",
  "source": ["file:line | test_name | commit_hash"],
  "epistemic_status": "verified | inferred | unknown",
  "last_verified_at": "ISO8601",
  "ttl": "duration",
  "importance": "S0 | S1 | S2 | S3"
}
```

**validation rules**:
- `verified`は`source`が1つ以上必須
- `S0/S1`は`DISCARD`不可
- `ttl`超過で自動降格

---

## Context Engineering（v2.3新設）

### 動的メモリポリシー
3層メモリの管理ポリシー。重要度と鮮度に基づくアクション。

| アクション | 条件 | 対象 |
|-----------|------|------|
| **KEEP** | 高重要度 + 高鮮度 | Long-term保持 |
| **SUMMARIZE** | 高重要度 + 低鮮度 | 要約してLong-term |
| **DISCARD** | 低重要度 + 低鮮度 | 破棄（S0/S1はDISCARD不可） |

**鮮度**: `last_verified_at`からの経過時間（客観的指標）

### 3層メモリモデル

| Layer | 内容 | TTL | scope |
|-------|------|-----|-------|
| **Working** | 現セッションの作業コンテキスト | session終了まで | `session` |
| **Short-term** | 最近のclaim、まだ検証途中 | 24h | `session` |
| **Long-term** | 検証済みclaim、ADR、Law/Term | 無期限（鮮度チェック付き） | `project` |

---

## Review Hybrid（v2.3新設）

### Artifact-Based Review
PRをアーティファクト（Evidence Pack、テスト結果、カバレッジ）で評価するレビュー方式。多くのPRはこの方式で十分。

### 行レビュー必須領域
以下の領域はArtifact-Based Reviewに加え、コード行単位の詳細レビューが必須:
- セキュリティ（認証/認可/暗号化）
- 並行処理（ロック/トランザクション/競合）
- 永続化（DBマイグレーション/スキーマ変更）
- 認証（トークン/セッション管理）
- マイグレーション（データ移行/後方互換）
- 課金（金額計算/決済処理）

---

## Contract概念

### Issue Contract（ローカル契約）
Issue単位の局所的な契約。

**構成要素**:
- 目的（Goal）: 何を達成したいか
- 不変条件（Invariants）: 変更してはいけないこと
- 物差し（Acceptance Criteria）: 完了を判定する観測可能な基準
- 停止条件（Stop Conditions）: これが発生したら追加計測/スコープ縮小

### Global Law（グローバル法則）
プロジェクト全体で守るべき法則（Law Card/Term Card）。

---

## 身体図概念

### Body Map（身体図）
コードを構造と依存のネットワークとして持つ内部地図。

**レイヤー**:
- シンボル（関数/クラス/型）
- 設定（環境変数/設定ファイル）
- データ（DB/外部API）
- 境界（入出力インターフェース）

### 触診（Palpation）
身体図を更新するための探索行為。

**目的別ツール選択**:

| 目的 | ツール | 備考 |
|------|--------|------|
| 特定キーワード検索 | `Grep` | 正規表現対応、高速 |
| ファイルパターン検索 | `Glob` | `**/*.ts` 等 |
| 定義・参照追跡 | `LSP` / `serena` | 言語理解に基づく |
| シンボル検索・編集 | `serena` | LSP + シンボル単位操作 |
| 特定ファイル読み込み | `Read` | パス既知時 |
| 意味的関連探索 | `kiri context_bundle` | セマンティック検索 |
| キーワードファイル検索 | `kiri files_search` | 曖昧な検索向け |
| 依存関係分析 | `kiri deps_closure` | 影響範囲特定 |
| 詳細取得 | `kiri snippets_get` | 範囲指定読み込み |
| 複雑な調査 | `Task (Explore)` | 並列探索 |

**serena MCP**（`.serena/project.yml`存在時）:
- `find_symbol`: シンボル検索
- `find_referencing_symbols`: 参照元シンボル検索
- `replace_symbol_body`: シンボル単位での置換

---

## 知識管理概念

### pce-memory 3層構造

| Layer | 内容 | TTL | scope |
|-------|------|-----|-------|
| **Working** | 現セッションの作業コンテキスト | session終了まで | `session` |
| **Short-term** | 最近のclaim、まだ検証途中 | 24h | `session` |
| **Long-term** | 検証済みclaim、ADR、Law/Term | 無期限（鮮度チェック付き） | `project` |

### Context Delta（文脈差分）
作業中に発生した知見・決定の差分。

**収集対象**:
- 意思決定の痕跡（なぜその選択をしたか）
- 学び・パターン（今後に活かせること）
- 再発防止策（追加したテスト/不変条件）

### Staleness Check（鮮度チェック）
記憶の鮮度を確認する仕組み。

1. `last_verified_at` を確認
2. TTLと比較
3. 超過なら自動降格（verified→inferred→unknown）
4. S0/S1はDISCARD不可、SUMMARIZEに回す

---

## 失敗パターン

### Epistemic（認識論的失敗）
- 推測を事実として扱う
- `unknown`と言う勇気がない
- 要約を真実として扱う
- sourceなしでverifiedを主張する（v2.3: 自動降格で防御）

### Grounding（接地の失敗）
- L0（静的整合）だけで完了扱い
- テストなしでLawを宣言
- 観測手段なしで本番投入
- Evaluator Qualityを考慮しない（v2.3: E要件で防御）

### Structure（構造的失敗）
- 名辞インフレ（Termだけ増えてLawがない）
- 関係スープ（Lawだけ増えて語彙が曖昧）
- Law/Termの孤立

### Safety（安全性の失敗）
- 参照がないから安全と判断（DI/生成/設定駆動を見落とす）
- 表層エラーを消すための無理なキャスト
- 停止条件なしで突き進む
