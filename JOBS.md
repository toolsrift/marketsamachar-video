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

## Scene kinds (data fields)
- `headline` {kicker, text (*accent*), sub}
- `stat` {label, value, prefix, suffix, tone up/down/neutral, delta, note}
- `facts` {items: [{label, value, tone, note}]} — 2–4
- `indices` / `world` {items: [{name, value, pct}], asof}
- `movers` {gainers: [{name, pct}], losers: [...], asof}
- `flows` {days: [{date: "16 Nov", fii, dii}]} — newest last, up to 8
- `dividend` {company, amount "₹1", type "Interim", ex_date, record_date}
- `split` {company, from_fv "₹10", to_fv "₹1", ex_date}
- `bonus` {company, ratio "1:1", ex_date, record_date}
- `buyback` {company, size, price, method, record_date}
- `ipo` {company, open, close, band, size, lot, listing}
- `results` {company, period, metrics: [{label, value, prev, unit, chg}]} or upcoming {company, date, purpose}
- `calendar` {items: [{date: "18 Nov", company, what, type}]} — up to 6
- `gauge` {name, value, min, max, pct}
Every scene takes `source` (shown as a chip). Every video needs `sources`.

## Rules the build enforces (`engine/check.py`)
- News only. No buy/sell/hold, targets, stop-loss, ratings/upgrades/downgrades, predictions ("will rise"), upside/downside,
  support/resistance, bullish/bearish, IPO GMP or listing gains, "stocks to buy/watch", tips, crypto/forex trading promotion,
  inducements ("opportunity", "don't miss"). Write "buyback", never "buy-back".
- Every number in `say` and `scene` must exist in the feed snapshot (exact, or the same at the shown precision).
- `sources` must be listed for every video.
