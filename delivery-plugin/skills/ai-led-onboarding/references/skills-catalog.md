# オンボーディングスキルカタログ

各ステップのYAML出力構造と、SKILL.mdに書かれていない失敗モードのみを定義する。手順そのものはSKILL.mdを参照。

---

## Skill 0: オンボーディング契約の確立

### 失敗モード
- 何をしたら終わりか分からず、オンボーディングが肥大化する
- → 合格条件を毎回先に置いて防ぐ

---

## Skill 1: タスク意図の抽出（目的・制約・成功条件）

### 出力
```yaml
intent:
  goal: |
    （1文で記述）
  success_criteria:
    - 基準1（可能なら数値）
    - 基準2
    - 基準3
  constraints:
    - 期限
    - 互換性要件
    - 性能要件
    - セキュリティ要件
    - 運用制約
```

---

## Skill 2: ソース・オブ・トゥルース選別

### 出力
```yaml
sources_of_truth:
  - source: ファイル名/URL
    trust_level: high/medium/low
    last_updated: 日付（分かれば）
    drift_risk: ドリフトの疑い
```

---

## Skill 3: 入口発見

### 出力
```yaml
entry_points:
  - path: src/auth/login.ts
    role: 認証エントリポイント
reading_order:
  1: 入口（エントリポイント）
  2: 主要分岐
  3: 永続化/外部I/F
  4: エラーハンドリング
  5: テスト
```

---

## Skill 4: 境界マップ作成

### 出力
```yaml
boundary_map:
  module: モジュール名
  responsibility: この部分が担う責務

  in:
    - 入力1（型、形式）
    - 入力2

  out:
    - 出力1（型、形式）
    - 副作用1（通知、課金、ログ等）

  depends:
    - 依存先1（DB/外部API/他モジュール）
    - 依存先2

  owns:
    - 自分が保証すること1
    - 自分が保証すること2

  touch: # 今回触る範囲
    - 対象1

  do_not_touch: # 今回触らない範囲
    - 対象1
```

### 失敗モード
- 仕様変更が周辺に波及し、後半で破綻する
- → 境界を先に固定することで、後の判断が成立する

---

## Skill 5: 不変条件の抽出

### 出力
```yaml
invariants:
  - condition: "不変条件1"
    source: 根拠（コード行/テスト名/ドキュメント）
    violation_symptom: 破ったときの症状

  - condition: "不変条件2"
    source: 根拠
    violation_symptom: 症状

  - condition: "不変条件3"
    source: 根拠
    violation_symptom: 症状
```

---

## Skill 6: アルゴリズム・設計意図の要約

### 出力
```yaml
algorithm_summary:
  objective: 何を最適化しているか
  assumptions:
    - 前提1
    - 前提2
  tradeoffs:
    - 何を捨てているか
  hypotheses: # 不確かな部分
    - 仮説1（要検証）
```

---

## Skill 7: 失敗モード仮説生成

### 出力
```yaml
failure_modes:
  frequent: # 起きやすい
    - description: 失敗パターン
      detection: 検知手段（テスト名/ログキー/メトリクス）

  critical: # 致命的
    - description: 失敗パターン
      detection: 検知手段

  subtle: # 気づきにくい
    - description: 失敗パターン
      detection: 検知手段
```

---

## Skill 8: 着手前の最小検証計画

### 出力
```yaml
verification_plan:
  time_budget: 15-30分

  todos:
    - action: 既存テスト実行
      command: npm test -- --grep "login"
    - action: 代表入力での挙動確認
      input: "test@example.com"
    - action: ログ確認
      key: "auth.login.attempt"

  falsification_conditions: # 何が起きたら仮説を捨てるか
    - "テストが5件以上失敗したら境界マップを再検討"
    - "予期しない依存が見つかったら入口発見からやり直し"
```

---

## Skill 9: 人間の理解確認（問い返しテスト）

### 出力
```yaml
understanding_check:
  confirmed:
    - 理解できた点1
    - 理解できた点2

  unknown_list: # 答えられなかった＝まだ分かっていない
    - 項目1
      resolution: どうやって調べるか
    - 項目2
      resolution: どうやって調べるか
```

### 失敗モード
- AIの説明で満足し、人間のスキーマが形成されない
- → 問い返しテストで必ず可視化する

---

## Skill 10: 作戦ブリーフ生成

### 出力
`references/briefing-template.md` のテンプレートに従う
