"""Synthesise industry sound effects (no samples, no licences) → faceoff/sfx/*.wav"""
import numpy as np, soundfile as sf, pathlib
SR = 48000; OUT = pathlib.Path(__file__).resolve().parent.parent / "sfx"; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(7)
t = lambda d: np.arange(int(SR * d)) / SR
def env(n, a=.003, r=.2):
    x = np.arange(n) / SR; return np.minimum(1, x / a) * np.exp(-x / r)
def lp(x, k=8):  # cheap low-pass
    return np.convolve(x, np.ones(k) / k, mode="same")
def norm(x, g=.8): return (x / (np.abs(x).max() + 1e-9) * g).astype(np.float32)
def save(name, x): sf.write(OUT / f"{name}.wav", norm(x), SR)

# banking
x = t(.6); save("coin", sum(np.sin(2 * np.pi * f * x) * env(len(x), .001, r) for f, r in [(2637, .18), (4186, .12), (5274, .08), (3322, .15)]))
x = t(.9); save("vault", np.sin(2 * np.pi * 52 * x) * env(len(x), .004, .25) + lp(rng.standard_normal(len(x)), 40) * env(len(x), .002, .08) * 2)
x = t(.35); save("notes", lp(rng.standard_normal(len(x)), 3) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 28 * x))) * env(len(x), .02, .12))
x = t(.12); save("tick", np.sin(2 * np.pi * 1800 * x) * env(len(x), .001, .015))
# IT
x = t(.09); save("blip", np.sign(np.sin(2 * np.pi * 1320 * x)) * env(len(x), .001, .03) * .5)
x = t(.14); save("blip-low", np.sign(np.sin(2 * np.pi * 660 * x)) * env(len(x), .001, .05) * .5)
k = np.zeros(int(SR * .7))
for i in range(9):
    s = int(SR * (i * .07 + rng.uniform(0, .02))); n = int(SR * .025); k[s:s + n] += rng.standard_normal(n) * env(n, .0005, .006)
save("keys", k)
x = t(1.2); save("hum", (np.sin(2 * np.pi * 110 * x) + .5 * np.sin(2 * np.pi * 220 * x)) * np.minimum(1, x / .2) * np.minimum(1, (1.2 - x) / .3) * .4)
# auto
x = t(1.4); f = 70 + 160 * (1 - np.exp(-x * 2.2)); ph = 2 * np.pi * np.cumsum(f) / SR
save("rev", lp(((ph / np.pi) % 2 - 1) + .4 * np.sin(2 * ph), 12) * np.minimum(1, x / .05) * np.minimum(1, (1.4 - x) / .25))
x = t(.3); save("shift", lp(rng.standard_normal(len(x)), 6) * env(len(x), .001, .03) + np.sin(2 * np.pi * 140 * x) * env(len(x), .001, .06))
x = t(.8); sw = np.sin(np.pi * x / .8) ** 2; save("tyre", lp(rng.standard_normal(len(x)), 5) * sw * .7)
# generic
x = t(1.6); save("riser2", np.sin(2 * np.pi * (200 + 500 * x ** 2) * x) * (x / 1.6) ** 2 * .6 + lp(rng.standard_normal(len(x)), 4) * (x / 1.6) ** 3 * .3)
print(sorted(p.name for p in OUT.iterdir()))
