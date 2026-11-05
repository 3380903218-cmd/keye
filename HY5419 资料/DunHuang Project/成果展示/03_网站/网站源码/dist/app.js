/* Dunhuang / In Motion — buildless, self-contained exhibition. */
(() => {
  'use strict';
  const D = window.DUNHUANG_DATA, WORLD = window.DUNHUANG_WORLD;
  const $ = id => document.getElementById(id);
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const SVG = 'http://www.w3.org/2000/svg';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const state = {lang:new URLSearchParams(window.location.search).get('lang')==='zh'?'zh':'en',stage:4,view:'history',route:'stein',material:true,knowledge:true,playing:false,speed:1,selection:null};
  const colors = {stein:'#e6b878',pelliot:'#7fc3b8',qing:'#d88f78',knowledge:'#acc2e1'};
  const places = new Map(D.places.map(p => [p.id,p]));
  let clock = null, cameraFrame = 0, toastClock = null;
  const camera = {x:163,y:26,w:162,h:94};
  const strings = {
    zh:{skip:'跳至互动地图',navMap:'探索地图',navCollections:'今日馆藏',navSources:'史料与方法',hero:'一座藏经洞，<br>不止一条去向。',heroSub:'DUNHUANG MANUSCRIPTS, ACROSS MANY WORLDS.',intro:"本项目整理敦煌文献的运输、收存和研究记录，并列出相关的现藏机构。",start:'开始一次旅程 <span>↗</span>',findCollection:'它们今天在哪里？ ↓',artifact:'《金刚经》卷首与经文 · 868年',mapKicker:'01 / FOLLOW THE CONNECTIONS',mapTitle:'线路，让关系浮现。',present:'⤢ 展演模式',exitPresent:'⤢ 退出展演',history:'历史流转',holdings:'现藏机构',all:'全部',stein:'斯坦因',pelliot:'伯希和',qing:'清政府',mapCaption:'敦煌及其联系地域',mapReference:'地理参考 · 示意连接',noRoutes:'当前筛选下没有已显示的关系。请选择其他年份、路线或图层。',material:'实物流转',knowledge:'知识／行政通信',origin:'莫高窟',play:'播放旅程',pause:'暂停播放',narrativeTime:'按叙事阶段播放，不模拟逐日位置',mapNote:'曲线表示史料支持的地域联系，不复原实际道路、航线或电缆。地点采用城市／遗址参考点；点击线段可查看时间精度、批次与来源。',relationList:'查看当前可见关系列表',chapterKicker:'READ THE JOURNEY',chaptersTitle:"流转记录的六个阶段",chapterHelp:"选择时间阶段，查看相应记录。",collectionKicker:'03 / WHERE THEY ARE NOW',collectionsTitle:"相关收藏机构",collectionsIntro:"本案例涉及伦敦、巴黎和北京的五个现藏机构，写本与相关绘画分别标明。各项附官方馆藏链接。",collectionsNote:"这里只列出本案例涉及的收藏机构，并非敦煌文献全部现藏地。地图标注城市位置；馆藏文物未必正在展出。",sourcesKicker:'04 / BEHIND THE MAP',sourcesTitle:"资料来源与证据范围",sourceIntro:"路线图和关系网络根据考察记录、书信、研究论著及馆藏目录整理。点击地图连线或网络节点，可查阅相应的来源与证据说明。尚未核实的中转地点和单件文献对应关系，不作确定标注。",download:'下载本页展示数据 ↓',method1Title:"路线与地点",method1:"地图连线表示资料记载的两地联系，不复原途中经过的全部地点。没有核实的中转站、港口或历史建筑不予定位；现今馆址也不作为当年的交接地点。",method2Title:"运输记录与入藏记录",method2:"伯希和考察队主批材料于1909年抵达巴黎，法国国家图书馆则记载写本于1910年进入写本部，两项分别记录。原资料中的箱、卷、件、图像和编号保留各自单位，不相互换算。",method3Title:"批次与单件文献",method3:"多数历史连线依据批次或整批收藏的记录。除少数已核实的目录实例外，本项目尚未将现藏写本与每次历史交接逐件对应。",sourceList:'展开史料与官方馆藏来源',imageCredit:'图像：British Library / Wikimedia Commons · CC0 ↗',verified:'馆藏资料核对：2026-10-28 · v1.1.1',now:'现藏',story:"阶段说明",storyHelp:"点击地点或连线，查看日期、所涉材料和资料出处。",back:'← 返回章节',date:'时间与精度',evidence:'依据',source:'查阅来源 ↗',precision:'地点精度',objects:'收藏与对象',cityNote:'现藏机构按城市归组，不标注文献的具体库房或当年交接地点。',locate:'在地图上定位 ↗',catalogue:'官方馆藏页面 ↗',noInstitutions:'当前路线筛选下没有机构。',relationHelp:"连线仅示意两地之间的联系，具体记录请查阅所附来源。",locationHelp:'拖动平移 · 使用 + / − 缩放',exitHint:'已进入展演模式；按 Esc 退出。',returned:'已退出展演模式。',listSuffix:'段示意关系',mapA11y:'敦煌文献传播互动地图，可缩放、拖动；也可使用关系列表。'},
    en:{skip:'Skip to interactive map',navMap:'Explore',navCollections:'Collections today',navSources:'Sources & method',hero:'From one cave,<br>across many worlds.',heroSub:'DUNHUANG MANUSCRIPTS · DISPERSAL & CONNECTION',intro:"This project documents the transport, custody and study of Dunhuang materials and identifies related collecting institutions today.",start:'Begin the journey <span>↗</span>',findCollection:'Where are they now? ↓',artifact:'Diamond Sutra, frontispiece and text · 868',mapKicker:'01 / FOLLOW THE CONNECTIONS',mapTitle:'Trace the connections.',present:'⤢ Presentation mode',exitPresent:'⤢ Exit presentation',history:'Historical journeys',holdings:'Collections today',all:'All routes',stein:'Stein',pelliot:'Pelliot',qing:'Qing',mapCaption:'Dunhuang and its connected regions',mapReference:'Reference geography · schematic links',noRoutes:'No connections for these filters. Try a different year, route or layer.',material:'Material movement',knowledge:'Knowledge / communication',origin:'Mogao',play:'Play journey',pause:'Pause',narrativeTime:'Narrative stages, not simulated daily positions',mapNote:'Curves show documented geographical relationships, not reconstructed roads, shipping lanes or cables. Locations are city / site references. Select a link for dates, batches and sources.',relationList:'Browse visible relationships',chapterKicker:'READ THE JOURNEY',chaptersTitle:"Six stages of the records",chapterHelp:"Choose a stage to view the corresponding records.",collectionKicker:'03 / WHERE THEY ARE NOW',collectionsTitle:"Related collecting institutions",collectionsIntro:"This case study includes five institutions in London, Paris and Beijing. Manuscripts and related paintings are identified separately, with official collection links.",collectionsNote:"These institutions represent this case study, not a complete inventory of Dunhuang collections. Locations are city-level references; holding an object does not mean it is on public display.",sourcesKicker:'04 / BEHIND THE MAP',sourcesTitle:"Sources and evidence",sourceIntro:"The route map and relationship network draw on expedition accounts, correspondence, research publications and collection catalogues. Select a map connection or network node to consult its sources and evidence notes. Unverified stops and links to individual manuscripts are left unspecified.",download:'Download exhibition data ↓',method1Title:"Routes and locations",method1:"Map lines represent geographical connections recorded in the sources, rather than every stop along a journey. Unverified stops, ports and historical buildings are left unlocated. Present-day museum addresses are not used as historical handover sites.",method2Title:"Transport and accession records",method2:"Pelliot’s main expedition cargo arrived in Paris in 1909; the BnF records entry of the manuscripts into its department in 1910. These are recorded separately. Cases, scrolls, objects, images and catalogue numbers retain their original units and are not converted into one another.",method3Title:"Batches and individual manuscripts",method3:"Most historical connections are based on records of batches or whole collections. Apart from a few verified catalogue examples, this project has not matched individual manuscripts to every historical handover.",sourceList:'Expand historical and collection sources',imageCredit:'Image: British Library / Wikimedia Commons · CC0 ↗',verified:'Collection references checked: 28 Oct 2026 · v1.1.1',now:'Today',story:"Stage notes",storyHelp:"Select a place or connection to view its dates, materials and sources.",back:'← Back to chapter',date:'Date & precision',evidence:'Evidence',source:'Read the source ↗',precision:'Location precision',objects:'Collection & objects',cityNote:'Institutions are grouped by city. These markers do not locate storage rooms or historical handover sites.',locate:'Locate on the map ↗',catalogue:'Official collection page ↗',noInstitutions:'No institutions for this route filter.',relationHelp:"Lines indicate connections between places. Consult the attached sources for the recorded details.",locationHelp:'Drag to pan · Use + / − to zoom',exitHint:'Presentation mode. Press Esc to exit.',returned:'Exited presentation mode.',listSuffix:'schematic connections',mapA11y:'Interactive map of Dunhuang manuscript journeys. Zoom, pan or use the relationship list.'}
  };
  Object.assign(strings.zh,{
    networkNav:'传播网络',pageTitle:"敦煌文献的流转与研究 | Dunhuang, in motion",pageDescription:'从敦煌藏经洞到今日馆藏：探索1900—1910年写本流转、知识传播与可追溯的史料。',
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
  Object.assign(strings.en,{hero:'The journeys of<br>Dunhuang manuscripts.',mapKicker:'01 / THE JOURNEYS',mapTitle:'Where were the manuscripts sent?',collectionKicker:'CHAPTER 03 / COLLECTIONS TODAY',collectionsTitle:'Where are they now?',sourcesKicker:'SOURCES & METHOD',skip:'Skip to the story',start:'Play from 1900',navMap:'The journeys'});
  Object.assign(strings.zh,{hero:'敦煌文献，<br>如何走向世界？',mapKicker:'第一章 / 文献流转',mapTitle:'文献被运往何处？',collectionKicker:'第三章 / 今日馆藏',collectionsTitle:'它们今天在哪里？',sourcesKicker:'史料与方法',skip:'跳至正文',start:'从1900年开始播放',navMap:'文献的流转'});
  const routeStories={
    stein:{year:'1907–1909',title:{en:'Stein: acquisition and transport',zh:'斯坦因相关批次的取得与转运'},text:{en:'Stein-related cargo was transported from Mogao through Anxi and Xinjiang to London. The records also concern Wang Yuanlu, Jiang Xiaowan, carriers and messengers.',zh:'斯坦因相关批次从莫高窟经安西、新疆转运至伦敦。相关记录还涉及王圆箓、蒋孝琬，以及参与驮运和送信的人。'},help:{en:'The route is schematic. Each recorded segment has its own date and source; it is not a reconstruction of every stop.',zh:'路线为示意连接。各段记录有各自的时间与来源，不复原途中经过的每一个地点。'}},
    pelliot:{year:'1908–1910',title:{en:'Pelliot: transport and accession',zh:'伯希和主批材料的运输与入藏'},text:{en:'Pelliot’s main expedition cargo moved towards Lanzhou, Xi’an, Zhengzhou and Shanghai before Paris. Its arrival in Paris in 1909 is separate from manuscript entry into the BnF department in 1910.',zh:'伯希和考察队主批经兰州、西安、郑州与上海，转往巴黎。1909年主批抵达巴黎，与1910年写本进入法国国家图书馆写本部，是不同阶段。'},help:{en:'The cargo’s movements are recorded separately from Pelliot’s own itinerary. Arrival and departmental accession are different events.',zh:'材料的行程与伯希和本人的行程分别记录；运输抵达与写本部入藏也属于不同事件。'}},
    qing:{year:'1909–1910',title:{en:'Qing government: telegram and transfer',zh:'清政府的通信与运京安排'},text:{en:'The 1909 ministry telegram from Beijing to Lanzhou belongs to administrative communication. The Qing-organised transfer to Beijing in 1910 belongs to material circulation.',zh:'1909年北京发往兰州的学部电报属于行政通信；1910年清政府组织的运京属于实物流转。'},help:{en:'The telegram records administrative communication; it does not establish the date on which manuscripts were dispatched.',zh:'电报记录的是行政通信，不能据此确定文献实际发运的日期。'}}
  };
  const t = k => strings[state.lang][k] ?? k;
  const tr = v => typeof v === 'object' ? (v[state.lang] ?? v.zh ?? '') : v;
  const stageTitles={
    zh:['藏经洞的发现','斯坦因取得文献','文献分批转运','抵达与通信','机构收存','今日馆藏'],
    en:['Discovery of the Library Cave','Stein’s acquisitions','Cargo transfers','Arrivals and communication','Institutional custody','Present-day collections']
  };
  const chapterTitle=i=>stageTitles[state.lang][i];
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
    document.querySelectorAll('.map-label').forEach(n=>{
      const px=n.classList.contains('sub-label')?12:14;
      const width=[...n.textContent].reduce((sum,c)=>sum+(c.codePointAt(0)>255?px:px*.55),0);
      const x=(Number(n.getAttribute('x'))-camera.x)/u,canvas=$('map').clientWidth;
      let dx=Number(n.dataset.dx||9);
      if(dx<0&&x+dx-width<12)dx=9;
      if(dx>=0&&x+dx+width>canvas-12)dx=-9;
      n.setAttribute('font-size',u*px);n.setAttribute('dx',u*dx);n.setAttribute('dy',u*Number(n.dataset.dy||4));n.setAttribute('text-anchor',dx<0?'end':'start');
    });
    document.querySelectorAll('.geo-label').forEach(n=>n.setAttribute('font-size',u*13));
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
    }else if(state.view==='history'&&state.stage===4&&routeStories[state.route]){
      const r=routeStories[state.route];html=`<p class="story-kicker">${esc(routeName(state.route))}</p><p class="story-year">${r.year}</p><h3>${esc(tr(r.title))}</h3><p class="story-copy">${esc(tr(r.text))}</p><div class="story-rule"></div><p class="story-help">${esc(tr(r.help))}</p>`;
    }else{
      html=`<p class="story-kicker">${esc(t('story'))} / 0${state.stage+1}</p><p class="story-year">${state.stage===5?esc(t('now')):esc(chapter.year)}</p><h3>${esc(chapterTitle(state.stage))}</h3><p class="story-copy">${esc(tr(chapter.text))}</p><div class="story-rule"></div><p class="story-help">${esc(state.view==='history'?t('storyHelp'):t('cityNote'))}</p>`;
      if(state.view==='holdings')html+=visibleInstitutions().map(i=>`<button class="institution-mini" data-institution="${i.id}">${esc(tr(i.name))}<small>${esc(tr(places.get(i.city).name))} · ${esc(i.short)}</small></button>`).join('');
    }
    $('storyPanel').innerHTML=html;
    const heading=document.createElement('div'),body=document.createElement('div');heading.className='story-record-heading';body.className='story-record-body';
    for(const item of [...$('storyPanel').children]){
      (item.matches('h3,.story-back,.story-kicker,.story-year,.detail-label,.detail-date')?heading:body).append(item);
    }
    $('storyPanel').replaceChildren(heading,body);
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
    $('collectionGrid').innerHTML=D.institutions.map(i=>`<article class="collection-card"><p class="collection-city">${esc(tr(places.get(i.city).name))}</p><div class="collection-monogram">${esc(i.short)}</div><h3>${esc(tr(i.name))}</h3><p class="collection-kind">${esc(tr(i.kind))}</p><p class="collection-body">${esc(tr(i.collection))}</p>${anchor(i.url,t('catalogue'),'collection-link')}</article>`).join('');
    $('collectionGrid').querySelectorAll('[data-institution]').forEach(n=>n.addEventListener('click',()=>selectInstitution(n.dataset.institution,true)));
    $('sourceList').innerHTML=D.sources.map(s=>`<li>${anchor(s.url,tr(s.title),'')}<small>${esc(s.id)} · ${esc(tr(s.type))}</small></li>`).join('');
    $('yearButtons').innerHTML=D.chapters.map((c,i)=>`<button data-stage="${i}" aria-label="${esc((i===5?t('now'):c.year)+' '+chapterTitle(i))}">${i===5?esc(t('now')):esc(c.year)}</button>`).join('');
    $('yearButtons').querySelectorAll('button').forEach(n=>n.addEventListener('click',()=>{pause();setStage(Number(n.dataset.stage));}));
    $('chapterGrid').innerHTML=D.chapters.map((c,i)=>`<button class="chapter-card" data-stage="${i}"><span>${i===5?esc(t('now')):esc(c.year)}</span><b>${esc(chapterTitle(i))}</b><small>0${i+1} <span aria-hidden="true">↗</span></small></button>`).join('');
    $('chapterGrid').querySelectorAll('button').forEach(n=>n.addEventListener('click',()=>{pause();setStage(Number(n.dataset.stage));$('exhibition').scrollIntoView({behavior:reduced.matches?'instant':'smooth'});}));
  }
  function render(){
    $('mapReadingStage').textContent=state.view==='holdings'?t('holdings'):(state.lang==='zh'?`记录截至${D.chapters[state.stage].year}年`:`Records through ${D.chapters[state.stage].year}`);
    $('historyView').classList.toggle('active',state.view==='history');$('holdingsView').classList.toggle('active',state.view==='holdings');
    $('historyView').setAttribute('aria-pressed',String(state.view==='history'));$('holdingsView').setAttribute('aria-pressed',String(state.view==='holdings'));
    document.querySelectorAll('[data-route]').forEach(n=>{const yes=n.dataset.route===state.route;n.classList.toggle('active',yes);n.setAttribute('aria-pressed',String(yes));});
    document.querySelectorAll('[data-stage]').forEach(n=>{const yes=Number(n.dataset.stage)===state.stage;n.classList.toggle('active',yes);n.setAttribute('aria-current',yes?'step':'false');});
    $('yearSlider').value=state.stage;$('yearSlider').setAttribute('aria-valuetext',`${D.chapters[state.stage].year} ${chapterTitle(state.stage)}`);
    $('layers').hidden=state.view==='holdings';
    $('playIcon').textContent=state.playing?'Ⅱ':'▶';$('playLabel').textContent=t(state.playing?'pause':'play');$('play').setAttribute('aria-label',t(state.playing?'pause':'play'));
    renderMap();renderStory();renderRelations();
  }
  function setStage(stage){state.stage=stage;state.view=stage===5?'holdings':'history';state.selection=null;render();}
  function pause(){clearInterval(clock);clock=null;state.playing=false;}
  function startClock(){clearInterval(clock);clock=setInterval(()=>{if(state.stage>=5){pause();render();return;}setStage(state.stage+1);if(state.stage===5){pause();render();}},6500/state.speed);}
  function play(){if(state.playing){pause();render();return;}if(state.stage>=4)state.stage=0;state.view='history';state.selection=null;state.playing=true;render();home();startClock();}
  function selectInstitution(id,scroll){pause();const institution=D.institutions.find(i=>i.id===id);state.view='holdings';state.stage=5;state.route='all';state.selection={type:'institution',id};render();fitCamera([institution.city],true);if(scroll)$('exhibition').scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'start'});}
  function toast(text){clearTimeout(toastClock);$('toast').textContent=text;$('toast').hidden=false;toastClock=setTimeout(()=>$('toast').hidden=true,3500);}
  function togglePresentation(){const active=document.body.classList.toggle('presenting');window.DUNHUANG_READING_LAYOUT?.refresh();$('presentation').textContent=t(active?'exitPresent':'present');toast(t(active?'exitHint':'returned'));if(active)$('exhibition').scrollIntoView({behavior:'instant'});requestAnimationFrame(()=>home(false));}
  $('lang').addEventListener('click',()=>{state.lang=state.lang==='zh'?'en':'zh';renderStaticContent();render();window.dispatchEvent(new CustomEvent('dunhuang:language',{detail:{lang:state.lang}}));});
  $('play').addEventListener('click',play);
  $('startJourney')?.addEventListener('click',()=>{pause();state.stage=0;state.route='all';state.material=true;state.knowledge=true;$('materialToggle').checked=true;$('knowledgeToggle').checked=true;play();$('exhibition').scrollIntoView({behavior:reduced.matches?'instant':'smooth'});});
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
  buildGeography();renderStaticContent();render();fitCamera([...new Set(visibleFlows().flatMap(f=>[f.fromId,f.toId]))],false);
  // Useful for a repeatable presentation and browser verification. No network API.
  window.DUNHUANG_EXHIBITION={fitVisible:()=>home(false),selectEvent:id=>{window.DUNHUANG_SHOWCASE?.showMap('interactive');const flow=D.flows.find(f=>f.visible&&f.eventIds.includes(id));if(!flow)return false;pause();state.stage=4;state.view='history';state.route='all';state.material=true;state.knowledge=true;$('materialToggle').checked=true;$('knowledgeToggle').checked=true;state.selection={type:'flow',id:flow.id};render();home(false);$('exhibition').scrollIntoView({behavior:reduced.matches?'instant':'smooth'});return true;},getState:()=>({...state}),restart:()=>{pause();state.stage=0;state.route='all';play();}};
})();
