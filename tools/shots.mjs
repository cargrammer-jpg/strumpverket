// Usage: node tools/shots.mjs <baseUrl> <outDir> <prefix>
import { createRequire } from 'module';
const require = createRequire('/tmp/svtools/');
const { chromium } = require('playwright-core');
const [,, base, out, prefix] = process.argv;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
for (const w of [1440, 390]) {
  const ctx = await b.newContext({ viewport: { width: w, height: w === 390 ? 844 : 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
  const p = await ctx.newPage();
  const errs = [];
  p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + m.text()); });
  p.on('pageerror', e => errs.push('pageerror: ' + e.message));
  p.on('requestfailed', r => errs.push('failed: ' + r.url()));
  p.on('response', r => { if (r.status() >= 400) errs.push(r.status() + ' ' + r.url()); });
  await p.goto(base, { waitUntil: 'networkidle' });
  await p.waitForTimeout(2600);
  await p.screenshot({ path: `${out}/${prefix}-${w}-fold.png` });
  // scroll through to trigger reveals
  const h = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < h; y += 500) { await p.evaluate(y => window.scrollTo(0, y), y); await p.waitForTimeout(120); }
  await p.waitForTimeout(1200);
  await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(400);
  await p.screenshot({ path: `${out}/${prefix}-${w}-full.png`, fullPage: true });
  const vid = await p.evaluate(() => { const v = document.querySelector('video'); return { paused: v.paused, src: v.currentSrc, t: v.currentTime }; });
  console.log(w, 'height', h, 'video', JSON.stringify(vid), 'errors', JSON.stringify(errs));
  if (w === 390) {
    // cart flow test
    await p.click('#strumpor form[data-product="vardag"] button[type=submit]');
    await p.waitForTimeout(400);
    await p.click('[data-open-cart]'); await p.waitForTimeout(700);
    await p.click('[data-checkout]'); await p.waitForTimeout(300);
    await p.screenshot({ path: `${out}/${prefix}-390-cart.png` });
    const c = await p.evaluate(() => ({ count: document.querySelector('.cart-count').textContent, open: document.getElementById('varukorg').open, notice: !document.querySelector('.cart__notice').hidden }));
    console.log('cart', JSON.stringify(c));
  }
  await ctx.close();
}
// reduced motion check
const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
const p = await ctx.newPage(); await p.goto(base, { waitUntil: 'networkidle' }); await p.waitForTimeout(1500);
console.log('reduced-motion video paused:', await p.evaluate(() => document.querySelector('video').paused));
await b.close();
