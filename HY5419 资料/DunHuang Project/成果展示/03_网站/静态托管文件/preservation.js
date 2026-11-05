/* Bilingual, dated preservation evidence; no changes to map or Gephi research inputs. */
(() => {
  'use strict';
  const data=window.DUNHUANG_PRESERVATION_DATA, host=document.getElementById('preservation');
  if(!host||!data)return;
  const copy={
    en:{kicker:'PRESERVATION & COMPLETENESS',title:'How are the manuscripts preserved?',intro:'Conservation records show changes to paper, bindings and storage. Textual completeness needs a separate assessment.',observation:'What can fragmentary scrolls tell us?',table:'Three documented conservation examples',institution:'Library & manuscript',state:'Recorded condition',treatment:'Treatment & housing',limit:'After treatment & completeness',history:'How did the present objects take shape?',historyIntro:'Fragmentation and changes in format also belong to the history of these collections.',note:'The examples concern paper manuscripts. The paintings and objects listed above require separate comparisons. No common condition survey is available here from which to calculate institutional completeness rates or rank storage conditions.',sources:'Sources for preservation records',download:'Download these evidence records ↓',cite:'Source',verified:'Sources checked: 29 October 2026',label:'Preservation and manuscript completeness'},
    zh:{kicker:'保存方式与文献完整度',title:'这些文献如何保存？',intro:'修复记录可以说明纸张、装帧与存放方式的变化。文字是否完整，需要另外判断。',observation:'残卷多，能说明什么？',table:'三项有记录的修复案例',institution:'图书馆与写本',state:'修复前的状况',treatment:'修复与存放方式',limit:'修复后与完整度',history:'今天的文献形态如何形成？',historyIntro:'残片和装帧的形成过程，也是馆藏历史的一部分。',note:'以上比较限于纸本文献，相关绘画与文物需另行研究。本节尚无统一的逐件状况调查，不能据此计算各馆完整率或排列保存条件的优劣。',sources:'保存状况资料出处',download:'下载本节证据记录 ↓',cite:'来源',verified:'资料核对：2026年10月29日',label:'保存方式与文献完整度'}
  };
  let lang='en';
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const t=value=>esc(value[lang]);
  const ref=(id,loc)=>{const s=data.sources.find(x=>x.id===id);return `<a class="preservation-cite" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${copy[lang].cite} ${id} · ${esc(loc||s.year)} ↗</a>`;};
  function render(){
    lang=window.DUNHUANG_EXHIBITION.getState().lang;
    const c=copy[lang],o=data.observations[0],wasOpen=host.querySelector('details')?.open;
    host.setAttribute('aria-label',c.label);
    host.innerHTML=`<header class="preservation-heading"><p class="eyebrow">${c.kicker}</p><h3>${c.title}</h3><p class="preservation-deck">${c.intro}</p><p class="preservation-scope">${t(data.scope)}</p></header>
      <aside class="preservation-observation"><h4>${c.observation}</h4><p>${t(o.claim)}</p><p class="preservation-inference">${t(o.limit)}</p>${ref(o.source,'2025 · BD00020')}</aside>
      <table class="preservation-table"><caption>${c.table}</caption><thead><tr><th scope="col">${c.institution}</th><th scope="col">${c.state}</th><th scope="col">${c.treatment}</th><th scope="col">${c.limit}</th></tr></thead><tbody>${data.treatments.map(r=>`<tr data-preservation-case="${r.id}"><th scope="row"><span class="preservation-city">${t(r.city)}</span><strong>${t(r.institution)}</strong><span class="preservation-object">${t(r.object)}</span><small>${t(r.date)}</small></th><td data-label="${c.state}">${t(r.condition)}</td><td data-label="${c.treatment}">${t(r.treatment)}</td><td data-label="${c.limit}">${t(r.limit)}${ref(r.source,r.locator)}</td></tr>`).join('')}</tbody></table>
      <div class="preservation-history-heading"><h4>${c.history}</h4><p>${c.historyIntro}</p></div><div class="preservation-histories">${data.histories.map(h=>`<article data-preservation-history="${h.id}"><p class="preservation-meta">${t(h.meta)}</p><h5>${t(h.title)}</h5><p>${t(h.body)}</p>${h.counts?`<dl class="preservation-counts">${h.counts.map(n=>`<div><dt>${esc(n.value)}</dt><dd>${esc(n[lang])}</dd></div>`).join('')}</dl>`:''}<p class="preservation-limit">${t(h.limit)}</p>${ref(h.source,h.locator)}</article>`).join('')}</div>
      <p class="preservation-boundary">${c.note}</p><details class="preservation-sources" ${wasOpen?'open':''}><summary>${c.sources} (6)</summary><ol>${data.sources.map(s=>`<li id="preservation-source-${s.id}"><span>${esc(s.id)}</span> ${esc(s.author)} (${s.year}). <a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${t(s.title)} ↗</a>. <em>${esc(s.publication)}</em>. <small>${esc(s.locator)}</small></li>`).join('')}</ol></details><div class="preservation-footer"><button class="text-link" type="button" id="preservationDownload">${c.download}</button><span>${c.verified}</span></div>`;
    host.querySelector('#preservationDownload').addEventListener('click',()=>{const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='dunhuang-preservation-evidence.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);});
  }
  window.addEventListener('dunhuang:language',render);render();
})();
