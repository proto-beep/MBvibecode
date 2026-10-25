"""Credits Importer 3.30.7: the members of a band (collected item 96; https://visionfortune.bandcamp.com/album/iii).
A) A pasted text, the release's artist Vision Fortune: "Vision Fortune are AC Williams, Alex Townend and Andres Ayerbe" –
   each of the three a performer (S041, T043); "The band is now a trio." and "Vision Fortune is back with a new album."
   give no entry.
B) Bandcamp, the sentence in the "about" text (which otherwise gives only places): the three performers again; "Vision
   Fortune is back with a new album." there neither."""
from playwright.sync_api import sync_playwright
import harness as H

ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', (tr.querySelector('[data-tcount]') || {}).textContent]; })])))()"""
MEMBERS = ['AC Williams', 'Alex Townend', 'Andres Ayerbe']
VF = (H.uid('dddddddd', 60), 'Vision Fortune')
H.ARTISTS[3060] = VF
H.RELEASE_AC[:] = [(VF[0], 'Vision Fortune', 'Vision Fortune', '')]
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(600)
    H.src_menu(pg, 'text-open')
    pg.fill('[data-f=text-src]', 'Vision Fortune are AC Williams, Alex Townend and Andres Ayerbe\nThe band is now a trio.\nVision Fortune is back with a new album.')
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(1200)
    g = pg.evaluate(ROWS)
    a1 = {n: [x[1] for x in g.get(n, [])] for n in MEMBERS}
    print('A) Text:', a1, '| Einträge:', list(g))
    results.append(all(v == ['performer'] for v in a1.values()) and not any(('trio' in k or 'back' in k) for k in g))
    print('Fehler:', errs)
    results.append(not errs)
    b.close()

# B) Bandcamp, the "about" text
BAND = 'https://visionfortune.bandcamp.com'
ALBUM = f'{BAND}/album/iii'
H.BC_ARTISTS[BAND + '/'] = VF
TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
ABOUT = ('Vision Fortune is back with a new album.\nRecorded in a cottage in rural Wales.\n'
         'Vision Fortune are AC Williams, Alex Townend and Andres Ayerbe')
H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Vision Fortune', 'current': {'title': 'III', 'credits': '', 'about': ABOUT, 'release_date': '02 Oct 2026 00:00:00 GMT'},
                               'trackinfo': TRACKS}, ALBUM)
for t in TRACKS:
    url = f'{BAND}{t["title_link"]}'
    H.BC_PAGES[url] = H.bc_html({'artist': 'Vision Fortune', 'album_url': '/album/iii', 'current': {'title': t['title'], 'credits': ''}, 'trackinfo': [t]}, url)
orig_ws = H.ws_release


def ws(full=False):
    d = orig_ws(full)
    d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
    for m in d['media']:
        m['format'] = 'Digital Media'
    return d


H.ws_release = ws
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    pg.click('#dci-open')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
    pg.wait_for_timeout(1500)
    g = pg.evaluate(ROWS)
    b1 = {n: [x[1] for x in g.get(n, [])] for n in MEMBERS}
    print('B) Bandcamp „about“:', b1, '| Einträge:', list(g))
    results.append(all(v == ['performer'] for v in b1.values()) and not any('back' in k for k in g))
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
