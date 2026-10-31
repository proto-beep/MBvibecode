"""Works: the works of the artists, skipping the works matrix (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: artistworks, worksskip, livecom (3.32.9), livecomrun (3.32.10), liveoffer (3.37.3) – each the former smoke/t_<case>.py, unchanged –, livegroup (3.38.3); `python3 t_works_more.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_artistworks():
    """Import 3.15.0: the tracks without a work are compared with all works of the release's artists, its writers and its
    performers (works linked to the artist, and works of the artist's recordings – also covers), in the background.
    A) Track 4 (no writers): the release artist's work "Song Four" is offered ("work of Test Band"), under the heading that
       names the artists. Track 3 (Writer Z, nothing found): the bassist recorded "Song Three" (a cover, "Song Three (live)")
       – offered with that recording. Track 2: the writer's own search and his works find the same work – shown once.
    B) The order: the release's artists first, then the writers, then the performers; the log names the works read and the
       result; a work chosen from these is linked as one found by the search, and goes into the stored works (3.16.0) of the
       artists credited on its track.
    C) Read once per session: a second import (a pasted text) compares again without asking MusicBrainz again (the release
       artist's work is offered again for track 4, whose chosen work was given up).
    D) A large catalogue: an artist with 2,500 recordings takes longer than 10 seconds – a message says why; with the
       setting "at most 2,000 per artist" (3.16.0; default 4,000) only the first 2,000 are read, and a message says so.
    E) A result of the background does not disturb typing: while a date field of the works matrix is being typed in, the
       matrix is not drawn anew (focus and text stay); once the field is left, the work found is shown."""
    H.MAIN = H.MAIN_SLOW  # [3.31.1] the time matters here: the script's own gap between requests to MusicBrainz
    import re

    TB = H.uid('dddddddd', 60)
    BASS, GUITAR, WW, WZ = H.ARTISTS[3001][0], H.ARTISTS[3002][0], H.ARTISTS[3007][0], H.ARTISTS[3009][0]
    W2, W3, W4 = H.uid('cccccccc', 72), H.uid('cccccccc', 73), H.uid('cccccccc', 74)
    H.RELEASE_AC[:] = [(TB, 'Test Band', 'Test Band', '')]
    H.WORK_SEARCH.append({'id': W2, 'title': H.TITLES[1], 'aliases': [], 'type': 'Song',
                          'relations': [{'target-type': 'artist', 'type': 'writer', 'artist': {'id': WW, 'name': 'Writer W'}}]})
    H.ARTIST_WORKS.update({TB: [{'id': W4, 'title': H.TITLES[3], 'type': 'Song', 'aliases': []},
                                {'id': H.uid('cccccccc', 79), 'title': 'Another Song', 'type': 'Song', 'aliases': []}],
                           WW: [{'id': W2, 'title': H.TITLES[1], 'type': 'Song', 'aliases': []}]})
    H.ARTIST_RECORDINGS.update({BASS: [{'title': 'Song Three (live)', 'work': {'id': W3, 'title': H.TITLES[2], 'type': 'Song'}},
                                       {'title': 'Jam', 'work': None}]})
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    SAME = """(i) => { const td = document.querySelector(`tr[data-work="${i}"]`); const s = td && td.querySelector('.dci-same');
  return s ? [s.querySelector('strong').textContent, [...s.querySelectorAll('li')].map(li => [li.querySelector('[data-act=work-pick]').dataset.gid,
    li.querySelector('.dci-sub').textContent.trim()])] : null; }"""


    def same(pg, i):
        return pg.evaluate(f"({SAME})({i})")


    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
        pg.wait_for_timeout(300)
        # A)
        s4, s3, s2 = same(pg, 3), same(pg, 2), same(pg, 1)
        print('A) Track 4:', s4)
        print('   Track 3:', s3)
        print('   Track 2:', s2)
        results.append(s4 is not None and s4[1] == [[W4, 'Song – work of Test Band']] and 'release' in s4[0]
                       and s3 is not None and s3[1] == [[W3, 'Song – recorded by Bass Man (“Song Three (live)”)']]
                       and s2 is not None and [g for g, _ in s2[1]] == [W2] and 'by these writers' in s2[0])
        # B) order of the artists, the log, picking a work
        order = []
        for kind, artist, off in H.BROWSES:
            if artist not in order:
                order.append(artist)
        names = {TB: 'Test Band', WW: 'Writer W', WZ: 'Writer Z', BASS: 'Bass Man', GUITAR: 'Guitar Guy'}
        print('B) Reihenfolge:', [names.get(a, a[-3:]) for a in order])
        log = [x for x in pg.evaluate(LOGS) if 'Works of' in x]
        print('   Protokoll:', log)
        ok_order = order[:3] == [TB, WW, WZ] and BASS in order[3:] and GUITAR in order[3:]
        ok_log = ('Works of Test Band: 2 works read (linked to the artist or recorded by them)' in log
                  and 'Works of the artists compared: 3 works with the same title as a track (1.2, 1.3, 1.4)' in log
                  and not any('Guitar Guy' in x or 'large catalogue' in x for x in log))
        pg.locator('tr[data-work="3"]').locator(f'[data-act=work-pick][data-gid="{W4}"]').evaluate('b => b.click()')
        pg.wait_for_timeout(400)
        picked = [x for x in pg.evaluate(LOGS) if 'chosen for linking' in x]
        # 3.16.0: the work chosen goes into the stored works of the artists credited on the track (Bass Man plays on all tracks)
        pg.wait_for_timeout(500)
        kept = pg.evaluate("""new Promise(r => { const q = indexedDB.open('dci-works', 1); q.onsuccess = () => {
      const t = q.result.transaction('artists').objectStore('artists').get('%s'); t.onsuccess = () => r(t.result ? t.result.works.map(w => w[0]) : null); }; })""" % BASS)
        print('   gespeicherte Werke von Bass Man:', kept)
        print('   gewählt:', picked, '| Track 4 hat Werk:', pg.locator('tr[data-work="3"]').locator('.dci-same').count() == 0)
        results.append(ok_order and ok_log and picked == ['Track 1.4: work “Song Four” chosen for linking'] and kept and W4 in kept and W3 in kept
                       and pg.locator('tr[data-work="3"]').locator('.dci-same').count() == 0)
        # C) a second import: compared again from what was read (the work chosen for track 4 is given up before)
        pg.locator('tr[data-work="3"] [data-act=work-unplan]').evaluate('b => b.click()')
        pg.wait_for_timeout(300)
        n0 = len(H.BROWSES)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Bass – Bass Man')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, f"{LOGS}.filter(x => /Works of the artists compared/.test(x)).length >= 2", 60)
        pg.wait_for_timeout(500)
        s4b = same(pg, 3)
        print('C) neue Anfragen:', len(H.BROWSES) - n0, '| Track 4:', s4b)
        results.append(len(H.BROWSES) == n0 and s4b is not None and s4b[1] == [[W4, 'Song – work of Test Band']])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()

        # D) a large catalogue (a page of its own: the works read are kept per session)
        H.RELEASE_AC[:] = []
        H.ARTIST_WORKS.clear()
        H.ARTIST_RECORDINGS.clear()
        H.ARTIST_RECORDINGS[GUITAR] = 2500
        H.BROWSES.clear()
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        # 3.16.0: at most 2,000 works and recordings per artist (the setting, stored; read when the script starts)
        pg.evaluate("localStorage.setItem('dci-aw-max', '2000')")
        pg.reload(); pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 120)
        msgs = [re.sub(r'\s+', ' ', m) for m in pg.locator('.dci-msg').all_inner_texts() if 'Guitar Guy' in m]
        log = [x for x in pg.evaluate(LOGS) if 'Guitar Guy' in x]
        recs = [off for kind, a, off in H.BROWSES if kind == 'recording' and a == GUITAR]
        print('D) Meldungen:', msgs)
        print('   Protokoll:', log)
        print('   Aufnahmen gelesen bis Offset:', max(recs), '| Anfragen:', len(recs))
        results.append(any('takes a while: a large catalogue (2500 recordings' in m for m in msgs)
                       and any('Guitar Guy has 2500 works and recordings; only the first 2000 were compared' in m for m in msgs)
                       and any('a large catalogue' in x for x in log) and any('only the first 2000 compared' in x for x in log)
                       and len(recs) == 20 and max(recs) == 1900)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()

        # E) typing in the works matrix while the comparison finds a work
        H.ARTIST_RECORDINGS.clear()
        DRUM = H.ARTISTS[3004][0]
        H.ARTIST_RECORDINGS[DRUM] = [{'title': 'Song Four', 'work': {'id': W4, 'title': H.TITLES[3], 'type': 'Song'}}]
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
        pg.locator('[data-colhead] [data-act=mx-colmenu]').first.click(); pg.wait_for_timeout(300)
        pg.locator('[data-f=cd-by]').first.click()
        pg.keyboard.type('19', delay=100)
        H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
        pg.keyboard.type('99', delay=100)
        st = pg.evaluate("(() => { const a = document.activeElement; return [a && a.dataset ? a.dataset.f : '', a && a.value]; })()")
        during = same(pg, 3)
        print('E) beim Tippen:', st, '| Track 4:', during, '|', [x for x in pg.evaluate(LOGS) if 'compared' in x])
        pg.evaluate("document.activeElement.blur()"); pg.wait_for_timeout(1200)
        after = same(pg, 3)
        print('   nach dem Verlassen – Track 4:', after)
        results.append(st == ['cd-by', '1999'] and during is None and after is not None and after[1] == [[W4, 'Song – recorded by Drum Guy (“Song Four”)']])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_worksskip():
    """Credits Importer 3.18.0: the works matrix can be skipped and folded (collected item 26), and with many tracks the
    works section asks before the work lookups.
    A) The head of the works matrix folds and unfolds it ("▾ Works matrix"): folded, only its head and what it holds are
       shown; the fold is not stored (after a reload the matrix is unfolded again).
    B) "Skip works" ([3.32.1] until then "Skip works matrix", item 106): the matrix folds, says "skipped", its rows (writers, publishers) go to "Skip", nothing of it is
       staged (no links to works – also not of works marked as new – and no work relationships); the work lookups stop.
       Stored for this release: after a reload it is still skipped, its rows on "Skip" at once and no work is looked up.
       Meanwhile a row has no works level (the button says why). Before and after, the work rows are in the matrix
       ([3.31.5] a publisher's row also in its entry, on "Works" – item 112).
    C) "Take works again" (until 3.32.0 "Take works matrix again"): the rows come back to the works level, the matrix unfolds, the lookups run.
    D) From so many tracks without a work (setting "Ask before the work lookups from …", 100; here 3) the works section
       asks first, with about how long it takes; nothing is looked up until then. "Not now" leaves out only the lookups
       (the matrix stays); "Look up now" starts them later. The setting is in the menu, topic Works (100 by default).
       [3.19.3] The question and the setting say in a tooltip what is counted (tracks without a work).
    G) [3.19.3] Setting "Show the rows skipped with the works matrix with their entries" (on): off, their entry says how
       many are not shown; on again, they are back."""
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    HEAD = """(() => { const w = document.querySelector('[data-el=works]'); if (!w || w.hidden) return null;
  const f = w.querySelector('[data-act=mx-fold]'); const s = w.querySelector('[data-act=mx-skip]');
  return { fold: f ? [f.textContent.trim(), f.getAttribute('aria-expanded')] : null, skip: s ? [s.textContent.trim(), s.dataset.on] : null,
    table: !!w.querySelector('table.dci-matrix'), cols: w.querySelectorAll('thead th[data-col], thead .dci-mx-colhead').length,
    folded: (w.querySelector('[data-el=works-folded]') || {}).textContent || '', badge: (w.querySelector('.dci-works-skipped') || {}).textContent || '',
    off: w.classList.contains('dci-works-off'), ask: (w.querySelector('[data-el=works-ask]') || {}).textContent || '',
    later: (w.querySelector('[data-el=works-lookups-off]') || {}).textContent || '' }; })()"""
    LEVEL = """(n) => { const g = [...document.querySelectorAll('section.dci-group, .dci-companies section, .dci-companies .dci-group')]
  .find(s => (s.querySelector('.dci-gname strong') || {}).textContent?.trim() === n);
  const lv = g && g.querySelector('tr.dci-row [data-act=level][aria-pressed=true]'); return lv ? lv.dataset.level : null; }"""
    PLAN = """(() => { const b = document.querySelector('[data-act=preview]'); if (b.getAttribute('aria-expanded') !== 'true') b.click();
  return document.querySelector('[data-el=preview]').textContent.replace(/\\s+/g, ' '); })()"""
    results = []


    def click(pg, sel):
        pg.locator(sel).first.evaluate('b => b.click()')


    def head(pg):
        return pg.evaluate(HEAD)


    def level(pg, n):
        return pg.evaluate(f"({LEVEL})('{n}')")


    def logs(pg, rx):
        return [x for x in pg.evaluate(LOGS) if __import__('re').search(rx, x)]


    def start(ctx, wait='Checks complete'):
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        H.wait_for(pg, f"{LOGS}.some(x => /{wait}/.test(x))", 60)
        pg.wait_for_timeout(1200)
        return pg, errs


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = start(ctx)
        # A) fold / unfold
        a0 = head(pg)
        click(pg, '[data-el=works] [data-act=mx-fold]')
        a1 = head(pg)
        click(pg, '[data-el=works] [data-act=mx-fold]')
        a2 = head(pg)
        print('A) offen:', a0)
        print('   zu:', a1)
        print('   wieder auf:', a2['fold'], a2['table'])
        results.append(a0['fold'] == ['▾ Works matrix', 'true'] and a0['table'] and a0['skip'] == ['Skip works', '1']
                       and a1['fold'] == ['▸ Works matrix', 'false'] and not a1['table'] and '4 tracks' in a1['folded'] and 'column' in a1['folded']
                       and a2['fold'][1] == 'true' and a2['table'])
        # B) skip: mark new works first (links planned), then skip
        click(pg, '[data-el=works] [data-act=works-pending-all]')
        pg.wait_for_timeout(500)
        plan0 = pg.evaluate(PLAN)
        lv0 = [level(pg, 'Writer W'), level(pg, 'Pub Co')]
        q0 = len(H.WORK_QUERIES)
        click(pg, '[data-el=works] [data-act=mx-skip]')
        pg.wait_for_timeout(600)
        b1 = head(pg)
        plan1 = pg.evaluate(PLAN)
        lv1 = [level(pg, 'Writer W'), level(pg, 'Pub Co')]
        stored = pg.evaluate(f"localStorage.getItem('dci-works-skip:{H.REL}')")
        print('B) vorher:', lv0, '| Plan: Werk-Links', plan0.count('Link work'), '| Writer W', plan0.count('Writer W'), '| Pub Co', plan0.count('Pub Co'))
        print('   übersprungen:', b1, lv1, '| gespeichert:', stored)
        print('   Plan danach: Werk-Links', plan1.count('Link work'), '| Writer W', plan1.count('Writer W'), '| Pub Co', plan1.count('Pub Co'))
        print('   Protokoll:', logs(pg, 'Works matrix'))
        # [3.31.5] a publisher's row shows in its entry too, with its level (item 112)
        ok_b = (lv0 == [None, 'work'] and 'Link work' in plan0 and 'Writer W' in plan0 and b1['badge'] == 'skipped' and b1['skip'] == ['Take works again', '0']
                and not b1['table'] and b1['off'] and lv1 == ['skip', 'skip'] and stored == 'true'
                and 'Link work' not in plan1 and 'Writer W' not in plan1 and 'Pub Co' not in plan1)
        # no works level for a row while the matrix is skipped
        wbtn = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Writer Z');
      const b = g && g.querySelector('tr.dci-row [data-act=level][data-level=work]'); return b ? [b.disabled, b.title] : null; })()""")
        print('   Writer Z, Werk-Ebene:', wbtn)
        ok_b = ok_b and wbtn is not None and wbtn[0] and 'works matrix is skipped' in wbtn[1]
        pg.close()
        # stored: reload – still skipped, no work looked up
        H.BROWSES.clear()
        q1 = len(H.WORK_QUERIES)
        pg, errs2 = start(ctx, 'Import complete')
        pg.wait_for_timeout(2500)
        b2 = head(pg)
        lv2 = [level(pg, 'Writer W'), level(pg, 'Pub Co')]
        print('   neu geladen:', b2['badge'], b2['table'], lv2, '| Werk-Abfragen:', len(H.WORK_QUERIES) - q1, len(H.BROWSES))
        results.append(ok_b and b2['badge'] == 'skipped' and not b2['table'] and lv2 == ['skip', 'skip'] and len(H.WORK_QUERIES) == q1 and not H.BROWSES)
        # C) take it again – [3.36.4] the new works planned before the matrix was skipped come back with it (remembered with the
        #    release, as within the tab), so no track is looked up; their plans taken back, the next load looks the tracks up (D)
        click(pg, '[data-el=works] [data-act=mx-skip]')
        H.wait_for(pg, f"{LOGS}.some(x => /Works matrix taken again/.test(x))", 60)
        pg.wait_for_timeout(800)
        c1 = head(pg)
        lv3 = [level(pg, 'Writer W'), level(pg, 'Pub Co')]
        stored = pg.evaluate(f"localStorage.getItem('dci-works-skip:{H.REL}')")
        plan2 = pg.evaluate(PLAN)
        print('C) wieder genommen:', c1['fold'], c1['table'], c1['badge'], lv3, '| gespeichert:', stored, '| Abfragen:', len(H.WORK_QUERIES) - q1,
              '| Werk-Links wieder:', plan2.count('Link work'))
        print('   Protokoll:', logs(pg, 'Works matrix'))
        results.append(c1['fold'][1] == 'true' and c1['table'] and not c1['badge'] and lv3 == [None, 'work'] and stored is None
                       and plan2.count('Link work') == plan0.count('Link work') and len(H.WORK_QUERIES) == q1)
        while pg.locator('tr[data-mrow^="p:"] [data-act=work-unplan]').count():
            click(pg, 'tr[data-mrow^="p:"] [data-act=work-unplan]')
            pg.wait_for_timeout(200)
        pg.wait_for_timeout(1600)
        pg.close()
        # D) the question for many tracks
        pg = ctx.new_page()
        pg.goto(f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
        pg.evaluate("localStorage.setItem('dci-aw-ask', '3')")
        pg.close()
        H.BROWSES.clear()
        q2 = len(H.WORK_QUERIES)
        pg, errs3 = start(ctx, 'Import complete')
        pg.wait_for_timeout(2500)
        d1 = head(pg)
        n1 = [len(H.WORK_QUERIES) - q2, len(H.BROWSES)]
        tip = pg.evaluate("document.querySelector('[data-el=works-ask] strong').title")
        print('D) Frage:', d1['ask'], '| Abfragen bis dahin:', n1, '| Matrix:', d1['table'], '| Tooltip:', tip)
        click(pg, '[data-el=works] [data-act=mx-lookups][data-on=\"0\"]')
        pg.wait_for_timeout(600)
        d2 = head(pg)
        n2 = [len(H.WORK_QUERIES) - q2, len(H.BROWSES)]
        print('   „Jetzt nicht“:', d2['later'], '| Matrix:', d2['table'], '| Abfragen:', n2)
        click(pg, '[data-el=works] [data-el=works-lookups-off] [data-act=mx-lookups]')
        H.wait_for(pg, f"{LOGS}.some(x => /Checks complete/.test(x))", 60)
        d3 = head(pg)
        print('   später abgefragt:', len(H.WORK_QUERIES) - q2, '| Hinweis weg:', not d3['later'], '| Protokoll:', logs(pg, 'Work lookups|without a work'))
        results.append('Look up works for 3 tracks without a work?' in d1['ask'] and 'about 1 min' in d1['ask'] and n1 == [0, 0] and d1['table']
                       and 'Work lookups left out' in d2['later'] and d2['table'] and not d2['ask'] and n2 == [0, 0]
                       and len(H.WORK_QUERIES) > q2 and not d3['later'] and not d3['ask'])
        # the setting in the menu
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
        pg.wait_for_timeout(300)
        pg.locator('[data-act=settings-topic][data-topic=works]').evaluate('b => b.click()')
        pg.wait_for_timeout(300)
        f = pg.evaluate("(() => { const i = document.querySelector('[data-set=awAsk]'); return i ? [i.value, i.min, i.getAttribute('aria-label'), i.closest('label').textContent.replace(/\\s+/g, ' ').trim(), i.closest('label').title] : null; })()")
        pg.evaluate("localStorage.removeItem('dci-aw-ask')")
        print('   Einstellung:', f)
        results.append(f is not None and f[0] == '3' and f[1] == '0' and 'tracks without a work (0: never)' in f[3]
                       and tip.startswith('Counted are the tracks without a work') and f[4] == tip)
        # G) [3.19.3] the rows skipped with the works matrix: shown with their entries (setting, on) or not
        click(pg, '[data-el=works] [data-act=mx-skip]')
        pg.wait_for_timeout(500)
        GROUP = """(n) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === n);
      return g ? [g.querySelectorAll('tr.dci-row').length, [...g.querySelectorAll('.dci-work-note')].map(p => p.textContent.trim())] : null; }"""
        g1 = pg.evaluate(f"({GROUP})('Writer W')")
        pg.locator('[data-set=mx-skiprows]').evaluate('i => i.click()')
        pg.wait_for_timeout(400)
        g2 = [pg.evaluate(f"({GROUP})('Writer W')"), pg.evaluate("localStorage.getItem('dci-mx-skiprows')")]
        pg.locator('[data-set=mx-skiprows]').evaluate('i => i.click()')
        pg.wait_for_timeout(400)
        g3 = [pg.evaluate(f"({GROUP})('Writer W')"), pg.evaluate("localStorage.getItem('dci-mx-skiprows')")]
        click(pg, '[data-el=works] [data-act=mx-skip]')
        pg.wait_for_timeout(500)
        print('G) übersprungen, gezeigt:', g1, '| Einstellung aus:', g2, '| wieder an:', g3)
        results.append(g1 is not None and g1[0] >= 1 and g2[0][0] == 0 and g2[0][1] == ['1 row skipped with the works matrix is not shown (setting)'] and g2[1] == 'false'
                       and g3[0][0] == g1[0] and g3[1] is None)
        print('Fehler:', errs, errs2, errs3)
        results.append(not errs and not errs2 and not errs3)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_livecom():
    """Credits Importer 3.32.9: disambiguation comments of live recordings – the proposals (collected item 113; maintainer: "kannst
    du das feature bei live recordings als abfrage das disambiguation comment zu ergänzen in die optionen mit einbinden?
    standardmäßig aus. die infos kommen aus dem im dashboard eingegebenen alias des recording places und des datums.", "ja bitte
    mit Kommentar. unter staging. nur "live"").
    A) ⚙ Settings → Staging: "Live recordings: add a disambiguation comment" is off – no list above "Stage …" ([3.37.3] the offer
       instead, case liveoffer); switched on (stored).
    B) The release group is Live: tracks 2–4 (planned links with "live" preselected, S021) are listed – track 1 (a link in
       MusicBrainz without "live") is not; "live: Abbey Road Studios, New York, NY, USA" (the place of "recorded at", its area
       from MusicBrainz: city, US state code, "USA"); track 3 has "live" in MusicBrainz (ticked), track 4 another comment (not
       tickable, red note).
       [3.38.3] Tracks 2 and 3 are one line "2–3 · ▸ 2 tracks" (the same comment, item 168), ▸ shows them; the heading "▾ Live
       disambiguation comments: 2 of 3" (item 170).
    C) The place credited as "Iridium" and the matrix applied (the date 2001-03 on the place): "live, 2001‐03: Iridium, New
       York, NY, USA"; a comment changed by hand stays and says so; unticked stays unticked."""
    PLACE = H.COMPANIES[1002][1]
    NYC, NYS, US = H.uid('abababab', 1), H.uid('abababab', 2), H.uid('abababab', 3)
    H.PLACE_AREAS[PLACE] = NYC
    H.AREA_INFO.update({NYC: {'name': 'New York', 'type': 'City', 'parent': NYS}, NYS: {'name': 'New York', 'type': 'Subdivision', 'iso2': ['US-NY'], 'parent': US},
                        US: {'name': 'United States', 'type': 'Country', 'iso1': ['US']}})
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        for m in d['media']:
            for t in m['tracks']:
                if t['position'] == 3:
                    t['recording']['disambiguation'] = 'live'
                if t['position'] == 4:
                    t['recording']['disambiguation'] = 'demo version'
        return d

    H.ws_release = ws
    LIST = """(() => { const el = document.querySelector('[data-el=livecom]'); if (!el || el.hidden) return null;
      return [...el.querySelectorAll('tr[data-livecom]')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(), tr.querySelector('[data-f=livecom-text]').value,
        tr.querySelector('[data-f=livecom-on]').checked, tr.querySelector('[data-f=livecom-on]').disabled, tr.lastElementChild.textContent.replace(/\\s+/g, ' ').trim()]); })()"""
    EXPAND = """(() => { for (let k = 0; k < 20; k++) { const b = document.querySelector('[data-el=livecom] [data-act=livecom-group][aria-expanded=false]');
      if (!b) return k; b.click(); } return -1; })()"""
    GROUPS = """[...document.querySelectorAll('[data-el=livecom] tr[data-livecom-group]')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(),
      tr.querySelector('[data-act=livecom-group]').textContent.trim(), tr.querySelector('[data-f=livecom-text]').value, tr.querySelector('[data-f=livecom-on]').checked])"""
    ALONE = "[...document.querySelectorAll('[data-el=livecom] tr[data-livecom]:not(.dci-livecom-sub) .dci-livecom-pos')].map(x => x.textContent.trim())"
    HEAD = "(document.querySelector('[data-el=livecom] .dci-livecom-head') || {textContent: ''}).textContent.trim()"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1000)
        a0 = pg.evaluate(LIST)
        offer0 = pg.evaluate("!!document.querySelector('[data-el=livecom] .dci-livecom-offer')")
        H.open_settings(pg, 'staging')
        sw = pg.locator('[data-el=settings] [data-set=live-comments]')
        off0 = sw.is_checked()
        sw.check()
        pg.wait_for_timeout(2500)
        stored = pg.evaluate("localStorage.getItem('dci-live-comments')")
        b0 = pg.evaluate(GROUPS), pg.evaluate(ALONE), pg.evaluate(HEAD)
        pg.evaluate(EXPAND); pg.wait_for_timeout(200)
        b1 = pg.evaluate(LIST)
        print('A) vorher:', a0, '| Angebot:', offer0, '| Schalter an?', off0, '| gespeichert:', stored)
        print('B) Gruppen:', b0, '\n  ', b1)
        ok_a = a0 == [] and offer0 and off0 is False and stored == 'true'
        base = 'live: Abbey Road Studios, New York, NY, USA'
        ok_b = b1 is not None and [x[0] for x in b1] == ['2', '3', '4'] and all(x[1] == base for x in b1) \
            and [x[2] for x in b1] == [True, True, False] and [x[3] for x in b1] == [False, False, True] and 'demo version' in b1[2][4] \
            and not pg.evaluate("!!document.querySelector('[data-el=livecom] .dci-livecom-offer')") \
            and b0[0] == [['2–3', '▸ 2 tracks', base, True]] and b0[1] == ['4'] and b0[2] == '▾ Live disambiguation comments: 2 of 3'
        # C)
        rid = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => /Abbey Road Studios/.test(s.querySelector('.dci-gname').textContent));
          return g ? g.querySelector('tr.dci-row').dataset.row : null; })()""")
        pg.fill(f'tr[data-row="{rid}"] [data-f=credit]', 'Iridium')
        pg.locator(f'tr[data-row="{rid}"] [data-f=credit]').dispatch_event('change')
        pg.wait_for_timeout(300)
        if pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') != 'true':
            pg.click('.dci-pools-toggle'); pg.wait_for_timeout(200)
        pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(600)
        c1 = pg.evaluate(LIST)
        pg.fill('tr[data-livecom] [data-f=livecom-text] >> nth=0', 'live, 2001: Iridium (by hand)')
        pg.locator('tr[data-livecom] [data-f=livecom-text] >> nth=0').dispatch_event('change')
        pg.locator('tr[data-livecom] [data-f=livecom-on] >> nth=1').uncheck()
        pg.wait_for_timeout(300)
        c2 = pg.evaluate(LIST)
        print('C)', c1, '\n  ', c2)
        want = 'live, 2001‐03: Iridium, New York, NY, USA'
        ok_c = c1 and [x[1] for x in c1[:2]] == [want, want] and c2[0][1] == 'live, 2001: Iridium (by hand)' and 'changed by you' in c2[0][4] \
            and c2[1][2] is False and c2[0][2] is True
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_livecomrun():
    """Credits Importer 3.32.10: disambiguation comments of live recordings – entered after "Enter edit" (collected item 113;
    maintainer: "es soll mit einem klick auf enter edit aus dem relationship editor erst ausgeführt werden", "falls nachträglich im
    relationship editor das alias verändert wird bitte rote nachricht im log ausgeben", "ja bitte mit Kommentar").
    A) Staged with the setting on: the job of the release holds the ticked comments (tracks 2 and 3) and the edit note – the
       script's block and "MB: QoL: Seed the batch recording comments script v2022.6.13: Seed live comments"; nothing is sent.
    B) "Enter edit" (the form of the edit note submitted): MusicBrainz has the relationships – the place credited "The Iridium"
       now (changed in the relationship editor) –: one POST to /ws/js/edit/create with two edits of type 72, "live, 2001‐03: The
       Iridium, New York, NY, USA" (MusicBrainz's credit), the edit note of the job; the log says in red what changed; a box on
       the page lists it; the job is done (a second "Enter edit" sends nothing).
    C) The release page MusicBrainz shows next: a job armed there (track 2 only, its comment changed by hand) is entered on that
       page – the hand-made comment with the new credit; "live" in MusicBrainz counts as no comment, another one is not
       overwritten (red)."""
    PLACE = H.COMPANIES[1002][1]
    NYC, NYS, US = H.uid('abababab', 1), H.uid('abababab', 2), H.uid('abababab', 3)
    H.PLACE_AREAS[PLACE] = NYC
    H.AREA_INFO.update({NYC: {'name': 'New York', 'type': 'City', 'parent': NYS}, NYS: {'name': 'New York', 'type': 'Subdivision', 'iso2': ['US-NY'], 'parent': US},
                        US: {'name': 'United States', 'type': 'Country', 'iso1': ['US']}})
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        for m in d['media']:
            for t in m['tracks']:
                if t['position'] == 3:
                    t['recording']['disambiguation'] = 'live'
                if t['position'] == 4:
                    t['recording']['disambiguation'] = 'demo version'
        return d

    H.ws_release = ws
    area = {'name': 'New York', 'typeID': 3, 'containment': [{'name': 'New York', 'typeID': 2, 'primary_code': 'US-NY'},
                                                             {'name': 'United States', 'typeID': 1, 'primary_code': 'US', 'country_code': 'US'}]}

    def js_release(credit, comments):
        tracks = []
        for i, g in enumerate(H.REC):
            rels = [{'linkTypeID': 278, 'attributes': [{'typeID': 578}], 'target': {'gid': H.uid('cdcdcdcd', i + 1), 'name': H.TITLES[i]}}] if i else []
            if i:
                rels.append({'linkTypeID': 693, 'entity0_credit': credit, 'begin_date': {'year': 2001, 'month': 3, 'day': None}, 'end_date': {'year': 2001, 'month': 3, 'day': None},
                             'target': {'gid': PLACE, 'name': 'Abbey Road Studios', 'area': area}})
            tracks.append({'number': str(i + 1), 'recording': {'gid': g, 'comment': comments.get(i + 1, ''), 'relationships': rels}})
        return {'gid': H.REL, 'mediums': [{'position': 1, 'tracks': tracks}], 'releaseGroup': {'secondaryTypeIDs': [6]}}

    JOB = f"JSON.parse(localStorage.getItem('dci-live-job:{H.REL}') || 'null')"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("try { localStorage.setItem('dci-live-comments', 'true'); } catch (e) {}")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        rid = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => /Abbey Road Studios/.test(s.querySelector('.dci-gname').textContent));
          return g ? g.querySelector('tr.dci-row').dataset.row : null; })()""")
        pg.fill(f'tr[data-row="{rid}"] [data-f=credit]', 'Iridium')
        pg.locator(f'tr[data-row="{rid}"] [data-f=credit]').dispatch_event('change')
        if pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') != 'true':
            pg.click('.dci-pools-toggle'); pg.wait_for_timeout(200)
        pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(600)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(1500)
        job = pg.evaluate(JOB)
        print('A) Auftrag:', job and [(x['pos'], x['comment'], x['place']) for x in job['items']], '| Notiz endet:', job and repr(job['note'][-90:]), '| gesendet:', len(H.EDITS_POSTED))
        want = 'live, 2001‐03: Iridium, New York, NY, USA'
        ok_a = bool(job) and [(x['pos'], x['comment']) for x in job['items']] == [('2', want), ('3', want)] and job['items'][0]['place']['credit'] == 'Iridium' \
            and job['note'].endswith('\n\nMB: QoL: Seed the batch recording comments script v2022.6.13: Seed live comments') and 'MB x Vibecode' in job['note'] and not H.EDITS_POSTED
        # B) "Enter edit": the relationships saved, the place credited otherwise in the editor
        H.WS_JS_RELEASE.update(js_release('The Iridium', {3: 'live', 4: 'demo version'}))
        pg.evaluate("""(() => { const ta = document.getElementById('edit-note-text'); const f = document.createElement('form'); f.addEventListener('submit', (e) => e.preventDefault());
          ta.parentNode.insertBefore(f, ta); f.appendChild(ta); const btn = document.createElement('button'); btn.type = 'submit'; btn.className = 'submit positive';
          btn.textContent = 'Enter edit'; btn.id = 'test-enter-edit'; f.appendChild(btn); })()""")
        # (the button is below the dashboard: clicked as the page would be)
        pg.evaluate("document.getElementById('test-enter-edit').click()")
        pg.wait_for_timeout(2500)
        posted = list(H.EDITS_POSTED)
        logs = pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => [li.className, li.textContent.replace(/\\s+/g, ' ').trim()]).filter(x => /live recording|credit of|comment/i.test(x[1]))")
        notice = pg.evaluate("(() => { const n = document.getElementById('dci-livecom-notice'); return n ? n.textContent.replace(/\\s+/g, ' ').trim() : null; })()")
        job2 = pg.evaluate(JOB)
        pg.evaluate("document.getElementById('test-enter-edit').click()")
        pg.wait_for_timeout(1500)
        print('B) gesendet:', posted, '\n   Protokoll:', logs, '\n   Kasten:', notice, '| erledigt:', bool(job2 and job2.get('done')), '| danach:', len(H.EDITS_POSTED))
        new = 'live, 2001‐03: The Iridium, New York, NY, USA'
        ok_b = len(posted) == 1 and [(e['edit_type'], e['to_edit'], e['comment']) for e in posted[0]['edits']] == [(72, H.REC[1], new), (72, H.REC[2], new)] \
            and posted[0]['editNote'] == job['note'] and posted[0]['makeVotable'] is False \
            and any(c == 'dci-log-error' and '“Iridium” → “The Iridium”' in t for c, t in logs) and any('Comments of 2 live recordings entered' in t for c, t in logs) \
            and notice and 'The Iridium' in notice and bool(job2 and job2.get('done')) and len(H.EDITS_POSTED) == 1
        pg.close()
        # C) the release page
        H.WS_JS_RELEASE.clear()
        H.WS_JS_RELEASE.update(js_release('The Iridium', {4: 'demo version'}))
        armed = {'release': H.REL, 'at': 1, 'armedAt': 0, 'note': 'note C\n\nMB: QoL: Seed the batch recording comments script v2022.6.13: Seed live comments',
                 'items': [{'rec': H.REC[1], 'pos': '2', 'comment': 'live 2001: Iridium (by hand)', 'manual': True, 'place': {'mbid': PLACE, 'credit': 'Iridium', 'name': 'Abbey Road Studios'}},
                           {'rec': H.REC[3], 'pos': '4', 'comment': want, 'manual': False, 'place': {'mbid': PLACE, 'credit': 'Iridium', 'name': 'Abbey Road Studios'}}]}
        rp, errs2 = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{H.REL}')
        rp.evaluate("(job) => { job.armedAt = Date.now(); localStorage.setItem('dci-live-job:%s', JSON.stringify(job)); }" % H.REL, armed)
        rp.reload()
        rp.wait_for_timeout(2500)
        posted3 = H.EDITS_POSTED[1:]
        notice3 = rp.evaluate("(() => { const n = document.getElementById('dci-livecom-notice'); return n ? [...n.querySelectorAll('.dci-livecom-line')].map(d => [d.className, d.textContent]) : null; })()")
        logged = rp.evaluate("JSON.parse(sessionStorage.getItem('dci-log:%s') || '[]').map(e => [e.level, e.key])" % H.REL)
        print('C) gesendet:', posted3, '\n   Kasten:', notice3, '\n   Protokoll:', logged)
        ok_c = len(posted3) == 1 and [(e['to_edit'], e['comment']) for e in posted3[0]['edits']] == [(H.REC[1], 'live 2001: The Iridium (by hand)')] \
            and posted3[0]['editNote'] == armed['note'] and notice3 and any('dci-livecom-error' in c and 'demo version' in t for c, t in notice3) \
            and ['error', 'liveOther'] in logged and ['ok', 'liveSet'] in logged
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs, errs2)
        results.append(not errs and not errs2)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_liveoffer():
    """Credits Importer 3.37.3: the comments of live recordings offered while the setting is off (collected item 150b; maintainer:
    "so als abfrage/angebot für den jeweiligen fall. per mouseover tooltip wo das standardmäßig eingestellt werden kann").
    A) The setting off, the release group Live: above "Stage …" the offer "Tracks 2–4 are live recordings. Propose
       disambiguation comments for them (“live: Abbey Road Studios, New York, NY, USA”)?" – no list; its tooltip names
       ⚙ Settings → Staging → “Live recordings: add a disambiguation comment”.
    B) ✓: the list as with the setting on (tracks 2–4, 2 and 3 ticked – [3.38.3] one line, ▸ shows them), the setting stays off
       (not stored); the log says so;
       staged: the job of the release holds tracks 2 and 3.
    C) The page loaded again: the offer is back (for the case, not stored); ✕: no offer, no list, the log says so; the job is
       gone."""
    PLACE = H.COMPANIES[1002][1]
    NYC, NYS, US = H.uid('abababab', 1), H.uid('abababab', 2), H.uid('abababab', 3)
    H.PLACE_AREAS[PLACE] = NYC
    H.AREA_INFO.update({NYC: {'name': 'New York', 'type': 'City', 'parent': NYS}, NYS: {'name': 'New York', 'type': 'Subdivision', 'iso2': ['US-NY'], 'parent': US},
                        US: {'name': 'United States', 'type': 'Country', 'iso1': ['US']}})
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        for m in d['media']:
            for t in m['tracks']:
                if t['position'] == 3:
                    t['recording']['disambiguation'] = 'live'
                if t['position'] == 4:
                    t['recording']['disambiguation'] = 'demo version'
        return d

    H.ws_release = ws
    LIST = """(() => { const el = document.querySelector('[data-el=livecom]'); if (!el || el.hidden) return null;
      return [...el.querySelectorAll('tr[data-livecom]')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(), tr.querySelector('[data-f=livecom-text]').value,
        tr.querySelector('[data-f=livecom-on]').checked]); })()"""
    EXPAND = """(() => { for (let k = 0; k < 20; k++) { const b = document.querySelector('[data-el=livecom] [data-act=livecom-group][aria-expanded=false]');
      if (!b) return k; b.click(); } return -1; })()"""
    OFFER = """(() => { const o = document.querySelector('[data-el=livecom]:not([hidden]) .dci-livecom-offer'); return o ? [o.querySelector('span').textContent.replace(/\\s+/g, ' ').trim(), o.title,
      [...o.querySelectorAll('button')].map(b => b.textContent.trim())] : null; })()"""
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /Comments of live recordings/.test(t))"
    JOB = f"JSON.parse(localStorage.getItem('dci-live-job:{H.REL}') || 'null')"
    base = 'live: Abbey Road Studios, New York, NY, USA'

    def stage(pg):
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(1500)

    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        a_offer, a_list = pg.evaluate(OFFER), pg.evaluate(LIST)
        print('A) Angebot:', a_offer, '| Liste:', a_list)
        ok_a = bool(a_offer) and a_offer[0] == f'Tracks 2–4 are live recordings. Propose disambiguation comments for them (“{base}”)?' \
            and '⚙ Settings → Staging → “Live recordings: add a disambiguation comment”' in a_offer[1] and a_offer[2] == ['✓ Propose comments', '✕ Not for this release'] \
            and a_list == []
        # B) ✓
        pg.click('[data-act=livecom-yes]'); pg.wait_for_timeout(500)
        pg.evaluate(EXPAND); pg.wait_for_timeout(200)
        b_list, b_offer = pg.evaluate(LIST), pg.evaluate(OFFER)
        stored = pg.evaluate("localStorage.getItem('dci-live-comments')")
        H.open_settings(pg, 'staging')
        sw_on = pg.locator('[data-el=settings] [data-set=live-comments]').is_checked()
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
        pg.wait_for_timeout(300)
        b_logs = pg.evaluate(LOGS)
        stage(pg)
        job = pg.evaluate(JOB)
        print('B) Liste:', b_list, '| Angebot:', b_offer, '| Einstellung:', stored, sw_on, '\n   Protokoll:', b_logs, '\n   Auftrag:', job and [(x['pos'], x['comment']) for x in job['items']])
        ok_b = b_list == [['2', base, True], ['3', base, True], ['4', base, False]] and b_offer is None and stored is None and sw_on is False \
            and any('proposed for this release' in t for t in b_logs) and bool(job) and [(x['pos'], x['comment']) for x in job['items']] == [('2', base), ('3', base)]
        # C) loaded again, ✕
        pg.reload(); pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        c_offer = pg.evaluate(OFFER)
        pg.click('[data-act=livecom-no]'); pg.wait_for_timeout(500)
        c_offer2, c_list, c_logs, c_job = pg.evaluate(OFFER), pg.evaluate(LIST), pg.evaluate(LOGS), pg.evaluate(JOB)
        print('C) Angebot wieder:', bool(c_offer), '| nach ✕:', c_offer2, c_list, '\n   Protokoll:', c_logs, '| Auftrag:', c_job)
        ok_c = bool(c_offer) and c_offer2 is None and c_list is None and any('not for this release' in t for t in c_logs) and c_job is None
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_livegroup():
    """Credits Importer 3.38.3: the comments of live recordings in short (collected items 168, 170; maintainer: ""Tracks 1, 2, 3, 4,
    5 are live recordings." -> kanns du die tracks gruppieren? "1-5"? kannst du medien erwähnen, falls sie komplett live sind?",
    "bei einem release mit nur einem medium nur die tracks. es kann auch mediengruppen geben bspw. CD 1-5", "da viele tracks die
    gleichen live-Disambiguation notes bekommen", "rechts unten im kasten soll immer die Überschrift stehen", "Live disambiguation
    comments: 5 of 5").
    A) Two media of two tracks, the release group Live, the setting off: the offer names the whole medium and the other track –
       "Live recordings: CD 2, track 1.2. Propose disambiguation comments for them (“live: Abbey Road Studios”)?" (the positions
       as in the list).
    B) ✓: one line for the three (the same comment) – "CD 2, 1.2", "▸ 3 tracks"; ▸ shows the three; its text changed: all three
       have it (each "changed by you"); unticked: all three unticked – "0 of 3".
    C) The heading "▾ Live disambiguation comments: …" is the last line of the box, at its right edge, below the list; the list at
       most a third of the dashboard's height; the heading clicked: only the heading, at the same place (bottom right), ▸."""
    H.MEDIA = [2, 2]
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        return d

    H.ws_release = ws
    OFFER = """(() => { const o = document.querySelector('[data-el=livecom]:not([hidden]) .dci-livecom-offer'); return o ? o.querySelector('span').textContent.replace(/\\s+/g, ' ').trim() : null; })()"""
    GROUPS = """[...document.querySelectorAll('[data-el=livecom] tr[data-livecom-group]')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(),
      tr.querySelector('[data-act=livecom-group]').textContent.trim(), tr.querySelector('[data-f=livecom-text]').value, tr.querySelector('[data-f=livecom-on]').checked])"""
    SUBS = """[...document.querySelectorAll('[data-el=livecom] tr.dci-livecom-sub')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(),
      tr.querySelector('[data-f=livecom-text]').value, tr.querySelector('[data-f=livecom-on]').checked, tr.lastElementChild.textContent.replace(/\\s+/g, ' ').trim()])"""
    BOX = """(() => { const box = document.querySelector('[data-el=livecom] .dci-livecom-box'); if (!box) return null; const h = box.querySelector('.dci-livecom-head');
      const body = box.querySelector('.dci-livecom-body'); const r = (e) => { const x = e.getBoundingClientRect(); return [Math.round(x.left), Math.round(x.top), Math.round(x.right), Math.round(x.bottom)]; };
      return { last: box.lastElementChild.contains(h), head: h.textContent.trim(), h: r(h), box: r(box), body: body ? r(body) : null,
        max: body ? parseFloat(body.style.maxHeight) : null, dash: Math.round(document.getElementById('dci-overlay').getBoundingClientRect().height) }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        a = pg.evaluate(OFFER)
        print('A) Angebot:', a)
        ok_a = a == 'Live recordings: CD 2, track 1.2. Propose disambiguation comments for them (“live: Abbey Road Studios”)?'
        # B)
        pg.click('[data-act=livecom-yes]'); pg.wait_for_timeout(500)
        g0 = pg.evaluate(GROUPS)
        pg.click('[data-el=livecom] [data-act=livecom-group]'); pg.wait_for_timeout(200)
        s0 = pg.evaluate(SUBS)
        pg.fill('tr[data-livecom-group] [data-f=livecom-text]', 'live (all three)')
        pg.press('tr[data-livecom-group] [data-f=livecom-text]', 'Tab')
        pg.wait_for_timeout(300)
        s1 = pg.evaluate(SUBS)
        pg.locator('tr[data-livecom-group] [data-f=livecom-on]').uncheck()
        pg.wait_for_timeout(300)
        s2, g2 = pg.evaluate(SUBS), pg.evaluate(GROUPS)
        print('B) Gruppe:', g0, '\n   ▸:', s0, '\n   Text:', s1, '\n   aus:', g2, s2)
        ok_b = len(g0) == 1 and g0[0][0] == 'CD 2, 1.2' and g0[0][1] == '▸ 3 tracks' and g0[0][3] is True and [x[0] for x in s0] == ['1.2', '2.1', '2.2'] \
            and all(x[1] == g0[0][2] for x in s0) and all(x[1] == 'live (all three)' and 'changed by you' in x[3] for x in s1) \
            and len(g2) == 1 and g2[0][3] is False and all(x[2] is False for x in s2)
        # C) the heading
        c1 = pg.evaluate(BOX)
        pg.click('[data-el=livecom] .dci-livecom-head'); pg.wait_for_timeout(300)
        c2 = pg.evaluate(BOX)
        print('C) offen:', c1, '\n   zu:', c2)
        ok_c = bool(c1 and c2) and c1['last'] and c1['head'].startswith('▾ Live disambiguation comments: 0 of 3') and abs(c1['h'][2] - c1['box'][2]) <= 12 \
            and c1['body'] and c1['h'][1] >= c1['body'][3] - 1 and c1['max'] <= max(120, c1['dash'] / 3) + 2 \
            and c2['body'] is None and c2['head'].startswith('▸ Live disambiguation comments') and abs(c2['h'][2] - c1['h'][2]) <= 2 and abs(c2['h'][3] - c1['h'][3]) <= 2
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
