# -*- coding: utf-8 -*-
"""Package the current exhibition into a standalone HTML file for presenting."""
from pathlib import Path
import base64, hashlib, json, re, urllib.parse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT/'dist'
OUTPUT = ROOT.parent/'敦煌互动传播地图.html'
record = ROOT.parent/'交付核验.json'
# Preserve any independently edited local exhibition before regeneration.
if OUTPUT.exists() and record.exists():
    previous=json.loads(record.read_text()).get('standalone_sha256')
    current=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    if previous and current!=previous:
        saved=OUTPUT.with_name(OUTPUT.stem+'_保留已有修改_'+current[:8]+'.html')
        if not saved.exists():saved.write_bytes(OUTPUT.read_bytes())
        print('Preserved edited standalone:',saved.name)
html=(DIST/'index.html').read_text()
for name in ['style.css','network.css']:
    html=re.sub(r'<link\b[^>]*href="'+re.escape(name)+r'"[^>]*>',lambda _,name=name: '<style>'+(DIST/name).read_text()+'</style>',html)
for name in ['data.js','assets/world.js','app.js','network-data.js','network.js']:
    html=re.sub(r'<script\b[^>]*src="'+re.escape(name)+r'"[^>]*>\s*</script>','',html)
scripts='\n'.join((DIST/name).read_text() for name in ['data.js','assets/world.js','app.js','network-data.js','network.js'])
html=html.replace('</body>','<script>'+scripts.replace('</script','<\\/script')+'</script>\n</body>')
html=html.replace('assets/diamond-sutra.jpg','data:image/jpeg;base64,'+base64.b64encode((DIST/'assets/diamond-sutra.jpg').read_bytes()).decode())
html=html.replace('assets/favicon.svg','data:image/svg+xml,'+urllib.parse.quote((DIST/'assets/favicon.svg').read_text(),safe=''))
html=html.replace('assets/dunhuang-network.gexf','data:application/gexf+xml;base64,'+base64.b64encode((DIST/'assets/dunhuang-network.gexf').read_bytes()).decode())
OUTPUT.write_text(html)
print('Standalone created:',OUTPUT.name,'sha256',hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
