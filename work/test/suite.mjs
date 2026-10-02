// TOKYO TEARDOWN headless test suite.  usage: node work/test/suite.mjs <html> [--shots] [--soak]
import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
const file=process.argv[2]; const SHOTS=process.argv.includes('--shots'); const SOAK=process.argv.includes('--soak');
const base=path.basename(file,'.html');
const html=fs.readFileSync(file,'utf8'); const three=fs.readFileSync('work/lib/three.r128.min.js','utf8');
const t0=Date.now(); const results=[]; let page, ctx, browser; let logs=[]; let pageErrors=[];
function rec(name,status,info){ results.push({name,status,info:String(info||'')}); console.log((status==='PASS'?'✅':status==='FAIL'?'❌':'⚠️ ')+' '+status+' '+name+(info?' — '+info:'')); }
async function newPage(vw,vh){
  if(page) await page.close().catch(()=>{});
  ctx=ctx||await browser.newContext({viewport:{width:vw||393,height:vh||852},deviceScaleFactor:1,isMobile:true,hasTouch:true,
    userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1'});
  if(vw) await ctx.close().catch(()=>{}), ctx=await browser.newContext({viewport:{width:vw,height:vh},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  page=await ctx.newPage(); logs=[]; pageErrors=[];
  page.on('console',m=>{ if(m.type()==='error') logs.push(m.text()); });
  page.on('pageerror',e=>pageErrors.push(e.message));
  await page.addInitScript(()=>{ window.TT_DEBUG=true; window.TT_QUALITY='low'; window.__wb=()=>{ const T=window.__tt; for(let i=0;i<300&&T.booting&&T.booting();i++) T.step(1/60); }; });
  await page.route('**/*',async route=>{ const u=route.request().url();
    if(u.includes('three')&&u.endsWith('.js')) return route.fulfill({status:200,contentType:'application/javascript',body:three});
    if(u.startsWith('http://local.test/')) return route.fulfill({status:200,contentType:'text/html',body:html});
    return route.abort(); });
  await page.goto('http://local.test/index.html');
  await page.waitForFunction(()=>window.__tt && document.getElementById('boot') && getComputedStyle(document.getElementById('boot')).display==='none',null,{timeout:150000}).catch(()=>{});
  await page.evaluate(()=>{ try{ window.__tt.setQuality('low'); }catch(e){} });
  return page;
}
const ev=(fn,...args)=>page.evaluate(fn,...args);
async function check(name,fn){ try{ const r=await fn(); if(r===undefined||r===true) rec(name,'PASS'); else if(r&&r.skip) rec(name,'SKIP',r.skip); else if(r&&r.ok===false) rec(name,'FAIL',r.info); else rec(name,'PASS',typeof r==='string'?r:(r&&r.info)||JSON.stringify(r)); }catch(e){ rec(name,'FAIL','exception: '+(e.message||e).slice(0,300)); } }
const STEP=(n,dt)=>ev(({n,dt})=>{ const T=window.__tt; for(let i=0;i<n;i++) T.step(dt); },{n,dt:dt||1/60});
const AIM=()=>ev(()=>{ const T=window.__tt; T.cam.pos.set(0,80,260); T.cam.yaw=0; T.cam.pitch=-0.3; T.updCam(0.016); });
// 建物に当たる向きを探す（地面や空を向いたままにしない）
const AIMB_SRC=`(function(){ const T=window.__tt; T.cam.pos.set(0,70,260); T.cam.yaw=0; for(let p=-0.35;p<=0.15;p+=0.025){ T.cam.pitch=p; T.updCam(0.016); const h=T.aimRay(); if(!h.miss&&!h.ground&&h.d<420) return h.d; } T.cam.pitch=-0.2; T.updCam(0.016); return -1; })()`
browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
await newPage();
await check('1 boot',async()=>{ const r=await ev(()=>({canvas:!!document.querySelector('canvas'),boot:getComputedStyle(document.getElementById('boot')).display,hud:document.getElementById('hud').style.display,tt:!!window.__tt}));
  if(!r.canvas||r.boot!=='none'||!r.tt) return {ok:false,info:JSON.stringify(r)}; if(pageErrors.length) return {ok:false,info:'pageerror: '+pageErrors[0]}; return 'console errors: '+logs.length; });
await check('2 maps generate',async()=>{ const r=await ev(()=>{ const T=window.__tt, out=[]; for(const m of [0,1,2]){ const a=performance.now(); T.genCity(m); __wb(); out.push({m,blds:T.blds.length,tot:T.totalVox(),ms:Math.round(performance.now()-a)}); } return out; });
  if(r.some(x=>x.blds<10||x.tot<1000)) return {ok:false,info:JSON.stringify(r)}; if(pageErrors.length) return {ok:false,info:pageErrors[0]}; return r.map(x=>`map${x.m}:${x.blds}b/${x.tot}v/${x.ms}ms`).join(' '); });
await check('3 hp precision (620/260 kept)',async()=>{ const r=await ev(()=>{ const T=window.__tt; T.genCity(0); __wb(); let m42=0,ok42=0,m21=0,ok21=0,over=0; for(const b of T.blds) for(let i=0;i<b.vox.length;i++){ const m=b.vox[i]; if(!m) continue; if(b.hp[i]>T.MATS[m].hp) over++; if(m===42){m42++; if(b.hp[i]===620) ok42++;} if(m===21){m21++; if(b.hp[i]===260) ok21++;} } return {m42,ok42,m21,ok21,over,type:T.blds[0].hp.constructor.name}; });
  if(r.m42&&r.ok42!==r.m42) return {ok:false,info:JSON.stringify(r)}; if(r.m21&&r.ok21!==r.m21) return {ok:false,info:JSON.stringify(r)}; if(r.over) return {ok:false,info:'hp over max '+r.over}; return JSON.stringify(r); });
const WEAPONS=['missile','rail','cutter','grav','orbit','demo','meteor','ball','orb','nuke'];
for(const w of WEAPONS){
  await check('4 weapon '+w,async()=>{ const r=await ev(async([w,AIMB])=>{ const T=window.__tt; T.genCity(0); __wb(); eval(AIMB); T.selW(w); T.setCd(0); const k0=T.killedVox(); const s0=T.S.score;
      if(w==='rail'){ for(let i=0;i<60;i++) T.railTick(1/60); }
      else if(w==='cutter'){ const d=[0,-0.3,-0.95]; T.doCut(T.camera().position,[d[0]*0.97-d[2]*0.26,d[1],d[0]*0.26+d[2]*0.97],[d[0]*0.97+d[2]*0.26,d[1],-d[0]*0.26+d[2]*0.97]); }
      else if(w==='demo'){ const h=T.aimRay(); T.placeCharge(h.x,h.y+1,h.z); T.placeCharge(h.x+6,h.y+1,h.z); T.blowCharges(); }
      else T.fireWeapon();
      const secs={grav:8,meteor:9,orb:16,nuke:9,orbit:5}[w]||4;
      for(let i=0;i<60*secs;i++) T.step(1/60);
      const out={killed:T.killedVox()-k0, dscore:T.S.score-s0, chunks:T.chunkCount()};
      T.selW('missile'); T.setCd(0); T.fireWeapon(); for(let i=0;i<120;i++) T.step(1/60); out.back=T.killedVox()-k0-out.killed;
      return out; },[w,AIMB_SRC]);
    if(pageErrors.length) return {ok:false,info:'pageerror: '+pageErrors.join(' | ').slice(0,300)}; if(r.killed<=0) return {ok:false,info:'no destruction '+JSON.stringify(r)}; return JSON.stringify(r); });
}
await check('5 zero score for nuke/orb',async()=>{ const r=await ev(()=>{ const T=window.__tt, out={}; for(const w of ['nuke','orb']){ T.genCity(0); __wb(); T.cam.pos.set(0,80,260); T.cam.yaw=0; T.cam.pitch=-0.3; T.updCam(0.016); T.selW(w); T.setCd(0); const s0=T.S.score, n0=T.TALLY.nuke; T.fireWeapon(); for(let i=0;i<60*14;i++) T.step(1/60); out[w]={dscore:T.S.score-s0, nukeTally:T.TALLY.nuke-n0, otherTally:T.TALLY.wpn+T.TALLY.collapse+T.TALLY.fire+T.TALLY.chain+T.TALLY.domino}; }
    T.genCity(0); __wb(); T.cam.pos.set(0,80,260); T.cam.yaw=0; T.cam.pitch=-0.3; T.updCam(0.016); T.selW('missile'); T.setCd(0); const s1=T.S.score; T.fireWeapon(); for(let i=0;i<180;i++) T.step(1/60); out.missile={dscore:T.S.score-s1}; return out; });
  if(r.nuke.dscore!==0||r.orb.dscore!==0) return {ok:false,info:JSON.stringify(r)}; if(r.missile.dscore<=0) return {ok:false,info:'missile no score '+JSON.stringify(r)}; return JSON.stringify(r); });
await check('6 rail damage independent of call count',async()=>{ const r=await ev((AIMB)=>{ const T=window.__tt; const run=(n)=>{ T.genCity(0,12345); __wb(); eval(AIMB); const a=T.killedVox(); for(let i=0;i<n;i++) T.railTick(1/n); return T.killedVox()-a; }; return {n30:run(30),n120:run(120)}; },AIMB_SRC);
  const ratio=r.n120/Math.max(1,r.n30); if(ratio>1.6||ratio<0.6) return {ok:false,info:JSON.stringify(r)+' ratio '+ratio.toFixed(2)}; return JSON.stringify(r); });
await check('6b chunk damping independent of dt',async()=>{ const r=await ev(()=>{ const T=window.__tt; const run=(dt)=>{ T.genCity(0,777); __wb(); T.detonate(0,10,0,40,500); let maxV=0; for(let t=0;t<3;t+=dt){ T.step(dt); for(const c of T.chunks) maxV=Math.max(maxV,Math.hypot(c.v[0],c.v[1],c.v[2])); } let sleeping=0; for(const c of T.chunks) if(c.sleep) sleeping++; return {maxV:Math.round(maxV),n:T.chunkCount(),sleeping,killed:T.killedVox()}; }; return {dt30:run(1/30),dt120:run(1/120)}; });
  return JSON.stringify(r); });
await check('7 live integrity after heavy destruction',async()=>{ const r=await ev(()=>{ const T=window.__tt; T.genCity(0); __wb(); for(let i=0;i<8;i++){ T.detonate(-60+i*25,12,20,45,500); for(let s=0;s<40;s++) T.step(1/60); } for(let s=0;s<600;s++) T.step(1/60); let neg=0,mis=0,over=0; for(const b of T.blds){ if(b.live<0) neg++; let n=0; for(let i=0;i<b.vox.length;i++){ if(b.vox[i]){ n++; if(b.hp[i]>T.MATS[b.vox[i]].hp) over++; } } if(n!==b.live) mis++; } let cm=0; for(const c of T.chunks){ let n=0; for(let i=0;i<c.vox.length;i++) if(c.vox[i]) n++; if(n!==c.live) cm++; } return {neg,mis,over,cm,killed:T.killedVox(),total:T.totalVox(),chunks:T.chunkCount()}; });
  if(r.neg||r.mis||r.over||r.cm||r.killed>r.total) return {ok:false,info:JSON.stringify(r)}; return JSON.stringify(r); });
await check('8 modes: 60s timer and 3 shots',async()=>{ const r=await ev(()=>{ const T=window.__tt, out={}; T.setMode('time'); T.genCity(0); __wb(); T.cam.pos.set(0,80,260); T.cam.yaw=0; T.cam.pitch=-0.3; T.updCam(0.016); T.selW('missile'); T.setCd(0); T.fireWeapon();
    const rs0=T.runState(); out.startedAfterShot=rs0.runStarted; // タイマーは実時間なので step では進まない（loop の実時間が進める）
    out.clockHook=!!T.clock; T.setMode('shots'); T.genCity(0); __wb(); T.cam.pos.set(0,80,260); T.updCam(0.016); for(let i=0;i<3;i++){ T.setCd(0); T.fireWeapon(); for(let s=0;s<30;s++) T.step(1/60); } out.canShootAfter3=T.canShoot(); for(let s=0;s<60*14;s++) T.step(1/60); out.runOver=T.runState().runOver; out.resultOn=T.runState().resultOn; T.hideResult(); T.setMode('free'); T.genCity(0); __wb(); return out; });
  if(!r.startedAfterShot||r.canShootAfter3||!r.runOver) return {ok:false,info:JSON.stringify(r)}; return JSON.stringify(r); });
await check('8b 60s timer runs on real time',async()=>{ await ev(()=>{ const T=window.__tt; T.setMode('time'); T.genCity(0); __wb(); T.cam.pos.set(0,80,260); T.cam.yaw=0; T.cam.pitch=-0.3; T.updCam(0.016); T.selW('missile'); T.setCd(0); T.fireWeapon(); }); const raf2=()=>ev(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))); await raf2(); const a=await ev(()=>window.__tt.runState().runLeft); await page.waitForTimeout(2500); await raf2(); const b=await ev(()=>window.__tt.runState().runLeft); await ev(()=>{ const T=window.__tt; T.setMode('free'); T.genCity(0); __wb(); });
  const d=a-b; if(!(d>1.5&&d<9)) return {ok:false,info:`runLeft ${a}->${b} in 2.5s`}; return `runLeft ${a.toFixed(1)}->${b.toFixed(1)} in 2.5s`; });
await check('9 regen stability + resources',async()=>{ const r=await ev(()=>{ const T=window.__tt, res=[]; for(let k=0;k<2;k++) for(const m of [0,1,2]){ T.genCity(m); __wb(); T.cam.pos.set(0,80,260); T.cam.yaw=0; T.cam.pitch=-0.3; T.updCam(0.016); T.selW('nuke'); T.setCd(0); T.fireWeapon(); for(let s=0;s<60*5;s++) T.step(1/60); T.selW('grav'); T.setCd(0); T.fireWeapon(); for(let s=0;s<60*4;s++) T.step(1/60); res.push(T.resources?T.resources():null); } T.genCity(0); __wb(); for(let s=0;s<60;s++) T.step(1/60); res.push(T.resources?T.resources():null); return {res,chunks:T.chunkCount(),mem:performance.memory?Math.round(performance.memory.usedJSHeapSize/1048576):null}; });
  if(pageErrors.length) return {ok:false,info:pageErrors.join('|').slice(0,300)}; const g=r.res.filter(Boolean).map(x=>x.geometries+'g/'+x.textures+'t'); return 'geo/tex per cycle: '+g.join(' ')+' heapMB '+r.mem; });
await check('10 quality toggle restores pixel ratio',async()=>{ const r=await ev(()=>{ const T=window.__tt; const pr0=T.pixelRatio?T.pixelRatio():null; T.setQuality('high'); const prH=T.pixelRatio?T.pixelRatio():null; T.setQuality('low'); const prL=T.pixelRatio?T.pixelRatio():null; const lvL=T.QUAL().level; T.setQuality('high'); const prH2=T.pixelRatio?T.pixelRatio():null; const q=T.QUAL(); return {pr0,prH,prL,prH2,mode:q.mode,lvH:q.level,lvL,dpr:window.devicePixelRatio}; });
  if(r.prH==null) return {skip:'no pixelRatio hook'}; if(r.mode!=='high'||Math.abs(r.prH-r.prH2)>1e-6||!(r.prL<=r.prH)||r.lvH!==0||r.lvL!==2) return {ok:false,info:JSON.stringify(r)}; return JSON.stringify(r); });
await check('11 input: two fingers (stick + fire), pointercancel releases',async()=>{
  await ev(()=>{ const T=window.__tt; T.genCity(0); __wb(); for(let i=0;i<150&&T.booting();i++) T.step(1/60); T.selW('missile'); T.setCd(0); });
  const r=await ev(()=>{ const T=window.__tt; const st=document.getElementById('stick'), fb=document.getElementById('fire'); const sr=st.getBoundingClientRect(), fr=fb.getBoundingClientRect();
    const pe=(type,el,id,x,y)=>el.dispatchEvent(new PointerEvent(type,{pointerId:id,pointerType:'touch',isPrimary:id===1,clientX:x,clientY:y,bubbles:true,cancelable:true}));
    const cx=sr.left+sr.width/2, cy=sr.top+sr.height/2;
    pe('pointerdown',st,1,cx,cy); pe('pointermove',window,1,cx,cy-40);
    const fwdHeld=T.inp().fwd;
    pe('pointerdown',fb,2,fr.left+fr.width/2,fr.top+fr.height/2);
    const held=T.fireHeld?T.fireHeld():null;
    pe('pointermove',window,2,fr.left+fr.width/2+30,fr.top+fr.height/2);
    pe('pointercancel',window,2,0,0);
    const heldAfterCancel=T.fireHeld?T.fireHeld():null;
    pe('pointerup',window,1,cx,cy-40);
    const fwdAfter=T.inp().fwd;
    return {fwdHeld,held,heldAfterCancel,fwdAfter,ptr:T.ptr?T.ptr().length:null,booting:T.booting()}; });
  if(r.held==null) return {skip:'no fireHeld hook: '+JSON.stringify(r)}; if(!(r.fwdHeld>0.3)||!r.held||r.heldAfterCancel||r.fwdAfter!==0||r.ptr!==0) return {ok:false,info:JSON.stringify(r)}; return JSON.stringify(r); });
await check('12 pause blocks firing; same-seed regen is identical',async()=>{ const r=await ev(()=>{ const T=window.__tt; if(!T.setPaused||!T.seed) return {skip:true}; T.genCity(0,4242); __wb(); const sig=()=>{ let h=0; for(const b of T.blds){ h=(h*31+b.live)|0; h=(h*31+b.W)|0; } return h; }; const s1=sig(); T.genCity(0,4242); __wb(); const s2=sig(); T.genCity(0); __wb(); const s3=sig(); T.setPaused(true); const canFirePaused=T.canShoot(); T.setPaused(false); return {same:s1===s2,differentNewSeed:s1!==s3,canFirePaused,seed:T.seed()}; });
  if(r.skip) return {skip:'no seed hooks'}; if(!r.same||!r.differentNewSeed) return {ok:false,info:JSON.stringify(r)}; return JSON.stringify(r); });
if(SHOTS){
  await check('13 screenshots',async()=>{ fs.mkdirSync('work/test/shots',{recursive:true}); await ev(()=>{ const T=window.__tt; T.setQuality('high'); T.genCity(0); __wb(); T.spawnOverview(); }); await page.waitForTimeout(3000); await page.screenshot({path:`work/test/shots/${base}_portrait.png`,timeout:120000});
    await ev(()=>{ const T=window.__tt; T.selW('missile'); T.setCd(0); T.fireWeapon(); for(let i=0;i<90;i++) T.step(1/60); }); await page.waitForTimeout(1500); await page.screenshot({path:`work/test/shots/${base}_hit.png`,timeout:120000});
    await newPage(852,393); await ev(()=>{ const T=window.__tt; T.setQuality('high'); T.genCity(1); __wb(); T.spawnOverview(); }); await page.waitForTimeout(3000); await page.screenshot({path:`work/test/shots/${base}_landscape.png`,timeout:120000}); await newPage(); return 'saved'; });
}
if(SOAK){
  await check('14 soak 60s cycling all weapons',async()=>{ const r=await ev(async()=>{ const T=window.__tt; T.genCity(0); __wb(); const W=['missile','rail','cutter','grav','orbit','demo','meteor','ball','orb','nuke']; let k=0, worst=0; const a=performance.now(); while(performance.now()-a<60000){ T.cam.pos.set((Math.random()-.5)*200,80,260); T.cam.yaw=(Math.random()-.5)*.6; T.cam.pitch=-0.3; T.updCam(0.016); T.selW(W[k++%W.length]); T.setCd(0); T.fireWeapon(); if(W[(k-1)%W.length]==='rail') for(let i=0;i<30;i++) T.railTick(1/60); if(W[(k-1)%W.length]==='demo') T.blowCharges(); const b=performance.now(); for(let i=0;i<120;i++) T.step(1/60); worst=Math.max(worst,(performance.now()-b)/120); await new Promise(r=>setTimeout(r,50)); } return {shots:k,worstStepMs:worst.toFixed(1),chunks:T.chunkCount(),killed:T.killedVox(),res:T.resources?T.resources():null}; });
    if(pageErrors.length) return {ok:false,info:pageErrors.join('|').slice(0,300)}; return JSON.stringify(r); });
}
rec('console errors total',logs.length?'FAIL':'PASS',logs.slice(0,3).join(' | ').slice(0,300));
rec('page errors total',pageErrors.length?'FAIL':'PASS',pageErrors.slice(0,3).join(' | ').slice(0,300));
const summary={file,results,ms:Date.now()-t0}; fs.writeFileSync(`work/test/report_${base}.json`,JSON.stringify(summary,null,1));
console.log('done in '+((Date.now()-t0)/1000).toFixed(0)+'s  PASS '+results.filter(r=>r.status==='PASS').length+' FAIL '+results.filter(r=>r.status==='FAIL').length+' SKIP '+results.filter(r=>r.status==='SKIP').length);
await browser.close();
