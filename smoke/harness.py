"""Test harness: a mock MusicBrainz relationship editor, MB release page and Discogs release page.

The userscript manager's shared storage (GM_*) is replaced by a small local HTTP server, so the
companion script on several pages shares its values as it does in Tampermonkey.
"""
import json
import os
import re
import threading
import unicodedata
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = (ROOT / 'mb-vibecode-credits-importer.user.js').read_text()
# [3.33.1] the script's version (@version), for tests that name it (the files' versions follow it)
VERSION = re.search(r'^// @version\s+(\S+)', MAIN, re.M).group(1)
# [3.33.0] the mapping file (@resource mapping): every MusicBrainz page of a context gets it as the userscript manager gives it
# (GM_getResourceText); a test can leave it out (MAPPING_SHIM_OFF) to see the script fetch it or say it is missing
MAPPING_TEXT = (ROOT / 'mb-vibecode-credits-importer-mapping.json').read_text()
MAPPING_SHIM_OFF = False
# [3.34.0] the languages file the same way (German, Spanish, French); LANGUAGES_SHIM_OFF leaves it out
LANGUAGES_TEXT = (ROOT / 'mb-vibecode-credits-importer-languages.json').read_text()
LANGUAGES_SHIM_OFF = False
RAW_GITHUB = {}
# [3.34.1] the Cover Art Archive (text from cover art, beta): the release's images [(id, types, comment, width, height)] –
# their files are PNGs of that size; CAA_REQUESTS records what was asked for. TESSERACT_FAKE: jsDelivr serves a stand-in of
# Tesseract.js (window.__ocrTexts: [{text, words}] per piece read, in order; window.__ocr records the calls)
COVER_ART = []
CAA_REQUESTS = []
TESSERACT_FAKE = True
TESSERACT_REQUESTS = []
# [3.34.6] pdf.js for booklets as PDF: jsDelivr serves the real pdfjs-dist from a local copy (npm), whatever version the script
# names; PDFJS_REQUESTS records what was asked for. Without a local copy jsDelivr answers 404 for it.
PDFJS_DIR = next((d for d in (Path('/opt/npm-tools/node_modules/pdfjs-dist'), Path.home() / '.npm-global/lib/node_modules/pdfjs-dist',
                              ROOT / 'node_modules' / 'pdfjs-dist') if (d / 'package.json').exists()), None)
PDFJS_REQUESTS = []
FAKE_TESSERACT = """window.__ocr = window.__ocr || { calls: [], langs: null, created: 0, terminated: 0 };
window.Tesseract = { createWorker: async (langs, oem, opts) => { const o = window.__ocr; o.langs = langs; o.created++;
  return { recognize: async (img) => { const k = o.calls.length; o.calls.push([img.width, img.height]);
      if (opts && opts.logger) { opts.logger({ status: 'recognizing text', progress: 0.5 }); opts.logger({ status: 'recognizing text', progress: 1 }); }
      await new Promise((r) => setTimeout(r, 30));
      const texts = window.__ocrTexts || []; const t = texts[k] || texts[texts.length - 1] || { text: '' };
      return { data: { text: t.text, words: t.words || [], lines: t.lines || [] } }; },
    terminate: async () => { o.terminated++; } }; } };"""
_PNGS = {}


def png_of(w, h, rgb=(240, 236, 228)):
    """A PNG of one colour (the images of the Cover Art Archive in the tests)."""
    import struct
    import zlib
    if (w, h) not in _PNGS:
        raw = b''.join(b'\x00' + bytes(rgb) * w for _ in range(h))
        chunk = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
        _PNGS[(w, h)] = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                         + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))
    return _PNGS[(w, h)]


def pdf_of(pages, w=420, h=420):
    """[3.34.6] A small PDF: per page a list of lines (x, y, size, text) – a text of its own, in Helvetica – or None (only a
    drawing, like a scanned page: no text)."""
    body = {1: b'<< /Type /Catalog /Pages 2 0 R >>',
            2: ('<< /Type /Pages /Kids [%s] /Count %d >>' % (' '.join(f'{4 + 2 * i} 0 R' for i in range(len(pages))), len(pages))).encode(),
            3: b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>'}
    esc = lambda t: t.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    for i, lines in enumerate(pages):
        if lines is None:
            stream = b'0.85 0.85 0.85 rg 20 20 %d %d re f' % (w - 40, h - 40)
        else:
            stream = ('BT ' + ' '.join(f'/F1 {s} Tf 1 0 0 1 {x} {y} Tm ({esc(t)}) Tj' for x, y, s, t in lines) + ' ET').encode('cp1252')
        body[4 + 2 * i] = f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w} {h}] /Resources << /Font << /F1 3 0 R >> >> /Contents {5 + 2 * i} 0 R >>'.encode()
        body[5 + 2 * i] = b'<< /Length %d >>\nstream\n' % len(stream) + stream + b'\nendstream'
    out = b'%PDF-1.4\n'
    offsets = {}
    for k in sorted(body):
        offsets[k] = len(out)
        out += f'{k} 0 obj\n'.encode() + body[k] + b'\nendobj\n'
    xref = len(out)
    n = max(body) + 1
    out += f'xref\n0 {n}\n0000000000 65535 f \n'.encode() + b''.join(f'{offsets[k]:010d} 00000 n \n'.encode() for k in range(1, n))
    out += f'trailer\n<< /Size {n} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
    return out


RAW_REQUESTS = []
SYNC = (ROOT / 'mb-vibecode-credits-importer-companion.user.js').read_text()
# [3.31.1] The script asks MusicBrainz's web service at most once every 1.1 s (MusicBrainz's rate limit). The test server
# is local, so the tests use a short gap: an import takes about 1 s instead of 11 s. DCI_MB_GAP (milliseconds) sets it;
# 0 keeps the script's own gap. Only the copy of the script the tests load is changed, never the file.
MB_GAP = int(os.environ.get('DCI_MB_GAP', '25'))
MAIN_SLOW = MAIN
if MB_GAP:
    assert MAIN.count('lastMbRequest + 1100') == 1, 'the gap between requests to MusicBrainz is no longer where the tests expect it'
    MAIN = MAIN.replace('lastMbRequest + 1100', f'lastMbRequest + {MB_GAP}')

REL = 'aaaaaaaa-1111-4111-8111-000000000001'
RG = 'aaaaaaaa-1111-4111-8111-0000000000ff'
DISCOGS_ID = 1234


def uid(prefix, n):
    return f'{prefix}-0000-4000-8000-{n:012d}'


REC = [uid('bbbbbbbb', i) for i in range(1, 5)]
WORK1 = uid('cccccccc', 1)
TITLES = ['Song One', 'Song Two', 'Song Three', 'Song Four']

# Discogs artist id -> (MB gid, name)
ARTISTS = {
    3001: (uid('dddddddd', 1), 'Bass Man'), 3002: (uid('dddddddd', 2), 'Guitar Guy'), 3003: (uid('dddddddd', 3), 'Keys Guy'),
    3004: (uid('dddddddd', 4), 'Drum Guy'), 3005: (uid('dddddddd', 5), 'Bob Producer'), 3006: (uid('dddddddd', 6), 'Photo Guy'),
    3007: (uid('dddddddd', 7), 'Writer W'), 3008: (uid('dddddddd', 8), 'Ann Rep'), 3009: (uid('dddddddd', 9), 'Writer Z'),
}
# Discogs label id -> (entity type, MB gid, name)
COMPANIES = {
    1001: ('label', uid('eeeeeeee', 1), 'Sony'), 1002: ('place', uid('eeeeeeee', 2), 'Abbey Road Studios'),
    1003: ('label', uid('eeeeeeee', 3), 'Pub Co'), 1004: ('label', uid('eeeeeeee', 4), 'Other Pub'),
}

# --- MB.linkedEntities -------------------------------------------------------------------------
ATTRS = {}


def attr(i, name, root, parent=None, free=False, aliases=None):
    ATTRS[i] = {'id': i, 'gid': uid('a77a0000', i), 'name': name, 'root_id': root, 'parent_id': parent,
                'free_text': free, 'creditable': not free, 'instrument_aliases': aliases or []}


attr(14, 'instrument', 14)
for i, n, al in [(229, 'guitar', []), (78, 'electric guitar', []), (75, 'acoustic guitar', []), (70, 'bass', []),
                 (9102, 'double bass', ['upright bass', 'contrabass']), (74, 'electric bass guitar', []),
                 (9103, 'acoustic bass guitar', []), (9104, 'synthesizer', ['synth']), (9105, 'drums (drum set)', ['drums', 'drum set']),
                 (180, 'piano', []), (9106, 'saxophone', []), (9107, 'alto saxophone', [])]:
    attr(i, n, 14, 14, aliases=al)
attr(3, 'vocal', 3)
attr(4, 'lead vocals', 3, 3)
attr(5, 'background vocals', 3, 3)
attr(1, 'additional', 1)
attr(526, 'assistant', 526)
attr(194, 'guest', 194)
attr(596, 'solo', 596)
attr(1150, 'task', 1150, free=True)

LTS = {}


def lt(i, gid, name, t0, t1, attrs=(), dates=True, deprecated=False):
    LTS[i] = {'id': i, 'gid': gid, 'name': name, 'type0': t0, 'type1': t1, 'has_dates': dates, 'description': name,
              'deprecated': deprecated, 'attributes': {str(a): {'min': 0, 'max': None} for a in attrs},
              'link_phrase': name, 'reverse_link_phrase': name, 'long_link_phrase': name}


lt(148, '59054b12-01ac-43ee-a618-285fd397e461', 'instrument', 'artist', 'recording', (14, 1, 194, 596))
lt(149, '0fdbe3c6-7700-4a31-ae54-b53f06ae1cfa', 'vocal', 'artist', 'recording', (3, 1, 194, 596))
lt(141, '5c0ceac3-feb4-41f0-868d-dc06f6e27fc0', 'producer', 'artist', 'recording', (1, 526))
lt(143, '3e3102e1-1896-4f50-b5b2-dd9824e46efe', 'mix', 'artist', 'recording', (1, 526))
lt(128, 'a01ee869-80a8-45ef-9447-c59e91aa7926', 'recording', 'artist', 'recording', (1, 526))
# as on MusicBrainz (3.15.1): mastering on recordings is deprecated ("Please add mastering engineers at the release level")
lt(136, '30adb2d7-dbcb-4393-9230-2098510ddd64', 'mastering', 'artist', 'recording', (1, 526), deprecated=True)
lt(42, '84453d28-c3e8-4864-9aae-25aa968bcf3e', 'mastering', 'artist', 'release', (1, 526))
lt(129, 'b367fae0-c4b0-48b9-a40c-f3ae4c02cffc', 'miscellaneous support', 'artist', 'recording', (1150,))
lt(156, '628a9658-f54c-4142-b0c0-95f031b544da', 'performer', 'artist', 'recording', (1, 194, 596))
lt(928, '9c02ea37-7680-4fb5-8555-e330c7aa885b', 'design', 'artist', 'release', (1, 526, 1150))
lt(20, '0b58dc9b-9c49-4b19-bb58-9c06d41c8fbf', 'photography', 'artist', 'release', (1, 1150))
lt(24, '01323b2c-6f62-4b7e-af29-7e0d7d6f7b20', 'liner notes', 'artist', 'release', (1150,))
lt(30, '8bf377ba-8d71-4ecc-97f2-7bb2d8a2a75f', 'producer', 'artist', 'release', (1, 526))
lt(62, '25dd0db4-189f-436c-a610-aacb979f13e2', 'artists and repertoire', 'artist', 'release', (1150,))
lt(1010, '25dd0db4-189f-436c-a610-aacb979f1300', 'artists and repertoire', 'artist', 'release_group', (1150,))
lt(63, '0b63af5e-85b2-4891-8234-f4b0ea7d6d0f', 'miscellaneous support', 'artist', 'release', (1150,))
lt(168, 'd59d99ea-23d4-4a80-b066-edca32ee158f', 'composer', 'artist', 'work', (1,))
lt(165, '3e48faba-ec01-47fd-8e89-30e81161661c', 'lyricist', 'artist', 'work', (1,))
lt(167, 'a255bca1-b157-4518-9108-7b147dc3fc68', 'writer', 'artist', 'work', (1,))
lt(297, 'd3fd781c-5894-47e2-8c12-86cc0e2c8d08', 'arranger', 'artist', 'work', (1,))
lt(208, 'c2b5f9b1-9b8b-4c45-8a2e-6b9c5f6a1b01', 'publishing', 'label', 'work', ())
# [3.31.5] as on MusicBrainz: a person's publishing of a work (artist–work "publishing", "published / publisher"); on the
# release a label is "published" – its parent "publishing" there is a grouping without a description
lt(161, 'a442b140-830b-30b0-a4aa-2e36f098b6aa', 'publishing', 'artist', 'work', ())
lt(32, '25858332-bf31-4ad6-85b6-6a3bccebf02e', 'published', 'label', 'release', ())
lt(359, 'cee6eeeb-14f5-4079-9789-632b46acfd33', 'publishing', 'label', 'release', ())
LTS[359]['description'] = ''
lt(711, '7387c5a2-9abe-4515-b667-9eb5ed4dd4ce', 'phonographic copyright', 'label', 'release', ())
lt(708, '2ed5b5e5-1a2b-4c8b-9b5b-1c2d3e4f5a6b', 'copyright', 'label', 'release', ())
lt(693, 'ad462279-14b0-4180-9b58-571d0eef7c51', 'recorded at', 'place', 'recording', ())
lt(694, '11d74801-1493-4a5d-bc0f-4ddc537acddb', 'mixed at', 'place', 'recording', ())
lt(278, 'a3005666-a872-32c3-ad06-98af558e99b0', 'performance', 'recording', 'work', ())
lt(180, '04a5b104-a4c2-4bac-99a1-7b837c37d9e4', 'discogs', 'artist', 'url', (), False)
lt(217, '5b987f87-25bc-4a2d-b3f1-3618795b8207', 'discogs', 'label', 'url', (), False)
lt(705, '1c140ac8-8dc2-449e-92cb-52c90d525640', 'discogs', 'place', 'url', (), False)

LINKED = {
    'link_type': {str(k): v for k, v in LTS.items()},
    'link_attribute_type': {str(k): v for k, v in ATTRS.items()},
    'work_type': {'17': {'id': 17, 'name': 'Song'}, '1': {'id': 1, 'name': 'Aria'}},
    'language': {'120': {'id': 120, 'name': 'English', 'frequency': 2}, '486': {'id': 486, 'name': '[No lyrics]', 'frequency': 2}},
}

# --- MusicBrainz web service -------------------------------------------------------------------


def ws_release(full=False):
    tracks = []
    for i, gid in enumerate(REC):
        rels = []
        if i == 0:
            rels.append({'target-type': 'work', 'type': 'performance', 'type-id': LTS[278]['gid'], 'attributes': [],
                         'work': {'id': WORK1, 'title': TITLES[0], 'relations': [
                             {'target-type': 'artist', 'type': 'composer', 'type-id': LTS[168]['gid'], 'attributes': [],
                              'artist': {'id': ARTISTS[3007][0], 'name': 'Writer W'}}] + ([] if WORK_RELS_DIRECT_ONLY else MB_EXTRA.get(WORK1, []))}})
        # Already in MusicBrainz: Drum Guy plays drums on track 1
        if i == 0:
            rels.append({'target-type': 'artist', 'type': 'instrument', 'type-id': LTS[148]['gid'], 'attributes': ['drums (drum set)'],
                         'attribute-values': {}, 'artist': {'id': ARTISTS[3004][0], 'name': 'Drum Guy'}})
        tracks.append({'position': i + 1, 'number': str(i + 1), 'title': TITLES[i],
                       'recording': {'id': gid, 'title': TITLES[i], 'relations': rels + MB_EXTRA.get(gid, [])}})
    return {'id': REL, 'title': 'Testalbum', 'date': '2001', 'text-representation': {'language': 'eng'},
            'release-group': {'id': RG, 'title': 'Testalbum', 'relations': MB_EXTRA.get(RG, [])},
            'artist-credit': [{'name': n, 'joinphrase': j, 'artist': {'id': g, 'name': mbn}} for g, mbn, n, j in RELEASE_AC],
            'relations': [{'target-type': 'url', 'type': 'discogs', 'url': {'resource': f'https://www.discogs.com/release/{DISCOGS_ID}'}}]
            + MB_EXTRA.get(REL, []),
            'media': split_media(tracks, 'title') if full else [trim_medium(m) for m in split_media(tracks, 'title')]}


def trim_medium(m):
    """[3.21.1] A medium as the release lookup gives it (WS_DROP_TRACKS: without tracks, WS_NO_RELS: recordings without relationships)."""
    if m['position'] in WS_DROP_TRACKS:
        return dict(m, tracks=[])
    if m['position'] in WS_NO_RELS:
        return dict(m, tracks=[dict(t, recording={k: v for k, v in t['recording'].items() if k != 'relations'}) for t in m['tracks']])
    return m


# MB artist–label "personal publisher" relationships (as the web service names them)
PP_TYPE = 'personal publisher'
PERSONAL_PUBLISHERS = [
    {'label': uid('eeeeeeee', 3), 'lname': 'Pub Co', 'artist': uid('dddddddd', 7), 'name': 'Writer W'},
    # a personal publisher of Writer W that Discogs does not name (suggestion only)
    {'label': uid('eeeeeeee', 9), 'lname': 'Hidden Pub', 'artist': uid('dddddddd', 7), 'name': 'Writer W'},
]

# Track counts per medium (None: one medium with all tracks)
MEDIA = None

# Answers of the Discogs API for a test: path ("/artists/3030") → JSON (None: 404)
DG_API = {}
# Bandcamp for a test: page URL ("https://band.bandcamp.com/album/x") → HTML; band page URL → (MB gid, MB name)
BC_PAGES = {}
BC_ARTISTS = {}
# The release's artist credit (below its title): [(MB gid, MB name, name as credited, join phrase)]
RELEASE_AC = []
# [3.17.3] lookups to fail: {'release': n} – the next n lookups of the release answer 503
WS_FAIL = {}


def bc_page(data, band=None):
    """A Bandcamp album or track page with its data in "data-tralbum" (as Bandcamp writes it, HTML-escaped); [3.22.1] with
    band (the name of the account) also "data-band" and "og:site_name", as Bandcamp writes them."""
    import html as _html
    meta = f'<meta property="og:site_name" content="{_html.escape(band, quote=True)}">' if band else ''
    band_attr = f' data-band="{_html.escape(json.dumps({"id": 1, "name": band}), quote=True)}"' if band else ''
    return (f'<!doctype html><html><head><title>Bandcamp</title>{meta}</head><body>'
            f'<script type="text/javascript" src="tralbum.js" data-tralbum="{_html.escape(json.dumps(data), quote=True)}"{band_attr}></script>'
            '<h2 class="trackTitle">x</h2></body></html>')


def bc_html(data, url, about_cut=None, credits_cut=None, released='January 1, 2020'):
    """[3.17.0] A Bandcamp album or track page built like Bandcamp's own (as on real pages saved on 2026-10-17): the
    track table (album), the "about" and "credits" texts (lines separated by <br>, the credits after "released …"),
    Bandcamp's shortening of long texts ("..." and a hidden rest with "more", cut after about_cut/credits_cut
    characters), and the page data in "data-tralbum"."""
    import html as _html
    cur = data.get('current', {})
    track_page = '/track/' in url
    data = dict(data, url=url, item_type='track' if track_page else 'album')

    def lines(text):
        return '\n<br>\n'.join(_html.escape(x, quote=False) for x in re.split(r'\r?\n', text))

    def body(text, cut):
        if cut is None or cut >= len(text):
            return lines(text)
        return (lines(text[:cut]) + '<span><span class="bcTruncateEllipsis">...</span></span>'
                f'<span class="bcTruncateMore" style="display:none">{lines(text[cut:])}</span><span>&nbsp; <a>more</a></span>')

    tracks = '' if track_page else '<table class="track_list track_table" id="track_table"><tbody>' + ''.join(
        f'<tr class="track_row_view linked" rel="tracknum={t["track_num"]}"><td class="track-number-col"><div class="track_number secondaryText">{t["track_num"]}.</div></td>'
        f'<td class="title-col"><div class="title"><a href="{t.get("title_link", "")}"><span class="track-title">{_html.escape(t["title"])}</span></a></div></td></tr>'
        for t in data.get('trackinfo', [])) + '</tbody></table>'
    head = (f'from <a href="{data.get("album_url", "")}">Testalbum</a>, released {released}\n<br><span style="opacity: 0.7;">published {released}<br></span>'
            if track_page else f'released {released}\n<br><span style="opacity: 0.7;">published {released}<br></span><br><br>')
    about = f'<h3 class="about-label">about</h3><div class="tralbumData tralbum-about">{body(cur["about"], about_cut)}</div>' if cur.get('about') else ''
    credits = f'<h3 class="credits-label">credits</h3><div class="tralbumData tralbum-credits">{head}{body(cur.get("credits") or "", credits_cut)}</div>'
    return ('<!doctype html><html><head><meta charset="utf-8"><title>Bandcamp</title></head><body>'
            f'<div id="name-section"><h2 class="trackTitle">{_html.escape(cur.get("title", ""))}</h2></div>{tracks}'
            f'<div class="tralbumData">{about}{credits}</div>'
            f'<script type="text/javascript" data-tralbum="{_html.escape(json.dumps(data), quote=True)}"></script></body></html>')


# GM_xmlhttpRequest as a userscript manager gives it (with fetch); the calls are recorded in window.__gmXhr
GM_XHR_SHIM = """window.__gmXhr = [];
window.GM_xmlhttpRequest = (d) => { window.__gmXhr.push(d.url);
  fetch(d.url).then((r) => (d.responseType === 'blob' ? r.blob().then((b) => d.onload({ status: r.status, response: b }))
    : r.text().then((t) => d.onload({ status: r.status, responseText: t })))).catch(() => d.onerror && d.onerror()); };"""


def split_media(tracks, title_key):
    sizes = MEDIA or [len(tracks)]
    out, k = [], 0
    for pos, n in enumerate(sizes, 1):
        part = []
        for j, t in enumerate(tracks[k:k + n]):
            t = dict(t)
            t['position'] = j + 1
            t['number'] = str(j + 1)
            part.append(t)
        # [3.21.1] the medium's id and number of tracks, as MusicBrainz gives them (web service: "track-count", page data: track_count)
        out.append({'position': pos, 'format': 'CD', title_key: '', 'tracks': part, 'id': 4500 + pos,
                    ('track-count' if title_key == 'title' else 'track_count'): n})
        k += n
    return out


# [3.21.1] media whose tracks the release lookup leaves out (positions), media whose recordings come without relationships
# (MusicBrainz leaves them out with very many recordings), and MB's own pages of tracks (/ws/js/tracks/<medium id>)
WS_DROP_TRACKS = set()
WS_NO_RELS = set()
JS_TRACKS_PAGE = 100
JS_TRACKS_CALLS = []


def ws_to_js_rel(r):
    """A relationship of the web service as MB's relationship editor has it in its JSON."""
    et = r['target-type']
    e = r.get(et) or {}
    lt_id = next((k for k, v in LTS.items() if v['gid'] == r.get('type-id')), None)
    by_name = {v['name']: v for v in ATTRS.values()}
    attrs = []
    for a in r.get('attributes', []):
        if a in by_name:
            x = {'type': {'gid': by_name[a]['gid']}}
            if a in (r.get('attribute-values') or {}):
                x['text_value'] = r['attribute-values'][a]
            attrs.append(x)
    return {'id': 1, 'linkTypeID': lt_id, 'backward': et == 'artist', 'target_type': et, 'attributes': attrs,
            'entity0_credit': r.get('target-credit', '') if et == 'artist' else '', 'entity1_credit': '', 'begin_date': None, 'end_date': None, 'ended': False,
            'target': {'entityType': et, 'gid': e.get('id'), 'name': e.get('name') or e.get('title'),
                       'relationships': [ws_to_js_rel(x) for x in e.get('relations', [])]}}


def js_tracks(medium_id, page):
    """MB's own page of tracks of a medium (/ws/js/tracks/<id>?page=N), with the relationships of the recordings."""
    JS_TRACKS_CALLS.append((medium_id, page))
    media = ws_release(full=True)['media']
    m = next((x for x in media if x['id'] == medium_id), None)
    tracks = m['tracks'] if m else []
    part = tracks[(page - 1) * JS_TRACKS_PAGE:page * JS_TRACKS_PAGE]
    more = page * JS_TRACKS_PAGE < len(tracks)
    return {'linked_entities': {'link_type': {}, 'link_attribute_type': {}},
            'pager': {'current_page': page, 'next_page': page + 1 if more else None},
            'tracks': [{'id': 7000 + t['position'], 'position': t['position'], 'number': t['number'], 'name': t['title'],
                        'recording': {'entityType': 'recording', 'gid': t['recording']['id'], 'name': t['recording']['title'],
                                      'relationships': [ws_to_js_rel(r) for r in t['recording'].get('relations', [])]}} for t in part]}


# Relationships "submitted" in a test (as if "Enter edit" had been clicked): target gid -> relations
MB_EXTRA = {}
# True: submitted relationships of the work are missing in the release lookup (e.g. its link is still an open
# edit) and only a lookup of the work itself has them. WORK_LOOKUPS records those lookups.
WORK_RELS_DIRECT_ONLY = False
WORK_LOOKUPS = []


def ws_work(gid):
    WORK_LOOKUPS.append(gid)
    rels = list(MB_EXTRA.get(gid, []))
    if gid == WORK1:
        rels = [{'target-type': 'artist', 'type': 'composer', 'type-id': LTS[168]['gid'], 'attributes': [],
                 'artist': {'id': ARTISTS[3007][0], 'name': 'Writer W'}}] + rels
    return {'id': gid, 'title': TITLES[0] if gid == WORK1 else 'x', 'relations': rels}


# MB search answers beyond ARTISTS / COMPANIES for a test: kind → [{'id', 'name', 'disambiguation', 'aliases'}]
MB_SEARCH = {}
# works the MusicBrainz work search finds (3.12.1): {'id', 'title', 'aliases': [{'name'}], 'relations': [artist rels]};
# a work is found when one of its artists is named in the query (arid:…)
WORK_SEARCH = []
WORK_QUERIES = []
# works of an artist (3.15.0): browse "work?artist=" → artist gid → [{'id', 'title', 'aliases': [{'name'}]}];
# browse "recording?artist=" → artist gid → [{'title', 'work': {'id', 'title'}}] (a work may be missing) or a number
# (that many recordings without works – a large catalogue). BROWSES records the browse requests (kind, artist, offset).
ARTIST_WORKS = {}
ARTIST_RECORDINGS = {}
BROWSES = []


def ws_browse(kind, query):
    q = urllib.parse.parse_qs(query)
    artist, offset, limit = q.get('artist', [''])[0], int(q.get('offset', ['0'])[0]), int(q.get('limit', ['25'])[0])
    BROWSES.append((kind, artist, offset))
    if kind == 'work':
        works = ARTIST_WORKS.get(artist, [])
        return {'work-count': len(works), 'work-offset': offset, 'works': works[offset:offset + limit]}
    recs = ARTIST_RECORDINGS.get(artist, [])
    if isinstance(recs, int):
        page = [{'id': uid('99999999', k), 'title': f'Recording {k}', 'relations': []} for k in range(offset, min(recs, offset + limit))]
        return {'recording-count': recs, 'recording-offset': offset, 'recordings': page}
    page = [{'id': uid('99999998', offset + k), 'title': r['title'],
             'relations': [{'target-type': 'work', 'type': 'performance', 'work': r['work']}] if r.get('work') else []}
            for k, r in enumerate(recs[offset:offset + limit])]
    return {'recording-count': len(recs), 'recording-offset': offset, 'recordings': page}
# Areas of the places in COMPANIES, for the search with an area ("Abbey Road Studios, London")
PLACE_AREAS = {'Abbey Road Studios': 'London'}
# [3.22.2] areas: the area each one is part of (gid → name)
AREA_PARENTS = {}
# [3.32.9] places and areas with what they are part of (live comments, item 113): PLACE_AREAS place gid → area gid; AREA_INFO
# area gid → {'name', 'type', 'iso1': [...], 'iso2': [...], 'parent': gid}
PLACE_AREAS = {}
AREA_INFO = {}
# [3.32.10] MusicBrainz's /ws/js/release/<gid>?inc=rels recordings (a test sets the answer) and the edits sent to /ws/js/edit/create
WS_JS_RELEASE = {}
EDITS_POSTED = []


def fold(x):
    """A name as MusicBrainz' search compares it: lower case, without accents and punctuation."""
    x = unicodedata.normalize('NFD', str(x).lower())
    return ' '.join(re.sub(r'[^\w]+', ' ', ''.join(c for c in x if not unicodedata.combining(c))).split())


def ws_search(kind, query):
    """MB search over the known artists and companies, and MB_SEARCH: a phrase ("artist:"Name"") finds that name,
    words ("artist:(a AND b) OR alias:(a AND b)") every name or alias with all of them (accents do not count)."""
    q = urllib.parse.parse_qs(query).get('query', [''])[0]
    words = re.search(r':\(([^)]*)\)', q)
    if words:
        need = [fold(w) for w in words.group(1).split(' AND ') if w.strip()]
        names = lambda x: [x['name']] + [a['name'] for a in x.get('aliases', [])]
        hit = lambda x: any(all(w in fold(n).split() for w in need) for n in names(x))
    m = re.search(r'"(.*)"', q)
    name = (m.group(1) if m else q.split(':', 1)[-1]).replace('\\"', '"').strip().lower()
    items = []
    if kind == 'artist':
        items += [{'id': g, 'name': n, 'disambiguation': '', 'score': 100} for g, n in ARTISTS.values()]
    else:
        items += [{'id': g, 'name': n, 'disambiguation': '', 'score': 100, **({'area': {'name': PLACE_AREAS[n]}} if n in PLACE_AREAS else {})}
                  for et, g, n in COMPANIES.values() if et == kind]
    items += MB_SEARCH.get(kind, [])
    if words:
        hits = [x for x in items if hit(x)]
        # a place in an area ("place:(…) AND area:(…)"); [3.22.0] in a search of areas "area:" is the name itself
        area = kind != 'area' and re.search(r'area:\(([^)]*)\)', q)
        if area:
            want = [fold(w) for w in area.group(1).split(' AND ') if w.strip()]
            hits = [x for x in hits if all(w in fold((x.get('area') or {}).get('name', '')).split() for w in want)]
    else:
        hits = [x for x in items if x['name'].lower() == name or any(a['name'].lower() == name for a in x.get('aliases', []))]
    return {kind + 's': hits, 'count': len(hits)}


# [3.21.0] web profiles MusicBrainz has for artists: url → (gid, name)
WEB_URLS = {}


def ws_url(query):
    qs = urllib.parse.parse_qs(query)
    out = []
    for res in qs.get('resource', []):
        if res in WEB_URLS:
            gid, name = WEB_URLS[res]
            out.append({'resource': res, 'relations': [{'target-type': 'artist', 'artist': {'id': gid, 'name': name, 'disambiguation': 'artist with this link'}}]})
            continue
        bc = re.match(r'https?://([a-z0-9-]+\.bandcamp\.com)/?$', res)
        if bc and res in BC_ARTISTS:
            gid, name = BC_ARTISTS[res]
            out.append({'resource': res, 'relations': [{'target-type': 'artist', 'artist': {'id': gid, 'name': name, 'disambiguation': ''}}]})
            continue
        m = re.search(r'discogs\.com/(artist|label)/(\d+)', res)
        if not m:
            continue
        kind, i = m.group(1), int(m.group(2))
        rels = []
        if kind == 'artist' and i in ARTISTS:
            rels.append({'target-type': 'artist', 'artist': {'id': ARTISTS[i][0], 'name': ARTISTS[i][1], 'disambiguation': ''}})
        if kind == 'label' and i in COMPANIES:
            et, gid, name = COMPANIES[i]
            rels.append({'target-type': et, et: {'id': gid, 'name': name, 'disambiguation': ''}})
        if rels:
            out.append({'resource': res, 'relations': rels})
    return {'urls': out} if out else None


def js_entity(gid):
    for i, (g, n) in ARTISTS.items():
        if g == gid:
            return {'entityType': 'artist', 'id': i, 'gid': g, 'name': n, 'comment': '', 'sort_name': n}
    for i, (et, g, n) in COMPANIES.items():
        if g == gid:
            return {'entityType': et, 'id': i, 'gid': g, 'name': n, 'comment': ''}
    if gid == WORK1:
        return {'entityType': 'work', 'id': 7001, 'gid': gid, 'name': TITLES[0], 'comment': ''}
    return None


WORK_FORM = """<html><body><form>
<select name="edit-work.type_id"><option value=""></option><option value="17">Song</option><option value="1">Aria</option></select>
<select name="edit-work.languages.0"><optgroup label="Frequently used"><option value="120">English</option>
<option value="486">[No lyrics]</option></optgroup></select></form></body></html>"""

# --- Discogs -------------------------------------------------------------------------------------


def discogs_release():
    ex = lambda name, role, i, tracks='': {'name': name, 'anv': '', 'role': role, 'tracks': tracks, 'id': i, 'join': ''}
    return {
        'id': DISCOGS_ID, 'title': 'Testalbum', 'country': 'UK', 'year': 2001,
        'notes': 'Recorded March 1–3, 2001 at Abbey Road Studios. Mixed May 2001.',
        'artists': [{'name': 'Test Band', 'id': 2999, 'anv': '', 'role': '', 'join': ''}],
        'labels': [{'name': 'Sony', 'id': 1001, 'catno': 'X1', 'entity_type_name': 'Label'}],
        'companies': [{'name': 'Sony', 'entity_type_name': 'Phonographic Copyright (p)', 'id': 1001, 'catno': ''},
                      {'name': 'Abbey Road Studios', 'entity_type_name': 'Recorded At', 'id': 1002, 'catno': ''},
                      {'name': 'Pub Co', 'entity_type_name': 'Published By', 'id': 1003, 'catno': ''},
                      {'name': 'Other Pub', 'entity_type_name': 'Published By', 'id': 1004, 'catno': ''},
                      {'name': 'Ghost Pub', 'entity_type_name': 'Published By', 'id': 1005, 'catno': ''}],
        'extraartists': [ex('Bass Man', 'Bass', 3001), ex('Guitar Guy', 'Guitar', 3002), ex('Keys Guy', 'Synth', 3003, '2'),
                         ex('Drum Guy', 'Drums', 3004), ex('Bob Producer', 'Produced By', 3005), ex('Photo Guy', 'Photography By', 3006),
                         ex('Ann Rep', 'A&R Consultant', 3008)],
        'tracklist': [{'position': str(i + 1), 'title': t, 'type_': 'track', 'duration': '3:00',
                       'extraartists': [ex('Writer W', 'Written-By', 3007)] if i < 2 else [ex('Writer Z', 'Composed By', 3009)] if i == 2 else []}
                      for i, t in enumerate(TITLES)],
    }


def discogs_page():
    rows = ''.join(
        f'<tr data-track-position="{i + 1}"><td>{i + 1}</td><td>{t}'
        + ('<div>Written-By – <a href="/artist/3007-Writer-W">Writer W</a></div>' if i < 2 else '') + '</td></tr>'
        for i, t in enumerate(TITLES))
    credits = [('Bass', 3001, 'Bass Man'), ('Guitar', 3002, 'Guitar Guy'), ('Synth', 3003, 'Keys Guy'), ('Drums', 3004, 'Drum Guy'),
               ('Produced By', 3005, 'Bob Producer'), ('Photography By', 3006, 'Photo Guy'), ('A&amp;R Consultant', 3008, 'Ann Rep')]
    lis = ''.join(f'<li><span>{r}</span> – <a href="/artist/{i}-{n.replace(" ", "-")}">{n}</a></li>' for r, i, n in credits)
    comp = ''.join(f'<li><span>{r}</span> – <a href="/label/{i}-x">{n}</a></li>' for r, i, n in
                   [('Phonographic Copyright (p)', 1001, 'Sony'), ('Recorded At', 1002, 'Abbey Road Studios'), ('Published By', 1003, 'Pub Co')])
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>Discogs</title>'
            f'<meta property="og:image" content="https://i.discogs.com/cover-{DISCOGS_ID}.png"></head><body><h1>Test Band – Testalbum</h1>'
            f'<div class="gallery"><a href="/release/{DISCOGS_ID}-Test-Band-Testalbum/image/1"><img src="https://i.discogs.com/cover-{DISCOGS_ID}.png" width="40"></a></div>'
            f'<section id="release-tracklist"><table>{rows}</table></section>'
            f'<section id="release-credits"><ul>{lis}</ul><h2>Companies, etc.</h2><ul>{comp}</ul></section></body></html>')


# --- Pages ---------------------------------------------------------------------------------------

def mb_edit_page():
    mediums = split_media([
        {'position': i + 1, 'number': str(i + 1), 'name': t,
         'recording': {'entityType': 'recording', 'gid': g, 'id': 5001 + i, 'name': t}} for i, (t, g) in enumerate(zip(TITLES, REC))], 'name')
    entity = {'entityType': 'release', 'gid': REL, 'id': 4001, 'name': 'Testalbum', 'mediums': mediums,
              'releaseGroup': {'entityType': 'release_group', 'gid': RG, 'id': 4101, 'name': 'Testalbum'}}
    return f"""<!doctype html><html lang="en"><head><title>Edit relationships</title></head><body>
<div id="content"><h1>Testalbum</h1><div class="tabs"><a href="#">Overview</a></div>
<div id="editor">relationship editor</div><textarea id="edit-note-text"></textarea></div>
<script>
window.__dispatched = []; window.__removed = [];
let nextRelId = -1;
window.MB = {{
  linkedEntities: {json.dumps(LINKED)},
  tree: {{ fromDistinctAscArray: (a) => ({{ __tree: a }}) }},
  relationshipEditor: {{
    state: {{ entity: {json.dumps(entity)}, added: [], expandedMediums: new Map(), loadedTracks: new Map() }},
    getRelationshipStateId: () => nextRelId--,
    dispatch(a) {{
      window.__dispatched.push(a);
      const st = this.state;
      if (a.type === 'update-relationship-state') {{
        const added = [...st.added];
        const oldId = a.oldRelationshipState ? a.oldRelationshipState.id : (a.newRelationshipState || {{}}).id;
        const i = added.findIndex((x) => x.id === oldId);
        if (a.newRelationshipState) {{ if (i >= 0) added[i] = a.newRelationshipState; else added.push(a.newRelationshipState); }}
        else if (i >= 0) added.splice(i, 1);
        // Relationships already in MusicBrainz (a test may put some into "existingRels"): changed ones leave it
        const existingRels = (st.existingRels || []).filter((x) => x.id !== oldId);
        this.state = {{ ...st, added, existingRels }};
      }} else if (a.type === 'remove-relationship') {{
        window.__removed.push(a.relationship);
        this.state = {{ ...st, added: st.added.filter((x) => x.id !== a.relationship.id) }};
      }}
    }},
  }},
}};
</script></body></html>"""


def mb_release_page():
    return '<!doctype html><html lang="en"><head><title>Testalbum</title></head><body><div id="content"><h1>Testalbum</h1></div></body></html>'


# [3.19.0] The release editor ("Edit release" /release/<MBID>/edit, "Add release" /release/add), built like MusicBrainz's
# own (2026-10): tabs, the external links editor (#external-links-editor: saved links as a.url, the last row an input),
# the buttons with "Enter edit" (#enter-edit, shown only on the tab "Edit note") and MB.releaseEditor.submissionInProgress
# (a knockout observable). Helpers for a test: __tab('edit-note'), __submit(gid, fail) (as "Enter edit" does: in progress,
# then the release page – or false again on an error); the release a new release becomes: window.__gid (default REL).
EDITOR_LINKS = {'edit': [f'https://www.discogs.com/release/{DISCOGS_ID}'], 'add': []}
# [3.19.1] a seeded "redirect_uri" (Harmony: its "Release Actions"): kind → URL; "Enter edit" then goes there with ?…&release_mbid=
EDITOR_REDIRECT = {}


def mb_release_editor_page(kind):
    links = EDITOR_LINKS.get(kind, [])
    rows = ''.join(f'<tr class="external-link-item"><td></td><td class="link-actions"></td><td><a class="url " href="{u}" target="_blank">{u}</a></td></tr>'
                   for u in links)
    rows += '<tr class="external-link-item"><td></td><td class="link-actions"></td><td><input class="value with-button" type="url" placeholder="Add link" value=""></td></tr>'
    title = 'Add release' if kind == 'add' else 'Testalbum'
    return f"""<!doctype html><html lang="en"><head><title>{title}</title></head><body><div id="content"><h1>{title}</h1>
<div id="release-editor"><ul><li><a href="#information">Release information</a></li><li><a href="#edit-note">Edit note</a></li></ul>
<div id="information"><table class="row-form" id="external-links-editor"><tbody>{rows}</tbody></table></div>
<div id="edit-note" style="display: none;"><textarea id="edit-note-text"></textarea></div>
<div class="buttons"><button type="button" id="enter-edit" class="positive" style="display: none;">Enter edit</button>
<button type="button" class="negative">Cancel</button><button type="button" data-click="nextTab">Next »</button></div></div></div>
<script>
(function () {{
  function obs(v) {{ const subs = []; const f = function (x) {{ if (!arguments.length) return v; v = x; subs.forEach((s) => s(x)); }};
    f.subscribe = (s) => subs.push(s); return f; }}
  window.MB = {{ releaseEditor: {{ submissionInProgress: obs(false), rootField: {{ release: obs({{}}) }}, redirectURI: {json.dumps(EDITOR_REDIRECT.get(kind, ''))} }} }};
  window.__tab = (id) => {{ for (const t of ['information', 'edit-note']) document.getElementById(t).style.display = t === id ? '' : 'none';
    document.getElementById('enter-edit').style.display = id === 'edit-note' ? '' : 'none'; }};
  window.__submit = (gid, fail) => {{ MB.releaseEditor.submissionInProgress(true);
    setTimeout(() => {{ if (fail) {{ MB.releaseEditor.submissionInProgress(false); return; }}
      if (MB.releaseEditor.redirectURI) {{ const a = document.createElement('a'); a.href = MB.releaseEditor.redirectURI;
        a.search += /^\\?/.test(a.search) ? '&' : '?'; a.search += 'release_mbid=' + gid; window.location.href = a.href; return; }}
      window.location.pathname = '/release/' + gid; }}, 300); }};
  document.getElementById('enter-edit').addEventListener('click', () => window.__submit(window.__gid || '{REL}', window.__fail));
}})();
</script></body></html>"""


def open_mb_any(ctx, url, gm_xhr=True, all_tabs=False):
    """[3.19.0] A MusicBrainz tab whose pages all get the main script (as a userscript manager does), also after a
    navigation of the page itself; only in the page, not in its frames. [3.19.1] Also on Harmony's pages; all_tabs: in every
    tab of the context (also those a link opens)."""
    pg = ctx.new_page()
    errs = errors_of(pg)
    # [3.19.2] GM_openInTab: the tabs the script opens are recorded in window.__gmTabs ([url, options])
    tabs = "window.__gmTabs = []; window.GM_openInTab = (url, opts) => { window.__gmTabs.push([url, opts || null]); return null; };"
    view = "if (/^musicbrainz\\.org$/.test(location.hostname)) { (%s)('full'); (%s)(%s); (%s)(%s); }" % (VIEW_PRESET, ENTRIES_PRESET, json.dumps(ENTRIES_VIEW), REMEMBER_PRESET, json.dumps(REMEMBER))
    codes = ([GM_XHR_SHIM] if gm_xhr else []) + [tabs, view, MAIN]
    (ctx if all_tabs else pg).add_init_script(script="if (window.top === window && /^(musicbrainz\\.org|harmony\\.pulsewidth\\.org\\.uk)$/.test(location.hostname)) window.addEventListener('DOMContentLoaded', () => {"
                       " for (const code of %s) { const s = document.createElement('script'); s.textContent = code; document.documentElement.appendChild(s); } });"
                       % json.dumps(codes))
    pg.goto(url)
    return pg, errs


# --- Shared GM storage ---------------------------------------------------------------------------

class Store:
    def __init__(self):
        self.data = {}
        self.changes = []
        self.v = 0
        self.lock = threading.Lock()

    def set(self, k, val):
        with self.lock:
            old = self.data.get(k)
            self.data[k] = val
            self.v += 1
            self.changes.append({'v': self.v, 'k': k, 'old': old, 'new': val})

    def delete(self, k):
        with self.lock:
            old = self.data.pop(k, None)
            self.v += 1
            self.changes.append({'v': self.v, 'k': k, 'old': old, 'new': None})


STORE = Store()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.end_headers()

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == '/get':
            self._send(STORE.data.get(q['k'][0]))
        elif u.path == '/list':
            self._send(list(STORE.data.keys()))
        elif u.path == '/version':
            self._send(STORE.v)
        elif u.path == '/changes':
            since = int(q['since'][0])
            self._send([c for c in STORE.changes if c['v'] > since])
        else:
            self._send(None)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        n = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(n).decode() if n else ''
        if u.path == '/set':
            STORE.set(q['k'][0], json.loads(body) if body else None)
        elif u.path == '/del':
            STORE.delete(q['k'][0])
        self._send(True)


SERVER = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=SERVER.serve_forever, daemon=True).start()
PORT = SERVER.server_address[1]

GM_SHIM = """(function () {
  const BASE = 'http://127.0.0.1:%d';
  const req = (m, p, body) => { const x = new XMLHttpRequest(); x.open(m, BASE + p, false); x.send(body == null ? null : body); return x.responseText; };
  window.GM_getValue = (k, d) => { const v = JSON.parse(req('GET', '/get?k=' + encodeURIComponent(k))); return v == null ? d : v; };
  window.GM_setValue = (k, v) => { req('POST', '/set?k=' + encodeURIComponent(k), JSON.stringify(v === undefined ? null : v)); };
  window.GM_deleteValue = (k) => { req('POST', '/del?k=' + encodeURIComponent(k), ''); };
  window.GM_listValues = () => JSON.parse(req('GET', '/list'));
  const listeners = [];
  window.GM_addValueChangeListener = (k, fn) => { listeners.push([k, fn]); return listeners.length; };
  let since = JSON.parse(req('GET', '/version'));
  setInterval(() => {
    const ch = JSON.parse(req('GET', '/changes?since=' + since));
    for (const c of ch) {
      since = Math.max(since, c.v);
      listeners.filter(([k]) => k === c.k).forEach(([, fn]) => { try { fn(c.k, c.old, c.new, true); } catch (e) { console.error(e); } });
    }
  }, 150);
  window.GM_openInTab = (url) => { (window.__opened = window.__opened || []).push(url); };
})();""" % PORT


def json_route(route, obj, status=200):
    if obj is None:
        route.fulfill(status=404, body='{}', content_type='application/json', headers={'Access-Control-Allow-Origin': '*'})
    else:
        route.fulfill(status=status, body=json.dumps(obj), content_type='application/json', headers={'Access-Control-Allow-Origin': '*'})


def install_routes(ctx):
    def mb(route):
        u = urllib.parse.urlparse(route.request.url)
        p = u.path
        if p == f'/release/{REL}/edit-relationships':
            return route.fulfill(body=mb_edit_page(), content_type='text/html')
        if p == f'/release/{REL}':
            return route.fulfill(body=mb_release_page(), content_type='text/html')
        if p == f'/release/{REL}/edit':
            return route.fulfill(body=mb_release_editor_page('edit'), content_type='text/html')
        if p == '/release/add':
            return route.fulfill(body=mb_release_editor_page('add'), content_type='text/html')
        if p == f'/ws/2/release/{REL}':
            # [3.17.3] a test can let the next lookups of the release fail (MusicBrainz busy: 503)
            if WS_FAIL.get('release', 0) > 0:
                WS_FAIL['release'] -= 1
                return route.fulfill(status=503, body='{}', content_type='application/json')
            return json_route(route, ws_release())
        m = re.match(r'/ws/2/label/([0-9a-f-]{36})', p)
        if m:
            return json_route(route, {'id': m.group(1), 'relations': [r for r in PERSONAL_PUBLISHERS if r['label'] == m.group(1) and False] or [
                {'target-type': 'artist', 'type': PP_TYPE, 'direction': 'backward', 'begin': r.get('begin'), 'end': r.get('end'),
                 'artist': {'id': r['artist'], 'name': r['name']}} for r in PERSONAL_PUBLISHERS if r['label'] == m.group(1)]})
        m = re.match(r'/ws/2/artist/([0-9a-f-]{36})', p)
        if m:
            return json_route(route, {'id': m.group(1), 'relations': [
                {'target-type': 'label', 'type': PP_TYPE, 'direction': 'forward', 'label': {'id': r['label'], 'name': r['lname']}}
                for r in PERSONAL_PUBLISHERS if r['artist'] == m.group(1)]})
        m = re.match(r'/ws/2/work/([0-9a-f-]{36})', p)
        if m:
            return json_route(route, ws_work(m.group(1)))
        if p.startswith('/ws/2/release-group/'):
            return json_route(route, {'id': RG, 'relations': MB_EXTRA.get(RG, [])})
        if p in ('/ws/2/work', '/ws/2/recording') and 'artist' in urllib.parse.parse_qs(u.query):
            return json_route(route, ws_browse(p.rsplit('/', 1)[1], u.query))
        if p == '/ws/2/work':
            q = urllib.parse.parse_qs(u.query).get('query', [''])[0]
            WORK_QUERIES.append(q)
            ids = set(re.findall(r'arid:([0-9a-f-]{36})', q))
            return json_route(route, {'works': [dict(w, score=100) for w in WORK_SEARCH
                                                if any(r.get('artist', {}).get('id') in ids for r in w.get('relations', []))]})
        # [3.32.9] a place with its area; an area with its type, ISO codes and the area it is part of (AREA_INFO)
        m = re.match(r'/ws/2/place/([0-9a-f-]{36})$', p)
        if m and m.group(1) in PLACE_AREAS:
            a = AREA_INFO.get(PLACE_AREAS[m.group(1)], {})
            return json_route(route, {'id': m.group(1), 'area': {'id': PLACE_AREAS[m.group(1)], 'name': a.get('name', '')}})
        m = re.match(r'/ws/2/area/([0-9a-f-]{36})$', p)
        if m and m.group(1) in AREA_INFO:
            a = AREA_INFO[m.group(1)]
            par = a.get('parent')
            return json_route(route, {'id': m.group(1), 'name': a['name'], 'type': a.get('type', ''), 'iso-3166-1-codes': a.get('iso1', []), 'iso-3166-2-codes': a.get('iso2', []),
                                      'relations': [{'type': 'part of', 'direction': 'backward', 'target-type': 'area',
                                                     'area': {'id': par, 'name': AREA_INFO.get(par, {}).get('name', '')}}] if par else []})
        # [3.32.10] the release with the relationships of its recordings, as MusicBrainz's own pages read it
        if p == f'/ws/js/release/{REL}' and WS_JS_RELEASE:
            return json_route(route, WS_JS_RELEASE)
        if p == '/ws/js/edit/create' and route.request.method == 'POST':
            EDITS_POSTED.append(json.loads(route.request.post_data or '{}'))
            return json_route(route, {'edits': [{'edit_type': 72, 'response': 1, 'edit_id': 9000 + len(EDITS_POSTED)}]})
        # [3.22.2] an area with the area it is part of (AREA_PARENTS: gid → name)
        m = re.match(r'/ws/2/area/([0-9a-f-]{36})$', p)
        if m:
            parent = AREA_PARENTS.get(m.group(1))
            return json_route(route, {'id': m.group(1), 'relations': [{'type': 'part of', 'direction': 'backward', 'target-type': 'area',
                                                                       'area': {'id': uid('aaaaaaaa', 1), 'name': parent}}] if parent else []})
        m = re.match(r'/ws/2/(artist|label|place|area|event)$', p)
        if m:
            return json_route(route, ws_search(m.group(1), u.query))
        if p == '/ws/2/url':
            return json_route(route, ws_url(u.query))
        m = re.match(r'/ws/js/tracks/(\d+)$', p)
        if m:
            return json_route(route, js_tracks(int(m.group(1)), int((urllib.parse.parse_qs(u.query).get('page') or ['1'])[0])))
        m = re.match(r'/ws/js/entity/([0-9a-f-]{36})', p)
        if m:
            return json_route(route, js_entity(m.group(1)))
        if p == '/work/create':
            return route.fulfill(body=WORK_FORM, content_type='text/html')
        return route.fulfill(status=404, body='')

    def dg_api(route):
        p = urllib.parse.urlparse(route.request.url).path
        # a test's own answers (path → JSON, None: 404)
        if p in DG_API:
            return json_route(route, DG_API[p])
        if p == f'/releases/{DISCOGS_ID}':
            return json_route(route, discogs_release())
        m = re.match(r'/(artists|labels)/(\d+)', p)
        if m:
            return json_route(route, {'id': int(m.group(2)), 'name': 'x', 'aliases': [], 'members': [], 'groups': []})
        return json_route(route, None)

    def dg_web(route):
        p = urllib.parse.urlparse(route.request.url).path
        if p.startswith(f'/release/{DISCOGS_ID}'):
            return route.fulfill(body=discogs_page(), content_type='text/html')
        return route.fulfill(body='<!doctype html><html><body><h1>Discogs</h1></body></html>', content_type='text/html')

    ctx.route('https://musicbrainz.org/**', mb)

    def harmony(route):
        # [3.19.1] Harmony's "Release Actions", built like its own page (2026-10): actions as div.action with an icon
        u = urllib.parse.urlparse(route.request.url)
        if u.path != '/release/actions':
            return route.fulfill(status=404, body='')
        mbid = urllib.parse.parse_qs(u.query).get('release_mbid', [''])[0]
        rel = f'https://musicbrainz.org/release/{mbid}'
        acts = ('<div class="action"><svg class="icon"></svg><p><a href="../release?x=1">Switch to Release Lookup</a></p></div>'
                f'<div class="action"><svg class="icon"></svg><p><a href="{rel}">Open in MusicBrainz</a></p></div>'
                f'<div class="action"><svg class="icon"></svg><div><p><a href="{rel}/add-cover-art">Add cover art</a></p></div></div>'
                '<figure class="cover-image">cover</figure>') if mbid else '<form><input name="release_mbid"></form>'
        return route.fulfill(body=f'<!doctype html><html><head><title>Release Actions – Harmony</title></head><body><main><h2>Release Actions</h2>{acts}</main></body></html>',
                             content_type='text/html')
    ctx.route('https://harmony.pulsewidth.org.uk/**', harmony)

    # [3.33.0] files on GitHub (RAW_GITHUB: path → text; others 404), e.g. the mapping file the script fetches itself
    def raw_github(route):
        u = urllib.parse.urlparse(route.request.url)
        RAW_REQUESTS.append(route.request.url)
        text = RAW_GITHUB.get(u.path)
        if text is None:
            return route.fulfill(status=404, body='404: Not Found', headers={'Access-Control-Allow-Origin': '*'})
        return route.fulfill(body=text, content_type='text/plain', headers={'Access-Control-Allow-Origin': '*'})
    ctx.route('https://raw.githubusercontent.com/**', raw_github)

    # [3.34.1] the Cover Art Archive: /release/<mbid> (the list, 404 without images) and the files (<id>.jpg, <id>-250.jpg, -1200.jpg)
    def caa(route):
        u = urllib.parse.urlparse(route.request.url)
        CAA_REQUESTS.append(u.path)
        cors = {'Access-Control-Allow-Origin': '*'}
        m = re.match(r'^/release/([0-9a-f-]{36})/?$', u.path)
        if m:
            if not COVER_ART or m.group(1) != REL:
                return route.fulfill(status=404, body='Not Found', headers=cors)
            base = f'http://coverartarchive.org/release/{REL}'
            images = [{'id': i, 'types': types, 'front': 'Front' in types, 'back': 'Back' in types, 'comment': comment, 'approved': True, 'edit': 1,
                       'image': f'{base}/{i}.jpg', 'thumbnails': {'250': f'{base}/{i}-250.jpg', '500': f'{base}/{i}-500.jpg', '1200': f'{base}/{i}-1200.jpg',
                                                                  'small': f'{base}/{i}-250.jpg', 'large': f'{base}/{i}-500.jpg'}}
                      for i, types, comment, w, h in COVER_ART]
            return route.fulfill(body=json.dumps({'images': images, 'release': f'https://musicbrainz.org/release/{REL}'}), content_type='application/json', headers=cors)
        m = re.match(r'^/release/[0-9a-f-]{36}/(\d+)(?:-(\d+))?\.jpg$', u.path)
        hit = m and next((x for x in COVER_ART if str(x[0]) == m.group(1)), None)
        if not hit:
            return route.fulfill(status=404, body='Not Found', headers=cors)
        w, h = hit[3], hit[4]
        if m.group(2):
            k = min(1, int(m.group(2)) / max(w, h))
            w, h = max(1, round(w * k)), max(1, round(h * k))
        return route.fulfill(body=png_of(w, h), content_type='image/png', headers=cors)
    ctx.route('https://coverartarchive.org/**', caa)

    def jsdelivr(route):
        m = re.match(r'^https://cdn\.jsdelivr\.net/npm/pdfjs-dist@[^/]+/(.+)$', route.request.url)
        if m:
            PDFJS_REQUESTS.append(route.request.url)
            f = PDFJS_DIR / m.group(1) if PDFJS_DIR else None
            if f and f.is_file():
                return route.fulfill(body=f.read_bytes(), content_type='text/javascript' if f.suffix in ('.mjs', '.js') else 'application/octet-stream',
                                     headers={'Access-Control-Allow-Origin': '*'})
            return route.fulfill(status=404, body='', headers={'Access-Control-Allow-Origin': '*'})
        TESSERACT_REQUESTS.append(route.request.url)
        if TESSERACT_FAKE and '/tesseract.js@' in route.request.url and route.request.url.endswith('/tesseract.min.js'):
            return route.fulfill(body=FAKE_TESSERACT, content_type='application/javascript', headers={'Access-Control-Allow-Origin': '*'})
        return route.fulfill(status=404, body='', headers={'Access-Control-Allow-Origin': '*'})
    ctx.route('https://cdn.jsdelivr.net/**', jsdelivr)
    ctx.route('https://api.discogs.com/**', dg_api)
    ctx.route('https://www.discogs.com/**', dg_web)

    def bc_web(route):
        u = urllib.parse.urlparse(route.request.url)
        page = BC_PAGES.get(f'{u.scheme}://{u.netloc}{u.path}')
        if page is None:
            return route.fulfill(status=404, body='', headers={'Access-Control-Allow-Origin': '*'})
        return route.fulfill(body=page, content_type='text/html', headers={'Access-Control-Allow-Origin': '*'})

    ctx.route(re.compile(r'https://[a-z0-9-]+\.bandcamp\.com/.*'), bc_web)
    png = bytes.fromhex('89504e470d0a1a0a0000000d4948445200000001000000010806000000'
                        '1f15c4890000000d49444154789c6360f8cf00000301010018dd8db40000000049454e44ae426082')
    ctx.route('https://i.discogs.com/**', lambda route: route.fulfill(body=png, content_type='image/png'))


LAUNCH_ARGS = ['--disable-web-security',
               '--disable-features=BlockInsecurePrivateNetworkRequests,PrivateNetworkAccessSendPreflights,PrivateNetworkAccessRespectPreflightResults']


def add_mapping(ctx):
    """[3.33.0] The mapping file as the userscript manager gives it (@resource mapping: GM_getResourceText), unless
    MAPPING_SHIM_OFF; [3.34.0] the languages file too (@resource languages), unless LANGUAGES_SHIM_OFF. For a context made
    without new_context (another browser language, a screenshot) as well."""
    files = {}
    if not MAPPING_SHIM_OFF:
        files['mapping'] = MAPPING_TEXT
    if not LANGUAGES_SHIM_OFF:
        files['languages'] = LANGUAGES_TEXT
    if files:
        ctx.add_init_script(script="if (typeof window.GM_getResourceText !== 'function') { const files = %s; window.GM_getResourceText = (name) => (name in files ? files[name] : null); }"
                            % json.dumps(files))


def new_context(browser):
    ctx = browser.new_context(viewport={'width': 1500, 'height': 1000}, accept_downloads=True)
    install_routes(ctx)
    add_mapping(ctx)
    return ctx


def errors_of(pg):
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    return errs


def with_companion(pg):
    pg.add_script_tag(content=GM_SHIM)
    pg.add_script_tag(content=SYNC)


# [3.27.0] the tests were written for the full view of the entries; the compact view has a test of its own ([3.27.2] full is
# the default again – the preset stays, harmless)
# [3.34.23] … and the arrow at "Compact | Full" (item 143) as seen – it stands below the head; t_ui_head.py compacthint tests it
VIEW_PRESET = "(v) => { if (!localStorage.getItem('dci-store-epoch')) localStorage.setItem('dci-store-epoch', '4'); if (localStorage.getItem('dci-view') === null) localStorage.setItem('dci-view', JSON.stringify(v)); if (localStorage.getItem('dci-hint-compact') === null) localStorage.setItem('dci-hint-compact', 'true'); }"
# [3.34.29] the entries as before ("legacy": a row per role, nothing joined) for the cases written before E4; the cases of the
# matrix set ENTRIES_VIEW = 'matrix' (the default of the script) before they open the page
ENTRIES_VIEW = 'legacy'
# (with the generation of the stored data: without it the script clears what is stored when it starts)
ENTRIES_PRESET = "(v) => { if (v !== 'legacy' || localStorage.getItem('dci-entries-view') !== null) return; if (!localStorage.getItem('dci-store-epoch')) localStorage.setItem('dci-store-epoch', '4'); localStorage.setItem('dci-entries-view', JSON.stringify(v)); }"

# [3.36.0] what is stored for a release (pools, matrix, the choices of the import, the rows) is only remembered with
# ⚙ Settings → Cache → "Remember changes and import settings per release" (off by default); the tests written before it
# expect it on: REMEMBER = True switches it on before the script starts (unless the browser has it stored already); the cases
# of t_ui_settings.py 'cache' set REMEMBER = False to see the script's default
REMEMBER = True
REMEMBER_PRESET = "(on) => { if (!on || localStorage.getItem('dci-remember-on') !== null) return; if (!localStorage.getItem('dci-store-epoch')) localStorage.setItem('dci-store-epoch', '4'); localStorage.setItem('dci-remember-on', 'true'); }"


# [3.32.0] built-in rules switched off before the script starts, unless the browser has stored switched rules already
# (e.g. ['D022'] for the cases about periods and "choose", written before D022 placed what the days have in common)
RULES_OFF = []
RULES_PRESET = "(ids) => { if (localStorage.getItem('dci-rules-off') === null) localStorage.setItem('dci-rules-off', JSON.stringify(ids)); }"


def open_mb_edit(ctx, companion=True, gm_xhr=False, view='full'):
    pg = ctx.new_page()
    errs = errors_of(pg)
    pg.goto(f'https://musicbrainz.org/release/{REL}/edit-relationships')
    if view:
        pg.evaluate(VIEW_PRESET, view)
    pg.evaluate(ENTRIES_PRESET, ENTRIES_VIEW)
    pg.evaluate(REMEMBER_PRESET, REMEMBER)
    if RULES_OFF:
        pg.evaluate(RULES_PRESET, RULES_OFF)
    if companion:
        with_companion(pg)
    if gm_xhr:
        pg.add_script_tag(content=GM_XHR_SHIM)
    pg.add_script_tag(content=MAIN)
    return pg, errs


def open_discogs(ctx):
    pg = ctx.new_page()
    errs = errors_of(pg)
    pg.goto(f'https://www.discogs.com/release/{DISCOGS_ID}-Test-Band-Testalbum')
    with_companion(pg)
    return pg, errs


def open_bandcamp(ctx, url):
    """[3.17.0] A Bandcamp tab with the companion; it stays with the companion when it loads another page."""
    pg = ctx.new_page()
    errs = errors_of(pg)
    # only in the page itself, not in its frames (@noframes)
    pg.add_init_script(script="if (window.top === window) window.addEventListener('DOMContentLoaded', () => { for (const code of [%s, %s]) {"
                       " const s = document.createElement('script'); s.textContent = code; document.documentElement.appendChild(s); } });"
                       % (json.dumps(GM_SHIM), json.dumps(SYNC)))
    pg.goto(url)
    return pg, errs


def submit_staged(pg, leave_out=0):
    """As if "Enter edit" had been clicked: MusicBrainz gets what is staged (except the last \"leave_out\")."""
    added = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity1 && r.entity1.gid && r.entity0 && r.entity0.gid)"
                        ".map(r => ({lt: r.linkTypeID, e0: r.entity0.gid, e0t: r.entity0.entityType, e1: r.entity1.gid}))")
    keep = added[:len(added) - leave_out] if leave_out else added
    for r in keep:
        lt = LTS[r['lt']]
        et = r['e0t']
        MB_EXTRA.setdefault(r['e1'], []).append({'target-type': et, 'type': lt['name'], 'type-id': lt['gid'], 'attributes': [],
                                                 et: {'id': r['e0'], 'name': 'x'}})
    return added[len(keep):]


def open_mb_release(ctx):
    pg = ctx.new_page()
    errs = errors_of(pg)
    pg.goto(f'https://musicbrainz.org/release/{REL}')
    with_companion(pg)
    return pg, errs


def open_reset(pg):
    """[3.25.0] "↺ Reset all settings …" is in the settings (below their tabs): the settings open, then the question."""
    if pg.evaluate("!document.querySelector('[data-el=settings]') || document.querySelector('[data-el=settings]').hidden"):
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
        pg.wait_for_timeout(200)
    pg.click('[data-el=settings] [data-act=reset-open]')
    pg.wait_for_timeout(150)


def wait_for(pg, js, timeout=30):
    pg.wait_for_function(js, timeout=timeout * 1000)


def answer_media(pg, text=None, release=True, remember=False):
    """Media choice before the import (releases with several media): media as text ("1-2, 4"), release level, remember."""
    pg.wait_for_selector('[data-el=media] [data-mact=ok]', timeout=30000)
    if text is not None:
        pg.fill('[data-el=media] [data-mf=text]', text)
    box = pg.locator('[data-el=media] [data-mf=release]')
    if box.is_checked() != release:
        box.click()
    if remember:
        pg.check('[data-el=media] [data-mf=remember]')
    pg.click('[data-el=media] [data-mact=ok]')


def open_dashboard(pg, media=None):
    """Opens the dashboard and waits until the import is checked; with several media the choice is answered
    (default: all media with the release level, as before; media=False leaves the dialog open)."""
    pg.click('#dci-open')
    if MEDIA and len(MEDIA) > 1 and media is not False:
        answer_media(pg, **(media or {}))
    if media is False:
        return
    wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete|Prüfungen abgeschlossen/.test(li.textContent))", 60)


def src_menu(pg, act=None):
    """[3.26.0] The menu "Source ▾" in the head (a linked source, another source, paste text, the order of the sources,
    Bandcamp, "Leave out the about text", delete the stored import): opened if closed, then `act` clicked in it."""
    if pg.evaluate("(() => { const m = document.querySelector('#dci-overlay .dci-srcmenu'); return !m || m.hidden; })()"):
        pg.click('#dci-overlay [data-act=srcmenu]')
        pg.wait_for_timeout(150)
    if act:
        pg.click(f'#dci-overlay .dci-srcmenu [data-act={act}]')
        pg.wait_for_timeout(150)


def open_supp(pg):
    """[3.26.0] "+ Supplement" in the head opens the bar "Supplement with" (open anyway while a supplement is loaded)."""
    if not pg.evaluate("!!document.querySelector('#dci-overlay .dci-suppbar')"):
        pg.click('#dci-overlay [data-act=supp-open]')
        pg.wait_for_timeout(150)


def toggle_place(pg):
    """[3.26.0] Window ⇄ in the page with the switch of the page bar (the head of the dashboard has none any more)."""
    pg.locator('#dci-launcher [data-place][aria-pressed=false]').evaluate('b => b.click()')
    pg.wait_for_timeout(300)


def open_settings(pg, tab=None):
    """⚙ Settings opened (if closed), at the tab `tab` if given ([3.26.0] the language is only there)."""
    if pg.evaluate("!document.querySelector('[data-el=settings]') || document.querySelector('[data-el=settings]').hidden"):
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
        pg.wait_for_timeout(200)
    if tab:
        pg.click(f'[data-el=settings] .dci-set-tab[data-topic={tab}]')
        pg.wait_for_timeout(150)


def nav_switch(pg, attr):
    """[3.28.0] A switch of the navigation (data-dg-artwork, data-click-toggle, data-keep-marks …): only in ⚙ Settings →
    Discogs and Bandcamp view now (the bar below "Import credits …" has the status only)."""
    open_settings(pg, 'discogs')
    pg.locator(f'[data-el=settings] [{attr}]').evaluate('b => b.click()')
    pg.wait_for_timeout(150)
