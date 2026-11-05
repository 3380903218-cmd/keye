# -*- coding: utf-8 -*-
"""Apply bounded review edits to the original OOXML package, preserving its parts."""
from pathlib import Path
from copy import deepcopy
from lxml import etree as ET
import hashlib,json,re,zipfile,os,uuid

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
TARGET=ROOT/'HY5419_敦煌项目_8分钟展演稿_中英对照.docx'
BACKUP=HERE/'批注原稿备份.docx'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(TARGET)==sha(BACKUP)==json.loads((HERE/'baseline.json').read_text())['sha256']
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W14='http://schemas.microsoft.com/office/word/2010/wordml'
W15='http://schemas.microsoft.com/office/word/2012/wordml'
ns={'w':W,'w14':W14,'w15':W15}
q=lambda t:'{'+W+'}'+t
with zipfile.ZipFile(BACKUP) as z:
    infos=z.infolist();parts={i.filename:z.read(i.filename) for i in infos}
doc=ET.fromstring(parts['word/document.xml'])
original_doc=deepcopy(doc)
body=doc.find('w:body',ns);paragraphs=body.findall('w:p',ns)
changes=[];touched=set()
visible=lambda p:''.join(p.xpath('.//w:t/text()',namespaces=ns))

def find(text,scope=None):
    hits=[p for p in (scope if scope is not None else body.findall('w:p',ns)) if text in visible(p)]
    assert len(hits)==1,(text,len(hits));return hits[0]

def replace(p,old,new,reason):
    # Only change w:t. All runs, properties, anchors, fields and relationships survive.
    texts=p.findall('.//w:t',ns);flat=''.join(t.text or '' for t in texts)
    assert flat.count(old)==1,(old,flat)
    start=flat.index(old);end=start+len(old);offset=0;inserted=False
    for t in texts:
        value=t.text or '';a=offset;b=a+len(value);offset=b
        if b<=start or a>=end:continue
        before=value[:max(0,start-a)];after=value[max(0,end-a):] if end<b else ''
        t.text=before+(new if not inserted else '')+after;inserted=True
        if t.text and (t.text[0].isspace() or t.text[-1].isspace()):t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    assert inserted and visible(p)==flat.replace(old,new,1)
    changes.append({'reason':reason,'old':old,'new':new});touched.add(p)

def clone_plain(template,text):
    assert not template.findall('.//w:hyperlink',ns) and not template.findall('.//w:commentRangeStart',ns)
    p=deepcopy(template)
    for k in ['paraId','textId']:
        if p.get('{'+W14+'}'+k) is not None:p.set('{'+W14+'}'+k,uuid.uuid4().hex[:8].upper())
    ts=p.findall('.//w:t',ns);assert ts
    ts[0].text=text
    for t in ts[1:]:t.text=''
    return p

# Comment 0: author's factual correction about the first digital tool tried.
old='The Gephi network is the part I find most useful.'
new='Gephi was the first tool I tried for this project. Its network is the part I find most useful.'
replace(find(old),old,new,'批注0：最先尝试Gephi；英文同步')
old='Gephi网络是我觉得最有用的部分。'
new='Gephi是我在这个项目中最先尝试的工具，它的网络也是我觉得最有用的部分。'
replace(find(old),old,new,'批注0：保留已有作用说明，补充工具尝试顺序')

# Comment 1 selected the AI-assistance clause, not the whole data paragraph.
replace(find('To build this, I used the literature'),', with AI assistance.','.','批注1：按圈选范围删去英文对应短语')
replace(find('在制作过程中，我依据文献'),'，并使用AI协助整理','','批注1：删去圈选短语，保留表格与证据处理说明')
old='操作提示｜停在当前关系实例上即可。这里强调你的研究选择与判断，不演示代码或长篇解释AI工具。'
new='操作提示｜先停在关系实例上。若进度提前，可用10—15秒简示Excel，再返回网页讲AI分工；文件和工作表见第一页。时间紧则略过Excel，不演示代码。'
replace(find(old),old,new,'批注1：加入有余时间时的Excel操作')
replace(find('3:25–4:25  说明资料工作与AI的分工'),'说明资料工作与AI的分工','资料记录与AI分工（Excel可选）','与可选操作同步标题')

# The first-page table contains the same timing plan.
table_ps=body.findall('.//w:tbl//w:p',ns)
replace(find('资料整理与AI分工',table_ps),'资料整理与AI分工','资料记录与AI分工','时间表与正文同步')
replace(find('停在关系实例；说明数据整理、skills与个人判断',table_ps),'停在关系实例；说明数据整理、skills与个人判断','有余时简示Excel；随后说明skills与个人判断','时间表加入可选Excel')
replace(find('时间紧时先省略原图切换和第二个通信例子。'),'时间紧时先省略原图切换和第二个通信例子。','时间紧时先省略Excel、原图切换和第二个通信例子。','保证五分钟主讲，优先省略可选操作')

bullet_template=find('问答准备了8题供选用')
optional='有余时简示Excel：打开“文献/文献综述/Gephi传播网络_可直接使用.xlsx”的“08_Gephi_Edges”，展示Source、Target、Relation、SourceIds。此表为较早版本，只示字段结构，不与当前网页总数作一一对应。'
extra=clone_plain(bullet_template,optional);body.insert(body.index(bullet_template),extra)
note_template=find('演示备忘｜最后一句只指向网页已有的通信实例')
en=clone_plain(note_template,'Excel可选口述（不计入主稿）｜This spreadsheet shows how I recorded each relationship and linked it to its source.')
zh=clone_plain(note_template,'中文参考｜这张表展示了我怎样记录每项关系，并把它与资料来源联系起来。')
body.insert(body.index(extra)+1,en);body.insert(body.index(en)+1,zh)

# Comment 2: StoryMaps as the inspiration and a reader-facing sharing/discussion purpose.
old='The website brings the map and network together, and links them to present-day collections and further reading. Visitors can follow a route, examine a relationship, and check the evidence behind it. My main result is a way to read the movement of manuscripts together with the people and scholarly work around them. Thank you. I welcome your questions.'
new='Learning about StoryMaps inspired me to bring these results together on a website. Visitors can explore the routes and relationships, consult the sources and share the link. I want it to be a platform for discussion and feedback as well, so I can keep improving it. Thank you. I welcome your questions.'
replace(find(old),old,new,'批注2：StoryMaps启发及查阅、分享、反馈的平台价值；不虚构站内留言功能')
old='网页把地图与网络放在一起，并连接到今日馆藏与继续阅读的资料。使用者可以沿着路线阅读，查看一项人物关系，再核对它的依据。我的主要成果，是提供一种把文献流转、相关人物及其学术工作放在一起阅读的方式。谢谢大家，欢迎提问。'
new='这个网站的想法来自我对StoryMaps的学习。我希望把这些成果放在一起，让大家沿路线阅读、查看人物关系、查阅资料并分享链接。它也可以成为交流和反馈的平台，让我根据读者意见继续完善。谢谢大家，欢迎提问。'
replace(find(old),old,new,'批注2：中文与英文同步')
old='Together, the map and network connect manuscript journeys with the people who studied them. The website also lets readers check the sources. Thank you. I welcome your questions.'
new='Inspired by StoryMaps, I built a website for exploring the routes and relationships, consulting sources and sharing the project. I hope readers’ feedback will help me improve it. Thank you.'
replace(find(old),old,new,'批注2：同步超时备用收尾')
old='地图与网络把文献流转与研究这些材料的人联系起来，网页也让读者能够核对来源。谢谢大家，欢迎提问。'
new='学习StoryMaps启发我制作这个网站，让大家查看路线和人物关系、查阅资料并分享项目。我希望读者的反馈能帮助我继续改进。谢谢大家。'
replace(find(old),old,new,'批注2：同步备用收尾中文')

# Apply the same emphasis where the script prepares the likely "main result" question.
old='For me, it is the connection between a readable story and a checkable network. Readers can see how collectors, Chinese scholars and library workers performed different tasks, then inspect the evidence. I am presenting relationships drawn from scholarship, rather than claiming to discover all these contacts for the first time.'
new='For me, it is a website inspired by StoryMaps that connects a readable story with a checkable network. Readers can follow the routes and relationships, consult the sources and share the project. Their feedback helps me improve the presentation. The historical relationships come from the literature I have studied.'
replace(find(old),old,new,'批注2：同步问答中最突出成果的表述')
old='对我来说，是把可阅读的叙述和可核对的网络联系起来。读者能看到收藏者、中国学者和图书馆工作人员承担了不同工作，再查看依据。我是在已有研究基础上整理和呈现这些联系，而不是声称首次发现了所有交往。'
new='对我来说，是在StoryMaps启发下，把可阅读的叙述和可核对的网络放在一个网站中。读者能沿路线和人物关系阅读、查阅资料并分享项目，他们的反馈也帮助我改进呈现。历史关系则来自我阅读和整理的文献。'
replace(find(old),old,new,'批注2：同步问答中文')

# Recount only the main English speech, excluding optional wording and prepared Q&A.
main_start=paragraphs.index(find('EN  My project is called'))
main_end=paragraphs.index(find('若接近5分钟'))
spoken=[]
for p in paragraphs[main_start:main_end]:
    st=p.find('w:pPr/w:pStyle',ns)
    if st is not None and st.get(q('val'))=='ScriptEN':spoken.append(visible(p).removeprefix('EN  '))
words=sum(len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b",s)) for s in spoken)
old_count=find('英文主讲正文约486词。')
old=visible(old_count)
new=f'英文主讲正文约{words}词。按每分钟110—120词，口述约{words/120:.1f}—{words/110:.1f}分钟，再预留约30—45秒网页操作。Excel为可选，不计入上述词数；以实际排练为准，控制在5分钟内。'
replace(old_count,old,new,'重新核算英文正文词数，区分可选Excel口述')

# Preserve the three review threads and their anchors, and mark them as addressed.
extended=ET.fromstring(parts['word/commentsExtended.xml'])
assert len(extended)==3
for c in extended:c.set('{'+W15+'}done','1')
parts['word/commentsExtended.xml']=ET.tostring(extended,encoding='UTF-8',xml_declaration=True,standalone=True)
parts['word/document.xml']=ET.tostring(doc,encoding='UTF-8',xml_declaration=True,standalone=True)

# Untouched paragraphs and rich content are byte/semantic identical.
before_ps=original_doc.find('w:body',ns).findall('w:p',ns)
for old,p in zip(before_ps,paragraphs):
    if p not in touched:assert ET.tostring(old)==ET.tostring(p)
    else:
        old_rpr=[ET.tostring(x) for x in old.findall('.//w:rPr',ns)]
        new_rpr=[ET.tostring(x) for x in p.findall('.//w:rPr',ns)]
        assert old_rpr==new_rpr,'Run formatting changed'
for tag in ['hyperlink','fldChar','instrText','sectPr','tbl','commentRangeStart','commentRangeEnd','commentReference']:
    assert len(doc.findall('.//w:'+tag,ns))==len(original_doc.findall('.//w:'+tag,ns)),tag
assert not doc.findall('.//w:ins',ns) and not doc.findall('.//w:del',ns)
assert len(doc.xpath('.//w:commentRangeStart',namespaces=ns))==3
ids=doc.xpath('.//w:p/@w14:paraId',namespaces=ns);assert len(ids)==len(set(ids))

temp=HERE/'修改候选.docx'
with zipfile.ZipFile(temp,'w') as z:
    for info in infos:z.writestr(info,parts[info.filename])
assert sha(TARGET)==sha(BACKUP),'The original changed during editing; do not overwrite newer user edits.'
os.replace(temp,TARGET)
report={'baseline_sha256':sha(BACKUP),'output_sha256':sha(TARGET),'original_path':str(TARGET),'english_spoken_words':words,'main_english_paragraphs':len(spoken),'comments_accepted':3,'comments_unresolved':0,'comment_threads_retained':True,'comments_marked_resolved':3,'changed_zip_parts':['word/document.xml','word/commentsExtended.xml'],'untouched_part_bytes_preserved':True,'run_formatting_preserved':True,'rich_element_counts_preserved':True,'changes':changes}
(HERE/'逐项修改记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='changes'},ensure_ascii=False,indent=2))
