"""render.py <pair> snap T1 T2 ...   |   render.py <pair> full [procs]   |   render.py <pair> chunk a b name (internal)"""
import sys, json, os, subprocess, pathlib, math
ROOT = pathlib.Path(__file__).resolve().parent.parent; ENG = ROOT / "engine"
pair, mode = sys.argv[1], sys.argv[2]; OD = ROOT / "out" / pair
spec = json.load(open(OD / "spec.json")); FPS = 30; W, H = 1920, 1080
page = ENG / f"page_{pair}.html"
page.write_text((ENG / "page.html").read_text().replace('src="SPEC"', f'src="../out/{pair}/spec.js"'))
def open_page(p):
    b = p.chromium.launch(args=["--disable-gpu"]); pg = b.new_page(viewport=dict(width=W, height=H))
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
    pg.goto("file://" + str(page)); pg.evaluate("window.ready"); pg.wait_for_timeout(300); return b, pg, errs
if mode == "full":
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    N = round(spec["total"] * FPS); CH = 240; chunks = [(a, min(N, a + CH)) for a in range(0, N, CH)]
    todo = [c for c in chunks if not (OD / f"c{c[0]:06d}.mp4").exists()]
    groups = [todo[i::procs] for i in range(procs)]
    ps = [subprocess.Popen([sys.executable, __file__, pair, "chunk", json.dumps(g)]) for g in groups if g]
    rc = [p.wait() for p in ps]
    with open(OD / "concat.txt", "w") as f:
        for a, b in chunks: f.write(f"file 'c{a:06d}.mp4'\n")
    missing = [a for a, b in chunks if not (OD / f"c{a:06d}.mp4").exists()]
    print("frames", N, "chunks", len(chunks), "missing", missing, "rc", rc)
    sys.exit(0)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b, pg, errs = open_page(p)
    if mode == "snap":
        for T in sys.argv[3:]:
            pg.evaluate(f"seek({T})"); pg.screenshot(path=str(OD / f"snap_{float(T):07.2f}.jpg"), type="jpeg", quality=85)
    elif mode == "chunk":
        for a, z in json.loads(sys.argv[3]):
            tmp = OD / f"c{a:06d}.tmp.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", "30", "-c:v", "mjpeg", "-i", "-",
                                   "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30", str(tmp)], stdin=subprocess.PIPE)
            for f in range(a, z):
                pg.evaluate(f"seek({f / FPS})"); ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            ff.stdin.close()
            if ff.wait() == 0: os.replace(tmp, OD / f"c{a:06d}.mp4")
            print("chunk", a, flush=True)
    if errs: print("ERRORS:", errs[:10])
    b.close()
