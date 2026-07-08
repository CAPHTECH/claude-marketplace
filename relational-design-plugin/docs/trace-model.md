# Trace Model

## Trace graph

Relational Design の trace は、厳密なグラフ DB ではなく、v0.1 では YAML / Markdown による人間可読な trace graph として扱う。

```text
Observation / Assumption / Constraint
  -> Relation
  -> Hypothesis
  -> Design Decision
  -> Artifact
  -> Critique
  -> Revision / Retraction / Backflow
```

## Node types

### Observation

観測された事実。user brief、既存コード、スクリーンショット、デザインシステム、ドキュメントから直接取れるもの。

```yaml
id: RD-O-001
kind: observation
source: user_brief
claim: "The user asked for a pricing page redesign."
confidence: high
```

### Assumption

Agent が埋めた前提。観測ではない。

```yaml
id: RD-A-001
kind: assumption
claim: "Primary users are technical decision makers."
confidence: low
isolated: true
```

### Constraint

実装・ブランド・アクセシビリティ・デバイス・時間などの制約。

```yaml
id: RD-C-001
kind: constraint
claim: "Must reuse existing Button and Card components."
confidence: high
```

### Relation

設計上の張力・関係。

```yaml
id: RD-R-001
kind: relation
relation_type: information_to_confidence
claim: "More proof increases trust but can reduce first-scan clarity."
depends_on: [RD-O-001, RD-A-001]
```

### Hypothesis

UI 案の根拠となる仮説。

```yaml
id: RD-H-001
kind: hypothesis
name: proof-first
claim: "Comparison-stage users need dense evidence before conversion."
expected_effect: "Higher confidence for evaluators, possibly lower speed for first-time users."
risk: "May feel heavy for exploratory visitors."
depends_on: [RD-R-001]
if_false_retract: [RD-DD-002, RD-DD-003]
```

### Design Decision

非自明な判断。layout、copy、component、interaction、visual hierarchy など。

```yaml
id: RD-DD-001
kind: decision
claim: "Place proof blocks before the primary CTA."
decision_area: information_architecture
depends_on: [RD-H-001]
reversibility: costly
```

### Artifact

実際の成果物。ファイル、画面、wireframe、component spec など。

```yaml
id: RD-AR-001
kind: artifact
artifact_type: react_component
path: src/app/pricing/page.tsx
based_on: [RD-DD-001, RD-DD-002]
```

### Critique

批評。

```yaml
id: RD-CR-001
kind: critique
target: RD-AR-001
claim: "CTA becomes visually secondary after proof density increases."
severity: medium
violated_relation: RD-R-002
recommendation: "Add sticky secondary CTA or strengthen CTA grouping after proof blocks."
```

## ID conventions

```text
RD-O-xxxx   Observation
RD-A-xxxx   Assumption
RD-C-xxxx   Constraint
RD-R-xxxx   Relation
RD-H-xxxx   Hypothesis
RD-DD-xxxx  Design decision
RD-AR-xxxx  Artifact
RD-CR-xxxx  Critique
RD-RV-xxxx  Revision
RD-RT-xxxx  Retraction
RD-BF-xxxx  Backflow
```

## Retraction semantics

retraction は「修正」ではない。前提・仮説・判断を無効化し、その依存先を再評価することである。

```text
If RD-A-001 is false:
  affected relations: RD-R-001, RD-R-003
  affected hypotheses: RD-H-001
  affected decisions: RD-DD-001, RD-DD-002
  affected artifacts: RD-AR-001
```

## v0.1 storage

v0.1 では `.relational-design/` 以下に保存する。

```text
.relational-design/
├── current-session.yaml
├── sessions/
│   └── 2026-07-07-pricing-redesign.yaml
├── decisions/
│   └── RD-DD-001.md
├── critiques/
│   └── RD-CR-001.md
└── events/
    └── hook-events.jsonl
```
