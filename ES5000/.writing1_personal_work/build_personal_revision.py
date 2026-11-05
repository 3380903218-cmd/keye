from pathlib import Path
import json, hashlib
from copy import deepcopy
from docx import Document
from docx.text.paragraph import Paragraph
from docx.shared import Inches, Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'Writing_Assignment_1_personal_revision'
WORK = BASE / '.writing1_personal_work'
NAME = 'G6_WANG XIWEN_Writing Assignment 1_personal revision'

P1 = "Loneliness can arise when living far from home reduces familiar companionship and opportunities for everyday interaction. Distance from family may leave people without the company they want during ordinary activities, especially before new friendships develop. For example, I am studying abroad for a master's degree and living alone. This is my first time studying so far from home. I feel lonely when I have to buy daily necessities by myself or spend weekends alone at home. These experiences show how routine situations can make the absence of companionship more noticeable. Ozdamar (2025) describes conversations during shared meals as an important source of social connection. This suggests that everyday interactions can provide a sense of belonging that may be missed when living independently. Being alone does not always produce loneliness, but it can feel painful when company is desired. Overall, distance from home and limited everyday companionship can contribute to loneliness."
P2 = "For people living away from home, loneliness can affect emotional well-being, sleep and the ability to manage everyday responsibilities. In their review of research on university students, Ellard et al. (2023) report associations between loneliness and anxiety, stress, depression, sleep problems and lower life satisfaction. These findings illustrate possible consequences of feeling disconnected, although they do not prove a simple causal relationship. For someone living far from home, ordinary difficulties may feel more overwhelming without familiar emotional support. Sleep problems may also leave a person tired the next day, potentially affecting concentration and the ability to complete daily tasks. As low mood and fatigue accumulate, work, study and household responsibilities may become harder to manage. Reduced energy may also make it more difficult to maintain social contact. Overall, loneliness may extend beyond moments of sadness, affecting both emotional health and a person's ability to cope with everyday demands."

REFS = [
    {'authors': 'Ellard, O. B., Dennison, C., & Tuomainen, H.', 'year': '2023',
     'title': 'Review: Interventions addressing loneliness amongst university students: A systematic review.',
     'journal': 'Child and Adolescent Mental Health', 'volume': '28', 'issue': '4', 'pages': '512–523', 'doi': 'https://doi.org/10.1111/camh.12614'},
    {'authors': 'Ozdamar, M.', 'year': '2025, May 9',
     'title': 'Sharing a meal with friends and family could be the key to better mental health.',
     'journal': 'National Geographic', 'doi': 'https://www.nationalgeographic.com/health/article/communal-dining-loneliness-epidemic'},
]

def hyperlink(p, url):
    link = OxmlElement('w:hyperlink')
    link.set(qn('r:id'), p.part.relate_to(url, RT.HYPERLINK, is_external=True))
    run = OxmlElement('w:r')
    props = OxmlElement('w:rPr')
    color = OxmlElement('w:color'); color.set(qn('w:val'), '0563C1'); props.append(color)
    underline = OxmlElement('w:u'); underline.set(qn('w:val'), 'single'); props.append(underline)
    run.append(props)
    t = OxmlElement('w:t'); t.text = url; run.append(t)
    link.append(run); p._p.append(link)

def single(p, after=0):
    p.paragraph_format.line_spacing = 1
    p.paragraph_format.space_after = Pt(after)
    return p

counts = [len(P1.split()), len(P2.split())]
assert all(140 <= n <= 155 for n in counts), counts
assert sum(counts) <= 300, counts

doc = Document(BASE / 'writing 1 draft.docx')
for child in list(doc._element.body):
    if child.tag != qn('w:sectPr'):
        doc._element.body.remove(child)
section = doc.sections[0]
section.page_width = Mm(210); section.page_height = Mm(297)
section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(1)
section.footer_distance = Inches(.5)
style = doc.styles['Normal']
style.font.name = 'Times New Roman'; style.font.size = Pt(12)
style.font.color.rgb = RGBColor(0, 0, 0)
style.paragraph_format.line_spacing = 1.5
style.paragraph_format.space_before = Pt(0)
style.paragraph_format.space_after = Pt(12)
style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
style.paragraph_format.first_line_indent = Inches(0)
style.paragraph_format.widow_control = True

for text in ['WANG XIWEN', 'ES5000 Group 6', '15 September 2026']:
    single(doc.add_paragraph(text))
TITLE = 'Loneliness Away from Home: Causes and Effects'
title = doc.add_paragraph(TITLE)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.paragraph_format.space_before = Pt(12)
title.paragraph_format.space_after = Pt(12)
title.runs[0].bold = True
for text in [P1, P2]:
    p = doc.add_paragraph(text)
    p.paragraph_format.keep_together = True
single(doc.add_paragraph(f'W={sum(counts)}'))

h = single(doc.add_paragraph('References'), 8)
h.runs[0].bold = True
h.paragraph_format.page_break_before = True
h.paragraph_format.keep_with_next = True
for ref in REFS:
    p = single(doc.add_paragraph(), 10)
    p.paragraph_format.left_indent = Inches(.5)
    p.paragraph_format.first_line_indent = Inches(-.5)
    p.paragraph_format.keep_together = True
    p.add_run(f"{ref['authors']} ({ref['year']}). {ref['title']} ")
    if 'volume' in ref:
        p.add_run(f"{ref['journal']}, {ref['volume']}").italic = True
        p.add_run(f"({ref['issue']}), {ref['pages']}. ")
    else:
        p.add_run(ref['journal']).italic = True
        p.add_run('. ')
    hyperlink(p, ref['doi'])

h = single(doc.add_paragraph('Declaration'), 8)
h.paragraph_format.space_before = Pt(8)
h.paragraph_format.keep_with_next = True
h.runs[0].bold = True
declaration = Document(BASE / '第二周/2.3a ES5000 Assignment Declaration.docx')
started = False
for original_p in declaration.paragraphs:
    txt = ''.join(original_p._p.xpath('.//w:t/text()')).strip()
    if txt.startswith('I understand what plagiarism'):
        started = True
    if not started or not txt:
        continue
    copied = deepcopy(original_p._p)
    for t in copied.xpath('.//w:t'):
        if t.text:
            t.text = t.text.replace('[AI tool name, e.g., GPT-4.1]', 'OpenAI Codex')
    # Preserve the original Word checkbox content controls, all unchecked.
    doc._element.body.insert_element_before(copied, 'w:sectPr')
    p = Paragraph(copied, doc._body)
    p.style = doc.styles['Normal']
    single(p, 4)
    if txt.startswith('☐ to '):
        p.paragraph_format.left_indent = Inches(0)

footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), 'PAGE')
run = OxmlElement('w:r'); text = OxmlElement('w:t'); text.text = '1'; run.append(text); field.append(run)
footer._p.append(field)
doc.core_properties.title = TITLE
doc.core_properties.author = 'WANG XIWEN'
doc.core_properties.comments = 'Revision of the student-supplied draft with cited sources. AI declaration to be completed by the student.'
path = OUT / (NAME + '.docx')
doc.save(path)

md = '# ' + TITLE + '\n\n' + P1 + '\n\n' + P2 + f'\n\nW={sum(counts)}\n\n## References\n\n'
for ref in REFS:
    publication = f"*{ref['journal']}, {ref['volume']}*({ref['issue']}), {ref['pages']}" if 'volume' in ref else f"*{ref['journal']}*"
    md += f"{ref['authors']} ({ref['year']}). {ref['title']} {publication}. {ref['doi']}\n\n"
(WORK / 'revised_body.md').write_text(md)
(WORK / 'content_master.json').write_text(json.dumps({'paragraphs':[P1,P2], 'counts':counts, 'total':sum(counts), 'references':REFS}, ensure_ascii=False, indent=2))
print(json.dumps({'path':str(path), 'counts':counts, 'total':sum(counts), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}, ensure_ascii=False))
