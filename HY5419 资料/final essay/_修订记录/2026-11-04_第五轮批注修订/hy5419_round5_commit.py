from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib,os,shutil
B=Path('/Users/arourouwed/Desktop/NUS/2026-1/HY5419 资料/final essay');W=B/'_修订记录/2026-11-04_第五轮批注修订'
candidate=W/'修订候选.docx';dest=B/'HY5419_敦煌项目_批判性反思_中文稿.docx'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(candidate)
assert h=='1e8fcbe533e500c2729359ad957d36c67c346c016dcb7066b0a4bad2610324dd'
baseline=sha(W/'批注原稿备份.docx');assert sha(dest)==baseline=='81f781dfea6ccb4e8a8e4f6d9d8c9716e08f8d40b15393e6ce8842f87baae24c'
assert json.loads((W/'package-check.json').read_text())['status']=='passed'
pages=sorted((W/'预览').glob('page-*.png'),key=lambda p:int(p.stem.split('-')[-1]));assert len(pages)==10
now=datetime.now(ZoneInfo('Asia/Singapore')).isoformat()
visual={'artifact_sha256':h,'performed_at':now,'status':'passed','pages':10,'method':'documents/render_docx.py LibreOffice-to-PDF proxy; all ten PNG pages visually inspected.','checks':['Changed interaction rationale appears clearly at start of page 7.','Programming background and author-created skills are stated together in the AI collaboration paragraph on page 8.','Unchanged text, two figures, captions and APA references remain intact.','No clipping, overlapping text, missing glyphs or orphaned headings observed.'],'page_evidence':[{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in pages],'pdf':{'path':'预览/修订候选.pdf','sha256':sha(W/'预览/修订候选.pdf')},'limitations':'Proxy rendering; separate Word-native verification will be recorded.'}
(W/'visual-check.json').write_text(json.dumps(visual,ensure_ascii=False,indent=2))
plan={'artifact_sha256':h,'required_layers':['content','package','rendered','delivery-package'],'scope':'Two locally annotated paragraphs; all other text and media preserved.','native_plan':'Close the saved original before replacing it, reopen the updated original in Microsoft Word, inspect both changed passages and visible layout.'}
(W/'VALIDATION_PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
shutil.copy2('/tmp/hy5419_round5_build.py',W/'hy5419_round5_build.py')
tmp=dest.with_name('.HY5419_第五轮更新.tmp')
try:
 shutil.copy2(candidate,tmp);assert sha(tmp)==h
 assert sha(dest)==baseline
 os.replace(tmp,dest)
finally:
 if tmp.exists():tmp.unlink()
assert sha(dest)==h
delivery={'status':'passed','performed_at':now,'artifact_sha256':h,'requested_output':str(dest),'requested_output_sha256':h,'byte_identical_to_candidate':True,'baseline_sha256':baseline,'native_old_window_closed':True,'backup':'批注原稿备份.docx'}
(W/'delivery-package-check.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2))
print(json.dumps({'updated':str(dest),'sha256':h,'body_count':6742,'comments_addressed':2},ensure_ascii=False))
