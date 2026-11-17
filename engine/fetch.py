#!/usr/bin/env python3
"""Snapshot the public marketsamachar.in endpoints into one JSON file (runs on GitHub Actions).

  python3 engine/fetch.py feed/latest.json

Output: {"fetched_at": <IST iso>, "market_data": [...], "movers": {...}, "fii_dii": [...], "news_buzz": [...],
         "events": [...], "news": [...], "regulatory": [...], "briefs": [...]}
"""
import json, sys, time, datetime, urllib.request, pathlib

SITE = "https://www.marketsamachar.in"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def get(path):
    for attempt in range(3):
        try:
            req = urllib.request.Request(SITE + path, headers={"User-Agent": "marketsamachar-video/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            err = e; time.sleep(3)
    print(f"WARN {path}: {err}", file=sys.stderr)
    return None


def main(out):
    mm = get("/api/market-move") or {}
    ev = get("/api/events") or {}
    news = get("/api/news") or {}
    snap = {
        "fetched_at": datetime.datetime.now(IST).isoformat(timespec="seconds"),
        "market_data": get("/api/market-data") or [],
        "movers": mm.get("movers") or get("/api/stocks/movers") or {},
        "is_market_open": mm.get("isMarketOpen"),
        "fii_dii": mm.get("fiiDii") or [],
        "news_buzz": mm.get("newsBuzz") or [],
        "events": ev.get("events") or [],
        "news": news.get("items") or [],
        "regulatory": get("/api/regulatory") or [],
        "briefs": (get("/api/briefs") or {}).get("items") or [],
    }
    for e in snap["events"]:
        if isinstance(e.get("event_data"), str):
            try: e["event_data"] = json.loads(e["event_data"])
            except Exception: pass
    p = pathlib.Path(out); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(snap, indent=1, ensure_ascii=False))
    print(f"snapshot {out}: market_data={len(snap['market_data'])} events={len(snap['events'])} news={len(snap['news'])} "
          f"regulatory={len(snap['regulatory'])} fii_dii={len(snap['fii_dii'])} movers={len(snap['movers'].get('gainers', []))}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "feed/latest.json")
