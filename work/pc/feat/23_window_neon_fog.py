# 窓明かりの時間変化（L03）＋ネオン管のゆらぎ・不良管・停電からの順次復帰（L04）＋地表の高さ霧（L09）
#   L03 窓明かりの時間変化：ttRoom（LIT_PRE）の部屋ごとの乱数 r1/r2/r3 を使い、部屋ごとに 35〜95 秒周期のスケジュールを持たせる。
#       約 14% の部屋がその周期の一部で消灯（1.5 秒のフェード）。8% の部屋はテレビの青白い明滅が奥の壁に映り（消灯中の部屋でも
#       テレビだけ点いている）、約 0.6% は切れかけの蛍光灯が不規則に明滅する。消灯窓（class 4）にも 8% の割合でテレビの淡い青が入る。
#   L04 ネオン管のゆらぎ：LIT_MAIN の発光面（class 2）のうち、ttBoard が看板を描く面（vUv に面の大きさが埋め込まれた面）・自販機・
#       航空障害灯（素材 19）を除いた「管」に、建物ローカル座標 4 ボクセル（5.6m）単位のハッシュで位相を持たせ、8〜13Hz の ±4% のゆらぎと
#       1 割の不良管（不規則に 15% まで落ちる）を入れる。ttBoard は非看板面を base*gain で上書きするので、必ずその後に掛ける。
#       停電（uSignPow）は即時に落ち、復旧は 1.5 秒ほどで管ごとに順に戻る（uSignPow を JS でじわっと戻し、管ごとの閾値で復帰）。
#   L09 地表の高さ霧：密度が高さで指数減衰（尺度 18m）する霞を、建物・車・人（LIT_MAIN）、路面・地面（WET_MAIN）、煙（SMOKE_FRAG）に
#       足す。視線に沿った積分は解析式（exp 2 回と割り算 1 回）、霞の色は光の地図（uLM）を視線の中点で 1 回引いて看板の色に染める。
#       three.js の線形霧（1100〜3400m）はこの後に掛かるので地平線の色は変わらない。核の閃光で霞が白く光る。低画質（低／最低）では切る。
TITLE='窓明かりの時間変化（L03）＋ネオン管のゆらぎ・不良管・停電からの順次復帰（L04）＋地表の高さ霧（L09）'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)

    # ══════════ L09: uniform（LITU・LIT_PRE） ══════════
    rep("  uTop:SKYU.uTop, uMid:SKYU.uMid, uHor:SKYU.uHor, uHaze:SKYU.uHaze,   // ガラスに映す空",
        "  uTop:SKYU.uTop, uMid:SKYU.uMid, uHor:SKYU.uHor, uHaze:SKYU.uHaze,   // ガラスに映す空\n"
        "  uHazeK:{value:1.0}, uFlash:SKYU.uFlash,                 // 地表の高さ霧（L09）の強さ／核の閃光（霞が白く光る）")
    rep("uniform float uStreet, uStreetFall, uSkyAmb, uEmLo, uEmHi;\nvarying vec3 vWPos; varying vec3 vLPos; varying float vM;",
        "uniform float uStreet, uStreetFall, uSkyAmb, uEmLo, uEmHi, uHazeK, uFlash;\nvarying vec3 vWPos; varying vec3 vLPos; varying float vM;")

    # ══════════ L09: 霞の関数（LIT_PRE。ttRoom の直前、uLM/uHaze/uStreetCol の宣言より後） ══════════
    HAZE_FN = r"""/* 地表の高さ霧（L09）：湿った空気に看板の光が散乱し、通りの奥ほど色づいた霞に沈む。
   密度は高さで指数減衰（尺度 18m）、視線に沿った積分は解析式。霞の色は光の地図（看板・窓・街灯の色）を視線の中点で引いて染める。
   反射パス（上下反転）では wp.y が負になるので |y| を使う（鏡像の経路長はそのまま正しい） */
vec3 ttHaze(vec3 col, vec3 wp){
  if(uHazeK<=0.0) return col;
  vec3 dv=wp-uCam; float d=length(dv);
  float yc=max(uCam.y,0.0), yp=abs(wp.y), dy=yp-yc, k=0.055;
  float f=abs(dy)<0.5 ? exp(-k*yc) : (exp(-k*yc)-exp(-k*yp))/(k*dy);
  f=1.0-exp(-0.0026*uHazeK*d*f);
  vec3 mid=uCam+dv*0.5;
  vec4 lm=texture2D(uLM,(mid.xz-uLMo.xy)*uLMo.z);
  vec3 hc=uHaze*1.2+uStreetCol*(uStreet*0.35)+lm.rgb*(0.42*uLMGain*uSignPow)+vec3(1.0,0.9,0.8)*(uFlash*0.6);
  return mix(col,hc,f*0.42);
}
"""
    rep("/* 窓の奥の部屋：窓ごとに奥行きのある箱を想定し、", HAZE_FN+"/* 窓の奥の部屋：窓ごとに奥行きのある箱を想定し、")
    # 建物・車・人：看板の後、three.js の線形霧の前
    rep("  outgoingLight=ttSign(outgoingLight,vWPos,ttN);\n}\n`;",
        "  outgoingLight=ttSign(outgoingLight,vWPos,ttN);\n  outgoingLight=ttHaze(outgoingLight,vWPos);                 // 地表の高さ霧（L09）\n}\n`;")

    # ══════════ L09: 路面・地面（WET） ══════════
    rep("uniform sampler2D uLM; uniform vec4 uLMo; uniform float uLMGain, uSignPow;\nvarying vec3 vWPos;\nfloat wH(vec2 p)",
        "uniform sampler2D uLM; uniform vec4 uLMo; uniform float uLMGain, uSignPow;\n"
        "uniform vec3 uHaze, uStreetCol; uniform float uHazeK, uStreet, uFlash;   // 地表の高さ霧（L09）\n"
        "varying vec3 vWPos;\n"
        "vec3 wHaze(vec3 col, vec3 wp){\n"
        "  if(uHazeK<=0.0) return col;\n"
        "  vec3 dv=wp-uCam; float d=length(dv);\n"
        "  float yc=max(uCam.y,0.0), yp=abs(wp.y), dy=yp-yc, k=0.055;\n"
        "  float f=abs(dy)<0.5 ? exp(-k*yc) : (exp(-k*yc)-exp(-k*yp))/(k*dy);\n"
        "  f=1.0-exp(-0.0026*uHazeK*d*f);\n"
        "  vec3 mid=uCam+dv*0.5;\n"
        "  vec4 lm=texture2D(uLM,(mid.xz-uLMo.xy)*uLMo.z);\n"
        "  vec3 hc=uHaze*1.2+uStreetCol*(uStreet*0.35)+lm.rgb*(0.42*uLMGain*uSignPow)+vec3(1.0,0.9,0.8)*(uFlash*0.6);\n"
        "  return mix(col,hc,f*0.42);\n"
        "}\n"
        "float wH(vec2 p)")
    rep("  outgoingLight=outgoingLight*(1.0-0.45*wet*pud)+rr*(mix(0.20,0.92,F)*wet);\n}\n`;",
        "  outgoingLight=outgoingLight*(1.0-0.45*wet*pud)+rr*(mix(0.20,0.92,F)*wet);\n}\n"
        "outgoingLight=wHaze(outgoingLight,vWPos);                   // 地表の高さ霧（L09）：遠い通りが看板色の霞に沈む\n`;")
    rep("    sh.uniforms.uLM=LITU.uLM; sh.uniforms.uLMo=LITU.uLMo; sh.uniforms.uLMGain=LITU.uLMGain; sh.uniforms.uSignPow=LITU.uSignPow;",
        "    sh.uniforms.uLM=LITU.uLM; sh.uniforms.uLMo=LITU.uLMo; sh.uniforms.uLMGain=LITU.uLMGain; sh.uniforms.uSignPow=LITU.uSignPow;\n"
        "    sh.uniforms.uHazeK=LITU.uHazeK; sh.uniforms.uStreet=LITU.uStreet; sh.uniforms.uStreetCol=LITU.uStreetCol; sh.uniforms.uHaze=LITU.uHaze; sh.uniforms.uFlash=SKYU.uFlash;   // 高さ霧（L09）")

    # ══════════ L09: 煙（SMOKE_FRAG。線形霧の前に掛ける） ══════════
    rep("uniform vec3 uStreetCol, uFogC, uCamP; uniform float uStreet, uStreetFall, uFogN, uFogF;\n",
        "uniform vec3 uStreetCol, uFogC, uCamP; uniform float uStreet, uStreetFall, uFogN, uFogF;\n"
        "uniform vec3 uHaze; uniform float uHazeK, uFlash;   // 地表の高さ霧（L09）\n")
    rep("  float fg=clamp((length(vWp-uCamP)-uFogN)/(uFogF-uFogN),0.0,1.0);\n  col=mix(col,uFogC,fg);",
        "  if(uHazeK>0.0){                                                     // 地表の高さ霧（L09）：建物と同じ式\n"
        "    vec3 hdv=vWp-uCamP; float hd=length(hdv);\n"
        "    float yc=max(uCamP.y,0.0), yp=abs(vWp.y), dy=yp-yc, hk=0.055;\n"
        "    float hf=abs(dy)<0.5 ? exp(-hk*yc) : (exp(-hk*yc)-exp(-hk*yp))/(hk*dy);\n"
        "    hf=1.0-exp(-0.0026*uHazeK*hd*hf);\n"
        "    vec4 hlm=texture2D(uLM,((uCamP+hdv*0.5).xz-uLMo.xy)*uLMo.z);\n"
        "    vec3 hc=uHaze*1.2+uStreetCol*(uStreet*0.35)+hlm.rgb*(0.42*uLMGain*uSignPow)+vec3(1.0,0.9,0.8)*(uFlash*0.6);\n"
        "    col=mix(col,hc,hf*0.42);\n"
        "  }\n"
        "  float fg=clamp((length(vWp-uCamP)-uFogN)/(uFogF-uFogN),0.0,1.0);\n  col=mix(col,uFogC,fg);")
    rep("      uLM:LITU.uLM,uLMo:LITU.uLMo,uLMGain:LITU.uLMGain,uSignPow:LITU.uSignPow},transparent:true,depthWrite:false});",
        "      uLM:LITU.uLM,uLMo:LITU.uLMo,uLMGain:LITU.uLMGain,uSignPow:LITU.uSignPow,\n"
        "      uHazeK:LITU.uHazeK,uHaze:LITU.uHaze,uFlash:SKYU.uFlash},transparent:true,depthWrite:false});")

    # ══════════ L09: 画質段階（最高・高 1.0／中 0.7／低・最低 0） ══════════
    rep("  POST.aoOn=!!Q.ao && aoUser; POST.streakOn=!!Q.streak;",
        "  POST.aoOn=!!Q.ao && aoUser; POST.streakOn=!!Q.streak;\n"
        "  LITU.uHazeK.value=[1.0,1.0,0.7,0.0,0.0][L];                // 地表の高さ霧（L09）：低画質では切る")

    # ══════════ L03: 部屋ごとのスケジュール・テレビ・切れかけの蛍光灯（ttRoom） ══════════
    rep("  vec3 room=col*sh*(0.72+0.60*r2)*mix(1.0,0.05,dark);",
        "  // 時間変化（L03）：部屋ごとに 35〜95 秒の周期を持ち、その周期の一部（14%）で消灯する（端で 1.5 秒ほどフェード）。\n"
        "  // 8% の部屋はテレビの青白い明滅が奥の壁に映る（消灯中の部屋でもテレビだけ点いている）。約 0.6% は切れかけの蛍光灯\n"
        "  float per=35.0+60.0*r2, tph=uTime/per+r1*7.0, slot=floor(tph), ph=fract(tph), fe=1.5/per;\n"
        "  float offK=step(0.86,ttH3(vec3(rid,slot*0.37+sd)))*smoothstep(0.0,fe,ph)*smoothstep(1.0,1.0-fe,ph);\n"
        "  dark=max(dark,offK);\n"
        "  float tv=step(0.62,r3)*step(r3,0.70);\n"
        "  vec3 tvc=vec3(0.45,0.60,1.0)*((0.55+0.45*ttBN(vec2(uTime*3.3+r1*40.0,uTime*0.7)))*tv*mix(1.0,0.30,dark));\n"
        "  float flk=(r2>0.60&&ttH3(vec3(rid,sd+9.0))>0.985)?mix(0.35,1.0,step(0.30,fract(sin(floor(uTime*11.0)+r1*77.0)*43758.5453))):1.0;\n"
        "  vec3 room=(col*sh*(0.72+0.60*r2)*mix(1.0,0.45,tv)*mix(1.0,0.05,dark)+tvc*(t==tZ?0.9:0.30))*flk;")
    rep("    room=vec3(0.86,0.83,0.77)*(0.80+0.20*step(0.5,fract(wy*11.0)))*(0.85+0.30*r1)*mix(1.0,0.05,dark);",
        "    room=(vec3(0.86,0.83,0.77)*(0.80+0.20*step(0.5,fract(wy*11.0)))*(0.85+0.30*r1)*mix(1.0,0.45,tv)*mix(1.0,0.05,dark)+tvc*0.30)*flk;   // ブラインド越しも同じ時間変化")

    # ══════════ L04: ネオン管のゆらぎ・不良管・停電からの順次復帰（LIT_MAIN。ttBoard／自販機の上書きの後） ══════════
    rep("    if(ttCls>1.5&&ttVert<0.5) outgoingLight=ttC0*0.08+vec3(0.015);   // 看板の天面・底面は金属",
        "    if(ttCls>1.5&&ttVert<0.5) outgoingLight=ttC0*0.08+vec3(0.015);   // 看板の天面・底面は金属\n"
        "    if(ttCls>1.5&&ttCls<2.5&&ttVert>0.5&&!ttVend&&ttMid!=19.0){        // ネオン管のゆらぎ・不良管（L04）\n"
        "      float ttSg=0.0;\n"
        "#ifdef USE_UV\n"
        "      ttSg=step(0.5,floor(vUv.x/1000.0+0.0001));                        // 看板の面（ttBoard が描く）は除く\n"
        "#endif\n"
        "      if(ttSg<0.5){\n"
        "        float hq=ttH3(floor(vLPos*0.17857)+vec3(0.37));                  // 4 ボクセル（5.6m）単位の「管」ごとの位相\n"
        "        float fl=0.96+0.04*sin(uTime*(8.0+hq*5.0)+hq*6.2832);           // 8〜13Hz の微小なゆらぎ（±4%）\n"
        "        if(hq>0.90){ float g=fract(sin(floor(uTime*9.0+hq*70.0)*12.9898)*43758.5453); fl*=mix(0.15,1.0,step(0.42,g)); }   // 1 割の不良管\n"
        "        fl*=smoothstep(hq*0.7,hq*0.7+0.3,uSignPow);                       // 停電から戻るときは管ごとに順に点く\n"
        "        outgoingLight*=fl;\n"
        "      }\n"
        "    }")
    # 停電：即時に落ち、復旧は 1.5 秒ほどでじわっと戻る（ネオン管はシェーダ側で管ごとに順に）
    rep("  LITU.uSignPow.value=blackout?0:1;                        // 停電で消える",
        "  if(blackout) LITU.uSignPow.value=0;                     // 停電で即消える\n"
        "  else { const sp=LITU.uSignPow.value+(1-LITU.uSignPow.value)*Math.min(1,dt*1.8); LITU.uSignPow.value=sp>0.999?1:sp; }   // 復旧は 1.5 秒ほどでじわっと（L04）")

    # ══════════ 検証フック ══════════
    U("/*@PCDBG*/",
      "wnf:()=>({haze:LITU.uHazeK.value, signPow:LITU.uSignPow.value, flash:SKYU.uFlash.value, uTime:LITU.uTime.value,\n"
      "    lit:LIT_PRE.includes('ttHaze(')&&LIT_MAIN.includes('ttHaze(')&&LIT_MAIN.includes('不良管')&&LIT_PRE.includes('tvc'),\n"
      "    wet:WET_MAIN.includes('wHaze('), smoke:SMOKE_FRAG.includes('uHazeK'), key:LIT_PRE.length+'_'+LIT_MAIN.length+'_'+WET_MAIN.length}),\n"
      "  wnfHaze:(v)=>{ LITU.uHazeK.value=+v; return LITU.uHazeK.value; }, /*@PCDBG*/")
