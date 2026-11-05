from pathlib import Path
import subprocess,time,html,json
import fitz
from docx import Document

ROOT=Path(__file__).resolve().parent.parent
WORK=Path('/tmp/hy5305-delivery-work')

def chrome_pdf(source,pdf,profile):
    pdf.unlink(missing_ok=True)
    command=['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless','--disable-gpu','--disable-background-networking','--no-first-run','--user-data-dir='+str(WORK/profile),'--no-pdf-header-footer','--print-to-pdf='+str(pdf),source.as_uri()]
    with (WORK/(profile+'.log')).open('w') as log:
        process=subprocess.Popen(command,stdout=log,stderr=log)
        for _ in range(120):
            if pdf.exists():time.sleep(.5);break
            if process.poll() is not None:break
            time.sleep(.2)
        if process.poll() is None:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait()
    assert pdf.exists(),str(pdf)

slides=''.join('<section><img src="'+(WORK/f'deck-preview/slide-{i}.svg').as_uri()+'"></section>' for i in range(1,6))
lecture=WORK/'deck-preview.html'
lecture.write_text('<html><head><style>@page{size:338.6666666667mm 190.5mm;margin:0}html,body{margin:0}section{width:338.6666666667mm;height:190.5mm;page-break-after:always}section:last-child{page-break-after:auto}img{width:100%;height:100%;display:block}</style></head><body>'+slides+'</body></html>')
deck_pdf=WORK/'deck-svg-preview.pdf'
chrome_pdf(lecture,deck_pdf,'chrome-deck-preview')
deck=fitz.open(deck_pdf)
assert len(deck)==5,len(deck)
for i,page in enumerate(deck,1):page.get_pixmap(matrix=fitz.Matrix(1.15,1.15),alpha=False).save(WORK/f'deck-slide-{i}.jpg')

document=Document(ROOT/'HY5305_Porcelain_in_Translation_English_Chinese_Script.docx')
pages=[];page=[]
for p in document.paragraphs:
    if p._element.xpath('.//w:br[@w:type="page"]'):
        pages.append(page);page=[];continue
    if not p.text:continue
    fmt=p.paragraph_format
    run=p.runs[0]
    size=run.font.size.pt if run.font.size else 13.5
    face=run.font.name or 'Georgia'
    colour=str(run.font.color.rgb) if run.font.color.rgb else '262721'
    before=fmt.space_before.pt if fmt.space_before else 0
    after=fmt.space_after.pt if fmt.space_after else 0
    line=fmt.line_spacing if isinstance(fmt.line_spacing,float) else 1.16
    weight=700 if run.bold else 400
    page.append(f'<p style="font-family:\'{face}\';font-size:{size}pt;line-height:{line};font-weight:{weight};color:#{colour};margin:{before}pt 0 {after}pt">'+html.escape(p.text)+'</p>')
pages.append(page)
assert len(pages)==5
parts=[]
for i,blocks in enumerate(pages,1):
    parts.append('<section><header>PORCELAIN IN TRANSLATION | EN / 中文讲稿</header><main>'+''.join(blocks)+'</main><footer>English delivery under 8 minutes · '+str(i)+'</footer></section>')
word=WORK/'word-layout-preview.html'
word.write_text('<html><head><meta charset="utf-8"><style>@page{size:210mm 297mm;margin:0}body{margin:0}section{width:210mm;height:297mm;box-sizing:border-box;padding:18mm 20mm;position:relative;page-break-after:always}section:last-child{page-break-after:auto}header{position:absolute;top:8mm;left:20mm;font:9pt Georgia}footer{position:absolute;bottom:9mm;left:20mm;right:20mm;text-align:center;font:9pt Georgia}main{font-family:Georgia,"Songti SC"}</style></head><body>'+''.join(parts)+'</body></html>')
word_pdf=WORK/'word-browser-preview.pdf'
chrome_pdf(word,word_pdf,'chrome-word-preview')
script=fitz.open(word_pdf)
assert len(script)==5,len(script)
for i,page in enumerate(script,1):page.get_pixmap(matrix=fitz.Matrix(1.15,1.15),alpha=False).save(WORK/f'word-page-{i}.jpg')
print('Browser proofs: 5 presentation slides and 5 bilingual-script page sections.')
