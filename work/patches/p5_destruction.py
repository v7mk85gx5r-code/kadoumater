import sys, re; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
snd=open('/home/user/kadoumater/work/ui/snd.js',encoding='utf-8').read()
# 1. 音モジュールの差し替え
p.rex(r"/\* ══════════ 音 ══════════ \*/\nconst Snd=\(\(\)=>\{.*?\n\}\)\(\);\n", snd)
# 2. 転倒：すぐに足元を切らず、0.5秒ほど「軋んで傾き始める」フェーズを挟む
p.rex(r"  // ④ 転倒：重心が外れている方向へ倒す\n  b\.toppled=1;.*?\n  return k;\n\}\nfunction checkBuckle",
'''  // ④ 転倒：重心が外れている方向へ倒す
  b.toppled=1;
  // ⑤ 大きな建物が傾き始めた瞬間を見せ場にする。一瞬止めてからスローモーション、画角を少し引く
  { const hgt=H*VOX;
    if(hgt>=60 || b.init>=6000){
      const k=Math.min(1,(hgt-40)/160);
      slowMo(.7+k*1.1);
      hitStop(.05); fovPunch(3+k*4);
    } }
  const l=Math.hypot(ox,oz)||1;
  // 重心は「残った側」に寄るが、建物は支点を軸にして支えを失った側（＝抉られた側）へ倒れ込む
  const tx=-ox/l, tz=-oz/l;
  // 支点：倒れる方向の反対側の足元の縁（そこを軸に回る）
  const pvx=b.ox+(spx+.5)*VOX - tx*Math.max(1.2,rx*0.9)*VOX;
  const pvz=b.oz+(spz+.5)*VOX - tz*Math.max(1.2,rz*0.9)*VOX;
  const big=H*VOX>=40 || b.init>=2500;
  b.toppling={t:0, dur:big?0.55:0.32, ang:0, maxAng:big?0.13:0.09,
              tx:tx, tz:tz, px:pvx, pz:pvz, spx:spx, spz:spz, rx:rx, cgx:cgx, cgz:cgz, over:over, W:W, D:D, H:H};
  TOPPLING.push(b);
  b.dirty=false;                             // 傾いている間は剥離判定を待つ（倒れきってから切る）
  causeToast('重心が支持面を外れた → 転倒');
  { const wx=b.ox+cgx*VOX, wz=b.oz+cgz*VOX;
    Snd.creak(wx,6,wz); dustAt(pvx,2,pvz,6,1.2); hap(HAP.crack,200); }
  return 1;
}
/* 傾き終わり：足元を断ち切り、塊が支点を軸に回りながら倒れ込む */
function toppleCut(b){
  const T=b.toppling; if(!T) return 0;
  const {W,H,D}=b, tx=T.tx, tz=T.tz, spx=T.spx, spz=T.spz, rx=T.rx;
  b.lean=[tx, tz, Math.min(1.3, 0.7+T.over*0.4)];
  b.buckT=0;
  if(b.capLimit) b.capLimit*=0.12;           // 傾いた時点で構造は保たない
  let k=0;
  const cut=Math.min(H-2, 2+((Math.random()*2)|0));
  for(let y=0;y<=cut;y++) for(let z=0;z<D;z++) for(let x=0;x<W;x++){
    const rel=(x-spx)*tx+(z-spz)*tz;           // 倒れる方向側の足元を抜く。反対側（支点）は残す
    if(rel < -Math.max(1.5, rx*0.25)) continue;
    k+=killVoxel(b,x,y,z,1);
  }
  b.dirty=true; b.mdirty=true;
  if(k>0){
    const wx=b.ox+T.cgx*VOX, wz=b.oz+T.cgz*VOX;
    dustAt(wx, 4, wz, 16, 2.0);
    collapseDust(wx, wz, k*3);
    for(let i=0;i<4;i++) vfxSmoke(T.px+rf(-6,6),2,T.pz+rf(-6,6),rf(10,18),rf(3,5),tx*rf(4,9)+rf(-3,3),rf(1,3),tz*rf(4,9)+rf(-3,3),-1);
    Snd.collapse(Math.min(1,b.init/4000),wx,6,wz);
    shake(1.0); hap(HAP.topple, 200);
  }
  return k;
}
/* 傾きの姿勢：建物の描画メッシュを支点まわりに回す（ボクセル自体は動かさない） */
const _tq=new THREE.Quaternion(), _ta=new THREE.Vector3(), _tp=new THREE.Vector3(), _to=new THREE.Vector3();
function bldPose(b,ang){
  const T=b.toppling; if(!T||!b.sec) return;
  _ta.set(T.tz,0,-T.tx).normalize();               // 回転軸：倒れる向きに直交する水平軸
  _tq.setFromAxisAngle(_ta,ang);
  _tp.set(T.px,0,T.pz);
  for(const s of b.sec){ const m=s.mesh; if(!m) continue;
    _to.set(b.ox-T.px,0,b.oz-T.pz).applyQuaternion(_tq).add(_tp);
    m.position.copy(_to); m.quaternion.copy(_tq); }
}
function bldPoseReset(b){
  if(!b.sec) return;
  for(const s of b.sec){ const m=s.mesh; if(!m) continue; m.position.set(b.ox,b.oy,b.oz); m.quaternion.set(0,0,0,1); }
}
let TOPPLING=[];
function updToppling(dt){
  for(let i=TOPPLING.length-1;i>=0;i--){
    const b=TOPPLING[i], T=b.toppling;
    if(!T||b.live<=0||b.culledGone){ if(T) bldPoseReset(b); b.toppling=null; TOPPLING.splice(i,1); continue; }
    T.t+=dt;
    const k=Math.min(1,T.t/T.dur);
    T.ang=T.maxAng*k*k*(3-2*k);
    bldPose(b,T.ang);
    if(chance(.5)) dustAt(T.px+rf(-4,4),1.5,T.pz+rf(-4,4),1,1.0);
    shake(.08+k*.25);
    if(k>=1){
      bldPoseReset(b);
      // 塊に姿勢と回転の勢いを引き継ぐ
      _ta.set(T.tz,0,-T.tx).normalize();
      _tq.setFromAxisAngle(_ta,T.maxAng);
      const wmag=T.maxAng/T.dur*1.4;
      b.pose={x:T.px,y:0,z:T.pz,q:[_tq.x,_tq.y,_tq.z,_tq.w],quat:_tq.clone(),w:[_ta.x*wmag,_ta.y*wmag,_ta.z*wmag],t:1.5};
      b.toppling=null; TOPPLING.splice(i,1);
      toppleCut(b);
    }
  }
}
function checkBuckle''')
# 塊の生成：建物の傾き姿勢を引き継ぐ
p.rep("  const px=b.ox+(x0+W/2)*VOX, py=(y0+H/2)*VOX, pz=b.oz+(z0+D/2)*VOX;\n  // 倒す向きが指示されていれば、横向きの初速と倒れ込む回転を与える\n  const L = b.lean ? {dx:b.lean[0],dz:b.lean[1],mag:b.lean[2]} : leanFor(px,py,pz);\n  chunkSrc=(b.lastSrc==='nuke')?'nuke':'collapse';      // 核で剥がれた塊は最後まで核扱い\n  const c=addChunk(vox,hpv,W,H,D,px,py,pz,vx,vy,vz,0,null,b.tint);\n  if(c) c.bid=b.id;\n  if(c&&L){\n    const tall=Math.min(2.2, (H*VOX)/Math.max(8,(W+D)*VOX*.5));   // 細長いほど倒れやすい\n    const m=L.mag*tall;",
'''  let px=b.ox+(x0+W/2)*VOX, py=(y0+H/2)*VOX, pz=b.oz+(z0+D/2)*VOX;
  // 倒す向きが指示されていれば、横向きの初速と倒れ込む回転を与える
  const L = b.lean ? {dx:b.lean[0],dz:b.lean[1],mag:b.lean[2]} : leanFor(px,py,pz);
  chunkSrc=(b.lastSrc==='nuke')?'nuke':'collapse';      // 核で剥がれた塊は最後まで核扱い
  let quat=null, PZ=(b.pose&&b.pose.t>0)?b.pose:null;
  if(PZ){ const r=qRot(PZ.q,px-PZ.x,py-PZ.y,pz-PZ.z); px=PZ.x+r[0]; py=PZ.y+r[1]; pz=PZ.z+r[2]; quat=PZ.quat; }   // 傾いた姿勢のまま塊になる
  const c=addChunk(vox,hpv,W,H,D,px,py,pz,vx,vy,vz,0,quat,b.tint);
  if(c) c.bid=b.id;
  if(c&&PZ){ c.w[0]+=PZ.w[0]; c.w[1]+=PZ.w[1]; c.w[2]+=PZ.w[2]; }
  if(c&&L){
    const tall=Math.min(2.2, (H*VOX)/Math.max(8,(W+D)*VOX*.5));   // 細長いほど倒れやすい
    const m=L.mag*tall*(PZ?0.6:1);''')
p.rep("  for(let k=0;k<blds.length;k++){ const b=blds[k];\n    if(b.buckT>0) b.buckT-=dt;\n    if(b.rmT>0) b.rmT-=dt; }",
      "  for(let k=0;k<blds.length;k++){ const b=blds[k];\n    if(b.buckT>0) b.buckT-=dt;\n    if(b.rmT>0) b.rmT-=dt;\n    if(b.pose){ b.pose.t-=dt; if(b.pose.t<=0) b.pose=null; } }\n  updToppling(dt);")
p.rep("  if(b.culled) m.visible=false;\n  scene.add(m); s.mesh=m;", "  if(b.culled) m.visible=false;\n  scene.add(m); s.mesh=m;\n  if(b.toppling) bldPose(b,b.toppling.ang);")
p.rep("      if(b.live>0 && b.style!=='pole' && b.style!=='gate'){\n        if(!checkTopple(b)) checkBuckle(b);   // まず転倒、次に座屈\n      }",
      "      if(comps.length&&_spawnMoved>0) causeToast('支えを失った → 剥離');\n      if(b.live>0 && !b.toppling && b.style!=='pole' && b.style!=='gate'){\n        if(!checkTopple(b)) checkBuckle(b);   // まず転倒、次に座屈\n      }")
p.rep("      const comps=detachBuilding(b,false);\n      for(let j=0;j<comps.length;j++) spawnChunk(b,comps[j],0,0,0);",
      "      const comps=detachBuilding(b,false);\n      _spawnMoved=0;\n      for(let j=0;j<comps.length;j++) spawnChunk(b,comps[j],0,0,0);")
p.rep("  TOPPLING=[]; lmT=0;", "  TOPPLING=[]; lmT=0;",0) if False else None
p.rep("  LMS=[]; lmT=0; bannerLmT=0; fireHeld=false;", "  LMS=[]; lmT=0; bannerLmT=0; fireHeld=false; TOPPLING=[];")
# 座屈：原因表示と音
p.rep("    efx('ring',wx,Math.max(1,wy),wz, 6, 62, .55, 0xd8b48a, .55, true);\n    Snd.crumble(.42);\n    shake(.9);",
      "    efx('ring',wx,Math.max(1,wy),wz, 6, 62, .55, 0xd8b48a, .55, true);\n    Snd.collapse(Math.min(1,k/300),wx,wy,wz);\n    causeToast('柱の耐力を超えた → 座屈');\n    shake(.9);")
# 3. 演出の強弱（fxK）とスローモーションの上限
p.rep("function shake(v){\n  shakeAmt=Math.min(SHAKE_MAX, Math.max(shakeAmt,v*0.45));",
      "function slowMo(x){ slowT=Math.min(1.8, Math.max(slowT, x*(QUAL.fxK<1?0.5:1))); }   // 大きな事件だけ。連鎖中ずっと止まらないよう上限あり\nfunction shake(v){\n  v*=QUAL.fxK;\n  shakeAmt=Math.min(SHAKE_MAX, Math.max(shakeAmt,v*0.45));")
p.rep("function hitStop(sec){\n  const now=performance.now();", "function hitStop(sec){\n  sec*=QUAL.fxK;\n  const now=performance.now();")
p.rep("function fovPunch(v){ fovOff=Math.min(14, Math.max(fovOff,v*0.55)); }", "function fovPunch(v){ fovOff=Math.min(14, Math.max(fovOff,v*0.55*QUAL.fxK)); }")
p.rep("    slowT=Math.max(slowT, 1.6);", "    slowMo(1.6);")
p.rep("  slowT=Math.max(slowT, n>2200 ? .85 : (n>700 ? .55 : .30));", "  slowMo(n>2200 ? .85 : (n>700 ? .55 : .30));")
# 4. 音の位置・種類
p.rep("  Snd.blast(Math.min(1,rad/90));\n  for(let k=0;k<chunks.length;k++){", "  Snd.blast(Math.min(1,rad/90),x,y,z);\n  for(let k=0;k<chunks.length;k++){")
p.rep("      shake(Math.min(1.5,E*.0022));\n      Snd.thud(Math.min(.5,E*.0016));",
      "      shake(Math.min(1.5,E*.0022));\n      Snd.thud(Math.min(.5,E*.0016),c.p[0],c.p[1],c.p[2]);\n      if(E>420) Snd.rubble(c.p[0],c.p[1],c.p[2],c.live);\n      { const gy=Math.max(1,c.p[1]-c.h[1]); for(let i=0;i<2;i++) vfxSmoke(c.p[0]+rf(-3,3),gy+1,c.p[2]+rf(-3,3),Math.min(30,8+E*.02),rf(2.5,4),rf(-4,4),rf(1,3),rf(-4,4),-1); }   // 接地点から土煙")
p.rep("      if(E>320){ shake(Math.min(1.2,E*.0018)); Snd.crumble(.28); }", "      if(E>320){ shake(Math.min(1.2,E*.0018)); Snd.crumble(.28,hx,hy,hz); }")
p.rep("  if(n>2200) banner('大 崩 壊','MASS COLLAPSE');", "  if(n>2200) banner('大 崩 壊','MASS COLLAPSE');\n  Snd.collapse(Math.min(1,n/2500),x,y,z);")
p.rep("  shake(Math.min(2.6,n*.006));\n  Snd.rumble();\n  dustAt(x,y,z,Math.min(96,26+n*.09),2.6);", "  shake(Math.min(2.6,n*.006));\n  if(n>700) Snd.rumble();\n  dustAt(x,y,z,Math.min(96,26+n*.09),2.6);")
p.rep("    Snd.rumble(); if(Snd.quake) Snd.quake(.5,4);\n    hap(HAP.topple, 0);", "    Snd.rumble(); if(Snd.quake) Snd.quake(.5,4); Snd.collapse(1,cx,ch*.3,cz);\n    hap(HAP.topple, 0);")
p.rep("  shake(.85); fovPunch(6); kick(-.02,(Math.random()-.5)*.03); Snd.cut();\n  if(n>500) banner('切断','SEVERED');",
      "  shake(.85); fovPunch(6); kick(-.02,(Math.random()-.5)*.03); Snd.cut();\n  if(n>60) causeToast('切断 → 上部が支えを失う');\n  if(n>500) banner('切断','SEVERED');")
p.rep("    if(ng>40){\n      efx('ring',x,Math.max(2,y),z, rad*.5, sr*1.15, .5, 0xbfe8ff, .5, true);\n      Snd.glass&&Snd.glass();\n    }",
      "    if(ng>40){\n      efx('ring',x,Math.max(2,y),z, rad*.5, sr*1.15, .5, 0xbfe8ff, .5, true);\n      Snd.glass(x,y,z); causeToast('爆風で街区の窓が砕けた');\n    }")
# 素材ごとの破片音と破片の形
p.rep("  if(!quiet && Math.random()<.14)\n    spawnDebris(b.ox+x*VOX+VOX/2, y*VOX+VOX/2, b.oz+z*VOX+VOX/2, M);",
      "  if(!quiet && Math.random()<.14)\n    spawnDebris(b.ox+x*VOX+VOX/2, y*VOX+VOX/2, b.oz+z*VOX+VOX/2, M);\n  if(!quiet && Math.random()<.10) Snd.mat(m, b.ox+x*VOX+VOX/2, y*VOX+VOX/2, b.oz+z*VOX+VOX/2);")
p.rep("  const glass=M.n.indexOf('窓')>=0;\n  const k=kick||1;\n  const s0=glass?(.45+Math.random()*.45):(.30+Math.random()*.85);",
      "  const glass=M.n.indexOf('窓')>=0;\n  const metal=!glass&&(M.n==='鉄骨'||M.n==='金属パネル'||M.n==='ダクト'||M.n==='シャッター'||M.n==='サッシ'||M.n==='手すり'||M.n==='ガス管');\n  const wood=!glass&&(M.n==='樹木'||M.n==='幹');\n  const k=kick||1;\n  const s0=glass?(.45+Math.random()*.45):(.30+Math.random()*.85);")
p.rep("    sx:s0*rf(.6,1.3), sy:glass?.05:s0*rf(.5,1.1), sz:s0*rf(.6,1.3),",
      "    sx:metal?s0*rf(1.8,3.2):(wood?s0*rf(1.4,2.4):s0*rf(.6,1.3)), sy:glass?.05:(metal?s0*rf(.15,.3):(wood?s0*rf(.12,.25):s0*rf(.5,1.1))), sz:metal?s0*rf(.15,.35):(wood?s0*rf(.35,.6):s0*rf(.6,1.3)),   // 金属は細長く、木は板状、コンクリートは塊")
p.save()
