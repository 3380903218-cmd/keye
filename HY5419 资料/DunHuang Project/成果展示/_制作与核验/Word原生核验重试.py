# -*- coding: utf-8 -*-
import sys,json
from pathlib import Path
skill=Path('/Users/arourouwed/.agents/skills/word-authoring/scripts')
sys.path.insert(0,str(skill))
import verify_office_macos as native
# Materialise the document list before iterating; leave all original safety checks intact.
native.WORD=native.WORD.replace('repeat with existingDoc in documents','set existingDocs to get documents\n      repeat with existingDoc in existingDocs')
here=Path(__file__).resolve().parent
r=native.verify(here.parent/'HY5419_敦煌项目_8分钟展演稿_中英对照.docx',here/'Word排版核验.pdf',here/'Word原生核验_重试.json')
print(json.dumps(r,ensure_ascii=False,indent=2))
raise SystemExit(0 if r['native_open']=='passed' else 1)
