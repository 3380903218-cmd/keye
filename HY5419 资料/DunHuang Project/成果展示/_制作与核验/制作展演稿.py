# -*- coding: utf-8 -*-
"""Author the bilingual presentation from its reviewed structured text."""
from pathlib import Path
import json, re, hashlib
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

HERE=Path(__file__).resolve().parent
DATA=json.loads((HERE/'展演稿内容.json').read_text(encoding='utf-8'))
OUT=HERE.parent/'HY5419_敦煌项目_8分钟展演稿_中英对照.docx'
if OUT.exists():raise FileExistsError(OUT)
doc=Document();sec=doc.sections[0]
sec.page_width=Cm(21);sec.page_height=Cm(29.7)
sec.top_margin=Cm(1.8);sec.bottom_margin=Cm(1.8)
sec.left_margin=Cm(2);sec.right_margin=Cm(2)
sec.header_distance=Cm(.7);sec.footer_distance=Cm(.7)
doc.core_properties.title=DATA['title'];doc.core_properties.author='Xiwen Wang'
doc.core_properties.subject='Five-minute live website presentation and two-to-three-minute Q&A'
doc.core_properties.language='en-SG';doc.core_properties.keywords='HY5419, Dunhuang, QGIS, Gephi, bilingual presentation'

for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','List Bullet','List Number','Caption']:
    st=doc.styles[name];st.font.name='Arial'
    f=st.element.get_or_add_rPr().get_or_add_rFonts()
    for k in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:f.attrib.pop(qn('w:'+k),None)
    for k,v in [('ascii','Arial'),('hAnsi','Arial'),('eastAsia','Songti SC')]:f.set(qn('w:'+k),v)
normal=doc.styles['Normal'];normal.font.size=Pt(11)
normal.paragraph_format.line_spacing=1.15;normal.paragraph_format.space_after=Pt(5)
for level,size in [(1,16),(2,12.5),(3,11.5)]:
    st=doc.styles['Heading '+str(level)];st.font.size=Pt(size);st.font.color.rgb=RGBColor.from_string('344B43')
    st.paragraph_format.keep_with_next=True;st.paragraph_format.space_before=Pt(9);st.paragraph_format.space_after=Pt(6)
for name,size,color in [('Script EN',11.5,'202825'),('Script ZH',11,'4F5851'),('Stage Cue',10,'76543F'),('Small Note',9.5,'565E59'),('QA EN',11,'202825'),('QA ZH',10.5,'4F5851')]:
    st=doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH);st.base_style=normal;st.font.size=Pt(size);st.font.color.rgb=RGBColor.from_string(color)
    st.paragraph_format.line_spacing=1.15;st.paragraph_format.space_after=Pt(5)
    st.paragraph_format.widow_control=True
    if name in ['Script EN','QA EN']:st.paragraph_format.keep_with_next=True
doc.styles['Stage Cue'].paragraph_format.keep_with_next=True

def fonts(run,size=None,bold=None,color=None,lang=None):
    run.font.name='Arial';rf=run._element.get_or_add_rPr().get_or_add_rFonts()
    for key,value in [('ascii','Arial'),('hAnsi','Arial'),('eastAsia','Songti SC')]:rf.set(qn('w:'+key),value)
    if size:run.font.size=Pt(size)
    if bold is not None:run.bold=bold
    if color:run.font.color.rgb=RGBColor.from_string(color)
    if lang:
        l=OxmlElement('w:lang');l.set(qn('w:val'),lang);l.set(qn('w:eastAsia'),'zh-CN');run._element.get_or_add_rPr().append(l)
    return run

def p(text='',style=None):
    para=doc.add_paragraph(style=style);fonts(para.add_run(text));return para

def heading(text,level=1):
    para=doc.add_heading(level=level);fonts(para.add_run(text));return para

def cue(text):
    para=p('操作提示｜'+text,'Stage Cue');pr=para._p.get_or_add_pPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'F2EEE5');pr.append(sh)
    para.paragraph_format.left_indent=Cm(.2);para.paragraph_format.right_indent=Cm(.2)
    return para

def pair(en,zh,qa=False):
    para=doc.add_paragraph(style='QA EN' if qa else 'Script EN')
    fonts(para.add_run('EN  '),bold=True,color='86583F',lang='en-SG');fonts(para.add_run(en),lang='en-SG')
    para=doc.add_paragraph(style='QA ZH' if qa else 'Script ZH')
    fonts(para.add_run('中  '),bold=True,color='576D5A',lang='zh-CN');fonts(para.add_run(zh),lang='zh-CN')

def hyperlink(para,text,url):
    relation=para.part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
    h=OxmlElement('w:hyperlink');h.set(qn('r:id'),relation);r=OxmlElement('w:r');pr=OxmlElement('w:rPr')
    color=OxmlElement('w:color');color.set(qn('w:val'),'6B513E');pr.append(color)
    underline=OxmlElement('w:u');underline.set(qn('w:val'),'single');pr.append(underline)
    r.append(pr);t=OxmlElement('w:t');t.text=text;r.append(t);h.append(r);para._p.append(h)

def page():doc.add_page_break()

# A compact first page is a practical running order rather than a separate cover.
t=doc.add_paragraph();fonts(t.add_run(DATA['title']),size=20,bold=True,color='344B43')
p(DATA['subtitle'],'Subtitle');p(DATA['author']+'  |  '+DATA['date'],'Small Note')
heading('使用方式',2)
p('正式展示只读英文；中文用于理解与排练。主讲约5分钟，另留2—3分钟由同学提问。操作提示、问答备选和资料定位均不计入口述正文。')
words=sum(len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b",x['en'])) for s in DATA['speech'] for x in s['paragraphs'])
p(f'英文主讲正文约{words}词。按每分钟110—120词，口述约{words/120:.1f}—{words/110:.1f}分钟，再预留约30—45秒网页操作。以带操作的实际排练计时为准，控制在5分钟内。','Small Note')
para=p();hyperlink(para,'英文展示入口：'+DATA['url'],DATA['url'])
heading('时间与屏幕安排',2)
table=doc.add_table(rows=1,cols=3);table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
widths=[2.7,4.5,9.7]
for c,w in zip(table.columns,widths):c.width=Cm(w)
for c,w in zip(table.rows[0].cells,widths):c.width=Cm(w)
for c,text in zip(table.rows[0].cells,['时间','主讲重点','网页画面／操作']):
    c.text=text;shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EDE7');c._tc.get_or_add_tcPr().append(shade)
repeat=OxmlElement('w:tblHeader');table.rows[0]._tr.get_or_add_trPr().append(repeat)
for row in DATA['timing']:
    cells=table.add_row().cells
    for c,text,w in zip(cells,row,widths):c.width=Cm(w);c.text=text
for row_index,row in enumerate(table.rows):
    for c in row.cells:
        c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for para in c.paragraphs:
            para.paragraph_format.space_after=Pt(5);para.paragraph_format.space_before=Pt(4)
            for run in para.runs:fonts(run,size=9.5,bold=row_index==0)
    cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)
heading('上台前与时间控制',2)
for text in [
    '预先打开英文网站并加载地图、网络和原图；关闭无关标签页、通知及聊天窗口。现场不用跳到Gephi或QGIS软件。',
    '备份文件：项目“07_互动传播地图/国内外访问版/敦煌传播地图_离线英文版.html”。网页加载异常时直接切换离线版。',
    '地图到1:30就转入网络；网络到3:25就转入方法与AI分工。时间紧时先省略原图切换和第二个通信例子。',
    '问答准备了8题供选用；现场只回应同学实际提出的问题，不主动把整份问答再念一遍。'
]:
    bp=p(text,'List Bullet');bp.paragraph_format.space_after=Pt(3)
    for run in bp.runs:fonts(run,size=9.5)

# Main script: page 2 (opening/map), page 3 (network), page 4 (methods/closing).
groups=[DATA['speech'][:2],DATA['speech'][2:3],DATA['speech'][3:]]
for index,group in enumerate(groups):
    page();heading('英文主讲稿与中文对照'+('' if index==0 else '（续）'))
    for s in group:
        heading(s['time']+'  '+s['title'],2);cue(s['cue'])
        for x in s['paragraphs']:pair(x['en'],x['zh'])
        if s.get('cue_after'):p('演示备忘｜'+s['cue_after'],'Small Note')
    if index==2:
        heading('若接近5分钟：用以下短句替换最后一段',2)
        pair('Together, the map and network connect manuscript journeys with the people who studied them. The website also lets readers check the sources. Thank you. I welcome your questions.',
             '地图与网络把文献流转与研究这些材料的人联系起来，网页也让读者能够核对来源。谢谢大家，欢迎提问。')
        p('5:00后停止主讲。先听完问题，再用一句话直接回答，然后补充一个例子；不需要继续展示所有功能。','Small Note')

# Prepared Q&A: three per page; last two share a page with source locations.
for start,end in [(0,3),(3,6),(6,8)]:
    page();heading('问答备选｜Q&A preparation')
    if start==0:p('以下是准备材料，不是固定问答流程。每次只读英文回答中的必要部分，目标20—35秒；有余时再指向网页实例。','Small Note')
    for i in range(start,end):
        item=DATA['qa'][i];heading(f'Q{i+1}. '+item['q_en'],2)
        p(item['q_zh'],'Small Note');pair(item['a_en'],item['a_zh'],qa=True)
        p('备忘｜'+item['cue'],'Small Note')
    if end==8:
        heading('资料定位与事实边界（不口述）',2)
        for item in DATA['references']:
            para=p(style='Small Note');hyperlink(para,item['label'],item['url'])
            p(item['note'],'Small Note')
        p('范围：早期网络为1900—1910年；今日馆藏与保存资料另列。地图连线为示意；文献批次不等于逐件写本。节点数与活动记录数不等于完整历史规模。','Small Note')

# Native fields, restrained header/footer, and explicit fonts for every normal run.
hp=sec.header.paragraphs[0];fonts(hp.add_run('HY5419  |  Dunhuang, in motion  |  Website demonstration'),size=8.5,color='5A665D')
fp=sec.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
fonts(fp.add_run('英文口述 · 中文参考  |  '),size=8.5,color='5A665D')
for k in ['PAGE','NUMPAGES']:
    if k=='NUMPAGES':fonts(fp.add_run(' / '),size=8.5)
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),k);fp._p.append(fld)
for para in doc.paragraphs:
    para.paragraph_format.widow_control=True
    for run in para.runs:fonts(run)
doc.save(OUT)

# Content acceptance against the structured text, including paragraphs inside tables.
loaded=Document(OUT);texts=[p.text for p in loaded.paragraphs]
for table in loaded.tables:
    texts += [p.text for row in table.rows for cell in row.cells for p in cell.paragraphs]
flat='\n'.join(texts)
required=[p[k] for s in DATA['speech'] for p in s['paragraphs'] for k in ['en','zh']]
required += [q[k] for q in DATA['qa'] for k in ['q_en','q_zh','a_en','a_zh']]
missing=[t for t in required if t not in flat];assert not missing,missing
receipt={'file':str(OUT),'source':str(HERE/'展演稿内容.json'),'source_sha256':hashlib.sha256((HERE/'展演稿内容.json').read_bytes()).hexdigest(),'docx_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'english_spoken_words':words,'main_speech_paragraphs':sum(len(s['paragraphs']) for s in DATA['speech']),'qa_pairs':len(DATA['qa']),'bilingual_content_check':'passed','source_items_checked':len(required),'native_and_visual_check':'pending','date':'2026-10-31'}
(HERE/'内容核验.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
