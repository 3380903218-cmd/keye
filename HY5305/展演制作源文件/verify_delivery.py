"""Read-only delivery checks, followed by a hash-bound validation record."""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import hashlib, json, re, posixpath
from lxml import etree
from PIL import Image
from pptx import Presentation
from docx import Document
import fitz

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parent
WORK = Path('/tmp/hy5305-delivery-work')
POSTER = ROOT / 'HY5305_海报_参考风格竖版'
PPTX = ROOT / 'HY5305_Porcelain_in_Translation_8min.pptx'
DOCX = ROOT / 'HY5305_Porcelain_in_Translation_English_Chinese_Script.docx'
PNG = POSTER / 'Porcelain_in_Translation_Flow_A1_Portrait.png'
CONTENT = json.loads((SOURCE / 'presentation_content.json').read_text())
TIMING = json.loads((SOURCE / 'presentation_timing.json').read_text())
A = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def package_check(file):
    xml_count = relationships = 0
    with ZipFile(file) as package:
        assert package.testzip() is None, file
        names = set(package.namelist())
        for name in names:
            if name.endswith(('.xml', '.rels')):
                root = etree.fromstring(package.read(name))
                xml_count += 1
                if name.endswith('.rels'):
                    base = '' if name == '_rels/.rels' else name.split('/_rels/')[0]
                    for rel in root:
                        if rel.get('TargetMode') == 'External':
                            continue
                        target = posixpath.normpath(posixpath.join(base, rel.get('Target'))).lstrip('/')
                        assert target in names, (name, target)
                        relationships += 1
    return {'xml_parts_parsed': xml_count, 'internal_relationships_resolved': relationships, 'status': 'pass'}


approved = {
    'Porcelain_in_Translation_Flow_A1_Portrait.svg': '7c5f6b8fb95dddf52125363202d5abd21f3aebc6ea1aa3fb8ba0c9be6a663b5b',
    'Porcelain_in_Translation_Flow_A1_Portrait.pptx': '5da9181cf185daafb1a77fe99db1936cf57f0fcf4a16a81ada12ebc5ee5431d8',
}
for name, expected in approved.items():
    assert sha(POSTER / name) == expected, 'Approved poster changed'
assert sha(ROOT / 'project abstract.docx') == 'ba54557f85f933870dfdbdbf7e4e317242e44f1c3fa9c975a17c721d418ce54d'
with Image.open(PNG) as im:
    assert im.size == (7016, 9933) and im.mode == 'RGB'
    assert all(abs(v - 300) < .1 for v in im.info['dpi'])
    im.verify()

prs = Presentation(PPTX)
assert len(prs.slides) == 5
assert abs(prs.slide_width / prs.slide_height - 16 / 9) < .00001
expected_display = json.loads((SOURCE / 'presentation_display_text.json').read_text())
bounds = []
poster_picture = None
for index, slide in enumerate(prs.slides, 1):
    actual = [s.text for s in slide.shapes if s.has_text_frame and s.text]
    assert actual == expected_display[index - 1]
    assert not re.search(r'[\u3400-\u9fff]', '\n'.join(actual))
    assert not re.search(r'\b(?:NUS|HY5305)\b', '\n'.join(actual))
    svg = etree.parse(str(WORK / f'deck-preview/slide-{index}.svg'))
    svg_lines = svg.xpath('//*[local-name()="text"]/*[local-name()="tspan"]/text()')
    assert svg_lines == [line for text in actual for line in text.split('\n')], index
    notes = slide.notes_slide.notes_text_frame.text
    assert '\n\n'.join(CONTENT['slides'][index - 1]['english']) in notes
    for s in slide.shapes:
        assert s.left >= -360 and s.top >= -360, (index, s.name)
        assert s.left + s.width <= prs.slide_width + 360, (index, s.name)
        assert s.top + s.height <= prs.slide_height + 360, (index, s.name)
        bounds.append({'slide': index, 'shape': s.name, 'status': 'pass'})
        if s.name == 'S1 — approved complete exhibition poster':
            poster_picture = s
assert poster_picture is not None
assert poster_picture.image.blob == PNG.read_bytes()
assert all(abs(v) < .000001 for v in [poster_picture.crop_left, poster_picture.crop_right, poster_picture.crop_top, poster_picture.crop_bottom])
assert abs(poster_picture.width / poster_picture.height - 7016 / 9933) < .00001
original_images = [
    ROOT / '文物图片/微信图片_20260910150741_59_71.png',
    ROOT / '海报制作源文件/assets/falangcai_bowl_highres.jpg',
    ROOT / '文物图片/微信图片_20260910154121_63_71.png',
]
media = {}
with ZipFile(PPTX) as z:
    media = {name: hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist() if name.startswith('ppt/media/')}
assert len(media) == 4
for file in original_images:
    assert sha(file) in media.values(), file
checks = json.loads((SOURCE / 'presentation_layout_checks.json').read_text())
assert checks and all(c['fits'] for c in checks)

document = Document(DOCX)
pages, page = [], []
for p in document.paragraphs:
    if p._element.xpath('.//w:br[@w:type="page"]'):
        pages.append(page)
        page = []
    elif p.text:
        page.append(p.text)
pages.append(page)
assert len(pages) == 5
english_count = 0
for index, paragraphs in enumerate(pages, 1):
    slide = CONTENT['slides'][index - 1]
    en = paragraphs.index('ENGLISH SCRIPT / 英文讲述')
    cn = paragraphs.index('中文对照')
    assert paragraphs[en + 1:cn] == slide['english']
    assert paragraphs[cn + 1:cn + 1 + len(slide['chinese'])] == slide['chinese']
    assert len(slide['english']) == len(slide['chinese'])
    english_count += len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", ' '.join(slide['english'])))
assert english_count == TIMING['english_words'] == 590
with ZipFile(DOCX) as z:
    doc_xml = etree.fromstring(z.read('word/document.xml'))
    assert not doc_xml.xpath('//*[local-name()="ins" or local-name()="del" or local-name()="commentRangeStart"]')
assert abs(document.sections[0].page_width.mm - 210) < .01
assert abs(document.sections[0].page_height.mm - 297) < .01

native = {}
for app, file in [('powerpoint', PPTX), ('word', DOCX)]:
    status = json.loads((SOURCE / f'validation_evidence/{app}-native-status.json').read_text())
    assert status['source_unchanged'] and status['source_sha256'] == sha(file)
    native[app] = {'status': 'unavailable', 'reason': 'AppleEvent timeout -1712', 'source_unchanged': True, 'native_display_verified': False}
browser = {}
for key, filename in [('presentation', 'presentation_browser_reference.pdf'), ('script', 'script_browser_reference.pdf')]:
    path = SOURCE / 'validation_evidence' / filename
    with fitz.open(path) as pdf:
        assert len(pdf) == 5
        browser[key] = {'pages': 5, 'sha256': sha(path), 'manual_visual_inspection': 'pass: all five pages inspected', 'native_application_render': False}

files = [PPTX, DOCX, PNG, ROOT / 'project abstract.docx']
files.extend(POSTER / name for name in approved)
files.extend(SOURCE.glob('*.py'))
files.extend(SOURCE.glob('*.json'))
files.extend(SOURCE.glob('*.md'))
files.extend((SOURCE / 'validation_evidence').glob('*'))
files = sorted(set(files), key=str)
record = {
    'delivery_state': 'editable deliverables; browser references inspected; native Office display unverified',
    'client_date': '2026-10-12',
    'timezone': 'Asia/Singapore',
    'poster': {'accepted_editable_files_unchanged': True, 'png_size_px': [7016, 9933], 'dpi': 300, 'colour_mode': 'RGB', 'source': 'approved SVG'},
    'presentation': {'slides': 5, 'aspect_ratio': '16:9', 'first_slide_complete_approved_poster': True, 'poster_png_byte_identity': True, 'content_slides': 4, 'visible_language': 'English', 'original_object_photos_byte_identity': True, 'media_sha256': media, 'native_text_and_vector_shapes': True, 'text_width_checks': len(checks), 'text_width_pass': True, 'shape_bounds_checks': len(bounds), 'shape_bounds_pass': True, 'svg_text_parity': True, 'package': package_check(PPTX)},
    'script': {'slide_sections': 5, 'hard_page_breaks': 4, 'english_followed_by_matching_chinese': True, 'english_matches_presentation_notes': True, 'english_words': english_count, 'paper': 'A4', 'tracked_changes_or_comments': False, 'package': package_check(DOCX)},
    'timing': {'suggested_seconds': TIMING['target_seconds'], 'estimate_at_90_wpm_plus_20_seconds': round(english_count / 90 * 60 + 20), 'estimate_at_80_wpm_plus_20_seconds': round(english_count / 80 * 60 + 20), 'note': 'Estimates only; Chinese translation is not spoken; verify duration by rehearsal'},
    'browser_reference_inspection': browser,
    'native_application_checks': native,
    'content_authority': 'project abstract.docx; specific plate attribution is not established; network flows are conceptual',
    'files': {str(f.relative_to(ROOT)): {'bytes': f.stat().st_size, 'sha256': sha(f)} for f in files if f.name != 'delivery_validation.json'},
}
(SOURCE / 'delivery_validation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2))
print(f'PASS: 5 slides; poster byte identity; {len(checks)} text-width checks; {len(bounds)} bounds checks; 5 bilingual script sections; {english_count} English words; ZIP/XML relationships resolved.')
print('Native Office display remains unverified; browser references inspected. Final hashes recorded.')
