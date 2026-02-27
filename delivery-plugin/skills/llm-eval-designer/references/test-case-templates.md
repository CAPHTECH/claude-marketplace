# Test Case Templates

assay-kit/golden-dataset.yaml形式のテストケーステンプレート。

## 基本構造

```yaml
- id: "<category>-<operation>-<number>"
  name: "<日本語の説明的な名前>"
  userMessage: "<ユーザーからのリクエスト>"
  pages:
    - id: "<uuid>"
      title: "<ページタイトル>"
      blocks:
        - id: "<block-id>"
          type: "<block-type>"
          content:
            - type: "text"
              text: "<テキスト内容>"
          children: []
      version: 1
  expected:
    operations:
      - pageId: "<uuid>"
        operations:
          - type: "<insert|replace|delete>"
            targetBlockId: "<block-id>"
            position: "<before|after>"  # insertの場合のみ
            expectedContentPatterns:
              - "<正規表現パターン>"
    totalSuccessCount: <期待される成功ページ数>
  scorers:  # オプション
    - type: operation-accuracy
      weight: 1.0
    - type: target-block-precision
      weight: 1.0
    - type: content-quality
      weight: 1.0
```

---

## Template 1: 基本置換テスト

```yaml
- id: "replace-basic-001"
  name: "基本的なテキスト置換"
  userMessage: "「古いテキスト」を「新しいテキスト」に置換してください"
  pages:
    - id: "00000000-0000-0000-0000-000000000001"
      title: "テストページ"
      blocks:
        - id: "block-001"
          type: "paragraph"
          content:
            - type: "text"
              text: "これは古いテキストを含む文章です。"
          children: []
      version: 1
  expected:
    operations:
      - pageId: "00000000-0000-0000-0000-000000000001"
        operations:
          - type: "replace"
            targetBlockId: "block-001"
            expectedContentPatterns:
              - "新しいテキスト"
    totalSuccessCount: 1
```

---

## Template 2: 複数出現置換テスト

```yaml
- id: "replace-multiple-001"
  name: "複数出現の全置換"
  userMessage: "「ターゲット」を「置換後」に置換してください"
  pages:
    - id: "00000000-0000-0000-0000-000000000001"
      title: "複数出現テスト"
      blocks:
        - id: "block-001"
          type: "paragraph"
          content:
            - type: "text"
              text: "ターゲットとターゲットとターゲットが含まれています。"
          children: []
        - id: "block-002"
          type: "paragraph"
          content:
            - type: "text"
              text: "別のブロックにもターゲットがあります。"
          children: []
      version: 1
  expected:
    operations:
      - pageId: "00000000-0000-0000-0000-000000000001"
        operations:
          - type: "replace"
            targetBlockId: "block-001"
            expectedContentPatterns:
              - "置換後.*置換後.*置換後"  # 3回の置換
          - type: "replace"
            targetBlockId: "block-002"
            expectedContentPatterns:
              - "置換後"
    totalSuccessCount: 1
```

---

## Template 3: 汎化テスト（異カテゴリ）

```yaml
# プロンプト例が「カート」の場合、異なるカテゴリでテスト
- id: "generalization-kanji-001"
  name: "漢字語の置換（汎化テスト）"
  userMessage: "「効率化」を「最適化」に置換してください"
  pages:
    - id: "00000000-0000-0000-0000-000000000001"
      title: "業務改善計画"
      blocks:
        - id: "block-001"
          type: "heading"
          content:
            - type: "text"
              text: "効率化の目標"
          children: []
        - id: "block-002"
          type: "paragraph"
          content:
            - type: "text"
              text: "本プロジェクトでは効率化を目指します。"
          children: []
      version: 1
  expected:
    operations:
      - pageId: "00000000-0000-0000-0000-000000000001"
        operations:
          - type: "replace"
            targetBlockId: "block-001"
            expectedContentPatterns:
              - "最適化"
          - type: "replace"
            targetBlockId: "block-002"
            expectedContentPatterns:
              - "最適化"
    totalSuccessCount: 1
```

---

## Template 4: 幻覚検出テスト

```yaml
- id: "anti-hallucination-001"
  name: "幻覚防止テスト（内容追加なし）"
  userMessage: "「A」を「B」に置換してください"
  pages:
    - id: "00000000-0000-0000-0000-000000000001"
      title: "シンプルなドキュメント"
      blocks:
        - id: "block-001"
          type: "paragraph"
          content:
            - type: "text"
              text: "AとAがある文章。"
          children: []
      version: 1
  expected:
    operations:
      - pageId: "00000000-0000-0000-0000-000000000001"
        operations:
          - type: "replace"
            targetBlockId: "block-001"
            expectedContentPatterns:
              - "^BとBがある文章。$"  # 完全一致（余計な内容なし）
    totalSuccessCount: 1
  scorers:
    - type: anti-hallucination  # 幻覚検出スコアラー
      weight: 1.0
```

---

## Template 5: 大規模ドキュメントテスト

```yaml
- id: "scale-large-001"
  name: "大規模ドキュメントの全置換"
  userMessage: "「ターゲット」を「置換後」に置換してください"
  pages:
    - id: "00000000-0000-0000-0000-000000000001"
      title: "大規模ドキュメント"
      blocks:
        # 30+ブロック、20+出現
        - id: "block-001"
          type: "heading"
          content:
            - type: "text"
              text: "1. ターゲットについて"
          children: []
        - id: "block-002"
          type: "paragraph"
          content:
            - type: "text"
              text: "ターゲットの定義..."
          children: []
        # ... 中略 ...
        - id: "block-030"
          type: "paragraph"
          content:
            - type: "text"
              text: "最後のターゲット参照。"
          children: []
      version: 1
  expected:
    operations:
      - pageId: "00000000-0000-0000-0000-000000000001"
        operations:
          # 全てのターゲットを含むブロックに対する操作
          - type: "replace"
            targetBlockId: "block-001"
            expectedContentPatterns:
              - "置換後"
          # ... 他のブロック ...
    totalSuccessCount: 1
```

---

## Template 6: 変更不要テスト

```yaml
- id: "no-change-001"
  name: "変更不要なリクエスト"
  userMessage: "「存在しないテキスト」を置換してください"
  pages:
    - id: "00000000-0000-0000-0000-000000000001"
      title: "変更なしテスト"
      blocks:
        - id: "block-001"
          type: "paragraph"
          content:
            - type: "text"
              text: "このテキストには対象がありません。"
          children: []
      version: 1
  expected:
    operations: []  # 操作なし
    totalSuccessCount: 0
```

---

## Template 7: 複数ページテスト

```yaml
- id: "multi-page-001"
  name: "複数ページへの一括置換"
  userMessage: "すべてのページの「共通」を「一般」に置換してください"
  pages:
    - id: "00000000-0000-0000-0000-000000000001"
      title: "ページ1"
      blocks:
        - id: "block-001"
          type: "paragraph"
          content:
            - type: "text"
              text: "共通の内容です。"
          children: []
      version: 1
    - id: "00000000-0000-0000-0000-000000000002"
      title: "ページ2"
      blocks:
        - id: "block-002"
          type: "paragraph"
          content:
            - type: "text"
              text: "こちらも共通です。"
          children: []
      version: 1
  expected:
    operations:
      - pageId: "00000000-0000-0000-0000-000000000001"
        operations:
          - type: "replace"
            targetBlockId: "block-001"
            expectedContentPatterns:
              - "一般"
      - pageId: "00000000-0000-0000-0000-000000000002"
        operations:
          - type: "replace"
            targetBlockId: "block-002"
            expectedContentPatterns:
              - "一般"
    totalSuccessCount: 2
```

---

## ID命名規則

```
<category>-<subcategory>-<number>

categories:
  - basic          # 基本操作
  - replace        # 置換系
  - insert         # 挿入系
  - delete         # 削除系
  - multi-page     # 複数ページ
  - edge           # エッジケース
  - scale          # 規模テスト
  - generalization # 汎化テスト
  - anti-hallucination  # 幻覚防止

examples:
  - replace-basic-001
  - generalization-kanji-001
  - scale-large-001
  - edge-empty-001
```
