"""Clean PDMX titles for display and derive Polish titles for common musical forms."""
import re

FIRST_NAMES = {
    'johann', 'sebastian', 'j', 's', 'js', 'jsb', 'wolfgang', 'amadeus', 'w', 'a', 'wa', 'ludwig', 'van', 'l', 'v', 'lv',
    'frederic', 'frédéric', 'fryderyk', 'franciszek', 'f', 'franz', 'pyotr', 'peter', 'piotr', 'pjotr', 'ilyich', 'ilich',
    'iljitsch', 'p', 'i', 'claude', 'c', 'erik', 'e', 'robert', 'r', 'johannes', 'joseph', 'georg', 'george', 'g',
    'friedrich', 'frideric', 'george frideric', 'antonio', 'edvard', 'felix', 'domenico', 'd', 'muzio', 'carl', 'karl',
    'scott', 'sergei', 'sergey', 'serge', 'sergej', 'maurice', 'm', 'modest', 'alexander', 'alexandre', 'aleksandr',
    'enrique', 'gabriel', 'jean', 'philippe', 'jean-philippe', 'henry', 'henri', 'h', 'philipp', 'johann pachelbel',
    'anton', 'cornelius', 'edward', 'nikolai', 'nikolay', 'n', 'mikhail', 'moritz', 'ignacy', 'jan', 'john', 'louis',
    'moreau', 'maria', 'von', 'jacques', 'georges', 'camille', 'jules', 'giuseppe', 'giacomo', 'gioachino', 'gioacchino',
    'émile', 'luigi', 'arcangelo', 'tomaso', 'dieterich', 'cécile', 'anatoly', 'anatol', 'samuil', 'vladimir', 'ludvig',
    'nepomuk', 'bedřich', 'bedrich', 'béla', 'bela', 'b', 'charles', 'valentin', 'charles-valentin', 'christoph',
    'willibald', 'william', 'orlando', 'stephen', 'stanisław', 'stanislaw', 'henryk', 'isaac', 'isaak', 'antonín',
    'antonin', 'ferruccio', 'philip', 'gustav', 'richard', 'léo', 'leo', 'emanuel', 'cpe', 'k', 'ph', 'jl', 'jb',
    'baptiste', 'jean-baptiste', 'mr', 'herr', 'by', 'de', 'di', 'da', 'del', 'le', 'la', 'anatoliy', 'anatolij',
    'bartholdy', 'achille', 'claude-achille', 'nikolay', 'andreyevich', 'ilych', 'modeste', 'petrovich',
}
NOISE = re.compile(
    r'\(\s*(?:for\s+)?(?:solo\s+)?piano(?:\s+solo)?(?:\s+version)?\s*\)|\bfor\s+(?:solo\s+)?piano(?:\s+solo)?\b|'
    r'\bpiano\s+solo\b|\bsolo\s+piano\b|\bpiano\s+version\b|\bsheet\s+music\b|\bfull\s+score\b|\(\s*original\s*\)|'
    r'\(\s*\d{4}\s*[-–]\s*\d{4}\s*\)|\(\s*\)|\[\s*\]|^\s*piano\s+(?=sonat|concert|piece)|\{[^}]*\}|'
    r'\[\s*unedited\s*\]|\(\s*real audio\s*\)|\(\s*origi?a?nal\s*\)|\(\s*midiflip\s*\)|'
    r'\(\s*piano (?:score|transcription|arrangement)\s*\)|[-–]\s*(?:bug)?fix\s*$|[-–]\s*piano\s*$|\bpiano\s*$', re.I)
SEPARATORS = ' -–—:|/,.;_~*'


def strip_composer(title, composer_rx):
    """Remove the composer's name (with first names, initials and life dates) from a title."""
    for _ in range(3):
        match = composer_rx.search(title)
        if not match:
            break
        start, end = match.span()
        # Grow left over first names and initials: "Johann Sebastian " / "J. S. " / "W.A."
        while True:
            left = re.search(r"([\wÀ-ÿ.\-']+)[\s.]*$", title[:start])
            if not left:
                break
            word = left.group(1).strip('.').lower()
            if word.replace('.', '') in FIRST_NAMES or all(part in FIRST_NAMES for part in word.split('.') if part):
                start = left.start(1)
            else:
                break
        # Grow right over "'s", life dates and first names written after the surname ("Bach, Johann Sebastian")
        right = re.match(r"(?:'s)?\s*(?:\(\s*\d{4}\s*[-–]\s*\d{4}\s*\))?", title[end:])
        end += right.end() if right else 0
        while True:
            nxt = re.match(r"[\s,]*([\wÀ-ÿ.\-']+)", title[end:])
            if not nxt:
                break
            word = nxt.group(1).strip('.').lower()
            if word and (word.replace('.', '') in FIRST_NAMES or all(p in FIRST_NAMES for p in word.split('.') if p)) \
                    and word not in ('a', 'i', 'la', 'le', 'de', 'by', 'v'):
                end += nxt.end()
            else:
                break
        before, after = title[:start], title[end:]
        before = re.sub(r'\b(?:by|von|de|di)\s*$', '', before.rstrip(), flags=re.I)
        title = before.rstrip() + ' ' + after.lstrip()
    return title


def clean_title(title, composer_rx):
    text = title.replace('_', ' ')
    text = re.sub(r'\S*(?:-\S*){3,}', lambda m: m.group(0).replace('-', ' '), text)  # "Album-fuer-die-Jugend-Nr-35" 
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^\d{1,3}\s*[-.)]\s*|^\d{1,3}\s+(?=[A-Za-zÀ-ÿ])', '', text)  # "05 Mein Gott" / "3. Prelude"
    text = strip_composer(text, composer_rx)
    text = NOISE.sub(' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([,.;:)\]])', r'\1', text)
    text = re.sub(r'([(\[])\s+', r'\1', text)
    text = re.sub(r'([(\[])[,.;:\s]+', r'\1', text)
    text = re.sub(r'\s*[-–]\s*,', ',', text)  # "(, Op.61)" after the composer was removed
    text = re.sub(r'\s*[-–—|:/]\s*([-–—|:/]\s*)+', ' - ', text)
    text = text.strip(SEPARATORS + ' ')
    if text.count('(') > text.count(')'):
        text = text.replace('(', '', 1) if text.endswith('(') else text + ')'
    if text and (text.isupper() or text.islower()):
        text = smart_title(text)
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    return text


def smart_title(text):
    def fix(word):
        if re.fullmatch(r'(?i)[ivxl]+', word) or re.fullmatch(r'(?i)(bwv|hwv|rv|woo|kv|k|op|no|nr|anh)\.?', word):
            return word.upper() if re.fullmatch(r'(?i)[ivxl]+|bwv|hwv|rv|kv', word) else word.capitalize()
        if word.lower() in ('in', 'of', 'the', 'and', 'for', 'a', 'de', 'la', 'le', 'du', 'des', 'der', 'die', 'das',
                            'und', 'major', 'minor', 'flat', 'sharp'):
            return word.lower()
        return word[:1].upper() + word[1:].lower()
    return ' '.join(fix(w) for w in text.split(' '))


# --- Polish titles -------------------------------------------------------------------------------------------------

WHOLE = [  # well-known titles first
    (r'prelude and fugue|pr[eé]lude et fugue|praeludium und fuge', 'Preludium i fuga'),
    (r'f[uü]e?r elise', 'Dla Elizy'), (r'moonlight sonata|mondscheinsonate|sonata quasi una fantasia', 'Sonata księżycowa'),
    (r'rondo alla turca|turkish march|t[uü]rkischer marsch', 'Marsz turecki'),
    (r'minute waltz', 'Walc minutowy'), (r'raindrop prelude', 'Preludium „Deszczowe”'),
    (r'revolutionary [eé]tude', 'Etiuda „Rewolucyjna”'), (r'heroic polonaise', 'Polonez „Heroiczny”'),
    (r'military polonaise', 'Polonez „Wojskowy”'), (r'fantais?ie[- ]impromptu', 'Fantazja-Impromptu'),
    (r'album for the young|album f[uü]r die jugend', 'Album dla młodzieży'),
    (r'children\'?s corner', 'Kącik dziecięcy'), (r'kinderszenen|scenes from childhood', 'Sceny dziecięce'),
    (r'the seasons|les saisons|vremena goda', 'Pory roku'), (r'well[- ]tempered clavier|wohltemperierte', 'Das Wohltemperierte Klavier'),
    (r'songs? without words|lieder? ohne worte', 'Pieśń bez słów'), (r'hungarian rhapsody', 'Rapsodia węgierska'),
    (r'hungarian dance', 'Taniec węgierski'), (r'slavonic dance', 'Taniec słowiański'),
    (r'wedding march', 'Marsz weselny'), (r'funeral march|marche fun[eè]bre', 'Marsz żałobny'),
    (r'flight of the bumble-?bee', 'Lot trzmiela'), (r'pictures at an exhibition', 'Obrazki z wystawy'),
    (r'in the hall of the mountain king', 'W grocie Króla Gór'), (r'morning mood', 'Poranek'),
    (r'dance of the sugar plum fairy', 'Taniec Wieszczki Cukrowej'), (r'swan lake', 'Jezioro łabędzie'),
    (r'nutcracker', 'Dziadek do orzechów'), (r'the entertainer', 'The Entertainer'),
    (r'liebestraum', 'Marzenie miłosne'), (r'tr[aä]umerei', 'Marzenie (Träumerei)'),
    (r'the happy farmer|fr[oö]hlicher landmann', 'Wesoły rolnik'), (r'wild horseman|wilder reiter', 'Dziki jeździec'),
    (r'the four seasons', 'Cztery pory roku'),
]
FORMS = [
    (r'pr[eé]ludes?|praeludium|preludio|prelude', 'Preludium'), (r'fugue|fuga|fughetta', 'Fuga'),
    (r'invention|inventio', 'Inwencja'), (r'sinfonia', 'Sinfonia'),
    (r'minuet|menuett?o?|minuetto', 'Menuet'), (r'waltz|valse|walzer|vals', 'Walc'),
    (r'nocturne|notturno', 'Nokturn'), (r'mazurka', 'Mazurek'), (r'polonaise|polonez', 'Polonez'),
    (r'[eé]tudes?|study|studie', 'Etiuda'), (r'ballade|ballad', 'Ballada'), (r'sonatina|sonatine', 'Sonatina'),
    (r'sonata|sonate', 'Sonata'), (r'gavotte', 'Gawot'), (r'sarabande', 'Sarabanda'), (r'allemande', 'Allemande'),
    (r'courante|corrente', 'Kuranta'), (r'march|marche|marsch|marcia', 'Marsz'),
    (r'lullaby|berceuse|wiegenlied|cradle song', 'Kołysanka'), (r'variations?|variationen', 'Wariacje'),
    (r'fantasia|fantasie|fantaisie|fantasy', 'Fantazja'), (r'rhapsody|rhapsodie', 'Rapsodia'),
    (r'romance|romanze', 'Romans'), (r'arabesque|arabeske', 'Arabeska'), (r'bagatelle', 'Bagatela'),
    (r'dance|danse|tanz', 'Taniec'), (r'song|lied|chanson', 'Pieśń'), (r'toccata', 'Toccata'),
    (r'impromptu', 'Impromptu'), (r'scherzo', 'Scherzo'), (r'rondo', 'Rondo'), (r'gigue|giga|jig', 'Gigue'),
    (r'air|aria', 'Aria'), (r'chorale?|choral', 'Chorał'), (r'serenade|st[aä]ndchen', 'Serenada'),
    (r'humoresque', 'Humoreska'), (r'elegy|[eé]l[eé]gie', 'Elegia'), (r'barcarolle', 'Barkarola'),
    (r'polka', 'Polka'), (r'galop', 'Galop'), (r'ecossaise|[eé]cossaise', 'Ecossaise'), (r'rag', 'Rag'),
    (r'suite', 'Suita'), (r'partita', 'Partita'), (r'canon|kanon', 'Kanon'), (r'overture|ouverture', 'Uwertura'),
    (r'symphony|symphonie|sinfonie', 'Symfonia'), (r'concerto|konzert', 'Koncert'),
]
KEY = re.compile(r'\b(?:in\s+)?([A-Ga-g])(?:[\s-]?(flat|sharp|♭|♯|b|#|is|es|s))?[\s-]+(major|minor|maj\.?|min\.?|dur|moll)\b', re.I)
MOVEMENT_WORDS = re.compile(r'\b(\d)(?:st|nd|rd|th)\s+mov(?:ement|t)?\.?|\bmov(?:ement|t)?\.?\s*(\d|[IV]+)\b', re.I)


def german_key(letter, accidental, mode):
    letter = letter.upper()
    acc = (accidental or '').lower()
    flat = acc in ('flat', '♭', 'b', 'es', 's')
    sharp = acc in ('sharp', '♯', '#', 'is')
    if letter == 'B' and flat:
        name = 'B'
    elif letter == 'B':
        name = 'H' + ('is' if sharp else '')
    elif flat:
        name = letter + ('s' if letter in 'AE' else 'es')
    elif sharp:
        name = letter + 'is'
    else:
        name = letter
    minor = mode.lower().startswith(('min', 'moll'))
    return (name.lower() + '-moll') if minor else (name + '-dur')


def polish_title(clean):
    """Polish title when the title starts with a known form or famous name; None when no rule fits."""
    text = clean
    for rx, pl in WHOLE:
        match = re.match(r'(?i)\s*(?:the\s+)?(?:' + rx + r')\b', text)
        if match:
            return _finish(pl, text[match.end():])
    match = re.match(r'(?i)\s*(' + '|'.join(rx for rx, _ in FORMS) + r')s?\b', text)
    if not match:
        return None
    word = match.group(1)
    pl = next(p for rx, p in FORMS if re.fullmatch(rx, word, re.I))
    return _finish(pl, text[match.end():])


# Words a Polish title may keep from the original: catalogue numbers, keys, numbering, roman numerals.
_ALLOWED = re.compile(r'(?i)^(op|nr|cz|bwv|hwv|kv|k|woo|hob|anh|l|d|s|r|rv|sz|wq|h|b|lwv|m|tr|[ivx]+|'
                      r'[a-h](is|es|s)?-(dur|moll)|\d+[a-z]{0,3}|[a-z]{1,3}\d+[a-z]{0,3}|[a-z]|fragment|posth)$')


NICKNAMES = {
    'revolutionary': 'Rewolucyjna', 'black keys': 'Na czarnych klawiszach', 'winter wind': 'Wicher zimowy',
    'butterfly': 'Motylek', 'raindrop': 'Deszczowe', 'heroic': 'Heroiczny', 'military': 'Wojskowy',
    'waterfall': 'Wodospad', 'ocean': 'Ocean', 'tristesse': 'Tristesse', 'aeolian harp': 'Harfa eolska',
    'appassionata': 'Appassionata', 'pathetique': 'Patetyczna', 'pathétique': 'Patetyczna', 'tempest': 'Burza',
    'moonlight': 'Księżycowa', 'farewell': 'Pożegnalny', 'minute': 'Minutowy', 'funeral march': 'Marsz żałobny',
}


def _finish(head, rest):
    # A nickname in quotes is translated when known, otherwise left out of the Polish title
    def nickname(m):
        pl = NICKNAMES.get(m.group(1).strip().lower())
        return f' „{pl}”' if pl else ''
    rest = re.sub(r'[,\s]*["“”„\'‘’]([^"“”„\'‘’]{3,30})["“”„\'‘’]', nickname, rest)
    quoted = re.findall(r'„[^”]*”', rest)
    rest = re.sub(r'„[^”]*”', ' ', rest)
    rest = re.sub(r'\b(excerpt|fragment)\b', 'fragment', rest, flags=re.I)
    rest = re.sub(r'\bop\.?\s*posth?\.?|\bposth(?:umous|ume)?\.?', 'op. posth.', rest, flags=re.I)
    rest = KEY.sub(lambda m: german_key(*m.groups()), rest)
    rest = MOVEMENT_WORDS.sub(lambda m: 'cz. ' + (m.group(1) or m.group(2)), rest)
    rest = re.sub(r'\bNo\.?\s*(?=\d)|\bNr\.?\s*(?=\d)|\bN[°º]\s*|#\s*(?=\d)', 'nr ', rest, flags=re.I)
    rest = re.sub(r'\bOp(?:us)?\.?\s*(?=\d)', 'op. ', rest, flags=re.I)
    rest = re.sub(r'\b(?:in|en|in der|en la)\s+(?=[A-H](?:is|es|s)?-dur|[a-h](?:is|es|s)?-moll)', '', rest, flags=re.I)
    rest = re.sub(r'\s+', ' ', rest).strip(' -–—:,')
    words = re.findall(r'[^\s,.;:()\[\]–—/-]+(?:-(?:dur|moll))?', rest)
    if any(not _ALLOWED.match(w) for w in words):
        return None  # the rest of the title is in another language: keep the original instead of mixing
    rest = re.sub(r'\s*,\s*(?=op\.|nr |cz\.|BWV|KV|K\.|Hob|WoO|HWV|D\.|B\.)', ' ', rest)
    rest = re.sub(r'(?<=\d)[.:]+(?=\s|$)', '', rest)
    rest = (rest + ' ' + ' '.join(quoted)).strip()
    return f'{head} {rest}'.strip() if rest else head
