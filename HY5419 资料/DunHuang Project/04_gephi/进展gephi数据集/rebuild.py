#!/usr/bin/env python3
"""Rebuild Gephi views from the auditable CSVs. Python 3 standard library only."""
from pathlib import Path
from collections import defaultdict, Counter
import argparse, csv, hashlib, json, platform, sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
VERSION = '2026-10-13-v1'
GEXF = 'http://www.gexf.net/1.2draft'
VIZ = 'http://www.gexf.net/1.2draft/viz'
ET.register_namespace('', GEXF)
ET.register_namespace('viz', VIZ)
INPUTS = ['entities.csv','events.csv','event_evidence.csv','event_participants.csv',
          'quantities.csv','context_only.csv','legacy_mapping.csv','gaps.csv',
          'sources.csv','literature_coverage.csv']

def read(name):
    with (ROOT/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def write(name, rows):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def refs(s):return set(filter(None,s.split(';')))

def check_inputs(data):
    entities={r['Id']:r for r in data['entities.csv']}
    events={r['EventId']:r for r in data['events.csv']}
    sources={r['SourceID']:r for r in data['sources.csv']}
    contexts={r['ContextId'] for r in data['context_only.csv']}
    checks=[]
    def require(ok, message):
        if not ok:raise ValueError(message)
        checks.append(message)
    for name,key in [('entities.csv','Id'),('events.csv','EventId'),
                     ('event_evidence.csv','EvidenceId'),('event_participants.csv','ParticipationId'),
                     ('quantities.csv','QuantityId'),('sources.csv','SourceID'),
                     ('context_only.csv','ContextId'),('legacy_mapping.csv','LegacyId'),('gaps.csv','GapId')]:
        rows=data[name]; ids=[r[key] for r in rows]
        require(all(ids) and len(ids)==len(set(ids)),f'{name}: IDs nonempty and unique')
    for r in data['events.csv']:
        eid=r['EventId']
        require(r['Source'] in entities and r['Target'] in entities,f'{eid}: endpoints resolve')
        require(r['Source']!=r['Target'],f'{eid}: no self transfer')
        require(r['Type']=='Directed' and float(r['Weight'])==1,f'{eid}: directed equal-weight event')
        require(int(r['YearStart'])<=int(r['YearEnd']),f'{eid}: ordered year bounds')
        require(r['Relationship'] not in ['administrative_order','custody_and_access_context'],f'{eid}: core event is a transfer/acquisition')
        require(r['EventConfidence'] in ['high','medium'] and bool(r['DateBasis']),f'{eid}: event threshold and date basis supplied')
        require(bool(refs(r['SourceRef'])) and refs(r['SourceRef'])<=sources.keys(),f'{eid}: source references resolve')
        evidence=[e for e in data['event_evidence.csv'] if e['RecordId']==eid]
        require(refs(r['SourceRef'])<={e['SourceID'] for e in evidence},f'{eid}: every declared source has event-level evidence')
    for r in data['event_evidence.csv']:
        require(r['RecordId'] in events or r['RecordId'] in contexts,f"{r['EvidenceId']}: record resolves")
        require(r['SourceID'] in sources and bool(r['Locator']) and bool(r['SupportFor']),f"{r['EvidenceId']}: source and precise support locator supplied")
    for r in data['event_participants.csv']:
        require(r['EventId'] in events and r['EntityId'] in entities,f"{r['ParticipationId']}: event and participant resolve")
        require(bool(refs(r['SourceRef'])) and refs(r['SourceRef'])<=sources.keys(),f"{r['ParticipationId']}: source refs resolve")
        require(refs(r['SourceRef'])<={e['SourceID'] for e in data['event_evidence.csv'] if e['RecordId']==r['EventId']},f"{r['ParticipationId']}: participant has event-source support")
    for r in data['quantities.csv']:
        require(r['EventId'] in events and r['SourceID'] in sources,f"{r['QuantityId']}: event and source resolve")
        require(float(r['Value'])>=0 and bool(r['Unit']),f"{r['QuantityId']}: nonnegative value and explicit unit")
    for r in data['entities.csv']+data['context_only.csv']:
        require(refs(r['SourceRef'])<=sources.keys(),f"{r.get('Id',r.get('ContextId'))}: source refs resolve")
    for r in data['sources.csv']:
        if r['LocalPath']:
            p=PROJECT/r['LocalPath']
            require(p.is_file() and sha(p)==r['SHA256'],f"{r['SourceID']}: source bytes match recorded hash")
    for r in data['legacy_mapping.csv']:
        require(refs(r['NewRecordId'])<=events.keys()|contexts,f"{r['LegacyId']}: legacy destination resolves")
    return checks

def derive(data):
    events=data['events.csv'];ent={r['Id']:r for r in data['entities.csv']}
    groups=defaultdict(list)
    for e in events:groups[(e['Source'],e['Target'])].append(e)
    edges=[]
    for (source,target),es in sorted(groups.items()):
        edges.append({'Id':f'L_{source}_{target}','Source':source,'Target':target,
          'Type':'Directed','Weight':1,'Label':f'{len(es)}个记录事件',
          'EventCount':len(es),'EventIds':';'.join(e['EventId'] for e in es),
          'Route':';'.join(sorted({e['Route'] for e in es})),
          'Relationship':';'.join(sorted({e['Relationship'] for e in es})),
          'YearStart':min(int(e['YearStart']) for e in es),
          'YearEnd':max(int(e['YearEnd']) for e in es),
          'SourceRef':';'.join(sorted(set().union(*(refs(e['SourceRef']) for e in es)))),
          'EvidenceIds':';'.join(e['EvidenceId'] for e in data['event_evidence.csv'] if e['RecordId'] in {x['EventId'] for x in es}),
          'Confidence':'medium' if any(e['EventConfidence']=='medium' for e in es) else 'high',
          'DateNotes':' / '.join(f"{e['EventId']}: {e['DateDisplay']}" for e in es),
          'GraphView':'actor_transfer_aggregated',
          'Notes':'Weight=1为邻接关系；EventCount为记录事件数，不是件数、捆数或独立来源数。'})
    incident={i for e in edges for i in [e['Source'],e['Target']]}
    nodes=[]
    for eid in sorted(incident):
        n=dict(ent[eid]);n['GraphView']='actor_transfer_aggregated'
        n['InLinks']=sum(e['Target']==eid for e in edges)
        n['OutLinks']=sum(e['Source']==eid for e in edges)
        n['Degree']=n['InLinks']+n['OutLinks']
        n['RecordedEvents']=sum(e['Source']==eid or e['Target']==eid for e in events)
        n['Route']=';'.join(sorted({e['Route'] for e in events if eid in [e['Source'],e['Target']]}))
        nodes.append(n)
    role_edges=[]
    for e in events:
        for src,tgt,role in [(e['Source'],e['EventId'],'transfer_from'),(e['EventId'],e['Target'],'transfer_to')]:
            role_edges.append({'Id':f'R_{e["EventId"]}_{role}','Source':src,'Target':tgt,
              'Type':'Directed','Weight':1,'Label':role,'Role':role,'EventId':e['EventId'],
              'Route':e['Route'],'SourceRef':e['SourceRef'],'Locator':'见event_evidence.csv',
              'GraphView':'entity_event_incidence'})
    for p in data['event_participants.csv']:
        e=next(x for x in events if x['EventId']==p['EventId'])
        role_edges.append({'Id':f'R_{p["ParticipationId"]}','Source':p['EntityId'],'Target':p['EventId'],
          'Type':'Directed','Weight':1,'Label':p['Role'],'Role':p['Role'],
          'EventId':p['EventId'],'Route':e['Route'],'SourceRef':p['SourceRef'],
          'Locator':p['Locator'],'GraphView':'entity_event_incidence'})
    entities_in_role={i for r in role_edges for i in [r['Source'],r['Target']] if i in ent}
    role_nodes=[]
    for i in sorted(entities_in_role):
        n=ent[i];role_nodes.append({'Id':i,'Label':n['Label'],'LabelEN':n['LabelEN'],
          'NodeType':n['NodeType'],'Bipartite':0,'Route':';'.join(sorted({r['Route'] for r in role_edges if i in [r['Source'],r['Target']]})),
          'SourceRef':n['SourceRef'],'EventId':'','YearStart':'','YearEnd':'',
          'DateDisplay':'','GraphView':'entity_event_incidence'})
    for e in events:
        role_nodes.append({'Id':e['EventId'],'Label':f"{e['EventId']} {e['Label']}",
          'LabelEN':e['EventId'],'NodeType':'Event','Bipartite':1,
          'Route':e['Route'],'SourceRef':e['SourceRef'],'EventId':e['EventId'],
          'YearStart':e['YearStart'],'YearEnd':e['YearEnd'],
          'DateDisplay':e['DateDisplay'],'GraphView':'entity_event_incidence'})
    return nodes,edges,role_nodes,role_edges

CORE_POS={'N002':(-340,100),'N006':(-20,220),'N007':(300,220),
          'N013':(-20,-20),'N014':(300,-20),'N010':(-340,-330),
          'N011':(-20,-330),'N009':(300,-330)}
COLORS={'Person':(213,94,0),'Expedition':(0,114,178),'Institution':(0,158,115),
        'Government':(117,83,153),'Event':(150,150,150),'SourceSite':(204,169,45)}
NUMERIC={'Core','Degree','InLinks','OutLinks','RecordedEvents','EventCount','YearStart','YearEnd','Bipartite'}

def gexf(name,nodes,edges,view):
    root=ET.Element(f'{{{GEXF}}}gexf',version='1.2')
    meta=ET.SubElement(root,f'{{{GEXF}}}meta',lastmodifieddate='2026-10-13')
    ET.SubElement(meta,f'{{{GEXF}}}creator').text='HY5419 Dunhuang evidence-linked dataset'
    ET.SubElement(meta,f'{{{GEXF}}}description').text=f'{VERSION}; {view}; static graph; equal edge weight; year bounds are uncertainty attributes.'
    graph=ET.SubElement(root,f'{{{GEXF}}}graph',mode='static',defaultedgetype='directed')
    nk=[k for k in nodes[0] if k not in ['Id','Label']]
    ek=[k for k in edges[0] if k not in ['Id','Source','Target','Type','Weight','Label']]
    for cls,keys in [('node',nk),('edge',ek)]:
        aa=ET.SubElement(graph,f'{{{GEXF}}}attributes',**{'class':cls,'mode':'static'})
        for k in keys:ET.SubElement(aa,f'{{{GEXF}}}attribute',id=k,title=k,type='integer' if k in NUMERIC else 'string')
    nn=ET.SubElement(graph,f'{{{GEXF}}}nodes')
    for index,n in enumerate(nodes):
        el=ET.SubElement(nn,f'{{{GEXF}}}node',id=n['Id'],label=n['Label'])
        av=ET.SubElement(el,f'{{{GEXF}}}attvalues')
        for k in nk:
            if n[k]!='':ET.SubElement(av,f'{{{GEXF}}}attvalue',**{'for':k,'value':str(n[k])})
        r,g,b=COLORS[n['NodeType']]
        ET.SubElement(el,f'{{{VIZ}}}color',r=str(r),g=str(g),b=str(b),a='1.0')
        ET.SubElement(el,f'{{{VIZ}}}size',value='16' if n['NodeType']!='Event' else '12')
        x,y=CORE_POS.get(n['Id'],((index%5)*220-440,-(index//5)*210)) if view=='actor_transfer_aggregated' else ((index%5)*220-440,-(index//5)*210)
        ET.SubElement(el,f'{{{VIZ}}}position',x=str(x),y=str(y),z='0')
    ee=ET.SubElement(graph,f'{{{GEXF}}}edges')
    for e in edges:
        el=ET.SubElement(ee,f'{{{GEXF}}}edge',id=e['Id'],source=e['Source'],target=e['Target'],
                         type='directed',weight=str(e['Weight']),label=e['Label'])
        av=ET.SubElement(el,f'{{{GEXF}}}attvalues')
        for k in ek:
            if e[k]!='':ET.SubElement(av,f'{{{GEXF}}}attvalue',**{'for':k,'value':str(e[k])})
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    ET.indent(root,space='  ');ET.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)

def weak_components(nodes,edges):
    neighbors={n['Id']:set() for n in nodes}
    for e in edges:neighbors[e['Source']].add(e['Target']);neighbors[e['Target']].add(e['Source'])
    unseen=set(neighbors);components=[]
    while unseen:
        todo=[min(unseen)];seen=set()
        while todo:
            n=todo.pop()
            if n in seen:continue
            seen.add(n);todo.extend(neighbors[n]-seen)
        unseen-=seen;components.append(sorted(seen))
    return components

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args()
    data={f:read(f) for f in INPUTS};checks=check_inputs(data)
    nodes,edges,rnodes,redges=derive(data)
    if not args.check_only:
        write('nodes.csv',nodes);write('edges.csv',edges)
        write('辅助_事件参与图/nodes.csv',rnodes);write('辅助_事件参与图/edges.csv',redges)
        gexf('进展gephi数据集.gexf',nodes,edges,'actor_transfer_aggregated')
        gexf('辅助_事件参与图/进展gephi数据集_事件参与图.gexf',rnodes,redges,'entity_event_incidence')
        for route in ['Stein','Pelliot','Qing']:
            es=[e for e in edges if route in refs(e['Route'])];ids={i for e in es for i in [e['Source'],e['Target']]}
            ns=[n for n in nodes if n['Id'] in ids]
            gexf(f'分路线/{route}.gexf',ns,es,'actor_transfer_aggregated')
        write('node_metrics.csv',[{k:n[k] for k in ['Id','Label','InLinks','OutLinks','Degree','RecordedEvents']} for n in nodes])
    def equal_rows(file,expected):
        observed=read(file)
        if observed!=[{k:str(v) for k,v in r.items()} for r in expected]:raise ValueError(f'{file}: stale derived CSV')
        checks.append(f'{file}: exact authoritative-input parity')
    equal_rows('nodes.csv',nodes);equal_rows('edges.csv',edges)
    equal_rows('辅助_事件参与图/nodes.csv',rnodes);equal_rows('辅助_事件参与图/edges.csv',redges)
    xml_checks=[]
    expected_graphs={'进展gephi数据集.gexf':(nodes,edges),'辅助_事件参与图/进展gephi数据集_事件参与图.gexf':(rnodes,redges)}
    for route in ['Stein','Pelliot','Qing']:
        es=[e for e in edges if route in refs(e['Route'])];ids={i for e in es for i in [e['Source'],e['Target']]}
        expected_graphs[f'分路线/{route}.gexf']=([n for n in nodes if n['Id'] in ids],es)
    for fn,(ns,es) in expected_graphs.items():
        doc=ET.parse(ROOT/fn);graph=doc.find(f'{{{GEXF}}}graph')
        observed_n=graph.find(f'{{{GEXF}}}nodes');observed_e=graph.find(f'{{{GEXF}}}edges')
        if {n.get('id') for n in observed_n}!={n['Id'] for n in ns}:raise ValueError(f'{fn}: wrong nodes')
        signatures=lambda seq:{(e['Id'],e['Source'],e['Target'],str(e['Weight'])) for e in seq}
        actual={(e.get('id'),e.get('source'),e.get('target'),e.get('weight')) for e in observed_e}
        if actual!=signatures(es):raise ValueError(f'{fn}: wrong edges or weights')
        if len(actual)!=len(observed_e):raise ValueError(f'{fn}: duplicate XML edges')
        xml_checks.append({'file':fn,'nodes':len(ns),'edges':len(es),'status':'passed'})
    if sum(e['EventCount'] for e in edges)!=len(data['events.csv']):raise ValueError('Aggregated count does not close')
    legacy={r['LegacyId']:r for r in data['legacy_mapping.csv']}
    if legacy['E004']['NewRecordId']!=legacy['E007']['NewRecordId']:raise ValueError('BM duplicate not merged')
    report={'version':VERSION,'status':'passed','scope':'CSV identities, evidence/source closure, hashes, aggregation, XML and CSV parity; source interpretation manually checked as recorded',
      'main_nodes':len(nodes),'main_links':len(edges),'recorded_transfer_events':len(data['events.csv']),
      'main_weight_sum':sum(e['Weight'] for e in edges),'event_count_sum':sum(e['EventCount'] for e in edges),
      'event_participation_nodes':len(rnodes),'event_participation_links':len(redges),
      'evidence_rows':len(data['event_evidence.csv']),'registered_sources':len(data['sources.csv']),
      'sources_used_in_core':sum(int(s['UsedInCore']) for s in data['sources.csv']),
      'route_event_counts':dict(Counter(e['Route'] for e in data['events.csv'])),
      'weak_components':weak_components(nodes,edges),'checked_invariants':len(checks),
      'checks':checks,'graphs':xml_checks,'GephiGUIImport':'not_exercised',
      'limitations':['Formal accession not equated with physical deposit.','Qing front-end handoff not evidenced; disconnected component retained.','S19 archival transcription, not original images.','Calendar conversion is derived.']}
    if not args.check_only:
        (ROOT/'validation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (ROOT/'BUILD_SUCCESS.txt').write_text(f'{VERSION}: all {len(checks)} data/provenance checks and 5 XML parity checks passed.\n',encoding='utf8')
        upstream=hashlib.sha256((''.join(sha(ROOT/f) for f in INPUTS)+sha(Path(__file__))+platform.python_version()).encode()).hexdigest()
        output_files=['nodes.csv','edges.csv','进展gephi数据集.gexf','node_metrics.csv',
                      '辅助_事件参与图/nodes.csv','辅助_事件参与图/edges.csv',
                      '辅助_事件参与图/进展gephi数据集_事件参与图.gexf',
                      '分路线/Stein.gexf','分路线/Pelliot.gexf','分路线/Qing.gexf','validation_report.json','BUILD_SUCCESS.txt']
        delivery_files=['使用说明.md','数据字典.md','使用说明.html','进展gephi数据集_结构预览.svg',
                        'render_delivery.py','independent_validation.json','method_sources/日期换算记录.md',
                        'method_sources/HKO_1910_公农历对照表.pdf']
        output_files += [f for f in delivery_files if (ROOT/f).is_file()]
        manifest={'schema_version':'1.0','run_id':'HY5419-gephi-progress-20261013','stage_id':'audited-graph-build',
          'scientific_question':'1900–1910 manuscript acquisition and custody-transfer batches; unit=recorded transfer event; participants separated from transferring actors',
          'state':'complete','inputs':[{'input_id':f'input-{i}','role':'authoritative-curated-CSV',
              'path':f,'identity':sha(ROOT/f),'verification':'CSV closure and source hashes'} for i,f in enumerate(INPUTS)],
          'code':{'entrypoint':'rebuild.py','version':sha(Path(__file__)),'parameters':VERSION+'; grouping=Source,Target; Weight=1; static GEXF1.2'},
          'environment':{'identity':f'Python {platform.python_version()}; standard library; {platform.system()}',
            'activation':'python3 rebuild.py','verification':'actual successful execution'},
          'partition_contract':{'unit':'single curated graph bundle','expected_task_ids':['build'],
            'retry_rule':'fix source or structural errors, then rerun','overwrite_rule':'overwrite only derived CSV/GEXF/validation outputs; input CSVs untouched; this dated bundle is isolated from the previous pilot'},
          'tasks':[{'task_id':'build','state':'complete','attempt':1,'exit_code':0,'success_marker':'BUILD_SUCCESS.txt',
            'skip_record':None,'output_ids':[f'out-{i}' for i in range(len(output_files))],'evidence':'validation_report.json'}],
          'outputs':[{'output_id':f'out-{i}','role':'validated-derived-artifact','completion_critical':True,
            'path':f,'semantic_state':'produced','sha256':sha(ROOT/f),'schema':Path(f).suffix or 'text',
            'row_or_record_count':len(read(f)) if f.endswith('.csv') else None,
            'upstream_fingerprint':upstream,'verification':'input invariants, graph endpoint and count parity'} for i,f in enumerate(output_files)],
          'checkpoints':[{'checkpoint_id':'build-check','task_id':'build','completion_contract':'all invariant checks and graph counts match canonical events','status':'passed','evidence':'validation_report.json'}],
          'failures_and_fallbacks':[],
          'privacy_and_release':'Local research dataset from user-provided literature; only short evidence excerpts; no upload or publication.',
          'next_action':f'Open the main GEXF in Gephi and save a native .gephi project after verifying {len(nodes)} nodes and {len(edges)} links.',
          'extensions':{'literature_source_hashes':'sources.csv','GephiGUIImport':'not_exercised',
            'delivery_render_entrypoint':'render_delivery.py','delivery_render_version':sha(ROOT/'render_delivery.py')}}
        (ROOT/'run-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k] for k in ['status','main_nodes','main_links','recorded_transfer_events','event_participation_nodes','event_participation_links','route_event_counts']},ensure_ascii=False))

if __name__=='__main__':main()
