"""Create reader-facing catalogues for the 2026-09-22 source collection."""
from pathlib import Path
import csv, json, hashlib
B=Path(__file__).resolve().parents[1]
def csvout(name, fields, rows):
    with (B/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

rows=[]
def source(sid,author,year,title,pub,url,path,status,use,limits,locator,doi=''):
    p=B/path if path else None
    rows.append(dict(SourceID=sid,作者=author,出版日期=year,题名=title,出处与版本=pub,URL=url,DOI=doi,访问或本地核对日期='2026-09-22',本地路径=path,获取状态=status,本周用途=use,优先定位=locator,限制与依赖=limits,SHA256=hashlib.sha256(p.read_bytes()).hexdigest() if p and p.exists() else ''))
source('S01','Mélodie Doumy','2025',"Wang Yuanlu, the first ‘curator’ of the Stein collection’s Dunhuang corpus",'JRAS 35:821–845；现有正式版','https://doi.org/10.1017/S1356186325000161','../wang-yuanlu-the-first-curator-of-the-stein-collections-dunhuang-corpus.pdf','复用现有全文','E001保管与控制进入；北京补证入口','S02为同篇AAM，不是独立研究；其引述Stein的部分不算独立目击佐证','印刷821、825页＝PDF1、5页','10.1017/S1356186325000161')
source('S03','Paschalia Terzi; Susan Whitfield','2024','Reconstructing a Medieval Library?','Silk Roads Archaeology and Heritage 1(1):56–76；现有正式版','https://doi.org/10.5334/srah.8','../Terzi_Whitfield_2024_Reconstructing_a_Medieval_Library_Dunhuang.pdf','复用现有全文','E002、E005、E006取得批次；E003角色；E004/E007拆箱与编号','日记和书信原件本轮未取得；转引有日数与数量差异；不可把全部论述视为与Stein独立','印刷60、63–64、73页＝PDF5、8–9、18页','10.5334/srah.8')
source('S07','M. Aurel Stein','1921','Serindia, vol. II：审计关键页','Oxford: Clarendon Press；NII/东洋文库原书扫描；本地合成6页摘录','https://dsr.nii.ac.jp/toyobunko/VIII-5-B2-9/V-2/','full-text/S07_Serindia_审计关键页_823-825_829-830_916.pdf','本轮补充原页扫描','E002–E009原始措辞与上下文','全卷没有重新下载；作者的北京叙述来自1914年回访所得消息，不是1910年北京接收目击；扫描无OCR层','本地PDF1–6依次为印刷823、824、825、829、830、916页','10.20676/00000183')
source('S11','孙利平；林世田','未核定','中国国家图书馆敦煌文献数字化与国际敦煌学项目','国家图书馆官网托管PDF；6页','https://www.nlc.cn/upload/attachments/2023-01-31/7f8581ea.pdf','full-text/S11_NLC_敦煌文献数字化.pdf','新增全文','E008/E009：1910年运京与京师图书馆的机构说明','回顾性机构文章；URL上传日期不是出版日期；下载时暂拟2005已撤销','PDF1页末—2页首')
source('S12','林世田','2020-03-23','缪荃孙逝世100周年|林世田：缪荃孙先生对敦煌遗书编目有首创之功','国家古籍保护中心网页；正文快照','https://www.nlc.cn/pcab/zx/xw/20200416_191121.shtml','full-text/S12_NLC_2020_敦煌整理与编目.html','新增正文快照','E009：接收机构和早期编目角色','回顾性讲述；网页路径日期与页面刊载日期不同；后续1911年以后事迹只作背景','首个正文长段；检索“京师图书馆刚接手”')
source('S13','刘波','2025-04-28','《中国国家图书馆藏敦煌文献》的整理与出版','国家古籍保护中心转载整理出版文章；正文快照','https://www.nlc.cn/pcab/zx/xw/20250423_2644574.shtml','full-text/S13_NLC_2025_馆藏敦煌文献.html','新增正文快照','E009：1910年运京部分与后续入藏的边界','16516是该文所述现存编号数；不可作为1910年运输件数；机构回顾不能替代接收原件','一、国图敦煌文献整理概况；开头来源构成段')
source('S15','Nathalie Monnet','未标明','Paul Pelliot (1878–1945) et Dunhuang','BnF France–Chine专题；署名机构文章；正文快照','https://heritage.bnf.fr/france-chine/paul-pelliot-1878-1945-et-dunhuang','full-text/S15_BnF_Pelliot_Dunhuang.html','新增正文快照','第二周预备：巴黎接收机构与文献/艺术品分流','回顾性机构说明；没有取得正式交接凭证；30 000 fascicules是另购印本，不是敦煌写卷数','正文检索“arrivèrent à Paris à la fin de 1909”')
source('S17','Michelle Wang; Xin Wen; Susan Whitfield','2020','Buddhism and Silk: Reassessing a Painted Banner from Medieval Central Asia in the Metropolitan Museum of Art','Metropolitan Museum Journal 55:8–25；UEA存储的27页AAM','https://ueaeprints.uea.ac.uk/id/eprint/76988/1/Accepted_Manuscript.pdf','full-text/S17_Whitfield_Buddhism_and_Silk_AAM.pdf','新增全文（AAM）','E004/E007：1909年到英、整理与正式入藏的区分','采用AAM页码，不冒充期刊印刷页；关键档案MSS. Stein 7/81–2未独立取得；本文旗幡路径本身是probable','AAM/PDF16页；20页注61；metadata另存','10.1086/712767')
source('S19','方广锠','2009','百年前的一桩公案——关于22卷续交敦煌遗书的考察','《敦煌研究》2009(1):64–73；佛教导航2010-12-13转载正文','https://www.fjdh.cn/wumin/2010/12/071837135094.html','full-text/S19_Fang_2009_百年前的一桩公案_转载.html','新增转载正文；原刊未取得','E008/E009：学部行文、京师图书馆接收底账录文','不是档案原件影像；存在疑似转录字误；原日期保留清代纪年，月日未换算公历；分析与档案录文须分开','一、档案录文（一）（二）；二、历史探秘之呈样和两次调拨')
source('S20','Helen Wang; John Perkins (eds.)','2008','Handbook to the Collections of Sir Aurel Stein in the UK','British Museum；第2修订版；ISBN 9780861599776；机构仓储PDF','https://real.mtak.hu/169501/1/Wang__Stein_handbook_for_web.pdf','full-text/S20_Stein_Handbook_2008.pdf','新增全文','E004/E007及E006：后续查档入口与档案号','档案指南不是交接证据；2008年阅览规则不能当作现行规则；旧CE32编号需按其说明追查','印刷9页＝PDF15页；印刷29页＝PDF35页')
source('S21','阮靜玲；錢月蓮','2015-10-15','敦煌文書調查與研究：以北京國家圖書館為例','台湾国家图书馆出国考察报告；62页','https://nclfile.ncl.edu.tw/nclhistory/public/Data/5102716244471.pdf','full-text/S21_NCL_敦煌文献调查报告.pdf','新增全文','E009：中国机构研究及北京馆藏资料线索','发布机构是台湾国家图书馆，考察对象是北京国家图书馆；两次调拨叙述与S19重合，不视为另一份独立接收记录；月日历法待核','印刷10–11页＝PDF14–15页；调查清单供后续选对象')
source('S22','Paul Pelliot','1910','Trois ans dans la haute Asie','Paris: Comité de l’Asie française；1909-12-10索邦演讲；1910年1月会刊抽印本；NII/东洋文库扫描','https://dsr.nii.ac.jp/toyobunko/VIII-5-B2-12/','full-text/S22_Pelliot_1910_Trois_ans_完整扫描.pdf','新增完整扫描；28幅合成PDF','第二周预备：现场选择、王圆箓角色、同行带回收藏与北京展示','与S08（1908年BEFEO文章）是两项不同作品；参与者自述；不直接证明法国机构正式入藏；无OCR层；只精读相关页','PDF5题名页；PDF19–21＝印刷13–15页','10.20676/00000241')
for args in [
 ('S08','Paul Pelliot','1908','Une bibliothèque médiévale retrouvée au Kan-sou','BEFEO 8:501–529；Persée入口','https://www.persee.fr/doc/befeo_0336-1519_1908_num_8_1_4297','sources/metadata/S08_Pelliot_1908_Persee.html','仅元数据；正文未取得','Pelliot路线后续补证','HTML只有元数据/在线阅读器；Penn PDF超时；不能将此文件计作全文','原文501–529页待取得','10.3406/befeo.1908.4297'),
 ('S14','British Museum','未核定','Exploring the Silk Roads','博物馆官网入口','https://www.britishmuseum.org/collection/china/exploring-silk-roads','','未取得正文：HTTP403','伦敦路线发现线索','只保留检索记录；不进入事件证据表','待访问',''),
 ('S16','INHA / AGORHA','未核定','Paul Pelliot收藏史条目（入口）','机构数据库；访问返回维护页','https://agorha.inha.fr/ark:/54721/85f38a16-31af-4757-8f53-eb7371821cb0','','访问失败：维护页','法国接收日期后续线索','HTTP成功不等于正文可用；检索缓存中的具体日期未提升为核验事实；2026-10-27已清理维护页本体，失败状态日志保留','sources/download_batch1_results.json中的失败入口记录；无可用正文',''),
 ('S18','Wang; Persson; Wood','2012（下载入口所对应版本待核）','Dunhuang Textiles in London: A History of the Collection','British Museum论文入口','https://www.britishmuseum.org/pdf/19_Wang-Persson-Wood.pdf','','未取得正文：HTTP403','伦敦纺织品整理史补证入口','有不同版本线索；不据检索摘要下事件结论','待取得PDF',''),
 ('S23','第三方期刊目录平台','2009期刊目录','《敦煌研究》2009年第1期目录入口','Oriprobe目录；只用于S19书目信息发现','https://caod.oriprobe.com/issues/507132/toc.htm','','未取得页面：HTTP403','书目辅助，不作为历史证据','原刊页码由S19文章编码及期刊目录检索线索核对；正式刊页仍待取得','检索记录',''),
 ('S24','Helen Wang','2004','Catalogue of the Sir Aurel Stein Papers in the British Museum Central Archives','档案目录下载线索；题名依S20印刷9页参考文献；原文37–62页','https://www.britishmuseum.org/pdf/Stein%20Wang.pdf','','未取得正文：HTTP403','旧CE32档案号后续核查','先使用已取得的2008年手册定位；不能称为档案原件已读；S20内部系列号有142/129不一致，原刊待核','待取得PDF','')
]:source(*args)
csvout('资料目录.csv',list(rows[0]),rows)
byid={r['SourceID']:r for r in rows}

ev=[]
def evidence(event,sid,where,fact,kind,limit,action):
    ev.append(dict(证据编号='W1-%02d'%(len(ev)+1),EventId=event,SourceID=sid,定位=where,中文转述=fact,证据性质=kind,尚不能证明=limit,建议审计动作=action,本地来源=byid[sid]['本地路径']))
evidence('E001','S01','印刷821、825页；PDF1、5页','1900年发现；1904年保管安排；1907年王持钥匙控制进入','研究综合；含日记及早期报告转引','保管关系不等同法律所有权；1907不自动代表保管结束','区分来源地点与保管者；说明1900–1907是试点截取区间还是事件持续期')
evidence('E001','S22','印刷13页；PDF19页','伯希和记述王前来开洞，并在王顾虑下安排洞内查看','参与者自述；跨路线的后续观察','1908观察不能精确证明1900年的制度状态','作为王控制进入的补充材料；不把洞窟作为先前持有人')
evidence('E002','S07','印刷824页末agreement段；摘录PDF2页','协议列50捆中文及5捆藏文卷子，并另提混合捆中的选择物','参与者事后出版叙述','55捆不是此次全部取得物的精确总数；捆不等于卷','保留55的计量口径；混合捆选择物另说明，不相加为手稿件数')
evidence('E002','S03','印刷60页Ac1分项；73页注25；PDF5、18页','作者分解取得阶段；不同报告、日记与后出书籍的装箱及捆数并不一致','研究者比对早期记录；原档案未独立取得','不支持用后出总数重新拼出每一天的精确数量','逐一核对Ac1分项；保留版本与数量差异')
evidence('E003','S07','印刷824末—825首；摘录PDF2–3页','蒋与Ibrahim Beg、Tila Bai协助两次夜间搬运至Stein库房','参与者叙述','协助运输不证明蒋个人先持有整批材料','将蒋记录为参与者/翻译/搬运协调角色；审查N004→N006是否符合保管者网络定义')
evidence('E003','S03','印刷63页；PDF8页','和田阶段蒋参与手稿编号，1908年6–7月另有编目活动','研究者据日记和编号材料重建','编号活动不等于1907年所有权或保管权转移','把1907搬运与1908编号分开记录；不要为了显示中介角色制造转移边')
for event in ['E004','E007']:
    evidence(event,'S07','印刷825页第三段末；摘录PDF3页','作者在回顾取得批次之后，总括24箱手稿及另5箱艺术品已存入British Museum','参与者回顾；两行现用同一段','该段未证明两次独立入馆，也未明确到馆日或正式入藏日','与另一条作为同一疑似重复组；合并前保留旧ID映射；24箱和5箱类别分清')
    evidence(event,'S03','印刷64页；PDF9页','记载1908年和田装箱及1909年开始拆箱','档案研究转引','装箱、拆箱、抵达和正式入藏并非同一时点','撤销仅据825页推定1907–1908入馆的理由；分别记录日期依据')
    evidence(event,'S17','AAM/PDF16页；20页注61','论文称材料1909年抵英并由Andrews整理；注61指出所述阶段尚未正式纳入任何馆藏','研究者依据书信重建；MSS. Stein 7/81–2原件待核','1909抵英不能自动落实到某一天的BM接收；也不等于正式入藏或所有权','可作1909到英候选依据；将physical deposit与formal accession分开；查原书信')
    evidence(event,'S07','印刷916页；摘录PDF6页','1910年初夏Pelliot来伦敦检查材料；1910年秋部分材料送巴黎编目','参与者叙述；后续使用情境','此处巴黎移动不是Pelliot自己1908年取得批次的初次入藏','作为在伦敦已有材料的时序补证；避免与伯希和取得路线混合')
evidence('E005','S07','印刷825页第二段；摘录PDF3页','约一周后追加约20捆中文材料及混合捆选择物','参与者后出叙述','不保证与日记记数一致；不是另一次博物馆接收','与E002区分取得阶段；保留约数和混合材料范围')
evidence('E005','S03','印刷60页Ac1c及73页注24；PDF5、18页','研究转引日记13捆，指出1912和1921年的叙述作20捆','版本差异；日记原件MSS Stein 204/339待取得','不能从13与20中无理由选择一个作为精确事实','给Quantity增加版本依据及冲突备注；把日记直接核查列入后续')
evidence('E006','S07','印刷825页第三段；摘录PDF3页','安西追加取得描述为230余捆','参与者后出叙述','不能给230设置精确件数；本段不支持具体公历日','保留捆为单位及约数；与55、20捆阶段分别审核')
evidence('E006','S03','印刷60页Ac2、73页注26；PDF5、18页','Ac2标题为1907年10月1日；注26并列220/230捆说法及10月5日日记所记前夜到达','存在日期与数量差异的研究转引','10月1日与10月4日不能未经核对便视为同一时点或两个新事件','分别记录文书/日记所称行为与日期，日精度暂不定；查MSS Stein 205/94–5、37/104及CE32/23/16/2')
evidence('E008','S07','印刷829页下部—830页首；摘录PDF4–5页','Stein记中央命令运京，并叙述1914回访所听到的运输情况','命令叙述及后得消息；不是北京接收目击','运京命令不直接证明王→抽象中央政府的一次实物交接；作者也未核定实际到京量','分开命令事件、运输过程与接收；保留1909/1910叙述差异')
evidence('E008','S11','PDF1页末—2页首','机构文章称1910年清学部令甘肃将残卷运京，移藏京师图书馆','后出机构概述','没有载明具体交接人、凭证和公历日','把学部、甘肃经手机构、京师图书馆区分；不得补出未知运输节点')
evidence('E008','S19','一、档案录文（一）学部行文','录文追述此前18箱已由收文馆派员取运，并列续送写经及样本','研究文章转载中的档案转录','原档案影像未取得；不直接证明王本人如何交出；续送不是主批首次运输','用于追查实际拨送层级；与E009相接的事件须重新定义')
evidence('E009','S19','一、档案录文（一）（二）','所录学部文件日期为宣统二年十一月十二日；接收底账为宣统[二]年[十一]月[十四]日，续送22卷及粘片2本','档案转录；原件未核','月日未换算公历；不得写作1910-11-12/14；此前18箱的精确接收时间未知','具体接收机构可推进为京师图书馆；主批与续交分开；日期保留原文及历法待核状态')
evidence('E009','S11','PDF1–2页','文章区分1910年运京主体与后续购买、捐赠等来源','机构回顾','现代馆藏总数不等于1910年运到数量','落实历史馆名，保持批次边界')
evidence('E009','S12','首个正文长段；检索“京师图书馆刚接手”','京师图书馆接手后组织整理编目，文章说明缪荃孙、沈曾植、李翊灼相关角色','机构发布的回顾性讲述','回顾不是1910接收登记原件；编目完成年不能当接收年','作为接收后管理的旁证；角色另列，不制造多次移交')
evidence('E009','S13','一、国图敦煌文献整理概况开头','将1910年甘肃解运部分与新字号等后续入藏部分区分','机构整理出版说明','现藏16516号不是当年接收件数；残片编号可能随整理变化','禁止把现代总数写入历史运输数量；以后按对象号核对')
evidence('E009','S21','印刷10–11页；PDF14–15页','报告转述18箱及续交批次，并使用现代年/月/日写法','后出考察报告；与S19相关叙述重合','重复叙述不构成另一份独立接收原件；不能解决原月日历法','只作导航与语境，日期返回S19录文和原档案核查')
csvout('事件证据对照.csv',list(ev[0]),ev)

search=[]
purposes={1:'北京运京、伦敦到馆、法国接收入口',2:'沿引用查中文档案和伦敦整理史；最初检索作者联想为荣新江，后核实S19作者为方广锠',3:'中文原刊PDF、Stein档案目录和法国机构记录',4:'具体档案号与方广锠原刊；机构扫描库入口',5:'Stein具体页码及中文原刊继续检索',6:'机构全文与Pelliot1910扫描库',7:'核对书目及中文录文线索',8:'核对1910报告机构题录',9:'核对卷级扫描入口与中文PDF'}
for p in sorted((B/'sources').glob('search_*.json')):
    d=json.loads(p.read_text());q=d['query'];n=int(p.stem.split('_')[1])
    for mode in ['search_query','open','find']:
        for item in q.get(mode,[]):search.append({'批次':n,'日期':'2026-09-22','后端':'内置web工具','动作':mode,'查询或入口':json.dumps(item,ensure_ascii=False),'目的与修正':purposes[n],'原始记录':str(p.relative_to(B))})
csvout('检索记录.csv',list(search[0]),search)
screen=[{'SourceID':r['SourceID'],'决定':'纳入阅读包' if r['SourceID'] in ['S01','S03','S07','S11','S12','S13','S15','S17','S19','S20','S21','S22'] else '保留入口；不作已读正文','获取状态':r['获取状态'],'用途':r['本周用途'],'原因及限制':r['限制与依赖']} for r in rows]
csvout('筛选与缺口.csv',list(screen[0]),screen)
print(json.dumps({'catalogue_entries':len(rows),'new_works':9,'reader_files':len(list((B/'full-text').iterdir())),'evidence_rows':len(ev),'covered_events':sorted(set(r['EventId'] for r in ev)),'search_actions':len(search)},ensure_ascii=False,indent=2))
