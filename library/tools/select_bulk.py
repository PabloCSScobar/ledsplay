"""Stage 1 of the bulk library: list public-domain piano pieces from PDMX.csv (all copies; dedup happens in build_bulk).

Usage: python3 select_bulk.py PDMX.csv resolved.json OUT.json
resolved.json is the hand-picked list (skipped here, it stays in the catalog as is).
"""
import csv, json, re, sys, unicodedata
from composers import match_composer

csv.field_size_limit(10**9)

# Not a solo piano piece, or not a classical work (games, films, pop styles).
EXCLUDE = re.compile(
    r'\b(tetris|movie|film|anime|undertale|minecraft|pok[eé]mon|zelda|mario|sonic|cover|remix|meme|lo-?fi|jazz(y|ed)?|'
    r'rock|trap|rap|swing|boogie|ringtone|fortnite|among us|genshin|tiles|duet|duo|trio|quartet|4[ -]hands?|four hands|'
    r'vierh[aä]ndig|4 mains|quatre mains|two pianos|2 pianos|orchestra|orchestral|choir|chorus|satb|vocal|voice|soprano|'
    r'alto|tenor|bass(o)? continuo|violin|viola|cello|flute|clarinet|oboe|bassoon|trumpet|horn|guitar|harp|lute|recorder|'
    r'accordion|ukulele|mandolin|organ|lyrics|karaoke|mashup|medley|vs\.?|feat\.?|ft\.?|tiktok|youtube|exercise only|'
    r'unfinished|incomplete|wip|draft|test|practice part|left hand only|right hand only|melody only|accompaniment|'
    r'acc|with a twist|twist|contest|competition|submission|midiflip|inverted|harmonic exercises?|not played|majorized|'
    r'ost|soundtrack|anthem|himno|secondo|secoundo|primo|one[- ]handed|weird|booked|inspiration|inspired|homage|hommage|'
    r'style of|in the style|parody|ai|chatgpt|generated|my version|own version|reharmoni[sz]ed|for (my|a) student)\b|'
    # living or recently deceased composers (not public domain) named next to a classical one
    r'\b(mompou|sabina|jay chou|hisaishi|einaudi|yiruma|zimmer|morricone|tiersen|shostakovich|stravinsk|khachaturian|'
    r'kabalevsk|poulenc|piazzolla|britten|copland|bernstein|messiaen|villa-?lobos|sibelius|vaughan williams|grainger|'
    r'lecuona|rodrigo|gli[eè]re|gretchaninov|grechaninov|ibert|milhaud|honegger|dohn[aá]nyi|richard clayderman|'
    r'kevin macleod|ludovico|joe hisaishi|john williams|hans zimmer|max richter|philip glass|arvo p[aä]rt)', re.I)
ARRANGED = re.compile(r'\b(arr\.?|arranged|arrangement|arranger|bearb\.?|transcribed by|transcription by)\b', re.I)
CATALOG = re.compile(
    r'\b(bwv|k|kv|op|opus|woo|hob|l|d|s|r|sz|m|lwv|hwv|rv|wq|h|b|tr|th|anh)\.?\s*([a-z]{0,4}\.?\s*\d+[a-z]?)'
    r'(?:\s*(?:,|/)?\s*(?:no|nr|n|#|num)\.?\s*(\d+))?', re.I)
MOVEMENT = re.compile(
    r'\b(?:(\d)(?:st|nd|rd|th)\s+mov(?:ement|t)?|mov(?:ement|t)?\.?\s*(\d|i{1,3}|iv|v)|(i{1,3}|iv|v)\.\s|'
    r'(first|second|third|fourth|fifth) movement)\b', re.I)


def fold(text):
    text = text.replace('ł', 'l').replace('Ł', 'L')
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()


def fix_mojibake(text):
    """Undo UTF-8 read as Latin-1/CP1252, also twice over ("Ð\x9f..." -> "П", "Bâ\x99\xad" -> "B♭")."""
    for _ in range(2):
        for codec in ('latin-1', 'cp1252'):
            try:
                fixed = text.encode(codec).decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
            if fixed != text:
                text = fixed
                break
        else:
            break
    return text


def work_key(composer, title):
    """Same key for copies of one work: catalogue number (+ number in set, + movement), else folded title."""
    folded = fold(title)
    match = CATALOG.search(folded)
    movement = MOVEMENT.search(folded)
    move = next((g for g in movement.groups() if g), '') if movement else ''
    if match:
        kind = {'kv': 'k', 'opus': 'op'}.get(match.group(1).lower(), match.group(1).lower())
        number = re.sub(r'\W', '', match.group(2))
        return f"{composer}|{kind}{number}|{match.group(3) or ''}|{move}"
    words = re.sub(composer_words(composer), ' ', folded)
    words = re.sub(r'\b(for|piano|solo|version|easy|simplified|the|by|in|from|full|original|score|sheet|music|no|nr)\b', ' ', words)
    return f"{composer}|{' '.join(re.findall(r'[a-z0-9]+', words))}|{move}"


def composer_words(composer):
    parts = [fold(p) for p in re.findall(r'[\w\-]+', composer) if len(p) > 2]
    return r'\b(' + '|'.join(map(re.escape, parts)) + r')\b' if parts else r'(?!)'


def popularity(r):
    def num(key):
        try:
            return float(r[key] or 0)
        except ValueError:
            return 0.0
    return (num('n_favorites') * 3 + num('n_ratings') * num('rating') + num('n_views') / 500)



def main():
    CSV_PATH, CURATED, OUT = sys.argv[1:4]
    curated = json.load(open(CURATED))
    curated_mxl = {c['mxl'] for c in curated}
    stats = {}
    def count(name):
        stats[name] = stats.get(name, 0) + 1

    picked = []
    with open(CSV_PATH) as f:
        for r in csv.DictReader(f):
            if r['license'] not in ('publicdomain', 'cc-zero') or r['license_conflict'] == 'True':
                continue
            if r['is_official'] == 'True' or r['has_paywall'] == 'True' or r['subset:all_valid'] != 'True':
                continue
            if r['is_draft'] == 'True' or r['has_lyrics'] == 'True' or r['is_original'] == 'True':
                continue
            tracks = r['tracks'].split('-') if r['tracks'] not in ('', 'NA') else []
            if tracks != ['0']:  # one piano part (two staves are checked in the file later)
                continue
            count('piano')
            title = fix_mojibake(r['title'])
            subtitle = fix_mojibake(r['subtitle']) if r['subtitle'] != 'NA' else ''
            composer_field = fix_mojibake(r['composer_name'])
            composer = match_composer(composer_field, title, subtitle)
            if not composer:
                continue
            count('composer')
            text = ' | '.join((title, subtitle, composer_field, r['tags'] if r['tags'] != 'NA' else ''))
            if EXCLUDE.search(text):
                count('excluded words')
                continue
            if ARRANGED.search(text) and not composer['rx'].search(text.split('arr')[-1]):
                count('arranged by someone else')
                continue
            try:
                notes = int(float(r['n_notes'] or 0)); seconds = float(r['song_length.seconds'] or 0)
            except ValueError:
                continue
            if notes < 100 or not 30 <= seconds <= 20 * 60:
                count('size')
                continue
            count('candidates')
            if r['mxl'] in curated_mxl:
                continue
            picked.append({'key': work_key(composer['en'], title), 'title': title, 'subtitle': subtitle,
                           'composer_field': composer_field, 'composer': composer['en'], 'composer_pl': composer['pl'],
                           'mxl': r['mxl'], 'metadata': r['metadata'], 'license': r['license'], 'seconds': seconds,
                           'notes': notes, 'notes_per_bar': r['notes_per_bar'], 'complexity': r['complexity'],
                           'popularity': popularity(r)})

    picked.sort(key=lambda e: -e['popularity'])
    json.dump(picked, open(OUT, 'w'), ensure_ascii=False, indent=0)
    print(json.dumps(stats, indent=1))


if __name__ == '__main__':
    main()
