"""Phase 3 — story-first episodes.

  episode.py pick <pair> [--format F] [--seed N]     → choose format / opening / look / motion / voices (no-repeat rules)
  episode.py build <episode.json> [--no-voice]       → voice every line, write out/<slug>/spec.js for page.html

An episode file (faceoff/episodes/<slug>.json) is written per video around ONE angle in the data:
  {"pair", "slug", "angle", "show", "format", "opening", "look", "motion",
   "voices": {"n": voice, "a": voice, "b": voice}, "hosts": {"n": {...}, "a": {"name","role","init"}, "b": {...}},
   "scenes": [{"type": hero|kinetic|duel|chartzoom|invest|mythfact|quiz|split|classic|cta,
               "tag", "title", "spec": {...}, "lines": [[speaker, text] | ["pause", seconds]]}]}
Every line (and pause) is a beat; scene specs refer to beats by index.
"""
import json, sys, re, random, hashlib, pathlib, argparse, datetime, os
ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
KDIR = pathlib.Path(os.environ.get("KOKORO_DIR", REPO))
FORMATS = {1: ["documentary", "bullbear", "quiz", "newsdesk"],      # single-stock deep dive
           2: ["documentary", "debate", "quiz", "newsdesk"],      # face-off
           3: ["panel", "countdown", "documentary", "quiz"]}      # three-stock industry round-up
OPENINGS = ["stat", "question", "invest", "chart"]
LOOKS = ["glass", "paper", "blueprint", "neon", "flat"]
MOTIONS = ["canvas", "cards", "split"]
VOICES = {"female": ["af_heart", "af_bella", "bf_emma"], "male": ["am_michael", "am_fenrir", "am_puck"]}
MUSIC = {"glass": "pulse", "paper": "marimba", "blueprint": "cinematic", "neon": "lofi", "flat": "bright"}
SPEED = {"documentary": 1.06, "debate": 1.1, "quiz": 1.08, "newsdesk": 1.16, "bullbear": 1.1, "panel": 1.1, "countdown": 1.12}
GAP = {"documentary": .34, "debate": .42, "quiz": .3, "newsdesk": .22, "bullbear": .4, "panel": .38, "countdown": .3}


def recent(hist, key, n):
    return [h.get(key) for h in hist[-n:] if h.get(key)]


def pick(args):
    hist = json.load(open(ROOT / "history.json")) if (ROOT / "history.json").exists() else []
    seed = args.seed if args.seed is not None else int(hashlib.md5(f"{args.pair}{datetime.datetime.now():%Y%m%d%H}".encode()).hexdigest(), 16) % 10**6
    rng = random.Random(seed)
    choose = lambda opts, key, n: rng.choice([o for o in opts if o not in recent(hist, key, n)] or opts)
    D = json.load(open(ROOT / "data" / f"{args.pair}.json"))
    ns = sum(1 for k in "abc" if k in D)
    fmt = args.format or choose(FORMATS[ns], "format", 3)
    out = dict(seed=seed, format=fmt, opening=choose(OPENINGS, "opening", 3), look=choose(LOOKS, "look", 3),
               motion=choose(MOTIONS, "motion", 1))
    lastv = set(recent(hist, "voice", 1)) | set((hist[-1].get("voices") or {}).values() if hist else [])
    fem = [v for v in VOICES["female"] if v not in lastv] or VOICES["female"]
    mal = [v for v in VOICES["male"] if v not in lastv] or VOICES["male"]
    if fmt == "debate":
        n = rng.choice(fem)
        out["voices"] = {"n": n, "a": rng.choice(mal), "b": rng.choice([v for v in VOICES["female"] if v != n])}
    elif fmt == "bullbear":   # Arjun argues the bull case, Meera the bear case, Priya moderates
        n = rng.choice(fem)
        out["voices"] = {"n": n, "a": rng.choice(mal), "b": rng.choice([v for v in VOICES["female"] if v != n])}
    elif fmt == "panel":      # one analyst per stock (Arjun, Meera, Kabir) + Priya moderating
        n = rng.choice(fem); a, c = rng.sample(mal, 2)
        out["voices"] = {"n": n, "a": a, "b": rng.choice([v for v in VOICES["female"] if v != n]), "c": c}
    else:
        out["voices"] = {"n": rng.choice(fem + mal)}
    out["stocks"] = ns
    print(json.dumps(out))


def envelope(a, sr):
    import numpy as np
    hop = sr // 30; n = len(a) // hop + 1
    rms = np.array([float(np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2))) if len(a[i * hop:(i + 1) * hop]) else 0 for i in range(n)])
    m = rms.max() or 1
    return [round(x / m, 2) for x in rms]


def build(args):
    ep = json.load(open(args.episode))
    D = json.load(open(ROOT / "data" / f"{ep['pair']}.json"))
    od = ROOT / "out" / ep["slug"]; od.mkdir(parents=True, exist_ok=True)
    fmt = ep["format"]; LEAD, TAIL = .8, .75
    if not args.no_voice:
        import numpy as np, soundfile as sf
        from kokoro_onnx import Kokoro
        K = Kokoro(str(KDIR / "kokoro-v1.0.onnx"), str(KDIR / "voices-v1.0.bin"))
    env = {}; t = 0.0; scenes = []
    for i, sc in enumerate(ep["scenes"]):
        cur = LEAD; beats = []; clips = []; said = []; prev = None
        for j, ln in enumerate(sc["lines"]):
            who, txt, opt = ln[0], ln[1], (ln[2] if len(ln) > 2 else {})
            if who == "pause":
                beats.append(round(cur, 3)); cur += float(txt); continue
            if prev and prev != who: cur += .15          # a beat of air when the speaker changes
            beats.append(round(cur, 3)); said.append(txt)
            if args.no_voice:
                d = len(txt.split()) / 2.7
            else:
                v = ep["voices"].get(who, ep["voices"]["n"])
                sp = txt.replace("P/E", "P E").replace("FY", "F Y ").replace("₹", " rupees ")
                a, sr = K.create(sp, voice=v, speed=SPEED[fmt] * (1.08 if v.startswith("am_") else 1), lang="en-gb" if v.startswith("b") else "en-us")
                a = np.asarray(a, dtype=np.float32); nz = np.where(np.abs(a) > .004)[0]; a = a[max(0, nz[0] - 240): nz[-1] + 1200]
                fn = f"v{i:02d}_{j}.wav"; sf.write(od / fn, a, sr); d = len(a) / sr; env[fn] = envelope(a, sr)
                clips.append([fn, round(cur, 3), round(d, 3), who, opt.get("g")])
            cur += d + GAP[fmt]; prev = who
        dur = max(cur - GAP[fmt] + TAIL + sc.get("hold", 0), 3.5 if sc["type"] != "cta" else 5.5)
        dur = round(dur * 30) / 30
        key = sc["spec"]["key"] if sc["type"] == "classic" else sc["type"]
        scenes.append(dict(key=key, type=sc["type"], tag=sc.get("tag", ""), title=sc.get("title", ""), spec=sc.get("spec", {}),
                           start=round(t, 4), dur=dur, beats=beats, clips=clips, said=said, num=None, part=None, result=None))
        t += dur
    # icons: every "icon" named anywhere in the episode, embedded as SVG (Lucide, ISC licence)
    names = set(re.findall(r'"icons?":\s*"([a-z0-9-]+)"', json.dumps(ep)))
    for m in re.findall(r'"icons":\s*\[([^\]]*)\]', json.dumps(ep)): names |= set(re.findall(r'"([a-z0-9-]+)"', m))
    idir = REPO / "node_modules" / "lucide-static" / "icons"
    icons = {n: (idir / f"{n}.svg").read_text().split("-->")[-1].strip() for n in names if (idir / f"{n}.svg").exists()}
    spec = dict(mode="episode", industry=ep.get("industry"), icons=icons, pair=ep["pair"], slug=ep["slug"], angle=ep.get("angle"), show=ep.get("show", "STOCK FACE-OFF"),
                format=fmt, opening=ep.get("opening"), look=ep["look"], motion=ep["motion"], music=MUSIC[ep["look"]],
                voices=ep["voices"], hosts=ep.get("hosts", {}), total=round(t, 4), scenes=scenes, var={}, env=env)
    (od / "spec.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False))
    (od / "spec.js").write_text("window.D=" + json.dumps(D, ensure_ascii=False) + ";window.V=" + json.dumps(spec, ensure_ascii=False) + ";")
    print(json.dumps(dict(slug=ep["slug"], total=round(t, 1), scenes=len(scenes), words=sum(len(" ".join(s["said"]).split()) for s in scenes))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd")
    p1 = sub.add_parser("pick"); p1.add_argument("pair"); p1.add_argument("--format"); p1.add_argument("--seed", type=int)
    p2 = sub.add_parser("build"); p2.add_argument("episode"); p2.add_argument("--no-voice", action="store_true")
    a = ap.parse_args()
    pick(a) if a.cmd == "pick" else build(a)
