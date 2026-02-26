---
name: eld-ground-verify
context: fork
description: |
  ELD接地検証の統合スキル。Law/Termの接地チェック、生成物の品質・Law整合性評価、Evidence Pack完全性・孤立検出・Evidence Ladder達成確認をPR前に一括実行する。使用タイミング: PR作成前の接地確認、「Grounding Checkして」「品質チェックして」「完成度を確認して」、Law/Term追加後の接地完了確認
---

# ELD Ground Verify

Law/Termの接地検証、生成物の品質評価、PR前の完成度確認を一括で実行する。

## 検証の3フェーズ

```
Phase A: 接地検証 → Phase B: 出力評価 → Phase C: 完成度確認
   Law/Term接地          品質・Law整合性       Evidence Pack・孤立・Ladder
```

---

## Phase A: 接地検証（Grounding Check）

Law/Termの検証手段・観測手段が設定されているか確認する。

### 接地要件マトリクス

| 重要度 | Law検証手段 | Law観測手段 | Term境界検証 | Term観測 |
|--------|------------|------------|-------------|---------|
| S0 | **必須** (Test + Runtime) | **必須** (Telemetry全量) | **必須** (Validation + Normalization) | **必須** |
| S1 | **必須** (Test or Runtime) | **必須** (Telemetry) | **必須** (Validation or Normalization) | **必須** |
| S2 | 推奨 | 推奨 | 推奨 | 推奨 |
| S3 | 任意 | 任意 | 任意 | 任意 |

### 検証プロセス

#### Step 1: Catalog読み込み

`docs/lde/law-catalog.md` と `docs/lde/vocabulary-catalog.md` から全Law/Termを取得する。

#### Step 2: Law接地チェック

各Law IDについて以下を確認:

```yaml
law_grounding_check:
  law_id: LAW-xxx
  severity: S0 | S1 | S2 | S3
  verification:
    test: { exists: bool, path: <パス>, coverage: <率> }
    runtime_check: { exists: bool, type: assert | guard | validation }
  observability:
    telemetry: { exists: bool, metric: <名前> }
    log_event: { exists: bool, event_name: <名前> }
  status: PASS | FAIL | WARN
```

**チェック項目:**

| 項目 | 内容 |
|------|------|
| テスト存在 | Law IDに対応するテストがあるか |
| テスト品質 | PBTも含むか（S0/S1） |
| 実行時チェック | assert/guard/validationが実装されているか |
| カバレッジ | Law関連コードが80%以上カバーされているか |
| Telemetry | `law.<domain>.<name>.*` メトリクスが定義されているか |
| アラート | S0/S1違反時のアラートが設定されているか |

#### Step 3: Term接地チェック

各Term IDについて以下を確認:

```yaml
term_grounding_check:
  term_id: TERM-xxx
  importance: S0 | S1 | S2 | S3
  boundary_verification:
    validation: { exists: bool, method: <手法> }
    normalization: { exists: bool, method: <手法> }
  observability:
    observable_fields: { exists: bool, fields: [<名前>] }
    telemetry: { exists: bool, metric: <名前> }
  status: PASS | FAIL | WARN
```

**チェック項目:**

| 項目 | 内容 |
|------|------|
| Validation | IO境界で検証が実装されているか |
| Normalization | 正規化処理が実装されているか |
| Type Safety | Brand/Newtypeで型安全性が確保されているか |
| Observable Fields | ログ/テレメトリで観測フィールドが設定されているか |

#### Step 4: 相互拘束チェック

```yaml
mutual_constraint_check:
  orphan_laws: [<Terms欄が空のLaw>]
  orphan_terms: [<Related Lawsが空のS0/S1 Term>]
  status: PASS | FAIL
```

---

## Phase B: 出力評価（Output Evaluation）

生成物の品質とLaw整合性を評価する。

### 評価チェックリスト

```markdown
## Evaluation: [成果物名]

### 目的整合性
- [ ] Goalを達成している
- [ ] 期待する形式で出力されている
- [ ] 完了条件を満たしている

### 制約遵守
- [ ] セキュリティ要件OK
- [ ] 性能要件OK
- [ ] 禁止事項に違反なし

### パターン一貫性
- [ ] 既存パターンに準拠
- [ ] コーディング規約に準拠
- [ ] ADR決定事項と整合

### 品質基準
- [ ] テストカバレッジ >= 80%
- [ ] エラーハンドリング適切
- [ ] 必要なコメント記述済み

### Law遵守
- [ ] 関連Lawを参照済み
- [ ] Invariant違反なし
- [ ] Pre/Post条件が実装済み
- [ ] 新規Lawの接地完了
```

### Law遵守チェック

| Law Type | チェック内容 |
|----------|-------------|
| **Invariant** | 状態制約が維持されているか |
| **Pre** | 入力バリデーションが実装されているか |
| **Post** | 出力保証がアサーションされているか |
| **Policy** | ビジネスルールが正しく実装されているか |

### 評価結果の活用

| 結果 | アクション |
|------|-----------|
| 全てOK | Context Deltaとして記録し完了 |
| 軽微な問題 | 修正後に再評価 |
| 重大な問題 | 根本原因を調査し設計から見直し |

---

## Phase C: 完成度確認（Pre-Completion Verification）

PR作成前にEvidence Pack完全性、Law/Term孤立、Evidence Ladder達成レベルを確認する。

### C-1: Evidence Pack完全性

Evidence Packの4要素を検証:
- **因果マップ**: 変更の因果関係・影響範囲・データフロー
- **証拠**: テスト結果(L1-L3)、再現手順、Telemetry設定(L4)
- **影響範囲グラフ**: 変更ファイル・依存関係・波及範囲
- **Law/Term整合性**: Law/Term Card、Link Map、Grounding Map

詳細なチェック項目: [evidence-pack-spec.md](references/evidence-pack-spec.md) - Evidence Packの構成・フォーマット仕様。PR本文の構造を決めるとき参照

### C-2: Law/Term孤立チェック

Link Mapの3つの検証:
- **Law孤立**: どのTermにも参照されないLaw
- **Term孤立**: どのLawにも参照されないTerm
- **循環参照**: Law <-> Term の循環参照

### C-3: Evidence Ladder達成

| Severity | 要件 |
|----------|------|
| S0 | L1/L2/L4必須、カバレッジ100% |
| S1 | L1必須、カバレッジ80% |
| S2 | L1/L4オプション（推奨） |

### C-4: 停止条件確認

以下が発生したらPR作成を中止:
- 予測と現実の継続的乖離（想定外テスト失敗3回以上）
- 観測不能な変更の増加（Evidence Level未設定の変更）
- ロールバック線の崩壊（不可逆的な変更の検出）

### 自動検証スクリプト

```bash
bash scripts/pre-completion-check.sh
```

詳細チェックリスト: [checklist-detailed.md](references/checklist-detailed.md) - 49項目の詳細チェックリスト。手動確認やトラブルシューティング時に参照

CI/CD統合設定: [ci-integration.md](references/ci-integration.md) - GitHub Actions/GitLab CI/CircleCIへの統合方法。パイプライン構築時に参照

---

## 完了条件

すべて満たす必要がある:
- [ ] Evidence Ladder目標レベル達成
- [ ] Issue Contractの物差し満足
- [ ] Law/Termが接地している（Grounding Map確認）
- [ ] Link Mapに孤立がない
- [ ] ロールバック可能な状態

## 停止条件

以下が発生したら即座に停止し、追加計測またはスコープ縮小:
- 予測と現実の継続的乖離（想定外テスト失敗3回以上）
- 観測不能な変更の増加（物差しで検証できない変更）
- ロールバック線の崩壊（戻せない変更の発生）

---

## 出力形式

### Grounding Report

```markdown
# ELD Ground Verify Report

## Summary
- Total Laws: 25 (S0: 3, S1: 5, S2: 10, S3: 7)
- Total Terms: 18 (S0: 2, S1: 4, S2: 8, S3: 4)
- Law Grounding: 7/8 S0/S1 (87.5%)
- Term Grounding: 5/6 S0/S1 (83.3%)
- Mutual Constraint: PASS

## Phase A: Law/Term Grounding

### S0/S1 Laws
| Law ID | Severity | Test | Runtime | Telemetry | Status |
|--------|----------|------|---------|-----------|--------|
| LAW-inv-balance | S0 | PASS | PASS | PASS | PASS |
| LAW-post-payment | S0 | FAIL | FAIL | FAIL | FAIL |

### S0/S1 Terms
| Term ID | Importance | Validation | Normalization | Observable | Status |
|---------|------------|------------|---------------|------------|--------|
| TERM-order-quantity | S1 | PASS | PASS | PASS | PASS |

## Phase B: Output Evaluation
- 目的整合性: OK
- 制約遵守: OK
- Law遵守: 1件のWARN

## Phase C: Pre-Completion
- Evidence Pack: Complete
- Law/Term孤立: None
- Evidence Ladder: S0 3/3, S1 2/2
- 停止条件: OK

## Action Required
### FAIL: LAW-post-payment (S0)
- Test missing: 決済完了後の状態検証テストがない
- Runtime check missing: 事後条件のアサーションがない
- Telemetry missing: law.payment.completed.* メトリクスがない

推奨アクション:
1. tests/payment.test.ts に事後条件テストを追加
2. src/payment/service.ts に事後アサーション追加
3. src/payment/telemetry.ts にメトリクス追加
```

---

## CI/CD統合

### pre-commit hook

```bash
#!/bin/bash
changed_files=$(git diff --cached --name-only)
lde_files=$(echo "$changed_files" | grep -E "(law|term|invariant|assert)")
if [ -n "$lde_files" ]; then
  echo "LDE関連ファイルが変更されています"
  echo "$lde_files"
  echo "Grounding Map/Link Mapの更新を確認してください"
fi
```

### CI workflow

```yaml
name: eld-ground-verify
on: [pull_request]
jobs:
  ground-verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Ground Verify
        run: bash scripts/pre-completion-check.sh
```
