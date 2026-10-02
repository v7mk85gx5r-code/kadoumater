// Quick probe: boot with TT_DEBUG, run a script of __tt calls, print JSON. usage: node probe.mjs file.html "js expression returning JSON-able" [ms]
import { chromium } from 'playwright';
import fs from 'fs';
const file=process.argv[2], expr=process.argv[3], wait=+(process.argv[4]||8000);
const html=fs.readFileSync(file,'utf8'); const three=fs.readFileSync('work/lib/three.r128.min.js','utf8');
const browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:+(process.env.VW||393),height:+(process.env.VH||852)},deviceScaleFactor:2,isMobile:true,hasTouch:true});
const page=await ctx.newPage(); const logs=[];
page.on('console',m=>{ if(m.type()==='error'||m.type()==='warning') logs.push('['+m.type()+'] '+m.text()); });
page.on('pageerror',e=>logs.push('[pageerror] '+e.message));
await page.addInitScript(()=>{ window.TT_DEBUG=true; });
await page.route('**/*',async route=>{ const u=route.request().url();
  if(u.includes('three')&&u.endsWith('.js')) return route.fulfill({status:200,contentType:'application/javascript',body:three});
  if(u.startsWith('http://local.test/')) return route.fulfill({status:200,contentType:'text/html',body:html});
  return route.abort(); });
await page.goto('http://local.test/index.html'); await page.waitForTimeout(wait);
let out; try{ out=await page.evaluate(expr); }catch(e){ out='EVAL ERROR: '+e.message; }
console.log(JSON.stringify(out,null,1)); console.log(logs.slice(0,30).join('\n'));
if(process.argv[5]) await page.screenshot({path:process.argv[5],timeout:150000,animations:'disabled'});
await browser.close();
