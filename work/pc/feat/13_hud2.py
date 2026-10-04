# HUD 第2弾：破壊の実況フィード、照準下のターゲットカード（損傷ゲージ）、クールダウンリングと READY、倒壊予告のコールアウト、F で全画面、フレーム上限
TITLE='実況フィード・ターゲットカード・クールダウンリング・倒壊コールアウト・全画面(F)・フレーム上限'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    C=lambda a,b,c=1: src.rep('css',a,b,c)
    B=lambda a,b,c=1: src.rep('body',a,b,c)
    # ── DOM ──
    B('  <div id="xhInfo"><div id="xhDist">—</div><div id="xhTgt"></div></div>',
      '  <div id="xhInfo"><div id="xhDist">—</div><div id="xhTgt"></div><div id="xhBar"><i></i></div></div>\n  <div id="xhRing"></div>\n  <div id="feed"></div>\n  <div id="callouts"></div>')
    C('#xhCd{', """#xhBar{width:150px;height:3px;margin:5px auto 0;background:rgba(255,255,255,.14);border-radius:2px;overflow:hidden;opacity:0;transition:opacity .15s;}
#xhBar.on{opacity:1;}
#xhBar i{display:block;height:100%;width:100%;background:linear-gradient(90deg,var(--cyan),#9ff);transform-origin:0 50%;}
#xhBar.hurt i{background:linear-gradient(90deg,#ff5a1f,var(--amber));}
#xhRing{position:absolute;left:50%;top:50%;width:56px;height:56px;transform:translate(-50%,-50%);border-radius:50%;opacity:0;pointer-events:none;
  background:conic-gradient(rgba(255,181,61,.85) var(--cd,0deg), rgba(255,255,255,.08) 0);-webkit-mask:radial-gradient(circle,transparent 24px,#000 25px,#000 27px,transparent 28px);mask:radial-gradient(circle,transparent 24px,#000 25px,#000 27px,transparent 28px);}
#xhRing.on{opacity:1;}
#xhRing.ready{animation:xhReady .32s ease-out;}
@keyframes xhReady{0%{transform:translate(-50%,-50%) scale(1);opacity:1;box-shadow:0 0 0 0 rgba(79,227,240,.9);}100%{transform:translate(-50%,-50%) scale(1.6);opacity:0;}}
#feed{position:absolute;left:18px;top:140px;width:360px;pointer-events:none;display:flex;flex-direction:column;gap:5px;}
.fd{font-size:12.5px;line-height:1.4;color:var(--ink);background:rgba(6,10,16,.62);border-left:3px solid var(--cyan);padding:5px 10px;border-radius:0 8px 8px 0;
  text-shadow:0 1px 0 #000;animation:fdIn .32s cubic-bezier(.2,.9,.3,1);}
.fd b{color:#fff;} .fd .s{color:var(--dim);font-size:11px;margin-left:6px;} .fd .t{color:var(--amber);font-weight:900;margin-left:6px;font-variant-numeric:tabular-nums;}
.fd.lm{border-left-color:var(--gold);background:rgba(40,30,8,.7);} .fd.lm b{color:var(--gold);}
.fd.chain{border-left-color:var(--mag);} .fd.nuke{border-left-color:#8f869d;color:var(--dim);}
.fd.out{animation:fdOut .4s ease-in forwards;}
@keyframes fdIn{from{opacity:0;transform:translateX(-14px);}to{opacity:1;transform:none;}}
@keyframes fdOut{to{opacity:0;transform:translateX(-10px);}}
.co{position:absolute;left:0;top:0;transform:translate(-50%,-100%);white-space:nowrap;font-size:12px;font-weight:900;letter-spacing:.08em;color:#fff;
  text-shadow:0 1px 0 #000,0 0 10px rgba(255,61,127,.8);pointer-events:none;}
.co i{display:inline-block;font-style:normal;color:var(--mag);transform-origin:50% 50%;margin-left:4px;}
#xhCd{""")
    # ── 実況フィード ──
    U("let causeT=0, causeLast='';", """/* 破壊の実況フィード：何が・なぜ・どれだけ */
const feedEl=document.getElementById('feed');
let feedN=0;
function feedPush(html,cls,ms){
  if(!feedEl) return;
  const d=document.createElement('div'); d.className='fd'+(cls?' '+cls:''); d.innerHTML=html; feedEl.appendChild(d);
  while(feedEl.children.length>6) feedEl.removeChild(feedEl.firstChild);
  const id=++feedN;
  setTimeout(()=>{ if(d.parentNode){ d.classList.add('out'); setTimeout(()=>{ if(d.parentNode) d.parentNode.removeChild(d); },420); } },ms||6500);
}
function bldName(b){ const lm=(b.lm!==undefined&&LMS[b.lm])?LMS[b.lm]:null; return lm?lm.name:(STYLE_NAME[b.style]||'建物'); }
const FEED_SKIP={pole:1,car:1,tree:1,trafo:1,water:1,tank:1,gate:1};
let feedRankLast='';
/* 同時に多数が倒れた時は「N棟 倒壊」にまとめる（核・破壊球・連鎖で流れが埋まらないように） */
const FEEDB={n:0,t:0,cls:''};
function feedBld(html,cls,isLm){
  const now=performance.now();
  if(isLm || now-FEEDB.t>900){ FEEDB.t=now; FEEDB.n=1; FEEDB.cls=cls; feedPush(html,cls); return; }
  FEEDB.n++;
  const last=feedEl.lastElementChild;
  if(last && last.dataset.agg){ last.innerHTML='<b>'+FEEDB.n+'棟</b> 倒壊<span class="s">'+(cls==='nuke'?'核･破壊球・加点なし':'連鎖')+'</span>'; }
  else { feedPush('<b>'+FEEDB.n+'棟</b> 倒壊<span class="s">'+(cls==='nuke'?'核･破壊球・加点なし':'連鎖')+'</span>',cls); feedEl.lastElementChild.dataset.agg='1'; }
}
let causeT=0, causeLast='';""")
    # 倒壊イベント：updScoreUI の棟数集計で、初めて「倒壊」になった建物をフィードへ
    U("""    tot2++;
    if(b.live<=b.init*0.15) d2++;
  }""","""    tot2++;
    if(b.live<=b.init*0.15){ d2++;
      if(!b.fedDown){ b.fedDown=1; if(b.init>=320 && !booting && !FEED_SKIP[b.style]){ const src=b.lastSrc||'collapse'; const ton=Math.round(b.init*TON_PER_VOX);
        feedBld('<b>'+bldName(b)+'</b> 倒壊<span class="s">'+(SRCNAME[src]||'')+(src==='nuke'?'・加点なし':'')+'</span><span class="t">'+(ton>=1000?(ton/1000).toFixed(1)+'kt':ton+'t')+'</span>', src==='nuke'?'nuke':'', b.lm!==undefined); } }
    } else if(b.fedDown && b.live>b.init*0.15) b.fedDown=0;
  }""")
    # ランドマーク陥落・連鎖ランク
    U("""function banner(t,u,cls,dur){
  const now=performance.now();""","""function banner(t,u,cls,dur){
  if(cls==='lm') feedPush('<b>'+t+'</b> 陥落<span class="s">LANDMARK DOWN</span>','lm',9000);
  const now=performance.now();""")
    U("""function showCombo(){
  elChain.animate([""","""function showCombo(){
  { let col='#ffd166', nm='GOOD'; for(const r of CHAINRANK) if(S.combo>=r[0]){ col=r[1]; nm=r[2]; } if(S.combo>=4 && nm!==feedRankLast){ feedRankLast=nm; feedPush('<b style="color:'+col+'">×'+S.combo+'</b> <span class="s">'+nm+'</span>','chain',3500); } }
  elChain.animate([""")
    # ── ターゲットカード：損傷ゲージ ──
    U("""  const dmg=b.init?Math.round((1-b.live/b.init)*100):0;
  el.tgt.classList.toggle('lm',!!lm);
  return name+(mat?'　'+mat:'')+(dmg>0?'　損傷'+dmg+'%':'');""","""  const dmg=b.init?Math.round((1-b.live/b.init)*100):0;
  el.tgt.classList.toggle('lm',!!lm);
  const bar=document.getElementById('xhBar'); if(bar){ bar.classList.add('on'); bar.classList.toggle('hurt',dmg>=15); bar.firstElementChild.style.transform='scaleX('+(b.init?Math.max(0,b.live/b.init):0).toFixed(3)+')'; }
  const hgt=Math.round(b.H*VOX);
  return name+(mat?'　'+mat:'')+'　'+hgt+'m'+(dmg>0?'　損傷'+dmg+'%':'');""")
    U("  if(h.miss){ el.dist.textContent='—'; el.dist.style.color=''; el.tgt.textContent=''; }",
      "  if(h.miss){ el.dist.textContent='—'; el.dist.style.color=''; el.tgt.textContent=''; const bar=document.getElementById('xhBar'); if(bar) bar.classList.remove('on'); }")
    U("    el.tgt.textContent=targetLabel(h);\n  }","    el.tgt.textContent=targetLabel(h);\n    if(h.ground){ const bar=document.getElementById('xhBar'); if(bar) bar.classList.remove('on'); }\n  }")
    # ── クールダウンリングと READY ──
    U("""function updWeaponUI(){
  const cool=cd>0;""","""let wasCool=false;
function updWeaponUI(){
  const cool=cd>0;
  const ring=document.getElementById('xhRing');
  if(ring){ if(cool && cdMax>=0.5){ ring.classList.add('on'); ring.style.setProperty('--cd',((1-cd/cdMax)*360).toFixed(0)+'deg'); }
    else { ring.classList.remove('on'); if(wasCool && cdMax>=0.5){ ring.classList.remove('ready'); void ring.offsetWidth; ring.classList.add('ready'); } } }
  wasCool=cool;""")
    # ── 倒壊予告のコールアウト ──
    U("let hitFlash=0;", """/* 倒壊予告：傾き始めた建物の上に「倒壊」と倒れる向きを 1.5 秒ほど出す */
const coEl=document.getElementById('callouts'); const coMap=new Map(); const _cv=new THREE.Vector3();
function updCallouts(){
  if(!coEl) return;
  const seen=new Set();
  if(!uiBlocked() && typeof TOPPLING!=='undefined'){
    for(let i=0;i<TOPPLING.length && seen.size<4;i++){ const b=TOPPLING[i]; if(!b||!b.toppling||b.live<=0) continue;
      seen.add(b.id);
      let d=coMap.get(b.id);
      if(!d){ d=document.createElement('div'); d.className='co'; d.innerHTML='倒壊 <i>➜</i>'; coEl.appendChild(d); coMap.set(b.id,d); d._t=performance.now(); }
      _cv.set(b.ox+b.W*VOX/2, b.H*VOX+4, b.oz+b.D*VOX/2).project(camera);
      if(_cv.z>1||Math.abs(_cv.x)>1.2||Math.abs(_cv.y)>1.2){ d.style.display='none'; continue; }
      d.style.display='';
      d.style.left=((_cv.x*.5+.5)*window.innerWidth)+'px'; d.style.top=((-_cv.y*.5+.5)*window.innerHeight)+'px';
      if(b.lean){ const a=Math.atan2(-(b.lean[0]*Math.cos(cam.yaw)-b.lean[1]*Math.sin(cam.yaw)),(b.lean[0]*Math.sin(cam.yaw)+b.lean[1]*Math.cos(cam.yaw))); d.firstElementChild.style.transform='rotate('+(-a).toFixed(2)+'rad)'; }
      d.style.opacity=Math.max(0,1-(performance.now()-d._t)/2200).toFixed(2);
    }
  }
  for(const [id,d] of coMap){ if(!seen.has(id)){ if(d.parentNode) d.parentNode.removeChild(d); coMap.delete(id); } }
}
let hitFlash=0;""")
    U("function updHUD(dt){\n  updAimRings(dt); updHitMark(dt); drawCompass(dt); updTut(dt);","function updHUD(dt){\n  updAimRings(dt); updHitMark(dt); drawCompass(dt); updTut(dt); updCallouts();")
    # ── F で全画面、フレーム上限の設定 ──
    U("    case 'KeyH': toggleHud(); break;","    case 'KeyH': toggleHud(); break;\n    case 'KeyF': toggleFull(); break;")
    U("'F1','F2','Slash','KeyO','KeyM',","'F1','F2','Slash','KeyO','KeyM','KeyF',")
    U("    if(ov===titleEl && (code==='F1'||code==='Slash') && !rep){ openKeys(); e.preventDefault(); return; }",
      "    if(ov===titleEl && (code==='F1'||code==='Slash') && !rep){ openKeys(); e.preventDefault(); return; }\n    if(code==='KeyF' && !rep && (ov===titleEl||ov===pmenu)){ toggleFull(); e.preventDefault(); return; }")
    B('<button class="pb sub" id="bFull">全画面</button>','<button class="pb sub" id="bFull">全画面 (F)</button>')
    B('<div class="k"><kbd>M</kbd></div><div class="v">大きな地図（ランドマーク名・損傷・火災）</div>',
      '<div class="k"><kbd>M</kbd></div><div class="v">大きな地図（ランドマーク名・損傷・火災）</div>\n      <div class="k"><kbd>F</kbd></div><div class="v">全画面の切替</div>')
    U("const PCS={q:'auto',scale:1,fov:75,sens:5,invY:false,ao:true,snd:true,fx:1,hud:true,mlook:'lock'};",
      "const PCS={q:'auto',scale:1,fov:75,sens:5,invY:false,ao:true,snd:true,fx:1,hud:true,mlook:'lock',fps:0};   // fps: 0=無制限（ProMotion なら 120）")
    U("  if(!['lock','hover','drag'].includes(PCS.mlook)) PCS.mlook='lock';","  if(!['lock','hover','drag'].includes(PCS.mlook)) PCS.mlook='lock';\n  fpsCap=[0,60,30].includes(+PCS.fps)?+PCS.fps:0;")
    B('<div class="row"><span class="lb">効果</span>','<div class="row"><span class="lb">フレーム上限</span><div class="row" id="pmFpsRow" style="margin:0;flex:1"></div></div>\n  <div class="row"><span class="lb">効果</span>')
    U("  const lk=document.getElementById('pmLookRow'); lk.innerHTML='';","""  const fr=document.getElementById('pmFpsRow'); fr.innerHTML='';
  [[0,'無制限（ProMotion 120）'],[60,'60'],[30,'30（省電力）']].forEach(([v,n])=>{ fr.appendChild(mkPB(n,(+PCS.fps||0)===v,()=>{ PCS.fps=v; fpsCap=v; savePCS(); renderMenu(); },'pmFps_'+v)); });
  const lk=document.getElementById('pmLookRow'); lk.innerHTML='';""")
    # ループ：上限が設定されていれば描画フレームを間引く（dt は次の実行フレームに持ち越される）
    rep("function loop(now){\n  requestAnimationFrame(loop);\n  const rawReal=(now-last)/1000; last=now;",
        "function loop(now){\n  requestAnimationFrame(loop);\n  if(fpsCap>0 && now-lastDraw<1000/fpsCap-2) return;   // フレーム上限（省電力）：間引いた時間は次の dt に含まれる\n  lastDraw=now;\n  const rawReal=(now-last)/1000; last=now;")
    # fpsCap は起動列（applyPCS）より前に初期化されている必要があるので UI ブロックの先頭で宣言
    U("const clampN=(v,a,b)=>Math.max(a,Math.min(b,v));","const clampN=(v,a,b)=>Math.max(a,Math.min(b,v));\nlet fpsCap=0, lastDraw=0;                    // フレーム上限（設定）と最後に描いた時刻")
    U("keysOn:()=>keysOn, mapOn:()=>mapOn,","keysOn:()=>keysOn, mapOn:()=>mapOn, feedPush:feedPush, feedCount:()=>feedEl.children.length, fpsCap:()=>fpsCap,")
    # フレーム上限中は計測フレームが上限の間隔になるので、自動画質の「重い」判定は上限を基準にする
    rep("  if(m>25 && QUAL.level<QLV.length-1){ QUAL.downT=now; applyLevel(QUAL.level+(m>60?2:1)); }   // 極端に重ければ2段落とす",
        "  const slowMs=Math.max(25, fpsCap>0?1000/fpsCap*1.35:0);   // フレーム上限（30/60）の時はその間隔を基準に\n  if(m>slowMs && QUAL.level<QLV.length-1){ QUAL.downT=now; applyLevel(QUAL.level+(m>slowMs*2.4?2:1)); }   // 極端に重ければ2段落とす")
