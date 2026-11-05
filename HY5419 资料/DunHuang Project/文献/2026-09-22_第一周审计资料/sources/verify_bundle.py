"""Verify paths, downloaded bytes, page counts and source/event references."""
from pathlib import Path
import argparse, csv, json, hashlib, re, urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from embedded_scan_storage import read_scan_bytes
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check-only',action='store_true',help='Do not rewrite the historical manifests or report')
parser.add_argument('--checked-date',default=datetime.now(ZoneInfo('Asia/Singapore')).date().isoformat())
args=parser.parse_args()
B=Path(__file__).resolve().parents[1]
def rows(name):
    with (B/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
problems=[]
catalogue=rows('资料目录.csv'); sources={r['SourceID']:r for r in catalogue}
for r in catalogue:
    if r['本地路径']:
        p=B/r['本地路径']
        if not p.is_file():problems.append('Missing source: '+r['SourceID'])
        elif digest(p)!=r['SHA256']:problems.append('Source hash mismatch: '+r['SourceID'])
events=rows('事件证据对照.csv')
with (B/'../../03_data_clean/edges.csv').open(encoding='utf-8-sig',newline='') as f:
    original={r['EventId'] for r in csv.DictReader(f)}
for r in events:
    if r['EventId'] not in original:problems.append('Unknown event: '+r['EventId'])
    if r['SourceID'] not in sources:problems.append('Unknown source: '+r['SourceID'])
    if not (B/r['本地来源']).is_file():problems.append('Evidence file missing: '+r['证据编号'])
covered={r['EventId'] for r in events}
if original!=covered:problems.append('Events not covered: '+str(original-covered))
rename=json.loads((B/'sources/整理路径映射.json').read_text())
checked=0; embedded_checked=0; discarded_failed_responses=0
cleanup_log=B/'../../06_notes/2026-10-27_文件整理/整理明细.csv'
discarded={}
if cleanup_log.exists():
    with cleanup_log.open(encoding='utf-8-sig',newline='') as handle:
        for item in csv.DictReader(handle):
            if item['action']=='delete' and item['category']=='失败下载':
                discarded[item['source']]=item
for p in (B/'sources').glob('download_batch*_results.json'):
    for r in json.loads(p.read_text()):
        if r['status'] in ['downloaded','already_present']:
            old='full-text/'+r['filename']; new=rename.get(old,old); dest=B/new
            if not dest.exists():
                try:
                    raw=read_scan_bytes(new)
                    if hashlib.sha256(raw).hexdigest()!=r['sha256']:problems.append('Embedded scan bytes changed: '+new)
                    embedded_checked+=1
                except FileNotFoundError:
                    removed=discarded.get(str(Path('文献/2026-09-22_第一周审计资料')/new))
                    if removed and removed['sha256']==r['sha256'] and new.startswith('sources/failed_responses/'):
                        discarded_failed_responses+=1
                    else:problems.append('Downloaded file missing: '+new)
            elif digest(dest)!=r['sha256']:problems.append('Downloaded bytes changed: '+new)
            checked+=1
for r in json.loads((B/'sources/PDF合成记录.json').read_text()):
    if digest(B/r['file'])!=r['sha256']:problems.append('Assembled PDF changed')
    if len(r['inputs'])!=r['page_count']:problems.append('Assembly page count mismatch')
pdfs=json.loads((B/'sources/PDF解析校验.json').read_text())
if len(pdfs)!=8 or not all(r['all_pages_parse'] and r['pages']>0 for r in pdfs):problems.append('PDF parse check failed')
expected={'S07_':6,'S22_':28}
for prefix,n in expected.items():
    match=[r for r in pdfs if Path(r['file']).name.startswith(prefix)]
    if len(match)!=1 or match[0]['pages']!=n:problems.append('Scan page count mismatch '+prefix)

# Hash every bundle file other than the two generated manifests themselves.
inventory=[]
for p in sorted(B.rglob('*')):
    if p.is_file() and p.name not in ['文件校验清单.csv','最终校验.json']:
        inventory.append({'相对路径':str(p.relative_to(B)),'字节数':p.stat().st_size,'SHA256':digest(p)})
if not args.check_only:
    with (B/'文件校验清单.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['相对路径','字节数','SHA256']);w.writeheader();w.writerows(inventory)

note=B/'../../06_notes/本周资料收集进度_2026-09-22.md'
links=0
for p in list(B.glob('*.md'))+[note]:
    for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if dest.startswith(('http:','https:','#')):continue
        target=p.parent/urllib.parse.unquote(dest.split('#')[0])
        if target.name=='最终校验.json':continue
        if not target.exists():problems.append('Broken link in '+p.name+': '+dest)
        links+=1
report={'checked_date':args.checked_date,'historical_bundle_date':'2026-09-22','status':'pass' if not problems else 'fail','new_works':9,'readable_files':len(list((B/'full-text').iterdir())),'catalogue_entries':len(catalogue),'evidence_rows':len(events),'covered_events':sorted(covered),'original_event_count':len(original),'download_records_hash_verified':checked,'embedded_scans_hash_verified':embedded_checked,'discarded_failed_download_responses':discarded_failed_responses,'pdfs_parse_verified':len(pdfs),'historical_render_spot_checks':['S07 assembled PDF page 3 = printed 825','S22 assembled PDF page 19 = printed 13'],'pdf_diagnostic':'Historical PDFKit diagnostics retained; this run checks files, hashes and references without a new visual review.','local_links_checked':links,'file_inventory_rows':len(inventory),'bundle_bytes_before_manifests':sum(r['字节数'] for r in inventory),'issues':problems}
if not args.check_only:(B/'sources/最终校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(problems))
