# Output Schema（完全な出力スキーマ）

impact-analysisの完全な出力構造。

## 完全スキーマ

```yaml
impact_analysis:
  meta:
    schema_version: "2.0"
    generated_at: "<iso8601>"
    scope:
      max_graph_depth: 3
      max_items_per_section: 20
      analyzed_from: ["diff", "changed_files", "target"]
    confidence:
      overall: 0.0-1.0
      notes:
        - "<不確実性の理由>"

  change_overview:
    summary: "<何が変わるか>"
    change_type: <behavior_change|refactor|bugfix|perf|security|config|data_migration|unknown>
    risk_domain_tags:
      - "<重要領域タグ>"   # auth, session, payment, cache等
    blast_radius_hint: <local|module|service|system|unknown>

  targets:
    - entity:
        file: "<ファイルパス>"
        symbol: "<シンボル名>"
        kind: <function|class|method|module|endpoint|sql|config>
        location: "<path:line-line>"
      role_in_change: <modified|added|deleted|suspected>
      public_surface: <internal|exported|api|library|unknown>

  impacts:
    code:
      direct:
        - ref: "<path:line>"
          relation: <caller|callee|importer|override|implements|type_depends|route_maps_to|di_binds_to>
          risk_level: <high|medium|low>
          confidence: 0.0-1.0
          evidence:
            - "<根拠>"

      transitive:
        - ref: "<path or pattern>"
          relation: <depends_on_caller|fanout_from_entrypoint|shared_middleware|unknown>
          depth: <int>
          risk_level: <high|medium|low>
          confidence: 0.0-1.0
          evidence:
            - "<根拠>"

    interface:
      exports:
        - ref: "<path>"
          kind: <exported_function|type|constant>
          compatibility: <breaking|non_breaking|unknown>
          evidence:
            - "<根拠>"

      api_endpoints:
        - ref: "<METHOD /path>"
          change_risk: <high|medium|low|unknown>
          evidence:
            - "<根拠>"

    data:
      stores:
        - store: <postgres|mysql|redis|dynamodb|filesystem|unknown>
          entity: "<テーブル/コレクション名>"
          operation: <read|write|upsert|delete|migrate|unknown>
          fields:
            - "<フィールド名>"   # optional
          transactional: <inside_tx|outside_tx|unknown>
          risk_level: <high|medium|low>
          confidence: 0.0-1.0
          evidence:
            - "<根拠>"

    external:
      dependencies:
        - service: "<サービス名>"
          interaction: <cache_read|cache_write|cache_invalidation|lock|rate_limit|api_call|message_publish|message_consume|unknown>
          contract_risk: <high|medium|low|unknown>
          failure_modes:
            - "<障害時の挙動>"
          evidence:
            - "<根拠>"

    config:
      items:
        - key: "<設定キー>"
          impact: "<変更時の影響>"
          risk_level: <high|medium|low|unknown>
          evidence:
            - "<根拠>"

    runtime_quality:
      performance:
        - ref: "<対象>"
          risk: "<性能リスクの説明>"
          evidence:
            - "<根拠>"

      availability:
        - risk: "<可用性リスクの説明>"
          evidence:
            - "<根拠>"

    security_privacy:
      concerns:
        - type: <authn|authz|session|pii|injection|logging_sensitive|rate_limit|csrf|unknown>
          risk_level: <high|medium|low>
          evidence:
            - "<根拠>"

  risk_assessment:
    overall:
      level: <high|medium|low>
      score: 0-100

    scoring_model:
      factors:
        - factor: "<因子名>"
          weight: <int>

    applied_factors:
      - factor: "<因子名>"
        contribution: <int>
        evidence:
          - "<根拠>"

    matrix:
      high: <int>
      medium: <int>
      low: <int>

  recommended_verification:
    tests_to_run:
      - ref: "<テストファイルパス>"
        layer: <unit|integration|e2e>
        priority: <p0|p1|p2>
        purpose: "<何を保証するテストか>"
        evidence:
          - "<根拠>"

    tests_to_add_or_update:
      - suggestion: "<不足するテストの提案>"
        reason: "<なぜ必要か>"
        risk_mitigated: "<どのリスクを下げるか>"

    rollout_and_safety:
      - measure: <feature_flag|canary|shadow|rollback_plan|none>
        reason: "<理由>"

  observation_plan:
    logs:
      - name: "<ログ名パターン>"
        level: <info|warn|error>
        include_fields:
          - "<フィールド名>"
        privacy_note: "<プライバシー注意事項>"

    metrics:
      - name: "<メトリクス名>"
        type: <histogram|counter|gauge>
        dimensions:
          - "<ディメンション>"
        alert_hint: "<アラート設定のヒント>"

    traces:
      - name: "<トレース名>"
        spans_hint:
          - "<スパン名>"

    dashboards:
      - "<ダッシュボード名>"

    validation_window:
      - "<監視強化期間>"

  unknowns_and_assumptions:
    unknowns:
      - "<静的解析では追えない依存/設定/契約>"

    assumptions:
      - "<前提として置いたこと>"

    suggested_followups:
      - "<分かれば精度が上がる追加情報>"
```

## 必須フィールド

以下は必ず出力する必須フィールド:

| パス | 説明 |
|------|------|
| `meta.schema_version` | スキーマバージョン |
| `meta.confidence.overall` | 全体の確度 |
| `change_overview.summary` | 変更の要約 |
| `change_overview.change_type` | 変更の種類 |
| `targets` | 変更対象（1つ以上） |
| `risk_assessment.overall` | 全体リスク評価 |
| `unknowns_and_assumptions.unknowns` | 不確実性リスト（空でも明示） |

## オプショナルフィールド

影響がない場合は省略可能:

- `impacts.interface`（公開IF変更がない場合）
- `impacts.external`（外部依存変更がない場合）
- `impacts.config`（設定変更がない場合）
- `observation_plan.traces`（トレース不要な場合）
