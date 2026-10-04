# 歌舞伎町の実在感（K1・K3・K5・K2）
#   K1 通り幅の序列：ZW を実際の序列 [職安通り25 / 11 / 11 / 花道通り16 / さくら通り11 / 靖国通り30] に直す。
#      これまでは配列が逆向きで、アーチと初期視点 VIEWS[0] のある ZL[5]（靖国通り）が 14m の裏通り、さくら通り ZL[4] が 25m の幹線だった。
#      直すと自動で：靖国通りに車線（buildTraffic は ZW>=20）・街灯（20_street_lamps）・区役所通りとの交差点に信号、
#      さくら通りに提灯・駐車・歩行者。路面キャンバスのセントラルロード区間（花道通り〜靖国通り）をタイル舗装で塗る。
#      mkGate は ZL[5]-ZW[5]/2-5 で 8m 南へ動くので VIEWS[0] も z+8 して見え方を保つ。
#   K3 空き区画を埋める：区画 (1,0)・(4,1) を「超高層タワー」として fillLot から外し、中央に小さなオフィス 1 棟だけ置いていたのをやめ、
#      ほかの区画と同じく fillLot（27m 格子の雑居ビル）で詰める。
#   K5 袖看板の積層：mkBuilding に opt.signs（2〜4）と opt.signFace を追加。指定された建物は通り側の面の同じ柱に、高さ帯を分けた
#      袖看板を色違いで積み上げる（面が広ければもう 1 列）。fillLot（歌舞伎町）でセントラルロード XL[2] か幅 11m 以下の通りに面する
#      建物に signs:2〜4 を渡す。signs 未指定の建物（他マップ・他の通り）は従来どおり 1 枚で乱数列も変えない。
#   K2 セントラルロードの歩行者天国：XL[2] に駐車しない・アーチ〜花道通りの間に歩行者 220 人（画質係数つき）・提灯の間隔を半分・
#      アーチの奥と花道通りの T 字路に鉄の車止め（mkProp、style 'gate' で倒壊や得点の対象外）。
TITLE='歌舞伎町の実在感：通り幅の序列・空き区画を埋める・袖看板の積層・セントラルロードの歩行者天国'
def apply(rep, between, src):
    # ── K1. 通り幅の序列 ──
    rep("  ZW=[  30,  11,  11,  16,  25,  14];   // 靖国通り30m・職安通り25m",
        "  ZW=[  25,  11,  11,  16,  11,  30];   // ZL[0]=職安通り25m／ZL[3]=花道通り16m／ZL[4]=さくら通り11m／ZL[5]=靖国通り30m（アーチ側）")
    rep("  ()=>({x:XL[2]+1.0, y:40, z:ZL[5]+70, yaw:0, pitch:-0.11}),",
        "  ()=>({x:XL[2]+1.0, y:40, z:ZL[5]+78, yaw:0, pitch:-0.11}),")
    # 路面キャンバス：セントラルロード（花道通り〜靖国通り）はタイル舗装の歩行者天国。ゴジラロード北側と他マップは従来の暖色
    rep("""  g.fillStyle='rgba(70,58,48,.30)';
  g.fillRect(TX(XL[2]-XW[2]/2),TZ(ZL[0]),XW[2]*px,(ZL[4]-ZL[0])*px);""",
        """  if(MAPID===0){
    const a=TX(XL[2]-XW[2]/2), za=ZL[3]+ZW[3]/2, zb=ZL[5]-ZW[5]/2-4;
    g.fillStyle='#26262a'; g.fillRect(a,TZ(za),XW[2]*px,(zb-za)*px);
    g.fillStyle='rgba(120,110,100,.16)';
    for(let z=za;z<zb;z+=2) g.fillRect(a,TZ(z),XW[2]*px,0.12*px);
    g.fillStyle='rgba(70,58,48,.30)'; g.fillRect(a,TZ(ZL[0]),XW[2]*px,(ZL[2]-ZL[0])*px);
  } else {
    g.fillStyle='rgba(70,58,48,.30)';
    g.fillRect(TX(XL[2]-XW[2]/2),TZ(ZL[0]),XW[2]*px,(ZL[4]-ZL[0])*px);
  }""")

    # ── K3. 空き区画を埋める ──
    rep("    if(i===1&&j===0) continue;                     // 超高層タワーA\n    if(i===4&&j===1) continue;                     // 超高層タワーB\n", "")
    rep("""  // 超高層タワー2棟
  // 歌舞伎町に超高層は無い。最も高いのは東宝ビル(130m)
  mkBuilding((XL[1]+XL[2])/2-16, (ZL[0]+ZL[1])/2-16, 16, 16, 32, 'office', 4211,
             {faces:[0,1,2,3], dense:.75});
  mkBuilding((XL[4]+XL[5])/2-14, (ZL[1]+ZL[2])/2-14, 14, 14, 28, 'office', 9137,
             {faces:[0,1,2,3], dense:.70});
""", """  // 歌舞伎町に超高層は無い。最も高いのは東宝ビル(130m)。区画 (1,0)・(4,1) も fillLot で雑居ビルを詰める
""")

    # ── K5. 袖看板の積層（mkBuilding） ──
    rep("""  /* ── ④ 巨大縦看板：地上から屋上まで一気に届く電照看板。
        歌舞伎町の写真で最も目立つ要素 ── */
  if((style==='zakkyo'||style==='shop') && H>12 && R()<dense*0.55){
    const f=faces[(R()*faces.length)|0];
    const nm=(R()<.6)?mainNeon:NEON[(R()*NEON.length)|0];
    const y0=g1, y1=H-1;
    const wdt=RI(2,3);                  // 看板の幅
    const d=RI(3,5);                    // 街路へのせり出し
    // 支持する鉄骨
    if(f===0||f===1){
      const zc=fZ0+((fd/2)|0);
      const bx=(f===0)?fX0-1:fX1+1;
      for(let y=y0;y<=y1;y+=4)
        for(let k=1;k<=d;k++) set((f===0)?bx-k+1:bx+k-1, y, zc, 5);
      // 看板本体
      if(f===0) fill(fX0-d,y0,zc-wdt, fX0-1,y1,zc+wdt, nm);
      else      fill(fX1+1,y0,zc-wdt, fX1+d,y1,zc+wdt, nm);
      // 縁の電飾
      for(let y=y0;y<=y1;y+=3){
        if(f===0){ set(fX0-d,y,zc-wdt,16); set(fX0-d,y,zc+wdt,16); }
        else     { set(fX1+d,y,zc-wdt,16); set(fX1+d,y,zc+wdt,16); }
      }
    } else {
      const xc=fX0+((fw/2)|0);
      for(let y=y0;y<=y1;y+=4)
        for(let k=1;k<=d;k++) set(xc, y, (f===2)?fZ0-k+1:fZ1+k-1, 5);
      if(f===2) fill(xc-wdt,y0,fZ0-d, xc+wdt,y1,fZ0-1, nm);
      else      fill(xc-wdt,y0,fZ1+1, xc+wdt,y1,fZ1+d, nm);
      for(let y=y0;y<=y1;y+=3){
        if(f===2){ set(xc-wdt,y,fZ0-d,16); set(xc+wdt,y,fZ0-d,16); }
        else     { set(xc-wdt,y,fZ1+d,16); set(xc+wdt,y,fZ1+d,16); }
      }
    }
  }
""", """  /* ── ④ 巨大縦看板：地上から屋上まで一気に届く電照看板。
        歌舞伎町の写真で最も目立つ要素 ──
        opt.signs（2〜4）を渡された建物は、通り側の面（opt.signFace）の同じ柱に高さ帯を分けた袖看板を色違いで積み上げる
        （一番街・さくら通りの密度）。面が広ければもう 1 列、帯を半分ずらして並べる。signs 未指定なら従来どおり 1 枚 */
  { const nS=Math.max(1,Math.min(4,((opt&&opt.signs)|0)||1));
  if((style==='zakkyo'||style==='shop') && H>12 && (nS>1 || R()<dense*0.55)){
    const f=(nS>1&&opt.signFace!=null&&faces.indexOf(opt.signFace)>=0)?opt.signFace:faces[(R()*faces.length)|0];
    const xf=(f===0||f===1), span=xf?fd:fw, c0=((span/2)|0);
    const cols=[[c0,nS,0]];                                      // 列：[面に沿った中心, 枚数, 帯のずらし]
    if(nS>1&&span>=16) cols.push([(span>=17&&R()<.5)?c0+6:c0-6, RI(1,nS-1), 1]);
    const band=(nS===1)?(H-1-g1):Math.max(3,((H-1-g1)/nS)|0);  // 1 帯の高さ（マス）
    for(let ci=0;ci<cols.length;ci++){
      const cc=cols[ci][0], n=cols[ci][1];
      for(let s=0;s<n;s++){
        const nm=(s===0&&R()<.6)?mainNeon:NEON[(R()*NEON.length)|0];
        let y0=g1, y1=H-1;
        if(nS>1){ const b0=(s+cols[ci][2])%nS; y0=g1+b0*band; y1=Math.min(H-1,y0+band-1-(band>=5?1:0)); if(y1<y0+1) continue; }
        const wdt=(ci===0)?RI(2,3):2;        // 看板の幅
        const d=(nS===1)?RI(3,5):RI(3,4);    // 街路へのせり出し（余白 MG=4 マス内）
        if(xf){
          const zc=fZ0+cc, bx=(f===0)?fX0-1:fX1+1;
          // 支持する鉄骨（1 列目だけ）
          if(ci===0) for(let y=y0;y<=y1;y+=4) for(let k=1;k<=d;k++) set((f===0)?bx-k+1:bx+k-1, y, zc, 5);
          // 看板本体
          if(f===0) fill(fX0-d,y0,zc-wdt, fX0-1,y1,zc+wdt, nm);
          else      fill(fX1+1,y0,zc-wdt, fX1+d,y1,zc+wdt, nm);
          // 縁の電飾
          for(let y=y0;y<=y1;y+=3){
            if(f===0){ set(fX0-d,y,zc-wdt,16); set(fX0-d,y,zc+wdt,16); }
            else     { set(fX1+d,y,zc-wdt,16); set(fX1+d,y,zc+wdt,16); }
          }
        } else {
          const xc=fX0+cc;
          if(ci===0) for(let y=y0;y<=y1;y+=4) for(let k=1;k<=d;k++) set(xc, y, (f===2)?fZ0-k+1:fZ1+k-1, 5);
          if(f===2) fill(xc-wdt,y0,fZ0-d, xc+wdt,y1,fZ0-1, nm);
          else      fill(xc-wdt,y0,fZ1+1, xc+wdt,y1,fZ1+d, nm);
          for(let y=y0;y<=y1;y+=3){
            if(f===2){ set(xc-wdt,y,fZ0-d,16); set(xc+wdt,y,fZ0-d,16); }
            else     { set(xc-wdt,y,fZ1+d,16); set(xc+wdt,y,fZ1+d,16); }
          }
        }
      }
    }
  } }
""")
    # fillLot（歌舞伎町）：通り側の面に積層看板を渡す
    rep("""    mkBuilding(x0+a*pw+1.2, z0+b*pd+1.2, fw, fd, H, style,
               ((x0+a*pw)*7+(z0+b*pd)*13)|0, {faces:faces,dense:dense});""",
        """    const bo={faces:faces,dense:dense};
    if(MAPID===0){ const sf=kbSignFace(x0,z0,x1,z1,faces); if(sf>=0){ bo.signs=RI2(2,4); bo.signFace=sf; } }
    mkBuilding(x0+a*pw+1.2, z0+b*pd+1.2, fw, fd, H, style,
               ((x0+a*pw)*7+(z0+b*pd)*13)|0, bo);""")

    # ── 定義：kbSignFace・車止め ──
    rep("/*@DEFS*/", r"""/* ══════════ 歌舞伎町の密度（work/pc/feat/30_kabukicho_density.py） ══════════ */
/* 区画 (x0,z0)-(x1,z1) の面 faces のうち、セントラルロード（XL[2]。花道通りで塞がれた区間を除く）か
   幅 11m 以下の通りに面する面の番号を返す。無ければ -1。袖看板を積層する面を決める */
function kbSignFace(x0,z0,x1,z1,faces){
  for(let k=0;k<faces.length;k++){ const f=faces[k];
    if(f===0||f===1){ const e=(f===0)?x0-1.5:x1+1.5;                 // 区画の縁 → 通りの端
      for(let i=0;i<XL.length;i++){ if(Math.abs(Math.abs(e-XL[i])-XW[i]/2)>1) continue;
        if(i===2 && !(z0>=ZL[2]-1&&z1<=ZL[3]+1)) return f;
        if(XW[i]<=11) return f; } }
    else { const e=(f===2)?z0-1.5:z1+1.5;
      for(let j=0;j<ZL.length;j++){ if(Math.abs(Math.abs(e-ZL[j])-ZW[j]/2)>1) continue;
        if(ZW[j]<=11) return f; } }
  }
  return -1;
}
/* 車止め：通りを横切る鉄柱 n 本（2 マス＝2.8m 間隔、高さ 1 マス）。cx を中心に x 方向へ並べる。
   style 'gate' なので倒壊・得点・画面の対象にならない */
function kbBollards(cx,z,n){
  const W=(n-1)*2+1;
  mkProp(cx-((W/2)|0)*VOX, z, W, 2, 1, 'gate', (set,fill)=>{ for(let k=0;k<n;k++){ set(k*2,0,0,5); } });
}
/*@DEFS*/""")

    # ── K2. セントラルロードの歩行者天国 ──
    # 駐車しない（XL[2] 全体）
    rep("      if(MAPID===0&&i===2&&j===2) continue;           // 行き止まりの先は建物",
        "      if(MAPID===0&&i===2) continue;                  // セントラルロード（ゴジラロード）は歩行者天国：駐車しない")
    # 歩行者：アーチ〜花道通りの間に人の川（車道の中央まで歩く）。画質係数つき
    rep("  if(MAPID===1&&CGAI){                                      // センター街は人通りが多い",
        """  if(MAPID===0){                                            // セントラルロード：アーチから花道通りまで人の川
    const a=ZL[3]+ZW[3]/2+2, b=ZL[5]-ZW[5]/2-2, n=(220*QUAL.pedK)|0;
    for(let k=0;k<n;k++){ const x=XL[2]+rf(-XW[2]/2+1.5,XW[2]/2-1.5), t=rf(a,b);
      put(x,t,{m:0,ax:2,c:x,t:t,dir:Math.random()<.5?-1:1,v:rf(0.9,1.4),a:a,b:b}); }
  }
  if(MAPID===1&&CGAI){                                      // センター街は人通りが多い""")
    # 提灯：XL[2] は間隔を半分に
    rep("    for(let z=CITY.z0+10;z<CITY.z1-10;z+=rf(7,13)){\n      if(Math.random()>.55||!bldAt(c+sd*1.9,3,z)) continue;",
        "    for(let z=CITY.z0+10;z<CITY.z1-10;z+=((MAPID===0&&i===2)?rf(4,7):rf(7,13))){   // セントラルロードは密に\n      if(Math.random()>.55||!bldAt(c+sd*1.9,3,z)) continue;")
    # 車止め：アーチの奥と花道通りの T 字路
    rep("  { const _l=blds.length; mkGate(XL[2]-XW[2]/2-VOX*3, ZL[5]-ZW[5]/2-5, Math.round(XW[2]/VOX)+1); regLM(_l,'歌舞伎町一番街','GATE DOWN',0.5); }",
        "  { const _l=blds.length; mkGate(XL[2]-XW[2]/2-VOX*3, ZL[5]-ZW[5]/2-5, Math.round(XW[2]/VOX)+1); regLM(_l,'歌舞伎町一番街','GATE DOWN',0.5); }\n  kbBollards(XL[2], ZL[5]-ZW[5]/2-9, 6);                       // 車止め：アーチの奥\n  kbBollards(XL[2], ZL[3]+ZW[3]/2+1.5, 6);                     // 車止め：花道通りの T 字路")

    # ── 検証フック ──
    rep("  TRFcars:()=>TRF.cars, PARKED:()=>PARKED,",
        "  TRFcars:()=>TRF.cars, PARKED:()=>PARKED, kb:()=>({ZW:ZW.slice(),ZL:ZL.slice(),lanes:TRF.lanes.length,peds:PED.list.length,lan:LAN.list.length,parked:PARKED.length,blds:blds.length,gate:blds.filter(b=>b.style==='gate').length}),")
