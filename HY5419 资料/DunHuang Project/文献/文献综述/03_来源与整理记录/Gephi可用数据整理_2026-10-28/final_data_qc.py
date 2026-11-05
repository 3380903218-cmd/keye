# -*- coding: utf-8 -*-
"""Read-only, exact-deliverable audit. Source anchors locate rather than prove claims."""
from pathlib import Path
import json, hashlib, csv, unicodedata, re, xml.etree.ElementTree as ET
from openpyxl import load_workbook
from bs4 import BeautifulSoup
import fitz

R=Path(__file__).resolve().parent; B=R.parents[1]; P=B.parents[1]
x=json.loads((R/'curated_data.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:re.sub(r'\s+','',unicodedata.normalize('NFKC',s)).casefold()
anchors=[]
for e in x['evidence']:
    p=Path(e['file']); assert digest(p)==e['source_sha256'],e['id']
    pages=e['pages']
    if not pages:
        m=re.search(r'(?:章节)?PDF([0-9、–-]+)',e['printed'])
        if m:
            pages=[]
            for part in m[1].split('、'):
                nums=[int(z) for z in re.split('[–-]',part)]
                pages.extend(range(nums[0],nums[-1]+1))
    if p.suffix.lower()=='.pdf':
        with fitz.open(p) as pdf:
            text='\n'.join(pdf[n-1].get_text() for n in (pages or range(1,len(pdf)+1)))
    else:
        text=p.read_text(encoding='utf-8',errors='replace')
        if p.suffix.lower() in ['.html','.htm']:text=BeautifulSoup(text,'html.parser').get_text(' ')
    assert norm(e['anchor']) in norm(text),[e['id'],e['printed'],e['anchor']]
    anchors.append(dict(id=e['id'],source=e['source'],pages_checked=pages or 'full saved text',anchor_found=True,sha256=e['source_sha256']))
(R/'证据定位核验.json').write_text(json.dumps(dict(status='passed',count=len(anchors),checks=anchors),ensure_ascii=False,indent=2))
ns={n['Id'] for n in x['nodes']}; es={e['Id'] for e in x['edges']}
events={e['EventId'] for e in x['events']}; sources={s['SourceId'] for s in x['sources']}; evid={e['id'] for e in x['evidence']}
assert len(ns)==122 and len(es)==136 and len(events)==42 and len(sources)==21 and len(evid)==49
assert all(e['Source'] in ns and e['Target'] in ns for e in x['edges'])
assert events<=ns
for group in ['nodes','edges','events']:
    for row in x[group]:
        assert not any('ReviewDecision' in k for k in row)
        assert set(filter(None,row.get('SourceIds','').split(';')))<=sources,(group,row)
        assert set(filter(None,row.get('EvidenceIds','').split(';')))<=evid,(group,row)
        for key in ['YearStart','YearEnd']:
            if row.get(key)!='' and row.get(key) is not None:assert 1900<=int(row[key])<=1910,(group,row)
for e in x['events']:assert re.fullmatch('[a-z_]+',e['Action']),e
assert next(e for e in x['events'] if e['EventId']=='DH006')['Action']=='arrival_in_city'
folder=B/'Gephi传播网络_导入文件'; out=B/'Gephi传播网络_可直接使用.xlsx'; wb=load_workbook(out,data_only=False)
for fname,sheet in [('nodes.csv','07_Gephi_Nodes'),('edges.csv','08_Gephi_Edges')]:
    with (folder/fname).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f))
    vals=[['' if v is None else str(v) for v in row] for row in wb[sheet].iter_rows(values_only=True)]
    assert len(rows)==len(vals)
    for i,(a,b) in enumerate(zip(rows,vals)):
        if a!=b:
            assert fname=='edges.csv' and all(c==d or (c=='1.0' and d=='1') for c,d in zip(a,b)),[fname,i,a,b]
root=ET.parse(folder/'敦煌双层传播网络.gexf').getroot(); q={'g':'http://www.gexf.net/1.2draft'}
assert {n.attrib['id'] for n in root.findall('.//g:node',q)}==ns
assert {n.attrib['id'] for n in root.findall('.//g:edge',q)}==es
assert '/Users/' not in (folder/'web_network_data.json').read_text()
old=json.loads((R.parent/'Gephi完善整理_2026-10-28'/'输入快照与哈希.json').read_text())
unchanged={rel:digest(P/rel)==h for rel,h in old.items()}
assert all(unchanged.values()),unchanged
report=dict(status='passed',workbook_sha256=digest(out),counts=dict(nodes=len(ns),edges=len(es),events=len(events),sources=len(sources),evidence=len(evid)),source_anchors=len(anchors),csv_excel_parity='passed; numeric weight 1 and 1.0 equivalent',gexf_ids_endpoints='passed',original_inputs_preserved=unchanged,old_review_workbook_sha256=digest(B/'Gephi完善_文献证据与数据工作表.xlsx'))
(R/'数据一致性核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
