# xcconfig 活用ガイド

## 概要

xcconfig（Xcode Configuration Files）は、Xcodeプロジェクトのビルド設定を外部ファイルで管理するための仕組み。以下のメリットがある:

- ビルド設定のバージョン管理が容易
- 環境間での設定差分が明確
- 設定の再利用と継承が可能
- コードレビューでの設定変更確認が容易

## 基本構文

```xcconfig
// コメント
SETTING_NAME = value
SETTING_NAME = $(inherited) additional_value
SETTING_NAME[sdk=iphoneos*] = device_value
SETTING_NAME[config=Debug] = debug_value
```

## 推奨ディレクトリ構成

```
Configurations/
├── Base.xcconfig           # 全構成共通の基本設定
├── Debug.xcconfig          # Debug構成固有の設定
├── Release.xcconfig        # Release構成固有の設定
├── Signing/
│   ├── Debug.xcconfig      # Debug署名設定
│   └── Release.xcconfig    # Release署名設定
├── Targets/
│   ├── App.xcconfig        # メインアプリTarget
│   ├── AppTests.xcconfig   # テストTarget
│   └── Framework.xcconfig  # Framework Target
└── Environment/
    ├── Development.xcconfig
    ├── Staging.xcconfig
    └── Production.xcconfig
```

## 設定ファイル例

### Base.xcconfig

```xcconfig
// Base.xcconfig
// 全構成で共通の設定

// Swift
SWIFT_VERSION = 5.9
SWIFT_STRICT_CONCURRENCY = complete

// Deployment
IPHONEOS_DEPLOYMENT_TARGET = 15.0
MACOSX_DEPLOYMENT_TARGET = 12.0

// Localization
INFOPLIST_KEY_CFBundleDisplayName = $(PRODUCT_NAME)
GENERATE_INFOPLIST_FILE = YES

// Warnings
GCC_WARN_ABOUT_DEPRECATED_FUNCTIONS = YES
CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES
CLANG_WARN_INFINITE_RECURSION = YES
CLANG_WARN_SUSPICIOUS_MOVE = YES

// Static Analysis
CLANG_ANALYZER_LOCALIZABILITY_NONLOCALIZED = YES

// Asset Catalog
ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon
ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES
```

### Debug.xcconfig

```xcconfig
// Debug.xcconfig
#include "Base.xcconfig"

// Optimization
SWIFT_OPTIMIZATION_LEVEL = -Onone
GCC_OPTIMIZATION_LEVEL = 0
SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG

// Debug Information
DEBUG_INFORMATION_FORMAT = dwarf
ENABLE_TESTABILITY = YES
ONLY_ACTIVE_ARCH = YES

// Preprocessor
GCC_PREPROCESSOR_DEFINITIONS = $(inherited) DEBUG=1

// Signing (開発用)
#include "Signing/Debug.xcconfig"
```

### Release.xcconfig

```xcconfig
// Release.xcconfig
#include "Base.xcconfig"

// Optimization
SWIFT_OPTIMIZATION_LEVEL = -O
GCC_OPTIMIZATION_LEVEL = s
SWIFT_COMPILATION_MODE = wholemodule

// Debug Information
DEBUG_INFORMATION_FORMAT = dwarf-with-dsym
ENABLE_TESTABILITY = NO

// Strip
STRIP_INSTALLED_PRODUCT = YES
STRIP_SWIFT_SYMBOLS = YES
COPY_PHASE_STRIP = YES

// Bitcode (iOS 16以降不要だが念のため)
ENABLE_BITCODE = NO

// Signing (配布用)
#include "Signing/Release.xcconfig"
```

### Signing/Debug.xcconfig

```xcconfig
// Signing/Debug.xcconfig
// 開発用署名設定

CODE_SIGN_STYLE = Automatic
DEVELOPMENT_TEAM = XXXXXXXXXX

// Development証明書を使用
CODE_SIGN_IDENTITY = Apple Development
```

### Signing/Release.xcconfig

```xcconfig
// Signing/Release.xcconfig
// 配布用署名設定

CODE_SIGN_STYLE = Manual
DEVELOPMENT_TEAM = XXXXXXXXXX

// Distribution証明書を使用
CODE_SIGN_IDENTITY = Apple Distribution

// Provisioning Profile
PROVISIONING_PROFILE_SPECIFIER = AppStore_Profile_Name
```

## 条件付き設定

### SDK別設定

```xcconfig
// シミュレータとデバイスで異なる設定
EXCLUDED_ARCHS[sdk=iphonesimulator*] = arm64
ONLY_ACTIVE_ARCH[sdk=iphonesimulator*] = YES
```

### アーキテクチャ別設定

```xcconfig
// ARM64専用の設定
OTHER_SWIFT_FLAGS[arch=arm64] = -D ARM64
```

### 構成別設定

```xcconfig
// Debug構成でのみ有効
SWIFT_ACTIVE_COMPILATION_CONDITIONS[config=Debug] = $(inherited) PREVIEW_ENABLED
```

## 変数と継承

### $(inherited) の使用

```xcconfig
// 親設定を継承しつつ追加
OTHER_LDFLAGS = $(inherited) -lz -lsqlite3
OTHER_SWIFT_FLAGS = $(inherited) -D CUSTOM_FLAG
```

### カスタム変数

```xcconfig
// カスタム変数定義
MY_API_BASE_URL = https://api.example.com

// 他の設定で参照
OTHER_SWIFT_FLAGS = $(inherited) -D API_BASE_URL=\"$(MY_API_BASE_URL)\"
```

### 環境変数の参照

```xcconfig
// 環境変数を参照
DEVELOPMENT_TEAM = $(TEAM_ID)
API_KEY = $(APP_API_KEY)
```

## Xcodeプロジェクトへの適用

### 手順

1. **Project Navigator でプロジェクトを選択**
2. **PROJECT > Info タブを開く**
3. **Configurations セクションで構成を展開**
4. **各Target/Projectのドロップダウンで xcconfig を選択**

### 構成例

```
├─ Debug
│   ├─ Project: Debug.xcconfig
│   ├─ App Target: Targets/App.xcconfig
│   └─ Tests Target: Targets/AppTests.xcconfig
└─ Release
    ├─ Project: Release.xcconfig
    ├─ App Target: Targets/App.xcconfig
    └─ Tests Target: Targets/AppTests.xcconfig
```

## CocoaPods との共存

CocoaPodsを使用している場合、Pods が生成する xcconfig を include する必要がある:

```xcconfig
// Debug.xcconfig
#include "Base.xcconfig"
#include "Pods/Target Support Files/Pods-App/Pods-App.debug.xcconfig"

// 自プロジェクトの設定
SWIFT_OPTIMIZATION_LEVEL = -Onone
```

**重要**: `pod install` 実行後、Pods の xcconfig パスが変わる可能性があるため注意。

## トラブルシューティング

### 設定が反映されない

1. **Build Settings で確認**
   - Resolved 列で実際に適用される値を確認
   - Level 別の値を確認（Project / Target / xcconfig）

2. **$(inherited) の確認**
   - 継承が必要な設定で $(inherited) を使用しているか

3. **include パスの確認**
   - 相対パスが正しいか確認

### 設定の優先順位

1. コマンドライン引数（最高）
2. Target Build Settings
3. Target xcconfig
4. Project Build Settings
5. Project xcconfig
6. Xcode デフォルト値（最低）

## ベストプラクティス

1. **すべてのビルド設定を xcconfig で管理**
   - Xcode GUI での直接変更を避ける

2. **機密情報は環境変数から取得**
   - API キーやチームIDを直接記述しない

3. **明確な命名規則**
   - 設定ファイルの役割が名前から分かるように

4. **コメントで意図を記述**
   - なぜその設定が必要かを記載

5. **バージョン管理**
   - すべての xcconfig を Git 管理下に
   - ただし機密情報を含むファイルは .gitignore に追加
