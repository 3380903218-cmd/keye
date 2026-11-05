# -*- coding: utf-8 -*-
from pathlib import Path
import sys,json
sys.path.insert(0,'/Users/arourouwed/.agents/skills/word-authoring/scripts')
import verify_office_macos as native
native.WORD=native.WORD.replace('repeat with existingDoc in documents','set existingDocs to get documents\n      repeat with existingDoc in existingDocs')
here=Path(__file__).resolve().parent
native.WORD=native.WORD.replace('set itemCount to count paragraphs of taskDoc', 'set print revisions of taskDoc to false\n      set show revisions and comments of view of active window to false\n      set show comments of view of active window to false\n      set itemCount to count paragraphs of taskDoc')
r=native.verify(here.parents[1]/'HY5419_敦煌项目_8分钟展演稿_中英对照.docx',here/'修订完成排版.pdf',here/'修订完成Word核验.json')
print(json.dumps(r,ensure_ascii=False,indent=2))
raise SystemExit(0 if r['native_open']=='passed' else 1)
