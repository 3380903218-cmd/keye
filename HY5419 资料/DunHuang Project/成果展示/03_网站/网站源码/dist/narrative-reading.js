/* Reading paths point to existing, page-located evidence rather than new claims. */
(() => {
  'use strict';
  const host=document.getElementById('furtherReading'),sources=new Map(window.DUNHUANG_NETWORK.sources.map(s=>[s.SourceId,s]));
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const readings=[
    {id:'S07',evidence:'EV046',question:['How was an examination recorded?','检查怎样留下了文字记录？'],title:'Serindia, Volume II',pages:['pp. 916–917','第916–917页'],note:['Stein prints extracts from Pelliot’s inspection memorandum.','斯坦因刊出的伯希和检查备忘录摘文。']},
    {id:'G06',evidence:'EV054',question:['Who helped arrange the collection?','谁协助整理了这些材料？'],pages:['pp. 215–216','第215–216页'],note:['Lorimer’s work and Droop’s participation in cataloguing.','洛里默的工作及德鲁普参与编目的记载。']},
    {id:'G07',evidence:'EV021',question:['What did the ministry telegram record?','学部电报记录了什么？'],pages:['p. 48','第48页'],note:['The 5 October 1909 telegram from Beijing to the office in Lanzhou.','1909年10月5日北京致兰州机构的电报。']}
  ];
  function render(){
    const zh=window.DUNHUANG_EXHIBITION.getState().lang==='zh',i=zh?1:0;
    host.setAttribute('aria-label',zh?'继续查阅的文献与页码':'Further reading with source locations');
    host.innerHTML=`<h3>${zh?'从这些问题继续阅读':'Continue with these sources'}</h3><p class="reading-source-intro">${zh?'以下页码对应正文中的具体实例。查阅原文时，可将作者的记载与本页整理的关系相互核对。':'These page references correspond to examples in the text. Use them to compare the source accounts with the relationships presented here.'}</p><div class="reading-source-list">${readings.map(r=>{const s=sources.get(r.id);return `<article data-reading-source="${r.id}" data-reading-proof="${r.evidence}"><h4>${esc(r.question[i])}</h4><p>${esc(s.Author)} (${esc(s.Year)}). <a href="${esc(s.URL)}" target="_blank" rel="noopener noreferrer">${esc(r.title||s.Title)} ↗</a></p><p class="reading-source-location">${esc(r.pages[i])} · ${esc(r.note[i])}</p></article>`;}).join('')}</div>`;
  }
  window.addEventListener('dunhuang:language',render);render();
})();
