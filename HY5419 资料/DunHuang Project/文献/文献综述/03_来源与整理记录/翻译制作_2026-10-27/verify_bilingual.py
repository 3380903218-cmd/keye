# -*- coding: utf-8 -*-
"""Validate actual delivered files, including every original-page appendix."""
from pathlib import Path
import hashlib, json, re
import fitz

ROOT=Path(__file__).resolve().parent
INPUT=ROOT.parent.parent/'01_待读文献PDF'/'英文文献'
OUTPUT=INPUT/'翻译版'
reports=[]
for record in sorted(ROOT.glob('*_output.json')):
    key=record.stem.replace('_output','')
    out=json.loads(record.read_text());manifest=json.loads((ROOT/(key+'_source.json')).read_text())
    path=OUTPUT/out['file']
    if not path.exists():continue
    assert hashlib.sha256(path.read_bytes()).hexdigest()==out['sha256'],path
    original=INPUT/manifest['source']
    assert hashlib.sha256(original.read_bytes()).hexdigest()==manifest['source_sha256'],original
    src=fitz.open(original);pdf=fitz.open(path);offset=out['appendix_start']-1
    assert len(pdf)-offset==len(manifest['pages'])
    whitespace_only_extraction_differences=[]
    for j,pn in enumerate(manifest['pages']):
        source_text=src[pn-1].get_text();appendix_text=pdf[offset+j].get_text()
        if source_text!=appendix_text:
            # PDF resource consolidation can cause MuPDF to infer an extra
            # interword space. Accept only whitespace differences whose page
            # renders are byte-identical, never altered source characters.
            assert re.sub(r'\s+','',source_text)==re.sub(r'\s+','',appendix_text),(key,pn,'original-page text differs')
            source_pixels=src[pn-1].get_pixmap(annots=False)
            appendix_pixels=pdf[offset+j].get_pixmap(annots=False)
            assert source_pixels.samples==appendix_pixels.samples,(key,pn,'whitespace difference with nonidentical rendering')
            whitespace_only_extraction_differences.append(pn)
        assert src[pn-1].rect==pdf[offset+j].rect
    sampled=sorted({0,len(manifest['pages'])//2,len(manifest['pages'])-1})
    render_differences=[]
    for j in sampled:
        a=src[manifest['pages'][j]-1].get_pixmap(matrix=fitz.Matrix(.6,.6),annots=False)
        b=pdf[offset+j].get_pixmap(matrix=fitz.Matrix(.6,.6),annots=False)
        import numpy as np
        delta=np.abs(np.frombuffer(a.samples,dtype=np.uint8).astype(np.int16)-np.frombuffer(b.samples,dtype=np.uint8).astype(np.int16))
        maximum=int(delta.max());mean=float(delta.mean())
        # Renderer colour/antialias rounding can change channels by 1–2/255.
        assert maximum<=4 and mean<=.5,(key,j,'material original-page rendering difference',maximum,mean)
        render_differences.append(dict(source_page=manifest['pages'][j],max_channel_delta=maximum,mean_channel_delta=mean))
    maintext='\n'.join(pdf[i].get_text() for i in range(offset))
    absent=[s['id'] for s in manifest['segments'] if maintext.count(s['id'])<2]
    assert not absent,(key,absent)
    assert len(re.findall(r'[\u3400-\u9fff]',maintext))>300
    placements=json.loads((ROOT/(key+'_placements.json')).read_text())
    for place in placements:
        page=pdf[place['outpage']]
        assert 20<=place['x']<=page.rect.width-20
        assert place['x']+place['width']<page.rect.width-20
        assert 35<=place['y'] and place['y']+place['height']<=page.rect.height-25
    report=dict(key=key,file=out['file'],pages=len(pdf),paragraph_groups=len(manifest['segments']),
        original_pages_verified=len(manifest['pages']),all_paragraph_ids_present=True,
        original_hash_unchanged=True,original_page_pixel_samples=len(sampled),
        whitespace_only_extraction_differences=whitespace_only_extraction_differences,
        original_page_render_checks=render_differences,
        sha256=out['sha256'],bytes=path.stat().st_size)
    reports.append(report)
    print(json.dumps(report,ensure_ascii=False),flush=True)
    src.close();pdf.close()
(ROOT/'最终文件核验.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
print('VERIFIED PDF COUNT:',len(reports))
