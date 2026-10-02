/* ══════════ HUD ══════════ */
const el={
  bld:document.getElementById('kBld'), chunk:document.getElementById('kChunk'),
  fill:document.getElementById('dmgFill'), num:document.getElementById('dmgNum'),
  banner:document.getElementById('banner'), dist:document.getElementById('xhDist'), tgt:document.getElementById('xhTgt'),
  fire:document.getElementById('fire'), fireLbl:document.getElementById('fireLbl'), fireSub:document.getElementById('fireSub'),
  wdesc:document.getElementById('wdesc'), flash:document.getElementById('flash'), cause:document.getElementById('cause'),
  xh:document.getElementById('xh'), toast:document.getElementById('wtoast'),
};
const STYLE_NAME={zakkyo:'雑居ビル',shop:'商店ビル',apart:'マンション',office:'オフィスビル',tower:'高層ビル',car:'駐車車両',
  pole:'電柱',tree:'街路樹',gate:'アーチ',toho:'新宿東宝ビル',trafo:'変圧器',rail:'高架',hardened:'耐爆構造ビル',park:'公園',
  water:'給水塔',tank:'タンク',gov:'庁舎',hall:'ホール',station:'駅'};
/* いま何を狙っているか：建物の種類（ランドマークなら名前）・素材・損傷 */
function targetLabel(h){
  if(!h||h.miss) return '';
  if(h.ground) return '地面';
  const q=bldAt(h.x,h.y,h.z);
  if(!q) return '';
  const b=q.b, m=b.vox[q.x+b.W*(q.y+b.H*q.z)];
  const lm=(b.lm!==undefined&&LMS[b.lm])?LMS[b.lm]:null;
  const name=lm?lm.name:(STYLE_NAME[b.style]||'建物');
  const mat=MATS[m]?MATS[m].n:'';
  const dmg=b.init?Math.round((1-b.live/b.init)*100):0;
  el.tgt.classList.toggle('lm',!!lm);
  return name+(mat?'　'+mat:'')+(dmg>0?'　損傷'+dmg+'%':'');
}
let hudT=0;
function updHUD(dt){
  hudT+=dt; if(hudT<.1) return; hudT=0;
  let p=Math.min(100,killedVox/totalVox*100);
  let restVox=0, alive=0;
  for(let k=0;k<blds.length;k++){ const b=blds[k]; restVox+=b.live; if(b.live>0&&b.style!=='pole'&&b.style!=='car'&&b.style!=='tree') alive++; }
  if(restVox>0) p=Math.min(p,99.9); else p=100;                 // 端数の切り上げで「100%なのに残っている」と見えるのを防ぐ
  el.bld.textContent=alive;
  el.chunk.textContent=chunks.length;
  el.fill.style.width=p+'%';
  el.num.innerHTML=p.toFixed(1)+'<small>%</small>';
  const h=aimRay();
  if(h.miss){ el.dist.textContent='—'; el.dist.style.color=''; el.tgt.textContent=''; }
  else {
    if(wpn==='missile'){ el.dist.textContent='◈ LOCK  '+Math.round(h.d)+' m'; el.dist.style.color='#ff5a6a'; }
    else { el.dist.textContent=Math.round(h.d)+' m'; el.dist.style.color=''; }
    el.tgt.textContent=targetLabel(h);
  }
}
/* 「なぜ効いたか」：転倒・座屈・剥離などの短い説明を照準の下に出す */
let causeT=0, causeLast='';
function causeToast(t){
  const now=performance.now();
  if(now<causeT && t===causeLast) return;
  causeT=now+1100; causeLast=t;
  el.cause.textContent=t;
  el.cause.animate([{opacity:0,transform:'translate(-50%,6px)'},{opacity:1,transform:'translate(-50%,0)',offset:.15},
    {opacity:1,offset:.75},{opacity:0,transform:'translate(-50%,-8px)'}],{duration:1500,easing:'ease-out'});
}
/* ══════════ スコアと連鎖の演出 ══════════ */
const elScore=document.getElementById('scoreBig'),
      elPops=document.getElementById('pops'),
      elChain=document.getElementById('chain'),
      elChainN=document.getElementById('chainN'),
      elChainBar=(document.getElementById('chainBar')||{}).firstElementChild,
      elChainRank=document.getElementById('chainRank');
const elBld=document.getElementById('bldCount'), elScoreSub=document.getElementById('scoreSub');
let shownScore=0, popBuf=0, popT=0, popSlot=0, scoreHotT=0;
let shownTon=0, downed=0, shownDowned=0, bldHotT=0;
const TON_PER_VOX=2.6;                 // ボクセル1個 ≒ 2.6トン
function fmtTon(t){
  if(t>=1e6) return (t/1e6).toFixed(2)+'<span>Mt</span>';
  if(t>=1e3) return (t/1e3).toFixed(1)+'<span>kt</span>';
  return Math.round(t)+'<span>t</span>';
}
const CHAINRANK=[
  [2,'#ffd166','GOOD'],[4,'#ffb03a','GREAT'],[7,'#ff8a2b','EXCELLENT'],
  [11,'#ff5a1f','AMAZING'],[16,'#ff2d78','UNREAL'],[24,'#c47bff','GODLIKE'],
  [34,'#a24bff','ANNIHILATOR'],[46,'#ff2020','CATACLYSM'],[60,'#ffffff','BEYOND']
];
let popVox=0;
function pushVox(n){ if(n>0) popVox+=n; }
function flushPops(dt){
  popT-=dt;
  if(popT>0 || popVox<=0) return;
  const v=popVox*TON_PER_VOX; popVox=0; popBuf=0;
  if(v<1) return;
  popT = v>9000?.055 : v>3000?.075 : v>900?.10 : .14;
  const big=v>9000, mid=v>2600;
  const d=document.createElement('div');
  d.className='pop';
  d.style.fontSize=(big?26:mid?20:(v>4000?16:13))+'px';
  d.style.color= big?'#fff' : mid?'#ffd98a' : (v>4000?'#ffb03a':'#e6b98a');
  d.style.textShadow = big
    ? '0 0 22px rgba(255,190,60,1),0 0 48px rgba(255,90,31,.8),0 2px 0 rgba(0,0,0,.7)'
    : '0 0 12px rgba(255,176,58,.7),0 2px 0 rgba(0,0,0,.6)';
  d.innerHTML='+'+fmtTon(v);
  popSlot=(popSlot+1)%7;
  d.style.top=(popSlot*13)+'px';
  elPops.appendChild(d);
  const dx=-8-Math.random()*26, dy=-46-Math.random()*40;
  const dur=big?1500:1050;
  d.animate([
    {transform:'translate(26px,10px) scale(.6)',opacity:0},
    {transform:'translate(0,0) scale('+(big?1.35:1.12)+')',opacity:1,offset:.13},
    {transform:'translate(0,0) scale(1)',opacity:1,offset:.30},
    {transform:'translate('+dx+'px,'+dy+'px) scale(.94)',opacity:0}
  ],{duration:dur,easing:'cubic-bezier(.16,.9,.3,1)'});
  setTimeout(()=>{ if(d.parentNode) d.parentNode.removeChild(d); },dur+60);
  if(mid){
    elScore.classList.add('hot'); scoreHotT=.42;
    elScore.animate([{transform:'scale(1.22)'},{transform:'scale(1)'}],{duration:280,easing:'cubic-bezier(.2,1.6,.4,1)'});
  }
}
function updScoreUI(dt){
  flushPops(dt);
  if(scoreHotT>0){ scoreHotT-=dt; if(scoreHotT<=0) elScore.classList.remove('hot'); }
  const ton=killedVox*TON_PER_VOX;
  if(Math.abs(shownTon-ton)>0.5){
    const d=ton-shownTon;
    shownTon += d*Math.min(1,dt*6) + Math.sign(d)*Math.min(Math.abs(d),Math.max(1,Math.abs(d)*.02));
    if(Math.abs(ton-shownTon)<1) shownTon=ton;
    elScore.innerHTML=fmtTon(shownTon);
  }
  let d2=0, tot2=0;
  for(let k=0;k<blds.length;k++){
    const b=blds[k];
    if(b.style==='pole'||b.style==='car'||b.style==='tree') continue;
    tot2++;
    if(b.live<=b.init*0.15) d2++;
  }
  if(d2!==downed){
    if(d2>downed && elBld){
      elBld.animate([{transform:'scale(1.45)',filter:'brightness(2.2)'},{transform:'scale(1)',filter:'brightness(1)'}],
        {duration:400,easing:'cubic-bezier(.2,1.7,.4,1)'});
      flashDom(.05);
    }
    downed=d2;
  }
  if(elBld) elBld.innerHTML=downed+'<span>/ '+tot2+' 棟</span>';
  if(elScoreSub && S.score!==shownScore){ shownScore=S.score; elScoreSub.innerHTML=fmtScore(S.score)+'<span>SCORE</span>'; }
  if(S.combo>1 && S.comboT>0){
    elChain.style.opacity='1';
    elChainN.textContent='×'+S.combo;
    elChainN.style.fontSize = S.combo>=100 ? '42px' : (S.combo>=10 ? '50px' : '56px');
    if(elChainBar) elChainBar.style.transform='scaleX('+Math.max(0,Math.min(1,S.comboT))+')';
    let col='#ffd166', nm='GOOD';
    for(const r of CHAINRANK) if(S.combo>=r[0]){ col=r[1]; nm=r[2]; }
    elChainN.style.color=col;
    elChainRank.textContent=nm;
    elChainRank.style.color=col;
  } else elChain.style.opacity='0';
}
function showCombo(){
  elChain.animate([
    {transform:'translateX(-50%) scale(1.5)',filter:'brightness(2.2)'},
    {transform:'translateX(-50%) scale(1)',filter:'brightness(1)'}
  ],{duration:340,easing:'cubic-bezier(.2,1.7,.4,1)'});
  flashDom(.08*QUAL.fxK); fovPunch(3);
}
function hideCombo(){}
let bannerLmT=0;
function banner(t,u,cls,dur){
  const now=performance.now();
  if(cls!=='lm' && now<bannerLmT) return;
  if(cls==='lm') bannerLmT=now+(dur||2800);
  el.banner.classList.toggle('lm',cls==='lm');
  el.banner.querySelector('.t').textContent=t;
  el.banner.querySelector('.u').textContent=u;
  el.banner.animate([{opacity:0,transform:'translateY(16px)'},
    {opacity:1,transform:'translateY(0)',offset:.18},
    {opacity:1,transform:'translateY(0)',offset:.72},
    {opacity:0,transform:'translateY(-14px)'}],{duration:dur||1800,easing:'cubic-bezier(.2,.9,.3,1)'});
}
let flashV=0;
function flashDom(v){ flashV=Math.max(flashV,v*QUAL.fxK); }
function updFlash(dt){
  if(flashV>0){ el.flash.style.opacity=flashV; flashV-=dt*1.6; if(flashV<0) flashV=0; }
  else el.flash.style.opacity=0;
}
/* ══════════ 武器の選択：クイックバー（現在＋直近2つ＋一覧）と一覧シート ══════════ */
const WICON={
  missile:'<svg class="ic" viewBox="0 0 24 24"><path d="M14 3c3 1 5 4 5 8l-4 4-4-4c0-4 1-7 3-8z"/><path d="M11 11l-4 2 2 3-3 3"/><path d="M15 11l4 2-2 3 3 3"/><circle cx="14" cy="8" r="1.3"/></svg>',
  rail:'<svg class="ic" viewBox="0 0 24 24"><path d="M13 2L5 13h6l-1 9 9-12h-6l1-8z"/></svg>',
  cutter:'<svg class="ic" viewBox="0 0 24 24"><path d="M3 20L21 4"/><path d="M8 15l3 3"/><path d="M12 11l3 3"/><path d="M16 7l3 3"/><path d="M3 4l6 6"/></svg>',
  grav:'<svg class="ic" viewBox="0 0 24 24"><circle cx="12" cy="12" r="2.5"/><path d="M12 4a8 8 0 0 1 8 8"/><path d="M12 20a8 8 0 0 1-8-8"/><path d="M17 7a6 6 0 0 1 1 8"/><path d="M7 17a6 6 0 0 1-1-8"/></svg>',
  orbit:'<svg class="ic" viewBox="0 0 24 24"><path d="M12 3v15"/><path d="M8 18h8"/><path d="M6 21h12"/><path d="M9 5h6"/><path d="M4 3h3M17 3h3"/></svg>',
  demo:'<svg class="ic" viewBox="0 0 24 24"><rect x="4" y="12" width="9" height="8" rx="1.5"/><path d="M8.5 12V6"/><path d="M5 6h7"/><path d="M13 16h3l2-5 2 5"/><circle cx="20" cy="18" r="1.2"/></svg>',
  meteor:'<svg class="ic" viewBox="0 0 24 24"><circle cx="15" cy="15" r="5"/><path d="M12.5 12.5L4 4"/><path d="M15 10L10 3"/><path d="M10 15L3 10"/></svg>',
  ball:'<svg class="ic" viewBox="0 0 24 24"><path d="M4 3l8 8"/><circle cx="15" cy="15" r="5.5"/><path d="M6 3h-2v2"/></svg>',
  orb:'<svg class="ic" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4" fill="currentColor"/><circle cx="12" cy="12" r="8"/><path d="M12 1v2M12 21v2M1 12h2M21 12h2"/></svg>',
  nuke:'<svg class="ic" viewBox="0 0 24 24"><circle cx="12" cy="12" r="1.6"/><path d="M12 9.5V3.5a8.5 8.5 0 0 1 7.4 4.3L14.2 11"/><path d="M9.8 11L4.6 7.8A8.5 8.5 0 0 1 12 3.5"/><path d="M14.2 13l5.2 3.2A8.5 8.5 0 0 1 12 20.5v-6"/><path d="M9.8 13l-5.2 3.2A8.5 8.5 0 0 1 4.6 7.8"/></svg>',
};
const FIRE_LBL={missile:['FIRE','押しながらドラッグで照準'],rail:['FIRE','長押しで照射'],cutter:['CUT','ドラッグで切断線'],
  grav:['FIRE','特異点を置く'],orbit:['FIRE','上空から照射'],demo:['SET','装薬を設置'],meteor:['FIRE','隕石を呼ぶ'],
  ball:['FIRE','鉄球を撃ち込む'],orb:['FIRE','破壊球 ／ 加点なし'],nuke:['FIRE','戦術核 ／ 加点なし']};
let recentW=['rail','cutter'];
const qbar=document.getElementById('qbar'), wgrid=document.getElementById('wgrid');
function wBtn(w,cls){
  const b=document.createElement('button');
  b.className=cls+(w.id===wpn?' sel':'')+((w.id==='orb'||w.id==='nuke')?' nosc':'');
  b.dataset.w=w.id;
  b.innerHTML='<div class="ic">'+WICON[w.id]+'</div><div class="n">'+w.n+'</div>';
  return b;
}
function renderQuickBar(){
  qbar.innerHTML='';
  const cur=WPN.find(w=>w.id===wpn);
  const ids=[cur.id].concat(recentW.filter(id=>id!==cur.id)).slice(0,3);
  for(const id of ids){ const w=WPN.find(x=>x.id===id); if(!w) continue; const b=wBtn(w,'q'); b.addEventListener('click',e=>{ e.stopPropagation(); selW(w.id,true); }); qbar.appendChild(b); }
  const L=document.createElement('button'); L.className='q list';
  L.innerHTML='<div class="ic"><svg class="ic" viewBox="0 0 24 24"><rect x="3" y="4" width="7" height="7" rx="1.5"/><rect x="14" y="4" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg></div><div class="n">武器一覧</div>';
  L.addEventListener('click',e=>{ e.stopPropagation(); openSheet(); });
  qbar.appendChild(L);
}
function renderSheet(){
  wgrid.innerHTML='';
  WPN.forEach(w=>{ const b=wBtn(w,'w'); b.addEventListener('click',e=>{ e.stopPropagation(); selW(w.id,true); closeSheet(); }); wgrid.appendChild(b); });
  const W=WPN.find(w=>w.id===wpn);
  el.wdesc.innerHTML='<b>'+W.n+'</b>　'+W.d;
}
function openSheet(){ releasePointers(); renderSheet(); document.getElementById('wsheet').classList.add('on'); }
function closeSheet(){ document.getElementById('wsheet').classList.remove('on'); }
let toastT=null;
function wToast(html,ms){
  el.toast.innerHTML=html; el.toast.classList.add('on');
  if(toastT) clearTimeout(toastT);
  toastT=setTimeout(()=>el.toast.classList.remove('on'),ms||2600);
}
function selW(id,fromUser){
  const prev=wpn;
  if(prev!==id){ recentW=[prev].concat(recentW.filter(x=>x!==prev&&x!==id)).slice(0,2); }
  wpn=id; cd=Math.min(cd,.2);
  const W=WPN.find(w=>w.id===id);
  const F=FIRE_LBL[id]||['FIRE',''];
  el.fireLbl.textContent=F[0]; el.fireSub.textContent=F[1];
  el.fire.classList.toggle('cut',!!W.swipe);
  el.xh.classList.toggle('cut',false);
  renderQuickBar();
  if(fromUser) wToast('<b style="color:var(--cyan)">'+W.n+'</b>　'+W.d);
  Snd.kick();
  updWeaponUI();
}
function updWeaponUI(){
  const cool=cd>0;
  el.fire.classList.toggle('cool',cool);
  if(cool){
    const k=Math.max(0,Math.min(1,1-cd/cdMax));
    el.fire.style.background='conic-gradient(rgba(255,61,127,.55) '+(k*360).toFixed(0)+'deg, rgba(255,61,127,.08) 0)';
  } else el.fire.style.background='';
  const q=qbar.firstElementChild;
  if(q){ q.classList.toggle('cool',cool); q.style.setProperty('--cd',cool?((cd/cdMax)*100).toFixed(0)+'%':'0%'); }
}
/* ══════════ 入力：指ごとの所有権を pointerId で管理する ══════════
   役割：stick（移動）／look（視点）／fire（発射。押しながら視点も動かせる）／cut（カッターの切断線）／alt（高度）
   pointercancel・キャプチャ喪失・メニュー表示では「攻撃確定」せず、安全に解除する */
const stickEl=document.getElementById('stick'), stickIn=stickEl.querySelector('i');
const cutLineEl=document.getElementById('cutline');
const PTR=new Map();
let stickC={x:0,y:0};
let fireHeld=false, fireId=null;
let btnUp=false, btnDn=false;
function hasRole(r){ for(const p of PTR.values()) if(p.role===r) return true; return false; }
function uiBlocked(){ return paused || resultOn || document.getElementById('pmenu').classList.contains('on') || document.getElementById('wsheet').classList.contains('on'); }
function showCutLine(x1,y1,x2,y2){
  const dx=x2-x1, dy=y2-y1;
  cutLineEl.style.opacity='1';
  cutLineEl.style.left=x1+'px'; cutLineEl.style.top=y1+'px';
  cutLineEl.style.width=Math.hypot(dx,dy)+'px';
  cutLineEl.style.transform='rotate('+Math.atan2(dy,dx)+'rad)';
}
function hideCutLine(){ cutLineEl.style.opacity='0'; cutLineEl.style.width='0px'; }
function setAlt(){ inp.up = btnUp?1:(btnDn?-1:0);
  document.getElementById('bUp').classList.toggle('on',btnUp); document.getElementById('bDn').classList.toggle('on',btnDn); }
function resetStick(){ inp.fwd=0; inp.side=0; inp.boost=0; stickIn.style.transform='translate(0,0)'; stickEl.classList.remove('on'); stickEl.classList.remove('boost'); }
function moveStick(e){
  const dx=e.clientX-stickC.x, dy=e.clientY-stickC.y;
  const d=Math.min(50,Math.hypot(dx,dy)), a=Math.atan2(dy,dx);
  const nx=Math.cos(a)*d, ny=Math.sin(a)*d;
  stickIn.style.transform='translate('+nx+'px,'+ny+'px)';
  // 中心付近は不感帯：止めたい時にすぐ止まる。外周は高速移動
  const k=d<7?0:(d-7)/43;
  inp.side=k*Math.cos(a); inp.fwd=-k*Math.sin(a);
  inp.boost = d>45;
  stickEl.classList.toggle('boost',inp.boost);
}
/* カッターの切断線：主操作ボタンから引いた指の動きを、照準を中心にした線として描く */
function cutPts(p){
  const cx=window.innerWidth/2, cy=window.innerHeight/2;
  const dx=p.x-p.x0, dy=p.y-p.y0;
  return {ax:cx-dx/2, ay:cy-dy/2, bx:cx+dx/2, by:cy+dy/2, len:Math.hypot(dx,dy)};
}
function endPtr(id,p,cancelled){
  if(!p) return;
  if(p.role==='stick') resetStick();
  else if(p.role==='fire'){ if(fireId===id){ fireHeld=false; fireId=null; } el.fire.classList.remove('on'); }
  else if(p.role==='cut'){
    el.fire.classList.remove('on'); hideCutLine(); el.xh.classList.remove('cut');
    if(!cancelled && cd<=0 && canShoot()){
      const c=cutPts(p);
      cd=WPN.find(w=>w.id===wpn).cd; cdMax=Math.max(.001,cd); S.shots++; noteShot(); Snd.kick();
      if(c.len>26) doCut(camera.position, screenRay(c.ax,c.ay), screenRay(c.bx,c.by));
      else { // 短いタップ：照準の高さで水平に断つ
        const dir=new THREE.Vector3(); camera.getWorldDirection(dir);
        const ca=Math.cos(-.30), sa=Math.sin(-.30), cb=Math.cos(.30), sb=Math.sin(.30);
        doCut(camera.position,[dir.x*ca-dir.z*sa, dir.y, dir.x*sa+dir.z*ca],[dir.x*cb-dir.z*sb, dir.y, dir.x*sb+dir.z*cb]);
      }
      updWeaponUI();
    }
  }
  else if(p.role==='altUp'){ btnUp=false; setAlt(); }
  else if(p.role==='altDn'){ btnDn=false; setAlt(); }
}
function releasePointers(){
  for(const [id,p] of PTR) endPtr(id,p,true);
  PTR.clear();
  resetStick(); fireHeld=false; fireId=null; btnUp=false; btnDn=false; setAlt(); hideCutLine();
  el.fire.classList.remove('on'); el.xh.classList.remove('cut');
}
function onDown(e){
  if(uiBlocked()) return;
  const t=e.target;
  if(t.closest && t.closest('button,.ov,#qbar,#alt,#fire,#det,#bPause')) return;
  if(PTR.has(e.pointerId)) return;
  const r=stickEl.getBoundingClientRect();
  const inStick = e.clientX>=r.left-36 && e.clientX<=r.right+36 && e.clientY>=r.top-36 && e.clientY<=r.bottom+36;
  if(inStick && !hasRole('stick')){
    stickC={x:r.left+r.width/2, y:r.top+r.height/2};
    PTR.set(e.pointerId,{role:'stick'}); stickEl.classList.add('on'); moveStick(e); return;
  }
  if(!hasRole('look')){ PTR.set(e.pointerId,{role:'look',x:e.clientX,y:e.clientY}); }
}
function lookDelta(p,e){
  const dx=e.clientX-p.x, dy=e.clientY-p.y;
  p.x=e.clientX; p.y=e.clientY;
  const sens=.0042*(430/Math.max(320,Math.min(window.innerWidth,window.innerHeight)));
  cam.yaw-=dx*sens;
  cam.pitch=Math.max(-1.45,Math.min(1.45,cam.pitch-dy*sens));
}
function onMove(e){
  const p=PTR.get(e.pointerId); if(!p) return;
  if(p.role==='stick') moveStick(e);
  else if(p.role==='look') lookDelta(p,e);
  else if(p.role==='fire'){ if(!hasRole('look')) lookDelta(p,e); }      // 押しながらドラッグで照準
  else if(p.role==='cut'){ p.x=e.clientX; p.y=e.clientY; const c=cutPts(p); if(c.len>26){ showCutLine(c.ax,c.ay,c.bx,c.by); el.xh.classList.add('cut'); } else { hideCutLine(); el.xh.classList.remove('cut'); } }
}
function onUp(e){ const p=PTR.get(e.pointerId); if(!p) return; PTR.delete(e.pointerId); endPtr(e.pointerId,p,false); }
function onCancel(e){ const p=PTR.get(e.pointerId); if(!p) return; PTR.delete(e.pointerId); endPtr(e.pointerId,p,true); }
let _sndUnlocked=false;
window.addEventListener('pointerdown',function(){
  if(_sndUnlocked) return;
  _sndUnlocked=true;
  Snd.kick();                     // 最初のタッチで AudioContext を起こしておく
},{capture:true});
window.addEventListener('pointerdown',onDown);
window.addEventListener('pointermove',onMove,{passive:true});
window.addEventListener('pointerup',onUp);
window.addEventListener('pointercancel',onCancel);
window.addEventListener('lostpointercapture',e=>{ const p=PTR.get(e.pointerId); if(p&&(p.role==='fire'||p.role==='cut'||p.role==='altUp'||p.role==='altDn')){ /* 指が離れた時も lostpointercapture が来るので、up/cancel 側で処理する */ } });
window.addEventListener('blur',()=>releasePointers());
const fb=document.getElementById('fire');
fb.addEventListener('pointerdown',e=>{
  e.stopPropagation(); e.preventDefault();
  if(uiBlocked()||PTR.has(e.pointerId)) return;
  try{ fb.setPointerCapture(e.pointerId); }catch(err){}
  const W=WPN.find(w=>w.id===wpn);
  el.fire.classList.add('on');
  if(W.swipe){ PTR.set(e.pointerId,{role:'cut',x0:e.clientX,y0:e.clientY,x:e.clientX,y:e.clientY}); return; }
  PTR.set(e.pointerId,{role:'fire',x:e.clientX,y:e.clientY});
  fireId=e.pointerId; fireHeld=true;
  if(!W.cont) fireWeapon();
});
fb.addEventListener('contextmenu',e=>e.preventDefault());
const bu=document.getElementById('bUp'), bd=document.getElementById('bDn');
bu.addEventListener('pointerdown',e=>{ e.stopPropagation(); e.preventDefault(); if(uiBlocked()) return; try{ bu.setPointerCapture(e.pointerId); }catch(err){} PTR.set(e.pointerId,{role:'altUp'}); btnUp=true; setAlt(); });
bd.addEventListener('pointerdown',e=>{ e.stopPropagation(); e.preventDefault(); if(uiBlocked()) return; try{ bd.setPointerCapture(e.pointerId); }catch(err){} PTR.set(e.pointerId,{role:'altDn'}); btnDn=true; setAlt(); });
const detB=document.getElementById('det');
detB.addEventListener('pointerdown',e=>{ e.stopPropagation(); e.preventDefault(); if(uiBlocked()) return; detB.classList.add('hot'); setTimeout(()=>detB.classList.remove('hot'),200); blowCharges(); });
document.getElementById('wClose').addEventListener('click',e=>{ e.stopPropagation(); closeSheet(); });
document.getElementById('wsheet').addEventListener('click',e=>{ if(e.target.id==='wsheet') closeSheet(); });
/* ══════════ ポーズメニュー ══════════ */
const pmenu=document.getElementById('pmenu');
function openMenu(reason){
  releasePointers(); closeSheet();
  setPaused(true,reason||'menu');
  renderMenu();
  pmenu.classList.add('on');
}
function closeMenu(){ pmenu.classList.remove('on'); setPaused(false); }
onPauseChange=(v,reason)=>{ if(v && !pmenu.classList.contains('on') && !resultOn){ renderMenu(); pmenu.classList.add('on'); } };
function renderMenu(){
  document.getElementById('bSnd').textContent=S.sound?'🔊 音':'🔇 音 OFF';
  document.getElementById('bSnd').classList.toggle('on',S.sound);
  const bh=document.getElementById('bHap'); bh.textContent=hapticOn?'振動':'振動 OFF'; bh.classList.toggle('on',hapticOn);
  document.getElementById('bFx').textContent='演出: '+(QUAL.fxK<1?'控えめ':'標準');
  document.getElementById('bPerf').classList.toggle('on',QUAL.showPerf);
  updQualLabel();
  const pm=document.getElementById('pmModes'); pm.innerHTML='';
  MODES.forEach(M=>{ const b=document.createElement('button'); b.className='pb'+(M.id===MODE?' on':''); b.textContent=M.n;
    b.title=M.d; b.addEventListener('click',e=>{ e.stopPropagation(); setMode(M.id); genCity(MAPID,citySeed); spawnOverview(); closeMenu(); banner(M.n+'モード',M.lbl); wToast(M.d); }); pm.appendChild(b); });
  const pp=document.getElementById('pmMaps'); pp.innerHTML='';
  MAPNAMES.forEach((n,i)=>{ const b=document.createElement('button'); b.className='pb'+(i===MAPID?' on':''); b.textContent=n;
    b.addEventListener('click',e=>{ e.stopPropagation(); genCity(i); spawnOverview(); closeMenu(); banner(MAPNAMES[MAPID],''); }); pp.appendChild(b); });
  document.getElementById('pmSeed').textContent='SEED '+citySeed+'　·　'+MAPNAMES[MAPID]+'　·　'+modeDef().lbl;
}
document.getElementById('bPause').addEventListener('click',e=>{ e.stopPropagation(); if(resultOn) return; if(pmenu.classList.contains('on')) closeMenu(); else openMenu('menu'); });
document.getElementById('pmClose').addEventListener('click',e=>{ e.stopPropagation(); closeMenu(); });
document.getElementById('pmResume').addEventListener('click',e=>{ e.stopPropagation(); closeMenu(); });
document.getElementById('bSnd').addEventListener('click',e=>{ e.stopPropagation(); S.sound=!S.sound; if(!S.sound) Snd.pause(); renderMenu(); if(S.sound) Snd.kick(); });
document.getElementById('bHap').addEventListener('click',e=>{ e.stopPropagation(); hapticOn=!hapticOn; renderMenu(); if(hapticOn) hap(HAP.hit,0); });
document.getElementById('bQual').addEventListener('click',e=>{ e.stopPropagation(); const order=['auto','high','mid','low'], i=order.indexOf(QUAL.mode); setQuality(order[(i+1)%order.length]); renderMenu(); });
document.getElementById('bFx').addEventListener('click',e=>{ e.stopPropagation(); QUAL.fxK=QUAL.fxK<1?1:0.5; try{ localStorage.setItem('tt2_fx',String(QUAL.fxK)); }catch(err){} renderMenu(); });
document.getElementById('bPerf').addEventListener('click',e=>{ e.stopPropagation(); QUAL.showPerf=!QUAL.showPerf; document.getElementById('perf').classList.toggle('on',QUAL.showPerf); renderMenu(); });
document.getElementById('bHint').addEventListener('click',e=>{ e.stopPropagation(); closeMenu(); showHint(true); });
document.getElementById('pmRetry').addEventListener('click',e=>{ e.stopPropagation(); genCity(MAPID,citySeed); spawnOverview(); closeMenu(); banner('再挑戦','SAME CITY'); });
document.getElementById('pmNew').addEventListener('click',e=>{ e.stopPropagation(); genCity(MAPID); spawnOverview(); closeMenu(); banner('新しい街','NEW CITY'); });
document.getElementById('rAgain').addEventListener('click',e=>{ e.stopPropagation(); hideResult(); genCity(MAPID,citySeed); spawnOverview(); });
document.getElementById('rNewCity').addEventListener('click',e=>{ e.stopPropagation(); hideResult(); genCity(MAPID); spawnOverview(); });
document.getElementById('rNext').addEventListener('click',e=>{ e.stopPropagation(); hideResult(); genCity(MAPID+1); banner(MAPNAMES[MAPID],''); spawnOverview(); });
onCtxLost=(lost)=>{ const o=document.getElementById('ctxov'); o.classList.toggle('on',lost);
  const rb=document.getElementById('ctxReload'); rb.style.display='none';
  if(lost) setTimeout(()=>{ if(ctxLost) rb.style.display=''; },3000); };
document.getElementById('ctxReload').addEventListener('click',()=>location.reload());
/* 初回だけ短い操作ヒント */
let hintT=null;
function showHint(force){
  let seen=false; try{ seen=!!localStorage.getItem('tt2_hint'); }catch(e){}
  if(seen&&!force) return;
  try{ localStorage.setItem('tt2_hint','1'); }catch(e){}
  const h=document.getElementById('hint');
  h.innerHTML='左下 <b>スティック</b>＝移動（外周で高速）　画面 <b>ドラッグ</b>＝視点<br>右下 <b>FIRE</b>＝発射（押しながらドラッグで照準）　▲▼＝高度';
  h.classList.add('on');
  if(hintT) clearTimeout(hintT);
  hintT=setTimeout(()=>h.classList.remove('on'),7000);
}
// キーボード（PC）
const keys={};
window.addEventListener('keydown',e=>{
  keys[e.code]=1;
  if(e.code==='Escape'){ if(pmenu.classList.contains('on')) closeMenu(); else if(!resultOn) openMenu('menu'); }
  if(uiBlocked()) return;
  if(e.code==='Space'){ e.preventDefault(); fireHeld=true;
    const W=WPN.find(w=>w.id===wpn); if(!W.cont && cd<=0) fireWeapon(); }
  const n=parseInt(e.key,10);
  if(n>=1&&n<=WPN.length) selW(WPN[n-1].id,true);
  if(e.code==='Digit0') selW(WPN[9].id,true);
  if(e.code==='KeyX') blowCharges();
});
window.addEventListener('keyup',e=>{ keys[e.code]=0; if(e.code==='Space') fireHeld=false; });
function readKeys(){
  if(hasRole('stick')) return;
  const f=(keys.KeyW||keys.ArrowUp?1:0)-(keys.KeyS||keys.ArrowDown?1:0), s=(keys.KeyD||keys.ArrowRight?1:0)-(keys.KeyA||keys.ArrowLeft?1:0);
  if(f||s||keys._any){ inp.fwd=f; inp.side=s; keys._any=(f||s)?1:0; }
  if(!btnUp && !btnDn) inp.up=(keys.KeyE?1:0)-(keys.KeyQ?1:0);
  if(keys.ShiftLeft!==undefined) inp.boost=keys.ShiftLeft?1:inp.boost&&0;
}
