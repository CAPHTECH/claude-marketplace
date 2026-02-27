---
name: eld-model
context: fork
argument-hint: "discover | card | full (default: full)"
description: |
  **Deprecated**: `/eld-spec` を使用してください。
  このスキルは後方互換のためのエイリアスです。すべての呼び出しは `/eld-spec` に転送されます。
---

# eld-model (Deprecated → /eld-spec)

> **このスキルは非推奨です。** `/eld-spec` を使用してください。

このスキルは delivery-plugin との後方互換性のために残されています。

## 転送先

`/eld-spec $ARGUMENTS`

すべての引数はそのまま `/eld-spec` に転送されます:
- `discover` → `/eld-spec discover`
- `card` → `/eld-spec card`
- `full` → `/eld-spec full`

## 移行ガイド

| 旧スキル | 新スキル |
|----------|---------|
| `/eld-model` | `/eld-spec` |
| `/eld-model discover` | `/eld-spec discover` |
| `/eld-model card` | `/eld-spec card` |
| `/eld-model-law-discovery` | `/eld-spec-discover` |
| `/eld-model-law-card` | `/eld-spec-card law` |
| `/eld-model-term-card` | `/eld-spec-card term` |
| `/eld-model-link-map` | `/eld-spec-link` |
