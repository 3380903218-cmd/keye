from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile
import json
import re

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.packuri import PackURI
from docx.opc.part import Part
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from lxml import etree as E

ROOT = Path('/Users/arourouwed/Desktop/NUS/2026-1/HY6101')
AUDIT = ROOT / '.essay2_english_20261026'
SOURCE = ROOT / 'seminar 11/HY6101_Combined_Essay2_中文版.docx'
OUTPUT = ROOT / 'seminar 11/HY6101_Combined_Essay2_English.docx'
MD = AUDIT / 'essay2_english.md'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XML = 'http://www.w3.org/XML/1998/namespace'
VOLUME = 'Archives, Documentation, and Institutions of Social Memory: Essays from the Sawyer Seminar'
EDITORS = 'Francis X. Blouin Jr. and William G. Rosenberg'
DOI = 'https://doi.org/10.3998/mpub.93171'


def hash_file(p):
    return sha256(p.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def full_chapter(author, title, pages):
    return f'{author}, “{title},” in *{VOLUME}*, ed. {EDITORS} (University of Michigan Press, 2006), {pages}.'


notes = {
    'N01': full_chapter('Kathleen Marquis', 'Not Dragon at the Gate but Research Partner: The Reference Archivist as Mediator', '36–37'),
    'N02': full_chapter('Patrick Geary', 'Medieval Archivists as Authors: Social Memory and Archival Memory', '106–11'),
    'N03': full_chapter('Terry Cook', 'Remembering the Future: Appraisal of Records and the Role of Archives in Constructing Social Memory', '169–70, 176–78'),
    'N04': full_chapter('Elizabeth Yakel', 'Archival Representation', '151–53'),
    'N05': 'Marquis, “Not Dragon at the Gate but Research Partner,” 38–39.',
    'N06': full_chapter('Beatrice S. Bartlett', 'Qing Statesmen, Archivists, and Historians and the Question of Memory', '422–23'),
    'N07': 'Bartlett, “Qing Statesmen, Archivists, and Historians,” 417–18.',
    'N08': 'Doreen Lee, *Activist Archives: Youth Culture and the Political Past in Indonesia* (Duke University Press, 2016), 171–77, 186–88; Cook, “Remembering the Future,” 169–70.',
    'N09': 'Lee, *Activist Archives*, 25–30, 57–59.',
    'N10': 'Lee, *Activist Archives*, 168–70.',
    'N11': 'Lee, *Activist Archives*, 181–82.',
    'N12': full_chapter('James M. O’Toole', 'Between Veneration and Loathing: Loving and Hating Documents', '43–45'),
    'N13': 'O’Toole, “Between Veneration and Loathing,” 43–45.',
    'N14': 'Bartlett, “Qing Statesmen, Archivists, and Historians,” 417–18.',
    'N15': 'Lee, *Activist Archives*, 44–45.',
}

chapters = [
    ('Bartlett, Beatrice S.', 'Qing Statesmen, Archivists, and Historians and the Question of Memory', '417–26'),
    ('Cook, Terry', 'Remembering the Future: Appraisal of Records and the Role of Archives in Constructing Social Memory', '169–81'),
    ('Geary, Patrick', 'Medieval Archivists as Authors: Social Memory and Archival Memory', '106–13'),
    ('Marquis, Kathleen', 'Not Dragon at the Gate but Research Partner: The Reference Archivist as Mediator', '36–42'),
    ('O’Toole, James M.', 'Between Veneration and Loathing: Loving and Hating Documents', '43–53'),
    ('Yakel, Elizabeth', 'Archival Representation', '151–63'),
]
bibliography = [f'{author}. “{title}.” In *{VOLUME}*, edited by {EDITORS}, {pages}. University of Michigan Press, 2006. {DOI}.' for author, title, pages in chapters]
bibliography.append('Lee, Doreen. *Activist Archives: Youth Culture and the Political Past in Indonesia*. Duke University Press, 2016. https://dukeupress.edu/activist-archives.')
bibliography.sort(key=lambda s: s.casefold())

metadata = {
    'citation_system': 'Chicago Notes and Bibliography, 18th edition; full first notes, shortened later notes, alphabetized bibliography',
    'format_guide': 'https://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-1.html',
    'publisher_verification': [
        {'url': 'https://press.umich.edu/Books/A/Archives-Documentation-and-Institutions-of-Social-Memory', 'verified': 'Volume title, editors, University of Michigan Press, 2006 copyright; DOI 10.3998/mpub.93171'},
        {'url': 'https://dukeupress.edu/activist-archives', 'verified': 'Doreen Lee, full title, Duke University Press, 2016'},
    ],
    'edition_decision': 'Cite the 2006 collected volume matching the course excerpts and their printed pagination; do not substitute the earlier journal versions of individual essays.',
    'chapter_ranges_from_course_pdf_printed_page_markers': [{'author': author, 'title': title, 'pages': pages} for author, title, pages in chapters],
    'pinpoint_checks': {
        'N01': 'Marquis 36–37: partnership and mediation',
        'N02': 'Geary 106–111: authorship, cartularies, authority and compilation',
        'N03': 'Cook 169–170, 176–178: appraisal, future users, functions and context',
        'N04': 'Yakel 151–153: representation, classification and access',
        'N05': 'Marquis 38–39: nuclear medicine example',
        'N06': 'Bartlett 422–423: Zhong Renjie case; published text confirms pinyin spelling',
        'N07': 'Bartlett 417–418: preservation of forbidden books',
        'N08': 'Lee page ranges retained from user’s Seminar 7–8 Chinese draft; Cook 169–170 contextualizes social memory responsibility',
        'N09': 'Lee 25–30, 57–59 retained from approved Chinese source',
        'N10': 'Lee 168–170 retained from approved Chinese source',
        'N11': 'Lee 181–182 retained from approved Chinese source',
        'N12': 'O’Toole 43–45: original documents, public ceremony and emotional significance',
        'N13': 'O’Toole 43–45: Stasi files, hostility and preservation',
        'N14': 'Bartlett 417–418: secrecy, preservation and official archives',
        'N15': 'Lee 44–45 retained from approved Chinese source',
    },
    'notes': notes,
    'bibliography': bibliography,
    'new_readings_or_substantive_claims_added': False,
}
write_json(AUDIT / 'citation_verification.json', metadata)

source_blocks = json.loads((AUDIT / 'source_paragraphs.json').read_text())
source_boundary = next(i for i, x in enumerate(source_blocks) if x['text'] == '阅读文献')
blocks = []
for block in MD.read_text(encoding='utf-8').split('\n\n'):
    block = block.strip()
    if not block:
        continue
    if block.startswith('# '):
        for line in block.splitlines():
            blocks.append(('Title' if line.startswith('# ') else 'Subtitle', line.split(' ', 1)[1]))
    elif block.startswith('### '):
        blocks.append(('Heading 1', block[4:]))
    else:
        blocks.append(('Normal', block))
assert len(blocks) == source_boundary == 54
assert [style for style, _ in blocks] == [x['style'] for x in source_blocks[:source_boundary]]
assert hash_file(SOURCE) == hash_file(AUDIT / 'approved_chinese_source.docx')


def set_font(style, size, bold=False, italic=False):
    style.font.name = 'Times New Roman'
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = italic
    style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rpr.insert(0, rf)
    for attr in list(rf.attrib):
        if 'theme' in attr.lower():
            del rf.attrib[attr]
    for attr in ['ascii', 'hAnsi', 'cs', 'eastAsia']:
        rf.set(qn('w:' + attr), 'Times New Roman')
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'en-US')
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


def inline_runs(paragraph, text):
    for token in re.split(r'(\*[^*]+\*)', text):
        if not token:
            continue
        run = paragraph.add_run(token[1:-1] if token.startswith('*') and token.endswith('*') else token)
        if token.startswith('*') and token.endswith('*'):
            run.italic = True


def plain(text):
    return re.sub(r'\[\[N\d+\]\]', '', text).replace('*', '')


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Inches(1)
sec.header_distance = sec.footer_distance = Inches(0.5)
set_font(doc.styles['Normal'], 12)
pf = doc.styles['Normal'].paragraph_format
pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
pf.first_line_indent = Inches(0.5)
pf.line_spacing = Pt(23)
pf.space_after = Pt(0)
pf.widow_control = True

for name, size in [('Title', 16), ('Subtitle', 12), ('Heading 1', 13), ('Header', 9), ('Footer', 9)]:
    set_font(doc.styles[name], size, bold=name in ['Title', 'Heading 1'])
    pf = doc.styles[name].paragraph_format
    pf.first_line_indent = Pt(0)
    pf.line_spacing = Pt(18 if name in ['Title','Subtitle','Heading 1'] else 12)

for name in ['Title', 'Subtitle']:
    pf = doc.styles[name].paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.keep_with_next = True
    pf.space_after = Pt(8 if name == 'Title' else 20)
pf = doc.styles['Heading 1'].paragraph_format
pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
pf.keep_with_next = True
pf.keep_together = True
pf.space_before, pf.space_after = Pt(12), Pt(8)

for name, kind in [('Footnote Text', WD_STYLE_TYPE.PARAGRAPH), ('Footnote Reference', WD_STYLE_TYPE.CHARACTER), ('Bibliography Entry', WD_STYLE_TYPE.PARAGRAPH)]:
    if name not in doc.styles:
        doc.styles.add_style(name, kind)
set_font(doc.styles['Footnote Text'], 10)
pf = doc.styles['Footnote Text'].paragraph_format
pf.first_line_indent = Inches(0.25)
pf.line_spacing, pf.space_after = Pt(12), Pt(4)
pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
pf.widow_control = True
set_font(doc.styles['Footnote Reference'], 10)
doc.styles['Footnote Reference'].font.superscript = True
set_font(doc.styles['Bibliography Entry'], 11)
pf = doc.styles['Bibliography Entry'].paragraph_format
pf.left_indent, pf.first_line_indent = Inches(0.5), Inches(-0.5)
pf.line_spacing, pf.space_after = Pt(14), Pt(10)
pf.keep_together = True
pf.alignment = WD_ALIGN_PARAGRAPH.LEFT

hp = sec.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hp.add_run('HY6101  |  Combined Essay 2')
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
field = OxmlElement('w:fldSimple')
field.set(qn('w:instr'), 'PAGE')
r = OxmlElement('w:r')
t = OxmlElement('w:t')
t.text = '1'
r.append(t)
field.append(r)
fp._p.append(field)

footnotes_root = E.Element(qn('w:footnotes'), nsmap={'w': W})
for ident, typ, child in [(-1, 'separator', 'separator'), (0, 'continuationSeparator', 'continuationSeparator')]:
    n = E.SubElement(footnotes_root, qn('w:footnote'))
    n.set(qn('w:id'), str(ident))
    n.set(qn('w:type'), typ)
    p = E.SubElement(n, qn('w:p'))
    rr = E.SubElement(p, qn('w:r'))
    E.SubElement(rr, qn('w:' + child))

note_order = []
alignment = []
for i, (style, content) in enumerate(blocks):
    p = doc.add_paragraph(style=style)
    if content == 'Conclusion':
        p.paragraph_format.page_break_before = True
    for token in re.split(r'(\[\[N\d+\]\])', content):
        m = re.fullmatch(r'\[\[(N\d+)\]\]', token)
        if not m:
            inline_runs(p, token)
            continue
        key = m.group(1)
        assert key not in note_order
        note_order.append(key)
        number = len(note_order)
        ref_run = p.add_run(style='Footnote Reference')
        ref = OxmlElement('w:footnoteReference')
        ref.set(qn('w:id'), str(number))
        ref_run._r.append(ref)
        note = E.SubElement(footnotes_root, qn('w:footnote'))
        note.set(qn('w:id'), str(number))
        np = doc.add_paragraph(style='Footnote Text')
        nr = np.add_run(style='Footnote Reference')
        nr._r.append(OxmlElement('w:footnoteRef'))
        np.add_run(' ')
        inline_runs(np, notes[key])
        note.append(np._p)
    alignment.append({'source_index': i, 'source_style': source_blocks[i]['style'], 'source_zh': source_blocks[i]['text'], 'translation_en': plain(content), 'footnotes': re.findall(r'\[\[(N\d+)\]\]', content)})

assert note_order == list(notes)
head = doc.add_paragraph('Bibliography', style='Heading 1')
head.paragraph_format.page_break_before = True
for entry in bibliography:
    p = doc.add_paragraph(style='Bibliography Entry')
    inline_runs(p, entry)

footnote_part = Part(PackURI('/word/footnotes.xml'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml', E.tostring(footnotes_root, encoding='UTF-8', xml_declaration=True, standalone=True), doc.part.package)
doc.part.relate_to(footnote_part, RT.FOOTNOTES)
fpr = OxmlElement('w:footnotePr')
for tag, value in [('pos', 'pageBottom'), ('numFmt', 'decimal'), ('numStart', '1'), ('numRestart', 'continuous')]:
    node = OxmlElement('w:' + tag)
    node.set(qn('w:val'), value)
    fpr.append(node)
for ident in [-1, 0]:
    ref = OxmlElement('w:footnote')
    ref.set(qn('w:id'), str(ident))
    fpr.append(ref)
settings = doc.settings.element
compat_anchor = settings.find(qn('w:compat'))
if compat_anchor is not None:
    settings.insert(list(settings).index(compat_anchor), fpr)
else:
    settings.insert(0, fpr)
update = OxmlElement('w:updateFields')
update.set(qn('w:val'), 'true')
settings.insert(list(settings).index(fpr), update)
compat = doc.settings.element.find(qn('w:compat'))
if compat is not None:
    for setting in compat:
        if setting.get(qn('w:name')) == 'compatibilityMode':
            setting.set(qn('w:val'), '15')
doc.core_properties.title = 'From Keeping Documents to Understanding History: Rethinking the Archival Profession and Archives'
doc.core_properties.subject = 'HY6101 Combined Essay 2 — English translation'
doc.core_properties.author = ''
doc.core_properties.last_modified_by = ''
doc.core_properties.comments = ''
doc.save(OUTPUT)

saved = Document(OUTPUT)
assert [p.text for p in saved.paragraphs[:54]] == [plain(content) for _, content in blocks]
assert len(saved.paragraphs) == 62
assert len([p for p in saved.paragraphs[:54] if p.style.name == 'Normal']) == 46
with ZipFile(OUTPUT) as z:
    root = E.fromstring(z.read('word/document.xml'))
    ns = {'w': W}
    refs = root.findall('.//w:footnoteReference', ns)
    notes_xml = E.fromstring(z.read('word/footnotes.xml'))
    actual_notes = notes_xml.findall('w:footnote', ns)
    assert [r.get(qn('w:id')) for r in refs] == [str(n) for n in range(1, 16)]
    assert len(actual_notes) == 17
    assert not any('comment' in n.lower() for n in z.namelist())
    assert all(len(n.findall('w:p', ns)) == 1 for n in actual_notes)

body_words = len(re.findall(r"\b[\w’'-]+\b", ' '.join(plain(content) for style, content in blocks if style == 'Normal')))
write_json(AUDIT / 'paragraph_alignment.json', alignment)
write_json(AUDIT / 'content_check.json', {
    'source_path': str(SOURCE), 'source_sha256': hash_file(SOURCE),
    'output_path': str(OUTPUT), 'output_sha256': hash_file(OUTPUT),
    'source_body_paragraphs': 46, 'translation_body_paragraphs': 46,
    'source_and_translation_blocks_before_bibliography': 54,
    'paragraph_order_and_style_roles_preserved': True,
    'translation_body_word_count': body_words,
    'native_word_footnotes': 15, 'bibliography_entries': 7,
    'bibliography_alphabetized': True,
    'citations_verified_against_local_printed_pages_and_publisher_metadata': True,
    'chinese_source_unchanged': hash_file(SOURCE) == hash_file(AUDIT / 'approved_chinese_source.docx'),
    'comments_from_chinese_review_not_included_in_translation': True,
    'translation_to_docx_text_parity': True,
})
print(json.dumps({'output': str(OUTPUT), 'body_words': body_words, 'native_footnotes': 15, 'bibliography_entries': 7, 'source_unchanged': True}, ensure_ascii=False))
