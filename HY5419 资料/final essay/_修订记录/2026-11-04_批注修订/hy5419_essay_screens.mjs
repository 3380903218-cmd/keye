import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob, SpreadsheetFile, Workbook} from '@oai/artifact-tool';

const out='/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/final essay/_修订记录/2026-11-04_批注修订';
const specs=JSON.parse(await fs.readFile(path.join(out,'figure-data.json'),'utf8'));
const cache=new Map();
for (const s of specs) {
  if (!cache.has(s.path)) cache.set(s.path,await SpreadsheetFile.importXlsx(await FileBlob.load(s.path)));
  const original=cache.get(s.path).worksheets.getItem(s.sheet);
  for (let r=0;r<s.cells.length;r++) for(let c=0;c<s.cells[r].length;c++) {
    const value=original.getRange(s.cells[r][c]).values[0][0];
    if ((value??null)!==(s.values[r][c]??null)) throw new Error(`Value mismatch ${s.key} ${s.cells[r][c]}`);
  }
  if(s.key==='gephi') continue;
  // Read-only presentation of selected source cells. No XLSX is exported or changed.
  const wb=Workbook.create();
  const sh=wb.worksheets.add(s.sheet);
  const end=String.fromCharCode(64+s.widths.length);
  const range=sh.getRange(`A1:${end}${s.values.length}`);
  range.values=s.values;
  range.format.font={name:'PingFang SC',size:17,color:'#1F2522'};
  range.format.wrapText=true;
  range.format.verticalAlignment='center';
  range.format.rowHeightPx=s.key==='gephi'?64:82;
  range.format.borders={preset:'all',style:'thin',color:'#D9D9D9'};
  sh.getRange(`A1:${end}1`).format={fill:'#E9ECE8',font:{name:'PingFang SC',size:15,bold:true,color:'#111111'},rowHeightPx:52,wrapText:true,verticalAlignment:'center'};
  for(let c=0;c<s.widths.length;c++) {
    const letter=String.fromCharCode(65+c);
    sh.getRange(`${letter}1:${letter}${s.values.length}`).format.columnWidthPx=s.widths[c];
  }
  for(let r=2;r<=s.values.length;r++) if (r%2===0) sh.getRange(`A${r}:${end}${r}`).format.fill='#FAFBF9';
  if(s.key==='map_places') sh.getRange('B2:C4').setNumberFormat('0.#######');
  const png=await wb.render({sheetName:s.sheet,range:`A1:${end}${s.values.length}`,scale:2,format:'png'});
  await fs.writeFile(path.join(out,s.key+'.png'),new Uint8Array(await png.arrayBuffer()));
  console.log(JSON.stringify({key:s.key,verifiedCells:s.cells.flat().length,png:path.join(out,s.key+'.png')}));
}
