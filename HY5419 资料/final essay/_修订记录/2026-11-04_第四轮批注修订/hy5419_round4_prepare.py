from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json,re

BASE=Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/final essay')
W=BASE/'_修订记录/2026-11-04_第四轮批注修订'
PREV=BASE/'_修订记录/2026-11-04_第三轮批注修订'
cfg=json.loads((PREV/'revisions.json').read_text())
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(W/'批注原稿备份.docx') as z:
    root=etree.fromstring(z.read('word/document.xml'))
    texts=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in root.xpath('//w:body/w:p',namespaces=ns)]
assert len(texts)==71
cfg['changes']['57']='接下来，我会继续核对关键书信和交接记录，补充文献批次与具体写本的对应，并把新查到的内容更新到表格、地图和网络中。我也想请更多读者试用网站，看看他们能否找到路线的出处、看懂人物之间的关系，再根据他们遇到的问题调整页面。我希望先把现有内容讲清楚、让出处容易查找，再逐步增加人物和馆藏资料。'
cfg['remove']=[58]
headings={4,11,21,29,39,49,55};captions={15,16,17,32,33,34}
body=''.join(cfg['changes'].get(str(i),t) for i,t in enumerate(texts[:60]) if i>=2 and i not in headings|captions and i not in cfg['remove'])+cfg['inserts'][0]['text']
main=''.join(cfg['changes'].get(str(i),t) for i,t in enumerate(texts[:60]) if i>=2 and i not in cfg['remove'])+cfg['inserts'][0]['text']
def count(t):return len(re.findall(r'[\u3400-\u9fff]',t))+len(re.findall(r'[A-Za-z]+(?:[\-’\'][A-Za-z]+)*',t))+len(re.findall(r'\d+(?:[.\-—–]\d+)*',t))
cfg['body_count']=count(body);cfg['body_han_count']=len(re.findall(r'[\u3400-\u9fff]',body));cfg['main_count_including_headings_captions_sources']=count(main)
assert 6500<=cfg['body_count']<=7000
(W/'revisions.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2))
actions=json.loads((PREV/'批注处理.json').read_text())
for a in actions:a['round4_action']='Reapplied because current user-annotated original still contains the previous wording; latest comments do not revoke these corrections.'
actions.append({'comment_id':'5','status':'applied','action':'将两段后续工作合为一段，保留资料核对、数据同步与读者试用三项实际工作，删去重复的“后续”和抽象的功能检查说明。','paragraphs':[57,58]})
(W/'批注处理.json').write_text(json.dumps(actions,ensure_ascii=False,indent=2))
for name in ['新增IDP来源记录.json']:(W/name).write_bytes((PREV/name).read_bytes())
script=(PREV/'hy5419_round3_build.py').read_text()
script=script.replace('2026-11-04_第三轮批注修订','2026-11-04_第四轮批注修订')
script=script.replace('ac1931155845d6d7945f9248af46d9d2ceb9642be654ec552ddb70b0b0000748','5968476e9236133793bca2adc1f5dc205fdd604d07b014ccc0dbd8513a5c2ef1')
script=script.replace("    # Keep the large second figure intact.","    for i in cfg['remove']:\n        ps[i].getparent().remove(ps[i])\n        changelog.append({'original_paragraph':i,'old':original[i],'new':None,'reason':'Merged future-work content into original paragraph 57, as requested by comment 5.'})\n    # Keep the large second figure intact.")
script=script.replace('order=list(range(len(original)))','order=[i for i in range(len(original)) if i not in cfg[\'remove\']]')
script=script.replace('assert len(result)==73','assert len(result)==72')
script=script.replace("[i+2],method='c14n'","[i+1],method='c14n'")
script=script.replace("'comments_addressed':5","'comments_addressed':6,'new_comments_addressed':1,'prior_corrections_reapplied':5,'merged_original_paragraphs':[57,58]")
(W/'hy5419_round4_build.py').write_text(script)
print(json.dumps({'body_count':cfg['body_count'],'main_count':cfg['main_count_including_headings_captions_sources'],'new_paragraph':cfg['changes']['57']},ensure_ascii=False))
