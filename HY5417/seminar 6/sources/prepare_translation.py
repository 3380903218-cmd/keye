import json, re
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / '05_Everingham_2021_Tourism_otherwise_英文全文_作者接受稿.pdf'
doc = fitz.open(SOURCE)
segments, footnotes = [], []
line_inventory = []
last = None

def normalize(lines):
    text = '\n'.join(lines)
    text = re.sub(r'-\s*\n\s*', '-', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

for pi, page in enumerate(doc):
    if pi == 0:
        continue
    raw = []
    for block in page.get_text('dict')['blocks']:
        if block['type'] != 0:
            continue
        for ln in block['lines']:
            spans = [s for s in ln['spans'] if s['text'].strip()]
            if not spans or ln['bbox'][1] > 725:
                continue
            raw.append({'x': ln['bbox'][0], 'y': ln['bbox'][1], 'end': ln['bbox'][3],
                        'size': max(s['size'] for s in spans),
                        'bold': all('Bold' in s['font'] for s in spans if s['size'] >= 10.5),
                        'text': ''.join(s['text'] for s in ln['spans']).strip()})
    raw.sort(key=lambda x: (round(x['y']), x['x']))
    lines = []
    for row in raw:
        if lines and abs(lines[-1]['y']-row['y']) < 2:
            lines[-1]['text'] += ' ' + row['text']
            lines[-1]['end'] = max(lines[-1]['end'], row['end'])
            lines[-1]['size'] = max(lines[-1]['size'], row['size'])
        else:
            lines.append(row.copy())
    prev = None
    for ln in lines:
        ln['page'] = pi+1
        ln['line_id'] = len(line_inventory)+1
        line_inventory.append(ln)
        if ln['size'] < 10.5:
            if re.match(r'^[1-4]\s*\D', ln['text']):
                footnotes.append({'kind':'footnote', 'pages':[pi+1], 'lines':[], 'line_ids':[]})
            assert footnotes
            footnotes[-1]['lines'].append(ln['text'])
            footnotes[-1]['line_ids'].append(ln['line_id'])
            continue
        kind = 'heading' if ln['bold'] else ('reference' if pi >= 19 else 'body')
        if not segments:
            new = True
        elif prev is None:
            # A page boundary does not split an unfinished paragraph.
            new = (segments[-1]['kind'] == 'heading' or kind == 'heading'
                   or bool(re.search(r'[.!?][”\'\"]?$', segments[-1]['lines'][-1]))
                   or ln['text'].startswith('•')
                   or last is not None and abs(ln['x']-last['x']) > 20
                   or kind == 'reference' and bool(re.match(r'^[A-ZÀ-Ž][^\n]{0,130}\((?:\d{4}|n\.d\.)', ln['text'])))
        else:
            new = (ln['y'] - prev['end'] > 8
                   or (kind == 'heading') != (segments[-1]['kind'] == 'heading')
                   or kind == 'reference' and ln['text'].startswith('Tlostanova, M. (2010)')
                   or ln['text'].startswith('•'))
        if new:
            segments.append({'kind':kind, 'pages':[], 'lines':[], 'line_ids':[]})
        s=segments[-1]
        if pi+1 not in s['pages']: s['pages'].append(pi+1)
        s['lines'].append(ln['text']); s['line_ids'].append(ln['line_id'])
        prev = ln
        last = ln

for i, s in enumerate(segments):
    s['id']=f'S{i+1:03}'
    s['en']=normalize(s.pop('lines'))
for i, s in enumerate(footnotes):
    s['id']=f'F{i+1}'
    s['en']=normalize(s.pop('lines'))

all_ids=[n for s in segments+footnotes for n in s['line_ids']]
assert sorted(all_ids)==list(range(1,len(line_inventory)+1)), 'Source text lines lost or duplicated'
out={'source':SOURCE.name,'source_pages':len(doc),'segments':segments,'footnotes':footnotes,
     'source_line_count':len(line_inventory)}
(ROOT/'sources/paragraphs_en.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
(ROOT/'sources/source_lines.json').write_text(json.dumps(line_inventory,ensure_ascii=False,indent=2))
for s in segments+footnotes:
    print(s['id'],s['kind'],','.join(map(str,s['pages'])),len(s['en'].split()),s['en'][:110])
