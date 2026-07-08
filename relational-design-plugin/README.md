# Relational Design Plugin

Relational Design は、Claude Code 上で UI/UX・フロントエンド・デザインシステム関連の作業を行うときに、デザイン判断を **traceable / isolable / retractable** にするための Claude Code Plugin です。

この plugin は「良い見た目を素早く出す」ことを第一目的にしていません。目的は、Agent が行ったデザイン判断を、あとから検証・分離・撤回・再利用できる状態にすることです。

## 何を含むか

```text
relational-design-plugin/
├── .claude-plugin/plugin.json
├── skills/
│   ├── design-trace/
│   ├── design-review/
│   ├── design-retract/
│   └── design-system-backflow/
├── agents/
│   ├── context-reader.md
│   ├── relation-mapper.md
│   ├── hypothesis-generator.md
│   ├── variant-designer.md
│   ├── variant-designer-isolated.md
│   ├── design-critic.md
│   ├── implementation-verifier.md
│   ├── trace-archivist.md
│   └── retraction-analyst.md
├── hooks/hooks.json
├── scripts/
│   ├── trace-hook.py
│   ├── trace-check.py
│   └── trace-report.py
├── templates/
└── docs/
```

## 中心思想

通常のデザイン生成では、次のものが一つの文脈に混ざりがちです。

- ユーザーの依頼
- 事業目的
- ユーザー状態
- 競合観察
- 見た目の好み
- 実装制約
- Agent が置いた仮説
- 生成された UI
- 批評
- 修正理由

Relational Design はこれらを分離します。

```text
Observed input
  -> Relation map
  -> Design hypotheses
  -> Design decisions
  -> Artifact
  -> Critique
  -> Retraction / Backflow
```

## 最初の使い方

1. このフォルダを Claude Code の plugin として読み込める場所に置く。
2. Claude Code で plugin を有効化する。
3. UI/UX 作業で `/relational-design-plugin:design-trace` を呼ぶ、または通常依頼の中で「Relational Design で進めて」と指示する。
4. 生成された `.relational-design/current-session.yaml` と `sessions/` をレビューする。

## 推奨モード

- **Light**: 小さな UI 修正。assumptions / decisions / critique のみ。
- **Standard**: 通常の画面設計。relation map / hypotheses / artifact / critique。
- **Deep**: 重要な LP、主要導線、デザインシステム変更。subagent 分担、必要なら isolated variant worktree。

## Hooks の挙動

同梱 hooks は **advisory-only** です。デザイン関連ファイルの編集を観測し、必要に応じて Claude に trace 作成を促しますが、編集を拒否したり止めたりすることはありません。v0.1 では enforce モード（trace session がない場合に Write/Edit を拒否する）は提供していません。

## 重要な設計判断

この plugin は v0.1 では MCP server を含めていません。理由は、初期段階で MCP を入れると、trace store の実装に引っ張られて、最も重要な「観察・関係・仮説・判断・批評の責務分離」が曖昧になるためです。v0.2 以降で必要になったら追加する想定です。

## 主要コマンド相当の Skill

- `/relational-design-plugin:design-trace`  
  デザイン作業の入口。brief を分解し、必要な agent を使い分ける。

- `/relational-design-plugin:design-review`  
  既存 UI / 実装 / 画面案を relation に戻して批評する。

- `/relational-design-plugin:design-retract`  
  前提が崩れたとき、どの判断・UI・copy・component を撤回すべきか分析する。

- `/relational-design-plugin:design-system-backflow`  
  一回限りの画面から token / component / pattern / copy rule を抽出する。

## 手動検査

```bash
python3 scripts/trace-check.py --root .relational-design
python3 scripts/trace-report.py --root .relational-design
```

## ライセンス

MIT
