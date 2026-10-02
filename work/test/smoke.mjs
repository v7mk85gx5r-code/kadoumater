// Headless smoke test: serve HTML, intercept three.js CDN to local copy, check WebGL + console errors.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
const file = process.argv[2] || 'work/original.html';
const html = fs.readFileSync(file, 'utf8');
const three = fs.readFileSync('work/lib/three.r128.min.js', 'utf8');
const browser = await chromium.launch({ headless: true, args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ viewport: { width: 393, height: 852 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1' });
const page = await ctx.newPage();
const logs = [];
page.on('console', m => logs.push(`[${m.type()}] ${m.text()}`));
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.route('**/*', async route => {
  const u = route.request().url();
  if (u.includes('three') && u.endsWith('.js')) return route.fulfill({ status: 200, contentType: 'application/javascript', body: three });
  if (u.startsWith('http://local.test/')) return route.fulfill({ status: 200, contentType: 'text/html', body: html });
  return route.abort();
});
await page.goto('http://local.test/index.html');
await page.waitForTimeout(12000);
const info = await page.evaluate(() => {
  const c = document.querySelector('canvas');
  const boot = document.getElementById('boot');
  return { hasCanvas: !!c, bootDisplay: boot && getComputedStyle(boot).display, bootMsg: document.getElementById('bootMsg')?.textContent, hud: document.getElementById('hud')?.style.display, tt: typeof window.__tt, err: document.getElementById('err')?.textContent };
});
console.log(JSON.stringify(info, null, 2));
console.log(logs.slice(0, 40).join('\n'));
await page.screenshot({ path: 'work/test/shot_' + path.basename(file, '.html') + '.png' });
await browser.close();
