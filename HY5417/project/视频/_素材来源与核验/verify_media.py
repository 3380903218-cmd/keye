from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess, re, json, hashlib, shutil
from PIL import Image, ImageOps, ImageDraw
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parent.parent
META=ROOT/'_素材来源与核验'
FF=imageio_ffmpeg.get_ffmpeg_exe()
PREVIEW=META/'画面预览'
PREVIEW.mkdir(exist_ok=True)

def verify(p):
 probe=subprocess.run([FF,'-hide_banner','-i',str(p)],capture_output=True,text=True)
 dm=re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)',probe.stderr)
 duration=int(dm[1])*3600+int(dm[2])*60+float(dm[3]) if dm else None
 vl=next((x.strip() for x in probe.stderr.splitlines() if 'Video:' in x),'')
 al=next((x.strip() for x in probe.stderr.splitlines() if 'Audio:' in x),'')
 wh=re.search(r'\b(\d{3,5})x(\d{3,5})\b',vl)
 fps=re.search(r'([\d.]+) fps',vl)
 decode=subprocess.run([FF,'-v','error','-threads','2','-i',str(p),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
 digest=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):digest.update(block)
 row={'file':p.name,'bytes':p.stat().st_size,'sha256':digest.hexdigest(),'duration_seconds':duration,'width':int(wh[1]) if wh else None,'height':int(wh[2]) if wh else None,'fps':float(fps[1]) if fps else None,'video_stream':vl,'audio_stream':al,'full_decode_exit_code':decode.returncode,'decode_errors':decode.stderr.strip()}
 canvas=Image.new('RGB',(1040,450),'#eeeeee');draw=ImageDraw.Draw(canvas)
 for i,frac in enumerate([0.03,0.18,0.35,0.52,0.70,0.88]):
  t=duration*frac
  temp=Path('/tmp')/(p.stem+f'-{i}.jpg')
  r=subprocess.run([FF,'-v','error','-y','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=336:-2',str(temp)],capture_output=True,text=True)
  if r.returncode==0 and temp.exists():
   im=ImageOps.contain(Image.open(temp),(336,190));x=8+(i%3)*344;y=8+(i//3)*220
   canvas.paste(im,(x,y));draw.text((x,y+193),f'{int(t)//60:02d}:{int(t)%60:02d}',fill='black')
 canvas.save(PREVIEW/(p.stem+'.jpg'))
 return row

rows=[]
with ThreadPoolExecutor(max_workers=2) as pool:
 futs={pool.submit(verify,p):p for p in sorted(ROOT.glob('网络_*.mp4'))}
 for fut in as_completed(futs):
  row=fut.result();rows.append(row)
  (META/'媒体核验.json').write_text(json.dumps(sorted(rows,key=lambda r:r['file']),ensure_ascii=False,indent=2))
  print(json.dumps({k:row[k] for k in ['file','width','height','duration_seconds','bytes','full_decode_exit_code','decode_errors']},ensure_ascii=False),flush=True)
if Path('/tmp/hy5417-existing-contact.jpg').exists():shutil.copy2('/tmp/hy5417-existing-contact.jpg',PREVIEW/'已有13段实拍_画面总览.jpg')
if Path('/tmp/hy5417-existing-inventory.json').exists():shutil.copy2('/tmp/hy5417-existing-inventory.json',META/'已有实拍文件信息.json')
print('COMPLETE',len(rows),'videos',sum(x['duration_seconds'] for x in rows),'seconds',sum(x['bytes'] for x in rows),'bytes',flush=True)
