---
title: Newtradium — AI Trading Platform
created: 2026-09-17
tags: [property, newtradium, trading, finance]
status: active
aliases: [Newtradium Trading, newtradium]
---

# Newtradium

> AI trading platform with a strategy engine, sandbox/live execution, and an encrypted key vault. Signals carry full `reasoning[]` transparency.
> Repository: `/root/projects/newtradium` (jaykgimple/newtradium, private) · Live: newtradium.vercel.app
> Part of → [[Home]]

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router) + Tailwind + three/gsap/framer-motion |
| Backend | Prisma 6 (pinned, see pitfalls) |
| DB | PostgreSQL 16 on VPS (Neon is intended prod, pending Jay OAuth) |
| Market data | Binance public REST via `data-api.binance.vision` |

## Key Mechanisms

- **5 strategies** (rsi-bollinger, macd-momentum, ema-crossover, breakout, ml-adaptive ensemble).
- **Engine:** backtester + gate (>=30% CAGR / >=38% WR / PF>=1.2), risk-manager (inertia-brake drawdown halt), fill-simulator, trading-engine (DI, no direct prisma imports).
- **Exchanges:** Alpaca (REST v2), Binance (HMAC-SHA256), Coinbase (ES256 JWT). Registry fail-closed without creds.
- **Live mode triple-gated:** active keys + `tradingMode==='LIVE'` + typed `I_UNDERSTAND_REAL_MONEY`.
- **Key vault:** AES-256-GCM, `ENCRYPTION_KEY_BASE64`.
- **Cron:** `0 7 * * *` -> `/api/engine/tick` (Vercel Hobby = daily only).

## Notes

- Prisma 7 breaks this project; pinned to 6.
- Binance Vercel US = HTTP 451; always `data-api.binance.vision`.
- Subagent delegation failed twice; prefer direct execution on core files.
- Full pitfalls in the `newtradium-development` skill.