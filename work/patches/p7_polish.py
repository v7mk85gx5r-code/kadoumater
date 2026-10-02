import sys, re; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
# 1. 処理の時間予算：剥離・メッシュ生成はセル数に加えて実行時間でも打ち切る（大きな建物でも1フレームを独占しない）
p.rep("function processDetach(){\n  // 支持判定とメッシュ再生成で別々に予算を持つ（再生成の方が重いので1棟/フレーム）\n  let bfsDone=0, meshDone=0;\n  const bfsLim = chunks.length>40 ? 1 : 2;\n  for(let k=0;k<blds.length;k++){\n    const b=blds[k];\n    if(!b.dirty && !b.mdirty) continue;",
      "function processDetach(){\n  // 支持判定とメッシュ再生成で別々に予算を持つ（再生成の方が重いので1棟/フレーム）。加えて実行時間でも打ち切る\n  let bfsDone=0, meshDone=0;\n  const bfsLim = chunks.length>40 ? 1 : 2;\n  const _t0=_now(), TB=QUAL.level>=2?5:7;\n  for(let k=0;k<blds.length;k++){\n    const b=blds[k];\n    if(!b.dirty && !b.mdirty) continue;\n    if(_now()-_t0>TB && (bfsDone||meshDone)) break;     // 時間切れ：残りは次フレームへ（最低1件は進める）")
p.rep("    stepChunk(c,dt);\n    if(meshBudget>0){\n      if(c.split){ splitChunk(c); meshBudget--; }\n      else if(c.dirty){ chunkRemesh(c); meshBudget--; }\n    }",
      "    stepChunk(c,dt);\n    if(meshBudget>0 && (_now()-_a)<9){\n      if(c.split){ splitChunk(c); meshBudget--; }\n      else if(c.dirty){ chunkRemesh(c); meshBudget--; }\n    }")
# 2. 光の地図：壊れた看板・窓の光が地面に残り続けないよう、破壊が進んだら作り直す（最大2.5秒に1回）
p.rep("let cullT=0;\nfunction updCull(dt){", "let lmT2=0, lmKilled=0;\nfunction updLightMap(dt){\n  lmT2-=dt; if(lmT2>0) return;\n  lmT2=2.5;\n  if(killedVox-lmKilled<1200) return;\n  lmKilled=killedVox;\n  buildLightMap();\n}\nlet cullT=0;\nfunction updCull(dt){")
p.rep("  const _q5=_now(); updCull(dt);        PROF.pCull=_now()-_q5;", "  const _q5=_now(); updCull(dt); updLightMap(dt);        PROF.pCull=_now()-_q5;")
p.rep("  blds=[]; chunks=[]; totalVox=0; killedVox=0; lampPos=[]; PARKED=[];", "  blds=[]; chunks=[]; totalVox=0; killedVox=0; lampPos=[]; PARKED=[]; lmKilled=0; lmT2=0;")
# 3. 模様は局所座標、照明はワールド座標：動く塊の窓・材質模様が表面を滑らない
p.rep("varying vec3 vWPos; varying float vM;\nfloat ttCls=0.0;", "varying vec3 vWPos; varying vec3 vLPos; varying float vM;\nfloat ttCls=0.0;")
p.rep("    sh.vertexShader='attribute float aM; varying float vM; varying vec3 vWPos;\\n'+sh.vertexShader.replace('#include <project_vertex>',\n      '#include <project_vertex>\\n  vM=aM;\\n#ifdef USE_INSTANCING\\n  vWPos=(modelMatrix*instanceMatrix*vec4(transformed,1.0)).xyz;\\n#else\\n  vWPos=(modelMatrix*vec4(transformed,1.0)).xyz;\\n#endif');",
      "    sh.vertexShader='attribute float aM; varying float vM; varying vec3 vWPos; varying vec3 vLPos;\\n'+sh.vertexShader.replace('#include <project_vertex>',\n      '#include <project_vertex>\\n  vM=aM;\\n#ifdef USE_INSTANCING\\n  vWPos=(modelMatrix*instanceMatrix*vec4(transformed,1.0)).xyz; vLPos=vWPos;\\n#else\\n  vWPos=(modelMatrix*vec4(transformed,1.0)).xyz; vLPos=transformed.xyz;\\n#endif');")
p.rep("    vec3 room=ttRoom(vWPos,ttN,ttRd,0.0)*ttC0;", "    vec3 room=ttRoom(vLPos,ttN,ttRd,0.0)*ttC0;")
p.rep("      vec3 room=ttRoom(vWPos,ttN,ttRd,1.0)*0.9;", "      vec3 room=ttRoom(vLPos,ttN,ttRd,1.0)*0.9;")
p.rep("      float fu=abs(ttN.x)>0.5?vWPos.z:vWPos.x;\n      float wx=0.92+0.16*ttVN(vWPos.xz*0.013+vec2(vWPos.y*0.011));\n      if(ttVert>0.5){\n        wx*=1.0-0.20*smoothstep(0.52,0.86,ttVN(vec2(fu*0.85,vWPos.y*0.055)));",
      "      float fu=abs(ttN.x)>0.5?vLPos.z:vLPos.x;\n      float wx=0.92+0.16*ttVN(vLPos.xz*0.013+vec2(vLPos.y*0.011));\n      if(ttVert>0.5){\n        wx*=1.0-0.20*smoothstep(0.52,0.86,ttVN(vec2(fu*0.85,vLPos.y*0.055)));")
p.rep("      } else wx*=0.86+0.20*ttVN(vWPos.xz*0.21);\n      alb*=wx;\n      alb=ttSurf(alb,vWPos,ttN,ttVert,ttPx);",
      "      } else wx*=0.86+0.20*ttVN(vLPos.xz*0.21);\n      alb*=wx;\n      alb=ttSurf(alb,vLPos,ttN,ttVert,ttPx);")
p.rep("  mat.customProgramCacheKey=()=>'tt_lit_22';", "  mat.customProgramCacheKey=()=>'tt_lit_23';")
# 4. 倒壊・大破した建物の壁面看板（シェーダー描画）は消す：文字だけが元の場所に浮かない
p.rep("    const dmg=G2.b&&G2.b.init?Math.max(0,1-G2.b.live/G2.b.init):0;\n    LITU.uSgO.value[i].set(G2.o[0],G2.o[1],G2.o[2],G2.w);",
      "    const dmg=G2.b&&G2.b.init?Math.max(0,1-G2.b.live/G2.b.init):0;\n    const gone=G2.b&&(G2.b.toppled||G2.b.toppling||dmg>0.45);          // 倒れた・大破した壁の看板は描かない\n    LITU.uSgO.value[i].set(G2.o[0],G2.o[1],G2.o[2],gone?0:G2.w);")
p.save()
