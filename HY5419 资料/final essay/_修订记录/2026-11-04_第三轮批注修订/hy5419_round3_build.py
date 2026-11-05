from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree
from copy import deepcopy
import hashlib,json,re

W=Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/final essay/_修订记录/2026-11-04_第三轮批注修订')
src=W/'批注原稿备份.docx';out=W/'修订候选.docx'
cfg=json.loads((W/'revisions.json').read_text())
changes={int(i):s for i,s in cfg['changes'].items()}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
tag=lambda s:'{'+ns['w']+'}'+s
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(src.read_bytes())=='ac1931155845d6d7945f9248af46d9d2ceb9642be654ec552ddb70b0b0000748'
with ZipFile(src) as zin:
    root=etree.fromstring(zin.read('word/document.xml'))
    ps=root.xpath('//w:body/w:p',namespaces=ns);assert len(ps)==71
    original=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in ps]
    drawings=[etree.tostring(d) for d in root.xpath('//w:drawing',namespaces=ns)]
    fields={n:zin.read(n) for n in zin.namelist() if n.startswith('word/') and n.endswith('.xml') and n not in {'word/document.xml','word/settings.xml'} and b'fldChar' in zin.read(n)}
    changelog=[]
    for i,new in changes.items():
        p=ps[i]
        assert not p.xpath('.//w:drawing|.//w:fldChar|.//w:fldSimple|.//w:instrText|.//w:hyperlink',namespaces=ns)
        for r in p.findall('w:r',ns):
            if r.find('w:t',ns) is None:continue
            rp=r.find('w:rPr',ns)
            assert rp is None or {etree.QName(c).localname for c in rp}<={'lang'}
        ts=p.xpath('.//w:t',namespaces=ns);assert ts
        ts[0].text=new;ts[0].set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        for t in ts[1:]:t.text=''
        changelog.append({'original_paragraph':i,'old':original[i],'new':new})
    for ins in cfg['inserts']:
        template=ps[ins['template']]
        p=etree.Element(tag('p'))
        pp=template.find('w:pPr',ns)
        if pp is not None:p.append(deepcopy(pp))
        if ins['kind']=='reference':
            for text,italic in ins['runs']:
                run=etree.SubElement(p,tag('r'));rp=etree.SubElement(run,tag('rPr'))
                fonts=etree.SubElement(rp,tag('rFonts'))
                for f in ['ascii','hAnsi']:fonts.set(tag(f),'Times New Roman')
                fonts.set(tag('eastAsia'),'Songti SC')
                if italic:etree.SubElement(rp,tag('i'))
                etree.SubElement(rp,tag('sz')).set(tag('val'),'21')
                etree.SubElement(rp,tag('szCs')).set(tag('val'),'21')
                etree.SubElement(rp,tag('lang')).set(tag('eastAsia'),'zh-CN')
                t=etree.SubElement(run,tag('t'));t.text=text;t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        else:
            run=etree.SubElement(p,tag('r'))
            text_run=next(r for r in template.findall('w:r',ns) if r.find('w:t',ns) is not None)
            rp=text_run.find('w:rPr',ns)
            if rp is not None:run.append(deepcopy(rp))
            t=etree.SubElement(run,tag('t'));t.text=ins['text'];t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        ps[ins['after']].addnext(p)
        changelog.append({'insert_after_original_paragraph':ins['after'],'new':ins['text'],'kind':ins['kind']})
    # Keep the large second figure intact. Let its adjacent time-record example
    # precede it so the preceding page is filled instead of leaving a large gap.
    ps[31].addnext(ps[35])
    changelog.append({'kind':'layout-order','original_paragraph':35,'moved_after_original_paragraph':31,'text_unchanged':True,'reason':'Keep full-size Figure 2 together and avoid excessive preceding-page whitespace.'})
    for e in list(root.iter()):
        if etree.QName(e).localname in {'commentRangeStart','commentRangeEnd','commentReference'}:e.getparent().remove(e)
    removed={n for n in zin.namelist() if re.search(r'(^|/)(comments[^/]*|people)\.xml$',n,re.I) or re.search(r'(^|/)_rels/(comments[^/]*|people)\.xml\.rels$',n,re.I)}
    with ZipFile(out,'w',ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            name=item.filename
            if name in removed:continue
            data=zin.read(name)
            if name=='word/document.xml':data=etree.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
            elif name=='[Content_Types].xml' or name.endswith('.rels') or name=='word/settings.xml':
                part=etree.fromstring(data)
                if name=='[Content_Types].xml':
                    for e in list(part):
                        if e.get('PartName','').lstrip('/') in removed:part.remove(e)
                elif name.endswith('.rels'):
                    for e in list(part):
                        typ=e.get('Type','').lower()
                        if 'comment' in typ or typ.endswith('/people'):part.remove(e)
                elif name=='word/settings.xml':
                    for e in list(part):
                        if etree.QName(e).localname in {'trackRevisions','doNotTrackMoves','doNotTrackFormatting'}:part.remove(e)
                data=etree.tostring(part,encoding='UTF-8',xml_declaration=True,standalone=True)
            zout.writestr(deepcopy(item),data)
    with ZipFile(out) as z:
        newroot=etree.fromstring(z.read('word/document.xml'))
        result=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in newroot.xpath('//w:body/w:p',namespaces=ns)]
        expected=[]
        order=list(range(len(original)));order.remove(35);order.insert(order.index(31)+1,35)
        for i in order:
            t=original[i]
            expected.append(changes.get(i,t))
            expected.extend(ins['text'] for ins in cfg['inserts'] if ins['after']==i)
        assert result==expected
        assert len(result)==73
        assert [etree.tostring(d) for d in newroot.xpath('//w:drawing',namespaces=ns)]==drawings
        media={n:sha(z.read(n)) for n in z.namelist() if n.startswith('word/media/')}
        assert media=={n:sha(zin.read(n)) for n in zin.namelist() if n.startswith('word/media/')}
        assert z.read('word/styles.xml')==zin.read('word/styles.xml')
        assert all(z.read(n)==data for n,data in fields.items())
        assert not newroot.xpath('//w:commentRangeStart|//w:commentRangeEnd|//w:commentReference|//w:ins|//w:del',namespaces=ns)
        assert not any(re.search('(comments|people)',n,re.I) for n in z.namelist())
        assert '有来源支持' not in ''.join(result)
        assert '我需要用英文在NUS展示' not in ''.join(result)
        assert len(newroot.xpath('//w:drawing',namespaces=ns))==2
        # Existing reference formatting, images, body typography, and footer remain untouched.
        for i in range(61,71):
            orig=deepcopy(ps[i])
            for e in list(orig.iter()):
                if etree.QName(e).localname in {'commentRangeStart','commentRangeEnd','commentReference'}:e.getparent().remove(e)
            assert etree.tostring(orig,method='c14n',exclusive=True)==etree.tostring(newroot.xpath('//w:body/w:p',namespaces=ns)[i+2],method='c14n',exclusive=True)
    (W/'修改对照.json').write_text(json.dumps(changelog,ensure_ascii=False,indent=2))
    (W/'修订稿全文.md').write_text('\n\n'.join(result))
    report={'sha256':sha(out.read_bytes()),'baseline_sha256':sha(src.read_bytes()),'comments_addressed':5,'changed_original_paragraphs':sorted(changes),'insertions':cfg['inserts'],'layout_paragraph_move':{'original_paragraph':35,'after_original_paragraph':31,'text_unchanged':True},'body_count':cfg['body_count'],'body_han_count':cfg['body_han_count'],'count_method':'Han characters + English words + numeric groups; excluding headings, figure captions, source lines and bibliography.','main_count_including_headings_captions_sources':cfg['main_count_including_headings_captions_sources'],'media_unchanged':media,'drawings_preserved':len(drawings),'field_parts_byte_preserved':list(fields),'styles_unchanged':True,'unmodified_paragraph_texts_exactly_preserved':True,'existing_reference_xml_preserved':True,'removed_parts':sorted(removed)}
    (W/'content-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='insertions'},ensure_ascii=False))
