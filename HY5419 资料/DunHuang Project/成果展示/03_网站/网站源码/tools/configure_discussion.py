"""Activate the public discussion only after its real HTTPS API is reachable."""
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--enable', metavar='SUPABASE_FUNCTION_URL')
group.add_argument('--disable', action='store_true')
args = parser.parse_args()
manifest = json.loads((ROOT / 'publication-manifest.json').read_text())
config_file = ROOT / 'dist/discussion-config.js'
config = json.loads(config_file.read_text().split('window.DUNHUANG_DISCUSSION_CONFIG = ', 1)[1].strip().removesuffix(';'))

if args.enable:
    target = urlsplit(args.enable)
    if (target.scheme != 'https' or target.username or target.password or target.query or target.fragment
        or target.port or not re.fullmatch(r'[a-z0-9-]+\.supabase\.co', target.hostname or '')
        or target.path != '/functions/v1/dunhuang-discussion'):
        raise SystemExit('Use the exact HTTPS Supabase function URL, without credentials or query parameters.')
    page = urlsplit(manifest['pages_url'])
    request = Request(args.enable, headers={'Accept': 'application/json', 'Origin': f'{page.scheme}://{page.netloc}'})
    with urlopen(request, timeout=20) as response:
        if response.headers.get('Access-Control-Allow-Origin') != f'{page.scheme}://{page.netloc}':
            raise SystemExit('The real API does not allow this GitHub Pages origin; nothing was enabled.')
        result = json.load(response)
    if not isinstance(result.get('threads'), list) or 'next' not in result:
        raise SystemExit('The real API has not passed the list contract; nothing was enabled.')
    config.update(enabled=True, apiUrl=args.enable, siteUrl=manifest['pages_url'])
else:
    config['enabled'] = False

config_file.write_text('/* Public endpoint only. Database credentials remain on the server. */\nwindow.DUNHUANG_DISCUSSION_CONFIG = ' + json.dumps(config, ensure_ascii=False, indent=2) + ';\n')
manifest['discussion'] = {'enabled': config['enabled'], 'provider': 'Supabase', 'account_required_for_visitors': False, 'api_url': config['apiUrl']}
manifest['publication_files'] = [
    {'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
    for p in sorted((ROOT / 'dist').rglob('*')) if p.is_file()
]
(ROOT / 'publication-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print('Discussion enabled after a real API read check.' if config['enabled'] else 'Discussion disabled; public forms and link are hidden.')
