(async()=>{
  const T=window.__tt; T.setQuality('high');
  T.genCity(2);
  let best=null; for(const b of T.blds){ if(b.style==='tower'&&b.H>90&&(!best||b.init>best.init)) best=b; }
  if(!best) return 'no tower';
  const cz=best.oz+best.D*T.VOX/2, W=best.W*T.VOX;
  for(let k=0;k<4;k++) T.damageSphere(best.ox+W*0.28, 6+k*8, cz, W*0.55, 6000);
  let topplingSeen=false, maxAng=0, poseChunks=0, cutDone=false;
  for(let i=0;i<60*8;i++){ T.step(1/60);
    if(best.toppling){ topplingSeen=true; maxAng=Math.max(maxAng,best.toppling.ang); }
    if(best.toppled&&!best.toppling) cutDone=true;
    for(const c of T.chunks) if((Math.abs(c.q[0])+Math.abs(c.q[2]))>0.03 && c.live>800) poseChunks++;
  }
  return {toppled:!!best.toppled, topplingSeen, maxAng:+maxAng.toFixed(3), cutDone, poseChunks, live:best.live, init:best.init, chunks:T.chunkCount(), killed:T.killedVox()};
})()
