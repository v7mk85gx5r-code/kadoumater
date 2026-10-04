# 操作スタイルの選択（タイトル：キーボードのみ／マウス／トラックパッド／ゲームパッド）、ホバー視点の画面端ターン、武器一覧の案内強化、Retina の細い罫線
TITLE='操作スタイル選択・ホバー視点の端ターン・武器一覧の案内・Retina 罫線'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    C=lambda a,b,c=1: src.rep('css',a,b,c)
    B=lambda a,b,c=1: src.rep('body',a,b,c)
    # ── タイトルに操作スタイルの行 ──
    B('    <div class="tPick"><span>マップ</span><div id="tMaps"></div></div>','    <div class="tPick"><span>操作</span><div id="tInput"></div></div>\n    <div class="tPick"><span>マップ</span><div id="tMaps"></div></div>')
    U("const PCS={q:'auto',scale:1,fov:75,sens:5,invY:false,ao:true,snd:true,fx:1,hud:true,mlook:'lock',fps:0,amb:1};",
      "const PCS={q:'auto',scale:1,fov:75,sens:5,invY:false,ao:true,snd:true,fx:1,hud:true,mlook:'lock',fps:0,amb:1,istyle:'kb'};   // istyle: kb | mouse | pad(トラックパッド) | gp")
    U("""function renderTitlePick(){
  const tm=document.getElementById('tMaps'); if(!tm) return; tm.innerHTML='';""","""const ISTYLES=[['kb','キーボードのみ'],['mouse','マウス'],['pad','トラックパッド'],['gp','ゲームパッド']];
function applyIStyle(s){ PCS.istyle=s; PCS.mlook = s==='pad' ? 'hover' : (s==='mouse' ? 'lock' : PCS.mlook); if(s==='kb') PCS.mlook='drag'; savePCS(); updKeyHint(); }
function renderTitlePick(){
  const ti=document.getElementById('tInput'); if(ti){ ti.innerHTML=''; ISTYLES.forEach(([s,n])=>{ ti.appendChild(mkPB(n,PCS.istyle===s,()=>{ applyIStyle(s); renderTitlePick(); knavOpen(titleEl,'tI_'+s); wToast({kb:'矢印キーで視点、Space で発射。マウスは使いません',mouse:'クリックで視点をロック。Esc で解除',pad:'トラックパッドの指の動きがそのまま視点になります（ホバー）。画面端で振り向きが続きます',gp:'Standard 配列。右スティック視点、RT 発射、Start メニュー'}[s]); },'tI_'+s)); }); }
  const tm=document.getElementById('tMaps'); if(!tm) return; tm.innerHTML='';""")
    U("  if(!['lock','hover','drag'].includes(PCS.mlook)) PCS.mlook='lock';","  if(!['lock','hover','drag'].includes(PCS.mlook)) PCS.mlook='lock';\n  if(!['kb','mouse','pad','gp'].includes(PCS.istyle)) PCS.istyle='kb';")
    # キーヒント：スタイルに応じて
    U("+'<br><span>WASD 移動　↑↓←→ 視点　E/Q 上下　Shift 加速　Z/C 武器　Tab 一覧　V ズーム　T 俯瞰　M 地図　Esc メニュー　/ 操作一覧'+(PAD.on?'　🎮 パッド有効':'')+'</span>';",
      "+'<br><span>'+(PCS.istyle==='gp'?'左スティック 移動　右スティック 視点　RT 発射　LB/RB 武器　Y 一覧　X 起爆　Start メニュー':(PCS.istyle==='pad'?'WASD 移動　指の動き＝視点　クリック 発射　二本指スクロール 武器　Z/C 武器　Tab 一覧　Esc メニュー':'WASD 移動　↑↓←→ 視点　E/Q 上下　Shift 加速　Z/C 武器　Tab 一覧　V ズーム　T 俯瞰　M 地図　Esc メニュー　/ 操作一覧'))+(PAD.on?'　🎮 パッド有効':'')+'</span>';")
    # ── ホバー視点：画面端で振り向きが続く ──
    U("let locked=false, mouseUsed=false, lockFails=0, lockFailed=false;","let locked=false, mouseUsed=false, lockFails=0, lockFailed=false;\nconst mouseAt={x:-1,y:-1,in:false};")
    U("window.addEventListener('mousemove',e=>{\n  mouseUsed=true;","window.addEventListener('mousemove',e=>{\n  mouseUsed=true; mouseAt.x=e.clientX; mouseAt.y=e.clientY; mouseAt.in=true;")
    U("window.addEventListener('blur',()=>releasePointers());","window.addEventListener('blur',()=>releasePointers());\ndocument.addEventListener('mouseleave',()=>{ mouseAt.in=false; });")
    U("  const zt=Math.max((zoomHeld||PAD.zoom)?1:0, zoomToggle?ZOOM_STAGES[zoomStage]:0);","""  if(PCS.mlook==='hover' && !locked && mouseAt.in && mouseUsed && !CUT.on){        // 画面端で振り向きが続く（トラックパッド向け）
    const ex=Math.max(1,window.innerWidth*.04), ey=Math.max(1,window.innerHeight*.06);
    let kx=0, ky=0;
    if(mouseAt.x<ex) kx=-(1-mouseAt.x/ex); else if(mouseAt.x>window.innerWidth-ex) kx=(1-(window.innerWidth-mouseAt.x)/ex);
    if(mouseAt.y<ey) ky=-(1-mouseAt.y/ey); else if(mouseAt.y>window.innerHeight-ey) ky=(1-(window.innerHeight-mouseAt.y)/ey);
    if(kx||ky) lookPx(kx*KEYLOOK_PX*dt, ky*KEYLOOK_PX*.6*dt);
  }
  const zt=Math.max((zoomHeld||PAD.zoom)?1:0, zoomToggle?ZOOM_STAGES[zoomStage]:0);""")
    # ── 武器一覧の案内：クールダウン秒・キー・初心者向けの一言 ──
    U("function showWDesc(W){ el.wdesc.innerHTML='<b>'+W.n+'</b>　'+W.d; }",
      """const WTIP={missile:'まずはこれ。連打できる',gun:'窓と外壁を削る。長押し',rail:'照射しながら視点を動かすと切れる',cutter:'足元を切って隣へ倒すと高得点',carpet:'通りに沿って撃つと効率がいい',incend:'木造（ゴールデン街）に効く',grav:'密集地の中心に置く',orbit:'高層ビルの真上から',demo:'片側に寄せて置くと倒す向きが決まる',meteor:'爆発しない。上から貫く',ball:'当てた方向へ倒れる',orb:'加点なし。最後の掃除用',nuke:'加点なし。最後の掃除用'};
function showWDesc(W){ const i=WPN.indexOf(W); el.wdesc.innerHTML='<b>'+W.n+'</b>　'+W.d+'<br><span style="color:var(--dim);font-size:11px">キー '+WKEYS[i]+'　'+(W.cont?'連続（長押し）':(W.cd>=1?'再使用 '+W.cd+' 秒':'連射間隔 '+W.cd+' 秒'))+'　'+(WTIP[W.id]||'')+'</span>'; }""")
    # ── Retina：細い罫線 ──
    C('@media (max-width:1100px){', """@media (min-resolution:2dppx){ .q,.w,.sheet,.pb,#minimap,#wtoast,#hint,#tut,#tKeys,.rBtn,#det{border-width:.5px;} .fd{border-left-width:2px;} }
@media (max-width:1100px){""")
