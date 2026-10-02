(async()=>{
  const T=window.__tt; if(!T) return 'no __tt';
  const r={};
  // 1. HP precision
  T.genCity(0);
  let m42=0,m21=0,ok42=0,ok21=0,maxOver=0;
  for(const b of T.blds){ for(let i=0;i<b.vox.length;i++){ const m=b.vox[i]; if(!m) continue;
    if(b.hp[i]>T.MATS[m].hp) maxOver=Math.max(maxOver,b.hp[i]-T.MATS[m].hp);
    if(m===42){ m42++; if(b.hp[i]===620) ok42++; } if(m===21){ m21++; if(b.hp[i]===260) ok21++; } } }
  r.hp={m42,ok42,m21,ok21,maxOver,hpType:T.blds[0].hp.constructor.name};
  // 2. singularity tear
  T.cam.pos.set(0,80,260); T.cam.yaw=0; T.cam.pitch=-0.3; T.updCam(0.016);
  T.selW('grav'); T.setCd(0); const k0=T.killedVox(); T.fireWeapon();
  let maxChunks=0; for(let i=0;i<60*7;i++){ T.step(1/60); maxChunks=Math.max(maxChunks,T.chunkCount()); }
  let negLive=0, liveMismatch=0; for(const b of T.blds){ if(b.live<0) negLive++; let n=0; for(let i=0;i<b.vox.length;i++) if(b.vox[i]) n++; if(n!==b.live) liveMismatch++; }
  r.grav={maxChunks,killed:T.killedVox()-k0,negLive,liveMismatch,attrLeft:!!T.getAttr()};
  // 3. rail independence
  const railTest=(n,total)=>{ T.genCity(0); T.cam.pos.set(0,60,260); T.cam.yaw=0; T.cam.pitch=-0.2; T.updCam(0.016);
    const a=T.killedVox(); for(let i=0;i<n;i++) T.railTick(total/n); return T.killedVox()-a; };
  r.rail={n30:railTest(30,1.0), n120:railTest(120,1.0)};
  // 4. live integrity after detonations
  T.genCity(0); for(let i=0;i<6;i++){ T.detonate(-40+i*30,10,0,40,400); for(let s=0;s<60;s++) T.step(1/60); }
  for(let s=0;s<600;s++) T.step(1/60);
  negLive=0; liveMismatch=0; let over=0; for(const b of T.blds){ if(b.live<0) negLive++; let n=0; for(let i=0;i<b.vox.length;i++){ if(b.vox[i]){ n++; if(b.hp[i]>T.MATS[b.vox[i]].hp) over++; } } if(n!==b.live) liveMismatch++; }
  let cneg=0; for(const c of T.chunks){ let n=0; for(let i=0;i<c.vox.length;i++) if(c.vox[i]) n++; if(n!==c.live) cneg++; }
  r.integrity={negLive,liveMismatch,over,chunkMismatch:cneg,chunks:T.chunkCount(),killed:T.killedVox(),total:T.totalVox(),rubble:T.rubble()};
  r.qual=T.QUAL().level+'/'+T.QUAL().mode+' pr='+T.QUAL().pr.toFixed(2);
  return r;
})()
