import csv, json, sys
csv.field_size_limit(10**9)
picks = json.load(open(sys.argv[1]))
wanted = {p[0]: p for p in picks}
best = {}
with open('/home/pawel/data/pdmx/PDMX.csv') as f:
    for r in csv.DictReader(f):
        t = r['title']
        if t not in wanted and t[:70] not in wanted:
            continue
        key = t if t in wanted else t[:70]
        if r['license'] not in ('publicdomain', 'cc-zero') or r['license_conflict'] == 'True' or r['subset:all_valid'] != 'True':
            continue
        tracks = r['tracks'].split('-')
        if any(x != '0' for x in tracks) or len(tracks) > 2:
            continue
        if key not in best or float(r['n_favorites'] or 0) > float(best[key]['n_favorites'] or 0):
            best[key] = r
out = []
for title, display, composer, diff in picks:
    r = best.get(title)
    if not r:
        print('MISSING', title, file=sys.stderr); continue
    out.append({'pdmx_title': title, 'title': display, 'composer': composer, 'difficulty': diff,
                'mxl': r['mxl'], 'metadata': r['metadata'], 'license': r['license'], 'license_url': r['license_url'],
                'seconds': r['song_length.seconds']})
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
print(len(out))
