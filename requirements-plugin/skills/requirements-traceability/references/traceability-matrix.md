# Traceability Matrix

要件管理では、要件から下流成果物へ一方向に流すだけでは足りない。
逆方向にもたどれることを前提に行列を作る。

## 最小列

| req_id | title | law_ids | test_ids | code_symbols | telemetry | manual_checks | status |
|--------|-------|---------|----------|--------------|-----------|---------------|--------|

## 記入ルール

- `law_ids`: Law Card や制約ID
- `test_ids`: 自動テスト、property test、E2E、stateful test
- `code_symbols`: 関数、クラス、API、画面、状態遷移
- `telemetry`: event、span、log field、metric
- `manual_checks`: 手動確認ケースID
- `status`: `grounded | partial | missing`

## 判定ルール

- `grounded`: テストか観測か手動確認の少なくとも1つがあり、要件との接続が説明できる
- `partial`: 一部の接続はあるが、観測か検証が不足
- `missing`: 主要列が空

## 推奨補助列

- `confidence`: `confirmed | assumed`
- `last_verified_at`
- `changed_files`
- `notes`

## アンチパターン

- コードシンボルだけあり、検証や観測が空
- テストIDはあるが要件側の `negative_examples` と結びつかない
- `manual_checks` を付けずに人手確認前提の要件を `grounded` 扱いにする
