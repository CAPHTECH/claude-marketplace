# Context継承設計ガイド

並列実行時の親→子、子→親のContext継承を適切に設計するための詳細ガイド。
Context window節約と情報完全性のバランスを取る。

## Context継承の型

### 1. 親→子（Input）

**定義**: 親タスクから子タスクへ渡す入力Context

**含めるべき情報**:
```yaml
essential_context:
  - Issue Contract（目的/不変条件/物差し/停止条件）
  - 現状証拠（Sense結果の要約）
  - Law/Term候補
  - 制約条件（技術的/ビジネス的）

optional_context:
  - 関連ファイルパス（内容は含めず、パスのみ）
  - 依存関係グラフ
  - Evidence要件
```

**最小化の原則**:
- ファイル内容は含めず、パスのみを渡す
- 要約を活用し、詳細は子タスクが必要に応じて読み取る
- 大きなデータ構造は参照で渡す

**例（Good）**:
```yaml
parent_to_child:
  issue_contract:
    goal: "JWT認証実装"
    invariants: ["後方互換性維持"]
    acceptance_criteria: ["全テスト通過", "レスポンス<200ms"]

  current_evidence:
    summary: "既存認証: src/auth/legacy.ts (Basic認証)"
    files: ["src/auth/legacy.ts", "src/middleware/auth.ts"]
    # ← ファイル内容は含めず、パスのみ

  law_term_candidates:
    - LAW-token-expiry: "アクセストークンは1時間で失効"
    - TERM-jwt-token: "JWT形式のアクセストークン"

  constraints:
    - "Node.js 18以上"
    - "既存APIとの互換性維持"
```

**例（Bad - context window無駄遣い）**:
```yaml
parent_to_child:
  issue_contract: [...]

  current_evidence:
    files:
      - path: "src/auth/legacy.ts"
        content: |
          // ← 全ファイル内容を含めてしまう（無駄）
          function authenticate(req, res) {
            // 100行のコード...
          }
      - path: "src/middleware/auth.ts"
        content: |
          // ← これも全内容（無駄）
          function authMiddleware(req, res, next) {
            // 50行のコード...
          }
```

---

### 2. 子→親（Output）

**定義**: 子タスクから親タスクへ返す出力Context

**含めるべき情報**:
```yaml
mandatory_output:
  - タスク結果（成功/失敗）
  - 生成物（Law Card/Term Card/コード/Evidence）
  - Evidence達成レベル（L0-L4）
  - 発見した新事実

optional_output:
  - 警告・注意事項
  - 次ステップへの推奨
  - 追加調査が必要な項目
```

**完全性の原則**:
- 証拠は必ず親に返す（Evidence First原則）
- 失敗時はエラー詳細と原因を明記
- 次ステップへの推奨を含める

**例（成功時）**:
```yaml
child_to_parent:
  status: "success"

  artifacts:
    - type: "Law Card"
      id: "LAW-token-expiry"
      path: "law-catalog/LAW-token-expiry.yaml"
      content: |
        scope: S0
        statement: "アクセストークンは1時間で失効"
        enforcement: [...]

  evidence:
    level: "L1"
    verification: "tests/auth/token-expiry.test.ts"
    coverage: "100%"

  new_findings:
    - "既存コードに有効期限チェックのバグ発見"
    - "リフレッシュトークンの実装が未完成"

  next_steps:
    - "LAW-refresh-token の定義が必要"
    - "既存バグの修正タスク追加を推奨"
```

**例（失敗時）**:
```yaml
child_to_parent:
  status: "failed"

  error:
    type: "InsufficientEvidence"
    message: "src/auth/jwt.ts が存在せず、Law候補を抽出できない"
    details:
      - "期待ファイル: src/auth/jwt.ts"
      - "実際: ファイルが存在しない"

  partial_results:
    - "既存Basic認証の分析は完了"
    - "Term候補は3件抽出済み"

  recommendations:
    - "先にsrc/auth/jwt.ts の実装タスクを実行"
    - "または既存コードからLaw抽出に切り替え"
```

---

## Context継承パターン

### パターン1: Broadcast（一斉配信）

**用途**: 複数の独立タスクに同じContextを配信

**特徴**:
- 親→複数の子に同じContext
- 子タスク間は独立（相互参照なし）

**例**:
```yaml
parent: "認証システム調査"

children:
  - child-1: "Law候補抽出"
  - child-2: "Term候補抽出"
  - child-3: "依存関係分析"

context_inheritance:
  parent_to_all_children:
    - Issue Contract
    - 調査対象ファイル一覧: ["src/auth/*"]
    - 制約条件

  children_to_parent:
    - child-1 → parent: Law候補リスト
    - child-2 → parent: Term候補リスト
    - child-3 → parent: 依存関係グラフ
```

**利点**: Context準備が1回で済む、並列実行に最適

---

### パターン2: Pipeline（パイプライン）

**用途**: タスクの出力が次のタスクの入力になる

**特徴**:
- 子タスクが順次実行
- 各タスクの出力が次の入力

**例**:
```yaml
parent: "認証機能実装"

children:
  - child-1: "コードベース調査"
  - child-2: "Law抽出（child-1の結果を使用）"
  - child-3: "Law Card化（child-2の結果を使用）"

context_inheritance:
  parent → child-1:
    - Issue Contract
    - 調査対象: ["src/auth/*"]

  child-1 → child-2:
    - 調査レポート（child-1の出力）

  child-2 → child-3:
    - Law候補リスト（child-2の出力）

  child-3 → parent:
    - Law Card集（child-3の出力）
```

**利点**: データフローが明確、段階的な処理に最適

**注意**: 並列実行不可（順次実行のみ）

---

### パターン3: Scatter-Gather（分散・集約）

**用途**: タスクを分散実行し、結果を集約

**特徴**:
- 親→複数の子に異なるContext
- 子→親に結果を返し、親が集約

**例**:
```yaml
parent: "マイクロサービス統合テスト"

children:
  - child-1: "認証サービステスト"
  - child-2: "カタログサービステスト"
  - child-3: "注文サービステスト"

context_inheritance:
  parent → child-1:
    - Issue Contract
    - 対象サービス: "auth"
    - エンドポイント: "https://auth.example.com"

  parent → child-2:
    - Issue Contract
    - 対象サービス: "catalog"
    - エンドポイント: "https://catalog.example.com"

  parent → child-3:
    - Issue Contract
    - 対象サービス: "order"
    - エンドポイント: "https://order.example.com"

  children → parent:
    - child-1: テスト結果（auth）
    - child-2: テスト結果（catalog）
    - child-3: テスト結果（order）

  parent_aggregation:
    - 3サービスのテスト結果を統合
    - 全体のEvidence Ladder達成レベルを判定
```

**利点**: 並列実行で効率化、結果の一元管理

---

### パターン4: Hierarchical（階層的）

**用途**: タスクが階層構造を持つ場合の継承

**特徴**:
- 親→子→孫の階層
- 各レベルでContext継承

**例**:
```yaml
parent: "認証システム実装"

child-1: "JWT認証実装"
  grandchild-1-1: "トークン生成実装"
  grandchild-1-2: "トークン検証実装"

child-2: "セッション管理実装"
  grandchild-2-1: "セッション作成実装"
  grandchild-2-2: "セッション破棄実装"

context_inheritance:
  parent → child-1:
    - Issue Contract
    - Law: [LAW-token-expiry, LAW-token-signature]

  child-1 → grandchild-1-1:
    - Law: [LAW-token-expiry, LAW-token-signature]
    - 実装ファイル: "src/auth/jwt-generator.ts"

  child-1 → grandchild-1-2:
    - Law: [LAW-token-signature]
    - 実装ファイル: "src/auth/jwt-verifier.ts"

  grandchild-1-1 → child-1:
    - 実装コード + Evidence L1

  grandchild-1-2 → child-1:
    - 実装コード + Evidence L1

  child-1 → parent:
    - JWT認証実装完了 + Evidence L1-L2達成
```

**利点**: 複雑なタスクを階層的に管理、Evidence集約が容易

---

## Context最小化のテクニック

### 1. 要約の活用

**Before（無駄が多い）**:
```yaml
parent_to_child:
  file_contents:
    - path: "src/auth/legacy.ts"
      content: |
        // 100行の全コード...
    - path: "src/middleware/auth.ts"
      content: |
        // 50行の全コード...
```

**After（要約で効率化）**:
```yaml
parent_to_child:
  file_summary:
    - path: "src/auth/legacy.ts"
      summary: "Basic認証を実装。authenticate()関数が主要エントリーポイント。"
      key_functions: ["authenticate", "validateCredentials"]
      # ← 詳細はパスを使って子タスクが読み取る

    - path: "src/middleware/auth.ts"
      summary: "Express middleware。authMiddleware()でリクエスト認証。"
      key_functions: ["authMiddleware"]
```

**削減効果**: 100行 → 5行（95%削減）

---

### 2. 参照パスの使用

**Before（内容をすべて含める）**:
```yaml
parent_to_child:
  law_cards:
    - id: "LAW-token-expiry"
      content: |
        # 全Law Cardの内容（50行）
    - id: "LAW-token-signature"
      content: |
        # 全Law Cardの内容（50行）
```

**After（パスのみ渡す）**:
```yaml
parent_to_child:
  law_cards:
    - id: "LAW-token-expiry"
      path: "law-catalog/LAW-token-expiry.yaml"
      # ← 子タスクが必要に応じて読み取る

    - id: "LAW-token-signature"
      path: "law-catalog/LAW-token-signature.yaml"
```

**削減効果**: 100行 → 4行（96%削減）

---

### 3. 段階的読み込み

**戦略**: 子タスクが必要なContextだけを段階的に読み取る

**例**:
```yaml
parent_to_child:
  available_resources:
    - type: "Law Cards"
      location: "law-catalog/*.yaml"
    - type: "Term Cards"
      location: "term-catalog/*.yaml"
    - type: "調査レポート"
      location: "docs/survey-report.md"

  task_instruction:
    "必要に応じて上記リソースを読み取り、Law候補を抽出してください"
```

**子タスクの動作**:
1. まずLaw Cards一覧を確認（Glob）
2. 必要なLaw Cardのみ読み取り（Read）
3. Law候補を抽出

**利点**: 必要最小限のContext読み込み、柔軟性が高い

---

## Task Tool統合

### Task Toolでの並列実行パターン

**1メッセージで複数Task Toolを呼び出し**:

```markdown
## 並列実行: Law/Term候補抽出

以下のタスクを並列実行します:

### Context（共通）
- Issue Contract: JWT認証実装
- 調査対象: src/auth/*
- Law/Term Catalog: law-catalog/, term-catalog/

### 並列タスク
```

次に、複数のTask tool呼び出しを1メッセージで:

**Task 1**: Law候補抽出
```yaml
subagent_type: general-purpose
prompt: |
  Issue Contract:
    - Goal: JWT認証実装
    - Invariants: 後方互換性維持

  タスク: src/auth/*からLaw候補を抽出

  リソース:
    - 調査対象: src/auth/*
    - 既存Law: law-catalog/*.yaml（必要に応じて参照）

  出力: Law候補リスト（YAML形式）
```

**Task 2**: Term候補抽出
```yaml
subagent_type: general-purpose
prompt: |
  Issue Contract:
    - Goal: JWT認証実装

  タスク: src/auth/*からTerm候補を抽出

  リソース:
    - 調査対象: src/auth/*
    - 既存Term: term-catalog/*.yaml（必要に応じて参照）

  出力: Term候補リスト（YAML形式）
```

**重要**: 2つのTask toolを**同じメッセージ内**で呼び出すことで真の並列実行を実現。

---

### Context継承のベストプラクティス（Task Tool）

**Good（最小限のContext）**:
```yaml
prompt: |
  ## Task: Law候補抽出

  ### Issue Contract
  - Goal: JWT認証実装
  - Invariants: 後方互換性維持

  ### 調査対象
  - src/auth/*

  ### リソース（必要に応じて読み取り）
  - Law Catalog: law-catalog/*.yaml
  - Term Catalog: term-catalog/*.yaml

  ### 出力
  - Law候補リスト（YAML形式）
  - Evidence要件（L0-L4）
```

**Bad（Context過剰）**:
```yaml
prompt: |
  ## Task: Law候補抽出

  ### Issue Contract
  [全文を含める - 200行]

  ### 既存Law Card
  [すべてのLaw Cardの内容 - 500行]

  ### 既存Term Card
  [すべてのTerm Cardの内容 - 500行]

  ### 調査対象ファイル内容
  [src/auth/*の全コード - 1000行]

  # ← context window を無駄遣い
```

---

## トラブルシューティング

### Context不足による失敗

**症状**: 子タスクが「情報不足で実行できない」と報告

**原因**: 必要なContextが親から渡されていない

**対策**:
```yaml
診断:
  - 子タスクのエラーメッセージを確認
  - 不足している情報を特定

修正:
  parent_to_child:
    # 不足情報を追加
    missing_context: [...]
```

---

### Context過剰によるパフォーマンス低下

**症状**: Task toolの実行が遅い、context window警告

**原因**: 不要なContextを大量に渡している

**対策**:
```yaml
最適化:
  - ファイル内容→パスのみに変更
  - 全内容→要約に変更
  - 段階的読み込みに変更
```

---

### 結果統合の失敗

**症状**: 子タスクの結果を統合できない

**原因**: 出力形式が統一されていない

**対策**:
```yaml
出力形式の統一:
  child_to_parent:
    format: "YAML"
    schema:
      - status: "success | failed"
      - artifacts: [...]
      - evidence: [...]
```

---

## まとめ

### Context継承の核心原則

1. **最小限の継承**: ファイル内容ではなくパス、全内容ではなく要約
2. **段階的読み込み**: 子タスクが必要に応じて読み取る
3. **証拠の完全性**: Evidence は必ず親に返す
4. **失敗時の詳細**: エラー原因と推奨を明記

### Context設計チェックリスト

**親→子（Input）**:
- [ ] Issue Contractは含まれているか
- [ ] ファイル内容ではなくパスのみか
- [ ] 要約を活用しているか
- [ ] 必要最小限のContextか

**子→親（Output）**:
- [ ] タスク結果（成功/失敗）を返しているか
- [ ] 生成物（Law/Term/コード）を返しているか
- [ ] Evidence達成レベルを返しているか
- [ ] 新事実・推奨を返しているか
