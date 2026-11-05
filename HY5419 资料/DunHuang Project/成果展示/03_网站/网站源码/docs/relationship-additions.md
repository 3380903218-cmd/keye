# Scholarly relationships added in edition 2.8.0

Historical scope: **1900–1910**. Research checked on 30 October 2026.

The original Gephi export remains at `dist/assets/dunhuang-network.gexf`: 122 nodes and 136 relationships. Its bytes, attributes, colours and positions are preserved. The expanded file adds 10 nodes and 21 relationships, making **132 nodes and 157 relationships**. There are 48 activity records and 57 evidence notes, drawing on the same 21 source entries.

The new person is Zhang Yuanji. Other additions specify the roles of people already present: Dong Kang, Wang Shitong, Wang Guowei, Luo Zhenyu, Paul Pelliot and Jin Shaocheng. Dong Kang’s association with the Songfen shi pamphlet imprint is also recorded. No separate person called “Dong Wu” has been established.

| Activity record | Historical date | Source and printed pages | Limitation |
|---|---|---|---|
| SUP_CONTACT1909 | 1909, before the 4 October banquet | G07, p. 45; Dong-to-Luo report: p. 51 n. 3 | Viewing may overlap KE009. The American intermediary’s identity and the earlier route of the news are not asserted. |
| SUP_VIEW1909 | Autumn 1909 | G07, pp. 50–51 | Wang Guowei’s viewing account may overlap KE009; it does not establish another distinct meeting. |
| SUP_LETTER19091222 | 22 December 1909 | G07, p. 49 n. 1 | Joint letter and French translation, not proof of completed publication or original-manuscript transfer. |
| SUP_REPLY1910 | Around August 1910 | G07, p. 49 n. 1 | Approximate arrival of a reply, not proof that photographs arrived or translation was completed. |
| SUP_PARIS191005 | May 1910 | L05, p. 136 | Reconstructed from Zhang’s 1911 letter. The later letter is evidence, not a 1911 network event. |
| SUP_REQUEST19101203 | 3 December 1910 | G07, p. 49 and n. 2 | A request to view Pelliot’s collection; the study states that the intended viewing did not take place. |

These are six additional **records**, not six demonstrably separate historical events. The two Beijing viewing records retain `ParentEventId=KE009`. New node positions are provisional web positions; node sizes are uniform and centralities have not been recalculated. Original node positions and sizes are unchanged.

G07: Qin Hualin, “1909年北京学界公宴伯希和事件补考——兼论王国维与早期敦煌学,” 2018, 48(3), 44–56. L05: Pan Sheng, “时代的遮蔽：敦煌文献早期流散过程中部分史事杂考,” 2025(2), 134–143. The full texts of these studies were checked. Their quoted original diary and letter images were **not independently inspected**; the evidence notes preserve that distinction and supply the primary-document references for follow-up.

No “conceals for Stein” edge is added. Pan’s interpretation of deliberate concealment is discussed alongside the same article’s evidence for awareness of British acquisitions in 1910. Speculative communication failures between Shengyun and Wang Jiayan are not coded as factual transmission edges. En Yuru’s photographs reported in 1912, Tianwo’s 1921 account, Ling Bing’s 1926 appeal and the later IDP fall outside this expansion.

## 在 Gephi 中使用

1. 打开 `dist/assets/dunhuang-network-expanded.gexf`，选择有向图并导入新工作区。应为132个节点、157条关系。原项目继续保留，便于对照。
2. 建议先在数据实验室筛选 `Supplement=2026-10-30`，检查新增人物、活动、角色、`SourceIds`、`EvidenceIds`。`SUP_REQUEST19101203` 是请求，不能改为已经观看。
3. 新节点的位置是网页暂定值。若要形成新的 Gephi 成果，可运行 ForceAtlas 2、调整防重叠与标签，再另存项目；需要分析中心性时重新计算，原大小不能作为新版中心性数值。
4. `network-expanded-nodes.csv` 与 `network-expanded-edges.csv` 是同一补充版的节点表与边表，UTF-8 BOM编码，可用Excel查看。手动导入时先导节点表、后导边表，使用逗号分隔、有向关系，`Id`、`Source`、`Target` 保持字符串。
5. `relationship-supplement-evidence.csv` 列出8条新增证据说明、印刷页码、原始文书定位与证据限度。网页 JSON 下载包含全部57条证据，适合与图中 `EvidenceIds` 对照。

The website shows the full expanded network directly. Four visible reading examples explain the new relationships without requiring interaction. Their locate buttons highlight the corresponding activity in the same full graph. The QGIS map, original exports, preservation section and bilingual/offline reading remain available.

Rebuild downloads with `python3 tools/build_relationship_supplement.py`. The public supplement is `dist/relationship-supplement-data.js`; personal notes and downloaded academic PDFs are not part of the public repository.
