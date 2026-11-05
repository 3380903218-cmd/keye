from pathlib import Path
import json, math

ROOT=Path(__file__).resolve().parent.parent
META=ROOT/'_素材来源与核验'
qa=json.loads((META/'媒体核验.json').read_text())
infos={}
for name in ['download_results.json','youtube_download_results.json']:
 for r in json.loads((META/name).read_text()):
  if r['status']=='downloaded':infos[r['number']]=r
notes={
 '01':('优先','振兴保护区，是否也改变了街道的用途和使用者？','以史密斯街更新作为具体案例，接你的店屋与街巷实拍。','Henderson；Goh；Yeoh & Kong','这是2023年的计划报道，不能当作2026年的最终成效；文件名中的“争议”是选材分类。'),
 '02':('补充','旅游收入能够帮助哪些商家继续营业？','呈现旅游低迷、空铺与租金减免，说明商家也可能需要游客。','Henderson；Poulios','报道发生于疫情后旅游复苏阶段；租金减免是当时的措施，不能概括为长期租金趋势。'),
 '03':('优先','更新带来的收益和成本，分别落在谁身上？','与01形成前后对照，保留生意改善和租金、人手压力两方面。','Henderson；Poulios；Goh','“最高约40%”是部分受访商家的销售变化，不能写成整个牛车水统一增长40%。'),
 '04':('补充','保护店屋以外，政策如何支持传统行业继续经营？','为“建筑保护需要配合经营条件”提供政策背景。','Poulios；Goh','报道涉及多个历史街区；其他街区的受访者和镜头不能标为牛车水。'),
 '05':('补充','官方的总体租金判断，与商家的经营压力如何并存？','呈现统计层面和个别商家的不同诉求。','Henderson；Goh','涉及Kampong Glam、Little India和Chinatown；不可把其他街区的租金个案套用于牛车水。'),
 '06':('优先','传统如何在当下的劳动、学习和社区联系中延续？','接你拍到的白新春店面，让观众看到店内工艺、经营者和传承活动。','Poulios；Chan','国家文物局的表彰短片，适合展示实践，也应说明其推广、表彰视角；不代表全体居民。'),
 '07':('可选扩展','谁能决定历史人物在公共空间中怎样被表现？','如需讨论文化形象与管理权，可短用壁画及艺术家的讲述。','Chan；Goh','属于公共艺术与历史再现的旁支；这是2024年7月的艺术家采访，不是壁画争议全过程。'),
 '08':('补充','展示过去生活，与支持今天的生活，是否是同一件事？','使用原貌馆展陈作转场，引出“看见历史”与“继续使用街区”的关系。','Chan；Yeoh & Kong','馆内的复原展陈是当代展示，不能标注为1950年代实拍。'),
 '09':('补充','节庆中醒目的文化形象，与平日的街道有什么联系？','用灯饰和市集，与自己的普通日街景形成对照。','Chan','这是2025年春节的特定场景；节庆热闹本身不能证明日常文化消失或保育成功。'),
 '10':('优先','传统商家如何继续服务社区，而不只作为过去的展品？','白新春段落约00:25–01:30，可接06及你的店面实拍，呈现社区活动与持续经营的意义。','Poulios；Henderson；Goh','约01:30后转向其他族群、其他街区的商家；不要标为牛车水。关于现代化与保留年长员工的细节见配套文字报道，不是该短片中已核实的采访引语。文件日期按YouTube元数据2026-11-01，配套CNA文字报道日期为2026-11-02。'),
}
def tm(sec):
 n=int(sec);return f'{n//60:02d}:{n%60:02d}'
total=sum(r['duration_seconds'] for r in qa)
size=sum(r['bytes'] for r in qa)
lines=[
 '# HY5417 牛车水视频：网络补充素材与来源',
 '',
 '整理日期：2026年11月5日。选材依据：`HY5417_Annotated_Bibliography_WangXiwen.docx`，以及已有13段实拍的画面抽查。',
 '',
 f'本次新增 **{len(qa)}段完整视频**，共约 **{tm(total)}**，约 **{size/1e6:.1f} MB**（十进制）。全部为1920×1080、H.264视频与AAC音轨的MP4，保留原发布版本，没有放大、去水印或改写画面。原有13段实拍保留原文件名。',
 '',
 '## 先看哪些',
 '',
 '优先看 **01、03、06、10**：史密斯街更新计划 → 更新后商家的收益与压力 → 白新春的传承实践 → 经营延续与社区联系。这组材料最贴近你提出的“保存建筑之后，什么样的生活能够继续、谁能够参与决定”的问题。02可补充旅游对商家生存的支持作用；08、09用于讨论文化展示；07适合需要时扩展。',
 '',
 '这些材料是剪辑素材池，不需要全部放入成片，也不需要用完原片。你的论证和实地观察仍应主导叙事。',
 '',
 '## 下载清单',
 '',
 '| 编号 | 优先程度 | 文件／主题 | 来源日期 | 时长 | 原发布者 |',
 '|---|---|---|---|---|---|',
]
for q in qa:
 num=q['file'].split('_')[1];r=infos[num];date=r.get('upload_date','');date=f'{date[:4]}-{date[4:6]}-{date[6:]}'
 institution=r.get('uploader') or ('CNA Lifestyle' if num=='07' else 'CNA')
 label=q['file'].removesuffix('.mp4') if hasattr(str,'removesuffix') else q['file'][:-4]
 lines.append(f'| {num} | {notes[num][0]} | [{label}](./{q["file"]}) | {date} | {tm(q["duration_seconds"])} | {institution} |')
lines += ['', '## 每段如何服务你的问题', '']
for q in qa:
 num=q['file'].split('_')[1];r=infos[num];n=notes[num]
 lines += [f'### {num} — {q["file"][len("网络_00_00000000_"):-4]}','',
  f'- 原片标题：{r["title"]}',
  f'- 来源：[{"Roots Sg / National Heritage Board" if num=="06" else "CNA Lifestyle" if num=="07" else "CNA"}]({r["source_url"]})',
  f'- 对应问题：{n[1]}',f'- 建议用途：{n[2]}',f'- 对应阅读：{n[3]}（这是选材与阅读的关联判断，不表示文献讨论了这个后来发生的个案。）',
  f'- 使用边界：{n[4]}',
  f'- [六帧画面预览](./_素材来源与核验/画面预览/{q["file"][:-4]}.jpg)','']
 if num=='01':lines += ['背景补读：[CNA关于史密斯街更新与绅士化风险的报道](https://www.channelnewsasia.com/singapore/smith-street-revamp-chinatown-businesses-look-preserve-culture-experts-warn-against-gentrification-3958941)；[SLA联合招标公告，2023-11-30](https://www.sla.gov.sg/news/press-release/rejuvenating-smith-street-to-enhance-the-inclusiveness-and-vibrancy-of-chinatown/)。','']
 if num=='07':lines += ['事件结局补读：[CNA，2024-07-10：壁画完整保留，楼宇业主因未事先申请被罚款](https://www.channelnewsasia.com/singapore/samsui-woman-mural-smoking-chinatown-no-changes-building-owner-fined-4469331)。若提及事件，不宜停留在最初要求修改的阶段。','']
 if num=='10':lines += ['[配套文字报道，2026-11-02](https://www.channelnewsasia.com/singapore/heritage-business-scheme-nhb-new-customers-challenges-remain-6512471)。','']
lines += [
 '## 与已有实拍衔接', '',
 '- `3c6c67f7b5272aa2324fa98dd3a134e0.mp4` 拍到白新春店面，可接06的店内工艺与讲述，再接10关于社区活动和持续经营的讲述。',
 '- `0287720ba6da6426f2cb2676c01483db.mp4` 的沿街衣物展示，以及其他店铺、餐饮、街巷画面，可与01、03中的经营与用途变化配合。',
 '- 店面类型与街道画面可作为你的观察材料；仅凭一段外观镜头，不能判断店家租金、店龄、客户群或是否替代了旧商户。',
 '- [已有13段实拍的缩略图总览](./_素材来源与核验/画面预览/已有13段实拍_画面总览.jpg)。实拍合计约2分38秒。',
 '',
 '## 字幕与署名', '',
 '04和09另存了来源提供的英文VTT字幕；其余视频没有下载到独立字幕文件，画面内原有字幕保留。另外留存了10的YouTube平台英文自动字幕用于核对内容，位于辅助文件夹的`sources/`，未当作人工校对字幕交付。没有自行转录或翻译字幕。',
 '',
 '片尾可按“发布机构，原片标题，发布日期，来源网址”列出实际使用的片段。保留原始台标及受访者标识。各片版权仍属原权利人；本次下载不等于取得公开重用授权。',
 '',
 '## 历史影像候选：未下载', '',
 '[Changing Landscapes: Chinatown（1981），国家档案馆条目](https://www.nas.gov.sg/archivesonline/audiovisual_records/record-details/4840ed79-1164-11e3-83d5-0050568939ad)。档案号1997001872，英语，条目时长44分钟，播出日期1981-09-11，涉及保护与现代化的不同意见及居民生活。条目注明复制和使用需版权方书面许可，复制申请处理可能需7个工作日。它未计入上面的10段已下载视频。',
 '',
 '## 文件核验记录', '',
 '全部新增MP4均进行了完整音视频解码检查；分辨率、时长、音轨、文件大小、SHA-256及解码结果见 `_素材来源与核验/媒体核验.json`。各片原始元数据、下载日志、原始网络检索结果和六帧预览保存在同一辅助文件夹中。预览图只用于选材，时间标签是该图在原片中的位置，不是已确认的采访引用区间。',
 '',
 '本轮检索使用research-lookup的来源留存方法；本机未安装parallel-cli，使用可用的网页检索工具替代，结果已保存在`sources/`。',
]
(ROOT/'00_网络素材清单与使用建议.md').write_text('\n'.join(lines)+'\n')
merged=[]
for q in qa:
 num=q['file'].split('_')[1];merged.append({**infos[num],**q,'priority':notes[num][0],'question':notes[num][1],'suggested_use':notes[num][2],'scope_note':notes[num][4],'retrieved_date':'2026-11-05'})
(META/'素材总清单.json').write_text(json.dumps(merged,ensure_ascii=False,indent=2))
print('Guide written:',len(qa),'videos',tm(total),round(size/1e6,1),'MB')
