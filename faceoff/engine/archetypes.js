/* ======================= PHASE 3: EPISODE SCENE TYPES (1–3 stocks) ======================= */
const E={};const KEYS=['a','b','c'].filter(k=>D[k]);const NS=KEYS.length;const SK=k=>D[k];
const SCOL=s=>({a:'var(--a)',b:'var(--b)',c:'var(--c)',g:'var(--gt)',dn:'var(--dn)',up:'var(--up)',bench:'var(--sub)'})[s]||'var(--ink)';
const NUMRE=/^([^\d−-]*?)(-|−)?([\d,]*\.?\d+)(.*)$/;
function countStr(id,t,s,d,str){const e=$(id);if(!e)return;const m=String(str).match(NUMRE);if(!m){e.textContent=str;return}
 const raw=m[3].replace(/,/g,''),dec=(raw.split('.')[1]||'').length,v=parseFloat(raw)*eo(P(t,s,d));
 let txt=dec?v.toFixed(dec):String(Math.round(v));if(m[3].includes(','))txt=Number(txt).toLocaleString('en-IN',{minimumFractionDigits:dec,maximumFractionDigits:dec});
 e.textContent=m[1]+(m[2]||'')+txt+m[4]}
const BT=(b,k)=>b.length?b[Math.min(k||0,b.length-1)]:0;
const NM=c=>c==='bench'?(D.benchLabel||'Industry avg'):(SK(c).say||SK(c).tick);
const TK=c=>c==='bench'?(D.benchShort||'INDUSTRY'):SK(c).tick;
const LAYC=(n,x0=110,w=1700)=>Array.from({length:n},(_,k)=>({x:x0+k*w/n,w:w/n,cx:x0+(k+.5)*w/n}));
const FMT=(v,f)=>v==null?'—':f==='pct'?v.toFixed(Math.abs(v)<10?2:1)+'%':f==='x'?v.toFixed(1)+'×':f==='inr'?'₹'+inr(v):f==='L'?'₹'+(v/1e5).toFixed(2)+' L Cr':f==='k'?'₹'+(v/1e3).toFixed(1)+'K Cr':f==='int'?String(Math.round(v)):String(v);
const SIDES=sp=>sp.sides||(NS===1&&sp.rows&&sp.rows.some(r=>r.bench!=null)?['a','bench']:KEYS);   // single stock: compare with a benchmark when one is given

// one to three giant numbers
E.hero=(sp,S)=>{const it=sp.items,n=it.length,cols=LAYC(n),fs=n===1?250:n===2?180:140;let h='';
 it.forEach((x,k)=>{h+=`<div class="ab" id="hr_${k}_${S._i}" style="left:${cols[k].x}px;top:${n===1?250:290}px;width:${cols[k].w}px;text-align:center;opacity:0">
   ${x.icon?`<div id="hr_i${k}_${S._i}" style="margin-bottom:10px">${ICON(x.icon,n===1?84:64,SCOL(x.color||x.side||'g'))}</div>`:''}${x.side?`<div class="tk" style="font-size:${n===1?46:n===2?52:42}px;color:${SCOL(x.side)}">${NM(x.side)}</div>`:''}
   <div class="num" id="hr_v${k}_${S._i}" style="font-size:${fs}px;line-height:1.05;color:${SCOL(x.color||x.side)}">${x.value}</div>
   <div style="font-weight:800;font-size:${n===1?44:n===2?36:30}px;margin-top:10px">${x.label||''}</div>${x.sub?`<div class="cs" style="font-weight:600;font-size:26px;margin-top:8px">${x.sub}</div>`:''}</div>`});
 if(sp.caption)h+=`<div class="ab" id="hr_c${S._i}" style="left:160px;width:1600px;top:${n===1?780:770}px;text-align:center;font-family:var(--fh);font-size:50px;line-height:1.2;opacity:0"><span class="hl">${sp.caption}</span></div>`;
 return {html:h,anim(t,b){it.forEach((x,k)=>{const s=BT(b,x.beat)+.1;pop(`hr_${k}_${S._i}`,t,s,.5,.6);countStr(`hr_v${k}_${S._i}`,t,s,1.1,x.value);if(x.icon)pop(`hr_i${k}_${S._i}`,t,s-.1,.5,.2)});
  if(sp.caption)rise('hr_c'+S._i,t,BT(b,sp.captionBeat)+.2,.5,30)}}};

// kinetic typography
E.kinetic=(sp,S)=>{const L=sp.lines,tot=L.length;let h=`<div class="ab" style="left:150px;width:1620px;top:${sp.top||120}px;height:${sp.h||860}px;display:flex;flex-direction:column;justify-content:center;gap:${sp.gap||28}px;text-align:${sp.align||'center'}">`;
 const clean=w=>w.replace(/[^\w₹%.−-]/g,'').toLowerCase();
 L.forEach((ln,k)=>{const sz=ln.size||(ln.sub?38:tot>2?84:104),words=ln.text.split(' ');
  h+=`<div style="${ln.sub?'font-family:Inter;font-weight:700;color:var(--sub);':'font-family:var(--fh);'}font-size:${sz}px;line-height:1.14">`+(ln.icon?`<span id="kw_${S._i}_${k}_i" style="display:inline-block;opacity:0;margin-right:18px">${ICON(ln.icon,Math.round(sz*.9),SCOL(ln.ec||'g'))}</span>`:'')+words.map((w,j)=>{const em=(ln.emph||[]).some(e=>clean(w)===e.toLowerCase());
   return `<span id="kw_${S._i}_${k}_${j}" style="display:inline-block;opacity:0;${em?`color:${SCOL(ln.ec||'g')};`:''}">${em?`<span class="hl">${w}</span>`:w}</span>`}).join(' ')+`</div>`});
 h+='</div>';
 return {html:h,anim(t,b){L.forEach((ln,k)=>{const s=BT(b,ln.beat)+.05,n=ln.text.split(' ').length,step=ln.step||Math.min(.12,1.5/n);if(ln.icon)pop(`kw_${S._i}_${k}_i`,t,s-.1,.45,.3);
  for(let j=0;j<n;j++){const p=eo(P(t,s+j*step,.35));st(`kw_${S._i}_${k}_${j}`,{opacity:p,transform:`translateY(${(1-p)*36}px) scale(${.92+.08*p})`})}})}}};

// metric rows: split-screen duel for 2 stocks; a table for 1 stock (vs benchmark) or 3 stocks
E.duel=(sp,S)=>{const sides=SIDES(sp),R=sp.rows,i=S._i;
 if(sides.length!==2)return E.table(sp,S);
 const [L0,R0]=sides;
 let h=`<div class="ab" style="left:0;top:0;width:960px;height:1080px;background:linear-gradient(90deg,color-mix(in srgb,${SCOL(L0)} 16%,transparent),transparent 85%)"></div><div class="ab" style="left:960px;top:0;width:960px;height:1080px;background:linear-gradient(270deg,color-mix(in srgb,${SCOL(R0)} 16%,transparent),transparent 85%)"></div>
  <div class="ab" style="left:958px;top:250px;width:4px;height:640px;background:var(--grid)"></div>
  ${[[L0,110],[R0,1050]].map(([c,x])=>`<div class="ab" id="du_h${c}${i}" style="left:${x}px;width:760px;top:250px;text-align:center;opacity:0"><div class="tk" style="font-size:80px;color:${SCOL(c)}">${TK(c)}</div><div class="cs" style="font-weight:700;font-size:26px">${c==='bench'?(sp.benchNote||D.benchNote||''):SK(c).name}</div></div>`).join('')}`;
 const y0=440,dy=Math.min(130,460/R.length);
 R.forEach((r,k)=>{const va=r[L0],vb=r[R0],y=y0+k*dy,mx=Math.max(Math.abs(va),Math.abs(vb))||1,w=r.better==='low'?(va<vb?'l':'r'):r.better==='high'?(va>vb?'l':'r'):null,id=`du${i}_`;
  h+=`<div class="ab" id="${id}r${k}" style="left:0;top:${y}px;width:1920px;height:${dy}px;opacity:0">
   <div style="position:absolute;left:820px;width:280px;top:14px;text-align:center"><span class="chip" style="font-size:23px;padding:8px 18px;background:var(--card);border:2px solid var(--cardb)">${r.icon?ICON(r.icon,26,'var(--gt)'):''}${r.label}</span></div>
   <div class="num" style="position:absolute;right:1130px;top:0;font-size:60px;color:${w==='l'&&L0!=='bench'?'var(--gt)':'var(--ink)'};white-space:nowrap">${w==='l'&&L0!=='bench'?'✓ ':''}${FMT(va,r.f)}</div>
   <div class="num" style="position:absolute;left:1130px;top:0;font-size:60px;color:${w==='r'&&R0!=='bench'?'var(--gt)':R0==='bench'?'var(--sub)':'var(--ink)'};white-space:nowrap">${FMT(vb,r.f)}${w==='r'&&R0!=='bench'?' ✓':''}</div>
   <div id="${id}bl${k}" data-w="${Math.abs(va)/mx*560}" style="position:absolute;right:1130px;top:${dy-36}px;height:16px;width:0;border-radius:8px;background:${SCOL(L0)}"></div>
   <div id="${id}br${k}" data-w="${Math.abs(vb)/mx*560}" style="position:absolute;left:1130px;top:${dy-36}px;height:16px;width:0;border-radius:8px;background:${SCOL(R0)}"></div></div>`});
 return {html:h,anim(t,b){rise(`du_h${L0}${i}`,t,.4,.5);rise(`du_h${R0}${i}`,t,.55,.5);R.forEach((r,k)=>{const s=BT(b,r.beat),id=`du${i}_`;rise(id+'r'+k,t,s,.45,25);const p=eio(P(t,s+.2,.8));
  ['l','r'].forEach(c=>{const e=$(id+'b'+c+k);if(e)e.style.width=(+e.dataset.w*p)+'px'})})}}};

// table: label column + one column per side (1 stock + benchmark, or 3 stocks); best value glows
E.table=(sp,S)=>{const sides=SIDES(sp),R=sp.rows,i=S._i,cols=LAYC(sides.length,560,1250),y0=430,dy=Math.min(118,470/R.length);
 let h=cols.map((c,k)=>`<div class="ab" id="tb_h${k}_${i}" style="left:${c.x}px;width:${c.w}px;top:260px;text-align:center;opacity:0"><div class="tk" style="font-size:${sides.length>2?60:70}px;color:${SCOL(sides[k])}">${TK(sides[k])}</div><div class="cs" style="font-weight:700;font-size:22px">${sides[k]==='bench'?(sp.benchNote||D.benchNote||''):SK(sides[k]).name}</div></div>`).join('');
 R.forEach((r,k)=>{const vals=sides.map(s=>r[s]),ok=vals.filter(v=>v!=null),best=r.better==='low'?Math.min(...ok):r.better==='high'?Math.max(...ok):null,mx=Math.max(...ok.map(Math.abs))||1,y=y0+k*dy;
  h+=`<div class="ab" id="tb_r${k}_${i}" style="left:110px;top:${y}px;width:1700px;height:${dy-12}px;border-radius:var(--rad);background:${k%2?'transparent':'color-mix(in srgb,var(--ink) 5%,transparent)'};opacity:0">
   <div style="position:absolute;left:24px;top:0;height:100%;display:flex;align-items:center;gap:14px;font-weight:800;font-size:30px">${r.icon?ICON(r.icon,34,'var(--gt)'):''}${r.label}</div>
   ${cols.map((c,j)=>{const v=vals[j],win=best!=null&&v===best&&sides[j]!=='bench';return `<div style="position:absolute;left:${c.x-110}px;width:${c.w}px;top:${dy/2-46}px;text-align:center"><span class="num" style="font-size:52px;color:${win?'var(--gt)':sides[j]==='bench'?'var(--sub)':'var(--ink)'}">${FMT(v,r.f)}${win?' ✓':''}</span>
    <div style="margin:4px auto 0;width:${c.w*.6}px;height:10px;border-radius:5px;background:var(--grid);overflow:hidden"><div class="tbbar" data-w="${v==null?0:Math.abs(v)/mx*100}" style="height:100%;width:0;background:${SCOL(sides[j])}"></div></div></div>`}).join('')}</div>`});
 return {html:h,anim(t,b){cols.forEach((c,k)=>rise(`tb_h${k}_${i}`,t,.4+k*.12,.5,30));R.forEach((r,k)=>{const s=BT(b,r.beat);rise(`tb_r${k}_${i}`,t,s,.45,20);const e=$(`tb_r${k}_${i}`);if(e)e.querySelectorAll('.tbbar').forEach(x=>x.style.width=(+x.dataset.w*eio(P(t,s+.2,.8)))+'%')})}}};

// big chart; the camera flies to each callout. A line for every stock (+ optional dashed benchmark)
E.chartzoom=(sp,S)=>{const xs=D[sp.x||'years10'],ix=sp.index,id=`cz${S._i}`;
 const ser=KEYS.map(k=>[k,SK(k)[sp.series]]);if(sp.bench)ser.push(['bench',sp.bench]);
 const SV=ser.map(([k,a])=>[k,ix?a.map(x=>x/a[0]*100):a]);
 const fmt=sp.fmt==='pct'?(v=>Math.round(v)+'%'):sp.fmt==='L'?(v=>(v/1e5).toFixed(2)):sp.fmt==='k'?(v=>(v/1e3).toFixed(1)):(v=>String(Math.round(v)));
 const x0=240,x1=1700,y0=870,y1=360,n=xs.length,all=SV.flatMap(s=>s[1]),lo=sp.zero===false?Math.floor(Math.min(...all)*0.8):Math.min(0,Math.min(...all)*1.1),hi=Math.max(...all)*1.1,gw=(x1-x0)/(n-1),X=i=>x0+i*gw,Y=v=>y0-(v-lo)/(hi-lo)*(y0-y1);
 const pth=arr=>arr.map((v,i)=>(i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1)).join(' ');
 let g='';for(let k=0;k<=4;k++){const v=lo+(hi-lo)/4*k;g+=`<line x1="${x0}" x2="${x1}" y1="${Y(v)}" y2="${Y(v)}" style="stroke:var(--grid);stroke-width:2"/><text x="${x0-22}" y="${Y(v)+8}" text-anchor="end" style="fill:var(--sub);font-size:22px">${fmt(v)}</text>`}
 xs.forEach((l,i)=>{g+=`<text x="${X(i)}" y="${y0+44}" text-anchor="middle" style="fill:var(--sub);font-size:22px;font-family:Mono">${l}</text>`});
 const CO=sp.callouts||[],get=w=>(SV.find(s=>s[0]===w)||SV[0])[1];
 let h=`<div class="ab" id="${id}w" style="left:0;top:0;width:1920px;height:1080px;transform-origin:0 0">
  <div class="ab lbl" style="left:110px;top:262px">${sp.unit||''}</div>${D.note10&&(sp.x||'years10')==='years10'&&!sp.noNote?`<div class="ab" style="right:110px;top:258px;font-weight:700;font-size:21px;color:var(--sub);max-width:860px;text-align:right">ⓘ ${D.note10}</div>`:''}
  <div class="ab" style="left:${x0}px;top:300px;display:flex;gap:30px">${SV.map(([k])=>`<span class="tk" style="font-size:30px;color:${SCOL(k)}">● ${k==='bench'?(sp.benchLabel||D.benchLabel||'Industry avg'):TK(k)}</span>`).join('')}</div>
  <svg class="ab" style="left:0;top:0" width="1920" height="1080"><defs><clipPath id="${id}cp"><rect id="${id}cr" x="0" y="0" width="0" height="1080"/></clipPath></defs>${g}
   <g clip-path="url(#${id}cp)">${SV.map(([c,arr])=>`<path d="${pth(arr)}" style="fill:none;stroke:${SCOL(c)};stroke-width:${c==='bench'?5:8};${c==='bench'?'stroke-dasharray:14 12;':''}stroke-linejoin:round;stroke-linecap:round"/>${c==='bench'?'':arr.map((v,i)=>`<circle cx="${X(i)}" cy="${Y(v)}" r="9" style="fill:var(--bg);stroke:${SCOL(c)};stroke-width:5"/>`).join('')}`).join('')}</g></svg>`;
 CO.forEach((c,k)=>{const arr=get(c.who),px=X(c.i),py=Y(arr[c.i]),left=px>1250;c._p=[px,py];const up=c.below?false:py>470;
  h+=`<div class="ab" id="${id}c${k}" style="left:${left?px-420:px+34}px;top:${up?py-150:py+34}px;width:380px;opacity:0"><div class="card" style="padding:14px 18px;border-color:${SCOL(c.who)};border-width:3px"><div class="num" style="font-size:36px;color:${SCOL(c.who)};display:flex;align-items:center;gap:10px">${c.icon?ICON(c.icon,34,SCOL(c.who)):''}${c.big||fmt(arr[c.i])}</div><div style="font-weight:700;font-size:21px;line-height:1.25">${c.text}</div></div></div>
  <div class="ab" id="${id}d${k}" style="left:${px-24}px;top:${py-24}px;width:48px;height:48px;border-radius:50%;border:5px solid ${SCOL(c.who)};opacity:0"></div>`});
 h+='</div>';
 return {html:h,anim(t,b){const s0=BT(b,sp.drawBeat||0)+.2,e=$(id+'cr');if(e)e.setAttribute('width',(x0+(x1-x0)*eio(P(t,s0,1.8))+30).toFixed(0));
  const ks=[[0,null]];CO.forEach((c,k)=>ks.push([BT(b,c.beat),k]));const outT=sp.outBeat!=null?BT(b,sp.outBeat):S.dur-1.7;ks.push([outT,null]);
  let cur={x:960,y:540,s:1,t:0},prev=cur;for(const [kt,k] of ks){if(t>=kt){prev=cur;cur=k==null?{x:960,y:540,s:1,t:kt}:{x:CO[k]._p[0],y:CO[k]._p[1],s:sp.zoom||1.45,t:kt}}}
  const p=eio(P(t,cur.t,.9)),zs=prev.s+(cur.s-prev.s)*p,zx=prev.x+(cur.x-prev.x)*p,zy=prev.y+(cur.y-prev.y)*p,cx=Math.min(Math.max(zx,960/zs),1920-960/zs),cy=Math.min(Math.max(zy,540/zs),1080-540/zs);
  st(id+'w',{transform:`translate(${960-cx*zs}px,${540-cy*zs}px) scale(${zs})`});const fade=1-cl((zs-1)/.3),te=$('tt'+S._i);if(te)te.style.opacity=(parseFloat(te.style.opacity)||0)*fade;st('tr'+S._i,{opacity:fade});
  CO.forEach((c,k)=>{pop(id+'d'+k,t,BT(b,c.beat)+.35,.35,.3);const s=BT(b,c.beat)+.5,end=k<CO.length-1?BT(b,CO[k+1].beat):outT,q=eo(P(t,s,.4))*(1-P(t,end,.3));st(id+'c'+k,{opacity:q,transform:`translateY(${(1-cl(P(t,s,.4)))*20}px)`})})}}};

// ₹1 lakh invested N years ago — one column per stock
E.invest=(sp,S)=>{const Y=sp.years||5,amt=sp.amount||100000,i=S._i,vals=KEYS.map(k=>amt*Math.pow(1+SK(k).ret[Y+'Y']/100,Y)),mx=Math.max(...vals,amt)*1.05,cols=LAYC(NS,NS===1?560:260,NS===1?800:1400);
 const L=v=>'₹'+(v/1e5).toFixed(2)+' L';
 let h=`<div class="ab" id="iv_q${i}" style="left:110px;width:1700px;top:250px;text-align:center;font-family:var(--fh);font-size:60px;opacity:0">${sp.title||`₹1 lakh invested ${Y} years ago`}</div>`;
 KEYS.forEach((c,j)=>{const v=vals[j],ch=(v/amt-1)*100,cx=cols[j].cx;S['_iv'+c]=v;
  h+=`<div class="ab" id="iv_${c}${i}" style="left:${cx-300}px;width:600px;top:350px;height:580px;opacity:0"><div style="text-align:center"><span class="tk" style="font-size:48px;color:var(--${c})">${SK(c).tick}</span></div>
   <div style="position:absolute;left:190px;width:220px;bottom:130px;height:370px;display:flex;align-items:flex-end"><div id="iv_b${c}${i}" data-h0="${amt/mx*370}" data-h1="${v/mx*370}" style="width:220px;height:${amt/mx*370}px;background:repeating-linear-gradient(0deg,var(--${c}) 0 28px,color-mix(in srgb,var(--${c}) 65%,var(--bg)) 28px 32px);border-radius:10px 10px 4px 4px"></div></div>
   <div style="position:absolute;left:0;width:600px;bottom:50px;text-align:center;white-space:nowrap"><span class="num" id="iv_v${c}${i}" style="font-size:${NS>2?54:64}px">${L(amt)}</span> <span class="num" id="iv_p${c}${i}" style="font-size:34px;color:var(--${ch>=0?'up':'dn'});opacity:0">${ch>=0?'+':'−'}${Math.abs(ch).toFixed(0)}%</span></div></div>`});
 h+=`<div class="ab cs" id="iv_n${i}" style="left:110px;width:1700px;top:930px;text-align:center;font-weight:700;font-size:21px;opacity:0">From ${NS>1?"each stock's":"the stock's"} ${Y}-year share-price CAGR · excludes dividends · past returns don't predict future returns</div>`;
 const beats=sp.beats||KEYS.map((k,j)=>sp['beat'+k.toUpperCase()]??(j+1));
 return {html:h,anim(t,b){rise('iv_q'+i,t,BT(b,0),.5,30);KEYS.forEach((c,j)=>rise(`iv_${c}${i}`,t,BT(b,0)+.3+j*.15,.5));st('iv_n'+i,{opacity:P(t,BT(b,0)+.8,.4)});
  KEYS.forEach((c,j)=>{const s=BT(b,beats[j]),p=eio(P(t,s+.2,1.5)),e=$('iv_b'+c+i);if(e)e.style.height=(+e.dataset.h0+(e.dataset.h1-e.dataset.h0)*p)+'px';$('iv_v'+c+i).textContent=L(amt+(S['_iv'+c]-amt)*p);st('iv_p'+c+i,{opacity:P(t,s+1.6,.3)})})}}};

// myth vs fact
E.mythfact=(sp,S)=>{const vd=sp.verdict||'FALSE',vc=vd==='TRUE'?'var(--up)':vd==='FALSE'?'var(--dn)':'var(--b)',i=S._i;
 return {html:`<div class="ab card" id="mf_c${i}" style="left:240px;top:250px;width:1440px;padding:44px 56px;opacity:0">
   <div class="lbl" style="font-size:26px;display:flex;align-items:center;gap:12px">${sp.icon?ICON(sp.icon,34,'var(--sub)'):''}Myth</div><div style="font-family:var(--fh);font-size:62px;line-height:1.14;margin-top:10px;position:relative">“${sp.myth}”${vd==='FALSE'?`<div id="mf_x${i}" style="position:absolute;left:0;top:52%;height:8px;width:0;background:${vc};border-radius:4px"></div>`:''}</div>
   <div id="mf_f${i}" style="opacity:0;margin-top:34px;border-top:3px solid var(--grid);padding-top:26px"><div class="lbl" style="font-size:26px;color:${vc}">Fact</div><div style="font-weight:800;font-size:40px;line-height:1.28;margin-top:8px">${sp.fact}</div></div></div>
  <div class="stamp" id="mf_s${i}" style="right:170px;top:190px;border-color:${vc};color:${vc};font-size:62px">${vd}</div>`,
  anim(t,b){rise('mf_c'+i,t,BT(b,0),.5,40);const s=BT(b,sp.factBeat??1),p=P(t,s,.35);st('mf_s'+i,{opacity:cl(p*4),transform:`rotate(-8deg) scale(${2.2-1.2*eo(p)})`});st('mf_x'+i,{width:eo(P(t,s+.1,.4))*100+'%'});rise('mf_f'+i,t,s+.4,.5,30)}}};

// quiz with countdown — options are the stocks, or custom options (single-stock quizzes)
E.quiz=(sp,S)=>{const R=110,Cc=2*Math.PI*R,i=S._i,opts=sp.options||KEYS.map(k=>({key:k,label:SK(k).tick,sub:SK(k).name,col:k})),n=opts.length;
 const W=n===2?600:n===3?480:380,gap=n===2?220:n===3?60:40,x0=(1920-(n*W+(n-1)*gap))/2;
 const ans=typeof sp.answer==='number'?sp.answer:opts.findIndex(o=>o.key===sp.answer);
 return {html:`<div class="ab" id="qz_q${i}" style="left:160px;width:1600px;top:240px;text-align:center;font-family:var(--fh);font-size:58px;line-height:1.15;opacity:0"><span class="lbl" style="display:block;font-size:26px;margin-bottom:14px;color:var(--gt)">Quick quiz · ${sp.n||'for you'}</span>${sp.q}</div>
  ${opts.map((o,k)=>`<div class="ab card" id="qz_${k}_${i}" style="left:${x0+k*(W+gap)}px;top:520px;width:${W}px;height:240px;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;border-width:4px">
   <div class="tk" style="font-size:${n>2?60:80}px;color:${SCOL(o.col||'g')}">${o.label}</div><div class="cs" style="font-weight:700;font-size:26px;text-align:center;padding:0 16px">${o.sub||''}</div>
   <div id="qz_k${k}_${i}" class="ck" style="position:absolute;right:-24px;top:-24px;width:68px;height:68px;font-size:40px;opacity:0">✓</div></div>`).join('')}
  <div class="ab" id="qz_t${i}" style="left:${960-R-20}px;top:${n===2?640-R-20:770}px;width:${2*R+40}px;height:${2*R+40}px;opacity:0"><svg width="${2*R+40}" height="${2*R+40}"><circle cx="${R+20}" cy="${R+20}" r="${R}" style="fill:var(--bg);stroke:var(--grid);stroke-width:14"/><circle id="qz_tc${i}" cx="${R+20}" cy="${R+20}" r="${R}" transform="rotate(-90 ${R+20} ${R+20})" stroke-dasharray="${Cc}" stroke-dashoffset="0" style="fill:none;stroke:var(--g);stroke-width:14;stroke-linecap:round"/></svg>
   <div class="num" id="qz_n${i}" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:100px"></div></div>
  <div class="ab" id="qz_r${i}" style="left:160px;width:1600px;top:820px;text-align:center;font-weight:800;font-size:42px;line-height:1.25;opacity:0">${sp.reveal}</div>`,
 anim(t,b){rise('qz_q'+i,t,BT(b,0),.5,30);const cs=BT(b,sp.countBeat??1),cd=sp.count||3,rv=BT(b,sp.revealBeat??2);
  opts.forEach((o,k)=>{if(t<rv)pop(`qz_${k}_${i}`,t,BT(b,0)+.6+k*.2,.4,.7);else{const pr=eo(P(t,rv,.4));if(k===ans)st(`qz_${k}_${i}`,{opacity:1,transform:`scale(${1+.06*pr})`,borderColor:'var(--g)',boxShadow:'0 0 60px color-mix(in srgb,var(--g) 45%,transparent)'});else st(`qz_${k}_${i}`,{opacity:1-.6*pr,transform:`scale(${1-.04*pr})`})}});
  st('qz_t'+i,{opacity:t>=cs&&t<rv+.25?cl(P(t,cs,.2))*(1-P(t,rv,.25)):0,transform:`scale(${.8+.2*eo(P(t,cs,.3))})`});
  const left=cl(cd-(t-cs),0,cd);$('qz_n'+i).textContent=left>0?Math.ceil(left):'';$('qz_tc'+i).setAttribute('stroke-dashoffset',Cc*(1-left/cd));
  pop(`qz_k${ans}_${i}`,t,rv+.1,.35,.2);rise('qz_r'+i,t,rv+.3,.45,25)}}};

// closing: coloured columns, one per stock (single stock: bull case vs bear case via sp.cols)
E.split=(sp,S)=>{const i=S._i,cs=sp.cols||KEYS.map(k=>({key:k,...sp[k]})),n=cs.length,cols=LAYC(n,0,1920);let h='';
 cs.forEach((q,j)=>{const c=q.key,col=q.color?SCOL(q.color):SCOL(c),x=cols[j].x,w=cols[j].w;
  h+=`<div class="ab" id="sv_${j}_${i}" style="left:${x}px;top:0;width:${w}px;height:1080px;background:color-mix(in srgb,${col} 14%,transparent);opacity:0"></div>
  <div class="ab" id="sv_t${j}_${i}" style="left:${x+(n>2?70:110)}px;width:${w-(n>2?120:180)}px;top:240px;opacity:0"><div class="tk" style="font-size:${n>2?56:70}px;color:${col}">${q.title||SK(c).tick}</div><div style="font-family:var(--fh);font-size:${n>2?36:44}px;margin-top:6px;line-height:1.15">${q.head}</div></div>
  ${q.rows.map((r,k)=>`<div class="ab" id="sv_${j}_${k}_${i}" style="left:${x+(n>2?70:110)}px;width:${w-(n>2?110:150)}px;top:${(n>2?440:420)+k*84}px;display:flex;gap:16px;align-items:center;opacity:0">${q.icons&&q.icons[k]?ICON(q.icons[k],40,col):'<span class="ck">✓</span>'}<span style="font-weight:800;font-size:${n>2?27:33}px;line-height:1.2">${r}</span></div>`).join('')}`});
 if(sp.q)h+=`<div class="ab" id="sv_q${i}" style="left:110px;top:790px;width:1700px;height:140px;background:var(--g);color:var(--onG);display:flex;align-items:center;gap:30px;padding:0 50px;border-radius:var(--rad);opacity:0"><svg width="80" height="80" viewBox="0 0 24 24"><path d="M4 4h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-5 4v-4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z" fill="currentColor"/></svg><div><div style="font-family:var(--fh);font-size:50px;line-height:1">${sp.q}</div><div style="font-weight:800;font-size:26px;margin-top:8px">Not a buy or sell call</div></div></div>`;
 return {html:h,anim(t,b){cs.forEach((q,j)=>{const s=BT(b,q.beat);st(`sv_${j}_${i}`,{opacity:P(t,s,.5)});rise(`sv_t${j}_${i}`,t,s+.1,.5,30);q.rows.forEach((r,k)=>slide(`sv_${j}_${k}_${i}`,t,s+.7+k*.6,.4,-30))});if(sp.q)pop('sv_q'+i,t,BT(b,sp.qBeat),.5,.7)}}};

// podium: rank the stocks on ONE metric (3rd → 2nd → 1st). Never an overall verdict.
E.podium=(sp,S)=>{const i=S._i,vals=KEYS.map(k=>({k,v:sp[k]})),ord=[...vals].sort((x,y)=>sp.better==='low'?x.v-y.v:y.v-x.v),place={};ord.forEach((o,r)=>place[o.k]=r);
 const pos=[{x:960,h:330,lab:'1st'},{x:560,h:240,lab:'2nd'},{x:1360,h:170,lab:'3rd'}].slice(0,NS);
 let h=`<div class="ab" id="pd_l${i}" style="left:110px;width:1700px;top:250px;text-align:center;opacity:0"><span class="lbl" style="font-size:26px">${sp.label}</span><div class="cs" style="font-weight:700;font-size:22px;margin-top:6px">${sp.better==='low'?'lower is better':'higher is better'} · ranked on this metric only</div></div>`;
 KEYS.forEach(k=>{const r=place[k],p=pos[r];h+=`<div class="ab" id="pd_${k}${i}" style="left:${p.x-170}px;top:${960-p.h-170}px;width:340px;opacity:0;text-align:center">
   <div class="tk" style="font-size:52px;color:var(--${k})">${SK(k).tick}</div><div class="num" style="font-size:56px">${FMT(sp[k],sp.f)}</div></div>
  <div class="ab" id="pd_b${k}${i}" style="left:${p.x-170}px;top:${960-p.h}px;width:340px;height:${p.h}px;background:linear-gradient(color-mix(in srgb,var(--${k}) 80%,#fff),var(--${k}));border-radius:12px 12px 0 0;transform-origin:bottom;transform:scaleY(0);display:flex;align-items:flex-start;justify-content:center;padding-top:20px">
   <span class="num" style="font-size:64px;color:rgba(255,255,255,.92)">${p.lab}</span></div>`});
 const rb=sp.revealBeats||[1,2,3];
 return {html:h,anim(t,b){rise('pd_l'+i,t,BT(b,0),.5,20);KEYS.forEach(k=>{const r=place[k],s=BT(b,rb[NS-1-r]);st(`pd_b${k}${i}`,{transform:`scaleY(${P(t,s,.6)<1?eb(P(t,s,.6)):1})`});pop(`pd_${k}${i}`,t,s+.4,.45,.5)})}}};

// scorecard grid: stocks × metrics; best per row lights up
E.scorecard=(sp,S)=>{const i=S._i,R=sp.rows,cols=LAYC(NS,620,1190),dy=Math.min(84,560/R.length);
 let h=cols.map((c,k)=>`<div class="ab tk" id="sc_h${k}_${i}" style="left:${c.x}px;width:${c.w}px;top:270px;text-align:center;font-size:54px;color:var(--${KEYS[k]});opacity:0">${SK(KEYS[k]).tick}</div>`).join('');
 R.forEach((r,k)=>{const vals=KEYS.map(s=>r[s]),best=r.better==='low'?Math.min(...vals):r.better==='high'?Math.max(...vals):null,y=360+k*dy;
  h+=`<div class="ab" style="left:110px;top:${y}px;width:1700px;height:${dy-8}px"><div style="position:absolute;left:20px;top:0;height:100%;display:flex;align-items:center;gap:12px;font-weight:800;font-size:27px">${r.icon?ICON(r.icon,30,'var(--gt)'):''}${r.label}</div>
   ${cols.map((c,j)=>{const win=best!=null&&vals[j]===best;return `<div id="sc_${k}_${j}_${i}" style="position:absolute;left:${c.x-110+10}px;width:${c.w-20}px;top:0;height:100%;border-radius:var(--rad);display:flex;align-items:center;justify-content:center;opacity:0;background:${win?'color-mix(in srgb,var(--g) 22%,transparent)':'color-mix(in srgb,var(--ink) 5%,transparent)'};${win?'border:3px solid var(--g)':''}"><span class="num" style="font-size:40px">${FMT(vals[j],r.f)}</span></div>`}).join('')}</div>`});
 return {html:h,anim(t,b){cols.forEach((c,k)=>rise(`sc_h${k}_${i}`,t,.4+k*.12,.5,30));R.forEach((r,k)=>{const s=(r.beat!=null?BT(b,r.beat):BT(b,0)+.3+k*.35);KEYS.forEach((x,j)=>pop(`sc_${k}_${j}_${i}`,t,s+j*.1,.35,.7))})}}};

// milestone timeline (single-stock deep dives)
E.timeline=(sp,S)=>{const i=S._i,M=sp.items,x0=200,x1=1720,X=k=>x0+(x1-x0)*(M.length>1?k/(M.length-1):.5);
 let h=`<div class="ab" style="left:${x0}px;top:600px;width:${x1-x0}px;height:6px;background:var(--grid)"></div><div class="ab" id="tl_f${i}" style="left:${x0}px;top:600px;width:0;height:6px;background:var(--gt)"></div>`;
 M.forEach((m,k)=>{const up=k%2===0;h+=`<div class="ab" id="tl_d${k}_${i}" style="left:${X(k)-16}px;top:587px;width:32px;height:32px;border-radius:50%;background:var(--bg);border:6px solid ${SCOL(m.color||'g')};opacity:0"></div>
  <div class="ab" id="tl_c${k}_${i}" style="left:${X(k)-170}px;width:340px;top:${up?300:650}px;height:250px;display:flex;flex-direction:column;justify-content:${up?'flex-end':'flex-start'};text-align:center;opacity:0">
   ${m.icon?`<div>${ICON(m.icon,46,SCOL(m.color||'g'))}</div>`:''}<div class="num" style="font-size:44px;color:${SCOL(m.color||'g')}">${m.when}</div><div style="font-weight:800;font-size:26px;line-height:1.22">${m.text}</div></div>`});
 return {html:h,anim(t,b){const f0=BT(b,M[0].beat??1),last=BT(b,M[M.length-1].beat??M.length);st('tl_f'+i,{width:((x1-x0)*eio(P(t,f0,Math.max(.5,last-f0+.6))))+'px'});
  M.forEach((m,k)=>{const s=BT(b,m.beat??k+1);pop(`tl_d${k}_${i}`,t,s,.35,.3);rise(`tl_c${k}_${i}`,t,s+.15,.45,30)})}}};

E.classic=(sp,S)=>C[sp.key](sp.variant||0,S);
E.cta=(sp,S)=>C.cta(0,S);

// overlays: speaker pill (debate / bull-bear / panel), news-desk ticker
const TALK=['debate','bullbear','panel'];
function speakerPill(S,t){const el=$('spk');if(!TALK.includes(V.format)||!S.clips||S.type==='desk'){el.style.opacity=0;return}
 let best=null,bo=0;for(const c of S.clips){const o=cl((t-(c[1]-.2))/.2)*(1-cl((t-(c[1]+c[2]+.15))/.3));if(o>bo){bo=o;best=c}}
 if(!best){el.style.opacity=0;return}
 const H=V.hosts[best[3]]||{},col=H.color?SCOL(H.color):best[3]==='n'?'var(--gt)':SCOL(best[3]),env=(V.env||{})[best[0]]||[],lv=env[Math.max(0,Math.floor((t-best[1])*30))]||0;
 el.innerHTML=`<div class="av" style="background:${col};box-shadow:0 0 0 ${4+lv*16}px color-mix(in srgb,${col} 35%,transparent)">${H.init||'•'}</div><div><div class="nm">${H.name||''}</div><div class="fr" style="color:${col}">${H.role||''}</div></div>`;
 el.style.opacity=bo;el.style.borderColor=col}
const TICK=(()=>{if(V.format!=='newsdesk')return '';const r=S2=>`${S2.tick} ₹${inr(S2.price)}  ${S2.ret['1Y']>=0?'▲':'▼'} ${Math.abs(S2.ret['1Y'])}% 1Y`;
 const m=(lab,f)=>`${lab} `+KEYS.map(k=>f(SK(k))).join(' · ');
 return [...KEYS.map(k=>r(SK(k))),m('P/E',s=>s.pe),m('ROE',s=>s.roe+'%'),m('Div yield',s=>s.dy+'%'),m('M-cap',s=>'₹'+Lc(s.mcap)+' L Cr')].join('   ◆   ')+'   ◆   '})();
