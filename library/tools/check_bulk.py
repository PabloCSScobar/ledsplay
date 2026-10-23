"""Stage 2 of the bulk library: keep files that are a two-staff piano score the LEDsplay parser reads.

Usage: LEDSPLAY_DATA_DIR=/tmp/x python3 check_bulk.py BACKEND_DIR stage1.json EXTRACT_DIR stage2.json
"""
import json, multiprocessing, os, shutil, sys, tempfile, zipfile
import xml.etree.ElementTree as ET

BACKEND, STAGE1, EXTRACT, OUT = sys.argv[1:5]


def score_xml(path):
    with zipfile.ZipFile(path) as z:
        container = ET.fromstring(z.read('META-INF/container.xml'))
        rootfile = next(el.get('full-path') for el in container.iter() if el.tag.endswith('rootfile'))
        return ET.fromstring(z.read(rootfile))


def structure(root):
    parts = root.findall('part')
    if len(parts) != 1:
        return f'{len(parts)} parts'
    staves = {el.text for el in parts[0].iter('staves')}
    if staves != {'2'}:
        return f'staves {sorted(staves)}'
    per_staff = {'1': 0, '2': 0}
    for note in parts[0].iter('note'):
        if note.find('rest') is None:
            per_staff[note.findtext('staff', '1')] = per_staff.get(note.findtext('staff', '1'), 0) + 1
    if min(per_staff['1'], per_staff['2']) < 20:
        return f'one hand nearly empty {per_staff}'
    return None


def check(entry):
    sys.path.insert(0, BACKEND)
    from midi.score_loader import ScoreLoader
    path = os.path.join(EXTRACT, entry['mxl'].lstrip('./'))
    try:
        problem = structure(score_xml(path))
    except Exception as e:  # broken zip or XML
        problem = f'unreadable: {e!r}'[:120]
    if problem:
        return dict(entry, problem=problem)
    work = tempfile.mkdtemp()
    try:
        copy = os.path.join(work, 'song.mxl')
        shutil.copyfile(path, copy)
        data = ScoreLoader().prepare_musicxml_data(copy)
        notes = [n for n in data['notes_with_ms'] if not n.get('is_rest')]
        if len(notes) < 100:
            return dict(entry, problem=f'parser found {len(notes)} notes')
        return dict(entry, problem=None, parsed_notes=len(notes),
                    parsed_seconds=round(data.get('total_duration_ms', 0) / 1000), size=os.path.getsize(path))
    except Exception as e:
        return dict(entry, problem=f'parser: {e!r}'[:160])
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    entries = json.load(open(STAGE1))
    with multiprocessing.Pool(max(2, os.cpu_count() - 2), maxtasksperchild=50) as pool:
        results = []
        for i, result in enumerate(pool.imap(check, entries, chunksize=4), 1):
            results.append(result)
            if i % 100 == 0:
                print(i, 'checked', flush=True)
    json.dump(results, open(OUT, 'w'), ensure_ascii=False, indent=0)
    bad = [r for r in results if r['problem']]
    print(len(results) - len(bad), 'ok,', len(bad), 'rejected')
    reasons = {}
    for r in bad:
        reason = r['problem'].split(':')[0].split(' {')[0]
        reasons[reason] = reasons.get(reason, 0) + 1
    print(json.dumps(reasons, indent=1))
