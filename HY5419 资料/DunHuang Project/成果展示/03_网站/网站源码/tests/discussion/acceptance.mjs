import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { database, handler, PGlite } from './support.mjs';

const dir=await mkdtemp(join(tmpdir(),'dunhuang-discussion-'));
let db;const checks=[];const origin='https://3380903218-cmd.github.io';
try {
  db=await database(join(dir,'pg'));
  const api=handler(db);
  const get=async query=>{
    const url=new URL('https://local-test.invalid/discussion');
    for(const [key,value] of Object.entries(query||{}))url.searchParams.set(key,typeof value==='object'?JSON.stringify(value):value);
    const response=await api(new Request(url,{headers:{Origin:origin}}));
    assert.equal(response.status,200);return response.json();
  };
  const makeBody=(extra={})=>({clientId:crypto.randomUUID(),visitorId:crypto.randomUUID(),name:'Reader',body:'A question about this route.',category:'map',website:'',...extra});
  const post=body=>api(new Request('https://local-test.invalid/discussion',{method:'POST',headers:{Origin:origin,'content-type':'application/json'},body:JSON.stringify(body)}));
  assert.deepEqual((await get()).threads,[]);
  const rootBody=makeBody({body:'请核查这段路线。 <img src=x onerror=alert(1)>'}),rootResponse=await post(rootBody);
  assert.equal(rootResponse.status,201);const root=await rootResponse.json();
  const duplicate=await post(rootBody);assert.equal(duplicate.status,201);assert.equal((await duplicate.json()).id,root.id);
  const conflict=await post({...rootBody,body:'Changed content'});assert.equal(conflict.status,409);
  assert.equal((await db.query('select count(*)::int as n from discussion_private.messages')).rows[0].n,1);
  checks.push('A retry of the same submission produces one row; conflicting reuse is rejected.');

  const replyResponse=await post(makeBody({threadId:root.id,name:'Another reader',body:'Could this date refer to accession rather than arrival?'}));
  assert.equal(replyResponse.status,201);const reply=await replyResponse.json();assert.equal(reply.threadId,root.id);
  const secondView=await get();assert.equal(secondView.threads[0].replies[0].id,reply.id);
  assert.equal(secondView.threads[0].body,rootBody.body);
  assert.equal((await post(makeBody({threadId:reply.id}))).status,404);
  assert.equal((await post(makeBody({threadId:crypto.randomUUID()}))).status,404);
  checks.push('A second reader sees the root and its reply; nested/missing reply targets are rejected.');

  assert.equal((await post(makeBody({body:' '}))).status,400);
  assert.equal((await post(makeBody({website:'spam.example'}))).status,400);
  assert.equal((await post(makeBody({body:'x'.repeat(17000)}))).status,413);
  const blocked=await api(new Request('https://local-test.invalid/discussion',{headers:{Origin:'https://unrelated.example'}}));assert.equal(blocked.status,403);
  const preflight=await api(new Request('https://local-test.invalid/discussion',{method:'OPTIONS',headers:{Origin:origin}}));assert.equal(preflight.status,204);assert.equal(preflight.headers.get('Access-Control-Allow-Origin'),origin);
  const badCursor=await api(new Request('https://local-test.invalid/discussion?before=not-json',{headers:{Origin:origin}}));assert.equal(badCursor.status,400);
  checks.push('Validation, payload cap, honeypot, CORS and invalid cursors fail without saving messages.');

  const sameVisitor=makeBody();assert.equal((await post(sameVisitor)).status,201);
  assert.equal((await post({...sameVisitor,clientId:crypto.randomUUID()})).status,429);
  assert.equal((await post(makeBody())).status,201);
  checks.push('One visitor is throttled without blocking a different reader on the same network.');

  for(const role of ['anon','authenticated']) {
    await assert.rejects(db.transaction(async tx=>{await tx.exec(`set local role ${role}`);await tx.query('select * from discussion_private.messages');}));
    await assert.rejects(db.transaction(async tx=>{await tx.exec(`set local role ${role}`);await tx.query('select public.dunhuang_discussion_list()');}));
  }
  assert(!JSON.stringify(await get()).includes('local-test-credential'));
  assert(!JSON.stringify(await get()).includes('fingerprint'));
  checks.push('Browser database roles cannot read tables or call RPCs; responses exclude credentials and rate hashes.');

  // Explicit test fixtures stay in this disposable local database.
  for(let i=0;i<33;i++)await db.query('insert into discussion_private.messages(client_id,parent_id,display_name,body,category) values($1,$2,$3,$4,$5)',[crypto.randomUUID(),root.id,'Fixture',`Reply ${i}`,'map']);
  const firstReplies=(await get({thread:root.id})).threads[0];assert.equal(firstReplies.replies.length,25);assert(firstReplies.replyNext);
  const olderReplies=(await get({thread:root.id,replyBefore:firstReplies.replyNext})).threads[0];
  const ids=new Set([...firstReplies.replies,...olderReplies.replies].map(r=>r.id));assert.equal(ids.size,34);assert.equal(olderReplies.replyNext,null);
  for(let i=0;i<13;i++)await db.query('insert into discussion_private.messages(client_id,display_name,body) values($1,$2,$3)',[crypto.randomUUID(),'Fixture',`Thread ${i}`]);
  const firstPage=await get();assert.equal(firstPage.threads.length,10);assert(firstPage.next);
  const secondPage=await get({before:firstPage.next});assert.equal(new Set([...firstPage.threads,...secondPage.threads].map(t=>t.id)).size,16);
  checks.push('Thread and reply pagination have no missing or duplicated records.');

  await db.query('update discussion_private.messages set hidden=true where id=$1',[root.id]);
  assert.equal((await get({thread:root.id})).threads.length,0);
  assert.equal((await post(makeBody({threadId:root.id}))).status,404);
  const beforeClose=(await db.query('select count(*)::int as n from discussion_private.messages')).rows[0].n;
  await db.close();db=new PGlite(join(dir,'pg'));
  assert.equal((await db.query('select count(*)::int as n from discussion_private.messages')).rows[0].n,beforeClose);
  checks.push('Hiding a root hides its replies; records persist after closing and reopening Postgres.');
  console.log(JSON.stringify({result:'pass',scope:'Real local Postgres engine plus the production HTTP handler; not a deployed Supabase test.',checks},null,2));
} finally {if(db)await db.close();await rm(dir,{recursive:true,force:true});}
