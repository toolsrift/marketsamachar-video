#!/usr/bin/env python3
"""Zernio posting for MarketSamachar (runs on GitHub Actions; key from the ZERNIO_API_KEY repo secret).

  python3 engine/zernio.py drafts <dir with <id>/video.mp4, meta.json, thumb.png> <out drafts.json>
        long video -> YouTube draft (with thumbnail); each Short -> YouTube Short draft + Instagram Reel draft (cover)
  python3 engine/zernio.py publish <drafts.json> [--at "YYYY-MM-DD HH:MM"] [--spread MIN] [ids or video ids ...]
  python3 engine/zernio.py status <drafts.json>
Nothing is published by `drafts`. `publish` is only run after the owner approves.
"""
import os, sys, json, pathlib, mimetypes, urllib.request, urllib.error, datetime

API = "https://zernio.com/api/v1"
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def call(method, path, body=None, raw=None, ctype="application/json", url=None):
    h = {"Content-Type": ctype, "Accept": "application/json", "User-Agent": "marketsamachar-video"}
    if not url: h["Authorization"] = "Bearer " + os.environ["ZERNIO_API_KEY"]
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url or API + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            t = r.read().decode() or "{}"
            return json.loads(t) if t.strip()[:1] in "{[" else {"raw": t}
    except urllib.error.HTTPError as e:
        sys.exit(f"ZERNIO_ERROR {method} {url or path}: HTTP {e.code} {e.read().decode(errors='replace')[:600]}")


def accounts():
    r = call("GET", "/accounts"); items = r if isinstance(r, list) else r.get("accounts") or r.get("data") or []
    return {a.get("platform"): a.get("_id") or a.get("id") for a in items}


def upload(path):
    path = pathlib.Path(path); ct = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    p = call("POST", "/media/presign", {"filename": path.name, "contentType": ct})
    call("PUT", "", raw=path.read_bytes(), ctype=ct, url=p["uploadUrl"])
    return p["publicUrl"]


def pid(r):
    p = r.get("post", r); return p.get("_id") or p.get("id")


def drafts(d, out):
    acc = accounts(); yt, ig = acc.get("youtube"), acc.get("instagram"); res = []
    if not yt: sys.exit("ZERNIO_ERROR no YouTube account connected")
    for m in sorted(pathlib.Path(d).glob("*/meta.json")):
        meta = json.loads(m.read_text()); mp4 = m.parent / "video.mp4"; thumb = m.parent / "thumb.png"
        if not mp4.exists(): continue
        vurl = upload(mp4); turl = upload(thumb) if thumb.exists() else None
        media = {"type": "video", "url": vurl}
        if turl and meta["kind"] == "long": media["thumbnail"] = turl
        body = {"content": meta["description"], "tags": meta.get("tags", []), "isDraft": True, "mediaItems": [media],
                "platforms": [{"platform": "youtube", "accountId": yt, "platformSpecificData": {
                    "title": meta["title"][:100], "visibility": os.environ.get("ZERNIO_YT_VISIBILITY", "public"), "categoryId": "25", "madeForKids": False}}]}
        r = call("POST", "/posts", body); res.append(dict(video=meta["id"], kind=meta["kind"], platform="youtube", id=pid(r), title=meta["title"]))
        print(f"DRAFT youtube {meta['id']}: {res[-1]['id']}")
        if meta["kind"] == "short" and ig:
            im = {"type": "video", "url": vurl}
            if turl: im["instagramThumbnail"] = turl
            r = call("POST", "/posts", {"content": meta["caption"], "isDraft": True, "mediaItems": [im], "platforms": [{"platform": "instagram", "accountId": ig}]})
            res.append(dict(video=meta["id"], kind="reel", platform="instagram", id=pid(r), title=meta["title"]))
            print(f"DRAFT instagram {meta['id']}: {res[-1]['id']}")
    pathlib.Path(out).write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print("ZERNIO_DRAFTS " + " ".join(f'{x["video"]}/{x["platform"]}={x["id"]}' for x in res))


def publish(dfile, rest):
    at, spread = None, None
    while rest[:1] and rest[0] in ("--at", "--spread"):
        if rest[0] == "--at": at = datetime.datetime.strptime(rest[1], "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        else: spread = int(rest[1])
        rest = rest[2:]
    ds = json.loads(pathlib.Path(dfile).read_text())
    sel = [x for x in ds if not rest or x["id"] in rest or x["video"] in rest]
    if spread and not at: at = datetime.datetime.now(IST) + datetime.timedelta(minutes=5)
    order = {v: i for i, v in enumerate(dict.fromkeys(x["video"] for x in sel if x["kind"] != "long"))}
    for x in sel:
        when = at + datetime.timedelta(minutes=spread * (order.get(x["video"], -1) + 1)) if (spread and at and x["kind"] != "long") else at
        body = {"isDraft": False, "timezone": "Asia/Kolkata"}
        if when: body["scheduledFor"] = when.isoformat()
        else: body["publishNow"] = True
        call("PUT", f"/posts/{x['id']}", body)
        print(f"{x['video']} {x['platform']}: {'SCHEDULED ' + when.strftime('%d %b %H:%M IST') if when else 'PUBLISHING'}")


def status(dfile):
    for x in json.loads(pathlib.Path(dfile).read_text()):
        p = call("GET", f"/posts/{x['id']}"); p = p.get("post", p)
        urls = ", ".join(f'{q.get("platform")}: {q.get("status", "")} {q.get("platformPostUrl") or ""}'.strip() for q in p.get("platforms", []))
        print(f'{x["video"]:<14} {x["platform"]:<9} {p.get("status", "")}  {urls}')


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "drafts": drafts(sys.argv[2], sys.argv[3])
    elif cmd == "publish": publish(sys.argv[2], sys.argv[3:])
    elif cmd == "status": status(sys.argv[2])
    elif cmd == "accounts": print(accounts())
