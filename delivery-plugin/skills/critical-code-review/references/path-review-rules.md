# Path-Based Review Rules

ファイルパスに基づいてレビュー観点を自動ルーティングする。

## デフォルトルール

| パスパターン | レビュー重点 | 追加チェック |
|-------------|-------------|-------------|
| `**/auth/**`, `**/login/**`, `**/session/**` | Security (認証・認可) | OWASP Auth Cheatsheet準拠 |
| `**/api/**`, `**/routes/**`, `**/handlers/**` | Security (入力検証), Reliability | エンドポイント認可、入力バリデーション |
| `**/middleware/**` | Security, Reliability | エラーハンドリング、チェーン順序 |
| `**/db/**`, `**/models/**`, `**/migrations/**` | Data Integrity | トランザクション、マイグレーション可逆性 |
| `**/repositories/**`, `**/dao/**` | Data Integrity, Performance | N+1, クエリ効率 |
| `**/config/**`, `**/env/**` | Security (秘密情報) | ハードコード秘密鍵、デフォルト値の安全性 |
| `**/components/**`, `**/pages/**`, `**/views/**` | UI/UX, Performance | アクセシビリティ、再レンダリング |
| `**/hooks/**` | Reliability, Performance | 依存配列、クリーンアップ |
| `**/utils/**`, `**/helpers/**`, `**/lib/**` | Type Safety, Design | 汎用性、エッジケース |
| `**/test/**`, `**/spec/**`, `**/__tests__/**` | Maintainability | テスト品質（フレーキー、モック過多） |
| `**/infra/**`, `**/deploy/**`, `**/ci/**` | Security, Reliability | 秘密管理、冪等性 |
| `**/types/**`, `**/interfaces/**` | Type Safety, Design | 型の表現力、互換性 |
| `**/workers/**`, `**/jobs/**`, `**/queues/**` | Reliability, Data Integrity | 冪等性、タイムアウト、リトライ |
| `Dockerfile*`, `docker-compose*` | Security, Reliability | ベースイメージ安全性、マルチステージ |
| `*.proto`, `*.graphql`, `*.openapi.*` | Design, Type Safety | 後方互換性、命名規則 |

## ルールの適用方法

1. 変更ファイルのパスを各パターンと照合
2. 一致したルールのレビュー重点をPhase 3に伝達
3. 複数ルールが一致する場合はすべて適用（Union）
4. 一致なしの場合はデフォルト観点（全カテゴリ均等）を使用

## カスタムルール

プロジェクト固有のルールは `.claude/review-rules.yml` で定義可能。

```yaml
# .claude/review-rules.yml
rules:
  - path: "src/billing/**"
    focus: [DataIntegrity, Security]
    note: "金額計算は浮動小数点を避けること"

  - path: "src/notifications/**"
    focus: [Reliability]
    note: "通知の重複送信・欠損に注意"

  - path: "*.sql"
    focus: [Security, Performance]
    note: "動的SQLは禁止、プリペアドステートメント必須"
```

カスタムルールが存在する場合、デフォルトルールに加えて適用する（Override ではなく Merge）。
