from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable
)


OUT = "/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/seminar 4/seminar4_课程重点与回顾笔记_20260901.pdf"

# Apple system fonts provide Chinese glyphs without requiring a network download.
pdfmetrics.registerFont(TTFont("STHeiti", "/System/Library/Fonts/STHeiti Light.ttc"))
pdfmetrics.registerFont(TTFont("STHeitiMedium", "/System/Library/Fonts/STHeiti Medium.ttc"))

PAGE_W, PAGE_H = A4
INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#526070")
BLUE = colors.HexColor("#1D4ED8")
PALE_BLUE = colors.HexColor("#EAF1FF")
PALE_GOLD = colors.HexColor("#FFF6D8")
PALE_GREEN = colors.HexColor("#EAF8F0")
PALE_RED = colors.HexColor("#FFF0F0")
LINE = colors.HexColor("#D6DEE9")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverKicker", fontName="STHeitiMedium", fontSize=11, leading=16,
    textColor=BLUE, alignment=TA_CENTER, spaceAfter=8
))
styles.add(ParagraphStyle(
    name="CoverTitle", fontName="STHeitiMedium", fontSize=25, leading=35,
    textColor=INK, alignment=TA_CENTER, spaceAfter=12
))
styles.add(ParagraphStyle(
    name="CoverSub", fontName="STHeiti", fontSize=12, leading=20,
    textColor=MUTED, alignment=TA_CENTER, spaceAfter=6
))
styles.add(ParagraphStyle(
    name="H1CN", fontName="STHeitiMedium", fontSize=17, leading=25,
    textColor=INK, spaceBefore=3, spaceAfter=9, keepWithNext=1
))
styles.add(ParagraphStyle(
    name="H2CN", fontName="STHeitiMedium", fontSize=12.3, leading=19,
    textColor=BLUE, spaceBefore=8, spaceAfter=5, keepWithNext=1
))
styles.add(ParagraphStyle(
    name="BodyCN", fontName="STHeiti", fontSize=9.8, leading=16,
    textColor=INK, spaceAfter=6, wordWrap="CJK"
))
styles.add(ParagraphStyle(
    name="BodyTight", fontName="STHeiti", fontSize=9.1, leading=14,
    textColor=INK, spaceAfter=3, wordWrap="CJK"
))
styles.add(ParagraphStyle(
    name="SmallCN", fontName="STHeiti", fontSize=8.1, leading=12,
    textColor=MUTED, spaceAfter=3, wordWrap="CJK"
))
styles.add(ParagraphStyle(
    name="TableHead", fontName="STHeitiMedium", fontSize=8.6, leading=12,
    textColor=colors.white, alignment=TA_LEFT, wordWrap="CJK"
))
styles.add(ParagraphStyle(
    name="TableCN", fontName="STHeiti", fontSize=8.25, leading=12.2,
    textColor=INK, wordWrap="CJK"
))
styles.add(ParagraphStyle(
    name="QuoteCN", fontName="STHeitiMedium", fontSize=11, leading=18,
    textColor=INK, alignment=TA_LEFT, wordWrap="CJK"
))


def P(text, style="BodyCN"):
    return Paragraph(text, styles[style])


def bullets(items, style="BodyCN", bullet_color=BLUE):
    rows = []
    for item in items:
        rows.append([
            P("•", "H2CN"),
            P(item, style),
        ])
    t = Table(rows, colWidths=[7 * mm, 167 * mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("TEXTCOLOR", (0, 0), (0, -1), bullet_color),
    ]))
    return t


def callout(title, text, bg=PALE_BLUE):
    inner = [P(title, "H2CN"), P(text, "BodyTight")]
    t = Table([[inner]], colWidths=[174 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def table(data, widths, header=True, font_size=None):
    converted = []
    for r, row in enumerate(data):
        converted.append([
            P(str(cell), "TableHead" if header and r == 0 else "TableCN")
            for cell in row
        ])
    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0,
              hAlign="LEFT", splitByRow=1)
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                cmds.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7F9FC")))
    t.setStyle(TableStyle(cmds))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.35)
    canvas.line(18 * mm, 14 * mm, PAGE_W - 18 * mm, 14 * mm)
    canvas.setFont("STHeiti", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8.5 * mm, "HY5419 · Seminar 4 · 文本语料库、数字档案与文本分析工作坊")
    canvas.drawRightString(PAGE_W - 18 * mm, 8.5 * mm, f"{doc.page}")
    canvas.restoreState()


story = []

# Cover
story += [Spacer(1, 27 * mm), P("HY5419 · Seminar 4", "CoverKicker"),
          P("文本语料库、数字档案与\n文本分析工作坊", "CoverTitle"),
          P("课程重点、内容梳理与后续思考笔记", "CoverSub"),
          Spacer(1, 14 * mm),
          HRFlowable(width="50%", thickness=1.1, color=BLUE, spaceBefore=3, spaceAfter=15),
          P("一句话总括", "H2CN"),
          P("数字史研究不是按下按钮就得到答案，而是把研究问题、语料库、档案生产链、清洗、分析、解释与反思串成一个可追溯、可复现、会迭代的过程。", "QuoteCN"),
          Spacer(1, 19 * mm),
          P("课程日期：2026 年 9 月 1 日", "CoverSub"),
          P("素材：课堂录音（约 2:14:35）与有道听课宝转写 PDF", "SmallCN"),
          P("本笔记已将转写中的明显识别错误按课堂语境规范化；涉及原声复核时，请以音频为准。", "SmallCN"),
          PageBreak()]

# How to use and overview
story += [P("一、课程地图：今天到底学了什么", "H1CN"),
          P("课堂先回接上周关于公共史、社区研究与研究伦理的讨论，再转入“文本如何被做成可搜索的数据”，由 Gale 讲解数字档案生产与 OCR，最后进入 Digital Scholar Lab 的操作练习。", "BodyCN"),
          table([
              ["时间点（录音）", "课堂段落", "回顾时要抓住的关键词"],
              ["00:33–12:02", "上周问题回顾与研究伦理", "开放获取、社区合作、补偿、风险、AI 与专家协作"],
              ["12:02–30:00", "进入本周主题：语料库与项目设计", "语料库结构、关键词、异质数据、范围、文档化"],
              ["30:34–1:25:11", "Chris（Gale）数字档案幕后讲解", "编辑选择、商业案例、扫描、元数据、OCR、维护"],
              ["1:25:22–1:45:42", "文本与数据挖掘、实验心态", "n-gram、主题建模、探索与推断、迭代、反思"],
              ["1:47:00–2:04:17", "Digital Scholar Lab 动手练习", "Build–Clean–Analyze、内容集、清洗配置、分类主题"],
              ["2:04:27–2:14:28", "总结与下周预告", "工具不是答案；人文学者负责问题、语境与解释；下周空间数据"],
          ], [31 * mm, 52 * mm, 91 * mm]),
          Spacer(1, 8),
          callout("建议的三遍回顾法", "第一遍只看本笔记的“主张”；第二遍按时间点回听，补上讲者的例子；第三遍把“研究日志模板”用于自己的项目，写出一个可执行的小实验。", PALE_GOLD),
          Spacer(1, 10),
          P("六个最需要带走的结论", "H2CN"),
          bullets([
              "数字化不是中性的搬运：选什么、删什么、怎样命名和怎样呈现，都会改变研究者能看到的问题。",
              "语料库的来源、结构、缺失与编辑历史，决定了数据可以支持什么结论；不理解语料库，就无法恰当地解释结果。",
              "OCR 让档案可搜索，但它是概率性的机器读取，不是原文的完美替身；搜索不到不等于文本中不存在。",
              "文本分析适合先探索“数据的轮廓”，再回到原始图像和细读，最后才形成有证据边界的论证。",
              "Build–Clean–Analyze 不是直线流程，而是循环：一次只改少量变量，记录改变，再运行、比较和反思。",
              "工具不会自动产生历史意义；研究问题、语境化、伦理判断与解释仍然是人文学者的工作。",
          ], "BodyTight"), PageBreak()]

# Ethics
story += [P("二、研究伦理：开放、合作与“不要把人当成资料”", "H1CN"),
          P("开场回顾把数字史研究放回更大的制度环境：知识和教育常被当成商品，研究评价又受资金、影响力和机构结构影响。课程并不假装一次课能解决这些结构性问题，但要求研究者看见它们，并在项目设计中作出负责任的选择。", "BodyCN"),
          P("课堂要点", "H2CN"),
          bullets([
              "公共史与开放获取的目标，不只是把成果放到网上，而是让合作社区和更广泛公众能够接触、参与并从研究中受益。",
              "社区研究应从“与人一起研究”出发，而不是“在别人身上取材”。社区成员不欠研究者他们的故事、知识或经历，尤其是仍在世的人。",
              "补偿要询问对方认为什么有意义：可以是报酬、交通与时间补偿，也可以是仪式性礼物、建议、持续投入或建立关系的时间；应在经费申请阶段列入预算。",
              "开放获取有不同层级：公开、限制访问、延迟开放（embargo），甚至不公开数据或成果，都可能是合乎伦理的选项。关键是尽早与社区共同决定。",
              "研究极化或仇恨团体时，要审查对方为何参与、他们想获得什么，以及研究是否会无意中为其观点背书或提供合法性；同时要安排研究者的心理安全与支持资源。",
              "AI 和代码工具可用于早期探索可行性，却不能替代对研究问题、代码逻辑、证据语境和偏差的理解。需要与计算机科学家从项目初期形成公平的“贸易区”式合作。",
          ], "BodyTight"),
          Spacer(1, 6),
          callout("伦理决策的最早节点", "不要等到论文写完才问“能不能发布”。从招募、取样、数据结构设计开始，就写下谁能访问、哪些字段需要遮蔽、谁拥有撤回权，以及研究结果如何回馈社区。", PALE_RED),
          Spacer(1, 8),
          P("回顾问题", "H2CN"),
          table([
              ["问自己", "写下一个具体回答"],
              ["我的数据中有哪些活着的个人、社区或脆弱群体？", ""],
              ["他们对“有价值的回馈”如何定义？我是否真正问过？", ""],
              ["如果公开会造成伤害，限制、延迟或不公开的理由是什么？", ""],
              ["我的分析是否可能被参与者用来合法化有害主张？", ""],
          ], [83 * mm, 91 * mm]), PageBreak()]

# Corpus, keywords, scope and documentation
story += [P("三、先理解语料库，再按下分析按钮", "H1CN"),
          P("语料库不是自然存在的“过去本身”，而是由收藏、选择、数字化、命名、切分、OCR、元数据和平台界面共同制造的研究对象。课堂反复追问：哪些东西被纳入？哪些被留下？哪些语境被移除了？", "BodyCN"),
          P("搜索与语境", "H2CN"),
          bullets([
              "先做近距离阅读，了解来源的年代、体裁、作者、受众和术语习惯，再设计关键词。用今天的概念或拼写去搜历史文本，可能得到零结果。",
              "为拼写变体、旧称、缩写、不同语言和词形建立词表；同时记录哪些变体被合并、哪些被保留。",
              "搜索结果只反映“被 OCR 正确识别、被平台索引、并且用你的词命中”的部分，不等于完整的历史分布。",
              "不同来源的扫描质量、DPI、版式、语言与 OCR 水平可能不同。跨语料库比较前，先问：项目成功的最低数据质量是什么？",
          ], "BodyTight"),
          Spacer(1, 5),
          P("项目范围与数据文档", "H2CN"),
          table([
              ["层级", "要问的问题", "例子"],
              ["必须有（must）", "没有它，项目是否无法回答问题？", "核心年份、关键来源、最基本的 OCR 质量"],
              ["应该有（should）", "有它会让结论更稳健吗？", "另一种来源、可比的元数据、人工抽查"],
              ["可以有（could）", "如果时间和预算允许，什么会提升解释力？", "额外可视化、扩展样本、定制代码"],
              ["暂不做（won’t）", "什么超出范围或无法可靠完成？", "无法验证的超大规模推断"],
          ], [29 * mm, 71 * mm, 74 * mm]),
          Spacer(1, 7),
          callout("文档化不是行政负担，而是方法论的一部分", "记录每一次删选、改名、纠错、参数变化和解释决定。一个星期后你会忘记为什么这样做；更重要的是，没有这些记录，别人无法判断数据是否适合复用，也无法复现你的结果。", PALE_GREEN),
          Spacer(1, 8),
          P("最小数据文档模板", "H2CN"),
          table([
              ["字段", "应记录什么"],
              ["来源与范围", "收藏名称、来源机构、时间范围、文献类型、纳入/排除规则"],
              ["数据处理", "下载日期、文件格式、OCR 版本、清洗规则、拼写变体处理"],
              ["分析设置", "工具、参数、停用词表、运行日期、输出文件名"],
              ["解释与限制", "观察到什么、没有看到什么、可能的替代解释与下一步"],
          ], [40 * mm, 134 * mm]), PageBreak()]

# Archive pipeline
story += [P("四、数字档案的幕后：从收藏到可搜索文本", "H1CN"),
          P("Chris 的核心教学目标，是让使用者知道数字档案并非“透明窗口”。Gale 以商业出版者身份与世界各地档案馆、图书馆和数字化供应商合作；平台上的每一层都包含技术、编辑、商业和制度选择。", "BodyCN"),
          table([
              ["阶段", "做什么", "研究者需要追问"],
              ["1. 编辑构想", "根据学科趋势、课程、研究需求和市场判断主题与收藏。", "谁决定值得数字化？哪些主题被预先想象？"],
              ["2. 商业案例", "估算保存、设备、人工、转换和平台维护成本，决定是否投资。", "商业可行性是否造成了资料偏向？"],
              ["3. 谈判与权利", "与来源馆协商数字化许可、收益分成、版权和服务责任。", "图像知识产权、平台销售权和访问权分别属于谁？"],
              ["4. 扫描成像", "使用高质量设备逐页拍摄；珍贵或脆弱材料可用真空翻页设备。", "装订、变形、褪色、裁切是否改变了可读性？"],
              ["5. 预生产与元数据", "补充标题、作者、日期、出版物、馆藏关系等，使内容可发现、可交叉搜索。", "哪些字段是通用的？哪些是针对某种文献定制的？"],
              ["6. 转换与 OCR", "把数字图像转换成机器可读文本，支撑全文搜索和文本挖掘。", "哪些字符、版式和语言可能被误读或漏读？"],
              ["7. QA、维护与反馈", "抽样检查、修正高频元数据，更新数据库、界面并观察使用情况。", "使用数据如何反过来决定下一批数字化内容？"],
          ], [30 * mm, 74 * mm, 70 * mm]),
          Spacer(1, 8),
          P("规模感", "H2CN"),
          P("课堂给出的数量级提醒是：小型馆藏可能有 35–40 万页，中型约 100–150 万页，大型可达 400–600 万页；Gale 的跨馆藏资源覆盖约九个世纪、六大洲。正因规模巨大，很多质量控制采用抽样而不是逐页人工校正。", "BodyCN"),
          callout("可用性也会塑造研究方向", "平台会根据搜索频率、课程和市场需求决定维护或新增内容；因此“什么能被搜到”会反过来推动研究兴趣。使用平台时既要利用其便利，也要意识到供应商、馆藏选择和界面正在参与知识生产。", PALE_GOLD), PageBreak()]

# OCR
story += [P("五、OCR：搜索入口，也是误差入口", "H1CN"),
          P("OCR（optical character recognition，光学字符识别）通过识别页面上的线条、形状与上下文，把扫描图像转换成机器可读文本。它让研究者可以从实体档案的“逐页翻找”转向全文搜索，但它仍是概率性识别。", "BodyCN"),
          P("课堂示范的关键认识", "H2CN"),
          bullets([
              "OCR 对水平、清晰、规则的印刷体最有把握；装订边弯曲、页面倾斜、褪色、污损、复杂版式、旧字体和多栏排版都会降低准确度。",
              "讲者给出的当代大规模 OCR 经验范围约为 85%–95%（按馆藏而异，来自抽样估计）。这意味着仍可能有相当数量的字符、词和整段文本被误读。",
              "标题、作者、日期、出版物等高频元数据通常会投入额外人工核查；正文则不可能在数百万页规模上逐页纠正。",
              "搜索不到一个词，可能是关键词错了，也可能是拼写变体、OCR 错误或索引缺失。搜索结果需要回到页面图像核对。",
          ], "BodyTight"),
          Spacer(1, 5),
          table([
              ["当你看到……", "不要直接推断……", "应当做……"],
              ["结果为零", "文本里不存在", "换旧称、拼写变体、邻近词；检查原图和上下文"],
              ["词频异常高", "主题真的如此重要", "排查页眉、脚注、模板词、OCR 重复与文献类型偏差"],
              ["乱码或奇怪符号", "数据没有价值", "定位扫描/版式原因，记录清洗规则，保留原始文本"],
              ["可视化很漂亮", "论证已经成立", "抽取样本做细读，说明方法、误差与替代解释"],
          ], [43 * mm, 59 * mm, 72 * mm]),
          Spacer(1, 8),
          callout("研究者的 OCR 三步核查", "① 用多种关键词与变体检索；② 回看原始图像和前后段落；③ 在研究日志中记录 OCR 限制、人工修正和未解决的不确定性。", PALE_RED), PageBreak()]

# Text mining
story += [P("六、文本与数据挖掘：从探索到有边界的推断", "H1CN"),
          P("课堂示例从数字档案下载 PDF、图像或原始 OCR 文本，再用 Voyant Tools（转写中听作“Buoyant”）等免费工具生成词频统计和可视化。文本可以来自十八世纪法令，也可以来自推文；只要能表达为文本，就能被组合、比较和分析。", "BodyCN"),
          P("工具的角色", "H2CN"),
          table([
              ["工具/方法", "它擅长回答什么", "不能单独回答什么"],
              ["词频与 n-gram", "哪些词或词组最常出现？哪些搭配值得追踪？", "某个词为何出现、谁在说、语境和权力关系是什么？"],
              ["词云/统计可视化", "快速获得文本的轮廓和比较线索。", "视觉大小不是历史重要性的直接证明。"],
              ["主题建模", "数据中可能存在哪些主题簇或结构？", "主题标签不是机器自动给出的历史概念，需要人来命名、核查和解释。"],
              ["情感/邻近词分析", "某关键词附近的评价词和倾向如何变化？", "词典、语料、体裁和时代语义会影响“正/负面”判断。"],
              ["细读与跨语料比较", "验证模式、理解例外，并在来源之间作可比比较。", "不能把不同 OCR 质量、体裁和取样方式的数据当成完全同质。"],
          ], [33 * mm, 72 * mm, 69 * mm]),
          Spacer(1, 7),
          P("课堂示例与方法边界", "H2CN"),
          bullets([
              "1930 年代关于计划生育的广播谈话：词频很快提示“出生控制、儿童健康、家庭、母亲”等方向，随后仍需回到原始文档做验证。",
              "妇女参政主题的报纸社论：以 suffragette / suffragism / suffragist 等变体检索，再观察邻近词，发现“militant、opposing、outrage、conspiracy”等负面词群；这提示舆论框架，但不等于整个社会的单一态度。",
              "文本分析有两种用途：一是探索语料库、发现原先没想到的维度；二是在清洗、抽样和验证后，形成可比较的描述或推断。研究问题决定你应停在哪一步。",
          ], "BodyTight"),
          callout("重要转折", "数据不会“自己说话”。你选择哪些文本、如何清洗、使用哪个工具、怎样给主题命名，都是研究者介入；透明记录这些介入，才能把工具输出转化为历史论证。", PALE_BLUE), PageBreak()]

# Lab workflow and exercise
story += [P("七、Digital Scholar Lab：把分析做成可复盘的循环", "H1CN"),
          P("Lab 将 Gale 订阅内容与常见的开源分析工具放在同一个工作区。课堂把界面工作流概括为 Build → Clean → Analyze，但强调它不是单向流水线，而是可以随时返回前一步的迭代循环。", "BodyCN"),
          table([
              ["环节", "课堂操作", "产出/判断"],
              ["Build（构建）", "从已有馆藏检索或上传自己的文本，组成 content set（内容集；课堂说明上限为 10,000 份文档）。", "明确样本边界、来源和纳入规则。"],
              ["Clean（清洗）", "删除数字/特殊字符/标点；find and replace 纠正系统性 OCR 错误；加入 stopwords；命名并保存 cleaning configuration。", "减少噪音，同时保留可追溯的处理决定。"],
              ["Analyze（分析）", "添加 n-grams 与 topic modeling，运行工具，查看词云和主题可视化。", "得到探索性模式，而不是未经核查的结论。"],
              ["Evaluate（评估）", "识别噪音，查看原文与主题内文档，挑出值得细读的词/短语。", "决定下一轮只改变哪些变量。"],
              ["Interpret（解释）", "回到研究问题，比较结果与预期，说明限制、替代解释和下一步。", "形成有证据边界的历史推论。"],
          ], [31 * mm, 88 * mm, 55 * mm]),
          Spacer(1, 8),
          P("课堂动手练习：义和团运动数据集", "H2CN"),
          bullets([
              "在 Learning Center → Analyze datasets 中选择预建的 data set 6：义和团运动相关材料，时间范围 1898–1907，共 111 份文档。",
              "进入 Analyze，添加 n-grams 和 topic modeling，分别运行并查看可视化。",
              "先记录三类噪音：OCR 错误、无信息量的格式/标点、与研究问题无关的高频词。",
              "进入 Clean，创建一个可识别名称的 cleaning configuration；设置数字/标点处理、find and replace 和 stopwords，然后保存。",
              "返回 Analyze，应用该配置并重新运行；比较清洗前后哪些模式消失、哪些模式变得清晰。",
              "从 n-gram 可视化中标出三个值得细读的词或短语；再检查主题模型中的文档，并为主题作暂定分类。",
          ], "BodyTight"),
          callout("每次只改一个关键变量", "若一次改了停用词、标点、样本和模型参数，就无法知道结果为何变化。小步迭代、保存配置、命名输出，才能把“试试看”变成可解释的方法。", PALE_GREEN), PageBreak()]

# Reflection worksheet
story += [P("八、课后回顾工作表：把课堂方法迁移到自己的项目", "H1CN"),
          P("以下问题可直接复制到你的研究日志。不要只记录“结果是什么”，也记录你为什么这样设计、什么没有被看见，以及下次会改变什么。", "BodyCN"),
          table([
              ["阶段", "回顾/记录提示"],
              ["研究问题", "我究竟想解释什么变化、关系、语义或历史经验？这个问题能否被一个小型实验检验？"],
              ["语料库", "文本从哪里来？谁选择和描述了它？时间、体裁、语言、缺失和版权是什么？"],
              ["关键词", "历史时期的人会怎样称呼它？有哪些旧称、拼写变体、转写、歧义词和反例？"],
              ["质量控制", "哪些页面/字段可能 OCR 失败？我检查了多少原图？搜索零结果是否可能是技术问题？"],
              ["清洗", "我删掉了什么？为什么？有没有把本来有历史意义的变体误当噪音？"],
              ["工具", "n-gram、主题模型或其他工具分别提供哪一种证据？为什么适合这个问题？"],
              ["验证", "我是否抽取了代表性、异常性和反例文本做细读？不同来源是否真的可比？"],
              ["解释", "我的推论超出了数据能支持的范围吗？还有什么替代解释？"],
              ["伦理与回馈", "谁可能受到影响？访问限制、匿名化、延迟开放和社区回馈如何安排？"],
              ["下一轮", "如果重做一次，我只会改变哪一个变量？我需要补读、补数据还是换工具？"],
          ], [34 * mm, 140 * mm]),
          Spacer(1, 9),
          P("一页研究日志（可填写）", "H2CN"),
          table([
              ["日期/运行编号", ""],
              ["本轮只改变的变量", ""],
              ["观察到的模式与三个待细读位置", ""],
              ["噪音、缺失与不确定性", ""],
              ["下一步与理由", ""],
          ], [48 * mm, 126 * mm]), PageBreak()]

# Glossary and closing
story += [P("九、术语速查与下周衔接", "H1CN"),
          table([
              ["术语", "本课语境中的简明定义"],
              ["语料库 corpus", "为特定问题收集、组织并可计算分析的一组文本；不是“全部过去”。"],
              ["元数据 metadata", "关于数据的数据，如标题、作者、日期、出版物、来源和馆藏关系。"],
              ["OCR", "把页面图像转换为机器可读文字的光学字符识别过程。"],
              ["n-gram", "连续 n 个词/字符的频率或搭配统计，用于发现重复模式。"],
              ["主题建模", "从词语共现中生成主题簇的探索性方法；主题命名与历史解释需要人参与。"],
              ["停用词 stopwords", "在特定分析中被忽略的高频功能词或无信息量词。"],
              ["清洗配置", "一组可保存、可重复应用的删除、替换、标准化与停用词规则。"],
              ["可复现性", "他人能够依据数据、代码、参数和文档重做你的过程并理解差异。"],
              ["迭代方法", "计划—运行—检查—修改—再运行的循环，而不是一次性得到答案。"],
              ["策展/编辑选择", "决定纳入什么、如何分类、如何呈现和如何关联的知识生产行为。"],
          ], [43 * mm, 131 * mm]),
          Spacer(1, 10),
          callout("下周预告：空间数据与历史地图", "课程将转向旧地图：如何从地图生成或描绘数据，如何探索地图中的具体信息，以及历史学者如何介入空间数据的制作、调解和解释。可把本课的同一组问题带过去：谁制作了数据？什么被省略？平台如何引导问题？", PALE_BLUE),
          Spacer(1, 10),
          P("最后的回顾句", "H2CN"),
          P("当你看到一个漂亮的词云或主题图时，先不要问“它证明了什么”，而要问：“这个结果是由什么问题、什么语料库、什么编辑选择、什么 OCR、什么清洗和什么参数共同制造的？我还需要回到哪些原文，才能把它说成历史？”", "QuoteCN"),
          Spacer(1, 12),
          P("资料说明", "H2CN"),
          P("本笔记依据 2026 年 9 月 1 日课堂录音及配套转写 PDF 整理。转写中存在自动识别造成的专名、术语和句子错误；本笔记按上下文统一了 Gale、Digital Scholar Lab、OCR、Voyant Tools、n-gram、topic modeling、义和团运动等术语，但不替代原始音频、页面图像或课程指定阅读。", "SmallCN")]


doc = SimpleDocTemplate(
    OUT, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
    topMargin=16 * mm, bottomMargin=19 * mm, title="HY5419 Seminar 4 课程重点与回顾笔记",
    author="OpenAI"
)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
