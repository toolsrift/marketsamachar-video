#!/usr/bin/env python3
"""Check a job and build its HyperFrames projects.

  python3 engine/build.py jobs/<job>.json [--feed feed.json] [--out work] [--only <video id>] [--check-only]

Writes work/<id>/ (project) + work/<id>/meta.json, and work/manifest.json listing every video.
Exits with CHECK_FAILED and the list of problems if wording or numbers fail the gate.
"""
import sys, json, pathlib, argparse, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check

DISCLAIMER = ("Disclaimer: News and information only — not investment advice or a recommendation to buy, sell or hold any security. "
              "MarketSamachar is not registered with SEBI as an investment adviser or research analyst. Figures are from public sources "
              "(exchanges, RBI, news publishers) and may be delayed or provisional. Please consult a SEBI-registered adviser before investing. "
              "Full disclaimer: https://www.marketsamachar.in/disclaimer")


def ts(sec):
    sec = int(max(0, sec)); return f"{sec // 60}:{sec % 60:02d}"


def meta_for(v, info, date):
    src = list(dict.fromkeys(v.get("sources", [])))
    desc = [v.get("description", "").strip(), ""]
    if info.get("chapters"):
        desc += ["Chapters:", "0:00 Intro"] + [f"{ts(t)} {n}" for t, n in info["chapters"]] + [""]
    desc += ["Sources: " + ", ".join(src), "", "Live market news & events: https://www.marketsamachar.in", "", DISCLAIMER, "",
             " ".join(v.get("hashtags", ["#StockMarketIndia", "#Nifty", "#Sensex", "#ShareMarket", "#MarketSamachar"]))]
    caption = (v.get("caption", "").strip() + "\n\nSource: " + ", ".join(src) + "\nNews only, not investment advice.\nMore: marketsamachar.in\n\n"
               + " ".join(v.get("hashtags", ["#stockmarketindia", "#nifty", "#sensex", "#sharemarket", "#marketsamachar"])))
    title = v.get("title", "")[:100]
    if v["kind"] == "short" and "#shorts" not in title.lower() and len(title) < 92: title += " #Shorts"
    return dict(id=v["id"], kind=v["kind"], title=title, description="\n".join(desc).strip(), caption=caption.strip(),
                tags=v.get("tags", []), seconds=round(info["total"], 1), date=date,
                look=dict(background=info.get("background"), text=info.get("text"), transitions=info.get("transitions"), side=info.get("side")))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("job"); ap.add_argument("--feed"); ap.add_argument("--out", default="work")
    ap.add_argument("--only"); ap.add_argument("--style"); ap.add_argument("--check-only", action="store_true"); a = ap.parse_args()
    job = json.loads(pathlib.Path(a.job).read_text())
    feed = json.loads(pathlib.Path(a.feed).read_text()) if a.feed and pathlib.Path(a.feed).exists() else None
    errs, warns = check.problems(job, feed)
    for w in warns: print("WARN", w)
    if errs:
        print("CHECK_FAILED"); [print("ERROR", e) for e in errs]; sys.exit(2)
    print(f"CHECK_OK {len(job.get('videos', []))} videos")
    if a.check_only: return
    import world
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True); date = job.get("date") or datetime.date.today().isoformat()
    manifest = []
    for v in job["videos"]:
        if a.only and v["id"] != a.only: continue
        proj = out / v["id"]
        info = world.build(v, proj, date, job.get("ticker"), a.style or job.get("style"))
        m = meta_for(v, info, date); (proj / "meta.json").write_text(json.dumps(m, indent=1, ensure_ascii=False)); manifest.append(m)
        print(f"built {v['id']} ({v['kind']}) {info['total']:.1f}s · style={info.get('background')} music={info.get('text')} moves={info.get('transitions')}")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
