"""Generated music bed + sound effects (no samples, no licences). All functions return float32 @ 24 kHz."""
import numpy as np

SR = 24000
PROGS = [[(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (261.6, 329.6, 392.0), (196.0, 246.9, 293.7)],
         [(261.6, 329.6, 392.0), (196.0, 246.9, 293.7), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6)],
         [(293.7, 349.2, 440.0), (233.1, 293.7, 349.2), (261.6, 329.6, 392.0), (220.0, 277.2, 329.6)],
         [(164.8, 196.0, 246.9), (261.6, 329.6, 392.0), (196.0, 246.9, 293.7), (146.8, 185.0, 220.0)],
         [(196.0, 246.9, 293.7), (164.8, 196.0, 246.9), (130.8, 164.8, 196.0), (146.8, 185.0, 220.0)],
         [(233.1, 293.7, 349.2), (207.7, 261.6, 311.1), (174.6, 220.0, 261.6), (196.0, 246.9, 311.1)]]
GROOVES = [dict(bpm=104, timbre="pluck", kick=[1,0,0,0,1,0,0,0], snare=[0,0,1,0,0,0,1,0]),
           dict(bpm=112, timbre="sine", kick=[1,0,0,1,0,0,1,0], snare=[0,0,1,0,0,0,1,0]),
           dict(bpm=120, timbre="pluck", kick=[1,0,1,0,1,0,1,0], snare=[0,0,1,0,0,0,1,1]),
           dict(bpm=96, timbre="sine", kick=[1,0,0,0,0,0,1,0], snare=[0,0,0,0,1,0,0,0]),
           dict(bpm=126, timbre="square", kick=[1,0,0,0,1,0,0,0], snare=[0,0,1,0,0,0,1,0]),
           dict(bpm=100, timbre="saw", kick=[1,0,0,1,0,0,1,0], snare=[0,0,1,0,0,1,0,0])]


def tone(f, d, amp=.3, decay=6.0, timbre="sine"):
    t = np.arange(int(d * SR)) / SR; ph = 2 * np.pi * f * t
    if timbre == "square": w = np.sign(np.sin(ph)) * .5 + .2 * np.sin(ph)
    elif timbre == "saw": w = 2 * ((f * t) % 1) - 1
    elif timbre == "pluck": w = np.sin(ph) + .5 * np.sin(2 * ph) + .25 * np.sin(3 * ph)
    else: w = np.sin(ph)
    return (amp * w * np.exp(-t * decay)).astype(np.float32)


def bgm(total, seed):
    cfg = GROOVES[seed % len(GROOVES)]; prog = PROGS[(seed // 7) % len(PROGS)]
    n = int(total * SR); out = np.zeros(n + SR * 4, np.float32); step = 60 / cfg["bpm"] / 2
    rng = np.random.default_rng(seed)
    def add(sig, at):
        i = int(at * SR); e = min(len(out), i + len(sig)); out[i:e] += sig[:e - i]
    s = 0
    while s * step < total:
        t0 = s * step; bar = s // 8; chord = prog[bar % 4]; k8 = s % 8
        if cfg["kick"][k8]:
            tt = np.arange(int(.25 * SR)) / SR; add((.5 * np.sin(2 * np.pi * (48 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12)).astype(np.float32), t0)
        if cfg["snare"][k8]:
            nz = rng.standard_normal(int(.18 * SR)).astype(np.float32); add(.11 * nz * np.exp(-np.arange(len(nz)) / SR * 22), t0)
        if k8 % 2 == 1:
            hh = rng.standard_normal(int(.04 * SR)).astype(np.float32); hh = np.diff(hh, prepend=0) * np.exp(-np.arange(len(hh)) / SR * 80); add(.05 * hh, t0)
        if k8 == 0:
            d = step * 8; tt = np.arange(int(d * SR)) / SR; env = np.minimum(1, tt / .5) * np.minimum(1, (d - tt) / .7)
            add((sum(np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt) for f in chord) * env * .028).astype(np.float32), t0)
        if k8 in (0, 3, 6): add(tone(chord[0] / 2, step * 1.6, .2, 4, "sine"), t0)
        if k8 in (2, 5, 7) and (bar % 2 == 1 or cfg["timbre"] != "sine"):
            add(tone(chord[(k8 + bar) % 3] * 2, step * 1.2, .04 if cfg["timbre"] != "square" else .028, 8, cfg["timbre"]), t0)
        s += 1
    tail = np.linspace(1, 0, int(2.0 * SR)); out[max(0, n - len(tail)):n] *= tail[-min(n, len(tail)):]
    return out[:n]


def whoosh(d=.5, seed=1):
    rng = np.random.default_rng(seed); n = int(d * SR); x = rng.standard_normal(n).astype(np.float32)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2; y = np.zeros(n, np.float32); a = 0.0
    for i in range(n):
        c = .02 + .3 * (i / n); a += c * (x[i] - a); y[i] = a
    y = y - np.convolve(y, np.ones(40) / 40, "same"); return .6 * env * y / (np.abs(y).max() + 1e-6)


def ching():
    a = tone(1318, .6, .18, 5); b = np.pad(tone(1760, .5, .12, 5), (int(.05 * SR), 0)); b = np.pad(b, (0, max(0, len(a) - len(b))))[:len(a)]
    return a + b


def pop():
    t = np.arange(int(.18 * SR)) / SR; f = 900 * np.exp(-t * 25) + 300
    return (.35 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)).astype(np.float32)


def coin():
    return _sum(tone(2093, .35, .16, 9), np.pad(tone(2637, .3, .12, 9), (int(.06 * SR), 0)))


def _sum(*sigs):
    n = max(len(x) for x in sigs); out = np.zeros(n, np.float32)
    for x in sigs: out[:len(x)] += x
    return out


def bell():
    return _sum(tone(880, 1.6, .22, 2.2), tone(1760, 1.2, .08, 3), tone(2640, .8, .04, 4))


def tick():
    t = np.arange(int(.05 * SR)) / SR
    return (.25 * np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 90)).astype(np.float32)


def riser(d=1.0):
    t = np.arange(int(d * SR)) / SR; f = 200 + 900 * (t / d) ** 2
    return (.12 * np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d)).astype(np.float32)


SFX = dict(whoosh=lambda s=1: whoosh(.5, s), ching=lambda s=0: ching(), pop=lambda s=0: pop(), coin=lambda s=0: coin(),
           bell=lambda s=0: bell(), tick=lambda s=0: tick(), riser=lambda s=0: riser(1.0))


def mix(total, voice_parts, sfx_parts, seed, music_gain=.42):
    N = int(total * SR) + SR
    v = np.zeros(N, np.float32)
    for at, a in voice_parts:
        i = int(at * SR); v[i:i + len(a)] += a[:max(0, N - i)]
    m = bgm(total, seed)[:N]; m = np.pad(m, (0, max(0, N - len(m))))
    env = np.convolve((np.abs(v) > .01).astype(np.float32), np.ones(int(.3 * SR)) / (.3 * SR), "same")
    m *= (music_gain - .3 * np.clip(env * 3, 0, 1)).astype(np.float32)
    fx = np.zeros(N, np.float32)
    for at, name, g in sfx_parts:
        sig = SFX[name](int(at * 10)); i = int(at * SR); e = min(N, i + len(sig)); fx[i:e] += g * sig[:e - i]
    out = v + m + .6 * fx
    return (out / max(1.0, np.abs(out).max() / .95)).astype(np.float32)[:int(total * SR)]
