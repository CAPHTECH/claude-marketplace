---
name: eld-ground-pre-completion
context: fork
description: |
  PR作成前の完成前検証チェックリスト実行。
  Evidence Pack完全性、Law/Term孤立、Evidence Ladder達成レベルを体系的に確認。

  トリガー条件:
  - 「PRを作る前にチェックして」「完成度を確認して」「リリース準備チェック」
  - ELD Phase 4: Review の自動前段階
  - CI/CDでのPR前自動検証
  - 「Evidence Packを確認して」
---

# ELD Ground: Pre-Completion Verification

PR作成前の完成前検証チェックリストを実行するスキル。
Evidence Pack完全性、Law/Term孤立、Evidence Ladder達成レベルを体系的に確認し、
PRの品質を事前に保証する。

## 核心原則

1. **完了の定義の厳格性**: Issue Contractの物差しをすべて満たす
2. **Evidence First**: 証拠なき主張は不完全と判定
3. **孤立の排除**: Law/Term Link Mapに孤立がないこと
4. **観測可能性**: すべてのLawに観測写像が存在すること
5. **ロールバック可能性**: 失敗時に元に戻せること

## 検証フロー

### Phase 1: Evidence Pack完全性チェック

Evidence Packの4つの要素を検証:
- 因果マップ（変更の因果関係・影響範囲・データフロー）
- 証拠（テスト結果L1-L3、再現手順、Telemetry設定L4）
- 影響範囲グラフ（変更ファイル・依存関係・波及範囲）
- Law/Term整合性（Law/Term Card、Link Map、Grounding Map）

詳細なチェック項目: [evidence-pack-spec.md](references/evidence-pack-spec.md)

---

### Phase 2: Law/Term孤立チェック

Link Mapの3つの検証:
- Law孤立: どのTermにも参照されないLaw
- Term孤立: どのLawにも参照されないTerm
- 循環参照: Law ↔ Term の循環参照

自動検出スクリプト: [scripts/pre-completion-check.sh](scripts/pre-completion-check.sh) の `check_orphan()` 関数

---

### Phase 3: Evidence Ladder達成確認

Law Severity別の要件確認:
- **S0 Laws**: L1/L2/L4必須、カバレッジ100%
- **S1 Laws**: L1必須、カバレッジ80%
- **S2 Laws**: L1/L4オプション（推奨）

各LawのEvidence達成状況を確認し、不足レベルを検出。

詳細な確認方法: [checklist-detailed.md](references/checklist-detailed.md) Phase 3セクション

---

### Phase 4: 停止条件確認

Issue Contractの3つの標準停止条件を確認:
- 予測と現実の継続的乖離（想定外テスト失敗3回以上）
- 観測不能な変更の増加（Evidence Level未設定の変更）
- ロールバック線の崩壊（不可逆的な変更の検出）

違反時は即座に停止し、追加計測またはスコープ縮小を実施。

詳細な確認方法: [checklist-detailed.md](references/checklist-detailed.md) Phase 4セクション

---

### Phase 5: 自動検証スクリプト実行

Phase 1-4の検証を自動実行し、完了判定を行う統合スクリプト。

スクリプト実行:
```bash
bash scripts/pre-completion-check.sh
```

詳細とスクリプト本体: [scripts/pre-completion-check.sh](scripts/pre-completion-check.sh)

---

## 完了条件と不完全条件

**完了条件** (すべて満たす必要あり):
- Evidence Pack完全（因果マップ・証拠・影響範囲グラフ）
- Law/Term孤立なし（Link Map完全）
- Evidence Ladder達成（S0: L1/L2/L4、S1: L1）
- Issue Contract物差し満足
- ロールバック可能

**不完全条件** (1つでも該当で不完全):
- 上記の逆（Evidence不足、孤立存在、カバレッジ未達、停止条件発生、不可逆変更）

詳細: [checklist-detailed.md](references/checklist-detailed.md)

---

## CI/CD統合

PR作成前の自動検証として統合可能（GitHub Actions、GitLab CI、CircleCI等）。

統合例とワークフロー設定: [ci-integration.md](references/ci-integration.md)

---

## eld-ground-checkとの違い

| 観点 | eld-ground-check | eld-ground-pre-completion |
|------|------------------|---------------------------|
| **実行タイミング** | 各ステップ完了後 | PR作成直前 |
| **チェック範囲** | 単一Law/Termの接地 | Evidence Pack全体 |
| **孤立チェック** | なし | あり（全Law/Term） |
| **停止条件** | なし | あり（Issue Contract） |
| **自動化** | 手動実行 | CI/CD統合可能 |
| **完了判定** | 個別Evidenceの達成 | PR全体の完成度 |

**使い分け**:
- `eld-ground-check`: 各ステップでのEvidence達成確認（粒度: 個別Law/Term）
- `eld-ground-pre-completion`: PR作成前の最終チェック（粒度: Evidence Pack全体）

---

## 使用例

```
User: PRを作る前にチェックして

Claude:
## ELD Pre-Completion Verification

PR作成前の完成前検証を実行します。

### Phase 1: Evidence Pack完全性

因果マップ: ✓ Complete
証拠: ✓ Complete
  - L1: 10/10 tests passed
  - L2: 3/3 integration tests passed
  - L4: Telemetry configured
影響範囲グラフ: ✓ Complete
  - 変更ファイル: 5 files
  - 依存関係: 12 modules
  - 波及範囲: 予測済み

### Phase 2: Law/Term孤立チェック

Law孤立: ✓ None
Term孤立: ✓ None
循環参照: ✓ None

Link Map:
  - LAW-token-expiry ↔ TERM-access-token
  - LAW-token-signature ↔ TERM-access-token
  - LAW-session-timeout ↔ TERM-session-id

### Phase 3: Evidence Ladder達成確認

S0 Laws: ✓ 3/3 Complete
  - LAW-token-expiry: L1/L2/L4 達成
  - LAW-token-signature: L1/L2/L4 達成
  - LAW-session-timeout: L1/L2/L4 達成

S1 Laws: ✓ 2/2 Complete
  - LAW-password-min-length: L1 達成
  - LAW-username-format: L1 達成

### Phase 4: 停止条件確認

予測と現実の乖離: ✓ OK (失敗回数: 1/3)
観測不能な変更: ✓ OK (0件)
ロールバック線: ✓ OK (全変更可逆)

### Phase 5: 完了判定

**結果**: ✓ **PR作成可能**

すべての完了条件が満たされています。
PRを作成してください。
```

---

## リファレンス

- [checklist-detailed.md](references/checklist-detailed.md): 詳細チェックリスト
- [evidence-pack-spec.md](references/evidence-pack-spec.md): Evidence Pack仕様
- [ci-integration.md](references/ci-integration.md): CI/CD統合ガイド
- [pre-completion-check.sh](scripts/pre-completion-check.sh): 自動検証スクリプト

---

## 品質優先原則（Superpowers統合）

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

---

## 完了条件

- [ ] Evidence Pack完全性チェックが通過している
- [ ] Law/Term孤立が検出されていない
- [ ] Evidence Ladder目標レベルを達成している
- [ ] 停止条件が発生していない
- [ ] ロールバック可能な状態

---

## 停止条件

以下が発生したらPR作成を中止し、問題を修正:

- Evidence Pack不完全
- Law/Term孤立が存在
- Evidence Ladder目標未達成
- 停止条件が発生
- ロールバック不可能な変更が存在
