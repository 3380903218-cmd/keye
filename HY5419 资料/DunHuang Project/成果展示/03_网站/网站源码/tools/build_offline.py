"""Export this checkout as a bilingual, standalone exhibition, with no remote assets."""
from pathlib import Path
import argparse, base64, re, urllib.parse

parser=argparse.ArgumentParser()
parser.add_argument('output',type=Path)
parser.add_argument('--lang',choices=('en','zh'),default='en')
args=parser.parse_args()
dist=Path(__file__).resolve().parents[1]/'dist'
html=(dist/'index.html').read_text(encoding='utf-8')
css_files=re.findall(r'<link\b[^>]*href="([^"]+\.css(?:\?[^"]*)?)"[^>]*>',html)
js_files=re.findall(r'<script\b[^>]*src="([^"]+\.js(?:\?[^"]*)?)"[^>]*>\s*</script>',html)
for ref in css_files:
    name=urllib.parse.urlsplit(ref).path
    html=re.sub(r'<link\b[^>]*href="'+re.escape(ref)+r'"[^>]*>',lambda m:'<style>'+(dist/name).read_text(encoding='utf-8')+'</style>',html)
for ref in js_files:
    html=re.sub(r'<script\b[^>]*src="'+re.escape(ref)+r'"[^>]*>\s*</script>','',html)
scripts='\n'.join((dist/urllib.parse.urlsplit(ref).path).read_text(encoding='utf-8') for ref in js_files)
if args.lang=='zh':
    scripts=scripts.replace("new URLSearchParams(window.location.search).get('lang')==='zh'?'zh':'en'","'zh'",1)
html=html.replace('</body>','<script>'+scripts.replace('</script','<\\/script')+'</script>\n</body>')
# Inline every local raster image used by HTML, including narrative photographs.
rasters=sorted(set(re.findall(r'(?:src|href)="(assets/[^"?]+\.(?:jpg|jpeg|png|webp))"',html)))
documents=sorted(set(re.findall(r'href="(assets/[^"?]+\.(?:pdf|gexf|csv|json))"',html)))
for name in rasters+documents+['assets/dunhuang-network.gexf']:
    suffix=Path(name).suffix.lower()
    mime={'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp','.gexf':'application/gexf+xml','.pdf':'application/pdf','.csv':'text/csv;charset=utf-8','.json':'application/json'}[suffix]
    html=html.replace(name,'data:'+mime+';base64,'+base64.b64encode((dist/name).read_bytes()).decode())
html=html.replace('assets/favicon.svg','data:image/svg+xml,'+urllib.parse.quote((dist/'assets/favicon.svg').read_text(encoding='utf-8'),safe=''))
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(html,encoding='utf-8')
print('Created standalone exhibition:',args.output.name,'language:',args.lang)
