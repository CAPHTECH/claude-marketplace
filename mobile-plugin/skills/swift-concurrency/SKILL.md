---
name: swift-concurrency
context: fork
description: Swift Concurrency支援。async/await、Actor、Sendable、データ競合防止。使用タイミング: (1) 並行処理コードの実装時、(2) Swift 6 Strict Concurrency対応時、(3) データ競合の診断・修正時、(4) MainActorとバックグラウンド処理の設計時
---

# Swift Concurrency 支援スキル

Swift Concurrencyの正しい使用法とデータ競合防止をガイドする。

## 対象

- Actor と隔離
- Sendable 準拠
- Task キャンセルと構造化並行性
- @MainActor とUI更新
- Swift 6 Strict Concurrencyへの移行

## Swift 6 Strict Concurrency

### Sendable要件

```swift
// ✅ 値型は自動的にSendable
struct UserData: Sendable {
    let id: UUID
    let name: String
}

// ✅ Actorは暗黙的にSendable
actor DataManager {
    private var cache: [String: Data] = [:]
    
    func getData(for key: String) -> Data? {
        cache[key]
    }
}

// ⚠️ クラスは明示的な対応が必要
// 方法1: @unchecked Sendable（内部で同期を保証している場合のみ使用）
final class ThreadSafeCache: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: Any] = [:]
    
    func get(_ key: String) -> Any? {
        lock.withLock { storage[key] }
    }
}

// 方法2: 不変クラス
final class ImmutableConfig: Sendable {
    let apiURL: URL
    let timeout: TimeInterval
    
    init(apiURL: URL, timeout: TimeInterval) {
        self.apiURL = apiURL
        self.timeout = timeout
    }
}
```

### Actor隔離

```swift
// グローバルActor定義
@globalActor
actor DatabaseActor {
    static let shared = DatabaseActor()
}

// Actor隔離されたクラス
@DatabaseActor
class DatabaseService {
    private var connection: DatabaseConnection?
    
    func query(_ sql: String) async throws -> [Row] {
        // DatabaseActor上で実行される
        guard let conn = connection else {
            throw DatabaseError.notConnected
        }
        return try await conn.execute(sql)
    }
}

// MainActorへの切り替え
@DatabaseActor
class ViewModel {
    private var data: [Item] = []
    
    func loadData() async {
        let items = try? await fetchItems()
        
        // UI更新はMainActorで
        await MainActor.run {
            self.updateUI(with: items ?? [])
        }
    }
    
    @MainActor
    private func updateUI(with items: [Item]) {
        // UI更新処理
    }
}
```

## Swift 6移行ビルド設定

### Package.swift

```swift
swiftSettings: [
    .enableExperimentalFeature("StrictConcurrency")
    // または
    .swiftLanguageMode(.v6)
]
```

### Xcodeプロジェクト

- Build Settings > Swift Compiler - Upcoming Features
- `SWIFT_STRICT_CONCURRENCY = complete`（コンパイラフラグとしては `-strict-concurrency=complete`）

### 段階的移行

- Phase 1: `.enableUpcomingFeature("StrictConcurrency")` で警告のみ有効化
- Phase 2-3: 新規コードから準拠、依存の少ないモジュールから順次移行
- Phase 4: `swiftLanguageMode: .v6` でアプリ全体をSwift 6モードへ

## Task管理

### 構造化並行性とキャンセル

```swift
class SearchViewModel: ObservableObject {
    @Published var results: [SearchResult] = []
    @Published var isSearching = false
    
    private var searchTask: Task<Void, Never>?
    
    func search(query: String) {
        // 前の検索をキャンセル
        searchTask?.cancel()
        
        searchTask = Task {
            await MainActor.run {
                isSearching = true
            }
            
            // デバウンス
            try? await Task.sleep(for: .milliseconds(300))
            
            // キャンセルチェック
            guard !Task.isCancelled else { return }
            
            do {
                let results = try await performSearch(query)
                
                guard !Task.isCancelled else { return }
                
                await MainActor.run {
                    self.results = results
                    self.isSearching = false
                }
            } catch {
                guard !Task.isCancelled else { return }
                
                await MainActor.run {
                    self.isSearching = false
                }
            }
        }
    }
    
    deinit {
        searchTask?.cancel()
    }
}
```

## よくあるエラーと解決策

### Actor再入問題

```swift
actor BankAccount {
    var balance: Int = 0
    
    // ⚠️ awaitの前後でbalanceが変わる可能性
    func transferTo(_ other: BankAccount, amount: Int) async {
        guard balance >= amount else { return }
        
        balance -= amount  // ここで中断
        await other.deposit(amount)  // 他のタスクがbalanceを変更可能
        // 戻ってきた時、想定外の状態かも
    }
    
    // ✅ トランザクション的に処理
    func withdraw(_ amount: Int) -> Bool {
        guard balance >= amount else { return false }
        balance -= amount
        return true
    }
    
    func deposit(_ amount: Int) {
        balance += amount
    }
}

// 呼び出し側で制御
func transfer(from: BankAccount, to: BankAccount, amount: Int) async {
    let withdrawn = await from.withdraw(amount)
    if withdrawn {
        await to.deposit(amount)
    }
}
```

## チェックリスト

### 設計時
- [ ] 共有状態を持つクラスはActorにすべきか検討
- [ ] Sendable要件を満たす型設計か
- [ ] MainActorの範囲は適切か

### 実装時
- [ ] Taskのキャンセル処理を実装したか
- [ ] await前後での状態変化を考慮したか（Actor再入）

### レビュー時
- [ ] @unchecked Sendableの使用は正当化されているか
- [ ] nonisolated(unsafe)の使用は避けられているか
- [ ] 循環参照やメモリリークはないか
