"""Populate a separate workbook from audited evidence and newly checked local passages."""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, re
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
DATA=PROJECT/'04_gephi/进展gephi数据集'
TEMPLATE=ROOT/'双层传播网络_中文记录工作簿.xlsx'
OUTDIR=ROOT/'整理版_2026-10-13'
OUT=OUTDIR/'双层传播网络_中文记录工作簿_整理版.xlsx'
if OUT.exists():raise SystemExit('Refusing to overwrite an existing organized workbook.')
OUTDIR.mkdir(exist_ok=True)
before=hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()
def read(name):
    with (DATA/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
entities={r['Id']:r for r in read('entities.csv')}
sources={r['SourceID']:r for r in read('sources.csv')}
core={r['EventId']:r for r in read('events.csv')}
evidence=read('event_evidence.csv')
parts=read('event_participants.csv')

object_rows=[]
def obj(oid,kind,name,pressmark,scope,ref,loc,unknown,parent=''):
    object_rows.append([oid,kind,name,pressmark,parent,scope,ref,loc,unknown])
for eid,oid in {'DH001':'B0001','DH002':'B0002','DH003':'B0003','DH004':'B0004','DH005':'B0005','DH006':'B0005','DH007':'O0002','DH008':'B0006','DH009':'B0007'}.items():
    if oid in {r[0] for r in object_rows}:continue
    e=core[eid]
    obj(oid,'原卷（身份待核）' if oid=='O0002' else '批次／集合',
        '1909年送呈样本卷（S19鉴定线索）' if oid=='O0002' else e['Label']+'所涉材料',
        'BD06825；羽025（S19鉴定，未独立核原物）' if oid=='O0002' else '',
        '自建分析ID；不是馆藏号。'+e['QuantitySummary'],e['SourceRef'],'见对应阅读记录及既有event_evidence.csv',
        '样本身份、原档和影像待核；不把既有样本返还计作新增收藏。' if oid=='O0002' else '具体写本号未逐件匹配；不得据批次推定每件材料完整同路。',
        'B0004（汇集关系按S07叙述；逐件映射未知）' if oid in ['B0001','B0002','B0003'] else '')
obj('B0008','工作对象集合','1908年和田列单、编号与索引所涉材料','','与B0004有关的工作集合；逐件范围未知','S07;S03','S07印刷916；S03印刷63/PDF8','列单、编号和索引是相关流程，不是多笔实物取得。')
obj('B0009','范围待限定的集合','1909年抵英后由Andrews整理的Stein材料','','S17原句称Stein finds；不强行等同所有藏经洞写本','S17','AAM/PDF16','哪些箱和哪些对象参与该次整理尚待接收／拆箱清单。')
obj('B0010','工作对象集合','1910年伯希和在伦敦检查的Stein中国写本','','S07印刷916称中国写本24箱；与825页总括材料范围不能逐箱等同','S07','印刷916/摘录PDF6','逐件清单、每箱材料语种及与B0004的精确范围对应未知。','B0004（有关联；范围未逐箱核）')
obj('B0011','临时送寄批次','1910年秋送巴黎编目的first instalment','','仅对应S07此次首次送寄；不等于伯希和1908年取得批次','S07','印刷916/摘录PDF6','寄件责任人、具体对象号、收件与归还记录待核。','B0010（文中关联；具体成员未知）')
obj('B0012','展示对象集合','1909年伯希和在北京出示的少量写本','','S01记small selection；S22记保留随身的几件','S01;S22','S01印刷840/PDF20；S22印刷15/PDF21','不能把任一具体Pelliot写本自动归入该组；实际观看和摄影者未逐一核名。','B0005（来源关联；逐件身份未知）')
obj('O0001','原卷','S03所举Or.8210/S.316写本','Or.8210/S.316；编号778（据S03对应）','题名暂空；743为原卷纪年，不是现代传播年','S03','印刷63/PDF8；图6及注41','需核馆藏影像与MSS Stein272/59原件；未证明该卷属于B0011巴黎批次。')
object_by_event={'DH001':'B0001','DH002':'B0002','DH003':'B0003','DH004':'B0004','DH005':'B0005','DH006':'B0005','DH007':'O0002','DH008':'B0006','DH009':'B0007'}

role_zh={'acquiring_expedition_leader':'取得行动负责人','negotiator':'谈判参与','transport_assistant':'搬运参与','selector':'选取参与'}
def roletext(eid):
    e=core[eid]
    out=[f"{e['Source']} {entities[e['Source']]['Label']}：文中所述转出／拨送主体",f"{e['Target']} {entities[e['Target']]['Label']}：接收行动／机构"]
    for p in parts:
        if p['EventId']==eid:
            out.append(p['EntityId']+' '+entities[p['EntityId']]['Label']+'：'+'／'.join(role_zh.get(x,x) for x in p['Role'].split(';')))
    return '；'.join(out)

nature_map={'participant_retrospective':'参与者自述','participant_near_contemporary':'参与者自述',
 'participant_later_hearsay':'参与者自述（后得消息）','scholarly_archival_reconstruction':'研究者转引',
 'scholarly_synthesis':'研究综合','institutional_retrospective':'机构回顾',
 'archival_transcription':'档案转录','archival_transcription_and_analysis':'档案转录及作者解释',
 'authoritative_calendar_table':'历表（方法）'}
activities={'DH001':'协议取得／相关日期与搬运角色','DH002':'追加取得／数量版本差异','DH003':'追加取得／运输到达与数量版本',
 'DH004':'实物存放／到英及在馆时间旁证','DH005':'选择与取得','DH006':'机构接收','DH007':'样本送呈','DH008':'主批取运／接收','DH009':'续交接收／日期和数量口径'}
reading=[];reading_to_evidence={};record_to_reading={}
for e in evidence:
    rid='RD'+e['EvidenceId'][2:].zfill(4)
    eid=e['RecordId'];ce=core.get(eid)
    layer='实物流转' if ce else '背景'
    action=activities.get(eid,'保管与出入背景' if eid=='CTX001' else '行政命令与运输回顾')
    quote=e['ExcerptOriginal'];par=e['ParaphraseZH']
    ob=object_by_event.get(eid,'藏经洞保管背景' if eid=='CTX001' else '')
    people=roletext(eid) if ce else ('N002王圆箓：控制出入；地点不是上一持有人' if eid=='CTX001' else '学部／中央命令；具体执行交接主体不能从此句补出')
    date=ce['DateDisplay'] if ce else ('1904／1907／1908的不同观察，不能直接视作连续保管区间' if eid=='CTX001' else 'S11作1910；S07回访叙述作1909年底或稍后，分别保留')
    place='／'.join(dict.fromkeys([entities[ce['Source']]['Place'],entities[ce['Target']]['Place']])) if ce else '敦煌' if eid=='CTX001' else '敦煌—北京路线回顾'
    status='可整理事件' if ce else '背景／方法'
    note='；'.join(filter(None,[e['Limitation'],e['Dependency']]))
    note+=('；该摘录支持：'+e['SupportFor']+'，不能把本行引文视为支持全部事件属性。')
    if e['EvidenceId']=='EV003':action='同次取得的搬运参与角色';people='N004蒋孝琬、N015 Ibrahim Beg、N016 Tila Bai：协助搬运；接收地为斯坦因库房'
    if e['EvidenceId']=='EV010':
        layer='知识传播';action='伯希和在伦敦检查中国写本';ob='B0010'
        quote='in the early summer of 1910 Professor Pelliot […] came to London and devoted several weeks of unremitting labour to a rapid examination of those manuscripts.'
        par='1910年初夏伯希和到伦敦，用数周检查斯坦因带回的中国写本。';people='N012伯希和：检查者；N005斯坦因：叙述者'
        date='1910年初夏；具体日未知';place='伦敦'
    if e['EvidenceId']=='EV013':
        layer='知识传播';action='现场清点／查看与选择';ob='待识别的洞内所查文献；不能全部等同B0005已取得材料'
        people='N012伯希和：查看、选择；N002王圆箓：打开洞';note+='；inventaire不自动等于已出版正式目录。'
    if e['EvidenceId']=='EV021':
        quote='样本一卷带返';action='既有样本返还的目录注记与解释';ob='O0002';par='S19引用目录注记，并解释该样本此前已经入账；不能将其再计新增收藏。'
        people='样本的具体经手与归还人未核';date='宣统二年续交文书语境；样本实际归还日未核';status='待核验'
    if e['EvidenceId']=='EV022':
        layer='背景';status='背景／方法';action='清历日期换算（方法记录）';ob='';people='';place=''
        quote='历表读数转写：公历12月13列为十一月十二；12月15列为十一月十四。'
        note+='；此栏为历表读数转写，不是史料叙述原句；不是新增历史事件。'
    if e['EvidenceId']=='EV019':layer='背景';status='背景／方法';action='运京命令与接收机构的概述';people='N011清学部：发令；N009京师图书馆：概述接收机构';note+='；仅作DH008年与机构背景，不能靠命令补王→学部交接。'
    reading.append([rid,e['SourceID'],e['Locator'],quote,par,layer,action,ob,people,date,place,nature_map[e['EvidenceNature']],status,note])
    reading_to_evidence[rid]=e['EvidenceId'];record_to_reading.setdefault(eid,[]).append(rid)

# Newly inspected passages, kept distinct from the frozen core graph evidence.
new_specs=[
 ('S07','印刷916页；摘录PDF6；Collection of Chinese manuscripts段','the weeks available before my final departure from Khotan sufficed only for a first rapid listing of less than a third of them.',
  '斯坦因记述1908年7月在和田让蒋孝琬工作，时间只够初步列出不到三分之一的材料。','知识传播','初步列单','B0008','N004蒋孝琬：列单参与；N005斯坦因：组织与叙述','1908年7月，按原段明确July, 1908','和田','参与者自述','可整理事件','列单范围与对象号未完整核；不把不到三分之一写成完整编目。'),
 ('S03','印刷63页／PDF8；Id2与图5','these numbers were almost certainly written on the manuscripts by Jiang.',
  '研究者将红色苏州码子编号归于蒋孝琬，并把工作置于1908年6–7月和田阶段。','知识传播','写入编号（作者高度推定）','B0008','N004蒋孝琬：研究者所推定编号者','1908年6–7月；图5摄影日为7月31日，不能作为全部编号日','和田','研究者转引','待核验','保留almost certainly；不能把作者的手迹归属判断升级为每卷已核事实。'),
 ('S03','印刷63页／PDF8；Id2索引段','Jiang prepared an index slip list of these 1318 manuscripts',
  '研究者转引记蒋制作1318件材料的索引卡清单，装入箱91；作者称该清单尚未找到。','知识传播','编制索引卡清单','B0008','N004蒋孝琬：据转引制作索引清单','1908年和田装箱阶段；具体制作日未核','和田','研究者转引','可整理事件','索引原件未取得；1318是清单覆盖数，不是本次新增取得量；参见MSS Stein37/119。'),
 ('S03','印刷63页／PDF8；27 June段及图6','on 27 June 1908 in Khotan Stein noted the manuscript 778 which had the date 743.',
  '研究者把1908年6月27日的笔记条目、编号778与Or.8210/S.316对应。','知识传播','笔记记录与对象编号对应','O0001','N005斯坦因：记录者；蒋的识读工作为上下文，个别手迹归属仍需原件','1908年6月27日（研究者转引）；743为写本纪年','和田','研究者转引','可整理事件','核MSS Stein272/59、馆藏影像和编号对应；不据此推定该卷后来送巴黎。'),
 ('S17','AAM/PDF16页；When Stein’s finds段及PDF20注61','Andrews was employed by the India Office Library to unpack, sort and list them.',
  '研究记1909年材料抵英后，Andrews受India Office Library雇用拆箱、分类和列单。','知识传播','拆箱整理、分类与列单','B0009','N017 Frederick Henry Andrews：整理者；雇用机构India Office Library尚未新增实体ID','1909年；确切工作起止日未知','英国／伦敦语境','研究者转引','待核验','明确此处Stein finds范围，核日常工作与机构地点；抵英、拆箱、入藏不等同。'),
 ('S07','印刷916页／摘录PDF6；At my request段','to sum up the main result of his observations in a brief but very instructive memorandum (reproduced below)',
  '斯坦因记伯希和应请求概括观察结果，形成一份备忘录，并称在下文重印。','知识传播','形成检查备忘录','B0010','N012伯希和：备忘录作者；N005斯坦因：请求者','1910年伦敦检查的上下文；成稿具体日未知','伦敦语境','参与者自述','可整理事件','W001为工作命名；未独立核备忘录正文与原稿。1921年重印载体不自动进入1900–1910知识层。'),
 ('S07','印刷916页／摘录PDF6；to express his readiness段','to express his readiness to undertake under certain conditions the preparation of a systematic inventory',
  '伯希和表示愿在一定条件下准备系统清单。','知识传播','有条件同意编目／意向','B0010','N012伯希和：表示编目意向；N005斯坦因：请求与叙述者','1910年伦敦检查安排语境；承诺日未核','伦敦语境','参与者自述','可整理事件','仅录有条件的意向；不得把这一条写成完成编目或已出版目录。'),
 ('S07','印刷916页／摘录PDF6；In the autumn of 1910段','In the autumn of 1910 a first instalment of manuscripts was duly transmitted to Professor Pelliot at Paris for the purpose of being catalogued.',
  '1910年秋，一批手稿被送给巴黎的伯希和，用于编目。','两层关联','为编目目的临时送寄','B0011','N012伯希和：所称送寄对象；实际寄出、承运责任人未载','1910年秋；公历日未知','伦敦馆藏语境→巴黎','参与者自述','待核验','收件、具体对象号与归还待核；不是伯希和1908取得批次初次入藏，也不是已完成编目。'),
 ('S01','印刷840页／PDF20；In August and September 1909段','He brought a small selection of Dunhuang manuscripts, which several scholars examined and photographed.',
  '研究记1909年8–9月伯希和带少量写本到北京，若干学者查看。','知识传播','展示／查看','B0012','N012伯希和：带来／展示；观看者未逐一核名','1909年8–9月（研究者叙述）；不定精确日','北京','研究者转引','可整理事件','该段依赖S22印刷15；人员与具体写本对应待核，不把所有中国学者都画进事件。'),
 ('S01','印刷840页／PDF20；同一展示段','which several scholars examined and photographed',
  '研究记北京学者对这些写本进行摄影。','知识传播','摄影／复制','B0012；对应复制品组R0001','摄影者、底片编号及接收者未逐一核实','1909年8–9月上下文；具体摄影日未知','北京','研究者转引','可整理事件','R0001是文中照片的集合登记，不是已取得的具体影像；逐张对应、复制与刊布去向待核。'),
 ('S01','印刷840页／PDF20；They formed an association句','They formed an association to reproduce and publish the most important texts.',
  '研究记学者组织团体，目的为复制和刊布重要文本。','知识传播','组织与刊布计划线索','B0012；计划的对象范围未核','团体名称、成员与分工未逐一核实','1909年访京上下文；组织日期未核','北京','研究者转引','仅线索','本轮保留为补证线索；不能据目的推定具体出版物已完成或每个人均为合作作者。'),
 ('S22','印刷15页／PDF21；末段右栏；扫描0021','Les érudits de Pékin se succédaient chez moi pour examiner et photographier quelques pièces',
  '伯希和自述北京学者来访，查看并摄影他保留的几件材料。','知识传播','查看与摄影的参与者自述','B0012；对应复制品组R0001','N012伯希和：叙述者与提供接触者；访客未逐一核名','原句未给日；1909框架由S01及演讲上下文限定','北京','参与者自述','可整理事件','S01转引这份材料，二者不算两个独立目击；逐件号、访客与照片去向仍未知。')
]
new_ids=[]
for spec in new_specs:
    rid=f'RD{len(reading)+1:04d}';reading.append([rid,*spec]);new_ids.append(rid)

event_rows=[]
for eid,e in core.items():
    ids=record_to_reading[eid]
    supported=f"{e['Label']}；{e['QuantitySummary']}；来源性质：{e['EvidenceStatus']}"
    unresolved='；'.join(filter(None,[e['QuantityConflict'],e['Notes']]))
    event_rows.append([eid,';'.join(ids),'实物流转',e['Relationship'],object_by_event[eid],'','',e['Source'],e['Target'],e['DateDisplay'],e['DatePrecision'],
        '／'.join(dict.fromkeys([entities[e['Source']]['Place'],entities[e['Target']]['Place']])),roletext(eid),supported,unresolved,'可整理事件',
        '\n'.join(f"{x['SourceID']}：{x['Locator']}" for x in evidence if x['RecordId']==eid)])

def add_event(eid,indices,layer,act,oid,rep='',work='',source='',target='',precision='year',support='',unknown='',status='可整理事件'):
    rs=[reading[i-1] for i in indices]
    event_rows.append([eid,';'.join(r[0] for r in rs),layer,act,oid,rep,work,source,target,rs[0][9],precision,rs[0][10],
        rs[0][8],support or rs[0][4],unknown or rs[0][13],status,'\n'.join(f'{r[1]}：{r[2]}' for r in rs)])

# Reading27 onward maps to the 12 newly inspected rows; RD0010 supplies the London examination.
add_event('KE001',[27],'知识传播','初步列单','B0008',precision='month',unknown='不到三分之一的范围；与下列编号、索引为相关工作流程，不按三次实物交接统计。')
add_event('KE002',[28],'知识传播','手稿编号（归属推定）','B0008',precision='month_range',status='待核验')
add_event('KE003',[29],'知识传播','编制索引卡清单','B0008',work='W002',precision='year',unknown='索引原件未取得，1318为转引覆盖数；不计新增取得。')
add_event('KE004',[30],'知识传播','笔记记录','O0001',work='W003',precision='day_from_secondary')
add_event('KE005',[31],'知识传播','拆箱整理与列单','B0009',status='待核验')
add_event('KE006',[10],'知识传播','检查写本','B0010',precision='season')
add_event('KE007',[32],'知识传播','形成检查备忘录','B0010',work='W001',unknown='工作题名，原稿与正文未独立核；不得据1921载体反推早期发表。')
add_event('KE008',[33],'知识传播','编目意向（有条件）','B0010',unknown='仅支持意向；完成时间、成果与作品ID不能补写。')
add_event('PE001',[34],'两层关联','为编目目的临时送寄','B0011',target='N012',precision='season',status='待核验')
add_event('KE009',[35,38],'知识传播','展示／查看','B0012',precision='month_range',unknown='S01依赖S22；访客、具体写本逐项对应未核；没有给无名访客虚构人物ID。')
add_event('KE010',[36,38],'知识传播','摄影／复制','B0012',rep='R0001',precision='month_range',unknown='具体摄影者、底片和原卷匹配未知；照片组不是完整原卷集合，也不证明已刊布。')

wb=load_workbook(TEMPLATE)
for name,rows in [('阅读记录',reading),('事件整理',event_rows)]:
    ws=wb[name];ws.delete_rows(2,ws.max_row-1)
    for row in rows:ws.append(row)

def sheet(name,headers,rows):
    ws=wb.create_sheet(name);ws.append(headers)
    for r in rows:ws.append(r)
    return ws
sheet('对象与批次',['ObjectId','对象单位','工作名称','馆藏号／旧号（含限定）','关联集合（非逐件已核）','范围与身份说明','来源ID','定位','待核问题'],object_rows)
works=[
 ['W001','备忘录','伯希和关于Stein中国写本检查的memorandum（工作命名）','1910年检查语境；确切成稿日未知','N012伯希和；N005斯坦因请求','S07','印刷916／摘录PDF6','仅由S07记述及称下文重印；本轮未独立核原稿／正文。'],
 ['W002','索引卡清单','蒋孝琬所制手稿索引卡清单（工作命名）','1908年和田工作阶段；制作日未核','N004蒋孝琬（研究者转引）','S03','印刷63／PDF8','作者称尚未找到；1318件与箱91为转引记数。'],
 ['W003','笔记条目','Stein笔记MSS Stein272/59','1908-06-27（S03转引）','N005斯坦因','S03','印刷63／PDF8、图6','S03图6和正文为线索；档案原件未独立取得。']]
sheet('作品与载体',['WorkId','载体类型','题名（工作命名须注明）','原始日期／日期依据','作者或相关人','证据来源ID','证据定位','获取与核验状态'],works)
sheet('复制品登记',['RepresentationId','类型与单位','来源对象组','制作人','日期依据','现存编号／文件','来源ID','定位','对应状态与待核问题'],[
 ['R0001','写本照片组（逐张待识别）','B0012','未逐一核实','1909访京上下文；具体摄影日未核','','S01;S22','S01印刷840/PDF20；S22印刷15/PDF21','仅登记史料所称照片集合；不声称影像已取得，不能将B0012每件原卷都配一张照片。']])
sheet('编号对应',['对应记录ID','ObjectId','编号类型','编号值','来源ID','定位','对应等级与限制'],[
 ['ID001','O0001','现藏编号（据研究）','Or.8210/S.316','S03','印刷63/PDF8','研究者明确对应；本轮未独立核馆藏影像。'],
 ['ID002','O0001','所记编号','778','S03','印刷63/PDF8','红色苏州码子与蓝色编号的描述；日期743指写本纪年。'],
 ['ID003','O0002','现藏编号（作者鉴定）','BD06825','S19','三、（二）样本','作者据目录鉴定；原档与原物影像待独立核验。'],
 ['ID004','O0002','旧号（作者鉴定）','羽025','S19','三、（二）样本','作者所称样本旧号；不能无依据扩展到其他对象。']])

participant_rows=[]
def participation(pid,eid,nid,role,ref,loc,lim):participant_rows.append([pid,eid,nid,role,ref,loc,lim])
for i,e in enumerate(core.values(),1):
    participation(f'WP{i:03d}A',e['EventId'],e['Source'],'转出／拨送主体（按事件定义）',e['SourceRef'],'见阅读记录','不裁定法律所有权；拨送主体不必等于亲自承运人。')
    participation(f'WP{i:03d}B',e['EventId'],e['Target'],'接收行动／机构',e['SourceRef'],'见阅读记录','保留取得、存放和机构接收的区别。')
for p in parts:participation(p['ParticipationId'],p['EventId'],p['EntityId'],p['Role'],p['SourceRef'],p['Locator'],p['Notes'])
for eid,nid,role,ref,loc,lim in [
 ('KE001','N004','初步列单参与','S07','印刷916','不到全部材料三分之一。'),
 ('KE002','N004','编号者（研究者高度推定）','S03','印刷63','almost certainly，待核手迹。'),
 ('KE003','N004','索引卡制作（据转引）','S03','印刷63','原索引未取得。'),
 ('KE004','N005','笔记记录者','S03','印刷63','原档未独立取得。'),
 ('KE005','N017','整理者','S17','AAM/PDF16','对象范围与工作日期尚待核。'),
 ('KE006','N012','检查者','S07','印刷916','不是新取得。'),
 ('KE007','N012','备忘录作者（据S07）','S07','印刷916','具体题名／正文未核。'),
 ('KE007','N005','请求者','S07','印刷916','请求不计一次实物交接。'),
 ('KE008','N012','有条件表示编目意向','S07','印刷916','不等于完成编目。'),
 ('PE001','N012','所称送寄对象','S07','印刷916','实际收件日未核；转出及承运人未补写。'),
 ('KE009','N012','展示提供者／叙述者','S01;S22','S01印刷840；S22印刷15','具体访客未逐一核名。')]:
    participation(f'WP_NEW{len(participant_rows)+1:03d}',eid,nid,role,ref,loc,lim)
sheet('参与角色',['参与记录ID','事件ID','主体ID','具体角色','来源ID','定位','限制'],participant_rows)

background_rows=[r for r in reading if r[5]=='背景' or r[0]=='RD0037']
sheet('背景与补证线索',list(c.value for c in wb['阅读记录'][1]),background_rows)
new_entities=[['N017','Frederick Henry Andrews','Frederick Henry Andrews','Person','受India Office Library雇用的材料整理者','Fred Andrews','新增至此工作簿；依据S17 AAM/PDF14、16；对象范围待核，不修改旧Gephi实体表。']]
for r in new_entities:wb['现有主体ID'].append(r)

guide=wb['从这里开始']
guide.insert_rows(2,7)
guide_rows=[
 ('本版状态','2026-10-13快速整理版：按既有26条证据与本轮12条新增摘录填入阅读记录；是研究记录工作簿，未自动替换Gephi主图。'),
 ('阅读记录与事件数','阅读行不是事件数，同一事件可有多条来源。事件整理包括既有DH001–DH009，以及新知识活动和临时送寄记录；背景、日期换算与刊布计划线索单列。'),
 ('怎样继续','先筛选“待核验”补对象身份、具体参与者与原件；再筛“可整理事件”审查是否足以生成需要的网络关系。'),
 ('同一物的连接','已能在批次层面连接Pelliot取得与巴黎接收；其他汇集、检查与临时送寄的范围关系均在对象表保留限定，不强行逐件配对。'),
 ('知识行为的等级','编号手迹推定、复制品组和编目意向都有单独限定；查看不等于取得，摄影不等于出版，编目意向不等于完成。'),
 ('新增IDs','新增N017与ObjectId、WorkId、RepresentationId仅在本整理版登记。B为自建批次／集合ID，O为原物，均不伪称馆藏编号。'),
 ('原始文件','原工作簿和旧Gephi数据保留。本文件已另存，示范记录仍与实际阅读记录分开。')]
for i,r in enumerate(guide_rows,2):
    guide.cell(i,1,r[0]);guide.cell(i,2,r[1])
guide_revisions={
 'ID建议':'本版已用RD0001–RD0038、PE001、KE001–KE010、B0001–B0012、O0001–O0002、R0001、W001–W003及N017。继续记录从RD0039、PE002、KE011、B0013、O0003、R0002、W004开始；新主体从N018、新来源从S26检查后分配。',
 '现有主体和来源':'主体表含原14条与本版新增N017 Andrews；来源表为既有25条来源快照。新增主体、来源均应登记依据，不在未知处补名字。',
 '表的状态':'阅读记录和事件整理已填入本轮资料；示范记录另表保留。原来空白工作簿、旧Gephi数据与原文献保留。'}
for row in guide.iter_rows(min_row=2):
    if row[0].value in guide_revisions:row[1].value=guide_revisions[row[0].value]

statuses=['待核验','可整理事件','仅线索','背景／方法','排除']
natures=['参与者自述','参与者自述（后得消息）','档案原件','档案转录','档案转录及作者解释','机构回顾','研究者转引','研究综合','目录记录','历表（方法）','未核']
def dropdown(ws,col,options):
    dv=DataValidation(type='list',formula1='"'+','.join(options)+'"',allow_blank=True)
    dv.showErrorMessage=True;dv.error='请选择列表值；未知信息可留空。';ws.add_data_validation(dv);dv.add(f'{col}2:{col}1000')
for name in ['阅读记录','示范记录']:
    ws=wb[name];ws.data_validations.dataValidation=[]
    dropdown(ws,'F',['实物流转','知识传播','两层关联','背景']);dropdown(ws,'L',natures);dropdown(ws,'M',statuses)
wb['事件整理'].data_validations.dataValidation=[]
dropdown(wb['事件整理'],'C',['实物流转','知识传播','两层关联']);dropdown(wb['事件整理'],'P',statuses)

for ws in wb:
    ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions;ws.sheet_view.zoomScale=80
    ws.row_dimensions[1].height=44
    for cell in ws[1]:
        cell.fill=PatternFill('solid',fgColor='24465A');cell.font=Font(name='PingFang SC',size=11,bold=True,color='FFFFFF');cell.alignment=Alignment(wrap_text=True,vertical='center')
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font=Font(name='PingFang SC',size=11);c.number_format='@';c.alignment=Alignment(wrap_text=True,vertical='top')
            c.fill=PatternFill('solid',fgColor='F1F6F9' if row[0].row%2==0 else 'FFFFFF')
        if ws.title in ['阅读记录','事件整理','背景与补证线索']:ws.row_dimensions[row[0].row].height=128
        elif ws.title in ['对象与批次','作品与载体','复制品登记','编号对应']:ws.row_dimensions[row[0].row].height=100
        elif ws.title=='从这里开始':ws.row_dimensions[row[0].row].height=65
        else:ws.row_dimensions[row[0].row].height=70
    if ws.title not in ['从这里开始','阅读记录','事件整理','示范记录','现有主体ID','现有来源ID']:
        for col in ws.columns:ws.column_dimensions[col[0].column_letter].width=30
        for col in ['C','F','H','I']:
            if ws.max_column>=ord(col)-64:ws.column_dimensions[col].width=48
    if ws.title in ['阅读记录','事件整理']:
        status_col=13 if ws.title=='阅读记录' else 16
        for i in range(2,ws.max_row+1):
            c=ws.cell(i,status_col)
            c.fill=PatternFill('solid',fgColor={'待核验':'FFF0CC','可整理事件':'DFF2E4','仅线索':'E8E5F2','背景／方法':'E1EAF0'}.get(c.value,'FFFFFF'))
    ws.print_title_rows='1:1'
wb['阅读记录'].cell(1,1).comment=Comment('阅读ID唯一；阅读行数不等于事件数。','HY5419')
wb.active=wb.sheetnames.index('阅读记录')
wb.save(OUT)

# Companion CSVs preserve workbook values and contain no invented missing endpoints.
for name in ['阅读记录','事件整理','对象与批次','作品与载体','复制品登记','编号对应','参与角色']:
    ws=wb[name]
    with (OUTDIR/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
        csv.writer(f).writerows([[c.value if c.value is not None else '' for c in row] for row in ws.iter_rows()])

check=load_workbook(OUT)
assert check['阅读记录'].max_row-1==38
assert check['事件整理'].max_row-1==20
assert len({r[0] for r in reading})==len(reading)
assert len({r[0] for r in event_rows})==len(event_rows)
reading_ids={r[0] for r in reading};object_ids={r[0] for r in object_rows};work_ids={r[0] for r in works};event_ids={r[0] for r in event_rows}
entity_ids=set(entities)|{'N017'}
for r in reading:
    assert r[1] in sources and r[2] and r[3] and r[4]
    assert r[12] in statuses and r[11] in natures
for r in event_rows:
    assert set(r[1].split(';'))<=reading_ids
    assert r[4] in object_ids
    assert not r[5] or r[5]=='R0001'
    assert not r[6] or r[6] in work_ids
    for nid in r[7:9]:assert not nid or nid in entity_ids
    assert r[15] in statuses
for r in participant_rows:assert r[1] in event_ids and r[2] in entity_ids
assert len(set(object_ids))==len(object_rows)
assert before==hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()
assert next(r for r in event_rows if r[0]=='PE001')[7]==''
assert next(r for r in event_rows if r[0]=='KE008')[3]=='编目意向（有条件）'
assert all('完成编目'!=r[3] for r in event_rows)
assert check['示范记录'].max_row==4
report={'status':'passed','date':'2026-10-13','file':OUT.name,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
 'reading_records':len(reading),'event_records':len(event_rows),'core_physical_events_reused':9,
 'new_dispatch_record':1,'knowledge_activity_records':10,'objects_or_groups':len(object_rows),
 'work_records':len(works),'representation_groups':1,'participant_records':len(participant_rows),
 'event_status_counts':dict(Counter(r[15] for r in event_rows)),
 'reading_status_counts':dict(Counter(r[12] for r in reading)),
 'template_unchanged':True,'original_Gephi_dataset_unchanged':True,
 'input_files':[{'path':str((DATA/f).relative_to(PROJECT)),'sha256':hashlib.sha256((DATA/f).read_bytes()).hexdigest()} for f in ['events.csv','entities.csv','sources.csv','event_evidence.csv','event_participants.csv']],
 'checked_new_passages':['S03 printed63/PDF8','S01 printed840/PDF20','S17 AAM/PDF16','S07 printed916 scan0412','S22 printed15 scan0021'],
 'verification':['Workbook reopen and CSV exports','Unique reading/event/object IDs','Source, entity, object, work and event references','Missing physical dispatch sender retained','No completed-cataloguing event inferred from intention','Examples remain separate','Original workbook hash unchanged'],
 'scope':'Quick organization of already collected material, not a full-text exhaustive review or a Gephi graph release.'}
(OUTDIR/'整理版校验记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(OUTDIR/'整理说明.md').write_text(f'''# 中文记录工作簿整理版

2026-10-13。共{len(reading)}条阅读记录、{len(event_rows)}条事件整理记录：9条既有实物流转、1条待补证的临时送寄、10条知识活动；另登记{len(object_rows)}个原物／批次／工作集合、3份作品或载体、1个逐张待识别的照片组。

先打开“阅读记录”，再看“事件整理”。绿色“可整理事件”表示来源可支持限定行为，仍保留参与者自述、研究者转引或档案转录的限制；黄色“待核验”优先补身份、手迹、端点或原档。背景和方法记录、刊布计划线索不直接进入事件主表。

新增记录来自现有S07、S03、S17、S01和S22。Pelliot北京展示与摄影的S01转引S22，不能作为两份独立目击。临时送巴黎的寄件人未知仍留空；编目意向未写成完成编目。对象和批次号是分析ID，具体成员未核时不强行补对应。

整理版另存，原来正在Excel打开的空白工作簿、旧Gephi文件与原文献均保留。本轮没有把新增记录直接追加到Gephi，也未声称全部38行对应38次历史事件。

CSV为工作簿的表格副本，不是已经生成的Gephi边表。现有9条DH事件与之前数据保持一致，其余记录需按两层关系和证据阈值生成下一版网络。完整字段、来源、待核项均保留在工作簿中。
''',encoding='utf8')
print(json.dumps({k:report[k] for k in ['status','reading_records','event_records','objects_or_groups','knowledge_activity_records','event_status_counts','template_unchanged']},ensure_ascii=False))
