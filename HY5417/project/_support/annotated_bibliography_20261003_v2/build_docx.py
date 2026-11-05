from pathlib import Path
import json, re, hashlib
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
DATA = json.loads((HERE / 'draft_content.json').read_text())
OUTPUT = PROJECT / 'HY5417_Annotated_Bibliography_个人思考修订版_20261003.docx'

def fonts(style, size, east='Songti SC', west='Times New Roman'):
    style.font.name = west
    style.font.size = Pt(size)
    rf = style.element.get_or_add_rPr().get_or_add_rFonts()
    rf.set(qn('w:eastAsia'), east)
    rf.set(qn('w:ascii'), west)
    rf.set(qn('w:hAnsi'), west)

def link(p, text, url, italic=False):
    h = OxmlElement('w:hyperlink')
    h.set(qn('r:id'), p.part.relate_to(url, RT.HYPERLINK, is_external=True))
    r = OxmlElement('w:r')
    pr = OxmlElement('w:rPr')
    rf = OxmlElement('w:rFonts')
    rf.set(qn('w:ascii'), 'Times New Roman')
    rf.set(qn('w:hAnsi'), 'Times New Roman')
    pr.append(rf)
    if italic:
        pr.append(OxmlElement('w:i'))
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '222222')
    pr.append(color)
    r.append(pr)
    t = OxmlElement('w:t')
    t.text = text
    r.append(t)
    h.append(r)
    p._p.append(h)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.1)
sec.left_margin = sec.right_margin = Cm(2.3)
sec.header_distance = sec.footer_distance = Cm(1)
normal = doc.styles['Normal']
fonts(normal, 11)
normal.paragraph_format.line_spacing = 1.35
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.first_line_indent = Cm(0.78)
normal.paragraph_format.widow_control = True
fonts(doc.styles['Title'], 18, 'PingFang SC')
doc.styles['Title'].font.color.rgb = RGBColor.from_string('222222')
doc.styles['Title'].paragraph_format.space_after = Pt(5)
fonts(doc.styles['Subtitle'], 10, 'PingFang SC')
doc.styles['Subtitle'].font.color.rgb = RGBColor.from_string('666666')
fonts(doc.styles['Heading 1'], 12, 'PingFang SC')
doc.styles['Heading 1'].font.bold = True
doc.styles['Heading 1'].font.color.rgb = RGBColor.from_string('222222')
doc.styles['Heading 1'].paragraph_format.space_before = Pt(12)
doc.styles['Heading 1'].paragraph_format.space_after = Pt(5)
doc.styles['Heading 1'].paragraph_format.keep_with_next = True

refstyle = doc.styles.add_style('Bibliographic Entry', 1)
fonts(refstyle, 10)
refstyle.paragraph_format.left_indent = Cm(0.5)
refstyle.paragraph_format.first_line_indent = Cm(-0.5)
refstyle.paragraph_format.line_spacing = 1.1
refstyle.paragraph_format.space_after = Pt(7)
refstyle.paragraph_format.keep_with_next = True

p = doc.add_paragraph(DATA['title'], 'Title')
p.paragraph_format.first_line_indent = Cm(0)
p = doc.add_paragraph(DATA['subtitle'], 'Subtitle')
p.paragraph_format.first_line_indent = Cm(0)
doc.add_paragraph(DATA['introduction'])

italics = ['Tourism Management', 'The Past in the Present: A Living Heritage Approach—Meteora, Greece',
           'Localities', 'TRaNS: Trans-Regional and -National Studies of Southeast Asia',
           'Heritage, Contested Sites, and Borders of Memory in the Asia Pacific']
for entry, italic_phrase in zip(DATA['entries'], italics):
    p = doc.add_heading(entry['heading'], 1)
    p.paragraph_format.first_line_indent = Cm(0)
    p = doc.add_paragraph(style='Bibliographic Entry')
    before, after = entry['reference'].split(italic_phrase, 1)
    p.add_run(before)
    link(p, italic_phrase, entry['url'], italic=True)
    p.add_run(after)
    for text in entry['paragraphs']:
        doc.add_paragraph(text)

p = doc.add_heading(DATA['synthesis_heading'], 1)
p.paragraph_format.first_line_indent = Cm(0)
doc.add_paragraph(DATA['synthesis'])

footer = sec.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer.paragraph_format.first_line_indent = Cm(0)
run = footer.add_run()
run.font.size = Pt(9)
field = OxmlElement('w:fldSimple')
field.set(qn('w:instr'), 'PAGE')
run._r.addnext(field)

doc.core_properties.title = DATA['title']
doc.core_properties.subject = 'HY5417: 五项学术来源的注释书目与比较综合'
doc.core_properties.author = ''
doc.core_properties.keywords = '牛车水, 注释书目, 日常生活, 遗产保护, 旅游开发'
doc.core_properties.comments = ''
doc.save(OUTPUT)

blocks = [DATA['title'], DATA['subtitle'], DATA['introduction']]
for e in DATA['entries']:
    blocks.extend([e['heading'], e['reference'], *e['paragraphs']])
blocks.extend([DATA['synthesis_heading'], DATA['synthesis']])
text = '\n'.join(blocks)
(HERE / 'draft_text.txt').write_text(text)
body = DATA['introduction'] + ''.join(p for e in DATA['entries'] for p in e['paragraphs']) + DATA['synthesis']
body_han = len(re.findall(r'[\u4e00-\u9fff]', body))
assert 3000 <= body_han <= 4000
assert len(body) <= 4000
result = {'file': str(OUTPUT), 'sha256': hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
          'nonspace_characters_including_bibliography': len(re.sub(r'\s', '', text)),
          'characters_with_spaces_and_newlines': len(text),
          'chinese_characters': len(re.findall(r'[\u4e00-\u9fff]', text)),
          'academic_entries': len(DATA['entries']), 'synthesis_paragraphs': 1, 'body_han_excluding_headings_and_bibliography': body_han, 'body_characters_including_punctuation_and_author_names': len(body)}
(HERE / 'build_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False))
