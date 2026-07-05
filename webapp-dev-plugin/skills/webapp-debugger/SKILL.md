---
name: webapp-debugger
context: fork
description: Chrome DevTools MCPを使用したWebアプリのデバッグ支援スキル。ブラウザ操作、コンソールログ監視、ネットワークリクエスト分析、パフォーマンス計測を行う。使用タイミング: (1) Webアプリの動作確認・デバッグ (2) UIの自動操作テスト (3) ネットワークエラーの調査 (4) コンソールエラーの確認 (5) パフォーマンス問題の診断 (6) フォーム入力の自動化 (7) スクリーンショット取得
---

# Webapp Debugger

Chrome DevTools MCPを使用してWebアプリをデバッグするためのスキル。ツールのシグネチャはMCPサーバーが提供するスキーマに従う。

## 重要なポイント

1. **uid取得が必須**: 要素操作前に必ず`take_snapshot()`を実行
2. **スナップショット優先**: スクリーンショットより`take_snapshot()`を使用（軽量・uid取得可能）
3. **待機の活用**: 非同期操作後は`wait_for(text: "期待するテキスト")`で待機
4. **エラー確認**: 操作後は`list_console_messages(types: ["error"])`でエラーチェック

## デバッグシナリオ別ガイド

- **UIデバッグ**: [references/ui-debugging.md](references/ui-debugging.md)
- **ネットワークデバッグ**: [references/network-debugging.md](references/network-debugging.md)
- **パフォーマンス分析**: [references/performance-analysis.md](references/performance-analysis.md)
- **活用シナリオ集**: [references/use-cases.md](references/use-cases.md)

## トラブルシューティング

| 問題 | 解決策 |
|------|--------|
| uidが見つからない | `take_snapshot(verbose: true)`で詳細情報取得 |
| 要素が操作できない | `wait_for()`で要素の出現を待機 |
| ダイアログが出る | `handle_dialog(action: "accept")`で処理 |
| ネットワークエラー | `list_network_requests()`でステータス確認 |
