# -*- coding: utf-8 -*-
from pathlib import Path
import concurrent.futures,datetime,hashlib,json,re
from urllib.parse import quote
import requests,fitz
ROOT=Path(__file__).resolve().parent
jobs=[
 ('NUS_G06','https://libproxy1.nus.edu.sg/login?url=https://doi.org/10.1017/S1356186300009986',False),
 ('NUS_G10','https://libproxy1.nus.edu.sg/login?url=https://doi.org/10.1515/9783111569550-003',False),
 ('NUS_L06','https://libproxy1.nus.edu.sg/login?url=https://doi.org/10.1080/1547402X.2018.1522817',False),
 ('G10','https://uplopen.com/chapters/9085/files/a9be2fe2-4be9-49d9-b8fd-5db6628849a1.pdf',True),
 ('L06','https://soas-repository.worktribe.com/OutputFile/421743',True),
 ('G06_publisher','https://www.cambridge.org/core/journals/journal-of-the-royal-asiatic-society/article/abs/steins-recording-angel-miss-f-m-g-lorimer/DDBEAF0E1DB1819C6128FD8A586424ED',False),
 ('NUS_portal','https://lib.nus.edu.sg/',False),
]
def fetch(job):
 ident,url,pdf_expected=job;record=dict(id=ident,requested=url,date='2026-10-28',authenticated=False)
 try:
  r=requests.get(url,timeout=40,headers={'User-Agent':'Mozilla/5.0'})
  record.update(status=r.status_code,final_url=r.url,bytes=len(r.content),content_type=r.headers.get('Content-Type',''))
  if r.content.startswith(b'%PDF'):
   p=ROOT/'sources'/(ident+'_original.pdf');p.write_bytes(r.content)
   with fitz.open(p) as doc:pages=[page.get_text() for page in doc]
   (ROOT/'sources'/(ident+'_pages.json')).write_text(json.dumps(pages,ensure_ascii=False),encoding='utf-8')
   (ROOT/'sources'/(ident+'_text.txt')).write_text('\n\n'.join('=== PDF '+str(i+1)+' ===\n'+t for i,t in enumerate(pages)),encoding='utf-8')
   record.update(path=p.name,pages=len(pages),sha256=hashlib.sha256(r.content).hexdigest(),first_page=pages[0][:400])
  else:
   (ROOT/'sources'/(ident+'.html')).write_text(r.text,encoding='utf-8')
   title=re.search(r'<title[^>]*>(.*?)</title>',r.text,re.S|re.I)
   record['title']=re.sub(r'\s+',' ',title.group(1)) if title else ''
 except Exception as exc:record['error']=str(exc)
 return record
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:results=list(ex.map(fetch,jobs))
(ROOT/'sources/retrieval_log.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
