#!/usr/bin/env python3
"""Thumbnails: 1280x720 for the long video, 1080x1920 cover for each Short — brand look + the video's host character.

  python3 engine/thumb.py jobs/<job>.json work      -> work/<id>/thumb.png
"""
import sys, json, re, html, pathlib, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cast
from fx import C

E = html.escape
BASE = pathlib.Path(__file__).resolve().parent.parent
NM = BASE / "node_modules/@fontsource"


def _fonts():
    return (f"@font-face{{font-family:Slab;src:url('file://{NM}/alfa-slab-one/files/alfa-slab-one-latin-400-normal.woff2')}}"
            f"@font-face{{font-family:'Alfa Slab One';src:url('file://{NM}/alfa-slab-one/files/alfa-slab-one-latin-400-normal.woff2')}}"
            f"@font-face{{font-family:Sans;font-weight:800;src:url('file://{NM}/dm-sans/files/dm-sans-latin-800-normal.woff2')}}"
            f"@font-face{{font-family:'DM Sans';font-weight:800;src:url('file://{NM}/dm-sans/files/dm-sans-latin-800-normal.woff2')}}"
            f"@font-face{{font-family:'DM Mono';src:url('file://{NM}/dm-mono/files/dm-mono-latin-500-normal.woff2')}}")


def accent(t):
    return "".join(f'<span style="color:{C["green"]}">{E(x[1:-1])}</span>' if x.startswith("*") else E(x) for x in re.findall(r"\*[^*]+\*|[^*]+", t))


def page(v, W, H):
    host = (v.get("beats") or v.get("segments", [{}])[0].get("beats", [{}]))[0].get("host", "ghanti")
    hc = cast.CAST.get(host, {}).get("color", C["green"]); logo = (BASE / "assets/logo-icon.png").as_uri()
    hook = v.get("thumb") or v.get("hook") or v.get("title", "")
    vert = H > W; ch = 620 if vert else 520
    fs = (118 if len(hook) < 24 else 96 if len(hook) < 40 else 80) if vert else (96 if len(hook) < 24 else 80 if len(hook) < 40 else 66)
    return f"""<html><head><style>{_fonts()}
*{{margin:0;box-sizing:border-box}} body{{width:{W}px;height:{H}px;overflow:hidden;position:relative;font-family:Sans;color:{C['ink']};
background:radial-gradient(circle at {70 if not vert else 50}% {40 if not vert else 70}%,{hc}33,transparent 55%),radial-gradient(circle at 10% 0%,#13204a,transparent 50%),{C['bg']}}}
.g{{position:absolute;inset:0;background:linear-gradient(rgba(255,255,255,.04) 2px,transparent 2px) 0 0/80px 80px,linear-gradient(90deg,rgba(255,255,255,.04) 2px,transparent 2px) 0 0/80px 80px}}
.ab{{position:absolute}} .h{{font-family:Slab;line-height:1.02;letter-spacing:1px;text-shadow:0 6px 0 rgba(0,0,0,.5)}}
</style></head><body><div class="g"></div>
<div class="ab" style="left:{44 if not vert else 60}px;top:{36 if not vert else 110}px;display:flex;align-items:center;gap:14px">
<img src="{logo}" width="{70 if not vert else 96}" style="border-radius:16px"><span class="h" style="font-size:{36 if not vert else 48}px"><span style="color:{C['green']}">MARKET</span> SAMACHAR</span></div>
<div class="ab h" style="{'left:50px;top:150px;width:760px' if not vert else 'left:70px;right:70px;top:330px;text-align:center'};font-size:{fs}px">{accent(hook)}</div>
<div class="ab" style="{'right:20px;bottom:10px' if not vert else 'left:50%;margin-left:-' + str(ch // 2) + 'px;bottom:300px'}">{cast.svg(host, 'th', ch)}</div>
<div class="ab" style="{'left:54px;bottom:44px' if not vert else 'left:0;right:0;bottom:200px;text-align:center'}"><span style="font-family:Sans;font-weight:800;letter-spacing:3px;font-size:{26 if not vert else 34}px;background:{hc};color:#0B0B16;border-radius:999px;padding:10px 22px">{E(v.get('stamp', ''))}</span></div>
</body></html>"""


def main(job_path, work):
    from playwright.sync_api import sync_playwright
    job = json.loads(pathlib.Path(job_path).read_text())
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for v in job["videos"]:
            d = pathlib.Path(work).resolve() / v["id"]
            if not d.exists(): continue
            W, H = (1280, 720) if v["kind"] == "long" else (1080, 1920)
            f = d / "_thumb.html"; f.write_text(page(v, W, H))
            pg = b.new_page(viewport={"width": W, "height": H}); pg.goto(f.as_uri()); pg.wait_for_timeout(500)
            pg.screenshot(path=str(d / "thumb.png")); pg.close(); f.unlink()
            print("thumb", d / "thumb.png")
        b.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "work")
