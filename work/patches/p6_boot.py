import sys, re; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
# 1. three.js：検証した同一版（0.128.0）を複数CDNから。失敗時は再試行ボタン
p.rex(r"/\* three\.js を読み込む.*?\nloadThree\(\)\.then\(function\(\)\{\n  try \{ start\(\); \}\n  catch\(e\)\{\n    console\.error\(e\);\n    fail\('起動時にエラーが発生した。<br>'\+\(\(e&&e\.message\)\|\|e\)\);\n  \}\n\}, function\(\)\{\n  fail\('3Dライブラリ（three\.js）を読み込めなかった。<br>通信環境を確認して開き直してほしい。'\);\n\}\);\n",
'''/* three.js（0.128.0 UMD 版。onBeforeCompile・色管理・WebGLMultisampleRenderTarget の挙動をこの版で検証済み）
   同じ版を複数の CDN から順に試す。別の版へは落とさない（API 差で描画が壊れるため）。
   ※ CDN 依存のため完全オフラインでは動かない */
const THREE_URLS=[
  'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
  'https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js',
  'https://unpkg.com/three@0.128.0/build/three.min.js',
];
function loadThree(){
  return new Promise((res,rej)=>{
    if(window.THREE&&String(window.THREE.REVISION)==='128') return res();
    let i=0;
    (function next(){
      if(i>=THREE_URLS.length) return rej();
      boot(.04+i*.03,'3Dライブラリを読み込み中…'+(i?'（別の配信元で再試行 '+i+'）':''));
      const s=document.createElement('script');
      s.src=THREE_URLS[i++];
      s.onload=()=>{ (window.THREE&&String(window.THREE.REVISION)==='128') ? res() : next(); };
      s.onerror=()=>{ s.remove(); next(); };
      document.head.appendChild(s);
    })();
  });
}
let _started=false;
function bootLoad(){
  loadThree().then(function(){
    if(_started) return; _started=true;
    try { start(); }
    catch(e){
      console.error(e);
      fail('起動時にエラーが発生した。<br>'+((e&&e.message)||e)+'<br><br><button class="pb hi" onclick="location.reload()">再読み込み</button>');
    }
  }, function(){
    boot(0,'3Dライブラリ（three.js）を読み込めなかった。通信環境を確認して再試行してほしい。');
    const rb=document.getElementById('bootRetry');
    if(rb){ rb.style.display=''; rb.onclick=()=>{ rb.style.display='none'; bootLoad(); }; }
  });
}
bootLoad();
''')
# 2. 起動：街のメッシュが出来るまで起動画面を残し、できたらプレイへ。再生成時も同じ覆いを短く出す
p.rep("boot(.3,'シーンを構築中…');\ninitScene();\napplyLevel(0,true);\nboot(.5,'東京を生成中…');\ngenCity();\nboot(.9,'完了');\ndocument.getElementById('boot').style.display='none';\ndocument.getElementById('hud').style.display='block';",
'''boot(.3,'シーンを構築中…');
initScene();
applyLevel(0,true);
boot(.5,'東京を生成中…');
genCity();
boot(.6,'街を構築中…');
document.getElementById('hud').style.display='block';''')
p.rep("function buildQueued(){\n  if(!meshQ.length) return;", "let booting=true, meshQTotal=1;\nfunction finishBoot(){\n  booting=false;\n  const b=document.getElementById('boot'); if(b) b.style.display='none';\n  needFrame=true;\n}\nfunction buildQueued(){\n  if(!meshQ.length){ if(booting) finishBoot(); return; }")
p.rep("  while(meshQ.length && budget>0){\n    const b=meshQ.shift();\n    budget-=b.W*b.H*b.D;\n    remesh(b);\n  }\n  if(!meshQ.length){ buildHalos(); buildGlowFloor(); }",
      "  while(meshQ.length && budget>0){\n    const b=meshQ.shift();\n    budget-=b.W*b.H*b.D;\n    remesh(b);\n  }\n  if(booting) boot(.6+.4*(1-meshQ.length/Math.max(1,meshQTotal)),'街を構築中…');\n  if(!meshQ.length){ buildHalos(); buildGlowFloor(); if(booting) finishBoot(); }")
p.rep("  deferMesh=false;\n  totalVox=Math.max(1,totalVox);", "  deferMesh=false;\n  meshQTotal=Math.max(1,meshQ.length);\n  if(!booting && meshQ.length>6){ booting=true; const bt=document.getElementById('boot'); if(bt){ bt.style.display='flex'; boot(.6,'街を構築中…'); } }   // 再生成：見えていない街へ撃てる状態で始めない\n  totalVox=Math.max(1,totalVox);")
p.rep("function uiBlocked(){ return paused || resultOn", "function uiBlocked(){ return booting || paused || resultOn")
# 3. 記録の版管理：新しい採点仕様は別の鍵に保存し、旧記録は上書きしない
p.rep("function bestKey(){ return 'tt_best_'+MAPID+'_'+MODE; }\nfunction loadBest(){ try{ const v=localStorage.getItem(bestKey()); return v?JSON.parse(v):null; }catch(e){ return null; } }\nfunction saveBest(o){ try{ localStorage.setItem(bestKey(), JSON.stringify(o)); }catch(e){} }",
      "const SAVE_VER=2;                       // 採点仕様の版。変わったら鍵を変え、過去の記録は残す\nfunction bestKey(){ return 'tt'+SAVE_VER+'_best_'+MAPID+'_'+MODE; }\nfunction loadBest(){ try{ const v=localStorage.getItem(bestKey()); const o=v?JSON.parse(v):null; return (o&&o.v===SAVE_VER)?o:null; }catch(e){ return null; } }\nfunction saveBest(o){ try{ o.v=SAVE_VER; o.seed=citySeed; o.at=Date.now(); localStorage.setItem(bestKey(), JSON.stringify(o)); }catch(e){} }")
# 4. ゲーム用乱数（損傷の抽選）を装飾用（粒子）の Math.random から分離する
p.rep("let citySeed=0;\nfunction mulberry32(a){", "let citySeed=0, _grs=1;\nfunction grnd(){ _grs=(_grs*1664525+1013904223)>>>0; return _grs/4294967296; }   // ゲーム用乱数：損傷・誘爆・延焼の抽選\nfunction mulberry32(a){")
p.rep("  resetWorld();\n  const _rnd=Math.random;", "  resetWorld();\n  _grs=(citySeed^0x5bd1e995)>>>0;\n  const _rnd=Math.random;")
p.rep("      n+=hitVoxel(b,x,y,z,pow*Math.max(.12,1-d/fr)*(.72+Math.random()*.56));", "      n+=hitVoxel(b,x,y,z,pow*Math.max(.12,1-d/fr)*(.72+grnd()*.56));")
p.rep("    const h=c.hp[i]-pow*(1-d/r)*(.7+Math.random()*.6);", "    const h=c.hp[i]-pow*(1-d/r)*(.7+grnd()*.6);")
p.rep("        if(hitVoxel(b,x,y,z,pow*f*(.6+Math.random()*.8))){", "        if(hitVoxel(b,x,y,z,pow*f*(.6+grnd()*.8))){")
p.rep("    if(Math.random()<.94){ k+=killVoxel(b,x,worstY,z,k%3!==0); }", "    if(grnd()<.94){ k+=killVoxel(b,x,worstY,z,k%3!==0); }")
p.rep("    if(M.boom && blasts.length<BLAST_CAP && Math.random()<blastChance())", "    if(M.boom && blasts.length<BLAST_CAP && grnd()<blastChance())")
p.rep("  if(b.wood && KSRC!=='fire' && fires.length<FIRECAP && Math.random()<.03){", "  if(b.wood && KSRC!=='fire' && fires.length<FIRECAP && grnd()<.03){")
p.rep("  if(Math.random()>p) return;\n  fires.push({x:px, y:py, z:pz, t: wood?rf(14,22):rf(6,11)", "  if(grnd()>p) return;\n  fires.push({x:px, y:py, z:pz, t: wood?rf(14,22):rf(6,11)")
p.rep("  const b=cand[(Math.random()*cand.length)|0];\n  const fx0=b.ox+rf(0,b.W*VOX), fz0=b.oz+rf(0,b.D*VOX);", "  const b=cand[(grnd()*cand.length)|0];\n  const fx0=b.ox+rf(0,b.W*VOX), fz0=b.oz+rf(0,b.D*VOX);")
# 5. 検証フック：URL に debug を付けても有効。性能・資源・時計・seed・入力の状態
p.rep("if(window.TT_DEBUG) window.__tt={", "if(window.TT_DEBUG || /[?#&]debug/.test(location.search+location.hash)) window.__tt={")
p.rep("  showResult:showResult, hideResult:hideResult, canShoot:canShoot, setFireHeld:(v)=>{fireHeld=v;}, getSlow:()=>({slowT,slowK}), loop:loop,\n};",
'''  showResult:showResult, hideResult:hideResult, canShoot:canShoot, setFireHeld:(v)=>{fireHeld=v;}, getSlow:()=>({slowT,slowK}), loop:loop,
  // ── 改修版で追加 ──
  seed:()=>citySeed, setSeed:(s)=>genCity(MAPID,s), genCityKeep:(m)=>genCity(m===undefined?MAPID:m,citySeed), grnd:grnd,
  setPaused:setPaused, isPaused:()=>paused, booting:()=>booting,
  perf:()=>({avg:QUAL.lastAvg,worst:QUAL.lastWorst,ring:Array.from(QUAL.ring),level:QUAL.level,mode:QUAL.mode,pr:QUAL.pr}),
  resources:()=>({geometries:renderer.info.memory.geometries,textures:renderer.info.memory.textures,calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,programs:renderer.info.programs?renderer.info.programs.length:-1}),
  pixelRatio:()=>renderer.getPixelRatio(), clock:()=>({run:runElapsed,runLeft:runLeft,slowK:slowK,real:performance.now()}),
  sndVoices:()=>Snd.voices(), toppling:()=>TOPPLING, QLV:QLV, applyLevel:applyLevel,
  releasePointers:releasePointers, ptr:()=>Array.from(PTR.entries()), fireHeld:()=>fireHeld, openMenu:openMenu, closeMenu:closeMenu,
  TRFcars:()=>TRF.cars, PARKED:()=>PARKED, causeToast:causeToast, chipTest:()=>MATS,
};''')
p.rep("    if(!T||b.live<=0||b.culledGone){ if(T) bldPoseReset(b); b.toppling=null; TOPPLING.splice(i,1); continue; }",
      "    if(!T||b.live<=0){ if(T) bldPoseReset(b); b.toppling=null; TOPPLING.splice(i,1); continue; }")
p.save()
