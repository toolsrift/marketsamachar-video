/* Signature moment for hdfc-icici-v2 — the July 2023 merger. Used only in this video. */
E.sig_merger=(sp,S)=>{const i=S._i;
 const bank=(w,h,col,lab,id)=>`<svg width="${w}" height="${h}" viewBox="0 0 300 300" id="${id}"><path d="M20 92 L150 22 L280 92 Z" fill="${col}"/><rect x="28" y="92" width="244" height="18" fill="${col}"/>
  ${[0,1,2,3,4].map(k=>`<rect x="${44+k*48}" y="118" width="22" height="132" rx="4" fill="color-mix(in srgb,${col} 75%,var(--bg))"/>`).join('')}<rect x="20" y="252" width="260" height="22" fill="${col}"/><rect x="8" y="274" width="284" height="18" fill="color-mix(in srgb,${col} 80%,#000)"/>
  <circle cx="150" cy="66" r="14" fill="var(--bg)"/><text x="150" y="72" text-anchor="middle" style="font-size:18px;font-weight:800;fill:${col}">₹</text></svg>
  <div class="tk" style="text-align:center;font-size:40px;color:${col};margin-top:6px">${lab}</div>`;
 const h=`<div class="ab lbl" id="mg_d${i}" style="left:110px;width:1700px;top:250px;text-align:center;font-size:28px;opacity:0">${ICON('calendar',30,'var(--gt)')} 1 JULY 2023</div>
  <div class="ab" id="mg_a${i}" style="left:300px;top:330px;width:340px;opacity:0">${bank(340,340,'var(--a)','HDFC Bank','mg_sa')}</div>
  <div class="ab" id="mg_b${i}" style="left:1280px;top:330px;width:340px;opacity:0">${bank(340,340,'#2BB3A3','HDFC Ltd','mg_sb')}<div class="cs" style="text-align:center;font-weight:700;font-size:24px">India's largest home-loan company</div></div>
  <div class="ab" id="mg_m${i}" style="left:660px;top:300px;width:600px;opacity:0">${bank(600,420,'var(--a)','HDFC Bank, after the merger','mg_sm')}</div>
  ${Array.from({length:14},(_,k)=>`<div class="ab" id="mg_p${k}_${i}" style="left:950px;top:520px;width:${14+k%4*6}px;height:${14+k%4*6}px;border-radius:50%;background:color-mix(in srgb,var(--ink) 30%,transparent);opacity:0"></div>`).join('')}
  <div class="ab" style="left:110px;width:1700px;top:850px;display:flex;justify-content:center;gap:28px">
   <span class="chip card" id="mg_c1${i}" style="font-size:30px;padding:14px 26px;opacity:0">${ICON('trending-up',32,'var(--gt)')} Much bigger equity base</span>
   <span class="chip card" id="mg_c2${i}" style="font-size:30px;padding:14px 26px;opacity:0">${ICON('trending-down',32,'var(--dn)')} ROE: 17% (FY24) → 14% (FY25)</span></div>`;
 return {html:h,anim(t,b){const s0=BT(b,0),s1=BT(b,1),s2=BT(b,2);rise('mg_d'+i,t,s0,.5,20);rise('mg_a'+i,t,s0+.3,.6,40);rise('mg_b'+i,t,s0+.5,.6,40);
  const m=eio(P(t,s1+.4,1.0));if(t>=s1+.4){st('mg_a'+i,{transform:`translateX(${m*330}px)`,opacity:1-cl((m-.85)/.15)});st('mg_b'+i,{transform:`translateX(${-m*330}px)`,opacity:1-cl((m-.85)/.15)})}
  pop('mg_m'+i,t,s1+1.35,.6,.6);for(let k=0;k<14;k++){const a=k/14*6.283,p=eo(P(t,s1+1.3,.9));st(`mg_p${k}_${i}`,{opacity:t>s1+1.3?(1-p)*.9:0,transform:`translate(${Math.cos(a)*p*380}px,${Math.sin(a)*p*220}px)`})}
  pop('mg_c1'+i,t,s2+.3,.45,.6);pop('mg_c2'+i,t,s2+1.6,.45,.6)}}};
