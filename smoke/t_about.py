"""Import 3.7.0: the "about" text of a Bandcamp album: "recorded at Loft in Cologne, june 16/17 2018".
A) The place: an entry "Loft" (Cologne) with "Recorded At"; MusicBrainz places of that name are suggested only in
   that area (a "Loft" in New York is not); the about text's prose is not read as credits and not listed as not
   recognized.
B) The date: "june 16/17 2018" (and "16/17 June 2018") – two days in a row, in the date pool as a period
   (2018-06-16 – 2018-06-17), which can be split into the single days as with "June 16 & 17, 2018".
C) "Loft, Cologne" in the credits works the same way.
D) A private place is no place: "mixed at home in Oslo" gives no entry "home" (and is not listed as not recognized).
E) What follows "at" without being a place gives no entry either (3.13.1): "recorded at the same time as the video",
   "overdubs at last, in the summer of 2018"."""
from playwright.sync_api import sync_playwright
import harness as H

ALBUM = 'https://testband.bandcamp.com/album/swift'
H.MB_SEARCH['place'] = [
    {'id': H.uid('eeeeeeee', 60), 'name': 'Loft', 'disambiguation': '', 'area': {'name': 'Cologne'}, 'score': 100},
    {'id': H.uid('eeeeeeee', 61), 'name': 'The Loft', 'disambiguation': '', 'area': {'name': 'New York'}, 'score': 100},
    {'id': H.uid('eeeeeeee', 62), 'name': 'Loft', 'disambiguation': 'club', 'area': {'name': 'New York'}, 'score': 100},
    {'id': H.uid('eeeeeeee', 63), 'name': 'Studio Nord', 'disambiguation': '', 'area': {'name': 'Bremen'}, 'score': 100},
]
H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Test Band', 'current': {
    'title': 'Swift', 'credits': 'Bass Man – bass\nMastered at Studio Nord, Bremen',
    'about': 'An evening of improvised music, three friends, one room.\nrecorded at Loft in Cologne, june 16/17 2018\nmixed at home in Oslo, july 2018\nrecorded at the same time as the video\noverdubs recorded at last, in the summer of 2018'},
    'trackinfo': [{'track_num': i + 1, 'title': t} for i, t in enumerate(H.TITLES)]})
orig_ws = H.ws_release


def ws():
    d = orig_ws()
    d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
    for m in d['media']:
        m['format'] = 'Digital Media'
    return d


H.ws_release = ws
GROUPS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(),
  [[...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim()), [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim())]])))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    pg.click('#dci-open')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
    pg.wait_for_timeout(1000)
    g = pg.evaluate(GROUPS)
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    stored = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => [d.name, JSON.stringify(d.begin), JSON.stringify(d.end)].join(' '))")
    for k, v in g.items():
        print('   ', k, v)
    print('   nicht erkannt:', unrec, '| Pool:', stored)
    loft = next((v for k, v in g.items() if k.startswith('Place Loft') or 'Loft (Cologne)' in k), None)
    nord = next((v for k, v in g.items() if 'Studio Nord (Bremen)' in k), None)
    ok_a = loft is not None and loft[0] == ['Recorded At'] and loft[1] == ['Loft (Cologne) – place'] and not unrec
    ok_b = any('{"year":2018,"month":6,"day":16} {"year":2018,"month":6,"day":17}' in s for s in stored)
    ok_c = nord is not None and nord[0] == ['Mastered At'] and nord[1] == ['Studio Nord (Bremen) – place']
    ok_d = not any('home' in k.lower() for k in g)
    ok_e = not any(w in k.lower() for k in g for w in ('same time', 'last'))
    print('A)', ok_a, '| B)', ok_b, '| C)', ok_c, '| D)', ok_d, '| E)', ok_e)
    results += [ok_a, ok_b, ok_c, ok_d, ok_e]
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
