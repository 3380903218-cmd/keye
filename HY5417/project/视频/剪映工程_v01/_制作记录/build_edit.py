from pathlib import Path
import json, subprocess, textwrap, math, wave, xml.etree.ElementTree as E
from fractions import Fraction
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]; MEDIA=ROOT.parent; WORK=ROOT/'_制作记录'
FF='/Users/arourouwed/Desktop/codex/toolchain/native-tools/.pixi/envs/default/bin/ffmpeg'
PROBE=FF.replace('ffmpeg','ffprobe')
G=ROOT/'图卡';G.mkdir(exist_ok=True)
BG='#151e20';CREAM='#f3eee2';TEAL='#84c4b6';MUTED='#b9c4bf'; GOLD='#d8b879'
REG='/System/Library/Fonts/Helvetica.ttc'; BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(n,b=False):return ImageFont.truetype(BOLD if b else REG,n)
def lines(d,text,xy,size=50,fill=CREAM,width=1500,bold=False,spacing=17):
 x,y=xy;f=font(size,bold)
 for para in text.split('\n'):
  buf=''
  for word in para.split():
   s=(buf+' '+word).strip()
   if d.textlength(s,font=f)>width and buf:
    d.text((x,y),buf,font=f,fill=fill); y+=size+spacing;buf=word
   else:buf=s
  d.text((x,y),buf,font=f,fill=fill);y+=size+spacing
 return y
cards={}
def card(key,kicker,title,body='',note='',diagram=None):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 d.rectangle((96,91,180,100),fill=TEAL)
 d.text((96,120),kicker.upper(),font=font(29,True),fill=TEAL)
 y=lines(d,title,(96,202),74,CREAM,1650,True,16)
 if diagram:
  yy=max(y+80,460); w=510; gap=72
  for i,(a,b) in enumerate(diagram):
   xx=96+i*(w+gap)
   d.rounded_rectangle((xx,yy,xx+w,yy+230),radius=12,fill='#233438',outline='#435958',width=2)
   lines(d,a,(xx+28,yy+24),37,TEAL,w-56,True,10)
   lines(d,b,(xx+28,yy+99),32,CREAM,w-56,False,11)
   if i<2 and key!='voices':
    ax=xx+w+16;ay=yy+118;d.line((ax,ay,ax+39,ay),fill=GOLD,width=3);d.polygon([(ax+39,ay),(ax+28,ay-8),(ax+28,ay+8)],fill=GOLD)
 else: lines(d,body,(100,y+57),43,MUTED,1570,False,20)
 if note:lines(d,note,(100,811),29,MUTED,1650,False,10)
 d.line((96,906,1824,906),fill='#42524f',width=2)
 d.text((100,1031),'CHINATOWN  /  BUILDINGS · LIVELIHOODS · RELATIONSHIPS',font=font(21),fill='#839590')
 im.save(G/f'{key}.png');cards[key]=G/f'{key}.png'
card('title','A public history film','The Buildings Remain.\nHow Does Life Continue?','Conservation and change in Singapore’s Chinatown','Wang Xiwen  |  HY5417  |  2026')
for key,k,t,b in [
 ('ch2','01 / A conserved district','What does conservation keep?','Buildings, living conditions and the choices between them.'),
 ('ch3','02 / Beyond the display','Visible culture. Everyday use.','How do celebrations and exhibitions connect with daily life?'),
 ('ch4','03 / Revitalisation','Who gains what?','Customers, costs and the conditions for staying.'),
 ('ch5','04 / A working tea business','Pek Sin Choon','Heritage carried through work, learning and relationships.'),
 ('ch6','05 / Shaping change','Whose voice can influence a decision?','Different users can value the same street in different ways.'),
 ('ch7','06 / Back to the street','Three questions to take with you','Look at what people can continue to do here.')]:card(key,k,t,b)
card('shophouse','Work and home','A building held connected uses.',diagram=[('Ground floor','Trade and everyday exchange'),('Upper floors','Living space and family life'),('The street','Movement, services and encounters')],note='Historical context: URA, Chinatown Historic District trail, pp. 1–2.')
card('choices','Remembering earlier life','Memory should include difficult conditions.','Overcrowding and poor sanitation were also part of the past.\nContinuity must allow people to improve their lives.','Context: Henderson (2000), pp. 526–527; URA historical trail.')
card('date','A conservation milestone','7 July 1989','Chinatown receives conservation status.\nProtecting the streetscape opens a further question: how can its uses continue?','Source: URA, Chinatown Historic District trail, pp. 1–2.')
card('visible','Two related questions','What is shown? What can continue?',diagram=[('Cultural display','Festivals and exhibitions'),('Everyday use','Work, shopping and gathering'),('Conditions','Space, resources and influence')])
card('costs','Assessing change','A benefit has to be understood with its costs.',diagram=[('Income','More visitors and customers'),('Costs','Rent, staffing and operation'),('Continuity','The ability to stay and transmit')])
card('limits','Reading the evidence','A shopkeeper is not every resident.','A report about some businesses is not a survey of the whole district.\nDifferent initiatives need to be assessed separately.')
card('practice','Living heritage','Continuity happens through practice.',diagram=[('Doing','Blending, tasting and packing'),('Learning','Sharing skills and experience'),('Adapting','New workshops and connections')],note='Conceptual lens: Poulios (2014). Visual case: NHB / Roots Sg (2025).')
card('quote','Kenry Peh / Pek Sin Choon','“Here to last.”','A hope for heritage businesses to remain in present life.','Short quotation from CNA, 1 November 2026. Full source listed in the accompanying source record.')
card('voices','The same place, different needs','“Community” contains many voices.',diagram=[('Residents','Daily life and continuing ties'),('Businesses','Livelihoods and transmission'),('Other users','Visitors, agencies and cultural groups')],note='Different needs can overlap; no single voice represents every user.')
card('influence','Participation and decisions','Taking part is only one form of influence.',diagram=[('Join','Attend an activity'),('Speak','Offer an opinion'),('Shape','Change an outcome')],note='Analytical question informed by Poulios (2014) and the project reading reflections.')
card('return','Connections beyond residence','Leaving a building need not end a relationship.','Returning to shop, work, worship or meet others can also sustain a connection.','Interpretive question informed by Yeoh & Kong (2012); not a claim about every former resident.')
card('q1','Question 1','Who can continue to use this place?','Look beyond the facade to the activities it makes possible.')
card('q2','Question 2','Do the benefits support continued work\nand transmission?','Visitor numbers alone cannot explain all the costs.')
card('q3','Question 3','Can different users influence change?','Examine the consequences of decisions as well as their intentions.')
card('credits1','A public history project','The Buildings Remain.\nHow Does Life Continue?','Research, field footage and interpretation: Wang Xiwen\nHY5417 · National University of Singapore · 2026','Initial cut v0.1.0 / r2. English synthetic narration: macOS Daniel; independently replaceable.')
card('credits2','Moving-image sources','Field observation and published films','Field footage: 13 clips supplied by Wang Xiwen.\nCNA: 30 Nov 2023; 8 Jan, 13 May, 18 May 2025; 1 Nov 2026.\nNHB / Roots Sg: Pek Sin Choon, 4 Apr 2025.','Original source logos and identities retained. Complete titles, links and clip timings accompany this project.')
card('credits3','Research and interpretation','Reading conservation through continued use','Henderson (2000) · Tourism Management 21(5): 525–534\nPoulios (2014) · The Past in the Present\nYeoh & Kong (2012) · Localities 2: 117–159\nGoh (2014) · TRaNS 2(1): 79–101\nChan (2023) · “The Chineseness of Chinatown in Singapore”','Historical chronology: URA, Chinatown Historic District trail. Full bibliography accompanies the project.')
card('credits4','Production note','Look again. Keep asking.','AI-assisted scripting, translation and edit preparation.\nTemporary local synthetic voice; source footage remains credited.','Prepared from the project’s existing research and footage. Initial cut for review; not yet submitted.')
# Sources and edit decisions. Times are seconds on the finished 25 fps timeline.
Sfiles=['0287720ba6da6426f2cb2676c01483db','3c6c67f7b5272aa2324fa98dd3a134e0','7297cb044842ecdddf78671b2262e225','76ab065286129349a3be8663ca8e7400','7cf7b40e0f4af282daa59f06519643b3','83893a7b87f6fa1dadc723d16e9b1cea','8ac019da8f77960c2429d99252f9c1cf','90884d6b5a7dc62ee420b53c6e88c343','98726540b1e54615f54998c231463dbb','ab09b94c74636b38e558855ca163abea','bc9f7fb8606579dcbd297a16468d4195','d9c6a0327faee41f0feb22d9d78e97f8','fc192df2de3c25edac1cd447e725c8db']
files={f'S{i:02}':MEDIA/(v+'.mp4') for i,v in enumerate(Sfiles,1)}
files.update({f'N{n}':next(MEDIA.glob(f'网络_{n}_*.mp4')) for n in ['01','03','06','08','09','10']})
files['N06V']=ROOT/'衍生素材/N06_旁白画面_下缘字幕避让.mp4';files.update(cards)
rows=[]
def add(a,b,key,src=0,quote=False):rows.append(dict(start=a,end=b,source=key,inpoint=src,original_audio=quote))
for r in [
 (0,7,'S03',2),(7,11,'S11',.4),(11,17,'S01',3),(17,22,'S07',1),(22,25,'S02',.2),(25,33,'S10',4),(33,40,'title'),
 (40,45,'ch2'),(45,53,'S09',1),(53,63,'shophouse'),(63,72,'N08',112),(72,84,'choices'),(84,92,'S10',6),(92,101,'date'),(101,110,'S08',1),
 (110,114,'ch3'),(114,123,'N09',52),(123,131,'N09',89),(131,136,'S12',1),(136,144,'N08',112),(144,152,'N08',120),(152,159,'visible'),(159,166,'S01',3),(166,172,'S07',0),(172,180,'S03',14),
 (180,184,'ch4'),(184,192,'N01',28),(192,199,'N01',74),(199,205,'N01',97),(205,214.2,'N01',107.6,True),(214.2,219,'S12',2),(219,227,'N03',26),(227,235,'N03',80),(235,241,'N03',123),(241,256.2,'N03',49.05,True),(256.2,263,'S13',3),(263,273,'costs'),(273,282,'S09',6),(282,290,'limits'),
 (290,293,'ch5'),(293,296,'S02',.25),(296,304,'N06V',37.5),(304,312,'N06V',113),(312,320,'N06V',177),(320,331,'N06V',234),(331,342.8,'N06',44.2,True),(342.8,345,'S12',2),(345,354,'N06V',142),(354,363,'practice'),(363,371,'N06V',296),(371,379,'N10',25),(379,388,'N10',48),(388,397,'N10',65),(397,402.4,'N10',74.7,True),(402.4,410,'quote'),
 (410,414,'ch6'),(414,424,'voices'),(424,431,'S04',1),(431,438,'S01',3),(438,448,'influence'),(448,456,'N10',65),(456,464,'N03',160),(464,474,'S08',0),(474,482,'S10',8),(482,490,'return'),
 (490,494,'ch7'),(494,503,'S03',3),(503,513,'q1'),(513,520,'N06V',232),(520,530,'q2'),(530,538,'S09',4),(538,548,'q3'),(548,556,'S13',7),(556,565,'S03',14),
 (565,575,'credits1'),(575,585,'credits2'),(585,595,'credits3'),(595,600,'credits4')]:add(*r)
assert all(abs(rows[i]['end']-rows[i+1]['start'])<1e-5 for i in range(len(rows)-1))
# Probe originals and cards, create normalized narration without changing timing.
meta={}
for k,p in files.items():
 if p.suffix=='.png':meta[k]={'width':1920,'height':1080,'fps':25,'duration':600,'audio':False};continue
 d=json.loads(subprocess.check_output([PROBE,'-v','error','-show_streams','-show_format','-of','json',str(p)]))
 v=next(s for s in d['streams'] if s['codec_type']=='video');meta[k]={'width':v['width'],'height':v['height'],'fps':str(v['r_frame_rate']),'duration':float(d['format']['duration']),'audio':any(s['codec_type']=='audio' for s in d['streams'])}
for r in rows:
 assert r['inpoint']+r['end']-r['start']<=meta[r['source']]['duration']+.06,r
narr=json.loads((WORK/'narration_rendered.json').read_text());aud=ROOT/'配音/标准化';aud.mkdir(exist_ok=True)
for i,b in enumerate(narr,1):
 p=aud/Path(b['file']).name
 if not p.exists():subprocess.run([FF,'-v','error','-y','-i',b['file'],'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','48000','-c:a','pcm_s16le',str(p)],check=True)
 b['normalized_file']=str(p)
# Captions: narration cues + four complete original statements.
raw_cues=json.loads((WORK/'narration_cues.json').read_text());cues=[]
for c in raw_cues:
 if cues and c['end']-c['start']<1.65 and c['start']-cues[-1]['end']<0.1 and not cues[-1]['text'].endswith(('.', '?', '!')) and len(cues[-1]['text'])+len(c['text'])<115 and c['end']-cues[-1]['start']<8:
  cues[-1]['text']+=' '+c['text'];cues[-1]['end']=c['end']
 else:cues.append(c.copy())
quotes=[(205.25,209.6,'He wishes to stay on under the new master tenant'),(209.6,213.99,"but hopes the rejuvenation project won't over-commercialise the area and drive up rents."),
 (241.26,243.54,'First of all is definitely the rental.'),(243.54,248.56,"Yeah, in this location, definitely it's not going to be low."),(249.46,255.92,'And subsequently, I think for us, manpower is a challenge.'),
 (331.34,335.9,'These 100 years in Singapore, we have been experiencing tea,'),(335.9,339.26,'drinking tea, sharing tea and making teas.'),(339.52,342.58,"It's all inside our blood for generations of us here."),
 (397.27,402.03,'Hopefully, Singapore will have more of the heritage businesses that are here to last.')]
for a,b,t in quotes:cues.append({'start':a,'end':b,'text':t,'kind':'source interview/report'})
cues.sort(key=lambda x:x['start'])
def wrap(t,width=62):
 ls=textwrap.wrap(t,width=width,break_long_words=False,break_on_hyphens=False)
 if len(ls)==2 and min(map(len,ls))<20:
  words=t.split();best=min(range(1,len(words)),key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))));ls=[' '.join(words[:best]),' '.join(words[best:])]
 return '\n'.join(ls)
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(ROOT/'字幕/03_English_Subtitles.srt').write_text('\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{wrap(c["text"])}' for i,c in enumerate(cues,1))+'\n')
# XML builder. Connected layers attach to the first spine clip using source-relative offsets.
def tm(s):return f'{round(s*25)}/25s'
def el(parent,tag,**a):return E.SubElement(parent,tag,{k:str(v) for k,v in a.items()})
x=E.Element('fcpxml',version='1.8');res=el(x,'resources');el(res,'format',id='fmt',name='FFVideoFormat1080p25',frameDuration='1/25s',width=1920,height=1080,colorSpace='1-1-1 (Rec. 709)')
ids={}
for i,(k,p) in enumerate(files.items(),1):
 if not any(r['source']==k for r in rows):continue
 m=meta[k];fid=f'f{i}';rid=f'a{i}';ids[k]=rid
 rate=Fraction(str(m['fps']));el(res,'format',id=fid,frameDuration=f'{rate.denominator}/{rate.numerator}s',width=m['width'],height=m['height'],colorSpace='1-1-1 (Rec. 709)')
 attrs=dict(id=rid,name=k+'_'+p.stem,start='0s',duration=tm(m['duration']),hasVideo=1,format=fid)
 if m['audio']:attrs.update(hasAudio=1,audioSources=1,audioChannels=2,audioRate=48000)
 a=el(res,'asset',**attrs);el(a,'media-rep',kind='original-media',src=p.as_uri())
for i,b in enumerate(narr,1):
 rid=f'voice{i}';a=el(res,'asset',id=rid,name=f'EN_{i:02}_replaceable',start='0s',duration=tm(b['duration']),hasAudio=1,audioSources=1,audioChannels=1,audioRate=48000);el(a,'media-rep',kind='original-media',src=Path(b['normalized_file']).as_uri())
el(res,'effect',id='text',name='Basic Title',uid='.../Titles.localized/Bumper:Opener.localized/Basic Title.localized/Basic Title.moti')
lib=el(x,'library');event=el(lib,'event',name='HY5417_Public_History');proj=el(event,'project',name='HY5417_Chinatown_v01_English_r2');seq=el(proj,'sequence',format='fmt',duration='600s',tcStart='0s',tcFormat='NDF',audioLayout='stereo',audioRate='48k');sp=el(seq,'spine');clips=[]
for r in rows:
 p=files[r['source']];c=el(sp,'asset-clip',name=f'{r["start"]:06.2f}_{r["source"]}',ref=ids[r['source']],offset=tm(r['start']),start=tm(r['inpoint']),duration=tm(r['end']-r['start']));clips.append(c)
 if p.suffix!='.png':
  el(c,'adjust-transform',position='0 5',scale='0.77 0.77')
  # Keep original speech only in the four deliberate sound bites; field ambience under narration.
  gain=('3dB' if r['source']=='N03' else '2dB' if r['source']=='N06' else '0dB') if r['original_audio'] else ('-28dB' if r['source'].startswith('S') else '-96dB')
  el(c,'adjust-volume',amount=gain)
anchor=clips[0];anchor_src=rows[0]['inpoint']
for i,b in enumerate(narr,1):el(anchor,'asset-clip',ref=f'voice{i}',name=f'EN narration {i:02} (replaceable)',lane=-1,offset=tm(anchor_src+b['start']),start='0s',duration=tm(b['duration']),audioRole='dialogue')
counter=0
def title(start,end,text,size=54,pos='0 -41.5',lane=2,color='1 1 1 1',name='EN subtitle'):
 global counter
 counter+=1;tid=f'ts{counter}';t=el(anchor,'title',ref='text',name=name,lane=lane,offset=tm(anchor_src+start),start='0s',duration=tm(end-start),role='titles')
 te=el(t,'text');st=el(te,'text-style',ref=tid);st.text=text
 de=el(t,'text-style-def',id=tid);el(de,'text-style',font='Helvetica Neue',fontSize=size,fontColor=color,alignment='center',bold=0,shadowColor='0 0 0 0.8',shadowOffset='2 2',shadowBlurRadius=3)
 el(t,'adjust-transform',position=pos,scale='1 1')
for c in cues:
 if 331<=c['start']<342.8:continue # This original excerpt already carries clear English source subtitles.
 title(c['start'],c['end'],wrap(c['text']))
labels={'N01':'CNA · 30 NOV 2023  |  SMITH STREET TENDER REPORT','N03':'CNA · 18 MAY 2025  |  HERITAGE CENTRE COLLABORATION','N06':'NHB / ROOTS SG · 4 APR 2025  |  ORIGINAL PEK SIN CHOON INTERVIEW','N06V':'NHB / ROOTS SG · 4 APR 2025  |  NARRATED VISUAL EXCERPT','N08':'CNA · 13 MAY 2025  |  HERITAGE CENTRE: RECONSTRUCTED EXHIBITS','N09':'CNA · 8 JAN 2025  |  CHINESE NEW YEAR COVERAGE','N10':'CNA · 1 NOV 2026  |  PEK SIN CHOON / HERITAGE BUSINESSES'}
for r in rows:
 if r['source'] in cards:continue
 label=labels.get(r['source'],'FIELD FOOTAGE · WANG XIWEN  |  CHINATOWN')
 if r['original_audio']:label+='  ·  ORIGINAL SOUND'
 title(r['start'],r['end'],label,31,'0 46.5',3,'0.75 0.85 0.81 1','Source / context')
E.indent(x);E.ElementTree(x).write(ROOT/'HY5417_Chinatown_v01_English_r2.fcpxml',encoding='utf-8',xml_declaration=True)
manifest={'version':'0.1.0','revision':'r2','duration':600,'fps':25,'cuts':len(rows),'source_files':{k:str(v) for k,v in files.items()},'edit':rows,'narration':narr,'captions':cues,'notes':['N06V is a muted visual derivative with the lower 144 pixels replaced by a black matte to avoid conflicting source subtitles; original retained for interview. No logo removed.','News lower-thirds, logos and identities remain in the visible frame.','Narration is local Daniel speech; subtitles are measured sentence-based timing, not word-for-word forced alignment.']}
(WORK/'edit_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
text=['# 初剪时间轴与来源','', '600秒，1920×1080，25fps；v0.1.0 / r2。原文件未修改。','', '| 成片 | 素材 | 原片入出点 | 声音 |','|---|---|---|---|']
for r in rows:text.append(f'| {r["start"]:.2f}–{r["end"]:.2f}s | {r["source"]} | {r["inpoint"]:.2f}–{r["inpoint"]+r["end"]-r["start"]:.2f}s | {"原声选段" if r["original_audio"] else "旁白／低音量现场环境"} |')
text+=['','## 素材路径','']+[f'- {k}: `{v.relative_to(MEDIA)}`' for k,v in files.items()]
(ROOT/'04_剪辑时间轴与来源.md').write_text('\n'.join(text)+'\n')
print('BUILT',len(rows),'cuts',len(cues),'captions')
