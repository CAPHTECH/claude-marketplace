# Model（モデル化）フェーズ

語彙（Term）と関係（Law）を同定し、カードに落とす。

## 目的

- ドメインの語彙を運用可能に固定
- ビジネス上の「守るべき条件」を明文化
- Law ↔ Term の相互拘束を確立

## 二つの抽象

| 抽象 | 主役 | 強み | 弱み |
|------|------|------|------|
| **名辞抽象** | 語彙/型/Entity | 共有言語、境界設計 | 整合性が散りやすい |
| **関係抽象** | Law/制約/写像 | 整合性の中心化 | 語彙と境界が薄れやすい |

**ELDの立ち位置**:
- **一次**: 関係抽象（Law）
- **二次**: 名辞抽象（Vocabulary/Type）
- 両者を「カード」「連結表」「接地」で結ぶ

## Vocabulary同定（Phase A）

### 入力
- 要件、ドメイン知識、既存用語
- Senseフェーズの観測結果

### 出力
- Vocabulary Catalog v0

### 完了条件
- 同義語と境界（どこで使う言葉か）が書かれている
- **ここでは型を作り込まない**

### 手法

1. **語彙の抽出**
   - コードから主要な名詞を抽出
   - 要件書から業務用語を抽出
   - 既存ドキュメントから定義を収集

2. **境界の特定**
   - どのモジュールで使われる言葉か
   - どのレイヤーで使われる言葉か
   - どのインターフェースで使われる言葉か

3. **同義語の整理**
   - 同じ意味で使われる別の言葉を列挙
   - 正規の呼び方を決定

## Law同定（Phase B）

### 入力
- 要件、障害履歴、監査要件、運用手順
- Senseフェーズの観測結果

### 出力
- Law Catalog v0

### 完了条件
- 主要な「壊れ方」がLawに紐づく
- S0/S1優先で列挙されている

### 手法

1. **「壊れると困る関係」から書く**
   - 障害履歴から不変条件を抽出
   - 監査要件から制約を抽出
   - 運用手順から前提/事後条件を抽出

2. **重要度分類**
   - S0（Critical）: 違反=即障害
   - S1（High）: 違反=重大な不整合
   - S2（Medium）: 違反=軽微な不整合
   - S3（Low）: 違反=ベストプラクティス逸脱

3. **タイプ分類**
   - Invariant: 常に成り立つ
   - Pre: 操作の前提条件
   - Post: 操作の事後条件
   - Policy: ビジネスルール

## Law Card化（Phase C）

### 出力
- Law Card（Scope/例外/違反時動作）

### 完了条件
- 各Lawに Terms が紐づいている

### Law Card構成

```markdown
# LAW-{domain}-{name}

## 基本情報
- **ID**: LAW-{domain}-{name}
- **Type**: Pre | Post | Invariant | Policy
- **Severity**: S0 | S1 | S2 | S3
- **Created**: YYYY-MM-DD

## Statement（自然言語）
<!-- 日本語での記述 -->

## Formal（疑似式）
例: 1 ≤ orderQty ≤ 100
例: ∀t: token.expiry > now → token.valid

## Scope（適用範囲）
- モジュール:
- 関数/メソッド:
- レイヤー:

## Terms（参照する語彙）
<!-- このLawが参照するTerm。孤立禁止 -->
- TERM-xxx
- TERM-yyy

## Exceptions（例外）
<!-- Lawが適用されないケース -->

## Violation Behavior（違反時動作）
- エラー種別:
- 回復戦略:
- 通知先:

## Grounding（接地）
<!-- 50-ground.mdで詳細化 -->
```

→ `/lde-law-card` スキルを使用
→ `/lde-link-map` を同時更新

## Term Card化（Phase D）

### 出力
- Term Card（意味・境界・観測写像）

### 完了条件
- 重要Termに Related Laws が紐づいている

### Term Card構成

```markdown
# TERM-{domain}-{name}

## 基本情報
- **ID**: TERM-{domain}-{name}
- **Type**: Entity | Value | Context | Boundary
- **Severity**: S0 | S1 | S2 | S3
- **Created**: YYYY-MM-DD

## Meaning（意味）
<!-- このTermが表すもの -->

## Synonyms（同義語）
<!-- 同じ意味で使われる別の言葉 -->

## Boundary（境界）
- 使用モジュール:
- 使用レイヤー:
- 使用インターフェース:

## Type/Shape（型表現）
```typescript
type OrderQuantity = Brand<number, 'OrderQuantity'>;
z.number().min(1).max(100)
```

## Observable Fields（観測写像）
| フィールド | 型 | 説明 |
|-----------|-----|------|

## I/O Boundaries（境界での扱い）
### 入力時
- 検証:
- 正規化:

### 出力時
- シリアライズ:

## Related Laws（関連Law）
<!-- S0/S1は必須 -->
- LAW-xxx
- LAW-yyy
```

→ `/lde-term-card` スキルを使用

## Link Map（連結表）

Law ↔ Term の相互参照を管理:

```yaml
# law-term-link-map.yaml
laws:
  LAW-order-quantity-range:
    terms: [TERM-order-quantity]
    grounding:
      tests: [test_order_quantity_validation]
      telemetry: [order.quantity.out_of_range]

terms:
  TERM-order-quantity:
    laws: [LAW-order-quantity-range, LAW-order-total-limit]
    boundaries:
      input: OrderSchema.quantity
      output: OrderResponse.quantity
```

## 孤立チェック

### Law → Term
- [ ] すべてのLawがTerms欄に参照するTermを持つ
- [ ] 孤立したLaw（Term参照なし）がない

### Term → Law
- [ ] S0/S1のTermがRelated Laws欄に関連Lawを持つ
- [ ] 孤立したS0/S1 Termがない

## よくある失敗パターン

### 名辞インフレ
- **症状**: Term/型が増えるがLawが増えない
- **対策**: 重要Termは Related Laws を必須にする

### 関係スープ
- **症状**: Lawは増えるが主要語彙が曖昧
- **対策**: Law CardにTermsを必須化

### 型の過信
- **症状**: Brand/Newtypeがあるが境界検証が薄い
- **対策**: Term CardにIO BoundaryとValidationを必須化

## チェックリスト

- [ ] Vocabulary Catalog v0 がある（同義語と境界が書かれている）
- [ ] Law Catalog v0 がある（壊れ方が列挙されている）
- [ ] S0/S1 Law は Law Card化され、Terms が紐づいている
- [ ] S0/S1 Term は Term Card化され、Related Laws が紐づいている
- [ ] Link Map が更新され、孤立Law/孤立Termがない
