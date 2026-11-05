import fs from 'node:fs/promises';
import {resolve} from 'node:path';
import assert from 'node:assert/strict';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const work=resolve(import.meta.dirname);
const destination=resolve(work,'../../04_Excel数据');
const data=JSON.parse(await fs.readFile(resolve(work,'最终数据提取.json'),'utf8'));
const workbook=Workbook.create();
const summary=workbook.worksheets.add('00_展示数据说明');
const palette={ink:'#2C332D',sage:'#52604E',paper:'#F7F3E9',ochre:'#A34E32'};
const definitions=[
 ['01_Gephi节点','nodes','GephiNodes'],
 ['02_Gephi关系','edges','GephiEdges'],
 ['03_活动记录','events','Activities'],
 ['04_证据定位','evidence','Evidence'],
 ['05_引用文献','sources','Sources']
];
const columnName=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const sheets=[];
for(const [name,key,tableName] of definitions){
 const records=data[key];const headers=[...new Set(records.flatMap(Object.keys))];
 const numeric=new Set(['YearStart','YearEnd','Year']);
 const values=records.map(record=>headers.map(header=>{
  const value=record[header]??null;
  if(value!==null&&numeric.has(header)&&/^\d{4}$/.test(String(value)))return Number(value);
  return value;
 }));
 const sheet=workbook.worksheets.add(name);sheet.showGridLines=false;
 const last=columnName(headers.length-1),range=sheet.getRange(`A1:${last}${records.length+1}`);
 range.values=[headers,...values];range.format.font={name:'Arial',size:11,color:palette.ink};
 range.format.wrapText=true;range.format.verticalAlignment='top';range.format.rowHeight=34;
 sheet.tables.add(`A1:${last}${records.length+1}`,true,tableName);
 sheet.getRange(`A1:${last}1`).format={fill:palette.sage,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:42,wrapText:true,verticalAlignment:'center'};
 for(let c=0;c<headers.length;c++){
  const header=headers[c],letter=columnName(c);
  let width=24;
  if(/^(Id|id|Source|Target|EventId|SourceId|source)$/.test(header))width=23;
  if(/Label|Title|Author|claim|limit|Notes|note|Reference|URL/i.test(header))width=58;
  if(/^(Year|YearStart|YearEnd)$/.test(header))width=13;
  if(header==='DateText'||header==='dateEN')width=45;
  sheet.getRange(`${letter}1:${letter}${records.length+1}`).format.columnWidth=width;
  if(numeric.has(header))sheet.getRange(`${letter}2:${letter}${records.length+1}`).setNumberFormat('0');
 }
 // Fit prose rows without shrinking type or hiding evidence limits.
 for(let r=0;r<records.length;r++){
  let lines=1;
  for(let c=0;c<headers.length;c++){
   const value=String(values[r][c]??'');
   const chars=/Label|Title|Author|claim|limit|Notes|note|Reference|URL/i.test(headers[c])?40:22;
   lines=Math.max(lines,Math.ceil([...value].reduce((n,ch)=>n+(ch.charCodeAt(0)>255?1.8:1),0)/chars));
  }
  sheet.getRange(`A${r+2}:${last}${r+2}`).format.rowHeight=Math.max(34,lines*16+12);
 }
 sheet.freezePanes.freezeRows(1);sheet.freezePanes.freezeColumns(key==='edges'?3:1);
 sheets.push({name,key,rows:records.length,columns:headers.length});
}

summary.showGridLines=false;
summary.getRange('A1:B22').format={font:{name:'Arial',size:12,color:palette.ink},verticalAlignment:'center',rowHeight:34};
summary.getRange('A1:A22').format.columnWidth=36;
summary.getRange('B1:B22').format.columnWidth=105;
summary.getRange('A2').values=[['敦煌传播网络：最终展示数据']];summary.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:palette.ochre};
summary.getRange('A4:B4').values=[['项目','内容']];summary.getRange('A4:B4').format={fill:palette.sage,font:{name:'Arial',size:12,bold:true,color:'#FFFFFF'}};
summary.getRange('A5:B20').values=[
 ['整理日期','2026-11-03'],
 ['节点数',null],['关系数',null],['活动记录数',null],['证据记录数',null],['引用来源条目数',null],
 ['对应网页','https://3380903218-cmd.github.io/dunhuang-in-motion/'],
 ['对应 Gephi 文件','敦煌双层网络_最终132节点157关系.gexf'],
 ['历史范围','1900—1910年'],
 ['记录口径','48条为活动记录，部分查看记述可能重合，不代表48次独立事件。'],
 ['版本区别','原始排版工程及旧Excel为补充前版本；本表与最终网页和扩展GEXF对应。'],
 ['布局与统计','新增节点位置为暂定位置；保留原布局，不将新增节点大小解释为重算后的中心性。'],
 ['字段与导入','Id、Source、Target为文本标识；01和02工作表首行为Gephi字段名，可另存UTF-8 CSV导入。'],
 ['证据与来源','SourceIds与EvidenceIds用于回查05_引用文献及04_证据定位；保留原文页码、依据与限度。'],
 ['数据来源','最终网站的节点CSV、关系CSV、活动记录、证据定位与引用文献；未补写新的历史关系。'],
 ['网站版本',data.website_version]
];
for(let i=0;i<definitions.length;i++){
 const [sheetName,key]=definitions[i];summary.getRange(`B${i+6}`).formulas=[[`=COUNTA('${sheetName}'!A2:A${data[key].length+1})`]];
}
summary.getRange('B6:B10').setNumberFormat('0');
summary.getRange('A14:B19').format.wrapText=true;summary.getRange('A14:B19').format.rowHeight=58;
workbook.recalculate();
assert.deepEqual(summary.getRange('B6:B10').values.flat(),[132,157,48,57,21]);
const inspection=await workbook.inspect({kind:'table',range:'00_展示数据说明!A5:B10',include:'values,formulas',tableMaxRows:6,tableMaxCols:2,maxChars:1600});
await fs.writeFile(resolve(work,'Excel内容核验.ndjson'),inspection.ndjson);
await fs.mkdir(destination,{recursive:true});
const output=resolve(destination,'敦煌传播网络_最终展示数据_132节点157关系.xlsx');
await (await SpreadsheetFile.exportXlsx(workbook)).save(output);
for(const {name,key} of [{name:'00_展示数据说明',key:'summary'},...sheets]){
 const range=key==='summary'?'A2:B20':key==='evidence'?'A1:F5':key==='sources'?'A1:E5':'A1:E6';
 const preview=await workbook.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(resolve(work,`Excel预览_${key}.png`),new Uint8Array(await preview.arrayBuffer()));
}
await fs.writeFile(resolve(work,'Excel生成与核验.json'),JSON.stringify({output,engine:'@oai/artifact-tool',recalculated:true,counts:[132,157,48,57,21],source:'最终数据提取.json',sheets,visual_previews:sheets.length+1,native_excel_open:'not checked'},null,2));
console.log(JSON.stringify({output,counts:[132,157,48,57,21],previews:sheets.length+1}));
