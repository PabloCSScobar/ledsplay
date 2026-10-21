# LEDsplay song library

Piano scores the LEDsplay app can add with one tap (Practice → Add song → LEDsplay library).
The device reads `catalog.json` from GitHub Pages, downloads the chosen file from `files/`
and checks its SHA-256 before saving it.

## Source and licences

Every score comes from the [PDMX dataset](https://zenodo.org/records/15571083)
(Long, Novack, Berg-Kirkpatrick, McAuley, 2024; dataset licence CC BY 4.0), which collects
MuseScore scores that their uploaders published as Public Domain or CC0.
The selection keeps only:

- works whose music is in the public domain (classical and traditional pieces),
- scores marked `publicdomain` or `cc-zero` without a licence conflict in PDMX,
- solo piano scores that the LEDsplay MusicXML parser reads without errors.

Each catalog item names its licence, the MuseScore page (`source_url`) and the
person who made the transcription (`credit`).

## Catalog format

```json
{"version": 1, "updated": "2026-10-21",
 "items": [{"id": "pdmx-5534546", "title": "Gymnopédie No. 1", "composer": "Erik Satie",
   "title_pl": "Gymnopédie nr 1", "composer_pl": "Erik Satie", "difficulty": 2,
   "filename": "Gymnopedie No. 1 - Satie.mxl", "url": "files/gymnopedie-no-1-satie.mxl",
   "size": 12345, "sha256": "…", "duration_s": 157, "license": "CC0",
   "source_url": "https://musescore.com/user/…/scores/…", "credit": "… on MuseScore, via PDMX"}]}
```

`difficulty`: 1 easy, 2 intermediate, 3 advanced. `filename` is the name the file gets on the device.
To add a piece, put the MXL in `files/` and add an item with its size and SHA-256.

## Rebuilding

`tools/` holds the curation scripts: `find.py` searches `PDMX.csv` for candidates,
`picks.json` + `en_titles.json` are the hand-picked list with titles and difficulty,
`resolve.py` maps picks to PDMX files, `build_catalog.py` copies the MXL files and writes `catalog.json`.
