# 渋谷の実在感（S2・S3・S1）
#   S2 スクランブル交差点の人流：
#      ・PED_MAX 1600→2600（InstancedMesh 2 枚の枠。initPeds は PED_MAX を使うので追従する）。
#      ・四つ角の待機 34 人→130 人×画質係数（QUAL.pedK。中以下は自動で 0.7／0.4 倍）、待機位置を歩道の奥 9m まで広げる。
#        待っている人は交差点の中心を向く。
#      ・横断の波：青になった瞬間に全員が歩き出す（m=3 一斉）のをやめ、m=4「出発待ち」に 0〜4.5 秒のばらつきを持たせ、
#        先頭から順に渡り出す。目的地は 50% が対角（斜め横断）、50% が隣の角。目的点は角の奥 0〜9m に散らすので
#        交差点の中で重ならない。待機中（m=2／m=4）は歩かないので足踏み（bob）しない。
#   S3 大型ビジョンの枠 6→12 枚：
#      ・NSIGN・uSgO/uSgR/uSgA/uSgP の配列長・addSign／addScreensAtCrossing の上限を 12 に。LIT_PRE の文字列長が変わるので
#        シェーダのキャッシュ鍵は自動で更新される（19_hooks）。探索半径 30→40m。
#      ・北東の角（区画 (2,1)）：角から 55m 離れていた mkMegaTower(…,62,8123) を角に密着させ（addScreensAtCrossing が拾う）、
#        空き地だった残りの区画を fillLot で埋める（北の帯と東の帯）。
#      ・109 の北面（文化村通り側、交差点に向く面）に壁面ビジョン 1 枚。駅ビルの広場側にもビジョン 1 枚（下記）。
#   S1 ハチ公前広場（区画 (1,1)）：
#      ・舗装は路面キャンバス（buildRoad）に 5.6m の市松の石畳＋明るい縁石として描く（ボクセルの板にしないので
#        歩行者がそのまま立てる・bldAt の判定を変えなくてよい・メッシュ 0 枚）。東の帯はバス乗り場のアスファルトと白線。
#      ・駅ビル：白タイルの帯とオフィス窓の 31m の箱（mkProp。1 階は広場側がガラスの出入口、庇の下に灯り）、屋上の
#        駅名サイン台、広場側の壁面ビジョン（素材 25 の面に kind 2）。regLM '渋谷駅' は維持。
#      ・ハチ公像：黒御影石の台座（26）＋ブロンズ（新素材 54）の犬。倒壊や名所の対象にしない（regLM しない）。
#      ・滞留する群衆：像の周り半径 3〜13m に 120 人×画質係数。m=2・ci=-1 で立ち止まり、半分は像の方を向く。
#        updPeds のスクランブル切替は ci>=0 の人だけ対象にし、広場の人はときどき（1 人あたり平均 250 秒に 1 回）
#        広場の別の場所へ歩いて行って再び立ち止まる。
#      ・バス乗り場：東の帯に緑の都営／東急バス（新素材 53、mkProp・style 'car'）4 台と白線の乗車口。
#      ・広場の照明柱 3 本（lampPos に登録するので光点・光溜まり・光の地図・消灯に乗る）、ケヤキ 3 本、ベンチ 4 基。
#   新素材 ID は 53〜54（46〜52 は店先モジュールが使用済み）。
TITLE='渋谷：スクランブル交差点の人流（上限 2600・横断の波）／大型ビジョン 12 枚（四つ角・109・駅）／ハチ公前広場（舗装・像・滞留群衆・バス乗り場）'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)

    # ── 素材：53 バス車体（緑）、54 ブロンズ ──
    rep("  /*@MATS*/", """  53:{n:'バス車体(緑)', r:.16,g:.46,b:.28, hp:78,  sc:2, ld:0.1},
  54:{n:'ブロンズ',     r:.36,g:.30,b:.18, hp:160, sc:3, ld:1.0},
  /*@MATS*/""")

    # ══════════ S3. 大型ビジョンの枠 6→12 枚 ══════════
    rep("#define NSIGN 6", "#define NSIGN 12")
    rep("{value:Array.from({length:6},()=>new THREE.Vector4())},", "{value:Array.from({length:12},()=>new THREE.Vector4())},", 4)
    rep("  if(SIGNS.length>=6) return;", "  if(SIGNS.length>=12) return;")
    rep("    if(SIGNS.length>=6) break;", "    if(SIGNS.length>=12) break;")
    rep("      if(d<bd&&d<30){ bd=d; best=b; }", "      if(d<bd&&d<40){ bd=d; best=b; }")

    # ══════════ S2. スクランブル交差点の人流 ══════════
    rep("const PED_MAX=1600;", "const PED_MAX=2600;")
    # 四つ角の待機人数と待機位置。広場の滞留群衆もここで置く
    rep("""    PED.corners.forEach((q,ci)=>{ for(let k=0;k<34;k++) put(q[0]+q[2]*rf(0,4),q[1]+q[3]*rf(0,4),{m:2,ci:ci,v:rf(1.3,1.9)}); });
  }""", """    const nc=Math.round(130*QUAL.pedK);                                   // 1 角 130 人（画質係数つき）
    PED.corners.forEach((q,ci)=>{ for(let k=0;k<nc;k++) put(q[0]+q[2]*rf(0,9),q[1]+q[3]*rf(0,9),{m:2,ci:ci,v:rf(1.3,1.9)}); });
    // ハチ公前広場：像の周りに立ち止まる人（ci=-1 なのでスクランブルには出ない）
    PED.plaza=null;
    if(SBY&&SBY.statue){ PED.plaza={x:SBY.statue[0],z:SBY.statue[1],r:13};
      const np=Math.round(120*QUAL.pedK);
      for(let k=0;k<np;k++){ const a=Math.random()*6.283, r=rf(3,13), x=PED.plaza.x+Math.cos(a)*r, z=PED.plaza.z+Math.sin(a)*r;
        if(x>SBY.x1-1.5||z>SBY.z1-1.5) continue;
        const toS=Math.random()<.5;
        put(x,z,{m:2,ci:-1,v:rf(0.8,1.2),fx:toS?-Math.cos(a):rf(-1,1),fz:toS?-Math.sin(a):rf(-1,1)}); } }
  }""")
    # 横断の波：出発待ち m=4、対角 50%、目的点は角の奥に散らす。広場の人（ci<0）は対象外
    rep("""    if(scr&&!PED.scr) for(const p of L) if(p.m===2){
      let tc=(Math.random()*4)|0; if(tc===p.ci) tc=3-p.ci;
      const q=PED.corners[tc]; p.tc=tc; p.tx=q[0]+q[2]*rf(0,4); p.tz=q[1]+q[3]*rf(0,4); p.m=3; }""",
        """    if(scr&&!PED.scr) for(const p of L) if(p.m===2&&p.ci>=0){
      const tc=Math.random()<.5 ? 3-p.ci : (p.ci^(Math.random()<.5?1:2));     // 半分は斜め横断、半分は隣の角
      const q=PED.corners[tc]; p.tc=tc; p.tx=q[0]+q[2]*rf(0,9); p.tz=q[1]+q[3]*rf(0,9);
      p.m=4; p.wait=rf(0,4.5); }                                                 // 先頭から順に渡り出す""")
    rep("""    } else if(p.m===3){
      const dx=p.tx-p.x, dz=p.tz-p.z, d=Math.hypot(dx,dz);
      if(d<.4){ p.m=2; p.ci=p.tc; } else { p.x+=dx/d*p.v*dt; p.z+=dz/d*p.v*dt; }
    }""", """    } else if(p.m===3){
      const dx=p.tx-p.x, dz=p.tz-p.z, d=Math.hypot(dx,dz);
      if(d<.4){ p.m=2; p.ci=p.tc; if(p.tc<0){ p.fx=rf(-1,1); p.fz=rf(-1,1); } } else { p.x+=dx/d*p.v*dt; p.z+=dz/d*p.v*dt; }
    } else if(p.m===4){ p.wait-=dt; if(p.wait<=0) p.m=3; }                   // 出発待ち
    else if(p.m===2&&p.ci<0&&PED.plaza&&Math.random()<dt*0.004){           // 広場の人：ときどき別の場所へ歩く（1 人あたり平均 250 秒に 1 回）
      const a=Math.random()*6.283, r=rf(3,PED.plaza.r), tx=PED.plaza.x+Math.cos(a)*r, tz=PED.plaza.z+Math.sin(a)*r;
      if(!bldAt(tx,1,tz)&&!(SBY&&(tx>SBY.x1-1.5||tz>SBY.z1-1.5))){ p.tc=-1; p.tx=tx; p.tz=tz; p.m=3; }
    }""")
    rep("""    else if(p.m===3){ hx=p.tx-p.x; hz=p.tz-p.z; }
    else if(p.m===9){ hx=p.vx; hz=p.vz; }""", """    else if(p.m===3){ hx=p.tx-p.x; hz=p.tz-p.z; }
    else if(p.m===9){ hx=p.vx; hz=p.vz; }
    else if(p.m===2||p.m===4){ if(p.ci>=0&&PED.corners){ const q=PED.corners[p.ci]; hx=-q[2]; hz=-q[3]; } else if(p.fx!==undefined){ hx=p.fx; hz=p.fz; } }   // 待つ人は交差点（像）の方を向く""")
    rep("    const moving=p.m!==2, bob=", "    const moving=p.m!==2&&p.m!==4, bob=")

    # ══════════ S1／S3. 渋谷の街の生成 ══════════
    rep("/*@DEFS*/", r"""/* ══════════ 渋谷：ハチ公前広場・駅ビル・バス（work/pc/feat/31_shibuya_crowd.py） ══════════ */
let SBY=null;                                   // 広場の範囲と像の位置（buildRoad の舗装・buildPeds の群衆が参照）
HOOKS.reset.push(function(){ SBY=null; PED.plaza=null; });
/* 駅ビル（旧東急東横店の西口側）：白タイルの帯とオフィス窓。1 階の広場側はガラスの出入口と庇、屋上に駅名サイン台。
   広場側（+x 面）に壁面ビジョン（素材 25 の面に kind 2）。W・D に庇ぶんの余白 3 マスを含む */
function mkSbyStation(fx,fz){
  const W=35, D=27, H=22, HH=H+6, BX1=W-4, BZ1=D-4;      // 本体は x 0..BX1, z 0..BZ1
  const b=mkProp(fx,fz,W,HH,D,'office',(set,fill)=>{
    for(let y=0;y<H;y++){
      const slab=(y%3===0);
      for(let z=0;z<=BZ1;z++) for(let x=0;x<=BX1;x++){
        const edge=(x===0||x===BX1||z===0||z===BZ1);
        if(!edge&&!slab) continue;
        let m=1;
        if(edge){
          const front=(x===BX1||z===BZ1);                                  // 広場側
          if(y<3) m=front?3:(((x+z)%6===0)?23:4);                           // 1 階：広場側はガラスの出入口、裏は柱と蛍光灯の窓
          else if(y===3) m=25;                                              // 庇の高さの帯
          else if(x===BX1&&z>=3&&z<=16&&y>=6&&y<=14) m=25;                  // ビジョンの面
          else if(slab) m=22;                                               // 白タイルの帯
          else { const al=(x===0||x===BX1)?z:x; m=(al%4===0)?22:officeWin(x,y,z,3311,3); }
        }
        set(x,y,z,m);
      }
    }
    fill(0,H,0,BX1,H,BZ1,1);                                                // 屋上
    fill(0,H+1,0,BX1,H+1,0,18); fill(0,H+1,0,0,H+1,BZ1,18);                 // 裏の手すり
    fill(BX1-5,H+1,5,BX1,H+3,BZ1-5,25); fill(BX1,H+1,6,BX1,H+3,BZ1-6,17);   // 駅名サイン台（広場側は白電照）
    for(let x=4;x<BX1-4;x+=7) fill(x,H+1,BZ1-6,x+2,H+2,BZ1-4,20);           // 屋上の設備
    // 庇：広場側の 2 面に 3 マス張り出す（金属パネル、3 マスごとに灯り）
    for(let z=0;z<=BZ1+3;z++) for(let k=1;k<=3;k++) set(BX1+k,3,z,((z+k)%3===0)?27:25);
    for(let x=0;x<=BX1;x++) for(let k=1;k<=3;k++) set(x,3,BZ1+k,((x+k)%3===0)?27:25);
    for(let z=4;z<=BZ1;z+=6) set(BX1+3,0,z,5), set(BX1+3,1,z,5), set(BX1+3,2,z,5);     // 庇を支える柱
    for(let x=4;x<=BX1;x+=6) set(x,0,BZ1+3,5), set(x,1,BZ1+3,5), set(x,2,BZ1+3,5);
  });
  if(b){
    b.noScr=true;
    addSign([fx+(BX1+1)*VOX, 6*VOX, fz+17*VOX],[0,-1],14*VOX,9*VOX,SIGN_ATLAS.vision,2,0,b);   // 広場側の壁面ビジョン（+x 面）
  }
  return b;
}
/* ハチ公像：黒御影石の台座にブロンズの犬（座って +z／+x を向く）。倒壊や名所の対象にしない */
function mkHachiko(fx,fz){
  return mkProp(fx,fz,5,8,6,'statue',(set,fill)=>{
    fill(0,0,0,4,0,5,26); fill(1,1,1,3,2,4,26);           // 台座（基壇 1 段＋本体 2 段）
    fill(1,3,1,3,4,3,54);                                  // 胴
    fill(1,3,4,3,3,4,54);                                  // 前脚
    fill(1,5,2,2,6,3,54); set(1,7,2,54); set(2,7,3,54);    // 首・頭・耳
    set(2,3,0,54);                                         // 尾
  });
}
/* 都営／東急バス：全長 11.2m・幅 2.8m・高さ 4.2m の緑の箱。z 方向に向く（前が +z） */
function mkBus(fx,fz){
  return mkProp(fx,fz,2,3,8,'car',(set,fill)=>{
    fill(0,0,0,1,0,7,53); fill(0,0,1,1,0,1,35); fill(0,0,6,1,0,6,35);      // 床・スカートとタイヤ
    fill(0,1,1,1,1,6,37); fill(0,1,7,1,1,7,37);                             // 側窓・前面ガラス
    fill(0,1,0,1,1,0,53); fill(0,0,0,1,0,0,39); fill(0,0,7,1,0,7,38);       // 後部・尾灯・前照灯
    fill(0,2,0,1,2,7,53); fill(0,2,7,1,2,7,17);                             // 屋根・行先表示
  });
}
/* ハチ公前広場：区画 (1,1)。駅ビル（北西）・バス乗り場（東の帯）・像と群衆（南東の角寄り）・ケヤキ・照明柱・ベンチ */
function sbyBuildPlaza(){
  const x0=XL[1]+XW[1]/2+2, z0=ZL[1]+ZW[1]/2+2, x1=XL[2]-XW[2]/2-2, z1=ZL[2]-ZW[2]/2-2;
  SBY={x0:x0,z0:z0,x1:x1,z1:z1, bus:{x0:x1-32,x1:x1-2,z0:z0+2,z1:z0+62}, bays:[], statue:[x1-16,z1-16], lamps:[]};
  // 駅ビル
  { const _l=blds.length; mkSbyStation(x0+2, z0+2); regLM(_l,'渋谷駅','STATION DOWN'); }
  // ハチ公像（交差点側の角から 16m）
  { const s=SBY.statue; mkHachiko(s[0]-2.5*VOX, s[1]-3*VOX); }
  // ベンチ：像を囲んで 4 基
  for(const [dx,dz] of [[-9,-6],[8,-7],[-8,8],[9,7]]) mkProp(SBY.statue[0]+dx, SBY.statue[1]+dz, 3,1,1,'gate',(set)=>{ set(0,0,0,5); set(1,0,0,5); set(2,0,0,5); });
  // ケヤキ 3 本
  mkTree(x0+6, z1-56, 1); mkTree(x0+42, z1-20, 2); mkTree(x0+14, z1-36, 3);
  // 照明柱 3 本（鉄骨の柱＋灯り。lampPos に登録して光点・光溜まり・光の地図に乗せる）
  for(const [lx,lz] of [[x1-42,z1-30],[x0+28,z1-50],[x1-42,z1-62]]){
    mkProp(lx,lz,1,7,1,'pole',(set)=>{ for(let y=0;y<6;y++) set(0,y,0,5); set(0,6,0,27); });
    lampPos.push(lx+VOX/2,8.4,lz+VOX/2); SBY.lamps.push([lx,lz]);
  }
  // バス乗り場：東の帯に 4 台（z 方向に並ぶ）。白線は buildRoad で描く
  const B=SBY.bus;
  for(let k=0;k<4;k++){ const bz=B.z0+4+k*14; SBY.bays.push(bz); if(k!==2) mkBus(B.x0+9, bz); }   // 1 台分は出発した後の空き
}
/* 路面キャンバス：広場の石畳（5.6m の市松）・縁石・バス乗り場のアスファルトと白線 */
function sbyPaintPlaza(g,TX,TZ,px){
  const P=SBY, w=P.x1-P.x0, d=P.z1-P.z0;
  g.fillStyle='#2a2b2f'; g.fillRect(TX(P.x0)-2,TZ(P.z0)-2,w*px+4,d*px+4);                 // 縁石（やや明るい）
  for(let i=0;i<w/5.6;i++) for(let j=0;j<d/5.6;j++){
    g.fillStyle=((i+j)&1)?'#1f2126':'#25272c';
    g.fillRect(TX(P.x0+i*5.6),TZ(P.z0+j*5.6),Math.min(5.6,w-i*5.6)*px+0.5,Math.min(5.6,d-j*5.6)*px+0.5);
  }
  g.fillStyle='rgba(120,112,100,.10)';                                                       // 目地
  for(let x=P.x0;x<P.x1;x+=5.6) g.fillRect(TX(x),TZ(P.z0),0.12*px,d*px);
  for(let z=P.z0;z<P.z1;z+=5.6) g.fillRect(TX(P.x0),TZ(z),w*px,0.12*px);
  const B=P.bus;
  g.fillStyle='#0f1216'; g.fillRect(TX(B.x0),TZ(B.z0),(B.x1-B.x0)*px,(B.z1-B.z0)*px);        // バス乗り場のアスファルト
  g.fillStyle='rgba(232,232,226,.70)';
  g.fillRect(TX(B.x0+6),TZ(B.z0),0.35*px,(B.z1-B.z0)*px);                                   // 乗車口の縁の白線
  for(const bz of P.bays){
    g.fillRect(TX(B.x0+6),TZ(bz-1.5),20*px,0.35*px); g.fillRect(TX(B.x0+6),TZ(bz+12.5),20*px,0.35*px);   // 停車枠
    for(let k=0;k<5;k++) g.fillRect(TX(B.x0+1+k*1.0),TZ(bz+4),0.45*px,4*px);                            // 乗車位置のゼブラ
  }
  g.fillStyle='rgba(60,150,90,.35)'; g.fillRect(TX(B.x0),TZ(B.z0),6*px,(B.z1-B.z0)*px);    // 乗降場（緑の帯）
}
/*@DEFS*/""")

    # 109：北面（文化村通り側・交差点に向く面）に壁面ビジョン
    rep("  { const _l=blds.length; mk109(XL[1]+XW[1]/2+16, ZL[2]+ZW[2]/2+16); regLM(_l,'SHIBUYA109','109 FALLS'); }",
        """  { const _l=blds.length, fx=XL[1]+XW[1]/2+16, fz=ZL[2]+ZW[2]/2+16, b=mk109(fx, fz); regLM(_l,'SHIBUYA109','109 FALLS');
    if(b) addSign([fx+28*VOX, 7*VOX, fz],[-1,0],12*VOX,12*VOX,SIGN_ATLAS.vision,2,0,b); }   // 北面（交差点側）の壁面ビジョン""")
    # 北東の角：タワーを角に密着させ、残りの区画を fillLot で埋める。駅前はハチ公前広場に
    rep("""  mkMegaTower(XL[2]+XW[2]/2+10, ZL[1]+ZW[1]/2+10, 20, 20, 62, 8123);
  // 駅舎（低く広い）
  { const _l=blds.length; mkBuilding(XL[1]+XW[1]/2+8, ZL[1]+ZW[1]/2+8, 26, 20, 14, 'office', 3311,
             {faces:[1,3], dense:.5}); regLM(_l,'渋谷駅','STATION DOWN'); }""",
        """  { const tx=XL[2]+XW[2]/2+2, tz=ZL[2]-ZW[2]/2-2-20*VOX;              // 交差点の北東の角に密着（addScreensAtCrossing が拾う距離）
    mkMegaTower(tx, tz, 20, 20, 62, 8123);
    fillLot(tx, ZL[1]+ZW[1]/2+2, XL[3]-XW[3]/2-2, tz-8);                   // 区画 (2,1) の残り：北の帯（袖看板のせり出し 7m ぶん空ける）
    fillLot(tx+20*VOX+8, tz, XL[3]-XW[3]/2-2, ZL[2]-ZW[2]/2-2); }          // 東の帯
  // ハチ公前広場（駅ビル・像・バス乗り場・ケヤキ・照明柱）
  sbyBuildPlaza();""")
    # 路面：広場の舗装とバス乗り場
    rep("""  if(MAPID===1&&CGAI){
    // センター街：タイル舗装の歩行者の多い通り""", """  if(MAPID===1&&SBY) sbyPaintPlaza(g,TX,TZ,px);                      // ハチ公前広場の石畳とバス乗り場
  if(MAPID===1&&CGAI){
    // センター街：タイル舗装の歩行者の多い通り""")

    # ── 検証フック ──
    U("/*@PCDBG*/", "sby:()=>({signs:SIGNS.length, nsign:12, peds:PED.list.length, pedMax:PED_MAX, corner:PED.list.filter(p=>p.ci>=0&&(p.m===2||p.m===3||p.m===4)).length, crossing:PED.list.filter(p=>p.m===3&&p.ci>=0).length, waiting:PED.list.filter(p=>p.m===4).length, plaza:PED.list.filter(p=>p.ci===-1).length, buses:blds.filter(b=>b.style==='car'&&b.W===2&&b.D===8).length, statue:blds.filter(b=>b.style==='statue').length, sby:SBY?{x0:SBY.x0,z0:SBY.z0,x1:SBY.x1,z1:SBY.z1,statue:SBY.statue}:null}), /*@PCDBG*/")
