# 共通の差し込み口：複数の機能が同じ行を奪い合わないよう、フック配列とマーカーを 1 回だけ用意する
#   HOOKS.init   : initScene の空の生成直後（プールやメッシュを 1 度だけ作る）           f()
#   HOOKS.build  : genCity の最後（seed 付き乱数の中。街の付属物を配置する）             f()
#   HOOKS.reset  : resetWorld（再生成の前にリストを空にする）                              f()
#   HOOKS.update : step の毎フレーム（他の updXxx の後）                                   f(dt)
#   HOOKS.blast  : detonate（爆風。車・歩行者・提灯と同じ場所）                            f(x,y,z,R)
#   HOOKS.lights : updLights の候補集め（cand に {x,y,z,r,c,i,tau,s} を push する）        f(cand,dt)
#   HOOKS.hud    : updHUD の毎フレーム部                                                    f(dt)
#   マーカー（置換して自分のコード＋同じマーカーを残す）:
#     /*@MATS*/ 素材表の末尾   /*@DEFS*/ 本体の定義置き場（resetWorld の直前）   /*@UI_DEFS*/ UI の定義置き場
#     /*@CSS*/ CSS の末尾   <!--@BODY--> 本文（cutline の直前）   <!--@MENU_ROWS--> メニューの「モード」の前
#     /*@MENU_RENDER*/ renderMenu の中   /*@PCS_DEF*/ 設定の既定値   /*@PCS_APPLY*/ 設定の正規化
#     /*@KEYS*/ キー処理（switch の default の前）   /*@GAME_KEYS*/ preventDefault するキー   /*@PCDBG*/ 検証フック
#     <!--@KEYS_LEGEND--> 操作一覧の末尾
TITLE='共通フックとマーカー'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    C=lambda a,b,c=1: src.rep('css',a,b,c)
    B=lambda a,b,c=1: src.rep('body',a,b,c)
    rep("const MAXCHUNK=160;","const MAXCHUNK=160;\nconst HOOKS={init:[],build:[],reset:[],update:[],blast:[],lights:[],hud:[]};   // 機能モジュールの差し込み口（work/pc/feat/19_hooks.py）\nfunction runHooks(list,a,b,c,d){ for(let i=0;i<list.length;i++){ try{ list[i](a,b,c,d); }catch(e){ if(!list[i]._err){ list[i]._err=1; console.error('hook',e); } } } }")
    rep("  skyMesh=makeSky(); scene.add(skyMesh);","  skyMesh=makeSky(); scene.add(skyMesh);\n  runHooks(HOOKS.init);")
    rep("  buildLanterns();\n  buildSignals();\n  } finally { Math.random=_rnd; }","  buildLanterns();\n  buildSignals();\n  runHooks(HOOKS.build);\n  } finally { Math.random=_rnd; }")
    rep("  LMS=[]; lmT=0; bannerLmT=0; fireHeld=false; TOPPLING=[];","  LMS=[]; lmT=0; bannerLmT=0; fireHeld=false; TOPPLING=[];\n  runHooks(HOOKS.reset);")
    rep("updLanterns(dt); updSignals(dt);","updLanterns(dt); updSignals(dt); runHooks(HOOKS.update,dt);")
    rep("  pedsBlast(x,z,R*1.0); lanternsBlast(x,z,R);","  pedsBlast(x,z,R*1.0); lanternsBlast(x,z,R); runHooks(HOOKS.blast,x,y,z,R);")
    rep("  cand.sort((a,b)=>b.s-a.s);","  runHooks(HOOKS.lights,cand,dt);\n  cand.sort((a,b)=>b.s-a.s);")
    rep("  mat.customProgramCacheKey=()=>'tt_lit_23';","  mat.customProgramCacheKey=()=>'tt_lit_'+LIT_PRE.length+'_'+LIT_MAIN.length+'_'+LIT_COLOR.length;   // シェーダ文字列が変われば鍵も変わる")
    rep("  mat.customProgramCacheKey=()=>'tt_wet_2';","  mat.customProgramCacheKey=()=>'tt_wet_'+WET_PRE.length+'_'+WET_MAIN.length;")
    rep("  45:{n:'バスケットボール', r:.86,g:.40,b:.10, hp:60, sc:2, ld:0.3},","  45:{n:'バスケットボール', r:.86,g:.40,b:.10, hp:60, sc:2, ld:0.3},\n  /*@MATS*/")
    rep("function resetWorld(){","/*@DEFS*/\nfunction resetWorld(){")
    U("/* 初回だけ短い操作ヒント */","/*@UI_DEFS*/\n/* 初回だけ短い操作ヒント */")
    U("function updHUD(dt){\n  updAimRings(dt); updHitMark(dt); drawCompass(dt); updTut(dt); updCallouts();","function updHUD(dt){\n  updAimRings(dt); updHitMark(dt); drawCompass(dt); updTut(dt); updCallouts(); runHooks(HOOKS.hud,dt);")
    C("@media (max-height:640px){ #mmWrap{display:none;} #keyhint{bottom:92px;} }","@media (max-height:640px){ #mmWrap{display:none;} #keyhint{bottom:92px;} }\n/*@CSS*/")
    B('<div id="cutline"></div>','<!--@BODY-->\n<div id="cutline"></div>')
    B('  <div class="row lbl">モード</div>','  <!--@MENU_ROWS-->\n  <div class="row lbl">モード</div>')
    U("  const pm=document.getElementById('pmModes'); pm.innerHTML='';","  /*@MENU_RENDER*/\n  const pm=document.getElementById('pmModes'); pm.innerHTML='';")
    U("amb:1,istyle:'kb'};","amb:1,istyle:'kb' /*@PCS_DEF*/};")
    U("  if(!['kb','mouse','pad','gp'].includes(PCS.istyle)) PCS.istyle='kb';","  if(!['kb','mouse','pad','gp'].includes(PCS.istyle)) PCS.istyle='kb';\n  /*@PCS_APPLY*/")
    U("    default: { const wi=KEYCODE_W[code]; if(wi!==undefined&&WPN[wi]) selW(WPN[wi].id,true); }","    /*@KEYS*/\n    default: { const wi=KEYCODE_W[code]; if(wi!==undefined&&WPN[wi]) selW(WPN[wi].id,true); }")
    U("const GAME_KEYS=new Set(['Space','Tab',","const GAME_KEYS=new Set([/*@GAME_KEYS*/'Space','Tab',")
    U("const PCDBG={","const PCDBG={ /*@PCDBG*/")
    B('  <div class="row" style="justify-content:center;margin-top:16px"><button class="pb" id="kClose2"','  <!--@KEYS_LEGEND-->\n  <div class="row" style="justify-content:center;margin-top:16px"><button class="pb" id="kClose2"')
