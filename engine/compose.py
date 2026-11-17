"""Builds one HyperFrames project per video from a job file (written each slot by the daily Claude task).

Short (1080x1920): brand header, hook strip, scene box, character host + live speech bubble, compliance footer, end card.
Long  (1920x1080): studio — scene stage left, host right with bubble, market ticker, segment title cards between desks.
Every visual choice (background, text motion, transitions, host side, entrances, music) comes from a per-video seed,
so no two videos look the same.
"""
import json, math, random, hashlib, pathlib, datetime
import cast, scenes, voice, audio
from fx import C, E, T, BASE_CSS, setup, background, BG_KINDS, words, words_in, icon, fmt, TEXT_STYLES

FPS = 30
DISCLAIMER = "News only · Not investment advice · MarketSamachar is not SEBI-registered"
GESTURE = dict(ghanti="ring", tohfa="open", katli="split", wapsi="spin", bhonpu="waves", golu="present", teji="cheer",
               mandi="shrug", munshi="point", naya="wave", tareekh="present", desi="point", videshi="wave", arth="point")
TRANS = ["slide", "zoom", "wipe", "flip", "rise"]


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def _logo(size):
    return f'<img src="assets/logo-icon.png" width="{size}" height="{size}" style="border-radius:{size * .22:.0f}px;display:block">'


def _wordmark(fs):
    return (f'<span class="slab" style="font-size:{fs}px;letter-spacing:2px"><span style="color:{C["green"]}">MARKET</span> '
            f'<span style="color:{C["ink"]}">SAMACHAR</span></span>')


def _scene_in(js, sel, t, kind):
    if kind == "slide": js.append(f'tl.fromTo("{sel}",{{x:420,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"power3.out"}},{T(t)})')
    elif kind == "zoom": js.append(f'tl.fromTo("{sel}",{{scale:.82,opacity:0,filter:"blur(10px)"}},{{scale:1,opacity:1,filter:"blur(0px)",duration:.5,ease:"expo.out"}},{T(t)})')
    elif kind == "wipe": js.append(f'tl.fromTo("{sel}",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.55,ease:"power3.inOut"}},{T(t)})')
    elif kind == "flip": js.append(f'tl.fromTo("{sel}",{{rotationY:-70,opacity:0,transformPerspective:1600}},{{rotationY:0,opacity:1,duration:.6,ease:"back.out(1.4)"}},{T(t)})')
    else: js.append(f'tl.fromTo("{sel}",{{y:260,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.5)"}},{T(t)})')


def _scene_out(js, sel, t, kind):
    if kind == "slide": js.append(f'tl.to("{sel}",{{x:-420,opacity:0,duration:.35,ease:"power2.in"}},{T(t)})')
    elif kind == "zoom": js.append(f'tl.to("{sel}",{{scale:1.15,opacity:0,duration:.35,ease:"power2.in"}},{T(t)})')
    elif kind == "wipe": js.append(f'tl.to("{sel}",{{clipPath:"inset(0 0 0 100%)",duration:.4,ease:"power3.in"}},{T(t)})')
    elif kind == "flip": js.append(f'tl.to("{sel}",{{rotationY:70,opacity:0,duration:.35,ease:"power2.in"}},{T(t)})')
    else: js.append(f'tl.to("{sel}",{{y:-200,opacity:0,duration:.35,ease:"power2.in"}},{T(t)})')


def _bubble(bid, words_, cls, style, js, who, col):
    spans = " ".join(f'<span id="{bid}-{i}" class="cw">{E(w)}</span>' for i, (w, s, e) in enumerate(words_))
    for i, (w, s, e) in enumerate(words_):
        js.append(f'tl.to("#{bid}-{i}",{{opacity:1,duration:.06}},{T(s)})')
    return f'<div class="bub {cls}" id="{bid}" style="{style}"><span class="who" style="color:{col}">{E(who)}</span>{spans}</div>'


# ======================================================================== SHORT
def build_short(v, proj, date, feed_ts=None):
    rnd = random.Random(seed_of(v["id"], date, v.get("title")))
    W, H = 1080, 1920
    css = setup(proj); js, pre, sfx, vparts, htm = [], [], [], [], []
    host_side = rnd.choice(["L", "R"]); tstyle = rnd.choice(TEXT_STYLES); trans = rnd.sample(TRANS, 3)
    t = .35; plan = []
    for i, b in enumerate(v["beats"]):
        a, ws = voice.say(b["host"], b["say"]); dur = len(a) / voice.SR
        plan.append(dict(b=b, a=a, ws=ws, t0=t, d=max(3.2, dur + .75), speech=dur)); vparts.append((t + .15, a))
        t += plan[-1]["d"]
    end_at = t + .2; total = round((end_at + 2.8) * FPS) / FPS

    bgk = rnd.choice(BG_KINDS); bgc = cast.CAST.get(v["beats"][0]["host"], {}).get("color", C["green"])
    bgh, bgj = background(bgk, W, H, total, rnd, C["green"]); htm.append(bgh); js += bgj
    # header
    htm.append(f'<div class="ab" id="hdr" style="left:48px;top:64px;display:flex;align-items:center;gap:16px">{_logo(76)}{_wordmark(40)}</div>'
               f'<div class="ab chip" id="hdt" style="right:48px;top:80px;background:rgba(0,255,136,.12);color:{C["green"]};font-size:22px">'
               f'<span style="width:12px;height:12px;border-radius:50%;background:{C["green"]};box-shadow:0 0 12px {C["green"]}"></span>{E(v.get("stamp", ""))}</div>')
    js.append('tl.fromTo("#hdr,#hdt",{opacity:0,y:-30},{opacity:1,y:0,duration:.4,ease:"back.out(1.7)"},0)')
    # hook strip
    hk, hn = words(v.get("hook", v.get("title", "")), "hk")
    n_ch = len(v.get("hook", "").replace("*", ""))
    htm.append(f'<div class="ab slab" style="left:48px;right:48px;top:190px;font-size:{78 if n_ch < 26 else 64 if n_ch < 40 else 54}px;line-height:1.04">{hk}</div>')
    js += words_in("hk", hn, .1, tstyle, .07); sfx.append((.05, "whoosh", .8))
    # scenes
    box = (48, 400, W - 96, 660)
    for i, p in enumerate(plan):
        ctx = scenes.Ctx(rnd, True); ctx.host_color = cast.CAST.get(p["b"]["host"], {}).get("color", C["green"])
        sc = p["b"].get("scene") or {}
        inner = scenes.RENDER[sc.get("kind", "headline")](sc, ctx, f"s{i}", box[2], box[3], p["t0"] + .25, p["d"] - .5)
        js += ctx.js; pre += ctx.pre; sfx += ctx.sfx
        htm.append(f'<div class="ab" id="sc{i}" style="left:{box[0]}px;top:{box[1]}px;width:{box[2]}px;height:{box[3]}px">{inner}</div>')
        tr = trans[i % len(trans)]
        if i > 0: _scene_in(js, f"#sc{i}", p["t0"], tr)
        if i < len(plan) - 1: _scene_out(js, f"#sc{i}", p["t0"] + p["d"] - .35, tr)
        js.append(f'tl.set("#sc{i}",{{visibility:"hidden"}},0); tl.set("#sc{i}",{{visibility:"visible"}},{T(max(0, p["t0"] - .05))}); tl.set("#sc{i}",{{visibility:"hidden"}},{T(p["t0"] + p["d"] + .05)})' if i < len(plan) - 1 else
                  f'tl.set("#sc{i}",{{visibility:"hidden"}},0); tl.set("#sc{i}",{{visibility:"visible"}},{T(max(0, p["t0"] - .05))})')
    # hosts + bubbles
    hx = 40 if host_side == "L" else W - 40 - 330
    cur = None
    for i, p in enumerate(plan):
        host = p["b"]["host"]; pid = f"h{i}"
        if host != cur:
            kw = {}
            if host == "tareekh":
                kw = dict(day=date[8:10], mon=datetime.date.fromisoformat(date).strftime("%b").upper())
            htm.append(f'<div class="ab" id="{pid}" style="left:{hx}px;top:1100px;width:330px">{cast.svg(host, pid, 330, **kw)}</div>')
            js += cast.js_enter(pid, p["t0"] - .1, rnd.choice(["pop", "drop", "rise", "left" if host_side == "L" else "right"]))
            if cur is not None: js += cast.js_exit(owner, p["t0"] - .3, "pop")
            owner, cur = pid, host
            js.append(f'tl.set("#{pid}",{{visibility:"hidden"}},0); tl.set("#{pid}",{{visibility:"visible"}},{T(max(0, p["t0"] - .12))})')
        last = next((k for k in range(i + 1, len(plan)) if plan[k]["b"]["host"] != host), len(plan)) - 1
        js += cast.js_idle(owner, p["t0"] + .5, p["t0"] + p["d"], i)
        js += cast.js_talk(owner, voice.amps(p["a"], p["t0"] + .15))
        js += cast.js_gesture(owner, p["t0"] + .3, GESTURE.get(host, "point"))
        bx = 400 if host_side == "L" else 48
        words_t = [(w, p["t0"] + .15 + s, p["t0"] + .15 + e) for w, s, e in p["ws"]]
        fs = 38 if len(p["b"]["say"]) < 110 else 33 if len(p["b"]["say"]) < 170 else 29
        htm.append(_bubble(f"bb{i}", words_t, "bl" if host_side == "L" else "br",
                           f"left:{bx}px;width:{W - 400 - 48}px;top:1110px;font-size:{fs}px", js, cast.CAST[host]["label"], cast.CAST[host]["color"]))
        js.append(f'tl.fromTo("#bb{i}",{{scale:.4,opacity:0,transformOrigin:"{"0% 100%" if host_side == "L" else "100% 100%"}"}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{T(p["t0"])})')
        js.append(f'tl.to("#bb{i}",{{opacity:0,scale:.9,duration:.25}},{T(p["t0"] + p["d"] - .3)})')
        js.append(f'tl.set("#bb{i}",{{visibility:"hidden"}},0); tl.set("#bb{i}",{{visibility:"visible"}},{T(p["t0"] - .02)}); tl.set("#bb{i}",{{visibility:"hidden"}},{T(p["t0"] + p["d"])})')
    # footer + end card
    htm.append(f'<div class="ab" id="ftr" style="left:48px;right:48px;top:1500px;text-align:center;font-family:SansM;font-size:22px;color:{C["sub"]}">{E(DISCLAIMER)}</div>')
    htm.append(f'<div class="ab clip" id="endc" data-start="{T(end_at)}" data-duration="{T(total - end_at)}" data-track-index="5" '
               f'style="inset:0;background:radial-gradient(circle at 50% 40%,#10162b,{C["bg"]} 70%);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px">'
               f'<div id="enl">{_logo(260)}</div>{_wordmark(70)}'
               f'<div class="chip" style="background:{C["green"]};color:#07070e;font-size:34px">Subscribe · daily market updates</div>'
               f'<div style="font-family:SansM;font-size:32px;color:{C["sub"]}">Full details on <b style="color:{C["ink"]}">marketsamachar.in</b></div>'
               f'<div style="font-family:SansM;font-size:22px;color:{C["dim"]}">{E(DISCLAIMER)}</div></div>')
    js.append(f'tl.fromTo("#enl",{{scale:0,rotation:-20}},{{scale:1,rotation:0,duration:.6,ease:"back.out(2)"}},{T(end_at + .1)})')
    js.append(f'tl.to("#ftr",{{opacity:0,duration:.2}},{T(end_at)})')
    sfx.append((end_at, "whoosh", .8)); sfx.append((end_at + .3, "ching", .6))
    mix = audio.mix(total, vparts, sfx, seed_of(v["id"], date))
    _write(proj, W, H, total, css, htm, js, pre, mix)
    return dict(total=total, background=bgk, text=tstyle, transitions=trans, side=host_side)


# ======================================================================== LONG
def build_long(v, proj, date, ticker=None):
    rnd = random.Random(seed_of(v["id"], date, "long"))
    W, H = 1920, 1080
    css = setup(proj); js, pre, sfx, vparts, htm = [], [], [], [], []
    tstyle = rnd.choice(TEXT_STYLES); trans = rnd.sample(TRANS, 4)
    host_side = rnd.choice(["L", "R"])
    sbox = (70 if host_side == "R" else 640, 150, 1210, 760)
    hx = 1440 if host_side == "R" else 70
    t = 0.4; plan = []; chapters = []
    # intro card
    INTRO = 3.2
    t += INTRO
    for si, seg in enumerate(v["segments"]):
        seg_start = t; chapters.append((max(0.0, seg_start - .4), seg.get("title", "")))
        t += 2.4                                           # segment title card
        for b in seg["beats"]:
            a, ws = voice.say(b["host"], b["say"]); dur = len(a) / voice.SR
            plan.append(dict(b=b, a=a, ws=ws, t0=t, d=max(3.6, dur + .8), seg=si, speech=dur)); vparts.append((t + .2, a))
            t += plan[-1]["d"]
        seg["_t"] = (seg_start, t)
    end_at = t + .3; total = round((end_at + 4.0) * FPS) / FPS
    bgk = rnd.choice(BG_KINDS); bgh, bgj = background(bgk, W, H, total, rnd, C["green"]); htm.append(bgh); js += bgj
    # persistent brand + clock + ticker
    htm.append(f'<div class="ab hud" style="left:48px;top:36px;display:flex;align-items:center;gap:14px">{_logo(58)}{_wordmark(32)}</div>'
               f'<div class="ab hud chip" id="segl" style="right:48px;top:44px;background:rgba(0,255,136,.12);color:{C["green"]};font-size:20px">{E(v.get("stamp", ""))}</div>')
    if ticker:
        tk = "   ·   ".join(f'<b>{E(x["name"])}</b> {E(x["value"])} <span style="color:{C["green"] if x["pct"] > 0 else C["red"]}">{"▲" if x["pct"] > 0 else "▼"} {abs(x["pct"]):.2f}%</span>' for x in ticker)
        tk += f"   ·   <b>{E(DISCLAIMER)}</b>   ·   "
        htm.append(f'<div class="ab hud" style="left:0;right:0;bottom:0;height:54px;background:rgba(5,5,12,.94);border-top:2px solid {C["green"]};overflow:hidden;display:flex;align-items:center">'
                   f'<div style="flex:0 0 auto;height:54px;display:flex;align-items:center;padding:0 22px;background:{C["green"]};color:#07070e;font-family:Sans;font-weight:800;letter-spacing:3px;font-size:20px;z-index:2">MARKET</div>'
                   f'<div id="tkt" style="white-space:nowrap;font-family:Mono;font-size:24px;color:{C["ink"]};padding-left:30px">{tk * 4}</div></div>')
        L = len(tk) * 7.2
        js.append(f'tl.fromTo("#tkt",{{x:0}},{{x:{-L:.0f},duration:{T(L / 80)},ease:"none",repeat:{int(total / (L / 80)) + 1}}},0)')
    # intro
    hk, hn = words(v.get("hook", v.get("title", "")), "ih")
    htm.append(f'<div class="ab clip" id="intro" data-start="0" data-duration="{T(INTRO + .4)}" data-track-index="4" style="inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;background:radial-gradient(circle at 50% 40%,#10162b,{C["bg"]} 70%)">'
               f'<div id="ilg">{_logo(200)}</div>{_wordmark(64)}<div class="slab" style="font-size:66px;max-width:1500px;text-align:center">{hk}</div>'
               f'<div class="chip" style="background:rgba(255,255,255,.07);color:{C["sub"]};font-size:24px">{E(v.get("stamp", ""))} · DAILY MARKET WRAP</div></div>')
    js.append('tl.fromTo("#ilg",{scale:0,rotation:-30},{scale:1,rotation:0,duration:.7,ease:"back.out(2)"},.1)')
    js += words_in("ih", hn, .7, tstyle, .07)
    js.append(f'tl.to("#intro",{{opacity:0,scale:1.08,duration:.4}},{T(INTRO)})')
    js.append('tl.fromTo(".hud",{opacity:0},{opacity:1,duration:.4},' + T(INTRO) + ')')
    sfx += [(.1, "whoosh", .8), (.7, "bell", .5), (INTRO, "whoosh", .7)]
    # segment title cards
    for si, seg in enumerate(v["segments"]):
        s0, s1 = seg["_t"]; hostc = cast.CAST.get(seg["beats"][0]["host"], {}).get("color", C["green"])
        sid = f"seg{si}"
        htm.append(f'<div class="ab clip" id="{sid}" data-start="{T(s0)}" data-duration="2.5" data-track-index="4" style="inset:0;overflow:hidden;z-index:30">'
                   f'<div class="ab" id="{sid}-bar" style="left:0;top:0;width:100%;height:100%;background:{hostc}"></div>'
                   f'<div class="ab" id="{sid}-bar2" style="left:0;top:0;width:100%;height:100%;background:{C["panel"]}"></div>'
                   f'<div class="ab" id="{sid}-t" style="left:0;right:0;top:420px;text-align:center">'
                   f'<div class="chip" style="background:{hostc};color:#0B0B16;font-size:26px">{E(cast.CAST[seg["beats"][0]["host"]]["label"])} · {E(cast.CAST[seg["beats"][0]["host"]]["role"])}</div>'
                   f'<div class="slab" style="font-size:110px;margin-top:20px">{E(seg.get("title", ""))}</div></div></div>')
        js.append(f'tl.fromTo("#{sid}-bar",{{x:"-100%"}},{{x:"0%",duration:.35,ease:"power3.out"}},{T(s0)})')
        js.append(f'tl.fromTo("#{sid}-bar2",{{x:"-100%"}},{{x:"0%",duration:.4,ease:"power3.out"}},{T(s0 + .12)})')
        js.append(f'tl.fromTo("#{sid}-t",{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.4,ease:"back.out(2)"}},{T(s0 + .35)})')
        js.append(f'tl.to("#{sid}",{{x:"100%",duration:.4,ease:"power3.in"}},{T(s0 + 2.05)})')
        js.append(f'tl.set("#segl",{{textContent:{json.dumps(seg.get("title", "").upper())}}},{T(s0 + .4)})')
        sfx.append((s0, "whoosh", .9)); sfx.append((s0 + .4, "pop", .6))
    # beats: scenes + hosts
    owner = None; cur = None
    for i, p in enumerate(plan):
        ctx = scenes.Ctx(rnd, False); host = p["b"]["host"]; ctx.host_color = cast.CAST.get(host, {}).get("color", C["green"])
        sc = p["b"].get("scene") or {}
        inner = scenes.RENDER[sc.get("kind", "headline")](sc, ctx, f"s{i}", sbox[2], sbox[3], p["t0"] + .3, p["d"] - .6)
        js += ctx.js; pre += ctx.pre; sfx += ctx.sfx
        htm.append(f'<div class="ab" id="sc{i}" style="left:{sbox[0]}px;top:{sbox[1]}px;width:{sbox[2]}px;height:{sbox[3]}px">{inner}</div>')
        tr = trans[i % len(trans)]
        _scene_in(js, f"#sc{i}", p["t0"], tr); _scene_out(js, f"#sc{i}", p["t0"] + p["d"] - .35, tr)
        js.append(f'tl.set("#sc{i}",{{visibility:"hidden"}},0); tl.set("#sc{i}",{{visibility:"visible"}},{T(p["t0"] - .05)}); tl.set("#sc{i}",{{visibility:"hidden"}},{T(p["t0"] + p["d"] + .05)})')
        new_seg = i == 0 or plan[i - 1]["seg"] != p["seg"]
        if host != cur or new_seg:
            pid = f"h{i}"; kw = {}
            if host == "tareekh": kw = dict(day=date[8:10], mon=datetime.date.fromisoformat(date).strftime("%b").upper())
            htm.append(f'<div class="ab" id="{pid}" style="left:{hx}px;top:560px;width:410px">{cast.svg(host, pid, 410, **kw)}</div>')
            js += cast.js_enter(pid, p["t0"] - .05, rnd.choice(["pop", "drop", "rise", "right" if host_side == "R" else "left"]))
            js.append(f'tl.set("#{pid}",{{visibility:"hidden"}},0); tl.set("#{pid}",{{visibility:"visible"}},{T(p["t0"] - .1)})')
            if owner: js += cast.js_exit(owner, p["t0"] - .45, "down"); js.append(f'tl.set("#{owner}",{{visibility:"hidden"}},{T(p["t0"])})')
            owner, cur = pid, host
        js += cast.js_idle(owner, p["t0"] + .5, p["t0"] + p["d"], i)
        js += cast.js_talk(owner, voice.amps(p["a"], p["t0"] + .2))
        js += cast.js_gesture(owner, p["t0"] + .35, GESTURE.get(host, "point") if new_seg else rnd.choice(["point", "present", "jump", GESTURE.get(host, "point")]))
        words_t = [(w, p["t0"] + .2 + s, p["t0"] + .2 + e) for w, s, e in p["ws"]]
        fs = 34 if len(p["b"]["say"]) < 140 else 30 if len(p["b"]["say"]) < 220 else 26
        bxl = 1330 if host_side == "R" else 60
        htm.append(_bubble(f"bb{i}", words_t, "br" if host_side == "R" else "bl", f"left:{bxl}px;width:530px;top:150px;font-size:{fs}px", js,
                           cast.CAST[host]["label"], cast.CAST[host]["color"]))
        js.append(f'tl.fromTo("#bb{i}",{{scale:.4,opacity:0,transformOrigin:"50% 100%"}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{T(p["t0"] + .05)})')
        js.append(f'tl.to("#bb{i}",{{opacity:0,duration:.25}},{T(p["t0"] + p["d"] - .3)})')
        js.append(f'tl.set("#bb{i}",{{visibility:"hidden"}},0); tl.set("#bb{i}",{{visibility:"visible"}},{T(p["t0"])}); tl.set("#bb{i}",{{visibility:"hidden"}},{T(p["t0"] + p["d"])})')
    if owner: js += cast.js_exit(owner, end_at - .3, "down")
    # end card
    htm.append(f'<div class="ab clip" id="endc" data-start="{T(end_at)}" data-duration="{T(total - end_at)}" data-track-index="5" '
               f'style="inset:0;background:radial-gradient(circle at 50% 40%,#10162b,{C["bg"]} 70%);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px">'
               f'<div id="enl">{_logo(220)}</div>{_wordmark(72)}'
               f'<div class="chip" style="background:{C["green"]};color:#07070e;font-size:30px">Subscribe for the daily market wrap</div>'
               f'<div style="font-family:SansM;font-size:30px;color:{C["sub"]}">Live updates on <b style="color:{C["ink"]}">marketsamachar.in</b></div>'
               f'<div style="font-family:SansM;font-size:22px;color:{C["dim"]};max-width:1300px;text-align:center">{E(DISCLAIMER)}. Figures from public sources; may be provisional or delayed.</div></div>')
    js.append(f'tl.fromTo("#enl",{{scale:0,rotation:-20}},{{scale:1,rotation:0,duration:.6,ease:"back.out(2)"}},{T(end_at + .1)})')
    js.append(f'tl.to(".hud",{{opacity:0,duration:.3}},{T(end_at)})')
    sfx += [(end_at, "whoosh", .8), (end_at + .3, "bell", .5)]
    mix = audio.mix(total, vparts, sfx, seed_of(v["id"], date), .36)
    _write(proj, W, H, total, css, htm, js, pre, mix)
    return dict(total=total, chapters=chapters, background=bgk, text=tstyle, transitions=trans, side=host_side)


def _write(proj, W, H, total, css, htm, js, pre, mix):
    import soundfile as sf
    proj = pathlib.Path(proj)
    sf.write(str(proj / "assets/mix.wav"), mix, audio.SR)
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width={W}, height={H}">
<script src="assets/lib/gsap.min.js"></script>
<style>{css}{BASE_CSS}html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#07070e}}#root{{width:{W}px;height:{H}px}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
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
