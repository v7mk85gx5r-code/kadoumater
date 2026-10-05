# 屋上の造り込み（ENV-05）
#   mkBuilding（apart/zakkyo/shop/office）の屋上は、パラペット・2×2 の塔屋・2×2 の給水タンク・単発の室外機・1 本のアンテナだけで、
#   俯瞰（T）や高い視点から見ると面積の大半が素のコンクリ板だった。実際の雑居ビルの屋上を埋めている物をボクセルで足す：
#   ・占有表 ro（屋上の XZ）で互いに重ならないように置く。広告塔（既存）を先に置いて占有させ、残りに設備を詰める。
#   ・室外機の列：屋上の一辺に沿って 2 マス間隔で 54（室外機：薄い灰。ttSurf にファンの覆い＝円形グリルとルーバー）を 4〜12 台。
#     余裕があればパラペット側に配管（20）を 1 列這わせる。大きな屋上は 2 辺。入らない小さな屋上は 1〜3 台を散らす。
#     外壁に張り付く室外機も 20 → 54 に揃える。
#   ・架台つき給水塔：鉄骨の脚（5）4 本×2 段の上に 3×3×2 の 32（給水塔：water:1。壊すと放水する素材。mkBuilding では初めて使う）。
#     3×3 が入らない屋上は 2×2 の小型（脚 1 段）。
#   ・フェンス：マンション・オフィスは、パラペットの上に支柱（18、2 マス間隔）＋笠木（18）で金網風（ベランダの RAIL と同じ要領）。
#     横長の広告塔が占めている辺には立てない。
#   ・太陽光パネル：オフィス・マンションの 35%。空いている矩形に 53（太陽光パネル：濃紺。ttSurf に 0.47m のセル格子と枠）の
#     幅 4〜8×奥行 2 の板を 1 マス空けて 2〜4 列。後ろの列を 1 段高くして傾斜を表す。
#   ・ダクト：塔屋から屋上の端へ 20 を 1 列（曲がりを 1 回）。塔屋には扉（15）。
#   ・衛星アンテナ：鉄骨の支柱（5）の上に白い皿（22）。従来の細いアンテナ（5 の柱）も残す。
#   ・広告塔の照明バー：横長の看板の前面 1 マス内側に 27（灯り暖白）を 2 マス間隔で並べ、箱型は長辺の外側に並べる。
#     縦長の櫓は看板の直下の両端に 27。buildLightMap の照り返し（M_CLS 1）で看板面が下から照らされる。
#   ・航空障害灯は支柱（5）つきで屋上に立てる（従来は H+2 に浮いていた）。
#   全てボクセルなので、崩落の塊（spawnChunk）・剥離・延焼・看板の照り返しに自動で乗る。屋上は HH=H+9 の余白内（最大 H+8）。
#   新素材 ID は 53・54（46〜52 は 32_storefronts が使用）。
#   負荷：1 棟あたり +40〜120 ボクセル。greedy で面はまとまるので三角形は +100〜200／棟。毎フレームの処理は増えない。
TITLE='屋上の造り込み（室外機の列・架台つき給水塔・フェンス・太陽光パネル・ダクト・衛星アンテナ・広告塔の照明バー）'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)

    # ── 1. 素材表：53 太陽光パネル・54 室外機 ──
    rep("  /*@MATS*/", """  53:{n:'太陽光パネル', r:.11,g:.15,b:.24, hp:20, sc:1, ld:0.0},
  54:{n:'室外機',       r:.64,g:.64,b:.61, hp:40, sc:1, ld:0.2},
  /*@MATS*/""")

    # ── 2. シェーダ（ttSurf）：室外機のファンの覆い・ルーバー、太陽光パネルのセル格子 ──
    rep("  } else if(tile){\n    vec2 g=abs(fract(uv/0.7)-0.5);",
        """  } else if(mid==54.0){
    // 室外機：面の中央にファンの覆い（円形グリル：細い縦格子）、周りはルーバーの横筋
    vec2 lp=fract(uv/1.4)-0.5;
    float rr=length(lp);
    float fan=(1.0-smoothstep(0.30,0.36,rr))*smoothstep(0.07,0.11,rr);
    float ring=1.0-smoothstep(0.0,0.03,abs(rr-0.34));
    float lou=0.82+0.18*step(0.5,fract(uv.y/0.14));
    float grill=0.30+0.12*step(0.5,fract(uv.x/0.09));
    c*=mix(lou,grill,fan*near);
    c*=1.0-0.38*ring*near;
    c*=0.94+0.10*ttVN(uv*2.0);
  } else if(mid==53.0){
    // 太陽光パネル：濃紺のガラスに 0.47m のセル格子（銀の目地）と 1.4m ごとの枠
    vec2 g=abs(fract(uv/0.47)-0.5);
    float gl=1.0-smoothstep(0.42,0.48,max(g.x,g.y));
    c=mix(c*0.6+vec3(0.12,0.13,0.14),c,mix(1.0,gl,near));
    c*=0.90+0.20*ttVN(floor(uv/0.47)*1.7);
    float fr=abs(fract(uv.x/1.4)-0.5);
    c*=1.0-0.30*(1.0-smoothstep(0.0,0.04,fr))*near;
  } else if(tile){
    vec2 g=abs(fract(uv/0.7)-0.5);""")

    # ── 3. 外壁に張り付く室外機も同じ素材に ──
    rep("""      if(face===0) set(fX0-1,y,RI(fZ0+1,fZ1-1),20);
      else if(face===1) set(fX1+1,y,RI(fZ0+1,fZ1-1),20);
      else if(face===2) set(RI(fX0+1,fX1-1),y,fZ0-1,20);
      else set(RI(fX0+1,fX1-1),y,fZ1+1,20);""",
        """      if(face===0) set(fX0-1,y,RI(fZ0+1,fZ1-1),54);
      else if(face===1) set(fX1+1,y,RI(fZ0+1,fZ1-1),54);
      else if(face===2) set(RI(fX0+1,fX1-1),y,fZ0-1,54);
      else set(RI(fX0+1,fX1-1),y,fZ1+1,54);""")

    # ── 4. 屋上（塔屋から広告塔までを置き換える。パラペットの行はそのまま） ──
    rep("""    // 塔屋
    if(rX1-rX0>=3&&rZ1-rZ0>=3&&R()<.8){
      const tx=RI(rX0+1,rX1-2), tz=RI(rZ0+1,rZ1-2);
      fill(tx,H+1,tz,tx+1,H+3,tz+1,1);
    }
    // 給水タンク（脚付き）
    if(rX1-rX0>=3&&rZ1-rZ0>=3&&R()<.72){
      const tx=RI(rX0+1,rX1-2), tz=RI(rZ0+1,rZ1-2);
      set(tx,H+1,tz,5); set(tx+1,H+1,tz,5); set(tx,H+1,tz+1,5); set(tx+1,H+1,tz+1,5);
      fill(tx,H+2,tz,tx+1,H+3,tz+1,20);
    }
    // 室外機
    for(let k=0;k<RI(1,5);k++) set(RI(rX0,rX1),H+1,RI(rZ0,rZ1),20);
    // アンテナ
    if(R()<.5){
      const ax=RI(rX0,rX1), az=RI(rZ0,rZ1);
      for(let y=H+1;y<H+1+RI(3,7);y++) set(ax,y,az,5);
    }
    /* ⑥ 屋上広告塔：実際の歌舞伎町は屋上に鉄骨の櫓を組んで
       巨大な看板を立てる。上空から見た時の情報量を決める要素 */
    if((style==='zakkyo'||style==='shop'||style==='office') && R()<dense*0.92){
      const nm=(R()<.5)?mainNeon:NEON[(R()*NEON.length)|0];
      const kind=R();
      if(kind<0.45){
        // 縦長の塔：櫓を組んで、その上に細長い看板
        const tx=RI(rX0,Math.max(rX0,rX1-1)), tz=RI(rZ0,Math.max(rZ0,rZ1-1));
        const th=RI(6,12);
        for(let y=H+1;y<H+th;y++){          // 鉄骨の櫓
          set(tx,y,tz,5); set(tx+1,y,tz,5);
          if(y%3===0){ set(tx,y,tz+1,5); set(tx+1,y,tz+1,5); }
        }
        fill(tx-1,H+th,tz,tx+2,H+th+RI(3,6),tz,nm);
      } else if(kind<0.78){
        // 横長の看板：屋上の一辺いっぱいに立てる
        const th=RI(4,8), side=(R()<.5);
        for(let x=rX0;x<=rX1;x+=2)          // 支柱
          for(let y=H+1;y<H+3;y++) set(x,y,side?rZ0:rZ1,5);
        if(side) fill(rX0,H+3,rZ0,rX1,H+3+th,rZ0,nm);
        else     fill(rX0,H+3,rZ1,rX1,H+3+th,rZ1,nm);
      } else {
        // 箱型の広告塔：屋上に立方体を載せ、4面すべてが看板
        const bx=RI(rX0,Math.max(rX0,rX1-3)), bz=RI(rZ0,Math.max(rZ0,rZ1-3));
        const bw=Math.min(4,rX1-bx), bd=Math.min(4,rZ1-bz), bh=RI(4,9);
        if(bw>0&&bd>0){
          for(let y=H+1;y<=H+bh;y++)
            for(let z=bz;z<=bz+bd;z++) for(let x=bx;x<=bx+bw;x++){
              const edge=(x===bx||x===bx+bw||z===bz||z===bz+bd);
              if(edge) set(x,y,z, (y===H+1||y===H+bh)?5:nm);
            }
        }
      }
      // 広告塔の脇に赤い航空障害灯
      if(R()<.35) set(RI(rX0,rX1),H+2,RI(rZ0,rZ1),19);
    }""",
        """    /* ── 屋上の造り込み（work/pc/feat/25_rooftops.py）：占有表 ro で互いに重ならないように置く ── */
    const ro=new Uint8Array(W*D);
    const iX0=rX0+1, iX1=rX1-1, iZ0=rZ0+1, iZ1=rZ1-1, iw=iX1-iX0+1, idp=iZ1-iZ0+1;   // パラペットの内側
    const rIn=(x,z)=>x>=iX0&&x<=iX1&&z>=iZ0&&z<=iZ1;
    const rFree=(x0,z0,x1,z1)=>{ if(!rIn(x0,z0)||!rIn(x1,z1)) return false;
      for(let z=z0;z<=z1;z++) for(let x=x0;x<=x1;x++) if(ro[x+W*z]) return false; return true; };
    const rMark=(x0,z0,x1,z1)=>{ for(let z=Math.max(0,z0);z<=Math.min(D-1,z1);z++) for(let x=Math.max(0,x0);x<=Math.min(W-1,x1);x++) ro[x+W*z]=1; };
    const rPlace=(w,d,tries)=>{ if(iX1-w+1<iX0||iZ1-d+1<iZ0) return null;
      for(let t=0;t<tries;t++){ const x=RI(iX0,iX1-w+1), z=RI(iZ0,iZ1-d+1); if(rFree(x,z,x+w-1,z+d-1)){ rMark(x,z,x+w-1,z+d-1); return [x,z]; } } return null; };
    let signEdgeZ=-1;                              // 横長の広告塔が占めている辺（フェンスを立てない）
    /* ⑥ 屋上広告塔：実際の歌舞伎町は屋上に鉄骨の櫓を組んで
       巨大な看板を立てる。上空から見た時の情報量を決める要素。先に置いて占有させる */
    if((style==='zakkyo'||style==='shop'||style==='office') && R()<dense*0.92){
      const nm=(R()<.5)?mainNeon:NEON[(R()*NEON.length)|0];
      const kind=R();
      if(kind<0.45){
        // 縦長の塔：櫓を組んで、その上に細長い看板。看板の直下の両端に投光器（27）
        const tx=RI(rX0,Math.max(rX0,rX1-1)), tz=RI(rZ0,Math.max(rZ0,rZ1-1));
        const th=RI(6,12);
        for(let y=H+1;y<H+th;y++){          // 鉄骨の櫓
          set(tx,y,tz,5); set(tx+1,y,tz,5);
          if(y%3===0){ set(tx,y,tz+1,5); set(tx+1,y,tz+1,5); }
        }
        fill(tx-1,H+th,tz,tx+2,H+th+RI(3,6),tz,nm);
        set(tx-1,H+th-1,tz,27); set(tx+2,H+th-1,tz,27);
        rMark(tx-1,tz,tx+2,tz+1);
      } else if(kind<0.78){
        // 横長の看板：屋上の一辺いっぱいに立てる。前面 1 マス内側に照明バー（27、2 マス間隔）
        const th=RI(4,8), side=(R()<.5), ez=side?rZ0:rZ1, lz=side?rZ0+1:rZ1-1;
        for(let x=rX0;x<=rX1;x+=2)          // 支柱
          for(let y=H+1;y<H+3;y++) set(x,y,ez,5);
        fill(rX0,H+3,ez,rX1,H+3+th,ez,nm);
        for(let x=iX0;x<=iX1;x+=2) set(x,H+1,lz,27);
        rMark(rX0,ez,rX1,ez); rMark(rX0,lz,rX1,lz); signEdgeZ=ez;
      } else {
        // 箱型の広告塔：屋上に立方体を載せ、4面すべてが看板。長辺の外側 1 マスに照明バー
        const bx=RI(rX0,Math.max(rX0,rX1-3)), bz=RI(rZ0,Math.max(rZ0,rZ1-3));
        const bw=Math.min(4,rX1-bx), bd=Math.min(4,rZ1-bz), bh=RI(4,9);
        if(bw>0&&bd>0){
          for(let y=H+1;y<=H+bh;y++)
            for(let z=bz;z<=bz+bd;z++) for(let x=bx;x<=bx+bw;x++){
              const edge=(x===bx||x===bx+bw||z===bz||z===bz+bd);
              if(edge) set(x,y,z, (y===H+1||y===H+bh)?5:nm);
            }
          rMark(bx,bz,bx+bw,bz+bd);
          const lzs=(bw>=bd)?[bz-1,bz+bd+1]:null, lxs=(bw>=bd)?null:[bx-1,bx+bw+1];
          if(lzs){ for(const z of lzs) for(let x=bx;x<=bx+bw;x+=2) if(rFree(x,z,x,z)){ set(x,H+1,z,27); rMark(x,z,x,z); } }
          else   { for(const x of lxs) for(let z=bz;z<=bz+bd;z+=2) if(rFree(x,z,x,z)){ set(x,H+1,z,27); rMark(x,z,x,z); } }
        }
      }
      // 広告塔の脇に赤い航空障害灯（支柱つき）
      if(R()<.35){ const p=rPlace(1,1,4); if(p){ set(p[0],H+1,p[1],5); set(p[0],H+2,p[1],19); } }
    }
    // 塔屋（2×2、扉つき）とダクト（塔屋から屋上の端へ、曲がりを 1 回）
    if(iw>=3&&idp>=3&&R()<.8){
      const p=rPlace(2,2,6);
      if(p){
        const tx=p[0], tz=p[1];
        fill(tx,H+1,tz,tx+1,H+3,tz+1,1);
        set(tx+RI(0,1),H+1,(R()<.5)?tz:tz+1,15);
        if(R()<.55){
          const dx=(tx-iX0<iX1-tx)?-1:1, dz=(tz-iZ0<iZ1-tz)?-1:1;
          let x=(dx<0)?tx-1:tx+2, z=tz+RI(0,1);
          const bend=RI(1,3); let k=0;
          while(rIn(x,z)&&rFree(x,z,x,z)&&k<bend){ set(x,H+1,z,20); rMark(x,z,x,z); x+=dx; k++; }
          x-=dx; z+=dz;
          while(rIn(x,z)&&rFree(x,z,x,z)){ set(x,H+1,z,20); rMark(x,z,x,z); z+=dz; }
        }
      }
    }
    // 架台つき給水塔：鉄骨の脚 4 本×2 段の上に 3×3×2 の給水塔（32：壊すと放水）。入らなければ 2×2 の小型
    { const pw=(style==='office')?.35:((style==='shop')?.45:.55);
      if(R()<pw){
        const p=rPlace(3,3,6);
        if(p){
          const tx=p[0], tz=p[1];
          for(const [ox,oz] of [[0,0],[2,0],[0,2],[2,2]]) fill(tx+ox,H+1,tz+oz,tx+ox,H+2,tz+oz,5);
          fill(tx,H+3,tz,tx+2,H+4,tz+2,32);
        } else {
          const q=rPlace(2,2,4);
          if(q){ const tx=q[0], tz=q[1];
            set(tx,H+1,tz,5); set(tx+1,H+1,tz,5); set(tx,H+1,tz+1,5); set(tx+1,H+1,tz+1,5);
            fill(tx,H+2,tz,tx+1,H+3,tz+1,32); }
        }
      }
    }
    // 室外機の列：一辺に沿って 2 マス間隔で 4〜12 台。余裕があればパラペット側に配管（20）。大きな屋上は 2 辺
    { let rows=0, placed=0;
      const sides=[0,1,2,3]; for(let i=3;i>0;i--){ const j=RI(0,i); const t=sides[i]; sides[i]=sides[j]; sides[j]=t; }
      const want=(iw>=9&&idp>=9&&R()<.6)?2:1;
      for(let si=0;si<4&&rows<want;si++){
        const s=sides[si], ax=(s<2);                           // ax: 列は z 方向に伸びる（x 固定）
        const len=ax?idp:iw, span=ax?iw:idp;
        if(len<4) continue;
        const pipe=(span>=6);
        const e=(s===0||s===2)?(ax?iX0:iZ0):(ax?iX1:iZ1);      // パラペットの内側の列
        const uLine=pipe?((s===0||s===2)?e+1:e-1):e;           // 室外機の列（配管の内側）
        const a0=ax?iZ0:iX0, a1=ax?iZ1:iX1;
        const start=a0+RI(0,1), maxN=Math.min(12,4+RI(0,8));
        const cells=[];
        for(let a=start;a<=a1&&cells.length<maxN;a+=2){
          const x=ax?uLine:a, z=ax?a:uLine;
          if(rFree(x,z,x,z)) cells.push([x,z]);
        }
        if(cells.length<3) continue;
        for(const c of cells){ set(c[0],H+1,c[1],54); rMark(c[0],c[1],c[0],c[1]); }
        if(pipe){
          const f=cells[0], l=cells[cells.length-1];
          const pa0=ax?f[1]:f[0], pa1=ax?l[1]:l[0];
          for(let a=pa0;a<=pa1;a++){ const x=ax?e:a, z=ax?a:e; if(rFree(x,z,x,z)){ set(x,H+1,z,20); rMark(x,z,x,z); } }
        }
        rows++; placed+=cells.length;
      }
      if(!placed){ for(let k=0,n=RI(1,3);k<n;k++){ const p=rPlace(1,1,3); if(p) set(p[0],H+1,p[1],54); } }
    }
    // 太陽光パネル：オフィス・マンションの 35%。幅 4〜8×奥行 2 の板を 1 マス空けて 2〜4 列、後ろの列を 1 段高く
    if((style==='office'||style==='apart')&&iw>=5&&idp>=3&&R()<.35){
      const w=Math.min(iw-1,RI(4,8)), n=RI(2,4);
      const x0=RI(iX0,iX1-w+1); let z=RI(iZ0,Math.max(iZ0,iZ1-3*n+1));
      for(let k=0;k<n&&z+1<=iZ1;k++,z+=3){
        if(!rFree(x0,z,x0+w-1,z+1)) continue;
        fill(x0,H+1,z,x0+w-1,H+1,z+1,53);
        fill(x0,H+2,z+1,x0+w-1,H+2,z+1,53);
        rMark(x0,z,x0+w-1,z+1);
      }
    }
    // 衛星アンテナ（支柱 5 ＋ 皿 22）と、従来の細いアンテナ
    if(R()<.45){ const p=rPlace(1,1,4); if(p){ set(p[0],H+1,p[1],5); set(p[0],H+2,p[1],22); } }
    if(R()<.5){
      const p=rPlace(1,1,3);
      if(p){ const h=RI(3,6); for(let y=H+1;y<=H+h;y++) set(p[0],y,p[1],5); }
    }
    // フェンス：マンション・オフィスはパラペットの上に支柱（2 マス間隔）＋笠木で金網風。横長の広告塔の辺は除く
    if(((style==='apart'&&R()<.6)||(style==='office'&&R()<.45))&&iw>=3&&idp>=3){
      const fs=(x,y,z)=>{ if(!vox[at(x,y,z)]) set(x,y,z,18); };   // 櫓・看板の支柱は上書きしない
      const FZ=(z)=>{ if(z===signEdgeZ) return; for(let x=rX0;x<=rX1;x++){ fs(x,H+3,z); if((x-rX0)%2===0) fs(x,H+2,z); } };
      const FX=(x)=>{ for(let z=rZ0;z<=rZ1;z++){ if(z===signEdgeZ) continue; fs(x,H+3,z); if((z-rZ0)%2===0) fs(x,H+2,z); } };
      FZ(rZ0); FZ(rZ1); FX(rX0); FX(rX1);
    }""")

    # ── 5. 音：室外機は金属、太陽光パネルはガラス ──
    rep("m===27||m===28||m===41) this.glass(x,y,z);", "m===27||m===28||m===41||m===53) this.glass(x,y,z);")
    rep("m===10||m===30||m===32) this.metal(x,y,z);", "m===10||m===30||m===32||m===54) this.metal(x,y,z);")

    # ── 6. 検証フック：屋上設備のボクセル数（53 太陽光・54 室外機・32 給水塔・屋上の 27・屋上の 18） ──
    U("/*@PCDBG*/", "rfCount:()=>{ const c={solar:0,ac:0,water:0,lamp:0,fence:0,blds:0}; for(const b of blds){ if(!b.style||b.style==='pole'||b.style==='car'||b.style==='gate'||b.style==='rail') continue; c.blds++; const v=b.vox, W=b.W, H=b.H; for(let i=0;i<v.length;i++){ const m=v[i]; if(!m) continue; if(m===53) c.solar++; else if(m===54) c.ac++; else if(m===32) c.water++; else if(m===27||m===18){ const y=((i/W)|0)%H; if(y>=8){ if(m===27) c.lamp++; else c.fence++; } } } } return c; }, /*@PCDBG*/")
