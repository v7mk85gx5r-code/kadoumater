// 完全オフライン（ページ以外の通信をすべて遮断）で起動できるか
import { chromium } from 'playwright'; import fs from 'fs';
const html=fs.readFileSync(process.argv[2],'utf8');
const browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:393,height:852},deviceScaleFactor:1,isMobile:true,hasTouch:true});
const page=await ctx.newPage(); const errs=[], reqs=[];
page.on('pageerror',e=>errs.push(e.message)); page.on('console',m=>{ if(m.type()==='error') errs.push(m.text()); });
await page.addInitScript(()=>{ window.TT_DEBUG=true; window.TT_QUALITY='low'; });
await page.route('**/*',async route=>{ const u=route.request().url(); if(u.startsWith('http://local.test/')) return route.fulfill({status:200,contentType:'text/html',body:html}); reqs.push(u); return route.abort(); });
await page.goto('http://local.test/index.html');
const t0=Date.now();
await page.waitForFunction(()=>window.__tt&&!window.__tt.booting(),null,{timeout:150000}).catch(()=>{});
const r=await page.evaluate(()=>({three:window.THREE&&window.THREE.REVISION, boot:getComputedStyle(document.getElementById('boot')).display, nojs:getComputedStyle(document.getElementById('bootNoJs')).display, hud:document.getElementById('hud').style.display, blds:window.__tt?window.__tt.blds.length:-1}));
console.log(JSON.stringify({...r, bootMs:Date.now()-t0, externalRequests:reqs, errs:errs.slice(0,3)}));
await browser.close();
