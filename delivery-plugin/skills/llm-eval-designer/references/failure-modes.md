# LLM Failure Modes

LLM生成システムに特有の失敗パターンとその検出・対策。

## 1. 例への過学習（Example Overfitting）

**症状**: プロンプト内の具体例と同じ/類似の入力には正しく動作するが、異なる入力では失敗。

**実例**:
```
プロンプト例: "カート → Cart"
✓ 成功: "カート" の置換
✗ 失敗: "ユーザー" の置換（同じ置換ロジックなのに）
```

**検出テスト設計**:
```yaml
detection_strategy:
  # プロンプト例と異なる入力でテスト
  test_categories:
    - same_category_different_example  # カタカナ語だがカート以外
    - different_category               # 漢字語、英語など

  constraint: "テスト入力 ∩ プロンプト例 = ∅"
```

**対策**:
- プロンプト例を汎用的にする（具体的な単語を避ける）
- 複数カテゴリの例を含める
- 「任意のテキストX」のような抽象的表現を使用

---

## 2. 幻覚（Hallucination）

**症状**: 入力に存在しない情報を生成する。

**実例**:
```
入力: 12節のドキュメント
期待: 置換のみ
実際: 12.4節を新規追加（存在しない内容）
```

**検出テスト設計**:
```yaml
detection_strategy:
  # 入力と出力の差分を厳密に検証
  checks:
    - no_new_content_added      # 新規コンテンツの追加がない
    - no_blocks_deleted         # 既存ブロックの削除がない
    - only_specified_changes    # 指定された変更のみ

  scorer: anti-hallucination
  threshold: 100%  # 幻覚は0でなければならない
```

**対策**:
- プロンプトに明示的な禁止事項を追加
- 「DO NOT add/delete/invent」のような強い制約
- 入出力の構造比較による自動検出

---

## 3. 部分的処理（Partial Processing）

**症状**: 対象のうち一部のみを処理し、残りを見逃す。

**実例**:
```
入力: 20箇所の "カート"
期待: 20箇所すべて置換
実際: 5箇所のみ置換（先頭付近のみ）
```

**検出テスト設計**:
```yaml
detection_strategy:
  # 網羅性を検証
  test_cases:
    - multiple_occurrences_single_block   # 1ブロック内に複数出現
    - multiple_blocks_with_target         # 複数ブロックに分散
    - large_document                      # 30+ブロックの大規模ドキュメント

  verification:
    - count_all_matches_before
    - count_all_replacements_after
    - assert: before_count == after_count
```

**対策**:
- 「ALL blocks」「EVERY occurrence」を明示
- ブロックプレビューの文字数制限を緩和
- 処理完了の明示的な確認ステップ

---

## 4. 指示誤解釈（Instruction Misinterpretation）

**症状**: 類似だが異なる動作を行う。

**実例**:
```
指示: "置換してください"
期待: テキストの置換のみ
実際: 置換 + ブロック構造の変更
```

**検出テスト設計**:
```yaml
detection_strategy:
  # 境界条件で明確に区別
  test_cases:
    - replace_vs_insert          # 置換と挿入の区別
    - replace_vs_delete          # 置換と削除の区別
    - partial_vs_full            # 部分置換と全体置換

  boundary_tests:
    - exactly_what_was_asked     # 指示通りのみ
    - nothing_more               # 余計なことをしない
    - nothing_less               # 足りないこともない
```

**対策**:
- 操作種別ごとに明確な定義をプロンプトに記載
- 「ONLY do X, do NOT do Y」形式の制約
- 各操作種別の期待される出力形式を明示

---

## 5. コンテキスト喪失（Context Loss）

**症状**: 長いドキュメントの後半で精度が低下。

**実例**:
```
入力: 50ブロックのドキュメント
結果: 前半20ブロックは正確、後半は不正確/欠落
```

**検出テスト設計**:
```yaml
detection_strategy:
  # 位置による精度の変化を検証
  test_cases:
    - target_at_beginning        # 先頭付近
    - target_at_middle           # 中央
    - target_at_end              # 末尾
    - target_distributed         # 全体に分散

  analysis:
    - precision_by_position
    - recall_by_position
```

**対策**:
- ブロックインデックスを明示
- 重要な情報を複数回提示
- 分割処理の検討

---

## 失敗モード検出マトリクス

| 失敗モード | 検出スコアラー | 必須テストパターン |
|-----------|---------------|------------------|
| 例への過学習 | operation-accuracy | 異カテゴリ入力 |
| 幻覚 | anti-hallucination | 入出力差分検証 |
| 部分的処理 | target-block-precision | 複数出現テスト |
| 指示誤解釈 | operation-accuracy | 境界条件テスト |
| コンテキスト喪失 | content-quality | 位置分散テスト |
