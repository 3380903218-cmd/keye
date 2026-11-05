from pathlib import Path
import concurrent.futures, hashlib, json, requests, fitz
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent.parent
SOURCES = [
    ('G01_During_2015', 'html', 'https://programminghistorian.org/en/lessons/creating-network-diagrams-from-historical-sources'),
    ('G02_Ahnert_et_al_2020', 'pdf', 'https://www.cambridge.org/core/services/aop-cambridge-core/content/view/CC38F2EA9F51A6D1AFCB7E005218BBE5/9781108791908AR.pdf/the-network-turn.pdf'),
    ('G03_Faust_1997', 'pdf', 'https://sites.socsci.uci.edu/~kfaust/faust/research/articles/faust_centrality_sn_1997.pdf'),
    ('G04_Edelstein_et_al_2017', 'pdf', 'https://republicofletters.stanford.edu/publications/HistoricalResearch.pdf'),
    ('G05_Ahnert_Ahnert_2015', 'pdf', 'https://qmro.qmul.ac.uk/xmlui/bitstream/handle/123456789/10170/ProtestantLetterNetworks82.1.ahnert.pdf?sequence=6'),
    ('G10_Dotson_Doney_2025', 'pdf', 'https://uplopen.com/books/9085/files/69a133af-fbdf-4fd0-9cdd-0ca22ba39988.pdf'),
]

def fetch(entry):
    sid, kind, url = entry
    try:
        r = requests.get(url, timeout=45, headers={'User-Agent':'Mozilla/5.0 HY5419 academic reading package'})
        return entry, r.status_code, r.headers.get('Content-Type',''), r.url, r.content, None
    except Exception as exc:
        return entry, None, '', url, b'', str(exc)

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    fetched = list(pool.map(fetch, SOURCES))
for entry, code, ctype, final, data, err in fetched:
    sid, kind, url = entry
    rec = dict(source_id=sid, url=url, final_url=final, http_status=code, content_type=ctype, access_route='publisher_or_author_repository_OA_while_NUS_awaits_user_setup', error=err)
    if kind == 'pdf' and data[:5] == b'%PDF-':
        try:
            doc = fitz.open(stream=data, filetype='pdf')
            path = BASE/'full-text'/(sid+'.pdf')
            path.write_bytes(data)
            text = '\n'.join(f'\n[PDF PAGE {i+1}]\n'+page.get_text() for i,page in enumerate(doc))
            (BASE/'extracted'/(sid+'.txt')).write_text(text)
            rec.update(full_text_status='present', local_path=str(path.relative_to(BASE)), pages=len(doc), sha256=hashlib.sha256(data).hexdigest())
            print(sid, 'PDF', len(doc), 'pages', len(data), 'bytes', text[:700].replace('\n',' '), flush=True)
        except Exception as exc:
            rec.update(full_text_status='unavailable', error=str(exc))
    elif kind == 'html' and code == 200:
        soup=BeautifulSoup(data,'html.parser')
        if soup.h1 and 'Hermeneutics' in soup.h1.get_text():
            path=BASE/'full-text'/(sid+'.html'); path.write_bytes(data)
            for e in soup(['script','style','nav','footer']):e.decompose()
            text=soup.get_text('\n',strip=True)
            (BASE/'extracted'/(sid+'.txt')).write_text(text)
            rec.update(full_text_status='present',local_path=str(path.relative_to(BASE)),sha256=hashlib.sha256(data).hexdigest())
            print(sid, 'HTML', len(data),'bytes',text[:300].replace('\n',' '),flush=True)
        else: rec.update(full_text_status='unavailable',error='Expected article identity not found')
    else:
        rec.update(full_text_status='unavailable')
        (BASE/'sources'/(sid+'_failed_response.html')).write_bytes(data)
        print(sid,'UNAVAILABLE',code,ctype,err,flush=True)
    results.append(rec)
(BASE/'metadata'/'retrieval_status.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
