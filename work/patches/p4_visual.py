import sys, re; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
# ── 空と霧：光害のドームは残しつつ、暗さと階層を作る ──
p.rep("const SKY_TOP=[0.030,0.036,0.072];", "const SKY_TOP=[0.022,0.028,0.060];")
p.rep("const SKY_MID=[0.150,0.112,0.152];", "const SKY_MID=[0.105,0.082,0.125];")
p.rep("const SKY_HOR=[0.470,0.335,0.245];", "const SKY_HOR=[0.33,0.235,0.175];")
p.rep("const HAZE   =[0.150,0.112,0.112];", "const HAZE   =[0.105,0.080,0.082];")
p.rep("  vec3 sky=mix(uHor,uMid,smoothstep(3.0,20.0,a));\n  sky=mix(sky,uTop,smoothstep(16.0,55.0,a));",
      "  vec3 sky=mix(uHor,uMid,smoothstep(2.0,14.0,a));\n  sky=mix(sky,uTop,smoothstep(12.0,50.0,a));")
# ── ポスト：露出とブルーム（発光体の周辺だけに） ──
p.rep("uThr:{value:1.45},uKnee:{value:0.40}", "uThr:{value:1.38},uKnee:{value:0.36}")
p.rep("POST.mats.comp=fsMat(COMP_FRAG,{tScene:{value:null},tBloom:{value:null},uBloom:{value:0.34},\n      uExposure:{value:1.0},",
      "POST.mats.comp=fsMat(COMP_FRAG,{tScene:{value:null},tBloom:{value:null},uBloom:{value:0.30},\n      uExposure:{value:1.06},")
p.rep("uVig:{value:0.45},uGrain:{value:0.03}", "uVig:{value:0.38},uGrain:{value:0.028}")
# ── 濡れた路面：距離で薄れる（遠景が水面に見えない）／材質ごとの強さ ──
p.rep("const WET_PRE=`uniform sampler2D uRefl; uniform vec2 uScreen; uniform float uWet, uWTime; uniform vec3 uCam;",
      "const WET_PRE=`uniform sampler2D uRefl; uniform vec2 uScreen; uniform float uWet, uWTime, uWetK; uniform vec3 uCam;")
p.rep("  float wet=mix(0.45,1.0,pud)*uWet;", "  float wdist=1.0-smoothstep(150.0,460.0,length(vWPos.xz-uCam.xz));   // 遠くは反射を弱める\n  float wet=mix(0.45,1.0,pud)*uWet*uWetK*wdist;")
p.rep("    for(const k in WET.u) sh.uniforms[k]=WET.u[k];\n    sh.uniforms.uCam=LITU.uCam;",
      "    for(const k in WET.u) sh.uniforms[k]=WET.u[k];\n    sh.uniforms.uWetK={value:(mat.userData&&mat.userData.wetK!==undefined)?mat.userData.wetK:1};\n    sh.uniforms.uCam=LITU.uCam;")
p.rep("  const gm=new THREE.MeshBasicMaterial({color:0x0d1116,fog:true});", "  const gm=new THREE.MeshBasicMaterial({color:0x090b0f,fog:true});\n  gm.userData.wetK=0.45;")
p.rep("    size:26, map:radialTex('255,220,160',false), vertexColors:true,", "    size:15, map:radialTex('255,220,160',false), vertexColors:true,")
# ── 頂点属性 aM（素材＋損傷段階）：面ごとに素材と損傷をシェーダーへ渡す ──
p.rep("let _P=new Float32Array(1<<18), _C=new Float32Array(1<<18),\n    _U=new Float32Array((1<<18)/3*2), _I=new Uint32Array(1<<18);",
      "let _P=new Float32Array(1<<18), _C=new Float32Array(1<<18),\n    _U=new Float32Array((1<<18)/3*2), _I=new Uint32Array(1<<18), _M=new Float32Array((1<<18)/3);")
p.rep("  const nu=new Float32Array(s2/3*2); nu.set(_U); _U=nu;\n  return true;", "  const nu=new Float32Array(s2/3*2); nu.set(_U); _U=nu;\n  const nm=new Float32Array(s2/3); nm.set(_M); _M=nm;\n  return true;")
p.rep("    const base=_pn/3;\n    const x0=px*VOX-cx, y0=py*VOX-cy, z0=pz*VOX-cz;",
      "    const base=_pn/3;\n    _M[base]=_M[base+1]=_M[base+2]=_M[base+3]=m+st*64;   // 素材の種類＋損傷段階×64\n    const x0=px*VOX-cx, y0=py*VOX-cy, z0=pz*VOX-cz;")
p.rep("  geo.setAttribute('uv',new THREE.BufferAttribute(_U.slice(0,_un),2));\n  geo.setIndex(new THREE.BufferAttribute(_I.slice(0,_in),1));",
      "  geo.setAttribute('uv',new THREE.BufferAttribute(_U.slice(0,_un),2));\n  geo.setAttribute('aM',new THREE.BufferAttribute(_M.slice(0,_pn/3),1));\n  geo.setIndex(new THREE.BufferAttribute(_I.slice(0,_in),1));")
p.rep("let rubP=[], rubC=[], rubU=[], rubI=[], rubTris=0, rubMeshes=[], rubT=0;", "let rubP=[], rubC=[], rubU=[], rubM=[], rubI=[], rubTris=0, rubMeshes=[], rubT=0;")
p.rep("  const U=g.attributes.uv?g.attributes.uv.array:null;\n  _rq.set(c.q[0],c.q[1],c.q[2],c.q[3]);",
      "  const U=g.attributes.uv?g.attributes.uv.array:null, Mt=g.attributes.aM?g.attributes.aM.array:null;\n  _rq.set(c.q[0],c.q[1],c.q[2],c.q[3]);")
p.rep("  if(U) for(let i=0;i<U.length;i++) rubU.push(U[i]);\n  else  for(let i=0;i<P.length/3;i++) rubU.push(0,0);",
      "  if(U) for(let i=0;i<U.length;i++) rubU.push(U[i]);\n  else  for(let i=0;i<P.length/3;i++) rubU.push(0,0);\n  if(Mt) for(let i=0;i<Mt.length;i++) rubM.push(Math.min(63,Mt[i]%64)+3*64);   // 瓦礫は最も損傷した段階で描く\n  else  for(let i=0;i<P.length/3;i++) rubM.push(0);")
p.rep("  if(rubMeshes.length>=RUB_MAX_MESH){ rubP=[]; rubC=[]; rubU=[]; rubI=[]; return; }", "  if(rubMeshes.length>=RUB_MAX_MESH){ rubP=[]; rubC=[]; rubU=[]; rubM=[]; rubI=[]; return; }")
p.rep("  g.setAttribute('uv',new THREE.Float32BufferAttribute(rubU,2));\n  g.setIndex(rubI);", "  g.setAttribute('uv',new THREE.Float32BufferAttribute(rubU,2));\n  g.setAttribute('aM',new THREE.Float32BufferAttribute(rubM,1));\n  g.setIndex(rubI);")
p.rep("  scene.add(m); rubMeshes.push(m);\n  rubP=[]; rubC=[]; rubU=[]; rubI=[];", "  scene.add(m); rubMeshes.push(m);\n  rubP=[]; rubC=[]; rubU=[]; rubM=[]; rubI=[];")
p.rep("  rubMeshes=[]; rubP=[]; rubC=[]; rubU=[]; rubI=[]; rubTris=0;", "  rubMeshes=[]; rubP=[]; rubC=[]; rubU=[]; rubM=[]; rubI=[]; rubTris=0;")
# シェーダー：属性→varying、素材ごとの表面と損傷の表現
p.rep("varying vec3 vWPos;\nfloat ttCls=0.0; vec3 ttC0=vec3(1.0); vec3 ttTex=vec3(1.0);", "varying vec3 vWPos; varying float vM;\nfloat ttCls=0.0; vec3 ttC0=vec3(1.0); vec3 ttTex=vec3(1.0);")
p.rep("vec4 ttWB(int idx){ vec4 r=vec4(0.0,0.0,1.0,1.0); for(int i=0;i<46;i++){ if(i==idx) r=uWB[i]; } return r; }",
      "#ifdef TT_GL2\nvec4 ttWB(int idx){ return uWB[clamp(idx,0,45)]; }   // WebGL2 では配列を直接引ける（46回のループが不要）\n#else\nvec4 ttWB(int idx){ vec4 r=vec4(0.0,0.0,1.0,1.0); for(int i=0;i<46;i++){ if(i==idx) r=uWB[i]; } return r; }\n#endif")
p.rep('''  return room;
}
`;
const LIT_COLOR=`''',
'''  return room;
}
/* 素材ごとの表面：コンクリートの型枠むら、タイルの目地、金属パネルの継ぎ目、煉瓦の段。
   損傷段階（aM の上位）に応じてひび割れ・焦げ・骨材の露出を重ねる。遠くでは消してちらつきを防ぐ */
vec3 ttSurf(vec3 c, vec3 wp, vec3 N, float vert, float px){
  float mid=floor(vM+0.5); float st=floor(mid/64.0+0.001); mid-=st*64.0;
  if(mid<0.5) return c;
  vec2 uv = abs(N.x)>0.5 ? wp.zy : (abs(N.z)>0.5 ? wp.xy : wp.xz);
  float far=smoothstep(0.30,1.1,px);
  float near=1.0-far;
  bool conc = mid==1.0||mid==23.0||mid==9.0||mid==10.0||mid==42.0;
  bool tile = mid==12.0||mid==13.0||mid==22.0||mid==24.0;
  bool metal= mid==25.0||mid==5.0||mid==20.0||mid==14.0||mid==15.0||mid==18.0;
  bool brick= mid==6.0;
  if(conc){
    float n=ttVN(uv*0.9)*0.5+ttVN(uv*3.7)*0.3+ttVN(uv*11.0)*0.2;
    c*=0.88+0.22*n;
    float sm=abs(fract(uv.y/2.8)-0.5);                                   // 型枠の継ぎ目
    c*=1.0-0.10*(1.0-smoothstep(0.0,0.03,sm))*near;
  } else if(tile){
    vec2 g=abs(fract(uv/0.7)-0.5);
    float gl=1.0-smoothstep(0.40,0.49,max(g.x,g.y));                     // 目地
    c=mix(c,c*0.80,gl*0.5*near);
    c*=0.94+0.12*ttVN(floor(uv/0.7)*3.1);
  } else if(metal){
    float seam=abs(fract(uv.y/1.4)-0.5);
    c*=1.0-0.16*(1.0-smoothstep(0.0,0.05,seam))*near;
    c*=0.92+0.14*ttVN(uv*vec2(0.25,2.0));
  } else if(brick){
    float row=floor(uv.y/0.35);
    vec2 bq=vec2(uv.x/0.8+0.5*mod(row,2.0),uv.y/0.35);
    vec2 f=abs(fract(bq)-0.5);
    float m=1.0-smoothstep(0.40,0.5,max(f.x*0.6,f.y));
    c=mix(c*0.72+0.03,c,mix(1.0,m,near));
    c*=0.90+0.20*ttVN(floor(bq)*2.3);
  }
  if(st>0.5){
    float cr=ttVN(uv*2.6+st*7.0), cr2=ttVN(uv*7.0-st*3.0);
    float line=1.0-smoothstep(0.010*st,0.035*st,abs(cr-0.5));
    line=max(line,(1.0-smoothstep(0.008*st,0.028*st,abs(cr2-0.5)))*0.6);
    c=mix(c,c*0.22,line*near*min(1.0,st*0.55));                          // ひび割れ
    c*=1.0-0.13*st*ttVN(uv*5.0);                                         // まだらに焦げる
    if(st>2.5) c=mix(c,vec3(0.20,0.185,0.17),0.35*ttVN(uv*1.3));          // 骨材・内部の露出
  }
  return c;
}
`;
const LIT_COLOR=`''')
p.rep("      } else wx*=0.86+0.20*ttVN(vWPos.xz*0.21);\n      alb*=wx;\n    }",
      "      } else wx*=0.86+0.20*ttVN(vWPos.xz*0.21);\n      alb*=wx;\n      alb=ttSurf(alb,vWPos,ttN,ttVert,ttPx);\n    }")
p.rep("    sh.vertexShader='varying vec3 vWPos;\\n'+sh.vertexShader.replace('#include <project_vertex>',\n      '#include <project_vertex>\\n#ifdef USE_INSTANCING\\n  vWPos=(modelMatrix*instanceMatrix*vec4(transformed,1.0)).xyz;\\n#else\\n  vWPos=(modelMatrix*vec4(transformed,1.0)).xyz;\\n#endif');\n    sh.fragmentShader=LIT_PRE+sh.fragmentShader",
      "    sh.vertexShader='attribute float aM; varying float vM; varying vec3 vWPos;\\n'+sh.vertexShader.replace('#include <project_vertex>',\n      '#include <project_vertex>\\n  vM=aM;\\n#ifdef USE_INSTANCING\\n  vWPos=(modelMatrix*instanceMatrix*vec4(transformed,1.0)).xyz;\\n#else\\n  vWPos=(modelMatrix*vec4(transformed,1.0)).xyz;\\n#endif');\n    sh.fragmentShader=((renderer&&renderer.capabilities&&renderer.capabilities.isWebGL2)?'#define TT_GL2\\n':'')+LIT_PRE+sh.fragmentShader")
p.rep("  mat.customProgramCacheKey=()=>'tt_lit_21';", "  mat.customProgramCacheKey=()=>'tt_lit_22';")
# ── 欠けた縁：killVoxel で隣のボクセルにひびを入れる（破断面の周りに損傷の帯） ──
p.rep("  b.vox[i]=0; b.code[i]=0; b.live--; b.dirty=true; b.mdirty=true;\n  markSec(b,y);",
'''  b.vox[i]=0; b.code[i]=0; b.live--; b.dirty=true; b.mdirty=true;
  markSec(b,y);
  { // 欠けた縁：隣のボクセルを損傷段階1まで傷める。穴や切断面の周りに「割れた帯」ができ、素材と壊れ方が読める
    const W=b.W, Hh=b.H, hp=b.hp, vx=b.vox, cd=b.code, WH=W*Hh;
    for(let k=0;k<6;k++){
      let j;
      if(k===0){ if(x===0) continue; j=i-1; } else if(k===1){ if(x===W-1) continue; j=i+1; }
      else if(k===2){ if(y===0) continue; j=i-W; } else if(k===3){ if(y===Hh-1) continue; j=i+W; }
      else if(k===4){ j=i-WH; if(j<0) continue; } else { j=i+WH; if(j>=vx.length) continue; }
      const mm=vx[j]; if(!mm||M_EMIS[mm]) continue;
      const lim=(MATS[mm].hp*0.70)|0;
      if(hp[j]>lim){ hp[j]=lim; const nc=codeOf(mm,lim); if(nc!==cd[j]) cd[j]=nc; }
    }
  }''')
# ── 駐車車両：ボクセルの巨大な車（12マス＝17m）をやめ、走行車と同じ実寸のインスタンスにする ──
p.rep("const TRF_MAX=96;", "const TRF_MAX=240;                 // 走行車＋駐車車両\nlet PARKED=[];                     // 駐車車両（街の生成時に置く。buildTraffic で実体化）\nfunction carXZ(c){ if(c.parked) return [c.x,c.z]; const L=TRF.lanes[c.l]; return [L.ax===2?L.c:c.t, L.ax===2?c.t:L.c]; }\nfunction carAng(c){ if(c.parked) return c.ang; const L=TRF.lanes[c.l]; return L.ax===0?(L.dir>0?0:Math.PI):(L.dir>0?-Math.PI/2:Math.PI/2); }")
p.rep('''      t+=rf(34,90);
    }
  }
}''', '''      t+=rf(34,90);
    }
  }
  for(const q of PARKED){
    if(TRF.cars.length>=TRF_MAX) break;
    const taxi=Math.random()<.12;
    TRF.cars.push({l:-1,parked:true,x:q.x,z:q.z,ang:q.ang,v:0,vmax:0,taxi:taxi,col:taxi?[.07,.09,.17]:CAR_COLS[(Math.random()*CAR_COLS.length)|0]});
  }
}''')
p.rep("  const L=TRF.lanes[c.l];\n  const x=L.ax===2?L.c:c.t, z=L.ax===2?c.t:L.c;\n  c.dead=true;", "  const xz=carXZ(c), x=xz[0], z=xz[1];\n  c.dead=true;")
p.rep("    const L=TRF.lanes[c.l], cx=L.ax===2?L.c:c.t, cz=L.ax===2?c.t:L.c;\n    if((cx-x)*(cx-x)+(cz-z)*(cz-z)+(y*y*.25)<r*r*1.3) wreckCar(c); }",
      "    const xz=carXZ(c), cx=xz[0], cz=xz[1];\n    if((cx-x)*(cx-x)+(cz-z)*(cz-z)+(y*y*.25)<r*r*1.3) wreckCar(c); }")
p.rep("  for(let i=0;i<C.length;i++){ const c=C[i]; if(c.dead) continue;\n    const L=TRF.lanes[c.l];\n    let gap=1e9;",
      "  for(let i=0;i<C.length;i++){ const c=C[i]; if(c.dead||c.parked) continue;\n    const L=TRF.lanes[c.l];\n    let gap=1e9;")
p.rep("    for(let j=0;j<C.length;j++){ if(i===j||C[j].dead||C[j].l!==c.l) continue;", "    for(let j=0;j<C.length;j++){ if(i===j||C[j].dead||C[j].parked||C[j].l!==c.l) continue;")
p.rep("    const L=TRF.lanes[c.l], cx=L.ax===2?L.c:c.t, cz=L.ax===2?c.t:L.c;\n    for(let k=0;k<chunks.length;k++){ const q=chunks[k];",
      "    const xz=carXZ(c), cx=xz[0], cz=xz[1];\n    for(let k=0;k<chunks.length;k++){ const q=chunks[k];")
p.rep("    const c=C[i], L=TRF.lanes[c.l];\n    const x=L.ax===2?L.c:c.t, z=L.ax===2?c.t:L.c;\n    // 車体は x 軸向きに作ってある。進行方向へ回す\n    const ang=L.ax===0?(L.dir>0?0:Math.PI):(L.dir>0?-Math.PI/2:Math.PI/2);",
      "    const c=C[i];\n    const xz=carXZ(c), x=xz[0], z=xz[1];\n    const ang=carAng(c);                                 // 車体は x 軸向きに作ってある。進行方向へ回す")
p.rep("    const brake=c.v<c.vmax*.6;", "    const brake=c.v<c.vmax*.6, prk=!!c.parked;")
p.rep("      if(q[3]){ CL[o*3]=5.0; CL[o*3+1]=4.95; CL[o*3+2]=4.82; }                        // ヘッドライト（強い発光の印）\n      else { const b=brake?1.0:.55; CL[o*3]=4+b; CL[o*3+1]=4+.06*b; CL[o*3+2]=4+.04*b; } }   // テールランプ（減速で明るく）",
      "      if(prk){ CL[o*3]=q[3]?.30:.22; CL[o*3+1]=q[3]?.30:.05; CL[o*3+2]=q[3]?.30:.04; }              // 駐車中は消灯\n      else if(q[3]){ CL[o*3]=5.0; CL[o*3+1]=4.95; CL[o*3+2]=4.82; }                        // ヘッドライト（強い発光の印）\n      else { const b=brake?1.0:.55; CL[o*3]=4+b; CL[o*3+1]=4+.06*b; CL[o*3+2]=4+.04*b; } }   // テールランプ（減速で明るく）")
p.rep("  for(let i=0;i<C.length;i++){ const c=C[i]; if(!c.taxi) continue;\n    const L=TRF.lanes[c.l], x=L.ax===2?L.c:c.t, z=L.ax===2?c.t:L.c;\n    const ang=L.ax===0?(L.dir>0?0:Math.PI):(L.dir>0?-Math.PI/2:Math.PI/2);",
      "  for(let i=0;i<C.length;i++){ const c=C[i]; if(!c.taxi||c.parked) continue;\n    const xz=carXZ(c), x=xz[0], z=xz[1];\n    const ang=carAng(c);")
p.rex(r"function placeCars\(density\)\{.*?\n\}\n",
'''function placeCars(density){
  // 細い通りの路肩に、実寸（全長4.4m）の駐車車両を点々と置く。走行車と同じ描画
  const put=(x,z,ang)=>{ if(PARKED.length<160) PARKED.push({x:x,z:z,ang:ang}); };
  for(let i=0;i<XL.length;i++)
    for(let j=0;j<ZL.length-1;j++){
      if(MAPID===0&&i===2&&j===2) continue;           // 行き止まりの先は建物
      if(XW[i]>=20) continue;                          // 幹線道路は車が走るので駐車しない
      const z0=ZL[j]+ZW[j]/2+8, z1=ZL[j+1]-ZW[j+1]/2-10;
      let z=z0;
      while(z<z1){
        if(Math.random()>density*0.7){ z+=RI2(18,40); continue; }
        const n2=1+((Math.random()*3)|0);
        const side=Math.random()<.5?-1:1;
        for(let q=0;q<n2 && z<z1;q++){ put(XL[i]+side*(XW[i]/2-1.7), z, Math.PI/2*(side<0?1:-1)); z+=rf(5.6,7.2); }
        z+=RI2(10,26);
      }
    }
  for(let j=0;j<ZL.length;j++)
    for(let i=0;i<XL.length-1;i++){
      if(ZW[j]>=20) continue;
      const x0=XL[i]+XW[i]/2+8, x1=XL[i+1]-XW[i+1]/2-10;
      let x=x0;
      while(x<x1){
        if(Math.random()>density*0.64){ x+=RI2(20,44); continue; }
        const n2=1+((Math.random()*3)|0);
        const side=Math.random()<.5?-1:1;
        for(let q=0;q<n2 && x<x1;q++){ put(x, ZL[j]+side*(ZW[j]/2-1.7), side<0?0:Math.PI); x+=rf(5.6,7.2); }
        x+=RI2(12,30);
      }
    }
}
''')
p.rep("  blds=[]; chunks=[]; totalVox=0; killedVox=0; lampPos=[];", "  blds=[]; chunks=[]; totalVox=0; killedVox=0; lampPos=[]; PARKED=[];")
# ── 初期視点：マップごとに「通りの奥行きと象徴的な建物が同時に見える」構図 ──
p.rex(r"function spawnOverview\(\)\{.*?\n\}\n",
'''/* マップごとの初期視点。街路の奥行きとランドマークが同時に入り、最初の標的（手前の建物）も狙いやすい位置 */
const VIEWS=[
  ()=>({x:XL[2]+1.0, y:27, z:ZL[5]+80, yaw:0, pitch:-0.085}),                               // 歌舞伎町：一番街アーチ越しにゴジラロードの奥、東宝ビルと歌舞伎町タワー
  ()=>({x:XL[2]+XW[2]/2+70, y:36, z:ZL[2]+ZW[2]/2+66, yaw:Math.PI*0.74, pitch:-0.17}),       // 渋谷：交差点の南東上空から。QFRONT・109・スクランブルスクエア
  ()=>({x:XL[2]+1.0, y:44, z:ZL[4]+86, yaw:0, pitch:-0.07}),                                 // 西新宿：中央通りの南端から北へ。両側の超高層と都庁
];
function spawnOverview(){
  let v=null;
  try{ v=VIEWS[MAPID](); }catch(e){ v=null; }
  if(!v){
    let x0=1e9,x1=-1e9,z0=1e9,z1=-1e9,top=0;
    for(let k=0;k<blds.length;k++){ const b=blds[k];
      x0=Math.min(x0,b.ox); x1=Math.max(x1,b.ox+b.W*VOX); z0=Math.min(z0,b.oz); z1=Math.max(z1,b.oz+b.D*VOX); top=Math.max(top,b.H*VOX); }
    if(x1<x0){ x0=CITY.x0; x1=CITY.x1; z0=CITY.z0; z1=CITY.z1; top=120; }
    v={x:(x0+x1)/2, y:60, z:z1+120, yaw:0, pitch:-0.3};
  }
  cam.pos.set(v.x, v.y, v.z);
  cam.vel.set(0,0,0);
  cam.yaw=v.yaw; cam.pitch=v.pitch;
  camera.position.copy(cam.pos);
  camera.rotation.set(0,0,0);
  camera.rotateY(cam.yaw); camera.rotateX(cam.pitch);
  shakeAmt=0; kickX=0; kickZ=0; fovOff=0;
}
''')
p.save()
