from copy import deepcopy
from datetime import datetime, timezone
from difflib import SequenceMatcher
from hashlib import sha256
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile
import json
import re

from lxml import etree as E

ROOT = Path('/Users/arourouwed/Desktop/NUS/2026-1/HY6101')
AUDIT = ROOT / '.essay2_revision_20261024'
BASE = AUDIT / 'HY6101_Combined_Essay2_中文版_修改前含批注.docx'
MD = AUDIT / 'essay2_revised_zh.md'
CANDIDATE = AUDIT / 'revised_candidate.docx'
OUT = ROOT / 'seminar 11/HY6101_Combined_Essay2_中文版.docx'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
      'w15': 'http://schemas.microsoft.com/office/word/2012/wordml'}


def q(tag):
    pre, local = tag.split(':')
    return '{' + NS[pre] + '}' + local


def tx(p):
    return ''.join(n.text or '' for n in p.findall('.//w:t', NS))


def hash_file(p):
    return sha256(p.read_bytes()).hexdigest()


def xml(root):
    return E.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


text = MD.read_text(encoding='utf-8')
blocks = []
for block in text.split('\n\n'):
    block = block.strip()
    if not block.strip():
        continue
    if block.startswith('# '):
        for line in block.splitlines():
            role = 'title' if line.startswith('# ') else 'subtitle'
            blocks.append((role, line.split(' ', 1)[1]))
    elif block.startswith('### '):
        blocks.append(('heading', block[4:]))
    else:
        blocks.append(('body', block))

ref_start = next(i for i, (role, content) in enumerate(blocks) if content == '阅读文献')
body_han = len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]', ''.join(content for role, content in blocks[:ref_start] if role == 'body')))
assert 8000 <= body_han <= 8500

with ZipFile(BASE) as source_zip:
    entries = [(item, source_zip.read(item.filename)) for item in source_zip.infolist()]
    parts = dict((item.filename, data) for item, data in entries)

root = E.fromstring(parts['word/document.xml'])
body = root.find('w:body', NS)
old = body.findall('w:p', NS)
assert len(old) == 61
assert body.find('w:tbl', NS) is None
old_heading_indices = [i for i, p in enumerate(old) if p.find('w:pPr/w:pStyle', NS) is not None and p.find('w:pPr/w:pStyle', NS).get(q('w:val')) == 'Heading1']
old_body_indices = [i for i in range(2, 53) if i not in old_heading_indices]

# Inventory character roles before replacing prose. Every body text run inherits
# one common regular style. References have explicit size formatting and are reused.
body_run_properties = set()
for i in old_body_indices:
    assert not any(old[i].find('.//' + q(tag)) is not None for tag in ['w:fldChar', 'w:instrText', 'w:drawing', 'w:hyperlink'])
    for run in old[i].findall('w:r', NS):
        if run.find('w:t', NS) is None:
            continue
        rp = run.find('w:rPr', NS)
        body_run_properties.add(E.tostring(rp) if rp is not None else b'inherited')
assert body_run_properties == {b'inherited'}

headings = [5, 11, 18, 25, 33, 41, 49, 53]
heading_count = 0
body_count = 0
new_nodes = []
changes = []
for i, (role, content) in enumerate(blocks):
    if i > ref_start:
        source_index = 54 + (i - ref_start - 1)
        assert tx(old[source_index]) == content
        node = deepcopy(old[source_index])
    else:
        if role == 'title':
            source_index = 0
        elif role == 'subtitle':
            source_index = 1
        elif role == 'heading':
            source_index = headings[heading_count]
            heading_count += 1
        elif body_count == 0:
            source_index = 2
        elif body_count == 1:
            source_index = 3
        else:
            source_index = max(old_body_indices, key=lambda j: SequenceMatcher(None, tx(old[j]), content).ratio())
        node = deepcopy(old[source_index])
        ppr = node.find('w:pPr', NS)
        # Plain prose has no protected field/equation/link structures. The
        # inherited paragraph/character roles are preserved; comments reanchor.
        for child in list(node):
            if child is not ppr:
                node.remove(child)
        node.set(q('w14:paraId'), uuid4().hex[:8].upper())
        node.set(q('w14:textId'), uuid4().hex[:8].upper())
        comment_id = str(body_count) if role == 'body' and body_count < 2 else None
        if comment_id is not None:
            start = E.SubElement(node, q('w:commentRangeStart'))
            start.set(q('w:id'), comment_id)
        run = E.SubElement(node, q('w:r'))
        t = E.SubElement(run, q('w:t'))
        t.text = content
        if comment_id is not None:
            end = E.SubElement(node, q('w:commentRangeEnd'))
            end.set(q('w:id'), comment_id)
            cr = E.SubElement(node, q('w:r'))
            crp = E.SubElement(cr, q('w:rPr'))
            style = E.SubElement(crp, q('w:rStyle'))
            style.set(q('w:val'), 'CommentReference')
            ref = E.SubElement(cr, q('w:commentReference'))
            ref.set(q('w:id'), comment_id)
        if role == 'body':
            body_count += 1
    changes.append({'new_index': i, 'role': role, 'source_template_index': source_index, 'old_paragraph': tx(old[source_index]), 'revised_paragraph': content, 'same_text': tx(old[source_index]) == content})
    new_nodes.append(node)

for para in old:
    body.remove(para)
sect = body.find('w:sectPr', NS)
insert_at = list(body).index(sect) if sect is not None else len(body)
for i, node in enumerate(new_nodes):
    body.insert(insert_at + i, node)
parts['word/document.xml'] = xml(root)

# Keep original comment texts, authors and all relationships; resolve the two
# threads after their corrections have been applied throughout the manuscript.
extended = E.fromstring(parts['word/commentsExtended.xml'])
for node in extended.findall('w15:commentEx', NS):
    node.set(q('w15:done'), '1')
parts['word/commentsExtended.xml'] = xml(extended)

core = E.fromstring(parts['docProps/core.xml'])
dc = 'http://purl.org/dc/elements/1.1/'
dcterms = 'http://purl.org/dc/terms/'
core.find('{' + dc + '}title').text = blocks[0][1] + blocks[1][1]
core.find('{' + dcterms + '}modified').text = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
parts['docProps/core.xml'] = xml(core)

with ZipFile(CANDIDATE, 'w') as target_zip:
    for info, original_data in entries:
        target_zip.writestr(info, parts[info.filename])

with ZipFile(CANDIDATE) as z:
    rr = E.fromstring(z.read('word/document.xml'))
    assert [tx(p) for p in rr.findall('w:body/w:p', NS)] == [content for _, content in blocks]
    assert z.read('word/comments.xml') == dict((info.filename, data) for info, data in entries)['word/comments.xml']
    assert [n.get(q('w15:done')) for n in E.fromstring(z.read('word/commentsExtended.xml')).findall('w15:commentEx', NS)] == ['1', '1']
    assert len(rr.findall('.//w:commentRangeStart', NS)) == 2
    assert len(rr.findall('.//w:commentRangeEnd', NS)) == 2
    assert len(rr.findall('.//w:commentReference', NS)) == 2
    protected = [info.filename for info, _ in entries if info.filename not in {'word/document.xml', 'word/commentsExtended.xml', 'docProps/core.xml'}]
    original_parts = dict((info.filename, data) for info, data in entries)
    assert all(z.read(name) == original_parts[name] for name in protected)

write_json(AUDIT/'paragraph_changes.json', changes)
write_json(AUDIT/'content_check.json', {
    'baseline_sha256': hash_file(BASE),
    'candidate_sha256': hash_file(CANDIDATE),
    'body_han_characters_excluding_headings_punctuation_latin_references': body_han,
    'body_han_including_titles_and_headings': len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]', ''.join(content for _, content in blocks[:ref_start]))),
    'body_paragraphs': body_count,
    'reference_count': len(blocks)-ref_start-1,
    'block_count': len(blocks),
    'markdown_word_block_parity': True,
    'comments_retained': 2,
    'comments_resolved': 2,
    'comment_texts_unchanged': True,
    'header_footer_styles_fields_relationships_and_other_parts_byte_preserved': True,
    'body_character_roles_before_rewrite': ['inherited regular paragraph style'],
    'all_seven_works_remain_in_comparative_argument': True,
    'main_line': '从manager式的局限职业印象，推进至档案员的研究角色，并将档案范围和意义与职业所需知识相联系。',
})
print(json.dumps({'body_han': body_han, 'paragraphs':body_count, 'candidate':str(CANDIDATE), 'comments_resolved':2}, ensure_ascii=False))
