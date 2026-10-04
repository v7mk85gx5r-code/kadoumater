# 初回チュートリアル：達成式のチェックリスト（見回す→移動→発射→武器切替→メニュー）。全部できたら消える
TITLE='初回チュートリアル（達成式）'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    C=lambda a,b,c=1: src.rep('css',a,b,c)
    B=lambda a,b,c=1: src.rep('body',a,b,c)
    B('  <div id="hint"></div>\n</div>','  <div id="hint"></div>\n  <div id="tut"><div class="h">はじめの操作</div><ol id="tutList"></ol><div class="f">全部できたら消えます　<kbd>/</kbd> 操作一覧</div></div>\n</div>')
    C('#perf{position:absolute;left:18px;top:110px;', """#tut{position:absolute;left:18px;top:50%;transform:translateY(-50%);width:300px;background:rgba(6,10,16,.78);border:1px solid var(--edge);border-radius:14px;
  padding:12px 14px;display:none;pointer-events:none;z-index:11;}
#tut.on{display:block;}
#tut .h{font-size:10px;letter-spacing:.34em;color:var(--cyan);font-weight:800;margin-bottom:6px;}
#tut ol{list-style:none;margin:0;padding:0;}
#tut li{display:flex;align-items:center;gap:10px;padding:6px 0;font-size:12.5px;color:var(--ink);border-bottom:1px solid rgba(255,255,255,.06);transition:opacity .4s;}
#tut li i{flex:0 0 18px;width:18px;height:18px;border-radius:50%;border:1.5px solid var(--dim);display:flex;align-items:center;justify-content:center;font-size:11px;font-style:normal;color:#000;}
#tut li.done{opacity:.45;} #tut li.done i{background:var(--cyan);border-color:var(--cyan);}
#tut li.done i::after{content:"✓";font-weight:900;}
#tut li.cur{color:#fff;} #tut li.cur i{border-color:var(--cyan);box-shadow:0 0 10px rgba(79,227,240,.6);}
#tut .f{margin-top:8px;font-size:10.5px;color:var(--dim);}
#tut.fin .h{color:var(--gold);}
#perf{position:absolute;left:18px;top:110px;""")
    U("/* 初回だけ短い操作ヒント */", """/* 初回チュートリアル：やってみれば分かることを、達成式で順に促す */
const TUT={on:false, done:false, steps:[
  {id:'look', t:'<kbd>↑↓←→</kbd> で見回す', v:0},
  {id:'move', t:'<kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> で移動（<kbd>Shift</kbd> 加速）', v:0},
  {id:'fire', t:'<kbd>Space</kbd> で発射', v:0},
  {id:'wpn',  t:'<kbd>Z</kbd> / <kbd>C</kbd> で武器を切り替える', v:0},
  {id:'menu', t:'<kbd>Tab</kbd> で武器一覧、<kbd>Esc</kbd> でメニュー', v:0},
], last:{yaw:0,pitch:0,x:0,z:0,shots:0,wpn:'missile'}, acc:{look:0,move:0}, finT:0};
function tutStart(){
  let seen=false; try{ seen=!!localStorage.getItem('tt_pc_tut'); }catch(e){}
  if(seen||TUT.done) return;
  TUT.on=true; TUT.last={yaw:cam.yaw,pitch:cam.pitch,x:cam.pos.x,z:cam.pos.z,shots:S.shots,wpn:wpn}; TUT.acc.look=0; TUT.acc.move=0;
  const ol=document.getElementById('tutList'); ol.innerHTML='';
  TUT.steps.forEach((s,i)=>{ s.v=0; const li=document.createElement('li'); li.id='tut_'+s.id; li.innerHTML='<i></i><span>'+s.t+'</span>'; if(i===0) li.classList.add('cur'); ol.appendChild(li); });
  document.getElementById('tut').classList.add('on');
}
function tutMark(id){ const s=TUT.steps.find(x=>x.id===id); if(!s||s.v) return; s.v=1; const li=document.getElementById('tut_'+id); if(li){ li.classList.add('done'); li.classList.remove('cur'); } Snd.kick();
  const nxt=TUT.steps.find(x=>!x.v); if(nxt){ const n=document.getElementById('tut_'+nxt.id); if(n) n.classList.add('cur'); }
  else { TUT.finT=2.6; const t=document.getElementById('tut'); t.classList.add('fin'); t.querySelector('.h').textContent='完了！あとは好きなように壊そう'; try{ localStorage.setItem('tt_pc_tut','1'); }catch(e){} } }
function updTut(dt){
  if(!TUT.on) return;
  const t=document.getElementById('tut');
  if(TUT.finT>0){ TUT.finT-=dt; if(TUT.finT<=0){ TUT.on=false; TUT.done=true; t.classList.remove('on'); t.classList.remove('fin'); } return; }
  const L=TUT.last;
  TUT.acc.look+=Math.abs(cam.yaw-L.yaw)+Math.abs(cam.pitch-L.pitch); L.yaw=cam.yaw; L.pitch=cam.pitch;
  TUT.acc.move+=Math.hypot(cam.pos.x-L.x,cam.pos.z-L.z); L.x=cam.pos.x; L.z=cam.pos.z;
  if(TUT.acc.look>0.6) tutMark('look');
  if(TUT.acc.move>30) tutMark('move');
  if(S.shots>L.shots||railOn||gunOn) tutMark('fire');
  if(wpn!==L.wpn) tutMark('wpn');
  if(menuOpen()||panelOpen()) tutMark('menu');
  t.style.opacity = (titleOn||keysOn||mapOn||resultOn) ? '0' : '1';
}
/* 初回だけ短い操作ヒント */""")
    U("  if(mouseUsed) requestLock();\n  showHint();\n  banner(MAPNAMES[MAPID],modeDef().lbl);","  if(mouseUsed) requestLock();\n  tutStart(); if(!TUT.on) showHint();\n  banner(MAPNAMES[MAPID],modeDef().lbl);")
    U("function updHUD(dt){\n  updAimRings(dt); updHitMark(dt); drawCompass(dt);","function updHUD(dt){\n  updAimRings(dt); updHitMark(dt); drawCompass(dt); updTut(dt);")
    U("keysOn:()=>keysOn, mapOn:()=>mapOn,","keysOn:()=>keysOn, mapOn:()=>mapOn, tut:()=>TUT, tutStart:tutStart,")
