---
name: eld-sense-activation
description: |
  PCE (Process-Context Engine) のアクティブコンテキスト構築スキル。タスクに最適化されたコンテキストをコンパイルし、プロセス駆動の投入物を生成する。

  トリガー条件:
  - 新しいタスクを開始する時（「この機能を実装して」）
  - AIにコード生成を依頼する時
  - 複雑な問題解決に着手する時
  - 「コンテキストを整理して」
  - 「必要な情報をまとめて」
---

# PCE Activation Skill

潜在的コンテキストプールから、目的に最適化されたアクティブコンテキストを構築する。

## アクティブコンテキストの構造

```yaml
active_context:
  goal: |
    このタスクの真の目的
    期待する成果物
    完了条件

  constraints:
    - セキュリティ要件
    - 性能要件
    - 互換性要件
    - 禁止事項
    - 期限

  references:
    - 参照すべきドキュメント
    - 関連する既存コード
    - 過去の決定事項
    - 外部仕様

  context:
    - 実行環境
    - 依存ライブラリ
    - 前提条件

  expected_output:
    format: 成果物の形式
    quality: 品質基準
    validation: 検証方法
```

## コンパイルプロセス

### 1. Goal明確化
- 「何を達成したいか」を3行以内で言語化
- 曖昧な場合はユーザーに確認

### 2. Constraints収集
- pce-memoryからプロジェクトルール取得
- CLAUDE.mdからコーディング規約取得

### 3. References選択
- 関連性の高いものから優先
- Context budget（上限）を意識
- 必要最小限に絞る

### 4. 編集・圧縮
- 冗長な情報を削除
- 欠落を埋める
- 矛盾を解消

## Context Budget管理

| 項目 | 推奨上限 |
|------|---------|
| Goal | 3行 |
| Constraints | 5項目 |
| References | 3ファイル |
| Context | 必要最小限 |

## 使用例

```
User: ユーザー認証機能を実装して

Claude:
アクティブコンテキストを構築中...

## Goal
- JWTベースのユーザー認証機能を実装
- ログイン/ログアウト/トークンリフレッシュ

## Constraints
- セキュリティ: OWASP Top 10準拠
- 性能: レスポンス < 200ms

## References
- src/models/user.ts (既存Userモデル)
- docs/adr/ADR-003.md (認証方式決定)

## Expected Output
- src/auth/ 配下に実装
- 単体テスト必須

準備完了。実装を開始します。
```

---

## 品質優先原則（Superpowers統合）

### 核心原則

1. **Epistemic Humility**: 推測を事実として扱わない。`unknown`と言う勇気を持つ
2. **Evidence First**: 結論ではなく因果と証拠を中心にする
3. **Minimal Change**: 最小単位で変更し、即時検証する
4. **Grounded Laws**: Lawは検証可能・観測可能でなければならない
5. **Source of Truth**: 真実は常に現在のコード。要約はインデックス

### 「速さより質」の実践

- 要件の曖昧さによる手戻りを根本から排除
- テストなし実装を許さない
- 観測不能な変更を防ぐ

### 完了の定義

- [ ] Evidence Ladder目標レベル達成
- [ ] Issue Contractの物差し満足
- [ ] Law/Termが接地している（Grounding Map確認）
- [ ] Link Mapに孤立がない
- [ ] ロールバック可能な状態

### 停止条件

以下が発生したら即座に停止し、追加計測またはスコープ縮小：

- 予測と現実の継続的乖離（想定外テスト失敗3回以上）
- 観測不能な変更の増加（物差しで検証できない変更）
- ロールバック線の崩壊（戻せない変更の発生）
