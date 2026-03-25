---
name: permission-promoter
description: .claude/settings.local.jsonのpermissions.allowから安全なコマンドを.claude/settings.jsonに昇格させる。チーム共有設定の整理、パーミッション棚卸し、「許可を整理して」「settings.local.jsonを整理して」「パーミッションを昇格して」「permission promoter」と言われた時に使用する。
allowed-tools: Bash, Read, Write, Edit
argument-hint: "[audit|promote]"
---

# Permission Promoter

.claude/settings.local.json の permissions.allow エントリを安全性で分類し、
安全なものを .claude/settings.json に昇格させる。

対象: プロジェクトレベル（.claude/settings.local.json → .claude/settings.json）

## Step 1: 現状の収集

両ファイルを読み取り、permissions.allow の内容を把握する。

```bash
echo "=== settings.json ===" && cat .claude/settings.json 2>/dev/null || echo "(not found)"
echo "=== settings.local.json ===" && cat .claude/settings.local.json 2>/dev/null || echo "(not found)"
```

settings.local.json が存在しないか permissions.allow が空なら「昇格対象なし」で終了。

## Step 2: 安全性の分類

settings.local.json の permissions.allow 内の各エントリを、
safety-rules に従って Safe / Review / Unsafe に分類する。

分類ルール詳細 → references/safety-rules.md

各エントリを以下の形式で整理:

```
## 分類結果

### Safe（昇格推奨）
- `Bash(npm test)` — 読み取り専用テストコマンド
- `WebSearch` — 副作用なしツール

### Review（要判断）
- `Bash(npm run dev)` — 任意スクリプト実行の可能性
- `Edit(src/**)` — ファイル編集権限

### Unsafe（昇格非推奨）
- `Bash(rm -rf *)` — 破壊的操作
```

分類の根拠を1行で添える。

## Step 2.5: 汎用化の提案

specifier内に環境固有の値が含まれるエントリを検出し、汎用パターンへの置換を提案する。

汎用化ルール → references/generalization-rules.md

汎用化が必要なエントリは、元のエントリと提案パターンを並べて表示:

```
### 汎用化の提案
- `Bash(cat /Users/rizumita/project/src/main.ts)` → `Bash(cat *)`
- `Read(/Users/rizumita/project/src/config.ts)` → `Read(src/**)`
- `Bash(cd /Users/rizumita/project && npm test)` → `Bash(npm test *)`
```

ユーザーが提案を承認した場合、汎用化後のエントリで昇格する。
拒否した場合、元のエントリのまま（昇格するかどうかはStep 3で判断）。

## Step 3: ユーザー確認

分類結果を提示し、昇格対象をユーザーに選択させる。

AskUserQuestionを使う:
- Safe分類のエントリは昇格推奨としてリスト
- Review分類のエントリは個別判断を求める
- Unsafe分類のエントリは警告付きで表示（昇格非推奨の理由を明記）

ユーザーが選択しなかったエントリはsettings.local.jsonに残す。

## Step 4: 昇格の実行

ユーザーが承認したエントリについて:

1. settings.json が存在しない場合は `{"permissions":{"allow":[]}}` で初期化
2. settings.json の permissions.allow に追加（重複チェック）
3. settings.local.json の permissions.allow から削除
4. settings.local.json の permissions.allow が空になったら permissions キー自体を削除
5. settings.local.json が `{}` になったらファイル自体を削除

JSONの整形は jq を使う。一時ファイルは mktemp で安全に作成:

```bash
# settings.json が存在しない場合の初期化
[ -f .claude/settings.json ] || echo '{}' > .claude/settings.json

# settings.json への追加例
tmp=$(mktemp) && jq '.permissions.allow += ["NewEntry"] | .permissions.allow |= unique' .claude/settings.json > "$tmp" && mv "$tmp" .claude/settings.json
```

## Step 5: 結果の報告

変更内容を簡潔に報告:
- 昇格したエントリ一覧
- settings.local.json に残ったエントリ一覧（あれば）
- 「git diff .claude/settings.json で差分を確認してください」と案内

## audit モード

引数に `audit` を指定した場合、Step 1〜2 の分類のみ実行し、変更は行わない。
現状のパーミッション構成と安全性評価レポートを出力する。
