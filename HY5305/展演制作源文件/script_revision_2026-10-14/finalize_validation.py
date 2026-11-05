from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone, timedelta
from lxml import etree
from docx import Document
import hashlib, json, re, posixpath, shutil
import fitz

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[1]
REVISED = ROOT / 'HY5305_Porcelain_in_Translation_Curatorial_Edit_Script_Revised.docx'
ORIGINAL = ROOT / 'HY5305_Porcelain_in_Translation_Curatorial_Edit_Script.docx'
BASELINE = SOURCE / 'baseline' / ORIGINAL.name
WORK = Path('/tmp/hy5305-script-revision-work')
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
write = lambda name, data: (SOURCE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2))
content = json.loads((SOURCE / 'revised_content.json').read_text())
baseline = json.loads((SOURCE / 'user_content_baseline.json').read_text())
timing = json.loads((SOURCE / 'timing.json').read_text())
status = json.loads((SOURCE / 'word-native-status.json').read_text())

assert sha(ORIGINAL) == sha(BASELINE) == baseline['source_sha256']
document = Document(REVISED)
before = Document(BASELINE)
pages, page = [], []
for p in document.paragraphs:
    if p._p.xpath('.//w:br[@w:type="page"]'):
        pages.append(page); page = []
    elif p.text:
        page.append(p.text)
pages.append(page)
assert len(pages) == 5
total = 0
for paragraphs, slide in zip(pages, content['slides']):
    en = paragraphs.index('ENGLISH SCRIPT / 英文讲述')
    cn = paragraphs.index('中文对照')
    assert paragraphs[en + 1:cn] == slide['english']
    assert paragraphs[cn + 1:cn + 1 + len(slide['chinese'])] == slide['chinese']
    assert len(slide['english']) == len(slide['chinese'])
    total += len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", ' '.join(slide['english'])))
assert total == timing['english_words'] == 615
assert timing['estimate_90_wpm_plus_20_seconds'] == 430
for index in baseline['slides'][0]['chinese_indices']:
    assert etree.tostring(document.paragraphs[index]._p, method='c14n') == etree.tostring(before.paragraphs[index]._p, method='c14n')
for slide_index in [2, 3]:
    for lang in ['english', 'chinese']:
        assert content['slides'][slide_index][lang] == baseline['slides'][slide_index][lang]
assert 'Lang Tingji' in ' '.join(content['slides'][1]['english'])
assert 'For my exhibition' in ' '.join(content['slides'][1]['english'])
assert 'ribbon' in content['slides'][4]['english'][3]
assert 'inheritance and renewal' in content['slides'][4]['english'][3]
write('content_checks.json', {'status': 'passed', 'artifact_sha256': sha(REVISED), 'sections': 5, 'english_words': total, 'estimate_seconds': 430, 'english_chinese_paragraph_parity': True, 'user_chinese_opening_preserved_including_run_formatting': True, 'slide_3_4_prose_preserved': True, 'manual_semantic_review': {'path': 'visual_review.md', 'sha256': sha(SOURCE / 'visual_review.md')}, 'sources': [{'publisher': 'The Palace Museum', 'url': 'https://intl.dpm.org.cn/Ceramicsis/944.html', 'supports': 'Kangxi attribution, high-fired copper-red glaze, naming, glassy surface and pale rim'}, {'publisher': 'National Museum of China', 'url': 'https://www.chnmuseum.cn/zp/zpml/201812/t20181218_26821.shtml', 'supports': 'Lang Tingji kiln supervision and relation to Ming Xuande red glazes'}], 'interpretive_claims': ['Imperial cultural identity is the exhibition interpretation', 'Ribbon continuity and change are the presenter’s design interpretation']})

xml_count = relationships = 0
with ZipFile(BASELINE) as old, ZipFile(REVISED) as package:
    assert package.testzip() is None
    assert old.namelist() == package.namelist()
    changed = [n for n in old.namelist() if old.read(n) != package.read(n)]
    assert changed == ['word/document.xml']
    names = set(package.namelist())
    for name in names:
        if name.endswith(('.xml', '.rels')):
            root = etree.fromstring(package.read(name)); xml_count += 1
            if name.endswith('.rels'):
                base = '' if name == '_rels/.rels' else name.split('/_rels/')[0]
                for rel in root:
                    if rel.get('TargetMode') == 'External': continue
                    target = posixpath.normpath(posixpath.join(base, rel.get('Target'))).lstrip('/')
                    assert target in names, (name, target); relationships += 1
    root = etree.fromstring(package.read('word/document.xml'))
    assert not root.xpath('//*[local-name()="ins" or local-name()="del" or local-name()="commentRangeStart"]')
write('package_checks.json', {'status': 'passed', 'artifact_sha256': sha(REVISED), 'changed_parts': changed, 'xml_parts_parsed': xml_count, 'internal_relationships_resolved': relationships, 'all_non_body_parts_byte_identical': True, 'headers_footers_fields_styles_notes_and_relationships_preserved': True, 'word_package_audit': {'path': 'package_audit_after.json', 'sha256': sha(SOURCE / 'package_audit_after.json')}})

assert status['returncode'] == 0 and status['pdf_created']
assert status['source_sha256'] == status['review_copy_sha256'] == sha(REVISED)
assert status['source_unchanged'] and status['pages'] == 5
pdf = WORK / 'word-native.pdf'
assert sha(pdf) == status['pdf_sha256']
shutil.copy2(pdf, SOURCE / 'word-native.pdf')
with fitz.open(pdf) as native:
    assert len(native) == 5
    for index, page in enumerate(native, 1):
        text = page.get_text()
        assert f'Slide {index} / 5' in text
        assert 'ENGLISH SCRIPT' in text
write('rendered_checks.json', {'status': 'passed', 'artifact_sha256': sha(REVISED), 'application': 'Microsoft Word', 'pages': 5, 'native_pdf': {'path': 'word-native.pdf', 'sha256': sha(SOURCE / 'word-native.pdf')}, 'manual_visual_review': {'path': 'visual_review.md', 'sha256': sha(SOURCE / 'visual_review.md')}})

delivery_file = SOURCE / 'delivery' / REVISED.name
assert sha(delivery_file) == sha(REVISED)
assert [p.name for p in (SOURCE / 'delivery').iterdir()] == [REVISED.name]
assert not (ROOT / ('~$' + REVISED.name[2:])).exists()
ppt_inventory = json.loads((SOURCE / 'ppt_preservation_inventory.json').read_text())
for name, expected in ppt_inventory.items(): assert sha(ROOT / name) == expected, 'PPT changed during Word-only round'
write('delivery_package_checks.json', {'status': 'passed', 'artifact_sha256': sha(REVISED), 'reader_facing_copy': str(REVISED), 'recorded_copy': 'delivery/' + REVISED.name, 'copies_byte_identical': True, 'delivery_directory_only_contains_requested_word': True, 'user_original_preserved': True, 'all_root_ppt_files_byte_identical': True, 'user_owned_original_locks_left_untouched': True})

record = json.loads((SOURCE / 'DELIVERY_RECORD.json').read_text())
record['state'] = 'final'
stamp = datetime.now(timezone(timedelta(hours=8))).isoformat()
files = {'content': 'content_checks.json', 'package': 'package_checks.json', 'rendered': 'rendered_checks.json', 'delivery-package': 'delivery_package_checks.json'}
record['validations'] = [{'gate': gate, 'status': 'passed', 'artifact_id': 'revised-script', 'artifact_sha256': sha(REVISED), 'performed_at': stamp, 'evidence': {'kind': 'file', 'path': file, 'sha256': sha(SOURCE / file), 'extensions': {}}, 'not_applicable': None, 'limitations': 'none', 'extensions': {}} for gate, file in files.items()]
record['unresolved_risks'] = []
record['next_action'] = 'Use the revised separate Word script for rehearsal; preserve the submitted PPT.'
record['extensions']['native_pdf_sha256'] = sha(SOURCE / 'word-native.pdf')
write('DELIVERY_RECORD.json', record)
print('PASS: bilingual meaning/content, 615 English words, five native Word pages, package relationships, user original and all PPT files preserved.')
