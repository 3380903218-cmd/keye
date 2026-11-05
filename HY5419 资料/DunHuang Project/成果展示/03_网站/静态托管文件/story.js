/* Narrative navigation and guided entry points; research records remain unchanged. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  let guide='N012';
  function language(){return window.DUNHUANG_EXHIBITION.getState().lang;}
  function groupCollections(){
    const grid=$('collectionGrid'),cards=[...grid.querySelectorAll('.collection-card')];
    if(!cards.length)return;
    const lang=language(),groups=[{label:['London','伦敦'],cards:cards.slice(0,2)},{label:['Paris','巴黎'],cards:cards.slice(2,4)},{label:['Beijing','北京'],cards:cards.slice(4)}];
    grid.replaceChildren();
    for(const g of groups){
      const section=document.createElement('section');section.className='collection-city-group';
      const heading=document.createElement('h3');heading.className='city-heading';heading.textContent=g.label[lang==='zh'?1:0];
      const count=document.createElement('span');count.className='city-count';count.textContent=lang==='zh'?`${g.cards.length} 个相关机构`:`${g.cards.length} related institution${g.cards.length===1?'':'s'}`;heading.append(count);
      for(const card of g.cards){const title=card.querySelector('h3');if(title){const sub=document.createElement('h4');sub.textContent=title.textContent;title.replaceWith(sub);}}
      const list=document.createElement('div');list.className='city-institutions';list.append(...g.cards);section.append(heading,list);grid.append(section);
    }
  }
  function syncText(){
    const lang=language();
    document.querySelectorAll('[data-story-en]').forEach(n=>{n.innerHTML=n.dataset[lang==='zh'?'storyZh':'storyEn'];});
    document.querySelector('.network-guides').setAttribute('aria-label',lang==='zh'?'网络导读视图':'Guided network views');
    document.querySelector('.map-and-story').setAttribute('aria-label',lang==='zh'?'流转路线导读地图':'Guided route map');
    groupCollections();
    // Preserve a shareable language choice on HTTP and offline files alike.
    if(location.protocol==='http:'||location.protocol==='https:'){
      const url=new URL(location.href);if(lang==='zh')url.searchParams.set('lang','zh');else url.searchParams.delete('lang');history.replaceState(null,'',url);
    }
  }
  function syncGuide(){
    if(window.DUNHUANG_NETWORK_GUIDE){window.DUNHUANG_NETWORK_GUIDE.syncButtons();return;}
    const S=window.DUNHUANG_NETWORK_VIEW.getState();
    if(S.layer==='all'&&!S.focus&&S.until===1910&&S.context)guide='all';
    else if(S.layer!=='Knowledge transmission'||!S.focus||S.selection?.id!==guide)guide=null;
    document.querySelectorAll('.network-guides [data-network-guide]').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.networkGuide===guide)));
  }
  document.querySelectorAll('[data-network-guide]').forEach(n=>n.addEventListener('click',()=>{
    guide=n.dataset.networkGuide;
    if(window.DUNHUANG_NETWORK_GUIDE){window.DUNHUANG_NETWORK_GUIDE.show(guide);}
    else if(guide==='all'){window.DUNHUANG_NETWORK_VIEW.reset();guide='all';}
    else window.DUNHUANG_NETWORK_VIEW.focusNode(guide);
    document.querySelectorAll('.network-guides [data-network-guide]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.networkGuide===guide)));
    if(n.closest('.document-example'))$('networkShell').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
  }));
  // Only explicit guided actions alter the network. Scrolling never overrides a visitor's filters.
  $('networkShell').addEventListener('click',e=>{if(!e.target.closest('[data-network-guide]'))requestAnimationFrame(syncGuide);});
  $('networkShell').addEventListener('change',syncGuide);
  window.addEventListener('dunhuang:language',syncText);
  const anchors=[...document.querySelectorAll('[data-chapter-link]')];
  const sections=['explore','network','collections'].map($);
  function navigation(){
    const cutoff=innerHeight*.32;
    let current='';for(const s of sections){if(s.getBoundingClientRect().top<=cutoff)current=s.id;}
    for(const a of anchors){if(a.dataset.chapterLink===current)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');}
  }
  window.addEventListener('scroll',navigation,{passive:true});window.addEventListener('resize',navigation);
  syncText();window.DUNHUANG_NETWORK_VIEW.focusNode('N012');navigation();
})();
