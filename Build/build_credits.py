"""Build player-visible attribution from the checked-in asset manifests."""
from html import escape
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = []
seen = set()
for entry in json.loads((root / 'SourceAssets/BlendSwap/manifest.json').read_text()):
    if entry['source_id'] in seen:
        continue
    seen.add(entry['source_id'])
    license = entry['license']
    rows.append((entry['source_url'], entry['attribution'], license['name'], license['url'], entry['changes']))
for entry in json.loads((root / 'SourceAssets/source-credits.json').read_text()):
    author = entry.get('author') or ', '.join(entry.get('authors', {}))
    license_url = 'https://creativecommons.org/publicdomain/zero/1.0/' if entry['license'] == 'CC0-1.0' else 'https://creativecommons.org/licenses/by/4.0/'
    rows.append((entry['source'], author, entry['license'], license_url, entry.get('modifications', 'From the original Echelon asset kit.')))
articles = []
for url, author, label, license_url, changes in rows:
    articles.append(f'<article><p><a href="{escape(url, quote=True)}">{escape(url)}</a></p><p>{escape(author)} · <a href="{escape(license_url, quote=True)}">{escape(label)}</a></p><p>{escape(changes)}</p></article>')
html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Echelon asset credits</title><style>body{max-width:800px;margin:40px auto;padding:20px;font:16px/1.6 system-ui;background:#10242e;color:#e4f2e9}a{color:#b8eada;overflow-wrap:anywhere}article{border-top:1px solid #51757a;padding:12px 0}h1{line-height:1.2}</style><a href="/">Return to Echelon</a><h1>Asset credits</h1><p>Thanks to the artists whose work helps build Kairos. Selected BlendSwap models were adapted in Blender: geometry selection, scale and pivot corrections, material consolidation, and portable shaders. Source backgrounds and reference images are omitted. Not every asset in the original browser kit appears in this preview.</p>''' + '\n'.join(articles) + '</html>\n'
out = root / 'GCP/player/public/credits.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html)
print('Built player-visible asset attribution.')
