import hashlib, json, re
from html import escape
from pathlib import Path
import fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'sources'
OUT = ROOT / '05_Everingham_2021_Tourism_otherwise_全文英中逐段对照.pdf'
data = json.loads((SRC/'paragraphs_en.json').read_text())
translations = {}
for f in sorted(SRC.glob('translation_0*.json')):
    part = json.loads(f.read_text())
    assert not translations.keys() & part.keys()
    translations.update(part)
title_map = json.loads((SRC/'reference_titles_zh.json').read_text())
months = dict(zip('January February March April May June July August September October November December'.split(),range(1,13)))
def translate_ref(s):
    txt = s['en']
    for en, zh in title_map[s['id']]:
        assert en in txt, (s['id'],en)
        txt = txt.replace(en, '《'+zh+'》', 1)
    txt = re.sub(r'(\d{1,2})\s+('+'|'.join(months)+r'),?\s+(\d{4})',lambda m:f'{m[3]}年{months[m[2]]}月{m[1]}日',txt)
    txt = re.sub(r'(\d{4}),\s*(\d{1,2})\s+('+'|'.join(months)+r')',lambda m:f'{m[1]}年{months[m[3]]}月{m[2]}日',txt)
    txt = re.sub(r'(\d{1,2})\s+('+'|'.join(months)+r')',lambda m:f'{months[m[2]]}月{m[1]}日',txt)
    for en,zh in [('(n.d.)','（无日期）'),('(n.d)','（无日期）'),('(eds.)','（编）'),('(eds)','（编）'),('(ed.)','（编）'),('(2nd ed.)','（第2版）'),('(4th ed.)','（第4版）'),('PhD thesis','博士学位论文'),('Retrieved from ','检索网址：'),('Retrieved ','检索于：'),('[ONLINE]','［在线］'),('(Online)','（在线）'),('Online','在线'),(' online',' 在线'),('Ed.','编'),('ch.5','第5章')]:
        txt=txt.replace(en,zh)
    txt=re.sub(r'\bIn\.?\s', '载于 ', txt)
    txt=re.sub(r',?\sfrom,?\s', '，网址：', txt)
    txt=re.sub(r'\b[Pp]p\.\s*', '页 ', txt)
    return txt
for s in data['segments']:
    if s['kind']=='reference': translations[s['id']]=translate_ref(s)
all_segments = data['segments'] + data['footnotes']
assert set(translations)=={s['id'] for s in all_segments}
assert set(title_map)=={s['id'] for s in data['segments'] if s['kind']=='reference'}
for s in all_segments:
    s['zh']=translations[s['id']]
    assert re.search(r'[\u3400-\u9fff]',s['zh']),s['id']
(SRC/'paragraphs_bilingual.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))

fonts='/System/Library/Fonts/Supplemental/'
pdfmetrics.registerFont(TTFont('EN',fonts+'Times New Roman.ttf'))
pdfmetrics.registerFont(TTFont('ENBold',fonts+'Times New Roman Bold.ttf'))
pdfmetrics.registerFont(TTFont('ZH',fonts+'Songti.ttc',subfontIndex=6))
pdfmetrics.registerFont(TTFont('ZHBold',fonts+'Songti.ttc',subfontIndex=1))
pdfmetrics.registerFont(TTFont('UI',fonts+'Arial Unicode.ttf'))
navy=colors.HexColor('#18394A'); green=colors.HexColor('#286A67'); dark=colors.HexColor('#20252A'); muted=colors.HexColor('#66737B')
styles={
 'en':ParagraphStyle('en',fontName='EN',fontSize=10.5,leading=14.1,textColor=dark,spaceAfter=5,splitLongWords=True,allowWidows=0,allowOrphans=0),
 'zh':ParagraphStyle('zh',fontName='ZH',fontSize=10.4,leading=16.1,textColor=dark,wordWrap='CJK',spaceAfter=14,allowWidows=0,allowOrphans=0),
 'label':ParagraphStyle('label',fontName='UI',fontSize=7.1,leading=10,textColor=muted,spaceBefore=3,spaceAfter=3,keepWithNext=True),
 'hen':ParagraphStyle('hen',fontName='ENBold',fontSize=12,leading=15.2,textColor=navy,spaceBefore=11,spaceAfter=5,keepWithNext=True),
 'hzh':ParagraphStyle('hzh',fontName='ZHBold',fontSize=12,leading=18,textColor=navy,wordWrap='CJK',spaceAfter=12,keepWithNext=True),
 'refen':ParagraphStyle('refen',fontName='EN',fontSize=9.2,leading=12.4,textColor=dark,spaceAfter=4,splitLongWords=True,allowWidows=0,allowOrphans=0),
 'refzh':ParagraphStyle('refzh',fontName='ZH',fontSize=9.2,leading=14,textColor=dark,wordWrap='CJK',spaceAfter=10,allowWidows=0,allowOrphans=0),
 'cover':ParagraphStyle('cover',fontName='ZHBold',fontSize=22,leading=31,textColor=navy,wordWrap='CJK',spaceAfter=14),
 'coveren':ParagraphStyle('coveren',fontName='ENBold',fontSize=15,leading=20,textColor=navy,spaceAfter=15),
 'note':ParagraphStyle('note',fontName='ZH',fontSize=10,leading=16,wordWrap='CJK',textColor=dark,spaceAfter=10),
 'link':ParagraphStyle('link',fontName='EN',fontSize=9,leading=12,textColor=green,spaceAfter=10,splitLongWords=True),
}

story=[]
def add(text,style):story.append(Paragraph(escape(text),styles[style]))
add('HY5417 / SEMINAR 6','label')
story.append(Spacer(1,16))
add('以另一种方式开展旅游的（不）可能性','cover')
add('定居殖民背景下的澳大利亚与乌鲁鲁攀爬关闭案例','hzh')
add('The (im)possibilities of doing tourism otherwise: The case of settler colonial Australia and the closure of the climb at Uluru','coveren')
add('Phoebe Everingham · Andrew Peters · Freya Higgins-Desbiolles','en')
add('Annals of Tourism Research 88 (2021), 103178, pp. 1–11.','en')
add('英文一段 · 中文一段 | 作者接受稿全文对照','hzh')
add('底本为南澳大学机构库公开的同行评审后作者接受稿（现由阿德莱德大学机构库提供）。原文件共28页：机构库声明1页，论文编号1–26页，末页仅有页码。本文标题、作者信息、摘要、正文、四条脚注及91条参考文献均已收入；脚注集中置于正文后。期刊正式版11页也单独保存，引用时应以正式出版版本为准。','note')
add('各段标签标出作者稿自身的页码。原文换行已合并，跨页续段已接合；英文内容、原有数据、日期和书目信息按底本保留。参考文献逐条提供中文题名，作者、期刊与出版机构名称、DOI及网址保留以便检索。译文由AI生成并校对，属于非官方学习译稿。','note')
add('术语：coloniality＝殖民性；settler colonialism＝定居殖民主义；Country＝原乡（包括土地、亲缘、文化及灵性关系）；unlearning＝去习得；un-mapping＝解构地图；pluriversality＝多元世界性。','note')
add('作者稿许可为 CC BY-NC-ND 4.0。依据第2(a)(1)(B)条，仅为非商业私人学习制作本地改编稿；不得公开传播本对照译稿。原作权利归作者及相应权利人所有；译文不代表原作者认可。','note')
add('DOI: https://doi.org/10.1016/j.annals.2021.103178','link')
add('License: https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en','link')
add('Source: https://digital.library.adelaide.edu.au/server/api/core/bitstreams/b11c52b3-79d5-431d-839d-b99c508fccb0/content','link')
add('制作日期：2026年9月16日','label')
story.append(PageBreak())

def pair(s):
    if s['kind']=='heading':
        add(s['en'],'hen');add(s['zh'],'hzh')
        return
    page_label='、'.join(str(p-1) for p in s['pages'])
    add(f"{s['id']} · EN · 作者稿第{page_label}页",'label')
    ref=s['kind']=='reference'
    add(s['en'],'refen' if ref else 'en')
    add(f"{s['id']} · 中文",'label')
    add(s['zh'],'refzh' if ref else 'zh')

for s in data['segments']:
    if s['id']=='S080':
        story.append(PageBreak())
        add('NOTES','hen');add('原文脚注','hzh')
        for f in data['footnotes']:pair(f)
        story.append(PageBreak())
    pair(s)

page_locations={}
class Doc(SimpleDocTemplate):
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph):
            t=flowable.getPlainText()
            m=re.match(r'([SF]\d+) · (EN|中文)',t)
            if m:page_locations.setdefault(m[1],{})[m[2]]=self.page
            if flowable.style.name=='hzh':
                key=f'bookmark-{self.seq.nextf("bookmark")}'
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(t,key,0,False)
def page_art(canvas,doc):
    w,h=A4
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#DDE4E5'))
    canvas.setLineWidth(.5);canvas.line(44,h-35,w-44,h-35)
    canvas.setFont('UI',7.1);canvas.setFillColor(muted)
    canvas.drawString(44,h-26,'HY5417 · Seminar 6 | Everingham et al. (2021)')
    canvas.line(44,34,w-44,34)
    canvas.drawString(44,22,'私人学习译稿 · 作者接受稿 · English / 中文')
    canvas.drawRightString(w-44,22,str(doc.page))
    canvas.restoreState()
docout=Doc(str(OUT),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=47,bottomMargin=45,
           title='The (im)possibilities of doing tourism otherwise — 英中逐段对照',
           author='Original: Phoebe Everingham; Andrew Peters; Freya Higgins-Desbiolles. Translation: AI-assisted private study copy',
           subject='Full author accepted manuscript with paragraph-aligned Chinese translation; private noncommercial use only')
docout.build(story,onFirstPage=page_art,onLaterPages=page_art)
(SRC/'pdf_paragraph_locations.json').write_text(json.dumps(page_locations,ensure_ascii=False,indent=2))
print(OUT)
print('Pages:',len(fitz.open(OUT)), 'Segments:',len(all_segments), 'References:',len(title_map))

def compact(s):
    return re.sub(r'\s+','',s).replace('\u00ad','')
pdfdoc=fitz.open(OUT)
pdftext='\n'.join(page.get_text() for page in pdfdoc)
joined=compact(pdftext)
missing=[]
for s in all_segments:
    for lang in ['en','zh']:
        if compact(s[lang]) not in joined:
            # Headers and footers may intervene in a paragraph split across pages.
            chunks=re.split(r'HY5417|私人学习译稿',pdftext)
            cleaned=re.sub(r'HY5417 · Seminar 6 \| Everingham et al\. \(2021\)\s*','',pdftext)
            cleaned=re.sub(r'私人学习译稿 · 作者接受稿 · English / 中文\s*\d+\s*','',cleaned)
            if compact(s[lang]) not in compact(cleaned):missing.append((s['id'],lang))
report={'file':OUT.name,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
        'pages':len(pdfdoc),'paragraph_units':len(all_segments),'references':len(title_map),
        'source_line_count':data['source_line_count'],'missing_text_units':missing,
        'page_text_chars':[len(p.get_text()) for p in pdfdoc]}
(SRC/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('Missing text units:',missing)
