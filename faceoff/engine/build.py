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
            "roce": 3, "cash": 2, "asset": 1, "ownership": 3, "latest": 2}
MUSIC = {"glass": "pulse", "paper": "marimba", "blueprint": "cinematic", "neon": "lofi", "flat": "bright"}


NUM = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]
INTRO_LINE = {"rounds": "{n} rounds, one stat sheet. Let's get into the ring.",
              "case": "We'll make the case for each one, then put them head to head.",
              "timeline": "We'll go from {y0} to today, then look at what's next."}
THEN, NEXT = ["revenue", "profit", "roce"], ["latest", "risks"]


def content(D):
    """The script lives in the data file: [{key, title, lines, winner}] — winner is a / b / even / none, or absent for
    framing scenes. Lines must read well in any order (no 'next', 'after that'); structures add their own lead-ins."""
    return [dict(key=s["key"], title=s.get("title", ""), lines=list(s["lines"]), winner=s.get("winner")) for s in D["script"]]


def scenes_for(structure, D):
    a, b = D["a"], D["b"]
    sc = content(D)
    by = {s["key"]: s for s in sc}
    data_keys = [s["key"] for s in sc if s["winner"] is not None]
    mk = lambda s, **kw: {**dict(key=s["key"], title=s["title"], lines=list(s["lines"]), lead=None, result=None, num=None, part=None), **kw}
    if structure in INTRO_LINE and len(by["intro"]["lines"]) > 2:
        by["intro"]["lines"][2] = INTRO_LINE[structure].format(n=NUM[len(data_keys) - 1].capitalize(), y0="20" + D["years10"][0][2:])
    if structure == "case":
        parts = [("a", f"CASE FOR {a['tick']}", f"First, the case for {a.get('say', a['tick'])}."),
                 ("b", f"CASE FOR {b['tick']}", f"Now, the case for {b.get('say', b['tick'])}."),
                 (None, "HEAD TO HEAD", "Now, head to head.")]
        order = [mk(by["intro"])]
        for w, label, lead in parts:
            ks = [k for k in data_keys if (by[k]["winner"] == w if w else by[k]["winner"] not in ("a", "b"))]
            for n, k in enumerate(ks):
                order.append(mk(by[k], part=label)); order[-1]["lead"] = lead if n == 0 else None
        order += [mk(by["risks"], part="BOTH SIDES"), mk(by["summary"], part="CLOSING"), mk(by["cta"])]
        return order
    if structure == "timeline":
        now = [k for k in data_keys if k not in THEN + NEXT]
        groups = [("THEN", [k for k in THEN if k in by], f"Let's start with the long view, from 20{D['years10'][0][2:]}."),
                  ("NOW", now, "Fast forward to today."), ("NEXT", [k for k in NEXT if k in by], "So, what comes next?")]
        order = [mk(by["intro"])]
        for label, ks, lead in groups:
            for n, k in enumerate(ks):
                order.append(mk(by[k], part=label)); order[-1]["lead"] = lead if n == 0 else None
        order += [mk(by["summary"], part="WRAP"), mk(by["cta"])]
        return order
    out = []; r = 0
    for s0 in sc:
        s = mk(s0)
        if structure == "rounds":
            if s["key"] == "intro":
                s["title"] = "TALE OF THE TAPE"
            elif s0["winner"] is not None:
                r += 1; s["num"] = r; s["lead"] = f"Round {NUM[r - 1]}."; s["result"] = s0["winner"]
            elif s["key"] == "summary":
                s["title"] = "THE DECISION"; s["lead"] = "The judges' card? A split decision."
        elif s0["winner"] is not None or s["key"] in ("risks", "summary"):
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
    LEAD, GAP, TAIL = 0.85, 0.26, 0.75
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
                a, sr = Kk.create(sp, voice=voice, speed=1.21 if voice.startswith("am_") else 1.08, lang="en-gb" if voice.startswith("b") else "en-us")
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
