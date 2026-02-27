---
name: eld-predict-light
context: fork
description: |
  ELD v2.3 Predict-Lightゲート。変更の影響度をP0/P1/P2で自動判定し、
  適切な検証深度を決定する。フルPredictの代わりに軽量ゲートとして機能。
  使用タイミング: (1) Change前の自動判定, (2) 「影響度を判定して」「P0/P1/P2を判定して」,
  (3) 実装前のリスク評価, (4) 段階化計画の策定
---

# ELD Predict-Light Gate

## Purpose

Change前の影響度を **P0 / P1 / P2** で自動判定し、検証深度を決定する軽量ゲート。
フルPredictスキル（廃止）の代わりに、必要十分な分析を最小コストで提供する。

---

## Impact Level Definitions

| Level | 条件 | 検証深度 |
|-------|------|----------|
| **P2** | 公開API変更 / DB スキーマ変更 / 認証・認可変更 / 課金ロジック変更 | フル影響分析 |
| **P1** | 複数ファイル変更 / テスト未カバー領域 / 外部依存変更 | 影響リスト + 停止条件 |
| **P0** | 上記いずれにも非該当 | 3行要約のみ |

### P2 詳細条件

- エンドポイントの追加・削除・シグネチャ変更（パス、メソッド、リクエスト/レスポンス型）
- テーブル作成・カラム追加削除・インデックス変更・マイグレーション
- 認証フロー変更、権限モデル変更、トークン/セッション処理変更
- 料金計算、サブスクリプション、決済連携、使用量計測の変更

### P1 詳細条件

- 3ファイル以上の同時変更
- 変更箇所のテストカバレッジが不十分（カバレッジ < 80% or 該当テストなし）
- 外部ライブラリのバージョン変更、外部API呼び出しの変更

### P0 条件

- P2・P1のいずれにも該当しない変更
- 例: ドキュメント修正、コメント追加、リネーム、フォーマット修正、単一ファイルの内部ロジック微修正（テストカバー済み）

---

## Machine Judgment Logic

```pseudo
function predict_light(change_set):
    # Phase 1: P2 check (critical domain detection)
    if touches_public_api(change_set):        return P2, "公開API変更"
    if touches_db_schema(change_set):          return P2, "DBスキーマ変更"
    if touches_auth(change_set):               return P2, "認証・認可変更"
    if touches_billing(change_set):            return P2, "課金ロジック変更"

    # Phase 2: P1 check (complexity/risk detection)
    if count_files(change_set) >= 3:           return P1, "複数ファイル変更"
    if test_coverage(change_set) < 0.80:       return P1, "テスト未カバー"
    if has_no_tests(change_set):               return P1, "テスト未カバー"
    if touches_external_deps(change_set):      return P1, "外部依存変更"

    # Phase 3: Default to P0
    return P0, "該当条件なし"
```

### 判定ヒューリスティクス

| チェック関数 | 判定方法 |
|-------------|---------|
| `touches_public_api` | ルーター/コントローラー定義、OpenAPI spec、エンドポイントハンドラの変更を検出 |
| `touches_db_schema` | マイグレーションファイル、モデル定義、スキーマファイルの変更を検出 |
| `touches_auth` | auth/、middleware/auth、permission、role、token、session 関連ファイルの変更を検出 |
| `touches_billing` | billing/、payment/、subscription/、pricing 関連ファイルの変更を検出 |
| `touches_external_deps` | package.json, go.mod, Cargo.toml, requirements.txt 等の依存定義変更を検出 |
| `test_coverage` | 変更対象ファイルに対応するテストファイルの存在とカバレッジを推定 |

---

## Manual Override

エージェントの自動判定は **Manual Override** で上書き可能。

### Override 構文

```
OVERRIDE: P{n} → P{m} REASON: {理由}
```

### Override ルール

1. **昇格（P0→P1, P1→P2）**: 常に許可。理由を記録。
2. **降格（P2→P1, P1→P0）**: 理由の明示が必須。以下の場合のみ許可:
   - 変更が既存テストで完全にカバーされていることを証明できる場合
   - 変更が後方互換性を完全に保つことを証明できる場合
3. **監査記録**: すべてのOverrideは `eld/references/predict-light-audit.md` に記録する。

### 週次監査

- 毎週、Override履歴をレビューし、自動判定ロジックの改善にフィードバックする。
- 誤判定パターンが3回以上繰り返された場合、判定ロジックを更新する。
- 監査結果は `eld/references/predict-light-audit.md` に追記する。

---

## Output Templates

### P0 Output（3行要約）

```markdown
## Predict-Light: P0

**変更概要**: {1行の変更説明}
**影響範囲**: {直接影響するファイル/モジュール}
**判定根拠**: {P0判定の理由}
```

### P1 Output（影響リスト + 停止条件）

```markdown
## Predict-Light: P1

**変更概要**: {変更の説明}
**判定根拠**: {P1判定の理由}

### 影響リスト
| # | 影響対象 | 影響種別 | 確信度 |
|---|---------|---------|--------|
| 1 | {ファイル/モジュール} | {direct/indirect} | {high/medium/low} |

### 停止条件
- [ ] {条件1}: {具体的な停止トリガー}
- [ ] {条件2}: {具体的な停止トリガー}

### 推奨アクション
- {検証すべき項目}
```

### P2 Output（フル影響分析）

```markdown
## Predict-Light: P2

**変更概要**: {変更の詳細説明}
**判定根拠**: {P2判定の理由}
**リスクレベル**: {high/critical}

### 影響分析
| # | 影響対象 | 影響種別 | 確信度 | 検証方法 |
|---|---------|---------|--------|---------|
| 1 | {対象} | {direct/indirect/transitive} | {high/medium/low} | {テスト/手動確認/レビュー} |

### 破壊的変更チェック
- [ ] 後方互換性: {評価}
- [ ] データ整合性: {評価}
- [ ] 外部連携影響: {評価}

### 停止条件
- [ ] {条件1}: {具体的な停止トリガーと対処方針}
- [ ] {条件2}: {具体的な停止トリガーと対処方針}

### 段階化計画
1. {Phase 1}: {内容} → {検証ポイント}
2. {Phase 2}: {内容} → {検証ポイント}

### 必須レビュー項目
- {専門レビューが必要な領域}
```

詳細テンプレートは `eld/references/predict-light-template.md` を参照。

---

## Stop Conditions（標準セット）

以下の条件に該当した場合、即座に作業を停止し報告する。

| ID | 条件 | 対応 |
|----|------|------|
| S-PRED-01 | 判定に必要な情報が不足（ファイル読み取り不可、コンテキスト不明） | 不足情報を列挙して停止 |
| S-PRED-02 | 変更範囲が曖昧で影響度を確定できない | 変更範囲の明確化を要求して停止 |
| S-PRED-03 | P2判定だが段階化計画を立案できない複雑さ | 人間の判断を仰いで停止 |
| S-PRED-04 | Override降格の根拠が不十分 | 降格を拒否し理由を説明 |
| S-PRED-05 | 複数のP2条件に同時該当 | 最も重大な条件を優先し全条件を報告 |

---

## Reflection Selection

各判定完了後、以下のいずれかのリフレクションを実施する。

### Mechanical Reflection
- 判定ロジックが正しく適用されたか確認
- 見落とした条件がないか再チェック
- 使用タイミング: P0判定時（軽量確認）

### Design Reflection
- 判定結果がプロジェクトのアーキテクチャ方針と整合しているか確認
- 影響範囲の見積もりが妥当か、過小/過大評価していないか検証
- 使用タイミング: P1判定時（中程度の確認）

### Stop Reflection
- 停止条件に該当していないか最終確認
- Override適用時の妥当性検証
- 段階化計画の実行可能性確認
- 使用タイミング: P2判定時、Override適用時（重点確認）

---

## Execution Flow

```
1. 変更セットを受け取る
2. Machine Judgment Logicで自動判定 → P0/P1/P2
3. Manual Overrideが指示されている場合は適用
4. 判定レベルに応じたOutput Templateで出力
5. Reflection実施（レベルに応じて選択）
6. 停止条件チェック
7. 結果を返却（後続のChange/Groundスキルへ引き継ぎ）
```
