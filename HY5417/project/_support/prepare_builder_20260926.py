"""Migrate the archived workbook formatter to the data-driven catalogue."""
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
old=(BASE/'_support/archive/20260917/build_workbook.py').read_text()
body=old[old.index('def write_outputs():'):]
start=body.index(' data=dict('); end=body.index(' wb=Workbook()',start)
body=body[:start]+body[end:]
start=body.index(' intro=['); end=body.index(" core_rows=[]",start)
intro=''' intro=[
 ['本表内容','17项学术文献、20项一手／机构／辅助资料、6个数据库入口。','每条含用途、获取路径、核验层级及阅读记录；新增2024、2026研究各一篇。'],
 ['项目主线','不同主体如何在移民传统、本土化、旅游与城市变化中协商牛车水的遗产身份？','以Kreta Ayer和白新春为主；同时关注张力、合作与持续使用。'],
 ['阅读顺序','五篇核心 → 学术文献 → 综述比较矩阵 → 注释书目记录。','先读本地A07（牛车水）及A06（活态遗产），再获取其余全文。'],
 ['推荐五篇候选','A07＋A02＋A03＋A04＋A06：背景、旅游保护、身份呈现、茶贸易、活态遗产。','A02/A03需尝试机构获取；9月27日前确认全文，受限按替代方案调整。'],
 ['全文优先备选','A07＋A10＋A04＋A06＋A17。','A07/A06本地PDF；A10/A17公开HTML；A04整书入口需手动确认。A17为Blair Plain比较案例。'],
 ['10月2日范围','按用户说明：2026-10-02完成项目所需文献综述。','课程要求Annotated Bibliography：5 academic sources，2000 words，并有比较综合段；具体提交时刻未给出。'],
 ['其他作业','另有Research Essay 4000 words及Public History 2000 words或10分钟视频。','本次未获知这些作业的截止日期；不推定同为10月2日。中文“字”不等于英文words。'],
 ['资料性质','学术文献用于五篇评注；商户、官方、新闻及政策材料用于核实和分析。','P类不直接凑入五篇学术来源；A16原文首页／方法仍待核。'],
 ['核验与访问','本表更新日2026-09-26；未重新访问的旧记录保留9月17日核验日期。','公开获取不等于已下载或已精读；未登录NUS，也未确认单篇订阅。'],
 ['中文导读用途','辅助译名用于理解，正式引用用原题；导读用于选读与提问。','本表不是已完成的2000 words评注；方法、页码与批判性评价须读原文后填写。'],
 ['本地附件','fulltexts/有3个复核可读的PDF：A06、A07、P06。','本轮未新增下载；自动抓取失败的开放入口可用浏览器手动尝试。'],
 ['事实边界','年份、迁店原因、器物制造地、问卷代表性见“论证与核验”。','未读取原访谈录音、原问卷或全部照片；相关材料状态以项目大纲为依据。'],
 ['检索范围','中文与英文；出版社、机构库、NLB/NHB/URA、商户网页及原Crossref记录。','精选阅读地图，非穷尽系统综述；查询与失败记录在sources/保存。'],
 ['使用与备份','阅读状态有下拉菜单；个人笔记、评注空格用于记录自己的阅读。','原表及原脚本保存于_support/archive/20260917/；本表无宏。'],
 ]
 sheet('使用说明','HY5417｜牛车水项目文献与资料表','2026-09-26更新  ·  文献综述截止：2026-10-02  ·  17篇学术文献／20项资料／3个本地PDF',['项目','说明','使用提示'],intro,[24,85,90],freeze='B6',height=78)
'''
body=body[:start]+intro+body[end:]
body=body.replace("'五篇核心学术文献｜选择理由与对话关系'","'五篇核心候选｜按研究问题互相对读'")
body=body.replace("'推荐组合用于2000 words annotated bibliography；必须读原文后写摘要、评析和综合段。替代项已列明。'","'五篇以能实际读到全文为入选条件；公开获取备选组合A07＋A10＋A04＋A06＋A17，A04入口尚需手动确认。'")
body=body.replace("a['title'],role", "a['title']+'\\n【辅助中译】'+a['title_zh'],role")
body=body.replace("'学术文献｜15项可用研究与方法读物'","'学术文献｜17项研究与方法读物'")
body=body.replace("'按项目相关性排序；书目信息核验与全文阅读分开记录。P0推荐五篇；P1补充；P2选读。'","'P0核心候选、P1补充、P2选读；书目核验与全文阅读分开记录。中文题名仅辅助理解，正式引用使用原题。'")
body=body.replace("[a[k] for k in ['id','priority','theme','authors','year','title','citation','guide','use','locator','limit','access','verified','url','full','identifier','local']]+['未开始','',TODAY,a['trace']]", "[a[k] if k!='title' else a['title']+'\\n【辅助中译】'+a['title_zh'] for k in ['id','priority','theme','authors','year','title','citation','guide','use','locator','limit','access','verified','url','full','identifier','local']]+saved_notes.get(a['id'],['未开始',''])+[a['checked_date'],a['trace']]")
body=body.replace("['未开始','',TODAY,p['trace']]", "saved_notes.get(p['id'],['未开始',''])+[p['checked_date'],p['trace']]")
body=body.replace("sheet('公共史路线材料','Public History｜3–5站资料对应表','这是资料如何转化为公众叙事的建议；保持大纲的多声部原则。路线实际通行、店址、拍摄与引用许可需在田野中确认。'", "sheet('公共史路线材料','后续Public History｜3–5站资料对应表','保留后续项目可用材料；本次10月2日截止仅针对文献综述，未增加同期实地访问或公共史交付要求。'")
body=body.replace("'阅读与取材安排｜在10月2日前完成项目'","'9月26日—10月2日｜文献综述阅读与写作'")
body=body.replace("'按当前日期2026-09-17安排；阅读、补访和原型部分并行。9月30日形成可提交版本，10月1日留作缓冲。'","'仅安排文献综述／五篇评注及综合段；Research Essay和Public History截止日期未获确认，不推定同日完成。'")
body=body.replace("[entry['id']+f'.{n}',TODAY,", "[entry['id']+f'.{n}','2026-09-17',")
body=body.replace("[entry['id'],TODAY,", "[entry['id'],'2026-09-17',")
needle=" sheet('检索记录',"
addlog=''' for fname in ['refresh_20260926.json','refresh_metadata_20260926.json']:
  raw=json.loads((BASE/'sources'/fname).read_text()); entries=raw if isinstance(raw,list) else [dict(id='refresh_last6',data=raw)]
  for e in entries:
   z=e['data']
   if isinstance(z,dict) and z.get('status')=='fulfilled':z=z['value']
   args=z.get('args',{}) if isinstance(z,dict) else {}
   if e['id']=='refresh_search1':args={'search_query':[{'q':q} for q in ['"Reading landscape meanings" Yeoh Kong pdf','"The Dynamics of Trans-Regional Business and National Politics" pdf','"The Chineseness of Chinatown in Singapore" Chan','Singapore Chinatown heritage negotiation living heritage 2024 2025 academic']]}
   searchrows.append([e['id'],TODAY,'网页补检／来源复核',json.dumps(args,ensure_ascii=False),'精确题名、DOI及出版社／机构入口','部分覆盖；403、限流和验证页面均记录；无新增PDF',f'sources/{fname}','保留旧记录；不将摘要写成已读全文'])
'''
body=body.replace(needle,addlog+needle)
body=body.replace("'确切查询保存在本表及sources/web_search_log.json；搜索引擎未提供稳定总命中数，本表不虚构检索数量或声称穷尽。'","'原始查询在sources/；旧记录日期9月17日、本轮9月26日。无稳定总命中数，不虚构计数或声称穷尽。'")
extra=''' sheet('综述比较矩阵','从书目到综述｜按五个问题比较','这是文献对读和提问框架；每条的核验层级见学术文献表，不能替代原文阅读后的判断。',['编号','比较问题','关联文献','概念／方法','可比较什么','证据差异与边界','对应项目／资料','本项目可检验的问题','结论层级'],DATA['comparison'],[10,36,32,38,60,70,54,60,48],height=132)
 annotations=[]
 for id,*_ in CORE:
  a=next(x for x in acad if x['id']==id)
  row=[id,a['authors']+f" ({a['year']})",'','','','','','','',a['use'],a['url'],'未开始']
  if id in saved_annotations and len(saved_annotations[id])==len(row):row=saved_annotations[id]
  annotations.append(row)
 nws=sheet('注释书目记录','五篇评注记录｜精读后填写','可选分配：每篇约320 words，综合约300，引入约100，共约2000。只是工作建议，非老师新增规定；空白栏须据全文填写。',['编号','作者／年份','研究问题','材料与方法','核心论点','关键证据及页码','优点与局限','与另两篇的关系','我的评析／可引用表述','与本项目的联系','原文入口','完成状态'],annotations,[10,34,54,60,65,60,60,62,72,62,19,20],height=138)
 for row in nws.iter_rows(min_row=6,min_col=3,max_col=9):
  for c in row:
   if not c.value:c.fill=PatternFill('solid',fgColor='EAF4FA')
 dv=DataValidation(type='list',formula1='"未开始,已取得全文,阅读中,已做笔记,已引用,暂不使用"');nws.add_data_validation(dv);dv.add(f'L6:L{nws.max_row}')
 order=['使用说明','五篇核心','学术文献','一手与机构资料','综述比较矩阵','注释书目记录','论证与核验','资料库与检索','公共史路线材料','截止前安排','检索记录','筛选与缺口']
 wb._sheets=[wb[x] for x in order]
 # Fit row heights to wrapped content while retaining the existing visual system.
 for ws in wb:
  for row in ws.iter_rows(min_row=6):
   required=60
   for c in row:
    if c.value is None or c.coordinate in ws.merged_cells:continue
    width=ws.column_dimensions[c.column_letter].width or 20
    lines=sum(max(1,math.ceil(sum(2 if ord(ch)>255 else 1 for ch in line)/max(width-3,5))) for line in str(c.value).split('\\n'))
    required=max(required,lines*16+14)
   ws.row_dimensions[row[0].row].height=min(360,max(ws.row_dimensions[row[0].row].height or 0,required))
'''
body=body.replace(' # Link source IDs throughout the workbook to their source row.',extra+' # Link source IDs throughout the workbook to their source row.')
body=body.replace('Snapshot 2026-09-17.','Snapshot 2026-09-26; per-source verification dates retained; literature review due 2026-10-02.')
body=body.replace("  import fitz\n  doc=fitz.open(p)","  from pypdf import PdfReader\n  doc=PdfReader(p)\n  if not doc.pages[0].extract_text():errors.append('empty PDF first page '+p.name)")
body=body.replace('pages=len(doc),','pages=len(doc.pages),')
body=body.replace("qa=dict(status=", "qa=dict(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),deadline_scope=DATA['deadline_scope'],rendering='No Excel application render performed; saved workbook reopened and structurally checked.',status=")
body=body.replace("'Metadata and access levels audited; abstract-only sources remain explicitly marked. Not a full-text review of every item.'", "'Metadata/access levels audited, old verification dates retained. A16 author first page and full methods pending. No new PDF downloads; 3 existing PDFs rechecked. Not a full-text review of every item.'")
prefix=old[:old.index("BASE=Path")]+'''BASE=Path(__file__).resolve().parents[1]
DATA=json.loads((BASE/'_support/catalogue.json').read_text())
TODAY=DATA['date']
acad=DATA['academic']; primary=DATA['primary']; CORE=DATA['core']; EVIDENCE=DATA['evidence']; DATABASES=DATA['databases']; STATIONS=DATA['stations']; SCHEDULE=DATA['schedule']; EXCLUSIONS=DATA['exclusions']
saved_notes={}; saved_annotations={}
oldpath=BASE/'HY5417_牛车水项目_文献与资料总表.xlsx'
if oldpath.exists():
 oldbook=load_workbook(oldpath)
 for name in ['学术文献','一手与机构资料']:
  if name not in oldbook:continue
  ws=oldbook[name];cols={c.value:c.column for c in ws[5]}
  for row in ws.iter_rows(min_row=6):
   if row[0].value:saved_notes[row[0].value]=[ws.cell(row[0].row,cols[k]).value for k in ['阅读状态','个人笔记']]
 if '注释书目记录' in oldbook:
  for row in oldbook['注释书目记录'].iter_rows(min_row=6,values_only=True):
   if row[0]:saved_annotations[row[0]]=list(row)

'''
(BASE/'_support/build_workbook.py').write_text(prefix+body)
print('Data-driven workbook formatter prepared.')
