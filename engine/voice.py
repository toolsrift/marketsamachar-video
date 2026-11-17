"""Character voices — Kokoro (natural, offline, free). Each host has its own voice and pace.

say(host, text) -> (float32 mono samples @ 24 kHz, [(word, start_s, end_s), ...])
Each sentence is synthesised separately, so word timings (spread by length inside a sentence) stay close to speech.
"""
import re, json, hashlib, pathlib
import numpy as np

SR = 24000
BASE = pathlib.Path(__file__).resolve().parent.parent
CACHE = BASE / ".ttscache"
VOICES = {   # host: (kokoro voice, speed)
    "ghanti": ("am_michael", 1.04), "teji": ("am_puck", 1.08), "mandi": ("af_nicole", 1.0),
    "munshi": ("bm_george", 1.0), "bhonpu": ("am_fenrir", 1.06), "golu": ("af_bella", 1.05),
    "katli": ("af_sky", 1.04), "tohfa": ("af_nova", 1.06), "wapsi": ("am_echo", 1.05),
    "naya": ("af_aoede", 1.06), "tareekh": ("af_heart", 1.02), "desi": ("am_adam", 1.0),
    "videshi": ("bf_emma", 1.02), "arth": ("bm_lewis", .97), "narrator": ("af_heart", 1.03),
}
SAY_AS = {  # spoken spellings for Indian names and market words
    "MarketSamachar": "Market Samaachaar", "Market Samachar": "Market Samaachaar", "marketsamachar.in": "market samaachaar dot in",
    "Ghanti": "Ghun-tee", "Teji": "Tay-jee", "Mandi": "Mun-dee", "Munshi": "Moon-shee", "Bhonpu": "Bhonpoo", "Golu": "Go-loo",
    "Katli": "Kutlee", "Tohfa": "Toh-fa", "Wapsi": "Waapsee", "Naya": "Nuh-yaa", "Tareekh": "Ta-reekh", "Desi": "Day-see",
    "Videshi": "Vi-day-shee", "Arth": "Urth", "crore": "crore", "lakh": "lack", "Sensex": "Sensex", "Nifty": "Nifty",
    "FII": "F I I", "FIIs": "F I Is", "DII": "D I I", "DIIs": "D I Is", "FPI": "F P I", "IPO": "I P O", "IPOs": "I P Os",
    "QIP": "Q I P", "NSE": "N S E", "BSE": "B S E", "RBI": "R B I", "SEBI": "Sebi", "WPI": "W P I", "CPI": "C P I", "GDP": "G D P",
    "VIX": "vix", "YoY": "year on year", "QoQ": "quarter on quarter", "Q1": "Q one", "Q2": "Q two", "Q3": "Q three", "Q4": "Q four",
    "FY27": "F Y twenty-seven", "FY26": "F Y twenty-six", "VRRR": "V R R R", "LAF": "L A F", "AGM": "A G M", "EV": "E V",
}


def speakable(s):
    s = re.sub(r"₹\s?([\d,]+(?:\.\d+)?)\s?(crore|cr|lakh)\b", r"\1 \2 rupees", s)
    s = re.sub(r"₹\s?([\d,]+(?:\.\d+)?)", r"\1 rupees", s)
    s = re.sub(r"\bcr\b", "crore", s).replace("%", " percent").replace("&", " and ")
    s = re.sub(r"\b(\d+):(\d+)\b", r"\1 for \2", s)
    for k in sorted(SAY_AS, key=len, reverse=True):
        s = re.sub(rf"(?<![\w.]){re.escape(k)}(?![\w])", SAY_AS[k], s)
    return s


_K = None
def _kokoro():
    global _K
    if _K is None:
        from kokoro_onnx import Kokoro
        _K = Kokoro(str(BASE / "kokoro-v1.0.onnx"), str(BASE / "voices-v1.0.bin"))
    return _K


def _spread(text, t0, dur):
    ws = text.split(); wt = [len(w) + 2 + (3 if re.search(r"[,.!?;:]$", w) else 0) for w in ws]; tot = sum(wt) or 1
    out, c, span = [], t0 + .06, max(.1, dur - .14)
    for w, x in zip(ws, wt):
        d = span * x / tot; out.append((w, c, c + d)); c += d
    return out


def _trim(a, thr=.004):
    idx = np.where(np.abs(a) > thr)[0]
    return a[max(0, idx[0] - 240):idx[-1] + 480] if len(idx) else a


def say(host, text):
    v, sp = VOICES.get(host, VOICES["narrator"])
    CACHE.mkdir(exist_ok=True)
    key = hashlib.md5(f"kokoro2|{v}|{sp}|{text}".encode()).hexdigest()
    f, m = CACHE / f"{key}.npy", CACHE / f"{key}.json"
    if f.exists() and m.exists():
        return np.load(f), [tuple(w) for w in json.loads(m.read_text())]
    sents = [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x]
    parts, words, t = [], [], 0.0
    for s in sents:
        a, _ = _kokoro().create(speakable(s), voice=v, speed=sp, lang="en-gb" if v.startswith("b") else "en-us")
        a = _trim(a.astype(np.float32)); d = len(a) / SR
        words += _spread(s, t, d)
        gap = .22 if s.endswith((".", "!", "?")) else .12
        parts += [a, np.zeros(int(gap * SR), np.float32)]; t += d + gap
    a = np.concatenate(parts) if parts else np.zeros(SR // 2, np.float32)
    a = (a / max(1e-6, np.abs(a).max()) * .89).astype(np.float32)      # consistent loudness per line
    np.save(f, a); m.write_text(json.dumps(words))
    return a, words


def amps(a, start, fps=30, step=2):
    out = []
    for fr in range(0, int(len(a) / SR * fps), step):
        ch = a[int(fr / fps * SR):int((fr + step) / fps * SR)]
        out.append((start + fr / fps, float(np.sqrt(np.mean(ch ** 2))) if len(ch) else 0.0))
    out.append((start + len(a) / SR + .02, 0.0))
    return out
