from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree
from copy import deepcopy
import json,hashlib,re

B=Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/final essay')
W=B/'_修订记录/2026-11-04_第五轮批注修订';src=W/'批注原稿备份.docx';out=W/'修订候选.docx'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(src.read_bytes())=='81f781dfea6ccb4e8a8e4f6d9d8c9716e08f8d40b15393e6ce8842f87baae24c'
n={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};tag=lambda s:'{'+n['w']+'}'+s
def count(t):return len(re.findall(r'[\u3400-\u9fff]',t))+len(re.findall(r'[A-Za-z]+(?:[\-’\'][A-Za-z]+)*',t))+len(re.findall(r'\d+(?:[.\-—–]\d+)*',t))
with ZipFile(src) as zin:
 r=etree.fromstring(zin.read('word/document.xml'));ps=r.xpath('//w:body/w:p',namespaces=n)
 ts=[''.join(p.xpath('.//w:t/text()',namespaces=n)) for p in ps];assert len(ts)==72
 changes={
 41:ts[41].replace('我没有编程背景，又看到课堂中的互动网络可以帮助观察关系，便希望自己的网络也能被搜索、点击和查阅。','课堂上展示的互动网络给了我启发。我希望读者在网页中也能搜索人物、点击节点，并查阅具体关系。'),
 51:ts[51].replace('网站代码主要由AI协助生成和修改，我把反复使用的要求整理成skills，指导资料处理与网页制作。','我没有编程背景，网站代码主要由AI协助生成和修改。我把自己的设计思路和反复使用的要求整理成skills，用这些工作指令指导AI处理资料和制作网页。')
 }
 assert all(changes[i]!=ts[i] for i in changes)
 drawings=[etree.tostring(e) for e in r.xpath('//w:drawing',namespaces=n)]
 refindex=ts.index('参考文献')
 included=[i for i,p in enumerate(ps[:refindex]) if i>=2 and p.find('w:pPr/w:pStyle',n) is None and not ts[i].startswith(('图1 ','图2 ','来源：'))]
 oldbody=''.join(ts[i] for i in included);assert count(oldbody)==6722
 newbody=''.join(changes.get(i,ts[i]) for i in included)
 for i,new in changes.items():
  p=ps[i];assert not p.xpath('.//w:drawing|.//w:hyperlink|.//w:fldChar|.//w:instrText|.//w:fldSimple|.//w:bookmarkStart|.//w:bookmarkEnd',namespaces=n)
  for run in p.findall('w:r',n):
   if run.find('w:t',n) is None:continue
   rp=run.find('w:rPr',n);assert rp is None or {etree.QName(e).localname for e in rp}<={'lang'}
  txts=p.xpath('.//w:t',namespaces=n);txts[0].text=new;txts[0].set('{http://www.w3.org/XML/1998/namespace}space','preserve')
  for t in txts[1:]:t.text=''
 for e in list(r.iter()):
  if etree.QName(e).localname in {'commentRangeStart','commentRangeEnd','commentReference'}:e.getparent().remove(e)
 removed={p for p in zin.namelist() if re.search(r'(^|/)(comments[^/]*|people)\.xml$',p,re.I) or re.search(r'(^|/)_rels/(comments[^/]*|people)\.xml\.rels$',p,re.I)}
 with ZipFile(out,'w',ZIP_DEFLATED) as zout:
  for info in zin.infolist():
   name=info.filename
   if name in removed:continue
   data=zin.read(name)
   if name=='word/document.xml':data=etree.tostring(r,encoding='UTF-8',xml_declaration=True,standalone=True)
   elif name=='[Content_Types].xml' or name.endswith('.rels'):
    root=etree.fromstring(data)
    for e in list(root):
     if name=='[Content_Types].xml':drop=e.get('PartName','').lstrip('/') in removed
     else:drop='comment' in e.get('Type','').lower() or e.get('Type','').lower().endswith('/people')
     if drop:root.remove(e)
    data=etree.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
   zout.writestr(deepcopy(info),data)
 with ZipFile(out) as z:
  final=etree.fromstring(z.read('word/document.xml'));finalps=final.xpath('//w:body/w:p',namespaces=n)
  finaltexts=[''.join(p.xpath('.//w:t/text()',namespaces=n)) for p in finalps]
  assert finaltexts==[changes.get(i,t) for i,t in enumerate(ts)]
  assert [etree.tostring(e) for e in final.xpath('//w:drawing',namespaces=n)]==drawings
  assert not final.xpath('//w:commentRangeStart|//w:commentRangeEnd|//w:commentReference|//w:ins|//w:del',namespaces=n)
  assert not any(re.search('(comments|people)',p,re.I) for p in z.namelist())
  unchanged=[p for p in zin.namelist() if p not in removed and p not in {'word/document.xml','[Content_Types].xml'} and not p.endswith('.rels')]
  assert all(z.read(p)==zin.read(p) for p in unchanged)
  assert '我没有编程背景' not in finaltexts[41] and finaltexts[51].startswith('我没有编程背景')
  assert 6500<=count(newbody)<=7000
  media={p:sha(z.read(p)) for p in z.namelist() if p.startswith('word/media/')}
 (W/'修订稿全文.md').write_text('\n\n'.join(finaltexts))
 (W/'修改对照.json').write_text(json.dumps([{'paragraph':i,'before':ts[i],'after':v} for i,v in changes.items()],ensure_ascii=False,indent=2))
 actions=[{'comment_id':'0','status':'applied','action':'取消编程背景与交互目标之间的牵强关联；直接说明课堂互动网络的启发及希望读者如何使用网络。','paragraph':41},{'comment_id':'1','status':'applied','action':'在AI协作段落交代没有编程背景，并明确自己整理设计思路和工作要求为skills，指导AI处理资料和制作网页。','paragraph':51}]
 (W/'批注处理.json').write_text(json.dumps(actions,ensure_ascii=False,indent=2))
 report={'sha256':sha(out.read_bytes()),'baseline_sha256':sha(src.read_bytes()),'comments_addressed':2,'changed_paragraphs':[41,51],'body_count':count(newbody),'body_han_count':len(re.findall(r'[\u3400-\u9fff]',newbody)),'count_method':'Han characters + English words + numeric groups; headings, figures/captions/source notes and bibliography excluded.','unmodified_paragraph_texts_preserved':True,'unmodified_non_relationship_parts_byte_preserved':unchanged,'drawings_preserved':len(drawings),'media':media,'removed_comment_parts':sorted(removed)}
 (W/'content-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k not in {'unmodified_non_relationship_parts_byte_preserved','removed_comment_parts'}},ensure_ascii=False))
