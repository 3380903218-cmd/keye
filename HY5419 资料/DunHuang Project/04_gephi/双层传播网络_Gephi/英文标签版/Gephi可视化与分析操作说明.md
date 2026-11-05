# HY5419：英文标签、可视化与分析

适用界面：本机Gephi 0.11.3。日期：2026-10-13，新加坡。

## 打开英文数据

File → Open，选择本文件夹的“**双层传播网络_英文标签.gexf**”，导入到新工作区。应为46节点、57条关联边。原中文GEXF和Excel没有修改。

Label和LabelEn是英文短名称；FullLabelEn是完整英文说明；LabelZh和FullLabelZh保存原中文名称。原FullLabel也保留中文。英文名称是显示标签的编辑性翻译，不声称所有批次名和作品工作题名都是正式馆藏题名。京师图书馆使用Jingshi Library；巴黎图书馆使用National Library, Paris，保留历史机构语境。

配套“中英文节点名称对照.csv”包含审阅图中全部52个节点，可按Id核对或调整翻译。来源、页码、研究状态、限制说明和日期仍保留原文；本版没有将所有研究属性全文翻译。

还提供英文实物流转层（30节点、37边）、知识传播层（19节点、20边）和含待核图（52节点、63边）。每个视图配套nodes.csv、edges.csv。打开GEXF以后，无须再追加同一视图的CSV。

## 让当前图更清楚

1. **让全图进入画布。** 图窗左下侧、相机按钮上方有放大镜按钮，悬停找到 **Center On Graph** 后点击。随后用触控板滚动／缩放调整视野。不要点击相邻的Center On Zero代替适应全图。
2. **调布局。** 左下Layout下拉菜单选择 **ForceAtlas 2**。可先尝试Scaling=30、Gravity=1，勾选Prevent Overlap，点击Run；图形趋于稳定后点击Stop。以上数值是本图的试用起点，不是标准答案。若组件持续向外散开，启用Stronger Gravity；若挤在一起，再逐步提高Scaling，最后再次Center On Graph。显示距离不表示地理距离、时间或传播速度。
3. **用颜色区分节点类型。** 左上Appearance → Nodes → 调色盘图标 → Partition → NodeType → Apply。Person、Event、Collection等类别可以分别设置颜色；Collection是分析批次／工作集合，不是逐件馆藏。事件色建议偏浅，人物与机构色较醒目。意向KE008可另手工设金色；按NodeType重新着色会覆盖文件原有的特殊颜色。
4. **放大节点。** Appearance → Nodes → 两个圆圈的大小图标 → Ranking → Degree，先试Min=8、Max=25 → Apply。Degree只作为本次显示的连接数量尺度，不把最大节点直接命名为“最重要人物”。改完大小可再短暂运行ForceAtlas 2的Prevent Overlap。
5. **放大标签。** 底部Nodes尺寸滑块右边的“小圆圈＋上标a”是 **Show Node Labels**。你提供的截图里已经显示标签，主要需要增大字号。左上Appearance → Nodes → T图标 → Unique，先试Size=12 → Apply。底部T旁的下拉箭头可选Fixed等标签大小模式；建议先用Fixed避免缩放时文字再次很小。标签相互压住时，Layout选择 **Label Adjust**，短暂Run后Stop，再适应全图。Noverlap主要处理节点碰撞，不能替代标签调整。
6. **整理最终显示。** Preview中启用Node Labels的Show Labels，选择如Arial的字体和合适字号；调浅边颜色，边粗细可先试0.5–1，适当缩小箭头，再点击Refresh。Preview的设置与Overview相互独立，Overview能看到标签不意味着Preview已经启用。想保留布局和样式，File → Save As另存为.gephi工程。你可以自行从Preview导出SVG或PDF。

从文件自带布局开始也完全可以；仅做节点、标签和颜色调整即可。不必为了画面运行所有布局算法。

布局、外观和Preview流程可参照[Gephi官方入门](https://gephi.org/quickstart/)。本说明的按钮名称还核对了本机0.11.3的资源文件。

## 这个数据集适合分析什么

当前是**人物／机构—事件—对象／载体的关联网络**。57条边对应17条可整理记录，包含9条实物流转记录、7条已发生的知识活动记录和1条有条件编目意向。每条边的含义由Relation解释；不能把所有箭头当作物件运输，也不能把57解释为57次传播。处理状态“可整理”不等于全部档案原件都核实过。

| 研究问题 | 可以怎样操作 | 解释范围 |
|---|---|---|
| 哪些人物参与记录较多？ | Statistics → Average Degree → Run；到Data Laboratory节点表查看Degree并只比较Person行 | 参与／关联次数；没有记录到的行为不进入计数，不是历史影响力 |
| 谁同时参与实物与知识活动？ | 对比两层文件的同一Id，查各边EventId、Role；按不同EventId计数 | 跨层角色；区分个人与考察队，不重复算成一个主体 |
| 哪些节点连接不同记录群？ | 在副本工作区中运行Statistics → Network Diameter，选择Undirected计算关联路径；查看Betweenness Centrality | 忽略箭头后的关联桥接，不是已证实的信息传递、控制权或时间先后 |
| 是否形成不同群组？ | Modularity → Run；Appearance颜色Partition选择Modularity Class | 数据关系的探索性分组；不能直接命名为真实学术派系或历史社群 |
| 哪里有断链或尚未接通的材料？ | Connected Components → Run，选择弱连通／忽略方向，查看组件 | 主图现有两组弱连通组件；可能反映采集缺口，不能断言当时互不往来 |
| 两层结构是否不同？ | 分别打开实物层和知识层，查看人物、对象、载体及组件；逐项比较记录范围 | 这两个视图采集覆盖不同，节点／边更多不能直接说明某层传播更强 |
| 活动随年份怎样分布？ | 利用YearStart、YearEnd、DatePrecision按事件整理 | 当前是静态图，尚未建立Timeline时间区间；年界限不等于持续活动 |

Network Diameter中可以选择计算方向，[Gephi官方FAQ](https://gephi.org/faq/)说明该模块也计算介数中心性。当前多数人物边是“人物→事件”，人物没有对应入边；有向介数可能为零，这是编码方向的结果，不能据此排除人物的跨层作用。使用无向计算时，应明确写“事件关联网络的无向介数”，并保留原有向数据供关系解释。

比较人物时应在完整关联图计算，再在Data Laboratory仅查看Person行。若在图上只筛Person节点，事件节点被移除后大部分／全部边也会消失；本数据没有直接的人物—人物交往边。若将来建立人物共参与投影图，应先明确共同参与的事件定义、计数单位和证据范围。

PageRank、HITS和Eigenvector Centrality可以计算，但本图混合节点类型与关系方向，暂不适合作为人物学术影响力排名。所有边Weight=1，Weighted Degree目前不会提供可比的写本数量；捆、箱、卷与本的单位不同。

## 本版已能追问的跨层人物

以下由主图关联的不同EventId计数，只描述已经登记的记录：

| 人物 | 实物记录 | 已发生知识活动记录 | 另列意向记录 |
|---|---|---|---|
| Jiang Xiaowan 蒋孝琬 | 2：DH001、DH003 | 2：KE001、KE003 | 0 |
| Aurel Stein 斯坦因 | 3：DH001、DH002、DH003 | 2：KE004、KE007 | 0 |
| Paul Pelliot 伯希和 | 1：DH005 | 3：KE006、KE007、KE009 | 1：KE008 |

可以据此提问：取得写本所需的语言与中介工作，怎样延续为列单、索引、检查和备忘录制作？不同人物的取得角色与知识处理角色是否相同？回答仍需回到Role、SourceRef、Locator及对应阅读记录。主图没有把研究者推定的编号归属KE002算入蒋的已发生知识活动计数。

## 自己修改英文标签或切换语言

- 改一个节点：Data Laboratory → Nodes，找到相应Id，编辑Label单元格，回Overview查看结果；只改显示名称，Id仍作为所有边的连接键。
- 英文版中批量切换：Overview图窗右下角展开设置 → Labels → Configure → Nodes，选择LabelEn或LabelZh作为显示字段，取消其他字段以免同时重复显示；完整英文名用FullLabelEn。此选项控制Overview显示，最终Preview通常仍使用Label；希望两处一致时，修改节点Label。
- 若只在Gephi里修改，Save As保存为新的.gephi工程；导入时保持新工作区，以便保留之前已调整的图。

标签字段选择参见[Gephi官方FAQ的标签说明](https://gephi.org/faq/)。

## 校验与重新生成

英文版4个GEXF均由NetworkX独立解析通过；Id、边端点、方向、权重、原属性和初始坐标／颜色／大小与中文输入一致；全部显示标签为英文。校验详情在“英文标签校验记录.json”。本轮没有在Gephi GUI逐个打开测试。

make_english_labels.py中的LABELS以稳定Id保存英文对照。如需调整译名，可编辑该对照再运行；脚本重新写入本英文文件夹的派生GEXF及CSV，不修改父目录中文输入。Python标准库即可转换；安装NetworkX时还会执行独立解析校验。以后新增节点应先补齐对应英文对照再转换，缺译名会明确报错，不会静默遗漏。
