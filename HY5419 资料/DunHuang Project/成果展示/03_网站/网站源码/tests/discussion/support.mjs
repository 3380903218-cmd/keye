import { readFile } from 'node:fs/promises';
import { createDiscussionHandler } from '../../supabase/functions/_shared/discussion-handler.mjs';
const {PGlite}=await import(process.env.PGLITE_MODULE || '@electric-sql/pglite');
export {PGlite};
export async function database(path) {
  const db=new PGlite(path);
  await db.exec('create role anon; create role authenticated; create role service_role bypassrls;');
  await db.exec(await readFile(new URL('../../supabase/migrations/20261102162018_create_reader_discussion.sql',import.meta.url),'utf8'));
  return db;
}
export function handler(db, origin='https://3380903218-cmd.github.io') {
  const serviceKey='local-test-credential-never-used-on-the-network';
  const fetchImpl=async (url,options)=>{
    if(options.headers.Authorization!==`Bearer ${serviceKey}`)throw new Error('Missing server credential');
    const name=new URL(url).pathname.split('/').pop();
    const definitions={
      dunhuang_discussion_list:[['p_before','timestamptz'],['p_before_id','uuid'],['p_thread_id','uuid'],['p_reply_before','timestamptz'],['p_reply_before_id','uuid']],
      dunhuang_discussion_post:[['p_client_id','uuid'],['p_thread_id','uuid'],['p_name','text'],['p_body','text'],['p_category','text'],['p_fingerprint','text'],['p_network_hash','text']]
    };
    const definition=definitions[name];if(!definition)throw new Error('Unexpected RPC');
    const values=JSON.parse(options.body);
    try {
      const result=await db.transaction(async tx=>{
        await tx.exec('set local role service_role');
        return await tx.query(`select public.${name}(${definition.map(([key,type],i)=>`${key}=>$${i+1}::${type}`).join(',')}) as result`,definition.map(([key])=>values[key]));
      });
      return Response.json(result.rows[0].result);
    } catch(error) {return Response.json({message:error.message},{status:400});}
  };
  return createDiscussionHandler({env:{SUPABASE_URL:'https://local-test.invalid',SUPABASE_SERVICE_ROLE_KEY:serviceKey,DISCUSSION_ALLOWED_ORIGINS:origin},fetchImpl});
}
