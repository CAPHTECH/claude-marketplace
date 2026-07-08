# Extension Roadmap

## v0.1: File-based governance

現在の範囲。

- skills
- role-bounded agents
- advisory-only hooks
- YAML / Markdown templates
- local scripts

目的は、Relational Design の reasoning protocol を検証すること。

## v0.2: Stronger hook governance

候補。

- design file glob を `.claude/relational-design-plugin.local.md`（plugin settings pattern）で細かく設定
- Write/Edit 前に current-session の存在だけでなく、active hypothesis の存在を検査
- Stop 時に incomplete trace を検出して継続を促す
- hook events から自動的に artifact node を生成

## v0.3: MCP trace store

候補 tool。

```text
create_trace_session
add_observation
add_assumption
add_relation
add_hypothesis
add_decision
add_artifact
add_critique
query_dependencies
retract_node
impact_analysis
export_trace_report
```

MCP 化の利点は、Agent が structured tool call として trace を更新できる点にある。ただし、早期に入れると storage 実装に引っ張られるため、v0.1 では外している。

## v0.4: Worktree variant orchestration

候補。

- `variant-designer-isolated` の標準運用化
- hypothesis ごとに worktree を作成
- artifact diff を relation / hypothesis に紐づける
- selected / rejected / merged / retracted を記録

## v0.5: Design-system integration

候補。

- design token extractor
- component inventory scanner
- accessibility baseline checker
- Figma MCP 連携
- Storybook / React component spec export

## v1.0: Design reasoning governance

v1.0 の目標は、単なる UI 生成支援ではない。

```text
Design reasoning becomes:
  observable
  reviewable
  retractable
  reusable
  systematizable
```
