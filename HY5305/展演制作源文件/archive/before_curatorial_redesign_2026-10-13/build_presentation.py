from pathlib import Path
import json,math,re,base64
from PIL import Image
import slide_toolkit as t

ROOT=Path(__file__).resolve().parent.parent
SOURCE=Path(__file__).resolve().parent
WORK=Path('/tmp/hy5305-delivery-work')
WORK.mkdir(exist_ok=True)
PREVIEW=WORK/'deck-preview'
PREVIEW.mkdir(exist_ok=True)
content=json.loads((SOURCE/'presentation_content.json').read_text())
poster=ROOT/'HY5305_海报_参考风格竖版/Porcelain_in_Translation_Flow_A1_Portrait.png'
assert poster.exists()
vase=ROOT/'文物图片/微信图片_20260910150741_59_71.png'
bowl=ROOT/'海报制作源文件/assets/falangcai_bowl_highres.jpg'
plate=ROOT/'文物图片/微信图片_20260910154121_63_71.png'
pres=t.prs
slide_text=[]
timing=[]
clock=0

def start(index):
    if index>1:t.slide=pres.slides.add_slide(pres.slide_layouts[6])
    t.svg=[];t.svg_defs=[]
    t.rect(f'S{index} — warm paper',0,0,t.W,t.H,'paper')
    if index>1:
        t.path(f'S{index} — red-brown footer flow',[('M',0,179),('C',40,177,82,174,138,177),('L',138,190.5),('L',0,190.5),('Z',)],fill='wash')
        t.path(f'S{index} — gold flow trace',[('M',14,185),('C',48,179,89,190,128,181)],'gold',lw=.8)
    if index==5:t.rect('S5 — full-width concluding band',0,175,t.W,15.5,'river')
    t.text(f'S{index} — page number',f'{index} / 5',304,183,20,5,10.5,'ivory' if index==5 else 'muted',t.SANS,align='right')

def finish(index):
    global clock
    data=content['slides'][index-1]
    words=len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*",' '.join(data['english'])))
    secs=5*math.ceil((words*60/95+3)/5)
    timing.append({'slide':index,'title':data['title'],'english_words':words,'start_seconds':clock,'end_seconds':clock+secs,'target_seconds':secs})
    t.slide.notes_slide.notes_text_frame.text=f'Slide {index}: {data["title"]}\nSuggested segment: {clock//60}:{clock%60:02d}–{(clock+secs)//60}:{(clock+secs)%60:02d}. English speaking only.\n\n'+'\n\n'.join(data['english'])+('\n\nContext source: '+data['source'] if data.get('source') else '\n\nContent authority: project abstract.docx. Flows are conceptual.')
    clock+=secs
    svg='<?xml version="1.0" encoding="UTF-8"?>\n'+f'<svg xmlns="http://www.w3.org/2000/svg" width="{t.W}mm" height="{t.H}mm" viewBox="0 0 {t.W} {t.H}"><title>Slide {index}: {data["title"]}</title><defs>'+''.join(t.svg_defs)+'</defs>'+''.join(t.svg)+'</svg>'
    (PREVIEW/f'slide-{index}.svg').write_text(svg)
    slide_text.append([sh.text for sh in t.slide.shapes if sh.has_text_frame and sh.text])

def header(index,key,title):
    t.text(f'S{index} — world',key,150,13,175,8,16.5,'deep',t.SANS,bold=True,spacing=.25)
    t.text(f'S{index} — title',title,149,28,176,39,42,'ink',t.SERIF,leading=44)

def takeaway(index,txt):
    t.rect(f'S{index} — argument band',150,167,175,13,'river')
    t.text(f'S{index} — key argument',txt,155,170.3,165,10,17,'ivory',t.SANS,bold=True)

# 1 — The complete approved poster is the first visual, without cropping.
start(1)
with Image.open(poster) as im:poster_w=180*im.width/im.height
t.rect('S1 — poster border',8.8,3.8,poster_w+2.4,182.4,None,'gold',lw=.75)
t.picture('S1 — approved complete exhibition poster',poster,10,5,poster_w,180)
# Browser preview uses the same-source lower-resolution proxy; PPTX retains HD PNG.
proxy=WORK/'approved-poster-preview.jpg'
if proxy.exists():
    t.svg[-1]=re.sub(r'href="data:image/[^\"]+"','href="data:image/jpeg;base64,'+base64.b64encode(proxy.read_bytes()).decode()+'"',t.svg[-1])
t.text('S1 — exhibition title','PORCELAIN\nin translation',157,33,165,47,42,'ink',t.SERIF,leading=47)
t.text('S1 — original framing','One porcelain tradition.\nThree worlds.',158,88,164,25,25,'deep',t.SERIF,italic=True,leading=29)
t.text('S1 — research question','How does one material\nacquire different meanings?',158,122,163,23,23,'ink',t.SANS,leading=28)
t.path('S1 — theme rule',[('M',158,155),('L',321,155)],'gold',lw=1.2)
t.text('S1 — explicit topic','Qing China & global\ncultural exchange',158,163,163,22,21,'deep',t.SANS,bold=True,leading=26)
finish(1)

# 2 — Tradition, technique and imperial cultural identity.
start(2)
header(2,'01 / THE CHINESE PAST','Reinventing\ntradition')
t.picture('S2 — complete Langyao red vase',vase,49,38,59,131.31,crop=(253,273,581,1003),outline=t.vase_outline)
t.text('S2 — object','Langyao-red Guanyin vase',150,76,175,11,21,'ink',t.SANS,bold=True)
t.text('S2 — reign','Kangxi reign, 1662–1722',150,90,175,9,17,'muted',t.SANS)
t.text('S2 — technique','Jingdezhen revived\nMing copper-red glazing.',150,108,175,26,24,'ink',t.SANS,leading=29)
t.text('S2 — meaning','An inherited technique became\na statement of Qing identity.',150,137,175,25,24,'ink',t.SANS,leading=29)
takeaway(2,'TRADITION → IMPERIAL IDENTITY')
t.text('S2 — context source','Palace Museum',14,181,113,6,12,'ivory',t.SANS,url=content['slides'][1]['source'])
finish(2)

# 3 — Imported enamel knowledge transformed by Qing institutions.
start(3)
header(3,'02 / THE QING COURT','Translating\ntechnology')
t.text('S3 — visual subject','Swallows & flowering branches',14,47,122,10,17.5,'deep',t.SANS)
t.picture('S3 — complete imperial falangcai bowl',bowl,10,83,125,64.8,crop=(201,808,1806,1640),outline=t.bowl_outline)
t.text('S3 — object name','Imperial falangcai\n“swallows” bowl',14,153,123,21,20,'ink',t.SANS,bold=True,leading=24)
t.text('S3 — reign','Qianlong reign, 1736–1795',150,76,175,9,17,'muted',t.SANS)
t.text('S3 — combined knowledge','European enamel knowledge\n+ Chinese porcelain and painting',150,97,175,28,23,'ink',t.SANS,leading=29)
t.text('S3 — court agency','Selected and adapted in\nimperial court workshops.',150,134,175,26,24,'ink',t.SANS,leading=29)
takeaway(3,'FOREIGN KNOWLEDGE → COURT TASTE')
t.text('S3 — context source','Sotheby’s / Dr Alice Cheng bowl',14,181,115,6,11.5,'ivory',t.SANS,url=content['slides'][2]['source'])
finish(3)

# 4 — Heraldic designs move east, commissioned wares move west.
start(4)
header(4,'03 / EUROPEAN MARKETS','Responding to\nthe market')
t.picture('S4 — complete original armorial plate',plate,14,43,124,124,crop=(16,16,587,587),ellipse=True)
t.text('S4 — object date','China, eighteenth century',14,170,124,9,16,'ink',t.SANS)
t.text('S4 — object name','Chinese armorial export plate',150,76,175,10,21,'ink',t.SANS,bold=True)
t.text('S4 — interpretation','Chinese artisans translated\nEuropean heraldry into porcelain.',150,98,175,27,24,'ink',t.SANS,leading=29)
t.text('S4 — European patrons','EUROPE',150,135,46,9,18,'deep',t.SANS,bold=True)
t.text('S4 — Chinese production','CHINA',273,135,52,9,18,'deep',t.SANS,bold=True,align='right')
t.path('S4 — designs to China',[('M',201,138),('L',269,138)],'gold',lw=1.7,arrow=True)
t.path('S4 — porcelain to Europe',[('M',269,148),('L',201,148)],'deep',lw=1.7,arrow=True)
t.text('S4 — design flow label','Designs',213,128,48,8,15,'ink',t.SANS,align='center')
t.text('S4 — return flow label','Finished wares',205,151,63,8,15,'ink',t.SANS,align='center')
takeaway(4,'TRADE → STATUS AND IDENTITY')
t.text('S4 — context source','The Met / trade context',14,183,111,5,11,'ivory',t.SANS,url=content['slides'][3]['source'])
finish(4)

# 5 — The four-location network and shared argument, without another content slide.
start(5)
t.text('S5 — synthesis title','One tradition. Three worlds.',14,14,310,25,40,'ink',t.SERIF)
t.text('S5 — causal explanation','Patrons, institutions, production and use shaped meaning.',14,45,311,12,21,'deep',t.SANS)
for idx,x,w,world,mechanism,result in [
    (1,14,94,'CHINESE PAST','Reinventing\ntradition','Imperial identity'),
    (2,123,94,'QING COURT','Translating\ntechnology','Imperial taste'),
    (3,232,93,'EUROPEAN MARKETS','Responding to\nthe market','Status & identity'),
]:
    t.path(f'S5 — comparison rule {idx}',[('M',x,66),('L',x+w,66)],'gold',lw=.9)
    t.text(f'S5 — world {idx}',world,x,71,w,10,17,'deep',t.SANS,bold=True)
    t.text(f'S5 — mechanism {idx}',mechanism,x,87,w,29,29,'ink',t.SERIF,leading=31)
    t.text(f'S5 — meaning {idx}',result,x,118,w,10,18,'ink',t.SANS,bold=True)
e=(286,149);b=(185,140);j=(111,151);g=(185,163)
t.path('S5 — enamel knowledge',[('M',e[0]-2,e[1]-2),('C',255,132,218,131,b[0]+2,b[1])],'gold',lw=1.4,dashed=True,arrow=True)
t.path('S5 — armorial designs',[('M',e[0]-2,e[1]+2),('C',248,160,216,169,g[0]+2,g[1])],'gold',lw=1.2,dashed=True,arrow=True)
t.path('S5 — finished export porcelain',[('M',g[0]+2,g[1]-2),('C',214,151,251,151,e[0]-2,e[1]+1)],'deep',lw=1.6,arrow=True)
t.path('S5 — porcelain bodies to Beijing',[('M',j[0]+2,j[1]-1),('L',b[0]-2,b[1]+1)],'deep',lw=1,arrow=True)
t.path('S5 — wares to Guangzhou',[('M',j[0]+2,j[1]+1),('L',g[0]-2,g[1]-1)],'deep',lw=1,arrow=True)
for label,pt in [('Europe',e),('Beijing',b),('Jingdezhen',j),('Guangzhou',g)]:t.rect('S5 — node '+label,pt[0]-.85,pt[1]-.85,1.7,1.7,'deep',ellipse=True)
t.text('S5 — Jingdezhen','Jingdezhen',14,145,85,9,15.5,'ink',t.SANS,bold=True)
t.text('S5 — Beijing','Beijing',159,131,70,9,15.5,'ink',t.SANS,bold=True)
t.text('S5 — Guangzhou','Guangzhou',152,164,77,9,15.5,'ink',t.SANS,bold=True)
t.text('S5 — Europe','Europe',290,144,36,9,15.5,'ink',t.SANS,bold=True)
t.text('S5 — flow qualification','Conceptual flows / schematic routes',14,163,122,7,10.5,'muted',t.SANS)
t.text('S5 — concluding claim','Qing China actively shaped global exchange.',14,178,278,11,24,'ivory',t.SANS,bold=True)
finish(5)

pres.core_properties.title='Porcelain in Translation — exhibition presentation'
pres.core_properties.subject='Five slides: approved poster plus four content slides; English delivery under eight minutes'
pres.core_properties.author=''
pres.core_properties.keywords='porcelain, Qing China, global cultural exchange, exhibition, English'
file=ROOT/'HY5305_Porcelain_in_Translation_8min.pptx'
pres.save(file)
(SOURCE/'presentation_timing.json').write_text(json.dumps({'english_words':sum(x['english_words'] for x in timing),'target_seconds':clock,'pace_words_per_minute':95,'slides':timing},ensure_ascii=False,indent=2))
(SOURCE/'presentation_layout_checks.json').write_text(json.dumps(t.checks,ensure_ascii=False,indent=2))
(SOURCE/'presentation_display_text.json').write_text(json.dumps(slide_text,ensure_ascii=False,indent=2))
bad=[c for c in t.checks if not c['fits']]
print('Created',file)
print('Slides:',len(pres.slides),'English words:',sum(x['english_words'] for x in timing),'Target seconds:',clock,'Text overflow:',len(bad))
for c in bad:print(c)
