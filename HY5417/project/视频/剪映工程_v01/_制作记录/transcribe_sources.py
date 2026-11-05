from pathlib import Path
import os, json, subprocess
os.environ['HF_HUB_OFFLINE'] = '1'
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / '转写'
OUT.mkdir(exist_ok=True)
FF = '/Users/arourouwed/Desktop/codex/toolchain/native-tools/.pixi/envs/default/bin/ffmpeg'
MODEL = '/Users/arourouwed/.cache/huggingface/hub/models--mobiuslabsgmbh--faster-whisper-large-v3-turbo/snapshots/0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf'
model = WhisperModel(MODEL, device='cpu', compute_type='int8', cpu_threads=6, num_workers=1, local_files_only=True)
for number in ['01', '03', '06', '10']:
    target = OUT / f'网络{number}.json'
    if target.exists():
        print(number, 'cached', flush=True)
        continue
    source = next(ROOT.glob(f'网络_{number}_*.mp4'))
    audio = OUT / f'网络{number}.wav'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(source), '-vn', '-ar', '16000', '-ac', '1', str(audio)], check=True)
    segments, info = model.transcribe(str(audio), beam_size=3, language='en', vad_filter=True, word_timestamps=True)
    result=[]
    for seg in segments:
        row={'start':seg.start,'end':seg.end,'text':seg.text,'words':[{'start':w.start,'end':w.end,'word':w.word} for w in (seg.words or [])]}
        result.append(row)
        print(number, f'{seg.start:.2f}-{seg.end:.2f}', seg.text, flush=True)
    target.write_text(json.dumps({'source':str(source),'method':'faster-whisper large-v3-turbo, local CPU int8; machine transcript for editorial verification','segments':result},ensure_ascii=False,indent=2))
print('DONE', flush=True)
