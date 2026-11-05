from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUT_DIR = Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5417/seminar 4')
OUT_PDF = OUT_DIR / 'HY5417_Seminar4_课堂重点整理_索姆纳特神庙.pdf'

PAGE_W, PAGE_H = A4
# ReportLab's ``mm`` constant is already expressed in points.  The original
# draft divided these values by 25.4 a second time, leaving only a few points
# of margin and causing section titles to collide with the running header.
# These point values give a readable ~22 mm side margin and room for the
# header/footer while keeping the compact study-guide tables legible.
LEFT = 62
RIGHT = 62
TOP = 54
BOTTOM = 43
CONTENT_W = PAGE_W - LEFT - RIGHT

NAVY = HexColor('#17324D')
NAVY_2 = HexColor('#1C405B')
BLUE = HexColor('#2E6590')
INK = HexColor('#202A33')
MUTED = HexColor('#5D6973')
RULE = HexColor('#D8E0E5')
GOLD = HexColor('#C69C52')
PALE_BLUE = HexColor('#EAF1F7')
PALE_CYAN = HexColor('#E8F2F0')
PALE_GOLD = HexColor('#F6EFE2')
PALE_GRAY = HexColor('#F3F5F6')
WHITE = colors.white


def register_fonts():
    font_dir = Path('/System/Library/Fonts')
    pdfmetrics.registerFont(
        TTFont('HeitiSC', str(font_dir / 'STHeiti Light.ttc'), subfontIndex=1)
    )
    pdfmetrics.registerFont(
        TTFont('HeitiSC-M', str(font_dir / 'STHeiti Medium.ttc'), subfontIndex=1)
    )
    pdfmetrics.registerFontFamily(
        'HeitiSC', normal='HeitiSC', bold='HeitiSC-M', italic='HeitiSC', boldItalic='HeitiSC-M'
    )


def make_styles():
    return {
        'body': ParagraphStyle(
            'body', fontName='HeitiSC', fontSize=9.25, leading=14.25,
            textColor=INK, spaceAfter=5.2, wordWrap='CJK', splitLongWords=True,
        ),
        'body_tight': ParagraphStyle(
            'body_tight', parent=None, fontName='HeitiSC', fontSize=8.65, leading=12.3,
            textColor=INK, spaceAfter=3.6, wordWrap='CJK', splitLongWords=True,
        ),
        'small': ParagraphStyle(
            'small', fontName='HeitiSC', fontSize=8.0, leading=10.8,
            textColor=MUTED, spaceAfter=3.0, wordWrap='CJK', splitLongWords=True,
        ),
        'tiny': ParagraphStyle(
            'tiny', fontName='HeitiSC', fontSize=7.25, leading=9.25,
            textColor=MUTED, spaceAfter=2.0, wordWrap='CJK', splitLongWords=True,
        ),
        'h1': ParagraphStyle(
            'h1', fontName='HeitiSC-M', fontSize=18.5, leading=23.5,
            textColor=BLUE, spaceBefore=1, spaceAfter=5.5, wordWrap='CJK',
        ),
        'h2': ParagraphStyle(
            'h2', fontName='HeitiSC-M', fontSize=12.7, leading=17.0,
            textColor=NAVY, spaceBefore=4, spaceAfter=4.5, wordWrap='CJK',
        ),
        'h3': ParagraphStyle(
            'h3', fontName='HeitiSC-M', fontSize=10.2, leading=13.5,
            textColor=NAVY, spaceBefore=3, spaceAfter=2.5, wordWrap='CJK',
        ),
        'meta': ParagraphStyle(
            'meta', fontName='HeitiSC', fontSize=7.45, leading=10.0,
            textColor=MUTED, spaceAfter=4.2, wordWrap='CJK',
        ),
        'section_meta': ParagraphStyle(
            'section_meta', fontName='HeitiSC', fontSize=8.15, leading=11.0,
            textColor=MUTED, spaceAfter=6.0, wordWrap='CJK',
        ),
        'callout_title': ParagraphStyle(
            'callout_title', fontName='HeitiSC-M', fontSize=9.4, leading=12.2,
            textColor=NAVY, spaceAfter=3.0, wordWrap='CJK',
        ),
        'callout_body': ParagraphStyle(
            'callout_body', fontName='HeitiSC', fontSize=8.65, leading=12.2,
            textColor=INK, wordWrap='CJK', splitLongWords=True,
        ),
        'quote': ParagraphStyle(
            'quote', fontName='HeitiSC', fontSize=9.35, leading=14.0,
            textColor=NAVY, leftIndent=8, rightIndent=5, spaceAfter=5,
            wordWrap='CJK', splitLongWords=True,
        ),
        'table_head': ParagraphStyle(
            'table_head', fontName='HeitiSC-M', fontSize=7.9, leading=10.2,
            textColor=WHITE, alignment=TA_LEFT, wordWrap='CJK', splitLongWords=True,
        ),
        'table_cell': ParagraphStyle(
            'table_cell', fontName='HeitiSC', fontSize=7.75, leading=10.25,
            textColor=INK, wordWrap='CJK', splitLongWords=True,
        ),
        'table_cell_small': ParagraphStyle(
            'table_cell_small', fontName='HeitiSC', fontSize=7.2, leading=9.25,
            textColor=INK, wordWrap='CJK', splitLongWords=True,
        ),
        'cover_kicker': ParagraphStyle(
            'cover_kicker', fontName='HeitiSC-M', fontSize=10.0, leading=13.0,
            textColor=GOLD, tracking=1.0, wordWrap='CJK',
        ),
        'cover_title': ParagraphStyle(
            'cover_title', fontName='HeitiSC-M', fontSize=26.0, leading=34.0,
            textColor=WHITE, spaceAfter=6, wordWrap='CJK',
        ),
        'cover_sub': ParagraphStyle(
            'cover_sub', fontName='HeitiSC', fontSize=13.0, leading=19.0,
            textColor=HexColor('#D9E8F1'), spaceAfter=8, wordWrap='CJK',
        ),
        'cover_meta': ParagraphStyle(
            'cover_meta', fontName='HeitiSC', fontSize=8.8, leading=13.0,
            textColor=HexColor('#C9D6DE'), wordWrap='CJK',
        ),
        'cover_note': ParagraphStyle(
            'cover_note', fontName='HeitiSC', fontSize=7.7, leading=11.0,
            textColor=HexColor('#B5C6D0'), wordWrap='CJK',
        ),
        'cover_index': ParagraphStyle(
            'cover_index', fontName='HeitiSC-M', fontSize=8.0, leading=10.5,
            textColor=HexColor('#B5C6D0'), alignment=TA_RIGHT, wordWrap='CJK',
        ),
    }


STYLES = None


def P(text, style='body'):
    return Paragraph(text, STYLES[style])


def plain(text, style='body'):
    return Paragraph(escape(text), STYLES[style])


def bullets(items, style='body_tight', bullet_color=BLUE):
    out = []
    for item in items:
        # A literal ASCII hyphen keeps extraction/search robust and avoids font-specific bullets.
        out.append(Paragraph(f'<font color="{bullet_color.hexval()}"><b>-</b></font> {item}', STYLES[style]))
    return out


def callout(title, body, kind='blue'):
    bg, edge = {
        'blue': (PALE_BLUE, BLUE),
        'cyan': (PALE_CYAN, HexColor('#4C8278')),
        'gold': (PALE_GOLD, GOLD),
        'gray': (PALE_GRAY, HexColor('#8A99A4')),
    }[kind]
    inner = [P(title, 'callout_title'), P(body, 'callout_body')]
    t = Table([[inner]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('LINEBEFORE', (0, 0), (0, -1), 3.2, edge),
        ('BOX', (0, 0), (-1, -1), 0.35, edge),
        ('LEFTPADDING', (0, 0), (-1, -1), 11),
        ('RIGHTPADDING', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return t


def label_box(label, body, kind='blue'):
    bg, edge = {
        'blue': (PALE_BLUE, BLUE),
        'cyan': (PALE_CYAN, HexColor('#4C8278')),
        'gold': (PALE_GOLD, GOLD),
        'gray': (PALE_GRAY, HexColor('#8A99A4')),
    }[kind]
    label_p = Paragraph(f'<b>{label}</b>', STYLES['table_cell_small'])
    body_p = Paragraph(body, STYLES['table_cell_small'])
    t = Table([[label_p, body_p]], colWidths=[72, CONTENT_W - 72])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), edge),
        ('TEXTCOLOR', (0, 0), (0, -1), WHITE),
        ('BACKGROUND', (1, 0), (1, -1), bg),
        ('BOX', (0, 0), (-1, -1), 0.35, edge),
        ('LINEBEFORE', (1, 0), (1, -1), 0.35, edge),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return t


def data_table(rows, widths, header=True, small=False, repeat_rows=1):
    style_cell = 'table_cell_small' if small else 'table_cell'
    converted = []
    for r, row in enumerate(rows):
        converted.append([
            P(str(cell), 'table_head' if header and r == 0 else style_cell)
            for cell in row
        ])
    ts = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.35, RULE),
    ]
    if header:
        ts += [
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('LINEBELOW', (0, 0), (-1, 0), 0.8, GOLD),
        ]
        for i in range(1, len(rows)):
            if i % 2 == 0:
                ts.append(('BACKGROUND', (0, i), (-1, i), PALE_GRAY))
    else:
        for i in range(len(rows)):
            if i % 2 == 1:
                ts.append(('BACKGROUND', (0, i), (-1, i), PALE_GRAY))
    t = Table(converted, colWidths=widths, repeatRows=repeat_rows if header else 0, hAlign='LEFT')
    t.setStyle(TableStyle(ts))
    return t


def section_heading(number, title, subtitle, timecode):
    return [
        P(f'{number:02d}  {title}', 'h1'),
        P(f'{subtitle}  |  音频定位 {timecode}', 'section_meta'),
        HRFlowable(width='100%', thickness=0.7, color=RULE, spaceBefore=0, spaceAfter=9),
    ]


class ChainFlowable(Table):
    pass


def argument_chain(labels):
    arrow_width = 22
    cells = []
    for i, label in enumerate(labels):
        if i:
            cells.append(P('->', 'h3'))
        cells.append(P(label, 'table_cell_small'))
    widths = []
    for i in range(len(cells)):
        widths.append(arrow_width if i % 2 else (CONTENT_W - arrow_width * (len(labels) - 1)) / len(labels))
    t = Table([cells], colWidths=widths, hAlign='LEFT')
    ts = [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]
    for i in range(0, len(cells), 2):
        ts += [
            ('BACKGROUND', (i, 0), (i, 0), PALE_BLUE if (i // 2) % 2 == 0 else PALE_CYAN),
            ('BOX', (i, 0), (i, 0), 0.45, BLUE),
        ]
    t.setStyle(TableStyle(ts))
    return t


def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(HexColor('#1C405B'))
    canvas.circle(PAGE_W + 18, PAGE_H - 36, 148, fill=1, stroke=0)
    canvas.setFillColor(HexColor('#244D69'))
    canvas.circle(-22, 80, 105, fill=1, stroke=0)
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1.0)
    canvas.line(LEFT, 104, PAGE_W - RIGHT, 104)
    canvas.setStrokeColor(HexColor('#496B83'))
    canvas.setLineWidth(0.5)
    canvas.line(LEFT, PAGE_H - 74, PAGE_W - RIGHT, PAGE_H - 74)
    canvas.restoreState()


def body_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.55)
    canvas.line(LEFT, PAGE_H - 29, PAGE_W - RIGHT, PAGE_H - 29)
    canvas.setFont('HeitiSC', 7.35)
    canvas.setFillColor(MUTED)
    canvas.drawString(LEFT, PAGE_H - 21, 'HY5417 课堂笔记 | Somnath / Somanatha')
    canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 21, '2026-09-03')
    canvas.line(LEFT, 30, PAGE_W - RIGHT, 30)
    canvas.setFont('HeitiSC', 7.05)
    canvas.drawString(LEFT, 18, '根据课堂录音、自动转写与课程大纲整理 | AI 辅助，供复习使用')
    canvas.drawRightString(PAGE_W - RIGHT, 18, f'{doc.page:02d}')
    canvas.restoreState()


def build_story():
    story = []
    story.append(NextPageTemplate('body'))
    # Cover
    story += [
        Spacer(1, 84),
        P('HY5417  ·  SEMINAR 4', 'cover_kicker'),
        Spacer(1, 17),
        P('索姆纳特神庙<br/>（Somnath / Somanatha）', 'cover_title'),
        P('民族主义、历史叙事与选择性记忆', 'cover_sub'),
        Spacer(1, 20),
        P('Contested Sites: Built Heritage and Historical Memory', 'cover_meta'),
        Spacer(1, 6),
        P('课程日期  2026 年 9 月 3 日<br/>录音约 2:06:06  ·  自动转写 PDF 142 页', 'cover_meta'),
        Spacer(1, 158),
        P('本册用途', 'cover_kicker'),
        Spacer(1, 6),
        P('把课堂论证、案例时间轴、概念工具和研究方法放在同一条回听路径上。时间码来自自动转写并以音频时长校对；转写中的专名与数字已按上下文校正或标注待核。', 'cover_note'),
        Spacer(1, 13),
        P('Wang Xiwen  ·  NUS 2026-1', 'cover_index'),
        PageBreak(),
    ]

    # Page 2: executive summary
    story += section_heading(1, '先看结论', '一页掌握本节课的论证主线', '00:00-02:06:00')
    story.append(callout(
        '全课中心论点',
        '索姆纳特争议并不只是“谁毁了神庙”的事实争论。课堂真正追问的是：不同历史框架如何选择、压缩并重写过去，再把这种叙事固定在建筑、物件和国家仪式中，以定义“我们”、制造“他者”，并服务当下的政治目标。',
        'gold',
    ))
    story.append(Spacer(1, 10))
    story.append(P('六个必须记住的结论', 'h2'))
    story += bullets([
        '<b>民族国家不是自然容器。</b>它是近代历史中形成的政治形式，需要通过抽象价值、教育、媒体和象征不断被解释与维持。',
        '<b>民族主义依赖选择性记忆。</b>共同体通常要突出共同点、放大某些损失，同时把内部差异和复杂历史移到叙事边缘。',
        '<b>爱国主义与民族主义不能简单等同。</b>课堂借助戴高乐的区分说明：民族主义更容易通过敌我边界来组织归属。',
        '<b>历史学家提供“原材料”，政治行动者负责动员。</b>复杂研究一旦进入学校、媒体、纪念仪式或旅游营销，就可能被简化成身份工具。',
        '<b>索姆纳特的长时段历史被压缩为一次“穆斯林毁坏”。</b>殖民叙事和后殖民民族主义都可能重复这一缩减。',
        '<b>重建既能保存信仰和国家承诺，也可能清除考古层。</b>一旦物质证据被拆除，未来能够知道的内容就永久减少。',
    ], 'body_tight')
    story.append(Spacer(1, 7))
    story.append(P('可背诵的分析链', 'h2'))
    story.append(argument_chain(['物质遗址', '选择性解释', '情感与敌我', '国家象征', '现实动员']))
    story.append(Spacer(1, 9))
    story.append(callout(
        '读题提醒',
        '遇到“遗址归属”“重建是否尊重历史”“这是宗教冲突吗”等题目，不要只回答立场。先拆开物质层、叙事层、行动者、受众、制度后果和被省略的证据。',
        'cyan',
    ))
    story.append(PageBreak())

    # Page 3: lecture map
    story += section_heading(2, '课堂地图', '按时间码回听：从民族主义概念到研究伦理', '00:00-02:06:00')
    story.append(P('时间码由 852 个自动转写节点汇总，通常以约 10 秒为间隔；个别句子可能有数秒偏差。约 01:03:00 处为课堂休息/下半场转折。', 'meta'))
    rows = [
        ['录音时间', '板块', '教授在做什么 / 回听问题'],
        ['00:00-04:50', '导入与 Hobsbawm', '承接帕台农、圣索菲亚等案例；提出遗址是否中立、谁拥有解释权，并引出“历史学家提供民族主义原材料”的比喻。'],
        ['04:50-10:00', '民族主义概念', '区分爱国主义与民族主义；说明“他者”、抽象价值和想象共同体。'],
        ['10:00-26:30', '德国例子', '以 1815、1848、1871 和 Arminius、Luther、Kulturkampf 说明国家边界与历史英雄都是被定义出来的。'],
        ['26:30-35:00', '索姆纳特登场', '介绍 Gujarat、遗址的反复毁建与重用；追问为什么公共叙事只记住一次事件。'],
        ['35:00-54:00', '殖民叙事与门', '讨论 Gibbon、James Tod、Ellenborough 及“Gates of Somnath”；欧洲宗教战争框架如何被带到南亚。'],
        ['54:00-01:03', '历史观与编年', '比较希腊/西方、中国和印度关于过去的不同用途；警惕把殖民判断当作中性事实。'],
        ['01:03-01:18', '重建与考古', '转入独立后重建；考古研究、铭文和建筑层与“国家承诺”之间的张力。'],
        ['01:18-01:52', '选择性记忆', '“真实历史”、印度教民族国家、Partition、德国/奥地利及当代政治比较。'],
        ['01:52-02:06', '方法与收束', '历史学家的危险位置、沉默与证据限度、遗址破坏的不可逆性；预告 Ayodhya。'],
    ]
    story.append(data_table(rows, [70, 82, CONTENT_W - 152], small=True))
    story.append(Spacer(1, 10))
    story.append(callout(
        '时间码使用法',
        '准备概念题：优先回听 00:04:50-00:10:00、00:54:00-01:03:00。准备案例题：回听 00:26:30-00:54:00、01:03:00-01:30:00。准备方法题：回听 01:52:00-02:06:00。',
        'blue',
    ))
    story.append(PageBreak())

    # Page 4: toolbox
    story += section_heading(3, '概念工具箱', '把课堂口语转成可用于答题和研究的分析语言', '00:00-02:06:00')
    rows = [
        ['术语', '本课中的工作定义', '在索姆纳特案例中问什么'],
        ['Built heritage / 建成遗产', '具有物质形态、历史层累和社会使用史的建筑或遗址。', '保留的是哪一层？拆除、改建或重建改变了什么？'],
        ['Historical memory / 历史记忆', '群体在当下选择、传播和使用的过去，不等于过去本身。', '谁把哪一次毁坏变成共同体必须记住的事件？'],
        ['Selective memory / 选择性记忆', '主动突出某些片段并压低其他片段的公共叙事机制。', '反复毁建、改作清真寺和地方多样性为何被压缩？'],
        ['Imagined community / 想象共同体', '成员彼此并不认识，却通过媒介、教育和抽象价值想象为同一体。', '谁被纳入“印度人”，谁被放到“外来者”位置？'],
        ['Instrumentalization / 工具化', '把历史、遗址或宗教情感转化为政治合法性、动员或治理资源。', '“门”“废墟”和“屈辱”服务了谁的当下目标？'],
        ['Historiography / 历史编纂', '不仅是事件叙述，也是关于证据、时间和因果的文化方法。', '谁规定什么算“真正的历史”？'],
        ['Reuse / 再利用', '建筑被改造、拆解或赋予新功能；既是物质变化，也是权力声明。', '新建筑是否必须抹去旧层，才能表达新的身份？'],
        ['Totalizing discourse / 总括性话语', '把复杂生活和历史归入单一、全面的真理框架；民族主义可以但不必成为此类话语。', '“印度就是印度教国家”是否排除了其他经验？'],
        ['Epistemic humility / 认识论谦抑', '明确证据边界，区分知道、推断和无法知道的部分。', '遗址被毁后，哪些问题只能保留为未决？'],
    ]
    story.append(data_table(rows, [112, 202, CONTENT_W - 314], small=True))
    story.append(Spacer(1, 10))
    story.append(callout(
        '三层分辨',
        '同一句“索姆纳特被毁了”至少包含三层：物质事件（建筑发生了什么）、叙事选择（后来如何讲述）、政治使用（现在用它来证明什么）。写作时不要把三层压成一个事实。',
        'gold',
    ))
    story.append(PageBreak())

    # Page 5: opening / Hobsbawm
    story += section_heading(4, '导入：遗址为什么会被“激活”？', '从前几周的宗教建筑案例转向民族主义', '00:00-04:50')
    story.append(P('教授先承接帕台农神庙、圣索菲亚和科尔多瓦清真寺-主教座堂等案例：问题不只是建筑“原来是什么”，还包括谁拥有它、谁有解释特权，以及遗址能否真正保持中立。历史可能一直存在于空间中，却要等旅游局、国家、宗教组织或媒体把它说出来，才成为公共问题。', 'body'))
    story.append(P('Hobsbawm 的“罂粟种植者”比喻', 'h2'))
    story.append(P('课堂引用 Eric Hobsbawm 的比喻：历史学家之于民族主义，类似罂粟种植者之于海洛因使用者 - 他们提供原材料。教授随后补充，政治家和制度是把原材料加工、包装和分发出去的中介。这个比喻的重点不是指控每位历史学家有意宣传民族主义，而是提醒我们：学术叙述一旦离开课堂，就可能被重新剪裁。', 'body'))
    story.append(argument_chain(['过去的材料', '历史学家的选择', '政治中介与媒介', '公共记忆', '身份与政策']))
    story.append(Spacer(1, 11))
    story.append(label_box('课堂问题', '如果遗址本身沉默，谁有权替它发声？“保护”说明、旅游路线、纪念仪式和重建工程是否同样在解释历史？', 'blue'))
    story.append(Spacer(1, 9))
    story.append(callout(
        '注意引文状态',
        '自动转写把 Hobsbawm、poppy growers 等专名多次误识别。此处只保留课堂比喻的意旨；若论文需要逐字引用，应回听录音并核对原文版本。',
        'gray',
    ))
    story.append(PageBreak())

    # Page 6: nationalism
    story += section_heading(5, '民族主义如何制造“我们”？', '爱国主义、他者与抽象共同体', '04:50-10:00；01:44:59-01:46:59')
    story.append(P('课堂用一个常被归于 Charles de Gaulle 的区分来打开讨论：爱国主义强调对自己家园和人民的爱；民族主义更容易通过对“不是我们的人”的敌意来定义自己。无论引文的确切出处如何，教授要学生抓住的是结构差异，而不是背诵一句名言。', 'body'))
    rows = [
        ['维度', '较接近爱国主义的表达', '民族主义式的动员'],
        ['归属来源', '可经验的家乡、邻里和生活关系。', '与陌生人共享抽象身份，靠语言、文化、历史和制度媒介连接。'],
        ['边界机制', '不必先设定敌人。', '常通过一个外部他者或“世袭敌人”划界。'],
        ['共同体规模', '较容易通过日常经验确认。', '必须依靠学校、报纸、电视、社交媒体、纪念物和仪式想象。'],
        ['风险', '地方自豪感也可能排他，但不必然总括。', '把复杂社会压成单一身份，容易把少数群体写成外来者。'],
    ]
    story.append(data_table(rows, [78, 190, CONTENT_W - 268], small=True))
    story.append(Spacer(1, 9))
    story.append(P('民族国家是历史现象，不是自然状态', 'h2'))
    story += bullets([
        '教授把民族国家放在 18 世纪末至 19 世纪欧洲的历史进程中讨论。更早时期，人们也生活在王国、帝国、领地和城邦共和国中。',
        '“法国先成为民族国家”“拿破仑创造新体系”等是课堂的概括性说法；答题时应说明它们是分析入口，不是没有争议的唯一时间表。',
        '新加坡作为城市国家的例子说明：地理和社会经验越容易被直接体验，抽象的全国共同体越容易被日常化；大型国家则更依赖媒介和象征。',
    ], 'body_tight')
    story.append(PageBreak())

    # Page 7 German case
    story += section_heading(6, '德国案例：边界、英雄与敌人都是“定义”', '用熟悉的欧洲史检验民族主义的生成机制', '10:00-26:30')
    story.append(P('教授反复说明，选择德国不是为了把某个国家单独“钉在被告席上”，而是为了展示自己熟悉的民族主义如何运作。德国的例子揭示：同一片土地可以同时拥有多种历史谱系，国家最终采用哪一条，取决于政治协商、战争和制度安排。', 'body'))
    rows = [
        ['节点', '课堂叙述', '分析意义'],
        ['1815', '维也纳会议后的德意志邦联；边界内有德语与非德语人口。', '语言、疆域和民族并不天然重合。'],
        ['1848', '法兰克福议会尝试建立宪政民族国家，并向普鲁士国王提供皇冠；国王以君权来源为由拒绝。', '“人民授予的国家”与“神授君权”竞争。'],
        ['1866-1871', '普鲁士击败奥地利并排除奥地利；1871 年德意志帝国在对法战争胜利后建立。', '战争把外部敌人和内部统一绑在一起。'],
        ['帝国内部', '课堂以巴伐利亚保留某些军政与外交特权为例。', '统一并不等于内部差异消失。'],
    ]
    story.append(data_table(rows, [70, 248, CONTENT_W - 318], small=True))
    story.append(Spacer(1, 9))
    story.append(P('被选出的历史人物', 'h2'))
    story += bullets([
        '<b>Arminius（Hermann）</b>：公元 9 年击败罗马军队的日耳曼首领，19 世纪被塑造成“德国区别于罗马”的象征。',
        '<b>Martin Luther</b>：宗教改革人物；反罗马、反教皇的叙事可被纳入德国身份，但南德大量天主教人口使这种叙事始终不完整。',
        '<b>Bismarck 与 Kulturkampf</b>：课堂举例（制度细节待核）说明，国家与天主教会的权力冲突，以及婚姻登记、教会税和牧师政治活动等制度，都可能参与定义“合格的德国人”。',
        '<b>法国作为“世袭敌人”</b>：教授以法语的拉丁语源和法兰克人名称反讽“我们憎恨法国两千年”的说法，说明敌意需要被后人不断教会。',
    ], 'body_tight')
    story.append(callout('答题句式', '民族身份不是从地图或血缘自动读出来的，而是通过边界、象征、制度和被选择的过去反复定义出来的。', 'cyan'))
    story.append(PageBreak())

    # Page 8 Somnath timeline
    story += section_heading(7, '索姆纳特：长时段遗址被压缩成单一事件', '先把建筑史与后来的记忆史分开', '26:30-29:00；01:52:12-01:53:31')
    story.append(P('索姆纳特（Somnath / Somanatha）位于印度西部古吉拉特邦，处在印度洋世界和多种政权往来的交通节点。教授先强调它“历史很长”，经历过多次建造、毁坏、改作和再利用；随后马上指出，公共叙事却往往只谈马哈茂德·加兹尼的那一次袭击。', 'body'))
    rows = [
        ['阶段', '课堂/材料中的说法', '证据状态与写作提醒'],
        ['约 649 CE', '课堂转写为遗址最早见于记录的时间。', '专名和句子在录音中不够清楚；写论文前核对 Thapar 或一手材料。'],
        ['约 7-8 世纪（课堂举 735）', '课堂提及一位印度教国王重建。', '年代与行动者待核；不要据此推断之后每次毁坏都是同一模式。'],
        ['约 1024/25', '马哈茂德·加兹尼的袭击/毁坏成为后世最醒目的节点。', '课堂转写写 1024；学术写作常见 1025/26，日期应查原始来源。'],
        ['后续时期', '反复重建、毁坏、改作清真寺或形成废墟，再被重新解释。', '完整序列在课堂未逐项核实；避免把复杂过程简化成单线宗教战争。'],
        ['独立后', '在民族国家叙事中以“重建”取代废墟的可见性。', '重建的政治史与 1951 年落成等细节需对照课程阅读。'],
    ]
    story.append(data_table(rows, [82, 215, CONTENT_W - 297], small=True))
    story.append(Spacer(1, 9))
    story.append(argument_chain(['多次毁建与再利用', '被挑出的 1024/25', '“国耻”情感', '民族复兴', '新神庙']))
    story.append(Spacer(1, 10))
    story.append(callout(
        '核心辨析',
        '“反复毁建”是遗址的物质史；“只记住马哈茂德”是记忆史；“必须重建一座新神庙”是政治行动。三者相互关联，但不能互相替代。',
        'gold',
    ))
    story.append(PageBreak())

    # Page 9 colonial narrative
    story += section_heading(8, '殖民叙事：把南亚放进欧洲的宗教战争框架', 'Mahmud of Ghazni、Gibbon 与 James Tod', '29:00-40:00')
    story.append(P('课堂把英国殖民知识生产放在一个“移植框架”中解释。教授认为，欧洲读者熟悉十字军东征、收复失地运动、君士坦丁堡和格拉纳达等故事，于是容易把南亚的穆斯林征服想成基督教世界与伊斯兰世界冲突的镜像。这个框架先把印度想象为单一的印度教国家，再把穆斯林统治写成外来的历史伤害。', 'body'))
    story.append(P('课堂还把 James Tod 与 Stamford Raffles 作对比：Raffles 谈前伊斯兰马来文明时承认当地人未必共享同一记忆；Ellenborough 则更直接地替一个“假想的印度人”发声。两者都提示我们，殖民作者的文化表象不能自动代表地方社会。', 'body_tight'))
    story.append(P('课堂朗读文本的修辞功能', 'h2'))
    story.append(P('录音中朗读了一段华丽的英文叙述，描写马哈茂德、寺庙财富、成千上万的信徒、婆罗门赎金和宝石等。转写无法可靠确认该段的具体版本，课堂随后又谈到 Edward Gibbon 与 James Tod，因此本册不把数字当作已核实事实，而把它当作叙事证据来读。', 'body'))
    rows = [
        ['叙事元素', '产生的情感效果', '历史学家的追问'],
        ['英雄化的征服者', '把袭击写成勇气、骑士精神或宗教使命。', '作者借用了哪一种熟悉的欧洲类型？'],
        ['神圣偶像与亵渎', '把建筑变成“我们”受伤的身体。', '谁被设定为拥有纯粹的宗教身份？'],
        ['巨大财富与伤亡数字', '制造震撼和道德确定性。', '数字来自何种来源，是否为修辞夸张？'],
        ['八百年屈辱', '把遥远事件连续接到殖民统治和当下。', '“集体记忆”在事件发生时真的已经存在吗？'],
        ['被掠走的门', '把物件变成可移动的胜利标志。', '物件的来源和政治意义是否相同？'],
    ]
    story.append(data_table(rows, [100, 150, CONTENT_W - 250], small=True))
    story.append(Spacer(1, 9))
    story.append(callout(
        '不要把殖民文本当透明窗口',
        'James Tod 等殖民作者可能以“替印度人发声”的姿态写作，但这并不自动赋予其代表印度人的合法性。文本首先是殖民者的分类、情感和读者预期的产物。',
        'blue',
    ))
    story.append(PageBreak())

    # Page 10 Gates
    story += section_heading(9, '“索姆纳特之门”：物件如何制造国耻与胜利', 'Lord Ellenborough 的殖民 spectacle', '40:00-54:00')
    story.append(P('据 Lord Ellenborough 声称，一组来自加兹尼陵墓的门是索姆纳特神庙被掠走的门；他以“归还”方式把它们带回印度。门的来源是课堂反复要求核对的说法，并非本册独立确认的史实。课堂强调，这不是单纯的文物运输，而是一次公开的政治 spectacle：1842 年（课堂所述，年份与宣言细节待核）门被装车、覆盖、护送、展示，并被解释为英国替印度人报了八百年前的仇。', 'body'))
    story.append(argument_chain(['门（物件）', '“来自索姆纳特”的说法', '集体屈辱', '英国胜利', '帝国合法性']))
    story.append(Spacer(1, 10))
    rows = [
        ['观察层', '课堂要点', '为什么重要'],
        ['视觉/风格', '教授让同学观察门的几何装饰，指出它不像带有印度教神话雕刻的印度寺庙门；更接近伊斯兰艺术语汇。', '物质对象本身与政治标签之间出现断裂。'],
        ['受众假设', 'Ellenborough 预设所有印度人都知道、都感到屈辱，并会为“归还”欢呼。', '他把自己的阅读经验投射成印度人的集体记忆。'],
        ['公共仪式', '门被缓慢、庄严地运送和展示； spectacle 让抽象历史变成可见事件。', '记忆不是被动发现，而是被仪式化生产。'],
        ['结果', '当地人未必知道他在谈什么；但几十年后叙事可以被殖民国家和印度民族主义共同接受。', '一个最初不成功的故事，也可能在制度和重复中取得支配力。'],
    ]
    story.append(data_table(rows, [83, 234, CONTENT_W - 317], small=True))
    story.append(Spacer(1, 9))
    story.append(callout(
        '史实与叙事的分离',
        '“门是否真的来自索姆纳特”与“门被成功用来象征屈辱”是两个不同问题。即使物件来源说法不成立，政治 spectacle 仍然可能改变公众对过去的理解。',
        'gold',
    ))
    story.append(PageBreak())

    # Page 11 historiography
    story += section_heading(10, '历史书写不是唯一的自然方式', '编年、证据与“过去的用途”', '54:00-01:03:00')
    story.append(P('教授从词源提醒历史系学生：希腊语 historia 更接近“调查、询问”，不是单纯讲故事。课堂点名希罗多德（Herodotus）、修昔底德（Thucydides）与司马迁（Sima Qian）作为讨论入口（代表关系与具体比较需按阅读核对）。希腊/西方传统把过去当作可以分析的证据库，用来解释当下政治和经济、寻找模式；中国王朝史则常通过“前朝为何失去天命”来反思治理。两种传统都不是无目的的观看。', 'body'))
    story.append(P('转写中关于印度编年批评的引文可能来自比鲁尼（al-Biruni；课堂提及，作者与逐字引文待核）；本册只保留其作为殖民比较材料的功能，不把它当作对“印度人没有历史”的证明。', 'body_tight'))
    rows = [
        ['课堂比较', '过去被赋予的功能', '需要避免的误读'],
        ['希腊/西方史学', '通过调查、证据和相对连续的编年解释人类事务。', '不要把“数据化”误当作完全中立；选择问题本身就有目的。'],
        ['中国王朝史', '在王朝更替后解释失去天命的原因，为当下治理提供镜鉴。', '“以史为鉴”不是没有政治，而是另一种政治用途。'],
        ['课堂概括的印度传统', '重视跨时代的智慧、轮回和道德教训；史诗与论述可不断编辑更新。', '不要把“非线性/非编年”写成“印度人没有历史”。这是殖民比较框架需要被批判的地方。'],
        ['阿拉伯/伊斯兰知识世界', '课堂以 Aristotle 和知识翻译传统说明希腊模型的跨文化传播。', '传播不等于简单复制，具体史学传统仍需分别研究。'],
    ]
    story.append(data_table(rows, [112, 195, CONTENT_W - 307], small=True))
    story.append(Spacer(1, 10))
    story.append(P('课堂的关键转折', 'h2'))
    story.append(P('当历史被视为解释现在的工具时，问题就不再是“有没有历史”，而是“谁规定什么算证据、什么算时间、什么算有意义”。殖民作者把印度与欧洲编年标准比较，实际上也在输出一种文化等级秩序。', 'body'))
    story.append(callout('与索姆纳特的连接', '如果一座神庙的意义被定义为“永恒的精神连续性”，那么考古学所关心的每一层墙、每一块铭文就可能被说成“不重要”。这正是后半堂重建争议的理论准备。', 'cyan'))
    story.append(PageBreak())

    # Page 12 colonial categories
    story += section_heading(11, '从殖民分类到印度民族主义', '“Hinduism”与国家身份的现代形成', '01:03:00-01:15:00')
    story.append(P('课堂分析认为，英国殖民知识体系把多样的种姓、地方神祇、奉献实践和仪式系统整理为一个可与 Christianity 对比的统一“宗教” - Hinduism。类似的分类过程也可在日本把多样实践整理为 Shinto 的现代宗教类别。这里不是说前殖民社会没有宗教生活，而是说“统一宗教”这一行政、学术和政治形式有其历史条件。', 'body'))
    story.append(argument_chain(['多样实践', '殖民分类', '统一宗教名称', '政党与教育', '民族身份']))
    story.append(Spacer(1, 10))
    rows = [
        ['层次', '课堂讨论', '分析提醒'],
        ['制度形式', '国大党以英国议会模式为参照，同时宣称世俗并吸收社会主义语言。', '现代国家形式可能借用殖民制度，即使政治目标是独立。'],
        ['民族主义分歧', '印度教民族主义政治力量把印度描述为 Hindu nation / civilization，并把伊斯兰统治后的事物说成外来。', '转写把党名和年代识别得不稳定；本册不把党史细节写死。'],
        ['索姆纳特的角色', '神庙成为印度独立、文化复兴和恢复尊严的象征。', '宗教意义、国家意义和政党动员不能互相化约。'],
        ['殖民遗产', '“印度曾遭穆斯林统治而受伤”的框架先在殖民文本中成形，之后可被本土政治重新使用。', '后殖民民族主义并不必然摆脱殖民分类。'],
    ]
    story.append(data_table(rows, [82, 232, CONTENT_W - 314], small=True))
    story.append(Spacer(1, 9))
    story.append(callout(
        '不要把“印度教”当作无历史的固定实体',
        '答题时可写：课堂关注的是“统一宗教类别如何在殖民接触和民族国家建设中被制度化”，而不是用一个单一标签覆盖印度社会所有地方性和内部差异。',
        'blue',
    ))
    story.append(PageBreak())

    # Page 13 reconstruction
    story += section_heading(12, '独立后重建：国家承诺与考古层的冲突', '新神庙是否等于旧神庙？', '01:15:00-01:20:00；01:52:12-01:54:30')
    story.append(P('英国离开后，古吉拉特出现重建索姆纳特神庙的政治运动。课堂图像和语境指向 K. M. Munshi（转写发音不清，依据上下文校正）等倡议者；Sardar Patel 的支持以及 1951 年落成等制度史细节应以课程阅读进一步核对。教授的重点不在列出所有人物，而在问：为什么要用一座全新的建筑替代废墟？课堂也提醒，反对拆除者未必只是出于考古好奇，保护立场本身可能被策略性地强调。', 'body'))
    story.append(P('结尾将索姆纳特与圣索菲亚作课堂对照：若保留建筑及其附着的多层叙事，过去仍可被看见；若拆除旧址再造新象征，未来可研究的物质范围就会缩小。', 'body_tight'))
    rows = [
        ['立场', '他们想保护什么', '可能失去什么'],
        ['考古/保护立场', '保留废墟、建筑阶段、铭文、梵文描述和颜色证据；通过多季田野工作理解复杂历史。', '如果无法阻止拆除，研究机会和物质证据永久减少。'],
        ['国家重建立场', '恢复神圣连续性、国家尊严和独立后的文化自信；让“重建”成为国家承诺。', '旧层被清除，新建筑容易把多声部历史变成单一象征。'],
        ['历史学分析', '承认宗教情感和国家情感是真实的社会事实。', '不把情感事实自动转换为某个历史主张已被证明。'],
    ]
    story.append(data_table(rows, [94, 210, CONTENT_W - 304], small=True))
    story.append(Spacer(1, 10))
    story.append(P('“真实历史”的两种含义', 'h2'))
    story += bullets([
        '<b>考古意义上的历史：</b>一系列可分辨的建筑阶段、铭文、材料和使用变化；结论必须随证据强弱调整。',
        '<b>民族情感意义上的历史：</b>一个群体认为自己拥有跨时代的精神连续性，神庙是这种连续性的可见承诺。',
        '<b>课堂的批判：</b>两种意义都可以研究，但不能用“国家情感”替代对物质层的调查，也不能用考古层否认情感作为政治事实。',
    ], 'body_tight')
    story.append(callout('一句话', '重建不是简单恢复原状，而是选择哪一段过去可以继续被看见、被礼拜、被国家代表。', 'gold'))
    story.append(PageBreak())

    # Page 14 real history
    story += section_heading(13, '“真实历史”如何变成当代工具？', '黄金时代、八千万年与选择性记忆', '01:18:00-01:30:00')
    story.append(P('课堂把民族主义叙事概括为一条常见链条：印度曾有辉煌的印度教文明 -> 穆斯林到来并摧毁它 -> 在该民族主义叙事中，殖民统治被描述为利用内部腐败建立现状 -> 独立后的印度必须回到“真正的”过去并重生。这个链条的效力来自情感和政治用途，不来自它把所有历史细节都解释清楚。', 'body'))
    story.append(argument_chain(['黄金文明', '外来伤害', '长期屈辱', '国家重生', '永恒连续']))
    story.append(Spacer(1, 10))
    story.append(P('时间尺度的政治效果', 'h2'))
    story.append(P('教授以神庙网站/祭司叙述中极端的“八千万年”时间尺度作反讽案例。重点不是接受这个数字，而是观察它如何把文明写成“早于人类、永远存在”，把穆斯林统治的几个世纪压缩成一段短暂的黑暗插曲。时间尺度在这里是一种身份修辞：我们一直在这里，也将永远在这里。', 'body'))
    story.append(callout(
        '同时拒绝两个极端',
        '教授也反对另一种浪漫化叙事：过去的人一直和谐相处，只有邪恶的英国人教会他们互相仇恨。前殖民社会同样有冲突与差异；历史学的任务不是用另一个神话替换民族主义神话。录音还指出，索姆纳特的复兴叙事往往省略 1947 年 Partition / 巴基斯坦等不便纳入连续性神话的经验。',
        'cyan',
    ))
    story.append(Spacer(1, 10))
    rows = [
        ['要问的问题', '不要直接接受的答案', '更好的追问'],
        ['这是真实历史吗？', '“国家情感”就等于事实，或“学术史”就等于唯一真相。', '它依赖什么来源？哪些层次被选择，哪些被省略？'],
        ['为什么人们接受它？', '因为所有人自古都这样想。', '学校、政党、媒体、仪式和政府成就如何让它显得有用？'],
        ['为什么重建重要？', '因为新建筑完全等同于原建筑。', '新建筑在当下承担了什么象征和治理功能？'],
    ]
    story.append(data_table(rows, [110, 152, CONTENT_W - 262], small=True))
    story.append(PageBreak())

    # Page 15 comparisons
    story += section_heading(14, '比较案例：历史仇恨需要被教会', '从德国、奥地利到中国与当代政治', '01:30:00-01:52:00')
    story.append(P('民族国家的成员通常不会亲自认识所谓“世袭敌人”。教授因此追问：一个远离边界、从未见过法国人的德国人，如何学会法国是敌人？答案是历史教科书、电影、流行文化、报纸和纪念仪式。历史仇恨不是自然情绪，而是被不断媒介化的公共知识。', 'body'))
    rows = [
        ['课堂旁例', '叙事如何工作', '本课的比较目的'],
        ['德国与法国', '1871 年战争胜利可被写成对“长期敌人”的报复；语言和古代族群被重新接上。', '显示敌人谱系可以被追溯得很远，也可以被人为拼接。'],
        ['Hindenburg / Tannenberg', '1914 年对俄胜利被命名为 Tannenberg，借用 1410 年波兰击败条顿骑士团的记忆。', '战役名称把当下胜利连接到旧失败，制造复仇感。'],
        ['奥地利', '1938 年 Anschluss 曾受到不少奥地利人的欢迎；战后又形成“奥地利是纳粹第一个受害者”的国家叙事。', '相近语言和血缘不自动决定同一国家，叙事可随政治环境翻转。'],
        ['中国的“百年屈辱”', '用过去的屈辱界定当下国家复兴。', '说明这种结构不只属于欧洲或印度。'],
        ['Brexit、以色列/加沙', '课堂以当代例子提示历史如何持续参与政治正当化。', '不是把不同冲突等同，而是提醒我们追问谁在选择起点。'],
    ]
    story.append(data_table(rows, [105, 216, CONTENT_W - 321], small=True))
    story.append(Spacer(1, 9))
    story.append(callout(
        '民族主义可以是总括性话语，但不必然如此',
        '回应课堂提问：像宗教一样，民族主义在某些情境下可以把政治、历史、道德和日常生活都纳入单一框架；纳粹德国是极端例子，但不能因此把所有民族认同都当作同一强度。',
        'blue',
    ))
    story.append(PageBreak())

    # Page 16 historian ethics
    story += section_heading(15, '历史学家的危险位置', '复杂研究如何被变成简单政治弹药', '01:52:00-01:59:34')
    story.append(P('课堂后半段回到 Hobsbawm 的比喻：即使历史学家努力做负责任的研究，复杂论证也可能被媒体、政党或公众截取，简化到足以服务某个既定立场。公众常希望得到“谁是好人、谁是坏人”的答案，而学术史恰恰会让这种二分变得困难。', 'body'))
    rows = [
        ['风险', '课堂解释', '研究者的应对'],
        ['把复杂性剪掉', '多阶段、矛盾和不确定性被压缩成一个口号。', '在正文中分开事实、解释和推测。'],
        ['把研究当答案', '历史学家为当代问题提供“最终解释”，容易过度营销自己的成果。', '说明研究问题的范围，不把局部证据写成全局结论。'],
        ['隐含模型', '“我只是客观地做历史”掩盖了选择材料和概念的前提。', '明确写出研究者的假设、位置和分析路径。'],
        ['受众错位', '学术史的复杂表达与公共叙事的简洁需求不一致。', '公共史项目要调节语言，但不能牺牲证据边界。'],
    ]
    story.append(data_table(rows, [92, 210, CONTENT_W - 302], small=True))
    story.append(Spacer(1, 10))
    story.append(P('“显式建模”小清单', 'h2'))
    story += bullets([
        '我在研究什么对象，为什么选择它？',
        '我把哪些词当作分析类别（例如“印度教”“民族”“外来者”）？这些词是谁在什么时代使用的？',
        '哪些结论由直接材料支持，哪些只是合理推断？',
        '如果读者不同意我的政治或道德立场，证据链是否仍然成立？',
        '哪些问题我希望知道，却没有足够证据回答？',
    ], 'body_tight')
    story.append(callout('适用于本课程作业', '研究论文需要回答一个具体问题；公共史项目需要向非专业受众解释复杂历史。两者都不能把“可传播”误当作“已证明”。', 'cyan'))
    story.append(PageBreak())

    # Page 17 evidence and silence
    story += section_heading(16, '沉默、证据与不可知', '遗址被毁后，什么还能够被知道？', '01:59:45-02:02:54')
    story.append(P('课堂讨论从“沉默是否就是证据”开始。教授的回答非常明确：证据的缺失不等于某件事不存在；同样，没有人谈论某件事，也不能自动证明它被压制或掩盖。沉默只有放回档案制度、保存条件、语言和权力关系中，才可能成为需要解释的现象。', 'body'))
    story.append(argument_chain(['可见材料', '保存/选择机制', '沉默或缺失', '谨慎推断', '明确未知']))
    story.append(Spacer(1, 10))
    rows = [
        ['层级', '可以说什么', '不能跳到哪里'],
        ['直接证据', '录音、铭文、建筑材料、同时期文本等支持某个具体观察。', '不能把一条材料扩展成整个社会的共同意识。'],
        ['间接证据', '后来的叙事、仪式、网站和教材说明记忆如何形成。', '不能直接证明早期人群当时就拥有同样记忆。'],
        ['证据空白', '说明“目前没有材料回答”，并记录可能的保存/获取原因。', '不能把空白自动填成阴谋、创伤或不存在。'],
        ['不可逆损失', '考古层被拆除后，建筑阶段和使用痕迹可能永远无法恢复。', '不能把新建筑当作旧证据的等价替代品。'],
    ]
    story.append(data_table(rows, [93, 224, CONTENT_W - 317], small=True))
    story.append(Spacer(1, 10))
    story.append(callout(
        '本课最重要的方法句',
        '承认你不知道的事，并说明你能知道什么、凭什么知道、结论的可信范围在哪里。若材料不足，就把“不确定”写进结论，而不是用想象填空。',
        'gold',
    ))
    story.append(PageBreak())

    # Page 18 analytical framework
    story += section_heading(17, '争议遗产分析框架', '把索姆纳特转成可操作的研究步骤', '全课综合；重点 01:03:00-02:06:00')
    rows = [
        ['步骤', '要做什么', '索姆纳特示例'],
        ['1. 列出物质层', '记录现存建筑、废墟、材料、重建和拆除，不先用民族标签解释。', '区分旧遗址、新神庙、门和清真寺阶段。'],
        ['2. 画时间轴', '把每次建造、毁坏、改作和叙述出现的时间分开。', '不要把 1024/25 的袭击等同于全部遗址史。'],
        ['3. 识别行动者', '列出地方信众、统治者、殖民官员、考古学家、政党、游客和媒体。', '比较 Ellenborough、Munshi、保护者和后来的民族主义者。'],
        ['4. 分开主张', '分别写“物件是什么”“谁这样说”“谁因此获益”。', '门的物质来源与“归还圣门”的政治效果分开。'],
        ['5. 查媒介', '追踪文本、学校、网站、仪式、旅游路线如何传播叙事。', '殖民文本如何让“国耻”变得可教、可见。'],
        ['6. 查被省略者', '问哪些宗教、地方、阶层和建筑阶段没有进入主叙事。', '穆斯林居民、混合实践与多次重用是否被抹平？'],
        ['7. 评估干预', '考察保护、重建、改名、展示和拆除的目标与后果。', '重建带来认同，也可能终止田野考古。'],
        ['8. 写出边界', '标记直接证据、解释、推测和未知。', '对 649、735、1024/25、1951 等日期逐项核源。'],
    ]
    story.append(data_table(rows, [72, 205, CONTENT_W - 277], small=True))
    story.append(Spacer(1, 11))
    story.append(callout(
        '公共史项目的设计原则',
        '如果要为遗址制作展板、二维码或短视频，可以把“多声部时间轴”作为替代单一英雄叙事的形式：同时显示物质变化、叙事变化和证据空白，并明确哪些说法属于传统、殖民文本、国家仪式或现代政治。',
        'cyan',
    ))
    story.append(PageBreak())

    # Page 19 revision questions
    story += section_heading(18, '复习题与闪卡', '先遮住右栏回答，再用时间码回听', '全课综合')
    rows = [
        ['问题', '答题要点（自测后再看）'],
        ['为什么说民族国家不是自然状态？', '它是近代历史中的制度形式，需要抽象价值、媒介和历史叙事把陌生人组织成共同体。'],
        ['爱国主义与民族主义的课堂区分是什么？', '前者可围绕家园与人民的爱，后者更容易通过外部他者和敌意划界；区分是结构分析，不是简单道德标签。'],
        ['Hobsbawm 的“罂粟种植者”比喻想说明什么？', '历史学家提供可被政治行动者加工的原材料；研究者要意识到知识离开学术场域后的再利用。'],
        ['索姆纳特的“长时段历史”与“单一事件”如何冲突？', '遗址有多次毁建、改作和重用，现代叙事却优先记住马哈茂德·加兹尼一次袭击。'],
        ['“索姆纳特之门”为什么重要，即使门未必来自神庙？', '物质来源与政治功能不同；展示和归还仪式把门变成屈辱、胜利和帝国合法性的象征。'],
        ['殖民叙事如何把欧洲框架带到印度？', '用十字军、收复失地和基督教/伊斯兰冲突的熟悉模式，把印度想象成单一印度教国家。'],
        ['为什么重建可能同时是保存与抹除？', '它保存信仰和国家情感，却可能清除建筑层、铭文和未来研究所需的证据。'],
        ['“印度教”作为统一宗教类别应如何谨慎表述？', '课堂关注其在殖民分类与民族国家建设中的制度化，不是说此前没有宗教实践。'],
        ['为什么“没有证据”不能直接等于“没有发生”？', '保存、获取和权力会制造证据空白；需要说明未知范围，不能用想象填补。'],
        ['民族主义何时成为总括性话语？', '当它把政治、道德、历史和日常生活都纳入单一身份框架；它可以如此，但并非所有民族认同都达到同一程度。'],
        ['研究本课案例时最重要的伦理要求是什么？', '显式说明假设，分开事实/解释/推测，承认不可知，并追问谁从某种叙事中获益。'],
    ]
    story.append(data_table(rows, [196, CONTENT_W - 196], small=True))
    story.append(Spacer(1, 10))
    story.append(callout('最后自测', '不用看笔记，用 90 秒回答：如果你只能给索姆纳特案例写一个研究问题，你会研究物件、叙事、行动者还是后果？为什么？', 'gold'))
    story.append(PageBreak())

    # Page 20 reading/connection/source note
    story += section_heading(19, '阅读连接、作业与来源说明', '把本节课带回你的研究计划', '02:03:15-02:06:00')
    story.append(P('课程大纲列出的本周核心阅读', 'h2'))
    rows = [
        ['阅读', '带着什么问题读'],
        ['Romila Thapar, <i>Somanatha: The Many Voices of a History</i>', '“Many voices”如何拆开单一的神庙故事？不同年代、语言和作者如何改变索姆纳特的意义？'],
        ['Alka Patel, “The Historiography of Re-Use in South Asia,” <i>Archives of Asian Art</i> 59', '建筑再利用如何同时改变物质形态、历史解释和权力关系？'],
        ['Himanshu Prabha Ray, <i>Sacred Landscapes in Asia: Shared Traditions, Multiple Histories</i>', '如何在共享传统、多重历史和跨区域流动之间理解圣地？'],
    ]
    story.append(data_table(rows, [235, CONTENT_W - 235], small=True))
    story.append(Spacer(1, 9))
    story.append(P('与你已有阅读思考的连接（明确标为个人反思）', 'h2'))
    story.append(callout(
        '个人反思，不是教师原话',
        '你在《每周文献思考.docx》中提出：文化遗产不仅是被保护的对象，也是一种“固态记忆”，能够补充档案沉默；政府保护常与文化自信、国际形象和社会稳定相连；宗教力量既超越世俗武力，也可能被世俗权力迅速动员。这些观察可以与本课的“物质遗址 -> 国家叙事 -> 政治使用”链条相接，但写入作业时仍需用具体来源支持。',
        'cyan',
    ))
    story.append(Spacer(1, 9))
    story.append(P('下周与课程作业', 'h2'))
    story += bullets([
        '下周主题：Ayodhya（Babri Mosque / Ram temple），继续追踪宗教、民族国家、考古和法律证据如何相互塑形。',
        '研究论文：把本课的八步框架用于一个具体遗址，明确研究问题、证据范围和干预后果。',
        '公共史项目：面向公众解释复杂历史；可考虑多声部时间轴、说明牌、二维码、展览或反纪念物，但要标出不确定性。',
    ], 'body_tight')
    story.append(Spacer(1, 8))
    story.append(P('来源与处理说明', 'h2'))
    source_text = (
        '<b>主要输入：</b>课堂录音《民族主义、历史叙事与索姆纳特神庙案例》WAV（PCM 16-bit、单声道、16 kHz，约 02:06:06.8）；对应有道自动转写 PDF（142 页，时间戳 00:00-02:06:00）；HY5417 课程大纲（Week 4: Somnath）；以及《每周文献思考.docx》的个人阅读反思。<br/>'
        '<b>处理原则：</b>以录音时间轴和转写双语文本为主，统一校正明显误识别（例如 Somnath、Mahmud of Ghazni、Lord Ellenborough、Edward Gibbon、James Tod、Arminius、Hobsbawm、Babri Mosque/Ayodhya），对无法确认的数字、党史、引文和完整毁建序列保留“课堂说法/待核”标记。<br/>'
        '<b>使用边界：</b>本册是复习笔记，不是逐字稿，也不是对所有历史事实的独立考证。正式论文引用英文原句、精确年代、人物职务、门的来源和重建史时，请回听 WAV 并核对指定阅读或一手材料。'
    )
    story.append(callout('资料出处与证据边界', source_text, 'gray'))
    story.append(Spacer(1, 8))
    story.append(P('整理完成：2026 年 9 月 3 日  ·  保存于 HY5417 / seminar 4', 'tiny'))
    return story


def main():
    global STYLES
    register_fonts()
    STYLES = make_styles()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H - TOP - BOTTOM, id='body', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc = BaseDocTemplate(
        str(OUT_PDF), pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT,
        topMargin=TOP, bottomMargin=BOTTOM, title='HY5417 Seminar 4 - 索姆纳特神庙：民族主义、历史叙事与选择性记忆',
        author='Codex', subject='HY5417 course notes',
    )
    doc.addPageTemplates([
        PageTemplate(id='cover', frames=[frame], onPage=cover_page),
        PageTemplate(id='body', frames=[frame], onPage=body_page),
    ])
    doc.build(build_story())
    print(OUT_PDF)


if __name__ == '__main__':
    main()
