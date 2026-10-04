# MacBook 向け：F1/F2 は輝度キーなので代替キー、トラックパッド向けのマウス視点モード（ロック／ホバー／ドラッグ）
TITLE='Mac のキー事情とマウス視点モード'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    B=lambda a,b,c=1: src.rep('body',a,b,c)
    # ── キー：操作一覧は / (Slash) でも、性能表示は O でも開く ──
    U("const GAME_KEYS=new Set(['Space','Tab','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter','F1','F2',",
      "const GAME_KEYS=new Set(['Space','Tab','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter','F1','F2','Slash','KeyO',")
    U("    if(code==='Escape'||(code==='KeyP'&&ov!==keysEl)||(code==='F1'&&ov===keysEl)){ if(!rep) closeTop(); e.preventDefault(); return; }",
      "    if(code==='Escape'||(code==='KeyP'&&ov!==keysEl)||((code==='F1'||code==='Slash')&&ov===keysEl)){ if(!rep) closeTop(); e.preventDefault(); return; }")
    U("    if(ov===titleEl && code==='F1' && !rep){ openKeys(); e.preventDefault(); return; }",
      "    if(ov===titleEl && (code==='F1'||code==='Slash') && !rep){ openKeys(); e.preventDefault(); return; }")
    U("    case 'F1': openKeys(); break;\n    case 'F2': togglePerf(); break;",
      "    case 'F1': case 'Slash': openKeys(); break;\n    case 'F2': case 'KeyO': togglePerf(); break;")
    U("el.keyhint.innerHTML='<b>'+W.n+'</b>　'+(WHINT[W.id]||'')+'<br><span>WASD 移動　↑↓←→ 視点　E/Q 上下　Shift 加速　Z/C 武器　Tab 一覧　V ズーム　T 俯瞰　Esc メニュー'+(PAD.on?'　🎮 パッド有効':'')+'</span>';",
      "el.keyhint.innerHTML='<b>'+W.n+'</b>　'+(WHINT[W.id]||'')+'<br><span>WASD 移動　↑↓←→ 視点　E/Q 上下　Shift 加速　Z/C 武器　Tab 一覧　V ズーム　T 俯瞰　Esc メニュー　/ 操作一覧'+(PAD.on?'　🎮 パッド有効':'')+'</span>';")
    B('<button class="pb" id="tKeysBtn">操作方法　<kbd>F1</kbd></button>','<button class="pb" id="tKeysBtn">操作方法　<kbd>/</kbd></button>')
    B('<div class="k"><kbd>H</kbd><kbd>F2</kbd></div><div class="v">HUD表示切替／性能表示</div>','<div class="k"><kbd>H</kbd><kbd>O</kbd></div><div class="v">HUD表示切替／性能表示（F2 でも）</div>')
    B('<div class="k"><kbd>H</kbd> / <kbd>F2</kbd></div><div class="v">HUD表示切替 ／ 性能表示</div>','<div class="k"><kbd>H</kbd> / <kbd>O</kbd></div><div class="v">HUD表示切替 ／ 性能表示（MacBook の F1/F2 は輝度キーなので / と O を用意）</div>')
    B('<button class="pb sub" id="bHint">操作方法 (F1)</button>','<button class="pb sub" id="bHint">操作方法 ( / )</button>')
    B('<div class="k"><kbd>Esc</kbd></div><div class="v">メニュー（設定・マップ・モード）。メニューも矢印キーと Enter で操作</div>',
      '<div class="k"><kbd>Esc</kbd></div><div class="v">メニュー（設定・マップ・モード）。メニューも矢印キーと Enter で操作</div>\n      <div class="k"><kbd>/</kbd></div><div class="v">操作一覧（MacBook の F1 は輝度キー）</div>')
    # ── マウス視点モード：ロック（クリックで取得）／ホバー（動かすだけで視点。トラックパッド向け）／ドラッグ ──
    U("const PCS={q:'auto',scale:1,fov:75,sens:5,invY:false,ao:true,snd:true,fx:1,hud:true};",
      "const PCS={q:'auto',scale:1,fov:75,sens:5,invY:false,ao:true,snd:true,fx:1,hud:true,mlook:'lock'};   // mlook: lock | hover | drag")
    U("function lockOk(){ return !window.TT_NOLOCK && !lockFailed && !!(document.body.requestPointerLock||document.body.mozRequestPointerLock); }",
      "function lockOk(){ return PCS.mlook==='lock' && !window.TT_NOLOCK && !lockFailed && !!(document.body.requestPointerLock||document.body.mozRequestPointerLock); }")
    U("""  if(locked) lookPx(e.movementX||0,e.movementY||0);
  else { const p=PTR.get('m'); if(p){ lookPx(e.clientX-p.x,e.clientY-p.y); p.x=e.clientX; p.y=e.clientY; } }""",
      """  if(locked) lookPx(e.movementX||0,e.movementY||0);
  else if(PCS.mlook==='hover' && !PTR.has('m')) lookPx(e.movementX||0,e.movementY||0);          // ホバー：動かすだけで視点（トラックパッド向け）
  else { const p=PTR.get('m'); if(p){ lookPx(e.clientX-p.x,e.clientY-p.y); p.x=e.clientX; p.y=e.clientY; } }""")
    # メニューに行を追加
    B('<div class="row"><span class="lb">視点の速さ</span>','<div class="row"><span class="lb">マウス視点</span><div class="row" id="pmLookRow" style="margin:0;flex:1"></div></div>\n  <div class="row"><span class="lb">視点の速さ</span>')
    U("  document.getElementById('pmSensV').textContent=PCS.sens;",
      """  const lk=document.getElementById('pmLookRow'); lk.innerHTML='';
  [['lock','ロック（クリックで取得）'],['hover','ホバー（動かすだけ・トラックパッド向け）'],['drag','ドラッグ']].forEach(([m,n])=>{ lk.appendChild(mkPB(n,PCS.mlook===m,()=>{ PCS.mlook=m; savePCS(); if(m!=='lock'&&locked){ try{ document.exitPointerLock(); }catch(e){} } renderMenu(); },'pmL_'+m)); });
  document.getElementById('pmSensV').textContent=PCS.sens;""")
    U("  PCS.scale=clampN(+PCS.scale||1,.5,2); PCS.fov=clampN(+PCS.fov||75,55,110); PCS.sens=clampN((+PCS.sens||5)|0,1,10);",
      "  PCS.scale=clampN(+PCS.scale||1,.5,2); PCS.fov=clampN(+PCS.fov||75,55,110); PCS.sens=clampN((+PCS.sens||5)|0,1,10);\n  if(!['lock','hover','drag'].includes(PCS.mlook)) PCS.mlook='lock';")
    B('<div class="k">移動</div><div class="v">視点（クリックでロック）</div>','<div class="k">移動</div><div class="v">視点（クリックでロック。トラックパッドは設定で「ホバー」に）</div>')
