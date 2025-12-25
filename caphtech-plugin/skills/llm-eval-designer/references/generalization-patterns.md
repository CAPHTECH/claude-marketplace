# Generalization Patterns

LLMの汎化能力を検証するためのテスト設計パターン。

## 原則: テスト入力 ∩ プロンプト例 = ∅

プロンプトに含まれる例と同じ入力でテストしても、過学習を検出できない。

```
プロンプト例: X
    ↓
テストケース: X以外のY, Z, A, B...
```

---

## Pattern 1: カテゴリ多様性

同じ操作を異なるカテゴリの入力でテスト。

```yaml
# テキスト置換の例
categories:
  katakana:     # カタカナ語
    - "カート → Cart"
    - "ユーザー → 利用者"
    - "サービス → Service"

  kanji:        # 漢字語
    - "効率化 → 最適化"
    - "管理者 → 運用者"

  english:      # 英語
    - "API → インターフェース"
    - "URL → アドレス"

  mixed:        # 混合
    - "DB接続 → データベース接続"

  special:      # 特殊文字
    - "→ → ⇒"
    - "（旧） → 【旧】"
```

**テスト設計ルール**:
```
IF プロンプト例がカテゴリXの場合:
  必須テスト:
    - カテゴリXの別の例（同種汎化）
    - カテゴリY, Zの例（異種汎化）
```

---

## Pattern 2: 規模多様性

同じ操作を異なる規模でテスト。

```yaml
scale_levels:
  minimal:      # 最小
    blocks: 1
    occurrences: 1

  small:        # 小規模
    blocks: 3-5
    occurrences: 3-5

  medium:       # 中規模
    blocks: 10-15
    occurrences: 10-15

  large:        # 大規模
    blocks: 30+
    occurrences: 20+
```

**テスト設計ルール**:
```
各規模レベルで最低1テストケースを含める
特に large は部分的処理の検出に重要
```

---

## Pattern 3: 出現パターン多様性

同じ操作を異なる出現パターンでテスト。

```yaml
occurrence_patterns:
  single_block_single:     # 1ブロック内に1回
    blocks: [A]
    pattern: "...target..."

  single_block_multiple:   # 1ブロック内に複数回
    blocks: [A]
    pattern: "...target...target...target..."

  multi_block_single:      # 複数ブロックに各1回
    blocks: [A, B, C]
    pattern: "A:target, B:target, C:target"

  multi_block_multiple:    # 複数ブロック × 複数回
    blocks: [A, B, C]
    pattern: "A:target×2, B:target×3, C:target×1"

  nested:                  # ネストされたブロック
    blocks: [A > B > C]
    pattern: "A:target, B:target, C:target"
```

---

## Pattern 4: 境界条件

エッジケースと境界条件を網羅。

```yaml
boundary_conditions:
  empty:
    - empty_page           # 空のページ
    - empty_block          # 空のブロック
    - no_matches           # マッチなし

  single:
    - single_character     # 1文字
    - single_block         # 1ブロック
    - single_match         # 1マッチ

  maximum:
    - very_long_text       # 非常に長いテキスト
    - many_blocks          # 多数のブロック
    - many_matches         # 多数のマッチ

  special:
    - special_characters   # 特殊文字
    - unicode              # Unicode文字
    - whitespace           # 空白・改行
```

---

## Pattern 5: 操作組み合わせ

複数の操作を組み合わせてテスト。

```yaml
operation_combinations:
  single_page:
    - insert_only          # 挿入のみ
    - replace_only         # 置換のみ
    - delete_only          # 削除のみ
    - insert_and_replace   # 挿入 + 置換
    - replace_and_delete   # 置換 + 削除
    - all_three            # 全操作

  multi_page:
    - same_op_all_pages    # 全ページ同一操作
    - different_ops        # ページごとに異なる操作
    - selective            # 一部ページのみ操作
```

---

## 汎化テストマトリクス生成

```yaml
# ペアワイズ法による組み合わせ削減
dimensions:
  - category: [katakana, kanji, english, special]
  - scale: [minimal, small, medium, large]
  - occurrence: [single, multiple, nested]
  - operation: [insert, replace, delete]

# 全組み合わせ: 4×4×3×3 = 144
# ペアワイズ削減後: 約20-30テストケース

priority_rules:
  high:
    - category != prompt_example_category
    - scale == large
    - occurrence == multiple
  medium:
    - boundary conditions
  low:
    - redundant combinations
```

---

## チェックリスト

```
[ ] プロンプト例と同じ入力をテストに含めていないか？
[ ] 複数のカテゴリ（カタカナ、漢字、英語）をカバーしているか？
[ ] 複数の規模（最小、小、中、大）をカバーしているか？
[ ] 複数の出現パターンをカバーしているか？
[ ] 境界条件を網羅しているか？
[ ] 操作の組み合わせをテストしているか？
```
