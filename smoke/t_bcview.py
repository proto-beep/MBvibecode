"""Credits Importer 3.17.0 / Companion 1.8.0: the Bandcamp view (collected items 4 and 7).
A) Bandcamp loaded (digital release), a Discogs tab open but no Bandcamp tab: the view names Bandcamp ("no Bandcamp
   tab"), "open in background" opens the album; the Discogs tab gets no marks.
B) A Bandcamp tab on another album: "a Bandcamp tab is open, but on another page" – "Load the release there" loads the
   album; then "connected".
C) Status marks only in the credits, before each part of a line: "Written by Jane Roe, mixed by Bob Mix" two marks,
   "Mixed and mastered by Mark Master" two marks at the same place, none for "Thanks Mom." and none in the "about"
   text (also when Bandcamp shortened it: "more").
D) A click on a mark shows its row in the dashboard ("From Bandcamp: …") – since 3.17.5 with "Click switches" off (on, a
   click switches the credit, see t_bcoff.py).
E) A row jumps to its part of the line; a place from the "about" text marks only its sentence (the shortened text is
   opened), the row says "From the “about” text"; a track of the works matrix highlights its row of the track table;
   the pointer on a track of the Bandcamp page highlights its row in the works matrix.
F) Credits of track pages: the row links its track pages ("From the track page: 2"); a jump loads the track page,
   which has a mark for its own credit only; the same place on two track pages is one row for both tracks (since
   3.16.1 the tracks had not been joined). Back on the album: staged credits ● ; after "Enter edit" the MB release page
   checks them: ✓.
G) The menu: topic "Discogs and Bandcamp view", "Bandcamp status", no cover button; an old companion (before 1.8.0):
   "needs the companion script 1.8.0"."""
import re
from playwright.sync_api import sync_playwright
import harness as H

H.attr(9120, 'trumpet', 14, 14)
H.attr(9121, 'viola', 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
BAND = 'https://testband.bandcamp.com'
ALBUM = f'{BAND}/album/testalbum'
OTHER = f'{BAND}/album/other'
H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
CREDITS = ('Written by Jane Roe, mixed by Bob Mix\nMixed and mastered by Mark Master\nTest Band – guitar\nTrumpet: Peter Evans\n'
           'Thanks Mom.\nPhotography Tom Barrett')
ABOUT = ('This album took a long time to make, and it went through many rooms and many hands before it was done. '
         '\nRecorded at Loft in Cologne, june 16/17 2018. It was a warm summer.')
TRACK_CREDITS = {1: 'Recorded at Studio X', 2: 'Viola: Anna Viola', 3: 'Recorded at Studio X'}
TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': CREDITS, 'about': ABOUT,
                               'release_date': '01 Jan 2020 00:00:00 GMT'}, 'trackinfo': TRACKS}, ALBUM, about_cut=60, credits_cut=70)
for i, t in enumerate(TRACKS):
    url = f'{BAND}{t["title_link"]}'
    H.BC_PAGES[url] = H.bc_html({'artist': 'Test Band', 'album_url': '/album/testalbum', 'current': {'title': t['title'], 'credits': TRACK_CREDITS.get(i + 1, '')},
                                 'trackinfo': [t]}, url)
H.BC_PAGES[OTHER] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Other', 'credits': 'Bass: Nobody'}, 'trackinfo': TRACKS[:1]}, OTHER)
orig_ws = H.ws_release


def ws():
    d = orig_ws()
    d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}})
    for m in d['media']:
        m['format'] = 'Digital Media'
    return d


H.ws_release = ws
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
SYNC = "document.querySelector('[data-el=sync] .dci-syncstatus').textContent.replace(/\\s+/g, ' ').trim()"
MARKS = """(sel) => { const root = document.querySelector(sel); if (!root) return null;
  return [...root.querySelectorAll('.dci-dg-mark')].map(m => { const r = document.createRange(); r.setStartAfter(m); r.setEnd(root, root.childNodes.length);
    const f = r.cloneContents(); f.querySelectorAll('.dci-dg-mark, .dci-bc-off').forEach(x => x.remove());
    return [m.textContent, f.textContent.replace(/\\s+/g, ' ').trim().slice(0, 16), m.title.split(':')[0]]; }); }"""
HL = "[...document.querySelectorAll('.dci-bc-hl')].map(x => x.textContent).join('').replace(/\\s+/g, ' ').trim()"
results = []


def marks(bc, sel='.tralbum-credits'):
    return bc.evaluate(f"({MARKS})('{sel}')")


def row_of(pg, name, role):
    return pg.evaluate("""([n, r]) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === n);
      const tr = g && [...g.querySelectorAll('tr.dci-row')].find(t => t.querySelector('.dci-drole').textContent.trim() === r); return tr ? tr.dataset.row : null; }""", [name, role])


def poll(pg, js, timeout=20):
    """Waits for a condition on a page that may be loading another page meanwhile."""
    for _ in range(timeout * 5):
        try:
            if pg.evaluate(js):
                return True
        except Exception:
            pass
        pg.wait_for_timeout(200)
    raise TimeoutError(js)


def jump(pg, bc, name, role, wait="!!document.querySelector('.dci-bc-hl')"):
    rid = row_of(pg, name, role)
    bc.evaluate("document.querySelectorAll('.dci-bc-hl').forEach(x => x.classList.remove('dci-bc-hl'))")
    pg.locator(f'tr[data-row="{rid}"] .dci-drole').click()
    poll(bc, wait)
    bc.wait_for_timeout(300)
    return bc.evaluate(HL)


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg, dgerr = H.open_discogs(ctx)
    pg, errs = H.open_mb_edit(ctx, companion=True, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.wait_for_timeout(3500)
    # A) no Bandcamp tab yet
    a1 = pg.evaluate(SYNC)
    pg.locator('[data-el=sync] [data-act=sync-open]').click()
    pg.wait_for_timeout(300)
    opened = pg.evaluate("window.__opened || []")
    dg_marks = dg.evaluate("document.querySelectorAll('.dci-dg-mark').length")
    print('A) Ansicht:', a1, '| geöffnet:', opened, '| Marken auf Discogs:', dg_marks)
    results.append(a1.startswith('Bandcamp view: no Bandcamp tab') and ALBUM in opened and dg_marks == 0)
    # B) a Bandcamp tab on another album, then "Load the release there"
    bc, bcerr = H.open_bandcamp(ctx, OTHER)
    H.wait_for(pg, f"{SYNC}.includes('on another page')", 20)
    b1 = pg.evaluate(SYNC)
    pg.locator('[data-el=sync] [data-act=sync-load]').click()
    poll(bc, f"location.href === '{ALBUM}'")
    H.wait_for(pg, f"{SYNC}.includes('connected')", 20)
    b2 = pg.evaluate(SYNC)
    print('B) andere Seite:', b1, '| danach:', b2)
    results.append(b1.startswith('Bandcamp view: a Bandcamp tab is open, but on another page') and b2.startswith('Bandcamp view: connected'))
    # C) the marks
    poll(bc, "document.querySelectorAll('.tralbum-credits .dci-dg-mark').length >= 7")
    bc.wait_for_timeout(500)
    c1 = marks(bc)
    c_about = bc.evaluate("document.querySelectorAll('.tralbum-about .dci-dg-mark').length")
    shown = bc.evaluate("[...document.querySelectorAll('.tralbum-credits .bcTruncateMore')].map(x => x.style.display)")
    print('C) Marken:', c1)
    print('   im about-Text:', c_about, '| gekürzte Credits geöffnet:', shown)
    want = [['○', 'Written by Jane ', 'Written By'], ['○', 'mixed by Bob Mix', 'Mixed By'], ['○', 'Mixed and master', 'Mixed By'],
            ['○', 'Mixed and master', 'Mastered By'], ['○', 'Test Band – guit', 'guitar'], ['○', 'Trumpet: Peter E', 'Trumpet'],
            ['○', 'Photography Tom ', 'Photography By']]
    results.append(c1 == want and c_about == 0 and shown == [''])
    # D) a click on a mark: its row in the dashboard (3.17.5: with "Click switches" off)
    pg.locator('[data-el=sync] [data-click-toggle]').click()
    poll(bc, "document.querySelector('.tralbum-credits .dci-dg-mark').title.includes('click to show it')")
    bc.locator('.tralbum-credits .dci-dg-mark').nth(1).click()
    H.wait_for(pg, f"{LOGS}.some(x => /From Bandcamp: Bob Mix/.test(x))", 15)
    d1 = [x for x in pg.evaluate(LOGS) if 'From Bandcamp' in x]
    flash = pg.evaluate("[...document.querySelectorAll('tr.dci-flash')].map(t => t.querySelector('.dci-drole').textContent.trim())")
    print('D) Protokoll:', d1, '| hervorgehoben:', flash)
    results.append(d1 == ['From Bandcamp: Bob Mix – Mixed By'] and flash == ['Mixed By'])
    pg.locator('[data-el=sync] [data-click-toggle]').click()
    # E) jumps: a part of a line, a sentence of the "about" text, a track
    e1 = jump(pg, bc, 'Peter Evans', 'Trumpet')
    e2 = jump(pg, bc, 'Bob Mix', 'Mixed By')
    e3 = jump(pg, bc, 'Mark Master', 'Mastered By')
    e4 = jump(pg, bc, 'Loft', 'Recorded At')
    about_open = bc.evaluate("[...document.querySelectorAll('.tralbum-about .bcTruncateMore')].map(x => x.style.display)")
    hint = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Loft');
      return g ? [...g.querySelectorAll('.dci-sub')].map(x => x.textContent.trim()).filter(t => /about/.test(t)) : null; })()""")
    H.wait_for(pg, f"{SYNC}.includes('credit highlighted')", 10)
    print('E) Sprünge:', [e1, e2, e3, e4], '| about geöffnet:', about_open, '| Hinweis:', hint, '|', pg.evaluate(SYNC))
    pg.locator('.dci-matrix tr[data-work="1"]').first.click(position={'x': 5, 'y': 5})
    H.wait_for(bc, "!!document.querySelector('tr.track_row_view.dci-discogs-highlight')", 15)
    e5 = bc.evaluate("document.querySelector('tr.track_row_view.dci-discogs-highlight').getAttribute('rel')")
    bc.locator('tr[rel="tracknum=3"] .track-title').hover()
    H.wait_for(pg, "!!document.querySelector('.dci-matrix tr.dci-mx-hover')", 15)
    e6 = pg.evaluate("document.querySelector('.dci-matrix tr.dci-mx-hover').dataset.work")
    print('   Track:', e5, '| Maus auf Track 3 → Matrix-Zeile', e6)
    results.append(e1 == 'Trumpet: Peter Evans' and e2 == 'mixed by Bob Mix' and e3 == 'Mixed and mastered by Mark Master'
                   and e4 == 'Recorded at Loft in Cologne, june 16/17 2018.' and about_open == [''] and hint == ['From the “about” text']
                   and e5 == 'tracknum=2' and e6 == '2')
    # F) track pages
    links = pg.evaluate("""(() => [...document.querySelectorAll('.dci-bcpages')].map(d => [d.closest('section').querySelector('.dci-gname strong').textContent.trim(),
      d.textContent.replace(/\\s+/g, ' ').trim(), [...d.querySelectorAll('a')].map(a => a.href)]))()""")
    studio = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Studio X');
      return g ? [...g.querySelectorAll('tr.dci-row')].map(t => t.querySelector('.dci-drole').textContent.trim() + ' · ' + t.querySelector('[data-tcount]').textContent.trim()) : null; })()""")
    print('F) Track-Seiten:', links, '| Studio X:', studio)
    f1 = jump(pg, bc, 'Anna Viola', 'Viola', "location.pathname === '/track/song-2' && !!document.querySelector('.dci-bc-hl')")
    poll(bc, "document.querySelectorAll('.tralbum-credits .dci-dg-mark').length >= 1")
    f2 = marks(bc)
    print('   Sprung auf die Track-Seite:', bc.evaluate("location.pathname"), f1, '| Marken dort:', f2)
    results.append(links == [['Anna Viola', 'From the track page: 2', [f'{BAND}/track/song-2']],
                             ['Studio X', 'From the track pages: 1, 3', [f'{BAND}/track/song-1', f'{BAND}/track/song-3']]]
                   and studio is not None and len(studio) == 1 and studio[0].startswith('Recorded At · 2')
                   and f1 == 'Viola: Anna Viola' and f2 == [['○', 'Viola: Anna Viol', 'Viola']])
    # back on the album, staged, then checked on the release page
    f3 = jump(pg, bc, 'Peter Evans', 'Trumpet', "location.pathname === '/album/testalbum' && !!document.querySelector('.dci-bc-hl')")
    pg.click('[data-act=apply]')
    H.wait_for(bc, "[...document.querySelectorAll('.tralbum-credits .dci-dg-mark')].some(m => m.textContent === '●')", 20)
    f4 = [m for m in marks(bc) if m[0] != '○']
    H.submit_staged(pg)
    pg.goto(f'https://musicbrainz.org/release/{H.REL}')
    H.with_companion(pg)
    H.wait_for(bc, "[...document.querySelectorAll('.tralbum-credits .dci-dg-mark')].some(m => m.textContent === '✓')", 30)
    f5 = [m for m in marks(bc) if m[0] != '○']
    print('   zurück:', f3, '| vorgemerkt:', f4, '| nach „Enter edit“:', f5)
    results.append(f3 == 'Trumpet: Peter Evans' and f4 == [['●', 'Test Band – guit', 'guitar']] and f5 == [['✓', 'Test Band – guit', 'guitar']])
    dg_url = dg.evaluate("location.pathname")
    print('   Discogs-Tab:', dg_url, '| Marken:', dg.evaluate("document.querySelectorAll('.dci-dg-mark').length"))
    results.append(dg_url == f'/release/{H.DISCOGS_ID}-Test-Band-Testalbum' and dg.evaluate("document.querySelectorAll('.dci-dg-mark').length") == 0)
    # the harness' shared storage (synchronous requests) cannot be written while a page is left: not an error of the scripts
    real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]
    print('Fehler:', real(errs), real(bcerr), real(dgerr))
    results.append(not real(errs) and not real(bcerr) and not real(dgerr))
    b.close()

    # G) the menu, and an old companion
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.evaluate("""document.dispatchEvent(new CustomEvent('dci:from-discogs', { detail: JSON.stringify({ type: 'status', tabs: 1,
      target: { id: 'x', visible: true, releaseId: '1234' }, releases: ['1234'] }) }))""")
    pg.wait_for_timeout(300)
    g1 = pg.evaluate(SYNC)
    pg.locator('.dci-head [data-act=settings-open]').click()
    pg.locator('[data-act=settings-topic][data-topic=discogs]').click()
    pg.wait_for_timeout(300)
    # [3.25.0] the topic is a tab, its content the pane
    g2 = pg.evaluate("""(() => { const s = document.querySelector('[data-el=settings]'); const t = s.querySelector('.dci-set-pane');
      return [s.querySelector('[data-act=settings-topic][data-topic=discogs]').textContent.trim(), t.querySelector('[data-dg-status]').textContent.trim(),
        !!t.querySelector('[data-dg-artwork]'), t.querySelector('.dci-sub').textContent.trim().slice(0, 60)]; })()""")
    print('G) alter Companion:', g1, '| Menü:', g2)
    results.append(g1.startswith('Bandcamp view: needs the companion script 1.8.0') and g2[:3] == ['Discogs and Bandcamp view', 'Bandcamp status', False])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
