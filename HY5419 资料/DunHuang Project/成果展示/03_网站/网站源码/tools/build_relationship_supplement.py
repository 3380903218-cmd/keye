"""Produce portable Gephi / CSV files without changing the saved Gephi export."""
from pathlib import Path
import csv, hashlib, json, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]; DIST=ROOT/'dist'; ASSETS=DIST/'assets'
def js_data(name):
    return json.loads((DIST/name).read_text(encoding='utf-8').split('=',1)[1].strip().removesuffix(';'))
base=js_data('network-data.js'); extra=js_data('relationship-supplement-data.js')
assert base['meta']['sourceHash']==extra['meta']['baseHash']
merged={**base,'meta':{**base['meta'],'version':'1.2.0','date':extra['meta']['date'],'supplement':extra['meta']}}
for key in ('nodes','edges','events','evidence'):merged[key]=base[key]+extra[key]
assert [len(merged[k]) for k in ('nodes','edges','events','evidence')]==[132,157,48,57]
for key,id_key in [('nodes','id'),('edges','id'),('events','EventId'),('evidence','id')]:
    assert len({x[id_key] for x in merged[key]})==len(merged[key])
nodes={n['id'] for n in merged['nodes']}; proof={e['id'] for e in merged['evidence']}
sources={s['SourceId'] for s in merged['sources']}; events={e['EventId'] for e in merged['events']}
for e in extra['edges']:
    a=e['attributes'];assert e['source'] in nodes and e['target'] in nodes
    assert a['EventId'] in events
    assert set(a['EvidenceIds'].split(';'))<=proof and set(a['SourceIds'].split(';'))<=sources
    assert 1900<=int(a['YearStart'])<=int(a['YearEnd'])<=1910
    assert a['RoleEN'] and a['RoleZH']
for e in extra['events']:
    assert e['english']['date'] and e['english']['note'] and e['NotesZH']
assert not any(e['attributes']['Relation']=='conceals_for' for e in merged['edges'])
assert next(e for e in extra['events'] if e['EventId']=='SUP_REQUEST19101203')['ProcessState']=='Proposal made'

# Append to the original XML tree so its nodes, roles, positions and colours survive.
original=ASSETS/'dunhuang-network.gexf'
assert hashlib.sha256(original.read_bytes()).hexdigest()==extra['meta']['baseHash']
tree=ET.parse(original); root=tree.getroot(); G=root.tag.split('}')[0][1:]; V=G+'/viz'
ET.register_namespace('',G); ET.register_namespace('viz',V)
q=lambda name:'{'+G+'}'+name
graph=root.find(q('graph'))
for kind,items in [('node',extra['nodes']),('edge',extra['edges'])]:
    attributes=next(a for a in graph.findall(q('attributes')) if a.get('class')==kind)
    attr_ids={a.get('title'):a.get('id') for a in attributes}
    for item in items:
        for title in item['attributes']:
            if title not in attr_ids:
                aid='supp_'+title.lower();attr_ids[title]=aid
                ET.SubElement(attributes,q('attribute'),id=aid,title=title,type='string')
    container=graph.find(q(kind+'s'))
    for item in items:
        fields={'id':item['id'],'label':item['label']['en'] if kind=='node' else item['label']}
        if kind=='edge':fields.update(source=item['source'],target=item['target'])
        entry=ET.SubElement(container,q(kind),fields); vals=ET.SubElement(entry,q('attvalues'))
        for key,value in item['attributes'].items():ET.SubElement(vals,q('attvalue'),{'for':attr_ids[key],'value':str(value)})
        rgb=item['color'].lstrip('#');ET.SubElement(entry,'{'+V+'}color',dict(zip(('r','g','b'),[str(int(rgb[i:i+2],16)) for i in (0,2,4)])))
        if kind=='node':
            ET.SubElement(entry,'{'+V+'}position',x=str(item['x']),y=str(-item['y']))
            ET.SubElement(entry,'{'+V+'}size',value=str(item['size']))
meta=root.find(q('meta'))
if meta is not None:
    meta.set('lastmodifieddate',extra['meta']['date'])
    desc=meta.find(q('description'))
    if desc is not None:desc.text='Original Gephi export plus cited 1900–1910 research additions. New positions provisional; centralities not recalculated.'
ET.indent(tree,space='  ');tree.write(ASSETS/'dunhuang-network-expanded.gexf',encoding='utf-8',xml_declaration=True)

def table(name,rows,columns):
    with (ASSETS/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
nrows=[{'Id':n['id'],'Label':n['label']['en'],**n['attributes']} for n in merged['nodes']]
erows=[{'Id':e['id'],'Source':e['source'],'Target':e['target'],'Type':'Directed','Label':e['label'],**e['attributes']} for e in merged['edges']]
for filename,rows,first in [('network-expanded-nodes.csv',nrows,['Id','Label','LabelZH','NodeType']),('network-expanded-edges.csv',erows,['Source','Target','Id','Type','Label'])]:
    columns=first+sorted(set().union(*(row.keys() for row in rows))-set(first));table(filename,rows,columns)
source_urls={s['SourceId']:s['URL'] for s in base['sources']}
proof_rows=[{**e,'sourceURL':source_urls[e['source']]} for e in extra['evidence']]
table('relationship-supplement-evidence.csv',proof_rows,list(proof_rows[0]))
print('PASS: 132 nodes / 157 relationships; original Gephi export retained; 48 activity records / 57 evidence notes.')
