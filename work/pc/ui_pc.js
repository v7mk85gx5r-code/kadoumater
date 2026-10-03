/* ══════════ HUD ══════════
   PC版：上段＝数値、中央＝照準、下段＝武器バー・ミニマップ・キーヒント。
   操作はキーボードだけで完結し、マウスとゲームパッドは任意で重ねられる */
const el={
  bld:document.getElementById('kBld'), chunk:document.getElementById('kChunk'),
  fill:document.getElementById('dmgFill'), num:document.getElementById('dmgNum'),
  banner:document.getElementById('banner'), dist:document.getElementById('xhDist'), tgt:document.getElementById('xhTgt'),
  wdesc:document.getElementById('wdesc'), flash:document.getElementById('flash'), cause:document.getElementById('cause'),
  xh:document.getElementById('xh'), toast:document.getElementById('wtoast'), hud:document.getElementById('hud'),
  keyhint:document.getElementById('keyhint'), xhCd:document.getElementById('xhCd'), modeTag:document.getElementById('modeTag'),
};
const clampN=(v,a,b)=>Math.max(a,Math.min(b,v));
const STYLE_NAME={zakkyo:'雑居ビル',shop:'商店ビル',apart:'マンション',office:'オフィスビル',tower:'高層ビル',car:'駐車車両',
  pole:'電柱',tree:'街路樹',gate:'アーチ',toho:'新宿東宝ビル',trafo:'変圧器',rail:'高架',hardened:'耐爆構造ビル',park:'公園',
  water:'給水塔',tank:'タンク',gov:'庁舎',hall:'ホール',station:'駅'};
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
let hudT=0, mmT=0;
function updHUD(dt){
  mmT+=dt; if(mmT>.15){ mmT=0; drawMinimap(); }
  hudT+=dt; if(hudT<.1) return; hudT=0;
  let p=Math.min(100,killedVox/totalVox*100);
  let restVox=0, alive=0;
  for(let k=0;k<blds.length;k++){ const b=blds[k]; restVox+=b.live; if(b.live>0&&b.style!=='pole'&&b.style!=='car'&&b.style!=='tree') alive++; }
  if(restVox>0) p=Math.min(p,99.9); else p=100;
  el.bld.textContent=alive;
  el.chunk.textContent=chunks.length;
  el.fill.style.width=p+'%';
  el.num.innerHTML=p.toFixed(1)+'<small>%</small>';
  const h=aimRay();
  if(h.miss){ el.dist.textContent='—'; el.dist.style.color=''; el.tgt.textContent=''; }
  else {
    if(wpn==='missile'||wpn==='carpet'){ el.dist.textContent='◈ LOCK  '+Math.round(h.d)+' m'; el.dist.style.color='#ff5a6a'; }
    else { el.dist.textContent=Math.round(h.d)+' m'; el.dist.style.color=''; }
    el.tgt.textContent=targetLabel(h);
  }
  if(el.modeTag) el.modeTag.textContent=modeDef().lbl;
}
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
const TON_PER_VOX=2.6;
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
  d.style.fontSize=(big?30:mid?23:(v>4000?18:14))+'px';
  d.style.color= big?'#fff' : mid?'#ffd98a' : (v>4000?'#ffb03a':'#e6b98a');
  d.style.textShadow = big
    ? '0 0 22px rgba(255,190,60,1),0 0 48px rgba(255,90,31,.8),0 2px 0 rgba(0,0,0,.7)'
    : '0 0 12px rgba(255,176,58,.7),0 2px 0 rgba(0,0,0,.6)';
  d.innerHTML='+'+fmtTon(v);
  popSlot=(popSlot+1)%7;
  d.style.top=(popSlot*15)+'px';
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
    elChainN.style.fontSize = S.combo>=100 ? '50px' : (S.combo>=10 ? '60px' : '68px');
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
/* ══════════ 武器の選択：下段の武器バー（13枠・キー表示）と一覧パネル ══════════ */
const WICON={
  missile:'<svg class="ic" viewBox="0 0 24 24"><path d="M14 3c3 1 5 4 5 8l-4 4-4-4c0-4 1-7 3-8z"/><path d="M11 11l-4 2 2 3-3 3"/><path d="M15 11l4 2-2 3 3 3"/><circle cx="14" cy="8" r="1.3"/></svg>',
  gun:'<svg class="ic" viewBox="0 0 24 24"><path d="M3 10h13l3-2v4l-3 2H9l-1 5H5l1-5H3z"/><path d="M16 10v2"/><path d="M19 8l2-1"/></svg>',
  rail:'<svg class="ic" viewBox="0 0 24 24"><path d="M13 2L5 13h6l-1 9 9-12h-6l1-8z"/></svg>',
  cutter:'<svg class="ic" viewBox="0 0 24 24"><path d="M3 20L21 4"/><path d="M8 15l3 3"/><path d="M12 11l3 3"/><path d="M16 7l3 3"/><path d="M3 4l6 6"/></svg>',
  carpet:'<svg class="ic" viewBox="0 0 24 24"><path d="M2 9l10-5 10 5-10 5z"/><path d="M6 14v3M12 15v4M18 14v3"/><circle cx="6" cy="19" r="1"/><circle cx="12" cy="21" r="1"/><circle cx="18" cy="19" r="1"/></svg>',
  incend:'<svg class="ic" viewBox="0 0 24 24"><path d="M12 3c1 3 4 4 4 8a4 4 0 0 1-8 0c0-2 1-3 1-5 1 1 2 2 3-3z"/><path d="M4 21h16"/><path d="M7 21c0-3 2-5 5-5s5 2 5 5"/></svg>',
  grav:'<svg class="ic" viewBox="0 0 24 24"><circle cx="12" cy="12" r="2.5"/><path d="M12 4a8 8 0 0 1 8 8"/><path d="M12 20a8 8 0 0 1-8-8"/><path d="M17 7a6 6 0 0 1 1 8"/><path d="M7 17a6 6 0 0 1-1-8"/></svg>',
  orbit:'<svg class="ic" viewBox="0 0 24 24"><path d="M12 3v15"/><path d="M8 18h8"/><path d="M6 21h12"/><path d="M9 5h6"/><path d="M4 3h3M17 3h3"/></svg>',
  demo:'<svg class="ic" viewBox="0 0 24 24"><rect x="4" y="12" width="9" height="8" rx="1.5"/><path d="M8.5 12V6"/><path d="M5 6h7"/><path d="M13 16h3l2-5 2 5"/><circle cx="20" cy="18" r="1.2"/></svg>',
  meteor:'<svg class="ic" viewBox="0 0 24 24"><circle cx="15" cy="15" r="5"/><path d="M12.5 12.5L4 4"/><path d="M15 10L10 3"/><path d="M10 15L3 10"/></svg>',
  ball:'<svg class="ic" viewBox="0 0 24 24"><path d="M4 3l8 8"/><circle cx="15" cy="15" r="5.5"/><path d="M6 3h-2v2"/></svg>',
  orb:'<svg class="ic" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4" fill="currentColor"/><circle cx="12" cy="12" r="8"/><path d="M12 1v2M12 21v2M1 12h2M21 12h2"/></svg>',
  nuke:'<svg class="ic" viewBox="0 0 24 24"><circle cx="12" cy="12" r="1.6"/><path d="M12 9.5V3.5a8.5 8.5 0 0 1 7.4 4.3L14.2 11"/><path d="M9.8 11L4.6 7.8A8.5 8.5 0 0 1 12 3.5"/><path d="M14.2 13l5.2 3.2A8.5 8.5 0 0 1 12 20.5v-6"/><path d="M9.8 13l-5.2 3.2A8.5 8.5 0 0 1 4.6 7.8"/></svg>',
};
const WKEYS=['1','2','3','4','5','6','7','8','9','0','-','^','¥'];
const KEYCODE_W={Digit1:0,Digit2:1,Digit3:2,Digit4:3,Digit5:4,Digit6:5,Digit7:6,Digit8:7,Digit9:8,Digit0:9,Minus:10,Equal:11,Backslash:12,IntlYen:12};
const WHINT={missile:'発射：<kbd>Space</kbd>（連打可）',gun:'連射：<kbd>Space</kbd> 長押し（撃ち続けると散る）',rail:'照射：<kbd>Space</kbd> 長押し',
  cutter:'<kbd>Space</kbd> を押したまま <kbd>↑↓←→</kbd>（またはマウス）で線を引き、離して切断。押すだけで水平切り',
  carpet:'投下：<kbd>Space</kbd>　照準の向きへ9発が歩く',incend:'投擲：<kbd>Space</kbd>　着弾点が火の海になる',
  grav:'設置：<kbd>Space</kbd>',orbit:'照射：<kbd>Space</kbd>',demo:'設置：<kbd>Space</kbd>（最大16）　起爆：<kbd>X</kbd>',
  meteor:'落下：<kbd>Space</kbd>',ball:'発射：<kbd>Space</kbd>　当たった方向へ倒れる',orb:'投下：<kbd>Space</kbd>（加点なし）',nuke:'投下：<kbd>Space</kbd>（加点なし）'};
const wbar=document.getElementById('wbar'), wgrid=document.getElementById('wgrid');
function curW(){ return WPN.find(w=>w.id===wpn)||WPN[0]; }
function wSlot(w,i,cls){
  const b=document.createElement('button');
  b.className=cls+(w.id===wpn?' sel':'')+((w.id==='orb'||w.id==='nuke')?' nosc':'');
  b.dataset.w=w.id; b.id=cls+'_'+w.id;
  b.innerHTML='<span class="k">'+WKEYS[i]+'</span><div class="ic">'+WICON[w.id]+'</div><div class="n">'+w.n+'</div>';
  return b;
}
function renderWBar(){
  wbar.innerHTML='';
  WPN.forEach((w,i)=>{ const b=wSlot(w,i,'q'); b.addEventListener('click',e=>{ e.stopPropagation(); if(uiBlocked()) return; selW(w.id,true); }); wbar.appendChild(b); });
}
function renderPanel(){
  wgrid.innerHTML='';
  WPN.forEach((w,i)=>{ const b=wSlot(w,i,'w'); b.addEventListener('click',e=>{ e.stopPropagation(); selW(w.id,true); closePanel(); }); wgrid.appendChild(b); });
  showWDesc(curW());
}
function showWDesc(W){ el.wdesc.innerHTML='<b>'+W.n+'</b>　'+W.d; }
const wpanel=document.getElementById('wpanel');
function panelOpen(){ return wpanel.classList.contains('on'); }
function openPanel(){ if(panelOpen()) return; releasePointers(); renderPanel(); wpanel.classList.add('on'); knavOpen(wpanel,'w_'+wpn); }
function closePanel(){ if(!panelOpen()) return; wpanel.classList.remove('on'); if(KNAV.root===wpanel) knavClose(); }
let toastT=null;
function wToast(html,ms){
  el.toast.innerHTML=html; el.toast.classList.add('on');
  if(toastT) clearTimeout(toastT);
  toastT=setTimeout(()=>el.toast.classList.remove('on'),ms||2600);
}
function selW(id,fromUser){
  if(!WPN.find(w=>w.id===id)) return;
  if(CUT.on) cancelCut();
  wpn=id; cd=Math.min(cd,.2);
  const W=curW();
  el.xh.classList.toggle('cutw',!!W.swipe);
  renderWBar();
  if(fromUser) wToast('<b style="color:var(--cyan)">'+W.n+'</b>　'+W.d);
  Snd.kick();
  updWeaponUI(); updKeyHint();
}
function updWeaponUI(){
  const cool=cd>0;
  const q=wbar.querySelector('.q.sel');
  if(q){ q.classList.toggle('cool',cool); q.style.setProperty('--cd',cool?((cd/cdMax)*100).toFixed(0)+'%':'0%'); }
  if(el.xhCd){ el.xhCd.style.opacity=cool?'.9':'0'; el.xhCd.style.transform='scaleX('+(cool?Math.max(0,1-cd/cdMax).toFixed(3):0)+')'; }
}
function cycleW(dir){ const i=WPN.findIndex(w=>w.id===wpn); selW(WPN[(i+dir+WPN.length)%WPN.length].id,true); }
function updKeyHint(){
  const W=curW();
  el.keyhint.innerHTML='<b>'+W.n+'</b>　'+(WHINT[W.id]||'')+'<br><span>WASD 移動　↑↓←→ 視点　E/Q 上下　Shift 加速　Z/C 武器　Tab 一覧　V ズーム　T 俯瞰　Esc メニュー'+(PAD.on?'　🎮 パッド有効':'')+'</span>';
}
/* ══════════ 設定（端末に保存） ══════════ */
const PCS={q:'auto',scale:1,fov:75,sens:5,invY:false,ao:true,snd:true,fx:1,hud:true};
function loadPCS(){ try{ const o=JSON.parse(localStorage.getItem('tt_pc_v1')||'null'); if(o&&typeof o==='object') Object.assign(PCS,o); }catch(e){} }
function savePCS(){ try{ localStorage.setItem('tt_pc_v1',JSON.stringify(PCS)); }catch(e){} }
function applyPCS(){
  loadPCS();
  PCS.scale=clampN(+PCS.scale||1,.5,2); PCS.fov=clampN(+PCS.fov||75,55,110); PCS.sens=clampN((+PCS.sens||5)|0,1,10);
  resScale=PCS.scale; aoUser=!!PCS.ao; fovUser=PCS.fov; S.sound=!!PCS.snd; QUAL.fxK=PCS.fx<1?.5:1;
  PCS.hud=true; el.hud.classList.remove('off');
  if(window.TT_QUALITY) applyLevel(QUAL.level,true); else setQuality(['auto','ultra','high','mid','low'].includes(PCS.q)?PCS.q:'auto');
  renderWBar(); updKeyHint();
}
function renderQualUI(){ if(pmenu.classList.contains('on')) renderMenu(); }
/* ══════════ 入力 ══════════
   役割：キーボード（主）・マウス（任意：ポインタロック、使えない時はドラッグ）・ゲームパッド（任意）。
   どの入力も fireDown/fireUp・lookPx・inp に集約する。メニュー表示・ポーズ・ロック喪失では攻撃を確定させず安全に解除する */
const keys={};
const CUT={on:false,x:0,y:0};
const PTR=new Map();
let fireHeld=false, fireSrc=null, zoomHeld=false, zoomToggle=false;
let titleOn=false, keysOn=false, titleShown=false;
const KEYLOOK_PX=1050, CUT_PX=720, PADLOOK_PX=1400;
const pmenu=document.getElementById('pmenu'), titleEl=document.getElementById('title'), keysEl=document.getElementById('keys'), resultEl=document.getElementById('result');
const cutLineEl=document.getElementById('cutline');
function menuOpen(){ return pmenu.classList.contains('on'); }
function uiBlocked(){ return booting || paused || resultOn || titleOn || menuOpen() || panelOpen() || keysOn; }
function topOverlay(){
  if(keysOn) return keysEl;
  if(panelOpen()) return wpanel;
  if(menuOpen()) return pmenu;
  if(titleOn) return titleEl;
  if(resultOn && resultEl.classList.contains('on')) return resultEl;
  return null;
}
function closeTop(){
  const ov=topOverlay();
  if(ov===titleEl){ openMenu('menu'); return; }        // タイトルでは Esc＝設定・マップ・モード
  if(ov===keysEl) closeKeys();
  else if(ov===wpanel) closePanel();
  else if(ov===pmenu) closeMenu();
}
function sensRad(){ return 0.0022*(PCS.sens/5)*(fovBase()/fovUser); }
function lookPx(dx,dy){
  if(CUT.on){ CUT.x+=dx; CUT.y+=dy; updCutPreview(); return; }
  const s=sensRad();
  cam.yaw-=dx*s;
  cam.pitch=clampN(cam.pitch-dy*s*(PCS.invY?-1:1),-1.45,1.45);
}
function showCutLine(x1,y1,x2,y2){
  const dx=x2-x1, dy=y2-y1;
  cutLineEl.style.opacity='1';
  cutLineEl.style.left=x1+'px'; cutLineEl.style.top=y1+'px';
  cutLineEl.style.width=Math.hypot(dx,dy)+'px';
  cutLineEl.style.transform='rotate('+Math.atan2(dy,dx)+'rad)';
}
function hideCutLine(){ cutLineEl.style.opacity='0'; cutLineEl.style.width='0px'; }
function cutPts(){ const cx=window.innerWidth/2, cy=window.innerHeight/2; return {ax:cx-CUT.x/2, ay:cy-CUT.y/2, bx:cx+CUT.x/2, by:cy+CUT.y/2, len:Math.hypot(CUT.x,CUT.y)}; }
function updCutPreview(){ const c=cutPts(); if(c.len>26){ showCutLine(c.ax,c.ay,c.bx,c.by); el.xh.classList.add('cut'); } else { hideCutLine(); el.xh.classList.remove('cut'); } }
function cancelCut(){ CUT.on=false; CUT.x=0; CUT.y=0; hideCutLine(); el.xh.classList.remove('cut'); }
function fireDown(src){
  if(uiBlocked()||fireHeld) return;
  fireHeld=true; fireSrc=src;
  const W=curW();
  if(W.swipe){ CUT.on=true; CUT.x=0; CUT.y=0; el.xh.classList.add('cut'); return; }
  if(!W.cont && cd<=0) fireWeapon();
}
function fireUp(cancelled){
  if(!fireHeld){ if(CUT.on) cancelCut(); return; }
  fireHeld=false; fireSrc=null;
  if(CUT.on){
    const c=cutPts(); CUT.on=false; hideCutLine(); el.xh.classList.remove('cut');
    if(!cancelled && cd<=0 && canShoot() && curW().swipe) execCut(c);
    CUT.x=0; CUT.y=0;
  }
}
function execCut(c){
  cd=curW().cd; cdMax=Math.max(.001,cd); S.shots++; noteShot(); Snd.kick();
  if(c.len>26) doCut(camera.position, screenRay(c.ax,c.ay), screenRay(c.bx,c.by));
  else {
    const dir=new THREE.Vector3(); camera.getWorldDirection(dir);
    const ca=Math.cos(-.30), sa=Math.sin(-.30), cb=Math.cos(.30), sb=Math.sin(.30);
    doCut(camera.position,[dir.x*ca-dir.z*sa, dir.y, dir.x*sa+dir.z*ca],[dir.x*cb-dir.z*sb, dir.y, dir.x*sb+dir.z*cb]);
  }
  updWeaponUI();
}
function releasePointers(){
  fireUp(true);
  PTR.clear(); zoomHeld=false;
  for(const k in keys) keys[k]=0;
  inp.fwd=0; inp.side=0; inp.up=0; inp.boost=0;
  keyLook.x=0; keyLook.y=0;
  PAD.reset(); if(PAD.fire){ PAD.fire=false; }
  hideCutLine(); el.xh.classList.remove('cut');
}
/* ── キーボード ── */
const GAME_KEYS=new Set(['Space','Tab','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter','F1','F2','KeyW','KeyA','KeyS','KeyD','KeyQ','KeyE','KeyZ','KeyC','KeyX','KeyV','KeyR','KeyT','KeyH','KeyP','KeyI','KeyJ','KeyK','KeyL','ShiftLeft','ShiftRight','Escape']);
const keyLook={x:0,y:0};
window.addEventListener('keydown',e=>{
  const code=e.code;
  if(e.ctrlKey||e.metaKey||e.altKey) return;
  const rep=e.repeat;
  keys[code]=1;
  const ov=topOverlay();
  if(ov){
    if(code==='Escape'||(code==='KeyP'&&ov!==keysEl)||(code==='F1'&&ov===keysEl)){ if(!rep) closeTop(); e.preventDefault(); return; }
    if(ov===titleEl && (code==='Enter'||code==='Space') && !rep && (!KNAV.lastId||KNAV.lastId==='tStart')){ startGame(); e.preventDefault(); return; }
    if(ov===titleEl && code==='F1' && !rep){ openKeys(); e.preventDefault(); return; }
    if(code==='Tab'){ if(ov===wpanel) closePanel(); e.preventDefault(); return; }
    if(code==='ArrowUp'||code==='KeyW'||code==='KeyI'){ knavMove(0,-1); e.preventDefault(); return; }
    if(code==='ArrowDown'||code==='KeyS'||code==='KeyK'){ knavMove(0,1); e.preventDefault(); return; }
    if(code==='ArrowLeft'||code==='KeyA'||code==='KeyJ'){ knavMove(-1,0); e.preventDefault(); return; }
    if(code==='ArrowRight'||code==='KeyD'||code==='KeyL'){ knavMove(1,0); e.preventDefault(); return; }
    if(code==='Enter'||code==='Space'){ if(!rep) knavActivate(); e.preventDefault(); return; }
    if(ov===wpanel){ const wi=KEYCODE_W[code]; if(wi!==undefined&&WPN[wi]){ selW(WPN[wi].id,true); closePanel(); e.preventDefault(); return; } }
    if(GAME_KEYS.has(code)) e.preventDefault();
    return;
  }
  if(code==='Escape'||code==='KeyP'){ if(!rep && !booting && !resultOn) openMenu('menu'); e.preventDefault(); return; }
  if(booting||resultOn||paused) return;
  if(GAME_KEYS.has(code)) e.preventDefault();
  if(rep) return;
  switch(code){
    case 'Space': case 'Enter': fireDown('key'); break;
    case 'Tab': openPanel(); break;
    case 'KeyZ': cycleW(-1); break;
    case 'KeyC': cycleW(1); break;
    case 'KeyX': blowCharges(); break;
    case 'KeyV': zoomToggle=!zoomToggle; break;
    case 'KeyR': cam.pitch=0; break;
    case 'KeyT': cycleView(); break;
    case 'KeyH': toggleHud(); break;
    case 'F1': openKeys(); break;
    case 'F2': togglePerf(); break;
    default: { const wi=KEYCODE_W[code]; if(wi!==undefined&&WPN[wi]) selW(WPN[wi].id,true); }
  }
});
window.addEventListener('keyup',e=>{ keys[e.code]=0; if((e.code==='Space'||e.code==='Enter') && fireSrc==='key') fireUp(false); if(GAME_KEYS.has(e.code) && !topOverlay()) e.preventDefault(); });
// ボタンをクリックした後にフォーカスが残ると Space/Enter がそのボタンを押してしまうので外す
window.addEventListener('click',e=>{ const b=e.target&&e.target.closest&&e.target.closest('button'); if(b&&b.blur) setTimeout(()=>{ try{ b.blur(); }catch(err){} },0); });
function readKeys(){
  const dt=realDt;
  pollPad(dt);
  if(resultOn && resultEl.classList.contains('on')){ if(KNAV.root!==resultEl) knavOpen(resultEl,'rAgain'); }
  else if(KNAV.root===resultEl) knavClose();
  if(titleOn){ titleT+=dt; cam.yaw=titleYaw0+Math.sin(titleT*.21)*.045; cam.pos.y=titleY0+Math.sin(titleT*.33)*2.2; }   // タイトル中はゆっくり漂う
  if(uiBlocked()){ inp.fwd=0; inp.side=0; inp.up=0; inp.boost=0; return; }
  const f=(keys.KeyW?1:0)-(keys.KeyS?1:0), s=(keys.KeyD?1:0)-(keys.KeyA?1:0);
  if(PAD.mv.on){ inp.fwd=PAD.mv.f; inp.side=PAD.mv.s; } else { inp.fwd=f; inp.side=s; }
  inp.up=((keys.KeyE?1:0)-(keys.KeyQ?1:0))||PAD.up;
  inp.boost=(keys.ShiftLeft||keys.ShiftRight)?1:PAD.boost;
  // 視点（矢印キー／IJKL）：押し始めは緩く、0.25秒ほどで最高速。離すとすぐ止まる
  const kx=((keys.ArrowRight||keys.KeyL)?1:0)-((keys.ArrowLeft||keys.KeyJ)?1:0);
  const ky=((keys.ArrowDown||keys.KeyK)?1:0)-((keys.ArrowUp||keys.KeyI)?1:0);
  keyLook.x = kx ? keyLook.x+(kx-keyLook.x)*Math.min(1,dt*4.5) : 0;    // 離した瞬間に止まる（狙いが流れない）
  keyLook.y = ky ? keyLook.y+(ky-keyLook.y)*Math.min(1,dt*4.5) : 0;
  if(Math.abs(keyLook.x)>.003||Math.abs(keyLook.y)>.003){ const px=(CUT.on?CUT_PX:KEYLOOK_PX)*dt; lookPx(keyLook.x*px, keyLook.y*px); }
  const zt=(zoomHeld||zoomToggle||PAD.zoom)?1:0;
  zoomK+=(zt-zoomK)*Math.min(1,dt*11); if(Math.abs(zoomK-zt)<.003) zoomK=zt;
  el.xh.classList.toggle('zoom',zoomK>.5);
}
/* ── マウス（任意）：ポインタロックで視点。ロックが使えなければドラッグで視点 ── */
let locked=false, mouseUsed=false, lockFails=0, lockFailed=false;
function canvasEl(){ return renderer?renderer.domElement:null; }
function lockOk(){ return !window.TT_NOLOCK && !lockFailed && !!(document.body.requestPointerLock||document.body.mozRequestPointerLock); }
function lockFail(){ lockFails++; if(lockFails>=3 && !lockFailed){ lockFailed=true; wToast('ポインタロックが使えないため、マウスはドラッグで視点を動かします（矢印キーでも可）'); } }
function requestLock(){
  if(!lockOk()||locked) return;
  const c=canvasEl(); if(!c||!c.requestPointerLock) return;
  const plain=()=>{ try{ const p2=c.requestPointerLock(); if(p2&&p2.catch) p2.catch(lockFail); }catch(e){ lockFail(); } };
  try{ const p=c.requestPointerLock({unadjustedMovement:true}); if(p&&p.catch) p.catch(plain); }
  catch(e){ plain(); }
}
document.addEventListener('pointerlockchange',()=>{
  const was=locked; locked=(document.pointerLockElement===canvasEl());
  if(!locked){ if(fireSrc==='mouse') fireUp(true); zoomHeld=false; if(was && !uiBlocked()) openMenu('menu'); }
});
document.addEventListener('pointerlockerror',()=>{ locked=false; lockFails=3; lockFail(); });
window.addEventListener('mousemove',e=>{
  mouseUsed=true;
  if(uiBlocked()) return;
  if(locked) lookPx(e.movementX||0,e.movementY||0);
  else { const p=PTR.get('m'); if(p){ lookPx(e.clientX-p.x,e.clientY-p.y); p.x=e.clientX; p.y=e.clientY; } }
});
window.addEventListener('mousedown',e=>{
  mouseUsed=true;
  const t=e.target;
  if(t&&t.closest&&t.closest('button,.ov,#title,#result,#wbar,#mmWrap,#det')) return;
  if(uiBlocked()) return;
  if(e.button===0){
    if(!locked && lockOk()){ requestLock(); return; }       // 最初のクリックはロックだけ（誤射しない）
    fireDown('mouse'); if(!locked) PTR.set('m',{x:e.clientX,y:e.clientY});
  } else if(e.button===2){ zoomHeld=true; if(!locked) PTR.set('m',{x:e.clientX,y:e.clientY}); }
  else if(e.button===1){ e.preventDefault(); blowCharges(); }
});
window.addEventListener('mouseup',e=>{
  if(e.button===0 && fireSrc==='mouse') fireUp(false);
  if(e.button===2) zoomHeld=false;
  if(!e.buttons) PTR.delete('m');
});
window.addEventListener('contextmenu',e=>e.preventDefault());
window.addEventListener('wheel',e=>{ if(uiBlocked()) return; if(Math.abs(e.deltaY)<1) return; cycleW(e.deltaY>0?1:-1); e.preventDefault(); },{passive:false});
window.addEventListener('blur',()=>releasePointers());
window.addEventListener('pointerdown',function(){ Snd.kick(); },{capture:true});
window.addEventListener('keydown',function(){ Snd.kick(); },{capture:true});
/* ── ゲームパッド（任意・Standard 配列）── */
const PAD={on:false, idx:-1, mv:{on:false,f:0,s:0}, up:0, boost:0, zoom:false, fire:false, prev:[], navT:0,
  reset(){ this.mv.on=false; this.mv.f=0; this.mv.s=0; this.up=0; this.boost=0; this.zoom=false; }};
function padBtn(gp,i){ const b=gp.buttons&&gp.buttons[i]; return !!b && (b.pressed || b.value>.5); }
function pollPad(dt){
  if(!PAD.on && !window.TT_FAKEPAD) return;
  let gp=null;
  if(window.TT_FAKEPAD) gp=window.TT_FAKEPAD;
  else { try{ const L=navigator.getGamepads?navigator.getGamepads():[]; gp=(PAD.idx>=0&&L[PAD.idx])||null; if(!gp) for(let i=0;i<L.length;i++) if(L[i]&&L[i].connected){ gp=L[i]; break; } }catch(e){} }
  if(!gp){ PAD.reset(); return; }
  const ax=(i)=>{ const v=gp.axes&&gp.axes[i]||0; const a=Math.abs(v); if(a<.18) return 0; return Math.sign(v)*Math.pow((a-.18)/.82,1.5); };
  const lx=ax(0), ly=ax(1), rx=ax(2), ry=ax(3);
  const now=[]; for(let i=0;i<16;i++) now[i]=padBtn(gp,i);
  const edge=(i)=>now[i]&&!PAD.prev[i];
  const ov=topOverlay();
  if(ov){
    PAD.navT-=dt;
    const nx=(now[15]?1:0)-(now[14]?1:0)+(Math.abs(lx)>.6?Math.sign(lx):0), ny=(now[13]?1:0)-(now[12]?1:0)+(Math.abs(ly)>.6?Math.sign(ly):0);
    if((nx||ny) && PAD.navT<=0){ PAD.navT=.22; if(ny) knavMove(0,ny); else knavMove(nx,0); }
    if(!nx&&!ny) PAD.navT=0;
    if(edge(0)){ if(ov===titleEl && (!KNAV.lastId||KNAV.lastId==='tStart')) startGame(); else knavActivate(); }
    if(edge(1)||edge(9)) closeTop();
    PAD.prev=now; PAD.reset(); return;
  }
  if(booting||resultOn||paused){ PAD.prev=now; PAD.reset(); return; }
  if(edge(9)){ openMenu('menu'); PAD.prev=now; return; }
  PAD.mv.on=(lx!==0||ly!==0); PAD.mv.f=-ly; PAD.mv.s=lx;
  PAD.up=(now[0]?1:0)-(now[1]?1:0);
  PAD.boost=now[10]?1:0;
  PAD.zoom=!!now[6];
  if(rx||ry){ const px=(CUT.on?CUT_PX:PADLOOK_PX)*dt; lookPx(rx*px, ry*px); }
  if(now[7]&&!PAD.fire){ PAD.fire=true; fireDown('pad'); }
  else if(!now[7]&&PAD.fire){ PAD.fire=false; if(fireSrc==='pad') fireUp(false); }
  if(edge(5)||edge(15)) cycleW(1);
  if(edge(4)||edge(14)) cycleW(-1);
  if(edge(2)) blowCharges();
  if(edge(3)) openPanel();
  if(edge(8)) toggleHud();
  if(edge(12)) cam.pitch=0;
  if(edge(13)) cycleView();
  if(edge(11)) zoomToggle=!zoomToggle;
  PAD.prev=now;
}
window.addEventListener('gamepadconnected',e=>{ PAD.on=true; PAD.idx=e.gamepad.index; wToast('🎮 ゲームパッドを認識：'+String(e.gamepad.id||'').slice(0,42)); updKeyHint(); });
window.addEventListener('gamepaddisconnected',e=>{ if(e.gamepad.index===PAD.idx){ PAD.on=false; PAD.idx=-1; PAD.reset(); if(fireSrc==='pad') fireUp(true); updKeyHint(); } });
/* ══════════ キーボードでメニューを操作する（最寄りのボタンへ移動） ══════════ */
const KNAV={root:null, idx:0, lastId:null};
function knavItems(){ if(!KNAV.root) return []; return Array.from(KNAV.root.querySelectorAll('button')).filter(b=>!b.disabled && b.offsetParent!==null); }
function knavSet(i){
  const it=knavItems(); if(!it.length) return;
  KNAV.idx=((i%it.length)+it.length)%it.length;
  it.forEach((b,k)=>b.classList.toggle('kf',k===KNAV.idx));
  const b=it[KNAV.idx]; KNAV.lastId=b.id||null;
  try{ b.scrollIntoView({block:'nearest'}); }catch(e){}
  if(KNAV.root===wpanel && b.dataset.w){ const W=WPN.find(w=>w.id===b.dataset.w); if(W) showWDesc(W); }
}
function knavMove(dx,dy){
  const it=knavItems(); if(!it.length) return;
  const cur=it[KNAV.idx]||it[0];
  const r=cur.getBoundingClientRect(); const cx=r.left+r.width/2, cy=r.top+r.height/2;
  let best=-1, bd=1e18;
  for(let k=0;k<it.length;k++){ if(it[k]===cur) continue;
    const q=it[k].getBoundingClientRect(); const ddx=q.left+q.width/2-cx, ddy=q.top+q.height/2-cy;
    const along=ddx*dx+ddy*dy; if(along<=4) continue;
    const perp=Math.abs(ddx*dy-ddy*dx);
    const sc=along*along+perp*perp*6; if(sc<bd){ bd=sc; best=k; } }
  if(best<0){ // 端まで来たら反対側へ回り込む
    for(let k=0;k<it.length;k++){ if(it[k]===cur) continue;
      const q=it[k].getBoundingClientRect(); const ddx=q.left+q.width/2-cx, ddy=q.top+q.height/2-cy;
      const along=-(ddx*dx+ddy*dy); if(along<=4) continue;
      const perp=Math.abs(ddx*dy-ddy*dx);
      const sc=-along*along+perp*perp*6; if(sc<bd){ bd=sc; best=k; } }
  }
  if(best>=0){ knavSet(best); Snd.kick(); }
}
function knavOpen(root,preferId){ KNAV.root=root; const it=knavItems(); let i=0; if(preferId){ const k=it.findIndex(b=>b.id===preferId); if(k>=0) i=k; } knavSet(i); }
function knavClose(){ if(KNAV.root) knavItems().forEach(b=>b.classList.remove('kf')); KNAV.root=null; }
function knavActivate(){ const it=knavItems(); const b=it[KNAV.idx]; if(b) b.click(); }
for(const root of [pmenu,wpanel,titleEl,keysEl,resultEl]) root.addEventListener('pointerover',e=>{ const b=e.target.closest&&e.target.closest('button'); if(!b||KNAV.root!==root) return; const k=knavItems().indexOf(b); if(k>=0) knavSet(k); });
/* ══════════ タイトル ══════════ */
function onBootDone(){ if(!titleShown){ titleShown=true; showTitle(); } }
let titleT=0, titleYaw0=0, titleY0=0;
function showTitle(){
  titleOn=true; titleEl.classList.add('on'); el.hud.classList.add('title');
  titleT=0; titleYaw0=cam.yaw; titleY0=cam.pos.y;
  document.getElementById('tSeed').textContent='SEED '+citySeed+'　·　'+MAPNAMES[MAPID]+'　·　'+modeDef().lbl;
  knavOpen(titleEl,'tStart'); updKeyHint();
  if(locked){ try{ document.exitPointerLock(); }catch(e){} }
}
function startGame(){
  if(!titleOn) return;
  titleOn=false; titleEl.classList.remove('on'); el.hud.classList.remove('title'); if(KNAV.root===titleEl) knavClose();
  cam.yaw=titleYaw0; cam.pos.y=titleY0;
  Snd.kick();
  if(mouseUsed) requestLock();
  showHint();
  banner(MAPNAMES[MAPID],modeDef().lbl);
}
document.getElementById('tStart').addEventListener('click',e=>{ e.stopPropagation(); startGame(); });
document.getElementById('tKeysBtn').addEventListener('click',e=>{ e.stopPropagation(); openKeys(); });
document.getElementById('tMenuBtn').addEventListener('click',e=>{ e.stopPropagation(); openMenu('menu'); });
/* ══════════ 操作一覧 ══════════ */
function openKeys(){ if(keysOn) return; keysOn=true; keysEl.classList.add('on'); releasePointers(); knavOpen(keysEl,'kClose2'); }
function closeKeys(){ if(!keysOn) return; keysOn=false; keysEl.classList.remove('on'); if(KNAV.root===keysEl) knavClose(); const ov=topOverlay(); if(ov) knavOpen(ov, ov===titleEl?'tStart':(ov===pmenu?'bHint':null)); }
document.getElementById('kClose').addEventListener('click',e=>{ e.stopPropagation(); closeKeys(); });
document.getElementById('kClose2').addEventListener('click',e=>{ e.stopPropagation(); closeKeys(); });
/* ══════════ ポーズメニュー ══════════ */
function openMenu(reason){
  if(menuOpen()) return;
  closePanel(); releasePointers();
  if(!titleOn) setPaused(true,reason||'menu');
  renderMenu();
  pmenu.classList.add('on');
  knavOpen(pmenu,'pmResume');
  if(locked){ try{ document.exitPointerLock(); }catch(e){} }
}
function closeMenu(){
  pmenu.classList.remove('on'); if(KNAV.root===pmenu) knavClose();
  if(titleOn){ knavOpen(titleEl,'tStart'); return; }
  setPaused(false);
  if(mouseUsed) requestLock();
}
onPauseChange=(v,reason)=>{
  if(v){ if(!menuOpen() && !resultOn && !titleOn){ renderMenu(); pmenu.classList.add('on'); knavOpen(pmenu,'pmResume'); } }
  else { pmenu.classList.remove('on'); if(KNAV.root===pmenu) knavClose(); }
};
function mkPB(text,on,fn,id){ const b=document.createElement('button'); b.className='pb'+(on?' on':''); b.textContent=text; if(id) b.id=id; b.addEventListener('click',e=>{ e.stopPropagation(); fn(); }); return b; }
function setTog(id,text,on){ const b=document.getElementById(id); if(!b) return; b.textContent=text; b.classList.toggle('on',!!on); }
function renderMenu(){
  const q=document.getElementById('pmQualRow'); q.innerHTML='';
  [['auto','自動'],['ultra','最高'],['high','高'],['mid','中'],['low','低']].forEach(([m,n])=>{
    const b=mkPB(m==='auto'?('自動（'+QNAME[QUAL.level]+'）'):n, QUAL.mode===m, ()=>{ PCS.q=m; savePCS(); setQuality(m); renderMenu(); }, 'pmQ_'+m);
    if(m!=='auto') b.title={ultra:'ネイティブ解像度・SSAO・反射毎フレーム・ブルーム6段',high:'3.2MP上限・SSAO',mid:'2.1MP上限・反射隔フレーム',low:'1.2MP上限・反射なし・MSAAなし'}[m];
    q.appendChild(b); });
  const sc=document.getElementById('pmScaleRow'); sc.innerHTML='';
  [.5,.75,1,1.25,1.5,2].forEach(v=>{ sc.appendChild(mkPB(Math.round(v*100)+'%',Math.abs(PCS.scale-v)<.01,()=>{ PCS.scale=v; savePCS(); resScale=v; applyLevel(QUAL.level,true); renderMenu(); },'pmS_'+Math.round(v*100))); });
  const fv=document.getElementById('pmFovRow'); fv.innerHTML='';
  [60,70,75,80,90,100].forEach(v=>{ fv.appendChild(mkPB(v+'°',PCS.fov===v,()=>{ PCS.fov=v; savePCS(); fovUser=v; renderMenu(); },'pmF_'+v)); });
  document.getElementById('pmSensV').textContent=PCS.sens;
  setTog('bInvY','Y軸反転',PCS.invY); setTog('bSnd',PCS.snd?'🔊 音':'🔇 音 OFF',PCS.snd);
  setTog('bAO','SSAO '+(PCS.ao?'ON':'OFF'),PCS.ao); setTog('bFx','演出 '+(PCS.fx<1?'控えめ':'標準'),PCS.fx>=1);
  setTog('bPerf','性能表示',QUAL.showPerf); setTog('bHud','HUD '+(PCS.hud?'表示':'非表示'),PCS.hud);
  const pm=document.getElementById('pmModes'); pm.innerHTML='';
  MODES.forEach(M=>{ pm.appendChild(mkPB(M.n+'　'+M.d, M.id===MODE, ()=>{ setMode(M.id); genCity(MAPID,citySeed); spawnOverview(); closeMenu(); banner(M.n+'モード',M.lbl); wToast(M.d); },'pmM_'+M.id)); });
  const pp=document.getElementById('pmMaps'); pp.innerHTML='';
  MAPNAMES.forEach((n,i)=>{ pp.appendChild(mkPB(n, i===MAPID, ()=>{ genCity(i); spawnOverview(); closeMenu(); banner(MAPNAMES[MAPID],''); },'pmP_'+i)); });
  document.getElementById('pmSeed').textContent='SEED '+citySeed+'　·　'+MAPNAMES[MAPID]+'　·　'+modeDef().lbl+'　·　'+(POST.on?(POST.hdr?'HDR':'8bit')+(POST.msaa?' MSAA':'')+(POST.aoOn?' SSAO':'')+(WET.on?' 反射':''):'ポスト処理なし');
  if(KNAV.root===pmenu) knavOpen(pmenu,KNAV.lastId);
}
document.getElementById('pmClose').addEventListener('click',e=>{ e.stopPropagation(); closeMenu(); });
document.getElementById('pmResume').addEventListener('click',e=>{ e.stopPropagation(); closeMenu(); });
document.getElementById('bSnd').addEventListener('click',e=>{ e.stopPropagation(); PCS.snd=!PCS.snd; S.sound=PCS.snd; savePCS(); if(!S.sound) Snd.pause(); renderMenu(); if(S.sound) Snd.kick(); });
document.getElementById('bInvY').addEventListener('click',e=>{ e.stopPropagation(); PCS.invY=!PCS.invY; savePCS(); renderMenu(); });
document.getElementById('bAO').addEventListener('click',e=>{ e.stopPropagation(); PCS.ao=!PCS.ao; aoUser=PCS.ao; savePCS(); applyLevel(QUAL.level,true); renderMenu(); });
document.getElementById('bFx').addEventListener('click',e=>{ e.stopPropagation(); PCS.fx=PCS.fx<1?1:0.5; QUAL.fxK=PCS.fx; savePCS(); renderMenu(); });
document.getElementById('bPerf').addEventListener('click',e=>{ e.stopPropagation(); togglePerf(); renderMenu(); });
document.getElementById('bHud').addEventListener('click',e=>{ e.stopPropagation(); toggleHud(); renderMenu(); });
document.getElementById('bHint').addEventListener('click',e=>{ e.stopPropagation(); openKeys(); });
document.getElementById('bFull').addEventListener('click',e=>{ e.stopPropagation(); toggleFull(); });
document.getElementById('pmSensM').addEventListener('click',e=>{ e.stopPropagation(); PCS.sens=clampN(PCS.sens-1,1,10); savePCS(); renderMenu(); });
document.getElementById('pmSensP').addEventListener('click',e=>{ e.stopPropagation(); PCS.sens=clampN(PCS.sens+1,1,10); savePCS(); renderMenu(); });
document.getElementById('pmRetry').addEventListener('click',e=>{ e.stopPropagation(); genCity(MAPID,citySeed); spawnOverview(); closeMenu(); banner('再挑戦','SAME CITY'); });
document.getElementById('pmNew').addEventListener('click',e=>{ e.stopPropagation(); genCity(MAPID); spawnOverview(); closeMenu(); banner('新しい街','NEW CITY'); });
document.getElementById('pmTitle').addEventListener('click',e=>{ e.stopPropagation(); pmenu.classList.remove('on'); if(KNAV.root===pmenu) knavClose(); genCity(MAPID,citySeed); spawnOverview(); setPaused(false); showTitle(); });
document.getElementById('wClose').addEventListener('click',e=>{ e.stopPropagation(); closePanel(); });
wpanel.addEventListener('click',e=>{ if(e.target.id==='wpanel') closePanel(); });
document.getElementById('det').addEventListener('click',e=>{ e.stopPropagation(); if(uiBlocked()) return; blowCharges(); });
document.getElementById('rAgain').addEventListener('click',e=>{ e.stopPropagation(); hideResult(); genCity(MAPID,citySeed); spawnOverview(); });
document.getElementById('rNewCity').addEventListener('click',e=>{ e.stopPropagation(); hideResult(); genCity(MAPID); spawnOverview(); });
document.getElementById('rNext').addEventListener('click',e=>{ e.stopPropagation(); hideResult(); genCity(MAPID+1); banner(MAPNAMES[MAPID],''); spawnOverview(); });
onCtxLost=(lost)=>{ const o=document.getElementById('ctxov'); o.classList.toggle('on',lost);
  const rb=document.getElementById('ctxReload'); rb.style.display='none';
  if(lost) setTimeout(()=>{ if(ctxLost) rb.style.display=''; },3000); };
document.getElementById('ctxReload').addEventListener('click',()=>location.reload());
function toggleHud(){ PCS.hud=!PCS.hud; el.hud.classList.toggle('off',!PCS.hud); }   // HUD の非表示は保存しない（次回は表示から）
function togglePerf(){ QUAL.showPerf=!QUAL.showPerf; document.getElementById('perf').classList.toggle('on',QUAL.showPerf); }
function toggleFull(){ try{ if(document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen(); }catch(e){} }
/* ══════════ 俯瞰ポイント（T キー）══════════ */
let viewIdx=0;
function setView(v){ cam.pos.set(v.x,v.y,v.z); cam.vel.set(0,0,0); cam.yaw=v.yaw; cam.pitch=v.pitch; camera.position.copy(cam.pos); }
function cycleView(){
  viewIdx=(viewIdx+1)%4;
  const cx=(CITY.x0+CITY.x1)/2, cz=(CITY.z0+CITY.z1)/2;
  if(viewIdx===0) spawnOverview();
  else setView([null,
    {x:cx, y:240, z:CITY.z1+280, yaw:0, pitch:-.62},
    {x:CITY.x1+320, y:180, z:cz, yaw:Math.PI/2, pitch:-.52},
    {x:cx, y:640, z:cz+30, yaw:0, pitch:-1.45}][viewIdx]);
  wToast('視点：'+['初期位置','南の上空','東の上空','真上'][viewIdx]);
}
/* ══════════ ミニマップ ══════════ */
const mmCv=document.getElementById('minimap'), mmg=mmCv?mmCv.getContext('2d'):null;
function drawMinimap(){
  if(!mmg||!CITY||!PCS.hud) return;
  const W=mmCv.width, H=mmCv.height;
  const x0=CITY.x0-50,x1=CITY.x1+50,z0=CITY.z0-50,z1=CITY.z1+50;
  const sc=Math.min(W/(x1-x0),H/(z1-z0)); const ox=(W-(x1-x0)*sc)/2, oz=(H-(z1-z0)*sc)/2;
  const X=(x)=>ox+(x-x0)*sc, Z=(z)=>oz+(z-z0)*sc;
  mmg.clearRect(0,0,W,H);
  mmg.fillStyle='rgba(6,10,16,.82)'; mmg.fillRect(0,0,W,H);
  for(let k=0;k<blds.length;k++){ const b=blds[k]; if(b.style==='pole'||b.style==='tree'||b.style==='car') continue;
    const r=b.init?b.live/b.init:0;
    mmg.fillStyle = r<=0.15 ? 'rgba(255,61,127,.45)' : (r<0.85 ? 'rgba(255,181,61,.8)' : (b.lm!==undefined?'rgba(255,209,102,.95)':'rgba(79,227,240,.5)'));
    mmg.fillRect(X(b.ox),Z(b.oz),Math.max(2,b.W*VOX*sc),Math.max(2,b.D*VOX*sc)); }
  mmg.fillStyle='rgba(255,120,30,.95)';
  for(let i=0;i<fires.length;i++){ const f=fires[i]; mmg.beginPath(); mmg.arc(X(f.x),Z(f.z),3,0,6.283); mmg.fill(); }
  const px=X(camera.position.x), pz=Z(camera.position.z);
  const fx=-Math.sin(cam.yaw), fz=-Math.cos(cam.yaw);
  const hf=Math.atan(Math.tan(camera.fov*Math.PI/360)*camera.aspect);
  mmg.fillStyle='rgba(255,255,255,.10)';
  mmg.beginPath(); mmg.moveTo(px,pz);
  mmg.arc(px,pz,W*.28,Math.atan2(fz,fx)-hf,Math.atan2(fz,fx)+hf); mmg.closePath(); mmg.fill();
  mmg.fillStyle='#fff'; mmg.strokeStyle='rgba(0,0,0,.8)'; mmg.lineWidth=2;
  mmg.beginPath(); mmg.moveTo(px+fx*11,pz+fz*11); mmg.lineTo(px-fx*7+fz*6,pz-fz*7-fx*6); mmg.lineTo(px-fx*7-fz*6,pz-fz*7+fx*6); mmg.closePath(); mmg.fill(); mmg.stroke();
}
/* 初回だけ短い操作ヒント */
let hintT=null;
function showHint(force){
  let seen=false; try{ seen=!!localStorage.getItem('tt_pc_hint'); }catch(e){}
  if(seen&&!force) return;
  try{ localStorage.setItem('tt_pc_hint','1'); }catch(e){}
  const h=document.getElementById('hint');
  h.innerHTML='<b>矢印キー</b>で視点、<b>WASD</b>で移動、<b>Space</b>で発射。マウスは任意（クリックで視点をロック）<br><b>Z / C</b> で武器切替、<b>Tab</b> で一覧、<b>Esc</b> でメニュー';
  h.classList.add('on');
  if(hintT) clearTimeout(hintT);
  hintT=setTimeout(()=>h.classList.remove('on'),9000);
}
/* ══════════ 性能表示（検証用） ══════════ */
function drawPerf(avg,worst){
  const d=document.getElementById('perf'); if(!d) return;
  const r=Array.from(QUAL.ring).filter(v=>v>0).sort((a,b)=>a-b);
  const q=(k)=>r.length?r[Math.min(r.length-1,(r.length*k)|0)].toFixed(1):'-';
  const info=renderer?renderer.info:null;
  d.textContent=
    'frame avg '+avg.toFixed(1)+'ms  p50 '+q(.5)+'  p95 '+q(.95)+'  worst '+worst.toFixed(0)+'ms  '+(POST.w||0)+'x'+(POST.h||0)+'\n'+
    'quality '+QUAL.mode+' L'+QUAL.level+' pr'+QUAL.pr.toFixed(2)+' scale'+resScale+(POST.on?(POST.hdr?' HDR':' 8bit')+(POST.msaa?' MSAA':'')+(POST.aoOn?' SSAO':'')+(POST.streakOn?' streak':'')+(WET.on?' refl/'+WET.every:''):' noPost')+'\n'+
    'step wpn '+PROF.wpn.toFixed(1)+' chunk '+PROF.chunk.toFixed(1)+' bfs '+PROF.bfs.toFixed(1)+' mesh '+PROF.mesh.toFixed(1)+' fx '+PROF.fx.toFixed(1)+'ms\n'+
    'chunks '+chunks.length+' meshQ '+meshQ.length+' zoneQ '+zoneQ.length+' rubble '+rubMeshes.length+'/'+rubTris+'tri\n'+
    'smoke '+VFX.sa.length+' fire '+VFX.fa.length+' spark '+VFX.pa.length+' pts '+fx.length+'/'+gxA.length+' debris '+DEB.arr.length+' peds '+PED.list.length+' fires '+fires.length+' tracers '+tracers.length+'\n'+
    (info?('gpu geo '+info.memory.geometries+' tex '+info.memory.textures+' calls '+info.render.calls+' tris '+info.render.triangles):'')+'\n'+
    'input '+(locked?'mouse-locked':(mouseUsed?'mouse':'keyboard'))+(PAD.on?' pad':'')+' fire '+fireHeld+' cut '+CUT.on;
}
/* 検証用フック（PC） */
const PCDBG={
  start:startGame, showTitle:showTitle, titleOn:()=>titleOn,
  key:(code,down)=>{ window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code:code,key:code,bubbles:true,cancelable:true})); },
  look:lookPx, keys:()=>keys, cut:()=>CUT, zoomK:()=>zoomK, fov:()=>camera.fov, PCS:PCS, cycleW:cycleW,
  menuOpen:menuOpen, panelOpen:panelOpen, keysOn:()=>keysOn, knav:()=>({root:KNAV.root?KNAV.root.id:null, idx:KNAV.idx, id:KNAV.lastId}),
  pad:()=>PAD, locked:()=>locked, fireDown:fireDown, fireUp:fireUp, fireSrc:()=>fireSrc,
  wbar:()=>Array.from(wbar.querySelectorAll('.q')).map(b=>b.dataset.w+(b.classList.contains('sel')?'*':'')),
  minimap:()=>mmCv, readKeys:readKeys, openMenu:openMenu, closeMenu:closeMenu, openPanel:openPanel, closePanel:closePanel, openKeys:openKeys,
  cycleView:cycleView, viewIdx:()=>viewIdx, resScale:()=>resScale, aoOn:()=>POST.aoOn, uiBlocked:uiBlocked, keyhint:()=>el.keyhint.textContent,
  hudOff:()=>el.hud.classList.contains('off'), savePCS:savePCS, applyPCS:applyPCS, renderMenu:renderMenu,
  resetFx:()=>{ flashV=0; el.flash.style.opacity=0; shownTon=killedVox*TON_PER_VOX; elScore.innerHTML=fmtTon(shownTon); popVox=0; el.banner.getAnimations().forEach(a=>a.cancel()); },
};
