from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
from pypdf import PdfReader
from io import BytesIO
import json, hashlib, datetime

BASE=Path(__file__).resolve().parents[1]
STAMP='2026-09-27'
TARGETS=[
 ('A04','https://www.ssoar.info/ssoar/bitstream/document/31509/1/ssoar-2011-heng_et_al-Singapore_in_global_history.pdf','A04_Singapore_in_Global_History_2011_full_book.pdf'),
 ('A04chapter','https://www.degruyterbrill.com/document/doi/10.1515/9789048514373-009/pdf','A04_Lim_2011_Trans_Regional_Tea_Trading_Networks.pdf'),
 ('A02','https://www.sciencedirect.com/science/article/pii/S0261517799001089/pdfft?isDTMRedir=true&download=true','A02_Henderson_2000_Chinatown_Conservation_and_Promotion.pdf'),
 ('A03','https://brill.com/downloadpdf/book/9789004512986/BP000013.xml','A03_Chan_2023_Chineseness_of_Chinatown.pdf'),
]
def fetch(item):
 id,url,name=item
 rec=dict(id=id,date=STAMP,url=url)
 try:
  req=Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/pdf,text/html;q=0.8'})
  with urlopen(req,timeout=35) as response:
   content=response.read(); rec.update(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type',''),bytes=len(content))
  if content.startswith(b'%PDF'):
   pdf=PdfReader(BytesIO(content)); txt='\n'.join(p.extract_text() or '' for p in pdf.pages[:3])
   path=BASE/'fulltexts'/name; path.write_bytes(content)
   rec.update(kind='pdf',local=str(path.relative_to(BASE)),pages=len(pdf.pages),sha256=hashlib.sha256(content).hexdigest(),first_pages_text=txt[:3000])
  else:
   rec.update(kind='not_pdf',response_excerpt=content[:600].decode('utf-8',errors='replace'))
 except HTTPError as e:
  rec.update(kind='http_error',status=e.code,error=str(e),response_excerpt=e.read(400).decode('utf-8',errors='replace'))
 except Exception as e:rec.update(kind='error',error=repr(e))
 return rec
results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 for future in as_completed([pool.submit(fetch,t) for t in TARGETS]):
  rec=future.result();results.append(rec)
  print(json.dumps(rec,ensure_ascii=False),flush=True)
(BASE/'sources/retrieval_core_20260927.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
