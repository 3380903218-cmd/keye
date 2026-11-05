from copy import deepcopy
from pathlib import Path
import hashlib
import json

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor
from docx.text.paragraph import Paragraph
from docx.opc.constants import RELATIONSHIP_TYPE as RT


BASE = Path(__file__).resolve().parent.parent
WORK = BASE / '.writing2_work'
OUT = BASE / 'writing 2'
OUTPUT = OUT / 'G6_WANG XIWEN_p-s essay.docx'
if OUTPUT.exists():
    raise SystemExit('The reviewed Word draft already exists. Edit it in place to preserve comments and student declaration choices.')
TITLE = 'Rebuilding Connections: Addressing Loneliness among University Students'

PARAGRAPHS = ['University life can create new opportunities while weakening familiar sources of companionship. Quinn (2025) explains that loneliness involves unmet needs for connection and belonging, rather than simply being alone. For students adjusting to a different social environment, maintaining meaningful relationships can therefore be challenging. To address this problem, students should keep in touch with family and old friends, develop shared interests and take part in volunteering or internships.', 'University brings together students from different regions, and for some, it is their first experience of living far from home for an extended period. Unlike relatively stable secondary-school classes, university courses may involve changing groups of classmates, making close friendships harder to establish. Ellard et al. (2023) identify academic and social pressures as features of this transition. Uncertainty about future careers may further intensify loneliness when familiar support is absent. How can students rebuild a sense of belonging under these conditions? Maintaining contact with trusted people and joining regular activities with shared goals could provide emotional support and new connections. Together, these responses offer a way to rebuild support while adapting to greater independence.', 'Students can respond by maintaining existing relationships while building new ones through shared interests. Communication tools make regular contact with family and old friends possible despite geographical distance. For example, scheduled video calls can provide opportunities to discuss everyday experiences and personal worries. Such conversations may offer reassurance while students adjust to university. Meanwhile, developing hobbies through clubs or informal groups can bring students into repeated contact with people who share their interests. Ellard et al. (2023) found promising evidence for interventions promoting social connectedness, although the size of the benefits remained unclear. Joining a painting group or sports club could thus create opportunities for companionship. Developing a hobby can also give students a satisfying focus beyond coursework. Together, familiar support and new friendships may help students feel more connected.', 'Volunteering and internships may offer further opportunities for connection and personal development. Ellard et al. (2023) report that interventions promoting social interaction show promise in reducing student loneliness. Applying this principle, a student could join a community project, cooperate with a team and take responsibility for a practical task. Working towards shared goals may create relationships while developing communication and problem-solving skills. Internships could also help students explore career interests and feel more confident about future choices. Students should choose manageable commitments that allow meaningful cooperation without adding excessive academic pressure.', "In conclusion, university students' loneliness can reflect separation from familiar relationships, changing peer groups and pressure about studies and the future. Keeping in touch, developing hobbies and participating in volunteering or internships offer complementary responses. Students should seek both supportive relationships and manageable opportunities for personal development as they adapt to university life."]

REFERENCES = [
    {
        'author': 'Ellard, O. B., Dennison, C., & Tuomainen, H.',
        'date': '2023',
        'title': 'Review: Interventions addressing loneliness amongst university students: A systematic review.',
        'journal': 'Child and Adolescent Mental Health',
        'volume': '28', 'issue': '4', 'pages': '512–523',
        'url': 'https://doi.org/10.1111/camh.12614',
    },
    {
        'author': 'Quinn, K.', 'date': '2025, March 4',
        'title': 'Reducing loneliness on college campuses.',
        'site': 'Psychology Today',
        'url': 'https://www.psychologytoday.com/us/blog/optimized/202503/reducing-loneliness-on-college-campuses',
    },
]


def single(paragraph, after=0):
    paragraph.paragraph_format.line_spacing = 1
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(after)
    return paragraph


def link(paragraph, url):
    element = OxmlElement('w:hyperlink')
    element.set(qn('r:id'), paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True))
    run = OxmlElement('w:r')
    props = OxmlElement('w:rPr')
    font = OxmlElement('w:rFonts')
    font.set(qn('w:ascii'), 'Times New Roman')
    font.set(qn('w:hAnsi'), 'Times New Roman')
    props.append(font)
    size = OxmlElement('w:sz'); size.set(qn('w:val'), '24'); props.append(size)
    run.append(props)
    text = OxmlElement('w:t'); text.text = url; run.append(text)
    element.append(run)
    paragraph._p.append(element)


def heading(doc, text):
    p = single(doc.add_paragraph(text), 8)
    p.paragraph_format.keep_with_next = True
    p.runs[0].bold = True
    return p


doc = Document()
section = doc.sections[0]
section.page_width = Mm(210); section.page_height = Mm(297)
section.top_margin = section.bottom_margin = Inches(1)
section.left_margin = section.right_margin = Inches(1)
section.footer_distance = Inches(.5)
normal = doc.styles['Normal']
normal.font.name = 'Times New Roman'
normal.font.size = Pt(12)
normal.font.color.rgb = RGBColor(0, 0, 0)
normal.paragraph_format.line_spacing = 1.5
normal.paragraph_format.space_before = Pt(0)
normal.paragraph_format.space_after = Pt(18)
normal.paragraph_format.first_line_indent = Inches(0)
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
normal.paragraph_format.widow_control = True

for value in ['WANG XIWEN', 'ES5000 Group 6', '20 October 2026']:
    single(doc.add_paragraph(value))
title = doc.add_paragraph(TITLE)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.paragraph_format.space_before = Pt(12)
title.paragraph_format.space_after = Pt(18)
title.paragraph_format.keep_with_next = True
title.runs[0].bold = True

for text in PARAGRAPHS:
    doc.add_paragraph(text)
counts = [len(text.split()) for text in PARAGRAPHS]
assert 450 <= sum(counts) <= 500
single(doc.add_paragraph(f'W={sum(counts)}'), 18)

heading(doc, 'References')
for ref in REFERENCES:
    p = single(doc.add_paragraph(), 10)
    p.paragraph_format.left_indent = Inches(.5)
    p.paragraph_format.first_line_indent = Inches(-.5)
    p.paragraph_format.keep_together = True
    p.add_run(f"{ref['author']} ({ref['date']}). ")
    if 'journal' in ref:
        p.add_run(ref['title'] + ' ')
        p.add_run(f"{ref['journal']}, {ref['volume']}").italic = True
        p.add_run(f"({ref['issue']}), {ref['pages']}. ")
    else:
        p.add_run(ref['title']).italic = True
        p.add_run(f" {ref['site']}. ")
    link(p, ref['url'])

heading(doc, 'Declaration')
note = single(doc.add_paragraph("AI use in this draft: OpenAI Codex generated the initial draft and revised it using the student's own ideas, with assistance in English expression, source checking and formatting. The student should review and complete the declaration below."), 8)

declaration_source = BASE / '第二周/2.3a ES5000 Assignment Declaration.docx'
template = Document(declaration_source)
copying = False
declaration_paragraphs = []
for original in template.paragraphs:
    text = ''.join(original._p.xpath('.//w:t/text()')).strip()
    if text.startswith('I understand what plagiarism'):
        copying = True
    if not copying or not text:
        continue
    element = deepcopy(original._p)
    for t in element.xpath('.//w:t'):
        if t.text:
            t.text = t.text.replace('[AI tool name, e.g., GPT-4.1]', 'OpenAI Codex')
    doc._element.body.insert_element_before(element, 'w:sectPr')
    p = Paragraph(element, doc._body)
    p.style = normal
    single(p, 4)
    p.paragraph_format.keep_together = True
    for r in p.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
    declaration_paragraphs.append(p)

# Keep the template intact, with its checkbox content controls still unchecked.
# A draft does not attest that the student has already reviewed or revised it.
for p in [note] + declaration_paragraphs[:-1]:
    p.paragraph_format.keep_with_next = True

footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), 'PAGE')
run = OxmlElement('w:r')
t = OxmlElement('w:t'); t.text = '1'; run.append(t); field.append(run)
footer._p.append(field)

doc.core_properties.title = TITLE
doc.core_properties.author = 'WANG XIWEN'
doc.core_properties.subject = 'ES5000 Writing Assignment 2: Problem-solution essay draft'
doc.core_properties.comments = 'AI-assisted draft. The student must review, revise and complete the course declaration.'
OUT.mkdir(exist_ok=True)
doc.save(OUTPUT)

master = {
    'title': TITLE, 'paragraphs': PARAGRAPHS, 'paragraph_counts': counts,
    'body_word_count': sum(counts),
    'word_count_scope': 'Five essay paragraphs including in-text citations; excludes heading, title, W= line, references and declaration.',
    'references': REFERENCES,
    'focus': 'University students: separation from home, disrupted class relationships, academic pressure and uncertainty about future careers; maintaining familiar relationships, developing hobbies, and volunteering or internships.',
    'structure': ['Introduction and thesis', 'Problem: disrupted relationships and academic/career pressures', 'Solutions: contact with family and old friends; shared hobbies', 'Solution: volunteering or internships for connection, skills and career exploration', 'Conclusion and recommendation'],
    'student_identity_source': 'Prior ES5000 writing assignment and project decisions: WANG XIWEN; Group 6.',
    'date': '2026-10-20',
    'ai_declaration': 'Official template appended with tool name filled; all checkboxes deliberately unchecked for student completion.',
}
(WORK / 'content_master.json').write_text(json.dumps(master, ensure_ascii=False, indent=2))
(WORK / 'essay_body.md').write_text('# ' + TITLE + '\n\n' + '\n\n'.join(PARAGRAPHS) + f'\n\nW={sum(counts)}\n')
print(json.dumps({'output': str(OUTPUT), 'counts': counts, 'body_words': sum(counts), 'sha256': hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}, ensure_ascii=False))
