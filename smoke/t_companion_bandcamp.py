"""Companion on Bandcamp: the Bandcamp view, credits switched off, dates and track groups underlined (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: bcview, bcoff, textmarks – each the former smoke/t_<case>.py, unchanged; `python3 t_companion_bandcamp.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_bcview():
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
    G) The menu: topic "Discogs and Bandcamp view" ([3.30.5] "Source pages"), "Bandcamp status", no cover button; an old companion (before 1.8.0):
       "needs the companion script 1.8.0"."""
    import re

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
        H.nav_switch(pg, 'data-click-toggle')
        poll(bc, "document.querySelector('.tralbum-credits .dci-dg-mark').title.includes('click to show it')")
        bc.locator('.tralbum-credits .dci-dg-mark').nth(1).click()
        H.wait_for(pg, f"{LOGS}.some(x => /From Bandcamp: Bob Mix/.test(x))", 15)
        d1 = [x for x in pg.evaluate(LOGS) if 'From Bandcamp' in x]
        flash = pg.evaluate("[...document.querySelectorAll('tr.dci-flash')].map(t => t.querySelector('.dci-drole').textContent.trim())")
        print('D) Protokoll:', d1, '| hervorgehoben:', flash)
        results.append(d1 == ['From Bandcamp: Bob Mix – Mixed By'] and flash == ['Mixed By'])
        H.nav_switch(pg, 'data-click-toggle')
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
        results.append(g1.startswith('Bandcamp view: needs the companion script 1.8.0') and g2[:3] == ['Source pages', 'Bandcamp status', False])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_bcoff():
    """Credits Importer 3.17.1 / Companion 1.8.1: credits switched off and on on Bandcamp (collected item 5); since 3.17.5 /
    1.8.3 with a click on the mark itself (collected item 20, before: ⊘).
    A) The pointer resting on a mark shows its row in the dashboard (no line in the log); a click on the mark switches the
       credit off: its row goes to "Skip" in the dashboard and says so, its mark is greyed (–) and – as it is the only credit
       of its part – the part of the line too ("mixed by Bob Mix"); the log says it.
    B) A group of marks ("Mixed and mastered by Mark Master"): one credit switched off greys only its mark; both switched off
       grey the text too. A click on a switched-off mark switches it on again: the row has its level back.
    C) Kept for the release: after loading the edit page again and importing anew, the credits switched off are off again.
    D) Choosing a level in the dashboard switches a credit on again (on Bandcamp too).
    E) "Delete stored import" forgets what was switched off."""
    import re

    H.attr(9120, 'trumpet', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    BAND = 'https://testband.bandcamp.com'
    ALBUM = f'{BAND}/album/testalbum'
    H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
    H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
    H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
    CREDITS = 'Written by Jane Roe, mixed by Bob Mix\nMixed and mastered by Mark Master\nTest Band – guitar\nTrumpet: Peter Evans'
    TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
    H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': CREDITS}, 'trackinfo': TRACKS}, ALBUM)
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
    MARKS = """(() => { const root = document.querySelector('.tralbum-credits');
  return [...root.querySelectorAll('.dci-dg-mark')].map(m => [m.textContent, m.title.split(':')[0], m.classList.contains('dci-mark-off')]); })()"""
    GREY = "[...document.querySelectorAll('.tralbum-credits .dci-bc-offtext')].map(x => x.textContent).join('|').replace(/\\s+/g, ' ')"
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


    def row(pg, name, role):
        return pg.evaluate("""([n, r]) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === n);
      const tr = g && [...g.querySelectorAll('tr.dci-row')].find(t => t.querySelector('.dci-drole').textContent.trim() === r);
      if (!tr) return null; const lv = tr.querySelector('[data-act=level][aria-pressed=true]');
      return [tr.dataset.row, lv ? lv.dataset.level : '', !!tr.querySelector('.dci-srcoff')]; }""", [name, role])


    def toggle(bc, k):
        """Clicks the k-th mark (3.17.5: the mark itself switches its credit)."""
        bc.locator('.tralbum-credits .dci-dg-mark').nth(k).click()


    def start(p):
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=True, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        return b, ctx, pg, errs


    real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]

    with sync_playwright() as p:
        b, ctx, pg, errs = start(p)
        bc, bcerr = H.open_bandcamp(ctx, ALBUM)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
        poll(bc, "document.querySelectorAll('.tralbum-credits .dci-dg-mark').length >= 6")
        bc.wait_for_timeout(500)
        # A) the pointer resting on a mark shows its row; a click switches the credit off
        bc.locator('.tralbum-credits .dci-dg-mark').nth(1).hover()
        H.wait_for(pg, "document.querySelectorAll('tr.dci-flash').length > 0", 10)
        hidden = pg.evaluate("[...document.querySelectorAll('tr.dci-flash')].map(t => t.querySelector('.dci-drole').textContent.trim())")
        shown = [x for x in pg.evaluate(LOGS) if 'From Bandcamp' in x]
        bc.mouse.move(5, 5)
        level0 = row(pg, 'Bob Mix', 'Mixed By')[1]
        toggle(bc, 1)
        H.wait_for(pg, f"{LOGS}.some(x => /Bob Mix – Mixed By switched off/.test(x))", 15)
        poll(bc, "[...document.querySelectorAll('.tralbum-credits .dci-dg-mark')][1].classList.contains('dci-mark-off')")
        a1 = row(pg, 'Bob Mix', 'Mixed By')
        a2 = bc.evaluate(MARKS)[1]
        a3 = bc.evaluate(GREY)
        print('A) Zeiger auf der Marke → Zeile:', hidden, '| Protokoll:', shown, '| Zeile:', a1, '(vorher', level0, ') | Marke:', a2, '| grau:', a3)
        results.append(hidden == ['Mixed By'] and shown == [] and a1[1] == 'skip' and a1[2] and a2 == ['–', 'Mixed By', True] and a3 == 'mixed by Bob Mix')
        # B) a group: one off, then both, then one on again
        toggle(bc, 3)
        poll(bc, "[...document.querySelectorAll('.tralbum-credits .dci-dg-mark')][3].classList.contains('dci-mark-off')")
        b1 = [bc.evaluate(MARKS)[2:4], bc.evaluate(GREY)]
        toggle(bc, 2)
        poll(bc, "[...document.querySelectorAll('.tralbum-credits .dci-dg-mark')][2].classList.contains('dci-mark-off')")
        bc.wait_for_timeout(300)
        b2 = bc.evaluate(GREY)
        master = row(pg, 'Mark Master', 'Mastered By')
        toggle(bc, 3)
        poll(bc, "![...document.querySelectorAll('.tralbum-credits .dci-dg-mark')][3].classList.contains('dci-mark-off')")
        bc.wait_for_timeout(300)
        b3 = [row(pg, 'Mark Master', 'Mastered By'), bc.evaluate(GREY)]
        print('B) eins aus:', b1, '| beide aus:', b2, master, '| wieder an:', b3)
        results.append(b1[0] == [['○', 'Mixed By', False], ['–', 'Mastered By', True]] and b1[1] == 'mixed by Bob Mix'
                       and b2 == 'mixed by Bob Mix|Mixed and mastered by Mark Master' and master[1] == 'skip'
                       and b3[0][1] == 'release' and not b3[0][2] and b3[1] == 'mixed by Bob Mix')
        # C) kept for the release
        pg.evaluate("Object.keys(sessionStorage).filter(k => k.startsWith('dci-')).forEach(k => sessionStorage.removeItem(k))")
        pg.reload()
        H.with_companion(pg)
        pg.add_script_tag(content=H.GM_XHR_SHIM)
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
        pg.wait_for_timeout(500)
        c1 = [row(pg, 'Bob Mix', 'Mixed By'), row(pg, 'Mark Master', 'Mixed By'), row(pg, 'Mark Master', 'Mastered By')]
        poll(bc, "[...document.querySelectorAll('.tralbum-credits .dci-dg-mark.dci-mark-off')].length === 2")
        c2 = [m[2] for m in bc.evaluate(MARKS)]
        print('C) nach Neuladen:', c1, '| Marken aus:', c2)
        results.append([x[1] for x in c1] == ['skip', 'skip', 'release'] and c2 == [False, True, True, False, False, False])
        # D) a level chosen in the dashboard switches it on
        rid = row(pg, 'Bob Mix', 'Mixed By')[0]
        pg.locator(f'tr[data-row="{rid}"] [data-act=level][data-level=recording]').click()
        poll(bc, "![...document.querySelectorAll('.tralbum-credits .dci-dg-mark')][1].classList.contains('dci-mark-off')")
        d1 = [row(pg, 'Bob Mix', 'Mixed By'), [m[2] for m in bc.evaluate(MARKS)], [x for x in pg.evaluate(LOGS) if 'switched on' in x][-1:]]
        print('D) Ebene gewählt:', d1)
        results.append(d1[0][1] == 'recording' and not d1[0][2] and d1[1] == [False, False, True, False, False, False]
                       and d1[2] == ['Bandcamp: Bob Mix – Mixed By switched on again'])
        # E) "Delete stored import"
        H.src_menu(pg, 'forget-open')
        pg.locator('[data-act=forget-do]').click()
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
        pg.wait_for_timeout(1500)
        e1 = [row(pg, 'Mark Master', 'Mixed By'), pg.evaluate(f"localStorage.getItem('dci-src-off:{H.REL}')")]
        poll(bc, "document.querySelectorAll('.tralbum-credits .dci-dg-mark.dci-mark-off').length === 0")
        print('E) nach „Gespeicherten Import löschen“:', e1)
        results.append(e1[0][1] != 'skip' and e1[1] is None)
        print('Fehler:', real(errs), real(bcerr))
        results.append(not real(errs) and not real(bcerr))
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_textmarks():
    """Credits Importer 3.28.3 / Companion 1.9.0: the dates and track groups the dashboard uses, underlined in the texts of
    the source (collected item 63).
    A) Discogs: the notes "Dedicated to Jim, 1999." and "Tracks 1-2 recorded March 1–3, 2001 at Abbey Road Studios. Mixed May
       2001." – both dates with a word naming their group go into the date matrix, so "March 1–3, 2001" and "May 2001" are
       underlined in the date colour, "Tracks 1-2" (the track group of its sentence in the matrix) in the track colour;
       "1999" (only in the pool) is not. The tooltip says where the dashboard uses it.
    B) The pool date "1999" dropped onto a row: underlined too ("the date of a row").
    C) "Status on Discogs" switched off: no underlines (and no marks); on again: back.
    D) Bandcamp: "Recorded by Jane Roe in 2020" in the credits and "Tracks 1-2 mixed in July 2019." in the "about" text –
       each underlined in its text, "Tracks 1-2" too ("2020" in its line, not in "released January 1, 2020" above the
       credits); the credit marks are still there.
    E) [1.9.0] Two lines of one artist with the same role ("Vocals [Clean]", "Vocals [Screams]"): a mark on each line."""
    import json

    NOTES = 'Dedicated to Jim, 1999.\nTracks 1-2 recorded March 1–3, 2001 at Abbey Road Studios. Mixed May 2001.'
    orig_rel = H.discogs_release
    orig_page = H.discogs_page
    H.ARTISTS[3015] = (H.uid('dddddddd', 25), 'Valfar')


    def rel():
        d = orig_rel()
        d['notes'] = NOTES
        d['extraartists'] += [{'name': 'Valfar', 'anv': '', 'role': 'Vocals [Clean]', 'tracks': '', 'id': 3015, 'join': ''},
                              {'name': 'Valfar', 'anv': '', 'role': 'Vocals [Screams]', 'tracks': '', 'id': 3015, 'join': ''}]
        return d


    def page():
        extra = ''.join(f'<li><span>{r}</span> – <a href="/artist/3015-Valfar">Valfar</a></li>' for r in ('Vocals [Clean]', 'Vocals [Screams]'))
        p = orig_page().replace('</ul><h2>Companies, etc.</h2>', f'{extra}</ul><h2>Companies, etc.</h2>')
        notes = ('<section id="release-notes"><header><h2>Notes</h2></header><div>Dedicated to Jim, 1999.<br>Tracks 1-2 recorded March 1–3, 2001'
                 ' at Abbey Road Studios. Mixed May 2001.</div></section>')
        return p.replace('</body>', f'{notes}</body>')


    H.discogs_release = rel
    H.discogs_page = page
    UL = """(() => ['dci-txt-date', 'dci-txt-tracks'].map(c => [...document.querySelectorAll('.' + c)].map(s => [s.textContent, s.title])))()"""
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


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg, dgerr = H.open_discogs(ctx)
        pg, errs = H.open_mb_edit(ctx, companion=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        poll(dg, "document.querySelectorAll('#release-notes .dci-txt-date').length >= 2")
        dg.wait_for_timeout(600)
        a1 = dg.evaluate(UL)
        print('A) unterstrichen (Daten, Trackgruppen):', a1)
        results.append([x[0] for x in a1[0]] == ['March 1–3, 2001', 'May 2001'] and [x[0] for x in a1[1]] == ['Tracks 1-2']
                       and all('in the date matrix' in x[1] for x in a1[0] + a1[1])
                       and dg.evaluate("document.querySelector('#release-notes').textContent.replace(/\\s+/g, ' ').includes('Dedicated to Jim, 1999.')"))
        # B) "1999" from the pool onto a row
        dropped = pg.evaluate("""(() => { const src = [...document.querySelectorAll('[data-drag=date]')].find(x => /1999/.test(x.textContent));
      const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bob Producer');
      const dst = g && g.querySelector('tr.dci-row .dci-c-date');
      if (!src || !dst) return [!!src, !!dst];
      const dt = new DataTransfer();
      src.dispatchEvent(new DragEvent('dragstart', { bubbles: true, dataTransfer: dt }));
      dst.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt }));
      dst.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }));
      src.dispatchEvent(new DragEvent('dragend', { bubbles: true, dataTransfer: dt }));
      return [true, true]; })()""")
        print('   gezogen:', dropped)
        pg.wait_for_timeout(500)
        poll(dg, "[...document.querySelectorAll('.dci-txt-date')].some(s => s.textContent === '1999')")
        b1 = dg.evaluate(UL)[0]
        print('B) 1999 auf einer Zeile:', b1)
        results.append(['1999', 'Credits Importer: “1999” is the date of a row'] in b1 and len(b1) == 3)
        # C) status off and on
        H.open_settings(pg, 'discogs')
        pg.locator('[data-el=settings] [data-dg-status]').first.click()
        poll(dg, "!document.querySelector('.dci-txt-date, .dci-txt-tracks, .dci-dg-mark')")
        c1 = dg.evaluate(UL)
        pg.locator('[data-el=settings] [data-dg-status]').first.click()
        poll(dg, "document.querySelectorAll('.dci-txt-date').length >= 3")
        c2 = dg.evaluate(UL)
        print('C) aus:', c1, '| wieder an:', [len(x) for x in c2])
        results.append(c1 == [[], []] and [len(x) for x in c2] == [3, 1])
        # E) two lines of Valfar
        e1 = dg.evaluate("[...document.querySelectorAll('#release-credits li')].filter(li => /Vocals/.test(li.textContent)).map(li => [li.querySelector('span').textContent, li.querySelectorAll('.dci-dg-mark').length])")
        print('E) Valfar:', e1)
        results.append(e1 == [['Vocals [Clean]', 1], ['Vocals [Screams]', 1]])
        print('Fehler:', errs, dgerr)
        results.append(not errs and not dgerr)
        b.close()

    # D) Bandcamp
    H.attr(9121, 'viola', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    BAND = 'https://testband.bandcamp.com'
    ALBUM = f'{BAND}/album/testalbum'
    H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
    H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
    H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
    TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
    H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': 'Recorded by Jane Roe in 2020\nViola: Anna Viola',
                                   'about': 'Tracks 1-2 mixed in July 2019.', 'release_date': '01 Jan 2020 00:00:00 GMT'}, 'trackinfo': TRACKS}, ALBUM)
    for i, t in enumerate(TRACKS):
        url = f'{BAND}{t["title_link"]}'
        H.BC_PAGES[url] = H.bc_html({'artist': 'Test Band', 'album_url': '/album/testalbum', 'current': {'title': t['title'], 'credits': ''},
                                     'trackinfo': [t]}, url)
    orig_ws = H.ws_release


    def ws():
        d = orig_ws()
        d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}})
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d


    H.ws_release = ws
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        bc, bcerr = H.open_bandcamp(ctx, ALBUM)
        pg, errs = H.open_mb_edit(ctx, companion=True, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        poll(bc, "document.querySelectorAll('.dci-txt-date').length >= 2")
        bc.wait_for_timeout(600)
        d1 = bc.evaluate("""(() => ['.tralbum-credits', '.tralbum-about'].map(sel => { const r = document.querySelector(sel);
      return [[...r.querySelectorAll('.dci-txt-date')].map(s => s.textContent), [...r.querySelectorAll('.dci-txt-tracks')].map(s => s.textContent),
        r.querySelectorAll('.dci-dg-mark').length, [...r.querySelectorAll('.dci-txt-date')].map(s => (s.previousSibling || {}).textContent || '')]; }))()""")
        print('D) Bandcamp (Credits, about):', d1)
        results.append([x[:3] for x in d1] == [[['2020'], [], 2], [['July 2019'], ['Tracks 1-2'], 0]] and d1[0][3][0].endswith('Jane Roe in '))
        bcerr = [e for e in bcerr if 'page dismissal' not in e]
        print('Fehler:', errs, bcerr)
        results.append(not errs and not bcerr)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
