# ELD Issue Template

ELD (Evidence-Loop Development) v2.3 のIssue Contract雛形。

## Issue Contract

```markdown
## 目的（Goal）
<!-- 何を達成したいか。3行以内で明確に -->


## 不変条件（Invariants）
<!-- 変更してはいけないこと。既存の振る舞い、API互換性など -->
- [ ]


## 物差し（Acceptance Criteria）
<!-- 完了を判定する観測可能な基準 -->
- [ ] テスト:
- [ ] 性能:
- [ ] その他:


## 停止条件（Stop Conditions）
<!-- これが発生したら追加計測 or スコープ縮小 -->
- 予測と現実の継続的乖離
- 観測不能な変更の増加
- ロールバック線の崩壊
- その他:


## 制約（Constraints）
<!-- セキュリティ、性能、互換性、禁止事項、期限 -->
-


## 参照（References）
<!-- 関連ドキュメント、既存コード、過去の決定事項 -->
-
```

---

## 現状証拠（DCCA観測）

```markdown
## 関連モジュール
<!-- 目的に応じたツールで特定したファイル:
     - Grep: 特定キーワード検索
     - Glob: ファイルパターン検索
     - LSP: 定義・参照追跡
     - kiri context_bundle: 意味的関連探索
-->
- `path/to/file.ts:line` - 説明


## 既存の挙動
<!-- 現状どう動いているか。証拠付きで -->


## 影響範囲（依存グラフ）
<!-- deps_closureで特定した依存元 -->


## 未確定事項
<!-- 分からないこと。推測には [推測] タグ -->
- [推測]
```

---

## Term/Law候補（Spec Phase A-B）

```markdown
## Vocabulary候補（Term）
<!-- 主要な語彙と意味 -->
| ID | 名前 | 意味 | 確度 |
|----|------|------|------|
| TERM-xxx | | | High/Medium/Low |


## Law候補（関係・制約）
<!-- 守るべき条件 -->
| ID | Type | Statement | Terms | 確度 |
|----|------|-----------|-------|------|
| LAW-xxx | Pre/Post/Inv | | | High/Medium/Low |


## 未確定・要確認
<!-- レビューが必要な点 -->
-
```

---

## チェックリスト

- [ ] 目的が明確（3行以内）
- [ ] 物差しが観測可能（テスト/メトリクスで判定可能）
- [ ] 停止条件が定義されている
- [ ] 現状証拠がある（推測ではない）
- [ ] Term/Law候補が列挙されている
