from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json,re

W=Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/final essay/_修订记录/2026-11-04_第二轮批注修订')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(W/'批注原稿备份.docx') as z:
 root=etree.fromstring(z.read('word/document.xml'))
 ps=root.xpath('//w:body/w:p',namespaces=ns)
 texts=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in ps]
changes={}
changes[3]=texts[3].replace('网页最初服务于课堂成果展示，后来经过多位读者试用，逐渐转向让不熟悉敦煌文献的人也能阅读和查找资料。','建立网页最初是为了展示成果。网页完成后，我邀请多位使用者体验，并根据他们的问题继续修改，才逐渐有了把它作为知识传播平台的想法，希望不熟悉敦煌文献的人也能由此开始了解和查找资料。')
changes[7]=texts[7].replace('我把Excel作为史料阅读与Gephi之间的整理环节。','我先使用Excel整理搜集到的资料。')
changes[8]='整理文献综述思考时，我注意到，斯坦因取得敦煌文献早于伯希和，部分流转活动却更晚为当时国人所知 (潘晟, 2025, pp. 135–136)。这使我不能把现存报告较详细等同于当时消息公开，而需要分别考虑文献何时移动、消息何时传开。对人物关系的梳理，也应关注被早期记述遮蔽的联系。'
changes[14]=texts[14].replace('（Stein，1921：916—917）','(Stein, 1921, pp. 916–917)')
changes[18]=texts[18].replace('秦桦林对','秦桦林 (2018) 对').replace('（秦桦林，2018）','')
changes[22]=texts[22].replace('，通过NUS入口取得部分论文和章节，再与','，再与')
changes[25]=texts[25].replace('潘晟对早期流散史事的考订','潘晟 (2025) 对早期流散史事的考订').replace('（潘晟，2025）','')
changes[27]=texts[27].replace('Terzi与Whitfield区分','Terzi和Whitfield (2024, pp. 56–59) 区分').replace('（2024：56—59）','')
changes[30]='老师建议我用路线地图补充网络展示，我因此开始尝试QGIS。Gephi能够呈现角色和联系，却不能直接表现实际空间与路线顺序。Yihan展示卡伦设置变化的地图时，原来抽象的地域问题变得清晰，也让我考虑自己的文献流转能否获得类似帮助。我希望读者能够直观看到文献在什么时间经过哪些地方，同时与网络中的人物和活动对照。QGIS因此补充了项目原来缺少的空间表达，也让我必须重新检查地点与事件之间的对应。'
changes[35]=texts[35].replace('White强调','White (2010, p. 6) 强调').replace('（2010：6）','')
changes[41]=texts[41].replace('Theibault对','Theibault (2013, p. 174) 对').replace('（2013：174）','')
changes[42]=texts[42].replace('Storying on the Coquille River给了我组织页面的参照。','StoryMaps将地图、图像和文字结合起来的方式，给了我组织网页的启发。')
changes[44]=texts[44].replace('（Wang，1998）','(Wang, 1998)')
changes[53]='我需要用英文在NUS展示，也希望中文读者方便阅读，因此设置了中英文切换。网站在GitHub Pages发布，使用平台提供的网址，没有另购域名。另购域名、配置托管和维护环境，会增加这个学生项目的费用与操作负担，我也难以独立处理。把源码与发布版本放在一起，便于我按反馈修改。家人最初在国内打不开网站，调整资源加载和发布方式后，才反馈网页、地图与网络均能打开；其他网络环境下的访问情况仍需继续关注。'
changes[54]='我已经把网站分享到课程讨论平台，希望交流能够在课堂展示之后继续。此前的试用意见已经促使我调整字号、布局和箭头，也带来了增加保存现状的建议。保留讨论区，是为了让后来的读者仍能提出问题、补充线索，并看到彼此的看法。涉及历史事实的建议，我会再核对出处后决定是否修改数据；日常维护也需要注意公开发言与个人信息的边界。'
changes[55]='作为知识入口的网站'
changes[56]='我的资料来源有限，因此将网站定位为初步了解敦煌文献、连接相关资料的平台。现有内容涉及部分人物关系、路线与馆藏案例，不能代替完整的流转史。许多路线仍以批次为单位，个别交接和日期尚未落实。我希望读者先获得大致认识，再沿着出处查阅论文、原始记述和馆方资料。'
changes[57]='后续我会先核对关键通信和交接的原件影像，补充批次与具体写本的对应，检查资料链接是否仍可使用。新资料若改变判断，就需要同步更新表格、网络和地图并保留修改记录。我希望先让现有内容便于核对，再逐步扩充人物与收藏。'
changes[59]='回看这个项目，我起初只是希望用Gephi把人物关系画出来，后来才发现，画图之前需要花很多时间读资料、整理表格和辨认事件。加入地图、制作网页和听取使用者意见，又让我开始考虑怎样把这些材料讲给没有读过相关文献的人。现在的网站还只是一个起点，但它让我把本学期学到的工具实际用在了自己关心的问题上。我希望读者看过以后，除了知道文献去了哪里，也会对经手、整理和研究这些文献的人产生兴趣，并愿意继续查阅相关资料。'

# APA 7 reference entries. Keep Chinese source names and titles in their original script.
# Italic spans are explicitly marked for native Word formatting by the builder.
refs={
61:[('Stein, M. A. (1921). ',False),('Serindia',True),(' (Vol. 2). Clarendon Press.',False)],
62:[('Terzi, P., & Whitfield, S. (2024). Reconstructing a medieval library? The contents of the manuscript bundles in the Dunhuang Library Cave. ',False),('Silk Roads Archaeology and Heritage, 1',True),('(1), 56–76. https://doi.org/10.5334/srah.8',False)],
63:[('Theibault, J. (2013). Visualizations and historical arguments. In K. Nawrotzki & J. Dougherty (Eds.), ',False),('Writing history in the digital age',True),(' (pp. 173–185). University of Michigan Press.',False)],
64:[('Wang, H. (1998). Stein’s recording angel—Miss F. M. G. Lorimer. ',False),('Journal of the Royal Asiatic Society, 8',True),('(2), 207–228. https://doi.org/10.1017/S1356186300009986',False)],
65:[('White, R. (2010, February 1). ',False),('What is spatial history?',True),(' [Working paper]. Stanford University Spatial History Lab. https://web.stanford.edu/group/spatialhistory/static/publications/pub29.html',False)],
66:[('潘晟. (2025). 时代的遮蔽：敦煌文献早期流散过程中部分史事杂考. ',False),('浙江学刊',True),(', (2), 134–143.',False)],
67:[('秦桦林. (2018). 1909年北京学界公宴伯希和事件补考——兼论王国维与早期敦煌学. ',False),('浙江大学学报（人文社会科学版）, 48',True),('(3), 44–56. https://doi.org/10.3785/j.issn.1008-942X.CN33-6000/C.2018.02.051',False)],
70:[('Wang, X. (2026). ',False),('Dunhuang, in Motion',True),(' [项目网站]. https://3380903218-cmd.github.io/dunhuang-in-motion/',False)]
}
for i,runs in refs.items():changes[i]=''.join(t for t,it in runs)
remove=[71]
headings={4,11,21,29,39,49,55}
captions={15,16,17,32,33,34}
body=''.join(changes.get(i,t) for i,t in enumerate(texts[:60]) if i>=2 and i not in headings|captions)
main=''.join(changes.get(i,t) for i,t in enumerate(texts[:60]) if i>=2)
def count(t): return len(re.findall(r'[\u3400-\u9fff]',t))+len(re.findall(r'[A-Za-z]+(?:[\-’\'][A-Za-z]+)*',t))+len(re.findall(r'\d+(?:[.\-—–]\d+)*',t))
obj={'changes':changes,'reference_runs':refs,'remove':remove,'body_count':count(body),'main_count_including_headings_captions_sources':count(main),'body_han_count':len(re.findall(r'[\u3400-\u9fff]',body))}
(W/'revisions.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2))
(W/'修订稿正文.txt').write_text('\n\n'.join(changes.get(i,t) for i,t in enumerate(texts) if i not in remove))
print(json.dumps({k:v for k,v in obj.items() if k not in ['changes','reference_runs','remove']},ensure_ascii=False))
