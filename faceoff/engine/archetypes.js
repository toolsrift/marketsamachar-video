/* ======================= PHASE 3: EPISODE SCENE TYPES ======================= */
const E={};const SCOL=s=>s==='a'?'var(--a)':s==='b'?'var(--b)':s==='g'?'var(--gt)':s==='dn'?'var(--dn)':s==='up'?'var(--up)':'var(--ink)';
const NUMRE=/^([^\d−-]*?)(-|−)?([\d,]*\.?\d+)(.*)$/;
function countStr(id,t,s,d,str){const e=$(id);if(!e)return;const m=String(str).match(NUMRE);if(!m){e.textContent=str;return}
 const raw=m[3].replace(/,/g,''),dec=(raw.split('.')[1]||'').length,v=parseFloat(raw)*eo(P(t,s,d));
 let txt=dec?v.toFixed(dec):String(Math.round(v));if(m[3].includes(','))txt=Number(txt).toLocaleString('en-IN',{minimumFractionDigits:dec,maximumFractionDigits:dec});
 e.textContent=m[1]+(m[2]||'')+txt+m[4]}
const BT=(b,k)=>b.length?b[Math.min(k||0,b.length-1)]:0;
const NM=c=>c==='a'?(A.say||A.tick):(B.say||B.tick);

// one or two giant numbers
E.hero=(sp,S)=>{const it=sp.items,two=it.length>1;let h='';
 it.forEach((x,k)=>{const L=two?(k?990:110):110,W=two?820:1700;
  h+=`<div class="ab" id="hr_${k}" style="left:${L}px;top:${two?290:250}px;width:${W}px;text-align:center;opacity:0">
   ${x.side?`<div class="tk" style="font-size:${two?52:46}px;color:${SCOL(x.side)}">${NM(x.side)}</div>`:''}
   <div class="num" id="hr_v${k}" style="font-size:${two?180:250}px;line-height:1.05;color:${SCOL(x.color||x.side)}">${x.value}</div>
   <div style="font-weight:800;font-size:${two?36:44}px;margin-top:10px">${x.label||''}</div>
   ${x.sub?`<div class="cs" style="font-weight:600;font-size:28px;margin-top:8px">${x.sub}</div>`:''}</div>`});
 if(two)h+=`<div class="ab tk" id="hr_vs" style="left:910px;width:100px;top:430px;text-align:center;font-size:44px;color:var(--sub);opacity:0">vs</div>`;
 if(sp.caption)h+=`<div class="ab" id="hr_c" style="left:160px;width:1600px;top:${two?770:780}px;text-align:center;font-family:var(--fh);font-size:50px;line-height:1.2;opacity:0"><span class="hl">${sp.caption}</span></div>`;
 return {html:h,anim(t,b){it.forEach((x,k)=>{const s=BT(b,x.beat)+.1;pop('hr_'+k,t,s,.5,.6);countStr('hr_v'+k,t,s,1.1,x.value)});
  if(two)pop('hr_vs',t,BT(b,it[1].beat),.4,.5);if(sp.caption)rise('hr_c',t,BT(b,sp.captionBeat)+.2,.5,30)}}};

// kinetic typography — words land one by one, key words highlighted
E.kinetic=(sp,S)=>{const L=sp.lines,tot=L.length;let h=`<div class="ab" style="left:150px;width:1620px;top:${sp.top||120}px;height:${sp.h||860}px;display:flex;flex-direction:column;justify-content:center;gap:${sp.gap||28}px;text-align:${sp.align||'center'}">`;
 const clean=w=>w.replace(/[^\w₹%.−-]/g,'').toLowerCase();
 L.forEach((ln,k)=>{const sz=ln.size||(ln.sub?38:tot>2?84:104),words=ln.text.split(' ');
  h+=`<div style="${ln.sub?'font-family:Inter;font-weight:700;color:var(--sub);':'font-family:var(--fh);'}font-size:${sz}px;line-height:1.14">`+words.map((w,j)=>{const em=(ln.emph||[]).some(e=>clean(w)===e.toLowerCase());
   return `<span id="kw_${S._i}_${k}_${j}" style="display:inline-block;opacity:0;${em?`color:${SCOL(ln.ec||'g')};`:''}">${em?`<span class="hl">${w}</span>`:w}</span>`}).join(' ')+`</div>`});
 h+='</div>';
 return {html:h,anim(t,b){L.forEach((ln,k)=>{const s=BT(b,ln.beat)+.05,n=ln.text.split(' ').length,step=ln.step||Math.min(.12,1.5/n);
  for(let j=0;j<n;j++){const p=eo(P(t,s+j*step,.35));st(`kw_${S._i}_${k}_${j}`,{opacity:p,transform:`translateY(${(1-p)*36}px) scale(${.92+.08*p})`})}})}}};

// permanent split-screen duel with metric rows
E.duel=(sp,S)=>{const R=sp.rows;const fmt=(v,f)=>f==='pct'?v.toFixed(Math.abs(v)<10?2:1)+'%':f==='x'?v.toFixed(1)+'×':f==='inr'?'₹'+inr(v):f==='L'?'₹'+(v/1e5).toFixed(2)+' L Cr':f==='int'?String(Math.round(v)):String(v);
 let h=`<div class="ab" style="left:0;top:0;width:960px;height:1080px;background:linear-gradient(90deg,color-mix(in srgb,var(--a) 16%,transparent),transparent 85%)"></div><div class="ab" style="left:960px;top:0;width:960px;height:1080px;background:linear-gradient(270deg,color-mix(in srgb,var(--b) 16%,transparent),transparent 85%)"></div>
  <div class="ab" style="left:958px;top:250px;width:4px;height:640px;background:var(--grid)"></div>
  <div class="ab" id="du_ha${S._i}" style="left:110px;width:760px;top:250px;text-align:center;opacity:0"><div class="tk" style="font-size:80px;color:var(--a)">${A.tick}</div><div class="cs" style="font-weight:700;font-size:26px">${A.name}</div></div>
  <div class="ab" id="du_hb${S._i}" style="left:1050px;width:760px;top:250px;text-align:center;opacity:0"><div class="tk" style="font-size:80px;color:var(--b)">${B.tick}</div><div class="cs" style="font-weight:700;font-size:26px">${B.name}</div></div>`;
 const y0=440,dy=Math.min(130,460/R.length);
 R.forEach((r,k)=>{const y=y0+k*dy,mx=Math.max(Math.abs(r.a),Math.abs(r.b))||1,w=r.better==='low'?(r.a<r.b?'a':'b'):r.better==='high'?(r.a>r.b?'a':'b'):null,id=`du${S._i}_`;
  h+=`<div class="ab" id="${id}r${k}" style="left:0;top:${y}px;width:1920px;height:${dy}px;opacity:0">
   <div style="position:absolute;left:820px;width:280px;top:14px;text-align:center"><span class="chip" style="font-size:23px;padding:8px 18px;background:var(--card);border:2px solid var(--cardb)">${r.label}</span></div>
   <div class="num" style="position:absolute;right:${1920-790}px;top:0;font-size:60px;color:${w==='a'?'var(--gt)':'var(--ink)'};white-space:nowrap">${w==='a'?'✓ ':''}${fmt(r.a,r.f)}</div>
   <div class="num" style="position:absolute;left:1130px;top:0;font-size:60px;color:${w==='b'?'var(--gt)':'var(--ink)'};white-space:nowrap">${fmt(r.b,r.f)}${w==='b'?' ✓':''}</div>
   <div id="${id}ba${k}" data-w="${Math.abs(r.a)/mx*560}" style="position:absolute;right:${1920-790}px;top:${dy-36}px;height:16px;width:0;border-radius:8px;background:var(--a)"></div>
   <div id="${id}bb${k}" data-w="${Math.abs(r.b)/mx*560}" style="position:absolute;left:1130px;top:${dy-36}px;height:16px;width:0;border-radius:8px;background:var(--b)"></div></div>`});
 return {html:h,anim(t,b){rise('du_ha'+S._i,t,.4,.5);rise('du_hb'+S._i,t,.55,.5);R.forEach((r,k)=>{const s=BT(b,r.beat),id=`du${S._i}_`;rise(id+'r'+k,t,s,.45,25);const p=eio(P(t,s+.2,.8));
  ['a','b'].forEach(c=>{const e=$(id+'b'+c+k);if(e)e.style.width=(+e.dataset.w*p)+'px'})})}}};

// big chart; the camera flies to each callout
E.chartzoom=(sp,S)=>{const xs=D[sp.x||'years10'],va0=A[sp.series],vb0=B[sp.series],ix=sp.index,id=`cz${S._i}`;
 const va=ix?va0.map(x=>x/va0[0]*100):va0,vb=ix?vb0.map(x=>x/vb0[0]*100):vb0;
 const fmt=sp.fmt==='pct'?(v=>Math.round(v)+'%'):sp.fmt==='L'?(v=>(v/1e5).toFixed(2)):sp.fmt==='k'?(v=>(v/1e3).toFixed(1)):(v=>String(Math.round(v)));
 const x0=240,x1=1700,y0=870,y1=360,n=xs.length,all=[...va,...vb],lo=sp.zero===false?Math.floor(Math.min(...all)*0.8):0,hi=Math.max(...all)*1.1,gw=(x1-x0)/(n-1),X=i=>x0+i*gw,Y=v=>y0-(v-lo)/(hi-lo)*(y0-y1);
 const pth=arr=>arr.map((v,i)=>(i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1)).join(' ');
 let g='';for(let k=0;k<=4;k++){const v=lo+(hi-lo)/4*k;g+=`<line x1="${x0}" x2="${x1}" y1="${Y(v)}" y2="${Y(v)}" style="stroke:var(--grid);stroke-width:2"/><text x="${x0-22}" y="${Y(v)+8}" text-anchor="end" style="fill:var(--sub);font-size:22px">${fmt(v)}</text>`}
 xs.forEach((l,i)=>{g+=`<text x="${X(i)}" y="${y0+44}" text-anchor="middle" style="fill:var(--sub);font-size:22px;font-family:Mono">${l}</text>`});
 const CO=sp.callouts||[];
 let h=`<div class="ab" id="${id}w" style="left:0;top:0;width:1920px;height:1080px;transform-origin:0 0">
  <div class="ab lbl" style="left:110px;top:262px">${sp.unit||''}</div>${D.note10&&(sp.x||'years10')==='years10'&&!sp.noNote?`<div class="ab" style="right:110px;top:258px;font-weight:700;font-size:21px;color:var(--sub);max-width:860px;text-align:right">ⓘ ${D.note10}</div>`:''}
  <div class="ab" style="left:${x0}px;top:300px;display:flex;gap:30px"><span class="tk" style="font-size:32px;color:var(--a)">● ${A.tick}</span><span class="tk" style="font-size:32px;color:var(--b)">● ${B.tick}</span></div>
  <svg class="ab" style="left:0;top:0" width="1920" height="1080"><defs><clipPath id="${id}cp"><rect id="${id}cr" x="0" y="0" width="0" height="1080"/></clipPath></defs>${g}
   <g clip-path="url(#${id}cp)">${[[va,'a'],[vb,'b']].map(([arr,c])=>`<path d="${pth(arr)}" style="fill:none;stroke:var(--${c});stroke-width:8;stroke-linejoin:round;stroke-linecap:round"/>${arr.map((v,i)=>`<circle cx="${X(i)}" cy="${Y(v)}" r="9" style="fill:var(--bg);stroke:var(--${c});stroke-width:5"/>`).join('')}`).join('')}</g></svg>`;
 CO.forEach((c,k)=>{const arr=c.who==='a'?va:vb,px=X(c.i),py=Y(arr[c.i]),left=px>1250;c._p=[px,py];const up=c.below?false:py>470;
  h+=`<div class="ab" id="${id}c${k}" style="left:${left?px-420:px+34}px;top:${up?py-150:py+34}px;width:380px;opacity:0"><div class="card" style="padding:14px 18px;border-color:${SCOL(c.who)};border-width:3px"><div class="num" style="font-size:36px;color:${SCOL(c.who)}">${c.big||fmt(arr[c.i])}</div><div style="font-weight:700;font-size:21px;line-height:1.25">${c.text}</div></div></div>
  <div class="ab" id="${id}d${k}" style="left:${px-24}px;top:${py-24}px;width:48px;height:48px;border-radius:50%;border:5px solid ${SCOL(c.who)};opacity:0"></div>`});
 h+='</div>';
 return {html:h,anim(t,b){const s0=BT(b,sp.drawBeat||0)+.2,e=$(id+'cr');if(e)e.setAttribute('width',(x0+(x1-x0)*eio(P(t,s0,1.8))+30).toFixed(0));
  const ks=[[0,null]];CO.forEach((c,k)=>ks.push([BT(b,c.beat),k]));ks.push([sp.outBeat!=null?BT(b,sp.outBeat):S.dur-1.7,null]);
  let cur={x:960,y:540,s:1,t:0},prev=cur;
  for(const [kt,k] of ks){if(t>=kt){prev=cur;cur=k==null?{x:960,y:540,s:1,t:kt}:{x:CO[k]._p[0],y:CO[k]._p[1],s:sp.zoom||1.45,t:kt}}}
  const p=eio(P(t,cur.t,.9)),zs=prev.s+(cur.s-prev.s)*p,zx=prev.x+(cur.x-prev.x)*p,zy=prev.y+(cur.y-prev.y)*p;
  const cx=Math.min(Math.max(zx,960/zs),1920-960/zs),cy=Math.min(Math.max(zy,540/zs),1080-540/zs);
  st(id+'w',{transform:`translate(${960-cx*zs}px,${540-cy*zs}px) scale(${zs})`});
  const fade=1-cl((zs-1)/.3),te=$('tt'+S._i);if(te)te.style.opacity=(parseFloat(te.style.opacity)||0)*fade;st('tr'+S._i,{opacity:fade});
  CO.forEach((c,k)=>{pop(id+'d'+k,t,BT(b,c.beat)+.35,.35,.3);rise(id+'c'+k,t,BT(b,c.beat)+.5,.4,20)})}}};

// ₹1 lakh invested N years ago
E.invest=(sp,S)=>{const Y=sp.years||5,amt=sp.amount||100000,va=amt*Math.pow(1+A.ret[Y+'Y']/100,Y),vb=amt*Math.pow(1+B.ret[Y+'Y']/100,Y),mx=Math.max(va,vb,amt)*1.05;
 const L=v=>'₹'+(v/1e5).toFixed(2)+' L';
 let h=`<div class="ab" id="iv_q${S._i}" style="left:110px;width:1700px;top:250px;text-align:center;font-family:var(--fh);font-size:60px;opacity:0">${sp.title||`₹1 lakh invested ${Y} years ago`}</div>`;
 [[A,'a',va,600],[B,'b',vb,1320]].forEach(([S2,c,v,cx])=>{const ch=(v/amt-1)*100;S['_iv'+c]=v;
  h+=`<div class="ab" id="iv_${c}${S._i}" style="left:${cx-300}px;width:600px;top:350px;height:580px;opacity:0">
   <div style="text-align:center"><span class="tk" style="font-size:48px;color:var(--${c})">${S2.tick}</span></div>
   <div style="position:absolute;left:190px;width:220px;bottom:130px;height:370px;display:flex;align-items:flex-end"><div id="iv_b${c}${S._i}" data-h0="${amt/mx*370}" data-h1="${v/mx*370}" style="width:220px;height:${amt/mx*370}px;background:repeating-linear-gradient(0deg,var(--${c}) 0 28px,color-mix(in srgb,var(--${c}) 65%,var(--bg)) 28px 32px);border-radius:10px 10px 4px 4px"></div></div>
   <div style="position:absolute;left:0;width:600px;bottom:50px;text-align:center;white-space:nowrap"><span class="num" id="iv_v${c}${S._i}" style="font-size:64px">${L(amt)}</span> <span class="num" id="iv_p${c}${S._i}" style="font-size:36px;color:var(--${ch>=0?'up':'dn'});opacity:0">${ch>=0?'+':'−'}${Math.abs(ch).toFixed(0)}%</span></div></div>`});
 h+=`<div class="ab cs" id="iv_n${S._i}" style="left:110px;width:1700px;top:930px;text-align:center;font-weight:700;font-size:21px;opacity:0">From each stock's ${Y}-year share-price CAGR · excludes dividends · past returns don't predict future returns</div>`;
 return {html:h,anim(t,b){const i=S._i;rise('iv_q'+i,t,BT(b,0),.5,30);rise('iv_a'+i,t,BT(b,0)+.3,.5);rise('iv_b'+i,t,BT(b,0)+.45,.5);st('iv_n'+i,{opacity:P(t,BT(b,0)+.8,.4)});
  [['a',BT(b,sp.beatA??1)],['b',BT(b,sp.beatB??2)]].forEach(([c,s])=>{const p=eio(P(t,s+.2,1.5)),e=$('iv_b'+c+i);if(e)e.style.height=(+e.dataset.h0+(e.dataset.h1-e.dataset.h0)*p)+'px';
   $('iv_v'+c+i).textContent=L(amt+(S['_iv'+c]-amt)*p);st('iv_p'+c+i,{opacity:P(t,s+1.6,.3)})})}}};

// myth vs fact
E.mythfact=(sp,S)=>{const vd=sp.verdict||'FALSE',vc=vd==='TRUE'?'var(--up)':vd==='FALSE'?'var(--dn)':'var(--b)',i=S._i;
 return {html:`<div class="ab card" id="mf_c${i}" style="left:240px;top:250px;width:1440px;padding:44px 56px;opacity:0">
   <div class="lbl" style="font-size:26px">Myth</div><div style="font-family:var(--fh);font-size:62px;line-height:1.14;margin-top:10px;position:relative">“${sp.myth}”${vd==='FALSE'?`<div id="mf_x${i}" style="position:absolute;left:0;top:52%;height:8px;width:0;background:${vc};border-radius:4px"></div>`:''}</div>
   <div id="mf_f${i}" style="opacity:0;margin-top:34px;border-top:3px solid var(--grid);padding-top:26px"><div class="lbl" style="font-size:26px;color:${vc}">Fact</div><div style="font-weight:800;font-size:40px;line-height:1.28;margin-top:8px">${sp.fact}</div></div></div>
  <div class="stamp" id="mf_s${i}" style="right:170px;top:190px;border-color:${vc};color:${vc};font-size:62px">${vd}</div>`,
  anim(t,b){rise('mf_c'+i,t,BT(b,0),.5,40);const s=BT(b,sp.factBeat??1),p=P(t,s,.35);st('mf_s'+i,{opacity:cl(p*4),transform:`rotate(-8deg) scale(${2.2-1.2*eo(p)})`});
   st('mf_x'+i,{width:eo(P(t,s+.1,.4))*100+'%'});rise('mf_f'+i,t,s+.4,.5,30)}}};

// quiz with countdown
E.quiz=(sp,S)=>{const R=120,Cc=2*Math.PI*R,i=S._i;
 return {html:`<div class="ab" id="qz_q${i}" style="left:160px;width:1600px;top:240px;text-align:center;font-family:var(--fh);font-size:58px;line-height:1.15;opacity:0"><span class="lbl" style="display:block;font-size:26px;margin-bottom:14px;color:var(--gt)">Quick quiz · ${sp.n||''}</span>${sp.q}</div>
  ${[[A,'a',250],[B,'b',1070]].map(([S2,c,x])=>`<div class="ab card" id="qz_${c}${i}" style="left:${x}px;top:520px;width:600px;height:240px;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;border-width:4px">
   <div class="tk" style="font-size:80px;color:var(--${c})">${S2.tick}</div><div class="cs" style="font-weight:700;font-size:28px">${S2.name}</div>
   <div id="qz_k${c}${i}" class="ck" style="position:absolute;right:-24px;top:-24px;width:68px;height:68px;font-size:40px;opacity:0">✓</div></div>`).join('')}
  <div class="ab" id="qz_t${i}" style="left:${960-R-20}px;top:${640-R-20}px;width:${2*R+40}px;height:${2*R+40}px;opacity:0"><svg width="${2*R+40}" height="${2*R+40}"><circle cx="${R+20}" cy="${R+20}" r="${R}" style="fill:var(--bg);stroke:var(--grid);stroke-width:14"/><circle id="qz_tc${i}" cx="${R+20}" cy="${R+20}" r="${R}" transform="rotate(-90 ${R+20} ${R+20})" stroke-dasharray="${Cc}" stroke-dashoffset="0" style="fill:none;stroke:var(--g);stroke-width:14;stroke-linecap:round"/></svg>
   <div class="num" id="qz_n${i}" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:110px"></div></div>
  <div class="ab" id="qz_r${i}" style="left:160px;width:1600px;top:810px;text-align:center;font-weight:800;font-size:42px;line-height:1.25;opacity:0">${sp.reveal}</div>`,
 anim(t,b){rise('qz_q'+i,t,BT(b,0),.5,30);const cs=BT(b,sp.countBeat??1),cd=sp.count||3,rv=BT(b,sp.revealBeat??2),w=sp.answer,l=w==='a'?'b':'a';
  if(t<rv){pop('qz_a'+i,t,BT(b,0)+.6,.4,.7);pop('qz_b'+i,t,BT(b,0)+.8,.4,.7)}
  else{const pr=eo(P(t,rv,.4));st('qz_'+w+i,{opacity:1,transform:`scale(${1+.06*pr})`,borderColor:'var(--g)',boxShadow:'0 0 60px color-mix(in srgb,var(--g) 45%,transparent)'});st('qz_'+l+i,{opacity:1-.6*pr,transform:`scale(${1-.04*pr})`})}
  st('qz_t'+i,{opacity:t>=cs&&t<rv+.25?cl(P(t,cs,.2))*(1-P(t,rv,.25)):0,transform:`scale(${.8+.2*eo(P(t,cs,.3))})`});
  const left=cl(cd-(t-cs),0,cd);$('qz_n'+i).textContent=left>0?Math.ceil(left):'';$('qz_tc'+i).setAttribute('stroke-dashoffset',Cc*(1-left/cd));
  pop('qz_k'+w+i,t,rv+.1,.35,.2);rise('qz_r'+i,t,rv+.3,.45,25)}}};

// two coloured halves for the closing
E.split=(sp,S)=>{let h='';const i=S._i;[['a',A,0],['b',B,960]].forEach(([c,S2,x])=>{const q=sp[c];
  h+=`<div class="ab" id="sv_${c}${i}" style="left:${x}px;top:0;width:960px;height:1080px;background:color-mix(in srgb,var(--${c}) 14%,transparent);opacity:0"></div>
  <div class="ab" id="sv_t${c}${i}" style="left:${x+110}px;width:760px;top:240px;opacity:0"><div class="tk" style="font-size:70px;color:var(--${c})">${S2.tick}</div><div style="font-family:var(--fh);font-size:44px;margin-top:6px">${q.head}</div></div>
  ${q.rows.map((r,k)=>`<div class="ab" id="sv_${c}${k}_${i}" style="left:${x+110}px;width:780px;top:${420+k*84}px;display:flex;gap:18px;align-items:center;opacity:0"><span class="ck">✓</span><span style="font-weight:800;font-size:33px">${r}</span></div>`).join('')}`});
 if(sp.q)h+=`<div class="ab" id="sv_q${i}" style="left:110px;top:790px;width:1700px;height:140px;background:var(--g);color:var(--onG);display:flex;align-items:center;gap:30px;padding:0 50px;border-radius:var(--rad);opacity:0"><svg width="80" height="80" viewBox="0 0 24 24"><path d="M4 4h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-5 4v-4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z" fill="currentColor"/></svg><div><div style="font-family:var(--fh);font-size:50px;line-height:1">${sp.q}</div><div style="font-weight:800;font-size:26px;margin-top:8px">Not a buy or sell call</div></div></div>`;
 return {html:h,anim(t,b){['a','b'].forEach(c=>{const s=BT(b,sp[c].beat);st('sv_'+c+i,{opacity:P(t,s,.5)});rise('sv_t'+c+i,t,s+.1,.5,30);sp[c].rows.forEach((r,k)=>slide(`sv_${c}${k}_${i}`,t,s+.7+k*.6,.4,-30))});if(sp.q)pop('sv_q'+i,t,BT(b,sp.qBeat),.5,.7)}}};

E.classic=(sp,S)=>C[sp.key](sp.variant||0,S);
E.cta=(sp,S)=>C.cta(0,S);

// overlays: debate speaker pill, news-desk ticker
function speakerPill(S,t){const el=$('spk');if(V.format!=='debate'||!S.clips){el.style.opacity=0;return}
 let best=null,bo=0;for(const c of S.clips){const o=cl((t-(c[1]-.2))/.2)*(1-cl((t-(c[1]+c[2]+.15))/.3));if(o>bo){bo=o;best=c}}
 if(!best){el.style.opacity=0;return}
 const H=V.hosts[best[3]]||{},col=best[3]==='a'?'var(--a)':best[3]==='b'?'var(--b)':'var(--gt)',env=(V.env||{})[best[0]]||[],lv=env[Math.max(0,Math.floor((t-best[1])*30))]||0;
 el.innerHTML=`<div class="av" style="background:${col};box-shadow:0 0 0 ${4+lv*16}px color-mix(in srgb,${col} 35%,transparent)">${H.init||'•'}</div><div><div class="nm">${H.name||''}</div><div class="fr" style="color:${col}">${H.role||''}</div></div>`;
 el.style.opacity=bo;el.style.borderColor=col}
const TICK=(()=>{if(V.format!=='newsdesk')return '';const r=(S2,k)=>`${S2.tick} ₹${inr(S2.price)}  ${S2.ret['1Y']>=0?'▲':'▼'} ${Math.abs(S2.ret['1Y'])}% 1Y`;
 return [r(A),r(B),`P/E ${A.pe} vs ${B.pe}`,`ROE ${A.roe}% vs ${B.roe}%`,`Div yield ${A.dy}% vs ${B.dy}%`,`M-cap ₹${Lc(A.mcap)} L Cr vs ₹${Lc(B.mcap)} L Cr`].join('   ◆   ')+'   ◆   '})();
