from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re
import unicodedata

from docx import Document
import fitz

ROOT = Path('/Users/arourouwed/Desktop/NUS/2026-1/HY6101')
AUDIT = ROOT / '.essay2_delivery_20261024'
OUT = ROOT / 'seminar 11/HY6101_Combined_Essay2_中文版.docx'
PDF = AUDIT / 'word_render_v2.pdf'
NOW = datetime.now(ZoneInfo('Asia/Singapore')).isoformat()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def norm(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s))


doc = Document(OUT)
expected = norm(''.join(p.text for p in doc.paragraphs))
pdf = fitz.open(PDF)
chunks = []
glyph_mapping_count = 0
for page in pdf:
    text = page.get_text()
    # Word's Songti PDF subset maps the visually correct 口 glyph to U+2F1C.
    # Both affected words were inspected at 3x: 入口 (page 4), 口述 (page 9).
    glyph_mapping_count += text.count('\u2f1c')
    text = text.replace('\u2f1c', '口')
    text = re.sub(r'HY6101\s*\|\s*Combined Essay 2', '', text)
    text = re.sub(r'第\s*\d+\s*页', '', text)
    chunks.append(text)
actual = norm(''.join(chunks))
if actual != expected:
    from difflib import SequenceMatcher
    mismatch = [(tag, expected[i:j], actual[k:l]) for tag,i,j,k,l in SequenceMatcher(None,expected,actual).get_opcodes() if tag != 'equal']
    write(AUDIT/'render_text_mismatch.json', mismatch)
assert actual == expected, 'Rendered text differs; see render_text_mismatch.json'
assert glyph_mapping_count == 2
assert '\ufffd' not in actual

content = json.loads((AUDIT/'content_check.json').read_text())
assert content['sha256'] == sha(OUT)
for path, value in content['source_sha256'].items():
    assert sha(Path(path)) == value
content['editorial_review'] = {
    'central_question': '多人参与历史生产时，解释权如何受到约束，并为后来者保留重新理解的可能。',
    'source_supported_progression': '从记录者与档案范围，推进至鉴定、描述、合作、证明限度和记忆责任。',
    'all_seven_readings_compared_by_theme': True,
    'structure_is_not_weekly_or_author_summaries': True,
    'no_invented_personal_experiences_or_research_results': True,
    'extensions_are_personal_inferences_or_conditional': True,
    'page_citations_checked_against_user_draft': ['Lee 44–45','Lee 127–132','Lee 135–144','Lee 181–182'],
    'article_authors_and_titles_checked_from_local_course_pdf_first_pages': True,
    'source_documents_unchanged': True,
    'reviewed_at': NOW,
}
write(AUDIT/'content_check.json', content)

package = json.loads((AUDIT/'package_check.json').read_text())
assert package['exit_code'] == 0
assert package['files'][0]['summary']['errors'] == 0
assert package['files'][0]['summary']['issues'] == 0

render = {
    'source_docx_sha256': sha(OUT),
    'render_pdf': PDF.name,
    'render_pdf_sha256': sha(PDF),
    'application': 'Microsoft Word for Mac',
    'pages': len(pdf),
    'rendered_text_matches_docx_after_documented_normalization': actual == expected,
    'normalization': ['NFKC', 'whitespace/header/footer removal', 'Two U+2F1C extraction mappings to visually verified 口; actual 又 characters are separate U+53C8 and preserved.'],
    'glyph_verification_crops': [{'path': f'extraction_glyph_page{n}.png', 'sha256': sha(AUDIT/f'extraction_glyph_page{n}.png')} for n in [4,9]],
    'visual_inspection': {
        'pages_inspected': list(range(1, len(pdf)+1)),
        'contact_sheets': [{'path': f'v2_contact_{n}.png', 'sha256': sha(AUDIT/f'v2_contact_{n}.png')} for n in [1,2]],
        'fonts_consistent': True,
        'title_and_subtitle_clean': True,
        'heading_and_paragraph_flow_acceptable': True,
        'body_line_spacing': '22 pt exact at 12 pt Songti SC',
        'page_numbers_continuous': True,
        'no_blank_pages_or_clipped_text_observed': True,
        'references_separate_readable_page': True,
    },
    'export_note': 'The current v2 PDF is the successful export of the current DOCX hash. An earlier overwrite attempt timed out; its old PDF is not validation evidence. The task-owned read-only Word window was closed using the window close command.',
    'performed_at': NOW,
}
write(AUDIT/'rendered_check.json', render)

members = sorted(p.name for p in OUT.parent.iterdir())
assert members == [OUT.name], members
delivery = {
    'directory': str(OUT.parent),
    'members': members,
    'sha256': {OUT.name: sha(OUT)},
    'no_locks_temporary_files_or_audit_artifacts_in_delivery_directory': True,
    'performed_at': NOW,
}
write(AUDIT/'delivery_package_check.json', delivery)

gates = {'content': 'content_check.json', 'package': 'package_check.json', 'rendered': 'rendered_check.json', 'delivery-package': 'delivery_package_check.json'}
record = {
    'schema_version': '2.0',
    'delivery_id': 'HY6101-essay2-zh-20261024',
    'state': 'final',
    'content_authority': 'User-designated Seminar 7–8 and 9–10 Chinese DOCX drafts; source identities are in .essay2_delivery_20261024/content_check.json',
    'format_authority': 'User-provided instructor requirement image and requested Chinese Word essay of 8000–8500 Chinese characters; A4 scholarly manuscript formatting selected for readability.',
    'synchronization_direction': 'markdown-to-word',
    'submitted_baseline_id': None,
    'artifacts': [{
        'artifact_id': 'essay2-zh-docx',
        'role': 'final',
        'path': OUT.relative_to(ROOT).as_posix(),
        'media_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'sha256': sha(OUT),
        'frozen': False,
        'required_gates': [{'gate': gate, 'evidence_mode': 'file', 'extensions': {}} for gate in gates],
        'extensions': {'content_stage': 'Chinese manuscript draft requested by the user; not represented as submitted.'},
    }],
    'validations': [{
        'gate': gate,
        'status': 'passed',
        'artifact_id': 'essay2-zh-docx',
        'artifact_sha256': sha(OUT),
        'performed_at': NOW,
        'evidence': {'kind': 'file', 'path': (AUDIT/name).relative_to(ROOT).as_posix(), 'sha256': sha(AUDIT/name), 'extensions': {}},
        'not_applicable': None,
        'limitations': 'none for the requested drafting and Word-delivery scope',
        'extensions': {},
    } for gate,name in gates.items()],
    'delivery_members': ['essay2-zh-docx'],
    'invalidated_checks': [],
    'unresolved_risks': [],
    'next_action': 'Hand off the Word manuscript for the user to review.',
    'extensions': {'counting_rule': '8197 Han characters in body prose, excluding headings, punctuation, Latin words and references; 8279 including title/subtitle/headings.'},
}
write(ROOT/'.HY6101_essay2_delivery_record.json', record)
print(json.dumps({'body_han': content['body_han_characters_excluding_titles_headings_punctuation_latin_references'], 'pages':len(pdf), 'render_text_parity':actual==expected,'sha256':sha(OUT), 'delivery_members':members},ensure_ascii=False,indent=2))
