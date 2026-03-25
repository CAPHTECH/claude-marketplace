# Generalization Rules

settings.local.json のエントリを settings.json（チーム共有）に昇格する際、
環境固有の値を汎用パターンに置換するルール。

## 検出パターン

### 1. 絶対パス

ホームディレクトリやプロジェクトルートの絶対パスを含むエントリ。

検出: `/Users/`, `/home/`, `/tmp/`, `C:\` 等のパスプレフィックス

| 元のエントリ | 汎用化 |
|---|---|
| `Read(/Users/alice/project/src/main.ts)` | `Read(src/**)` |
| `Read(/Users/alice/project/config/app.json)` | `Read(config/**)` |
| `Bash(cat /Users/alice/project/src/utils.ts)` | `Bash(cat *)` |
| `Bash(python3 /Users/alice/project/scripts/gen.py)` | `Bash(python3 scripts/*)` |

**置換方針**:
- Read/Glob/Grep: プロジェクトルートからの相対パスに変換し、ファイル名を `**` に
- Bash: コマンド部分を残し、パス引数を `*` に。コマンド自体の意図を保つ

### 2. ユーザー名・ホスト名

specifier内にユーザー名やホスト名がハードコードされている。

検出: `whoami` の出力値、`hostname` の出力値と一致する文字列

| 元のエントリ | 汎用化 |
|---|---|
| `Bash(ssh alice@dev-server)` | `Bash(ssh *)` |
| `WebFetch(domain:alice-dev.local)` | 個別判断（チーム共通ならそのまま） |

### 3. 特定ファイル名 → ワイルドカード

同じコマンドの異なるファイルが複数ある場合、ワイルドカードに統合。

検出: 同じ `Tool(command` プレフィックスで末尾だけ異なるエントリが2つ以上

| 元のエントリ群 | 汎用化 |
|---|---|
| `Bash(cat src/a.ts)`, `Bash(cat src/b.ts)` | `Bash(cat *)` |
| `Edit(src/a.ts)`, `Edit(src/b.ts)` | `Edit(src/**)` |
| `Read(docs/a.md)`, `Read(docs/b.md)` | `Read(docs/**)` |

### 4. cd + コマンドのパターン

`cd /absolute/path && command` パターンを検出し、コマンド部分だけに簡略化。

| 元のエントリ | 汎用化 |
|---|---|
| `Bash(cd /Users/alice/project && npm test)` | `Bash(npm test *)` |
| `Bash(cd /Users/alice/project && cargo build)` | `Bash(cargo build *)` |

## 汎用化しないケース

以下は環境固有に見えても汎用化しない:

- **プロジェクト内の相対パス**: `Read(src/**)`, `Edit(config/**)` — すでに汎用的
- **ドメイン指定の WebFetch**: `WebFetch(domain:github.com)` — チーム共通の外部サービス
- **引数なしのツール**: `WebSearch`, `Read`, `Glob` — 汎用化の余地なし
- **MCP ツール名**: `mcp__server__tool` — サーバー名はチーム共通

## 提案時の注意

- 汎用化は「提案」であり、ユーザーが最終判断する
- 汎用化によりスコープが広がりすぎる場合は警告を添える
  - 例: `Bash(cat src/config.ts)` → `Bash(cat *)` はスコープが広い。`Bash(cat src/*)` を代案として提示
- 元のエントリを残す選択肢も常に提供する（settings.local.jsonに残留）
