# Gephi 使用步骤：敦煌项目主试点

## 0. 先解决启动问题

我检查到当前电脑里的 `/Applications/Gephi.app` 是 Intel x86_64 版本，而电脑系统是 arm64。如果双击后出现“Bad CPU type”或完全打不开，需要先安装 Rosetta 2，或下载能够在 Apple Silicon 上运行的 Gephi 版本。Gephi 能正常打开后，再进行下面的步骤。

## 1. 新建并保存项目

打开 Gephi，选择 `File > New Project`，马上选择 `File > Save As`，把项目保存到：

`/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/DunHuang Project/04_gephi/`

建议文件名：`dunhuang_pilot_stein_qing.gephi`。

## 2. 导入节点表

进入 `Data Laboratory`，选择 `Import Spreadsheet`。

选择文件：

`03_data_clean/nodes.csv`

在导入窗口设置：

- `Separator`：Comma
- `Charset`：UTF-8
- 勾选第一行为列名
- `Import as`：Nodes table
- 确认 `Id` 是节点唯一编号，`Label` 是显示名称

导入后检查节点表。重点确认：

- `Id` 没有重复或空值；
- `Label` 显示正常；
- `NodeType`、`Role`、`Place` 等字段已经作为节点属性出现。

## 3. 导入边表

仍在 `Data Laboratory`，再次选择 `Import Spreadsheet`。

选择文件：

`03_data_clean/edges.csv`

设置：

- `Separator`：Comma
- `Charset`：UTF-8
- 勾选第一行为列名
- `Import as`：Edges table
- `Source`：Source
- `Target`：Target
- `Type`：Directed

如果 Gephi 询问图类型，选择 `Directed graph`。导入后检查：

- 每个 `Source` 和 `Target` 都能在节点表中找到；
- `Relationship`、`SourceWording`、`Confidence`、`SourceRef` 都存在；
- 没有出现 Unknown node、Missing source 或 Missing target。

本项目主图的正确数量应为：7 个节点、9 条有向事件。

## 4. 先检查方向，再做布局

切换到 `Overview`。先不要急着运行布局，确认箭头方向是否符合数据：

- Cave 17 → Wang Yuanlu：custody
- Wang Yuanlu → Stein expedition：acquisition
- Jiang Xiaowan → Stein expedition：physical transfer
- Stein expedition → British Museum：institutional transfer
- Wang Yuanlu → Qing government：state transfer
- Qing government → Beijing receiving system：institutional transfer

如果方向反了，回到 `Data Laboratory` 检查 `Source` 和 `Target`，不要在图上凭感觉修改箭头。

## 5. 设置节点颜色

在右侧 `Appearance` 面板：

1. 选择 `Nodes`；
2. 选择 `Partition`；
3. 在属性列表中选择 `NodeType`；
4. 点击 `Apply`。

建议颜色含义保持稳定：

- SourceSite：紫色
- Person：蓝色
- Expedition：橙色
- Institution：绿色

颜色表示主体类型，不表示证据等级或道德评价。

## 6. 设置节点大小

在 `Appearance > Nodes > Ranking` 中选择 `Degree`，点击 `Apply`。

建议先使用较小范围，例如最小 10、最大 40。小样本网络中，节点大小只能表示当前数据里的连接数，不能直接解释为历史权力、责任或重要性。

## 7. 运行布局

在左侧 `Layout` 面板：

1. 选择 `ForceAtlas 2`；
2. 勾选 `Prevent overlap`；
3. 点击 `Run`；
4. 图形基本稳定后点击 `Stop`；
5. 再运行 `Noverlap`，处理标签和节点重叠。

注意：ForceAtlas 2 产生的是视觉布局。节点之间的距离不是敦煌、北京、伦敦之间的地理距离，也不是事件发生时间的距离。

## 8. 显示标签和箭头

在 `Overview` 中打开节点标签。标签字段选择 `Label`，不要选择长的 `Notes` 字段。

进入 `Preview`：

- 打开节点标签；
- 打开边；
- 打开有向箭头；
- 调整边宽和标签字号；
- 背景使用白色或浅色；
- 先保证箭头和标签清楚，再调整颜色。

课堂投影时，优先保留 `Cave 17`、`Wang Yuanlu`、`Jiang Xiaowan`、`Stein expedition`、`British Museum`、`Qing government` 和 `Beijing receiving system` 等短标签。

## 9. 运行统计指标

在 `Statistics` 中可以先运行：

- `Average Degree`：查看平均连接程度；
- `Network Diameter`：如需要，再查看 betweenness centrality。

汇报时建议优先报告 degree。当前主试点中，Stein expedition 和 Wang Yuanlu 的连接数最高，但这只是由当前样本和编码方式产生的探索性结果。不要把中心性直接写成历史权力或道德责任。

## 10. 保存和导出

先保存 Gephi 项目。

在 `Preview` 中导出：

- 优先导出 SVG，方便放入 PowerPoint 后缩放；
- 也可以导出 PNG，建议宽度至少 2000 像素；
- 文件名写清楚范围和版本，例如 `dunhuang_pilot_stein_qing_v1.svg`。

导出文件时，在图注或幻灯片中注明：

`Pilot data, 1900-1910; 7 nodes; 9 source-linked events; layout distance is not geographic distance.`

## 11. 伯希和扩展路径怎么导入

伯希和路径不要直接追加到主图。扩展文件是：

- `03_data_clean/nodes_extension_pelliot.csv`
- `03_data_clean/edges_extension_pelliot.csv`

如果要做比较图，建议先另存一个 Gephi 项目，再导入扩展节点和边。扩展数据中的候选巴黎接收机构仍有低可信度标记，不要把它和主图的高可信度边混在一起解释。

## 12. 最常见的错误

### 中文乱码
重新导入时确认 `Charset = UTF-8`。如果仍乱码，使用数据文件的 UTF-8 编码版本，不要改动原始来源文件。

### Unknown node
检查 `edges.csv` 的 `Source` 和 `Target` 是否与 `nodes.csv` 的 `Id` 完全一致。不要用 `Label` 代替 `Id`。

### 没有箭头
确认图类型是 `Directed`，并在 `Preview` 中打开箭头显示。

### 图太乱
先运行 `Noverlap`，减少标签数量，缩短标签。不要为了好看删除有来源的关键节点或边。

### 想把数量做成边权
当前项目不要这样做。“卷”“包”“箱”“件”不是同一计量单位；数量先作为属性保留，所有边暂时使用同等视觉权重。

## 13. 汇报时可以这样解释图

“这是一张基于来源链接事件的探索性有向网络。箭头表示文献支持的方向，颜色表示节点类型，节点大小表示当前样本中的 degree。布局距离不是地理距离。图形的作用是显示已经记录的中介环节，并暴露仍然缺少证据的部分；它不裁定法律所有权、责任或文化归属。”


## 14. Apple Silicon + Rosetta 启动命令

如果双击仍无反应，在用户自己的 Terminal 中运行：

```bash
arch -x86_64 "/Applications/Gephi.app/Contents/MacOS/gephi" --userdir "$HOME/Library/Application Support/gephi-hy5419" --cachedir "$HOME/Library/Caches/gephi-hy5419"
```

窗口出现后，用 `File > Open` 打开 `dunhuang_pilot_stein_qing.gexf`。这个命令使用独立配置目录，不会覆盖原来的 Gephi 配置。
