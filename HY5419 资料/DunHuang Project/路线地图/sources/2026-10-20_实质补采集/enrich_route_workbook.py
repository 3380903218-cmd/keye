from pathlib import Path
import csv, json, hashlib, re
from urllib.parse import quote
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[2]
COLLECT = Path(__file__).resolve().parent
OUT = ROOT / '敦煌项目_路线地图资料与制作指南.xlsx'
BASE = COLLECT / '原始工作表_补采集前.xlsx'
EXPORT = ROOT / '地图导入数据'
EXPORT.mkdir(exist_ok=True)
wb = load_workbook(BASE)
DATE = '2026-10-20'
RUC = 'http://iqh.ruc.edu.cn/old/jssxwhsyj/wbydyzygx/zlgxypj/008fc7fe609449428944b45de683c9de.htm'
QIN = 'https://www.zjujournals.com/soc/CN/article/downloadArticleFile.do?attachType=PDF&id=11967'
RUINS = 'https://dsr.nii.ac.jp/toyobunko/VIII-5-B2-8/V-2/'
def page(n):
    scans={339:'0521',350:'0532',376:'0584',377:'0587',435:'0687',438:'0692',484:'0770',485:'0771',488:'0774',490:'0776'}
    return RUINS+'page/'+scans[n]+'.html.en'
def data(name):
    s=wb[name];h=[c.value for c in s[1]]
    return [dict(zip(h,r)) for r in list(s.values)[1:]]
def put(name, headers, rows):
    if name in wb: del wb[name]
    s=wb.create_sheet(name);s.append(headers)
    for row in rows:
        s.append([row.get(h) for h in headers] if isinstance(row,dict) else list(row))
    return s
def update_record(rows, key, value, fields):
    d=next(d for d in rows if d[key]==value);d.update(fields);return d

# Preserve every original PlaceId. Modern reference points are explicit spatial proxies.
places=data('03_地点与坐标');ph=list(places[0])
for d in places:
    d['DefaultUse']=bool(d.get('Longitude') is not None)
    d['ReferenceFor']=''
update_record(places,'PlaceId','PL_MOGAO',{'LabelEN':'Mogao Caves (site reference)','适用年代与语境':'现代遗址参考点；关联1907–1908活动','Longitude':94.8042114,'Latitude':40.0373163,'坐标条目ID':'OSM node 512563307 v12','来源ID':'R09；S03','来源URL':'https://api.openstreetmap.org/api/0.6/node/512563307.json','定位精度／方法':'OSM遗址标注点；不代表洞窟或帐篷实测位置','地图状态':'可导入遗址参考点','使用限制／待补内容':'与UNESCO、Getty及旧图索引存在位置差异，见16；第16、17、130窟及两营地保留独立PlaceId和空坐标。','DefaultUse':True})
update_record(places,'PlaceId','PL_ANXI',{'LabelEN':'Anxi (historical town; exact site unresolved)','原名／异名':'An-hsi；安西州城；今渊泉／瓜州相关异名','来源ID':'R01；R10；R11','来源URL':'https://dsr.nii.ac.jp/digital-maps/stein/place-names/00269.html.en','适用年代与语境':'1907年知州衙门存放、10月寺院住宿处接收','地图状态':'地名有索引；历史城址未精定位','使用限制／待补内容':'NII 00269（图幅38.3.D）与GeoNames渊泉1529004坐标不同。区域示意另用PL_ANXI_REF，不将现代县城点当衙门或寺院。'})
update_record(places,'PlaceId','PL_BM_HIST',{'使用限制／待补内容':'机构寄存有据；R06关于先存自然史博物馆、后迁BM地下室的线索未读全文，不升级为已核事实。另列PL_BM_REF建筑参考点。','来源ID':'S07；S17；R01；R06'})
update_record(places,'PlaceId','PL_BN_HIST',{'使用限制／待补内容':'另列PL_BNF_REF（Richelieu现代场址参考），未证明1909年具体交接发生在该门址。不能采用Tolbiac现代馆址代替。'})

def addplace(pid,zh,en,aliases,kind,context,period,lon,lat,authority,sid,url,precision,state,note,default=False,ref=''):
    places.append(dict(zip(ph,[pid,zh,en,aliases,kind,context,period,lon,lat,'EPSG:4326' if lon is not None else '',authority,sid,url,precision,state,note])) | {'DefaultUse':default,'ReferenceFor':ref})
citydata=[
 ('PL_ANXI_REF','渊泉／瓜州（安西区域参考）','Yuanquan / Anxi (regional reference)','An-hsi；Anxi；Guazhou；Yuanquan',95.8,40.5,'1529004','yuanquan','PL_ANXI'),
 ('PL_HAMI','哈密（城市参考）','Hami (city reference)','Hāmi；Hami',93.50601,42.83393,'1529484','hami',''),
 ('PL_SHANSHAN','鄯善（城市参考）','Shanshan (city reference)','Pichan；鄯善',90.20463,42.86750,'1529214','shanshan',''),
 ('PL_TURPAN','吐鲁番（城市参考）','Turpan (city reference)','Turfan；吐鲁番',89.17886,42.94769,'1529114','turpan',''),
 ('PL_YANQI','焉耆（城市参考）','Yanqi / Karashahr (city reference)','Karashahr；焉耆',86.57185,42.06321,'1529031','yanqi',''),
 ('PL_LUNTAI','轮台（城市参考）','Luntai / Bugur (city reference)','Bugur；轮台',84.27049,41.77953,'1529333','luntai',''),
 ('PL_KUCHA','库车（城市参考）','Kucha / Kuqa (city reference)','Kuqa；Kucha；现条目Xincheng',82.93249,41.71497,'1529363','xincheng',''),
 ('PL_LANZHOU','兰州（城市参考）','Lanzhou (city reference)','兰州；Lanzhou',103.83987,36.05701,'1804430','lanzhou',''),
 ('PL_ZHENGZHOU','郑州（城市参考）','Zhengzhou (city reference)','Tcheng-tcheou；郑州',113.64861,34.75778,'1784658','zhengzhou',''),
 ('PL_SHANGHAI','上海（城市参考）','Shanghai (city reference)','Chang-haï；上海',121.45806,31.22222,'1796236','shanghai',''),
 ('PL_XIAN','西安（城市参考）',"Xi’an (city reference)",'Si-ngan-fou；西安',108.92861,34.25833,'1790630','xi-an',''),
]
for pid,zh,en,al,lon,lat,gid,slug,ref in citydata:
    note='现代城市／镇参考点；历史城门、旅舍和装箱处未定位。'
    if ref:note+=' 只代理安西区域，用于小比例尺示意；不代表历史城址已核。'
    if pid=='PL_LANZHOU':note+=' 对应1909-10-05电报目的地，另用于伯希和考察队主批区域行程；不证明1909年清代样本从兰州发出。'
    addplace(pid,zh,en,al,'现代城市／镇参考',None,'现代参考；1907–1909事件位置另见12',lon,lat,'GeoNames '+gid,'R11','https://www.geonames.org/'+gid+'/'+slug+'.html','城市／区域级；历史误差未量化','可导入区域参考',note,True,ref)
hist=[
 ('PL_HONGLIUYUAN','红柳园（安西支）','Hung-liu-yuan (Anxi branch)','Hung-liu-yüan of An-hsi；不与01597混同','01596','1907-10-09','Anxi支条目；旧图索引坐标不直接作现代实测点。'),
 ('PL_XINGXINGXIA','星星峡','Xingxingxia / Hsing-hsing-hsia','猩猩峡；Hsing-hsing-hsia','01557','1907-10-12','原文拼作猩猩峡；仅核历史站名。'),
 ('PL_KUSHUI','苦水驿（哈密支）','Kushui (Hami branch)','K’u-shui of Hāmi；不采用肃州同名条目','02816','1907-10-14','信件写信地可核；驿站建筑位置尚未精定位。'),
 ('PL_SANJOU','Sanjou／桑株区域','Sanjou / Sanju','Sanjou；Sanju；桑株','03814','1908-08-01发往此地','R05 p438发运目的地；旧图索引Sanju为绿洲，不等于山口03817。'),
 ('PL_SANJU_PASS','桑株山口','Sanju Pass','Sanju-dawān；Sanju Pass','03817','1908-09-27前通过','R05 p484回述文物驮队已越过该山口；具体通过日未定。'),
]
for pid,zh,en,al,index,period,note in hist:
    addplace(pid,zh,en,al,'历史路线地点；坐标未采用',None,period,None,None,'NII Stein Gazetteer '+index,'R01；R05；R10','https://dsr.nii.ac.jp/digital-maps/stein/place-names/'+index+'.html.en','旧图索引已查；尚未与现代位置完成配准','有路线文字；暂不绘精确点',note+' 候选经纬见16，CRS和旧图误差未核。')
for args in [
 ('PL_PORTASH','Portash（历史中转点）','Portash (unlocated)','Portash','1908-09-27前文物到达','R05 p484；NII按Portash检索未命中；不据相似音译补坐标。'),
 ('PL_KASHMIR','克什米尔（运输地域）','Kashmir (transport region)','Kashmir','1908年10月叙述语境','R05 p488指文物正由Lal Singh运往Kashmir；不自动改成斯坦因11月13日到达的Srinagar市点。'),
 ('PL_SIXNATIONS','六国饭店（1909宴会地点）','Six Nations Hotel (1909 banquet; unlocated)','六国饭店；Hôtel des Six Nations','1909-10-04晚','R04印刷45页／PDF2据两位与会者日记核地点和日期；未采现代酒店替代坐标。'),
 ('PL_ANXI_YAMEN','安西知州衙门（存放处）','Anxi magistrate’s yamen (unlocated)','安西知州衙门','1907-06-15起存放','R01开头六月叙述；12箱密封存放。旧址未核，不与十月寺院住宿处合并。'),
]:
    pid,zh,en,al,period,note=args
    addplace(pid,zh,en,al,'历史场所／地域', 'PL_BEIJING' if pid=='PL_SIXNATIONS' else ('PL_ANXI' if pid=='PL_ANXI_YAMEN' else None),period,None,None,'','R04' if pid=='PL_SIXNATIONS' else ('R01' if pid=='PL_ANXI_YAMEN' else 'R05'),QIN if pid=='PL_SIXNATIONS' else (RUC if pid=='PL_ANXI_YAMEN' else page(484 if pid=='PL_PORTASH' else 488)),'场所／地域有据；确址未知','只在区域层表达',note)
venue=[
 ('PL_BM_REF','英国博物馆（建筑参考）','British Museum (premises reference)',-0.1267051,51.5193118,'relation/177044','PL_LONDON','PL_BM_HIST'),
 ('PL_NHM_REF','自然史博物馆（待核线索）','Natural History Museum (candidate venue)',-0.1760019,51.4965109,'way/24436446','PL_LONDON',''),
 ('PL_BNF_REF','法国国家图书馆Richelieu（场址参考）','BnF Richelieu (premises reference)',2.3381642,48.8672823,'relation/545655','PL_PARIS','PL_BN_HIST'),
 ('PL_GUANGHUASI_REF','广化寺（1910接收场址待核）','Guanghua Temple (candidate venue)',116.3846060,39.9398918,'way/929752805','PL_BEIJING','PL_JINGSHI'),
]
for pid,zh,en,lon,lat,osm,context,ref in venue:
    addplace(pid,zh,en,en,'现代建筑参考／历史候选',context,'现代坐标；1909–1910事件对应未核',lon,lat,'OSM '+osm,'R09','https://www.openstreetmap.org/'+osm,'建筑标注／中心参考；非交接房间','候选层；默认关闭','现代建筑位置查询成功，但当年具体交接／整理行动与此址的对应仍待证。',False,ref)
put('03_地点与坐标',ph+['DefaultUse','ReferenceFor'],places)
P={d['PlaceId']:d for d in places}

# Retain original event records and add research results without overwriting their raw status.
events=data('04_事件梳理');eh=list(events[0])
for e in events:e.update({'本轮补采集结果':'沿用既有记录；未发现足以改变本行属性的新证据。','本轮证据ID':'','推荐地图参考PlaceId':''})
revisions={
 'DH001':('R01记6月7–11日将前两次所获合装12箱（1–12号），6月12日出发、15日存安西衙门；是后续存放，不改首次取得计数。','C001;C002','PL_MOGAO'),
 'DH002':('补出6月装箱与安西存放；数量口径与既有研究不同，保留原20／13捆及R01叙述，不据此覆盖。','C001;C002','PL_MOGAO'),
 'DH003':('区分10月1日取得、2日驮队出发、4日22时到安西、5日蒋另行归队。新增哈桑·阿洪为驮运参与者；Tila参与卸货。经哈密木箱13–24号，再在和田重装73–88号。','C003;C004;C005;C006;C007;C008','PL_MOGAO;PL_ANXI_REF'),
 'DH004':('R01记1909年1月到伦敦，但不采用其“入藏”措辞替代寄存。R05支持1908年8月1日自和田发运、9月27日前越桑株山口至Portash，后由Lal Singh运向克什米尔。具体抵英港口及收讫建筑仍未核。','C013;C014;C015;C016','PL_LONDON'),
 'KE001':('R05 p435直接记蒋在和田做初步清单；参与者后出记述，与S07不算独立证人。','C017','PL_KHOTAN'),
 'KE005':('发现R08 Lorimer研究和R06博士论文可追英国整理场址；当前只读到元数据／搜索片段，尚未据此提升核验状态。','C020',''),
 'KE009':('补到1909-10-04六国饭店学界宴请这一后续事件；不把宴会当作所有原卷均在场的证据。','C018','PL_BEIJING'),
 'KE010':('R04 p45引恽毓鼎日记记摄影制印；摄影者、底片号和复制品去向仍未核，未另造一条摄影运输路线。','C019','PL_BEIJING'),
 'DH005':('R13记3月3–25日查看选择，5月8日后四天才谈妥所选汉藏文书取得；五月取得语境补强，但逐卷交接、日记原页仍未核。','C029','PL_MOGAO'),
 'DH006':('新增主批郑州→上海铁路运输及Nouette赴法链；R13记考察队74包于1909-01-16已到巴黎，而S15称文献1909年底到巴黎。先区分城市到货、部门接收与主批／留身子集，保留差异。','C025;C026;C027','PL_PARIS'),
 'DH007':('S19三（二）将1909年呈样认定为BD06825／羽025《大般若波罗蜜多经》卷157，依据旧草目样本注记；原件影像仍待核。','C030','PL_BEIJING'),
 'DH009':('S19将续交22卷对应BD06826–BD06847／羽026–047；粘片2本后来拆分编号BD15818–BD15994，共177号。保留原卷数／原册数与后期号数的层次。','C031;C032','PL_BEIJING'),
}
for eid,(finding,claim,ref) in revisions.items():update_record(events,'EventId',eid,{'本轮补采集结果':finding,'本轮证据ID':claim,'推荐地图参考PlaceId':ref})
update_record(events,'EventId','KE009',{'本轮补采集结果':'R13记留身小批写本先示端方等于南京，后示罗振玉于北京，并转引1909-08-19罗致汪康年信。不是主批全部经北京；论文R04另核10月4日宴会。','本轮证据ID':'C018;C028','推荐地图参考PlaceId':'PL_BEIJING'})
for eid,ref in [('DH005','PL_MOGAO'),('DH006','PL_PARIS'),('DH007','PL_BEIJING'),('DH008','PL_BEIJING'),('DH009','PL_BEIJING'),('KE003','PL_KHOTAN'),('KE004','PL_KHOTAN'),('KE006','PL_LONDON')]:update_record(events,'EventId',eid,{'推荐地图参考PlaceId':ref})
def newevent(eid,action,summary,date,place,roles,support,lim,locator,claim,mapref):
    d={h:'' for h in eh};d.update(dict(zip(eh,[eid,'知识传播',action,summary,'','','',date,'day_from_secondary_diary_transcription',1909,1909,place,'区域活动点；场址未精定位','本轮新增；已读论文全文',roles,support,lim,'历史场址／原档影像仍待核',locator,'',''])))
    d.update({'本轮补采集结果':'新增地图研究记录，未修改原Gephi工作簿或其节点／边。','本轮证据ID':claim,'推荐地图参考PlaceId':mapref});events.append(d)
newevent('MAP_KE011','学术宴会／交流','1909年10月4日晚六国饭店宴请伯希和','1909-10-04晚','PL_SIXNATIONS','伯希和、Fredrick McCormick及16位中国与会者；董康、王式通推动','R04据恽毓鼎、江瀚两位与会者日记互证日期、场所与18位名单；王国维在列，罗振玉未出席。','未核原日记影像；不证明原卷在宴会现场；不将所有参会者两两自动连边。','R04：印刷45–47页／PDF2–4','C018','PL_BEIJING')
newevent('MAP_KE012','行政通信／保护指令','1909年10月5日学部电告兰州制台查收存经','1909-10-05','PL_BEIJING;PL_LANZHOU','学部：发出；兰州制台：电文收文对象（实际收讫待核）','R04据学部官报与日记校日期，电文涉及核查、保护、禁止继续外流及送部。','电报目的地域明确，发出具体建筑、实际收讫时刻未核；不是当天实物发运证据。','R04：印刷48页／PDF5；原引《学部官报》宣统元年第12期3页正','C021','PL_BEIJING;PL_LANZHOU')
put('04_事件梳理',eh+['本轮补采集结果','本轮证据ID','推荐地图参考PlaceId'],events)

# Claim-level ledger: read state is explicit; unacquired sources only support leads.
claims=[]
def claim(cid,rel,statement,sid,loc,kind,url,local,limit):
    claims.append([cid,rel,statement,sid,loc,kind,url,str(COLLECT/local) if local else '',limit,DATE])
claim('C001','DH001;DH002;ST001','1907年6月7–11日前两次取得物合装12箱，编号1–12。','R01','开头1907年6月7—11日段；注①：MSS Stein199/81–82','学术机构全文转载；日记转引',RUC,'R01_Wang_2015_RUC_http.txt','原日记影像未取得；不由箱数反推写本件数。')
claim('C002','ST002;ST003','6月12日离开莫高窟，15日到安西，12箱封存知州衙门；6月24日本人离开不等于文物离开。','R01','开头6月15日段及10月14日书信回述','全文研究＋书信转引',RUC,'R01_Wang_2015_RUC_http.txt','衙门具体地址未核。')
claim('C003','DH003;ST005;ST006;ST007','10月1日交易装袋，2日驮队出发，4日22时到安西；蒋赴敦煌县城后5日另返。','R01','10月1–5日逐日段；注20–24','全文研究；按日记转引区分行动',RUC,'R01_Wang_2015_RUC_http.txt','1912游记p339的压缩叙述与此有别；原日记尚未核。')
claim('C004','ST006;ST007','Ibrahim Beg、Hassan Akhun带4峰骆驼运输7大袋；Tila Bai与Ibrahim参与卸货。','R01','10月2日出发与4日晚接收段；注20–24','全文研究／日记转引',RUC,'R01_Wang_2015_RUC_http.txt','230为报告的捆数口径；不是每袋均分。')
claim('C005','ST008;ST009;ST010;ST011;ST012;ST013','安西10月7日将7袋材料分装8只临时箱；8日出发，9日红柳园，12日星星峡，14日苦水，18日哈密。','R01','10月7日包装至10月18日哈密段；注27–31','全文研究；书信写信地与行程叙述',RUC,'R01_Wang_2015_RUC_http.txt','各站精确驿址未核；线几何仍是参考点之间的示意。')
claim('C006','ST014;箱号表','哈密将新增材料装入12只木箱，编号13–24；10月31日逐箱清单。','R01;R05','R01注32：MSS Stein200/53v；R05印刷350／扫描0532','研究转引＋1912参与者游记全文',page(350),'R05_Ruins_printed_350_scan_0532.txt','不能再简化为一直袋装至和田；原日记图像未读。')
claim('C007','箱号表;G03','哈密逐箱转引清单合计193捆汉文、22捆藏文，共215捆；与约230捆不一致。','R01','13–24号箱清单；本表独立算术求和','全文转引清单＋计算',RUC,'R01_Wang_2015_RUC_http.txt','0为清单未列该语言捆，不等于箱中绝无该类文物；绘画、泥塑、陶器不计入捆数。')
claim('C008','ST015–ST020','1907年11月1日离开哈密，依次经鄯善、吐鲁番、焉耆、轮台，1908年1月19日到库车。','R01','哈密清单后运输段','全文研究',RUC,'R01_Wang_2015_RUC_http.txt','中间站到离日未给出，不能按均速补日。')
claim('C009','ST021','1908年1月25日，24峰骆驼的重物驮队由蒋、Tila护送出发去和田；斯坦因另走克里雅河方向。','R01;R05','R05印刷376–377／扫描0584、0587','1912参与者游记全文；研究互参',page(377),'R05_Ruins_printed_377_scan_0587.txt','是文物与人员分路；斯坦因当天／翌日自身出发日叙述有差异，不影响驮队1月25日。')
claim('C010','ST022','从库车来的文物驮队在斯坦因3月26日到和田前已到，存房东Akhun Beg家。','R01','库车分队段后，3月26日前后叙述','全文研究',RUC,'R01_Wang_2015_RUC_http.txt','文物到达日未知；不得用3月26日替代。')
claim('C011','ST023;箱号表','和田7月10日将新增批次101捆装73–79号7箱；7月11日127捆装80–88号9箱。','R01','注33–34：MSS Stein202/89v–90','全文研究；日记转引',RUC,'R01_Wang_2015_RUC_http.txt','16箱228捆为范围对应；不证明哈密某一箱对应和田某一箱。')
claim('C012','ST023;DH004','和田总包装95箱为全部考察物资；其中所述敦煌材料24箱写本、5箱艺术品。','R01','1908年6月19日至7月18日段','全文研究',RUC,'R01_Wang_2015_RUC_http.txt','总箱数包含书籍底版等；打包起日与S03的6月9日不同，见16。')
claim('C013','ST025','1908年8月1日文物重载驮队从和田发往Sanjou，由Tila及Badruddin Khan一名可信商队人员照管。','R05;R01','R05印刷438／扫描0692','1912参与者游记全文',page(438),'R05_Ruins_printed_438.txt','该页对Suget与后续会合使用计划语气；只确认本次发往Sanjou。')
claim('C014','ST026;ST027','1908年9月27日斯坦因到Portash时，文物驮队已越桑株山口安全到达。','R05','印刷484／扫描0770','1912参与者游记全文及页面影像',page(484),'R05_Ruins_printed_484.txt','9月27日是本人见到驮队的日期／到达上限；驮队具体抵达日未知。')
claim('C015','ST028;ST029','Lal Singh负责继续护运文物；安排越喀喇昆仑、再换牦牛过Sasser；后记文物正运往Kashmir。','R05','印刷485、488／扫描0771、0774','1912参与者游记全文',page(488),'R05_Ruins_printed_488.txt','p485为运输安排，p488为运输正进行；不能给文物套用作者10月3日过山口、10月12日到Leh的个人日期。')
claim('C016','ST030;DH004','R01称29箱敦煌文物于1909年1月到伦敦。','R01','和田发运段后，1909年1月叙述','全文研究',RUC,'R01_Wang_2015_RUC_http.txt','月精度；不把1月21日本人到伦敦日当货到日；“入藏”须与S17寄存说明区分。')
claim('C017','KE001','蒋在和田初步列出部分中国写本，并协助识读长城遗址出土汉文。','R05','印刷435／扫描0687','1912参与者游记全文',page(435),'R05_Ruins_printed_435.txt','与S07是同一作者，不作独立证人计数；具体清单原件未找到。')
claim('C018','MAP_KE011','北京学界宴请在1909年10月4日晚六国饭店；据两位与会者日记互证，名单18人。','R04','印刷45–47／PDF2–4','期刊原版PDF全文；已视觉核p45',QIN,'R04_Qin_2018.pdf','未见原日记影像；宴会不证明原卷在场；罗振玉未出席。')
claim('C019','KE010','恽毓鼎日记的引述提及对携来写本摄影制印。','R04','印刷45／PDF2上半及末段','期刊原版PDF全文',QIN,'R04_Qin_2018.pdf','仅证明当时复制活动的记述；具体摄影时间、地点、摄影者与底片去向待核。')
claim('C020','KE005;DH004','R08和R06可追查1909年英国收存与整理场所。','R08;R06','R08元数据；R06搜索片段，未取得全文','仅检索线索；不作为地图事实','https://doi.org/10.1017/S1356186300009986','R08_Wang1998_Cambridge.html','自然史博物馆及1909-08-10迁库说法未核原文，不进入运输路线。')
claim('C021','MAP_KE012','1909年10月5日学部发电兰州制台，要求核查、保护及将存经送部。','R04','印刷48／PDF5；注14及参考文献14','期刊原版PDF全文；已视觉核p48',QIN,'R04_Qin_2018.pdf','核的是电文发出／目的地域，不是文物已发运或电报已收讫。')
claim('C022','地点表','莫高窟采用OSM node512563307的遗址参考点，非单窟位置。','R09','OSM node512563307 v12；2025-08-29更新','公开数据库原始JSON','https://api.openstreetmap.org/api/0.6/node/512563307.json','OSM_Mogao_node_512563307.json','遗址层；Getty、GeoNames同源参考与旧图有偏差；见16。')
claim('C023','地点表','An-hsi有NII00269历史索引；现代Yuanquan1529004列Anxi/An-hsi异名，二者坐标不同。','R10;R11','NII图幅38.3.D；GeoNames详情异名表','历史地图索引＋现代地名数据库','https://www.geonames.org/1529004/yuanquan.html','GN_Yuanquan.txt','现代镇点只作区域代理，不证明历史衙门／寺院确址。')
claim('C024','MAP_KG001;ST004','研究者据1907年9月26日雇马账目推定从安西派信使送购买提议到莫高窟；使者姓名亦为推断。','R01','9月26–28日通信段；注④–⑨','全文研究；账目、日记与书信转引',RUC,'R01_Wang_2015_RUC_http.txt','9月26日为研究者推定的发信日；采用匿名信使，不把张宝作为已核承运人。')
claim('C025','DH005;DH006;ST032–ST034','考察队主批经兰州、西安后，从郑州由铁路发往上海，由Vaillant和Nouette负责。','R13','Pékin-Hanoï, le retour：Mais avant d’aller vers le nord段及开头convoi段','博物馆专题全文；书信／日记转引','https://guimet-photo-pelliot.fr/essais/essai_11.php','R13_Pelliot_Guimet_return.html','主批含敦煌材料和其他购藏；保留的小批写本不随主批自动连线；逐箱清单未核。')
claim('C026','ST035;ST036','1908-12-01伯希和自无锡信称箱子已存上海法租界；Nouette随后携箱赴法，伯希和赴海防。','R13','Pékin-Hanoï, le retour：1 décembre1908书信段，注165及随后段','博物馆专题全文／书信转引','https://guimet-photo-pelliot.fr/essais/essai_11.php','R13_Pelliot_Guimet_return.html','12月1日为已存上海的上限；船名、装船日和法国到港日未核；不把伯希和本人去海防画成主批路线。')
claim('C027','ST037;DH006','专题记考察队74包在1909年1月16日已到巴黎，清关三周后分往Muséum、Louvre及Nouette工作室。','R13','Pékin encore：À ce moment les74colis段','博物馆专题全文；年由1909年上下文落实','https://guimet-photo-pelliot.fr/essais/essai_12.php','R13_Pelliot_Guimet_Beijing.html','74包为全队，不是74箱敦煌写本；未逐箱落实图书馆交接。与S15年底到巴黎叙述的范围／行动差异未消除。')
claim('C028','KE009;KE010','留在伯希和身边的小批写本于1909年先向南京、再向北京学人展示；罗8月19日信提复制与保护呼吁。','R13','Pékin encore：En même temps段及注170','博物馆专题全文；罗振玉书信转引','https://guimet-photo-pelliot.fr/essais/essai_12.php','R13_Pelliot_Guimet_Beijing.html','留身数量估计与旧目录数十件表述不同；不设精确总数。复制请求不等于全部已完成，1911后续不放入1900–1910主图。')
claim('C029','DH005;ST031','查看选择延续3月3–25日；文书交易最终谈妥在5月8日记事后四天。','R13','Dunhuang, la réussite：8 mai段及随后四天句，注148–149','博物馆专题全文；日记转引','https://guimet-photo-pelliot.fr/essais/essai_10.php','R13_Pelliot_Guimet.html','5月12日由文脉计算，尚未核日记原页；本表只提升到5月取得语境，不改为独立核过的精确交接日。')
claim('C030','DH007;O0002','方广锠据旧草目样本注记，将呈样认定为BD06825／羽025《大般若波罗蜜多经》卷157。','S19','三、实物现状（二）样本','复读既有全文转载；原目录转录','https://www.fjdh.cn/wumin/2010/12/071837135094.html','','原卷与旧草目影像尚未本轮读取；它是1909样本及后来返还，不新增两卷。')
claim('C031','DH009;B0007','S19将续交22卷对应BD06826–BD06847（羽026–047），逐卷列题名并讨论后加题记／勘记作伪。','S19','三（三）退还的22卷；四、真伪考辨','既有全文转载；馆藏整理者研究','https://www.fjdh.cn/wumin/2010/12/071837135094.html','','不是整卷全为伪造；转录个别编号有字母误写，保留校录说明。')
claim('C032','DH009;B0007','S19记粘片2本后来揭下修整，编号BD15818–BD15994，总177号。','S19','三（四）粘片2本','既有全文转载；整理者记录','https://www.fjdh.cn/wumin/2010/12/071837135094.html','','177是后期编号数，不得加在1910年的22卷＋2本上当新增到件。')
claim('C033','G06;SG007','高田时雄文回述押运者傅宝华及何震彝宅中转；可作进一步追原文的线索。','R15','印刷186／PDF2左栏','作者公开PDF；相关页视觉读取','https://www.zinbun.kyoto-u.ac.jp/~takata/shingi.pdf','R15_Takata.pdf','本轮未获承运／交接原件，亦未定位私人住宅；不升级为已核私人住宅路线。')
put('11_采集证据',['ClaimId','关联记录','补得的事实／线索','SourceId','页码／段落／档号','证据与阅读状态','SourceURL','本地证据文件','限制与来源依赖','采集日期'],claims)

# Chronology is not automatically a geometry; date bounds never become precise arrival dates.
steps=[]
def step(n,parent,obj,layer,place,start,end,precision,action,actor,caseid,cid,status='已发生（来源所述）',mapping=''):
    steps.append([f'ST{n:03}',parent,obj,layer,place,start,end,precision,action,actor,caseid,cid,status,mapping])
step(1,'DH001;DH002','B0001;B0002','实物流转','PL_MOGAO','1907-06-07','1907-06-11','日范围','包装前两批材料','斯坦因考察队','莫高窟箱1–12','C001',mapping='遗址参考点')
step(2,'DH001;DH002','B0001;B0002','实物流转','PL_MOGAO','1907-06-12','','日','携12箱出发','斯坦因考察队','莫高窟箱1–12','C002',mapping='遗址参考点')
step(3,'DH001;DH002','B0001;B0002','实物流转','PL_ANXI_YAMEN','1907-06-15','','日','到安西并封存；本人6月24日离开而对象留存','斯坦因考察队；安西知州机构','莫高窟箱1–12','C002',mapping='PL_ANXI_REF仅区域代理')
step(4,'DH003','','知识传播','PL_ANXI','1907-09-26','','日（作者据雇马账目推定）','派信使往莫高窟送购买提议','斯坦因；匿名信使；王圆箓','','C024',mapping='PL_ANXI_REF→PL_MOGAO；通信示意；姓名未核')
step(5,'DH003','B0003','实物流转','PL_MOGAO','1907-10-01','','日（研究据日记转引）','追加取得并装为7大袋','蒋孝琬；王圆箓','7袋；约230捆口径','C003;C004',mapping='遗址参考点')
step(6,'DH003','B0003','实物流转','PL_MOGAO','1907-10-02','','日','驮队离开；蒋另赴敦煌县城','Ibrahim Beg；Hassan Akhun；4峰骆驼','7袋','C003;C004',mapping='遗址参考点')
step(7,'DH003','B0003','实物流转','PL_ANXI','1907-10-04','','日；22时到、23时前卸毕','驮队到寺院住宿处卸货；蒋10月5日另返','Ibrahim Beg；Hassan Akhun；Tila Bai卸货','7袋','C003;C004',mapping='PL_ANXI_REF；不是衙门确址')
step(8,'DH003','B0003','实物流转','PL_ANXI','1907-10-07','','日（转引）','临行将大袋材料分放到8只可用箱内','斯坦因考察队','临时8箱；非哈密最终12箱','C005',mapping='PL_ANXI_REF')
step(9,'DH003','B0003','实物流转','PL_ANXI','1907-10-08','','日；11:30','带材料离开安西','斯坦因考察队','临时包装','C005',mapping='PL_ANXI_REF')
step(10,'DH003','B0003','实物流转','PL_HONGLIUYUAN','1907-10-09','','日','途中红柳园；有书信写信地','斯坦因考察队','','C005',mapping='历史地名已查；不输出精确点')
step(11,'DH003','B0003','实物流转','PL_XINGXINGXIA','1907-10-12','','日','途中星星峡','斯坦因考察队','','C005',mapping='历史地名已查；不输出精确点')
step(12,'DH003','B0003','实物流转','PL_KUSHUI','1907-10-14','','日','苦水驿写信，报告所得与包装状态','斯坦因','','C005',mapping='历史地名已查；不输出精确点')
step(13,'DH003','B0003','实物流转','PL_HAMI','1907-10-18','','日','抵达哈密','斯坦因考察队','','C005',mapping='城市参考点')
step(14,'DH003','B0003','实物流转','PL_HAMI','1907-10-23','1907-10-31','包装工作日范围；31日清单','重新装入12只坚固木箱','斯坦因考察队','哈密箱13–24','C006;C007',mapping='城市参考点')
step(15,'DH003','B0003','实物流转','PL_HAMI','1907-11-01','','日','带含新增12箱的队伍出发；另有先前12箱','斯坦因考察队','所述敦煌箱共24箱','C008',mapping='城市参考点')
for n,pid,zh in [(16,'PL_SHANSHAN','鄯善'),(17,'PL_TURPAN','吐鲁番'),(18,'PL_YANQI','焉耆'),(19,'PL_LUNTAI','轮台')]:
    step(n,'DH003','B0003','实物流转',pid,'1907-11-01','1908-01-19','经过日期未知；只知在此区间','运输队经'+zh,'斯坦因考察队','前两批及新增批次同行','C008',mapping='日期字段是界限，不能当驻留期；城市参考点')
step(20,'DH003','B0003','实物流转','PL_KUCHA','1908-01-19','','日','运输队到库车','斯坦因考察队','所述敦煌箱共24箱','C008',mapping='城市参考点')
step(21,'DH003','B0003','实物流转','PL_KUCHA','1908-01-25','','日','重物驮队向和田出发；与斯坦因本人分路','蒋孝琬；Tila Bai；24峰骆驼','含敦煌24箱；不等于24只骆驼只驮敦煌箱','C009',mapping='城市参考点；走和田河床，非克里雅河')
step(22,'DH003;KE001','B0003','实物流转','PL_KHOTAN','','1908-03-26','到达日未知；上限来自本人到达前已在','存放房东Akhun Beg家','蒋孝琬；Tila Bai；Akhun Beg（存放处关联）','库车运输队材料','C010',mapping='城市参考点；03-26不是货物精确到达日')
step(23,'DH003','B0003','实物流转','PL_KHOTAN','1908-07-10','','日（转引）','新增批次101捆装7箱','斯坦因考察队','和田箱73–79','C011',mapping='城市参考点')
step(24,'DH003','B0003','实物流转','PL_KHOTAN','1908-07-11','','日（转引）','新增批次127捆装9箱','斯坦因考察队','和田箱80–88','C011',mapping='城市参考点')
step(25,'DH004','B0004','实物流转','PL_KHOTAN','1908-08-01','','日','发重载文物队往Sanjou','Tila Bai；Badruddin Khan的商队人员','全队文物；B0004为敦煌子集','C013',mapping='起点可绘城市参考；Sanjou精确点未采用')
step(26,'DH004','B0004','实物流转','PL_SANJU_PASS','','1908-09-27','通过日未知；上限','文物驮队已越过桑株山口','Tila Bai及驮队','全队文物；未逐箱收讫','C014',mapping='历史索引点待配准')
step(27,'DH004','B0004','实物流转','PL_PORTASH','','1908-09-27','到达上限；27日本人见到已到驮队','文物驮队已安全到达','Tila Bai；斯坦因见证','未见单箱损伤的参与者报告','C014',mapping='历史地点未定位')
step(28,'DH004','B0004','实物流转','PL_PORTASH','1908-09','','月／安排语境','安排经Kara-koram及Sasser，骆驼后换牦牛','Lal Singh负责护运','约50驼载为全部文物口径','C015','运输安排；逐站到达未证','默认不作已发生线段')
step(29,'DH004','B0004','实物流转','PL_KASHMIR','1908-10','','月（本人在Leh休养的叙述语境）','文物正由Lal Singh运向克什米尔','Lal Singh','全队文物；不逐箱核对','C015',mapping='地域级；不自动转为Leh／Srinagar到达事件')
step(30,'DH004','B0004','实物流转','PL_LONDON','1909-01','','月','所述敦煌文物到伦敦','考察队；接收与承运人待核','29箱口径；对照寄存记录','C016',mapping='城市参考点；港口与接收建筑仍缺')
step(31,'DH005','B0005','实物流转','PL_MOGAO','1908-05','','月；日候选12日由文脉推算','所选汉藏文书交易谈妥','伯希和；王圆箓','逐箱／逐卷清单待核','C029',mapping='遗址参考点；3月查看不当交接日')
step(32,'DH005;DH006','B0005','实物流转','PL_LANZHOU','1908','','年；夏季行程语境','主批运输队经兰州地域','考察队','主批含敦煌及其他材料；留身子集分开','C025',mapping='城市参考点；不是清代样本起点')
step(33,'DH005;DH006','B0005','实物流转','PL_XIAN','1908-09','','月；主批行程／购藏语境','主批队伍经西安并另添购藏','考察队','不将西安购藏均算入敦煌B0005','C025',mapping='城市参考点；逐箱身份未核')
step(34,'DH005;DH006','B0005','实物流转','PL_ZHENGZHOU','1908','','年；秋季语境','主批由郑州铁路发上海','Vaillant；Nouette','考察队主批，敦煌为其子集','C025',mapping='城市参考点；不猜车站地址、车次与发车日')
step(35,'DH005;DH006','B0005','实物流转','PL_SHANGHAI','','1908-12-01','存放上限；不是精确到货日','箱子已存上海法租界','Vaillant；Nouette；伯希和信中回述','考察队主批','C026',mapping='城市参考；法租界内具体库房未知')
step(36,'DH005;DH006','B0005','实物流转','PL_SHANGHAI','1908','','年底发运语境；精确日待核','Nouette携主批箱件赴法；伯希和另赴海防','Nouette','不包括伯希和留身小批','C026',mapping='港口与航线未核；上海至巴黎关系示意')
step(37,'DH006','B0005','实物流转','PL_PARIS','1909-01-16','','日；年份由上下文落实','全队74包已到巴黎；后清关分流','Nouette及接收方','74包为全队，不能称74箱敦煌写本','C027',mapping='城市到货与年底图书馆接收分开；见16冲突')
step(38,'DH006','B0005','实物流转','PL_PARIS','1909','','年底机构接收（S15）；与主批到城日分列','S15所述国立图书馆接收敦煌文书','Bibliothèque nationale','不能将所有74包归给图书馆','C027',mapping='PL_BN_HIST未精定位；不消除来源叙述差异')
put('12_运输与通信节点',['MapStepId','关联EventId','ObjectId','网络层','PlaceId','日期起／下限','日期止／上限','日期含义与精度','行动','人员与角色','箱号／范围','ClaimId','发生／计划状态','地图处理'],steps)

# Packaging is indexed by place and numbering system, never joined on the bare case number.
boxes=[]
counts=[(13,21,0,''),(14,10,7,''),(15,18,0,''),(16,6,10,''),(17,22,0,''),(18,15,0,''),(19,19,0,'另有绘画；未给数量'),(20,15,2,''),(21,19,0,''),(22,20,0,''),(23,15,1,''),(24,13,2,'另有桥子至Ara-tam泥塑、陶器标本；不能均算敦煌')]
for no,zh,ti,note in counts:
    boxes.append([f'PK_HAMI_{no:02}','B0003','PL_HAMI','Hami_1907','1907-10-31',str(no),1,zh,ti,zh+ti,'捆',note or '清单未列其他物品','C006;C007','MSS Stein200/53v（R01注32转引）','此处0只表示转引清单该语言分项未列，不证明该箱绝无该类内容。'])
boxes += [
 ['PK_MOGAO_01_12','B0001;B0002','PL_MOGAO','Mogao_1907','1907-06-07至11','1–12',12,None,None,None,'箱','前两次取得合装；不填单箱捆数','C001','MSS Stein199/81–82（R01注①）','与Hami编号接续不等于后来的Khotan同号箱。'],
 ['PK_KHOTAN_73_79','B0003','PL_KHOTAN','Khotan_1908','1908-07-10','73–79',7,None,None,101,'捆','语言分项未知','C011','MSS Stein202/89v（R01注33）','仅组范围对应，不与哈密单箱一一配对。'],
 ['PK_KHOTAN_80_88','B0003','PL_KHOTAN','Khotan_1908','1908-07-11','80–88',9,None,None,127,'捆','语言分项未知','C011','MSS Stein202/90（R01注34）','两组合计16箱228捆，和约230捆并存。'],
]
put('13_箱号与批次',['PackingId','ObjectId','PlaceId','NumberingSystem','记录日期','箱号／范围','箱数','汉文捆数_清单列项','藏文捆数_清单列项','合计捆数','捆数单位','其他物品／范围','ClaimId','原档线索（尚未读影像）','数量解释'],boxes)

# Map geometry consists of schematic endpoint connections in EPSG:4326.
lines=[]
def line(sid,parent,obj,layer,fr,to,date,claimids,sources,scale,note):
    a,b=P[fr],P[to]
    geom=f"LINESTRING ({a['Longitude']} {a['Latitude']}, {b['Longitude']} {b['Latitude']})"
    lines.append([sid,parent,obj,layer,fr,to,date,claimids,sources,'schematic_flow','EPSG:4326',geom,scale,'城市／区域／遗址参考端点；非实际道路',note])
line('MAP_SG001','DH001;DH002','B0001;B0002','实物流转','PL_MOGAO','PL_ANXI_REF','1907-06-12至15','C001;C002','R01','regional','12箱后续转存；安西仅现代区域代理。')
line('MAP_SG002','DH003','B0003','实物流转','PL_MOGAO','PL_ANXI_REF','1907-10-02至04','C003;C004','R01','regional','Ibrahim、Hassan驮运；不把蒋10月5日归队当货到日。')
line('MAP_SG003','DH003','B0003','实物流转','PL_ANXI_REF','PL_HAMI','1907-10-08至18','C005','R01','regional','已补途经红柳园、星星峡、苦水；这些站的确址未编码在本条几何中，见12。')
for n,fr,to in [(4,'PL_HAMI','PL_SHANSHAN'),(5,'PL_SHANSHAN','PL_TURPAN'),(6,'PL_TURPAN','PL_YANQI'),(7,'PL_YANQI','PL_LUNTAI'),(8,'PL_LUNTAI','PL_KUCHA')]:
    line(f'MAP_SG{n:03}','DH003','B0003','实物流转',fr,to,'1907-11-01至1908-01-19；中间站日未知','C008','R01','regional','来源记驮队经这些地域；现代城市点连线不复原道路或停车建筑。')
line('MAP_SG009','DH003','B0003','实物流转','PL_KUCHA','PL_KHOTAN','1908-01-25发；03-26前已到','C009;C010','R01;R05','regional','文字支持走和田河床；直线不代表河道。本人经克里雅河的路线不移植到本线。')
line('MAP_SG010','DH004','B0004','实物流转','PL_KHOTAN','PL_LONDON','1908-08-01发；1909-01伦敦到达','C013;C014;C015;C016','R01;R05;S07;S17','global_aggregate','总览关系线：文字已补Sanjou、Sanju Pass、Portash与Kashmir；未精定位和未核港口不造中途坐标。此线不与区域段累加计运输次数。')
line('MAP_SG011','DH005;DH006','B0005','实物流转','PL_MOGAO','PL_PARIS','1908取得；1909年底机构接收','','S15;S22','global_aggregate','取得与机构接收集合的汇总关系；不代表全批经过北京，巴黎为城市参考。')
line('MAP_KG001','DH003','','知识传播','PL_ANXI_REF','PL_MOGAO','1907-09-26派信使（据雇马账目推定）','C024','R01','regional','购买提议信传送；载体未获存世编号；匿名信使，返信日未强填。')
line('MAP_KG002','MAP_KE012','','知识传播','PL_BEIJING','PL_LANZHOU','1909-10-05发电','C021','R04','regional','行政通信目的地域；不代表电缆铺设路线，不是文物运输。实际收讫时刻未知。')
for n,fr,to in [(12,'PL_MOGAO','PL_LANZHOU'),(13,'PL_LANZHOU','PL_XIAN'),(14,'PL_XIAN','PL_ZHENGZHOU')]:
    line(f'MAP_SG{n:03}','DH005;DH006','B0005','实物流转',fr,to,'1908年主批行程；逐站货到日未核','C025','R13','regional','主批含敦煌及其他材料；保留的少量写本另行。按考察队主批集合表达，未逐卷匹配；不画成全批经北京。')
line('MAP_SG015','DH005;DH006','B0005','实物流转','PL_ZHENGZHOU','PL_SHANGHAI','1908年；12月1日前已存上海','C025;C026','R13','regional','主批由Vaillant、Nouette负责，铁路运输有记述；直线不复原铁路轨迹、车站或车次。')
line('MAP_SG016','DH006','B0005','实物流转','PL_SHANGHAI','PL_PARIS','1908年底语境发；1909-01-16主批到巴黎','C026;C027','R13','global_aggregate','Nouette护送的考察队主批，含敦煌子集但逐箱未核。上海至法国航路、法国到港及转巴黎铁路未知；不套伯希和本人海防行程。')
lh=['MapSegmentId','关联EventId','ObjectId','网络层','FromReferencePlaceId','ToReferencePlaceId','时间证据','ClaimId','SourceId','GeometryType','CRS','WKT','MapScale','EndpointPrecision','说明']
for row in lines:
    fr,to=P[row[4]],P[row[5]]
    primaryurl=RUC if 'R01' in row[8] else ('https://guimet-photo-pelliot.fr/essais/essai_11.php' if 'R13' in row[8] else (QIN if 'R04' in row[8] else 'https://heritage.bnf.fr/france-chine/paul-pelliot-1878-1945-et-dunhuang'))
    group='Pelliot' if row[2]=='B0005' else ('Qing_administrative_communication' if row[0]=='MAP_KG002' else 'Stein')
    row.extend([fr['LabelEN']+' → '+to['LabelEN'],group,primaryurl])
lh += ['Label','RouteGroup','SourceURL']
put('14_示意线导入',lh,lines)
segs=data('05_移动段待补');sh=list(segs[0])
for s in segs:s.update({'本轮结果':'尚无足够新证据关闭此项；详见06。','参考线ID':''})
update_record(segs,'SegmentId','SG002',{'时间证据':'1907-10-01取得；10-02驮队发；10-04 22时抵安西；蒋10-05另返','人员／机构角色':'蒋谈判；Ibrahim Beg、Hassan Akhun带4峰骆驼运输；Tila参与卸货','TransportMode':'4峰骆驼驮运7大袋（R01转引）','证据状态':'已补行动日、驮运者；具体道路未知','来源与定位':'R01日期逐段／注20–24；R05 p339为压缩回述，不能覆盖日记分日','WKT':lines[1][11],'绘线决定':'只作参考端点示意；安西用PL_ANXI_REF代理','本轮结果':'完成区域级示意所需端点与时间；历史建筑和道路仍缺。','参考线ID':'MAP_SG002'})
update_record(segs,'SegmentId','SG003',{'时间证据':'1907-10-08安西发，18日哈密；11-01哈密发；1908-01-19库车，25日文物驮队发，03-26前到和田','人员／机构角色':'后段蒋、Tila护运；与斯坦因本人分路','TransportMode':'驮队；库车后24峰骆驼为全部重载队口径','证据状态':'已补中转地域与分队、哈密／和田两轮箱号；单箱对应未核','当前可表达什么':'按14分段展示区域关系；12保留未精定位历史站','来源与定位':'R01哈密清单与库车分队段，注32–34；R05 p350、376–377','绘线决定':'采用14的MAP_SG003–009；本行不复制多段几何','解释限制':'哈密已改木箱13–24，再于和田改箱73–88；不是一直袋装至和田。','本轮结果':'运输链得到实质补齐；不等于逐箱实体匹配或真实道路复原。','参考线ID':'MAP_SG003–009'})
update_record(segs,'SegmentId','SG004',{'时间证据':'1908-08-01发重载队往Sanjou；09-27前越Sanju Pass至Portash；1909-01到伦敦（月精度）','人员／机构角色':'Tila等前段；Lal Singh负责后续往Kashmir；收讫与海运承运人未核','TransportMode':'驮运已记；p485骆驼换牦牛为安排；后续cart/rail/mail steamer为计划，缺运单','证据状态':'已补发运、山口／中转点和护运人；港口、船名及最后收讫待核','来源与定位':'R05 p438、484–485、488；R01和田发运及伦敦抵达段','WKT':lines[9][11],'绘线决定':'仅总览关系线；未知中段不拟造道路','本轮结果':'和田后不再全空白；缺口明确缩小到逐站到达、海港／船运及英国收存。','参考线ID':'MAP_SG010'})
update_record(segs,'SegmentId','SG005',{'WKT':lines[10][11],'时间证据':'1908年五月取得语境；1908年底主批上海发；R13记1909-01-16主批到巴黎；S15年底机构接收另列','TransportMode':'郑州→上海铁路；上海赴法船运记述，船名及航路未核','来源与定位':'R13专题Dunhuang／Pékin-Hanoï／Pékin encore；S15接收段；C025–029','绘线决定':'总体线MAP_SG011；主批区域分段12–15与上海→巴黎16可另展示','本轮结果':'补齐主批郑州铁路→上海法租界存放→Nouette赴法；小批留身北京展示分开，逐箱未核。到巴黎日叙述差异见16。','参考线ID':'MAP_SG011;MAP_SG012–016'})
put('05_移动段待补',sh+['本轮结果','参考线ID'],segs)

# Source catalog. Preserve project Sxx/Mxx identifiers; Rxx identify this collection round.
sources=data('07_资料与来源');srch=list(sources[0])
def source(sid,title,kind,year,use,loc,url,local,state,limit):
    sources.append([sid,title,kind,year,use,loc,url,str(COLLECT/local) if local else '',state,limit,DATE])
# Convert the retained dict records before appending list records.
sources=[[d.get(h) for h in srch] for d in sources]
source('R01','王冀青｜斯坦因在安西所获敦煌写本之外流过程研究','敦煌研究2015(6):75–83；人大清史所全文转载','2015（转载2016）','运输日、驮运者、哈密与和田箱号','日期段与注①、20–34；HTML无法逐段对应原刊页','https://dlbs.liberal.ntu.edu.tw/en/search/search_detail.jsp?seq=565999','R01_Wang_2015_RUC_http.html','题录经NTU学术目录核；人大HTTP全文读取成功','转载入口 '+RUC+'；日记原件未读；不能以元数据原刊页范围伪作具体页码。')
source('R03','Brandon Dotson; Lewis Doney｜Conserving Limitless Life','Producing Buddhist Sutras in Ninth-Century Tibet ch.1,27–81','2025（在线2024-12）','英国初期收存、整理的追查线索','DOI 10.1515/9783111569550-003','https://doi.org/10.1515/9783111569550-003','','发现OA入口；请求403／202，未取得全文','搜索片段不作为已核地图事实；非-005章节。')
source('R04','秦桦林｜1909年北京学界公宴伯希和事件补考——兼论王国维与早期敦煌学','浙江大学学报（人文社会科学版）48(3):44–56','2018','六国饭店宴会、与会者、学部电报','印刷45–48／PDF2–5；参考文献14','https://www.zjujournals.com/soc/CN/abstract/abstract11967.shtml','R04_Qin_2018.pdf','期刊PDF13页成功读取；p45、48视觉核查','日记和官报为论文转引，不冒充原档影像；卷号按PDF48卷，索引页面错误不沿用。')
source('R05','M. Aurel Stein｜Ruins of Desert Cathay, vol.II','参与者后出游记；NII东洋文库扫描','1912','哈密装箱、库车分队、和田发运、Portash及Kashmir','p339,350,376–377,435,438,484–485,488；页号索引与图像对应',RUINS,'R05_selected_pages.json','已读指定页OCR；p350、484另核原页影像','同作者S07非独立见证；区别已发生、计划、人走的路线；索引与IIIF序列不能混算页号。')
source('R06','Michelle Ying-Ling Huang｜The reception of Chinese painting in Britain, circa1880–1920: with special reference to Laurence Binyon','PhD, University of St Andrews；DOI10.17630/10023-1020','2010（仓储issued2010-06-24）','英国暂存建筑、迁库日期的待核线索','搜索片段p113注3；原文未取得；题名、作者、日期已核仓储元数据','https://research-repository.st-andrews.ac.uk/handle/10023/1020?show=full','route_collect_search_29.json','公开仓储元数据已读；删节开放版PDF未取得；完整版本永久禁用不访问','更正初查2009年猜测；不将片段所述自然史博物馆或迁库日期当已核事实。')
source('R08','Helen Wang｜Stein’s Recording Angel—Miss F. M. G. Lorimer','JRAS,3rd series8(2):207–228；DOI10.1017/S1356186300009986','1998','英国保管／整理档案线索','元数据与引用；全文待NUS授权访问','https://doi.org/10.1017/S1356186300009986','R08_Wang1998_Cambridge.html','出版社HTML元数据已读；PDF请求返回HTML，未取得PDF','未读正文，不能支持具体运输日期／场所。')
source('R09','OpenStreetMap｜Mogao node512563307及4处建筑Nominatim查询','公开地点数据库；API0.6／Nominatim search','查询2026-10-20','现代遗址点与建筑参考坐标','OSM元素ID、version、原始响应；4次精确机构查询','https://api.openstreetmap.org/api/0.6/node/512563307.json','OSM_institution_queries.json','原始JSON响应已保存；检索参数见OSM_retrieval_contract.json','© OpenStreetMap contributors, ODbL1.0；现代标注不证明历史交接地点。')
source('R10','NII Digital Silk Road｜Stein Gazetteer / Index of Local Names','历史地图地名索引；Innermost Asia图幅','1930书系地图索引；在线查询2026-10-20','历史站名、图幅、同名消歧','An-hsi00269；红柳园01596/01597；苦水02816；Sanju03814/03817','https://dsr.nii.ac.jp/digital-maps/stein/place-names/','gazetteer_selected_places.json','条目与查询响应已保存','网站提示旧图定位会有误差；CRS未明示，候选数值不自动写成WGS84实测点。')
source('R11','GeoNames｜渊泉、哈密、鄯善、吐鲁番、焉耆、轮台、库车、兰州、西安、郑州、上海','现代地名数据库详情与异名','查询2026-10-20','小比例尺城市／区域参考点','固定GeonameId与详情页坐标；库车条目当前主名Xincheng','https://www.geonames.org/','geonames_selected_city_pages.json','目标页面与异名已读取；另存GN_Yuanquan及GN_Pelliot_route_cities.json','© GeoNames, CC BY4.0；城市参考，不表示1907城址或接收建筑。')
source('R12','NUS Libraries｜NUSearch+、中文电子资源、CNKI馆藏入口','校内学术资源发现入口','查询2026-10-20','优先检索原刊全文与英国整理研究','CNKI LINC记录b2144364；使用官方代理登录','https://linc.nus.edu.sg/record=b2144364','NUS_CNKI_record.html','已打开NUS发现页与CNKI；Safari网页读取权限待用户开启','未读取认证后的检索结果，不能据入口存在宣称NUS已检得／已下载全文。')
source('R13','Jean-Pierre Drège｜La mission de Paul Pelliot au Turkestan chinois et en Chine(1906–1909): les clefs d’un succès','Musée Guimet／Rmn-GP专题原文（3节）','2023上线','文书五月取得、郑州→上海主批、Nouette赴法、巴黎主批与北京留身子集','Dunhuang, la réussite；Pékin-Hanoï, le retour；Pékin encore','https://guimet-photo-pelliot.fr/essais/essai_11.php','R13_Pelliot_Guimet_return.html','3节全文已读取并保存HTML／文本；书信日记为作者转引','74包为整个考察队；不能当74箱敦煌写本；与S15到巴黎时间不同；部分日记引文的书目信息显示异常，原版待核。')
source('R14','Catherine Delacour｜AP8392（旧号796）考察队箱件照片目录说明','Musée Guimet摄影档案条目','2023-03-15','照片用途／批次辨识的限制；避免用错示意照片','图号AP8392；拍摄年1909，法国未识别车站；Kommentar段','https://guimet-photo-pelliot.fr/notice/notice.php?id=1530','route_collect_search_32.json','目录全文已读；未下载或再发布照片','条目说照片箱内可能是后来印本／留身写本；地点不明，不能据照片认定1909-01-16主批或巴黎某站；条目西安1909字样与所引1908信不一致。')
source('R15','高田时雄／著；马永平／译｜日藏敦煌遗书的来源与真伪问题','西南民族大学学报（人文社会科学版）2016(11):185–192；作者公开PDF','2016','押运者傅宝华、何宅中转等既往叙述的追查线索','印刷186／PDF2左栏；末页参考文献','https://www.zinbun.kyoto-u.ac.jp/~takata/shingi.pdf','R15_Takata.pdf','公开PDF8页已取得；p186及首页／末页视觉读取','研究回述不替代1910年承运、交接原件；不据此添加私人住宅确址或已核途中线。')
put('07_资料与来源',srch,sources)

# Access tracking states what was actually done, not just recommended searches.
nus=[]
titles=[
 ('NU01','斯坦因在安西所获敦煌写本之外流过程研究','R01','中文论文','已通过NUS发现页打开题名检索及CNKI入口；结果正文未读','已读人大清史所全文转载；原刊PDF待核',RUC),
 ('NU02','Stein’s Recording Angel Miss F M G Lorimer','R08','英文论文','NUS题名检索链接已准备；尚未读取认证检索结果','出版社元数据已读；全文待取','https://doi.org/10.1017/S1356186300009986'),
 ('NU03','Producing Buddhist Sutras in Ninth-Century Tibet','R03','英文专著／章节','NUS题名检索链接已准备；尚未读取认证检索结果','OA入口已发现，下载返回403／202；未读全文','https://uplopen.com/en/chapters/m/10.1515/9783111569550-003'),
 ('NU04','1909年北京学界公宴伯希和事件补考','R04','中文论文','NUS题名检索链接已准备；尚未读取认证检索结果','期刊官网PDF已读，可独立推进',QIN),
 ('NU05','Ruins of Desert Cathay','R05','英文一手游记','NUS题名检索链接已准备；尚未读取认证检索结果','NII公开原页已读',RUINS),
 ('NU06','Paul Pelliot Carnets de route 1906 1908','R13','法文日记版本','NUS题名检索链接已准备；尚未读取认证检索结果','博物馆专题已引日记，原版2008需核对','https://guimet-photo-pelliot.fr/essais/essai_10.php'),
 ('NU07','日藏敦煌遗书的来源与真伪问题','R15','中文论文','NUS题名检索链接已准备；尚未读取认证检索结果','作者京都大学网页PDF已读','https://www.zinbun.kyoto-u.ac.jp/~takata/shingi.pdf'),
]
for uid,title,sid,kind,state,alt,url in titles:
    nus.append([uid,sid,title,kind,'https://nus.summon.serialssolutions.com/search?s.q='+quote(title),'https://linc.nus.edu.sg/record=b2144364' if kind=='中文论文' else 'https://lib.nus.edu.sg/',state,alt,url,'Safari需启用Allow JavaScript from Apple Events；若NUS登录／2FA出现，由用户在官方页完成；不收集密码或验证码。',DATE])
put('15_NUS检索与访问',['QueryId','SourceId','检索题名','资料类型','NUSearch题名检索','官方资源入口','NUS实际访问状态','公开替代／阅读状态','公开入口','下一步权限与验证','日期'],nus)

issues=[
 ['QC01','莫高窟定位','OSM 512563307：40.0373163,94.8042114','Getty7029798／GeoNames1529271约40.0335,94.9192；UNESCO440约40.13333,94.81667；旧图00862约40.0159,94.93001','坐标条目位置／语义不同；Getty、GeoNames可能共用NIMA数据，不作两份独立测量','采用OSM遗址参考点；不采用其余点定位洞窟／帐篷','R09;M11;R10','未解决单窟或营地定位'],
 ['QC02','安西历史城与现代参考','NII00269：40.529990,95.953280；图幅38.3.D','GeoNames1529004渊泉：40.5,95.8；含Anxi、An-hsi异名','历史索引有旧图误差；不能仅凭差值断言城址搬迁','PL_ANXI保留空精确坐标，另建PL_ANXI_REF作区域代理','R10;R11','衙门、寺院及1907城址未精核'],
 ['QC03','哈密捆数','13–24号逐箱列项求和193＋22＝215捆','同期报告约230捆；和田73–88号范围101＋127＝228捆','不同包装与数量口径，原日记及遗漏原因未核','分别保存三组数字；不强制匹配、不拿捆数当卷数','R01;R05','缺15捆原因不能擅定'],
 ['QC04','装箱起日','S03给1908-06-09至07-18','R01给1908-06-19至07-18','原档未逐页核，可能不同工作范围或日期差错','保留冲突；精确引用已给日期的7月10、11日分组','S03;R01','未据二手文改写原档'],
 ['QC05','哈密中间包装','R05 p350明确在哈密已装12木箱','旧汇总只列袋装→和田装箱，易造成一直袋装的印象','阶段缺失','新增哈密13–24箱阶段，后有和田73–88箱；不作单箱对照','R01;R05;S03','8只临时箱／大袋叙述仍需原件细核'],
 ['QC06','物到日与人到日','驮队10月4日晚安西；蒋10月5日另返','1912游记p339将秘书与材料归来压缩合叙','参与者不同时间尺度叙述','按R01日记转引分开；不把10月1日取得写成安西到达','R01;R05','原日记影像待核'],
 ['QC07','和田到达上限','文物在1908-03-26本人到达前已到','本人的3月26日精确到达日','行动主体不同','物到日空、只记不晚于3月26日；不用于计算运时','R01','精确货到日未知'],
 ['QC08','箱号系统','Mogao_1907 1–12；Hami_1907 13–24','Khotan_1908 73–88为新增批次16箱；另有其他箱','重装后编号范围、箱数改变','主键含地点和编号系统；不以裸箱号关联','R01;R05','现存馆藏号逐卷匹配仍缺'],
 ['QC09','寄存与入藏','R01简写大英博物院入藏','S17注61指出相关阶段尚未正式入藏','行为属性不同','DH004继续为physical_deposit；不增正式入藏日期','R01;S17','需正式登记／移交档'],
 ['QC10','英国首个暂存场址','R06片段提自然史博物馆后迁BM','原论文／档案尚未完整读取','搜索线索不是核验事实','PL_NHM_REF仅候选现代建筑点，默认关闭','R06;R08','需NUS或OA全文'],
 ['QC11','宴会日期与名单','R04核1909-10-04、六国饭店、18人','旧文可能1909-09-04、遗漏王国维或误纳罗振玉','历日／抄录和名单差异','以已读论文的两位与会者日记校核结果记录；原日记仍待核','R04','不由参会推原卷在场'],
 ['QC12','运输安排与已发生','p438 Suget为计划；p485 Kara-koram／Sasser换畜为安排','p484已越Sanju Pass至Portash；p488正运向Kashmir','证据语气不同','只将后者记为已发生；计划单列ST028，不绘为已核路径','R05','不拿斯坦因本人过关／抵达日套货物'],
 ['QC13','R04题录','PDF为2018年48卷3期，44–56页','期刊目录页误显示4卷或缺结束页','数据库显示不一致','按原刊PDF首页／末页，13页核对','R04','DOI按PDF首页10.3785/j.issn.1008-942X.CN33-6000/C.2018.02.051'],
 ['QC14','伯希和主批到巴黎与部门接收','R13记主批74包于1909-01-16已到巴黎，后三周清关分往Muséum、Louvre、Nouette工作室','S15称文献1909年底到巴黎，BnF接收敦煌写本','主批／留身子集、到城／部门接收可能混述；尚无逐箱清单对照','保留两来源原范围；不将全队74包或1月到城日写成BnF全批入藏日','R13;S15','需查1909年1月与年底两次到货／接收登记'],
 ['QC15','AP8392照片能证明哪批箱','专题将照片与74包到巴黎叙述并置','照片目录仅定1909年、法国未识别车站，认为可能是后来印本／留身写本箱','影像批次与地点的目录解释有不确定性','本轮不据该照片给主批定箱号、车站和具体日；不下载再发布照片','R13;R14','需要底片背记与运输／清关清单匹配'],
 ['QC16','清代押运者与私人中转','R15 p186称押运者傅宝华、何宅中转；S19也回述相关事件','尚未获得同期承运单、交接原件、住宅地址与收讫凭证','转引叙述的证据层级不足以还原具体路段','留作人名与档案检索线索；不加已核住宅点／道路','R15;S19','可追原文参考文献，再核原档'],
 ['QC17','S19编号转录','第12项标题写JSD06837','同篇四、勘记列表写BD06837，且羽037、邻号连续','转载字母转录差异','18表保留原写JSD06837并采用BD06837为待核规范号；不隐去校录','S19','需要国图目录／影像复核该条'],
]
for pid,lat,lon in [('PL_HONGLIUYUAN',41.05965,95.54802),('PL_XINGXINGXIA',41.790043,95.21042),('PL_KUSHUI',42.04533,94.58066),('PL_SANJOU',37.192574,78.51028),('PL_SANJU_PASS',36.631363,78.47265)]:
    issues.append(['CAND_'+pid,pid,f'NII旧图索引候选：Latitude={lat}, Longitude={lon}','CRS未明示；未经本轮配准','来源已查但现代定位误差未核','仅留候选；不进入默认点位CSV和线几何','R10',P[pid]['来源URL']])
put('16_矛盾与未决',['IssueId','问题','记录A','记录B／参照','差异性质','本表处理决定','SourceId','尚缺／补充'],issues)

# Close tasks with concrete collection results and leave only genuinely unresolved components.
tasks=data('06_优先补采集');th=list(tasks[0])
taskresults={
 'G01':('部分完成','莫高窟遗址参考点已核；S03的窟前帐篷和Cave130营地分开保存。','R09;S03;C022','单窟、两营地确址、摄影／平面图配准仍缺。','03;09;16'),
 'G02':('区域参考已完成；确址未定','已查An-hsi00269图幅38.3.D与渊泉1529004异名；同名／坐标差异明示。','R10;R11;C023','1907城址、知州衙门及寺院需历史图精定位。','03;16'),
 'G03':('实质补齐包装链；逐件未定','新增哈密13–24号逐箱清单；和田73–79＝101捆、80–88＝127捆；拆开两编号系统。','R01;R05;C001;C006;C007;C011','原日记影像、单箱重装对应与现藏写本号仍缺。','13;16'),
 'G04':('实质补齐；最后航运仍缺','8月1日发Sanjou，9月27日前过Sanju Pass至Portash，Lal Singh续运向Kashmir；1909年1月伦敦。','R01;R05;C013–C016','逐站货到日、海港、船名、运单与收讫原件；不以个人行程代替。','12;14'),
 'G05':('现代参照完成；历史交接未定','BM、NHM、BnF Richelieu、广化寺现代OSM点已查，但均作为候选；英国暂存线索另列。','R09;R06;R08','英国整理研究全文与三机构历史接收记录。','03;15;16'),
 'G06':('补齐馆藏号与通信；原运单仍缺','新增样本BD06825、续交22卷BD06826–06847及粘片后期177号对应；电报1909-10-05；傅宝华为研究回述中的追档人名。','S19;S11;R04;R15;C021;C030–033','清代实际承运、途中、原档影像和私宅地址仍缺；兰州不可代样本出发地。','04;11;14;18'),
 'G07':('主批运输与知识活动实质补齐','新增郑州铁路→上海法租界→Nouette赴法与巴黎74包；小批留身写本先南京、后北京展示；10月4日宴会核日。','R04;R13;C018;C025–029','逐卷箱号、船名与BnF接收登记仍缺；1909年1月到城与年底接收叙述分列。','04;11;12;14;16'),
 'G08':('原记述已保留；关键证据仍缺','S07的秋1910送寄仍为待核；本轮无足够新材料补寄出地、到件和归还。','S07','须查Stein–Pelliot通信、清单、寄件和归还记录。','04;05'),
 'G09':('部分完成；新增有两端通信','已有列单／笔记活动；新增1907安西→莫高窟购买信、1909北京→兰州电报。','R01;R04;R05;C017;C024;C021','照片R0001、备忘录W001和索引W002实际发送接收链仍未闭合。','11;12;14'),
 'G10':('资料入口与使用边界完成','NII图幅／页号索引可追；现代背景与历史地图分开。','R05;R10;M08;M17','本轮未生成配准底图或假称误差值；若使用旧图需另做配准。','07;16'),
 'G11':('默认参考点已完成','17个默认城市／遗址参考点具公开来源；另4个建筑候选默认关闭；历史索引候选不冒充WGS84。','R09;R10;R11;M12–M16','洞窟／营地和交接房间坐标仍空；候选坐标独立保存。','03;09;16'),
 'G12':('非当前采集阻断项','本地Excel与CSV已可用于QGIS；未代用户注册StoryMaps账号。','M01–M05','需要网页发布时再验证账号功能；与NUS学术资料读取权限区分。','02;08;15'),
}
for t in tasks:
    state,result,src,remaining,where=taskresults[t['任务ID']]
    t.update({'本轮完成状态':state,'实际补得内容':result,'补采集证据':src,'仍缺什么':remaining,'结果位置':where,'更新日期':DATE})
    if t['任务ID']=='G11':t['怎么摘录／查找']='本轮17个默认点均为现代城市／遗址参考；每点保存ID、CRS、来源和历史适用边界。'
put('06_优先补采集',th+['本轮完成状态','实际补得内容','补采集证据','仍缺什么','结果位置','更新日期'],tasks)

# Ready-to-import points deliberately contain only adopted site/city references.
pointheaders=['PlaceId','Label','LabelZH','Longitude','Latitude','CRS','PointRole','Precision','SourceURL','Note','MapUse','AuthorityId','ReferenceFor','SourceId']
pointrows=[];candidatepoints=[]
for p in places:
    if p['Longitude'] is None:continue
    row=[p['PlaceId'],p['LabelEN'],p['中文名称'],p['Longitude'],p['Latitude'],'EPSG:4326',p['空间类型'],p['定位精度／方法'],p['来源URL'],p['使用限制／待补内容'],'reference_default' if p['DefaultUse'] else 'candidate_off',p['坐标条目ID'],p['ReferenceFor'],p['来源ID']]
    (pointrows if p['DefaultUse'] else candidatepoints).append(row)
put('09_点位导入',pointheaders,pointrows)

# Event points use regional proxies and keep intent/unverified records out of the default layer.
epheaders=['EventId','Label','LabelZH','MapPlaceId','Longitude','Latitude','LocationPrecision','DateText','Layer','ObjectId','SourceLocator','ClaimId','Note']
eventpoints=[]
for e in events:
    refs=e.get('推荐地图参考PlaceId','') or ''
    if not refs:continue
    if e['EventId'] in ['MAP_KE012']:continue  # represented by communication endpoints below
    for pid in refs.split(';'):
        p=P[pid]
        if p['Longitude'] is None:continue
        en={'MAP_KE011':'Scholarly banquet for Pelliot (1909-10-04)'}.get(e['EventId'],e['EventId']+' at '+p['LabelEN'])
        eventpoints.append([e['EventId'],en,e['地图事件摘要'],pid,p['Longitude'],p['Latitude'],'区域／遗址参考；确切活动场址见04',e['原日期与历法'],e['网络层'],e['ObjectId'],e['来源与页码'],e.get('本轮证据ID',''),e['原证据限制']])
put('17_活动点导入',epheaders,eventpoints)

# Object identifiers: original project batches remain intact; these keys are local catalog links.
fangpath=ROOT.parent/'文献/文献综述/extracted/L03_Fang_2009.txt'
fang=fangpath.read_text()
objrows=[['QING_SAMPLE_BD06825','O0002','DH007;DH009','BD06825','羽025','084:2412','大般若波罗蜜多经 卷157','样本；后来返还，同一卷','C030','S19 三（二）样本','研究者据旧草目注记识别；未读原卷／目录影像','样本返还不计新增取得。']]
matches=list(re.finditer(r'(?m)^\s*(\d{1,2})\s+([A-Z]+\d{5})[（(]([^\n]+)',fang))
assert len(matches)==22
for i,m in enumerate(matches):
    rawid=m.group(2);num=int(m.group(1));norm='BD'+rawid[-5:]
    block=fang[m.end():matches[i+1].start() if i+1<len(matches) else fang.find('判定这22卷',m.end())]
    title=re.search(r'《([^》]+)》([^，。,\n]*)',block)
    title=(title.group(1)+' '+title.group(2)).strip() if title else '题名待核'
    old=re.search(r'羽\d+',m.group(3)).group(0)
    micro=re.sub(r'^.*?[，,]','',m.group(3)).strip(')）').replace('；',':').replace('：',':')
    note='研究讨论的是后加题记／勘记作伪，不能说整卷写本均为伪造。'
    if rawid!=norm:note+=' 此项标题原写'+rawid+'，同篇后文作'+norm+'；原写与规范候选均保留。'
    objrows.append(['QING_SUPP_'+norm,'B0007','DH009',norm,old,micro,title,'续交22卷之一；逐件对应为研究者判断','C031',f'S19 三（三）第{num}项；标题原写{rawid}','未读本轮国图目录／原卷影像；不声称完成独立馆藏核验',note])
objrows.append(['QING_GLUED_FRAGMENTS','B0007','DH009','BD15818–BD15994','粘片原2本','','题名不一；后期揭裱残片','原2本；后期177个编号，不是1910年到件177卷','C032','S19 三（四）粘片2本','后期编号范围为研究转引；未逐号查图','不与原22卷＋2本相加；范围内编号数177。'])
put('18_对象与馆藏号',['LocalObjectKey','项目ObjectId','EventId','规范馆藏号／候选','旧号','缩微号_转录','题名_转录规范','身份与单位','ClaimId','SourceLocator','本轮核验层级','注意事项'],objrows)

# Update instructions so no obsolete 'only five points / all WKT empty' assertions survive.
intro=[
 ['项目目标','1900–1910年敦煌文献实物流转与知识传播；本轮完成实质补采集。','资料截止2026-10-20；地图为来源约束下的表达。'],
 ['本轮成果',f'{len(events)}条事件（保留原20条＋2条新增地图记录）；{len(places)}条地点记录；{len(steps)}条运输／通信节点；{len(claims)}条证据条目；15条包装记录；24条对象／馆藏号对应。','原始事件工作簿、Gephi文件未改动；原Excel备份保存在sources/2026-10-20_实质补采集。'],
 ['可直接导入',f'09有{len(pointrows)}个默认城市／遗址参考点；14有{len(lines)}条示意线；17有{len(eventpoints)}条事件点记录。','地图导入数据/已另存UTF-8 CSV及GeoJSON；无需手动从Excel导出。'],
 ['重要新证据','斯坦因安西—哈密—库车—和田与山口后续节点；伯希和主批郑州—上海—赴法；六国饭店宴会、学部电报；清代样本与续交卷馆藏号。','先看11证据→12节点→13箱号／18馆藏号；14只编码已采用参考端点。'],
 ['线的含义','14的GeometryType全部为schematic_flow：端点之间的流转／通信关系示意。','未复原实际道路、河道、航线或电缆；不得据这些线的长度算历史运距。'],
 ['尺度与重复','regional供区域图，global_aggregate供总览；汇总线与细分段是同一过程的不同尺度。',f'切勿把14的{len(lines)}条显示线当作{len(lines)}次独立交易；不与12的节点数累加作流转次数。'],
 ['点的含义','现代城市或遗址位置作为区域参考，坐标为WGS84／EPSG:4326，经度X在前。','PL_ANXI_REF只代理安西地域；不是1907衙门／寺院坐标；建筑候选CSV默认关闭。'],
 ['知识传播','已有和田列单／笔记、伦敦查看、北京展示／摄影；新增购买信与行政电报的跨地域关系。','宴会不证明写本在场；通信不等于当天实物发运；意向和待核活动不进入默认点层。'],
 ['日期精度','12独立注明发生日、区间、上限和计划；1908-03-26只是文物到和田的上限；9月27日是Portash到达上限。','中间站时间区间不是驻留期；不得据上下限算精确运时；DH009保留清历。'],
 ['数量与编号','哈密清单215捆、报告约230捆、和田重装228捆并存；箱号含地点与编号系统。','不能自动一箱对一箱；箱、捆、卷、件、绘画、照片不可混作同一权重。'],
 ['来源状态','R01人大清史所全文、R04期刊PDF、R05 NII游记指定页、R13博物馆专题全文、R15公开论文及复读S19已用；Sxx沿用项目来源，Rxx本轮新增。','日记、官报多为研究转引；没有冒充档案原件已读。11逐项列页码／段落及限制。'],
 ['NUS访问','已优先打开NUSearch与官方CNKI入口；此前Safari网页读取权限未启用，用户表示正在设置，尚未收到完成回复。','15记录实际访问状态；未把检索链接当作已读NUS全文。R03、R06、R08和R13日记原版仍为明确待读项。'],
 ['未决范围','历史单窟／营地、安西确址、伦敦收存建筑、清代主批解运、伯希和逐卷与1910送寄归还未全部核定。','06已有逐项完成结果，16记录矛盾；未知保持空值，不填0或虚构坐标。'],
 ['文件与复核','本表为静态研究快照；sources/2026-10-20_实质补采集/保存查询、全文、原响应、生成脚本与校验报告。','导入数据也为本次快照，编辑03／04后应同步重导。'],
]
for s in sorted(wb.sheetnames):
    if s!='00_开始使用':intro.append(['打开工作表',s,'点击中间单元格跳转；首行固定、可筛选。'])
put('00_开始使用',['项目','说明','下一步／边界'],intro)
instructions=data('08_制作步骤')
for d in instructions:
    if d['步骤']=='02':d['具体做法']='先看06实际补得结果与16未决项；可直接用已交付CSV试图，再针对研究问题补原件。'
    if d['步骤']=='03':d['具体做法']='直接使用地图导入数据/地点_默认参考点.csv，或从09另存CSV UTF-8。';d['本项目核查点']=f'{len(pointrows)}个城市／遗址参考点；不是历史营地或收存建筑实测。'
    if d['步骤']=='06':d['具体做法']='使用实物流转_示意线.csv或知识传播_示意线.csv；导入时选择WKT列。';d['本项目核查点']='全部为流转关系示意；使用虚线，保留MapScale与说明。';d['使用哪张表']='14'
    if d['步骤']=='10':d['具体做法']='导入已交付CSV；几何定义选WKT，字段WKT，类型LineString，CRS为EPSG:4326；按MapScale筛选区域图／总览图。';d['本项目核查点']=f'{len(lines)}条线均为示意关系，不能转称已核道路路径。';d['使用哪张表']='14'
    if d['步骤']=='09':d['本项目核查点']='默认点与建筑候选分文件；候选不当作已核收存位置。'
put('08_制作步骤',list(instructions[0]),instructions)
legend=data('10_图例与核查');lgh=list(legend[0])
update_record(legend,'图层／核查项','现代参考点',{'本项目例子':f'09的{len(pointrows)}个默认城市／遗址参考点；另4建筑候选在独立CSV。'})
update_record(legend,'图层／核查项','历史场址已核',{'本项目例子':'莫高窟已有遗址参考点；六国饭店有文字定位但未采精确坐标；仍无历史房间／营地实测点。'})
update_record(legend,'图层／核查项','端点关系示意',{'本项目例子':f'14共{len(lines)}条，分实物{sum(r[3]=="实物流转" for r in lines)}条、知识2条；按regional／global_aggregate选择尺度。'})
put('10_图例与核查',lgh,legend)

# Presentation and hyperlinks, all table ranges rebuilt after expansion.
for idx,name in enumerate(sorted(wb.sheetnames)):
    s=wb[name];s.freeze_panes='B2';s.sheet_view.showGridLines=False
    for key in list(s.tables):del s.tables[key]
    if s.max_row>1:
        tab=Table(displayName='RouteData'+str(idx),ref=f'A1:{get_column_letter(s.max_column)}{s.max_row}')
        tab.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True);s.add_table(tab)
    for c in s[1]:c.fill=PatternFill('solid',fgColor='17365D');c.font=Font(name='Aptos',bold=True,color='FFFFFF',size=11);c.alignment=Alignment(wrap_text=True,vertical='center')
    s.row_dimensions[1].height=42
    for row in s.iter_rows(min_row=2):
        for c in row:
            c.font=Font(name='Aptos',size=11);c.alignment=Alignment(vertical='top',wrap_text=True)
            v=c.value
            if isinstance(v,str) and v.startswith(('https://','http://')) and '\n' not in v and ' ' not in v:
                c.hyperlink=v;c.font=Font(name='Aptos',size=11,color='0563C1',underline='single')
            elif isinstance(v,str) and v.startswith('/Users/') and Path(v).is_file():
                c.hyperlink=Path(v).as_uri();c.font=Font(name='Aptos',size=11,color='0563C1',underline='single')
        maxlen=max(len(str(c.value or '')) for c in row)
        s.row_dimensions[row[0].row].height=min(130,max(40,30+(maxlen//28)*14))
    for col in s.columns:
        h=str(col[0].value or '')
        width=30
        if h in ['Longitude','Latitude']:width=17
        elif 'WKT'==h:width=38
        elif h in ['说明','下一步／边界','本轮补采集结果','本轮结果','限制与来源依赖','实际补得内容','仍缺什么','使用限制／待补内容']:width=55
        elif any(k in h for k in ['URL','入口','本地','网址']):width=42
        elif h.endswith('Id') or h in ['SourceId','ClaimId','CRS','DateText']:width=23
        s.column_dimensions[col[0].column_letter].width=width
    s.print_options.horizontalCentered=False;s.sheet_properties.pageSetUpPr.fitToPage=True
    s.page_setup.orientation='landscape';s.page_setup.paperSize=s.PAPERSIZE_A3;s.page_setup.fitToWidth=1;s.page_setup.fitToHeight=0
    s.print_title_rows='1:1'
    s.sheet_properties.tabColor='1F4E78' if name[:2] in ['00','09','14','17'] else '70AD47'
for row in wb['00_开始使用'].iter_rows(min_row=2):
    if row[0].value=='打开工作表':
        row[1].hyperlink=f"#'{row[1].value}'!A1";row[1].font=Font(name='Aptos',size=11,color='0563C1',underline='single')
wb._sheets.sort(key=lambda s:s.title)
wb.active=0
tmp=OUT.with_name(OUT.stem+'_写入中.xlsx');wb.save(tmp);tmp.replace(OUT)

def writecsv(name,headers,rows):
    with (EXPORT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)
writecsv('地点_默认参考点.csv',pointheaders,pointrows)
writecsv('地点_建筑候选_默认关闭.csv',pointheaders,candidatepoints)
writecsv('实物流转_示意线.csv',lh,[r for r in lines if r[3]=='实物流转'])
writecsv('知识传播_示意线.csv',lh,[r for r in lines if r[3]=='知识传播'])
writecsv('知识与实物活动点.csv',epheaders,eventpoints)
writecsv('对象与馆藏号对应.csv',[c.value for c in wb['18_对象与馆藏号'][1]],objrows)
features=[]
for row in pointrows:
    prop=dict(zip(pointheaders,row));features.append({'type':'Feature','geometry':{'type':'Point','coordinates':[prop['Longitude'],prop['Latitude']]},'properties':prop})
for row in lines:
    prop=dict(zip(lh,row));coords=[[float(t) for t in pair.strip().split()] for pair in prop['WKT'][12:-1].split(',')]
    features.append({'type':'Feature','geometry':{'type':'LineString','coordinates':coords},'properties':prop})
for name,subset in [
    ('地点_默认参考点.geojson',[f for f in features if f['geometry']['type']=='Point']),
    ('实物流转_示意线.geojson',[f for f in features if f['properties'].get('网络层')=='实物流转']),
    ('知识传播_示意线.geojson',[f for f in features if f['properties'].get('网络层')=='知识传播']),
]:
    (EXPORT/name).write_text(json.dumps({'type':'FeatureCollection','features':subset},ensure_ascii=False,indent=2))
oldmixed=EXPORT/'敦煌地图数据_参考点与示意线.geojson'
if oldmixed.exists():oldmixed.unlink()

# Meaningful integrity checks, including preservation of original IDs and traceable references.
check=load_workbook(OUT,data_only=False)
assert check['04_事件梳理'].max_row==23
originalids={r[0] for r in list(load_workbook(BASE,read_only=True)['04_事件梳理'].values)[1:]}
assert originalids.issubset({e['EventId'] for e in events})
assert len(P)==len(places)
for p in places:
    assert (p['Longitude'] is None)==(p['Latitude'] is None)
    if p['Longitude'] is not None:assert -180<=p['Longitude']<=180 and -90<=p['Latitude']<=90
assert all(row[4] in P for row in steps)
assert all(row[4] in P and row[5] in P for row in lines)
assert sum(r[1] for r in counts)==193 and sum(r[2] for r in counts)==22
assert all(not p['DefaultUse'] for p in places if p['PlaceId'].endswith('_HIST'))
assert len(lines)==18 and len(pointrows)==17
assert len(objrows)==24 and len({r[3] for r in objrows if r[3].startswith('BD068')})==23
assert len({r[0] for r in claims})==len(claims)
sourceids={r[0] for r in sources}
for row in lines:
    assert set(row[8].split(';'))<=sourceids
for row in claims:assert set(row[3].split(';'))<=sourceids
for s in check:
    assert s.max_row>1 and s.freeze_panes=='B2'
    for t in s.tables.values():assert t.ref.endswith(str(s.max_row))
invalid=[]
for f in COLLECT.glob('*.pdf'):
    if not f.read_bytes().startswith(b'%PDF'):
        invalid.append({'file':f.name,'reason':'未返回PDF；保留失败响应，不作为全文','bytes':f.stat().st_size})
        dest=f.with_suffix('.failed_response');f.rename(dest)
report={'date':DATE,'output':str(OUT),'sheet_rows':{s.title:s.max_row-1 for s in check},'default_points':len(pointrows),'candidate_points':len(candidatepoints),'schematic_lines':len(lines),'event_points':len(eventpoints),'claim_count':len(claims),'original_event_ids_preserved':True,'hamicounts':{'Chinese':193,'Tibetan':22,'total':215},'actual_road_geometries':0,'invalid_pdf_responses_renamed':invalid,'input_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'checks':'所有断言通过：ID、外键、来源、坐标范围、箱数求和、表格范围和原事件保留。'}
(COLLECT/'补采集校验报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
