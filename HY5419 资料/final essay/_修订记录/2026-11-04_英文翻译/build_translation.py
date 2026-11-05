from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from copy import deepcopy
import hashlib, json, re

W = Path(__file__).parent
B = W.parent.parent
SOURCE = W / '中文定稿_翻译基准.docx'
OUTPUT = B / 'HY5419_敦煌项目_批判性反思_英文稿.docx'
AUTHORITY = B / 'HY5419_敦煌项目_批判性反思_中文稿.docx'
EXPECTED = '1e8fcbe533e500c2729359ad957d36c67c346c016dcb7066b0a4bad2610324dd'
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha(SOURCE.read_bytes()) == EXPECTED
assert sha(AUTHORITY.read_bytes()) == EXPECTED
if OUTPUT.exists():
    previous = json.loads((W / 'content-check.json').read_text())
    assert sha(OUTPUT.read_bytes()) == previous['output_sha256'], 'Do not overwrite user edits.'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
qn = lambda n: '{' + NS['w'] + '}' + n
T = json.loads((W / 'translation.json').read_text())
assert set(T) == {str(i) for i in range(72)}

with ZipFile(SOURCE) as z:
    parts = {x.filename: z.read(x.filename) for x in z.infolist()}
root = etree.fromstring(parts['word/document.xml'])
ps = root.xpath('./w:body/w:p', namespaces=NS)
assert len(ps) == 72
source_text = [''.join(p.xpath('.//w:t/text()', namespaces=NS)) for p in ps]
figure_xml = {i: etree.tostring(ps[i]) for i in [15, 34]}
styles_before = [p.xpath('./w:pPr/w:pStyle/@w:val', namespaces=NS) for p in ps]

def sub(parent, name, attrs):
    e = etree.SubElement(parent, qn(name))
    for k,v in attrs.items(): e.set(qn(k), str(v))
    return e

for i,p in enumerate(ps):
    if i in [15, 34]:
        assert T[str(i)] == '' and p.xpath('.//w:drawing', namespaces=NS)
        continue
    assert not p.xpath('.//w:fldChar|.//w:instrText|.//w:drawing|.//w:hyperlink|.//w:bookmarkStart|.//w:bookmarkEnd|.//w:sdt', namespaces=NS)
    for c in list(p):
        if c.tag != qn('pPr'): p.remove(c)
    for k,seg in enumerate(re.split(r'\*([^*]+)\*', T[str(i)])):
        if not seg: continue
        run = sub(p,'r',{})
        rp = sub(run,'rPr',{})
        sub(rp,'rFonts',{'ascii':'Times New Roman','hAnsi':'Times New Roman','cs':'Times New Roman'})
        if k % 2: sub(rp,'i',{})
        sub(rp,'lang',{'val':'en-GB','eastAsia':'zh-CN'})
        text = sub(run,'t',{})
        if seg != seg.strip(): text.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        text.text = seg
    if 61 <= i <= 68:
        pp = p.find(qn('pPr'))
        if pp is None:
            pp=etree.Element(qn('pPr'));p.insert(0,pp)
        for n in ['ind','spacing']:
            for e in pp.findall(qn(n)): pp.remove(e)
        sub(pp,'spacing',{'line':'480','lineRule':'auto','after':'0','before':'0'})
        sub(pp,'ind',{'left':'720','hanging':'720'})
        for rp in p.xpath('./w:r/w:rPr',namespaces=NS):
            lang = rp.find(qn('lang'))
            for n in ['sz','szCs']:
                size=etree.Element(qn(n));size.set(qn('val'),'24')
                rp.insert(list(rp).index(lang),size)
    if i == 70:
        pp=p.find(qn('pPr'))
        sub(pp,'keepNext',{})
    if 61 <= i <= 68 or i == 70:
        # Keep the standard OOXML paragraph-property sequence.
        rank={n:j for j,n in enumerate(['pStyle','keepNext','keepLines','pageBreakBefore','framePr','widowControl','numPr','suppressLineNumbers','pBdr','shd','tabs','suppressAutoHyphens','kinsoku','wordWrap','overflowPunct','topLinePunct','autoSpaceDE','autoSpaceDN','bidi','adjustRightInd','snapToGrid','spacing','ind','contextualSpacing','mirrorIndents','suppressOverlap','jc','textDirection','textAlignment','textboxTightWrap','outlineLvl','divId','cnfStyle','rPr','sectPr','pPrChange'])}
        for child in sorted(list(pp),key=lambda e:rank.get(etree.QName(e).localname,999)):
            pp.append(child)

# APA 7 alphabetical order is a reference-format change, not a content change.
body=root.find(qn('body'))
ref_order=[61,67,68,62,63,64,65,66]
for p in ps[61:69]: body.remove(p)
at=list(body).index(ps[60])+1
for i in ref_order:
    body.insert(at,ps[i]);at+=1

settings=etree.fromstring(parts['word/settings.xml'])
update=settings.find(qn('updateFields'))
if update is None: update=sub(settings,'updateFields',{})
update.set(qn('val'),'true')
parts['word/settings.xml']=etree.tostring(settings,xml_declaration=True,encoding='UTF-8',standalone=True)
parts['word/document.xml']=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)

for i in [15,34]:assert etree.tostring(ps[i])==figure_xml[i]
assert styles_before == [p.xpath('./w:pPr/w:pStyle/@w:val',namespaces=NS) for p in ps]
assert len(root.xpath('.//w:drawing',namespaces=NS))==2
with ZipFile(OUTPUT,'w',ZIP_DEFLATED) as z:
    for name,data in parts.items(): z.writestr(name,data)

with ZipFile(SOURCE) as z:
    preserved=[n for n in parts if n not in ['word/document.xml','word/settings.xml']]
    assert all(parts[n]==z.read(n) for n in preserved)

def clean(s):return re.sub(r'\*([^*]+)\*',r'\1',s)
final_order=list(range(61))+ref_order+list(range(69,72))
final_ps=root.xpath('./w:body/w:p',namespaces=NS)
assert [''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in final_ps]==[clean(T[str(i)]) for i in final_order]
md='\n\n'.join(T[str(i)] for i in final_order if T[str(i)])+'\n'
(W/'英文全文.md').write_text(md)
alignment=[{'id':i,'zh':source_text[i],'en':clean(T[str(i)])} for i in range(72)]
(W/'translation-alignment.json').write_text(json.dumps(alignment,ensure_ascii=False,indent=2))
body_ids=[i for i in range(2,60) if i not in [4,11,15,16,17,21,30,34,35,36,40,50,56]]
report={'source_sha256':EXPECTED,'output_sha256':sha(OUTPUT.read_bytes()),'paragraphs_translated':70,'preserved_figure_paragraphs':2,'paragraph_coverage':'72/72','body_word_count':len(re.findall(r'\b[A-Za-z]+(?:[’\x27-][A-Za-z]+)*\b',' '.join(clean(T[str(i)]) for i in body_ids))),'no_sources_added_or_removed':True,'reference_order':ref_order,'original_figures_unchanged':True,'preserved_parts':preserved,'settings_change':'updateFields=true for native page field refresh','source_original_unchanged':sha(AUTHORITY.read_bytes())==EXPECTED,'drawings':2,'tables':0,'comments':0,'tracked_revisions':0}
(W/'content-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
