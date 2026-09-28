// Build a PDF of the talk: node build-pdf.mjs [page.html] [output.pdf]
//   node build-pdf.mjs index.html talk.pdf       (20-minute version)
//   node build-pdf.mjs long.html talk-long.pdf   (full version)
// Needs `npm install` (puppeteer-core) and Google Chrome; set CHROME=/path/to/chrome if it is elsewhere.
// Starts serve.py, opens <page>?print-pdf, waits for reveal, fonts and the inlined SVGs, prints 1280×720 pages.
import puppeteer from 'puppeteer-core';
import { spawn } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const pageName = process.argv[2] || 'index.html';
const out = resolve(process.argv[3] || 'talk.pdf');
const port = 8000 + Math.floor(Math.random() * 900) + 100;
const chrome = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const server = spawn('python3', ['serve.py', String(port)], { cwd: here, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 800));
try {
  const browser = await puppeteer.launch({ executablePath: chrome, headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });
  await page.goto(`http://127.0.0.1:${port}/${pageName}?print-pdf`, { waitUntil: 'networkidle0', timeout: 60000 });
  await page.waitForFunction(
    () => window.Reveal && Reveal.isReady() && !document.querySelector('.reveal img[data-inline]') && document.fonts.status === 'loaded',
    { timeout: 60000 });
  await new Promise(r => setTimeout(r, 1500));
  await page.pdf({ path: out, printBackground: true, width: '1280px', height: '720px', preferCSSPageSize: false });
  await browser.close();
  console.log(`PDF written: ${out}`);
} finally {
  server.kill();
}
