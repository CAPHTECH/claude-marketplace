# Safety Rules

permissions.allow エントリの安全性分類ルール。

## 分類: Safe（自動で昇格候補）

副作用なし・読み取り専用のエントリ。

### ツール系（引数なし）
- `Read`, `Glob`, `Grep`, `WebSearch`
- `Agent(Explore)`, `Agent(Plan)`

### Bash: 読み取り専用コマンド
パターンマッチで判定。以下のプレフィックスで始まるもの:
- `git log *`, `git status *`, `git diff *`, `git branch *`, `git show *`, `git remote *`
- `ls *`, `cat *`, `head *`, `tail *`, `wc *`, `file *`, `which *`, `type *`
- `date *`, `whoami`, `pwd`, `uname *`, `hostname`
- `node --version`, `python3 --version`, `ruby --version`
- `* --version`, `* --help`, `* -v`, `* -h`
- `npm list *`, `npm ls *`, `npm view *`, `npm info *`, `npm outdated *`
- `cargo --version`, `rustc --version`, `go version`
- `jq *`, `yq *`

### Bash: ビルド・テスト系（出力のみ）
- `npm test *`, `npm run test *`, `npm run lint *`, `npm run check *`, `npm run build *`
- `npx tsc *`, `npx eslint *`, `npx prettier --check *`
- `cargo test *`, `cargo check *`, `cargo clippy *`, `cargo build *`
- `go test *`, `go vet *`, `go build *`
- `swift build *`, `swift test *`, `xcodebuild *`
- `pytest *`, `python3 -m pytest *`, `ruff *`, `mypy *`, `black --check *`
- `make test *`, `make check *`, `make build *`, `make lint *`

### MCP: 読み取り専用ツール
- `mcp__*` で末尾が `query`, `search`, `list`, `get`, `read`, `fetch`, `status` のもの

### Read/Edit パス指定
- `Read(*)` — 読み取りは常に安全
- `Glob(*)`, `Grep(*)` — 検索は常に安全

## 分類: Review（ユーザー判断が必要）

副作用の可能性があるが、開発ワークフローで一般的。

### Bash: 書き込み系コマンド
- `npm install *`, `npm ci *`, `npm run *`（test/lint/check/build以外）
- `git add *`, `git commit *`, `git push *`, `git checkout *`, `git switch *`
- `cargo install *`, `pip install *`, `gem install *`
- `mkdir *`, `cp *`, `mv *`, `touch *`
- `echo *`, `printf *` — リダイレクトでファイル書き込みの可能性
- `node -e *`, `node --eval *` — 任意コード実行
- ワイルドカードを含むBashエントリ（`Bash(*)` 等の広範なもの）

### ツール系
- `WebFetch` — 引数なしは任意URLアクセス可能（データ送信リスク）
- `WebFetch(domain:*)` — ドメイン指定あり
- `Edit(*)`, `Write(*)` — パス指定付き編集・書き込み
- `Agent(*)` — カスタムエージェント
- `mcp__*` — Safe分類に該当しないMCPツール

## 分類: Unsafe（昇格非推奨、警告付き）

破壊的操作やセキュリティリスク。チーム共有設定に入れるべきでない。

### Bash: 破壊的コマンド
- `rm *`, `rmdir *`
- `git reset *`, `git clean *`, `git push --force *`, `git push -f *`
- `chmod *`, `chown *`
- `kill *`, `pkill *`
- `docker rm *`, `docker rmi *`
- `sudo *`, `su *`
- `curl * | *sh*`（パイプ経由の実行）

### 広範すぎるパーミッション（チーム共有に不適切）
- `Bash` 単体（全コマンド許可）
- `Edit` 単体（全ファイル編集許可）
- `Write` 単体（全ファイル書き込み許可）
- `Agent` 単体（全エージェント許可）

## 判定アルゴリズム

1. エントリを `Tool` と `(specifier)` に分解
2. Tool名で大分類（Bash / Read / Edit / MCP / その他）
3. specifier をSafe → Unsafe → Reviewの順でパターンマッチ
4. マッチしなければ Review に分類
