"""Stage 3 of the bulk library: add the checked PDMX pieces to catalog.json after the hand-picked ones.

Usage: python3 build_bulk.py stage2.json EXTRACT_DIR resolved.json LIBRARY_DIR UPDATED [reject.txt]
The hand-picked items already in catalog.json stay first and get "featured": true.
reject.txt lists PDMX ids (one per line, "#" comments) removed after review.
"""
import hashlib, json, re, sys, unicodedata
from pathlib import Path
from composers import match_composer
from select_bulk import fix_mojibake
from dedup import Deduper
from titles import clean_title, polish_title


def ascii_fold(text):
    text = text.replace('ł', 'l').replace('Ł', 'L')
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', ascii_fold(text).lower()).strip('-')


def safe_name(text):
    return re.sub(r'\s+', ' ', re.sub(r"[^A-Za-z0-9 .,()'-]", '', ascii_fold(text))).strip()


STAGE2, EXTRACT, CURATED, LIBRARY, UPDATED = sys.argv[1:6]
REJECT = sys.argv[6] if len(sys.argv) > 6 else None
LIBRARY = Path(LIBRARY); EXTRACT = Path(EXTRACT)
LICENSES = {'publicdomain': 'Public Domain', 'cc-zero': 'CC0'}
MAX_FILENAME = 120

rejected = set()
if REJECT and Path(REJECT).exists():
    rejected = {line.split('#')[0].strip() for line in open(REJECT)} - {''}

catalog = json.load(open(LIBRARY / 'catalog.json'))
# First run: every item is hand-picked. Later runs: only items marked featured (bulk items have no flag).
first_run = not any('featured' in i for i in catalog['items'])
featured = [i for i in catalog['items'] if first_run or i.get('featured')]
for item in featured:
    item['featured'] = True
taken_names = {i['filename'].lower() for i in featured}

# Works already on the device as demo songs, then the hand-picked ones: copies of them are skipped.
DEMO = [('Johann Pachelbel', 'Canon in D'), ('Claude Debussy', 'Clair de Lune'), ('Ludwig van Beethoven', 'Fur Elise'),
        ('Ludwig van Beethoven', 'Moonlight Sonata 3rd movement'), ('Ludwig van Beethoven', 'Ode to Joy'),
        ('Scott Joplin', 'The Entertainer'), ('W.A. Mozart', 'Turkish March'),
        ('W.A. Mozart', 'Twinkle Twinkle Little Star Variations'), ('Frédéric Chopin', 'Waltz in A Minor')]
deduper = Deduper()
for composer_en, title in DEMO:
    deduper.add(composer_en, title, f'demo: {title}')
for pick in json.load(open(CURATED)):
    composer = match_composer(pick['composer'], pick['pdmx_title'])
    if composer:
        deduper.add(composer['en'], pick['pdmx_title'], f"featured: {pick['title']}")
for item in featured:
    composer = match_composer(item['composer'], item['title'])
    if composer:
        deduper.add(composer['en'], item['title'], f"featured: {item['title']}")
featured_ids = {i['id'] for i in featured}


def difficulty(entry):
    if entry['complexity'] in ('1', '2', '3'):
        return int(entry['complexity'])
    per_bar = float(entry['notes_per_bar'] or 0)
    return 1 if per_bar < 10 else 2 if per_bar < 25 else 3


def unique_filename(title, surname, pdmx_id):
    base = safe_name(title)[:MAX_FILENAME - 30].rstrip(' .,-')
    name = f'{base} - {safe_name(surname)}.mxl'
    if name.lower() in taken_names:
        name = f'{base} ({pdmx_id}) - {safe_name(surname)}.mxl'
    taken_names.add(name.lower())
    return name


bulk, skipped = [], {}
def skip(reason):
    skipped[reason] = skipped.get(reason, 0) + 1

duplicates = []
for entry in json.load(open(STAGE2)):
    if entry['problem']:
        skip('file check'); continue
    meta = json.load(open(EXTRACT / entry['metadata'].lstrip('./')))['data']['score']
    pdmx_id = f"pdmx-{meta['id']}"
    if pdmx_id in featured_ids or str(meta['id']) in rejected:
        skip('rejected in review' if str(meta['id']) in rejected else 'featured'); continue
    # The CSV lost some bytes of non-ASCII titles; the metadata file has them
    raw_title = fix_mojibake(meta.get('title') or entry['title']).replace('_', ' ')
    if re.search(r'[\u0400-\u04ff]', raw_title) and re.search(r' / [A-Za-z]', raw_title):
        raw_title = raw_title.split(' / ', 1)[1]  # "Итальянская полька / Italian Polka"
    composer = match_composer(entry['composer_field'], raw_title, entry['subtitle'])
    if not composer:
        skip('composer lost with the full title'); continue
    title = clean_title(raw_title, composer['strip_rx'])
    if len(re.findall(r'[A-Za-zÀ-ÿ]', title)) < 3:
        title = clean_title(entry['subtitle'], composer['strip_rx']) if entry['subtitle'] else ''
    if len(re.findall(r'[A-Za-zÀ-ÿ\u0400-\u04ff]', title)) < 3:
        skip('no usable title'); continue
    same = deduper.find(composer['en'], title)
    if same:
        duplicates.append(f"{meta['id']}\t{composer['en']}\t{title}\t= {same}")
        skip('duplicate'); continue
    deduper.add(composer['en'], title, f"{meta['id']} {title}")
    surname = re.sub(r'\s+(II|Jr\.?)$', '', composer['en']).split()[-1]
    filename = unique_filename(title, surname, meta['id'])
    url = f"files/{slug(title)[:80]}-{slug(surname)}-{meta['id']}.mxl"
    src = EXTRACT / entry['mxl'].lstrip('./')
    data = src.read_bytes()
    (LIBRARY / url).write_bytes(data)
    item = {
        'id': pdmx_id, 'title': title, 'composer': composer['en'],
        'title_pl': polish_title(title) or title, 'composer_pl': composer['pl'],
        'difficulty': difficulty(entry), 'filename': filename, 'url': url,
        'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
        'duration_s': round(entry.get('parsed_seconds') or entry['seconds']),
        'license': LICENSES[meta['license']], 'source_url': meta['url'],
        'credit': f"{fix_mojibake(meta['user']['name'])} on MuseScore, via PDMX",
    }
    bulk.append((entry['popularity'], item))

# Remove files of bulk items from an earlier build that are no longer in the catalog
keep = {i['url'] for i in featured} | {item['url'] for _, item in bulk}
for path in (LIBRARY / 'files').iterdir():
    if f'files/{path.name}' not in keep:
        path.unlink()

bulk.sort(key=lambda pair: -pair[0])
catalog['items'] = featured + [item for _, item in bulk]
catalog['updated'] = UPDATED
(LIBRARY / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=1) + '\n')
total = sum(i['size'] for i in catalog['items'])
Path(LIBRARY / 'tools' / 'duplicates.txt').write_text('\n'.join(duplicates) + '\n')
print(len(featured), 'featured +', len(bulk), 'more =', len(catalog['items']), 'items,', total // 1024, 'KiB;', 'skipped:', skipped)
