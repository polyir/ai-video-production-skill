// usage: node stills.mjs <comp> <sec> [sec...]  → out/stills/s<sec>.jpg (one bundle, many stills)
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition, openBrowser} from '@remotion/renderer';
import path from 'node:path';
const [comp, ...secs] = process.argv.slice(2);
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const browser = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}});
const composition = await selectComposition({serveUrl, id: comp, puppeteerInstance: browser, chromiumOptions: {gl: 'angle'}});
await Promise.all(secs.map(async (s) => {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(parseFloat(s) * 30));
  await renderStill({serveUrl, composition, frame, output: `out/stills/${comp}-${s}.jpg`, imageFormat: 'jpeg', jpegQuality: 85, puppeteerInstance: browser, chromiumOptions: {gl: 'angle'}, timeoutInMilliseconds: 120000});
  console.log('ok', s);
}));
await browser.close({silent: true});
