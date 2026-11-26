#!/usr/bin/env node
/* Draw the film frame by frame and put the voice under it.

     node film/tools/render.js                 # the film, its poster
     node film/tools/render.js --still 42.5    # one frame, to look at

   Needs Playwright with Chromium, and ffmpeg on the PATH. Run
   film/tools/voice.py first: it writes the timeline the picture is drawn
   against and the narration this lays under it.

   The page is asked for each frame by its time, so a frame comes out the same
   however fast or slow the machine is, and the frames can be drawn by several
   pages at once. */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const REPO = path.resolve(__dirname, '..', '..');
const BUILD = path.join(REPO, 'film', 'build');
const OUT = path.join(REPO, 'site', 'assets', 'film');
const FPS = 24, W = 1920, H = 1080, PAGES = 4;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.svg': 'image/svg+xml' };

function serve() {
  const server = http.createServer((req, res) => {
    const file = path.join(REPO, decodeURIComponent(req.url.split('?')[0]));
    if (!file.startsWith(REPO) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server)));
}

async function stage(browser, port) {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto(`http://127.0.0.1:${port}/film/film.html`);
  await page.evaluate(() => document.fonts.ready);
  return page;
}

function run(cmd, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, { stdio: ['ignore', 'ignore', 'pipe'] });
    let err = '';
    child.stderr.on('data', d => { err += d; });
    child.on('close', code => code === 0 ? resolve() : reject(new Error(err.slice(-800))));
  });
}

(async () => {
  const args = process.argv.slice(2);
  const server = await serve();
  const port = server.address().port;
  const browser = await chromium.launch();
  try {
    if (args[0] === '--still') {
      const page = await stage(browser, port);
      for (const value of args.slice(1)) {
        const t = parseFloat(value);
        await page.evaluate(x => window.FILM.seek(x), t);
        const file = path.join(BUILD, `still-${value.replace('.', '_')}.png`);
        fs.mkdirSync(BUILD, { recursive: true });
        await page.screenshot({ path: file });
        console.log(file);
      }
      return;
    }
    const frames = path.join(BUILD, 'frames');
    fs.rmSync(frames, { recursive: true, force: true });
    fs.mkdirSync(frames, { recursive: true });
    fs.mkdirSync(OUT, { recursive: true });
    const pages = await Promise.all(Array.from({ length: PAGES }, () => stage(browser, port)));
    const duration = await pages[0].evaluate(() => window.FILM.duration);
    const total = Math.ceil(duration * FPS);
    let next = 0, done = 0;
    await Promise.all(pages.map(async page => {
      while (next < total) {
        const frame = next++;
        await page.evaluate(x => window.FILM.seek(x), frame / FPS);
        await page.screenshot({ path: path.join(frames, `f${String(frame).padStart(5, '0')}.png`) });
        if (++done % 240 === 0) console.log(`${done} of ${total} frames`);
      }
    }));
    const film = path.join(OUT, 'archreator.mp4');
    await run('ffmpeg', ['-y', '-framerate', String(FPS), '-i', path.join(frames, 'f%05d.png'),
      '-i', path.join(BUILD, 'narration.wav'),
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-pix_fmt', 'yuv420p', '-tune', 'animation',
      // The voice arrives quiet with sharp peaks; this brings it to the level
      // web video is expected at, without clipping.
      '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000',
      '-c:a', 'aac', '-b:a', '112k', '-ac', '1', '-movflags', '+faststart', '-shortest', film]);
    // The poster is the film's own argument in one frame: the two roads, side by side.
    const pitch = await pages[0].evaluate(() => window.FILM.lines.find(line => line.key === 'fix/2').end + 0.1);
    await pages[0].evaluate(x => window.FILM.seek(x), pitch);
    await pages[0].screenshot({ path: path.join(OUT, 'poster.jpg'), type: 'jpeg', quality: 86 });
    console.log(`${film}: ${(fs.statSync(film).size / 1e6).toFixed(1)} MB, ${duration.toFixed(1)} s, ${total} frames`);
  } finally {
    await browser.close();
    server.close();
  }
})().catch(error => { console.error(String(error)); process.exit(1); });
