"""Verify public static assets, the Gephi snapshot and portable relative paths."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib, json, re, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist'
class References(HTMLParser):
    def __init__(self):super().__init__();self.items=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ('script','img') and 'src' in attrs:self.items.append(attrs['src'])
        if tag=='link' and 'href' in attrs:self.items.append(attrs['href'])
page=References();page.feed((DIST/'index.html').read_text(encoding='utf-8'))
for ref in page.items:
    url=urlsplit(ref)
    if url.scheme or not url.path:continue
    assert not url.path.startswith('/'),f'Root-relative asset breaks a project Pages URL: {ref}'
    p=(DIST/unquote(url.path)).resolve();assert DIST.resolve() in p.parents and p.is_file(),ref
source=(DIST/'network-data.js').read_text(encoding='utf-8');prefix='window.DUNHUANG_NETWORK = '
assert source.startswith(prefix)
data=json.loads(source[len(prefix):].strip().removesuffix(';'))
assert len(data['nodes'])==122 and len(data['edges'])==136
assert len(data['events'])==42 and len(data['sources'])==21 and len(data['evidence'])==49
assert all(e.get('claimEN') and e.get('limitEN') for e in data['evidence'])
node_ids={n['id'] for n in data['nodes']}
assert all(e['source'] in node_ids and e['target'] in node_ids for e in data['edges'])
gexf=DIST/'assets/dunhuang-network.gexf'
assert hashlib.sha256(gexf.read_bytes()).hexdigest()==data['meta']['sourceHash']
xml=ET.parse(gexf).getroot();ns={'g':xml.tag.split('}')[0][1:]}
assert len(xml.findall('.//g:node',ns))==122 and len(xml.findall('.//g:edge',ns))==136
extra_source=(DIST/'relationship-supplement-data.js').read_text(encoding='utf-8')
extra=json.loads(extra_source.split('=',1)[1].strip().removesuffix(';'))
assert extra['meta']['baseHash']==data['meta']['sourceHash']
assert [len(extra[k]) for k in ('nodes','edges','events','evidence')]==[10,21,6,8]
expanded=ET.parse(DIST/'assets/dunhuang-network-expanded.gexf').getroot()
assert len(expanded.findall('.//g:node',ns))==132 and len(expanded.findall('.//g:edge',ns))==157
for kind in ('node','edge'):
    originals={x.get('id'):x for x in xml.findall('.//g:'+kind,ns)}
    extended={x.get('id'):x for x in expanded.findall('.//g:'+kind,ns)}
    for key,item in originals.items():
        other=extended[key]
        assert item.attrib==other.attrib
        def semantic(element):
            return (element.tag,sorted(element.attrib.items()),tuple(semantic(c) for c in element))
        assert semantic(item)==semantic(other),key
assert all(e.get('claimEN') and e.get('limitEN') and e.get('primaryReference') for e in extra['evidence'])
manifest=json.loads((ROOT/'publication-manifest.json').read_text())
if manifest.get('qgis_pdf_sha256'):
    assert hashlib.sha256((DIST/'assets/qgis-regional-map.pdf').read_bytes()).hexdigest()==manifest['qgis_pdf_sha256']
for e in manifest['publication_files']:
    p=ROOT/e['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'],e['path']
for p in DIST.rglob('*'):
    if p.is_file() and p.suffix in ('.html','.js','.css','.json','.gexf'):
        text=p.read_text(encoding='utf-8');assert '/Users/' not in text,p
assert not (ROOT/'.openai').exists()
print('PASS: local assets, project-subpath URLs, original Gephi export, evidence records and publication hashes.')
