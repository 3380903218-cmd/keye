# -*- coding: utf-8 -*-
from pathlib import Path
from collections import Counter
from openpyxl import Workbook,load_workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.worksheet.table import Table,TableStyleInfo
from openpyxl.utils import get_column_letter
import csv,hashlib,json,math,os,random,re,unicodedata,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent;B=ROOT.parents[1]
OUT=B/'Gephi传播网络_可直接使用.xlsx';IMPORT=B/'Gephi传播网络_导入文件';IMPORT.mkdir(exist_ok=True)
D=json.loads((ROOT/'curated_data.json').read_text());N={n['Id']:n for n in D['nodes']};S={s['SourceId']:s for s in D['sources']};EV={e['id']:e for e in D['evidence']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
split=lambda s:[v for v in str(s or '').split(';') if v]
for n in N.values():
 if n['NodeType']=='Event':continue
 scopes={e['Scope'] for e in D['edges'] if n['Id'] in [e['Source'],e['Target']]}
 n['Scope']=next(iter(scopes)) if len(scopes)==1 else 'Cross-context'
node_headers=['Id','Label','LabelZH','NodeType','Layer','EventId','ParentEventId','YearStart','YearEnd','DateText','DatePrecision','ProcessState','Scope','EvidenceStatus','SourceIds','EvidenceIds','NotesZH']
edge_headers=['Id','Source','Target','Type','Weight','Label','Relation','Role','Layer','EventId','YearStart','YearEnd','DateText','DatePrecision','ProcessState','Scope','EvidenceStatus','SourceIds','EvidenceIds','NotesZH']
node_rows=[[n.get(k,'') for k in node_headers] for n in N.values()];edge_rows=[[e.get(k,'') for k in edge_headers] for e in D['edges']]
def csvwrite(name,headers,rows):
 p=IMPORT/name
 with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.writer(f);w.writerow(headers);w.writerows(rows)
 return p
csvwrite('nodes.csv',node_headers,node_rows);csvwrite('edges.csv',edge_headers,edge_rows)
csvwrite('events.csv',list(D['events'][0]),[[r.get(k,'') for k in D['events'][0]] for r in D['events']])
csvwrite('sources.csv',['SourceId','Author','Year','Title','URL'],[[r.get(k,'') for k in ['SourceId','Author','Year','Title','URL']] for r in D['sources']])

# A deterministic force layout makes the GEXF visible immediately on opening.
rng=random.Random(5419);ids=list(N);pos={i:[rng.uniform(-900,900),rng.uniform(-700,700)] for i in ids}
k=230.0
for iteration in range(100):
 disp={i:[0.0,0.0] for i in ids}
 for ai,a in enumerate(ids):
  for b in ids[ai+1:]:
   dx=pos[a][0]-pos[b][0];dy=pos[a][1]-pos[b][1];dist=max(math.hypot(dx,dy),0.1);force=k*k/dist
   fx=dx/dist*force;fy=dy/dist*force;disp[a][0]+=fx;disp[a][1]+=fy;disp[b][0]-=fx;disp[b][1]-=fy
 for e in D['edges']:
  a,b=e['Source'],e['Target'];dx=pos[a][0]-pos[b][0];dy=pos[a][1]-pos[b][1];dist=max(math.hypot(dx,dy),0.1);force=dist*dist/k
  fx=dx/dist*force;fy=dy/dist*force;disp[a][0]-=fx;disp[a][1]-=fy;disp[b][0]+=fx;disp[b][1]+=fy
 temp=55*(1-iteration/100)+2
 for i in ids:
  dx,dy=disp[i];dist=max(math.hypot(dx,dy),0.1);step=min(temp,dist);pos[i][0]+=dx/dist*step;pos[i][1]+=dy/dist*step
  pos[i][0]*=0.997;pos[i][1]*=0.997
NS='http://www.gexf.net/1.2draft';VIZ='http://www.gexf.net/1.2draft/viz';ET.register_namespace('',NS);ET.register_namespace('viz',VIZ)
q=lambda s:'{'+NS+'}'+s
root=ET.Element(q('gexf'),version='1.2');meta=ET.SubElement(root,q('meta'),lastmodifieddate='2026-10-29');ET.SubElement(meta,q('creator')).text='HY5419 Dunhuang project';ET.SubElement(meta,q('description')).text='Curated material and knowledge circulation network, 1900–1910; source limitations retained as attributes.'
graph=ET.SubElement(root,q('graph'),mode='static',defaultedgetype='directed')
ndef=[x for x in node_headers if x not in ['Id','Label']];edef=[x for x in edge_headers if x not in ['Id','Source','Target','Type','Weight','Label']]
for cls,headers in [('node',ndef),('edge',edef)]:
 attrs=ET.SubElement(graph,q('attributes'),{'class':cls,'mode':'static'})
 for key in headers:ET.SubElement(attrs,q('attribute'),id=key,title=key,type='integer' if key in ['YearStart','YearEnd'] else 'string')
degrees=Counter(v for e in D['edges'] for v in [e['Source'],e['Target']])
colours={'Person':(206,103,55),'Event':(40,114,113),'Institution':(52,108,165),'Government':(52,108,165),'Expedition':(165,105,44),'PublicationOrganisation':(88,108,150),'Collection':(132,91,159),'Object':(132,91,159),'Work':(148,128,65),'Representation':(94,141,89)}
xn=ET.SubElement(graph,q('nodes'))
for n in N.values():
 el=ET.SubElement(xn,q('node'),id=n['Id'],label=n['Label']);atts=ET.SubElement(el,q('attvalues'))
 for key in ndef:
  value=n.get(key,'')
  if value not in ['',None]:ET.SubElement(atts,q('attvalue'),{'for':key,'value':str(value)})
 red,green,blue=colours[n['NodeType']];ET.SubElement(el,q('color'),r=str(red),g=str(green),b=str(blue),a='1.0');ET.SubElement(el,q('position'),x='%.2f'%pos[n['Id']][0],y='%.2f'%pos[n['Id']][1],z='0.0');ET.SubElement(el,q('size'),value='%.2f'%(4+min(12,math.sqrt(degrees[n['Id']])*2)))
xe=ET.SubElement(graph,q('edges'))
for e in D['edges']:
 el=ET.SubElement(xe,q('edge'),id=e['Id'],source=e['Source'],target=e['Target'],weight='1.0',label=e['Label']);atts=ET.SubElement(el,q('attvalues'))
 for key in edef:
  value=e.get(key,'')
  if value not in ['',None]:ET.SubElement(atts,q('attvalue'),{'for':key,'value':str(value)})
gexf=IMPORT/'敦煌双层传播网络.gexf';ET.ElementTree(root).write(gexf,encoding='utf-8',xml_declaration=True)
web=dict(version='2026-10-29',scope='1900–1910',nodes=list(N.values()),edges=D['edges'],events=D['events'],sources=[{k:s[k] for k in ['SourceId','Author','Year','Title','URL']} for s in D['sources']],evidence=[{k:e[k] for k in ['id','source','printed','claim','limit','status']} for e in D['evidence']])
(IMPORT/'web_network_data.json').write_text(json.dumps(web,ensure_ascii=False,indent=2),encoding='utf-8')

wb=Workbook();wb.remove(wb.active);wb.properties.title='敦煌传播网络：可直接使用的数据';wb.properties.creator='HY5419 project';wb.properties.description='Curated data; sources and uncertainty are attributes, not approval tasks.'
FONT='Arial Unicode MS';TEAL='245B54';INK='253F39';BLUE='2453A1'
def lines(value,width):
 return max(1,sum(max(1,math.ceil(sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in part)/max(5,width-2))) for part in str(value or '').split('\n')))
def sheet(name,title,note,headers,rows,widths,machine=False):
 ws=wb.create_sheet(name);ws.sheet_view.showGridLines=False;ws.sheet_view.zoomScale=100;top=1 if machine else 4;last=get_column_letter(len(headers))
 if not machine:
  for rr,text in [(1,title),(2,note)]:
   ws.merge_cells(start_row=rr,start_column=1,end_row=rr,end_column=len(headers));c=ws.cell(rr,1,text);c.font=Font(name=FONT,size=16 if rr==1 else 11,bold=rr==1,color=INK);c.alignment=Alignment(wrap_text=True,vertical='center');ws.row_dimensions[rr].height=32 if rr==1 else 38
  ws.row_dimensions[3].height=9
 for j,(label,width) in enumerate(zip(headers,widths),1):
  ws.column_dimensions[get_column_letter(j)].width=width;c=ws.cell(top,j,label);c.font=Font(name=FONT,size=11,bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor=TEAL);c.alignment=Alignment(wrap_text=True,vertical='center')
 ws.row_dimensions[top].height=43
 for i,row in enumerate(rows,top+1):
  for j,value in enumerate(row,1):
   c=ws.cell(i,j,value)
   if isinstance(value,str) and value.startswith('='):c.data_type='s'
   c.font=Font(name=FONT,size=11,color=INK);c.alignment=Alignment(wrap_text=True,vertical='top');c.border=Border(bottom=Side(style='hair',color='D8E0DB'))
   if i%2==0:c.fill=PatternFill('solid',fgColor='F0F5F1')
  ws.row_dimensions[i].height=max(43,min(400,max(lines(v,w) for v,w in zip(row,widths))*15+28))
 if rows:
  table=Table(displayName='ReadyTable'+str(len(wb.worksheets)),ref='A%d:%s%d'%(top,last,top+len(rows)));table.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=False);ws.add_table(table)
 ws.freeze_panes='A'+str(top+1);ws.print_title_rows='1:'+str(top);ws.print_area='A1:'+last+str(ws.max_row);ws.page_setup.orientation='landscape';ws.page_setup.paperSize=ws.PAPERSIZE_A3;ws.page_setup.scale=100;ws._header=top
 return ws
def link(cell,target,label=None):
 if label is not None:cell.value=label
 cell.hyperlink=target;cell.font=Font(name=FONT,size=11,color=BLUE,underline='single')
layers={'Physical circulation':'实物流转','Knowledge transmission':'知识传播','Cross-layer':'跨层关联'}
relation_zh={'subject_of_event':'所涉文献／批次','transfer_from':'拨交／提供','transfer_to':'接收','participant_in_event':'参与活动','dispatch_destination':'送寄目的方','addressed_to':'通信指向','produces_work':'形成文字记录','produces_representation':'形成影像／复制品','circulates_representation':'散发刊物','collection_associated_with':'材料所属考察队','author_of_manifestation':'载体作者','publisher_of_manifestation':'载体刊印者','contains_representation':'载有影像','presents_representation':'展示影像','photographic_source_creator':'原摄影者','documented_in':'记述于文书','deposit_at':'暂存于','subset_of_collection':'所属收藏子组','annotates_work':'补注清单'}
overview=[['已整理规模',f"{len(N)}个节点；{len(D['edges'])}条关系；{len(D['events'])}个事件",'全部主表记录已作纳入判断，附日期精度和来源；不需要先填写审核清单。'],['直接打开Gephi','敦煌双层传播网络.gexf','打开同目录“Gephi传播网络_导入文件”内GEXF；文件含英文标签、颜色及初始布局。'],['直接阅读','01_传播关系','一行一条关系；中文名称便于查看，SourceIds与EvidenceIds能追溯。'],['事件与角色','02_事件数据；03_人物机构','时间、动作、范围与角色已经填入。共同出席宴会只连向事件，不造两两通信。'],['节点与边','07_Gephi_Nodes；08_Gephi_Edges','与配套nodes.csv、edges.csv完全一致；无需筛选“待复核”后才能使用。'],['时间范围','1900–1910；范围外材料另列','提议与承诺按已发生的表达行为纳入，ProcessState明确标注；不表示承诺事项已完成。'],['研究边界','一般Stein收藏／遗址摄影以Scope区分','可按Scope筛选严格的写本记录，保留与整理、展示相关的背景关联。'],['来源证据',f"{len(D['sources'])}条实际引用来源；{len(D['evidence'])}条证据定位",'G06、G10、L06均已通过NUS补取正式PDF并核对关键段落，补入整理人员、剑桥存放与摄影传播。'],['网页数据','web_network_data.json','配套JSON含中英文Label、事件、来源与证据，可供后续网页使用。'],['数量含义','边权重均为1','边数不是交易数、卷数或可信度。按EventId及行为类型统计事件。']]
ws=sheet('00_数据概览','敦煌传播网络｜已整理数据','完成日期：2026-10-29 · 主数据可直接阅读、筛选和导入；原网络文件保留作对照。',['内容','数据／入口','使用说明'],overview,[23,59,94]);link(ws.cell(6,2),os.path.relpath(gexf,B))
for r,target in [(7,'01_传播关系'),(8,'02_事件数据'),(9,'07_Gephi_Nodes')]:link(ws.cell(r,2),"#'%s'!A1"%target)
human=[]
for e in D['edges']:
 human.append([e['DateText'],N[e['Source']]['LabelZH'],relation_zh.get(e['Relation'],e['Relation']),N[e['Target']]['LabelZH'],layers[e['Layer']],e['Role'],e['EventId'],e['YearStart'],e['Id'],e['SourceIds'],e['EvidenceIds'],e['NotesZH']])
sheet('01_传播关系','传播关系明细｜已填充','与配套边表逐行一致。通信指向表示目的对象；共同参加不等于直接交流；文字、影像和原物分开。',['日期／精度说明','起点名称','关系','终点名称','网络层','具体角色','EventId','年份','EdgeId','SourceIds','EvidenceIds','限定说明'],human,[32,28,20,33,17,31,31,12,45,29,33,65])
evheads=['EventId','日期／界限','中文事件','地点','行为类型','English event','ProcessState','Scope','DatePrecision','起始年','结束年','对象／批次','SourceIds','EvidenceIds','具体说明']
evrows=[[e['EventId'],e['DateText'],e['LabelZH'],e['Place'],e['Action'],e['Label'],e['ProcessState'],e['Scope'],e['DatePrecision'],e['YearStart'],e['YearEnd'],e['ObjectIds'],e['SourceIds'],e['EvidenceIds'],e['NotesZH']] for e in D['events']]
sheet('02_事件数据','事件数据｜时间、地点与动作','一行一个事件；送寄与收讫、1909巴黎抵达与1910写本部接收已分开；文书记日不自动当行动日。',evheads,evrows,[24,38,40,34,33,44,26,38,32,12,12,24,32,33,72])
actor_types={'Person','Institution','Government','Expedition','PublicationOrganisation'}
arows=[[n['Id'],n['LabelZH'],n['Label'],n['NodeType'],layers[n['Layer']],';'.join(dict.fromkeys(e['EventId'] for e in D['edges'] if n['Id'] in [e['Source'],e['Target']])),n['SourceIds'],n['EvidenceIds'],n['NotesZH']] for n in N.values() if n['NodeType'] in actor_types]
sheet('03_人物机构','人物与机构｜双语名称及关联事件','人物与其所在机构分别建节点；姓名转写保留工作标签，原称呼放在说明中。',['Id','中文名称','English label','NodeType','网络层','参与／关联EventIds','SourceIds','EvidenceIds','说明'],arows,[19,33,38,29,19,68,36,36,69])
orows=[[n['Id'],n['LabelZH'],n['Label'],n['NodeType'],n.get('Scope',''),n['SourceIds'],n['EvidenceIds'],n['NotesZH']] for n in N.values() if n['NodeType'] not in actor_types|{'Event'}]
sheet('04_文献载体','文献、批次与载体｜已采用记录','B为分析批次，O为单件，W为文本／作品，R为复制品或影像组；分析ID不是馆藏号。',['Id','中文名称','English label','NodeType','Scope','SourceIds','EvidenceIds','范围与对应说明'],orows,[19,47,48,26,39,35,35,85])
srows=[[s['SourceId'],s['Author'],s['Year'],s['Title'],s['Publication'],s['Access'],s['LocalPath'],s['URL'],s['NUS'],s['Note']] for s in S.values()]
ws=sheet('05_来源依据','来源依据｜实际引用的文献与机构说明','来源篇数不是独立证实次数；S01/S02合并为L01，S17与L08按同文处理。原档未见时保留“研究转引”性质。',['SourceId','作者','出版年','题名','出处／版本','本轮取得方式','本地全文','官方来源','NUS入口','来源边界'],srows,[17,31,13,65,58,38,40,19,20,91])
for i,s in enumerate(S.values(),5):
 if s['LocalPath'] and (B/s['LocalPath']).is_file():link(ws.cell(i,7),s['LocalPath'],'打开本地原文')
 if s['URL']:link(ws.cell(i,8),s['URL'],'官方原文 ↗')
 if s['NUS']:link(ws.cell(i,9),s['NUS'],'NUS入口 ↗')
erows=[[e['id'],e['source'],e['printed'],';'.join(map(str,e.get('pages',[]))),e['claim'],e['status'],e['limit'],os.path.relpath(e['file'],B)] for e in D['evidence']]
ws=sheet('06_证据定位','证据定位｜直接回到原文','转述为数据依据；不能把关键词出现本身当作全部属性被证明。PDF页码与原刊页码分别保留，HTML用节名／注号。',['EvidenceId','SourceId','原刊页／章节与注号','本地PDF页','支持的内容','证据性质','解释边界','本地原文'],erows,[17,16,47,19,77,30,78,30])
for i,e in enumerate(D['evidence'],5):link(ws.cell(i,8),os.path.relpath(e['file'],B),'打开原文')
sheet('07_Gephi_Nodes','','',node_headers,node_rows,[27,43,42,30,29,30,28,15,15,49,34,30,41,39,35,38,90],True)
sheet('08_Gephi_Edges','','',edge_headers,edge_rows,[53,29,29,16,12,41,41,49,29,32,15,15,49,34,30,41,40,36,38,90],True)
xrows=[[r['RecordId'],r['EventId'],r['What'],r['Reason'],r['EvidenceIds']] for r in D['excluded']]
sheet('09_未纳入记录','未纳入默认网络的记录｜处理结论','主表和导出文件已经执行这些取舍；无需由你逐条审批后才能使用。新资料能够改变结论时，再追加新版本。',['RecordId','EventId','内容','本轮处理理由','EvidenceIds'],xrows,[65,32,54,101,36])
usage=[['GEXF','File → Open → 敦煌双层传播网络.gexf','直接打开配套文件；已有英文名称、类型颜色、初始布局。'],['CSV','先nodes.csv，后edges.csv；UTF-8、逗号、有向图','Excel中的07/08表就是同一数据；不要把01中文阅读表当边表导入。'],['Label / LabelZH','英文显示名称／中文对照','网页中英文切换使用这两个字段，Id保持不变。'],['Relation / Role','关系类型／具体角色','参加、接收、出版、图像来源、文书记述各自编码；不都表示所有权移动。'],['Layer','Physical circulation / Knowledge transmission / Cross-layer','实物流转、知识传播与跨层实体。'],['ProcessState','Reported action / Proposal made / Recorded promise / Work in progress','提议、承诺与进行中的工作分别标明，不把它们当作已经完成的成果。'],['Scope','Dunhuang materials / General Stein collection context / Site documentation context / Expedition communication context','限制严格写本分析时，先筛Scope；普通收藏处理、遗址摄影和全考察讲座保留背景标志。'],['DateText / DatePrecision','原样时间说明／精度','年份和期间界限不自动转换成1月1日；document_date只说明文书记日。'],['YearStart / YearEnd','数值年界','用于筛选范围，不代表全年持续活动。'],['EventId / ParentEventId','稳定事件键／父事件键','与路线地图和网页按ID关联；不同步骤不得重复统计取得。'],['SourceIds / EvidenceIds','来源键／证据键','分别连接05来源与06证据；同一材料的不同发表版本不增可信度权重。'],['Weight','统一为1','描述一条编码关系。来源数、照片数和卷数不作为默认边权。'],['分析用法','先选主体—事件子图，再按ActorId–EventId去重','全图多类节点的中心性不能直接解释为人物历史权力；18人共宴不是153次通信。'],['网页接入','web_network_data.json','JSON与本轮CSV/GEXF保持同一数据，含双语名称、事件、来源和证据；不含登录凭据或本地绝对路径。'],['更新','按现有Id追加或修正，另存新版本','没有公式；数量与核验报告是这一版文件的快照。']]
sheet('10_字段与使用','字段与使用｜Gephi和网页均可复用','这是一份已经整理的数据集。精确到什么程度由字段直接表达，未决文件对应和范围外资料不混入默认网络。',['字段／用途','定义／操作','说明'],usage,[31,91,110])
for ws in wb:
 for row in ws.iter_rows(min_row=ws._header+1):
  ws.row_dimensions[row[0].row].height=max(43,min(400,max(lines(c.value,ws.column_dimensions[c.column_letter].width) for c in row)*15+28))
if OUT.exists():
 old=ROOT/'delivery_manifest.json';known=json.loads(old.read_text()).get('workbook_sha256') if old.exists() else None
 if sha(OUT)!=known:
  import shutil
  p=ROOT/('保留已有版本_'+sha(OUT)[:10]+'.xlsx')
  if not p.exists():shutil.copy2(OUT,p)
wb.save(OUT)

readme=f'''敦煌双层传播网络：直接使用说明
完成日期：2026-10-29

一、直接打开
在Gephi中选择File → Open，打开“敦煌双层传播网络.gexf”。本版为{len(N)}节点、{len(D['edges'])}边，包含{len(D['events'])}个事件。英文标签、节点类型颜色和初始布局已写入。

二、使用Excel
上级目录的“Gephi传播网络_可直接使用.xlsx”中，01表是中文关系明细，02是事件数据，07/08与本目录nodes.csv和edges.csv逐行相同，不需先做审核筛选。

三、边界
时间1900–1910。ProcessState区分实际活动、已提出的方案、已记录的承诺；提议不表示编目已经完成。Scope区分严格敦煌文献、一般Stein材料、遗址摄影及全考察讲座背景。边数不是交易数，Weight不表示可信度。未决身份对应与1911后续已从默认图排除。

四、CSV与网页
CSV为UTF-8 BOM、逗号分隔。先导节点，再导有向边；Id、Source、Target按文本保留。web_network_data.json包含同一数据及来源，供后续中英文网页接入；没有登录信息和本地绝对路径。
'''
(IMPORT/'使用说明.txt').write_text(readme,encoding='utf-8')
check=load_workbook(OUT,data_only=False)
assert not check._external_links and not any(c.data_type=='f' for w in check for row in w for c in row)
assert all(c.font.sz>=11 for w in check for row in w for c in row if c.value is not None)
assert len(node_rows)==len(N) and len(edge_rows)==len(D['edges'])
for key,headers,rows in [('nodes.csv',node_headers,node_rows),('edges.csv',edge_headers,edge_rows)]:
 with (IMPORT/key).open(encoding='utf-8-sig') as f:read=list(csv.reader(f))
 assert len(read)==len(rows)+1 and read[0]==headers
xml=ET.parse(gexf);assert len(xml.findall('.//'+q('node')))==len(N) and len(xml.findall('.//'+q('edge')))==len(D['edges'])
assert '/Users/' not in (IMPORT/'web_network_data.json').read_text()
report=dict(workbook=str(OUT),workbook_sha256=sha(OUT),workbook_bytes=OUT.stat().st_size,nodes=len(N),edges=len(D['edges']),events=len(D['events']),sources=len(S),evidence=len(EV),sheets=wb.sheetnames,formulas=0,imports={p.name:sha(p) for p in IMPORT.iterdir() if p.is_file()},curated_sha256=sha(ROOT/'curated_data.json'),native_open='pending',visual_check='pending')
(ROOT/'delivery_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['imports','sheets']},ensure_ascii=False,indent=2))
