from pathlib import Path
import hashlib
import json
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path('/Users/arourouwed/Desktop/NUS/2026-1/HY6101')
AUDIT = ROOT / '.essay2_delivery_20261024'
SOURCE = AUDIT / 'essay2_zh.md'
OUTPUT = ROOT / 'seminar 11/HY6101_Combined_Essay2_中文版.docx'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(style, east_asia='Songti SC', size=12, bold=False):
    style.font.name = 'Times New Roman'
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = False
    style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rpr.insert(0, rf)
    for attr in list(rf.attrib):
        if 'theme' in attr.lower():
            del rf.attrib[attr]
    for key, value in [('eastAsia', east_asia), ('ascii', 'Times New Roman'), ('hAnsi', 'Times New Roman')]:
        rf.set(qn('w:' + key), value)
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'en-GB')
    lang.set(qn('w:eastAsia'), 'zh-CN')
    rpr.append(lang)
    for tag in ['spacing', 'kern']:
        node = rpr.find(qn('w:' + tag))
        if node is not None:
            rpr.remove(node)
    ppr = style.element.find(qn('w:pPr'))
    if ppr is not None:
        for tag in ['pBdr', 'numPr']:
            node = ppr.find(qn('w:' + tag))
            if node is not None:
                ppr.remove(node)
        snap = OxmlElement('w:snapToGrid')
        snap.set(qn('w:val'), '0')
        ppr.append(snap)


md = SOURCE.read_text(encoding='utf-8')
blocks = [p.strip() for p in md.split('\n\n') if p.strip()]
body = [p for p in md.split('### 阅读文献')[0].split('\n\n') if p.strip() and not p.startswith('#')]
han_count = len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]', ''.join(body)))
assert 8000 <= han_count <= 8500, han_count

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.54)
sec.left_margin = sec.right_margin = Cm(2.54)
sec.header_distance = sec.footer_distance = Cm(1.25)

normal = doc.styles['Normal']
font(normal)
pf = normal.paragraph_format
pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pf.first_line_indent = Pt(24)
pf.line_spacing = Pt(22)
pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
pf.space_after = Pt(4)
pf.widow_control = True

font(doc.styles['Title'], size=18, bold=True)
tp = doc.styles['Title'].paragraph_format
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
tp.first_line_indent = Pt(0)
tp.space_after = Pt(6)
tp.line_spacing = Pt(27)
tp.keep_with_next = True
font(doc.styles['Subtitle'], size=13)
sp = doc.styles['Subtitle'].paragraph_format
sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
sp.first_line_indent = Pt(0)
sp.space_after = Pt(18)
sp.line_spacing = Pt(20)
sp.keep_with_next = True

font(doc.styles['Heading 1'], east_asia='Heiti SC', size=13, bold=True)
hp = doc.styles['Heading 1'].paragraph_format
hp.first_line_indent = Pt(0)
hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
hp.line_spacing = Pt(20)
hp.space_before = Pt(12)
hp.space_after = Pt(7)
hp.keep_with_next = True
hp.keep_together = True

for name in ['Header', 'Footer']:
    font(doc.styles[name], size=9)
    doc.styles[name].paragraph_format.first_line_indent = Pt(0)
    doc.styles[name].paragraph_format.line_spacing = Pt(12)

header = sec.header.paragraphs[0]
header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
header.add_run('HY6101  |  Combined Essay 2')
footer = sec.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer.add_run('第 ')
fld = OxmlElement('w:fldSimple')
fld.set(qn('w:instr'), 'PAGE')
r = OxmlElement('w:r')
t = OxmlElement('w:t')
t.text = '1'
r.append(t)
fld.append(r)
footer._p.append(fld)
footer.add_run(' 页')

ref_mode = False
expected = []
for block in blocks:
    # The title and subtitle are adjacent Markdown lines in one block.
    if block.startswith('# '):
        for line in block.splitlines():
            if line.startswith('# '):
                text = line[2:]
                doc.add_paragraph(text, 'Title')
            elif line.startswith('## '):
                text = line[3:]
                doc.add_paragraph(text, 'Subtitle')
            else:
                raise ValueError(line)
            expected.append(text)
    elif block.startswith('### '):
        text = block[4:]
        p = doc.add_paragraph(text, 'Heading 1')
        if text == '阅读文献':
            ref_mode = True
            p.paragraph_format.page_break_before = True
        expected.append(text)
    else:
        p = doc.add_paragraph(block)
        if ref_mode:
            pf = p.paragraph_format
            pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
            pf.first_line_indent = Cm(-0.65)
            pf.left_indent = Cm(0.65)
            pf.line_spacing = Pt(16)
            pf.space_after = Pt(10)
            pf.keep_together = True
            for run in p.runs:
                run.font.size = Pt(11)
        expected.append(block)

settings = doc.settings.element
update = OxmlElement('w:updateFields')
update.set(qn('w:val'), 'true')
settings.append(update)
doc.core_properties.title = '让过去保有被重新理解的可能——档案生产中的解释权与历史责任'
doc.core_properties.subject = 'HY6101 Combined Essay 2 中文稿'
doc.core_properties.author = ''
doc.core_properties.last_modified_by = ''
doc.core_properties.keywords = 'HY6101, Combined Essay 2, 档案, 历史责任'
doc.core_properties.comments = ''
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUTPUT)

saved = Document(OUTPUT)
actual = [p.text for p in saved.paragraphs if p.text.strip()]
assert actual == expected
assert not saved.tables
assert all('待补' not in p and 'TODO' not in p for p in actual)
sources = [
    ROOT / 'seminar 7&8/HY6101_Seminar7-8_Reading_Paper_中文稿.docx',
    ROOT / 'seminar9&10/HY6101_第9—10周阅读思考_中文版.docx',
]
data = {
    'output': str(OUTPUT),
    'sha256': sha(OUTPUT),
    'source_sha256': {str(p): sha(p) for p in sources},
    'body_han_characters_excluding_titles_headings_punctuation_latin_references': han_count,
    'body_han_characters_including_titles_headings': len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]',md.split('### 阅读文献')[0])),
    'body_nonspace_characters_excluding_titles_headings_references': len(re.sub(r'\s', '', ''.join(body))),
    'body_paragraphs': len(body),
    'body_markdown_to_word_parity': actual == expected,
    'references': 7,
    'section_organization': 'thematic comparative argument, not weekly reading summaries',
    'sources_modified': False,
}
(AUDIT / 'content_check.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(data, ensure_ascii=False, indent=2))
