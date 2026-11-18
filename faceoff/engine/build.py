"""MarketSamachar stock face-off builder.

build.py <pair> [--look L] [--structure S] [--motion M] [--seed N] [--no-voice]
Picks a look / story structure / motion set (never repeating the previous video's look or structure),
picks one chart variant per scene, writes the narration, generates Kokoro voice per sentence,
and writes out/<pair>/spec.js for page.html.
"""
import json, sys, random, hashlib, pathlib, argparse, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent          # faceoff/
REPO = ROOT.parent                                               # repo root (assets, node_modules, Kokoro model)
import os
KDIR = pathlib.Path(os.environ.get("KOKORO_DIR", REPO))
LOOKS = ["glass", "paper", "blueprint", "neon", "flat"]
STRUCTURES = ["chapters", "rounds", "case", "timeline"]
MOTIONS = ["canvas", "cards", "split"]
VOICES = ["af_heart", "af_bella", "bf_emma", "am_michael"]
VARIANTS = {"size": 3, "returns": 3, "valuation": 3, "revenue": 3, "profit": 3, "quarterly": 3,
            "roce": 3, "cash": 2, "ownership": 3, "latest": 2}
MUSIC = {"glass": "pulse", "paper": "marimba", "blueprint": "cinematic", "neon": "lofi", "flat": "bright"}


def L(v):  # lakh crore, spoken
    return f"{v / 1e5:.1f} lakh crore"


def K(v):
    return f"{round(v / 1e3)} thousand crore"


def content(D):
    a, b = D["a"], D["b"]
    return [
        ("intro", "THE FACE-OFF", [
            f"{a['tick']} and Infosys. India's two largest IT services companies.",
            f"Together they're worth over {(a['mcap'] + b['mcap']) / 1e5:.1f} lakh crore rupees, and both have fallen more than 20 percent in the last year.",
            "So how do they really compare? Let's go through the numbers, one by one."], None),
        ("size", "SIZE", [
            f"Start with size. TCS has a market cap of {L(a['mcap'])}. Infosys, {L(b['mcap'])}.",
            f"TCS also earns about {a['sales10'][-1] / 1e5:.2f} lakh crore in yearly revenue, around {a['sales10'][-1] / b['sales10'][-1]:.1f} times Infosys."], "a"),
        ("returns", "SHARE PRICE", [
            "Now the share price. It's been a tough stretch for both.",
            f"Over one year, TCS is down {-a['ret']['1Y']} percent, and Infosys {-b['ret']['1Y']} percent.",
            f"Even over five years, both have returned around minus 7 to minus 8 percent a year.",
            f"Only the ten-year view is positive: about {a['ret']['10Y']} percent a year for TCS, and {b['ret']['10Y']} for Infosys.",
            f"Today, TCS trades {round((1 - a['price'] / a['high']) * 100)} percent below its 52-week high. Infosys, {round((1 - b['price'] / b['high']) * 100)} percent below."], "even"),
        ("valuation", "VALUATION", [
            "After that fall, here's what you pay for each.",
            f"TCS trades at {a['pe']} times earnings. Infosys, at {b['pe']}.",
            f"On book value, TCS is at {a['pb']:.1f} times, Infosys at {b['pb']:.1f}.",
            f"And Infosys pays a higher dividend yield: {b['dy']:.1f} percent, versus {a['dy']:.1f} for TCS."], "b"),
        ("revenue", "REVENUE GROWTH", [
            f"Next, growth. Since financial year 2017, TCS grew revenue from {a['sales10'][0] / 1e5:.2f} lakh crore to {a['sales10'][-1] / 1e5:.2f} lakh crore.",
            f"Infosys grew faster, from {K(b['sales10'][0])} to {b['sales10'][-1] / 1e5:.2f} lakh crore.",
            f"Over ten years, that's about {a['salesCagr10']} percent a year for TCS, and {b['salesCagr10']} for Infosys."], "b"),
        ("profit", "PROFIT GROWTH", [
            f"Profits followed a similar path. TCS earned {K(a['profit10'][-1])} last year. Infosys, {K(b['profit10'][-1])}.",
            f"Ten-year profit growth is about {a['profitCagr10']} percent a year for both."], "even"),
        ("quarterly", "LAST 8 QUARTERS", [
            "Zooming into the last eight quarters, both have kept revenue rising.",
            f"TCS reached {K(a['qSales'][-1])} in the September quarter. Infosys, {K(b['qSales'][-1])}.",
            "Operating margins are steady: around 26 to 27 percent for TCS, and 24 for Infosys."], "even"),
        ("roce", "EFFICIENCY", [
            "Now, efficiency. Return on capital employed shows how much profit each rupee in the business earns.",
            f"TCS has lifted it from {a['roce10'][0]} percent to {a['roce10'][-1]} percent over ten years.",
            f"Infosys improved too, from {b['roce10'][0]} to {b['roce10'][-1]} percent. Both are strong, but TCS is far ahead."], "a"),
        ("cash", "CASH & DIVIDENDS", [
            "Profits matter most when cash actually comes in.",
            f"Last year, TCS generated {K(a['cfo5'][-1])} in operating cash, more than its net profit.",
            f"Infosys generated {K(b['cfo5'][-1])}, also above its profit.",
            f"Both return most of it. TCS paid out {a['payout10'][-1]} percent of profit as dividends. Infosys, {b['payout10'][-1]} percent."], "even"),
        ("ownership", "WHO OWNS IT", [
            f"Who owns these companies? Tata Sons holds about {round(a['share']['prom'][-1])} percent of TCS, unchanged for two years.",
            f"Infosys promoters hold just {round(b['share']['prom'][-1])} percent. Domestic institutions, like mutual funds and insurers, own the biggest share, at nearly {round(b['share']['dii'][-1])} percent.",
            "One shared trend: foreign investors have been selling both, while domestic institutions keep buying."], "none"),
        ("latest", "LATEST QUARTER", [
            "Now, the latest quarter, July to September 2026.",
            f"TCS grew revenue {round(a['q2']['revYoy'])} percent and profit {round(a['q2']['npYoy'])} percent from a year ago, and signed 9.6 billion dollars of new deals.",
            f"Infosys grew revenue nearly {round(b['q2']['revYoy'])} percent and profit {round(b['q2']['npYoy'])} percent. Its large-deal wins hit 5.2 billion dollars.",
            "But Infosys also cut its full-year growth guidance, to 1 to 2 percent in constant currency."], "a"),
        ("risks", "STRENGTHS & WATCH-OUTS", [
            "So, what are the strengths, and what should you watch?",
            "TCS: top-tier return ratios, strong cash generation, and steady margins. The watch-outs: slower sales growth, and a high price to book.",
            "Infosys: a lower valuation, a higher dividend yield, and faster long-term growth. The watch-outs: the guidance cut, and low promoter holding."], None),
        ("summary", "THE SUMMARY", [
            "To sum up. TCS is the bigger, more efficient company, with a stable owner.",
            "Infosys is cheaper, pays a higher yield, and has grown a little faster.",
            "This is not a buy or sell call. Which one suits your style? Tell us in the comments."], None),
        ("cta", "", ["Follow Market Samachar for more stock face-offs. Full data on marketsamachar dot in."], None),
    ]


NUM = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]


ORDER = {
    "case": [("intro", None), ("size", "CASE FOR TCS"), ("roce", "CASE FOR TCS"), ("cash", "CASE FOR TCS"),
             ("valuation", "CASE FOR INFY"), ("revenue", "CASE FOR INFY"), ("profit", "CASE FOR INFY"),
             ("returns", "HEAD TO HEAD"), ("quarterly", "HEAD TO HEAD"), ("ownership", "HEAD TO HEAD"), ("latest", "HEAD TO HEAD"),
             ("risks", "BOTH SIDES"), ("summary", "CLOSING"), ("cta", None)],
    "timeline": [("intro", None), ("revenue", "THEN"), ("profit", "THEN"), ("roce", "THEN"),
                 ("size", "NOW"), ("returns", "NOW"), ("valuation", "NOW"), ("quarterly", "NOW"), ("cash", "NOW"), ("ownership", "NOW"),
                 ("latest", "NEXT"), ("risks", "NEXT"), ("summary", "WRAP"), ("cta", None)],
}
OVR = {
    "case": {("intro", 2): "We'll make the case for each one, then put them head to head.",
             ("size", 0): "First, the case for TCS. Start with size. TCS has a market cap of {am}. Infosys, {bm}.",
             ("valuation", 0): "Now, the case for Infosys. It starts with price: here's what you pay for each.",
             ("returns", 0): "Now, head to head. First, the share price. It's been a tough stretch for both."},
    "timeline": {("intro", 2): "We'll go from 2017 to today, and then look at what's next.",
                 ("revenue", 0): "Let's start in 2017. Since then, TCS grew revenue from {as0} lakh crore to {as9} lakh crore.",
                 ("size", 0): "Fast forward to today. TCS has a market cap of {am}. Infosys, {bm}.",
                 ("returns", 0): "The share price, though, has had a tough stretch.",
                 ("valuation", 0): "After that fall, here's what you pay for each.",
                 ("latest", 0): "So what comes next? Start with the latest quarter, July to September 2026."},
}


def scenes_for(structure, D):
    a, b = D["a"], D["b"]
    fmt = dict(am=L(a["mcap"]), bm=L(b["mcap"]), as0=f"{a['sales10'][0] / 1e5:.2f}", as9=f"{a['sales10'][-1] / 1e5:.2f}")
    base = {k: (t, l, r) for k, t, l, r in content(D)}
    out = []; r = 0
    if structure in ORDER:
        for key, part in ORDER[structure]:
            title, lines, res = base[key]; lines = list(lines)
            for (k, j), txt in OVR[structure].items():
                if k == key: lines[j] = txt.format(**fmt)
            if key == "summary" and structure == "case": title = "THE CLOSING"
            out.append(dict(key=key, title=title, lines=lines, lead=None, result=None, num=None, part=part))
        return out
    for key, title, lines, res in content(D):
        s = dict(key=key, title=title, lines=list(lines), lead=None, result=None, num=None, part=None)
        if structure == "rounds":
            if key == "intro":
                s["title"] = "TALE OF THE TAPE"
                s["lines"][2] = "Ten rounds, one stat sheet. Let's get into the ring."
            elif res is not None:
                r += 1; s["num"] = r; s["lead"] = f"Round {NUM[r - 1]}."
                s["result"] = res
            elif key == "summary":
                s["title"] = "THE DECISION"
                s["lines"][0] = "The judges' card? A split decision. TCS is the bigger, more efficient company, with a stable owner."
        else:
            if res is not None or key in ("risks", "summary"):
                r += 1; s["num"] = r
        out.append(s)
    return out


def pick(pair, args, hist):
    seed = args.seed if args.seed is not None else int(hashlib.md5(f"{pair}{datetime.date.today()}".encode()).hexdigest(), 16) % 10**6
    rng = random.Random(seed)
    last = hist[-1] if hist else {}
    recent = hist[-2:]
    combos = [(l, s, m) for l in LOOKS for s in STRUCTURES for m in MOTIONS
              if all(l != h.get("look") for h in recent) and s != last.get("structure")]
    pref = [c for c in combos if c[2] != last.get("motion")] or combos
    look, structure, motion = rng.choice(pref)
    look = args.look or look; structure = args.structure or structure; motion = args.motion or motion
    var = {k: rng.randrange(n) for k, n in VARIANTS.items()}
    var["profit"] = rng.choice([x for x in range(VARIANTS["profit"]) if x != var["revenue"]])   # revenue and profit never share a chart form
    voice = rng.choice([v for v in VOICES if v != last.get("voice", "af_heart")])
    voice = args.voice or voice
    return seed, look, structure, motion, var, voice


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("pair"); ap.add_argument("--look"); ap.add_argument("--structure")
    ap.add_argument("--motion"); ap.add_argument("--seed", type=int); ap.add_argument("--no-voice", action="store_true")
    ap.add_argument("--fmt", default="long"); ap.add_argument("--var"); ap.add_argument("--voice"); ap.add_argument("--out")
    args = ap.parse_args()
    D = json.load(open(ROOT / "data" / f"{args.pair}.json"))
    hpath = ROOT / "history.json"; hist = json.load(open(hpath)) if hpath.exists() else []
    seed, look, structure, motion, var, voice = pick(args.pair, args, hist)
    if args.var: var.update(json.loads(args.var))
    sc = scenes_for(structure, D)
    od = pathlib.Path(args.out) if args.out else ROOT / "out" / args.pair; od.mkdir(parents=True, exist_ok=True)
    LEAD, GAP, TAIL = 0.95, 0.28, 0.9
    if not args.no_voice:
        import numpy as np, soundfile as sf
        from kokoro_onnx import Kokoro
        Kk = Kokoro(str(KDIR / "kokoro-v1.0.onnx"), str(KDIR / "voices-v1.0.bin"))
    t = 0.0
    for i, s in enumerate(sc):
        lines = ([s["lead"]] if s["lead"] else []) + s["lines"]
        cur = LEAD; beats = []; clips = []
        for j, ln in enumerate(lines):
            if args.no_voice:
                d = len(ln.split()) / 2.7
            else:
                sp = ln.replace("P/E", "P E").replace("FY", "F Y ")
                a, sr = Kk.create(sp, voice=voice, speed=1.08, lang="en-gb" if voice.startswith("b") else "en-us")
                a = np.asarray(a, dtype=np.float32); nz = np.where(np.abs(a) > .004)[0]; a = a[max(0, nz[0] - 240): nz[-1] + 1200]
                fn = od / f"v{i:02d}_{j}.wav"; sf.write(fn, a, sr); d = len(a) / sr; clips.append((fn.name, cur))
            beats.append(round(cur, 3)); cur += d + GAP
        dur = max(cur - GAP + TAIL, 4.0 if s["key"] != "cta" else 5.5)
        dur = round(dur * 30) / 30
        s.update(dur=dur, start=round(t, 4), beats=beats[1:] if s["lead"] else beats, leadBeat=beats[0] if s["lead"] else None,
                 clips=clips, said=lines)
        t += dur
    spec = dict(pair=args.pair, seed=seed, look=look, structure=structure, motion=motion, var=var, music=MUSIC[look], voice=voice,
                total=round(t, 4), scenes=sc, fmt=args.fmt)
    (od / "spec.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False))
    (od / "spec.js").write_text("window.D=" + json.dumps(D, ensure_ascii=False) + ";window.V=" + json.dumps(spec, ensure_ascii=False) + ";")
    print(json.dumps(dict(seed=seed, look=look, structure=structure, motion=motion, var=var, voice=voice, total=round(t, 1),
                          words=sum(len(" ".join(s["said"]).split()) for s in sc)), indent=None))


if __name__ == "__main__":
    main()
