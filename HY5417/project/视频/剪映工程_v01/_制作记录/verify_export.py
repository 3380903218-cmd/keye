from pathlib import Path
import json,subprocess,hashlib,io,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]; W=R/'_制作记录'; F='/Users/arourouwed/Desktop/codex/toolchain/native-tools/.pixi/envs/default/bin/ffmpeg'; P=F.replace('ffmpeg','ffprobe')
mov=R/'_制作记录/剪映原始导出/HY5417_Chinatown_v01_English_初剪.mov';mp4=R/'HY5417_Chinatown_v01_English_初剪.mp4'
subprocess.run([F,'-v','error','-y','-i',str(mov),'-c','copy','-movflags','+faststart',str(mp4)],check=True)
qa=W/'成片核验';qa.mkdir(exist_ok=True)
meta=json.loads(subprocess.check_output([P,'-v','error','-show_format','-show_streams','-of','json',str(mp4)]))
subprocess.run([F,'-v','info','-i',str(mp4),'-vf','blackdetect=d=0.08:pix_th=0.01:pic_th=0.99','-f','null','-'],stderr=open(qa/'decode.log','w'),stdout=subprocess.DEVNULL,check=True)
def audio(p,start=None,dur=None):
 args=[F,'-v','error']
 if start is not None:args+=['-ss',str(start)]
 args+=['-i',str(p)]
 if dur is not None:args+=['-t',str(dur)]
 args+=['-vn','-ar','16000','-ac','1','-f','f32le','-']
 return np.frombuffer(subprocess.check_output(args),dtype='<f4')
def env(x):
 x=x[:len(x)//160*160].reshape(-1,160);return np.sqrt(np.mean(x*x,axis=1))
def align(ref,export,at):
 r=env(ref[:128000]);e=env(export);scores=[]
 for shift in range(-20,21):
  st=round(at*100)+shift
  if st<0:continue
  z=e[st:st+len(r)]
  scores.append((float(np.corrcoef(r,z)[0,1]),shift/100))
 return max(scores)
a=audio(mp4);manifest=json.loads((W/'edit_manifest.json').read_text());checks=[]
for i,b in enumerate(manifest['narration'],1):
 ref=audio(b['normalized_file']);seg=a[round(b['start']*16000):round(b['start']*16000)+len(ref)];c,lag=align(ref,a,b['start'])
 checks.append({'narration':i,'envelope_correlation_first8s':c,'lag_ms':lag*1000,'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(seg**2))+1e-9))})
 assert c>.9 and abs(lag)<.09,(i,c,lag)
for r in manifest['edit']:
 if not r['original_audio']:continue
 src=manifest['source_files'][r['source']];dur=r['end']-r['start'];ss=round(r['inpoint']*25)/25
 ref=audio(src,ss,dur);z=a[round(r['start']*16000):round(r['end']*16000)];c,lag=align(ref,a,r['start'])
 checks.append({'original_sound':r['source'],'at':r['start'],'envelope_correlation':c,'lag_ms':lag*1000,'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(z**2))+1e-9))})
 assert c>.85 and abs(lag)<.09,(r,c,lag)
times=[4,21,35,57,78,96,119,140,175,188,208,230,249,268,295,306,318,336,350,377,399,418,442,480,507,525,543,560,570,580,590,598]
fnt=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23)
for batch in range(4):
 ts=times[batch*8:(batch+1)*8];im=Image.new('RGB',(1280,4*390),(35,39,39));d=ImageDraw.Draw(im)
 for i,t in enumerate(ts):
  raw=subprocess.check_output([F,'-v','error','-ss',str(t),'-i',str(mp4),'-frames:v','1','-vf','scale=640:360','-f','image2pipe','-vcodec','mjpeg','-threads','1','-']);v=Image.open(io.BytesIO(raw));x=i%2*640;y=i//2*390;im.paste(v,(x,y));d.text((x+9,y+363),f'{t//60:02}:{t%60:02}',font=fnt,fill='white')
 im.save(qa/f'frame_sheet_{batch+1}.jpg')
report={'file':str(mp4),'sha256':hashlib.sha256(mp4.read_bytes()).hexdigest(),'bytes':mp4.stat().st_size,'video':{k:meta['streams'][0].get(k) for k in ['width','height','r_frame_rate','duration','nb_frames']},'audio_peak_dbfs':float(20*np.log10(np.max(np.abs(a))+1e-9)),'full_decode':'passed','unintended_black_gaps':re.findall(r'black_start:[^\r\n]+',(qa/'decode.log').read_text()),'audio_checks':checks,'sampled_frames':times,'visual_review':'pending model inspection of four contact sheets','limitations':['No end-to-end human listening pass. Narration correlation checks establish track presence and alignment, not pronunciation quality.','Subtitles use measured sentence timing; original interview wording lightly cleaned from machine transcript and source context; human final proofread recommended.']}
(qa/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
