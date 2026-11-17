"""Builds one HyperFrames project per video from a job file (written each slot by the daily task).

Short (1080x1920) follows the 9:16 safe band (nothing readable above 168 px or below 1330 px):
  frame-0 hook · scene stage · host + kinetic captions · spoken end CTA (subscribe click + bell + marketsamachar.in).
Long (1920x1080): scene stage + host with kinetic captions, ticker, desk title cards, spoken end CTA.
Motion follows the HyperFrames motion guide: titles land and hold still, transitions have a cause
(whip with blur, iris, colour flood, blur swap, zoom-through), punch-ins on the number that matters,
render-time motion blur, characters act (anticipation, squash, offset arms, reactions to the data).
Every look choice comes from a per-video seed, so no two videos look the same.
"""
import re, json, random, hashlib, pathlib, datetime
import cast, scenes, voice, audio
from fx import C, E, T, BASE_CSS, setup, background, BG_KINDS, words, words_in, TEXT_STYLES

FPS = 30
DISCLAIMER = "News only · Not investment advice · MarketSamachar is not SEBI-registered"
GESTURE = dict(ghanti="ring", tohfa="open", katli="split", wapsi="spin", bhonpu="waves", golu="present", teji="cheer",
               mandi="shrug", munshi="point", naya="wave", tareekh="present", desi="point", videshi="wave", arth="point")
TRANS = ["whip", "iris", "flood", "blurswap", "zoom"]
CTA_LINES = ["For the full details, visit marketsamachar.in, and subscribe for every market update.",
             "Follow MarketSamachar for daily market updates. The full story is on marketsamachar.in.",
             "Subscribe to MarketSamachar so you never miss a market move. More on marketsamachar.in.",
             "That's the update. Subscribe for more, and read the details on marketsamachar.in."]


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def _logo(size, extra=""):
    return f'<img src="assets/logo-icon.png" width="{size}" height="{size}" style="border-radius:{size * .22:.0f}px;display:block;{extra}">'


def _wordmark(fs):
    return f'<span class="slab" style="font-size:{fs}px;letter-spacing:2px"><span style="color:{C["green"]}">MARKET</span> <span style="color:{C["ink"]}">SAMACHAR</span></span>'


# ---------------------------------------------------------------- transitions with a cause (stage wrapper per beat)
def trans_out(js, sel, t, kind, color):
    if kind == "whip": js.append(f'tl.to("{sel}",{{x:-520,filter:"blur(18px)",opacity:0,duration:.26,ease:"power3.in"}},{T(t)})')
    elif kind == "zoom": js.append(f'tl.to("{sel}",{{scale:1.6,filter:"blur(14px)",opacity:0,duration:.3,ease:"power3.in"}},{T(t)})')
    elif kind == "iris": js.append(f'tl.to("{sel}",{{opacity:0,filter:"blur(8px)",duration:.18,ease:"power2.in"}},{T(t + .1)})')
    elif kind == "flood": js.append(f'tl.to("{sel}",{{opacity:0,duration:.2,ease:"power2.in"}},{T(t + .15)})')
    else: js.append(f'tl.to("{sel}",{{opacity:0,filter:"blur(8px)",duration:.18,ease:"power2.in"}},{T(t + .1)})')


def trans_in(js, sel, t, kind):
    if kind == "whip": js.append(f'tl.fromTo("{sel}",{{x:520,filter:"blur(18px)",opacity:0}},{{x:0,filter:"blur(0px)",opacity:1,duration:.42,ease:"expo.out"}},{T(t)})')
    elif kind == "zoom": js.append(f'tl.fromTo("{sel}",{{scale:.55,filter:"blur(14px)",opacity:0}},{{scale:1,filter:"blur(0px)",opacity:1,duration:.5,ease:"expo.out"}},{T(t)})')
    elif kind == "iris": js.append(f'tl.fromTo("{sel}",{{clipPath:"circle(0% at 50% 50%)"}},{{clipPath:"circle(150% at 50% 50%)",duration:.45,ease:"power3.in"}},{T(t)})')
    elif kind == "flood": js.append(f'tl.fromTo("{sel}",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.45,ease:"expo.out"}},{T(t + .1)})')
    else: js.append(f'tl.fromTo("{sel}",{{opacity:0,filter:"blur(8px)"}},{{opacity:1,filter:"blur(0px)",duration:.16,ease:"power2.out"}},{T(t)})')


def flood(js, htm, fid, t, color, W, H):
    """Colour flood: the next host's colour sweeps across the frame between beats."""
    htm.append(f'<div class="ab" id="{fid}" style="left:0;top:0;width:{W}px;height:{H}px;background:{color};opacity:0;z-index:4"></div>')
    js.append(f'tl.fromTo("#{fid}",{{opacity:.0,clipPath:"inset(0 100% 0 0)"}},{{opacity:.92,clipPath:"inset(0 0% 0 0)",duration:.22,ease:"power2.inOut"}},{T(t)})')
    js.append(f'tl.to("#{fid}",{{clipPath:"inset(0 0 0 100%)",duration:.24,ease:"power2.inOut"}},{T(t + .24)})')


# ---------------------------------------------------------------- kinetic captions (one group visible at a time)
def captions(js, htm, words_t, cid, box, fs, align="center", maxw=5):
    groups, g = [], []
    for w in words_t:
        g.append(w)
        if len(g) >= maxw or re.search(r"[,.!?;:]$", w[0]): groups.append(g); g = []
    if g: groups.append(g)
    x, y, w_, h_ = box
    for gi, gr in enumerate(groups):
        s0 = max(0.1, gr[0][1] - .06); s1 = groups[gi + 1][0][1] - .02 if gi + 1 < len(groups) else gr[-1][2] + .35
        gid = f"{cid}g{gi}"
        spans = " ".join(f'<span id="{gid}-{k}" class="cwd">{E(wd)}</span>' for k, (wd, a, b) in enumerate(gr))
        htm.append(f'<div class="ab capg" id="{gid}" style="left:{x}px;top:{y}px;width:{w_}px;height:{h_}px;display:flex;align-items:center;'
                   f'justify-content:{"center" if align == "center" else "flex-start"};text-align:{align};font-size:{fs}px;opacity:0;visibility:hidden">'
                   f'<div style="width:100%">{spans}</div></div>')
        js.append(f'tl.set("#{gid}",{{visibility:"visible"}},{T(s0)}); tl.fromTo("#{gid}",{{opacity:0,filter:"blur(6px)"}},{{opacity:1,filter:"blur(0px)",duration:.12}},{T(s0)})')
        for k, (wd, a, b) in enumerate(gr):
            js.append(f'tl.fromTo("#{gid}-{k}",{{color:"#8B93A7"}},{{color:"#FFFFFF",duration:.08}},{T(a)})')
            if re.search(r"\d", wd): js.append(f'tl.to("#{gid}-{k}",{{color:"{C["green"]}",duration:.08}},{T(a + .02)})')
        js.append(f'tl.to("#{gid}",{{opacity:0,duration:.1,ease:"power2.in"}},{T(s1 - .1)}); tl.set("#{gid}",{{visibility:"hidden"}},{T(s1)})')


CAP_CSS = """.capg{font-family:Sans;font-weight:800;line-height:1.12;letter-spacing:-.5px;text-shadow:0 4px 18px rgba(0,0,0,.65)}
.capg .cwd{display:inline-block;margin:0 .12em}"""


# ---------------------------------------------------------------- end CTA (spoken + subscribe click + bell + URL)
def cta_block(js, htm, sfx, t0, d, W, H, V, host, hpid):
    big = 1.0 if V else .85
    htm.append(f'<div class="ab clip" id="cta" data-start="{T(t0)}" data-duration="{T(d)}" data-track-index="6" style="left:0;top:0;width:{W}px;height:{H}px;z-index:20">'
               f'<div class="ab" style="inset:0;background:radial-gradient(circle at 50% 38%,#12203f,{C["bg"]} 68%)"></div>'
               f'<div class="ab" style="left:0;top:{(250 if V else 80)}px;width:{W}px;display:flex;flex-direction:column;align-items:center;gap:{int(26 * big)}px">'
               f'<div id="cta-l">{_logo(int(190 * big))}</div>{_wordmark(int(66 * big))}'
               f'<div style="position:relative;display:flex;align-items:center;gap:22px;margin-top:10px">'
               f'<div id="cta-btn" style="position:relative;font-family:Sans;font-weight:800;font-size:{int(46 * big)}px;letter-spacing:1px;background:#FF0033;color:#fff;border-radius:999px;padding:{int(20 * big)}px {int(46 * big)}px">'
               f'<span id="cta-sub">SUBSCRIBE</span><span id="cta-done" style="position:absolute;left:0;right:0;top:0;bottom:0;display:flex;align-items:center;justify-content:center;opacity:0">SUBSCRIBED ✓</span></div>'
               f'<div id="cta-bell" style="width:{int(92 * big)}px;height:{int(92 * big)}px;border-radius:50%;background:rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center">'
               f'<svg width="{int(52 * big)}" height="{int(52 * big)}" viewBox="0 0 24 24" fill="none" stroke="{C["ink"]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
               f'<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg></div>'
               f'<svg id="cta-cur" class="ab" style="left:{int(160 * big)}px;top:{int(60 * big)}px" width="{int(70 * big)}" height="{int(70 * big)}" viewBox="0 0 24 24">'
               f'<path d="M4 2 L4 20 L9 15 L12.5 22 L15.5 20.5 L12 13.5 L19 13.5 Z" fill="#fff" stroke="#07070e" stroke-width="1.4" stroke-linejoin="round"/></svg></div>'
               f'<div id="cta-url" style="font-family:Mono;font-size:{int(44 * big)}px;color:{C["green"]};background:rgba(0,255,136,.08);border:2px solid rgba(0,255,136,.35);border-radius:16px;padding:12px 26px">'
               + "".join(f'<span id="cu{i}">{E(ch)}</span>' for i, ch in enumerate("marketsamachar.in")) + '</div>'
               f'<div style="font-family:SansM;font-size:{int(22 * big)}px;color:{C["dim"]};margin-top:6px">{E(DISCLAIMER)}</div></div></div>')
    js.append(f'tl.fromTo("#cta-l",{{scale:0,rotation:-25}},{{scale:1,rotation:0,duration:.6,ease:"back.out(1.8)"}},{T(t0 + .05)})')
    js.append(f'tl.fromTo("#cta-btn",{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"back.out(2)"}},{T(t0 + .35)})')
    js.append(f'tl.fromTo("#cta-bell",{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:"back.out(2)"}},{T(t0 + .45)})')
    tc = t0 + 1.25
    js.append(f'tl.fromTo("#cta-cur",{{x:260,y:260,opacity:0}},{{x:0,y:0,opacity:1,duration:.55,ease:"power3.out"}},{T(tc - .55)})')
    js.append(f'tl.to("#cta-cur",{{scale:.82,duration:.07,yoyo:true,repeat:1,transformOrigin:"20% 10%"}},{T(tc)})')
    js.append(f'tl.to("#cta-btn",{{scale:.93,duration:.07,yoyo:true,repeat:1}},{T(tc)})')
    js.append(f'tl.to("#cta-btn",{{backgroundColor:"#3A3F55",duration:.15}},{T(tc + .1)})')
    js.append(f'tl.to("#cta-sub",{{opacity:0,duration:.1}},{T(tc + .1)}); tl.to("#cta-done",{{opacity:1,duration:.12}},{T(tc + .14)})')
    js.append(f'tl.to("#cta-cur",{{x:{int(330 * big)},y:6,duration:.35,ease:"power2.inOut"}},{T(tc + .45)})')
    js.append(f'tl.to("#cta-cur",{{scale:.82,duration:.07,yoyo:true,repeat:1,transformOrigin:"20% 10%"}},{T(tc + .85)})')
    js.append(f'tl.to("#cta-bell svg",{{rotation:18,duration:.08,yoyo:true,repeat:7,transformOrigin:"50% 10%",ease:"sine.inOut"}},{T(tc + .9)})')
    js.append(f'tl.to("#cta-bell",{{backgroundColor:"rgba(0,255,136,.22)",duration:.2}},{T(tc + .9)})')
    js.append(f'tl.to("#cta-cur",{{opacity:0,duration:.25}},{T(tc + 1.6)})')
    for i in range(17): js.append(f'tl.fromTo("#cu{i}",{{opacity:0}},{{opacity:1,duration:.02}},{T(tc + 1.7 + i * .045)})')
    sfx += [(t0, "whoosh", .8), (t0 + .35, "pop", .6), (tc, "click", 1.0), (tc + .85, "click", .8), (tc + .9, "notify", .7), (tc + 1.7, "type", .7)]
    hw = 330 if V else 380
    hx, hy = (W - hw - 40, 1000) if V else (W - hw - 70, H - hw * 1.1 - 30)
    htm.append(f'<div class="ab" id="{hpid}" style="left:{hx:.0f}px;top:{hy:.0f}px;width:{hw}px;z-index:21;visibility:hidden">{cast.svg(host, hpid, hw)}</div>')
    js.append(f'tl.set("#{hpid}",{{visibility:"visible"}},{T(t0 + .1)})')
    js += cast.js_enter(hpid, t0 + .15, "rise") + cast.js_gesture(hpid, t0 + .9, "wave") + cast.js_idle(hpid, t0 + 1.2, t0 + d, 3)


# ======================================================================== SHORT
def build_short(v, proj, date, feed_ts=None):
    rnd = random.Random(seed_of(v["id"], date, v.get("title")))
    W, H = 1080, 1920
    css = setup(proj) + CAP_CSS; js, pre, sfx, vparts, htm = [], [], [], [], []
    side = rnd.choice(["L", "R"]); tstyle = rnd.choice(TEXT_STYLES); trans = rnd.sample(TRANS, 3)
    t = .5; plan = []
    for b in v["beats"]:
        a, ws = voice.say(b["host"], b["say"]); dur = len(a) / voice.SR
        plan.append(dict(b=b, a=a, ws=ws, t0=t, d=max(3.0, dur + .65))); vparts.append((t + .12, a)); t += plan[-1]["d"]
    host0 = v["beats"][0]["host"]
    cta_line = v.get("cta") or CTA_LINES[seed_of(v["id"], "cta") % len(CTA_LINES)]
    ca, cws = voice.say(host0, cta_line); cta_t0 = t + .1; cta_d = max(4.6, len(ca) / voice.SR + 1.6)
    vparts.append((cta_t0 + .35, ca)); total = round((cta_t0 + cta_d) * FPS) / FPS

    bgk = rnd.choice(BG_KINDS); bgh, bgj = background(bgk, W, H, total, rnd, C["green"]); htm.append(bgh); js += bgj
    htm.append(f'<div class="ab" id="hdr" style="left:44px;top:184px;display:flex;align-items:center;gap:14px">{_logo(58)}{_wordmark(30)}</div>'
               f'<div class="ab chip" id="hdt" style="right:44px;top:194px;background:rgba(0,255,136,.12);color:{C["green"]};font-size:20px">'
               f'<span style="width:10px;height:10px;border-radius:50%;background:{C["green"]};box-shadow:0 0 10px {C["green"]}"></span>{E(v.get("stamp", ""))}</div>'
               f'<div class="ab" id="dsc" style="left:44px;right:44px;top:254px;font-family:SansM;font-size:19px;color:{C["dim"]}">{E(DISCLAIMER)}</div>')
    hk, hn = words(v.get("hook", v.get("title", "")), "hk"); n_ch = len(v.get("hook", "").replace("*", ""))
    htm.append(f'<div class="ab slab" id="hook" style="left:44px;right:44px;top:292px;font-size:{86 if n_ch < 24 else 72 if n_ch < 38 else 60}px;line-height:1.02">{hk}</div>')
    js.append('tl.fromTo("#hook",{scale:1.08,transformOrigin:"0% 50%"},{scale:1,duration:.5,ease:"expo.out"},0)')
    sfx.append((0.02, "impact", .6))
    SX, SY, SW, SH = 44, 500, W - 88, 520
    for i, p in enumerate(plan):
        hc = cast.CAST.get(p["b"]["host"], {}).get("color", C["green"])
        ctx = scenes.Ctx(rnd, True); ctx.host_color = hc
        sc = p["b"].get("scene") or {}
        inner = scenes.RENDER[sc.get("kind", "headline")](sc, ctx, f"s{i}", SW, SH, p["t0"] + .2, p["d"] - .45)
        js += ctx.js; pre += ctx.pre; sfx += ctx.sfx; p["ctx"] = ctx
        htm.append(f'<div class="ab clip" id="scw{i}" data-start="{T(max(0, p["t0"] - .02))}" data-duration="{T(p["d"] + .35)}" data-track-index="2" '
                   f'style="left:{SX}px;top:{SY}px;width:{SW}px;height:{SH}px"><div class="ab" id="sc{i}" style="left:0;top:0;width:{SW}px;height:{SH}px">{inner}</div></div>')
        if i > 0: trans_in(js, f"#sc{i}", p["t0"], trans[i % len(trans)])
        nxt = trans[(i + 1) % len(trans)] if i < len(plan) - 1 else "whip"
        trans_out(js, f"#sc{i}", p["t0"] + p["d"] - .3, nxt, hc)
        if i < len(plan) - 1 and nxt == "flood":
            flood(js, htm, f"fl{i}", p["t0"] + p["d"] - .3, cast.CAST.get(plan[i + 1]["b"]["host"], {}).get("color", C["green"]), W, H)
        for pt in ctx.punch:
            js.append(f'tl.fromTo("#sc{i}",{{scale:1}},{{scale:1.045,duration:.14,ease:"power3.out",transformOrigin:"50% 40%"}},{T(pt)})')
        if i < len(plan) - 1: sfx.append((p["t0"] + p["d"] - .3, "whoosh", .8))
    HW = 300; hx = 30 if side == "L" else W - HW - 30; HY = 1020
    capx = HW + 60 if side == "L" else 44; capw = W - HW - 104
    cur = owner = None
    for i, p in enumerate(plan):
        host = p["b"]["host"]
        if host != cur:
            pid = f"h{i}"; kw = dict(day=date[8:10], mon=datetime.date.fromisoformat(date).strftime("%b").upper()) if host == "tareekh" else {}
            htm.append(f'<div class="ab" id="{pid}" style="left:{hx}px;top:{HY}px;width:{HW}px;visibility:hidden">{cast.svg(host, pid, HW, **kw)}</div>')
            js.append(f'tl.set("#{pid}",{{visibility:"visible"}},{T(max(0, p["t0"] - .1))})')
            js += cast.js_enter(pid, max(0, p["t0"] - .05), rnd.choice(["pop", "rise", "left" if side == "L" else "right"]))
            if owner: js += cast.js_exit(owner, p["t0"] - .3, "pop"); js.append(f'tl.set("#{owner}",{{visibility:"hidden"}},{T(p["t0"] + .1)})')
            owner, cur = pid, host
        js += cast.js_idle(owner, p["t0"] + .6, p["t0"] + p["d"], i)
        js += cast.js_talk(owner, voice.amps(p["a"], p["t0"] + .12))
        js += cast.js_look(owner, p["t0"] + .3, 5 if side == "L" else -5)
        js += cast.js_gesture(owner, p["t0"] + .3, GESTURE.get(host, "point"))
        for mt, mood in p["ctx"].mood[:2]: js += cast.js_react(owner, mt, mood)
        wt = [(w, p["t0"] + .12 + s, p["t0"] + .12 + e) for w, s, e in p["ws"]]
        htm.append(f'<div class="ab chip" id="nm{i}" style="left:{capx}px;top:{HY + 6}px;background:{cast.CAST[host]["color"]};color:#0B0B16;font-size:20px;opacity:0">'
                   f'{E(cast.CAST[host]["label"])} · {E(cast.CAST[host]["role"])}</div>')
        js.append(f'tl.fromTo("#nm{i}",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.3}},{T(p["t0"])}); tl.to("#nm{i}",{{opacity:0,duration:.2}},{T(p["t0"] + p["d"] - .25)})')
        captions(js, htm, wt, f"c{i}", (capx, HY + 56, capw, 250), 54, "left", 5)
    if owner: js += cast.js_exit(owner, cta_t0 - .2, "down")
    js.append(f'tl.to("#hook,#hdr,#hdt,#dsc",{{opacity:0,duration:.2}},{T(cta_t0)})')
    cta_block(js, htm, sfx, cta_t0, cta_d, W, H, True, host0, "hc")
    cwt = [(w, cta_t0 + .35 + s, cta_t0 + .35 + e) for w, s, e in cws]
    htm.append('<div class="ab" style="left:0;top:0;width:1px;height:1px;z-index:22">')
    captions(js, htm, cwt, "cc", (44, 1060, W - 88 - 360, 220), 50, "left", 5)
    htm.append('</div>')
    js += cast.js_talk("hc", voice.amps(ca, cta_t0 + .35))
    mix = audio.mix(total, vparts, sfx, seed_of(v["id"], date))
    _write(proj, W, H, total, css, htm, js, pre, mix)
    return dict(total=total, background=bgk, text=tstyle, transitions=trans, side=side)


# ======================================================================== LONG
def build_long(v, proj, date, ticker=None):
    rnd = random.Random(seed_of(v["id"], date, "long"))
    W, H = 1920, 1080
    css = setup(proj) + CAP_CSS; js, pre, sfx, vparts, htm = [], [], [], [], []
    tstyle = rnd.choice(TEXT_STYLES); trans = rnd.sample(TRANS, 4); side = rnd.choice(["L", "R"])
    SX, SY, SW, SH = (70, 150, 1240, 690) if side == "R" else (610, 150, 1240, 690)
    HW = 440; hx = W - HW - 60 if side == "R" else 60; HY = 330
    capbox = (110, 860, W - 220, 120)
    INTRO = 3.6; t = INTRO + .2; plan = []; chapters = []
    for si, seg in enumerate(v["segments"]):
        s0 = t; chapters.append((max(0.0, s0 - .3), seg.get("title", ""))); t += 2.2
        for b in seg["beats"]:
            a, ws = voice.say(b["host"], b["say"]); dur = len(a) / voice.SR
            plan.append(dict(b=b, a=a, ws=ws, t0=t, d=max(3.4, dur + .7), seg=si)); vparts.append((t + .15, a)); t += plan[-1]["d"]
        seg["_t"] = (s0, t)
    host0 = v["segments"][0]["beats"][0]["host"]
    cta_line = v.get("cta") or "That's the market wrap for today. Subscribe to MarketSamachar for the daily wrap, and find every update on marketsamachar.in."
    ca, cws = voice.say(host0, cta_line); cta_t0 = t + .1; cta_d = max(5.0, len(ca) / voice.SR + 1.8)
    vparts.append((cta_t0 + .35, ca)); total = round((cta_t0 + cta_d) * FPS) / FPS
    bgk = rnd.choice(BG_KINDS); bgh, bgj = background(bgk, W, H, total, rnd, C["green"]); htm.append(bgh); js += bgj
    htm.append(f'<div class="ab hud" style="left:48px;top:40px;display:flex;align-items:center;gap:14px">{_logo(56)}{_wordmark(30)}</div>'
               f'<div class="ab hud chip" id="segl" style="right:48px;top:48px;background:rgba(0,255,136,.12);color:{C["green"]};font-size:20px">{E(v.get("stamp", ""))}</div>')
    if ticker:
        tk = "   ·   ".join(f'<b>{E(x["name"])}</b> {E(x["value"])} <span style="color:{C["green"] if x["pct"] > 0 else C["red"]}">{"▲" if x["pct"] > 0 else "▼"} {abs(x["pct"]):.2f}%</span>' for x in ticker)
        tk += f"   ·   <b>{E(DISCLAIMER)}</b>   ·   "
        htm.append(f'<div class="ab hud" style="left:0;right:0;bottom:0;height:52px;background:rgba(5,5,12,.94);border-top:2px solid {C["green"]};overflow:hidden;display:flex;align-items:center;z-index:5">'
                   f'<div style="flex:0 0 auto;height:52px;display:flex;align-items:center;padding:0 22px;background:{C["green"]};color:#07070e;font-family:Sans;font-weight:800;letter-spacing:3px;font-size:19px;z-index:2">MARKET</div>'
                   f'<div id="tkt" style="white-space:nowrap;font-family:Mono;font-size:23px;color:{C["ink"]};padding-left:30px">{tk * 4}</div></div>')
        L = len(re.sub(r"<[^>]+>", "", tk)) * 13.8
        js.append(f'tl.fromTo("#tkt",{{x:0}},{{x:{-L:.0f},duration:{T(L / 70)},ease:"none",repeat:{int(total / (L / 70)) + 1}}},0)')
    hk, hn = words(v.get("hook", v.get("title", "")), "ih")
    htm.append(f'<div class="ab clip" id="intro" data-start="0" data-duration="{T(INTRO + .3)}" data-track-index="4" style="left:0;top:0;width:{W}px;height:{H}px;z-index:30">'
               f'<div class="ab" id="intro-in" style="inset:0;background:radial-gradient(circle at 50% 40%,#12203f,{C["bg"]} 70%);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px">'
               f'<div id="ilg">{_logo(190)}</div>{_wordmark(60)}<div class="slab" style="font-size:72px;max-width:1550px;text-align:center">{hk}</div>'
               f'<div class="chip" style="background:rgba(255,255,255,.07);color:{C["sub"]};font-size:24px">{E(v.get("stamp", ""))} · DAILY MARKET WRAP</div></div></div>')
    js.append('tl.fromTo("#ilg",{scale:0,rotation:-30},{scale:1,rotation:0,duration:.7,ease:"back.out(1.8)"},.05)')
    js += words_in("ih", hn, .55, tstyle)
    js.append(f'tl.to("#intro-in",{{scale:1.4,opacity:0,filter:"blur(14px)",duration:.35,ease:"power3.in"}},{T(INTRO - .1)})')
    js.append(f'tl.fromTo(".hud",{{opacity:0}},{{opacity:1,duration:.4}},{T(INTRO)})')
    sfx += [(.05, "impact", .7), (INTRO - .1, "whoosh", .7)]
    for si, seg in enumerate(v["segments"]):
        s0, _ = seg["_t"]; host = seg["beats"][0]["host"]; hc = cast.CAST.get(host, {}).get("color", C["green"]); sid = f"seg{si}"
        tw, tn = words(seg.get("title", ""), f"{sid}w")
        htm.append(f'<div class="ab clip" id="{sid}" data-start="{T(s0)}" data-duration="2.3" data-track-index="4" style="left:0;top:0;width:{W}px;height:{H}px;z-index:30">'
                   f'<div class="ab" id="{sid}-in" style="inset:0"><div class="ab" id="{sid}-a" style="inset:0;background:{hc}"></div><div class="ab" id="{sid}-b" style="inset:0;background:{C["panel"]}"></div>'
                   f'<div class="ab" style="left:0;right:0;top:400px;text-align:center"><div class="chip" id="{sid}-c" style="background:{hc};color:#0B0B16;font-size:26px">'
                   f'{E(cast.CAST[host]["label"])} · {E(cast.CAST[host]["role"])}</div><div class="slab" style="font-size:118px;margin-top:22px">{tw}</div></div></div></div>')
        js.append(f'tl.fromTo("#{sid}-a",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.3,ease:"power2.inOut"}},{T(s0)})')
        js.append(f'tl.fromTo("#{sid}-b",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.34,ease:"power2.inOut"}},{T(s0 + .1)})')
        js.append(f'tl.fromTo("#{sid}-c",{{opacity:0,filter:"blur(6px)"}},{{opacity:1,filter:"blur(0px)",duration:.2}},{T(s0 + .4)})')
        js += words_in(f"{sid}w", tn, s0 + .5, rnd.choice(["blur", "ink", "line"]))
        js.append(f'tl.to("#{sid}-in",{{scale:1.5,opacity:0,filter:"blur(14px)",duration:.32,ease:"power3.in"}},{T(s0 + 1.95)})')
        js.append(f'tl.set("#segl",{{textContent:{json.dumps(seg.get("title", "").upper())}}},{T(s0 + .4)})')
        sfx += [(s0, "whoosh", .8), (s0 + .45, "pop", .5)]
    cur = owner = None
    for i, p in enumerate(plan):
        host = p["b"]["host"]; hc = cast.CAST.get(host, {}).get("color", C["green"])
        ctx = scenes.Ctx(rnd, False); ctx.host_color = hc; sc = p["b"].get("scene") or {}
        inner = scenes.RENDER[sc.get("kind", "headline")](sc, ctx, f"s{i}", SW, SH, p["t0"] + .25, p["d"] - .55)
        js += ctx.js; pre += ctx.pre; sfx += ctx.sfx
        htm.append(f'<div class="ab clip" id="scw{i}" data-start="{T(p["t0"] - .02)}" data-duration="{T(p["d"] + .35)}" data-track-index="2" '
                   f'style="left:{SX}px;top:{SY}px;width:{SW}px;height:{SH}px"><div class="ab" id="sc{i}" style="left:0;top:0;width:{SW}px;height:{SH}px">{inner}</div></div>')
        trans_in(js, f"#sc{i}", p["t0"], trans[i % len(trans)])
        trans_out(js, f"#sc{i}", p["t0"] + p["d"] - .3, trans[(i + 1) % len(trans)], hc)
        for pt in ctx.punch:
            js.append(f'tl.fromTo("#sc{i}",{{scale:1}},{{scale:1.04,duration:.14,ease:"power3.out",transformOrigin:"50% 45%"}},{T(pt)})')
        new_seg = i == 0 or plan[i - 1]["seg"] != p["seg"]
        if host != cur or new_seg:
            pid = f"h{i}"; kw = dict(day=date[8:10], mon=datetime.date.fromisoformat(date).strftime("%b").upper()) if host == "tareekh" else {}
            htm.append(f'<div class="ab" id="{pid}" style="left:{hx}px;top:{HY}px;width:{HW}px;visibility:hidden">{cast.svg(host, pid, HW, **kw)}</div>')
            js.append(f'tl.set("#{pid}",{{visibility:"visible"}},{T(p["t0"] - .1)})')
            js += cast.js_enter(pid, p["t0"] - .05, rnd.choice(["pop", "drop", "rise", "right" if side == "R" else "left"]))
            if owner: js.append(f'tl.set("#{owner}",{{visibility:"hidden"}},{T(p["t0"] - .1)})')
            owner, cur = pid, host
        js += cast.js_idle(owner, p["t0"] + .6, p["t0"] + p["d"], i)
        js += cast.js_talk(owner, voice.amps(p["a"], p["t0"] + .15))
        js += cast.js_look(owner, p["t0"] + .3, -6 if side == "R" else 6)
        js += cast.js_gesture(owner, p["t0"] + .35, GESTURE.get(host, "point") if new_seg else rnd.choice(["point", "present", GESTURE.get(host, "point")]))
        for mt, mood in ctx.mood[:2]: js += cast.js_react(owner, mt, mood)
        wt = [(w, p["t0"] + .15 + s, p["t0"] + .15 + e) for w, s, e in p["ws"]]
        captions(js, htm, wt, f"c{i}", capbox, 52, "center", 6)
    if owner: js.append(f'tl.set("#{owner}",{{visibility:"hidden"}},{T(cta_t0)})')
    js.append(f'tl.to(".hud",{{opacity:0,duration:.3}},{T(cta_t0)})')
    cta_block(js, htm, sfx, cta_t0, cta_d, W, H, False, host0, "hc")
    cwt = [(w, cta_t0 + .35 + s, cta_t0 + .35 + e) for w, s, e in cws]
    htm.append('<div class="ab" style="left:0;top:0;width:1px;height:1px;z-index:22">')
    captions(js, htm, cwt, "cc", (110, 900, W - 220 - 420, 110), 46, "center", 6)
    htm.append('</div>')
    js += cast.js_talk("hc", voice.amps(ca, cta_t0 + .35))
    mix = audio.mix(total, vparts, sfx, seed_of(v["id"], date), .26)
    _write(proj, W, H, total, css, htm, js, pre, mix)
    return dict(total=total, chapters=chapters, background=bgk, text=tstyle, transitions=trans, side=side)


def _write(proj, W, H, total, css, htm, js, pre, mix):
    import soundfile as sf
    proj = pathlib.Path(proj)
    sf.write(str(proj / "assets/mix.wav"), mix, audio.SR)
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width={W}, height={H}">
<script src="assets/lib/gsap.min.js"></script>
<style>{css}{BASE_CSS}html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#07070e}}#root{{width:{W}px;height:{H}px}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}" data-motion-blur="on">
{''.join(htm)}
<audio id="mix" class="clip" src="assets/mix.wav" data-start="0" data-duration="{total}" data-track-index="10" data-volume="1"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(pre)}
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script></body></html>"""
    (proj / "index.html").write_text(doc)
