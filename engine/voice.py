"""Character voices: Microsoft Edge neural voices (Indian English, free, word timings) with Kokoro as offline fallback.

say(host, text) -> (float32 mono samples @ 24 kHz, [(word, start_s, end_s), ...])
"""
import re, json, hashlib, asyncio, pathlib, subprocess, tempfile
import numpy as np

SR = 24000
BASE = pathlib.Path(__file__).resolve().parent.parent
CACHE = BASE / ".ttscache"
# host -> (edge voice, rate, pitch, kokoro fallback voice, kokoro speed)
VOICES = {
    "munshi":  ("en-IN-PrabhatNeural", "+0%", "-6Hz", "bm_george", 1.0),
    "bhonpu":  ("en-IN-PrabhatNeural", "+8%", "+4Hz", "am_puck", 1.12),
    "golu":    ("en-IN-NeerjaExpressiveNeural", "+6%", "+18Hz", "af_bella", 1.08),
    "katli":   ("en-IN-NeerjaNeural", "+4%", "+10Hz", "af_nicole", 1.05),
    "tohfa":   ("en-IN-NeerjaExpressiveNeural", "+8%", "+6Hz", "af_heart", 1.1),
    "wapsi":   ("en-IN-PrabhatNeural", "+10%", "+12Hz", "am_puck", 1.12),
    "naya":    ("en-IN-NeerjaExpressiveNeural", "+10%", "+22Hz", "af_sky", 1.12),
    "tareekh": ("en-IN-NeerjaNeural", "+0%", "+0Hz", "af_heart", 1.02),
    "ghanti":  ("en-IN-PrabhatNeural", "+4%", "+0Hz", "am_michael", 1.05),
    "teji":    ("en-IN-PrabhatNeural", "+12%", "+10Hz", "am_puck", 1.12),
    "mandi":   ("en-IN-NeerjaNeural", "+6%", "-4Hz", "af_nicole", 1.05),
    "desi":    ("en-IN-PrabhatNeural", "+2%", "-2Hz", "am_michael", 1.02),
    "videshi": ("en-IN-NeerjaNeural", "+4%", "+6Hz", "bf_emma", 1.04),
    "arth":    ("en-IN-PrabhatNeural", "-6%", "-14Hz", "bm_george", .95),
    "narrator":("en-IN-NeerjaNeural", "+2%", "+0Hz", "af_heart", 1.05),
}
KEEP = {"NIFTY", "SENSEX", "VIX", "SEBI", "NASA", "OPEC", "ITC", "RBI"}


def speakable(s):
    s = re.sub(r"₹\s?([\d,]+(?:\.\d+)?)\s?(crore|cr|lakh)\b", r"\1 \2 rupees", s)
    s = re.sub(r"₹\s?([\d,]+(?:\.\d+)?)", r"\1 rupees", s)
    s = re.sub(r"\bcr\b", "crore", s).replace("%", " percent").replace("&", " and ")
    s = re.sub(r"\b(\d+):(\d+)\b", r"\1 for \2", s)          # bonus 1:1 -> "1 for 1"
    s = re.sub(r"\bQ([1-4])\b", r"Q\1", s)
    return s


def _edge(text, voice, rate, pitch, mp3):
    import edge_tts
    async def go():
        c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
        words = []
        with open(mp3, "wb") as f:
            async for ch in c.stream():
                if ch["type"] == "audio": f.write(ch["data"])
                elif ch["type"] == "WordBoundary":
                    words.append((ch["text"], ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7))
        return words
    return asyncio.run(go())


def _kokoro(text, v, sp):
    from kokoro_onnx import Kokoro
    k = Kokoro(str(BASE / "kokoro-v1.0.onnx"), str(BASE / "voices-v1.0.bin"))
    a, _ = k.create(text, voice=v, speed=sp, lang="en-us")
    return a.astype(np.float32)


def _decode(mp3):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def _spread(text, dur):
    ws = text.split(); wt = [len(w) + 2 + (3 if re.search(r"[,.!?;:]$", w) else 0) for w in ws]; tot = sum(wt) or 1
    out, c = [], .05
    for w, x in zip(ws, wt):
        d = (dur - .1) * x / tot; out.append((w, c, c + d)); c += d
    return out


def _align(display, spoken_words, dur):
    """Map edge word timings (spoken form) back onto the display words for captions."""
    disp = display.split()
    if not spoken_words: return _spread(display, dur)
    if len(spoken_words) == len(disp):
        return [(d, s, e) for d, (_, s, e) in zip(disp, spoken_words)]
    # different tokenisation (₹, %, ratios): spread display words over the spoken timeline proportionally
    t0, t1 = spoken_words[0][1], spoken_words[-1][2]
    return [(w, t0 + (s - .05) * (t1 - t0) / max(.1, dur - .1), t0 + (e - .05) * (t1 - t0) / max(.1, dur - .1)) for w, s, e in _spread(display, dur)]


def say(host, text):
    voice, rate, pitch, kv, ksp = VOICES.get(host, VOICES["narrator"])
    spoken = speakable(text).replace("MarketSamachar", "Market Samachar").replace("Market Samachar", "Market Samaachaar")
    CACHE.mkdir(exist_ok=True)
    key = hashlib.md5(f"{voice}|{rate}|{pitch}|{spoken}".encode()).hexdigest()
    wav, meta = CACHE / f"{key}.npy", CACHE / f"{key}.json"
    if wav.exists() and meta.exists():
        return np.load(wav), [tuple(w) for w in json.loads(meta.read_text())]
    try:
        with tempfile.TemporaryDirectory() as td:
            mp3 = pathlib.Path(td) / "v.mp3"
            sw = _edge(spoken, voice, rate, pitch, mp3)
            a = _decode(mp3)
        words = _align(text, sw, len(a) / SR)
    except Exception as e:
        print(f"edge-tts unavailable ({type(e).__name__}); using Kokoro for {host}")
        a = _kokoro(spoken, kv, ksp); words = _spread(text, len(a) / SR)
    np.save(wav, a); meta.write_text(json.dumps(words))
    return a, words


def amps(a, start, fps=30, step=2):
    """RMS envelope every `step` frames, for mouth animation."""
    out = []
    for f in range(0, int(len(a) / SR * fps), step):
        ch = a[int(f / fps * SR):int((f + step) / fps * SR)]
        out.append((start + f / fps, float(np.sqrt(np.mean(ch ** 2))) if len(ch) else 0.0))
    out.append((start + len(a) / SR + .02, 0.0))
    return out
