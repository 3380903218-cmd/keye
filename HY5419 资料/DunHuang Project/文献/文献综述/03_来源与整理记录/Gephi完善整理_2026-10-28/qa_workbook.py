# -*- coding: utf-8 -*-
"""Read-only saved-file audit, HTML layout preview, and target-only Excel open."""
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import hashlib, html, json, subprocess, sys, re

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parents[1]/'Gephi完善_文献证据与数据工作表.xlsx'
PREVIEW=ROOT/'排版预览'
PREVIEW.mkdir(exist_ok=True)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
wb=load_workbook(OUT,data_only=False)
issues=[];links=0
for ws in wb:
    for row in ws:
        for c in row:
            if isinstance(c.value,str) and '/Users/' in c.value:issues.append([ws.title,c.coordinate,'absolute path in visible text'])
            if c.hyperlink and c.hyperlink.target:
                target=c.hyperlink.target;links+=1
                if target.startswith('#'):
                    name=target.split("'")[1]
                    if name not in wb.sheetnames:issues.append([ws.title,c.coordinate,'invalid internal link'])
                elif not re.match(r'https?://',target) and not (OUT.parent/target).is_file():
                    issues.append([ws.title,c.coordinate,'missing local hyperlink',target])
assert not issues,issues
manifest=[]
for number,ws in enumerate(wb):
    if ws.sheet_state!='visible':continue
    widths=[round(ws.column_dimensions[get_column_letter(j)].width*7+5) for j in range(1,ws.max_column+1)]
    merges={(m.min_row,m.min_col):m for m in ws.merged_cells.ranges}
    skipped={(r,c) for m in ws.merged_cells.ranges for r in range(m.min_row,m.max_row+1) for c in range(m.min_col,m.max_col+1) if (r,c)!=(m.min_row,m.min_col)}
    parts=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>'+html.escape(ws.title)+'</title>',
           '<style>*{box-sizing:border-box}body{margin:0;padding:16px;background:#e5e9e4}table{border-collapse:collapse;table-layout:fixed;background:white}td{padding:0;border-bottom:1px solid #d8e0db;vertical-align:top}.cell{padding:5px 6px;overflow-wrap:anywhere;white-space:pre-wrap;line-height:1.3;overflow:hidden}a{color:inherit}header{height:32px;font:14px Arial;color:#245B54}.rownum{display:none}</style>',
           '<header>'+html.escape(ws.title)+' · saved XLSX preview · 100% CSS scale</header>',
           '<table style="width:'+str(sum(widths))+'px"><colgroup>']
    parts += ['<col style="width:'+str(w)+'px">' for w in widths];parts.append('</colgroup>')
    for row in ws:
        r=row[0].row;height=(ws.row_dimensions[r].height or 15)*4/3
        parts.append('<tr style="height:'+str(height)+'px" data-row="'+str(r)+'">')
        for c in row:
            if (r,c.column) in skipped:continue
            value='' if c.value is None else str(c.value)
            rgb=c.font.color.rgb if c.font.color and c.font.color.type=='rgb' else '00253F39'
            fill=c.fill.fgColor.rgb if c.fill.patternType=='solid' and c.fill.fgColor.type=='rgb' else '00FFFFFF'
            style='font-family:Arial Unicode MS,Arial,PingFang SC,sans-serif;font-size:'+str(c.font.sz*4/3)+'px;color:#'+str(rgb)[-6:]+';background:#'+str(fill)[-6:]+';'
            style+='font-weight:700;' if c.font.bold else ''
            span=merges.get((r,c.column));colspan=span.max_col-span.min_col+1 if span else 1
            parts.append('<td colspan="'+str(colspan)+'" style="'+style+'"><div class="cell" data-cell="'+c.coordinate+'" style="height:'+str(height)+'px">'+html.escape(value)+'</div></td>')
        parts.append('</tr>')
    parts.append('</table></html>')
    path=PREVIEW/('%02d.html'%number);path.write_text(''.join(parts),encoding='utf-8')
    manifest.append(dict(name=ws.title,file=path.name,rows=ws.max_row,columns=ws.max_column,width=sum(widths)))
(PREVIEW/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
report=dict(path=str(OUT),sha256=digest(OUT),hyperlinks=links,broken_links=issues,formulas=0,preview_sheets=len(manifest))
(ROOT/'链接与预览核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if '--native' in sys.argv:
    def literal(s):return '"'+s.replace('\\','\\\\').replace('"','\\"')+'"'
    script='''on normalizePath(fileName)
    if fileName starts with "/" then return fileName
    return POSIX path of (fileName as alias)
end normalizePath
tell application "Microsoft Excel"
    set priorNames to name of every workbook
    set targetPath to TARGET
    set foundWorkbook to missing value
    repeat with existingName in priorNames
        try
            set candidate to workbook (existingName as text)
            if my normalizePath(full name of candidate as text) is targetPath then
                set foundWorkbook to candidate
                exit repeat
            end if
        end try
    end repeat
    set openedHere to false
    set readOnlyConfirmed to false
    if foundWorkbook is missing value then
        set nativeFileName to (POSIX file targetPath) as text
        try
            set foundWorkbook to open workbook workbook file name nativeFileName read only true add to mru false
        on error
            open (POSIX file targetPath)
            set foundWorkbook to workbook WORKBOOKNAME
        end try
        set openedHere to true
    end if
    set readOnlyConfirmed to read only of foundWorkbook
    set workbookPath to my normalizePath(full name of foundWorkbook as text)
    set sheetCount to count of worksheets of foundWorkbook
    set firstTitle to value of range "A1" of worksheet 1 of foundWorkbook
    set nodeHeader to value of range "A1" of worksheet "06_Gephi_Nodes" of foundWorkbook
    set edgeHeader to value of range "B1" of worksheet "07_Gephi_Edges" of foundWorkbook
    if openedHere then close foundWorkbook saving no
    set afterNames to name of every workbook
    set othersPreserved to (priorNames is afterNames)
    return workbookPath & "|" & (sheetCount as text) & "|" & firstTitle & "|" & nodeHeader & "|" & edgeHeader & "|" & (openedHere as text) & "|" & (othersPreserved as text) & "|" & (readOnlyConfirmed as text)
end tell'''.replace('TARGET',literal(str(OUT))).replace('WORKBOOKNAME',literal(OUT.name))
    native=dict(status='unverified',sha256_before=digest(OUT),calculation='0 formulas; no global recalculation invoked')
    try:
        result=subprocess.run(['osascript','-e',script],capture_output=True,text=True,timeout=45)
        native.update(returncode=result.returncode,stdout=result.stdout.strip(),stderr=result.stderr.strip())
        if result.returncode==0:
            fields=result.stdout.strip().split('|')
            assert fields[0]==str(OUT) and int(fields[1])==13 and fields[3:5]==['Id','Source'],fields
            assert fields[6]=='true',fields
            native.update(status='passed',sheet_count=13,other_workbooks_preserved=True,opened_by_script=fields[5]=='true',read_only_confirmed=fields[7]=='true')
    except Exception as exc:native.update(reason=str(exc))
    native['sha256_after']=digest(OUT)
    assert native['sha256_before']==native['sha256_after']
    (ROOT/'Excel原生打开核验.json').write_text(json.dumps(native,ensure_ascii=False,indent=2),encoding='utf-8')
    report['native']=native
print(json.dumps(report,ensure_ascii=False,indent=2))
