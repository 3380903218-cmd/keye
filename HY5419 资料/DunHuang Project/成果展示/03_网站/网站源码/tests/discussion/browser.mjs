// Run with PLAYWRIGHT_MODULE and CHROME_EXECUTABLE when not using local npm modules.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve, extname, sep } from 'node:path';
import { database, handler } from './support.mjs';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright-core');
const root=resolve(fileURLToPath(new URL('../../dist/',import.meta.url)));
const output=process.env.DISCUSSION_QA_OUTPUT||fileURLToPath(new URL('./artifacts/',import.meta.url));
await mkdir(output,{recursive:true});
const db=await database();let api;
const server=createServer(async(req,res)=>{
  try{
    const url=new URL(req.url,'http://localhost');
    if(url.pathname==='/api/discussion'){
      const chunks=[];for await(const chunk of req)chunks.push(chunk);
      const request=new Request(origin+req.url,{method:req.method,headers:req.headers,body:req.method==='POST'?Buffer.concat(chunks):undefined});
      const response=await api(request);res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));return;
    }
    if(url.pathname==='/discussion-config.js'){
      res.setHeader('Content-Type','text/javascript');res.end(`window.DUNHUANG_DISCUSSION_CONFIG=${JSON.stringify({enabled:true,apiUrl:origin+'/api/discussion',siteUrl:origin+'/'})}`);return;
    }
    const file=resolve(root,'.'+decodeURIComponent(url.pathname==='/'?'/index.html':url.pathname));
    if(!file.startsWith(root+sep)&&file!==resolve(root,'index.html')){res.writeHead(403);res.end();return;}
    const content=await readFile(file);
    res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.svg':'image/svg+xml','.pdf':'application/pdf'})[extname(file)]||'application/octet-stream');res.end(content);
  }catch{res.writeHead(404);res.end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;api=handler(db,origin);
const browser=await chromium.launch({headless:true,...(process.env.CHROME_EXECUTABLE?{executablePath:process.env.CHROME_EXECUTABLE}:{})});
const report={result:'pending',scope:'Two independent browser contexts, production HTML/JS, HTTP handler, real local Postgres; not cloud deployment.',checks:[]};
try{
  const a=await browser.newContext({viewport:{width:1440,height:1000}}),b=await browser.newContext({viewport:{width:1440,height:1000}}),c=await browser.newContext({viewport:{width:390,height:844}});
  const A=await a.newPage(),B=await b.newPage(),C=await c.newPage();const errors=[];
  for(const page of [A,B,C])page.on('pageerror',error=>errors.push(String(error)));
  await A.goto(origin+'/#discussion');await A.locator('#discussion').scrollIntoViewIfNeeded();await A.waitForFunction(()=>window.DUNHUANG_DISCUSSION?.getState().loading===false);
  const rootForm=A.locator('.discussion-composer form');
  await rootForm.locator('[name=name]').fill('LOCAL QA Reader A');await rootForm.locator('[name=body]').fill('LOCAL QA: <img src=x onerror="window.__injected=true"> — can the arrival and accession dates be distinguished?');
  await rootForm.getByRole('button',{name:'Post message',exact:true}).click();await A.waitForFunction(()=>document.querySelectorAll('.discussion-thread').length===1);
  await B.goto(origin+'/?lang=zh#discussion');await B.locator('#discussion').scrollIntoViewIfNeeded();await B.waitForFunction(()=>document.querySelectorAll('.discussion-thread').length===1);
  assert.notEqual(await A.evaluate(()=>localStorage.getItem('dunhuang-discussion-visitor')),await B.evaluate(()=>localStorage.getItem('dunhuang-discussion-visitor')));
  assert.equal(await B.locator('.discussion-body img').count(),0);assert.equal(await B.evaluate(()=>window.__injected),undefined);
  await B.locator('.discussion-thread').getByRole('button',{name:'回复',exact:true}).click();const replyForm=B.locator('.discussion-inline-form form');
  await replyForm.locator('[name=name]').fill('LOCAL QA 读者B');await replyForm.locator('[name=body]').fill('LOCAL QA：可以在同一问题下补充来源。');
  await B.locator('#lang').click();assert.equal(await replyForm.locator('[name=body]').inputValue(),'LOCAL QA：可以在同一问题下补充来源。');
  await replyForm.getByRole('button',{name:'Post message',exact:true}).click();await B.waitForFunction(()=>document.querySelectorAll('.discussion-response').length===1);
  await A.locator('.discussion-refresh').click();await A.waitForFunction(()=>document.querySelectorAll('.discussion-response').length===1);
  report.checks.push('A second independent reader reads and replies to the first reader; language switching preserves draft.');
  assert.equal(await A.locator('.discussion-body img').count(),0);assert.equal(await A.evaluate(()=>window.__injected),undefined);
  report.checks.push('User HTML is displayed as text and never runs.');

  await A.locator('.discussion-thread').getByRole('button',{name:'Reply',exact:true}).click();
  await A.locator('.discussion-inline-form textarea').fill('LOCAL QA draft survives a refresh.');await A.locator('.discussion-refresh').click();
  await A.waitForFunction(()=>window.DUNHUANG_DISCUSSION.getState().loading===false);
  assert.equal(await A.locator('.discussion-inline-form textarea').inputValue(),'LOCAL QA draft survives a refresh.');
  await A.locator('.discussion-inline-form').getByRole('button',{name:'Cancel',exact:true}).click();
  assert.equal(await A.locator('.discussion-inline-form').count(),0);
  await B.reload();await B.locator('#discussion').scrollIntoViewIfNeeded();await B.waitForFunction(()=>document.querySelectorAll('.discussion-response').length===1);
  report.checks.push('Refreshing preserves an unfinished reply and saved messages survive a full page reload.');

  await C.goto(origin+'/#discussion');await C.locator('#discussion').scrollIntoViewIfNeeded();
  let lost=false;await C.route('**/api/discussion',async route=>{if(route.request().method()==='POST'&&!lost){lost=true;await route.fetch();await route.abort('failed');}else await route.continue();});
  const lostForm=C.locator('.discussion-composer form');await lostForm.locator('[name=name]').fill('LOCAL QA Reader C');await lostForm.locator('[name=body]').fill('LOCAL QA lost response retry test.');
  await lostForm.getByRole('button',{name:'Post message',exact:true}).click();await C.waitForFunction(()=>document.querySelector('.discussion-composer .discussion-form-status').textContent.includes('could not confirm'));
  assert.equal(await lostForm.locator('textarea').inputValue(),'LOCAL QA lost response retry test.');
  await lostForm.getByRole('button',{name:'Post message',exact:true}).click();await C.waitForFunction(()=>document.querySelector('.discussion-composer textarea').value==='');
  assert.equal((await db.query('select count(*)::int as n from discussion_private.messages')).rows[0].n,3);
  report.checks.push('A saved request with a lost HTTP response can be retried without duplicate messages.');

  const graph=await A.evaluate(()=>({nodes:window.DUNHUANG_NETWORK.nodes.length,edges:window.DUNHUANG_NETWORK.edges.length,events:window.DUNHUANG_NETWORK.events.length,map:!!window.DUNHUANG_EXHIBITION}));
  assert.deepEqual(graph,{nodes:132,edges:157,events:48,map:true});
  report.checks.push('The existing map and 132-node/157-edge network still initialise.');
  for(const [page,width] of [[A,1440],[C,390]]){
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.locator('#discussion').evaluate(node=>node.scrollIntoView({block:'start',behavior:'instant'}));
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    const geometry=await page.evaluate(()=>({title:document.querySelector('#discussion-heading').getBoundingClientRect().top,header:document.querySelector('.site-header').getBoundingClientRect().bottom}));
    assert(geometry.title>=geometry.header,'The discussion title is covered by the sticky header');
    await page.screenshot({path:resolve(output,`discussion-viewport-${width}.png`)});
    // Exclude fixed UI only from the full-section export, where browser stitching relocates it.
    const clean=await page.addStyleTag({content:'.site-header,.skip-link{visibility:hidden!important}'});
    await page.locator('#discussion').screenshot({path:resolve(output,`discussion-${width}.png`)});
    await clean.evaluate(node=>node.remove());
  }
  const disabledPage=await browser.newPage();let disabledRequests=0;
  // Test deactivation independently of this checkout's production activation state.
  const disabledConfig='window.DUNHUANG_DISCUSSION_CONFIG = {enabled:false};';
  await disabledPage.route('**/discussion-config.js*',route=>route.fulfill({contentType:'text/javascript',body:disabledConfig}));
  disabledPage.on('request',request=>{if(request.url().includes('/api/discussion'))disabledRequests++;});
  await disabledPage.goto(origin+'/#discussion');
  assert.equal(await disabledPage.locator('#discussion').isVisible(),false);assert.equal(disabledRequests,0);
  await disabledPage.close();report.checks.push('An unconfigured release hides the feature and makes no discussion API calls; anchored titles clear the sticky header.');
  assert.deepEqual(errors,[]);report.checks.push('Desktop and mobile layouts have no horizontal overflow or JavaScript errors.');report.result='pass';
}finally{
  await writeFile(resolve(output,'browser-verification.json'),JSON.stringify(report,null,2));
  await browser.close();await new Promise(resolve=>server.close(resolve));await db.close();
}
console.log(JSON.stringify(report,null,2));
