# -*- coding: utf-8 -*-
"""Build an editable, evidence-linked Gephi review workbook. Originals are read-only."""
from pathlib import Path
from collections import defaultdict
import csv, datetime, hashlib, importlib.util, json, math, os, re, shutil, textwrap, unicodedata
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment
from content import EVIDENCE, PARTICIPANTS, EXTRA_ENTITIES, NEW_EVENTS, TASKS

ROOT=Path(__file__).resolve().parent
B=ROOT.parents[1]
PROJECT=B.parents[1]
G=PROJECT/'04_gephi/双层传播网络_Gephi'
OUT=B/'Gephi完善_文献证据与数据工作表.xlsx'
INDEX=json.loads((ROOT/'原文索引.json').read_text())
def read_csv(path):return list(csv.DictReader(path.open(encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s)).casefold()
def split(s):return [v for v in str(s or '').split(';') if v]
def rel(p):return os.path.relpath(p,B)

raw={n:read_csv(G/n) for n in ['事件原始记录.csv','主体原始记录.csv','参与角色原始记录.csv','对象原始记录.csv','复制品原始记录.csv','作品原始记录.csv','来源目录.csv']}
base_nodes=read_csv(G/'英文标签版/nodes.csv');base_edges=read_csv(G/'英文标签版/edges.csv')
all_nodes=read_csv(G/'英文标签版/含待核记录/nodes.csv');all_edges=read_csv(G/'英文标签版/含待核记录/edges.csv')
in_nodes={r['Id'] for r in base_nodes};in_edges={r['Id'] for r in base_edges}
assert (len(base_nodes),len(base_edges),len(all_nodes),len(all_edges))==(46,57,52,63)
inputs={str(p.relative_to(PROJECT)):sha(p) for p in [G/'英文标签版/nodes.csv',G/'英文标签版/edges.csv',G/'英文标签版/含待核记录/nodes.csv',G/'英文标签版/含待核记录/edges.csv',*(G/n for n in raw)]}
inputs[str((PROJECT/'路线地图/敦煌项目_路线地图资料与制作指南.xlsx').relative_to(PROJECT))]=sha(PROJECT/'路线地图/敦煌项目_路线地图资料与制作指南.xlsx')
original_workbook=PROJECT/'06_notes/2026-10-13_双层传播网络补采集/整理版_2026-10-13/双层传播网络_中文记录工作簿_整理版.xlsx'
inputs[str(original_workbook.relative_to(PROJECT))]=sha(original_workbook)

evidence_by={x['id']:x for x in EVIDENCE}
anchor_checks=[]
for e in EVIDENCE:
    source=INDEX[e['source']]
    assert sha(Path(source['file']))==source['sha256'],e['source']
    text='\n'.join(source['pages'][p-1] for p in e['pages']) if e['pages'] else source['text']
    assert norm(e['anchor']) in norm(text),(e['id'],e['source'],e['anchor'])
    e['file']=source['file'];e['source_sha256']=source['sha256']
    anchor_checks.append(dict(EvidenceID=e['id'],SourceID=e['source'],pages=e['pages'],anchor_found=True))

# Literature IDs remain separate from the older Sxx and map Rxx namespaces.
source_alias={'L01':'S01;S02','L02':'S03','L03':'S19','L08':'S17','G07':'R04','G08':'R01'}
literature=read_csv(B/'02_阅读说明与网页全文/阅读清单.csv')
lit_rows=[]
for l in literature:
    sid=l['文献ID'];available=sid in INDEX;f=Path(INDEX[sid]['file']) if available else None
    role='方法' if sid in ['G01','G02','G03','G04','G05'] else '历史／对象研究'
    state='重点段落已复核' if any(e['source']==sid for e in EVIDENCE) else ('正文可用，非本轮重点' if available else '未取得正文，不建边')
    lit_rows.append([sid,l['作者'],int(l['年份']) if l['年份'].isdigit() else l['年份'],l['题名'],role,state,l['先读位置'],source_alias.get(sid,''),l['限制与待核'],rel(f) if f else '',l['官方入口'],
        'https://nus.summon.serialssolutions.com/search?s.q='+__import__('urllib.parse',fromlist=['quote']).quote(l['题名'])])
lit_rows.append(['WEB_BNF','Bibliothèque nationale de France',None,'Manuscrits du Monde – Asie - Océanie：Dunhuang收藏段','机构校验','指定段落已复核','Le fonds des manuscrits de Dunhuang','与旧S15对读','无出版年；2026-10-28为核查日，不是事件日。机构叙述不替代入藏凭证。',rel(Path(INDEX['WEB_BNF']['file'])),'https://www.bnf.fr/fr/manuscrits-du-monde-asie-oceanie',''])

event_raw={r['事件ID']:r for r in raw['事件原始记录.csv']}
event_evidence={
 'DH001':'EV001;EV003;EV043','DH002':'EV001;EV003','DH003':'EV003;EV040;EV041;EV042','DH004':'EV011;EV015','DH005':'EV001','DH006':'EV044','DH007':'EV029',
 'DH008':'EV029;EV032','DH009':'EV029;EV030;EV031','KE001':'EV008','KE002':'EV006;EV007','KE003':'EV008','KE004':'EV009','KE005':'EV010;EV015;EV016',
 'KE006':'EV011','KE007':'EV012','KE008':'EV012;EV013','PE001':'EV014','KE009':'EV017;EV019','KE010':'EV033;EV034'}
event_proposals={
 'DH004':('1909年8月转入英国博物馆地下室（研究叙述）','month_from_secondary','原范围可细化为存放阶段；不改成抵英／正式入藏日期'),
 'DH006':('1910年进入写本部（机构说明）；1909年底旧说待对读','conflicting_event_definitions','先分到巴黎、收存和写本部入藏；旧S15与本轮WEB_BNF指涉范围待核'),
 'KE007':('1910年检查语境；仍不定成稿月','year','W001与Or.13114/1 ff.37–44同一性未核；不据July 1910直接改日期'),
 'KE008':('1910年7月编目建议备忘录语境','month_from_secondary','附条件的计划；不是目录完成、款项已付或写本已送达'),
 'KE005':('1909年；工作起止日未定','year','补正式版L08印刷20/PDF13定位；与旧S17 AAM是同篇材料，范围继续待核'),
 'DH003':(event_raw['DH003']['原始日期与历法'],'month_conflicting_days','分赴敦煌／驮回／安西卸货；Hassan与Tila不同角色不互相替代')}
event_rows=[]
for eid,r in event_raw.items():
    node=next((n for n in all_nodes if n['Id']==eid),{})
    date,precision,note=event_proposals.get(eid,(r['原始日期与历法'],r['日期精度'],r['尚未确认什么']))
    decision='保留意向' if eid=='KE008' else '待复核'
    event_rows.append([eid,'','原有事件',node.get('FullLabelEn') or node.get('LabelEn') or eid,r['原始日期与历法'],date,precision,r['网络层'],r['对象／批次ObjectId'],event_evidence.get(eid,''),decision,note])
for eid,parent,zh,en,action,date,precision,year,evs,note in NEW_EVENTS:
    decision='暂不纳入' if year>1910 else '保留意向' if eid=='NEW_KA_PROMISE1907' else '待复核'
    event_rows.append([eid,parent,'地图已有／Gephi待并入' if eid.startswith('MAP_') else '建议新增（ID待采纳）',en,'',date,precision,'知识传播' if eid!='PE001_F1911' else '两层关联','',evs,decision,zh+'；'+note])
steps=[
 ('DH001_S01','DH001','agreement','Agreement reached','1907-05-29','day_from_secondary','EV043','交易安排；支付完成日另核'),
 ('DH001_S02','DH001','retrieval','Night-time retrieval','1907-05-29夜至30日凌晨','night_range_from_secondary','EV043','同一取得过程，不将两趟取袋计两次取得'),
 ('DH003_S02','DH003','caravan_transport','Caravan journey','1907年9月底至10月初；路线日期据不同记录','range_from_secondary','EV042','Hassan参与外出驮运；实际每个停靠日不补齐'),
 ('DH003_S03','DH003','unloading','Unloading at Anxi','1907-10-04夜（10月5日日记回述）','day_from_secondary','EV041','Tila与Ibrahim卸货；保留日志日期差异')]
for sid,parent,action,en,date,precision,evs,note in steps:
    event_rows.append([parent,parent,'步骤，非独立EventID',en,'',date,precision,'实物流转','B0001' if parent=='DH001' else 'B0003',evs,'待复核','StepID='+sid+'；'+note])

# Build node records for review. InCurrentGraph records the baseline, not approval.
nodes={}
for n in all_nodes:
    eid=n.get('EventId') or (n['Id'] if n['NodeType']=='Event' else '')
    nodes[n['Id']]=dict(Id=n['Id'],Label=n['LabelEn'] or n['Label'],NodeType=n['NodeType'],LabelZH=n.get('FullLabelZh') or n.get('LabelZh') or n.get('FullLabel',''),Layer=n.get('LayerEn') or n.get('Layer',''),EventId=eid,ParentEventId='',InCurrentGraph=int(n['Id'] in in_nodes),ReviewDecision='原图暂保留' if n['Id'] in in_nodes else '待复核',EpistemicStatus=n.get('EpistemicStatus',''),EvidenceIds=event_evidence.get(eid,''),YearStart=n.get('YearStart',''),YearEnd=n.get('YearEnd',''),DatePrecision=n.get('DatePrecision',''),NotesZH=n.get('Notes',''))
for ident,zh,en,alias in PARTICIPANTS:
    assert ident not in nodes,ident
    nodes[ident]=dict(Id=ident,Label=en,NodeType='Person',LabelZH=zh,Layer='Knowledge transmission',EventId='',ParentEventId='',InCurrentGraph=0,ReviewDecision='待复核',EpistemicStatus='secondary_reported_attendee',EvidenceIds='EV018',YearStart='',YearEnd='',DatePrecision='',NotesZH='建议ID；原文称呼：'+alias+'；英文为展示工作标签，未另核权威库')
for ident,zh,en,typ,evs,note in EXTRA_ENTITIES:
    assert ident not in nodes,ident
    nodes[ident]=dict(Id=ident,Label=en,NodeType=typ,LabelZH=zh,Layer='Knowledge transmission',EventId='',ParentEventId='',InCurrentGraph=0,ReviewDecision='待复核',EpistemicStatus='research_candidate',EvidenceIds=evs,YearStart='',YearEnd='',DatePrecision='',NotesZH=note)
for eid,parent,zh,en,action,date,precision,year,evs,note in NEW_EVENTS:
    assert eid not in nodes,eid
    nodes[eid]=dict(Id=eid,Label=en,NodeType='Event',LabelZH=zh,Layer='Cross-layer' if eid=='PE001_F1911' else 'Knowledge transmission',EventId=eid,ParentEventId=parent,InCurrentGraph=0,ReviewDecision='暂不纳入' if year>1910 else '保留意向' if eid=='NEW_KA_PROMISE1907' else '待复核',EpistemicStatus='out_of_scope_followup' if year>1910 else 'research_interpretation' if eid=='NEW_KE_INTRO1909' else 'reported_intention' if eid=='NEW_KA_PROMISE1907' else 'secondary_reported_activity',EvidenceIds=evs,YearStart=year,YearEnd=year,DatePrecision=precision,NotesZH=note)
nodes['KE008']['ReviewDecision']='保留意向'
for eid in ['DH004','DH006','KE007','KE008','KE005','KE002','PE001']:
    nodes[eid]['NotesZH']=event_proposals.get(eid,('','',''))[2] or nodes[eid]['NotesZH']
    if eid in event_proposals:nodes[eid]['DatePrecision']=event_proposals[eid][1]
nodes['DH004']['YearStart']=nodes['DH004']['YearEnd']=1909

roles=[]
for r in raw['参与角色原始记录.csv']:
    role=r['具体角色'];evs=event_evidence.get(r['事件ID'],'');step='';note=r['限制']
    if r['参与记录ID']=='P009':role='unloader_at_Anxi（建议细化）';evs='EV041';step='DH003_S03';note+=' 本文支持安西卸货，不据此指派赴敦煌驮运。'
    if r['参与记录ID']=='P008':evs='EV041;EV042';step='DH003_S02;DH003_S03';note+=' 区分驮运和安西卸货。'
    roles.append([r['参与记录ID'],r['事件ID'],step,r['主体ID'],role,evs,r['来源ID'],r['定位'],'原有待细化' if r['参与记录ID'] in ['P008','P009'] else '原有记录','待复核',note])

edges=[]
for e in all_edges:
    eid=e['EventId'];note=e['Notes'];role=e['Role']
    if e['Source']=='N016' and eid=='DH003':role='unloader_at_Anxi';note='建议把原transport_assistant细化为安西卸货；赴敦煌驮运另有Hassan记录。'
    if e['Source']=='N015' and eid=='DH003':role='carrier;unloader_at_Anxi';note='两个步骤在同一父事件中；按ActorID–EventID去重后再分析。'
    edges.append(dict(Id=e['Id'],Source=e['Source'],Target=e['Target'],Type=e['Type'],Weight=float(e['Weight']),Label=e['Label'],Relation=e['Relation'],Role=role,Layer=e.get('LayerEn') or e['Layer'],EventId=eid,InCurrentGraph=int(e['Id'] in in_edges),ReviewDecision='保留意向' if eid=='KE008' else '原图暂保留' if e['Id'] in in_edges else '待复核',EpistemicStatus=e['EpistemicStatus'],EvidenceIds=event_evidence.get(eid,''),SourceRef=e['SourceRef'],YearStart=1909 if eid=='DH004' else e['YearStart'],YearEnd=1909 if eid=='DH004' else e['YearEnd'],DatePrecision=event_proposals[eid][1] if eid in event_proposals else e['DatePrecision'],NotesZH=note))
new_edge_keys=set()
def edge(source,target,eid,relation,role,evs,label,status='secondary_reported_activity',note=''):
    assert source in nodes and target in nodes,(source,target)
    key=(source,target,relation,eid)
    assert key not in new_edge_keys,key
    new_edge_keys.add(key)
    sources=';'.join(dict.fromkeys(evidence_by[x]['source'] for x in split(evs)))
    en=nodes.get(eid,{})
    edges.append(dict(Id='NEW_E_%s_%s_%s_%s'%(eid,source,target,relation),Source=source,Target=target,Type='Directed',Weight=1,Label=label,Relation=relation,Role=role,Layer=en.get('Layer','Knowledge transmission'),EventId=eid,InCurrentGraph=0,ReviewDecision='暂不纳入' if status=='out_of_scope_followup' else '保留意向' if status=='reported_intention' else '待复核',EpistemicStatus=status,EvidenceIds=evs,SourceRef=sources,YearStart=en.get('YearStart',''),YearEnd=en.get('YearEnd',''),DatePrecision=en.get('DatePrecision',''),NotesZH=note))
def participate(actor,eid,role,evs,label='Participant',status='secondary_reported_activity',note='',step=''):
    edge(actor,eid,eid,'participant_in_event',role,evs,label,status,note)
    refs=';'.join(dict.fromkeys(evidence_by[k]['source'] for k in split(evs)))
    roles.append(['NEW_P_%s_%s'%(eid,actor),eid,step,actor,role,evs,refs,'见02_文献证据','建议新增','暂不纳入' if status=='out_of_scope_followup' else '待复核',note])
for actor in ['N012']+[p[0] for p in PARTICIPANTS]:
    extra=actor in ['N022','N027']
    participate(actor,'MAP_KE011','attendee;organizer_attributed' if extra else 'attendee','EV018;EV020' if extra else 'EV018','Attendee / organiser (attributed)' if extra else 'Attendee',note='赴宴由名单支持；组织角色为研究解释。' if extra else '名录是18人下限；不据同场共现创建两两通信。')
participate('N035','MAP_KE011','organizer_attributed_not_attendee','EV020','Organiser (attributed)','research_interpretation','论文明确未出席；不得纳入到场者投影。')
def communication(eid,sender,recipient,evs,note=''):
    participate(sender,eid,'sender',evs,'Sender',note=note)
    edge(eid,recipient,eid,'addressed_to','addressed_recipient',evs,'Addressed to',note='目的对象不等于已收讫。'+note)
    refs=';'.join(dict.fromkeys(evidence_by[k]['source'] for k in split(evs)))
    roles.append(['NEW_P_%s_%s_TO'%(eid,recipient),eid,'',recipient,'addressed_recipient',evs,refs,'见02_文献证据','建议新增','待复核','实际收到日期未知。'+note])
communication('MAP_KE012','N011','N010','EV021','电文兰州制台按机构登记，不强指某位总督本人。')
communication('DH003_K01','N005','N002','EV040','日期与Jan-pao归属为推定；未新增具名信使边。')
communication('NEW_KA01','N037','N036','EV023;EV025','同一申报报道链；未取得原电。')
communication('NEW_KA02','N036','N038','EV023;EV025','发出日仅有1907-05-20之前的界限。')
communication('NEW_KA03','N038','N039','EV023;EV024','报道说已照会；没有执行止挖证据。')
participate('N043','NEW_KP01','publisher','EV023;EV025','Publisher')
edge('NEW_KP01','W007','NEW_KP01','produces_work','published_report','EV023;EV025','Published report')
participate('N035','NEW_KP02','credited_author','EV026','Credited author')
edge('NEW_KP02','R0003','NEW_KP02','produces_representation','periodical_version','EV026','Periodical version')
edge('R0003','W005','NEW_KP02','represents_work','text_version','EV026','Version of work',status='research_interpretation',note='与小册子是否同文本待核，工作层对应为候选。')
edge('MAP_KE011','R0002','MAP_KE011','circulates_representation','pamphlet_circulation','EV020','Pamphlet circulated',note='研究记散发；不自动连接每名参加者为收件人。')
edge('R0002','W005','MAP_KE011','represents_work','pamphlet_version','EV020;EV026','Version of work',status='research_interpretation',note='版本身份待核；不与期刊载体合并。')
participate('N041','NEW_KE_YE19100123','diarist','EV027','Diarist')
edge('NEW_KE_YE19100123','W006','NEW_KE_YE19100123','produces_work','diary_entry','EV027','Diary entry',note='没有从斯坦因到叶昌炽的直接告知边。')
participate('N042','DH003','carrier','EV042','Carrier',note='Hassan的外出驮运不替代Tila的安西卸货。',step='DH003_S02')
participate('N040','KE005','employing_institution','EV015','Employing institution',note='工作对象仍为范围未限定Stein finds；雇用机构不等于房址。')
edge('KE008','W004','KE008','proposal_recorded_in','proposal_document','EV012;EV013','Proposal memorandum',status='reported_intention',note='与W001身份待核；同一备忘录不重复当成两个已完成工作。')
participate('N012','PE001_F1911','reported_recipient','EV014','Reported recipient','out_of_scope_followup','1911范围外；与PE001是否同批待核。')
edge('B0011','PE001_F1911','PE001_F1911','subject_of_event','candidate_batch_identity','EV014','Candidate batch','out_of_scope_followup','批次同一性仍待核；不据编号范围把每件对象加入。')

# Harmonise synonyms for the same layer before partitioning in Gephi.
for rec in list(nodes.values())+edges:
    old_layer=rec['Layer']
    parts={v.strip() for v in old_layer.split(';') if v.strip()}
    if len(parts)>1 or any(v.startswith('Cross-layer') for v in parts):rec['Layer']='Cross-layer'
    elif old_layer=='Knowledge dissemination':rec['Layer']='Knowledge transmission'
    assert rec['Layer'] in ['Physical circulation','Knowledge transmission','Cross-layer'],(rec['Id'],rec['Layer'])

# Existing objects retain their uncertainty; modern holding claims are not inferred from routes.
object_rows=[]
for o in raw['对象原始记录.csv']:
    evs={'B0008':'EV006;EV007;EV008','O0001':'EV009','B0009':'EV015;EV016','B0011':'EV014','B0006':'EV029','B0007':'EV029;EV030;EV031','B0012':'EV017'}.get(o['ObjectId'],'')
    object_rows.append([o['ObjectId'],o['对象单位'],o['工作名称'],o['馆藏号／旧号（含限定）'],o['关联集合（非逐件已核）'],o['范围与身份说明'],o['来源ID'],evs,'原有记录／待复核',o['待核问题']])
for o in raw['复制品原始记录.csv']:
    object_rows.append([o['RepresentationId'],'Representation',o['类型与单位'],o['现存编号／文件'],o['来源对象组'],o['日期依据'],o['来源ID'],'EV033;EV034','原有记录／待复核',o['对应状态与待核问题']])
for o in raw['作品原始记录.csv']:
    oid=o['WorkId'];evs={'W001':'EV012','W002':'EV008','W003':'EV009'}[oid]
    object_rows.append([oid,o['载体类型'],o['题名（工作命名须注明）'],'','',o['原始日期／日期依据'],o['证据来源ID'],evs,'原有记录／待复核',o['获取与核验状态']+(' 与W004是否同一文件待核。' if oid=='W001' else '')])
for ident,zh,en,typ,evs,note in EXTRA_ENTITIES:
    if typ in ['Work','Representation']:object_rows.append([ident,typ,zh,'Or.13114/1 ff.37–44' if ident=='W004' else '', 'W005' if ident in ['R0002','R0003'] else '', '', ';'.join(dict.fromkeys(evidence_by[k]['source'] for k in split(evs))),evs,'建议新增／待核',note])

gap_rows=[
 ['GAP01','P0','W001 / W004同一性','KE007;KE008','EV012','Or.13114/1 ff.37–44原件／目录与Serindia所印memorandum对读','保留两个工作标识并标候选；不强改KE007为1910-07'],
 ['GAP02','P0','到巴黎、收存与入藏','DH006','EV044','核1909到巴黎记录与1910写本部接收／登记文件','旧日期与新阶段并列，不能择一当同一精确交接'],
 ['GAP03','P0','送寄与首批收件对应','PE001;PE001_F1911','EV014','核寄出信、箱单、1911-01-13收讫及退还','暂不合并批次；1911后续排除核心图'],
 ['GAP04','P0','续交原解委员身份','DH009','EV030;EV031','何彦升说与傅宝书说对读原文书、签收及当事人信札','不按两篇文献多数表决，不新建具名交出边'],
 ['GAP05','P1','信使姓名与发送日期','DH003_K01','EV040','核Jan-pao雇用／雇马账目与实际信件','未具名角色先留空，日期另标推定'],
 ['GAP06','P1','实际承运与卸货','DH003','EV041;EV042','对读9月29日外出队、10月4日晚卸货与10月5日日记','Hassan与Tila分主体、分步骤'],
 ['GAP07','P1','编号者与编号形成日期','KE002','EV007;EV010','原卷手迹、MSS Stein日记及拆箱清单','编号者推断与摄影日期分开'],
 ['GAP08','P1','索引原件与覆盖范围','KE003;W002','EV008','查箱91、1318索引清单及后续目录','未取得实物不等于清单从未存在；不按1318新增取得'],
 ['GAP09','P1','Andrews整理对象范围','KE005','EV015;EV016','核India Office Library雇用、拆箱清单与材料语种','保留Stein finds范围，不补绘幡所有权链'],
 ['GAP10','P1','宴会人数与具名下限','MAP_KE011','EV017;EV018;EV020','对照江瀚、恽毓鼎日记和回忆','18是具名下限；罗振玉是组织归因而非到场'],
 ['GAP11','P1','照片／小册子／期刊版身份','R0001;R0002;R0003;W005','EV020;EV026;EV033;EV034','逐张／逐版核原卷、底片号、版次、页码和文字差异','不因题名相似或同场即视为同一载体或人人收件'],
 ['GAP12','P1','个人获知的来源','NEW_KE_YE19100123','EV027','核叶昌炽日记原页和相关来访、赠书记录','不臆定斯坦因或伯希和直接向叶传递'],
 ['GAP13','P1','电报收讫与命令执行','MAP_KE012;NEW_KA03','EV021;EV024','查收电簿、后续公文、承运与接收记录','发出、收讫、执行、实物移动各自有日期'],
 ['GAP14','P2','Lorimer正文','G06','','优先NUS题名／DOI检索，取得正文后核工作年份','未取得正文，不根据摘要补参与边'],
 ['GAP15','P2','Conserving Limitless Life正文','G10','','优先NUS及OA官方入口，第1章53、64页目录线索','尚未读正文，不按目录补编目行为'],
 ['GAP16','P2','Cabos摄影研究正文','L06','','优先NUS／SOAS作者仓储，核拍摄、照片和后续传播的日期','未取得正文，不补Nouette拍某一具体写卷的边']]

analysis_rows=[
 ['AN01','分析','二模参与图','Actor–event affiliation','Person／Institution／Expedition／Government／PublicationOrganisation与Event分类型；排除Work、Representation、Collection','先按ActorID–EventID去重；含角色的方向另保留','EV035;EV036','描述被本语料记录的参与结构，不直接判定权力'],
 ['AN02','分析','到场者投影','Attendee co-participation','MAP_KE011只用attendee角色；不把organizer_not_attendee当到场','18名具名者投影可产生153对共参与，均非直接通信','EV018;EV020;EV037','投影边名须写co-attendance；没有通讯频率含义'],
 ['AN03','分析','人物参与次数','Distinct event participation','在明确类型与时间子图中统计不同EventID','一个父取得的多个StepID不得变成多次取得计数','EV035;EV036;EV043','不按角色条数或证据篇数重复增权'],
 ['AN04','分析','中介与角色比较','Brokerage and role diversity','分物质参与、知识处理和通信；先看蒋、信使、承运、整理者的不同动作','若计算中介中心性，先定义方向、连通性和纳入状态','EV003;EV039;EV041;EV042','中心性受史料覆盖影响，不能单独推断历史因果'],
 ['AN05','分析','敏感性比较','Evidence sensitivity','分别比较已报告活动、加入推断、加入意向的视图','KE002推断、KE008计划、1911后续不混作同类事实','EV007;EV013;EV014;EV038','报告节点／边纳入规则；不宣称漏记关系不存在'],
 ['AN06','分析','独立事件计数','Distinct historical actions','按EventID与ParentEventID及事件定义计数','57条旧边不是57次转移；不可求和重复EventCount','EV035;EV043','行政通信、宴会、发表和取得分别计量'],
 ['WEB01','网页','英文标签','Label / LabelZH','06表Label为英文；LabelZH用于中英切换','图例、人物详情、事件说明同步切换','EV038','拼音是工作标签；原文异名保留，不因异名拆人'],
 ['WEB02','网页','网络与地图连接','EventId / ParentEventId','MAP_KE011、MAP_KE012直接复用；DH003_K01关联父DH003','网络布局坐标与地理经纬度分开','EV021;EV038;EV040','地图端点直连不是历史道路；人物不强设终身固定地点'],
 ['WEB03','网页','悬停证据卡','EvidenceIds → 02 → 01','显示动作、日期精度、角色、来源定位和未决项','由证据表关联来源URL；原文支持与推断分开显示','EV035;EV038','不只展示节点大小和颜色；用户能回到原文'],
 ['WEB04','网页','范围开关','Core / Follow-up / Intention','核心1900–1910；PE001_F1911作为后续单独开关','KE008保留计划标签，不播放成完成编目','EV013;EV014','现藏机构bl/bnf/nlc与历史N007/N014/N009分开'],
 ['WEB05','网页','作品与载体','ObjectId / WorkId / RepresentationId','R0001照片组、R0002小册子、R0003期刊版分别显示','未核图像可显示有文字记录、影像待取','EV033;EV034','不伪造写卷图片，不把画作当写本'],
 ['WEB06','网页','Gephi成果接入','Stable NodeID / filtered exports','先审核本表，再从Gephi导出英文图及对应节点／边快照','先可嵌入静态矢量成果，交互数据仍需和本工作簿版本一致','EV038','本次仅准备数据，未替换既有Gephi或网页成果']]

dictionary=[
 ['EventId','事件ID','文本，沿用旧ID或MAP ID','DH003；MAP_KE011','同一事件不同文献证据复用ID；新建议ID待采纳'],
 ['StepId','动作步骤ID','父事件下的动作','DH003_S03','步骤非独立取得；04表步骤行的EventID仍填父事件'],
 ['ParentEventId','父事件ID','空或已有事件ID','DH003','可连接子事件，但不能据父子关系推断多次取得'],
 ['Id / Source / Target','Gephi标识与端点','文本，区分大小写','N012 → MAP_KE011','稳定ID；不得因英文拼写变化重新发号'],
 ['Label / LabelZH','双语显示名称','英文／中文','Paul Pelliot／伯希和','Label默认英文，别名与原词留在备注／文献'],
 ['NodeType','节点类型','Person, Event, Collection, Object, Work, Representation, Institution, Government, Expedition, PublicationOrganisation','Person','文化材料、事件与主体不混作同类节点；报刊机构与单篇报道分开'],
 ['Layer','网络层','Physical circulation / Knowledge transmission / Cross-layer','Knowledge transmission','统一旧Knowledge dissemination与新transmission；跨层主体合并为Cross-layer，原值仍见未修改的原CSV'],
 ['InCurrentGraph','本轮原主图标志','0或1','1','只说明旧46节点／57边是否出现，不是新数据的批准标志'],
 ['ReviewDecision','审核决定','原图暂保留／待复核／同意纳入／保留意向／暂不纳入','待复核','新关系不默认批准；导出前复制审核通过的可见记录到新表'],
 ['EpistemicStatus','认识／活动状态','reported_activity / research_interpretation / reported_intention / out_of_scope_followup','reported_intention','与处理状态、来源类型分开；有条件计划不是完成活动'],
 ['EvidenceIds','本表证据索引','分号分隔EV编号','EV017;EV018','每一编号指02中的一条主张—来源关系'],
 ['SourceRef','来源ID命名空间','旧Sxx／地图Rxx／阅读文献ID','S03；G13b；R04','12表对照；同文版本和同源原档不重复当独立证据'],
 ['DatePrecision','日期精度','day_from_secondary / month_from_secondary / before_date / year / day_inferred','before_date','报道称日前，不填精确发电日；证据界限不是持续时间'],
 ['YearStart / YearEnd','筛选年界','数值或空','1909 / 1910','用于范围筛选；不代表全年持续活动。不得以1月1日假造精确日期'],
 ['OriginalDate / SourceDate','活动日期与记述日期','分别记录历法与来源','10月4日晚行动／10月5日日记','现代论文出版年不是历史活动年；不擅自换算农历'],
 ['Relation','边类型','participant_in_event, addressed_to, subject_of_event, produces_work, produces_representation, represents_work','addressed_to','目的对象不等于已收讫；表示角色和材料关系，不都表示传播'],
 ['Role','具体角色','attendee, sender, addressed_recipient, carrier, unloader_at_Anxi, organizer_attributed_not_attendee','unloader_at_Anxi','同一主体同一事件多角色合并到一条边；角色证据仍可分别登记'],
 ['Weight','边权重','此审核快照统一为1','1','不是史料可靠度、箱数或卷数；投影时另定义共享事件权重'],
 ['SourceType / Basis','来源与本轮获取方式','研究转引／参与者记述／档案转录／机构回顾／方法文献','研究所引日记','原文已读不等于原档已核；译稿不作为另一条证据'],
 ['ObjectId','对象／集合','B批次或O单件等分析ID','B0003','批次不是馆藏号；未逐件匹配不能外推整批身份'],
 ['WorkId','逻辑作品／文本','W开头的工作ID','W005','同一题名不证明不同载体逐字相同'],
 ['RepresentationId','具体照片／摹本／刊载','R开头的工作ID','R0002','原物、照片、摹抄与印刷版本不等价'],
 ['Missing value','缺失信息','留空并记缺口','摄影者未核','空白不是0；不为未知收件人或未定位地点造精确值']]

# Resolve old source identities without rewriting legacy CSVs.
alias_to_lit={old:lit for lit,olds in source_alias.items() for old in split(olds)}
alias_rows=[]
for s in raw['来源目录.csv']:
    old=s['来源ID'];lit=alias_to_lit.get(old,'');f=None
    if lit in INDEX:f=Path(INDEX[lit]['file'])
    elif s['本地路径（相对项目）']:
        candidate=PROJECT/s['本地路径（相对项目）']
        if candidate.is_file():f=candidate
        else:
            found=list(PROJECT.rglob(candidate.name))
            if len(found)==1:f=found[0]
    alias_rows.append([old,lit,s['题名'],s['年份'],rel(f) if f else '',s['链接'],s['限制'],'同文AAM／正式版不独立计数' if old in ['S01','S02','S17'] else '旧来源保留，未在本轮重新全面审定'])
alias_rows.extend([['R04','G07','秦桦林2018宴会论文',2018,rel(Path(INDEX['G07']['file'])),'','与MAP_KE011/012同源','地图ID与阅读ID对照'],['R01','G08','王冀青2015安西流转研究',2015,rel(Path(INDEX['G08']['file'])),'','同一机构转载，不是新增独立原始材料','地图ID与阅读ID对照']])

wb=Workbook();wb.remove(wb.active)
wb.properties.title='Gephi完善：文献证据与数据工作表'
wb.properties.subject='1900–1910敦煌双层传播网络；证据审核与英文网页展示准备'
wb.properties.creator='HY5419 project'
wb.properties.description='Literature-linked review workbook; existing graphs and research workbooks unchanged.'
FONT='Arial Unicode MS';INK='253F39';TEAL='245B54';CREAM='F4EFE4';LINE='D8E0DB';BLUE='2453A1'
def lines_for(value,width):
    if value is None:return 1
    count=0
    for part in str(value).split('\n'):
        units=sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in part)
        count+=max(1,math.ceil(units/max(5,width-2)))
    return count
def make_sheet(name,title,subtitle,headers,rows,widths,machine=False):
    ws=wb.create_sheet(name);ws.sheet_view.showGridLines=False;ws.sheet_view.zoomScale=100
    top=1 if machine else 4;last=get_column_letter(len(headers))
    if not machine:
        ws.merge_cells('A1:'+last+'1');ws['A1']=title;ws['A1'].font=Font(name=FONT,size=16,bold=True,color=INK);ws.row_dimensions[1].height=31
        ws.merge_cells('A2:'+last+'2');ws['A2']=subtitle;ws['A2'].font=Font(name=FONT,size=11,color='626F66');ws['A2'].alignment=Alignment(vertical='center',wrap_text=True);ws.row_dimensions[2].height=34;ws.row_dimensions[3].height=9
    for j,(h,width) in enumerate(zip(headers,widths),1):ws.column_dimensions[get_column_letter(j)].width=width;ws.cell(top,j,h)
    for j in range(1,len(headers)+1):
        c=ws.cell(top,j);c.font=Font(name=FONT,size=11,bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor=TEAL);c.alignment=Alignment(wrap_text=True,vertical='center')
    ws.row_dimensions[top].height=43 if machine else 34
    for i,row in enumerate(rows,top+1):
        for j,value in enumerate(row,1):
            c=ws.cell(i,j,value)
            if isinstance(value,str) and value.startswith('='):c.data_type='s'
            c.font=Font(name=FONT,size=11,color=INK);c.alignment=Alignment(wrap_text=True,vertical='top');c.border=Border(bottom=Side(style='hair',color=LINE))
            if i%2==0:c.fill=PatternFill('solid',fgColor='F0F5F1')
        height=max(lines_for(v,w) for v,w in zip(row,widths))*15+13
        ws.row_dimensions[i].height=max(32,min(400,height))
    ws.freeze_panes='A'+str(top+1)
    if rows:
        table=Table(displayName='Table_'+str(len(wb.worksheets)).zfill(2),ref='A%d:%s%d'%(top,last,top+len(rows)));table.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=False);ws.add_table(table)
    ws.print_title_rows='1:'+str(top);ws.print_area='A1:'+last+str(top+len(rows));ws.sheet_properties.pageSetUpPr.fitToPage=False
    ws.page_setup.orientation='landscape';ws.page_setup.paperSize=ws.PAPERSIZE_A3;ws.page_setup.scale=100
    ws.oddFooter.center.text='HY5419 · 2026-10-28 · &P / &N';ws.oddFooter.center.size=10
    ws.sheet_properties.outlinePr.summaryRight=False
    ws._review_header=top;return ws
def link(cell,target,label=None):
    if not target:return
    if label is not None:cell.value=label
    cell.hyperlink=target;cell.font=Font(name=FONT,size=11,color=BLUE,underline='single')
def validation(ws,header,values):
    top=ws._review_header;heads=[ws.cell(top,j).value for j in range(1,ws.max_column+1)];idx=heads.index(header)+1
    d=DataValidation(type='list',formula1='"'+','.join(values)+'"',allow_blank=True);d.errorTitle='请选择列表值';d.error='请使用下拉列表；需要新增词表时先在字段字典说明。';d.showErrorMessage=True;d.errorStyle='stop';ws.add_data_validation(d);d.add('%s%d:%s%d'%(get_column_letter(idx),top+1,get_column_letter(idx),max(top+len(ws.tables)*0+1,ws.max_row+100)))
    for row in ws.iter_rows(min_row=top+1,min_col=idx,max_col=idx):row[0].font=Font(name=FONT,size=11,color=BLUE)
    rng='%s%d:%s%d'%(get_column_letter(idx),top+1,get_column_letter(idx),ws.max_row)
    for val,color in [('同意纳入','DBEBD9'),('待复核','FFF0C9'),('暂不纳入','E8E8E8'),('保留意向','E8DFF1')]:ws.conditional_formatting.add(rng,CellIsRule(operator='equal',formula=['"'+val+'"'],fill=PatternFill('solid',fgColor=color)))

navigation=[
 ['本次范围','20条待读文献＋1条BnF校验来源','只复核与网络修改有关的重点段落；3篇仍待正文','原英文PDF为证据；翻译版仅辅助阅读'],
 ['基线快照','46节点／57边；含待核版52节点／63边','原文件与原记录保持不变','本表包含候选，不是已审定的新Gephi数据'],
 ['1','03_优先修改','先处理P0任务，再填写审核决定与备注','优先核存放阶段、备忘录身份、1911后续及宴会名单'],
 ['2','02_文献证据','按EV编号回到具体页码／段落','一行是一条主张—来源关系，不按论文篇数增权'],
 ['3','04_事件修订；05_角色补充','保留EventID；步骤、日期和角色各自记录','宴会、查看、摄影、通信、取得不是同一动作'],
 ['4','06_Gephi_Nodes；07_Gephi_Edges','表头已用Gephi字段名，Label是英文','InCurrentGraph只说明旧主图出现，不代表新审核已通过'],
 ['5','审核后导出','将决定采纳的可见行复制到新空表，再另存UTF-8 CSV','仅在Excel筛选后直接另存CSV，可能仍包含隐藏行；不要整表直接导入'],
 ['6','10_分析与网页','审核后再用稳定NodeID、EventID、EvidenceID接入网页','现藏机构、地图位置和历史主体保留不同语义'],
 ['证据规则','意向／推断／范围外','KE008计划、KE002推断、1911收件分别标示','不把条件补成已完成，不因缺少资料就断言从未发生'],
 ['来源规则','同源／同文版本','L01=S01/S02；L08=S17；G07=R04；G08=R01','新文献重复引用同一日记、报刊，不等于独立证实'],
 ['数量规则','箱／捆／卷／件／照片／编号','数量与单位分开；原样本返还不新增计数','图中边数不等于实际运输或交易次数'],
 ['导出检查','边表端点必须存在于节点表','所选每条边的Source和Target都要在所选节点Id中','审核后建立新Gephi项目，保留旧版作对照'],
 ['本轮未做','没有回写既有研究或网页','本表是审核与补采集工作表；分析方法是建议','没有重新计算中心性，也没有把候选称为定稿网络']]
ws=make_sheet('00_开始使用','Gephi完善｜文献证据与数据工作表','2026-10-28 · 英文展示字段＋中文研究说明 · 可编辑审核表 · 数量是本次快照，不自动随编辑刷新',['步骤／主题','入口／范围','怎么用','重要边界'],navigation,[18,38,56,58])
for i,row in enumerate(navigation,5):
    target=row[1].split('；')[0]
    if target.startswith(('02_','03_','04_','06_','10_')):link(ws.cell(i,2),"#'%s'!A1"%target)

ws=make_sheet('01_文献核查','文献与本轮核查状态','正文可用≠全文逐页已读；17条本地正文中选读相关段落，3条待正文。中文／英文译稿不重复计来源。',['文献ID','作者','出版年','题名','用途类型','本轮状态','重点定位','旧ID／地图ID','限制与待核','本地原文','官方入口','NUS入口'],lit_rows,[15,25,12,48,18,26,38,20,52,36,18,18])
for i,row in enumerate(lit_rows,5):
    if row[9]:link(ws.cell(i,10),row[9])
    if row[10]:link(ws.cell(i,11),row[10],'官方入口 ↗')
    if row[11]:link(ws.cell(i,12),row[11],'NUS题名检索 ↗')
ev_rows=[[e['id'],e['source'],e['printed'],';'.join(map(str,e['pages'])) if e['pages'] else '网页定位',e['anchor'],e['claim'],e['status'],e['events'],e['limit'],e['dependency'],rel(Path(e['file']))] for e in EVIDENCE]
ws=make_sheet('02_文献证据','逐条证据｜原文定位与支持边界','证据转述不是逐字引文。原文关键词已经在指定页／本地正文中核对；研究转引不等于本轮见过原档。',['EvidenceID','文献ID','原刊／章内定位','原PDF页码','原文关键词','证据转述（非引文）','证据性质','关联事件／记录','不能支持什么','共同来源／依赖组','打开原文'],ev_rows,[15,13,23,15,27,56,24,30,54,34,28])
for i,e in enumerate(EVIDENCE,5):link(ws.cell(i,11),rel(Path(e['file'])),'原文：'+e['source'])
task_rows=[[tid,priority,title,where,evs,action,bound,'未处理',''] for tid,priority,title,where,evs,action,bound in TASKS]
ws=make_sheet('03_优先修改','先做这20项｜按证据推进','P0先处理；审核状态与用户备注可直接编辑。候选节点、边不会自动写回原Gephi文件。',['任务ID','优先级','修改事项','操作位置','依据EV／文献','建议操作','保留的限制','处理状态','用户备注'],task_rows,[13,12,33,28,22,53,48,18,32]);validation(ws,'处理状态',['未处理','进行中','已核可用','暂缓','不采用'])
ws=make_sheet('04_事件修订','事件修订与动作步骤','先保留父EventID；步骤行明确StepID且不生成独立取得。所有新增ID均为工作建议，MAP编号沿用已有地图记录。',['EventID','ParentEventID','记录类型','英文事件／步骤名','原记录日期','建议日期／证据界限','DatePrecision','网络层','对象／批次','EvidenceIDs','审核决定','具体说明'],event_rows,[18,18,25,39,36,43,27,18,18,26,18,58]);validation(ws,'审核决定',['待复核','同意纳入','保留意向','暂不纳入'])
ws=make_sheet('05_角色补充','主体参与｜角色、步骤与证据分开','原39条角色、旧来源与定位保留；EV是本轮补充或限定。新增为候选，多个角色不自动生成多条Actor–Event边。',['ParticipationID','EventID','StepID','ActorID','具体Role','本轮关联EV','SourceRef','原定位／本轮定位','记录来源','审核决定','限定与待核'],roles,[33,24,27,16,42,25,23,33,22,18,58]);validation(ws,'审核决定',['待复核','同意纳入','保留意向','暂不纳入'])
node_headers=['Id','Label','NodeType','LabelZH','Layer','EventId','ParentEventId','InCurrentGraph','ReviewDecision','EpistemicStatus','EvidenceIds','YearStart','YearEnd','DatePrecision','NotesZH']
for rec in list(nodes.values())+edges:
    for field in ['YearStart','YearEnd']:
        value=rec.get(field)
        if value not in ['',None]:
            assert str(value).isdigit(),(rec['Id'],field,value)
            rec[field]=int(value)
ws=make_sheet('06_Gephi_Nodes','','',node_headers,[[n.get(k,'') for k in node_headers] for n in nodes.values()],[21,38,22,35,28,24,23,19,21,34,27,14,14,29,62],machine=True);validation(ws,'ReviewDecision',['原图暂保留','待复核','同意纳入','保留意向','暂不纳入']);validation(ws,'Layer',['Physical circulation','Knowledge transmission','Cross-layer'])
edge_headers=['Id','Source','Target','Type','Weight','Label','Relation','Role','Layer','EventId','InCurrentGraph','ReviewDecision','EpistemicStatus','EvidenceIds','SourceRef','YearStart','YearEnd','DatePrecision','NotesZH']
ws=make_sheet('07_Gephi_Edges','','',edge_headers,[[e.get(k,'') for k in edge_headers] for e in edges],[38,23,24,15,11,30,33,44,26,24,19,21,33,27,24,14,14,30,60],machine=True);validation(ws,'ReviewDecision',['原图暂保留','待复核','同意纳入','保留意向','暂不纳入']);validation(ws,'Layer',['Physical circulation','Knowledge transmission','Cross-layer'])
ws=make_sheet('08_对象与载体','对象、作品和复制品','14条原对象、原照片组与原3份作品保留；新备忘录、刊载载体为候选。分析ID不是馆藏号。',['RecordID','对象／载体类型','工作名称','馆藏号／档号（含限定）','关联对象／作品','日期／单位与范围','旧SourceRef','EvidenceIDs','本轮状态','身份与对应边界'],object_rows,[18,29,47,45,26,47,22,28,26,66])
ws=make_sheet('09_缺口与争议','证据缺口｜明确下一步查什么','缺口保留在研究表，不能靠绘图补全。三个待正文文献保留NUS入口，未据摘要生成人物或事件边。',['GapID','优先级','待解决问题','关联ID','EvidenceIDs','下一份需要的材料','当前处理'],gap_rows,[14,12,32,36,27,66,70])
ws=make_sheet('10_分析与网页','分析子图与英文网页对接','方法文献只支持建模决策，不提供新的敦煌事实。本次没有重新计算网络指标或修改已发布网页。',['PlanID','用途','中文问题／字段','英文名称／字段','纳入规则／输入','怎样做／定义','EvidenceIDs','解释边界'],analysis_rows,[15,14,30,40,64,65,28,67])
ws=make_sheet('11_字段字典','字段与关系编码约定','缺失留空；状态、来源类型、证据依据各自记录。YearStart/End仅为年界筛选，不能当精确连续时长。',['字段','中文意义','允许值／定义','示例','使用边界'],dictionary,[38,30,70,45,78])
ws=make_sheet('12_旧源ID对照','旧来源与阅读／地图ID对照','保留旧Sxx与地图Rxx；路径能确认的给出当前原文。没有找到原件时留空，不用失效旧路径伪装已可读。',['旧来源ID','文献ID','旧来源题名','年份（原记录）','当前原文路径','来源入口','来源限制','本轮说明'],alias_rows,[16,15,56,20,52,18,70,44])
for i,row in enumerate(alias_rows,5):
    if row[4]:link(ws.cell(i,5),row[4])
    if str(row[5]).startswith('http'):link(ws.cell(i,6),row[5],'来源入口 ↗')

# Workbook-level audit — never depend on a visually plausible but broken link.
for ws in wb:
    for row in ws.iter_rows(min_row=ws._review_header+1):
        height=max(lines_for(c.value,ws.column_dimensions[c.column_letter].width) for c in row)*15+25
        ws.row_dimensions[row[0].row].height=max(32,min(400,height))
node_ids=set(nodes);assert len(node_ids)==len(nodes)
assert len({e['Id'] for e in edges})==len(edges)
assert all(e['Source'] in node_ids and e['Target'] in node_ids for e in edges)
assert sum(n['InCurrentGraph'] for n in nodes.values())==46
assert sum(e['InCurrentGraph'] for e in edges)==57
for rec in list(nodes.values())+edges:
    assert all(k in evidence_by for k in split(rec.get('EvidenceIds',''))),(rec.get('Id'),rec.get('EvidenceIds'))
assert len([e for e in edges if e['EventId']=='MAP_KE011' and 'attendee' in split(e['Role'])])==18
assert not any(e['Source']=='N035' and e['EventId']=='MAP_KE011' and 'attendee' in split(e['Role']) for e in edges)
assert not any(e['Relation']=='conceals_for' for e in edges)
assert all(e['Weight']==1 for e in edges)
assert all((e['Source'] in {'N011','MAP_KE012'} and e['Target'] in {'MAP_KE012','N010'}) for e in edges if e['EventId']=='MAP_KE012')
assert all(e['ReviewDecision']=='暂不纳入' for e in edges if e['EventId']=='PE001_F1911')
if OUT.exists():
    previous=ROOT/'工作簿核验.json'
    known=json.loads(previous.read_text()).get('sha256') if previous.exists() else None
    if sha(OUT)!=known:
        saved=OUT.with_name(OUT.stem+'_保留已有版本_'+sha(OUT)[:8]+'.xlsx')
        if not saved.exists():shutil.copy2(OUT,saved)
wb.save(OUT)
check=load_workbook(OUT,read_only=False,data_only=False)
formula_count=sum(c.data_type=='f' for s in check for row in s for c in row)
assert formula_count==0
assert not check._external_links
assert all(c.font.sz>=11 for s in check for row in s for c in row if c.value is not None)
assert all((PROJECT/f).exists() and sha(PROJECT/f)==h for f,h in inputs.items())
report=dict(path=str(OUT),sha256=sha(OUT),bytes=OUT.stat().st_size,sheets=[dict(name=s.title,rows=s.max_row,columns=s.max_column,tables=len(s.tables),freeze_panes=s.freeze_panes) for s in check],base_nodes=46,base_edges=57,review_nodes=len(nodes),review_edges=len(edges),evidence_claims=len(EVIDENCE),literature_records=20,supplementary_web_records=1,proposed_event_records=len(NEW_EVENTS),role_records=len(roles),formulas=0,calculation='不使用公式；数量为明确标注的快照，不需要公式重算',original_input_hashes_unchanged=True,anchor_checks=anchor_checks,native_open='待核',visual_acceptance='待核')
(ROOT/'工作簿核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'输入快照与哈希.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2))
(ROOT/'证据矩阵.json').write_text(json.dumps(EVIDENCE,ensure_ascii=False,indent=2))
(ROOT/'建议节点与边.json').write_text(json.dumps(dict(nodes=list(nodes.values()),edges=edges),ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['anchor_checks','sheets']},ensure_ascii=False,indent=2))
