# -*- coding: utf-8 -*-
"""Build the public exhibition snapshot; never modify research workbooks."""
from pathlib import Path
import csv, hashlib, json

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
INPUT = PROJECT / '路线地图' / '地图导入数据'
def read(name):
    return list(csv.DictReader((INPUT/name).open(encoding='utf-8-sig')))
def pair(zh,en): return {'zh':zh,'en':en}

places=[]
for r in read('地点_默认参考点.csv'):
    places.append(dict(id=r['PlaceId'],name=pair(r['LabelZH'].split('（')[0],r['Label'].split(' (')[0]),lon=float(r['Longitude']),lat=float(r['Latitude']),precision=pair(r['Precision'],'City / site reference; historical location uncertainty is unquantified.'),note=pair(r['Note'],'A geographical reference, not an identified historical building or handover room.'),source=r['SourceURL']))

en_notes=[
    'Twelve cases were subsequently stored in Anxi. Anxi is represented by a modern regional reference point.',
    'Transport by Ibrahim and Hassan. The cargo arrival date must not be inferred from Jiang Xiaowan’s return on 5 October.',
    'Hongliuyuan, Xingxingxia and Kushui are documented, but their precise historical locations are not plotted.',
    'These regions are documented along the caravan journey. Individual stop dates are unknown.',
    'These regions are documented along the caravan journey. Individual stop dates are unknown.',
    'These regions are documented along the caravan journey. Individual stop dates are unknown.',
    'These regions are documented along the caravan journey. Individual stop dates are unknown.',
    'These regions are documented along the caravan journey. Individual stop dates are unknown.',
    'The source describes the Khotan riverbed. Stein’s own Keriya River itinerary is not the cargo’s itinerary.',
    'Overview link only. Intermediate places are mentioned in the source; ports and the complete transport geometry remain unverified.',
    'Collection-level overview; not an extra shipment. It does not imply that the whole collection passed through Beijing.',
    'The expedition’s main cargo included Dunhuang and other materials. The separately retained manuscripts are not merged into this route.',
    'Main-cargo itinerary; individual manuscript identities and arrival dates at each stop are not matched.',
    'Main-cargo itinerary; individual manuscript identities and arrival dates at each stop are not matched.',
    'Rail transport under Vaillant and Nouette is documented. This curve does not reconstruct railway tracks or stations.',
    'Nouette escorted the main cargo, which arrived in Paris on 16 January 1909. Sea ports and the onward railway are not reconstructed.'
]
date_en=[
    '12–15 June 1907','2–4 October 1907','8–18 October 1907',
    '1 Nov 1907–19 Jan 1908; stop date unknown','1 Nov 1907–19 Jan 1908; stop date unknown','1 Nov 1907–19 Jan 1908; stop date unknown','1 Nov 1907–19 Jan 1908; stop date unknown','1 Nov 1907–19 Jan 1908; stop date unknown',
    'Dispatched 25 Jan 1908; arrived before 26 Mar','Dispatched 1 Aug 1908; London Jan 1909',
    'Acquired 1908; Paris arrival and institutional accession are separate',
    'Main cargo in 1908; individual stop date unknown','Main cargo in 1908; individual stop date unknown','Main cargo in 1908; individual stop date unknown',
    '1908; stored in Shanghai before 1 Dec','Main cargo arrived Paris 16 Jan 1909'
]
flows=[]
for i,r in enumerate(read('实物流转_示意线.csv')):
    n=i+1
    # SG011 repeats the same Pelliot process at another scale. Keep its record
    # for provenance, but never play it as an additional movement.
    flows.append(dict(id=r['MapSegmentId'],fromId=r['FromReferencePlaceId'],toId=r['ToReferencePlaceId'],route=r['RouteGroup'].lower(),layer='material',stage=1 if n<=3 else (3 if n in [10,11,16] else 2),visible=n!=11,date=pair(r['时间证据'],date_en[i]),note=pair(r['说明'],en_notes[i]),eventIds=r['关联EventId'].split(';'),claimIds=r['ClaimId'].split(';'),source=r['SourceURL'],sourceId=r['SourceId'],scope=r['MapScale'],geometry='schematic_flow',evidence=pair('研究文献／机构叙述','Research / institutional narrative')))
for i,r in enumerate(read('知识传播_示意线.csv')):
    flows.append(dict(id=r['MapSegmentId'],fromId=r['FromReferencePlaceId'],toId=r['ToReferencePlaceId'],route='stein' if i==0 else 'qing',layer='knowledge',stage=1 if i==0 else 3,visible=True,date=pair(r['时间证据'],'26 Sep 1907; inferred from horse-hire accounts' if i==0 else 'Telegram dispatched 5 Oct 1909; receipt time unknown'),note=pair(r['说明'],'Purchase proposal sent by an unnamed messenger. Dating is inferred, not a surviving dated letter.' if i==0 else 'An administrative telegram from Beijing to Lanzhou, not an object shipment or a reconstructed cable route.'),eventIds=r['关联EventId'].split(';'),claimIds=r['ClaimId'].split(';'),source=r['SourceURL'],sourceId=r['SourceId'],scope=r['MapScale'],geometry='schematic_flow',evidence=pair('研究者推定日期' if i==0 else '研究文献所引电报','Inferred date' if i==0 else 'Telegram cited in research')))
flows.append(dict(id='WEB_QING_1910',fromId='PL_MOGAO',toId='PL_BEIJING',route='qing',layer='material',stage=4,visible=True,date=pair('1910年；中途交接与主批接收日待核','1910; intermediate handovers and main-batch receipt date unresolved'),note=pair('仅表达敦煌遗书运京的总览关系。中途押运节点尚未闭合，不绘制经兰州等具体路径；续交22卷另有记录，不能与主批混算。','Overview of the transfer to Beijing. Intermediate custody stages remain incomplete. The supplementary 22 scrolls are a separate recorded batch.'),eventIds=['DH008','DH009'],claimIds=[],source='https://www.nlc.cn/upload/attachments/2023-01-31/7f8581ea.pdf',sourceId='WEB_NLC;S19',scope='global_aggregate',geometry='schematic_flow',evidence=pair('国图机构文章＋项目既有研究记录','NLC institutional account + existing project research')))

sources=[
 dict(id='R01',title=pair('王冀青（2015）：斯坦因在安西所获敦煌写本之外流过程研究','Wang Jiqing (2015): the dispersal of Stein’s Anxi acquisitions'),url=flows[0]['source'],type=pair('学术机构转载','Academic institutional republication')),
 dict(id='R02',title=pair('吉美博物馆：伯希和考察队的返程','Musée Guimet: the expedition’s return journey'),url='https://guimet-photo-pelliot.fr/essais/essai_11.php',type=pair('博物馆专题研究','Museum research essay')),
 dict(id='R04',title=pair('秦桦林（2018）：1909年北京学界公宴伯希和事件补考','Qin Hualin (2018): the 1909 Beijing banquet for Pelliot'),url='https://www.zjujournals.com/soc/CN/abstract/abstract11967.shtml',type=pair('研究论文','Research article')),
 dict(id='NLC',title=pair('国家图书馆：敦煌文献数字化与国际敦煌学项目','NLC: Dunhuang digitisation and the International Dunhuang Project'),url='https://www.nlc.cn/upload/attachments/2023-01-31/7f8581ea.pdf',type=pair('机构资料','Institutional account')),
 dict(id='BNF',title=pair('法国国家图书馆：亚洲与大洋洲写本馆藏','BnF: Asian and Oceanian manuscript collections'),url='https://www.bnf.fr/fr/manuscrits-du-monde-asie-oceanie',type=pair('机构馆藏说明','Institutional collection guide')),
 dict(id='IDP',title=pair('IDP：《金刚经》Or.8210/P.2馆藏记录','IDP: Diamond Sutra, Or.8210/P.2'),url='https://idp.bl.uk/collection/51FDAEAFB4A24E2E9981692A98130BC8/',type=pair('藏品目录','Object catalogue')),
 dict(id='BM',title=pair('英国博物馆：1919,0101,0.1馆藏记录','British Museum: collection record 1919,0101,0.1'),url='https://www.britishmuseum.org/collection/object/A_1919-0101-0-1',type=pair('藏品目录；检索索引可读，正文访问受限','Object catalogue; indexed description, page access restricted')),
 dict(id='GUIMET',title=pair('吉美博物馆：馆藏问答与五佛曼荼罗','Musée Guimet: collections FAQ and Mandala of the Five Jina'),url='https://www.guimet.fr/fr/faq-sur-nos-collections',type=pair('机构馆藏说明','Institutional collection guide')),
 dict(id='NLC2025',title=pair('国家古籍保护中心（2025）：国图敦煌文献彩版图录','National Center for Preservation (2025): NLC Dunhuang catalogues'),url='https://www.nlc.cn/pcab/zx/xw/20250423_2644574.shtml',type=pair('机构出版与整理说明','Institutional catalogue / conservation account'))
]

institutions=[
 dict(id='bl',city='PL_LONDON',short='BL',name=pair('大英图书馆','British Library'),kind=pair('图书馆 · 写本与印本','Library · manuscripts & prints'),route='stein',collection=pair('斯坦因收藏中的敦煌写本与印本','Dunhuang manuscripts and prints in the Stein collection'),example=pair('示例：《金刚经》，868年','Example: Diamond Sutra, dated 868'),shelfmark='Or.8210/P.2',note=pair('IDP目录明确记载现藏机构为British Library，出土地为敦煌莫高窟，来源为Stein 1906–8。批次路线不等于已逐件重建本卷的全部交接。','The IDP catalogue records British Library, Dunhuang Mogao and Stein 1906–8. A batch-level route is not a complete object-level custody chain.'),url=sources[5]['url'],status=pair('官方藏品目录已核','Official object record checked')),
 dict(id='bm',city='PL_LONDON',short='BM',name=pair('英国博物馆','British Museum'),kind=pair('博物馆 · 相关绘画','Museum · related paintings'),route='stein',collection=pair('斯坦因取得的敦煌佛教绘画','Buddhist paintings from Dunhuang acquired by Stein'),example=pair('示例：敦煌佛教绘画馆藏记录','Example: Dunhuang Buddhist painting record'),shelfmark='1919,0101,0.1',note=pair('绘画与写本文献分开登记。本例证明相关绘画的现藏机构，不把它自动计作写本转移。目录索引可读，正文访问受限。','Paintings are distinguished from manuscripts. This catalogue example documents a related painting, not an additional manuscript transfer. Indexed description accessible; full page access restricted.'),url=sources[6]['url'],status=pair('官方目录索引已核','Official catalogue index checked')),
 dict(id='bnf',city='PL_PARIS',short='BnF',name=pair('法国国家图书馆','Bibliothèque nationale de France'),kind=pair('图书馆 · 伯希和写本','Library · Pelliot manuscripts'),route='pelliot',collection=pair('Pelliot chinois、Pelliot tibétain等写本收藏','Pelliot chinois, Pelliot tibétain and related manuscript collections'),example=pair('收藏级入口：馆方目录与数字图像','Collection-level catalogue and digitised images'),shelfmark='Pelliot chinois',note=pair('馆方说明记载敦煌写本于1910年进入写本部。考察队主批1909年抵巴黎，与1910年机构入藏是两个不同阶段。','The BnF collection guide records entry into the manuscript department in 1910. Arrival of the expedition cargo in Paris in 1909 and institutional accession in 1910 are separate stages.'),url=sources[4]['url'],status=pair('官方收藏说明已核','Official collection guide checked')),
 dict(id='guimet',city='PL_PARIS',short='MNAAG',name=pair('吉美博物馆','Musée Guimet'),kind=pair('博物馆 · 相关绘画与文物','Museum · related paintings & objects'),route='pelliot',collection=pair('伯希和考察相关的敦煌绘画与文物','Dunhuang paintings and objects associated with the Pelliot expedition'),example=pair('示例：五佛曼荼罗','Example: Mandala of the Five Jina'),shelfmark='',note=pair('馆方明确区分：相关绘画、雕塑等在吉美，写本在法国国家图书馆。本例作为文献传播的物质文化背景。','The museum distinguishes its paintings and sculptures from manuscripts held by the BnF. This example provides material-cultural context for manuscript dispersal.'),url='https://www.guimet.fr/fr/nos-collections/chine-bouddhique-asie-centrale/mandala-des-cinq-jina',status=pair('官方馆藏与问答已核','Official collection / FAQ checked')),
 dict(id='nlc',city='PL_BEIJING',short='NLC',name=pair('中国国家图书馆','National Library of China'),kind=pair('图书馆 · 敦煌遗书','Library · Dunhuang manuscripts'),route='qing',collection=pair('敦煌遗书专藏；1910年运京文献为主体来源之一','Dunhuang special collection, with the 1910 transfer as a principal historical source'),example=pair('收藏级入口：目录、整理与保护','Collection-level catalogue and conservation work'),shelfmark=pair('BD系列','BD series'),note=pair('保留收藏级对应。项目中BD06825、BD06826–BD06847等逐件对应来自研究文献，尚未逐卷独立查核，未作为已核单件加入本页。','Shown at collection level. Individual BD-number matches in the project derive from research and have not all been independently checked against original manuscript images.'),url=sources[8]['url'],status=pair('官方馆藏与整理说明已核','Official collection / catalogue account checked'))
]
chapters=[
 dict(year='1900',title=pair('洞门重启','The cave opens'),text=pair('王圆箓发现藏经洞。写本在保管、赠送、选择与交易中，开始进入新的关系网络。','Wang Yuanlu discovers the Library Cave. Custody, gifts, selection and transactions gradually place its contents within new networks.'),focus='PL_MOGAO'),
 dict(year='1907',title=pair('取得，也有交涉','Acquisition and negotiation'),text=pair('从莫高窟到安西，箱笼与书信走着不同方向。王圆箓、蒋孝琬、信使与驮运者共同参与这一过程。','Cases and correspondence travel in different directions between Mogao and Anxi. Wang Yuanlu, Jiang Xiaowan, messengers and carriers all have roles.'),focus='PL_ANXI_REF'),
 dict(year='1908',title=pair('分岔的旅程','Journeys diverge'),text=pair('斯坦因批次向新疆转运；伯希和考察队主批向兰州、西安、郑州、上海移动。人的行程与物的行程需要分别辨认。','Stein’s cargo moves through Xinjiang; Pelliot’s main cargo travels towards Lanzhou, Xi’an, Zhengzhou and Shanghai. The traveller’s itinerary and the objects’ itinerary are distinguished.'),focus='PL_KUCHA'),
 dict(year='1909',title=pair('抵达，与消息传开','Arrivals and communication'),text=pair('运输批次抵达伦敦与巴黎。北京的学术交流与学部电报，使敦煌发现进入新的知识与行政网络。','Cargo arrives in London and Paris. Scholarly exchange in Beijing and an administrative telegram form part of a different network of knowledge and response.'),focus='PL_PARIS'),
 dict(year='1910',title=pair('进入公共收藏','Entering institutional collections'),text=pair('清政府组织运京，成为国图敦煌专藏的重要历史来源。法国国家图书馆也记载敦煌写本在1910年进入写本部。','The Qing-organised transfer to Beijing becomes a major historical source of the NLC collection. The BnF records entry of the Dunhuang manuscripts into its department in 1910.'),focus='PL_BEIJING'),
 dict(year='NOW',title=pair('分藏各地，重新相逢','Dispersed, yet connected'),text=pair('写本、印本与相关绘画今天分藏于不同机构。数字目录与图像，让我们可以重新连接这些材料。','Manuscripts, prints and related paintings are held by different institutions today. Digital catalogues and images reconnect the dispersed materials.'),focus='PL_MOGAO')
]
data=dict(version='1.0.1',verifiedOn='2026-10-28',places=places,flows=flows,institutions=institutions,chapters=chapters,sources=sources,notes=pair('曲线只表达史料支持的地域联系；不复原实际道路、航线或电缆。动画表现叙事顺序，不模拟逐日位置或运输速度。','Curves show documented geographical relationships, not reconstructed roads, shipping lanes or cables. Animation follows narrative stages, not daily positions or transport speeds.'))
(ROOT/'dist/data.js').write_text('window.DUNHUANG_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
world=ROOT/'dist/assets/world.json'
if world.exists():
    (ROOT/'dist/assets/world.js').write_text('window.DUNHUANG_WORLD='+world.read_text()+';\n')
    world.unlink()
manifest={n:hashlib.sha256((INPUT/n).read_bytes()).hexdigest() for n in ['地点_默认参考点.csv','实物流转_示意线.csv','知识传播_示意线.csv']}
(ROOT/'data-provenance.json').write_text(json.dumps(dict(input_hashes=manifest,excluded_summary_link='MAP_SG011',added_overview='WEB_QING_1910',originals_modified=False,modern_collection_level_mapping=True),indent=2))
print('Prepared:',len(places),'places,',len(flows),'source relationships,',sum(f['visible'] for f in flows),'displayed relationships,',len(institutions),'institutions')
