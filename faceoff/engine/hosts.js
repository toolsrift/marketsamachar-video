/* ======================= HOSTS: original flat-vector presenters ======================= */
// Each host is drawn in a 400×560 box. Lip-sync comes from the voice loudness envelope (V.env), sampled per frame.
const CAST={
 a:{skin:'#B57E57',shade:'#9A6744',hair:'#1E1714',cloth:'#1F3A6B',lapel:'#172C52',accent:'var(--a)',style:'blazer'},
 b:{skin:'#C48D63',shade:'#A8734D',hair:'#231915',cloth:'#9C5A1C',lapel:'#7E4615',accent:'var(--b)',style:'kurta',glasses:true},
 n:{skin:'#A9734D',shade:'#8E5D3B',hair:'#191210',cloth:'#145C55',lapel:'#0F4842',accent:'var(--g)',style:'moderator'},
 c:{skin:'#9E6A47',shade:'#84563A',hair:'#16100D',cloth:'#4F2A74',lapel:'#3C1F5A',accent:'var(--c)',style:'sweater',beard:true}};
const HL={};function hostSVG(k,id,L){const c=CAST[k];L=L??(k==='b'||k==='c');HL[id]=L;
 const hair={a:`<path d="M110 214 C104 140 150 106 204 108 C258 110 298 146 290 212 C282 184 268 168 246 160 C214 176 168 176 134 166 C120 178 114 194 110 214 Z" fill="${c.hair}"/>`,
  b:`<path d="M114 202 C120 140 170 116 214 118 C250 122 282 142 290 194 C262 162 224 152 190 160 C160 170 134 188 114 202 Z" fill="${c.hair}"/>`,
  n:`<path d="M112 206 C108 142 154 112 204 112 C256 112 296 146 288 206 C276 168 246 148 200 148 C156 148 126 168 112 206 Z" fill="${c.hair}"/>`,
  c:`<path d="M108 216 C100 136 152 100 212 104 C268 108 300 150 292 214 C286 186 270 170 252 164 C230 150 190 148 160 158 C134 168 116 188 108 216 Z" fill="${c.hair}"/><path d="M150 132 C176 114 222 112 252 128" stroke="#2C211B" stroke-width="5" fill="none" opacity=".5"/>`}[k];
 const back={a:'',c:'',b:`<path d="M102 222 C94 120 160 94 206 96 C266 98 312 140 300 244 C304 304 318 380 302 424 L98 424 C82 380 96 304 102 222 Z" fill="${c.hair}"/>`,
  n:`<circle cx="200" cy="104" r="42" fill="${c.hair}"/>`}[k];
 const outfit={blazer:`<path d="M160 398 L200 466 L240 398 Z" fill="#F2F4F8"/><path d="M192 406 L208 406 L214 496 L200 516 L186 496 Z" fill="${c.accent}"/>
   <path d="M150 398 L200 478 L174 560 L112 560 L118 424 Z" fill="${c.lapel}"/><path d="M250 398 L200 478 L226 560 L288 560 L282 424 Z" fill="${c.lapel}"/>`,
  kurta:`<path d="M162 400 Q200 452 238 400" fill="none" stroke="#E8C77A" stroke-width="5"/>${[0,1,2,3,4,5,6].map(i=>`<circle cx="${170+i*10}" cy="${416+Math.sin(i/6*Math.PI)*24}" r="3" fill="#E8C77A"/>`).join('')}
   <path d="M120 430 Q200 470 280 430" fill="none" stroke="${c.lapel}" stroke-width="10" opacity=".6"/>`,
  sweater:`<path d="M168 398 L186 420 L200 404 L214 420 L232 398" fill="#F2F4F8"/><path d="M160 400 Q200 432 240 400" fill="none" stroke="${c.lapel}" stroke-width="12"/><path d="M120 470 L120 560 M280 470 L280 560" stroke="${c.lapel}" stroke-width="6" opacity=".6"/>`,
  moderator:`<path d="M168 400 Q200 430 232 400 L236 560 L164 560 Z" fill="#EEF0F2"/><path d="M150 398 L196 470 L170 560 L112 560 L118 424 Z" fill="${c.lapel}"/><path d="M250 398 L204 470 L230 560 L288 560 L282 424 Z" fill="${c.lapel}"/><circle cx="246" cy="470" r="7" fill="var(--g)"/>`}[c.style];
 return `<svg viewBox="0 0 400 560" width="400" height="560" style="overflow:visible">
  <g id="${id}_body" style="transform-origin:200px 560px">${back}
   <path d="M172 330 L228 330 L232 404 C214 418 186 418 168 404 Z" fill="${c.shade}"/>
   <path d="M30 560 C34 470 80 412 150 398 L250 398 C320 412 366 470 370 560 Z" fill="${c.cloth}"/>${outfit}</g>
  <g id="${id}_head" style="transform-origin:200px 330px">
   <ellipse cx="114" cy="238" rx="14" ry="22" fill="${c.shade}"/><ellipse cx="286" cy="238" rx="14" ry="22" fill="${c.shade}"/>
   ${k==='n'?`<circle cx="112" cy="262" r="5" fill="#E8C77A"/><circle cx="288" cy="262" r="5" fill="#E8C77A"/>`:''}
   <path d="M114 222 C114 302 160 340 200 340 C240 340 286 302 286 222 C286 160 250 128 200 128 C150 128 114 160 114 222 Z" fill="${c.skin}"/>
   <circle cx="152" cy="268" r="16" fill="#E06B5A" opacity=".13"/><circle cx="248" cy="268" r="16" fill="#E06B5A" opacity=".13"/>
   ${hair}${c.beard?`<path d="M118 246 C122 312 160 346 200 346 C240 346 278 312 282 246 C272 292 242 318 200 320 C158 318 128 292 118 246 Z" fill="${c.hair}" opacity=".92"/><path d="M178 282 Q200 274 222 282 Q200 290 178 282 Z" fill="${c.hair}"/>`:''}
   <g id="${id}_brow"><path d="M146 194 Q166 184 186 192" stroke="${c.hair}" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M214 192 Q234 184 254 194" stroke="${c.hair}" stroke-width="6" fill="none" stroke-linecap="round"/></g>
   <g id="${id}_eyes" style="transform-origin:200px 222px"><ellipse cx="166" cy="222" rx="14" ry="10" fill="#FBFBF8"/><ellipse cx="234" cy="222" rx="14" ry="10" fill="#FBFBF8"/>
    <g id="${id}_pup"><circle cx="166" cy="223" r="6.5" fill="#2A1D16"/><circle cx="234" cy="223" r="6.5" fill="#2A1D16"/><circle cx="168" cy="221" r="2" fill="#fff"/><circle cx="236" cy="221" r="2" fill="#fff"/></g></g>
   ${c.glasses?`<g stroke="#2A2A2A" stroke-width="4" fill="rgba(255,255,255,.07)"><rect x="143" y="205" width="46" height="34" rx="11"/><rect x="211" y="205" width="46" height="34" rx="11"/><path d="M189 220 L211 220" fill="none"/></g>`:''}
   <path d="M198 238 Q191 262 200 268 Q206 270 211 266" stroke="${c.shade}" stroke-width="4" fill="none" stroke-linecap="round"/>
   <g id="${id}_mouth"><path id="${id}_lip" d="M182 294 Q200 302 218 294" stroke="#6B2E2A" stroke-width="5" fill="none" stroke-linecap="round"/>
    <ellipse id="${id}_mo" cx="200" cy="296" rx="16" ry="0" fill="#4A1A1A"/><ellipse id="${id}_te" cx="200" cy="290" rx="11" ry="0" fill="#F6F2EC"/><ellipse id="${id}_to" cx="200" cy="302" rx="9" ry="0" fill="#C4566A"/></g></g>
  <g id="${id}_arm" style="transform-origin:${L?110:290}px 560px;opacity:0"><path d="M${L?110:290} 560 L${L?120:280} 420" stroke="${c.cloth}" stroke-width="50" stroke-linecap="round"/>
   <circle cx="${L?120:280}" cy="402" r="28" fill="${c.skin}"/><path d="M${L?136:264} 384 l${L?14:-14} -26" stroke="${c.skin}" stroke-width="14" stroke-linecap="round"/></g></svg>`}
const hash=(s,n)=>{let h=0;for(const ch of s)h=(h*31+ch.charCodeAt(0))%9973;return (h*n*7919)%1000/1000};
function blinkAt(k,t){const per=3.6+hash(k,1)*1.6,ph=(t+hash(k,2)*3)%per;return ph<.13?Math.sin(ph/.13*Math.PI):0}
function animHost(id,k,t,{speaking,lv,look,gesture,gt}){
 const bl=blinkAt(id,t);st(id+'_eyes',{transform:`scaleY(${1-.9*bl})`});
 st(id+'_body',{transform:`scaleY(${1+.008*Math.sin(t*1.7+hash(id,3)*6)})`});
 const sway=speaking?Math.sin(t*2.2)*2.2+lv*3:Math.sin(t*.7+hash(id,4)*6)*1.2,nod=speaking?lv*5:Math.max(0,Math.sin(t*1.1+hash(id,5)*6))*1.5;
 st(id+'_head',{transform:`translate(${look*7}px,${nod}px) rotate(${sway}deg)`});
 const pe=$(id+'_pup');if(pe)pe.setAttribute('transform',`translate(${look*4},0)`);
 const browUp=(speaking&&gt<.7?6*(1-gt/.7):0)+(gesture==='surprise'?10:0);st(id+'_brow',{transform:`translateY(${-browUp}px)`});
 const o=speaking?lv:0,mo=$(id+'_mo');if(mo){mo.setAttribute('ry',(o*15).toFixed(1));mo.setAttribute('rx',(15+o*7).toFixed(1));$(id+'_te').setAttribute('ry',(o>.25?3.2:0));$(id+'_to').setAttribute('ry',(o*5).toFixed(1));$(id+'_lip').style.opacity=o>.08?0:1}
 const arm=$(id+'_arm');if(arm){const on=speaking&&(gesture==='point'||gesture==='raise')?eo(cl(gt/.4))*(1-cl((gt-2.6)/.4)):0;
  const dir=HL[id]?1:-1;st(arm,{opacity:on?1:0,transform:`rotate(${dir*(gesture==='point'?-28:-6)*on+dir*Math.sin(t*3)*2*on}deg) translateY(${(1-on)*140}px)`})}}
// level of the voice for a host at local scene time t (smoothed)
function hostState(S,t,who){let best=null;for(const c of S.clips||[]){if(c[3]===who&&t>=c[1]-.05&&t<=c[1]+c[2]+.05){best=c;break}}
 if(!best)return {speaking:false,lv:0,gt:0,gesture:null};const env=(V.env||{})[best[0]]||[],f=(t-best[1])*30,i=Math.floor(f),a=env[i]||0,b=env[i+1]||0;
 const lv=cl((a+(b-a)*(f-i))*1.25);return {speaking:true,lv:lv<.07?0:lv,gt:t-best[1],gesture:best[4]||null}}
function currentSpeaker(S,t){for(const c of S.clips||[]){if(t>=c[1]-.1&&t<=c[1]+c[2]+.25)return c[3]}return null}

// full-screen desk cutaway: the hosts talk, the camera pushes in on whoever speaks. Charts never share this frame.
E.desk=(sp,S)=>{const i=S._i,who=sp.hosts||(V.format==='panel'?['a','b','c','n']:TALK.includes(V.format)?['a','n','b']:['n']),solo=who.length===1,four=who.length>=4;
 const XS=solo?[960]:four?[260,740,1180,1660]:[430,960,1490],X={};who.forEach((k,j)=>X[k]=XS[j]);const back=(typeof PK!=='undefined'&&PK&&PK.backdrop)?PK.backdrop(i):'';
 let h=`<div class="ab" id="dk_w${i}" style="left:0;top:0;width:1920px;height:1080px;transform-origin:0 0">${back}`;
 who.forEach(k=>{const H=V.hosts[k]||{},s=k==='n'&&!solo&&!four?.92:four?.9:1;h+=`<div class="ab" id="dk_h${i}${k}" style="left:${X[k]-200*s}px;top:${300+(1-s)*560}px;width:${400*s}px;height:${560*s}px"><div style="transform:scale(${s});transform-origin:0 0">${hostSVG(k,`h${i}${k}`,X[k]>960)}</div></div>`});
 h+=`<div class="ab" style="left:-40px;top:820px;width:2000px;height:300px;background:linear-gradient(var(--card),color-mix(in srgb,var(--card) 80%,var(--bg)));border-top:4px solid color-mix(in srgb,var(--g) 55%,transparent);box-shadow:0 -20px 60px rgba(0,0,0,.25)"></div>
  <div class="ab" style="left:810px;top:858px;width:300px;height:64px;display:${four?'none':'flex'};align-items:center;justify-content:center;gap:12px;border-radius:12px;background:var(--bg);border:2px solid var(--cardb)"><img src="../../assets/logo-icon.png" style="width:44px;height:44px;border-radius:9px"><span class="wm" style="font-size:22px"><span class="m">MARKET</span> <span class="s">SAMACHAR</span></span></div>`;
 who.filter(k=>!(k==='n'&&!solo&&!four)).forEach(k=>{const H=V.hosts[k]||{},col=H.color?SCOL(H.color):k==='n'?'var(--gt)':SCOL(k);
  h+=`<div class="ab" style="left:${X[k]-(four?150:170)}px;top:${solo?950:858}px;width:${four?300:340}px;height:70px;border-radius:10px;background:var(--bg);border:3px solid ${col};display:flex;flex-direction:column;align-items:center;justify-content:center"><div style="font-weight:800;font-size:26px;line-height:1">${H.name||''}</div><div style="font-family:Mono;font-weight:700;font-size:15px;letter-spacing:2px;color:${col};text-transform:uppercase;margin-top:4px">${H.role||''}</div></div>`});
 h+='</div>';
 return {html:h,anim(t,b){let sp2=currentSpeaker(S,t);
  // camera: push in on the speaking host (debate); slow push for solo
  const tgt=k=>k&&(k!=='n'||four)&&!solo&&X[k]!=null?{x:X[k],y:440,s:four?1.4:1.3}:{x:960,y:540,s:solo?1.06+.04*cl(t/S.dur):1.0};
  const segs=(S.clips||[]).map(c=>[c[1]-.25,c[3]]);let cur=tgt(null),prev=cur,ct=0;for(const [tt,k] of segs){if(t>=tt){const nt=tgt(k);if(nt.x!==cur.x||nt.s!==cur.s){prev=cur;cur=nt;ct=tt}}}
  const p=eio(P(t,ct,.7)),zs=prev.s+(cur.s-prev.s)*p,zx=prev.x+(cur.x-prev.x)*p,zy=prev.y+(cur.y-prev.y)*p,cx=Math.min(Math.max(zx,960/zs),1920-960/zs),cy=Math.min(Math.max(zy,540/zs),1080-540/zs);
  st('dk_w'+i,{transform:`translate(${960-cx*zs}px,${540-cy*zs}px) scale(${zs})`});
  who.forEach(k=>{const s=hostState(S,t,k);const look=sp2&&sp2!==k?(X[sp2]>X[k]?1:-1):0;animHost(`h${i}${k}`,k,t+({a:0,b:1.3,c:.7,n:2.1})[k],{...s,look})})}}};
