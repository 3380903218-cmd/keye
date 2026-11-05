from pathlib import Path
import subprocess, json
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parent.parent
META=ROOT/'_素材来源与核验'
jobs=[
 ('06','20250404','白新春茶庄_活态传承与社区联系','https://www.youtube.com/watch?v=-Fa4oH-TbGA'),
 ('10','20261101','遗产企业支持_经营延续与社区活动','https://www.youtube.com/watch?v=guUSk-UD-eQ'),
]
results=[]
for num,date,label,url in jobs:
 stem=f'网络_{num}_{date}_{label}'
 args=['/tmp/hy5417-yt-dlp-macos','--no-progress','--no-warnings','--socket-timeout','30','--retries','3','--no-playlist',
 '-f','bv[ext=mp4][vcodec^=avc1][height<=1080][protocol=https]+ba[ext=m4a][protocol=https]/bv[ext=mp4][vcodec^=avc1][height<=1080]+ba[ext=m4a]/b[ext=mp4]',
 '--merge-output-format','mp4','--ffmpeg-location',imageio_ffmpeg.get_ffmpeg_exe(),
 '--write-info-json','--write-subs','--sub-langs','en,zh-Hans,zh-Hant','--no-write-auto-subs','-o',str(ROOT/(stem+'.%(ext)s')),url]
 print('START '+stem,flush=True)
 r=subprocess.run(args)
 info_path=ROOT/(stem+'.info.json')
 row={'number':num,'source_url':url,'file_stem':stem,'status':'downloaded' if r.returncode==0 else 'failed','exit_code':r.returncode}
 if info_path.exists():
  info=json.loads(info_path.read_text())
  row.update({k:info.get(k) for k in ['id','title','duration','upload_date','description','width','height','uploader','vcodec','acodec','fps','format_id','license']})
  info_path.rename(META/info_path.name)
 row['files']=[p.name for p in ROOT.glob(stem+'*')]
 results.append(row)
 (META/'youtube_download_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
 print('DONE '+json.dumps(row,ensure_ascii=False),flush=True)
