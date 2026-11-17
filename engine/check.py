"""Pre-render gate: SEBI/RBI-safe wording + every number traceable to the feed snapshot + sources on every video.

problems(job, feed) -> (errors, warnings). The build refuses to render while errors exist.
"""
import re, json

HARD = [
    (r"\b(buy|sell|hold|accumulate|book profits?)\b(?! (?:rating|call))", "advice verb"),
    (r"\btarget (price|of)\b|\bprice target\b|\btp\b", "target price"),
    (r"\bstop[- ]?loss\b", "stop loss"),
    (r"\b(should|must|can|could) (you )?(invest|buy|sell|enter|exit|add)\b", "advice"),
    (r"\brecommend", "recommendation"),
    (r"\b(upgrade|downgrade)[sd]?\b|\b(overweight|underweight|outperform|underperform) rating\b|\brating\b", "brokerage rating"),
    (r"\bmultibagger|\bjackpot|\bsure[- ]shot|\bguarantee", "performance claim"),
    (r"\b(will|could|may|might|likely to|set to|poised to|expected to|going to) (rise|fall|rally|crash|jump|surge|soar|slump|go up|go down|hit|touch|cross|double|recover|bounce)\b", "prediction"),
    (r"\b(upside|downside)\b", "upside/downside"),
    (r"\bsupport (level|zone)\b|\bresistance\b|\bbreakout\b", "technical levels"),
    (r"\bbullish\b|\bbearish\b", "bull/bear labels (use positive/negative)"),
    (r"\bgrey market\b|\bGMP\b|\blisting gains?\b|\bexpected listing\b", "IPO grey market"),
    (r"\bstocks? to (buy|sell|watch)\b|\btrading (idea|tip|call)s?\b|\btips?\b", "tips"),
    (r"\b(forex|crypto|bitcoin) (trading|app|platform)s?\b", "forex/crypto promotion (RBI)"),
    (r"\bopportunity\b|\bdon'?t miss\b|\bact now\b", "inducement"),
]
SOFT = [r"\boutlook\b", r"\bforecast\b", r"\bpredict", r"\bexpect"]
OK_NUM = {"50", "100", "500", "30", "250", "150"}       # index names (Nifty 50 etc.)


def _texts(v):
    out = [("title", v.get("title", "")), ("hook", v.get("hook", "")), ("description", v.get("description", "")), ("caption", v.get("caption", ""))]
    for i, b in enumerate(v.get("beats", [])):
        out.append((f"beat{i}.say", b.get("say", "")))
        out.append((f"beat{i}.scene", json.dumps(b.get("scene", {}), ensure_ascii=False)))
    for si, s in enumerate(v.get("segments", [])):
        for i, b in enumerate(s.get("beats", [])):
            out.append((f"seg{si}.beat{i}.say", b.get("say", "")))
            out.append((f"seg{si}.beat{i}.scene", json.dumps(b.get("scene", {}), ensure_ascii=False)))
    return out


def feed_numbers(feed):
    nums = set()
    def walk(x):
        if isinstance(x, bool): return
        if isinstance(x, (int, float)): nums.add(float(x)); return
        if isinstance(x, str):
            for m in re.findall(r"-?\d[\d,]*\.?\d*", x):
                try: nums.add(float(m.replace(",", "")))
                except ValueError: pass
            return
        if isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(feed); return nums


def _num_ok(val, txt, nums):
    if txt in OK_NUM or 2000 <= val <= 2100: return True
    dec = len(txt.split(".")[1]) if "." in txt else 0
    for n in nums:
        if abs(abs(n) - abs(val)) <= .5 * 10 ** -dec + 1e-9: return True        # same number at the shown precision
        if dec == 0 and abs(val) >= 1000 and abs(abs(n) - abs(val)) / abs(val) < .002: return True
    return False


def numbers_in(text):
    out = []
    for m in re.finditer(r"(?<![\w.])(-?\d[\d,]*(?:\.\d+)?)(\s?%|\s?(?:cr|crore|lakh|points|pts))?", text):
        raw = m.group(1).replace(",", "")
        try: val = float(raw)
        except ValueError: continue
        unit = (m.group(2) or "").strip()
        before = text[max(0, m.start() - 1):m.start()]
        if not unit and before not in ("₹", "$") and abs(val) < 32 and "." not in raw: continue   # dates, ratios, counts
        out.append((val, raw))
    return out


def problems(job, feed):
    errs, warns = [], []
    nums = feed_numbers(feed) if feed else set()
    for v in job.get("videos", []):
        vid = v.get("id", "?")
        if not v.get("sources"): errs.append(f"{vid}: no sources listed")
        for where, t in _texts(v):
            for pat, why in HARD:
                m = re.search(pat, t or "", re.I)
                if m: errs.append(f'{vid}.{where}: {why} — "{m.group(0)}"')
            for pat in SOFT:
                m = re.search(pat, t or "", re.I)
                if m: warns.append(f'{vid}.{where}: check wording — "{m.group(0)}"')
            if nums and where not in ("title", "description", "caption"):
                for val, raw in numbers_in(t or ""):
                    if not _num_ok(val, raw, nums): errs.append(f'{vid}.{where}: number {raw} not found in the feed')
    return errs, warns
