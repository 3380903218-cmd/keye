from pathlib import Path
import subprocess,io
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/'候选画面'; OUT.mkdir(exist_ok=True)
ff='/Users/arourouwed/Desktop/codex/toolchain/native-tools/.pixi/envs/default/bin/ffmpeg'
f=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',21)
sets={'01':[20,35,55,80,98,111,137], '03':[15,30,50,59,82,104,130,160,180], '06':[40,49,90,115,145,170,195,220,245,275,300], '08':[24,44,68,92,112], '09':[22,38,65,100,145,170], '10':[26,45,52,61,70,78,84]}
for n,times in sets.items():
 fn=next(ROOT.glob(f'网络_{n}_*.mp4'))
 canvas=Image.new('RGB',(1200, (len(times)+2)//3*265),(22,25,25)); d=ImageDraw.Draw(canvas)
 for i,t in enumerate(times):
  raw=subprocess.check_output([ff,'-v','error','-ss',str(t),'-i',str(fn),'-frames:v','1','-vf','scale=400:225','-f','image2pipe','-vcodec','mjpeg','-threads','1','-'])
  im=Image.open(io.BytesIO(raw)); x=i%3*400;y=i//3*265
  canvas.paste(im,(x,y));d.text((x+8,y+231),f'N{n}  {t}s',font=f,fill='white')
 canvas.save(OUT/f'N{n}.jpg')
print(OUT)
