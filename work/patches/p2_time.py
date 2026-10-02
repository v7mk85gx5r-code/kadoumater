import sys; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
# ── dt スケールの共通ヘルパー（描画回数に依存する確率・減衰をなくす） ──
p.rep("const GRAV=42, MAXW=8.5;",
'''const GRAV=42, MAXW=8.5;
/* 毎フレームの確率や減衰を「60fps基準」で書いてあった箇所を、実際の刻み幅に比例させるための係数 */
let dtK=1;
function chance(p){ return Math.random()<p*dtK; }                       // 1フレームあたり p（60fps基準）の確率
function nK(n){ const v=n*dtK; let k=v|0; if(Math.random()<v-k) k++; return k; }   // 個数を刻みに比例させる（端数は確率で）
function dampK(k){ return Math.pow(k,dtK); }                            // 毎フレーム k 倍の減衰''')
# ── 塊の減衰・粉塵 ──
p.rep("  if(Math.random()<.14&&c.live>60){ const cs=Math.cbrt(c.live)*VOX*.6;",
      "  if(chance(.14)&&c.live>60){ const cs=Math.cbrt(c.live)*VOX*.6;")
p.rep("  c.v[0]*=.9985; c.v[1]*=.9985; c.v[2]*=.9985;\n  c.w[0]*=.993; c.w[1]*=.993; c.w[2]*=.993;",
      "  { const dv=dampK(.9985), dw=dampK(.993);\n    c.v[0]*=dv; c.v[1]*=dv; c.v[2]*=dv;\n    c.w[0]*=dw; c.w[1]*=dw; c.w[2]*=dw; }")
p.rep("  if(sp2<3.0){ c.v[0]*=.90; c.v[1]*=.94; c.v[2]*=.90; }\n  if(sw<1.2){ c.w[0]*=.88; c.w[1]*=.88; c.w[2]*=.88; }",
      "  if(sp2<3.0){ const a=dampK(.90), b2=dampK(.94); c.v[0]*=a; c.v[1]*=b2; c.v[2]*=a; }\n  if(sw<1.2){ const a=dampK(.88); c.w[0]*=a; c.w[1]*=a; c.w[2]*=a; }")
# ── 点粒子：寿命と減衰が毎フレーム固定だった ──
p.rep("    const p=fx[i]; p.life-=p.dec;", "    const p=fx[i]; p.life-=p.dec*dtK;")
p.rep("        p.vy*=.997; p.vx*=.996; p.vz*=.996;", "        { const a=dampK(.997), b2=dampK(.996); p.vy*=a; p.vx*=b2; p.vz*=b2; }")
p.rep("        p.vx*=.985; p.vz*=.985;                 // 外向きの勢いを減衰させる", "        { const a=dampK(.985); p.vx*=a; p.vz*=a; }                 // 外向きの勢いを減衰させる")
p.rep("    else { p.vy+=2.2*dt; p.vx*=.975; p.vz*=.975; p.r+=p.gr*dt*10; }", "    else { const a=dampK(.975); p.vy+=2.2*dt; p.vx*=a; p.vz*=a; p.r+=p.gr*dt*10; }")
p.rep("    const p=gxA[i]; p.life-=p.dec;", "    const p=gxA[i]; p.life-=p.dec*dtK;")
p.rep("    p.vy-=6*dt; p.vx*=.93; p.vz*=.93; p.vy*=.93;", "    { const a=dampK(.93); p.vy-=6*dt; p.vx*=a; p.vz*=a; p.vy*=a; }")
# ── 埃・火・ガス・旋風・破壊球・隕石・誘導弾・特異点・軌道砲・塊の粉塵 ──
p.rep("  for(let k=0;k<4;k++){\n    dustScan=(dustScan+1)%blds.length;", "  for(let k=0,kn=nK(4);k<kn;k++){\n    dustScan=(dustScan+1)%blds.length;")
p.rep("    for(let k=0;k<5 && gxA.length<680;k++){\n      const h=Math.random();", "    for(let k=0,kn=nK(5);k<kn && gxA.length<680;k++){\n      const h=Math.random();")
p.rep("    for(let k=0;k<3 && fx.length<FXCAP-30;k++){\n      const a2=Math.random()*6.283 + S2.t*2.0*S2.spin;", "    for(let k=0,kn=nK(3);k<kn && fx.length<FXCAP-30;k++){\n      const a2=Math.random()*6.283 + S2.t*2.0*S2.spin;")
p.rep("    if(Math.random()<.3){ KSRC=S2.src||'fire';", "    if(chance(.3)){ KSRC=S2.src||'fire';")
p.rep("    if(Math.random()<.05) Snd.rumble();\n    shake(.10);", "    if(chance(.05)) Snd.rumble();\n    shake(.10);")
p.rep("    if(fx.length<FXCAP-20 && Math.random()<.5)\n      fx.push({t:'smoke', x:g.x+rf(-1.5,1.5)", "    if(fx.length<FXCAP-20 && chance(.5))\n      fx.push({t:'smoke', x:g.x+rf(-1.5,1.5)")
p.rep("    if(Math.random()<.035) vfxSmoke(f.x+rf(-2,2)", "    if(chance(.035)) vfxSmoke(f.x+rf(-2,2)")
p.rep("    if(fx.length<FXCAP-40 && Math.random()<.75){\n      const a=Math.random()*6.283, r=Math.random()*f.r;", "    if(fx.length<FXCAP-40 && chance(.75)){\n      const a=Math.random()*6.283, r=Math.random()*f.r;")
p.rep("    for(let i=0;i<3 && gxA.length<640;i++){", "    for(let i=0,kn=nK(3);i<kn && gxA.length<640;i++){")
p.rep("    if(Math.random()<.05) Snd.suck();", "    if(chance(.05)) Snd.suck();")
p.rep("    for(let i=0;i<14 && gxA.length<660;i++){", "    for(let i=0,kn=nK(14);i<kn && gxA.length<660;i++){")
p.rep("    for(let i=0;i<7 && fx.length<FXCAP-30;i++){", "    for(let i=0,kn=nK(7);i<kn && fx.length<FXCAP-30;i++){")
p.rep("    if(Math.random()<.22) Snd.blast(.8);", "    if(chance(.22)) Snd.blast(.8);")
p.rep("      for(let q=0;q<5;q++)\n        spark(m.p[0]+rf(-m.r,m.r)", "      for(let q=0,qn=nK(5);q<qn;q++)\n        spark(m.p[0]+rf(-m.r,m.r)")
p.rep("      if(Math.random()<.5) vfxFire(m.p[0]-m.v[0]/sp2*m.r*1.5", "      if(chance(.5)) vfxFire(m.p[0]-m.v[0]/sp2*m.r*1.5")
p.rep("      if(Math.random()<.35) vfxSmoke(m.p[0]-m.v[0]/sp2*m.r*3", "      if(chance(.35)) vfxSmoke(m.p[0]-m.v[0]/sp2*m.r*3")
p.rep("      for(let q=0;q<3 && fx.length<FXCAP-40;q++)\n        fx.push({t:'smoke',x:m.p[0]+rf(-6,6)", "      for(let q=0,qn=nK(3);q<qn && fx.length<FXCAP-40;q++)\n        fx.push({t:'smoke',x:m.p[0]+rf(-6,6)")
p.rep("    if(Math.random()<.22){                                   // 新しい煙で尾を引く", "    if(chance(.22)){                                   // 新しい煙で尾を引く")
p.rep("    if(fx.length<FXCAP-60 && Math.random()<.85){\n      const sp3=", "    if(fx.length<FXCAP-60 && chance(.85)){\n      const sp3=")
p.rep("    if(A.tick%2===0){\n      // 中心付近を削り、削れた分は吸い込まれる光として見せる\n      const n2=40;   // 破壊はしない。吸い込まれる光だけを出す\n      for(let i=0;i<Math.min(10,n2*.4) && gxA.length<700;i++){",
      "    {\n      // 吸い込まれる光（破壊はしない）\n      for(let i=0,kn=nK(5);i<kn && gxA.length<700;i++){")
p.rep("    for(let i=0;i<7;i++){\n      const a=Math.random()*6.283, e=Math.random()*3.14, r=120+Math.random()*150;",
      "    for(let i=0,kn=nK(7);i<kn;i++){\n      const a=Math.random()*6.283, e=Math.random()*3.14, r=120+Math.random()*150;")
p.rep("    if(A.tick%6===0) shake(.5);", "    A.shkT=(A.shkT||0)+dt; if(A.shkT>=.1){ A.shkT=0; shake(.5); }")
p.rep('''    orbitFx.tick=(orbitFx.tick||0)+1;
    if(orbitFx.tick%2===0) damageColumn(orbitFx.x,orbitFx.z,17,900,0,760);
    if(orbitFx.tick%6===0) addHot(orbitFx.x,2,orbitFx.z,26,.6,3.0);
    dustAt(orbitFx.x+rf(-24,24),Math.random()*180,orbitFx.z+rf(-24,24),4,2.2);
    // 吹き上がる火の粉（光の筋）と、足元で渦巻く炎・立ち上る煙
    for(let i=0;i<5;i++){''',
'''    // 柱状の破壊は固定の刻み（30Hz）で進める＝描画回数に威力が依存しない
    orbitFx.dmgT=(orbitFx.dmgT||0)+dt;
    for(let n=0;orbitFx.dmgT>=1/30 && n<4;n++){ orbitFx.dmgT-=1/30; damageColumn(orbitFx.x,orbitFx.z,17,900,0,760); }
    if(orbitFx.dmgT>1/30*4) orbitFx.dmgT=0;
    orbitFx.hotT=(orbitFx.hotT||0)+dt; if(orbitFx.hotT>=.1){ orbitFx.hotT=0; addHot(orbitFx.x,2,orbitFx.z,26,.6,3.0); }
    dustAt(orbitFx.x+rf(-24,24),Math.random()*180,orbitFx.z+rf(-24,24),nK(4),2.2);
    // 吹き上がる火の粉（光の筋）と、足元で渦巻く炎・立ち上る煙
    for(let i=0,kn=nK(5);i<kn;i++){''')
p.rep("    if(orbitFx.tick%3===0) vfxFire(orbitFx.x+rf(-14,14)", "    if(chance(.33)) vfxFire(orbitFx.x+rf(-14,14)")
p.rep("    if(orbitFx.tick%5===0) vfxSmoke(orbitFx.x+rf(-24,24)", "    if(chance(.2)) vfxSmoke(orbitFx.x+rf(-24,24)")
p.rep("      if(fx.length<FXCAP-30 && Math.random()<.5)\n        fx.push({t:'smoke', x:P.x+rf(-1,1), y:y+4", "      if(fx.length<FXCAP-30 && chance(.5))\n        fx.push({t:'smoke', x:P.x+rf(-1,1), y:y+4")
p.rep("    if(!c.sleep && Math.hypot(c.v[0],c.v[1],c.v[2])>18 && Math.random()<.5)", "    if(!c.sleep && Math.hypot(c.v[0],c.v[1],c.v[2])>18 && chance(.5))")
# 交通：塊との衝突判定を時間基準に
p.rep("let trfT=0;", "let trfT=0, trfChk=0;")
p.rep("  if(((trfT*60)|0)%4===0) for(const c of C){ if(c.dead) continue;", "  trfChk+=dt;\n  if(trfChk>=1/15){ trfChk=0; for(const c of C){ if(c.dead) continue;")
p.rep("      if(q.p[1]<14&&Math.abs(q.p[0]-cx)<6&&Math.abs(q.p[2]-cz)<6){ wreckCar(c, q.src==='nuke'?'nuke':'domino'); break; } } }",
      "      if(q.p[1]<14&&Math.abs(q.p[0]-cx)<6&&Math.abs(q.p[2]-cz)<6){ wreckCar(c, q.src==='nuke'?'nuke':'domino'); break; } } } }")
# step の先頭で dtK を更新
p.rep("function step(dt){\n  const _a=_now();", "function step(dt){\n  const _a=_now();\n  dtK=dt*60;")
# ── レールガン：固定刻み（50Hz）で削る。描画回数ではなく時間で威力が決まる ──
p.rep('''let railOn=false, railHum=null;
function railTick(dt){
  const o=camera.position, dir=new THREE.Vector3();
  camera.getWorldDirection(dir);
  const hit=aimRay();
  const from=Math.max(5,(hit.miss?60:hit.d)-6);
  damageBeam(o.x+dir.x*from,o.y+dir.y*from,o.z+dir.z*from,dir.x,dir.y,dir.z,190,4.3,175);''',
'''let railOn=false, railHum=null, railAcc=0;
const RAIL_DT=1/50;
function railTick(dt){
  const o=camera.position, dir=new THREE.Vector3();
  camera.getWorldDirection(dir);
  const hit=aimRay();
  const from=Math.max(5,(hit.miss?60:hit.d)-6);
  railAcc+=dt;
  let ticks=0;
  while(railAcc>=RAIL_DT && ticks<6){ railAcc-=RAIL_DT; ticks++; }   // 長いフレームでは遅れを取り戻す（上限あり）
  if(railAcc>RAIL_DT*6) railAcc=0;
  for(let k=0;k<ticks;k++) damageBeam(o.x+dir.x*from,o.y+dir.y*from,o.z+dir.z*from,dir.x,dir.y,dir.z,190,4.3,175);''')
p.rep("    for(let i=0;i<7;i++)                                   // 着弾点から青白い火花の筋がこちらへ飛び散る",
      "    for(let i=0,kn=nK(7);i<kn;i++)                                   // 着弾点から青白い火花の筋がこちらへ飛び散る")
p.rep("    if(Math.random()<.22) vfxFire(hit.x,hit.y,hit.z,rf(2.5,4.5),rf(.25,.45),1.25,0,4,0);\n    if(Math.random()<.10) vfxSmoke(hit.x,hit.y,hit.z,rf(3,5),rf(1.5,2.6),rf(-2,2),rf(3,6),rf(-2,2),.6);",
      "    if(chance(.22)) vfxFire(hit.x,hit.y,hit.z,rf(2.5,4.5),rf(.25,.45),1.25,0,4,0);\n    if(chance(.10)) vfxSmoke(hit.x,hit.y,hit.z,rf(3,5),rf(1.5,2.6),rf(-2,2),rf(3,6),rf(-2,2),.6);")
p.rep("    for(let i=0;i<2;i++)\n      gxA.length<700 && gxA.push({x:hit.x,y:hit.y,z:hit.z,", "    for(let i=0,kn=nK(2);i<kn;i++)\n      gxA.length<700 && gxA.push({x:hit.x,y:hit.y,z:hit.z,")
p.rep("    if(Math.random()<.6) dustAt(hit.x,hit.y,hit.z,1,.8);\n    if(Math.random()<.10) efx('ball',hit.x,hit.y,hit.z, 1.5, 9, .16, 0x9fe8ff, .8);",
      "    if(chance(.6)) dustAt(hit.x,hit.y,hit.z,1,.8);\n    if(chance(.10)) efx('ball',hit.x,hit.y,hit.z, 1.5, 9, .16, 0x9fe8ff, .8);")
# ── 音の同時発音予算を時間基準に／一時停止 ──
p.rep("    f(){ bud=8; }, kick(){ A(); },",
      "    f(dt){ bud=Math.min(12, bud+(dt||.016)*480); }, kick(){ A(); },\n    pause(){ try{ this.humOff(); if(ac&&ac.state==='running') ac.suspend(); }catch(e){} },\n    resume(){ try{ if(ac&&S.sound&&ac.state==='suspended') ac.resume(); }catch(e){} },")
# ── 反射：一時変更した可視状態を必ず元に戻す（元々非表示のものを表示してしまわない）／更新間隔 ──
p.rep('''  WET.u.uWet.value=WET_LEVEL;
  const hide=[WET.ground,roadMesh,glowFloor,VFX.smoke];   // 煙は反射に描かない（半透明の重なりが重い）
  for(const m of hide) if(m) m.visible=false;
  // 点光源も上下反転する（地面の下に写る世界を、正しい側から照らすため）
  const P=LITU.uLP.value;
  for(let i=0;i<NLIT;i++) P[i].y=-P[i].y;
  for(const h of LITU.uHot.value) h.y=-h.y;
  // 看板も上下反転（反射の中で文字が鏡像になる）
  for(let i=0;i<SIGNS.length;i++){ const u=LITU.uSgO.value[i]; u.y=-(u.y+LITU.uSgR.value[i].z); }
  scene.scale.y=-1; LITU.uFlip.value=-1;
  renderer.setRenderTarget(WET.rt);
  renderer.render(scene,camera);
  scene.scale.y=1; LITU.uFlip.value=1;
  for(const h of LITU.uHot.value) h.y=-h.y;
  for(let i=0;i<SIGNS.length;i++){ const u=LITU.uSgO.value[i]; u.y=-u.y-LITU.uSgR.value[i].z; }
  for(let i=0;i<NLIT;i++) P[i].y=-P[i].y;
  for(const m of hide) if(m) m.visible=true;
  WET.u.uRefl.value=WET.rt.texture;
}''',
'''  WET.u.uWet.value=WET_LEVEL;
  WET.frame=(WET.frame|0)+1;
  if((WET.every|0)>1 && (WET.frame%WET.every)!==0 && WET.u.uRefl.value){ return; }   // 中画質では隔フレームで更新（前の結果を使い回す）
  const hide=[WET.ground,roadMesh,glowFloor,VFX.smoke,VFX.fire,DEB.mesh];   // 煙・火球・破片は反射に描かない（半透明の重なりが重い）
  const prev=[];
  for(let i=0;i<hide.length;i++){ const m=hide[i]; prev[i]=m?m.visible:false; if(m) m.visible=false; }
  const P=LITU.uLP.value;
  const flip=(s)=>{
    // 点光源・赤熱・看板も上下反転する（地面の下に写る世界を、正しい側から照らすため）
    for(let i=0;i<NLIT;i++) P[i].y=-P[i].y;
    for(const h of LITU.uHot.value) h.y=-h.y;
    for(let i=0;i<SIGNS.length;i++){ const u=LITU.uSgO.value[i]; u.y = s<0 ? -(u.y+LITU.uSgR.value[i].z) : -u.y-LITU.uSgR.value[i].z; }
    scene.scale.y=s; LITU.uFlip.value=s;
  };
  try{
    flip(-1);
    renderer.setRenderTarget(WET.rt);
    renderer.render(scene,camera);
    WET.u.uRefl.value=WET.rt.texture;
  }catch(e){ WET.u.uWet.value=0; }
  finally{
    if(scene.scale.y<0) flip(1);
    for(let i=0;i<hide.length;i++) if(hide[i]) hide[i].visible=prev[i];   // 元の可視状態へ（元々非表示だったものは非表示のまま）
    renderer.setRenderTarget(null);
  }
}''')
# ── 画質プリセット：段階を一元管理。低→高で元の解像度へ戻る。自動は数秒の傾向で上下する ──
p.rex(r"const QUAL=\{mode:'auto', smokeMax:120, pedK:1, basePR:1, el:null, acc:0, n:0, worst:0, t:0\};\nfunction setQuality\(mode\)\{.*?\n\}\nfunction updPerf\(rawDt\)\{.*?\n\}\n",
'''const QUAL={mode:'auto', level:0, applied:false, smokeMax:120, pedK:1, pr:1, el:null, acc:0, n:0, worst:0, t:0,
  hist:[], settleUntil:0, downT:0, showPerf:false, ring:new Float32Array(180), ri:0, fxK:1, minDt:1};
/* 段階ごとの設定：3D内部解像度（目標画素数, MP）／反射の更新間隔（0=切る）／煙・人の上限／ブルーム段数／MSAA */
const QLV=[
  {mp:1.00, refl:1, smoke:120, ped:1.0,  mips:5, msaa:true },   // 高
  {mp:0.72, refl:2, smoke:84,  ped:0.6,  mips:4, msaa:true },   // 中
  {mp:0.48, refl:0, smoke:56,  ped:0.35, mips:4, msaa:false},   // 低
  {mp:0.36, refl:0, smoke:40,  ped:0.2,  mips:3, msaa:false},   // 最低（自動のみ）
];
const QNAME=['高','中','低','最低'];
function prForLevel(L){
  const w=Math.max(1,window.innerWidth), h=Math.max(1,window.innerHeight);
  const dpr=Math.min(3,window.devicePixelRatio||1);
  return Math.max(0.75, Math.min(dpr, Math.sqrt(QLV[L].mp*1e6/(w*h))));
}
function applyLevel(L,force){
  L=Math.max(0,Math.min(QLV.length-1,L|0));
  if(!force && QUAL.applied && QUAL.level===L) return;
  QUAL.level=L; QUAL.applied=true;
  const Q=QLV[L];
  QUAL.smokeMax=Q.smoke; VFX_SMAX=Q.smoke;
  if(VFX.sa.length>VFX_SMAX) VFX.sa.splice(0,VFX.sa.length-VFX_SMAX);
  const pedUp=Q.ped>QUAL.pedK; QUAL.pedK=Q.ped;
  QUAL.pr=prForLevel(L);
  if(renderer) renderer.setPixelRatio(QUAL.pr);
  POST.level=L; POST.mipsN=Q.mips; POST.wantMsaa=Q.msaa;
  WET.every=Q.refl;
  if(typeof resize==='function' && renderer) resize();      // RT も作り直す
  WET.on=POST.on&&Q.refl>0;
  if(PED.list.length>PED_MAX*QUAL.pedK) PED.list.length=Math.floor(PED_MAX*QUAL.pedK);
  else if(pedUp && blds.length && typeof buildPeds==='function') buildPeds();
  QUAL.settleUntil=performance.now()+3000; QUAL.hist.length=0;
  updQualLabel();
}
function updQualLabel(){
  const b=document.getElementById('bQual');
  const name=(QUAL.mode==='auto')?('自動('+QNAME[QUAL.level]+')'):({high:'高',mid:'中',low:'低'})[QUAL.mode];
  if(b) b.textContent='画質: '+name;
  const b2=document.getElementById('pmQual'); if(b2) b2.textContent=name;
}
function setQuality(mode){
  QUAL.mode=mode;
  if(mode==='auto') applyLevel(QUAL.level,true);
  else applyLevel({high:0,mid:1,low:2}[mode]||0,true);
}
/* 性能計測：実フレーム間隔を蓄積し、1秒ごとに集計。自動画質は3秒の傾向で下げ、12秒以上余裕が続いたら1段戻す */
function updPerf(rawDt){
  QUAL.acc+=rawDt; QUAL.n++; if(rawDt>QUAL.worst) QUAL.worst=rawDt; QUAL.t+=rawDt;
  if(rawDt<QUAL.minDt) QUAL.minDt=rawDt;
  QUAL.ring[QUAL.ri]=rawDt*1000; QUAL.ri=(QUAL.ri+1)%QUAL.ring.length;
  if(QUAL.t<1.0) return;
  const avg=QUAL.acc/QUAL.n*1000, worst=QUAL.worst*1000, base=Math.max(4,QUAL.minDt*1000);
  QUAL.lastAvg=avg; QUAL.lastWorst=worst;
  QUAL.acc=0; QUAL.n=0; QUAL.worst=0; QUAL.t=0;
  if(QUAL.showPerf && typeof drawPerf==='function') drawPerf(avg,worst);
  const now=performance.now();
  if(QUAL.mode!=='auto' || now<QUAL.settleUntil || document.hidden || paused) return;
  QUAL.hist.push(avg); if(QUAL.hist.length>3) QUAL.hist.shift();
  if(QUAL.hist.length<3) return;
  const m=(QUAL.hist[0]+QUAL.hist[1]+QUAL.hist[2])/3;
  if(m>25 && QUAL.level<QLV.length-1){ QUAL.downT=now; applyLevel(QUAL.level+1); }
  else if(QUAL.level>0 && m<=base*1.2+1.0 && now-QUAL.downT>12000){ applyLevel(QUAL.level-1); QUAL.settleUntil=now+6000; }
}
''')
# resizePost：段階設定に従う（MSAA／ブルーム段数／反射の解像度）
p.rep("  if(POST.gl2&&THREE.WebGLMultisampleRenderTarget&&POST.level<2){",
      "  if(POST.gl2&&THREE.WebGLMultisampleRenderTarget&&POST.wantMsaa!==false){")
p.rep("  for(let i=0;i<5;i++){ mw=Math.max(1,mw>>1); mh=Math.max(1,mh>>1); POST.mips.push(mkRT(mw,mh,false)); }\n  for(let i=0;i<4;i++) POST.ups.push(mkRT(POST.mips[i].width,POST.mips[i].height,false));",
      "  const nm=POST.mipsN||5;\n  for(let i=0;i<nm;i++){ mw=Math.max(1,mw>>1); mh=Math.max(1,mh>>1); POST.mips.push(mkRT(mw,mh,false)); }\n  for(let i=0;i<nm-1;i++) POST.ups.push(mkRT(POST.mips[i].width,POST.mips[i].height,false));")
p.rep("  if(WET.rt) WET.rt.dispose();\n  WET.rt=mkRT(Math.max(1,w>>1),Math.max(1,h>>1),true);\n  WET.u.uScreen.value.set(w,h);\n  WET.on=POST.level<1;",
      "  if(WET.rt){ WET.rt.dispose(); WET.rt=null; WET.u.uRefl.value=null; }\n  if((WET.every|0)>0){ const dv=(WET.every|0)>1?3:2; WET.rt=mkRT(Math.max(1,(w/dv)|0),Math.max(1,(h/dv)|0),true); }\n  WET.u.uScreen.value.set(w,h);\n  WET.on=(WET.every|0)>0 && !!WET.rt;")
p.rep("    if(POST.level<2){ POST.level=2; resizePost(); return; }\n    POST.on=false; renderer.setRenderTarget(null);",
      "    if(POST.wantMsaa!==false){ POST.wantMsaa=false; resizePost(); return; }\n    POST.on=false; WET.on=false; renderer.setRenderTarget(null);")
p.rep("    for(const t of [POST.rt, POST.mips[0]]){", "    for(const t of [POST.rt, POST.mips[0], WET.rt]){ if(!t) continue;")
# renderFrame 末尾の旧・自動画質（下げるだけで戻らない）を撤去
p.rex(r"  fsPass\(M\.comp,null\);\n  // 自動画質調整：実時間で重い状態が続いたら段階的に下げる\n  const now=performance\.now\(\);\n  if\(POST\.lastT\)\{.*?\n  POST\.lastT=now;\n\}",
      "  fsPass(M.comp,null);\n}")
# 初期化：DPR の決め方を段階設定に統一
p.rep("  renderer.setPixelRatio(Math.min(2,window.devicePixelRatio||1));", "  renderer.setPixelRatio(prForLevel(0));")
p.rep("function resize(){\n  renderer.setSize(window.innerWidth,window.innerHeight);",
      "function resize(){\n  if(QUAL.applied) renderer.setPixelRatio(prForLevel(QUAL.level));   // 回転で画面の画素数が変わる\n  renderer.setSize(window.innerWidth,window.innerHeight);\n  needFrame=true;")
# ── モードの時計：実経過時間（ポーズ・バックグラウンドを除く）。スローモーションや処理落ちで延びない ──
p.rep("      runLeft = runStarted ? Math.max(0, runLeft-dt) : M.sec;", "      runLeft = runStarted ? Math.max(0, M.sec-runElapsed) : M.sec;")
p.rep("  runOver=false; runStarted=false; runLeft=modeDef().sec||0; runEndT=0; settleT=0; runEndTitle=null;",
      "  runOver=false; runStarted=false; runLeft=modeDef().sec||0; runElapsed=0; runEndT=0; settleT=0; runEndTitle=null;")
# ── メインループ：実フレーム間隔／制限付きシミュレーション刻み／演出用の時計を区別。ポーズ・コンテキスト喪失 ──
p.rex(r"let last=performance\.now\(\);\nfunction loop\(now\)\{.*?\n\}\nrequestAnimationFrame\(loop\);",
'''let last=performance.now(), paused=false, ctxLost=false, runElapsed=0, realDt=.016, needFrame=true;
let onPauseChange=null;            // UI 側が差し替える（ポーズメニューの表示）
function setPaused(v,reason){
  v=!!v;
  if(paused===v) return;
  paused=v;
  if(v){
    if(typeof releasePointers==='function') releasePointers();
    if(railOn){ railOn=false; Snd.humOff(); }
    fireHeld=false;
    Snd.pause();
  } else {
    last=performance.now();
    Snd.resume();
  }
  if(onPauseChange) onPauseChange(v,reason);
}
document.addEventListener('visibilitychange',()=>{
  if(document.hidden) setPaused(true,'bg');
  else last=performance.now();                      // 復帰後の最初の刻みを巨大にしない（再開はメニューから）
});
window.addEventListener('pagehide',()=>setPaused(true,'bg'));
function loop(now){
  requestAnimationFrame(loop);
  let raw=(now-last)/1000; last=now;
  if(!(raw>0)||raw>1) raw=.016;                     // 長い空白（バックグラウンド復帰など）はコマ送りにしない
  if(ctxLost) return;
  updPerf(raw);                                     // 実フレーム間隔（上限なし）で性能を見る
  if(paused){ if(needFrame){ needFrame=false; try{ renderFrame(0); }catch(e){} } return; }
  realDt=Math.min(.05,raw);                         // 入力・カメラ・UI 用：スローモーションの影響を受けない
  let dt=realDt;                                    // シミュレーション用：上限付き
  if(slowT>0){
    slowT-=realDt;
    slowK += ((slowT>0?.34:1)-slowK)*Math.min(1,realDt*9);
  } else if(slowK<1){
    slowK += (1-slowK)*Math.min(1,realDt*3.2);
    if(slowK>.99) slowK=1;
  }
  dt*=slowK;
  if(hitStopT>0){ hitStopT-=realDt; dt*=.05; }     // ヒットストップ：大きな着弾の瞬間だけ時間がほぼ止まる
  if(runStarted && !runOver && !resultOn) runElapsed+=raw;   // モードの時計は実時間
  Snd.f(realDt);
  readKeys();
  const CW=WPN.find(w=>w.id===wpn);
  // レールガンは照射の開始で1発。撃ち切った後は新たに照射できない（照射中のものは続く）
  const wantRail=fireHeld && !!CW.cont && (railOn || canShoot());
  if(wantRail!==railOn){ railOn=wantRail; railOn?Snd.humOn():Snd.humOff();
    if(railOn){ S.shots++; noteShot(); railAcc=RAIL_DT; } }
  if(fireHeld && !CW.cont && cd<=0 && CW.id!=='demo') fireWeapon();
  updCam(realDt);
  if(railOn) railTick(dt);
  step(dt);
  updHUD(realDt);
  updFlash(realDt); updScoreUI(realDt);
  renderFrame(dt);
  needFrame=false;
}
requestAnimationFrame(loop);''')
p.save()
