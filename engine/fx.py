"""Brand look + shared motion helpers (marketsamachar.in palette: #07070e, #0d0d1e, #00ff88, DM Sans / DM Mono, slab headings)."""
import re, json, html, math, random, pathlib, shutil

E = html.escape
BASE = pathlib.Path(__file__).resolve().parent.parent
NM = BASE / "node_modules"
C = dict(bg="#07070e", panel="#0d0d1e", line="#1d2238", green="#00ff88", red="#FF4D6D", amber="#F5B83D", blue="#38BDF8",
         violet="#7C6CF6", ink="#E8EAF0", sub="#8B93A7", dim="#4B5270")
FONTS = [("Slab", "@fontsource/alfa-slab-one/files/alfa-slab-one-latin-400-normal.woff2", "400"),
         ("Sans", "@fontsource/dm-sans/files/dm-sans-latin-800-normal.woff2", "800"),
         ("SansM", "@fontsource/dm-sans/files/dm-sans-latin-600-normal.woff2", "600"),
         ("Mono", "@fontsource/dm-mono/files/dm-mono-latin-500-normal.woff2", "500")]


def T(x): return f"{x:.3f}"


def setup(proj):
    """Copy gsap, fonts and logo into the HyperFrames project; return @font-face css."""
    proj = pathlib.Path(proj); (proj / "assets/fonts").mkdir(parents=True, exist_ok=True); (proj / "assets/lib").mkdir(parents=True, exist_ok=True)
    shutil.copy(NM / "gsap/dist/gsap.min.js", proj / "assets/lib/gsap.min.js")
    shutil.copy(BASE / "assets/logo-icon.png", proj / "assets/logo-icon.png")
    css = ""
    for fam, src, w in FONTS:
        shutil.copy(NM / src, proj / "assets/fonts" / pathlib.Path(src).name)
        css += f"@font-face{{font-family:{fam};font-weight:{w};src:url('assets/fonts/{pathlib.Path(src).name}')}}\n"
    # the alias names used inside the character SVGs
    css += ("@font-face{font-family:'Alfa Slab One';src:url('assets/fonts/alfa-slab-one-latin-400-normal.woff2')}"
            "@font-face{font-family:'DM Sans';font-weight:800;src:url('assets/fonts/dm-sans-latin-800-normal.woff2')}"
            "@font-face{font-family:'DM Mono';src:url('assets/fonts/dm-mono-latin-500-normal.woff2')}\n")
    return css


def icon(name, size, stroke, sw="2.4"):
    p = NM / "lucide-static/icons" / f"{name}.svg"
    s = p.read_text() if p.exists() else (NM / "lucide-static/icons/circle.svg").read_text()
    s = re.sub(r'width="\d+"', f'width="{size}"', s, count=1); s = re.sub(r'height="\d+"', f'height="{size}"', s, count=1)
    s = s.replace('stroke="currentColor"', f'stroke="{stroke}"').replace('stroke-width="2"', f'stroke-width="{sw}"')
    return re.sub(r"<!--.*?-->", "", s, flags=re.S).strip()


BASE_CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
#root{{position:relative;overflow:hidden;background:{C['bg']};font-family:Sans,'DM Sans',sans-serif;color:{C['ink']}}}
.ab{{position:absolute}}
.slab{{font-family:Slab,'Alfa Slab One',serif;letter-spacing:1px;line-height:1.02}}
.mono{{font-family:Mono,'DM Mono',monospace;font-variant-numeric:tabular-nums}}
.pnl{{position:absolute;background:linear-gradient(160deg,rgba(22,24,48,.92),rgba(13,13,30,.92));border:1.5px solid {C['line']};border-radius:26px;box-shadow:0 24px 60px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.05)}}
.glow{{box-shadow:0 0 0 1.5px rgba(0,255,136,.35),0 0 40px rgba(0,255,136,.18),0 24px 60px rgba(0,0,0,.45)}}
.chip{{display:inline-flex;align-items:center;gap:10px;font-family:Sans;font-weight:800;letter-spacing:3px;text-transform:uppercase;border-radius:999px;padding:8px 18px}}
.src{{display:inline-flex;align-items:center;gap:10px;font-family:SansM;font-weight:600;color:{C['sub']};background:rgba(255,255,255,.05);border:1px solid {C['line']};border-radius:12px;padding:7px 14px}}
.src b{{color:{C['ink']};font-family:Sans;font-weight:800}}
.w{{display:inline-block;will-change:transform}}
.acc{{color:{C['green']}}} .neg{{color:{C['red']}}}
.bub{{position:absolute;background:#F4F6FB;color:#0B0B16;font-family:Sans;font-weight:800;border-radius:30px;padding:20px 26px;line-height:1.22;box-shadow:0 18px 40px rgba(0,0,0,.4)}}
.bub .cw{{opacity:.28;display:inline-block}}
.bub:after{{content:"";position:absolute;width:30px;height:30px;background:#F4F6FB;transform:rotate(45deg)}}
.bub.tl:after{{left:46px;top:-12px}} .bub.tr:after{{right:46px;top:-12px}} .bub.bl:after{{left:46px;bottom:-12px}} .bub.br:after{{right:46px;bottom:-12px}}
.bub .who{{display:block;font-size:.55em;letter-spacing:3px;text-transform:uppercase;margin-bottom:6px}}
"""


# ---------------------------------------------------------------- animated backgrounds (seeded)
def background(kind, W, H, total, rnd, accent=C["green"]):
    js = []
    if kind == "grid":
        h = (f'<div class="ab" id="bgA" style="inset:-200px;background:linear-gradient(rgba(255,255,255,.035) 2px,transparent 2px) 0 0/90px 90px,'
             f'linear-gradient(90deg,rgba(255,255,255,.035) 2px,transparent 2px) 0 0/90px 90px"></div>'
             f'<div class="ab" style="left:{W * .15:.0f}px;top:{H * .05:.0f}px;width:{W * .9:.0f}px;height:{W * .9:.0f}px;border-radius:50%;background:radial-gradient(circle,{accent}22,transparent 65%)"></div>')
        js.append(f'tl.fromTo("#bgA",{{x:0,y:0}},{{x:-90,y:-90,duration:{T(total)},ease:"none"}},0)')
    elif kind == "radar":
        cx, cy = W * rnd.uniform(.2, .8), H * rnd.uniform(.2, .5); rings = ""
        for i in range(1, 9):
            r = i * max(W, H) * .11
            rings += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="none" stroke="{accent}" stroke-opacity="{.16 - i * .014:.3f}" stroke-width="2"/>'
        h = (f'<svg class="ab" style="left:0;top:0" width="{W}" height="{H}">{rings}'
             f'<circle id="bgP" cx="{cx:.0f}" cy="{cy:.0f}" r="40" fill="none" stroke="{accent}" stroke-width="4" opacity=".5"/></svg>')
        js.append(f'tl.fromTo("#bgP",{{attr:{{r:20}},opacity:.6}},{{attr:{{r:{max(W, H) * .9:.0f}}},opacity:0,duration:2.6,ease:"power1.out",repeat:{int(total / 2.6) + 1}}},0)')
    elif kind == "candles":
        cs = ""; x = -40; y = H * .62
        while x < W + 60:
            up = rnd.random() > .45; bh = rnd.uniform(30, 120); y += (-1 if up else 1) * rnd.uniform(4, 30); y = min(H * .9, max(H * .2, y))
            col = C["green"] if up else C["red"]
            cs += (f'<line x1="{x}" y1="{y - bh / 2 - 20:.0f}" x2="{x}" y2="{y + bh / 2 + 20:.0f}" stroke="{col}" stroke-opacity=".12" stroke-width="3"/>'
                   f'<rect x="{x - 9}" y="{y - bh / 2:.0f}" width="18" height="{bh:.0f}" rx="3" fill="{col}" fill-opacity=".11"/>')
            x += 44
        h = f'<svg class="ab" id="bgA" style="left:0;top:0" width="{W + 400}" height="{H}">{cs}</svg>'
        js.append(f'tl.fromTo("#bgA",{{x:0}},{{x:-300,duration:{T(total)},ease:"none"}},0)')
    elif kind == "dots":
        h = (f'<div class="ab" id="bgA" style="inset:-100px;background:radial-gradient(circle,rgba(255,255,255,.10) 1.6px,transparent 2.6px) 0 0/34px 34px"></div>'
             f'<div class="ab" id="bgS" style="left:-{W}px;top:0;width:{W * .6:.0f}px;height:{H}px;background:linear-gradient(90deg,transparent,{accent}14,transparent)"></div>')
        js.append(f'tl.fromTo("#bgS",{{x:0}},{{x:{W * 2.6:.0f},duration:4.5,ease:"none",repeat:{int(total / 4.5) + 1}}},0)')
    elif kind == "rain":
        cols = ""
        for i in range(int(W / 70)):
            digits = "".join(rnd.choice("0123456789.+-%") for _ in range(30))
            cols += (f'<div class="mono" style="position:absolute;left:{i * 70 + rnd.randint(0, 20)}px;top:{-rnd.randint(0, 900)}px;writing-mode:vertical-rl;'
                     f'font-size:22px;letter-spacing:10px;color:{accent};opacity:{rnd.uniform(.04, .1):.2f}">{digits}</div>')
        h = f'<div class="ab" id="bgA" style="left:0;top:0;width:{W}px;height:{H * 2}px">{cols}</div>'
        js.append(f'tl.fromTo("#bgA",{{y:-{H * .5:.0f}}},{{y:0,duration:{T(total)},ease:"none"}},0)')
    else:  # aurora
        h = "".join(f'<div class="ab" id="bgO{i}" style="left:{rnd.uniform(-.3, .7) * W:.0f}px;top:{rnd.uniform(-.2, .7) * H:.0f}px;width:{W * .8:.0f}px;height:{W * .8:.0f}px;'
                    f'border-radius:50%;background:radial-gradient(circle,{c}28,transparent 62%)"></div>' for i, c in enumerate((accent, C["violet"], C["blue"])))
        for i in range(3):
            js.append(f'tl.fromTo("#bgO{i}",{{x:0,y:0}},{{x:{rnd.uniform(-200, 200):.0f},y:{rnd.uniform(-160, 160):.0f},duration:{T(total)},ease:"sine.inOut"}},0)')
    vign = f'<div class="ab" style="inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 45%,rgba(0,0,0,.55))"></div>'
    return f'<div class="ab" style="inset:0;overflow:hidden">{h}{vign}</div>', js


BG_KINDS = ["grid", "radar", "candles", "dots", "rain", "aurora"]


# ---------------------------------------------------------------- text motion
def words(text, pid, cls=""):
    """*accent* words; returns (html, n)."""
    out, i = [], 0
    for tok in re.findall(r"\*[^*]+\*|\S+", text):
        acc = tok.startswith("*"); ws = tok.strip("*").split()
        spans = " ".join(f'<span id="{pid}-{i + j}" class="w{" acc" if acc else ""}">{E(w)}</span>' for j, w in enumerate(ws)); i += len(ws)
        out.append(spans)
    return " ".join(out), i


def words_in(pid, n, t, style, gap=.067):
    """Title entrances from the HyperFrames motion guide: land, then hold dead still."""
    if style == "blur":   # per word: blur 6px -> 0 and opacity, no translate
        return [f'tl.fromTo("#{pid}-{k}",{{opacity:0,filter:"blur(6px)"}},{{opacity:1,filter:"blur(0px)",duration:.14,ease:"power2.out"}},{T(t + k * gap)})' for k in range(n)]
    if style == "ink":    # per word from light grey to ink
        return [f'tl.fromTo("#{pid}-{k}",{{opacity:.18}},{{opacity:1,duration:.12,ease:"none"}},{T(t + k * .085)})' for k in range(n)]
    if style == "line":   # whole line blurs in
        return [f'tl.fromTo("#{pid}-{k}",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.18,ease:"power2.out"}},{T(t)})' for k in range(n)]
    return [f'tl.fromTo("#{pid}-{k}",{{opacity:0,y:28,filter:"blur(4px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:.42,ease:"expo.out"}},{T(t + k * .08)})' for k in range(n)]


TEXT_STYLES = ["blur", "ink", "line", "rise"]


def pop(js, sel, t, kind="up", d=.45):
    m = {"up": ('{opacity:0,y:50}', '{opacity:1,y:0'), "down": ('{opacity:0,y:-50}', '{opacity:1,y:0'),
         "left": ('{opacity:0,x:-80}', '{opacity:1,x:0'), "right": ('{opacity:0,x:80}', '{opacity:1,x:0'),
         "scale": ('{opacity:0,scale:.5,transformOrigin:"50% 50%"}', '{opacity:1,scale:1'),
         "flip": ('{opacity:0,rotationX:-90,transformOrigin:"50% 0%"}', '{opacity:1,rotationX:0'),
         "fade": ('{opacity:0}', '{opacity:1')}[kind]
    js.append(f'tl.fromTo("{sel}",{m[0]},{m[1]},duration:{d},ease:"back.out(1.7)"}},{T(t)})')


def counter(js, pre, el, value, t, dec=0, prefix="", suffix="", dur=1.2, var=[0]):
    var[0] += 1; v = f"K{var[0]}"; pre.append(f"const {v}={{v:0}};")
    js.append(f'tl.to({v},{{v:{abs(value)},duration:{dur},ease:"power2.out",onUpdate:()=>{{document.getElementById("{el}").textContent='
              f'{json.dumps(prefix)}+{v}.v.toLocaleString("en-IN",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})+{json.dumps(suffix)}}}}},{T(t)})')


def fmt(v, dec=2):
    neg = v < 0; v = abs(v); s = f"{v:.{dec}f}"; ip, _, fp = s.partition(".")
    if len(ip) > 3:
        head, tail = ip[:-3], ip[-3:]; ip = ",".join(re.findall(r"\d{1,2}(?=(?:\d{2})*$)", head)) + "," + tail
    return ("-" if neg else "") + ip + ("." + fp if fp else "")


def tone_col(v):
    return C["green"] if v > 0 else C["red"] if v < 0 else C["sub"]


def source_chip(names, pid, size=22):
    names = [n for n in names if n]
    return f'<span class="src" id="{pid}" style="font-size:{size}px">{icon("link", size, C["sub"], "2.2")}Source: <b>{E(" · ".join(names))}</b></span>'
