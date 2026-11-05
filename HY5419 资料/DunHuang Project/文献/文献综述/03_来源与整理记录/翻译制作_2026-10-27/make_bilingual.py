# -*- coding: utf-8 -*-
"""Local, resumable paragraph translation and source-preserving PDF composition.

Original PDFs are never modified. English blocks in the reading copy are placed
directly from the source PDF, not recreated from imperfect text extraction.
"""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, re, time, unicodedata, os, shutil
from collections import Counter
from io import BytesIO
from xml.sax.saxutils import escape
import fitz
import requests
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                               Flowable, KeepTogether)
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
INPUT = BASE / '01_待读文献PDF' / '英文文献'
OUTPUT = INPUT / '翻译版'
ENDPOINT = 'http://127.0.0.1:15819/v1/chat/completions'

DOCS = [
 dict(key='L01', prefix='04_', title='Wang Yuanlu, the first “curator” of the Stein collection’s Dunhuang corpus',
      zh='王圆箓：斯坦因藏敦煌文献的首位“保管者”', by='Mélodie Doumy · 2025', doi='10.1017/S1356186325000161'),
 dict(key='L02', prefix='05_', title='Reconstructing a Medieval Library? The Contents of the Manuscript Bundles in the Dunhuang Library Cave',
      zh='重建一座中世纪藏书库？敦煌藏经洞写本卷束的内容', by='Paschalia Terzi & Susan Whitfield · 2024', doi='10.5334/srah.8'),
 dict(key='G03', prefix='09_', title='Centrality in affiliation networks',
      zh='二模参与网络中的中心性', by='Katherine Faust · 1997', doi='10.1016/S0378-8733(96)00300-0'),
 dict(key='G04', prefix='10_', title='Historical Research in a Digital Age: Reflections from the Mapping the Republic of Letters Project',
      zh='数字时代的历史研究：“文人共和国地图”项目的反思', by='Dan Edelstein et al. · 2017', doi='10.1093/ahr/122.2.400'),
 dict(key='L08', prefix='12_', title='Buddhism and Silk: Reassessing a Painted Banner from Medieval Central Asia in The Met',
      zh='佛教与丝绸：重新审视大都会艺术博物馆收藏的一件中世纪中亚绘幡',
      by='Michelle C. Wang, Xin Wen & Susan Whitfield · 2020', doi='10.1086/712767'),
 dict(key='G13', prefix='02_', title='Sir Aurel Stein, Colleagues and Collections',
      zh='斯坦因、同事与收藏', by='Helen Wang (ed.) · 2012', doi=''),
 dict(key='G02', prefix='11_', title='The Network Turn: Changing Perspectives in the Humanities',
      zh='网络转向：人文学科视角的变迁', by='Ruth Ahnert, Sebastian E. Ahnert, Catherine Nicole Coleman & Scott B. Weingart · 2020', doi='10.1017/9781108866804'),
]

# Only terms occurring in a source segment are included in its prompt.
TERMS = [
 ('Wang Yuanlu', '王圆箓'), ('Wang Yüan-lu', '王圆箓'), ('Wang Yuan-lu', '王圆箓'),
 ('Wang Jiayan', '王家彦'), ('Wang Zonghan', '汪宗翰'), ('Huang Wanchun', '黄万春'),
 ('Pan Zhen', '潘震'), ('Ye Changchi', '叶昌炽'), ('Ye Changshi', '叶昌炽'),
 ('Lin Taiqing', 'Lin Taiqing'), ('Zhang Huming', 'Zhang Huming'),
 ('Zhang Jianming', 'Zhang Jianming'), ('He Lin', 'He Lin'),
 ('Aurel Stein', '奥雷尔·斯坦因'), ('Stein', '斯坦因'), ('Paul Pelliot', '保罗·伯希和'), ('Pelliot', '伯希和'),
 ('Jiang Xiaowan', '蒋孝琬'), ('Chiang Ssu-yeh', '蒋师爷'), ('Jiang Shiye', '蒋师爷'),
 ('Shiye', '师爷'), ('Ssu-yeh', '师爷'), ('Ssŭ-yeh', '师爷'), ('Daoshi', '道士'), ('[D]aoshi', '道士'),
 ('Dunhuang', '敦煌'), ('Tun-huang', '敦煌'), ('Mogao', '莫高'),
 ('Library Cave', '藏经洞'), ('library cave', '藏经洞'), ('Cave 17', '第17窟'),
 ('Cave 16', '第16窟'), ('photographing', '拍摄照片'), ('photographed', '拍摄'),
 ('regular bundles', '常规卷束'), ('pothis', '梵夹装写本'), ('pothi', '梵夹装写本'),
 ('dispersal', '流散'), ('manuscripts', '写本'), ('manuscript', '写本'),
 ('bundles', '卷束'), ('bundle', '卷束'), ('scrolls', '卷子'), ('scroll', '卷子'),
 ('rolls', '卷'), ('roll', '卷'), ('corpus', '文献总集'), ('curator', '保管者'),
 ('affiliation networks', '二模参与网络'), ('affiliation network', '二模参与网络'),
 ('affiliation relation', '参与关系'), ('non-dyadic', '非二元关系'), ('dual networks', '对偶网络'),
 ('one-mode projection', '单模投影'), ('bipartite network', '二部网络'),
 ('membership', '成员资格'), ('subsets', '子集'), ('subset', '子集'),
 ('directed network', '有向网络'), ('undirected network', '无向网络'),
 ('community detection', '社群发现'), ('missing data', '缺失数据'),
 ('uncertainty', '不确定性'), ('courier', '信使'),
 ('beg for alms', '募化'), ('begging for alms', '募化'), ('alms round', '募化行程'),
 ('begging tours', '募化之旅'),
 ('Mahāmāyūrī', '孔雀明王'), ('dharani', '陀罗尼'), ('dharanis', '陀罗尼'),
 ('dhāraṇī', '陀罗尼'), ('mantra', '真言'), ('mantras', '真言'),
 ('two-mode', '二模'), ('one-mode', '单模'), ('bipartite', '二部'),
 ('betweenness centrality', '中介中心性'), ('closeness centrality', '接近中心性'),
 ('flow betweenness centrality', '流中介中心性'), ('flow betweenness', '流中介中心性'),
 ('degree centrality', '度中心性'), ('eigenvector centrality', '特征向量中心性'),
 ('centrality', '中心性'), ('centralization', '中心势'), ('adjacency matrix', '邻接矩阵'), ('incidence matrix', '关联矩阵'),
 ('projection', '投影'), ('actors', '行动者'), ('actor', '行动者'),
 ('events', '事件'), ('event', '事件'),
 ('Republic of Letters', '文人共和国'), ('provenance', '来源与流传记录'),
 ('British Library', '英国图书馆'), ('British Museum', '大英博物馆'),
 ('Bibliothèque nationale de France', '法国国家图书馆'),
 ('Metropolitan Museum of Art', '大都会艺术博物馆'),
]

def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def norm_text(s):
    s = unicodedata.normalize('NFKC', s)
    s = s.replace('\u00ad','').replace('\x1b',' × ').replace('\ufffd','[无法识别字符]')
    s = s.replace('WangYuanlu','Wang Yuanlu')
    if re.fullmatch(r'(?:[A-Z] ?){4,}',s.strip()) and s.count(' ')>=len(s.replace(' ',''))/2:
        s=s.replace(' ','')
    # British Museum's PDF separates typographic ligatures in text extraction.
    for wrong, right in [('offi cial','official'), ('diff er','differ'), ('fi rst','first'),
                         ('eff ect','effect'), ('identifi c','identific'), ('signifi c','signific'),
                         ('suffi c','suffic'), ('specifi c','specific'), ('fi nd','find'),
                         ('fi ve','five'), ('fi nal','final'), ('fi gure','figure')]:
        s = re.sub(re.escape(wrong).replace(r'\ ',r'\s+'),right,s,flags=re.I)
    return re.sub(r'\s+',' ',s).strip()

def lines_text(lines):
    parts=[]
    for line in lines:
        s=''.join(span.get('text','') for span in sorted(line['spans'],key=lambda z:z['bbox'][0])).strip()
        if parts and parts[-1].endswith('-') and s[:1].islower():
            parts[-1]=parts[-1][:-1]+s
        else: parts.append(s)
    return norm_text(' '.join(parts))

def extract(docmeta, scope):
    src=next(INPUT.glob(docmeta['prefix']+'*.pdf'))
    doc=fitz.open(src)
    pages=list(range(len(doc)))
    if scope=='selected' and docmeta['key']=='G13': pages=list(range(23,29))+list(range(104,113))
    if scope=='selected' and docmeta['key']=='G02': pages=list(range(50,80))
    segments=[];excluded=[]
    for pi in pages:
        page=doc[pi];original_rotation=page.rotation
        # Text extraction uses unrotated coordinates. Work in that same frame;
        # retain the source display rotation for the later vector placement.
        if original_rotation:page.set_rotation(0)
        w=page.rect.width;h=page.rect.height
        blocks=[b for b in page.get_text('dict', flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] if b.get('type')==0]
        # Reading order: top spanning title/header, left column, right column,
        # and bottom spanning material. Never interleave two body columns.
        left=[b for b in blocks if b['bbox'][2]<w*.59 and b['bbox'][0]<w*.45 and b['bbox'][2]-b['bbox'][0]>w*.18]
        right=[b for b in blocks if b['bbox'][0]>w*.44 and b['bbox'][2]-b['bbox'][0]>w*.18]
        two_col=bool(left and right and (docmeta['key'] in ('L02','L08','G13')))
        if two_col:
            split_y=min(min(b['bbox'][1] for b in left),min(b['bbox'][1] for b in right))
            def order(b):
                x0,y0,x1,y1=b['bbox']
                if x1-x0>w*.63: return (0 if y1<split_y+10 else 3,y0,x0)
                return (1 if (x0+x1)/2<w*.5 else 2,y0,x0)
            blocks.sort(key=order)
        else: blocks.sort(key=lambda b:(round(b['bbox'][1],1),b['bbox'][0]))
        serial=0
        for block in blocks:
            ls=[l for l in block['lines'] if ''.join(s['text'] for s in l['spans']).strip()]
            if not ls: continue
            txt=lines_text(ls);bbox=block['bbox']
            header=(bbox[3]<max(24,h*.035) or bbox[1]>h*.967)
            pure=re.fullmatch(r'[\W\d_]+',txt) is not None
            if header or pure or not re.search(r'[A-Za-z]{2}',txt):
                excluded.append(dict(page=pi+1,text=txt,reason='running margin / non-prose; source preserved in appendix'))
                continue
            groups=[];group=[];words=0
            for line in ls:
                wc=len(lines_text([line]).split())
                if group:
                    gap=line['bbox'][1]-group[-1]['bbox'][3]
                    start=line['bbox'][0]-min(l['bbox'][0] for l in group)
                    prev=lines_text([group[-1]])
                    new_para=gap>5 or (start>7 and prev.endswith(('.',':','?','!')))
                    # Segment only at visible line boundaries; retain exact source crop.
                    at_sentence_end=bool(re.search(r'[.!?][”’\"\')\]0-9]*$',prev))
                    if new_para or (words+wc>200 and at_sentence_end) or words+wc>280 or len(group)>=32:
                        groups.append(group);group=[];words=0
                group.append(line);words+=wc
            if group:groups.append(group)
            for gi,g in enumerate(groups):
                text=lines_text(g)
                if not text:continue
                rect=fitz.Rect(g[0]['bbox'])
                for l in g[1:]:rect|=fitz.Rect(l['bbox'])
                rect=fitz.Rect(max(0,rect.x0-1),max(0,rect.y0-.5),min(w,rect.x1+1),min(h,rect.y1+.5))
                sizes=[s['size'] for l in g for s in l['spans'] if len(s['text'].strip())>2]
                fontsize=sorted(sizes)[len(sizes)//2] if sizes else 10
                serial+=1
                segments.append(dict(id='%s-P%03d-%03d'%(docmeta['key'],pi+1,serial),
                                     page=pi+1,rect=list(rect),en=text,font_size=fontsize,
                                     rotation=original_rotation,continuation=gi>0,
                                     sha256=hashlib.sha256(text.encode()).hexdigest()))
    kept=[]
    for seg in segments:
        ph=doc[seg['page']-1].rect.height
        t=seg['en']
        known_header=(re.match(r'^\d+\s+Mélodie Doumy$',t)
            or re.match(r'^Journal of the Royal Asiatic Society\s+\d+$',t)
            or re.match(r'^\d+\s+Terzi and Whitfield\s+Silk Roads Archaeology and Heritage\s+DOI:',t)
            or re.match(r'^(?:\d+\s+)?K\.\s*Faust\s*/\s*Social Networks',t)
            or re.match(r'^Historical Research in a Digital Age\s+\d+$',t)
            or re.match(r'^\d+\s+Edelstein, Findlen, Ceserani, Winterer, and Coleman$',t)
            or re.match(r'^\d+\s+BUDDHISM AND SILK$',t))
        running=((known_header and seg['rect'][3]<ph*.085)
          or t.startswith('Published online by Cambridge University Press')
          or re.fullmatch(r'(?:The Network Turn\s+\d+|\d+\s+Publishing and Book Culture)',t)
          or re.match(r'^(?:Sir Aurel Stein, Colleagues and Collections\s*\||Papers Relating to Sir Aurel Stein,.*\||\d+\s*\|\s*(?:Ursula Sims-Williams|Wang Jiqing))',t))
        if running:excluded.append(dict(page=seg['page'],text=t,reason='running header/footer; retained in original-page appendix'))
        else:kept.append(seg)
    segments=kept
    for i,seg in enumerate(segments):
        context='文献题名：'+docmeta['title']+'。'
        if docmeta['key']=='L01':context+=' 本文讨论王圆箓（Wang Yuanlu）与敦煌藏经洞。叙述中单用Wang通常指王圆箓；Stein指斯坦因，Pelliot指伯希和。作者及参考文献中的其他Wang须据姓名分别辨识。'
        prev=segments[i-1]['en'][-260:] if i else ''
        nxt=segments[i+1]['en'][:200] if i+1<len(segments) else ''
        seg['context']=context+'\n上文片段（仅供参考）：'+prev+'\n下文片段（仅供参考）：'+nxt
    actual_scope='selected' if scope=='selected' and docmeta['key'] in ('G13','G02') else 'full'
    manifest=dict(**docmeta,source=src.name,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                  original_pages=len(doc),pages=[p+1 for p in pages],scope=actual_scope,
                  segments=segments,excluded=excluded)
    dump(ROOT/(docmeta['key']+'_source.json'),manifest)
    return manifest

def term_present(term,text):
    return re.search(r'(?<![A-Za-z])'+re.escape(term)+r'(?![A-Za-z])',text,re.I) is not None

def build_prompt(text,context=''):
    matches=[(a,b) for a,b in TERMS if term_present(a,text)]
    prompt=''
    if matches:
        prompt='参考下面的翻译：\n'+'\n'.join(a+' 翻译成 '+b for a,b in matches)+'\n\n'
    # One isolated source span per request prevents a translation model from
    # translating an adjacent context paragraph in place of the requested span.
    return (prompt+'将以下文本准确翻译为简体中文，只输出完整译文，不要额外解释或概述。'+
       '保留原有的推测、否定、数字、引注与符号，不更换行为主体。没有通用译名的人名和专名保留原文：\n\n'+text)

def translate(seg):
    if not re.search(r'[A-Za-z]{2}',seg['en']):return dict(id=seg['id'],sha256=seg['sha256'],zh='数式与符号依英文原版保留。',finish='retained notation')
    prompt=build_prompt(seg['en'],seg.get('context',''))
    for attempt in range(3):
        try:
            r=requests.post(ENDPOINT,json=dict(messages=[dict(role='user',content=prompt)],
                temperature=.2 if attempt==0 else .1, top_k=20, top_p=.6,
                repeat_penalty=1.05, max_tokens=max(300,min(1100,int(len(seg['en'])*.65))),
                seed=5419+attempt),timeout=240)
            r.raise_for_status();j=r.json();choice=j['choices'][0]
            zh=choice['message']['content'].strip()
            if choice['finish_reason']=='length' or not zh:raise ValueError('truncated/empty translation')
            years=set(re.findall(r'\b(?:1[0-9]{3}|20[0-9]{2})\b',seg['en']))
            if years-set(re.findall(r'(?:1[0-9]{3}|20[0-9]{2})',zh)) and attempt<2:
                prompt=build_prompt(seg['en'],'文献题名：'+seg['id'].split('-')[0])+('\n4、所有年份和阿拉伯数字必须照录，不得改为汉字或更改。须保留的年份：'+', '.join(sorted(years)))
                continue
            # A translation model occasionally outputs the source for names-only fragments.
            return dict(id=seg['id'],sha256=seg['sha256'],zh=zh,finish=choice['finish_reason'],
                        tokens=j.get('usage',{}),seconds=j.get('timings',{}).get('predicted_ms',0)/1000,
                        engine=Path(j.get('model','unknown')).name,method='isolated-source-v2')
        except Exception:
            if attempt==2:raise
            time.sleep(1+attempt)

def translate_group(group):
    """Translate neighbouring paragraphs together, preserving explicit IDs."""
    if len(group)==1:return [translate(group[0])]
    text='\n\n'.join('[[['+s['id']+']]]\n'+s['en'] for s in group)
    matches=[(a,b) for a,b in TERMS if term_present(a,text)]
    terms='\n'.join(a+' 翻译成 '+b for a,b in matches)
    prompt=('【背景信息】\n'+group[0].get('context','').split('\n上文片段')[0]+
        '\n参考下面的翻译：\n'+terms+'\n\n【待翻译文本】\n'+text+
        '\n\n【翻译任务】\n1、将上述各段忠实翻译为简体中文，不概述、不解释，不更换行为主体，不添加原文没有的事实。'+
        '\n2、必须逐字保留所有[[[段落编号]]]标记，数量与顺序完全不变；每个标记下只写该段对应的译文。不得合并、遗漏或重复段落。'+
        '\n3、保留可能性、否定、全部数字、年份、引注与变量。所有阿拉伯数字照录，不转为汉字。没有通用译名的姓名可保留原文。')
    try:
        r=requests.post(ENDPOINT,json=dict(messages=[dict(role='user',content=prompt)],temperature=.15,
             top_k=20,top_p=.6,repeat_penalty=1.05,max_tokens=2400,seed=5419),timeout=400)
        r.raise_for_status();j=r.json();c=j['choices'][0]
        if c['finish_reason']=='length':raise ValueError('group truncated')
        raw=c['message']['content']
        pattern=r'\[\[\[([A-Z0-9]+-P\d+-\d+)\]\]\]'
        ms=list(re.finditer(pattern,raw))
        if [m.group(1) for m in ms]!=[s['id'] for s in group]:raise ValueError('group IDs changed')
        results=[]
        for i,(seg,match) in enumerate(zip(group,ms)):
            zh=raw[match.end():ms[i+1].start() if i+1<len(ms) else len(raw)].strip()
            if not zh:
                citation_fragment=(len(seg['en'].split())<15 and re.search(r'(?:19|20)\d{2}',seg['en'])
                    and not re.search(r'\b(the|is|was|were|from|in|by|to|a|an|at|may|could|will|for|with)\b',seg['en'],re.I))
                if citation_fragment:
                    zh='（原文引注续行，按原文记为：'+seg['en']+'）'
                else:raise ValueError('empty substantive group member')
            years=set(re.findall(r'\b(?:1[0-9]{3}|20[0-9]{2})\b',seg['en']))
            if years-set(re.findall(r'(?:1[0-9]{3}|20[0-9]{2})',zh)):
                results.append(translate(seg));continue
            results.append(dict(id=seg['id'],sha256=seg['sha256'],zh=zh,finish='stop',
              engine=Path(j.get('model','unknown')).name,group_ids=[s['id'] for s in group]))
        return results
    except Exception as error:
        print('GROUP FALLBACK '+group[0]['id']+': '+str(error)[:180],flush=True)
        return [translate(seg) for seg in group]

class SourceClip(Flowable):
    def __init__(self,seg,placements,maxwidth):
        super().__init__();self.seg=seg;self.placements=placements
        r=fitz.Rect(seg['rect'])
        visual_width,visual_height=(r.height,r.width) if seg.get('rotation',0)%180 else (r.width,r.height)
        scale=min(maxwidth/visual_width,11/max(7,seg['font_size']),1.5)
        self.width=visual_width*scale;self.height=visual_height*scale
    def draw(self):
        c=self.canv
        x,y=c.absolutePosition(0,0)
        self.placements.append(dict(outpage=c.getPageNumber()-1,x=x,y=y,width=self.width,height=self.height,
                                    srcpage=self.seg['page']-1,rect=self.seg['rect'],id=self.seg['id'],
                                    angle=(-self.seg.get('rotation',0))%360))

def styles():
    pdfmetrics.registerFont(TTFont('Bilingual','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
    return dict(
       title=ParagraphStyle('title',fontName='Bilingual',fontSize=19,leading=27,spaceAfter=16,wordWrap='CJK'),
       subtitle=ParagraphStyle('subtitle',fontName='Bilingual',fontSize=13,leading=20,spaceAfter=14,wordWrap='CJK'),
       body=ParagraphStyle('body',fontName='Bilingual',fontSize=10.5,leading=17,spaceAfter=8,wordWrap='CJK'),
       ref=ParagraphStyle('ref',fontName='Bilingual',fontSize=8,leading=11,textColor=colors.HexColor('#506579'),spaceAfter=4,keepWithNext=True,wordWrap='CJK'),
       small=ParagraphStyle('small',fontName='Bilingual',fontSize=8.5,leading=13,spaceAfter=8,wordWrap='CJK'))

def p(text,style):return Paragraph(escape(text).replace('\n','<br/>'),style)

def page_label(key,pn):
    offsets={'L01':820,'L02':55,'G03':156,'G04':399,'L08':7,'G02':-8}
    label='原PDF第%d页'%pn
    if key in offsets:
        label+='（'+('书内' if key=='G02' else '原刊')+'第%d页）'%(pn+offsets[key])
    elif key=='G13':
        if 24<=pn<=29:label+='（章内第%d页）'%(pn-23)
        if 105<=pn<=113:label+='（章内第%d页）'%(pn-104)
    return label

def notation_only(key,text):
    if key!='G03' or re.match(r'^(?:Table|Fig(?:ure)?\.?|Appendix)\b',text,re.I):return False
    letters=re.findall(r'[A-Za-z]{3,}',text)
    chars=max(1,len(re.sub(r'\s','',text)))
    numerical=sum(c.isdigit() for c in text)/chars
    punctuation=sum(not c.isalnum() and not c.isspace() for c in text)/chars
    return len(letters)<4 and (numerical>.12 or punctuation>.25)

def compose(manifest,cache):
    OUTPUT.mkdir(exist_ok=True)
    key=manifest['key'];st=styles();placements=[]
    selected=manifest['scope']=='selected' and key in ('G13','G02')
    suffix='重点章节' if selected else '全文'
    name=Path(manifest['source']).stem+'_'+suffix+'_英中逐段对照.pdf'
    tmp=ROOT/(key+'_layout.pdf');final=OUTPUT/name
    callouts={}
    with fitz.open(INPUT/manifest['source']) as refs:
        if key!='G03':
            perpage={}
            for pn in manifest['pages']:
                found=[]
                for block in refs[pn-1].get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks']:
                    for line in block.get('lines',[]):
                        for span in line.get('spans',[]):
                            if span['flags'] & 1 and re.fullmatch(r'\d{1,3}',span['text'].strip()):
                                found.append(span)
                perpage[pn]=found
            for seg in manifest['segments']:
                r=fitz.Rect(seg['rect']);numbers=[]
                for span in perpage[seg['page']]:
                    b=fitz.Rect(span['bbox']);center=fitz.Point((b.x0+b.x1)/2,(b.y0+b.y1)/2)
                    if r.contains(center) and span['text'].strip() not in numbers:numbers.append(span['text'].strip())
                if numbers:callouts[seg['id']]=numbers
    dump(ROOT/(key+'_callouts.json'),callouts)
    story=[p(manifest['zh'],st['title']),p(manifest['title'],st['subtitle']),
           p(manifest['by'],st['body']),p('英文原文／中文译文 · 辅助阅读译稿',st['subtitle'])]
    if manifest['doi']:story.append(p('DOI: '+manifest['doi'],st['small']))
    page_ranges=[]
    for n in manifest['pages']:
        if not page_ranges or n!=page_ranges[-1][-1]+1:page_ranges.append([n])
        else:page_ranges[-1].append(n)
    pagelabel='、'.join(str(a[0]) if len(a)==1 else '%d–%d'%(a[0],a[-1]) for a in page_ranges)
    story += [p('范围：'+('重点章节' if selected else '所提供PDF全文')+'；原PDF第'+pagelabel+'页。',st['body']),
        p('阅读方法：每组先显示直接取自原PDF的英文段落，再显示中文译文。编号中的P为原PDF页码，不一定等于期刊或书内印刷页码。长段落按原文行界、跨页处接续；脚注、图题和参考文献也按原页编组。',st['body']),
        p('原文核对：英文区域直接嵌入原PDF内容，保留原字形与符号。末尾“原页核对附录”保留本译稿范围内的完整原页，供查阅图片、表格、数式及版面上下文。纯数字、数式、页眉页脚等非叙述材料不另作逐字翻译。',st['body']),
        p('译文说明：使用本机运行的Hy-MT2系列翻译模型，配合项目术语表与上下文生成；已进行版面与对应关系检查，部分重点段落另行校读。此为辅助阅读译稿，未逐句人工审定。引文、数值、人名和含义有歧义的段落应依据所附英文原页核实。',st['body']),
        p('原文件：'+manifest['source'],st['small']),
        p('制作日期：2026-10-27。原始PDF及批注未改动。',st['small']),PageBreak()]
    if selected:
        details=('所选文章：Wang Jiqing（王冀青），Aurel Stein’s Dealings with Wang Yuanlu and Chinese Officials in Dunhuang in 1907（原PDF24–29页）；Ursula Sims-Williams，Aurel Stein’s Correspondence with Paul Pelliot and Lionel Barnett（原PDF105–113页）。'
                 if key=='G13' else '所选章节：第3章 Culture Is Data（文化即数据），印刷43–56页／原PDF51–64页；第4章 Visual Networks（网络的可视化），印刷57–72页／原PDF65–80页。')
        story.insert(-1,p(details,st['small']))
    current=None
    for seg in manifest['segments']:
        if current!=seg['page']:
            if current is not None:story.append(Spacer(1,10))
            current=seg['page']
            story.append(p(page_label(key,current),st['subtitle']))
        story.append(p(seg['id']+'  |  英文原文'+('（原段接续／分段）' if seg['continuation'] else ''),st['ref']))
        story.append(SourceClip(seg,placements,A4[0]-96))
        story.append(Spacer(1,5))
        refnote=('  |  原文注号：'+'、'.join(callouts[seg['id']])) if seg['id'] in callouts else ''
        original_notation=notation_only(key,seg['en'])
        story.append(p(('中文说明（原文编号／符号／数值保留）' if original_notation else '中文译文')+'  |  '+seg['id']+refnote,st['ref']))
        zh=('此处为包含编号、符号、数式、数表或题录的非叙述区块，按原版保留，不依赖文本识别重新转录；请以上方原版及原页核对附录为准，相关解释见相邻中文段落。'
            if original_notation else cache[seg['id']]['zh'])
        if not seg['en'].lstrip().startswith(']'):zh=re.sub(r'^\s*\]+\s*','',zh)
        if seg['id'] in callouts:
            # Separate a plain-text callout from an immediately following year.
            years=set(re.findall(r'\b(?:1[0-9]{3}|20[0-9]{2})\b',seg['en']))
            for note in callouts[seg['id']]:
                for year in years:zh=zh.replace(note+year+'年','〔'+note+'〕'+year+'年')
        for part in zh.split('\n\n'):
            if part.strip():story.append(p(part.strip(),st['body']))
        story.append(Spacer(1,8))
    story += [PageBreak(),p('原页核对附录',st['title']),
              p('以下为原PDF第'+pagelabel+'页。原页依序保留，可核对图像、表格、数学符号、引注及跨栏上下文。',st['body'])]
    def footer(c,d):
        c.setFont('Bilingual',8);c.setFillColor(colors.HexColor('#657489'))
        c.drawString(48,24,key+' · 英中逐段对照 · 辅助阅读译稿')
        c.drawRightString(A4[0]-48,24,str(c.getPageNumber()))
    SimpleDocTemplate(str(tmp),pagesize=A4,rightMargin=48,leftMargin=48,
       topMargin=44,bottomMargin=40,title=manifest['title']+' | English–Chinese reading copy',
       author=manifest['by']).build(story,onFirstPage=footer,onLaterPages=footer)
    layout=fitz.open(tmp);src=fitz.open(INPUT/manifest['source'])
    for source_page in src:
        if source_page.rotation:source_page.set_rotation(0)
    for place in placements:
        page=layout[place['outpage']];height=page.rect.height
        rect=fitz.Rect(place['x'],height-place['y']-place['height'],place['x']+place['width'],height-place['y'])
        try:
            page.show_pdf_page(rect,src,place['srcpage'],clip=fitz.Rect(place['rect']),
                               rotate=place.get('angle',0),overlay=True)
        except Exception as error:
            raise ValueError('English source placement failed: '+json.dumps(place,ensure_ascii=False)+' destination='+str(rect)) from error
    appendix_start=len(layout)+1
    # Append from a separate, untouched document so figure-page rotations and
    # the original page appearance are preserved exactly.
    with fitz.open(INPUT/manifest['source']) as originals:
        for pn in manifest['pages']:layout.insert_pdf(originals,from_page=pn-1,to_page=pn-1,annots=False)
    layout.set_metadata(dict(title=manifest['title']+' — 英中逐段对照',author=manifest['by'],
         subject='辅助阅读译稿；原PDF页码定位；本地模型翻译；英文取自原文件',keywords='Dunhuang; bilingual; English; Chinese; HY5419'))
    toc=[[1,'英中逐段对照',1]]
    for pn in manifest['pages']:
        matched=[x['outpage']+1 for x in placements if x['srcpage']==pn-1]
        if matched:toc.append([2,page_label(key,pn),min(matched)])
    toc.append([1,'原页核对附录',appendix_start])
    for j,pn in enumerate(manifest['pages']):toc.append([2,'原PDF第%d页（完整原页）'%pn,appendix_start+j])
    layout.set_toc(toc)
    staged=ROOT/(key+'_final.tmp.pdf')
    layout.save(staged,garbage=4,deflate=True);layout.close();src.close()
    preserved_annotation_file=None
    if final.exists():
        oldhash_full=hashlib.sha256(final.read_bytes()).hexdigest()
        with fitz.open(final) as old:
            annotation_count=sum(1 for page in old for _ in (page.annots() or []))
        previous_record=ROOT/(key+'_output.json')
        previous=json.loads(previous_record.read_text()) if previous_record.exists() else {}
        external_change=(previous.get('file')==final.name and previous.get('sha256') and previous['sha256']!=oldhash_full)
        if annotation_count or external_change:
            oldhash=oldhash_full[:10]
            saved=OUTPUT/(final.stem+'_保留已有修改_'+oldhash+'.pdf')
            if not saved.exists():shutil.copy2(final,saved)
            preserved_annotation_file=saved.name
    os.replace(staged,final)
    check=fitz.open(final)
    result=dict(file=name,pages=len(check),segments=len(manifest['segments']),english_placements=len(placements),
        source_page_count=len(manifest['pages']),appendix_start=appendix_start,sha256=hashlib.sha256(final.read_bytes()).hexdigest(),
        bytes=final.stat().st_size,source_sha256=manifest['source_sha256'])
    if preserved_annotation_file:result['preserved_annotation_file']=preserved_annotation_file
    assert len(placements)==len(manifest['segments'])
    assert hashlib.sha256((INPUT/manifest['source']).read_bytes()).hexdigest()==manifest['source_sha256']
    dump(ROOT/(key+'_placements.json'),placements)
    dump(ROOT/(key+'_preserved_notation.json'),[s['id'] for s in manifest['segments'] if notation_only(key,s['en'])])
    dump(ROOT/(key+'_output.json'),result)
    check.close();tmp.unlink()
    return result

def run(manifest,workers):
    key=manifest['key'];cp=ROOT/(key+'_translations.jsonl');cache={}
    if cp.exists():
        for line in cp.read_text(encoding='utf-8').splitlines():
            if line.strip():
                r=json.loads(line);cache[r['id']]=r
    valid={s['id']:s['sha256'] for s in manifest['segments']}
    cache={k:v for k,v in cache.items() if valid.get(k)==v['sha256']}
    overrides_path=ROOT/'reviewed_corrections.json'
    overrides=json.loads(overrides_path.read_text(encoding='utf-8')) if overrides_path.exists() else {}
    for seg in manifest['segments']:
        if seg['id'] in overrides:
            cache[seg['id']]=dict(id=seg['id'],sha256=seg['sha256'],zh=overrides[seg['id']],reviewed=True,engine='reviewed correction')
    todo=[s for s in manifest['segments'] if s['id'] not in cache]
    print('%s: %d segments, %d pending'%(key,len(valid),len(todo)),flush=True)
    groups=[];group=[];words=0
    for seg in todo:
        wc=len(seg['en'].split())
        if group and (words+wc>500 or len(group)>=10 or seg['page']!=group[-1]['page']):
            groups.append(group);group=[];words=0
        group.append(seg);words+=wc
    if group:groups.append(group)
    print('%s: %d neighbouring-paragraph groups'%(key,len(groups)),flush=True)
    with cp.open('a',encoding='utf-8') as out, concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        tasks={pool.submit(translate_group,g):g for g in groups}
        done=0;last=time.time()
        for f in concurrent.futures.as_completed(tasks):
            for r in f.result():
                cache[r['id']]=r
                out.write(json.dumps(r,ensure_ascii=False)+'\n');out.flush();done+=1
            if done%20==0 or time.time()-last>40:
                print('%s translated %d/%d'%(key,len(cache),len(valid)),flush=True);last=time.time()
    overrides=json.loads(overrides_path.read_text(encoding='utf-8')) if overrides_path.exists() else {}
    for sid,zh in overrides.items():
        if sid in cache:cache[sid]=dict(cache[sid],zh=zh,reviewed=True)
    audit=[]
    for seg in manifest['segments']:
        zh=cache[seg['id']]['zh'];flags=[]
        ennums=set(re.findall(r'\b\d{2,}\b',seg['en']));zhnums=set(re.findall(r'\d{2,}',zh))
        if ennums-zhnums:flags.append('numeric tokens require source check: '+','.join(sorted(ennums-zhnums)))
        if not re.search(r'[\u3400-\u9fff]',zh):flags.append('no Chinese characters; names/formula or untranslated fragment')
        if re.search(r'(.)\1{15,}',zh):flags.append('repetition')
        if len(zh)>len(seg['en'])*2+250:flags.append('long translation')
        if flags:audit.append(dict(id=seg['id'],page=seg['page'],flags=flags,en=seg['en'],zh=zh))
    dump(ROOT/(key+'_review_flags.json'),audit)
    result=compose(manifest,cache)
    print('PDF READY '+json.dumps(result,ensure_ascii=False),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--keys',default='L01,L02,G03,G04,L08')
    ap.add_argument('--scope',choices=['full','selected'],default='full')
    ap.add_argument('--workers',type=int,default=4);ap.add_argument('--extract-only',action='store_true')
    args=ap.parse_args()
    for key in args.keys.split(','):
        d=next(d for d in DOCS if d['key']==key)
        manifest=extract(d,args.scope)
        print(key,'pages',len(manifest['pages']),'segments',len(manifest['segments']),'words',sum(len(s['en'].split()) for s in manifest['segments']),flush=True)
        if not args.extract_only:run(manifest,args.workers)

if __name__=='__main__':main()
