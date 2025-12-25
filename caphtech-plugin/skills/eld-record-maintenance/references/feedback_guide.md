# feedback 詳細ガイド

## 概要

`pce_memory_feedback` は Claim の評価・修正・削除を行うための MCP ツールである。このガイドでは、feedback の効果的な使用方法を詳細に説明する。

## feedback の基本構造

```yaml
pce_memory_feedback({
  claim_hash: string    # 対象 Claim の content_hash（必須）
  signal: string        # positive | negative | delete（必須）
  note: string          # 理由・コンテキスト（推奨）
})
```

## シグナル詳細

### positive シグナル

**目的:** Claim が有用で正確であることを記録する

**効果:**
- Claim の信頼度スコアが向上
- AC 構築時の優先度が上がる
- 長期保持の候補となる

**使用タイミング:**
- Claim の内容が現在も正確であることを確認した時
- Claim が実際のタスクで役立った時
- 定期レビューで問題がないことを確認した時

**例:**
```
# 技術的事実の確認
pce_memory_feedback({
  claim_hash: "sha256:abc123...",
  signal: "positive",
  note: "コードベース確認: XState v5 が src/machines/ で使用されている"
})

# ポリシーの有効性確認
pce_memory_feedback({
  claim_hash: "sha256:def456...",
  signal: "positive",
  note: "CLAUDE.md と一致: pnpm のみ使用ルールは有効"
})

# タスクでの有用性
pce_memory_feedback({
  claim_hash: "sha256:ghi789...",
  signal: "positive",
  note: "Issue #500 の解決に役立った"
})
```

### negative シグナル

**目的:** Claim に問題があることを記録する

**効果:**
- Claim の信頼度スコアが低下
- レビュー対象としてマークされる
- AC 構築時の優先度が下がる

**使用タイミング:**
- Claim が部分的に不正確な時
- Claim が古くなりつつある時
- Claim の表現が不明確な時
- 削除するほどではないが問題がある時

**例:**
```
# 部分的な不正確さ
pce_memory_feedback({
  claim_hash: "sha256:...",
  signal: "negative",
  note: "バージョン情報が古い: XState v4 ではなく v5 を使用中"
})

# 曖昧な表現
pce_memory_feedback({
  claim_hash: "sha256:...",
  signal: "negative",
  note: "表現が曖昧: 'いくつかのモジュール' → 具体的なパスが必要"
})

# 重複の可能性
pce_memory_feedback({
  claim_hash: "sha256:...",
  signal: "negative",
  note: "sha256:xyz... と類似。統合を検討"
})
```

### delete シグナル

**目的:** Claim の削除を要求する

**効果:**
- Claim が削除候補としてマークされる
- システムによる削除処理が実行される
- 関連する Relation も影響を受ける可能性

**使用タイミング:**
- Claim が明らかに不正確な時
- Claim が完全に古くなった時
- 重複 Claim を統合した後
- Claim が不要になった時

**例:**
```
# 不正確な情報の削除
pce_memory_feedback({
  claim_hash: "sha256:...",
  signal: "delete",
  note: "事実誤認: Firebase ではなく Cognito を使用"
})

# 古い情報の削除
pce_memory_feedback({
  claim_hash: "sha256:...",
  signal: "delete",
  note: "ADR-0009 により無効: Redux は XState に置換済み"
})

# 重複の削除
pce_memory_feedback({
  claim_hash: "sha256:...",
  signal: "delete",
  note: "重複削除: sha256:canonical... に統合済み"
})
```

## note の書き方ベストプラクティス

### 良い note の特徴

1. **具体的な理由**: なぜこのシグナルを送るのか
2. **証拠の参照**: 根拠となる情報源
3. **関連する識別子**: 関連 Claim や Issue の参照
4. **アクション可能**: 次のステップが明確

### note テンプレート

```
# positive
"[確認方法]: [確認結果]"
例: "CLAUDE.md 確認: ログポリシーは logger.* 使用で正しい"

# negative
"[問題の種類]: [具体的な問題内容]"
例: "情報古い: v4 → v5 への更新が必要"

# delete
"[削除理由]: [根拠または代替]"
例: "重複削除: sha256:abc... に統合済み"
```

### note の長さガイドライン

- **最小**: 10文字（理由が明確な場合）
- **推奨**: 30-100文字
- **最大**: 200文字（複雑な状況の場合）

## 複数 Claim への一括対応

### 重複 Claim の統合

```
# 1. 統合先の Claim を作成
pce_memory_upsert({
  text: "パッケージ管理は pnpm のみ使用（npm 禁止）",
  ...
})

# 2. 元の Claim A を削除
pce_memory_feedback({
  claim_hash: "sha256:claim-a...",
  signal: "delete",
  note: "統合: sha256:merged... に統合"
})

# 3. 元の Claim B を削除
pce_memory_feedback({
  claim_hash: "sha256:claim-b...",
  signal: "delete",
  note: "統合: sha256:merged... に統合"
})
```

### 矛盾 Claim の解決

```
# 1. 正しい Claim を確認
pce_memory_feedback({
  claim_hash: "sha256:correct...",
  signal: "positive",
  note: "矛盾解決: こちらが CLAUDE.md と一致"
})

# 2. 誤った Claim を削除
pce_memory_feedback({
  claim_hash: "sha256:wrong...",
  signal: "delete",
  note: "矛盾解決: sha256:correct... が正しい"
})
```

### 階層的な更新

親 Claim を更新する場合、子 Claim への影響を確認する。

```
# 1. 親 Claim の状態を確認
# "状態管理には Redux を使用" → XState に変更

# 2. 子 Claim を確認
# - "Redux の store は src/store/ に配置" → 無効化が必要
# - "Redux DevTools を使用" → 無効化が必要

# 3. 親 Claim を置換
pce_memory_upsert({
  text: "状態管理には XState を使用する",
  ...
})
pce_memory_feedback({
  claim_hash: "sha256:redux-parent...",
  signal: "delete",
  note: "XState に移行: ADR-0009"
})

# 4. 子 Claim も対応
pce_memory_feedback({
  claim_hash: "sha256:redux-store...",
  signal: "delete",
  note: "親 Claim (Redux) が無効化されたため"
})
```

## feedback の頻度とタイミング

### 即時対応が必要なケース

- 明らかな事実誤認を発見
- セキュリティに関わる誤情報
- 矛盾する Claim の発見

### 定期レビューで対応するケース

- 軽微な不正確さ
- 表現の改善
- 重複の検出

### feedback を送らないケース

- 単なる表現の好み（内容が正確な場合）
- 一時的な状況への言及（session scope で対応）
- 確信が持てない場合（調査を優先）

## トラブルシューティング

### feedback が反映されない場合

1. claim_hash が正しいか確認
2. Claim が既に削除されていないか確認
3. pce-memory の状態を確認

### 誤って delete を送った場合

- pce-memory の設計によっては復元が可能
- 必要に応じて同じ内容で新しい Claim を作成

### 大量の feedback が必要な場合

1. 優先度の高いものから対応
2. バッチ処理を検討
3. 根本原因（収集や構造化の問題）を調査
