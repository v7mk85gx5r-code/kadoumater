# 店先の造り込み（ENV-04）＋自動販売機の造り込み（ENV-08）
#   ENV-04 店先：
#   ・1 階の庇をシャッター素材（灰）から「色テント庇」に：赤（46）・黄（47）・緑（48）・灰（14）をビルごとに選び、
#     先端の 1 列を 1 段垂らして垂れ（valance）を作る。ttSurf に 0.45m ピッチの縞（赤・黄はクリーム色と交互、緑は濃淡）。
#     縞の向きは面の向きで決まるので、X 面の庇は 46、Z 面の庇は 47 を使って「壁に直交する縞」になるようにする。
#   ・1 階の面を「店」単位（幅 4〜6 マス、鉄骨の柱で区切る）で組み直す：開いている店（窓・ネオン）／シャッターの店（28%、
#     そのうち 6 割は最下段だけ店内の灯り 27 が漏れる「半開き」）。シャッター（14）は金属パネルの分岐から外し、
#     ttSurf に 0.11m ピッチの横スラットを描く。
#   ・入口の奥行き：開いている店の中央 1 マスを外周から 1 マス凹ませ（高さ 3 マス）、奥の面に灯り（27 か 3）を置く。
#     greedy の AO で凹みが暗く縁取られる。45% の入口は最上段に暖簾（49：布。紺／えんじ／生成りに紋）。
#   ・のぼり（鉄骨の柱 1 段＋布 3 段）を開いている店の入口脇の歩道（壁から 2 マス）に、積層看板ポール（50：白電照、
#     IS_SIGN なので ttBoard が「階ごとの縦型テナント看板」を描く）を街路側の角の外側 2 マスに高さ 9 マスで立てる。
#     歌舞伎町（MAPID 0）は 7 割で両角。
#   ENV-08 自動販売機：
#   ・素材 19（赤）に 51（白）・52（青）を加え、LIT_MAIN の看板処理の前に自販機の分岐を置く：垂直面の上 53% が商品窓
#     （白い内照に 5 列×2 段のボトルの影）、中段が金属とボタン、下がメーカー色と取出口（高さ 2.8m 未満の面だけ）。
#   ・壁沿いに 1〜4 台（2 台ごとに 1 マス空け、入口の前は避ける）。街角の mkUtility 'vend' は幅 2・高さ 4 の箱から
#     1×2 マスの個体 n 台（色違い）に改める。
#   ・壊れると缶（小さな円筒：赤・銀・緑・青）が 3 個散る（DEB の破片。kick 1.6 倍、短命）。
#   すべてボクセル＋シェーダなので破壊・延焼（BURNM に 46〜49）・看板の照り返し（buildLightMap）に自動で乗る。
#   新素材 ID は 46〜52（他モジュールと重ならない範囲）。
TITLE='店先の造り込み（色テント庇・暖簾・のぼり・看板ポール・スラット入り半開きシャッター・奥行きのある入口）＋自販機'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)

    # ── 1. 素材表：46〜52 ──
    rep("  /*@MATS*/", """  46:{n:'テント庇(赤)', r:.72,g:.16,b:.14, hp:18, sc:1, ld:0.0},
  47:{n:'テント庇(黄)', r:.86,g:.66,b:.12, hp:18, sc:1, ld:0.0},
  48:{n:'テント庇(緑)', r:.14,g:.46,b:.22, hp:18, sc:1, ld:0.0},
  49:{n:'暖簾',         r:.88,g:.84,b:.78, hp:8,  sc:1, ld:0.0},
  50:{n:'看板ポール',   r:.96,g:.95,b:.90, hp:14, sc:3, emis:1, ld:0.0},
  51:{n:'自販機(白)',   r:.92,g:.93,b:.95, hp:20, sc:2, emis:1, ld:0.0},
  52:{n:'自販機(青)',   r:.16,g:.36,b:.78, hp:20, sc:2, emis:1, ld:0.0},
  /*@MATS*/""")

    # ── 2. 素材の種類（発光・看板）・延焼表 ──
    rep("/*@DEFS*/", """/* ══════════ 店先（work/pc/feat/32_storefronts.py）══════════ */
M_CLS[50]=2; M_CLS[51]=2; M_CLS[52]=2;        // 看板ポール・自販機は強い発光（看板と同じ区分）
IS_SIGN[50]=1;                                // 看板ポールは ttBoard が縦型テナント看板を描く（NEON には入れない）
HOOKS.init.push(function(){ BURNM[46]=1; BURNM[47]=1; BURNM[48]=1; BURNM[49]=1; });   // テント・布は燃える
const SF_VEND=[19,51,52];
/*@DEFS*/""")

    # ── 3. シェーダ：自販機の前面（LIT_PRE）、テント庇・布・シャッターのスラット（ttSurf）、自販機の分岐（LIT_MAIN） ──
    rep("/* 素材ごとの表面：コンクリートの型枠むら、タイルの目地、金属パネルの継ぎ目、煉瓦の段。", """/* 自動販売機の前面：高さ 2.8m を、上 53% の商品窓（白い内照に 5 列×2 段のボトルの影）、
   中段の金属とボタン列、下のメーカー色と取出口に分ける。面の向きは問わない（側面にも窓がある機種） */
vec3 ttVendF(vec3 base, vec3 wp, vec3 N, float px){
  float vy=clamp(wp.y/2.8,0.0,1.0);
  float hx=fract((abs(N.x)>0.5?wp.z:wp.x)/1.4);
  float far=smoothstep(0.25,1.0,px);
  vec3 body=base*0.62;
  vec3 col;
  if(vy>0.47){
    float wy=(vy-0.47)/0.53;
    float frame=step(0.07,hx)*step(hx,0.93)*step(0.07,wy)*step(wy,0.90);
    vec2 g=vec2(hx*5.0,wy*2.0), gf=fract(g), gi=floor(g);
    float bottle=1.0-smoothstep(0.24,0.34,length((gf-vec2(0.5,0.45))*vec2(1.0,0.55)));
    vec3 can=ttPal(fract(gi.x*0.37+gi.y*0.61+base.r*0.5))*0.75;
    vec3 win=vec3(1.0,0.98,0.93)*1.45;
    col=mix(win,can,bottle*(1.0-far)*0.9);
    col=mix(body*0.35,col,frame);
  } else if(vy>0.34){
    float bx=fract(hx*5.0+0.5);
    float btn=step(0.3,bx)*step(bx,0.7)*step(0.395,vy)*step(vy,0.435);
    col=vec3(0.16,0.17,0.19)+vec3(0.9,0.55,0.15)*btn*(1.0-far);
  } else {
    float slot=step(0.18,hx)*step(hx,0.82)*step(0.06,vy)*step(vy,0.19);
    col=mix(body,vec3(0.02),slot*(1.0-far));
    col=mix(col,body*1.35,step(0.26,vy)*step(vy,0.33)*0.6);
  }
  return col;
}
/* 素材ごとの表面：コンクリートの型枠むら、タイルの目地、金属パネルの継ぎ目、煉瓦の段。""")
    rep("  bool metal= mid==25.0||mid==5.0||mid==20.0||mid==14.0||mid==15.0||mid==18.0;\n  bool brick= mid==6.0;\n  if(conc){",
        """  bool metal= mid==25.0||mid==5.0||mid==20.0||mid==15.0||mid==18.0;
  bool brick= mid==6.0;
  bool shut= mid==14.0;
  bool tent= mid>45.5&&mid<48.5;
  bool cloth= mid==49.0;
  if(tent){
    // テント庇：0.45m の縞。46 は X 面の庇（縞は z 方向）、47 は Z 面の庇（縞は x 方向）、48 は濃淡の縞
    float sc=(mid==46.0&&vert<0.5)?uv.y:uv.x;
    float s=step(0.5,fract(sc/0.9));
    if(mid==48.0) c=mix(c,c*0.78,s*near);
    else c=mix(c,vec3(0.86,0.83,0.76),s*near*0.92);
    c*=0.94+0.10*ttVN(uv*6.0);                                           // 布の織り
  } else if(cloth){
    // 暖簾・のぼり：柱ごとに紺／えんじ／生成りを選び、紋（丸）と切れ目を入れる
    float h=ttH3(vec3(floor(uv.x/1.4),floor(uv.y/4.2),7.0));
    vec3 dye=h<0.5?vec3(0.14,0.17,0.40):(h<0.75?vec3(0.62,0.12,0.12):vec3(1.0,0.97,0.92));
    vec3 ink=h<0.75?vec3(1.0,0.97,0.92):vec3(0.16,0.14,0.16);
    vec2 lp=fract(uv/1.4);
    float em=1.0-smoothstep(0.22,0.28,length(lp-0.5));
    c*=mix(dye,ink,em*near)*1.15;
    c*=1.0-0.45*(1.0-smoothstep(0.0,0.05,abs(fract(uv.x/0.47)-0.5)))*near;
    c*=0.92+0.14*ttVN(uv*5.0);
  } else if(shut){
    // シャッター：0.11m ピッチの横スラット（遠くでは消える）＋縦の筋むら
    float sl=fract(uv.y/0.11);
    float band=0.84+0.20*smoothstep(0.0,0.5,sl)*(1.0-smoothstep(0.72,1.0,sl));
    c*=mix(1.0,band,near);
    c*=0.92+0.14*ttVN(uv*vec2(2.4,0.3));
  } else if(conc){""")
    rep("""#ifdef USE_UV
    if(ttCls>1.5&&ttVert>0.5) outgoingLight=ttBoard(ttC0,vUv,vWPos,ttN,ttPx,uEmHi);
#endif
    if(ttCls>1.5&&ttVert<0.5) outgoingLight=ttC0*0.08+vec3(0.015);   // 看板の天面・底面は金属""",
        """    float ttMid=floor(vM+0.5); ttMid-=floor(ttMid/64.0+0.001)*64.0;
    bool ttVend=ttCls>1.5&&ttVert>0.5&&abs(vWPos.y)<4.5&&(ttMid==19.0||ttMid==51.0||ttMid==52.0);   // 自販機（地上の面だけ。屋上の障害灯は除く）
    if(ttVend) outgoingLight=ttVendF(ttC0,vLPos,ttN,ttPx);
#ifdef USE_UV
    else if(ttCls>1.5&&ttVert>0.5) outgoingLight=ttBoard(ttC0,vUv,vWPos,ttN,ttPx,uEmHi);
#endif
    if(ttCls>1.5&&ttVert<0.5) outgoingLight=ttC0*0.08+vec3(0.015);   // 看板の天面・底面は金属""")

    # ── 4. 建物生成（mkBuilding）：店の区画 → 1 階の面 → 庇・入口・暖簾・のぼり・看板ポール・自販機 ──
    rep("  const mainNeon=NEON[(R()*NEON.length)|0];   // ビルごとの基調色（1階から使う）",
        """  const mainNeon=NEON[(R()*NEON.length)|0];   // ビルごとの基調色（1階から使う）
  /* ── 店の区画（1 階の面を店ごとに分ける。side 0:-x 1:+x 2:-z 3:+z、al は面に沿った位置） ── */
  const SF={sw:RI(4,6), off:RI(0,3), st:[]};
  const sfStore=(side,al)=>{
    const k=((al+SF.off)/SF.sw)|0, key=side*64+k; let s=SF.st[key];
    if(!s){
      s={shut:R()<.28, half:R()<.6, band:(R()<.62)?mainNeon:((R()<.5)?11:NEON[(R()*NEON.length)|0]),
         neon:(R()<.5)?mainNeon:NEON[(R()*NEON.length)|0], noren:R()<.45, lit:(R()<.6)?27:3,
         ent:k*SF.sw-SF.off+(SF.sw>>1)};
      SF.st[key]=s;
    }
    return s;
  };
  const clr=(x,y,z)=>{ if(!(x>=0&&y>=0&&z>=0&&x<W&&y<HH&&z<D)) return; const i=at(x,y,z); if(vox[i]){ vox[i]=0; hpv[i]=0; live--; } };""")
    rep("""          const cell=((al2+ (y*3))%7);
          if(cell===0) m=5;                            // 店舗を仕切る柱
          else if(y===g1-2) m=(R()<.62)?mainNeon:11;   // 入口上の電飾帯
          else if(R()<.30) m=baseM;                    // 一部はシャッター
          else m=(R()<.55)?3:((R()<.5)?mainNeon:NEON[(R()*NEON.length)|0]);""",
        """          const side=xf2?(x===X0?0:1):(z===Z0?2:3);
          const s=sfStore(side,al2);
          if(((al2+SF.off)%SF.sw)===0) m=5;            // 店舗を仕切る柱（鉛直）
          else if(y===g1-2) m=s.band;                  // 入口上の電飾帯（店ごとの色）
          else if(s.shut) m=(y===0&&s.half)?27:baseM;  // シャッターの店。半開きは最下段から店内の灯りが漏れる
          else if(al2===s.ent&&y<=2) m=(y===2&&s.noren)?49:0;   // 入口（後で 1 マス凹ませる）。最上段は暖簾
          else m=(R()<.55)?3:((R()<.5)?s.neon:NEON[(R()*NEON.length)|0]);""")
    rep("""    const y=g1-1, aw=RI(2,3);
    for(let fi=0;fi<faces.length;fi++){
      const f=faces[fi];
      if(f===0)      fill(fX0-aw,y,fZ0,fX0-1,y,fZ1,14);
      else if(f===1) fill(fX1+1,y,fZ0,fX1+aw,y,fZ1,14);
      else if(f===2) fill(fX0,y,fZ0-aw,fX1,y,fZ0-1,14);
      else           fill(fX0,y,fZ1+1,fX1,y,fZ1+aw,14);
    }
  }""",
        """    const y=g1-1, aw=RI(2,3);
    // 色テント庇：ビルごとに「色（X 面 46／Z 面 47）」「緑 48」「灰 14」。先端の 1 列は 1 段垂らす（垂れ）
    const tc=R(), tentOf=(f)=>tc<.5?(f<2?46:47):(tc<.8?48:14);
    for(let fi=0;fi<faces.length;fi++){
      const f=faces[fi], tm=tentOf(f);
      if(f===0)     { fill(fX0-aw,y,fZ0,fX0-1,y,fZ1,tm); fill(fX0-aw,y-1,fZ0,fX0-aw,y-1,fZ1,tm); }
      else if(f===1){ fill(fX1+1,y,fZ0,fX1+aw,y,fZ1,tm); fill(fX1+aw,y-1,fZ0,fX1+aw,y-1,fZ1,tm); }
      else if(f===2){ fill(fX0,y,fZ0-aw,fX1,y,fZ0-1,tm); fill(fX0,y-1,fZ0-aw,fX1,y-1,fZ0-aw,tm); }
      else          { fill(fX0,y,fZ1+1,fX1,y,fZ1+aw,tm); fill(fX0,y-1,fZ1+aw,fX1,y-1,fZ1+aw,tm); }
    }
    /* ── 入口の奥行き：開いている店の入口を外周から 1 マス凹ませ、奥の面に灯りを置く（全ての面） ── */
    SF.st.forEach((s,key)=>{
      if(s.shut) return;
      const side=(key/64)|0, al=s.ent, len=(side<2)?fd:fw;
      if(al<1||al>len-2) return;
      let x,z,ix,iz;
      if(side===0){ x=fX0; z=fZ0+al; ix=x+1; iz=z; }
      else if(side===1){ x=fX1; z=fZ0+al; ix=x-1; iz=z; }
      else if(side===2){ x=fX0+al; z=fZ0; ix=x; iz=z+1; }
      else { x=fX0+al; z=fZ1; ix=x; iz=z-1; }
      const yT=s.noren?1:2;
      for(let yy=0;yy<=yT;yy++) clr(x,yy,z);
      for(let yy=0;yy<=2;yy++) set(ix,yy,iz,s.lit);
    });
    /* ── 街路側の面：積層看板ポール・のぼり・自販機 ── */
    for(let fi=0;fi<faces.length;fi++){
      const f=faces[fi], len=(f<2)?fd:fw;
      if(len<5) continue;
      const P=(al,out)=> f===0?[fX0-out,fZ0+al] : f===1?[fX1+out,fZ0+al] : f===2?[fX0+al,fZ0-out] : [fX0+al,fZ1+out];
      // 積層看板ポール：角の外側 2 マス、高さ 9 マス（≈12.6m）。歌舞伎町は 7 割で両角
      const corners=(MAPID===0&&R()<.7)?[1,len-2]:[(R()<.5)?1:len-2];
      for(const al of corners){ if(R()<.45+.45*dense){ const p=P(al,2); fill(p[0],0,p[1],p[0],g1+1,p[1],50); } }
      const ents=new Set();
      for(let k=0;k<64;k++){ const s=SF.st[f*64+k]; if(!s) continue;
        if(!s.shut&&s.ent>=1&&s.ent<=len-2) ents.add(s.ent);
        // のぼり：開いている店の入口脇の歩道（壁から 2 マス）。鉄骨の柱 1 段＋布 3 段
        if(!s.shut&&R()<.25+.4*dense){ const al=s.ent+((R()<.5)?-2:2);
          if(al>=3&&al<=len-4){ const p=P(al,2); set(p[0],0,p[1],5); fill(p[0],1,p[1],p[0],3,p[1],49); } }
      }
      // 自動販売機：壁沿いに 1〜4 台（2 台ごとに 1 マス空け）。入口の前は避ける。赤 55%・白 30%・青 15%
      if(R()<.30+.45*dense){
        const n=RI(1,4), a0=RI(1,Math.max(1,len-2-(n+(n>>1))));
        for(let i=0;i<n;i++){ const al=a0+i+(i>>1); if(al>len-2||ents.has(al)) continue;
          const r=R(), p=P(al,1); fill(p[0],0,p[1],p[0],1,p[1],r<.55?19:(r<.85?51:52)); }
      }
    }
  }""")
    # 旧：1 棟 1 台の自販機（上で面ごとに複数台を置くので外す）
    rep("""  if(R()<.42){
    const vx=RI(fX0+1,Math.max(fX0+1,fX1-1)), vz=RI(fZ0+1,Math.max(fZ0+1,fZ1-1));
    if(face===0) fill(fX0-1,0,vz,fX0-1,1,vz,19);
    else if(face===1) fill(fX1+1,0,vz,fX1+1,1,vz,19);
    else if(face===2) fill(vx,0,fZ0-1,vx,1,fZ0-1,19);
    else fill(vx,0,fZ1+1,vx,1,fZ1+1,19);
  }""",
        """  // 自販機は上の「街路側の面」で店ごとに置く（商店・雑居ビル）。他の様式は 1 台
  if(style!=='shop'&&style!=='zakkyo'&&R()<.30){
    const vx=RI(fX0+1,Math.max(fX0+1,fX1-1)), vz=RI(fZ0+1,Math.max(fZ0+1,fZ1-1)), vm=SF_VEND[(R()<.55)?0:((R()<.7)?1:2)];
    if(face===0) fill(fX0-1,0,vz,fX0-1,1,vz,vm);
    else if(face===1) fill(fX1+1,0,vz,fX1+1,1,vz,vm);
    else if(face===2) fill(vx,0,fZ0-1,vx,1,fZ0-1,vm);
    else fill(vx,0,fZ1+1,vx,1,fZ1+1,vm);
  }""")
    # 街角の自販機（mkUtility）：幅 2・高さ 4 の箱 → 1×2 マスの個体 n 台（色違い、隣接）
    rep("""    const n=2+Math.abs(seed|0)%3;
    return mkProp(fx,fz,n*2,5,2,'vend',(set,fill)=>{
      for(let k=0;k<n;k++) fill(k*2,0,0,k*2+1,3,1,19);
    });""",
        """    const n=2+Math.abs(seed|0)%3, sd=Math.abs(seed|0);
    return mkProp(fx,fz,n,3,1,'vend',(set,fill)=>{
      for(let k=0;k<n;k++){ const c=(sd*7+k*13)%20; fill(k,0,0,k,1,0,c<11?19:(c<17?51:52)); }
    });""")

    # ── 5. 壊すと缶が散る ──
    rep("  // 窓ガラスは砕けて、回転しながらきらめく板になる",
        """  // 自販機は缶が散る（地上の自販機だけ。屋上の障害灯も素材 19 なので高さで分ける）
  if(!quiet && (m===19||m===51||m===52) && y<4){
    const px=b.ox+x*VOX+VOX/2, py=y*VOX+VOX/2, pz=b.oz+z*VOX+VOX/2;
    spawnDebris(px,py,pz,M,1.6); spawnDebris(px,py,pz,M,1.3); spawnDebris(px,py,pz,M,1.0);
  }
  // 窓ガラスは砕けて、回転しながらきらめく板になる""")
    rep("  const al=Math.hypot(p.ax,p.ay,p.az)||1; p.ax/=al; p.ay/=al; p.az/=al;",
        """  if(M.n.indexOf('自販機')>=0){                                      // 缶：小さな円筒。赤・銀・緑・青
    p.sx=p.sz=rf(.14,.20); p.sy=rf(.24,.30); p.life=rf(4,7); p.wm=rf(6,16);
    const cc=[[.85,.15,.12],[.74,.76,.80],[.15,.55,.25],[.20,.35,.80]][(Math.random()*4)|0];
    p.r=cc[0]; p.g=cc[1]; p.b=cc[2];
  }
  const al=Math.hypot(p.ax,p.ay,p.az)||1; p.ax/=al; p.ay/=al; p.az/=al;""")
    # 音：自販機・看板ポールはガラス、テント・布は木（鈍い音）
    rep("m===19||m===38||m===39) this.glass(x,y,z);",
        "m===19||m===38||m===39||m===50||m===51||m===52) this.glass(x,y,z);\n      else if(m>=46&&m<=49) this.wood(x,y,z);")

    # ── 6. 検証フック：46〜52 のボクセル数 ──
    U("/*@PCDBG*/", "sfCount:()=>{ const c={}; for(const b of blds){ const v=b.vox; for(let i=0;i<v.length;i++){ const m=v[i]; if(m>=46&&m<=52) c[m]=(c[m]||0)+1; } } return c; }, /*@PCDBG*/")
