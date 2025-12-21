---
name: lde
description: |
  Law-Driven Engineering (LDE) - 名辞抽象（Noun Abstraction）と関係抽象（Relation Abstraction）を統合した開発手法。
  ビジネス上の「守るべき条件」をLaw（法則）として、ドメインの語彙をVocabulary（名辞）として明文化し、
  相互拘束（mutual constraint）によって実装の一貫性と保守性を高める。
  使用タイミング: (1) 新規プロジェクトでLDEを導入する時、(2) 開発フェーズ（A-F）を実行する時、
  (3) トラック（Simple/Standard/Complex）を選択する時、(4) チェックリストで品質確認する時
---

# Law-Driven Engineering (LDE)
## ― 名辞抽象（Noun Abstraction）と関係抽象（Relation Abstraction）統合版 ―

## LDEとは

**関係（Law）が名辞（Vocabulary）の意味を拘束し続け、名辞が関係の運用可能性を支える**という**相互拘束（mutual constraint）**を作る開発手法。

### 二つの抽象

| 抽象 | 主役 | 強み | 弱み |
|------|------|------|------|
| **名辞抽象** | 語彙/型/Entity | 共有言語、境界設計、観測フィールド | 整合性が散りやすい |
| **関係抽象** | Law/制約/写像 | 整合性の中心化、テスト・監査 | 語彙と責務境界が薄れやすい |

**LDEの立ち位置**：
- **一次**：関係抽象（Law）
- **二次**：名辞抽象（Vocabulary/Type）
- 両者を「カード」「連結表」「接地」で結び、相互に崩れない状態を維持

## Core定義（12行）

1. ビジネス上の「守るべき条件」を **Law（法則）** として明文化し、実装の中心に置く
2. 同時に、ドメインで使う語彙を **Vocabulary（名辞）** として明文化し、チームの共通理解を固定
3. Lawは **Invariant / Pre / Post / Policy** に分類
4. Vocabularyは **Term（用語）/ Type（型）/ Value（値制約）/ Context（文脈）** に分類
5. 各Lawは **Scope・例外・違反時扱い** を含む「Law Card」として管理
6. 各Termは **意味・境界・観測写像** を含む「Term Card」として管理
7. **各Lawは参照するTermを明示**し、**各重要Termは関連Lawを最低1つ**持つ（孤立禁止）
8. Lawは必ず **検証手段（Test/Runtime Check）** を最低1つ持つ
9. Lawは必ず **観測手段（Telemetry/Log/Event）** を最低1つ持つ
10. 実装は「Law → Pure（判定/変換） → IO境界」に分離
11. 型はLawを補助し、**不可能な状態を排除**するが、型だけで真理を代替しない
12. 変更時は「Vocabulary変更/Law変更 → 影響範囲 → 互換性 → 段階リリース」で扱う

## トラック選択

### Simple Track
**対象**: CRUD中心、低リスク、短期

- **Law**: 重要LawのみCard化、例示テスト中心
- **Term**: 重要TermのみCard化、スキーマで境界検証
- **連結**: Link Mapは薄くてよいが、**S0/S1は必須**

### Standard Track
**対象**: 状態整合が重要、変更頻度が高い、チーム開発

- **Law**: 重要InvariantはPBT、主要Lawはテレメトリ全量
- **Term**: 主要TermはBrand/Newtype/ADTで区別、境界で正規化徹底
- **連結**: Link Mapは必須（変更レビューで使う）

### Complex Track
**対象**: ミッションクリティカル、分散、法令・監査

- **Law**: 致命箇所のみ形式仕様（TLA+/Alloy等）
- **Term**: 監査・法令で意味が変えられないTermを強固に固定
- **連結**: 影響は候補列挙（Impact Graph）に限定

## 開発プロセス（Phase A-F）

### Phase A: Vocabulary同定（名辞抽象の初期固定）
- **入力**: 要件、ドメイン知識、既存用語
- **出力**: Vocabulary Catalog v0
- **完了条件**: 同義語と境界（どこで使う言葉か）が書かれている
- ここでは型を作り込まない

### Phase B: Law同定（関係抽象の初期固定）
- **入力**: 要件、障害履歴、監査要件、運用手順
- **出力**: Law Catalog v0
- **完了条件**: 主要な「壊れ方」がLawに紐づく
- "壊れると困る関係"から書く（S0/S1優先）

### Phase C: Law Card化（関係を仕様化）
- **出力**: Law Card（Scope/例外/違反時動作）
- **完了条件**: 各Lawに Terms が紐づいている
- → `/lde-law-card` スキルを使用
- → `/lde-link-map` を同時更新

### Phase D: Term Card化（名辞を運用可能に固定）
- **出力**: Term Card（意味・境界・観測写像）
- **完了条件**: 重要Termに Related Laws が紐づいている
- → `/lde-term-card` スキルを使用
- Termは"言葉"ではなく"運用単位"にする

### Phase E: 接地（Grounding）
- **出力**: Grounding Map
- **完了条件**:
  - Law: 検証（Test/Runtime）と観測（Telemetry/Log/Event）が最低1つ
  - Term: 観測フィールドと境界での検証/正規化が最低1つ
- → `/lde-grounding-check` スキルを使用

### Phase F: 実装（Pure/IO分離）
- **出力**: Pure関数群 + IO境界
- **完了条件**: Lawのテストが副作用無しで回る
- 違反分類（Taxonomy）に従って扱いを統一

## 必須成果物

| 成果物 | 説明 |
|--------|------|
| **Law Catalog** | 全Lawの索引（ID/Type/Scope/重要度/Owner） |
| **Law Card** | 1法則=1カード（例外・違反時動作・Terms参照） |
| **Vocabulary Catalog** | 全Termの索引（ID/Meaning/Context/Owner） |
| **Term Card** | 1用語=1カード（意味・境界・観測写像・Related Laws） |
| **Link Map（連結表）** | Law ↔ Term の関係（依存・参照） |
| **Grounding Map** | Law ↔ Test ↔ Telemetry/Log/Event |
| **Violation Taxonomy** | 違反分類（Bug/UserError/BusinessException/DataDrift/Compliance） |
| **Change Procedure** | 変更手順（Vocabulary/Law/Interface/Dataの互換性） |

## チェックリスト（名辞×関係統合Core）

### 設計開始
- [ ] Vocabulary Catalog v0 がある（同義語と境界が書かれている）
- [ ] Law Catalog v0 がある（壊れ方が列挙されている）

### 仕様化（カード）
- [ ] S0/S1 Law は Law Card化され、Terms が紐づいている
- [ ] S0/S1 Term は Term Card化され、Related Laws が紐づいている
- [ ] Link Map が更新され、孤立Law/孤立Termがない

### 接地（検証と観測）
- [ ] S0/S1 Law は検証（Test/Runtime）が最低1つある
- [ ] S0/S1 Law は観測（Telemetry/Log/Event）が最低1つある
- [ ] S0/S1 Term は境界で検証/正規化され、観測フィールドに落ちている

### 実装
- [ ] Lawの中核はPureでテスト可能
- [ ] IO境界が集約され、Lawが散っていない
- [ ] 違反分類（Bug/User/Exception/Data/Compliance）が統一されている

### 変更
- [ ] Term変更が関連Lawにどう影響するか列挙されている
- [ ] Law変更が関連Termの意味やI/F互換性にどう影響するか列挙されている
- [ ] 段階リリースとロールバック方針がある

## よくある失敗パターン

### 名辞インフレ（名辞だけ増える）
- **症状**: Term/型が増えるがLawが増えない
- **対策**: 重要Termは Related Laws を必須にする

### 関係スープ（関係だけ増える）
- **症状**: Lawは増えるが主要語彙が曖昧
- **対策**: Law CardにTermsを必須化

### 型の過信
- **症状**: Brand/Newtypeがあるが境界検証が薄い
- **対策**: Term CardにIO BoundaryとValidationを必須化

## ディレクトリ構造例（Standard向け）

```
/docs/lde/
  law-catalog.md
  vocabulary-catalog.md
  link-map.md
  grounding-map.md
  violation-taxonomy.md
  change-procedure.md
/modules/<domain>/
  laws.ts
  terms.ts
  domain.ts
  tests/
    spec.test.ts
  telemetry.ts
```

## References

- [grounding.md](references/grounding.md) - 接地・テスト戦略・テレメトリ
- [change-procedure.md](references/change-procedure.md) - Law変更手順
- [violation-taxonomy.md](references/violation-taxonomy.md) - 違反分類
