---
name: app-idea-workshop
context: fork
description: Web/モバイルアプリのアイデアを共創型インタビューで具体化し、開発用ドキュメント一式を生成するスキル。「アプリのアイデアがある」「新しいサービスを考えたい」「仕様を固めたい」「アプリ開発の相談」と言った時に使用する。アイデア段階から開発着手可能なドキュメントまで一貫してサポート。
---

# App Idea Workshop

共創型インタビューでアプリアイデアを具体化し、開発用ドキュメント一式を生成する。

## ワークフロー概要

```
1. ビジョン探索 → 2. 共創的深掘り → 3. 機能定義 → 4. 検証 → 5. ドキュメント生成
```

## Phase 1: ビジョン探索

課題・緊急性・既存代替手段の不満点・成功像を明確化する。質問トピックは references/questions.md を参照。

## Phase 2: 共創的深掘り（発散→収束）

ユーザーの初期アイデアに複数の切り口を提示して発散させ、ターゲットユーザーと差別化ポイントを絞り込んで収束させる。

## Phase 3: 機能定義

コア機能（3つ以内）、MVP範囲、将来機能（Phase 2以降）、非機能要件を確定する。質問トピックは references/questions.md を参照。

## Phase 4: 批判的検証

差別化の十分性、技術的実現可能性、継続利用理由、ビジネスモデルの成立性を厳しい視点で検証する。

## Phase 5: ドキュメント生成

インタビュー内容を基に、開発用ドキュメント一式を生成する。

### 出力ディレクトリ構成

```
docs/
├── 01_product_overview.md      # プロダクト概要書
├── 02_user_stories.md          # ユーザーストーリー一覧
├── 03_functional_spec.md       # 機能仕様書
├── 04_screen_flow.md           # 画面遷移図
├── 05_non_functional_req.md    # 非機能要件
├── 06_competitive_analysis.md  # 競合分析
├── 07_risks_assumptions.md     # リスク・前提条件
└── 08_roadmap.md               # ロードマップ
```

### ドキュメント生成手順

1. ユーザーに出力先ディレクトリを確認（デフォルト: `./docs/`）
2. 各テンプレート（[assets/](assets/)）を使用してドキュメント生成
3. 生成後、ユーザーに確認・修正の機会を提供

**テンプレート参照**:
- [assets/01_product_overview.md](assets/01_product_overview.md)
- [assets/02_user_stories.md](assets/02_user_stories.md)
- [assets/03_functional_spec.md](assets/03_functional_spec.md)
- [assets/04_screen_flow.md](assets/04_screen_flow.md)
- [assets/05_non_functional_req.md](assets/05_non_functional_req.md)
- [assets/06_competitive_analysis.md](assets/06_competitive_analysis.md)
- [assets/07_risks_assumptions.md](assets/07_risks_assumptions.md)
- [assets/08_roadmap.md](assets/08_roadmap.md)

### トレーサビリティ規則

03_functional_spec.md の機能ID（F-001, F-002, ...）は 02_user_stories.md のユーザーストーリーID（US-001, US-002, ...）を必ず参照する。08_roadmap.md の各機能も同じUS-IDで紐づける。ID追加・変更時は3ファイル間の整合を保つ。

## 注意事項

- ドキュメント生成前に必ずユーザー確認を取る
- 技術的判断は参考情報として提示し、最終判断はユーザーに委ねる
- 競合分析は公開情報に基づく推測であることを明記
