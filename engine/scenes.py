"""Data scenes. Each renderer draws inside a box (w x h) and animates within the beat window [t, t+d].

render(kind, data, ctx, pid, w, h, t, d) -> html   (GSAP lines go to ctx.js, counter vars to ctx.pre, sounds to ctx.sfx)
Scene kinds and their data:
  headline  {kicker, text, sub}                         big kinetic headline
  stat      {label, value, prefix, suffix, dec, delta, tone, note}
  facts     {items:[{label, value, tone}]}              2-4 key-number cards
  indices   {items:[{name, value, pct}], asof}          index board
  movers    {gainers:[{name, pct}], losers:[...], asof}
  flows     {days:[{date, fii, dii}]}                   FII/DII bars, newest last
  dividend  {company, amount, kind, ex_date, record_date}
  split     {company, from_fv, to_fv, ex_date}
  bonus     {company, ratio, ex_date, record_date}
  buyback   {company, size, price, method}
  ipo       {company, open, close, band, size, lot, listing}
  results   {company, period, metrics:[{label, value, prev, unit, chg}]}    or upcoming: {company, date, purpose}
  calendar  {items:[{date, company, what, type}]}
  world     {items:[{name, value, pct}]}
  gauge     {name, value, min, max, pct}
Every scene shows ctx.source (or data.source) as a source chip.
"""
import math
from fx import C, E, T, icon, pop, counter, fmt, tone_col, source_chip, words, words_in


class Ctx:
    def __init__(self, rnd, V):
        self.rnd, self.V, self.js, self.pre, self.sfx = rnd, V, [], [], []


def _num(x):
    try: return float(str(x).replace(",", "").replace("₹", "").replace("%", "").replace("$", "").strip())
    except (TypeError, ValueError): return None


def _src(data, ctx, pid, w, h, t):
    s = data.get("source")
    if not s: return ""
    ctx.js.append(f'tl.fromTo("#{pid}-src",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4}},{T(t + .6)})')
    return f'<div class="ab" style="left:0;bottom:-6px">{source_chip([s] if isinstance(s, str) else s, f"{pid}-src", 22 if ctx.V else 20)}</div>'


# ---------------------------------------------------------------- headline
def headline(data, ctx, pid, w, h, t, d):
    st = ctx.rnd.choice(["rise", "drop", "zoom", "slide"])
    txt = data.get("text", ""); n_ch = len(txt.replace("*", ""))
    fs = (104 if n_ch < 28 else 86 if n_ch < 46 else 70) if ctx.V else (96 if n_ch < 34 else 78 if n_ch < 56 else 64)
    hw, n = words(txt, f"{pid}-w")
    kick = data.get("kicker", "")
    out = (f'<div class="ab" style="left:0;top:{h * .12:.0f}px;width:{w}px">'
           + (f'<span class="chip" id="{pid}-k" style="background:{ctx.host_color};color:#0B0B16;font-size:{26 if ctx.V else 24}px">{E(kick)}</span>' if kick else "")
           + f'<div class="slab" style="font-size:{fs}px;margin-top:26px;color:{C["ink"]}">{hw}</div>'
           + (f'<div id="{pid}-sub" style="font-family:SansM;font-size:{36 if ctx.V else 32}px;color:{C["sub"]};margin-top:22px;line-height:1.3">{E(data["sub"])}</div>' if data.get("sub") else "")
           + '</div>' + _src(data, ctx, pid, w, h, t))
    if kick: pop(ctx.js, f"#{pid}-k", t, "left")
    ctx.js += words_in(f"{pid}-w", n, t + .15, st)
    if data.get("sub"): pop(ctx.js, f"#{pid}-sub", t + .3 + n * .06, "up")
    ctx.sfx.append((t, "whoosh", .7))
    return out


# ---------------------------------------------------------------- stat (one hero number)
def stat(data, ctx, pid, w, h, t, d):
    v = _num(data.get("value")); tone = data.get("tone") or ("up" if (v or 0) >= 0 else "down")
    col = C["green"] if tone == "up" else C["red"] if tone == "down" else C["amber"]
    var = ctx.rnd.choice(["ring", "bar", "plain"] if len(str(data.get("value", ""))) + len(str(data.get("prefix", ""))) <= 5 else ["bar", "plain"])
    dec = int(data.get("dec", 0 if v is not None and float(v).is_integer() else 2))
    shown = f'{data.get("prefix", "")}{data.get("value")}{data.get("suffix", "")}'
    fs = min(190 if ctx.V else 170, w * 1.55 / max(1, len(shown)))
    num = (f'<div class="mono" id="{pid}-n" style="font-size:{fs}px;font-weight:500;color:{col};letter-spacing:-6px;line-height:1">'
           f'{E(shown)}</div>')
    deco = ""
    if var == "ring":
        r = min(w, h) * .42
        deco = (f'<svg class="ab" style="left:{w / 2 - r - 20:.0f}px;top:{h * .46 - r - 20:.0f}px" width="{2 * r + 40:.0f}" height="{2 * r + 40:.0f}">'
                f'<circle cx="{r + 20:.0f}" cy="{r + 20:.0f}" r="{r:.0f}" fill="none" stroke="{C["line"]}" stroke-width="16"/>'
                f'<circle id="{pid}-ring" cx="{r + 20:.0f}" cy="{r + 20:.0f}" r="{r:.0f}" fill="none" stroke="{col}" stroke-width="16" stroke-linecap="round" '
                f'pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" transform="rotate(-90 {r + 20:.0f} {r + 20:.0f})"/></svg>')
        ctx.js.append(f'tl.to("#{pid}-ring",{{strokeDashoffset:.18,duration:1.4,ease:"power2.out"}},{T(t + .1)})')
    elif var == "bar":
        deco = f'<div class="ab" id="{pid}-bar" style="left:{w * .15:.0f}px;top:{h * .70:.0f}px;width:{w * .7:.0f}px;height:14px;border-radius:7px;background:{col}"></div>'
        ctx.js.append(f'tl.fromTo("#{pid}-bar",{{scaleX:0}},{{scaleX:1,duration:1.0,ease:"power3.out"}},{T(t + .2)})')
    out = (deco + f'<div class="ab" style="left:0;width:{w}px;top:{h * .46 - fs * .62:.0f}px;text-align:center">'
           f'<div class="chip" id="{pid}-l" style="background:rgba(255,255,255,.07);color:{C["ink"]};font-size:{26 if ctx.V else 24}px">{E(data.get("label", ""))}</div>'
           f'<div style="margin-top:14px">{num}</div>'
           + (f'<div class="chip" id="{pid}-dl" style="margin-top:14px;background:{col}22;color:{col};font-size:{30 if ctx.V else 26}px">{E(data["delta"])}</div>' if data.get("delta") else "")
           + (f'<div id="{pid}-nt" style="font-family:SansM;color:{C["sub"]};font-size:{28 if ctx.V else 24}px;margin-top:16px">{E(data["note"])}</div>' if data.get("note") else "")
           + '</div>' + _src(data, ctx, pid, w, h, t))
    pop(ctx.js, f"#{pid}-l", t, "down")
    if v is not None:
        counter(ctx.js, ctx.pre, f"{pid}-n", v, t + .15, dec, str(data.get("prefix", "")), str(data.get("suffix", "")), 1.3)
    else:
        pop(ctx.js, f"#{pid}-n", t + .15, "scale")
    if data.get("delta"): pop(ctx.js, f"#{pid}-dl", t + 1.3, "scale")
    if data.get("note"): pop(ctx.js, f"#{pid}-nt", t + 1.6, "fade")
    ctx.sfx.append((t + .15, "riser", .5)); ctx.sfx.append((t + 1.4, "pop", .6))
    return out


# ---------------------------------------------------------------- facts (2-4 cards)
def facts(data, ctx, pid, w, h, t, d):
    items = data.get("items", [])[:4]; n = len(items); out = []
    cols = 1 if ctx.V and n <= 2 else 2 if n > 1 else 1
    if not ctx.V: cols = min(n, 4) if n <= 4 else 2
    rows = math.ceil(n / cols); g = 24; bh = min(260, (h - 70 - g * (rows - 1)) / rows); bw = (w - g * (cols - 1)) / cols
    for i, it in enumerate(items):
        r, c = divmod(i, cols); x = c * (bw + g); y = r * (bh + g)
        col = {"up": C["green"], "down": C["red"]}.get(it.get("tone"), ctx.host_color)
        val = str(it.get("value", "")); vs = 74 if len(val) <= 8 else 56 if len(val) <= 12 else 44
        out.append(f'<div class="pnl" id="{pid}-f{i}" style="left:{x:.0f}px;top:{y:.0f}px;width:{bw:.0f}px;height:{bh:.0f}px;padding:26px 30px;border-top:6px solid {col}">'
                   f'<div style="font-family:Sans;font-weight:800;letter-spacing:2px;text-transform:uppercase;font-size:{24 if ctx.V else 22}px;color:{C["sub"]}">{E(it.get("label", ""))}</div>'
                   f'<div class="mono" style="font-size:{vs}px;color:{col};margin-top:14px;letter-spacing:-2px">{E(val)}</div>'
                   + (f'<div style="font-family:SansM;font-size:22px;color:{C["sub"]};margin-top:8px">{E(it["note"])}</div>' if it.get("note") else "") + '</div>')
        pop(ctx.js, f"#{pid}-f{i}", t + .2 + i * d * .6 / max(1, n), ctx.rnd.choice(["up", "scale", "flip"]))
        ctx.sfx.append((t + .2 + i * d * .6 / max(1, n), "tick", .7))
    return "".join(out) + _src(data, ctx, pid, w, h, t)


# ---------------------------------------------------------------- index board
def indices(data, ctx, pid, w, h, t, d):
    items = data.get("items", [])[:6]; n = len(items); out = []
    ladder = ctx.rnd.random() < .5 and n >= 3
    if ladder:
        rh = min(130, (h - 80) / n)
        for i, it in enumerate(items):
            pc = _num(it.get("pct")) or 0; col = tone_col(pc)
            out.append(f'<div class="pnl" id="{pid}-i{i}" style="left:0;top:{i * (rh + 10):.0f}px;width:{w}px;height:{rh:.0f}px;display:flex;align-items:center;padding:0 30px;gap:20px">'
                       f'<span style="flex:1;font-family:Sans;font-weight:800;font-size:{32 if ctx.V else 30}px;letter-spacing:1px">{E(it["name"])}</span>'
                       f'<span class="mono" id="{pid}-v{i}" style="font-size:{44 if ctx.V else 40}px">{E(str(it.get("value", "")))}</span>'
                       f'<span class="chip" style="background:{col}22;color:{col};font-size:26px;min-width:150px;justify-content:center">{"▲" if pc > 0 else "▼" if pc < 0 else "■"} {abs(pc):.2f}%</span></div>')
            pop(ctx.js, f"#{pid}-i{i}", t + .1 + i * .18, "left")
            vv = _num(it.get("value"))
            if vv is not None: counter(ctx.js, ctx.pre, f"{pid}-v{i}", vv, t + .1 + i * .18, 2, "", "", 1.0)
    else:
        cols = 2 if ctx.V else (3 if n in (3, 5, 6) else 2); rows = math.ceil(n / cols); g = 22
        bw = (w - g * (cols - 1)) / cols; bh = min(250, (h - 70 - g * (rows - 1)) / rows)
        for i, it in enumerate(items):
            r, c = divmod(i, cols); pc = _num(it.get("pct")) or 0; col = tone_col(pc)
            out.append(f'<div class="pnl{" glow" if i == 0 else ""}" id="{pid}-i{i}" style="left:{c * (bw + g):.0f}px;top:{r * (bh + g):.0f}px;width:{bw:.0f}px;height:{bh:.0f}px;padding:24px 28px">'
                       f'<div style="font-family:Sans;font-weight:800;font-size:{26 if ctx.V else 24}px;letter-spacing:2px;color:{C["sub"]}">{E(it["name"])}</div>'
                       f'<div class="mono" id="{pid}-v{i}" style="font-size:{60 if ctx.V else 56}px;margin-top:10px;letter-spacing:-2px">{E(str(it.get("value", "")))}</div>'
                       f'<div class="chip" style="margin-top:10px;background:{col}22;color:{col};font-size:26px">{"▲" if pc > 0 else "▼" if pc < 0 else "■"} {abs(pc):.2f}%</div>'
                       f'<div class="ab" id="{pid}-b{i}" style="left:0;bottom:0;height:6px;width:{min(100, 30 + abs(pc) * 40):.0f}%;background:{col};border-radius:0 6px 0 26px"></div></div>')
            pop(ctx.js, f"#{pid}-i{i}", t + .1 + i * .16, "scale")
            ctx.js.append(f'tl.fromTo("#{pid}-b{i}",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,duration:.8,ease:"power3.out"}},{T(t + .4 + i * .16)})')
            vv = _num(it.get("value"))
            if vv is not None: counter(ctx.js, ctx.pre, f"{pid}-v{i}", vv, t + .1 + i * .16, 2, "", "", 1.0)
    for i in range(n): ctx.sfx.append((t + .1 + i * .17, "tick", .6))
    if data.get("asof"):
        out.append(f'<div class="ab" id="{pid}-as" style="right:0;bottom:-4px;font-family:SansM;font-size:20px;color:{C["sub"]}">{E(data["asof"])}</div>')
        pop(ctx.js, f"#{pid}-as", t + .8, "fade")
    return "".join(out) + _src(data, ctx, pid, w, h, t)


# ---------------------------------------------------------------- movers
def movers(data, ctx, pid, w, h, t, d):
    G = data.get("gainers", [])[:5]; L = data.get("losers", [])[:5]; out = []
    mx = max([abs(_num(s["pct"]) or 0) for s in G + L] + [1])
    style = ctx.rnd.choice(["bars", "bubbles"]) if not ctx.V else "bars"
    if style == "bubbles":
        allm = [(s, 1) for s in G] + [(s, -1) for s in L]; n = len(allm)
        for i, (s, sg) in enumerate(allm):
            pc = abs(_num(s["pct"]) or 0); r = 50 + 70 * pc / mx; col = C["green"] if sg > 0 else C["red"]
            x = (w * .25 if sg > 0 else w * .75) + ctx.rnd.uniform(-w * .17, w * .17); y = (i % max(1, len(G) if sg > 0 else len(L))) * (h - 120) / 5 + 90
            out.append(f'<div class="ab" id="{pid}-u{i}" style="left:{x - r:.0f}px;top:{y - r * .6:.0f}px;width:{2 * r:.0f}px;height:{2 * r:.0f}px;border-radius:50%;'
                       f'background:radial-gradient(circle at 35% 30%,{col}cc,{col}55);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;box-shadow:0 0 30px {col}44">'
                       f'<span style="font-family:Sans;font-weight:800;font-size:{max(16, r * .26):.0f}px;color:#fff;line-height:1.05;padding:0 8px">{E(s["name"])}</span>'
                       f'<span class="mono" style="font-size:{max(18, r * .3):.0f}px;color:#fff">{"+" if sg > 0 else "-"}{pc:.2f}%</span></div>')
            pop(ctx.js, f"#{pid}-u{i}", t + .15 + i * .12, "scale"); ctx.sfx.append((t + .15 + i * .12, "pop", .45))
        out.append(f'<div class="ab chip" style="left:0;top:0;background:{C["green"]}22;color:{C["green"]};font-size:22px">Top gainers</div>'
                   f'<div class="ab chip" style="right:0;top:0;background:{C["red"]}22;color:{C["red"]};font-size:22px">Top losers</div>')
    else:
        panels = [("Top gainers", G, C["green"], 1), ("Top losers", L, C["red"], -1)]
        if ctx.V: geo = [(0, 0, w, h * .48), (0, h * .5, w, h * .46)]
        else: geo = [(0, 0, w * .49, h - 50), (w * .51, 0, w * .49, h - 50)]
        for pi, ((lab, lst, col, sg), (x, y, pw, ph)) in enumerate(zip(panels, geo)):
            if not lst: continue
            rh = min(78, (ph - 70) / len(lst)); nw = pw * .42
            out.append(f'<div class="pnl" id="{pid}-p{pi}" style="left:{x:.0f}px;top:{y:.0f}px;width:{pw:.0f}px;height:{ph:.0f}px">'
                       f'<div class="ab chip" style="left:24px;top:18px;background:{col}22;color:{col};font-size:20px">{icon("trending-up" if sg > 0 else "trending-down", 22, col)}{lab}</div>')
            for k, s in enumerate(lst):
                pc = abs(_num(s["pct"]) or 0); bw = max(14, (pw - nw - 170) * pc / mx)
                out.append(f'<div class="ab" style="left:24px;top:{74 + k * rh:.0f}px;display:flex;align-items:center;gap:14px">'
                           f'<span style="width:{nw:.0f}px;font-family:Sans;font-weight:800;font-size:{30 if ctx.V else 26}px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{E(s["name"])}</span>'
                           f'<span id="{pid}-b{pi}{k}" style="width:{bw:.0f}px;height:{rh * .5:.0f}px;border-radius:10px;background:linear-gradient(90deg,{col}66,{col})"></span>'
                           f'<span class="mono" id="{pid}-v{pi}{k}" style="font-size:{30 if ctx.V else 26}px;color:{col}">0</span></div>')
                tt = t + (.1 if pi == 0 else d * .45) + k * .12
                ctx.js.append(f'tl.fromTo("#{pid}-b{pi}{k}",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,duration:.7,ease:"power3.out"}},{T(tt)})')
                counter(ctx.js, ctx.pre, f"{pid}-v{pi}{k}", pc, tt, 2, "+" if sg > 0 else "-", "%", .7)
                ctx.sfx.append((tt, "tick", .5))
            out.append('</div>')
            pop(ctx.js, f"#{pid}-p{pi}", t + (0 if pi == 0 else d * .45) - .05, "left" if pi == 0 else "right")
    if data.get("asof"):
        out.append(f'<div class="ab" style="right:0;bottom:-4px;font-family:SansM;font-size:20px;color:{C["sub"]}">{E(data["asof"])}</div>')
    return "".join(out) + _src(data, ctx, pid, w, h, t)


# ---------------------------------------------------------------- FII / DII flows
def flows(data, ctx, pid, w, h, t, d):
    days = data.get("days", [])[-8:]; n = len(days); out = []
    if not n: return ""
    mx = max([abs(x.get("fii", 0)) for x in days] + [abs(x.get("dii", 0)) for x in days] + [1])
    ch = h - 150; zero = 60 + ch / 2; gw = w / n; bw = min(34, gw * .32)
    svg = [f'<line x1="0" y1="{zero:.0f}" x2="{w}" y2="{zero:.0f}" stroke="{C["dim"]}" stroke-width="2"/>']
    for i, dday in enumerate(days):
        cx = gw * (i + .5)
        for k, (key, col) in enumerate((("fii", C["blue"]), ("dii", C["amber"]))):
            v = dday.get(key, 0) or 0; bh = max(2, (ch / 2 - 10) * abs(v) / mx); x = cx + (k - 1) * (bw + 4) + 2
            y = zero - bh if v >= 0 else zero
            last = i == n - 1
            svg.append(f'<rect id="{pid}-r{i}{k}" x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{bh:.0f}" rx="6" fill="{col}" opacity="{1 if last else .55}"/>')
            ctx.js.append(f'tl.fromTo("#{pid}-r{i}{k}",{{scaleY:0,transformOrigin:"50% {"100%" if v >= 0 else "0%"}"}},{{scaleY:1,duration:.5,ease:"back.out(1.6)"}},{T(t + .2 + i * .1 + k * .04)})')
        svg.append(f'<text x="{cx:.0f}" y="{h - 70:.0f}" text-anchor="middle" font-family="Mono" font-size="{20 if ctx.V else 18}" fill="{C["sub"]}">{E(str(dday.get("date", "")))}</text>')
    last = days[-1]
    out.append(f'<svg class="ab" style="left:0;top:0;overflow:visible" width="{w}" height="{h}">{"".join(svg)}</svg>')
    leg = (f'<div class="ab" style="left:0;top:0;display:flex;gap:16px">'
           f'<span class="chip" style="background:{C["blue"]}22;color:{C["blue"]};font-size:20px">FII / FPI</span>'
           f'<span class="chip" style="background:{C["amber"]}22;color:{C["amber"]};font-size:20px">DII</span>'
           f'<span class="chip" style="background:rgba(255,255,255,.06);color:{C["sub"]};font-size:20px">₹ crore · cash</span></div>')
    out.append(leg)
    lx = w - 360 if not ctx.V else w - 380
    out.append(f'<div class="pnl glow" id="{pid}-lt" style="left:{lx}px;top:66px;width:{360 if not ctx.V else 380}px;padding:18px 24px">'
               f'<div style="font-family:Sans;font-weight:800;font-size:20px;letter-spacing:2px;color:{C["sub"]}">LATEST · {E(str(last.get("date", "")))}</div>'
               f'<div class="mono" style="font-size:34px;color:{C["blue"]};margin-top:6px">FII {"+" if last.get("fii", 0) >= 0 else "-"}₹{fmt(abs(last.get("fii", 0)), 0)} cr</div>'
               f'<div class="mono" style="font-size:34px;color:{C["amber"]}">DII {"+" if last.get("dii", 0) >= 0 else "-"}₹{fmt(abs(last.get("dii", 0)), 0)} cr</div></div>')
    pop(ctx.js, f"#{pid}-lt", t + .3 + n * .1, "scale"); ctx.sfx.append((t + .3 + n * .1, "pop", .6))
    return "".join(out) + _src(data, ctx, pid, w, h, t)


# ---------------------------------------------------------------- dividend: coin rain + amount + dates
def dividend(data, ctx, pid, w, h, t, d):
    amt = str(data.get("amount", "")); out = []
    coins = ""
    for i in range(14):
        x = ctx.rnd.uniform(w * .05, w * .95); delay = ctx.rnd.uniform(0, .9); r = ctx.rnd.uniform(20, 34)
        coins += (f'<div class="ab" id="{pid}-c{i}" style="left:{x:.0f}px;top:-60px;width:{2 * r:.0f}px;height:{2 * r:.0f}px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFE59A,#F5C542 55%,#B7791F);'
                  f'border:3px solid #8A6510;display:flex;align-items:center;justify-content:center;font-family:Mono;font-size:{r:.0f}px;color:#8A6510">₹</div>')
        ctx.js.append(f'tl.fromTo("#{pid}-c{i}",{{y:-80,rotation:0,opacity:1}},{{y:{h * ctx.rnd.uniform(.75, 1.05):.0f},rotation:{ctx.rnd.choice([-1, 1]) * 360},opacity:0,duration:1.6,ease:"power1.in"}},{T(t + .1 + delay)})')
    out.append(f'<div class="ab" style="inset:0;overflow:hidden">{coins}</div>')
    out.append(f'<div class="ab" style="left:0;top:{h * .08:.0f}px;width:{w}px;text-align:center">'
               f'<div style="font-family:Sans;font-weight:800;font-size:{30 if ctx.V else 26}px;letter-spacing:3px;color:{C["sub"]}">{E(data.get("company", "")).upper()}</div>'
               f'<div class="chip" style="margin-top:12px;background:#F5C54222;color:#F5C542;font-size:24px">{E(data.get("type", ""))} dividend</div>'
               f'<div class="mono" id="{pid}-a" style="font-size:{170 if ctx.V else 150}px;color:#F5C542;letter-spacing:-6px;margin-top:10px;text-shadow:0 0 40px #F5C54255">{E(amt)}</div>'
               f'<div style="font-family:SansM;font-size:{30 if ctx.V else 26}px;color:{C["sub"]}">per share</div></div>')
    pop(ctx.js, f"#{pid}-a", t + .4, "scale", .6)
    dates = [(lab, data.get(k)) for lab, k in (("Ex-date", "ex_date"), ("Record date", "record_date")) if data.get(k)]
    for i, (lab, val) in enumerate(dates):
        x = w / 2 - (len(dates) * 300 + (len(dates) - 1) * 24) / 2 + i * 324
        out.append(f'<div class="pnl" id="{pid}-d{i}" style="left:{x:.0f}px;top:{h * .66:.0f}px;width:300px;padding:16px 20px;text-align:center;transform:rotate({-3 if i == 0 else 3}deg)">'
                   f'<div style="font-family:Sans;font-weight:800;font-size:20px;letter-spacing:2px;color:{C["sub"]}">{lab.upper()}</div>'
                   f'<div class="mono" style="font-size:36px;margin-top:6px">{E(str(val))}</div></div>')
        ctx.js.append(f'tl.fromTo("#{pid}-d{i}",{{scale:2.2,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"power4.in"}},{T(t + 1.2 + i * .35)})')
        ctx.sfx.append((t + 1.5 + i * .35, "pop", .7))
    for k in range(3): ctx.sfx.append((t + .3 + k * .25, "coin", .5))
    return "".join(out) + _src(data, ctx, pid, w, h, t)


# ---------------------------------------------------------------- split: a share bar sliced into pieces
def split(data, ctx, pid, w, h, t, d):
    f0, f1 = _num(data.get("from_fv")), _num(data.get("to_fv"))
    n = int(round(f0 / f1)) if f0 and f1 and f1 > 0 and f0 / f1 <= 20 else 2
    out = [f'<div class="ab" style="left:0;top:0;width:{w}px;text-align:center;font-family:Sans;font-weight:800;font-size:{30 if ctx.V else 26}px;letter-spacing:3px;color:{C["sub"]}">{E(data.get("company", "")).upper()}</div>']
    bx, by, bw, bh = w * .08, h * .2, w * .84, h * .3; pw = bw / n
    for i in range(n):
        out.append(f'<div class="ab" id="{pid}-s{i}" style="left:{bx + i * pw:.0f}px;top:{by:.0f}px;width:{pw:.0f}px;height:{bh:.0f}px;'
                   f'background:linear-gradient(160deg,#F7F3EA,#E9D6AE);border:3px solid #0B0B16;display:flex;align-items:center;justify-content:center">'
                   f'<span class="mono" style="font-size:{min(60, pw * .4):.0f}px;color:#0B1A44">{E(str(data.get("to_fv", "")))}</span></div>')
        ctx.js.append(f'tl.fromTo("#{pid}-s{i}",{{x:0,rotation:0}},{{x:{(i - (n - 1) / 2) * 18:.0f},rotation:{(i - (n - 1) / 2) * 2:.1f},duration:.5,ease:"back.out(2)"}},{T(t + 1.3)})')
    out.append(f'<div class="ab" id="{pid}-whole" style="left:{bx:.0f}px;top:{by:.0f}px;width:{bw:.0f}px;height:{bh:.0f}px;background:linear-gradient(160deg,#F7F3EA,#E9D6AE);border:3px solid #0B0B16;'
               f'display:flex;align-items:center;justify-content:center"><span class="mono" style="font-size:90px;color:#0B1A44">{E(str(data.get("from_fv", "")))}</span></div>')
    ctx.js.append(f'tl.to("#{pid}-whole",{{opacity:0,duration:.15}},{T(t + 1.2)})')
    knife = f'<div class="ab" id="{pid}-kn" style="left:{bx:.0f}px;top:{by - 40:.0f}px;width:6px;height:{bh + 80:.0f}px;background:#fff;box-shadow:0 0 20px #fff"></div>'
    out.append(knife)
    ctx.js.append(f'tl.fromTo("#{pid}-kn",{{x:0,opacity:1}},{{x:{bw:.0f},opacity:0,duration:.8,ease:"power2.inOut"}},{T(t + .4)})')
    ctx.sfx.append((t + .4, "whoosh", .8))
    out.append(f'<div class="ab" id="{pid}-lb" style="left:0;top:{by + bh + 40:.0f}px;width:{w}px;text-align:center">'
               f'<span class="slab" style="font-size:{64 if ctx.V else 56}px">Face value <span class="mono" style="color:{C["amber"]}">{E(str(data.get("from_fv", "")))}</span> → '
               f'<span class="mono" style="color:{C["green"]}">{E(str(data.get("to_fv", "")))}</span></span>'
               + (f'<div style="font-family:SansM;font-size:28px;color:{C["sub"]};margin-top:14px">1 share becomes {n} · ex-date {E(str(data.get("ex_date")))}</div>' if data.get("ex_date") else "")
               + '</div>')
    pop(ctx.js, f"#{pid}-lb", t + 1.7, "up"); ctx.sfx.append((t + 1.3, "pop", .7))
    return "".join(out) + _src(data, ctx, pid, w, h, t)


# ---------------------------------------------------------------- bonus: 1 share card -> ratio of new cards pops out
def bonus(data, ctx, pid, w, h, t, d):
    ratio = str(data.get("ratio", "1:1")); a, _, b = ratio.partition(":")
    try: na, nb = int(a), int(b)
    except ValueError: na, nb = 1, 1
    na, nb = min(na, 5), min(nb, 5)
    out = [f'<div class="ab" style="left:0;top:0;width:{w}px;text-align:center;font-family:Sans;font-weight:800;font-size:{30 if ctx.V else 26}px;letter-spacing:3px;color:{C["sub"]}">{E(data.get("company", "")).upper()}</div>',
           f'<div class="ab slab" id="{pid}-r" style="left:0;top:{h * .1:.0f}px;width:{w}px;text-align:center;font-size:{150 if ctx.V else 130}px;color:{C["green"]};text-shadow:0 0 40px {C["green"]}55">{E(ratio)}</div>']
    pop(ctx.js, f"#{pid}-r", t + .1, "scale", .6)
    cw, chh = 120, 160; total = na + nb; x0 = w / 2 - (total * cw + (total - 1) * 20) / 2; y = h * .48
    for i in range(total):
        new = i >= nb
        col = C["green"] if new else "#CBD5E1"
        out.append(f'<div class="ab" id="{pid}-k{i}" style="left:{x0 + i * (cw + 20):.0f}px;top:{y:.0f}px;width:{cw}px;height:{chh}px;border-radius:16px;'
                   f'background:{"linear-gradient(160deg,#00ff88,#00b862)" if new else "linear-gradient(160deg,#F8FAFC,#CBD5E1)"};border:3px solid #0B0B16;'
                   f'display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:Sans;font-weight:800;color:#0B0B16">'
                   f'<span style="font-size:22px">{"BONUS" if new else "HELD"}</span><span class="mono" style="font-size:44px">1</span></div>')
        if new:
            ctx.js.append(f'tl.fromTo("#{pid}-k{i}",{{y:-160,scale:0,rotation:-20}},{{y:0,scale:1,rotation:0,duration:.55,ease:"back.out(2)"}},{T(t + 1.0 + (i - nb) * .25)})')
            ctx.sfx.append((t + 1.0 + (i - nb) * .25, "pop", .7))
        else: pop(ctx.js, f"#{pid}-k{i}", t + .5 + i * .1, "up")
    out.append(f'<div class="ab" id="{pid}-x" style="left:0;top:{y + chh + 36:.0f}px;width:{w}px;text-align:center;font-family:SansM;font-size:{30 if ctx.V else 26}px;color:{C["sub"]}">'
               f'{nb} bonus share{"s" if nb > 1 else ""} for every {na} held'
               + (f' · record date {E(str(data["record_date"]))}' if data.get("record_date") else f' · ex-date {E(str(data["ex_date"]))}' if data.get("ex_date") else "") + '</div>')
    pop(ctx.js, f"#{pid}-x", t + 1.6, "fade")
    return "".join(out) + _src(data, ctx, pid, w, h, t)


# ---------------------------------------------------------------- generic company card for buyback / ipo
def _rows_card(data, ctx, pid, w, h, t, d, rows, badge, col):
    rows = [(k, v) for k, v in rows if v]
    out = [f'<div class="pnl glow" id="{pid}-c" style="left:0;top:0;width:{w}px;height:{h - 60:.0f}px;padding:34px 40px;border-top:8px solid {col}">'
           f'<div class="chip" style="background:{col};color:#0B0B16;font-size:22px">{E(badge)}</div>'
           f'<div class="slab" style="font-size:{60 if ctx.V else 54}px;margin-top:18px">{E(data.get("company", ""))}</div>']
    rh = min(92, (h - 300) / max(1, len(rows)))
    for i, (k, v) in enumerate(rows):
        out.append(f'<div id="{pid}-row{i}" style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid {C["line"]};padding:{(rh - 50) / 2:.0f}px 0">'
                   f'<span style="font-family:SansM;font-size:{30 if ctx.V else 26}px;color:{C["sub"]}">{E(k)}</span>'
                   f'<span class="mono" style="font-size:{40 if ctx.V else 34}px">{E(str(v))}</span></div>')
        pop(ctx.js, f"#{pid}-row{i}", t + .4 + i * d * .5 / max(1, len(rows)), "left")
        ctx.sfx.append((t + .4 + i * d * .5 / max(1, len(rows)), "tick", .6))
    out.append('</div>')
    pop(ctx.js, f"#{pid}-c", t, "scale")
    return "".join(out) + _src(data, ctx, pid, w, h, t)


def buyback(data, ctx, pid, w, h, t, d):
    return _rows_card(data, ctx, pid, w, h, t, d, [("Buyback size", data.get("size")), ("Price", data.get("price")),
                                                   ("Method", data.get("method")), ("Record date", data.get("record_date"))], "Buyback", "#FACC15")


def ipo(data, ctx, pid, w, h, t, d):
    return _rows_card(data, ctx, pid, w, h, t, d, [("Opens", data.get("open")), ("Closes", data.get("close")), ("Price band", data.get("band")),
                                                   ("Issue size", data.get("size")), ("Lot", data.get("lot")), ("Listing", data.get("listing"))], "IPO", C["blue"])


# ---------------------------------------------------------------- results: metric bars (this vs last) or upcoming meeting
def results(data, ctx, pid, w, h, t, d):
    ms = data.get("metrics") or []
    if not ms:
        return _rows_card(data, ctx, pid, w, h, t, d, [("Board meeting", data.get("date")), ("Agenda", data.get("purpose"))], "Results due", C["violet"])
    out = [f'<div class="ab" style="left:0;top:0"><div class="chip" style="background:{C["violet"]};color:#fff;font-size:22px">{E(data.get("period", "Results"))}</div>'
           f'<div class="slab" style="font-size:{58 if ctx.V else 52}px;margin-top:14px">{E(data.get("company", ""))}</div></div>']
    n = min(3, len(ms)); gw = w / n
    for i, m in enumerate(ms[:3]):
        cur, prev = _num(m.get("value")), _num(m.get("prev"))
        top = 190; ch = h - top - 150; mx = max(abs(cur or 0), abs(prev or 0), 1)
        col = tone_col((cur or 0) - (prev or 0)) if prev is not None else C["green"]
        bars = ""
        for k, (lab, v, c2) in enumerate((("Last year", prev, C["dim"]), ("Now", cur, col))):
            if v is None: continue
            bh = ch * abs(v) / mx; x = gw * i + gw * (.18 + k * .36)
            bars += (f'<div class="ab" id="{pid}-b{i}{k}" style="left:{x:.0f}px;top:{top + ch - bh:.0f}px;width:{gw * .28:.0f}px;height:{bh:.0f}px;border-radius:12px 12px 4px 4px;background:{c2}"></div>'
                     f'<div class="ab" style="left:{x - 20:.0f}px;width:{gw * .28 + 40:.0f}px;text-align:center;top:{top + ch + 8:.0f}px;font-family:SansM;font-size:20px;color:{C["sub"]}">{lab}</div>')
            ctx.js.append(f'tl.fromTo("#{pid}-b{i}{k}",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:.7,ease:"power3.out"}},{T(t + .3 + i * .5 + k * .25)})')
        out.append(bars)
        out.append(f'<div class="ab" style="left:{gw * i:.0f}px;width:{gw:.0f}px;top:{top + ch + 44:.0f}px;text-align:center">'
                   f'<div style="font-family:Sans;font-weight:800;font-size:{26 if ctx.V else 22}px;letter-spacing:2px;color:{C["sub"]}">{E(m.get("label", "")).upper()}</div>'
                   f'<div class="mono" style="font-size:{36 if ctx.V else 30}px">{E(str(m.get("value", "")))}{(" " + E(m["unit"])) if m.get("unit") else ""}'
                   + (f' <span style="color:{col}">{E(m["chg"])}</span>' if m.get("chg") else "") + '</div></div>')
        ctx.sfx.append((t + .3 + i * .5, "tick", .6))
    return "".join(out) + _src(data, ctx, pid, w, h, t)


# ---------------------------------------------------------------- calendar list
def calendar(data, ctx, pid, w, h, t, d):
    items = data.get("items", [])[:6]; n = len(items); out = []
    rh = min(150, (h - 60) / max(1, n)) - 14
    for i, it in enumerate(items):
        dt = str(it.get("date", "")); day, _, mon = dt.partition(" ")
        col = {"DIVIDEND": "#F5C542", "RESULTS": C["violet"], "BONUS": "#2DD4BF", "SPLIT": "#E9D6AE", "IPO": C["blue"]}.get(str(it.get("type", "")).upper(), C["green"])
        out.append(f'<div class="pnl" id="{pid}-e{i}" style="left:0;top:{i * (rh + 14):.0f}px;width:{w}px;height:{rh:.0f}px;display:flex;align-items:center;gap:24px;padding:0 22px">'
                   f'<div style="flex:0 0 {rh * .9:.0f}px;height:{rh * .78:.0f}px;border-radius:14px;background:#F8FAFC;overflow:hidden;text-align:center">'
                   f'<div style="background:#EF4444;color:#fff;font-family:Sans;font-weight:800;font-size:{rh * .14:.0f}px;letter-spacing:2px;padding:2px 0">{E(mon.upper() or "DATE")}</div>'
                   f'<div class="slab" style="color:#0B1A44;font-size:{rh * .36:.0f}px;line-height:1.2">{E(day)}</div></div>'
                   f'<div style="flex:1;min-width:0"><div style="font-family:Sans;font-weight:800;font-size:{min(38, rh * .3):.0f}px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{E(it.get("company", ""))}</div>'
                   f'<div style="font-family:SansM;font-size:{min(28, rh * .22):.0f}px;color:{C["sub"]};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{E(it.get("what", ""))}</div></div>'
                   f'<span class="chip" style="background:{col}22;color:{col};font-size:18px">{E(str(it.get("type", "")).title())}</span></div>')
        ctx.js.append(f'tl.fromTo("#{pid}-e{i}",{{rotationX:-90,opacity:0,transformOrigin:"50% 0%"}},{{rotationX:0,opacity:1,duration:.45,ease:"back.out(1.6)"}},{T(t + .1 + i * d * .7 / max(1, n))})')
        ctx.sfx.append((t + .1 + i * d * .7 / max(1, n), "tick", .6))
    return "".join(out) + _src(data, ctx, pid, w, h, t)


# ---------------------------------------------------------------- world / commodities tiles
def world(data, ctx, pid, w, h, t, d):
    return indices(dict(data, items=data.get("items", [])), ctx, pid, w, h, t, d)


# ---------------------------------------------------------------- gauge (e.g. India VIX)
def gauge(data, ctx, pid, w, h, t, d):
    v, lo, hi = _num(data.get("value")) or 0, _num(data.get("min")) or 0, _num(data.get("max")) or 40
    f = max(0, min(1, (v - lo) / (hi - lo))); r = min(w * .42, h * .6); cx, cy = w / 2, h * .66
    ang = -180 + 180 * f
    arc = f'M{cx - r:.0f},{cy:.0f} A{r:.0f},{r:.0f} 0 0 1 {cx + r:.0f},{cy:.0f}'
    out = (f'<svg class="ab" style="left:0;top:0;overflow:visible" width="{w}" height="{h}"><defs><linearGradient id="{pid}-g"><stop offset="0" stop-color="{C["green"]}"/>'
           f'<stop offset=".55" stop-color="{C["amber"]}"/><stop offset="1" stop-color="{C["red"]}"/></linearGradient></defs>'
           f'<path d="{arc}" fill="none" stroke="{C["line"]}" stroke-width="34" stroke-linecap="round"/>'
           f'<path id="{pid}-a" d="{arc}" fill="none" stroke="url(#{pid}-g)" stroke-width="34" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>'
           f'<g id="{pid}-nd"><line x1="{cx:.0f}" y1="{cy:.0f}" x2="{cx + r * .82:.0f}" y2="{cy:.0f}" stroke="{C["ink"]}" stroke-width="10" stroke-linecap="round"/>'
           f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="20" fill="{C["ink"]}"/></g></svg>'
           f'<div class="ab" style="left:0;width:{w}px;top:{cy + 30:.0f}px;text-align:center"><div class="mono" id="{pid}-v" style="font-size:90px">{fmt(v)}</div>'
           f'<div style="font-family:Sans;font-weight:800;font-size:24px;letter-spacing:3px;color:{C["sub"]}">{E(data.get("name", "")).upper()}'
           + (f' · <span style="color:{tone_col(_num(data.get("pct")) or 0)}">{E(str(data.get("pct")))}%</span>' if data.get("pct") is not None else "") + '</div></div>')
    ctx.js.append(f'tl.to("#{pid}-a",{{strokeDashoffset:{1 - f:.3f},duration:1.2,ease:"power2.out"}},{T(t + .2)})')
    ctx.js.append(f'tl.fromTo("#{pid}-nd",{{rotation:-180,svgOrigin:"{cx:.0f} {cy:.0f}"}},{{rotation:{ang:.1f},svgOrigin:"{cx:.0f} {cy:.0f}",duration:1.4,ease:"elastic.out(1,.5)"}},{T(t + .2)})')
    counter(ctx.js, ctx.pre, f"{pid}-v", v, t + .2, 2, "", "", 1.2)
    return out + _src(data, ctx, pid, w, h, t)


RENDER = dict(headline=headline, stat=stat, facts=facts, indices=indices, movers=movers, flows=flows, dividend=dividend, split=split,
              bonus=bonus, buyback=buyback, ipo=ipo, results=results, calendar=calendar, world=world, gauge=gauge)
