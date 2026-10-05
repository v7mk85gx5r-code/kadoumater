# 走行車の車種（V1）：路線バス（緑帯＋灯った窓帯）・配送トラック・黒塗りハイヤーと、大通りの停留所
#   ・走行車は 4.4m の乗用車 1 種類（TRF.body/cabin）で、タクシーは色と行灯の違いだけだった。東京の大通りの実在感は
#     「緑帯の都バス」「白い配送トラック」「行灯のない黒いハイヤー」の混在で決まるので、車線幅 24m 以上の通りにだけ混ぜる。
#   ・InstancedMesh を 4 枚足す（バス：帯＋車輪／窓帯＋クリーム車体＋行先表示、トラック：荷台＋キャビン＋車輪／ガラス）。
#     乗用車の body/cabin には積まず、乗用車用のカウンタ nc を別に持つ（ランプは全車 4 灯のまま。位置だけ車種で変える）。
#   ・バスの窓帯は LIT_COLOR の区分 1（控えめな発光）で車内の灯りを表す。帯色はマップごと（都バス緑／渋谷はハチ公バス橙も／西新宿は京王赤も）。
#   ・車間は車長で測る（c.hl＝半長。乗用車 2.2／トラック 3.75／バス 5.25）。信号の停止位置も車長ぶん手前。
#   ・停留所：21_street_furniture のバス停（STF 'bus'）のうち、バス車線（幅 ≥24）の縁にあるものを車線に結び付け、
#     バスはそこで 4〜9 秒停車してから発車する（減速中はテールランプが明るくなる既存の表現に乗る）。歩道には待ち列（m=2, ci=-1）。
#     渋谷のスクランブル開始で m=2 の人を角へ送る処理は ci>=0 に限定した。
#   ・ヘッドライトの路面照射（22_lights_core の HL）は hlNote に c を渡しているので、半長を記録して前照灯／尾灯の位置を車種に合わせる。
#   ・爆風（trafficBlast）・落下塊・wreckCar は carXZ 経由でそのまま働く。爆風の半径判定と破片の数だけ車長で広げた。
#   負荷：InstancedMesh +4（各 1 ドローコール）。updTraffic の分岐は配列参照 1 回。毎フレームの配列生成（lp）を無くしたので CPU は僅かに軽い。
TITLE='走行車の車種（路線バス・配送トラック・黒塗りハイヤー）と大通りの停留所'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)

    # ── 1. 車線に通りの幅を持たせる ──
    # （34_shinjuku.py が先に中央通りの車線を lo に置き換えているので、その行を anchor にする）
    rep("    TRF.lanes.push({ax:2,c:XL[i]-lo,dir:-1,a:z0,b:z1}); TRF.lanes.push({ax:2,c:XL[i]+lo,dir:1,a:z0,b:z1}); }",
        "    TRF.lanes.push({ax:2,c:XL[i]-lo,dir:-1,a:z0,b:z1,w:XW[i]}); TRF.lanes.push({ax:2,c:XL[i]+lo,dir:1,a:z0,b:z1,w:XW[i]}); }")
    rep("    TRF.lanes.push({ax:0,c:ZL[j]-2.3,dir:1,a:x0,b:x1}); TRF.lanes.push({ax:0,c:ZL[j]+2.3,dir:-1,a:x0,b:x1}); }",
        "    TRF.lanes.push({ax:0,c:ZL[j]-2.3,dir:1,a:x0,b:x1,w:ZW[j]}); TRF.lanes.push({ax:0,c:ZL[j]+2.3,dir:-1,a:x0,b:x1,w:ZW[j]}); }")

    # ── 2. 走行車の生成：車種を選ぶ（vehSpawn）。長い車の後ろは間隔を広げる ──
    rep("""      const v=rf(10,14.5);
      const taxi=Math.random()<.28;                        // 約3割は濃紺のタクシー
      TRF.cars.push({l:li,t:t,v:v,vmax:v,taxi:taxi,col:taxi?[.07,.09,.17]:CAR_COLS[(Math.random()*CAR_COLS.length)|0]});
      t+=rf(34,90);""",
        """      const c=vehSpawn(li,L,t); TRF.cars.push(c);          // 車種：乗用車・タクシー・ハイヤー・バス・トラック（work/pc/feat/35_vehicles.py）
      t+=rf(34,90)+(c.hl-2.2)*2;""")

    # ── 3. 車間と信号の停止位置を車長で測る ──
    rep("    let gap=1e9;", "    let gap=1e9, ghl=2.2;")
    rep("      let d=(C[j].t-c.t)*L.dir; if(d<=0) d+=(L.b-L.a); if(d<gap) gap=d; }",
        "      let d=(C[j].t-c.t)*L.dir; if(d<=0) d+=(L.b-L.a); if(d<gap){ gap=d; ghl=C[j].hl||2.2; } }")
    rep("    let want=Math.min(c.vmax,Math.max(0,(gap-11)*.9));",
        "    let want=Math.min(c.vmax,Math.max(0,(gap-ghl-(c.hl||2.2)-6.6)*.9));   // 車間＝前の車の半長＋自分の半長＋6.6m")
    rep("      if(g<.4||(g<.6&&dd>9)) want=Math.min(want,Math.max(0,(dd-4)*.8));",
        "      if(g<.4||(g<.6&&dd>9)) want=Math.min(want,Math.max(0,(dd-1.8-(c.hl||2.2))*.8));")
    # 停留所：バスは停車してから発車する
    rep("    c.v+=(want-c.v)*Math.min(1,dt*(want<c.v?3.5:1.2));",
        "    if(c.kind==='bus'&&L.stops) want=busStopWant(c,L,want,dt);\n    c.v+=(want-c.v)*Math.min(1,dt*(want<c.v?3.5:1.2));")

    # ── 4. 描画：乗用車は nc 基準で body/cabin へ、バス・トラックは専用メッシュへ。ランプの位置は車種別 ──
    rep("""  for(let i=0;i<C.length;i++){
    const c=C[i];
    const xz=carXZ(c), x=xz[0], z=xz[1];
    const ang=carAng(c);                                 // 車体は x 軸向きに作ってある。進行方向へ回す""",
        """  let nc=0; vehBegin();                                  // nc＝乗用車の数（body/cabin の添字）。バス・トラックは別のメッシュ
  for(let i=0;i<C.length;i++){
    const c=C[i];
    const xz=carXZ(c), x=xz[0], z=xz[1];
    const ang=carAng(c);                                 // 車体は x 軸向きに作ってある。進行方向へ回す""")
    rep("""    put(MB,i*16,cs,sn,x,0,z); put(MC,i*16,cs,sn,x,0,z);
    CB[i*3]=c.col[0]; CB[i*3+1]=c.col[1]; CB[i*3+2]=c.col[2];
    CC[i*3]=8.08; CC[i*3+1]=8.10; CC[i*3+2]=8.13;                  // ガラスの印（種類4）""",
        """    if(c.kind) vehPut(c,cs,sn,x,z);                     // バス・トラック（work/pc/feat/35_vehicles.py）
    else {
      put(MB,nc*16,cs,sn,x,0,z); put(MC,nc*16,cs,sn,x,0,z);
      CB[nc*3]=c.col[0]; CB[nc*3+1]=c.col[1]; CB[nc*3+2]=c.col[2];
      CC[nc*3]=8.08; CC[nc*3+1]=8.10; CC[nc*3+2]=8.13; nc++;      // ガラスの印（種類4）
    }""")
    rep("    const lp=[[2.22,.62,.62,1],[2.22,.62,-.62,1],[-2.22,.66,.62,0],[-2.22,.66,-.62,0]];",
        "    const lp=VEH_LAMPS[c.kind]||VEH_LAMPS.car;             // 前照灯 2・尾灯 2 の位置（車種別。毎フレーム配列を作らない）")
    rep("  TRF.body.count=C.length; TRF.cabin.count=C.length; TRF.lamp.count=C.length*4;",
        "  TRF.body.count=nc; TRF.cabin.count=nc; TRF.lamp.count=C.length*4; vehEnd();")

    # ── 5. 破壊：爆風の半径と破片の数を車長で広げる ──
    rep("    if((cx-x)*(cx-x)+(cz-z)*(cz-z)+(y*y*.25)<r*r*1.3) wreckCar(c); }",
        "    const rr=r+(c.hl||2.2)-2.2;                             // 長い車は端が届く\n    if((cx-x)*(cx-x)+(cz-z)*(cz-z)+(y*y*.25)<rr*rr*1.3) wreckCar(c); }")
    rep("  for(let i=0;i<8;i++) spawnDebris(x+rf(-1.5,1.5),1.2,z+rf(-1.5,1.5),M,.9);",
        "  const nd=c.kind==='bus'?16:(c.kind==='truck'?11:8), sd=(c.hl||2.2)*.7;\n  for(let i=0;i<nd;i++) spawnDebris(x+rf(-sd,sd),1.2,z+rf(-sd,sd),M,.9);")

    # ── 6. ヘッドライトの路面照射（22_lights_core）：前照灯・尾灯の位置を車長に合わせる ──
    rep("  HL.a[k]=tmp; tmp.x=x; tmp.z=z; tmp.cs=cs; tmp.sn=sn; tmp.brake=brake; tmp.d=d;",
        "  HL.a[k]=tmp; tmp.x=x; tmp.z=z; tmp.cs=cs; tmp.sn=sn; tmp.brake=brake; tmp.d=d; tmp.hl=c.hl||2.2;")
    rep("    H.x=q.x+q.cs*2.4; H.y=0.9; H.z=q.z-q.sn*2.4; H.r=26; H.i=0.95*fade;",
        "    const fh=(q.hl||2.2)+0.2;\n    H.x=q.x+q.cs*fh; H.y=0.9; H.z=q.z-q.sn*fh; H.r=26; H.i=0.95*fade;")
    rep("      B.x=q.x-q.cs*2.3; B.y=0.7; B.z=q.z+q.sn*2.3; B.r=7; B.i=0.5*fade;",
        "      const bh=(q.hl||2.2)+0.1;\n      B.x=q.x-q.cs*bh; B.y=0.7; B.z=q.z+q.sn*bh; B.r=7; B.i=0.5*fade;")

    # ── 7. 歩行者：停留所の待ち列。buildPeds の再実行（画質変更）でも並び直す。渋谷のスクランブルは ci>=0 の人だけ ──
    # （31_shibuya_crowd.py が先に buildPeds の末尾（ハチ公前広場）とスクランブルの ci>=0 の判定を書いているので、その行を anchor にする）
    rep("        put(x,z,{m:2,ci:-1,v:rf(0.8,1.2),fx:toS?-Math.cos(a):rf(-1,1),fz:toS?-Math.sin(a):rf(-1,1)}); } }\n  }\n}",
        "        put(x,z,{m:2,ci:-1,v:rf(0.8,1.2),fx:toS?-Math.cos(a):rf(-1,1),fz:toS?-Math.sin(a):rf(-1,1)}); } }\n  }\n  vehBusQueue();                                            // 停留所の待ち列（work/pc/feat/35_vehicles.py）\n}")

    # ── 8. 定義：メッシュ・車種・停留所 ──
    rep("/*@DEFS*/", r"""/* ══════════ 走行車の車種 VEH（work/pc/feat/35_vehicles.py） ══════════
   路線バス（クリームの車体に緑帯、灯った窓帯、行先表示）・配送トラック（白い荷台＋キャビン）・黒塗りハイヤー（行灯なし）。
   幅 24m 以上の通りの車線にだけ混ぜる。乗用車の body/cabin には積まず、専用の InstancedMesh（4 枚）へ。
   局所座標：+x＝進行方向、原点＝地面。頂点色×インスタンス色が LIT_COLOR の区分になるので、
   発光・ガラスの部品を持つメッシュ（busWin・truckWin）のインスタンス色は 1 に固定する */
const VEH={bus:null, busWin:null, truck:null, truckWin:null, nb:0, nt:0, cb:0, ct:0, stops:[], BUS_MAX:48, TRUCK_MAX:64};
const VEH_LAMPS={                                      // [x, y, z, 1=前照灯/0=尾灯]
  car:[[2.22,.62,.62,1],[2.22,.62,-.62,1],[-2.22,.66,.62,0],[-2.22,.66,-.62,0]],
  bus:[[5.30,.80,.90,1],[5.30,.80,-.90,1],[-5.30,1.25,.95,0],[-5.30,1.25,-.95,0]],
  truck:[[3.78,.95,.78,1],[3.78,.95,-.78,1],[-3.78,.78,.88,0],[-3.78,.78,-.88,0]],
};
const VEH_HL={car:2.2, bus:5.25, truck:3.75};        // 半長
const VEH_BUS_COLS=[[[.16,.40,.24]],                  // 歌舞伎町：都バスの緑帯
  [[.16,.40,.24],[.82,.36,.18]],                       // 渋谷：都バス＋ハチ公バス風の橙
  [[.16,.40,.24],[.16,.40,.24],[.58,.12,.16]]];        // 西新宿：都バス＋京王バスの赤帯
const VEH_TRUCK_COLS=[[.86,.86,.84],[.86,.86,.84],[.86,.86,.84],[.72,.74,.78],[.58,.68,.82],[.64,.76,.60]];
function initVeh(){
  if(VEH.bus) return;
  // 箱を合成して 1 つのジオメトリに（21_street_furniture と同じ要領）。[w,h,d, x,y,z, r,g,b]
  const merge=(boxes)=>{
    const gs=boxes.map(b=>{ const g=new THREE.BoxGeometry(b[0],b[1],b[2]).toNonIndexed(); g.translate(b[3],b[4],b[5]);
      const n=g.attributes.position.count, c=new Float32Array(n*3);
      for(let i=0;i<n;i++){ c[i*3]=b[6]; c[i*3+1]=b[7]; c[i*3+2]=b[8]; }
      g.setAttribute('color',new THREE.BufferAttribute(c,3)); return g; });
    let n=0; for(const g of gs) n+=g.attributes.position.count;
    const P=new Float32Array(n*3), C=new Float32Array(n*3), V=new Float32Array(n*2); let o=0;
    for(const g of gs){ P.set(g.attributes.position.array,o*3); C.set(g.attributes.color.array,o*3); V.set(g.attributes.uv.array,o*2); o+=g.attributes.position.count; g.dispose(); }
    const m=new THREE.BufferGeometry();
    m.setAttribute('position',new THREE.BufferAttribute(P,3)); m.setAttribute('color',new THREE.BufferAttribute(C,3)); m.setAttribute('uv',new THREE.BufferAttribute(V,2));
    return m;
  };
  const mk=(geo,max)=>{ const mat=new THREE.MeshBasicMaterial({vertexColors:true,fog:true}); setupLitMaterial(mat);
    const m=new THREE.InstancedMesh(geo,mat,max); m.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    m.instanceColor=new THREE.InstancedBufferAttribute(new Float32Array(max*3),3);
    m.count=0; m.frustumCulled=false; scene.add(m); return m; };
  const ONE=[1,1,1], DK=[.13,.13,.14], TIRE=[.09,.09,.10], CREAM=[.84,.84,.79], GLOW=[2.66,2.68,2.60], GLASS=[8.08,8.10,8.13];
  // バス（全長 10.5m・幅 2.5m・高さ 3.05m）。帯と車輪＝インスタンス色（帯の色）、他は busWin（インスタンス色 1）
  VEH.bus=mk(merge([
    [10.5,.55,2.52, 0,1.375,0, ...ONE],                 // 窓下の帯
    [10.5,.18,2.52, 0,.44,0, ...ONE],                   // 裾の細い帯
    [.14,.42,2.46, 5.22,.62,0, ...DK],[.14,.42,2.46, -5.22,.62,0, ...DK],   // 前後バンパー
    [.95,.90,.30, 3.3,.45,1.12, ...TIRE],[.95,.90,.30, 3.3,.45,-1.12, ...TIRE],
    [.95,.90,.30, -3.3,.45,1.12, ...TIRE],[.95,.90,.30, -3.3,.45,-1.12, ...TIRE],
  ]),VEH.BUS_MAX);
  VEH.busWin=mk(merge([
    [10.5,.75,2.50, 0,.725,0, ...CREAM],                // 下まわりの車体
    [10.5,1.0,2.46, 0,2.15,0, ...GLOW],                 // 窓帯：車内の灯り（区分 1＝控えめな発光）。前後の面＝前面・後面ガラス
    [10.5,.40,2.50, 0,2.85,0, ...CREAM],                // 屋根
    [.06,.32,1.7, 5.26,2.84,0, 2.95,2.74,2.34],         // 行先表示（橙の LED）
    [.06,.26,1.3, -5.26,2.84,0, 2.95,2.68,2.30],        // 後部の系統表示
  ]),VEH.BUS_MAX);
  // トラック（全長 7.5m・幅 2.3m）。荷台とキャビン＝インスタンス色、ガラスは truckWin
  VEH.truck=mk(merge([
    [5.0,2.2,2.30, -1.25,2.0,0, ...ONE],                // 荷台（アルミバン）
    [2.2,1.7,2.10, 2.6,1.45,0, ...ONE],                 // キャビン
    [7.4,.34,1.90, 0,.55,0, ...DK],                     // シャシー
    [.14,.36,2.0, 3.68,.46,0, ...DK],                   // 前バンパー
    [.85,.85,.30, 2.6,.43,1.0, ...TIRE],[.85,.85,.30, 2.6,.43,-1.0, ...TIRE],
    [.85,.85,.30, -2.3,.43,1.0, ...TIRE],[.85,.85,.30, -2.3,.43,-1.0, ...TIRE],
  ]),VEH.TRUCK_MAX);
  VEH.truckWin=mk(merge([
    [.08,.72,1.90, 3.68,1.84,0, ...GLASS],              // フロントガラス
    [1.1,.66,2.14, 2.8,1.84,0, ...GLASS],               // 側面の窓
  ]),VEH.TRUCK_MAX);
}
/* 走行車 1 台の生成（buildTraffic の車線ループから）。幅 24m 以上の車線だけバス 10%・トラック 14% を混ぜる */
function vehSpawn(li,L,t){
  if(TRF.cars.length===0){ VEH.cb=0; VEH.ct=0; }        // buildTraffic の先頭（車列を空にした直後）で数え直す
  const wide=(L.w||0)>=24;
  let kind=null;
  if(wide){ const r=Math.random(); if(r<.10&&VEH.cb<VEH.BUS_MAX) kind='bus'; else if(r<.24&&VEH.ct<VEH.TRUCK_MAX) kind='truck'; }
  if(kind==='bus'){ VEH.cb++; const v=rf(7,10), cols=VEH_BUS_COLS[MAPID]||VEH_BUS_COLS[0];
    return {l:li,t:t,v:v,vmax:v,taxi:false,kind:'bus',hl:VEH_HL.bus,col:cols[(Math.random()*cols.length)|0],dwell:0,srv:null}; }
  if(kind==='truck'){ VEH.ct++; const v=rf(8.5,12);
    return {l:li,t:t,v:v,vmax:v,taxi:false,kind:'truck',hl:VEH_HL.truck,col:VEH_TRUCK_COLS[(Math.random()*VEH_TRUCK_COLS.length)|0]}; }
  const v=rf(10,14.5), r=Math.random();
  const taxi=r<.196, hire=!taxi&&r<.28;                 // 約3割がタクシー。そのうち 3 割は行灯のない黒塗りハイヤー
  return {l:li,t:t,v:v,vmax:v,taxi:taxi,hl:VEH_HL.car,col:taxi?[.07,.09,.17]:(hire?[.08,.08,.09]:CAR_COLS[(Math.random()*CAR_COLS.length)|0])};
}
/* 描画：updTraffic の描画ループから。行列の形は updTraffic の put と同じ（y 軸回転＋平行移動） */
function vehBegin(){ VEH.nb=0; VEH.nt=0; }
function vehMat(M,o,cs,sn,x,z){ M[o]=cs;M[o+1]=0;M[o+2]=-sn;M[o+3]=0; M[o+4]=0;M[o+5]=1;M[o+6]=0;M[o+7]=0;
  M[o+8]=sn;M[o+9]=0;M[o+10]=cs;M[o+11]=0; M[o+12]=x;M[o+13]=0;M[o+14]=z;M[o+15]=1; }
function vehPut(c,cs,sn,x,z){
  if(!VEH.bus) return;
  let A,B,j;
  if(c.kind==='bus'){ if(VEH.nb>=VEH.BUS_MAX) return; A=VEH.bus; B=VEH.busWin; j=VEH.nb++; }
  else { if(VEH.nt>=VEH.TRUCK_MAX) return; A=VEH.truck; B=VEH.truckWin; j=VEH.nt++; }
  vehMat(A.instanceMatrix.array,j*16,cs,sn,x,z); vehMat(B.instanceMatrix.array,j*16,cs,sn,x,z);
  const CA=A.instanceColor.array, CBw=B.instanceColor.array;
  CA[j*3]=c.col[0]; CA[j*3+1]=c.col[1]; CA[j*3+2]=c.col[2];
  CBw[j*3]=1; CBw[j*3+1]=1; CBw[j*3+2]=1;
}
function vehEnd(){
  if(!VEH.bus) return;
  VEH.bus.count=VEH.nb; VEH.busWin.count=VEH.nb; VEH.truck.count=VEH.nt; VEH.truckWin.count=VEH.nt;
  for(const m of [VEH.bus,VEH.busWin,VEH.truck,VEH.truckWin]){ m.instanceMatrix.needsUpdate=true; m.instanceColor.needsUpdate=true; }
}
/* 停留所：STF のバス停（k==='bus'）のうち、バス車線の縁（左側通行＝進行方向の左）にあるものを車線に結び付ける */
function vehFindStops(){
  VEH.stops.length=0;
  for(const L of TRF.lanes) L.stops=null;
  if(typeof STF!=='object'||!STF.list) return;
  for(const L of TRF.lanes){ if((L.w||0)<24) continue;
    const sd=L.ax===2?L.dir:-L.dir;                           // 縁石の側
    const cross=L.c+sd*(L.w/2-1.1);                            // バス停の柱（縁石から歩道側 1.2m）の横位置
    for(const q of STF.list){ if(q.k!=='bus'||q.dead) continue;
      const qc=L.ax===2?q.x:q.z, qt=L.ax===2?q.z:q.x;
      if(Math.abs(qc-cross)>1.6||qt<L.a+20||qt>L.b-20) continue;
      if(!L.stops) L.stops=[];
      const s={t:qt, x:q.x, z:q.z, L:L, sd:sd};
      L.stops.push(s); VEH.stops.push(s);
    }
  }
}
/* バスの停車：次の停留所の手前で止まり、4〜9 秒待って発車する。戻り値＝目標速度 */
function busStopWant(c,L,want,dt){
  if(c.dwell>0){ c.dwell-=dt; if(c.dwell<=0){ c.dwell=0; } return 0; }
  let best=null, bd=1e9;
  for(let i=0;i<L.stops.length;i++){ const s=L.stops[i];
    const dd=(s.t-L.dir*4.0-c.t)*L.dir;                       // バスの中心の目標＝柱の 4m 手前（前扉が柱に揃う）
    if(s===c.srv){ if(dd<-6) c.srv=null; continue; }          // 発車した停留所は 6m 離れるまで覚えておく
    if(dd<-1.5||dd>=bd) continue; bd=dd; best=s; }
  if(!best||bd>45) return want;
  if(bd<.9&&c.v<.5){ c.dwell=rf(4,9); c.srv=best; return 0; }
  return Math.min(want,Math.max(0,(bd-.5)*.8));
}
/* 停留所の待ち列：柱の後ろ（バスが来る側）へ 0.7m おきに 2〜6 人。buildPeds の末尾と街の生成の最後から呼ぶ */
function vehBusQueue(){
  if(!PED.body||!VEH.stops.length) return;
  const Lp=PED.list;
  for(let i=Lp.length-1;i>=0;i--){ const p=Lp[i]; if(p.bq) Lp.splice(i,1); }   // 並び直す（停留所の列だけ。広場の人は ci=-1 でも残す）
  for(const s of VEH.stops){
    const L=s.L, n=Math.round(rf(2,6)*QUAL.pedK);
    for(let k=0;k<n;k++){
      if(Lp.length>=PED_MAX) return;
      const t=s.t-L.dir*(1.4+.7*k)+rf(-.12,.12), cr=L.c+s.sd*(L.w/2-2.3+rf(1.35,1.75));   // 縁石から 1.35〜1.75m（柱とベンチの間）
      const x=L.ax===2?cr:t, z=L.ax===2?t:cr;
      if(bldAt(x,1,z)) continue;
      Lp.push({m:2,ci:-1,bq:true,v:rf(1.3,1.9),x:x,z:z,col:CLOTH[(Math.random()*CLOTH.length)|0],hair:Math.random()<.85?.06:.32,hs:rf(.92,1.08),ph:Math.random()*6.28});
    }
  }
}
function buildVeh(){ vehFindStops(); vehBusQueue(); }
function resetVeh(){ VEH.stops.length=0; VEH.nb=0; VEH.nt=0; VEH.cb=0; VEH.ct=0; if(VEH.bus) for(const m of [VEH.bus,VEH.busWin,VEH.truck,VEH.truckWin]) m.count=0; }
HOOKS.init.push(initVeh); HOOKS.build.push(buildVeh); HOOKS.reset.push(resetVeh);
/*@DEFS*/""")

    # ── 9. 検証フック ──
    U("/*@PCDBG*/",
      "VEH:()=>VEH, vehStats:()=>{ const C=TRF.cars; let bus=0,truck=0,car=0,hire=0,taxi=0,dwell=0; for(const c of C){ if(c.kind==='bus'){ bus++; if(c.dwell>0) dwell++; } else if(c.kind==='truck') truck++; else { car++; if(c.taxi) taxi++; else if(c.col[0]===.08) hire++; } }\n"
      "    return {cars:C.length, car:car, bus:bus, truck:truck, taxi:taxi, hire:hire, dwell:dwell, drawn:TRF.body.count+VEH.bus.count+VEH.truck.count, body:TRF.body.count, busDrawn:VEH.bus.count, truckDrawn:VEH.truck.count, lamps:TRF.lamp.count, stops:VEH.stops.length, lanesWithStops:TRF.lanes.filter(l=>l.stops).length, queue:PED.list.filter(p=>p.m===2&&p.ci===-1).length}; }, /*@PCDBG*/")
