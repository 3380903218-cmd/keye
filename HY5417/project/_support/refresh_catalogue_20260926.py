"""One-off, deterministic catalogue revision from the archived 2026-09-17 snapshot."""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parents[1]
d = json.loads((BASE/'_support/archive/20260917/catalogue.json').read_text())
d.update(snapshot='HY5417_chinatown_20260926_v2', date='2026-09-26', deadline='2026-10-02', deadline_scope='文献综述／五篇学术文献注释书目；不推定研究论文及公共史作品同日截止')
by = {a['id']:a for a in d['academic']+d['primary']}
for a in by.values():
    a['checked_date']='2026-09-17'
    a['reading_status']='未开始'
    a['notes']=''
for id in ['A01','A04','A10','P14','P15']:
    by[id]['checked_date']='2026-09-26'
    by[id]['trace'] += '; sources/refresh_20260926.json'
by['A01']['access']='SMU机构库标示acceptedVersion并提供Download；本轮自动下载失败，可手动尝试或经NUS查DOI'
by['A01']['verified']='2026-09-26复核机构库作者、卷页、摘要、版本及许可；未取得全文'
by['A04']['full']='https://www.ssoar.info/ssoar/bitstream/document/31509/1/ssoar-2011-heng_et_al-Singapore_in_global_history.pdf'
by['A04']['access']='出版社及JSTOR标为开放获取；新增SSOAR整书PDF入口，手动打开后读第7章；未下载到本地'
by['A04']['verified']='核对出版社目录、JSTOR及SSOAR整书封面索引；未核读完整章节'
by['A04']['locator']='第7章，印刷pp. 135–150；SSOAR提供整书，PDF页序可能有封面偏移，以印刷页码为准。'
by['A10']['access']='出版社HTML正文可读；已有及本轮网页返回均包含新加坡相关正文；未下载PDF'
by['A10']['verified']='已核出版社书目信息与新加坡相关正文；本轮复核入口'
by['P14']['priority']='P2 待取得'
by['P14']['url']='https://www.nhb.gov.sg/-/media/nhb/files/media/releases/2025/media-release---celebrating-heritage-practitioners-and-nurturing-youth-stewards-at-the-stewards-of-ich-award-2024.pdf'
by['P14']['full']='https://www.nhb.gov.sg/what-we-do/our-work/sector-development/heritage-businesses/sg-heritage-business-registry/chinatown/pek-sin-choon-pte-ltd'
by['P14']['access']='原新闻稿旧PDF曾返回404；相关商户名录本轮触发网页验证；保留为待取得线索'
by['P14']['verified']='沿用既有官方检索索引记录；2026-09-26确认相关名录未能读取正文；不称已核原稿'
by['P14']['limit']='原新闻稿与相关商户名录是两份材料，不可混用题名和URL。原稿未取得，奖项细节仍需复核；获奖也不能证明代表性。'
by['P15']['year']='2026-05-18'
by['P15']['verified']='2026-09-26核读网页正文、署名、日期及茶贸易／白新春段落'
by['P15']['locator']='Early Tea Trade Networks；Not a Storm in a Teacup；文末注释23–33。网页日期18 May 2026；卷期标识见URL。'
by['P15']['use']='作为进入茶贸易与本地拼配史的导读，并沿注释回溯A04及原始报刊；不能代替五篇学术文献。'

def add(id, **kw):
    rec=dict(id=id, priority='P1 优先补充', local='', checked_date='2026-09-26', reading_status='未开始', notes='', trace='sources/refresh_20260926.json; sources/refresh_metadata_20260926.json')
    rec.update(kw); d['academic'].append(rec); by[id]=rec
add('A16', theme='老人记忆／怀旧／地方经验', authors='Thomas A. Lowe; Lucas Puah; Zoe Jane-Lara Hildon', year=2026,
    title='“Bring back the culture!”: An exploration of the relationship between cultural heritage, nostalgia and older adult subjective wellbeing in Singapore’s Chinatown',
    citation='Lowe, Thomas A., Lucas Puah, and Zoe Jane-Lara Hildon. 2026. “Bring Back the Culture!”: An Exploration of the Relationship between Cultural Heritage, Nostalgia and Older Adult Subjective Wellbeing in Singapore’s Chinatown. Wellbeing, Space and Society 10: 100349. https://doi.org/10.1016/j.wss.2026.100349. [作者全名待以原文首页再核]',
    guide='2026年直接研究牛车水的开放获取文章。出版社摘要说明使用社区焦点小组及反思性主题分析，讨论老人对文化变化的怀旧、失落和延续愿望。',
    use='补足既有商户／游客视角之外的老人声音；将“文化消失”的感受作为记忆叙事分析，而非直接当成客观衰退指标。',
    locator='先读摘要；取得全文后核Methods中的人数、年龄、招募地点及时间，再读主题分析与局限。文章编号100349不是页码。',
    limit='本轮只核出版社摘要和开放获取标识，未读方法全文；作者来自ResearchGate及Crossref转录记录，需首页复核。不能替代本项目当代访谈，也不能将焦点小组外推到全体居民。',
    url='https://www.sciencedirect.com/science/article/pii/S2666558126000072', full='https://doi.org/10.1016/j.wss.2026.100349',
    access='出版社索引标示Open access；自动全文抓取403，浏览器手动访问待确认；未下载',
    verified='核出版社索引中的题名、期刊、卷年、DOI、摘要及OA标识；作者顺序由两项辅助记录交叉核，原文首页待核',
    identifier='10.1016/j.wss.2026.100349')
add('A17', theme='建筑保护／参与／遗产过程', authors='Xintong Wei; Haoming Zhou; Nikhil Joshi; Muyuan Tang', year=2024,
    title='Beyond Preservation: Heritage as an Educational Practice Process at 141 Neil Road, Singapore',
    citation='Wei, Xintong, Haoming Zhou, Nikhil Joshi, and Muyuan Tang. 2024. “Beyond Preservation: Heritage as an Educational Practice Process at 141 Neil Road, Singapore.” Buildings 14 (5): 1225. https://doi.org/10.3390/buildings14051225.',
    guide='以尼路141号建筑保护实验室为案例，将修缮、功能转换、教学及社区参与视为遗产持续形成的过程。',
    use='回应课程的built heritage要求；与商户案例比较不同的持续使用方式，并提供保护与变化相容的材料，避免只收集破坏叙事。',
    locator='第1节研究范围；第4节案例背景；第5节实践过程；第6–7节讨论与结论；图1区分Blair Plain与Chinatown范围。',
    limit='案例在Blair Plain保护区，不能直接代表Kreta Ayer。建筑实验室与商业茶庄的资源、功能和参与机制不同；描述性案例不证明普遍因果效果。',
    url='https://www.mdpi.com/2075-5309/14/5/1225', full='https://doi.org/10.3390/buildings14051225',
    access='开放获取HTML及PDF入口；通过DOI成功读取出版社正文，直链曾限流；未下载PDF',
    verified='已核出版社完整作者、日期、卷期、文章编号与DOI，并核读相关正文；非逐页精读', identifier='10.3390/buildings14051225')

translations=[
'解读景观意义：新加坡牛车水的国家建构与生活经验',
'吸引游客到新加坡牛车水：保护与推广的案例研究',
'新加坡牛车水的华人性：多种族遗产地的春节庆典',
'跨区域商业与国家政治的互动：中国事件对福建—新加坡茶贸易网络的影响，1920—1960',
'遗产的运用', '过去在当下：活态遗产路径——希腊迈泰奥拉',
'新加坡牛车水：多种族城市中的国家建设与遗产旅游',
'全球背景下的遗产空间：新加坡牛车水案例',
'唐人街是地方还是空间？新加坡牛车水案例研究',
'历史与遗产之间：后殖民主义、全球化与马六甲、槟城和新加坡的重塑',
'新加坡小印度：作为争议景观的旅游景点', '重新思考旅游体验中的真实性',
'路易吉·特拉斯图利之死及其他故事：口述史的形式与意义',
'共享的权威：口述史与公共史实践及意义论集',
'“新唐人街”：新加坡新近中国移民的种族化',
'“把文化带回来！”：新加坡牛车水的文化遗产、怀旧与老年人主观福祉',
'超越保存：新加坡尼路141号作为教育实践过程的遗产']
for a,t in zip(d['academic'],translations): a['title_zh']=t
core_ids=['A07','A02','A03','A04','A06']
for a in d['academic']:
    if a['id'] in core_ids: a['priority']='P0 核心候选'
    elif a['id'] in ['A01','A05']: a['priority']='P1 理论／经典补充'
d['core']=[
['A07','总体框架：牛车水、国家建设与多种族性','本地已有全文，可先建立街区背景及“谁定义遗产”的问题。','与A02比较历史／旅游尺度；与A03比较多种族与华人性。','若偏重国家规划与居民日常，可改用A01；A01/A07有作者与材料重叠，五篇中优先二选一。'],
['A02','历史争论：保护与旅游推广','直接回应牛车水旅游开发与保护张力，最贴近课程争议主题。','与A07建立历史脉络；与P09/P10对照早期争论和近期更新。','9月27日前取不到全文，换已可读HTML的A10；比较重点相应转为城市空间与国家／市民关系。'],
['A03','身份：华人性与多种族国家','拆开华人文化、国家身份与节庆展示，避免“中国／新加坡”二选一。','与A04比较符号展示和跨境贸易实践；检查二者时间与材料不同。','通过NUS查Brill章节；取不到可用A17改为“参与式保护”，但须在综合段说明身份维度证据变弱。'],
['A04','商户历史：福建—新加坡茶贸易','把白新春微观案例放进迁移和商业网络，追踪本土化的历史过程。','与P15沿引文链互查；与A06比较跨区域变化和连续性。','先试SSOAR整书PDF的第7章、JSTOR或出版社OA入口；不能用非学术商户网页顶替此学术名额。'],
['A06','理论：活态遗产与社区连续性','本地已有全文；围绕持续使用、技艺与社区关系讨论保护。','与A04比较传统如何适应；与A02讨论保护何物、为谁保护。','重点读第4及14章；若选A05代替，理论中心改为授权遗产话语和解释权。'],
]
d['open_route']=['A07','A10','A04','A06','A17']
d['schedule']=[
['2026-09-26','2026-09-26','先建立问题与阅读地图','读A07引言／结论及A06第4、14章；浏览五篇核心和比较矩阵。','明确综述主线及五篇候选','A07；A06；综述比较矩阵','暂不要求写完研究论文或公共史作品。'],
['2026-09-27','2026-09-27','取得五篇全文并锁定版本','经NUS尝试A02/A03；打开A04整书第7章。受限即按核心表替换，不等到最后一天。','五篇实际能阅读的全文或完整HTML','核心五篇；资料库D01','全文优先备选为A07＋A10＋A04＋A06＋A17；A04仍需手动确认入口。'],
['2026-09-28','2026-09-29','精读并填写注释书目记录','每篇记研究问题、材料／方法、核心论点、局限、与另两篇的关系及引文页码。','五篇阅读笔记和注释初稿','注释书目记录；学术文献','五篇各约320 words为可选分配，共约1600；不是老师新增规定。'],
['2026-09-30','2026-09-30','写比较与综合段','围绕解释权、持续使用和变迁比较文献；说明研究尺度、年代、证据差异及本项目可检验的问题。','综合段约300 words；引入约100 words；合计约2000 words','综述比较矩阵；五篇核心','此为工作分配建议；最终计数及格式按老师说明。'],
['2026-10-01','2026-10-01','核对引文与论证','核书目、版本、具体页码与语气；检查五篇均为学术来源，且不是同文再版重复。','完整注释书目及综合段的修订稿','完整书目；个人阅读记录','摘要与本表导读不能当作已读全文的文献评析。'],
['2026-10-02','2026-10-02','完成文献综述内容','按老师要求完成／提交相关内容；具体时刻以课程通知为准。','本次文献综述成果','用户本次说明','只确认文献综述截止；Research Essay及Public History未获同日截止信息。']
]
d['comparison']=[
['M01','谁有权定义牛车水？','A01；A07；A05；A10','地方景观经验、遗产话语与城市政治','区分规划／机构、商户、居民、游客；检查合作和差异。','不同年代和研究尺度不等同；“官方”和“民间”内部也有差异。','理论框架、公共叙事；对读P03共同策展','谁选择展品、谁写说明、商户能否修改？','提问／比较框架；非已完成综述结论'],
['M02','旅游保护保存了什么？','A02；A07；A08；A09；A10','旅游推广、历史地方与泛化文化符号','比较建筑、商业活动、社区关系及游客体验分别如何被重视。','摘要可提出阅读问题；是否方法充分及样本偏差须读全文。','城市更新章；对读P05/P09/P10','今日更新是否让某些实践受益、另一些承压？','历史争论可追溯；2026影响需田野'],
['M03','华人／南洋／新加坡身份如何相连？','A03；A04；A07；A15','节庆呈现与移民／贸易／本地实践','比较文化符号与材料流动两种形成地方身份的方式。','A04研究1920–1960贸易；A03研究庆典，两者不能互作现状证明。A15地点需核。','身份框架、白新春案例；P01/P02/P07/P15','原料、配方、口味和名称分别在哪里、何时发生变化？','跨文献比较建议；细节须原文'],
['M04','变化是否必然破坏遗产？','A06；A04；A17；A05','活态连续性、文化过程、参与保护','比较维持原用途与重新赋予用途的不同路径。','宗教社区、建筑实验室和商业茶庄的主体与资源不同；A17在Blair Plain。','商户实践、建筑保护、结论；P03/P17','迁店或改配方后，什么关系和实践继续存在？','保留适应、合作材料，防止只找破坏'],
['M05','谁的记忆较少被呈现？','A13；A14；A16；A07','口述史、共同解释、老人怀旧','将可核的事件、讲述方式与情感意义分开。','A16目前仅摘要；小样本不代表全体居民，老人视角也不代表商户。','方法及公共史后续；P04/P18/P19/P20','标牌与壁画遗漏了哪些生活经验？如何保留不同来源署名？','方法阅读候选；不预先推定遗漏原因']
]
d['exclusions'].extend([
['X07','2026老人怀旧研究A16','保留补充，不列必选五篇','题名、DOI、卷年和摘要已核；全文方法与作者首页尚待核，不能凭摘要制作正式评注。'],
['X08','尼路141号A17','纳入比较／开放获取替代','与built heritage直接相关，但在Blair Plain；明确其比较角色，不扩展主田野范围。'],
['X09','本轮未重新打开的既有记录','沿用2026-09-17核验日期','不把表格更新日期冒充每条来源的重新核验日期；保留旧检索与访问记录。'],
['X10','2026-10-02全部项目截止说法','纠正','用户只要求此日完成文献综述；旧表研究论文及公共史同期截止的安排删除。']
])
d['evidence'].append(['E15','建筑继续使用可形成新的遗产意义','A17相关正文已核；不等同牛车水整体','A17；A06','A17第1、4–7节及图1','可比较保护中的使用、教学和参与；不能证明所有改造都有益。','支持适应路径，限制负面单线叙事','建筑保护／结论','对照茶庄功能和参与者；说明Blair Plain案例与Kreta Ayer主田野的范围差异。'])
d['databases'][0][3]='复制学术文献完整题名或DOI；A02查Tourism Management；A03查Brill章节；A05查电子书或纸本。先读可直接获得的A07/A06/A10。'
d['review_contract']={
 'stance':'面向课程的精选证据地图与阅读计划，不是已完成的系统综述或五篇评注正文',
 'scope':'新加坡牛车水，侧重Kreta Ayer与白新春；英文及中文；学术期刊／学术书章／理论专著另列一手、机构和辅助资料；经典研究至2026-09-26可检索资料',
 'inclusion':'直接讨论牛车水遗产与身份，或为茶贸易、活态遗产、口述史／公共史提供明确分析工具；资料必须有可追溯出处',
 'exclusion':'无稳定出处、同文重复、纯旅游推荐、无关城市案例；无全文材料保留但标阅读限制',
 'sources':'继承出版社、大学机构库、NLB/NHB/URA、商户及Crossref记录；本轮用web搜索和页面工具补核；未登录NUS订阅数据库',
 'limits':'网页搜索无稳定总命中数；不是穷尽检索。Parallel/Perplexity专用依赖或密钥不可用，采用可用web工具；本轮无新增PDF下载。',
 'reused':'15篇学术文献、20项机构／一手／辅助资料、3个本地PDF及原检索记录',
 'delta':'新增A16/A17；更新A01/A04/A10访问记录、P14链接角色及P15；调整五篇组合、比较矩阵及截止安排'
}
(BASE/'_support/catalogue.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
print('Updated catalogue:',len(d['academic']),'academic;',len(d['primary']),'primary/other')
