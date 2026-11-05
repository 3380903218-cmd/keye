from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from pptx import Presentation
import hashlib, json
import slide_toolkit as t

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[1]
WORK = Path('/tmp/hy5305-curatorial-work')
FILE = ROOT / 'HY5305_Porcelain_in_Translation_Curatorial_Edit.pptx'
BASELINE = SOURCE / 'archive/before_cover_update_2026-10-14' / FILE.name
assert hashlib.sha256(FILE.read_bytes()).digest() == hashlib.sha256(BASELINE.read_bytes()).digest(), 'Current deck differs from preserved editing baseline'

prs = Presentation(FILE)
slide = prs.slides[0]
for shape in slide.shapes:
    if shape.name == 'S1 — gallery background':
        shape.fill.fore_color.rgb = t.rgb('dark')
    elif shape.has_text_frame:
        colour = 'gold' if shape.name == 'S1 — presentation context' or shape.name.startswith('S1 — contents number') else 'ivory'
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.color.rgb = t.rgb(colour)

t.slide, t.svg, t.svg_defs = slide, [], []
t.text('S1 — presenter', 'Presented by Xiwen Wang', 154, 180.5, 148, 8, 15.5, 'ivory', t.SANS)
first_xml = etree.tostring(slide._element, encoding='UTF-8', xml_declaration=True, standalone=True)
staged = WORK / 'cover-updated.pptx'
with ZipFile(FILE) as before, ZipFile(staged, 'w') as after:
    for info in before.infolist():
        after.writestr(info, first_xml if info.filename == 'ppt/slides/slide1.xml' else before.read(info.filename))
with ZipFile(BASELINE) as before, ZipFile(staged) as after:
    changed = [name for name in before.namelist() if before.read(name) != after.read(name)]
assert changed == ['ppt/slides/slide1.xml'], changed
staged.replace(FILE)

# Keep the source SVG and its text inventory aligned with the surgical PPT edit.
svg_path = WORK / 'deck-preview/slide-1.svg'
svg = etree.parse(str(svg_path))
ns = {'svg': 'http://www.w3.org/2000/svg'}
svg.getroot().find('svg:rect', ns).set('fill', t.hexcol('dark'))
for text in svg.xpath('//svg:text', namespaces=ns):
    value = ''.join(text.itertext())
    colour = 'gold' if value == 'AN EXHIBITION IN THREE OBJECTS' or value in ['01','02','03'] and text.get('x') == '154' else 'ivory'
    text.set('fill', t.hexcol(colour))
svg.getroot().append(etree.fromstring(t.svg[0].encode()))
svg.write(str(svg_path), encoding='UTF-8', xml_declaration=True)
display = json.loads((SOURCE / 'presentation_display_text.json').read_text())
display[0] = [s.text for s in slide.shapes if s.has_text_frame and s.text]
(SOURCE / 'presentation_display_text.json').write_text(json.dumps(display, ensure_ascii=False, indent=2))
checks = json.loads((SOURCE / 'presentation_layout_checks.json').read_text())
checks.extend(t.checks)
(SOURCE / 'presentation_layout_checks.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2))
print('Updated only slide1.xml: charcoal background, light text, Presented by Xiwen Wang.')
print('Slides 2–5, notes, relationships and all media remain byte-identical to the baseline.')
