#!/usr/bin/env python3
"""Export event-centred Gephi views from the Chinese recording workbook.

Requires openpyxl. NetworkX is optional and provides a deterministic starting layout.
By default only records marked 可整理事件 enter the main graph; all records enter review.
"""
from pathlib import Path
from collections import defaultdict, Counter
import argparse, csv, hashlib, json, platform, re, shutil
import xml.etree.ElementTree as ET
from openpyxl import load_workbook

G='http://www.gexf.net/1.2draft'
V='http://www.gexf.net/1.2draft/viz'
ET.register_namespace('',G);ET.register_namespace('viz',V)
SCRIPT=Path(__file__).resolve()
ROOT=SCRIPT.parent
PROJECT=ROOT.parents[1]
DEFAULT_WORKBOOK=PROJECT/'06_notes/2026-10-13_双层传播网络补采集/整理版_2026-10-13/双层传播网络_中文记录工作簿_整理版.xlsx'
DEFAULT_OUT=PROJECT/'04_gephi/双层传播网络_Gephi'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def refs(value):return list(dict.fromkeys(x.strip() for x in value.split(';') if x.strip()))
def rows(workbook,name):
    ws=workbook[name];headers=[str(c.value or '') for c in ws[1]]
    assert all(headers),f'{name}: blank column header'
    out=[]
    for cells in ws.iter_rows(min_row=2,values_only=True):
        if not any(v is not None and str(v).strip() for v in cells):continue
        out.append(dict(zip(headers,['' if v is None else str(v).strip() for v in cells])))
    return out
def index(records,key,label):
    values=[r[key] for r in records]
    if not all(values) or len(values)!=len(set(values)):raise ValueError(f'{label}: empty or duplicate IDs')
    return {r[key]:r for r in records}
def write_csv(path,records,fields=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=fields or list(records[0])
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)

def load_contract(path):
    wb=load_workbook(path,data_only=True)
    data={name:rows(wb,name) for name in ['阅读记录','事件整理','现有主体ID','现有来源ID','对象与批次','作品与载体','复制品登记','参与角色']}
    reading=index(data['阅读记录'],'阅读ID','reading')
    events=index(data['事件整理'],'事件ID','events')
    entities=index(data['现有主体ID'],'实体ID','entities')
    sources=index(data['现有来源ID'],'来源ID','sources')
    objects=index(data['对象与批次'],'ObjectId','objects')
    works=index(data['作品与载体'],'WorkId','works')
    representations=index(data['复制品登记'],'RepresentationId','representations')
    sets=[set(events),set(entities),set(objects),set(works),set(representations)]
    flat=[v for s in sets for v in s]
    if len(flat)!=len(set(flat)):raise ValueError('Node IDs must be globally unique across entities/events/objects/works/representations')
    for e in events.values():
        if e['核验状态'] not in ['可整理事件','待核验','仅线索','背景／方法','排除']:raise ValueError('Unknown status: '+e['事件ID'])
        if e['网络层'] not in ['实物流转','知识传播','两层关联']:raise ValueError('Unknown layer: '+e['事件ID'])
        rids=refs(e['关联阅读ID'])
        if not rids or not set(rids)<=reading.keys():raise ValueError('Event reading links unresolved: '+e['事件ID'])
        for key,register in [('对象／批次ObjectId',objects),('复制品RepresentationId',representations),('作品WorkId',works),('转出主体ID（实物）',entities),('接收／目的主体ID（实物）',entities)]:
            if e[key] and e[key] not in register:raise ValueError(f'{e["事件ID"]}: unresolved {key}: {e[key]}')
        for rid in rids:
            if not set(refs(reading[rid]['来源ID']))<=sources.keys():raise ValueError('Unknown evidence source: '+rid)
    for p in data['参与角色']:
        if p['事件ID'] not in events or p['主体ID'] not in entities:raise ValueError('Unresolved participation: '+p['参与记录ID'])
        if not set(refs(p['来源ID']))<=sources.keys():raise ValueError('Unresolved participant source: '+p['参与记录ID'])
    for r in representations.values():
        if r['来源对象组'] and r['来源对象组'] not in objects:raise ValueError('Representation origin unresolved')
    return data,reading,events,entities,sources,objects,works,representations

def year_bounds(date,precision):
    # First year is the event year. Later years can be contextual (e.g. 1909 inferred from a 1910 letter).
    found=re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',date)
    if not found:return '',''
    if precision=='year_range':return min(map(int,found)),max(map(int,found))
    return int(found[0]),int(found[0])

def build_view(allowed,data,reading,events,entities,objects,works,reps):
    nodes={};edges={}
    def node(nid):
        if nid in nodes:return nodes[nid]
        n={'Id':nid,'Label':'','NodeType':'','Layer':'','RecordStatus':'','EpistemicStatus':'',
           'EventId':'','Action':'','DateOriginal':'','YearStart':'','YearEnd':'','DatePrecision':'',
           'ObjectId':'','RepresentationId':'','WorkId':'','RelatedCollectionNote':'','SourceRef':'','Locator':'','Notes':''}
        if nid in entities:
            r=entities[nid];n.update(Label=r['中文名称'],NodeType=r['节点类型'],RecordStatus='实体登记',Notes=r['注意事项'])
        elif nid in objects:
            r=objects[nid];n.update(Label=r['工作名称'],NodeType='Object' if r['对象单位'].startswith('原卷') else 'Collection',
                RecordStatus=r['对象单位'],EpistemicStatus='registered_analytical_unit',ObjectId=nid,
                RelatedCollectionNote=r['关联集合（非逐件已核）'],SourceRef=r['来源ID'],Locator=r['定位'],Notes='；'.join(filter(None,[r['馆藏号／旧号（含限定）'],r['范围与身份说明'],r['待核问题']])))
        elif nid in works:
            r=works[nid];n.update(Label=r['题名（工作命名须注明）'],NodeType='Work',RecordStatus='载体登记（有获取限制）',
                WorkId=nid,DateOriginal=r['原始日期／日期依据'],SourceRef=r['证据来源ID'],Locator=r['证据定位'],Notes=r['获取与核验状态'])
        elif nid in reps:
            r=reps[nid];n.update(Label=r['类型与单位'],NodeType='Representation',RecordStatus='复制品集合登记（逐张未核）',
                RepresentationId=nid,ObjectId=r['来源对象组'],DateOriginal=r['日期依据'],SourceRef=r['来源ID'],Locator=r['定位'],Notes=r['对应状态与待核问题'])
        elif nid in events:
            e=events[nid];intent='意向' in e['行为类型'] or '计划' in e['行为类型']
            ys,ye=year_bounds(e['原始日期与历法'],e['日期精度'])
            name=e['证据支持什么'].split('；')[0] if nid.startswith('DH') else e['行为类型']
            n.update(Label=nid+' '+name,NodeType='Event',Layer=e['网络层'],RecordStatus=e['核验状态'],
                EpistemicStatus='reported_intention' if intent else 'reported_activity',EventId=nid,Action=e['行为类型'],
                DateOriginal=e['原始日期与历法'],YearStart=ys,YearEnd=ye,DatePrecision=e['日期精度'],
                ObjectId=e['对象／批次ObjectId'],RepresentationId=e['复制品RepresentationId'],WorkId=e['作品WorkId'],
                SourceRef=';'.join(sorted({s for rid in refs(e['关联阅读ID']) for s in refs(reading[rid]['来源ID'])})),
                Locator=e['证据来源及定位'],Notes=e['尚未确认什么'])
            if e['核验状态']=='待核验':n['Label']='[待核] '+n['Label']
        else:raise ValueError('Unknown node '+nid)
        n['FullLabel']=n['Label']
        if n['NodeType'] in ['Object','Collection','Work','Representation']:
            short=n['Label'] if len(n['Label'])<=18 else n['Label'][:18]+'…'
            n['Label']=nid+' '+short
        nodes[nid]=n;return n

    def edge(src,tgt,e,relation,role='',source_ref='',locator='',participation_id='',note=''):
        eid=e['事件ID'];key=(src,tgt,eid)
        node(src);node(tgt)
        if key in edges:
            old=edges[key]
            old['Role']=';'.join(dict.fromkeys(refs(old['Role'])+refs(role)))
            old['ParticipationIds']=';'.join(dict.fromkeys(refs(old['ParticipationIds'])+refs(participation_id)))
            old['SourceRef']=';'.join(sorted(set(refs(old['SourceRef']))|set(refs(source_ref))))
            return
        event_node=node(eid)
        edges[key]={'Id':f'E_{eid}_{src}_{tgt}','Source':src,'Target':tgt,'Type':'Directed','Weight':1,
           'Label':{'transfer_from':'转出／拨送关联','transfer_to':'接收关联','dispatch_destination':'送寄目的方（收件日未核）',
             'subject_of_event':'所涉对象','participant_in_event':'参与角色','produces_work':'形成记录／载体',
             'produces_representation':'摄影／复制品组'}.get(relation,relation),
           'Relation':relation,'Role':role,'Layer':e['网络层'],'EventId':eid,'EventCount':1,
           'ReviewRequired':1 if e['核验状态']=='待核验' else 0,'RecordStatus':e['核验状态'],
           'EpistemicStatus':event_node['EpistemicStatus'],'DateOriginal':e['原始日期与历法'],
           'YearStart':event_node['YearStart'],'YearEnd':event_node['YearEnd'],'DatePrecision':e['日期精度'],
           'ReadingIds':e['关联阅读ID'],'SourceRef':source_ref or event_node['SourceRef'],
           'Locator':locator or e['证据来源及定位'],'ParticipationIds':participation_id,
           'Notes':'；'.join(filter(None,[note,e['尚未确认什么']]))}

    for eid in sorted(allowed):
        e=events[eid];node(eid)
        if e['对象／批次ObjectId']:edge(e['对象／批次ObjectId'],eid,e,'subject_of_event','对象／批次关联')
        if e['转出主体ID（实物）']:edge(e['转出主体ID（实物）'],eid,e,'transfer_from','转出／拨送主体')
        if e['接收／目的主体ID（实物）']:
            relation='dispatch_destination' if '送寄' in e['行为类型'] else 'transfer_to'
            edge(eid,e['接收／目的主体ID（实物）'],e,relation,'所称送寄目的方' if relation=='dispatch_destination' else '接收行动／机构')
        for p in data['参与角色']:
            if p['事件ID']!=eid:continue
            if p['主体ID']==e['接收／目的主体ID（实物）']:
                edge(eid,p['主体ID'],e,'dispatch_destination' if '送寄' in e['行为类型'] else 'transfer_to',p['具体角色'],p['来源ID'],p['定位'],p['参与记录ID'],p['限制'])
            else:
                edge(p['主体ID'],eid,e,'transfer_from' if p['主体ID']==e['转出主体ID（实物）'] else 'participant_in_event',
                     p['具体角色'],p['来源ID'],p['定位'],p['参与记录ID'],p['限制'])
        if e['作品WorkId']:edge(eid,e['作品WorkId'],e,'produces_work','所记载的记录／载体成果',note='这条边不表示已经公开出版；具体载体获取状态见节点属性。')
        if e['复制品RepresentationId']:edge(eid,e['复制品RepresentationId'],e,'produces_representation','文中照片组',note='仅按组登记，不代表具体影像已取得或已刊布。')

    incident_layers=defaultdict(set);incident_refs=defaultdict(set)
    for e in edges.values():
        for nid in [e['Source'],e['Target']]:
            incident_layers[nid].add(e['Layer']);incident_refs[nid].update(refs(e['SourceRef']))
    for nid,n in nodes.items():
        if not n['Layer']:n['Layer']=';'.join(sorted(incident_layers[nid]))
        if not n['SourceRef']:n['SourceRef']=';'.join(sorted(incident_refs[nid]))
    return [nodes[i] for i in sorted(nodes)],sorted(edges.values(),key=lambda e:e['Id'])

def positions(nodes,edges):
    try:
        import networkx as nx
        graph=nx.Graph();graph.add_nodes_from(n['Id'] for n in nodes);graph.add_edges_from((e['Source'],e['Target']) for e in edges)
        components=sorted(nx.connected_components(graph),key=lambda c:(-len(c),min(c)))
        out={}
        for k,component in enumerate(components):
            sub=graph.subgraph(sorted(component));scale=max(220,len(component)*22)
            pos=nx.spring_layout(sub,seed=5419,iterations=160,scale=scale)
            for nid,p in pos.items():out[nid]=(float(p[0])+k*2200,float(p[1]))
        return out,'NetworkX '+nx.__version__+' spring layout; seed5419; visual only'
    except ImportError:
        return {n['Id']:((i%8)*170,-(i//8)*170) for i,n in enumerate(nodes)},'standard-library grid fallback'

COLORS={'Person':(213,94,0),'Expedition':(0,114,178),'Institution':(0,158,115),'Government':(117,83,153),
 'Object':(163,120,39),'Collection':(191,160,80),'Work':(166,66,146),'Representation':(224,132,172),'Event':(126,142,153)}
NUMERIC={'YearStart','YearEnd','EventCount','ReviewRequired'}
def export_gexf(path,nodes,edges,layout,description):
    root=ET.Element(f'{{{G}}}gexf',version='1.2')
    meta=ET.SubElement(root,f'{{{G}}}meta',lastmodifieddate='2026-10-13')
    ET.SubElement(meta,f'{{{G}}}creator').text='HY5419 workbook-to-Gephi conversion'
    ET.SubElement(meta,f'{{{G}}}description').text=description
    graph=ET.SubElement(root,f'{{{G}}}graph',mode='static',defaultedgetype='directed')
    nkeys=[k for k in nodes[0] if k not in ['Id','Label']]
    ekeys=[k for k in edges[0] if k not in ['Id','Label','Source','Target','Type','Weight']]
    for cls,keys in [('node',nkeys),('edge',ekeys)]:
        decl=ET.SubElement(graph,f'{{{G}}}attributes',**{'class':cls,'mode':'static'})
        for k in keys:ET.SubElement(decl,f'{{{G}}}attribute',id=k,title=k,type='integer' if k in NUMERIC else 'string')
    ns=ET.SubElement(graph,f'{{{G}}}nodes')
    for n in nodes:
        el=ET.SubElement(ns,f'{{{G}}}node',id=n['Id'],label=n['Label'])
        values=ET.SubElement(el,f'{{{G}}}attvalues')
        for k in nkeys:
            if n[k]!='':ET.SubElement(values,f'{{{G}}}attvalue',**{'for':k,'value':str(n[k])})
        color=COLORS.get(n['NodeType'],(120,120,120))
        if n['EpistemicStatus']=='reported_intention':color=(225,159,0)
        if n['RecordStatus']=='待核验':color=(155,155,155)
        ET.SubElement(el,f'{{{V}}}color',r=str(color[0]),g=str(color[1]),b=str(color[2]),a='1.0')
        size=10 if n['NodeType']=='Event' else 15 if n['NodeType'] in ['Collection','Object','Work','Representation'] else 19
        ET.SubElement(el,f'{{{V}}}size',value=str(size))
        x,y=layout[n['Id']];ET.SubElement(el,f'{{{V}}}position',x=str(x),y=str(y),z='0')
    es=ET.SubElement(graph,f'{{{G}}}edges')
    for e in edges:
        el=ET.SubElement(es,f'{{{G}}}edge',id=e['Id'],source=e['Source'],target=e['Target'],type='directed',weight='1',label=e['Label'])
        values=ET.SubElement(el,f'{{{G}}}attvalues')
        for k in ekeys:
            if e[k]!='':ET.SubElement(values,f'{{{G}}}attvalue',**{'for':k,'value':str(e[k])})
    ET.indent(root,space='  ');ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def check_graph(path,nodes,edges,allowed):
    assert len({n['Id'] for n in nodes})==len(nodes)
    assert len({e['Id'] for e in edges})==len(edges)
    ids={n['Id'] for n in nodes}
    for e in edges:
        assert e['Source'] in ids and e['Target'] in ids and e['Source']!=e['Target']
        assert e['EventId'] in allowed and e['Weight']==1
    assert len({(e['Source'],e['Target']) for e in edges})==len(edges),'Unexpected parallel adjacency'
    doc=ET.parse(path);nn=doc.findall(f'.//{{{G}}}node');ee=doc.findall(f'.//{{{G}}}edge')
    assert {n.get('id') for n in nn}==ids
    assert {(e.get('id'),e.get('source'),e.get('target')) for e in ee}=={(e['Id'],e['Source'],e['Target']) for e in edges}
    assert len(nn)==len(nodes) and len(ee)==len(edges)
    try:
        import networkx as nx
        g=nx.read_gexf(path)
        assert g.is_directed() and not g.is_multigraph()
        assert g.number_of_nodes()==len(nodes) and g.number_of_edges()==len(edges)
        components=nx.number_weakly_connected_components(g);parser='NetworkX '+nx.__version__
    except ImportError:components=None;parser='ElementTree structural verification only'
    return {'nodes':len(nodes),'association_edges':len(edges),'event_records':len(allowed),
            'node_type_counts':dict(Counter(n['NodeType'] for n in nodes)),
            'weak_components':components,'independent_parser':parser,'status':'passed'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workbook',type=Path,default=DEFAULT_WORKBOOK)
    ap.add_argument('--output',type=Path,default=DEFAULT_OUT)
    ap.add_argument('--overwrite',action='store_true',help='Explicitly replace only previously generated outputs in this directory.')
    args=ap.parse_args();workbook=args.workbook.resolve();out=args.output.resolve()
    if out.exists() and any(out.iterdir()) and not args.overwrite:raise SystemExit('Output exists; choose another output path or pass --overwrite after review.')
    input_hash=digest(workbook)
    data,reading,events,entities,sources,objects,works,reps=load_contract(workbook)
    allowed={eid for eid,e in events.items() if e['核验状态']=='可整理事件'}
    review={eid for eid,e in events.items() if e['核验状态'] not in ['排除','背景／方法','仅线索']}
    definitions=[('',allowed,'双层传播网络.gexf'),
      ('实物流转层',{eid for eid in allowed if events[eid]['网络层']=='实物流转'},'实物流转层.gexf'),
      ('知识传播层',{eid for eid in allowed if events[eid]['网络层']=='知识传播'},'知识传播层.gexf'),
      ('含待核记录',review,'双层传播网络_含待核.gexf')]
    report={'input_workbook':str(workbook),'input_sha256':input_hash,'date':'2026-10-13',
       'graph_model':'entity-event-object-work incidence; arrows have typed relations, not all physical transfers',
       'status_policy':'main=可整理事件; review additionally includes待核验; intention retained as intention',
       'main_event_ids':sorted(allowed),'review_event_ids':sorted(review),'graphs':{},'GephiGUIImport':'not_exercised'}
    out.mkdir(parents=True,exist_ok=True)
    outputs=[]
    for subdir,ids,filename in definitions:
        if not ids:continue
        folder=out/subdir;folder.mkdir(exist_ok=True)
        nodes,edges=build_view(ids,data,reading,events,entities,objects,works,reps)
        pos,method=positions(nodes,edges)
        gf=folder/filename
        export_gexf(gf,nodes,edges,pos,'HY5419 two-layer event-centred graph; 1900–1910; static; unit-weight associations; scope and uncertainty in attributes.')
        write_csv(folder/'nodes.csv',nodes);write_csv(folder/'edges.csv',edges)
        view=check_graph(gf,nodes,edges,ids);view['layout']=method;view['file']=str(gf.relative_to(out))
        report['graphs'][subdir or '主图']=view
        outputs.extend([gf,folder/'nodes.csv',folder/'edges.csv'])
    assert {e['EventId'] for e in build_view(allowed,data,reading,events,entities,objects,works,reps)[1]}==allowed
    main_edges=build_view(allowed,data,reading,events,entities,objects,works,reps)[1]
    assert all(e['ReviewRequired']==0 for e in main_edges)
    # Preserve the source and logic tables separately from Gephi edge lists.
    excluded=[{'EventId':eid,'Action':e['行为类型'],'Status':e['核验状态'],'Reason':e['尚未确认什么']} for eid,e in events.items() if eid not in allowed]
    write_csv(out/'主图未纳入记录.csv',excluded,['EventId','Action','Status','Reason'])
    for tab,filename in [('阅读记录','来源阅读记录.csv'),('事件整理','事件原始记录.csv'),('现有来源ID','来源目录.csv'),
       ('参与角色','参与角色原始记录.csv'),('对象与批次','对象原始记录.csv'),('作品与载体','作品原始记录.csv'),
       ('复制品登记','复制品原始记录.csv'),('现有主体ID','主体原始记录.csv')]:
        write_csv(out/filename,data[tab]);outputs.append(out/filename)
    outputs.append(out/'主图未纳入记录.csv')
    report['counts']={'reading_records':len(reading),'workbook_events':len(events),
      'main_events':len(allowed),'main_physical_events':sum(events[e]['网络层']=='实物流转' for e in allowed),
      'main_knowledge_records':sum(events[e]['网络层']=='知识传播' for e in allowed),
      'main_intention_records':sum('意向' in events[e]['行为类型'] for e in allowed),'review_only_events':len(review-allowed)}
    assert digest(workbook)==input_hash,'Workbook changed during export; rerun against a saved snapshot.'
    report['status']='passed'
    report['conversion_rules']=[
      'one stable ID per entity/object/event/work/representation',
      'object -> event records a subject association',
      'transfer source -> physical event -> receiving institution/operation',
      'known participant -> event with explicit Role',
      'event -> work/representation records reported production, not necessarily publication or current availability',
      'missing actors remain blank; no synthetic unknown people or inferred co-occurrence edges',
      'source-group relationships and uncertain identifier equivalence are metadata only, not extra graph edges',
      'each node pair in each event appears once; duplicate participation annotations are merged at Weight1',
      'provenance sources and reading rows are not automatically early knowledge-network publication nodes',
      'YearStart/End remain uncertainty attributes; graph is static',
      'EventCount1 on association edges is a locator; do not sum it to estimate unique historical events']
    report['outputs']=[{'path':str(f.relative_to(out)),'sha256':digest(f)} for f in outputs]
    (out/'转换校验记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (out/'CONVERSION_SUCCESS.txt').write_text('Workbook and four graph views validated; '+input_hash+'\n',encoding='utf8')
    # Keep an exact converter copy for the local handoff; its defaults still point to this project.
    copy=out/'export_gephi.py'
    if copy.resolve()!=SCRIPT.resolve():shutil.copyfile(SCRIPT,copy)
    print(json.dumps({'status':'passed','graphs':report['graphs'],'counts':report['counts']},ensure_ascii=False))

if __name__=='__main__':main()
