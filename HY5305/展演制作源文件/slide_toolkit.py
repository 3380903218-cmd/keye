from pathlib import Path
from zipfile import ZipFile
import json, base64, math, hashlib, html, random
from datetime import datetime
from lxml import etree
from PIL import Image, ImageFont
from pptx import Presentation
from pptx.util import Mm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(__file__).resolve().parent
OUT = ROOT
OUT.mkdir(exist_ok=True)
W,H = 338.6666666667,190.5
# One continuous warm-paper field; warm charcoal typography and quiet taupe lines.
# Saturated reds, greens and gilding belong to the original objects themselves.
C = {'paper':'F0E8D7','ink':'262721','muted':'746B5E','grain':'DFD3B9','river':'874839','wash':'985540','rivergrain':'A56851','deep':'683D32','gold':'C3A36B','ivory':'F8EEDB','line':'D2C3A6'}
SERIF='Didot'
SANS='Avenir Next'
DISPLAY='Avenir Next Condensed'
CHINESE='Songti SC'
POINT_MM=25.4/72
prs = Presentation()
prs.slide_width,prs.slide_height=Mm(W),Mm(H)
slide=prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid()
slide.background.fill.fore_color.rgb=RGBColor.from_string(C['paper'])
svg=[]
svg_defs=[]
checks=[]
ornament_checks=[]

def esc(s): return html.escape(str(s),quote=True)
def rgb(c): return RGBColor.from_string(C.get(c,c))
def hexcol(c): return '#'+C.get(c,c)
def name(sh,n): sh.name=n; return sh

FONTFILE={SERIF:'/System/Library/Fonts/Supplemental/Didot.ttc',SANS:'/System/Library/Fonts/Avenir Next.ttc',DISPLAY:'/System/Library/Fonts/Avenir Next Condensed.ttc',CHINESE:'/System/Library/Fonts/Supplemental/Songti.ttc'}
def getfont(face,size,bold=False,italic=False):
    path=FONTFILE[face]
    idx=(2 if bold else 1 if italic else 0) if face==SERIF else 0
    if face==SANS:
        for i in range(16):
            try:
                f=ImageFont.truetype(path,100,index=i)
                if f.getname()[1]==('Demi Bold' if bold else 'Regular'):idx=i;break
            except OSError:break
    if face==DISPLAY:
        style=('Bold Italic' if italic else 'Bold') if bold else ('Italic' if italic else 'Regular')
        for i in range(16):
            try:
                f=ImageFont.truetype(path,100,index=i)
                if f.getname()[1]==style:idx=i;break
            except OSError:break
    if face==CHINESE:
        for i in range(16):
            try:
                f=ImageFont.truetype(path,100,index=i)
                if f.getname()[0]=='Songti SC' and f.getname()[1]=='Regular':idx=i;break
            except OSError:break
    return ImageFont.truetype(path,int(round(size*10)),index=idx)

def text(label,txt,x,y,w,h,size=22,color='ink',font=SANS,bold=False,italic=False,leading=None,align='left',spacing=0,url=None):
    sh=name(slide.shapes.add_textbox(Mm(x),Mm(y),Mm(w),Mm(h)),label)
    tf=sh.text_frame
    tf.clear();tf.word_wrap=False
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    tf.vertical_anchor=MSO_ANCHOR.TOP
    lines=txt.split('\n')
    leading=leading or size*1.24
    f=getfont(font,size,bold,italic)
    for i,line in enumerate(lines):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment={'left':PP_ALIGN.LEFT,'right':PP_ALIGN.RIGHT,'center':PP_ALIGN.CENTER}[align]
        p.space_before=p.space_after=Pt(0)
        p.line_spacing=Pt(leading)
        r=p.add_run();r.text=line
        r.font.name=font;r.font.size=Pt(size);r.font.bold=bold;r.font.italic=italic;r.font.color.rgb=rgb(color)
        rp=r._r.get_or_add_rPr()
        if spacing:rp.set('spc',str(round(spacing*100)))
        for t in ['a:ea','a:cs']:
            el=OxmlElement(t);el.set('typeface',font);rp.append(el)
        if url:r.hyperlink.address=url
        width=(f.getlength(line)/10+max(len(line)-1,0)*spacing)*POINT_MM
        checks.append({'shape':label,'line':line,'width_mm':round(width,2),'available_mm':w,'fits':width<=w+0.3})
    anchor={'left':'start','right':'end','center':'middle'}[align]
    xx=x if align=='left' else x+w if align=='right' else x+w/2
    weight=(700 if font==DISPLAY else 600) if bold else 400
    s=f'<text x="{xx}" y="{y}" font-family="{esc(font)}" font-size="{size*POINT_MM:.4f}" fill="{hexcol(color)}" font-weight="{weight}" font-style="'+('italic' if italic else 'normal')+f'" text-anchor="{anchor}" letter-spacing="{spacing*POINT_MM:.4f}">'
    for i,line in enumerate(lines):
        s+=f'<tspan x="{xx}" y="{y+(size*.82+i*leading)*POINT_MM:.4f}">{esc(line)}</tspan>'
    s+='</text>'
    if url:s=f'<a href="{esc(url)}">{s}</a>'
    svg.append(s)
    return sh

# -------------------- Exhibition design / porcelain in translation --------------------

def rect(label,x,y,w,h,fill,line=None,lw=.6,ellipse=False):
    sh=name(slide.shapes.add_shape(MSO_SHAPE.OVAL if ellipse else MSO_SHAPE.RECTANGLE,Mm(x),Mm(y),Mm(w),Mm(h)),label)
    if fill:sh.fill.solid();sh.fill.fore_color.rgb=rgb(fill)
    else:sh.fill.background()
    if line:sh.line.color.rgb=rgb(line);sh.line.width=Pt(lw)
    else:sh.line.fill.background()
    if ellipse:svg.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{hexcol(fill) if fill else "none"}" stroke="{hexcol(line) if line else "none"}" stroke-width="{lw*POINT_MM}"/>')
    else:svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hexcol(fill) if fill else "none"}" stroke="{hexcol(line) if line else "none"}" stroke-width="{lw*POINT_MM}"/>')
    return sh

def path(label,commands,stroke=None,fill=None,lw=1,dashed=False,arrow=False):
    # Tight shape bounds keep every line and path easy to select in PowerPoint.
    xs=[c[k] for c in commands for k in range(1,len(c),2)]
    ys=[c[k] for c in commands for k in range(2,len(c),2)]
    xmin,ymin=min(xs),min(ys)
    dx,dy=max(max(xs)-xmin,.01),max(max(ys)-ymin,.01)
    builder=slide.shapes.build_freeform(0,0,scale=Mm(1)/1000)
    builder.move_to(round(commands[0][1]*1000),round(commands[0][2]*1000))
    builder.add_line_segments([(round(commands[0][1]*1000),round(commands[0][2]*1000))],close=False)
    sh=name(builder.convert_to_shape(),label)
    sh.left=Mm(xmin);sh.top=Mm(ymin);sh.width=Mm(dx);sh.height=Mm(dy)
    cg=sh._element.spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}custGeom')
    cg.clear()
    for tag in ['a:avLst','a:gdLst','a:ahLst','a:cxnLst']:
        cg.append(OxmlElement(tag))
    rr=OxmlElement('a:rect');rr.set('l','0');rr.set('t','0');rr.set('r','r');rr.set('b','b');cg.append(rr)
    pl=OxmlElement('a:pathLst');pp=OxmlElement('a:path');pp.set('w',str(round(dx*1000)));pp.set('h',str(round(dy*1000)))
    pp.set('fill','norm' if fill else 'none')
    for cmd in commands:
        tags={'M':'a:moveTo','L':'a:lnTo','C':'a:cubicBezTo','Q':'a:quadBezTo','Z':'a:close'}
        el=OxmlElement(tags[cmd[0]])
        for k in range(1,len(cmd),2):
            pt=OxmlElement('a:pt');pt.set('x',str(round((cmd[k]-xmin)*1000)));pt.set('y',str(round((cmd[k+1]-ymin)*1000)));el.append(pt)
        pp.append(el)
    pl.append(pp);cg.append(pl)
    if fill:sh.fill.solid();sh.fill.fore_color.rgb=rgb(fill)
    else:sh.fill.background()
    if stroke:
        sh.line.color.rgb=rgb(stroke);sh.line.width=Pt(lw)
        if dashed:
            el=OxmlElement('a:prstDash');el.set('val','dash');sh.line._get_or_add_ln().append(el)
        if arrow:
            el=OxmlElement('a:tailEnd');el.set('type','triangle');el.set('w','sm');el.set('len','sm');sh.line._get_or_add_ln().append(el)
    else:sh.line.fill.background()
    d=' '.join(c[0]+' '+ ' '.join(str(v) for v in c[1:]) for c in commands)
    if arrow:
        idd='arrow'+(C.get(stroke,stroke))
        if idd not in ''.join(svg_defs):svg_defs.append(f'<marker id="{idd}" markerWidth="7" markerHeight="7" refX="5.5" refY="3.5" orient="auto" markerUnits="strokeWidth"><path d="M 0 0 L 7 3.5 L 0 7 z" fill="{hexcol(stroke)}"/></marker>')
    svg.append(f'<path d="{d}" fill="{hexcol(fill) if fill else "none"}" stroke="{hexcol(stroke) if stroke else "none"}" stroke-width="{lw*POINT_MM}" stroke-linejoin="round" stroke-linecap="round"'+(' stroke-dasharray="2.3 1.7"' if dashed else '')+(f' marker-end="url(#{idd})"' if arrow else '')+'/>')
    return sh

def picture(label,file,x,y,w,h,crop=None,outline=None,ellipse=False):
    # Original photo pixels are retained. PowerPoint crops use editable geometry.
    sh=name(slide.shapes.add_picture(str(file),Mm(x),Mm(y),Mm(w),Mm(h)),label)
    photo=Image.open(file)
    iw,ih=photo.size
    mime=Image.MIME.get(photo.format,'image/png')
    if crop:
        l,t,r,b=crop
        sh.crop_left=l/iw;sh.crop_right=(iw-r)/iw;sh.crop_top=t/ih;sh.crop_bottom=(ih-b)/ih
    else:l,t,r,b=0,0,iw,ih
    if ellipse:
        sp=sh._element.spPr
        old=sp.find('{http://schemas.openxmlformats.org/drawingml/2006/main}prstGeom');old.set('prst','ellipse')
    if outline:
        sp=sh._element.spPr
        old=sp.find('{http://schemas.openxmlformats.org/drawingml/2006/main}prstGeom');sp.remove(old)
        cg=OxmlElement('a:custGeom')
        for tag in ['a:avLst','a:gdLst','a:ahLst','a:cxnLst']:cg.append(OxmlElement(tag))
        rr=OxmlElement('a:rect');rr.set('l','0');rr.set('t','0');rr.set('r','r');rr.set('b','b');cg.append(rr)
        pl=OxmlElement('a:pathLst');pp=OxmlElement('a:path');pp.set('w',str(round(r-l)));pp.set('h',str(round(b-t)))
        for c in outline:
            el=OxmlElement({'M':'a:moveTo','L':'a:lnTo','C':'a:cubicBezTo','Z':'a:close'}[c[0]])
            for k in range(1,len(c),2):
                pt=OxmlElement('a:pt');pt.set('x',str(round(c[k]-l)));pt.set('y',str(round(c[k+1]-t)));el.append(pt)
            pp.append(el)
        pl.append(pp);cg.append(pl);sp.insert(1,cg)
    # Matching SVG image with vector clipping, original image embedded.
    imgdata=base64.b64encode(file.read_bytes()).decode()
    sx,sy=w/(r-l),h/(b-t)
    clid='clip'+str(len(svg_defs))
    if outline:
        dd=[]
        for c in outline:
            dd.append(c[0]+' '+' '.join(f'{x+(c[k]-l)*sx:.4f} {y+(c[k+1]-t)*sy:.4f}' for k in range(1,len(c),2)))
        clip=f'<path d="{" ".join(dd)}"/>'
    elif ellipse:clip=f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}"/>'
    else:clip=f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>'
    svg_defs.append(f'<clipPath id="{clid}">{clip}</clipPath>')
    svg.append(f'<image href="data:{mime};base64,{imgdata}" x="{x-l*sx:.4f}" y="{y-t*sy:.4f}" width="{iw*sx:.4f}" height="{ih*sy:.4f}" preserveAspectRatio="none" clip-path="url(#{clid})"/>')
    return sh


vase_outline=[('M', 322, 282), ('C', 348, 274, 491, 274, 512, 282), ('C', 510, 287, 502, 289, 498, 290), ('C', 490, 313, 485, 354, 486, 390), ('C', 486, 417, 491, 437, 506, 446), ('C', 529, 453, 551, 469, 562, 491), ('C', 575, 518, 577, 550, 570, 583), ('C', 566, 628, 547, 690, 532, 739), ('C', 516, 790, 505, 822, 505, 861), ('C', 504, 901, 509, 924, 524, 941), ('C', 531, 951, 529, 963, 516, 974), ('C', 479, 1001, 353, 1000, 313, 976), ('C', 303, 969, 299, 954, 304, 941), ('C', 317, 920, 325, 904, 327, 881), ('C', 331, 847, 327, 814, 317, 780), ('C', 307, 746, 288, 703, 277, 665), ('C', 262, 621, 250, 570, 254, 531), ('C', 257, 495, 273, 468, 298, 457), ('C', 317, 449, 330, 444, 338, 424), ('C', 347, 401, 346, 349, 336, 311), ('C', 332, 299, 327, 288, 322, 285), ('Z',)]
bowl_outline=[('M', 207, 825), ('C', 205, 815, 210, 816, 236, 816), ('C', 682, 809, 1308, 809, 1765, 817), ('C', 1800, 818, 1805, 828, 1780, 842), ('C', 1748, 859, 1741, 878, 1735, 905), ('C', 1702, 1032, 1649, 1244, 1525, 1372), ('C', 1463, 1444, 1352, 1509, 1298, 1530), ('C', 1292, 1550, 1295, 1580, 1289, 1611), ('C', 1281, 1636, 751, 1638, 703, 1619), ('C', 690, 1616, 693, 1595, 694, 1578), ('C', 696, 1551, 696, 1539, 684, 1530), ('C', 574, 1490, 463, 1398, 389, 1276), ('C', 301, 1135, 262, 988, 238, 886), ('C', 230, 861, 218, 842, 207, 825), ('Z',)]
