"""Credits Importer 3.19.1: Harmony's "Release Actions" get the link "Edit relationships with Credits Importer" (collected
item 29). A release imported with Harmony goes on to Harmony's page after "Enter edit" (Harmony seeds "redirect_uri").
[3.19.2] With the setting "Imported with Harmony: open it in a background tab" (on) the start is offered there too (items
32, 38); [3.23.0] by the button "Enter edit & import credits" instead of the tick (item 50).
A) Release editor seeded by Harmony, setting off: no button, the note "for the Credits Importer: … use … on Harmony";
   "Enter edit" leads to Harmony's "Release Actions" with the new MBID, nothing opens by itself.
A2) Setting on (default): the button, its tooltip names the background tab; it → Harmony's page, which opens the
   relationship editor in a background tab (once, the sign #dci-open taken off) and says so next to its link.
A3) An error while submitting with the button: the return address is as before (no sign).
B) There, right below "Add cover art": the action "Edit relationships with Credits Importer" (Harmony's look: icon,
   link), to "Edit relationships" of the release in a new tab, with the Bandcamp album Harmony looked up.
C) The link: "Edit relationships" opens, the dashboard starts by itself and loads that album at once (MusicBrainz does not
   have the link yet); the # is taken off the address.
D) Harmony's page without a release: no link; "discogs=1234" gives the Discogs release; another tool's "redirect_uri":
   the note names its host.
E) The settings (topic Sources): the button (on) and the background tab (on); "↺" of the topic sets them back."""
from urllib.parse import quote
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
HARMONY = 'https://harmony.pulsewidth.org.uk/release/actions'
H.EDITOR_LINKS['add'] = [ALBUM]
H.EDITOR_REDIRECT['add'] = f'{HARMONY}?bandcamp=testband%2Ftestalbum'
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
TICK = """(() => { const b = document.getElementById('dci-after-edit'); const g = document.getElementById('dci-enter-import'); if (!b || !g) return null;
  return { shown: getComputedStyle(b).display !== 'none', box: getComputedStyle(g).display !== 'none', text: b.textContent.trim(), redirect: b.dataset.redirect,
    bg: g.dataset.bg, title: g.title, button: g.textContent.trim() }; })()"""
ACTION = """(() => { const d = document.getElementById('dci-harmony'); if (!d) return null; const a = d.querySelector('a');
  const prev = d.previousElementSibling; const use = d.querySelector('svg use');
  return { text: a.textContent, href: a.href, target: a.target, cls: d.className, after: prev ? prev.textContent.trim() : '',
    next: d.nextElementSibling ? d.nextElementSibling.tagName : '', icon: use ? use.getAttribute('xlink:href') || use.getAttribute('href') : '' }; })()"""
results = []
real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_any(ctx, 'https://musicbrainz.org/release/add', all_tabs=True)
    pg.on('dialog', lambda d: d.accept())
    pg.evaluate("localStorage.setItem('dci-after-edit-bg', 'false')")
    pg.reload()
    pg.wait_for_selector('#dci-after-edit', state='attached', timeout=15000)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(400)
    # A) setting off: the note
    a1 = pg.evaluate(TICK)
    pg.click('#enter-edit')
    pg.wait_for_url(f'{HARMONY}**', timeout=15000)
    pg.wait_for_selector('#dci-harmony', timeout=10000)
    a2 = [pg.url, pg.evaluate("sessionStorage.getItem('dci-after-edit-go')"), pg.evaluate("window.__gmTabs")]
    print('A) Release-Editor mit Harmony, Einstellung aus:', a1)
    print('   nach Enter edit:', a2)
    results.append(a1['shown'] and not a1['box'] and a1['redirect'] == 'harmony.pulsewidth.org.uk'
                   and a1['text'] == 'for the Credits Importer: after “Enter edit”, use “Edit relationships with Credits Importer” on Harmony'
                   and a2[0] == f'{HARMONY}?bandcamp=testband%2Ftestalbum&release_mbid={H.REL}' and a2[1] is None and a2[2] == [])
    want = f'https://musicbrainz.org/release/{H.REL}/edit-relationships#dci-import&src={quote(ALBUM, safe="")}'
    # A3) an error while submitting (setting on): the return address as before
    pg.goto('https://musicbrainz.org/release/add')
    pg.evaluate("localStorage.removeItem('dci-after-edit-bg')")
    pg.reload()
    pg.wait_for_selector('#dci-after-edit', state='attached', timeout=15000)
    pg.evaluate("__tab('edit-note'); window.__fail = true")
    pg.wait_for_timeout(400)
    pg.click('#dci-enter-import')
    pg.wait_for_timeout(800)
    a3 = pg.evaluate("MB.releaseEditor.redirectURI")
    # A2) setting on: the button, a background tab
    pg.evaluate("window.__fail = false")
    a4 = pg.evaluate(TICK)
    pg.click('#dci-enter-import')
    pg.wait_for_url(f'{HARMONY}**', timeout=15000)
    pg.wait_for_selector('#dci-harmony', timeout=10000)
    pg.wait_for_timeout(400)
    a5 = [pg.url, pg.evaluate("window.__gmTabs"), pg.evaluate("document.querySelector('#dci-harmony p').textContent.trim()")]
    print('A3) Fehler beim Abschicken – Rücksprung:', a3)
    print('A2) Einstellung an:', a4, '| Harmony:', a5)
    results.append(a3 == f'{HARMONY}?bandcamp=testband%2Ftestalbum'
                   and not a4['shown'] and a4['box'] and a4['bg'] == '1' and a4['button'] == 'Enter edit & import credits' and 'background tab' in a4['title']
                   and a5[0] == f'{HARMONY}?bandcamp=testband%2Ftestalbum&release_mbid={H.REL}'
                   and a5[1] == [[want, {'active': False, 'insert': True, 'setParent': True}]]
                   and a5[2] == 'Edit relationships with Credits Importer – opened in a background tab')
    pg.reload()
    pg.wait_for_selector('#dci-harmony', timeout=10000)
    pg.wait_for_timeout(400)
    again = pg.evaluate("window.__gmTabs")
    print('   neu geladen – geöffnet:', again)
    results.append(again == [])
    # B)
    b1 = pg.evaluate(ACTION)
    print('B) Harmony-Seite:', b1)
    results.append(b1['text'] == 'Edit relationships with Credits Importer' and b1['href'] == want and b1['target'] == '_blank'
                   and b1['cls'] == 'action' and b1['after'] == 'Add cover art' and b1['next'] == 'FIGURE' and b1['icon'] == '/icon-sprite.svg#database-edit')
    # C)
    with ctx.expect_page() as info:
        pg.click('#dci-harmony a')
    tab = info.value
    tab.wait_for_load_state()
    opened = tab.url
    tab.close()
    # (the script is not injected into a tab opened by a click in this harness: the same address in a new tab)
    mb = ctx.new_page()
    mb_errs = H.errors_of(mb)
    mb.on('dialog', lambda d: d.accept())
    mb.goto(b1['href'])
    H.wait_for(mb, f"{LOGS}.some(x => /Source handed over by the link/.test(x))", 60)
    H.wait_for(mb, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    mb.wait_for_timeout(800)
    c1 = [x for x in mb.evaluate(LOGS) if 'link' in x.lower() and ('Started' in x or 'handed' in x)]
    names = mb.evaluate("[...document.querySelectorAll('.dci-gname strong')].map(s => s.textContent.trim())")
    print('C) neuer Tab:', opened == want, '| Beziehungs-Editor:', mb.url, '| Protokoll:', c1, '| Einträge:', names)
    results.append(opened == want and mb.url == f'https://musicbrainz.org/release/{H.REL}/edit-relationships' and 'Jane Roe' in names
                   and any('Started from a link' in x and 'Bandcamp testband.bandcamp.com/album/testalbum' in x for x in c1)
                   and any('Source handed over by the link, not in MusicBrainz yet: Bandcamp testband.bandcamp.com/album/testalbum' in x for x in c1)
                   and mb.evaluate("!document.getElementById('dci-overlay').hidden"))
    mb.close()
    # D)
    pg.goto(HARMONY)
    pg.wait_for_timeout(1200)
    d1 = pg.evaluate("!!document.getElementById('dci-harmony')")
    pg.goto(f'{HARMONY}?discogs=1234&release_mbid={H.REL}')
    pg.wait_for_selector('#dci-harmony', timeout=10000)
    d2 = pg.evaluate(ACTION)['href']
    H.EDITOR_REDIRECT['edit'] = 'https://example.org/back'
    pg.goto(f'https://musicbrainz.org/release/{H.REL}/edit')
    pg.wait_for_selector('#dci-after-edit', state='attached', timeout=15000)
    pg.evaluate("__tab('edit-note')")
    pg.wait_for_timeout(400)
    d3 = pg.evaluate(TICK)
    print('D) ohne Release:', d1, '| Discogs:', d2, '| anderes Werkzeug:', d3)
    results.append(not d1 and d2.endswith('#dci-import&src=' + quote('https://www.discogs.com/release/1234', safe=''))
                   and d3['text'] == 'after “Enter edit” MusicBrainz goes on to example.org; the relationship editor does not open by itself' and not d3['box'])
    # E) the settings (topic Sources): the button of the release editor and the background tab
    pg.evaluate("localStorage.removeItem('dci-after-edit-btn'); localStorage.removeItem('dci-after-edit-bg')")
    pg.goto(f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
    pg.wait_for_timeout(300)
    pg.locator('[data-act=settings-topic][data-topic=sources]').evaluate('b => b.click()')
    pg.wait_for_timeout(300)
    SET = "[...document.querySelectorAll('[data-set=after-edit], [data-set=after-edit-bg]')].map(i => [i.dataset.set, i.checked, i.closest('label').textContent.trim().slice(0, 40)])"
    e1 = pg.evaluate(SET)
    pg.locator('[data-set=after-edit-bg]').evaluate('i => i.click()')
    pg.locator('[data-set=after-edit]').evaluate('i => i.click()')
    pg.wait_for_timeout(300)
    e2 = [pg.evaluate("localStorage.getItem('dci-after-edit-bg')"), pg.evaluate("localStorage.getItem('dci-after-edit-btn')"), pg.evaluate(SET)]
    pg.locator('[data-el=settings] [data-act=settings-reset][data-topic=sources]').evaluate('b => b.click()')
    pg.wait_for_timeout(400)
    e3 = [pg.evaluate("localStorage.getItem('dci-after-edit-btn')"), pg.evaluate("localStorage.getItem('dci-after-edit-bg')"), pg.evaluate(SET)]
    print('E) Einstellungen:', e1, '| beide aus:', e2, '| ↺ Quellen:', e3)
    results.append(e1 == [['after-edit', True, 'Release editor: the button “Enter edit &'], ['after-edit-bg', True, 'Imported with Harmony (Bandcamp, Discogs']]
                   and e2[0] == 'false' and e2[1] == 'false' and e3[0] is None and e3[1] is None and [x[1] for x in e3[2]] == [True, True])
    print('Fehler:', real(errs), real(mb_errs))
    results.append(not real(errs) and not real(mb_errs))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
