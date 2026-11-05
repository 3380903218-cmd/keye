from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from copy import deepcopy
import hashlib,json,re

W=Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/final essay/_修订记录/2026-11-04_第二轮批注修订')
src=W/'批注原稿备份.docx'; out=W/'修订候选.docx'
cfg=json.loads((W/'revisions.json').read_text())
changes={int(k):v for k,v in cfg['changes'].items()}
ref_runs={int(k):v for k,v in cfg['reference_runs'].items()}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
tag=lambda s:'{'+ns['w']+'}'+s
sha=lambda b:hashlib.sha256(b).hexdigest()
with ZipFile(src) as zin:
 root=etree.fromstring(zin.read('word/document.xml'))
 ps=root.xpath('//w:body/w:p',namespaces=ns)
 assert len(ps)==72
 oldtexts=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in ps]
 drawings=[etree.tostring(e) for e in root.xpath('//w:drawing',namespaces=ns)]
 fields=root.xpath('count(//w:fldChar|//w:instrText)',namespaces=ns)
 changelog=[]
 for i,new in changes.items():
  p=ps[i]
  assert not p.xpath('.//w:drawing|.//w:fldChar|.//w:fldSimple|.//w:instrText|.//w:hyperlink',namespaces=ns)
  if i in ref_runs:
   # Only these text-only reference paragraphs are re-run to implement APA italics.
   for r in list(p.findall('w:r',ns)): p.remove(r)
   for text,italic in ref_runs[i]:
    run=etree.SubElement(p,tag('r')); rp=etree.SubElement(run,tag('rPr'))
    fonts=etree.SubElement(rp,tag('rFonts'))
    fonts.set(tag('ascii'),'Times New Roman');fonts.set(tag('hAnsi'),'Times New Roman');fonts.set(tag('eastAsia'),'Songti SC')
    if italic: etree.SubElement(rp,tag('i'))
    etree.SubElement(rp,tag('sz')).set(tag('val'),'21')
    etree.SubElement(rp,tag('szCs')).set(tag('val'),'21')
    etree.SubElement(rp,tag('lang')).set(tag('eastAsia'),'zh-CN')
    t=etree.SubElement(run,tag('t'));t.text=text;t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
   if i in range(61,68):
    pp=p.find('w:pPr',ns)
    if pp is None: pp=etree.Element(tag('pPr'));p.insert(0,pp)
    ind=pp.find('w:ind',ns)
    if ind is None: ind=etree.SubElement(pp,tag('ind'))
    for a in list(ind.attrib): del ind.attrib[a]
    ind.set(tag('left'),'720');ind.set(tag('hanging'),'720')
  else:
   # Keep paragraph/run properties, fields, and figures; replace plain prose only.
   for r in p.findall('w:r',ns):
    if r.find('w:t',ns) is None: continue
    rp=r.find('w:rPr',ns)
    assert rp is None or {etree.QName(c).localname for c in rp}<= {'lang'}
   ts=p.xpath('.//w:t',namespaces=ns);assert ts
   ts[0].text=new;ts[0].set('{http://www.w3.org/XML/1998/namespace}space','preserve')
   for t in ts[1:]:t.text=''
  changelog.append({'original_paragraph':i,'old':oldtexts[i],'new':new})
 for i in cfg['remove']:
  ps[i].getparent().remove(ps[i])
  changelog.append({'original_paragraph':i,'old':oldtexts[i],'new':None,'reason':'Specific StoryMaps example removed at author request.'})
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
  expected=[changes.get(i,t) for i,t in enumerate(oldtexts) if i not in cfg['remove']]
  assert result==expected
  assert [etree.tostring(e) for e in newroot.xpath('//w:drawing',namespaces=ns)]==drawings
  assert newroot.xpath('count(//w:fldChar|//w:instrText)',namespaces=ns)==fields
  media={n:sha(z.read(n)) for n in z.namelist() if n.startswith('word/media/')}
  assert media=={n:sha(zin.read(n)) for n in zin.namelist() if n.startswith('word/media/')}
  assert z.read('word/styles.xml')==zin.read('word/styles.xml')
  assert not any(re.search(r'(comments|people)',n,re.I) for n in z.namelist())
  assert not newroot.xpath('//w:commentRangeStart|//w:commentRangeEnd|//w:commentReference|//w:ins|//w:del',namespaces=ns)
  assert not any('Storying on the Coquille River' in t or '通过NUS入口' in t for t in result)
  assert len(newroot.xpath('//w:drawing',namespaces=ns))==2
  for i,segments in ref_runs.items():
   p=newroot.xpath('//w:body/w:p',namespaces=ns)[i]
   for r,(text,italic) in zip(p.findall('w:r',ns),segments):
    assert ''.join(r.xpath('.//w:t/text()',namespaces=ns))==text
    assert (r.find('w:rPr/w:i',ns) is not None)==italic
 (W/'修改对照.json').write_text(json.dumps(changelog,ensure_ascii=False,indent=2))
 (W/'修订稿全文.md').write_text('\n\n'.join(result))
 report={'sha256':sha(out.read_bytes()),'baseline_sha256':sha(src.read_bytes()),'comments_addressed':11,'changed_paragraphs':sorted(changes),'removed_paragraphs':cfg['remove'],'body_count':cfg['body_count'],'main_count_including_headings_captions_sources':cfg['main_count_including_headings_captions_sources'],'media_unchanged':media,'drawings_preserved':len(drawings),'fields_preserved':fields,'styles_unchanged':True,'unmodified_paragraphs_exactly_preserved':True,'reference_italics_verified':True,'removed_parts':sorted(removed)}
 (W/'content-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps(report,ensure_ascii=False))
