# Xcode Build Settings リファレンス

## 概要

Xcode のビルド設定は数百種類存在する。本ドキュメントでは特に重要な設定を分類して解説する。

## Swift コンパイラ設定

### SWIFT_VERSION

Swiftのバージョンを指定。

```xcconfig
SWIFT_VERSION = 5.9
```

| 値 | 説明 |
|---|---|
| 5.9 | Swift 5.9（最新、推奨） |
| 5.8 | Swift 5.8 |
| 5.7 | Swift 5.7 |

### SWIFT_OPTIMIZATION_LEVEL

Swift コードの最適化レベル。

```xcconfig
// Debug
SWIFT_OPTIMIZATION_LEVEL = -Onone

// Release
SWIFT_OPTIMIZATION_LEVEL = -O
```

| 値 | 説明 | 用途 |
|---|---|---|
| -Onone | 最適化なし | Debug |
| -O | 速度最適化 | Release |
| -Osize | サイズ最適化 | Release（アプリサイズ重視） |

### SWIFT_COMPILATION_MODE

コンパイルモード。

```xcconfig
// Debug
SWIFT_COMPILATION_MODE = incremental

// Release
SWIFT_COMPILATION_MODE = wholemodule
```

| 値 | 説明 |
|---|---|
| incremental | 増分ビルド（Debug向け） |
| wholemodule | モジュール全体最適化（Release向け） |

### SWIFT_STRICT_CONCURRENCY

Swift Concurrency の厳格性チェック。

```xcconfig
SWIFT_STRICT_CONCURRENCY = complete
```

| 値 | 説明 |
|---|---|
| minimal | 最小限のチェック |
| targeted | @Sendable 注釈付きのみチェック |
| complete | 完全なチェック（Swift 6 準備） |

### SWIFT_ACTIVE_COMPILATION_CONDITIONS

条件付きコンパイルフラグ。

```xcconfig
// Debug
SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG

// Release
SWIFT_ACTIVE_COMPILATION_CONDITIONS =
```

コードでの使用:
```swift
#if DEBUG
print("Debug mode")
#endif
```

## デプロイメント設定

### IPHONEOS_DEPLOYMENT_TARGET

サポートする最小 iOS バージョン。

```xcconfig
IPHONEOS_DEPLOYMENT_TARGET = 15.0
```

**考慮事項**:
- 古いバージョンをサポートするほどユーザー数は増加
- 新しい API が使用できなくなる
- メンテナンスコストが増加

### TARGETED_DEVICE_FAMILY

サポートするデバイスファミリー。

```xcconfig
TARGETED_DEVICE_FAMILY = 1,2
```

| 値 | デバイス |
|---|---|
| 1 | iPhone |
| 2 | iPad |
| 1,2 | iPhone + iPad（Universal） |
| 3 | Apple TV |
| 4 | Apple Watch |

## コード署名設定

### CODE_SIGN_STYLE

署名スタイル。

```xcconfig
// 開発時
CODE_SIGN_STYLE = Automatic

// リリース時
CODE_SIGN_STYLE = Manual
```

### DEVELOPMENT_TEAM

開発チームID（10文字の英数字）。

```xcconfig
DEVELOPMENT_TEAM = XXXXXXXXXX
```

### CODE_SIGN_IDENTITY

使用する証明書。

```xcconfig
// 開発
CODE_SIGN_IDENTITY = Apple Development

// 配布
CODE_SIGN_IDENTITY = Apple Distribution
```

### PROVISIONING_PROFILE_SPECIFIER

Provisioning Profile の指定（Manual 時）。

```xcconfig
PROVISIONING_PROFILE_SPECIFIER = MyApp_AppStore_Profile
```

## ビルド出力設定

### DEBUG_INFORMATION_FORMAT

デバッグ情報の形式。

```xcconfig
// Debug
DEBUG_INFORMATION_FORMAT = dwarf

// Release
DEBUG_INFORMATION_FORMAT = dwarf-with-dsym
```

| 値 | 説明 |
|---|---|
| dwarf | バイナリ内に埋め込み |
| dwarf-with-dsym | 別ファイル（dSYM）として出力 |

### ENABLE_TESTABILITY

テストからの private アクセス許可。

```xcconfig
// Debug
ENABLE_TESTABILITY = YES

// Release
ENABLE_TESTABILITY = NO
```

### ONLY_ACTIVE_ARCH

アクティブアーキテクチャのみビルド。

```xcconfig
// Debug（ビルド高速化）
ONLY_ACTIVE_ARCH = YES

// Release
ONLY_ACTIVE_ARCH = NO
```

## リンカ設定

### OTHER_LDFLAGS

追加のリンカフラグ。

```xcconfig
OTHER_LDFLAGS = $(inherited) -ObjC -lz
```

よく使うフラグ:
| フラグ | 説明 |
|---|---|
| -ObjC | Objective-C カテゴリの強制リンク |
| -all_load | すべてのシンボルを強制リンク |
| -lz | zlib ライブラリのリンク |
| -lsqlite3 | SQLite ライブラリのリンク |

### DEAD_CODE_STRIPPING

未使用コードの除去。

```xcconfig
DEAD_CODE_STRIPPING = YES
```

### STRIP_INSTALLED_PRODUCT

シンボル情報の除去。

```xcconfig
// Release
STRIP_INSTALLED_PRODUCT = YES
STRIP_SWIFT_SYMBOLS = YES
```

## 警告設定

### GCC_WARN_* / CLANG_WARN_*

コンパイラ警告の設定。

```xcconfig
// 推奨: 厳格な警告設定
GCC_WARN_ABOUT_DEPRECATED_FUNCTIONS = YES
GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR
GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE

CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES
CLANG_WARN_BOOL_CONVERSION = YES
CLANG_WARN_COMMA = YES
CLANG_WARN_CONSTANT_CONVERSION = YES
CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES
CLANG_WARN_EMPTY_BODY = YES
CLANG_WARN_ENUM_CONVERSION = YES
CLANG_WARN_INFINITE_RECURSION = YES
CLANG_WARN_INT_CONVERSION = YES
CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES
CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES
CLANG_WARN_OBJC_LITERAL_CONVERSION = YES
CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES
CLANG_WARN_RANGE_LOOP_ANALYSIS = YES
CLANG_WARN_STRICT_PROTOTYPES = YES
CLANG_WARN_SUSPICIOUS_MOVE = YES
CLANG_WARN_UNREACHABLE_CODE = YES
CLANG_WARN__DUPLICATE_METHOD_MATCH = YES
```

### GCC_TREAT_WARNINGS_AS_ERRORS

警告をエラーとして扱う。

```xcconfig
// CI環境で推奨
GCC_TREAT_WARNINGS_AS_ERRORS = YES
```

## 静的解析設定

### CLANG_ANALYZER_*

Clang Static Analyzer の設定。

```xcconfig
CLANG_ANALYZER_LOCALIZABILITY_NONLOCALIZED = YES
CLANG_ANALYZER_NONNULL = YES
CLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE
```

## アセット設定

### ASSETCATALOG_COMPILER_APPICON_NAME

App Icon の Asset 名。

```xcconfig
ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon
```

### ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS

Swift のアセットシンボル拡張を生成。

```xcconfig
ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES
```

## Info.plist 設定

### GENERATE_INFOPLIST_FILE

Info.plist の自動生成。

```xcconfig
GENERATE_INFOPLIST_FILE = YES
```

### INFOPLIST_KEY_*

Info.plist のキーを個別に設定。

```xcconfig
INFOPLIST_KEY_CFBundleDisplayName = MyApp
INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES
INFOPLIST_KEY_UILaunchScreen_Generation = YES
INFOPLIST_KEY_UISupportedInterfaceOrientations = UIInterfaceOrientationPortrait
```

## Framework 配布設定

### BUILD_LIBRARY_FOR_DISTRIBUTION

Framework の安定 ABI を有効化。

```xcconfig
BUILD_LIBRARY_FOR_DISTRIBUTION = YES
```

**注意**: これを有効にすると .swiftinterface ファイルが生成され、異なる Swift バージョン間での互換性が向上するが、ビルド時間が増加する。

## 環境別推奨設定

### Debug 構成

```xcconfig
// 最適化なし（デバッグ容易）
SWIFT_OPTIMIZATION_LEVEL = -Onone
GCC_OPTIMIZATION_LEVEL = 0

// 増分ビルド
SWIFT_COMPILATION_MODE = incremental
ONLY_ACTIVE_ARCH = YES

// デバッグ情報
DEBUG_INFORMATION_FORMAT = dwarf
ENABLE_TESTABILITY = YES

// 条件付きコンパイル
SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG
GCC_PREPROCESSOR_DEFINITIONS = $(inherited) DEBUG=1
```

### Release 構成

```xcconfig
// 最適化
SWIFT_OPTIMIZATION_LEVEL = -O
GCC_OPTIMIZATION_LEVEL = s
SWIFT_COMPILATION_MODE = wholemodule
ONLY_ACTIVE_ARCH = NO

// シンボル
DEBUG_INFORMATION_FORMAT = dwarf-with-dsym
ENABLE_TESTABILITY = NO

// ストリップ
STRIP_INSTALLED_PRODUCT = YES
STRIP_SWIFT_SYMBOLS = YES
DEAD_CODE_STRIPPING = YES

// Bitcode（iOS 16以降不要）
ENABLE_BITCODE = NO
```

## 参考リンク

- [Xcode Build Settings Reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
- [xcodeproj gem - Build Settings](https://www.rubydoc.info/gems/xcodeproj/Xcodeproj/Constants)
