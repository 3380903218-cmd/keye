/* Dunhuang / In Motion — buildless, self-contained exhibition. */
(() => {
  'use strict';
  const D = window.DUNHUANG_DATA, WORLD = window.DUNHUANG_WORLD;
  const $ = id => document.getElementById(id);
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const SVG = 'http://www.w3.org/2000/svg';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const state = {lang:'en',stage:4,view:'history',route:'all',material:true,knowledge:true,playing:false,speed:1,selection:null};
  const colors = {stein:'#e6b878',pelliot:'#7fc3b8',qing:'#d88f78',knowledge:'#acc2e1'};
  const places = new Map(D.places.map(p => [p.id,p]));
  let clock = null, cameraFrame = 0, toastClock = null;
  const camera = {x:163,y:26,w:162,h:94};
  const strings = {
    zh:{skip:'跳至互动地图',navMap:'探索地图',navCollections:'今日馆藏',navSources:'史料与方法',hero:'一座藏经洞，<br>不止一条去向。',heroSub:'DUNHUANG MANUSCRIPTS, ACROSS MANY WORLDS.',intro:'跟随写本、箱笼与书信，走进敦煌文献的传播网络。从一次交涉到一次远行，从藏经洞到今天的公共收藏。',start:'开始一次旅程 <span>↗</span>',findCollection:'它们今天在哪里？ ↓',artifact:'《金刚经》卷首与经文 · 868年',mapKicker:'01 / FOLLOW THE CONNECTIONS',mapTitle:'线路，让关系浮现。',present:'⤢ 展演模式',exitPresent:'⤢ 退出展演',history:'历史流转',holdings:'现藏机构',all:'全部',stein:'斯坦因',pelliot:'伯希和',qing:'清政府',mapCaption:'敦煌及其联系地域',mapReference:'地理参考 · 示意连接',noRoutes:'当前筛选下没有已显示的关系。请选择其他年份、路线或图层。',material:'实物流转',knowledge:'知识／行政通信',origin:'莫高窟',play:'播放旅程',pause:'暂停播放',narrativeTime:'按叙事阶段播放，不模拟逐日位置',mapNote:'曲线表示史料支持的地域联系，不复原实际道路、航线或电缆。地点采用城市／遗址参考点；点击线段可查看时间精度、批次与来源。',relationList:'查看当前可见关系列表',chapterKicker:'READ THE JOURNEY',chaptersTitle:'沿着时间，重新阅读。',chapterHelp:'选择一个章节，让地图为你讲述。',collectionKicker:'03 / WHERE THEY ARE NOW',collectionsTitle:'分藏各地，仍可相逢。',collectionsIntro:'写本与绘画，图书馆与博物馆。这里展示三座城市中的五个相关机构，点击可定位并查阅官方目录。',collectionsNote:'本页是研究案例的馆藏切片，并非全球敦煌文献收藏全表。地图以城市标注现藏机构；馆藏不等于常设展出。',sourcesKicker:'04 / BEHIND THE MAP',sourcesTitle:'每一条线，都有来处。',sourceIntro:'地图从现有项目的路线与事件记录出发。不同资料能够支持的范围不一；让来源、推定和缺口一起被看见。',download:'下载本页展示数据 ↓',method1Title:'关系，不等于完整路线',method1:'曲线连接有证据的地域。未知中转站、港口和历史建筑保持未知；今天的馆址不反推为当年的收存地点。',method2Title:'到达，不等于入藏',method2:'1909年考察队主批到巴黎，与法国国家图书馆所记1910年入藏分开呈现。箱、卷、件、图像和编号也不相互换算。',method3Title:'批次，不等于每一件原物',method3:'历史线主要表示批次或集合。除明确目录实例外，不声称已将每一卷现藏写本与所有历史交接逐件匹配。',sourceList:'展开史料与官方馆藏来源',imageCredit:'图像：British Library / Wikimedia Commons · CC0 ↗',verified:'馆藏资料核对：2026-10-28 · v1.1.0',now:'现藏',story:'研究叙事',storyHelp:'点击地图的地点或连线，查看人物之外的运输、批次与证据。',back:'← 返回章节',date:'时间与精度',evidence:'依据',source:'查阅来源 ↗',precision:'地点精度',objects:'收藏与对象',cityNote:'现藏机构按城市归组，不标注文献的具体库房或当年交接地点。',locate:'在地图上定位 ↗',catalogue:'官方馆藏页面 ↗',noInstitutions:'当前路线筛选下没有机构。',relationHelp:'关系线为示意几何；请结合来源阅读。',locationHelp:'拖动平移 · 使用 + / − 缩放',exitHint:'已进入展演模式；按 Esc 退出。',returned:'已退出展演模式。',listSuffix:'段示意关系',mapA11y:'敦煌文献传播互动地图，可缩放、拖动；也可使用关系列表。'},
    en:{skip:'Skip to interactive map',navMap:'Explore',navCollections:'Collections today',navSources:'Sources & method',hero:'From one cave,<br>across many worlds.',heroSub:'DUNHUANG MANUSCRIPTS · DISPERSAL & CONNECTION',intro:'Follow manuscripts, cases and letters through the networks of Dunhuang: from negotiations and journeys to the public collections that hold them today.',start:'Begin the journey <span>↗</span>',findCollection:'Where are they now? ↓',artifact:'Diamond Sutra, frontispiece and text · 868',mapKicker:'01 / FOLLOW THE CONNECTIONS',mapTitle:'Trace the connections.',present:'⤢ Presentation mode',exitPresent:'⤢ Exit presentation',history:'Historical journeys',holdings:'Collections today',all:'All routes',stein:'Stein',pelliot:'Pelliot',qing:'Qing',mapCaption:'Dunhuang and its connected regions',mapReference:'Reference geography · schematic links',noRoutes:'No connections for these filters. Try a different year, route or layer.',material:'Material movement',knowledge:'Knowledge / communication',origin:'Mogao',play:'Play journey',pause:'Pause',narrativeTime:'Narrative stages, not simulated daily positions',mapNote:'Curves show documented geographical relationships, not reconstructed roads, shipping lanes or cables. Locations are city / site references. Select a link for dates, batches and sources.',relationList:'Browse visible relationships',chapterKicker:'READ THE JOURNEY',chaptersTitle:'A journey, read through time.',chapterHelp:'Choose a chapter to explore the map.',collectionKicker:'03 / WHERE THEY ARE NOW',collectionsTitle:'Dispersed, yet connected.',collectionsIntro:'Manuscripts and paintings. Libraries and museums. Explore five related institutions in three cities, and open their official catalogues.',collectionsNote:'A collection snapshot for this case study, not a worldwide inventory. Locations are city-level references; collection ownership does not imply permanent public display.',sourcesKicker:'04 / BEHIND THE MAP',sourcesTitle:'Every line has a source.',sourceIntro:'Built from the project’s existing route and event records. Sources support different kinds of claims. Evidence, inference and gaps remain visible together.',download:'Download exhibition data ↓',method1Title:'A connection is not a complete itinerary',method1:'Curves join documented regions. Unverified stops, ports and historical premises remain unlocated. Present-day addresses do not establish historical handover sites.',method2Title:'Arrival is not accession',method2:'The expedition cargo’s arrival in Paris in 1909 is distinguished from BnF accession in 1910. Cases, scrolls, objects, images and catalogue numbers are not interchangeable units.',method3Title:'A batch is not every individual object',method3:'Historical links mostly represent batches or collections. Apart from identified catalogue examples, individual manuscripts are not claimed to have complete reconstructed custody chains.',sourceList:'Expand historical and collection sources',imageCredit:'Image: British Library / Wikimedia Commons · CC0 ↗',verified:'Collection references checked: 28 Oct 2026 · v1.1.0',now:'Today',story:'A research narrative',storyHelp:'Select a place or connection to explore cargo, batches and evidence behind the journeys.',back:'← Back to chapter',date:'Date & precision',evidence:'Evidence',source:'Read the source ↗',precision:'Location precision',objects:'Collection & objects',cityNote:'Institutions are grouped by city. These markers do not locate storage rooms or historical handover sites.',locate:'Locate on the map ↗',catalogue:'Official collection page ↗',noInstitutions:'No institutions for this route filter.',relationHelp:'Schematic geometry. Read the associated source for its evidential scope.',locationHelp:'Drag to pan · Use + / − to zoom',exitHint:'Presentation mode. Press Esc to exit.',returned:'Exited presentation mode.',listSuffix:'schematic connections',mapA11y:'Interactive map of Dunhuang manuscript journeys. Zoom, pan or use the relationship list.'}
  };
  Object.assign(strings.zh,{
    networkNav:'传播网络',pageTitle:'敦煌 · 流散与相逢 | Dunhuang, in motion',pageDescription:'从敦煌藏经洞到今日馆藏：探索1900—1910年写本流转、知识传播与可追溯的史料。',
    navA11y:'主导航',viewA11y:'地图视图',routeA11y:'路线筛选',controlsA11y:'地图控制',speedA11y:'播放速度',chaptersA11y:'叙事章节',
    artifactAlt:'868年《金刚经》卷首与经文，大英图书馆Or.8210/P.2',mapTitleA11y:'敦煌文献传播互动地图',mapDesc:'地图中的点和连线可点击；也可使用下方关系列表查阅相同内容。',
    noScript:'互动地图需要JavaScript。请启用后重载；馆藏与来源说明也可参阅项目阅读说明。'
  });
  Object.assign(strings.en,{
    networkNav:'Network',pageTitle:'Dunhuang, in motion | Manuscripts, journeys & collections',pageDescription:'Explore Dunhuang manuscript journeys, knowledge networks and present-day collections through an evidence-based interactive map focused on 1900–1910.',
    navA11y:'Main navigation',viewA11y:'Map view',routeA11y:'Filter routes',controlsA11y:'Map controls',speedA11y:'Playback speed',chaptersA11y:'Narrative chapters',
    artifactAlt:'Frontispiece and text of the Diamond Sutra, dated 868. British Library, Or.8210/P.2.',mapTitleA11y:'Interactive map of Dunhuang manuscript journeys',mapDesc:'Select a place or connection for details. The relationship list below provides the same information without using the map.',
    noScript:'The interactive map requires JavaScript. Enable it and reload, or consult the project reading guide for collection and source references.'
  });
  const t = k => strings[state.lang][k] ?? k;
  const tr = v => typeof v === 'object' ? (v[state.lang] ?? v.zh ?? '') : v;
  function el(tag, attrs={}, parent) {
    const n=document.createElementNS(SVG,tag);
    for(const [k,v] of Object.entries(attrs)) n.setAttribute(k,String(v));
    if(parent)parent.appendChild(n);
    return n;
  }
  function project(lon,lat){return [lon+180,(85-lat)*1.6];}
  function getPoint(id){const p=places.get(id);return project(p.lon,p.lat);}
  const routeName = r => t(r);
  function visibleFlows(){return D.flows.filter(f=>f.visible&&f.stage<=state.stage&&(state.route==='all'||state.route===f.route)&&((f.layer==='material'&&state.material)||(f.layer==='knowledge'&&state.knowledge)));}
  function visibleInstitutions(){return D.institutions.filter(i=>state.route==='all'||i.route===state.route);}
  function selectable(n,fn){n.setAttribute('tabindex','0');n.setAttribute('role','button');n.addEventListener('click',e=>{e.stopPropagation();fn();});n.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();e.stopPropagation();fn();}});}
  function mapUnit(){return camera.w/Math.max($('map').clientWidth,300);}
  function updateViewbox(){
    $('map').setAttribute('viewBox',`${camera.x} ${camera.y} ${camera.w} ${camera.h}`);
    const u=mapUnit();
    document.querySelectorAll('.node-dot').forEach(n=>n.setAttribute('r',u*Number(n.dataset.pixels||4)));
    document.querySelectorAll('.origin-ring').forEach(n=>n.setAttribute('r',u*12));
    document.querySelectorAll('.map-label').forEach(n=>{n.setAttribute('font-size',u*(n.classList.contains('sub-label')?8:11));n.setAttribute('dx',u*Number(n.dataset.dx||9));n.setAttribute('dy',u*Number(n.dataset.dy||4));});
    document.querySelectorAll('.geo-label').forEach(n=>n.setAttribute('font-size',u*11));
    document.querySelectorAll('.route-particle').forEach(n=>n.setAttribute('r',u*2.5));
    document.querySelectorAll('.map-arrow').forEach(n=>{n.setAttribute('markerWidth',u*7);n.setAttribute('markerHeight',u*7);});
  }
  function fitCamera(ids, animate=true){
    const list=ids.map(id=>places.get(id)).filter(Boolean);
    if(!list.length)return;
    const points=list.map(p=>project(p.lon,p.lat));
    const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
    let w=Math.max(...xs)-Math.min(...xs),h=Math.max(...ys)-Math.min(...ys);
    w=Math.max(w,35);h=Math.max(h,22);
    const aspect=Math.max($('map').clientWidth,300)/Math.max($('map').clientHeight,300);
    w*=1.25;h*=1.7;
    if(w/h<aspect)w=h*aspect;else h=w/aspect;
    const cx=(Math.min(...xs)+Math.max(...xs))/2,cy=(Math.min(...ys)+Math.max(...ys))/2;
    const target={x:cx-w/2,y:cy-h/2,w,h};
    moveCamera(target,animate);
  }
  function moveCamera(target,animate=true){
    cancelAnimationFrame(cameraFrame);
    if(!animate||reduced.matches){Object.assign(camera,target);updateViewbox();return;}
    const start={...camera},time=performance.now();
    const step=now=>{const v=Math.min((now-time)/320,1),p=1-Math.pow(1-v,3);for(const k of ['x','y','w','h'])camera[k]=start[k]+(target[k]-start[k])*p;updateViewbox();if(v<1)cameraFrame=requestAnimationFrame(step);};
    cameraFrame=requestAnimationFrame(step);
  }
  function home(animate=true){fitCamera(['PL_LONDON','PL_PARIS','PL_BEIJING','PL_MOGAO','PL_KHOTAN'],animate);}
  function zoom(factor,anchor){
    const w=Math.min(370,Math.max(12,camera.w*factor)),ratio=w/camera.w;
    const p=anchor||[camera.x+camera.w/2,camera.y+camera.h/2];
    moveCamera({x:p[0]-(p[0]-camera.x)*ratio,y:p[1]-(p[1]-camera.y)*ratio,w,h:camera.h*ratio},false);
  }
  function buildGeography(){
    const pathRing=ring=>ring.map((p,i)=>`${i?'L':'M'}${project(p[0],p[1]).map(n=>n.toFixed(3)).join(' ')}`).join('')+'Z';
    for(const f of WORLD.features){
      if(f.geometry.type==='Polygon')el('path',{class:'land',d:f.geometry.coordinates.map(pathRing).join('')},$('land'));
      else if(f.geometry.type==='MultiPolygon')el('path',{class:'land',d:f.geometry.coordinates.map(poly=>poly.map(pathRing).join('')).join('')},$('land'));
    }
    for(let lon=-180;lon<=180;lon+=20){const a=project(lon,-70),b=project(lon,85);el('path',{class:'grid-line',d:`M${a}L${b}`},$('graticule'));}
    for(let lat=-60;lat<=80;lat+=10){const a=project(-180,lat),b=project(180,lat);el('path',{class:'grid-line',d:`M${a}L${b}`},$('graticule'));}
    for(const [name,lon,lat] of [['EUROPE',20,55],['CENTRAL ASIA',65,48],['CHINA',106,29],['INDIA',76,22],['ARABIAN SEA',61,12]]){
      const p=project(lon,lat);el('text',{class:'geo-label',x:p[0],y:p[1],'text-anchor':'middle','data-geo':name},$('geographicLabels')).textContent=name;
    }
  }
  function routePath(f){
    const a=getPoint(f.fromId),b=getPoint(f.toId),dx=b[0]-a[0],dy=b[1]-a[1];
    let bend=f.layer==='knowledge'?.2:.10;
    if(f.id==='MAP_SG002')bend=-.18;
    return `M ${a[0]} ${a[1]} Q ${(a[0]+b[0])/2+dy*bend} ${(a[1]+b[1])/2-dx*bend} ${b[0]} ${b[1]}`;
  }
  function renderMap(){
    $('routes').replaceChildren();$('locations').replaceChildren();
    document.querySelectorAll('.map-arrow').forEach(n=>n.remove());
    const flows=visibleFlows(), ids=new Set(['PL_MOGAO']);
    if(state.view==='history'){
      for(const f of flows){
        ids.add(f.fromId);ids.add(f.toId);
        const color=f.layer==='knowledge'?colors.knowledge:colors[f.route];
        const marker=el('marker',{id:'arrow-'+f.id,class:'map-arrow',viewBox:'0 0 8 8',refX:7,refY:4,orient:'auto',markerUnits:'userSpaceOnUse'},$('map').querySelector('defs'));
        el('path',{d:'M0 1L7 4L0 7Z',fill:color},marker);
        const g=el('g',{class:'route-item'+(state.selection?.id===f.id?' selected':''),'data-flow':f.id,'aria-label':`${tr(places.get(f.fromId).name)} → ${tr(places.get(f.toId).name)}; ${tr(f.date)}`},$('routes'));
        const path=routePath(f);
        el('path',{id:'path-'+f.id,class:'route-line '+f.layer,d:path,stroke:color,'marker-end':'url(#arrow-'+f.id+')'},g);
        el('path',{class:'route-hit',d:path},g);
        if(!reduced.matches&&((state.playing&&f.stage===state.stage)||state.selection?.id===f.id)){
          const dot=el('circle',{class:'route-particle',fill:color},g);
          const motion=el('animateMotion',{dur:'3.4s',repeatCount:'indefinite',path},dot);
          motion.setAttribute('calcMode','paced');
        }
        selectable(g,()=>{pause();state.selection={type:'flow',id:f.id};render();});
      }
      $('mapEmpty').hidden=flows.length>0||state.stage===0;
    }else{
      visibleInstitutions().forEach(i=>ids.add(i.city));$('mapEmpty').hidden=visibleInstitutions().length>0;
    }
    const overrides={PL_MOGAO:[10,-10],PL_ANXI_REF:[12,8],PL_DUNHUANG:[9,-8],PL_HAMI:[9,-8],PL_SHANSHAN:[-7,18],PL_TURPAN:[-8,-10],PL_YANQI:[0,20],PL_LUNTAI:[-1,-12],PL_KUCHA:[-10,18],PL_LONDON:[-6,-15],PL_PARIS:[10,15],PL_KHOTAN:[9,16]};
    const major=new Set(['PL_LONDON','PL_PARIS','PL_BEIJING','PL_MOGAO','PL_KHOTAN','PL_LANZHOU','PL_SHANGHAI']);
    const showMinor=camera.w<100;
    for(const id of ids){
      const p=places.get(id),point=getPoint(id),origin=id==='PL_MOGAO';
      const institutions=state.view==='holdings'?visibleInstitutions().filter(i=>i.city===id):[];
      const selected=state.selection?.id===id||state.selection?.type==='institution'&&D.institutions.find(i=>i.id===state.selection.id)?.city===id;
      const g=el('g',{class:'location','data-place':id,'aria-label':`${tr(p.name)}${institutions.length?' · '+institutions.length:''}`},$('locations'));
      if(origin){el('circle',{cx:point[0],cy:point[1],r:6,fill:'url(#originGlow)'},g);el('circle',{class:'origin-ring',cx:point[0],cy:point[1]},g);}
      const fill=origin?'#e6b878':(institutions.length?'#b8c99f':selected?'#f5e0b3':'#bac6a7');
      el('circle',{class:'node-dot',cx:point[0],cy:point[1],fill,'data-pixels':origin?5:(institutions.length?6:3.4)},g);
      const title=el('title',{},g);title.textContent=tr(p.name);
      if(major.has(id)||showMinor||selected){
        const [dx,dy]=overrides[id]||[9,-7];
        const label=el('text',{class:'map-label',x:point[0],y:point[1],'data-dx':dx,'data-dy':dy,'text-anchor':dx<0?'end':'start'},g);
        label.textContent=tr(p.name)+(institutions.length?' · '+institutions.length:'');
      }
      selectable(g,()=>{pause();state.selection={type:'place',id};render();});
    }
    $('mapCaption').textContent=state.view==='history'?t('mapCaption'):t('holdings');
    $('mapLegend').hidden=state.view!=='history';
    updateViewbox();
  }
  function anchor(url,text,cls='source-link'){return `<a class="${cls}" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(text)}</a>`;}
  function renderStory(){
    const sel=state.selection,chapter=D.chapters[state.stage];let html='';
    const back=`<button class="story-back" data-back>${esc(t('back'))}</button>`;
    if(sel?.type==='flow'){
      const f=D.flows.find(x=>x.id===sel.id);
      html=`${back}<p class="story-kicker">${esc(routeName(f.route))} / ${esc(t(f.layer==='knowledge'?'knowledge':'material'))}</p><h3>${esc(tr(places.get(f.fromId).name))}<br><span aria-hidden="true">↓</span> ${esc(tr(places.get(f.toId).name))}</h3><p class="detail-label">${esc(t('date'))}</p><p class="detail-date">${esc(tr(f.date))}</p><span class="story-badge">${esc(tr(f.evidence))}</span><p class="story-copy">${esc(tr(f.note))}</p><p class="detail-id">${esc(f.id)}<br>EventID: ${esc(f.eventIds.join(' · '))}${f.claimIds.length?'<br>ClaimID: '+esc(f.claimIds.join(' · ')):''}</p>${anchor(f.source,t('source'))}<div class="story-rule"></div><p class="story-help">${esc(t('relationHelp'))}</p>`;
    }else if(sel?.type==='institution'){
      const i=D.institutions.find(x=>x.id===sel.id);
      html=`${back}<p class="story-kicker">${esc(tr(places.get(i.city).name))} / ${esc(i.short)}</p><h3>${esc(tr(i.name))}</h3><span class="story-badge">${esc(tr(i.kind))}</span><p class="story-copy">${esc(tr(i.collection))}</p><div class="story-rule"></div><p class="detail-label">${esc(tr(i.example))}</p>${i.shelfmark?'<p class="detail-date">'+esc(tr(i.shelfmark))+'</p>':''}<p class="story-copy">${esc(tr(i.note))}</p><p class="detail-id">${esc(tr(i.status))} · 2026-10-28</p>${anchor(i.url,t('catalogue'))}`;
    }else if(sel?.type==='place'){
      const p=places.get(sel.id),institutions=state.view==='holdings'?visibleInstitutions().filter(i=>i.city===sel.id):[];
      html=`${back}<p class="story-kicker">${esc(t(state.view==='holdings'?'holdings':'precision'))}</p><h3>${esc(tr(p.name))}</h3>`;
      if(institutions.length){html+=`<p class="story-help">${esc(t('cityNote'))}</p>`+institutions.map(i=>`<button class="institution-mini" data-institution="${i.id}">${esc(tr(i.name))} ↗<small>${esc(tr(i.kind))}</small></button>`).join('');}
      else{html+=`<span class="story-badge">${esc(tr(p.precision))}</span><p class="story-copy">${esc(tr(p.note))}</p>${anchor(p.source,t('source'))}`;
        const relevant=visibleFlows().filter(f=>f.fromId===p.id||f.toId===p.id);
        if(state.view==='history'&&relevant.length)html+='<div class="story-rule"></div>'+relevant.map(f=>`<button class="institution-mini" data-flow-button="${f.id}">${esc(tr(places.get(f.fromId).name))} → ${esc(tr(places.get(f.toId).name))}<small>${esc(tr(f.date))}</small></button>`).join('');
      }
    }else{
      html=`<p class="story-kicker">${esc(t('story'))} / 0${state.stage+1}</p><p class="story-year">${state.stage===5?esc(t('now')):esc(chapter.year)}</p><h3>${esc(tr(chapter.title))}</h3><p class="story-copy">${esc(tr(chapter.text))}</p><div class="story-rule"></div><p class="story-help">${esc(state.view==='history'?t('storyHelp'):t('cityNote'))}</p>`;
      if(state.view==='holdings')html+=visibleInstitutions().map(i=>`<button class="institution-mini" data-institution="${i.id}">${esc(tr(i.name))}<small>${esc(tr(places.get(i.city).name))} · ${esc(i.short)}</small></button>`).join('');
    }
    $('storyPanel').innerHTML=html;
    $('storyPanel').scrollTop=0;
    $('storyPanel').querySelector('[data-back]')?.addEventListener('click',()=>{state.selection=null;render();});
    $('storyPanel').querySelectorAll('[data-institution]').forEach(n=>n.addEventListener('click',()=>selectInstitution(n.dataset.institution,false)));
    $('storyPanel').querySelectorAll('[data-flow-button]').forEach(n=>n.addEventListener('click',()=>{state.selection={type:'flow',id:n.dataset.flowButton};render();}));
  }
  function renderRelations(){
    const fs=state.view==='history'?visibleFlows():[];
    $('relationCount').textContent=`${fs.length} ${t('listSuffix')}`;
    $('relationList').innerHTML=fs.length?fs.map(f=>`<button data-flow-button="${f.id}"><i class="swatch ${f.route}"></i> ${esc(tr(places.get(f.fromId).name))} → ${esc(tr(places.get(f.toId).name))}<small>${esc(tr(f.date))} · ${esc(t(f.layer==='knowledge'?'knowledge':'material'))}</small></button>`).join(''):`<p>${esc(state.view==='history'?t('noRoutes'):t('cityNote'))}</p>`;
    $('relationList').querySelectorAll('button').forEach(n=>n.addEventListener('click',()=>{pause();state.selection={type:'flow',id:n.dataset.flowButton};render();$('exhibition').scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'start'});}));
  }
  function renderStaticContent(){
    document.documentElement.lang=state.lang==='zh'?'zh-Hans':'en';
    document.title=t('pageTitle');
    document.querySelector('meta[name="description"]').content=t('pageDescription');
    document.querySelectorAll('[data-i18n]').forEach(n=>{const k=n.dataset.i18n;if(k==='start')n.innerHTML=t(k);else n.textContent=t(k);});
    document.querySelectorAll('[data-i18n-html]').forEach(n=>n.innerHTML=t(n.dataset.i18nHtml));
    document.querySelectorAll('[data-i18n-aria]').forEach(n=>n.setAttribute('aria-label',t(n.dataset.i18nAria)));
    document.querySelectorAll('[data-i18n-alt]').forEach(n=>n.setAttribute('alt',t(n.dataset.i18nAlt)));
    const geoZH={'EUROPE':'欧洲','CENTRAL ASIA':'中亚','CHINA':'中国','INDIA':'印度','ARABIAN SEA':'阿拉伯海'};
    document.querySelectorAll('[data-geo]').forEach(n=>n.textContent=state.lang==='zh'?geoZH[n.dataset.geo]:n.dataset.geo);
    $('lang').innerHTML=state.lang==='zh'?'EN <span>/</span> <strong>中文</strong>':'<strong>EN</strong> <span>/</span> 中文';
    $('lang').setAttribute('aria-label',state.lang==='zh'?'Switch to English':'切换至中文');
    $('map').setAttribute('aria-label',t('mapA11y'));
    $('presentation').textContent=t(document.body.classList.contains('presenting')?'exitPresent':'present');
    $('yearSlider').setAttribute('aria-label',state.lang==='zh'?'选择叙事阶段':'Select narrative stage');
    $('zoomIn').setAttribute('aria-label',state.lang==='zh'?'放大':'Zoom in');$('zoomOut').setAttribute('aria-label',state.lang==='zh'?'缩小':'Zoom out');$('resetMap').setAttribute('aria-label',state.lang==='zh'?'重置视野':'Reset view');
    $('collectionGrid').innerHTML=D.institutions.map(i=>`<article class="collection-card"><p class="collection-city">${esc(tr(places.get(i.city).name))}</p><div class="collection-monogram">${esc(i.short)}</div><h3>${esc(tr(i.name))}</h3><p class="collection-kind">${esc(tr(i.kind))}</p><p class="collection-body">${esc(tr(i.collection))}</p><button data-institution="${i.id}">${esc(t('locate'))}</button>${anchor(i.url,t('catalogue'),'collection-link')}</article>`).join('');
    $('collectionGrid').querySelectorAll('[data-institution]').forEach(n=>n.addEventListener('click',()=>selectInstitution(n.dataset.institution,true)));
    $('sourceList').innerHTML=D.sources.map(s=>`<li>${anchor(s.url,tr(s.title),'')}<small>${esc(s.id)} · ${esc(tr(s.type))}</small></li>`).join('');
    $('yearButtons').innerHTML=D.chapters.map((c,i)=>`<button data-stage="${i}" aria-label="${esc((i===5?t('now'):c.year)+' '+tr(c.title))}">${i===5?esc(t('now')):esc(c.year)}</button>`).join('');
    $('yearButtons').querySelectorAll('button').forEach(n=>n.addEventListener('click',()=>{pause();setStage(Number(n.dataset.stage));}));
    $('chapterGrid').innerHTML=D.chapters.map((c,i)=>`<button class="chapter-card" data-stage="${i}"><span>${i===5?esc(t('now')):esc(c.year)}</span><b>${esc(tr(c.title))}</b><small>0${i+1} <span aria-hidden="true">↗</span></small></button>`).join('');
    $('chapterGrid').querySelectorAll('button').forEach(n=>n.addEventListener('click',()=>{pause();setStage(Number(n.dataset.stage));$('explore').scrollIntoView({behavior:reduced.matches?'instant':'smooth'});}));
  }
  function render(){
    $('historyView').classList.toggle('active',state.view==='history');$('holdingsView').classList.toggle('active',state.view==='holdings');
    $('historyView').setAttribute('aria-pressed',String(state.view==='history'));$('holdingsView').setAttribute('aria-pressed',String(state.view==='holdings'));
    document.querySelectorAll('[data-route]').forEach(n=>{const yes=n.dataset.route===state.route;n.classList.toggle('active',yes);n.setAttribute('aria-pressed',String(yes));});
    document.querySelectorAll('[data-stage]').forEach(n=>{const yes=Number(n.dataset.stage)===state.stage;n.classList.toggle('active',yes);n.setAttribute('aria-current',yes?'step':'false');});
    $('yearSlider').value=state.stage;$('yearSlider').setAttribute('aria-valuetext',`${D.chapters[state.stage].year} ${tr(D.chapters[state.stage].title)}`);
    $('layers').hidden=state.view==='holdings';
    $('playIcon').textContent=state.playing?'Ⅱ':'▶';$('playLabel').textContent=t(state.playing?'pause':'play');$('play').setAttribute('aria-label',t(state.playing?'pause':'play'));
    renderMap();renderStory();renderRelations();
  }
  function setStage(stage){state.stage=stage;state.view=stage===5?'holdings':'history';state.selection=null;render();}
  function pause(){clearInterval(clock);clock=null;state.playing=false;}
  function startClock(){clearInterval(clock);clock=setInterval(()=>{if(state.stage>=5){pause();render();return;}setStage(state.stage+1);if(state.stage===5){pause();render();}},6500/state.speed);}
  function play(){if(state.playing){pause();render();return;}if(state.stage>=4)state.stage=0;state.view='history';state.selection=null;state.playing=true;render();home();startClock();}
  function selectInstitution(id,scroll){pause();const institution=D.institutions.find(i=>i.id===id);state.view='holdings';state.stage=5;state.route='all';state.selection={type:'institution',id};render();fitCamera([institution.city],true);if(scroll)$('explore').scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'start'});}
  function toast(text){clearTimeout(toastClock);$('toast').textContent=text;$('toast').hidden=false;toastClock=setTimeout(()=>$('toast').hidden=true,3500);}
  function togglePresentation(){const active=document.body.classList.toggle('presenting');$('presentation').textContent=t(active?'exitPresent':'present');toast(t(active?'exitHint':'returned'));if(active)$('explore').scrollIntoView({behavior:'instant'});requestAnimationFrame(()=>home(false));}
  $('lang').addEventListener('click',()=>{state.lang=state.lang==='zh'?'en':'zh';renderStaticContent();render();window.dispatchEvent(new CustomEvent('dunhuang:language',{detail:{lang:state.lang}}));});
  $('play').addEventListener('click',play);
  $('startJourney').addEventListener('click',()=>{pause();state.stage=0;state.route='all';state.material=true;state.knowledge=true;$('materialToggle').checked=true;$('knowledgeToggle').checked=true;play();$('explore').scrollIntoView({behavior:reduced.matches?'instant':'smooth'});});
  $('speed').addEventListener('click',()=>{state.speed=state.speed===1?1.5:state.speed===1.5?2:1;$('speed').textContent=state.speed+'×';if(state.playing)startClock();});
  $('yearSlider').addEventListener('input',e=>{pause();setStage(Number(e.target.value));});
  $('historyView').addEventListener('click',()=>{pause();state.view='history';if(state.stage===5)state.stage=4;state.selection=null;render();home();});
  $('holdingsView').addEventListener('click',()=>{pause();setStage(5);home();});
  document.querySelectorAll('[data-route]').forEach(n=>n.addEventListener('click',()=>{pause();state.route=n.dataset.route;state.selection=null;render();if(state.route==='all')home();else{const ids=state.view==='history'?[...new Set(visibleFlows().flatMap(f=>[f.fromId,f.toId]))]:visibleInstitutions().map(i=>i.city);fitCamera(ids,true);}}));
  for(const [id,layer] of [['materialToggle','material'],['knowledgeToggle','knowledge']])$(id).addEventListener('change',e=>{pause();state[layer]=e.target.checked;state.selection=null;render();});
  $('zoomIn').addEventListener('click',()=>{zoom(.75);renderMap();});$('zoomOut').addEventListener('click',()=>{zoom(1.35);renderMap();});$('resetMap').addEventListener('click',()=>home());
  $('presentation').addEventListener('click',togglePresentation);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.body.classList.contains('presenting'))togglePresentation();});
  $('map').addEventListener('keydown',e=>{if(e.target!==$('map'))return;const k=e.key;if(['+','=','-','ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home'].includes(k)){e.preventDefault();if(k==='+'||k==='=')zoom(.8);else if(k==='-')zoom(1.25);else if(k==='Home')home();else{const d=camera.w*.06;if(k==='ArrowLeft')camera.x-=d;if(k==='ArrowRight')camera.x+=d;if(k==='ArrowUp')camera.y-=d;if(k==='ArrowDown')camera.y+=d;updateViewbox();}}});
  let drag=null;
  $('map').addEventListener('pointerdown',e=>{if(e.target.closest('.location,.route-item'))return;cancelAnimationFrame(cameraFrame);drag={id:e.pointerId,x:e.clientX,y:e.clientY,start:{...camera}};$('map').setPointerCapture(e.pointerId);$('map').classList.add('dragging');});
  $('map').addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const u=camera.w/$('map').clientWidth;camera.x=drag.start.x-(e.clientX-drag.x)*u;camera.y=drag.start.y-(e.clientY-drag.y)*u;updateViewbox();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])$('map').addEventListener(event,()=>{drag=null;$('map').classList.remove('dragging');});
  $('map').addEventListener('wheel',e=>{if(document.activeElement!==$('map')&&!e.ctrlKey)return;e.preventDefault();zoom(e.deltaY>0?1.10:.9);},{passive:false});
  window.addEventListener('resize',()=>{cancelAnimationFrame(cameraFrame);updateViewbox();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&state.playing){pause();render();}});
  reduced.addEventListener('change',()=>renderMap());
  const jsonBlob=new Blob([JSON.stringify(D,null,2)],{type:'application/json;charset=utf-8'});$('downloadData').href=URL.createObjectURL(jsonBlob);
  buildGeography();renderStaticContent();render();home(false);
  // Useful for a repeatable presentation and browser verification. No network API.
  window.DUNHUANG_EXHIBITION={selectEvent:id=>{const flow=D.flows.find(f=>f.visible&&f.eventIds.includes(id));if(!flow)return false;pause();state.stage=4;state.view='history';state.route='all';state.material=true;state.knowledge=true;$('materialToggle').checked=true;$('knowledgeToggle').checked=true;state.selection={type:'flow',id:flow.id};render();home(false);$('explore').scrollIntoView({behavior:reduced.matches?'instant':'smooth'});return true;},getState:()=>({...state}),restart:()=>{pause();state.stage=0;state.route='all';play();}};
})();
