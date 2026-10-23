"""Composers whose music is in the public domain in the EU (died before 1956, life + 70 years).

Each entry: (regex matched against PDMX composer/title text, English name, Polish name, year of death).
Regexes are anchored on surnames that are unlikely to be ordinary words.
"""
import re

COMPOSERS = [
    (r'c\.?\s?p\.?\s?e\.?\s?bach|carl philipp emanuel bach', 'C.P.E. Bach', 'C.P.E. Bach', 1788),
    (r'(?<!c\.p\.e\. )\bbach\b|\bbwv\b', 'J.S. Bach', 'J.S. Bach', 1750),
    (r'\bchopin\b|\bszopen\b', 'Frédéric Chopin', 'Fryderyk Chopin', 1849),
    (r'\bmozart\b', 'W.A. Mozart', 'W.A. Mozart', 1791),
    (r'\bbeethoven\b', 'Ludwig van Beethoven', 'Ludwig van Beethoven', 1827),
    (r'\bschubert\b', 'Franz Schubert', 'Franz Schubert', 1828),
    (r'\bschumann\b', 'Robert Schumann', 'Robert Schumann', 1856),
    (r'\bliszt\b', 'Franz Liszt', 'Ferenc Liszt', 1886),
    (r'\bdebussy\b', 'Claude Debussy', 'Claude Debussy', 1918),
    (r'\bsatie\b', 'Erik Satie', 'Erik Satie', 1925),
    (r'(tch?aikovsk|tschaikowsk|czajkowsk|chaikovsk)\w*', 'P.I. Tchaikovsky', 'Piotr Czajkowski', 1893),
    (r'\bbrahms\b', 'Johannes Brahms', 'Johannes Brahms', 1897),
    (r'\bhaydn\b', 'Joseph Haydn', 'Joseph Haydn', 1809),
    (r'\bh[aäe]e?ndel\b', 'G.F. Handel', 'Georg Friedrich Händel', 1759),
    (r'\bvivaldi\b', 'Antonio Vivaldi', 'Antonio Vivaldi', 1741),
    (r'\bgrieg\b', 'Edvard Grieg', 'Edvard Grieg', 1907),
    (r'\bmendels+h?o+h?n\b(?:[- ]bartholdy)?|\bbartholdy\b', 'Felix Mendelssohn', 'Felix Mendelssohn', 1847),
    (r'\bd(omenico)?\.?\s*scarlatti\b|\bscarlatti\b', 'Domenico Scarlatti', 'Domenico Scarlatti', 1757),
    (r'\bclementi\b', 'Muzio Clementi', 'Muzio Clementi', 1832),
    (r'\bczerny\b', 'Carl Czerny', 'Carl Czerny', 1857),
    (r'\bburgm[uü]e?ller\b', 'Friedrich Burgmüller', 'Friedrich Burgmüller', 1874),
    (r'\bjoplin\b', 'Scott Joplin', 'Scott Joplin', 1917),
    (r'\brach?maninoff?\b|\brachmaninov\b|\brachmaninow\b', 'Sergei Rachmaninoff', 'Siergiej Rachmaninow', 1943),
    (r'\bravel\b', 'Maurice Ravel', 'Maurice Ravel', 1937),
    (r'\bdvo[rř][aá]k\b', 'Antonín Dvořák', 'Antonín Dvořák', 1904),
    (r'\bmuss?orgsk\w*', 'Modest Mussorgsky', 'Modest Musorgski', 1881),
    (r'\bscriabin\b|\bskriabin\b|\bskrjabin\b', 'Alexander Scriabin', 'Aleksandr Skriabin', 1915),
    (r'\balb[eé]niz\b', 'Isaac Albéniz', 'Isaac Albéniz', 1909),
    (r'\bgranados\b', 'Enrique Granados', 'Enrique Granados', 1916),
    (r'\bfaur[eé]\b', 'Gabriel Fauré', 'Gabriel Fauré', 1924),
    (r'\bc[eé]sar franck\b', 'César Franck', 'César Franck', 1890),
    (r'\bcouperin\b', 'François Couperin', 'François Couperin', 1733),
    (r'\brameau\b', 'Jean-Philippe Rameau', 'Jean-Philippe Rameau', 1764),
    (r'\bpurcell\b', 'Henry Purcell', 'Henry Purcell', 1695),
    (r'\btelemann\b', 'G.P. Telemann', 'Georg Philipp Telemann', 1767),
    (r'\bpachelbel\b', 'Johann Pachelbel', 'Johann Pachelbel', 1706),
    (r'\bdiabelli\b', 'Anton Diabelli', 'Anton Diabelli', 1858),
    (r'\bkuhlau\b', 'Friedrich Kuhlau', 'Friedrich Kuhlau', 1832),
    (r'\bgurlitt\b', 'Cornelius Gurlitt', 'Cornelius Gurlitt', 1901),
    (r'stephen heller', 'Stephen Heller', 'Stephen Heller', 1888),
    (r'\bstreabbog\b', 'Jean Louis Streabbog', 'Jean Louis Streabbog', 1886),
    (r'\bduvernoy\b', 'J.-B. Duvernoy', 'Jean-Baptiste Duvernoy', 1880),
    (r'\blemoine\b', 'Henry Lemoine', 'Henry Lemoine', 1854),
    (r'\belgar\b', 'Edward Elgar', 'Edward Elgar', 1934),
    (r'\bborodin\b', 'Alexander Borodin', 'Aleksandr Borodin', 1887),
    (r'rimsk[iy][\w-]*', 'N. Rimsky-Korsakov', 'Nikołaj Rimski-Korsakow', 1908),
    (r'\bglinka\b', 'Mikhail Glinka', 'Michaił Glinka', 1857),
    (r'\bmoszkowski\b', 'Moritz Moszkowski', 'Moritz Moszkowski', 1925),
    (r'\bpaderewski\b', 'I.J. Paderewski', 'Ignacy Jan Paderewski', 1941),
    (r'\bszymanowsk[ai]\b', 'Karol Szymanowski', 'Karol Szymanowski', 1937),
    (r'\bogi[nń]ski\b', 'Michał Kleofas Ogiński', 'Michał Kleofas Ogiński', 1833),
    (r'\bmoniuszko\b', 'Stanisław Moniuszko', 'Stanisław Moniuszko', 1872),
    (r'john field', 'John Field', 'John Field', 1837),
    (r'\balkan\b', 'Charles-Valentin Alkan', 'Charles-Valentin Alkan', 1888),
    (r'\bgottschalk\b', 'L.M. Gottschalk', 'Louis Moreau Gottschalk', 1869),
    (r'\bmacdowell\b', 'Edward MacDowell', 'Edward MacDowell', 1908),
    (r'\bc\.?\s?m\.?\s?(von|v\.)\s?weber\b|carl maria von weber', 'C.M. von Weber', 'Carl Maria von Weber', 1826),
    (r'\boffenbach\b', 'Jacques Offenbach', 'Jacques Offenbach', 1880),
    (r'\bbizet\b', 'Georges Bizet', 'Georges Bizet', 1875),
    (r'saint[- ]sa[eë]ns', 'Camille Saint-Saëns', 'Camille Saint-Saëns', 1921),
    (r'\bmassenet\b', 'Jules Massenet', 'Jules Massenet', 1912),
    (r'\bverdi\b', 'Giuseppe Verdi', 'Giuseppe Verdi', 1901),
    (r'\bpuccini\b', 'Giacomo Puccini', 'Giacomo Puccini', 1924),
    (r'\brossini\b', 'Gioachino Rossini', 'Gioachino Rossini', 1868),
    (r'johann strauss|j\. strauss|\bstrauss ii\b', 'Johann Strauss II', 'Johann Strauss (syn)', 1899),
    (r'\bwaldteufel\b', 'Émile Waldteufel', 'Émile Waldteufel', 1915),
    (r'\bboccherini\b', 'Luigi Boccherini', 'Luigi Boccherini', 1805),
    (r'\bcorelli\b', 'Arcangelo Corelli', 'Arcangelo Corelli', 1713),
    (r'\balbinoni\b', 'Tomaso Albinoni', 'Tomaso Albinoni', 1751),
    (r'\bbuxtehude\b', 'Dieterich Buxtehude', 'Dieterich Buxtehude', 1707),
    (r'\breinecke\b', 'Carl Reinecke', 'Carl Reinecke', 1910),
    (r'\bchaminade\b', 'Cécile Chaminade', 'Cécile Chaminade', 1944),
    (r'\bl[iy]adov\b', 'Anatoly Lyadov', 'Anatolij Liadow', 1914),
    (r'\barensky\b', 'Anton Arensky', 'Anton Arienski', 1906),
    (r'\bmaykapar\b|\bmaikapar\b', 'Samuil Maykapar', 'Samuił Majkapar', 1938),
    (r'\brebikov\b', 'Vladimir Rebikov', 'Władimir Riebikow', 1920),
    (r'\bschytte\b', 'Ludvig Schytte', 'Ludvig Schytte', 1909),
    (r'\bhummel\b', 'J.N. Hummel', 'Johann Nepomuk Hummel', 1837),
    (r'\bsmetana\b', 'Bedřich Smetana', 'Bedřich Smetana', 1884),
    (r'\bjan[aá][cč]ek\b', 'Leoš Janáček', 'Leoš Janáček', 1928),
    (r'\bbart[oó]k\b', 'Béla Bartók', 'Béla Bartók', 1945),
    (r'\bprokofiev\b|\bprokofjew\b', 'Sergei Prokofiev', 'Siergiej Prokofiew', 1953),
    (r'\bgershwin\b', 'George Gershwin', 'George Gershwin', 1937),
    (r'\bbusoni\b', 'Ferruccio Busoni', 'Ferruccio Busoni', 1924),
    (r'\bsinding\b', 'Christian Sinding', 'Christian Sinding', 1941),
    (r'\bnielsen\b', 'Carl Nielsen', 'Carl Nielsen', 1931),
    (r'\bmahler\b', 'Gustav Mahler', 'Gustav Mahler', 1911),
    (r'\bwagner\b', 'Richard Wagner', 'Richard Wagner', 1883),
    (r'\bgounod\b', 'Charles Gounod', 'Charles Gounod', 1893),
    (r'\bdelibes\b', 'Léo Delibes', 'Léo Delibes', 1891),
    (r'\bgluck\b', 'C.W. Gluck', 'Christoph Willibald Gluck', 1787),
    (r'\bboëllmann\b|\bboellmann\b', 'Léon Boëllmann', 'Léon Boëllmann', 1897),
    (r'\bbyrd\b', 'William Byrd', 'William Byrd', 1623),
    (r'\borlando gibbons\b', 'Orlando Gibbons', 'Orlando Gibbons', 1625),
    (r'\bdowland\b', 'John Dowland', 'John Dowland', 1626),
    (r'\bfrescobaldi\b', 'Girolamo Frescobaldi', 'Girolamo Frescobaldi', 1643),
    (r'\bsweelinck\b', 'J.P. Sweelinck', 'Jan Pieterszoon Sweelinck', 1621),
    (r'\bfroberger\b', 'J.J. Froberger', 'Johann Jakob Froberger', 1667),
    (r'\bsoler\b', 'Antonio Soler', 'Antonio Soler', 1783),
    (r'\bcimarosa\b', 'Domenico Cimarosa', 'Domenico Cimarosa', 1801),
    (r'\bdussek\b', 'J.L. Dussek', 'Jan Ladislav Dusík', 1812),
    (r'\bbertini\b', 'Henri Bertini', 'Henri Bertini', 1876),
    (r'\bsteibelt\b', 'Daniel Steibelt', 'Daniel Steibelt', 1823),
    (r'\bmarcello\b', 'Alessandro Marcello', 'Alessandro Marcello', 1747),
    (r'\bgade\b', 'Niels Gade', 'Niels Gade', 1890),
    (r'\bkarłowicz\b|\bkarlowicz\b', 'Mieczysław Karłowicz', 'Mieczysław Karłowicz', 1909),
    (r'\bżeleński\b|\bzelenski\b', 'Władysław Żeleński', 'Władysław Żeleński', 1921),
    (r'\bwieniawski\b', 'Henryk Wieniawski', 'Henryk Wieniawski', 1880),
    (r'\bnoskowski\b', 'Zygmunt Noskowski', 'Zygmunt Noskowski', 1909),
    (r'\bmaria szymanowska\b', 'Maria Szymanowska', 'Maria Szymanowska', 1831),
    (r'\bivanovici\b', 'Iosif Ivanovici', 'Iosif Ivanovici', 1902),
    (r'\bbadarzewska\b|\bbądarzewska\b', 'Tekla Bądarzewska', 'Tekla Bądarzewska', 1861),
    (r'\bsousa\b', 'John Philip Sousa', 'John Philip Sousa', 1932),
    (r'\bfoster\b', 'Stephen Foster', 'Stephen Foster', 1864),
    (r'\bkomzák\b|\bkomzak\b', 'Karel Komzák', 'Karel Komzák', 1905),
    (r'\bgranville bantock\b', 'Granville Bantock', 'Granville Bantock', 1946),
]

PD_YEAR_LIMIT = 1955  # died in 1955 or earlier -> public domain in the EU since 1 Jan 2026

# Surnames that also belong to living artists or ordinary words: trusted only in the composer field.
COMPOSER_FIELD_ONLY = {'Stephen Foster', 'Niels Gade', 'Antonio Soler', 'Alessandro Marcello', 'Richard Wagner',
                       'John Philip Sousa', 'C.W. Gluck', 'Carl Nielsen', 'Charles-Valentin Alkan', 'Christian Sinding',
                       'Gustav Mahler', 'Giuseppe Verdi', 'Henry Lemoine'}

_cpe = re.compile(COMPOSERS[0][0], re.I)
_compiled = [(re.compile(rx, re.I), en, pl, year) for rx, en, pl, year in COMPOSERS if year <= PD_YEAR_LIMIT]


def match_composer(composer_field, *other_texts):
    """Composer named in the PDMX composer field, else in the title/subtitle (strong surnames only)."""
    for text in (composer_field,) + other_texts:  # "Polonaise in G minor C.P.E. Bach" under a "J.S. Bach" composer field
        if text and _cpe.search(text):
            return _cpe_match
    for index, text in enumerate((composer_field,) + other_texts):
        if not text or text == 'NA':
            continue
        text = text.replace('_', ' ')
        for rx, en, pl, year in _compiled:
            if index > 0 and en in COMPOSER_FIELD_ONLY:
                continue
            if rx.search(text):
                return {'en': en, 'pl': pl, 'died': year, 'rx': rx,
                        'strip_rx': re.compile(rx.pattern.replace(r'|\bbwv\b', ''), re.I)}
    return None


_cpe_match = {'en': COMPOSERS[0][1], 'pl': COMPOSERS[0][2], 'died': COMPOSERS[0][3], 'rx': _cpe, 'strip_rx': _cpe}
