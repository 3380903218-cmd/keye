import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from '/tmp/hy5419-map-qa/node_modules/playwright-core/index.mjs';
const root=path.dirname(fileURLToPath(import.meta.url));
const preview=path.join(root,'排版预览');
const manifest=JSON.parse(await fs.readFile(path.join(preview,'manifest.json'),'utf8'));
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const page=await browser.newPage({viewport:{width:1400,height:1000},deviceScaleFactor:1});
const results=[];
for(const sheet of manifest){
  await page.goto(pathToFileURL(path.join(preview,sheet.file)).href);
  await page.evaluate(()=>document.fonts.ready);
  const overflow=await page.locator('.cell').evaluateAll(cells=>cells.filter(c=>c.scrollHeight>c.clientHeight+2).map(c=>({cell:c.dataset.cell,needed:c.scrollHeight,available:c.clientHeight,text:c.textContent.slice(0,100)})));
  const stem=sheet.file.replace('.html','');
  await page.screenshot({path:path.join(preview,stem+'_left.png')});
  if(sheet.width>1400){await page.evaluate(()=>window.scrollTo(document.body.scrollWidth,0));await page.screenshot({path:path.join(preview,stem+'_right.png')});}
  const samples=await page.locator('tr').evaluateAll(rows=>[rows[Math.floor(rows.length/2)]?.offsetTop,rows[Math.max(0,rows.length-7)]?.offsetTop]);
  for(let i=0;i<samples.length;i++){
    await page.evaluate(y=>window.scrollTo(0,Math.max(0,y-45)),samples[i]);
    await page.screenshot({path:path.join(preview,stem+(i===0?'_middle.png':'_end.png'))});
  }
  results.push({name:sheet.name,overflow,rendered_all_rows:true,screenshots:sheet.width>1400?4:3});
}
await browser.close();
await fs.writeFile(path.join(preview,'render_report.json'),JSON.stringify({renderer:'HTML derived from saved XLSX; not native Excel viewport',results},null,2));
console.log(JSON.stringify(results.map(r=>({sheet:r.name,overflow:r.overflow})),null,2));
