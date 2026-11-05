from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json,re

W=Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/final essay/_修订记录/2026-11-04_第三轮批注修订')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(W/'批注原稿备份.docx') as z:
    root=etree.fromstring(z.read('word/document.xml'))
    ps=root.xpath('//w:body/w:p',namespaces=ns)
    texts=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in ps]
assert len(texts)==71
changes={
2:texts[2].replace('我没有试图复原所有敦煌文献的去向，而是从有来源支持的活动入手，整理人物、文献与机构之间的联系。','我围绕文献的流转和研究活动，整理人物、文献与机构之间的联系。'),
30:'整理网络时，我发现它能说明谁参与了流转，却很难直观呈现文献何时经过哪些地方。老师补充路线地图的建议，以及Yihan展示卡伦设置变化的地图，也让我进一步考虑空间表达的作用。我选择QGIS，是因为它可以分层组织地点与路线，把表格中的地名、坐标和事件对应起来。地图说明流转的时间和地点顺序，人物网络则解释由谁经手、发生了什么。两者配合，可以更清楚地呈现传播过程，也促使我重新检查地点与事件的对应。',
40:texts[40].replace('制作网页最直接的初衷，是把分散的Gephi、QGIS和表格成果放在一起，让老师和同学不必打开多种软件也能查看。',''),
53:texts[53].replace('我需要用英文在NUS展示，也希望中文读者方便阅读，因此设置了中英文切换。','我采用中英双语，希望扩大使用人群，让不同语言背景的读者都能在这里学习、分享敦煌文献知识。')
}
for i,new in changes.items():assert new!=texts[i]
idp='敦煌文献已有较成熟的数字资源。国际敦煌项目（IDP）汇集合作机构的文献图像、相关资料与学习资源，便于查阅分藏各地的收藏 (International Dunhuang Programme, n.d.)。这些资源为我的项目提供了基础，也帮助我把重点放在选定时期的人物、活动与路线的联系上。'
ref_runs=[('International Dunhuang Programme. (n.d.). ',False),('About',True),('. https://idp.bl.uk/about/',False)]
inserts=[{'after':21,'text':idp,'template':22,'kind':'body'},
         {'after':60,'text':''.join(t for t,i in ref_runs),'template':61,'kind':'reference','runs':ref_runs}]
headings={4,11,21,29,39,49,55}
captions={15,16,17,32,33,34}
body=''.join(changes.get(i,t) for i,t in enumerate(texts[:60]) if i>=2 and i not in headings|captions)+idp
main=''.join(changes.get(i,t) for i,t in enumerate(texts[:60]) if i>=2)+idp
def count(t):return len(re.findall(r'[\u3400-\u9fff]',t))+len(re.findall(r'[A-Za-z]+(?:[\-’\'][A-Za-z]+)*',t))+len(re.findall(r'\d+(?:[.\-—–]\d+)*',t))
cfg={'changes':changes,'inserts':inserts,'body_count':count(body),'body_han_count':len(re.findall(r'[\u3400-\u9fff]',body)),'main_count_including_headings_captions_sources':count(main)}
assert 6500<=cfg['body_count']<=7000
(W/'revisions.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2))
actions=[
{'comment_id':'0','status':'applied','action':'将开篇最后一句改为围绕文献流转和研究活动整理联系，删去刻意的“有来源支持”及多余限定。','paragraph':2},
{'comment_id':'1','status':'applied','action':'在资料选择一节补充IDP汇集分藏文献数字资源的基础，并说明本项目如何组织选定时期的关系与路线；依据IDP官网新增APA参考文献。','insert_after':21,'source':'https://idp.bl.uk/about/'},
{'comment_id':'2','status':'applied','action':'以网络不能直观显示空间和经过顺序的问题引出QGIS，说明分层组织地名、路线、事件及与人物网络互补的理由；保留老师和Yihan的启发。','paragraph':30},
{'comment_id':'3','status':'applied','action':'删除网页设计一节重复陈述初衷的首句，保留导论中的一次说明。','paragraph':40},
{'comment_id':'4','status':'applied','action':'将双语功能的目的改为扩大使用人群、方便不同语言读者学习和分享；保留其余发布与访问经历。','paragraph':53}]
(W/'批注处理.json').write_text(json.dumps(actions,ensure_ascii=False,indent=2))
source={'url':'https://idp.bl.uk/about/','title':'About','author':'International Dunhuang Programme','date':'n.d.','accessed':'2026-11-04','verified_claims':['Official platform provides images, information, and learning resources about manuscripts and other Eastern Silk Road materials.','Partner institutions link collections and share data, images, and expertise.'],'used_for':'Added context paragraph in source selection section; no numerical or comprehensive-coverage claim made.'}
(W/'新增IDP来源记录.json').write_text(json.dumps(source,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in cfg.items() if k not in {'changes','inserts'}},ensure_ascii=False))
