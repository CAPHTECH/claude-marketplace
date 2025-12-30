# Apple Platform Plugin for Claude Code

Apple Platform（iOS/macOS/watchOS/tvOS）開発を支援するスキル・エージェントのコレクションです。

## 概要

このプラグインは、Swift/SwiftUI開発、Xcodeプロジェクト管理、テスト・品質保証の3つの領域でiOS開発を包括的にサポートします。

## スキル一覧

### Swift/SwiftUI開発支援

| スキル | 説明 |
|--------|------|
| `swift-code-review` | Swiftコードの品質レビュー。Swift 6 Strict Concurrency、プロトコル指向、値型/参照型の使い分けをチェック |
| `swiftui-component` | SwiftUIコンポーネント設計支援。状態管理、View構造化、アクセシビリティ対応 |
| `swift-protocol` | プロトコル指向設計支援。Protocol拡張、関連型、依存性注入パターン |
| `swift-concurrency` | Swift Concurrency支援。async/await、Actor、Sendable、データ競合防止 |

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

### デバッグ・自動化

| スキル | 説明 |
|--------|------|
| `ios-simulator-debug` | SimulatorをAIで操作してデバッグ。ビルド→起動→UI操作→スクショ→分析のループ |

## MCP Server

このプラグインは以下のMCPサーバーを自動で有効化します：

| サーバー | 説明 |
|----------|------|
| `ios-simulator` | iOS Simulator操作（UI操作、スクショ、録画、アプリ管理） |

**前提条件**: `brew tap facebook/fb && brew install idb-companion`

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
/ios-test-design           # テスト設計を支援
/xcode-project             # Xcodeプロジェクト設定を支援
/ios-design-direction      # デザイン哲学とHIG準拠を支援

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
apple-platform-plugin/
├── skills/                    # スキルソース
│   ├── swift-code-review/     # Swift開発
│   ├── swiftui-component/
│   ├── swift-protocol/
│   ├── swift-concurrency/
│   ├── xcode-project/         # Xcode/ビルド
│   ├── ios-signing/
│   ├── ios-archive/
│   ├── ios-test-design/       # テスト
│   ├── ios-snapshot-test/
│   ├── ios-performance/
│   ├── ios-design-direction/  # デザイン・UI/UX
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
    "/path/to/claude-marketplace/apple-platform-plugin"
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

## ライセンス

MIT License
