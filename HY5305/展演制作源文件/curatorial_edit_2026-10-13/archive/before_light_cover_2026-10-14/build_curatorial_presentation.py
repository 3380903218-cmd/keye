from pathlib import Path
import json, math, re, base64
from PIL import Image
import slide_toolkit as t

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).resolve().parent
WORK = Path('/tmp/hy5305-curatorial-work')
PREVIEW = WORK / 'deck-preview'
PREVIEW.mkdir(parents=True, exist_ok=True)
content = json.loads((SOURCE / 'presentation_content.json').read_text())
poster = ROOT / 'HY5305_海报_参考风格竖版/Porcelain_in_Translation_Flow_A1_Portrait.png'
vase = ROOT / '文物图片/微信图片_20260910150741_59_71.png'
bowl = ROOT / '海报制作源文件/assets/falangcai_bowl_highres.jpg'
plate = ROOT / '文物图片/微信图片_20260910154121_63_71.png'
pres = t.prs
clock = 0
timing, display = [], []


def start(index, chapter, background='paper', footer_left=18):
    if index > 1:
        t.slide = pres.slides.add_slide(pres.slide_layouts[6])
    t.svg, t.svg_defs = [], []
    t.rect(f'S{index} — gallery background', 0, 0, t.W, t.H, background)
    if chapter:
        t.text(f'S{index} — exhibition chapter', chapter, 18, 13, 230, 8, 12.5, 'deep', t.SANS, spacing=.25)
    t.text(f'S{index} — folio', f'{index:02d}', 313, 180.5, 10, 6, 11, 'muted', t.SANS, align='right')
    if index > 1:
        t.path(f'S{index} — folio rule', [('M', footer_left, 187), ('L', 323, 187)], 'line', lw=.55)


def finish(index):
    global clock
    data = content['slides'][index - 1]
    words = len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", ' '.join(data['english'])))
    seconds = 5 * math.ceil((words * 60 / 95 + 3) / 5)
    timing.append({'slide': index, 'title': data['title'], 'english_words': words, 'start_seconds': clock, 'end_seconds': clock + seconds, 'target_seconds': seconds})
    t.slide.notes_slide.notes_text_frame.text = (
        f'Slide {index}: {data["title"]}\nSuggested segment: {clock//60}:{clock%60:02d}–{(clock+seconds)//60}:{(clock+seconds)%60:02d}. English speaking only.\n\n'
        + '\n\n'.join(data['english'])
        + ('\n\nContext source: ' + data['source'] if data.get('source') else '\n\nContent authority: project abstract.docx. Network connections are conceptual.')
    )
    clock += seconds
    svg = '<?xml version="1.0" encoding="UTF-8"?>\n' + f'<svg xmlns="http://www.w3.org/2000/svg" width="{t.W}mm" height="{t.H}mm" viewBox="0 0 {t.W} {t.H}"><title>Slide {index}: {data["title"]}</title><defs>' + ''.join(t.svg_defs) + '</defs>' + ''.join(t.svg) + '</svg>'
    (PREVIEW / f'slide-{index}.svg').write_text(svg)
    display.append([s.text for s in t.slide.shapes if s.has_text_frame and s.text])


# 1. Opening spread: the approved exhibition poster in full, with a quiet contents list.
start(1, '', 'dark')
for run in t.slide.shapes[1].text_frame.paragraphs[0].runs:
    run.font.color.rgb = t.rgb('ivory')
t.svg[1] = t.svg[1].replace(t.hexcol('muted'), t.hexcol('ivory'))
with Image.open(poster) as im:
    poster_width = 180 * im.width / im.height
t.picture('S1 — approved complete exhibition poster', poster, 9, 5, poster_width, 180)
t.text('S1 — presentation context', 'AN EXHIBITION IN THREE OBJECTS', 154, 23, 169, 8, 12.5, 'gold', t.SANS, spacing=.3)
t.text('S1 — exhibition title', 'Porcelain\nin Translation', 152, 43, 170, 43, 39, 'ivory', t.SERIF, leading=44)
t.text('S1 — exhibition framing', 'One porcelain tradition.\nThree worlds.', 154, 95, 166, 24, 23, 'ivory', t.SERIF, italic=True, leading=27)
t.path('S1 — contents rule', [('M', 154, 128), ('L', 318, 128)], 'line', lw=.75)
for y, number, label in [(137, '01', 'The Chinese past'), (151, '02', 'The Qing court'), (165, '03', 'European markets')]:
    t.text('S1 — contents number ' + number, number, 154, y, 14, 8, 13, 'gold', t.SANS)
    t.text('S1 — contents label ' + number, label, 174, y - .5, 143, 10, 18, 'ivory', t.SANS)
t.text('S1 — presenter', 'Presented by Xiwen Wang', 154, 180.5, 148, 8, 15.5, 'ivory', t.SANS)
finish(1)

# 2. Full object and glaze sample, positioned as a catalogue spread.
start(2, '01    THE CHINESE PAST')
t.text('S2 — title', 'Reviving\ncopper-red', 18, 31, 168, 38, 37, 'ink', t.SERIF, leading=42)
t.text('S2 — technical history', 'Jingdezhen potters recovered\nMing copper-red glazing.', 18, 83, 169, 23, 22, 'ink', t.SANS, leading=27)
t.text('S2 — exhibition interpretation', 'An inherited technique became\na statement of Qing identity.', 18, 112, 169, 24, 21, 'ink', t.SANS, leading=27)
t.picture('S2 — original glaze detail', vase, 18, 144, 72, 28.8, crop=(310, 485, 535, 575))
t.text('S2 — glaze detail caption', 'Copper-red glaze | detail', 18, 176, 158, 7, 12.5, 'muted', t.SANS)
t.picture('S2 — complete Langyao red vase', vase, 232, 22, 61, 61*730/328, crop=(253, 273, 581, 1003), outline=t.vase_outline)
t.text('S2 — object name', 'Langyao-red Guanyin vase', 194, 165, 130, 10, 19, 'ink', t.SANS)
t.text('S2 — object attribution', 'Kangxi reign, 1662–1722 · Palace Museum', 194, 176, 116, 7, 12.5, 'muted', t.SANS)
finish(2)

# 3. Dark object display, light reading column, and a close view of the painting.
start(3, '', footer_left=184)
t.rect('S3 — charcoal object field', 0, 0, 165, t.H, 'dark')
t.text('S3 — exhibition chapter', '02    THE QING COURT', 18, 13, 139, 8, 12.5, 'ivory', t.SANS, spacing=.25)
t.picture('S3 — original swallow detail', bowl, 18, 34, 81, 48.6, crop=(1150, 850, 1700, 1180))
t.text('S3 — detail caption', 'Swallows\nin enamel', 109, 52, 50, 15, 14, 'ivory', t.SANS, leading=18)
t.picture('S3 — complete imperial falangcai bowl', bowl, 7, 88, 153, 153*832/1605, crop=(201, 808, 1806, 1640), outline=t.bowl_outline)
t.text('S3 — object caption', 'Imperial falangcai “swallows” bowl', 18, 173, 144, 8, 13.5, 'ivory', t.SANS)
t.text('S3 — title', 'Enamels at the\nQing court', 184, 29, 140, 35, 34, 'ink', t.SERIF, leading=40)
t.text('S3 — object date', 'Qianlong reign, 1736–1795', 184, 69, 138, 9, 15, 'muted', t.SANS)
t.text('S3 — materials and painting', 'European enamel knowledge\nmet Chinese porcelain and\nbird-and-flower painting.', 184, 90, 138, 30, 20.5, 'ink', t.SANS, leading=26)
t.text('S3 — court interpretation', 'Beijing court workshops\nselected and adapted these\ntechniques for imperial taste.', 184, 126, 138, 31, 20.5, 'ink', t.SANS, leading=26)
t.path('S3 — workshop rule', [('M', 184, 165), ('L', 321, 165)], 'line', lw=.7)
t.text('S3 — production connection', 'JINGDEZHEN → BEIJING', 184, 170, 125, 8, 12.5, 'deep', t.SANS, spacing=.1)
finish(3)

# 4. A plate, its heraldic centre, and the two directions of an overseas commission.
start(4, '03    EUROPEAN MARKETS')
t.text('S4 — title', 'A coat of arms,\nmade in China.', 18, 31, 201, 37, 35, 'ink', t.SERIF, leading=41)
t.text('S4 — object identity', 'Chinese armorial export plate · eighteenth century', 18, 74, 174, 9, 14, 'muted', t.SANS)
t.picture('S4 — complete original armorial plate', plate, 18, 86, 91, 91, crop=(16, 16, 587, 587), ellipse=True)
t.picture('S4 — original heraldic detail', plate, 127, 96, 59, 59*242/229, crop=(180, 184, 409, 426))
t.text('S4 — heraldry detail caption', 'Heraldry | detail', 127, 163, 66, 8, 12.5, 'muted', t.SANS)
t.text('S4 — Europe label', 'EUROPE', 237, 26, 86, 7, 12.5, 'deep', t.SANS, align='center', spacing=.2)
t.text('S4 — China label', 'CHINA', 237, 79, 86, 7, 12.5, 'deep', t.SANS, align='center', spacing=.2)
t.path('S4 — designs travel east', [('M', 265, 39), ('L', 265, 69)], 'deep', lw=1.0, arrow=True)
t.path('S4 — wares travel west', [('M', 294, 69), ('L', 294, 39)], 'deep', lw=1.0, arrow=True)
t.text('S4 — designs label', 'Designs', 218, 52, 41, 8, 12, 'muted', t.SANS, align='right')
t.text('S4 — wares label', 'Wares', 301, 52, 22, 8, 12, 'muted', t.SANS)
t.text('S4 — commission account', 'European patrons sent\nheraldic designs to China.\nChinese artisans made\nporcelain for family identity\nand social status.', 204, 101, 119, 46, 19.5, 'ink', t.SANS, leading=25)
t.text('S4 — exhibition interpretation', 'Chinese production,\nEuropean family identity.', 204, 158, 117, 22, 20, 'deep', t.SERIF, italic=True, leading=25)
finish(4)

# 5. Bring the objects back into view, with the exhibition's argument and conceptual network.
start(5, '')
t.text('S5 — synthesis title', 'Porcelain changes meaning.', 18, 18, 305, 24, 32, 'ink', t.SERIF)
t.text('S5 — interpretive context', 'Tradition, court workshops and overseas patrons each shaped the object.', 18, 46, 305, 11, 17.5, 'muted', t.SANS)
t.picture('S5 — vase comparison', vase, 23, 66, 24, 24*730/328, crop=(253, 273, 581, 1003), outline=t.vase_outline)
t.picture('S5 — bowl comparison', bowl, 60, 82, 72, 72*832/1605, crop=(201, 808, 1806, 1640), outline=t.bowl_outline)
t.picture('S5 — plate comparison', plate, 144, 69, 51, 51, crop=(16, 16, 587, 587), ellipse=True)
t.text('S5 — tradition label', 'Tradition', 18, 128, 39, 10, 16, 'deep', t.SANS)
t.text('S5 — court label', 'Court taste', 67, 128, 68, 10, 16, 'deep', t.SANS)
t.text('S5 — market label', 'Status', 150, 128, 45, 10, 16, 'deep', t.SANS)
t.path('S5 — argument rule', [('M', 18, 147), ('L', 192, 147)], 'line', lw=.75)
t.text('S5 — exhibition claim', 'Qing makers actively shaped\ncultural exchange.', 18, 158, 177, 25, 23, 'ink', t.SERIF, leading=29)
e, b, j, g = (219, 103), (299, 76), (280, 105), (299, 137)
t.path('S5 — enamel knowledge to Beijing', [('M', 223, 101), ('C', 235, 75, 268, 72, 296, 76)], 'deep', lw=.9, dashed=True, arrow=True)
t.path('S5 — designs to Guangzhou', [('M', 223, 107), ('C', 244, 131, 272, 143, 296, 137)], 'gold', lw=.9, dashed=True, arrow=True)
t.path('S5 — finished wares to Europe', [('M', 296, 141), ('C', 256, 167, 233, 132, 221, 108)], 'river', lw=1.2, arrow=True)
t.path('S5 — bodies to Beijing', [('M', 282, 101), ('L', 297, 80)], 'deep', lw=.7, arrow=True)
t.path('S5 — wares to Guangzhou', [('M', 282, 109), ('L', 297, 133)], 'deep', lw=.7, arrow=True)
for label, point in [('Europe', e), ('Beijing', b), ('Jingdezhen', j), ('Guangzhou', g)]:
    t.rect('S5 — node ' + label, point[0] - .7, point[1] - .7, 1.4, 1.4, 'deep', ellipse=True)
t.text('S5 — Europe label', 'Europe', 204, 86, 47, 8, 13.5, 'ink', t.SANS)
t.text('S5 — Beijing label', 'Beijing', 282, 63, 41, 8, 13.5, 'ink', t.SANS)
t.text('S5 — Jingdezhen label', 'Jingdezhen', 235, 98, 40, 8, 13.5, 'ink', t.SANS, align='right')
t.text('S5 — Guangzhou label', 'Guangzhou', 273, 156, 52, 8, 13.5, 'ink', t.SANS)
t.text('S5 — network qualifier', 'Conceptual connections', 204, 172, 105, 8, 11.5, 'muted', t.SANS)
finish(5)

pres.core_properties.title = 'Porcelain in Translation — Curatorial Edit'
pres.core_properties.subject = 'Approved poster followed by four content slides; original object photographs and editable detail crops'
pres.core_properties.author = ''
pres.core_properties.keywords = 'porcelain, Qing China, cultural exchange, curatorial presentation'
file = ROOT / 'HY5305_Porcelain_in_Translation_Curatorial_Edit.pptx'
pres.save(file)
(SOURCE / 'presentation_timing.json').write_text(json.dumps({'english_words': sum(x['english_words'] for x in timing), 'target_seconds': clock, 'pace_words_per_minute': 95, 'slides': timing}, ensure_ascii=False, indent=2))
(SOURCE / 'presentation_layout_checks.json').write_text(json.dumps(t.checks, ensure_ascii=False, indent=2))
(SOURCE / 'presentation_display_text.json').write_text(json.dumps(display, ensure_ascii=False, indent=2))
bad = [x for x in t.checks if not x['fits']]
print('Created', file)
print('Slides:', len(pres.slides), 'Text-width warnings:', len(bad), 'English words:', sum(x['english_words'] for x in timing))
for x in bad:
    print(x)
