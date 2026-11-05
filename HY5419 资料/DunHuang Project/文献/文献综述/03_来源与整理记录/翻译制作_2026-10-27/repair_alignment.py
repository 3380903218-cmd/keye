# -*- coding: utf-8 -*-
"""Replace legacy long-span readings with isolated source-span translations."""
from pathlib import Path
import concurrent.futures, importlib.util, json, time
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bilingual',ROOT/'make_bilingual.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
manual=json.loads((ROOT/'reviewed_corrections.json').read_text())
affected=set(json.loads((ROOT/'段落长度复核.json').read_text())['affected_group_ids'])
jobs=[]
for path in sorted(ROOT.glob('*_source.json')):
    manifest=json.loads(path.read_text());key=manifest['key'];cache={}
    for line in (ROOT/(key+'_translations.jsonl')).read_text().splitlines():
        item=json.loads(line);cache[item['id']]=item
    for seg in manifest['segments']:
        if seg['id'] in manual or m.notation_only(key,seg['en']):continue
        old=cache[seg['id']]
        if old.get('method')=='isolated-source-v2':continue
        words=len(seg['en'].split())
        special=(key=='L08' and any(t in seg['en'].lower() for t in ('mahāmāyūrī','dharani','mantra')))
        needs=((key!='L01' and words>=25) or seg['id'] in affected or special)
        if needs:jobs.append((key,seg))
print('ISOLATED REPAIR',len(jobs),'spans',sum(len(s['en'].split()) for _,s in jobs),'English words',flush=True)
(ROOT/'单段重译范围.json').write_text(json.dumps([s['id'] for _,s in jobs],ensure_ascii=False,indent=2))
done=0;started=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    futures={pool.submit(m.translate,s):(k,s) for k,s in jobs}
    for future in concurrent.futures.as_completed(futures):
        key,seg=futures[future];item=future.result()
        with (ROOT/(key+'_translations.jsonl')).open('a',encoding='utf-8') as out:
            out.write(json.dumps(item,ensure_ascii=False)+'\n')
        done+=1
        if done%20==0 or done==len(jobs):
            print('repaired %d/%d; elapsed %.0fs'%(done,len(jobs),time.time()-started),flush=True)
print('REPAIR FINISHED',flush=True)
