/**
 * Render tiap artboard .dc.html jadi PNG 2x di design/export/.
 *
 * Dipakai supaya Ferry dan PDK tidak perlu buka canvas — dan supaya
 * layar-layar ini bisa diseret ke Figma / ditempel ke deck.
 *
 *   node scripts/render_design.js
 *
 * Butuh Chromium yang sudah terpasang (PLAYWRIGHT_BROWSERS_PATH).
 * Jangan jalankan "playwright install" — browsernya sudah ada.
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SRC = path.join(__dirname, '..', 'design');
const OUT = path.join(SRC, 'export');

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const files = fs.readdirSync(SRC).filter((f) => f.endsWith('.dc.html')).sort();

  for (const f of files) {
    const ctx = await browser.newContext({
      deviceScaleFactor: 2,
      viewport: { width: 1600, height: 1200 },
    });
    const page = await ctx.newPage();
    await page.goto('file://' + path.join(SRC, f), { waitUntil: 'load' });

    // <x-dc> adalah elemen tak dikenal — tanpa ini dia inline dan ukurannya kacau.
    await page.addStyleTag({ content: 'x-dc{display:block} body{margin:0}' });

    // Tunggu Instrument Sans + IBM Plex Mono benar-benar termuat. Kalau tidak,
    // hasilnya jatuh ke font sistem dan seluruh tata letak bergeser.
    try {
      await page.waitForFunction(() => document.fonts.status === 'loaded', { timeout: 8000 });
    } catch (e) {
      console.warn(`  ! ${f}: font belum termuat, hasil mungkin meleset`);
    }

    const box = await page.evaluate(() => {
      const dc = document.querySelector('x-dc');
      const el = [...dc.children].find((c) => c.tagName !== 'HELMET');
      const r = el.getBoundingClientRect();
      return { w: Math.round(r.width), h: Math.round(r.height) };
    });

    await page.setViewportSize({ width: box.w, height: box.h });
    await page.waitForTimeout(300);

    const name = f.replace('.dc.html', '');
    await page.screenshot({
      path: path.join(OUT, name + '.png'),
      clip: { x: 0, y: 0, width: box.w, height: box.h },
    });
    console.log(`${name}  ${box.w}x${box.h}`);
    await ctx.close();
  }

  await browser.close();
})();
