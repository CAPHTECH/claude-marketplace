---
name: eld-spec-card
argument-hint: "law | term | both (default: both)"
description: |
  ELD SpecのLaw Card・Term Card作成統合スキル。
  ビジネス上の「守るべき条件」（Law）およびドメインの語彙（Vocabulary/Term）を
  標準フォーマットで文書化する。
  使用タイミング: (1) 新しいLaw/Termを追加する時、(2) 既存Law/Termを更新する時、
  (3) Law Catalog/Vocabulary Catalogに新規エントリを追加する時、
  (4) Grounding Mapを更新する時、(5) Discovery後にCard化する時
---

# ELD Spec Card: Law Card + Term Card

## $ARGUMENTS

| Value | Scope | Description |
|-------|-------|-------------|
| `law` | Law Card only | Law Cardを作成・更新する |
| `term` | Term Card only | Term Cardを作成・更新する |
| `both` | Law + Term | Law CardとTerm Cardの両方を作成（default） |

---

## Law Card

### Law分類

| 種別 | 定義 | 例 |
|------|------|-----|
| **Invariant** | どの状態でも常に成り立つ条件（状態制約） | `available = total - reserved` |
| **Pre** | 操作を受け付けるための条件（入力制約） | `orderQty ≤ available` |
| **Post** | 操作後に必ず成り立つ条件（出力制約） | `reserved' = reserved + orderQty` |
| **Policy** | 裁量・例外・外部状況を含む判断規則 | 「VIPは上限緩和」 |

### 分類時の注意

- **Invariant**: 「本当は手続き依存」なのにInvariantと言い張ると事故る
- **Pre**: UI/API境界でまず守る
- **Post**: 並行時の意味（同時実行）を別途定義することがある
- **Policy**: 純粋関数に落とすなら環境（Context）を入力化する

### Law Cardテンプレート

```md
## LAW-<domain>-<name> (ID)
- Type: Invariant | Pre | Post | Policy
- Scope: <module/usecase/endpoint/job>
- Statement: <自然言語 1〜3行>
- Formal-ish: <疑似式 / 型 / predicate（任意だが曖昧さ削減に有効）>

- Terms (required):
  - <このLawが参照するTerm ID。最低1つ必須>
  - 例: TERM-inventory-available, TERM-order-quantity

- Exceptions:
  - <例外条件と理由。無ければ "None">

- Violation Handling:
  - Severity: S0|S1|S2|S3
  - When Violated: reject | compensate | warn | quarantine | audit
  - Owner: <責任者/チーム>

- Verification (at least one):
  - Test: <unit/property/test-case>
  - Runtime Check: <assertion/guard>

- Observability (at least one):
  - Telemetry: law.<domain>.<law_name>.(applied|violated|latency_ms|coverage)
  - Log/Event: <event name / fields>
```

### Severity（重要度）

| レベル | 説明 |
|--------|------|
| **S0** | ビジネス停止レベル |
| **S1** | 重大な機能障害 |
| **S2** | 部分的な機能劣化 |
| **S3** | 軽微・改善レベル |

### Law Card作成手順

1. **Law同定**: ビジネス上の「守るべき条件」を特定
2. **分類**: Invariant / Pre / Post / Policy のいずれかに分類
3. **Scope定義**: 適用範囲（モジュール/エンドポイント/ジョブ）を明確化
4. **Statement記述**: 自然言語で1〜3行で記述
5. **Terms紐付け**: このLawが参照するTermを明示（最低1つ必須）
6. **Exceptions定義**: 例外条件があれば明記
7. **Handling決定**: Severity + 違反時動作 + Owner
8. **Verification設定**: Test または Runtime Check を最低1つ
9. **Observability設定**: Telemetry または Log/Event を最低1つ
10. **Link Map更新**: `/eld-spec-link` で Law <-> Term の関係を記録
11. **Grounding Map更新**: Law <-> Test <-> Telemetry の対応を記録

### Law Card実例：在庫の不変条件

```md
## LAW-inv-available-balance
- Type: Invariant
- Scope: `inventory.reserveStock` / `inventory.releaseStock`
- Statement: 利用可能在庫は総在庫から予約済み在庫を引いた値に等しい
- Formal-ish: `∀t: available(t) = total(t) - reserved(t)`

- Terms:
  - TERM-inventory-available（利用可能在庫）
  - TERM-inventory-total（総在庫）
  - TERM-inventory-reserved（予約済み在庫）

- Exceptions:
  - None

- Violation Handling:
  - Severity: S1
  - When Violated: quarantine（出荷停止）| audit（反例保存）
  - Owner: inventory-team

- Verification:
  - Test: `prop_inventory_balance` (PBT)
  - Runtime Check: `assert_balance()` in post-commit hook

- Observability:
  - Telemetry: `law.inventory.available_balance.violated_total`
  - Log/Event: `inventory.balance.violation` with `{expected, actual, diff}`
```

### Law Card実例：注文数量の事前条件

```md
## LAW-pre-order-quantity
- Type: Pre
- Scope: `order.create` API
- Statement: 注文数量は利用可能在庫を超えてはならない
- Formal-ish: `orderQty ≤ available`

- Terms:
  - TERM-order-quantity（注文数量）
  - TERM-inventory-available（利用可能在庫）

- Exceptions:
  - バックオーダー許可商品は例外（Policy LAW-policy-backorder 参照）

- Violation Handling:
  - Severity: S2
  - When Violated: reject（400 Bad Request）
  - Owner: order-team

- Verification:
  - Test: `test_order_quantity_exceeds_available`
  - Runtime Check: Zod schema validation

- Observability:
  - Telemetry: `law.order.quantity_limit.violated_total`
  - Log/Event: `order.validation.failed` with `{orderQty, available}`
```

### Law Catalog更新

Law Card作成後、Law Catalogに追加:

```md
| ID | Type | Scope | Severity | Owner | Status |
|----|------|-------|----------|-------|--------|
| LAW-inv-available-balance | Invariant | inventory.* | S1 | inventory-team | Active |
| LAW-pre-order-quantity | Pre | order.create | S2 | order-team | Active |
```

### Law Grounding Map更新

```md
| Law ID | Type | Test | Runtime Check | Telemetry | Notes |
|--------|------|------|---------------|-----------|-------|
| LAW-inv-available-balance | Invariant | prop_inventory_balance | assert_balance | law.inventory.* | - |
| LAW-pre-order-quantity | Pre | test_order_quantity | Zod validation | law.order.* | - |
```

### Law相互拘束ルール

- **Lawは孤立禁止**: すべてのLawは最低1つのTermを参照する必要がある
- **Terms参照はLink Mapと連動**: `/eld-spec-link` で Law <-> Term の関係を管理

---

## Term Card

### Term分類

| 種別 | 定義 | 例 |
|------|------|-----|
| **Term（用語）** | ビジネス上の概念・名詞 | 「利用可能在庫」「注文」 |
| **Type（型）** | 技術的な型・構造 | `OrderId`, `Quantity` |
| **Value（値制約）** | 値の範囲・形式 | `1 ≤ qty ≤ 100` |
| **Context（文脈）** | 用語が使われる文脈 | 「在庫管理」「注文処理」 |

### 分類時の注意

- **Term**: 「言葉」ではなく「運用単位」として定義する
- **Type**: Brand/Newtype/ADTで意味的区別を強制
- **Value**: 境界での検証・正規化を必須化
- **Context**: 同じ言葉でも文脈で意味が変わる場合を明確化

### Term Cardテンプレート

```md
## TERM-<domain>-<name> (ID)

### 基本情報
- Meaning: <定義（1〜2文）>
- Context: <使用される文脈・ドメイン>
- Synonyms: <同義語があれば列挙>
- Non-goals: <この用語が意味しないもの>

### 型・形状
- Type/Shape: <技術的な型表現>
- Constraints: <値制約>
- Example Values: <具体例>

### 境界と接地
- IO Boundaries: <どこで入力/出力されるか>
- Validation: <境界での検証方法>
- Normalization: <正規化処理>
- Observable Fields: <ログ/テレメトリで観測するフィールド>

### 関連Law
- Related Laws (at least one for S0/S1 Terms):
  - <関連するLaw ID>
```

### Term Card作成手順

1. **Term同定**: ドメインで使う語彙を特定
2. **分類**: Term / Type / Value / Context に分類
3. **Meaning記述**: 定義を1〜2文で明確に記述
4. **Context定義**: どの文脈で使われるかを明確化
5. **Type/Shape定義**: 技術的な型表現を決定
6. **Boundaries定義**: IO境界での検証・正規化を設計
7. **Observable Fields設定**: ログ/テレメトリで観測するフィールド
8. **Related Laws紐付け**: 関連するLawを明示（S0/S1は必須）
9. **Link Map更新**: `/eld-spec-link` で Term <-> Law の関係を記録

### Term Card実例：利用可能在庫

```md
## TERM-inventory-available

### 基本情報
- Meaning: 現時点で注文に割り当て可能な在庫数量
- Context: 在庫管理、注文処理
- Synonyms: 有効在庫、販売可能在庫
- Non-goals: 物理的な在庫数（予約済みを含む）

### 型・形状
- Type/Shape: `AvailableStock = Brand<number, 'AvailableStock'>`
- Constraints: `available ≥ 0`, `available ≤ total`
- Example Values: 0, 50, 1000

### 境界と接地
- IO Boundaries:
  - Input: 在庫API、管理画面
  - Output: 注文API、商品詳細
- Validation: `z.number().nonnegative().max(MAX_STOCK)`
- Normalization: 小数点以下切り捨て
- Observable Fields: `inventory.available`, `inventory.available_diff`

### 関連Law
- Related Laws:
  - LAW-inv-available-balance（利用可能在庫の計算式）
  - LAW-pre-order-quantity（注文数量上限）
```

### Term Card実例：注文数量

```md
## TERM-order-quantity

### 基本情報
- Meaning: 1回の注文で指定される商品数量
- Context: 注文処理
- Synonyms: 購入数量、オーダー数
- Non-goals: カート内の合計数量

### 型・形状
- Type/Shape: `OrderQuantity = Brand<number, 'OrderQuantity'>`
- Constraints: `1 ≤ qty ≤ 100`
- Example Values: 1, 5, 10

### 境界と接地
- IO Boundaries:
  - Input: 注文API、購入画面
  - Output: 確認画面、注文履歴
- Validation: `z.number().int().min(1).max(100)`
- Normalization: 整数化（Math.floor）
- Observable Fields: `order.quantity`, `order.total_items`

### 関連Law
- Related Laws:
  - LAW-pre-order-quantity（注文数量上限）
  - LAW-policy-bulk-order（大量注文ポリシー）
```

### Vocabulary Catalog更新

Term Card作成後、Vocabulary Catalogに追加:

```md
| ID | Meaning | Context | Type | Owner | Status |
|----|---------|---------|------|-------|--------|
| TERM-inventory-available | 利用可能在庫 | 在庫管理 | S1 | inventory-team | Active |
| TERM-order-quantity | 注文数量 | 注文処理 | S2 | order-team | Active |
```

### Term相互拘束ルール

- **重要Termは孤立禁止**: S0/S1 TermはRelated Lawsを最低1つ持つ
- **Related LawsはLink Mapと連動**: `/eld-spec-link` で Term <-> Law の関係を管理

---

## よくある失敗パターン

### 名辞インフレ（Term/型だけ増える）
- **症状**: Term/型が増えるがRelated Lawsが空
- **対策**: S0/S1 TermのRelated Lawsを必須化

### 関係スープ（Lawだけ増える）
- **症状**: Lawは増えるが主要語彙が曖昧
- **対策**: Lawが参照する語彙をTermカード化

### 型の過信
- **症状**: Brand/Newtypeがあるが境界検証が薄い
- **対策**: IO BoundaryとValidationを必須化

## 品質チェック

| チェック項目 | 確認内容 |
|-------------|---------|
| 意味明確性 | Meaningが1〜2文で明確か |
| 境界定義 | IO Boundariesが具体的か |
| 検証実装 | Validationが実装されているか |
| 観測可能 | Observable Fieldsが設定されているか |
| Law紐付け | S0/S1 TermにRelated Lawsがあるか |
| Law孤立 | すべてのLawにTerms参照があるか |
| Verification | Test/Runtime Checkが最低1つあるか |
| Observability | Telemetry/Log/Eventが最低1つあるか |
