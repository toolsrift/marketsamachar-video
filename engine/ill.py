"""MarketSamachar illustration library: animated, data-carrying SVG scenes (viewBox 0 0 1200 800).

Each scene draws a lit stage, an illustrated object for the kind of update, and the real numbers built into it
(count-ups, charts, tags, source). Styling comes from CSS classes (styles.py), so one scene renders in every
daily look: glossy 3D stickers, comic ink, blueprint lines, neon, cut paper.

scene(kind, p, a, d, data) -> (svg_inner, js_lines, pre_lines, ev)    ev = dict(punch=[t], mood=[(t, up|down)], sfx=[(t, name, gain)])
"""
import math, re, json
from fx import E, T, fmt

W, H = 1200, 800


# ------------------------------------------------------------------ primitives
def R(x, y, w, h, rx=0, c="", extra=""): return f'<rect class="{c}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}"{extra}/>'
def C(cx, cy, r, c="", extra=""): return f'<circle class="{c}" cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"{extra}/>'
def EL(cx, cy, rx, ry, c="", extra=""): return f'<ellipse class="{c}" cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"{extra}/>'
def P(d, c="", extra=""): return f'<path class="{c}" d="{d}"{extra}/>'


def TX(x, y, s, size=40, c="tx", anchor="middle", extra="", font=""):
    fc = {"h": " h", "num": " num"}.get(font, "")
    return f'<text class="{c}{fc}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" style="font-size:{size}px"{extra}>{s}</text>'


def slab(shape, n, depth=14, steps=4):
    """Extruded 3D sticker: dark copies stacked down-right, then the lit front face. shape uses {c} for the class."""
    out = []
    kc = "kdk" if n == "dk" else ("kcoin" if n == "coin" else f"k{n}")
    fc = "dk" if n == "dk" else ("coin" if n == "coin" else f"f{n}")
    for k in range(steps, 0, -1):
        o = depth * k / steps
        out.append(f'<g transform="translate({o * .7:.1f} {o:.1f})">{shape.replace("{c}", f"{kc} {"kd s" if k == steps else "km"}")}</g>')
    out.append(shape.replace("{c}", f"{fc} s"))
    return "".join(out)


def wrap(text, n):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > n: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    return lines


def num(x):
    try: return float(str(x).replace(",", "").replace("₹", "").replace("%", "").replace("$", "").replace("+", "").strip())
    except (TypeError, ValueError): return None


def decs(x):
    m = re.search(r"\.(\d+)", str(x)); return len(m.group(1)) if m else 0


def rep(d, per): return max(1, int(d / per))


class K:
    """Collects js / counter vars / events for one scene."""
    n = [0]

    def __init__(self, p): self.p, self.js, self.pre, self.ev = p, [], [], dict(punch=[], mood=[], sfx=[])

    def add(self, s): self.js.append(s)

    def pop(self, sel, t, ox, oy, s0=.2, d=.55, ease="back.out(1.8)"):
        self.add(f'tl.fromTo("{sel}",{{scale:{s0},opacity:0,svgOrigin:"{ox:.0f} {oy:.0f}"}},{{scale:1,opacity:1,duration:{d},ease:"{ease}"}},{T(t)})')

    def rise(self, sel, t, ox, oy, d=.5):
        self.add(f'tl.fromTo("{sel}",{{scaleY:0,svgOrigin:"{ox:.0f} {oy:.0f}"}},{{scaleY:1,duration:{d},ease:"back.out(1.5)"}},{T(t)})')

    def fade(self, sel, t, d=.35, y=0):
        self.add(f'tl.fromTo("{sel}",{{opacity:0,y:{y}}},{{opacity:1,y:0,duration:{d},ease:"power2.out"}},{T(t)})')

    def draw(self, sel, t, d=1.0, ease="power2.inOut"):
        self.add(f'tl.fromTo("{sel}",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{d},ease:"{ease}"}},{T(t)})')

    def bob(self, sel, t, dur, amp=10, per=1.4):
        if dur > per: self.add(f'tl.fromTo("{sel}",{{y:0}},{{y:{-amp},duration:{per / 2:.2f},ease:"sine.inOut",repeat:{rep(dur, per / 2)},yoyo:true}},{T(t)})')

    def spin(self, sel, t, dur, ox, oy, deg=90):
        self.add(f'tl.fromTo("{sel}",{{rotation:0,svgOrigin:"{ox:.0f} {oy:.0f}"}},{{rotation:{deg},duration:{T(max(.5, dur))},ease:"none"}},{T(t)})')

    def count(self, el, value, t, dec=0, prefix="", suffix="", dur=1.3, start=0):
        K.n[0] += 1; v = f"Q{K.n[0]}"; self.pre.append(f"const {v}={{v:{start}}};")
        self.add(f'tl.fromTo({v},{{v:{start}}},{{v:{abs(value)},duration:{dur},ease:"power2.out",onUpdate:()=>{{document.getElementById("{el}").textContent='
                 f'{json.dumps(prefix)}+{v}.v.toLocaleString("en-IN",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})+{json.dumps(suffix)}}}}},{T(t)})')

    def sfx(self, t, name, g=.6): self.ev["sfx"].append((t, name, g))


def numtext(k, el_id, raw, t, prefix="", suffix="", dur=1.3, start_frac=0.0):
    """A count-up when the value is numeric, else the plain text. Returns the initial text for the element."""
    v = num(raw)
    if v is None: return E(f"{prefix}{raw}{suffix}")
    dec = decs(raw)
    k.count(el_id, v, t, dec, prefix, suffix, dur, start=round(abs(v) * start_frac, dec))
    return E(f"{prefix}{fmt(abs(v) * start_frac, dec)}{suffix}")


def stage(p, cx=600, cy=380, r=330, gy=720, gw=420):
    pts = [(-1.15, -.55), (1.12, -.62), (-1.25, .25), (1.22, .3), (-.7, -1.0), (.75, -.98), (-1.0, .85), (1.05, .8)]
    parts = "".join(f'<g id="{p}-pt{k}">{C(cx + fx * r, cy + fy * r * .9, 8 if k % 2 else 6, "pt")}</g>' for k, (fx, fy) in enumerate(pts))
    return (EL(cx, gy, gw, 26, "gs") + C(cx, cy, r, "bd", f' id="{p}-bd"') +
            f'<g id="{p}-rg1">{C(cx, cy, r * 1.1, "rg")}</g><g id="{p}-rg2">{C(cx, cy, r * .8, "rg rg2")}</g>' + parts)


def stage_js(k, a, d, cx=600, cy=380):
    p = k.p
    k.add(f'tl.fromTo("#{p}-bd",{{scale:0,svgOrigin:"{cx} {cy}"}},{{scale:1,duration:.6,ease:"back.out(1.4)"}},{T(a)})')
    k.spin(f"#{p}-rg1", a, d, cx, cy, 70); k.spin(f"#{p}-rg2", a, d, cx, cy, -100)
    for i in range(8):
        k.add(f'tl.fromTo("#{p}-pt{i}",{{y:0,opacity:0}},{{y:{-16 if i % 2 else 16},opacity:1,duration:{1.4 + (i % 3) * .3:.2f},ease:"sine.inOut",repeat:{rep(d, 1.5)},yoyo:true}},{T(a + .2 + i * .06)})')


def src_tag(p, text, x=40, y=740):
    if not text: return ""
    t = "Source: " + (" · ".join(text) if isinstance(text, list) else str(text))
    w = 22 + len(t) * 12.4
    return (f'<g id="{p}-src">{R(x, y - 34, w, 48, 24, "dk", " opacity=\".88\"")}'
            f'{TX(x + 22, y - 2, E(t), 22, "txs", "start")}</g>')


def src_js(k, a): k.fade(f"#{k.p}-src", a + .9, .4, 12)


def confetti(k, t, n=16, x0=200, x1=1000, seed=1):
    import random
    r = random.Random(seed); out = ""
    for i in range(n):
        x = r.uniform(x0, x1); c = r.choice(["f1", "f2", "f4", "f5", "acc"])
        out += f'<g id="{k.p}-cf{i}">{R(x, -30, 14, 24, 3, c + " s")}</g>'
        k.add(f'tl.fromTo("#{k.p}-cf{i}",{{y:0,rotation:0,opacity:1,svgOrigin:"{x:.0f} -20"}},{{y:{r.uniform(620, 820):.0f},rotation:{r.uniform(-540, 540):.0f},opacity:0,duration:{r.uniform(1.6, 2.4):.2f},ease:"power1.in"}},{T(t + r.uniform(0, .35))})')
    k.sfx(t, "sparkle", .5)
    return f'<g opacity="1">{out}</g>'


def chip(x, y, text, cls="up", w=None, h=60, size=32, tid=None, txt_cls="tchip"):
    w = w or (40 + len(text) * size * .62)
    idattr = f' id="{tid}"' if tid else ""
    return R(x - w / 2, y - h / 2, w, h, h / 2, f"{cls} s") + TX(x, y + size * .35, E(text), size, txt_cls, "middle", idattr, "num")


def arrow3d(x, y, up=True, s=1.0, n=None):
    n = n or ("up" if up else "dn")
    d = "M0,-90 L70,0 L28,0 L28,90 L-28,90 L-28,0 L-70,0 Z" if up else "M0,90 L70,0 L28,0 L28,-90 L-28,-90 L-28,0 L-70,0 Z"
    return f'<g transform="translate({x} {y}) scale({s})">{P(d, "kd s", " transform=\"translate(9 12)\" opacity=\".55\"")}{P(d, n + " s")}{P(d.split(" L28")[0] + " Z", "hi")}</g>'


# ================================================================== scenes
def sc_index(p, a, d, data):
    k = K(p); up = (num(data.get("pct")) or 0) >= 0; tone = "up" if up else "dn"
    pts = data.get("points") or []
    vals = [num(x["value"]) for x in pts if num(x.get("value")) is not None]
    mil = num(data.get("milestone"))
    svg = stage(p, 430, 380, 330, 715, 400)
    # board
    bx, by, bw, bh = 60, 130, 720, 500
    svg += f'<g id="{p}-board">{slab(R(bx, by, bw, bh, 30, "{c}"), "dk", 16, 4)}'
    gx0, gx1, gy0, gy1 = bx + 70, bx + bw - 60, by + 80, by + bh - 90
    svg += "".join(f'<line class="grid" x1="{gx0}" x2="{gx1}" y1="{gy0 + i * (gy1 - gy0) / 3:.0f}" y2="{gy0 + i * (gy1 - gy0) / 3:.0f}"/>' for i in range(4))
    svg += TX(bx + 34, by + 52, E(str(data.get("chart_label", "Daily close")).upper()), 22, "txs", "start")
    if len(vals) >= 2:
        lo, hi_ = min(vals + ([mil] if mil else [])), max(vals + ([mil] if mil else []))
        pad = (hi_ - lo) * .15 or 1; lo -= pad; hi_ += pad
        X = lambda i: gx0 + i * (gx1 - gx0) / (len(vals) - 1)
        Y = lambda v: gy1 - (v - lo) / (hi_ - lo) * (gy1 - gy0)
        line = "M" + " L".join(f"{X(i):.0f},{Y(v):.0f}" for i, v in enumerate(vals))
        area = line + f" L{X(len(vals) - 1):.0f},{gy1} L{gx0},{gy1} Z"
        if mil:
            my = Y(mil)
            svg += (f'<path id="{p}-mil" d="M{gx0 - 20},{my:.0f} L{gx1 + 20},{my:.0f}" pathLength="1" stroke-dasharray="1" '
                    f'style="stroke:var(--acc);stroke-width:4;fill:none"/>'
                    f'<g id="{p}-milt">{R(gx0 - 10, my - 50, 150, 40, 8, "acc")}{TX(gx0 + 65, my - 21, E(fmt(mil, 0)), 24, "", "middle", " style=\"fill:var(--bg)\"", "num")}</g>')
        svg += f'<path id="{p}-area" d="{area}" class="{tone}" opacity=".22"/>'
        svg += f'<path id="{p}-line" d="{line}" pathLength="1" stroke-dasharray="1" class="ln{"U" if up else "D"}" style="stroke-width:9;stroke-linejoin:round;stroke-linecap:round"/>'
        for i, v in enumerate(vals):
            svg += f'<g id="{p}-dot{i}">{C(X(i), Y(v), 10 if i == len(vals) - 1 else 7, "f3 s")}</g>'
            lab = pts[i].get("label", "")
            svg += TX(X(i), gy1 + 46, E(lab), 21, "txs", "middle", f' id="{p}-lab{i}"')
        lx, ly = X(len(vals) - 1), Y(vals[-1])
        svg += (f'<g id="{p}-flag"><line x1="{lx:.0f}" y1="{ly:.0f}" x2="{lx:.0f}" y2="{ly - 110:.0f}" style="stroke:var(--ink);stroke-width:6"/>'
                f'<g id="{p}-fl">{P(f"M{lx:.0f},{ly - 110:.0f} L{lx + 70:.0f},{ly - 92:.0f} L{lx:.0f},{ly - 72:.0f} Z", "acc s")}</g></g>')
    svg += "</g>"
    # number column
    name = str(data.get("name", "")).upper()
    val = data.get("value", ""); vs = fmt(num(val), decs(val)) if num(val) is not None else str(val)
    fs = min(80, 380 / (max(6, len(vs)) * .58))
    svg += f'<g id="{p}-col">{TX(990, 220, E(name), 34, "txs", "middle", "", "h")}'
    svg += TX(990, 320, numtext(k, f"{p}-val", val, a + .6, dur=1.5, start_frac=.97), fs, "tx", "middle", f' id="{p}-val"', "num")
    pct = num(data.get("pct"))
    if pct is not None:
        svg += f'<g id="{p}-pct">{chip(990, 400, ("▲ " if up else "▼ ") + fmt(abs(pct), 2) + "%", tone, 230, 70, 36)}</g>'
    extra = data.get("extra") or []
    for i, e in enumerate(extra[:2]):
        svg += f'<g id="{p}-ex{i}">{TX(990, 486 + i * 74, E(e["label"]).upper(), 20, "txs", "middle")}{TX(990, 516 + i * 74, E(e["value"]), 27, "tx", "middle", "", "num")}</g>'
    svg += "</g>" + src_tag(p, data.get("source"))
    # motion
    stage_js(k, a, d, 430, 380)
    k.pop(f"#{p}-board", a + .05, 420, 380, .5, .6); k.sfx(a + .05, "pop", .5)
    if len(vals) >= 2:
        if mil: k.draw(f"#{p}-mil", a + .45, .6); k.fade(f"#{p}-milt", a + .7)
        k.draw(f"#{p}-line", a + .55, 1.2); k.sfx(a + .55, "swish", .45)
        k.fade(f"#{p}-area", a + 1.4, .5)
        for i in range(len(vals)): k.pop(f"#{p}-dot{i}", a + .6 + i * 1.1 / len(vals), 0, 0, 0, .3); k.fade(f"#{p}-lab{i}", a + .6 + i * .12)
        k.rise(f"#{p}-flag", a + 1.75, lx, ly, .45)
        k.add(f'tl.fromTo("#{p}-fl",{{skewY:0,svgOrigin:"{lx:.0f} {ly - 92:.0f}"}},{{skewY:-10,duration:.45,ease:"sine.inOut",repeat:{rep(d, .45)},yoyo:true}},{T(a + 2.2)})')
    k.fade(f"#{p}-col", a + .4, .4, 20)
    if pct is not None:
        k.pop(f"#{p}-pct", a + 1.95, 990, 400, .3, .5); k.sfx(a + 1.95, "impact", .7)
        k.ev["punch"].append(a + 1.95); k.ev["mood"].append((a + 2.0, "up" if up else "down"))
    for i in range(len(extra[:2])): k.fade(f"#{p}-ex{i}", a + 2.3 + i * .15, .35, 12)
    if mil and vals and vals[-1] >= mil: svg += confetti(k, a + 2.0, 18, 120, 760, 7)
    src_js(k, a)
    return svg, k


def sc_flows(p, a, d, data):
    k = K(p); days = data.get("days") or []
    last = days[-1] if days else {}
    fii, dii = num(last.get("fii")) or 0, num(last.get("dii")) or 0
    svg = stage(p, 600, 360, 340, 700, 470)
    gx, gy, gr = 250, 330, 120
    svg += (f'<defs><clipPath id="{p}-gc"><circle cx="{gx}" cy="{gy}" r="{gr}"/></clipPath></defs>'
            f'<g id="{p}-globe">{EL(gx + 10, gy + 14, gr, gr, "kd s", " opacity=\".5\"")}{C(gx, gy, gr, "f1 s")}'
            f'<g clip-path="url(#{p}-gc)"><g id="{p}-land">'
            + "".join(P(f"M{gx - 150 + o},{gy - 60} q40,-40 90,-10 q30,30 -10,60 q-50,20 -80,-10 z M{gx - 40 + o},{gy + 20} q50,-20 80,10 q10,50 -40,60 q-50,-10 -40,-70 z", "f2")
                      for o in (0, 260, -260)) +
            f'</g></g>{EL(gx, gy, gr, gr * .35, "ol", " opacity=\".35\"")}{EL(gx, gy, gr * .4, gr, "ol", " opacity=\".35\"")}'
            f'{P(f"M{gx - 80},{gy - 70} q30,-30 70,-35", "hi", " style=\"fill:none;stroke:#fff;stroke-width:10;stroke-linecap:round;opacity:.5\"")}</g>'
            f'<g id="{p}-gl">{chip(gx, gy + gr + 50, "FII / FPI", "f1", 170, 52, 26, None, "txd")}</g>')
    bx, byb = 950, 560
    cols = "".join(R(bx - 130 + i * 58, byb - 200, 30, 200, 4, "{c}") for i in range(5))
    svg += (f'<g id="{p}-bld">{slab(R(bx - 165, byb - 20, 330, 40, 8, "{c}"), 3, 10, 3)}'
            + slab(cols, 4, 8, 3)
            + slab(P(f"M{bx - 175},{byb - 200} L{bx},{byb - 300} L{bx + 175},{byb - 200} Z", "{c}"), 3, 10, 3)
            + TX(bx, byb - 222, "₹", 64, "txd", "middle", "", "h") + '</g>'
            f'<g id="{p}-bl">{chip(bx, byb + 60, "DII", "f4", 130, 52, 26, None, "txd")}</g>')
    ax0, ay0, ax1, ay1, cxp, cyp = gx + 90, gy - 90, bx - 60, byb - 300, 600, 70
    if fii < 0: ax0, ay0, ax1, ay1 = ax1, ay1, ax0, ay0
    svg += f'<path id="{p}-arc" d="M{ax0},{ay0} Q{cxp},{cyp} {ax1},{ay1}" pathLength="1" stroke-dasharray="1" class="ol" style="stroke-width:5;stroke-dasharray:1"/>'
    coins = ""
    for i in range(6): coins += f'<g id="{p}-c{i}" opacity="0">{EL(0, 4, 26, 26, "kcoin s")}{C(0, 0, 26, "coin s")}{TX(0, 11, "₹", 30, "txd", "middle", "", "h")}</g>'
    svg += coins
    tf = "up" if fii >= 0 else "dn"; td = "up" if dii >= 0 else "dn"
    svg += (f'<g id="{p}-n1">{TX(gx, 120, numtext(k, f"{p}-fv", fmt(abs(fii), 0), a + .7, ("+₹" if fii >= 0 else "−₹"), " cr", 1.3), 54, tf, "middle", f" id=\"{p}-fv\"", "num")}'
            f'{TX(gx, 160, "Foreign investors" + (" bought" if fii >= 0 else " sold"), 24, "txs", "middle")}</g>'
            f'<g id="{p}-n2">{TX(bx, 160, numtext(k, f"{p}-dv", fmt(abs(dii), 0), a + 1.5, ("+₹" if dii >= 0 else "−₹"), " cr", 1.3), 54, td, "middle", f" id=\"{p}-dv\"", "num")}'
            f'{TX(bx, 200, "Domestic institutions" + (" bought" if dii >= 0 else " sold"), 24, "txs", "middle")}</g>')
    # 8-day strip
    n = len(days)
    if n >= 2:
        m = max(max(abs(num(x["fii"]) or 0), abs(num(x["dii"]) or 0)) for x in days) or 1
        x0, x1, base = 470, 760, 690
        step = (x1 - x0) / n; strip = ""
        for i, x in enumerate(days):
            f_, d_ = num(x["fii"]) or 0, num(x["dii"]) or 0
            hf, hd = abs(f_) / m * 60, abs(d_) / m * 60
            cx = x0 + i * step
            strip += (f'<g id="{p}-sb{i}">' + R(cx, base - hf if f_ > 0 else base, step * .36, max(2, hf), 3, "f1 s")
                      + R(cx + step * .4, base - hd if d_ > 0 else base, step * .36, max(2, hd), 3, "f4 s") + "</g>")
        svg += f'<g id="{p}-strip"><line class="grid" x1="{x0 - 10}" x2="{x1 + 6}" y1="{base}" y2="{base}"/>{strip}' \
               f'{TX((x0 + x1) / 2, base + 92, f"Last {n} sessions · ₹ crore", 20, "txs")}</g>'
    svg += src_tag(p, data.get("source"))
    stage_js(k, a, d, 600, 360)
    k.pop(f"#{p}-globe", a + .05, gx, gy, .2, .6); k.fade(f"#{p}-gl", a + .4)
    k.add(f'tl.fromTo("#{p}-land",{{x:0}},{{x:260,duration:{T(max(1, d))},ease:"none"}},{T(a)})')
    k.add(f'tl.fromTo("#{p}-bld",{{y:300,opacity:0}},{{y:0,opacity:1,duration:.6,ease:"back.out(1.4)"}},{T(a + .2)})'); k.fade(f"#{p}-bl", a + .55)
    k.sfx(a + .05, "pop", .5); k.sfx(a + .2, "swish", .4)
    k.draw(f"#{p}-arc", a + .55, .7)
    k.fade(f"#{p}-n1", a + .6, .35, 14); k.fade(f"#{p}-n2", a + 1.4, .35, 14)
    # coins fly along the arc in a loop
    steps = 6; pts = [((1 - u) ** 2 * ax0 + 2 * (1 - u) * u * cxp + u ** 2 * ax1, (1 - u) ** 2 * ay0 + 2 * (1 - u) * u * cyp + u ** 2 * ay1) for u in [i / steps for i in range(steps + 1)]]
    per = 1.3; loops = max(1, int((d - 1.2) / per))
    for i in range(6):
        t0 = a + 1.0 + i * per / 6
        kf = ",".join(f'{{x:{x:.0f},y:{y:.0f},duration:{per / steps:.3f},ease:"none"}}' for x, y in pts[1:])
        k.add(f'tl.fromTo("#{p}-c{i}",{{x:{pts[0][0]:.0f},y:{pts[0][1]:.0f},opacity:1,scale:.7}},{{keyframes:[{kf}],repeat:{loops - 1}}},{T(t0)})')
        k.add(f'tl.set("#{p}-c{i}",{{opacity:0}},{T(t0 + loops * per)})')
        if i % 2 == 0: k.sfx(t0 + per, "ping", .25)
    if n >= 2:
        for i in range(n): k.rise(f"#{p}-sb{i}", a + 1.2 + i * .07, 0, 690, .4)
        k.fade(f"#{p}-strip", a + 1.15, .3)
    k.ev["punch"].append(a + 1.9); k.ev["mood"].append((a + 1.9, "up" if fii >= 0 else "down")); k.sfx(a + 1.9, "impact", .6)
    src_js(k, a)
    return svg, k


def sc_movers(p, a, d, data):
    k = K(p); g, l = data.get("gainers") or [], data.get("losers") or []
    items, tone = (g[:3], "up") if g else (l[:3], "dn")
    svg = stage(p, 600, 400, 330, 700, 450)
    order = [1, 0, 2] if len(items) == 3 else list(range(len(items)))
    xs = {3: [330, 600, 870], 2: [440, 760], 1: [600]}[len(items)]
    mx = max(abs(num(x["pct"]) or 1) for x in items)
    base = 650; fills = ["f4", "f1", "f5"]
    for slot, idx in enumerate(order):
        it = items[idx]; x = xs[slot]; pc = abs(num(it["pct"]) or 0)
        h = 140 + 210 * pc / mx
        fn = fills[idx][1]
        svg += (f'<g id="{p}-b{idx}">{slab(R(x - 115, base - h, 230, h, 14, "{c}"), fn, 16, 4)}'
                f'{R(x - 100, base - h + 12, 26, h - 30, 10, "hi")}'
                f'{TX(x, base - h + 100, str(idx + 1), 92, "txd", "middle", "", "h")}'
                + (TX(x, base - 26, "₹" + E(fmt(num(it["price"]), 2)), 24, "txd", "middle", "", "num") if num(it.get("price")) else "") + "</g>"
                f'<g id="{p}-t{idx}">{chip(x, base - h - 50, "", tone, 210, 64, 32)}'
                f'{TX(x, base - h - 38, numtext(k, f"{p}-pv{idx}", fmt(pc, 2), a + .7 + idx * .15, "+" if tone == "up" else "−", "%", 1.0), 32, "tchip", "middle", f" id=\"{p}-pv{idx}\"", "num")}'
                + "".join(TX(x, base - h - 100 - (len(wrap(it["name"], 14)) - 1 - j) * 34, E(line), 30, "tx", "middle", "", "h")
                          for j, line in enumerate(wrap(it["name"], 14)[:2])) + "</g>")
    if tone == "up" and items:
        x = xs[order.index(0)]; h = 140 + 210 * abs(num(items[0]["pct"]) or 0) / mx
        svg += f'<g id="{p}-star">{P(_star(x + 118, base - h + 26, 34, 15), "f4 s")}</g>'
    svg += f'<g id="{p}-lbl">{chip(600, 745, "TOP GAINERS" if tone == "up" else "TOP LOSERS", "dk", 290, 50, 24, None, "tx")}</g>'
    svg += src_tag(p, data.get("source"), 40, 790)
    stage_js(k, a, d, 600, 400)
    for slot, idx in enumerate(reversed(order)):
        k.rise(f"#{p}-b{idx}", a + .2 + slot * .17, 0, base, .55); k.sfx(a + .2 + slot * .17, "pop", .45)
        k.pop(f"#{p}-t{idx}", a + .55 + slot * .17, xs[order.index(idx)], base - 200, .3, .45)
    k.fade(f"#{p}-lbl", a + .3)
    if tone == "up" and items:
        k.pop(f"#{p}-star", a + 1.2, x + 118, base - h + 26, 0, .5)
        k.spin(f"#{p}-star", a + 1.7, d - 1.7, x + 118, base - h + 26, 180)
        svg += confetti(k, a + 1.25, 16, 150, 1050, 3)
    k.ev["punch"].append(a + 1.0); k.ev["mood"].append((a + 1.05, "up" if tone == "up" else "down")); k.sfx(a + 1.0, "impact", .6)
    src_js(k, a)
    return svg, k


def _star(cx, cy, r1, r2):
    pts = []
    for i in range(10):
        r = r1 if i % 2 == 0 else r2; an = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{cx + r * math.cos(an):.1f},{cy + r * math.sin(an):.1f}")
    return "M" + " L".join(pts) + " Z"


def _megaphone(p, x, y, s=1.0):
    return (f'<g id="{p}-mega" transform="translate({x} {y}) scale({s})">'
            + slab(P("M-60,-30 L60,-90 L60,90 L-60,30 Z", "{c}"), 5, 12, 3) + slab(R(-100, -36, 44, 72, 10, "{c}"), "dk", 8, 2)
            + slab(EL(66, 0, 22, 92, "{c}"), 3, 6, 2) + R(-80, 30, 20, 60, 8, "dk s") + '</g>'
            + "".join(f'<g id="{p}-wv{i}">{P(f"M{x + 110 + i * 34},{y - 60 - i * 18} Q{x + 150 + i * 40},{y} {x + 110 + i * 34},{y + 60 + i * 18}", "ol", " style=\"stroke-width:7;stroke-linecap:round\"")}</g>' for i in range(3)))


def _mega_js(k, a, d, x, y):
    k.pop(f"#{k.p}-mega", a + .1, x, y, .2, .55)
    for i in range(3):
        k.add(f'tl.fromTo("#{k.p}-wv{i}",{{opacity:0,x:-20}},{{opacity:1,x:10,duration:.5,ease:"power1.out",repeat:{rep(d, .9)},repeatDelay:.4}},{T(a + .5 + i * .15)})')


def sc_announce(p, a, d, data):
    k = K(p)
    svg = stage(p, 640, 380, 330, 720, 460)
    svg += "".join(f'<g opacity=".55">{slab(R(x, 520 - h, 90, h, 6, "{c}"), "dk", 8, 2)}</g>' for x, h in ((470, 210), (880, 260), (1000, 170)))
    svg += _megaphone(p, 190, 470, 1.0)
    cx, cy = 720, 380
    lines = wrap(data.get("company", ""), 18)[:2]
    svg += (f'<g id="{p}-card"><g transform="rotate(-5 {cx} {cy})">{slab(R(cx - 330, cy - 200, 660, 400, 26, "{c}"), 3, 18, 4)}'
            f'{R(cx - 330, cy - 200, 660, 80, 26, "f1 s")}{R(cx - 330, cy - 150, 660, 30, 0, "f1")}'
            f'{TX(cx - 300, cy - 146, E(str(data.get("kicker", "ANNOUNCEMENT")).upper()), 30, "txd", "start", "", "h")}'
            + "".join(TX(cx - 300, cy - 76 + j * 46, E(l), 42, "txd", "start", "", "h") for j, l in enumerate(lines))
            + TX(cx - 300, cy + 70 + (len(lines) - 1) * 20, numtext(k, f"{p}-amt", data.get("amount", ""), a + .9, data.get("prefix", ""), data.get("suffix", ""), 1.3), 96, "txd", "start", f' id="{p}-amt"', "num")
            + TX(cx - 300, cy + 130 + (len(lines) - 1) * 20, E(data.get("sub", "")), 28, "txd", "start", ' opacity=".7"')
            + '</g></g>')
    st = str(data.get("stamp", "")).upper()
    if st:
        sx, sy = cx + 200, cy + 150
        svg += (f'<g id="{p}-stamp"><g transform="rotate(-14 {sx} {sy})">{R(sx - 150, sy - 42, 300, 84, 12, "", " style=\"fill:none;stroke:var(--dn);stroke-width:8\"")}'
                f'{TX(sx, sy + 16, E(st), 44, "", "middle", " style=\"fill:var(--dn);font-size:44px\"", "h")}</g></g>')
    svg += src_tag(p, data.get("source"))
    stage_js(k, a, d, 640, 380); _mega_js(k, a, d, 190, 470)
    k.add(f'tl.fromTo("#{p}-card",{{x:700,rotation:18,opacity:0,svgOrigin:"{cx} {cy}"}},{{x:0,rotation:0,opacity:1,duration:.7,ease:"back.out(1.3)"}},{T(a + .25)})')
    k.sfx(a + .25, "whoosh", .5)
    if st:
        k.add(f'tl.fromTo("#{p}-stamp",{{scale:2.6,opacity:0,svgOrigin:"{cx + 200} {cy + 150}"}},{{scale:1,opacity:1,duration:.28,ease:"power4.in"}},{T(a + 1.7)})')
        k.sfx(a + 1.98, "impact", .8); k.ev["punch"].append(a + 1.98)
    k.ev["mood"].append((a + 2.1, "up")); src_js(k, a)
    return svg, k


def sc_headline(p, a, d, data):
    k = K(p)
    svg = stage(p, 600, 380, 330, 720, 460)
    cx, cy = 640, 370
    lines = wrap(data.get("text", ""), 22)[:4]
    fs = 52 if len(lines) <= 3 else 44
    svg += (f'<g id="{p}-np"><g transform="rotate(3 {cx} {cy})">{slab(R(cx - 360, cy - 250, 720, 500, 18, "{c}"), 3, 18, 4)}'
            f'{R(cx - 330, cy - 220, 260, 44, 8, "f2 s")}{TX(cx - 200, cy - 188, E(str(data.get("kicker", "NEWS")).upper()), 26, "txd", "middle", "", "h")}'
            + "".join(TX(cx - 330, cy - 120 + j * (fs + 12), E(l), fs, "txd", "start", f' id="{p}-l{j}"', "h") for j, l in enumerate(lines))
            + "".join(R(cx - 330, cy + 120 + j * 30, 660 - j * 140, 12, 6, "txd", ' opacity=".18"') for j in range(3))
            + TX(cx - 330, cy + 220, E(data.get("sub", "")), 26, "txd", "start", ' opacity=".7"') + '</g></g>')
    icons = [("₹", "f4", 160, 200), ("%", "f1", 1080, 170), ("▲", "f2", 1090, 600), ("●", "f5", 150, 620)]
    for i, (g, c, x, y) in enumerate(icons):
        svg += f'<g id="{p}-ic{i}">{slab(C(x, y, 52, "{c}"), c[1], 8, 2)}{TX(x, y + 17, g, 48, "txd", "middle", "", "h")}</g>'
    svg += src_tag(p, data.get("source"))
    stage_js(k, a, d)
    k.add(f'tl.fromTo("#{p}-np",{{y:700,rotation:-12,svgOrigin:"{cx} {cy}"}},{{y:0,rotation:0,duration:.75,ease:"back.out(1.2)"}},{T(a + .1)})')
    k.sfx(a + .1, "whoosh", .5)
    for j in range(len(lines)): k.fade(f"#{p}-l{j}", a + .6 + j * .12, .3)
    for i in range(4):
        k.pop(f"#{p}-ic{i}", a + .5 + i * .1, icons[i][2], icons[i][3], 0, .5); k.bob(f"#{p}-ic{i}", a + 1.1, d - 1.1, 12, 1.6 + i * .2)
    k.ev["punch"].append(a + .9); src_js(k, a)
    return svg, k


def sc_world(p, a, d, data):
    k = K(p); items = (data.get("items") or [])[:4]
    svg = stage(p, 260, 380, 240, 700, 260)
    gx, gy, gr = 260, 360, 170
    svg += (f'<defs><clipPath id="{p}-gc"><circle cx="{gx}" cy="{gy}" r="{gr}"/></clipPath></defs>'
            f'<g id="{p}-globe">{EL(gx + 12, gy + 16, gr, gr, "kd s", " opacity=\".5\"")}{C(gx, gy, gr, "f1 s")}'
            f'<g clip-path="url(#{p}-gc)"><g id="{p}-land">'
            + "".join(P(f"M{gx - 200 + o},{gy - 80} q60,-50 120,-10 q40,40 -20,80 q-70,20 -100,-20 z M{gx - 40 + o},{gy + 30} q70,-30 110,10 q20,70 -60,80 q-60,-20 -50,-90 z", "f2")
                      for o in (0, 360, -360)) +
            f'</g></g>{EL(gx, gy, gr, gr * .35, "ol", " opacity=\".35\"")}{EL(gx, gy, gr * .4, gr, "ol", " opacity=\".35\"")}</g>')
    pins = [(gx - 80, gy - 60), (gx + 60, gy - 20), (gx - 10, gy + 70), (gx + 90, gy + 80)]
    mx = max([abs(num(x.get("pct")) or 0) for x in items] + [.5])
    for i, it in enumerate(items):
        pc = num(it.get("pct")) or 0; up = pc >= 0; y = 160 + i * 140
        px, py = pins[i]
        svg += f'<g id="{p}-pin{i}">{P(f"M{px},{py} q-24,-30 -24,-46 a24,24 0 1 1 48,0 q0,16 -24,46 z", ("up" if up else "dn") + " s")}{C(px, py - 46, 9, "f3")}</g>'
        bl = 30 + 160 * abs(pc) / mx
        svg += (f'<g id="{p}-r{i}">{slab(R(500, y - 50, 640, 104, 20, "{c}"), "dk", 8, 2)}'
                f'{TX(530, y - 6, E(it["name"]), 30, "tx", "start", "", "h")}'
                f'{TX(530, y + 32, E(str(it.get("value", ""))), 24, "txs", "start", "", "num")}'
                f'<g id="{p}-bar{i}">{R(820, y - 18, bl, 36, 18, ("up" if up else "dn") + " s")}</g>'
                f'{TX(820 + bl + 12, y + 12, numtext(k, f"{p}-pc{i}", fmt(abs(pc), 2), a + .7 + i * .2, "+" if up else "−", "%", .9), 30, "up" if up else "dn", "start", f" id=\"{p}-pc{i}\"", "num")}</g>')
    svg += src_tag(p, data.get("source"))
    stage_js(k, a, d, 260, 380)
    k.pop(f"#{p}-globe", a + .05, gx, gy, .2, .6); k.sfx(a + .05, "pop", .5)
    k.add(f'tl.fromTo("#{p}-land",{{x:0}},{{x:360,duration:{T(max(1, d))},ease:"none"}},{T(a)})')
    big = max(range(len(items)), key=lambda i: abs(num(items[i].get("pct")) or 0)) if items else 0
    for i in range(len(items)):
        y = 160 + i * 140
        k.add(f'tl.fromTo("#{p}-r{i}",{{x:500,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"power3.out"}},{T(a + .3 + i * .18)})')
        k.add(f'tl.fromTo("#{p}-bar{i}",{{scaleX:0,svgOrigin:"820 {y}"}},{{scaleX:1,duration:.7,ease:"power3.out"}},{T(a + .7 + i * .2)})')
        k.add(f'tl.fromTo("#{p}-pin{i}",{{y:-260,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"bounce.out"}},{T(a + .6 + i * .2)})')
        k.sfx(a + .3 + i * .18, "swish", .3)
    if items:
        t = a + 1.3 + big * .2; k.ev["punch"].append(t); k.sfx(t, "impact", .5)
        k.ev["mood"].append((t, "up" if (num(items[big].get("pct")) or 0) >= 0 else "down"))
    src_js(k, a)
    return svg, k


def sc_stat(p, a, d, data):
    k = K(p); tone = data.get("tone", "up"); up = tone != "down"
    svg = stage(p, 600, 360, 330, 720, 430)
    svg += f'<g id="{p}-pl">{slab(P("M330,560 L870,560 L820,680 L380,680 Z", "{c}"), "dk", 14, 4)}{slab(R(300, 520, 600, 50, 12, "{c}"), 4 if up else 5, 10, 3)}</g>'
    val = data.get("value", ""); vs = f'{data.get("prefix", "")}{val}{data.get("suffix", "")}'
    fs = min(170, 980 / (max(4, len(vs)) * .6))
    svg += f'<g id="{p}-lb">{TX(600, 170, E(str(data.get("label", "")).upper()), 38, "txs", "middle", "", "h")}</g>'
    svg += TX(600, 470, numtext(k, f"{p}-v", val, a + .5, data.get("prefix", ""), data.get("suffix", ""), 1.4), fs, "up" if up else "dn", "middle", f' id="{p}-v"', "num")
    svg += f'<g id="{p}-ar">{arrow3d(150, 380, up, 1.0, "up" if up else "dn")}</g>'
    if data.get("note"): svg += f'<g id="{p}-nt">{TX(600, 625, E(data["note"]), 28, "tx", "middle")}</g>'
    svg += src_tag(p, data.get("source"))
    stage_js(k, a, d)
    k.add(f'tl.fromTo("#{p}-pl",{{y:260,opacity:0}},{{y:0,opacity:1,duration:.55,ease:"back.out(1.4)"}},{T(a + .1)})')
    k.fade(f"#{p}-lb", a + .3, .35, 14); k.fade(f"#{p}-v", a + .45, .25)
    k.pop(f"#{p}-ar", a + 1.4, 150, 380, 0, .5); k.bob(f"#{p}-ar", a + 2, d - 2, 14, 1.2)
    if data.get("note"): k.fade(f"#{p}-nt", a + 1.6, .35, 10)
    t = a + 1.9; k.ev["punch"].append(t); k.ev["mood"].append((t, "up" if up else "down")); k.sfx(t, "impact", .7)
    src_js(k, a)
    return svg, k


def _info_tags(p, k, rows, x, y0, a, w=420):
    out = ""
    for i, (lab, val) in enumerate(rows):
        y = y0 + i * 92
        out += (f'<g id="{p}-tg{i}">{slab(R(x, y, w, 74, 16, "{c}"), "dk", 6, 2)}{TX(x + 24, y + 30, E(lab.upper()), 20, "txs", "start")}'
                f'{TX(x + 24, y + 62, E(str(val)), 30, "tx", "start", "", "num")}</g>')
        k.add(f'tl.fromTo("#{p}-tg{i}",{{x:200,opacity:0}},{{x:0,opacity:1,duration:.45,ease:"power3.out"}},{T(a + 1.0 + i * .15)})')
        k.sfx(a + 1.0 + i * .15, "click", .3)
    return out


def sc_dividend(p, a, d, data):
    k = K(p)
    svg = stage(p, 400, 400, 300, 700, 360)
    px, py = 380, 470
    svg += (f'<g id="{p}-pig">{slab(EL(px, py, 190, 140, "{c}"), 5, 16, 4)}{slab(EL(px + 190, py - 10, 40, 48, "{c}"), 5, 6, 2)}'
            f'{C(px + 182, py - 20, 7, "dk")}{C(px + 198, py - 2, 7, "dk")}{C(px + 100, py - 60, 12, "dk")}'
            f'{P(f"M{px - 60},{py - 120} l40,-50 l20,46 z", "f5 s")}{R(px - 60, py - 150, 120, 16, 8, "dk s")}'
            + "".join(R(px + dx, py + 110, 40, 70, 12, "f5 s") for dx in (-120, -40, 50, 120)) +
            f'{EL(px - 60, py - 50, 60, 30, "hi")}</g>')
    for i in range(5): svg += f'<g id="{p}-co{i}" opacity="0">{EL(px, py - 210 + 5, 34, 34, "kcoin s")}{C(px, py - 210, 34, "coin s")}{TX(px, py - 196, "₹", 40, "txd", "middle", "", "h")}</g>'
    amt = data.get("amount", "")
    svg += (f'<g id="{p}-r">{TX(870, 190, E(data.get("company", "")), 40, "tx", "middle", "", "h")}'
            f'{TX(870, 320, numtext(k, f"{p}-am", amt, a + .6, "₹", "", 1.2), 120, "up", "middle", f" id=\"{p}-am\"", "num")}'
            f'{TX(870, 370, "per share" + (" · " + E(data.get("type")) if data.get("type") else ""), 28, "txs", "middle")}</g>')
    rows = [(l, data[f]) for l, f in (("Ex-date", "ex_date"), ("Record date", "record_date")) if data.get(f)]
    svg += _info_tags(p, k, rows, 660, 430, a) + src_tag(p, data.get("source"))
    stage_js(k, a, d, 400, 400)
    k.pop(f"#{p}-pig", a + .05, px, py + 140, .3, .6); k.fade(f"#{p}-r", a + .4, .4, 20)
    for i in range(5):
        k.add(f'tl.fromTo("#{p}-co{i}",{{y:-200,opacity:1}},{{y:150,opacity:1,duration:.55,ease:"power2.in",repeat:{rep(d - 1, 1.6)},repeatDelay:1.05}},{T(a + .8 + i * .32)})')
        k.sfx(a + 1.35 + i * .32, "ping", .25)
    t = a + 1.8; k.ev["punch"].append(t); k.ev["mood"].append((t, "up")); k.sfx(t, "sparkle", .6)
    src_js(k, a)
    return svg, k


def sc_split(p, a, d, data):
    k = K(p)
    f0, f1 = num(data.get("from_fv")), num(data.get("to_fv"))
    nparts = int(round(f0 / f1)) if f0 and f1 and 1 < f0 / f1 <= 10 else 2
    svg = stage(p, 600, 380, 330, 700, 460)
    bw = 840; bx = 600 - bw / 2; by = 300; pw = bw / nparts
    svg += TX(600, 160, E(data.get("company", "")), 46, "tx", "middle", "", "h")
    for i in range(nparts):
        svg += f'<g id="{p}-pc{i}">{slab(R(bx + i * pw + 4, by, pw - 8, 190, 16, "{c}"), 4, 14, 4)}{R(bx + i * pw + 18, by + 14, 14, 160, 7, "hi")}' \
               f'<g id="{p}-pl{i}" opacity="0">{TX(bx + i * pw + pw / 2, by + 112, "₹" + E(str(data.get("to_fv", ""))), 40, "txd", "middle", "", "num")}</g></g>'
    svg += f'<g id="{p}-whole">{TX(600, by + 118, "FACE VALUE ₹" + E(str(data.get("from_fv", ""))), 52, "txd", "middle", "", "h")}</g>'
    svg += f'<g id="{p}-res">{chip(600, 580, f"₹{data.get("from_fv", "")}  →  ₹{data.get("to_fv", "")}", "up", 420, 76, 40)}</g>'
    rows = [("Ex-date", data["ex_date"])] if data.get("ex_date") else []
    svg += "".join(f'<g id="{p}-ex">{TX(600, 680, E(l) + ": " + E(str(v)), 30, "tx", "middle", "", "num")}</g>' for l, v in rows)
    svg += src_tag(p, data.get("source"))
    stage_js(k, a, d)
    for i in range(nparts): k.pop(f"#{p}-pc{i}", a + .15, 600, by + 95, .4, .5)
    k.fade(f"#{p}-whole", a + .4)
    ts = a + 1.3
    k.add(f'tl.to("#{p}-whole",{{opacity:0,duration:.15}},{T(ts - .05)})')
    for i in range(nparts):
        off = (i - (nparts - 1) / 2) * 34
        k.add(f'tl.to("#{p}-pc{i}",{{x:{off:.0f},y:{(-18 if i % 2 else 18)},rotation:{(-4 if i % 2 else 4)},svgOrigin:"{bx + i * pw + pw / 2:.0f} {by + 95}",duration:.45,ease:"back.out(2)"}},{T(ts)})')
        k.fade(f"#{p}-pl{i}", ts + .2 + i * .06, .25)
    k.sfx(ts, "glitch", .4); k.sfx(ts + .05, "impact", .6); k.ev["punch"].append(ts)
    k.pop(f"#{p}-res", a + 1.8, 600, 580, .3, .45)
    if rows: k.fade(f"#{p}-ex", a + 2.1, .35, 10)
    k.ev["mood"].append((ts + .1, "up")); src_js(k, a)
    return svg, k


def sc_bonus(p, a, d, data):
    k = K(p)
    svg = stage(p, 420, 400, 300, 700, 380)
    bx, by = 420, 470
    svg += (f'<g id="{p}-box">{slab(R(bx - 170, by - 120, 340, 250, 18, "{c}"), 5, 16, 4)}{R(bx - 26, by - 120, 52, 250, 0, "f4 s")}</g>'
            f'<g id="{p}-lid">{slab(R(bx - 195, by - 190, 390, 76, 16, "{c}"), 5, 10, 3)}{R(bx - 30, by - 190, 60, 76, 0, "f4 s")}'
            f'{P(f"M{bx},{by - 190} q-80,-90 -110,-20 q30,30 110,20 q80,10 110,-20 q-30,-70 -110,20 z", "f4 s")}</g>')
    for i in range(6):
        svg += f'<g id="{p}-sh{i}" opacity="0">{slab(R(bx - 50, by - 160, 100, 64, 10, "{c}"), 3, 6, 2)}{TX(bx, by - 120, "SHARE", 20, "txd", "middle", "", "h")}</g>'
    svg += (f'<g id="{p}-r">{TX(870, 190, E(data.get("company", "")), 40, "tx", "middle", "", "h")}'
            f'{TX(870, 330, E(str(data.get("ratio", ""))), 130, "up", "middle", "", "num")}{TX(870, 380, "bonus ratio", 28, "txs", "middle")}</g>')
    rows = [(l, data[f]) for l, f in (("Ex-date", "ex_date"), ("Record date", "record_date")) if data.get(f)]
    svg += _info_tags(p, k, rows, 660, 440, a) + src_tag(p, data.get("source"))
    stage_js(k, a, d, 420, 400)
    k.pop(f"#{p}-box", a + .05, bx, by + 130, .3, .55); k.pop(f"#{p}-lid", a + .15, bx, by - 150, .3, .5)
    to = a + 1.1
    k.add(f'tl.to("#{p}-lid",{{y:-130,x:-60,rotation:-24,svgOrigin:"{bx} {by - 150}",duration:.45,ease:"back.out(2)"}},{T(to)})')
    k.sfx(to, "pop", .7)
    for i in range(6):
        ang = -150 + i * 24
        dx, dy = 300 * math.cos(math.radians(ang)) + 120, 300 * math.sin(math.radians(ang)) - 40
        k.add(f'tl.fromTo("#{p}-sh{i}",{{x:0,y:40,opacity:1,rotation:0,svgOrigin:"{bx} {by - 128}"}},{{x:{dx:.0f},y:{dy:.0f},rotation:{-30 + i * 12},duration:.8,ease:"power3.out"}},{T(to + .05 + i * .05)})')
    k.fade(f"#{p}-r", a + .5, .4, 20)
    k.ev["punch"].append(to + .1); k.ev["mood"].append((to + .15, "up")); svg += confetti(k, to + .1, 12, 150, 700, 5)
    src_js(k, a)
    return svg, k


def sc_buyback(p, a, d, data):
    k = K(p)
    svg = stage(p, 600, 380, 330, 700, 460)
    svg += f'<g id="{p}-bld">{slab(R(820, 220, 260, 400, 14, "{c}"), 1, 16, 4)}' + "".join(R(850 + (i % 3) * 76, 260 + (i // 3) * 80, 50, 50, 6, "f3 s") for i in range(12)) + \
           f'{TX(950, 200, E(data.get("company", "")), 34, "tx", "middle", "", "h")}</g>'
    mx, my = 640, 420
    svg += f'<g id="{p}-mag">{slab(P(f"M{mx - 90},{my - 120} L{mx - 30},{my - 120} L{mx - 30},{my + 20} Q{mx - 30},{my + 60} {mx},{my + 60} Q{mx + 30},{my + 60} {mx + 30},{my + 20} L{mx + 30},{my - 120} L{mx + 90},{my - 120} L{mx + 90},{my + 20} Q{mx + 90},{my + 120} {mx},{my + 120} Q{mx - 90},{my + 120} {mx - 90},{my + 20} Z", "{c}"), 5, 14, 4)}' \
           f'{R(mx - 90, my - 150, 60, 34, 4, "f3 s")}{R(mx + 30, my - 150, 60, 34, 4, "f3 s")}</g>'
    for i in range(5):
        svg += f'<g id="{p}-sh{i}" opacity="0">{slab(R(60, 260 + i * 80, 110, 60, 10, "{c}"), 3, 6, 2)}{TX(115, 298 + i * 80, "SHARE", 20, "txd", "middle", "", "h")}</g>'
    rows = [(l, data[f]) for l, f in (("Size", "size"), ("Price", "price"), ("Method", "method")) if data.get(f)]
    svg += f'<g id="{p}-hd">{chip(380, 130, "BUYBACK", "f4", 240, 64, 32, None, "txd")}</g>'
    for i, (l, v) in enumerate(rows[:3]):
        svg += f'<g id="{p}-tg{i}">{chip(240 + i * 300, 690, f"{l}: {v}", "dk", 280, 56, 24, None, "tx")}</g>'
        k.fade(f"#{p}-tg{i}", a + 1.2 + i * .15, .35, 12)
    svg += src_tag(p, data.get("source"), 40, 790)
    stage_js(k, a, d)
    k.add(f'tl.fromTo("#{p}-bld",{{y:300,opacity:0}},{{y:0,opacity:1,duration:.6,ease:"back.out(1.3)"}},{T(a + .1)})')
    k.pop(f"#{p}-mag", a + .3, mx, my, .2, .5); k.fade(f"#{p}-hd", a + .2)
    k.add(f'tl.fromTo("#{p}-mag",{{rotation:-6,svgOrigin:"{mx} {my}"}},{{rotation:6,duration:.3,ease:"sine.inOut",repeat:{rep(d, .3)},yoyo:true}},{T(a + .8)})')
    for i in range(5):
        k.add(f'tl.fromTo("#{p}-sh{i}",{{x:0,y:0,opacity:1,scale:1}},{{x:820,y:{-(i * 80) + 100},opacity:0,scale:.5,duration:1.1,ease:"power2.in",repeat:{rep(d - 1, 2.4)},repeatDelay:1.3}},{T(a + .9 + i * .25)})')
    k.sfx(a + .9, "whoosh", .4); k.ev["punch"].append(a + 1.4); src_js(k, a)
    return svg, k


def sc_ipo(p, a, d, data):
    k = K(p)
    svg = stage(p, 420, 380, 300, 700, 360)
    dx, dy = 420, 400
    svg += f'<g id="{p}-inside">{R(dx - 180, dy - 230, 360, 460, 20, "acc", " opacity=\".25\"")}{TX(dx, dy - 10, "NEW", 70, "txa", "middle", "", "h")}{TX(dx, dy + 60, "LISTING", 44, "txa", "middle", "", "h")}</g>'
    svg += f'<g id="{p}-dl">{slab(R(dx - 190, dy - 240, 190, 480, 14, "{c}"), 2, 12, 3)}{C(dx - 30, dy, 12, "f4 s")}</g>'
    svg += f'<g id="{p}-dr">{slab(R(dx, dy - 240, 190, 480, 14, "{c}"), 2, 12, 3)}{C(dx + 30, dy, 12, "f4 s")}</g>'
    svg += slab(R(dx - 220, dy - 270, 440, 40, 10, "{c}"), "dk", 6, 2)
    rows = [(l, data[f]) for l, f in (("Price band", "band"), ("Opens", "open"), ("Closes", "close"), ("Issue size", "size"), ("Lot", "lot")) if data.get(f)][:4]
    svg += TX(900, 150, E(data.get("company", "")), 40, "tx", "middle", "", "h")
    svg += _info_tags(p, k, rows, 690, 200, a) + src_tag(p, data.get("source"))
    stage_js(k, a, d, 420, 380)
    k.fade(f"#{p}-inside", a, .2)
    k.add(f'tl.fromTo("#{p}-dl",{{scaleX:1,svgOrigin:"{dx - 190} {dy}"}},{{scaleX:.12,duration:.8,ease:"power3.inOut"}},{T(a + .7)})')
    k.add(f'tl.fromTo("#{p}-dr",{{scaleX:1,svgOrigin:"{dx + 190} {dy}"}},{{scaleX:.12,duration:.8,ease:"power3.inOut"}},{T(a + .7)})')
    k.sfx(a + .7, "swish", .5); k.ev["punch"].append(a + 1.5); k.ev["mood"].append((a + 1.5, "up")); k.sfx(a + 1.5, "chime", .5)
    src_js(k, a)
    return svg, k


def sc_results(p, a, d, data):
    k = K(p)
    svg = stage(p, 600, 380, 330, 720, 440)
    cx = 600; x0, y0, w, h = 300, 110, 600, 600
    svg += (f'<g id="{p}-cb">{slab(R(x0, y0, w, h, 24, "{c}"), 3, 18, 4)}{slab(R(cx - 90, y0 - 30, 180, 60, 12, "{c}"), "dk", 6, 2)}'
            f'{TX(cx, y0 + 80, E(data.get("company", "")), 40, "txd", "middle", "", "h")}'
            f'{TX(cx, y0 + 120, E(str(data.get("period", data.get("purpose", "")))), 24, "txd", "middle", " opacity=\".65\"")}</g>')
    mets = (data.get("metrics") or [])[:4]
    if mets:
        for i, m in enumerate(mets):
            y = y0 + 190 + i * 100; ch = num(m.get("chg"))
            unit = m.get("unit", "")
            svg += (f'<g id="{p}-m{i}">{R(x0 + 30, y - 40, w - 60, 80, 14, "f1", " opacity=\".18\"")}{TX(x0 + 54, y + 10, E(m["label"]), 28, "txd", "start")}'
                    f'{TX(x0 + 360, y + 12, numtext(k, f"{p}-mv{i}", m["value"], a + .8 + i * .2, "₹" if "cr" in unit else "", " " + unit if unit else "", 1.0), 32, "txd", "end", f" id=\"{p}-mv{i}\"", "num")}'
                    + (chip(x0 + 470, y, ("▲ " if ch >= 0 else "▼ ") + fmt(abs(ch), 1) + "%", "up" if ch >= 0 else "dn", 160, 52, 26) if ch is not None else "") + "</g>")
            k.add(f'tl.fromTo("#{p}-m{i}",{{x:-80,opacity:0}},{{x:0,opacity:1,duration:.4,ease:"power3.out"}},{T(a + .7 + i * .2)})'); k.sfx(a + .7 + i * .2, "click", .35)
    else:
        svg += f'<g id="{p}-m0">{TX(cx, y0 + 330, E(str(data.get("date", ""))), 90, "txd", "middle", "", "num")}{TX(cx, y0 + 400, "board meeting", 30, "txd", "middle", " opacity=\".6\"")}</g>'
        k.fade(f"#{p}-m0", a + .8, .4, 20)
    sx, sy = x0 + w - 60, y0 + h - 70
    svg += (f'<g id="{p}-st"><g transform="rotate(-12 {sx} {sy})">{C(sx, sy, 78, "", " style=\"fill:none;stroke:var(--acc);stroke-width:8\"")}'
            f'{TX(sx, sy + 12, "RESULTS" if mets else "DATE", 30, "txa", "middle", "", "h")}</g></g>')
    svg += src_tag(p, data.get("source"), 40, 790)
    stage_js(k, a, d)
    k.add(f'tl.fromTo("#{p}-cb",{{y:700,rotation:8,svgOrigin:"{cx} {y0 + h}"}},{{y:0,rotation:0,duration:.7,ease:"back.out(1.2)"}},{T(a + .05)})'); k.sfx(a + .05, "whoosh", .5)
    ts = a + .9 + len(mets) * .2 + .3
    k.add(f'tl.fromTo("#{p}-st",{{scale:2.6,opacity:0,svgOrigin:"{sx} {sy}"}},{{scale:1,opacity:1,duration:.26,ease:"power4.in"}},{T(ts)})')
    k.sfx(ts + .26, "impact", .7); k.ev["punch"].append(ts + .26)
    up = all((num(m.get("chg")) or 0) >= 0 for m in mets) if mets else True
    k.ev["mood"].append((ts + .3, "up" if up else "down")); src_js(k, a)
    return svg, k


def sc_calendar(p, a, d, data):
    k = K(p); items = (data.get("items") or [])[:4]
    svg = stage(p, 280, 380, 240, 700, 280)
    cx, cy = 280, 400
    svg += (f'<g id="{p}-cal">{slab(R(cx - 170, cy - 200, 340, 380, 24, "{c}"), 3, 16, 4)}{R(cx - 170, cy - 200, 340, 100, 24, "f2 s")}{R(cx - 170, cy - 130, 340, 30, 0, "f2")}'
            + "".join(R(cx - 110 + i * 70, cy - 230, 22, 60, 11, "dk s") for i in range(4))
            + f'{TX(cx, cy - 128, E(str(data.get("month", "THIS WEEK"))), 40, "txd", "middle", "", "h")}'
            + "".join(R(cx - 140 + (i % 5) * 58, cy - 70 + (i // 5) * 54, 42, 38, 8, "f1", " opacity=\".3\"") for i in range(20)) + '</g>')
    for i, it in enumerate(items):
        y = 150 + i * 150
        svg += (f'<g id="{p}-r{i}">{slab(R(520, y - 55, 620, 120, 20, "{c}"), "dk", 8, 2)}{R(540, y - 38, 130, 86, 14, "acc")}'
                f'{TX(605, y + 16, E(str(it.get("date", ""))), 28, "tchip", "middle", "", "num")}'
                f'{TX(700, y - 2, E(it.get("company", "")), 32, "tx", "start", "", "h")}{TX(700, y + 36, E(it.get("what", "")), 24, "txs", "start")}</g>')
        k.add(f'tl.fromTo("#{p}-r{i}",{{x:400,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"power3.out"}},{T(a + .5 + i * .2)})'); k.sfx(a + .5 + i * .2, "swish", .3)
    svg += src_tag(p, data.get("source"), 40, 790)
    stage_js(k, a, d, 280, 380)
    k.pop(f"#{p}-cal", a + .05, cx, cy + 180, .3, .6); k.sfx(a + .05, "pop", .5)
    k.ev["punch"].append(a + 1.0); src_js(k, a)
    return svg, k


def sc_facts(p, a, d, data):
    k = K(p); items = (data.get("items") or [])[:4]
    svg = stage(p)
    n = len(items); cols = 2 if n > 2 else n; rows_ = (n + 1) // 2
    tw, th = 500, 260 if rows_ > 1 else 340
    x0 = 600 - (cols * tw + (cols - 1) * 40) / 2; y0 = 400 - (rows_ * th + (rows_ - 1) * 40) / 2
    fills = ["f1", "f4", "f2", "f5"]
    for i, it in enumerate(items):
        x = x0 + (i % cols) * (tw + 40); y = y0 + (i // cols) * (th + 40); tone = it.get("tone")
        svg += (f'<g id="{p}-f{i}">{slab(R(x, y, tw, th, 24, "{c}"), "dk", 12, 3)}{R(x, y, 14, th, 7, fills[i][0] + fills[i][1:] + " s")}'
                f'{TX(x + 40, y + 64, E(str(it["label"]).upper()), 24, "txs", "start")}'
                f'{TX(x + 40, y + th / 2 + 52, numtext(k, f"{p}-fv{i}", it["value"], a + .5 + i * .2, "", "", 1.1), 70, ("up" if tone == "up" else "dn" if tone == "down" else "tx"), "start", f" id=\"{p}-fv{i}\"", "num")}</g>')
        k.pop(f"#{p}-f{i}", a + .2 + i * .15, x + tw / 2, y + th / 2, .5, .5); k.sfx(a + .2 + i * .15, "pop", .35)
    svg += src_tag(p, data.get("source"), 40, 790)
    stage_js(k, a, d); k.ev["punch"].append(a + 1.4)
    return svg, k


def sc_gauge(p, a, d, data):
    k = K(p)
    lo, hi_, v = num(data.get("min")) or 0, num(data.get("max")) or 100, num(data.get("value")) or 0
    f = max(0, min(1, (v - lo) / ((hi_ - lo) or 1)))
    cx, cy, r = 600, 560, 330
    svg = stage(p, 600, 420, 330, 720, 430)
    arc = lambda r_: f"M{cx - r_},{cy} A{r_},{r_} 0 0 1 {cx + r_},{cy}"
    svg += (f'<g id="{p}-g">{P(arc(r), "", " style=\"fill:none;stroke:var(--line);stroke-width:60\"")}'
            f'<path id="{p}-ga" d="{arc(r)}" pathLength="1" stroke-dasharray="1" style="fill:none;stroke:var(--acc);stroke-width:60"/>'
            f'<g id="{p}-nd">{P(f"M{cx - 14},{cy} L{cx},{cy - r + 40} L{cx + 14},{cy} Z", "f3 s")}{C(cx, cy, 30, "dk s")}</g></g>'
            f'{TX(cx, 180, E(str(data.get("name", "")).upper()), 38, "txs", "middle", "", "h")}'
            f'{TX(cx, cy - 100, numtext(k, f"{p}-gv", data.get("value", ""), a + .5), 110, "tx", "middle", f" id=\"{p}-gv\"", "num")}')
    svg += src_tag(p, data.get("source"), 40, 790)
    stage_js(k, a, d, 600, 420)
    k.add(f'tl.fromTo("#{p}-ga",{{strokeDashoffset:1}},{{strokeDashoffset:{1 - f:.3f},duration:1.3,ease:"power2.out"}},{T(a + .4)})')
    k.add(f'tl.fromTo("#{p}-nd",{{rotation:-90,svgOrigin:"{cx} {cy}"}},{{rotation:{-90 + 180 * f:.1f},duration:1.3,ease:"back.out(1.4)"}},{T(a + .4)})')
    k.ev["punch"].append(a + 1.7); k.sfx(a + 1.7, "impact", .5)
    return svg, k


SCENES = dict(indices=sc_index, index=sc_index, flows=sc_flows, movers=sc_movers, announce=sc_announce, headline=sc_headline,
              world=sc_world, stat=sc_stat, dividend=sc_dividend, split=sc_split, bonus=sc_bonus, buyback=sc_buyback,
              ipo=sc_ipo, results=sc_results, calendar=sc_calendar, facts=sc_facts, gauge=sc_gauge)


def scene(kind, p, a, d, data):
    data = dict(data or {})
    if kind == "indices" and data.get("items") and not data.get("value"):   # old board format -> hero index + extras
        it = data["items"]; data.update(name=it[0]["name"], value=it[0]["value"], pct=it[0].get("pct"))
        data.setdefault("extra", [dict(label=x["name"], value=f'{x["value"]} ({"+" if (num(x.get("pct")) or 0) >= 0 else ""}{x.get("pct")}%)') for x in it[1:3]])
    if kind == "headline" and data.get("amount"): kind = "announce"
    fn = SCENES.get(kind, sc_headline)
    svg, k = fn(p, a, d, data)
    return svg, k.js, k.pre, k.ev
