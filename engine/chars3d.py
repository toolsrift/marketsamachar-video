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

// ---- the presenter: one clear 3D news anchor; suit colour + a floating topic icon change per category
const SKIN = M(0xf1c7a1, {clearcoat:.2, roughness:.55}); const HAIR = M(0x23262f, {roughness:.5, clearcoat:.3});
const SHIRT = M(0xf7f8fb, {clearcoat:.2, roughness:.5}); const DARK = M(0x12142b, {roughness:.45});
function icon(kind, col){
  const g = new THREE.Group(); const C = M(col);
  if (kind==="ghanti"){ g.add(lathe([[0,.62],[.09,.6],[.15,.5],[.2,.25],[.27,.06],[0,.06]], GOLD)); g.add(mesh(S(.06), GOLD, 0, .02, 0)); }
  else if (kind==="teji"||kind==="mandi"){ const up=kind==="teji"; const a=extrudeShape(up?[[0,.3],[.27,0],[.11,0],[.11,-.26],[-.11,-.26],[-.11,0],[-.27,0]]:[[0,-.3],[.27,0],[.11,0],[.11,.26],[-.11,.26],[-.11,0],[-.27,0]], .1, M(up?0x00e68a:0xff4d6d)); a.position.y=.3; g.add(a); }
  else if (kind==="munshi"){ const d=mesh(new RoundedBoxGeometry(.4,.5,.06,3,.03), M(0xf7f8fb), 0, .3, 0); g.add(d); for(let k=0;k<3;k++) d.add(mesh(new THREE.BoxGeometry(.26,.035,.02), C, 0, .12-k*.11, .035)); }
  else if (kind==="bhonpu"){ const m=lathe([[0,0],[.08,0],[.1,.12],[.24,.42],[.26,.44],[0,.44]], M(0xff8a3d)); m.rotation.z=-1.2; m.position.set(-.12,.3,0); g.add(m); }
  else if (kind==="golu"||kind==="desi"){ const tex=canvasTex((x,w,h)=>{x.fillStyle="#f5c542";x.fillRect(0,0,w,h);x.fillStyle="#9a6a12";x.font="bold 300px sans-serif";x.textAlign="center";x.textBaseline="middle";x.fillText("₹",w/2,h*.36);});
    const c=mesh(new THREE.CylinderGeometry(.28,.28,.07,48), [GOLD, M(0xffffff,{map:tex,metalness:.4,roughness:.3}), GOLD], 0, .3, 0); c.rotation.x=Math.PI/2; g.add(c); }
  else if (kind==="katli"){ for(const sx of [-1,1]){ const h=mesh(new RoundedBoxGeometry(.2,.4,.12,3,.03), M(0xf5b83d), sx*.13, .3, 0); h.rotation.z=sx*.18; g.add(h);} }
  else if (kind==="tohfa"){ g.add(mesh(new RoundedBoxGeometry(.42,.36,.42,3,.04), M(0x2dd4bf), 0, .22, 0)); g.add(mesh(new THREE.BoxGeometry(.09,.38,.44), M(0xfacc15), 0, .22, 0)); g.add(mesh(new THREE.TorusGeometry(.08,.03,10,24), M(0xfacc15), 0, .46, 0)); }
  else if (kind==="wapsi"){ const u=mesh(new THREE.TorusGeometry(.17,.08,16,40,Math.PI), M(0xef4444), 0, .36, 0); u.rotation.z=Math.PI; g.add(u); for(const sx of [-1,1]) g.add(mesh(new THREE.CylinderGeometry(.08,.08,.14,20), SILVER, sx*.17, .44, 0)); }
  else if (kind==="naya"){ g.add(lathe([[0,0],[.12,.03],[.14,.25],[.08,.45],[0,.52]], M(0xf7f8fb))); g.add(mesh(new THREE.ConeGeometry(.08,.16,16), M(0x38bdf8), 0, .48, 0)); }
  else if (kind==="tareekh"){ g.add(mesh(new RoundedBoxGeometry(.42,.42,.1,3,.04), M(0xf7f8fb), 0, .3, 0)); g.add(mesh(new RoundedBoxGeometry(.43,.12,.11,3,.04), M(0xff4d6d), 0, .47, 0)); }
  else if (kind==="videshi"){ const tex=canvasTex((x,w,h)=>{x.fillStyle="#2563eb";x.fillRect(0,0,w,h);x.fillStyle="#22c55e";for(const b of [[.2,.4,.12,.15],[.55,.3,.1,.1],[.75,.6,.14,.12]]){x.beginPath();x.ellipse(b[0]*w,b[1]*h,b[2]*w,b[3]*h,0,0,7);x.fill();}},512,256);
    g.add(mesh(S(.25,40,30), M(0xffffff,{map:tex,roughness:.4}), 0, .3, 0)); }
  else { for(let k=0;k<3;k++) g.add(mesh(new RoundedBoxGeometry(.11,.18+k*.14,.11,2,.02), M(k===2?0x00e68a:0x2dd4bf), -.15+k*.15, .09+k*.07+.05, 0)); }
  return g;
}
const ANCHOR = {   // three co-anchors: suit colour, hair, extras
  A: {suit:0x2f6fed, hair:0x23262f, style:"short", tie:0x12142b},
  B: {suit:0xe2557a, hair:0x3b2416, style:"bob", tie:null},
  C: {suit:0x64748b, hair:0xc9ccd3, style:"side", tie:0xf5b83d, glasses:true},
};
function build(kind, col, who){
  const P = ANCHOR[who] || ANCHOR.A;
  const root = new THREE.Group(), bob = new THREE.Group(); root.add(bob);
  const add = o => (bob.add(o), o); const SUIT = M(P.suit, {clearcoat:.35, roughness:.5}); const HR = M(P.hair, {roughness:.5, clearcoat:.3}); const extra = {};
  // short legs + shoes (chunky, friendly proportions)
  for (const sx of [-1,1]){ add(mesh(new THREE.CapsuleGeometry(.14,.16,8,16), DARK, sx*.18, .26, 0)); const sh=add(mesh(S(.16), DARK, sx*.19, .08, .07)); sh.scale.set(1.1,.5,1.5); }
  // torso: wide, short
  const tor = add(mesh(new THREE.CapsuleGeometry(.48,.18,12,32), SUIT, 0, .86, 0)); tor.scale.set(1.18, 1, .82);
  const v = extrudeShape([[-.18,.18],[.18,.18],[0,-.2]], .02, SHIRT); v.position.set(0, 1.16, .37); add(v);
  if (P.tie){ if (P.style==="side"){ for(const sx of [-1,1]){ const b=extrudeShape([[0,0],[sx*.12,.07],[sx*.12,-.07]], .03, M(P.tie)); b.position.set(0,1.27,.4); add(b);} add(mesh(S(.035), M(P.tie), 0, 1.27, .42)); }
    else { const tie = extrudeShape([[0,.08],[.06,.03],[.045,-.22],[0,-.27],[-.045,-.22],[-.06,.03]], .03, M(P.tie)); tie.position.set(0, 1.12, .4); add(tie); } }
  else { add(mesh(new THREE.TorusGeometry(.13,.018,8,32), GOLD, 0, 1.24, .3)).rotation.x = 1.2; }
  for (const sx of [-1,1]){ const l = extrudeShape([[0,.2],[sx*.17,0],[sx*.06,-.2]], .03, M(P.suit,{roughness:.4})); l.position.set(sx*.14, 1.12, .38); add(l); }
  add(mesh(new THREE.CylinderGeometry(.12,.13,.1,20), SKIN, 0, 1.38, 0));
  // big friendly head
  const head = new THREE.Group(); head.position.set(0, 1.86, 0); bob.add(head);
  const hd = mesh(S(.5,48,36), SKIN); hd.scale.set(1.04,1,.95); head.add(hd);
  for (const sx of [-1,1]) head.add(mesh(S(.09), SKIN, sx*.5, -.03, 0));
  const hair = mesh(new THREE.SphereGeometry(.53,48,24,0,Math.PI*2,0,Math.PI*.42), HR, 0, .1, -.04); hair.rotation.x=.72; head.add(hair);
  if (P.style==="short") head.add(mesh(S(.17), HR, .12, .43, .16)).scale.set(1.6,.55,1);
  if (P.style==="side") { const sp=mesh(S(.2), HR, -.18, .4, .18); sp.scale.set(1.5,.45,1); head.add(sp); }
  if (P.style==="bob") { for (const sx of [-1,1]){ const h=mesh(new THREE.CapsuleGeometry(.17,.42,8,16), HR, sx*.47, -.08, -.04); h.rotation.z = sx*.12; head.add(h); }
                         const fr=mesh(S(.24), HR, .14, .38, .2); fr.scale.set(1.7,.5,1); head.add(fr); }
  const fc = face(head, -.04, .44, .82, {glasses:!!P.glasses});
  for (const sx of [-1,1]){ const b=mesh(new THREE.CapsuleGeometry(.028,.13,6,10), HR, sx*.22, .22, .45); b.rotation.z=Math.PI/2+sx*.15; head.add(b); fc["brow"+(sx<0?"L":"R")]=b; }
  if (P.style==="bob") for (const sx of [-1,1]) head.add(mesh(new THREE.CapsuleGeometry(.012,.06,4,8), INK, sx*.33, .11, .44)).rotation.z = sx*.9;
  // arms: free one gestures, the other holds the branded mic
  const armL = arm(bob,-1,-.58,1.22,0,SUIT,.42,SKIN), armR = arm(bob,1,.58,1.22,0,SUIT,.42,SKIN);
  armR.userData.rest = .55; armR.userData.restX = -1.05;
  const mic = new THREE.Group(); mic.position.set(0,-.53,0); mic.rotation.x = 1.3; armR.add(mic);
  mic.add(mesh(new THREE.CylinderGeometry(.04,.05,.32,16), DARK, 0, .1, 0));
  mic.add(mesh(S(.085,20,16), M(0x8b93a7,{metalness:.6,roughness:.35}), 0, .3, 0));
  mic.add(mesh(new RoundedBoxGeometry(.13,.09,.13,2,.02), M(0x00ff88), 0, .17, 0));
  const ic = icon(kind, col); ic.position.set(.78, 2.05, .1); ic.scale.setScalar(1.0); bob.add(ic); extra.icon = ic;
  return {root, bob, fc, head, armL, armR, extra, kind};
}

// ---- motion helpers (pure functions of time)
const clamp = (x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const backOut = x=>{x=clamp(x); const c=1.7; return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2);};
const ease = x=>{x=clamp(x); return x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2;};
const pulse = (t,a,d)=> (t<a||t>a+d)?0:Math.sin(Math.PI*(t-a)/d);
function amp(win, t){ const T=win.talk; if(!T||!T.length) return 0; const dt=T.length>1?(T[1][0]-T[0][0]):.066;
  const i=Math.round((t-T[0][0])/dt); return (i<0||i>=T.length)?0:T[i][1]; }

const chars = D.windows.map(w=>{ const c=build(w.char, w.color||D.accent, w.anchor||"A"); c.win=w; c.root.visible=false; scene.add(c.root); return c; });

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
    if(mood==="up"){ const pre=pulse(k,0,.14), air=pulse(k,.12,.5), post=pulse(k,.6,.22); sy+=-pre*.18+air*.08-post*.15; sx+=pre*.12+post*.1; y+=air*.35; }
    else { const d=ease(k/.35)*(1-ease((k-1.0)/.35)); sy-=d*.1; y-=d*.06; rz+=d*.08; }
  }
  b.position.y=y; b.scale.set(sx,sy,sx); b.rotation.z=rz + Math.sin(t*1.3)*.035;
  b.rotation.y = (w.look||0)*.3 + Math.sin(t*.8)*.12;     // turn to show the 3D form
  // arms: rest + gestures
  let aL=c.armL.userData.rest, aR=c.armR.userData.rest, xL=0, xR=c.armR.userData.restX||0;
  for (const [gt,kind] of (w.gest||[])){
    const k=t-gt; if(k<0||k>1.6) continue; const e=ease(k/.25)*(1-ease((k-1.25)/.3));
    if(kind==="wave"){ aL = aL + e*(-2.5-aL) - e*Math.sin(k*14)*.35; }
    else if(kind==="cheer"){ aR=aR+e*(2.7-aR); aL=aL+e*(-2.7-aL); }
    else if(kind==="present"||kind==="open"||kind==="split"){ aR=aR+e*(1.4-aR); aL=aL+e*(-1.4-aL); }
    else if(kind==="shrug"){ aR=aR+e*(1.0-aR); aL=aL+e*(-1.0-aL); xL=xR=e*.5; }
    else if(kind==="ring"){ aL=aL+e*(-2.2-aL)-e*Math.sin(k*16)*.25; }
    else { aL=aL+e*(-1.6-aL); xL=-e*.4; }
  }
  for (const [mt,mood] of (w.moods||[])){ const k=t-mt; if(mood==="up"&&k>=0&&k<1.1){ const e=ease(k/.15)*(1-ease((k-.8)/.3)); aL=aL+e*(-2.6-aL);} }
  c.armL.rotation.set(xL,0,aL); c.armR.rotation.set(xR,0,aR);
  // face: blink, look, talk
  const bt=(t+w.seed*.37)%2.9, blink=bt<.12?Math.sin(Math.PI*bt/.12):0;
  for (const e of c.fc.lids) e.scale.y=1-blink*.92;
  c.fc.eyes.position.x=(w.look||0)*.06;
  const a=amp(w,t); c.fc.mouth.scale.set(1, .25+Math.min(1.5,a*10), 1);
  if(c.head){ c.head.rotation.x = Math.sin(t*5.3)*Math.min(.06,a*.8) - .04; c.head.rotation.z = Math.sin(t*.9)*.05;
    const br = .22 + Math.min(.04, a*.4); if(c.fc.browL){ c.fc.browL.position.y=br; c.fc.browR.position.y=br; } }
  // character extras
  const X=c.extra;
  if(X.icon){ X.icon.position.y=2.05+Math.sin(t*2.2)*.06; X.icon.rotation.y=Math.sin(t*1.1)*.6; }
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
