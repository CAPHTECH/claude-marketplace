# Classification（分類定義）

ワークフローテンプレート選択のための分類基準。

## severity（深刻度）

### trivial

**定義**: 機能影響が限定的な軽微な変更

**例**:
- ドキュメント修正
- typo修正
- コメント追加/修正
- CI設定の軽微な調整
- ログメッセージの修正

**特徴**:
- ロールバックがほぼ不要
- テスト追加は任意
- レビューは簡略化可能

### minor

**定義**: 限定ケースのバグ、影響範囲が狭い

**例**:
- 特定条件下でのみ発生するバグ
- UIの軽微な表示崩れ
- エラーハンドリングの改善
- 性能の軽微な改善

**特徴**:
- ロールバック容易
- 影響範囲が1-2モジュール
- 単体テスト追加推奨

### major

**定義**: 主要フローに影響、複数モジュールに波及

**例**:
- 主要機能のバグ修正
- API変更を伴う修正
- 複数モジュールにまたがる修正
- 性能の大幅改善

**特徴**:
- テスト追加必須
- 影響範囲分析必須
- レビュー強化

### critical

**定義**: 緊急対応が必要

**例**:
- データ破壊の可能性
- セキュリティ脆弱性
- 広範囲の障害
- 本番環境の停止

**特徴**:
- 緊急対応フロー適用
- 承認プロセス短縮可
- ロールバック計画必須
- 事後レビュー必須

## type（種別）

### bugfix

**定義**: 既存機能の不具合修正

**判定条件**:
- 期待と実際の動作に乖離がある
- 以前は動いていた（回帰）
- 仕様通りに動かない

### feature

**定義**: 新機能追加

**判定条件**:
- 新しい機能の実装
- 既存機能の拡張
- 新しいエンドポイント/画面の追加

**追加フェーズ**:
- 設計フェーズが追加される

### refactor

**定義**: 機能変更なしの内部改善

**判定条件**:
- 外部挙動は変わらない
- コード品質の改善
- 依存関係の整理
- パフォーマンス最適化

**注意**:
- `affected_files > 10` の場合は承認必要

### chore

**定義**: 維持管理タスク

**判定条件**:
- 依存ライブラリの更新
- CI/CD設定の変更
- 開発環境の改善

### security

**定義**: セキュリティ関連の修正

**判定条件**:
- 脆弱性の修正
- 認証/認可の改善
- データ保護の強化

**特徴**:
- 別テンプレート（security_fix_v1）を適用
- 追加の検証ステップ
- セキュリティチームの承認

### docs

**定義**: ドキュメントのみの変更

**判定条件**:
- README、API仕様書等の更新
- コードコメントの大幅な改善

## 分類マトリクス

| issue-intake結果 | type | severity |
|------------------|------|----------|
| classification=Critical, security_signal=true | security | critical |
| classification=Critical | bugfix | critical |
| classification=Major | bugfix | major |
| classification=Minor | bugfix | minor |
| classification=Enhancement, type=feature | feature | 内容による |
| classification=Enhancement, type=refactor | refactor | 内容による |
| classification=NeedsInfo | - | 分類保留 |

## テンプレート選択ロジック

```
if type == "security":
    return "security_fix_v1"

if severity == "critical":
    return "critical_hotfix_v1"

if severity == "trivial":
    return "trivial_fix_v1"

if type == "feature":
    return "feature_v1"

if severity == "minor":
    return "minor_bugfix_v1"

if severity == "major":
    return "major_bugfix_v2"

# default
return "minor_bugfix_v1"
```
