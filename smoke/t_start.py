"""Starting: from the release editor, from Harmony, the source in the navigation (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: afteredit, harmony, navlink – each the former smoke/t_<case>.py, unchanged; `python3 t_start.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_afteredit():
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


def case_harmony():
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


def case_navlink():
    """Credits Importer 3.17.4: the source next to the status in the navigation bar (collected item 22), and a link at each
    name suggestion (collected item 24).
    A) Bandcamp loaded, no Bandcamp tab: the bar above "Import credits …" says "Bandcamp view: no Bandcamp tab", links the
       album ("↗ Bandcamp", a new tab) and has "open in background", which opens it in the background.
    B) A Bandcamp tab on another album: the bar offers "Load the release there", which loads the album there.
    C) Discogs loaded: the bar links the Discogs release.
    D) Each suggestion of a name has a small ↗ that opens its MusicBrainz entry in a new tab (artist, label)."""
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


run_cases(globals())
