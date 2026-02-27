# 証拠収集方法の体系

バグの発見と法則復元確認のための証拠収集方法を体系的に整理する。

## 収集タイミング × レイヤーマトリクス

| タイミング | コード層 | ランタイム層 | インフラ層 | ユーザー層 |
|------------|----------|--------------|------------|------------|
| **静的** | 型チェック、Lint、静的解析 | - | IaC検証 | 仕様レビュー |
| **動的** | デバッガ、REPL | ログ、トレース、メトリクス | APM、分散トレース | セッション録画 |
| **事後** | コードレビュー、差分分析 | ログ解析、クラッシュダンプ | 障害解析 | ユーザー報告 |

## 詳細リスト

### 1. 静的証拠（実行前）

| 方法 | 検出対象 | ツール例 | 法則への適用 |
|------|----------|----------|--------------|
| **型チェック** | 型の不整合 | TypeScript, mypy, Flow | 型レベルの不変条件 |
| **Lint** | コーディング規約違反 | ESLint, Clippy, SwiftLint | 構文レベルのPolicy |
| **静的解析** | 潜在バグ、セキュリティ | SonarQube, CodeQL, Semgrep | 安全性Invariant |
| **依存関係分析** | 脆弱性、非互換 | Dependabot, Snyk | 依存性Policy |
| **コンパイル警告** | 未使用変数、到達不能コード | コンパイラ | 構造的Invariant |
| **形式検証** | 論理的正しさ | TLA+, Alloy, Coq | 数学的Law |
| **契約検証** | 事前/事後条件 | Design by Contract | Pre/Post条件 |
| **AST解析** | コード構造の異常 | Tree-sitter | 構造的Law |

### 2. 動的証拠（実行中）

#### 2.1 ログ・トレース系

| 方法 | 収集内容 | ツール例 | 法則への適用 |
|------|----------|----------|--------------|
| **構造化ログ** | イベント、状態変化 | Winston, Bunyan, structlog | 状態遷移の観測 |
| **分散トレース** | リクエストフロー | Jaeger, Zipkin, OpenTelemetry | 因果関係の追跡 |
| **監査ログ** | セキュリティイベント | 専用監査システム | セキュリティPolicy |
| **イベントソーシング** | 状態変化の全履歴 | EventStore, Kafka | 状態Invariant |
| **コンソール出力** | デバッグ情報 | console.log, print | 局所的観測 |

**ELD的ログ出力パターン**:
```typescript
// 従来のログ
console.log("order failed:", error);

// ELD的ログ（法則視点）
console.log("[Law: 保存則] 在庫不整合検出", {
  expected: available + reserved,
  actual: total,
  delta: total - (available + reserved),
  lawViolated: true
});
```

#### 2.2 メトリクス系

| 方法 | 収集内容 | ツール例 | 法則への適用 |
|------|----------|----------|--------------|
| **アプリメトリクス** | カウンタ、ゲージ | Prometheus, StatsD | 定量的Invariant |
| **APM** | レイテンシ、エラー率 | Datadog, New Relic, Sentry | 性能Policy |
| **プロファイリング** | CPU、メモリ、I/O | perf, py-spy, Instruments | リソースInvariant |
| **ヒープダンプ** | メモリ状態 | jmap, heapdump | メモリPolicy |
| **GCログ** | ガベージコレクション | JVM GC logs | メモリInvariant |

#### 2.3 デバッガ系

| 方法 | 収集内容 | ツール例 | 法則への適用 |
|------|----------|----------|--------------|
| **ステップ実行** | 行ごとの状態 | lldb, gdb, IDE debugger | 局所的状態観測 |
| **ブレークポイント** | 特定地点の状態 | 同上 | 条件成立確認 |
| **条件付きブレーク** | 条件成立時の状態 | 同上 | 法則違反の捕捉 |
| **ウォッチポイント** | 変数変更の検出 | 同上 | 状態変化の追跡 |
| **リモートデバッグ** | 本番/ステージングの状態 | Chrome DevTools, delve | 環境固有の観測 |
| **タイムトラベルデバッグ** | 過去状態の再現 | rr, WinDbg TTD | 法則違反時点の特定 |

**ELD的デバッグ**: 条件付きブレークポイントで法則違反を捕捉
```
// 保存則違反で停止
break if (stock !== available + reserved)
```

#### 2.4 ランタイム検証系

| 方法 | 収集内容 | ツール例 | 法則への適用 |
|------|----------|----------|--------------|
| **アサーション** | 不変条件違反 | assert, invariant checks | Invariant直接検証 |
| **サニタイザ** | メモリエラー、データ競合 | ASan, TSan, MSan | 安全性Invariant |
| **ランタイム型チェック** | 型違反 | io-ts, zod (runtime) | 型Invariant |
| **カナリア値** | バッファオーバーフロー | Stack canaries | メモリPolicy |

### 3. テスト系証拠

| 方法 | 検証内容 | ツール例 | 法則への適用 |
|------|----------|----------|--------------|
| **ユニットテスト** | 単体の法則 | Jest, pytest, XCTest | 単一Law検証 |
| **統合テスト** | コンポーネント連携 | 同上 | 複合Law検証 |
| **E2Eテスト** | ユーザーフロー | Playwright, Cypress | システムレベルPolicy |
| **Property-based test** | 法則の網羅的検証 | fast-check, Hypothesis | **Law検証の本命** |
| **Mutation testing** | テストの品質 | Stryker, mutmut | 検証の信頼性 |
| **Fuzz testing** | 予期しない入力 | AFL, libFuzzer | 境界条件Law |
| **Chaos testing** | 障害耐性 | Chaos Monkey, Litmus | 可用性Policy |
| **負荷テスト** | 性能限界 | k6, Locust, JMeter | 性能Policy |
| **回帰テスト** | 既知バグの再発防止 | CI/CD pipeline | Law違反の再発防止 |
| **スナップショットテスト** | 出力の変化検出 | Jest snapshot | 出力Invariant |
| **契約テスト** | API互換性 | Pact, Spring Cloud Contract | インターフェースLaw |

**Property-based testによる法則検証**:
```typescript
// 保存則のProperty-based test
test('在庫保存則', () => {
  fc.assert(fc.property(
    fc.integer({ min: 0, max: 1000 }),
    fc.integer({ min: 0, max: 100 }),
    (initial, reserveAmount) => {
      const inv = new Inventory(initial);
      if (reserveAmount <= initial) {
        inv.reserve(reserveAmount);
      }
      // Law: stock === available + reserved
      return inv.total === inv.available + inv.reserved;
    }
  ));
});
```

### 4. インフラ層証拠

| 方法 | 収集内容 | ツール例 | 法則への適用 |
|------|----------|----------|--------------|
| **システムログ** | OS/ミドルウェアイベント | syslog, journald | 環境Invariant |
| **ネットワークキャプチャ** | パケット内容 | tcpdump, Wireshark | 通信Law |
| **コンテナログ** | コンテナ出力 | docker logs, kubectl logs | 実行環境観測 |
| **リソースモニタリング** | CPU/メモリ/ディスク | top, htop, Grafana | リソースPolicy |
| **DBクエリログ** | 実行SQL | slow query log | データアクセスLaw |
| **DBトランザクションログ** | データ変更履歴 | binlog, WAL | データInvariant |
| **クラウドログ** | クラウドサービスイベント | CloudWatch, Cloud Logging | インフラPolicy |

### 5. ユーザー層証拠

| 方法 | 収集内容 | ツール例 | 法則への適用 |
|------|----------|----------|--------------|
| **エラーレポート** | クラッシュ情報 | Sentry, Crashlytics | 例外Law |
| **セッション録画** | ユーザー操作 | FullStory, LogRocket | ユーザー体験Policy |
| **ユーザー報告** | 症状の記述 | Issue tracker | 現象の言語化 |
| **スクリーンショット** | 視覚的状態 | 手動/自動キャプチャ | UI状態観測 |
| **再現手順** | 操作シーケンス | ユーザー提供 | 因果関係の手がかり |
| **A/Bテスト結果** | 振る舞い差異 | Optimizely, LaunchDarkly | 変更影響の観測 |

### 6. 履歴・差分系証拠

| 方法 | 収集内容 | ツール例 | 法則への適用 |
|------|----------|----------|--------------|
| **Git履歴** | コード変更 | git log, git blame | 変更との相関 |
| **git bisect** | バグ導入コミット特定 | git bisect | **法則違反開始点の特定** |
| **デプロイ履歴** | リリース情報 | CI/CD logs | 環境変更との相関 |
| **設定変更履歴** | 環境変更 | Terraform state, Ansible logs | 設定Law違反 |
| **依存関係履歴** | ライブラリ変更 | lockfile diff | 依存性Law |

**git bisectによる法則違反開始点の特定**:
```bash
# 法則違反を検出するテストで bisect
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
git bisect run npm test -- --grep "保存則"
```

## 証拠の梯子との対応表

| Level | 主な収集方法 | 検証の確度 |
|-------|-------------|-----------|
| **L0** | 型チェック、Lint、静的解析、形式検証 | 構文レベルの保証 |
| **L1** | ユニットテスト、Property-based test、アサーション | 単体での法則成立 |
| **L2** | 統合テスト、E2Eテスト、契約テスト | 連携での法則成立 |
| **L3** | Chaos testing、Fuzz testing、サニタイザ | 異常時の法則維持 |
| **L4** | APM、分散トレース、メトリクス、エラーレポート | 実運用での法則成立 |

## ELD的デバッグで特に有効な組み合わせ

| 目的 | 組み合わせ | 効果 |
|------|-----------|------|
| **法則発見** | git bisect + 差分分析 | 「いつ法則が破られたか」特定 |
| **法則検証** | Property-based test | 「法則が網羅的に成立するか」確認 |
| **法則監視** | アサーション + メトリクス | 「法則違反を即時検出」 |
| **法則復元** | タイムトラベルデバッグ | 「法則が破られた瞬間を再現」 |
| **根本原因** | 構造化ログ + 分散トレース | 「法則違反の因果を追跡」 |
