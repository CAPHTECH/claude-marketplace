# Category Taxonomy（suspected_categories 標準タグ）

Issue分類に使用する標準カテゴリタグ。

## 機能カテゴリ

### 認証/認可

| タグ | 説明 |
|------|------|
| `auth_failure` | 認証失敗 |
| `auth_bypass` | 認証バイパス（セキュリティ） |
| `authorization_error` | 認可エラー |
| `session_issue` | セッション問題 |
| `token_issue` | トークン問題 |
| `sso_issue` | SSO連携問題 |

### データ

| タグ | 説明 |
|------|------|
| `data_loss` | データ損失 |
| `data_corruption` | データ破損 |
| `data_inconsistency` | データ不整合 |
| `data_validation` | バリデーション問題 |

### パフォーマンス

| タグ | 説明 |
|------|------|
| `slow_response` | レスポンス遅延 |
| `timeout` | タイムアウト |
| `memory_issue` | メモリ問題 |
| `resource_exhaustion` | リソース枯渇 |

### UI/UX

| タグ | 説明 |
|------|------|
| `display_issue` | 表示問題 |
| `layout_broken` | レイアウト崩れ |
| `usability_issue` | 操作性問題 |
| `accessibility` | アクセシビリティ |
| `localization` | 多言語/ロケール |

### API/連携

| タグ | 説明 |
|------|------|
| `api_error` | APIエラー |
| `integration_failure` | 外部連携失敗 |
| `webhook_issue` | Webhook問題 |
| `sync_issue` | 同期問題 |

### インフラ/運用

| タグ | 説明 |
|------|------|
| `deployment_issue` | デプロイ問題 |
| `configuration_issue` | 設定問題 |
| `infrastructure` | インフラ問題 |
| `monitoring_gap` | 監視不足 |

### セキュリティ

| タグ | 説明 |
|------|------|
| `security_vulnerability` | 脆弱性 |
| `credential_exposure` | 認証情報露出 |
| `injection` | インジェクション |
| `xss` | クロスサイトスクリプティング |
| `csrf` | CSRF |

## 原因カテゴリ

| タグ | 説明 |
|------|------|
| `regression` | 回帰（以前は動いていた） |
| `edge_case` | エッジケース |
| `race_condition` | 競合状態 |
| `null_handling` | NULL/未定義処理 |
| `boundary_condition` | 境界条件 |
| `dependency_issue` | 依存関係問題 |
| `version_mismatch` | バージョン不整合 |
| `environment_specific` | 環境固有 |

## 要求カテゴリ（Enhancement用）

| タグ | 説明 |
|------|------|
| `feature_request` | 機能追加要求 |
| `improvement` | 改善要求 |
| `documentation` | ドキュメント要求 |
| `refactoring` | リファクタリング要求 |

## 使用ルール

1. **複数タグ可**: 1つのIssueに複数タグを付与可能
2. **最も具体的なタグを優先**: `auth_failure` > `auth_*` > 一般
3. **推測の場合は接尾辞**: `auth_failure_suspected`（確証がない場合）
4. **セキュリティは必ず付与**: セキュリティ関連の兆候があれば必ずタグ付け
