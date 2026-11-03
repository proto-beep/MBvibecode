"""Works: the works of the artists, skipping the works matrix (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: artistworks, worksskip, livecom (3.32.9), livecomrun (3.32.10), liveoffer (3.37.3) – each the former smoke/t_<case>.py, unchanged –, livegroup (3.38.3), liveall (3.40.13), workpick (3.38.15), coverworks (3.38.16), suitedata (3.41.0), suiteask (3.41.1); `python3 t_works_more.py <case> …` runs only those."""
import re
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
    """Credits Importer 3.32.9: disambiguation comments of live recordings – the proposals (collected item 113).
    A) ⚙ Settings → Staging: "Live recordings: add a disambiguation comment" is off – no list above "Stage …" ([3.37.3] the offer
       instead, case liveoffer); switched on (stored).
    B) The release group is Live: tracks 2–4 (planned links with "live" preselected, S021) are listed – track 1 (a link in
       MusicBrainz without "live") is not; "live: Abbey Road Studios, New York, NY, USA" (the place of "recorded at", its area
       from MusicBrainz: city, US state code, "USA"); track 3 has "live" in MusicBrainz (ticked), track 4 another comment (not
       tickable, red note).
       [3.38.3] Tracks 2 and 3 are one line "2–3 · ▸ 2 tracks" (the same comment, item 168), ▸ shows them; the heading "▾ Live
       disambiguation comments: 2 of 3" (item 170).
    C) The place credited as "Iridium" and the matrix applied (the date 2001-03 on the place): "live, 2001‐03: Iridium, New
       York, NY, USA"; a comment changed by hand stays and says so; unticked stays unticked.
       [Z-LC] (3.40.13) The box "All" is for tracks 2 and 3 only (track 4 cannot be ticked)."""
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
            and b0[0] == [['2–3', '▸ 2 tracks', base, True]] and b0[1] == ['4'] and b0[2] == '▾ Live disambiguation comments: 2 of 3' \
            and pg.evaluate("document.querySelector('[data-el=livecom] thead [data-all]').dataset.recs.split(',').length") == 2
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
    """Credits Importer 3.32.10: disambiguation comments of live recordings – entered after "Enter edit" (collected item 113).
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
    """Credits Importer 3.37.3: the comments of live recordings offered while the setting is off (collected item 150b).
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
    """Credits Importer 3.38.3: the comments of live recordings in short (collected items 168, 170).
    A) Two media of two tracks, the release group Live, the setting off: the offer names the whole medium and the other track –
       "Live recordings: track 1.2, CD 2. Propose disambiguation comments for them (“live: Abbey Road Studios”)?" (the positions
       as in the list; [3.38.13] F-2: in their order, until 3.38.12 "CD 2, track 1.2").
    B) ✓: one line for the three (the same comment) – "1.2, CD 2", "▸ 3 tracks"; ▸ shows the three; its text changed: all three
       have it (each "changed by you"); unticked: all three unticked – "0 of 3".
    C) The heading "▾ Live disambiguation comments: …" is the last line of the box, at its right edge, below the list; the list at
       most a third of the dashboard's height; the heading clicked: only the heading, at the same place (bottom right), ▸;
       [3.38.13] (F-1) the heading purple with white text, open and closed (darker under the pointer)."""
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
      return { last: box.lastElementChild.contains(h), head: h.textContent.trim(), h: r(h), box: r(box), body: body ? r(body) : null, bg: getComputedStyle(h).backgroundColor, color: getComputedStyle(h).color,
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
        # [3.38.13] (F-2) in the order of the positions (until 3.38.12 "CD 2, track 1.2")
        ok_a = a == 'Live recordings: track 1.2, CD 2. Propose disambiguation comments for them (“live: Abbey Road Studios”)?'
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
        ok_b = len(g0) == 1 and g0[0][0] == '1.2, CD 2' and g0[0][1] == '▸ 3 tracks' and g0[0][3] is True and [x[0] for x in s0] == ['1.2', '2.1', '2.2'] \
            and all(x[1] == g0[0][2] for x in s0) and all(x[1] == 'live (all three)' and 'changed by you' in x[3] for x in s1) \
            and len(g2) == 1 and g2[0][3] is False and all(x[2] is False for x in s2)
        # C) the heading
        c1 = pg.evaluate(BOX)
        pg.click('[data-el=livecom] .dci-livecom-head'); pg.wait_for_timeout(300)
        c2 = pg.evaluate(BOX)
        print('C) offen:', c1, '\n   zu:', c2)
        ok_c = bool(c1 and c2) and c1['last'] and c1['head'].startswith('▾ Live disambiguation comments: 0 of 3') and abs(c1['h'][2] - c1['box'][2]) <= 12 \
            and c1['body'] and c1['h'][1] >= c1['body'][3] - 1 and c1['max'] <= max(120, c1['dash'] / 3) + 2 \
            and c2['body'] is None and c2['head'].startswith('▸ Live disambiguation comments') and abs(c2['h'][2] - c1['h'][2]) <= 2 and abs(c2['h'][3] - c1['h'][3]) <= 2 \
            and c1['bg'] == 'rgb(115, 109, 171)' and c1['color'] == 'rgb(255, 255, 255)' and c2['bg'] in ('rgb(115, 109, 171)', 'rgb(75, 69, 133)')
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_liveall():
    """Credits Importer 3.40.13 (collected item Z-LC): one box for all live disambiguation comments.
    A) Two media of two tracks, the release group Live, ✓ proposed: a first line "All" above the list – ticked (all three are),
       its label "All live disambiguation comments".
    B) The group opened, track 2.1 unticked: "All" mixed (neither ticked nor not), "2 of 3".
    C) "All" clicked: all three ticked ("3 of 3"), not mixed; again: none ("0 of 3").
    D) (case livecom's release) a recording MusicBrainz has another comment for cannot be ticked: not among those of "All"."""
    H.MEDIA = [2, 2]
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        return d

    H.ws_release = ws
    ALL = """(() => { const x = document.querySelector('[data-el=livecom] thead tr.dci-livecom-all [data-f=livecom-on]'); if (!x) return null;
      return [x.checked, x.indeterminate, x.closest('tr').textContent.trim(), x.getAttribute('aria-label'), x.dataset.recs.split(',').length]; })()"""
    ONS = "[...document.querySelectorAll('[data-el=livecom] tbody [data-f=livecom-on]')].map(x => x.checked)"
    HEAD = "(document.querySelector('[data-el=livecom] .dci-livecom-head') || {textContent: ''}).textContent.trim()"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        pg.click('[data-act=livecom-yes]'); pg.wait_for_timeout(500)
        a0 = pg.evaluate(ALL)
        print('A)', a0)
        results.append(a0 == [True, False, 'All', 'All live disambiguation comments', 3])
        pg.click('[data-el=livecom] [data-act=livecom-group]'); pg.wait_for_timeout(200)
        pg.locator('tr.dci-livecom-sub [data-f=livecom-on] >> nth=1').evaluate('x => x.click()')
        pg.wait_for_timeout(300)
        b0 = [pg.evaluate(ALL), pg.evaluate(HEAD)]
        print('B)', b0)
        results.append(b0[0] is not None and b0[0][:2] == [False, True] and b0[1].startswith('▾ Live disambiguation comments: 2 of 3'))
        pg.click('[data-el=livecom] thead [data-f=livecom-on]'); pg.wait_for_timeout(300)
        c0 = [pg.evaluate(ALL), pg.evaluate(HEAD), pg.evaluate(ONS)]
        pg.click('[data-el=livecom] thead [data-f=livecom-on]'); pg.wait_for_timeout(300)
        c1 = [pg.evaluate(ALL), pg.evaluate(HEAD), pg.evaluate(ONS)]
        print('C) an:', c0, '\n   aus:', c1)
        results.append(c0[0][:2] == [True, False] and c0[1].startswith('▾ Live disambiguation comments: 3 of 3') and all(c0[2])
                       and c1[0][:2] == [False, False] and c1[1].startswith('▾ Live disambiguation comments: 0 of 3') and not any(c1[2]))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_workpick():
    """Credits Importer 3.38.15 (collected item 180, F-180): the works found for a track are a choice "n works ▾" in its line.
    A) Track 1.4 (two works of the release artist with its title): "2 works ▾" in the line of "no work yet" (same line), its list hidden;
       track 1.3 (one work): "1 work ▾" – offered, not set (still "no work yet").
    B) A click on "2 works ▾": the list below the line (both works, the second with its disambiguation), aria-expanded; the focus
       stays on the button. A click elsewhere closes it; opened again, Esc closes it (the dashboard stays) and the focus is on the
       button; one list at a time (track 1.3 opened: 1.4 closes); with a list open, "＋ New work" of track 1.2 acts at the first click
       (3.38.16).
    C) "Link" of the second work in the open list: the track's work is planned ("chosen for linking" in the log), the choice is gone."""
    TB = H.uid('dddddddd', 60)
    W3, W4, W5 = H.uid('cccccccc', 73), H.uid('cccccccc', 74), H.uid('cccccccc', 75)
    H.RELEASE_AC[:] = [(TB, 'Test Band', 'Test Band', '')]
    H.ARTIST_WORKS.update({TB: [{'id': W4, 'title': H.TITLES[3], 'type': 'Song', 'aliases': []},
                                {'id': W5, 'title': H.TITLES[3], 'type': 'Song', 'aliases': [], 'disambiguation': 'instrumental'},
                                {'id': W3, 'title': H.TITLES[2], 'type': 'Song', 'aliases': []}]})
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    STATE = """(i) => { const tr = document.querySelector(`tr[data-work="${i}"]`); if (!tr) return null;
      const b = tr.querySelector('[data-act=mx-works]'); const l = tr.querySelector('.dci-mx-wlist'); const badge = tr.querySelector('.dci-mx-line .dci-badge');
      const mid = (e) => { const r = e.getBoundingClientRect(); return Math.round(r.top + r.height / 2); };
      return { btn: b ? b.textContent.replace(/\\s+/g, ' ').trim() : null, exp: b ? b.getAttribute('aria-expanded') : null,
        shown: !!(l && l.getClientRects().length), gids: l ? [...l.querySelectorAll('[data-act=work-pick]')].map(x => x.dataset.gid) : [],
        disamb: l ? [...l.querySelectorAll('.dci-disamb')].map(x => x.textContent) : [], badge: badge ? badge.textContent.trim() : null,
        sameLine: !!(b && badge && Math.abs(mid(b) - mid(badge)) <= 4), focus: document.activeElement === b,
        below: !!(b && l && l.getClientRects().length && l.getBoundingClientRect().top >= b.getBoundingClientRect().bottom - 1) }; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
        pg.add_style_tag(content='#dci-log { display: none !important; }')
        pg.wait_for_timeout(400)
        st = lambda i: pg.evaluate(f"({STATE})({i})")
        a4, a3 = st(3), st(2)
        print('A) Track 1.4:', a4, '\n   Track 1.3:', a3)
        results.append(a4 and a4['btn'] == '2 works ▾' and a4['exp'] == 'false' and not a4['shown'] and a4['sameLine'] and a4['badge'] == 'no work yet'
                       and a3 and a3['btn'] == '1 work ▾' and a3['badge'] == 'no work yet' and not a3['shown'])
        pg.locator('tr[data-work="3"] [data-act=mx-works]').click(); pg.wait_for_timeout(300)
        b1 = st(3)
        pg.locator('tr[data-work="3"] .dci-mx-title strong').click(); pg.wait_for_timeout(300)
        b2 = st(3)
        pg.locator('tr[data-work="3"] [data-act=mx-works]').click(); pg.wait_for_timeout(300)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
        b3, still = st(3), pg.evaluate("!document.getElementById('dci-overlay').hidden")
        pg.locator('tr[data-work="3"] [data-act=mx-works]').click(); pg.wait_for_timeout(300)
        pg.locator('tr[data-work="2"] [data-act=mx-works]').click(); pg.wait_for_timeout(300)
        b4, b5 = st(3), st(2)
        # (3.38.16, review) with a list open, a click on another button acts at once: "＋ New work" of track 1.2
        pg.locator('tr[data-work="1"] [data-act=work-pending]').click(); pg.wait_for_timeout(400)
        b6, pend = st(2), pg.evaluate("!!document.querySelector('tr[data-work=\"1\"] .dci-badge-plan')")
        print('B) offen:', b1, '\n   daneben geklickt:', b2['shown'], '| Esc:', b3['shown'], b3['focus'], still, '| eine zur Zeit:', b4['shown'], b5['shown'],
              '| anderer Knopf:', b6['shown'], pend)
        results.append(b1['shown'] and b1['exp'] == 'true' and b1['below'] and b1['gids'] == [W4, W5] and b1['disamb'] == ['(instrumental)'] and b1['focus']
                       and b1['btn'] == '2 works ▴' and not b2['shown'] and b2['exp'] == 'false' and not b3['shown'] and b3['focus'] and still
                       and not b4['shown'] and b5['shown'] and not b6['shown'] and pend)
        pg.locator('tr[data-work="3"] [data-act=mx-works]').click(); pg.wait_for_timeout(300)
        pg.locator(f'tr[data-work="3"] .dci-mx-wlist [data-act=work-pick][data-gid="{W5}"]').click(); pg.wait_for_timeout(500)
        # (3.40.3) under load the matrix may be drawn anew by a result of the background just then: once more while the list is still open
        for _ in range(2):
            if [x for x in pg.evaluate(LOGS) if 'chosen for linking' in x] or not st(3)['shown']:
                break
            pg.locator(f'tr[data-work="3"] .dci-mx-wlist [data-act=work-pick][data-gid="{W5}"]').click(); pg.wait_for_timeout(1500)
        c = st(3)
        picked = [x for x in pg.evaluate(LOGS) if 'chosen for linking' in x]
        planned = pg.evaluate("(() => { const tr = document.querySelector('tr[data-work=\"3\"]'); return tr.querySelector('.dci-badge-plan') ? tr.querySelector('.dci-mblink').textContent : null; })()")
        print('C) gewählt:', picked, '| geplant:', planned, '| Auswahl:', c['btn'])
        results.append(picked == [f'Track 1.4: work “{H.TITLES[3]}” chosen for linking'] and planned and c['btn'] is None)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_coverworks():
    """Credits Importer 3.38.16 (collected item 179, 179b, F-179b – F-179d): works of a track's composer by a similar title.
    A) Track 1.4 "Variants On A Theme By Monk", Discogs "Written-By [Theme] – Monk" (Thelonious Monk) on it: of Monk's four works
       only "Variants on a Theme of Thelonious Monk (Criss-Cross)" is offered ("… the composer of the track (similar title)") –
       not all his works. Track 1.3 "Round Midnight (Thelonious Monk cover)" (no credit of Monk): the full name of the title looked
       up in MusicBrainz – "'Round Midnight" offered ("the title names “Thelonious Monk”"). Track 1.2 "Epistrophy By Monk": the
       surname matches an artist of the release – "Epistrophy" offered. The log names the three titles (1.4: "By Monk" too).
    B) "Link" of Monk's work for track 1.4: the link offers "co?" (dashed; Monk is none of the performers), a click sets "cover";
       the credited writer's own work of the same title ("Epistrophy By Monk" by Writer W) gets no "co?"; the works of the artists are
       compared once (the name in the title looked up within the same run). [Z-CV] (3.40.17) Monk has only writing credits on the
       release (not classical): "cover" is set by itself – "co" yellow, ticked; a click takes it off ("co?" again), another sets it.
    D) (3.39.9, collected item K-9) no "co?" when Monk performs the track: a member of the release's band ("member of band" in
       MusicBrainz), the pianist of the recording in MusicBrainz, or the track's artist. (3.40.17: where it was "co?", "cover" set by
       itself; neither when he performs.)
    E) [Z-CV] (3.40.17) Not set by itself – "co?" only: the release of the genre "Classical" at Discogs; Monk with another credit
       on the release (Liner Notes).
    C) In Node: titleComposerNames – "(Thelonious Monk cover)" → Thelonious Monk (full), "By Monk" → Monk (surname), "(Live)",
       "(Theme)", "Stand By Me", "(Part 2)" → none; (3.38.16, review) "(Prod. By Metro Boomin)", "(Main Title)", "(Dub)", "Stand By Your
       Man", "(Act II)" → none, "Theme By Monk For Piano" → Monk, "(Ludwig van Beethoven cover)" → the full name, "BY MONK" → MONK; similarWorkTitle – the composer's names and brackets left out, a work's title
       whole in the track's title from two words or six letters ("Theme" alone not)."""
    import json
    import subprocess
    MONK = H.uid('dddddddd', 3410)
    TB = H.uid('dddddddd', 60)
    W6, W7, W8, W9, W10, W11 = (H.uid('cccccccc', n) for n in (86, 87, 88, 89, 90, 91))
    WW = H.ARTISTS[3007][0]
    H.ARTISTS[3410] = (MONK, 'Thelonious Monk')
    # [Z-CV] (3.40.17) Monk's work known to /ws/js/entity (it is staged)
    H.COMPANIES[7086] = ('work', H.uid('cccccccc', 86), 'Variants on a Theme of Thelonious Monk (Criss-Cross)')
    H.TITLES[1:4] = ['Epistrophy By Monk', 'Round Midnight (Thelonious Monk cover)', 'Variants On A Theme By Monk']
    H.RELEASE_AC[:] = [(TB, 'Test Band', 'Test Band', '')]
    for i, n in [(567, 'cover'), (578, 'live')]:
        H.attr(i, n, i)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.ARTIST_WORKS.update({MONK: [{'id': W6, 'title': 'Variants on a Theme of Thelonious Monk (Criss-Cross)', 'type': 'Song', 'aliases': []},
                                  {'id': W7, 'title': 'Criss Cross', 'type': 'Song', 'aliases': []},
                                  {'id': W8, 'title': "'Round Midnight", 'type': 'Song', 'aliases': []},
                                  {'id': W9, 'title': 'Epistrophy', 'type': 'Song', 'aliases': []}],
                           TB: [{'id': W10, 'title': 'Song One', 'type': 'Song', 'aliases': []}],
                           WW: [{'id': W11, 'title': 'Epistrophy By Monk', 'type': 'Song', 'aliases': []}]})
    orig = H.discogs_release

    def rel():
        d = orig()
        d['tracklist'][3]['extraartists'] = [{'name': 'Thelonious Monk', 'anv': 'Monk', 'role': 'Written-By [Theme]', 'tracks': '', 'id': 3410, 'join': ''}]
        return d

    H.discogs_release = rel
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    SAME = """(i) => { const tr = document.querySelector(`tr[data-work="${i}"]`); const s = tr && tr.querySelector('.dci-same');
      return s ? [...s.querySelectorAll('li')].map(li => [li.querySelector('[data-act=work-pick]').dataset.gid, li.querySelector('.dci-sub').textContent.trim()]) : null; }"""
    PILL = """(i) => { const tr = document.querySelector(`tr[data-work="${i}"]`); const p = tr && tr.querySelector('.dci-wpill[data-attr=cover]');
      return p ? [p.className.replace(/.*dci-wpill-(\\w+).*/, '$1'), p.textContent.trim(), p.title] : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
        pg.add_style_tag(content='#dci-log { display: none !important; }')
        pg.wait_for_timeout(400)
        same = lambda i: pg.evaluate(f"({SAME})({i})")
        s4, s3, s2 = same(3), same(2), same(1)
        logs = [x for x in pg.evaluate(LOGS) if 'the title names' in x]
        print('A) 1.4:', s4, '\n   1.3:', s3, '\n   1.2:', s2, '\n   Protokoll:', logs)
        results.append(s4 == [[W6, 'Song – work of Thelonious Monk, the composer of the track (similar title)']]
                       and s3 == [[W8, 'Song – work of Thelonious Monk – the title names “Thelonious Monk”']]
                       and sorted(s2 or []) == sorted([[W9, 'Song – work of Thelonious Monk – the title names “Monk”'], [W11, 'Song – work of Writer W']])
                       and len([x for x in pg.evaluate(LOGS) if 'Works of the artists compared' in x]) == 1
                       and sorted(logs) == sorted(['Track 1.3: the title names “Thelonious Monk” – the works of Thelonious Monk are compared',
                                                   'Track 1.2: the title names “Monk” – the works of Thelonious Monk are compared',
                                                   'Track 1.4: the title names “Monk” – the works of Thelonious Monk are compared']))
        pg.locator('tr[data-work="3"] [data-act=mx-works]').click(); pg.wait_for_timeout(300)
        pg.locator(f'tr[data-work="3"] .dci-mx-wlist [data-act=work-pick][data-gid="{W6}"]').click(); pg.wait_for_timeout(500)
        # [3.39.9] "co?" once MusicBrainz said who is a member of whom (looked up in the background; (3.40.3) 45 s under load)
        H.wait_for(pg, f"!!({PILL})(3)", 45)
        b0 = pg.evaluate(f"({PILL})(3)")
        # [Z-CV] (3.40.17) staged with "cover" (567)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        staged = pg.evaluate(f"""(() => {{ const ids = (r) => r && r.attributes && r.attributes.__tree ? r.attributes.__tree.map(a => a.typeID || a.type.id) : [];
          return MB.relationshipEditor.state.added.filter(x => x.linkTypeID === 278 && x.entity1 && x.entity1.gid === '{W6}').map(ids); }})()""")
        pg.wait_for_timeout(300)
        pg.locator('tr[data-work="3"] .dci-wpill[data-attr=cover]').click(); pg.wait_for_timeout(300)
        b1 = pg.evaluate(f"({PILL})(3)")
        # the credited writer's own work of the same title: no "co?" (a songwriter's song is no cover)
        pg.locator('tr[data-work="1"] [data-act=mx-works]').click(); pg.wait_for_timeout(300)
        pg.locator(f'tr[data-work="1"] .dci-mx-wlist [data-act=work-pick][data-gid="{W11}"]').click(); pg.wait_for_timeout(500)
        b2 = pg.evaluate(f"({PILL})(1)")
        pg.locator('tr[data-work="3"] .dci-wpill[data-attr=cover]').click(); pg.wait_for_timeout(300)
        b1b = pg.evaluate(f"({PILL})(3)")
        print('B) co:', b0, '| gestaged:', staged, '→', b1, '→', b1b, '| eigenes Werk von Writer W:', b2)
        # [Z-CV] (3.40.17) set by itself (until 3.40.16 offered: "co?", a click set it)
        results.append(b0 and b0[0] == 'auto' and b0[1] == 'co' and staged == [[567]] and b0[2].startswith('Cover – set by itself: the composer (Thelonious Monk) is none of the performers')
                       and b1 and b1[0] == 'hint' and b1[1] == 'co?' and b1[2].startswith('Cover? The composer (Thelonious Monk) is none of the performers')
                       and b1b and b1b[0] == 'on' and (b2 is None or b2[0] not in ('hint', 'auto')))
        print('Fehler:', errs)
        results.append(not errs)

        # D) (3.39.9, K-9, Q-m, Q-w) no "co?" when Monk performs: a member of the release's band, MusicBrainz's pianist of the
        # recording, or the track's artist
        def pill_with(setup, look=None):
            setup()
            c2 = H.new_context(b)
            # (3.39.9, review) the lookups of "member of band": the composer's only
            looked = []
            c2.on('request', lambda r: looked.append(re.search(r'/ws/2/artist/([0-9a-f-]{36})', r.url).group(1)) if re.search(r'/ws/2/artist/[0-9a-f-]{36}\?inc=artist-rels', r.url) else None)
            p2, e2 = H.open_mb_edit(c2, companion=False)
            p2.on('dialog', lambda d: d.accept())
            p2.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(p2)
            H.wait_for(p2, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
            p2.add_style_tag(content='#dci-log { display: none !important; }')
            p2.wait_for_timeout(400)
            # (3.40.3) under load: the button there first (60 s)
            p2.wait_for_selector('tr[data-work="3"] [data-act=mx-works]', timeout=60000)
            pick = p2.locator(f'tr[data-work="3"] .dci-mx-wlist [data-act=work-pick][data-gid="{W6}"]')
            for _ in range(3):
                p2.locator('tr[data-work="3"] [data-act=mx-works]').click(); p2.wait_for_timeout(300)
                if pick.is_visible():
                    break
                p2.wait_for_timeout(1500)
            pick.click()
            p2.wait_for_timeout(3000)
            # (3.40.1) the lookups (the composer's, (3.40.1) its other names'): until they are asked (30 s at most, under load), then a
            # moment for their answers and the matrix (the cases without a lookup wait as long as before)
            for _ in range(120):
                if len(looked) >= len(look or [MONK]):
                    break
                p2.wait_for_timeout(250)
            p2.wait_for_timeout(3000)
            out = p2.evaluate(f"({PILL})(3)")
            c2.close()
            return out, e2 + ([] if looked == (look or [MONK]) else [f'lookups: {looked}'])
        d0, e0 = pill_with(lambda: None)  # the same page without any of them: "cover" (so the three below say something)
        d1, e1 = pill_with(lambda: H.BAND_MEMBERS.update({TB: [MONK]}))
        H.BAND_MEMBERS.clear()
        # (review) the other direction: the band of the composer, the release's artist a member of it
        d1b, e1b = pill_with(lambda: H.BAND_MEMBERS.update({MONK: [TB]}))
        H.BAND_MEMBERS.clear()
        d2, e2 = pill_with(lambda: H.MB_EXTRA.setdefault(H.REC[3], []).append({'target-type': 'artist', 'type': 'instrument', 'type-id': H.LTS[148]['gid'],
                                                                                 'attributes': ['piano'], 'attribute-values': {}, 'artist': {'id': MONK, 'name': 'Thelonious Monk'}}))
        H.MB_EXTRA.pop(H.REC[3], None)
        d3, e3 = pill_with(lambda: H.TRACK_AC.update({3: [(MONK, 'Thelonious Monk')]}))
        H.TRACK_AC.clear()
        # (review) MusicBrainz's pianist of the whole release
        d4, e4 = pill_with(lambda: H.MB_EXTRA.setdefault(H.REL, []).append({'target-type': 'artist', 'type': 'instrument', 'type-id': '67555849-61e5-455b-96e3-29733f0115f5',
                                                                               'attributes': ['piano'], 'attribute-values': {}, 'artist': {'id': MONK, 'name': 'Thelonious Monk'}}))
        H.MB_EXTRA.pop(H.REL, None)
        # [Z-AF] (3.40.1) "is person": Monk's other name is the release's artist; Monk's other name is a member of the release's band
        # (Q-ah – the bands of the other name looked up too)
        ALIAS = H.uid('dddddddd', 3411)
        d5, e5 = pill_with(lambda: H.IS_PERSON.update({MONK: [TB]}))
        H.IS_PERSON.clear()
        d6, e6 = pill_with(lambda: (H.IS_PERSON.update({MONK: [ALIAS]}), H.BAND_MEMBERS.update({TB: [ALIAS]})), look=[MONK, ALIAS])
        H.IS_PERSON.clear()
        H.BAND_MEMBERS.clear()
        # the control: the other name in no band of the release – "cover" (after both lookups)
        d7, e7 = pill_with(lambda: H.IS_PERSON.update({MONK: [ALIAS]}), look=[MONK, ALIAS])
        H.IS_PERSON.clear()
        H.BAND_MEMBERS.clear()
        # (3.40.3, review) two performance names of one person: Monk and the release's artist both "is person" of LEGAL – from LEGAL's
        # answer, no lookup more
        LEGAL = H.uid('dddddddd', 3412)
        d8, e8 = pill_with(lambda: H.IS_PERSON.update({LEGAL: [MONK, TB]}), look=[MONK, LEGAL])
        H.IS_PERSON.clear()
        print('   is person:', d5, '| anderer Name in der Band:', d6, '| anderer Name, keine Band (Gegenprobe):', d7, '| zwei Künstlernamen:', d8, '| Fehler:', e5, e6, e7, e8)
        print('D) ohne:', d0, '| Mitglied der Band:', d1, '| Band des Komponisten:', d1b, '| Pianist in MB:', d2, '| Track-Artist:', d3, '| Pianist des Release:', d4, '| Fehler:', e0, e1, e1b, e2, e3, e4)
        no_co = lambda x: x is None or x[0] not in ('hint', 'auto')
        # d2, d3: performers known without a lookup – none asked then (the lookups list says [MONK] only where one is made)
        results.append(d0 is not None and d0[0] == 'auto' and no_co(d1) and no_co(d1b) and no_co(d2) and no_co(d3) and no_co(d4)
                       and not (e0 or e1 or e1b) and all(not [x for x in e if not x.startswith('lookups')] for e in (e2, e3, e4)))
        results.append(no_co(d5) and no_co(d6) and d7 is not None and d7[0] == 'auto' and no_co(d8) and not (e5 or e6 or e7 or e8))

        # E) [Z-CV] (3.40.17) "co?" only: classical; another credit of Monk
        def with_rel(change):
            def setup():
                def r2():
                    d = rel()
                    change(d)
                    return d
                H.discogs_release = r2
            return setup
        f0, f0e = pill_with(with_rel(lambda d: d.update({'genres': ['Classical']})))
        f1, f1e = pill_with(with_rel(lambda d: d.update({'extraartists': d['extraartists'] + [{'name': 'Thelonious Monk', 'anv': '', 'role': 'Liner Notes', 'tracks': '', 'id': 3410, 'join': ''}]})))
        H.discogs_release = rel
        print('E) Classical:', f0, '| Liner Notes:', f1, '| Fehler:', f0e, f1e)
        results.append(f0 is not None and f0[0] == 'hint' and f1 is not None and f1[0] == 'hint' and not (f0e or f1e))
        b.close()
    TITLES = ['Round Midnight (Thelonious Monk cover)', 'Epistrophy By Monk', 'Song (Live)', 'Song (Theme)', 'Stand By Me', 'Song (Part 2)',
              'Money (Prod. By Metro Boomin)', 'Song (Main Title)', 'Song (Dub)', 'Theme By Monk For Piano', 'Ode (Ludwig van Beethoven cover)',
              'Stand By Your Man', 'Overture (Act II)', 'Theme BY MONK']
    SIM = [['Variants On A Theme By Monk', ['Variants on a Theme of Thelonious Monk (Criss-Cross)'], ['Thelonious Monk', 'Monk']],
           ['Round Midnight (Thelonious Monk cover)', ["'Round Midnight"], ['Thelonious Monk', 'Monk']],
           ['Variants On A Theme By Monk', ['Criss Cross'], ['Thelonious Monk', 'Monk']],
           ['A Theme For Ernie', ['Theme'], ['Fred Lacey', 'Lacey']],
           ['Blue Monk Live At Newport', ['Blue Monk'], ['Thelonious Monk', 'Monk']]]
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const t = JSON.parse(process.argv[2]).map((x) => m.titleComposerNames(x));
const s = JSON.parse(process.argv[3]).map(([a, b, c]) => m.similarWorkTitle(a, b, c));
console.log(JSON.stringify([t, s]));
"""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(TITLES), json.dumps(SIM)], capture_output=True, text=True)
    got = json.loads(js.stdout) if not js.returncode else [js.stderr[-500:], None]
    print('C) Namen:', got[0], '| ähnlich:', got[1])
    results.append(got[0] == [[{'name': 'Thelonious Monk', 'full': True}], [{'name': 'Monk', 'full': False}], [], [], [], [], [], [], [],
                              [{'name': 'Monk', 'full': False}], [{'name': 'Ludwig van Beethoven', 'full': True}], [], [], [{'name': 'MONK', 'full': False}]]
                   and got[1] == [True, True, False, False, True])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suitedata():
    """Credits Importer 3.41.0 (collected item Z-SU; Q-bt, Q-ca, Q-ch): what a suite can be made of – in Node.
    A) Discogs: the headings of the track list kept ("Side A" before track 1, "Trisect" before track 3 …), the sub-tracks of an
       index of one track as its parts ("Transition", "Phase 4", "Coda"), the index's title kept (until 3.40.17 headings were left
       out and the sub-tracks only their positions).
    B) The parts of a title: "Phase 2 / Phase 3" → two, "AC/DC" none; headings: "Side A", "CD 1", "Bonus Tracks", "Encore" – a side
       or medium (T061), "Recorded live at Moers, 1981" – a recording, "Trisect", "Sidewinder" – a name.
    C) The suites offered: below the heading "Trisect" tracks 3–5 (until "Recorded live …"), the index "Suite X" for track 6; a
       release without headings whose track has parts: all tracks with the release's title; without parts: none."""
    import json
    import subprocess
    sub = lambda pos, title: {'position': pos, 'type_': 'track', 'title': title, 'duration': '', 'extraartists': []}
    head = lambda title: {'position': '', 'type_': 'heading', 'title': title, 'duration': ''}
    d = {'id': 1, 'title': 'Live In Moers', 'tracklist': [
        head('Side A'), sub('A1', 'Introduction'), sub('A2', 'Phase 1'),
        head('Trisect'), sub('A3', 'Phase 2 / Phase 3'), sub('B1', 'Interlude'), sub('B2', 'Finale'),
        head('Recorded live at Moers, 1981'),
        {'position': 'C1', 'type_': 'index', 'title': 'Suite X', 'duration': '', 'sub_tracks': [sub('C1a', 'Transition'), sub('C1b', 'Phase 4'), sub('C1c', 'Coda')]},
        sub('C2', 'Encore Piece')]}
    plain = {'id': 2, 'title': 'Trisect', 'tracklist': [sub('1', 'Introduction'), sub('2', 'Phase 1'), sub('3', 'Phase 2 / Phase 3'), sub('4', 'Transition / Phase 4 / Coda')]}
    none = {'id': 3, 'title': 'Songs', 'tracklist': [sub('1', 'One'), sub('2', 'Two')]}
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const [d, plain, none] = JSON.parse(process.argv[2]);
const r = m.DISCOGS.toRelease(d, d.id);
console.log(JSON.stringify({
  headings: r.headings, tracks: r.tracks.map((t) => [t.position, t.title, t.parts || null, t.indexTitle || null]),
  parts: [m.titleParts('Phase 2 / Phase 3'), m.titleParts('AC/DC')],
  kinds: ['Side A', 'CD 1', 'Bonus Tracks', 'Encore', 'Recorded live at Moers, 1981', 'Trisect', 'Sidewinder'].map(m.headingKind),
  offers: [m.suiteOffers(r), m.suiteOffers(m.DISCOGS.toRelease(plain, 2)), m.suiteOffers(m.DISCOGS.toRelease(none, 3))],
}));
"""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps([d, plain, none])], capture_output=True, text=True)
    got = json.loads(js.stdout) if not js.returncode else {'error': js.stderr[-600:]}
    print('A)', got.get('headings'), '\n  ', got.get('tracks'))
    print('B)', got.get('parts'), got.get('kinds'))
    print('C)', got.get('offers'))
    results = [
        got.get('headings') == [{'title': 'Side A', 'at': 0}, {'title': 'Trisect', 'at': 2}, {'title': 'Recorded live at Moers, 1981', 'at': 5}]
        and got.get('tracks') == [['A1', 'Introduction', None, None], ['A2', 'Phase 1', None, None], ['A3', 'Phase 2 / Phase 3', None, None], ['B1', 'Interlude', None, None],
                                  ['B2', 'Finale', None, None], ['C1', 'Suite X', ['Transition', 'Phase 4', 'Coda'], 'Suite X'], ['C2', 'Encore Piece', None, None]],
        got.get('parts') == [['Phase 2', 'Phase 3'], []] and got.get('kinds') == ['medium', 'medium', 'medium', 'medium', 'recording', 'name', 'name'],
        got.get('offers') == [[{'name': 'Trisect', 'from': 'heading', 'tracks': [2, 3, 4]}, {'name': 'Suite X', 'from': 'index', 'tracks': [5]}],
                              [{'name': 'Trisect', 'from': 'release', 'tracks': [0, 1, 2, 3]}], []],
    ]
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suiteask():
    """Credits Importer 3.41.1 (collected item Z-SU; Q-bt, Q-bu, Q-bv, Q-cc, Q-ci): the question of a suite and its parts as works.
    The release "Trisect" (Discogs 2793066 in short): 1 Introduction · 2 Phase 1 · 3 Phase 2 / Phase 3 · 4 Transition / Phase 4 / Coda;
    track 1 has a work in MusicBrainz.
    A) At the top of the works matrix, yellow: "all 4 tracks: parts of the suite “Trisect”?" – ✓ Yes, ✕ No, another name, "from the
       title of the release".
    B) ✓ Yes: track 2 one new work "Trisect: Phase 1", track 3 two ("part 1 of 2" "Trisect: Phase 2", "part 2 of 2" "Trisect: Phase 3"),
       track 4 three; track 1 keeps its work; the line "all 4 tracks: parts of the suite “Trisect” – 6 works ↺ undo"; the log says so.
    C) Staged: the recording of track 3 with "Trisect: Phase 2" (order 1) and "Trisect: Phase 3" (order 2), of track 4 three in their
       order, of track 2 one (no order); the new works of the parts have no type.
    D) ⚙ Settings → Works → "Suite, Part": "Trisect, Phase 2" … (stored); ↺ of the topic: "Suite: Part" again.
    E) ↺ undo: the parts gone, the question back; ✕ No: "all 4 tracks: no suite “Trisect”" with "↺ ask again"; another name
       ("Trisect Suite") with "✓ Yes, with this name": "Trisect Suite: Introduction" is not planned (track 1 has its work),
       "Trisect Suite: Phase 1" is."""
    H.TITLES[:] = ['Introduction', 'Phase 1', 'Phase 2 / Phase 3', 'Transition / Phase 4 / Coda']
    orig = H.discogs_release

    def rel():
        d = orig()
        d['title'] = 'Trisect'
        return d

    H.discogs_release = rel
    ASK = """(() => { const b = document.querySelector('[data-el=suites]'); if (!b) return null; return [...b.children].map(x => [x.className,
      x.querySelector('strong') ? x.querySelector('strong').textContent.trim() : x.textContent.replace(/\\s+/g, ' ').trim(), [...x.querySelectorAll('button')].map(y => y.textContent.trim()),
      (x.querySelector('[data-f=suite-name]') || {}).value || null, getComputedStyle(x).backgroundColor]); })()"""
    PARTS = """(i) => [...document.querySelectorAll(`.dci-matrix tr[data-work="${i}"]`)].map(tr => [(tr.querySelector('.dci-mx-part') || {textContent: ''}).textContent.trim(),
      (tr.querySelector('.dci-mx-line strong') || tr.querySelector('.dci-mx-line .dci-mblink') || {textContent: ''}).textContent.trim()])"""
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 278).map(r => [r.entity0.gid ? r.entity0.gid.slice(-1) : '', r.entity1.name, r.linkOrder, r.entity1.typeID == null]))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "!!document.querySelector('[data-el=suites] .dci-mx-suite')", 60)
        pg.wait_for_timeout(500)
        a0 = pg.evaluate(ASK)
        print('A)', a0)
        results.append(a0 is not None and len(a0) == 1 and a0[0][1] == 'all 4 tracks: parts of the suite “Trisect”?' and a0[0][2] == ['✓ Yes', '✕ No', '✓ Yes, with this name']
                       and a0[0][3] == 'Trisect' and a0[0][4] == 'rgb(255, 248, 219)' and 'from the title of the release' in pg.evaluate("document.querySelector('[data-el=suites] .dci-mx-suite').textContent"))
        pg.click('[data-el=suites] [data-act=suite-yes]'); pg.wait_for_timeout(500)
        b0 = [pg.evaluate(PARTS, i) for i in range(4)] + [pg.evaluate(ASK)[0][1], [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'Suite “' in x]]
        print('B)', b0)
        results.append(b0[1] == [['', 'Trisect: Phase 1']] and b0[2] == [['part 1 of 2', 'Trisect: Phase 2'], ['part 2 of 2', 'Trisect: Phase 3']]
                       and b0[3] == [['part 1 of 3', 'Trisect: Transition'], ['part 2 of 3', 'Trisect: Phase 4'], ['part 3 of 3', 'Trisect: Coda']]
                       and b0[0] and b0[0][0][0] == '' and b0[4] == 'all 4 tracks: parts of the suite “Trisect” – 6 works ↺ undo'
                       and b0[5] == ['Suite “Trisect” (all 4 tracks): 6 parts planned as works'])
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        c0 = sorted(pg.evaluate(STAGED))
        print('C)', c0)
        results.append([x for x in c0 if x[1].startswith('Trisect')] == sorted([[H.REC[1][-1], 'Trisect: Phase 1', 0, True], [H.REC[2][-1], 'Trisect: Phase 2', 1, True], [H.REC[2][-1], 'Trisect: Phase 3', 2, True],
                                                                              [H.REC[3][-1], 'Trisect: Coda', 3, True], [H.REC[3][-1], 'Trisect: Phase 4', 2, True], [H.REC[3][-1], 'Trisect: Transition', 1, True]]))
        H.open_settings(pg, 'works')
        pg.click('[data-el=settings] [data-act=suite-naming][data-naming=comma]'); pg.wait_for_timeout(400)
        d0 = [pg.evaluate("localStorage.getItem('dci-suite-naming')"), pg.evaluate(PARTS, 2)]
        pg.click('[data-el=settings] [data-act=settings-reset][data-topic=works]'); pg.wait_for_timeout(400)
        d1 = [pg.evaluate("localStorage.getItem('dci-suite-naming')"), pg.evaluate(PARTS, 2)]
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()'); pg.wait_for_timeout(200)
        print('D)', d0, d1)
        results.append(d0 == ['"comma"', [['part 1 of 2', 'Trisect, Phase 2'], ['part 2 of 2', 'Trisect, Phase 3']]] and d1 == [None, [['part 1 of 2', 'Trisect: Phase 2'], ['part 2 of 2', 'Trisect: Phase 3']]])
        pg.click('[data-el=suites] [data-act=suite-undo]'); pg.wait_for_timeout(400)
        e0 = [pg.evaluate(ASK)[0][0], pg.evaluate(PARTS, 2)]
        pg.click('[data-el=suites] [data-act=suite-no]'); pg.wait_for_timeout(400)
        e1 = pg.evaluate(ASK)[0][1:3]
        pg.click('[data-el=suites] [data-act=suite-undo]'); pg.wait_for_timeout(400)
        pg.fill('[data-el=suites] [data-f=suite-name]', 'Trisect Suite')
        pg.click('[data-el=suites] [data-act=suite-yes-name]'); pg.wait_for_timeout(400)
        e2 = [pg.evaluate(PARTS, 0), pg.evaluate(PARTS, 1)]
        print('E) ↺:', e0, '| ✕:', e1, '| anderer Name:', e2)
        results.append('dci-mx-suite' in e0[0] and len(e0[1]) == 1 and e0[1][0][0] == '' and e1 == ['all 4 tracks: no suite “Trisect” ↺ ask again', ['↺ ask again']]
                       and e2[1] == [['', 'Trisect Suite: Phase 1']] and not any('Trisect Suite' in x[1] for x in e2[0]))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
