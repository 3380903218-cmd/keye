#!/usr/bin/env python3
"""Build the HY5419 route-map research workbook from the preserved project records."""
from pathlib import Path
from datetime import datetime
import csv, hashlib, json, math, re
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

BASE = Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/DunHuang Project')
OUT = BASE / '路线地图'
DATE = '2026-10-20'
FILE = OUT / '敦煌项目_路线地图资料与制作指南.xlsx'
INPUT = BASE / '04_gephi/双层传播网络_Gephi'

def read_csv(name):
    with (INPUT / name).open(encoding='utf-8-sig', newline='') as h:
        return list(csv.DictReader(h))

events = read_csv('事件原始记录.csv')
old_sources = {r['来源ID']: r for r in read_csv('来源目录.csv')}
wb = Workbook()
wb.remove(wb.active)
wb.properties.title = 'HY5419 敦煌项目：路线地图资料与制作指南'
wb.properties.subject = '1900–1910年实物流转、知识活动与地理证据'
wb.properties.creator = 'HY5419 项目资料整理'
wb.properties.description = '包含来源、采集字段、地点坐标、事件及移动段缺口；城市参考点不代表历史场址，未补写实际运输路径。'
NAVY, TEAL, GOLD = '213A52', '167D8D', 'D4A44A'
GRAY, BLUE, GREEN, RED = 'F1F4F7', 'E9F3FB', 'E8F3EA', 'FCEAE8'

def sheet(name, headers, rows, widths=None, freeze='B2', color=TEAL):
    ws = wb.create_sheet(name)
    ws.sheet_properties.tabColor = color
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 85
    ws.append(headers)
    for row in rows:
        assert len(row) == len(headers), (name, len(row), len(headers), row)
        ws.append(row)
    ws.freeze_panes = freeze
    ws.row_dimensions[1].height = 36
    for c in ws[1]:
        c.font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor=NAVY)
        c.alignment = Alignment(vertical='center', wrap_text=True)
    for ri in range(2, ws.max_row + 1):
        maxlines = 1
        for ci, c in enumerate(ws[ri], 1):
            width = widths[ci-1] if widths else 24
            c.font = Font(name='Arial', size=11, color='243746')
            c.alignment = Alignment(vertical='top', wrap_text=True)
            if ri % 2 == 0:
                c.fill = PatternFill('solid', fgColor='F4F8FA')
            val = str(c.value or '')
            # Approximate Chinese glyph width to keep prose readable without manual resizing.
            line_est = sum(max(1, math.ceil(sum(2 if ord(ch)>255 else 1 for ch in line) / max(8, width-2))) for line in val.split('\n'))
            maxlines = max(maxlines, line_est)
            if val.startswith('http://') or val.startswith('https://'):
                c.hyperlink = val
                c.font = Font(name='Arial', size=10, color='136BB0', underline='single')
        ws.row_dimensions[ri].height = min(180, max(38, maxlines * 15 + 8))
    for ci in range(1, len(headers)+1):
        ws.column_dimensions[get_column_letter(ci)].width = widths[ci-1] if widths else 24
    if rows:
        table = Table(displayName='T' + str(len(wb.worksheets)).zfill(2), ref=f'A1:{get_column_letter(len(headers))}{ws.max_row}')
        table.tableStyleInfo = TableStyleInfo(name='TableStyleMedium2', showFirstColumn=False, showLastColumn=False, showRowStripes=False, showColumnStripes=False)
        ws.add_table(table)
    ws.print_options.horizontalCentered = True
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = ws.PAPERSIZE_A3
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = '1:1'
    ws.oddFooter.center.text = 'HY5419 | 路线地图资料 | &P / &N'
    return ws

intro = [
 ['项目目标', '为1900–1910年敦煌文献的实物流转与知识活动制作有出处的路线地图。现有重点是斯坦因、伯希和及清学部／京师图书馆相关事件。', '先读本页，再看06_优先补采集与02_工具选择。'],
 ['推荐工具', '快速核对点位：Google My Maps；正式制图：QGIS。若需要滚动叙事网页，可在资料核验后选ArcGIS StoryMaps。', '推荐依据是本项目需要保存坐标来源、区分线型和标注不确定性；属于本次方法建议。'],
 ['已填入的资料', '20条既有事件、15条地点记录、12条移动段／缺口、12项优先补采集任务；另有29项来源与工具资源。', '所有事件沿用原EventId，未改动原始工作簿或Gephi数据。'],
 ['可立即尝试', '09_点位导入已有敦煌、和田、伦敦、巴黎、北京5个参考点。只将这一张表另存为CSV UTF-8即可练习导入。', '这些是现代城市／城区参考点，不是1907年营地、1910年接收建筑或实际运输沿途点。'],
 ['暂时不能直接生成的内容', '实际运输折线尚缺中途停留、装运、发运和抵达证据。05_移动段待补的WKT留空，是明确的证据缺口。', '若只画起终点示意，必须命名为“流转关系示意／沿途未核”，并与已核路径使用不同线型。'],
 ['核心记录原则', '一行事件＝某批对象在某时某地发生的行动；一行移动段＝同一批对象从A到B的一段移动；一个PlaceId＝一个明确空间对象。', '探险家行程、馆藏归属和实物移动分别记录；共享人物不能自动连接两条实物路线。'],
 ['日期与时间轴', '保留原纪年和日期精度；年份、月份、季节不补成某月某日。DH009公历1910-12-15来自清历换算，仍需与原档核对。', 'StartYear/EndYear只方便筛选年份，不表示事件持续，也不能拿来计算旅行耗时。'],
 ['地点与坐标', '坐标统一使用WGS84／EPSG:4326，Longitude为经度X，Latitude为纬度Y。地点证据与坐标证据分开。', '留空表示未核，不填0。小数位数是数值显示精度，不是历史定位的米级精度。'],
 ['知识传播怎么上图', '先把列单、编号、查看、摄影、笔记等作为地点上的事件。只有找到信件、照片、目录等的发送／接收地点和时间，才增加传播线。', 'KE008是有条件的编目意向；KE002、KE005、PE001仍待核，默认不进入已核图层。'],
 ['原资料中的混列地点', 'DH001等旧单元格把敦煌、安西、和田并列。04_事件梳理保留原文，另给建议地点，不能按单元格顺序自动连线。', '斯坦因1907年的帐篷在莫高窟前；蒋孝琬营地在第130窟大佛脚下，均不能直接定位为敦煌市中心。'],
 ['阅读与筛选', '深蓝表头可筛选；黄色为待补或待核；蓝色为现代背景参考；绿色为可从现有文字开展定位。', '点击来源网址打开页面；07_资料与来源的本地文件列可直接打开已存在文件。'],
 ['数据关系', '03地点表的PlaceId→04事件表地点；04的EventId→05移动段；Sxx沿用项目文献编号，Mxx是本次地图与工具资源编号。', 'ObjectId为项目分析批次，并非每卷写本的实体同一性证明；要补馆藏号、箱号及对应页。'],
 ['本次查核范围', f'整理日期：{DATE}。复用原项目事件与阅读记录；新增核查官方软件文档、历史地名与地图入口、现代坐标来源。', '不是路线全复原或穷尽检索；本地历史来源优先保留既有页码，不将检索摘要冒充档案原件。'],
 ['文件与检索记录', '本Excel是阅读和后续补录入口。sources/保留检索日志、生成脚本、输入哈希及结构校验报告。', '若原始事件表更新，应重新核对本表；09_点位导入是本次快照，不会随其他表自动联动。'],
]
sheet('00_开始使用', ['项目', '说明', '下一步／边界'], intro, [24, 85, 78], color=NAVY)

fields = [
 ['事件', 'EventId', '必填', '沿用DH001、KE001等唯一编号', '关联既有Gephi事件；不要用地点名称当事件ID。', '04_事件梳理'],
 ['事件', 'Layer', '必填', '实物流转／知识传播／两层关联', '同一地点可发生两种行动，不强行合并。', '04_事件梳理'],
 ['事件', 'Action', '必填', '取得、装箱、寄存、接收、列单、摄影等', '把行政命令、编目意向和实际行动区分。', '04_事件梳理'],
 ['对象', 'ObjectId', '实物路线必填', 'B0003；逐卷时使用经核验的馆藏号', '同一批箱内可能有不同对象；需说明集合范围。', '04／05'],
 ['对象', 'RepresentationId / WorkId', '知识传播按需', '照片R0001；清单或备忘录W001', '复制品、作品与原卷分开；不知道时留空。', '04／后续新增记录'],
 ['对象', 'Shelfmark / CaseId', '优先补采集', '馆藏号；原箱号；行李／运单号', '建立文献、装箱清单、接收记录之间的实体对应。', '05／06'],
 ['时间', 'OriginalDate', '必填', '原样抄录纪年、月日与历法', '宣统二年十一月十四日不能直接写成1910-11-14。', '04_事件梳理'],
 ['时间', 'DatePrecision', '必填', 'day、month、year、season、范围或推定', '史料只到月，不补成每月1日；保留日期冲突。', '04_事件梳理'],
 ['时间', 'StartYear / EndYear', '建议', '1908；1908', '整数年份用于筛选，不代表一整年持续。', '04_事件梳理'],
 ['时间', 'Departure / Arrival', '运输段优先', '分别记录有证据的发运和收讫日期', '装箱日不等于出发日；首次查看日不等于入藏日。', '05_移动段待补'],
 ['地点', 'PlaceId', '必填', 'PL_KHOTAN等稳定编号', '改中英文标签不改ID；未知地点留空并写缺口。', '03_地点与坐标'],
 ['地点', 'OriginalName / LabelEN', '必填', 'Khotan／和阗；英文标签Khotan (Hotan)', '保留原拼写、异名；历史城市与今日行政区分开。', '03_地点与坐标'],
 ['地点', 'PlaceType / ContextPlaceId', '必填', '城市参考、洞窟、营地、历史机构', 'ContextPlaceId是定位上下文，不是转运、管辖或保管关系。', '03_地点与坐标'],
 ['地点', 'ValidPeriod', '历史地点必填', '1907年营地／1910年机构地址', '今天地址不能倒填为1910年接收建筑。', '03_地点与坐标'],
 ['坐标', 'Longitude', '地图点必填', '十进制度，经度X，数值-180至180', '西经为负；不填“94°”文本。', '03／09'],
 ['坐标', 'Latitude', '地图点必填', '十进制度，纬度Y，数值-90至90', '北纬为正；不要与经度倒置。', '03／09'],
 ['坐标', 'CRS', '地图点必填', 'EPSG:4326', '来源若为其他坐标系，先正确转换，不只改名称。', '03／09'],
 ['坐标', 'CoordinateSource / AuthorityId', '必填', 'GeoNames条目URL＋ID；历史地图图幅号', '坐标来源与证明事件发生的史料是两条证据。', '03／07'],
 ['坐标', 'PlacementMethod / Precision', '必填', '现代城市参考／历史图配准／建筑定位／未知', '无法量化误差时不编造半径；写明城市或区域级。', '03_地点与坐标'],
 ['路线', 'SegmentId', '每段必填', 'SG001；每一段单独编号', '找到新中转地时拆段，同时保留原汇总关系，避免重复统计。', '05_移动段待补'],
 ['路线', 'FromPlaceId / ToPlaceId', '绘线前必填', '只填已核验起终点', '转出机构的所在地不自动等于实际发运地。', '05_移动段待补'],
 ['路线', 'Waypoint / Sequence', '还原路径时必填', '逐站地点、顺序及各自证据', '只列出来源支持的中途点；不要自动套用今日驾车路线。', '05_移动段待补'],
 ['路线', 'Carrier / Role', '优先补采集', '蒋孝琬：取运；承运公司：实物运输', '谈判、搬运、保管、接收分别记；不知道承运人就留空。', '04／05'],
 ['路线', 'TransportMode', '按证据填写', '驮运／铁路／轮船；没有记载则未知', '不因跨海或路程远就补写交通工具。', '05_移动段待补'],
 ['路线', 'GeometryType / WKT', '有坐标后填写', 'actual_path／schematic_flow；LINESTRING(经度 纬度, …)', 'WKT仅是几何格式，不证明线路真实；My Maps列名必须是WKT。', '05／08'],
 ['证据', 'SourceId / Locator', '必填', 'S03，印刷60页／PDF5，Ac2段', '原件、出版原文、档案录文、研究推断、机构回顾分别说明。', '04／05／07'],
 ['证据', 'SupportedClaim', '必填', '此条材料具体支持地点、日期、对象还是行动', '一句话可能只支持部分属性，不把引用扩大成全链已核。', '04／05'],
 ['证据', 'Uncertainty / Contradiction', '必填', '日数冲突、地点未核、箱卷对应缺失', '空缺可见；不将来源数量当独立证据数量。', '04／05／06'],
 ['展示', 'MapUse / LineStatus', '必填', '城市事件参考点／关系示意待核／不绘线', '知识活动原地发生可以只画点；同城交接未定位时不画零长度线。', '04／05'],
 ['图件', 'MapDate / Sheet / Scale / Rights', '使用历史图时必填', '出版年、图幅、比例尺、扫描页、许可信息', '后出地图可辅助定位，不能单凭地图证明1907年的对象经过。', '06／07'],
 ['质控', 'CheckedBy / CheckedDate', '建议', '核验者＋YYYY-MM-DD', '补证后写明改动依据，更新对应EventId与SegmentId。', '后续补录列'],
]
sheet('01_采集字段', ['类别', '字段名', '何时需要', '怎么记录', '本项目注意事项', '记录位置'], fields, [14, 35, 24, 54, 66, 26])

tools_rows = [
 ['首选：正式制图', 'QGIS Desktop', '免费开源；Mac可用，本地工作无需云端账号。', '适合保存点、线、来源属性；分层显示历史事件、知识活动和路径确定性；排版正式地图。', '先导入09表的CSV点位；补证后建立线图层；保存GeoPackage＋QGIS项目。', '需要学习图层、坐标系与符号；旧地图配准误差和缺失路线仍须自己说明。', 'M01；M02', 'https://qgis.org/project/overview/'],
 ['入门：快速点位草图', 'Google My Maps', '浏览器＋Google登录。', 'CSV／XLSX等点位导入；按属性着色、加说明。CSV／Google Sheets可用WKT几何。', '09表另存CSV UTF-8→新建地图→添加图层→导入；选择Latitude／Longitude和Label。', '官方建议导入不超过2000行；历史地名自动地址匹配须逐项复核。实际路径不要套用今日导航。', 'M03', 'https://support.google.com/mymaps/answer/3024836?hl=en'],
 ['可选：网页叙事', 'ArcGIS StoryMaps', '使用条件取决于ArcGIS账号及组织权限；未核验你的NUS账号授权。', '将地图与叙述、证据说明组合；express map可手绘点线面，也可使用web map。', '先在Excel／QGIS维护资料，再按“取得—装箱列单—接收—查看复制”组织章节。', 'express map不能作为可导出的结构化资料主档；先确认账号功能。', 'M04；M05；M18', 'https://doc.esri.com/en/arcgis-storymaps/latest/author-and-share/add-maps.html'],
 ['已有工具的分工', 'Gephi（继续配合使用）', '沿用现有本地项目。', '保留人物—事件—对象的关系网络；地图补充“在哪里、何时发生”。', '共享EventId与ObjectId，把地图地点表与原网络事件互相对照。', '力导向布局位置没有地理含义；原57条关系边不能直接当57段运输路径。此为对现有数据结构的判断。', '项目既有GEXF和事件CSV', ''],
]
sheet('02_工具选择', ['建议用途', '工具', '账号／成本', '适合做什么', '你的起步方式', '限制与选择依据', '来源编号', '官方入口'], tools_rows, [24, 25, 43, 58, 64, 67, 28, 52], color=GOLD)

# Coordinates are source-backed modern reference anchors, deliberately not historical venue coordinates.
places = [
 ['PL_DUNHUANG', '敦煌（城市参考）', 'Dunhuang (city reference)', 'Tun-huang；敦煌', '城市参考', '', '现代参考；关联1907–1908区域语境', 94.68333, 40.16667, 'EPSG:4326', 'GeoNames 1529531', 'M12', 'https://www.geonames.org/1529531/dunhuang.html', '现代城市点；城市级，历史误差未量化', '可导入背景点', '用于地域概览；不能代替莫高窟、取运地点或营地坐标。'],
 ['PL_MOGAO', '莫高窟（遗址范围）', 'Mogao Caves (site; position pending)', 'Ch’ien-fo’-t’ung；千佛洞', '遗址', 'PL_DUNHUANG', '1907–1908；具体位置待核', None, None, 'EPSG:4326', '', 'S03；M11', 'https://whc.unesco.org/en/list/440', '遗址级；未采用数值坐标', '待定位', 'UNESCO条目参考坐标未核到洞窟尺度；保留在来源说明，不将其当第17窟或帐篷实测点。'],
 ['PL_CAVE17', '第17窟／藏经洞', 'Library Cave (Cave 17)', '藏经洞；Library Cave', '洞窟', 'PL_MOGAO', '1907–1908相关取得事件', None, None, 'EPSG:4326', '', 'S03；S07；S22', '', '洞窟级；坐标待核', '待定位', '与第16窟分开；不能把第17窟设为所有选择、搬运的唯一起点。'],
 ['PL_CAVE16', '第16窟及甬道', 'Cave 16 and corridor', 'Cave 16', '洞窟／选择地点', 'PL_MOGAO', '1907年5月', None, None, 'EPSG:4326', '', 'S03', '', '洞窟／甬道；坐标待核', '可按文献开展定位', 'S03印刷60页／PDF5：日间选择与打包材料位置；第17窟、16窟甬道、帐篷不能并成一处。'],
 ['PL_STEIN_TENT', '斯坦因帐篷（窟前，确址待核）', 'Stein’s tent in front of the caves (unlocated)', 'Stein’s tent', '营地', 'PL_MOGAO', '1907年5月取得阶段', None, None, 'EPSG:4326', '', 'S03；S07', '', '窟前营地；确址未知', '可按文献开展定位', 'S03印刷60页／PDF5明确帐篷在窟前。禁止把敦煌城市点当营地。'],
 ['PL_JIANG_CAMP', '蒋孝琬营地（第130窟大佛脚下）', 'Jiang Xiaowan’s camp at Cave 130 (unlocated)', 'Camp at the foot of the large Buddha, Cave 130', '营地', 'PL_MOGAO', '1907年5月取得阶段', None, None, 'EPSG:4326', '', 'S03', '', '第130窟内部参照；确址未知', '可按文献开展定位', 'S03印刷60页／PDF5；营地与接收手稿的斯坦因帐篷分开，不能仅因角色就画所有写本经过此营地。'],
 ['PL_ANXI', '安西（1907历史地点待对照）', 'Anxi (historical location pending)', 'Anxi；An-hsi；安西；今瓜州相关地名待核', '历史城镇／接收地点', '', '1907年10月', None, None, 'EPSG:4326', '', 'S03；S07；M06；M07', '', '历史城镇；未采用今日县域中心', '待核地名与坐标', '先查1907年对应城址、同名地点和年代；接收地点在安西不表示王圆箓亲赴安西。'],
 ['PL_KHOTAN', '和田／和阗（城区参考）', 'Khotan / Hotan (urban reference)', 'Khotan；Ho-t’ien；和阗；和田', '城区参考', '', '现代参考；1908年工作场址未定位', 79.93433, 37.10927, 'EPSG:4326', 'GeoNames 1281019（现名Gujangbagh）', 'M13；S03；S07', 'https://www.geonames.org/1281019/gujangbagh.html', '现代城区参考；非1908年装箱建筑', '可导入背景点', 'GeoNames检索页称Hotan，当前详情主名为Gujangbagh；保留ID与异名。装箱、列单和笔记仅作城市级位置。'],
 ['PL_LONDON', '伦敦（城市参考）', 'London (city reference)', 'London', '城市参考', '', '现代参考；1909–1910活动城市', -0.12574, 51.50853, 'EPSG:4326', 'GeoNames 2643743', 'M14；S07', 'https://www.geonames.org/2643743/london.html', '现代城市点；城市级，历史误差未量化', '可导入背景点', '可概览城市；英国博物馆／India Office整理地点须另核，不自动采用今日英国图书馆地址。'],
 ['PL_BM_HIST', '英国博物馆（历史存放场址待核）', 'British Museum (historical deposit venue pending)', 'British Museum；BM', '历史机构场址', 'PL_LONDON', '1909–1910；机构关系已见记述', None, None, 'EPSG:4326', '', 'S07；S17', '', '历史机构；具体存放房间与坐标待核', '待核历史场址', '寄存与正式入藏有别；Andrews的工作地点也不能仅据受雇机构推为此处。'],
 ['PL_PARIS', '巴黎（城市参考）', 'Paris (city reference)', 'Paris', '城市参考', '', '现代参考；1909–1910活动城市', 2.34880, 48.85341, 'EPSG:4326', 'GeoNames 2988507', 'M15；S15；S07', 'https://www.geonames.org/2988507/paris.html', '现代城市点；城市级，历史误差未量化', '可导入背景点', '法国国立图书馆接收与伯希和个人收件地点分开；暂时同城不合并为同一场址。'],
 ['PL_BN_HIST', '巴黎国立图书馆（历史接收场址待核）', 'Bibliothèque nationale (historical receipt venue pending)', 'Bibliothèque nationale；BN', '历史机构场址', 'PL_PARIS', '1909年底', None, None, 'EPSG:4326', '', 'S15', 'https://heritage.bnf.fr/france-chine/paul-pelliot-1878-1945-et-dunhuang', '历史机构；具体交接场址待核', '待核历史场址', '不用今日Tolbiac馆址替代1909年接收点；先查当时部门、登记册与Richelieu相关地址线索。'],
 ['PL_BEIJING', '北京（城市参考）', 'Beijing (city reference)', 'Peking；北京', '城市参考', '', '现代参考；1909–1910相关事件', 116.39723, 39.90750, 'EPSG:4326', 'GeoNames 1816670', 'M16；S19；S22', 'https://www.geonames.org/1816670/beijing.html', '现代城市点；城市级，历史误差未量化', '可导入背景点', '只用于城市背景；1909年展示地点、学部发出地点、1910年图书馆接收地点均需各自核实。'],
 ['PL_QING_EDU', '清学部（实际交接地址待核）', 'Qing Ministry of Education (handover venue pending)', '学部', '历史机构场址', 'PL_BEIJING', '1909–1910', None, None, 'EPSG:4326', '', 'S19', '', '机构已识别；实物交接场所未定位', '待核历史场址', '行政拨送主体不自动等于物品发运建筑；需查行文、取运与收讫记录。'],
 ['PL_JINGSHI', '京师图书馆（1910接收地点待核）', 'Metropolitan Library (1910 receipt venue pending)', '京师图书馆；Jingshi Library', '历史机构场址', 'PL_BEIJING', '1910年', None, None, 'EPSG:4326', '', 'S19；S11', '', '机构已识别；实际接收建筑待核', '待核历史场址', '广化寺是历史馆址查核线索，尚不能据此认定每次接收即发生在那里；不得使用今日国图总馆坐标。'],
]
place_headers = ['PlaceId', '中文名称', 'LabelEN', '原名／异名', '空间类型', 'ContextPlaceId', '适用年代与语境', 'Longitude', 'Latitude', 'CRS', '坐标条目ID', '来源ID', '来源URL', '定位精度／方法', '地图状态', '使用限制／待补内容']
ws_places = sheet('03_地点与坐标', place_headers, places, [24, 44, 58, 52, 22, 24, 45, 16, 16, 17, 39, 28, 52, 48, 26, 85], freeze='C2')
for r in range(2, ws_places.max_row+1):
    for ci in [8,9]: ws_places.cell(r,ci).number_format = '0.00000'
    state = ws_places.cell(r,15).value
    ws_places.cell(r,15).fill = PatternFill('solid', fgColor=BLUE if ws_places.cell(r,8).value is not None else GREEN if state=='可按文献开展定位' else 'FFF3D8')

# Event locations are editorially separated from the contaminated, mixed original location cells.
# tuple: locations, summary, map use, next location question, years
event_map = {
 'DH001': ('PL_CAVE17;PL_CAVE16;PL_STEIN_TENT', '1907年5月取得与窟前短距离搬运', '遗址活动点待定位', '补第16窟选择地与帐篷位置；不连安西和和田。', 1907,1907),
 'DH002': ('PL_MOGAO', '1907年6月追加取得', '遗址活动点待定位', '核具体取得与交接位置；20／13捆差异保留。',1907,1907),
 'DH003': ('PL_MOGAO;PL_ANXI', '蒋赴敦煌取得后带往安西', '端点关系待定位', '分别核取得地、到安西日期、同批身份和途中点。',1907,1907),
 'DH004': ('PL_BM_HIST', '1909年抵英；至1910年初夏已有BM存放记述', '城市级接收点参考；机构待定位', '抵英港口、箱号、存放场址与收讫日分开查；不是所有中间点已知。',1909,1910),
 'DH005': ('PL_MOGAO', '伯希和1908年查看、选取与取得', '遗址活动点待定位', '3月查看日不当交接日；1909北京小批次与此集合须逐件对应。',1908,1908),
 'DH006': ('PL_BN_HIST', '伯希和写本1909年底由巴黎国立图书馆接收', '城市级接收点参考；机构待定位', '查正式收讫凭证、接收部门与历史建筑；不加入卢浮宫非写本对象。',1909,1909),
 'DH007': ('PL_QING_EDU', '1909年样本送学部（年份据文书回推）', '北京接收语境；原始发运点未知', '陕甘总督机构不是空间坐标，不擅自补兰州为发运点。',1909,1909),
 'DH008': ('PL_QING_EDU;PL_JINGSHI', '1910年主批十八箱由图书馆取运', '同城机构关系；不绘运输线', '学部实际存放处、图书馆接收处与主批收讫日待核。',1910,1910),
 'DH009': ('PL_QING_EDU;PL_JINGSHI', '1910年续交22卷及粘片2本', '同城机构关系；不绘运输线', '公历12月15日为换算；核原接收底账及取运地点。',1910,1910),
 'KE001': ('PL_KHOTAN', '蒋孝琬初步列单', '城市级知识活动参考点', '列单的具体营地／建筑与清单原件待补。',1908,1908),
 'KE002': ('PL_KHOTAN', '红色苏州码子编号者归属推定', '待核图层；默认排除', '作者使用归属判断；逐卷图像、手迹和工作日期尚未核。',1908,1908),
 'KE003': ('PL_KHOTAN', '1318件索引卡清单的制作记述', '城市级知识活动参考点', '索引原件未找到；核箱91与清单身份，不能画成1318件新增流转。',1908,1908),
 'KE004': ('PL_KHOTAN', '斯坦因笔记与Or.8210/S.316编号对应', '城市级知识活动参考点', '核MSS Stein272/59与原卷影像；743为写本纪年。',1908,1908),
 'KE005': ('', '1909年Andrews拆箱、分类与列单', '待核图层；默认排除', '英国／伦敦语境不足以定位具体工作地；不据雇主补场址。',1909,1909),
 'KE006': ('PL_LONDON', '伯希和1910年初夏在伦敦检查写本', '城市级知识活动参考点', '核检查的机构、房间与逐件对象；人员到访不是新一笔收藏取得。',1910,1910),
 'KE007': ('PL_LONDON', '伦敦检查语境中的备忘录', '城市语境参考；成稿处待核', '成稿地点与时间不等同查看地点；原稿和出版载体分别记录。',1910,1910),
 'KE008': ('PL_LONDON', '表示愿有条件编目', '意向记录；不作为已完成活动点', '不能补成已编目、已形成目录或知识流出路线。',1910,1910),
 'PE001': ('PL_PARIS', '为编目送给在巴黎的伯希和一批手稿', '待核图层；默认排除', '伦敦只是寄出语境；实发地点、寄件人、收讫、对象号与归还均待核。',1910,1910),
 'KE009': ('PL_BEIJING', '北京少量写本展示与查看', '城市级知识活动参考点', '核1909年8–9月具体场所、观看者、写本号；S01与S22不当独立目击。',1909,1909),
 'KE010': ('PL_BEIJING', '北京摄影／复制', '城市级知识活动参考点', '照片制作者、载体、接收人和去向未核；不能当原卷转交。',1909,1909),
}
event_rows = []
for e in events:
    eid=e['事件ID']; loc, summary, use, gap, ys, ye = event_map[eid]
    event_rows.append([eid, e['网络层'], e['行为类型'], summary, e['对象／批次ObjectId'], e['复制品RepresentationId'], e['作品WorkId'], e['原始日期与历法'], e['日期精度'], ys, ye, loc, use, e['核验状态'], e['参与者及具体角色'], e['证据支持什么'], e['尚未确认什么'], gap, e['证据来源及定位'], e['地点'], e['关联阅读ID']])
sheet('04_事件梳理', ['EventId','网络层','行动类型','地图事件摘要','ObjectId','RepresentationId','WorkId','原日期与历法','日期精度','StartYear','EndYear','建议PlaceId','地图用途','原核验状态','参与者与角色','现有证据支持','原证据限制','地点／路线待补','来源与页码','原始地点单元格（保留）','关联阅读ID'], event_rows, [17,18,28,48,19,22,17,58,31,13,13,44,44,22,78,80,80,80,75,48,32], freeze='E2')

segments = [
 ['SG001','DH001','B0001','实物流转','PL_CAVE16','PL_STEIN_TENT','第16窟选择地→窟前帐篷','1907年5月；各夜未逐日核','蒋孝琬：取回；其他参与者按原事件记录','夜间搬运；交通方式不另补','文字支持局部搬移；几何未知','可作局部关系示意，先核两端位置','第16窟及帐篷确址；每天取回对象是否有逐批明细','S03：印刷60页／PDF5，Ac1a段；S07：印刷824末–825首／摘录PDF2–3','','不绘线：坐标待核','不把蒋第130窟营地插入本段。'],
 ['SG002','DH003','B0003','实物流转','PL_MOGAO','PL_ANXI','敦煌取得地→安西接收地','1907年10月；各来源日数冲突','蒋孝琬：赴敦煌取得并运回；参与角色不等于沿途地点','未知；不由常识推定驮运','已见起终地域与取运叙述；道路未核','端点定位后可画关系示意','安西历史城址、敦煌具体交接处、逐日路线和承运凭证','S03：印刷60页／PDF5，Ac2；73页注26；S07：印刷825页／摘录PDF3','','不绘线：坐标与路径待核','Mogao是本次取得的来源区域语境；需核具体交接地点，不假定王亲到安西。'],
 ['SG003','DH003','B0003','实物流转','PL_ANXI','PL_KHOTAN','安西批次→和田装箱阶段','1907年10月之后；至1908年7月已到和田装箱','承运人未核','未知','文献串联同批袋装与后来装箱；中间路线未知','只在补齐端点后画关系示意','袋号／箱号对应、各停靠地和日期、批次是否随人同行','S03：印刷60页／PDF5，Ac2；印刷64页／PDF9，Id4；MSS Stein37/117–20为原档线索','','不绘线：历史端点与沿途待核','不能仅按斯坦因第二次考察的个人行程生成写本路线。'],
 ['SG004','DH004;KE001','B0004','实物流转','PL_KHOTAN','PL_LONDON','和田装箱→伦敦存放：聚合批次对应待核','装箱1908-06-09至07-18；抵英1909；至1910初夏存放记述','装箱组织者、承运人、收货人分别待核','未知；港口、船运与铁路均待证','集合关系与运输细节待核','候选关系，不当已核运输段','MSS Stein37/117–20箱号；发运日、货运单、入港与收讫；与24箱手稿的范围对应','S03：印刷64页／PDF9，Id4；S07：印刷825、916页／摘录PDF3、6；S17：AAM16页及20页注61','','不绘线：批次对应及路径待核','“为送伦敦而装箱”不等于当天离开和田；不能凭地理常识加入印度或海港节点。'],
 ['SG005','DH005;DH006','B0005','实物流转','PL_MOGAO','PL_BN_HIST','伯希和取得→巴黎机构接收（汇总）','1908年取得；1909年底接收','伯希和考察队：取得／带回；国立图书馆：接收','未知','有取得与接收记述；逐箱路径未知','端点核实后可画汇总关系示意','逐卷／箱号；寄运链、离境和接收；北京展示小批次是否对应','S22：印刷13页／PDF19；S15：Les documents rapportés…段；DH005／DH006原阅读记录','','不绘线：历史场址与沿途待核','不把所有写本都画成经北京；不混入另购印本及卢浮宫对象。'],
 ['SG006','DH007','O0002','实物流转','','PL_QING_EDU','未知发运地→北京学部（样本）','1909年，依1910文书“上年”回推','陕甘总督机构：送样主体；实际寄运者未知','未知','档案录文支持送样及接收机构；起点缺失','保留接收记录，不绘完整线','发运地点、送样文书、取样对象、收讫时间','S19：一、档案录文（一）；二、第一先呈样本','','不绘线：起点与历史场址待核','不能用总督官署的推定所在地代替样本出发地。'],
 ['SG007','DH008','B0006','实物流转','','PL_BEIJING','陕甘解运→北京主批：行程待补','1910年；解运与十八箱接收节点须分别核','陕甘总督机构、解运者、学部与图书馆角色分开','未知','文书回述解运；主批身份与中间交接细节待核','研究缺口，不作已核线段','原始发运点与名单；沿途、箱号和学部存放处；不能只据同一句拆多笔交接','S19：一、（一）学部行文；二、第二两次调拨；S11：PDF1末–2首','','不绘线：起点、批次对应与沿途待核','北京为城市层级接收背景；不是已经定位了学部或图书馆建筑。'],
 ['SG008','DH008','B0006','实物流转','PL_QING_EDU','PL_JINGSHI','学部拨送→京师图书馆取运十八箱','1910年；早于宣统二年十一月十二日行文','学部：拨送；图书馆派员：取运／接收','未知','档案录文支持机构交接；实际取运点未核','先作为同城交接事件记录','主批接收日、学部仓储／交出地址、图书馆接收建筑及底账影像','S19：一、（一）；二、第二两次调拨；S11：PDF1末–2首','','不绘线：同城场址待核','行政箭头与真实运输路径分开；不把两机构都放北京参考点后画零长度线。'],
 ['SG009','DH009','B0007','实物流转','PL_QING_EDU','PL_JINGSHI','学部→京师图书馆续交批次','宣统二年十一月十四日＝1910-12-15（换算）','学部：拨送；京师图书馆：接收','未知','接收底账录文支持22卷＋粘片2本；地点待核','先作为同城接收事件记录','原底账影像、取运和收讫地址、样本返还与新增对象分开','S19：一、（二）接收底账；S25：1910对照表第1页，公历12月行','','不绘线：同城场址待核','返还既有样本1卷不算新增第23卷；日期保留原历法。'],
 ['SG010','PE001','B0011','两层关联','','PL_PARIS','寄出地点待核→巴黎伯希和（编目送寄）','1910年秋；发运和收讫日未知','收件对象伯希和；寄出与承运主体未知','未知','来源有送寄记述；实际寄出地点未落实','待核层；默认排除','具体馆藏号、寄出地、邮运或交接记录、到件与归还、编目成果','S07：印刷916页／摘录PDF6，In the autumn of 1910段','','不绘线：默认排除待核','伦敦仅为上文馆藏语境；不直接补写为已证实的伦敦→巴黎运输。'],
 ['SG011','DH005;KE009;KE010','B0012','两层关联','PL_MOGAO','PL_BEIJING','敦煌取得→1909北京展示小批次（对应待核）','1908年取得语境；1909年8–9月北京展示','伯希和：带来／展示；观看者与摄影者待核','未知','北京展示支持对象在场；逐件与取得集合关联未核','保留北京活动点；暂不连接物理路线','展示具体写本号、带到北京之前的保管地点、照片原件与参与者','S22：印刷15页／PDF21；S01：印刷840页／PDF20；S22印刷13页为取得背景','','不绘线：批次及中间行程待核','本段是需检验的关联，不能把全部B0005或照片R0001都当原卷经过北京。'],
 ['SG012','DH004;KE006','B0004','实物流转','PL_LONDON','PL_BM_HIST','英国抵达／伦敦背景→BM历史存放点','1909年抵英；至1910年初夏BM存放语境','考察队：材料来源；BM：存放机构','未知','存放有据；伦敦城市参考不是实际发货点','接收点记录，不作单独运输线','抵英地点、伦敦中转仓储、具体BM存放场址与保管责任','S07：印刷825、916页／摘录PDF3、6；S17：AAM16页及20页注61','','不绘线：空间层级不一致','这是需要细化的接收过程，不新增计算一笔已知实物运输。'],
]
seg_headers = ['SegmentId','关联EventId','ObjectId','网络层','FromPlaceId','ToPlaceId','候选移动关系','时间证据','人员／机构角色','TransportMode','证据状态','当前可表达什么','优先补什么','来源与定位','WKT','绘线决定','解释限制']
ws_seg = sheet('05_移动段待补', seg_headers, segments, [18,29,17,18,25,25,54,66,62,45,58,58,85,82,26,42,80], freeze='G2', color=GOLD)
for r in range(2,ws_seg.max_row+1):
    ws_seg.cell(r,15).fill=PatternFill('solid',fgColor='FFF3D8')
    ws_seg.cell(r,15).comment=Comment('未填是因为尚无核实后的几何路径。若后续创建示意线，请同时在“绘线决定”标记schematic_flow，并保留沿途未核的说明。','HY5419')

gaps = [
 ['G01','P1','地点','PL_CAVE16；PL_STEIN_TENT；PL_JIANG_CAMP','1907年莫高窟营地和短距离搬运具体在哪里？','S03印刷60页；斯坦因同期照片、营地平面图、日记和原地图','Stein tent Cave 16 Cave 130 May 1907；莫高窟 斯坦因 营地','先从S03注20–21追到日记与照片，记录拍摄日／图号、所见方位和可识别地物。','建筑／洞窟可定位，并解释配准或定位误差；不能只靠城市地名。','M07；M08；M09；M10；S03','SG001'],
 ['G02','P1','历史地名','PL_ANXI','1907年的Anxi具体是哪个城址／接收处？','CHGIS年代检索；斯坦因地图与Index of Local Names；地方志历史城图','Anxi An-hsi 1907；安西 瓜州 城址 县治','分别查名称、1907年和要素类型，记录查询结果ID、图幅、年代及与今地关系。','两种来源能相互对照；县域中心、旧城和接收营地不混用。','M06；M07；M08；S03','SG002；SG003'],
 ['G03','P1','批次和箱号','B0003；B0004；B0008','取得的袋装写本如何对应和田装箱、伦敦接收？','MSS Stein37/117–20（S03引用）；每箱清单与接收登记','MSS Stein 37 117 120 Khotan packing list 1908','先核档号与页／叶，再摘箱号、包捆号、题名、数量单位，逐项对应现存馆藏号。','至少一个可追踪箱或具体写本能跨两节点对应；汇总范围不强行相等。','S03；M09；M10','SG003；SG004'],
 ['G04','P1','运输节点','SG004','和田装箱后究竟何日从何地发运、经何处抵英？','发运信、运单、运输账、包装／保险记录、港口到货或收讫记录','Stein 1908 1909 cases dispatch London shipping receipts','逐段找起终点、发到日期、承运人、运单号；人走的路只当查档线索。','每个沿途点有同批对象证据；无证据段保持断开或关系示意。','S07；S03；M09','SG004'],
 ['G05','P1','历史接收地点','PL_BM_HIST；PL_BN_HIST；PL_JINGSHI','1909–1910的存放或接收实际在哪栋建筑？','机构当年年报、部门登记、收讫底账、历史地址／平面图','British Museum Stein deposit 1909；Bibliothèque nationale Pelliot 1909；京师图书馆 1910 接收 广化寺','逐机构核当年部门、地址、接收行动与场所；今日地址只能作为对照字段。','地址有当年证据，且与本次接收行动相连；不是只核机构创立地点。','S07；S15；S19；S11','SG005；SG008；SG009；SG012'],
 ['G06','P1','清代解运与样本','DH007；DH008；DH009','样本和十八箱主批从何地、由谁解运至北京？','S19所录学部档案、接收底账及陕甘机构往来原件','敦煌遗书 学部 陕甘 解运 十八箱 十一月十四','按S19文书抬头、时间、标题追原档；摘文号、签署人、交接人、箱数和地点。','能够区分命令、寄送、到件、取运、返样；清历与公历分列。','S19；S11；S25','SG006；SG007；SG008；SG009'],
 ['G07','P2','伯希和批次','B0005；B0012','1909年北京展示的是哪些写本？是否全部经北京？','S22印刷15页、同期书信／日记、中文学人题记和照片目录、BnF入藏资料','Pelliot Pékin 1909 manuscrits photographies；伯希和 北京 1909 写本 照相','用具体题名、写本号和照片相互对应；记录每个来源是亲见还是转引。','只能对已识别子集画路线；其余批次不跟随子集自动经过北京。','S22；S01；S15','SG005；SG011'],
 ['G08','P2','临时送寄','PE001；B0011','1910年编目送巴黎一批写本的寄出与返回有何证据？','S07印刷916页后文；Stein–Pelliot往来信件、借出单、收件和归还记录','Stein Pelliot autumn 1910 first instalment catalogue loan','优先找对象清单、寄件地址、日期、收件批示、归还确认和实际编目成果。','四要素能核：具体对象、寄出地、到件、用途；缺一则对应项保留待核。','S07；M09；M10','SG010'],
 ['G09','P2','知识传播载体','R0001；W001；W002；W003','照片、笔记、索引和备忘录如何从一个地点传给另一主体？','摄影原件背记、信封、题名页、清单原件、抄本或出版记录','Pelliot photographs Peking 1909；MSS Stein272/59；Stein Pelliot memorandum','区分制作地点、寄出地、收件地、阅读地、刊印地；每次传播记载体与收件人。','可识别同一复制品／作品及两端动作；不能把原卷路线复制给照片。','S03；S07；S22；M09；M10','KE003；KE004；KE007；KE010'],
 ['G10','P2','底图与历史边界','地图全部','地图的底图是哪个年代、能表达什么？','NII原地图／图幅；Natural Earth现代海岸线与地貌背景','Digital Silk Road Toyo Bunko map Stein；Natural Earth physical','记录历史图出版年、图幅、比例尺；现代底图在图注注明“现代背景”。','不用今日国界证明清末行政路线；若边界无关研究可只用海岸线／陆地背景。','M08；M17','地图底图'],
 ['G11','P2','坐标核验','03_地点与坐标','各点的空间精度和历史对应能否说明？','地点史料＋坐标条目／配准图，两者分别保存','地点原名＋年份＋旧图；GeoNames ID','已有5点只作现代参考；新增每个点记录坐标来源、CRS、定位法和适用年。','未知不用0；不把来源小数位数当历史精度；不把城市背景点当场址。','M06；M07；M11–M16','全部点位'],
 ['G12','P3','网页展示与使用条件','项目展示','是否需要网页叙事及哪些账户权限？','ArcGIS官方文档；NUS GIS指南／校内软件入口','ArcGIS StoryMaps express maps account privileges NUS GIS','先用已有Excel和QGIS推进；有展示需求再查个人账号能否建立及分享故事。','软件账号可用并明确分享范围；所有原始表仍保留本地可移交格式。','M01；M04；M05；M18','工具选择'],
]
sheet('06_优先补采集', ['任务ID','优先级','信息类型','关联对象','要解决的问题','优先找什么材料','建议检索词','怎么摘录／查找','达到什么程度可以上图','资料入口ID','关联事件／线段'], gaps, [16,14,22,45,65,76,70,85,85,40,40], freeze='E2', color=GOLD)

resources = []
def resource(sid,title,kind,use,locator,url,status,limit,local='',year='未标注／动态网页'):
    resources.append([sid,title,kind,year,use,locator,url,local,status,limit,DATE])

local_overrides = {'S01':'文献/文献综述/full-text/L01_Doumy_2025.pdf','S03':'文献/文献综述/full-text/L02_Terzi_Whitfield_2024.pdf','S19':'文献/文献综述/full-text/L03_Fang_2009_reprint.html'}
source_uses = {
 'S01':('人物与选择、1909北京展示的研究背景','印刷837–840页／PDF17–20；区分与S22的依赖关系'),
 'S03':('莫高窟营地、安西取运、和田装箱与编号工作','印刷60页／PDF5：窟前帐篷、Cave130营地与Ac2；63–64页／PDF8–9：索引、笔记、Id4；73页注24、26'),
 'S07':('取得批次、英国存放、伦敦查看与1910送寄记述','印刷824–825与916页；本地6页摘录PDF2–3、6；参与者后出记述'),
 'S11':('主批交接与国图收藏的机构回顾','本地PDF1页末–2页首；出版年未核，URL上传日不作出版日'),
 'S15':('伯希和取得与1909年底国立图书馆接收','3 mars 1908、négocia l’acquisition及Les documents rapportés…段'),
 'S17':('1909整理与寄存／正式入藏的区别','沿用本地AAM PDF16页及20页注61，不与期刊PDF页码混写'),
 'S19':('样本、十八箱、续交22卷与接收底账的档案录文','一、档案录文（一）（二）；二、第一／第二；三、样本；原档影像尚缺'),
 'S22':('伯希和参与者自述：1908取得、1909北京查看摄影','印刷13、15页／PDF19、21；扫描0019、0021'),
 'S25':('仅用于清历与公历换算','1910对照表第1页，公历12月行；原历十一月十四日对应12月15日'),
}
for sid in source_uses:
    r=old_sources[sid]; rel=local_overrides.get(sid,r['本地路径（相对项目）'])
    exists=(BASE/rel).is_file()
    limit = '转载正文不是档案原件影像；有疑似转录字误。原文采用清历，本表DH009另据S25换算公历，不能把换算结果当成原文直载。' if sid=='S19' else r['限制']
    resource(sid, r['作者']+'｜'+r['题名'], '既有历史／方法来源', *source_uses[sid], r['链接'], '复用本地文件／阅读记录；本次未重下载' if exists else '复用原阅读记录；原本地路径未找到', limit, str(BASE/rel) if exists else '', r['年份'])

resource('M01','QGIS｜Overview','官方软件说明','正式地图的点线编辑、图层组织与排版；支持Mac、Windows、Linux','Key features；Professional map production；Cross platform','https://qgis.org/project/overview/','官网全文已查','本轮未安装或操作QGIS；软件提供制图能力，不负责判断史料真伪。')
resource('M02','QGIS 3.44｜Opening Data','官方操作文档','导入CSV经纬度点和WKT；GeoPackage等文件入口','Importing a delimited text file → Geometry definition；X=Longitude，Y=Latitude','https://docs.qgis.org/3.44/en/docs/user_manual/managing_data_source/opening_data.html','官方文档已查','文档版本3.44用于说明操作；不声称是你电脑当前版本，菜单可能不同。')
resource('M03','Google My Maps｜Import map features from a file','官方操作文档','用CSV点位建立初步地图；后续可导入WKT','Import a file；Import info into the map；WKT列名；不超过2000行','https://support.google.com/mymaps/answer/3024836?hl=en','官方文档已查','本轮未登录或上传；现代地址自动匹配不替代历史地名核验。')
resource('M04','ArcGIS StoryMaps｜Add and configure maps','官方操作文档','地图与叙述展示；express map和web map选择','Add an express map；Add a web map','https://doc.esri.com/en/arcgis-storymaps/latest/author-and-share/add-maps.html','官方文档已查','express map不作为结构化资料主档；使用权限应先查个人账号。')
resource('M05','ArcGIS StoryMaps｜Frequently asked questions','官方条件说明','核对账号条件与express map的使用边界','Express maps相关问答；account／organization条件','https://doc.arcgis.com/en/arcgis-storymaps/get-started/faq.htm','官方页面已查','未核验NUS账号或订阅；不假定校内身份自动取得全部权限。')
resource('M06','Harvard CHGIS｜How To','历史地名数据库官方说明','查安西等地的历史名称、类型与适用年代；下载历史GIS资料','Place Name Search：name、feature type、year；Time Slice／Time Series','https://chgis.fas.harvard.edu/pages/howto/','官方说明已查；尚未取得匹配1907安西的条目','数据库存在不等于本项目地名已匹配；历史县域、县治与接收营地需分开。')
resource('M07','NII Digital Silk Road｜Stein Gazetteer','历史地图地名索引','查Anxi、Khotan、Tun-huang等原拼写与图上位置','Map of Innermost Asia＋Index of Local Names；name search／map search','https://dsr.nii.ac.jp/digital-maps/stein/place-names/','官方索引页已查；具体地名结果尚待核','据历史图和地名表构建；旧图位置不是现代实测GPS，更不能独立证明某批写本经过。')
resource('M08','NII／Toyo Bunko｜Digital Maps index','原书扫描与地图入口','搜斯坦因报告附图、地形和历史城址对照','Map index；需另记录书名、图幅、图版和出版年','https://dsr.nii.ac.jp/toyobunko/map/index.html.en','检索已发现官方入口；本轮正文打开不稳定','这里只收入口，未完成地图下载、配准或路线核验。')
resource('M09','Bodleian｜Archive of Sir Mark Aurel Stein','档案目录线索','追MSS Stein37/117–20、272/59等装箱单、日记与笔记原件','Collection catalogue：Notebooks／expedition correspondence等；档号来自S03','https://archives.bodleian.ox.ac.uk/repositories/2/resources/8334','官方检索摘要可见；直接打开被反自动访问拦截','目录不是档案影像；未取得上述原件，也未认定它们均已数字化。')
resource('M10','International Dunhuang Programme｜Stein Collection','馆藏与对象线索','定位具体写本、旧编号、机构分藏与照片的检索入口','Stein Collection专题；后续以Or.8210/S.316等具体馆藏号查条目','https://idp.bl.uk/discover/collection-categories/stein-collection/','官方检索摘要可见；直接打开返回403','未下载具体对象图像或核对逐件轨迹；专题介绍不代替运单和接收凭证。')
resource('M11','UNESCO｜Mogao Caves','遗产地条目','核正式遗产名称与遗址范围背景；仅提供坐标查核线索','条目坐标N40 7 59.988、E94 49 0.012（页面原值）','https://whc.unesco.org/en/list/440','官方条目／检索定位信息已查；未采作本表点位','条目参考坐标未验证为第17窟、16窟或营地；不填入点位导入表。')
resource('M12','GeoNames｜Dunhuang（1529531）','现代地理条目','城市背景点：纬40.16667，经94.68333','Coordinates；PPLA3','https://www.geonames.org/1529531/dunhuang.html','官方条目坐标已核','仅为现代城市参考，不代表莫高窟或1907营地。')
resource('M13','GeoNames｜Gujangbagh／Hotan（1281019）','现代地理条目','城区背景点：纬37.10927，经79.93433；连接Khotan异名','Coordinates；Alternate names含Hotan／Khotan；历史记录显示主名已改','https://www.geonames.org/1281019/gujangbagh.html','官方详情已核；与Hotan检索结果对应','现代城区点；不是1908年装箱建筑，不与和田地区／县域中心／机场坐标混用。')
resource('M14','GeoNames｜London（2643743）','现代地理条目','城市背景点：纬51.50853，经-0.12574','Coordinates','https://www.geonames.org/2643743/london.html','官方条目坐标已核','不代表英国博物馆、India Office或英国图书馆场址。')
resource('M15','GeoNames｜Paris（2988507）','现代地理条目','城市背景点：纬48.85341，经2.34880','Coordinates','https://www.geonames.org/2988507/paris.html','官方条目坐标已核','不代表1909国立图书馆接收建筑或伯希和私人收件地址。')
resource('M16','GeoNames｜Beijing（1816670）','现代地理条目','城市背景点：纬39.90750，经116.39723','Coordinates','https://www.geonames.org/1816670/beijing.html','官方条目坐标已核','不代表学部、京师图书馆或1909展示建筑。')
resource('M17','Natural Earth｜About','官方底图资料与许可','使用现代陆地、海岸线等概览背景；网站数据为public domain','About → Terms of Use；边界政策说明','https://www.naturalearthdata.com/about/','官方全文已查；本轮未下载底图','现代数据不代替清末国界和行政区；比例尺须匹配图幅，若无关可省略政治边界。')
resource('M18','NUS Libraries｜Geographical Information System (GIS)','校内GIS资源指南','从校内指南查数据、方法、培训及进一步咨询入口','Welcome；Key Resources；Geospatial Data Sources','https://libguides.nus.edu.sg/nuslgis','指南已查；未联系任何人或核验账号','仅作为入口；不能据此声称学校为该用户开通ArcGIS权限。')
resource('M19','GeoNames｜Home / data licence','坐标数据归属说明','使用GeoNames数值点位时注明数据来源与CC BY 4.0','主页数据库说明与许可链接','https://www.geonames.org/','官方主页已查','API账号和服务条件与网页查单点不同；本次只使用5个网页条目。')
resource('M20','Google Earth Outreach｜Visualize your data on a custom map using My Maps','官方入门教程','按步骤学习导入、分层与地图内容','Import your data；Style your map','https://www.google.com/earth/outreach/learn/visualize-your-data-on-a-custom-map-using-google-my-maps/','官方教程已检索；功能细节以M03已核文档为准','辅助教程；本轮未替用户建立或发布地图。')

assert len(resources)==29
ws_sources=sheet('07_资料与来源', ['SourceId','资料题名／提供机构','资料类型','年代／版本','可以用于什么','定位／建议先读处','来源URL','本地文件（已核路径）','本次访问／核验状态','不能据此证明什么','整理日期'], resources, [16,80,28,35,85,90,65,65,65,90,19], freeze='C2')
for row in ws_sources.iter_rows(min_row=2):
    cell=row[7]
    if cell.value:
        cell.hyperlink=Path(cell.value).as_uri()
        cell.font=Font(name='Arial',size=10,color='136BB0',underline='single')

steps = [
 ['共通','01','先定图要回答的问题','建议分两张／两组图层：①文献实物如何取得、装箱与接收；②在哪里被列单、查看、摄影或记为知识。','不要把知识活动的发生直接当作一条物理移动。','00；04；05','方法建议'],
 ['共通','02','清理与补证','优先完成06的P1任务；有证据的地点进入03，未定位点继续留空；不按旧“地点”单元格顺序连线。','起终点有据但沿途未知，只能表达流转关系示意。','03；06','方法建议'],
 ['Google My Maps','03','导出一个点位CSV','在Excel选中09_点位导入，另存CSV UTF-8。若Excel提示仅保存活动工作表，确认当前表为09；原.xlsx仍保留。','这5行只用于城市背景点。后续新增历史地点要先核坐标和来源。','09','M03'],
 ['Google My Maps','04','建立点位图','电脑登录My Maps→新建地图→添加图层→导入CSV；定位列选Latitude和Longitude；标题选Label。','英文标签来自Label；PlaceId保留用于关联。','09','M03；M20'],
 ['Google My Maps','05','检查点位和说明','逐点检查是否在预期城市；按PointRole等字段设置样式；说明中保留Note和SourceURL。','同城多个事件可写在说明中，不凭空偏移成多个真实地址。','03；09','M03；方法建议'],
 ['Google My Maps','06','后续导入线','仅当几何经核验后，从05筛出可展示记录另存CSV；几何列名称为WKT；导入时选择WKT作为定位列。','当前05的WKT均空，不能作为现成线文件。关系示意需在图层名和说明里写清。','05','M03'],
 ['QGIS','07','导入点位','将09表另存CSV UTF-8。打开QGIS数据源管理器→Delimited Text／分隔文本；选择CSV；X=Longitude，Y=Latitude；源坐标系EPSG:4326。','若落点异常先检查经纬倒置、负号与坐标系。','09','M01；M02'],
 ['QGIS','08','保存工作文件','将导入点图层另存为GeoPackage，保存QGIS项目文件。Excel继续保存研究字段与来源。','GeoPackage存图层，项目文件存图层引用和样式；移动文件时一起维护路径。','03；09','M01；M02；方法建议'],
 ['QGIS','09','按问题建立图层','分开：现代城市背景点、已核历史场址、实物关系示意、已核路径、知识活动点、待核项目。使用LabelEN显示英文地名。','当前城市背景点不能改名成确切历史建筑；待核层默认关闭。','03；04；10','方法建议'],
 ['QGIS','10','录入路线几何','补齐05的端点／路径证据后建立线图层，逐段记录SegmentId、EventId、ObjectId和来源。也可从有效WKT导入线。','只有两个端点时，直线／曲线表达的是关系；绘制形状不构成沿途史实。','05','M01；M02；方法建议'],
 ['QGIS','11','配置图例与标注','用颜色区分实物流转和知识活动；用线型区分已核路径与示意关系；地点标签用英文，弹出／说明保留中文异名。','线宽先保持统一；捆、箱、卷、件、照片不能混为一种数量加权。','10','方法建议'],
 ['QGIS','12','选择底图与地图范围','概览可用现代陆地／海岸线背景；需旧图时先保存图幅、年代、尺度、来源并做地理配准及误差核验。建议总览＋局部细节。','现代底图、历史地名和路线证据三者分开；不要自动把今日道路套到1907年。','06；07','M01；M07；M08；M17；方法建议'],
 ['QGIS','13','版面与交付检查','在布局中安排地图、图例、时间范围、点位精度说明和来源；保存项目，按课程提交格式导出。','图注写明示意关系、沿途未核、城市参考点和资料截止日；未确认线段不进入已核路径层。','10','M01；方法建议'],
 ['ArcGIS StoryMaps','14','资料稳定后再做叙事','核对账号功能后，按“莫高窟选择／和田装箱列单／欧洲存放查看／北京接收与复制”组织故事；每段附证据与缺口。','不把这些地点排成所有文献共享的一条路线；express map不替代本地结构化档案。','04；07','M04；M05'],
 ['与Gephi联动','15','用ID串起地图与网络','地图说明保留EventId／ObjectId；将“地点上发生的事”与“参与该事件的人／机构”回到Gephi对照。','分析解释基于证据覆盖；节点度数或地图线条密度不能单独说明历史重要性。','04；05；原Gephi项目','项目数据结构与方法建议'],
]
sheet('08_制作步骤', ['工具／阶段','步骤','操作目标','具体做法','本项目核查点','使用哪张表','说明依据'], steps, [25,14,34,100,100,30,50], freeze='D2')

point_rows=[]
for p in places:
    if isinstance(p[7], (int,float)):
        point_rows.append([p[0],p[2],p[1],p[7],p[8],p[9],'modern_reference','city / urban context; historical venue unlocated',p[12],p[15],'Background point only; not a verified historical venue or stop.',p[10]])
ws_points=sheet('09_点位导入', ['PlaceId','Label','LabelZH','Longitude','Latitude','CRS','PointRole','Precision','SourceURL','Note','MapUse','AuthorityId'], point_rows, [24,48,37,17,17,18,25,60,65,105,65,45], freeze='D2', color='387A9A')
for r in range(2,ws_points.max_row+1):
    for ci in [4,5]: ws_points.cell(r,ci).number_format='0.00000'

legend = [
 ['现代参考点','浅灰空心圆','仅表示地理背景或城市层级位置；与历史场址另列。','09中的5个点；全球／区域概览可以显示。','不能把城市点当某一间库房或营地。'],
 ['历史场址已核','实心圆；颜色表示实物／知识活动类别','先有场址证据和坐标来源，才能进入此层。','目前03中历史场址尚未填数值坐标。','地点在场不自动证明路线经过的道路。'],
 ['端点关系示意','虚线箭头；图层名明确“沿途未核”','起终点、方向与同一批对象已核，沿途缺失；不是实际道路。','05中多数是候选；应先完成各行待补条件。','曲线或直线只是表现方式；不要据示意线长度算运输距离。'],
 ['已核路径','实线箭头；逐段附出处','沿途、先后顺序和对象身份有材料支持；不确定段断开。','本次没有生成可直接导入的已核路径。','不能以今日导航、最短路或探险者个人行程替代对象运输证据。'],
 ['知识活动','不同形状的点；图例注明列单／查看／复制','先显示活动发生地；信件、照片等跨地传播另找两端证据。','和田KE001／003／004；伦敦KE006；北京KE009／010。','KE007成稿地点只属伦敦上下文；KE008意向不显示为已完成成果。'],
 ['待核事项','淡黄或默认关闭图层','推定身份、场址或过程未核；可展示研究问题但不进已核结论。','KE002；KE005；PE001。','“待核验”不等于“没有发生”；也不等于默认已发生。'],
 ['时间检验','原日期＋精度标签','装箱、发运、到件、寄存、入藏各有独立时间。','DH009保留清历并标公历换算；DH004年界不表示持续。','年份记录不要自动变成精确日期并生成旅行耗时。'],
 ['对象检验','ObjectId＋馆藏号／箱号','原卷、复制品、作品和研究者分组使用不同标识。','R0001照片与B0012所示写本不同；B0005不一定全经北京。','未知不能用0；箱、捆、卷、件不能直接相加。'],
 ['来源检验','每点／段显示SourceId和页码','事件来源、坐标来源、几何制作方法分别可追踪。','S01转引S22不算两份独立目击；S19是录文而非原档影像。','搜索摘要、机构回顾和档案原件的证据角色分别写明。'],
 ['提交前检查','图注与表格交叉核对','检查中英文名称、坐标方向、年代、图例、来源与未核范围。','图注建议：现代背景与城市参考点；虚线为流转关系示意，沿途未核；资料截至2026-10-20。','若后续补入已核场址／路径，应按实际情况修改图注。'],
]
sheet('10_图例与核查', ['图层／核查项','建议样式／内容','使用条件','本项目例子','不能忽略的边界'], legend, [26,53,85,95,95], color=NAVY)

# Controlled choices help future manual entry without changing existing records.
dv_status=DataValidation(type='list',formula1='"可导入背景点,待定位,可按文献开展定位,待核地名与坐标,待核历史场址"',allow_blank=False)
ws_places.add_data_validation(dv_status);dv_status.add('O2:O1000')
for ws, lon_col, lat_col in [(ws_places,'H','I'),(ws_points,'D','E')]:
    for col,lo,hi in [(lon_col,-180,180),(lat_col,-90,90)]:
        dv=DataValidation(type='decimal',operator='between',formula1=str(lo),formula2=str(hi),allow_blank=True)
        dv.errorTitle='坐标范围错误';dv.error='请填十进制度数值，并检查经纬度是否倒置。';dv.showErrorMessage=True;dv.errorStyle='stop'
        ws.add_data_validation(dv);dv.add(f'{col}2:{col}1000')

# Make the cover a practical clickable index, while preserving a rectangular table.
nav = {'01_采集字段':'A1','02_工具选择':'A1','03_地点与坐标':'A1','04_事件梳理':'A1','05_移动段待补':'A1','06_优先补采集':'A1','07_资料与来源':'A1','08_制作步骤':'A1','09_点位导入':'A1','10_图例与核查':'A1'}
cover=wb['00_开始使用']
for name in nav:
    r=cover.max_row+1
    cover.append(['打开工作表',name,'点击中间单元格跳转；全部表均可筛选，首行固定。'])
    cover.cell(r,2).hyperlink=f"#'{name}'!A1"
    for c in cover[r]:
        c.font=Font(name='Arial',size=11,color='136BB0' if c.column==2 else '243746',underline='single' if c.column==2 else None)
        c.alignment=Alignment(vertical='center',wrap_text=True)
        c.fill=PatternFill('solid',fgColor='E9F3FB')
    cover.row_dimensions[r].height=32
list(cover.tables.values())[0].ref=f'A1:C{cover.max_row}'

for name, column, forbidden in [('04_事件梳理',14,['待核验']),('05_移动段待补',16,[])]:
    ws=wb[name]
    for r in range(2,ws.max_row+1):
        c=ws.cell(r,column)
        if name=='05_移动段待补' or c.value in forbidden:
            c.fill=PatternFill('solid',fgColor='FFF0CD')
            c.font=Font(name='Arial',size=11,bold=True,color='805D1A')

OUT.mkdir(parents=True,exist_ok=True)
wb.save(FILE)

# Validate the actual saved workbook, not just the in-memory fixture.
saved=load_workbook(FILE, data_only=False)
assert len(saved.sheetnames)==11
ids={p[0] for p in places};eids={e['事件ID'] for e in events};sids={s[0] for s in resources}
assert len(ids)==len(places)==15
assert len(eids)==20 and len(point_rows)==5 and len(segments)==12
assert all(x in ids for p in places for x in p[5].split(';') if x)
assert all(x in ids for e in event_rows for x in e[11].split(';') if x)
assert all(x in eids for s in segments for x in s[1].split(';') if x)
assert all(x in ids for s in segments for x in s[4:6] if x)
assert all(x in sids for p in places for x in p[11].split('；') if x)
assert all(s[14]=='' for s in segments)
for p in places:
    assert (p[7] is None)==(p[8] is None)
    if p[7] is not None: assert -180<=p[7]<=180 and -90<=p[8]<=90
for ws in saved:
    assert ws.freeze_panes and len(ws.tables)==1
    assert not ws.merged_cells.ranges
    for row in ws:
        for c in row:
            assert c.data_type!='f', (ws.title,c.coordinate,'Unexpected formula')
            assert c.value not in ['#REF!','#VALUE!','#DIV/0!','#NAME?']
for row in saved['07_资料与来源'].iter_rows(min_row=2,values_only=True):
    if row[7]: assert Path(row[7]).is_file(), row[7]
for sr in segments:
    for code in re.findall(r'\bS\d{2}\b',sr[13]): assert code in sids, code

input_files=[INPUT/'事件原始记录.csv',INPUT/'来源目录.csv',INPUT/'来源阅读记录.csv',BASE/'06_notes/2026-10-13_双层传播网络补采集/整理版_2026-10-13/双层传播网络_中文记录工作簿_整理版.xlsx',BASE/'06_notes/项目反馈对照与优先事项_2026-10-19.md']
manifest={
 'snapshot_id':'HY5419-map-resources-20261020',
 'date':DATE,
 'scope':'1900–1910；实物流转与知识活动；后出地图和现代坐标仅辅助定位',
 'stance':'项目现有事件的地理证据整理、工具比较与补采集清单；非穷尽路线复原',
 'source_boundary':'本地既有20事件与来源记录；官方软件／地名／地图／坐标网页；11组检索日志',
 'backend':'built-in web fallback; parallel-cli and external research API keys unavailable',
 'inputs':[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in input_files if f.is_file()],
 'counts':{ws.title:ws.max_row-1 for ws in saved},
 'output':str(FILE),
 'output_sha256':hashlib.sha256(FILE.read_bytes()).hexdigest(),
 'unresolved':['10个地点无数值坐标','全部12条候选移动段WKT为空，未生成实际运输几何','Bodleian目录打开受限，IDP页面403；未取得所列档案原件','部分历史机构场址、起点、日期、箱号与批次对应尚待核'],
 'validation':['XLSX重新打开成功；11张工作表','事件、地点、来源编号引用闭合','20条事件、15条地点、12条移动段、5个坐标点数量核对','数值经纬度范围／空值配对核对','没有公式／错误值；全部工作表有筛选表格与冻结窗格','本地文件超链接目标存在','没有将候选线段写成已核实际路径'],
}
(OUT/'sources/input_manifest_and_validation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(FILE),'bytes':FILE.stat().st_size,'sheet_rows':manifest['counts'],'validation':'passed'},ensure_ascii=False,indent=2))
