# Severity Scoring Rules

深刻度スコアリングの詳細ルール。

## ベーススコア決定

### Security疑い（base 9）

以下のいずれかが検出された場合:
- credential/パスワード/トークンの露出疑い
- 権限昇格の可能性
- 認証バイパスの兆候
- データ漏洩の兆候
- インジェクション攻撃の可能性

### データ損失/破損（base 8）

- データが消失する可能性
- データが破損する可能性
- 不可逆な状態変更
- バックアップ不能な状態

### 主要機能不全（base 7）

critical_user_flows に該当する機能の障害:
- ログイン/認証
- 決済/課金
- コアビジネスロジック
- データ登録/更新の主要フロー

### 性能劣化/部分機能不全（base 4-6）

- レスポンス大幅遅延（base 5-6）
- 特定条件下での機能不全（base 4-5）
- エラーが発生するが回避策あり（base 4）

### UI/UX軽微（base 1-3）

- 表示崩れ（base 2-3）
- タイポ/文言（base 1）
- 軽微な操作性問題（base 2）

### Enhancement（base 1-2）

- 機能追加要求（base 2）
- 改善提案（base 1）

## Modifiers（修正子）

### 加点（+1 each, max +3）

| 条件 | 根拠 |
|------|------|
| prod影響が明記 | 本番環境への影響は重大 |
| 多数ユーザー影響が明記 | 影響範囲が広い |
| 回避策なし | ユーザーが stuck する |
| 回帰（以前は動いた） | リリース起因の可能性 |

### 減点（-1 each, max -3）

| 条件 | 根拠 |
|------|------|
| 影響が限定的（特定端末/アカウント） | 影響範囲が狭い |
| 回避策あり | ユーザーは業務継続可能 |
| 再現性が低い/断片的 | 確証が持てない |

## Confidence 算出

confidence は情報の充足度と矛盾の少なさを 0-1 で表現。

### 減点要因（-0.1 each）

- `missing_repro_steps`: 再現手順なし
- `missing_expected_vs_actual`: 期待/実際の記載なし
- `missing_environment`: 環境情報なし
- `missing_logs`: ログ/エラー情報なし
- `missing_frequency`: 発生頻度不明
- `missing_impact_breadth`: 影響範囲不明
- 本文が極端に短い（100文字未満）
- 矛盾する情報が含まれる

### 基準値

| confidence | 解釈 |
|------------|------|
| 0.8-1.0 | 高確信。十分な情報あり |
| 0.5-0.7 | 中程度。追加情報が望ましい |
| 0.3-0.4 | 低確信。情報取得優先 |
| 0.0-0.2 | 判断困難。NeedsInfo検討 |

## 不確実性ポリシー

```
uncertainty_flagsが多い場合:
  1. confidenceを下げる（機械的に-0.1/flag）
  2. severity_scoreは上限側に寄せない
  3. ただしsecurity_signal=trueの場合は例外的に高めを維持
```

## 計算例

```yaml
# 入力: "ログインできない" のみ、詳細なし

base_score: 7  # 主要機能疑い
modifiers: 0   # 情報不足で加減点なし
final_score: 7

uncertainty_flags:
  - missing_repro_steps      # -0.1
  - missing_environment      # -0.1
  - missing_expected_vs_actual # -0.1
  - missing_logs             # -0.1
  - missing_frequency        # -0.1
  - missing_impact_breadth   # -0.1

confidence: 1.0 - 0.6 = 0.4

# 結論: severity 7/10, confidence 0.40
# → Major だが情報取得を優先すべき
```
