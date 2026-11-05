const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const CATEGORIES = new Set(['general','map','network','collections','sources']);
const MAX_BYTES = 16384;

function cursor(value) {
  if (!value) return { at: null, id: null };
  try {
    const c = JSON.parse(value);
    if (typeof c.at !== 'string' || !Number.isFinite(Date.parse(c.at)) || !UUID.test(c.id)) throw 0;
    return c;
  } catch { throw new Error('invalid_cursor'); }
}

async function readJSON(request) {
  if (!request.body) throw new Error('invalid_input');
  const reader = request.body.getReader();
  const chunks = []; let size = 0;
  try {
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > MAX_BYTES) { await reader.cancel(); throw new Error('too_large'); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const merged = new Uint8Array(size); let offset=0;
  for (const chunk of chunks) { merged.set(chunk,offset); offset+=chunk.byteLength; }
  try { return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(merged)); }
  catch { throw new Error('invalid_input'); }
}

export function createDiscussionHandler({ env, fetchImpl = fetch, now = () => new Date(), cryptoImpl = crypto }) {
  const origins = new Set((env.DISCUSSION_ALLOWED_ORIGINS || 'https://3380903218-cmd.github.io').split(',').map(v=>v.trim()).filter(Boolean));
  const base = env.SUPABASE_URL?.replace(/\/$/,'');
  let injectedKeys={};
  try {injectedKeys=JSON.parse(env.SUPABASE_SECRET_KEYS||'{}');}catch{/* Missing/invalid server settings fail closed below. */}
  const modernKey=env.SUPABASE_SECRET_KEY||injectedKeys.default||Object.values(injectedKeys).find(v=>typeof v==='string'&&v.startsWith('sb_secret_'));
  const serviceKey = modernKey||env.SUPABASE_SERVICE_ROLE_KEY;
  const secret = env.DISCUSSION_RATE_SECRET || serviceKey;
  let hmacKey;
  async function digest(text) {
    hmacKey ||= cryptoImpl.subtle.importKey('raw',new TextEncoder().encode(secret),{name:'HMAC',hash:'SHA-256'},false,['sign']);
    const bytes=await cryptoImpl.subtle.sign('HMAC',await hmacKey,new TextEncoder().encode('dunhuang-discussion/rate/v1/'+text));
    return Array.from(new Uint8Array(bytes),v=>v.toString(16).padStart(2,'0')).join('');
  }
  async function rpc(name, args) {
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
    try {
      const response=await fetchImpl(`${base}/rest/v1/rpc/${name}`,{
        method:'POST',headers:{apikey:serviceKey,...(!serviceKey.startsWith('sb_secret_')?{Authorization:`Bearer ${serviceKey}`}:{}) ,'Content-Type':'application/json'},
        body:JSON.stringify(args),signal:controller.signal
      });
      const data=await response.json();
      if(!response.ok) {
        const code=['rate_limit','request_conflict','thread_unavailable','invalid_input','invalid_cursor'].find(c=>data.message===c);
        throw new Error(code||'storage_unavailable');
      }
      return data;
    } finally {clearTimeout(timer);}
  }
  return async request => {
    const origin=request.headers.get('origin');
    const allowed=!origin||origins.has(origin);
    const headers={
      'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',
      'X-Content-Type-Options':'nosniff','Vary':'Origin',
      ...(origin&&allowed?{'Access-Control-Allow-Origin':origin}:{}),
      'Access-Control-Allow-Methods':'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers':'content-type, apikey',
      'Access-Control-Max-Age':'600'
    };
    const respond=(data,status=200)=>new Response(JSON.stringify(data),{status,headers});
    if(!allowed)return respond({error:'origin_not_allowed'},403);
    if(request.method==='OPTIONS')return new Response(null,{status:204,headers});
    if(!['GET','POST'].includes(request.method))return respond({error:'method_not_allowed'},405);
    if(!base||!serviceKey||!secret)return respond({error:'service_not_configured'},503);
    try {
      if(request.method==='GET') {
        const url=new URL(request.url),before=cursor(url.searchParams.get('before'));
        const replyBefore=cursor(url.searchParams.get('replyBefore')),threadId=url.searchParams.get('thread');
        if(threadId&&!UUID.test(threadId))throw new Error('invalid_input');
        if(replyBefore.at&&!threadId)throw new Error('invalid_cursor');
        return respond(await rpc('dunhuang_discussion_list',{
          p_before:before.at,p_before_id:before.id,p_thread_id:threadId,
          p_reply_before:replyBefore.at,p_reply_before_id:replyBefore.id
        }));
      }
      if(!(request.headers.get('content-type')||'').toLowerCase().startsWith('application/json'))return respond({error:'json_required'},415);
      const body=await readJSON(request);
      if(!body||typeof body!=='object'||Array.isArray(body))throw new Error('invalid_input');
      const {clientId,visitorId,threadId=null,name,body:message,category='general',website=''}=body;
      if(!UUID.test(clientId)||!UUID.test(visitorId)||(threadId!==null&&!UUID.test(threadId))
        ||typeof name!=='string'||typeof message!=='string'
        ||!name.trim()||!message.trim()||name.trim().length>32||message.trim().length>2000
        ||!CATEGORIES.has(category)||typeof website!=='string'||website!=='')throw new Error('invalid_input');
      // Forwarded network headers are a best-effort second limit, not proof of identity.
      // A separate visitor limit avoids treating everyone on a classroom Wi-Fi as one person.
      const network=(request.headers.get('cf-connecting-ip')||request.headers.get('x-forwarded-for')?.split(',')[0]||'unknown').trim().slice(0,100);
      const day=now().toISOString().slice(0,10);
      return respond(await rpc('dunhuang_discussion_post',{
        p_client_id:clientId,p_thread_id:threadId,p_name:name.trim(),p_body:message.trim(),p_category:category,
        p_fingerprint:await digest(`${day}/visitor/${visitorId}`),p_network_hash:await digest(`${day}/network/${network}`)
      }),201);
    } catch(error) {
      const codes={rate_limit:429,invalid_cursor:400,invalid_input:400,too_large:413,request_conflict:409,thread_unavailable:404};
      const status=codes[error.message]||503;
      if(status===429)headers['Retry-After']='30';
      return respond({error:status===503?'storage_unavailable':error.message},status);
    }
  };
}
