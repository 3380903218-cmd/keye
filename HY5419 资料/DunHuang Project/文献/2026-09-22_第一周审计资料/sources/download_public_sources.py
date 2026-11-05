from pathlib import Path
import urllib.request, urllib.error, json, hashlib, datetime, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(sys.argv[1])
ITEMS = json.loads(MANIFEST.read_text())
(ROOT / 'full-text').mkdir(exist_ok=True)

def fetch(item):
    result = dict(item)
    result['access_date'] = '2026-09-22'
    dest = ROOT / 'full-text' / item['filename']
    if dest.exists():
        data = dest.read_bytes()
        result.update(status='already_present', bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        return result
    try:
        request = urllib.request.Request(item['url'], headers={'User-Agent':'Mozilla/5.0 (academic source retrieval)'})
        with urllib.request.urlopen(request, timeout=35) as response:
            data = response.read(40 * 1024 * 1024 + 1)
            result.update(http_status=response.status, final_url=response.geturl(), content_type=response.headers.get('Content-Type', ''))
        if len(data) > 40 * 1024 * 1024:
            raise ValueError('Download exceeds 40 MiB cap')
        if dest.suffix == '.pdf' and not data.startswith(b'%PDF-'):
            raise ValueError('Expected PDF but received a different file type')
        if dest.suffix == '.html' and not any(s in data[:2000].lower() for s in [b'<html', b'<!doctype']):
            raise ValueError('Expected HTML but received a different file type')
        dest.write_bytes(data)
        result.update(status='downloaded', bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as exc:
        result.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    return result

results=[]
with ThreadPoolExecutor(max_workers=4) as executor:
    for future in as_completed([executor.submit(fetch, i) for i in ITEMS]):
        result=future.result(); results.append(result)
        print(result['source_id'], result['status'], result.get('bytes', ''), result.get('error', ''), flush=True)
out=ROOT/'sources'/(MANIFEST.stem+'_results.json')
out.write_text(json.dumps(sorted(results,key=lambda x:x['source_id']),ensure_ascii=False,indent=2))
print('Download log saved:',out.name,flush=True)
