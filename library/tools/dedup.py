"""Recognise copies of the same work under different titles (one composer at a time)."""
import re, unicodedata
from collections import Counter

CATALOG = re.compile(
    r'\b(bwv|bmv|hwv|k|kv|op|opus|woo|hob|anh|l|d|s|rv|sz|wq|b|kk|m|twv|wwv)\.?\s*'
    r'((?:[ivx]+[a-z]?\s*[:/]\s*)?\d+[a-z]{0,2})(?:\s*(?:,|/|-|:)?\s*(?:no|nr|n|#|num|nº|n°)?\.?\s*(\d+)\b)?', re.I)
MOVEMENT = re.compile(
    r'(?:\b(\d)(?:st|nd|rd|th)\s+(?:mov|mvt)|\b(?:mov(?:ement|t)?|mvt|satz|cz)\.?\s*(\d|[ivx]+)\b|'
    r'\b(first|second|third|fourth|fifth)\s+movement|:\s*(i{1,3}|iv|v)\b)', re.I)
WORDS = {'first': '1', 'second': '2', 'third': '3', 'fourth': '4', 'fifth': '5',
         'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5'}

# Famous works: any title matching the pattern is the same work (per composer surname).
FAMOUS = [
    ('Beethoven', r'f[uü]e?r elise|para elisa|per elisa|woo\.?\s*59|bagatelle.*a[- ]?moll|bagatelle.*a minor', 'elise'),
    ('Beethoven', r'moonlight|mondschein|op\.?\s*27\D+2\b|sonat\w*\s*(no\.?\s*)?14\b', 'moonlight'),
    ('Beethoven', r'ode (to|an) (joy|die freude)|inno alla gioi|himno a la alegr|ode à la joie', 'joy'),
    ('Beethoven', r'path[eé]tique|op\.?\s*13\b', 'pathetique'),
    ('Debussy', r'clair de lune', 'clair'), ('Debussy', r'r[eê]v\w*rie|reveire', 'reverie'),
    ('Debussy', r'(premi[eè]re|first|no\.?\s*1|n1)\s*arabesque|arabesque\s*(no\.?\s*|n|#)?\s*1\b|deux arabesques|arabesques$', 'arabesque1'),
    ('Debussy', r'fille aux cheveux', 'fille'),
    ('Pachelbel', r'canon|kanon', 'canon'),
    ('Mozart', r'turkish|alla turca|t[oö]r[oö]k|t[uü]rkischer', 'turkish'),
    ('Mozart', r'ah,? vous dirai|twinkle|k\.?\s*265|k\.?\s*300e', 'twinkle'),
    ('Mozart', r'(sonat\w*|no\.?)\s*(no\.?\s*)?16\b|k\.?v?\.?\s*545|facile', 'k545'),
    ('Mozart', r'dice game|w[uü]rfelspiel|k\.?\s*516f', 'dice'),
    ('Joplin', r'entertainer', 'entertainer'), ('Joplin', r'maple leaf', 'mapleleaf'),
    ('Satie', r'gymnop[eé]die\s*(no\.?\s*|n|#)?\s*1\b|(1[eè]re|premi[eè]re|first)\s+gymnop', 'gymno1'),
    ('Satie', r'gymnop[eé]die\s*(no\.?\s*|n|#)?\s*2\b|(2[eè]me|deuxi[eè]me|second)\s+gymnop', 'gymno2'),
    ('Satie', r'gymnop[eé]die\s*(no\.?\s*|n|#)?\s*3\b|(3[eè]me|troisi[eè]me|third)\s+gymnop', 'gymno3'),
    ('Satie', r'gnossienne\s*(no\.?\s*|n|#)?\s*1\b|(1[eè]re|premi[eè]re|first)\s+gnoss', 'gnoss1'),
    ('Liszt', r'campanella', 'campanella'), ('Liszt', r'gnomenreigen|dance of the gnomes', 'gnomen'),
    ('Liszt', r'liebestr[aä]um|love dreams?|r[eê]ve d.amour|nocturne\s*(n|no\.?)\s*3', 'liebestraum'),
    ('Grieg', r'mountain king|bergk[oö]nig', 'mountainking'), ('Grieg', r'morning mood|morgenstimmung', 'morning'),
    ('Grieg', r'anitra', 'anitra'), ('Grieg', r'[aå]se.?s? (death|tod)', 'ase'),
    ('Elgar', r'nimrod', 'nimrod'),
    ('Chopin', r'minute waltz|op\.?\s*64\D+1\b', 'op64-1'), ('Chopin', r'revolutionary|op\.?\s*10\D+12\b', 'op10-12'),
    ('Chopin', r'heroic|h[eé]ro[iï]que|op\.?\s*53\b', 'op53'), ('Chopin', r'black keys|op\.?\s*10\D+5\b', 'op10-5'),
    ('Chopin', r'raindrop|op\.?\s*28\D+15\b', 'op28-15'), ('Chopin', r'fantais?ie[- ]impromptu|op\.?\s*66\b', 'op66'),
    ('Chopin', r'waltz in a minor|walc a-moll|b\.?\s*150|valse.*a minor', 'b150'),
    ('Chopin', r'funeral march|marche fun[eè]bre|op\.?\s*35', 'op35'),
    ('Chopin', r'ballade?\s*(no\.?\s*|n|#)?\s*1\b|op\.?\s*23\b', 'op23'),
    ('Chopin', r'ballade?\s*(no\.?\s*|n|#)?\s*2\b|op\.?\s*38\b', 'op38'),
    ('Chopin', r'ballade?\s*(no\.?\s*|n|#)?\s*3\b|op\.?\s*47\b', 'op47'),
    ('Chopin', r'ballade?\s*(no\.?\s*|n|#)?\s*4\b|op\.?\s*52\b', 'op52'),
    ('Chopin', r'nocturne\s*(no\.?\s*|n)?\s*20\b|c[- ]sharp minor.*(posth|b\.?\s*49)|cis-moll.*posth|lento con gran', 'b49'),
    ('Chopin', r'nocturne.*op\.?\s*9\D+2\b|nocturne\s*(no\.?\s*)?2\s*op\.?\s*9', 'op9-2'),
    ('Rachmaninoff', r'italian polk', 'polka'),
    ('Rachmaninoff', r'op\.?\s*3\D+2\b|prelude in c[- ]sharp minor|cis-moll', 'op3-2'),
    ('Tchaikovsky', r'swan lake|lago dos cisnes|lebedinoye|lac des cygnes', 'swanlake'),
    ('Tchaikovsky', r'sugar ?plum', 'sugarplum'), ('Tchaikovsky', r'october|autumn song|op\.?\s*37\D*10\b', 'october'),
    ('Rimsky-Korsakov', r'bumble', 'bumblebee'),
    ('Bach', r'air on the g|air auf der g|orchestral suite.*3.*air', 'air'),
    ('Bach', r'toccata (and|&|und|e) fug\w* in d minor|bwv\s*565', 'bwv565'),
    ('Bach', r'anh\.?\s*114\b|^(a )?minuet(to)?\s*(in )?g(\s*major)?$|^menuet(t)?\s*(in )?g(\s*major|-dur)?$|^minuet \(g major\)$', 'anh114'),
    ('Bach', r'bwv\.?\s*846\b(?!.*fug)|^(prelude|pr[eé]lude|preludio|praeludium)\s*(no\.?\s*|n)?\s*(1|i)\b(\s*in c(\s*major)?)?$|^prelude in c(\s*major)?$', 'bwv846'),
    ('Bach', r'^(fuga|fugue)\s*(no\.?\s*)?(1|i)$', 'bwv846f'),
    ('Bach', r'bwv\.?\s*772\b|^(invention|inventio|invenci[oó]n)\s*(no\.?\s*)?(1|i)\b(\s*in c(\s*major)?)?$', 'bwv772'),
    ('Mendelssohn', r'wedding march|hochzeitsmarsch', 'wedding'),
    ('Schumann', r'tr[aä]umerei', 'traumerei'), ('Schumann', r'happy farmer|fr[oö]hliche', 'happyfarmer'),
    ('Schumann', r'wild horseman|wilder reiter', 'wildhorseman'),
    ('Brahms', r'hungarian dance\s*(no\.?\s*)?5\b', 'hd5'), ('Brahms', r'hungarian dance\s*(no\.?\s*)?1\b', 'hd1'),
    ('Brahms', r'lullaby|wiegenlied|op\.?\s*49\D+4\b', 'lullaby'),
    ('Handel', r'sarabande?a?\b.*(d minor|hwv 437|re menor)|^sarabanda?e?$', 'sarabande'),
    ('Handel', r'queen of sheba', 'sheba'), ('Handel', r'passacag', 'passacaglia'),
    ('Vivaldi', r'\bspring\b|primavera|rv\.?\s*269', 'spring'), ('Vivaldi', r'\bwinter\b|l.?inverno|l.?hiver|rv\.?\s*297', 'winter'),
    ('Vivaldi', r'\bsummer\b|l.?estate|rv\.?\s*315', 'summer'),
    ('Offenbach', r'can.?can|galop infernal', 'cancan'),
    ('Rossini', r'william tell|guillaume tell|wilhelm tell', 'tell'),
    ('Strauss', r'blue danube|blauen donau|modrym dunajem', 'danube'), ('Strauss', r'radetzky', 'radetzky'),
    ('Ravel', r'pavane', 'pavane'), ('Ravel', r'bol[eé]ro', 'bolero'),
    ('Puccini', r'babbino', 'babbino'), ('Bizet', r'habanera|oiseau rebelle', 'habanera'),
    ('Wagner', r'valkyri|walk[uü]re', 'valkyries'),
]
FAMOUS = [(surname, re.compile(rx, re.I), key) for surname, rx, key in FAMOUS]

# The first of these in a title names the piece; two titles with different ones are different pieces
# (Gigue vs Sarabande of one suite, Invention vs Sinfonia, January vs February of The Seasons).
HEAD_FORMS = re.compile(
    r'\b(prelud\w*|praeludium|fug\w*|toccata|invention|inventio|invenci\w*|sinfonia|gigue|giga|sarabande?a?|allemande|'
    r'courante|corrente|menuet\w*|minuet\w*|gavotte|bourr\w*|passacai?l\w*|air|aria|polonaise|march\w*|musette|'
    r'rondo|scherzo|nocturne|waltz|valse|mazurka|etude|study|sonatina|sonata|fantasia|fantasy|variations?|chorale?|'
    r'january|february|march|april|may|june|july|august|september|october|november|december)\b', re.I)
KEY = re.compile(r'\b([a-h])(?:[\s-]?(flat|sharp|b|#|is|es))?[\s-]+(major|minor|dur|moll)\b', re.I)

STOP = {'for', 'piano', 'solo', 'version', 'easy', 'simplified', 'simple', 'the', 'by', 'in', 'from', 'full', 'original',
        'score', 'sheet', 'music', 'no', 'nr', 'and', 'of', 'a', 'de', 'la', 'le', 'en', 'st', 'nd', 'rd', 'th',
        'arrangement', 'arr', 'transcription', 'op', 'opus', 'complete', 'excerpt', 'short', 'fragment', 'part',
        'beginner', 'beginners', 'intermediate', 'advanced'}


def fold(text):
    text = text.replace('ł', 'l').replace('Ł', 'L')
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()


def movement_of(folded):
    match = MOVEMENT.search(folded)
    if not match:
        return '1'
    value = next(g for g in match.groups() if g).lower()
    return WORDS.get(value, value)


def signature(composer_en, title):
    """Strong ids (catalogue numbers, famous names) and weaker features of one composer's title."""
    folded = fold(title).replace('♯', '#').replace('♭', 'b')
    ids = set()
    move = movement_of(folded)
    for name, rx, key in FAMOUS:
        if name.lower() in fold(composer_en) and rx.search(folded):
            ids.add(f'famous:{key}#{move}')
    number_anywhere = re.search(r'\b(?:no|nr|n|num|#)\.?\s*[°º]?\s*(\d+)\b', folded)
    for match in CATALOG.finditer(folded):
        kind = {'kv': 'k', 'opus': 'op', 'bmv': 'bwv'}.get(match.group(1).lower(), match.group(1).lower())
        if kind in ('d', 'l', 's', 'b', 'm') and not re.search(r'\d{2,}', match.group(2)):
            continue  # "D 1" is more likely a key or a numbering than a catalogue number
        number = re.sub(r'\s', '', match.group(2))
        in_set = match.group(3) or (number_anywhere.group(1) if number_anywhere else '')
        ids.add(f'{kind}{number}-{in_set}#{move}')
    no_ordinals = re.sub(r'\b\d+(st|nd|rd|th)\b', ' ', folded)
    romans = {'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5', 'vi': '6', 'vii': '7', 'viii': '8', 'ix': '9',
              'x': '10', 'xi': '11', 'xii': '12'}
    numbers = Counter(re.findall(r'\d+', no_ordinals) +
                      [romans[r] for r in re.findall(r'(?<![\w\'])(i{1,3}|iv|vi{0,3}|ix|xi{0,2})(?![\w\'])', no_ordinals)])
    head = HEAD_FORMS.search(folded)
    head = _canonical_head(head.group(1).lower()) if head else None
    key = KEY.search(folded)
    key = (key.group(1) + {'flat': 'b', 'es': 'b', 'sharp': '#', 'is': '#'}.get((key.group(2) or '').lower(),
           key.group(2) or '') + key.group(3).lower()[:2].replace('du', 'ma').replace('mo', 'mi')) if key else None
    tokens = {t for t in re.findall(r'[a-z]+|\d+', folded) if t not in STOP and t not in fold(composer_en).split()}
    return {'ids': ids, 'tokens': tokens, 'numbers': numbers, 'move': move,
            'head': head, 'key': key}


def _canonical_head(word):
    for prefix, name in (('prel', 'prelude'), ('prae', 'prelude'), ('fug', 'fugue'), ('inven', 'invention'),
                         ('menu', 'minuet'), ('minu', 'minuet'), ('sarab', 'sarabande'), ('gig', 'gigue'),
                         ('passac', 'passacaglia'), ('bour', 'bourree'), ('cor', 'courante'), ('cou', 'courante'),
                         ('vals', 'waltz'), ('valse', 'waltz'), ('etude', 'etude'), ('study', 'etude'),
                         ('fanta', 'fantasia'), ('variation', 'variations'), ('choral', 'chorale'), ('aria', 'air')):
        if word.startswith(prefix):
            return name
    return word


def different_pieces(a, b):
    if (a['numbers'] - b['numbers']) and (b['numbers'] - a['numbers']):
        return True
    if a['head'] and b['head'] and a['head'] != b['head']:
        return True
    if a['key'] and b['key'] and a['key'] != b['key']:
        return True
    return a['move'] != b['move']


class Deduper:
    def __init__(self):
        self.seen = {}  # composer -> list of (signature, label)

    def find(self, composer_en, title):
        sig = signature(composer_en, title)
        for other, label in self.seen.get(composer_en, []):
            shared = sig['ids'] & other['ids']
            # A famous name or a full catalogue number ("op9-2") is enough on its own
            same_head = not (sig['head'] and other['head'] and sig['head'] != other['head'])
            if same_head and any(i.startswith('famous:') or not re.search(r'-#', i) for i in shared):
                return label
            if different_pieces(sig, other):
                continue
            if shared:
                return label
            if not sig['ids'] and not other['ids'] and sig['tokens'] and other['tokens']:
                if len(sig['tokens'] & other['tokens']) / len(sig['tokens'] | other['tokens']) >= 0.75:
                    return label
        return None

    def add(self, composer_en, title, label):
        self.seen.setdefault(composer_en, []).append((signature(composer_en, title), label))
