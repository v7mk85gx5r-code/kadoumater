# 点光源の土台と、動く光（L01 + L06 + L05）
#   L01 点光源の拡張：NLIT 16→32。実際に使っている灯数 uNL でシェーダのループを早期に打ち切る（灯が少ない場面は今より軽い）。
#       uLD[NLIT]（向き xyz と円錐の cos。w<=-1 で全方向光）でスポット光を表現できるようにする。
#       画質段階ごとの上限（最高 32／高 24／中 16／低 10／最低 8）。反射パス（WET）の上下反転では向きの y も反転する。
#       対象シェーダ：LIT_PRE/LIT_MAIN（建物・車・人）、SMOKE_FRAG（煙）、ptsMaterial（粉塵の粒）の 3 箇所。
#   L06 車のヘッドライトが路面と壁を照らす：カメラに近い走行車 ≤10 台（140m 以内）を円錐光（前方 26m・半頂角 ≒37°・やや下向き）
#       として HOOKS.lights の候補に入れる。減速中はテールランプの赤い全方向光（半径 7m）も足す。候補は再利用配列で GC を避ける。
#   L05 航空障害灯の現実化：ビルごと（44m 格子のハッシュ）に位相をずらし、150m 超は白色キセノン閃光（1.3Hz）。
#       街の生成時に素材 19（高さ 50m 超）を集め、カメラに近い 6 灯を「屋上を赤く照らす点光源」として候補に入れる
#       （明滅は GLSL と同じ式を JS で計算するので、発光と照らしが一致する）。倒壊した建物の灯は除外。
TITLE='点光源 32 灯・早期打ち切り・スポット光（L01）＋ヘッドライトの路面照射（L06）＋航空障害灯の非同期化と屋上照明（L05）'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)

    # ══════════ L01: NLIT 32、uLD/uNL の uniform ══════════
    rep("const NLIT=16;", "const NLIT=32;")
    rep("  uLC:{value:Array.from({length:NLIT},()=>new THREE.Vector4(0,0,0,0))},",
        "  uLC:{value:Array.from({length:NLIT},()=>new THREE.Vector4(0,0,0,0))},\n"
        "  uLD:{value:Array.from({length:NLIT},()=>new THREE.Vector4(0,0,0,-2))},   // スポット光の向き xyz と円錐の cos（w<=-1 で全方向光）\n"
        "  uNL:{value:0},                                                             // 実際に使っている灯数（シェーダはここで打ち切る）")
    # LIT_PRE（建物・車・人の共有材質）
    rep("const LIT_PRE=`#define NLIT ${NLIT}\nuniform vec4 uLP[NLIT]; uniform vec4 uLC[NLIT];\n",
        "const LIT_PRE=`#define NLIT ${NLIT}\nuniform vec4 uLP[NLIT]; uniform vec4 uLC[NLIT]; uniform vec4 uLD[NLIT]; uniform float uNL;\n")
    rep("""    for(int i=0;i<NLIT;i++){
      vec3 dv=uLP[i].xyz-vWPos;
      float dd=length(dv);
      float at=clamp(1.0-dd/uLP[i].w,0.0,1.0);
      float nl=max(dot(ttN,dv/max(dd,0.001)),0.0)*0.8+0.2;
      ttL+=uLC[i].rgb*(uLC[i].a*at*at*nl);
    }""", """    for(int i=0;i<NLIT;i++){
      if(float(i)>=uNL) break;                                           // 使っている灯数で打ち切る
      vec3 dv=uLP[i].xyz-vWPos;
      float dd=length(dv);
      float at=clamp(1.0-dd/uLP[i].w,0.0,1.0);
      if(at<=0.0) continue;
      vec3 ld=dv/max(dd,0.001);
      float cone=uLD[i].w<=-1.0?1.0:smoothstep(uLD[i].w,uLD[i].w+0.12,dot(-ld,uLD[i].xyz));   // スポット光の円錐（縁は柔らかく）
      float nl=max(dot(ttN,ld),0.0)*0.8+0.2;
      ttL+=uLC[i].rgb*(uLC[i].a*at*at*nl*cone);
    }""")
    # 煙（SMOKE_FRAG）
    rep("const SMOKE_FRAG=`#define NLIT ${NLIT}\nuniform vec4 uLP[NLIT]; uniform vec4 uLC[NLIT];\n",
        "const SMOKE_FRAG=`#define NLIT ${NLIT}\nuniform vec4 uLP[NLIT]; uniform vec4 uLC[NLIT]; uniform vec4 uLD[NLIT]; uniform float uNL;\n")
    rep("  for(int i=0;i<NLIT;i++){ vec3 dv=uLP[i].xyz-vWp; float d=length(dv); float at=clamp(1.0-d/uLP[i].w,0.0,1.0); L+=uLC[i].rgb*(uLC[i].a*at*at*1.3); }",
        "  for(int i=0;i<NLIT;i++){ if(float(i)>=uNL) break; vec3 dv=uLP[i].xyz-vWp; float d=length(dv); float at=clamp(1.0-d/uLP[i].w,0.0,1.0); if(at<=0.0) continue;\n"
        "    float cone=uLD[i].w<=-1.0?1.0:smoothstep(uLD[i].w,uLD[i].w+0.12,dot(-dv/max(d,0.001),uLD[i].xyz)); L+=uLC[i].rgb*(uLC[i].a*at*at*1.3*cone); }")
    rep("    uniforms:{uTime:SKYU.uTime,uAmp:{value:0.34},uLP:LITU.uLP,uLC:LITU.uLC,uStreet:LITU.uStreet,",
        "    uniforms:{uTime:SKYU.uTime,uAmp:{value:0.34},uLP:LITU.uLP,uLC:LITU.uLC,uLD:LITU.uLD,uNL:LITU.uNL,uStreet:LITU.uStreet,")
    # 粉塵の粒（ptsMaterial の頂点シェーダ）
    rep("    uLP:LITU.uLP, uLC:LITU.uLC, uStreet:LITU.uStreet, uStreetFall:LITU.uStreetFall, uStreetCol:LITU.uStreetCol };",
        "    uLP:LITU.uLP, uLC:LITU.uLC, uLD:LITU.uLD, uNL:LITU.uNL, uStreet:LITU.uStreet, uStreetFall:LITU.uStreetFall, uStreetCol:LITU.uStreetCol };")
    rep("uniform vec4 uLP[NLIT]; uniform vec4 uLC[NLIT];\nvarying vec3 vC;\n",
        "uniform vec4 uLP[NLIT]; uniform vec4 uLC[NLIT]; uniform vec4 uLD[NLIT]; uniform float uNL;\nvarying vec3 vC;\n")
    rep("""    for(int i=0;i<NLIT;i++){
      vec3 dv=uLP[i].xyz-wp; float d=length(dv);
      float at=clamp(1.0-d/uLP[i].w,0.0,1.0);
      L+=uLC[i].rgb*(uLC[i].a*at*at*1.4);
    }""", """    for(int i=0;i<NLIT;i++){
      if(float(i)>=uNL) break;
      vec3 dv=uLP[i].xyz-wp; float d=length(dv);
      float at=clamp(1.0-d/uLP[i].w,0.0,1.0);
      if(at<=0.0) continue;
      float cone=uLD[i].w<=-1.0?1.0:smoothstep(uLD[i].w,uLD[i].w+0.12,dot(-dv/max(d,0.001),uLD[i].xyz));
      L+=uLC[i].rgb*(uLC[i].a*at*at*1.4*cone);
    }""")
    # addLight：省略可能な向きと円錐
    rep("function addLight(x,y,z,r,col,inten,tau){", "function addLight(x,y,z,r,col,inten,tau,dir,cone){")
    rep("  LITQ.push({x:x,y:y,z:z,r:r,c:col,i:inten,tau:tau,s:0});",
        "  LITQ.push({x:x,y:y,z:z,r:r,c:col,i:inten,tau:tau,s:0,d:dir||null,cone:cone===undefined?-2:cone});")
    # updLights の uniform 書き込み：画質段階の上限で切り、向きを書き、uNL を更新
    rep("""  const P=LITU.uLP.value, C=LITU.uLC.value;
  for(let i=0;i<NLIT;i++){
    const L=cand[i];
    if(L){ P[i].set(L.x,L.y,L.z,L.r); C[i].set(L.c[0],L.c[1],L.c[2],L.i); }
    else { P[i].set(0,-1e4,0,1); C[i].set(0,0,0,0); }
  }""", """  const P=LITU.uLP.value, C=LITU.uLC.value, D=LITU.uLD.value;
  const nMax=Math.min(NLIT, LIT_LV[Math.max(0,Math.min(LIT_LV.length-1,QUAL.level|0))]);   // 画質段階ごとの灯数の上限
  let nUsed=0;
  for(let i=0;i<NLIT;i++){
    const L=i<nMax?cand[i]:null;
    if(L&&L.i>0.0){ P[i].set(L.x,L.y,L.z,L.r); C[i].set(L.c[0],L.c[1],L.c[2],L.i);
      if(L.d) D[i].set(L.d[0],L.d[1],L.d[2],L.cone); else D[i].w=-2; nUsed=i+1; }
    else { P[i].set(0,-1e4,0,1); C[i].set(0,0,0,0); D[i].w=-2; }
  }
  LITU.uNL.value=nUsed;""")
    # 反射パス：向きの y も反転
    rep("    for(let i=0;i<NLIT;i++) P[i].y=-P[i].y;",
        "    for(let i=0;i<NLIT;i++){ P[i].y=-P[i].y; LITU.uLD.value[i].y=-LITU.uLD.value[i].y; }")

    # ══════════ L05: 航空障害灯のシェーダ（ビルごとの位相、150m 超は白色閃光） ══════════
    rep("      float fl=fract(uTime*0.75);                                // 航空障害灯：街じゅうで同期して点滅する\n"
        "      outgoingLight*=0.06+1.9*smoothstep(0.0,0.06,fl)*smoothstep(0.50,0.36,fl);",
        "      vec2 bq=floor(vWPos.xz/44.0); float ph=ttH2(bq);           // 航空障害灯：44m 格子≒ビル単位で位相をずらす\n"
        "      float fl=fract(uTime*0.75+ph);\n"
        "      if(abs(vWPos.y)>150.0){ float s=fract(uTime*1.3+ph);      // 150m 超は白色のキセノン閃光（約 1.3Hz の鋭いフラッシュ）\n"
        "        outgoingLight=vec3(1.0,0.97,0.9)*(0.08+5.5*smoothstep(0.0,0.015,s)*smoothstep(0.07,0.025,s))*uEmHi; }\n"
        "      else outgoingLight*=0.06+1.9*smoothstep(0.0,0.06,fl)*smoothstep(0.50,0.36,fl);")

    # ══════════ L06: updTraffic でカメラ近傍の走行車を集める ══════════
    rep("  // 描画\n  const MB=TRF.body.instanceMatrix.array, MC=TRF.cabin.instanceMatrix.array, ML=TRF.lamp.instanceMatrix.array;",
        "  // 描画\n  hlBegin();\n  const MB=TRF.body.instanceMatrix.array, MC=TRF.cabin.instanceMatrix.array, ML=TRF.lamp.instanceMatrix.array;")
    rep("    const brake=c.v<c.vmax*.6, prk=!!c.parked;",
        "    const brake=c.v<c.vmax*.6, prk=!!c.parked;\n    if(!prk) hlNote(c,x,z,cs,sn,brake);")

    # ══════════ 定義：灯数の上限、ヘッドライト、航空障害灯 ══════════
    rep("/*@DEFS*/", r"""/* ══════════ 点光源の土台（L01）・ヘッドライト（L06）・航空障害灯（L05）（work/pc/feat/22_lights_core.py） ══════════ */
const LIT_LV=[32,24,16,10,8];                     // 画質段階ごとの点光源の上限（最高／高／中／低／最低）
/* ── ヘッドライト：updTraffic の描画ループで、カメラから 140m 以内の走行車を集め、近い順 10 台を円錐光にする ── */
const HL={n:0, cx:0, cz:0, a:[], ls:[], MAX:10, RANGE:140};
function hlBegin(){ HL.n=0; HL.cx=camera.position.x; HL.cz=camera.position.z; }
function hlNote(c,x,z,cs,sn,brake){
  const dx=x-HL.cx, dz=z-HL.cz, d2=dx*dx+dz*dz; if(d2>HL.RANGE*HL.RANGE) return;
  const d=Math.sqrt(d2);
  // 近い順 MAX 件を保つ（挿入ソート。枠はオブジェクトを再利用）
  let k=HL.n; if(k>=HL.MAX){ if(d>=HL.a[HL.MAX-1].d) return; k=HL.MAX-1; } else { HL.n++; if(!HL.a[k]) HL.a[k]={x:0,z:0,cs:1,sn:0,brake:false,d:0}; }
  const tmp=HL.a[k];
  while(k>0&&HL.a[k-1].d>d){ HL.a[k]=HL.a[k-1]; k--; }
  HL.a[k]=tmp; tmp.x=x; tmp.z=z; tmp.cs=cs; tmp.sn=sn; tmp.brake=brake; tmp.d=d;
}
function hlLights(cand){
  if(!TRF.body) return;
  const cx=camera.position.x, cy=camera.position.y, cz=camera.position.z;
  for(let k=0;k<HL.n;k++){ const q=HL.a[k];
    const fade=Math.min(1,(HL.RANGE-q.d)/30);                           // 枠の縁は徐々に消す
    if(fade<=0) continue;
    const H=HL.ls[k*2]||(HL.ls[k*2]={c:[1,.95,.82],tau:1,s:0,d:[1,0,0],cone:0.80});
    H.x=q.x+q.cs*2.4; H.y=0.9; H.z=q.z-q.sn*2.4; H.r=26; H.i=0.95*fade;
    H.d[0]=q.cs*0.96; H.d[1]=-0.28; H.d[2]=-q.sn*0.96;                  // 進行方向（車体の +x）へ、やや下向き
    H.s=0.9*H.i*H.r/(Math.hypot(H.x-cx,H.y-cy,H.z-cz)+H.r*0.5+1);
    cand.push(H);
    if(q.brake){
      const B=HL.ls[k*2+1]||(HL.ls[k*2+1]={c:[1,.10,.05],tau:1,s:0,d:null,cone:-2});
      B.x=q.x-q.cs*2.3; B.y=0.7; B.z=q.z+q.sn*2.3; B.r=7; B.i=0.5*fade;
      B.s=0.9*B.i*B.r/(Math.hypot(B.x-cx,B.y-cy,B.z-cz)+B.r*0.5+1);
      cand.push(B);
    }
  }
}
HOOKS.lights.push(hlLights);
HOOKS.reset.push(function(){ HL.n=0; });

/* ── 航空障害灯：街の生成時に素材 19（高さ 50m 超）を集め、カメラに近い 6 灯を屋上を照らす点光源にする ── */
const AVL=[];                                      // {b,idx,x,y,z,ph,white}
const AVLL={t:0, n:0, pick:[], ls:[], MAX:6, RANGE:420};
function avlFract(v){ return v-Math.floor(v); }
function avlH2(px,py){                             // GLSL の ttH2 と同じ式（float32 を模して位相を一致させる）
  const F=Math.fround;
  px=F(avlFract(F(px*123.34))); py=F(avlFract(F(py*456.21)));
  const d=F(F(px*F(px+45.32))+F(py*F(py+45.32)));
  px=F(px+d); py=F(py+d);
  return avlFract(F(px*py));
}
function avlSmooth(a,b,x){ const t=Math.max(0,Math.min(1,(x-a)/(b-a))); return t*t*(3-2*t); }
function buildAvl(){
  AVL.length=0; AVLL.n=0; AVLL.t=0;
  const y0=Math.ceil(50/VOX-0.5);
  for(let n=0;n<blds.length&&AVL.length<400;n++){ const b=blds[n];
    if(b.H<=y0) continue;
    const W=b.W, WH=W*b.H, vox=b.vox;
    for(let z=0;z<b.D;z++) for(let y=y0;y<b.H;y++){ const row=W*y+WH*z;
      for(let x=0;x<W;x++){ if(vox[row+x]!==19) continue;
        const wx=b.ox+(x+0.5)*VOX, wy=(y+0.5)*VOX, wz=b.oz+(z+0.5)*VOX;
        AVL.push({b:b, idx:row+x, x:wx, y:wy, z:wz, ph:avlH2(Math.floor(wx/44),Math.floor(wz/44)), white:wy>150});
        if(AVL.length>=400) return; } }
  }
}
function avlPick(){
  const P=AVLL.pick; AVLL.n=0;
  const cx=camera.position.x, cy=camera.position.y, cz=camera.position.z;
  for(let n=0;n<AVL.length;n++){ const a=AVL[n];
    if(a.b.toppled||a.b.toppling||a.b.vox[a.idx]!==19) continue;        // 倒れた・壊れた灯
    const d=Math.hypot(a.x-cx,a.y-cy,a.z-cz); if(d>AVLL.RANGE) continue;
    let k=AVLL.n; if(k>=AVLL.MAX){ if(d>=P[AVLL.MAX-1].d) continue; k=AVLL.MAX-1; } else { AVLL.n++; if(!P[k]) P[k]={a:null,d:0}; }
    const tmp=P[k];
    while(k>0&&P[k-1].d>d){ P[k]=P[k-1]; k--; }
    P[k]=tmp; tmp.a=a; tmp.d=d;
  }
}
function avlLights(cand,dt){
  if(!AVL.length) return;
  AVLL.t-=dt; if(AVLL.t<=0){ AVLL.t=0.3; avlPick(); }
  const cx=camera.position.x, cy=camera.position.y, cz=camera.position.z, T=LITU.uTime.value;
  for(let k=0;k<AVLL.n;k++){ const a=AVLL.pick[k].a;
    const L=AVLL.ls[k]||(AVLL.ls[k]={c:[1,.12,.06],tau:1,s:0,d:null,cone:-2});
    let it;
    if(a.white){ const s=avlFract(T*1.3+a.ph); it=2.5*avlSmooth(0,0.015,s)*avlSmooth(0.07,0.025,s); L.c[0]=1; L.c[1]=.95; L.c[2]=.85; L.r=26; }
    else { const fl=avlFract(T*0.75+a.ph); it=0.9*(0.03+avlSmooth(0,0.06,fl)*avlSmooth(0.50,0.36,fl)); L.c[0]=1; L.c[1]=.12; L.c[2]=.06; L.r=16; }
    if(it<0.02) continue;
    L.x=a.x; L.y=a.y+1.0; L.z=a.z; L.i=it;
    L.s=L.i*L.r/(Math.hypot(L.x-cx,L.y-cy,L.z-cz)+L.r*0.5+1);
    cand.push(L);
  }
}
HOOKS.build.push(buildAvl);
HOOKS.reset.push(function(){ AVL.length=0; AVLL.n=0; });
HOOKS.lights.push(avlLights);
/*@DEFS*/""")

    # ══════════ 検証フック ══════════
    U("/*@PCDBG*/",
      "lights:()=>({nlit:NLIT, nl:LITU.uNL.value, max:LIT_LV[Math.max(0,Math.min(LIT_LV.length-1,QUAL.level|0))], cand:_litCand.length, cars:HL.n, avl:AVL.length, avlOn:AVLL.n,\n"
      "    spots:LITU.uLD.value.filter((d,i)=>i<LITU.uNL.value&&d.w>-1).length}), HL:()=>HL, AVL:()=>AVL, AVLL:()=>AVLL, /*@PCDBG*/")
