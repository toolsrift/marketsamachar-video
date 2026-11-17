"""Daily looks. Every video made on the same day shares one style (fonts, palette, illustration treatment,
captions, background world, camera moves and music); the style changes the next day.

style(date) -> dict(name, fonts, vars, css, family, music, moves, ...)
Illustration classes (used by ill.py inside <svg class="ill">):
  f1..f5 fills · k1..k5 extrusion (km middle copies, kd back copy) · dk dark fill · hi gloss · up/dn fills
  ol outline-only stroke · tx text (on the stage) · txd text on light objects · txa accent text · num big numbers
  bd backdrop disc · rg/rg2 rings · pt particles · gs ground shadow · grid chart grid · lnU/lnD up/down lines
"""
import datetime, pathlib, shutil
from fx import NM, BASE


def _shade(hexc, f):
    h = hexc.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


FONTFILES = {
    "bricolage": ("@fontsource/bricolage-grotesque/files/bricolage-grotesque-latin-800-normal.woff2", 800),
    "inter": ("@fontsource/inter/files/inter-latin-800-normal.woff2", 800),
    "inter6": ("@fontsource/inter/files/inter-latin-600-normal.woff2", 600),
    "grotesk": ("@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2", 700),
    "bangers": ("@fontsource/bangers/files/bangers-latin-400-normal.woff2", 400),
    "spacemono": ("@fontsource/space-mono/files/space-mono-latin-700-normal.woff2", 700),
    "spacemono4": ("@fontsource/space-mono/files/space-mono-latin-400-normal.woff2", 400),
    "slab": ("@fontsource/alfa-slab-one/files/alfa-slab-one-latin-400-normal.woff2", 400),
    "dmsans": ("@fontsource/dm-sans/files/dm-sans-latin-800-normal.woff2", 800),
    "dmsans6": ("@fontsource/dm-sans/files/dm-sans-latin-600-normal.woff2", 600),
    "dmmono": ("@fontsource/dm-mono/files/dm-mono-latin-500-normal.woff2", 500),
    "archivo": ("@fontsource/archivo-black/files/archivo-black-latin-400-normal.woff2", 400),
    "jakarta8": ("@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-800-normal.woff2", 800),
    "jakarta7": ("@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-700-normal.woff2", 700),
}

S = {}

# ------------------------------------------------------------------ 1. STUDIO — glossy 3D stickers on deep indigo
S["studio"] = dict(
    family="flat", music="pulse", moves=["whip", "zoom", "crane", "whip"],
    fonts=dict(Head="bricolage", Body="inter", Num="grotesk", Body6="inter6"),
    fills=["#4FA3FF", "#00E68A", "#F3EBDD", "#FFC24B", "#FF6B6B"],
    v=dict(bg="#151838", bg2="#1E2352", ink="#F3EBDD", sub="#A9AFD6", acc="#00E68A", acc2="#FFC24B", up="#00E68A", dn="#FF5C7A",
           card="#F3EBDD", cardInk="#151838", line="rgba(243,235,221,.14)", dk="#0E1029"),
    world="dots",
)
# ------------------------------------------------------------------ 2. COMIC — halftone yellow, black ink outlines
S["comic"] = dict(
    family="ink", music="funk", moves=["whip", "arc", "zoom", "crane"],
    fonts=dict(Head="bangers", Body="inter", Num="bangers", Body6="inter6"),
    fills=["#29C5F6", "#FF4D6D", "#FFFFFF", "#FFD93D", "#FF8A3D"],
    v=dict(bg="#FFD93D", bg2="#FFE97A", ink="#111111", sub="#3A3A3A", acc="#FF4D6D", acc2="#29C5F6", up="#16A34A", dn="#E11D48",
           card="#FFFFFF", cardInk="#111111", line="rgba(17,17,17,.18)", dk="#111111"),
    world="halftone",
)
# ------------------------------------------------------------------ 3. BLUEPRINT — line drawings on drafting blue
S["blueprint"] = dict(
    family="line", music="cinematic", moves=["crane", "whip", "zoom", "whip"],
    fonts=dict(Head="spacemono", Body="spacemono", Num="spacemono", Body6="spacemono4"),
    fills=None,
    v=dict(bg="#0B3F86", bg2="#1563BE", ink="#EAF4FF", sub="#A8C8F0", acc="#FFD84D", acc2="#7CFFB2", up="#7CFFB2", dn="#FF9AA8",
           card="rgba(11,63,134,.92)", cardInk="#EAF4FF", line="rgba(234,244,255,.18)", dk="#08305F"),
    world="blueprint",
)
# ------------------------------------------------------------------ 4. NEON — brand dark, glowing outlines
S["neon"] = dict(
    family="neon", music="lofi", moves=["zoom", "whip", "arc", "whip"],
    fonts=dict(Head="slab", Body="dmsans", Num="dmmono", Body6="dmsans6"),
    fills=["#38BDF8", "#00FF88", "#E8EAF0", "#F5B83D", "#FF4D6D"],
    v=dict(bg="#07070E", bg2="#11122A", ink="#E8EAF0", sub="#8B93A7", acc="#00FF88", acc2="#38BDF8", up="#00FF88", dn="#FF4D6D",
           card="#0D0D1E", cardInk="#E8EAF0", line="rgba(255,255,255,.08)", dk="#0D0D1E"),
    world="neon",
)
# ------------------------------------------------------------------ 5. PAPER — light cream, pastel cut-paper with thin outlines
S["paper"] = dict(
    family="paper", music="marimba", moves=["whip", "crane", "arc", "zoom"],
    fonts=dict(Head="archivo", Body="inter", Num="archivo", Body6="inter6"),
    fills=["#7FB7FF", "#5FD3A2", "#FFFFFF", "#FFC857", "#FF8B7B"],
    v=dict(bg="#F6F1E7", bg2="#EDE4D3", ink="#1E2452", sub="#5B6190", acc="#6C4CF1", acc2="#FF8B7B", up="#0F9F6E", dn="#E0435C",
           card="#FFFFFF", cardInk="#1E2452", line="rgba(30,36,82,.12)", dk="#1E2452"),
    world="paper",
)
ORDER = ["studio", "comic", "neon", "paper"]   # optional looks; the default is the brand look below

# ------------------------------------------------------------------ BRAND — the default: MarketSamachar dark + brand green + one accent per video
ACCENT = dict(ghanti="#F5B83D", teji="#22D3EE", mandi="#FF6B6B", munshi="#8B5CF6", bhonpu="#FF8A3D", golu="#F472B6",
              katli="#F5B83D", tohfa="#2DD4BF", wapsi="#FACC15", naya="#38BDF8", tareekh="#8B5CF6", desi="#F5B83D",
              videshi="#3B82F6", arth="#2DD4BF")
MUSIC = ["pulse", "lofi", "cinematic", "bright", "marimba", "funk"]


def _mix(a, b, f):
    a, b = a.lstrip("#"), b.lstrip("#")
    return "#%02x%02x%02x" % tuple(int(int(a[i:i + 2], 16) * (1 - f) + int(b[i:i + 2], 16) * f) for i in (0, 2, 4))


def brand(accent, music):
    return dict(name="brand", family="flat", music=music, moves=["whip", "zoom", "crane", "arc"], world="brand",
                fonts=dict(Head="jakarta8", Body="jakarta8", Num="grotesk", Body6="jakarta7"),
                fills=[accent, "#00FF88", "#EEF1F7", _mix(accent, "#ffffff", .35), "#2B3060"],
                v=dict(bg="#07070E", bg2="#11122A", ink="#F2F4F8", sub="#9AA2B8", acc=accent, acc2="#00FF88", up="#00FF88", dn="#FF4D6D",
                       card="#12142B", cardInk="#F2F4F8", line="rgba(255,255,255,.08)", dk="#12142B"))


def pick(date, override=None, host=None, seed=0):
    if override and override in S:
        s = dict(S[override]); s["name"] = override; return s
    return brand(ACCENT.get(host, "#F5B83D"), MUSIC[seed % len(MUSIC)])


def setup(proj, s):
    """Copy gsap, logo and the day's fonts; return the full CSS for the day."""
    proj = pathlib.Path(proj); (proj / "assets/fonts").mkdir(parents=True, exist_ok=True); (proj / "assets/lib").mkdir(parents=True, exist_ok=True)
    shutil.copy(NM / "gsap/dist/gsap.min.js", proj / "assets/lib/gsap.min.js")
    shutil.copy(BASE / "assets/logo-icon.png", proj / "assets/logo-icon.png")
    css = ""
    need = dict(s["fonts"]); need.update(Brand="slab", BrandB="dmsans")
    for fam, key in need.items():
        src, w = FONTFILES[key]; fn = pathlib.Path(src).name
        shutil.copy(NM / src, proj / "assets/fonts" / fn)
        css += f"@font-face{{font-family:{fam};font-weight:{w};src:url('assets/fonts/{fn}')}}\n"
    for alias, key in (("Alfa Slab One", "slab"), ("DM Sans", "dmsans"), ("DM Mono", "dmmono")):
        src, w = FONTFILES[key]; fn = pathlib.Path(src).name; shutil.copy(NM / src, proj / "assets/fonts" / fn)
        css += f"@font-face{{font-family:'{alias}';font-weight:{w};src:url('assets/fonts/{fn}')}}\n"
    return css + page_css(s) + ill_css(s)


def page_css(s):
    v = s["v"]; n = s["name"]
    root = ";".join(f"--{k}:{c}" for k, c in v.items())
    css = f"""
:root{{{root}}}
*{{margin:0;padding:0;box-sizing:border-box}}
#root{{position:relative;overflow:hidden;background:var(--bg);font-family:Body,'DM Sans',sans-serif;color:var(--ink)}}
.ab{{position:absolute}}
.w{{display:inline-block}}
.h{{font-family:Head,'DM Sans',sans-serif;line-height:1.02;color:var(--ink)}} .h .acc{{color:var(--acc)}}
.num{{font-family:Num,'DM Sans',sans-serif;font-variant-numeric:tabular-nums}}
.brand{{font-family:Brand;letter-spacing:2px}}
.chip{{display:inline-flex;align-items:center;gap:10px;font-family:Body;font-weight:800;letter-spacing:2px;text-transform:uppercase;border-radius:999px;padding:8px 18px}}
.hud-ix{{display:flex;gap:14px;white-space:nowrap;font-family:Body6;font-size:22px;color:var(--sub)}} .hud-ix b{{font-family:Num;color:var(--ink);font-weight:700}}
.hud-ix .u{{color:var(--up)}} .hud-ix .d{{color:var(--dn)}}
.cap{{font-family:Body;font-weight:800;line-height:1.13;letter-spacing:-.3px}}
.cap .cwd{{display:inline-block;margin:0 .1em}}
.tick{{font-family:Num,'DM Sans',sans-serif;color:var(--ink)}}
.disc{{font-family:Body6;color:var(--sub)}}
.tcard{{background:var(--card);color:var(--cardInk)}}
.band{{background:var(--bg);box-shadow:0 18px 40px rgba(0,0,0,.25)}}
"""
    if n == "brand":
        css += """.cap{color:#fff;background:rgba(7,7,14,.78);border:1.5px solid rgba(255,255,255,.08);border-radius:16px;padding:8px 18px;display:inline-block} .cap .on{color:var(--up)}
.h{letter-spacing:-1.5px} .h .acc{color:var(--acc)} .chip.k{background:var(--acc);color:#07070E}
.tcard{border:1.5px solid rgba(255,255,255,.10);border-radius:20px;box-shadow:0 20px 50px rgba(0,0,0,.45)}
.band{border-bottom:3px solid var(--acc);box-shadow:0 20px 50px rgba(0,0,0,.6)}"""
    elif n == "studio":
        css += """.cap{color:#fff;text-shadow:0 5px 0 rgba(0,0,0,.35)} .cap .on{color:var(--acc)}
.h{letter-spacing:-1.5px;text-shadow:0 6px 0 rgba(0,0,0,.3)} .chip.k{background:var(--acc);color:#151838;box-shadow:0 6px 0 rgba(0,0,0,.3)}
.tcard{border-radius:18px;box-shadow:0 10px 0 rgba(0,0,0,.35)} .band{border-bottom:4px solid var(--acc)}"""
    elif n == "comic":
        css += """.cap{color:#111;background:#fff;border:6px solid #111;box-shadow:8px 8px 0 #111;padding:10px 20px;display:inline-block;transform:rotate(-1deg)} .cap .on{color:var(--acc)}
.h{letter-spacing:1px;color:#111;-webkit-text-stroke:0} .h .acc{color:var(--acc)} .chip.k{background:var(--acc);color:#fff;border:5px solid #111;box-shadow:6px 6px 0 #111;border-radius:6px}
.tcard{border:6px solid #111;box-shadow:10px 10px 0 #111} .band{border-bottom:7px solid #111;box-shadow:0 10px 0 rgba(17,17,17,.25)}"""
    elif n == "blueprint":
        css += """.cap{color:var(--ink);text-transform:uppercase;letter-spacing:1px} .cap .on{color:var(--acc)}
.h{text-transform:uppercase;letter-spacing:-1px} .chip.k{border:3px solid var(--acc);color:var(--acc);border-radius:0}
.tcard{border:3px solid var(--ink)}"""
    elif n == "neon":
        css += """.cap{color:#fff;text-shadow:0 0 18px rgba(0,255,136,.35),0 4px 16px rgba(0,0,0,.8)} .cap .on{color:var(--acc)}
.h{letter-spacing:1px} .h .acc{text-shadow:0 0 24px rgba(0,255,136,.55)} .chip.k{background:rgba(0,255,136,.12);color:var(--acc);border:1.5px solid rgba(0,255,136,.5)}
.tcard{border:1.5px solid rgba(0,255,136,.35);border-radius:22px;box-shadow:0 0 40px rgba(0,255,136,.15)} .band{border-bottom:2px solid rgba(0,255,136,.45);box-shadow:0 0 50px rgba(0,255,136,.12)}"""
    else:
        css += """.cap{color:var(--ink);background:#fff;border-radius:16px;padding:10px 20px;display:inline-block;box-shadow:0 8px 0 rgba(30,36,82,.12)} .cap .on{color:var(--acc)}
.h{letter-spacing:-1px} .chip.k{background:var(--ink);color:#fff;border-radius:8px}
.tcard{border-radius:16px;border:3px solid var(--ink);box-shadow:8px 8px 0 rgba(30,36,82,.18)} .band{border-bottom:4px solid var(--ink)}"""
    return css


def ill_css(s):
    v = s["v"]; fam = s["family"]; f = s["fills"]
    base = f"""
.ill text{{font-family:Body,'DM Sans',sans-serif}} .ill .tx{{fill:var(--ink)}} .ill .txs{{fill:var(--sub)}} .ill .txa{{fill:var(--acc)}} .ill .txd{{fill:#151838}}
.ill .h{{font-family:Head,'DM Sans',sans-serif}} .ill .num{{font-family:Num,'DM Sans',sans-serif}}
.ill .up{{fill:var(--up)}} .ill .dn{{fill:var(--dn)}} .ill .lnU{{stroke:var(--up);fill:none}} .ill .lnD{{stroke:var(--dn);fill:none}}
.ill .grid{{stroke:var(--line);stroke-width:2;fill:none}} .ill .gridk{{stroke:rgba(255,255,255,.14);stroke-width:2;fill:none}}
.ill .tdk{{fill:#F3F4F8}} .ill .tdks{{fill:#B8BCD0}}
.ill .acc{{fill:var(--acc)}} .ill .acc2{{fill:var(--acc2)}}
.ill .tchip{{fill:{dict(flat="#07070E",ink="#FFFFFF",line="#EAF4FF",neon="#07070E",paper="#FFFFFF")[fam]}}}
"""
    if fam in ("flat", "paper", "neon", "ink"):
        k = [_shade(c, .6) for c in f]
        base += "".join(f".ill .f{i + 1}{{fill:{c}}} .ill .k{i + 1}{{fill:{k[i]}}}" for i, c in enumerate(f))
        base += f""".ill .dk{{fill:{v['dk']}}} .ill .kdk{{fill:{_shade(v['dk'] if v['dk'] != '#111111' else '#333333', .6)}}}
.ill .hi{{fill:#fff;opacity:.35}} .ill .gs{{fill:#000;opacity:{.12 if fam == 'paper' else .28}}}
.ill .bd{{fill:{f[0]};opacity:{.14 if fam != 'paper' else .22}}} .ill .rg{{fill:none;stroke:{f[0]};stroke-width:3;stroke-dasharray:3 16;opacity:.5}}
.ill .rg2{{stroke:{f[3]};stroke-dasharray:24 16;opacity:.4}} .ill .pt{{fill:{f[3]}}} .ill .ptl{{stroke:{f[0]};stroke-width:5;fill:none;stroke-linecap:round}}
.ill .ol{{fill:none;stroke:var(--ink);stroke-width:4}} .ill .coin{{fill:#FFC24B}} .ill .kcoin{{fill:#B9861E}}
"""
    if fam == "ink":
        base += """.ill .s{stroke:#111;stroke-width:6;stroke-linejoin:round;stroke-linecap:round} .ill .km{display:none} .ill .kd{fill:#111}
.ill .hi{opacity:.6} .ill .gs{opacity:.0} .ill .bd{fill:#fff;opacity:.9;stroke:#111;stroke-width:6} .ill .tx{fill:#111}"""
    elif fam == "paper":
        base += """.ill .s{stroke:#1E2452;stroke-width:3.5;stroke-linejoin:round} .ill .km{display:none} .ill .kd{fill:#1E2452;opacity:.16}
.ill .hi{opacity:.5}"""
    elif fam == "neon":
        base += """.ill .s{stroke-width:3} .ill .f1,.ill .f2,.ill .f3,.ill .f4,.ill .f5{fill-opacity:.16}
.ill .f1.s{stroke:#38BDF8} .ill .f2.s{stroke:#00FF88} .ill .f3.s{stroke:#E8EAF0} .ill .f4.s{stroke:#F5B83D} .ill .f5.s{stroke:#FF4D6D}
.ill .km,.ill .kd{display:none} .ill .glw{filter:drop-shadow(0 0 10px rgba(0,255,136,.55))} .ill .hi{opacity:.12}
.ill .dk{fill:#12132a;stroke:rgba(255,255,255,.25);stroke-width:2} .ill .bd{fill:#00FF88;opacity:.06} .ill .coin{fill:#F5B83D;fill-opacity:.85}"""
    elif fam == "line":
        base += f"""
.ill .s,.ill .f1,.ill .f2,.ill .f3,.ill .f4,.ill .f5,.ill .dk{{fill:rgba(234,244,255,.07);stroke:#EAF4FF;stroke-width:4;stroke-linejoin:round}}
.ill .f4,.ill .f2{{stroke:#FFD84D}} .ill .km,.ill .kd,.ill .hi{{display:none}}
.ill .gs{{fill:none;stroke:#EAF4FF;stroke-dasharray:6 10;opacity:.35}} .ill .bd{{fill:none;stroke:#EAF4FF;stroke-opacity:.2;stroke-dasharray:3 12}}
.ill .rg{{fill:none;stroke:#EAF4FF;stroke-opacity:.25;stroke-dasharray:2 16}} .ill .rg2{{stroke-dasharray:22 14}}
.ill .pt{{fill:#FFD84D}} .ill .ptl{{stroke:#FFD84D;stroke-width:4;fill:none}} .ill .ol{{fill:none;stroke:#EAF4FF;stroke-width:3}}
.ill .coin{{fill:rgba(255,216,77,.15);stroke:#FFD84D;stroke-width:4}} .ill .kcoin{{display:none}} .ill .txd{{fill:#EAF4FF}}
.ill .up{{fill:rgba(124,255,178,.18);stroke:#7CFFB2;stroke-width:4}} .ill .dn{{fill:rgba(255,154,168,.18);stroke:#FF9AA8;stroke-width:4}}"""
    else:
        base += ".ill .s{}"
    return base


def world_bg(s, W, H):
    """Background for the whole camera world (moves with the camera) and a far parallax layer."""
    n = s["world"]; v = s["v"]
    if n == "dots":
        near = f"background:radial-gradient(circle,rgba(243,235,221,.10) 2px,transparent 3px) 0 0/44px 44px,var(--bg)"
        far = f"background:radial-gradient(circle at 30% 30%,{v['bg2']} 0,transparent 35%),radial-gradient(circle at 75% 70%,#2a2f6e 0,transparent 30%)"
    elif n == "halftone":
        near = "background:radial-gradient(circle,rgba(255,77,109,.30) 27%,transparent 30%) 0 0/30px 30px,var(--bg)"
        far = "background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(255,255,255,.35) 0deg 8deg,transparent 8deg 20deg)"
    elif n == "blueprint":
        near = ("background:linear-gradient(rgba(255,255,255,.07) 2px,transparent 2px) 0 0/30px 30px,linear-gradient(90deg,rgba(255,255,255,.07) 2px,transparent 2px) 0 0/30px 30px,"
                "linear-gradient(rgba(255,255,255,.16) 2px,transparent 2px) 0 0/150px 150px,linear-gradient(90deg,rgba(255,255,255,.16) 2px,transparent 2px) 0 0/150px 150px,var(--bg)")
        far = "background:radial-gradient(circle at 50% 40%,rgba(21,99,190,.9),transparent 60%)"
    elif n == "neon":
        near = "background:linear-gradient(rgba(255,255,255,.035) 2px,transparent 2px) 0 0/90px 90px,linear-gradient(90deg,rgba(255,255,255,.035) 2px,transparent 2px) 0 0/90px 90px,var(--bg)"
        far = "background:radial-gradient(circle at 25% 30%,rgba(0,255,136,.13),transparent 30%),radial-gradient(circle at 75% 65%,rgba(56,189,248,.12),transparent 30%)"
    elif n == "brand":
        near = ("background:radial-gradient(circle,rgba(255,255,255,.07) 1.6px,transparent 2.6px) 0 0/40px 40px,"
                "linear-gradient(rgba(255,255,255,.025) 2px,transparent 2px) 0 0/200px 200px,linear-gradient(90deg,rgba(255,255,255,.025) 2px,transparent 2px) 0 0/200px 200px,var(--bg)")
        far = f"background:radial-gradient(circle at 25% 30%,{v['acc']}24,transparent 32%),radial-gradient(circle at 75% 68%,rgba(0,255,136,.12),transparent 30%)"
    else:
        near = "background:radial-gradient(circle,rgba(30,36,82,.10) 2px,transparent 3px) 0 0/40px 40px,var(--bg)"
        far = "background:radial-gradient(circle at 20% 25%,#fff 0,transparent 30%),radial-gradient(circle at 80% 70%,#FFE6CF 0,transparent 30%)"
    return near, far
