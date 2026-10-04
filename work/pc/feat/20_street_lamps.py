# 幹線道路の街灯（ENV-02 + L02）
#   ・幅 20m 以上の通りの両側に、実物どおりのアーム式街灯（柱 10m・片持ちアーム・灯具）を InstancedMesh で 30m ピッチ（千鳥）に立てる。
#     渋谷・西新宿には街灯が 1 本も無かった（電柱が歌舞伎町と西新宿の細い通りにしか無い）ので、全マップの幹線が「光の列」になる。
#   ・灯具の位置を lampPos に登録するので、既存の 4 つの仕組み（光点 buildLamps・路面の光溜まり buildGlowFloor・光の地図 buildLightMap・
#     EMP／変圧器／警報での消灯 killLampsNear/empBlackout）がそのまま効く。電線 buildWires は電柱（y=26）だけに張る。
#   ・カメラ近傍の街灯 ≤8 灯を本物の点光源として updLights の候補に入れる（0.25 秒ごとに選び直し、出入りはフェード）。
#     壁・車・歩行者が「その街灯に」照らされる。爆発・火災より優先度を下げる（スコア 0.6 倍）。
#   ・色：歌舞伎町／渋谷＝電球色、西新宿＝昼白色（LED）。
#   ・爆風で柱が倒れる（根元で 80° 回転）。倒れた灯は消え、鉄骨の破片が飛ぶ。
TITLE='幹線道路のアーム式街灯（全マップ）＋近傍 8 灯の点光源化'
def apply(rep, between, src):
    # ── 1. 定義：プール・生成・消灯の同期・爆風 ──
    rep("const SIG={list:[], t:0, pole:null, head:null, lamp:null};", r"""/* ══════════ 幹線道路の街灯 ══════════
   幅 20m 以上の通りの両側に、アーム式街灯（柱 10m・片持ちアーム 2.3m・灯具）を 30m ピッチの千鳥で立てる。
   灯具の位置を lampPos に登録するので、光点・路面の光溜まり・光の地図・消灯の仕組みはそのまま効く。
   歌舞伎町／渋谷は電球色、西新宿は昼白色（LED）。爆風で柱が倒れる */
const SLP={pole:null, arm:null, head:null, list:[], t:0, MAX:720};
const SLP_PITCH=30, SLP_H=10, SLP_ARM=2.3;
function slpWhite(){ return MAPID===2; }                                  // 西新宿は昼白色
function slpLampCol(){ return slpWhite()?[.80,.88,1.0]:[1.0,.86,.62]; }   // 光点・光の地図の色
function slpLightCol(){ return slpWhite()?[.85,.90,1.0]:[1.0,.78,.50]; }  // 点光源の色
function initStreetLamps(){
  const box=(w,h,d,x,y)=>{ const g=new THREE.BoxGeometry(w,h,d).toNonIndexed(); g.translate(x,y,0);
    g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(g.attributes.position.count*3).fill(1),3)); return g; };
  const mat=new THREE.MeshBasicMaterial({vertexColors:true,fog:true}); setupLitMaterial(mat);
  const mk=(geo)=>{ const m=new THREE.InstancedMesh(geo,mat,SLP.MAX); m.instanceColor=new THREE.InstancedBufferAttribute(new Float32Array(SLP.MAX*3),3);
    m.instanceMatrix.setUsage(THREE.DynamicDrawUsage); m.count=0; m.frustumCulled=false; scene.add(m); return m; };
  SLP.pole=mk(box(.28,SLP_H,.28,0,SLP_H/2));                           // 柱（根元が原点）
  SLP.arm=mk(box(SLP_ARM+.3,.16,.16,(SLP_ARM+.3)/2-.15,SLP_H-.1));      // アーム：柱から +x へ
  SLP.head=mk(box(.95,.22,.38,SLP_ARM,SLP_H-.05));                      // 灯具：アームの先
}
const _slpM=new THREE.Matrix4(), _slpR=new THREE.Matrix4(), _slpAx=new THREE.Vector3();
function slpPose(k,q,fallX,fallZ){                                        // k 番目の行列を書く。fall があれば根元で倒す
  _slpM.makeRotationY(Math.atan2(-q.dz,q.dx));
  if(fallX!==undefined){ _slpAx.set(fallZ,0,-fallX).normalize(); _slpR.makeRotationAxis(_slpAx,1.40); _slpR.multiply(_slpM); _slpM.copy(_slpR); }
  _slpM.setPosition(q.x,0,q.z);
  SLP.pole.setMatrixAt(k,_slpM); SLP.arm.setMatrixAt(k,_slpM); SLP.head.setMatrixAt(k,_slpM);
}
function slpHeadCol(k,on){
  const C=SLP.head.instanceColor.array;
  if(!on){ C[k*3]=.12; C[k*3+1]=.12; C[k*3+2]=.13; return; }
  // 街灯の発光は「控えめな発光」の区分（最小成分 2〜4）。区分 2（ネオン）は壁面の看板として描かれるので使わない
  if(slpWhite()){ C[k*3]=3.60; C[k*3+1]=3.80; C[k*3+2]=3.95; } else { C[k*3]=3.90; C[k*3+1]=3.68; C[k*3+2]=3.30; }
}
function buildStreetLamps(){
  SLP.list.length=0; SLP.t=0;
  if(!SLP.pole) return;
  const nPole=lampPos.length/3;                                           // ここまでの lampPos は電柱の街灯（y=26）
  const nearPole=(x,z)=>{ for(let i=0;i<nPole*3;i+=3){ if(Math.abs(lampPos[i]-x)<10&&Math.abs(lampPos[i+2]-z)<10) return true; } return false; };
  const free=(x,z)=>!bldAt(x,1,z)&&!bldAt(x,5,z)&&!bldAt(x,9.4,z);
  const put=(x,z,dx,dz)=>{
    if(SLP.list.length>=SLP.MAX) return;
    const hx=x+dx*SLP_ARM, hz=z+dz*SLP_ARM;
    if(!free(x,z)||!free(hx,hz)||nearPole(x,z)) return;
    SLP.list.push({x:x,z:z,dx:dx,dz:dz,li:lampPos.length/3,dead:false,off:false});
    lampPos.push(hx,SLP_H+.2,hz);
  };
  // 南北の幹線：両側。片側を半ピッチずらして千鳥に。交差点（相手の通りの幅＋5m）は空ける
  for(let i=0;i<XL.length;i++){ if(XW[i]<20) continue;
    for(const sd of [-1,1]){ const x=XL[i]+sd*(XW[i]/2+1.3);
      for(let z=CITY.z0+12+(sd>0?SLP_PITCH/2:0); z<CITY.z1-12; z+=SLP_PITCH){
        let ok=true; for(let j=0;j<ZL.length;j++) if(Math.abs(z-ZL[j])<ZW[j]/2+5){ ok=false; break; }
        if(ok) put(x,z,-sd,0); } } }
  // 東西の幹線
  for(let j=0;j<ZL.length;j++){ if(ZW[j]<20) continue;
    for(const sd of [-1,1]){ const z=ZL[j]+sd*(ZW[j]/2+1.3);
      for(let x=CITY.x0+12+(sd>0?SLP_PITCH/2:0); x<CITY.x1-12; x+=SLP_PITCH){
        let ok=true; for(let i=0;i<XL.length;i++) if(Math.abs(x-XL[i])<XW[i]/2+5){ ok=false; break; }
        if(ok) put(x,z,0,-sd); } } }
  const CP=SLP.pole.instanceColor.array, CA=SLP.arm.instanceColor.array;
  for(let k=0;k<SLP.list.length;k++){
    slpPose(k,SLP.list[k]);
    CP[k*3]=.20; CP[k*3+1]=.21; CP[k*3+2]=.22; CA[k*3]=.20; CA[k*3+1]=.21; CA[k*3+2]=.22;
    slpHeadCol(k,true);
  }
  for(const m of [SLP.pole,SLP.arm,SLP.head]){ m.count=SLP.list.length; m.instanceMatrix.needsUpdate=true; m.instanceColor.needsUpdate=true; }
}
/* 消灯との同期：killLampsNear / empBlackout / 警報は光点（lampObj）の色を 0 にするだけなので、0.25 秒おきに灯具の発光を落とす */
function updStreetLamps(dt){
  if(!SLP.head||!SLP.list.length) return;
  SLP.t+=dt; if(SLP.t<.25) return; SLP.t=0;
  if(!lampObj) return;
  const col=lampObj.geometry.attributes.color||lampObj.geometry.attributes.acolor; if(!col) return;
  const A=col.array; let ch=false;
  for(let k=0;k<SLP.list.length;k++){ const q=SLP.list[k]; if(q.off) continue; const i=q.li*3;
    if(i+2<A.length && A[i]===0&&A[i+1]===0&&A[i+2]===0){ q.off=true; slpHeadCol(k,false); ch=true; } }
  if(ch) SLP.head.instanceColor.needsUpdate=true;
}
/* 爆風：半径内の柱を根元から倒す。灯は消え、鉄骨の破片と火花が飛ぶ */
function streetLampsBlast(x,z,r){
  if(!SLP.head||!SLP.list.length) return;
  const col=lampObj&&(lampObj.geometry.attributes.color||lampObj.geometry.attributes.acolor);
  let n=0, hit=false;
  for(let k=0;k<SLP.list.length;k++){ const q=SLP.list[k]; if(q.dead) continue;
    const dx=q.x-x, dz=q.z-z, d=Math.hypot(dx,dz); if(d>r*.95) continue;
    q.dead=true; q.off=true;
    const fx=d>1?dx/d:q.dx, fz=d>1?dz/d:q.dz;
    slpPose(k,q,fx,fz); slpHeadCol(k,false); hit=true;
    if(col){ const i=q.li*3; col.array[i]=col.array[i+1]=col.array[i+2]=0; }
    if(n<14){ n++;                                                      // 破片は近い柱だけ（1 回の爆発で最大 14 本分）
      const hx=q.x+q.dx*SLP_ARM, hz=q.z+q.dz*SLP_ARM;
      spawnDebris(hx,SLP_H,hz,MATS[5],1.2); spawnDebris(q.x,SLP_H*.5,q.z,MATS[5],1.0);
      for(let s=0;s<5;s++) spark(hx,SLP_H,hz,rf(-9,9),rf(2,10),rf(-9,9),rf(.2,.5),1,.75,.4); }
  }
  if(hit){ for(const m of [SLP.pole,SLP.arm,SLP.head]){ m.instanceMatrix.needsUpdate=true; m.instanceColor.needsUpdate=true; }
    if(col) col.needsUpdate=true; }
}
/* カメラ近傍の街灯を本物の点光源にする：0.25 秒ごとに 150m 以内の近い順 8 灯を選び、出入りはフェードさせる */
const SLPL={t:0, ls:[], pick:[]};
function pickLampLights(){
  const P=SLPL.pick; P.length=0;
  if(!lampObj||!lampPos.length||blackout) return;
  const col=lampObj.geometry.attributes.color||lampObj.geometry.attributes.acolor; const A=col?col.array:null;
  const cx=camera.position.x, cy=camera.position.y, cz=camera.position.z;
  for(let i=0;i<lampPos.length;i+=3){
    if(A&&A[i]===0&&A[i+1]===0&&A[i+2]===0) continue;                 // 消えた灯
    const d=Math.hypot(lampPos[i]-cx,lampPos[i+1]-cy,lampPos[i+2]-cz); if(d>150) continue;
    // 近い順 8 件を保つ（挿入ソート）
    let k=P.length; if(k>=8){ if(d>=P[7].d) continue; k=7; } else P.push(null);
    while(k>0&&P[k-1].d>d){ P[k]=P[k-1]; k--; }
    P[k]={i:i,d:d};
  }
}
function updLampLights(dt){
  SLPL.t-=dt;
  if(SLPL.t<=0){ SLPL.t=.25; pickLampLights();
    for(const L of SLPL.ls) L.keep=false;
    for(const p of SLPL.pick){ let L=null; for(const q of SLPL.ls) if(q.li===p.i){ L=q; break; }
      if(!L){ const pole=lampPos[p.i+1]>20;
        L={li:p.i, x:lampPos[p.i], y:lampPos[p.i+1]-.6, z:lampPos[p.i+2], r:pole?44:36, c:pole?[1,.78,.5]:slpLightCol(), i:0, tau:1, s:0, k:0, keep:true};
        SLPL.ls.push(L); }
      L.keep=true; } }
  for(let n=SLPL.ls.length-1;n>=0;n--){ const L=SLPL.ls[n];
    L.k+=(L.keep?1:-1)*dt/.35; if(L.k>1) L.k=1;
    if(L.k<=0){ SLPL.ls.splice(n,1); continue; }
    L.i=0.75*cityPower*L.k; }
  if(SLPL.ls.length>12) SLPL.ls.sort((a,b)=>b.k-a.k).length=12;
}
const SIG={list:[], t:0, pole:null, head:null, lamp:null};""")
    # ── 2. 初期化・生成・毎フレーム・再生成・爆風 ──
    rep("  initLanterns();\n  initSignals();", "  initLanterns();\n  initSignals();\n  initStreetLamps();")
    rep("  buildGrid();\n  buildLamps();", "  buildGrid();\n  buildStreetLamps();\n  buildLamps();")   # 空間グリッドの後（建物との重なりを bldAt で避ける）、光点の前
    rep("updLanterns(dt); updSignals(dt);", "updLanterns(dt); updSignals(dt); updStreetLamps(dt);")
    rep("SIGNS.length=0; HOT.length=0; CGAI=null; PED.list.length=0; LAN.list.length=0;",
        "SIGNS.length=0; HOT.length=0; CGAI=null; PED.list.length=0; LAN.list.length=0; SLP.list.length=0; SLPL.ls.length=0;")
    rep("  pedsBlast(x,z,R*1.0); lanternsBlast(x,z,R);", "  pedsBlast(x,z,R*1.0); lanternsBlast(x,z,R); streetLampsBlast(x,z,R);")
    # ── 3. 点光源の候補：爆発・火災の後に入れ、スコアは 0.6 倍（爆発優先） ──
    rep("  cand.sort((a,b)=>b.s-a.s);", """  updLampLights(dt);
  for(let i=0;i<SLPL.ls.length;i++){ const L=SLPL.ls[i]; L.s=0.6*L.i*L.r/(Math.hypot(L.x-cx,L.y-cy,L.z-cz)+L.r*0.5+1); cand.push(L); }
  cand.sort((a,b)=>b.s-a.s);""")
    # ── 4. 既存の光の仕組みを種別（y で判別：電柱 26 ／ アーム街灯 10.2）に対応させる ──
    # 光点：アーム街灯は少し控えめに（電柱の 15 サイズの光暈と同じ材質を共有するため）
    rep("  for(let i=0;i<lampPos.length/3;i++) col.push(1,.86,.62);",
        "  for(let i=0;i<lampPos.length/3;i++){ if(lampPos[i*3+1]>20) col.push(1,.86,.62); else { const c=slpLampCol(); col.push(c[0]*.78,c[1]*.78,c[2]*.78); } }")
    # 路面の光溜まり：アーム街灯は半径 18
    rep("  for(let i=0;i<lampPos.length;i+=3) add(lampPos[i],lampPos[i+2],30,.55,.44,.26);",
        "  for(let i=0;i<lampPos.length;i+=3){ if(lampPos[i+1]>20) add(lampPos[i],lampPos[i+2],30,.55,.44,.26); else if(slpWhite()) add(lampPos[i],lampPos[i+2],18,.34,.40,.46); else add(lampPos[i],lampPos[i+2],18,.50,.40,.24); }")
    # 光の地図：種別の色、アーム街灯は重み 3.2
    rep("  for(let i=0;i<lampPos.length;i+=3) add(lampPos[i],Math.min(lampPos[i+1],9),lampPos[i+2],1.0,.86,.62,5.0);",
        "  for(let i=0;i<lampPos.length;i+=3){ if(lampPos[i+1]>20) add(lampPos[i],9,lampPos[i+2],1.0,.86,.62,5.0); else { const c=slpLampCol(); add(lampPos[i],9,lampPos[i+2],c[0],c[1],c[2],3.2); } }")
    # 電線：電柱どうしだけに張る（アーム街灯には張らない）
    rep("    const ax=lampPos[i*3], ay=lampPos[i*3+1], az=lampPos[i*3+2];",
        "    const ax=lampPos[i*3], ay=lampPos[i*3+1], az=lampPos[i*3+2];\n    if(ay<20) continue;                                        // アーム街灯（幹線）は電線を持たない")
    rep("      const bx=lampPos[j*3], by=lampPos[j*3+1], bz=lampPos[j*3+2];",
        "      const bx=lampPos[j*3], by=lampPos[j*3+1], bz=lampPos[j*3+2];\n      if(by<20) continue;")
    # ── 5. 検証フック ──
    rep("  lampObj:()=>lampObj, lampPos:()=>lampPos, killLampsNear:killLampsNear,",
        "  lampObj:()=>lampObj, lampPos:()=>lampPos, killLampsNear:killLampsNear, SLP:()=>SLP, lampLights:()=>SLPL.ls, streetLampsBlast:streetLampsBlast,")
