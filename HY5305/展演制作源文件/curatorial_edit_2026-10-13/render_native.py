from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess, json, hashlib
import fitz

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[1]
WORK = Path('/tmp/hy5305-curatorial-work')
WORK.mkdir(exist_ok=True)
scripts = {
    'powerpoint': '''on run argv
    set sourcePath to item 1 of argv
    set outputPath to item 2 of argv
    set expectedName to item 3 of argv
    with timeout of 20 seconds
        tell application "Microsoft PowerPoint"
            open (POSIX file sourcePath)
            set p to active presentation
            if name of p is not expectedName then error "Unexpected active presentation; no export or close performed"
            save p in (POSIX file outputPath) as save as PDF
            close p saving no
        end tell
    end timeout
end run
''',
    'word': '''on run argv
    set sourcePath to item 1 of argv
    set outputPath to item 2 of argv
    with timeout of 20 seconds
        tell application "Microsoft Word"
            set d to open file name sourcePath read only true add to recent files false
            save as d file name outputPath file format format PDF add to recent files false
            close d saving no
        end tell
    end timeout
end run
''',
}


def render(app):
    file = ROOT / ('HY5305_Porcelain_in_Translation_Curatorial_Edit.pptx' if app == 'powerpoint' else 'HY5305_Porcelain_in_Translation_Curatorial_Edit_Script.docx')
    pdf = WORK / (app + '-native.pdf')
    pdf.unlink(missing_ok=True)
    script = WORK / ('render_' + app + '.applescript')
    script.write_text(scripts[app])
    sha = hashlib.sha256(file.read_bytes()).hexdigest()
    try:
        output = subprocess.run(['osascript', str(script), str(file), str(pdf), file.name], capture_output=True, text=True, timeout=27)
        status = {'returncode': output.returncode, 'stdout': output.stdout, 'stderr': output.stderr}
    except subprocess.TimeoutExpired:
        status = {'returncode': None, 'stderr': 'Task-owned osascript wrapper timed out after 27 seconds.'}
    status.update(application='Microsoft PowerPoint' if app == 'powerpoint' else 'Microsoft Word', pdf_created=pdf.exists(), source_sha256=sha, source_unchanged=hashlib.sha256(file.read_bytes()).hexdigest() == sha)
    if pdf.exists():
        with fitz.open(pdf) as document:
            status['pages'] = len(document)
            status['pdf_sha256'] = hashlib.sha256(pdf.read_bytes()).hexdigest()
            for index, page in enumerate(document, 1):
                page.get_pixmap(matrix=fitz.Matrix(1.15, 1.15), alpha=False).save(WORK / f'{app}-native-page-{index}.jpg')
    (WORK / (app + '-native-status.json')).write_text(json.dumps(status, ensure_ascii=False, indent=2))
    return app, status


with ThreadPoolExecutor(max_workers=2) as pool:
    for app, status in pool.map(render, ['powerpoint', 'word']):
        print(app, json.dumps(status, ensure_ascii=False), flush=True)
