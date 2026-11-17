"""MarketSamachar 3D cast — real three.js characters (glossy physical materials, studio + accent rim light,
reflections from a room environment), rendered on every HyperFrames frame via the `hf-seek` event.

One transparent WebGL canvas covers the host area. Python passes `windows`: when each character is on screen,
where, how big, the lip-sync amplitudes, gestures and reactions. All motion is a pure function of time.
"""
import json, shutil, pathlib
from fx import NM

FILES = [("three/build/three.module.js", "three/three.module.js"), ("three/build/three.core.js", "three/three.core.js"),
         ("three/examples/jsm/environments/RoomEnvironment.js", "three/addons/environments/RoomEnvironment.js"),
         ("three/examples/jsm/geometries/RoundedBoxGeometry.js", "three/addons/geometries/RoundedBoxGeometry.js")]


def setup(proj):
    lib = pathlib.Path(proj) / "assets/lib"
    for src, dst in FILES:
        (lib / dst).parent.mkdir(parents=True, exist_ok=True); shutil.copy(NM / src, lib / dst)


def html(left, top, w, h, windows, accent, z=10):
    data = json.dumps(dict(w=w, h=h, accent=accent, windows=windows), separators=(",", ":"))
    return (f'<canvas id="gl3d" width="{w}" height="{h}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;z-index:{z};pointer-events:none"></canvas>'
            '<script type="importmap">{"imports":{"three":"./assets/lib/three/three.module.js","three/addons/":"./assets/lib/three/addons/"}}</script>'
            '<script type="module">' + JS.replace("__DATA__", data) + '</script>')


JS = r"""
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
const D = __DATA__;
const canvas = document.getElementById("gl3d");
const R = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true, preserveDrawingBuffer:true});
R.setPixelRatio(1); R.setSize(D.w, D.h, false); R.toneMapping = THREE.NeutralToneMapping; R.toneMappingExposure = 1.0;
R.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const pm = new THREE.PMREMGenerator(R); scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
// orthographic pixel camera: x right, y down (we flip y when placing)
const cam = new THREE.OrthographicCamera(0, D.w, 0, -D.h, -2000, 2000); cam.position.z = 1000;
scene.add(new THREE.AmbientLight(0xffffff, 0.35));
const key = new THREE.DirectionalLight(0xffffff, 2.4); key.position.set(-300, 500, 800); scene.add(key);
const fill = new THREE.DirectionalLight(0xbfd4ff, 0.8); fill.position.set(500, 100, 400); scene.add(fill);
const rim = new THREE.DirectionalLight(new THREE.Color(D.accent), 2.2); rim.position.set(300, 300, -600); scene.add(rim);
const rim2 = new THREE.DirectionalLight(0x00ff88, 1.0); rim2.position.set(-500, -100, -500); scene.add(rim2);

const M = (c, o={}) => new THREE.MeshPhysicalMaterial(Object.assign({color:new THREE.Color(c), roughness:.34, metalness:0, clearcoat:.8, clearcoatRoughness:.15, envMapIntensity:.65}, o));
const INK = M(0x14141c, {roughness:.4}); const WHITE = M(0xffffff, {roughness:.18}); const MOUTH = M(0x5a0d1e, {roughness:.5, clearcoat:.3});
const TONGUE = M(0xff6b8a); const CHEEK = M(0xff7a9a, {transparent:true, opacity:.55, roughness:.6, clearcoat:0});
const GOLD = M(0xf5b83d, {metalness:.85, roughness:.22}); const SILVER = M(0xdfe6ef, {metalness:.9, roughness:.18});
const S = (r, w=32, h=24) => new THREE.SphereGeometry(r, w, h);
const mesh = (g, m, x=0, y=0, z=0) => { const o = new THREE.Mesh(g, m); o.position.set(x, y, z); return o; };
function canvasTex(draw, w=512, h=512){ const c=document.createElement("canvas"); c.width=w; c.height=h; draw(c.getContext("2d"), w, h);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=4; return t; }
function lathe(pts, m, seg=64){ return new THREE.Mesh(new THREE.LatheGeometry(pts.map(p=>new THREE.Vector2(p[0],p[1])), seg), m); }
function extrudeShape(path, depth, m){ const s=new THREE.Shape(); path.forEach((p,i)=> i? s.lineTo(p[0],p[1]) : s.moveTo(p[0],p[1])); s.closePath();
  const g=new THREE.ExtrudeGeometry(s,{depth, bevelEnabled:true, bevelThickness:.04, bevelSize:.04, bevelSegments:4}); g.center(); return new THREE.Mesh(g, m); }

// ---- shared rig: face, arms, feet. Units: character ~2.2 tall, feet at y=0.
function face(par, y, z, s=1, opts={}){
  const f = new THREE.Group(); f.position.set(0, y, z); f.scale.setScalar(s); par.add(f);
  const eyes = new THREE.Group(); f.add(eyes); const lids=[];
  for (const sx of [-1, 1]){
    const e = new THREE.Group(); e.position.set(sx*.27, .1, 0); eyes.add(e);
    const w = mesh(S(.2), WHITE); w.scale.set(1, 1.15, .55); e.add(w);
    const p = mesh(S(.11), INK, 0, -.01, .1); p.scale.set(1, 1.1, .5); e.add(p);
    e.add(mesh(S(.035, 12, 8), WHITE, .04, .05, .16));
    lids.push(e);
  }
  if (opts.glasses){ const gm=M(0x1b1b28,{metalness:.6}); for(const sx of [-1,1]){ const r=mesh(new THREE.TorusGeometry(.24,.035,12,40), gm, sx*.27,.1,.08); f.add(r);} f.add(mesh(new THREE.BoxGeometry(.16,.035,.035), gm, 0,.13,.1)); }
  const mouth = new THREE.Group(); mouth.position.set(0, -.28, .02); f.add(mouth);
  const mo = mesh(S(.16), MOUTH); mo.scale.set(1.1, .55, .35); mouth.add(mo);
  const tg = mesh(S(.08), TONGUE, 0, -.05, .04); tg.scale.set(1.2, .5, .4); mouth.add(tg);
  for (const sx of [-1,1]){ const c=mesh(S(.09), CHEEK, sx*.5, -.12, -.02); c.scale.set(1, .6, .3); f.add(c); }
  return {f, eyes, lids, mouth};
}
function arm(par, side, x, y, z, mat, len=.55, hand=null){
  const pv = new THREE.Group(); pv.position.set(x, y, z); par.add(pv);
  const a = mesh(new THREE.CapsuleGeometry(.075, len, 8, 16), mat, 0, -len/2, 0); pv.add(a);
  pv.add(mesh(S(.13), hand || mat, 0, -len-.05, 0));
  pv.rotation.z = side * .35; pv.userData.rest = side * .35; return pv;
}
function feet(par, mat, sep=.28, y=.07){ for (const sx of [-1,1]){ const f=mesh(S(.17), mat, sx*sep, y, .06); f.scale.set(1.15,.55,1.45); par.add(f); } }

// ---- the 14 characters
function build(kind){
  const root = new THREE.Group(), bob = new THREE.Group(); root.add(bob);
  let fc, armL, armR, extra = {};
  const add = o => (bob.add(o), o);
  if (kind === "ghanti"){            // market bell
    const b = lathe([[0,2.05],[.22,2.02],[.38,1.9],[.5,1.6],[.58,1.2],[.68,.75],[.86,.42],[.9,.34],[0,.34]], GOLD); add(b);
    add(mesh(new THREE.TorusGeometry(.17,.06,16,40), GOLD, 0, 2.12, 0));
    extra.clap = add(mesh(S(.16), M(0xb7791f,{metalness:.8,roughness:.3}), 0, .22, 0));
    fc = face(bob, 1.12, .62, .95); armL = arm(bob,-1,-.62,1.05,0,GOLD); armR = arm(bob,1,.62,1.05,0,GOLD); feet(bob, INK, .3, .05);
  } else if (kind === "teji" || kind === "mandi"){   // gainers (green, arrow up) / losers (red, arrow down)
    const up = kind === "teji", col = up ? 0x00e68a : 0xff4d6d;
    add(mesh(new THREE.CapsuleGeometry(.62, .55, 16, 32), M(col), 0, 1.0, 0));
    const ar = extrudeShape(up ? [[0,.55],[.5,0],[.2,0],[.2,-.45],[-.2,-.45],[-.2,0],[-.5,0]] : [[0,-.55],[.5,0],[.2,0],[.2,.45],[-.2,.45],[-.2,0],[-.5,0]], .22, M(up ? 0xffffff : 0xffe2e8));
    ar.position.set(0, up ? 2.15 : 2.1, 0); ar.scale.setScalar(.9); add(ar); extra.badge = ar;
    fc = face(bob, 1.18, .6, .95); armL = arm(bob,-1,-.6,1.1,0,M(col)); armR = arm(bob,1,.6,1.1,0,M(col)); feet(bob, INK);
  } else if (kind === "munshi"){     // results — scholar with glasses and a clipboard
    add(mesh(S(.78, 48, 32), M(0x8b5cf6), 0, 1.05, 0));
    const cap = add(mesh(new THREE.BoxGeometry(.9,.08,.9), INK, 0, 1.9, 0)); cap.rotation.y = .5;
    add(mesh(new THREE.CylinderGeometry(.3,.34,.2,24), INK, 0, 1.8, 0));
    fc = face(bob, 1.15, .7, .95, {glasses:true}); armL = arm(bob,-1,-.7,1.05,0,M(0x8b5cf6)); armR = arm(bob,1,.7,1.05,0,M(0x8b5cf6));
    const cb = mesh(new RoundedBoxGeometry(.45,.6,.06,3,.04), M(0xf2f4f8), .05, -.75, .12); armR.add(cb);
    for (let i=0;i<3;i++) cb.add(mesh(new THREE.BoxGeometry(.3,.04,.02), M(0x8b5cf6), 0, .12-i*.13, .04));
    feet(bob, INK);
  } else if (kind === "bhonpu"){     // announcements — megaphone
    add(lathe([[0,.3],[.42,.3],[.5,.6],[.62,1.3],[.82,1.95],[.86,2.0],[.7,2.0],[.58,1.6],[0,1.6]], M(0xff8a3d)));
    add(mesh(new THREE.TorusGeometry(.84,.06,16,60), M(0xffffff), 0, 2.0, 0)).rotation.x = Math.PI/2;
    fc = face(bob, 1.05, .6, .9); armL = arm(bob,-1,-.55,1.05,0,M(0xff8a3d)); armR = arm(bob,1,.55,1.05,0,M(0xff8a3d)); feet(bob, INK);
  } else if (kind === "golu"){       // dividends — piggy bank
    const P = M(0xff8fb1); add(mesh(S(.82, 48, 32), P, 0, 1.0, 0)).scale.set(1.08, .95, 1);
    const sn = add(mesh(new THREE.CylinderGeometry(.22,.25,.2,32), M(0xff6f9c), 0, .82, .8)); sn.rotation.x = Math.PI/2;
    for (const sx of [-1,1]) add(mesh(S(.045), INK, sx*.08, .82, .91));
    for (const sx of [-1,1]){ const e=add(mesh(new THREE.ConeGeometry(.17,.3,24), P, sx*.45, 1.75, 0)); e.rotation.z = -sx*.4; }
    add(mesh(new THREE.BoxGeometry(.4,.05,.1), INK, 0, 1.82, 0));
    extra.coin = add(mesh(new THREE.CylinderGeometry(.18,.18,.05,32), GOLD, 0, 2.3, 0)); extra.coin.rotation.x = Math.PI/2;
    fc = face(bob, 1.27, .64, .85); armL = arm(bob,-1,-.78,1.0,0,P,.45); armR = arm(bob,1,.78,1.0,0,P,.45); feet(bob, P, .35);
  } else if (kind === "katli"){      // splits — diamond sweet with silver leaf
    const g = add(mesh(new THREE.OctahedronGeometry(1, 0), M(0xf3e3c3, {roughness:.5}), 0, 1.05, 0)); g.scale.set(1.05, .82, .35); g.rotation.y = Math.PI/4;
    const t = add(mesh(new THREE.OctahedronGeometry(1, 0), SILVER, 0, 1.06, .02)); t.scale.set(1.0, .78, .3); t.rotation.y = Math.PI/4;
    fc = face(bob, 1.05, .36, .85); armL = arm(bob,-1,-.9,1.0,0,M(0xf3e3c3)); armR = arm(bob,1,.9,1.0,0,M(0xf3e3c3)); feet(bob, INK);
  } else if (kind === "tohfa"){      // bonus — gift box
    const B = M(0x2dd4bf); add(mesh(new RoundedBoxGeometry(1.4,1.25,1.2,5,.12), B, 0, .85, 0));
    const lid = add(mesh(new RoundedBoxGeometry(1.55,.3,1.35,5,.08), B, 0, 1.6, 0)); extra.lid = lid;
    const Y = M(0xfacc15); add(mesh(new THREE.BoxGeometry(.22,1.27,1.22), Y, 0, .85, 0)); lid.add(mesh(new THREE.BoxGeometry(.24,.32,1.37), Y));
    for (const sx of [-1,1]){ const bw=mesh(new THREE.TorusGeometry(.2,.07,12,32), Y, sx*.2, .25, 0); bw.scale.set(1,.7,1); lid.add(bw); }
    fc = face(bob, .95, .62, .85); armL = arm(bob,-1,-.72,1.05,0,B); armR = arm(bob,1,.72,1.05,0,B); feet(bob, INK, .35);
  } else if (kind === "wapsi"){      // buybacks — magnet
    const red = M(0xef4444); const u = add(mesh(new THREE.TorusGeometry(.62,.28,24,64,Math.PI), red, 0, 1.25, 0)); u.rotation.z = Math.PI;
    for (const sx of [-1,1]){ add(mesh(new THREE.CylinderGeometry(.28,.28,.5,32), red, sx*.62, 1.5, 0)); add(mesh(new THREE.CylinderGeometry(.285,.285,.28,32), SILVER, sx*.62, 1.88, 0)); }
    fc = face(bob, .8, .32, .75); armL = arm(bob,-1,-.95,1.2,0,red); armR = arm(bob,1,.95,1.2,0,red); feet(bob, INK, .3);
  } else if (kind === "naya"){       // IPOs — rocket
    const Bm = M(0xf2f4f8); add(lathe([[0,.25],[.5,.3],[.62,.8],[.6,1.4],[.45,1.9],[.2,2.25],[0,2.35]], Bm));
    add(lathe([[0,1.9],[.46,1.88],[.2,2.25],[0,2.36]], M(0x38bdf8)));
    for (let i=0;i<3;i++){ const f=extrudeShape([[0,0],[.5,-.2],[.5,-.6],[0,-.3]], .08, M(0x38bdf8)); const g=new THREE.Group(); g.rotation.y=i*2.094+.5; f.position.set(.55,.55,0); g.add(f); bob.add(g); }
    const win = add(mesh(new THREE.TorusGeometry(.2,.05,12,32), SILVER, 0, 1.55, .58)); add(mesh(S(.18), M(0x38bdf8,{transmission:.3}), 0, 1.55, .52)).scale.z=.4;
    extra.flame = add(mesh(new THREE.ConeGeometry(.28,.7,24), M(0xff8a3d,{emissive:0xff6a00, emissiveIntensity:.8}), 0, -.1, 0)); extra.flame.rotation.z = Math.PI;
    fc = face(bob, .95, .62, .75); armL = arm(bob,-1,-.62,1.0,0,Bm); armR = arm(bob,1,.62,1.0,0,Bm);
  } else if (kind === "tareekh"){    // events — calendar block
    add(mesh(new RoundedBoxGeometry(1.35,1.5,.55,4,.1), M(0xf2f4f8), 0, 1.0, 0));
    add(mesh(new RoundedBoxGeometry(1.37,.42,.57,4,.1), M(0xff4d6d), 0, 1.6, 0));
    for (const sx of [-.35,.35]) add(mesh(new THREE.TorusGeometry(.1,.035,10,24), SILVER, sx, 1.86, 0));
    fc = face(bob, .95, .3, .8); armL = arm(bob,-1,-.72,1.05,0,M(0xf2f4f8)); armR = arm(bob,1,.72,1.05,0,M(0xf2f4f8)); feet(bob, INK);
  } else if (kind === "desi"){       // DII — rupee coin
    const tex = canvasTex((g,w,h)=>{ g.fillStyle="#f5c542"; g.fillRect(0,0,w,h); g.fillStyle="#b7791f"; g.font="bold 300px sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.fillText("₹", w/2, h*.36); });
    const c = add(mesh(new THREE.CylinderGeometry(.9,.9,.28,64), [M(0xd4a017,{metalness:.8,roughness:.25}), M(0xffffff,{map:tex, metalness:.5, roughness:.3}), GOLD], 0, 1.1, 0)); c.rotation.x = Math.PI/2;
    add(mesh(new THREE.TorusGeometry(.9,.05,12,80), GOLD, 0, 1.1, 0));
    fc = face(bob, .85, .2, .75); armL = arm(bob,-1,-.88,1.1,0,GOLD); armR = arm(bob,1,.88,1.1,0,GOLD); feet(bob, INK);
  } else if (kind === "videshi"){    // FII — globe with an orbit ring
    const tex = canvasTex((g,w,h)=>{ g.fillStyle="#2563eb"; g.fillRect(0,0,w,h); g.fillStyle="#22c55e";
      const blobs=[[.18,.35,.13,.12],[.3,.62,.08,.14],[.52,.3,.1,.09],[.58,.55,.08,.13],[.78,.38,.14,.1],[.85,.7,.06,.06],[.1,.75,.05,.05]];
      for (const b of blobs){ g.beginPath(); g.ellipse(b[0]*w,b[1]*h,b[2]*w,b[3]*h,0,0,7); g.fill(); } }, 1024, 512);
    tex.wrapS = THREE.RepeatWrapping;
    extra.globe = add(mesh(S(.82, 64, 48), M(0xffffff,{map:tex, roughness:.4}), 0, 1.05, 0));
    const ring = add(mesh(new THREE.TorusGeometry(1.15,.04,12,96), SILVER, 0, 1.05, 0)); ring.rotation.set(1.2, 0, .35); extra.ring = ring;
    fc = face(bob, 1.05, .72, .85); armL = arm(bob,-1,-.78,1.0,0,M(0x2563eb)); armR = arm(bob,1,.78,1.0,0,M(0x2563eb)); feet(bob, INK);
  } else {                            // arth — economy professor tortoise
    const G = M(0x22a06b); add(mesh(S(.62, 40, 32), G, 0, 1.55, .15));
    const sh = add(mesh(new THREE.SphereGeometry(.85, 48, 24, 0, Math.PI*2, 0, Math.PI/2), M(0x0f766e), 0, .55, -.2)); sh.scale.set(1, .9, .8);
    add(mesh(new THREE.CylinderGeometry(.86,.86,.12,48), M(0xfacc15), 0, .55, -.2));
    const cap = add(mesh(new THREE.BoxGeometry(.85,.07,.85), INK, 0, 2.15, .15)); cap.rotation.y = .4;
    add(mesh(new THREE.CylinderGeometry(.28,.32,.18,24), INK, 0, 2.05, .15));
    fc = face(bob, 1.58, .66, .8, {glasses:true}); armL = arm(bob,-1,-.6,1.15,0,G); armR = arm(bob,1,.6,1.15,0,G); feet(bob, G, .35);
  }
  return {root, bob, fc, armL, armR, extra, kind};
}

// ---- motion helpers (pure functions of time)
const clamp = (x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const backOut = x=>{x=clamp(x); const c=1.7; return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2);};
const ease = x=>{x=clamp(x); return x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2;};
const pulse = (t,a,d)=> (t<a||t>a+d)?0:Math.sin(Math.PI*(t-a)/d);
function amp(win, t){ const T=win.talk; if(!T||!T.length) return 0; const dt=T.length>1?(T[1][0]-T[0][0]):.066;
  const i=Math.round((t-T[0][0])/dt); return (i<0||i>=T.length)?0:T[i][1]; }

const chars = D.windows.map(w=>{ const c=build(w.char); c.win=w; c.root.visible=false; scene.add(c.root); return c; });

function pose(c, t){
  const w=c.win, lt=t-w.t_in, out=t-w.t_out;
  const on = lt>=-0.02 && out<0.45; c.root.visible=on; if(!on) return;
  const unit = w.size/2.3;
  let s = unit*(lt<.55? backOut(lt/.55) : 1); if(out>0) s*= 1-ease(out/.4);
  c.root.position.set(w.x, -(w.y), 0); c.root.scale.setScalar(Math.max(.001,s));
  const b=c.bob; let y=Math.abs(Math.sin(t*Math.PI/.62))*.05, sx=1, sy=1, rz=0;
  // land squash after the pop
  const land=pulse(lt,.42,.3); sx+=land*.16; sy-=land*.2;
  // reactions
  for (const [mt,mood] of (w.moods||[])){
    const k=t-mt; if(k<0||k>1.4) continue;
    if(mood==="up"){ const pre=pulse(k,0,.14), air=pulse(k,.12,.5), post=pulse(k,.6,.22); sy+=-pre*.18+air*.08-post*.15; sx+=pre*.12+post*.1; y+=air*.75; }
    else { const d=ease(k/.35)*(1-ease((k-1.0)/.35)); sy-=d*.1; y-=d*.06; rz+=d*.08; }
  }
  b.position.y=y; b.scale.set(sx,sy,sx); b.rotation.z=rz + Math.sin(t*1.3)*.035;
  b.rotation.y = (w.look||0)*.35 + Math.sin(t*.8)*.22;     // turn to show the 3D form
  // arms: rest + gestures
  let aL=c.armL.userData.rest, aR=c.armR.userData.rest, xL=0, xR=0;
  for (const [gt,kind] of (w.gest||[])){
    const k=t-gt; if(k<0||k>1.6) continue; const e=ease(k/.25)*(1-ease((k-1.25)/.3));
    if(kind==="wave"){ aR = aR + e*(2.5-aR) + e*Math.sin(k*14)*.35; }
    else if(kind==="cheer"){ aR=aR+e*(2.7-aR); aL=aL+e*(-2.7-aL); }
    else if(kind==="present"||kind==="open"||kind==="split"){ aR=aR+e*(1.4-aR); aL=aL+e*(-1.4-aL); }
    else if(kind==="shrug"){ aR=aR+e*(1.0-aR); aL=aL+e*(-1.0-aL); xL=xR=e*.5; }
    else if(kind==="ring"){ b.rotation.z += e*Math.sin(k*16)*.18; aR=aR+e*(1.9-aR); }
    else { const dir=(w.look||1)>=0?1:-1; if(dir>0) aR=aR+e*(1.75-aR); else aL=aL+e*(-1.75-aL); }
  }
  for (const [mt,mood] of (w.moods||[])){ const k=t-mt; if(mood==="up"&&k>=0&&k<1.1){ const e=ease(k/.15)*(1-ease((k-.8)/.3)); aR=aR+e*(2.6-aR); aL=aL+e*(-2.6-aL);} }
  c.armL.rotation.set(xL,0,aL); c.armR.rotation.set(xR,0,aR);
  // face: blink, look, talk
  const bt=(t+w.seed*.37)%2.9, blink=bt<.12?Math.sin(Math.PI*bt/.12):0;
  for (const e of c.fc.lids) e.scale.y=1-blink*.92;
  c.fc.eyes.position.x=(w.look||0)*.06;
  const a=amp(w,t); c.fc.mouth.scale.set(1, .25+Math.min(1.5,a*10), 1);
  // character extras
  const X=c.extra;
  if(X.clap) X.clap.position.x=Math.sin(t*9)*.08;
  if(X.globe) X.globe.rotation.y=t*.6; if(X.ring) X.ring.rotation.z=.35+t*.4;
  if(X.coin) { X.coin.position.y=2.3+Math.sin(t*3)*.08; X.coin.rotation.z=t*2; }
  if(X.flame) X.flame.scale.set(1, .8+Math.abs(Math.sin(t*18))*.4, 1);
  if(X.lid) X.lid.position.y=1.6+Math.max(0,Math.sin(t*2.2))*.12;
  if(X.badge) X.badge.rotation.y=Math.sin(t*1.7)*.5;
}

function renderAt(t){ for (const c of chars) pose(c, t); R.render(scene, cam); }
window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
window.__hf.buildReady["ms3d"] = R.compileAsync ? R.compileAsync(scene, cam) : Promise.resolve();
window.addEventListener("hf-seek", (e)=>renderAt(e.detail.time));
window.__ms3d = renderAt;
renderAt(0);
"""
