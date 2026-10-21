"""Build the LEDsplay song library from curated PDMX picks: copies MXL files, writes catalog.json."""
import hashlib, json, re, shutil, sys, unicodedata
from pathlib import Path

WORK = Path(sys.argv[1]); OUT = Path(sys.argv[2])
resolved = json.load(open(WORK / 'resolved.json'))
en = json.load(open(WORK / 'en_titles.json'))
LICENSES = {'publicdomain': 'Public Domain', 'cc-zero': 'CC0'}

def ascii_fold(text):
    text = text.replace('ł', 'l').replace('Ł', 'L')
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()

def fix_mojibake(text):
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', ascii_fold(text).lower()).strip('-')

def safe_name(text):
    return re.sub(r'\s+', ' ', re.sub(r'[^A-Za-z0-9 .,()\'-]', '', ascii_fold(text))).strip()

files = OUT / 'files'; files.mkdir(parents=True, exist_ok=True)
items = []
for pick in resolved:
    meta = json.load(open(WORK / 'extract' / pick['metadata'].lstrip('./')))['data']['score']
    src = WORK / 'extract' / pick['mxl'].lstrip('./')
    title_en, composer_en = en[pick['title']]
    surname = re.sub(r'\s+(II|Jr\.?)$', '', composer_en.replace('(attr. J.S. Bach)', '').strip()).split()[-1]
    name = slug(f"{title_en}-{surname}") + '.mxl'
    shutil.copyfile(src, files / name)
    data = (files / name).read_bytes()
    items.append({
        'id': f"pdmx-{meta['id']}",
        'title': title_en, 'composer': composer_en,
        'title_pl': pick['title'], 'composer_pl': pick['composer'],
        'difficulty': pick['difficulty'],
        'filename': f"{safe_name(title_en)} - {safe_name(surname)}.mxl",
        'url': f'files/{name}', 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
        'duration_s': round(float(pick['seconds'])),
        'license': LICENSES[meta['license']],
        'source_url': meta['url'],
        'credit': f"{fix_mojibake(meta['user']['name'])} on MuseScore, via PDMX",
    })
items.sort(key=lambda i: (i['difficulty'], i['composer'], i['title']))
catalog = {'version': 1, 'updated': sys.argv[3], 'source': 'PDMX dataset (Long et al., 2024), CC BY 4.0: https://zenodo.org/records/15571083',
           'items': items}
(OUT / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=1) + '\n')
print(len(items), 'items,', sum(i['size'] for i in items) // 1024, 'KiB')
