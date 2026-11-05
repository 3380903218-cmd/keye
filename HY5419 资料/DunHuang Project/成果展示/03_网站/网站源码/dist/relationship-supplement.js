/* Add cited research records while retaining the immutable Gephi snapshot. */
(() => {
  'use strict';
  const base=window.DUNHUANG_NETWORK,extra=window.DUNHUANG_RELATIONSHIP_SUPPLEMENT;
  if(!base||!extra)return;
  if(base.meta.sourceHash!==extra.meta.baseHash)throw new Error('Relationship supplement: base snapshot mismatch');
  for(const key of ['nodes','edges','events','evidence']){
    const id=key==='events'?'EventId':'id',seen=new Set(base[key].map(x=>x[id]));
    for(const x of extra[key]){if(seen.has(x[id]))throw new Error('Duplicate supplement ID: '+x[id]);seen.add(x[id]);}
  }
  window.DUNHUANG_NETWORK_BASE=base;
  window.DUNHUANG_NETWORK={...base,meta:{...base.meta,version:'1.2.0',date:extra.meta.date,supplement:extra.meta},
    nodes:[...base.nodes,...extra.nodes],edges:[...base.edges,...extra.edges],
    events:[...base.events,...extra.events],evidence:[...base.evidence,...extra.evidence]};
})();
