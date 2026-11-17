"""Mix: Kokoro voices + a real music bed (assets/music/*.mp3, picked by seed, ducked under speech) + recorded SFX
(assets/sfx, Pixabay licence). No synthesised tones. All samples float32 mono @ 24 kHz."""
import subprocess, pathlib, random
import numpy as np

SR = 24000
BASE = pathlib.Path(__file__).resolve().parent.parent
SFX_DIR, MUSIC_DIR = BASE / "assets/sfx", BASE / "assets/music"
# cue -> takes (rotated so repeated cues don't sound identical), gain
SFX = {"whoosh": (["whoosh", "whoosh-short"], .55), "swish": (["whoosh-short"], .45), "big": (["whoosh-cinematic"], .5),
       "pop": (["pop"], .5), "ping": (["ping"], .4), "impact": (["impact-bass-1", "impact-bass-2"], .6), "sparkle": (["sparkle"], .45),
       "click": (["click"], .6), "type": (["typing"], .3), "key": (["key-press"], .4), "chime": (["chime"], .4),
       "notify": (["notification"], .4), "glitch": (["glitch-3"], .35), "riser": (["riser"], .4),
       # legacy names used by scenes
       "tick": (["click-soft"], .35), "coin": (["sparkle"], .4), "bell": (["chime"], .45), "ching": (["sparkle"], .4)}
_cache = {}


def load(path):
    if path not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        _cache[path] = np.frombuffer(raw, np.float32).copy()
    return _cache[path]


def music_bed(total, seed):
    tracks = sorted(MUSIC_DIR.glob("*.mp3")) + sorted(MUSIC_DIR.glob("*.m4a")) + sorted(MUSIC_DIR.glob("*.wav"))
    if not tracks: return None
    m = load(tracks[seed % len(tracks)]); n = int(total * SR)
    start = int(len(m) * random.Random(seed).uniform(0, .25)) if len(m) > n * 1.4 else 0
    out = np.zeros(n, np.float32); i = 0; src = m[start:]
    while i < n:
        k = min(n - i, len(src)); out[i:i + k] = src[:k]; i += k; src = m
    fi, fo = int(.6 * SR), int(2.2 * SR)
    out[:fi] *= np.linspace(0, 1, fi); out[-fo:] *= np.linspace(1, 0, fo)
    return out


def mix(total, voice_parts, sfx_parts, seed, music_gain=.30):
    N = int(total * SR) + SR
    v = np.zeros(N, np.float32)
    for at, a in voice_parts:
        i = int(at * SR); v[i:i + len(a)] += a[:max(0, N - i)]
    out = v.copy()
    bed = music_bed(total + 1, seed)
    if bed is not None:
        bed = np.pad(bed, (0, max(0, N - len(bed))))[:N]
        env = np.convolve((np.abs(v) > .02).astype(np.float32), np.ones(int(.35 * SR)) / (.35 * SR), "same")
        out += bed * (music_gain - (music_gain - .11) * np.clip(env * 2.5, 0, 1)).astype(np.float32)   # ~0.11 under the voice
    rot = {}
    for at, name, g in sfx_parts:
        takes, base = SFX.get(name, ([name], .4))
        k = rot.get(name, 0); rot[name] = k + 1
        f = SFX_DIR / f"{takes[k % len(takes)]}.mp3"
        if not f.exists(): continue
        sig = load(f); i = int((at + 1 / 30) * SR)        # sound lands one frame after the picture
        if i >= N: continue
        e = min(N, i + len(sig)); out[i:e] += base * g * sig[:e - i]
    peak = np.abs(out).max()
    return (out / max(1.0, peak / .89)).astype(np.float32)[:int(total * SR)]
