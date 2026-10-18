"""Credits Importer 3.19.0: "open relationship editor and start import dashboard" in the release editor (collected item 18).
A) "Edit release" with a Discogs link: the tick stands next to "Enter edit" only on the tab "Edit note" (where
   MusicBrainz shows that button), off at first; its tooltip names the link.
B) Not ticked: "Enter edit" leads to the release page, which stays.
C) Ticked (remembered): "Enter edit" → release page → "Edit relationships", the dashboard opens by itself and loads the
   Discogs release; the log says it was started from the release editor.
D) An error while submitting (MusicBrainz's "in progress" back to false): nothing is noted, the release page stays.
E) "Add release" without a link: no tick; a Bandcamp album typed into "External links" brings it (in the dashboard
   language, here German). After "Enter edit" the new release's relationship editor loads that album at once, though
   MusicBrainz does not have the link yet.
F) Other pages of a release (e.g. its cover art): the script adds nothing."""
from playwright.sync_api import sync_playwright
import harness as H

BAND = 'https://testband.bandcamp.com'
ALBUM = f'{BAND}/album/testalbum'
H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': 'Mixed by Jane Roe'}, 'trackinfo': TRACKS}, ALBUM)
for t in TRACKS:
    H.BC_PAGES[f'{BAND}{t["title_link"]}'] = H.bc_html({'artist': 'Test Band', 'album_url': '/album/testalbum', 'current': {'title': t['title'], 'credits': ''},
                                                        'trackinfo': [t]}, f'{BAND}{t["title_link"]}')
EDIT = f'https://musicbrainz.org/release/{H.REL}/edit'
RELPAGE = f'https://musicbrainz.org/release/{H.REL}'
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
TICK = """(() => { const b = document.getElementById('dci-after-edit'); if (!b) return null;
  return { shown: getComputedStyle(b).display !== 'none', on: b.querySelector('input').checked, text: b.textContent.trim(), title: b.title,
    before: b.nextElementSibling && b.nextElementSibling.id }; })()"""
results = []


def tick(pg):
    return pg.evaluate(TICK)


def at_editor(pg, url=EDIT):
    if pg.url != url:
        pg.goto(url)
    pg.wait_for_selector('#dci-after-edit', state='attached', timeout=15000)
    pg.wait_for_timeout(300)


def path(pg):
    return pg.evaluate('location.pathname')


real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_any(ctx, EDIT)
    pg.on('dialog', lambda d: d.accept())
    # A)
    at_editor(pg)
    a1 = tick(pg)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(400)
    a2 = tick(pg)
    print('A) Reiter Release-Info:', a1)
    print('   Reiter Edit note:', a2)
    results.append(a1 is not None and not a1['shown'] and a2['shown'] and not a2['on'] and a2['before'] == 'enter-edit'
                   and a2['text'] == 'open relationship editor and start import dashboard' and 'Discogs 1234' in a2['title'])
    # B) not ticked
    pg.click('#enter-edit')
    pg.wait_for_url(RELPAGE, timeout=10000)
    pg.wait_for_timeout(1500)
    b1 = [path(pg), pg.evaluate("sessionStorage.getItem('dci-after-edit-go')")]
    print('B) ohne Haken:', b1)
    results.append(b1 == [f'/release/{H.REL}', None])
    # C) ticked
    at_editor(pg)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(300)
    pg.locator('#dci-after-edit input').check()
    stored = pg.evaluate("localStorage.getItem('dci-after-edit')")
    pg.goto(RELPAGE)
    at_editor(pg)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(300)
    kept = tick(pg)['on']
    pg.click('#enter-edit')
    pg.wait_for_url(f'**/release/{H.REL}/edit-relationships', timeout=15000)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.wait_for_timeout(800)
    c1 = [x for x in pg.evaluate(LOGS) if 'release editor' in x or 'Discogs release' in x.lower() or 'Discogs 1234' in x]
    src = pg.evaluate("(document.querySelector('[data-el=source]') || document.body).textContent.includes('Discogs 1234')")
    print('C) gemerkt:', stored, kept, '| Protokoll:', c1, '| Discogs geladen:', src, '| Seite:', path(pg))
    results.append(stored == 'true' and kept and any('Started from the release editor' in x and 'Discogs 1234' in x for x in c1)
                   and pg.evaluate("!document.getElementById('dci-overlay').hidden") and pg.evaluate("sessionStorage.getItem('dci-autostart')") is None)
    # D) an error while submitting
    pg.goto(EDIT)
    at_editor(pg)
    pg.evaluate("__tab('edit-note'); window.__fail = true")
    pg.wait_for_timeout(300)
    pg.click('#enter-edit')
    pg.wait_for_timeout(800)
    d1 = pg.evaluate("sessionStorage.getItem('dci-after-edit-go')")
    pg.goto(RELPAGE)
    pg.wait_for_timeout(1500)
    print('D) Fehler beim Abschicken – vorgemerkt:', d1, '| Seite:', path(pg))
    results.append(d1 is None and path(pg) == f'/release/{H.REL}')
    # E) Add release, a Bandcamp album typed in, German
    pg.evaluate("localStorage.setItem('dci-lang', JSON.stringify('de'))")
    pg.goto('https://musicbrainz.org/release/add')
    at_editor(pg, 'https://musicbrainz.org/release/add')
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(300)
    e1 = tick(pg)
    pg.evaluate("__tab('information')")
    pg.fill('#external-links-editor input.value', ALBUM)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(400)
    e2 = tick(pg)
    print('E) ohne Link:', e1['shown'], '| mit Bandcamp:', e2)
    pg.click('#enter-edit')
    pg.wait_for_url(f'**/release/{H.REL}/edit-relationships', timeout=15000)
    H.wait_for(pg, f"{LOGS}.some(x => /Quelle im Release-Editor/.test(x))", 60)
    H.wait_for(pg, f"{LOGS}.filter(x => /Import (complete|abgeschlossen)/.test(x)).length >= 2", 60)
    pg.wait_for_timeout(800)
    e3 = [x for x in pg.evaluate(LOGS) if 'Release-Editor' in x]
    bc = pg.evaluate("[...document.querySelectorAll('.dci-gname strong')].map(s => s.textContent.trim())")
    print('   Einträge:', bc)
    print('   Protokoll:', e3)
    results.append(not e1['shown'] and e2['shown'] and e2['on'] and e2['text'] == 'Beziehungs-Editor öffnen und Import-Dashboard starten'
                   and 'Bandcamp testband.bandcamp.com/album/testalbum' in e2['title']
                   and any('Quelle im Release-Editor eingetragen' in x and 'testband.bandcamp.com/album/testalbum' in x for x in e3) and 'Jane Roe' in bc)
    pg.evaluate("localStorage.removeItem('dci-lang'); localStorage.removeItem('dci-after-edit')")
    # F) another page of the release
    pg.goto(f'https://musicbrainz.org/release/{H.REL}/cover-art')
    pg.wait_for_timeout(1000)
    f1 = pg.evaluate("[!!document.getElementById('dci-pagebar'), !!document.getElementById('dci-after-edit'), !!document.getElementById('dci-styles')]")
    print('F) Cover-Art-Seite:', f1)
    results.append(f1 == [False, False, False])
    print('Fehler:', real(errs))
    results.append(not real(errs))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
