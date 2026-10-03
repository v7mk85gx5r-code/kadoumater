# TOKYO TEARDOWN PC 版ビルド：Enhanced 版（three.js 同梱）を元に、PC向けの UI/操作系・画質・上限値・新武器を差し込む
import re, sys, os, shutil
ROOT='/home/user/kadoumater'
SRC=ROOT+'/work/TOKYO_TEARDOWN_iPhone17_Enhanced.html'
OUT=ROOT+'/work/TOKYO_TEARDOWN_PC.html'
D=ROOT+'/work/pc/'
def rd(p): return open(p,encoding='utf-8').read()
t=rd(SRC); n=0
def rep(old,new,count=1):
    global t,n
    c=t.count(old)
    if c!=count: print('PATTERN COUNT MISMATCH (%d != %d):\n%s'%(c,count,old[:200])); sys.exit(1)
    t=t.replace(old,new); n+=1
def between(a,b,new):
    global t,n
    i=t.index(a); j=t.index(b,i)
    t=t[:i]+new+t[j:]; n+=1

# ── 文書の枠：タイトル・CSS・本文 ──
rep('<title>TOKYO TEARDOWN — 東京解体</title>','<title>TOKYO TEARDOWN PC — 東京解体</title>')
between('<style>\n','</style>','<style>\n'+rd(D+'style_pc.css'))
between('<body>\n','<script>\n/* three.js r128',rd(D+'body_pc.html'))
# ── UI ブロック（HUD・入力・メニュー）を PC 版に差し替え ──
between('/* ══════════ HUD ══════════ */','/* ══════════ 初期化 ══════════ */',rd(D+'ui_pc.js')+'\n')
# ── 版の説明 ──
rep("""   2026-10-02 iPhone 17 向け改修（Enhanced）：""","""   2026-10-03 PC 版（キーボードだけで完結・マウス／ゲームパッド任意）：
   ・操作：矢印キー視点／WASD 移動／Space 発射（長押しで連射・照射、カッターは押したまま矢印で線）／Z・C・数字・Tab 武器／
     X 起爆／V ズーム／T 俯瞰／Esc メニュー（矢印と Enter で操作）。マウスはポインタロック（クリックで取得）、Standard 配列のパッド
   ・画質：5段階プリセット＋解像度スケール、深度プリパスによる SSAO、異方性ストリーク、点光源16、ブルーム6段、遠景3600m
   ・規模：塊160・粒子3000・破片3000・煙260・車360・歩行者1600・メッシュ予算2倍以上
   ・兵装：機関砲（毎秒14発の固定刻み）・絨毯爆撃（9発が歩く）・焼夷弾（火の海）を追加して13種
   ──────────────────────────────────────────────────────────────
   2026-10-02 iPhone 17 向け改修（Enhanced）：""")

# ── 上限値 ──
rep('const MAXCHUNK=84;','const MAXCHUNK=160;')
rep('const FOG_NEAR=850, FOG_FAR=2950;','const FOG_NEAR=1100, FOG_FAR=3400;')
rep('const NLIT=10;','const NLIT=16;')
rep('  if(LITQ.length>=48){','  if(LITQ.length>=96){')
rep('const TRF_MAX=240;','const TRF_MAX=360;')
rep('const PED_MAX=900;','const PED_MAX=1600;')
rep("  LAN.mesh=new THREE.InstancedMesh(g,mat,220);\n  LAN.mesh.instanceColor=new THREE.InstancedBufferAttribute(new Float32Array(220*3),3);",
    "  LAN.mesh=new THREE.InstancedMesh(g,mat,400);\n  LAN.mesh.instanceColor=new THREE.InstancedBufferAttribute(new Float32Array(400*3),3);")
rep('if(LAN.list.length<218)','if(LAN.list.length<398)')
rep('const VFX_FMAX=72, VFX_PMAX=1400;','const VFX_FMAX=120, VFX_PMAX=3000;')
rep('let VFX_SMAX=120;','let VFX_SMAX=260;')
rep('VFX.smoke=new THREE.InstancedMesh(mkS(120),mS,120);','VFX.smoke=new THREE.InstancedMesh(mkS(260),mS,260);')
rep('const RUB_MAX_MESH=16, RUB_MAX_TRI=150000, RUB_FLUSH_TRI=14000,','const RUB_MAX_MESH=32, RUB_MAX_TRI=400000, RUB_FLUSH_TRI=14000,')
rep('const FXCAP=1500;','const FXCAP=3000, GXCAP=1400;')
rep('const DEB_MAX=1400;','const DEB_MAX=3000;')
rep('gxPos=new Float32Array(700*3); gxCol=new Float32Array(700*3); gxSize=new Float32Array(700);','gxPos=new Float32Array(GXCAP*3); gxCol=new Float32Array(GXCAP*3); gxSize=new Float32Array(GXCAP);')
rep('let m=Math.min(gxA.length,700);','let m=Math.min(gxA.length,GXCAP);')
rep('gxA.length<700','gxA.length<GXCAP',5)
rep('gxA.length<660','gxA.length<GXCAP-40',3)
rep('gxA.length<650','gxA.length<GXCAP-50',1)
rep('gxA.length<680','gxA.length<GXCAP-20',2)
rep('gxA.length<640','gxA.length<GXCAP-60',1)
rep('  meshBudget = chunks.length>24 ? 1 : 2;','  meshBudget = chunks.length>48 ? 2 : 4;')
rep('  spawnBudget = 3;','  spawnBudget = 6;')
rep('  geoBudget = 50000;','  geoBudget = 110000;')
rep('  scanBudget = 140000;','  scanBudget = 320000;')
rep('const _t0=_now(), TB=QUAL.level>=2?5:7;','const _t0=_now(), TB=QUAL.level>=3?6:12;')
rep('  const bfsLim = chunks.length>40 ? 1 : 2;','  const bfsLim = chunks.length>80 ? 2 : 4;')
rep('  for(let i=0;i<8;i++){\n    // 弾体：光らない金属の筒','  for(let i=0;i<24;i++){\n    // 弾体：光らない金属の筒')
rep('  for(let i=0;i<10;i++){                                 // 設置した装薬','  for(let i=0;i<16;i++){                                 // 設置した装薬')
rep('const CHG_MAX=10;','const CHG_MAX=16;')
rep("mkEfxPool('ball',20,","mkEfxPool('ball',32,")
rep("mkEfxPool('smoke',14,","mkEfxPool('smoke',24,")
rep("mkEfxPool('ring',12,","mkEfxPool('ring',20,")
rep("mkEfxPool('disc',10,","mkEfxPool('disc',16,")
rep("  for(let i=0;i<14;i++){\n    const m=new THREE.MeshBasicMaterial({color:0xffa040,","  for(let i=0;i<24;i++){\n    const m=new THREE.MeshBasicMaterial({color:0xffa040,")
rep("  for(let i=0;i<14;i++){\n    // ビーム：","  for(let i=0;i<24;i++){\n    // ビーム：")
rep('const BLAST_CAP=26;','const BLAST_CAP=40;')
rep('camera=new THREE.PerspectiveCamera(72,window.innerWidth/window.innerHeight,.6,3000);','camera=new THREE.PerspectiveCamera(72,window.innerWidth/window.innerHeight,.6,3600);')
rep('  const S=1400;\n  const spanX=CITY.x1-CITY.x0','  const S=2800;\n  const spanX=CITY.x1-CITY.x0')
rep('  const MAXV=30;','  const MAXV=40;')
# 曳光弾のプール（initPools の末尾）
rep("    beamPool.push({o:o,mat:m});\n  }\n}","""    beamPool.push({o:o,mat:m});
  }
  for(let i=0;i<24;i++){                                 // 機関砲の曳光弾
    const m=new THREE.MeshBasicMaterial({color:0xffc070,transparent:true,opacity:0,blending:THREE.AdditiveBlending,depthWrite:false,fog:false});
    const o=new THREE.Mesh(UNIT_CYL,m); o.visible=false; o.frustumCulled=false; scene.add(o);
    trcPool.push({o:o,mat:m,busy:false});
  }
}""")

# ── 画質プリセット（5段階＋解像度スケール＋SSAO/ストリーク） ──
between('const QLV=[','function updPerf(rawDt){',"""const QLV=[
  {mp:99,   refl:1, smoke:260, ped:1.0,  mips:6, msaa:true,  ao:1, streak:1},   // 最高：ネイティブ解像度・SSAO・反射を毎フレーム
  {mp:3.2,  refl:1, smoke:200, ped:1.0,  mips:5, msaa:true,  ao:1, streak:1},   // 高
  {mp:2.1,  refl:2, smoke:140, ped:0.7,  mips:5, msaa:true,  ao:0, streak:1},   // 中
  {mp:1.2,  refl:0, smoke:90,  ped:0.4,  mips:4, msaa:false, ao:0, streak:0},   // 低
  {mp:0.7,  refl:0, smoke:60,  ped:0.2,  mips:3, msaa:false, ao:0, streak:0},   // 最低（自動のみ）
];
const QNAME=['最高','高','中','低','最低'];
let resScale=1;                        // 解像度スケール（設定）。描画画素数に掛ける（1.5 以上は超解像）
let aoUser=true;                       // SSAO（設定）
function prForLevel(L){
  const w=Math.max(1,window.innerWidth), h=Math.max(1,window.innerHeight);
  const dpr=Math.min(3,(window.devicePixelRatio||1)*resScale);
  return Math.max(0.5, Math.min(dpr, Math.sqrt(QLV[L].mp*1e6/(w*h))));
}
function applyLevel(L,force){
  L=Math.max(0,Math.min(QLV.length-1,L|0));
  if(!force && QUAL.applied && QUAL.level===L) return;
  QUAL.level=L; QUAL.applied=true;
  const Q=QLV[L];
  QUAL.smokeMax=Q.smoke; VFX_SMAX=Q.smoke;
  if(VFX.sa.length>VFX_SMAX) VFX.sa.splice(0,VFX.sa.length-VFX_SMAX);
  const pedUp=Q.ped>QUAL.pedK; QUAL.pedK=Q.ped;
  QUAL.pr=prForLevel(L);
  if(renderer) renderer.setPixelRatio(QUAL.pr);
  POST.level=L; POST.mipsN=Q.mips; POST.wantMsaa=Q.msaa;
  POST.aoOn=!!Q.ao && aoUser; POST.streakOn=!!Q.streak;
  WET.every=Q.refl;
  if(typeof resize==='function' && renderer) resize();      // RT も作り直す
  WET.on=POST.on&&Q.refl>0;
  if(PED.list.length>PED_MAX*QUAL.pedK) PED.list.length=Math.floor(PED_MAX*QUAL.pedK);
  else if(pedUp && blds.length && typeof buildPeds==='function') buildPeds();
  QUAL.settleUntil=performance.now()+3000; QUAL.hist.length=0;
  updQualLabel();
}
function updQualLabel(){ if(typeof renderQualUI==='function') renderQualUI(); }
function setQuality(mode){
  QUAL.mode=mode;
  if(mode==='auto') applyLevel(QUAL.level,true);
  else { const L={ultra:0,high:1,mid:2,low:3}[mode]; applyLevel(L===undefined?0:L,true); }
}
/* 性能計測：実フレーム間隔を蓄積し、1秒ごとに集計。自動画質は3秒の傾向で下げ、12秒以上余裕が続いたら1段戻す */
""")

# ── ポストプロセス：SSAO とストリーク ──
rep("const POST={on:false,hdr:false,gl2:false,msaa:false,type:0,w:1,h:1,rt:null,mips:[],ups:[],\n  q:null,sc:null,cam:null,mats:{},level:0,lastT:0,acc:0,frames:0,warm:0};",
    "const POST={on:false,hdr:false,gl2:false,msaa:false,type:0,w:1,h:1,rt:null,mips:[],ups:[],\n  q:null,sc:null,cam:null,mats:{},level:0,lastT:0,acc:0,frames:0,warm:0,\n  aoOn:false,streakOn:false,ao:{depth:null,rt:null,blur:null,w:1,h:1},streak:{a:null,b:null},depthMat:null};")
rep('uniform vec2 uRes; uniform vec4 uShock; uniform vec4 uShk[4]; uniform vec4 uLens;',
    'uniform vec2 uRes; uniform vec4 uShock; uniform vec4 uShk[4]; uniform vec4 uLens;\nuniform sampler2D tAO, tStreak; uniform float uAOk, uStreak;')
rep('  col=lin(col)*uExposure+texture2D(tBloom,uv).rgb*uBloom;',
"""  col=lin(col)*uExposure;
  if(uAOk>0.001){                             // 環境光遮蔽：暗い面だけに効かせ、発光する窓や看板は守る
    float ao=texture2D(tAO,uv).r;
    float br=max(col.r,max(col.g,col.b));
    col*=mix(1.0,ao,uAOk*(1.0-smoothstep(0.9,2.2,br)));
  }
  col+=texture2D(tBloom,uv).rgb*uBloom;
  if(uStreak>0.001) col+=texture2D(tStreak,uv).rgb*uStreak;   // 強い光から横に伸びる筋（アナモルフィック）""")
rep('function fsMat(frag,uni){', rd(D+'post_pc.js')+'\nfunction fsMat(frag,uni){')
rep("      uShk:{value:[0,1,2,3].map(()=>new THREE.Vector4())},uLens:{value:new THREE.Vector4()}});\n    LITU.uEmLo.value=hdr?1.05:1.0;",
"""      uShk:{value:[0,1,2,3].map(()=>new THREE.Vector4())},uLens:{value:new THREE.Vector4()},
      tAO:{value:null},uAOk:{value:0},tStreak:{value:null},uStreak:{value:0}});
    POST.mats.ao=fsMat(AO_FRAG,{tDepth:{value:null},uTexel:{value:new THREE.Vector2()},uNear:{value:.6},uFar:{value:3600},
      uRadius:{value:7.0},uBias:{value:0.35},uTime:{value:0},uProj:{value:new THREE.Matrix4()},uInvProj:{value:new THREE.Matrix4()}});
    POST.mats.aoBlur=fsMat(AOBLUR_FRAG,{tSrc:{value:null},uDir:{value:new THREE.Vector2()}});
    POST.mats.streak=fsMat(STREAK_FRAG,{tSrc:{value:null},uTexel:{value:new THREE.Vector2()},uStride:{value:1},uTint:{value:new THREE.Vector3(0.74,0.86,1.0)}});
    POST.depthMat=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking,side:THREE.DoubleSide});   // 空のドーム（内側から見る）も描くため両面
    LITU.uEmLo.value=hdr?1.05:1.0;""")
rep("  for(const t of POST.ups) t.dispose();",
"""  for(const t of POST.ups) t.dispose();
  for(const k of ['depth','rt','blur']){ if(POST.ao[k]){ POST.ao[k].dispose(); POST.ao[k]=null; } }
  for(const k of ['a','b']){ if(POST.streak[k]){ POST.streak[k].dispose(); POST.streak[k]=null; } }""")
rep("  for(let i=0;i<nm-1;i++) POST.ups.push(mkRT(POST.mips[i].width,POST.mips[i].height,false));",
"""  for(let i=0;i<nm-1;i++) POST.ups.push(mkRT(POST.mips[i].width,POST.mips[i].height,false));
  if(POST.aoOn){                               // SSAO は半分の解像度で計算する
    const aw=Math.max(1,w>>1), ah=Math.max(1,h>>1);
    POST.ao.w=aw; POST.ao.h=ah;
    POST.ao.depth=mkRT8(aw,ah,true); POST.ao.rt=mkRT8(aw,ah,false); POST.ao.blur=mkRT8(aw,ah,false);
  }
  if(POST.streakOn && POST.mips.length>1){
    POST.streak.a=mkRT(POST.mips[1].width,POST.mips[1].height,false);
    POST.streak.b=mkRT(POST.mips[1].width,POST.mips[1].height,false);
  }""")
rep("  renderer.setRenderTarget(POST.rt);\n  renderer.render(scene,camera);\n  const M=POST.mats;",
    "  renderer.setRenderTarget(POST.rt);\n  renderer.render(scene,camera);\n  const M=POST.mats;\n  renderAO();")
rep("  const C=M.comp.uniforms;\n  C.tScene.value=POST.rt.texture; C.tBloom.value=lo.texture;",
    "  renderStreak();\n  const C=M.comp.uniforms;\n  C.tScene.value=POST.rt.texture; C.tBloom.value=lo.texture;")

# ── カメラ：視野角とズーム、移動速度 ──
rep('const FOV0=72;','const FOV0=72;\nlet fovUser=75, zoomK=0;                   // 設定の視野角と、ズーム（0..1）\nfunction fovBase(){ return fovUser*(1-0.56*zoomK); }')
rep('  const nf=FOV0+fovOff;','  const nf=fovBase()+fovOff;')
rep('  const sp=(inp.boost?260:110);','  const sp=(inp.boost?300:125);')
rep("function finishBoot(){\n  booting=false;\n  const b=document.getElementById('boot'); if(b) b.style.display='none';\n  needFrame=true;\n}",
    "function finishBoot(){\n  booting=false;\n  const b=document.getElementById('boot'); if(b) b.style.display='none';\n  needFrame=true;\n  if(typeof onBootDone==='function') onBootDone();\n}")
rep("function initHaptics(){ try{ hapticOn = localStorage.getItem('tt2_hap')!=='0'; }catch(e){} }","function initHaptics(){ hapticOn=false; }   // PC 版：振動なし")

# ── 兵装表と発射 ──
between('const WPN=[',"let wpn='missile', cd=0, cdMax=1;","""const WPN=[
  {id:'missile',g:'🚀',n:'誘導弾',   cd:.28, d:'照準の先へ飛び、数ボクセル食い込んでから内部で起爆する。連打できる基本兵装。'},
  {id:'gun',    g:'🔫',n:'機関砲',   cd:0, cont:2, d:'押している間、毎秒14発の連射。壁を削り、窓を割り、撃ち続けると散る。連射開始1回＝1発。'},
  {id:'rail',   g:'⚡',n:'レールガン',cd:0, cont:1, d:'押している間ずっと照射し、穴を掘り進める。照射開始1回＝1発。'},
  {id:'cutter', g:'✂️',n:'解体カッター',cd:.70,swipe:1,d:'発射キーを押したまま視点を動かして線を引き、離すと断ち切る。押すだけなら水平に切る。'},
  {id:'carpet', g:'✈️',n:'絨毯爆撃', cd:7.0, d:'照準の向きに沿って9発の爆弾が歩くように落ちる。通りごと叩く。'},
  {id:'incend', g:'🔥',n:'焼夷弾',   cd:2.4, d:'放物線で投げ込み、着弾点に火の海を作る。木造や可燃物に延焼して燃え落とす。'},
  {id:'grav',   g:'🕳️',n:'特異点',   cd:5.5, d:'周囲のビルを順に地面から引き剥がし、渦を巻いて吸い込む。限界で崩壊。'},
  {id:'orbit',  g:'🔆',n:'軌道砲',   cd:4.0, d:'成層圏から照射。柱状に消し飛ばす。'},
  {id:'demo',   g:'📿',n:'制御発破', cd:.16, place:1, d:'発射で装薬を置き（最大16）、起爆キーで順に爆破。片側に寄せれば折れる向きが決まる。起爆1回＝1発。'},
  {id:'meteor', g:'☄️',n:'隕石',     cd:6,   d:'爆発しない。質量で床を1枚ずつ突き抜けて落ちる。'},
  {id:'ball',   g:'🔗',n:'鉄球',     cd:1.0, d:'照準の先へ鉄球を撃ち込む。当たった方向へ建物が倒れる。'},
  {id:'orb',    g:'🔴',n:'破壊球',   cd:45, d:'成層圏から質量塊を落とす。着弾点から衝撃波の壁が街を舐め尽くす。スコア加算なし。'},
  {id:'nuke',   g:'☢️',n:'戦術核',   cd:15,  d:'半径190mを消し飛ばす。再使用まで15秒。スコア加算なし＝最後の掃除用。'},
];
""")
rep("  if(W.id!=='demo'){ S.shots++; noteShot(); }   // 装薬は「置く」では数えない。起爆1回＝1発",
    "  if(W.id!=='demo' && !W.cont){ S.shots++; noteShot(); }   // 装薬は「置く」では数えない。起爆1回＝1発。連射・照射は開始時に数える")
rep("    case 'nuke':\n","    case 'gun': cd=0; break;                       // 押している間の連射（gunTick）で処理する\n    case 'carpet': fireCarpet(o,dir,hit); break;\n    case 'incend': fireIncend(o,dir,hit); break;\n    case 'nuke':\n")
rep("function aimRay(maxD){\n  const o=camera.position, dir=new THREE.Vector3();\n  camera.getWorldDirection(dir);\n  maxD = maxD || 9000;",
    "function aimRay(maxD){\n  const o=camera.position, dir=new THREE.Vector3();\n  camera.getWorldDirection(dir);\n  return rayCast(o,dir,maxD);\n}\n/* 任意の原点・向きからの照準線（機関砲の散りなど） */\nfunction rayCast(o,dir,maxD){\n  maxD = maxD || 9000;")
rep("/* いびつな岩塊。", rd(D+'weapons_pc.js')+"\n/* いびつな岩塊。")
# 弾体の処理：爆弾（重い重力・噴射炎なし）と焼夷弾
rep("        m.v[1]-=10*dt/steps;","        m.v[1]-=(m.bomb?m.bomb:10)*dt/steps;")
rep("      E.flame.visible=true;","      E.flame.visible=!m.bomb;")
rep("    // 光るのは噴射炎の位置だけ\n    { const sp2=","    // 光るのは噴射炎の位置だけ\n    if(!m.bomb){ const sp2=")
rep("""      if(hit){
        // 遅延信管：進行方向へ数ボクセル食い込んでから内部で起爆
        const sp=Math.hypot(m.v[0],m.v[1],m.v[2])||1;
        const pen=m.gd?VOX*3.4:0;
        detonate(m.p[0]+m.v[0]/sp*pen, Math.max(1,m.p[1]+m.v[1]/sp*pen), m.p[2]+m.v[2]/sp*pen,
                 m.gd?30:34, m.gd?300:360);
      }""","""      if(hit){
        if(m.inc) incendHit(m.p[0],Math.max(1,m.p[1]),m.p[2]);
        else if(m.bomb) bombHit(m);
        else {
          // 遅延信管：進行方向へ数ボクセル食い込んでから内部で起爆
          const sp=Math.hypot(m.v[0],m.v[1],m.v[2])||1;
          const pen=m.gd?VOX*3.4:0;
          detonate(m.p[0]+m.v[0]/sp*pen, Math.max(1,m.p[1]+m.v[1]/sp*pen), m.p[2]+m.v[2]/sp*pen,
                   m.gd?30:34, m.gd?300:360);
        }
      }""")
# ── 連射のディスパッチ（ループ）と終了判定 ──
rep("""  const CW=WPN.find(w=>w.id===wpn);
  // レールガンは照射の開始で1発。撃ち切った後は新たに照射できない（照射中のものは続く）
  const wantRail=fireHeld && !!CW.cont && (railOn || canShoot());
  if(wantRail!==railOn){ railOn=wantRail; railOn?Snd.humOn():Snd.humOff();
    if(railOn){ S.shots++; noteShot(); railAcc=RAIL_DT; } }
  if(fireHeld && !CW.cont && cd<=0 && CW.id!=='demo') fireWeapon();
  updCam(realDt);
  if(railOn) railTick(dt);""","""  const CW=WPN.find(w=>w.id===wpn);
  // レールガン・機関砲は照射（連射）の開始で1発。撃ち切った後は新たに始められない（進行中のものは続く）
  const wantRail=fireHeld && CW.cont===1 && (railOn || canShoot());
  if(wantRail!==railOn){ railOn=wantRail; railOn?Snd.humOn():Snd.humOff();
    if(railOn){ S.shots++; noteShot(); railAcc=RAIL_DT; } }
  const wantGun=fireHeld && CW.cont===2 && (gunOn || canShoot());
  if(wantGun!==gunOn){ gunOn=wantGun; if(gunOn){ S.shots++; noteShot(); gunAcc=GUN_DT; } }
  if(fireHeld && !CW.cont && !CW.swipe && cd<=0 && CW.id!=='demo') fireWeapon();
  updCam(realDt);
  if(railOn) railTick(dt);
  if(gunOn) gunTick(dt);""")
rep("||orbitFx||railOn) return false;","||orbitFx||railOn||gunOn) return false;")
rep("if(S.shots>=M.shots && !railOn && !charges.length)","if(S.shots>=M.shots && !railOn && !gunOn && !charges.length)")
rep("  nukePend=null; orbitFx=null; railOn=false; railBeam=null; beamFx=[];",
    "  nukePend=null; orbitFx=null; railOn=false; railBeam=null; beamFx=[];\n  gunOn=false; gunAcc=0; for(const tr of tracers){ tr.e.busy=false; tr.e.o.visible=false; tr.e.mat.opacity=0; } tracers=[];")
rep("  updFX(dt); updShells(dt); updEfx(dt);","  updFX(dt); updShells(dt); updTracers(dt); updEfx(dt);")
# ── 音 ──
rep("    rail(){ T(160,3000,.14,.24,'square'); N(.34,.2,'bandpass',900,3200,2.4); },",
"""    rail(){ T(160,3000,.14,.24,'square'); N(.34,.2,'bandpass',900,3200,2.4); },
    gun(){ if(!gate('gun',40)) return; N(.06,.24,'bandpass',1500,380,1.1); T(170,55,.07,.18,'square'); },
    whistle(){ if(!gate('whistle',400)) return; T(2200,500,1.4,.07,'sine'); },
    incend(x,y,z){ const pos=P(x,y,z); N(.7,.32,'lowpass',1200,110,1,pos); T(120,40,.5,.3,'sine',pos);
      for(let i=0;i<4;i++) setTimeout(()=>N(.08,.08,'bandpass',2600+Math.random()*2000,900,3,pos),200+i*140+Math.random()*120); },""")
# ── 起動列・可視性・検証フック ──
rep("selW('missile');\nsetMode('free');\nshowHint();","selW('missile');\nsetMode('free');\napplyPCS();")
rep("  else { last=performance.now(); if(booting||resultOn) setPaused(false); }",
    "  else { last=performance.now(); if(booting||resultOn||titleOn) setPaused(false); }")
rep("  if(paused){\n    if(booting){ try{ buildQueued(); }catch(e){} }","  if(paused){\n    try{ pollPad(raw); }catch(e){}                           // ポーズ中もパッドでメニューを操作できる\n    if(booting){ try{ buildQueued(); }catch(e){} }")
rep("  if(m>25 && QUAL.level<QLV.length-1){ QUAL.downT=now; applyLevel(QUAL.level+1); }",
    "  if(m>25 && QUAL.level<QLV.length-1){ QUAL.downT=now; applyLevel(QUAL.level+(m>60?2:1)); }   // 極端に重ければ2段落とす")
# 色収差は高解像度では目立ちすぎる（1080p で端が 6px ずれる）ので弱める
rep("uVig:{value:0.38},uGrain:{value:0.028},uCA:{value:0.0035},","uVig:{value:0.36},uGrain:{value:0.022},uCA:{value:0.0012},")
rep("  C.uCA.value=0.0035+caPulse*0.022;","  C.uCA.value=0.0012+caPulse*0.006;")
rep("  TRFcars:()=>TRF.cars, PARKED:()=>PARKED, causeToast:causeToast, chipTest:()=>MATS,",
    "  TRFcars:()=>TRF.cars, PARKED:()=>PARKED, causeToast:causeToast, chipTest:()=>MATS,\n  pc:PCDBG, gunOn:()=>gunOn, gunTick:gunTick, tracers:()=>tracers, fovBase:fovBase, zoomK:()=>zoomK, rayCast:rayCast, renderAO:renderAO,")

open(OUT,'w',encoding='utf-8').write(t)
shutil.copyfile(OUT, ROOT+'/TOKYO_TEARDOWN_PC.html')
print('applied',n,'patches; size',len(t))
