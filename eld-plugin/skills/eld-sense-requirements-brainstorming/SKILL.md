---
name: eld-sense-requirements-brainstorming
context: fork
description: 要件の曖昧さを能動的に発見する対話的ブレインストーミングスキル。Issue Contract作成前に、Law/Term観点、境界条件、失敗モードから多角的質問を生成する。「要件を明確にして」「要件をブレストして」「要件の曖昧さをチェックして」「何が不明確か教えて」等、新機能開発の最初期（Issue Contract作成前）に使用。ELD Phase 1: Issueの前段階として自動実行される。
---

# ELD Sense: Requirements Brainstorming

要件の曖昧さを**能動的に発見**し、Issue Contract作成前に要件を対話的に明確化するスキル。
推測で進めるのではなく、Law/Term観点・境界条件・失敗モードから体系的に質問を生成する。

## 核心原則

1. **Epistemic Humility**: 曖昧さを見つけたら必ず質問する。推測で埋めない
2. **Law/Term First**: 要件をLaw（守るべき条件）とTerm（語彙）の観点で整理
3. **Failure Mode Driven**: 「何が壊れうるか」から逆算して要件を明確化
4. **Progressive Disclosure**: 段階的質問で認知負荷を下げる

## 実行フロー

### Phase 1: 初期理解と質問カテゴリ選択

ユーザーの要求を読み、以下の質問カテゴリから**最も重要な3つ**を選択:

```yaml
質問カテゴリ:
  1. Law/Term観点: 守るべき条件と語彙の定義
  2. 境界条件: 入力の範囲、例外ケース、制約
  3. 失敗モード: 何が壊れうるか、エラーハンドリング
  4. 性能要件: レスポンスタイム、スループット、リソース制約
  5. セキュリティ要件: 認証、認可、データ保護
  6. 既存システムとの関係: 互換性、移行戦略、依存関係
```

**選択基準**:
- ユーザーの要求で言及されていない領域を優先
- リスクが高い領域（セキュリティ、失敗モード）を優先
- 曖昧さが多い領域を優先

### Phase 2: 段階的質問生成

選択したカテゴリごとに、**具体的で答えやすい質問**を生成:

**質問設計パターン**:
```markdown
## [カテゴリ名]

### 質問1: [具体的な質問]
- なぜこれを聞くか: [Law/Term/境界のどれに関係するか]
- 例: [具体例を示して選択肢を提示]

### 質問2: [具体的な質問]
...
```

詳細な質問テンプレートは references/question-templates.md を参照。

### Phase 3: 回答収集と深掘り

ユーザーの回答から:
1. **明確になった点**を記録
2. **まだ曖昧な点**を特定し、追加質問
3. **Law/Term候補**を抽出

**深掘りトリガー**:
- 回答が抽象的すぎる場合（「適切に」「柔軟に」など）
- 例外ケースが不明確な場合
- 複数の解釈が可能な場合

### Phase 4: Issue Contract下書き生成

明確化した要件から Issue Contract を下書き:

```yaml
Issue Contract:
  目的 (Goal): [ビジネス価値と実現内容]

  不変条件 (Invariants):
    - [既存システムで守られている条件]
    - [新規実装でも守るべき条件]

  物差し (Acceptance Criteria):
    - [検証可能な成功条件]
    - [Evidence Ladderレベルを明記]

  停止条件 (Stop Conditions):
    - [予測と現実の継続的乖離]
    - [観測不能な変更の増加]
    - [ロールバック線の崩壊]

  Law/Term候補:
    Law:
      - LAW-xxx: [守るべき条件の記述] (Severity: S0/S1/S2)
    Term:
      - TERM-yyy: [語彙の定義] (Type: Entity/Value/Context/Boundary)

  未確定事項 (Open Questions):
    - [まだ決まっていないこと]
    - [追加調査が必要なこと]
```

### Phase 5: Law/Term候補の引き継ぎ

抽出したLaw/Term候補を `/eld-spec` に引き継ぎ:
- Law候補: 守るべき条件（Invariant/Precondition/Postcondition/Policy）
- Term候補: ドメイン語彙（Entity/Value Object/Context/Boundary）

## 対話パターン

曖昧さは指摘して具体化を促す。例:

```
User: ユーザーが適切に認証されるようにして

Claude: 「適切に」の定義を明確にしたいです。

具体的には：
1. 認証方法: パスワード？OAuth？多要素認証？
2. 失敗時の挙動: リトライ回数制限は？アカウントロックは？
3. セッション管理: ログイン状態の保持期間は？
```

他の対話パターン（質問→回答→深掘り、境界条件の確認等）は references/dialogue-patterns.md を参照。

## Law/Term発見ガイドライン

### Law候補の抽出パターン

ユーザーの回答から以下をLaw候補として抽出:

```yaml
抽出パターン:
  - 「〜しなければならない」→ Invariant (S0/S1)
  - 「〜の前に〜が必要」→ Precondition (S1)
  - 「〜した後は〜が保証される」→ Postcondition (S1)
  - 「〜してはいけない」→ Policy (S0/S1)
  - 「〜の範囲内」→ Boundary constraint (S1/S2)

Severity判定:
  S0: ビジネスクリティカル（違反で金銭損失/法令違反）
  S1: 機能要件（違反で機能不全）
  S2: 品質要件（違反で UX 低下）
```

### Term候補の抽出パターン

```yaml
抽出パターン:
  - ドメイン固有の名詞 → Entity/Value Object
  - 状態を表す語 → Context
  - 範囲を表す語 → Boundary

例:
  - "JWT トークン" → TERM-jwt-token (Value Object)
  - "認証済みユーザー" → TERM-authenticated-user (Context)
  - "有効期限内" → TERM-token-validity-period (Boundary)
```

詳細は references/law-term-discovery.md を参照。

---

## 完了条件

以下をすべて満たしたら Phase 終了:

- [ ] 選択した3つの質問カテゴリすべてで質問を完了
- [ ] ユーザーの回答がすべて具体的（抽象語が解消されている）
- [ ] Issue Contract 下書きが作成済み
- [ ] Law/Term候補が少なくとも3つ以上抽出済み
- [ ] 未確定事項が明示されている

## 次のステップ

完了後、以下のスキルに引き継ぎ:

1. `/eld-spec`: Law/Term候補の詳細化・Card作成
2. `/eld-sense-planning`: タスク分解（Issue Contract をもとに）

## リファレンス

- references/question-templates.md - 質問カテゴリ別テンプレート集
- references/dialogue-patterns.md - 対話フローパターン詳細
- references/law-term-discovery.md - Law/Term発見の詳細ガイド
