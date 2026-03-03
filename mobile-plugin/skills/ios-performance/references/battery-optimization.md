# バッテリー最適化詳細

## バッテリー消費の要因

### 主要なエネルギー消費源

```
1. CPU処理
   - アルゴリズムの非効率
   - 不要なバックグラウンド処理
   - ポーリング

2. ネットワーク
   - 頻繁な通信
   - 非効率なデータ転送
   - セルラー通信

3. 位置情報
   - 高精度測位
   - 継続的な追跡
   - バックグラウンド更新

4. GPU
   - 複雑なアニメーション
   - 高フレームレート
   - オフスクリーンレンダリング

5. センサー
   - 加速度計
   - ジャイロスコープ
   - 気圧計
```

### エネルギー影響レベル

| 操作 | 影響 | 注意点 |
|-----|------|--------|
| GPS（高精度） | 非常に高い | 必要最小限に |
| セルラー通信 | 高い | WiFi優先 |
| Bluetooth スキャン | 中〜高 | 間隔を空ける |
| CPU（フルパワー） | 高い | バックグラウンド処理に注意 |
| 画面（最大輝度） | 高い | 自動調整を推奨 |
| WiFi 通信 | 中 | バッチ処理を推奨 |

## 位置情報の最適化

### 精度レベルの選択

```swift
import CoreLocation

class LocationManager: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    
    /// ナビゲーション用（最高精度、高消費）
    func startNavigationTracking() {
        manager.desiredAccuracy = kCLLocationAccuracyBestForNavigation
        manager.distanceFilter = 10  // 10m ごとに更新
        manager.startUpdatingLocation()
    }
    
    /// 近くのスポット表示用（中精度）
    func startNearbySearch() {
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        manager.distanceFilter = 100
        manager.startUpdatingLocation()
    }
    
    /// 都市レベルの位置用（低精度、低消費）
    func startCityLevelTracking() {
        manager.desiredAccuracy = kCLLocationAccuracyKilometer
        manager.startUpdatingLocation()
    }
    
    /// 大きな移動のみ検出（最低消費）
    func startSignificantLocationMonitoring() {
        manager.startMonitoringSignificantLocationChanges()
    }
    
    func stopAllTracking() {
        manager.stopUpdatingLocation()
        manager.stopMonitoringSignificantLocationChanges()
    }
}
```

### バックグラウンド位置情報

```swift
// Info.plist 設定
// UIBackgroundModes: location

class BackgroundLocationManager: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    
    func startBackgroundTracking() {
        manager.requestAlwaysAuthorization()
        
        // バックグラウンド更新を許可
        manager.allowsBackgroundLocationUpdates = true
        
        // バックグラウンドでの自動一時停止
        manager.pausesLocationUpdatesAutomatically = true
        
        // 省電力モード
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        manager.distanceFilter = 50
        
        manager.startUpdatingLocation()
    }
    
    // 用途に応じた activityType 設定
    func configureForFitness() {
        manager.activityType = .fitness  // ワークアウト追跡
    }
    
    func configureForNavigation() {
        manager.activityType = .automotiveNavigation  // カーナビ
    }
}
```

### ジオフェンス

```swift
// 継続的な位置追跡の代わりにジオフェンスを使用
class GeofenceManager: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    
    func monitorRegion(center: CLLocationCoordinate2D, radius: Double, identifier: String) {
        let region = CLCircularRegion(
            center: center,
            radius: radius,
            identifier: identifier
        )
        region.notifyOnEntry = true
        region.notifyOnExit = true
        
        manager.startMonitoring(for: region)
    }
    
    func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        // エリアに入った時の処理
    }
    
    func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion) {
        // エリアを出た時の処理
    }
}
```

## ネットワークの最適化

### バッチ処理

```swift
class NetworkBatchManager {
    private var pendingRequests: [NetworkRequest] = []
    private var batchTimer: Timer?
    private let batchInterval: TimeInterval = 5.0
    
    func enqueue(_ request: NetworkRequest) {
        pendingRequests.append(request)
        scheduleBatchExecution()
    }
    
    private func scheduleBatchExecution() {
        batchTimer?.invalidate()
        batchTimer = Timer.scheduledTimer(
            withTimeInterval: batchInterval,
            repeats: false
        ) { [weak self] _ in
            self?.executeBatch()
        }
    }
    
    private func executeBatch() {
        guard !pendingRequests.isEmpty else { return }
        
        let requests = pendingRequests
        pendingRequests = []
        
        // バッチリクエストを実行
        Task {
            await sendBatchRequest(requests)
        }
    }
}
```

### バックグラウンドダウンロード

```swift
class BackgroundDownloadManager: NSObject, URLSessionDownloadDelegate {
    private lazy var session: URLSession = {
        let config = URLSessionConfiguration.background(
            withIdentifier: "com.myapp.background-download"
        )
        config.isDiscretionary = true  // システムに最適なタイミングを任せる
        config.sessionSendsLaunchEvents = true
        return URLSession(configuration: config, delegate: self, delegateQueue: nil)
    }()
    
    func startDownload(url: URL) {
        let task = session.downloadTask(with: url)
        task.earliestBeginDate = Date().addingTimeInterval(60)  // 1分後以降
        task.countOfBytesClientExpectsToSend = 200  // 送信予定バイト数
        task.countOfBytesClientExpectsToReceive = 1024 * 1024  // 受信予定バイト数
        task.resume()
    }
    
    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, 
                    didFinishDownloadingTo location: URL) {
        // ダウンロード完了処理
    }
}
```

### ネットワーク状態の監視

```swift
import Network

class NetworkMonitor {
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "NetworkMonitor")
    
    var isWiFi: Bool = false
    var isCellular: Bool = false
    var isExpensive: Bool = false
    
    func start() {
        monitor.pathUpdateHandler = { [weak self] path in
            self?.isWiFi = path.usesInterfaceType(.wifi)
            self?.isCellular = path.usesInterfaceType(.cellular)
            self?.isExpensive = path.isExpensive
            
            // WiFi 時のみ大きなデータを転送
            if path.usesInterfaceType(.wifi) {
                self?.performLargeDataTransfer()
            }
        }
        monitor.start(queue: queue)
    }
    
    private func performLargeDataTransfer() {
        // WiFi 接続時のみ実行
    }
}
```

## バックグラウンド処理の最適化

### Background Tasks Framework (iOS 13+)

```swift
import BackgroundTasks

class BackgroundTaskManager {
    static let shared = BackgroundTaskManager()
    
    func registerTasks() {
        // 処理タスク（30秒以内）
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.myapp.refresh",
            using: nil
        ) { task in
            self.handleAppRefresh(task: task as! BGAppRefreshTask)
        }
        
        // 長時間タスク（数分）
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.myapp.processing",
            using: nil
        ) { task in
            self.handleProcessing(task: task as! BGProcessingTask)
        }
    }
    
    func scheduleAppRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: "com.myapp.refresh")
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)  // 15分後
        
        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("Failed to schedule: \(error)")
        }
    }
    
    func scheduleProcessing() {
        let request = BGProcessingTaskRequest(identifier: "com.myapp.processing")
        request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 60)  // 1時間後
        request.requiresNetworkConnectivity = true
        request.requiresExternalPower = true  // 充電中のみ
        
        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("Failed to schedule: \(error)")
        }
    }
    
    private func handleAppRefresh(task: BGAppRefreshTask) {
        scheduleAppRefresh()  // 次のスケジュール
        
        task.expirationHandler = {
            // タイムアウト処理
        }
        
        Task {
            await refreshData()
            task.setTaskCompleted(success: true)
        }
    }
    
    private func handleProcessing(task: BGProcessingTask) {
        task.expirationHandler = {
            // クリーンアップ
        }
        
        Task {
            await performHeavyProcessing()
            task.setTaskCompleted(success: true)
        }
    }
}
```

### ポーリングの回避

```swift
// Bad: ポーリング
Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { _ in
    checkForUpdates()
}

// Good: プッシュ通知
class PushNotificationHandler {
    func didReceiveRemoteNotification(_ userInfo: [AnyHashable: Any]) {
        if userInfo["type"] as? String == "data_update" {
            refreshData()
        }
    }
}

// Good: WebSocket（リアルタイム更新が必要な場合）
class WebSocketManager {
    func connect() {
        let task = URLSession.shared.webSocketTask(with: url)
        task.resume()
        receiveMessage(task: task)
    }
    
    private func receiveMessage(task: URLSessionWebSocketTask) {
        task.receive { [weak self] result in
            switch result {
            case .success(let message):
                self?.handleMessage(message)
                self?.receiveMessage(task: task)
            case .failure(let error):
                print("WebSocket error: \(error)")
            }
        }
    }
}
```

## 画面とアニメーション

### ディスプレイリンクの管理

```swift
class AnimationManager {
    private var displayLink: CADisplayLink?
    
    func startAnimation() {
        displayLink = CADisplayLink(target: self, selector: #selector(update))
        displayLink?.preferredFrameRateRange = CAFrameRateRange(
            minimum: 30,
            maximum: 60,
            preferred: 60
        )
        displayLink?.add(to: .main, forMode: .common)
    }
    
    func pauseAnimation() {
        displayLink?.isPaused = true
    }
    
    func stopAnimation() {
        displayLink?.invalidate()
        displayLink = nil
    }
    
    @objc private func update(_ link: CADisplayLink) {
        // アニメーション更新
    }
}
```

### アイドル時の処理停止

```swift
class AppLifecycleManager {
    func setup() {
        NotificationCenter.default.addObserver(
            forName: UIApplication.willResignActiveNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.pauseNonEssentialTasks()
        }
        
        NotificationCenter.default.addObserver(
            forName: UIApplication.didBecomeActiveNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.resumeTasks()
        }
    }
    
    private func pauseNonEssentialTasks() {
        AnimationManager.shared.pauseAnimation()
        LocationManager.shared.reduceAccuracy()
        NetworkManager.shared.pauseNonCriticalRequests()
    }
    
    private func resumeTasks() {
        AnimationManager.shared.startAnimation()
        LocationManager.shared.restoreAccuracy()
        NetworkManager.shared.resumeRequests()
    }
}
```

## MetricKit によるモニタリング

```swift
import MetricKit

class EnergyMetricsCollector: NSObject, MXMetricManagerSubscriber {
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            // セルラー使用状況
            if let cellularMetrics = payload.cellularConditionMetrics {
                print("Cellular bars: \(cellularMetrics.histogrammedCellularConditionTime)")
            }
            
            // CPU時間
            if let cpuMetrics = payload.cpuMetrics {
                print("CPU time: \(cpuMetrics.cumulativeCPUTime)")
            }
            
            // 位置情報使用
            if let locationMetrics = payload.locationActivityMetrics {
                print("Location time: \(locationMetrics.cumulativeBestAccuracyTime)")
            }
        }
    }
}
```

## Energy Gauge（Xcode）

### 使い方

```
1. アプリを実機で実行
2. Xcode → Debug Navigator
3. Energy Impact を選択
4. 各リソースの使用状況を確認

表示項目:
- CPU: 処理による消費
- Network: 通信による消費
- Location: 位置情報による消費
- GPU: 描画による消費
- Background: バックグラウンド処理
- Overhead: システムオーバーヘッド
```

### 理想的な状態

```
アイドル時:
- CPU: 0〜1%
- Network: なし
- Location: なし
- GPU: 0〜1%

アクティブ時:
- CPU: 必要に応じて
- Network: バッチ処理
- Location: 必要最小限の精度
- GPU: 60fps 以下
```

## チェックリスト

### 位置情報

- [ ] 必要な精度のみ使用
- [ ] 不要時は停止
- [ ] significantLocationChanges の検討
- [ ] ジオフェンスの活用

### ネットワーク

- [ ] バッチ処理の実装
- [ ] WiFi 優先の設計
- [ ] isDiscretionary の活用
- [ ] ポーリングの回避

### バックグラウンド

- [ ] BGTaskScheduler の使用
- [ ] requiresExternalPower の設定
- [ ] 適切な earliestBeginDate
- [ ] expirationHandler の実装

### UI/アニメーション

- [ ] 不要なアニメーションの削減
- [ ] 適切なフレームレート設定
- [ ] アイドル時の処理停止
- [ ] 画面消灯時の対応

### モニタリング

- [ ] MetricKit の導入
- [ ] Energy Gauge での確認
- [ ] 実機でのテスト
- [ ] 長時間使用テスト
