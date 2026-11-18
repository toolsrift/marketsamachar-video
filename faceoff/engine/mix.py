"""mix.py <pair> [outname] — join rendered chunks and lay voice, music and SFX from spec.json."""
import sys, json, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
pair = sys.argv[1]; OD = ROOT / "out" / pair; spec = json.load(open(OD / "spec.json"))
name = sys.argv[2] if len(sys.argv) > 2 else f"{pair}_{spec['look']}_{spec['structure']}_{spec['motion']}.mp4"
AS = ROOT.parent / "assets"; total = spec["total"]
PALS = {"banking": dict(trans="whoosh-cinematic", pop="coin", stamp="vault"), "it": dict(trans="whoosh-short", pop="blip", stamp="blip-low"),
        "auto": dict(trans="tyre", pop="shift", stamp="rev")}
PAL = PALS.get(spec.get("industry"), dict(trans=None, pop="pop", stamp="impact-bass-1"))
MUSIC = {"banking": "cinematic", "it": "pulse", "auto": "bright"}
music = MUSIC.get(spec.get("industry"), spec["music"])
def sfx(n):
    w = ROOT / "sfx" / f"{n}.wav"
    return str(w) if w.exists() else str(AS / "sfx" / f"{n}.mp3")
ev = []
for i, s in enumerate(spec["scenes"]):
    st = s["start"]
    if i and PAL["trans"] and spec.get("mode") == "episode": ev.append((st + .05, PAL["trans"], .3))
    elif i: ev.append((st + .05, {"canvas": "whoosh", "cards": "whoosh-short", "split": "whoosh-cinematic"}[spec["motion"]] if spec["look"] != "neon" else "glitch-1", .35))
    if s["key"] == "intro": ev.append((st + .85, "impact-bass-1", .55))
    if spec.get("structure") == "rounds" and s.get("num") and s.get("result"): ev.append((st + .55, "ping", .5))
    if spec.get("structure") == "rounds" and s.get("result"): ev.append((st + s["dur"] - 2.05, "impact-bass-2", .35 if s["result"] != "none" else .2))
    if s["key"] == "summary": ev.append((st + s["beats"][-1] + .2, "chime", .4))
    if s["key"] == "cta": ev += [(st + 2.4, "click", .8), (st + 2.5, "sparkle", .4)]
    if spec.get("mode") == "episode":
        sp, b = s.get("spec", {}), s["beats"] or [0]
        B = lambda k: b[min(k or 0, len(b) - 1)]
        T = s["type"]
        if T == "hero": ev.append((st + B(sp["items"][0].get("beat")) + .1, PAL["stamp"], .5))
        if T == "mythfact": ev.append((st + B(sp.get("factBeat", 1)), PAL["stamp"], .5))
        if T == "quiz":
            cs, rv = st + B(sp.get("countBeat", 1)), st + B(sp.get("revealBeat", 2))
            ev += [(cs + k, "click-soft", .6) for k in range(int(sp.get("count", 3)))] + [(rv, "chime", .5)]
        if T == "chartzoom": ev += [(st + B(c["beat"]) + .1, "whoosh-short", .2) for c in sp.get("callouts", [])] + [(st + B(c["beat"]) + .45, PAL["pop"], .3) for c in sp.get("callouts", [])]
        if T == "invest": ev += [(st + B(sp.get("beatA", 1)) + .2, "riser2", .3), (st + B(sp.get("beatB", 2)) + .2, "riser2", .3)]
        if T == "duel": ev += [(st + B(r.get("beat")) + .05, PAL["pop"], .3) for r in sp.get("rows", [])]
        if T == "kinetic": ev += [(st + B(l.get("beat")), PAL["pop"], .25) for l in sp.get("lines", []) if l.get("icon")]
        if T == "split": ev += [(st + B(q.get("beat")) + .7 + k * .6, PAL["pop"], .22) for q in (sp.get("cols") or [sp[c] for c in "abc" if c in sp]) for k in range(len(q["rows"]))]
        if T == "podium": ev += [(st + B(x) + .05, "riser2", .25) for x in sp.get("revealBeats", [1, 2, 3])[:-1]] + [(st + B(sp.get("revealBeats", [1, 2, 3])[-1]) + .4, "chime", .5)]
        if T == "scorecard": ev += [(st + B(r.get("beat", 0)) + .3, PAL["pop"], .22) for r in sp.get("rows", [])]
        if T == "timeline": ev += [(st + B(x.get("beat", k + 1)), PAL["pop"], .3) for k, x in enumerate(sp.get("items", []))]
        if T == "table": ev += [(st + B(r.get("beat")) + .05, PAL["pop"], .3) for r in sp.get("rows", [])]
        if T == "vault": ev += [(st + B(sp.get(x, d)) + .2, "vault", .45) for x, d in (("beatA", 1), ("beatB", 2), ("beatC", 3)) if x[-1].lower() in sp] + [(st + B(sp.get(x, d)) + 1.8, "coin", .35) for x, d in (("beatA", 1), ("beatB", 2), ("beatC", 3)) if x[-1].lower() in sp]
        if T == "stacks": ev += [(st + B(sp.get(x, d)) + .2 + k * .3, "notes", .3) for x, d in (("beatA", 1), ("beatB", 2), ("beatC", 3)) if x[-1].lower() in sp for k in range(3)]
        if T == "racks": ev += [(st + B(sp.get(x, d)) + .2 + k * .12, "blip", .2) for x, d in (("beatA", 1), ("beatB", 2), ("beatC", 3)) if x[-1].lower() in sp for k in range(8)]
        if T in ("speedo", "race"): ev += [(st + B(sp.get("beatA", sp.get("beat", 1))) + .1, "rev", .45)]
voices = [(OD / c[0], s["start"] + c[1]) for s in spec["scenes"] for c in s["clips"]]
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(OD / "concat.txt"), "-c", "copy", str(OD / "video.mp4")], check=True)
inp = ["-i", str(OD / "video.mp4"), "-stream_loop", "-1", "-i", str(AS / "music" / f"{music}.mp3")]
# music level per scene: quieter under desk talk, fuller on data scenes, swell on the close; then ducked under every voice
lvl = []
for s_ in spec["scenes"]:
    g = .55 if s_.get("type") == "desk" else 1.25 if s_.get("type") in ("split", "cta") else 1.0
    lvl.append(f"between(t,{s_['start']:.2f},{s_['start'] + s_['dur']:.2f})*{g}")
vexpr = "0.16*(" + "+".join(lvl) + ")" if spec.get("mode") == "episode" else "0.11"
f = [f"[1:a]atrim=0:{total:.3f},aresample=48000,aformat=channel_layouts=stereo,volume='{vexpr}':eval=frame,afade=t=in:d=1,afade=t=out:st={total - 3:.3f}:d=3[m0]"]; k = 2
vl = []
for j, (fn, t) in enumerate(voices):
    inp += ["-i", str(fn)]; d = int(t * 1000); f.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.5,adelay={d}|{d}[v{j}]"); vl.append(f"[v{j}]"); k += 1
f.append("".join(vl) + f"amix=inputs={len(vl)}:normalize=0:duration=longest,apad,atrim=0:{total:.3f}[vb]")
f.append("[vb]asplit=2[vb1][vb2]")
f.append("[m0][vb1]sidechaincompress=threshold=0.015:ratio=9:attack=20:release=450:makeup=1[m]")
lab = ["[m]", "[vb2]"]
for j, (t, n, vol) in enumerate(ev):
    inp += ["-i", sfx(n)]; d = int(t * 1000); f.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={d}|{d}[e{j}]"); lab.append(f"[e{j}]"); k += 1
f.append("".join(lab) + f"amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
(OD / "filter.txt").write_text(";".join(f))
out = OD / name
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inp, "-filter_complex_script", str(OD / "filter.txt"), "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(out)], check=True)
print(out, total)
