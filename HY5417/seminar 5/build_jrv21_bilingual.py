from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


BASE = Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5417/seminar 5')
OUT = BASE / 'JournalofReligionandViolence21_英中逐段对照.pdf'
FONT = '/System/Library/Fonts/STHeiti Medium.ttc'
ARIAL = '/System/Library/Fonts/Supplemental/Arial.ttf'
ARIAL_BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
ARIAL_ITALIC = '/System/Library/Fonts/Supplemental/Arial Italic.ttf'

pdfmetrics.registerFont(TTFont('STHeiti', FONT, subfontIndex=0))
pdfmetrics.registerFont(TTFont('Arial', ARIAL))
pdfmetrics.registerFont(TTFont('Arial-Bold', ARIAL_BOLD))
pdfmetrics.registerFont(TTFont('Arial-Italic', ARIAL_ITALIC))

NAVY = HexColor('#17324D')
TEAL = HexColor('#0E7490')
PALE = HexColor('#EEF6F8')
INK = HexColor('#202A33')
MUTED = HexColor('#5C6B76')
LINE = HexColor('#D4E1E7')
GOLD = HexColor('#B7791F')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='CoverTitle', fontName='Arial-Bold', fontSize=22, leading=28,
    alignment=TA_CENTER, textColor=NAVY, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name='CoverCN', fontName='STHeiti', fontSize=15, leading=22,
    alignment=TA_CENTER, textColor=TEAL, wordWrap='CJK', spaceAfter=8,
))
styles.add(ParagraphStyle(
    name='CoverMeta', fontName='STHeiti', fontSize=9.2, leading=14,
    alignment=TA_CENTER, textColor=MUTED, wordWrap='CJK',
))
styles.add(ParagraphStyle(
    name='Note', fontName='STHeiti', fontSize=8.8, leading=14,
    textColor=INK, backColor=PALE, borderColor=TEAL, borderWidth=0.6,
    borderPadding=9, wordWrap='CJK', spaceBefore=8, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name='Section', fontName='STHeiti', fontSize=15, leading=21,
    textColor=NAVY, wordWrap='CJK', spaceBefore=9, spaceAfter=7,
    borderColor=LINE, borderWidth=0, borderPadding=0,
))
styles.add(ParagraphStyle(
    name='LabelEN', fontName='Arial-Bold', fontSize=7.2, leading=9,
    textColor=TEAL, spaceBefore=2, spaceAfter=2,
))
styles.add(ParagraphStyle(
    name='LabelCN', fontName='STHeiti', fontSize=7.4, leading=10,
    textColor=GOLD, wordWrap='CJK', spaceBefore=3, spaceAfter=2,
))
styles.add(ParagraphStyle(
    name='English', fontName='Arial', fontSize=9.1, leading=13.8,
    textColor=INK, alignment=TA_LEFT, spaceAfter=2,
))
styles.add(ParagraphStyle(
    name='EnglishQuote', parent=styles['English'], leftIndent=9*mm,
    rightIndent=7*mm, fontName='Arial-Italic', textColor=NAVY,
))
styles.add(ParagraphStyle(
    name='Chinese', fontName='STHeiti', fontSize=9.3, leading=15.2,
    textColor=INK, wordWrap='CJK', backColor=PALE,
    borderColor=LINE, borderWidth=0.45, borderPadding=7, spaceAfter=5,
))
styles.add(ParagraphStyle(
    name='ReferenceEN', parent=styles['English'], fontSize=8.2, leading=12.2,
))
styles.add(ParagraphStyle(
    name='ReferenceCN', parent=styles['Chinese'], fontSize=8.4, leading=13.2,
    borderPadding=5,
))


def e(text: str) -> str:
    return escape(text).replace('\n', '<br/>')


body = [
    {
        'kind': 'abstract',
        'en': """Abstract: Religious sites are often at the center of confrontation. Groups frequently clash over the structures and the historical narratives surrounding sacred spaces. Religious sites encompass deeply entrenched meanings for groups of all backgrounds. These spaces represent identity, tradition, history, family, and belief systems. For minority groups, their religious sites can help provide a sense of belonging and serve as a monument to their history in the community. Due to their symbolic importance, religious sites are also vulnerable to violence by outside groups. Destructive acts targeting religious architecture and symbols are common throughout the world, but are especially frequent in identity-based conflicts, such as in Bosnia. However, the study of these attacks and their relationship to nationalist movements, particularly in Asia, has not been adequately studied. This article examines the destruction of Islamic sites in three distinct countries and contexts: India, Myanmar, and Xinjiang, China. In each case, Muslims are religious minorities and face varying levels of persecution. This article argues that the destruction of religious spaces and symbols has been used both literally and symbolically to claim a space for the dominant group and assert a right to the associated territory. The elimination of Muslim sites is part of a broader attempt to engage in a historical revisionism that diminishes or vilifies Muslims belonging in the region.""",
        'zh': """摘要：宗教场所常常处于冲突的中心。不同群体经常围绕神圣空间中的建筑，以及环绕这些空间形成的历史叙事发生冲突。对于各种背景的群体而言，宗教场所承载着根深蒂固的意义；这些空间代表着身份、传统、历史、家庭和信仰体系。对少数群体来说，宗教场所能够提供归属感，并作为其群体历史在当地社会中的纪念物。也正因为具有象征意义，宗教场所容易遭受外部群体的暴力攻击。针对宗教建筑和宗教象征的破坏在世界各地都很常见，在波斯尼亚等以身份认同为基础的冲突中尤其频繁。然而，关于此类袭击及其与民族主义运动之间关系的研究仍不充分，特别是在亚洲语境下。本文考察三个不同国家和情境中伊斯兰场所遭破坏的情况：印度、缅甸和中国新疆。在每个案例中，穆斯林都是宗教少数群体，并面临程度不一的迫害。本文认为，对宗教空间和象征的破坏既在字面上、也在象征意义上被用来为主导群体占据空间，并宣示其对相关领土的权利。消除穆斯林场所，是一种更广泛的历史修正主义行动的一部分；这种行动贬低或妖魔化穆斯林在相关地区的归属。""",
    },
    {
        'kind': 'keywords',
        'en': "Keywords: Hindu nationalism, Buddhist nationalism, Xinjiang, India, Babri Masjid, Rohingya",
        'zh': "关键词：印度教民族主义、佛教民族主义、新疆、印度、巴布里清真寺、罗兴亚人",
    },
    {
        'kind': 'para',
        'en': """On August 5th, 2020 Narendra Modi, the prime minister of India, participated in a stone laying ceremony at the construction site of the new Rama temple in Ayodhya. The site stood at the location of the Babri mosque before it was destroyed in 1992 by thousands of Kar Sevaks, Hindu volunteers. Many Hindus claim the site is the birthplace of the Hindu god Rama and an ancient temple which was destroyed by Muslims in the sixteenth century. While at the ceremony, Modi addressed a national television audience using language steeped in Hindu rhetoric:""",
        'zh': """2020年8月5日，印度总理纳伦德拉·莫迪参加了阿约提亚新罗摩神庙建筑工地的奠基仪式。该建筑工地位于巴布里清真寺的原址；1992年，数千名被称为“卡尔·塞瓦克”（Kar Sevaks）的印度教志愿者摧毁了这座清真寺。许多印度教徒声称，该地点是印度教神祇罗摩的诞生地，那里曾有一座古代神庙，于十六世纪被穆斯林摧毁。在仪式上，莫迪以充满印度教修辞的语言向全国电视观众发表讲话：""",
    },
    {
        'kind': 'quote',
        'en': """A long wait has ended today. . . . A grand temple will now be built for our Ram Lalla who had been living under a tent for many years. Ram Janmabhoomi has been freed from this interference which was on for centuries. . . . Shri Ram’s temple will become the modern symbol of our culture, eternal faith and national spirit. And this temple will also become a symbol of the collective resolve power of [millions of] people. . . . There is no aspect of life where our Ram does not inspire us. There is no such feeling of India in which Lord Ram is not seen. Ram is in the faith of India, Rama is in the ideals of India. Rama is in the divinity and philosophy of India. (Modi 2020)""",
        'zh': """漫长的等待今天终于结束了……现在，一座宏伟的神庙将为我们的罗摩拉拉（Ram Lalla）建造；多年来，他一直住在帐篷之下。罗摩诞生地已经摆脱了延续数百年的这种干扰……圣罗摩的神庙将成为我们文化、永恒信仰和民族精神的现代象征。这座神庙也将成为数以百万计民众集体决心与力量的象征……生活中没有哪个方面不受到罗摩的启发；印度也不存在一种看不见罗摩神的情感。罗摩存在于印度的信仰之中，存在于印度的理想之中，也存在于印度的神性与哲学之中。（Modi 2020）""",
    },
    {
        'kind': 'para',
        'en': """Although India is a multi-religious and constitutionally secular country, the policies and language of Modi and the Bharatiya Janata Party (BJP) have fused the Indian state to Hindu nationalism. Since the 1907 Hague Convention, international law formally prohibits the destruction of religious and heritage sites. More recently, the International Criminal Court has prosecuted individuals for destroying buildings of historic or religious importance (Swart 2020). In 2016, Ahmad Al-Faqi Al-Mahdi was convicted for his role in attacks on heritage sites in Timbuktu (Swart 2020). The normalization of the Babri Masjid destruction and the building of the Rama temple serves as a dangerous precedent about what tactics are acceptable when addressing contested religious sites. The Babri Masjid incident, however, is not an isolated case. This paper explores how the destruction of minority religious sites is a strategy of nationalism in India, Myanmar, and China.""",
        'zh': """尽管印度是一个多宗教国家，并且宪法规定其为世俗国家，但莫迪和印度人民党（BJP）的政策与言论已经把印度国家同印度教民族主义结合起来。自1907年《海牙公约》以来，国际法正式禁止破坏宗教场所和遗产地。近些年，国际刑事法院也对摧毁具有历史或宗教重要性建筑的人提起了公诉（Swart 2020）。2016年，艾哈迈德·法基·马赫迪因参与袭击廷巴克图遗产地而被定罪（Swart 2020）。将摧毁巴布里清真寺和建造罗摩神庙正常化，构成了一个危险的先例，因为它暗示在处理有争议的宗教场所时，某些破坏性手段是可以接受的。不过，巴布里清真寺事件并非孤例。本文探讨摧毁少数群体宗教场所如何在印度、缅甸和中国成为一种民族主义策略。""",
    },
    {'kind': 'heading', 'en': 'Literature', 'zh': '文献回顾'},
    {
        'kind': 'para',
        'en': """Benedict Anderson refers to the nation as “an imagined political community—and imagined as both inherently limited and sovereign” (Anderson 2006: 6). As a nation, members feel connected to one another through the bond of community, which may include language, ethnicity, religion, territory, or a combination of these. Nationalism, however, involves excessive identification with one’s nation and belief in its superiority. Nationalism often relies upon the construction of narratives that emphasize a group’s historical connectedness to the land. While building this connection, groups may also attempt to minimize or even erase the historical evidence of other groups within the same territory. Archaeological evidence may be used to further promote nationalist discourse, manipulate historical narratives, and assert ownership of a territory (Kohl and Fawcett 1995; Coningham and Lewer 2000; Kohl 1998).""",
        'zh': """本尼迪克特·安德森把民族国家称为“一个想象的政治共同体——并且，它被想象为本质上有限而又拥有主权的共同体”（Anderson 2006: 6）。作为一个民族国家，其成员通过共同体纽带感到彼此相连；这种纽带可能包括语言、族群、宗教、领土，或其中若干要素的组合。然而，民族主义意味着对本民族的过度认同，以及对本民族优越性的信念。民族主义往往依赖叙事建构，强调某一群体与土地之间的历史联系。在建立这种联系的同时，相关群体也可能试图淡化、甚至抹除同一领土上其他群体存在的历史证据。考古证据可以被用来进一步推动民族主义话语、操纵历史叙事，并宣示对某片领土的所有权（Kohl and Fawcett 1995; Coningham and Lewer 2000; Kohl 1998）。""",
    },
    {
        'kind': 'para',
        'en': """Architecture and cultural sites are meant to reflect the ethnic and historic makeup of a country. Various authors have discussed how archaeology creates belonging and meaning (Stovel, Stanley-Price, and Killick 2005). Kaldor emphasizes how architecture can be utilized in the process of legitimizing the nation (Kaldor 2004). Likewise, destruction of archaeological sites can demonstrate that certain sites no longer belong in the new ethno-religious state. Acts of cultural destruction are thus used strategically as a weapon of psychological warfare (Auwera 2012).""",
        'zh': """建筑和文化遗址被认为能够反映一个国家的族群构成与历史构成。许多作者讨论了考古学如何创造归属与意义（Stovel, Stanley-Price, and Killick 2005）。卡尔多强调，建筑可以被用于使民族国家合法化的过程（Kaldor 2004）。同样，摧毁考古遗址也可以用来表明，某些场所不再属于新的族群—宗教国家。因此，文化破坏行为被策略性地用作心理战的武器（Auwera 2012）。""",
    },
    {
        'kind': 'para',
        'en': """As nationalist movements attempt to rewrite historical narratives, they may utilize what is called a backward-looking nationalism that erases or villainizes specific groups in the past. Backward-looking nationalism means nationalists want to emphasize a revised version of history where the belligerent ethnic group is the actual victim (Kaldor 2004). Through such victimization, the nationalists can justify violence toward a historical antagonist. For instance, Serb nationalists considered Ottoman rule responsible for ending Serbia’s golden age. During the Bosnian war, Serb nationalists memorized anti-Ottoman/Muslim verses by nineteenth-century Serbian Poet-Prince, Petar II Petrović-Njegoš, to inspire and justify their aggression. During his reign, Njegoš wrote verses that glorified violence and promoted the destruction of Muslim sites and villages (Sells 2002). According to Njegoš, the creation of a greater Serbian ethnic state was not possible without such destruction. To restore the glory of the former Serbian civilization, the nationalists felt they had to correct what they considered historical wrongdoings toward them.""",
        'zh': """当民族主义运动试图重写历史叙事时，它们可能采用所谓“向后看的民族主义”，抹除或妖魔化过去的特定群体。“向后看的民族主义”意味着，民族主义者希望突出一种经过修订的历史版本，在这个版本中，发动争斗的族群反而被塑造成真正的受害者（Kaldor 2004）。通过这种受害者化，民族主义者便可以为针对历史敌手的暴力辩护。例如，塞尔维亚民族主义者认为奥斯曼统治终结了塞尔维亚的黄金时代。波斯尼亚战争期间，他们背诵十九世纪塞尔维亚诗人兼亲王彼得二世·彼得罗维奇—涅戈什创作的反奥斯曼、反穆斯林诗句，以激发并正当化其侵略行动。在位期间，涅戈什写下了歌颂暴力、鼓吹摧毁穆斯林场所和村庄的诗句（Sells 2002）。在涅戈什看来，若不实施此类破坏，就不可能建立一个“大塞尔维亚”族群国家。民族主义者认为，要恢复昔日塞尔维亚文明的荣耀，就必须纠正他们所认定的历史不公。""",
    },
    {
        'kind': 'para',
        'en': """Destroying artifacts of Ottoman domination was considered a symbolic way to reclaim the territory for their ethnic group. When Serb nationalists destroyed Bosniak mosques and architecture, they later denied the historical presence of Muslims in those areas (Sells 2002). Sites of architectural and historical importance, such as the Aladza mosque, known as the jewel of Islamic Balkan architecture, were destroyed (Riedlmayer 2002). In his investigation of damage and destruction at 392 Muslim sites throughout Bosnia, Riedlmayer finds that the damage was intended to erase the multi-ethnic history of the country while also reconstructing the collective memory of a nation and replacing it with a newer ethnocentric version (Riedlmayer 2002). The goal of this was also to minimize the incentives of Bosnian Muslims to return, symbolizing their lack of belonging and connection to the area.""",
        'zh': """摧毁象征奥斯曼统治的遗迹，被视为一种替本族群重新夺回领土的象征性方式。塞尔维亚民族主义者摧毁波斯尼亚克人的清真寺和建筑之后，又否认穆斯林曾在这些地区存在过（Sells 2002）。具有建筑与历史重要性的遗址——例如被誉为巴尔干伊斯兰建筑明珠的阿拉扎清真寺——也遭到摧毁（Riedlmayer 2002）。里德尔迈尔调查了波斯尼亚各地392处穆斯林场所的损毁情况，发现这些破坏旨在抹除该国的多族群历史，同时重构民族的集体记忆，以一种新的族群中心主义版本取而代之（Riedlmayer 2002）。这样做还意在削弱波斯尼亚穆斯林返回当地的意愿，象征他们不属于、也不再与该地区相连。""",
    },
    {
        'kind': 'para',
        'en': """Although intentional destruction of heritage sites is not formally considered genocide, the systematic use of it can serve as evidence that genocide has occurred. During the International Criminal Tribunal for the former Yugoslavia, the Trial Chamber emphasized that coordinated attacks on religious and cultural property alongside physical attacks of a specific group can demonstrate evidence of intent to destroy a group (Abtahi 2001). Consequently, the destruction of mosques, libraries, and cultural centers were considered evidence of acts of genocide. Annex eight of the Dayton Peace Agreement established the Commission to Preserve National Monuments. The eighth annex formally ended the Bosnian War and was considered foundational in the parties coming to an agreement.""",
        'zh': """尽管故意摧毁遗产地在法律上并不直接被视为种族灭绝，但系统性地实施此类破坏，可以成为已经发生种族灭绝的证据。在前南斯拉夫问题国际刑事法庭的审理中，审判分庭强调：如果针对宗教和文化财产的协调袭击，与针对某一特定群体成员的身体攻击同时发生，就可以证明存在摧毁该群体的意图（Abtahi 2001）。因此，对清真寺、图书馆和文化中心的摧毁被视为种族灭绝行为的证据。《代顿和平协定》附件八设立了“保护国家纪念物委员会”。该附件是正式结束波斯尼亚战争的安排之一，并被认为是各方达成协议的基础。""",
    },
    {
        'kind': 'para',
        'en': """Not surprisingly, cultural heritage sites are especially vulnerable during conflicts. As group polarization increases, the willingness to target cultural heritage sites may likewise increase (Sørensen and Viejo-Rose 2015). Sites that are targeted may be directly tied to the underlying cause of the conflict (Brosche et al. 2017). For example, the 2012 destruction of the burial tombs in Timbuktu, Mali was carried out by Islamic insurgents that considered the tombs blasphemous. The destruction of the Bamiyan Buddhas by the Taliban may have been a tactic to signal their strength and ideology to the rest of the world. Although Buddhists were no longer a part of Afghanistan, the symbolic attack was intended to shock the world and signal the resolve of the Taliban to the Western world (Knuth 2006; Brosche et al. 2017).""",
        'zh': """不出所料，文化遗产地在冲突期间尤其脆弱。随着群体极化加剧，人们攻击文化遗产地的意愿也可能随之增强（Sørensen and Viejo-Rose 2015）。遭到攻击的遗址，可能同冲突的根本原因直接相关（Brosche et al. 2017）。例如，2012年马里廷巴克图陵墓被毁，是认为这些陵墓亵渎宗教的伊斯兰叛乱分子所为。塔利班摧毁巴米扬大佛，则可能是向世界其他地区展示其实力和意识形态的一种策略。尽管当时佛教徒已经不再构成阿富汗社会的一部分，这种象征性袭击仍旨在震惊世界，并向西方传达塔利班的决心（Knuth 2006; Brosche et al. 2017）。""",
    },
    {
        'kind': 'para',
        'en': """While targeting cultural heritage sites can be a strategy used by states or rebels, it can also be utilized in the mobilizing stage of a political movement. Symbols and architecture can create a rallying effect that incentivizes new membership. Both states and rebel groups utilize symbols such as flags, national anthems, and cultural heritage sites to evoke pride in their identity. To the group, symbols can provide cohesion, while also creating strict parameters regarding the in and out group. Symbols and myths serve an important part of nationhood and belonging and a perceived threat toward those symbols can help increase recruitment efforts (Smith 2009).""",
        'zh': """攻击文化遗产地既可以是国家或叛乱组织采用的策略，也可以在政治运动的动员阶段发挥作用。象征和建筑能够产生号召效应，吸引新成员加入。国家与叛乱组织都会利用旗帜、国歌和文化遗产地等象征，激发群体对自身身份的自豪感。对象征所属的群体而言，这些符号既能增强凝聚力，也能严格划定内群体与外群体的界线。象征和神话是民族共同体与归属感的重要组成部分；一旦人们认为这些象征受到威胁，组织就更容易扩大招募（Smith 2009）。""",
    },
    {
        'kind': 'para',
        'en': """Militants may also use their own heritage sites strategically to store weapons and launch attacks. This tactic was used by Sikhs at the Golden Temple in 1984 when fighting an insurgency with the government of India. Because Sikhs did not expect the Indian government to target their holiest sites, they took refuge in the site along with their weapons. Once the Indian government attacked and damaged the site it severely damaged the relationship between Sikhs and the Indian government, ultimately leading to anti-Sikh riots and the assassination of Prime Minister Indira Gandhi by her Sikh bodyguards. In Myanmar, the government often burnt village churches in the Kachin state because they were used as a center for recruitment during both phases of the Kachin Civil War from 1961 to 1994 and 2011 to 2021 (Sithu 2016).""",
        'zh': """武装人员也可能策略性地利用本群体的遗产地储藏武器并发动袭击。1984年，锡克教武装在与印度政府的叛乱冲突中，就曾在金庙使用这种策略。由于锡克教徒没有料到印度政府会攻击他们最神圣的场所，便携带武器躲入金庙。印度政府随后袭击并破坏了该场所，严重损害了锡克教徒与印度政府之间的关系，最终引发反锡克教骚乱，并导致总理英迪拉·甘地被其锡克教保镖刺杀。在缅甸，政府经常焚毁克钦邦的乡村教堂，因为在1961至1994年、以及2011至2021年克钦内战的两个阶段中，这些教堂曾被用作招募中心（Sithu 2016）。""",
    },
    {
        'kind': 'para',
        'en': """Targeting cultural sites can also be financially opportunistic. Looted antiquities and relics potentially can create an attractive income stream for rebel groups or corrupt governments. Capturing and controlling territory that holds important cultural and historical significance creates a new revenue for the group (Baker and Anjar 2012). For example, ISIS gained substantial revenue from the illegal antiquities trade beginning in 2013 (Al Azm 2015). From 1970–1998, organized looting rings stole tens of thousands of antiquities from temples during Cambodia’s period of instability (Mackenzie and Davis 2016). Widespread looting of museums also took place following the US-led invasion of Iraq and Afghanistan (Rothfield 2009). More recently, close to 2000 artifacts were looted from war torn Yemen (Khalidi 2017).""",
        'zh': """攻击文化场所也可能出于经济投机。被掠夺的古物和文物，可能为叛乱组织或腐败政府带来颇具吸引力的收入来源。夺取并控制具有重要文化和历史意义的领土，会为相关群体创造新的收益（Baker and Anjar 2012）。例如，自2013年起，“伊斯兰国”（ISIS）从非法古物贸易中获取了大量收入（Al Azm 2015）。1970至1998年柬埔寨局势动荡期间，有组织的盗掘团伙从寺庙中偷走了数以万计的古物（Mackenzie and Davis 2016）。在美国主导入侵伊拉克和阿富汗之后，当地博物馆也遭到大规模洗劫（Rothfield 2009）。较近时期，饱受战争摧残的也门有近两千件文物被掠走（Khalidi 2017）。""",
    },
    {
        'kind': 'para',
        'en': """Finally, it is important to consider the capacity and the willingness of the state both to participate in and prevent targeted acts of destruction. In many authoritarian countries the state may actively participate or support the destruction of heritage sites and use its strength to limit the response by the targeted groups. However, state weakness may prevent the state from effectively protecting cultural sites. Empirically, the destruction of cultural property occurs most often in weak, failing, or failed states because the state lacks the capacity to protect the property (Auwera 2012).""",
        'zh': """最后，还必须同时考察国家参与和阻止定向破坏行为的能力与意愿。在许多威权国家中，国家可能主动参与或支持摧毁遗产地，并利用自身力量限制被针对群体的回应。然而，国家能力薄弱也可能使政府无法有效保护文化场所。从经验上看，文化财产破坏最常发生在国家能力薄弱、正在衰败或已经失效的国家，因为这些国家缺乏保护相关财产的能力（Auwera 2012）。""",
    },
    {
        'kind': 'para',
        'en': """In the cases explored in this paper, the state has utilized its role to support the destruction of minority cultural heritage sites in varying capacities in India, Myanmar, and China. In the case of India, the BJP opposition party alongside Hindu nationalist paramilitary organizations used the destruction of the Babri Masjid to mobilize existing supporters and attract new followers. Within the same decade, the BJP became the ruling government. These three cases represent nationalism in three distinct political regimes: a democracy (India), a semi-authoritarian state (Myanmar), and a one-party authoritarian system (China). In India, the Vishva Hindu Parishad (VHP)/Rashtriya Swayamsevak Sangh (RSS) maintain close ties to the BJP. In Myanmar, Buddhist militias and the state participated in the destruction of Muslim sites throughout the country, specifically in the Rakhine state. In China, the destruction has primarily been carried out by the state. The cases demonstrate that similar tactics are used across diverse regime types against religious minorities to promote nationalism. The destructive tactics demonstrate the risk to religious minorities in different political systems.""",
        'zh': """在本文考察的案例中，印度、缅甸和中国的国家以不同程度、不同方式利用自身角色，支持对少数群体文化遗产地的破坏。在印度，作为反对党的印度人民党与印度教民族主义准军事组织一道，利用摧毁巴布里清真寺来动员已有支持者，并吸引新的追随者；不到十年，印度人民党便成为执政党。这三个案例分别代表三种不同政治体制中的民族主义：民主制（印度）、半威权国家（缅甸）和一党威权体制（中国）。在印度，世界印度教理事会（VHP）和国民志愿服务团（RSS）与印度人民党保持密切联系。在缅甸，佛教民兵与国家共同参与摧毁全国各地、尤其若开邦的穆斯林场所。在中国，相关破坏主要由国家实施。这些案例表明，在多种政治体制中，都可能以相似策略针对宗教少数群体，以推动民族主义。此类破坏策略揭示了不同政治制度中的宗教少数群体所面临的风险。""",
    },
    {'kind': 'heading', 'en': 'India: Religious Nationalism Becomes State Sanctioned', 'zh': '印度：宗教民族主义获得国家认可'},
    {
        'kind': 'para',
        'en': """Modern independent India has been pulled in many different philosophical directions. On one end, elites associated with the dominant Indian National Congress Party (INC) have traditionally promoted a vision of secularism, a word explicitly added to the Constitution in 1976 during Indira Gandhi’s 21-month state of emergency. “The Emergency” period was an attempt to quell what she and the INC considered internal disturbances, including those relating to Sikh and Hindu Nationalists. The word secularism was poorly defined in the Indian Constitution, leaving the meaning up to interpretation. However, the opponents of secularism were more clearly defined by the Gandhi administration. Any organization considered to be a threat to public order was banned. The RSS, a Hindu paramilitary organization, became one of the main targets of arrests during The Emergency (Jaffrelot 2007). The Sikh community in Punjab was also widely targeted. Estimates suggest that nearly 30% of the 140,000 arrests were Sikhs (Grewal 1990). The instability in Punjab later escalated into a Sikh separatist insurgency in 1981.""",
        'zh': """现代独立印度受到多种不同政治哲学方向的牵引。一方面，与占主导地位的印度国民大会党（INC）有关的精英，传统上倡导世俗主义愿景。“世俗”一词是在英迪拉·甘地持续21个月的紧急状态期间，于1976年明确写入宪法的。“紧急状态”时期旨在压制她本人及国大党认定的国内动乱，其中包括与锡克教和印度教民族主义者有关的活动。印度宪法对“世俗主义”的界定并不清楚，其含义因而留待解释。不过，甘地政府对世俗主义反对者的界定更加明确：任何被视为威胁公共秩序的组织都会遭到取缔。作为印度教准军事组织的国民志愿服务团（RSS），成为紧急状态时期主要的逮捕对象之一（Jaffrelot 2007）。旁遮普的锡克教社群也受到广泛打击。据估计，在14万名被捕者中，近30%是锡克教徒（Grewal 1990）。旁遮普的不稳定局势后来升级，并在1981年演变为锡克教分离主义叛乱。""",
    },
    {
        'kind': 'para',
        'en': """On the other end of the spectrum, Hindu nationalists have attempted to make Hinduism central to India’s identity. While Hindu nationalist organizations were not new to India, the tactics and philosophy of the Gandhi administration during The Emergency helped give rise to a more organized movement. The Hindutva ideology sought to unite fragmented Hindu divisions into a more united, albeit mostly upper caste, organization. The arrests and perceived suppression of the RSS during The Emergency helped build upon a narrative of Hindu oppression. Hindu nationalists asserted that secular politicians, religious minorities, and their allies, particularly in the universities, sought to diminish Hindu identity and expression of faith. From the 1980s onward, the Hindu nationalist organizations RSS and VHP became increasingly powerful alongside the growing power of the recently established BJP. Communal violence between Hindus and Muslims also began increasing alongside the growing power of these movements (Wilkinson 2005). Several features became the key foci of the Hindu Nationalist movement as it gained momentum, but none more than the disputed site of the Babri Masjid.""",
        'zh': """另一方面，印度教民族主义者一直试图使印度教成为印度身份的核心。印度教民族主义组织在印度并非新生事物，但甘地政府在紧急状态期间采取的策略和政治理念，促进了一场组织化程度更高的运动兴起。“印度教特性”（Hindutva）意识形态试图把分散的印度教群体整合为一个更统一、但主要由高种姓构成的组织。紧急状态期间国民志愿服务团成员遭到逮捕、组织受到压制的经历，强化了“印度教徒遭受压迫”的叙事。印度教民族主义者声称，世俗派政治人物、宗教少数群体及其盟友——尤其是大学中的相关人士——意图削弱印度教身份和信仰表达。自20世纪80年代起，随着新成立的印度人民党力量增长，国民志愿服务团和世界印度教理事会等印度教民族主义组织也日益强大。印度教徒与穆斯林之间的群体暴力，也伴随这些运动的壮大而增加（Wilkinson 2005）。印度教民族主义运动声势日隆后，有多个议题成为其核心关注点，但没有任何议题比巴布里清真寺争议地点更为重要。""",
    },
    {'kind': 'heading', 'en': 'Babri Masjid', 'zh': '巴布里清真寺'},
    {
        'kind': 'para',
        'en': """During colonial rule, architectural preservation was used to assert authority (Anderson 2006). In India, the British saw themselves as caretakers of Indian archaeology that might otherwise be destroyed amid Hindu-Muslim tensions and what the British considered Indian “carelessness” (Rai 2009). In 1857–1858, Indians of all religious backgrounds fought in the Sepoy Mutiny against the increasing power and presence of the British in India. The Sepoy Mutiny was fought throughout much of Central India, with some of the strongest areas of resistance in Awadh, a region in modern Uttar Pradesh near Ayodhya. The rebels fought under the auspices of Bahadur Shah, a Muslim whom they declared the emperor of Hindustan. Both Hindus and Muslims recognized Shah as their leader which led British officials to note they could not use the “divide and rule” strategy against the two religions in this instance (Chandra, Tripathi, and De 1972). Once the British defeated the Indians, they began to refer to Muslims as “ferocious fanatics” (Metcalf 1965). This stirred a narrative of Hindu-Muslim historical division and built upon growing contention between the two religious groups. It also further aided in ongoing revisionism about the historical relationship between Hindus and Muslims prior to British colonization (Truschke 2016).""",
        'zh': """殖民统治时期，建筑保护被用来宣示权威（Anderson 2006）。在印度，英国人把自己视为印度考古遗产的守护者，并声称若非由其保护，这些遗产可能会在印度教徒与穆斯林的紧张关系中，以及英国人所谓印度人的“漫不经心”之下遭到毁坏（Rai 2009）。1857至1858年，各种宗教背景的印度人在“土兵起义”中共同反抗英国在印度不断扩张的权力与存在。战斗遍及印度中部许多地区，其中抵抗最强烈的地区包括阿瓦德，即今天北方邦靠近阿约提亚的一片区域。叛军在穆斯林巴哈杜尔·沙的名义下作战，并宣布他为印度斯坦皇帝。印度教徒和穆斯林都承认沙为领袖，这使英国官员指出，在这一事件中他们无法对两个宗教群体运用“分而治之”的策略（Chandra, Tripathi, and De 1972）。英国击败印度人后，开始把穆斯林称为“凶残的狂热分子”（Metcalf 1965）。这种称谓推动了印度教徒与穆斯林在历史上相互分裂的叙事，并加剧了两个宗教群体之间不断增长的对立；它也进一步助长了对英国殖民以前印度教徒与穆斯林历史关系的持续修正（Truschke 2016）。""",
    },
    {
        'kind': 'para',
        'en': """At the same time as the Sepoy uprising, the British developed close relationships with the Nirbani Hindu sect in Ayodhya. The Nirbani had provided refuge to the British during the mutiny and later received land in exchange for their loyalty (Ratnagar et al. 2004). The British began relying on the Nirbani’s historical accounts to write reports on the history of the area, specifically of the Babri Masjid (Srivastava 1991). The Nirbani had seized the mosque in 1853 claiming it was the birthplace of the Hindu God Rama. The Babri Masjid had been built in the sixteenth century during the reign of Mughal emperor Babur. However, the mosque became a site of increased contention following independence in 1947.""",
        'zh': """在土兵起义发生的同时，英国人与阿约提亚的印度教涅槃派（Nirbani）建立了密切关系。起义期间，涅槃派曾为英国人提供庇护，后来又因其忠诚而获赠土地（Ratnagar et al. 2004）。英国人开始依据涅槃派的历史叙述撰写该地区、尤其是巴布里清真寺的历史报告（Srivastava 1991）。涅槃派早在1853年便曾夺取这座清真寺，声称那里是印度教神祇罗摩的诞生地。巴布里清真寺建于十六世纪莫卧儿皇帝巴布尔统治时期。然而，1947年印度独立后，这座清真寺日益成为争议中心。""",
    },
    {
        'kind': 'para',
        'en': """In 1949, Hindus held a nine-day reading of the Ramayana and placed statues of Rama and Sita at the site of the mosque. This act of defiance by Hindus caused a confrontation with local Muslims. Following this confrontation, the mosque was locked. Over the next decades, both Hindus and Muslims initiated several lawsuits claiming ownership of the property. The mosque aroused increasing interest from the VHP and RSS in the 1980s. The groups held ceremonies at the location in 1983 and formed a committee that called for the liberation of the Rama temple and the removal of locks (Bacchetta 2000). During the 1980s, there was also increasing popularity of the Ramayana TV series which spurred countrywide interest in the god Rama. The television show reinforced the city of Ayodhya as the birthplace of Rama and subsequently drew attention to the location of the Babri Masjid (Bacchetta 2000). In 1986, to placate demands of the growing Hindu nationalist movement, Prime Minister Rajiv Gandhi had the locks on the mosque removed and allowed Hindus to worship at the site but did not permit Muslim prayers (Ratnagar 2004).""",
        'zh': """1949年，印度教徒举行了为期九天的《罗摩衍那》诵读活动，并在清真寺所在地安放罗摩和悉多的神像。印度教徒的这一挑战性行动引发了与当地穆斯林的冲突。冲突之后，清真寺被上锁。此后数十年间，印度教徒和穆斯林都提起多起诉讼，主张对该地产拥有所有权。到20世纪80年代，这座清真寺日益引起世界印度教理事会和国民志愿服务团的关注。1983年，这些组织在当地举行仪式，并成立委员会，要求“解放”罗摩神庙和打开门锁（Bacchetta 2000）。同一时期，电视剧《罗摩衍那》日益流行，在全国范围激发了人们对罗摩神的兴趣。该电视剧强化了阿约提亚是罗摩诞生地的观念，继而把公众注意力引向巴布里清真寺所在地（Bacchetta 2000）。1986年，为安抚不断壮大的印度教民族主义运动的诉求，总理拉吉夫·甘地下令打开清真寺门锁，允许印度教徒在当地礼拜，却不准穆斯林在那里祈祷（Ratnagar 2004）。""",
    },
    {
        'kind': 'para',
        'en': """In August 1990, the BJP launched its national political campaign under the slogan “Towards Ram Rajya” meaning the rule of Rama. Alongside this slogan, the party also launched a commemorative Ram Rath Yatra campaign in the months leading up to the election. With a truck constructed like an ancient Hindu chariot, BJP President L.K Advani launched a month-long rally, visiting temples throughout India with the Babri Masjid as the end destination. Advani was joined by thousands of fervent supporters during his campaign (Bhatt 2001). Two years later, the mosque was destroyed by thousands of Kar Sevaks, including many who had participated in the Rath Yatra. The site would become a politicized landmark that would define Indian politics until the present-day.""",
        'zh': """1990年8月，印度人民党以“迈向罗摩之治”（Towards Ram Rajya）为口号，发起全国政治运动。在选举前数月，该党还配合这一口号，展开纪念性的“罗摩战车巡游”（Ram Rath Yatra）。印度人民党主席拉尔·克里希纳·阿德瓦尼乘坐一辆仿古代印度教战车改造的卡车，开始为期一个月的集会巡游，沿途访问印度各地的寺庙，并以巴布里清真寺为最终目的地。竞选期间，数千名热情支持者加入阿德瓦尼的队伍（Bhatt 2001）。两年后，数千名卡尔·塞瓦克摧毁了清真寺，其中许多人曾参加战车巡游。此后，该地点成为一处高度政治化的地标，并持续影响印度政治直至今日。""",
    },
    {
        'kind': 'para',
        'en': """The destruction of the Babri Masjid is perhaps one of the most defining examples of architectural destruction by modern religious nationalists. The destruction of the mosque, however, is about more than just the elimination of a particular Muslim religious site. Instead, the mosque was seen as a symbol of historical subjugation, harking back to the dominion of Mughal emperor Babur. Hindu nationalists assert that despite being the demographic majority, they are historical victims of occupation and violence at the hands of minorities, including the British and Muslims. To remove the symbol of historical subjugation is to correct historical wrongs.""",
        'zh': """巴布里清真寺被毁，也许是现代宗教民族主义者摧毁建筑最具代表性的案例之一。然而，摧毁这座清真寺并不仅仅意味着消除某个特定的穆斯林宗教场所。相反，清真寺被视为历史屈从的象征，使人联想到莫卧儿皇帝巴布尔的统治。印度教民族主义者主张，尽管印度教徒在人口上占多数，他们在历史上仍是英国人和穆斯林等少数群体实施占领和暴力的受害者。因此，消除这个历史屈从的象征，就被解释成对历史错误的纠正。""",
    },
    {
        'kind': 'para',
        'en': """The destruction of the mosque was strongly condemned by the ruling Indian National Congress (INC) and thus the act of destruction was not done under the auspices of the ruling government at the time. However, the leaders of the BJP, RSS, and the VHP who mobilized around the destruction of the mosque would go on to become key leaders in the BJP. The party made the construction of the Rama temple a top campaign priority. Eventually, the party won national elections and formed a successful coalition in 1998, ending the long dominance of the INC. Although the initial reign of the BJP was short, the party rose to power once again in 2014, and was reelected in 2019 with decisive margins that essentially prevented opposition to their legislative measures.""",
        'zh': """当时执政的印度国民大会党强烈谴责摧毁清真寺的行为，因此，这场破坏并不是在当时执政政府的支持下实施的。然而，围绕摧毁清真寺进行动员的印度人民党、国民志愿服务团和世界印度教理事会领导人，后来成为印度人民党的重要领袖。该党把建造罗摩神庙列为竞选的首要任务。最终，印度人民党在全国选举中获胜，并于1998年成功组成联合政府，结束了国大党长期占据主导地位的局面。尽管印度人民党首次执政时间不长，该党在2014年再度上台，并于2019年以决定性优势获得连任，使反对党实际上难以阻止其立法措施。""",
    },
    {
        'kind': 'footnote',
        'en': """1. The BJP won the largest number of seats in the 1996 election but failed to form a tangible coalition. The BJP won the 1998 election but dissolved after thirteen months and then formed a successful government coalition in 1999.""",
        'zh': """注1：印度人民党在1996年选举中赢得最多席位，但未能组成可行的联合政府。该党在1998年选举中获胜，但其政府在十三个月后解散；1999年，该党又成功组成联合政府。""",
    },
    {'kind': 'heading', 'en': 'A New Era of Hindu Nationalism', 'zh': '印度教民族主义的新时代'},
    {
        'kind': 'para',
        'en': """Since gaining a large legislative majority in 2019, the BJP has utilized its power to quickly enact legislation that is considered anti-Muslim by many human rights activists. The most prominent examples of this are the Citizenship Amendment Act (CAA) and the elimination of Article 370 and 35a. The CAA fast tracks the citizenship of Buddhist, Christian, Hindu, Jain, and Sikh migrants from neighboring Muslim countries. Essentially, a path to citizenship is provided for migrants of all religious backgrounds except Muslims. Critics worry that the CAA alongside the proposed National Register of Citizens (NRC) will disproportionately impact Muslims. The NRC, which seeks to identify and detain anyone without proper documentation, was previously implemented in the northeast state of Assam as a mechanism of locating residents, primarily of Bangladeshi origin, without documentation. The final list of citizens in Assam contained 31 million names and excluded 1.9 million applicants, primarily Bangladeshis. In response to criticism from poor Hindus whose names were also not on the register, Home Minister Amit Shah reassured them that Hindu, Sikh, Jain, and Christian names not on the NRC need not worry (Amit Shah 2019). The publication of the Assam NRC in August came amid a heightened sense of worry following the August 5th constitutional order eliminating Article 370 and 35a. Article 370 had been enacted in 1949 and allowed Kashmir to have its own constitution, flag, and autonomous governance. Article 35a was enacted in 1954 to maintain the unique cultural heritage of Kashmir by preventing non-Kashmiris from purchasing land in Kashmir. The elimination of these two articles weakened constitutional protections for Kashmiris and threatened to facilitate a demographic transition that Hinduize Kashmir. Combined, these August 2019 measures created a sense of worry among India’s Muslims about their future and safety within the country under the governance of Hindu nationalists. Protests erupted throughout the country against the NRC and CAA in December 2019. In February 2020, the protests in New Delhi escalated into some of the country’s most violent riots in decades.""",
        'zh': """2019年取得国会压倒性多数席位后，印度人民党利用其权力迅速通过了一系列立法，其中许多被人权活动人士视为反穆斯林措施。最突出的例子是《公民身份修正法》（CAA），以及废除宪法第370条和第35A条。《公民身份修正法》为来自邻近穆斯林国家的佛教徒、基督徒、印度教徒、耆那教徒和锡克教徒移民加快入籍程序。实际上，除穆斯林之外，各种宗教背景的移民都获得了取得公民身份的途径。批评者担忧，《公民身份修正法》与拟议中的“全国公民登记册”（NRC）会对穆斯林造成不成比例的影响。全国公民登记册旨在识别和拘留所有缺少有效身份证明的人；这一制度此前已在东北部阿萨姆邦实施，用于查找没有证明文件的居民，其中主要是孟加拉国裔居民。阿萨姆邦最后公布的公民名单包括3100万人，却排除了190万名申请人，其中多数为孟加拉国人。一些贫困印度教徒的姓名也不在名单上，因此引发批评；内政部长阿米特·沙阿向他们保证，未被列入登记册的印度教徒、锡克教徒、耆那教徒和基督徒无需担忧（Amit Shah 2019）。阿萨姆邦于8月公布公民登记册时，社会正因8月5日废除宪法第370条和第35A条的命令而忧虑加剧。1949年制定的第370条允许克什米尔拥有自己的宪法、旗帜和自治政府。1954年制定的第35A条则禁止非克什米尔人购买当地土地，以维护克什米尔独特的文化遗产。废除这两个条款削弱了对克什米尔人的宪法保护，并可能推动使克什米尔“印度教化”的人口结构转变。2019年8月采取的这些措施共同加深了印度穆斯林对自身在印度教民族主义者治理下的未来与安全的担忧。2019年12月，全国各地爆发反对全国公民登记册和《公民身份修正法》的抗议。2020年2月，新德里的抗议升级为该国数十年来最严重的骚乱之一。""",
    },
    {
        'kind': 'para',
        'en': """The exclusionary measures of the BJP have come under increased international scrutiny. The Council on Foreign Relations notes that the leadership of Prime Minister Modi and the BJP have heightened anti-Muslim sentiment and disenfranchised millions of Muslims. Indian Muslims continue to face social barriers that limit equitable access to education, housing, and political power and representation (Maizland 2020). Consequently, Indian Muslims live with higher rates of poverty and discrimination while having limited avenues to address grievances. Ongoing acts of institutionalized discrimination may also make India’s Muslim population, particularly the youth, vulnerable to extremist views. The destruction of the Babri Masjid served as a catalyst that helped empower a new generation of Hindu nationalists and created a precedent to assert dominion over Muslim sites throughout the country. Ultimately, the institutionalization of Hindu nationalism through the BJP has helped legitimize anti-Muslim policies and actions.""",
        'zh': """印度人民党的排斥性措施日益受到国际社会审视。美国外交关系委员会指出，莫迪总理及印度人民党的领导加剧了反穆斯林情绪，并使数百万穆斯林被剥夺权利。印度穆斯林仍面临社会壁垒，无法平等获得教育、住房、政治权力和政治代表（Maizland 2020）。因此，印度穆斯林承受着更高的贫困率和歧视，却只有很少途径能够申诉。持续的制度化歧视也可能使印度穆斯林、尤其是青年更容易受到极端主义观点影响。巴布里清真寺被毁成为一个催化事件，帮助新一代印度教民族主义者获得力量，并为在全国各地宣示对穆斯林场所的支配权开创了先例。归根结底，印度教民族主义通过印度人民党实现制度化，有助于使反穆斯林政策与行动取得合法性。""",
    },
    {'kind': 'heading', 'en': 'Myanmar: Buddhist Nationalism through State and Militia Collaboration', 'zh': '缅甸：国家与民兵合作下的佛教民族主义'},
    {
        'kind': 'para',
        'en': """It is difficult to know the exact demographics of Myanmar due to manipulations in the Census, government suppression of information, and exclusion of certain religious and ethnic groups. However, based on available information, the population of Myanmar is approximately 88% Buddhist, 4% Christian, and 4% Muslim. Myanmar is ethnically diverse with over 100 different ethnic groups, with the majority of the population being Bamar (68%), and many other large ethnic groups including the Shan (9%), Karen (7%), Rakhine (2%), and Rohingya (2%) (Wade 2019). Since independence in 1948, the government of Myanmar has considered the Rohingya, who primarily live in the Rakhine state, to be illegal aliens from Bangladesh. According to Myanmar officials, the British brought the Rohingya to the region during the colonial era and they likewise should have left at independence in 1948. The Rohingya, however, have lived in the region for more than a century, with evidence of a presence in the region as early as the eighth century (Wade 2019).""",
        'zh': """由于人口普查受到操纵、政府压制信息，并排除某些宗教和族群，缅甸人口构成的准确情况很难确定。不过，根据现有资料，缅甸人口大约88%信奉佛教、4%信奉基督教、4%信奉伊斯兰教。缅甸的族群构成十分多样，有一百多个族群；人口多数为缅族（68%），其他较大族群包括掸族（9%）、克伦族（7%）、若开族（2%）和罗兴亚人（2%）（Wade 2019）。自1948年独立以来，缅甸政府一直把主要生活在若开邦的罗兴亚人视为来自孟加拉国的非法外来者。缅甸官员宣称，罗兴亚人是在殖民时期由英国人带入这一地区的，因此也理应在1948年独立时离开。然而，罗兴亚人在该地区已经生活了一个多世纪，现有证据甚至表明，他们早在八世纪就已经出现于当地（Wade 2019）。""",
    },
    {
        'kind': 'para',
        'en': """Buddhism has been a defining feature of Myanmar’s state identity since independence. Burmese Independence leader Aung San originally gave hope to ethnic and religious minorities with his promotion of secular democratic ideas and multiculturalism. Unfortunately, this vision was left unfulfilled following his assassination in July 1947. Following increasing instability after his death, the military took an increasing role as a caretaker government. By 1962, a military junta was in power and would hold that power until gradual democratization efforts in 2010. The democratic experiment, however, appeared to end abruptly following the military coup on January 31, 2021.""",
        'zh': """独立以来，佛教一直是界定缅甸国家身份的重要特征。缅甸独立运动领袖昂山最初倡导世俗民主理念和多元文化主义，给族群与宗教少数群体带来了希望。不幸的是，他在1947年7月遇刺后，这一愿景未能实现。他去世后，国家日益不稳定，军方以看守政府身份承担了越来越重要的角色。到1962年，军事委员会掌权，并一直维持统治，直到2010年渐进式民主化改革启动。然而，2021年1月31日的军事政变似乎突然终结了这一民主实验。""",
    },
    {
        'kind': 'para',
        'en': """There have been several ethnic based uprisings since independence throughout the country including the Kachin in Kachin state, the Karen (Kayin) in Kayin state, the Chin and Rohingya in the Rakhine state, and the Shan in the Shan state. The junta responded harshly for decades and implemented its Burmanization policy, whereby it imposed the dominant Bamar ethnic group’s form of Buddhism and culture on the rest of the country (Berlie 2008; Rogers 2013). The semi-democratic government under Aung San Suu Kyi left many hopeful that it would bring an end to the internal violence, but for the Rohingya, the targeted violence escalated.""",
        'zh': """独立以来，缅甸各地发生过多次以族群为基础的起义，包括克钦邦的克钦人、克伦邦的克伦人（Kayin）、若开邦的钦族和罗兴亚人，以及掸邦的掸族。军政府数十年来一直采取严厉手段应对，并实施“缅族化”政策，把占主导地位的缅族所信奉的佛教形式及其文化强加于全国其他地区（Berlie 2008; Rogers 2013）。昂山素季领导的半民主政府曾使许多人相信，国内暴力有望结束；但对于罗兴亚人而言，针对他们的暴力反而不断升级。""",
    },
    {
        'kind': 'para',
        'en': """Part of the Burmanization policy was the destruction of religious and cultural sites that did not align with Bamar style Buddhism. Scholars have referred to the process as “iconoclasm from above” whereby the junta destroyed cultural heritage as part of the state policy (Lee and Zarandona 2020). The junta’s goal was to diminish both physical and cultural expressions of non-Bamar culture while promoting Bamar Buddhism (Noyes 2016). The junta did not want to create a multi-ethnic, multi-religious secular state as envisioned by Aung San. Instead, the state was to be governed by Bamar Buddhist principles. The Burmanization campaign destroyed non-Buddhist icons and structures, particularly in states with non-Buddhist and non-Bamar residents, specifically the Chin, Kachin, Karen, and Rakhine states (US Department of State 2017; Sithu Aung Myint 2016). The destruction, closure, and conversion of buildings was part of the strategy of erasing the old identity and consolidating the new Bamar Buddhist identity. Multiple Islamic sites have been closed or destroyed. The Badar Makkam Mosque was annexed into a naval base during the 1970s and later used as a Buddhist site. In the 1980s, the Babagyi Mosque was occupied by the military and closed indefinitely to the public. Mosques in the town of Mrauk-U including the Musa Pali and Shindhikhan mosques were destroyed in the 1980s and 1990s respectively (Lee and Zarandona 2020). In 2012, the culturally and historically important Jama mosque in Sittwe was ransacked amid ongoing violence targeting the Rohingya; the mosque has not since reopened.""",
        'zh': """“缅族化”政策的一部分，是摧毁不符合缅族佛教形式的宗教和文化场所。学者把这一过程称为“自上而下的圣像破坏”，即军政府把摧毁文化遗产作为国家政策的一部分（Lee and Zarandona 2020）。军政府的目标是削弱非缅族文化在物质和文化层面的表达，同时推广缅族佛教（Noyes 2016）。军政府不愿建立昂山设想的多族群、多宗教世俗国家，而是要以缅族佛教原则治理国家。“缅族化”运动摧毁非佛教的圣像与建筑，尤其集中于非佛教徒和非缅族居民较多的地区，即钦邦、克钦邦、克伦邦和若开邦（US Department of State 2017; Sithu Aung Myint 2016）。摧毁、关闭和改变建筑用途，都是抹除旧身份、巩固新的缅族佛教身份这一策略的组成部分。多处伊斯兰场所被关闭或摧毁。20世纪70年代，巴达尔·马卡姆清真寺被并入海军基地，后来被用作佛教场所。20世纪80年代，巴巴吉清真寺被军方占据，并无限期对公众关闭。妙乌镇的穆萨帕利清真寺和辛迪坎清真寺，分别在20世纪80年代和90年代被摧毁（Lee and Zarandona 2020）。2012年，在持续针对罗兴亚人的暴力中，实兑具有重要文化和历史意义的贾玛清真寺遭到洗劫，此后再未重新开放。""",
    },
    {
        'kind': 'para',
        'en': """Buddhist nationalism in Myanmar has long aligned with the goals of the state, even as the state began democratizing. Buddhist nationalism in Myanmar has centered around marginalizing, and in some cases, attempting to eliminate forces that threaten the Bamar Buddhist majority. In the 1980s, the government began taking increasingly aggressive actions to erase the historical and cultural identity of the Rohingya, including: removing the Rohingya from the list of recognized groups within the state, stripping Rohingya of their citizenship cards, destroying cultural heritage sites, forced removal of the group from their historical land, and systematic rape and murder. Beginning in 1988, the ruling junta began classifying the Rohingya as trespassers from Bangladesh. By the 1990s, the state began a relocation program that recruited Buddhists to move to the Rakhine state to offset what was perceived as a growing Muslim population (Wade 2019). Over the next two decades the state took multiple measures to limit opportunities and movement of the Rohingya, including admission bans at state-run institutions such as Sittwe University. Travel outside of the Rakhine state was also strictly controlled. The state also passed “Protection of Race and Religion” laws to limit interreligious marriages (Frydenlund 2017; White 2015). The state and its affiliated Buddhist militias sought to erase memories of the Rohingya’s existence within the region.""",
        'zh': """即使缅甸开始民主化，缅甸佛教民族主义长期以来仍与国家目标保持一致。它的核心是把威胁缅族佛教多数地位的力量边缘化，并在某些情况下试图彻底消灭这些力量。20世纪80年代，政府开始采取日益激进的行动，抹除罗兴亚人的历史与文化身份，包括：把罗兴亚人从国家承认的群体名单中删除；剥夺其公民身份证；摧毁文化遗产地；强迫他们离开历史上生活的土地；以及实施系统性强奸和杀戮。从1988年起，执政军政府开始把罗兴亚人归类为来自孟加拉国的“非法闯入者”。到20世纪90年代，国家启动人口迁移计划，招募佛教徒迁往若开邦，以抵消其所认定的穆斯林人口增长（Wade 2019）。此后约二十年中，国家采取多项措施，限制罗兴亚人的发展机会和迁徙自由，包括禁止他们进入实兑大学等国立机构。他们离开若开邦的旅行也受到严格控制。国家还通过“保护种族与宗教”法律，限制跨宗教婚姻（Frydenlund 2017; White 2015）。国家及其附属佛教民兵试图抹去有关罗兴亚人曾在这一地区生活的记忆。""",
    },
    {
        'kind': 'para',
        'en': """The democratization and liberalization of Myanmar that began in 2011 brought hope for many Rohingya that human rights in the country would improve. However, violence targeting the Rohingya only escalated. In 2012, in the state of Rakhine, widespread violence broke out between Arakanese Buddhists and Rohingya Muslims who make up 63% and 34% of Rakhine populations respectively. Tensions escalated between the two groups following the rape and murder of a Buddhist woman by Rohingya men (Wade 2019). The unrest led to a state of emergency that severely restricted travel of the Rohingya and allowed the military to administer the region. Unrest further escalated in the following weeks with violence impacting both groups, resulting in 90 deaths, 90,000 displacements, and 2500 homes burned (Human Rights Watch 2013).""",
        'zh': """2011年开始的缅甸民主化与自由化，使许多罗兴亚人期待该国人权状况能够改善。然而，针对罗兴亚人的暴力却不断升级。2012年，若开邦的阿拉干佛教徒和罗兴亚穆斯林之间爆发大范围暴力冲突；两者分别约占若开邦人口的63%和34%。一名佛教女性被罗兴亚男子强奸并杀害后，两个群体之间的紧张关系加剧（Wade 2019）。动乱导致若开邦进入紧急状态，罗兴亚人的出行受到严重限制，军方也获准接管当地。随后数周，动乱进一步升级，暴力波及双方，造成90人死亡、9万人流离失所、2500所住宅被焚毁（Human Rights Watch 2013）。""",
    },
    {
        'kind': 'para',
        'en': """Unrest spread to non-Rohingya Muslim areas in 2013 as well. Following a business dispute between a Muslim shop owner and Buddhist customer, mob violence broke out in Mandalay killing more than 40, mostly Muslims. Police failed to intervene and, in some cases, participated (International Crisis Group 2013). In Yangon, Buddhists burned more than 100 Muslim homes, shops, and mosques (Szep 2013). Riot police in Thaketa observed Buddhist residents destroying an Islamic school. Buddhist resident Min Thet Lin told reporters, “People don’t want a mosque here” (Marshall 2013). Additional incidents of Buddhists destroying Muslim homes, mosques, and businesses occurred in Lashio (Shan state) and Kantbalu (Sagaing state) that same year. However, most of the incidents in these states were able to be contained and incidents of violence were sporadic. However, in Rakhine, the targeted destruction by Buddhist militias was systematic and increasingly supported by the state.""",
        'zh': """2013年，动乱还蔓延到非罗兴亚穆斯林居住区。一名穆斯林店主与佛教徒顾客发生商业纠纷后，曼德勒爆发群体暴力，造成四十多人死亡，其中多数为穆斯林。警察没有介入，在某些情况下甚至参与其中（International Crisis Group 2013）。在仰光，佛教徒焚毁了一百多所穆斯林住宅、商店和清真寺（Szep 2013）。达基达镇的防暴警察旁观佛教居民摧毁一所伊斯兰学校。一名名叫敏德林的佛教居民告诉记者：“人们不希望这里有清真寺”（Marshall 2013）。同年，掸邦腊戍和实皆省甘勃卢也发生佛教徒摧毁穆斯林住宅、清真寺和商业设施的事件。不过，这些地区的大多数事态都得到控制，暴力事件相对零星。若开邦的情况则不同：佛教民兵实施的定向破坏具有系统性，并且得到国家越来越明确的支持。""",
    },
    {
        'kind': 'para',
        'en': """Two Buddhist nationalist militia groups, the 969 movement and Ma Ba Tha, originated around the same time of the increasing communal violence. The 969 movement, founded by Buddhist monk Ashin Wirathu in 2013, sought to oppose the expansion of Islam within Myanmar and to protect the country from “Bengalis.” Similarly, Ma Ba Tha (The Patriotic Association of Myanmar) was founded by Buddhist monks in 2014 to defend Buddhism from Islam in Myanmar. Over the next two years, the organizations led efforts to destroy mosques and Muslim properties and to remove Muslims, particularly Rohingya, from what they considered Buddhist lands (Wade 2019). This coincided with state-led efforts to relocate Bamar Buddhists to areas where the Rohingya had been forcefully removed and to build Bamar structures, including Buddhist temples (Lee and Zarandona 2020). Although the organizations were technically independent of the government, they were increasingly supported by senior officials in the government.""",
        'zh': """随着群体暴力加剧，两个佛教民族主义民兵组织——“969运动”和“缅甸爱国协会”（Ma Ba Tha）大约在同一时期出现。969运动由佛教僧侣阿欣威拉杜于2013年创立，旨在反对伊斯兰教在缅甸扩张，并保护国家免受所谓“孟加拉人”的威胁。同样，由佛教僧侣于2014年创立的缅甸爱国协会，声称要在缅甸保护佛教免受伊斯兰教侵害。此后两年，这些组织领导了摧毁清真寺和穆斯林财产的行动，并试图把穆斯林、尤其罗兴亚人赶出它们认定的佛教土地（Wade 2019）。与此同时，国家把缅族佛教徒迁往罗兴亚人被强行驱逐的地区，并在那里建造包括佛寺在内的缅族建筑（Lee and Zarandona 2020）。尽管这些组织在形式上独立于政府，它们却日益得到政府高级官员支持。""",
    },
    {
        'kind': 'footnote',
        'en': """2. The term Bengali is used to deny that the Rohingya belong to Myanmar and instead suggests they belong to Bangladesh.""",
        'zh': """注2：“孟加拉人”这一称谓被用来否认罗兴亚人属于缅甸，并暗示他们应当属于孟加拉国。""",
    },
    {
        'kind': 'para',
        'en': """By late 2016, the state transitioned from limited engagement and covert support of Buddhist militia groups to openly adopting much of the militia strategies as state policy. The state also introduced limitations on inter-religious marriage and the number of children Muslims can have (Frydenlund 2017). By the end of 2017, in what UN and Human Rights officials have labelled acts of genocide, the state forces and Buddhist militias killed at least 24,000 Rohingya and utilized widespread sexual violence against at least 18,000 Rohingya women and girls (APHR 2018). A further 116,000 Rohingya faced physical abuse and 36,000 were thrown into fires. Another 700,000 fled the country, mostly to neighboring Bangladesh (Habib et al. 2018). At least 300 Rohingya villages were destroyed, including the mosques within those villages (Human Rights Watch 2018). The actions by the military were classified as an ethnic cleansing by several scholarly sources and international organizations, including the United Nations Human Rights Council (UNHRC 2018). In 2019 Gambia brought charges of genocide against Myanmar in the International Court of Justice (UNHRC 2018).""",
        'zh': """到2016年末，国家从有限参与、暗中支持佛教民兵，转向公开把民兵使用的许多策略采纳为国家政策。国家还开始限制跨宗教婚姻，并限制穆斯林可生育的子女数量（Frydenlund 2017）。到2017年底，在联合国和人权官员称为种族灭绝的行动中，国家武装力量与佛教民兵杀害了至少2.4万名罗兴亚人，并对至少1.8万名罗兴亚妇女和女孩实施大规模性暴力（APHR 2018）。另有11.6万名罗兴亚人遭到身体虐待，3.6万人被投入火中；还有70万人逃离该国，其中大多数进入邻国孟加拉国（Habib et al. 2018）。至少三百个罗兴亚村庄被毁，村内清真寺也一并遭到摧毁（Human Rights Watch 2018）。包括联合国人权理事会在内的多项学术研究和国际组织把军方行动定性为族群清洗（UNHRC 2018）。2019年，冈比亚在国际法院对缅甸提出种族灭绝指控（UNHRC 2018）。""",
    },
    {
        'kind': 'para',
        'en': """Buddhist nationalist leaders and sentiment wield power over both the pro-military Union Solidarity and Development Party and Aung San Suu Kyi’s National League for Democracy (NLD). Despite previously including Muslims in the party, in the 2015 election neither party included any Muslim candidates (Nachemson 2020). To further limit representation, the state election commission cancelled the 2020 elections for the Rakhine state. However, the state had already stripped most Rohingya of voting rights in 2015. The removal of rights came alongside physical violence by both the state and state-sanctioned Buddhist militias. Consequently, the state of Rakhine and the Rohingya essentially had no national representation under the ruling parties. The NLD won the November 2020 election decisively, however, a military coup on January 31, 2021 prevented the elected government from assuming office. It is unknown how the return to the military junta will impact the Rohingya, but it remains notable that the worst atrocities thus far occurred under Suu Kyi’s semi-democratic regime.""",
        'zh': """佛教民族主义领袖及相关情绪，同时对亲军方的联邦巩固与发展党和昂山素季领导的全国民主联盟（NLD）施加影响。尽管两党过去都曾接纳穆斯林，2015年选举时却都没有推出任何穆斯林候选人（Nachemson 2020）。为进一步限制政治代表，国家选举委员会取消了若开邦的2020年选举。不过，国家早在2015年就已经剥夺大多数罗兴亚人的投票权。权利被剥夺的同时，国家和得到国家认可的佛教民兵还实施身体暴力。结果，在执政党制度下，若开邦和罗兴亚人在国家层面实际上没有代表。全国民主联盟在2020年11月的选举中取得决定性胜利，但2021年1月31日的军事政变阻止当选政府就职。军政府重新掌权会如何影响罗兴亚人尚不清楚；不过值得注意的是，迄今最严重的暴行发生在昂山素季的半民主政权之下。""",
    },
    {
        'kind': 'para',
        'en': """The Republic of the Union of Myanmar, alongside Buddhist militias, has utilized systematic violence to eliminate evidence of Rohingya presence in Myanmar. By destroying the architectural and historical evidence of their presence, the militias and government attempted to justify their narrative that the Rohingya did, and had never, belonged. The targeted elimination of architectural representations of the Rohingya happened alongside widespread violence, forced movement, and state-sanctioned death. Destroying and preventing access to Rohingya religious sites were strategic efforts by the government and militias to demonstrate that the Rohingya did not, and had never, belonged to Myanmar.""",
        'zh': """缅甸联邦共和国与佛教民兵共同运用系统性暴力，消除罗兴亚人曾在缅甸存在的证据。民兵和政府通过摧毁能够证明罗兴亚人存在的建筑与历史证据，试图为“罗兴亚人现在不属于、过去也从未属于缅甸”的叙事提供正当性。对罗兴亚人建筑表征的定向消除，与大范围暴力、强迫迁移和国家认可的杀戮同时发生。摧毁罗兴亚宗教场所并阻止他们进入这些地点，是政府和民兵为了证明罗兴亚人现在不属于、过去也从未属于缅甸而采取的策略性行动。""",
    },
    {'kind': 'heading', 'en': 'Xinjiang: State Sanctioned Nationalist Violence', 'zh': '新疆：国家认可的民族主义暴力'},
    {
        'kind': 'para',
        'en': """China’s nationalist vision varies from the previous cases of Myanmar and India. Whereas Myanmar and India’s cases are examples of religious nationalism targeting religious minorities, China’s is secular nationalism that aligns with the one-party state’s cultural and political vision. Nonetheless, similar tactics of cultural destruction have been utilized in all three cases. In China, minority groups that deviate from the state’s envisioned singular identity are often punished. In the case of Xinjiang, this has escalated to genocidal levels, particularly since 2017. The destruction of religious texts and worship sites, including churches, Tibetan monasteries, and mosques has been a strategy utilized by the state since the Cultural Revolution from 1966–1976 (Grim and Finke 2010).""",
        'zh': """中国的民族主义愿景不同于前述缅甸和印度案例。缅甸与印度属于宗教民族主义针对宗教少数群体的案例，而中国则是一种与一党制国家文化和政治愿景相一致的世俗民族主义。尽管如此，三个案例都采用了相似的文化破坏策略。在中国，偏离国家所设想的单一身份的少数群体经常受到惩罚。就新疆而言，这一状况尤其自2017年以来升级到了种族灭绝的程度。自1966至1976年文化大革命以来，国家便把摧毁宗教文本和礼拜场所——包括教堂、藏传佛教寺院和清真寺——作为一种策略（Grim and Finke 2010）。""",
    },
    {
        'kind': 'para',
        'en': """Xinjiang (meaning the new frontier in Mandarin) was incorporated into China as a province in 1884 under the Qing dynasty. The area was inhabited primarily by Muslims of Turkic descent. The region had a history of instability, uprising, and occasional attempts to establish independent Muslim states. China disputed the history of the region, stating that Xinjiang was part of China since the third century. Additionally, China claims that the religion of Islam was imposed from the Arab Empire and thus not indigenous to the region (The State Council Information Office of the People’s Republic of China 2019). When the People’s Republic of China (PRC) was formally established in 1949, local resistance in Xinjiang continued. The PRC made Xinjiang an autonomous region in 1955 as a concession to the non-Han Chinese in the region in hopes of quelling tensions. This policy is similar to what China did with other ethnic and religious minorities such as in Tibet or Inner Mongolia. However, these regions were not truly autonomous. Strict assimilation measures were enacted that limited the practice of minority religions (Heberer 2017). China also encouraged increased Han migration to the region. State-led suppression of minorities escalated during the Cultural Revolution. During this time, anything that deviated from Mao’s vision of a unitary state was strongly discouraged and punished. Practicing certain religions, particularly Tibetan Buddhism and Islam, speaking in a language other than Chinese, eating certain cultural cuisines, and wearing traditional clothes, were all strongly discouraged (Ruser, Leibold, Munro, and Hoja 2020). During the Cultural Revolution, approximately 50% of all mosques in China were destroyed (Ruser, Leibold, Munro, and Hoja 2020).""",
        'zh': """新疆——在汉语中意为“新的疆域”——于1884年清朝统治时期被纳入中国，成为一个省。当地居民主要是具有突厥血统的穆斯林。该地区历史上长期存在不稳定、起义，以及偶尔出现的建立独立穆斯林国家的尝试。中国对这一地区的历史持不同说法，主张新疆从三世纪起就是中国的一部分；中国还声称，伊斯兰教是由阿拉伯帝国强加于当地的，因此并非该地区的本土宗教（The State Council Information Office of the People’s Republic of China 2019）。1949年中华人民共和国正式成立后，新疆的地方抵抗仍在继续。1955年，中华人民共和国把新疆设为自治区，作为对当地非汉族群的让步，希望借此缓和紧张局势。这项政策与中国在西藏、内蒙古等其他族群和宗教少数群体地区采取的做法相似。然而，这些地区并没有获得真正自治。国家实施严格的同化措施，限制少数群体的宗教实践（Heberer 2017），并鼓励更多汉族人口迁入。文化大革命期间，国家主导的少数群体压制进一步升级。任何偏离毛泽东单一国家愿景的事物都遭到严厉压制和惩罚。信奉某些宗教——尤其藏传佛教和伊斯兰教——使用汉语以外的语言、食用特定民族饮食、穿着传统服装，都受到强烈限制（Ruser, Leibold, Munro, and Hoja 2020）。文化大革命期间，中国约有50%的清真寺被摧毁（Ruser, Leibold, Munro, and Hoja 2020）。""",
    },
    {
        'kind': 'para',
        'en': """As China liberalized following Mao’s death, the government instituted changes in Xinjiang. Some of these changes, such as allowing the rapid rebuilding of mosques, indicated a potential new openness toward minority religions. By the end of the 1990s, the number of new mosques nearly returned to pre-Cultural Revolution numbers (Ruser, Leibold, Munro, and Hoja 2020). At the same time, however, local Han leaders also feared that giving increased autonomy to the Uyghurs in Xinjiang would nurture instability and separatism, especially in the shadow of uprisings in neighboring Afghanistan and Iran (Mukherjee 2010). Over the following decades, occasional skirmishes and bomb attacks occurred in Urumqi, Xinjiang’s capital, and in Beijing. These attacks were carried out by Uyghur separatists and provoked China’s counter-terrorism response (Ruser, Leibold, Munro, and Hoja 2020).""",
        'zh': """毛泽东去世后，随着中国实行自由化改革，政府也在新疆推行了一些变化。其中部分措施——例如允许迅速重建清真寺——似乎表明政府可能对少数群体宗教采取更加开放的态度。到20世纪90年代末，新建清真寺的数量几乎恢复到文化大革命前的水平（Ruser, Leibold, Munro, and Hoja 2020）。然而与此同时，当地汉族领导人担忧，给予新疆维吾尔人更多自治会助长不稳定和分离主义，尤其是在邻近的阿富汗与伊朗发生起义的背景下（Mukherjee 2010）。此后数十年，新疆首府乌鲁木齐和北京间或发生冲突和炸弹袭击。这些袭击由维吾尔分离主义者实施，并引发中国的反恐回应（Ruser, Leibold, Munro, and Hoja 2020）。""",
    },
    {
        'kind': 'para',
        'en': """China began reframing the Xinjiang issue in the shadow of the Global War on Terrorism in the twenty-first century. In 2008, the Xinjiang separatist group Turkistan Islamic Party (ETIM) warned of attacks targeting the Beijing summer Olympics. The threat targeting the Olympics, in addition to attacks throughout Xinjiang in 2008, led China to take an increasingly aggressive approach in Xinjiang. The government first targeted cultural sites that were considered non-compliant due to lack of electricity, failure to register with the state, or poor road access (Raza 2019). In 2014, China began exerting the need for “deradicalization” and “transformation through education” via the “Strike Hard Campaign Against Violent Terrorism” initiative (Doyon 2019; Zhou 2019). Historically, this approach targeted the Falun Gong but under the leadership of Communist Party Chief Zhang Chunxian, this program was drastically expanded to include additional religious minority groups, specifically the Uyghurs (Tong 2009; Greitens, Lee, and Yazici 2020).""",
        'zh': """进入二十一世纪后，中国开始在“全球反恐战争”的背景下重新界定新疆问题。2008年，新疆分离主义组织突厥斯坦伊斯兰党（ETIM）发出警告，声称将对北京夏季奥运会发动袭击。针对奥运会的威胁，加上2008年新疆各地发生的袭击，促使中国在新疆采取愈加激进的做法。政府最初针对的是被认定“不合规”的文化场所，不合规理由包括缺少电力、未向国家登记或道路交通不便（Raza 2019）。2014年，中国通过“严厉打击暴力恐怖活动专项行动”，开始强调“去极端化”和“教育转化”的必要性（Doyon 2019; Zhou 2019）。历史上，这套做法曾以法轮功为对象；但在中共新疆党委书记张春贤领导下，该计划大幅扩展到其他宗教少数群体，尤其是维吾尔人（Tong 2009; Greitens, Lee, and Yazici 2020）。""",
    },
    {
        'kind': 'para',
        'en': """Around the same time of this escalation and new policy approach, China reportedly began its “re-education” camps as part of the “people’s war on terror.” The camps are said to help “integrate” and “Sinicize” minorities into Chinese society. Although estimates vary, between 1.5–3 million ethnic and religious minorities, primarily Uyghurs and other Muslims, are said to be detained in the camps (Greitens, Lee, and Yazici 2020). This accounts for up to 10% of the total Uyghur population. The policy of the camps is to eliminate cultural practices that do not align with Sino identity such as beards, hijabs, fasting, abstention of pork, and use of traditional Muslim names for children such as Muhammad (Denyer 2020). Additional reports detail forced contraception and/or sterilization of Uyghur women (Associated Press 2020).""",
        'zh': """据报道，大约在局势升级、政策路径改变的同一时期，中国把“再教育营”作为“人民反恐战争”的一部分加以推行。这些营地据称旨在帮助少数群体“融入”中国社会并实现“中国化”。尽管估计数字不一，据称有150万至300万名族群和宗教少数群体被拘禁在营地中，其中主要是维吾尔人和其他穆斯林（Greitens, Lee, and Yazici 2020），人数最高可达维吾尔总人口的10%。营地政策旨在消除不符合“中国式身份”的文化实践，例如蓄须、佩戴头巾、斋戒、不食猪肉，以及给孩子取“穆罕默德”等传统穆斯林姓名（Denyer 2020）。另有报道详细描述了针对维吾尔女性的强制避孕和／或绝育（Associated Press 2020）。""",
    },
    {
        'kind': 'para',
        'en': """Alongside the elimination of non-Sino cultural practices, China has actively destroyed religious sites of the Uyghurs. Using satellite evidence, a report by the Australian Strategic Policy Institute found that 16,000 mosques in Xinjiang (65% of the total) have been destroyed or damaged since 2017. Of those mosques, 8,500 were completely demolished. Additionally, an estimated 30% of all sacred sites were destroyed with an additional 28% damaged or altered. These sites include shrines, cemeteries, and pilgrimage sites (Ruser, Leibold, Munro, and Hoja 2020). This systematic elimination of sacred sites in conjunction with “re-education” camps by the Chinese government is an attempt to demonstrate that culture outside the narrowly defined Chinese state identity is not welcomed.""",
        'zh': """在消除非“中国式”文化实践的同时，中国还积极摧毁维吾尔人的宗教场所。澳大利亚战略政策研究所的一份报告利用卫星证据发现，自2017年以来，新疆有1.6万座清真寺被摧毁或损坏，占清真寺总数的65%；其中8500座被彻底拆除。此外，据估计，全部神圣场所中约30%被摧毁，另有28%受损或遭到改造。这些场所包括圣陵、墓地和朝圣地（Ruser, Leibold, Munro, and Hoja 2020）。中国政府把系统性消除神圣场所与“再教育营”结合起来，意在表明：不符合其狭隘定义的中国国家身份的文化不受欢迎。""",
    },
    {'kind': 'heading', 'en': 'Conclusion', 'zh': '结论'},
    {
        'kind': 'para',
        'en': """This article discussed how the destruction of cultural and religious sites of minority Muslims has been used as a nationalist tactic in India, Myanmar, and Xinjiang, China. In all three cases, the perpetrator has attempted to demonstrate that the targeted group did not historically belong to the land and posed a current security threat. Such historical revisionism attempts to re-frame national identities. In India, Hindu nationalists considered the Babri Masjid a sign of historical Muslim aggression. Destroying the Babri Masjid was seen as correcting a historical wrong and asserting Hindu authority over a sacred space in Ayodhya. In Myanmar, Rohingya Muslims are framed as recent, and violent, illegal immigrants who threaten to destroy the Buddhist nature of Myanmar. Buddhist militias, in conjunction with the state, have destroyed or converted multiple Islamic sites as well as forced removals of the Rohingya population. These violent acts occurred after increasingly aggressive measures by the state to limit the agency and autonomy of the Rohingya. Finally, approximately 16,000 mosques have been damaged or destroyed in Xinjiang, China. Unlike India and Myanmar, China’s policy has been carried out almost exclusively by the state. China’s mosque destruction was also not done in the name of religious nationalism. Instead, it was carried out as part of a state-led secular nationalist vision. However, in all three cases, the perpetrators justify their actions by framing Muslims as security threats.""",
        'zh': """本文讨论了在印度、缅甸和中国新疆，摧毁穆斯林少数群体的文化与宗教场所如何被用作民族主义策略。在三个案例中，实施者都试图证明：被针对的群体在历史上不属于相关土地，并且当前构成安全威胁。这种历史修正主义试图重新界定国家身份。在印度，印度教民族主义者把巴布里清真寺视为穆斯林历史侵略的象征；摧毁它被理解为纠正历史错误，并确立印度教徒对阿约提亚一处神圣空间的权威。在缅甸，罗兴亚穆斯林被描述成新近到来、具有暴力倾向的非法移民，被指控威胁破坏缅甸的佛教性质。佛教民兵与国家联合摧毁或改造多处伊斯兰场所，并强迫罗兴亚人迁离。这些暴力行为发生之前，国家已经采取日益激进的措施，限制罗兴亚人的行动能力和自治。最后，中国新疆约有1.6万座清真寺受损或被毁。不同于印度和缅甸，中国的政策几乎完全由国家实施；对清真寺的破坏也并非以宗教民族主义的名义进行，而是国家主导的世俗民族主义愿景的一部分。不过，在三个案例中，实施者都通过把穆斯林描述成安全威胁来为其行动辩护。""",
    },
]


references = [
    (
        "Abtahi, Hirad. 2001. “The Protection of Cultural Property in Times of Armed Conflict: The Practice of the International Criminal Tribunal for the Former Yugoslavia.” Harvard Human Rights Journal 14(1).",
        "中文题名：《武装冲突时期文化财产的保护：前南斯拉夫问题国际刑事法庭的实践》。",
    ),
    (
        "Al Azm, Amr. 2015. “The Pillaging of Syria’s Cultural Heritage.” Middle East Institute 22(1).",
        "中文题名：《对叙利亚文化遗产的劫掠》。",
    ),
    (
        "Anderson, Benedict. 2006. Imagined Communities: Reflections on the Origin and Spread of Nationalism. Verso Books.",
        "中文题名：《想象的共同体：民族主义的起源与传播》。",
    ),
    (
        "APHR. 2018. “The Rohingya Crisis: Past, Present, and Future: Summary Report of Findings from Fact-Finding Mission to Bangladesh.” ASEAN Parliamentarians for Human Rights.",
        "中文题名：《罗兴亚危机：过去、现在与未来——孟加拉国实况调查团调查结果摘要报告》。",
    ),
    (
        "Associated Press. 2020. “China Cuts Uighur Births with IUDs, Abortion, Sterilization.” AP News, https://apnews.com/article/269b3de1af34e17c1941a514f78d764c.",
        "中文题名：《中国以宫内节育器、堕胎和绝育减少维吾尔人生育》。",
    ),
    (
        "Auwera, Sigrid van der. 2012. “Contemporary Conflict, Nationalism, and the Destruction of Cultural Property During Armed Conflict: A Theoretical Framework.” Journal of Conflict Archaeology 7(1): 49–65.",
        "中文题名：《当代冲突、民族主义与武装冲突期间的文化财产破坏：一个理论框架》。",
    ),
    (
        "Bacchetta, Paola. 2000. “Sacred Space in Conflict in India: The Babri Masjid Affair.” Growth and Change 31(2): 255–284.",
        "中文题名：《印度冲突中的神圣空间：巴布里清真寺事件》。",
    ),
    (
        "Baker, Aryn, and Majdal Anjar. 2012. “Syria’s Looted Past: How Ancient Artifacts Are Being Traded for Guns.” Time World: 10–16.",
        "中文题名：《遭劫掠的叙利亚过去：古代文物如何被用于交换枪支》。",
    ),
    (
        "Berlie, Jean. 2008. The Burmanization of Myanmar’s Muslims. White Lotus Press. 61.",
        "中文题名：《缅甸穆斯林的缅族化》。",
    ),
    (
        "Bhatt, Chetan. 2001. Hindu Nationalism: Origins, Ideologies, and Modern Myths. Berg.",
        "中文题名：《印度教民族主义：起源、意识形态与现代神话》。",
    ),
    (
        "Brosche, Johan, Mattias Legner, Joakim Kreutz, and Akram Ijla. 2017. “Heritage under Attack: Motives for Targeting Cultural Property During Armed Conflict.” International Journal of Heritage Studies 23(3): 248–260.",
        "中文题名：《遭受攻击的遗产：武装冲突期间以文化财产为目标的动机》。",
    ),
    (
        "Chandra, Bipan, Amales Tripathi, and Barun De. 1972. Freedom Struggle. National Book Trust, India.",
        "中文题名：《自由斗争》。",
    ),
    (
        "Coningham, Robin, and Nick Lewer. 2000. “Archaeology and Identity in South Asia: Interpretations and Consequences.” Antiquity 74(285): 664–667.",
        "中文题名：《南亚的考古学与身份：阐释及其后果》。",
    ),
    (
        "Denyer, Simon. 2018. “Former Inmates of China’s Muslim ‘Re-education’ Camps Tell of Brainwashing, Torture.” The Washington Post, 17 May 2018.",
        "中文题名：《中国穆斯林“再教育”营前被拘押者讲述洗脑与酷刑》。",
    ),
    (
        "Doyon, Jerome. 2019. “Counter-Extremism in Xinjiang: Understanding China’s Community-focused Counter-terrorism Tactics.” War on the Rocks, 14 January 2019, https://warontherocks.com/2019/01/counter-extremism-in-xinjiang-understanding-chinas-community-focused-counter-terrorism-tactics/.",
        "中文题名：《新疆反极端主义：理解中国以社区为中心的反恐策略》。",
    ),
    (
        "Frydenlund, Iselin. 2017. “Religious Liberty for Whom? The Buddhist Politics of Religious Freedom during Myanmar’s Transition to Democracy.” Nordic Journal of Human Rights 35(1): 55–73.",
        "中文题名：《谁的宗教自由？缅甸民主转型期间宗教自由的佛教政治》。",
    ),
    (
        "Greitens, Sheena, Myunghee Lee, and Emir Yazici. 2020. “Counterterrorism and Preventive Repression: China’s Changing Strategy in Xinjiang.” International Security 44(3): 9–47.",
        "中文题名：《反恐与预防性镇压：中国在新疆不断变化的策略》。",
    ),
    (
        "Grewal, Jagtar Singh. 1990. The Sikhs of Punjab. Cambridge University Press.",
        "中文题名：《旁遮普的锡克教徒》。",
    ),
    (
        "Grim, Brian J., and Roger Finke. 2010. The Price of Freedom Denied: Religious Persecution and Conflict in the Twenty-First Century.",
        "中文题名：《自由被拒绝的代价：二十一世纪的宗教迫害与冲突》。",
    ),
    (
        "Habib, Mohshin, Christine Jubb, Salahuddin Ahmad, Masudur Rahman, and Henri Pallard. 2018. “Forced Migration of Rohingya: The Untold Experience.” Ontario International Development Agency.",
        "中文题名：《罗兴亚人的被迫迁移：未被讲述的经历》。",
    ),
    (
        "Heberer, Thomas. 2017. China and Its National Minorities: Autonomy or Assimilation: Autonomy or Assimilation. Routledge.",
        "中文题名：《中国及其少数民族：自治还是同化》。",
    ),
    (
        "Human Rights Watch. 2013. “Crimes Against Humanity and Ethnic Cleansing of Rohingya Muslims in Burma’s Arakan State.”",
        "中文题名：《缅甸阿拉干邦针对罗兴亚穆斯林的反人类罪与族群清洗》。",
    ),
    (
        "International Crisis Group. 2013. “The Dark Side of Transition: Violence Against Muslims in Myanmar.” Asia Report (251): 32.",
        "中文题名：《转型的阴暗面：缅甸针对穆斯林的暴力》。",
    ),
    (
        "Jaffrelot, Christophe. 2007. Hindu Nationalism: A Reader. Princeton University Press.",
        "中文题名：《印度教民族主义读本》。",
    ),
    (
        "Kaldor, Mary. 2004. “Nationalism and Globalisation.” Nations and Nationalism 10(1–2): 161–177.",
        "中文题名：《民族主义与全球化》。",
    ),
    (
        "Kohl, Philip. 1998. “Nationalism and Archaeology: On the Constructions of Nations and the Reconstructions of the Remote Past.” Annual Review of Anthropology 27(1): 223–246.",
        "中文题名：《民族主义与考古学：论民族国家的建构与遥远过去的重构》。",
    ),
    (
        "Kohl, Philip, and Claire Fawcett. 1995. Nationalism, Politics and the Practice of Archaeology. Cambridge University Press.",
        "中文题名：《民族主义、政治与考古学实践》。",
    ),
    (
        "Khalidi, Lamya. 2017. “The Destruction of Yemen and Its Cultural Heritage.” International Journal of Middle East Studies 49(4): 735–738.",
        "中文题名：《也门及其文化遗产的毁灭》。",
    ),
    (
        "Knuth, Rebecca. 2006. Burning Books and Leveling Libraries: Extremist Violence and Cultural Destruction. Praeger. 447.",
        "中文题名：《焚烧书籍与夷平图书馆：极端主义暴力与文化毁灭》。",
    ),
    (
        "Mackenzie, Simon and Davis, Tess. 2016. “Temple Looting in Cambodia: Anatomy of a Statue Trafficking Network.” In Art Crime, 179–199. Palgrave Macmillan, London.",
        "中文题名：《柬埔寨寺庙劫掠：雕像贩运网络的结构》。",
    ),
    (
        "Maizland, Lindsay. 2020. “India’s Muslims: An Increasingly Marginalized Population.” Council on Foreign Relations, 20 August 2020, https://www.cfr.org/backgrounder/india-muslims-marginalized-population-bjp-modi.",
        "中文题名：《印度穆斯林：日益被边缘化的人口》。",
    ),
    (
        "Metcalf, Thomas. 1965. The Aftermath of Revolt: India 1857–1870. Princeton University Press.",
        "中文题名：《起义的余波：1857—1870年的印度》。",
    ),
    (
        "Mukherjee, Kunal. 2010. “The Uyghur Question in Contemporary China.” Strategic Analysis 34(3): 420–435.",
        "中文题名：《当代中国的维吾尔问题》。",
    ),
    (
        "Nachemson, Andrew. 2020. “Myanmar ‘Undermining Lifeblood of Democracy’ before Polls.” Al-Jazeera, 7 November 2020.",
        "中文题名：《缅甸在选举前“损害民主的生命线”》。",
    ),
    (
        "Noyes, James. 2016. The Politics of Iconoclasm. Religion, Violence and the Culture of Image-Breaking in Christianity and Islam. I. B. Tauris.",
        "中文题名：《圣像破坏的政治：基督教与伊斯兰教中的宗教、暴力和毁像文化》。",
    ),
    (
        "Rai, Mridu. 2009. “To Tear the Mask Off of the Face of the Past: Archaeology and Politics in Jammu and Kashmir.” The Indian Economic and Social History Review 46(3): 401–426.",
        "中文题名：《撕下过去脸上的面具：查谟和克什米尔的考古学与政治》。",
    ),
    (
        "Ratnagar, Shereen. 2004. “Archaeology at the Heart of a Political Confrontation: The Case of Ayodhya.” Current Anthropology 45(2): 239–259.",
        "中文题名：《政治对抗核心的考古学：阿约提亚案例》。",
    ),
    (
        "Raza, Zainab. 2019. “China’s ‘Political Re-education’ Camps of Xinjiang’s Uyghur Muslims.” Asian Affairs 50: 488–501.",
        "中文题名：《中国针对新疆维吾尔穆斯林的“政治再教育”营》。",
    ),
    (
        "Riedlmayer, Andras. 2002. “From the Ashes: The Past and Future of Bosnia’s Cultural Heritage.” In Islam and Bosnia: Conflict Resolution and Foreign Policy in Multi-ethnic States, edited by Maya Shatzmiller, 98–135. McGill-Queens University Press.",
        "中文题名：《从灰烬中重生：波斯尼亚文化遗产的过去与未来》，载《伊斯兰与波斯尼亚：多族群国家的冲突解决与外交政策》。",
    ),
    (
        "Rogers, Benedict. 2016. Burma: A Nation at the Crossroads—Revised Edition. Random House.",
        "中文题名：《缅甸：十字路口的国家（修订版）》。",
    ),
    (
        "Rothfield, Lawrence. 2009. The Rape of Mesopotamia: Behind the Looting of the Iraq Museum. University of Chicago Press.",
        "中文题名：《美索不达米亚之劫：伊拉克博物馆遭洗劫的幕后》。",
    ),
    (
        "Ruser, Nathan, James Leibold, Kelsey Munro, and Tilla Hoja. 2020. Cultural Erasure: Tracing the Destruction of Uyghur and Islamic Spaces in Xinjiang. Australian Strategic Policy Institute.",
        "中文题名：《文化抹除：追踪新疆维吾尔与伊斯兰空间的毁坏》。",
    ),
    (
        "Sells, Michael. 2003. “Crosses of Blood: Sacred Space, Religion, and Violence in Bosnia-Hercegovina.” Sociology of Religion 64(3): 309–331.",
        "中文题名：《鲜血的十字架：波斯尼亚—黑塞哥维那的神圣空间、宗教与暴力》。",
    ),
    (
        "Sithu Aung Myint. 2016. “Of Pagodas, Churches and Mosques.” Frontier Myanmar, 15 May 2016, https://frontiermyanmar.net/en/pagodas-churches-and-mosques.",
        "中文题名：《佛塔、教堂与清真寺》。",
    ),
    (
        "Smith, Anthony. 2009. Ethno-symbolism and Nationalism: A Cultural Approach. Routledge.",
        "中文题名：《族群象征主义与民族主义：一种文化研究路径》。",
    ),
    (
        "Sørensen, Marie Louise Stig, and Dacia Viejo-Rose. 2015. War and Cultural Heritage. Cambridge University Press.",
        "中文题名：《战争与文化遗产》。",
    ),
    (
        "Srivastava, Sushil. 1991. The Disputed Mosque: A Historical Inquiry. Vistaar Publications.",
        "中文题名：《有争议的清真寺：一项历史调查》。",
    ),
    (
        "Stovel, Herb, Nicholas Stanley-Price, and Robert Killick. 2005. “Conservation of Living Religious Heritage.” In Conservation of Living Religious Heritage: Papers from the ICCROM 2003 Forum on Living Religious Heritage: Conserving the Sacred, 1–11.",
        "中文题名：《活态宗教遗产的保护》，载《活态宗教遗产保护：ICCROM 2003年活态宗教遗产论坛论文集——保护神圣事物》。",
    ),
    (
        "Swart, Mia. 2020. “More Than Bricks: How International Law Protects Cultural Sites.” Al Jazeera.",
        "中文题名：《不只是砖石：国际法如何保护文化场所》。",
    ),
    (
        "Szep, Jason. 2013. “Special Report: Buddhist Monks Incite Muslim Killings in Myanmar.” Reuters.",
        "中文题名：《特别报道：佛教僧侣煽动在缅甸杀害穆斯林》。",
    ),
    (
        "The State Council Information Office of the People’s Republic of China. 2019. Historical Matters concerning Xinjiang. Foreign Languages Press.",
        "中文题名：《新疆的若干历史问题》。",
    ),
    (
        "Truschke, Audrey. 2016. Culture of Encounters: Sanskrit at the Mughal Court. Penguin UK.",
        "中文题名：《相遇的文化：莫卧儿宫廷中的梵语》。",
    ),
    (
        "United Nations Human Rights Council (UNHRC). 2018. “Report of Independent International Fact-finding Mission on Myanmar.”",
        "中文题名：《缅甸问题独立国际事实调查团报告》。",
    ),
    (
        "US Department of State. 2017. “2016 Report on International Religious Freedom.” https://www.state.gov/j/drl/rls/irf/2016/eap/268718.htm.",
        "中文题名：《2016年国际宗教自由报告》。",
    ),
    (
        "Wade, Francis. 2019. Myanmar’s Enemy Within. Zed Books.",
        "中文题名：《缅甸内部的敌人》。",
    ),
    (
        "White, Chloe. 2015. “Protection for Whom? Violations of International Law in Myanmar’s New Race and Religion Protection Laws.” Georgetown Institute for Women, Peace and Security.",
        "中文题名：《保护谁？缅甸新种族与宗教保护法对国际法的违反》。",
    ),
    (
        "Wilkinson, Steven. 2005. Religious Politics and Communal Violence. Oxford University Press.",
        "中文题名：《宗教政治与群体暴力》。",
    ),
    (
        "Zhou, Zunyou. 2019. “Chinese Strategy for De-radicalization.” Terrorism and Political Violence 31(6): 1187–1209.",
        "中文题名：《中国的去极端化战略》。",
    ),
]


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(0.8)
    canvas.line(18 * mm, height - 13 * mm, width - 18 * mm, height - 13 * mm)
    if doc.page > 1:
        canvas.setFont('Arial', 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, height - 10 * mm, 'Journal of Religion and Violence 9(1), 2021 | EN-ZH bilingual edition')
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 13 * mm, width - 18 * mm, 13 * mm)
    canvas.setFont('STHeiti', 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8 * mm, '英文原文后接中文译文 | 2026-09-09')
    canvas.setFont('Arial', 7.2)
    canvas.drawRightString(width - 18 * mm, 8 * mm, str(doc.page))
    canvas.restoreState()


def add_pair(story, en, zh, kind='para'):
    if kind == 'heading':
        story.append(CondPageBreak(42 * mm))
        story.append(Paragraph(e(en), styles['Section']))
        story.append(Paragraph(e(zh), styles['Section']))
        return

    en_style = styles['EnglishQuote'] if kind == 'quote' else styles['English']
    if kind == 'footnote':
        en_style = styles['ReferenceEN']
    story.append(CondPageBreak(20 * mm))
    story.append(Paragraph('ENGLISH ORIGINAL', styles['LabelEN']))
    story.append(Paragraph(e(en), en_style))
    story.append(CondPageBreak(22 * mm))
    story.append(Paragraph('中文译文', styles['LabelCN']))
    story.append(Paragraph(e(zh), styles['Chinese']))
    story.append(Spacer(1, 3.2 * mm))


doc = SimpleDocTemplate(
    str(OUT), pagesize=A4,
    leftMargin=18 * mm, rightMargin=18 * mm,
    topMargin=20 * mm, bottomMargin=18 * mm,
    title='People Don’t Want a Mosque Here - 英中逐段对照',
    author='Andrea Malji; Chinese translation prepared for study',
    subject='Paragraph-by-paragraph English-Chinese bilingual translation',
)

story = [
    Spacer(1, 16 * mm),
    Paragraph(e('People Don’t Want a Mosque Here: Destruction of Minority Religious Sites as a Strategy of Nationalism'), styles['CoverTitle']),
    Paragraph(e('“人们不希望这里有清真寺”：摧毁少数群体宗教场所作为民族主义策略'), styles['CoverCN']),
    Spacer(1, 5 * mm),
    Paragraph(e('Andrea Malji | Hawai’i Pacific University'), styles['CoverMeta']),
    Paragraph(e('Journal of Religion and Violence, Vol. 9, No. 1, 2021'), styles['CoverMeta']),
    Spacer(1, 9 * mm),
    Paragraph(e('排版说明：本文件依据用户提供的原始 PDF 制作。正文按“英文原文段落—中文译文段落”排列，保留原有标题、摘要、章节、引文、引注和脚注；仅修复由 PDF 换行造成的断词与明显空格问题。参考文献保留原始著录信息，中文行只翻译题名，便于检索；译名仅供课程学习使用。'), styles['Note']),
    Spacer(1, 7 * mm),
    Paragraph(e('Reading order / 阅读顺序'), styles['Section']),
    Paragraph(e('Each English paragraph is followed immediately by its complete Chinese translation. Section headings appear in English and Chinese. Citations in parentheses correspond to the original article’s reference list.'), styles['English']),
    Paragraph(e('每一段英文原文之后紧接完整中文译文；章节标题同时列出英文和中文。正文括号内的引文信息对应原论文的参考文献表。'), styles['Chinese']),
    PageBreak(),
]

for item in body:
    add_pair(story, item['en'], item['zh'], item['kind'])

story.append(PageBreak())
story.append(Paragraph(e('References / 参考文献'), styles['Section']))
story.append(Paragraph(e('The bibliographic entries below retain the original publication details. Chinese lines translate titles only and are not official published Chinese titles.'), styles['English']))
story.append(Paragraph(e('以下著录信息保留原文格式；中文行只提供题名翻译，并不代表已有正式出版的中文题名。'), styles['Chinese']))
story.append(Spacer(1, 4 * mm))

for ref_en, ref_zh in references:
    story.append(CondPageBreak(20 * mm))
    story.append(Paragraph('ENGLISH REFERENCE', styles['LabelEN']))
    story.append(Paragraph(e(ref_en), styles['ReferenceEN']))
    story.append(CondPageBreak(15 * mm))
    story.append(Paragraph('中文题名', styles['LabelCN']))
    story.append(Paragraph(e(ref_zh), styles['ReferenceCN']))
    story.append(Spacer(1, 2.2 * mm))

doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(OUT)
