"""Build a Chinese intake workbook with examples separate from blank research tables."""
from pathlib import Path
import csv, hashlib, json
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
DATA=PROJECT/'04_gephi/进展gephi数据集'
OUT=ROOT/'双层传播网络_中文记录工作簿.xlsx'
if OUT.exists():
    raise SystemExit('Workbook exists. Refusing to overwrite potentially edited research records.')

def read(name):
    with (DATA/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

wb=Workbook();guide=wb.active;guide.title='从这里开始'
guide.append(['步骤／事项','填写方法'])
instructions=[
 ('1．先读一小段','在“阅读记录”填一行：来源ID、定位、原文、中文转述、具体动作、参与者及角色；日期和对象只记有依据的信息。'),
 ('2．保留未知','不确定对象就写“待识别批次”；未知人物、交接日、承运者等留空，并在“待核问题”说明。空值不等于不存在。'),
 ('3．标明证据性质','区分参与者自述、档案原件、档案转录、机构回顾、研究者转引。研究者引同一日记不是另一份独立目击证据。'),
 ('4．提取具体事件','核对后进入“事件整理”；每行一个可以定义的行为。一次取得的搬运参与角色不另造一次交接。'),
 ('5．连接两层','实物与知识事件复用同一ObjectId；照片、抄本等另给RepresentationId并记录与原卷的对应依据；作品给WorkId。'),
 ('6．精确记录知识行为','可以录“展示、抄录、摄影、编号、委托编目、刊布、引用”。未说明完成时，不能把意图或委托记成完成。'),
 ('7．从材料到图','事件整理后，按本文件夹已有8张CSV的相应字段分配对象、编号、复制品、作品、事件、参与角色与证据。只有有依据的关系进入Gephi。'),
 ('怎样使用示范','“示范记录”根据S07选段演示填写。示范不是已增加到主网络的事件，示范批次号是教学标记，不是真实馆藏号；不要直接批量导入。'),
 ('时间范围','当前基础范围仍是1900–1910。1921年出版的Serindia可支持1907／1910事件，但不会因此自动成为1900–1910的知识传播作品节点。'),
 ('现有主体和来源','“现有主体ID”与“现有来源ID”是已交付数据的只读参考副本。新人物／机构须先登记出处；新增来源须登记完整版本和本地路径。'),
 ('ID建议','阅读RD0001起；新实物事件PE001、新知识事件KE001；原物O0001、批次B0001、复制品R0001、作品W001。人物机构复用现有N编号；新号可从N017检查后分配，来源从S26检查后分配。'),
 ('身份不能靠题名合并','相同题名不代表同一物。馆藏号与旧号对应、原卷与照片对应均需单独证据；残片、批次与原卷明确区分。'),
 ('书信怎么记','先登记载体与档案号，再记录寄收人、日期、讨论对象和附寄物。谈到某物不证明物已寄出；收到信也不证明收到附件。'),
 ('引用怎么记','记录哪一作品引用哪一作品、准确页码和用途。主题相似、共读一卷不自动形成引用或合作关系。'),
 ('来源定位','印刷页、PDF页、folio与图版号明确区分。例如S07印刷916页＝6页摘录PDF第6页，不是扫描第916幅。'),
 ('保存原文','原文短摘录和中文转述分列；引文省略用[…]，OCR无法辨认的字回扫描核，不在引文中偷偷改写。'),
 ('核验状态','待核验＝尚未完成核对；可整理事件＝该条记载可支持所述行为，仍保留来源等级；仅线索＝只据摘要、元数据或笼统概述；排除＝记录具体理由。'),
 ('未完成的行为','“准备”“愿意”“送去用于”只支持意图或委托。实际执行、成果、归还各需相应来源，不能在缺证时画成完整链条。'),
 ('Excel日期','日期栏设为文本。保留清代纪年和历法；精确公历日期只在有依据时另加换算说明，不能默认公历11月就是清历十一月。'),
 ('表的状态','阅读记录和事件整理是空白可填写表；示范单列保存。原有Gephi数据与原文献不受本工作簿改动。')]
for r in instructions:guide.append(r)

headers=['阅读ID','来源ID','页码／段落／图版','原文短摘录','中文转述','网络层','具体动作','对象／批次ID或线索','参与者及角色','原始日期与历法','地点','证据性质','核验状态','待核问题／下一步']
intake=wb.create_sheet('阅读记录');intake.append(headers)
for _ in range(60):intake.append([None]*len(headers))
examples=wb.create_sheet('示范记录');examples.append(headers)
q825='Two midnight trips which they made to the temple with Chiang […] allowed the huge sackfuls to be safely removed to my store-room'
q916='In the autumn of 1910 a first instalment of manuscripts was duly transmitted to Professor Pelliot at Paris for the purpose of being catalogued.'
example_rows=[
 ['示范_RD01','S07','印刷825页首；摘录PDF第3页',q825,'蒋孝琬、Ibrahim Beg和Tila Bai参与两次夜间搬运，材料被搬到斯坦因库房。','实物流转','搬运参与','既有DH001取得批次；此段没有逐件号','N004蒋孝琬：搬运参与；N015 Ibrahim Beg、N016 Tila Bai：搬运参与；斯坦因库房为目的地','1907年章节语境；该句未标公历日','莫高窟附近库房','参与者自述','可整理事件','作为DH001参与角色补充；不新增蒋→斯坦因的一次保管权交接。精确日期另查S03和日记。'],
 ['示范_RD02','S07','印刷916页；摘录PDF第6页；1910年秋段',q916,'作者记1910年秋一批手稿被送给巴黎的伯希和，用于编目。','实物流转','为编目目的送寄','教学批次B_DEMO001；仅对应此处first instalment；具体写本号未知','N012伯希和：文中所称送寄对象；具体寄出、承运责任人未核','1910年秋；公历日未知','巴黎为目的地；前文语境为伦敦馆藏','参与者自述','待核验','找寄出／收件书信和对象清单；送寄不证明正式移藏BnF，也不自动证明实际收件日。'],
 ['示范_RD03','S07','印刷916页；摘录PDF第6页；同一送寄句',q916,'这次送寄的目的为编目；该句不能证明编目已完成。','知识传播','编目目的／委托线索','与示范_RD02同一教学批次B_DEMO001','N012伯希和：预定编目者；具体委托与接受条件要核前段及通信','1910年秋；公历日未知','巴黎','参与者自述','待核验','回前段及通信区分委托、同意、实际编目与成果；以“完成编目”为行为须另有证据。']]
for r in example_rows:examples.append(r)

eh=['事件ID','关联阅读ID','网络层','行为类型','对象／批次ObjectId','复制品RepresentationId','作品WorkId','转出主体ID（实物）','接收／目的主体ID（实物）','原始日期与历法','日期精度','地点','参与者及具体角色','证据支持什么','尚未确认什么','核验状态','证据来源及定位']
events=wb.create_sheet('事件整理');events.append(eh)
for _ in range(60):events.append([None]*len(eh))

entities=wb.create_sheet('现有主体ID');entities.append(['实体ID','中文名称','英文名称','节点类型','角色','别名','注意事项'])
for r in read('entities.csv'):entities.append([r['Id'],r['Label'],r['LabelEN'],r['NodeType'],r['Role'],r['Alias'],r['Notes']])
sources=wb.create_sheet('现有来源ID');sources.append(['来源ID','作者','题名','版本／出处','年份','本地路径（相对项目）','链接','限制'])
for r in read('sources.csv'):
 sources.append([r['SourceID'],r['Author'],r['Title'],r['Citation'],r['Year'],r['LocalPath'],r['URL'],r['Limitation']])

note_comments={
 '阅读ID':'自建稳定ID，例如RD0001；不能用页码充当ID。',
 '来源ID':'优先复用来源名录；多来源可用分号，但各来源定位要分别明确。',
 '原文短摘录':'照原文摘抄；省略使用[…]；与自己的转述分开。',
 '网络层':'选择本条记载主要支持的层。一个段落可提取不同动作，但不是每个人都互相连边。',
 '具体动作':'写可观察、可定位的行为；避免泛写“影响”“交流”。',
 '对象／批次ID或线索':'未能识别对象时写待识别批次；保留原文叫法，不虚构具体写本号。',
 '参与者及角色':'例如谈判人、搬运人、寄件人、收信人、作者、编目人；参与不自动等于保管。',
 '原始日期与历法':'文本保存原纪年与历法；不够精确时只到年、月或季。',
 '核验状态':'本行可支持的行为与来源限制分别记录；“可整理事件”不表示原档独立核验已完成。'}
for ws in [intake,examples]:
 for j,h in enumerate(headers,1):
  if h in note_comments:ws.cell(1,j).comment=Comment(note_comments[h],'HY5419')

def dropdown(ws,col,options):
 dv=DataValidation(type='list',formula1='"'+','.join(options)+'"',allow_blank=True)
 dv.errorTitle='请选择状态';dv.error='请选择下拉列表中的值。';dv.showErrorMessage=True
 dv.promptTitle='填写提示';dv.prompt='未知可留空；按本条史料实际支持范围选择。';dv.showInputMessage=True
 ws.add_data_validation(dv);dv.add(f'{col}2:{col}1000')
for ws in [intake,examples]:
 dropdown(ws,'F',['实物流转','知识传播','两层关联','背景'])
 dropdown(ws,'L',['参与者自述','档案原件','档案转录','机构回顾','研究者转引','目录记录','未核'])
 dropdown(ws,'M',['待核验','可整理事件','仅线索','排除'])
dropdown(events,'C',['实物流转','知识传播','两层关联'])
dropdown(events,'P',['待核验','可整理事件','仅线索','排除'])

for ws in wb:
 ws.freeze_panes='A2';ws.sheet_view.zoomScale=85
 ws.auto_filter.ref=ws.dimensions
 ws.row_dimensions[1].height=44
 for cell in ws[1]:
  cell.fill=PatternFill('solid',fgColor='24465A');cell.font=Font(name='PingFang SC',color='FFFFFF',bold=True,size=11)
  cell.alignment=Alignment(wrap_text=True,vertical='center')
 for row in ws.iter_rows(min_row=2):
  for cell in row:
   cell.font=Font(name='PingFang SC',size=11)
   cell.alignment=Alignment(wrap_text=True,vertical='top')
   cell.number_format='@'
   if row[0].row%2==0:cell.fill=PatternFill('solid',fgColor='F1F6F9')
  ws.row_dimensions[row[0].row].height=55
 for j in range(1,ws.max_column+1):
  ws.column_dimensions[ws.cell(1,j).column_letter].width=22
 if ws in [intake,examples]:
  for col,width in {'A':16,'B':12,'C':28,'D':65,'E':45,'F':16,'G':23,'H':32,'I':50,'J':28,'K':24,'L':20,'M':20,'N':65}.items():ws.column_dimensions[col].width=width
 if ws==examples:
  for i in range(2,5):ws.row_dimensions[i].height=145
 if ws==guide:
  ws.column_dimensions['A'].width=27;ws.column_dimensions['B'].width=110
  for i in range(2,ws.max_row+1):ws.row_dimensions[i].height=64
 if ws==entities:
  ws.column_dimensions['D'].width=18
  for c in ['E','F','G']:ws.column_dimensions[c].width=50
 if ws==sources:
  for c in ['C','D','F','G','H']:ws.column_dimensions[c].width=60
 if ws==events:
  for c in ['M','N','O','Q']:ws.column_dimensions[c].width=55
 ws.sheet_properties.pageSetUpPr.fitToPage=True
 ws.page_setup.orientation='landscape';ws.page_setup.paperSize=ws.PAPERSIZE_A3
 ws.print_title_rows='1:1';ws.print_options.horizontalCentered=True
guide.sheet_properties.tabColor='009E73';intake.sheet_properties.tabColor='0072B2'
examples.sheet_properties.tabColor='D55E00';events.sheet_properties.tabColor='755399'
wb.active=1
wb.save(OUT)

# Reopen the delivered file to verify blank input surfaces, example separation, and ID references.
check=load_workbook(OUT)
assert check.sheetnames==['从这里开始','阅读记录','示范记录','事件整理','现有主体ID','现有来源ID']
assert all(c.value is None for row in check['阅读记录'].iter_rows(min_row=2) for c in row)
assert all(c.value is None for row in check['事件整理'].iter_rows(min_row=2) for c in row)
assert check['示范记录'].max_row==4
assert check['现有主体ID'].max_row==15 and check['现有来源ID'].max_row==26
assert len(check['阅读记录'].data_validations.dataValidation)==3
report={'status':'passed','file':OUT.name,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
 'sheet_count':len(check.sheetnames),'blank_entry_sheets':['阅读记录','事件整理'],
 'example_rows':3,'existing_entities':14,'existing_sources':25,
 'source_of_examples':'S07 printed825 and916; previously visually checked scans',
 'example_object_ids_are_teaching_markers':True,'new_historical_events_added_to_Gephi':0,
 'scope':'Workbook reopening, empty input sheets, example separation, ID/source snapshot counts and data validations.'}
(ROOT/'填写工作簿_校验记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
