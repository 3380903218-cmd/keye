from pathlib import Path
import json, sys, traceback, datetime
import imageio_ffmpeg
import yt_dlp

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / '_素材来源与核验'
JOBS = [
 ('01','20231130','史密斯街更新_振兴与绅士化争议','https://www.channelnewsasia.com/watch/rejuvenating-chinatowns-smith-street-video-3956886'),
 ('02','20230312','旅游复苏与商铺生存_五成租金减免','https://www.channelnewsasia.com/watch/chinatown-offers-tenants-50-rent-relief-bid-revive-tourism-hotspot-video-3341836'),
 ('03','20250518','史密斯街更新后_生意改善与租金人手挑战','https://www.channelnewsasia.com/watch/local-firms-chinatown-enjoy-40-boost-sales-after-tie-up-heritage-centre-5137971'),
 ('04','20250221','传统行业生存_跨部门保护措施','https://www.channelnewsasia.com/watch/new-inter-agency-task-force-help-heritage-trades-amid-stiff-competition-and-rising-overheads-4952401'),
 ('05','20260131','历史街区租金_官方与商家的不同诉求','https://www.channelnewsasia.com/watch/rent-growth-in-heritage-districts-tracks-central-retail-areas-say-authorities-5898331'),
 ('07','20240731','三水女工壁画_艺术家与历史再现','https://cnalifestyle.channelnewsasia.com/watch/samsui-woman-mural-artist-sean-dunston-394246'),
 ('08','20250513','原貌与展示_牛车水原貌馆重新开放','https://www.channelnewsasia.com/watch/chinatown-heritage-centre-reopens-hopes-increase-number-visitors-up-30-5127276'),
 ('09','20250108','节庆文化的呈现_农历新年灯饰与市集','https://www.channelnewsasia.com/watch/chinatown-light-up-marks-start-chinese-new-year-festivities-4845991'),
]
results=[]
for n,date,label,url in JOBS:
 stem=f'网络_{n}_{date}_{label}'
 print(f'START {stem}',flush=True)
 opts={
  'outtmpl':str(ROOT/(stem+'.%(ext)s')),
  'format':'best[ext=mp4][protocol=https][height<=1080]/best[ext=mp4][protocol=http][height<=1080]/bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
  'merge_output_format':'mp4','ffmpeg_location':imageio_ffmpeg.get_ffmpeg_exe(),
  'noplaylist':True,'quiet':True,'noprogress':True,'no_warnings':True,'retries':3,'socket_timeout':30,
  'writesubtitles':True,'subtitleslangs':['en.*','zh.*'],'subtitlesformat':'srt/vtt/best',
 }
 try:
  with yt_dlp.YoutubeDL(opts) as ydl:
   info=ydl.extract_info(url,download=True)
   clean=ydl.sanitize_info(info)
  (META/(stem+'.info.json')).write_text(json.dumps(clean,ensure_ascii=False,indent=2))
  row={k:info.get(k) for k in ['id','title','duration','upload_date','timestamp','description','width','height','vcodec','acodec','fps','format_id','extractor','uploader']}
  row.update({'number':n,'source_url':url,'file_stem':stem,'status':'downloaded','files':[x.name for x in ROOT.glob(stem+'*')]})
  print('DONE '+json.dumps(row,ensure_ascii=False),flush=True)
 except Exception as e:
  row={'number':n,'source_url':url,'file_stem':stem,'status':'failed','error':str(e)}
  print('FAIL '+json.dumps(row,ensure_ascii=False),flush=True)
 results.append(row)
 (META/'download_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
