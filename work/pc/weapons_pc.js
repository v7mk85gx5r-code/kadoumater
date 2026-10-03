/* ══════════ 機関砲・絨毯爆撃・焼夷弾（PC版で追加） ══════════ */
let gunOn=false, gunAcc=0, gunHeat=0, gunShotN=0;
const GUN_DT=1/14;                                    // 毎秒14発（固定刻み。フレームレートに依存しない）
let tracers=[], trcPool=[];
function addTracer(ax,ay,az,bx,by,bz){
  let e=null; for(let i=0;i<trcPool.length;i++) if(!trcPool[i].busy){ e=trcPool[i]; break; }
  if(!e) return;
  e.busy=true; e.o.visible=true;
  tracers.push({e:e,ax:ax,ay:ay,az:az,bx:bx,by:by,bz:bz,t:0,len:Math.max(1,Math.hypot(bx-ax,by-ay,bz-az))});
}
function updTracers(dt){
  if(!gunOn) gunHeat=Math.max(0,gunHeat-dt*.6);
  for(let i=tracers.length-1;i>=0;i--){
    const T=tracers[i]; T.t+=dt;
    const spd=1100;                                   // 曳光弾の見かけの速度
    const head=Math.min(T.len,T.t*spd), tail=Math.max(0,head-Math.min(70,T.len*.5));
    if(tail>=T.len-.01 || T.t>1.4){ T.e.busy=false; T.e.o.visible=false; T.e.mat.opacity=0; tracers.splice(i,1); continue; }
    _d1.set(T.bx-T.ax,T.by-T.ay,T.bz-T.az).divideScalar(T.len);
    const m=(head+tail)*.5;
    T.e.o.position.set(T.ax+_d1.x*m, T.ay+_d1.y*m, T.az+_d1.z*m);
    T.e.o.quaternion.setFromUnitVectors(_up,_d1);
    T.e.o.scale.set(.36,Math.max(.5,head-tail),.36);
    T.e.mat.opacity=.9;
  }
}
function gunTick(dt){
  gunAcc+=dt;
  let n=0;
  while(gunAcc>=GUN_DT && n<6){ gunAcc-=GUN_DT; n++; }   // 長いフレームでは遅れを取り戻す（上限あり）
  if(gunAcc>GUN_DT*6) gunAcc=0;
  if(!n) return;
  const o=camera.position, dir=new THREE.Vector3(); camera.getWorldDirection(dir);
  const rt=new THREE.Vector3().crossVectors(dir,new THREE.Vector3(0,1,0)).normalize();
  const upv=new THREE.Vector3().crossVectors(rt,dir).normalize();
  for(let k=0;k<n;k++){
    gunHeat=Math.min(1,gunHeat+.035);
    const spd=.005+gunHeat*.013;                        // 撃ち続けるほど散る
    const d=new THREE.Vector3().copy(dir).addScaledVector(rt,rf(-spd,spd)).addScaledVector(upv,rf(-spd,spd)).normalize();
    const h=rayCast(o,d,2600);
    const side=(gunShotN++&1)?1:-1;
    const mx=o.x+d.x*5+rt.x*1.7*side-upv.x*1.1, my=o.y+d.y*5+rt.y*1.7*side-upv.y*1.1, mz=o.z+d.z*5+rt.z*1.7*side-upv.z*1.1;
    if(!h.miss){
      if(h.ground){
        dustAt(h.x,h.y+.4,h.z,2,1.0);
        for(let i=0;i<3;i++) spark(h.x,h.y+.3,h.z,rf(-14,14),rf(6,22),rf(-14,14),rf(.2,.4),1,.8,.5);
      } else {
        damageSphere(h.x,h.y,h.z,4.0,190);                 // 1発でコンクリート数個ぶん。窓と外壁を削り取る
        for(let i=0;i<6;i++) spark(h.x,h.y,h.z,-d.x*rf(8,34)+rf(-16,16),rf(-2,18),-d.z*rf(8,34)+rf(-16,16),rf(.2,.5),1,.78,.42);
        if(chance(.35)) dustAt(h.x,h.y,h.z,1,.7);
        addHot(h.x,h.y,h.z,2.5,.22,1.2);
        glow(h.x,h.y,h.z,2,8,[1,.75,.4]);
        if(chance(.3)){ const q=bldAt(h.x,h.y,h.z); if(q) Snd.mat(q.b.vox[q.x+q.b.W*(q.y+q.b.H*q.z)],h.x,h.y,h.z); }
      }
      addTracer(mx,my,mz,h.x,h.y,h.z);
    } else addTracer(mx,my,mz,o.x+d.x*1400,o.y+d.y*1400,o.z+d.z*1400);
    addLight(mx,my,mz,18,[1,.8,.5],1.0,.05);
    efx('ball',mx,my,mz,.6,2.6,.06,0xffe0a0,.9);
    Snd.gun(); kick(-.0025,(Math.random()-.5)*.002);
  }
  shake(.03); fovPunch(.5);
}
/* 絨毯爆撃：照準の向きに沿って9発。高度をずらして着弾を順に歩かせる（落下は無誘導の弾体と同じ経路） */
function fireCarpet(o,dir,hit){
  const tg = hit.miss ? {x:o.x+dir.x*600,y:0,z:o.z+dir.z*600} : hit;
  let fx0=dir.x, fz0=dir.z; const fl=Math.hypot(fx0,fz0)||1; fx0/=fl; fz0/=fl;
  const N=9, gap=26, g=150, vy0=-30, alt=Math.max(tg.y,0)+330;
  const sx=tg.x-fx0*gap*(N-1)/2, sz=tg.z-fz0*gap*(N-1)/2;
  for(let i=0;i<N;i++){
    const h=alt+i*18;
    const tf=(-vy0+Math.sqrt(vy0*vy0+2*g*h))/g;            // 着弾までの時間
    const vf=52, px=sx+fx0*gap*i+rf(-3,3), pz=sz+fz0*gap*i+rf(-3,3);
    missiles.push({p:[px-fx0*vf*tf, h, pz-fz0*vf*tf], v:[fx0*vf,vy0,fz0*vf], t:14, mp:null, gd:0, bomb:g});
  }
  Snd.whistle(); if(Snd.woosh) Snd.woosh();
  banner('絨毯爆撃','CARPET BOMBING');
  kick(-.01,0);
}
function bombHit(m){
  const x=m.p[0], y=Math.max(1,m.p[1]), z=m.p[2];
  detonate(x,y,z,30,340,1.2);
  efx('ring',x,1.5,z,6,110,.5,0xffd8a0,.8,true);
  setLeanFrom(x,y,z,.35);
}
/* 焼夷弾：放物線で投げ込み、着弾点に火の海を作る。延焼は既存の火災処理に任せる */
function fireIncend(o,dir,hit){
  const tg = hit.miss ? {x:o.x+dir.x*520,y:0,z:o.z+dir.z*520} : hit;
  const dx=tg.x-o.x, dz=tg.z-o.z, dist=Math.hypot(dx,dz)||1;
  const g=60, T=Math.max(1.0,Math.min(3.4,dist/150));
  const vx=dx/T, vz=dz/T, vy=(tg.y-o.y)/T+0.5*g*T;
  missiles.push({p:[o.x+dir.x*4,o.y-1.5,o.z+dir.z*4], v:[vx,vy,vz], t:9, mp:null, gd:0, bomb:g, inc:1});
  efx('ball',o.x+dir.x*6,o.y-1.5,o.z+dir.z*6,1.2,8,.1,0xffc080,1);
  if(Snd.woosh) Snd.woosh(); Snd.rail();
  kick(-.03,(Math.random()-.5)*.01); fovPunch(3);
}
function incendHit(x,y,z){
  detonate(x,y,z,16,150,.8);
  for(let i=0;i<12;i++){
    const a=Math.random()*6.283, r=rf(3,22);
    const px=x+Math.cos(a)*r, pz=z+Math.sin(a)*r;
    if(fires.length<70) fires.push({x:px,y:Math.max(1.5,y),z:pz,t:rf(14,24),r:rf(8,13),src:'fire'});
    vfxFire(px,y+2,pz,rf(5,9),rf(.8,1.6),1.3,Math.cos(a)*rf(4,12),rf(4,10),Math.sin(a)*rf(4,12));
  }
  for(let i=0;i<40;i++) spark(x,y+2,z,rf(-40,40),rf(10,60),rf(-40,40),rf(.6,1.4),1,.55,.15);
  addHot(x,y,z,22,1.2,6);
  glow(x,y+4,z,20,40,[1,.55,.2]);
  efx('disc',x,.5,z,4,46,8,0x120804,.7,true);
  Snd.incend(x,y,z); banner('焼夷弾','INCENDIARY');
}
