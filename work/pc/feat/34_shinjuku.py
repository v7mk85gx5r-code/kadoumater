# 西新宿の実在感（N1・N2）
#   N1 都庁を「3 棟＋広場」に：
#   ・第二本庁舎 mkMetroGov2（W=30・D=26、西側 x<16 を 163m（116 マス）、東側を 120m（86 マス）まで積む 2 段の階段状。
#     外装は第一本庁舎の低層部と同じ 3 マス角の市松（黒御影 26 と officeWin）、y%8 の床スラブ、四隅と段の境にシャフト、
#     屋上に冷却塔・アンテナ・航空障害灯）。区画 (1,1) の西側は 36m しか空いていないので、第一本庁舎の北（44m の空き）に
#     12m の隙間を取って置く。regLM で「都庁第二本庁舎」として登録（コンパス・地図に出る。閾値 0.4）。
#   ・都民広場 hsCivicPlaza：第一本庁舎の南面と議事堂の間に半径 22.4m の半円（平らな辺が都庁側、弧が議事堂側）。
#     弧に沿って 2 階レベルの列柱回廊（白タイルの台座 → 打放しの柱 23 を 3m 間隔 → 屋根 23 → 手すり 18。屋根の裏に 1 柱おきに
#     灯り 27）と、広場の照明柱 6 本（鉄骨 5＋灯り 27。buildLightMap の照り返しに乗る）。石畳の同心円は路面キャンバスに描く
#     （ボクセルで敷くと歩行者が埋まる）。広場には 60 人（画質係数つき）が滞留：半分は立ち止まり（m=2）、半分は弦に沿ってゆっくり歩く。
#   N2 一般区画を「駐車場に立つ 1 本塔」から「基壇＋中層 2 棟＋サンクンガーデン」に：
#   ・区画の対角 2 角に中層のオフィス（11〜13×13〜15 マス、50〜84m）。残る 2 角はサンクンガーデン（50%）／旧 9×9 の別棟（35%）／
#     樹木 3 本。北西の角は placeUtils の設備（x0+4,z0+4）と重なるのでガーデンは置かない。
#   ・サンクンガーデン hsSunken：20×20 マス。外周 2 マスのデッキ（打放し 23／タイル 13）＋内側の手すり 18、一辺の中央 4 マスは
#     白タイルの階段で手すりを開ける。内側は 1 層低い（路面のまま＝キャンバスに目地を描く）。樹木 3 本・照明柱 2 本・ベンチ。
#   ・中央通り（XW>=36）の中央分離帯：17m 間隔で銀杏（mkTree）。交差点は ZW/2+10m 空ける。路面キャンバスに 3.2m の分離帯を描き、
#     buildTraffic の車線を ±2.3 → ±6.0 に外へずらす（西新宿だけ。渋谷のスクランブル 40m は変えない）。
#   既存の mkMetroGov / mkAssembly / mkPodium / mkMegaTower の呼び出し行は変えず、buildHigh の一意な行を anchor に追加する。
#   新素材は使わない（既存の 1,3,5,13,18,19,22,23,25,26,27,44 だけ）。
#   負荷：第二本庁舎 ≈ 2 万ボクセル（greedy 後 4〜5 千面）、中層 8 棟（各 3〜5 千ボクセル）、樹木 +30 本、広場・ガーデンは数百ボクセル。
#   毎フレームの処理は 3 秒ごとの歩行者の再配置判定だけ。
TITLE='西新宿：都庁を 3 棟＋都民広場（半円の列柱）に／一般区画を基壇＋中層 2 棟＋サンクンガーデン／中央通りの中央分離帯の銀杏'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)

    # ── 1. 定義（本体）：第二本庁舎・都民広場・区画の中層群・サンクンガーデン・分離帯の銀杏・路面の描画・歩行者 ──
    rep("/*@DEFS*/", r"""/* ══════════ 西新宿の実在感（work/pc/feat/34_shinjuku.py） ══════════ */
const HS={plaza:null, paint:[], gov2:0, mid:0, sunken:0, annex:0, median:0, pedK:-1};
/* 東京都庁第二本庁舎：2 段の階段状（西 163m／東 120m）。外装は第一本庁舎の低層部と同じ 3 マス角の市松 */
function mkMetroGov2(fx,fz){
  const W=30, D=26, H1=86, H2=116, STEP=16, HH=H2+12;
  HS.gov2++;
  return mkProp(fx,fz,W,HH,D,'tower',(set,fill)=>{
    const seedN=(fx*0.31+fz*0.47)%100;
    for(let y=0;y<H2;y++){
      const xEnd=(y<H1)?W-2:STEP-1;                              // 低い段（東側）は H1 まで
      for(let z=1;z<D-1;z++) for(let x=1;x<=xEnd;x++){
        const edge=(x===1||x===xEnd||z===1||z===D-2);
        if(!edge && y%8!==0) continue;
        let m;
        if(y<10) m=(y===9)?1:(((x+z)%3===0)?5:3);                // ロビー：柱とガラス
        else if(y%8===0) m=1;                                      // 床スラブ
        else {
          const gx=Math.floor((x-1)/3), gz=Math.floor((z-1)/3), gy=Math.floor(y/8);
          m=((gx+gz+gy)%2===0) ? 26 : officeWin(x,y,z,seedN,8);  // 市松
        }
        set(x,y,z,m);
      }
      // シャフト：四隅と段の境（黒御影）
      for(const px of [1,2,W-3,W-2]) if(y<H1||px<STEP) for(const pz of [1,2,D-3,D-2]) set(px,y,pz,26);
      for(const px of [STEP-2,STEP-1]) for(const pz of [1,2,D-3,D-2]) set(px,y,pz,26);
    }
    fill(STEP,H1,1,W-2,H1,D-2,1);                                 // 東側の屋上
    fill(1,H2,1,STEP-1,H2,D-2,1);                                 // 西側の屋上
    fill(STEP+3,H1+1,4,STEP+6,H1+3,7,25); fill(STEP+8,H1+1,D-9,STEP+11,H1+3,D-6,25);   // 冷却塔
    for(let x=STEP+3;x<=STEP+6;x++) set(x,H1+4,5,5);
    fill(4,H2+1,4,7,H2+2,7,25);
    for(let y=H2+1;y<H2+11;y++) set(STEP-6,y,D>>1,5);             // アンテナ
    set(STEP-6,H2+11,D>>1,19);
    set(2,H2+1,2,19); set(STEP-2,H2+1,D-3,19); set(W-3,H1+1,2,19); set(W-3,H1+1,D-3,19);   // 航空障害灯
  });
}
/* 都民広場：半径 R の半円。平らな辺を z=zf（都庁側）に置き、弧（議事堂側）に沿って 2 階レベルの列柱回廊を立てる。
   石畳の同心円は路面キャンバス（hsPaintRoad）に描く */
function hsCivicPlaza(cx,zf,R){
  const Rv=Math.round(R/VOX), W=2*Rv+3, D=Rv+1, cxl=(W-1)/2;
  const b=mkProp(cx-cxl*VOX-VOX/2, zf, W, 9, D, 'plaza', (set,fill)=>{
    const n=Math.round(Math.PI*Rv*VOX/3.0);                       // 柱の本数（約 3m 間隔）
    for(let k=0;k<=n;k++){
      const a=Math.PI*k/n, px=Math.round(cxl+Math.cos(a)*(Rv-1)), pz=Math.round(Math.sin(a)*(Rv-1));
      for(let y=1;y<=5;y++) set(px,y,pz,23);                      // 打放しの柱
      if(k%2===1){ const ix=Math.round(cxl+Math.cos(a)*(Rv-1.6)), iz=Math.round(Math.sin(a)*(Rv-1.6)); if(ix!==px||iz!==pz) set(ix,5,iz,27); }   // 屋根の裏の灯り（屋根に接する）
    }
    for(let z=0;z<D;z++) for(let x=0;x<W;x++){
      const d=Math.hypot(x-cxl,z);
      if(d>=Rv-2.6&&d<=Rv+0.6){ set(x,0,z,22); set(x,6,z,23); } // 台座（白タイル）と屋根
      if(d>=Rv-0.6&&d<=Rv+0.6) set(x,7,z,18);                     // 屋根の手すり
    }
    for(const q of [[7,45],[7,135],[12,20],[12,70],[12,110],[12,160]]){   // 広場の照明柱 6 本
      const t=q[1]*Math.PI/180, px=Math.round(cxl+Math.cos(t)*q[0]), pz=Math.round(Math.sin(t)*q[0]);
      for(let y=0;y<5;y++) set(px,y,pz,5); set(px,5,pz,27);
    }
  });
  if(b){ b.noScr=true; HS.plaza={cx:cx,zf:zf,R:R}; HS.paint.push({t:'plaza',cx:cx,zf:zf,R:R}); }
  return b;
}
/* サンクンガーデン：20×20 マス。外周 2 マスのデッキと手すり、一辺の中央に白タイルの階段。内側は 1 層低い（路面のまま） */
function hsSunken(fx,fz,seed){
  const N=20, side=Math.abs(seed|0)%4, s0=8, s1=11;
  const b=mkProp(fx,fz,N,6,N,'plaza',(set,fill)=>{
    const stair=(x,z)=> (side===0&&z<=1&&x>=s0&&x<=s1)||(side===1&&z>=N-2&&x>=s0&&x<=s1)||(side===2&&x<=1&&z>=s0&&z<=s1)||(side===3&&x>=N-2&&z>=s0&&z<=s1);
    for(let z=0;z<N;z++) for(let x=0;x<N;x++){
      const e=Math.min(x,z,N-1-x,N-1-z);
      if(e<=1) set(x,0,z, stair(x,z)?22:((e===0)?23:13));
    }
    for(let k=1;k<N-1;k++){                                        // 手すり（階段の所は開ける）
      if(!stair(k,1)) set(k,1,1,18); if(!stair(k,N-2)) set(k,1,N-2,18);
      if(!stair(1,k)) set(1,1,k,18); if(!stair(N-2,k)) set(N-2,1,k,18);
    }
    for(const q of [[3,16],[16,3]]){ for(let y=0;y<4;y++) set(q[0],y,q[1],5); set(q[0],4,q[1],27); }   // 照明柱
    fill(4,0,3,5,0,3,44); fill(14,0,16,15,0,16,44); fill(3,0,9,3,0,10,44); fill(16,0,9,16,0,10,44);  // ベンチ
  });
  if(b){ b.noScr=true; HS.sunken++; HS.paint.push({t:'sq',x:fx+2*VOX,z:fz+2*VOX,w:(N-4)*VOX}); }
  mkTree(fx+2*VOX, fz+2*VOX, (seed*3+1)|0); mkTree(fx+11*VOX, fz+4*VOX, (seed*3+2)|0); mkTree(fx+6*VOX, fz+11*VOX, (seed*3+3)|0);
  return b;
}
/* 一般区画：基壇＋超高層の後に、対角 2 角へ中層オフィス（50〜84m）、残る 2 角へサンクンガーデン／別棟／樹木 */
function hsLotFill(i,j,cx,cz,w){
  const x0=XL[i]+XW[i]/2, x1=XL[i+1]-XW[i+1]/2, z0=ZL[j]+ZW[j]/2, z1=ZL[j+1]-ZW[j+1]/2;
  const C=((i*5+j*3)&1) ? [[-1,-1],[1,1],[1,-1],[-1,1]] : [[1,-1],[-1,1],[-1,-1],[1,1]];   // [sx,sz]：前 2 つが中層
  const at=(sx,sz,bw,bd,ins)=>[ (sx>0)?x1-ins-bw:x0+ins, (sz>0)?z1-ins-bd:z0+ins ];
  for(let k=0;k<2;k++){
    const bw=RI2(11,13), bd=RI2(13,15), BW=(bw+2*MG)*VOX, BD=(bd+2*MG)*VOX;
    const p=at(C[k][0],C[k][1],BW,BD,9);
    mkBuilding(p[0], p[1], bw, bd, RI2(36,60), 'office', (i*11+j*5+k*7)|0, {faces:[0,1,2,3], dense:.25});   // 西新宿は看板を控えめに
    HS.mid++;
  }
  for(let k=2;k<4;k++){
    const sx=C[k][0], sz=C[k][1], r=Math.random(), nw=(sx<0&&sz<0);   // 北西の角は placeUtils の設備と重なる
    if(r<.5&&!nw){ const p=at(sx,sz,20*VOX,20*VOX,6); hsSunken(p[0],p[1],(i*7+j*3+k)|0); }
    else if(r<.85||nw){ const p=at(sx,sz,17*VOX,17*VOX,9); mkBuilding(p[0],p[1],9,9,9+RI2(0,6),'office',(i*7+j+k)|0,{faces:[0,1,2,3],dense:.32}); HS.annex++; }
    else { const p=at(sx,sz,24*VOX,24*VOX,8); for(let t=0;t<3;t++) mkTree(p[0]+[2,12,6][t]*VOX, p[1]+[2,4,12][t]*VOX, (i*3+j+t)|0); }
  }
}
/* 中央通り（XW>=36）の中央分離帯に銀杏を sp 間隔で。交差点（ZW/2+10m）は空ける */
function hsMedianTrees(sp){
  for(let i=0;i<XL.length;i++){ if(XW[i]<36) continue;
    for(let z=CITY.z0+30; z<CITY.z1-30; z+=sp){
      let ok=true; for(let j=0;j<ZL.length;j++) if(Math.abs(z-ZL[j])<ZW[j]/2+10){ ok=false; break; }
      if(!ok) continue;
      mkTree(XL[i]-3.5*VOX, z-3.5*VOX, (i*29+z)|0); HS.median++;
    }
    HS.paint.push({t:'median',x:XL[i]});
  }
}
/* 路面キャンバス：都民広場の同心円の石畳、サンクンガーデンの目地、分離帯 */
function hsPaintRoad(g,TX,TZ,px){
  for(const P of HS.paint){
    if(P.t==='median'){
      const cuts=[]; for(let j=0;j<ZL.length;j++) cuts.push([ZL[j]-ZW[j]/2-6, ZL[j]+ZW[j]/2+6]);
      let za=CITY.z0+20; const segs=[];
      for(const c of cuts){ if(c[0]>za) segs.push([za,c[0]]); za=Math.max(za,c[1]); }
      if(za<CITY.z1-20) segs.push([za,CITY.z1-20]);
      for(const s of segs){
        g.fillStyle='#171b17'; g.fillRect(TX(P.x-1.6),TZ(s[0]),3.2*px,(s[1]-s[0])*px);
        g.fillStyle='rgba(150,150,140,.30)'; g.fillRect(TX(P.x-1.6),TZ(s[0]),0.35*px,(s[1]-s[0])*px); g.fillRect(TX(P.x+1.25),TZ(s[0]),0.35*px,(s[1]-s[0])*px);
      }
    } else if(P.t==='plaza'){
      const X=TX(P.cx), Z=TZ(P.zf), R=P.R*px;
      g.save(); g.beginPath(); g.moveTo(X-R,Z); g.arc(X,Z,R,0,Math.PI); g.closePath(); g.clip();
      g.fillStyle='#2a2927'; g.fillRect(X-R-2,Z-2,R*2+4,R+4);
      for(let r=P.R;r>0;r-=2.8){ g.fillStyle=(Math.round(r/2.8)&1)?'#2f2e2b':'#252422'; g.beginPath(); g.arc(X,Z,r*px,0,Math.PI); g.closePath(); g.fill(); }
      g.strokeStyle='rgba(0,0,0,.38)'; g.lineWidth=Math.max(1,0.3*px);
      for(let k=0;k<=8;k++){ const a=Math.PI*k/8; g.beginPath(); g.moveTo(X,Z); g.lineTo(X+Math.cos(a)*R,Z+Math.sin(a)*R); g.stroke(); }
      g.fillStyle='#38362f'; g.beginPath(); g.arc(X,Z,4*px,0,Math.PI); g.closePath(); g.fill();
      g.restore();
      g.fillStyle='#262523'; g.fillRect(X-4*px,Z+R-1,8*px,8*px);          // 議事堂への通路
    } else if(P.t==='sq'){
      const X=TX(P.x), Z=TZ(P.z), Wd=P.w*px;
      g.fillStyle='#22252a'; g.fillRect(X,Z,Wd,Wd);
      g.strokeStyle='rgba(0,0,0,.32)'; g.lineWidth=Math.max(1,0.25*px);
      for(let k=0;k<=P.w;k+=2.8){ g.beginPath(); g.moveTo(X+k*px,Z); g.lineTo(X+k*px,Z+Wd); g.stroke(); g.beginPath(); g.moveTo(X,Z+k*px); g.lineTo(X+Wd,Z+k*px); g.stroke(); }
      g.fillStyle='#2c2e31'; g.beginPath(); g.arc(X+Wd/2,Z+Wd/2,P.w*0.2*px,0,6.283); g.fill();
    }
  }
}
/* 都民広場の滞留：60 人（画質係数つき）。半分は立ち止まり（m=2）、半分は弦に沿ってゆっくり歩く */
function hsPlazaPeds(){
  if(MAPID!==2||!HS.plaza||!PED.body) return;
  const P=HS.plaza, n=Math.round(60*QUAL.pedK), R=P.R-5;
  for(let k=0;k<n&&PED.list.length<PED_MAX;k++){
    const a=Math.random()*Math.PI, r=Math.sqrt(Math.random())*R, x=P.cx+Math.cos(a)*r, z=P.zf+2.5+Math.sin(a)*r;
    if(bldAt(x,1,z)) continue;
    const o=(k&1) ? {m:2, ci:0, v:rf(1.3,1.9)} : (()=>{ const dz=z-P.zf, hc=Math.sqrt(Math.max(9,R*R-dz*dz)); return {m:0, ax:0, c:z, t:x, dir:Math.random()<.5?-1:1, v:rf(.45,.8), a:P.cx-hc+2, b:P.cx+hc-2}; })();
    o.x=x; o.z=z; o.plz=1; o.col=CLOTH[(Math.random()*CLOTH.length)|0]; o.hair=Math.random()<.85?.06:.32; o.hs=rf(.92,1.08); o.ph=Math.random()*6.28;
    PED.list.push(o);
  }
  HS.pedK=QUAL.pedK;
}
HOOKS.reset.push(function(){ HS.plaza=null; HS.paint.length=0; HS.gov2=0; HS.mid=0; HS.sunken=0; HS.annex=0; HS.median=0; HS.pedK=-1; });
HOOKS.build.push(function(){ if(MAPID===2) hsPlazaPeds(); });
HOOKS.update.push(function(dt){                                   // 画質の切替で歩行者が作り直されたら、広場の人も戻す
  if(MAPID!==2||!HS.plaza||QUAL.pedK===HS.pedK) return;
  HS.pedK=QUAL.pedK;
  for(let i=0;i<PED.list.length;i++) if(PED.list[i].plz) return;
  hsPlazaPeds();
});
HOOKS.init.push(function(){ if(typeof STYLE_NAME==='object') STYLE_NAME.plaza='広場'; });
/*@DEFS*/""")

    # ── 2. buildHigh：一般区画の別棟（9×9、55%）を「中層 2 棟＋サンクンガーデン／別棟／樹木」に ──
    rep("""    if(Math.random()<.55)
      mkBuilding(cx+w*VOX/2+24, cz-16, 9, 9, 9+((Math.random()*7)|0), 'office',
                 (i*7+j)|0, {faces:[0,2], dense:.32});""",
        """    hsLotFill(i,j,cx,cz,w);                         // ② 対角に中層 2 棟、残る角にサンクンガーデン／別棟／樹木（work/pc/feat/34_shinjuku.py）""")

    # ── 3. buildHigh：都庁を 3 棟＋都民広場に（議事堂の直後。gov の LM には含めない） ──
    rep("    const _l=blds.length; mkAssembly(gx-28, gz+52); regLM(_l,'都議会議事堂','ASSEMBLY HALL DOWN');",
        """    const _l=blds.length; mkAssembly(gx-28, gz+52); regLM(_l,'都議会議事堂','ASSEMBLY HALL DOWN');
    // 第二本庁舎：区画の西側は 36m しか無いので第一本庁舎の北（12m の隙間）に 2 段の階段状の棟を建てる（work/pc/feat/34_shinjuku.py）
    { const _l2=blds.length; mkMetroGov2(gx-52, gz-61); regLM(_l2,'都庁第二本庁舎','METRO GOV 2 FALLS',0.40); }
    // 都民広場：第一本庁舎の南面（gz+26.6）と議事堂（gz+52）の間に半径 22.4m の半円。弧に沿って 2 階レベルの列柱回廊
    hsCivicPlaza(gx+1.5, gz+27.5, 22.4);""")

    # ── 4. buildHigh：中央通りの中央分離帯の銀杏 ──
    rep("  // ③ 中央通りの銀杏並木\n",
        "  // ③ 中央通りの銀杏並木：歩道側は placeStreetTrees、中央分離帯は 17m 間隔（work/pc/feat/34_shinjuku.py）\n  hsMedianTrees(17);\n")

    # ── 5. buildTraffic：中央通り（西新宿・XW>=36）の車線を分離帯の外へ ──
    rep("    TRF.lanes.push({ax:2,c:XL[i]-2.3,dir:-1,a:z0,b:z1}); TRF.lanes.push({ax:2,c:XL[i]+2.3,dir:1,a:z0,b:z1}); }",
        "    const lo=(MAPID===2&&XW[i]>=36)?6.0:2.3;             // 西新宿の中央通り（40m）は中央分離帯の植栽を避けて車線を外へ（work/pc/feat/34_shinjuku.py）\n    TRF.lanes.push({ax:2,c:XL[i]-lo,dir:-1,a:z0,b:z1}); TRF.lanes.push({ax:2,c:XL[i]+lo,dir:1,a:z0,b:z1}); }")

    # ── 6. buildRoad：広場の石畳・ガーデンの目地・分離帯を描く（汚れの前） ──
    rep("  // 汚れとマンホール：車道の帯の中だけ（work/pc/feat/33_roads.py）\n",
        "  if(MAPID===2) hsPaintRoad(g,TX,TZ,px);                  // 都民広場の石畳・サンクンガーデン・中央分離帯（work/pc/feat/34_shinjuku.py）\n  // 汚れとマンホール：車道の帯の中だけ（work/pc/feat/33_roads.py）\n")

    # ── 7. 検証フック ──
    U("/*@PCDBG*/", "hs:()=>({gov2:HS.gov2, plaza:!!HS.plaza, mid:HS.mid, sunken:HS.sunken, annex:HS.annex, median:HS.median, peds:PED.list.filter(p=>p.plz).length, paint:HS.paint.length, lanes:TRF.lanes.filter(l=>l.ax===2&&Math.abs(l.c-XL[2])<8).map(l=>Math.round((l.c-XL[2])*10)/10), lm:LMS.map(L=>L.name)}), /*@PCDBG*/")
