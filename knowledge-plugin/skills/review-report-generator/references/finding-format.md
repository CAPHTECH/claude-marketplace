# 指摘の標準形式（詳細）

各指摘を以下のYAML形式に整形する。review.yaml の内容をこの形式にマッピングすること。

## 完全なYAML例

```yaml
finding:
  id: FINDING-001
  title: payment-serviceタイムアウト不整合

  # 1. 影響範囲
  scope:
    type: interaction  # component/interaction/crosscutting
    affected:
      - order-service -> payment-service

  # 2. 何が成立しなくなるか
  failure_mode:
    description: |
      order-serviceがタイムアウトしてもpayment-serviceは処理を続行。
      二重課金が発生する可能性がある。
    impact:
      - ユーザーへの影響: 二重請求
      - ビジネスへの影響: 返金対応コスト、信頼低下
      - システムへの影響: 不整合データの発生

  # 3. 発生条件
  trigger_conditions:
    - 高負荷時（>500 RPS）
    - payment-gateway遅延時（>20s）
    - ネットワーク不安定時

  # 4. 根拠（推測禁止）
  evidence:
    - source: component-dossiers/order-service.yaml
      field: failure_modes[0].trigger
      value: "25s timeout"
    - source: component-dossiers/payment-service.yaml
      field: non_functional.performance.timeout
      value: "30s"
    - note: order-service(25s) < payment-service(30s) で不整合

  # 5. 対応案とトレードオフ
  options:
    - id: A
      action: order-serviceタイムアウトを35sに延長
      pros:
        - 実装が簡単（設定変更のみ）
        - 既存の契約を維持
      cons:
        - ユーザー体験悪化（待ち時間増加）
        - 他の依存先にも影響
      effort: 小（1日）

    - id: B
      action: 冪等キーを導入して二重課金を防止
      pros:
        - 根本解決
        - タイムアウトを短縮可能
      cons:
        - 実装コストが高い
        - payment-serviceの改修も必要
      effort: 中（1週間）

    - id: C
      action: 非同期処理に変更（イベント駆動）
      pros:
        - スケーラビリティ向上
        - タイムアウト問題を回避
      cons:
        - アーキテクチャの大幅変更
        - ADR-003との整合性確認が必要
      effort: 大（2週間）

  # 6. 優先度
  priority:
    category: P0  # P0/P1/P2/P3/P4
    score: 48
    breakdown:
      severity: critical (4)
      likelihood: high (3)
      detectability: hard (3)
      quality_weight: reliability (5)
    rationale: 決済障害はリスク許容度ゼロ

  # 7. 実施単位
  implementation:
    recommended_option: B
    pr_breakdown:
      - pr: "feat: Add idempotency key to payment request"
        scope: order-service
        size: S
      - pr: "feat: Support idempotency key validation"
        scope: payment-service
        size: M
    adr_needed: true
    adr_topic: "サービス間タイムアウトと冪等性戦略"

  # 8. 受け入れ条件
  acceptance_criteria:
    tests:
      - 同一リクエストを3回送信して課金が1回のみ
      - タイムアウト発生時にリトライが正常動作
    metrics:
      - 二重課金率 = 0%
      - payment成功率 >= 99.9%
    logs:
      - idempotency_key_duplicate イベントが記録される
    contract:
      - OpenAPI に X-Idempotency-Key ヘッダーを追加
```

## フィールド補足

### scope.type の選択基準

| type | 条件 | 例 |
|------|------|-----|
| component | 単一コンポーネント内の問題 | メモリリーク、設定ミス |
| interaction | コンポーネント間の問題 | タイムアウト不整合、契約違反 |
| crosscutting | 複数箇所に横断する問題 | 認証方式の不統一、ログ形式のばらつき |

### priority.score の算出

`score = severity x likelihood x detectability x quality_weight`

- severity: trivial(1) / minor(2) / major(3) / critical(4)
- likelihood: rare(1) / possible(2) / high(3) / certain(4)
- detectability: obvious(1) / easy(2) / hard(3) / hidden(4)
- quality_weight: 品質属性ごとの重み（1-5、invariants.yaml から取得）

### evidence の記述ルール

- 推測は含めない。ソースファイルと該当フィールドを明記する
- note フィールドで複数根拠の関連を説明する
- ソースが存在しない指摘はレポートに含めない
