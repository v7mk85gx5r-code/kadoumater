# タイトル：マップ・モードをその場で選べる（←→ と Enter）、ベスト記録、レターボックスと START の脈動。結果画面：破壊マップと要因の積み上げバー
TITLE='タイトルのマップ/モード選択・ベスト記録・演出、結果画面の破壊マップと要因バー'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    C=lambda a,b,c=1: src.rep('css',a,b,c)
    B=lambda a,b,c=1: src.rep('body',a,b,c)
    # ── タイトル：マップ／モードの行 ──
    B('    <div id="tBtns">','    <div class="tPick"><span>マップ</span><div id="tMaps"></div></div>\n    <div class="tPick"><span>モード</span><div id="tModes"></div></div>\n    <div id="tBtns">')
    B('    <div id="tSeed">SEED —</div>','    <div id="tSeed">SEED —</div>\n    <div id="tBest">—</div>')
    C('#tBtns{display:flex;gap:10px;margin-top:22px;flex-wrap:wrap;}', """#tBtns{display:flex;gap:10px;margin-top:18px;flex-wrap:wrap;}
.tPick{display:flex;align-items:center;gap:10px;margin-top:10px;}
.tPick span{font-size:10px;letter-spacing:.3em;color:var(--dim);font-weight:800;min-width:48px;}
.tPick div{display:flex;gap:6px;}
.tPick .pb{flex:0 0 auto;min-height:34px;padding:6px 14px;font-size:12px;}
#tBest{font-size:12px;color:var(--gold);letter-spacing:.08em;margin-top:6px;font-variant-numeric:tabular-nums;min-height:16px;}
#title::before,#title::after{content:"";position:absolute;left:0;right:0;height:7vh;background:linear-gradient(#05070c,rgba(5,7,12,0));pointer-events:none;}
#title::before{top:0;} #title::after{bottom:0;transform:scaleY(-1);}
#tStart{animation:tPulse 2.2s ease-in-out infinite;}
@keyframes tPulse{0%,100%{box-shadow:0 0 0 0 rgba(255,61,127,.0);}50%{box-shadow:0 0 26px 2px rgba(255,61,127,.45);}}""")
    U("""function showTitle(){
  titleOn=true; titleEl.classList.add('on'); el.hud.classList.add('title');""","""function renderTitlePick(){
  const tm=document.getElementById('tMaps'); if(!tm) return; tm.innerHTML='';
  MAPNAMES.forEach((n,i)=>{ tm.appendChild(mkPB(n,i===MAPID,()=>{ if(i===MAPID) return; genCity(i); spawnOverview(); showTitle(); knavOpen(titleEl,'tP_'+i); },'tP_'+i)); });
  const td=document.getElementById('tModes'); td.innerHTML='';
  MODES.forEach(M=>{ td.appendChild(mkPB(M.n,M.id===MODE,()=>{ setMode(M.id); renderTitlePick(); knavOpen(titleEl,'tM_'+M.id); },'tM_'+M.id)); });
  const best=loadBest(); const tb=document.getElementById('tBest');
  if(tb) tb.innerHTML=best?('この街・このモードのベスト　<b>'+fmtScore(best.score)+'</b>　ランク '+best.rank+'　'+Math.round(best.ton)+'t'):('ベスト記録はまだありません　—　'+modeDef().d);
}
function showTitle(){
  titleOn=true; titleEl.classList.add('on'); el.hud.classList.add('title');
  renderTitlePick();""")
    # ── 結果画面：破壊マップと要因の積み上げバー ──
    B('  <div id="rMap">歌舞伎町</div>\n  <div id="rRows">','  <div id="rMap">歌舞伎町</div>\n  <div id="rViz"><canvas id="rMapCv" width="520" height="520"></canvas><div id="rStackWrap"><div id="rStackLbl">何で壊したか</div><div id="rStack"></div><div id="rStackKey"></div></div></div>\n  <div id="rRows">')
    C('#rRows{margin:18px auto 0;width:100%;}', """#rViz{display:flex;gap:16px;align-items:center;margin-top:14px;opacity:0;}
#rMapCv{width:150px;height:150px;border-radius:10px;border:1px solid var(--edge);flex:0 0 auto;position:relative;inset:auto;display:block;}
#rStackWrap{flex:1;text-align:left;}
#rStackLbl{font-size:10px;letter-spacing:.3em;color:var(--dim);font-weight:800;margin-bottom:6px;}
#rStack{display:flex;height:14px;border-radius:7px;overflow:hidden;background:rgba(255,255,255,.08);}
#rStack i{display:block;height:100%;}
#rStackKey{margin-top:6px;font-size:10.5px;color:var(--dim);line-height:1.7;}
#rStackKey b{display:inline-block;width:9px;height:9px;border-radius:2px;margin:0 4px 0 8px;vertical-align:-1px;}
#rRows{margin:14px auto 0;width:100%;}""")
    rep("""function showResult(){
  if(resultOn) return;
  resultOn=true; runOver=true;
  const el=document.getElementById('result');
  if(!el) return;
  el.classList.add('on');""","""function showResult(){
  if(resultOn) return;
  resultOn=true; runOver=true;
  const el=document.getElementById('result');
  if(!el) return;
  el.classList.add('on');
  if(typeof onResultShow==='function'){ try{ onResultShow(); }catch(e){} }""")
    U("/* 初回だけ短い操作ヒント */", """/* 結果画面：街の最終状態の地図と、壊した要因の内訳バー */
const SRC_COL={wpn:'#4fe3f0',collapse:'#ffd166',chain:'#ff8a2b',domino:'#ff3d7f',fire:'#ff7a30',nuke:'#8f869d'};
function onResultShow(){
  const cv=document.getElementById('rMapCv'); if(cv){ const g=cv.getContext('2d'); if(g) drawMapTo(cv,g,false); }
  let tt=0; for(const k in TALLY) tt+=TALLY[k];
  const st=document.getElementById('rStack'), key=document.getElementById('rStackKey');
  if(st){ st.innerHTML=''; key.innerHTML='';
    for(const k of ['domino','chain','collapse','fire','wpn','nuke']){ if(!TALLY[k]) continue; const pc=TALLY[k]/Math.max(1,tt)*100;
      const i=document.createElement('i'); i.style.width=pc+'%'; i.style.background=SRC_COL[k]; i.title=SRCNAME[k]+' '+Math.round(pc)+'%'; st.appendChild(i);
      key.innerHTML+='<b style="background:'+SRC_COL[k]+'"></b>'+SRCNAME[k]+' ×'+SRCMUL[k]+' '+Math.round(pc)+'%'; } }
  const v=document.getElementById('rViz'); if(v){ v.style.opacity='0'; setTimeout(()=>{ v.style.opacity='1'; v.animate([{transform:'translateY(12px)',opacity:0},{transform:'none',opacity:1}],{duration:420,easing:'cubic-bezier(.16,.9,.3,1)'}); },480); }
}
/* 初回だけ短い操作ヒント */""")
    U("keysOn:()=>keysOn, mapOn:()=>mapOn,","keysOn:()=>keysOn, mapOn:()=>mapOn, renderTitlePick:renderTitlePick, onResultShow:onResultShow,")
