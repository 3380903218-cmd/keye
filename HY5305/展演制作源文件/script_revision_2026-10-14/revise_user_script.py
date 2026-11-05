from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
import json, hashlib, math, re
from lxml import etree
from docx import Document

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[1]
ORIGINAL = ROOT / 'HY5305_Porcelain_in_Translation_Curatorial_Edit_Script.docx'
BASELINE = SOURCE / 'baseline' / ORIGINAL.name
OUTPUT = ROOT / 'HY5305_Porcelain_in_Translation_Curatorial_Edit_Script_Revised.docx'
baseline = json.loads((SOURCE / 'user_content_baseline.json').read_text())
assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == baseline['source_sha256'], 'User draft has changed; re-read it before revision'
assert hashlib.sha256(BASELINE.read_bytes()).hexdigest() == baseline['source_sha256']
slides = deepcopy(baseline['slides'])
revision = json.loads((SOURCE / 'revision_text.json').read_text())
slides[0]['english'][0] = revision['slide_1_english_1']
slides[1]['english'] = revision['slide_2_english']
slides[1]['chinese'] = revision['slide_2_chinese']
slides[1]['title'] = 'Langyao red: inheritance and renewal'
slides[1]['title_zh'] = '郎窑红：传承与更新'
slides[4]['english'][3:] = [revision['slide_5_english_4'], revision['slide_5_english_5']]
slides[4]['chinese'][3:] = [revision['slide_5_chinese_4'], revision['slide_5_chinese_5']]
word_count = lambda text: len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", text))
timing, clock = [], 0
for slide in slides:
    words = word_count(' '.join(slide['english']))
    seconds = 5 * math.ceil((words * 60 / 95 + 3) / 5)
    timing.append({'slide': slide['slide'], 'words': words, 'start_seconds': clock, 'end_seconds': clock + seconds})
    clock += seconds
total = sum(x['words'] for x in timing)
estimate = round(total / 90 * 60 + 20)
fmt = lambda seconds: f'{seconds//60}:{seconds%60:02d}'

document = Document(BASELINE)
changes = []


def replace_plain_paragraph(index, text, reason):
    paragraph = document.paragraphs[index]
    if paragraph.text == text:
        return
    # Body edits never rebuild header/footer fields or any structured paragraph.
    protected = paragraph._p.xpath('.//w:fldChar | .//w:instrText | .//w:fldSimple | .//w:hyperlink | .//w:drawing | .//m:oMath | .//w:footnoteReference | .//w:bookmarkStart')
    assert not protected, (index, 'Protected paragraph structure')
    run_properties = [etree.tostring(r._r.rPr) if r._r.rPr is not None else None for r in paragraph.runs]
    before = paragraph.text
    assert paragraph.runs
    for marker in paragraph._p.xpath('.//w:proofErr'):
        marker.getparent().remove(marker)
    paragraph.runs[0].text = text
    for run in paragraph.runs[1:]:
        run.text = ''
    after_properties = [etree.tostring(r._r.rPr) if r._r.rPr is not None else None for r in paragraph.runs]
    assert run_properties == after_properties, 'Run properties changed'
    changes.append({'paragraph': index, 'reason': reason, 'before': before, 'after': text})


for slide, old in zip(slides, baseline['slides']):
    for language in ['english', 'chinese']:
        for index, text in zip(old[language + '_indices'], slide[language]):
            replace_plain_paragraph(index, text, 'Translate user edits / verified Langyao account / ribbon interpretation')
    heading = next(i for i, p in enumerate(document.paragraphs) if p.text.startswith(f'Slide {slide["slide"]} / 5'))
    replace_plain_paragraph(heading, f'Slide {slide["slide"]} / 5 — {slide["title"]}', 'Accurate section title')
    replace_plain_paragraph(heading + 1, slide['title_zh'], 'Corresponding Chinese section title')
    cue = timing[slide['slide'] - 1]
    replace_plain_paragraph(heading + 2, f'Suggested cue: {fmt(cue["start_seconds"])}–{fmt(cue["end_seconds"])}  |  {cue["words"]} English words', 'Recounted English and estimated timing')
replace_plain_paragraph(3, f'只朗读英文；中文用于对照修改。英文共 {total} 词，按每分钟 90 词、另加 20 秒停顿估算约 {estimate//60} 分 {estimate%60} 秒。实际时长请以排练为准。', 'Updated delivery estimate')
replace_plain_paragraph(24, '器物资料：故宫博物院；中国国家博物馆。文化身份的联系为本展览的策展解读。', 'Separate verified object facts from exhibition interpretation')

# Preserve every package member except the edited body XML, including Word styles,
# header/footer PAGE fields, footnotes/endnotes, relationships and metadata.
body = etree.tostring(document._element, encoding='UTF-8', xml_declaration=True, standalone=True)
with ZipFile(BASELINE) as original, ZipFile(OUTPUT, 'w') as revised:
    for info in original.infolist():
        revised.writestr(info, body if info.filename == 'word/document.xml' else original.read(info.filename))
with ZipFile(BASELINE) as before, ZipFile(OUTPUT) as after:
    parts = [name for name in before.namelist() if before.read(name) != after.read(name)]
assert parts == ['word/document.xml'], parts
assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == baseline['source_sha256']

(SOURCE / 'revised_content.json').write_text(json.dumps({'title': 'Porcelain in Translation', 'slides': slides}, ensure_ascii=False, indent=2))
(SOURCE / 'timing.json').write_text(json.dumps({'english_words': total, 'estimate_90_wpm_plus_20_seconds': estimate, 'suggested_seconds': clock, 'slides': timing}, ensure_ascii=False, indent=2))
(SOURCE / 'change_log.json').write_text(json.dumps({'source_sha256': baseline['source_sha256'], 'output_sha256': hashlib.sha256(OUTPUT.read_bytes()).hexdigest(), 'parts_changed': parts, 'paragraph_changes': changes}, ensure_ascii=False, indent=2))
print('Created', OUTPUT)
print('English words:', total, 'Estimated delivery:', fmt(estimate), 'Suggested segments:', fmt(clock))
print('Preserved the user original, unchanged slide 3/4 prose, and all non-body package parts.')
