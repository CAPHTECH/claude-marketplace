# ELD PR Template

ELD (Evidence-Loop Development) v2.3 のPR & Evidence Pack雛形。

## PR Description

```markdown
## Summary
<!-- 何を変更したか。1-3行で -->


## Related Issue
closes #XXX


## Change Type
- [ ] 新機能（New Feature）
- [ ] バグ修正（Bug Fix）
- [ ] リファクタリング（Refactoring）
- [ ] ドキュメント（Documentation）
- [ ] その他:
```

---

## Predict-Light 要約（v2.3）

```markdown
## Predict-Light判定
- レベル: P0 / P1 / P2
- 判定理由:
- Manual Override: なし / あり（理由: ）
```

---

## Evidence Pack（証拠パック）

**PRの中心は「結論」ではなく「因果と証拠」**

```markdown
## 因果関係（Causality）
<!-- なぜこの変更が目的を達成するか -->


## 証拠の梯子（Evidence Ladder）

### L0: 静的整合
- [ ] 型チェック通過
- [ ] lint通過
- [ ] 依存関係解決

### L1: ユニットテスト
<!-- Law/Termの観測写像 -->
- [ ] テスト名: `test_xxx`
  - 検証内容:
  - 結果: Pass/Fail

### L2: 統合テスト・再現手順
<!-- 境界越えの因果 -->
- [ ] テスト名/手順:
  - 検証内容:
  - 結果:

### L3: 失敗注入/フェイルセーフ（該当する場合）
<!-- 違反時動作の確認 -->
- [ ] シナリオ:
  - 期待動作:
  - 実際の動作:

### L4: 本番Telemetry（該当する場合）
<!-- 実運用での観測 -->
- [ ] メトリクス名:
  - 観測結果:


## 証拠レベル達成
<!-- L0だけなら"未完了" -->
- 達成レベル: L0 / L1 / L2 / L3 / L4
- 理由:
```

---

## Evaluator Quality（v2.3）

```markdown
## 検証者品質
- 達成レベル: E0 / E1 / E2 / E3
- changed-lines coverage: ___%
- mutation score: ___% (該当する場合)
- 独立レビュー: なし / あり（レビュアー: ）
- 汚染チェック: なし / あり

## Severity↔E要件チェック
- [ ] S0+セキュリティ → E3達成
- [ ] S1 → E2達成
- [ ] S2-S3 → E1達成
```

---

## Review Hybrid分類（v2.3）

```markdown
## レビュー方式
- [ ] Artifact-Based Review のみ
- [ ] Artifact-Based + 行レビュー必須

## 行レビュー必須領域（該当にチェック）
- [ ] セキュリティ（認証/認可/暗号化）
- [ ] 並行処理（ロック/トランザクション/競合）
- [ ] 永続化（DBマイグレーション/スキーマ変更）
- [ ] 認証（トークン/セッション管理）
- [ ] マイグレーション（データ移行/後方互換）
- [ ] 課金（金額計算/決済処理）
```

---

## Law/Term整合性チェック

```markdown
## 関連Law
| Law ID | 接地状況 | Evidence Level | Evaluator Quality |
|--------|----------|----------------|-------------------|
| LAW-xxx | 接地済/未接地 | L0-L4 | E0-E3 |


## 関連Term
| Term ID | 境界検証 | 観測手段 |
|---------|----------|----------|
| TERM-xxx | 検証済/未検証 | テスト名/実装箇所 |


## 孤立チェック
- [ ] すべてのLawが参照するTermを持つ
- [ ] 重要なTermが関連Lawを持つ
- [ ] 孤立した定義がない
```

---

## 影響範囲（DCCA）

```markdown
## 変更ファイル
| ファイル | 変更内容 | 影響範囲 |
|----------|----------|----------|
| `path/to/file.ts` | | |


## 依存元への影響
<!-- deps_closure inbound結果 -->
-


## 意図しない影響
<!-- あれば記載 -->
- なし / あり:
```

---

## Context Delta（PCE）

```markdown
## 意思決定の痕跡
<!-- なぜその選択をしたか -->
- 決定:
- 理由:
- 却下した代替案:


## 学び・パターン
<!-- 今後に活かせること -->
-


## 再発防止
<!-- 追加したテスト/不変条件 -->
-
```

---

## レビューチェックリスト

### レビュアー向け
- [ ] Evidence Packが揃っている（L0以上）
- [ ] Evaluator Qualityが要件を満たしている
- [ ] Law/Termの孤立がない
- [ ] 影響範囲が明確
- [ ] 行レビュー必須領域を確認した
- [ ] 意図しない副作用がない
- [ ] Context Deltaが記録されている

### 作成者向け
- [ ] Issue Contractの物差しを満たしている
- [ ] テストが追加/更新されている
- [ ] 停止条件に該当する事象がない
- [ ] Predict-Light判定が記録されている
