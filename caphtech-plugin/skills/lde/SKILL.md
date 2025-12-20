---
name: lde
description: |
  Law-Driven Engineering (LDE)プロジェクトのセットアップと開発ワークフローガイド。
  ビジネス上の「守るべき条件」をLawとして明文化し、実装・テスト・運用観測を統一軸で結ぶ。
  使用タイミング: (1) 新規プロジェクトでLDEを導入する時、(2) LDEの開発フェーズ（A-E）を実行する時、
  (3) トラック（Simple/Standard/Complex）を選択する時、(4) LDEチェックリストで品質確認する時
---

# Law-Driven Engineering (LDE)

## LDEとは

ビジネス上「守るべき条件」を **Law（法則）** として明文化し、実装・テスト・運用観測を同じ軸で結び、実装の一貫性と保守性を高める開発手法。

## Core定義（10行）

1. ビジネス上の「守るべき条件」を **Law** として明文化し、実装の中心に置く
2. Lawは **Invariant / Pre / Post / Policy** に分類
3. 各Lawは **Scope・Exceptions・Handling** まで定義
4. Lawは必ず **検証手段（Test/Runtime Check）** を最低1つ持つ
5. Lawは必ず **観測手段（Telemetry/Log/Event）** を最低1つ持つ
6. 実装は「Law → Pure → IO境界」に分離
7. 型はLawを補助し、不可能な状態を排除
8. 変更時は「Law変更 → 影響範囲 → 互換性 → 段階リリース」
9. メトリクスは目標ではなく **兆候（signals）** として使う
10. 厳密性は段階適用（Simple/Standard/Complex）

## トラック選択

### Simple Track
**対象**: CRUD中心、低リスク、短期

- 重要LawだけをLaw Card化（S0/S1中心）
- Zod/Joi等で入力境界のPreを強制
- 重要Lawの違反が見える最低限のログ・カウンタ

### Standard Track
**対象**: 状態整合が重要、変更頻度が高い、チーム開発

- Law Module（境界）を定義し依存を絞る
- 重要InvariantはPBTで押さえる（対象限定）
- 主要Lawはテレメトリ全量

### Complex Track
**対象**: ミッションクリティカル、分散、法令・監査、巨額損害

- 形式仕様（TLA+/Alloy等）は「壊れると致命的」部分のみ
- 変更影響はImpact Graph候補列挙に限定
- 反例・監査証跡を運用資産として保存

## 開発プロセス（Phase A-E）

### Phase A: Law同定
- **入力**: 要件、障害履歴、監査要件、運用手順
- **出力**: Law Catalog v0
- **完了条件**: 主要な「壊れ方」がLawに紐づく

### Phase B: Lawカード化
- 重要度順にカード化（S0→S1→S2）
- **完了条件**: Scope/例外/違反時動作が曖昧でない
- → `/lde-law-card` スキルを使用

### Phase C: 接地（Grounding）
- 検証（Test or Runtime）最低1つ
- 観測（Telemetry or Log/Event）最低1つ
- **完了条件**: 本番で違反が"見える"
- 詳細は [grounding.md](references/grounding.md) 参照

### Phase D: 実装分離（Pure/IO境界）
- Lawの中核はPureに寄せる
- IOは境界で集約
- **完了条件**: Lawのテストが副作用無しで回る

### Phase E: 変更運用
- Law変更 → 影響範囲 → 互換性 → 段階リリース
- **完了条件**: Law変更が「仕様変更」として追跡できる
- 詳細は [change-procedure.md](references/change-procedure.md) 参照

## 必須成果物

| 成果物 | 説明 |
|--------|------|
| Law Catalog | 全Lawの索引（ID/Type/Scope/重要度/Owner） |
| Law Card | 1法則=1カード（例外・違反時動作まで） |
| Grounding Map | Law ↔ Test ↔ Telemetry/Log/Event の対応表 |
| Violation Taxonomy | 違反分類（Bug/UserError/BusinessException等） |
| Change Procedure | Law変更時の影響分析と互換性判断ルール |

## チェックリスト

### 開発開始時
- [ ] Law Catalog v0 がある（主要な壊れ方がLawに紐づく）
- [ ] 重要Law（S0/S1）がLaw Card化されている
- [ ] 重要Law（S0/S1）に検証が最低1つある
- [ ] 重要Law（S0/S1）に観測が最低1つある

### 実装時
- [ ] LawはPureでテスト可能になっている
- [ ] IOは境界に集約され、Lawの中核に混ざっていない
- [ ] 違反時の扱い（reject/compensate/...）が散っていない

### 変更時
- [ ] Law変更としてレビューされている
- [ ] 影響範囲（Scope/依存）が列挙されている
- [ ] 互換性と段階リリースが定義されている

## ディレクトリ構造例（Standard向け）

```
/docs/lde/
  law-catalog.md
  grounding-map.md
  violation-taxonomy.md
  change-procedure.md
/modules/<domain>/
  laws.ts
  domain.ts
  tests/
    spec.test.ts
  telemetry.ts
```

## References

- [grounding.md](references/grounding.md) - 接地・テスト戦略・テレメトリ
- [change-procedure.md](references/change-procedure.md) - Law変更手順
- [violation-taxonomy.md](references/violation-taxonomy.md) - 違反分類
