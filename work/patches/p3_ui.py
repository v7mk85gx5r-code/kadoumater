import sys, re; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
css=open('/home/user/kadoumater/work/ui/style.css',encoding='utf-8').read()
body=open('/home/user/kadoumater/work/ui/body.html',encoding='utf-8').read()
ui=open('/home/user/kadoumater/work/ui/ui.js',encoding='utf-8').read()
# 1. CSS
p.rex(r'<style>.*?</style>', '<style>\n'+css+'</style>')
# 2. body markup
p.rex(r'<body>.*?<div id="vig"></div>\n', body)
# 3. HUD〜入力の JS を差し替え
p.rex(r'/\* ══════════ HUD ══════════ \*/\nconst el=\{.*?\n/\* ══════════ 初期化 ══════════ \*/', ui+'\n/* ══════════ 初期化 ══════════ */')
# 4. 街の seed：生成用乱数を seed で固定し、装飾（粒子）の乱数とは分ける
p.rep('''function genCity(mapId){
  if(mapId!==undefined) MAPID=((mapId%3)+3)%3;
  resetWorld();
  deferMesh=true; meshQ=[];
  if(MAPID===0){ layoutKabuki(); buildKabuki(); }
  else if(MAPID===1){ layoutShibuya(); buildShibuya(); }

  else { layoutHigh(); buildHigh(); }
  deferMesh=false;''',
'''let citySeed=0;
function mulberry32(a){ return function(){ a|=0; a=a+0x6D2B79F5|0; let t=Math.imul(a^a>>>15,1|a); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }
/* 街の生成。seed を渡せば同じ街になる（「同じ街に再挑戦」）。省略すると新しい seed */
function genCity(mapId,seed){
  if(mapId!==undefined&&mapId!==null) MAPID=((mapId%3)+3)%3;
  citySeed=(seed!==undefined&&seed!==null)?(seed>>>0):((Math.random()*4294967296)>>>0);
  resetWorld();
  const _rnd=Math.random;
  Math.random=mulberry32(citySeed^Math.imul(MAPID+1,0x9E3779B1));   // 生成中だけ seed 付き乱数に差し替える
  try{
  deferMesh=true; meshQ=[];
  if(MAPID===0){ layoutKabuki(); buildKabuki(); }
  else if(MAPID===1){ layoutShibuya(); buildShibuya(); }
  else { layoutHigh(); buildHigh(); }
  deferMesh=false;''')
p.rep('''  buildTraffic();
  buildPeds();
  buildLanterns();
  buildSignals();
  const el=document.getElementById('mapName');
  if(el) el.textContent=MAPNAMES[MAPID];
}''',
'''  buildTraffic();
  buildPeds();
  buildLanterns();
  buildSignals();
  } finally { Math.random=_rnd; }
  QUAL.settleUntil=performance.now()+4000;          // 生成直後の重さで画質を下げない
  const el=document.getElementById('mapName');
  if(el) el.textContent=MAPNAMES[MAPID];
  const ps=document.getElementById('pmSeed'); if(ps) ps.textContent='SEED '+citySeed;
}''')
# 5. 起動後：クイックバー・ヒント・演出設定の読み込み
p.rep("document.getElementById('hud').style.display='block';\nselW('missile');\nsetMode('free');",
      "document.getElementById('hud').style.display='block';\ntry{ const v=parseFloat(localStorage.getItem('tt2_fx')); if(v>0&&v<=1) QUAL.fxK=v; }catch(e){}\nselW('missile');\nsetMode('free');\nshowHint();")
# 6. 振動：非保証の経路（隠しスイッチ・音の代替）を使わず、Vibration API がある端末だけ振動させる
p.rex(r"let hapticOn=true, hapT=0, hapSw=null, hapLb=null, hapIOSok=false;\nconst HAP_VIB = .*?\nfunction hap\(pattern, minGap\)\{.*?\n\}\n",
'''let hapticOn=true, hapT=0, hapSw=null, hapLb=null, hapIOSok=false;
const HAP_VIB = (typeof navigator!=='undefined' && typeof navigator.vibrate==='function');
function initHaptics(){ try{ hapticOn = localStorage.getItem('tt2_hap')!=='0'; }catch(e){} }
const HAP_SUPPORT = HAP_VIB;   // 対応している端末だけ「振動」を名乗る（iOS Safari は非対応）
function hap(pattern, minGap){
  if(!hapticOn||!HAP_VIB) return;
  const now=performance.now();
  if(now-hapT < (minGap||0)) return;
  hapT=now;
  try{ navigator.vibrate(pattern); }catch(e){}
}
''')
p.rep("  const bh=document.getElementById('bHap'); bh.textContent=hapticOn?'振動':'振動 OFF'; bh.classList.toggle('on',hapticOn);",
      "  const bh=document.getElementById('bHap'); bh.textContent=HAP_VIB?(hapticOn?'振動':'振動 OFF'):'振動（非対応）'; bh.classList.toggle('on',hapticOn&&HAP_VIB); bh.style.opacity=HAP_VIB?'1':'.5';")
p.rep("document.getElementById('bHap').addEventListener('click',e=>{ e.stopPropagation(); hapticOn=!hapticOn; renderMenu(); if(hapticOn) hap(HAP.hit,0); });",
      "document.getElementById('bHap').addEventListener('click',e=>{ e.stopPropagation(); if(!HAP_VIB) return; hapticOn=!hapticOn; try{ localStorage.setItem('tt2_hap',hapticOn?'1':'0'); }catch(err){} renderMenu(); if(hapticOn) hap(HAP.hit,0); });")
# 7. 性能表示（検証時だけ）：フレーム時間の分布・処理区間・塊数・待ち行列・描画資源
p.rep("/* ══════════ 初期化 ══════════ */\nfunction initScene(){",
'''/* ══════════ 性能表示（検証用。通常は隠す） ══════════ */
function drawPerf(avg,worst){
  const d=document.getElementById('perf'); if(!d) return;
  const r=Array.from(QUAL.ring).filter(v=>v>0).sort((a,b)=>a-b);
  const q=(k)=>r.length?r[Math.min(r.length-1,(r.length*k)|0)].toFixed(1):'-';
  const info=renderer?renderer.info:null;
  d.textContent=
    'frame avg '+avg.toFixed(1)+'ms  p50 '+q(.5)+'  p95 '+q(.95)+'  worst '+worst.toFixed(0)+'ms\\n'+
    'quality '+QUAL.mode+' L'+QUAL.level+' pr'+QUAL.pr.toFixed(2)+(POST.on?(POST.hdr?' HDR':' 8bit')+(POST.msaa?' MSAA':'')+(WET.on?' refl/'+WET.every:''):' noPost')+'\\n'+
    'step wpn '+PROF.wpn.toFixed(1)+' chunk '+PROF.chunk.toFixed(1)+' bfs '+PROF.bfs.toFixed(1)+' mesh '+PROF.mesh.toFixed(1)+' fx '+PROF.fx.toFixed(1)+'ms\\n'+
    'chunks '+chunks.length+' meshQ '+meshQ.length+' zoneQ '+zoneQ.length+' rubble '+rubMeshes.length+'/'+rubTris+'tri\\n'+
    'smoke '+VFX.sa.length+' fire '+VFX.fa.length+' spark '+VFX.pa.length+' pts '+fx.length+'/'+gxA.length+' debris '+DEB.arr.length+' peds '+PED.list.length+' fires '+fires.length+'\\n'+
    (info?('gpu geo '+info.memory.geometries+' tex '+info.memory.textures+' calls '+info.render.calls+' tris '+info.render.triangles):'');
}
/* ══════════ 初期化 ══════════ */
function initScene(){''')
p.save()
