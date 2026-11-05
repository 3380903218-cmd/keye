from pathlib import Path
import json,hashlib,subprocess,time
import fitz

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'HY5305_海报_参考风格竖版'
WORK=Path('/tmp/hy5305-delivery-work')
WORK.mkdir(exist_ok=True)
record=json.loads((ROOT/'海报制作源文件/flow_portrait_validation.json').read_text())
svg=OUT/'Porcelain_in_Translation_Flow_A1_Portrait.svg'
assert hashlib.sha256(svg.read_bytes()).hexdigest()==record['files'][svg.name]['sha256']
html=WORK/'approved-poster-export.html'
html.write_text('<html><head><style>@page{size:594mm 841mm;margin:0}html,body{margin:0;width:594mm;height:841mm}img{display:block;width:594mm;height:841mm}</style></head><body><img src="'+svg.as_uri()+'"></body></html>')
pdf=WORK/'approved-poster-export.pdf'
pdf.unlink(missing_ok=True)
cmd=['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless','--disable-gpu','--disable-background-networking','--no-first-run','--user-data-dir='+str(WORK/'chrome-poster-export'),'--no-pdf-header-footer','--print-to-pdf='+str(pdf),html.as_uri()]
with (WORK/'chrome-poster-export.log').open('w') as log:
    proc=subprocess.Popen(cmd,stdout=log,stderr=log)
    for _ in range(120):
        if pdf.exists():time.sleep(.5);break
        if proc.poll() is not None:break
        time.sleep(.2)
    if proc.poll() is None:
        proc.terminate()
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
assert pdf.exists(),'No fresh poster render was produced'
doc=fitz.open(pdf)
assert len(doc)==1
page=doc[0]
size=[v*25.4/72 for v in (page.rect.width,page.rect.height)]
assert abs(size[0]-594)<.3 and abs(size[1]-841)<.3,size
width,height=7016,9933
pix=page.get_pixmap(matrix=fitz.Matrix((width-.01)/page.rect.width,(height-.01)/page.rect.height),alpha=False)
assert (pix.width,pix.height)==(width,height)
pix.set_dpi(300,300)
png=OUT/'Porcelain_in_Translation_Flow_A1_Portrait.png'
pix.save(png)
preview=page.get_pixmap(matrix=fitz.Matrix(.6,.6),alpha=False)
preview.save(WORK/'approved-poster-preview.jpg')
print('Exported approved poster:',png)
print('Pixels:',width,height,'DPI: 300')
