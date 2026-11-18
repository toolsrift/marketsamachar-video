"""mix.py <pair> [outname] — join rendered chunks and lay voice, music and SFX from spec.json."""
import sys, json, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
pair = sys.argv[1]; OD = ROOT / "out" / pair; spec = json.load(open(OD / "spec.json"))
name = sys.argv[2] if len(sys.argv) > 2 else f"{pair}_{spec['look']}_{spec['structure']}_{spec['motion']}.mp4"
AS = ROOT.parent / "assets"; total = spec["total"]
ev = []
for i, s in enumerate(spec["scenes"]):
    st = s["start"]
    if i: ev.append((st + .05, {"canvas": "whoosh", "cards": "whoosh-short", "split": "whoosh-cinematic"}[spec["motion"]] if spec["look"] != "neon" else "glitch-1", .35))
    if s["key"] == "intro": ev.append((st + .85, "impact-bass-1", .55))
    if spec["structure"] == "rounds" and s.get("num") and s.get("result"): ev.append((st + .55, "ping", .5))
    if spec["structure"] == "rounds" and s.get("result"): ev.append((st + s["dur"] - 2.05, "impact-bass-2", .35 if s["result"] != "none" else .2))
    if s["key"] == "summary": ev.append((st + s["beats"][-1] + .2, "chime", .4))
    if s["key"] == "cta": ev += [(st + 2.4, "click", .8), (st + 2.5, "sparkle", .4)]
voices = [(OD / c[0], s["start"] + c[1]) for s in spec["scenes"] for c in s["clips"]]
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(OD / "concat.txt"), "-c", "copy", str(OD / "video.mp4")], check=True)
inp = ["-i", str(OD / "video.mp4"), "-stream_loop", "-1", "-i", str(AS / "music" / f"{spec['music']}.mp3")]
f = [f"[1:a]atrim=0:{total:.3f},volume=0.11,afade=t=in:d=1,afade=t=out:st={total - 3:.3f}:d=3[m]"]; lab = ["[m]"]; k = 2
# voice: one input per clip, delayed
for j, (fn, t) in enumerate(voices):
    inp += ["-i", str(fn)]; d = int(t * 1000); f.append(f"[{k}:a]aresample=48000,volume=1.5,adelay={d}|{d}[v{j}]"); lab.append(f"[v{j}]"); k += 1
for j, (t, n, vol) in enumerate(ev):
    inp += ["-i", str(AS / "sfx" / f"{n}.mp3")]; d = int(t * 1000); f.append(f"[{k}:a]aresample=48000,volume={vol},adelay={d}|{d}[e{j}]"); lab.append(f"[e{j}]"); k += 1
f.append("".join(lab) + f"amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
(OD / "filter.txt").write_text(";".join(f))
out = OD / name
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inp, "-filter_complex_script", str(OD / "filter.txt"), "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(out)], check=True)
print(out, total)
