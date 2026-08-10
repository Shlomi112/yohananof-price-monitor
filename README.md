# Yohananof Price/Promo Monitor

Watches the official price-transparency feed for one Yohananof branch
(default: **מישור אדומים**, store 046) and alerts on new, changed, or
ended promotions. Built on public data chains are legally required to
publish (Price Transparency in Food Law, 2014) — no scraping of the
consumer app, no automated purchasing.

## How it works

Yohananof (like ~19 other Israeli chains) publishes gzipped XML dumps of
every price and promotion, per branch, to a shared FTPS portal
(`url.retail.publishedprices.co.il`). This project connects there directly
with Python's stdlib `ftplib` — no browser automation needed for this chain.

Each run:
1. Downloads the latest full price dump and full promo dump for the store.
2. Compares the promos against the last saved snapshot (`data/*.json`).
3. If anything is new / changed price / ended, sends a Telegram message
   (or prints to stdout if Telegram isn't configured yet).

## Setup

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

Run once manually:
```
.venv\Scripts\python -m yohananof_monitor.main
```
The first run only saves a baseline snapshot (nothing to compare against
yet) — real alerts start from the second run onward.

## Telegram alerts

1. Message [@BotFather](https://t.me/BotFather) on Telegram, `/newbot`,
   grab the token it gives you.
2. Message your new bot anything, then visit
   `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your `chat.id`.
3. Copy `.env.example` to `.env` and fill in `TELEGRAM_BOT_TOKEN` /
   `TELEGRAM_CHAT_ID`.

Without these set, the script still runs and prints the report to stdout
(useful for testing, or for wiring into a different channel later).

## Running on a schedule (GitHub Actions - no PC required)

This repo runs itself on GitHub's servers, on the hour, via
`.github/workflows/monitor.yml` - your computer can be off. There's no
local Task Scheduler entry (there was one during development; it was
removed to avoid double alerts firing from two separate snapshots).

Setup (already done for this repo, kept here for reference / if you fork it):
1. Push this repo to GitHub.
2. `gh secret set TELEGRAM_BOT_TOKEN` and `gh secret set TELEGRAM_CHAT_ID`
   (or set them under Settings → Secrets and variables → Actions).
3. That's it - the workflow runs hourly on its own. Trigger it manually
   any time from the repo's Actions tab ("Run workflow"), or:
   `gh workflow run monitor.yml`.

Because each run happens on a fresh GitHub-hosted VM, the promo snapshot
(`data/*.json`) is committed back to the repo at the end of every run so
the next run has something to diff against - that's why `data/` is
tracked in git here instead of gitignored.

## Other branches or chains

Find a StoreID by (partial) branch name:
```
.venv\Scripts\python find_store.py yohananof "מישור אדומים"
```

To watch a different Yohananof branch, set `PRICE_MONITOR_STORE_ID` in
`.env`. To add another chain that publishes on the same shared FTPS portal
(many do — check via `find_store.py`, or the chain's own price-transparency
page linked from [gov.il](https://www.gov.il/he/pages/cpfta_prices_regulations)),
add its FTP username and chain ID to `CHAINS` in
`yohananof_monitor/config.py`. Not every chain uses this shared portal
(some run their own site, e.g. Shufersal) — those need a different fetch
method, not covered here.

## What this won't catch

Only promotions the chain actually reports through the transparency feed
show up here. Purely local, till-only clearance stickers that never make it
into the chain's own price system (rare, but they exist) won't appear —
there's no official data source for those; the "have someone snap a photo"
route from the original brainstorm is a separate, people-powered project.

## WhatsApp

Not wired up — see the conversation this was built from for why (WhatsApp
Business Cloud API requires Meta business verification + pre-approved
message templates; not a quick add). Telegram is the alert channel for now.
