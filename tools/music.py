"""Composes the channel's original background tracks (no third-party music, no licence issues).

MIDI is written with pretty_midi and rendered with FluidSynth + FluidR3_GM (MIT-licensed soundfont).
One track per daily style; each is ~150 s with intro / A / B / A' / B' / outro so loops don't feel repetitive.
Run once:  python3 tools/music.py assets/music      (needs: apt fluidsynth fluid-soundfont-gm, pip pretty_midi)
"""
import sys, random, pathlib, subprocess, tempfile
import pretty_midi as pm

SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
KICK, SNARE, CLAP, HAT, OHAT, SHAKER, RIDE, CRASH, TOM = 36, 38, 39, 42, 46, 70, 51, 49, 45
NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}


def chord(root, kind, octave=4):
    r = 12 * (octave + 1) + NOTE[root]
    iv = dict(maj=[0, 4, 7, 11], min=[0, 3, 7, 10], sus=[0, 5, 7, 10], add9=[0, 4, 7, 14], m9=[0, 3, 7, 14])[kind]
    return [r + i for i in iv]


TRACKS = {
    # name: bpm, progression A, progression B, instruments, drum feel
    "pulse":     dict(bpm=112, A=[("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "maj")], B=[("D", "min"), ("F", "maj"), ("A", "min"), ("G", "sus")],
                      pad=89, keys=81, bass=38, lead=82, feel="four"),
    "lofi":      dict(bpm=84, A=[("D", "m9"), ("G", "add9"), ("C", "maj"), ("A", "min")], B=[("F", "maj"), ("E", "min"), ("D", "m9"), ("G", "sus")],
                      pad=4, keys=4, bass=33, lead=11, feel="lofi"),
    "bright":    dict(bpm=120, A=[("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")], B=[("F", "maj"), ("G", "maj"), ("E", "min"), ("A", "min")],
                      pad=48, keys=0, bass=34, lead=12, feel="pop"),
    "cinematic": dict(bpm=96, A=[("E", "min"), ("C", "maj"), ("G", "maj"), ("D", "maj")], B=[("A", "min"), ("E", "min"), ("C", "maj"), ("D", "sus")],
                      pad=49, keys=46, bass=43, lead=48, feel="epic"),
    "funk":      dict(bpm=104, A=[("E", "min"), ("A", "sus"), ("E", "min"), ("G", "maj")], B=[("C", "maj"), ("D", "maj"), ("E", "min"), ("B", "min")],
                      pad=16, keys=7, bass=36, lead=61, feel="funk"),
    "marimba":   dict(bpm=100, A=[("F", "maj"), ("D", "min"), ("A#", "maj"), ("C", "maj")], B=[("G", "min"), ("A#", "maj"), ("F", "maj"), ("C", "sus")],
                      pad=89, keys=12, bass=32, lead=13, feel="shaker"),
}


def add(inst, p, s, d, v):
    inst.notes.append(pm.Note(velocity=max(1, min(127, int(v))), pitch=int(p), start=max(0, s), end=s + max(.03, d)))


def compose(name, cfg, seed, length=150):
    rnd = random.Random(seed)
    bpm = cfg["bpm"]; beat = 60 / bpm; bar = 4 * beat
    m = pm.PrettyMIDI(initial_tempo=bpm)
    pad = pm.Instrument(cfg["pad"]); keys = pm.Instrument(cfg["keys"]); bass = pm.Instrument(cfg["bass"])
    lead = pm.Instrument(cfg["lead"]); dr = pm.Instrument(0, is_drum=True)
    nbars = int(length / bar)
    # sections: intro 4 | A 8 | B 8 | A 8 | B 8 | ... | outro 4
    plan = ["I"] * 4
    while len(plan) < nbars - 4: plan += ["A"] * 8 + ["B"] * 8
    plan = plan[:nbars - 4] + ["O"] * 4
    motif = [rnd.choice([0, 2, 4, 7, 9, 12]) for _ in range(8)]
    hum = lambda: rnd.uniform(-.012, .012)
    for b, sec in enumerate(plan):
        t = b * bar
        prog = cfg["B"] if sec == "B" else cfg["A"]
        root, kind = prog[b % 4]
        c = chord(root, kind, 4 if cfg["feel"] != "epic" else 3)
        energy = dict(I=.55, A=.8, B=1.0, O=.5)[sec]
        # pad: whole bar, soft
        for n in c[:3]: add(pad, n, t, bar * .98, 38 * energy + 10)
        # keys pattern
        f = cfg["feel"]
        if f in ("four", "pop"):
            for k in range(8):
                if sec == "I" and k % 2: continue
                n = c[[0, 1, 2, 3, 2, 1, 2, 3][k]] + 12
                add(keys, n, t + k * beat / 2 + hum(), beat * .4, (62 if k % 2 == 0 else 50) * energy + 15)
        elif f == "lofi":
            for k, off in enumerate([0, 1.5, 2.5]):
                for n in c: add(keys, n, t + off * beat + k * .012 + hum(), beat * .9, 52 * energy + 10)
        elif f == "epic":
            for k in range(8): add(keys, c[k % 3] + 12, t + k * beat / 2 + hum(), beat * .45, 55 * energy + 15)
        elif f == "funk":
            for k in [0, 1.5, 2.25, 3, 3.5]:
                for n in c[1:]: add(keys, n + 12, t + k * beat + hum(), beat * .18, 62 * energy + 10)
        else:  # marimba
            for k in range(8):
                add(keys, c[[0, 2, 1, 2, 0, 3, 1, 2][k]] + 12, t + k * beat / 2 + hum(), beat * .35, 58 * energy + 12)
        # bass
        r = 12 * 2 + NOTE[root] + (12 if cfg["bass"] in (33, 34, 36) else 0)
        if f == "funk":
            for k, (o, dd) in enumerate([(0, .4), (.75, .2), (1.5, .3), (2, .2), (2.75, .2), (3.25, .4)]):
                add(bass, r + (12 if k == 3 else 0), t + o * beat + hum(), dd * beat, 88 * energy + 15)
        elif f == "lofi":
            add(bass, r, t, beat * 1.4, 80 * energy); add(bass, r + 7, t + 2.5 * beat, beat * .9, 70 * energy)
        elif f == "epic":
            for k in range(8): add(bass, r, t + k * beat / 2, beat * .4, (80 if k % 2 == 0 else 62) * energy)
        else:
            for k in range(4): add(bass, r + (7 if k == 3 and b % 2 else 0), t + k * beat + hum(), beat * .7, 82 * energy)
        # lead motif in B sections only (sparse, so it never fights the voice)
        if sec == "B" and b % 2 == 0:
            for k, iv in enumerate(motif[:4 if f != "pop" else 6]):
                add(lead, c[0] + 12 + iv, t + k * beat * .75 + hum(), beat * .5, 48)
        # drums
        if sec == "I" and b < 2: continue
        for k in range(16):
            s = t + k * beat / 4
            if f in ("four", "pop"):
                if k % 4 == 0: add(dr, KICK, s, .1, 100 * energy)
                if k in (4, 12): add(dr, CLAP if f == "pop" else SNARE, s, .1, 88 * energy)
                if k % 2 == 0: add(dr, HAT, s + hum(), .05, (60 if k % 4 else 45) * energy)
                if f == "four" and k % 4 == 2: add(dr, OHAT, s, .08, 48 * energy)
            elif f == "lofi":
                if k in (0, 7, 10): add(dr, KICK, s + .02, .1, 85 * energy)
                if k in (4, 12): add(dr, SNARE, s + .03, .1, 62 * energy)
                if k % 2 == 0: add(dr, HAT, s + (.025 if k % 4 else 0), .05, rnd.randint(30, 48) * energy)
            elif f == "epic":
                if k in (0, 6, 8, 11): add(dr, TOM, s, .2, 80 * energy)
                if k in (4, 12) and sec == "B": add(dr, SNARE, s, .1, 70)
                if k % 2 == 0: add(dr, SHAKER, s, .05, 35 * energy)
            elif f == "funk":
                if k in (0, 3, 10): add(dr, KICK, s, .1, 98 * energy)
                if k in (4, 12): add(dr, SNARE, s, .1, 92 * energy)
                add(dr, HAT, s + hum(), .04, (55 if k % 2 == 0 else 32) * energy)
            else:
                if k in (0, 8, 11): add(dr, KICK, s, .1, 80 * energy)
                if k in (4, 12): add(dr, CLAP, s, .1, 60 * energy)
                add(dr, SHAKER, s + hum(), .04, (45 if k % 2 == 0 else 28) * energy)
        if (b + 1) % 8 == 0 and sec in "AB":     # fill into next section
            for k in range(4): add(dr, TOM if f != "lofi" else SNARE, t + 3 * beat + k * beat / 4, .1, 70 + 6 * k)
        if b % 8 == 0 and sec in "AB": add(dr, CRASH, t, 1.0, 62)
    m.instruments += [pad, keys, bass, lead, dr]
    return m


def render(m, out_mp3):
    with tempfile.TemporaryDirectory() as td:
        mid = pathlib.Path(td, "t.mid"); wav = pathlib.Path(td, "t.wav")
        m.write(str(mid))
        subprocess.run(["fluidsynth", "-ni", "-g", "0.6", "-r", "44100", "-F", str(wav), SF2, str(mid)], check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af",
                        "acompressor=threshold=-18dB:ratio=3:attack=20:release=250,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st=146:d=4",
                        "-t", "150", "-ac", "2", "-b:a", "160k", str(out_mp3)], check=True)


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "assets/music"); out.mkdir(parents=True, exist_ok=True)
    for i, (name, cfg) in enumerate(TRACKS.items()):
        render(compose(name, cfg, 1000 + i), out / f"{name}.mp3"); print("made", name)
