# Swift Package Manager (SPM) 活用ガイド

## 概要

Swift Package Manager は Apple 公式の依存関係管理ツール。Xcode と完全に統合されており、以下のメリットがある:

- Xcode との完全な統合（追加ツール不要）
- クロスプラットフォーム対応
- ビルドシステムとの直接連携
- Apple のサポートと継続的な改善

## 依存関係の追加

### Xcode GUI から追加

1. **File > Add Package Dependencies...**
2. **パッケージ URL を入力**
   ```
   https://github.com/Alamofire/Alamofire
   ```
3. **バージョンルールを選択**
   - Up to Next Major Version（推奨）
   - Up to Next Minor Version
   - Exact Version
   - Branch
   - Commit
4. **追加する Target を選択**

### Package.swift で管理（Package製品の場合）

```swift
// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "MyPackage",
    platforms: [
        .iOS(.v15),
        .macOS(.v12)
    ],
    products: [
        .library(
            name: "MyPackage",
            targets: ["MyPackage"]
        )
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire", from: "5.8.0"),
        .package(url: "https://github.com/realm/realm-swift", exact: "10.45.0"),
        .package(url: "https://github.com/pointfreeco/swift-composable-architecture", .upToNextMajor(from: "1.0.0")),
    ],
    targets: [
        .target(
            name: "MyPackage",
            dependencies: [
                "Alamofire",
                .product(name: "RealmSwift", package: "realm-swift"),
                .product(name: "ComposableArchitecture", package: "swift-composable-architecture"),
            ]
        ),
        .testTarget(
            name: "MyPackageTests",
            dependencies: ["MyPackage"]
        )
    ]
)
```

## ローカルパッケージの作成

### 新規パッケージ作成

```bash
# パッケージディレクトリ作成
mkdir MyLocalPackage
cd MyLocalPackage

# パッケージ初期化
swift package init --type library
```

### 生成される構造

```
MyLocalPackage/
├── Package.swift
├── Sources/
│   └── MyLocalPackage/
│       └── MyLocalPackage.swift
└── Tests/
    └── MyLocalPackageTests/
        └── MyLocalPackageTests.swift
```

### プロジェクトへの追加

1. **File > Add Package Dependencies...**
2. **Add Local...** をクリック
3. **パッケージディレクトリを選択**

または、パッケージフォルダを Xcode プロジェクトにドラッグ&ドロップ。

## CocoaPods からの移行

### 移行手順

1. **SPM対応状況の確認**
   - 各ライブラリの GitHub/README で SPM サポートを確認
   - [Swift Package Index](https://swiftpackageindex.com/) で検索

2. **段階的な移行**
   ```ruby
   # Podfile
   # 移行前
   pod 'Alamofire', '~> 5.8'
   pod 'Kingfisher', '~> 7.0'
   pod 'SnapKit', '~> 5.0'

   # 移行中（SPM未対応のみ残す）
   # pod 'Alamofire'  # SPMに移行済み
   pod 'SomeOldLibrary'  # SPM未対応
   ```

3. **SPMで依存追加**
   - Xcode > File > Add Package Dependencies...

4. **Podfile 更新と pod install**

5. **ビルド確認**

### よくある移行問題

| 問題 | 解決方法 |
|------|----------|
| 重複シンボル | CocoaPods 版を完全に削除してから SPM 追加 |
| モジュール名の違い | import 文を更新（例: `import Kingfisher` → `import Kingfisher`） |
| バイナリ配布のみ | CocoaPods を継続使用、または .binaryTarget で対応 |

## バージョン管理

### バージョン指定方法

```swift
// 推奨: セマンティックバージョニングに従う
.package(url: "...", from: "1.0.0")           // >= 1.0.0, < 2.0.0
.package(url: "...", "1.0.0"..<"2.0.0")       // 明示的な範囲
.package(url: "...", .upToNextMinor(from: "1.0.0"))  // >= 1.0.0, < 1.1.0

// 特定バージョン固定（非推奨、セキュリティ更新が適用されない）
.package(url: "...", exact: "1.0.0")

// ブランチ指定（開発時のみ）
.package(url: "...", branch: "main")

// コミット指定（特殊なケースのみ）
.package(url: "...", revision: "abc123")
```

### Package.resolved

SPM は依存関係の解決結果を `Package.resolved` に保存する:

```json
{
  "pins": [
    {
      "identity": "alamofire",
      "kind": "remoteSourceControl",
      "location": "https://github.com/Alamofire/Alamofire",
      "state": {
        "revision": "f455c2975c4c3b...",
        "version": "5.8.1"
      }
    }
  ]
}
```

**推奨**: `Package.resolved` を Git にコミットし、チーム全体で同じバージョンを使用。

### バージョン更新

```bash
# 特定パッケージを更新
swift package update Alamofire

# すべてのパッケージを更新
swift package update
```

Xcode から: File > Packages > Update to Latest Package Versions

## プライベートリポジトリ

### SSH 認証

1. **SSH キーの設定**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ssh-add ~/.ssh/id_ed25519
   ```

2. **リポジトリ URL**
   ```swift
   .package(url: "git@github.com:myorg/private-package.git", from: "1.0.0")
   ```

### HTTPS + Credential

```bash
# Git Credential Helper を設定
git config --global credential.helper osxkeychain
```

## CI/CD での SPM

### GitHub Actions

```yaml
- name: Resolve Swift Packages
  run: xcodebuild -resolvePackageDependencies -project MyApp.xcodeproj

- name: Build
  run: xcodebuild build -project MyApp.xcodeproj -scheme MyApp
```

### パッケージキャッシュ

```yaml
- uses: actions/cache@v3
  with:
    path: |
      ~/Library/Developer/Xcode/DerivedData
      .build
    key: ${{ runner.os }}-spm-${{ hashFiles('**/Package.resolved') }}
```

## トラブルシューティング

### パッケージ解決エラー

```bash
# キャッシュクリア
rm -rf ~/Library/Caches/org.swift.swiftpm
rm -rf ~/Library/Developer/Xcode/DerivedData

# Xcode で再解決
# File > Packages > Reset Package Caches
```

### バージョン競合

```
Package 'A' requires 'B' 1.0.0
Package 'C' requires 'B' 2.0.0
```

**解決方法**:
1. 依存元パッケージのバージョンを調整
2. 共通のバージョン範囲を見つける
3. 必要に応じて fork して修正

### ビルド時間の最適化

```swift
// Package.swift
targets: [
    .target(
        name: "MyTarget",
        dependencies: [...],
        // 未使用のリソースを除外
        exclude: ["Resources/unused"],
        // ビルド設定
        swiftSettings: [
            .enableUpcomingFeature("StrictConcurrency")
        ]
    )
]
```

## ベストプラクティス

1. **セマンティックバージョニングを活用**
   - `from:` を使用し、自動的にパッチ更新を受ける

2. **Package.resolved を Git 管理**
   - チーム全体で同じバージョンを使用

3. **定期的な更新**
   - セキュリティ更新のため月1回程度の更新を推奨

4. **ローカルパッケージで共通コードを分離**
   - マルチモジュール化でビルド時間短縮

5. **依存の最小化**
   - 必要最小限のパッケージのみ追加
   - 軽量な代替があれば検討

6. **バイナリ配布の活用**
   - 大きなパッケージは .binaryTarget でビルド時間短縮

## 参考リンク

- [Swift Package Manager Documentation](https://www.swift.org/package-manager/)
- [Swift Package Index](https://swiftpackageindex.com/)
- [Apple: Adding Package Dependencies](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
