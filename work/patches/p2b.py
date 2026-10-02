import sys; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
# ループ用の状態は先頭で宣言（resetWorld/resize が起動時に触るため TDZ を避ける）
p.rep("let last=performance.now(), paused=false, ctxLost=false, runElapsed=0, realDt=.016, needFrame=true;\nlet onPauseChange=null;            // UI 側が差し替える（ポーズメニューの表示）\n",
      "last=performance.now();\n")
p.rep("function dampK(k){ return Math.pow(k,dtK); }                            // 毎フレーム k 倍の減衰",
      "function dampK(k){ return Math.pow(k,dtK); }                            // 毎フレーム k 倍の減衰\n/* ループの状態（起動時に resetWorld/resize から触るので先頭で宣言） */\nlet last=0, paused=false, ctxLost=false, runElapsed=0, realDt=.016, needFrame=true;\nlet onPauseChange=null, onCtxLost=null;   // UI 側が差し替える（ポーズメニュー／描画中断の表示）")
# WebGL コンテキスト喪失・復元
p.rep("  renderer.setClearColor(FOGC,1);\n  document.body.insertBefore(renderer.domElement,document.getElementById('hud'));",
'''  renderer.setClearColor(FOGC,1);
  document.body.insertBefore(renderer.domElement,document.getElementById('hud'));
  renderer.domElement.addEventListener('webglcontextlost',(e)=>{
    e.preventDefault();                                   // 復元を許可する
    ctxLost=true; setPaused(true,'ctx');
    if(onCtxLost) onCtxLost(true);
  },false);
  renderer.domElement.addEventListener('webglcontextrestored',()=>{
    ctxLost=false;
    try{ resizePost(); }catch(e){}
    if(LITU.uLM.value) LITU.uLM.value.needsUpdate=true;
    last=performance.now(); needFrame=true;
    if(onCtxLost) onCtxLost(false);
  },false);''')
# 起動時に段階設定を一度適用する
p.rep("boot(.3,'シーンを構築中…');\ninitScene();", "boot(.3,'シーンを構築中…');\ninitScene();\napplyLevel(0,true);")
p.save()
