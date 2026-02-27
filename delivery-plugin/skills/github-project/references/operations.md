# GitHub Project 操作リファレンス

## ID取得の手順

フィールド更新には3種類のIDが必要:

| ID種別 | 取得コマンド | 用途 |
|--------|-------------|------|
| project_id | `gh project view N --owner O --format json --jq '.id'` | item-editの--project-id |
| field_id | `gh project field-list N --owner O --format json` | item-editの--field-id |
| item_id | `gh project item-list N --owner O --format json` | item-editの--id |

## フィールドタイプ別の更新方法

### Single Select（Status等）

```bash
# 1. フィールドとオプションを取得
gh project field-list NUMBER --owner OWNER --format json | \
  jq '.fields[] | select(.name=="Status") | {id, options}'

# 出力例:
# {
#   "id": "PVTSSF_xxx",
#   "options": [
#     {"id": "opt_todo", "name": "Todo"},
#     {"id": "opt_inprog", "name": "In Progress"},
#     {"id": "opt_done", "name": "Done"}
#   ]
# }

# 2. 更新
gh project item-edit \
  --id ITEM_ID \
  --project-id PROJECT_ID \
  --field-id PVTSSF_xxx \
  --single-select-option-id opt_done
```

### Text

```bash
gh project item-edit \
  --id ITEM_ID \
  --project-id PROJECT_ID \
  --field-id FIELD_ID \
  --text "テキスト値"
```

### Number

```bash
gh project item-edit \
  --id ITEM_ID \
  --project-id PROJECT_ID \
  --field-id FIELD_ID \
  --number 42
```

### Date

```bash
gh project item-edit \
  --id ITEM_ID \
  --project-id PROJECT_ID \
  --field-id FIELD_ID \
  --date "2025-01-15"
```

### Iteration（スプリント等）

```bash
# iteration-idはfield-listから取得
gh project item-edit \
  --id ITEM_ID \
  --project-id PROJECT_ID \
  --field-id FIELD_ID \
  --iteration-id ITERATION_ID
```

### フィールド値のクリア

```bash
gh project item-edit \
  --id ITEM_ID \
  --project-id PROJECT_ID \
  --field-id FIELD_ID \
  --clear
```

## jqクエリ例

### アイテムのタイトルとステータス一覧

```bash
gh project item-list NUMBER --owner OWNER --format json | \
  jq '.items[] | {title: .content.title, status: .status}'
```

### 特定ステータスのアイテム抽出

```bash
gh project item-list NUMBER --owner OWNER --format json | \
  jq '.items[] | select(.status == "In Progress")'
```

### Issue URLからアイテムIDを検索

```bash
gh project item-list NUMBER --owner OWNER --format json | \
  jq --arg url "https://github.com/owner/repo/issues/123" \
  '.items[] | select(.content.url == $url) | .id'
```

## エラー対処

### "Resource not accessible by personal access token"

```bash
gh auth refresh -s project
```

### アイテムが見つからない

- `--limit` を増やす（デフォルト30）
- アーカイブ済みアイテムは表示されない

### フィールド更新が反映されない

- project_id, field_id, item_id が正しいか確認
- Single Selectの場合はoption_idも必要
