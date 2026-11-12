"""Starting: from the release editor, from Harmony, the source in the navigation (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: afteredit, harmony, navlink, mappingload (3.33.0) – each the former smoke/t_<case>.py, unchanged –, languagesload, gapline (3.39.0), gapmore (3.40.0), gapsplit; `python3 t_start.py <case> …` runs only those.

3.72.0: also the cases of the former t_media_choice.py – media, mediaload, mediasel (a release with several media, the media choice)."""
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
    A) Bandcamp loaded, no Bandcamp tab: the bar above "Import credits …" says "Script Companion: no Bandcamp tab" (until 3.93.0 "Bandcamp view: …"), links the
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
        results.append(a1 is not None and a1[0].startswith('Script Companion: no Bandcamp tab') and a1[1] is not None and a1[1][0] == '↗ Bandcamp'
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
        results.append('sync-load' in b1[2] and b2[0].startswith('Script Companion: connected') and b2[1] is not None)
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


def case_mappingload():
    """Credits Importer 3.33.0 (milestone "Mapping file"): where the mapping file comes from (Block W).
    A) Loaded by the userscript manager (GM_getResourceText): the dashboard works; "Mapping rules" says where the data comes from
       ("version <the script's>, loaded by the userscript manager"), the log "Mapping file <version> (loaded by the userscript manager)".
    B) The manager did not load it: the script fetches it from GitHub (…/main/mb-vibecode-credits-importer-mapping.json?v=…),
       keeps it for this version and loads the page once more – the dashboard works, "fetched from GitHub by the script"; the
       next page needs no fetch.
    C) Not on GitHub either: no dashboard, the message "mapping file missing" with "Update script" – it opens the script's
       address."""
    import json
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        # A)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.click('.dci-head [data-act=rules]'); pg.wait_for_timeout(300)
        src_a = pg.evaluate("document.querySelector('#dci-rules [data-rf=mapping-src]').textContent")
        log_a = pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => li.textContent).filter(t => /Mapping file/.test(t))")
        print('A)', src_a, '|', log_a)
        ok_a = f'mb-vibecode-credits-importer-mapping.json (version {H.VERSION}, loaded by the userscript manager)' in src_a \
            and any(f'Mapping file {H.VERSION} (loaded by the userscript manager)' in t for t in log_a)
        results += [ok_a, not errs]
        ctx.close()
        # B) fetched from GitHub
        H.MAPPING_SHIM_OFF = True
        H.RAW_GITHUB['/proto-beep/MBvibecode/main/mb-vibecode-credits-importer-mapping.json'] = H.MAPPING_TEXT
        H.RAW_REQUESTS.clear()
        ctx = H.new_context(b)
        pg, errs = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
        pg.wait_for_selector('#dci-open', timeout=30000)
        stored = pg.evaluate(f"!!localStorage.getItem('dci-mapping:{H.VERSION}')")
        H.open_dashboard(pg)
        pg.click('.dci-head [data-act=rules]'); pg.wait_for_timeout(300)
        src_b = pg.evaluate("document.querySelector('#dci-rules [data-rf=mapping-src]').textContent")
        n1 = len(H.RAW_REQUESTS)
        pg.reload(); pg.wait_for_selector('#dci-open', timeout=30000)
        n2 = len(H.RAW_REQUESTS)
        print('B) geholt:', H.RAW_REQUESTS[:1], '| gespeichert:', stored, '|', src_b, '| Abrufe:', n1, '→', n2)
        ok_b = n1 == 1 and f'mapping.json?v={H.VERSION}' in H.RAW_REQUESTS[0] and stored and 'fetched from GitHub by the script' in src_b and n2 == n1
        results += [ok_b, not errs]
        ctx.close()
        # C) missing
        H.RAW_GITHUB.clear()
        ctx = H.new_context(b)
        ctx.add_init_script("window.__opened = []; window.open = (u) => { window.__opened.push(u); return null; };")
        pg, errs = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
        pg.wait_for_selector('#dci-mapping-missing', timeout=20000)
        msg = pg.evaluate("document.getElementById('dci-mapping-missing').textContent")
        dash = pg.locator('#dci-open').count()
        pg.click('#dci-mapping-missing .dci-mapping-update')
        opened = pg.evaluate('window.__opened')
        print('C)', msg[:160], '| Dashboard-Knopf:', dash, '| geöffnet:', opened)
        ok_c = 'mapping file missing' in msg and 'Update script' in msg and dash == 0 \
            and opened == ['https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-vibecode-credits-importer.user.js']
        results += [ok_c]
        ctx.close()
        b.close()
    print('A)', results[0], '| B)', results[2], '| C)', results[4])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_languagesload():
    """Credits Importer 3.34.0 (milestone "Languages file", item E6): where the texts in German,
    Spanish and French come from.
    A) Loaded by the userscript manager, German chosen: the dashboard speaks German; the log notes the file (key
       languagesLoaded, "loaded by the userscript manager", its version the script's).
    B) The manager did not load it, German chosen: the script fetches it from GitHub (…/main/…-languages.json?v=<version>),
       keeps it for this version and loads the page once more – German; the next page needs no fetch.
    C) English chosen and the file missing: no reload and no message; it is fetched and kept, and German chosen in
       ⚙ Settings shows at once.
    D) Not on GitHub either, German chosen: the message "languages file missing" with "Update script", the dashboard in
       English, the log warns (languagesMissing)."""
    import json
    results = []
    LANG_PATH = '/proto-beep/MBvibecode/main/mb-vibecode-credits-importer-languages.json'
    LOG = f"JSON.parse(sessionStorage.getItem('dci-log:{H.REL}') || '[]').filter(e => /^languages/.test(e.key)).map(e => [e.key, e.params])"
    de = json.loads(H.LANGUAGES_TEXT)['de']

    def lang(ctx, code):
        ctx.add_init_script("localStorage.setItem('dci-lang', %s);" % json.dumps(json.dumps(code)))

    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        # A) from the manager
        ctx = H.new_context(b)
        lang(ctx, 'de')
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        btn_a = pg.locator('#dci-open').inner_text().strip()
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        log_a = pg.evaluate(LOG)
        print('A)', btn_a, '|', log_a)
        results += [btn_a == de['launcher.open'] and log_a and log_a[0][0] == 'languagesLoaded' and log_a[0][1]['version'] == H.VERSION
                    and log_a[0][1]['from'] in (de.get('mapping.from.manager'), 'loaded by the userscript manager'), not errs]
        ctx.close()
        # B) fetched from GitHub, German chosen: once more
        H.LANGUAGES_SHIM_OFF = True
        H.RAW_GITHUB[LANG_PATH] = H.LANGUAGES_TEXT
        H.RAW_REQUESTS.clear()
        ctx = H.new_context(b)
        lang(ctx, 'de')
        pg, errs = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
        H.wait_for(pg, "!!document.getElementById('dci-open') && document.getElementById('dci-open').textContent.includes('importieren')", 30)
        stored = pg.evaluate(f"!!localStorage.getItem('dci-languages:{H.VERSION}')")
        n1 = len(H.RAW_REQUESTS)
        pg.reload()
        pg.wait_for_selector('#dci-open', timeout=30000)
        btn_b = pg.locator('#dci-open').inner_text().strip()
        n2 = len(H.RAW_REQUESTS)
        print('B) geholt:', H.RAW_REQUESTS[:1], '| gespeichert:', stored, '|', btn_b, '| Abrufe:', n1, '→', n2)
        results += [n1 == 1 and f'languages.json?v={H.VERSION}' in H.RAW_REQUESTS[0] and stored and btn_b == de['launcher.open'] and n2 == n1, not errs]
        ctx.close()
        # C) English chosen: fetched in the background, no reload, German at once from ⚙ Settings
        H.RAW_REQUESTS.clear()
        ctx = H.new_context(b)
        lang(ctx, 'en')
        ctx.add_init_script("window.__loads = (window.__loads || 0) + 1; sessionStorage.setItem('t-loads', String(Number(sessionStorage.getItem('t-loads') || 0) + 1));")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.wait_for(pg, f"!!localStorage.getItem('dci-languages:{H.VERSION}')", 20)
        pg.wait_for_timeout(500)
        c1 = [pg.locator('#dci-open').inner_text().strip(), pg.evaluate("sessionStorage.getItem('t-loads')"), pg.locator('#dci-languages-missing').count(), len(H.RAW_REQUESTS)]
        H.open_dashboard(pg)
        H.open_settings(pg, 'general')
        pg.select_option('[data-el=settings] [data-f=lang]', 'de')
        pg.wait_for_timeout(500)
        c2 = pg.locator('.dci-head [data-act=settings-open]').get_attribute('aria-label')
        print('C) Englisch:', c1, '| auf Deutsch:', c2)
        results += [c1 == ['Import credits …', '1', 0, 1] and c2 == 'Einstellungen', not errs]
        ctx.close()
        # D) missing, German chosen
        H.RAW_GITHUB.clear()
        ctx = H.new_context(b)
        lang(ctx, 'de')
        ctx.add_init_script("window.__opened = []; window.open = (u) => { window.__opened.push(u); return null; };")
        pg, errs = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
        pg.wait_for_selector('#dci-languages-missing', timeout=20000)
        msg = pg.evaluate("document.getElementById('dci-languages-missing').textContent")
        btn_d = pg.locator('#dci-open').inner_text().strip()
        pg.click('#dci-languages-missing .dci-mapping-update')
        opened = pg.evaluate('window.__opened')
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        log_d = pg.evaluate(LOG)
        print('D)', msg[:120], '| Knopf:', btn_d, '| geöffnet:', opened, '| Log:', log_d)
        results += [msg.startswith('MB x Vibecode: Credits Importer – languages file missing') and 'Update script' in msg and btn_d == 'Import credits …'
                    and opened == ['https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-vibecode-credits-importer.user.js']
                    and log_d and log_d[0][0] == 'languagesMissing', not errs]
        ctx.close()
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_gapline():
    """Credits Importer 3.39.0 (collected item 172, F-172a – F-172g): the line of the release page.
    A) The release page (with its Discogs link): below the title "Discogs: about N relationships of its credits are not on
       MusicBrainz yet." – every credit counted on each of its tracks, by the names MusicBrainz has there (Drum Guy's drums on
       track 1 are there: 3 of his 4); ▸ shows the parts (recordings, release, works, labels and places, they add up to N); with the
       dashboard's number of its last check ("The dashboard counted 25 new ones on …").
    B) Loaded again: the Discogs credits are kept (no request to Discogs); ✕ hides the line – also loaded again; one relationship
       more on MusicBrainz (the number changes): the line is back.
    C) The setting off (⚙ Settings → Sources): no line, no request.
    D) "Import credits …": the relationship editor of the release, the dashboard opens and imports from Discogs; its number of new
       relationships is kept for the line."""
    REL = H.REL
    LINE = """(() => { const b = document.querySelector('.dci-gapline'); if (!b) return null; const h1 = document.querySelector('#content h1');
      return { text: b.querySelector('span').textContent, after: h1 && h1.nextElementSibling === b, parts: [...b.querySelectorAll('[data-gap-parts] li')].map(l => l.textContent),
        hidden: b.querySelector('[data-gap-parts]').hidden }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg = []
        # (3.39.2) the requests of the context from the start: the first one came before the page's listener under load
        ctx.on('request', lambda r: dg.append(r.url) if 'api.discogs.com' in r.url else None)
        pr, errs = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{REL}')
        pr.evaluate(f"localStorage.setItem('dci-gap-exact:{REL}', JSON.stringify({{ n: 25, at: Date.parse('2026-11-02T10:00:00Z') }}))")
        pr.reload(); pr.wait_for_timeout(500)
        H.wait_for(pr, "!!document.querySelector('.dci-gapline')", 20)
        a = pr.evaluate(LINE)
        pr.click('.dci-gapline [data-gap=parts]'); pr.wait_for_timeout(200)
        a2 = pr.evaluate(LINE)
        print('A)', a, '\n  ▸', a2)
        import re
        # (3.39.0, review) its notes are not counted (the test release has notes); the date in the format of the browser
        m = re.match(r'Discogs: about (\d+) relationships of its credits are not on MusicBrainz yet \(the credits of its notes not counted\)\. The dashboard counted 25 new ones on \S+\.$', a['text'] if a else '')
        nums = [int(re.search(r'(\d+)', x).group(1)) for x in (a2 or {'parts': []})['parts'][:4]]
        results.append(bool(m) and a['after'] and a['hidden'] and not a2['hidden'] and len(nums) == 4 and sum(nums) == int(m.group(1)) and nums[0] > 0)
        n0 = len(dg)
        pr.reload(); pr.wait_for_timeout(500)
        H.wait_for(pr, "!!document.querySelector('.dci-gapline')", 20)
        kept = len(dg) == n0
        pr.click('.dci-gapline [data-gap=close]'); pr.wait_for_timeout(200)
        gone = pr.evaluate("!document.querySelector('.dci-gapline')")
        pr.reload(); pr.wait_for_timeout(2500)
        still = pr.evaluate("!document.querySelector('.dci-gapline')")
        H.MB_EXTRA.setdefault(H.REC[1], []).append({'target-type': 'artist', 'type': 'instrument', 'type-id': H.LTS[148]['gid'], 'attributes': ['bass'],
                                                    'attribute-values': {}, 'artist': {'id': H.ARTISTS[3001][0], 'name': 'Bass Man'}})
        pr.reload(); pr.wait_for_timeout(500)
        H.wait_for(pr, "!!document.querySelector('.dci-gapline')", 20)
        back = pr.evaluate(LINE)
        print('B) Discogs-Anfragen:', n0, len(dg), '| ✕:', gone, '| neu geladen weg:', still, '| eine mehr auf MB:', back and back['text'][:60])
        results.append(n0 >= 1 and kept and gone and still and back is not None and int(re.search(r'about (\d+)', back['text']).group(1)) == int(m.group(1)) - 1)
        pr.evaluate("localStorage.setItem('dci-gap-on', 'false')")
        n1 = len(dg)
        pr.reload(); pr.wait_for_timeout(2500)
        c = pr.evaluate("!document.querySelector('.dci-gapline')")
        print('C) aus:', c, len(dg) == n1)
        results.append(c and len(dg) == n1)
        pr.evaluate("localStorage.removeItem('dci-gap-on')")
        pr.reload(); pr.wait_for_timeout(500)
        H.wait_for(pr, "!!document.querySelector('.dci-gapline')", 20)
        pr.click('.dci-gapline [data-gap=import]')
        pr.wait_for_url('**/edit-relationships', timeout=20000)
        H.wait_for(pr, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        d = pr.evaluate("[location.pathname, !document.getElementById('dci-overlay').hidden, [...document.querySelectorAll('#dci-log li')].map(li => li.textContent).filter(t => /links there/.test(t)).join(' | ')]")
        pr.wait_for_timeout(800)
        ex = pr.evaluate(f"[JSON.parse(localStorage.getItem('dci-gap-exact:{REL}') || 'null'), (document.querySelector('.dci-sum-new') || {{}}).textContent || '']")
        print('D)', d, '| Zahl des Dashboards:', ex)
        # (review) the Discogs link goes with it (the dashboard does not choose the source by itself); the number once, with the Discogs release
        results.append(d[0] == f'/release/{REL}/edit-relationships' and d[1] and 'links there: –' not in d[2] and 'Discogs' in d[2]
                       and ex[0] and f"{ex[0]['n']} new relationships" == ex[1].strip() and ex[0].get('dId') == str(H.DISCOGS_ID))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_gaprefresh3131():
    """Credits Importer 3.131.0 (collected item Z-GAPREFRESH; rule S218): "Enter edit" after a dashboard import.
    A) The dashboard imports from Discogs, everything that can be staged is staged; "Enter edit" (its form submitted): the number of the line
       counted once more – what is still missing – and kept with "afterEdit".
    B) The release page: less than a fifth of the credits' relationships still missing – no line (developer mode: "after “Enter edit” …").
    C) 20 still missing after "Enter edit": the line, "After “Enter edit” on … the dashboard counted 20 still missing."
    D) Rule S218 off: the line as before (the small number after "Enter edit" does not hide it)."""
    REL = H.REL
    import re
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1000)
        before = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-gap-exact:{REL}') || 'null')")
        pg.click('[data-act=apply]')
        pg.wait_for_timeout(3000)
        # "Enter edit": the edit note in a form with its submit button (as in MusicBrainz's editor), the submission stopped here
        pg.evaluate("""() => { const t = document.getElementById('edit-note-text'); const f = document.createElement('form'); t.parentNode.insertBefore(f, t); f.appendChild(t);
          const btn = document.createElement('button'); btn.type = 'submit'; btn.textContent = 'Enter edit'; f.appendChild(btn); f.addEventListener('submit', (e) => e.preventDefault()); }""")
        pg.evaluate("document.getElementById('edit-note-text').form.requestSubmit()")
        pg.wait_for_timeout(800)
        after = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-gap-exact:{REL}') || 'null')")
        log = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'Enter edit' in x and 'still missing' in x]
        print('A) vorher:', before, '| nach Enter edit:', after, log)
        results.append(before and not before.get('afterEdit') and after and after.get('afterEdit') and after['n'] < before['n'] and log and not errs)
        pg.evaluate("localStorage.setItem('dci-dev', 'true'); localStorage.setItem('dci-gap-why', 'true')")
        pr, errs2 = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{REL}')
        pr.wait_for_timeout(3000)
        bb = pr.evaluate("[!!document.querySelector('.dci-gapline'), (document.querySelector('.dci-gapwhy') || {}).textContent || '']")
        print('B)', bb)
        results.append(not bb[0] and 'after “Enter edit”' in bb[1])
        pr.evaluate(f"localStorage.setItem('dci-gap-exact:{REL}', JSON.stringify({{ ...JSON.parse(localStorage.getItem('dci-gap-exact:{REL}')), n: 20, open: 0 }}))")
        pr.reload()
        pr.wait_for_timeout(500)
        H.wait_for(pr, "!!document.querySelector('.dci-gapline')", 20)
        c = pr.evaluate("document.querySelector('.dci-gapline span').textContent")
        print('C)', c)
        results.append(bool(re.search(r'After “Enter edit” on \S+ the dashboard counted 20 still missing\.$', c)))
        pr.evaluate(f"localStorage.setItem('dci-gap-exact:{REL}', JSON.stringify({{ ...JSON.parse(localStorage.getItem('dci-gap-exact:{REL}')), n: 0, open: 1 }})); localStorage.setItem('dci-rules-off', JSON.stringify(['S083', 'S218']))")
        pr.reload()
        pr.wait_for_timeout(500)
        H.wait_for(pr, "!!document.querySelector('.dci-gapline')", 20)
        d = pr.evaluate("document.querySelector('.dci-gapline span').textContent")
        print('D)', d)
        results.append('still missing' in d and not errs2)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_gapsplit():
    """Credits Importer 3.41.15 (the check of Block BF, Z-SUB): the line of the release page reads an index of Discogs whose sub-tracks
    are tracks of their own in MusicBrainz as these tracks, as the dashboard does. Discogs: 1, 2 and the index "Suite X" with 3a
    "Song Three" and 3b "Song Four" (Bass Man, bass – the only credit); MusicBrainz has Bass Man's bass on its track 4.
    A) The line (with "Also when nothing seems to be missing"): "the credits of its list seem to be on MusicBrainz" – until 3.41.14 the release
       page read three tracks, Bass Man's bass on track 3, and said one relationship was missing."""
    REL = H.REL
    orig = H.discogs_release

    def rel():
        d = orig()
        t3, t4 = d['tracklist'][2], d['tracklist'][3]
        t3 = dict(t3, position='3a', extraartists=[])
        t4 = dict(t4, position='3b', extraartists=[{'name': 'Bass Man', 'anv': '', 'role': 'Bass', 'tracks': '', 'id': 3001, 'join': ''}])
        d['tracklist'] = [dict(t, extraartists=[]) for t in d['tracklist'][:2]] + [{'position': '', 'type_': 'index', 'title': 'Suite X', 'duration': '', 'sub_tracks': [t3, t4]}]
        d['extraartists'] = []
        d['companies'] = []
        return d

    H.discogs_release = rel
    H.MB_EXTRA.setdefault(H.REC[3], []).append({'target-type': 'artist', 'type': 'instrument', 'type-id': H.LTS[148]['gid'], 'attributes': ['bass'],
                                                'attribute-values': {}, 'artist': {'id': H.ARTISTS[3001][0], 'name': 'Bass Man'}})
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pr, errs = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{REL}')
        pr.evaluate("localStorage.setItem('dci-gap-none', 'true')")
        pr.reload(); pr.wait_for_timeout(500)
        H.wait_for(pr, "!!document.querySelector('.dci-gapline')", 30)
        a = pr.evaluate("document.querySelector('.dci-gapline [data-gap-text]').textContent")
        print('A)', a)
        results.append(a.startswith('Discogs: the credits of its list seem to be on MusicBrainz'))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_gapmore():
    """Credits Importer 3.40.0 (block AY: Q-g, Q-n, Q-o, Q-x): the line of the release page, more.
    A) No credits in the source: no line (nothing asked of Discogs again).
    B) Nothing missing (Drum Guy's drums on track 1 are on MusicBrainz): no line; with the setting "Also when nothing seems to be
       missing" (dci-gap-none, off): "Discogs: its credits seem to be on MusicBrainz …". One missing: the line – and none once the
       dashboard counted no new relationship since the credits were read.
    C) "Count exactly": the relationship editor of the release in a tab in the background (#dci-count), its dashboard imports
       Discogs by itself and counts – a release of two media without the dialog of the media (review); the line takes the number
       ("The dashboard counted N new ones on …") and closes the tab. An import that fails: "The count failed …", the tab closed.
    E) (3.40.2) A Discogs release without credits in its list: Bandcamp steps in, the line says so ("Discogs has no credits to import
       in its list for this release (its notes are not read here). Bandcamp: …"); (3.40.3, review) "Import credits …" imports Bandcamp; a
       release Discogs does not have (404): Bandcamp too ("Discogs does not have this release (any more). …"). Three Bandcamp pages (a label's with one credit, the
       artist's, one that cannot be read): the one with more credits, the others under ▸; ✕ holds for it.
    D) Without a Discogs link: Bandcamp's album page, a rough estimate ("Bandcamp: about N relationships … (a rough estimate)."),
       its parts and how it is counted, instruments in capitals ("Jane Roe – Electric Guitar", "Tenor Saxophone – Max Mustermann");
       "Count exactly" counts Bandcamp (its rows without a MusicBrainz entry named: still missing). An album page without credits
       – an "about" text with "Stream: …", "Length: …" – no line."""
    import re
    import time
    REL = H.REL
    DID = str(H.DISCOGS_ID)
    KEY = f'dci-gap:{REL}'
    BCKEY = f'dci-gap:{REL}:bandcamp'
    EXACT = f'dci-gap-exact:{REL}'
    LINE = """(() => { const b = document.querySelector('.dci-gapline'); if (!b) return null;
      return { src: b.dataset.src, text: b.querySelector('[data-gap-text]').textContent, count: !!b.querySelector('[data-gap=count]'),
        parts: [...b.querySelectorAll('[data-gap-parts] li')].map(l => l.textContent), disabled: b.querySelector('[data-gap=count]').disabled }; })()"""
    # GM_openInTab as a userscript manager has it: a tab and its handle with close() – noted here, the test opens the tab as a page of
    # its own (a popup of window.open would keep the window of its about:blank, without the script) and closes it when asked
    OPEN = """Object.defineProperty(window, 'GM_openInTab', { configurable: true, set() {}, get() { return (u, o) => {
      localStorage.setItem('t-opened', JSON.stringify([u, o || null])); localStorage.removeItem('t-closed');
      return { close: () => localStorage.setItem('t-closed', u) }; }; } });"""
    BAND = 'https://testband.bandcamp.com'
    ALBUM = f'{BAND}/album/testalbum'
    TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
    H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
    H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
    H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
    BC_CREDITS = {'text': 'Test Band – guitar\nMixed by Jane Roe\nTrumpet: Peter Evans\nDrum Guy – drums\nJane Roe – Electric Guitar\nTenor Saxophone – Max Mustermann'}
    # (review) two media: "Count exactly" without the dialog of the media
    H.MEDIA = [2, 2]
    H.BC_PAGES[ALBUM] = None
    orig_ws = H.ws_release
    # the release's links: Discogs (or not), Bandcamp pages ((3.40.2) several)
    MODE = {'discogs': True, 'bc': []}

    def ws(full=False):
        d = orig_ws(full)
        if not MODE['discogs']:
            d['relations'] = [r for r in d['relations'] if not (r.get('url') and 'discogs.com' in r['url']['resource'])]
        for u in MODE['bc']:
            d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': u}})
        return d
    H.ws_release = ws
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            ctx.add_init_script(OPEN)
            dg, bcq, warns = [], [], []
            ctx.on('request', lambda r: dg.append(r.url) if 'api.discogs.com' in r.url else (bcq.append(r.url) if 'bandcamp.com' in r.url else None))
            pr, errs = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{REL}', all_tabs=True)
            # ([3.78.0] Z-FLK) a request of the line still under way when the page is loaded again is cut off ("Failed to fetch") –
            # not a fault: a warning while the page is being loaded again is left out (only that one)
            nav = {'on': False}
            pr.on('console', lambda m: warns.append(m.text) if 'release gap' in m.text and not (nav['on'] and 'Failed to fetch' in m.text) else None)

            def again(goto=None):
                nav['on'] = True
                try:
                    pr.goto(goto) if goto else pr.reload()
                finally:
                    nav['on'] = False
            pr.wait_for_timeout(800)

            def seed(kept=None, exact=None, none=None):
                js = []
                js.append(f"localStorage.setItem('{KEY}', {repr(__import__('json').dumps(kept))})" if kept is not None else f"localStorage.removeItem('{KEY}')")
                js.append(f"localStorage.removeItem('{BCKEY}')")
                js.append(f"localStorage.setItem('{EXACT}', {repr(__import__('json').dumps(exact))})" if exact is not None else f"localStorage.removeItem('{EXACT}')")
                js.append("localStorage.setItem('dci-gap-none', 'true')" if none else "localStorage.removeItem('dci-gap-none')")
                pr.evaluate('; '.join(js))
                again()

            def line(wait=True):
                if wait:
                    H.wait_for(pr, "!!document.querySelector('.dci-gapline')", 30)
                else:
                    pr.wait_for_timeout(2500)
                return pr.evaluate(LINE)
            now = int(time.time() * 1000)
            # A) no credits
            n0 = len(dg)
            seed({'dId': DID, 'at': now, 'credits': [], 'nTracks': 4, 'notes': False})
            a = line(False)
            print('A) ohne Credits:', a, '| Discogs-Anfragen:', len(dg) - n0)
            results.append(a is None and len(dg) == n0)
            # B) nothing missing; the setting; one missing; the dashboard counted none
            drum = {'names': ['drum guy'], 'level': 'recording', 'tracks': [0], 'kind': 'person'}
            seed({'dId': DID, 'at': now, 'credits': [drum], 'nTracks': 4, 'notes': False})
            b1 = line(False)
            seed({'dId': DID, 'at': now, 'credits': [drum], 'nTracks': 4, 'notes': False}, none=True)
            b2 = line()
            miss = {'names': ['nobody here'], 'level': 'release', 'tracks': None, 'kind': 'person'}
            seed({'dId': DID, 'at': now, 'credits': [drum, miss], 'nTracks': 4, 'notes': False})
            b3 = line()
            seed({'dId': DID, 'at': now, 'credits': [drum, miss], 'nTracks': 4, 'notes': False}, exact={'n': 0, 'open': 0, 'at': now + 1000, 'src': 'discogs', 'id': DID, 'dId': DID})
            b4 = line(False)
            # (review) none new, but rows of the dashboard without a MusicBrainz entry: missing all the same
            seed({'dId': DID, 'at': now, 'credits': [drum, miss], 'nTracks': 4, 'notes': False}, exact={'n': 0, 'open': 2, 'at': now + 1000, 'src': 'discogs', 'id': DID, 'dId': DID})
            b5 = line()
            # (review) the same credits read again a week later: the count of the dashboard since then still holds (its "since" stays)
            seed()
            line()
            real = pr.evaluate(f"JSON.parse(localStorage.getItem('{KEY}')).credits")
            old = now - 8 * 86400000
            seed({'dId': DID, 'at': old, 'since': old, 'credits': real, 'nTracks': 4, 'notes': True},
                 exact={'n': 0, 'open': 0, 'at': old + 86400000, 'src': 'discogs', 'id': DID, 'dId': DID})
            b6 = line(False)
            b6k = pr.evaluate(f"(() => {{ const k = JSON.parse(localStorage.getItem('{KEY}')); return [k.since, k.at > {old}]; }})()")
            print('B) nichts fehlt:', b1, '| Einstellung:', b2 and b2['text'], '| eins fehlt:', b3 and b3['text'], '| Dashboard zählte keine:', b4,
                  '| keine, 2 offen:', b5 and b5['text'], '| eine Woche später:', b6, b6k)
            results.append(b1 is None and b2 and b2['text'] == 'Discogs: its credits seem to be on MusicBrainz (counted by names).'
                           and b3 and b3['text'] == 'Discogs: about 1 relationship of its credits is not on MusicBrainz yet.' and b4 is None
                           and b5 and b5['text'].startswith('Discogs: about 1 relationship') and b5['text'].endswith('. 2 of its rows still need a MusicBrainz entry or a type.')
                           and 'The dashboard counted 0 new ones on' in b5['text'] and b6 is None and b6k == [old, True])

            def count(expect_src):
                H.wait_for(pr, "!!document.querySelector('.dci-gapline [data-gap=count]')", 30)
                pr.click('.dci-gapline [data-gap=count]')
                pr.wait_for_timeout(300)
                during = pr.evaluate(LINE)
                opened = pr.evaluate("JSON.parse(localStorage.getItem('t-opened') || 'null')")
                tab = ctx.new_page()
                terrs = H.errors_of(tab)
                tab.goto(opened[0])
                H.wait_for(pr, "(() => { const t = document.querySelector('.dci-gapline [data-gap-text]'); return !!t && /The dashboard counted/.test(t.textContent); })()", 150)
                pr.wait_for_timeout(500)
                after = pr.evaluate(LINE)
                # (3.40.3, review) the dashboard's number per source
                exk = EXACT if expect_src == 'discogs' else f'{EXACT}:{expect_src}'
                ex = pr.evaluate(f"[JSON.parse(localStorage.getItem('{exk}') || 'null'), localStorage.getItem('dci-gap-count:{REL}'), localStorage.getItem('t-closed')]")
                tlog = tab.evaluate("[location.hash, [...document.querySelectorAll('#dci-log li')].map(li => li.textContent).filter(t => /Count exactly|Import complete/.test(t)), (document.querySelector('.dci-sum-new') || {}).textContent || '']")
                tab.close()
                print('   zählt:', during and during['text'], during and during['disabled'], '| Tab:', opened, '| im Tab:', tlog, '| danach:', after and after['text'],
                      '| Zahl:', ex, '| Fehler im Tab:', terrs)
                return (during and during['text'] == 'Counting in a tab in the background …' and during['disabled']
                        and opened and opened[0] == f'https://musicbrainz.org/release/{REL}/edit-relationships#dci-count' and opened[1].get('active') is False
                        and tlog[0] == '' and len(tlog[1]) == 2 and 'Started from the release page (“Count exactly”)' in tlog[1][0]
                        and f"{ex[0]['n']} new relationships" == tlog[2].strip()
                        and after and not after['disabled'] and ex[0] and ex[0]['src'] == expect_src and ex[1] is None and ex[2] == opened[0]
                        and f"The dashboard counted {ex[0]['n']} new" in after['text'] and not terrs)
            # C) Count exactly (Discogs)
            seed()
            print('C)')
            c = count('discogs')
            exc = pr.evaluate(f"JSON.parse(localStorage.getItem('{EXACT}') || 'null')")
            results.append(c and exc.get('dId') == DID and exc['n'] > 0)
            # (review) the import of the tab fails (Discogs answers 404 there; the line has the credits kept): said, the tab closed
            H.DG_API[f'/releases/{DID}'] = None
            again()
            H.wait_for(pr, "!!document.querySelector('.dci-gapline [data-gap=count]')", 30)
            pr.click('.dci-gapline [data-gap=count]')
            pr.wait_for_timeout(300)
            opened = pr.evaluate("JSON.parse(localStorage.getItem('t-opened') || 'null')")
            tab = ctx.new_page()
            tab.goto(opened[0])
            H.wait_for(pr, "(() => { const t = document.querySelector('.dci-gapline [data-gap-text]'); return !!t && /The count failed/.test(t.textContent); })()", 90)
            cf = pr.evaluate(f"[document.querySelector('.dci-gapline [data-gap-text]').textContent, document.querySelector('.dci-gapline [data-gap=count]').disabled, localStorage.getItem('t-closed'), localStorage.getItem('dci-gap-count:{REL}')]")
            tab.close()
            H.DG_API.pop(f'/releases/{DID}', None)
            print('C2) fehlgeschlagen:', cf)
            results.append(cf[0] == 'The count failed – the dashboard in the relationship editor says why.' and cf[1] is False and cf[2] == opened[0] and cf[3] is None)
            # D) Bandcamp only
            MODE.update(discogs=False, bc=[ALBUM])
            H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': BC_CREDITS['text']}, 'trackinfo': TRACKS}, ALBUM)
            n1 = len(dg)
            seed()
            d = line()
            pr.click('.dci-gapline [data-gap=parts]'); pr.wait_for_timeout(200)
            d2 = pr.evaluate(LINE)
            stored = pr.evaluate(f"(JSON.parse(localStorage.getItem('{BCKEY}') || '{{}}').pages || {{}})['{ALBUM}'] || null")
            m = re.match(r'Bandcamp: about (\d+) relationships of its credits are not on MusicBrainz yet \(a rough estimate\)\.$', d['text'] if d else '')
            nums = [int(re.search(r'(\d+)', x).group(1)) for x in (d2 or {'parts': []})['parts'][:4]]
            print('D) Bandcamp:', d, '\n   ▸', d2 and d2['parts'], '| gespeichert:', stored and {k: v for k, v in stored.items() if k != 'credits'},
                  '| Bandcamp-Anfragen:', len(bcq), '| Discogs:', len(dg) - n1)
            names = sorted(n for c in stored['credits'] for n in c['names'])
            print('   Namen:', names)
            results.append(bool(m) and d['src'] == 'bandcamp' and len(nums) == 4 and sum(nums) == int(m.group(1)) and nums[0] > 0
                           and d2['parts'][4].startswith('A rough estimate: the credits of the album page') and stored
                           and not stored.get('failAt') and len(dg) == n1 and any(ALBUM in u for u in bcq)
                           and 'max mustermann' in names and names.count('jane roe') == 2 and not [n for n in names if 'guitar' in n or 'saxophone' in n])
            print('D2)')
            d2c = count('bandcamp')
            exb = pr.evaluate(f"JSON.parse(localStorage.getItem('{EXACT}:bandcamp') || 'null')")
            after = pr.evaluate(LINE)
            # Jane Roe, Max Mustermann, Peter Evans, Drum Guy: no MusicBrainz entry chosen – rows open, named in the line
            results.append(d2c and exb['open'] > 0 and after['text'].endswith(f"{exb['open']} of its rows still need a MusicBrainz entry or a type."))
            # an album page without credits: no line
            H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': '',
                                           'about': 'Stream: Spotify, Apple Music\nLength: 45 minutes\nDigital: 24bit/96kHz\nPre-order: out on Friday'}, 'trackinfo': TRACKS}, ALBUM)
            seed()
            d3 = line(False)
            d3k = pr.evaluate(f"(JSON.parse(localStorage.getItem('{BCKEY}') || '{{}}').pages || {{}})['{ALBUM}'] || null")
            print('D3) ohne Credits:', d3, d3k and d3k.get('credits'))
            results.append(d3 is None and d3k and d3k.get('credits') == [])
            # E1) (3.40.2, Z-AD) a Discogs release without credits in its list (its notes kept): Bandcamp steps in, the line says so
            H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': BC_CREDITS['text']}, 'trackinfo': TRACKS}, ALBUM)
            empty = H.discogs_release()
            empty['extraartists'], empty['companies'] = [], []
            empty['tracklist'] = [dict(t, extraartists=[]) for t in empty['tracklist']]
            H.DG_API[f'/releases/{DID}'] = empty
            MODE.update(discogs=True, bc=[ALBUM])
            seed()
            e1 = line()
            print('E1) Discogs ohne Credits:', e1 and e1['text'])
            results.append(bool(e1) and e1['src'] == 'bandcamp' and bool(re.match(r'Discogs has no credits to import in its list for this release \(its notes are not read here\)\. '
                                                                      r'Bandcamp: about \d+ relationships of its credits are not on MusicBrainz yet \(a rough estimate\)\.', e1['text'])))
            # (3.40.3, review) "Import credits …" of that line: the dashboard imports Bandcamp (not the Discogs release without credits)
            pr.click('.dci-gapline [data-gap=import]')
            pr.wait_for_url('**/edit-relationships', timeout=20000)
            H.answer_media(pr)
            H.wait_for(pr, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
            e1i = pr.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9)).filter(t => / read: /.test(t))")
            print('   Import credits …:', e1i)
            results.append(bool(e1i) and e1i[-1].startswith('Bandcamp read:'))
            again(f'https://musicbrainz.org/release/{REL}')
            # (review) a release Discogs does not have (404): Bandcamp steps in too
            H.DG_API[f'/releases/{DID}'] = None
            seed()
            e1m = line()
            print('E1b) Discogs 404:', e1m and e1m['text'][:80])
            results.append(bool(e1m) and e1m['text'].startswith('Discogs does not have this release (any more). Bandcamp: about '))
            H.DG_API.pop(f'/releases/{DID}', None)
            # E2) (Z-AE) three Bandcamp pages – a label's with one credit, the artist's, one that cannot be read: the one with more credits
            LABEL = 'https://somelabel.bandcamp.com/album/testalbum'
            GONE = 'https://gone.bandcamp.com/album/testalbum'
            H.BC_PAGES[LABEL] = H.bc_html({'artist': 'Some Label', 'current': {'title': 'Testalbum', 'credits': 'Mixed by Jane Roe'}, 'trackinfo': TRACKS}, LABEL)
            MODE.update(discogs=False, bc=[LABEL, ALBUM, GONE])
            seed()
            e2 = line()
            pr.click('.dci-gapline [data-gap=parts]'); pr.wait_for_timeout(200)
            e2p = pr.evaluate(LINE)
            pages = pr.evaluate(f"Object.keys((JSON.parse(localStorage.getItem('{BCKEY}') || '{{}}').pages || {{}})).sort()")
            print('E2) drei Seiten:', e2 and e2['text'], '\n   ▸', e2p and e2p['parts'][4:], '| gemerkt:', pages)
            results.append(bool(e2 and m) and e2['text'].startswith(d['text']) and e2p['parts'][4:6] == [
                'Also linked: somelabel.bandcamp.com/album/testalbum – 1 credit there (the page with more credits is counted).',
                'Also linked: gone.bandcamp.com/album/testalbum – it could not be read.'] and pages == sorted([ALBUM, LABEL, GONE]))
            # ✕ hides it for the page counted (also loaded again)
            pr.click('.dci-gapline [data-gap=close]'); pr.wait_for_timeout(200)
            again()
            e3 = line(False)
            print('E3) ✕, neu geladen:', e3)
            results.append(e3 is None)
            print('Fehler:', errs, '| Warnungen:', warns)
            # the page that cannot be read is said in the console (as each failed request of the line)
            # (and the Discogs release that does not exist, E1b)
            results.append(not errs and not [w for w in warns if 'gone.bandcamp.com' not in w and f'Discogs release {DID} does not exist' not in w])
            b.close()
    finally:
        H.ws_release = orig_ws
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


# --- [3.72.0] the cases of the former t_media_choice.py (collected item Z-TST) ----------------------------------------


def case_media():
    """Release with two media: "CD2, tracks 1–3", "Disc 1", medium headings in the track form, and "+ new track
    group" with a whole medium or one group per medium."""
    import re
    import zooid
    from common_rows import cells
    zooid.setup('CD2, tracks 1–3 recorded May 1, 2020 at Brooklyn Recording.\nDisc 1 recorded April 4, 2020.')
    H.MEDIA = [5, 5]
    orig = H.discogs_release


    def rel():
        d = orig()
        for i, t in enumerate(d['tracklist']):
            t['position'] = f'{1 + i // 5}-{1 + i % 5}'
        for e in d['extraartists']:
            if e['tracks']:
                e['tracks'] = '2-1 to 2-5'
        return d


    H.discogs_release = rel
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.click('[data-el=datefind] summary')
        items = [re.sub(r'\s+', ' ', i)[:90] for i in pg.locator('[data-el=datefind-list] li').all_inner_texts()]
        print('Gefunden:', items)
        print('Matrix (Vorschläge):', cells(pg)['performance'])
        print('Track-Pool:', pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts())
        opts = pg.locator('[data-f=tg-new-pick] option').all_inner_texts()
        print('Auswahl „+ neue Track-Gruppe“:', opts)
        pg.select_option('[data-f=tg-new-pick]', 'pick'); pg.wait_for_timeout(200)
        print('Medium-Überschriften im Formular:', pg.locator('.dci-track-form [data-act=tg-medium]').all_inner_texts())
        pg.locator('.dci-track-form [data-act=tg-medium]').nth(1).click(); pg.wait_for_timeout(200)
        checked = pg.evaluate("[...document.querySelectorAll('.dci-track-form input[data-f=tg-track]:checked')].map(c => Number(c.dataset.i))")
        print('Klick auf Medium 2 hakt an (Index):', checked)
        pg.click('[data-act=tg-cancel]'); pg.wait_for_timeout(100)
        pg.select_option('[data-f=tg-new-pick]', 'all'); pg.wait_for_timeout(200)
        groups = [re.sub(r'\s+', ' ', g) for g in pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts()]
        print('Nach „alle Medien“ (Medium 1 gibt es schon als „Tracks 1-1–1-5“):', groups)
        pg.select_option('[data-f=tg-new-pick]', 'm:2'); pg.wait_for_timeout(200)
        again = len(pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts())
        ok = ('tracks 2-1–2-3' in items[0] and checked == [5, 6, 7, 8, 9] and len(opts) == 5 and len(groups) == 3
              and 'Medium 2 · CD 5 tracks' in groups and again == len(groups)
              and [c[1] for c in cells(pg)['performance']] == [['Tracks 2-1–2-3'], ['Tracks 1-1–1-5']])
        print('Ergebnis:', 'OK' if ok else 'FEHLER', '| Fehler:', errs)
        b.close()


def case_mediaload():
    """Credits Importer 3.20.0 / 3.21.1: the media dialog loads the chosen media in MB's relationship editor in the background,
    and asks about the works there when many tracks have none (collected items 34 and 44).
    Four media (1, 2, 1, 0 tracks: medium 4 has no tracklist in MusicBrainz, like CDs 2–13 of "Eternal"); MB's editor has
    loaded medium 1 only. [3.21.1] The editor is built as MusicBrainz builds it (musicbrainz-server, usePagedMediumTable):
    each medium a link `a.expand-medium#disc<n>` "2 ▶ CD" (number before the format, no aria-expanded), its tracks in the
    next tbody (hidden while folded), "Expand all mediums", and a medium shown in part with "Load all tracks..." (medium 2:
    MB loads one track, the link loads the rest).
    A) The dialog: "This release has 4 media", medium 4 named as without a tracklist; "Load the chosen media …" (off at
       first) says how many of the chosen media are not loaded yet; the works box ("3 tracks without a work", "Look up works"
       pressed) – both follow the choice (medium 1 alone: no box).
    B) Ticked, "Not now", Import: all media chosen → MB's "Expand all mediums"; medium 2's "Load all tracks..." clicked; the
       loading starts before the source is read (log before "Media chosen"); log, message, the tick is remembered; no work
       lookups.
    C) "Skip works" ([3.32.1] until then "Skip works matrix") in the dialog: the matrix is skipped for this release (its rows on "Skip"), not asked again.
    D) Media 1 and 3 only: their own toggles (#disc3), no "Expand all mediums".
    E) The web service leaves out the tracks of medium 2 and the relationships of medium 1's recordings (as MusicBrainz does
       with very many recordings): both are read from MB's own pages of tracks (/ws/js/tracks/<medium id>) – the dialog
       still offers medium 2 with its 2 tracks, and track 1 keeps its work (3 tracks without a work, not 4); the log names it."""
    import re

    H.MEDIA = [1, 2, 1, 0]
    orig = H.discogs_release


    def rel():
        d = orig()
        for i, t in enumerate(d['tracklist']):
            t['position'] = ['1-1', '2-1', '2-2', '3-1'][i]
        return d


    H.discogs_release = rel
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    # MB's editor as MusicBrainz builds it: media 2 and 3 folded and not loaded; medium 2 is loaded in part first
    EDITOR = """(() => { const st = MB.relationshipEditor.state; window.__saved = {}; window.__clicks = []; window.__more = []; window.__all = 0;
  for (const m of st.entity.mediums) if (m.position > 1 && m.track_count) { window.__saved[m.id] = m.tracks; m.tracks = null; }
  const box = document.createElement('div');
  box.innerHTML = '<button type="button" id="expand-all-mediums">Expand all mediums</button><table id="mb-media"></table>';
  const t = box.querySelector('table');
  for (const m of st.entity.mediums) {
    const open = m.position === 1;
    t.insertAdjacentHTML('beforeend', `<tbody><tr class="subh"><td></td><td><input type="checkbox" class="medium-recordings"> <a class="expand-medium"
      href="/medium/x${m.position}" id="disc${m.position}"><span>${m.position}</span><span class="expand-triangle">${open ? '\\u25BC' : '\\u25B6'}</span>CD</a></td></tr></tbody>
      <tbody${open ? '' : ' style="display: none"'}></tbody>`);
  }
  document.getElementById('editor').append(box);
  const load = (m) => setTimeout(() => {
    const body = document.getElementById('disc' + m.position).closest('tbody').nextElementSibling;
    const all = window.__saved[m.id] || [];
    if (m.position === 2) {
      st.loadedTracks.set(m.id, all.slice(0, 1));
      body.innerHTML = '<tr><td>This medium has too many tracks to load at once; <a class="load-tracks" href="#">Load all tracks...</a></td></tr>';
    } else st.loadedTracks.set(m.id, all);
  }, 400);
  const expand = (m) => { const a = document.getElementById('disc' + m.position); const tri = a.querySelector('.expand-triangle');
    if (tri.textContent === '\\u25BC') return; tri.textContent = '\\u25BC'; a.closest('tbody').nextElementSibling.style.display = '';
    if (window.__saved[m.id]) load(m); };
  box.addEventListener('click', (e) => {
    const a = e.target.closest('a.expand-medium, a.load-tracks, #expand-all-mediums'); if (!a) return; e.preventDefault();
    if (a.id === 'expand-all-mediums') { window.__all++; st.entity.mediums.forEach(expand); return; }
    if (a.classList.contains('load-tracks')) { const m = st.entity.mediums.find((x) => x.position === 2); window.__more.push(2);
      setTimeout(() => { st.loadedTracks.set(m.id, window.__saved[m.id]); a.closest('tr').remove(); }, 400); return; }
    const p = Number(a.id.slice(4)); window.__clicks.push(p); expand(st.entity.mediums.find((x) => x.position === p));
  });
})()"""
    DLG = """(() => { const d = document.querySelector('[data-el=media]'); if (!d || d.hidden) return null; const w = d.querySelector('[data-mel=works]');
  return { intro: d.querySelector('.dci-media-body p').textContent.trim(), empty: (d.querySelector('[data-mel=empty]') || {}).textContent || '',
    media: [...d.querySelectorAll('[data-mact=toggle]')].map(b => b.textContent.trim()),
    load: d.querySelector('[data-mf=load]').checked, state: d.querySelector('[data-mel=load]').textContent.trim(), works: !w.hidden,
    n: d.querySelector('[data-mel=works-n]').textContent.trim(), time: d.querySelector('[data-mel=works-time]').textContent.trim(),
    pressed: [...d.querySelectorAll('[data-mact=works][aria-pressed=true]')].map(b => b.dataset.w) }; })()"""
    results = []


    def start(ctx):
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.evaluate("localStorage.setItem('dci-aw-ask', '2')")
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.evaluate(EDITOR)
        H.open_dashboard(pg, media=False)
        pg.wait_for_selector('[data-el=media] [data-mact=ok]', timeout=30000)
        pg.wait_for_timeout(300)
        return pg, errs


    def loaded(pg, n):
        H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= 1", 60)
        for m in n:
            H.wait_for(pg, f"{LOGS}.some(x => /Medium {m} (loaded|did not load) in the editor/.test(x))", 40)
        pg.wait_for_timeout(1000)


    real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = start(ctx)
        # A)
        a1 = pg.evaluate(DLG)
        pg.fill('[data-el=media] [data-mf=text]', '1')
        pg.wait_for_timeout(200)
        a2 = pg.evaluate(DLG)
        pg.locator('[data-el=media] [data-mact=all]').click()
        pg.wait_for_timeout(200)
        print('A) Dialog:', a1)
        print('   nur Medium 1:', a2['state'], a2['works'])
        results.append(a1 is not None and a1['intro'].startswith('This release has 4 media.') and len(a1['media']) == 3
                       and a1['empty'].startswith('Without a tracklist in MusicBrainz: medium 4 – add its tracks in the release editor first')
                       and not a1['load'] and a1['state'] == '(2 of them not loaded yet: 2-3)' and a1['works']
                       and a1['n'] == '3 tracks without a work in the chosen media:' and 'about 1 min' in a1['time'] and a1['pressed'] == ['yes']
                       and a2['state'] == '(all of them loaded)' and not a2['works'])
        # B)
        q0 = len(H.WORK_QUERIES)
        pg.locator('[data-el=media] [data-mf=load]').check()
        pg.locator('[data-el=media] [data-mact=works][data-w=no]').click()
        pg.locator('[data-el=media] [data-mact=ok]').click()
        loaded(pg, [2, 3])
        logs = pg.evaluate(LOGS)
        bg = next((i for i, x in enumerate(logs) if 'in the background' in x), 99)
        chosen = next((i for i, x in enumerate(logs) if x.startswith('Works of the tracks without a work')), -1)
        log = [x for x in logs if re.search(r'loaded in the editor|in the background|media choice|no tracklist', x)]
        b1 = [pg.evaluate("window.__all"), pg.evaluate("window.__clicks"), pg.evaluate("window.__more"), pg.evaluate("localStorage.getItem('dci-media-load')"),
              pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(m => m.textContent.trim()).filter(t => /loaded in the editor/.test(t))"),
              bool(pg.evaluate("document.querySelector('[data-el=works-lookups-off]')")), len(H.WORK_QUERIES) - q0, bg < chosen]
        print('B) Alle aufklappen, Klicks, „Load all tracks“, gemerkt, Meldung, Werk-Hinweis, Abfragen, vor dem Lesen der Quelle:', b1)
        print('   Protokoll:', log)
        results.append(b1 == [1, [], [2], 'true', ['2 media are loaded in the editor.'], True, 0, True]
                       and 'Media 2-3 are loaded in the editor in the background' in log and 'Medium 2 loaded in the editor' in log
                       and 'Medium 3 loaded in the editor' in log and 'Works of the tracks without a work (media choice): Not now' in log
                       and 'Medium 4 has no tracklist in MusicBrainz – nothing can be imported for it' in log)
        print('Fehler:', real(errs))
        results.append(not real(errs))
        pg.close()
        # C) skip the works matrix in the dialog
        pg, errs = start(ctx)
        c0 = pg.evaluate(DLG)
        pg.locator('[data-el=media] [data-mact=works][data-w=skip]').click()
        pg.locator('[data-el=media] [data-mact=ok]').click()
        loaded(pg, [2, 3])
        c1 = [pg.evaluate(f"localStorage.getItem('dci-works-skip:{H.REL}')"), (pg.evaluate("(document.querySelector('[data-el=works] .dci-works-skipped') || {}).textContent") or ''),
              pg.evaluate("!document.querySelector('[data-el=works-ask]')")]
        print('C) Dialog vorher:', c0['load'], c0['state'], '| übersprungen:', c1)
        results.append(c0['load'] and c1 == ['true', 'skipped', True])
        pg.evaluate(f"localStorage.removeItem('dci-works-skip:{H.REL}')")
        pg.close()
        # D) media 1 and 3 only: the toggle of medium 3, not "Expand all mediums"
        pg, errs = start(ctx)
        pg.fill('[data-el=media] [data-mf=text]', '1, 3')
        pg.wait_for_timeout(200)
        pg.locator('[data-el=media] [data-mact=ok]').click()
        loaded(pg, [3])
        d1 = [pg.evaluate("window.__all"), pg.evaluate("window.__clicks"), pg.evaluate("window.__more")]
        print('D) Medien 1 und 3 – alle aufklappen, Klicks, „Load all tracks“:', d1)
        results.append(d1 == [0, [3], []])
        pg.close()
        # E) the web service leaves out the tracks of medium 2 and the relationships of medium 1
        H.WS_DROP_TRACKS.add(2)
        H.WS_NO_RELS.add(1)
        pg, errs = start(ctx)
        e0 = pg.evaluate(DLG)
        logs = pg.evaluate(LOGS)
        e1 = [x for x in logs if re.search(r'web service left out|read from the relationship editor', x)]
        print('E) Dialog:', e0['media'], e0['n'], '| Seiten:', H.JS_TRACKS_CALLS, '| Protokoll:', e1)
        results.append(e0['media'] == ['Medium 1 · CD (1 track)', 'Medium 2 · CD (2 tracks)', 'Medium 3 · CD (1 track)']
                       and e0['n'] == '3 tracks without a work in the chosen media:' and (4501, 1) in H.JS_TRACKS_CALLS and (4502, 1) in H.JS_TRACKS_CALLS
                       and e1 == ['MusicBrainz’s web service left out tracks or relationships of medium 1-2: read from the relationship editor',
                                  'Medium 1: 1 track read from the relationship editor', 'Medium 2: 2 tracks read from the relationship editor'])
        pg.locator('[data-el=media] [data-mact=ok]').click()
        H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= 1", 60)
        pg.wait_for_timeout(800)
        pg.evaluate("localStorage.removeItem('dci-aw-ask'); localStorage.removeItem('dci-media-load')")
        print('Fehler:', real(errs))
        results.append(not real(errs))
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_mediasel():
    """Media choice before the import (release with three media): "All" with the release level is the import as before;
    media 2-3 without the release level: only their credits, credits without tracks on their tracks, nothing on the
    release (group), works matrix and medium filter only with those media; "Choose media …" asks again (after a
    confirmation); a remembered choice is preselected next time (still asked); unknown media in the text field;
    cancelling keeps the import, Escape on the first question imports nothing (a message offers the question again)."""
    import re

    H.MEDIA = [2, 1, 1]
    orig = H.discogs_release


    def rel():
        d = orig()
        pos = ['1-1', '1-2', '2-1', '3-1']
        for i, t in enumerate(d['tracklist']):
            t['position'] = pos[i]
        for e in d['extraartists']:
            if e['name'] == 'Keys Guy':
                e['tracks'] = '2-1'
            if e['name'] == 'Drum Guy':
                e['tracks'] = '1-1 to 1-2'
        return d


    H.discogs_release = rel
    DLG = '[data-el=media]'
    STATE = """(() => {
  const groups = [...document.querySelectorAll('#dci-overlay section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent,
    [...g.querySelectorAll('tr.dci-row')].map(tr => (tr.className.match(/dci-lv-(\\w+)/) || [])[1] + ((tr.querySelector('[data-tcount]') || {}).textContent ? ':' + tr.querySelector('[data-tcount]').textContent.trim() : ''))]);
  const matrix = [...new Set([...document.querySelectorAll('.dci-matrix tr[data-work]')].map(tr => Number(tr.dataset.work)))];
  const cols = [...document.querySelectorAll('[data-colhead]')].map(h => h.dataset.colhead.startsWith('mb:') ? 'mb' : (h.querySelector('.dci-mx-name, strong') || h).textContent.trim().slice(0, 20));
  const filter = [...document.querySelectorAll('[data-f=medium-filter] option')].map(o => o.textContent.trim());
  const now = (document.querySelector('.dci-media-now') || {}).textContent || '';
  return { groups, matrix, cols, filter, now };
})()"""
    results = []


    def dialog(pg):
        pg.wait_for_selector(f'{DLG} [data-mact=ok]', timeout=20000)
        return pg.evaluate(f"""(() => {{ const d = document.querySelector('{DLG}');
      return {{ pressed: [...d.querySelectorAll('[data-mact=toggle]')].filter(b => b.getAttribute('aria-pressed') === 'true').map(b => Number(b.dataset.m)),
        text: d.querySelector('[data-mf=text]').value, release: d.querySelector('[data-mf=release]').checked,
        remember: d.querySelector('[data-mf=remember]').checked, sum: d.querySelector('[data-mel=sum]').textContent,
        err: d.querySelector('[data-mel=err]').hidden ? '' : d.querySelector('[data-mel=err]').textContent,
        ok: !d.querySelector('[data-mact=ok]').disabled, hint: d.querySelector('.dci-media-body > p.dci-sub').textContent }}; }})()""")


    def done(pg):
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)


    def names(st):
        return sorted(g[0] for g in st['groups'])


    def clear_log(pg):
        pg.evaluate("document.querySelector('#dci-log [data-log-act=clear]').click()")


    def ok_click(pg):
        # the log is kept in the session: cleared, so "Import complete" is the one of this import
        clear_log(pg)
        pg.click(f'{DLG} [data-mact=ok]')


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg, media=False)

        # A) the question, preselected "All" with the release level: the import as before
        q = dialog(pg)
        print('A1) Frage:', q)
        ok_a = q['pressed'] == [1, 2, 3] and q['text'] == '1-3' and q['release'] and not q['remember'] and q['sum'] == '3 of 3 media · 4 tracks' and q['ok']
        ok_click(pg)
        done(pg)
        base = pg.evaluate(STATE)
        print('A2) alle Medien:', base)
        ok_a = ok_a and 'Drum Guy' in names(base) and 'Photo Guy' in names(base) and 'Sony' in names(base) and base['matrix'] == [0, 1, 2, 3] \
            and base['now'] == 'all media with the release level' and base['filter'][0] == 'all' and len(base['filter']) == 4
        results.append(ok_a)

        # B) "Choose media …": media 2-3 without the release level
        pg.click('[data-act=media-choose]')
        q = dialog(pg)
        pg.fill(f'{DLG} [data-mf=text]', '2-3')
        pg.click(f'{DLG} [data-mf=release]')
        q = dialog(pg)
        print('B1) Frage mit „2-3“, ohne Release-Ebene:', q['pressed'], q['release'], q['sum'])
        ok_b = q['pressed'] == [2, 3] and not q['release'] and q['sum'] == '2 of 3 media · 2 tracks'
        ok_click(pg)
        done(pg)
        st = pg.evaluate(STATE)
        print('B2) Zeilen:', st['groups'])
        print('    Matrix:', st['matrix'], st['cols'], '| Filter:', st['filter'], '| Auswahl:', st['now'])
        g = dict(st['groups'])
        logs = pg.locator('#dci-log li').all_inner_texts()
        print('    Protokoll:', [x for x in logs if 'Media' in x])
        ok_b = ok_b and names(st) == ['Abbey Road Studios', 'Bass Man', 'Bob Producer', 'Ghost Pub', 'Guitar Guy', 'Keys Guy', 'Other Pub', 'Pub Co', 'Writer Z'] \
            and g['Bass Man'] == ['recording:2 of 2 tracks'] and g['Keys Guy'] == ['recording:1 of 2 tracks'] and g['Abbey Road Studios'] == ['recording:2 of 2 tracks'] \
            and st['matrix'] == [2, 3] and not any('Writer W' in c for c in st['cols']) and any('Writer Z' in c for c in st['cols']) \
            and st['now'] == 'media 2-3 without the release level' and len(st['filter']) == 3 and not any(o.startswith('Medium 1 ') for o in st['filter']) \
            and any('Media chosen: media 2-3 without the release level' in x for x in logs)
        results.append(ok_b)

        # C) only medium 1 (buttons), with the release level, remembered; cancelling later keeps that import
        pg.click('[data-act=media-choose]')
        dialog(pg)
        pg.click(f'{DLG} [data-mact=none]')
        q0 = dialog(pg)
        pg.click(f'{DLG} [data-mact=toggle][data-m="1"]')
        pg.check(f'{DLG} [data-mf=remember]')
        q = dialog(pg)
        print('C1) „Keine“:', q0['text'] or '–', q0['ok'], '| Medium 1:', q['text'], q['pressed'], q['release'])
        ok_c = q0['text'] == '' and q0['ok'] and q['text'] == '1' and q['pressed'] == [1] and q['release']
        ok_click(pg)
        done(pg)
        st = pg.evaluate(STATE)
        print('C2) Zeilen:', names(st), '| Matrix:', st['matrix'], '| Filter:', st['filter'], '| Auswahl:', st['now'])
        ok_c = ok_c and names(st) == ['Abbey Road Studios', 'Ann Rep', 'Bass Man', 'Bob Producer', 'Drum Guy', 'Ghost Pub', 'Guitar Guy', 'Other Pub', 'Photo Guy', 'Pub Co', 'Sony', 'Writer W'] \
            and st['matrix'] == [0, 1] and st['filter'] == [] and st['now'] == 'media 1 with the release level'
        stored = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-media-sel'))['{H.REL}']")
        print('    gemerkt:', stored)
        ok_c = ok_c and stored['media'] == [1] and stored['release'] is True
        pg.click('[data-act=media-choose]')
        q = dialog(pg)
        print('C3) erneut gefragt, vorausgewählt:', q['pressed'], q['remember'], '|', q['hint'][:40])
        pg.click(f'{DLG} [data-mact=cancel]'); pg.wait_for_timeout(300)
        st2 = pg.evaluate(STATE)
        ok_c = ok_c and q['pressed'] == [1] and q['remember'] and q['hint'].startswith('Preselected') and names(st2) == names(st) \
            and pg.locator(DLG).is_hidden()
        results.append(ok_c)

        # D) after reloading: still asked (remembered choice preselected); unknown media; Escape imports nothing
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg, media=False)
        q = dialog(pg)
        pg.fill(f'{DLG} [data-mf=text]', '1-4, x')
        bad = dialog(pg)
        pg.fill(f'{DLG} [data-mf=text]', '1, 3')
        q2 = dialog(pg)
        print('D1) nach Neuladen:', q['pressed'], q['remember'], '| „1-4, x“:', bad['err'], bad['ok'], '| „1, 3“:', q2['pressed'], q2['ok'])
        ok_d = q['pressed'] == [1] and q['remember'] and 'Not a medium of this release: 4, x (media: 1-3)' == bad['err'] and not bad['ok'] \
            and q2['pressed'] == [1, 3] and q2['ok'] and q2['err'] == ''
        pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
        msg = pg.locator('[data-el=msgs]').inner_text()
        print('D2) Escape:', pg.locator(DLG).is_hidden(), '| Nachricht:', re.sub(r'\s+', ' ', msg), '| Zeilen:', pg.locator('#dci-overlay section.dci-group').count())
        ok_d = ok_d and pg.locator(DLG).is_hidden() and 'Import cancelled' in msg and pg.locator('#dci-overlay section.dci-group').count() == 0
        pg.click('[data-el=msgs] [data-act=media-choose]')
        dialog(pg)
        pg.click(f'{DLG} [data-mact=all]')
        pg.uncheck(f'{DLG} [data-mf=remember]')
        ok_click(pg)
        done(pg)
        st = pg.evaluate(STATE)
        same = sorted(map(str, st['groups'])) == sorted(map(str, base['groups'])) and st['matrix'] == base['matrix'] and st['cols'] == base['cols']
        if not same:
            print('   vorher:', base); print('   jetzt: ', st)
        print('D3) „Alle“ mit Release-Ebene wie vorher:', same, '| gemerkt:', pg.evaluate("localStorage.getItem('dci-media-sel')"))
        ok_d = ok_d and same and pg.evaluate("localStorage.getItem('dci-media-sel')") is None
        results.append(ok_d)
        print('Fehler:', errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_gapwhy3105():
    """Credits Importer 3.105.0 (collected item Z-GAPL): why the line of the release page is missing – developer mode only.
    A) Developer mode and "show why it is missing" on, the page with a box of external links without Discogs or Bandcamp: a grey note
       "… no Discogs or Bandcamp link recognized among the 1 external links of the page." (no line).
    B) The Discogs link among them: the line as before, no note.
    C) Discogs not reachable (the request broken off): "… the request to Discogs (release …) was broken off: …".
    D) The setting on, developer mode off: no note (A again: nothing). ⚙ Settings → Sources: the switch only in developer mode."""
    orig = H.mb_release_page
    REL = H.REL
    WHY = "(() => { const b = document.querySelector('.dci-gapwhy'); return b ? [b.dataset.why, b.textContent] : null; })()"

    def page(links):
        lis = ''.join(f'<li><a href="{u}">{u}</a></li>' for u in links)
        return lambda: f'<!doctype html><html lang="en"><head><title>Testalbum</title></head><body><div id="content"><h1>Testalbum</h1></div><ul class="external_links">{lis}</ul></body></html>'
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            H.mb_release_page = page(['https://example.com/x'])
            pr, errs = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{REL}')
            pr.evaluate("localStorage.setItem('dci-dev', 'true'); localStorage.setItem('dci-gap-why', 'true')")
            pr.reload()
            H.wait_for(pr, "!!document.querySelector('.dci-gapwhy[data-why=noLink]')", 20)
            a = pr.evaluate(WHY)
            print('A)', a)
            # ([Z-GAPL3] 3.107.0) with the script's name; ([Z-GAPL2]) how many lists of links
            results.append(bool(a) and a[1] == 'MB x Vibecode: Credits Importer – line of the release page (developer mode): no Discogs or Bandcamp link recognized among'
                           ' the 1 external links of the page (lists of links: 1).'
                           and not pr.locator('.dci-gapline').count())
            H.mb_release_page = page([f'https://www.discogs.com/release/{H.DISCOGS_ID}-Test-Band-Testalbum'])
            pr.reload()
            H.wait_for(pr, "!!document.querySelector('.dci-gapline')", 20)
            bb = [pr.locator('.dci-gapline').count(), pr.evaluate(WHY)]
            print('B)', bb)
            results.append(bb == [1, None])
            pr.evaluate(f"Object.keys(localStorage).filter(k => k.startsWith('dci-gap:')).forEach(k => localStorage.removeItem(k))")
            pr.route('**/api.discogs.com/**', lambda r: r.abort())
            pr.reload()
            H.wait_for(pr, "!!document.querySelector('.dci-gapwhy[data-why=dgBroken]')", 30)
            c = pr.evaluate(WHY)
            print('C)', c)
            results.append(bool(c) and c[1].startswith(f'MB x Vibecode: Credits Importer – line of the release page (developer mode): the request to Discogs (release {H.DISCOGS_ID}) was broken off:'))
            pr.unroute('**/api.discogs.com/**')
            H.mb_release_page = page(['https://example.com/x'])
            pr.evaluate("localStorage.removeItem('dci-dev')")
            pr.reload()
            pr.wait_for_timeout(2500)
            dd = pr.evaluate(WHY)
            print('D)', dd)
            results.append(dd is None)
            print('Fehler:', errs)
            results.append(not errs)
            # the switch only in developer mode – ([Z-DEVTAB] 3.108.0) in the tab "Developer" (no longer in Sources; the tab only then)
            ctx2 = H.new_context(b)
            pg, errs2 = H.open_mb_edit(ctx2, companion=False)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.open_settings(pg, 'sources')
            off = pg.locator('[data-el=settings] [data-set=gap-why]').count() + pg.locator('[data-el=settings] .dci-set-tab[data-topic=developer]').count()
            pg.evaluate("localStorage.setItem('dci-dev', 'true')")
            pg.reload()
            pg.add_script_tag(content=H.MAIN)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.open_settings(pg, 'sources')
            in_src = pg.locator('[data-el=settings] [data-set=gap-why]').count()
            H.open_settings(pg, 'developer')
            on = pg.locator('[data-el=settings] [data-set=gap-why]').count()
            print('   Schalter: ohne', off, 'mit (Sources, Developer)', in_src, on)
            results.append(off == 0 and in_src == 0 and on == 1)
            b.close()
    finally:
        H.mb_release_page = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_gapl3107():
    """Credits Importer 3.107.0 (collected item Z-GAPL2): another script's list of links (the same class "external_links", above the release's
    own – "Ame" with search links) does not hide the line: the Discogs link of the release's list below it counts. Without any Discogs or
    Bandcamp link in all lists (developer mode): the note names the links of all of them."""
    orig = H.mb_release_page
    REL = H.REL

    def page(own):
        other = '<h2>Ame</h2><ul class="external_links"><li><a href="https://search.minc.or.jp/x">minc</a></li><li><a href="https://covers.musichoarders.xyz/?a=1">covers</a></li></ul>'
        lis = ''.join(f'<li><a href="{u}">{u}</a></li>' for u in own)
        return lambda: (f'<!doctype html><html lang="en"><head><title>Testalbum</title></head><body><div id="content"><h1>Testalbum</h1></div><div id="sidebar">{other}'
                        f'<h2 class="external-links">External links</h2><ul class="external_links">{lis}</ul></div></body></html>')
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            H.mb_release_page = page([f'https://www.discogs.com/release/{H.DISCOGS_ID}', 'https://harmony.pulsewidth.org.uk/release?x=1'])
            pr, errs = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{REL}')
            pr.evaluate("localStorage.setItem('dci-dev', 'true'); localStorage.setItem('dci-gap-why', 'true')")
            pr.reload()
            H.wait_for(pr, "!!document.querySelector('.dci-gapline') || !!document.querySelector('.dci-gapwhy:not([data-why=start])')", 30)
            a = [pr.locator('.dci-gapline').count(), pr.evaluate("(document.querySelector('.dci-gapwhy') || {}).dataset ? document.querySelector('.dci-gapwhy').dataset.why : null")]
            print('A)', a)
            results.append(a == [1, None])
            H.mb_release_page = page(['https://example.com/y'])
            pr.reload()
            H.wait_for(pr, "!!document.querySelector('.dci-gapwhy[data-why=noLink]')", 20)
            t = pr.evaluate("document.querySelector('.dci-gapwhy').textContent")
            print('B)', t)
            results.append(t.endswith('among the 3 external links of the page (lists of links: 2).'))
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.mb_release_page = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_gapcenter3120():
    """Credits Importer 3.120.0 (collected item Z-GAPCENTER): the line on the release page – its text in the middle of the box (review: the
    columns beside it as wide as each other), the buttons beside it on the same line, ✕ at the end; the list of parts below, the whole width."""
    REL = H.REL
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pr, errs = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{REL}')
        H.wait_for(pr, "!!document.querySelector('.dci-gapline [data-gap-text]')", 30)
        g = pr.evaluate("""(() => { const box = document.querySelector('.dci-gapline'); const t = box.querySelector('[data-gap-text]');
          const r = (x) => x.getBoundingClientRect(); const bt = r(t), bc = r(box.querySelector('[data-gap=count]')), bx = r(box.querySelector('[data-gap=close]'));
          return { align: getComputedStyle(t).textAlign, sameLine: Math.abs((bt.top + bt.bottom) / 2 - (bc.top + bc.bottom) / 2) < 3, countRight: bc.left >= bt.right - 1,
            closeLast: bx.left >= bc.right - 1, centred: t.getClientRects().length === 1 ? Math.abs((bt.left + bt.right) / 2 - (r(box).left + r(box).right) / 2) < 8 : true }; })()""")
        pr.click('.dci-gapline [data-gap=parts]')
        g['list'] = pr.evaluate("(() => { const box = document.querySelector('.dci-gapline'), ul = box.querySelector('[data-gap-parts]'); return !ul.hidden && ul.getBoundingClientRect().top > box.querySelector('[data-gap-text]').getBoundingClientRect().bottom - 1; })()")
        print('A)', g)
        results.append(g == {'align': 'center', 'sameLine': True, 'countRight': True, 'closeLast': True, 'centred': True, 'list': True})
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
