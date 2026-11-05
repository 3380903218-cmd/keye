# -*- coding: utf-8 -*-
"""Adjudicate records into a usable network; retain limitations as attributes."""
from pathlib import Path
from collections import defaultdict
from copy import deepcopy
import csv,json,re,hashlib,os

ROOT=Path(__file__).resolve().parent;B=ROOT.parents[1];PROJECT=B.parents[1]
PREVIOUS=B/'03_来源与整理记录/Gephi完善整理_2026-10-28'
G=PROJECT/'04_gephi/双层传播网络_Gephi'
readcsv=lambda p:list(csv.DictReader(p.open(encoding='utf-8-sig')))
original=json.loads((PREVIOUS/'建议节点与边.json').read_text())
nodes={r['Id']:deepcopy(r) for r in original['nodes']};edges=deepcopy(original['edges'])
evidence={r['id']:deepcopy(r) for r in json.loads((PREVIOUS/'证据矩阵.json').read_text())}
raw_events={r['事件ID']:r for r in readcsv(G/'事件原始记录.csv')}
literature={r['文献ID']:r for r in readcsv(B/'02_阅读说明与网页全文/阅读清单.csv')}
legacy={r['来源ID']:r for r in readcsv(G/'来源目录.csv')}
index=json.loads((PREVIOUS/'原文索引.json').read_text())
aliases={'S01':'L01','S02':'L01','S03':'L02','S17':'L08','S19':'L03','R04':'G07','R01':'G08'}
split=lambda s:[v for v in str(s or '').split(';') if v]
uniq=lambda vals:list(dict.fromkeys(v for v in vals if v))
def srcs(vals):return ';'.join(uniq(aliases.get(s,s) for s in split(vals)))
def ev(n,sid,locator,claim,limit,file,anchor,status='研究正文明确记载'):
 ident='EV%03d'%n
 evidence[ident]=dict(id=ident,source=sid,printed=locator,pages=[],anchor=anchor,claim=claim,limit=limit,status=status,events='',dependency=sid,file=str(file),source_sha256=hashlib.sha256(file.read_bytes()).hexdigest())
 return ident
ev(45,'S07','印刷916；NII扫描0412','1908年7月蒋孝琬在和田进行初步列单，覆盖不足三分之一。','列单不是新取得；不把覆盖数当作全藏总数。',ROOT/'sources/S07_412_OCR.txt','July, 1908','参与者原书')
ev(46,'S07','印刷916–917；NII扫描0412–0413','伯希和伦敦检查后应斯坦因请求写备忘录；原书印出其摘文。','可确认文字记录存在；不强认其与Or.13114/1 ff.37–44完全同一。',ROOT/'sources/S07_413_OCR.txt','above-mentioned memorandum','参与者原书及所印摘文')
ev(47,'S07','印刷916；NII扫描0412','斯坦因记1910年秋将第一批写本送往巴黎供伯希和编目。','记录送寄，不将1911年收件日倒填为寄出日，也不表示编目完成。',ROOT/'sources/S07_412_OCR.txt','autumn of 1910','参与者原书')
ev(48,'S15','“Les documents rapportés…”段','考察带回材料于1909年底抵达巴黎，写本与艺术品分流。','巴黎抵达与1910年写本部入藏分阶段登记；不新增第二次取得。',ROOT/'sources/BNF_Monnet.txt','fin de 1909','机构署名说明')

events={}
for eid,r in raw_events.items():
 n=nodes[eid]
 events[eid]=dict(EventId=eid,Label=n['Label'],LabelZH=n['LabelZH'],Action=r['行为类型'],Layer=n['Layer'],DateText=r['原始日期与历法'],DatePrecision=r['日期精度'],YearStart=n['YearStart'],YearEnd=n['YearEnd'],Place=r['地点'],ObjectIds=r['对象／批次ObjectId'],SourceIds='',EvidenceIds=n['EvidenceIds'],ProcessState='Reported action',Scope='Dunhuang materials',NotesZH=r['尚未确认什么'],ParentEventId='')
new_event_labels={r['Id']:r for r in original['nodes'] if r['NodeType']=='Event' and r['Id'] not in events}
event_actions={'MAP_KE011':'scholarly_banquet','MAP_KE012':'administrative_telegram','DH003_K01':'purchase_proposal_letter','NEW_KA01':'administrative_report','NEW_KA02':'administrative_telegram','NEW_KA03':'diplomatic_note','NEW_KP01':'press_publication','NEW_KP02':'text_publication','NEW_KE_YE19100123':'recorded_awareness','NEW_KA_PROMISE1907':'promise_to_send'}
date_text={'MAP_KE011':'1909-10-04晚','MAP_KE012':'1909-10-05','DH003_K01':'1907-09-26（研究推定；信件发送日未直接见）','NEW_KA01':'1907年4月（研究叙述）；早于5月20日报道','NEW_KA02':'早于1907-05-20；确日不详','NEW_KA03':'早于1907-05-20；确日不详','NEW_KP01':'1907-05-20','NEW_KP02':'1909-11-07','NEW_KE_YE19100123':'1910-01-23','NEW_KA_PROMISE1907':'1907-03-13'}
for eid,action in event_actions.items():
 n=nodes[eid]
 events[eid]=dict(EventId=eid,Label=n['Label'],LabelZH=n['LabelZH'],Action=action,Layer=n['Layer'],DateText=date_text[eid],DatePrecision=n['DatePrecision'],YearStart=n['YearStart'],YearEnd=n['YearEnd'],Place='北京' if eid.startswith('MAP_') else '',ObjectIds='',SourceIds='',EvidenceIds=n['EvidenceIds'],ProcessState='Recorded promise' if eid=='NEW_KA_PROMISE1907' else 'Reported action',Scope='Dunhuang materials',NotesZH=n['NotesZH'],ParentEventId=n['ParentEventId'])

# Adopt actions supported in full text. Hypothetical attribution is kept out.
excluded=[]
exclude_events={'KE002':'编号实际存在，但“蒋孝琬写下这些号码”的手迹归属为推断；从默认人物参与图排除该归属。','PE001_F1911':'1911年收讫作为时间范围外后续保存；与1910送寄批次不强行逐件匹配。','NEW_KE_INTRO1909':'具体逐步引荐链尚无直接材料，未作为事实通信链纳入。'}
filtered=[]
for e in edges:
 eid=e['EventId']
 if eid in exclude_events:
  excluded.append(dict(RecordId=e['Id'],EventId=eid,What=nodes[eid]['LabelZH'],Reason=exclude_events[eid],EvidenceIds=e['EvidenceIds']));continue
 if e['Source']=='N035' and eid=='MAP_KE011' and 'organizer' in e['Role']:
  excluded.append(dict(RecordId=e['Id'],EventId=eid,What='罗振玉公宴组织者归因',Reason='论文综合回忆作出的角色解释；不混入到场者记录。其作者关系另有明确依据。',EvidenceIds=e['EvidenceIds']));continue
 if e['Relation']=='represents_work' and e['Target']=='W005':
  excluded.append(dict(RecordId=e['Id'],EventId=eid,What='小册子与期刊版共用同一逻辑作品',Reason='分别保存两个实际载体；未核全文同一性，不强行合并。',EvidenceIds=e['EvidenceIds']));continue
 if e['Target']=='W004':
  excluded.append(dict(RecordId=e['Id'],EventId=eid,What='提议备忘录与检查备忘录的文件对应',Reason='不重复建立可能相同的文件节点；提议这一历史动作本身已纳入。',EvidenceIds=e['EvidenceIds']));continue
 if e['Source']=='N040' and eid=='KE005':
  pass
 if e['Role'].startswith('attendee;'):e['Role']='attendee'
 filtered.append(e)
edges=filtered
for eid in exclude_events:events.pop(eid,None)

# Resolve old broad dates and definitions rather than forwarding a task list.
events['DH001'].update(DateText='1907-05-29至30日凌晨：协议及夜间取回',DatePrecision='day_range_from_secondary')
events['DH003'].update(DateText='1907年9月底至10月初；安西卸货见10月4日晚记录',DatePrecision='range_with_recorded_step',NotesZH='取得、赴敦煌驮运与安西卸货是同一父事件的不同步骤；Hassan与Tila分角色。')
events['DH004'].update(DateText='1909年8月：转存英国博物馆地下室',DatePrecision='month_from_secondary',YearStart=1909,YearEnd=1909,NotesZH='实际存放阶段；不是正式入藏日。',EvidenceIds='EV011;EV015')
events['DH006'].update(Label='Arrival of Pelliot expedition materials in Paris',LabelZH='伯希和考察材料抵达巴黎',Action='arrival_in_city',DateText='1909年底',DatePrecision='year_end',YearStart=1909,YearEnd=1909,Place='巴黎',EvidenceIds='EV048',NotesZH='把原复合事件拆成巴黎抵达与1910年写本部接收两个阶段。')
events['KE001'].update(EvidenceIds='EV045')
events['KE005'].update(Label='Andrews processes Stein finds',LabelZH='Andrews拆箱、分类与列单Stein材料',Scope='General Stein collection context',NotesZH='明确记录Stein finds的工作；未将全部对象等同敦煌写本，也不把雇用机构当作实际房址。',EvidenceIds='EV015;EV010')
events['KE007'].update(EvidenceIds='EV046',NotesZH='原书已印出备忘录摘文；与另见档号文件同一性不强认。')
events['KE008'].update(Label='Pelliot makes a conditional cataloguing proposal',LabelZH='伯希和提出附条件编目方案',Action='proposal_made',DateText='1910年7月（备忘录语境）',DatePrecision='month_from_secondary',ProcessState='Proposal made',NotesZH='纳入已发生的提议，不表示编目完成或报酬已付。')
events['PE001'].update(Label='Dispatch of manuscripts to Pelliot in Paris',LabelZH='写本送寄巴黎供伯希和编目',EvidenceIds='EV047',NotesZH='原书明确记1910年秋送寄；边仅指送寄目的方，不断言1910已收讫或编目完成。')
places={'DH001':'敦煌／莫高窟','DH002':'敦煌／莫高窟','DH003':'莫高窟至安西（取得与运输阶段）','DH004':'伦敦／英国博物馆','DH005':'敦煌／莫高窟','DH006':'巴黎','DH007':'北京学部（接收）；发出地点未定','DH008':'北京（学部拨送、京师图书馆取运）','DH009':'北京／京师图书馆','KE001':'和田','KE003':'和田','KE004':'和田（记录语境）','KE005':'伦敦；具体工作房址未定','KE006':'伦敦／英国博物馆','KE007':'伦敦检查语境；成稿地点未独立落实','KE008':'伦敦检查后的提议；成稿地点未独立落实','PE001':'伦敦至巴黎（送寄端点）','KE009':'北京','KE010':'北京（相关查看活动语境）','MAP_KE011':'北京／六国饭店','MAP_KE012':'北京学部至兰州制台（通信端点）','DH003_K01':'安西至莫高窟（信件端点）','NEW_KA01':'肃州与陕甘总督体系（报告机构）','NEW_KA02':'陕甘总督至外务部（通信机构）','NEW_KA03':'北京（照会机构）','NEW_KP01':'报刊刊发；报道电头为北京，不代作刊发地','NEW_KP02':'期刊刊载；本条不作城市定位','NEW_KE_YE19100123':'日记记述；地点未在本轮材料中落实','NEW_KA_PROMISE1907':'会谈语境；具体地点未在本轮材料中落实'}
for eid,place in places.items():
 if eid in events:events[eid]['Place']=place
for e in edges:
 if e['EventId']=='KE001':e['EvidenceIds']='EV045'
 if e['EventId']=='KE007':e['EvidenceIds']='EV046'
 if e['EventId']=='PE001':e['EvidenceIds']='EV047'
 if e['EventId']=='DH006':e['EvidenceIds']='EV048'

def addnode(ident,zh,en,typ,evid='',notes=''):
 assert ident not in nodes,ident
 nodes[ident]=dict(Id=ident,Label=en,LabelZH=zh,NodeType=typ,Layer='Knowledge transmission',EventId='',ParentEventId='',YearStart='',YearEnd='',DatePrecision='',EvidenceIds=evid,NotesZH=notes)
def addevent(eid,zh,en,action,date,year,evid,place='',layer='Knowledge transmission',objects='',notes='',precision='year',state='Reported action',parent='',scope='Dunhuang materials'):
 addnode(eid,zh,en,'Event',evid,notes)
 events[eid]=dict(EventId=eid,Label=en,LabelZH=zh,Action=action,Layer=layer,DateText=date,DatePrecision=precision,YearStart=year,YearEnd=year,Place=place,ObjectIds=objects,SourceIds='',EvidenceIds=evid,ProcessState=state,Scope=scope,NotesZH=notes,ParentEventId=parent)
def edge(source,target,eid,relation,role,evid,notes=''):
 edges.append(dict(Id='E_READY_'+eid+'_'+source+'_'+target+'_'+relation,Source=source,Target=target,Type='Directed',Weight=1,Label=relation.replace('_',' '),Relation=relation,Role=role,Layer=events[eid]['Layer'],EventId=eid,EvidenceIds=evid,SourceRef='',NotesZH=notes))
addnode('N050','王家彦','Wang Jiayan','Person','EV022','依据G14所引日记；本事件只记录答应代发。')
edge('N050','NEW_KA_PROMISE1907','NEW_KA_PROMISE1907','participant_in_event','promisor','EV022')
edge('N005','NEW_KA_PROMISE1907','NEW_KA_PROMISE1907','participant_in_event','requester','EV022')
addevent('DH006_BNF1910','伯希和写本进入法国国家图书馆写本部','Pelliot manuscripts enter the manuscript department','institutional_receipt','1910年',1910,'EV044','巴黎','Physical circulation','B0005','机构说明的部门入藏阶段；与1909年底巴黎抵达分别记录。',parent='DH006')
# Reassign the old receiving endpoint to the documented department-entry stage.
for e in edges:
 if e['Id']=='E_DH006_DH006_N014':
  e.update(Id='E_READY_DH006_BNF1910_N014',Source='DH006_BNF1910',EventId='DH006_BNF1910',EvidenceIds='EV044',NotesZH='1910年写本部入藏；未使用1909年作为这一部门登记日期。')
edge('B0005','DH006_BNF1910','DH006_BNF1910','subject_of_event','manuscript_collection','EV044')
for e in edges:
 if e['Source']=='N013' and e['EventId']=='DH006':e.update(Relation='collection_associated_with',Role='expedition_collection_source',NotesZH='标记材料来源考察队，不声称队员在巴黎亲自交付。')

# L06 was obtained as full HTML through the authenticated NUS browser.
cabos=ROOT/'sources/L06_NUS_text.txt'
if cabos.exists() and len(cabos.read_text())>45000:
 ev(49,'L06','The Making of a Place；注16–18','Nouette为考察摄影者；1905–1906年与伯希和通信讨论设备。','通信按时间范围登记；不把每封信或未知日期补齐。',cabos,'Letters exchanged between 1905 and 1906')
 ev(50,'L06','摄影论述；注48','考察队1908年在敦煌拍摄影像。','日界与另一机构叙述存在口径差异，主表采用年份；遗址影像不等于每件写本照片。',cabos,'four hundred photographs')
 ev(51,'L06','The Shifting Trajectories；注59','1909年索邦讲座展示图像；1910年书面报告使用Nouette照片制版。','投影与印刷载体分开；不逐张匹配全部敦煌照片。',cabos,'Sorbonne')
 ev(52,'L06','注57；档号Pel Mi.67','1909年12月26日信函记复制敦煌文献照片的5000法郎款。','日期为信函记日；实际收款日和付款人未定；Tongkang不强认另一个姓名。',cabos,'26 December 1909')
 addnode('N045','夏尔·努埃特','Charles Nouette','Person','EV049;EV050;EV051')
 addnode('N051','诵芬室','Songfen Studio','PublicationOrganisation','EV020','G07明确记董康诵芬室刊印小册子；不等于董康亲手印刷。')
 addnode('R0004','努埃特敦煌遗址摄影组','Nouette Dunhuang site photographs','Representation','EV050','组级记录；未逐件生成馆藏号，也不覆盖全部考察影像。')
 addnode('R0005','1909索邦讲座所示摄影组','Photographs shown at the Sorbonne lecture','Representation','EV051','具体投影图与敦煌单张底片尚未逐件匹配。')
 addnode('R0006','1910报告内摄影制版组','Photo-engravings in the 1910 lecture report','Representation','EV051','与投影组分载体，不推定两组完全一致。')
 addnode('W008','Trois ans dans la haute Asie（1910）','Trois ans dans la haute Asie (1910)','Work','EV051','S22参与者报告；1909讲座与1910印本分别记录。')
 addnode('W009','1909年12月26日照片复制款相关信函','Letter recording photographic reproduction funds','Work','EV052','Pel Mi.67；本轮通过L06注57核查记述，未见原信影像。')
 addevent('PH001','努埃特在敦煌进行摄影记录','Nouette photographs Dunhuang','site_photography','1908年（敦煌考察阶段）',1908,'EV050','敦煌／莫高窟',notes='以年份记录，保留不同来源到离日差异；属于遗址摄影。',scope='Site documentation context')
 edge('N045','PH001','PH001','participant_in_event','photographer','EV050')
 edge('N013','PH001','PH001','participant_in_event','expedition_context','EV049;EV050')
 edge('PH001','R0004','PH001','produces_representation','site_photographs','EV050')
 addevent('PHOTO_LETTERS1905','伯希和与努埃特商议摄影设备','Pelliot and Nouette discuss photographic equipment','equipment_correspondence','1905–1906年往复信函',1905,'EV049',notes='合并为文献明确记载的往复通信组；不虚列每封信。',precision='year_range',scope='Expedition preparation context')
 events['PHOTO_LETTERS1905']['YearEnd']=1906
 edge('N012','PHOTO_LETTERS1905','PHOTO_LETTERS1905','participant_in_event','correspondent','EV049')
 edge('N045','PHOTO_LETTERS1905','PHOTO_LETTERS1905','participant_in_event','correspondent','EV049')
 addevent('LECTURE19091210','伯希和索邦讲座展示考察影像','Pelliot shows expedition images at the Sorbonne','illustrated_lecture','1909-12-10',1909,'EV051','巴黎／索邦',notes='讲座与印本分开；未把所有敦煌照片视为当晚全部投影。',precision='day',scope='Expedition communication context')
 edge('N012','LECTURE19091210','LECTURE19091210','participant_in_event','speaker','EV051')
 edge('LECTURE19091210','R0005','LECTURE19091210','presents_representation','projected_photographs','EV051')
 addevent('PUB_S22_1910','索邦讲座报告及摄影制版出版','Publication of the illustrated lecture report','illustrated_report_publication','1910年',1910,'EV051','巴黎',notes='原作S22；不以出版年替换讲座日期。',scope='Expedition communication context')
 edge('N012','PUB_S22_1910','PUB_S22_1910','participant_in_event','author','EV051')
 edge('PUB_S22_1910','W008','PUB_S22_1910','produces_work','printed_report','EV051')
 edge('W008','R0006','PUB_S22_1910','contains_representation','photo_engravings','EV051')
 edge('N045','R0006','PUB_S22_1910','photographic_source_creator','credited_photographer','EV051')
 addevent('PHOTO_FUNDS19091226','信函记述收到照片复制相关款项','Letter records receipt of reproduction funds','receipt_recorded_in_letter','1909-12-26（信函日期；实际收款日未定）',1909,'EV052','巴黎',notes='5000法郎用于照片复制；与1910编目方案报酬分开。Tongkang身份未强认，未虚构付款人。',precision='document_date')
 edge('N012','PHOTO_FUNDS19091226','PHOTO_FUNDS19091226','participant_in_event','reported_funds_recipient','EV052')
 edge('PHOTO_FUNDS19091226','W009','PHOTO_FUNDS19091226','documented_in','letter_evidence','EV052')
 edge('N035','R0002','MAP_KE011','author_of_manifestation','pamphlet_author','EV020')
 edge('N051','R0002','MAP_KE011','publisher_of_manifestation','recorded_imprint','EV020')

# Optional full-text additions are appended only after their own source audit.
if (ROOT/'sources/NUS_verified_PDFs.json').exists():
 exec(compile((ROOT/'add_NUS_content.py').read_text(),str(ROOT/'add_NUS_content.py'),'exec'),globals())
extra=ROOT/'verified_additions.json'
if extra.exists():
 data=json.loads(extra.read_text())
 for r in data.get('evidence',[]):evidence[r['id']]=r
 for r in data.get('nodes',[]):
  assert r['Id'] not in nodes,r['Id'];nodes[r['Id']]=r
 for r in data.get('events',[]):events[r['EventId']]=r;nodes[r['EventId']]=dict(Id=r['EventId'],Label=r['Label'],LabelZH=r['LabelZH'],NodeType='Event',EvidenceIds=r['EvidenceIds'],NotesZH=r['NotesZH'])
 edges.extend(data.get('edges',[]))

# Final rows are curated records, not approval placeholders.
used_nodes={e[k] for e in edges for k in ['Source','Target']}
nodes={i:n for i,n in nodes.items() if i in used_nodes}
for e in edges:
 event=events[e['EventId']];evs=split(e['EvidenceIds'])
 e['EvidenceIds']=';'.join(uniq(evs))
 e['SourceIds']=';'.join(uniq(split(srcs(e.get('SourceRef','')))+[evidence[v]['source'] for v in evs]))
 status={'Reported action':'Reported in cited sources','Proposal made':'Recorded proposal','Recorded promise':'Recorded promise','Work in progress':'Ongoing work reported'}[event['ProcessState']]
 e.update(YearStart=event['YearStart'],YearEnd=event['YearEnd'],DateText=event['DateText'],DatePrecision=event['DatePrecision'],ProcessState=event['ProcessState'],Scope=event['Scope'],Layer=event['Layer'],EvidenceStatus=status)
 for key in ['ReviewDecision','InCurrentGraph','SourceRef','EpistemicStatus']:e.pop(key,None)
 if e['EventId']=='DH003' and e['Source']=='N016':e['NotesZH']='Tila负责安西卸货；没有将其写成赴敦煌驮运者。'
 if e['EventId']=='DH003' and e['Source']=='N015':e['NotesZH']='Ibrahim参与外出队与安西卸货；同一Actor–Event关系只计一条。'
 if e['EventId']=='KE007':e['NotesZH']=event['NotesZH']
 if e['EventId']=='PE001':e['NotesZH']=event['NotesZH']
 e['NotesZH']=re.sub('建议把原transport_assistant细化为','角色细化为',e.get('NotesZH','')).replace('建议新增','已整理')
for eid,event in events.items():
 event['Label']=re.sub('^'+re.escape(eid)+r'\s+','',event['Label'])
 event['LabelZH']=re.sub('^'+re.escape(eid)+r'\s+','',event['LabelZH'])
 event['Action']={'初步列单':'preliminary_listing','编制索引卡清单':'index_slip_compilation','笔记记录':'notebook_recording','拆箱整理与列单':'unpacking_and_cataloguing','检查写本':'manuscript_examination','形成检查备忘录':'memorandum_preparation','为编目目的临时送寄':'temporary_cataloguing_dispatch','展示／查看':'manuscript_display_and_examination','摄影／复制':'photographic_reproduction'}.get(event['Action'],event['Action'])
 incident=[e for e in edges if e['EventId']==eid]
 event['SourceIds']=';'.join(uniq(s for e in incident for s in split(e['SourceIds'])))
 event['EvidenceIds']=';'.join(uniq(split(event['EvidenceIds'])+[v for e in incident for v in split(e['EvidenceIds'])]))
 if eid not in nodes:continue
 nodes[eid].update({k:v for k,v in event.items() if k not in ['SourceIds']})
for ident,n in nodes.items():
 incident=[e for e in edges if ident in [e['Source'],e['Target']]]
 n['SourceIds']=';'.join(uniq(s for e in incident for s in split(e['SourceIds'])))
 n['EvidenceIds']=';'.join(uniq(split(n.get('EvidenceIds',''))+[v for e in incident for v in split(e['EvidenceIds'])]))
 n['Label']=re.sub('^'+re.escape(ident)+r'\s+','',n['Label'])
 n['LabelZH']=re.sub('^'+re.escape(ident)+r'\s+','',n['LabelZH'])
 n['NotesZH']=n.get('NotesZH','').replace('建议ID；','').replace('建议新增','已整理').replace('候选','分立记录')
 n['EventId']=ident if n['NodeType']=='Event' else n.get('EventId','')
 n['EvidenceStatus']='Identified in cited sources'
 if n['NodeType']!='Event':
  layers={e['Layer'] for e in incident};n['Layer']=next(iter(layers)) if len(layers)==1 else 'Cross-layer'
 for key in ['ReviewDecision','InCurrentGraph','EpistemicStatus']:n.pop(key,None)

for eid,note in exclude_events.items():
 if not any(r['EventId']==eid for r in excluded):excluded.append(dict(RecordId=eid,EventId=eid,What=new_event_labels.get(eid,{}).get('LabelZH',eid),Reason=note,EvidenceIds=''))
source_rows={}
all_source_ids=uniq(s for n in nodes.values() for s in split(n['SourceIds']))
for sid in all_source_ids:
 l=literature.get(sid);old=legacy.get(sid)
 if l:
  p=Path(index[sid]['file']) if sid in index else None
  if (ROOT/'sources/NUS_verified_PDFs.json').exists():
   completed={r['SourceId']:r for r in json.loads((ROOT/'sources/NUS_verified_PDFs.json').read_text())}
   if sid in completed:p=Path(completed[sid]['file'])
  source_rows[sid]=dict(SourceId=sid,Author=l['作者'],Year=l['年份'],Title=l['题名'],Publication=l['出处'],URL=l['官方入口'],LocalPath=os.path.relpath(p,B) if p and p.exists() else '',Access='NUS订阅全文（HTML）' if sid=='L06' else '本地已有全文／本轮核对相关段落',NUS='https://libproxy1.nus.edu.sg/login?url=https://doi.org/'+l['DOI'] if l['DOI'] else 'https://nus.summon.serialssolutions.com/search?s.q='+l['题名'],Note=l['限制与待核'])
 elif old:
  p=PROJECT/old['本地路径（相对项目）']
  source_rows[sid]=dict(SourceId=sid,Author=old['作者'],Year=old['年份'],Title=old['题名'],Publication=old['版本／出处'],URL=old['链接'],LocalPath=os.path.relpath(p,B) if p.is_file() else '',Access='既有来源；相关原书另已补核' if sid=='S07' else '既有全文／原始扫描',NUS='',Note=old['限制'])
 elif sid=='WEB_BNF':source_rows[sid]=dict(SourceId=sid,Author='Bibliothèque nationale de France',Year='',Title='Manuscrits du monde – Asie - Océanie',Publication='机构馆藏说明',URL='https://www.bnf.fr/fr/manuscrits-du-monde-asie-oceanie',LocalPath=os.path.relpath(Path(index[sid]['file']),B),Access='官方馆藏正文',NUS='',Note='入写本部记1910；与巴黎抵达1909分别记录。')
 else:raise AssertionError(sid)
 if sid in ['G06','G10','L06']:
  source_rows[sid]['Access']='NUS入口取得正式PDF；关键段落已核'
  source_rows[sid]['Note']={'G06':'已核PDF9–10／印刷215–216；实际工作、进展报告与薪资提议分开，未把建议当作已执行。','G10':'已核章节PDF10–12、27／印刷36–38、53；月份差异保留，1914以后人物工作不提前到核心时间范围。','L06':'已核NUS完整HTML及正式PDF；摄影、讲座、刊载和复制款分别登记。'}[sid]
used_evidence=uniq(v for n in nodes.values() for v in split(n.get('EvidenceIds','')))
assert all(v in evidence for v in used_evidence)
assert all(e['Source'] in nodes and e['Target'] in nodes for e in edges)
assert len({e['Id'] for e in edges})==len(edges)
assert not any('待复核' in str(r.get('ReviewDecision','')) for r in list(nodes.values())+edges)
assert all(1900<=int(e['YearStart'])<=1910 and int(e['YearEnd'])<=1910 for e in edges)
assert len([e for e in edges if e['EventId']=='MAP_KE011' and e['Role']=='attendee'])==18
result=dict(nodes=list(nodes.values()),edges=edges,events=list(events.values()),sources=list(source_rows.values()),evidence=[evidence[v] for v in used_evidence],excluded=excluded)
(ROOT/'curated_data.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:len(v) for k,v in result.items()},ensure_ascii=False,indent=2))
