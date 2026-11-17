"""v3 composer: one camera world per video, one look per day.

Every beat is a "station" in a large world (title + illustrated data scene). A camera travels between stations
(whip pan, crane, zoom-through, arc), drifts while the host talks and punches in on the number that matters.
A far layer moves at 40% for parallax. The host character, captions, index strip and ticker are a fixed HUD.
Short 1080x1920: everything readable sits inside 168-1330 px. Long 1920x1080: intro flies in from a map of the day.
Both end with the spoken CTA (subscribe click, bell, marketsamachar.in) while the camera pulls back over the world.
"""
import re, json, random, hashlib, pathlib, datetime
import cast, voice, audio, ill, styles
from fx import E, T, fmt, words, words_in

FPS = 30
DISCLAIMER = "News only · Not investment advice · MarketSamachar is not SEBI-registered"
GESTURE = dict(ghanti="ring", tohfa="open", katli="split", wapsi="spin", bhonpu="waves", golu="present", teji="cheer",
               mandi="shrug", munshi="point", naya="wave", tareekh="present", desi="point", videshi="wave", arth="point")
CTA_LINES = ["For the full details, visit marketsamachar.in, and subscribe for every market update.",
             "Follow MarketSamachar for daily market updates. The full story is on marketsamachar.in.",
             "Subscribe to MarketSamachar so you never miss a market move. More on marketsamachar.in.",
             "That's the update. Subscribe for more, and read the details on marketsamachar.in."]
TITLE_IN = dict(studio="rise", comic="rise", blueprint="ink", neon="blur", paper="rise")
MOVE_SFX = dict(whip="whoosh", crane="swish", zoom="big", arc="whoosh")


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def _logo(size):
    return f'<img src="assets/logo-icon.png" width="{size}" height="{size}" style="border-radius:{size * .22:.0f}px;display:block">'


def _wordmark(fs):
    return f'<span class="brand" style="font-size:{fs}px"><span style="color:var(--acc)">MARKET</span> <span style="color:var(--ink)">SAMACHAR</span></span>'


def _title_of(b, v, i):
    if b.get("title"): return b["title"]
    if i == 0 and v.get("hook"): return v["hook"]
    sc = b.get("scene") or {}
    return sc.get("label") or sc.get("company") or sc.get("name") or sc.get("kicker") or ""


# ------------------------------------------------------------------ captions (one group at a time)
def captions(js, htm, words_t, cid, box, fs, align="left", maxw=5):
    groups, g = [], []
    for w in words_t:
        g.append(w)
        if len(g) >= maxw or re.search(r"[,.!?;:]$", w[0]): groups.append(g); g = []
    if g: groups.append(g)
    x, y, w_, h_ = box
    for gi, gr in enumerate(groups):
        s0 = max(0.05, gr[0][1] - .06); s1 = groups[gi + 1][0][1] - .02 if gi + 1 < len(groups) else gr[-1][2] + .35
        gid = f"{cid}g{gi}"
        spans = " ".join(f'<span id="{gid}-{k}" class="cwd{" on" if re.search(r"\d", wd) else ""}">{E(wd)}</span>' for k, (wd, a, b) in enumerate(gr))
        htm.append(f'<div class="ab" id="{gid}" style="left:{x}px;top:{y}px;width:{w_}px;height:{h_}px;display:flex;align-items:center;'
                   f'justify-content:{"center" if align == "center" else "flex-start"};text-align:{align};opacity:0;visibility:hidden">'
                   f'<div class="cap" style="font-size:{fs}px;max-width:{w_}px">{spans}</div></div>')
        js.append(f'tl.set("#{gid}",{{visibility:"visible"}},{T(s0)}); tl.fromTo("#{gid}",{{opacity:0,scale:.92,transformOrigin:"0% 50%"}},{{opacity:1,scale:1,duration:.14,ease:"back.out(2)"}},{T(s0)})')
        for k, (wd, a, b) in enumerate(gr):
            js.append(f'tl.fromTo("#{gid}-{k}",{{opacity:.38}},{{opacity:1,duration:.06}},{T(a)})')
        js.append(f'tl.to("#{gid}",{{opacity:0,duration:.08}},{T(s1 - .08)}); tl.set("#{gid}",{{visibility:"hidden"}},{T(s1)})')


# ------------------------------------------------------------------ station layout + camera path
def layout(n, moves, W, H, rnd):
    pos, mv = [(0, 0)], []
    for i in range(1, n):
        m = moves[(i - 1) % len(moves)]; x, y = pos[-1]
        if m == "whip": nx, ny = x + W * 1.3, y + rnd.uniform(-.12, .12) * H
        elif m == "crane": nx, ny = x + rnd.uniform(-.15, .15) * W, y + H * 1.15
        elif m == "zoom": nx, ny = x + W * 1.4, y - H * .35
        else: nx, ny = x + W * 1.2, y + H * .55
        pos.append((nx, ny)); mv.append(m)
    return pos, mv


def move_js(js, sfx, t, m, x, y, W, H, rnd):
    if m == "zoom":
        js.append(f'tl.to("#cam",{{scale:.5,duration:.34,ease:"power2.in"}},{T(t)})')
        js.append(f'tl.to("#pan",{{x:{-x:.0f},y:{-y:.0f},duration:.66,ease:"power2.inOut"}},{T(t)})')
        js.append(f'tl.to("#far",{{x:{-x * .4:.0f},y:{-y * .4:.0f},duration:.66,ease:"power2.inOut"}},{T(t)})')
        js.append(f'tl.to("#cam",{{scale:1,duration:.34,ease:"power2.out"}},{T(t + .34)})'); d = .68
    elif m == "arc":
        r = rnd.choice([-7, 7])
        js.append(f'tl.to("#cam",{{rotation:{r},scale:.82,duration:.3,ease:"power2.in"}},{T(t)})')
        js.append(f'tl.to("#pan",{{x:{-x:.0f},y:{-y:.0f},duration:.62,ease:"power3.inOut"}},{T(t)})')
        js.append(f'tl.to("#far",{{x:{-x * .4:.0f},y:{-y * .4:.0f},duration:.62,ease:"power3.inOut"}},{T(t)})')
        js.append(f'tl.to("#cam",{{rotation:0,scale:1,duration:.34,ease:"back.out(1.6)"}},{T(t + .3)})'); d = .64
    else:
        dur = .5 if m == "whip" else .62
        js.append(f'tl.to("#pan",{{x:{-x:.0f},y:{-y:.0f},duration:{dur},ease:"power3.inOut"}},{T(t)})')
        js.append(f'tl.to("#far",{{x:{-x * .4:.0f},y:{-y * .4:.0f},duration:{dur},ease:"power3.inOut"}},{T(t)})')
        d = dur
    sfx.append((t + .05, MOVE_SFX.get(m, "whoosh"), .7))
    return d


def world_html(S, pos, W, H, stations_html, pad):
    xs = [p[0] for p in pos]; ys = [p[1] for p in pos]
    x0, y0 = min(xs) - pad * W, min(ys) - pad * H; x1, y1 = max(xs) + (1 + pad) * W, max(ys) + (1 + pad) * H
    near, far = styles.world_bg(S, W, H)
    rail = "M" + " L".join(f"{x + W / 2 - x0:.0f},{y + H * .55 - y0:.0f}" for x, y in pos)
    dots = "".join(f'<circle cx="{x + W / 2 - x0:.0f}" cy="{y + H * .55 - y0:.0f}" r="18" style="fill:var(--acc);opacity:.35"/>' for x, y in pos)
    far_html = (f'<div class="ab" id="far" style="left:{x0 * .4 - W:.0f}px;top:{y0 * .4 - H:.0f}px;width:{(x1 - x0) * .4 + 3 * W:.0f}px;height:{(y1 - y0) * .4 + 3 * H:.0f}px;{far}"></div>')
    world = (f'<div class="ab" id="pan" style="left:0;top:0;width:{W}px;height:{H}px">'
             f'<div class="ab" style="left:{x0:.0f}px;top:{y0:.0f}px;width:{x1 - x0:.0f}px;height:{y1 - y0:.0f}px;{near};opacity:.96"></div>'
             f'<svg class="ab" style="left:{x0:.0f}px;top:{y0:.0f}px;overflow:visible" width="{x1 - x0:.0f}" height="{y1 - y0:.0f}">'
             f'<path d="{rail}" style="fill:none;stroke:var(--acc);stroke-width:10;stroke-dasharray:4 26;stroke-linecap:round;opacity:.3"/>{dots}</svg>'
             f'{stations_html}</div>')
    return far_html, world, (x0, y0, x1, y1)


def deco(S, sx, sy, W, H, word, rnd, vertical):
    """Big faint word + floating glyphs around a station, so the world is never empty between stations."""
    out = (f'<div class="ab h" style="left:{sx + (W - 140 if vertical else -60):.0f}px;top:{sy + (H * .2 if vertical else H - 260):.0f}px;'
           f'font-size:{200 if vertical else 240}px;opacity:.07;white-space:nowrap;transform-origin:0 0;{"transform:rotate(90deg)" if vertical else ""}">{E(word.upper())}</div>')
    for k in range(6):
        g = rnd.choice(["₹", "%", "+", "₹", "%"])
        gx = sx + (rnd.uniform(-.45, -.12) if k % 2 else rnd.uniform(1.05, 1.3)) * W
        out += (f'<div class="ab num" style="left:{gx:.0f}px;top:{sy + rnd.uniform(0, 1.0) * H:.0f}px;font-size:{rnd.randint(70, 160)}px;'
                f'color:var(--acc);opacity:{rnd.uniform(.06, .14):.2f};transform:rotate({rnd.randint(-25, 25)}deg)">{g}</div>')
    return out


# ------------------------------------------------------------------ HUD pieces
def index_strip(ticker, size=22):
    if not ticker: return ""
    out = []
    for x in ticker[:3]:
        pc = x.get("pct") or 0
        out.append(f'<span>{E(x["name"])} <b>{E(str(x["value"]))}</b> <span class="{"u" if pc >= 0 else "d"}">{"▲" if pc >= 0 else "▼"}{abs(pc):.2f}%</span></span>')
    return f'<div class="hud-ix" style="font-size:{size}px">{"<span style=\"opacity:.4\">·</span>".join(out)}</div>'


def ticker_tape(ticker, js, total, y, W, h, fs):
    if not ticker: return ""
    tk = "   ·   ".join(f'<b>{E(x["name"])}</b> {E(str(x["value"]))} <span style="color:var(--{"up" if (x.get("pct") or 0) >= 0 else "dn"})">{"▲" if (x.get("pct") or 0) >= 0 else "▼"} {abs(x.get("pct") or 0):.2f}%</span>' for x in ticker)
    tk += f"   ·   {E(DISCLAIMER)}   ·   "
    L = len(re.sub(r"<[^>]+>", "", tk)) * fs * .6
    js.append(f'tl.fromTo("#tkt",{{x:0}},{{x:{-L:.0f},duration:{T(L / 80)},ease:"none",repeat:{int(total / (L / 80)) + 1}}},0)')
    return (f'<div class="ab" style="left:0;top:{y}px;width:{W}px;height:{h}px;overflow:hidden;display:flex;align-items:center;background:var(--dk);border-top:3px solid var(--acc);z-index:8">'
            f'<div style="flex:0 0 auto;height:{h}px;display:flex;align-items:center;padding:0 20px;background:var(--acc);color:var(--bg);font-family:Body;font-weight:800;letter-spacing:3px;font-size:{fs - 3}px;z-index:2">LIVE</div>'
            f'<div id="tkt" class="tick" style="white-space:nowrap;font-size:{fs}px;padding-left:26px;color:#E8EAF0">{tk * 4}</div></div>')


def cta(js, htm, sfx, t0, d, W, H, V, host):
    big = 1.0 if V else .85
    top = 300 if V else 120
    htm.append(f'<div class="ab clip" id="cta" data-start="{T(t0)}" data-duration="{T(d)}" data-track-index="6" style="left:0;top:0;width:{W}px;height:{H}px;z-index:20">'
               f'<div class="ab" id="cta-bg" style="inset:0;background:var(--bg);opacity:.86"></div>'
               f'<div class="ab" style="left:0;top:{top}px;width:{W}px;display:flex;flex-direction:column;align-items:center;gap:{int(26 * big)}px">'
               f'<div id="cta-l">{_logo(int(190 * big))}</div><div id="cta-w">{_wordmark(int(66 * big))}</div>'
               f'<div style="position:relative;display:flex;align-items:center;gap:22px;margin-top:10px">'
               f'<div id="cta-btn" style="position:relative;font-family:Body;font-weight:800;font-size:{int(46 * big)}px;letter-spacing:1px;background:#FF0033;color:#fff;border-radius:999px;padding:{int(20 * big)}px {int(46 * big)}px;box-shadow:0 8px 0 rgba(0,0,0,.25)">'
               f'<span id="cta-sub" style="white-space:nowrap">SUBSCRIBE</span><span id="cta-done" style="white-space:nowrap;position:absolute;left:0;right:0;top:0;bottom:0;display:flex;align-items:center;justify-content:center;opacity:0">SUBSCRIBED ✓</span></div>'
               f'<div id="cta-bell" style="width:{int(92 * big)}px;height:{int(92 * big)}px;border-radius:50%;background:var(--card);display:flex;align-items:center;justify-content:center;box-shadow:0 8px 0 rgba(0,0,0,.2)">'
               f'<svg width="{int(52 * big)}" height="{int(52 * big)}" viewBox="0 0 24 24" fill="none" stroke="var(--cardInk)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
               f'<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg></div>'
               f'<svg id="cta-cur" class="ab" style="left:{int(160 * big)}px;top:{int(60 * big)}px" width="{int(70 * big)}" height="{int(70 * big)}" viewBox="0 0 24 24">'
               f'<path d="M4 2 L4 20 L9 15 L12.5 22 L15.5 20.5 L12 13.5 L19 13.5 Z" fill="#fff" stroke="#07070e" stroke-width="1.4" stroke-linejoin="round"/></svg></div>'
               f'<div id="cta-url" class="tcard num" style="font-size:{int(46 * big)}px;padding:12px 28px">'
               + "".join(f'<span id="cu{i}">{E(ch)}</span>' for i, ch in enumerate("marketsamachar.in")) + '</div>'
               f'<div class="disc" style="font-size:{int(23 * big)}px;margin-top:6px">{E(DISCLAIMER)}</div></div></div>')
    js.append(f'tl.fromTo("#cta-bg",{{opacity:0}},{{opacity:.86,duration:.4}},{T(t0)})')
    js.append(f'tl.fromTo("#cta-l",{{scale:0,rotation:-25}},{{scale:1,rotation:0,duration:.6,ease:"back.out(1.8)"}},{T(t0 + .1)})')
    js.append(f'tl.fromTo("#cta-w",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4}},{T(t0 + .25)})')
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
    js.append(f'tl.to("#cta-cur",{{opacity:0,duration:.25}},{T(tc + 1.6)})')
    for i in range(17): js.append(f'tl.fromTo("#cu{i}",{{opacity:0}},{{opacity:1,duration:.02}},{T(tc + 1.7 + i * .045)})')
    sfx += [(t0, "big", .7), (t0 + .35, "pop", .6), (tc, "click", 1.0), (tc + .85, "click", .8), (tc + .9, "notify", .7), (tc + 1.7, "type", .7)]


# ------------------------------------------------------------------ build
def build(v, proj, date, ticker=None, style=None):
    long_ = v["kind"] == "long"
    W, H = (1920, 1080) if long_ else (1080, 1920)
    S = styles.pick(date, style or v.get("style"))
    rnd = random.Random(seed_of(v["id"], date))
    css = styles.setup(proj, S)
    js, pre, sfx, vparts, htm = [], [], [], [], []
    # ---- beats + timing
    beats = []
    if long_:
        for si, seg in enumerate(v["segments"]):
            for bi, b in enumerate(seg["beats"]): beats.append(dict(b=b, seg=si, segtitle=seg.get("title", ""), first=bi == 0))
    else:
        beats = [dict(b=b, seg=0, first=False) for b in v["beats"]]
    INTRO = 3.0 if long_ else 0.0
    t = INTRO + (.3 if long_ else .35); chapters = []
    for i, x in enumerate(beats):
        if long_ and x["first"]:
            if i > 0: t += .7
            chapters.append((max(0.0, t - .6), x["segtitle"]))
        a, ws = voice.say(x["b"]["host"], x["b"]["say"]); dur = len(a) / voice.SR
        x.update(a=a, ws=ws, t0=t, d=max(3.4 if long_ else 3.2, dur + .62)); vparts.append((t + .15, a)); t += x["d"]
    host0 = beats[0]["b"]["host"]
    cta_line = v.get("cta") or (("That's the update. Subscribe to MarketSamachar, and find every story on marketsamachar.in.")
                                if long_ else CTA_LINES[seed_of(v["id"], "cta") % len(CTA_LINES)])
    ca, cws = voice.say(host0, cta_line); cta_t0 = t + .1; cta_d = max(4.8, len(ca) / voice.SR + 1.7)
    vparts.append((cta_t0 + .4, ca)); total = round((cta_t0 + cta_d) * FPS) / FPS
    # ---- stations
    pos, mvs = layout(len(beats), S["moves"], W, H, rnd)
    if long_:
        TX, TY, TW, TF = 90, 104, 1250, 60
        IX, IY, IW = 60, 196, 1110
    else:
        TX, TY, TW, TF = 56, 304, 968, 74
        IX, IY, IW = 48, 470, 984
    IH = IW * 800 / 1200
    st_html = ""
    for i, x in enumerate(beats):
        sx, sy = pos[i]; b = x["b"]; sc = b.get("scene") or {}
        a0 = x["t0"] + (.15 if i else .1)
        svg, sj, sp, ev = ill.scene(sc.get("kind", "headline"), f"s{i}", a0, x["d"] - .3, sc)
        js += sj; pre += sp; sfx += ev["sfx"]; x["ev"] = ev
        title = _title_of(b, v, i)
        tw, tn = words(title, f"t{i}")
        n_ch = len(title.replace("*", ""))
        tf = TF if n_ch < (26 if not long_ else 40) else int(TF * .82)
        hc = cast.CAST.get(b["host"], {}).get("color", "#00E68A")
        st_html += deco(S, sx, sy, W, H, sc.get("kind", "news"), rnd, not long_)
        st_html += (f'<div class="ab" style="left:{sx + IX + IW * .1:.0f}px;top:{sy + IY + IH * .05:.0f}px;width:{IW * .8:.0f}px;height:{IH * .9:.0f}px;border-radius:50%;'
                    f'background:radial-gradient(circle,{hc}30,transparent 65%)"></div>')
        st_html += (f'<div class="ab" style="left:{sx + TX}px;top:{sy + TY}px;width:{TW}px">'
                    f'<div class="chip k" id="k{i}" style="font-size:{20 if not long_ else 18}px;margin-bottom:12px">{E(cast.CAST[b["host"]]["role"])}</div>'
                    f'<div class="h" style="font-size:{tf}px">{tw}</div></div>')
        st_html += f'<svg class="ab ill" style="left:{sx + IX}px;top:{sy + IY}px;overflow:visible" width="{IW}" height="{IH:.0f}" viewBox="0 0 1200 800">{svg}</svg>'
        if i == 0 and not long_:
            js.append(f'tl.fromTo("#k{i}",{{opacity:0,y:-10}},{{opacity:1,y:0,duration:.3}},0.05)')   # hook title visible at frame 0
        else:
            js.append(f'tl.fromTo("#k{i}",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:.35,ease:"power3.out"}},{T(x["t0"] - .05)})')
            js += words_in(f"t{i}", tn, x["t0"] + .05, TITLE_IN[S["name"]])
    far_html, world, box = world_html(S, pos, W, H, st_html, .9 if not long_ else .7)
    htm.append(f'<div class="ab" id="cam" style="left:0;top:0;width:{W}px;height:{H}px;transform-origin:50% 50%">'
               f'<div class="ab" id="drift" style="left:0;top:0;width:{W}px;height:{H}px;transform-origin:50% 50%">'
               f'<div class="ab" id="punch" style="left:0;top:0;width:{W}px;height:{H}px;transform-origin:50% {45 if long_ else 42}%">'
               f'{far_html}{world}</div></div></div>')
    # ---- camera
    cx_all = (box[0] + box[2]) / 2 - W / 2; cy_all = (box[1] + box[3]) / 2 - H / 2
    ov = min(W / (box[2] - box[0]), H / (box[3] - box[1])) * 1.1
    if long_:
        js.append(f'tl.set("#pan",{{x:{-cx_all:.0f},y:{-cy_all:.0f}}},0); tl.set("#far",{{x:{-cx_all * .4:.0f},y:{-cy_all * .4:.0f}}},0)')
        js.append(f'tl.fromTo("#cam",{{scale:{ov:.3f}}},{{scale:{ov * 1.12:.3f},duration:{INTRO - 1:.2f},ease:"none"}},0)')
        js.append(f'tl.to("#cam",{{scale:1,duration:1.0,ease:"power3.inOut"}},{T(INTRO - 1)})')
        js.append(f'tl.to("#pan",{{x:{-pos[0][0]:.0f},y:{-pos[0][1]:.0f},duration:1.0,ease:"power3.inOut"}},{T(INTRO - 1)})')
        js.append(f'tl.to("#far",{{x:{-pos[0][0] * .4:.0f},y:{-pos[0][1] * .4:.0f},duration:1.0,ease:"power3.inOut"}},{T(INTRO - 1)})')
        sfx.append((INTRO - 1, "big", .7))
    else:
        js.append(f'tl.set("#pan",{{x:{-pos[0][0]:.0f},y:{-pos[0][1]:.0f}}},0)')
        js.append('tl.fromTo("#cam",{scale:1.14},{scale:1,duration:.9,ease:"expo.out"},0)')
    for i, x in enumerate(beats):
        if i > 0:
            tb = x["t0"] - .55
            move_js(js, sfx, tb, mvs[i - 1], pos[i][0], pos[i][1], W, H, rnd)
        js.append(f'tl.fromTo("#drift",{{scale:1,x:0}},{{scale:1.04,x:{rnd.choice([-18, 18])},duration:{T(max(.5, x["d"] - .5))},ease:"sine.inOut"}},{T(x["t0"])})')
        for pt in x["ev"]["punch"][:1]:
            js.append(f'tl.fromTo("#punch",{{scale:1}},{{scale:1.07,duration:.12,ease:"power3.out"}},{T(pt)})')
            js.append(f'tl.to("#punch",{{scale:1,duration:.9,ease:"power2.inOut"}},{T(pt + .35)})')
    # CTA: pull back over the world
    js.append(f'tl.to("#drift",{{scale:1,x:0,duration:.6}},{T(cta_t0)})')
    js.append(f'tl.to("#cam",{{scale:{ov * 1.05:.3f},duration:1.4,ease:"power3.inOut"}},{T(cta_t0)})')
    js.append(f'tl.to("#pan",{{x:{-cx_all:.0f},y:{-cy_all:.0f},duration:1.4,ease:"power3.inOut"}},{T(cta_t0)})')
    js.append(f'tl.to("#far",{{x:{-cx_all * .4:.0f},y:{-cy_all * .4:.0f},duration:1.4,ease:"power3.inOut"}},{T(cta_t0)})')
    # ---- HUD
    if long_:
        htm.append(f'<div class="ab hud" style="left:44px;top:30px;display:flex;align-items:center;gap:14px;z-index:9">{_logo(54)}{_wordmark(30)}</div>'
                   f'<div class="ab hud chip k" id="segl" style="right:44px;top:38px;font-size:19px;z-index:9">{E(v.get("stamp", ""))}</div>'
                   f'<div class="ab hud" style="left:560px;top:44px;z-index:9">{index_strip(ticker, 21)}</div>')
        htm.append(ticker_tape(ticker, js, total, 1028, W, 52, 23))
        hw, hx, hy = 420, 1400, 450; capbox, capfs, capal, capn = (110, 944, 1240, 76), 46, "center", 7
    else:
        htm.append(f'<div class="ab hud" style="left:44px;top:178px;display:flex;align-items:center;gap:14px;z-index:9">{_logo(56)}{_wordmark(30)}</div>'
                   f'<div class="ab hud chip k" style="right:44px;top:186px;font-size:19px;z-index:9">{E(v.get("stamp", ""))}</div>'
                   f'<div class="ab hud" style="left:46px;top:252px;z-index:9">{index_strip(ticker, 19)}</div>')
        htm.append(ticker_tape(ticker, js, total, 1352, W, 50, 22))
        htm.append(f'<div class="ab disc" style="left:44px;right:44px;top:1414px;font-size:19px;z-index:9">{E(DISCLAIMER)}</div>')
        hw, hx, hy = 270, 26, 1080; capbox, capfs, capal, capn = (316, 1124, 730, 190), 52, "left", 5
    # host (fixed) + captions
    cur = owner = None
    for i, x in enumerate(beats):
        host = x["b"]["host"]
        if host != cur:
            pid = f"h{i}"; kw = dict(day=date[8:10], mon=datetime.date.fromisoformat(date).strftime("%b").upper()) if host == "tareekh" else {}
            htm.append(f'<div class="ab" id="{pid}" style="left:{hx}px;top:{hy}px;width:{hw}px;visibility:hidden;z-index:10">{cast.svg(host, pid, hw, **kw)}</div>')
            js.append(f'tl.set("#{pid}",{{visibility:"visible"}},{T(max(0, x["t0"] - .15))})')
            js += cast.js_enter(pid, max(0, x["t0"] - .1), rnd.choice(["pop", "rise", "right" if long_ else "left"]))
            if owner: js += cast.js_exit(owner, x["t0"] - .35, "pop"); js.append(f'tl.set("#{owner}",{{visibility:"hidden"}},{T(x["t0"])})')
            owner, cur = pid, host
            sfx.append((max(0, x["t0"] - .1), "pop", .35))
        js += cast.js_idle(owner, x["t0"] + .6, x["t0"] + x["d"], i)
        js += cast.js_talk(owner, voice.amps(x["a"], x["t0"] + .15))
        js += cast.js_look(owner, x["t0"] + .3, -6 if long_ else 6)
        js += cast.js_gesture(owner, x["t0"] + .35, GESTURE.get(host, "point") if i == 0 or beats[i - 1]["b"]["host"] != host else rnd.choice(["point", "present"]))
        for mt, mood in x["ev"]["mood"][:1]: js += cast.js_react(owner, mt, mood)
        wt = [(w, x["t0"] + .15 + s, x["t0"] + .15 + e) for w, s, e in x["ws"]]
        captions(js, htm, wt, f"c{i}", capbox, capfs, capal, capn)
        if long_ and x["first"]:
            js.append(f'tl.set("#segl",{{textContent:{json.dumps(x["segtitle"].upper())}}},{T(x["t0"] - .3)})')
            if i > 0:   # desk banner in the host's colour while the camera travels
                bid = f"bn{i}"; hc = cast.CAST.get(host, {}).get("color", "#00E68A")
                bw_, bn = words(x["segtitle"], f"{bid}w")
                htm.append(f'<div class="ab" id="{bid}" style="left:0;top:400px;width:{W}px;height:240px;background:{hc};z-index:12;display:flex;align-items:center;justify-content:center;opacity:0">'
                           f'<div class="h" style="font-size:110px;color:#0B0B16;text-shadow:none">{bw_}</div></div>')
                tb = x["t0"] - 1.35
                js.append(f'tl.fromTo("#{bid}",{{opacity:1,clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.28,ease:"power3.out"}},{T(tb)})')
                js.append(f'tl.to("#{bid}",{{clipPath:"inset(0 0% 0 100%)",duration:.28,ease:"power3.in"}},{T(tb + 1.0)})')
                js.append(f'tl.set("#{bid}",{{opacity:0}},{T(tb + 1.3)})')
                sfx.append((tb, "whoosh", .7))
    if owner: js.append(f'tl.set("#{owner}",{{visibility:"hidden"}},{T(cta_t0 + .05)})'); js += cast.js_exit(owner, cta_t0 - .3, "pop")
    js.append(f'tl.to(".hud",{{opacity:0,duration:.3}},{T(cta_t0)})')
    # intro (long): title card over the map of the day
    if long_:
        hk, hn = words(v.get("hook", v.get("title", "")), "ih")
        htm.append(f'<div class="ab clip" id="intro" data-start="0" data-duration="{T(INTRO)}" data-track-index="4" style="left:0;top:0;width:{W}px;height:{H}px;z-index:15">'
                   f'<div class="ab" id="intro-in" style="left:260px;top:250px;width:1400px;padding:46px 60px;display:flex;flex-direction:column;align-items:center;gap:20px" class="">'
                   f'<div class="ab tcard" style="inset:0;opacity:.94"></div>'
                   f'<div style="position:relative;display:flex;align-items:center;gap:18px">{_logo(110)}{_wordmark(56)}</div>'
                   f'<div class="h" style="position:relative;font-size:82px;text-align:center;color:var(--cardInk)">{hk}</div>'
                   f'<div class="chip k" style="position:relative;font-size:22px">{E(v.get("stamp", ""))} · DAILY MARKET WRAP</div></div></div>')
        js += words_in("ih", hn, .35, TITLE_IN[S["name"]])
        js.append('tl.fromTo("#intro-in",{scale:.7,opacity:0},{scale:1,opacity:1,duration:.55,ease:"back.out(1.6)"},0.02)')
        js.append(f'tl.to("#intro-in",{{scale:1.3,opacity:0,filter:"blur(12px)",duration:.4,ease:"power3.in"}},{T(INTRO - 1.05)})')
        js.append(f'tl.fromTo(".hud",{{opacity:0}},{{opacity:1,duration:.4}},{T(INTRO - .3)})')
        sfx.append((.02, "impact", .6))
    # ---- CTA
    cta(js, htm, sfx, cta_t0, cta_d, W, H, not long_, host0)
    chw = 330 if not long_ else 380
    chx, chy = (W - chw - 40, 1010) if not long_ else (W - chw - 80, H - chw * 1.1 - 30)
    htm.append(f'<div class="ab" id="hc" style="left:{chx:.0f}px;top:{chy:.0f}px;width:{chw}px;z-index:21;visibility:hidden">{cast.svg(host0, "hc", chw)}</div>')
    js.append(f'tl.set("#hc",{{visibility:"visible"}},{T(cta_t0 + .1)})')
    js += cast.js_enter("hc", cta_t0 + .15, "rise") + cast.js_gesture("hc", cta_t0 + .9, "wave") + cast.js_idle("hc", cta_t0 + 1.3, cta_t0 + cta_d, 3)
    js += cast.js_talk("hc", voice.amps(ca, cta_t0 + .4))
    cwt = [(w, cta_t0 + .4 + s, cta_t0 + .4 + e) for w, s, e in cws]
    htm.append('<div class="ab" style="left:0;top:0;width:1px;height:1px;z-index:22">')
    captions(js, htm, cwt, "cc", (44, 1080, W - 88 - 360, 220) if not long_ else (110, 880, W - 220 - 440, 110), 50 if not long_ else 44, "left" if not long_ else "center", 5 if not long_ else 7)
    htm.append('</div>')
    mix = audio.mix(total, vparts, sfx, seed_of(v["id"], date), .30 if not long_ else .26, track=S["music"])
    _write(proj, W, H, total, css, htm, js, pre, mix)
    info = dict(total=total, background=S["name"], text=S["music"], transitions=mvs)
    if long_: info["chapters"] = chapters
    return info


def _write(proj, W, H, total, css, htm, js, pre, mix):
    import soundfile as sf
    proj = pathlib.Path(proj)
    sf.write(str(proj / "assets/mix.wav"), mix, audio.SR)
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width={W}, height={H}">
<script src="assets/lib/gsap.min.js"></script>
<style>{css}html,body{{width:{W}px;height:{H}px;overflow:hidden;background:var(--bg)}}#root{{width:{W}px;height:{H}px}}</style></head><body>
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
