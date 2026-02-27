---
name: eld-model
context: fork
argument-hint: discover | card | full (default: full)
description: コードベースや要件からVocabulary(語彙)とLaw(守るべき条件)を自動発見し、標準フォーマットのTerm Card / Law Cardとして文書化する。「Lawを発見して」「語彙を抽出して」「Term Cardを作成して」「Law Cardを作成して」「ELDモデリングして」と言われた時、新規プロジェクトのVocabulary/Law洗い出し時、既存コードからのLaw/Term抽出時に使用する。
---

# ELD Model: Discovery + Card

Vocabulary/Lawの発見からCard化までを一貫して行う。

## $ARGUMENTS

| Value | Scope | Description |
|-------|-------|-------------|
| `discover` | Phase 1 only | Vocabulary/Law候補を発見しレポート出力 |
| `card` | Phase 2 only | 既存候補をCard化（候補が既にある前提） |
| `full` | Phase 1 + 2 + 3 | 発見 → Card化 → Link Map更新促し（default） |

## Phase 1: Discovery（発見）

コードベースや要件からVocabulary候補とLaw候補を自動発見する。

### Discovery Process

#### Step 1: ソース収集

型定義・バリデーション・アサーション・テスト期待値・ビジネスロジックを走査する。
詳細な発見パターンとgrepコマンドは [discovery-patterns.md](references/discovery-patterns.md) を参照（コード走査時に読む）。

#### Step 2: 候補生成

```yaml
# Vocabulary候補
term_candidate:
  id: TERM-<domain>-<name>
  source: { file: <path>, line: <num> }
  meaning: <推定される意味>
  type_shape: <型表現>
  context: <使用文脈>
  confidence: high | medium | low
  needs_review: <確認が必要な点>

# Law候補
law_candidate:
  id: LAW-<domain>-<name>
  type: Pre | Post | Invariant | Policy
  source: { file: <path>, line: <num>, pattern: <検出パターン> }
  statement: <自然言語での記述>
  formal_ish: <疑似式>
  terms: [<関連するTerm候補>]
  confidence: high | medium | low
  needs_review: <確認が必要な点>
```

#### Step 3: 相互拘束チェック

- Lawで参照Termが不明確なものを検出
- Termで関連Lawがないものを検出
- 既存Catalogとの重複・類似・矛盾を照合

#### Step 4: Discovery Report出力

```markdown
# ELD Discovery Report

## Summary
- Vocabulary候補: N件 (High: x, Medium: y, Low: z)
- Law候補: N件 (High: x, Medium: y, Low: z)

## Vocabulary候補（名辞抽象）

### High Confidence
#### TERM-xxx
- Source: path:line
- Meaning: ...
- Type/Shape: ...

### Medium Confidence (確認推奨)
...

## Law候補（関係抽象）

### High Confidence
#### LAW-xxx
- Type: Pre
- Source: path:line
- Statement: ...
- Formal: ...
- Terms: [...]

### Medium Confidence (確認推奨)
...

## 相互拘束チェック
- 孤立リスク: ...
- 推奨アクション: ...
```

`$ARGUMENTS` が `discover` の場合はここで終了。ユーザーにレビューを促す。

## Phase 2: Card化

High Confidence候補（またはユーザーが確認済みの候補）をCard化する。

### Law Card作成

テンプレートは [law-card-template.md](references/law-card-template.md) を参照（Law Card作成・更新時に読む）。

作成手順:

1. Law同定 → 分類（Invariant / Pre / Post / Policy）
2. Scope定義 → Statement記述
3. Terms紐付け（最低1つ必須 -- Lawは孤立禁止）
4. Exceptions定義
5. Violation Handling決定（Severity + 違反時動作 + Owner）
6. Verification設定（Test or Runtime Check、最低1つ）
7. Observability設定（Telemetry or Log/Event、最低1つ）

### Term Card作成

テンプレートは [term-card-template.md](references/term-card-template.md) を参照（Term Card作成・更新時に読む）。

作成手順:

1. Term同定 → 分類（Term / Type / Value / Context）
2. Meaning記述（1〜2文）→ Context定義
3. Type/Shape定義 → Constraints
4. IO Boundaries定義 → Validation / Normalization
5. Observable Fields設定
6. Related Laws紐付け（S0/S1 Termは必須）

### Catalog更新

Card作成後、対応するCatalogに追加する。

Law Catalog:

```md
| ID | Type | Scope | Severity | Owner | Status |
|----|------|-------|----------|-------|--------|
```

Vocabulary Catalog:

```md
| ID | Meaning | Context | Type | Owner | Status |
|----|---------|---------|------|-------|--------|
```

### Grounding Map更新

```md
| Law ID | Type | Test | Runtime Check | Telemetry | Notes |
|--------|------|------|---------------|-----------|-------|
```

## Phase 3: Link Map更新

Card化完了後、`/eld-model-link-map` を使用してLaw <-> Termの相互参照を更新する。

チェック項目:
- 新規Lawにすべて参照Termがある
- 新規S0/S1 TermにRelated Lawsがある
- 孤立Law/Termがない
- 名辞インフレ（Termだけ増えてLawなし）の兆候がない
- 関係スープ（Lawだけ増えてTermなし）の兆候がない

## 相互拘束ルール

| Rule | Detail |
|------|--------|
| Law孤立禁止 | すべてのLawは最低1つのTermを参照する |
| 重要Term孤立禁止 | S0/S1 TermはRelated Lawsを最低1つ持つ |
| Link Map連動 | Card作成後は必ずLink Mapを更新 |

## よくある失敗パターン

| Pattern | Symptom | Countermeasure |
|---------|---------|----------------|
| 名辞インフレ | Term/型だけ増えてRelated Lawsが空 | S0/S1 TermのRelated Laws必須化 |
| 関係スープ | Lawは増えるが主要語彙が曖昧 | Lawが参照する語彙をTermカード化 |
| 型の過信 | Brand/Newtypeがあるが境界検証が薄い | IO BoundaryとValidation必須化 |

## 品質原則

1. **Epistemic Humility**: 推測を事実として扱わない。`unknown`と言う勇気を持つ
2. **Evidence First**: 因果と証拠を中心にする
3. **Grounded Laws**: Lawは検証可能・観測可能でなければならない
4. **Source of Truth**: 真実は常に現在のコード。要約はインデックス

### 完了チェック

- [ ] Law/Termが接地している（Grounding Map確認）
- [ ] Link Mapに孤立がない
- [ ] ロールバック可能な状態

### 停止条件

以下が発生したら即座に停止し、追加計測またはスコープ縮小:

- 想定外テスト失敗3回以上
- 観測不能な変更の増加
- ロールバック線の崩壊
