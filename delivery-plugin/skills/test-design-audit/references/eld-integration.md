# ELD統合ガイド

test-design-auditをELD（Evidence-Loop Development）と統合して使用するためのガイド。

## ELDループにおける位置づけ

```
ELD Loop: Sense → Model → Predict → Change → Ground → Record
                                              ↑
                                    test-design-audit
```

test-design-auditはELDのGroundフェーズにおいて、
Law/Termの接地（テストによる検証）を体系的に設計する。

## 統合ワークフロー

### 1. ELD Modelフェーズからの入力

test-design-auditはELDのModelフェーズで定義されたLaw/Termを入力として受け取る。

```
ELD Model → Law/Term Cards → test-design-audit Phase 1
```

**入力となるLaw/Term情報**:
- Law ID、名前、カテゴリ（Invariant/Pre/Post/Policy）
- Severity（S0-S3）
- 論理式
- 関連Term

### 2. Phase 1: REQ → Law/Term対応付け

既存の要求（REQ）を収集した後、ELDのLaw/Termと対応付ける。

```yaml
対応パターン:
  - REQ-001 → LAW-auth-valid-credential（既存Law）
  - REQ-002 → TERM-password（既存Term）
  - REQ-003 → (NEW-LAW) → /eld-modelで発見
```

**新しいLaw/Termの発見**:
テスト設計中に暗黙の法則を発見した場合は、ELDのModelフェーズに戻る。

### 3. Phase 3: Evidence Ladderの適用

カバレッジ基準にEvidence Ladderを適用する。

| Severity | 必須レベル | 推奨レベル |
|----------|------------|------------|
| S0（致命的） | L0 + L1 + L2 + L3 | L4 |
| S1（重要） | L0 + L1 + L2 | L3 + L4 |
| S2（中程度） | L0 + L1 | L2 |
| S3（低） | L0 | L1 |

### 4. Phase 4-6: テスト条件とGrounding Map

テスト条件（TCND）とテスト項目（TEST）をLaw/Termに紐付け、
Grounding Mapに反映する。

```yaml
# grounding-map.yaml
laws:
  LAW-auth-valid-credential:
    severity: S0
    verification:
      unit:
        - TEST-001
        - TEST-002
      integration:
        - TEST-010
```

### 5. Phase 5: Law接地監査

監査フェーズで`/eld-ground-verify`を使用してLaw/Termの接地状況を検証する。

```
/eld-ground-verify LAW-auth-valid-credential

結果:
✅ L0: 型チェック通過
✅ L1: Unit Test (3/3)
✅ L2: Integration Test (1/1)
❌ L3: 失敗注入テストなし
⚠️ L4: Telemetry設定済み

推奨アクション:
- L3: timeout時の動作テストを追加
```

### 6. ELD Recordフェーズへの出力

test-design-auditの結果をELDのRecordフェーズに渡す。

**出力**:
- 更新されたGrounding Map
- 新しく発見したLaw/Term候補
- テスト設計決定の記録

```
test-design-audit → Grounding Map → ELD Record → pce-memory
```

## ELDスキルとの連携

### 入力スキル（Modelフェーズ）

| スキル | 提供情報 |
|--------|----------|
| `/eld-model` | Law/Term Cardの詳細（Severity、論理式、関連Term、境界、観測写像）、Law ↔ Term の相互参照 |

### 出力スキル（Groundフェーズ）

| スキル | 受け取る情報 |
|--------|--------------|
| `/eld-ground-verify` | テスト条件とGrounding Mapの検証・テスト設計全体の評価 |

## 使用例

### 例1: 新機能のテスト設計

```
1. /eld-model で機能のLaw/Termを発見・カード化
2. /test-design-audit でテスト設計
   - Phase 1: REQとLaw/Termを対応付け
   - Phase 3: Evidence Ladderでカバレッジ基準設定
   - Phase 4-6: テスト条件・項目作成
   - Phase 5: /eld-ground-verify で接地監査
4. Grounding Mapを更新
5. /eld-record で知識を記録
```

### 例2: 既存機能のテスト改善

```
1. /eld-ground-verify で現在の接地状況を確認
2. 未達成のEvidence Ladderレベルを特定
3. /test-design-audit で追加テストを設計
   - Phase 4: 不足レベル（L2, L3等）のテスト条件を追加
   - Phase 5: Law接地監査で改善を確認
4. Grounding Mapを更新
```

## チェックリスト

### ELD統合前

- [ ] ELDのModelフェーズでLaw/Termが定義されているか
- [ ] Law/TermのSeverityが設定されているか
- [ ] Link Map（Law ↔ Term相互参照）が整備されているか

### test-design-audit実行中

- [ ] Phase 1でREQとLaw/Termを対応付けたか
- [ ] Phase 3でEvidence Ladderを適用したか
- [ ] Phase 4でテスト条件にLaw/Termを紐付けたか
- [ ] Phase 5でLaw接地監査を実施したか

### ELD統合後

- [ ] Grounding Mapが更新されているか
- [ ] 新しく発見したLaw/Termが記録されているか
- [ ] pce-memoryにテスト設計決定が記録されているか
