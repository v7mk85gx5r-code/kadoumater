import { chromium } from 'playwright'; import fs from 'fs';
const html=fs.readFileSync('work/TOKYO_TEARDOWN_iPhone17_Enhanced.html','utf8'); const three=fs.readFileSync('work/lib/three.r128.min.js','utf8');
const browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:393,height:852},deviceScaleFactor:1,isMobile:true,hasTouch:true});
const page=await ctx.newPage(); const errs=[]; page.on('pageerror',e=>errs.push(e.message));
await page.addInitScript(()=>{ window.TT_DEBUG=true; window.TT_QUALITY='low'; });
await page.route('**/*',async route=>{ const u=route.request().url();
  if(u.includes('three')&&u.endsWith('.js')) return route.fulfill({status:200,contentType:'application/javascript',body:three});
  if(u.startsWith('http://local.test/')) return route.fulfill({status:200,contentType:'text/html',body:html}); return route.abort(); });
await page.goto('http://local.test/index.html');
await page.waitForFunction(()=>window.__tt&&!window.__tt.booting(),null,{timeout:150000}).catch(()=>{});
// 初回起動の視点がマップの初期視点になっているか（spawnOverview が呼ばれている）
const view=await page.evaluate(()=>{ const T=window.__tt; return {x:+T.cam.pos.x.toFixed(1),y:+T.cam.pos.y.toFixed(1),z:+T.cam.pos.z.toFixed(1),pitch:+T.cam.pitch.toFixed(3),map:T.MAPID()}; });
// 構築中にバックグラウンドへ行っても構築が進み、復帰で再開できる
const bootPause=await page.evaluate(async()=>{ const T=window.__tt; T.genCity(1); const b0=T.booting(); T.setPaused(true,'bg');
  const t0=performance.now(); while(T.booting()&&performance.now()-t0<60000) await new Promise(r=>setTimeout(r,200));
  const bootHidden=getComputedStyle(document.getElementById('boot')).display==='none';
  const menuOn=document.getElementById('pmenu').classList.contains('on');
  document.getElementById('pmResume').click();
  return {b0, bootingAfter:T.booting(), bootHidden, menuOn, pausedAfterResume:T.isPaused(), canShoot:T.canShoot()}; });
// 結果画面中にポーズ→結果のボタンで再開される
const resPause=await page.evaluate(()=>{ const T=window.__tt; T.showResult(); T.setPaused(true,'bg'); const p1=T.isPaused(); document.getElementById('rNewCity').click(); return {p1, pausedAfter:T.isPaused(), resultOn:T.runState().resultOn, booting:T.booting()}; });
await page.waitForFunction(()=>!window.__tt.booting(),null,{timeout:120000}).catch(()=>{});
// FIRE の指：別の指が視点中は位置だけ追う
const fireAnchor=await page.evaluate(()=>{ const T=window.__tt; const fb=document.getElementById('fire'), fr=fb.getBoundingClientRect();
  const pe=(type,el,id,x,y)=>el.dispatchEvent(new PointerEvent(type,{pointerId:id,pointerType:'touch',isPrimary:id===1,clientX:x,clientY:y,bubbles:true,cancelable:true}));
  T.selW('rail'); const yaw0=T.cam.yaw;
  pe('pointerdown',fb,2,fr.left+50,fr.top+50);                 // 指2: FIRE
  pe('pointerdown',document.body,1,150,300);                     // 指1: 視点
  pe('pointermove',window,2,fr.left+50+80,fr.top+50);            // FIRE指を80px動かす（視点は指1が持つので無視されるが位置は追う）
  pe('pointerup',window,1,150,300);                              // 指1を離す
  const yawMid=T.cam.yaw;
  pe('pointermove',window,2,fr.left+50+82,fr.top+50);            // FIRE指をさらに2px
  const yawAfter=T.cam.yaw; pe('pointerup',window,2,fr.left+50+82,fr.top+50);
  return {jump:+Math.abs(yawAfter-yawMid).toFixed(4), yawMoved:+Math.abs(yawMid-yaw0).toFixed(4)}; });
console.log(JSON.stringify({view,bootPause,resPause,fireAnchor,errs:errs.slice(0,3)}));
await browser.close();
