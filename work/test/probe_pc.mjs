// PC build quick probe: desktop viewport, no pointer lock, TT_DEBUG. usage: node work/test/probe_pc.mjs file.html "expr" [ms] [shot.png] [quality]
import { chromium } from 'playwright';
import fs from 'fs';
const file=process.argv[2], expr=process.argv[3], wait=+(process.argv[4]||8000), shot=process.argv[5], qual=process.argv[6]||'low';
const html=fs.readFileSync(file,'utf8');
const browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:+(process.env.VW||1920),height:+(process.env.VH||1080)},deviceScaleFactor:1});
const page=await ctx.newPage(); const logs=[];
page.on('console',m=>{ if(m.type()==='error'||m.type()==='warning') logs.push('['+m.type()+'] '+m.text().slice(0,300)); });
page.on('pageerror',e=>logs.push('[pageerror] '+e.message));
await page.addInitScript((q)=>{ window.TT_DEBUG=true; window.TT_NOLOCK=true; window.TT_QUALITY=q; window.__wb=()=>{ const T=window.__tt; for(let i=0;i<400&&T.booting&&T.booting();i++) T.step(1/60); }; },qual);
await page.route('**/*',async route=>{ const u=route.request().url();
  if(u.startsWith('http://local.test/')) return route.fulfill({status:200,contentType:'text/html',body:html});
  return route.abort(); });
await page.goto('http://local.test/index.html');
await page.waitForFunction(()=>window.__tt && document.getElementById('boot') && getComputedStyle(document.getElementById('boot')).display==='none',null,{timeout:900000}).catch(()=>{});
await page.waitForTimeout(wait);
let out; try{ out=await page.evaluate(expr); }catch(e){ out='EVAL ERROR: '+e.message; }
console.log(JSON.stringify(out,null,1)); console.log(logs.slice(0,30).join('\n'));
if(shot) await page.screenshot({path:shot,timeout:150000,animations:'disabled'});
await browser.close();
