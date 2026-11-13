/**
 * Render tiap artboard .dc.html jadi PNG 2x di design/export/.
 *
 * Dipakai supaya anggota tim keuangan tidak perlu buka canvas — dan supaya
 * layar-layar ini bisa diseret ke Figma / ditempel ke deck.
 *
 *   node scripts/render_design.js            # folder design/
 *   node scripts/render_design.js wireframe  # folder wireframe/
 *
 * Butuh Chromium yang sudah terpasang (PLAYWRIGHT_BROWSERS_PATH).
 * Jangan jalankan "playwright install" — browsernya sudah ada.
 */
// Playwright terpasang global di lingkungan ini, bukan di node_modules proyek —
// jadi require biasa gagal. Coba keduanya sebelum menyerah.
function loadPlaywright() {
  const candidates = ['playwright', '/opt/node22/lib/node_modules/playwright'];
  for (const c of candidates) {
    try { return require(c); } catch (e) { /* coba berikutnya */ }
  }
  throw new Error(
    'Playwright tidak ditemukan. Pasang dengan "npm i -D playwright" ' +
    '(jangan jalankan "playwright install" — browsernya sudah ada).');
}
const { chromium } = loadPlaywright();

// Playwright menuntut nomor build Chromium yang persis cocok dengan versinya, dan
// yang terpasang di lingkungan ini sering berbeda nomor. Jadi jangan biarkan ia
// mencari sendiri — tunjuk binary yang benar-benar ada. Tanpa ini, render gagal
// dengan saran "npx playwright install" yang justru TIDAK boleh dijalankan.
function cariChromium() {
  const fs_ = require('fs');
  const base = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  if (!fs_.existsSync(base)) return undefined;
  const kandidat = fs_.readdirSync(base)
    .filter((d) => d.startsWith('chromium'))
    .map((d) => `${base}/${d}/chrome-linux/chrome`)
    .concat(fs_.readdirSync(base)
      .filter((d) => d.startsWith('chromium'))
      .map((d) => `${base}/${d}/chrome-linux/headless_shell`));
  return kandidat.find((p) => fs_.existsSync(p));
}
const EXEC = cariChromium();
const fs = require('fs');
const path = require('path');

// Argumen pertama memilih folder: "design" (hi-fi) atau "wireframe" (lo-fi).
const DIR = process.argv[2] || 'design';
const SRC = path.join(__dirname, '..', DIR);
const OUT = path.join(SRC, 'export');

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch(EXEC ? { executablePath: EXEC } : {});
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
