# Sense（感知）フェーズ

コードの事実・意図・関係を観測し、身体図を更新する。

## 目的

- コードを「テキスト」ではなく「相互接続された意味のグラフ」として理解
- 曖昧さを「unknown」として明示
- 変更の影響範囲を把握

## 原則

**ファイルを全部読むのではなく、まず「地図」を作り、必要な場所だけを「拡大鏡」で読む。**

## 感知ツール優先度

| Tool | 用途 | 優先度 |
|------|------|--------|
| `context_bundle` | ゴールベースの関連コード検索 | 最初に使用 |
| `files_search` | キーワード/パターン検索 | 特定文字列の検索時 |
| `deps_closure` | 依存関係グラフの取得 | 影響範囲分析時 |
| `snippets_get` | 特定ファイルの詳細取得 | 最後に使用 |

## 感知ワークフロー

### Step 1: ゴールベース検索

```
context_bundle({
  goal: "<達成したいこと/調査したいこと>",
  category: "bugfix" | "feature" | "debug" | ...
})
```

### Step 2: 記憶の活性化

```
pce.memory.activate({
  q: "<検索キーワード>",
  scope: ["project"],
  top_k: 10
})
```

### Step 3: 鮮度チェック

取得した各エントリについて:
1. `last_verified_commit` を確認
2. 現在のHEADと比較
3. 不一致なら Step 4 へ

### Step 4: JIT再解析（必要時のみ）

```
1. context_bundle({goal: "<エンティティ関連のゴール>"})
2. snippets_get({path: "<該当ファイル>"}) で詳細取得
3. 新しい解釈を生成
4. pce.memory.upsert で更新
```

## 身体図の更新

### レイヤー構成

| レイヤー | 内容 | 更新タイミング |
|----------|------|----------------|
| シンボル | 関数/クラス/型 | コード変更時 |
| 設定 | 環境変数/設定ファイル | 設定変更時 |
| データ | DB/外部API/ファイル | スキーマ変更時 |
| 境界 | 入出力インターフェース | API変更時 |

### 影響範囲分析

```
deps_closure({
  path: "<対象ファイル>",
  direction: "inbound"  // または "outbound"
})
```

**direction**:
- `inbound`: このファイルに依存しているファイル（変更の影響先）
- `outbound`: このファイルが依存しているファイル（変更の影響元）

## リソース制限

1回の感知に対する上限:

| リソース | 上限 |
|----------|------|
| files_search 実行回数 | 3回 |
| snippets_get 対象ファイル数 | 5ファイル |
| deps_closure 再帰深度 | 2 |
| 1ファイルあたりの読み取り行数 | 200行 |

上限に達した場合:

```markdown
**調査範囲の制限に達しました**

より詳細な調査が必要な場合は、以下を指定してください:
- 特定のファイルパス
- 特定の関数/クラス名
- 調査の優先順位
```

## Epistemic Status の明示

感知結果には必ずEpistemic Statusを付与:

```markdown
## 回答

<回答本文>

### 根拠 [verified]

- `src/services/AuthService.ts:45-67` - ログイン処理の実装
- `src/db/UserRepo.ts:23` - ユーザー検索クエリ

### 推論 [inferred]

- パターンから推測すると、エラーハンドリングは上位レイヤーで行われている

### 未確認 [unknown]

- 外部APIの仕様に依存する部分は確認が必要
- 確認推奨箇所: `src/payment/Gateway.ts:95`
```

## 感知の限界宣言

以下の場合は正直に不明であると宣言:

- pce-memoryに情報がなく、kiriでも解読困難
- ロジックが複雑すぎて確信が持てない
- 外部サービスの仕様に依存する部分
- DI/生成/設定駆動で静的に追跡困難

```markdown
**この部分は確認が必要です**

コード (`src/payment/Gateway.ts:89-120`) を確認しましたが、
外部APIの仕様に依存するため正確な動作を断定できません。

確認推奨箇所:
- `src/payment/Gateway.ts:95` - API呼び出し部分
- 外部ドキュメント: PaymentProvider API仕様
```

## 記憶の保存

感知結果は3層構造で保存:

```typescript
pce.memory.upsert({
  text: JSON.stringify({
    entity_id: "src/services/AuthService.ts:login",
    type: "function",
    last_verified_commit: "a1b2c3d",
    facts: { /* 客観的事実 */ },
    semantics: { /* 意味論的解釈 */ },
    relations: { /* 構造的結合 */ }
  }),
  kind: "fact",
  scope: "project",
  boundary_class: "internal",
  provenance: {
    at: new Date().toISOString(),
    actor: "eld-sense",
    note: "kiri context_bundle結果から生成"
  }
})
```

## チェックリスト

- [ ] ゴールベース検索を最初に実行したか
- [ ] 記憶の活性化と鮮度チェックを行ったか
- [ ] 身体図の関連レイヤーを更新したか
- [ ] Epistemic Statusを明示したか
- [ ] 不明な点を「unknown」として宣言したか
- [ ] リソース制限を守ったか
