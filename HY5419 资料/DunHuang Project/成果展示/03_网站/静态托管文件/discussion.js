/* Public threads use a shared API. Browser storage is never used for comments. */
(() => {
  'use strict';
  const host = document.getElementById('discussion');
  if (!host) return;
  const config = window.DUNHUANG_DISCUSSION_CONFIG || {};
  if (config.enabled === false) {
    host.hidden=true;
    document.querySelectorAll('[href="#discussion"]').forEach(n=>n.hidden=true);
    return;
  }
  host.hidden=false;
  document.querySelectorAll('[href="#discussion"]').forEach(n=>n.hidden=false);
  const offline=location.protocol==='file:'&&!!config.siteUrl;
  const configured=!!config.apiUrl&&!offline;
  const uuidPattern=/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  let visitorId=crypto.randomUUID();
  try { const saved=localStorage.getItem('dunhuang-discussion-visitor'); if(uuidPattern.test(saved))visitorId=saved;else localStorage.setItem('dunhuang-discussion-visitor',visitorId); } catch { /* A private browser can use an in-memory visitor ID. */ }
  let lang = window.DUNHUANG_EXHIBITION?.getState().lang || document.documentElement.lang || 'en';
  let threads = [], next = null, loading = false, started = false;
  const words = {
    en: {kicker:'READERS’ DISCUSSION',title:'Questions, suggestions and replies',intro:'Was a route hard to follow, or a relationship unclear? Share a specific example, suggest a source, or respond to another reader.',write:'Start a discussion',name:'Display name',area:'Related section',body:'Your question or suggestion',replyBody:'Your reply',public:'You can write in any language. Your name and message will be public. Please do not include contact details or private information.',send:'Post message',sending:'Posting…',list:'Reader discussions',refresh:'Refresh',empty:'No discussions yet. You can start the first one.',pending:'The discussion is being prepared. Posting is not available yet.',load:'Loading discussions…',error:'The discussion could not be loaded. Please try refreshing.',failed:'We could not confirm whether your message was posted. Your text is still here; retrying the same submission will not create a duplicate.',sent:'Your message has been posted.',reply:'Reply',replyTo:'Reply in this discussion',cancel:'Cancel',more:'Load more discussions',required:'Please enter a display name and a message.',tooLong:'The name or message is too long.',wait:'Please wait a moment before posting again.',areas:{general:'General',map:'Routes and dates',network:'People and relationships',collections:'Collections and preservation',sources:'Sources and corrections'}},
    zh: {kicker:'读者讨论',title:'建议、疑问与交流',intro:'哪段路线不容易看懂，或哪项人物关系还不清楚？欢迎留下具体意见、补充资料，也可以回应其他读者。',write:'提出问题或建议',name:'昵称',area:'相关板块',body:'你的问题或建议',replyBody:'你的回复',public:'可以使用任何语言留言或回复。昵称与留言将公开显示，请勿填写联系方式或私人信息。',send:'发表留言',sending:'正在发表…',list:'大家的讨论',refresh:'刷新',empty:'目前还没有讨论，欢迎留下第一条建议。',pending:'讨论区正在准备中，暂未开放发言。',load:'正在加载讨论…',error:'暂时无法加载讨论，请尝试刷新。',failed:'暂未确认留言是否发表。输入内容已保留，可以重试，同一条提交不会重复保存。',sent:'留言已发表。',reply:'回复',replyTo:'回复这条讨论',cancel:'取消',more:'加载更多讨论',required:'请填写昵称与留言内容。',tooLong:'昵称或留言超出长度限制。',wait:'发表较频繁，请稍后再试。',areas:{general:'综合意见',map:'路线与时间',network:'人物与关系',collections:'馆藏与保存',sources:'来源与纠错'}}
  };
  const tr = key => words[lang === 'zh' ? 'zh' : 'en'][key];
  Object.assign(words.en,{earlier:'Read earlier replies',offline:'The shared discussion is available on the live website.',online:'Open the live discussion ↗',sentRefresh:'Your message was posted, but the discussion could not be refreshed. Please refresh the list later.',unavailable:'This discussion is no longer available.',unverified:'Display names are chosen by readers. Comments are not verified historical sources.'});
  Object.assign(words.zh,{earlier:'查看较早的回复',offline:'共享讨论需要联网，请打开在线网站参与。',online:'前往在线讨论区 ↗',sentRefresh:'留言已发表，但暂时无法刷新讨论，请稍后刷新列表。',unavailable:'这条讨论已不可用。',unverified:'昵称由读者自行填写，留言不作为已经核实的历史资料。'});
  const el = (tag, className, text) => { const n=document.createElement(tag); if(className)n.className=className; if(text!==undefined)n.textContent=text; if(className==='discussion-body'||className==='discussion-name')n.dir='auto'; return n; };
  function setStatus(node,key){if(key)node.dataset.discussionText=key;else delete node.dataset.discussionText;node.textContent=key?tr(key):'';}
  function labelText(n, key) { n.dataset.discussionText=key; n.textContent=tr(key); return n; }
  function button(key, cls) { const n=labelText(el('button',cls),key); n.type='button'; return n; }
  function languageText() {
    host.querySelectorAll('[data-discussion-text]').forEach(n=>n.textContent=tr(n.dataset.discussionText));
    host.querySelectorAll('[data-discussion-area]').forEach(n=>n.textContent=tr('areas')[n.dataset.discussionArea]||tr('areas').general);
    host.querySelectorAll('time').forEach(n=>n.textContent=new Date(n.dateTime).toLocaleString(lang==='zh'?'zh-CN':'en-GB',{dateStyle:'medium',timeStyle:'short'}));
    if(stateKey) message.textContent=tr(stateKey);
  }
  async function request(method, data, query={}) {
    if(!configured) throw new Error('not_configured');
    const url = new URL(config.apiUrl);
    for(const [key,value] of Object.entries(query))if(value)url.searchParams.set(key,typeof value==='object'?JSON.stringify(value):value);
    const headers = {Accept:'application/json'};
    if(method==='POST')headers['Content-Type']='application/json';
    const controller=new AbortController(), timeout=setTimeout(()=>controller.abort(),15000);
    try {
      const response=await fetch(url,{method,headers,body:method==='POST'?JSON.stringify(data):undefined,signal:controller.signal,credentials:'omit'});
      if(!response.ok)throw new Error(response.status===429?'rate_limit':response.status===404?'thread_unavailable':'request_failed');
      return await response.json();
    } finally { clearTimeout(timeout); }
  }
  function form(threadId=null) {
    const f=el('form','discussion-form');
    const nameLabel=el('label'),name=el('input');nameLabel.append(labelText(el('span'),'name'));name.name='name';name.dir='auto';name.required=true;name.maxLength=32;name.autocomplete='nickname';nameLabel.append(name);
    f.append(nameLabel);
    if(!threadId){
      const areaLabel=el('label'),select=el('select');areaLabel.append(labelText(el('span'),'area'));select.name='category';
      for(const [key,value] of Object.entries(tr('areas'))){const option=el('option','',value);option.value=key;option.dataset.discussionArea=key;select.append(option);}
      areaLabel.append(select);f.append(areaLabel);
    }
    const bodyLabel=el('label'),body=el('textarea');bodyLabel.append(labelText(el('span'),threadId?'replyBody':'body'));body.name='body';body.dir='auto';body.required=true;body.maxLength=2000;body.rows=threadId?3:5;bodyLabel.append(body);f.append(bodyLabel);
    const trapLabel=el('label','discussion-trap','Website'),trap=el('input');trap.name='website';trap.tabIndex=-1;trap.autocomplete='off';trapLabel.setAttribute('aria-hidden','true');trapLabel.append(trap);f.append(trapLabel);
    const note=labelText(el('p','discussion-public-note'),'public');f.append(note);
    const submit=labelText(el('button','discussion-submit'),'send');submit.type='submit';f.append(submit);
    const status=el('p','discussion-form-status');status.setAttribute('role','status');status.setAttribute('aria-live','polite');f.append(status);
    let clientId=null,lastPayload='';
    f.addEventListener('submit',async e=>{
      e.preventDefault();
      if(!configured){setStatus(status,offline?'offline':'pending');return;}
      const nameText=name.value.trim(),bodyText=body.value.trim();
      if(!nameText||!bodyText){setStatus(status,'required');return;}
      if(nameText.length>32||bodyText.length>2000){setStatus(status,'tooLong');return;}
      submit.disabled=true;submit.dataset.discussionText='sending';submit.textContent=tr('sending');setStatus(status,'');
      const payload=JSON.stringify([nameText,bodyText,f.elements.category?.value,threadId]);
      if(!clientId||lastPayload!==payload)clientId=crypto.randomUUID();lastPayload=payload;
      try {
        const result=await request('POST',{clientId,visitorId,threadId,name:nameText,body:bodyText,category:f.elements.category?.value||'general',website:trap.value});
        if(!uuidPattern.test(result.id)||!uuidPattern.test(result.threadId))throw new Error('invalid_response');
        body.value='';clientId=null;setStatus(status,'sent');setStatus(announcement,'');
        try {
          if(threadId)await refreshThread(threadId);else await load(false);
        }catch{setStatus(announcement,'sentRefresh');}
        if(threadId)document.getElementById('discussion-thread-'+threadId)?.scrollIntoView({block:'nearest',behavior:'auto'});
      } catch(error) {setStatus(status,error.message==='rate_limit'?'wait':error.message==='thread_unavailable'?'unavailable':'failed');}
      finally{submit.disabled=false;submit.dataset.discussionText='send';submit.textContent=tr('send');}
    });
    return f;
  }
  const heading=el('div','discussion-heading');heading.append(labelText(el('p','discussion-kicker'),'kicker'));
  const title=labelText(el('h2'),'title');title.id='discussion-heading';heading.append(title,labelText(el('p'),'intro'));host.setAttribute('aria-labelledby',title.id);
  const layout=el('div','discussion-layout'),composer=el('div','discussion-composer');composer.append(labelText(el('h3'),'write'),form());
  if(offline)composer.hidden=true;
  const panel=el('div','discussion-panel'),listHeading=el('div','discussion-list-heading'),refresh=button('refresh','discussion-refresh');
  listHeading.append(labelText(el('h3'),'list'),refresh);panel.append(listHeading);
  const message=el('p','discussion-message');message.setAttribute('role','status');
  const list=el('div','discussion-list'),more=button('more','discussion-more');more.hidden=true;panel.append(message,list,more);layout.append(composer,panel);host.append(heading,layout);
  const announcement=el('p','discussion-form-status');announcement.setAttribute('role','status');host.append(announcement,labelText(el('p','discussion-public-note discussion-source-note'),'unverified'));
  if(offline){refresh.hidden=true;const link=labelText(el('a','discussion-reply'),'online');link.href=config.siteUrl+'#discussion';link.target='_blank';link.rel='noopener noreferrer';panel.append(link);}
  let stateKey = offline?'offline':configured?'load':'pending';message.textContent=tr(stateKey);
  function metadata(item, category) {
    const meta=el('div','discussion-meta'),name=el('span','discussion-name',item.name),date=el('time');date.dateTime=item.createdAt;
    date.textContent=new Date(item.createdAt).toLocaleString(lang==='zh'?'zh-CN':'en-GB',{dateStyle:'medium',timeStyle:'short'});meta.append(name,date);
    if(category){const label=el('span','discussion-category',tr('areas')[category]||tr('areas').general);label.dataset.discussionArea=category;meta.append(label);}
    return meta;
  }
  function renderThreads() {
    const drafts=new Map([...list.querySelectorAll('.discussion-thread')].map(n=>[n.id,n.querySelector('.discussion-inline-form')]));
    list.replaceChildren();
    for(const item of threads){
      const thread=el('article','discussion-thread');thread.id='discussion-thread-'+item.id;
      thread.append(metadata(item,item.category),el('p','discussion-body',item.body));
      if(item.replies?.length){const replies=el('div','discussion-replies');for(const reply of item.replies){const r=el('div','discussion-response');r.append(metadata(reply),el('p','discussion-body',reply.body));replies.append(r);}thread.append(replies);}
      if(item.replyNext){const earlier=button('earlier','discussion-more');earlier.addEventListener('click',async()=>{
        earlier.disabled=true;
        try{const data=await request('GET',null,{thread:item.id,replyBefore:item.replyNext});const older=data.threads?.[0];if(!older)throw new Error('invalid_response');item.replies=[...new Map([...older.replies,...item.replies].map(r=>[r.id,r])).values()];item.replyNext=older.replyNext;renderThreads();}
        catch{setStatus(announcement,'error');earlier.disabled=false;}
      });thread.append(earlier);}
      const replyButton=button('reply','discussion-reply');replyButton.setAttribute('aria-expanded','false');
      replyButton.addEventListener('click',()=>{
        const existing=thread.querySelector('.discussion-inline-form');
        if(existing){existing.querySelector('textarea').focus();return;}
        const container=el('div','discussion-inline-form');container.id='discussion-reply-'+item.id;
        container.append(labelText(el('h4'),'replyTo'),form(item.id));const cancel=button('cancel','discussion-cancel');
        cancel.addEventListener('click',()=>{const current=container.closest('.discussion-thread')?.querySelector('.discussion-reply');container.remove();if(current){current.setAttribute('aria-expanded','false');current.focus();}});container.append(cancel);thread.append(container);replyButton.setAttribute('aria-controls',container.id);replyButton.setAttribute('aria-expanded','true');container.querySelector('input').focus();
      });
      thread.append(replyButton);list.append(thread);
      const savedForm=drafts.get(thread.id);if(savedForm){thread.append(savedForm);replyButton.setAttribute('aria-expanded','true');replyButton.setAttribute('aria-controls',savedForm.id);}
    }
  }
  async function refreshThread(id){
    const data=await request('GET',null,{thread:id});const updated=data.threads?.[0];
    if(!updated)throw new Error('thread_unavailable');
    const index=threads.findIndex(t=>t.id===id);if(index>=0)threads[index]=updated;else threads.unshift(updated);renderThreads();
  }
  async function load(append=false){
    if(loading||!configured)return;
    loading=true;refresh.disabled=true;more.disabled=true;stateKey='load';message.textContent=tr(stateKey);
    try{
      const result=await request('GET',null,append?{before:next}:{});
      if(!Array.isArray(result.threads))throw new Error('invalid_response');
      const keepDrafts=threads.filter(t=>{const node=document.getElementById('discussion-thread-'+t.id);return !!node?.querySelector('.discussion-inline-form textarea')?.value.trim();});
      threads=[...new Map([...(append?threads:[]),...result.threads,...keepDrafts.filter(t=>!result.threads.some(r=>r.id===t.id))].map(t=>[t.id,t])).values()];next=result.next||null;renderThreads();more.hidden=!next;
      stateKey=threads.length?'':'empty';message.textContent=stateKey?tr(stateKey):'';
    }catch(error){stateKey='error';message.textContent=tr(stateKey);}
    finally{loading=false;refresh.disabled=false;more.disabled=false;}
  }
  refresh.addEventListener('click',()=>load(false));more.addEventListener('click',()=>load(true));
  window.addEventListener('dunhuang:language',e=>{lang=e.detail?.lang||window.DUNHUANG_EXHIBITION?.getState().lang||'en';languageText();});
  if(configured){
    if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)&&!started){started=true;observer.disconnect();load();}},{rootMargin:'300px'});observer.observe(host);}else load();
  }
  window.DUNHUANG_DISCUSSION={refresh:()=>load(false),getState:()=>({configured,threads:threads.length,loading})};
})();
