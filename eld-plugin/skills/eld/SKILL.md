---
name: eld
context: fork
description: |
  Evidence-Loop Development (ELD) v2.3 - 証拠で回す統合開発手法。
  5+1フェーズ（Sense → Spec → Change → Ground → Record + Predict-Light gate）で
  コード観測、Spec規範、安全な変更、知識管理を統一ループで実行する。

  トリガー条件:
  - 「ELDで進めて」「証拠ループで実装して」
  - 「コードベースを理解して」「影響範囲を分析して」（Sense）
  - 「Specを定義して」「Termをカード化して」（Spec）
  - 「安全に変更して」「証拠パックを作成して」（Change）
  - 「コンテキスト駆動で実装して」「PCEで進めて」（Record）
  - 「ELDでデバッグして」「法則視点でバグ調査して」（デバッグ）
  - 新機能開発、バグ修正、リファクタリング、障害調査
---

# Evidence-Loop Development (ELD) v2.3

**証拠で回す**統合開発手法。コードを「相互接続された意味のグラフ」として理解し、
Spec（Law/Term）で規範を定め、Predict-Light でリスクを軽量判定し、
安全な微小変更で実装し、知識を構造化して蓄積する。

## 核心原則

1. **Epistemic Humility**: 推測を事実として扱わない。`unknown`と言う勇気を持つ
2. **Evidence First**: 結論ではなく因果と証拠を中心にする
3. **Grounded Laws**: Lawは検証可能・観測可能でなければならない
4. **Minimal Change**: 最小単位で変更し、即時検証する
5. **Source of Truth**: 真実は常に「現在のコード」。要約をインデックスとして扱う

## 統一ループ（5+1フェーズ）

```
Sense → Spec → [Predict-Light gate] → Change → Ground → Record
  ↑                                                         ↓
  └──────────────────────── 循環 ←──────────────────────────┘
```

| Phase | 内容 | 参照 |
|-------|------|------|
| **Sense** | コードの事実/意図/関係を観測、身体図を更新 | `10-sense.md` |
| **Spec** | 語彙（Term）と関係（Law）を同定、カード化、Link Map管理 | `20-spec.md` |
| **Predict-Light** (gate) | リスクを P0/P1/P2 で軽量判定、High時のみ詳細分析 | `30-predict.md` |
| **Change** | 最小単位で変更、Pure/IO分離を優先、検証通過後コミット | `40-change.md` |
| **Ground** | テスト/Telemetry/再現手順で接地、Review Hybrid | `50-ground.md` |
| **Record** | Context Deltaをpce-memory/ADR/Catalogへ反映（Claim Schema） | `60-record.md` |

## 統一概念

### Evidence Pack（証拠パック）
変更の正当性を証明する一式の証拠。PRの中心。

### Epistemic Status（認識論的状態）
- **verified**: コードまたはテストで確認済み
- **inferred**: 構造や慣習から推論
- **unknown**: 確認不能/要調査

**Auto-Downgrade**: ソースファイルの hash 変更や TTL 超過で自動降格。
ソース要件: すべての Claim は source（type/path/hash/observed_at）を必須とする。

### Evidence Ladder（証拠の梯子）
| Level | 内容 | 備考 |
|-------|------|------|
| L0 | 静的整合（型/lint） | **ここで完了扱いしない** |
| L1 | ユニットテスト | Law/Termの観測写像の最小 |
| L2 | 統合テスト・再現手順 | 境界越えの因果 |
| L3 | 失敗注入/フェイルセーフ | 違反時動作の確認 |
| L4 | 本番Telemetry | 実運用でのLaw違反検知 |

### Evaluator Quality（評価者品質）
| Level | 内容 | 例 |
|-------|------|------|
| E0 | 人間の目視確認なし | 完全自動 |
| E1 | 静的解析+型チェック | lint, tsc |
| E2 | 自動テスト（L1-L2） | ユニット+統合テスト |
| E3 | 人間レビュー+本番観測 | PR Review + Telemetry |

### Predict-Light（軽量リスク判定）
| Level | 判定 | アクション |
|-------|------|-----------|
| P0 | Trivial（型修正、typo、コメント） | gate通過、即Change |
| P1 | Low-Medium（ロジック変更、新関数） | gate通過、Change + L1確認 |
| P2 | High-Critical（境界変更、データ移行） | 詳細分析、worktree隔離提案 |

### Claim Schema
すべての知識は Claim として構造化する（source auto-tag + epistemic auto-downgrade）。

### Context Engineering
3層メモリモデル（Working / Short-term / Long-term）+ 動的ポリシー（KEEP / SUMMARIZE / DISCARD）で知識の鮮度と信頼性を自動管理。

### Review Hybrid
Artifact-Based Review（証拠パック中心）+ Line Review（差分レビュー）を組み合わせた統合レビュー手法。

### Issue Contract（ローカル契約）
- 目的（Goal）
- 不変条件（Invariants）
- 物差し（Acceptance Criteria）
- 停止条件（Stop Conditions）

### Law/Term（グローバル法則）
- **Law**: ビジネス上の「守るべき条件」（Invariant/Pre/Post/Policy）
- **Term**: ドメインの語彙（Entity/Value/Context/Boundary）
- **Link Map**: Law <-> Term の相互参照。孤立禁止

詳細は `00-glossary.md` を参照。

## 開発フロー

### Phase 1: Issue（受付）

```yaml
成果物:
  - Issue Contract: 目的/不変条件/物差し/停止条件
  - 現状証拠: Senseフェーズの観測結果
  - Term/Law候補: Specフェーズの初期出力
```

**実行内容**:
0. **要件明確化** (新機能開発時):
   - `/eld-sense-requirements-brainstorming` で要件の曖昧さを対話的に解消
   - Law/Term観点、境界条件、失敗モードから体系的に質問
   - Issue Contract 下書き生成
1. `pce.memory.activate` で関連知識を活性化
2. 目的に応じたツールでコード調査（`10-sense.md` 参照）
   - 特定キーワード → `Grep`
   - 定義・参照追跡 → `LSP` / `serena`
   - シンボル検索 → `serena`（利用可能時）
   - 意味的関連探索 → `kiri context_bundle`
3. Issue Contractを作成（`issue-template.md`使用）
4. `/eld-spec` で Term/Law候補を列挙

使用スキル: `/eld-sense-requirements-brainstorming` (新機能時), `/eld-sense-activation`, `/eld-spec`

### Phase 2: Design（設計）

```yaml
成果物:
  - Law/Term Cards: 相互参照あり、孤立なし
  - Grounding Plan: 必要テスト/Telemetry（Evidence Ladder対応）
  - Change Plan: 微小変更列＋各ステップのチェック
  - Predict-Light 判定: P0/P1/P2 リスクレベル
```

**実行内容**:
1. `/eld-spec` で Law Card化（Scope/例外/違反時動作）
2. `/eld-spec-card` で Term Card化（意味/境界/観測写像）
3. `/eld-spec-link` で Link Map更新（孤立チェック）
4. `/eld-predict-light` でリスク判定（P0/P1/P2）
5. **Grounding Plan策定**（`/test-design-audit`でテスト設計）

使用スキル: `/eld-spec`, `/eld-spec-card`, `/eld-spec-link`, `/eld-predict-light`, `/test-design-audit`

### Phase 3: Implementation（実装ループ）

各ステップを同じ型で回す:

```
1. Sense   → 触るシンボル/境界/設定の身体図更新
2. Predict-Light → P0/P1/P2 リスク判定（gate）
   → P0/P1: gate通過、そのままChangeへ
   → P2: 詳細分析、worktree隔離提案
3. Change  → 最小単位で変更、Pure/IO分離を維持
           → 検証通過後にコミット（1ステップ=1コミット）
4. Ground  → テスト/Telemetryで観測写像を満たす
           → TDD強制（RED-GREEN-REFACTOR）でL1達成
5. Record  → Context Delta記録（Claim Schema準拠）
```

**Predict-Light gate**:
- P0 (Trivial): 即座にChange。型修正、typo、コメント等
- P1 (Low-Medium): Change + L1テスト確認必須
- P2 (High-Critical): 詳細影響分析 + worktree隔離環境作成

**TDD強制**:
- S0/S1 Lawは必ずL1（ユニットテスト）達成が必須
- RED（失敗テスト）→ GREEN（最小実装）→ REFACTOR（品質改善）サイクル
- テストなし実装を許さず、コミット前にEvidence L1確認

使用スキル: `/eld-predict-light`, `/eld-change-worktree`, `/eld-ground-tdd-enforcer`, `/eld-record`

**停止条件チェック**:
- 予測と現実の継続的乖離
- 観測不能な変更の増加
- ロールバック線の崩壊

### Phase 4: Review（レビュー）

```yaml
Review Hybrid:
  Artifact-Based Review:
    - 因果と証拠の整合（Evidence Pack）
    - Law/Term孤立チェック（Link Map）
    - 影響範囲のグラフ証拠
    - Evidence Ladder達成レベル
    - Evaluator Quality (E0-E3)
  Line Review:
    - 差分の行単位レビュー
    - コード品質チェック
    - セキュリティ/パフォーマンス観点
```

使用スキル: `/eld-ground`

PR作成: `pr-template.md` 使用

### Phase 5: Ops（運用）

- Telemetryで Law違反を監視
- Context Deltaを回収→構造化（Claim Schema準拠）
- 物差しの再点検
- pce-memoryへのフィードバック
- Epistemic Auto-Downgrade の定期実行

## 知識ストア

| ストア | 役割 | 内容 |
|--------|------|------|
| pce-memory | 履歴・痕跡（3層メモリ） | Claim Schema準拠、動的ポリシー管理 |
| Law/Term Catalog | 規範の正本 | Cards、Link Map、Grounding Map |
| ADR | アーキテクチャ決定 | 重要な意思決定の記録 |

### 3層メモリモデル

| Layer | 内容 | 寿命 | scope | 更新頻度 |
|-------|------|------|-------|----------|
| **Working** | 現セッションの仮説・中間結果 | セッション終了まで | `session` | 高 |
| **Short-term** | 直近タスクの決定・発見 | TTL (7-30日) | `project` | 中 |
| **Long-term** | 検証済み原則・ADR・Law/Term | 無期限 | `principle` | 低 |

### Claim Schema

```yaml
claim:
  id: "claim-<domain>-<short-name>"
  text: "主張内容"
  source:
    type: "code|test|log|human|inference"
    path: "ソースファイルパス"
    hash: "sha256:..."
    observed_at: "ISO8601"
  epistemic_status: "verified|inferred|unknown"
  ttl_days: 30
  confidence: 0.95
```

## Epistemic Status 管理

### Auto-Downgrade ルール

| 現在の状態 | トリガー | 降格先 |
|-----------|---------|--------|
| `verified` | ソース hash 変更 | `inferred` |
| `verified` | TTL 超過 (>30日) | `inferred` |
| `inferred` | ソース削除/大幅変更 | `unknown` |
| `inferred` | TTL 超過 (>60日) | `unknown` |

### Source 要件

すべての Claim は以下の source 情報を必須とする:
- `type`: ソースの種類（code/test/log/human/inference）
- `path`: ソースファイルパス（該当時）
- `hash`: ソースコンテンツの sha256 ハッシュ
- `observed_at`: 観測日時（ISO8601）

## 品質優先原則

### 核心原則

1. **Epistemic Humility**: 推測を事実として扱わない。`unknown`と言う勇気を持つ
2. **Evidence First**: 結論ではなく因果と証拠を中心にする
3. **Minimal Change**: 最小単位で変更し、即時検証する
4. **Grounded Laws**: Lawは検証可能・観測可能でなければならない
5. **Source of Truth**: 真実は常に現在のコード。要約はインデックス

### 「速さより質」の実践

- 要件の曖昧さによる手戻りを根本から排除
- テストなし実装を許さない
- 観測不能な変更を防ぐ

## 完了条件と停止条件

### 完了条件
- Issue Contractの物差しが満たされている
- Law/Termが接地している（Evidence Ladder L1以上）
- Evidence Packが揃っている
- Link Mapに孤立がない
- Evaluator Quality が目標レベル達成

### 停止条件（発生時は追加計測/スコープ縮小）
- 予測と現実の継続的乖離（想定外のテスト失敗3回以上）
- 観測不能な変更の増加（物差しで検証できない変更）
- ロールバック線の崩壊（戻せない変更の発生）

## リファレンス

### 概念定義
- `00-glossary.md` - 統一語彙

### フェーズ詳細
- `10-sense.md` - 感知フェーズ
- `20-spec.md` - Specフェーズ（Law/Term発見・カード化）
- `30-predict.md` - Predict-Lightフェーズ（軽量リスク判定）
- `40-change.md` - 変更フェーズ（コミット含む）
- `50-ground.md` - 接地フェーズ
- `60-record.md` - 記録フェーズ（Context Engineering）

### テンプレート
- `issue-template.md` - Issue Contract雛形
- `pr-template.md` - PR & Evidence Pack雛形
- `law-term-card.md` - Law/Term Card雛形
- `predict-light-template.md` - Predict-Light判定雛形
- `claim-schema.md` - Claim Schema定義
- `review-hybrid-guide.md` - Review Hybrid実施ガイド

## 使用例

```
User: ユーザー認証機能をELDで実装して

Claude:
## ELD Phase 1: Issue

### Issue Contract
- 目的: JWTベースの認証機能実装
- 不変条件: 既存APIとの後方互換性
- 物差し: 認証テスト通過 + レスポンス<200ms
- 停止条件: セキュリティ脆弱性発見時

### 現状証拠（Sense）
[verified]
- 既存認証: src/auth/legacy.ts:23-45（Basic認証）
- 関連モジュール: src/middleware/auth.ts

[unknown]
- 外部認証プロバイダとの連携状況

### Term/Law候補（Spec）
- TERM-jwt-token: JWT形式のアクセストークン（S1）
- TERM-refresh-token: リフレッシュトークン（S1）
- LAW-token-expiry: アクセストークンは1時間で失効（S0）
- LAW-refresh-validity: リフレッシュトークンは7日間有効（S1）

### Predict-Light: P1 (Low-Medium)
→ 新規機能追加、既存APIへの影響は限定的

Phase 2: Designに進みますか？
```

## デバッグへの適用

ELDの統一ループはデバッグにも適用できる。バグを「法則（Law）からの逸脱」として捉え、
証拠ループで系統的に解決する。

### デバッグループ

```
Sense → Spec → Predict-Light → Change → Ground → Record
  ↑                                                  ↓
  └──────────── 法則復元まで循環 ←────────────────────┘
```

| Phase | 通常開発 | デバッグ適用 |
|-------|----------|--------------|
| **Sense** | コード観測 | 症状の観測 + 関連法則候補の列挙 |
| **Spec** | Law/Term同定 | 破られた法則の仮説形成 + 論理式化 |
| **Predict-Light** | リスク判定 | 法則違反の伝播範囲を P0/P1/P2 で判定 |
| **Change** | 微小変更+コミット | 法則復元のための最小修正 |
| **Ground** | 接地検証 | 証拠の梯子での法則復元確認 |
| **Record** | 知識蓄積 | バグパターン + 法則違反パターン記録（Claim Schema） |

### ELD的デバッグの特徴

| 観点 | 従来 | ELD的 |
|------|------|-------|
| 視点 | 「なぜ壊れた？」 | 「どの法則が破られた？」 |
| 証拠 | ログ・スタックトレース | 法則違反の論理的証明 |
| 修正 | 症状の除去 | 法則の復元 |
| 検証 | 「動いた」 | 「法則が満たされた」（L0-L4） |
| 蓄積 | バグ票 | Law/Term Card + パターン（Claim Schema） |

詳細は `/eld-debug` スキルを参照。

## ユーティリティスキル

ELDループ内で使用する補助スキル:

### Sense（感知）
| スキル | 用途 |
|--------|------|
| `/eld-sense-activation` | アクティブコンテキスト構築 |
| `/eld-sense-planning` | タスクスコープ定義・タスク分解・並列実行最適化 |

### Spec（規範定義）
| スキル | 用途 |
|--------|------|
| `/eld-spec` | Law/Term発見・Card作成・Link Map管理 |
| `/eld-spec-discover` | Law/Term候補の自動発見 |
| `/eld-spec-card` | Term Card 詳細作成 |
| `/eld-spec-link` | Link Map更新・孤立チェック |

### Predict-Light（軽量リスク判定）
| スキル | 用途 |
|--------|------|
| `/eld-predict-light` | P0/P1/P2 リスク判定 gate |

### Change（変更・コミット）
| スキル | 用途 |
|--------|------|
| `/eld-change-worktree` | P2リスク時のworktree隔離環境 |
| `/git-commit` | ステップ完了時のコミット |

### Ground（接地・レビュー）
| スキル | 用途 |
|--------|------|
| `/test-design-audit` | **テスト設計監査（ELD統合版）** - Law/Term駆動のテスト設計 |
| `/systematic-test-design` | **体系的テスト設計** - ユニットテスト＋PBT統合 |
| `/eld-ground` | 接地検証・Review Hybrid（Artifact-Based + Line Review）・PR作成前検証 |
| `/eld-ground-tdd-enforcer` | TDD強制（RED-GREEN-REFACTOR） |
| `/eld-ground-law-monitor` | Law違反監視 |

### Record（記録）
| スキル | 用途 |
|--------|------|
| `/eld-record` | Context Delta収集・検証・構造化・知識移転（default: record） |
| `/eld-record compact` | 履歴圧縮・セッションノート作成 |
| `/eld-record maintenance` | Claim品質メンテナンス・矛盾解決 |

### Debug（デバッグ）
| スキル | 用途 |
|--------|------|
| `/eld-debug` | 法則駆動デバッグ（バグ=法則違反として分析・修正） |
