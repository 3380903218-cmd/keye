/* An event-centred reading of existing Gephi edges. The source graph is unchanged. */
(() => {
  'use strict';
  const D=window.DUNHUANG_NETWORK,api=window.DUNHUANG_NETWORK_VIEW;
  if(!D||!api)return;
  const $=id=>document.getElementById(id),N=new Map(D.nodes.map(n=>[n.id,n])),E=new Map(D.edges.map(e=>[e.id,e]));
  const events=new Map(D.events.map(e=>[e.EventId,e])),proof=new Map(D.evidence.map(e=>[e.id,e])),sources=new Map(D.sources.map(s=>[s.SourceId,s]));
  const G={mode:'guide',caseId:'N012',eventId:'KE007',edgeId:null,expanded:false};
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const language=()=>window.DUNHUANG_EXHIBITION.getState().lang;
  const words={
    en:{guide:'Relationship guide',graph:'Full Gephi network',case:'Related records',choose:'Choose a record',previous:'Previous record',next:'Next record',inputs:'People & materials',event:'Recorded activity',outputs:'Documents, images & destinations',read:'Read each arrow as the role stated on its card. All arrows below are original dataset edges.',noOutputs:'No resulting document or receiving institution is linked to this activity in the dataset.',noInputs:'No incoming relationship is recorded for this activity.',record:'Record',of:'of',relations:'recorded relationships',nodes:'nodes',source:'Open source ↗',evidence:'Sources and limits',selected:'Selected relationship',eventEvidence:'Evidence for the activity',limit:'What remains uncertain',more:'Show the remaining relationships',fewer:'Show fewer relationships',scope:'Expedition context; not limited to Dunhuang manuscripts',proposal:'Proposal recorded; completion not established',promise:'Promise recorded; fulfilment not established',ongoing:'Work in progress',action:'Activity reported in the sources',inspect:'Select a card to read the evidence for that relationship.',full:'Inspect this relationship in the full network ↗',fullEvent:'Inspect this activity in the full network ↗',map:'View this event on the route map ↗',arrangement:'This guide rearranges the recorded links around one activity. It does not imply direct contact between every participant. The full view retains the Gephi layout.',original:'Original record fields',none:'No evidence entry is attached to this record.',back:'Read this as a relationship guide',allLabel:'Open the full Gephi network',originalRole:'Recorded role',support:'Evidence notes apply to the claims they state; they do not independently verify every field.',material:'Material circulation',knowledge:'Knowledge transmission'},
    zh:{guide:'关系导读',graph:'完整 Gephi 网络',case:'相关记录',choose:'选择一条记录',previous:'上一条',next:'下一条',inputs:'人物与所涉材料',event:'记录的活动',outputs:'文书、图像与去向',read:'箭头表示卡片上注明的角色。以下均为原数据中已有的连线。',noOutputs:'本项目尚未给这项活动关联具体的成果文书或接收机构。',noInputs:'本项目尚未给这项活动关联入向记录。',record:'记录',of:'/',relations:'条原始关系',nodes:'个节点',source:'查阅来源 ↗',evidence:'出处与证据限度',selected:'当前选中的关系',eventEvidence:'这项活动的依据',limit:'尚不能确定的内容',more:'展开其余关系',fewer:'收起部分关系',scope:'考察背景：所涉材料不限于敦煌写本',proposal:'已提出方案，尚不能据此认定完成',promise:'已记录承诺，尚不能据此认定履行',ongoing:'工作正在进行',action:'来源记载的活动',inspect:'点击人物或材料卡片，可查看这条关系的依据。',full:'在完整网络中查看这条关系 ↗',fullEvent:'在完整网络中查看这项活动 ↗',map:'在路线地图中查看该事件 ↗',arrangement:'导读按一项活动重排原有连线，不据共同参与推定人物之间的直接联系。完整视图保留 Gephi 布局。',original:'原始记录字段',none:'这条记录未附证据条目。',back:'用关系导读查看',allLabel:'打开完整 Gephi 网络',originalRole:'原记录角色',support:'证据条目只支持其中说明的主张，不独立证明这条记录的全部字段。',material:'实物流转',knowledge:'知识传播'}
  };
  const t=k=>words[language()][k],name=n=>n.label[language()]||n.label.en;
  const types={Person:['Person','人物'],Collection:['Manuscript batch / collection','文献批次／收藏'],Institution:['Institution','机构'],Government:['Government institution','政府机构'],Work:['Letter / document','信函／文书'],Representation:['Image / copy','图像／复制品'],Event:['Activity','活动'],Object:['Individual object','单件文献'],Expedition:['Expedition','考察队'],PublicationOrganisation:['Publisher','出版机构']};
  // The reading guide follows the exhibition palette; original Gephi colours stay in the full graph.
  const guideColors={Person:'#788269',Collection:'#a08a65',Institution:'#7c806b',Government:'#7c806b',Work:'#956c52',Representation:'#968769',Event:'#9a775d',Object:'#a08a65',Expedition:'#788269',PublicationOrganisation:'#956c52'};
  const guideLineColors={'Knowledge transmission':'#85866f','Physical circulation':'#aa7858','Cross-layer':'#8b7965'};
  const lotus='<svg class="guide-lotus" viewBox="0 0 80 32" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M40 26C29 19 30 9 40 2C50 9 51 19 40 26Z"/><path d="M40 26C24 27 13 19 11 8C25 9 35 16 40 26ZM40 26C56 27 67 19 69 8C55 9 45 16 40 26Z"/><path d="M40 27C23 32 8 28 2 19C17 17 31 21 40 27ZM40 27C57 32 72 28 78 19C63 17 49 21 40 27Z"/><path d="M16 31H64"/></g></svg>';
  const aliases={KE007:['Writing the inspection memorandum','撰写检查备忘录'],KE005:['Unpacking, cataloguing and listing','拆箱、编目与列单'],MAP_KE012:['Ministry telegram','学部发出电报'],KE009:['Displaying manuscripts in Beijing','在北京出示写本'],KE006:['Examining manuscripts in London','在伦敦检查写本'],B0010:['Stein Chinese manuscripts examined in London','在伦敦检查的斯坦因中国写本'],W001:['Inspection memorandum (working title)','检查备忘录（工作命名）']};
  const label=n=>aliases[n.id]?.[language()==='zh'?1:0]||name(n);
  const role=e=>window.DUNHUANG_RELATION_TEXT(e,language(),e.label);
  const ids=v=>String(v||'').split(';').filter(Boolean);
  const incident=id=>D.edges.filter(e=>e.source===id||e.target===id);
  const currentEdges=()=>incident(G.eventId);
  function relatedEvents(id){
    if(events.has(id))return [id];
    return [...new Set(incident(id).filter(e=>e.attributes.Layer==='Knowledge transmission').flatMap(e=>[e.source,e.target]).filter(x=>events.has(x)))].sort((a,b)=>a==='KE007'?-1:b==='KE007'?1:Number(events.get(a).YearStart)-Number(events.get(b).YearStart)||a.localeCompare(b));
  }
  const evDate=ev=>ev.EventId==='KE007'?(language()==='zh'?'1910年；具体撰写日期未定':'1910; exact drafting date unresolved'):(language()==='zh'?ev.DateText:ev.english.date);
  const evPlace=ev=>ev.EventId==='KE007'?(language()==='zh'?'与伦敦的写本检查相关；成稿地点未核实':'Related to the London examination; drafting location unconfirmed'):(language()==='zh'?ev.Place:ev.english.place);
  const evNote=ev=>language()==='zh'?(ev.displayNoteZH||ev.NotesZH):ev.english.note;
  function link(url,text){try{const u=new URL(url);if(!['https:','http:'].includes(u.protocol))return esc(text);return `<a href="${esc(u.href)}" target="_blank" rel="noopener noreferrer">${esc(text)}</a>`;}catch{return esc(text);}}
  const lead={
    KE007:["At Stein’s request, Pelliot wrote an inspection memorandum. Extracts were printed in Stein’s Serindia.",'斯坦因请伯希和撰写检查备忘录。斯坦因的 Serindia 第二卷刊出了备忘录摘文。'],
    KE005:['Andrews coordinated the work. Lorimer joined in mid-October 1909, with Droop also working on the collection. These Stein materials were not necessarily all Dunhuang manuscripts.','安德鲁斯主持材料整理，洛里默于1909年10月中旬加入，德鲁普也参与工作。这些斯坦因材料并非全为敦煌写本。'],
    MAP_KE012:["The ministry sent a telegram from Beijing to the Governor-General’s office in Lanzhou. Its dispatch and intended destination are recorded; receipt and execution dates remain unresolved.",'清学部从北京向兰州的陕甘总督机构发出电报。记录确认发出与目的机构，收讫与执行日期尚待核实。'],
    MAP_KE011:['Eighteen named attendees are connected through the same banquet record. Shared attendance does not establish correspondence between every pair or the presence of original manuscripts.','18位具名参与者通过同一场宴会记录关联。共同出席不证明任意两人之间有直接通信，也不证明原卷当时在场。']
  };
  const host=$('network'),shell=$('networkShell');
  const panel=document.createElement('div');panel.id='networkGuide';panel.className='relationship-guide';
  panel.setAttribute('role','region');panel.setAttribute('aria-label','Relationship guide');
  shell.querySelector('.network-grid').insertAdjacentElement('beforebegin',panel);
  function mode(value){
    G.mode=value;host.dataset.networkView=value;panel.hidden=value!=='guide';
    document.querySelector('.network-grid').hidden=value==='guide';
    document.querySelector('.network-advanced').hidden=value==='guide';
    $('networkLegend').hidden=value==='guide';
    document.querySelector('.network-node-list').hidden=value==='guide';
    document.querySelector('.network-reading-note').hidden=value==='guide';
  }
  function syncButtons(){
    document.querySelectorAll('.network-guides [data-network-guide]').forEach(n=>n.setAttribute('aria-pressed',String(G.mode==='graph'?n.dataset.networkGuide==='all':n.dataset.networkGuide===G.caseId)));
  }
  function proofHTML(ev){
    const selected=G.edgeId?E.get(G.edgeId):null,a=selected?.attributes||ev;
    const entries=ids(a.EvidenceIds).map(id=>proof.get(id)).filter(Boolean);
    let html=`<div class="guide-proof" id="guideEvidence" aria-live="polite"><p class="guide-small-title">${esc(selected?t('selected'):t('eventEvidence'))}</p>`;
    if(selected)html+=`<p class="guide-statement"><b>${esc(label(N.get(selected.source)))}</b><span> — ${esc(role(selected))} → </span><b>${esc(label(N.get(selected.target)))}</b></p>`;
    html+=`<h4>${esc(t('evidence'))}</h4>`;
    if(!entries.length)html+=`<p>${esc(t('none'))}</p>`;
    for(const [i,p] of entries.entries()){
      const s=sources.get(p.source),claim=language()==='zh'?p.claim:p.claimEN,limit=language()==='zh'?p.limit:p.limitEN;
      const locator=language()==='zh'?p.printed:String(p.printed||'').replace(/印刷/g,'Printed pp. ').replace(/NII扫描/g,'NII scan ').replace(/；/g,'; ');
      const body=`<p class="guide-claim">${esc(claim)}</p><p class="guide-limit"><b>${esc(t('limit'))}</b> ${esc(limit)}</p><p class="guide-citation">${esc(s?.Author||p.source)} · ${esc(s?.Year||'')} · ${esc(locator)} ${s?link(s.URL,t('source')):''}</p>`;
      html+=i===0?body:`<details class="guide-extra-proof"><summary>${esc(s?.Author||p.source)} · ${esc(s?.Year||'')} · ${esc(p.id)}</summary>${body}</details>`;
    }
    html+=`<details class="guide-original"><summary>${esc(t('original'))}</summary><p>${esc(selected?.id||ev.EventId)}${selected?'<br>'+esc(t('originalRole'))+': '+esc(a.Role):''}<br>Evidence: ${esc(a.EvidenceIds||'—')}<br>Sources: ${esc(a.SourceIds||'—')}</p></details><p class="guide-support">${esc(t('support'))}</p><button class="guide-link" data-guide-full>${esc(selected?t('full'):t('fullEvent'))}</button>`;
    if(window.DUNHUANG_DATA.flows.some(f=>f.visible&&f.eventIds.includes(ev.EventId)))html+=`<button class="guide-link" data-guide-map>${esc(t('map'))}</button>`;
    return html+'</div>';
  }
  function nodeCard(edge,incoming){
    const n=N.get(incoming?edge.source:edge.target),kind=types[n.type]?.[language()==='zh'?1:0]||n.type;
    return `<button class="relation-card${G.edgeId===edge.id?' selected':''}" data-guide-edge="${esc(edge.id)}" aria-pressed="${G.edgeId===edge.id}" aria-controls="guideEvidence" style="--node-color:${guideColors[n.type]||'#8b7965'}"><span class="relation-type"><i aria-hidden="true"></i>${esc(kind)}</span><strong>${esc(label(n))}</strong><span class="relation-role">${esc(role(edge))}</span><span class="relation-direction" aria-hidden="true">→</span></button>`;
  }
  function drawLinks(){
    panel.querySelector('.guide-connectors')?.remove();
    if(G.mode!=='guide'||innerWidth<=800)return;
    const diagram=panel.querySelector('.relation-diagram'),activity=panel.querySelector('.activity-card');
    if(!diagram||!activity)return;
    const NS='http://www.w3.org/2000/svg',svg=document.createElementNS(NS,'svg'),bounds=diagram.getBoundingClientRect(),box=activity.getBoundingClientRect();
    svg.classList.add('guide-connectors');svg.setAttribute('width',bounds.width);svg.setAttribute('height',bounds.height);svg.setAttribute('viewBox',`0 0 ${bounds.width} ${bounds.height}`);svg.setAttribute('aria-hidden','true');
    const defs=document.createElementNS(NS,'defs');svg.append(defs);
    const groups=[['.guide-inputs [data-guide-edge]',true],['.guide-outputs [data-guide-edge]',false]];
    for(const [selector,incoming] of groups){
      const cards=[...diagram.querySelectorAll(selector)];
      cards.forEach((card,i)=>{
        const edge=E.get(card.dataset.guideEdge),r=card.getBoundingClientRect(),selected=edge.id===G.edgeId,color=selected?'#984b31':guideLineColors[edge.attributes.Layer]||'#8b7965';
        const marker=document.createElementNS(NS,'marker'),id='guide-arrow-'+(incoming?'in':'out')+'-'+i;
        for(const [k,v] of Object.entries({id,viewBox:'0 0 10 10',refX:8,refY:5,markerWidth:10,markerHeight:10,markerUnits:'userSpaceOnUse',orient:'auto'}))marker.setAttribute(k,v);
        const tip=document.createElementNS(NS,'path');tip.setAttribute('d','M3 2L8 5L3 8');tip.setAttribute('fill','none');tip.setAttribute('stroke',color);tip.setAttribute('stroke-width',selected?'1.8':'1.3');tip.setAttribute('stroke-linecap','round');tip.setAttribute('stroke-linejoin','round');marker.append(tip);defs.append(marker);
        const cardY=r.top+r.height/2-bounds.top,activityY=Math.max(box.top-bounds.top+18,Math.min(box.bottom-bounds.top-18,cardY));
        const a=incoming?[r.right-bounds.left+3,cardY]:[box.right-bounds.left+3,activityY];
        const b=incoming?[box.left-bounds.left-6,activityY]:[r.left-bounds.left-6,cardY];
        const p=document.createElementNS(NS,'path');
        p.setAttribute('d',`M${a[0]},${a[1]} L${b[0]},${b[1]}`);
        p.setAttribute('fill','none');p.setAttribute('stroke',color);p.setAttribute('stroke-width',selected?'1.9':'1.3');p.setAttribute('stroke-linecap','round');p.setAttribute('stroke-linejoin','round');p.setAttribute('marker-end',`url(#${id})`);p.dataset.guideConnector=edge.id;
        if(['Proposal made','Recorded promise'].includes(edge.attributes.ProcessState))p.setAttribute('stroke-dasharray','5 4');
        svg.append(p);
      });
    }
    diagram.prepend(svg);
  }
  function render(){
    if(G.mode!=='guide')return;const ev=events.get(G.eventId);if(!ev)return;
    const options=relatedEvents(G.caseId),at=options.indexOf(G.eventId),edges=currentEdges();
    const rank=e=>/请求者|requester/.test(e.attributes.Role)?0:N.get(e.source).type==='Person'?1:2;
    const incoming=edges.filter(e=>e.target===ev.EventId).sort((a,b)=>rank(a)-rank(b));
    const outgoing=edges.filter(e=>e.source===ev.EventId),shown=G.expanded?incoming:incoming.slice(0,6);
    const nodeCount=new Set(edges.flatMap(e=>[e.source,e.target])).size;
    const state=ev.ProcessState==='Proposal made'?'proposal':ev.ProcessState==='Recorded promise'?'promise':ev.ProcessState==='Work in progress'?'ongoing':'action';
    const summary=lead[ev.EventId]?.[language()==='zh'?1:0]||evNote(ev);
    panel.setAttribute('aria-label',t('guide'));
    panel.innerHTML=`<header class="guide-header"><div><p class="guide-small-title">${esc(t('guide'))} · ${esc(t('record'))} ${at+1} ${esc(t('of'))} ${options.length}</p></div><div class="guide-selector"><label for="guideEvent">${esc(t('choose'))}</label><select id="guideEvent">${options.map(id=>`<option value="${esc(id)}"${id===G.eventId?' selected':''}>${esc(label(N.get(id)))}</option>`).join('')}</select><div class="guide-paging"><button data-guide-step="-1"${at===0?' disabled':''}>← ${esc(t('previous'))}</button><button data-guide-step="1"${at===options.length-1?' disabled':''}>${esc(t('next'))} →</button></div></div></header>

    <div class="relation-diagram"><section class="guide-inputs"><h4><span>1</span>${esc(t('inputs'))}</h4><div class="relation-cards">${shown.map(e=>nodeCard(e,true)).join('')||`<p class="guide-no-record">${esc(t('noInputs'))}</p>`}</div>${incoming.length>6?`<button class="guide-expand" data-guide-expand>${esc(G.expanded?t('fewer'):t('more'))}${G.expanded?'':' ('+(incoming.length-6)+')'}</button>`:''}</section>
    <section class="guide-activity"><h4><span>2</span>${esc(t('event'))}</h4><article class="activity-card ${state}"><p class="activity-layer">${esc(t(ev.Layer==='Physical circulation'?'material':'knowledge'))}</p><p class="activity-state">${esc(t(state))}</p>${lotus}<h5>${esc(label(N.get(ev.EventId)))}</h5><p class="activity-date">${esc(evDate(ev))}</p><p class="activity-place">${esc(evPlace(ev))}</p>${ev.Scope!=='Dunhuang materials'?`<p class="activity-scope">${esc(t('scope'))}</p>`:''}</article></section>
    <section class="guide-outputs"><h4><span>3</span>${esc(t('outputs'))}</h4><div class="relation-cards">${outgoing.map(e=>nodeCard(e,false)).join('')||`<p class="guide-no-record">${esc(t('noOutputs'))}</p>`}</div></section></div>
    <p class="guide-lead guide-context">${esc(summary)}</p><div class="guide-reading"><p>${esc(t('read'))}</p><span>${nodeCount} ${esc(t('nodes'))} · ${edges.length} ${esc(t('relations'))}${shown.length+outgoing.length<edges.length?' · '+(language()==='zh'?'当前显示 ':'shown ')+(shown.length+outgoing.length):''}</span></div>
    <p class="guide-card-help">${esc(t('inspect'))}</p>${proofHTML(ev)}<p class="guide-arrangement">${esc(t('arrangement'))}</p>`;
    $('guideEvent').addEventListener('change',e=>{G.eventId=e.target.value;G.edgeId=null;G.expanded=false;render();$('guideEvent').focus({preventScroll:true});});
    panel.querySelectorAll('[data-guide-step]').forEach(b=>b.addEventListener('click',()=>{G.eventId=options[at+Number(b.dataset.guideStep)];G.edgeId=null;G.expanded=false;render();}));
    panel.querySelectorAll('[data-guide-edge]').forEach(b=>b.addEventListener('click',()=>{
      G.edgeId=b.dataset.guideEdge;render();panel.querySelector(`[data-guide-edge="${G.edgeId}"]`)?.focus({preventScroll:true});
      if(innerWidth<800)$('guideEvidence').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
    }));
    panel.querySelector('[data-guide-expand]')?.addEventListener('click',()=>{G.expanded=!G.expanded;render();});
    panel.querySelector('[data-guide-full]')?.addEventListener('click',()=>{
      const edge=G.edgeId;mode('graph');api.reset();syncButtons();requestAnimationFrame(()=>{edge?api.selectEdge(edge):api.selectNode(G.eventId);shell.scrollIntoView({block:'start',behavior:'instant'});});
    });
    panel.querySelector('[data-guide-map]')?.addEventListener('click',()=>window.DUNHUANG_EXHIBITION.selectEvent(G.eventId));
    syncButtons();
    requestAnimationFrame(drawLinks);
  }
  function show(id){
    if(id==='all'){mode('graph');api.reset();syncButtons();requestAnimationFrame(()=>api.fitVisible());return true;}
    const list=relatedEvents(id);if(!list.length){mode('graph');api.reset();syncButtons();requestAnimationFrame(()=>api.selectNode(id));return false;}
    G.caseId=id;G.eventId=list.includes('KE007')?'KE007':list[0];G.edgeId=null;G.expanded=false;
    mode('guide');api.focusNode(id);render();return true;
  }
  window.addEventListener('dunhuang:network-select',e=>{
    if(G.mode!=='guide')return;
    if(e.detail.kind==='node')show(e.detail.id);
  });
  window.addEventListener('dunhuang:language',()=>{render();syncButtons();});
  window.addEventListener('resize',()=>requestAnimationFrame(drawLinks));
  window.DUNHUANG_NETWORK_GUIDE={show,syncButtons,getState:()=>({...G,edgeIds:currentEdges().map(e=>e.id),nodeIds:[...new Set(currentEdges().flatMap(e=>[e.source,e.target]))]})};
  show('N012');
})();
