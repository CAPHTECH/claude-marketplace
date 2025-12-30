# XCUITestパターン集

## Page Objectパターン

### 基本構造

```swift
// MARK: - Base Page

protocol Page {
    var app: XCUIApplication { get }
    func waitForPageLoad() -> Self
}

extension Page {
    @discardableResult
    func waitForPageLoad() -> Self {
        // デフォルト実装
        return self
    }
}

// MARK: - Login Page

final class LoginPage: Page {
    let app: XCUIApplication
    
    // MARK: - Elements
    var emailField: XCUIElement { app.textFields["email_field"] }
    var passwordField: XCUIElement { app.secureTextFields["password_field"] }
    var loginButton: XCUIElement { app.buttons["login_button"] }
    var errorLabel: XCUIElement { app.staticTexts["error_label"] }
    var forgotPasswordLink: XCUIElement { app.buttons["forgot_password_link"] }
    
    // MARK: - Initialization
    init(app: XCUIApplication) {
        self.app = app
    }
    
    @discardableResult
    func waitForPageLoad() -> Self {
        XCTAssertTrue(emailField.waitForExistence(timeout: 5))
        return self
    }
    
    // MARK: - Actions
    @discardableResult
    func enterEmail(_ email: String) -> Self {
        emailField.tap()
        emailField.typeText(email)
        return self
    }
    
    @discardableResult
    func enterPassword(_ password: String) -> Self {
        passwordField.tap()
        passwordField.typeText(password)
        return self
    }
    
    func tapLogin() -> HomePage {
        loginButton.tap()
        return HomePage(app: app).waitForPageLoad()
    }
    
    func tapLoginExpectingError() -> Self {
        loginButton.tap()
        XCTAssertTrue(errorLabel.waitForExistence(timeout: 3))
        return self
    }
    
    func login(email: String, password: String) -> HomePage {
        enterEmail(email)
        enterPassword(password)
        return tapLogin()
    }
    
    // MARK: - Assertions
    func assertErrorMessage(_ message: String) -> Self {
        XCTAssertEqual(errorLabel.label, message)
        return self
    }
    
    func assertLoginButtonEnabled(_ enabled: Bool) -> Self {
        XCTAssertEqual(loginButton.isEnabled, enabled)
        return self
    }
}
```

### 画面遷移の表現

```swift
// 遷移を型で表現
final class ProductListPage: Page {
    let app: XCUIApplication
    
    func tapProduct(at index: Int) -> ProductDetailPage {
        app.cells["product_cell_\(index)"].tap()
        return ProductDetailPage(app: app).waitForPageLoad()
    }
    
    func tapCart() -> CartPage {
        app.buttons["cart_button"].tap()
        return CartPage(app: app).waitForPageLoad()
    }
}

final class ProductDetailPage: Page {
    let app: XCUIApplication
    
    func addToCart() -> Self {
        app.buttons["add_to_cart_button"].tap()
        return self
    }
    
    func goBack() -> ProductListPage {
        app.navigationBars.buttons.element(boundBy: 0).tap()
        return ProductListPage(app: app).waitForPageLoad()
    }
}
```

## Robot パターン

### 基本構造

```swift
// テストで使用するRobot
final class LoginRobot {
    private let app: XCUIApplication
    
    init(app: XCUIApplication) {
        self.app = app
    }
    
    // MARK: - Actions (What)
    
    @discardableResult
    func inputEmail(_ email: String) -> Self {
        app.textFields["email_field"].tap()
        app.textFields["email_field"].typeText(email)
        return self
    }
    
    @discardableResult
    func inputPassword(_ password: String) -> Self {
        app.secureTextFields["password_field"].tap()
        app.secureTextFields["password_field"].typeText(password)
        return self
    }
    
    @discardableResult
    func tapLoginButton() -> Self {
        app.buttons["login_button"].tap()
        return self
    }
    
    // MARK: - Verifications (Then)
    
    @discardableResult
    func verifyHomeScreenDisplayed() -> Self {
        XCTAssertTrue(app.staticTexts["welcome_label"].waitForExistence(timeout: 5))
        return self
    }
    
    @discardableResult
    func verifyErrorDisplayed(_ message: String) -> Self {
        let errorLabel = app.staticTexts["error_label"]
        XCTAssertTrue(errorLabel.waitForExistence(timeout: 3))
        XCTAssertEqual(errorLabel.label, message)
        return self
    }
}

// テストでの使用
final class LoginUITests: XCTestCase {
    private var app: XCUIApplication!
    private var loginRobot: LoginRobot!
    
    override func setUp() {
        super.setUp()
        app = XCUIApplication()
        app.launch()
        loginRobot = LoginRobot(app: app)
    }
    
    func test_login_withValidCredentials_showsHome() {
        loginRobot
            .inputEmail("user@example.com")
            .inputPassword("password123")
            .tapLoginButton()
            .verifyHomeScreenDisplayed()
    }
    
    func test_login_withInvalidPassword_showsError() {
        loginRobot
            .inputEmail("user@example.com")
            .inputPassword("wrong")
            .tapLoginButton()
            .verifyErrorDisplayed("Invalid credentials")
    }
}
```

## 待機パターン

### 要素の存在待機

```swift
extension XCUIElement {
    @discardableResult
    func waitForExistence(timeout: TimeInterval = 5, file: StaticString = #file, line: UInt = #line) -> Bool {
        let exists = self.waitForExistence(timeout: timeout)
        if !exists {
            XCTFail("Element \(self) did not appear within \(timeout) seconds", file: file, line: line)
        }
        return exists
    }
    
    func waitForDisappearance(timeout: TimeInterval = 5, file: StaticString = #file, line: UInt = #line) {
        let predicate = NSPredicate(format: "exists == false")
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: self)
        let result = XCTWaiter.wait(for: [expectation], timeout: timeout)
        if result != .completed {
            XCTFail("Element \(self) did not disappear within \(timeout) seconds", file: file, line: line)
        }
    }
}
```

### 状態変化の待機

```swift
extension XCUIElement {
    func waitForEnabled(timeout: TimeInterval = 5) {
        let predicate = NSPredicate(format: "isEnabled == true")
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: self)
        XCTWaiter.wait(for: [expectation], timeout: timeout)
    }
    
    func waitForValue(_ expectedValue: String, timeout: TimeInterval = 5) {
        let predicate = NSPredicate(format: "value == %@", expectedValue)
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: self)
        XCTWaiter.wait(for: [expectation], timeout: timeout)
    }
    
    func waitForLabel(_ expectedLabel: String, timeout: TimeInterval = 5) {
        let predicate = NSPredicate(format: "label == %@", expectedLabel)
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: self)
        XCTWaiter.wait(for: [expectation], timeout: timeout)
    }
}
```

### ローディング完了待機

```swift
final class LoadingHelper {
    private let app: XCUIApplication
    
    init(app: XCUIApplication) {
        self.app = app
    }
    
    func waitForLoadingToComplete(timeout: TimeInterval = 10) {
        let loadingIndicator = app.activityIndicators["loading_indicator"]
        
        // ローディングが表示されるまで待機（オプション）
        _ = loadingIndicator.waitForExistence(timeout: 2)
        
        // ローディングが消えるまで待機
        if loadingIndicator.exists {
            loadingIndicator.waitForDisappearance(timeout: timeout)
        }
    }
}
```

## Accessibility Identifier 管理

### 定数定義

```swift
// AccessibilityIdentifiers.swift
enum AccessibilityID {
    enum Login {
        static let screen = "login_screen"
        static let emailField = "login_email_field"
        static let passwordField = "login_password_field"
        static let loginButton = "login_submit_button"
        static let errorLabel = "login_error_label"
    }
    
    enum Home {
        static let screen = "home_screen"
        static let welcomeLabel = "home_welcome_label"
        static let menuButton = "home_menu_button"
    }
    
    enum ProductList {
        static let screen = "product_list_screen"
        static func cell(at index: Int) -> String { "product_cell_\(index)" }
        static let searchField = "product_search_field"
    }
}

// View側での設定
struct LoginView: View {
    var body: some View {
        VStack {
            TextField("Email", text: $email)
                .accessibilityIdentifier(AccessibilityID.Login.emailField)
            
            SecureField("Password", text: $password)
                .accessibilityIdentifier(AccessibilityID.Login.passwordField)
            
            Button("Login") { ... }
                .accessibilityIdentifier(AccessibilityID.Login.loginButton)
        }
        .accessibilityIdentifier(AccessibilityID.Login.screen)
    }
}
```

### テストでの使用

```swift
final class LoginPage: Page {
    let app: XCUIApplication
    
    var emailField: XCUIElement {
        app.textFields[AccessibilityID.Login.emailField]
    }
    
    var passwordField: XCUIElement {
        app.secureTextFields[AccessibilityID.Login.passwordField]
    }
    
    var loginButton: XCUIElement {
        app.buttons[AccessibilityID.Login.loginButton]
    }
}
```

## スクリーンショットパターン

### 失敗時の自動スクリーンショット

```swift
final class BaseUITestCase: XCTestCase {
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDown() {
        // テスト失敗時にスクリーンショットを保存
        if testRun?.hasSucceeded == false {
            takeScreenshot(name: "failure_\(name)")
        }
        super.tearDown()
    }
    
    func takeScreenshot(name: String) {
        let screenshot = app.screenshot()
        let attachment = XCTAttachment(screenshot: screenshot)
        attachment.name = name
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
```

### 任意のタイミングでのスクリーンショット

```swift
extension XCTestCase {
    func captureScreen(_ name: String) {
        let screenshot = XCUIScreen.main.screenshot()
        let attachment = XCTAttachment(screenshot: screenshot)
        attachment.name = name
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}

// 使用例
func test_checkout_flow() {
    // ... 操作
    captureScreen("step1_cart")
    
    // ... 次の操作
    captureScreen("step2_shipping")
    
    // ... 最終操作
    captureScreen("step3_confirmation")
}
```

## テストデータ管理

### Launch Arguments

```swift
// テスト側
final class MockDataUITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        app = XCUIApplication()
        
        // モックモード有効化
        app.launchArguments.append("--uitesting")
        app.launchArguments.append("--mock-api")
        
        // テストユーザー情報
        app.launchEnvironment["TEST_USER_EMAIL"] = "test@example.com"
        app.launchEnvironment["TEST_USER_TOKEN"] = "mock-token-123"
        
        app.launch()
    }
}

// アプリ側
@main
struct MyApp: App {
    init() {
        if ProcessInfo.processInfo.arguments.contains("--uitesting") {
            // UIテストモードの設定
            configureMockEnvironment()
        }
    }
    
    private func configureMockEnvironment() {
        if ProcessInfo.processInfo.arguments.contains("--mock-api") {
            APIClient.shared.useMockResponses = true
        }
        
        if let email = ProcessInfo.processInfo.environment["TEST_USER_EMAIL"] {
            TestUserManager.shared.setEmail(email)
        }
    }
}
```

### テストシナリオ別の設定

```swift
enum TestScenario: String {
    case loggedIn = "logged_in"
    case loggedOut = "logged_out"
    case emptyCart = "empty_cart"
    case fullCart = "full_cart"
    case networkError = "network_error"
}

extension XCUIApplication {
    func launch(with scenario: TestScenario) {
        launchArguments.append("--uitesting")
        launchArguments.append("--scenario=\(scenario.rawValue)")
        launch()
    }
}

// 使用例
func test_cart_whenEmpty_showsEmptyMessage() {
    app.launch(with: .emptyCart)
    // テスト実行
}
```

## デバイス・画面サイズ対応

### 画面サイズごとのテスト

```swift
final class ResponsiveUITests: XCTestCase {
    func test_layout_onAllDeviceSizes() {
        // このテストは複数のシミュレータで実行する想定
        let app = XCUIApplication()
        app.launch()
        
        // 画面サイズに応じた要素の存在確認
        let isCompact = UIScreen.main.bounds.width < 375
        
        if isCompact {
            XCTAssertTrue(app.buttons["menu_button"].exists)
            XCTAssertFalse(app.buttons["expanded_menu"].exists)
        } else {
            XCTAssertFalse(app.buttons["menu_button"].exists)
            XCTAssertTrue(app.buttons["expanded_menu"].exists)
        }
    }
}
```

### デバイスの向き

```swift
func test_layout_inLandscape() {
    XCUIDevice.shared.orientation = .landscapeLeft
    
    let app = XCUIApplication()
    app.launch()
    
    // 横向きでのレイアウト確認
    XCTAssertTrue(app.buttons["side_panel_button"].exists)
    
    // 元に戻す
    XCUIDevice.shared.orientation = .portrait
}
```

## システムアラート対応

### アラート処理

```swift
final class AlertHandlingTests: XCTestCase {
    func test_cameraAccess_whenAllowed_showsCamera() {
        let app = XCUIApplication()
        app.launch()
        
        // カメラ権限リクエストのトリガー
        app.buttons["open_camera"].tap()
        
        // システムアラートの処理
        addUIInterruptionMonitor(withDescription: "Camera Permission") { alert in
            if alert.buttons["Allow"].exists {
                alert.buttons["Allow"].tap()
                return true
            }
            return false
        }
        
        // インタラクションを発生させてモニターをトリガー
        app.tap()
        
        // カメラ画面の確認
        XCTAssertTrue(app.otherElements["camera_view"].waitForExistence(timeout: 5))
    }
}
```

### プッシュ通知権限

```swift
func test_notification_permission() {
    let app = XCUIApplication()
    app.launch()
    
    addUIInterruptionMonitor(withDescription: "Notification Permission") { alert in
        if alert.buttons["Allow"].exists {
            alert.buttons["Allow"].tap()
            return true
        } else if alert.buttons["Don't Allow"].exists {
            alert.buttons["Don't Allow"].tap()
            return true
        }
        return false
    }
    
    app.buttons["enable_notifications"].tap()
    app.tap() // モニターをトリガー
}
```
