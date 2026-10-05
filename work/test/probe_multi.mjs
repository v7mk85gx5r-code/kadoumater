// PC build multi-step probe: boots once, then runs steps from a JSON file [{name, expr, wait, shot}].
// usage: VW=1920 VH=1080 node work/test/probe_multi.mjs file.html steps.json [quality]
import { chromium } from 'playwright';
import fs from 'fs';
const file=process.argv[2], steps=JSON.parse(fs.readFileSync(process.argv[3],'utf8')), qual=process.argv[4]||'high';
const html=fs.readFileSync(file,'utf8');
const browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:+(process.env.VW||1920),height:+(process.env.VH||1080)},deviceScaleFactor:+(process.env.DPR||1)});
const page=await ctx.newPage(); let logs=[];
page.on('console',m=>{ if(m.type()==='error'||m.type()==='warning') logs.push('['+m.type()+'] '+m.text().slice(0,300)); });
page.on('pageerror',e=>logs.push('[pageerror] '+e.message));
await page.addInitScript((q)=>{ window.TT_DEBUG=true; window.TT_NOLOCK=true; window.TT_QUALITY=q; window.__wb=()=>{ const T=window.__tt; for(let i=0;i<400&&T.booting&&T.booting();i++) T.step(1/60); }; },qual);
await page.route('**/*',async route=>{ const u=route.request().url();
  if(u.startsWith('http://local.test/')) return route.fulfill({status:200,contentType:'text/html',body:html});
  return route.abort(); });
const t0=Date.now();
await page.goto('http://local.test/index.html');
await page.waitForFunction(()=>window.__tt && document.getElementById('boot') && getComputedStyle(document.getElementById('boot')).display==='none',null,{timeout:900000}).catch(()=>{ console.log('boot wait timed out'); });
console.log('boot ms', Date.now()-t0);
for(const s of steps){
  const t1=Date.now(); let out;
  try{ out=await page.evaluate(s.expr); }catch(e){ out='EVAL ERROR: '+e.message; }
  if(s.wait) await page.waitForTimeout(s.wait);
  if(s.shot){ try{ await page.screenshot({path:s.shot,timeout:300000,animations:'disabled'}); }catch(e){ out={out, shotError:e.message.slice(0,200)}; } }
  console.log('=== '+s.name+' ('+(Date.now()-t1)+' ms)'); console.log(JSON.stringify(out,null,1));
  const errs=logs.filter(l=>!/AudioContext/.test(l)); console.log('logs:', errs.length? errs.slice(0,20).join('\n'):'(none)'); logs=[];
}
await browser.close(); console.log('DONE');
