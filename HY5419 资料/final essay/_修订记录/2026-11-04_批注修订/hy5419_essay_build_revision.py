from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image, ImageDraw, ImageFont
import json,hashlib,re

W=Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/final essay/_修订记录/2026-11-04_批注修订')
src=W/'批注原稿备份.docx'
output=W/'修订候选.docx'
data=json.loads((W/'revisions.json').read_text())
changes={int(k):v for k,v in data['changes'].items()}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
qn=lambda s:'{'+ns['w']+'}'+s
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

# Compose two independently rendered source excerpts into one numbered figure.
panels=[Image.open(W/'map_places.png').convert('RGB'),Image.open(W/'map_lines.png').convert('RGB')]
width=max(p.width for p in panels)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Songti.ttc',40)
label_h=76
scaled=[p.resize((width,round(p.height*width/p.width)),Image.Resampling.LANCZOS) for p in panels]
canvas=Image.new('RGB',(width,sum(p.height for p in scaled)+label_h*2+32),'white')
draw=ImageDraw.Draw(canvas)
y=0
for label,p in zip(['（a）地点与定位精度','（b）路线起讫点与时间'],scaled):
 draw.text((6,y+14),label,font=font,fill='black')
 y+=label_h
 canvas.paste(p,(0,y)); y+=p.height+16
canvas.save(W/'qgis.png',dpi=(300,300))

doc=Document(src)
original=list(doc.paragraphs)
assert len(original)==72
protected={'drawing','fldChar','fldSimple','instrText','hyperlink','oMath','oMathPara'}
format_inventory={}
for i,new in changes.items():
 p=original[i]
 assert not any(etree.QName(n).localname in protected for n in p._p.iter()), f'Protected content in P{i}'
 text_nodes=p._p.xpath('.//w:t')
 assert text_nodes
 # Original affected prose uses only inherited font properties and zh-CN language.
 # Keep all run/paragraph formatting; replace visible text, not the paragraph node.
 signatures=[]
 for r in p._p.xpath('./w:r'):
  if r.find(qn('t')) is None: continue
  rp=r.find(qn('rPr'))
  if rp is not None:
   roles=[etree.QName(x).localname for x in rp]
   assert set(roles)<= {'lang'}, (i,roles)
   signatures.append(etree.tostring(rp).decode())
 format_inventory[str(i)]=signatures
 text_nodes[0].text=new
 text_nodes[0].set('{http://www.w3.org/XML/1998/namespace}space','preserve')
 for t in text_nodes[1:]: t.text=''

for i in data['remove']:
 p=original[i]._p
 p.getparent().remove(p)

def insert_after(anchor,text=None,style='Normal'):
 p=doc.add_paragraph(style=style)
 anchor.addnext(p._p)
 if text: p.add_run(text)
 return p

figures=[
 (14,'gephi.png','图1 Gephi关系表中的角色与证据',
  '来源：本人《敦煌传播网络_最终展示数据_132节点157关系》工作表“02_Gephi关系”第51—54行，节选A、B、H、I、O列。原值未改，图中字段已重新排版。',
  'Gephi关系数据节选，区分写本批次、形成的文书、请求者和作者，四条关系均关联证据EV046。'),
 (28,'qgis.png','图2 QGIS数据中的地点精度与路线时间',
  '来源：本人路线地图工作簿，“03_地点与坐标”与“14_示意线导入”第2—4行的部分列。原值未改，图中字段已重新排版；空白坐标仍保留为待核。',
  'QGIS数据节选。上图区分城市、遗址与洞窟定位；下图记录路线端点、事件编号与时间证据。')
]
for i,name,caption,source,alt in figures:
 picp=insert_after(original[i]._p)
 picp.alignment=WD_ALIGN_PARAGRAPH.CENTER
 fmt=picp.paragraph_format
 fmt.first_line_indent=Pt(0); fmt.line_spacing=1
 fmt.space_before=Pt(6); fmt.space_after=Pt(4); fmt.keep_with_next=True
 shape=picp.add_run().add_picture(str(W/name),width=Inches(6.14))
 shape._inline.docPr.set('descr',alt)
 cp=insert_after(picp._p,caption)
 cp.alignment=WD_ALIGN_PARAGRAPH.CENTER
 cf=cp.paragraph_format
 cf.first_line_indent=Pt(0); cf.line_spacing=Pt(15); cf.space_after=Pt(3); cf.keep_with_next=True
 for r in cp.runs: r.font.size=Pt(10.5)
 sp=insert_after(cp._p,source)
 sf=sp.paragraph_format
 sf.first_line_indent=Pt(0); sf.line_spacing=Pt(14); sf.space_after=Pt(8); sf.keep_with_next=False
 for r in sp.runs: r.font.size=Pt(9.5)

raw=W/'修订候选_未清批注.docx'
doc.save(raw)
CT='http://schemas.openxmlformats.org/package/2006/content-types'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
with ZipFile(raw) as zin:
 removed={n for n in zin.namelist() if re.search(r'(^|/)(comments[^/]*|people)\.xml$',n,re.I) or re.search(r'(^|/)_rels/(comments[^/]*|people)\.xml\.rels$',n,re.I)}
 with ZipFile(output,'w',ZIP_DEFLATED) as zout:
  for item in zin.infolist():
   if item.filename in removed: continue
   b=zin.read(item.filename)
   if item.filename.endswith('.xml') or item.filename.endswith('.rels'):
    root=etree.fromstring(b)
    if item.filename=='[Content_Types].xml':
     for c in list(root):
      if c.get('PartName','').lstrip('/') in removed: root.remove(c)
    elif item.filename.endswith('.rels'):
     for rel in list(root):
      typ=rel.get('Type','').lower()
      if 'comment' in typ or typ.endswith('/people'): root.remove(rel)
    elif item.filename.startswith('word/'):
     for n in list(root.iter()):
      if etree.QName(n).localname in {'commentRangeStart','commentRangeEnd','commentReference'}:
       n.getparent().remove(n)
     if item.filename=='word/settings.xml':
      for n in list(root):
       if etree.QName(n).localname in {'trackRevisions','doNotTrackMoves','doNotTrackFormatting'}: root.remove(n)
    b=etree.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
   zout.writestr(item,b)

with ZipFile(output) as z:
 root=etree.fromstring(z.read('word/document.xml'))
 assert len(root.xpath('//w:drawing',namespaces=ns))==2
 assert not root.xpath('//w:commentRangeStart|//w:commentRangeEnd|//w:commentReference|//w:ins|//w:del',namespaces=ns)
 assert not any(re.search(r'(comments|people)',n,re.I) for n in z.namelist())
 paras=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in root.xpath('//w:body/w:p',namespaces=ns)]
 assert not any(re.search(r'第[一二三四五六七八九十0-9]+周',t) for t in paras)
 for i,new in changes.items(): assert new in paras
 for i,p in enumerate(original):
  if i not in changes and i not in data['remove']:
   old=''.join(p._p.xpath('.//w:t/text()'))
   assert old in paras
 main=''.join(paras[2:paras.index('参考文献')])
 count=len(re.findall(r'[\u3400-\u9fff]',main))+len(re.findall(r'[A-Za-z]+(?:[\-’\'][A-Za-z]+)*',main))+len(re.findall(r'\d+(?:[.\-—]\d+)*',main))
 report={'sha256':sha(output),'baseline_sha256':sha(src),'changed_paragraphs':sorted(changes),'removed_paragraphs':data['remove'],'figures':2,'resolved_comments':4,'body_count_without_headings_captions_sources':data['stats'],'main_count_including_headings_captions_sources_excluding_punctuation':count,'removed_parts':sorted(removed),'format_roles_preserved':format_inventory}
 (W/'content-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 (W/'修订稿全文.md').write_text('\n\n'.join(paras))
print(json.dumps({k:v for k,v in report.items() if k!='format_roles_preserved'},ensure_ascii=False))
