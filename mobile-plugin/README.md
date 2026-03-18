# Mobile Plugin for Claude Code

モバイル開発（iOS/Android/Flutter）を支援するスキル・エージェントのコレクションです。mobile-mcp によるデバイス操作・UI自動化に加え、Swift/SwiftUI開発、Flutter/Riverpod UI設計、Xcodeプロジェクト管理、テスト・品質保証を提供します。

## 概要

このプラグインは、Swift/SwiftUI開発、Flutter/Riverpod UI設計、Xcodeプロジェクト管理、テスト・品質保証の領域でモバイル開発を包括的にサポートします。

## スキル一覧

### Swift/SwiftUI開発支援

| スキル | 説明 |
|--------|------|
| `swift-code-review` | Swiftコードの品質レビュー。Swift 6 Strict Concurrency、プロトコル指向、値型/参照型の使い分けをチェック |
| `swiftui-component` | SwiftUIコンポーネント設計支援。状態管理、View構造化、アクセシビリティ対応 |
| `swift-protocol` | プロトコル指向設計支援。Protocol拡張、関連型、依存性注入パターン |
| `swift-concurrency` | Swift Concurrency支援。async/await、Actor、Sendable、データ競合防止 |

### Flutter / Riverpod開発支援

| スキル | 説明 |
|--------|------|
| `flutter-widget-splitting` | Flutter Widget分割支援。巨大なbuild()の分割、共通化、Riverpodのwatch/read/listen/select境界整理 |

### Xcode/ビルド関連

| スキル | 説明 |
|--------|------|
| `xcode-project` | Xcodeプロジェクト設定支援。ビルド設定、Target/Scheme、SPM、xcconfig活用 |
| `ios-signing` | コード署名・プロビジョニング支援。証明書、Provisioning Profile、CI/CD環境設定 |
| `ios-archive` | アーカイブ・配布支援。App Store Connect、TestFlight、Ad Hoc/Enterprise配布 |

### テスト・品質保証

| スキル | 説明 |
|--------|------|
| `ios-test-design` | XCTest/UITest設計支援。テスト戦略、モック設計、カバレッジ分析 |
| `ios-snapshot-test` | スナップショットテスト支援。swift-snapshot-testing、UI変更検出 |
| `ios-performance` | パフォーマンス最適化。Instruments、メモリ/CPU分析、起動時間最適化 |

### デザイン・UI/UX

| スキル | 説明 |
|--------|------|
| `ios-design-direction` | デザイン哲学・クリエイティブディレクション。Apple HIG、SwiftUI実装、アクセシビリティ、マルチプラットフォーム対応 |
| `ios-ia-navigation` | 情報設計（IA）と画面遷移設計。タブ/push/modal選定、iPad適応、ディープリンク、状態保持ポリシー |

### デバッグ・自動化

| スキル | 説明 |
|--------|------|
| `ios-simulator-debug` | SimulatorをAIで操作してデバッグ。ビルド→起動→UI操作→スクショ→分析のループ |

## MCP Server

このプラグインは以下のMCPサーバーを自動で有効化します：

| サーバー | 説明 |
|----------|------|
| `mobile-mcp` | モバイルデバイス操作（iOS/Android対応、UI操作、スクショ、アプリ管理） |

## エージェント一覧

| エージェント | 説明 | 使用タイミング |
|-------------|------|----------------|
| `ios-architecture-advisor` | iOSアーキテクチャ設計支援 | 新規プロジェクト設計、アーキテクチャリファクタリング時 |
| `swift-code-analyzer` | Swiftコード品質分析 | コードレビュー、リファクタリング前の分析時 |

## 使い方

```bash
# スキルの実行
/swift-code-review         # Swiftコードをレビュー
/swiftui-component         # SwiftUIコンポーネントを設計
/flutter-widget-splitting  # Flutter Widgetを責務とRiverpod境界で分割
/ios-test-design           # テスト設計を支援
/xcode-project             # Xcodeプロジェクト設定を支援
/ios-design-direction      # デザイン哲学とHIG準拠を支援
/ios-ia-navigation         # 情報設計と画面遷移を設計

# エージェントの利用
「iOSのアーキテクチャを相談したい」  # ios-architecture-advisor
「Swiftコードを分析して」            # swift-code-analyzer
```

## 対応バージョン

- **Swift**: 5.9+（Swift 6 Strict Concurrency対応）
- **iOS**: 15.0+（SwiftUI重視）、iOS 17+ の新機能対応
- **Xcode**: 15.0+
- **macOS/watchOS/tvOS**: 対応

## ディレクトリ構造

```
mobile-plugin/
├── skills/                    # スキルソース
│   ├── swift-code-review/     # Swift開発
│   ├── swiftui-component/
│   ├── swift-protocol/
│   ├── swift-concurrency/
│   ├── flutter-widget-splitting/
│   ├── xcode-project/         # Xcode/ビルド
│   ├── ios-signing/
│   ├── ios-archive/
│   ├── ios-test-design/       # テスト
│   ├── ios-snapshot-test/
│   ├── ios-performance/
│   ├── ios-design-direction/  # デザイン・UI/UX
│   ├── ios-ia-navigation/     # 情報設計・画面遷移
│   └── ios-simulator-debug/   # デバッグ・自動化
├── agents/                    # エージェント定義
│   ├── ios-architecture-advisor.md
│   └── swift-code-analyzer.md
├── hooks/                     # フック定義
├── commands/                  # コマンド定義
└── .claude-plugin/
    └── plugin.json           # プラグイン設定
```

## インストール

1. このリポジトリをクローン
2. Claude Codeの設定でpluginパスを追加

```json
{
  "plugins": [
    "/path/to/claude-marketplace/mobile-plugin"
  ]
}
```

## 設計思想

### 1. 現代的なSwift開発

- Swift 6のStrict Concurrencyを前提
- プロトコル指向設計を推奨
- 値セマンティクスを重視

### 2. SwiftUI First

- SwiftUIをメインUIフレームワークとして想定
- @Observable（iOS 17+）への移行を支援
- 状態管理のベストプラクティスを提供

### 3. テスト駆動

- XCTestベースのテスト戦略
- スナップショットテストによるUI検証
- パフォーマンステストの統合

### 4. Flutter UI Architecture

- 大きな `build()` を責務と再ビルド境界で分割
- Riverpod の `watch/read/listen/select` を役割ごとに分離
- 共有状態と一時 UI 状態を分け、過剰な Provider 化を避ける

## ライセンス

MIT License
