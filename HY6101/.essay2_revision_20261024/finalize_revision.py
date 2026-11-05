from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from hashlib import sha256
from zipfile import ZipFile
import json
import re
import unicodedata

from lxml import etree as E
from docx import Document
import fitz

ROOT = Path('/Users/arourouwed/Desktop/NUS/2026-1/HY6101')
AUDIT = ROOT / '.essay2_revision_20261024'
OUT = ROOT / 'seminar 11/HY6101_Combined_Essay2_中文版.docx'
BASE = AUDIT / 'HY6101_Combined_Essay2_中文版_修改前含批注.docx'
PDF = AUDIT / 'revision_render_04.pdf'
NOW = datetime.now(ZoneInfo('Asia/Singapore')).isoformat()
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main', 'w15': 'http://schemas.microsoft.com/office/word/2012/wordml'}


def sha(p):
    return sha256(p.read_bytes()).hexdigest()


def write(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def norm(text):
    return re.sub(r'\s', '', unicodedata.normalize('NFKC', text))


assert OUT.read_bytes() == (AUDIT/'revised_candidate.docx').read_bytes()
content = json.loads((AUDIT/'content_check.json').read_text())
assert content['baseline_sha256'] == sha(BASE)
assert content['candidate_sha256'] == sha(OUT)
doc = Document(OUT)
ref_index = next(i for i,p in enumerate(doc.paragraphs) if p.text == '阅读文献')
body_text = ''.join(p.text for p in doc.paragraphs[:ref_index] if p.style.name not in ['Title','Subtitle','Heading 1'])
count = len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]', body_text))
assert count == 8185
content['final_sha256'] = sha(OUT)
content['checked_at'] = NOW
content['revision_decisions'] = 'revision_state.json'
content['professional_and_archive_meaning_focus_in_title_intro_sections_and_conclusion'] = True
content['old_general_silence_and_evidence_skepticism_trajectory_removed_as_main_argument'] = True
write(AUDIT/'content_check.json', content)

with ZipFile(OUT) as z:
    original_comments = ZipFile(BASE).read('word/comments.xml')
    assert z.read('word/comments.xml') == original_comments
    assert all(n.get('{'+NS['w15']+'}done') == '1' for n in E.fromstring(z.read('word/commentsExtended.xml')))

package = json.loads((AUDIT/'package_check.json').read_text())
assert package['exit_code'] == 0
assert package['files'][0]['summary']['errors'] == 0
assert package['files'][0]['summary']['issues'] == 0

pdf = fitz.open(PDF)
actual = ''
for page in pdf:
    text = page.get_text()
    assert '批注[' not in text
    text = re.sub(r'HY6101\s*\|\s*Combined Essay 2', '', text)
    text = re.sub(r'第\s*\d+\s*页', '', text)
    actual += text
assert actual.count('\u2f1c') == 1
assert norm(actual.replace('\u2f1c', '口')) == norm(''.join(p.text for p in doc.paragraphs))
render = {
    'source_docx_sha256': sha(OUT),
    'render_pdf': PDF.name,
    'render_pdf_sha256': sha(PDF),
    'application': 'Microsoft Word for Mac',
    'pages': len(pdf),
    'current_source_title_loaded_in_Word_verified': True,
    'word_source_refreshed_using_revert_before_render': True,
    'rendered_text_matches_docx': True,
    'normalization': ['NFKC', 'whitespace/header/footer removal', 'One Songti PDF extraction U+2F1C mapping to visually verified 口 in 口号 on page 8'],
    'review_markup_hidden_for_preview_only': True,
    'resolved_comments_preserved_in_docx': True,
    'visual_inspection': {
        'pages_inspected': list(range(1, len(pdf)+1)),
        'contact_sheets': [{'path': f'final_contact_{n}.png','sha256':sha(AUDIT/f'final_contact_{n}.png')} for n in [1,2]],
        'glyph_crop': {'path':'glyph_mouth_check.png','sha256':sha(AUDIT/'glyph_mouth_check.png')},
        'title_fonts_margins_spacing_page_numbers_checked': True,
        'no_blank_pages_clipping_or_orphan_headings_observed': True,
        'references_complete_and_readable': True,
    },
    'earlier_export_attempts': 'Initial attempts used a stale Word buffer and were invalidated; the source was explicitly reloaded. Render 03 included printed comments and was superseded by render 04 with markup hidden. Only render 04 validates the current file.',
    'performed_at': NOW,
}
write(AUDIT/'rendered_check.json', render)

members = sorted(p.name for p in OUT.parent.iterdir())
assert members == [OUT.name], members
write(AUDIT/'delivery_package_check.json', {'directory':str(OUT.parent),'members':members,'output_sha256':sha(OUT),'annotated_backup':BASE.name,'annotated_backup_sha256':sha(BASE),'no_locks_or_temporary_artifacts_in_delivery_directory':True,'performed_at':NOW})

state = json.loads((AUDIT/'revision_state.json').read_text())
state['next_action'] = 'Hand off the revised Word manuscript at the original path; both comments are resolved and the annotated original is backed up.'
state['extensions']['final_sha256'] = sha(OUT)
state['extensions']['render_pages'] = len(pdf)
state['extensions']['completed_at'] = NOW
write(AUDIT/'revision_state.json', state)

gates = {'content':'content_check.json', 'package':'package_check.json', 'rendered':'rendered_check.json', 'delivery-package':'delivery_package_check.json'}
record = {
    'schema_version':'2.0',
    'delivery_id':'HY6101-essay2-zh-comment-revision-20261024',
    'state':'final',
    'content_authority':'Two user annotations in the reviewed original, preserved in .essay2_revision_20261024/HY6101_Combined_Essay2_中文版_修改前含批注.docx, and the original user-designated Chinese reading drafts.',
    'format_authority':'Preserve reviewed original Word styles, headers, footers, references, fields, and page setup. Keep the prior 8000–8500 Han-character requirement.',
    'synchronization_direction':'bidirectional',
    'submitted_baseline_id':None,
    'artifacts':[{'artifact_id':'essay2-zh-docx','role':'final','path':OUT.relative_to(ROOT).as_posix(),'media_type':'application/vnd.openxmlformats-officedocument.wordprocessingml.document','sha256':sha(OUT),'frozen':False,'required_gates':[{'gate':g,'evidence_mode':'file','extensions':{}} for g in gates],'extensions':{'manuscript_title':'从管理者到研究伙伴——重新认识档案员与档案的意义','content_stage':'Revised Chinese manuscript; not represented as submitted.','comment_state':'2 retained, 2 resolved; no tracked changes were present.'}}],
    'validations':[{'gate':g,'status':'passed','artifact_id':'essay2-zh-docx','artifact_sha256':sha(OUT),'performed_at':NOW,'evidence':{'kind':'file','path':(AUDIT/name).relative_to(ROOT).as_posix(),'sha256':sha(AUDIT/name),'extensions':{}},'not_applicable':None,'limitations':'none for the requested revision scope','extensions':{}} for g,name in gates.items()],
    'delivery_members':['essay2-zh-docx'],
    'invalidated_checks':[],
    'unresolved_risks':[],
    'next_action':'Hand off the revised manuscript at the original path.',
    'extensions':{'prior_delivery_id':'HY6101-essay2-zh-20261024','prior_record_snapshot':'.essay2_revision_20261024/previous_delivery_record.json','reviewed_baseline_sha256':sha(BASE),'reviewed_baseline_path':BASE.relative_to(ROOT).as_posix(),'counting_rule':'8185 body Han characters, excluding headings, punctuation, Latin text and references; 8272 including titles/headings.','comments_applied_globally':['Correct initial manager impression and develop historical-research career recognition.','Refocus this course-half essay on archivists and archive scope/meaning throughout title, introduction, body and conclusion.']}
}
write(ROOT/'.HY6101_essay2_delivery_record.json', record)
print(json.dumps({'body_han':count,'pages':len(pdf),'output_sha256':sha(OUT),'comments_retained_and_resolved':2,'delivery_members':members},ensure_ascii=False,indent=2))
