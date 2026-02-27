---
name: eld-predict-impact
context: fork
description: |
  **Deprecated**: `/eld-predict-light` を使用してください。
  このスキルは後方互換のためのエイリアスです。すべての呼び出しは `/eld-predict-light` に転送されます。
---

# eld-predict-impact (Deprecated → /eld-predict-light)

> **このスキルは非推奨です。** `/eld-predict-light` を使用してください。

このスキルは既存ユーザーとの後方互換性のために残されています。

## 転送先

`/eld-predict-light`

## 変更点（v1.0 → v2.3）

- フルPredictフェーズ → Predict-Lightゲート（P0/P1/P2）
- 段階化は機械判定で自動決定
- P0（低リスク）は3行要約のみで通過

## 移行ガイド

| 旧スキル | 新スキル |
|----------|---------|
| `/eld-predict-impact` | `/eld-predict-light` |
