(async(N)=>{
  const T=window.__tt; T.setQuality('high');
  T.genCity(2);
  let best=null; for(const b of T.blds){ if(b.style==='tower'&&b.H>90&&(!best||b.init>best.init)) best=b; }
  const cx=best.ox+best.W*T.VOX/2, cz=best.oz+best.D*T.VOX/2, W=best.W*T.VOX;
  // 塔の南側から見上げる位置
  T.cam.pos.set(cx+10, 60, cz+230); T.cam.yaw=0; T.cam.pitch=0.12; T.updCam(0.016);
  for(let k=0;k<4;k++) T.damageSphere(best.ox+W*0.28, 6+k*8, cz, W*0.55, 6000);
  let seen=false, maxAng=0, poseChunks=0;
  for(let i=0;i<N;i++){ T.step(1/60); if(best.toppling){ seen=true; maxAng=Math.max(maxAng,best.toppling.ang); }
    for(const c of T.chunks) if((Math.abs(c.q[0])+Math.abs(c.q[2]))>0.03 && c.live>800) poseChunks++; }
  await new Promise(r=>setTimeout(r,1500));
  return {N, seen, maxAng:+maxAng.toFixed(3), poseChunks, chunks:T.chunkCount(), live:best.live, toppling:!!best.toppling, dirty:best.dirty};
})
