"""Credits Importer 3.19.0 / 3.23.0: start the import from the release editor (collected items 18, 50). [3.23.0] Instead
of the tick the button "Enter edit & import credits" next to "Enter edit" (orange, MusicBrainz's button otherwise;
Ctrl+Alt+Enter; setting, on).
A) "Edit release" with a Discogs link: the button stands right after "Enter edit" only on the tab "Edit note" (where
   MusicBrainz shows that button), orange, its tooltip names the link and the keys; no tick any more (the old one is
   removed from the storage).
B) "Enter edit": the release page, which stays.
C) "Enter edit & import credits" → release page → "Edit relationships", the dashboard opens by itself and loads the
   Discogs release; the log says it was started from the release editor. C2) Ctrl+Alt+Enter in the edit note: the same.
D) An error while submitting (MusicBrainz's "in progress" back to false): nothing is noted, the release page stays;
   a plain "Enter edit" afterwards stays a plain one.
E) "Add release" without a link: no button; a Bandcamp album typed into "External links" brings it (in the dashboard
   language, here German: "Enter edit & Credits importieren"). After it the new release's relationship editor loads that
   album at once, though MusicBrainz does not have the link yet.
F) The setting off ("dci-after-edit-btn" false): no button. G) Other pages of a release (e.g. its cover art): nothing."""
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
BTN = """(() => { const b = document.getElementById('dci-enter-import'); if (!b) return null;
  return { shown: getComputedStyle(b).display !== 'none', text: b.textContent.trim(), title: b.title, prev: b.previousElementSibling && b.previousElementSibling.id,
    bg: getComputedStyle(b).backgroundColor, cls: b.className, tick: !!document.querySelector('#dci-after-edit input') }; })()"""
results = []


def btn(pg):
    return pg.evaluate(BTN)


def at_editor(pg, url=EDIT):
    if pg.url != url:
        pg.goto(url)
    pg.wait_for_selector('#dci-enter-import', state='attached', timeout=15000)
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
    pg.evaluate("localStorage.setItem('dci-after-edit', 'true')")
    pg.reload()
    at_editor(pg)
    a1 = btn(pg)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(400)
    a2 = btn(pg)
    old = pg.evaluate("localStorage.getItem('dci-after-edit')")
    print('A) Reiter Release-Info:', a1)
    print('   Reiter Edit note:', a2, '| alter Haken gespeichert:', old)
    results.append(a1 is not None and not a1['shown'] and a2['shown'] and a2['prev'] == 'enter-edit' and a2['text'] == 'Enter edit & import credits'
                   and a2['bg'] == 'rgb(235, 116, 59)' and a2['cls'] == 'positive' and not a2['tick'] and 'Discogs 1234' in a2['title']
                   and 'Ctrl+Alt+Enter' in a2['title'] and old is None)
    # B) "Enter edit"
    pg.click('#enter-edit')
    pg.wait_for_url(RELPAGE, timeout=10000)
    pg.wait_for_timeout(1500)
    b1 = [path(pg), pg.evaluate("sessionStorage.getItem('dci-after-edit-go')")]
    print('B) Enter edit:', b1)
    results.append(b1 == [f'/release/{H.REL}', None])
    # C) "Enter edit & import credits"
    pg.goto(EDIT)
    at_editor(pg)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(300)
    pg.click('#dci-enter-import')
    pg.wait_for_url(f'**/release/{H.REL}/edit-relationships', timeout=15000)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.wait_for_timeout(800)
    c1 = [x for x in pg.evaluate(LOGS) if 'release editor' in x or 'Discogs release' in x.lower() or 'Discogs 1234' in x]
    print('C) Protokoll:', c1, '| Seite:', path(pg))
    results.append(any('Started from the release editor' in x and 'Discogs 1234' in x for x in c1)
                   and pg.evaluate("!document.getElementById('dci-overlay').hidden") and pg.evaluate("sessionStorage.getItem('dci-autostart')") is None)
    # C2) Ctrl+Alt+Enter in the edit note
    pg.goto(EDIT)
    at_editor(pg)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(300)
    pg.focus('#edit-note-text')
    pg.keyboard.press('Control+Alt+Enter')
    pg.wait_for_url(f'**/release/{H.REL}/edit-relationships', timeout=15000)
    H.wait_for(pg, f"{LOGS}.some(x => /Started from the release editor/.test(x))", 60)
    print('C2) Strg+Alt+Enter:', path(pg))
    results.append(path(pg) == f'/release/{H.REL}/edit-relationships')
    # D) an error while submitting, then a plain "Enter edit"
    pg.goto(EDIT)
    at_editor(pg)
    pg.evaluate("__tab('edit-note'); window.__fail = true")
    pg.wait_for_timeout(300)
    pg.click('#dci-enter-import')
    pg.wait_for_timeout(800)
    d1 = pg.evaluate("sessionStorage.getItem('dci-after-edit-go')")
    pg.evaluate("window.__fail = false")
    pg.click('#enter-edit')
    pg.wait_for_url(RELPAGE, timeout=10000)
    pg.wait_for_timeout(1500)
    print('D) Fehler beim Abschicken – vorgemerkt:', d1, '| danach Enter edit – Seite:', path(pg))
    results.append(d1 is None and path(pg) == f'/release/{H.REL}')
    # E) Add release, a Bandcamp album typed in, German
    pg.evaluate("localStorage.setItem('dci-lang', JSON.stringify('de'))")
    pg.goto('https://musicbrainz.org/release/add')
    at_editor(pg, 'https://musicbrainz.org/release/add')
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(300)
    e1 = btn(pg)
    pg.evaluate("__tab('information')")
    pg.fill('#external-links-editor input.value', ALBUM)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(400)
    e2 = btn(pg)
    print('E) ohne Link:', e1['shown'], '| mit Bandcamp:', e2)
    pg.click('#dci-enter-import')
    pg.wait_for_url(f'**/release/{H.REL}/edit-relationships', timeout=15000)
    H.wait_for(pg, f"{LOGS}.some(x => /Quelle im Release-Editor/.test(x))", 60)
    H.wait_for(pg, f"{LOGS}.filter(x => /Import (complete|abgeschlossen)/.test(x)).length >= 2", 60)
    pg.wait_for_timeout(800)
    e3 = [x for x in pg.evaluate(LOGS) if 'Release-Editor' in x]
    bc = pg.evaluate("[...document.querySelectorAll('.dci-gname strong')].map(s => s.textContent.trim())")
    print('   Einträge:', bc)
    print('   Protokoll:', e3)
    results.append(not e1['shown'] and e2['shown'] and e2['text'] == 'Enter edit & Credits importieren' and 'Strg+Alt+Enter' in e2['title']
                   and 'Bandcamp testband.bandcamp.com/album/testalbum' in e2['title']
                   and any('Quelle im Release-Editor eingetragen' in x and 'testband.bandcamp.com/album/testalbum' in x for x in e3) and 'Jane Roe' in bc)
    pg.evaluate("localStorage.removeItem('dci-lang')")
    # F) the setting off
    pg.evaluate("localStorage.setItem('dci-after-edit-btn', 'false')")
    pg.goto(EDIT)
    at_editor(pg)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(400)
    f1 = btn(pg)
    print('F) Einstellung aus:', f1['shown'])
    results.append(not f1['shown'])
    pg.evaluate("localStorage.removeItem('dci-after-edit-btn')")
    # G) another page of the release
    pg.goto(f'https://musicbrainz.org/release/{H.REL}/cover-art')
    pg.wait_for_timeout(1000)
    g1 = pg.evaluate("[!!document.getElementById('dci-pagebar'), !!document.getElementById('dci-enter-import'), !!document.getElementById('dci-styles')]")
    print('G) Cover-Art-Seite:', g1)
    results.append(g1 == [False, False, False])
    print('Fehler:', real(errs))
    results.append(not real(errs))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
