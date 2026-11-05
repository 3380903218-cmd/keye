#!/usr/bin/env python3
"""Render the documented structure preview and optional Markdown HTML manual."""
from pathlib import Path
import csv, html, json, math
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
def read(f):
    with (ROOT/f).open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
nodes=read('nodes.csv');edges=read('edges.csv');report=json.loads((ROOT/'validation_report.json').read_text())
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
svg=ET.Element(f'{{{NS}}}svg',width='1500',height='1100',viewBox='0 0 1500 1100',role='img')
ET.SubElement(svg,f'{{{NS}}}title').text='敦煌项目进展网络的结构预览'
ET.SubElement(svg,f'{{{NS}}}desc').text='根据同包CSV生成；8个主体、6条关系，关联9个事件。北京接收端因前段交接证据缺口而断开。不是Gephi界面导出。'
def el(tag,**kw):return ET.SubElement(svg,f'{{{NS}}}{tag}',{k.replace('_','-'):str(v) for k,v in kw.items()})
def text(x,y,t,size=20,fill='#213547',anchor='start',weight='400'):
    e=el('text',x=x,y=y,font_size=size,fill=fill,text_anchor=anchor,font_weight=weight,
         font_family='PingFang SC,Microsoft YaHei,Arial,sans-serif');e.text=t;return e
el('rect',x=0,y=0,width=1500,height=1100,fill='#f8fafb')
text(80,67,'HY5419 敦煌项目 · 进展网络',32,weight='600')
text(80,107,f"1900–1910 · {report['main_nodes']}个主体 · {report['main_links']}条聚合关系 · {report['recorded_transfer_events']}个记录事件",22)
text(80,141,'同包CSV生成的结构预览；布局不表示地理距离',17,fill='#617180')
defs=el('defs');marker=ET.SubElement(defs,f'{{{NS}}}marker',id='arrow',viewBox='0 0 10 10',refX='9',refY='5',markerWidth='7',markerHeight='7',orient='auto-start-reverse')
ET.SubElement(marker,f'{{{NS}}}path',d='M 0 0 L 10 5 L 0 10 z',fill='#596c7b')
positions={'N002':(220,340),'N006':(650,240),'N007':(1120,240),'N013':(650,465),
           'N014':(1120,465),'N010':(220,785),'N011':(650,785),'N009':(1120,785)}
colors={'Person':'#d55e00','Expedition':'#0072b2','Institution':'#009e73','Government':'#755399'}
for e in edges:
    (x1,y1),(x2,y2)=positions[e['Source']],positions[e['Target']]
    dx,dy=x2-x1,y2-y1
    t=1/max(abs(dx)/135,abs(dy)/47)
    el('line',x1=x1+t*dx,y1=y1+t*dy,x2=x2-t*dx-5,y2=y2-t*dy,
       stroke='#596c7b',stroke_width=2.5,marker_end='url(#arrow)')
    cx,cy=(x1+x2)/2,(y1+y2)/2
    text(cx,cy-15,f"{e['EventCount']}个记录事件",18,anchor='middle')
    ids=e['EventIds'].split(';')
    label=f'{ids[0]}–{ids[-1]}' if len(ids)>2 else ' / '.join(ids)
    text(cx,cy+34,label,14,fill='#617180',anchor='middle')
for n in nodes:
    x,y=positions[n['Id']]
    el('rect',x=x-135,y=y-47,width=270,height=94,rx=15,fill='white',stroke=colors[n['NodeType']],stroke_width=3)
    text(x,y-8,n['Label'],24,anchor='middle',weight='500')
    text(x,y+22,n['LabelEN'],14,anchor='middle',fill='#617180')
text(1400,236,'斯坦因',20,anchor='end',fill='#0072b2')
text(1400,461,'伯希和',20,anchor='end',fill='#0072b2')
text(80,619,'北京路线前段交接尚缺证据',23,fill='#755399',weight='500')
text(80,654,'未补画王圆箓与清方之间的推测交接；图中断开不表示历史上没有联系。',19,fill='#617180')
text(1400,781,'北京',20,anchor='end',fill='#755399')
legend=[('人物','#d55e00'),('考察队','#0072b2'),('收藏机构','#009e73'),('政府机构','#755399')]
for j,(label,c) in enumerate(legend):
    el('rect',x=80+j*230,y=934,width=22,height=22,rx=4,fill=c)
    text(114+j*230,953,label,19)
text(80,1011,'箭头表示有来源的取得、实物存放或机构接收；边等权，数量单位不作为边权。',18)
text(80,1047,'来源定位与限制见 events.csv、event_evidence.csv；数据版本 2026-10-13-v1。',17,fill='#617180')
ET.ElementTree(svg).write(ROOT/'进展gephi数据集_结构预览.svg',encoding='utf-8',xml_declaration=True)

manual=(ROOT/'使用说明.md').read_text(encoding='utf8')
dictionary=(ROOT/'数据字典.md').read_text(encoding='utf8')
try:
    import markdown
    md=lambda s:markdown.markdown(s,extensions=['tables','fenced_code'])
    parser='Python Markdown'
except ImportError:
    md=lambda s:'<pre class="plain">'+html.escape(s)+'</pre>'
    parser='standard-library plain-text fallback (install markdown for formatted HTML)'
css='''body{margin:0;background:#f4f6f8;color:#203040;font:17px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC",Arial,sans-serif}main{max-width:1080px;margin:32px auto;padding:36px 48px;background:white;border-radius:14px}h1{font-size:32px}h2{font-size:24px;margin-top:44px;border-top:1px solid #e0e6eb;padding-top:20px}h3{font-size:21px}a{color:#006bac}code{font:14px/1.6 Menlo,monospace;background:#eef2f5;padding:2px 5px}pre{padding:18px;background:#eef2f5;overflow:auto}pre code{padding:0}table{border-collapse:collapse;width:100%;font-size:15px}td,th{padding:10px 12px;border:1px solid #dce3e9;text-align:left;vertical-align:top}th{background:#edf3f7}blockquote{border-left:4px solid #0072b2;margin:18px 0;padding:8px 20px;background:#f3f8fb}img{width:100%;height:auto}.plain{white-space:pre-wrap}nav{font-size:15px}footer{font-size:14px;color:#617180}@media(max-width:720px){main{margin:0;padding:22px}table{display:block;overflow:auto}}'''
body=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HY5419 · 进展gephi数据集使用说明</title><style>{css}</style><main><nav><a href="进展gephi数据集.gexf">主网络GEXF</a> · <a href="使用说明.md">Markdown说明</a> · <a href="#dictionary">数据字典</a></nav><img src="进展gephi数据集_结构预览.svg" alt="八主体六关系九事件的结构预览">{md(manual)}<section id="dictionary">{md(dictionary)}</section><footer>本页离线可读，不使用外部脚本。渲染器：{html.escape(parser)}。预览来自同包CSV，不是Gephi界面导出。</footer></main></html>'''
(ROOT/'使用说明.html').write_text(body,encoding='utf8')
print('Rendered usage HTML and structure SVG:',parser)
