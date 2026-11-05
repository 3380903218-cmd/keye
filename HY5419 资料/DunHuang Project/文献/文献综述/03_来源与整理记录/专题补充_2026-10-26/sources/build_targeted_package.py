# -*- coding: utf-8 -*-
from pathlib import Path
import csv, hashlib, json, re
from urllib.parse import quote
import fitz

BASE=Path(__file__).resolve().parent.parent
PROJECT=BASE.parents[2]
DATE='2026-10-26'
BM='https://britishmuseum.iro.bl.uk/entities/publication/163f1704-dc82-47fa-9cdc-60aa50e5ca48'
BMFILE='full-text/G13_Wang_ed_2012.pdf'

def item(sid, author, year, title, venue, doi, url, path, status, locator, contribution, gephi, limitation, priority, search, **extra):
    d=dict(source_id=sid,author=author,year=year,title=title,venue=venue,doi=doi,url=url,path=path,status=status,locator=locator,contribution=contribution,gephi=gephi,limitation=limitation,priority=priority,search=search)
    d.update(extra)
    d['nus_search']='https://nus.summon.serialssolutions.com/search?s.q='+quote(title)
    d['nus_proxy']='https://libproxy1.nus.edu.sg/login?url='+quote('https://doi.org/'+doi if doi else url,safe=':/')
    return d

records=[
item('G14','王冀青',2020,'陕甘总督升允阻止斯坦因敦煌考古始末','敦煌学辑刊', '', 'https://dhxyjs.lzu.edu.cn/userfiles/files/20210203/6374794351518998576216398.pdf','full-text/G14_Wang_2020.pdf','present','原刊122–134页；先读122–123、126–129页（PDF1–2、5–8）','以相关记录讨论1907年地方官、电报与阻止挖掘的过程。','可为官员报送、发出指令和请求等关系补采证据；对应1907年取得事件的行政背景。','论文125–126页同时包含作者推论；应区分录文与“应、必定”等推断。1907年阻挖不自动等于藏经洞写本交接；原档未由本轮独立核验。','A：历史关系补采','S006',number='4',pages='122--134',entry_type='article',note='原刊以年度期次标示；本轮未核实独立卷号和DOI，不补造。'),
item('G13a','Wang, Jiqing',2012,'Aurel Stein’s Dealings with Wang Yuanlu and Chinese Officials in Dunhuang in 1907','In Helen Wang (ed.), Sir Aurel Stein, Colleagues and Collections','',BM,BMFILE,'present','合卷PDF24–29；章内页1–6，重点页1、3–5','讨论蒋孝琬代为交涉、官员称谓及1907年地方情境。','帮助细分代为交涉与直接交出；称谓作为属性保留，涉及DH001、DH002及蒋孝琬角色。','章末说明与2007年较长中文稿及IDP短文相关，不能当三项独立佐证；仍须逐条区分档案转引与作者解释。','A：中介角色','S007',pages='1--6',entry_type='incollection',booktitle='Sir Aurel Stein, Colleagues and Collections',editor='Wang, Helen',publisher='British Museum',isbn='9780861591848',note='合卷中的各章独立分页；本章位于所交付PDF24–29页。'),
item('G13b','Sims-Williams, Ursula',2012,'Aurel Stein’s Correspondence with Paul Pelliot and Lionel Barnett','In Helen Wang (ed.), Sir Aurel Stein, Colleagues and Collections','',BM,BMFILE,'present','合卷PDF105–113；章内页1–9。先读章内1–3页，特别PDF106','介绍Or.13114通信档案与整理工作机构，区分1910年编目建议和随后送寄、收件。','直接服务KE006、KE007、KE008、PE001的回查：检查、备忘录、意向与收件分别记录，不能重复建相同事件。','这是档案目录及研究说明，不是本轮已查见的逐封信件原件。后续多在1911–1930年代；1911年收件应标为核心范围外的后续，不并入1910年完成活动。','A：两层联动','S007',pages='1--9',entry_type='incollection',booktitle='Sir Aurel Stein, Colleagues and Collections',editor='Wang, Helen',publisher='British Museum',isbn='9780861591848',note='本章位于所交付合卷PDF105–113页，章内独立分页。'),
item('G08','王冀青',2015,'斯坦因在安西所获敦煌写本之外流过程研究','敦煌研究','', 'http://iqh.ruc.edu.cn/old/jssxwhsyj/wbydyzygx/zlgxypj/008fc7fe609449428944b45de683c9de.htm',str(PROJECT/'路线地图/sources/2026-10-20_实质补采集/R01_Wang_2015_RUC_http.html'),'existing','原刊75–83页；机构转载中安西通信、蒋赴敦煌及装箱运输段。转载段落未逐一对应原刊页','把信使、通信、代理取得和后续运输分开讨论。','补充DH003相关角色、传信活动和阶段；与现有地图源R01同源，复用原文件。','全文是学术机构转载；日记原件未读，部分日期和匿名信使身份是推定；不可将每段路线都计为独立取得。','A：已有路线研究，升入综述','S004',number='6',pages='75--83',entry_type='article',note='已在路线地图目录保存机构转载，未重复复制。原刊PDF及DOI本轮未独立取得。'),
item('G07','秦桦林',2018,'1909年北京学界公宴伯希和事件补考——兼论王国维与早期敦煌学','浙江大学学报（人文社会科学版）','10.3785/j.issn.1008-942X.CN33-6000/C.2018.02.051','https://www.zjujournals.com/soc/CN/abstract/abstract11967.shtml',str(PROJECT/'路线地图/sources/2026-10-20_实质补采集/R04_Qin_2018.pdf'),'existing','原刊44–56页；先读45–48页（PDF2–5），表1及学部电报段','通过日记等材料重考宴会日期、人员、组织背景与相关通信。','MAP_KE011/012与现有KE009对照；分别登记参加宴会、展示查看、发出电报，识别引荐和组织角色。','同场出现不等于人人互相通信；宴会不证明原物在场。原始日记、官报在本轮仍是论文转引。卷期48(3)据原刊PDF核对。','A：已有知识层研究，升入综述','S003',volume='48',number='3',pages='44--56',entry_type='article'),
item('G01','Düring, Marten',2015,'From Hermeneutics to Data to Networks: Data Extraction and Network Visualization of Historical Sources','Programming Historian','10.46430/phen0044','https://programminghistorian.org/en/lessons/creating-network-diagrams-from-historical-sources','full-text/G01_During_2015.md','present','Developing a coding scheme；The added value of network visualizations','同行评审方法教程，说明从叙述文本抽取关系、限定参与者、按关系类型编码并回到语境。','用于统一Role、Relation、EventId及证据定位；把一段叙述拆为有依据的动作，而非仅按人名共现连边。','案例为二战互助网络；工具操作写于2015年。借鉴编码方法，不照搬旧版界面、99缺失值或把其结论当敦煌事实。','A：第一篇方法阅读','S002',number='4',entry_type='article',note='在线教程无连续页码；交付官方GitHub Markdown源稿，图像请在原站查看。'),
item('G03','Faust, Katherine',1997,'Centrality in affiliation networks','Social Networks','10.1016/S0378-8733(96)00300-0','https://sites.socsci.uci.edu/~kfaust/faust/research/articles/faust_centrality_sn_1997.pdf','full-text/G03_Faust_1997.pdf','present','157–160页（PDF1–4）及Discussion 188–189页（PDF32–33）','讨论人物与事件二模参与网络及其中心性解释。','为从现有多类节点图抽取“主体—事件参与子图”、理解人物或事件中心性提供依据。','二模参与关系与目前带角色方向的混合总图不同；一模投影只表示共参与，不证明直接通信或实物交接；可先跳过公式推导。','A：指标解释','S001',volume='19',number='2',pages='157--191',entry_type='article'),
item('G05','Ahnert, Ruth and Ahnert, Sebastian E.',2015,'Protestant Letter Networks in the Reign of Mary I: A Quantitative Approach','ELH','10.1353/elh.2015.0000','https://model-articles.rrchnm.org/articles/ahnert/','full-text/G05_Ahnert_Ahnert_2015.html','present','网页Data Selection、Network Visualisation等作者注释及信使、资助者讨论；原文1–33页','历史通信网络案例，解释如何识别通信基础设施中的信使与支持者，并讨论材料选择偏差。','可比较蒋孝琬等角色如何连接不同活动；通信发送者、收件者、承运者须分开采集。','交付2021年作者注释网页全文，不是2015年原刊PDF；英国宗教史案例只作方法比较。原文页码1–33据作者注释版及引用复核，Crossref的1–1不沿用。','A：可仿照的案例论证','S003',volume='82',number='1',pages='1--33',entry_type='article',version='2021 annotated full-text web edition of 2015 article',note='注释版另有DOI10.31835/ma.2021.04；按原论文只计一项研究。'),
item('G04','Edelstein, Dan and Findlen, Paula and Ceserani, Giovanna and Winterer, Caroline and Coleman, Nicole',2017,'Historical Research in a Digital Age: Reflections from the Mapping the Republic of Letters Project','The American Historical Review','10.1093/ahr/122.2.400','https://republicofletters.stanford.edu/publications/HistoricalResearch.pdf','full-text/G04_Edelstein_et_al_2017.pdf','present','414、418–420页（PDF15、19–21）及结尾424页','讨论通信数据、地方与时间、元数据缺失和图形解释的边界。','为综述的方法部分与Gephi、地图、时间线共用事件证据提供参照。','早期近代欧洲通信项目，数据规模及语境不同；方法移用不构成敦煌传播关系的证据。','B：综述与方法论证','S003',volume='122',number='2',pages='400--424',entry_type='article'),
item('G02','Ahnert, Ruth and Ahnert, Sebastian E. and Coleman, Catherine Nicole and Weingart, Scott B.',2020,'The Network Turn: Changing Perspectives in the Humanities','Elements in Publishing and Book Culture','10.1017/9781108866804','https://www.cambridge.org/core/books/network-turn/CC38F2EA9F51A6D1AFCB7E005218BBE5','full-text/G02_Ahnert_et_al_2020.pdf','present','第3章Culture Is Data及第4章Visual Networks；先读48–50页（PDF56–58）的多模与投影讨论','解释文化材料如何建模为网络，以及多模、投影与视觉表达之间的差别。','用于说明NodeType分层、总图与子图的关系，以及图形布局和历史结论的差别。','理论概览，不要求通读128页；不是当前Gephi版本操作手册，也不能直接验证敦煌事件。','B：选读理论章节','S002',entry_type='book',publisher='Cambridge University Press',isbn='9781108866804',note='依PDF版权页与在线初版使用2020；纸本另有2021日期。'),
item('G06','Wang, Helen',1998,'Stein’s Recording Angel—Miss F. M. G. Lorimer','Journal of the Royal Asiatic Society','10.1017/S1356186300009986','https://www.cambridge.org/core/journals/journal-of-the-royal-asiatic-society/article/abs/steins-recording-angel-miss-f-m-g-lorimer/DDBEAF0E1DB1819C6128FD8A586424ED','','unavailable','出版社Extract与书目信息已核；正文内部页码尚不能指定','出版社简介明确涉及拆箱、登记、整理及展览等日常工作者。','高优先补取全文，核对Lorimer的实际工作日期与角色，再决定纳入1900–1910主图或作为后续比较。','尚未读正文；不据摘要生成她参与某一事件的边。1998是原刊年，2009是上线日期。NUS订阅覆盖尚未验证。','待NUS：优先1','S005',volume='8',number='2',pages='207--228',entry_type='article'),
item('G10','Dotson, Brandon and Doney, Lewis',2025,'1 Conserving Limitless Life','In Producing Buddhist Sutras in Ninth-Century Tibet','10.1515/9783111569550-003','https://uplopen.com/en/chapters/m/10.1515/9783111569550-003','','unavailable','已核目录：1.3 Cataloguing and preparatory work in Cambridge（53页）；1.4 Binding and cataloguing in London（64页）；正文27–81页待取','目录显示第1章专谈近现代保存和编目，适合追查原物在英国的知识处理。','优先获取第1章后，核对编号、整理者、装订和目录形成事件，不能只凭全书九世纪标题判断不相关。','OA身份、目录和章节书目已核，PDF请求返回202/403，正文未取得；不能声称内容已经全文验证。书目年2025，在线2024-12。','待手动：优先2','S005',pages='27--81',entry_type='incollection',booktitle='Producing Buddhist Sutras in Ninth-Century Tibet: The Sutra of Limitless Life and its Dunhuang Copies Kept at the British Library',publisher='De Gruyter',isbn='9783111569550'),
]

def write_table(path,fields,rows,delim='\t',bom=False):
    with path.open('w',encoding='utf-8-sig' if bom else 'utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter=delim,extrasaction='ignore');w.writeheader();w.writerows(rows)

old=[]
oldrows=list(csv.DictReader((BASE.parent/'10篇文献整理表.csv').open(encoding='utf-8-sig')))
decisions={
'L01':('保留核心','王圆箓的选择、保管和谈判；与新中介研究对读。'),
'L02':('保留核心','对象、捆束、编号及取得批次；继续支持数据模型。'),
'L03':('保留清代接收核心','区分行政文书录文、接收底账和写卷题记；原档仍待核。'),
'L04':('按收藏链问题选读','论证质量不等于本轮适配度；藏家归因与物质证据不是当前网络方法的替代。'),
'L05':('第一节升为核心','134–137页直接回应“取得时间与被知晓时间不同”；1912/1921案例作比较背景。'),
'L06':('待取全文，摄影专题备选','现只有摘要；不能据未读全文生成摄影传播关系。'),
'L07':('保留跨层专题','旧图版、原物与刊布载体的区别有用；1939等范围外事件不自动纳入。'),
'L08':('方法比较','对象是绘幡，不直接充当写本流转事实。'),
'L09':('降为项目背景','1996年IDP介绍不能承担1900–1910人物传播网络的主体论证。'),
'L10':('降为语义组织背景','图像知识关联与历史主体间的传播关系不是同一对象；不作为主要Gephi分析方法。')}
for row in oldrows:
    oid=row.get('ID') or row.get('文献ID') or list(row.values())[0]
    if oid not in decisions:continue
    action,why=decisions[oid]
    oldpath=row.get('本地正文','')
    old.append(dict(old_id=oid,title=row.get('题名',''),decision=action,reason=why,original_file=str(BASE.parent/oldpath) if oldpath else ''))
write_table(BASE/'旧文献重排.csv',['old_id','title','decision','reason','original_file'],old,',',True)

reading=[]
for rank,r in enumerate(records,1):
    reading.append({'阅读序':rank,'文献ID':r['source_id'],'优先级':r['priority'],'作者':r['author'],'年份':r['year'],'题名':r['title'],'出处':r['venue'],'DOI':r['doi'],'先读位置':r['locator'],'研究内容或已核范围':r['contribution'],'如何服务Gephi':r['gephi'],'限制与待核':r['limitation'],'全文状态':{'present':'本次新增全文','existing':'已有全文，复用原路径','unavailable':'正文待取'}[r['status']],'文件或已有路径':r['path'],'官方入口':r['url'],'NUS题名检索':r['nus_search'],'NUS代理入口':r['nus_proxy']})
write_table(BASE/'专题文献_阅读与Gephi用途.csv',list(reading[0]),reading,',',True)

manifest=[];screen=[];evidence=[]
for r in records:
    sid=r['source_id'];present=r['status']=='present';existing=r['status']=='existing';included=present or existing
    citation=f"{r['author']} ({r['year']}). {r['title']}. {r['venue']}"
    chapter=sid in ['G13a','G13b']
    path=r['path'] if present and not chapter else ''
    checksum=hashlib.sha256((BASE/path).read_bytes()).hexdigest() if path else ''
    notes=r['limitation']
    if chapter:notes+=' 章节正文已交付；实体文件由容器记录G13volume登记（'+BMFILE+'），本章节不重复登记同一文件。not_required仅指无需独立章节文件，不表示未读。'
    if existing:notes+=' 本次不重复交付原文件；已有路径见阅读索引。'
    manifest.append(dict(source_id=sid,citation=citation,stable_id=r['doi'] or r['url'],version=r.get('version','verified publisher/author full text' if included else 'metadata/abstract only'),evidence_role='original_study' if sid in ['G14','G13a','G13b','G07','G08','G05'] else ('review' if sid=='G02' else 'other'),full_text_status='present' if present and not chapter else ('not_required' if existing or chapter else 'unavailable'),full_text_path=path,sha256=checksum,notes=notes))
    screen.append(dict(record_id='SC_'+sid,search_id=r['search'],source_id=sid,title=r['title'],year=r['year'],stage='full_text' if included else 'abstract',decision='include' if included else 'pending',decision_round=1,current='true',supersedes='',reason='题材、证据粒度或网络模型直接适配；已查相应正文段落' if included else '书目/目录适配，但正文未取得，不升格为已读核心证据',evidence_role=manifest[-1]['evidence_role'],notes=r['priority']))
    if included:
        evidence.append(dict(evidence_id='EV_'+sid,claim_id='ROLE_'+sid,claim_text=r['contribution'],claim_status='fact',source_id=sid,source_role=manifest[-1]['evidence_role'],locator=r['locator'],evidence_excerpt=r['contribution'],scope='仅概括所查研究的内容与适配性；不替代原档核验',direction='supports',strength='direct',intended_use='method' if sid in ['G01','G02','G03','G04','G05'] else 'interpretation',notes=r['gephi']+' '+r['limitation']))

manifest.append(dict(source_id='G13volume',citation='Helen Wang (ed.) (2012). Sir Aurel Stein, Colleagues and Collections. British Museum Research Publication 184. ISBN 9780861591848.',stable_id=BM,version='British Museum repository volume PDF',evidence_role='other',full_text_status='present',full_text_path=BMFILE,sha256=hashlib.sha256((BASE/BMFILE).read_bytes()).hexdigest(),notes='仅为G13a与G13b两项章节研究登记共同的实体文件，不另计一项纳入研究。章节阅读与证据分别见对应记录。'))

for sid,title,reason,search in [
('X01','Social Network Centralization Dynamics in Print Production','材料生产网络案例有参考价值；本轮已有更直接处理参与、通信与缺失的案例，暂不扩展核心清单。PDF站点受验证保护。','S006'),
('X02','Formal network methods in history: why and how?','一般史学网络方法候选，作为后续理论补读；本轮优先较短编码教程与二模论文，不重复增加同类阅读负担。','S006'),
('X03','伯希和1909年北京之行相关事件杂考','可继续追查，但检索记录对页码有冲突（出现167–176与89等）；须NUS原刊核验，暂不作为完整书目或历史论断依据。','S004')]:
    manifest.append(dict(source_id=sid,citation=title,stable_id='',version='discovery only',evidence_role='background',full_text_status='not_required',full_text_path='',sha256='',notes=reason))
    screen.append(dict(record_id='SC_'+sid,search_id=search,source_id=sid,title=title,year='',stage='title',decision='exclude',decision_round=1,current='true',supersedes='',reason=reason,evidence_role='background',notes='不属于本轮交付的核心全文'))

fields=['source_id','citation','stable_id','version','evidence_role','full_text_status','full_text_path','sha256','notes']
write_table(BASE/'source-manifest.tsv',fields,manifest)
write_table(BASE/'screening-ledger.tsv',['record_id','search_id','source_id','title','year','stage','decision','decision_round','current','supersedes','reason','evidence_role','notes'],screen)
write_table(BASE/'evidence-matrix.tsv',['evidence_id','claim_id','claim_text','claim_status','source_id','source_role','locator','evidence_excerpt','scope','direction','strength','intended_use','notes'],evidence)

searchrows=[]
for i,p in enumerate(sorted((BASE/'sources').glob('search_[0-9][0-9][0-9].json')),1):
    j=json.loads(p.read_text());raw=j['result'];n=len(set(re.findall(r'cite([^]+)',raw)))
    searchrows.append(dict(search_id=f'S{i:03d}',source='Web search discovery; publisher, author/institutional full-text verification',executed_date=DATE,query=json.dumps(j['queries'],ensure_ascii=False),filters='中英文；相关历史事件1900–1910，范围外部分只作比较；文献截至2026-10-26',boundary='本次返回的有限结果；未遍历全部搜索结果或数据库',raw_count='',saved_count=n,output_path=str(p.relative_to(BASE)),status='partial',notes='未返回可审计的全库总数；网页检索只用于发现，正文按单篇复核。'))
searchrows.append(dict(search_id='NUS001',source='NUS Libraries / Safari',executed_date=DATE,query='NUS portal and proxy login for DOI10.1017/S1356186300009986',filters='NUS优先',boundary='打开官网及代理登录页；Safari网页读取设置未开启；尚未进入认证全文',raw_count='',saved_count='',output_path='metadata/NUS访问状态.json',status='partial',notes='已向用户请求在本机开启Allow JavaScript from Apple Events；不收取密码或二次验证码。未确认机构订阅覆盖。'))
write_table(BASE/'search-ledger.tsv',['search_id','source','executed_date','query','filters','boundary','raw_count','saved_count','output_path','status','notes'],searchrows)
(BASE/'metadata/NUS访问状态.json').write_text(json.dumps({'date':DATE,'portal':'https://lib.nus.edu.sg/','proxy_opened_for':'10.1017/S1356186300009986','observed_title':'NUS Libraries: Library Proxy: Login','authenticated_fulltext_read':False,'institutional_entitlement_confirmed':False,'blocker':'Safari Allow JavaScript from Apple Events is disabled; user setup requested asynchronously','downloads_via_nus':0,'public_full_text_files':7},ensure_ascii=False,indent=2))

def link(r):
    target=r['path'] if r['path'] else r['url']
    return '<'+target+'>' if ' ' in target else target

guide=['# 为敦煌双层传播网络重选的专题文献','',f'整理日期：{DATE}（新加坡）。本轮为专题筛选与阅读包，不是穷尽性综述。','',
'这轮的重点是让文献能够支持具体的事件、角色、关系与证据说明。现有清单的主要问题是阅读层级和当前问题不完全匹配，不能据此笼统判断全部研究质量低。新的清单同时补充直接历史研究与可迁移的历史网络案例。','',
'新增7份全文文件：5份PDF、1份作者注释网页全文、1份官方Markdown源稿。2012年论文集内选读两章，仍只保存一份合卷。另复用路线地图目录中已有的2篇研究，没有重复复制旧文件。2项高适配候选仍待取得正文。','',
'## 第一轮怎样读','',
'先读旧包L05潘晟2025的134–137页，再读G13a六页、G13b章内1–3页、G14的122–123及126–129页。带着这些案例读G01的编码部分，再选读G03开头与Discussion；G05作为如何把中介角色写成分析的比较案例。G02和G04按所列章节补读。无需把所有书从头通读后才工作。','',
'本轮尤其回应你在《敦煌-文献综述思考.docx》中提出的“取得早、被知晓晚”和“称谓如何影响交涉”。记录时把取得事件、通信/刊布事件、个人获知的时间与后来研究者的解释分开。文献没有提及某人，可以记录为可检验的文本现象；有意替另一人隐瞒则是另一层判断，需要独立证据。','',
'## 10项可立即阅读的专题条目','']
for r in records:
    if r['status']=='unavailable':continue
    guide += [f"### {r['source_id']}｜{r['title']}",'',f"{r['author']}，{r['year']}。{r['venue']}。",'',f"**先读：** {r['locator']}",'',f"**用途：** {r['contribution']} {r['gephi']}",'',f"**边界：** {r['limitation']}",'',f"[全文／已有原文件]({link(r)}) · [官方入口]({r['url']}) · [NUS题名检索]({r['nus_search']})",'']
guide += ['## 两项优先补取正文的候选','', '它们已核题名、书目或目录，但没有用未读正文生成历史关系。具体操作见[待手动下载_NUS优先.md](待手动下载_NUS优先.md)。','']
for r in records:
    if r['status']!='unavailable':continue
    guide += [f"- **{r['source_id']} {r['author']} ({r['year']})，{r['title']}**：{r['contribution']} {r['limitation']}",'']
guide += ['## 旧包怎样保留','', 'L01、L02、L03仍是核心史学阅读。L05第一节升为与你当前问题直接相关的核心；L07适合图版与原物的跨层联系。L09的1996年IDP介绍及L10的图像语义组织论文降为背景，它们不承担早期人物传播网络的主要论证。逐项判断见[旧文献重排.csv](旧文献重排.csv)。旧文件和旧综述正文均未改写。','',
'## 用这批文献完善Gephi的顺序','',
'1. 先从具体事件补证据与角色，复用既有EventID，新增材料不自动等于新增事件。','2. 区分取得、代为谈判、搬运、发信、代拟、登记、编目提议、正式收件。每种箭头写明含义。','3. 先明确人物—事件参与子图，再决定是否投影或计算指标；共参与不是两人直接通信。当前混合总图不能直接当作Faust讨论的二模图。','4. 用时间线区分活动、意向与后续执行；范围外的1911年事件可在注释中承接，不自动扩展1900–1910核心。','5. 把网络的结构现象带回史料解释，比较作者立场与来源覆盖；未记录不等于未发生。','',
'## 文件与获取状态','',
'- [专题文献_阅读与Gephi用途.csv](专题文献_阅读与Gephi用途.csv)：可用Excel打开，含阅读位置、对应字段、全文与NUS入口。','- [文献对Gephi的修改建议.md](文献对Gephi的修改建议.md)：具体回查线索，尚未执行数据修改。','- [references.bib](references.bib)：已核书目；候选全文状态仍见阅读表。','- source-manifest.tsv、screening-ledger.tsv、evidence-matrix.tsv、search-ledger.tsv：来源、筛选与证据记录。','- full-text/：已取得的新全文；extracted/与sources/保存核查材料。','',
'NUS优先入口已尝试打开，但Safari仍未开启网页读取，且代理页面停在登录。当前新增全文均来自公开的出版社或作者／机构版本，不能称为NUS授权下载；NUS下载数为0。受限全文与OA接口技术失败分别记录，订阅覆盖也尚未确认。','']
(BASE/'先读这份_专题文献与Gephi用途.md').write_text('\n'.join(guide))

manual=['# 待手动下载：NUS优先','',f'状态日期：{DATE}。NUS代理登录页已在Safari打开。请只在官方页面输入账号及二次验证码，无需发给助手。','',
'## 恢复自动协作','', 'Safari → 设置 → 开发者 → 勾选 Allow JavaScript from Apple Events。完成NUS登录后回复“已开启，NUS已登录”。目前没有读取认证后的页面，也没有确认以下文献的NUS订阅覆盖。','',
'## 两项待取全文','']
for sid in ['G06','G10']:
    r=next(x for x in records if x['source_id']==sid)
    manual += [f"### {sid} {r['title']}",'',f"作者：{r['author']}；书目年：{r['year']}；DOI：{r['doi']}。",'',f"[NUS代理入口]({r['nus_proxy']}) · [NUS题名检索]({r['nus_search']}) · [官方入口]({r['url']})",'',r['contribution'],'',r['locator'],'',r['limitation'],'']
manual += ['若你直接手动下载，可保存到本文件夹full-text/下，命名G06_Wang_Helen_1998.pdf或G10_Dotson_Doney_2025_chapter.pdf，告诉我完成即可；会先核对题名、页数和版本，再更新清单。G10需要第1章27–81页，不是第3章，也不是只有封面或目录。若只能下载全书也可，保留原文件即可。','',
'若NUS代理验证后仍无全文，不视为用户操作错误；可再核NUS其他平台或文献传递入口。本轮不代提交付费申请或向作者发送邮件。','',
'原刊PDF可后补：G08目前已有学术机构转载；不必为得到相同文本而立即重复下载。另一个2017年伯希和北京之行题名存在页码冲突，暂不进入核心清单。','']
(BASE/'待手动下载_NUS优先.md').write_text('\n'.join(manual))

(BASE/'文献对Gephi的修改建议.md').write_text('''# 文献对现有Gephi记录的具体用途

这是一份回查与修改建议，未修改既有工作簿、CSV、GEXF或地图。

## 1. 先回查KE006、KE007、KE008与PE001

G13b（合卷PDF106、章内2页）将1910年7月的编目备忘录／提议与1911年1月13日收到第一批材料分开记载，并列出Or.13114/1档案关系。可作为现有1910年检查、备忘录及有条件编目意向的补充研究依据。原信未由本轮查见，保留这一核验限制。

PE001原本属于待核记录，不在现有Gephi主图中。回查时要核对是否同一批次和同一行动，不将1911年收件日替换成1910年已完成事件；如研究范围维持1900–1910，将1911年作为后续说明。先保持EventID，并为提议、发出、收讫分别登记动作与日期，避免重复统计。

## 2. 用G13a检验“中介”编码

G13a（PDF24、章内1页）强调蒋孝琬代为交涉，并讨论斯坦因在中文护照中的称谓。可检查现有DH001、DH002的Role能否区分谈判、翻译／代拟与搬运；不同人物称谓需保存原词和规范姓名对应，不因称谓相近就合并主体。新的角色仍需对应具体文本证据。

## 3. 用G14补采行政通信关系

G14（原刊126–129页）可帮助梳理地方官、升允、清外务部和英方间不同的报送、指令、请求。文中存在“应、必定”等推断，须与引述的日记、电报分开；不据一条行政指令自动补出执行、交接或原物到达。相关官员若有充分证据，可作为具体主体登记，避免全部压成“清政府”一个角色。

## 4. 用L05第一节回应你的新问题

旧包L05（潘晟2025，134–137页）直接涉及斯坦因消息的传播。拆分取得时间、私人获知／通信时间、报刊时间、后出记述时间。“某文本未提到斯坦因”与“伯希和为斯坦因有意隐瞒”是不同性质的判断，后者需标明为谁的解释及所据证据，暂不自动生成conceals_for关系。

笔记所写“思裕如”可与潘文所写“恩裕如”进一步核对；该摄影案例涉及1912年，“天我”涉及1921年，均先作范围外比较。未自动改写原笔记。

## 5. 先定义分析子图，再用指标

G01用于写清关系判定规则；G03用于人物—事件参与子图的模型说明；G05提供信使等中介的论证案例。现有总图同时有主体、事件、物品、作品等类型，不能把全部节点的中心性排序直接当人物权力排序。先注明纳入哪些节点、关系、日期和状态；共同参与投影边也不能当作直接交往。G04与G02帮助解释资料缺失和图形选择。

这批方法文献不提供敦煌的新历史事实；几篇王冀青研究也可能共享档案线索，不等于多次独立证实。新角色和新边要回到可定位的历史材料。
''')

delta=[dict(old_id=x['old_id'],change='retained_reclassified',decision=x['decision'],reason=x['reason']) for x in old]
delta += [dict(old_id=r['source_id'],change='added' if r['status']=='present' else ('reused' if r['status']=='existing' else 'candidate_pending'),decision=r['priority'],reason=r['gephi']) for r in records]
write_table(BASE/'citation-delta.csv',['old_id','change','decision','reason'],delta,',',True)

bib=[]
for r in records:
    fields={'author':r['author'],'title':r['title'],'year':r['year']}
    typ=r['entry_type']
    if typ=='article':fields['journal']=r['venue']
    for k in ['volume','number','pages','publisher','isbn','editor','booktitle']:
        if r.get(k):fields[k]=r[k]
    if r['doi']:fields['doi']=r['doi']
    fields['url']=r['url']
    note=r.get('note','')
    if r['status']=='unavailable':note+=' 正文待取；本轮仅核题录／目录，不作为已读历史证据。'
    if note:fields['note']=note
    bib.append('@'+typ+'{'+r['source_id']+',\n'+''.join('  '+k+' = {'+str(v).replace('&','\\&')+'},\n' for k,v in fields.items())+'}\n')
(BASE/'references.bib').write_text('\n'.join(bib))
(BASE/'literature_data.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))

qc=[]
for p in sorted((BASE/'full-text').iterdir()):
    rec=dict(file=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    if p.suffix.lower()=='.pdf':
        d=fitz.open(p);rec.update(pages=len(d),extracted_chars=sum(len(pg.get_text()) for pg in d));assert len(d)>0 and rec['extracted_chars']>0
    else:
        rec['text_chars']=len(p.read_text());assert rec['text_chars']>1000
    qc.append(rec)
for r in records:
    if r['status']=='existing':assert Path(r['path']).is_file(), r['path']
assert len([r for r in records if r['status']!='unavailable'])==10
assert len(qc)==7
(BASE/'metadata/交付文件校验.json').write_text(json.dumps({'date':DATE,'new_full_text_files':len(qc),'readable_recommendation_entries':10,'pending_full_text_candidates':2,'files':qc,'old_files_modified':False},ensure_ascii=False,indent=2))
print('Package built:',BASE)
print('New full-text files:',len(qc),'Readable entries:',10,'Pending:',2,'Old-source decisions:',len(old))
