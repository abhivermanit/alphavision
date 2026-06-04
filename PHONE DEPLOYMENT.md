# AlphaVision — Setup & Deployment Guide

**Everything runs on GitHub Actions (free). No Railway. No server.**

---

## How It Works

- **GitHub Actions** runs the bot every weekday at 9:15 AM IST automatically
- **Screener.in** provides all stock data (price, fundamentals, 10-year history)
- **OpenAI GPT-4o-mini** generates thesis paragraphs and news sentiment
- **Supabase** stores recommendations, watchlist, and your holdings
- **Telegram** delivers the daily report to your phone

---

## Step 1: GitHub Repository

Your repo: `abhivermanit/alphavision`

Files that must be present:
- `alphavision_bot.py` — the main bot
- `requirements.txt` — dependencies
- `Procfile` — `worker: python alphavision_bot.py`
- `.github/workflows/daily_analysis.yml` — the cron schedule

To update the bot: go to GitHub → your file → pencil icon → paste new code → Commit.

---

## Step 2: GitHub Actions Secrets

Go to: GitHub repo → **Settings** → **Secrets and variables** → **Actions**

These 6 secrets must be set:

| Secret Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | `1358976952` |
| `OPENAI_API_KEY` | Your OpenAI key from platform.openai.com |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon key |
| `X_BEARER_TOKEN` | Twitter/X Bearer token (optional) |

---

## Step 3: Supabase Tables

Run these SQL statements once in Supabase → SQL Editor:

```sql
-- Daily scoring output
create table recommendations (
  ticker text, date text, recommendation text,
  composite_score int, p1_moat_score int, p2_valuation_score int,
  p3_health_score int, p4_management_score int, p5_macro_score int,
  margin_of_safety_pct float, moat_type text, gate_passed bool,
  fail_reasons text, thesis text, sector text,
  primary key (ticker, date)
);

-- Stocks to watch (MONITOR → BUY crossover alerts)
create table watchlist (
  ticker text primary key, sector text, date_added text,
  score_when_added int, score_today int, alerted bool default false
);

-- Your actual stock purchases
create table holdings (
  id serial primary key,
  ticker text not null,
  buy_price float not null,
  buy_date text not null,
  quantity int not null,
  invested_amount float,
  score_at_buy int,
  notes text,
  active bool default true
);
```

---

## Step 4: Logging a Stock Purchase

When you buy a stock, add a row in Supabase → Table Editor → `holdings`:

| Field | Example |
|---|---|
| ticker | `WIPRO` |
| buy_price | `204.35` |
| quantity | `20` |
| buy_date | `2026-06-04` |
| invested_amount | `4087` |
| score_at_buy | `77` (from that day's Telegram report) |
| active | `true` |

The bot will monitor it from the next morning onwards.

---

## Step 5: Running Manually

To trigger a run immediately:

1. Go to GitHub repo → **Actions** tab
2. Click **AlphaVision Daily Analysis**
3. Click **Run workflow** → **Run workflow**
4. Watch the logs — should complete in ~10 minutes
5. Check Telegram for the report

---

## What You Receive on Telegram

**Daily report (9:15 AM IST weekdays):**
- Top BUY/STRONG BUY stocks with score, moat type, ROCE, margin of safety
- Safe entry price vs current price
- Tax breakdown (STCG/LTCG) for ₹50,000 investment
- 3-paragraph investment thesis per stock
- News sentiment per stock

**Portfolio monitor (same run):**
- P&L for each holding (current price vs your buy price)
- Net return after STCG or LTCG tax
- Red flag alerts: score drop, overvaluation, financial health deterioration

**Watchlist alerts:**
- Notified when a MONITOR stock crosses into BUY territory

---

## Scoring Framework (5 Pillars)

| Pillar | Weight | What It Measures |
|---|---|---|
| P1 Business Quality & Moat | 30% | ROCE 10yr, moat type, IROE |
| P2 Valuation & Margin of Safety | 30% | Graham Number, DCF, EV/EBITDA |
| P3 Financial Health | 20% | D/E, interest coverage, CFO/PAT |
| P4 Management Quality | 10% | Promoter holding, pledge %, dividends |
| P5 Macro & Sentiment | 10% | Sector cycle, news sentiment |

**Recommendations:** STRONG BUY ≥80 | BUY ≥65 | MONITOR ≥50 | WEAK ≥35 | AVOID <35

---

## Cron Schedule

```
45 3 * * 1-5   →   9:15 AM IST, Monday to Friday
```

GitHub Actions may fire up to 15–30 min late on busy days. Use "Run workflow" for an immediate run.

---

## Telegram Bot

- Bot: `@abhivermanit_bot`
- Your chat ID: `1358976952`

To get chat ID: message the bot anything, then open:
`https://api.telegram.org/bot<TOKEN>/getUpdates`
Look for `"chat":{"id":XXXXXXXXX}`

---

## Current Holdings (as of June 2026)

| Ticker | Shares | Avg Price | Invested |
|---|---|---|---|
| WIPRO | 20 | ₹204.35 | ₹4,087 |
| RITES | 20 | ₹201.38 | ₹4,028 |
| GPPL | 20 | ₹155.00 | ₹3,100 |
| BPCL | 20 | ₹294.20 | ₹5,884 |

---

**That's it. Check Telegram every morning at 9:15 AM IST.**
