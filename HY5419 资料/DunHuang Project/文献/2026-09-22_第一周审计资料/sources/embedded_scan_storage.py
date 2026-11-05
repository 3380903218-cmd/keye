# -*- coding: utf-8 -*-
"""Read exact scan bytes from retained files or their verified PDF image streams."""
from pathlib import Path
import hashlib
import json

B = Path(__file__).resolve().parents[1]

def read_scan_bytes(relative_path):
    path = B/relative_path
    if path.is_file():
        return path.read_bytes()
    index = json.loads((B/'sources/PDF内嵌扫描页索引.json').read_text(encoding='utf-8'))
    entries = {r['original_image']: r for r in index['images']}
    if relative_path not in entries:
        raise FileNotFoundError(path)
    record = entries[relative_path]
    pdf = B/record['retained_pdf']
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == record['retained_pdf_sha256']
    import fitz
    with fitz.open(pdf) as document:
        raw = document.xref_stream_raw(record['image_xref'])
    assert hashlib.sha256(raw).hexdigest() == record['original_image_sha256']
    assert len(raw) == record['original_image_bytes']
    return raw

if __name__ == '__main__':
    index = json.loads((B/'sources/PDF内嵌扫描页索引.json').read_text(encoding='utf-8'))
    for record in index['images']:
        read_scan_bytes(record['original_image'])
    print('Verified exact PDF storage for', len(index['images']), 'original scan images.')
