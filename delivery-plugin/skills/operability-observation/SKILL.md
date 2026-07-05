---
name: operability-observation
context: fork
description: "運用観測性の確保。ログ、メトリクス、ヘルスチェック、設定検証でバグを扱う能力を担保。Use when: デプロイ前チェック、障害調査が困難、原因不明、ログ設計、メトリクス設計、設定管理実装。"
---

# Operability Observation（運用観測性）

## 目的

運用不能は「バグそのもの」ではなく、**バグや障害を扱う能力の欠如**。
このスキルは、MTTR（復旧時間）を下げ、フィードバックループを閉じる。

## 観測の恩恵

- MTTR（復旧時間）を下げる
- 失敗が起きたときの"次の一手"が見える
- 本番でのフィードバックが仕様・テストへ戻り、精度向上ループが閉じる

## Procedure

### Step 1: 起動時設定検証（Fail Fast）

設定が検証されず起動後に壊れるのを防ぐ。必須設定の欠落、型・範囲・形式の不正を起動時に検知し、検証に失敗したら即座に終了する。

### Step 2: ヘルスチェックの実装

オーケストレータが正しく扱えるようにする：

```python
# Liveness: プロセスが生きているか
@app.get("/health/live")
def liveness():
    return {"status": "ok"}

# Readiness: リクエストを受け付けられるか
@app.get("/health/ready")
async def readiness():
    checks = {
        "database": await check_db_connection(),
        "cache": await check_cache_connection(),
        "external_api": await check_external_api(),
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if all_healthy else "not_ready", "checks": checks}
    )
```

### Step 3: 構造化ログの実装

相関ID、操作名、結果、エラー分類を含めた構造化ログ（JSON形式）を出力する。エラーログにはエラー分類（validation_error / policy_violation / invariant_broken 等）を含める。

### Step 4: 基本メトリクスの設定

最低限必要なメトリクス：

| メトリクス | 種別 | 説明 |
|-----------|------|------|
| request_latency_seconds | Histogram | リクエスト処理時間 |
| request_total | Counter | リクエスト数（status, endpoint別） |
| error_total | Counter | エラー数（error_type別） |
| active_connections | Gauge | アクティブ接続数 |
| queue_depth | Gauge | キュー深度（飽和の兆候） |

### Step 5: エラー分類の設計

エラーを適切に分類し、対処可能にする：

| エラー分類 | 説明 | 対処 |
|-----------|------|------|
| validation_error | 入力検証失敗 | クライアント修正 |
| policy_violation | ビジネスルール違反 | 操作変更 |
| invariant_broken | 内部整合性違反 | 調査必要 |
| external_error | 外部システム障害 | リトライ/待機 |
| internal_error | 内部エラー | 即座に調査 |

## 最小セット

- **(F1)** 起動時設定検証（fail fast）
- **(F2)** ヘルスチェック（liveness/readiness）
- **(F3)** 構造化ログ ＋ 相関ID ＋ エラー分類
- **(F4)** 最低限のメトリクス（エラー率・レイテンシ・飽和のどれか2つでも）

## 運用チェックリスト

詳細は references/operability-checklist.md を参照。

## Outputs

- 設定スキーマ（Pydantic / Zod / JSON Schema等）
- ヘルスチェックエンドポイント実装
- 構造化ログ設定
- メトリクス設定
- エラー分類定義

## Examples

### Kubernetes ヘルスチェック設定

Liveness/Readinessプローブの設定例は references/operability-checklist.md を参照。
