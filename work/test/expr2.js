(async()=>{
  const T=window.__tt;
  T.genCity(0);
  const chk=(tag)=>{ const bad=[]; for(const b of T.blds){ let n=0; for(let i=0;i<b.vox.length;i++) if(b.vox[i]) n++; if(n!==b.live) bad.push({id:b.id,style:b.style,live:b.live,n:n,init:b.init,W:b.W,H:b.H,D:b.D}); } return {tag,bad}; };
  const out=[chk('fresh')];
  for(let i=0;i<6;i++){ T.detonate(-40+i*30,10,0,40,400); out.push(chk('det'+i)); for(let s=0;s<60;s++){ T.step(1/60); } out.push(chk('step'+i)); }
  return out.filter(o=>o.bad.length).slice(0,6);
})()
