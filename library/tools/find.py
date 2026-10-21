import csv, re, sys, json
csv.field_size_limit(10**9)
QUERIES = json.load(open(sys.argv[1]))
rows = []
with open('/home/pawel/data/pdmx/PDMX.csv') as f:
    for r in csv.DictReader(f):
        if r['license'] not in ('publicdomain', 'cc-zero') or r['license_conflict'] == 'True':
            continue
        if r['is_official'] == 'True' or r['has_paywall'] == 'True' or r['subset:all_valid'] != 'True':
            continue
        tracks = r['tracks'].split('-') if r['tracks'] not in ('', 'NA') else []
        if not tracks or any(t != '0' for t in tracks) or len(tracks) > 2:
            continue
        rows.append(r)
for key, pattern in QUERIES.items():
    rx = re.compile(pattern, re.I)
    hits = [r for r in rows if rx.search(r['title'] + ' | ' + r['composer_name'])]
    hits.sort(key=lambda r: -float(r['n_favorites'] or 0))
    print(f'## {key} ({len(hits)})')
    for r in hits[:4]:
        print('\t'.join([r['n_favorites'], r['rating'], r['complexity'], r['song_length.seconds'][:5], r['n_notes'],
                         r['composer_name'][:30], r['title'][:70], r['mxl'], r['metadata']]))
