from pathlib import Path
import json, re, subprocess, wave, math
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(__file__).resolve().parent
FF='/Users/arourouwed/Desktop/codex/toolchain/native-tools/.pixi/envs/default/bin/ffmpeg'
VOICE='Daniel'
R=48000
blocks=json.loads((WORK/'narration.json').read_text())
cues=[]; rendered=[]
cache=WORK/'voice_cache_v2';cache.mkdir(exist_ok=True)
def run(args): subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def readwav(p):
    with wave.open(str(p),'rb') as f:return f.readframes(f.getnframes())
for i,b in enumerate(blocks,1):
    sentences=re.split(r'(?<=[.!?])\s+', b['text'])
    pieces=[]
    for j,sentence in enumerate(sentences,1):
        wav=cache/f'{i:02}_{j:02}.wav'
        if not wav.exists():
            aiff=cache/f'{i:02}_{j:02}.aiff'
            run(['/usr/bin/say','-v',VOICE,'-r','145','-o',str(aiff),sentence])
            run([FF,'-v','error','-y','-i',str(aiff),'-af','silenceremove=start_periods=1:start_duration=0.02:start_threshold=-48dB,areverse,silenceremove=start_periods=1:start_duration=0.02:start_threshold=-48dB,areverse','-ar',str(R),'-ac','1','-c:a','pcm_s16le',str(wav)])
        pieces.append((sentence,readwav(wav)))
    duration=sum(len(raw)/2/R for _,raw in pieces)
    available=b['end']-b['start']
    gap=min(0.7,max(0.25,(available-duration)/max(1,len(pieces))))
    speed=max(1.0,duration/(available-gap*len(pieces)-0.1))
    assert speed<1.28,(i,duration,available,speed)
    pcm=b'';t=0
    for j,(sentence,raw) in enumerate(pieces,1):
        if speed>1.001:
            src=cache/f'{i:02}_{j:02}.wav'; fast=cache/f'{i:02}_{j:02}_fit.wav'
            run([FF,'-v','error','-y','-i',str(src),'-af',f'atempo={speed:.6f}','-ar',str(R),'-ac','1',str(fast)])
            raw=readwav(fast)
        sec=len(raw)/2/R
        words=sentence.split(); groups=[];buf=[]
        for word in words:
            if buf and (len(' '.join(buf+[word]))>65 or len(buf)>=12):groups.append(buf);buf=[]
            buf.append(word)
        if buf:groups.append(buf)
        total=sum(max(1,len(w)) for w in words); elapsed=0
        for group in groups:
            weight=sum(max(1,len(w)) for w in group)/total
            ct=sec*weight
            cues.append({'start':round(b['start']+t+elapsed,3),'end':round(b['start']+t+elapsed+ct,3),'text':' '.join(group),'kind':'narration'})
            elapsed+=ct
        pcm+=raw+b'\0'*int(gap*R)*2;t+=sec+gap
    out=ROOT/'配音'/f'{i:02}_EN_section{b["section"]}.wav'
    with wave.open(str(out),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(R);f.writeframes(pcm)
    assert t<=available+0.05,(i,t,available)
    rendered.append({**b,'file':str(out),'duration':t,'voice':VOICE,'rate':145,'fit_speed':speed})
    print(i,len(b['text'].split()),round(duration,2),round(t,2),'/',available,'speed',round(speed,3),flush=True)
(WORK/'narration_rendered.json').write_text(json.dumps(rendered,ensure_ascii=False,indent=2))
(WORK/'narration_cues.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2))
body=['# HY5417 — English narration','', 'Temporary synthetic voice: macOS Daniel. Replaceable audio blocks; based on the approved Chinese outline.','']
for i,b in enumerate(rendered,1):body.extend([f'## {i:02} | {b["start"]:06.2f}–{b["end"]:06.2f} seconds', '', b['text'], ''])
(ROOT/'02_English_Narration.md').write_text('\n'.join(body))
print('DONE',sum(len(b['text'].split()) for b in blocks),'words',len(cues),'caption cues',flush=True)
