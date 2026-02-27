# PRオンボーディングスキルカタログ

各スキルの詳細な実行方法、入出力、品質ゲートを定義する。

---

## Skill 0: オンボーディング契約の確立

### 目的
PR本文が長文化・散逸しないよう、AIが最初に"出力の契約"を確立する。

### 入力
- PRの差分（diff / file list）
- 関連チケット・設計ID・ドキュメント（あれば）

### 出力
```yaml
pr_contract:
  sections:
    - Summary
    - Why (Goal/Reason/Alternatives)
    - What Changed
    - Blast Radius
    - Invariants
    - Failure Modes
    - Evidence
    - Rollout & Rollback
    - Review Focus
    - Unknowns

  constraints:
    max_length: 1-2画面
    detail_handling: リンクに逃がす
```

### 品質ゲート
- 「PR本文＝契約」「詳細＝参照先」の分離ができている

### ガードレール
- "説明のための説明"を禁止（長文で安心させない）

---

## Skill 1: 変更の意味理解（diff要約ではなく"意味要約"）

### 目的
行数差分を要約するのではなく、振る舞い・責務・契約の変化を抽出する。

### 入力
- diff、主要ファイル、周辺の呼び出し元/先

### 出力
```yaml
change_summary:
  core_changes: # トップ3
    - change: "○○の判定条件がAからBに変更"
      impact: "Xの場合にYが発生するようになる"
    - change: "..."
      impact: "..."

  behavior_changed:
    - "認証失敗時のレスポンスコードが401から403に変更"

  behavior_unchanged:
    - "正常系のフローは変更なし"
    - "データベーススキーマは変更なし"
```

### 品質ゲート
- 変更点が「関数を追加した」ではなく「○○の判定条件がこう変わった」になっている

### ガードレール
- 推測で意味を断言しない（根拠が取れないものは「可能性」として扱う）

---

## Skill 2: 目的・意図の抽出（Whyを"根拠つき"で書く）

### 目的
Why（設計意図）を、作文ではなく意思決定の記録として残す。

### 入力
- チケット説明、コミットメッセージ、設計ドキュメント、PR内議論

### 出力
```yaml
design_intent:
  goal: |
    セッションタイムアウトを30分から60分に延長し、
    ユーザーの再ログイン頻度を下げる

  reason: |
    カスタマーサポートへの「頻繁にログアウトされる」
    問い合わせが月100件超。競合は60分が標準。

  alternatives:
    - option: "スライディングウィンドウ方式"
      rejected_because: |
        実装コストが高く、セキュリティ監査が必要。
        まず単純延長で効果を測定してから検討。

    - option: "Remember Me機能"
      rejected_because: |
        セキュリティポリシー上、永続セッション禁止。
```

### 品質ゲート
- 代替案が最低1つ出ている（探索がある）
- 採用理由が「好み」ではなく制約（性能・安全・運用・互換性）に結びつく

### ガードレール
- 代替案を"それっぽく捏造"しない（無いなら「未検討」と書く勇気）

---

## Skill 3: 境界と波及（Blast Radius）の特定

### 目的
レビューと運用の本質は「どこが巻き込まれるか」。境界・依存・互換性を確定する。

### 入力
- 変更箇所の依存関係（呼び出し、データ、外部I/F、設定、フラグ）

### 出力
```yaml
blast_radius:
  callers: # 呼び出し元
    - path: src/api/user.ts
      function: getUserProfile
      impact: "セッション検証ロジックが変更される"

  callees: # 呼び出し先
    - path: src/db/session.ts
      impact: "タイムアウト値の参照箇所"

  data:
    - table: sessions
      impact: "expires_at カラムの値が変わる"

  external_interfaces:
    - name: "認証API"
      impact: "なし（内部処理のみ）"

  compatibility:
    backward_compatible: true
    migration_required: false
    breaking_changes: []
```

### 品質ゲート
- "影響なし"と言う場合、理由（なぜ依存がないか）を示す

### ガードレール
- 影響範囲を過小評価しない（不確実なら不確実と書く）

---

## Skill 4: 不変条件（Invariants）の抽出と明文化

### 目的
「何を壊してはいけないか」を明文化し、レビューの焦点を固定する。

### 入力
- 既存テスト、既存ドキュメント、重要な関数の前提、ドメインルール

### 出力
```yaml
invariants:
  - condition: "セッションは必ず有効期限を持つ"
    source: "src/auth/session.ts:42 - expires_at NOT NULL制約"
    violation_symptom: "無期限セッションが発生し、セキュリティリスク"

  - condition: "タイムアウト値は設定ファイルで一元管理"
    source: "config/auth.yaml + ADR-012"
    violation_symptom: "ハードコードされた値が分散し、変更漏れが発生"

  - condition: "セッション延長はアクティビティがある場合のみ"
    source: "tests/session.test.ts:78"
    violation_symptom: "放置されたセッションが延命され、セキュリティリスク"
```

### 品質ゲート
- 不変条件が"検証/観測できる形"になっている（主観語だけではない）

### ガードレール
- 不変条件ゼロのPRを「普通」と扱わない（ゼロは危険信号）

---

## Skill 5: 失敗モード分析（Risk & Detection）

### 目的
「壊れ方」と「気づき方」をセットにして、運用可能性を担保する。

### 入力
- 変更点、境界、過去障害の傾向（もし分かれば）

### 出力
```yaml
failure_modes:
  frequent: # 起きやすい
    - pattern: "設定値の読み込み失敗でデフォルト30分にフォールバック"
      detection:
        - test: "tests/config.test.ts - タイムアウト設定読み込み"
        - log: "auth.session.timeout.fallback"
        - metric: "session_timeout_value gauge"

  critical: # 致命的
    - pattern: "タイムアウト値が0になり、即座にセッション無効化"
      detection:
        - test: "tests/session.test.ts - ゼロ値バリデーション"
        - alert: "session_duration_p99 < 1min"

  subtle: # 気づきにくい
    - pattern: "並行リクエストでセッション延長が競合し、片方が古い値で上書き"
      detection:
        - test: "tests/session.test.ts - 並行更新テスト"
        - log: "auth.session.concurrent_update"
```

### 品質ゲート
- "検知手段"が具体（どのテスト名・どのログ・どの指標）に寄っている

### ガードレール
- 「たぶん大丈夫」系の楽観表現は禁止（不確実なら検証ToDoに落とす）

---

## Skill 6: 検証の証拠化（Evidence Packaging）

### 目的
PR時のオンボーディングは「信頼できる根拠の束」。AIがそれを"見える形"にする。

### 入力
- テスト結果（CIログ、実行コマンド、スクショ、再現手順）
- 関連コードへのリンク

### 出力
```yaml
evidence:
  automated_tests:
    - name: "単体テスト"
      command: "npm test -- --grep 'session'"
      result: "42 passing, 0 failing"
      ci_link: "https://ci.example.com/runs/12345"

    - name: "統合テスト"
      command: "npm run test:integration"
      result: "全パス"

  manual_verification:
    - scenario: "60分放置後のセッション有効性確認"
      steps:
        - "ログイン"
        - "60分待機（またはセッション有効期限を手動変更）"
        - "APIリクエスト送信"
      expected: "正常レスポンス"
      actual: "正常レスポンス（200 OK）"

  code_references:
    - path: src/auth/session.ts
      lines: 42-56
      purpose: "タイムアウト計算ロジック"

    - path: config/auth.yaml
      lines: 15-18
      purpose: "タイムアウト設定値"
```

### 品質ゲート
- "何を見れば再検証できるか"が揃っている

### ガードレール
- **実行していないテストを「実行した」と書かない（最重要）**

---

## Skill 7: リリース戦略（Rollout & Rollback Contract）

### 目的
変更が間違っていたときに、継続が困難になるのを防ぐ。

### 入力
- フラグ、段階リリース、DBマイグレーション、設定変更

### 出力
```yaml
release_strategy:
  rollout:
    method: "設定変更（再起動不要）"
    steps:
      - "config/auth.yaml の session_timeout を 60 に変更"
      - "config reload API を呼び出し"
    monitoring:
      - "session_duration_p50, p99 を監視"
      - "auth.session.timeout.changed ログを確認"

  rollback:
    method: "設定を元に戻す"
    steps:
      - "config/auth.yaml の session_timeout を 30 に戻す"
      - "config reload API を呼び出し"
    time_estimate: "< 5分"

  cannot_rollback_if:
    - condition: "なし（設定変更のみのため即時ロールバック可能）"

  # データ変更がある場合の例
  # cannot_rollback_if:
  #   - condition: "マイグレーション後に新スキーマでデータが書き込まれた場合"
  #     mitigation: "バックアップからリストア、または手動データ修正"
```

### 品質ゲート
- ロールバック不能な場合、代替として「止血策（機能停止/フラグオフ/隔離）」が提示される

### ガードレール
- 「戻せるはず」の曖昧表現は禁止（戻す対象を明示）

---

## Skill 8: レビュー誘導（Review Map / Focus Points）

### 目的
レビューアの時間は有限。AIが「どこを見ると判断が速いか」を提供する。

### 入力
- 変更の中心、リスク、境界、不変条件

### 出力
```yaml
review_guide:
  focus_points:
    - aspect: "セキュリティ"
      question: "60分への延長はセキュリティポリシーに違反しないか？"
      files:
        - src/auth/session.ts

    - aspect: "設定管理"
      question: "タイムアウト値の一元管理が維持されているか？"
      files:
        - config/auth.yaml
        - src/auth/session.ts

  key_files:
    - path: src/auth/session.ts
      reason: "タイムアウト計算の中心ロジック"
      lines_to_review: 42-56

    - path: tests/session.test.ts
      reason: "不変条件のテストカバレッジ"
      lines_to_review: 78-120

  discussion_points:
    - topic: "60分は適切か？"
      context: "競合は60分が多いが、金融系は30分が多い"
      options:
        - "60分で進める"
        - "45分で様子を見る"
        - "A/Bテストで検証"
```

### 品質ゲート
- 重点が「変更行数」ではなく「リスクと不変条件」に基づいている

### ガードレール
- 重要論点を"全部レビューしてください"で逃がさない（重点化が仕事）

---

## Skill 9: DocDD同期（ドキュメントの正本を守る）

### 目的
PRで知識が散逸すると、DocDDが"名前だけ"になる。PRから正本へ沈殿させる。

### 入力
- 関連ドキュメント、設計ID、代表フロー/境界台帳

### 出力
```yaml
docdd_sync:
  referenced_docs:
    - path: docs/auth/session-management.md
      is_authoritative: true
      last_updated: "2024-01-15"
      drift_risk: "低（3ヶ月以内の更新）"

    - path: docs/adr/ADR-012-session-timeout.md
      is_authoritative: true
      status: "このPRで更新が必要"

  updates_required:
    - doc: docs/auth/session-management.md
      section: "セッションタイムアウト"
      current: "デフォルト30分"
      proposed: "デフォルト60分"
      diff: |
        - セッションタイムアウト: 30分
        + セッションタイムアウト: 60分

    - doc: docs/adr/ADR-012-session-timeout.md
      action: "ADRを更新し、60分への変更理由を追記"

  warnings:
    - "docs/security/session-policy.md が1年以上更新されていません。整合性を確認してください。"
```

### 品質ゲート
- "どのドキュメントが正本か"が明示される
- ドキュメントが古い可能性がある場合、警告が出る

### ガードレール
- ドキュメントの内容を"補完創作"しない（更新案は提案として分離）

---

## Skill 10: 不確実性管理（Unknowns & Follow-ups）

### 目的
生成AIの最大のリスクは、曖昧さを隠して断言すること。未知を構造化して残す。

### 入力
- 上記スキルの結果

### 出力
```yaml
unknowns:
  items:
    - item: "負荷テスト未実施"
      resolution: "リリース前に負荷テストを実行"
      is_blocker: true
      owner: "@performance-team"

    - item: "モバイルアプリへの影響"
      resolution: "モバイルチームに確認"
      is_blocker: false
      follow_up_issue: "#789"

    - item: "60分で問い合わせが減るかは未検証"
      resolution: "リリース後2週間でメトリクス確認"
      is_blocker: false
      follow_up_issue: "#790"

  merge_conditions:
    - "負荷テスト完了"
    - "セキュリティチームの承認"

  post_merge_actions:
    - "モバイルチームへの通知"
    - "カスタマーサポートへの周知"
```

### 品質ゲート
- 未確定が「気合で頑張る」ではなく検証可能なToDoになっている

### ガードレール
- 未確定事項をゼロに"見せかける"のは禁止（無理に埋めない）
