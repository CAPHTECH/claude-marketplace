---
name: eld-spec
context: fork
argument-hint: "discover | card | full (default: full)"
description: Spec駆動開発（SDD）のためのVocabulary(Term)とLaw発見・文書化スキル。コードベースや要件からVocabulary(語彙)とLaw(守るべき条件)を自動発見し、標準フォーマットのTerm Card / Law Cardとして文書化する。「Lawを発見して」「語彙を抽出して」「Term Cardを作成して」「Law Cardを作成して」「Spec化して」「ELDモデリングして」等で使用。新規プロジェクトのVocabulary/Law洗い出し時、既存コードからのLaw/Term抽出時に使用する。
---

# ELD Spec: Discovery + Card

Vocabulary/Lawの発見からCard化までを一貫して行う。Spec駆動開発（SDD）のフレームワークとして、コードベースや要件からドメインの仕様（Spec）を抽出・文書化する。

## $ARGUMENTS

| Value | Scope | Description |
|-------|-------|-------------|
| `discover` | Phase 1 only | Vocabulary/Law候補を発見しレポート出力 |
| `card` | Phase 2 only | 既存候補をCard化（候補が既にある前提） |
| `full` | Phase 1 + 2 + 3 | 発見 → Card化 → Link Map更新促し（default） |

## Phase 1: Discovery（発見）

コードベースや要件からのVocabulary候補・Law候補の自動発見は `/eld-spec-discover` に委譲する。
発見パターン・候補スキーマ・Discovery Reportの形式は [discovery-patterns.md](references/discovery-patterns.md) を参照。

`$ARGUMENTS` が `discover` の場合は `/eld-spec-discover` の実行結果をもって終了し、ユーザーにレビューを促す。

## Phase 2: Card化

High Confidence候補（またはユーザーが確認済みの候補）をCard化する。

### Law Card作成

`/eld-spec-card law` を使用してLaw Cardを作成する。

作成手順:

1. Law同定 → 分類（Invariant / Pre / Post / Policy）
2. Scope定義 → Statement記述
3. Terms紐付け（最低1つ必須 -- Lawは孤立禁止）
4. Exceptions定義
5. Violation Handling決定（Severity + 違反時動作 + Owner）
6. Verification設定（Test or Runtime Check、最低1つ）
7. Observability設定（Telemetry or Log/Event、最低1つ）

### Term Card作成

`/eld-spec-card term` を使用してTerm Cardを作成する。

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

Card化完了後、`/eld-spec-link` を使用してLaw <-> Termの相互参照を更新する。

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

## 完了チェック

- [ ] Law/Termが接地している（Grounding Map確認）
- [ ] Link Mapに孤立がない
- [ ] ロールバック可能な状態
