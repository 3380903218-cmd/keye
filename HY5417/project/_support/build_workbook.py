from pathlib import Path
import json, re, datetime, math, hashlib
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.hyperlink import Hyperlink

BASE=Path(__file__).resolve().parents[1]
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

def write_outputs():
 wb=Workbook(); wb.remove(wb.active)
 navy='183C4A'; teal='157A7C'; light='E8F3F3'; gold='E9B44C'; textc='223640'; gray='F1F4F6'
 default_font='PingFang SC'
 tables=[]
 def sheet(name,title,subtitle,headers,rows,widths,freeze='D6',height=94):
  ws=wb.create_sheet(name);ws.sheet_view.showGridLines=False;ws.sheet_view.zoomScale=85
  n=len(headers)
  ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=n);ws.cell(1,1,title)
  ws.cell(1,1).font=Font(name=default_font,size=20,bold=True,color='FFFFFF');ws.cell(1,1).fill=PatternFill('solid',fgColor=navy);ws.cell(1,1).alignment=Alignment(vertical='center')
  ws.row_dimensions[1].height=40
  ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=n);ws.cell(2,1,subtitle);ws.cell(2,1).font=Font(name=default_font,size=11,color='566870');ws.cell(2,1).alignment=Alignment(wrap_text=True,vertical='center');ws.row_dimensions[2].height=36
  ws.cell(3,1,'↩ 使用说明');ws.cell(3,1).hyperlink="#'使用说明'!A1";ws.cell(3,1).font=Font(name=default_font,size=10,color=teal,underline='single')
  for j,h in enumerate(headers,1):
   c=ws.cell(5,j,h);c.font=Font(name=default_font,bold=True,color='FFFFFF',size=11);c.fill=PatternFill('solid',fgColor=teal);c.alignment=Alignment(wrap_text=True,vertical='center')
  ws.row_dimensions[5].height=31
  for i,row in enumerate(rows,6):
   for j,v in enumerate(row,1):
    c=ws.cell(i,j,v);c.font=Font(name=default_font,size=11,color=textc);c.alignment=Alignment(wrap_text=True,vertical='top');c.fill=PatternFill('solid',fgColor='FFFFFF' if i%2==0 else gray)
    if j==1:c.font=Font(name=default_font,size=11,bold=True,color=teal)
    if isinstance(v,str) and v.startswith(('https://','http://')):
     c.hyperlink=v;c.value='打开链接 ↗';c.font=Font(name=default_font,size=11,color='0563C1',underline='single')
    if isinstance(v,str) and v.startswith('fulltexts/') and v.endswith('.pdf'):
     c.hyperlink=v;c.value='打开本地PDF ↗';c.font=Font(name=default_font,size=11,color='0563C1',underline='single')
   ws.row_dimensions[i].height=height
  for j,w in enumerate(widths,1):ws.column_dimensions[get_column_letter(j)].width=w
  ws.freeze_panes=freeze
  if rows:
   tab=Table(displayName='T'+str(len(tables)+1),ref=f'A5:{get_column_letter(n)}{5+len(rows)}');tab.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showFirstColumn=False,showLastColumn=False,showRowStripes=False,showColumnStripes=False);ws.add_table(tab);tables.append(tab)
  ws.sheet_properties.pageSetUpPr.fitToPage=True
  ws.page_setup.orientation='landscape';ws.page_setup.paperSize=ws.PAPERSIZE_A3;ws.page_setup.fitToWidth=1;ws.page_setup.fitToHeight=0
  ws.print_title_rows='1:5';ws.print_options.horizontalCentered=False
  ws.oddFooter.center.text='HY5417 | 牛车水资料地图 | &P / &N';ws.oddFooter.right.text=TODAY
  ws.sheet_properties.tabColor=teal
  return ws

 intro=[
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
 sheet('使用说明','HY5417｜牛车水项目文献与资料表','2026-09-27下载状态更新  ·  文献综述截止：2026-10-02  ·  五篇核心：2篇本地／3篇待手动下载',['项目','说明','使用提示'],intro,[24,85,90],freeze='B6',height=78)
 core_rows=[]
 for id,role,why,dialogue,fallback in CORE:
  a=next(x for x in acad if x['id']==id);core_rows.append([id,a['authors']+' ('+str(a['year'])+')',a['title']+'\n【辅助中译】'+a['title_zh'],role,why,dialogue,a['access'],fallback,a['url']])
 ws=sheet('五篇核心','五篇核心候选｜按研究问题互相对读','五篇以能实际读到全文为入选条件；公开获取备选组合A07＋A10＋A04＋A06＋A17，A04入口尚需手动确认。', ['编号','作者／年份','原题','承担角色','为什么选它','与其他材料怎样对话','当前访问情况','获取受限时的替代','来源'],core_rows,[9,27,55,28,47,50,36,50,18],height=128)
 # Add a compact synthesis planning row outside the filtered table.
 r=13;ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=9)
 ws.cell(r,1,'综合段写作问题：景观中的意义由谁赋予？旅游开发选择了哪些“华人性”？茶贸易与本地实践如何使传统持续改变？五篇在尺度、年代、材料与解释权上有何不同？先比较证据，再给出你的有限结论。');ws.cell(r,1).font=Font(name=default_font,size=12,bold=True,color=navy);ws.cell(r,1).alignment=Alignment(wrap_text=True,vertical='center');ws.cell(r,1).fill=PatternFill('solid',fgColor=light);ws.row_dimensions[r].height=65

 ah=['编号','优先级','主题','作者','年份','文献原题','完整书目信息','中文导读','对应项目用途','优先阅读位置','使用边界／待核事项','访问状态','本次核验层级','出处／记录','全文／替代入口','DOI／ISBN','本地全文','阅读状态','个人笔记','核验日期','检索记录']
 ar=[[a[k] if k!='title' else a['title']+'\n【辅助中译】'+a['title_zh'] for k in ['id','priority','theme','authors','year','title','citation','guide','use','locator','limit','access','verified','url','full','identifier','local']]+saved_notes.get(a['id'],['未开始',''])+[a['checked_date'],a['trace']] for a in acad]
 aws=sheet('学术文献','学术文献｜17项研究与方法读物','P0核心候选、P1补充、P2选读；书目核验与全文阅读分开记录。中文题名仅辅助理解，正式引用使用原题。',ah,ar,[9,18,24,29,11,58,65,50,50,45,52,38,35,18,19,38,20,18,42,15,35],height=148)
 ph=['编号','优先级','材料类别','作者／机构','日期／年份','资料名称','可用内容','项目用途','证据定位','使用边界／待核事项','访问状态','本次核验层级','来源','替代／相关入口','本地全文','阅读状态','个人笔记','核验日期','检索记录']
 pr=[[p[k] for k in ['id','priority','kind','authors','year','title','guide','use','locator','limit','access','verified','url','full','local']]+saved_notes.get(p['id'],['未开始',''])+[p['checked_date'],p['trace']] for p in primary]
 pws=sheet('一手与机构资料','一手、机构与辅助资料｜20项有明确用途的材料','这里的商户自述、官方文本、新闻及灰色文献不能直接替代五篇学术文献；旧链接与未核原稿已单独标识。',ph,pr,[9,18,27,38,24,60,52,49,48,55,43,36,18,19,20,18,42,15,35],height=140)
 for ws,statuscol in [(aws,18),(pws,16)]:
  dv=DataValidation(type='list',formula1='"未开始,已取得全文,阅读中,已做笔记,已引用,暂不使用"');dv.errorTitle='请选择阅读状态';dv.error='请从列表选择，也可在个人笔记中补充原因。';dv.showErrorMessage=True;ws.add_data_validation(dv);dv.add(f'{get_column_letter(statuscol)}6:{get_column_letter(statuscol)}{ws.max_row}')
  ws.conditional_formatting.add(f'{get_column_letter(statuscol)}6:{get_column_letter(statuscol)}{ws.max_row}',FormulaRule(formula=[f'{get_column_letter(statuscol)}6="已引用"'],fill=PatternFill('solid',fgColor='D9EEDC')))

 sheet('论证与核验','论证与事实核验｜哪些能说、哪些还需要补证','每行把具体主张、材料定位和下一步连起来；“已核”仅指所标层级，不代表对所有相关史实完成独立验证。', ['核验编号','问题／拟用主张','当前证据状态','关联资料','具体定位','目前能支持什么','证据方向','放入哪部分','下一步与推荐措辞'],EVIDENCE,[10,45,37,25,48,58,28,28,61],height=126)
 sheet('资料库与检索','资料库与检索入口｜6条后续查证路线','入口不是已完成的档案检索；先解决白新春迁址、同期争论与可复用图片这几项具体问题。', ['编号','资料库／入口','能找什么','可直接复制的检索词／办法','入口链接','帮助／线索链接','本次验证与访问限制','取得后应记录'],DATABASES,[10,42,36,72,18,18,59,54],height=119)
 sheet('公共史路线材料','后续Public History｜3–5站资料对应表','保留后续项目可用材料；本次10月2日截止仅针对文献综述，未增加同期实地访问或公共史交付要求。', ['站点','位置','关联资料','这一站研究什么','可并置的材料','尚需补充','可给公众的开放问题'],STATIONS,[10,42,37,45,57,61,58],height=116)
 schedule_rows=[[datetime.date.fromisoformat(r[0]),datetime.date.fromisoformat(r[1])]+r[2:]+['未开始'] for r in SCHEDULE]
 sws=sheet('截止前安排','9月26日—10月2日｜文献综述阅读与写作','仅安排文献综述／五篇评注及综合段；Research Essay和Public History截止日期未获确认，不推定同日完成。', ['开始','结束','阶段','具体行动','应产出','所用资料','注意事项','完成状态'],schedule_rows,[16,16,32,78,60,40,64,18],freeze='D6',height=88)
 for row in sws.iter_rows(min_row=6,max_row=sws.max_row,min_col=1,max_col=2):
  for c in row:c.number_format='yyyy-mm-dd'
 dv=DataValidation(type='list',formula1='"未开始,进行中,已完成,需调整"');sws.add_data_validation(dv);dv.add(f'H6:H{sws.max_row}')
 log=json.loads((BASE/'sources/web_search_log.json').read_text()) if (BASE/'sources/web_search_log.json').exists() else []
 if (BASE/'sources/final_metadata_query.json').exists(): log.append(json.loads((BASE/'sources/final_metadata_query.json').read_text()))
 searchrows=[]
 for entry in log:
  args=entry['args']; queries=args.get('search_query',[])
  for n,q in enumerate(queries,1):
   searchrows.append([entry['id']+f'.{n}','2026-09-17','公开网页搜索',q['q'],'; '.join(q.get('domains',[])) or '未限制域名','部分覆盖：仅返回可见排名结果，无总命中数与完整分页','sources/final_metadata_query.json' if entry['id']=='S11' else 'sources/web_search_log.json', '用于发现，原文／机构记录另核'])
  if not queries:
   ops=[]
   for op in ['open','click','find']:
    for x in args.get(op,[]):ops.append(op+': '+str(x))
   searchrows.append([entry['id'],'2026-09-17','页面／原文核验','\n'.join(ops),'已发现的具体来源','部分页面抓取失败或仅返回摘要；逐条状态见目录','sources/web_search_log.json','直接阅读与失败记录均保留'])
 for fname in ['refresh_20260926.json','refresh_metadata_20260926.json']:
  raw=json.loads((BASE/'sources'/fname).read_text()); entries=raw if isinstance(raw,list) else [dict(id='refresh_last6',data=raw)]
  for e in entries:
   z=e['data']
   if isinstance(z,dict) and z.get('status')=='fulfilled':z=z['value']
   args=z.get('args',{}) if isinstance(z,dict) else {}
   if e['id']=='refresh_search1':args={'search_query':[{'q':q} for q in ['"Reading landscape meanings" Yeoh Kong pdf','"The Dynamics of Trans-Regional Business and National Politics" pdf','"The Chineseness of Chinatown in Singapore" Chan','Singapore Chinatown heritage negotiation living heritage 2024 2025 academic']]}
   searchrows.append([e['id'],TODAY,'网页补检／来源复核',json.dumps(args,ensure_ascii=False),'精确题名、DOI及出版社／机构入口','部分覆盖；403、限流和验证页面均记录；无新增PDF',f'sources/{fname}','保留旧记录；不将摘要写成已读全文'])
 sheet('检索记录','检索边界与核验记录','原始查询在sources/；旧记录日期9月17日、本轮9月26日。无稳定总命中数，不虚构计数或声称穷尽。', ['批次','日期','渠道','原始检索式／操作','域名／范围','完成边界','本地记录','用途'],searchrows,[12,16,25,100,58,56,43,39],height=80)
 sheet('筛选与缺口','筛选决定与剩余缺口','为10月2日截止控制阅读量；保留不利或相反材料，排除未经核验的泛化信息。', ['编号','候选／问题','处理','理由／后续'],EXCLUSIONS,[10,78,44,100],freeze='B6',height=77)
 sheet('综述比较矩阵','从书目到综述｜按五个问题比较','这是文献对读和提问框架；每条的核验层级见学术文献表，不能替代原文阅读后的判断。',['编号','比较问题','关联文献','概念／方法','可比较什么','证据差异与边界','对应项目／资料','本项目可检验的问题','结论层级'],DATA['comparison'],[10,36,32,38,60,70,54,60,48],height=132)
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
 if DATA.get('downloads'):
  sheet('核心下载状态','五篇核心文献｜下载清单','2026-09-27：2篇本地全文已复核；3篇需手动操作。',['编号','文献','下载结果','本地PDF','需要你的操作','直接网站','NUS代理／备用入口','建议保存文件名','检查日期'],DATA['downloads'],[10,63,21,22,94,21,25,69,18],height=130)
  order.insert(1,'核心下载状态')
 wb._sheets=[wb[x] for x in order]
 # Fit row heights to wrapped content while retaining the existing visual system.
 for ws in wb:
  for row in ws.iter_rows(min_row=6):
   required=60
   for c in row:
    if c.value is None or c.coordinate in ws.merged_cells:continue
    width=ws.column_dimensions[c.column_letter].width or 20
    lines=sum(max(1,math.ceil(sum(2 if ord(ch)>255 else 1 for ch in line)/max(width-3,5))) for line in str(c.value).split('\n'))
    required=max(required,lines*16+14)
   ws.row_dimensions[row[0].row].height=min(360,max(ws.row_dimensions[row[0].row].height or 0,required))
 # Link source IDs throughout the workbook to their source row.
 locations={a['id']:('学术文献',i+6) for i,a in enumerate(acad)}|{p['id']:('一手与机构资料',i+6) for i,p in enumerate(primary)}
 for ws in wb:
  for row in ws.iter_rows(min_row=6):
   c=row[0]
   if c.value in locations and ws.title not in ['学术文献','一手与机构资料']:
    name,r=locations[c.value];c.hyperlink=f"#'{name}'!A{r}"
 wb.active=0
 wb.properties.title='HY5417 牛车水项目文献与资料地图'
 wb.properties.subject='Contested heritage; Chinatown; Nanyang tea; Public History'
 wb.properties.creator='HY5417 project research support'
 wb.properties.description='Verified catalogue with access levels, source roles, evidence limits, and reading schedule. Snapshot 2026-09-26; per-source verification dates retained; literature review due 2026-10-02.'
 out=BASE/'HY5417_牛车水项目_文献与资料总表.xlsx';wb.save(out)
 # Verification uses the actual saved workbook, hyperlinks and referenced PDF files.
 check=load_workbook(out);ids=[a['id'] for a in acad]+[p['id'] for p in primary]
 errors=[]
 if len(ids)!=len(set(ids)):errors.append('duplicate IDs')
 dois=[a['identifier'].split(';')[0].lower() for a in acad if a['identifier'].startswith('10.')]
 if len(dois)!=len(set(dois)):errors.append('duplicate DOI')
 metadata_checked=[]
 for a in acad:
  mf=BASE/'sources'/('crossref_'+a['id']+'.json')
  if mf.exists():
   m=json.loads(mf.read_text())['message']
   if m.get('DOI','').lower()!=a['identifier'].split(';')[0].lower():errors.append('DOI metadata mismatch '+a['id'])
   parts=m.get('published-print',m.get('published',{})).get('date-parts',[[None]])[0]
   if parts[0]!=a['year']:errors.append('year metadata mismatch '+a['id'])
   if m.get('page') and m['page'].replace('-', '–') not in a['citation']:errors.append('page metadata mismatch '+a['id'])
   for author in m.get('author',[]):
    if author.get('family','') not in a['authors']:errors.append('author metadata mismatch '+a['id'])
   metadata_checked.append(a['id'])
 for a in acad+primary:
  if a['local'] and not (BASE/a['local']).is_file():errors.append('missing local '+a['id'])
  if not a['url'].startswith('https://'):errors.append('invalid source URL '+a['id'])
 for ws in check:
  if ws.freeze_panes is None: errors.append('no freeze '+ws.title)
  for row in ws:
   for c in row:
    if isinstance(c.value,str) and ('cite' in c.value or '\ufffd' in c.value):errors.append('invalid characters '+ws.title+str(c.coordinate))
    if c.hyperlink and c.hyperlink.target.startswith('fulltexts/') and not (BASE/c.hyperlink.target).exists():errors.append('broken pdf '+str(c.coordinate))
 localfiles=[]
 for p in sorted((BASE/'fulltexts').glob('*.pdf')):
  from pypdf import PdfReader
  doc=PdfReader(p)
  if not doc.pages[0].extract_text():errors.append('empty PDF first page '+p.name)
  localfiles.append(dict(path=str(p.relative_to(BASE)),pages=len(doc.pages),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 qa=dict(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),deadline_scope=DATA['deadline_scope'],rendering='No Excel application render performed; saved workbook reopened and structurally checked.',status='PASS' if not errors else 'FAIL',errors=errors,workbook=out.name,sheets=check.sheetnames,academic=len(acad),primary=len(primary),database_routes=len(DATABASES),crossref_metadata_checked=metadata_checked,pdfs=localfiles,core=[x[0] for x in CORE],snapshot=TODAY,scope='Metadata/access levels audited, old verification dates retained. A16 author first page and full methods pending. No new PDF downloads; 3 existing PDFs rechecked. Not a full-text review of every item.')
 (BASE/'_support/validation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
 print(json.dumps(qa,ensure_ascii=False,indent=2))
 if errors:raise SystemExit(1)

if __name__=='__main__':write_outputs()
