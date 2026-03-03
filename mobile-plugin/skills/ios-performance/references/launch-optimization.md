# 起動時間最適化詳細

## 起動フェーズの理解

### Cold Launch

```
1. Kernel (OS)
   ↓ プロセス生成
2. dyld (Dynamic Linker)
   ↓ ライブラリ読み込み
3. libSystem
   ↓ ランタイム初期化
4. Runtime (+load, static initializers)
   ↓ クラス初期化
5. UIKit
   ↓ AppDelegate/SceneDelegate
6. Application Code
   ↓ 初期化処理
7. First Frame
   → 画面表示
```

### Warm Launch

```
プロセスは生存しているがバックグラウンドから復帰
- メモリ状態は保持
- UIの再構築が必要
- applicationWillEnterForeground から開始
```

### Resume

```
アプリがバックグラウンドから即座に復帰
- 状態が完全に保持
- 再描画のみ
```

## 起動時間の計測

### os_signpost による計測

```swift
import os.signpost

let log = OSLog(subsystem: "com.myapp", category: "Launch")

// AppDelegate
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    os_signpost(.begin, log: log, name: "AppLaunch")
    
    // 初期化処理
    
    DispatchQueue.main.async {
        os_signpost(.end, log: log, name: "AppLaunch")
    }
    
    return true
}
```

### 自前の計測

```swift
class LaunchTimer {
    static let shared = LaunchTimer()
    
    private var startTime: CFAbsoluteTime = 0
    private var milestones: [(name: String, time: CFAbsoluteTime)] = []
    
    private init() {
        // プロセス起動時刻を取得
        var kinfo = kinfo_proc()
        var size = MemoryLayout<kinfo_proc>.stride
        var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid()]
        sysctl(&mib, u_int(mib.count), &kinfo, &size, nil, 0)
        
        let startSec = kinfo.kp_proc.p_starttime.tv_sec
        let startUsec = kinfo.kp_proc.p_starttime.tv_usec
        startTime = CFAbsoluteTime(startSec) + CFAbsoluteTime(startUsec) / 1_000_000
    }
    
    func mark(_ name: String) {
        milestones.append((name, CFAbsoluteTimeGetCurrent()))
    }
    
    func report() {
        print("=== Launch Time Report ===")
        var previousTime = startTime
        
        for (name, time) in milestones {
            let delta = (time - previousTime) * 1000
            let total = (time - startTime) * 1000
            print("\(name): +\(String(format: "%.2f", delta))ms (total: \(String(format: "%.2f", total))ms)")
            previousTime = time
        }
    }
}

// 使用
// AppDelegate
func application(_ application: UIApplication, didFinishLaunchingWithOptions...) {
    LaunchTimer.shared.mark("didFinishLaunching start")
    
    setupCore()
    LaunchTimer.shared.mark("Core setup done")
    
    setupUI()
    LaunchTimer.shared.mark("UI setup done")
    
    DispatchQueue.main.async {
        LaunchTimer.shared.mark("First frame")
        LaunchTimer.shared.report()
    }
    
    return true
}
```

## dyld フェーズの最適化

### ライブラリの削減

```
確認方法:
1. Build Settings → Other Linker Flags → -Wl,-map,path/to/map.txt
2. map ファイルでリンクされているライブラリを確認

削減策:
- 未使用のフレームワークを削除
- 静的ライブラリへの置き換え検討
- 依存関係の整理
```

### +load メソッドの回避

```swift
// Bad: +load は起動時に実行される
@objc class LegacyClass: NSObject {
    override class func load() {
        // この処理は起動時に実行される
        registerSomething()
    }
}

// Good: 必要時に初期化
class ModernClass {
    static let shared = ModernClass()
    
    private init() {
        registerSomething()
    }
}
```

### 静的初期化子の回避

```swift
// Bad: グローバル変数の重い初期化
let heavyFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.locale = Locale(identifier: "ja_JP")
    formatter.dateFormat = "yyyy年MM月dd日 HH:mm:ss"
    return formatter
}()

// Good: lazy initialization
class Formatters {
    static let shared = Formatters()
    
    private var _dateFormatter: DateFormatter?
    
    var dateFormatter: DateFormatter {
        if _dateFormatter == nil {
            let formatter = DateFormatter()
            formatter.locale = Locale(identifier: "ja_JP")
            formatter.dateFormat = "yyyy年MM月dd日 HH:mm:ss"
            _dateFormatter = formatter
        }
        return _dateFormatter!
    }
}
```

## Application フェーズの最適化

### 必須処理と非必須処理の分離

```swift
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    
    // 必須: 起動に必要な最小限の処理
    setupCrashReporting()
    setupCoreData()
    setupRootViewController()
    
    // 非必須: バックグラウンドで実行
    DispatchQueue.global(qos: .utility).async {
        self.setupAnalytics()
        self.preloadCaches()
        self.warmUpNetworking()
    }
    
    // 遅延: アイドル時に実行
    DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
        self.setupNonCriticalServices()
    }
    
    return true
}
```

### 画面表示の優先

```swift
func setupRootViewController() {
    // 軽量なプレースホルダー画面を先に表示
    let loadingVC = LoadingViewController()
    window?.rootViewController = loadingVC
    window?.makeKeyAndVisible()
    
    // 本来の画面を非同期で構築
    DispatchQueue.main.async {
        let mainVC = self.buildMainViewController()
        self.window?.rootViewController = mainVC
    }
}
```

### 依存関係の管理

```swift
// 依存関係を明確にした初期化
class AppInitializer {
    func initialize() async {
        // Phase 1: 独立した初期化（並列実行可能）
        async let configLoaded = loadConfiguration()
        async let databaseReady = setupDatabase()
        async let networkReady = setupNetworking()
        
        let (_, _, _) = await (configLoaded, databaseReady, networkReady)
        
        // Phase 2: Phase 1 に依存する初期化
        await setupUserSession()
        
        // Phase 3: UI 表示
        await MainActor.run {
            showMainScreen()
        }
    }
}
```

## First Frame の最適化

### レイアウト計算の軽量化

```swift
// Bad: 複雑な Auto Layout
// 制約が多すぎると初期レイアウトに時間がかかる

// Good: 固定サイズの活用
view.frame = CGRect(x: 0, y: 0, width: UIScreen.main.bounds.width, height: 100)

// または、優先度の設定
constraint.priority = .defaultHigh  // required ではなく
```

### 初期画面のシンプル化

```swift
// スプラッシュスクリーンと同じデザインの初期画面
class InitialViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // LaunchScreen.storyboard と同じ見た目
        view.backgroundColor = .systemBackground
        
        let logoImageView = UIImageView(image: UIImage(named: "logo"))
        logoImageView.center = view.center
        view.addSubview(logoImageView)
    }
}
```

## Pre-warming の活用

### バックグラウンドでのプリロード

```swift
class PrewarmingManager {
    static let shared = PrewarmingManager()
    
    func prewarm() {
        DispatchQueue.global(qos: .background).async {
            // ネットワークセッションのウォームアップ
            URLSession.shared.dataTask(with: URL(string: "https://api.example.com/health")!) { _, _, _ in }.resume()
            
            // 画像キャッシュのプリロード
            ImageCache.shared.preload(urls: self.frequentlyUsedImageURLs)
            
            // フォントのプリロード
            _ = UIFont.systemFont(ofSize: 16)
            _ = UIFont.boldSystemFont(ofSize: 16)
        }
    }
    
    private var frequentlyUsedImageURLs: [URL] {
        // よく使う画像のURL
        []
    }
}
```

### Scene Delegate での Warm Launch 最適化

```swift
func sceneWillEnterForeground(_ scene: UIScene) {
    // Warm Launch 時の処理
    
    // 最小限のデータ更新
    DataManager.shared.refreshIfNeeded()
    
    // UI の更新は遅延
    DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
        self.updateUI()
    }
}
```

## 起動時間のベンチマーク

### 目標値

```
Cold Launch (iPhone 最新モデル):
- 目標: < 400ms
- 許容: < 1s
- 問題: > 2s

Warm Launch:
- 目標: < 200ms
- 許容: < 500ms

Resume:
- 目標: 即時
```

### デバイス別の考慮

```
最低スペックのサポートデバイスで計測することが重要

例:
- iPhone SE (2nd gen) / iPhone 8
- 最低サポート iOS バージョン
- ストレージ残量が少ない状態
```

## トラブルシューティング

### 問題1: dyld フェーズが長い

```
原因:
- 多すぎるダイナミックライブラリ
- 静的初期化子

対策:
- フレームワークの統合
- 静的リンクへの変更
- +load の削除
```

### 問題2: didFinishLaunching が長い

```
原因:
- 同期的なデータ読み込み
- 重い初期化処理

対策:
- 非同期化
- 遅延初期化
- 処理の分割
```

### 問題3: First Frame が遅い

```
原因:
- 複雑なレイアウト
- 大きな画像の読み込み

対策:
- シンプルな初期画面
- 画像の最適化
- プレースホルダーの使用
```

## Instruments: App Launch

### 使い方

```
1. Product → Profile (Cmd + I)
2. App Launch テンプレートを選択
3. アプリを終了
4. Record 開始
5. 自動的に起動して計測
6. 各フェーズの時間を確認
```

### 確認ポイント

```
Process Initialization:
- dyld の時間
- Runtime 初期化

UIKit Initialization:
- AppDelegate 初期化
- SceneDelegate 初期化

Initial Frame Rendering:
- レイアウト計算
- 描画処理
```

## チェックリスト

### dyld フェーズ

- [ ] 未使用のフレームワークを削除
- [ ] +load メソッドを使用していないか確認
- [ ] 静的初期化子を遅延初期化に変更
- [ ] リンクされているライブラリを確認

### Application フェーズ

- [ ] 必須/非必須処理を分類
- [ ] 非必須処理をバックグラウンドへ
- [ ] 依存関係を整理
- [ ] 同期処理を非同期化

### First Frame

- [ ] 初期画面をシンプルに
- [ ] 複雑なレイアウトを避ける
- [ ] プレースホルダーを活用
- [ ] 重い処理を遅延

### 計測

- [ ] 実機で計測
- [ ] 最低スペックデバイスで確認
- [ ] Instruments: App Launch で分析
- [ ] ベースラインを記録
