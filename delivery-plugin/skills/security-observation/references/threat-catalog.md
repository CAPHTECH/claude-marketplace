# 脅威カタログ

## OWASP Top 10 (2021)

| # | 脆弱性 | 観測方法 |
|---|--------|---------|
| A01 | アクセス制御の不備 | 認可の否定テスト |
| A02 | 暗号化の失敗 | 設定レビュー、静的解析 |
| A03 | インジェクション | 入力汚染テスト、SAST |
| A04 | 安全でない設計 | 脅威分析、設計レビュー |
| A05 | セキュリティ設定ミス | 設定スキャン |
| A06 | 脆弱なコンポーネント | 依存脆弱性スキャン |
| A07 | 識別・認証の失敗 | 認証テスト |
| A08 | 整合性確認の失敗 | 署名検証テスト |
| A09 | ログ・監視の失敗 | ログレビュー |
| A10 | SSRF | 入力汚染テスト |

## インジェクション攻撃ペイロード

### SQLインジェクション

```
' OR '1'='1
'; DROP TABLE users; --
' UNION SELECT * FROM users --
1; WAITFOR DELAY '00:00:10'--
```

### XSS（クロスサイトスクリプティング）

```html
<script>alert('xss')</script>
<img src=x onerror=alert('xss')>
<svg onload=alert('xss')>
javascript:alert('xss')
```

### パストラバーサル

```
../../../etc/passwd
..\..\..\..\windows\system32\config\sam
....//....//....//etc/passwd
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd
```

### コマンドインジェクション

```
; ls -la
| cat /etc/passwd
`whoami`
$(id)
```

### SSTIテンプレートインジェクション）

```
{{7*7}}
${7*7}
<%= 7*7 %>
#{7*7}
```

## 認可テストマトリクス

```markdown
## 認可テストチェックリスト

### 垂直権限昇格
- [ ] 一般ユーザーが管理者機能にアクセスできないこと
- [ ] 未認証ユーザーが認証必須エンドポイントにアクセスできないこと

### 水平権限昇格
- [ ] ユーザーAがユーザーBのリソースにアクセスできないこと
- [ ] IDを変更してもアクセス制御が機能すること

### 機能レベル
- [ ] 各エンドポイントに適切な認可チェックがあること
- [ ] APIとUIで同じ認可ルールが適用されること

### オブジェクトレベル
- [ ] リソースIDを推測してもアクセスできないこと
- [ ] バッチ操作でも認可チェックが機能すること
```

## Secret検出パターン

### gitleaks設定例

```toml
# .gitleaks.toml
title = "gitleaks config"

[[rules]]
id = "aws-access-key"
description = "AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''

[[rules]]
id = "aws-secret-key"
description = "AWS Secret Key"
regex = '''(?i)aws(.{0,20})?(?-i)['\"][0-9a-zA-Z\/+]{40}['\"]'''

[[rules]]
id = "github-token"
description = "GitHub Token"
regex = '''ghp_[0-9a-zA-Z]{36}'''

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '''(?i)(api[_-]?key|apikey|secret[_-]?key)[\s]*[=:]\s*['\"][0-9a-zA-Z]{16,}['\"]'''

[allowlist]
paths = [
  '''\.test\.''',
  '''_test\.go$''',
  '''\.spec\.''',
  '''__mocks__'''
]
```

## 暗号化のチェックリスト

```markdown
## 暗号化観測チェックリスト

### 使用してはいけない
- [ ] MD5（ハッシュ用途）
- [ ] SHA1（署名用途）
- [ ] DES / 3DES
- [ ] RC4
- [ ] ECBモード

### 推奨
- [ ] パスワードハッシュ: bcrypt / Argon2
- [ ] 一般ハッシュ: SHA-256以上
- [ ] 対称暗号: AES-256-GCM
- [ ] 非対称暗号: RSA-2048以上 / Ed25519

### 乱数
- [ ] 暗号用途には暗号論的疑似乱数生成器（CSPRNG）を使用
- [ ] Math.random() / rand() を秘密生成に使用していないこと
```

## 監査ログの要件

```markdown
## 監査ログに含めるべき情報

### 必須
- timestamp (ISO8601)
- actor (who)
- action (what)
- resource (on what)
- result (success/failure)
- source_ip

### 推奨
- correlation_id
- session_id
- user_agent
- request_id

### 記録すべきイベント
- 認証成功/失敗
- 認可失敗
- 権限変更
- データ変更（CRUD）
- 設定変更
- 機密データアクセス
```
