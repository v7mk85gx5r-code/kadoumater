import sys; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
# ── A. HP arrays → Uint16 (620/260 が 8bit で丸まる不整合を解消) ──
p.rep(', hpv=new Uint8Array(', ', hpv=new Uint16Array(', 7)
p.rep('const nv=new Uint8Array(nW*nH*nD), nh=new Uint8Array(nW*nH*nD);',
      'const nv=new Uint8Array(nW*nH*nD), nh=new Uint16Array(nW*nH*nD);')
# ── G. 区画境界の面も再生成する ──
p.rep('const SECH=34;                              // メッシュを分ける高さ（ボクセル）\n',
'''const SECH=34;                              // メッシュを分ける高さ（ボクセル）
/* ボクセルの変化を区画に伝える。境界の行では隣の区画が持つ面（天面・AO）も変わるので一緒に落とす */
function markSec(b,y){
  if(!b.sec) return;
  const si=(y/SECH)|0, s=b.sec[si];
  if(!s) return;
  s.dirty=true;
  if(si>0 && y===s.y0) b.sec[si-1].dirty=true;
  if(si<b.sec.length-1 && y===s.y1-1) b.sec[si+1].dirty=true;
}
''')
p.rep('if(b.sec){ const si=(y/SECH)|0; if(b.sec[si]) b.sec[si].dirty=true; }', 'markSec(b,y);', 4)
# ── B. spawnChunk の契約：移したボクセル数を _spawnMoved に積む ──
p.rep('let spawnBudget=0, geoBudget=90000, scanBudget=140000;',
      'let spawnBudget=0, geoBudget=90000, scanBudget=140000;\nlet _spawnMoved=0;                 // 直近の spawnChunk 呼び出し（再帰分割を含む）で建物から移したボクセル数')
p.rep('''    vox[j]=b.vox[i]; hpv[j]=b.hp[i];
    b.vox[i]=0; b.code[i]=0; b.live--;
    markSec(b,y);
  }
  b.dirty=true; b.mdirty=true;''',
'''    vox[j]=b.vox[i]; hpv[j]=b.hp[i];
    b.vox[i]=0; b.code[i]=0; b.live--;
    markSec(b,y);
  }
  _spawnMoved+=n;
  b.dirty=true; b.mdirty=true;''')
p.rep('''  const geo=buildGeo(code,W,H,D,true,tint);
  if(!geo){ return null; }
  let live=0; for(let i=0;i<vox.length;i++) if(vox[i]) live++;''',
'''  const geo=buildGeo(code,W,H,D,true,tint);
  if(!geo){ pulverizeArr(vox); return null; }       // 面が作れない＝消えたものとして必ず集計する
  let live=0; for(let i=0;i<vox.length;i++) if(vox[i]) live++;''')
# ── B. 特異点：予算条件（geoBudget>60000 は初期値50000で到達不能）と二重減算を修正 ──
p.rex(r'    // 2フレームに1棟ずつ地面から引き剥がす.*?    PROF\.gTear=_now\(\)-_gA;\n',
'''    // 一定時間ごとに1棟ずつ地面から引き剥がす＝順に浮き上がって吸い込まれていく
    // （1棟を丸ごと剥がすとメッシュ生成が集中するので、間隔を空けて予算にも従わせる）
    A.tearT=(A.tearT||0)+dt;
    const _gA=_now();
    if(A.tearT>=0.09 && A.qi<A.q.length && geoBudget>0 && scanBudget>0 && spawnBudget>0 && chunks.length<MAXCHUNK-4){
      const b=A.q[A.qi].b;
      if(b.live>2){
        const list=[];
        for(let i=0;i<b.vox.length;i++) if(b.vox[i]) list.push(i);
        b.lastSrc='wpn';                          // 特異点が引き剥がした分は兵装の直撃扱い
        _spawnMoved=0;
        spawnChunk(b, list, 0, 8, 0);             // ボクセルの移動と live の減算は spawnChunk の中で1回だけ行う
        if(_spawnMoved>0){                        // 塊にできた（巨大塊は内部で分割される）
          A.tearT=0; A.qi++;
          leanHint=null;
          b.dirty=true; b.mdirty=true;
          dustAt(b.ox+b.W*VOX/2,5,b.oz+b.D*VOX/2,6,1.6);
          Snd.crumble(.3);
        }                                         // 作れなかった（予算切れ）時は次フレームに再挑戦
      } else { A.qi++; }
    }
    PROF.gTear=_now()-_gA;
''')
# ── G. 資源の所有権：路面テクスチャ・共有マテリアルの解放／再利用 ──
p.rep('if(roadMesh){ scene.remove(roadMesh); roadMesh.geometry.dispose(); roadMesh.material.dispose(); }',
      'if(roadMesh){ scene.remove(roadMesh); roadMesh.geometry.dispose(); if(roadMesh.material.map) roadMesh.material.map.dispose(); roadMesh.material.dispose(); roadMesh=null; }')
p.rep('let glowFloor=null;\nfunction buildGlowFloor(){',
      'let glowFloor=null, glowMat=null;\nfunction buildGlowFloor(){')
p.rep('''  glowFloor=new THREE.Mesh(g,new THREE.MeshBasicMaterial({
    map:radialTex('255,255,255',true), vertexColors:true, transparent:true,
    blending:THREE.AdditiveBlending, depthWrite:false, fog:true}));''',
'''  if(!glowMat) glowMat=new THREE.MeshBasicMaterial({
    map:radialTex('255,255,255',true), vertexColors:true, transparent:true,
    blending:THREE.AdditiveBlending, depthWrite:false, fog:true});
  glowFloor=new THREE.Mesh(g,glowMat);''')
p.rep("let haloObj=null, haloGeo=null, haloCol=null, haloSize=null, halos=[], haloOfBld={};",
      "let haloObj=null, haloGeo=null, haloCol=null, haloSize=null, halos=[], haloOfBld={}, haloMat=null;")
p.rep("  haloObj=new THREE.Points(haloGeo,ptsMaterial(radialTex('255,255,255',true),THREE.AdditiveBlending));",
      "  if(!haloMat) haloMat=ptsMaterial(radialTex('255,255,255',true),THREE.AdditiveBlending);\n  haloObj=new THREE.Points(haloGeo,haloMat);")
p.rep('''  lampObj=new THREE.Points(g,new THREE.PointsMaterial({
    size:26, map:radialTex('255,220,160',false), vertexColors:true,
    transparent:true, depthWrite:false, blending:THREE.AdditiveBlending,
    sizeAttenuation:true, fog:true}));''',
'''  if(!lampMat) lampMat=new THREE.PointsMaterial({
    size:26, map:radialTex('255,220,160',false), vertexColors:true,
    transparent:true, depthWrite:false, blending:THREE.AdditiveBlending,
    sizeAttenuation:true, fog:true});
  lampObj=new THREE.Points(g,lampMat);''')
p.rep("let lampPos=[], lampObj=null, roadMesh=null;", "let lampPos=[], lampObj=null, lampMat=null, roadMesh=null;")
# ── resetWorld：塊の配列を走査中に splice していた（半分が残り、シーンに漏れる）／プールの解放漏れ ──
p.rep('''function resetWorld(){
  for(const b of blds) disposeBld(b);
  for(const c of chunks) removeChunk(c,true);''',
'''let cityGen=0;                     // 街の世代。再生成をまたいだ遅延処理を無効にする
function resetWorld(){
  cityGen++;
  for(const b of blds) disposeBld(b);
  for(const c of chunks.slice()) removeChunk(c,true);
  // 飛翔中の弾体・隕石・核が握っているプールを返す
  const freeMp=(mp)=>{ if(!mp) return; mp.busy=false; if(mp.o) mp.o.visible=false;
    if(mp.head) mp.head.visible=false; if(mp.flame){ mp.flame.visible=false; mp.fmat.opacity=0; }
    if(mp.rock){ mp.rock.visible=false; mp.glow.visible=false; mp.tail.visible=false; mp.gm.opacity=0; mp.tm.opacity=0; } };
  for(const m of missiles) freeMp(m.mp);
  if(nukePend) freeMp(nukePend.mp);
  nukePend=null; orbitFx=null; railOn=false; railBeam=null; beamFx=[];
  for(const a of efxA){ a.e.busy=false; a.e.o.visible=false; a.e.mat.opacity=0; } efxA=[];
  for(const e of shells){ e.s.busy=false; e.s.o.visible=false; e.s.mat.opacity=0; } shells=[];
  if(cutMesh){ cutMesh.visible=false; } cutT=0;
  if(orbCore) orbVisible(false);
  if(gravCore){ gravCore.visible=false; gravRing.visible=false; }''')
# ── F. 核・破壊球のゼロ加点を迂回する経路を塞ぐ ──
p.rep('function wreckCar(c){', 'function wreckCar(c,src){\n  src=src||KSRC;')
p.rep("  if(fires.length<30) fires.push({x:x,y:1.5,z:z,t:5+Math.random()*4,r:5});\n  addLight(x,3,z,30,[1,.6,.3],1.4,.3);\n  S.score+=2500;",
      "  if(fires.length<30) fires.push({x:x,y:1.5,z:z,t:5+Math.random()*4,r:5,src:(src==='nuke'?'nuke':'fire')});\n  addLight(x,3,z,30,[1,.6,.3],1.4,.3);\n  if((SRCMUL[src]||0)>0) S.score+=Math.round(2500*S.combo);   // 核・破壊球に巻き込まれた車は加点しない")
p.rep("      if(q.p[1]<14&&Math.abs(q.p[0]-cx)<6&&Math.abs(q.p[2]-cz)<6){ wreckCar(c); break; } } }",
      "      if(q.p[1]<14&&Math.abs(q.p[0]-cx)<6&&Math.abs(q.p[2]-cz)<6){ wreckCar(c, q.src==='nuke'?'nuke':'domino'); break; } } }")
p.rep("    S.score+=Math.round(L.init*40);          // ランドマーク1棟ぶんの巻き込み相当（ポップで加算が見える）",
      "    { let nk=0; for(const k of L.ids) if(blds[k].lastSrc==='nuke') nk++;\n      if(nk*2<=L.ids.length) S.score+=Math.round(L.init*40);   // ランドマーク1棟ぶんの巻き込み相当。核・破壊球で落とした時は加点しない\n      else L.nuked=true; }")
p.rep("    fires.push({x:px, y:Math.max(1.5,py), z:pz, t:rf(12,20), r:rf(8,12)});",
      "    fires.push({x:px, y:Math.max(1.5,py), z:pz, t:rf(12,20), r:rf(8,12), src:(KSRC==='nuke'?'nuke':'fire')});")
p.rep("      blasts.push({x:px,y:py,z:pz,t:.05+Math.random()*.35,r:M.boom,p:M.bp});",
      "      blasts.push({x:px,y:py,z:pz,t:.05+Math.random()*.35,r:M.boom,p:M.bp,src:(KSRC==='nuke'?'nuke':'chain')});")
p.rep("      fires.push({x:px, y:Math.max(1.5,py), z:pz,\n                  t:9+Math.random()*10, r:7+Math.random()*7});",
      "      fires.push({x:px, y:Math.max(1.5,py), z:pz,\n                  t:9+Math.random()*10, r:7+Math.random()*7, src:(KSRC==='nuke'?'nuke':'fire')});")
p.rep("      gasLeaks.push({x:px, y:py, z:pz, t:.9+Math.random()*1.6});",
      "      gasLeaks.push({x:px, y:py, z:pz, t:.9+Math.random()*1.6, src:(KSRC==='nuke'?'nuke':'chain')});")
p.rep("  fires.push({x:px, y:py, z:pz, t: wood?rf(14,22):rf(6,11), r: wood?rf(9,14):rf(5,9), bid:h.b.id});",
      "  fires.push({x:px, y:py, z:pz, t: wood?rf(14,22):rf(6,11), r: wood?rf(9,14):rf(5,9), bid:h.b.id, src:f.src});")
p.rep("  fires.push({x:fx0, y:2+Math.random()*10, z:fz0, t:6+Math.random()*8, r:8+Math.random()*14});",
      "  fires.push({x:fx0, y:2+Math.random()*10, z:fz0, t:6+Math.random()*8, r:8+Math.random()*14, src:(b.lastSrc==='nuke'?'nuke':'fire')});")
p.rep("      fires.push({x:g.x, y:Math.max(1.5,g.y), z:g.z, t:8+Math.random()*8, r:9+Math.random()*8});",
      "      fires.push({x:g.x, y:Math.max(1.5,g.y), z:g.z, t:8+Math.random()*8, r:9+Math.random()*8, src:(g.src==='nuke'?'nuke':'fire')});")
p.rep("    KSRC='chain'; damageSphere(g.x, g.y, g.z, 9, 70); KSRC='wpn';",
      "    KSRC=g.src||'chain'; damageSphere(g.x, g.y, g.z, 9, 70); KSRC='wpn';")
p.rep("  if(rad>70) fires.push({x:x,y:Math.max(1,y-rad*.3),z:z,t:2.4+Math.random()*2.2,r:rad*.45});",
      "  if(rad>70) fires.push({x:x,y:Math.max(1,y-rad*.3),z:z,t:2.4+Math.random()*2.2,r:rad*.45,src:(KSRC==='nuke'?'nuke':'fire')});")
p.rep("        fires.push({x:N.x+Math.cos(a2)*r2, y:2, z:N.z+Math.sin(a2)*r2,\n                    t:12+Math.random()*10, r:40+Math.random()*30});",
      "        fires.push({x:N.x+Math.cos(a2)*r2, y:2, z:N.z+Math.sin(a2)*r2,\n                    t:12+Math.random()*10, r:40+Math.random()*30, src:'nuke'});")
p.rep("      KSRC='fire';\n      const n=burnAt(f.x, f.y+rf(0,5), f.z, f.r*.6, 55);",
      "      KSRC=f.src||'fire';\n      const n=burnAt(f.x, f.y+rf(0,5), f.z, f.r*.6, 55);")
p.rep("    if(b.t<=0){ blasts.splice(i,1); KSRC=b.w?'wpn':'chain'; detonate(b.x,b.y,b.z,b.r,b.p); KSRC='wpn'; }",
      "    if(b.t<=0){ blasts.splice(i,1); KSRC=b.w?'wpn':(b.src||'chain'); detonate(b.x,b.y,b.z,b.r,b.p); KSRC='wpn'; }")
# 火災旋風：核起因の火が多数なら旋風の被害も核扱い
p.rep('''    let n=0, sx=0, sz=0;
    for(let j=0;j<fires.length;j++){
      const b=fires[j];
      if(Math.hypot(b.x-a.x, b.z-a.z)>110) continue;
      n++; sx+=b.x; sz+=b.z;
    }''',
'''    let n=0, sx=0, sz=0, nk=0;
    for(let j=0;j<fires.length;j++){
      const b=fires[j];
      if(Math.hypot(b.x-a.x, b.z-a.z)>110) continue;
      n++; sx+=b.x; sz+=b.z; if(b.src==='nuke') nk++;
    }''')
p.rep("    storms.push({x:cx, z:cz, t:0, life:16+Math.random()*10, r:26, spin:Math.random()<.5?-1:1});",
      "    storms.push({x:cx, z:cz, t:0, life:16+Math.random()*10, r:26, spin:Math.random()<.5?-1:1, src:(nk*2>n?'nuke':'fire')});")
p.rep("    if(Math.random()<.3){ KSRC='fire'; damageSphere(S2.x, 8+Math.random()*40, S2.z, S2.r*0.5, 60); KSRC='wpn'; }",
      "    if(Math.random()<.3){ KSRC=S2.src||'fire'; damageSphere(S2.x, 8+Math.random()*40, S2.z, S2.r*0.5, 60); KSRC='wpn'; }")
p.rep("      if(c.src!=='nuke') c.src='fire';          // 旋風が投げた瓦礫の被害は「延焼」扱い",
      "      if(c.src!=='nuke') c.src=(S2.src==='nuke'?'nuke':'fire');          // 旋風が投げた瓦礫の被害は「延焼」扱い（核起因なら核）")
# 消滅の遅延リザルトが再生成後の街に出ないように
p.rep("    setTimeout(showResult,1500);      // 崩れきる余韻を見せてから",
      "    { const g=cityGen; setTimeout(()=>{ if(g===cityGen) showResult(); },1500); }      // 崩れきる余韻を見せてから（再生成済みなら出さない）")
p.save()
