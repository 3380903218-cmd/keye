from pathlib import Path
import json, re, datetime, math, hashlib
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.hyperlink import Hyperlink

BASE=Path(__file__).resolve().parents[1]
TODAY='2026-09-17'
acad=[]; primary=[]
def A(id,priority,theme,authors,year,title,cite,guide,use,locator,limit,url,full,access,verified,identifier,local='',trace=''):
 acad.append(dict(id=id,priority=priority,theme=theme,authors=authors,year=year,title=title,citation=cite,guide=guide,use=use,locator=locator,limit=limit,url=url,full=full,access=access,verified=verified,identifier=identifier,local=local,trace=trace))
def P(id,priority,kind,author,year,title,guide,use,locator,limit,url,full='',access='公开网页可读',verified='已核读网页正文',local='',trace=''):
 primary.append(dict(id=id,priority=priority,kind=kind,authors=author,year=year,title=title,guide=guide,use=use,locator=locator,limit=limit,url=url,full=full,access=access,verified=verified,local=local,trace=trace))

A('A01','P0 核心五篇','景观／国家与日常','Brenda S. A. Yeoh; Lily Kong',1994,
 'Reading landscape meanings: State constructions and lived experiences in Singapore’s Chinatown',
 'Yeoh, Brenda S. A., and Lily Kong. 1994. “Reading Landscape Meanings: State Constructions and Lived Experiences in Singapore’s Chinatown.” Habitat International 18 (4): 17–35.',
 '从住房、社区、清洁化与保护等维度，比较国家赋予街区的意义和居民的日常经验；强调同一景观有相互关联的多重意义。',
 '全文框架最贴近大纲A/B/D层：把标牌、规划与商户记忆放在同一分析表中，而不先判定一方真实、一方虚假。',
 '先读摘要与结论，再读住房、社区和historic district相关段；具体引文页码须用取得的PDF核实。',
 '1994年的研究不能证明2026年商户仍持相同看法；官方与日常的分析区分也不等于双方始终对立。',
 'https://ink.library.smu.edu.sg/soss_research/1802/','https://doi.org/10.1016/0197-3975(94)90015-9',
 '机构库有Download入口；本次下载未成功，DOI可转出版社／NUS查阅','已核书目信息与机构库摘要，未核读全文',
 '10.1016/0197-3975(94)90015-9',trace='S05; V05; V06; sources/crossref_A01.json')
A('A02','P0 核心五篇','保护／旅游／真实性','Joan Henderson',2000,
 'Attracting tourists to Singapore’s Chinatown: A case study in conservation and promotion',
 'Henderson, Joan. 2000. “Attracting Tourists to Singapore’s Chinatown: A Case Study in Conservation and Promotion.” Tourism Management 21 (5): 525–534.',
 '以牛车水为案例讨论旅游推广与保护、社区参与及真实性；是追踪20世纪末街区改造争论的直接文献。',
 '用于历史背景和保护／商业章节；与P09的2023年更新文本对读，检查“活力”“传统”“游客”如何被重新组合。',
 'pp. 525–534；先查conservation、authenticity、local people与revitalisation；页码是文章范围，非已核具体论点页。',
 '本次只核到摘要和出版记录；不能据此复述全文细节，也不能把当年的批评直接套到白新春现状。',
 'https://www.sciencedirect.com/science/article/pii/S0261517799001089','https://doi.org/10.1016/S0261-5177(99)00108-9',
 '出版社摘要可检索；全文可能需NUS机构登录，具体订阅未测试','已核书目／出版社摘要；正文页面抓取失败',
 '10.1016/S0261-5177(99)00108-9',trace='S01; V01; V09; sources/crossref_A02.json')
A('A03','P0 核心五篇','华人性／国家身份','Ying-kit Chan',2023,
 'The Chineseness of Chinatown in Singapore: Chinese New Year Celebrations in a Multiracial Heritage Site',
 'Chan, Ying-kit. 2023. “The Chineseness of Chinatown in Singapore: Chinese New Year Celebrations in a Multiracial Heritage Site.” In Heritage, Contested Sites, and Borders of Memory in the Asia Pacific, edited by Edward Boyle and Steven Ivings, 56–79. Leiden: Brill.',
 '通过春节庆典讨论牛车水的“华人性”如何与多种族国家叙事相连；非常适合把中国／华人、南洋与新加坡认同分开分析。',
 '用于公共叙事章和节庆／壁画分析；与茶商的实际配茶、器物和家族叙事形成“符号—实践”比较。',
 'Chapter 3, pp. 56–79；先读摘要，取得全文后定位春节、多种族与方言群体论述。',
 '节庆是特定场景；不要把“展示中的华人性”直接当成所有商户的自我认同。细节引文需借阅版本补核。',
 'https://brill.com/display/book/9789004512986/BP000013.pdf','https://doi.org/10.1163/9789004512986_004',
 '出版社摘要可检索；显示机构登录入口；本次未取得全文','已核出版社摘要、章节、作者、年份与页码',
 '10.1163/9789004512986_004',trace='S02; V01; V09; S11; sources/crossref_A03.json')
A('A04','P0 核心五篇','茶贸易／跨区域历史','Jason Lim',2011,
 'The Dynamics of Trans-Regional Business and National Politics: The Impact of Events in China on Fujian-Singapore Tea Trading Networks, 1920–1960',
 'Lim, Jason. 2011. “The Dynamics of Trans-Regional Business and National Politics: The Impact of Events in China on Fujian-Singapore Tea Trading Networks, 1920–1960.” In Singapore in Global History, edited by Derek Heng and Syed Muhd Khairudin Aljunied, 135–150. Amsterdam University Press.',
 '研究福建—新加坡茶商网络与中国政治变化，提供移民、贸易和本地再加工的历史背景；比泛泛的“文化混杂”理论更接近白新春案例。',
 '用于历史背景与白新春微观案例；追踪茶叶来源、运输、加工与地方口味的关系，提出可向店方核实的具体问题。',
 'Chapter 7, pp. 135–150；重点检索Expanding the business network、Pek Sin Choon与re-process。',
 '1920–1960年贸易史不能直接证明今天的配方。检索摘录中Pek Sin Choon旁的中文店名疑有错配，正式引用应核原页及脚注，不照抄。',
 'https://www.degruyterbrill.com/document/doi/10.1515/9789048514373-009/html','https://www.jstor.org/stable/j.ctt46mtvv.11',
 '出版社／JSTOR标为开放获取；本次直接下载受阻，须手动打开章节入口','已核出版社完整引文和开放获取标识；未核读完整章节',
 '10.1515/9789048514373-009',trace='S02; S06; S09; V07; V08')
A('A05','P0 核心五篇','遗产理论／解释权','Laurajane Smith',2006,
 'Uses of Heritage',
 'Smith, Laurajane. 2006. Uses of Heritage. Routledge.',
 '把遗产理解为赋予过去意义的文化过程，帮助分析哪些价值获得机构认可，以及哪些日常经验较少被展示。',
 '用于引言与结论的概念框架；将authorized heritage discourse作为提问工具，再用田野检验，不把它当作已证明的官民冲突。',
 '优先第1章The Discourse of Heritage、第2章Heritage as Cultural Process；无需从头读完整本。',
 '出版社不同版次页面出现2007版权字样；此处采用作者机构记录的2006年初版。具体引文页码必须与使用版本一致。',
 'https://researchportalplus.anu.edu.au/en/publications/uses-of-heritage/','https://doi.org/10.4324/9780203602263',
 '书目与出版社目录可读；全文需电子书权限或借阅，NUS馆藏未登录核实','已核作者机构书目、出版社简介与目录；未读全文',
 '10.4324/9780203602263; ISBN 0415318300',trace='S04; V04')
A('A06','P1 优先补充','活态遗产／连续性','Ioannis Poulios',2014,
 'The Past in the Present: A Living Heritage Approach – Meteora, Greece',
 'Poulios, Ioannis. 2014. The Past in the Present: A Living Heritage Approach – Meteora, Greece. London: Ubiquity Press.',
 '以希腊迈泰奥拉为案例，讨论社区与场所关系的连续性、使用与维护实践，以及有形和无形表达如何持续变化。',
 '用于白新春章节：把延续口味、制作过程、器物使用和经营适应作为观察维度；也可替代A05承担核心书目的理论角色。',
 '印刷pp. 25–29（第4章）、pp. 129–133（第14章）；PDF第37–41、141–145页。',
 '宗教社区与商业街区不同；“核心社区”和“原有功能”的前提不能直接套用到迁店商户。作者也讨论适用边界。',
 'https://www.ubiquitypress.com/books/m/19','https://discovery.ucl.ac.uk/1465977/1/Poulios.11-3-95-1-10-20140826.pdf',
 '开放获取；PDF已下载（182页）','已核全文身份并核读相关章节；非全书精读',
 '10.5334/bak; ISBN 9781909188297','fulltexts/A06_Poulios_2014_Past_in_the_Present.pdf','S04; V02; sources/retrieval_manifest.json')
A('A07','P1 优先补充','牛车水史／多种族性','Brenda S. A. Yeoh; Lily Kong',2012,
 'Singapore’s Chinatown: Nation Building and Heritage Tourism in a Multiracial City',
 'Yeoh, Brenda S. A., and Lily Kong. 2012. “Singapore’s Chinatown: Nation Building and Heritage Tourism in a Multiracial City.” Localities 2: 117–159.',
 '连接殖民时期的族群空间、建国、遗产旅游和地方政治，说明新加坡牛车水不能直接等同于西方城市的少数族裔飞地。',
 '最方便先读的开放全文；为历史背景、1990年代争论与多种族框架提供线索。A03取不到时可替代。',
 '印刷pp. 117–123（定位）、pp. 145–153（多种族、地方意义与结论）；PDF页码=印刷页码−116。',
 '文章与A01有作者及部分材料重合，不能算两组独立田野验证；2012年后的变化仍须新资料。',
 'https://pncc.pusan.ac.kr/bbs/pncc/12025/648424/download.do','https://pncc.pusan.ac.kr/bbs/pncc/12025/648424/download.do',
 '公开PDF已下载（44页，含末页空白）','已核全文身份与关键段落；未逐页精读',
 '本次未查得DOI；以期刊卷页及大学托管PDF定位','fulltexts/A07_Yeoh_Kong_2012_Singapore_Chinatown.pdf','S05; V02; V03')
A('A08','P1 优先补充','地方／游客／商业化','Voon Chin Phua; Jesse E. Shircliff',2020,
 'Heritage spaces in a global context: The case of Singapore Chinatown',
 'Phua, Voon Chin, and Jesse E. Shircliff. 2020. “Heritage Spaces in a Global Context: The Case of Singapore Chinatown.” Current Issues in Tourism 23 (12): 1449–1453.',
 '基于2018年半结构访谈，比较本地人与游客对遗产与商业化的理解；摘要呈现两类人对商业化的不同关注。',
 '用于说明不同受众的真实性标准可能不同；帮助设计开放访谈问题和公共史受众反馈，而非替代你的问卷。',
 '全文仅5页，适合快速精读；先查样本、访谈招募、heritage与commercialization编码。',
 '机构库明确不提供全文。2019在线发表、2020卷期出版；采用2020。与A09可能使用相关研究材料，独立性待全文核查。',
 'https://cupola.gettysburg.edu/socfac/47/','https://doi.org/10.1080/13683500.2019.1689930',
 '机构库摘要可读；全文转出版社／NUS，订阅未测试','已核机构库摘要与完整引文；未读全文',
 '10.1080/13683500.2019.1689930',trace='S05; V03')
A('A09','P1 优先补充','空间／标准化华人符号','Jesse Ezra Shircliff',2020,
 'Is Chinatown a place or space? A case study of Chinatown Singapore',
 'Shircliff, Jesse Ezra. 2020. “Is Chinatown a Place or Space? A Case Study of Chinatown Singapore.” Geoforum 117: 225–233.',
 '以访谈和问卷讨论人们如何用全球唐人街的熟悉符号理解新加坡牛车水；区分具体地方历史与抽象化的唐人街想象。',
 '用于壁画、标牌和旅游展示分析；公共史页面可主动加入具体店铺、年份和声音，检验是否打破泛化符号。',
 'pp. 225–233；先读Abstract、Chinatown as a cultural space，再核方法部分。',
 '不能由游客认可某些符号推出其“不了解历史”；本次未取得样本与分析全过程。不是2021年论文，卷期为2020年。',
 'https://www.sciencedirect.com/science/article/abs/pii/S0016718520302542','https://doi.org/10.1016/j.geoforum.2020.10.006',
 '出版社摘要与部分段落可读；全文需检查机构权限','已核出版社摘要、部分段落与卷页',
 '10.1016/j.geoforum.2020.10.006',trace='S02; S08')
A('A10','P1 优先补充','后殖民城市／历史与遗产','Daniel P. S. Goh',2014,
 'Between History and Heritage: Post-Colonialism, Globalisation, and the Remaking of Malacca, Penang, and Singapore',
 'Goh, Daniel P. S. 2014. “Between History and Heritage: Post-Colonialism, Globalisation, and the Remaking of Malacca, Penang, and Singapore.” TRaNS: Trans-Regional and -National Studies of Southeast Asia 2 (1): 79–101.',
 '比较三个海峡城市的遗产生产与城市改造，讨论国家认同、资本与市民组织的相互作用；新加坡段落涉及1998年牛车水计划和民间回应。',
 '用于保护／更新章节及追溯争议；A02全文受限时，可用其公开正文补充历史争论。',
 '网页小节Singapore: Gridlocked Heritage Space and The Developmental State，尤其At the Margins of the Gridlock；网页无稳定页码时按节定位。',
 '关于SHS具体立场的叙述是二手引用；正式分析其原话，应追到P13原书或同期报纸。三个城市不能等量套用。',
 'https://www.cambridge.org/core/journals/trans-trans-regional-and-national-studies-of-southeast-asia/article/between-history-and-heritage-postcolonialism-globalisation-and-the-remaking-of-malacca-penang-and-singapore/35674CFC127BC80D81A186EFA672C7C6','https://doi.org/10.1017/trn.2013.17',
 '出版社HTML正文可读；本次已核读新加坡相关段落','已核书目与相关全文段落',
 '10.1017/trn.2013.17',trace='S02; V01; V05; sources/crossref_A10.json')
A('A11','P2 按需选读','比较案例／多方主体','T. C. Chang',2000,
 'Singapore’s Little India: A Tourist Attraction as a Contested Landscape',
 'Chang, T. C. 2000. “Singapore’s Little India: A Tourist Attraction as a Contested Landscape.” Urban Studies 37 (2): 343–366.',
 '小印度案例把游客／本地人之外的族群关系、规划者与空间使用者也纳入“争议景观”研究。',
 '用于完善主体分类：商户、居民、文化机构、游客、规划部门并非各自内部同质。不要把论文扩写成两个街区比较。',
 '摘要、insider–outsider讨论及结论；pp. 343–366。',
 '研究地点是小印度，不能作为牛车水搬迁、租金或态度的直接事实证据。',
 'https://journals.sagepub.com/doi/10.1080/0042098002221','https://doi.org/10.1080/0042098002221',
 '出版社摘要／部分文本可检索；完整阅读权限待核','已核摘要和Crossref完整书目；未读全文',
 '10.1080/0042098002221',trace='S02; sources/crossref_A11.json')
A('A12','P2 按需选读','真实性／旅游理论','Ning Wang',1999,
 'Rethinking authenticity in tourism experience',
 'Wang, Ning. 1999. “Rethinking Authenticity in Tourism Experience.” Annals of Tourism Research 26 (2): 349–370.',
 '真实性理论的经典阅读候选，可帮助区分对物品、展示和个人体验的不同判断；本次仅核到书目，理论细分须读原文。',
 '当论文确实需要authenticity概念时再读；可检验商户配茶、游客体验、复原展陈是否使用同一标准。',
 'pp. 349–370；全文检索objective、constructive、existential authenticity。',
 '尚未核读原文，不能直接将此导读作为文献摘要提交。对游客体验的理论也不能证明历史事实。',
 'https://doi.org/10.1016/S0160-7383(98)00103-0','https://doi.org/10.1016/S0160-7383(98)00103-0',
 'DOI书目已核；全文需通过出版社／NUS查阅','仅核书目；理论说明为阅读方向',
 '10.1016/S0160-7383(98)00103-0',trace='S05; V09; sources/crossref_A12.json')
A('A13','P1 优先补充','口述史／记忆方法','Alessandro Portelli',1991,
 'The Death of Luigi Trastulli and Other Stories: Form and Meaning in Oral History',
 'Portelli, Alessandro. 1991. The Death of Luigi Trastulli and Other Stories: Form and Meaning in Oral History. Albany: State University of New York Press.',
 '讨论讲述者如何通过叙事理解生活，以及访谈关系如何影响历史知识，适合处理商户口述与公开时间线之间的差异。',
 '用于方法段和访谈分析：把“发生了什么”与“受访者如何记忆和赋义”分开记录；保留听不清内容。',
 '优先目录中关于口述史意义与方法的篇章；章节页码在取得版本后补记。',
 '口述史重视主观意义，不等于可以补写听不清的回答或免除年份核验。本次只读出版社说明。',
 'https://sunypress.edu/Books/T/The-Death-of-Luigi-Trastulli-and-Other-Stories','https://sunypress.edu/Books/T/The-Death-of-Luigi-Trastulli-and-Other-Stories',
 '出版社简介可读；全文需电子书权限或借阅','已核出版社作者、年份、ISBN与简介；未读全文',
 'ISBN 9780791404300',trace='S06')
A('A14','P1 优先补充','公共史／共同解释','Michael Frisch',1990,
 'A Shared Authority: Essays on the Craft and Meaning of Oral and Public History',
 'Frisch, Michael. 1990. A Shared Authority: Essays on the Craft and Meaning of Oral and Public History. Albany: State University of New York Press.',
 '口述史与公共史方法著作，可用于思考研究者、讲述者与公众如何共同参与历史解释；适合多声部路线设计。',
 '用于Public History设计说明：让每站保留来源署名、不同叙述和开放问题，并邀请商户核对其被引用的说法。',
 '优先Introduction与Memory, History, and Cultural Authority部分；具体引用页码待借阅本核实。',
 '“共同解释”并不取消史料核查和研究者责任；不能假设加入一段录音便实现平等参与。',
 'https://sunypress.edu/Books/A/A-Shared-Authority','https://utpdistribution.com/9780791401330/a-shared-authority/',
 '出版社／发行方简介与目录可读；全文需借阅','已核出版社记录与发行方目录；未读全文',
 'ISBN 9780791401330',trace='V04; V07')
A('A15','P2 按需选读','同族差异／新移民','Sylvia Ang',2018,
 'The ‘new Chinatown’: The racialization of newly arrived Chinese migrants in Singapore',
 'Ang, Sylvia. 2018. “The ‘New Chinatown’: The Racialization of Newly Arrived Chinese Migrants in Singapore.” Journal of Ethnic and Migration Studies 44 (7): 1177–1194.',
 '讨论新加坡华人与新来中国移民之间的差异化及空间化叙述，提醒研究者不要把“华人”当成单一身份。',
 '只在访谈出现“本地／中国新移民”等分类时辅助解释；可校准研究语言，避免把中国、华人、南洋和本土当成互斥固定标签。',
 'pp. 1177–1194；先核全文的“new Chinatown”具体地点与招募方法，再决定是否引用。',
 '题名中的“new Chinatown”不能未经核实就等同牛车水保护区；2017 online、2018卷期，采用2018。',
 'https://www.tandfonline.com/doi/full/10.1080/1369183X.2017.1364155','https://doi.org/10.1080/1369183X.2017.1364155',
 '出版社摘要可读；正文显示Get Access','已核出版社摘要与卷页；未读全文',
 '10.1080/1369183X.2017.1364155',trace='S08')

P('P01','P0 必查','商户自述／一手材料','Pek Sin Choon Pte Ltd','n.d.','History — Pek Sin Choon',
 '店方明确区分1910年迁入与1925年创店，并叙述George Street、New Market Road及1998年Mosque Street迁店、茶具与品牌。',
 '核对访谈时间线；分析店方如何组织家族、南洋口味和现代化叙事。',
 'Our Forefathers；Passing the Reins；Tea Man；特别是1998、2001两段。',
 '品牌自述不是独立档案；现有页面未证明每次搬迁与哪一个政府工程有关。“第四代”应向店方问清计算口径。',
 'https://peksinchoon.com/about/history/',trace='S01; V01')
P('P02','P0 必查','商户自述／技艺说明','Pek Sin Choon Pte Ltd','n.d.','What is Nanyang Tea?',
 '店方对“南洋茶”的定义及制作叙述，是观察传统如何被命名和解释的直接文本。',
 '与访谈、实际配茶观察、A04茶贸易史对读；比较原料来源、加工地点与地方口味。',
 '页面主体“What is Nanyang Tea?”；摘录须保存页面日期并由店方解释专门术语。',
 '属于商户的自我表述，不能直接代表所有南洋茶商；网页不等于现场工艺观察。',
 'https://peksinchoon.com/about/what-is-nanyang-tea/',verified='页面可解析，已确认身份；详细工序待逐段核读',trace='V03')
P('P03','P0 必查','NHB—商户共同策展','National Heritage Board','n.d.','老店铺文化站（牛车水）／Street Corner Heritage Galleries: Chinatown',
 '计划由NHB与老店铺合作，使用历史文件、照片及文物策展；白新春专节谈1910迁入、1925创店和南洋茶拼配。',
 '核心“合作／协商”材料；与P01比较共同选择的历史、遗漏和展品，避免把店内展陈一概视为完全独立的民间声音。',
 '中文“老店铺文化站”计划介绍；“上乘名茶的保证：白新春茶庄”专节。',
 '机构与店方可能共享同一口述来源；两网页一致不等于两份独立历史证据。不要把介绍写成无争议的全貌。',
 'https://www.roots.gov.sg/stories-landing/stories/Street-Corner-Heritage-Galleries-Chinatown-Chinese',
 'https://www.roots.gov.sg/stories-landing/stories/Street-Corner-Heritage-Galleries-Chinatown',trace='S01; S03; V06')
P('P04','P0 必查','官方地点解释','National Heritage Board','2020（内容截至2019）','37 Pagoda Street',
 '解释苦力馆、劳工生活与后来商业使用，且对广合源旧址使用“believed to be”的谨慎表述。',
 '对读现场“A Former Coolie House”标牌；分析移民苦难如何成为公共历史，并比较文字、图片和今天用途。',
 '正文第1段及末段；页脚说明内容截至2019年9月，Last Updated 15 October 2020。',
 '网页并非现场标牌逐字版；旧址认定带保留语气。2019租户不等于2026现状；Roots收录本身不代表法定保护身份。',
 'https://www.roots.gov.sg/places/places-landing/Places/surveyed-sites/37-Pagoda-Street',trace='S01; V06')
P('P05','P0 必查','规划部门／保护叙事','Urban Redevelopment Authority','n.d.','Chinatown — Kreta Ayer Conservation Area',
 '提供牛车水保护区历史、四个分区、1989年保护日期、建筑形态，并提到印度教、穆斯林等群体的空间使用。',
 '核定田野主要范围与built heritage背景；比较官方对居住改善、保护和持续使用的叙述。',
 'About；The History；The Architecture；The Legacy；保护日期7 July 1989。',
 '这是规划部门的历史解释；整个Chinatown与Kreta Ayer不是完全相同范围。现代“华人街区”叙事不能抹去其他社群。',
 'https://www.ura.gov.sg/conservation/find-a-building/conservation-portal/ktay/',trace='S03; V06')
P('P06','P0 必查','官方地图／遗产路线册','Urban Redevelopment Authority; Preservation of Sites and Monuments','n.d.（册内未见明确年款）','Chinatown Historic District — Trail Brochure',
 '含历史街区地图、分区及历史建筑条目；适合建立固定路线与比较官方选点方式。',
 '用于Public History路线底稿、保护范围与历史地点索引；与用户自摄照片建立过去／现在对照。',
 'PDF第1页总图与历史概述；其余页按站点标题阅读。',
 '旧册中的机构、建筑用途及交通标注可能已变；不能作为当前导航或营业情况证明。复制地图前核图像使用条件。',
 'https://www.roots.gov.sg/-/media/Roots/Files/ura-chinatown-trail/urachinatowntrail17_brochure.pdf',
 access='公开PDF已下载（6页）',verified='已核PDF身份、地图及相关正文',local='fulltexts/P06_URA_Chinatown_Historic_District_Trail.pdf',trace='S03; sources/retrieval_manifest.json')
P('P07','P0 必查','官方非遗清单／实践者叙事','National Heritage Board','n.d.','Making and Sharing of Tea',
 '涵盖不同社区的茶实践；白新春段落描述选叶、分层拼配、揉拌和焙制，以及讲座和工作坊。',
 '与P02对读：观察技艺如何被纳入“新加坡非遗”框架；为补访问法和器物观察提供线索。',
 'Experience of Practitioners → Mr Kenry Peh — Pek Sin Choon Tea Merchants；References。',
 '官方清单仍可能源自同一位实践者；工序和原料当前情况需现场核验，不推断为行业通则。',
 'https://www.roots.gov.sg/ich-landing/ich/Making-and-Sharing-of-Tea',trace='S07; V06')
P('P08','P1 补充','旅游推广文本','Singapore Tourism Board',2019,'Singapore Insider, January–March 2019 — Multicultural Chinatown',
 '以“Multicultural Chinatown”组织春节、原貌馆与街区景点，提供有明确年份的旅游宣传文本。',
 '分析“华人文化”与“多种族”如何在同一推广框架中并置；与A03和今天的现场展示比较。',
 '册内印刷p. 12，Multicultural Chinatown；地图与景点条目。',
 '2019季刊不能代表2026宣传；这是宣传选择的证据，不是受众实际体验证据。',
 'https://www.visitsingapore.com/content/dam/desktop/global/about-singapore/traveller-information/q1-singapore-insider-2019-en.pdf',
 access='官方PDF内容可检索；未下载，直接打开状态待用户核查',verified='已核官方索引中的页题与内容摘录',trace='S07')
P('P09','P0 必查','政府更新方案／一手文本','Singapore Land Authority; Singapore Tourism Board; Urban Redevelopment Authority','2023-11-30','Rejuvenating Smith Street to Enhance the Inclusiveness and Vibrancy of Chinatown',
 '联合招标文件同时强调文化保护、多样用途、社区活动、客流与商业活力，提供明确的当代城市更新话语。',
 '用于保护／商业章；对照A02历史批评和P10营业反馈，检验计划目标、实施和具体店铺经验之间的距离。',
 '第1–4段：目标；第7段：商会表述；Price-Quality tender及附表：管理与用途。',
 '招标文本只能证明计划和目标，不能证明更新已成功、租金已上涨或所有商户获益。',
 'https://www.sla.gov.sg/news/press-release/rejuvenating-smith-street-to-enhance-the-inclusiveness-and-vibrancy-of-chinatown/',
 'https://www.stb.gov.sg/about-stb/media-publications/media-centre/rejuvenating-smith-street-to-enhance-the-inclusiveness-and-vibrancy-of-chinatown/',trace='S03; S08; V06')
P('P10','P1 补充','新闻采访／多方反馈','Nadine Regina Yeam; Calvin Yang（CNA）','2025-05-19','Some Chinatown businesses see boost in sales with rejuvenation of iconic Smith Street',
 '报道同时呈现部分商家营业改善，以及租金和人手压力；可防止把更新预设成纯粹破坏或全面成功。',
 '与P09计划文本、自己的2026观察对读；可用于设计“哪些变化有帮助、哪些带来困难”的补访问题。',
 'Overcoming Challenges及商会回应段；任何销售数字必须保留“部分商户／受访者自述”的范围。',
 '新闻选择的受访者不是总体抽样；销售变化未经本项目独立核实，也不能推断全街区因果效果。',
 'https://www.channelnewsasia.com/singapore/chinatown-rejunvenate-smith-street-cultural-historical-heritage-businesses-rental-manpower-5139211',
 verified='已核新闻页面索引正文与作者日期；未逐段核读全篇',trace='V08')
P('P11','P0 必查','商户自述／公司时间线','Lau Choy Seng Pte Ltd','n.d.','About Us — Lau Choy Seng',
 '列出1948创店、1960年代迁至38 Temple Street、1970年代厨具业务、1993年迁至23与25 Temple Street等节点。',
 '补充低清录音可核事实；访谈可追问客户、供货地、产品类型变化与“传统”的关系。',
 'About Us；Company Timeline → 1948、1960s、1970s、1993。',
 '企业自述可互证时间线但非独立档案；不能据此补成录音里未能辨认的回答，也没有证明壁画如何影响经营。',
 'https://lauchoyseng.com/about-us/',trace='S03; V01')
P('P12','P2 待取得','政策分析报告／灰色文献','Alisa Toh Qian Wen; Chee Wei Jia; Lai Jian Qin; Norman Maswari Aziz-Boey; Tan Han Feng, Chester Matthias; Vanessa Chiam Hui Ting',2017,'Safeguarding Intangible Cultural Heritage in Chinatown: Threats & Strategies',
 'NUS李光耀公共政策学院学生为SHS开展的Policy Analysis Exercise，主题直接针对牛车水非遗的威胁与策略。',
 '若及时取得，可补充利益相关者／保护策略框架；先读研究方法和限制再引用结果。',
 '待取得完整报告后定位Executive Summary、Methodology与Recommendations；目前不填结果页码。',
 '非同行评审论文，不建议充当五篇学术文献之一。旧PDF直链本次404，未核全文；不能把摘要线索当成已验证结果。',
 'https://www.singaporeheritage.org/?author=3','https://www.singaporeheritage.org/wp-content/uploads/2018/05/LKYSPP-SHS-Cultural-Heritage-in-Chinatown-Final-Report-13-Nov-2017.pdf',
 access='发布记录可查；旧PDF失效，待向图书馆／SHS查询',verified='仅核发布机构记录及封面索引；未核全文',trace='S02; S09; V07; sources/retrieval_manifest.json')
P('P13','P1 补充','民间组织立场／争论原始材料','Kwok Kian Woon; C. J. Wan-Ling Wee; Karen Chia（编）',2000,'Rethinking Chinatown and Heritage Conservation in Singapore',
 'SHS关于1998年牛车水重塑计划的讨论集，是追溯“谁来定义遗产”历史争议的重要原始材料；含中英文内容。',
 '用来核对A10对SHS立场的二手转述；比较民间组织如何理解多族群、生活传统与公共参与。',
 'ISBN 9810421338；NLB参考书目确认编辑、题名与2000年。取得书后核相关篇章及pp. 17–22线索。',
 'pp. 17–22来自A10的引文线索，尚未核原书。组织倡议文本与同行评审研究角色不同。',
 'https://reference.nlb.gov.sg/arts/visual-arts/artxstacks/places/',
 'https://openlibrary.org/works/OL19032218W/Rethinking_Chinatown_and_heritage_conservation_in_Singapore',
 access='NLB书目确认；全文需查馆藏借阅，未测试当前可借性',verified='已核NLB书目与A10引文链；未读原书',trace='S06; V01')
P('P14','P1 补充','官方奖项／认可过程','National Heritage Board','2025-04-04','Celebrating Heritage Practitioners and Nurturing Youth Stewards at the Stewards of Intangible Cultural Heritage Award 2024',
 '官方发布材料列白新春为2024届非遗传承奖获奖者；颁奖活动发生于2025年4月，届次与颁奖年份不同。',
 '讨论商户实践如何获得国家遗产认可；补访可问获奖、展示或教学活动怎样影响店方表达。',
 '媒体稿第一页日期、获奖者图片说明；颁奖2 April 2025／发布4 April 2025，奖项届次2024。',
 '原PDF当前下载404，信息由官方搜索索引及商户注册页互核；使用前取得原稿。奖项不能单独证明社区代表性或传统真实性。',
 'https://www.nhb.gov.sg/what-we-do/our-work/sector-development/heritage-businesses/sg-heritage-business-registry/chinatown/pek-sin-choon-pte-ltd',
 'https://www.nhb.gov.sg/-/media/nhb/files/media/releases/2025/media-release---celebrating-heritage-practitioners-and-nurturing-youth-stewards-at-the-stewards-of-ich-award-2024.pdf',
 access='官方索引可查；详情抓取受限、旧PDF404，待取得原稿',verified='已核官方索引元数据／关键日期；未核完整原稿',trace='S07; S09; V07; sources/retrieval_manifest.json')
P('P15','P1 补充','图书馆专题文章／二手历史','Ng Yun Ling（BiblioAsia／NLB）',2026,'The Perfect Brew: Singapore’s Chinese Tea Culture',
 '连接茶贸易、社群和当代创新，包含白新春包装与南洋拼配线索；文末参考资料可继续追到茶业史原始出处。',
 '方便中文背景读者进入英文茶文化资料；与A04、P01和P07串联阅读，区分1910家族故事和1925店铺建立。',
 '网页标示18 May 2026；期刊卷期线索Vol. 22, Issue 2（Jul–Sep 2026）；参考注释与白新春段落。',
 '图书馆专题写作不等同于同行评审研究；“traces its history to 1910”不能改写成1910创店。',
 'https://biblioasia.nlb.gov.sg/all-sections/vol-22-issue-2-jul-sep-2026-the-perfect-brew--singapore-s-chinese-tea-culture/',
 verified='已核网页正文相关段、作者与日期',trace='S02; V02; V03')
P('P16','P1 补充','国际规范／非遗定义','UNESCO',2003,'Convention for the Safeguarding of the Intangible Cultural Heritage',
 '用作非遗定义和社区参与的概念参照，重点看不断再创造的实践、知识及技艺如何被界定。',
 '方法／理论界定的短引用候选；帮助构造口味、调配、器物、传承和展示的观察清单。',
 'Article 2.1（定义）、2.2（类别）、15（社区参与）；正式引用前核官方条文。',
 '规范性文本并非牛车水现状证据；不能把收录／获奖自动等同UNESCO名录。',
 'https://ich.unesco.org/en/convention',access='官方条文入口；本次抓取受限，正文待复核',verified='已确认官方入口；条文作为待核阅读位置',trace='V08')
P('P17','P1 补充','国际建议／历史城市景观','UNESCO',2011,'Recommendation on the Historic Urban Landscape',
 '主张把有形与无形城市遗产纳入城市发展、生活质量及持续变化的整体语境。',
 '用于解释为什么保护不只是保存立面；可为比较店屋保护、店铺经营与社区使用提供观察维度。',
 '官方入口About the Recommendation；第3段概念说明与2011年11月10日通过日期。',
 '作为分析参照，不能直接说牛车水被列入世界遗产或本地规划已经满足此建议。',
 'https://whc.unesco.org/en/hul/',trace='V08; V09')
P('P18','P1 补充','商会旅游解释／公共艺术','Chinatown Business Association','n.d.','My Chinatown Home Mural',
 '街区推广页定位30 Smith Street的壁画；为比较家庭记忆如何在街面呈现提供选点。',
 'Public History候选站；与自己的壁画照片、作者说明及观众使用方式并读，分析记忆展示。',
 '地址30 Smith Street及Introduction；作者意图另向艺术家来源核实。',
 '商会推广页不是艺术家的自述，不能把全部壁画归为“政府叙事”；公开页面也不自动授权复制作品。',
 'https://chinatown.sg/visit/my-chinatown-home-mural/',trace='S10; V08')
P('P19','P1 补充','展馆自我呈现／公共史案例','Chinatown Heritage Centre','n.d.（2026访问）','Chinatown Heritage Centre — About / Exhibitions',
 '馆方以1950年代店屋居住者的复原生活与多感官体验组织历史故事；可观察“authentic”在展馆中的使用。',
 '比较复原展陈、P04街头标牌与商户仍在进行的实践；作为双语公共史呈现的参考对象。',
 'About Chinatown Heritage Centre；“One House, Many Lives”；展览说明。',
 '网站可读不代表已参观展览；展馆宣传的“唯一／第一”等词不作为本项目事实。线下门票与拍摄条件需另查。',
 'https://www.chinatownheritagecentre.com.sg/',trace='V08; V09')
P('P20','P1 补充','图书馆数字公共史／地图','National Library Board',2021,'Chinatown — Curiocity Story Map',
 '把牛车水地标、历史资料和地图组织为公众可浏览的故事地图，说明数字路线可如何标明来源与覆盖范围。',
 '用于“一街一忆”形式参考；分析其选点与遗漏，再设计自己的多声部站点，而非复制地图内容。',
 '页面15 December 2021；Notes说明非穷尽覆盖、OneMap底图和参考资料。',
 '此资料首先是公共史设计案例；2021地图内容与当前现场用途需分别核对，地图及图片权利逐项检查。',
 'https://curiocity.nlb.gov.sg/resource-room/story-maps/chinatown/',
 'https://curiocity.nlb.gov.sg/story-maps/historic-districts/',verified='已核NLB页面说明及参考来源',trace='S10')

# Retrieval updates are read from actual saved manifests; no absent file is advertised as downloaded.
for mf in ['retrieval_manifest.json','retrieval_extra.json']:
 if (BASE/'sources'/mf).exists():
  for r in json.loads((BASE/'sources'/mf).read_text()):
   if r.get('kind')=='pdf' and r.get('local'):
    id=r['id'][:3]
    for item in acad+primary:
     if item['id']==id:
      item['local']=r['local']
      item['access']=f"公开PDF已下载（{r.get('pages','?')}页）；见本地全文"
      if id in ['A01','A04','P12']: item['verified']='已核下载文件身份；重点内容待精读'

CORE=[
 ['A01','框架起点：国家规划与日常经验','把大纲A/B/D四层具体化，建立“谁说、在哪里说、如何使用”的比较表。','与A02共同讨论保护／旅游；与A05比较地方经验和机构解释权。','若SMU下载失败，先读A07；两篇作者与部分材料重合，避免在五篇中占用两个重复位置。'],
 ['A02','案例争议：保护与旅游开发','提供牛车水20世纪末旅游开发争议，回应课程的contestation要求。','与P09/P10对读计划、反馈和当代使用；与A03比较不同年代的公共形象。','优先通过NUS打开DOI；仍取不到可用公开HTML的A10替代，并相应改为城市空间比较视角。'],
 ['A03','身份协商：华人性与多种族国家','将中国／华人、地方文化和新加坡国家身份拆开，避免传承与本土化二选一。','与A04比较节庆／视觉符号和茶贸易／经营实践这两种身份形成路径。','若Brill无法取得全文，用A07替代；不要把摘要改写成已完成的文献评述。'],
 ['A04','具体历史：茶贸易与南洋网络','把核心商户放回福建—新加坡贸易及移民历史，给微观案例提供历史深度。','与A03形成“被展示的华人性—跨地区形成的实践”对话；与P01/P07核对细节。','JSTOR与出版社标为OA；先试章节入口。若仍受阻，可先读A07完成背景，但茶贸易论点应暂缓。'],
 ['A05','解释权理论：遗产是文化过程','为“谁定义值得保存的遗产”提供概念，帮助统合前四篇。','用P03共同策展材料检验其适用性，保留合作、重合与张力。','优先读第1–2章；借阅受限时可用已下载A06替代，理论重点将转向社区与连续性。'],
]

EVIDENCE=[
 ['E01','1910迁入与1925创店应区分','公开自述一致，独立史实仍可追核','P01; P03; P15','P01 Our Forefathers；P03白新春专节','店方与NHB叙述区分移民时间和商铺建立；P15的1910是history trace。','支持时间线区分','白新春案例开头','用旧广告、名录或原始公司材料补核；不要写“1910创店”。'],
 ['E02','1998迁至Mosque Street；具体政府工程原因尚未证实','年份有店方资料；原因未解决','P01','Tea Man → 1998 relocation段','公开店史记迁至Mosque Street，但本次未核到每次迁店对应的工程、通知或补偿。','限制因果推断','城市更新／商户适应','补访：旧址、起止年、通知、工程名；查D02/D04，不凭MRT时间线反推因果。'],
 ['E03','“第四代”称谓须问清传承计算方式','店方自我称谓，口径待说明','P01; P03','P01 Tea Man；P03创办人和传承叙述','创办人与其母亲共同创店，世代可按不同起点计算。','待核口径','商户家族记忆','问“第一代从谁算起”；区分家族代际、经营者顺序与受访者称谓。'],
 ['E04','南洋茶与本地拼配／口味有关','实践者及机构记载，适用范围有限','P02; P07; A04','P07 Experience of Practitioners；A04 chapter 7待精读','国家非遗网页有拼配和焙制叙述；茶贸易章提供历史问题线索。','支持本地加工；未证明唯一源起','活态遗产／本土化','拍摄经同意的器物与动作；原料、名称、味道改变分别追问。'],
 ['E05','茶具“本土制作”与获准使用Merlion标志不同','部分店方自述可核；制作地仍待核','P01','Tea Man → 2001 Merlion logo段','店史讲2001年获准使用Merlion标志，不足以证明所有器物均在本地制造。','限制等同推论','物质文化／品牌','核器物款识、制造商、采购记录和店方授权材料。'],
 ['E06','NHB与商户共同策展，双方不总是对立','项目设计有直接官方说明','P03','中文页“老店铺文化站”计划介绍','说明文件、照片、器物和策展支持的合作过程；不代表双方对每一细节都一致。','限制简单官民二分','解释权／结论','补访：谁选展品、谁写文字、店方能否修改、未被选入哪些故事。'],
 ['E07','37 Pagoda Street旧址认定保留不确定性','官方表述有明确限定','P04','正文第1段；资料截至2019说明','网页用believed to be而非无保留确认；街头牌文还需现场逐字转录。','支持谨慎措辞','官方标牌分析／公共史站点','保留“被认为是”；对照现场牌署名、日期与网页差异。'],
 ['E08','牛车水不仅有华人实践，也有多种族宗教与空间使用','规划部门与学术问题相互参照','P05; A03; A07','P05 The History、The Legacy；A07 pp. 118–123','规划页直接谈印度教和穆斯林群体；A07讨论族群分类在新加坡的特殊性。','支持多主体范围','历史背景／身份框架','无需新增完整宗教案例；在路线和背景中标明这些使用者，避免空间同质化。'],
 ['E09','更新同时追求文化保护与商业／客流目标','政府计划文本已核；实际效果另查','P09; P10','P09第1–4、7–10段；P10商户反馈','官方目标多重；新闻同时出现部分营业改善和经营压力。','支持复杂目标，限制单向结论','保护／商业／城市更新','按店铺具体变化核实获益与压力；不把个别销量报道写成总体效果。'],
 ['E10','Lau Choy Seng 1948创店有店方时间线','企业自述，待独立记录补核','P11','Company Timeline → 1948、1960s、1993','店方时间线提供录音之外的可追问节点，不证明模糊回答的具体内容。','支持限定事实核验','辅助商户案例','重新提问并核照片；无法辨认处标[听不清]，不补写。'],
 ['E11','1998年前后存在可追溯的公共争论，不能等同当前受访者态度','学术正文可核，原始回应待取得','A10; P13; A02','A10 At the Margins of the Gridlock；P13原书待取得','A10记STB计划与SHS批评；具体引语依赖其二手引文。','支持历史争论；限制时间外推','项目争议背景','通过P13／同期报纸核原文；当前张力用自己的材料分别论证。'],
 ['E12','n=16游客问卷只用于探索受众偏好','用户大纲所述，未审原数据','用户项目大纲','第四部分“游客问卷”','大纲记9人从未到访、12/16偏好图片等、15/16有中英语言需求；未读取问卷原表。','限制总体推断','Public History形式选择','不称代表牛车水游客；展示分母、招募方式和探索性质。'],
 ['E13','建筑保存与活态遗产连续性可以分别观察','理论提出分析工具，非本地实证','A06; P05; P17','A06 pp. 129–133；P05 Architecture／Legacy','社区联系、使用、照管与有形／无形表达提供多个观察维度。','理论参照','比较框架／结论','用店铺和街段材料逐项判断；避免“建筑在=文化在”或“有新店=遗产消失”。'],
 ['E14','壁画、商户展示、展馆与官方标牌应逐项辨认作者','材料来源已分，现场内容待采集','P18; P19; P03; P04','各页面的机构／项目身份与现场署名','可同时属于艺术家、商会推广、馆方策展或NHB合作，不宜合称一种“官方声音”。','方法决定','公共叙事编码','拍每处署名和说明；记录委托、创作、策展与宣传主体是否不同。'],
]

DATABASES=[
 ['D01','NUS Libraries / FindMore / Databases','取得核心学术文献与书籍','逐条复制A01–A15完整题名或DOI；书籍也用ISBN；先查A02、A03、A05。','https://nus.edu.sg/nuslibraries/databases-search','https://nus.edu.sg/nuslibraries/services-help/online-tools','数据库目录及官方远程访问说明已核；未登录用户账号，也未确认单篇订阅。','借不到时使用核心五篇表的替代项；记录版本及页码。'],
 ['D02','NewspaperSG（NLB）','同期报纸、广告、迁址及1998–1999争论','白新春／Pek Sin Choon；广合源／Kwong Hup Yuen；牛车水 保护／Chinatown revitalisation；时间窗1925–1935、1997–1999分别检索。','https://eresources.nlb.gov.sg/newspapers/','','入口可打开；尚未逐条完成报刊检索，部分全文可能有访问地点限制。','记录报刊名、日期、版次、页码及永久链接；中文OCR以影像复核。'],
 ['D03','NAS Archives Online — Oral History','补充居民、劳动与地方记忆','Chinatown；Kreta Ayer；牛车水；NG Pek Fong／吴碧芳／002454（粤语，官方发布目录线索）。','https://www.nas.gov.sg/archivesonline/oral_history_interviews/','https://www.nas.gov.sg/archivesonline/public/Q2_2016_New_Record_Releases.pdf','已核官方发布目录存在该访谈号；未收听原音频或核逐字稿，不能先写结论。','筛出与路线相关的1–2段；记访谈号、卷／段及时间戳；核公开再用许可。'],
 ['D04','NAS Archives Online — Maps and Building Plans','历史地图、店址、城市工程与空间变化','Mosque Street；George Street；New Market Road；Pagoda Street；Smith Street；按搬迁年代分段筛。','https://www.nas.gov.sg/archivesonline/maps_building_plans/','','入口已打开；尚未定位能证明白新春具体搬迁原因的单件档案。','地图可证明位置／形态，未必证明搬迁因果；记录比例尺、制作年、馆藏号。'],
 ['D05','NAS Archives Online — Photographs','历史街景与过去／现在对照','Chinatown；Temple Street；Mosque Street；Pagoda Street；筛同街段、相近拍摄方向。','https://www.nas.gov.sg/archivesonline/photographs/','','检索入口作为后续路线，未把搜索中转引的图片当成已核原件。','每图记拍摄者、日期、馆藏号、可用范围；不要用不同街段照片冒充原址。'],
 ['D06','NLB Curiocity / Spatial Discovery','数字公共史、历史地图与扩展出处','Chinatown；Streets of Chinatown；由地图的references回溯原书、照片或档案。','https://curiocity.nlb.gov.sg/story-maps/historic-districts/','https://reference.nlb.gov.sg/arts/visual-arts/artxstacks/places/','NLB页面与来源说明已核；具体底图或档案仍需逐件确认。','参考其署名和非穷尽说明，重点建立自己的3–5站路线。'],
]

STATIONS=[
 ['R01','37 Pagoda Street／原苦力馆牌','P04; P05; P06; A01','劳动者与移民历史如何被压缩为一块牌？','网页／现场牌文＋同一建筑今天的用途＋历史照片候选。','补拍整牌、署名、语言版本与店面；保存逐字转录；旧址不确定性照录。','如果这栋店屋只讲一个故事，哪些后来住过或工作过的人会被遗漏？'],
 ['R02','36 Mosque Street／白新春','P01; P02; P03; P07; A04; A06','跨区域原料怎样形成地方传统？谁参与展示？','商户声音＋NHB展陈＋茶叶包装／器物＋经核实的迁店时间线。','补访世代、配方命名、旧址与政府工程；录音／照片及署名授权逐项确认。','如果原料来自别处、味道在这里形成，我们会把它叫作哪里的传统？'],
 ['R03','Temple Street／Lau Choy Seng','P11; A01; A13','老字号的延续是否允许产品与顾客改变？','1948及迁址时间线＋今天商品与客户用途＋重新访谈片段。','重录听不清部分；核具体门牌；不以现有模糊录音支撑壁画／政策观点。','一家老店改变了卖的东西和服务对象，哪些联系仍使它成为老字号？'],
 ['R04','Smith Street／壁画与更新','P09; P10; P18; A02; A09','家庭记忆的展示与当代经营如何相遇？','壁画／现场使用照片＋2023更新目标＋2025新闻反馈＋2026观察。','核壁画作者及委托方；照片显示时间、街段和当天用途；不预设施工仍在继续。','谁在为这条街的“活力”下定义：来访者、经营者，还是在这里生活的人？'],
 ['R05','Pagoda Street／原貌馆（可选）','P19; P20; A05; A14','复原生活和仍在发生的生活如何互补？','馆方公开介绍＋实地展览观察（若去）＋相邻街面日常。','网页与实地证据分开；若时间不足仅保留前4站，不增加额外访问负担。','一处复原的房间能让我们理解过去的哪些部分，又有哪些部分需要其他声音？'],
]

SCHEDULE=[
 ['2026-09-17','2026-09-18','取得与筛选核心文献','先用A07/A06开放全文进入主题；通过D01取得A02/A03/A05；无法取得及时换备选。','确定五篇学术文献＋每篇版本／查阅路径','核心五篇；学术文献','优先保证能读到原文，不以资料数量替代阅读。'],
 ['2026-09-19','2026-09-21','精读与五篇注释初稿','每篇记录主张、材料、方法、限制、具体页码和与另两篇的关系。','Annotated bibliography初稿；保留比较综合段','A01–A05及替代项','课程要求2000 words、5 academic sources；网页和新闻不凑入五篇。'],
 ['2026-09-19','2026-09-22','针对性补访与固定路线观察','白新春优先；Lau Choy Seng按需要补录；逐项核E01–E10，拍署名、器物与当前用途。','可引用访谈段／照片清单／授权记录／待核清单','P01–P11；论证与核验；路线材料','与阅读同步；不能按时补访时缩小主张，保留已确认内容。'],
 ['2026-09-22','2026-09-23','完成论证结构与书目综合','比较不同来源中的重合、差异、合作与沉默；区分历史争论和当前观察。','论文详细提纲＋五篇比较段定稿候选','A01–A10；E06/E08/E11/E14','不把观点差异自动升级为明确冲突。'],
 ['2026-09-24','2026-09-26','写Research Essay完整初稿','围绕核心案例组织历史背景、公共展示、商户实践和更新；每个关键事实带出处。','4000 words完整初稿及引文表','学术文献；一手与机构资料','大纲中的“字”与课程的words不同，最终按课程要求计量。'],
 ['2026-09-26','2026-09-28','完成Public History作品','以3–5站双语图文路线制作可演示版本；每站来源、商户声音、变化和开放问题。','2000 words公共史文本或10分钟视频；形式按已获老师认可方案落实','路线材料；P06/P18–P20；A14','小程序／地图若作载体，也应覆盖课程的文字或视频内容要求。'],
 ['2026-09-29','2026-09-30','交叉核查与修订','检查注释书目与论文是否相互支持；核名字、年份、页码、地图范围、语气和授权；检查双语一致。','三项作业可提交版本＋修订记录','论证与核验；资料访问状态','纠正未核事实和泛化，删除无法支持的确定性结论。'],
 ['2026-10-01','2026-10-01','导出与最终检查','打开最终文件／视频；检查链接、图片、字幕、字数、文件名及课程提交说明。','最终文件包与备份','所有成果','这一天作为缓冲，避免10月2日才开始排版。'],
 ['2026-10-02','2026-10-02','按老师要求完成全部内容','以用户告知的10月2日为硬截止；具体提交时刻以课程系统为准。','完成全部项目内容；按课程要求提交','用户最新说明','年份按当前学期推定2026；未替用户执行提交。'],
]

EXCLUSIONS=[
 ['X01','Wikipedia / Reddit / 一般旅游博客','仅用于发现线索，不纳入主文献表','无法替代学术原文、商户原述或官方记录；个别帖子不代表商户整体。'],
 ['X02','Yeoh & Kong “Reading Landscape Meanings” 2017再版章节','与A01去重','保留1994原刊记录，避免同一文章占五篇中的两个名额。'],
 ['X03','泛指伦敦、曼彻斯特、温哥华的Chinatown研究','本轮不扩展','可提供比较，但10月2日前应优先牛车水直接案例和白新春材料。A11仅保留一个新加坡邻近比较。'],
 ['X04','Conservation of Chinatown (Tanjong Pagar): The Impact on Heritage and Identity（NUS论文线索）','不纳入核心','本次未核作者、论文级别和全文；现有直接文献已足以覆盖，避免用未核学位论文凑数。'],
 ['X05','P12及P14旧PDF','保留为待取得线索','直接下载返回404；不能标“已下载”或把搜索摘要当完整原稿。'],
 ['X06','白新春市场占有率及最早／唯一类宣传','不作本项目关键事实','不是核心研究问题，且需独立统计／历史证明；保留叙事角色即可。'],
]

def write_outputs():
 data=dict(snapshot='HY5417_chinatown_20260917_v1',date=TODAY,academic=acad,primary=primary,core=CORE,evidence=EVIDENCE,databases=DATABASES,stations=STATIONS,schedule=SCHEDULE,exclusions=EXCLUSIONS)
 (BASE/'_support/catalogue.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 wb=Workbook(); wb.remove(wb.active)
 navy='183C4A'; teal='157A7C'; light='E8F3F3'; gold='E9B44C'; textc='223640'; gray='F1F4F6'
 default_font='PingFang SC'
 tables=[]
 def sheet(name,title,subtitle,headers,rows,widths,freeze='D6',height=94):
  ws=wb.create_sheet(name);ws.sheet_view.showGridLines=False;ws.sheet_view.zoomScale=85
  n=len(headers)
  ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=n);ws.cell(1,1,title)
  ws.cell(1,1).font=Font(name=default_font,size=20,bold=True,color='FFFFFF');ws.cell(1,1).fill=PatternFill('solid',fgColor=navy);ws.cell(1,1).alignment=Alignment(vertical='center')
  ws.row_dimensions[1].height=40
  ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=n);ws.cell(2,1,subtitle);ws.cell(2,1).font=Font(name=default_font,size=11,color='566870');ws.cell(2,1).alignment=Alignment(wrap_text=True,vertical='center');ws.row_dimensions[2].height=36
  ws.cell(3,1,'↩ 使用说明');ws.cell(3,1).hyperlink="#'使用说明'!A1";ws.cell(3,1).font=Font(name=default_font,size=10,color=teal,underline='single')
  for j,h in enumerate(headers,1):
   c=ws.cell(5,j,h);c.font=Font(name=default_font,bold=True,color='FFFFFF',size=11);c.fill=PatternFill('solid',fgColor=teal);c.alignment=Alignment(wrap_text=True,vertical='center')
  ws.row_dimensions[5].height=31
  for i,row in enumerate(rows,6):
   for j,v in enumerate(row,1):
    c=ws.cell(i,j,v);c.font=Font(name=default_font,size=11,color=textc);c.alignment=Alignment(wrap_text=True,vertical='top');c.fill=PatternFill('solid',fgColor='FFFFFF' if i%2==0 else gray)
    if j==1:c.font=Font(name=default_font,size=11,bold=True,color=teal)
    if isinstance(v,str) and v.startswith(('https://','http://')):
     c.hyperlink=v;c.value='打开链接 ↗';c.font=Font(name=default_font,size=11,color='0563C1',underline='single')
    if isinstance(v,str) and v.startswith('fulltexts/') and v.endswith('.pdf'):
     c.hyperlink=v;c.value='打开本地PDF ↗';c.font=Font(name=default_font,size=11,color='0563C1',underline='single')
   ws.row_dimensions[i].height=height
  for j,w in enumerate(widths,1):ws.column_dimensions[get_column_letter(j)].width=w
  ws.freeze_panes=freeze
  if rows:
   tab=Table(displayName='T'+str(len(tables)+1),ref=f'A5:{get_column_letter(n)}{5+len(rows)}');tab.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showFirstColumn=False,showLastColumn=False,showRowStripes=False,showColumnStripes=False);ws.add_table(tab);tables.append(tab)
  ws.sheet_properties.pageSetUpPr.fitToPage=True
  ws.page_setup.orientation='landscape';ws.page_setup.paperSize=ws.PAPERSIZE_A3;ws.page_setup.fitToWidth=1;ws.page_setup.fitToHeight=0
  ws.print_title_rows='1:5';ws.print_options.horizontalCentered=False
  ws.oddFooter.center.text='HY5417 | 牛车水资料地图 | &P / &N';ws.oddFooter.right.text=TODAY
  ws.sheet_properties.tabColor=teal
  return ws

 intro=[
 ['研究对象','协商中的牛车水：南洋华人传统、新加坡本土化与城市更新中的遗产身份。','以Kreta Ayer及现有田野路线为重点；不写整个新加坡华人通史。'],
 ['本表定位','项目用文献与材料地图，含15项学术文献、20项一手／机构／辅助资料、6个检索入口。','这是经筛选的起步资料包；不声称系统综述或穷尽所有文献。'],
 ['先打开哪张表','先看“五篇核心”，再到“学术文献”点击来源；“论证与核验”决定哪些事实还需补证。','P0＝先读／先查；P1＝优先补充；P2＝需要时才查或尚待取得。'],
 ['核心五篇','A01＋A02＋A03＋A04＋A05，覆盖景观、旅游争议、华人性、茶贸易与遗产理论。','A06/A07/A10为可读的替代或补充；替换时同时改比较段，不机械凑五篇。'],
 ['访问状态','区分已下载全文、公开HTML、仅摘要／目录、机构登录／借阅及旧链接失效。','没有登录NUS或NLB账号；不能保证具体书刊订阅或当前馆藏可借性。'],
 ['导读与证据','中文导读解释“为什么值得读”；只有注明核读全文／段落的内容才经过相应层级检查。','摘要、书目和检索片段不能替代原文阅读；此表不是可直接提交的annotated bibliography。'],
 ['课程交付与截止','课程文件要求：Annotated Bibliography 2000 words（5 academic sources）；Research Essay 4000 words；Public History 2000 words或10分钟视频。','按你最新说明：2026-10-02完成所有内容；不是沿用课程周次推断。具体提交时刻未给出。'],
 ['大纲中的字数','中文项目大纲写“4000字”，但课程大纲写4000 words。','最终按课程指定写作语言与words要求核算；中文大纲用于结构，不能把字数直接等同英文词数。'],
 ['研究立场','比较重合、合作、差异、张力和沉默；只有材料足够时才写明确冲突。','尤其P03共同策展和P10多向经营反馈应进入分析，不只收集符合预设的批评。'],
 ['本地材料','读取了项目大纲和课程大纲；没有读取原访谈、问卷原表或完整田野相册。','E12问卷信息只来自你的大纲；所有需要原音频／原数据确认之处已标明。'],
 ['检索范围','检索日2026-09-17；主题包含牛车水保护／旅游、多种族身份、茶贸易、活态遗产、口述史、公共史；英文＋中文关键词。','采用网页检索、出版社／机构库、官方网页及Crossref；未运行Scopus、WoS或NUS订阅库的穷尽检索。'],
 ['本地附件','fulltexts/保存实际成功下载的PDF；sources/保留检索与下载记录；_support/保存目录数据、重建脚本和校验结果。','PDF为阅读参考；公开网页可读不等于图片／录音可直接公开再使用。'],
 ['日常使用','在学术／机构资料表的“阅读状态”和“个人笔记”中记录进度；表头均可筛选，前列和表头已冻结。','本表无宏、无外部数据连接。点击来源、全文或本地PDF即可查阅。'],
 ]
 sheet('使用说明','HY5417｜牛车水项目文献与材料地图','检索快照：2026-09-17  ·  全部内容完成：2026-10-02  ·  使用前请先看访问状态与核验层级', ['项目','说明','使用提示'],intro,[23,85,85],freeze='B6',height=61)
 core_rows=[]
 for id,role,why,dialogue,fallback in CORE:
  a=next(x for x in acad if x['id']==id);core_rows.append([id,a['authors']+' ('+str(a['year'])+')',a['title'],role,why,dialogue,a['access'],fallback,a['url']])
 ws=sheet('五篇核心','五篇核心学术文献｜选择理由与对话关系','推荐组合用于2000 words annotated bibliography；必须读原文后写摘要、评析和综合段。替代项已列明。', ['编号','作者／年份','原题','承担角色','为什么选它','与其他材料怎样对话','当前访问情况','获取受限时的替代','来源'],core_rows,[9,27,55,28,47,50,36,50,18],height=128)
 # Add a compact synthesis planning row outside the filtered table.
 r=13;ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=9)
 ws.cell(r,1,'综合段写作问题：景观中的意义由谁赋予？旅游开发选择了哪些“华人性”？茶贸易与本地实践如何使传统持续改变？五篇在尺度、年代、材料与解释权上有何不同？先比较证据，再给出你的有限结论。');ws.cell(r,1).font=Font(name=default_font,size=12,bold=True,color=navy);ws.cell(r,1).alignment=Alignment(wrap_text=True,vertical='center');ws.cell(r,1).fill=PatternFill('solid',fgColor=light);ws.row_dimensions[r].height=65

 ah=['编号','优先级','主题','作者','年份','文献原题','完整书目信息','中文导读','对应项目用途','优先阅读位置','使用边界／待核事项','访问状态','本次核验层级','出处／记录','全文／替代入口','DOI／ISBN','本地全文','阅读状态','个人笔记','核验日期','检索记录']
 ar=[[a[k] for k in ['id','priority','theme','authors','year','title','citation','guide','use','locator','limit','access','verified','url','full','identifier','local']]+['未开始','',TODAY,a['trace']] for a in acad]
 aws=sheet('学术文献','学术文献｜15项可用研究与方法读物','按项目相关性排序；书目信息核验与全文阅读分开记录。P0推荐五篇；P1补充；P2选读。',ah,ar,[9,18,24,29,11,58,65,50,50,45,52,38,35,18,19,38,20,18,42,15,35],height=148)
 ph=['编号','优先级','材料类别','作者／机构','日期／年份','资料名称','可用内容','项目用途','证据定位','使用边界／待核事项','访问状态','本次核验层级','来源','替代／相关入口','本地全文','阅读状态','个人笔记','核验日期','检索记录']
 pr=[[p[k] for k in ['id','priority','kind','authors','year','title','guide','use','locator','limit','access','verified','url','full','local']]+['未开始','',TODAY,p['trace']] for p in primary]
 pws=sheet('一手与机构资料','一手、机构与辅助资料｜20项有明确用途的材料','这里的商户自述、官方文本、新闻及灰色文献不能直接替代五篇学术文献；旧链接与未核原稿已单独标识。',ph,pr,[9,18,27,38,24,60,52,49,48,55,43,36,18,19,20,18,42,15,35],height=140)
 for ws,statuscol in [(aws,18),(pws,16)]:
  dv=DataValidation(type='list',formula1='"未开始,已取得全文,阅读中,已做笔记,已引用,暂不使用"');dv.errorTitle='请选择阅读状态';dv.error='请从列表选择，也可在个人笔记中补充原因。';dv.showErrorMessage=True;ws.add_data_validation(dv);dv.add(f'{get_column_letter(statuscol)}6:{get_column_letter(statuscol)}{ws.max_row}')
  ws.conditional_formatting.add(f'{get_column_letter(statuscol)}6:{get_column_letter(statuscol)}{ws.max_row}',FormulaRule(formula=[f'{get_column_letter(statuscol)}6="已引用"'],fill=PatternFill('solid',fgColor='D9EEDC')))

 sheet('论证与核验','论证与事实核验｜哪些能说、哪些还需要补证','每行把具体主张、材料定位和下一步连起来；“已核”仅指所标层级，不代表对所有相关史实完成独立验证。', ['核验编号','问题／拟用主张','当前证据状态','关联资料','具体定位','目前能支持什么','证据方向','放入哪部分','下一步与推荐措辞'],EVIDENCE,[10,45,37,25,48,58,28,28,61],height=126)
 sheet('资料库与检索','资料库与检索入口｜6条后续查证路线','入口不是已完成的档案检索；先解决白新春迁址、同期争论与可复用图片这几项具体问题。', ['编号','资料库／入口','能找什么','可直接复制的检索词／办法','入口链接','帮助／线索链接','本次验证与访问限制','取得后应记录'],DATABASES,[10,42,36,72,18,18,59,54],height=119)
 sheet('公共史路线材料','Public History｜3–5站资料对应表','这是资料如何转化为公众叙事的建议；保持大纲的多声部原则。路线实际通行、店址、拍摄与引用许可需在田野中确认。', ['站点','位置','关联资料','这一站研究什么','可并置的材料','尚需补充','可给公众的开放问题'],STATIONS,[10,42,37,45,57,61,58],height=116)
 schedule_rows=[[datetime.date.fromisoformat(r[0]),datetime.date.fromisoformat(r[1])]+r[2:]+['未开始'] for r in SCHEDULE]
 sws=sheet('截止前安排','阅读与取材安排｜在10月2日前完成项目','按当前日期2026-09-17安排；阅读、补访和原型部分并行。9月30日形成可提交版本，10月1日留作缓冲。', ['开始','结束','阶段','具体行动','应产出','所用资料','注意事项','完成状态'],schedule_rows,[16,16,32,78,60,40,64,18],freeze='D6',height=88)
 for row in sws.iter_rows(min_row=6,max_row=sws.max_row,min_col=1,max_col=2):
  for c in row:c.number_format='yyyy-mm-dd'
 dv=DataValidation(type='list',formula1='"未开始,进行中,已完成,需调整"');sws.add_data_validation(dv);dv.add(f'H6:H{sws.max_row}')
 log=json.loads((BASE/'sources/web_search_log.json').read_text()) if (BASE/'sources/web_search_log.json').exists() else []
 if (BASE/'sources/final_metadata_query.json').exists(): log.append(json.loads((BASE/'sources/final_metadata_query.json').read_text()))
 searchrows=[]
 for entry in log:
  args=entry['args']; queries=args.get('search_query',[])
  for n,q in enumerate(queries,1):
   searchrows.append([entry['id']+f'.{n}',TODAY,'公开网页搜索',q['q'],'; '.join(q.get('domains',[])) or '未限制域名','部分覆盖：仅返回可见排名结果，无总命中数与完整分页','sources/final_metadata_query.json' if entry['id']=='S11' else 'sources/web_search_log.json', '用于发现，原文／机构记录另核'])
  if not queries:
   ops=[]
   for op in ['open','click','find']:
    for x in args.get(op,[]):ops.append(op+': '+str(x))
   searchrows.append([entry['id'],TODAY,'页面／原文核验','\n'.join(ops),'已发现的具体来源','部分页面抓取失败或仅返回摘要；逐条状态见目录','sources/web_search_log.json','直接阅读与失败记录均保留'])
 sheet('检索记录','检索边界与核验记录','确切查询保存在本表及sources/web_search_log.json；搜索引擎未提供稳定总命中数，本表不虚构检索数量或声称穷尽。', ['批次','日期','渠道','原始检索式／操作','域名／范围','完成边界','本地记录','用途'],searchrows,[12,16,25,100,58,56,43,39],height=80)
 sheet('筛选与缺口','筛选决定与剩余缺口','为10月2日截止控制阅读量；保留不利或相反材料，排除未经核验的泛化信息。', ['编号','候选／问题','处理','理由／后续'],EXCLUSIONS,[10,78,44,100],freeze='B6',height=77)
 # Link source IDs throughout the workbook to their source row.
 locations={a['id']:('学术文献',i+6) for i,a in enumerate(acad)}|{p['id']:('一手与机构资料',i+6) for i,p in enumerate(primary)}
 for ws in wb:
  for row in ws.iter_rows(min_row=6):
   c=row[0]
   if c.value in locations and ws.title not in ['学术文献','一手与机构资料']:
    name,r=locations[c.value];c.hyperlink=f"#'{name}'!A{r}"
 wb.active=0
 wb.properties.title='HY5417 牛车水项目文献与资料地图'
 wb.properties.subject='Contested heritage; Chinatown; Nanyang tea; Public History'
 wb.properties.creator='HY5417 project research support'
 wb.properties.description='Verified catalogue with access levels, source roles, evidence limits, and reading schedule. Snapshot 2026-09-17.'
 out=BASE/'HY5417_牛车水项目_文献与资料总表.xlsx';wb.save(out)
 # Verification uses the actual saved workbook, hyperlinks and referenced PDF files.
 check=load_workbook(out);ids=[a['id'] for a in acad]+[p['id'] for p in primary]
 errors=[]
 if len(ids)!=len(set(ids)):errors.append('duplicate IDs')
 dois=[a['identifier'].split(';')[0].lower() for a in acad if a['identifier'].startswith('10.')]
 if len(dois)!=len(set(dois)):errors.append('duplicate DOI')
 metadata_checked=[]
 for a in acad:
  mf=BASE/'sources'/('crossref_'+a['id']+'.json')
  if mf.exists():
   m=json.loads(mf.read_text())['message']
   if m.get('DOI','').lower()!=a['identifier'].split(';')[0].lower():errors.append('DOI metadata mismatch '+a['id'])
   parts=m.get('published-print',m.get('published',{})).get('date-parts',[[None]])[0]
   if parts[0]!=a['year']:errors.append('year metadata mismatch '+a['id'])
   if m.get('page') and m['page'].replace('-', '–') not in a['citation']:errors.append('page metadata mismatch '+a['id'])
   for author in m.get('author',[]):
    if author.get('family','') not in a['authors']:errors.append('author metadata mismatch '+a['id'])
   metadata_checked.append(a['id'])
 for a in acad+primary:
  if a['local'] and not (BASE/a['local']).is_file():errors.append('missing local '+a['id'])
  if not a['url'].startswith('https://'):errors.append('invalid source URL '+a['id'])
 for ws in check:
  if ws.freeze_panes is None: errors.append('no freeze '+ws.title)
  for row in ws:
   for c in row:
    if isinstance(c.value,str) and ('cite' in c.value or '\ufffd' in c.value):errors.append('invalid characters '+ws.title+str(c.coordinate))
    if c.hyperlink and c.hyperlink.target.startswith('fulltexts/') and not (BASE/c.hyperlink.target).exists():errors.append('broken pdf '+str(c.coordinate))
 localfiles=[]
 for p in sorted((BASE/'fulltexts').glob('*.pdf')):
  import fitz
  doc=fitz.open(p)
  localfiles.append(dict(path=str(p.relative_to(BASE)),pages=len(doc),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 qa=dict(status='PASS' if not errors else 'FAIL',errors=errors,workbook=out.name,sheets=check.sheetnames,academic=len(acad),primary=len(primary),database_routes=len(DATABASES),crossref_metadata_checked=metadata_checked,pdfs=localfiles,core=[x[0] for x in CORE],snapshot=TODAY,scope='Metadata and access levels audited; abstract-only sources remain explicitly marked. Not a full-text review of every item.')
 (BASE/'_support/validation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
 print(json.dumps(qa,ensure_ascii=False,indent=2))
 if errors:raise SystemExit(1)

if __name__=='__main__':write_outputs()
