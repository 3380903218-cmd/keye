from __future__ import annotations

import argparse
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
DEFAULT_SCRIPT_PATH = ROOT / "第二周" / "ES5000_Oral_Presentation_Script.md"
DEFAULT_PPTX_PATH = ROOT / "第二周" / "ES5000_Oral_Presentation_Slides.pptx"

NAVY = RGBColor(11, 31, 58)
BLUE = RGBColor(30, 90, 168)
CYAN = RGBColor(54, 185, 209)
GOLD = RGBColor(241, 178, 74)
INK = RGBColor(27, 39, 56)
MUTED = RGBColor(91, 102, 117)
PALE = RGBColor(235, 242, 250)
BG = RGBColor(247, 249, 252)
WHITE = RGBColor(255, 255, 255)
LIGHT_BLUE = RGBColor(222, 234, 248)


def rgb(hex_value: str) -> RGBColor:
    hex_value = hex_value.lstrip("#")
    return RGBColor(int(hex_value[0:2], 16), int(hex_value[2:4], 16), int(hex_value[4:6], 16))


def set_bg(slide, color: RGBColor) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_shape(slide, kind, x, y, w, h, fill=WHITE, line=None, radius=False):
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line if line is not None else fill
    if line is None:
        shape.line.fill.background()
    return shape


def add_text(
    slide,
    text,
    x,
    y,
    w,
    h,
    size=20,
    color=INK,
    bold=False,
    font="Arial",
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP,
    margin=0.05,
    italic=False,
    fit=False,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.space_after = Pt(0)
    p.line_spacing = 1.05
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    if fit:
        # Keep text large and readable; this only activates for unusually long source blocks.
        tf.fit_text(font_family=font, max_size=Pt(size), bold=bold)
    return box


def add_rich_lines(slide, lines, x, y, w, h, size=18, color=INK, bullet_color=BLUE, line_gap=0.12):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    for idx, line in enumerate(lines):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(line_gap * 72)
        p.line_spacing = 1.05
        p.text = "• " + line
        for run in p.runs:
            run.font.name = "Arial"
            run.font.size = Pt(size)
            run.font.color.rgb = color
    return box


def add_title(slide, title, kicker=None, dark=False, number=None):
    color = WHITE if dark else NAVY
    if kicker:
        add_text(slide, kicker.upper(), 0.62, 0.35, 4.7, 0.28, size=11, color=CYAN if dark else BLUE, bold=True)
    add_text(slide, title, 0.60, 0.63, 11.8, 0.62, size=31, color=color, bold=True)
    add_shape(slide, MSO_SHAPE.RECTANGLE, 0.62, 1.40, 1.05, 0.06, fill=GOLD)
    if number is not None:
        add_text(slide, f"{number:02d}", 12.25, 0.42, 0.45, 0.30, size=12, color=CYAN if dark else BLUE, bold=True, align=PP_ALIGN.RIGHT)


def add_footer(slide, text="ES5000 Oral Presentation · Xiwen Wang"):
    add_text(slide, text, 0.62, 7.12, 8.5, 0.18, size=9, color=MUTED)


def add_node(slide, label, x, y, w, h, fill, text_color=WHITE, size=16, line=None):
    node = add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, line=line)
    add_text(slide, label, x + 0.10, y + 0.08, w - 0.20, h - 0.16, size=size, color=text_color, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    return node


def add_arrow(slide, x1, y1, x2, y2, color=BLUE, width=2.2):
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    line.line.color.rgb = color
    line.line.width = Pt(width)
    line.line.end_arrowhead = True
    return line


def make_script() -> str:
    body = """# ES5000 Graduate English I – Oral Presentation

**Name:** Xiwen Wang  
**Tutorial group:** [Tutorial Group]  
**Date:** [Date]  
**Target length:** 4 minutes 35-50 seconds (W=619 spoken words; headings and declaration excluded)

## Title: Places, Pictures, and Stories

### Slide 1 · Opening (about 35 seconds)

Good morning, everyone. My name is Xiwen Wang, and I come from Tianjin, China. Before coming to NUS, I studied in Beijing. If I had to introduce myself in three words, I would choose places, pictures, and stories. Places represent my love of travel, pictures represent my interest in painting, and stories connect these hobbies with the history I study. Today I would like to share these three parts of my life. [Pause]

### Slide 2 · My background (about 40 seconds)

First, a little about where I come from. Tianjin is my hometown, Beijing is where I completed my undergraduate studies, and Singapore is the newest stop in my journey. At the University of Science and Technology Beijing, I studied Public Administration and International Economics and Trade. The names sound serious, but the most useful lesson was simple: people can look at the same issue from very different angles. Moving between cities and subjects made me more curious, flexible, and willing to listen. [Pause]

### Slide 3 · Why I enjoy travelling (about 55 seconds)

That curiosity is one reason I enjoy travelling. For me, travel is not only about taking a break or checking famous places off a list. I like the moment when an unfamiliar city begins to feel understandable: after I walk through its streets, notice its buildings, try local food, and watch how people use public spaces. Travel reminds me that everyday life can be organised in many different ways.

It also gives me a fresh view of home. When I return, I notice details that I used to ignore. I think travel makes me more open-minded because it asks me to observe before judging. It is also a good way to meet people and collect memories, not just photographs. [Emphasize: “observe before judging”]

### Slide 4 · Why I enjoy painting (about 50 seconds)

My second hobby is painting. Travel brings me movement, while painting gives me quiet time. When I draw or paint, I have to slow down and look carefully at colour, light, shape, and small details. I do not need every picture to be perfect. I enjoy the process of turning an idea or a scene into something visible.

Painting has taught me patience. It also helps me express feelings that are sometimes difficult to explain in words. These habits - looking carefully, staying patient, and thinking visually - also influence the way I study history. A historical image or museum object can communicate something before we read a long explanation. [Pause]

### Slide 5 · What I want to learn at NUS (about 55 seconds)

This brings me to my area of study. I chose Applied and Public History at NUS because I am interested in how people meet history outside a textbook. This can happen in a museum, an exhibition, an old building, a painting, or even a digital story. I want to learn how to make these experiences accurate, clear, and interesting for different audiences.

My hobbies make this subject feel personal. Travel makes me pay attention to places and communities. Painting makes me pay attention to images and details. Singapore is also an exciting place to study because many cultures and histories meet here. At NUS, I hope to improve both my research skills and my ability to explain ideas in everyday English. [Pause]

### Slide 6 · Future and closing (about 55 seconds)

After I complete my NUS degree, I hope to continue studying history, possibly through a PhD. At the same time, I do not want my future work to speak only to specialists. I would like to take part in museum, exhibition, heritage, or cultural projects that help more people feel connected to the past.

I also hope travel and painting will remain part of my life. They help me stay curious and balanced, and they remind me to see the world from more than one angle. So, if you remember three things about me, remember places, pictures, and stories. I enjoy discovering places, creating pictures, and sharing stories from the past. Thank you. [Smile]

## Pronunciation and delivery notes

- **heritage:** HER-i-tij; **exhibition:** ek-si-BISH-uhn.
- **perspective:** per-SPEK-tiv; **curious:** KYOOR-ee-us.
- Keep a friendly pace of about 130-135 words per minute. Smile at the opening and closing, and use a small three-part hand gesture for “places, pictures, and stories.”

## Emergency short version

If the rehearsal runs over five minutes, remove the two sentences beginning “It also gives me a fresh view of home” in Slide 3 and the sentence beginning “Singapore is also an exciting place” in Slide 5. This removes about thirty words while preserving the main structure.

## Sources used for factual claims and visuals

- `ES5000 Oral Presentation.pdf`: assignment instructions and assessment criteria.
- National University of Singapore, Department of History. *MA (Coursework) in Applied and Public History*. https://fass.nus.edu.sg/hist/maph/
- Personal background and hobbies were provided by Xiwen Wang.
- All diagrams and decorative shapes in the accompanying slides are self-created; no external image is used.

## AI Declaration (paste at the bottom of the submitted assignment)

**Draft status:** This declaration reflects the AI use in the current draft. Please review the script and slides, make your own edits, and confirm the boxes before submission.

Declaration:

I understand what plagiarism is, and I declare that I did not plagiarise any part of this assignment. I also acknowledge that I

☐ did not use any AI tools.

☒ used OpenAI Codex for this assignment
       ☒ to brainstorm ideas.
       ☒ to suggest topics, reasons and supporting points for my arguments.
       ☐ to generate some sentences that I developed into the final version.
       ☐ to generate paragraphs that I organized into the final version.
       ☒ to generate a complete draft that I edited into the final version.
       ☐ to edit/improve a draft originally written entirely by me.
       ☐ to provide comments on a draft originally written entirely by me.

**W=619 (spoken script, excluding headings, delivery notes, sources, and declaration).**
"""
    return body


def build_deck(pptx_path: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # Slide 1
    slide = prs.slides.add_slide(blank)
    set_bg(slide, NAVY)
    # Decorative field
    for x, y, d, c, alpha_note in [(9.15, -0.25, 3.2, BLUE, ""), (10.55, 1.00, 2.25, CYAN, ""), (8.55, 2.55, 1.65, GOLD, "")]:
        circ = add_shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill=c)
        circ.fill.transparency = 0.18
    add_text(slide, "ES5000 · GRADUATE ENGLISH I", 0.72, 0.72, 6.5, 0.28, size=13, color=CYAN, bold=True)
    add_text(slide, "Places, Pictures\n& Stories", 0.70, 1.55, 7.5, 1.55, size=42, color=WHITE, bold=True)
    add_text(slide, "A personal introduction", 0.74, 3.42, 6.8, 0.45, size=20, color=LIGHT_BLUE)
    add_shape(slide, MSO_SHAPE.RECTANGLE, 0.74, 4.30, 1.35, 0.07, fill=GOLD)
    add_text(slide, "Xiwen Wang", 0.74, 5.02, 3.5, 0.38, size=22, color=WHITE, bold=True)
    add_text(slide, "Tianjin · Beijing · Singapore", 0.74, 5.45, 6.7, 0.30, size=14, color=LIGHT_BLUE)
    add_text(slide, "[Tutorial Group] · [Date]", 0.74, 6.10, 3.8, 0.25, size=11, color=MUTED)
    # Three personal themes
    add_node(slide, "TRAVEL", 8.60, 4.85, 1.55, 0.82, BLUE, size=13)
    add_node(slide, "PAINTING", 10.35, 4.85, 1.55, 0.82, CYAN, size=13)
    add_node(slide, "STORIES", 9.48, 5.85, 1.55, 0.82, GOLD, text_color=NAVY, size=13)

    # Slide 2
    slide = prs.slides.add_slide(blank)
    set_bg(slide, BG)
    add_title(slide, "My Background", "01 · Past", number=2)
    add_text(slide, "Three cities in my journey", 0.65, 1.65, 5.7, 0.38, size=18, color=MUTED)
    # Route line
    add_shape(slide, MSO_SHAPE.RECTANGLE, 1.25, 2.55, 0.05, 3.25, fill=BLUE)
    route = [("TIANJIN", "my hometown", 2.45, GOLD), ("BEIJING", "undergraduate years", 3.85, BLUE), ("SINGAPORE", "my newest chapter", 5.25, CYAN)]
    for label, sub, y, color in route:
        add_shape(slide, MSO_SHAPE.OVAL, 0.99, y, 0.55, 0.55, fill=color)
        add_text(slide, label, 1.80, y - 0.03, 2.0, 0.26, size=17, color=NAVY, bold=True)
        add_text(slide, sub, 1.80, y + 0.28, 2.8, 0.24, size=12, color=MUTED)
    add_text(slide, "My undergraduate background", 5.10, 2.16, 6.90, 0.35, size=18, color=BLUE, bold=True, align=PP_ALIGN.CENTER)
    add_node(slide, "PUBLIC\nADMINISTRATION", 5.25, 2.75, 3.05, 1.20, NAVY, size=18)
    add_node(slide, "INTERNATIONAL\nECONOMICS & TRADE", 8.85, 2.75, 3.05, 1.20, BLUE, size=18)
    add_text(slide, "Different places and subjects taught me to look\nfrom more than one angle.", 5.05, 4.75, 7.10, 0.90, size=25, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "curious · flexible · willing to listen", 5.10, 5.90, 7.00, 0.30, size=16, color=MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide)

    # Slide 3
    slide = prs.slides.add_slide(blank)
    set_bg(slide, NAVY)
    add_title(slide, "Why I Love Travelling", "02 · One of my hobbies", dark=True, number=3)
    add_text(slide, "Travel helps an unfamiliar place become understandable.", 0.68, 1.66, 11.8, 0.40, size=20, color=LIGHT_BLUE)
    travel_cards = [
        ("NOTICE", "streets · buildings · food", BLUE),
        ("LISTEN", "people · everyday life", CYAN),
        ("LEARN", "new ways to see the world", GOLD),
    ]
    for idx, (head, sub, color) in enumerate(travel_cards):
        x = 0.78 + idx * 4.18
        add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, 2.42, 3.55, 2.78, fill=rgb("173A66"), line=color)
        add_shape(slide, MSO_SHAPE.OVAL, x + 1.37, 2.78, 0.82, 0.82, fill=color)
        add_text(slide, str(idx + 1), x + 1.37, 3.03, 0.82, 0.24, size=16, color=NAVY if color == GOLD else WHITE, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, head, x + 0.20, 3.95, 3.15, 0.36, size=23, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, sub, x + 0.24, 4.48, 3.07, 0.36, size=15, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)
    add_text(slide, "OBSERVE BEFORE JUDGING", 2.15, 5.84, 9.05, 0.48, size=25, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Travel brings new places, new people, and new perspectives.", 2.05, 6.40, 9.25, 0.32, size=16, color=GOLD, align=PP_ALIGN.CENTER)
    add_footer(slide, "ES5000 Oral Presentation · Xiwen Wang")

    # Slide 4
    slide = prs.slides.add_slide(blank)
    set_bg(slide, BG)
    add_title(slide, "Why I Enjoy Painting", "03 · Another hobby", number=4)
    add_text(slide, "Travel brings movement. Painting gives me quiet time.", 0.66, 1.63, 9.3, 0.36, size=19, color=MUTED)
    # A simple editable abstract canvas
    add_shape(slide, MSO_SHAPE.RECTANGLE, 0.86, 2.18, 4.78, 3.86, fill=WHITE, line=LIGHT_BLUE)
    add_shape(slide, MSO_SHAPE.RECTANGLE, 1.18, 2.55, 1.55, 2.70, fill=BLUE)
    add_shape(slide, MSO_SHAPE.RECTANGLE, 2.92, 2.55, 2.36, 1.15, fill=CYAN)
    add_shape(slide, MSO_SHAPE.RECTANGLE, 2.92, 3.88, 1.08, 1.37, fill=GOLD)
    add_shape(slide, MSO_SHAPE.OVAL, 4.25, 3.86, 1.03, 1.03, fill=NAVY)
    add_text(slide, "an idea → something visible", 1.18, 5.47, 4.10, 0.28, size=14, color=MUTED, align=PP_ALIGN.CENTER)
    add_text(slide, "Painting helps me...", 6.35, 2.20, 5.72, 0.38, size=20, color=BLUE, bold=True)
    painting_cards = [
        ("NOTICE", "colour · light · shape", BLUE),
        ("PRACTISE", "patience · attention", CYAN),
        ("EXPRESS", "feelings beyond words", GOLD),
    ]
    yy = 2.86
    for head, sub, color in painting_cards:
        add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 6.35, yy, 5.72, 0.88, fill=PALE, line=PALE)
        add_shape(slide, MSO_SHAPE.OVAL, 6.68, yy + 0.14, 0.55, 0.55, fill=color)
        add_text(slide, head, 7.52, yy + 0.13, 1.45, 0.28, size=17, color=NAVY, bold=True)
        add_text(slide, sub, 9.00, yy + 0.15, 2.74, 0.28, size=15, color=MUTED)
        yy += 1.10
    add_text(slide, "Looking carefully also shapes the way I study history.", 6.38, 6.25, 5.65, 0.42, size=20, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide)

    # Slide 5
    slide = prs.slides.add_slide(blank)
    set_bg(slide, WHITE)
    add_title(slide, "What I Want to Learn at NUS", "04 · Present", number=5)
    add_text(slide, "Applied and Public History: history beyond the textbook", 0.65, 1.62, 9.8, 0.35, size=19, color=MUTED)
    add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 0.76, 2.22, 5.78, 1.20, fill=PALE, line=PALE)
    add_text(slide, "SINGAPORE", 1.04, 2.48, 1.65, 0.28, size=17, color=BLUE, bold=True)
    add_text(slide, "many cultures and histories meet", 2.72, 2.48, 3.42, 0.30, size=16, color=NAVY)
    add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 6.80, 2.22, 5.78, 1.20, fill=PALE, line=PALE)
    add_text(slide, "NUS", 7.08, 2.48, 0.95, 0.28, size=17, color=CYAN, bold=True)
    add_text(slide, "research + public communication", 8.10, 2.48, 4.05, 0.30, size=16, color=NAVY)
    learning = [
        ("PLACES", "old buildings\nand communities", BLUE),
        ("MUSEUMS", "objects and\nexhibitions", CYAN),
        ("STORIES", "clear language for\ndifferent audiences", GOLD),
    ]
    for idx, (head, sub, color) in enumerate(learning):
        x = 0.80 + idx * 4.18
        add_node(slide, head, x, 4.05, 3.55, 0.86, color, text_color=NAVY if color == GOLD else WHITE, size=20)
        add_text(slide, sub, x + 0.20, 5.14, 3.15, 0.70, size=17, color=NAVY, align=PP_ALIGN.CENTER)
    add_text(slide, "How can history feel accurate, clear, and interesting?", 1.38, 6.26, 10.60, 0.48, size=25, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide)

    # Slide 6
    slide = prs.slides.add_slide(blank)
    set_bg(slide, NAVY)
    add_title(slide, "Where I Hope to Go", "05 · Future", dark=True, number=6)
    add_text(slide, "A future with study, public projects, and personal balance", 0.68, 1.68, 9.6, 0.35, size=18, color=LIGHT_BLUE)
    # arrows first
    add_arrow(slide, 3.58, 3.40, 4.70, 3.40, color=GOLD, width=2.8)
    add_arrow(slide, 7.58, 3.40, 8.70, 3.40, color=CYAN, width=2.8)
    add_node(slide, "NUS\nDEGREE", 0.85, 2.42, 2.75, 1.92, BLUE, size=22)
    add_text(slide, "learn · communicate", 1.05, 4.62, 2.35, 0.32, size=14, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)
    add_node(slide, "FURTHER\nSTUDY", 4.72, 2.42, 2.75, 1.92, CYAN, text_color=NAVY, size=22)
    add_text(slide, "possibly a history PhD", 4.92, 4.62, 2.35, 0.32, size=14, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)
    add_node(slide, "CULTURAL\nPROJECTS", 8.75, 2.42, 3.00, 1.92, GOLD, text_color=NAVY, size=22)
    add_text(slide, "museums · exhibitions · heritage", 8.93, 4.62, 2.65, 0.44, size=14, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)
    add_node(slide, "KEEP TRAVELLING", 0.82, 5.62, 2.70, 0.72, rgb("173A66"), size=15)
    add_node(slide, "KEEP PAINTING", 9.82, 5.62, 2.70, 0.72, rgb("173A66"), size=15)
    add_text(slide, "PLACES · PICTURES · STORIES", 3.70, 5.76, 5.95, 0.38, size=21, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Stay curious. Stay balanced. Share the past with more people.", 2.05, 6.52, 9.30, 0.34, size=17, color=GOLD, align=PP_ALIGN.CENTER)
    add_footer(slide, "ES5000 Oral Presentation · Xiwen Wang")

    # Slide 7
    slide = prs.slides.add_slide(blank)
    set_bg(slide, BG)
    add_title(slide, "Sources & Visual Notes", "Appendix · Not part of the 4-5 minute speech", number=7)
    add_text(slide, "Sources used to check the assignment and programme description", 0.67, 1.62, 11.6, 0.30, size=17, color=MUTED)
    sources = [
        ("ES5000 · Oral Presentation brief", "local course PDF · 4-5 minutes"),
        ("NUS History · MA Applied and Public History", "fass.nus.edu.sg/hist/maph/"),
        ("Personal background and hobbies", "provided by Xiwen Wang"),
    ]
    y = 2.25
    for idx, (label, url) in enumerate(sources, 1):
        add_shape(slide, MSO_SHAPE.OVAL, 0.82, y + 0.02, 0.35, 0.35, fill=BLUE if idx % 2 else CYAN)
        add_text(slide, str(idx), 0.82, y + 0.07, 0.35, 0.18, size=11, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, label, 1.38, y, 4.20, 0.25, size=15, color=NAVY, bold=True)
        add_text(slide, url, 5.62, y, 6.85, 0.30, size=12, color=BLUE)
        y += 0.92
    add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 0.80, 5.40, 11.65, 1.05, fill=PALE, line=PALE)
    add_text(slide, "Visuals: all routes, cards, abstract painting shapes, arrows, and decorative elements are self-created and editable. No external image is used.", 1.12, 5.70, 11.00, 0.45, size=16, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Checked 15 August 2026 · Personal statements and final AI declaration remain subject to student confirmation.", 0.80, 6.78, 11.70, 0.22, size=10, color=MUTED, align=PP_ALIGN.CENTER)

    # Slide 8
    slide = prs.slides.add_slide(blank)
    set_bg(slide, WHITE)
    add_title(slide, "AI Declaration", "Appendix · Not part of the 4–5 minute speech", number=8)
    add_text(slide, "Please review the draft, make your own edits, and confirm the boxes before submission.", 0.68, 1.62, 11.6, 0.30, size=15, color=MUTED)
    declaration = (
        "Declaration:\n"
        "I understand what plagiarism is, and I declare that I did not plagiarise any part of this assignment. "
        "I also acknowledge that I\n"
        "☐ did not use any AI tools.\n"
        "☒ used OpenAI Codex for this assignment\n"
        "      ☒ to brainstorm ideas.\n"
        "      ☒ to suggest topics, reasons and supporting points for my arguments.\n"
        "      ☐ to generate some sentences that I developed into the final version.\n"
        "      ☐ to generate paragraphs that I organized into the final version.\n"
        "      ☒ to generate a complete draft that I edited into the final version.\n"
        "      ☐ to edit/improve a draft originally written entirely by me.\n"
        "      ☐ to provide comments on a draft originally written entirely by me."
    )
    add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 0.72, 2.10, 11.90, 4.26, fill=BG, line=LIGHT_BLUE)
    add_text(slide, declaration, 1.00, 2.36, 11.30, 3.75, size=15, color=INK, margin=0.02)
    add_text(slide, "Current checkboxes are a draft only; confirm the tool name and actual uses before submission.", 0.80, 6.70, 11.65, 0.24, size=11, color=BLUE, italic=True, align=PP_ALIGN.CENTER)

    pptx_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(pptx_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the ES5000 personal-introduction script and editable PPTX.")
    parser.add_argument("--script-output", type=Path, default=DEFAULT_SCRIPT_PATH)
    parser.add_argument("--pptx-output", type=Path, default=DEFAULT_PPTX_PATH)
    args = parser.parse_args()

    args.script_output.parent.mkdir(parents=True, exist_ok=True)
    args.script_output.write_text(make_script(), encoding="utf-8")
    build_deck(args.pptx_output)
    print(f"wrote {args.script_output}")
    print(f"wrote {args.pptx_output}")


if __name__ == "__main__":
    main()
