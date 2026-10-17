"""Credits Importer 3.17.2: liner notes in Bandcamp's "about" text (collected item 19).
A) In Node (BANDCAMP.linerNotes): prose of at least five sentences (over several paragraphs) and a name below it – after
   an empty line ("— Jane Roe, Berlin, May 2019"), on the line right below ("Jane Roe"), or at the end of the last line
   after a sign ("… our music. ~ Jane Roe") – gives the name; four sentences, a last line that is no name ("Special
   thanks", "Thanks to everyone"), a name after a sign without a finished sentence before it, and the "about" text of
   "Invisible Places" give nothing.
B) In the dashboard: an entry "Jane Roe" with the row "Liner Notes" (liner notes, release level) that says "From the
   “about” text"; MusicBrainz artists of that name only as suggestions (nothing assigned); the date by the name in the
   date pool as a suggestion named for the liner notes.
C) "Leave out the about text": the row hidden and the date out of the pool; ticked off again, both back.
D) With the companion: the row jumps to the name's line in the "about" text (only that sentence, no mark)."""
import json
import subprocess
from playwright.sync_api import sync_playwright
import harness as H

PROSE = ('This record was a long time coming. We met in a cold basement in the winter of 2017. The songs grew slowly, '
         'one evening at a time.\n\nNone of us knew where it would lead. But every take taught us something new.\n'
         'Listen to it loud, and listen to it twice.')
REAL = ('The music on this album was recorded in September and October 2026. It is an approach to ambient music with a more '
        'meditative and “earthty” character. The music originally appeared in Home Concert 85, but was re-recorded with attention '
        'to detail, dynamic mixing and sound design.\nThe last track, “Neptune’s Dream”, was previously released as a '
        'digital-only single and was remastered for this release.')
CASES = {
    'blank line': PROSE + '\n\n— Jane Roe, Berlin, May 2019',
    'line below': PROSE + '\nJane Roe',
    'end of line': PROSE[:-1] + '. ~ Jane Roe',
    'four sentences': 'One two three. Four five six. Seven eight nine. Ten eleven twelve.\n\nJane Roe',
    'special thanks': PROSE + '\n\nSpecial Thanks',
    'thanks to everyone': PROSE + '\n\nThanks to everyone',
    'no sentence before': PROSE + ' And the last one – Neptune Dream',
    'invisible places': REAL,
}
NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const cases = JSON.parse(process.argv[2]);
const out = {};
for (const [k, text] of Object.entries(cases)) {
  const r = m.SOURCES.bandcamp.linerNotes(text);
  out[k] = r ? [r.name, r.line, r.part, r.pi] : null;
}
console.log(JSON.stringify(out));
"""
results = []
js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(CASES)], capture_output=True, text=True)
if js.returncode:
    print(js.stderr[-1500:])
got = json.loads(js.stdout) if not js.returncode else {}
for k, v in got.items():
    print(f'A) {k}:', v)
results.append(got.get('blank line') == ['Jane Roe', '— Jane Roe, Berlin, May 2019', '— Jane Roe, Berlin, May 2019', 0]
               and got.get('line below') == ['Jane Roe', 'Jane Roe', 'Jane Roe', 0]
               and got.get('end of line') == ['Jane Roe', 'Listen to it loud, and listen to it twice. ~ Jane Roe', 'Jane Roe', 1]
               and all(got.get(k) is None for k in ['four sentences', 'special thanks', 'thanks to everyone', 'no sentence before', 'invisible places']))

BAND = 'https://testband.bandcamp.com'
ALBUM = f'{BAND}/album/testalbum'
H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
H.MB_SEARCH.setdefault('artist', []).append({'id': H.uid('dddddddd', 77), 'name': 'Jane Roe', 'aliases': []})
TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': 'Test Band – guitar', 'about': CASES['blank line']},
                               'trackinfo': TRACKS}, ALBUM)
for t in TRACKS:
    H.BC_PAGES[f'{BAND}{t["title_link"]}'] = H.bc_html({'artist': 'Test Band', 'album_url': '/album/testalbum', 'current': {'title': t['title'], 'credits': ''},
                                                        'trackinfo': [t]}, f'{BAND}{t["title_link"]}')
orig_ws = H.ws_release


def ws():
    d = orig_ws()
    d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}})
    for m in d['media']:
        m['format'] = 'Digital Media'
    return d


H.ws_release = ws
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
ENTRY = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Jane Roe');
  if (!g) return null; const tr = g.querySelector('tr.dci-row'); const lv = tr && tr.querySelector('[data-act=level][aria-pressed=true]');
  return [g.className.match(/dci-st-(\\w+)/)[1], tr ? tr.querySelector('.dci-drole').textContent.trim() : '', tr ? (tr.querySelector('[data-f=type]') || {}).value : '',
    lv ? lv.dataset.level : '', [...g.querySelectorAll('.dci-sub')].map(x => x.textContent.trim()).filter(t => /about/.test(t)),
    [...g.querySelectorAll('[data-act=name-use]')].length, !!(tr && tr.offsetParent)]; })()"""
POOL = f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => [d.name, d.begin && [d.begin.year, d.begin.month]])"


def poll(pg, js, timeout=20):
    for _ in range(timeout * 5):
        try:
            if pg.evaluate(js):
                return True
        except Exception:
            pass
        pg.wait_for_timeout(200)
    raise TimeoutError(js)


real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    bc, bcerr = H.open_bandcamp(ctx, ALBUM)
    pg, errs = H.open_mb_edit(ctx, companion=True, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.wait_for_timeout(1500)
    b1 = pg.evaluate(ENTRY)
    pool = pg.evaluate(POOL)
    print('B) Eintrag:', b1, '| Pool:', pool)
    results.append(b1 is not None and b1[1] == 'Liner Notes' and b1[3] == 'release' and b1[4] == ['From the “about” text'] and b1[5] >= 1
                   and b1[0] != 'linked' and ['Liner notes – Jane Roe', [2019, 5]] in pool)
    # D) the jump: the sentence with the name, no mark in the about text
    rid = pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Jane Roe'); return g.querySelector('tr.dci-row').dataset.row; })()")
    pg.locator(f'tr[data-row="{rid}"] .dci-drole').click()
    poll(bc, "!!document.querySelector('.dci-bc-hl')")
    bc.wait_for_timeout(300)
    d1 = [bc.evaluate("[...document.querySelectorAll('.dci-bc-hl')].map(x => x.textContent).join('')"), bc.evaluate("document.querySelectorAll('.tralbum-about .dci-dg-mark').length")]
    print('D) Sprung:', d1)
    results.append(d1 == ['— Jane Roe, Berlin, May 2019', 0])
    # C) leave out the about text
    pg.locator('[data-f=about-off]').check()
    pg.wait_for_timeout(800)
    c1 = [pg.evaluate(ENTRY), pg.evaluate(POOL)]
    pg.locator('[data-f=about-off]').uncheck()
    pg.wait_for_timeout(800)
    c2 = [pg.evaluate(ENTRY), pg.evaluate(POOL)]
    print('C) ausgelassen:', c1, '| wieder da:', c2)
    results.append((c1[0] is None or not c1[0][6] or c1[0][3] == 'skip') and not any(n == 'Liner notes – Jane Roe' for n, _ in c1[1])
                   and c2[0] is not None and c2[0][3] == 'release' and ['Liner notes – Jane Roe', [2019, 5]] in c2[1])
    print('Fehler:', real(errs), real(bcerr))
    results.append(not real(errs) and not real(bcerr))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
