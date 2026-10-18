"""Credits Importer 3.17.4: the source next to the status in the navigation bar (collected item 22), and a link at each
name suggestion (collected item 24).
A) Bandcamp loaded, no Bandcamp tab: the bar above "Import credits …" says "Bandcamp view: no Bandcamp tab", links the
   album ("↗ Bandcamp", a new tab) and has "open in background", which opens it in the background.
B) A Bandcamp tab on another album: the bar offers "Load the release there", which loads the album there.
C) Discogs loaded: the bar links the Discogs release.
D) Each suggestion of a name has a small ↗ that opens its MusicBrainz entry in a new tab (artist, label)."""
from playwright.sync_api import sync_playwright
import harness as H

BAND = 'https://testband.bandcamp.com'
ALBUM = f'{BAND}/album/testalbum'
OTHER = f'{BAND}/album/other'
H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
JANE = H.uid('dddddddd', 77)
K7 = H.uid('eeeeeeee', 77)
H.MB_SEARCH.setdefault('artist', []).append({'id': JANE, 'name': 'Jane Roe', 'aliases': []})
H.MB_SEARCH.setdefault('label', []).append({'id': K7, 'name': 'Pub House', 'aliases': []})
TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': 'Test Band – guitar\nMixed by Jane Roe\nPublished by Pub House'},
                               'trackinfo': TRACKS}, ALBUM)
for t in TRACKS:
    H.BC_PAGES[f'{BAND}{t["title_link"]}'] = H.bc_html({'artist': 'Test Band', 'album_url': '/album/testalbum', 'current': {'title': t['title'], 'credits': ''},
                                                        'trackinfo': [t]}, f'{BAND}{t["title_link"]}')
H.BC_PAGES[OTHER] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Other', 'credits': 'Bass: Nobody'}, 'trackinfo': TRACKS[:1]}, OTHER)
orig_ws = H.ws_release
DIGITAL = {'on': True}


def ws():
    d = orig_ws()
    if DIGITAL['on']:
        d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}})
        for m in d['media']:
            m['format'] = 'Digital Media'
    return d


H.ws_release = ws
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
BAR = """(() => { const s = document.querySelector('#dci-controls .dci-syncstatus'); if (!s) return null;
  const a = s.querySelector('a.dci-srclink');
  return [s.textContent.replace(/\\s+/g, ' ').trim(), a ? [a.textContent.trim(), a.href, a.target] : null, [...s.querySelectorAll('button')].map(b => b.dataset.act || '')]; })()"""
SUGG = """(() => [...document.querySelectorAll('.dci-suggitem')].map(x => [x.querySelector('.dci-suggbtn').textContent.trim().slice(0, 12),
  (x.querySelector('a.dci-sugglink') || {}).href || '', (x.querySelector('a.dci-sugglink') || {}).target || '']))()"""
results = []


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
    pg, errs = H.open_mb_edit(ctx, companion=True, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.wait_for_timeout(3500)
    # A)
    a1 = pg.evaluate(BAR)
    pg.locator('#dci-controls [data-act=sync-open]').evaluate('b => b.click()')  # the dashboard window may cover the bar
    pg.wait_for_timeout(300)
    opened = pg.evaluate("window.__opened || []")
    print('A) Leiste:', a1, '| geöffnet:', opened)
    results.append(a1 is not None and a1[0].startswith('Bandcamp view: no Bandcamp tab') and a1[1] is not None and a1[1][0] == '↗ Bandcamp'
                   and a1[1][1] == ALBUM and a1[1][2] == '_blank' and 'sync-open' in a1[2] and ALBUM in opened)
    # D) suggestions
    d1 = pg.evaluate(SUGG)
    print('D) Vorschläge:', d1)
    results.append(['Jane Roe', f'https://musicbrainz.org/artist/{JANE}', '_blank'] in d1 and any(x[1] == f'https://musicbrainz.org/label/{K7}' for x in d1))
    # B)
    bc, bcerr = H.open_bandcamp(ctx, OTHER)
    H.wait_for(pg, "(document.querySelector('#dci-controls .dci-syncstatus') || {}).textContent.includes('on another page')", 20)
    b1 = pg.evaluate(BAR)
    pg.locator('#dci-controls [data-act=sync-load]').evaluate('b => b.click()')
    poll(bc, f"location.href === '{ALBUM}'")
    H.wait_for(pg, "(document.querySelector('#dci-controls .dci-syncstatus') || {}).textContent.includes('connected')", 20)
    b2 = pg.evaluate(BAR)
    print('B) andere Seite:', b1, '| danach:', b2)
    results.append('sync-load' in b1[2] and b2[0].startswith('Bandcamp view: connected') and b2[1] is not None)
    print('Fehler:', real(errs), real(bcerr))
    results.append(not real(errs) and not real(bcerr))
    b.close()
    # C) Discogs
    DIGITAL['on'] = False
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.wait_for_timeout(3500)
    c1 = pg.evaluate(BAR)
    print('C) Discogs:', c1)
    results.append(c1 is not None and c1[1] is not None and c1[1][0] == '↗ Discogs' and c1[1][1] == f'https://www.discogs.com/release/{H.DISCOGS_ID}')
    print('Fehler:', real(errs))
    results.append(not real(errs))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
