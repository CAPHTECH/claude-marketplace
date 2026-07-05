---
name: eld-ground
context: fork
argument-hint: "verify | review | full (default: full)"
description: ELD v2.3 接地検証+PRレビュー統合スキル。2軸評価（Grounding Level G0-G4 × Evaluator Quality E0-E3）+TDD統制。verify: Law/Term接地チェック+完成度確認。review: PRレビュー（Artifact-Based + 行レビュー必須領域）。full: verify+review一括実行。使用タイミング: PR作成前の接地確認、PRレビュー、「Groundingチェックして」「PRレビューして」、Law/Term追加後の接地完了確認。
---

# ELD Ground: Verify + Review

## Purpose

実装の **接地検証（Grounding Verify）** と **PRレビュー（PR Review）** を統合したスキル。
2軸評価モデル（Grounding Level × Evaluator Quality）により、検証の品質を構造的に保証する。

---

## $ARGUMENTS

| Argument | Description | Behavior |
|----------|-------------|----------|
| `verify` | Law/Term接地チェック + 完成度確認 | Phase A-C を実行 |
| `review` | PRレビュー（Artifact-Based + 行レビュー必須領域） | Review Hybrid を実行 |
| `full` | verify + review 一括実行 **(default)** | Phase A-C → Review Hybrid を順次実行 |

引数省略時は `full` として動作する。

---

## 2-Axis Evaluation Model

### Grounding Level（接地レベル）

| Level | Name | Definition |
|-------|------|------------|
| **G0** | No Evidence | 根拠なし。主張のみ |
| **G1** | Anecdotal | 個別事例・経験則のみ |
| **G2** | Documented | ドキュメント・設計書に記載あり |
| **G3** | Tested | テストコードで検証済み |
| **G4** | Proven in Production | 本番環境で実証済み |

### Evaluator Quality（評価者品質）

| Level | Name | Definition |
|-------|------|------------|
| **E0** | Unchecked | 未レビュー |
| **E1** | Self-Checked | 実装者自身によるセルフチェック |
| **E2** | Peer-Reviewed | 同等スキルの他者によるレビュー |
| **E3** | Expert-Reviewed | ドメインエキスパートによるレビュー |

### Severity × Evaluator Quality Requirements

| Severity | 必要Evaluator Quality | 備考 |
|----------|----------------------|------|
| **S0 + security** | **E3** | セキュリティ関連の最重要変更は専門家レビュー必須 |
| **S1** | **E2** | 重要な変更はピアレビュー必須 |
| **S2** | **E1** | 中程度の変更はセルフチェック以上 |
| **S3** | **E1** | 軽微な変更はセルフチェック以上 |

この要件を満たさない場合、Ground結果は **不合格** とする。

---

## TDD統制

TDDサイクル（RED-GREEN-REFACTOR）とテストなし実装の防止を、Law Severityに応じて強制する。

### Law Severity別Evidence要件

| Severity | L1（ユニット） | L2（統合） | L4（本番Telemetry） |
|----------|---------------|-----------|---------------------|
| S0 | 必須 | 必須 | 必須 |
| S1 | 必須 | 推奨 | 推奨 |
| S2 | オプション | - | 推奨 |

S0/S1 LawはL1テストなしで実装完了扱いにしない。

### テストなきコミット禁止

該当Severityの要件を満たさない場合、コミットを拒否する:
- 変更コードに対応するテストが存在するか
- すべてのテストが成功しているか
- カバレッジが低下していないか

### RED状態の時間制限

| 経過時間 | 判定 | 対応 |
|---------|------|------|
| 5分以内 | 正常 | 実装を続行 |
| 5-15分 | 警告 | 設計の見直しを提案 |
| 15分超 | 停止 | タスクを原子化（5-10分単位）して再スタート |

### コードへの接地ルール

- **モデルベーステスト**: 状態を持つLawには、ランダム操作列に対して不変条件を毎ステップ検証するモデルベーステストを1本置く（手選びの例では到達しない状態を踏むため）。設計手順は /systematic-test-design のstate-machineプロパティを参照（delivery-plugin導入時）。
- **契約コメント**: Law Cardの事前・事後・不変条件は、対応する論理式（Formal-ish）をコメントとして実装関数のシグネチャ近傍に残す（カードとコードの接地）。
- **実行時アサーションの抑制**: 実行時アサーションは「破られたらデータ破壊につながる不変条件」のみに限定する。全Lawをassert化しない。

---

## Verify Mode

### Phase A: Grounding Check

Law/Termに対する実装の接地状態を検証する。

#### A-1. Law接地チェック

```
For each Law in eld/laws/:
  1. Lawの要求事項を抽出
  2. 対応する実装箇所を特定
  3. Grounding Levelを判定（G0-G4）
  4. 未接地（G0-G1）のLawを検出 → 要対応リストに追加
```

#### A-2. Term接地チェック

```
For each Term in eld/terms/:
  1. Termの定義を確認
  2. コード内での使用箇所を検索
  3. 定義と実装の一致度を検証
  4. 不一致・未使用Termを検出 → 要対応リストに追加
```

#### A-3. 接地マトリクス出力

```markdown
### Grounding Matrix

| Law/Term | Grounding Level | 接地箇所 | Gap |
|----------|-----------------|---------|-----|
| {Law/Term名} | G{n} | {ファイル:行} | {未接地の場合の説明} |
```

### Phase B: Output Evaluation

実装成果物の品質を2軸で評価する。

#### B-1. Grounding Level評価

各変更ファイルについて:
- テストの有無と品質 → G3判定の基準
- ドキュメントとの整合性 → G2判定の基準
- 本番実績の有無 → G4判定の基準

#### B-2. Evaluator Quality評価

```markdown
### Output Evaluation

| 対象 | Grounding Level | Evaluator Quality | Severity | 要件充足 |
|------|-----------------|-------------------|----------|---------|
| {ファイル/モジュール} | G{n} | E{n} | S{n} | {OK/NG} |
```

#### B-3. Gap Analysis

要件を満たさない項目について:
- 現在の状態と必要な状態のギャップを明示
- 改善アクションを具体的に提示

### Phase C: Pre-Completion

完成度の最終確認。

#### C-1. 完成度チェックリスト

- [ ] すべてのLawがG2以上で接地されている
- [ ] すべてのTermが定義通りに使用されている
- [ ] Severity × Evaluator Quality要件を全項目で充足
- [ ] 停止条件に該当する項目がない
- [ ] 未解決のGapが残っていない

#### C-2. 完成度スコア

```
完成度 = (接地済みLaw/Term数) / (全Law/Term数) × 100%
```

- 100%: 完全接地。Ground合格。
- 80-99%: 条件付き合格。残Gapを明示して判断を仰ぐ。
- 80%未満: 不合格。Gapリストを返却して停止。

---

## Review Mode

### Review Hybrid

PRレビューを **Artifact-Based Review** と **Line Review** のハイブリッドで実施する。

#### Artifact-Based Review（全PR共通）

すべてのPRに対してデフォルトで実施する成果物ベースのレビュー。

##### Compile Phase

```
1. PR差分を取得（git diff base...head）
2. 変更ファイルを分類:
   - 新規追加 / 修正 / 削除
   - ファイル種別（コード / テスト / 設定 / ドキュメント）
3. 変更の意図をPRタイトル・説明から抽出
4. 関連するLaw/Termを特定
```

##### Execute Phase

```
1. アーキテクチャ整合性チェック:
   - 既存パターンとの一貫性
   - 依存関係の方向性
   - モジュール境界の尊重

2. Law/Term接地チェック（verify modeのPhase A簡易版）:
   - 新規/変更コードが既存Law/Termに違反していないか
   - 新たなLaw/Termの追加が必要か

3. テスト充足度チェック:
   - 変更に対応するテストの有無
   - テストのカバレッジと品質

4. 設計品質チェック:
   - 命名の一貫性
   - 責務の分離
   - エラーハンドリング
   - ログ・可観測性
```

##### Capture Phase

```markdown
### Artifact-Based Review Result

| # | Category | Finding | Severity | Suggestion |
|---|----------|---------|----------|------------|
| 1 | {カテゴリ} | {発見事項} | S{n} | {改善提案} |

**Overall Assessment**: {APPROVE / REQUEST_CHANGES / COMMENT}
```

#### Line Review（必須領域）

以下の領域に該当する変更は、**行単位の詳細レビュー**を必須とする。

| 必須領域 | 対象パターン | レビュー観点 |
|---------|------------|-------------|
| **Security** | 認証・認可、入力検証、暗号化、シークレット管理 | 脆弱性、インジェクション、情報漏洩 |
| **Concurrency** | 並行処理、ロック、非同期、キュー | 競合状態、デッドロック、データ整合性 |
| **Persistence** | DB操作、ファイルI/O、キャッシュ | データ損失、整合性、パフォーマンス |
| **Auth** | 認証フロー、セッション管理、トークン | 認証バイパス、セッション固定、CSRF |
| **Migration** | DBマイグレーション、データ移行 | ロールバック可能性、データ損失リスク |
| **Billing** | 課金計算、決済連携、サブスクリプション | 計算誤り、二重課金、レース条件 |

##### Line Review Output

```markdown
### Line Review: {領域名}

**File**: {ファイルパス}

| Line | Code | Issue | Severity | Recommendation |
|------|------|-------|----------|----------------|
| L{n} | `{コード抜粋}` | {問題点} | S{n} | {改善案} |
```

#### LDE Integration Check

PRが以下のLDE（Law-Driven Engineering）要件を満たしているか確認する。

```
1. 新規機能の場合:
   - 対応するLawが存在するか
   - Termが適切に定義されているか
   - テストがLawの要求をカバーしているか

2. バグ修正の場合:
   - 原因となったLaw/Term違反を特定
   - 再発防止のためのLaw/Term追加が必要か

3. リファクタリングの場合:
   - 既存のLaw/Term接地を破壊していないか
   - 接地状態が改善されているか
```

```markdown
### LDE Integration

| Check | Status | Detail |
|-------|--------|--------|
| Law Coverage | {OK/NG/N/A} | {説明} |
| Term Consistency | {OK/NG/N/A} | {説明} |
| Test-Law Alignment | {OK/NG/N/A} | {説明} |
```

---

## Full Mode

`full` モード（デフォルト）は以下を順次実行する:

```
1. Verify Mode 実行
   ├── Phase A: Grounding Check
   ├── Phase B: Output Evaluation
   └── Phase C: Pre-Completion
2. Review Mode 実行
   ├── Artifact-Based Review (Compile → Execute → Capture)
   ├── Line Review (必須領域のみ)
   └── LDE Integration Check
3. 統合レポート出力
```

### 統合レポート

```markdown
## ELD Ground Report

### Summary
- **Verify**: {PASS/CONDITIONAL/FAIL} (完成度: {n}%)
- **Review**: {APPROVE/REQUEST_CHANGES/COMMENT}
- **Grounding Level Range**: G{min}-G{max}
- **Evaluator Quality**: E{n}

### Critical Findings
{S0-S1の発見事項をリスト}

### Action Items
- [ ] {必須対応項目}

### Detailed Results
{verify/reviewの詳細結果を展開}
```

---

## References

- 接地チェックリスト詳細: [checklist-detailed.md](references/checklist-detailed.md)
- Evidence Pack仕様: [evidence-pack-spec.md](references/evidence-pack-spec.md)
- CI統合ガイド: [ci-integration.md](references/ci-integration.md)
- 2軸評価モデル詳細: `eld/references/50-ground.md`

---

## Quality Principles

1. **Evidence over Opinion**: 主観的判断ではなく、証拠（テスト結果、ドキュメント、本番データ）に基づいて評価する。
2. **Severity-Proportional Rigor**: 重大度に比例した検証深度を適用する。S0は最高品質の検証を、S3は効率的な確認を。
3. **Grounding Completeness**: すべてのLaw/Termが実装に接地されていることを確認する。未接地は明示的にGapとして報告する。
4. **Review Transparency**: レビュー結果はすべて構造化された形式で出力し、判断根拠を追跡可能にする。
5. **LDE Alignment**: すべての変更がLaw-Driven Engineeringの原則に沿っていることを確認する。

---

## Stop Conditions

以下の条件に該当した場合、即座に作業を停止し報告する。

| ID | 条件 | 対応 |
|----|------|------|
| S-GND-01 | S0 + security の発見事項が E3 未満の状態で存在 | 専門家レビューを要求して停止 |
| S-GND-02 | Law接地率が 50% 未満 | 設計の根本的見直しを提案して停止 |
| S-GND-03 | DBマイグレーションにロールバック手順がない | ロールバック手順の追加を要求して停止 |
| S-GND-04 | 認証・認可の変更にテストがない | テスト追加を要求して停止 |
| S-GND-05 | 課金ロジックの変更で二重課金リスクが検出された | 即座に停止し、リスク分析を報告 |
| S-GND-06 | verify不合格（完成度 80% 未満）の状態でreviewに進もうとした | verifyのGap解消を優先 |
| S-GND-07 | PRの差分取得に失敗、またはベースブランチが不明 | 情報の確認を要求して停止 |

---

## Execution Flow

```
引数解析 → モード決定（verify / review / full）
  │
  ├─ verify ─→ Phase A → Phase B → Phase C → 結果出力
  │
  ├─ review ─→ Artifact-Based Review → Line Review(必須領域) → LDE Check → 結果出力
  │
  └─ full ───→ verify実行 → 合格判定 → review実行 → 統合レポート出力
                              │
                              └─ 不合格 → S-GND-06停止条件適用
```
