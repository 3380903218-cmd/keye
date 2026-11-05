from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from pptx import Presentation
import hashlib, json

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[1]
WORK = Path('/tmp/hy5305-curatorial-work')
FILE = ROOT / 'HY5305_Porcelain_in_Translation_Curatorial_Edit.pptx'
BASELINE = SOURCE / 'archive/before_light_cover_2026-10-14' / FILE.name
assert hashlib.sha256(FILE.read_bytes()).digest() == hashlib.sha256(BASELINE.read_bytes()).digest()

# Generate only the revised cover, without rebuilding or saving the other pages.
builder = SOURCE / 'build_curatorial_presentation.py'
prefix = builder.read_text().split('# 2. Full object')[0]
scope = {'__file__': str(builder), '__name__': '__cover_only__'}
exec(compile(prefix, str(builder), 'exec'), scope)
cover = scope['pres'].slides[0]
current = Presentation(FILE).slides[0]
for image in cover._element.xpath('.//a:blip'):
    rid = image.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    assert cover.part.related_part(rid).blob == current.part.related_part(rid).blob
cover_xml = etree.tostring(cover._element, encoding='UTF-8', xml_declaration=True, standalone=True)
staged = WORK / 'light-cover-updated.pptx'
with ZipFile(FILE) as before, ZipFile(staged, 'w') as after:
    for info in before.infolist():
        after.writestr(info, cover_xml if info.filename == 'ppt/slides/slide1.xml' else before.read(info.filename))
with ZipFile(BASELINE) as before, ZipFile(staged) as after:
    changed = [name for name in before.namelist() if before.read(name) != after.read(name)]
assert changed == ['ppt/slides/slide1.xml'], changed
staged.replace(FILE)

display_file = SOURCE / 'presentation_display_text.json'
display = json.loads(display_file.read_text())
display[0] = scope['display'][0]
display_file.write_text(json.dumps(display, ensure_ascii=False, indent=2))
checks_file = SOURCE / 'presentation_layout_checks.json'
checks = [x for x in json.loads(checks_file.read_text()) if not x['shape'].startswith('S1')]
checks.extend(scope['t'].checks)
assert all(x['fits'] for x in checks)
checks_file.write_text(json.dumps(checks, ensure_ascii=False, indent=2))
references_file = SOURCE / 'design_references.json'
references = json.loads(references_file.read_text())
references['light_cover_update'] = {
    'date': '2026-10-14',
    'visual_references_inspected': [
        {'title': 'Art Gallery — Envato', 'url': 'https://elements.envato.com/art-gallery-VYYQALT', 'used': 'Light editorial backgrounds, serif typography, artwork margins'},
        {'title': 'Art Gallery Presentation — Envato', 'url': 'https://elements.envato.com/art-gallery-presentation-YJP5Z8K', 'used': 'Comparison of bright presentation layouts'},
    ],
    'palette': {'porcelain_white': '#FAFAF7', 'light_stone': '#E8E6E1', 'warm_ink': '#3E3731', 'terracotta': '#8A5345'},
    'assets_imported_from_templates': False,
}
references_file.write_text(json.dumps(references, ensure_ascii=False, indent=2))
print('Updated cover: porcelain white, light stone display field, white poster mount, warm text and restrained terracotta accents.')
print('Only slide1.xml changed; all remaining pages, notes and media are byte-identical.')
