# Plugin 案レビューと修正方針

## レビュー対象

前案は、単一 Skill ではなく Claude Code Plugin として以下を束ねる構成だった。

- orchestrator skill
- 複数 subagent
- hooks
- scripts
- 将来的な MCP trace store
- worktree variant

方向性は正しい。ただし、そのまま実装すると v0.1 としては重すぎる。特に、初期段階から MCP・強制 hook・worktree 分岐を入れると、運用上の摩擦が大きく、Agent がデザインする前に儀式的な trace を作る状態になりやすい。

## 修正 1: 単一 orchestrator ではなく「入口 Skill + 専門 Skill」へ

前案では `design-trace` がほぼ全責務を持つ構成だった。修正版では、入口は `design-trace` のまま維持しつつ、以下を別 Skill に分離した。

- `design-review`: 批評専用
- `design-retract`: 撤回・影響分析専用
- `design-system-backflow`: design system への戻し専用

理由は、デザイン作業には「作る」「見る」「戻す」「再利用化する」があり、それぞれ異なる評価軸を持つためである。単一 Skill に押し込むと、生成の都合で批評や撤回が弱くなる。

## 修正 2: agent は「思考分業」ではなく「汚染経路の分離」として設計

subagent を増やすこと自体には価値がない。価値が出るのは、以下が分かれる場合だけである。

- 観察する agent
- 関係を抽出する agent
- 仮説を作る agent
- UI を作る agent
- 批評する agent
- 実装制約を見る agent
- trace を記録する agent
- 撤回影響を見る agent

修正版では、各 agent に「してはいけないこと」を明記した。特に以下を強制している。

- `context-reader`: 提案禁止
- `relation-mapper`: UI 生成禁止
- `hypothesis-generator`: 実装禁止
- `variant-designer`: 新規仮説の勝手な作成禁止
- `design-critic`: 編集禁止
- `trace-archivist`: 判断禁止
- `retraction-analyst`: 修正実装禁止

これは Relational 的には、責務の分割ではなく、前提・仮説・副作用の混線を防ぐための境界である。

## 修正 3: hooks は advisory-only にした

前案では、hooks による trace 強制を中心に置いていた。しかし v0.1 で強制しすぎると、現場では次の問題が出る。

- 小さな UI 修正にも trace session が必要になる
- hook が誤検出したときに作業が止まる
- Agent が trace を後付けで作るようになり、品質が上がらない
- Claude Code のバージョン差や OS 差で friction が増える

そのため、修正版では advisory-only に一本化した。当初は plugin option 経由の `enforce_trace` トグルで強制モードに切り替えられる想定だったが、`userConfig` / `CLAUDE_PLUGIN_OPTION_*` は実在する Claude Code の仕組みではなく、設定しても hook 側に値が渡らず何も起きない死んだ設定だったため v0.1 では削除した。強制が必要になったら `.claude/relational-design-plugin.local.md`（plugin settings pattern）を hook から読む形で実装し直す。

## 修正 4: MCP は v0.1 から外した

MCP trace store は魅力的だが、v0.1 では外した。理由は以下。

1. 最初に検証すべきなのは storage ではなく reasoning protocol である。
2. YAML / Markdown trace で十分に人間レビューできる。
3. MCP を入れると install / runtime / permission の確認点が増える。
4. Relational の本質は「記録媒体」ではなく「依存関係の分離と撤回可能性」である。

v0.2 以降で `create_trace_session`, `add_relation`, `query_dependencies`, `impact_analysis` などを MCP tool 化する余地は残している。

## 修正 5: worktree variant は標準ではなく Deep mode のみにした

worktree isolation は、仮説別 UI 案の比較には強い。一方で、すべてのデザイン作業に使うには重い。

したがって、通常の `variant-designer` とは別に `variant-designer-isolated` を用意し、Deep mode の仮説別実装だけで使う構成にした。

## 修正 6: trace id を成果物に埋め込みすぎない

前案では「non-trivial design decision に ID を付ける」方針が強かった。これは正しいが、React component や CSS にすべてコメントとして ID を埋め込むと、実装が汚れる。

修正版では、trace id の主な置き場を `.relational-design/` 以下にし、必要なときだけコードコメントに `RD-DD-xxxx` を書く方針にした。

## 修正後の v0.1 成功条件

v0.1 が成功しているかは、UI の見た目ではなく以下で判定する。

1. 観察と仮説が分離されている。
2. design hypotheses が style variant ではなく relation-based variant になっている。
3. デザイン判断が relation / hypothesis / constraint に依存している。
4. 批評が好みではなく relation に戻っている。
5. 仮説が間違っていた場合に、撤回すべき判断が分かる。
6. 一回限りの成果物から、再利用可能な token / component / pattern が抽出される。
