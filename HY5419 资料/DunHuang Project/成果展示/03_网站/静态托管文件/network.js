/* Dunhuang network: local SVG exploration of the user's saved Gephi layout. */
(() => {
  'use strict';
  const D=window.DUNHUANG_NETWORK, $=id=>document.getElementById(id), NS='http://www.w3.org/2000/svg';
  if(!D||!$('networkGraph'))return;
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const nodes=new Map(D.nodes.map(n=>[n.id,n])), edges=new Map(D.edges.map(e=>[e.id,e]));
  const events=new Map(D.events.map(e=>[e.EventId,e])), sources=new Map(D.sources.map(s=>[s.SourceId,s]));
  const evidence=new Map(D.evidence.map(e=>[e.id,e]));
  const S={lang:window.DUNHUANG_EXHIBITION?.getState().lang||'en',layer:'all',until:1910,context:true,focus:false,labels:false,compact:true,selection:null};
  const camera={x:0,y:0,w:1800,h:1000};
  let visibleNodes=[],visibleEdges=[],hover=null,drag=null,resizeFrame=0;
  const UI={
    en:{compact:'Compact component view',compactCaption:'Compact view · cited additions',kicker:'CHAPTER 02 / KNOWLEDGE TRANSMISSION',title:"Who examined and organised the materials?",intro:"The network records people, institutions and events involved in manuscript acquisition, correspondence, photography, cataloguing and scholarly exchange. Select a node or connection to view recorded roles and sources.",present:'⤢ Presentation mode',exit:'⤢ Exit presentation',all:'All connections',material:'Material circulation',knowledge:'Knowledge transmission',cross:'Cross-layer link',searchLabel:'FIND A PERSON, EVENT OR DOCUMENT',placeholder:'Try Stein, Pelliot or 王圆箓',focus:'Selected neighbourhood',labels:'Show all names',context:'Include expedition context',through:'Through',layout:'Gephi + cited additions · 1900–1910',hint:'Drag to pan · Click a node · Focus the graph or hold ⌘ / Ctrl to scroll-zoom',empty:'No connections for these filters. Use ↺ to reset the view.',note:'Original node sizes and positions come from the author’s Gephi export; added nodes use provisional positions and uniform sizes, without recalculating centrality. Compact view moves unconnected groups closer together; untick it to see the original layout. Size reflects connection count, not historical importance; position is not geographical. An arrow identifies the recorded role, not necessarily physical movement or direct correspondence. Date ranges enter the cumulative view at their earliest year.',downloadGraph:'Expanded Gephi network ↓',downloadData:'Download network & evidence ↓',nodeList:'Browse the visible nodes without the graph',nodes:'nodes',connections:'connections',beginTitle:"Select a person or event",beginCopy:"This graph records material transfers and activities such as correspondence, cataloguing and photography. Select a node to view its related records and sources.",beginHint:'Select a person below, search above, or click any node. Selecting a line reveals its direction and recorded role.',references:'Research references',referenceNote:'These references support specific claims. They are not independent proof of every attribute of a person or event.',connected:'Connected items',date:'Date & precision',place:'Place / documentary context',scope:'Evidential scope',process:'Recorded action',reading:'Research summary',original:'Original Chinese research note',clear:'← Clear selection',read:'Read source ↗',map:'View this event on the route map ↗',limits:'Limits of the evidence',sources:'Sources for this item',proposed:'Proposal / promise',update:'Network additions: 30 Oct 2026',unrecorded:'Not independently established',nomatch:'No matching nodes.',graphA11y:'Interactive network. Click a node or line; use the searchable node list for an alternative view.',panelA11y:'Selected network item',layersA11y:'Filter network layers',legendA11y:'Node types and connection layers',in:'incoming',out:'outgoing',zoomIn:'Zoom in',zoomOut:'Zoom out',fit:'Fit visible network',reset:'Reset filters and selection',edge:'Recorded relationship',source:'Source',target:'Target'},
    zh:{compact:'紧凑排列不同连通组',compactCaption:'紧凑视图 · 含文献补充',kicker:'第二章 / 知识传播',title:"谁参与了检查和整理？",intro:"网络整理了文献取得、通信、摄影、编目与学术交流中的人物、机构和事件。点击节点或连线，可查看记录中的角色和资料出处。",present:'⤢ 展演模式',exit:'⤢ 退出展演',all:'全部关系',material:'实物流转',knowledge:'知识传播',cross:'跨层关联',searchLabel:'查找人物、事件或文献',placeholder:'试试 Stein、Pelliot 或 王圆箓',focus:'仅看选中节点的邻域',labels:'显示全部名称',context:'包含考察相关背景',through:'截至',layout:'Gephi及文献补充 · 1900—1910',hint:'拖动画布平移 · 点击节点 · 聚焦图形或按住 ⌘ / Ctrl 滚动缩放',empty:'当前筛选下没有关系。点击 ↺ 可恢复完整网络。',note:'原节点的位置与相对大小来自作者保存的Gephi成果；新增节点采用暂定位置与统一大小，未重新计算中心性。紧凑视图仅平移不连通组，取消勾选即可查看原始布局。大小表示连接数量，不直接表示历史重要性；位置不代表地理方位。箭头表达已记录的角色，不必然意味着实物移动或直接通信。时间范围按其最早年份进入累计视图。',downloadGraph:'下载补充版Gephi文件 ↓',downloadData:'下载网络与证据数据 ↓',nodeList:'以列表查看当前可见节点',nodes:'个节点',connections:'条关系',beginTitle:"选择人物或事件",beginCopy:"这张图记录文献转移，以及通信、编目、摄影等活动。选择一个节点，可查看相关记录与资料出处。",beginHint:'点击下面的人物、使用上方搜索框，或直接选择节点。点击线段可查看方向和具体角色。',references:'研究依据',referenceNote:'这些资料各自支持特定主张，不表示每篇来源都独立证明了人物或事件的全部属性。',connected:'相关节点与关系',date:'时间与精度',place:'地点／文书语境',scope:'证据范围',process:'记录的活动状态',reading:'研究说明',original:'中文整理原注',clear:'← 清除选择',read:'查阅来源 ↗',map:'在路线地图中查看该事件 ↗',limits:'证据的限度',sources:'本条相关来源',proposed:'提议／承诺',update:'关系补充：2026-10-30',unrecorded:'尚未独立落实',nomatch:'没有匹配的节点。',graphA11y:'可互动关系网络。点击节点或连线；也可通过搜索与节点列表查阅。',panelA11y:'选中的网络记录',layersA11y:'传播层筛选',legendA11y:'节点类型与传播关系图例',in:'入向',out:'出向',zoomIn:'放大',zoomOut:'缩小',fit:'适应当前网络',reset:'恢复筛选与选择',edge:'记录的关系',source:'来源端',target:'指向端'}
  };
  const typeZH={Person:'人物',Event:'事件',Collection:'文献批次',Institution:'机构',Government:'政府机构',Expedition:'考察队',Object:'单件文献',Representation:'图像／复制载体',Work:'信函／报告等作品',PublicationOrganisation:'出版机构'};
  const typeEN={PublicationOrganisation:'Publication organisation',Work:'Letter / report / work',Representation:'Image / representation',Object:'Individual object'};
  const scopeZH={'Dunhuang materials':'敦煌材料','General Stein collection context':'一般 Stein 收藏工作','Cross-context':'跨语境','Site documentation context':'遗址影像记录','Expedition communication context':'考察讲座／通信背景','Expedition preparation context':'考察准备背景'};
  const processZH={'Reported action':'来源记载的活动','Proposal made':'已提出的方案','Recorded promise':'已记录的承诺','Work in progress':'正在进行的工作'};
  const relations={subject_of_event:['Subject of event','事件涉及的对象'],transfer_to:['Recipient','接收方'],transfer_from:['Transfer source','交出／提供方'],participant_in_event:['Participant in event','参与事件'],collection_associated_with:['Collection associated with','相关考察收藏'],produces_work:['Produces a text / work','形成文字作品'],produces_representation:['Produces an image / copy','形成图像／复制品'],dispatch_destination:['Intended dispatch destination','送寄目的方'],addressed_to:['Addressed to','文书指向'],circulates_representation:['Circulates an image / copy','传播图像／复制品'],presents_representation:['Presents an image','展示图像'],contains_representation:['Contains an image','包含图像'],photographic_source_creator:['Creates source photograph','拍摄原始图像'],documented_in:['Documented in','记载于'],author_of_manifestation:['Author of this version','该版本的作者'],publisher_of_manifestation:['Publisher of this version','该版本的出版者'],deposit_at:['Deposited at','存放于'],subset_of_collection:['Subset of collection','属于收藏子集'],annotates_work:['Annotates a document','补注文书']};
  const t=k=>UI[S.lang][k]??k, name=n=>n.label[S.lang]||n.label.en;
  const type=n=>S.lang==='zh'?(typeZH[n.type]||n.type):(typeEN[n.type]||n.type);
  const scope=v=>S.lang==='zh'?(scopeZH[v]||v):v;
  const process=v=>S.lang==='zh'?(processZH[v]||v):v;
  const relation=e=>window.DUNHUANG_RELATION_TEXT?.(e,S.lang,(relations[e.attributes.Relation]||[e.label,e.attributes.Role])[S.lang==='zh'?1:0])||(relations[e.attributes.Relation]||[e.label,e.attributes.Role])[S.lang==='zh'?1:0];
  const ids=value=>String(value||'').split(';').filter(Boolean);
  const radius=n=>n.size*.6+2;
  // Translate whole disconnected components only. Original coordinates stay intact.
  const adjacency=new Map(D.nodes.map(n=>[n.id,new Set()]));
  for(const e of D.edges){adjacency.get(e.source).add(e.target);adjacency.get(e.target).add(e.source);}
  const visited=new Set(),components=[];
  for(const n of D.nodes){
    if(visited.has(n.id))continue;
    const stack=[n.id],component=[];
    while(stack.length){const id=stack.pop();if(visited.has(id))continue;visited.add(id);component.push(nodes.get(id));for(const other of adjacency.get(id))if(!visited.has(other))stack.push(other);}
    components.push(component);
  }
  components.sort((a,b)=>b.length-a.length);
  const compactPoints=new Map(D.nodes.map(n=>[n.id,{x:n.x,y:n.y}]));
  const main=components[0],mainRight=Math.max(...main.map(n=>n.x)),mainTop=Math.min(...main.map(n=>n.y));
  components.slice(1).forEach((group,i)=>{
    const cx=(Math.min(...group.map(n=>n.x))+Math.max(...group.map(n=>n.x)))/2;
    const cy=(Math.min(...group.map(n=>n.y))+Math.max(...group.map(n=>n.y)))/2;
    const dx=mainRight+350-cx,dy=mainTop+110+i*230-cy;
    group.forEach(n=>compactPoints.set(n.id,{x:n.x+dx,y:n.y+dy}));
  });
  const point=n=>S.compact?compactPoints.get(n.id):n;
  function el(tag,attributes={},parent){const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attributes))e.setAttribute(k,String(v));if(parent)parent.append(e);return e;}
  function link(url,label){try{const u=new URL(url);if(!['https:','http:'].includes(u.protocol))return esc(label);return `<a href="${esc(u.href)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`;}catch{return esc(label);}}
  function selectedNode(){return S.selection?.kind==='node'?nodes.get(S.selection.id):null;}
  function baseEdges(){return D.edges.filter(e=>(S.layer==='all'||e.attributes.Layer===S.layer)&&(S.context||e.attributes.Scope==='Dunhuang materials')&&Number(e.attributes.YearStart||1900)<=S.until);}
  function calculateVisible(){
    visibleEdges=baseEdges();
    if(S.focus&&selectedNode())visibleEdges=visibleEdges.filter(e=>e.source===S.selection.id||e.target===S.selection.id);
    const set=new Set(visibleEdges.flatMap(e=>[e.source,e.target]));visibleNodes=D.nodes.filter(n=>set.has(n.id));
  }
  function activeSelection(){
    if(hover)return {kind:'node',id:hover};
    if(S.selection?.kind==='node'&&visibleNodes.some(n=>n.id===S.selection.id))return S.selection;
    if(S.selection?.kind==='edge'&&visibleEdges.some(e=>e.id===S.selection.id))return S.selection;
    return null;
  }
  function paint(){
    const active=activeSelection(), brightNodes=new Set(),brightEdges=new Set();
    if(active?.kind==='node'){
      brightNodes.add(active.id);
      for(const e of visibleEdges)if(e.source===active.id||e.target===active.id){brightEdges.add(e.id);brightNodes.add(e.source);brightNodes.add(e.target);}
    }else if(active){const e=edges.get(active.id);brightEdges.add(e.id);brightNodes.add(e.source);brightNodes.add(e.target);}
    $('networkNodes').querySelectorAll('.network-node').forEach(g=>{
      const id=g.dataset.node,n=nodes.get(id),lit=brightNodes.has(id);
      g.classList.toggle('dimmed',Boolean(active)&&!lit);g.classList.toggle('active',lit);
      g.querySelector('.network-name').style.display=S.labels||lit||n.size>=11.5?'':'none';
    });
    $('networkEdges').querySelectorAll('.network-link').forEach(g=>{g.classList.toggle('dimmed',Boolean(active)&&!brightEdges.has(g.dataset.edge));g.classList.toggle('active',brightEdges.has(g.dataset.edge));});
    if(!S.labels){
      const occupied=[];
      const labels=[...$('networkNodes').querySelectorAll('.network-node')].sort((a,b)=>{
        const priority=g=>(active?.kind==='node'&&active.id===g.dataset.node?1000:brightNodes.has(g.dataset.node)?100:0)+nodes.get(g.dataset.node).size;
        return priority(b)-priority(a);
      });
      for(const g of labels){
        const label=g.querySelector('.network-name');if(label.style.display==='none')continue;
        const r=label.getBoundingClientRect();
        if(occupied.some(b=>r.left<b.right+5&&r.right>b.left-5&&r.top<b.bottom+3&&r.bottom>b.top-3))label.style.display='none';
        else occupied.push(r);
      }
    }
  }
  function view(){
    $('networkGraph').setAttribute('viewBox',`${camera.x} ${camera.y} ${camera.w} ${camera.h}`);
    const unit=camera.w/Math.max($('networkGraph').clientWidth,280);
    $('networkNodes').querySelectorAll('.network-name').forEach(e=>{
      const n=nodes.get(e.parentElement.dataset.node);e.setAttribute('font-size',unit*14);
      const width=[...e.textContent].reduce((sum,c)=>sum+(c.codePointAt(0)>255?14:7.5),0)*unit;
      const flip=point(n).x+radius(n)+unit*6+width>camera.x+camera.w-unit*16;
      e.setAttribute('text-anchor',flip?'end':'start');e.setAttribute('dx',(flip?-1:1)*(radius(n)+unit*6));e.setAttribute('dy',unit*3.7);
    });
  }
  function fit(list=visibleNodes){
    if(!list.length){list=D.nodes;}
    const xs=list.map(n=>point(n).x),ys=list.map(n=>point(n).y),cx=(Math.min(...xs)+Math.max(...xs))/2,cy=(Math.min(...ys)+Math.max(...ys))/2;
    let w=Math.max(240,Math.max(...xs)-Math.min(...xs))*1.25,h=Math.max(220,Math.max(...ys)-Math.min(...ys))*1.3;
    const aspect=Math.max($('networkGraph').clientWidth,280)/Math.max($('networkGraph').clientHeight,250);
    if(w/h<aspect)w=h*aspect;else h=w/aspect;
    Object.assign(camera,{x:cx-w/2,y:cy-h/2,w,h});view();paint();
  }
  function zoom(factor,anchor){
    const w=Math.min(6500,Math.max(140,camera.w*factor)),ratio=w/camera.w;
    const p=anchor||[camera.x+camera.w/2,camera.y+camera.h/2];
    Object.assign(camera,{x:p[0]-(p[0]-camera.x)*ratio,y:p[1]-(p[1]-camera.y)*ratio,w,h:camera.h*ratio});view();paint();
  }
  function toggle(key){return Boolean(['Proposal made','Recorded promise'].includes(key));}
  function renderGraph(){
    calculateVisible();$('networkDefs').replaceChildren();$('networkEdges').replaceChildren();$('networkNodes').replaceChildren();
    const markerIds=new Map();
    for(const e of visibleEdges){
      if(!markerIds.has(e.color)){
        const id='net-arrow-'+markerIds.size;markerIds.set(e.color,id);
        const marker=el('marker',{id,viewBox:'0 0 8 8',refX:7,refY:4,markerWidth:6,markerHeight:6,orient:'auto',markerUnits:'strokeWidth'},$('networkDefs'));
        el('path',{d:'M0 1L7 4L0 7Z',fill:e.color},marker);
      }
      const na=nodes.get(e.source),nb=nodes.get(e.target),a=point(na),b=point(nb),len=Math.hypot(b.x-a.x,b.y-a.y)||1,dx=(b.x-a.x)/len,dy=(b.y-a.y)/len;
      const x1=a.x+dx*(radius(na)+1),y1=a.y+dy*(radius(na)+1),x2=b.x-dx*(radius(nb)+3),y2=b.y-dy*(radius(nb)+3);
      const g=el('g',{class:'network-link'+(toggle(e.attributes.ProcessState)?' proposal':''),'data-edge':e.id,role:'button',tabindex:0,'aria-label':`${name(na)} → ${name(nb)}: ${relation(e)}`},$('networkEdges'));
      el('line',{class:'network-link-line',x1,y1,x2,y2,stroke:e.color,'marker-end':`url(#${markerIds.get(e.color)})`},g);
      el('line',{class:'network-link-hit',x1,y1,x2,y2},g);
      el('title',{},g).textContent=`${name(na)} → ${name(nb)} · ${relation(e)}`;
      const select=()=>choose('edge',e.id,false);g.addEventListener('click',ev=>{ev.stopPropagation();select();});g.addEventListener('keydown',ev=>{if(['Enter',' '].includes(ev.key)){ev.preventDefault();ev.stopPropagation();select();}});
    }
    for(const n of visibleNodes){
      const g=el('g',{class:'network-node','data-node':n.id,transform:`translate(${point(n).x} ${point(n).y})`,role:'button',tabindex:0,'aria-label':`${name(n)} · ${type(n)}`},$('networkNodes'));
      el('circle',{class:'network-halo',r:radius(n)+5},g);el('circle',{class:'network-dot',r:radius(n),fill:n.color},g);
      el('text',{class:'network-name',x:0,y:0},g).textContent=name(n).length>44?name(n).slice(0,41)+'…':name(n);
      el('title',{},g).textContent=`${name(n)} · ${type(n)}`;
      const select=()=>choose('node',n.id,false);g.addEventListener('click',ev=>{ev.stopPropagation();select();});g.addEventListener('keydown',ev=>{if(['Enter',' '].includes(ev.key)){ev.preventDefault();ev.stopPropagation();select();}});
      g.addEventListener('mouseenter',()=>{hover=n.id;paint();});g.addEventListener('mouseleave',()=>{hover=null;paint();});
    }
    $('networkShell').dataset.filtered=String(visibleNodes.length!==D.nodes.length||visibleEdges.length!==D.edges.length);
    $('networkStatus').textContent=`${visibleNodes.length} ${t('nodes')} · ${visibleEdges.length} ${t('connections')}`;
    $('networkEmpty').hidden=visibleEdges.length>0;
    $('networkNodeList').innerHTML=[...visibleNodes].sort((a,b)=>name(a).localeCompare(name(b),S.lang)).map(n=>`<button data-list-node="${esc(n.id)}">${esc(name(n))}<small>${esc(type(n))}</small></button>`).join('');
    $('networkNodeList').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{choose('node',b.dataset.listNode,true);$('networkShell').scrollIntoView({behavior:'smooth',block:'start'});}));
    view();paint();renderLegend();renderSearch();
  }
  function renderLegend(){
    const order=['Person','Event','Collection','Institution','Government','Expedition','Work','Representation','Object','PublicationOrganisation'];
    const types=order.map(k=>D.nodes.find(n=>n.type===k)).filter(Boolean);
    const layers=['Physical circulation','Knowledge transmission','Cross-layer'];
    $('networkLegend').innerHTML=types.map(n=>`<span><i style="background:${n.color}"></i>${esc(type(n))}</span>`).join('')+layers.map(l=>{
      const e=D.edges.find(e=>e.attributes.Layer===l);return `<span><i class="edge-swatch" style="border-top-color:${e.color}"></i>${esc(l==='Physical circulation'?t('material'):l==='Knowledge transmission'?t('knowledge'):t('cross'))}</span>`;
    }).join('')+`<span><i class="proposal-swatch"></i>${esc(t('proposed'))}</span>`;
  }
  function evidenceHTML(a){
    const list=ids(a.EvidenceIds).map(id=>evidence.get(id)).filter(Boolean);
    if(!list.length)return '';
    return `<h4>${esc(t('references'))}</h4><p class="net-copy">${esc(t('referenceNote'))}</p>`+list.map(e=>{
      const source=sources.get(e.source);
      return `<details class="net-evidence"><summary>${esc(e.id)} · ${esc(source?.Author||e.source)} ${esc(source?.Year||'')}</summary><p>${esc(S.lang==='zh'?e.claim:e.claimEN)}</p><p><strong>${esc(t('limits'))}:</strong> ${esc(S.lang==='zh'?e.limit:e.limitEN)}</p><p class="net-locator">${esc(e.source)} · ${esc(e.printed)}</p>${source?link(source.URL,t('read')):''}</details>`;
    }).join('');
  }
  function sourceHTML(a){
    const list=ids(a.SourceIds).map(id=>sources.get(id)).filter(Boolean);
    if(!list.length)return '';
    return `<details class="net-original"><summary>${esc(t('sources'))} (${list.length})</summary><ol class="net-source-list">`+list.map(s=>`<li>${link(s.URL,s.Title)}<br>${esc(s.SourceId)} · ${esc(s.Author)}</li>`).join('')+'</ol></details>';
  }
  function nodeButton(n,extra=''){return `<button class="net-mini" data-inspect-node="${esc(n.id)}">${esc(name(n))}${extra?`<small>${esc(extra)}</small>`:''}</button>`;}
  function renderInspector(){
    const selection=S.selection,box=$('networkInspector');
    $('networkShell').dataset.hasSelection=String(!!selection);
    if(!selection){
      box.innerHTML=`<p class="net-kicker">1900—1910 / GEPHI</p><h3>${esc(t('beginTitle'))}</h3><p class="net-copy">${esc(t('beginCopy'))}</p><div class="net-related">${['N012','N005','MAP_KE011'].map(id=>nodeButton(nodes.get(id),type(nodes.get(id)))).join('')}</div><p class="net-copy">${esc(t('beginHint'))}</p><p class="net-kicker">${esc(t('update'))}</p>`;
    }else{
      const n=selection.kind==='node'?nodes.get(selection.id):null,e=selection.kind==='edge'?edges.get(selection.id):null,a=(n||e).attributes;
      const ev=events.get(n?.type==='Event'?n.id:a.EventId),date=ev?(S.lang==='zh'?ev.DateText:ev.english.date):'';
      let html=`<button class="net-clear" id="networkClear">${esc(t('clear'))}</button><p class="net-kicker">${esc(n?type(n):t('edge'))}</p><h3>${esc(n?name(n):relation(e))}</h3>`;
      if(e)html+=`<div class="net-related">${nodeButton(nodes.get(e.source),t('source'))}<span aria-hidden="true">↓</span>${nodeButton(nodes.get(e.target),t('target'))}</div>`;
      html+=`<span class="net-tag">${esc(a.Layer==='Physical circulation'?t('material'):a.Layer==='Knowledge transmission'?t('knowledge'):t('cross'))}</span>`;
      if(a.Supplement)html+=`<span class="net-tag">${S.lang==='zh'?'文献补充 · 2026-10-30':'Cited addition · 30 Oct 2026'}</span>`;
      if(a.ProcessState)html+=`<span class="net-tag">${esc(process(a.ProcessState))}</span>`;
      if(date)html+=`<h4>${esc(t('date'))}</h4><p class="net-copy">${esc(date)}</p>`;
      if(ev&&(ev.Place||ev.english.place))html+=`<h4>${esc(t('place'))}</h4><p class="net-copy">${esc(S.lang==='zh'?(ev.Place||t('unrecorded')):ev.english.place)}</p>`;
      if(a.Scope)html+=`<details class="net-original"><summary>${esc(t('scope'))}</summary><p>${esc(scope(a.Scope))}</p></details>`;
      if(ev)html+=`<h4>${esc(t('reading'))}</h4><p class="net-copy">${esc(S.lang==='zh'?(ev.displayNoteZH||ev.NotesZH):ev.english.note)}</p>`;
      const mapId=ev?.EventId;
      if(n)html+=`<button class="guide-back-button" id="networkReadGuide">${S.lang==='zh'?'用关系导读查看':'Read this as a relationship guide'}</button>`;
      if(mapId&&window.DUNHUANG_DATA?.flows.some(f=>f.visible&&f.eventIds.includes(mapId)))html+=`<button class="net-mini" id="networkMapEvent" data-event="${esc(mapId)}">${esc(t('map'))}</button>`;
      if(n){
        const related=baseEdges().filter(e=>e.source===n.id||e.target===n.id);
        html+=`<h4>${esc(t('connected'))} (${related.length})</h4>`+related.map(e=>{
          const outgoing=e.source===n.id,other=nodes.get(outgoing?e.target:e.source);
          return `<button class="net-mini" data-inspect-edge="${esc(e.id)}">${outgoing?'→':'←'} ${esc(name(other))}<small>${esc(relation(e))} · ${esc(outgoing?t('out'):t('in'))}</small></button>`;
        }).join('');
      }
      html+=evidenceHTML(a)+sourceHTML(a);
      if(a.NotesZH&&!ev)html+=`<details class="net-original"><summary>${esc(t('original'))}</summary><p lang="zh-Hans">${esc(a.NotesZH)}</p></details>`;
      html+=`<p class="net-kicker" style="margin-top:20px">${esc((n||e).id)}</p>`;box.innerHTML=html;
    }
    const heading=document.createElement('div'),body=document.createElement('div');heading.className='network-record-heading';body.className='network-record-body';
    for(const item of [...box.children]){
      (item.matches('h3,.net-clear,.net-kicker,.net-tag')?heading:body).append(item);
    }
    box.replaceChildren(heading,body);
    box.querySelectorAll('[data-inspect-node]').forEach(b=>b.addEventListener('click',()=>choose('node',b.dataset.inspectNode,true)));
    box.querySelectorAll('[data-inspect-edge]').forEach(b=>b.addEventListener('click',()=>choose('edge',b.dataset.inspectEdge,false)));
    $('networkClear')?.addEventListener('click',()=>{S.selection=null;S.focus=false;$('networkFocus').checked=false;$('networkFocus').disabled=true;hover=null;renderGraph();renderInspector();});
    $('networkMapEvent')?.addEventListener('click',e=>{if(document.body.classList.contains('network-presenting'))togglePresentation();window.DUNHUANG_EXHIBITION.selectEvent(e.currentTarget.dataset.event);});
    $('networkReadGuide')?.addEventListener('click',()=>{window.DUNHUANG_NETWORK_GUIDE?.show(selection.id);$('networkShell').scrollIntoView({behavior:'instant',block:'start'});});
  }
  function choose(kind,id,recenter){
    S.selection={kind,id};hover=null;$('networkSearchResults').hidden=true;
    if(kind==='edge'){S.focus=false;$('networkFocus').checked=false;}
    $('networkFocus').disabled=kind!=='node';
    renderGraph();renderInspector();
    if(recenter){const set=new Set([id]);for(const e of baseEdges())if(e.source===id||e.target===id){set.add(e.source);set.add(e.target);}fit(visibleNodes.filter(n=>set.has(n.id)));}
    window.dispatchEvent(new CustomEvent('dunhuang:network-select',{detail:{kind,id}}));
  }
  function renderSearch(){
    const q=$('networkSearch').value.trim().toLocaleLowerCase();
    if(!q){$('networkSearchResults').hidden=true;return;}
    const matches=D.nodes.filter(n=>`${n.label.en} ${n.label.zh} ${n.id}`.toLocaleLowerCase().includes(q)).slice(0,10);
    $('networkSearchResults').innerHTML=matches.length?matches.map(n=>`<button data-search-node="${esc(n.id)}">${esc(name(n))}<small>${esc(type(n))}</small></button>`).join(''):`<p>${esc(t('nomatch'))}</p>`;
    $('networkSearchResults').hidden=document.activeElement!==$('networkSearch');
    $('networkSearchResults').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{const id=b.dataset.searchNode;if(!visibleNodes.some(n=>n.id===id))reset();choose('node',id,true);$('networkSearch').value='';$('networkSearchResults').hidden=true;}));
  }
  function renderText(){
    document.querySelectorAll('[data-net-i18n]').forEach(e=>e.textContent=t(e.dataset.netI18n));
    $('networkSearch').placeholder=t('placeholder');$('networkGraph').setAttribute('aria-label',t('graphA11y'));
    $('networkInspector').setAttribute('aria-label',t('panelA11y'));$('networkLegend').setAttribute('aria-label',t('legendA11y'));
    document.querySelector('.network-layer-tabs').setAttribute('aria-label',t('layersA11y'));
    for(const [id,key] of [['networkZoomIn','zoomIn'],['networkZoomOut','zoomOut'],['networkFit','fit'],['networkReset','reset']])$(id).setAttribute('aria-label',t(key));
    document.querySelector('[data-net-i18n="layout"]').textContent=t(S.compact?'compactCaption':'layout');
    $('networkYearLabel').textContent=`${t('through')} ${S.until}`;
    $('networkYear').setAttribute('aria-valuetext',`${t('through')} ${S.until}`);
    $('networkPresent').textContent=t(document.body.classList.contains('network-presenting')?'exit':'present');
    document.querySelectorAll('[data-network-layer]').forEach(b=>{const active=b.dataset.networkLayer===S.layer;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
  }
  function filterChanged(){hover=null;S.selection=null;S.focus=false;$('networkFocus').checked=false;$('networkFocus').disabled=true;renderText();renderGraph();renderInspector();fit();}
  function reset(){
    S.layer='all';S.until=1910;S.context=true;S.labels=false;S.focus=false;S.compact=true;S.selection=null;hover=null;$('networkCompact').checked=true;
    $('networkYear').value=1910;$('networkContext').checked=true;$('networkLabels').checked=false;$('networkFocus').checked=false;$('networkFocus').disabled=true;$('networkSearch').value='';
    renderText();renderGraph();renderInspector();fit();
  }
  function togglePresentation(){
    const active=document.body.classList.toggle('network-presenting');window.DUNHUANG_READING_LAYOUT?.refresh();$('networkPresent').textContent=t(active?'exit':'present');
    if(active)$('networkShell').scrollIntoView({behavior:'instant'});requestAnimationFrame(()=>fit());
  }
  document.querySelectorAll('[data-network-layer]').forEach(b=>b.addEventListener('click',()=>{S.layer=b.dataset.networkLayer;filterChanged();}));
  $('networkCompact').addEventListener('change',e=>{S.compact=e.target.checked;renderText();renderGraph();fit();});
  $('networkContext').addEventListener('change',e=>{S.context=e.target.checked;filterChanged();});
  $('networkFocus').addEventListener('change',e=>{S.focus=e.target.checked;hover=null;renderGraph();fit();});
  $('networkLabels').addEventListener('change',e=>{S.labels=e.target.checked;paint();});
  $('networkYear').addEventListener('input',e=>{S.until=Number(e.target.value);filterChanged();});
  $('networkSearch').addEventListener('input',renderSearch);$('networkSearch').addEventListener('focus',renderSearch);
  $('networkSearch').addEventListener('keydown',e=>{if(e.key==='ArrowDown'){e.preventDefault();$('networkSearchResults').querySelector('button')?.focus();}if(e.key==='Enter'){e.preventDefault();$('networkSearchResults').querySelector('button')?.click();}if(e.key==='Escape'){$('networkSearchResults').hidden=true;}});
  document.addEventListener('click',e=>{if(!e.target.closest('.network-search'))$('networkSearchResults').hidden=true;});
  $('networkZoomIn').addEventListener('click',()=>zoom(.78));$('networkZoomOut').addEventListener('click',()=>zoom(1.28));$('networkFit').addEventListener('click',()=>fit());$('networkReset').addEventListener('click',reset);
  $('networkPresent').addEventListener('click',togglePresentation);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.body.classList.contains('network-presenting'))togglePresentation();});
  $('networkGraph').addEventListener('keydown',e=>{
    if(e.target!==$('networkGraph'))return;
    if(['+','=','-','Home','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){
      e.preventDefault();if(['+','='].includes(e.key))zoom(.8);else if(e.key==='-')zoom(1.25);else if(e.key==='Home')fit();else{const d=camera.w*.07;if(e.key==='ArrowLeft')camera.x-=d;if(e.key==='ArrowRight')camera.x+=d;if(e.key==='ArrowUp')camera.y-=d;if(e.key==='ArrowDown')camera.y+=d;view();}
    }
  });
  const graph=$('networkGraph');
  graph.addEventListener('pointerdown',e=>{if(e.target.closest('.network-node,.network-link'))return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,start:{...camera}};graph.setPointerCapture(e.pointerId);graph.classList.add('dragging');});
  graph.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const u=camera.w/graph.clientWidth;camera.x=drag.start.x-(e.clientX-drag.x)*u;camera.y=drag.start.y-(e.clientY-drag.y)*u;view();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])graph.addEventListener(event,()=>{drag=null;graph.classList.remove('dragging');});
  graph.addEventListener('wheel',e=>{if(document.activeElement!==graph&&!e.ctrlKey&&!e.metaKey)return;e.preventDefault();const rect=graph.getBoundingClientRect(),p=[camera.x+(e.clientX-rect.left)/rect.width*camera.w,camera.y+(e.clientY-rect.top)/rect.height*camera.h];zoom(e.deltaY>0?1.12:.89,p);},{passive:false});
  window.addEventListener('resize',()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(()=>{const cy=camera.y+camera.h/2;camera.h=camera.w*Math.max(graph.clientHeight,250)/Math.max(graph.clientWidth,280);camera.y=cy-camera.h/2;view();paint();});});
  window.addEventListener('dunhuang:language',e=>{S.lang=e.detail.lang;hover=null;renderText();renderGraph();renderInspector();});
  $('networkDownload').href=URL.createObjectURL(new Blob([JSON.stringify(D,null,2)],{type:'application/json;charset=utf-8'}));
  renderText();renderGraph();renderInspector();fit();
  function focusNode(id){
    if(!nodes.has(id))return false;
    reset();S.layer='Knowledge transmission';S.selection={kind:'node',id};S.focus=true;S.labels=false;
    $('networkFocus').disabled=false;$('networkFocus').checked=true;$('networkLabels').checked=false;
    renderText();renderGraph();renderInspector();fit();return true;
  }
  window.DUNHUANG_NETWORK_VIEW={focusNode,fitVisible:()=>fit(),getState:()=>({...S,selection:S.selection?{...S.selection}:null,counts:{nodes:visibleNodes.length,edges:visibleEdges.length},camera:{...camera}}),selectNode:id=>{if(!nodes.has(id))return false;choose('node',id,true);return true;},selectEdge:id=>{const e=edges.get(id);if(!e)return false;choose('edge',id,false);fit([nodes.get(e.source),nodes.get(e.target)]);return true;},reset};
})();
