/* Supporting case explanations from the existing evidence snapshot. */
(() => {
  'use strict';
  const D=window.DUNHUANG_NETWORK,host=document.getElementById('knowledgeCases');
  const nodes=new Map(D.nodes.map(n=>[n.id,n])),proof=new Map(D.evidence.map(e=>[e.id,e]));
  const sources=new Map(D.sources.map(s=>[s.SourceId,s]));
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const pair=(en,zh)=>({en,zh});
  const examples=[
    {id:'MAP_KE012',kind:pair('Administrative communication','行政通信'),date:pair('5 October 1909','1909年10月5日'),title:pair('A telegram from Beijing to Lanzhou','北京发往兰州的电报'),
      text:pair('The Qing Ministry of Education telegraphed the Governor-General’s office in Lanzhou about safeguarding and transporting the remaining manuscripts. This record follows a message between institutions.', '清学部电告兰州的陕甘总督机构，要求查收、保护并运送剩余写卷。这条记录呈现的是机构之间的一次消息传递。'),
      limit:pair('The dispatch and intended destination are recorded. Receipt and execution dates remain unresolved.', '记录确认电报的发出与目的机构，收讫和执行日期尚待核实。'),
      roles:[{label:pair('Sender','发出方'),ids:['N011']},{label:pair('Addressed institution','电文指向的机构'),ids:['N010']}],evidence:['EV021']},
    {id:'KE005',kind:pair('Collection work','材料整理'),date:pair('London, 1909','伦敦，1909年'),title:pair('Unpacking and cataloguing in London','在伦敦拆箱、分类与编目'),
      text:pair('Andrews coordinated the arrangement of Stein’s materials. Lorimer joined the work in mid-October 1909, with Droop also cataloguing. A letter of 20 November records Stein asking Andrews to direct their routine work.', '安德鲁斯主持斯坦因材料的整理。洛里默于1909年10月中旬加入，德鲁普也参与编目。11月20日的信中，斯坦因请安德鲁斯指导两人的日常工作。'),
      limit:pair('The records concern the broader Stein collection. They do not identify the person responsible for numbering each manuscript, or establish that all the material was from Dunhuang.', '这些记录涉及较广泛的斯坦因收藏，尚不能逐件确定编号者，也不能把全部材料都认定为敦煌写本。'),
      roles:[{label:pair('Coordinator','主持整理'),ids:['N017']},{label:pair('Cataloguing assistance','协助编目'),ids:['N044','N056']},{label:pair('Materials','所涉材料'),ids:['B0009']},{label:pair('Employing institution','雇用机构'),ids:['N040']}],evidence:['EV015','EV054','EV056']},
    {id:'KE007',kind:pair('Examination and writing','检查与写作'),date:pair('1910; exact drafting date unresolved','1910年；具体成稿日期未定'),title:pair('Pelliot’s memorandum for Stein','伯希和为斯坦因撰写备忘录'),
      text:pair('At Stein’s request, Pelliot wrote an inspection memorandum concerning the Chinese manuscripts examined in London. Stein later printed extracts in the second volume of Serindia.', '斯坦因请伯希和撰写检查备忘录，内容涉及在伦敦检查的中国写本。斯坦因后来在Serindia第二卷刊出了摘文。'),
      limit:pair('The drafting location is unconfirmed. The printed memorandum is not assumed to be identical to the separately archived proposal, Or.13114/1 ff.37–44.', '成稿地点尚未核实。书中备忘录与另存档的方案文件 Or.13114/1 ff.37–44，尚不能认定为同一份文书。'),
      roles:[{label:pair('Requesting party','提出请求'),ids:['N005']},{label:pair('Memorandum author','撰写备忘录'),ids:['N012']},{label:pair('Materials examined','所涉材料'),ids:['B0010']},{label:pair('Recorded document','形成的文书'),ids:['W001']}],evidence:['EV046']}
  ];
  const aliases={B0009:pair('Stein materials being arranged in London','在伦敦整理的斯坦因材料'),B0010:pair('Stein Chinese manuscripts examined in London','在伦敦检查的斯坦因中国写本'),W001:pair('Inspection memorandum (working title)','检查备忘录（工作命名）'),N017:pair('Frederick Henry Andrews','弗雷德里克·亨利·安德鲁斯'),N040:pair('India Office Library','印度事务部图书馆')};
  const locators={EV021:pair('p. 48','第48页'),EV015:pair('p. 20','第20页'),EV054:pair('pp. 215–216','第215–216页'),EV056:pair('p. 37, note 28','第37页及注28'),EV046:pair('vol. II, pp. 916–917','第二卷，第916–917页')};
  function render(){
    const lang=window.DUNHUANG_EXHIBITION.getState().lang,tr=v=>esc(v[lang]);
    host.setAttribute('aria-label',lang==='zh'?'检查与整理的两个实例':'Two records of examination and collection work');
    document.querySelector('.route-overview').setAttribute('aria-label',lang==='zh'?'三条流转线索的主要去向':'Three main destinations');
    host.innerHTML=examples.map((ex,i)=>{
      const edges=D.edges.filter(e=>e.source===ex.id||e.target===ex.id);
      const citations=ex.evidence.map(id=>{
        const p=proof.get(id),s=sources.get(p.source);
        return `<li data-reading-evidence="${id}"><a href="${esc(s.URL)}" target="_blank" rel="noopener noreferrer">${esc(s.Author)} (${esc(s.Year)}) ↗</a><span>${tr(locators[id])}</span></li>`;
      }).join('');
      return `<article class="knowledge-record" id="reading-${ex.id}" data-reading-event="${ex.id}" data-reading-edges="${esc(edges.map(e=>e.id).join(';'))}"><header><p class="record-order"><span>${tr(ex.kind)}</span></p><p class="record-date">${tr(ex.date)}</p><h3>${tr(ex.title)}</h3></header><div class="knowledge-record-content"><p class="knowledge-record-text">${tr(ex.text)}</p><dl class="record-roles">${ex.roles.map(r=>`<div><dt>${tr(r.label)}</dt><dd>${r.ids.map(id=>tr(aliases[id]||nodes.get(id).label)).join(lang==='zh'?'、':'; ')}</dd></div>`).join('')}</dl><p class="record-boundary"><b>${lang==='zh'?'记录的限度':'Limits of the record'}</b>${tr(ex.limit)}</p><div class="record-citations"><span>${lang==='zh'?'依据':'Sources'}</span><ul>${citations}</ul></div></div></article>`;
    }).join('');
    const telegram=host.querySelector('[data-reading-event="MAP_KE012"]');
    document.getElementById('mapCommunicationNote').replaceChildren(telegram);
    const mapLink=document.createElement('button');mapLink.type='button';mapLink.className='locate-reading-case';mapLink.dataset.readingMap='MAP_KE012';
    mapLink.textContent=lang==='zh'?'在地图中查看这封电报 ↑':'Locate this telegram on the map ↑';telegram.querySelector('.knowledge-record-content').append(mapLink);
    mapLink.addEventListener('click',()=>window.DUNHUANG_EXHIBITION.selectEvent('MAP_KE012'));
    const memo=host.querySelector('[data-reading-event="KE007"]');host.prepend(memo);
    const locate=document.createElement('button');locate.type='button';locate.className='locate-reading-case';locate.dataset.readingLocate='KE007';
    locate.textContent=lang==='zh'?'在图中定位这次检查与写作 ↑':'Locate this examination and writing activity ↑';memo.querySelector('.knowledge-record-content').append(locate);
    locate.addEventListener('click',()=>{window.DUNHUANG_NETWORK_GUIDE.show('all');window.DUNHUANG_NETWORK_VIEW.selectNode('KE007');window.DUNHUANG_NETWORK_VIEW.fitVisible();document.getElementById('networkShell').scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});});
  }
  const mapExtras=document.getElementById('mapExtras');
  mapExtras.addEventListener('toggle',()=>{
    if(!mapExtras.open&&window.DUNHUANG_EXHIBITION.getState().playing)document.getElementById('play').click();
  });
  function revealHash(hash){
    let target;try{target=document.getElementById(decodeURIComponent(hash.slice(1)));}catch{return;}
    for(let p=target?.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;
  }
  document.addEventListener('click',e=>{const a=e.target.closest('a[href^="#"]');if(a)revealHash(a.hash);},true);
  window.addEventListener('hashchange',()=>revealHash(location.hash));
  window.addEventListener('dunhuang:language',render);
  render();window.DUNHUANG_NETWORK_GUIDE.show('all');revealHash(location.hash);
})();
