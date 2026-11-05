from pathlib import Path
import json
from docx import Document
from docx.shared import Mm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path(__file__).resolve().parent
content=json.loads((SOURCE/'presentation_content.json').read_text())
timing=json.loads((SOURCE/'presentation_timing.json').read_text())
doc=Document()
section=doc.sections[0]
section.page_width=Mm(210);section.page_height=Mm(297)
section.top_margin=Mm(18);section.bottom_margin=Mm(18)
section.left_margin=Mm(20);section.right_margin=Mm(20)
section.header_distance=Mm(8);section.footer_distance=Mm(9)
for grid in list(section._sectPr):
    if grid.tag == qn('w:docGrid'):section._sectPr.remove(grid)
styles=doc.styles
styles['Normal'].font.name='Georgia';styles['Normal'].font.size=Pt(13.5)
styles['Normal'].paragraph_format.line_spacing=1.16
styles['Normal'].paragraph_format.space_after=Pt(5)
styles['Normal'].element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),'Songti SC')
def paragraph(text,size=13.5,chinese=False,bold=False,color='262721',before=0,after=5,keep=False):
    p=doc.add_paragraph()
    p.paragraph_format.line_spacing=Pt(size*1.2)
    grid=OxmlElement('w:snapToGrid');grid.set(qn('w:val'),'0');p._p.get_or_add_pPr().append(grid)
    p.paragraph_format.space_before=Pt(before);p.paragraph_format.space_after=Pt(after)
    p.paragraph_format.keep_with_next=keep
    p.paragraph_format.widow_control=True
    r=p.add_run(text);r.font.name='Songti SC' if chinese else 'Georgia'
    r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
    r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),'Songti SC')
    lang=OxmlElement('w:lang');lang.set(qn('w:val'),'zh-CN' if chinese else 'en-US');r._element.get_or_add_rPr().append(lang)
    return p
header=section.header.paragraphs[0]
header.add_run('PORCELAIN IN TRANSLATION  |  EN / 中文讲稿').font.size=Pt(9)
footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
fr=footer.add_run('English delivery under 8 minutes  ·  ');fr.font.size=Pt(9)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
for index,slide in enumerate(content['slides'],1):
    if index>1:doc.add_page_break()
    cue=timing['slides'][index-1]
    fmt=lambda sec:f'{sec//60}:{sec%60:02d}'
    paragraph(f'Slide {index} / 5 — {slide["title"]}',size=18.5,bold=True,color='874839',after=4,keep=True)
    paragraph(slide['title_zh'],size=14.5,chinese=True,bold=True,color='683D32',after=6,keep=True)
    paragraph(f'Suggested cue: {fmt(cue["start_seconds"])}–{fmt(cue["end_seconds"])}  |  {cue["english_words"]} English words',size=10.5,color='746B5E',after=6,keep=True)
    if index==1:
        paragraph('只朗读英文；中文用于对照修改。英文共 590 词，按每分钟 90 词、另加 20 秒停顿估算约 6 分 53 秒。实际时长请以排练为准。',size=10.5,chinese=True,color='683D32',after=8,keep=True)
    paragraph('ENGLISH SCRIPT / 英文讲述',size=11.5,bold=True,color='874839',before=3,after=6,keep=True)
    for block in slide['english']:paragraph(block)
    paragraph('中文对照',size=12,chinese=True,bold=True,color='874839',before=7,after=6,keep=True)
    for block in slide['chinese']:paragraph(block,size=13,chinese=True)
    if index in [2,3,4]:
        context={2:'故宫博物院',3:'Sotheby’s 珐琅彩碗资料',4:'The Met 中国外销瓷资料（贸易背景，非此瓷盘照片出处）'}[index]
        paragraph('内容依据：project abstract.docx；器物背景：'+context+'。',size=9.5,chinese=True,color='746B5E',before=4,after=0)
doc.core_properties.title='Porcelain in Translation — English script with Chinese translation'
doc.core_properties.subject='Five PPT pages, each followed by a matching Chinese translation; English-only delivery under eight minutes'
doc.core_properties.author=''
file=ROOT/'HY5305_Porcelain_in_Translation_Curatorial_Edit_Script.docx'
doc.save(file)
print('Created',file)
print('Five slide sections; English text followed by matching Chinese text.')
