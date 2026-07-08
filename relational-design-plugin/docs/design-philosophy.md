# 設計思想: Relational Design Trace

## 1. デザインは名辞から始めない

多くの design prompt は、次のような名辞から始まる。

- modern
- premium
- simple
- friendly
- minimal
- B2B SaaS
- dashboard
- landing page

これらは分類としては便利だが、デザイン判断の根拠としては弱い。なぜなら、同じ「premium」でも、文脈によって意味が違うからである。

- 価格の正当化が必要なのか
- 信頼性が不足しているのか
- 選別感を出したいのか
- 安っぽい競合と距離を取りたいのか
- ユーザーが単に派手な表現を嫌っているのか

Relational Design では、曖昧な形容詞をそのまま視覚表現へ変換しない。必ず関係へ展開する。

```text
名辞: premium
  -> possible relation:
     user-to-risk: 高額判断の失敗を避けたい
     business-to-user: 価格に対する納得を作りたい
     information-to-confidence: 根拠が少ないと不信が増える
     visual-to-behavior: 軽い表現は不安を増やす可能性がある
```

## 2. デザイン案は style variant ではなく hypothesis variant

悪い分岐は次のようなもの。

```text
A案: シンプル
B案: 高級感
C案: ポップ
```

良い分岐は次のようなもの。

```text
A案: trust-first
  仮説: ユーザーは不安が大きいため、行動より理解を優先する方が離脱を減らす。

B案: speed-first
  仮説: ユーザーはすでに行動意欲があるため、説明より即時行動を支える方が成果に近い。

C案: proof-first
  仮説: ユーザーは比較検討中であり、情緒的魅力より証拠密度を求めている。
```

スタイルは仮説の帰結であって、仮説そのものではない。

## 3. uncertainty を潰さない

Agent は、曖昧な brief を埋めたくなる。これは生成には便利だが、設計には危険である。

Relational Design では、unknown と assumption を必ず分ける。

```yaml
unknowns:
  - U-001: primary user is not specified
assumptions:
  - A-001:
      claim: primary user is a technical decision maker
      confidence: low
      isolated: true
```

低信頼の仮説に依存する design decision は、必ず撤回可能にする。

## 4. 批評は見た目ではなく関係に戻る

「弱い」「良くない」「もっと洗練」は批評ではない。Relational Design の批評は、以下へ戻す。

- ユーザーは次の行動を理解できるか
- 不可逆な行動の前に、十分な説明があるか
- 情報密度は安心を増やしているか、迷いを増やしているか
- 事業側の誘導は、ユーザー側の信頼を損なっていないか
- 視覚階層は、ユーザー状態に合っているか
- 実装上の妥協は、デザイン意図を壊していないか

## 5. デザインは一回限りで終わらせない

画面を作って終わりにすると、Agent は毎回似た判断をやり直す。良い成果物は、design system に戻す必要がある。

```text
artifact
  -> token
  -> component
  -> pattern
  -> copy rule
  -> interaction rule
```

Relational Design では、画面や UI の最終出力に加えて、再利用可能な構造を backflow する。

## 6. この plugin の人格

この plugin は、デザイナー風の言葉を増やすためのものではない。むしろ、見た目に逃げる前に、判断の根拠を明確にする。

```text
Do not start with style.
Start with relations.
Do not hide uncertainty.
Preserve dependency.
Make retraction possible.
Return artifacts to reusable structure.
```
