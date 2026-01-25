# 並列実行パターンと失敗処理ガイド

並列実行の実践的パターンと失敗時の対処方法の詳細ガイド。

## 並列実行パターン

### パターン1: 並列調査（Parallel Survey）

**用途**: 大規模コードベースの多角的調査

**特徴**:
- 複数の調査タスクを同時実行
- 各タスクは独立（相互依存なし）
- 調査結果を統合して全体像を把握

**実装例**:

```yaml
scenario: "認証システムの全体像把握"

parallel_tasks:
  - task-1:
      name: "関数定義調査"
      tool: Grep
      pattern: "^function|^export function|^const.*=.*function"
      target: "src/auth/**/*.ts"
      output: "関数一覧"

  - task-2:
      name: "インポート関係調査"
      tool: Grep
      pattern: "^import.*from"
      target: "src/auth/**/*.ts"
      output: "依存関係グラフ"

  - task-3:
      name: "テストコード調査"
      tool: Glob
      pattern: "tests/auth/**/*.test.ts"
      output: "テストファイル一覧"

  - task-4:
      name: "型定義調査"
      tool: Grep
      pattern: "^interface|^type|^enum"
      target: "src/auth/**/*.ts"
      output: "型定義一覧"

execution:
  method: "1メッセージで4つのTask toolを並列実行"
  time_estimate:
    sequential: "4タスク × 10分 = 40分"
    parallel: "10分（4タスク同時実行）"
    reduction: "75%"

integration:
  method: "4つの調査結果を統合して全体レポート作成"
  output: |
    # 認証システム調査レポート

    ## 関数一覧（task-1結果）
    - authenticate()
    - generateToken()
    - verifyToken()
    ...

    ## 依存関係（task-2結果）
    - src/auth/jwt.ts → jsonwebtoken
    - src/auth/session.ts → src/auth/jwt.ts
    ...

    ## テストカバレッジ（task-3結果）
    - tests/auth/jwt.test.ts
    - tests/auth/session.test.ts
    カバレッジ: 85%

    ## 型定義（task-4結果）
    - interface User
    - type Token
    ...
```

**利点**:
- 大幅な時間短縮（75%削減）
- 調査の完全性（見落とし防止）
- 結果統合で全体像が明確

---

### パターン2: 並列抽出（Parallel Extraction）

**用途**: 同じコードベースから異なる観点で抽出

**特徴**:
- Law/Term/Evidence等を並列抽出
- 各タスクは異なる観点（Law vs Term）
- 抽出結果を統合してCatalog作成

**実装例**:

```yaml
scenario: "新機能開発のLaw/Term同定"

parallel_tasks:
  - task-1:
      name: "Law候補抽出"
      focus: "不変条件/Pre/Post/Policy"
      target: "src/auth/**/*.ts"
      output: |
        law_candidates:
          - LAW-token-expiry: "アクセストークンは1時間で失効"
          - LAW-token-signature: "トークンは秘密鍵で署名"
          - LAW-session-timeout: "セッションは30分で無効化"

  - task-2:
      name: "Term候補抽出"
      focus: "Entity/Value/Context/Boundary"
      target: "src/auth/**/*.ts"
      output: |
        term_candidates:
          - TERM-access-token: "JWT形式のアクセストークン"
          - TERM-refresh-token: "リフレッシュトークン"
          - TERM-session-id: "セッション識別子"

execution:
  method: "2つのTask toolを並列実行"
  time_estimate:
    sequential: "2タスク × 15分 = 30分"
    parallel: "15分（2タスク同時実行）"
    reduction: "50%"

integration:
  method: "Law/Term候補を統合してCatalog初期版作成"
  output: |
    # Law/Term Catalog（初期版）

    ## Law候補（3件）
    - LAW-token-expiry (S0)
    - LAW-token-signature (S0)
    - LAW-session-timeout (S1)

    ## Term候補（3件）
    - TERM-access-token
    - TERM-refresh-token
    - TERM-session-id

    ## 次ステップ
    - Law/Term Card作成
    - Link Map作成
```

**利点**:
- 異なる観点を並列処理
- Law/Termの整合性を後から確認
- Catalog作成の効率化

---

### パターン3: 並列実装（Parallel Implementation）

**用途**: データ/制御依存のない複数モジュール実装

**特徴**:
- 独立したモジュールを並列実装
- 各モジュールはEvidence L1達成
- 統合テスト（L2）は並列完了後に実行

**実装例**:

```yaml
scenario: "マイクロサービスの並列実装"

parallel_tasks:
  - task-1:
      name: "ユーザー認証サービス実装"
      directory: "services/auth/"
      law: [LAW-token-expiry, LAW-token-signature]
      evidence_level: L1
      time_estimate: "40分"

  - task-2:
      name: "商品カタログサービス実装"
      directory: "services/catalog/"
      law: [LAW-product-active, LAW-stock-non-negative]
      evidence_level: L1
      time_estimate: "40分"

  - task-3:
      name: "注文処理サービス実装"
      directory: "services/order/"
      law: [LAW-order-consistency, LAW-payment-verified]
      evidence_level: L1
      time_estimate: "40分"

independence:
  data: "各サービスは独立したDBスキーマ"
  control: "各サービスは独立したAPIエンドポイント"
  resource: "異なるディレクトリに書き込み（競合なし）"
  evidence: "各サービスが独立してL1達成"

execution:
  method: "3つのTask toolを並列実行"
  time_estimate:
    sequential: "3サービス × 40分 = 120分"
    parallel: "40分（3サービス同時実装）"
    reduction: "67%"

integration:
  method: "統合テスト（L2）"
  task: "3サービス連携動作の検証"
  time_estimate: "20分"
  total_time: "60分（並列40分 + 統合20分）"
```

**利点**:
- 開発時間を1/3に短縮
- 各モジュールの独立性を保証
- Evidence達成を並列化

---

### パターン4: 並列Evidence収集（Parallel Evidence Collection）

**用途**: 異なるEvidence Levelの並行収集

**特徴**:
- L1/L2/L4を並列収集
- 各Evidenceは独立して収集可能
- S0 Lawの完全な接地を効率化

**実装例**:

```yaml
scenario: "S0 Law（LAW-token-expiry）の完全な接地"

parallel_tasks:
  - task-1:
      name: "L1 Evidence収集"
      method: "ユニットテスト作成"
      file: "tests/auth/token-expiry.test.ts"
      coverage_target: "100%"
      time_estimate: "15分"

  - task-2:
      name: "L2 Evidence収集"
      method: "統合テストシナリオ設計"
      file: "tests/integration/auth-flow.test.ts"
      scenario: "トークン有効期限切れ時の動作確認"
      time_estimate: "15分"

  - task-3:
      name: "L4 Evidence収集"
      method: "Telemetry設定"
      file: "src/observability/metrics.ts"
      metric: "token_expiry_violations_total"
      alert: "トークン有効期限違反検知"
      time_estimate: "15分"

independence:
  - L1: ユニットテストは実装コードのみに依存
  - L2: 統合テストは複数サービス連携を検証
  - L4: Telemetryは本番環境での観測
  - 各Evidenceは独立して収集可能

execution:
  method: "3つのTask toolを並列実行"
  time_estimate:
    sequential: "3タスク × 15分 = 45分"
    parallel: "15分（3タスク同時実行）"
    reduction: "67%"

verification:
  evidence_ladder:
    - L0: ✓ 型チェック通過
    - L1: ✓ ユニットテスト100%カバレッジ
    - L2: ✓ 統合テストシナリオ実装
    - L3: - （S0なので不要）
    - L4: ✓ Telemetry設定完了

  grounding_complete: true
```

**利点**:
- Evidence Ladder達成を並列化
- S0 Lawの完全な接地を効率化
- 各Evidence Levelの独立性を保証

---

## 失敗処理パターン

### パターン1: 部分失敗（Partial Failure）

**症状**: 並列実行中に一部のタスクが失敗

**対応戦略**:

```yaml
scenario: "4タスク並列実行中に2タスク失敗"

execution:
  parallel_tasks: 4
  success: [task-1, task-2]
  failed: [task-3, task-4]

strategy:
  step-1: "成功タスクの結果を採用"
  step-2: "失敗タスクを順次実行で再試行"
  step-3: "再試行で成功すれば統合、失敗すればスコープ縮小"

implementation:
  # 成功タスクの結果を保存
  successful_results:
    - task-1: "Law候補リスト"
    - task-2: "Term候補リスト"

  # 失敗タスクを順次再試行
  retry_sequential:
    - task-3:
        retry_count: 1
        method: "sequential"
        timeout: "20分"

    - task-4:
        retry_count: 1
        method: "sequential"
        timeout: "20分"

  # 再試行結果
  retry_results:
    - task-3: "success（順次実行で成功）"
    - task-4: "failed（再試行でも失敗）"

  # 最終統合
  final_integration:
    success: [task-1, task-2, task-3]
    failed: [task-4]
    action: "task-4をスコープから除外、残り3タスクで進行"
```

**利点**:
- 成功タスクの結果を無駄にしない
- 失敗タスクは慎重に再試行
- 完全失敗を避ける

---

### パターン2: 完全失敗（Complete Failure）

**症状**: 並列実行中に50%以上のタスクが失敗

**対応戦略**:

```yaml
scenario: "4タスク並列実行中に3タスク失敗"

execution:
  parallel_tasks: 4
  success: [task-1]
  failed: [task-2, task-3, task-4]
  failure_rate: 75%

strategy:
  decision: "並列実行を中止、順次実行に切り替え"
  reason: "失敗率が高く、並列実行のメリットがない"

implementation:
  # 並列実行中止
  abort_parallel: true

  # 順次実行に切り替え
  sequential_execution:
    - task-2:
        method: "sequential"
        timeout: "20分"
        debug: true

    - task-3:
        method: "sequential"
        timeout: "20分"
        debug: true

    - task-4:
        method: "sequential"
        timeout: "20分"
        debug: true

  # 失敗原因分析
  root_cause_analysis:
    common_error: "Context不足によるタスク実行失敗"
    fix: "親→子のContext継承を強化"

  # 修正後に再実行
  retry_with_fix:
    method: "sequential"
    context_enhanced: true
    success_rate: 100%
```

**利点**:
- 無駄な並列実行を回避
- 失敗原因を慎重に分析
- 修正後に再実行で成功

---

### パターン3: Evidence不足（Evidence Gap）

**症状**: 並列実行は成功したが、Evidenceが不足

**対応戦略**:

```yaml
scenario: "Law Card作成は成功したが、Evidence L1が未達成"

execution:
  parallel_tasks:
    - task-1: "LAW-token-expiry Card作成（success）"
    - task-2: "LAW-token-signature Card作成（success）"
    - task-3: "LAW-session-timeout Card作成（success）"

  evidence_check:
    - LAW-token-expiry: "L0のみ（L1未達成）"
    - LAW-token-signature: "L1達成"
    - LAW-session-timeout: "L0のみ（L1未達成）"

strategy:
  detection: "Evidence Ladder達成レベルを自動チェック"
  action: "不足Evidenceを補完する追加タスクを生成"

implementation:
  # Evidence Gap検出
  gap_detection:
    - law: "LAW-token-expiry"
      required: "L1"
      actual: "L0"
      gap: "L1（ユニットテスト）"

    - law: "LAW-session-timeout"
      required: "L1"
      actual: "L0"
      gap: "L1（ユニットテスト）"

  # 追加タスク生成
  補完_tasks:
    - task-補完-1:
        name: "LAW-token-expiry のL1 Evidence収集"
        method: "ユニットテスト作成"
        file: "tests/auth/token-expiry.test.ts"

    - task-補完-2:
        name: "LAW-session-timeout のL1 Evidence収集"
        method: "ユニットテスト作成"
        file: "tests/auth/session-timeout.test.ts"

  # 補完タスクを並列実行
  execution:
    method: "2つのTask toolを並列実行"
    time: "15分"

  # 最終確認
  final_check:
    - LAW-token-expiry: "L1達成"
    - LAW-token-signature: "L1達成"
    - LAW-session-timeout: "L1達成"
    all_laws_grounded: true
```

**利点**:
- Evidence不足を自動検出
- 補完タスクを効率的に生成
- Evidence Ladder完全達成を保証

---

### パターン4: 整合性違反（Consistency Violation）

**症状**: 並列実行結果を統合時に矛盾が発生

**対応戦略**:

```yaml
scenario: "Law/Term抽出結果に矛盾"

execution:
  parallel_tasks:
    - task-1: "Law候補抽出"
    - task-2: "Term候補抽出"

  results:
    task-1_output:
      - LAW-token-expiry: "アクセストークンは1時間で失効"
      - LAW-token-lifetime: "トークンは60分有効"  # ← 重複？

    task-2_output:
      - TERM-access-token: "JWT形式のアクセストークン"
      - TERM-jwt-token: "JWT認証トークン"  # ← 重複？

  contradiction_detected:
    - type: "Law重複"
      laws: ["LAW-token-expiry", "LAW-token-lifetime"]
      issue: "同じ概念を異なる名前で定義"

    - type: "Term重複"
      terms: ["TERM-access-token", "TERM-jwt-token"]
      issue: "synonym/aliasの可能性"

strategy:
  detection: "整合性チェックで矛盾を自動検出"
  resolution: "矛盾解決タスクを生成"

implementation:
  # 整合性チェック
  consistency_check:
    - check: "Law重複チェック"
      method: "Lawの意味を比較、重複を検出"

    - check: "Term重複チェック"
      method: "Termの定義を比較、synonym検出"

  # 矛盾解決
  resolution_task:
    name: "Law/Term重複解決"
    actions:
      - "LAW-token-expiry と LAW-token-lifetime を統合 → LAW-token-expiry"
      - "TERM-access-token と TERM-jwt-token を統合 → TERM-access-token"

  # 統合後の結果
  resolved_results:
    laws:
      - LAW-token-expiry: "アクセストークンは1時間で失効"

    terms:
      - TERM-access-token: "JWT形式のアクセストークン（別名: jwt-token）"
```

**利点**:
- 矛盾を自動検出
- 重複を統合して整合性を保証
- Link Mapの品質向上

---

## 並列度の動的調整

### リソース制約による調整

**トリガー**: Memory/CPU使用率が閾値を超えた

```yaml
scenario: "並列度4で実行中にメモリ不足"

monitoring:
  initial_parallelism: 4
  memory_usage: 85%
  threshold: 80%

adjustment:
  trigger: "memory_usage > threshold"
  action: "並列度を半減"
  new_parallelism: 2

implementation:
  # 実行中のタスクを一時停止
  pause_tasks: [task-3, task-4]

  # 並列度2で再開
  resume_tasks: [task-1, task-2]

  # task-1, task-2完了後にtask-3, task-4を実行
  sequential_completion: [task-3, task-4]
```

---

### 失敗率による調整

**トリガー**: タスク失敗率が30%を超えた

```yaml
scenario: "並列度4で実行中に失敗率30%超え"

monitoring:
  initial_parallelism: 4
  failed_tasks: 2
  failure_rate: 50%
  threshold: 30%

adjustment:
  trigger: "failure_rate > threshold"
  action: "並列度を1に削減（順次実行）"
  new_parallelism: 1

implementation:
  # 並列実行を中止
  abort_parallel: true

  # 順次実行に切り替え
  sequential_execution:
    - task-1: "success"
    - task-2: "success"
    - task-3: "failed → retry → success"
    - task-4: "success"
```

---

## まとめ

### 並列実行パターンの選択

| パターン | 用途 | 並列度 | 時間削減 |
|---------|------|--------|----------|
| 並列調査 | 多角的調査 | 4-6 | 75% |
| 並列抽出 | Law/Term抽出 | 2-3 | 50% |
| 並列実装 | 独立モジュール | 2-3 | 67% |
| 並列Evidence | Evidence収集 | 2-4 | 67% |

### 失敗処理の核心原則

1. **部分失敗は再試行**: 成功タスクを活かし、失敗タスクを順次再試行
2. **完全失敗は中止**: 失敗率50%超えで並列実行を中止、順次実行に切り替え
3. **Evidence不足は補完**: 自動検出で補完タスクを生成
4. **矛盾は解決**: 整合性チェックで矛盾を検出、統合で解決

### 並列実行成功のチェックリスト

- [ ] 依存関係グラフで並列実行可能性を判定
- [ ] Context継承を最小化（パス/要約を活用）
- [ ] 1メッセージで複数Task toolを呼び出し
- [ ] 並列度をリソース制約内に制御
- [ ] 失敗時の再試行・中止戦略を準備
- [ ] Evidence不足の自動検出と補完
- [ ] 整合性チェックで矛盾を解決
