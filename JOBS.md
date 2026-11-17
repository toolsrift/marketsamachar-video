# Writing a job (what the daily task produces each slot)

A job is `jobs/<YYYY-MM-DD>_<HHMM>.json`. Each video is a list of **beats**; a beat = one host saying one line while one scene animates.

```json
{
 "date": "2026-11-17",
 "slot": "1600",
 "feed": "feed/2026-11-17_1602.json",
 "ticker": [{"name": "NIFTY 50", "value": "25,291.10", "pct": 0.58}],
 "videos": [
  {"id": "s1-flows", "kind": "short", "stamp": "17 NOV · 4 PM IST",
   "title": "≤ 90 chars", "hook": "≤ 7 words, *accent*", "thumb": "optional ≤ 5 words",
   "sources": ["NSE (provisional)"],
   "beats": [{"host": "videshi", "say": "one or two short spoken sentences", "scene": {"kind": "stat", "...": "..."}}],
   "description": "1–2 sentences", "caption": "Instagram caption, 1–2 sentences", "tags": ["..."]},
  {"id": "long-wrap", "kind": "long", "stamp": "TUE · 17 NOV 2026", "title": "...", "hook": "...", "sources": ["..."],
   "segments": [{"title": "Closing Bell", "beats": [ ... ]}],
   "description": "...", "tags": ["..."]}
 ]
}
```

## Hosts — who presents what
| host | topic | | host | topic |
|---|---|---|---|---|
| ghanti | market open/close, indices | | naya | IPOs, listings |
| teji | top gainers | | tareekh | events calendar, what's coming |
| mandi | top losers | | munshi | results |
| desi | DII flows | | bhonpu | announcements, orders, deals, fund-raises, management |
| videshi | FII flows, global markets | | golu | dividends |
| arth | economy, RBI, rupee, inflation, policy | | tohfa | bonus issues |
| katli | stock splits | | wapsi | buybacks |

## Scene kinds (data fields) — v3 illustrated scenes (engine/ill.py)
Each beat may also carry `title` (on-screen headline for that station, *accent* allowed, max ~40 chars). Beat 1 of a Short uses the video `hook`.
- `indices` {name, value, pct, points: [{label: "16 Nov", value}] oldest first (last = "Now"), milestone (optional round number), chart_label, extra: [{label, value}] (≤2)}
  Use the daily closes from `briefs` ledes for `points`. Old board form {items:[{name,value,pct}]} still works (first item = hero).
- `stat` {label, value, prefix, suffix, tone up/down, note}
- `facts` {items: [{label, value, tone}]} — 2–4
- `world` {items: [{name, value, pct}]} — up to 4 (indices abroad, crude, gold, USD/INR)
- `movers` {gainers: [{name, pct, price}], losers: [...]} — 3 best; shows a podium
- `flows` {days: [{date: "16 Nov", fii, dii}]} — newest last, up to 8; coins fly between the globe (FII) and the building (DII)
- `announce` {company, kicker "Fund-raise"/"Order win"/"Acquisition", amount, prefix "₹", suffix " cr", sub, stamp "Launched"/"Won"/"Approved"}
- `headline` {kicker, text, sub} — newspaper card for news without one key number
- `dividend` {company, amount "1", type "Interim", ex_date, record_date}
- `split` {company, from_fv "10", to_fv "2", ex_date}
- `bonus` {company, ratio "1:1", ex_date, record_date}
- `buyback` {company, size, price, method}
- `ipo` {company, open, close, band, size, lot}
- `results` {company, period, metrics: [{label, value, unit "cr", chg}]} or upcoming {company, date, purpose}
- `calendar` {items: [{date: "18 Nov", company, what}]} — up to 4
- `gauge` {name, value, min, max}
Every scene takes `source` (string or list, shown as a tag). Every video needs `sources`.
The look (fonts, colours, illustration treatment, camera moves, music) is picked from the date: one style per day
(studio · comic · blueprint · neon · paper). Don't set `style` in jobs unless asked.

## Rules the build enforces (`engine/check.py`)
- News only. No buy/sell/hold, targets, stop-loss, ratings/upgrades/downgrades, predictions ("will rise"), upside/downside,
  support/resistance, bullish/bearish, IPO GMP or listing gains, "stocks to buy/watch", tips, crypto/forex trading promotion,
  inducements ("opportunity", "don't miss"). Write "buyback", never "buy-back".
- Every number in `say` and `scene` must exist in the feed snapshot (exact, or the same at the shown precision).
- `sources` must be listed for every video.
