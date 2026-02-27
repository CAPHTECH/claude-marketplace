# 言語別修正戦略

## 修正優先順位

全言語共通: **lint → type → build → test** の順序を厳守する。

## JS/TS

| カテゴリ | 自動修正 | 手動修正 |
|----------|---------|---------|
| lint | `npx eslint --fix .` / `npx prettier --write .` | 自動修正不可のルール違反をコード編集 |
| type | - | TSエラーメッセージから型定義を修正 |
| build | `npm install` | import パス・モジュール名を修正 |
| test | - | テストコード or 実装コードを修正 |

### 検出ヒント
- package.json の存在で判定
- tsconfig.json があれば TypeScript
- .eslintrc* / eslint.config.* でESLint設定確認

## Python

| カテゴリ | 自動修正 | 手動修正 |
|----------|---------|---------|
| lint | `ruff check --fix .` / `black .` | 自動修正不可のルール違反をコード編集 |
| type | - | mypy エラーから型アノテーションを修正 |
| build | `pip install -r requirements.txt` | import を修正 |
| test | - | テストコード or 実装コードを修正 |

### 検出ヒント
- pyproject.toml / setup.py / requirements.txt の存在で判定
- ruff.toml / .ruff.toml で Ruff 設定確認
- mypy.ini / pyproject.toml [tool.mypy] で mypy 設定確認

## Go

| カテゴリ | 自動修正 | 手動修正 |
|----------|---------|---------|
| lint | `go fmt ./...` / `golangci-lint run --fix` | 自動修正不可のルール違反をコード編集 |
| type | - | コンパイルエラーから型を修正 |
| build | `go mod tidy` | import パスを修正 |
| test | - | テストコード or 実装コードを修正 |

### 検出ヒント
- go.mod の存在で判定
- .golangci.yml で golangci-lint 設定確認

## Flutter

| カテゴリ | 自動修正 | 手動修正 |
|----------|---------|---------|
| lint | `dart fix --apply` / `dart format .` | dart analyze の指摘をコード編集 |
| type | - | dart analyze (error) から型を修正 |
| build | `flutter pub get` / `flutter clean && flutter pub get` | ネイティブ設定エラーを修正 |
| test | - | ウィジェットテスト or ユニットテストを修正 |

### 検出ヒント
- pubspec.yaml の存在で判定
- analysis_options.yaml で lint 設定確認

## Elixir

| カテゴリ | 自動修正 | 手動修正 |
|----------|---------|---------|
| lint | `mix format` | credo の指摘をコード編集 |
| type | - | Dialyzer 警告から @spec を修正 |
| build | `mix deps.get` / `mix compile --force` | モジュール参照を修正 |
| test | - | ExUnit テストを修正 |

### 検出ヒント
- mix.exs の存在で判定
- .credo.exs で Credo 設定確認

## 自動修正実行のガイドライン

1. **自動修正ツールは最初に実行**: 手動修正の前に自動修正ツールを試す
2. **実行結果を確認**: 自動修正後に変更内容を `git diff` で確認
3. **段階的に修正**: 1カテゴリずつ修正し、各ステップでローカル検証
4. **ローカル検証コマンド**: CI と同じチェックをローカルで実行してから push
