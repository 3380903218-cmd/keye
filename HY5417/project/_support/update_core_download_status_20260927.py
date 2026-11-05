from pathlib import Path
import json,hashlib,plistlib,re
from copy import copy
from pypdf import PdfReader
from openpyxl import load_workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.worksheet.table import Table,TableStyleInfo

B=Path(__file__).resolve().parents[1]
FILE=B/'HY5417_牛车水项目_文献与资料总表.xlsx'
d=json.loads((B/'_support/catalogue.json').read_text())
aa={a['id']:a for a in d['academic']}
d['date']='2026-09-27';d['snapshot']='HY5417_chinatown_20260927_download_status'
proxy='https://libproxy1.nus.edu.sg/login?url='
urls={
 'A02':'https://www.sciencedirect.com/science/article/pii/S0261517799001089',
 'A03':'https://brill.com/display/book/9789004512986/BP000013.xml',
 'A04':'https://www.ssoar.info/ssoar/bitstream/document/31509/1/ssoar-2011-heng_et_al-Singapore_in_global_history.pdf'
}
steps={
 'A02':'打开ScienceDirect论文页；通过NUS代理或Access through your institution登录National University of Singapore；如有订阅，点击View PDF／Download PDF。需10页完整论文，pp. 525–534。',
 'A03':'打开Brill第3章，先完成浏览器验证，再尝试Download PDF。如提示权限不足，选Login via Institution → National University of Singapore，或用NUS代理入口。需pp. 56–79（24页）的章节。',
 'A04':'打开SSOAR整书PDF，完成浏览器验证后保存；读第7章，印刷pp. 135–150。也可用JSTOR章节入口下载。开放获取，无须先购买。'
}
filenames={
 'A02':'A02_Henderson_2000_Chinatown_Conservation_and_Promotion.pdf',
 'A03':'A03_Chan_2023_Chineseness_of_Chinatown.pdf',
 'A04':'A04_Singapore_in_Global_History_2011_full_book.pdf'
}
records=[];pdfs=[]
for id in ['A07','A02','A03','A04','A06']:
 a=aa[id];a['checked_date']='2026-09-27'
 a['trace']+='; sources/core_download_web_20260927.json; sources/retrieval_core_20260927.json'
 if id in ['A07','A06']:
  p=B/a['local'];r=PdfReader(p);first=' '.join((x.extract_text() or '') for x in r.pages[:2])
  assert ('Chinatown' in first if id=='A07' else 'Poulios' in first)
  a['access']=f'本地已有完整PDF（{len(r.pages)}页）；2026-09-27复核身份与可读性'
  a['verified']+='；2026-09-27重新打开文件核对首页与总页数，非新增精读'
  pdfs.append(dict(id=id,path=a['local'],pages=len(r.pages),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
  records.append([id,a['title_zh'],'已在本地',a['local'],'无需操作',a['url'],'',p.name,'2026-09-27'])
 else:
  a['local']=''
  if id=='A02':
   a['access']='未取得全文：2026-09-27自动下载返回403；公开库检索未找到可用全文，需浏览器通过NUS尝试机构访问'
   a['verified']='书目及摘要已核；本轮下载失败，不能认定已取得或阅读全文'
   action=proxy+urls[id]
  elif id=='A03':
   a['access']='未取得全文：Brill两个PDF入口均返回浏览器验证页；请手动打开，若提示权限再用NUS登录'
   a['verified']='出版社摘要与书目已核；OpenAlex标OA，但出版社权限未能现场确认；本轮未取得PDF'
   action=proxy+urls[id]
  else:
   a['access']='未取得全文：SSOAR/JSTOR/出版社返回浏览器验证，UPLOpen返回403；需手动打开SSOAR整书或JSTOR章节'
   a['verified']='已核书目与开放获取来源；本轮实际下载未成功，未取得第7章全文'
   action='https://www.jstor.org/stable/j.ctt46mtvv.11'
  records.append([id,a['title_zh'],'待手动下载','',steps[id],urls[id],action,filenames[id],'2026-09-27'])
  for core in d['core']:
   if core[0]==id:core[4]=steps[id]
d['downloads']=records
(B/'_support/catalogue.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))

# Update existing cells directly to preserve all user-entered notes and progress.
w=load_workbook(FILE);ws=w['学术文献']
for row in ws.iter_rows(min_row=6):
 id=row[0].value
 if id not in [x[0] for x in records]:continue
 a=aa[id];r=row[0].row
 for col,key in [(12,'access'),(13,'verified'),(20,'checked_date'),(21,'trace')]:ws.cell(r,col,a[key])
 if id in ['A06','A07'] and ws.cell(r,18).value=='未开始':ws.cell(r,18,'已取得全文')
 ws.row_dimensions[r].height=max(ws.row_dimensions[r].height or 0,165)
for row in w['五篇核心'].iter_rows(min_row=6,max_row=10):
 id=row[0].value;r=row[0].row
 w['五篇核心'].cell(r,7,aa[id]['access'])
 if id in steps:w['五篇核心'].cell(r,8,steps[id])
ws=w['使用说明']
ws.cell(2,1,'2026-09-27下载状态更新  ·  文献综述截止：2026-10-02  ·  五篇核心：2篇本地／3篇待手动下载')
for row in ws.iter_rows(min_row=6):
 if row[0].value=='阅读顺序':ws.cell(row[0].row,2,'先看“核心下载状态”，再看五篇核心、学术文献、综述比较矩阵和注释书目记录。')
 if row[0].value=='核验与访问':ws.cell(row[0].row,2,'五篇核心下载状态于2026-09-27更新；其他条目保留各自核验日期。')
 if row[0].value=='本地附件':ws.cell(row[0].row,3,'本轮未新增成功下载；五篇核心仅A06/A07已有全文，P06路线册不计入核心五篇。另三篇手动入口见“核心下载状态”。')
name='核心下载状态'
if name in w:del w[name]
ws=w.create_sheet(name,1);ws.sheet_view.showGridLines=False;ws.sheet_view.zoomScale=85
headers=['编号','文献','下载结果','本地PDF','需要你的操作','直接网站','NUS代理／备用入口','建议保存文件名','检查日期']
widths=[10,63,21,22,94,21,25,69,18]
for rn,text in [(1,'五篇核心文献｜下载清单'),(2,'2026-09-27：2篇本地全文已复核，3篇需手动操作；网站验证页没有保存成PDF。')]:
 ws.merge_cells(start_row=rn,start_column=1,end_row=rn,end_column=9);c=ws.cell(rn,1,text);c.font=Font(name='PingFang SC',size=20 if rn==1 else 11,bold=rn==1,color='FFFFFF' if rn==1 else '365962');c.fill=PatternFill('solid',fgColor='183C4A' if rn==1 else 'E8F3F3');c.alignment=Alignment(wrap_text=True,vertical='center');ws.row_dimensions[rn].height=44
for j,h in enumerate(headers,1):
 c=ws.cell(5,j,h);c.font=Font(name='PingFang SC',size=11,bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='157A7C');c.alignment=Alignment(wrap_text=True,vertical='center');ws.column_dimensions[c.column_letter].width=widths[j-1]
for i,record in enumerate(records,6):
 for j,value in enumerate(record,1):
  c=ws.cell(i,j,value);c.font=Font(name='PingFang SC',size=11,color='223640');c.fill=PatternFill('solid',fgColor='FFFFFF' if i%2==0 else 'F1F4F6');c.alignment=Alignment(wrap_text=True,vertical='top')
  if value.startswith(('https://','fulltexts/')):c.hyperlink=value;c.value='打开 ↗';c.font=Font(name='PingFang SC',size=11,color='0563C1',underline='single')
 ws.row_dimensions[i].height=130
ws.freeze_panes='C6';ws.row_dimensions[5].height=31
tab=Table(displayName='CoreDownloadStatus20260927',ref='A5:I10');tab.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=False);ws.add_table(tab)
w.save(FILE)

shortcuts=B/'fulltexts/待手动下载入口';shortcuts.mkdir(exist_ok=True)
for id in ['A02','A03','A04']:
 with (shortcuts/f'{id}_直接下载网站.webloc').open('wb') as f:plistlib.dump({'URL':urls[id]},f)
 if id in ['A02','A03']:
  with (shortcuts/f'{id}_NUS登录入口.webloc').open('wb') as f:plistlib.dump({'URL':proxy+urls[id]},f)

# Keep the offline formatter aware of the new tab for future rebuilds.
builder=B/'_support/build_workbook.py';s=builder.read_text()
if "if DATA.get('downloads'):" not in s:
 s=s.replace(" wb._sheets=[wb[x] for x in order]", " if DATA.get('downloads'):\n  sheet('核心下载状态','五篇核心文献｜下载清单','2026-09-27：2篇本地全文已复核；3篇需手动操作。',['编号','文献','下载结果','本地PDF','需要你的操作','直接网站','NUS代理／备用入口','建议保存文件名','检查日期'],DATA['downloads'],[10,63,21,22,94,21,25,69,18],height=130)\n  order.insert(1,'核心下载状态')\n wb._sheets=[wb[x] for x in order]")
 s=s.replace('2026-09-26更新  ·  文献综述截止：2026-10-02  ·  17篇学术文献／20项资料／3个本地PDF','2026-09-27下载状态更新  ·  文献综述截止：2026-10-02  ·  五篇核心：2篇本地／3篇待手动下载')
 builder.write_text(s)

check=load_workbook(FILE);assert check['核心下载状态'].max_row==10
for row in records:
 if row[3]:assert (B/row[3]).is_file()
errors=[]
for sh in check:
 for row in sh:
  for c in row:
   if c.hyperlink and c.hyperlink.target.startswith('fulltexts/') and not (B/c.hyperlink.target).is_file():errors.append('broken local link '+c.coordinate)
assert not errors,errors
qa=json.loads((B/'_support/validation.json').read_text());qa['sha256']=hashlib.sha256(FILE.read_bytes()).hexdigest();qa['sheets']=check.sheetnames;qa['snapshot']=d['snapshot'];qa['core_download_check']=dict(date='2026-09-27',available=['A07','A06'],manual=['A02','A03','A04'],new_pdfs=0,local_pdf_validation=pdfs,errors=errors,status='PASS',meaning='Download status and package consistency verified; three requested texts remain unavailable locally.')
qa.pop('additional_checks',None)
(B/'_support/validation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
(B/'sources/core_download_status_20260927.json').write_text(json.dumps(qa['core_download_check'],ensure_ascii=False,indent=2))
print(json.dumps(qa['core_download_check'],ensure_ascii=False,indent=2))
