"""Works: the works of the artists, skipping the works matrix, choosing works, suites and medleys (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103; 3.72.0: the live comments in t_works_live.py, the covers in t_works_cover.py).

Cases: artistworks, worksskip, workpick (3.38.15), suitedata (3.41.0), suiteask (3.41.1), suiteparts (3.41.2), medley (3.41.3), suiteadd (3.41.11), subtracks (3.41.12), suiterestage (3.41.4), wts (3.52.0); `python3 t_works_more.py <case> …` runs only those."""
import re
import urllib.parse
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
    folded: w.querySelector('[data-el=works-folded]') ? [...w.querySelectorAll('.dci-wh-chip, [data-el=works-folded]')].map((e) => e.textContent).join(' · ') : '', badge: (w.querySelector('.dci-works-skipped') || {}).textContent || '',
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
        # ([Z-SETTABS2] 3.137.0) a row of two columns: the name (with the tooltip) on the left, "(0: never)" below the field
        f = pg.evaluate("(() => { const i = document.querySelector('[data-set=awAsk]'); const r = i && i.closest('.dci-set-row'); return i ? [i.value, i.min, i.getAttribute('aria-label'), r.textContent.replace(/\\s+/g, ' ').trim(), r.querySelector('.dci-set-lbl').title] : null; })()")
        pg.evaluate("localStorage.removeItem('dci-aw-ask')")
        print('   Einstellung:', f)
        results.append(f is not None and f[0] == '3' and f[1] == '0' and 'tracks without a work' in f[3] and f[3].endswith('0: never')
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
        results.append(a4 and a4['btn'] == '2 works ▾' and a4['exp'] == 'false' and not a4['shown'] and a4['sameLine'] and a4['badge'].lstrip('○ ') == 'no work yet'
                       and a3 and a3['btn'] == '1 work ▾' and a3['badge'].lstrip('○ ') == 'no work yet' and not a3['shown'])
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


def case_suitedata():
    """Credits Importer 3.41.0 (collected item Z-SU; Q-bt, Q-ca, Q-ch): what a suite can be made of – in Node.
    A) Discogs: the headings of the track list kept ("Side A" before track 1, "Trisect" before track 3 …), the sub-tracks of an
       index of one track as its parts ("Transition", "Phase 4", "Coda"), the index's title kept (until 3.40.17 headings were left
       out and the sub-tracks only their positions).
    B) The parts of a title: "Phase 2 / Phase 3" → two, "AC/DC" none; headings: "Side A", "CD 1", "Bonus Tracks", "Encore" – a side
       or medium (T061), "Recorded live at Moers, 1981" – a recording, "Trisect", "Sidewinder" – a name.
    C) The suites offered: below the heading "Trisect" tracks 3–5 (until "Recorded live …"), the index "Suite X" for track 6; a
       release without headings whose track has parts: all tracks with the release's title; without parts: none.
    D) (3.41.4, review) "Japan Bonus Tracks", "DVD", "Remixes": no suite; one track of four with parts: no suite of the release's title
       (a medley); a composer and the work before the same track: the work."""
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
  // (3.41.4, review) bonus anywhere, DVD; one track of four with parts: no suite of the release; two headings before one track
  more: [['Japan Bonus Tracks', 'DVD', 'Remixes'].map(m.headingKind),
    m.suiteOffers({ title: 'Songs', tracks: [{ title: 'A / B' }, { title: 'C' }, { title: 'D' }, { title: 'E' }], headings: [] }),
    m.suiteOffers({ title: 'X', tracks: [{ title: 'I' }, { title: 'II' }], headings: [{ title: 'Jean Sibelius', at: 0 }, { title: 'Karelia Suite', at: 0 }] })],
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
        got.get('more') == [['medium', 'medium', 'medium'], [], [{'name': 'Karelia Suite', 'from': 'heading', 'tracks': [0, 1]}]],
    ]
    print('D)', got.get('more'))
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
    # ((3.41.11) the line "＋ Suite …" below the questions is not one of them)
    # ([3.52.0] the questions in the header rows of the matrix: SUITES)
    ASK = """(() => { if (!document.querySelector('[data-el=works] table.dci-matrix')) return null; return [...document.querySelectorAll('[data-el=works] [data-suite]')].map(x => [x.className,
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
        H.wait_for(pg, "!!document.querySelector('[data-el=works] .dci-mx-suite')", 60)
        pg.wait_for_timeout(500)
        a0 = pg.evaluate(ASK)
        print('A)', a0)
        results.append(a0 is not None and len(a0) == 1 and a0[0][1] == 'all 4 tracks: parts of the suite “Trisect”?' and a0[0][2] == ['✓ Yes', '✕ No suite', '✓ Yes, with this name']
                       and a0[0][3] == 'Trisect' and a0[0][4] == 'rgb(255, 248, 219)' and 'from the title of the release' in pg.evaluate("document.querySelector('[data-el=works] .dci-mx-suite').textContent"))
        pg.click('[data-el=works] [data-act=suite-yes]'); pg.wait_for_timeout(500)
        b0 = [pg.evaluate(PARTS, i) for i in range(4)] + [pg.evaluate(ASK)[0][1], [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'Suite “' in x]]
        print('B)', b0)
        results.append(b0[1] == [['', 'Trisect: Phase 1']] and b0[2] == [['part 1 of 2', 'Trisect: Phase 2'], ['part 2 of 2', 'Trisect: Phase 3']]
                       and b0[3] == [['part 1 of 3', 'Trisect: Transition'], ['part 2 of 3', 'Trisect: Phase 4'], ['part 3 of 3', 'Trisect: Coda']]
                       and b0[0] and b0[0][0][0] == '' and b0[4].startswith('all 4 tracks: parts of the suite “Trisect” – 6 works ✎ ＋ Create the suite in MusicBrainz …')  # ([Z-SUITERENAME] 3.196.0 ✎) and b0[4].endswith('↺ undo')
                       and b0[5] == ['Suite “Trisect” (all 4 tracks): 6 parts planned as works'])
        # [3.52.0] (Q-fw) the question in a header row of the matrix above its first track, the tracks of the suite indented below it
        rows0 = pg.evaluate("""[...document.querySelectorAll('.dci-matrix tbody > tr')].map(tr => tr.classList.contains('dci-mx-suiterow') ? 'suite'
          : tr.classList.contains('dci-mx-inpart') ? 'part' : 'row')""")
        print('   Zeilen:', rows0)
        results.append(rows0[0] == 'suite' and rows0.count('suite') == 1 and rows0[1:] and set(rows0[1:]) == {'part'})
        H.stage_click(pg, least=3500)
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
        pg.click('[data-el=works] [data-act=suite-undo]'); pg.wait_for_timeout(400)
        e0 = [pg.evaluate(ASK)[0][0], pg.evaluate(PARTS, 2)]
        pg.click('[data-el=works] [data-act=suite-no]'); pg.wait_for_timeout(400)
        e1 = pg.evaluate(ASK)[0][1:3]
        pg.click('[data-el=works] [data-act=suite-undo]'); pg.wait_for_timeout(400)
        pg.fill('[data-el=works] [data-f=suite-name]', 'Trisect Suite')
        pg.click('[data-el=works] [data-act=suite-yes-name]'); pg.wait_for_timeout(400)
        e2 = [pg.evaluate(PARTS, 0), pg.evaluate(PARTS, 1)]
        print('E) ↺:', e0, '| ✕:', e1, '| anderer Name:', e2)
        results.append('dci-mx-suite' in e0[0] and len(e0[1]) == 1 and e0[1][0][0] == '' and e1 == ['all 4 tracks: no suite “Trisect” ↺ ask again', ['↺ ask again']]
                       and e2[1] == [['', 'Trisect Suite: Phase 1']] and not any('Trisect Suite' in x[1] for x in e2[0]))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suiteparts():
    """Credits Importer 3.41.2 (collected item Z-SU; Q-bv), 3.41.6 (Z-SUW, user report): the suite itself – a work of the type "Suite"
    with "parts". The release "Trisect" (as in suiteask; Writer W credited for all four tracks, Writer Z for track 3 too), ✓ Yes:
    A) The line of the suite: "＋ Create the suite in MusicBrainz …" and "Its “parts” wait …"; staged: the parts with their recordings,
       no "parts" yet (until 3.41.5 "parts" to a new work "Trisect" – MusicBrainz does not create a work linked by "parts" only:
       "An error occurred: unknown Work id:" on "Enter edit").
    B) "＋ Create …": MusicBrainz's form in the dashboard with the name "Trisect", the type Suite (6) and Writer W (the writer of all
       its tracks; not Writer Z); submitted (the frame on /work/<mbid>): "Suite in MusicBrainz: Trisect" (a link to it), the message
       says so.
    C) Staged again: "parts" from the work "Trisect" of MusicBrainz to each part, in the order of the parts – the work of track 1 in
       MusicBrainz ("Introduction") first, then "Trisect: Phase 1", "Trisect: Phase 2", … (order 1–7), each with "movement"; no
       recording is linked with it; the preview names them ("part 1 of the suite “Trisect” (movement)"); (3.41.15, review) the edit note
       says "linked 6 works to recordings; … linked 7 parts with their suites" (until 3.41.14 the parts counted as works linked).
    D) ↺ undo of the suite (before staging): nothing of it is planned."""
    H.TITLES[:] = ['Introduction', 'Phase 1', 'Phase 2 / Phase 3', 'Transition / Phase 4 / Coda']
    H.attr(1105, 'movement', 1105)
    H.lt(281, 'ca8d3642-ce5f-49f8-91f2-125d72524e6a', 'parts', 'work', 'work', (1105,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.WORK_FORM = H.WORK_FORM.replace('<option value="1">Aria</option>', '<option value="1">Aria</option><option value="6">Suite</option>')
    SUITE = H.uid('cccccccc', 96)
    WW = H.ARTISTS[3007][0]
    orig = H.discogs_release

    def rel():
        d = orig()
        d['title'] = 'Trisect'
        for t in d['tracklist'][2:]:
            t['extraartists'] = list(t.get('extraartists') or []) + [{'name': 'Writer W', 'anv': '', 'role': 'Written-By', 'tracks': '', 'id': 3007, 'join': ''}]
        return d

    H.discogs_release = rel
    PARTS = """(() => { const ids = (r) => r && r.attributes && r.attributes.__tree ? r.attributes.__tree.map(a => a.typeID || a.type.id) : [];
      return MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 281).map(r => [r.entity0.name, r.entity0.gid, r.entity1.name, r.linkOrder, ids(r)])
        .sort((a, b) => a[3] - b[3]); })()"""
    LINE = "(x => x ? [x.textContent.replace(/\\s+/g, ' ').trim(), [...x.querySelectorAll('button')].map(b => b.dataset.act), (x.querySelector('a.dci-suite-mb') || {}).href || null] : null)(document.querySelector('[data-el=works] .dci-mx-suite-done'))"
    PREVIEW = "[...document.querySelectorAll('li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /of the suite/.test(t))"

    def stage():
        H.stage_click(pg, least=3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(300)
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "!!document.querySelector('[data-el=works] .dci-mx-suite')", 60)
        pg.wait_for_timeout(500)
        # D) first: undone, nothing planned
        pg.click('[data-el=works] [data-act=suite-yes]'); pg.wait_for_timeout(300)
        pg.click('[data-el=works] [data-act=suite-undo]'); pg.wait_for_timeout(300)
        pg.click('[data-act=preview]'); pg.wait_for_timeout(500)
        d0 = pg.evaluate("[...document.querySelectorAll('.dci-preview li, [data-el=preview] li')].map(li => li.textContent).filter(t => /suite/.test(t)).length")
        pg.click('[data-act=preview]'); pg.wait_for_timeout(300)
        pg.click('[data-el=works] [data-act=suite-yes]'); pg.wait_for_timeout(500)
        a0 = pg.evaluate(LINE)
        pg.click('[data-act=preview]'); pg.wait_for_timeout(500)
        a1 = pg.evaluate(PREVIEW)
        pg.click('[data-act=preview]'); pg.wait_for_timeout(300)
        stage()
        a2 = [pg.evaluate(PARTS), pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 278 && /^Trisect: /.test(r.entity1.name)).length")]
        print('A)', a0, '| Vorschau:', a1, '| vorgemerkt:', a2)
        results.append(a0 is not None and '＋ Create the suite in MusicBrainz …' in a0[0] and 'Its “parts” wait until the suite exists in MusicBrainz' in a0[0]
                       and a0[1] == ['suite-rename', 'suite-create', 'suite-naming1', 'suite-undo'] and a0[2] is None and a1 == [] and a2 == [[], 6])
        pg.click('[data-el=works] [data-act=suite-create]')
        H.wait_for(pg, "!!document.querySelector('[data-el=sub-frame]') && /work\\/create/.test(document.querySelector('[data-el=sub-frame]').src)", 20)
        src = pg.evaluate("document.querySelector('[data-el=sub-frame]').src")
        q = urllib.parse.parse_qs(urllib.parse.urlparse(src).query)
        info = pg.evaluate("(document.querySelector('.dci-subdlg') || {textContent: ''}).textContent.replace(/\\s+/g, ' ')")
        b0 = [q.get('edit-work.name'), q.get('edit-work.type_id'), q.get('rels.0.target'), q.get('rels.1.target'), 'edit-work.languages.0' in q]
        H.COMPANIES[7096] = ('work', SUITE, 'Trisect')
        H.WORK_TITLES[SUITE] = 'Trisect'
        pg.evaluate(f"document.querySelector('[data-el=sub-frame]').src = 'https://musicbrainz.org/work/{SUITE}'")
        H.wait_for(pg, "!!document.querySelector('[data-el=works] a.dci-suite-mb')", 20)
        pg.wait_for_timeout(400)
        b1 = [pg.evaluate(LINE), pg.evaluate("[...document.querySelectorAll('.dci-msg, [data-el=messages] *')].map(x => x.textContent).join(' ')")]
        print('B)', b0, '| Info:', info[:160], '\n  ', b1[0], '|', 'Suite “Trisect” has been created' in b1[1])
        results.append(b0 == [['Trisect'], ['6'], [WW], None, False] and 'work type Suite, writer: Writer W.' in info and 'Writer Z' not in info
                       and b1[0][1] == ['suite-naming1', 'suite-undo'] and b1[0][2] and b1[0][2].endswith(f'/work/{SUITE}') and 'Suite in MusicBrainz: Trisect' in b1[0][0]
                       and 'Suite “Trisect” has been created' in b1[1])
        pg.click('[data-act=preview]'); pg.wait_for_timeout(500)
        c1 = pg.evaluate(PREVIEW)
        pg.click('[data-act=preview]'); pg.wait_for_timeout(300)
        stage()
        c0 = pg.evaluate(PARTS)
        rec = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 278 && r.entity1 && r.entity1.name === 'Trisect').length")
        note = [l for l in pg.evaluate("document.getElementById('edit-note-text').value").splitlines() if l.startswith('Done:')]
        print('   Notiz:', note)
        # (3.41.15, review) the parts with their suite are no works linked with recordings
        results.append(note and 'linked 7 parts with their suites' in note[0] and 'linked 6 works to recordings' in note[0])
        print('C)', c0, '| Aufnahme mit der Suite:', rec, '| Vorschau:', c1[:2], len(c1))
        print('D) nach ↺:', d0)
        want = ['Introduction', 'Trisect: Phase 1', 'Trisect: Phase 2', 'Trisect: Phase 3', 'Trisect: Transition', 'Trisect: Phase 4', 'Trisect: Coda']
        results.append(len(c0) == 7 and [x[2] for x in c0] == want and [x[3] for x in c0] == [1, 2, 3, 4, 5, 6, 7]
                       and all(x[0] == 'Trisect' and x[1] == SUITE and x[4] == [1105] for x in c0) and rec == 0)
        results.append(len(c1) == 7 and any('part 1 of the suite “Trisect”' in t and 'movement' in t for t in c1))
        results.append(d0 == 0)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_medley():
    """Credits Importer 3.41.3 (collected item Z-SU; Q-cb, Q-cd, Q-cg): a track of several works – a medley.
    Track 3 "Alpha / Beta" (Writer Z composed it); MusicBrainz has Writer Z's work "Beta".
    A) No suite asked ((3.41.4, review) one track of four with parts: a medley, not a suite of the release); track 3 (no work yet):
       "Split into 2 works (medley)" in its line (its tooltip names the parts) – not done by itself.
    B) Clicked: "medley 1 of 2" Alpha (a new work), "medley 2 of 2" Beta – a new work, (3.41.4, review) Writer Z's work "Beta" of
       MusicBrainz offered at it ("Link “Beta”"; until 3.41.3 taken by itself), "↺ one work"; the log says so; "Link “Beta”" links it.
    C) Staged: the recording of track 3 with "Alpha" (order 1) and "Beta" (order 2), both with "medley".
    D) "↺ one work": the track with one new work again ((3.99.0, review) "＋ New" planned it), the split offered again."""
    H.TITLES[2] = 'Alpha / Beta'
    WZ = H.ARTISTS[3009][0]
    BETA = H.uid('cccccccc', 95)
    H.attr(757, 'medley', 757)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (757,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.WORK_SEARCH[:] = [{'id': BETA, 'title': 'Beta', 'type': 'Song', 'aliases': [], 'relations': [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': WZ, 'name': 'Writer Z'}}]}]
    H.COMPANIES[7095] = ('work', BETA, 'Beta')
    ROWS = """() => [...document.querySelectorAll('.dci-matrix tr[data-work="2"]')].map(tr => [(tr.querySelector('.dci-mx-part') || {textContent: ''}).textContent.trim(),
      (tr.querySelector('.dci-mx-line strong') || tr.querySelector('.dci-mx-line .dci-mblink') || {textContent: ''}).textContent.trim(),
      [...tr.querySelectorAll('.dci-mx-line button')].map(b => b.textContent.trim()).filter(t => /medley|one work/.test(t))])"""
    STAGED = """(() => { const ids = (r) => r && r.attributes && r.attributes.__tree ? r.attributes.__tree.map(a => a.typeID || a.type.id) : [];
      return MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 278 && r.entity0.gid === '%s').map(r => [r.entity1.name, r.linkOrder, ids(r)]).sort((a, b) => a[1] - b[1]); })()""" % H.REC[2]
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "!!document.querySelector('.dci-matrix tr[data-work=\"2\"] [data-act=medley-mark]')", 60)
        pg.wait_for_timeout(500)
        a0 = [pg.evaluate(ROWS), pg.evaluate("(b => b ? b.title : null)(document.querySelector('.dci-matrix tr[data-work=\"2\"] [data-act=medley-mark]'))"),
              pg.evaluate("document.querySelectorAll('[data-el=works] .dci-mx-suite').length")]
        print('A)', a0)
        results.append(a0[0] == [['', '', ['Split into 2 works (medley)']]] and a0[1] == 'Switch: when “＋ New” or “＋ New works” plans this track, each part becomes a work of its own: Alpha · Beta' and a0[2] == 0)
        # ([3.52.0] clicked through the page: scrolled into view, the button may end up below the log of the harness)
        # ([3.99.0, Z-MDLY2] a switch: the parts come with "＋ New")
        pg.locator('.dci-matrix tr[data-work="2"] [data-act=medley-mark]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
        pg.locator('.dci-matrix tr[data-work="2"] [data-act=work-pending]').evaluate('b => b.click()')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /MusicBrainz has works for/.test(li.textContent))", 30)
        pg.wait_for_timeout(500)
        b0 = [pg.evaluate(ROWS), [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'medley' in x or 'MusicBrainz has works' in x],
              pg.evaluate("[...document.querySelectorAll('.dci-matrix tr[data-work=\"2\"] [data-act=part-pick]')].map(b => b.textContent.trim())")]
        pg.locator('.dci-matrix tr[data-work="2"] [data-act=part-pick]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
        b1 = pg.evaluate(ROWS)
        print('B)', b0, '\n  ', b1)
        results.append(b0[0] == [['medley 1 of 2', 'Alpha', ['↺ one work']], ['medley 2 of 2', 'Beta', []]] and b0[2] == ['Link “Beta”']
                       and b0[1] == ['Track 1.3: split into 2 works (medley)', 'Track 1.3: MusicBrainz has works for 1 of its parts – offered at them']
                       and b1 == [['medley 1 of 2', 'Alpha', ['↺ one work']], ['medley 2 of 2', 'MBBeta', []]])
        H.stage_click(pg, least=3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        c0 = pg.evaluate(STAGED)
        print('C)', c0)
        results.append(c0 == [['Alpha', 1, [757]], ['Beta', 2, [757]]])
        pg.locator('.dci-matrix tr[data-work="2"] [data-act=medley-join]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
        d0 = pg.evaluate(ROWS)
        print('D)', d0)
        # ((3.99.0, review) "＋ New" planned the track: joined, it is that one new work again, the split offered again)
        results.append(d0 == [['', 'Alpha / Beta', ['Split into 2 works (medley)']]])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_segue3204():
    """Credits Importer 3.204.0 (collected item Z-SEGUE, rule S391): segues of jam bands – track 3 "The Killers > Narragansett" (one track,
    two pieces), track 4 "China Cat Sunflower >" (the next piece follows on its own track).
    A) Track 3: "Split into 2 works (medley)" as for "/" – its parts The Killers · Narragansett; track 4: no split (a sign at the end only).
    B) S391 off: no split for track 3."""
    t0 = list(H.TITLES)
    H.TITLES[2] = 'The Killers > Narragansett'
    H.TITLES[3] = 'China Cat Sunflower >'
    H.attr(757, 'medley', 757)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (757,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    TIP = "(i) => (b => b ? b.title : null)(document.querySelector(`.dci-matrix tr[data-work=\"${i}\"] [data-act=medley-mark]`))"
    results = []

    def run(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Works of the artists compared|Checks complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
        out = [pg.evaluate(TIP, 2), pg.evaluate(TIP, 3)]
        b.close()
        return out, errs

    try:
        with sync_playwright() as p:
            a, errs = run(p)
            print('A)', a, errs)
            results.append(bool(a[0]) and a[0].endswith('The Killers · Narragansett') and a[1] is None and not errs)
            bb, errs = run(p, off=['S391'])
            print('B)', bb, errs)
            results.append(bb[0] is None and not errs)
    finally:
        H.TITLES[:] = t0
        H.RULES_OFF = []
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_mdly398():
    """Credits Importer 3.98.0 (collected item Z-MDLY; rule S157): medleys by the separators of the release; traditional tunes arranged.
    Track 2 "Alpha/Beta" (no spaces), track 3 "AC/DC Song", track 4 "Gamma + Delta"; Traditional wrote, The Band arranged (Discogs).
    MusicBrainz has two works "Alpha" by [traditional] – A1 with 3 recordings, A2 with 1 and an arrangement "Alpha" of another band.
    A) In the head: "Medleys: split 1 title" (track 2; "AC/DC" is an exception, "+" no separator yet), "✎ /".
    B) ✎, "+" added: "split 2 titles"; clicked: ([3.99.0] a switch – "✓", nothing split yet) "＋ New works": track 2 → Alpha · Beta,
       track 4 → Gamma · Delta (the titles of MusicBrainz).
    C) Alpha (a traditional tune with arrangers): a new work, "arrangement of" suggested in yellow – A1 first ("3 recordings"), A2 in its
       list – and "an arrangement exists: Alpha (Other Band arrangement)" (stage 1, the arrangements of A2).
    D) "link it instead": the part linked to that arrangement, the suggestion gone.
    E) (review) In Node, medleySplit: "/" with or without spaces, other separators only with spaces ("Hip-Hop", "Mr. Brown" whole),
       nothing inside brackets, the exceptions whole ("AC/DC", "w/Friends", "24/7", "1/2"); suites keep " / " (titleParts)."""
    import json
    import subprocess
    TRAD = '9be7f096-97ec-4615-8957-8d40b5dcbc41'
    H.TITLES[1] = 'Alpha/Beta'
    H.TITLES[2] = 'AC/DC Song'
    H.TITLES[3] = 'Gamma + Delta'
    H.attr(757, 'medley', 757)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (757,))
    H.lt(350, H.uid('1aaa0000', 350), 'arrangement', 'work', 'work')
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.ARTISTS[3093] = (TRAD, '[traditional]')
    H.ARTISTS[3094] = (H.uid('dddddddd', 94), 'The Band')
    A1, A2, EX = H.uid('cccccccc', 141), H.uid('cccccccc', 142), H.uid('cccccccc', 143)
    rel_trad = [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': TRAD, 'name': '[traditional]'}}]
    H.WORK_SEARCH[:] = [{'id': A1, 'title': 'Alpha', 'type': 'Song', 'aliases': [], 'relations': rel_trad},
                        {'id': A2, 'title': 'Alpha', 'type': 'Song', 'aliases': [], 'disambiguation': 'reel', 'relations': rel_trad}]
    rec = lambda k: {'target-type': 'recording', 'type': 'performance', 'recording': {'id': H.uid('eeeeeeee', k), 'title': 'Alpha'}}
    H.MB_EXTRA[A1] = [rec(1), rec(2), rec(3)]
    H.MB_EXTRA[A2] = [rec(4), {'target-type': 'work', 'type': 'arrangement', 'direction': 'forward',
                               'work': {'id': EX, 'title': 'Alpha', 'disambiguation': 'Other Band arrangement'}}]
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': 'Traditional', 'anv': '', 'role': 'Written-By', 'tracks': '', 'id': 3093, 'join': ''},
                             {'name': 'The Band', 'anv': '', 'role': 'Arranged By', 'tracks': '', 'id': 3094, 'join': ''}]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    HEAD = """(() => { const h = document.querySelector('[data-el=works] .dci-mx-medleys'); return h ? [(h.querySelector('[data-act=medley-split-all]') || {}).textContent || '',
      (h.querySelector('[data-act=medley-seps]') || {}).textContent.trim()] : null; })()"""
    PARTS = """(i) => [...document.querySelectorAll(`.dci-matrix tr[data-work="${i}"]`)].map(tr => (tr.querySelector('.dci-mx-line strong') || tr.querySelector('.dci-mx-line .dci-mblink') || tr.querySelector('.dci-mx-title strong') || {textContent: ''}).textContent.trim())"""
    SUGG = """(() => { const x = document.querySelector('.dci-matrix tr[data-work="1"] [data-wnote=arrsugg]'); return x ? [x.textContent.replace(/\\s+/g, ' ').trim(),
      [...x.querySelectorAll('select[data-f=mx-arr-cand] option')].map(o => o.textContent), !!x.querySelector('[data-act=arr-existing]')] : null; })()"""
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(800)
            a0 = pg.evaluate(HEAD)
            print('A)', a0)
            results.append(a0 == ['Medleys: split 1 title', '✎ /'])
            pg.locator('[data-el=works] [data-act=medley-seps]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            pg.fill('[data-el=works] [data-f=mx-medley-sep]', '+')
            pg.press('[data-el=works] [data-f=mx-medley-sep]', 'Enter'); pg.wait_for_timeout(400)
            b0 = pg.evaluate(HEAD)
            pg.locator('[data-el=works] [data-act=medley-split-all]').evaluate('b => b.click()'); pg.wait_for_timeout(500)
            b2 = [pg.evaluate(PARTS, 1), pg.evaluate("(b => b ? [b.getAttribute('aria-pressed'), b.textContent.trim()] : null)(document.querySelector('[data-el=works] [data-act=medley-split-all]'))")]
            # ([3.99.0, Z-MDLY2] a switch: nothing split until "＋ New works")
            pg.locator('[data-el=works] [data-act=works-pending-all]').evaluate('b => b.click()'); pg.wait_for_timeout(600)
            b1 = [pg.evaluate(PARTS, 1), pg.evaluate(PARTS, 2), pg.evaluate(PARTS, 3)]
            print('B)', b0, b2, b1)
            results.append(b0 == ['Medleys: split 2 titles', '✎ / +'] and b2 == [['Alpha/Beta'], ['true', '✓ Medleys: split 2 titles']]
                           and b1 == [['Alpha', 'Beta'], ['AC/DC Song'], ['Gamma', 'Delta']])
            pg.evaluate("document.activeElement && document.activeElement.blur && document.activeElement.blur()")
            H.wait_for(pg, "!!document.querySelector('.dci-matrix tr[data-work=\"1\"] [data-act=arr-existing]')", 60)
            c0 = pg.evaluate(SUGG)
            print('C)', c0)
            # ([3.99.0, Z-ARRUI] one line: "Alpha → arrangement of [list] ↗ ✓" – the list instead of a second link)
            results.append(bool(c0) and c0[0].startswith('Alpha → arrangement of Alpha – 3 recordings') and '↗' in c0[0] and 'MBAlpha (Other' in c0[0] and c0[1][0].startswith('Alpha – 3 recordings') and 'reel' in c0[1][1] and c0[2]
                           and 'Other Band arrangement' in c0[0])
            pg.locator('.dci-matrix tr[data-work="1"] [data-act=arr-existing]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
            d0 = [pg.evaluate(PARTS, 1), pg.evaluate(SUGG), pg.evaluate("[...document.querySelectorAll('.dci-matrix tr[data-work=\"1\"] .dci-mblink')].map(a => a.getAttribute('href'))")]
            print('D)', d0)
            results.append(d0[0] == ['MBAlpha', 'Beta'] and d0[1] is None and f'/work/{EX}' in d0[2])
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const T = ['Alpha/Beta', 'AC/DC Song', 'Jam w/Friends', 'Song (Live/Remix)', '24/7 Blues / Night', 'Hip-Hop Medley', '1/2 Time', 'Mr. Brown + St. Louis'];
console.log(JSON.stringify([T.map((t) => m.medleySplit(t, ['/', '+', '-'])), m.titleParts('Alpha/Beta'), m.titleParts('Phase 2 / Phase 3'),
  ["Patsy Geary's", "'Twas", "Rock 'n' Roll", "the 'Kesh' Jig", "Say 'Hello Again' Now", "'Til the Mornin'", "Lovin' You 'Til the Mornin'"].map(m.typoQuotes)]));
"""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    e0 = json.loads(js.stdout) if not js.returncode else {'error': js.stderr[-300:]}
    print('E)', e0)
    # ([3.99.0, Z-APOS] new works: ' → ’, quotes ‘…’; (review) an elision first or a dropped g last is no quotation)
    results.append(e0 == [[['Alpha', 'Beta'], [], [], [], ['24/7 Blues', 'Night'], [], [], ['Mr. Brown', 'St. Louis']], [], ['Phase 2', 'Phase 3'],
                          ['Patsy Geary’s', '’Twas', 'Rock ’n’ Roll', 'the ‘Kesh’ Jig', 'Say ‘Hello Again’ Now', '’Til the Mornin’', 'Lovin’ You ’Til the Mornin’']])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_arrdis398():
    """Credits Importer 3.98.0 (collected item Z-ARRDIS; rule S158): the disambiguation of new arrangement works of traditional tunes.
    Traditional wrote, The Band arranged (Discogs); tracks 2–4 get new works ("＋ New works").
    A) In the footer: "Disambiguation “The Band arrangement” for the new arrangement works (3 new works · tracks …)?" ✓ ✕.
    B) ✓: the text field "The Band arrangement" (changed to "The Band arr.").
    C) Staged: the three new works carry the disambiguation; the log says so; ([3.99.0] no box yet – a job of the release waits).
    D) (3.99.0, Z-ARRDIS2) "Enter edit", then the release page: MusicBrainz has the works – the box names them with their links.
    E) (3.99.0, Z-TRADC) [traditional] writes the new works without the credit "Traditional"."""
    TRAD = '9be7f096-97ec-4615-8957-8d40b5dcbc41'
    H.ARTISTS[3093] = (TRAD, '[traditional]')
    H.ARTISTS[3094] = (H.uid('dddddddd', 94), 'The Band')
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': 'Traditional', 'anv': '', 'role': 'Written-By', 'tracks': '', 'id': 3093, 'join': ''},
                             {'name': 'The Band', 'anv': '', 'role': 'Arranged By', 'tracks': '', 'id': 3094, 'join': ''}]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    BOX = "(() => { const x = document.querySelector('.dci-foot [data-el=arrcom]'); return x && !x.hidden ? [x.textContent.replace(/\\s+/g, ' ').trim(), [...x.querySelectorAll('input')].map(i => i.value)] : null; })()"
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 278 && !r.entity1.gid).map(r => [r.entity1.name, r.entity1.comment]).sort())()"""
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(800)
            pg.locator('[data-el=works] [data-act=works-pending-all]').evaluate('b => b.click()'); pg.wait_for_timeout(500)
            a0 = pg.evaluate(BOX)
            print('A)', a0)
            results.append(bool(a0) and a0[0].startswith('Disambiguation “The Band arrangement” for the new arrangement works (3 new works · ') and '2' in a0[0] and '4' in a0[0] and a0[1] == [])
            pg.locator('.dci-foot [data-act=arrcom-yes]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            b0 = pg.evaluate(BOX)
            pg.fill('.dci-foot [data-f=arrcom-text]', 'The Band arr.')
            pg.press('.dci-foot [data-f=arrcom-text]', 'Enter'); pg.wait_for_timeout(300)
            b1 = pg.evaluate(BOX)
            print('B)', b0, b1)
            results.append(bool(b0) and b0[1] == ['The Band arrangement'] and bool(b1) and b1[1] == ['The Band arr.'])
            H.stage_click(pg, least=3500)
            pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
            pg.wait_for_timeout(300)
            c0 = [pg.evaluate(STAGED), pg.evaluate("(document.getElementById('dci-arrcom-notice') || {}).textContent || ''"),
                  [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'disambiguation' in x]]
            print('C)', c0)
            # ([3.99.0, Z-ARRDIS2] no box yet: the works exist only after "Enter edit" – a job of the release waits for it)
            job = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-arrcom-job:{H.REL}') || 'null')")
            results.append(c0[0] == [['Song Four', 'The Band arr.'], ['Song Three', 'The Band arr.'], ['Song Two', 'The Band arr.']]
                           and c0[1] == '' and len(c0[2]) >= 3 and bool(job) and len(job['items']) == 3 and not job['armedAt'])
            # D) "Enter edit" (armed), the release page: MusicBrainz has the works – the box names them with their links
            W = [H.uid('cdcdcdcd', 60 + k) for k in range(4)]
            tracks = [{'number': str(k + 1), 'recording': {'gid': g, 'comment': '', 'relationships':
                       ([{'linkTypeID': 278, 'target': {'gid': W[k], 'name': H.TITLES[k], 'comment': 'The Band arr.'}}] if k else [])}} for k, g in enumerate(H.REC)]
            H.WS_JS_RELEASE.clear()
            H.WS_JS_RELEASE.update({'gid': H.REL, 'mediums': [{'position': 1, 'tracks': tracks}], 'releaseGroup': {'secondaryTypeIDs': []}})
            rp, errs2 = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{H.REL}')
            rp.evaluate("(job) => { job.armedAt = Date.now(); localStorage.setItem('dci-arrcom-job:%s', JSON.stringify(job)); }" % H.REL, job)
            rp.reload()
            H.wait_for(rp, "!!document.getElementById('dci-arrcom-notice')", 20)
            d0 = rp.evaluate("(() => { const n = document.getElementById('dci-arrcom-notice'); return [n.textContent, [...n.querySelectorAll('a')].map(a => a.getAttribute('href'))]; })()")
            job2 = rp.evaluate(f"JSON.parse(localStorage.getItem('dci-arrcom-job:{H.REL}') || 'null')")
            print('D)', d0, bool(job2 and job2.get('done')))
            results.append('“The Band arr.”: Song Two, Song Three, Song Four' in d0[0] and d0[1] == [f'/work/{W[1]}', f'/work/{W[2]}', f'/work/{W[3]}'] and bool(job2 and job2.get('done')))
            H.WS_JS_RELEASE.clear()
            # E) (3.99.0, Z-TRADC) [traditional] as the writer of the new works: no credit "Traditional" (Discogs's name)
            e0 = pg.evaluate("""(() => MB.relationshipEditor.state.added.filter(r => [r.entity0.gid, r.entity1.gid].includes('%s'))
              .map(r => [r.entity0_credit || '', r.entity1_credit || '']))()""" % TRAD)
            print('E)', e0)
            results.append(len(e0) >= 3 and all(c == ['', ''] for c in e0))
            print('Fehler:', errs, errs2)
            results.append(not errs and not errs2)
            b.close()
    finally:
        H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_colw399():
    """Credits Importer 3.99.0 (collected items Z-COLW, Z-APOS): the column of tracks and works no wider than 440 px.
    Track 2 "The Kesh Jig / Give Us a Drink of Water / The Flower of the Flock / Famous Ballymote", track 3 "Patsy Geary's / Coleman's Cross".
    A) The first column of the works matrix at most 460 px (until 3.98.0 as wide as its longest line); the titles wrap.
    B) "＋ New works": the new work of track 3 is "Patsy Geary’s / Coleman’s Cross" (’ instead of '); staged with that name."""
    H.TITLES[1] = 'The Kesh Jig / Give Us a Drink of Water / The Flower of the Flock / Famous Ballymote'
    H.TITLES[2] = "Patsy Geary's / Coleman's Cross"
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
        a0 = pg.evaluate("Math.max(...[...document.querySelectorAll('.dci-matrix th.dci-mx-front')].map(t => t.getBoundingClientRect().width))")
        print('A)', a0)
        results.append(a0 <= 460)
        pg.locator('[data-el=works] [data-act=works-pending-all]').evaluate('b => b.click()'); pg.wait_for_timeout(500)
        b0 = pg.evaluate("(tr => (tr.querySelector('.dci-mx-line strong') || {}).textContent)(document.querySelector('.dci-matrix tr[data-work=\"2\"]'))")
        H.stage_click(pg, least=3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        b1 = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 278 && !r.entity1.gid).map(r => r.entity1.name).filter(n => /Geary/.test(n))")
        print('B)', b0, b1)
        results.append(b0 == 'Patsy Geary’s / Coleman’s Cross' and b1 == ['Patsy Geary’s / Coleman’s Cross'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suiteadd():
    """Credits Importer 3.41.11 (collected item Z-SUM; Q-ck, Q-cq): a suite the source does not show, added by hand.
    The release of the harness (no headings, no index track, no " / "): no suite asked.
    A) "＋ Suite …" below the questions (none here); clicked: the yellow box "Parts of a suite: tracks [1.1 …] to [1.4 …] name: [ ]
       ✓ Yes · Cancel"; ✓ Yes without a name: "Please type the name of the suite." (nothing added).
    B) Tracks 1.2 – 1.4, "Trisect", ✓ Yes: as a suite found in the source – "tracks 2–4: parts of the suite “Trisect” – 3 works" with
       "＋ Create the suite in MusicBrainz …"; the parts "Trisect: …" (a track each); the log says it was added by hand.
    B2) (3.41.15, review) the tracks of "Trisect" cannot become another suite (until 3.41.14 the new suite took them, and undoing it
       left the tracks without a work) – (3.70.0, Z-SU2, S105) only track 1.1 is free (a suite needs two tracks in a row): the box is
       closed, "＋ Another suite …" in the head is disabled ("Every track is in a suite already …").
    C) ↺ undo: the parts go and so does the suite (nothing asked again); "＋ Suite …" is there again. Cancel closes the box.
    D) (3.70.0, Z-SU2) a suite "Duo" of tracks 3–4: tracks 1–2 are free – the box opens again for another suite (from track 1.1, the
       tracks "(Duo)" disabled, "Suites: Duo (tracks 3, 4)", the focus in the name field).
    (Until 3.41.10 a suite could only come from the source.)"""
    H.WORK_FORM = H.WORK_FORM.replace('<option value="1">Aria</option>', '<option value="1">Aria</option><option value="6">Suite</option>')
    # ([3.52.0] the questions in the header rows of the matrix, the box below the head, "＋ Suite …" in the head)
    BOX = """(() => { const w = document.querySelector('[data-el=works]'); const b = w && w.querySelector('[data-el=suites]'); return b ? [...w.querySelectorAll('.dci-matrix [data-suite]'), ...b.children,
      ...w.querySelectorAll('.dci-wh-c [data-act=suite-add-open]')].map(x => [x.className, x.textContent.replace(/\\s+/g, ' ').trim(),
      x.matches('button') ? [x.dataset.act] : [...x.querySelectorAll('button')].map(y => y.dataset.act), [...x.querySelectorAll('select')].map(s => [...s.options].map(o => o.textContent))[0] || null]) : null; })()"""
    PARTS = """(i) => [...document.querySelectorAll(`.dci-matrix tr[data-work="${i}"]`)].map(tr => (tr.querySelector('.dci-mx-line strong') || tr.querySelector('.dci-mx-line .dci-mblink') || tr.querySelector('.dci-mx-title strong') || {textContent: ''}).textContent.trim())"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "!!document.querySelector('[data-el=works] [data-act=suite-add-open]')", 60)
        pg.wait_for_timeout(500)
        a0 = pg.evaluate(BOX)
        pg.click('[data-el=works] [data-act=suite-add-open]'); pg.wait_for_timeout(300)
        a1 = pg.evaluate(BOX)
        pg.click('[data-el=suite-add] [data-act=suite-add-yes]'); pg.wait_for_timeout(300)
        a2 = pg.evaluate("(document.querySelector('[data-el=suite-add-error]') || {}).textContent || null")
        print('A)', a0, '\n  ', a1, '| ohne Namen:', a2)
        results.append(a0 == [['dci-small dci-mx-suite-add', '＋ Suite …', ['suite-add-open'], None]] and a1 and 'dci-mx-suite' in a1[0][0]
                       and a1[0][1].startswith('Parts of a suite: tracks') and a1[0][2] == ['suite-add-yes', 'suite-add-cancel'] and len(a1[0][3]) == 4
                       and a1[0][3][0].startswith('1.1 ') and a2 == 'Please type the name of the suite.' and pg.evaluate("document.querySelectorAll('[data-el=works] [data-suite]').length") == 0)
        pg.select_option('[data-el=suite-add] [data-f=mx-suite-from]', index=1)
        pg.select_option('[data-el=suite-add] [data-f=mx-suite-to]', index=3)
        pg.fill('[data-el=suite-add] [data-f=mx-suite-name]', 'Trisect')
        pg.click('[data-el=suite-add] [data-act=suite-add-yes]'); pg.wait_for_timeout(500)
        b0 = [pg.evaluate(BOX), [pg.evaluate(PARTS, i) for i in range(4)], [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'Suite “Trisect”' in x]]
        print('B)', b0)
        # ((3.191.0, S338) the line is a field that must be answered: its words before it)
        results.append(b0[0] and 'tracks 2–4: parts of the suite “Trisect” – 3 works ✎ ＋ Create the suite in MusicBrainz …' in b0[0][0][1]
                       and 'suite-create' in b0[0][0][2] and b0[1][1] == ['Trisect: ' + H.TITLES[1]] and b0[1][3] == ['Trisect: ' + H.TITLES[3]]
                       and b0[1][0] and not b0[1][0][0].startswith('Trisect') and b0[2][:1] == ['Suite “Trisect” added by hand (tracks 2–4)'])
        # (3.41.15, review) tracks of that suite cannot become another one – ([Z-SU2] 3.70.0, S105) only the track 1.1 is free: the box
        # is closed and "＋ Another suite …" in the head is disabled
        b1 = pg.evaluate("""(() => { const h = document.querySelector('[data-el=works] [data-act=suite-add-open]');
          return { open: !!document.querySelector('[data-el=suite-add]'), head: h.textContent.trim(), disabled: h.disabled, title: h.title }; })()""")
        print('B2) überlappend:', b1)
        results.append(b1 == {'open': False, 'head': '＋ Another suite …', 'disabled': True,
                              'title': 'Every track is in a suite already (or alone between them): nothing to add'})
        pg.click('[data-el=works] [data-act=suite-undo]'); pg.wait_for_timeout(400)
        c0 = [pg.evaluate(BOX), pg.evaluate(PARTS, 1)]
        pg.click('[data-el=works] [data-act=suite-add-open]'); pg.wait_for_timeout(200)
        pg.click('[data-el=suite-add] [data-act=suite-add-cancel]'); pg.wait_for_timeout(200)
        c1 = pg.evaluate(BOX)
        print('C)', c0, '|', c1)
        results.append(c0[0] == a0 and c0[1] and not c0[1][0].startswith('Trisect') and c1 == a0)
        # D) ([Z-SU2] 3.70.0, S105) a suite of tracks 3–4: tracks 1–2 are free, the box opens again for another suite, from track 1.1,
        # the tracks "(Duo)" cannot be chosen, "Suites: Duo (tracks 3–4)" in the box, the name field has the focus
        pg.click('[data-el=works] [data-act=suite-add-open]'); pg.wait_for_timeout(200)
        pg.select_option('[data-el=suite-add] [data-f=mx-suite-from]', index=2)
        pg.select_option('[data-el=suite-add] [data-f=mx-suite-to]', index=3)
        pg.fill('[data-el=suite-add] [data-f=mx-suite-name]', 'Duo')
        pg.click('[data-el=suite-add] [data-act=suite-add-yes]'); pg.wait_for_timeout(500)
        d0 = pg.evaluate("""(() => { const box = document.querySelector('[data-el=suite-add]'); if (!box) return null; const f = box.querySelector('[data-f=mx-suite-from]');
          return { from: f.value, disabled: [...f.options].filter(o => o.disabled).map(o => o.textContent.trim()), list: (box.querySelector('[data-el=suite-list]') || {}).textContent,
                   focus: document.activeElement && document.activeElement.dataset.f, head: document.querySelector('[data-el=works] [data-act=suite-add-open]').textContent.trim() }; })()""")
        print('D) frei 1–2:', d0)
        results.append(d0 == {'from': '0', 'disabled': [f'1.{k} {H.TITLES[k - 1]} (Duo)' for k in (3, 4)], 'list': 'Suites: Duo (tracks 3, 4)',
                              'focus': 'mx-suite-name', 'head': '＋ Another suite …'})
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_subtracks():
    """Credits Importer 3.41.12 (collected item Z-SUB; Q-cm): an index track of Discogs whose sub-tracks are tracks of their own in
    MusicBrainz. Discogs: 1 Song One · 2 Song Two · the index "Suite X" with 3a "Song Three" (Writer Z) and 3b "Song Four" (Bass
    Man, bass) – three tracks; MusicBrainz has four.
    A) Read as four tracks (the log says so: "1 index track of Discogs: its sub-tracks are tracks of their own …"); no message that
       the tracks differ (until 3.41.11 "3 tracks instead of 4", Bass Man's bass on track 3 with Song Three).
    B) Bass Man's bass on track 4 only; Writer Z writes track 3 (the works matrix); (3.41.15, review) a credit of the release for
       "tracks: 3" (the index) on both of its tracks (until 3.41.14 not resolved: the index has no position, its sub-tracks one base).
    C) The index is offered as a suite of tracks 3–4 ("tracks 3, 4: parts of the suite “Suite X”?"; [Z-TRR] 3.93.0).
    D) In Node: titles that do not fit, but splitting gives MusicBrainz's number of tracks: split; a number that does not fit: not."""
    import json
    import subprocess
    orig = H.discogs_release

    def rel():
        d = orig()
        t3, t4 = d['tracklist'][2], d['tracklist'][3]
        t3 = dict(t3, position='3a')
        t4 = dict(t4, position='3b', extraartists=[{'name': 'Bass Man', 'anv': '', 'role': 'Bass', 'tracks': '', 'id': 3001, 'join': ''}])
        d['tracklist'] = d['tracklist'][:2] + [{'position': '', 'type_': 'index', 'title': 'Suite X', 'duration': '', 'sub_tracks': [t3, t4]}]
        d['extraartists'] = [x for x in d['extraartists'] if x.get('name') != 'Bass Man']
        # (3.41.15, review) a credit for the index's position: both of its tracks
        d['extraartists'].append({'name': 'Con Duct', 'anv': '', 'role': 'Conductor', 'tracks': '3', 'id': 3083, 'join': ''})
        return d

    H.ARTISTS[3083] = (H.uid('dddddddd', 83), 'Con Duct')
    H.discogs_release = rel
    TRACKS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => (x.querySelector('.dci-gname strong').dataset.name || x.querySelector('.dci-gname strong').textContent.trim()) === name);
      return g ? [...g.querySelectorAll('tr.dci-row')].map(tr => tr.querySelector('.dci-cline, .dci-c-tracks') ? (tr.querySelector('.dci-c-tracks') || tr).textContent.replace(/\\s+/g, ' ').trim().slice(0, 80) : '') : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, view='full')
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(800)
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'index track' in x or 'Tracks differ' in x]
        msgs = pg.evaluate("[...document.querySelectorAll('[data-el=messages] *')].map(x => x.textContent).join(' ')")
        print('A)', logs, '| Meldung:', 'tracks instead of' in msgs)
        results.append(logs == ['1 index track of Discogs: its sub-tracks are tracks of their own in MusicBrainz – read as such'] and 'tracks instead of' not in msgs)
        rows = pg.evaluate("""(() => { const out = {}; for (const g of document.querySelectorAll('section.dci-group')) { const n = (g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim());
          out[n] = [...g.querySelectorAll('tr.dci-row')].map(tr => [tr.querySelector('.dci-drole').dataset.raw.trim(), [...document.querySelectorAll(`tr[data-tracksrow="${tr.dataset.row}"] input[data-f=track]:checked`)].map(x => Number(x.dataset.i))]); } return out; })()""")
        wz = pg.evaluate("[...document.querySelectorAll('.dci-matrix tr[data-work]')].map(tr => [Number(tr.dataset.work), [...tr.querySelectorAll('td')].map(td => td.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /composer|writer/i.test(t))])")
        print('B)', rows.get('Bass Man'), '| Matrix:', wz)
        print('   Con Duct (tracks: 3):', rows.get('Con Duct'))
        results.append(rows.get('Bass Man') == [['Bass', [3]]] and wz[2][1] and 'composer' in wz[2][1][0] and wz[3][1] == []
                       and rows.get('Con Duct') == [['Conductor', [2, 3]]])
        suites = pg.evaluate("[...document.querySelectorAll('[data-el=works] [data-suite] strong')].map(x => x.textContent.trim())")
        print('C)', suites)
        results.append(suites == ['tracks 3, 4: parts of the suite “Suite X”?'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const sub = (pos, title) => ({ position: pos, type_: 'track', title, duration: '', extraartists: [] });
const d = { id: 7, title: 'X', tracklist: [sub('1', 'Opening'), { position: '', type_: 'index', title: 'Suite', sub_tracks: [sub('2a', 'Prelude'), sub('2b', 'Quartet')] }] };
const t = (xs) => xs.map((title) => ({ title }));
console.log(JSON.stringify([[...m.DISCOGS.subTrackSplit(d, t(['Alpha', 'Beta', 'Gamma']))], [...m.DISCOGS.subTrackSplit(d, t(['Alpha', 'Beta', 'Gamma', 'Delta']))],
  [...m.DISCOGS.subTrackSplit(d, t(['Opening', 'Prelude', 'Quartet']))]]));
"""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    got = json.loads(js.stdout) if not js.returncode else {'error': js.stderr[-400:]}
    print('D)', got)
    results.append(got == [[1], [], [1]])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suiterestage():
    """Credits Importer 3.41.4 (the check of Block BD), 3.41.6 (Z-SUW): a suite staged, undone and accepted again, or named anew after
    staging.
    A) "Trisect": ✓ Yes, the suite created in MusicBrainz's form, staged; ↺ undo, ✓ Yes: (3.41.6) MusicBrainz has the work "Trisect"
       by Writer W now – "Link “Trisect”" offered at the suite (not taken by itself), clicked; staged again: in the editor one link of
       the recording of track 3 to "Trisect: Phase 2" (until 3.41.3 the link staged before was kept for the new part, and the suite's
       "parts" pointed to another new work – two works on "Enter edit"); each "parts" of the suite to a new work points to a work a
       recording is linked with, and comes from the work "Trisect" of MusicBrainz.
    B) ⚙ "Suite, Part" after staging: the links with the new names are staged, those with the old names are gone; again each "parts"
       points to a work a recording is linked with."""
    H.TITLES[:] = ['Introduction', 'Phase 1', 'Phase 2 / Phase 3', 'Transition / Phase 4 / Coda']
    H.attr(1105, 'movement', 1105)
    H.lt(281, 'ca8d3642-ce5f-49f8-91f2-125d72524e6a', 'parts', 'work', 'work', (1105,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.WORK_FORM = H.WORK_FORM.replace('<option value="1">Aria</option>', '<option value="1">Aria</option><option value="6">Suite</option>')
    SUITE = H.uid('cccccccc', 96)
    WW = H.ARTISTS[3007][0]
    orig = H.discogs_release

    def rel():
        d = orig()
        d['title'] = 'Trisect'
        for t in d['tracklist'][2:]:
            t['extraartists'] = list(t.get('extraartists') or []) + [{'name': 'Writer W', 'anv': '', 'role': 'Written-By', 'tracks': '', 'id': 3007, 'join': ''}]
        return d

    H.discogs_release = rel
    CHECK = """(() => { const add = MB.relationshipEditor.state.added; const links = add.filter(r => r.linkTypeID === 278 && r._status !== 3);
      const parts = add.filter(r => r.linkTypeID === 281 && r._status !== 3);
      const linked = new Set(links.map(r => r.entity1.id));
      return { phase2: links.filter(r => /^Trisect[:,] Phase 2$/.test(r.entity1.name)).map(r => r.entity1.name), parts: parts.length,
        orphans: parts.filter(r => !r.entity1.gid && !linked.has(r.entity1.id)).map(r => r.entity1.name), suites: [...new Set(parts.map(r => r.entity0.gid))] }; })()"""

    def stage():
        H.stage_click(pg, least=3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now|^yes$|^ja$/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(500)
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "!!document.querySelector('[data-el=works] .dci-mx-suite')", 60)
        pg.wait_for_timeout(500)
        pg.click('[data-el=works] [data-act=suite-yes]'); pg.wait_for_timeout(400)
        pg.click('[data-el=works] [data-act=suite-create]')
        H.wait_for(pg, "!!document.querySelector('[data-el=sub-frame]')", 20)
        H.COMPANIES[7096] = ('work', SUITE, 'Trisect')
        H.WORK_TITLES[SUITE] = 'Trisect'
        pg.evaluate(f"document.querySelector('[data-el=sub-frame]').src = 'https://musicbrainz.org/work/{SUITE}'")
        H.wait_for(pg, "!!document.querySelector('[data-el=works] a.dci-suite-mb')", 20)
        stage()
        a1 = pg.evaluate(CHECK)['parts']
        # MusicBrainz has the suite now (by Writer W)
        H.WORK_SEARCH[:] = [{'id': SUITE, 'title': 'Trisect', 'type': 'Suite', 'aliases': [], 'relations': [{'target-type': 'artist', 'type': 'writer', 'artist': {'id': WW, 'name': 'Writer W'}}]}]
        # ([Z-WORKIDS] 3.196.0, S355) the suite created is kept for the release; cleared here, the search offers it to link
        kept = pg.evaluate("Object.keys(localStorage).filter(k => k.startsWith('dci-created-suites:')).map(k => localStorage.getItem(k)).join(' ')")
        pg.evaluate("Object.keys(localStorage).filter(k => k.startsWith('dci-created-suites:')).forEach(k => localStorage.removeItem(k))")
        pg.click('[data-el=works] [data-act=suite-undo]'); pg.wait_for_timeout(400)
        pg.click('[data-el=works] [data-act=suite-yes]')
        H.wait_for(pg, "!!document.querySelector('[data-el=works] [data-act=suite-pick]')", 20)
        a2 = [pg.evaluate("document.querySelector('[data-el=works] [data-act=suite-pick]').textContent.trim()"), pg.evaluate("!!document.querySelector('[data-el=works] a.dci-suite-mb')")]
        pg.click('[data-el=works] [data-act=suite-pick]'); pg.wait_for_timeout(400)
        a3 = pg.evaluate("(document.querySelector('[data-el=works] a.dci-suite-mb') || {}).href || null")
        stage()
        a0 = pg.evaluate(CHECK)
        print('A)', a1, a2, a3, a0)
        results.append(SUITE in kept and a1 == 7 and a2 == ['Link “Trisect”', False] and a3 and a3.endswith(SUITE)
                       and a0['phase2'] == ['Trisect: Phase 2'] and a0['parts'] == 7 and a0['orphans'] == [] and a0['suites'] == [SUITE])
        H.open_settings(pg, 'works')
        pg.click('[data-el=settings] [data-act=suite-naming][data-naming=comma]'); pg.wait_for_timeout(400)
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()'); pg.wait_for_timeout(200)
        stage()
        b0 = pg.evaluate(CHECK)
        print('B)', b0)
        results.append(b0['phase2'] == ['Trisect, Phase 2'] and b0['parts'] == 7 and b0['orphans'] == [] and b0['suites'] == [SUITE])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_wts():
    """Credits Importer 3.52.0 (collected item Z-WTS; Q-ft, Q-fu, Q-ge): a work type and a lyrics language for all new works, suggested from
    the works of the artists the works matrix reads anyway (here the release artist: 3 Song in English, 1 Aria in [No lyrics]).
    A) Yellow below the head: "New works – suggested: Song · English", "from 3 of 4 works of Test Band in MusicBrainz", "Accept", and
       "if not accepted: neither type nor language is filled in"; each track without a work has a yellow "?" at its label ([3.97.0] its
       tooltip names the suggestion – until 3.96.0 "Song · English?": not filled in until "Accept").
    B) Not accepted: the new works are staged without a type and without a language.
    C) "Accept" (another page): the line and the hints go, the log says so; the defaults (popover of the head) hold Song and English; the new
       works are staged as Song in English.
    D) In Node (suggestFromWorks): type and language each on their own, more than half of the works ("" when most have none); fewer than
       3 works, no majority or a value this page does not offer: not suggested. (review) The languages of a work together; works whose
       languages are not known (stored by 3.51.0) are not counted; codes of the page's languages count too.
    E) (review) The works of the artists stored in this browser keep their languages: a new page (works from the store) suggests the
       same."""
    import json
    import subprocess
    TB = H.uid('dddddddd', 60)
    H.RELEASE_AC[:] = [(TB, 'Test Band', 'Test Band', '')]
    H.ARTIST_WORKS.update({TB: [{'id': H.uid('cccccccc', 120 + k), 'title': f'Elsewhere {k}', 'type': t, 'languages': [lg], 'aliases': []}
                                for k, (t, lg) in enumerate([('Song', 'eng'), ('Song', 'eng'), ('Aria', 'zxx'), ('Song', 'eng')])]})
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    LINE = """(() => { const x = document.querySelector('[data-el=works] [data-el=works-suggest]'); return x ? [(x.querySelector('strong') || {}).textContent,
      x.textContent.replace(/\\s+/g, ' ').trim(), [...x.querySelectorAll('button')].map(b => b.dataset.act), getComputedStyle(x).backgroundColor] : null; })()"""
    HINTS = "[...document.querySelectorAll('.dci-matrix tr[data-work] .dci-mx-wtsrow')].map(x => [x.closest('tr').dataset.work, x.textContent.trim(), x.title])"
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 278 && !r.entity1.gid).map(r => [r.entity1.name, r.entity1.typeID,
      (r.entity1.languages || []).map(l => l.language.id)]).sort())()"""
    results = []

    def start(ctx):
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
        pg.add_style_tag(content='#dci-log { display: none !important; }')
        pg.wait_for_timeout(400)
        return pg, errs

    def stage(pg):
        pg.locator('[data-el=works] [data-act=works-pending-all]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
        H.stage_click(pg, least=3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(300)
        return pg.evaluate(STAGED)

    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = start(ctx)
        a0, a1 = pg.evaluate(LINE), pg.evaluate(HINTS)
        print('A)', a0, '\n  ', a1)
        results.append(a0 is not None and a0[0] == 'Song · English' and 'from the works of Test Band in MusicBrainz: type 3 of 4 · language 3 of 4' in a0[1] and 'mx-wts-accept' in a0[2]
                       and a0[1].endswith('if not accepted: neither type nor language is filled in') and a0[3] == 'rgb(255, 248, 219)'
                       and [x[1] for x in a1] == ['?'] * 3 and all(x[2] == 'Suggested from the works of the artists: Song · English' for x in a1))  # ([3.170.0] F-TOOLTIPLEN: one sentence)
        b0 = stage(pg)
        print('B) nicht angenommen:', b0)
        results.append(len(b0) == 3 and all(x[1] is None and x[2] == [] for x in b0))
        ctx.close()
        ctx = H.new_context(b)
        pg, errs2 = start(ctx)
        # E) a second page of this browser (before anything is staged): the works of Test Band from the store, with their languages
        pg3, errs3 = start(ctx)
        e0 = [pg3.evaluate(LINE), [x for x in pg3.evaluate(LOGS) if 'Test Band' in x][:3]]
        pg3.close()
        print('E) aus dem Speicher:', e0)
        results.append(e0[0] is not None and e0[0][0] == 'Song · English' and any('from the store' in x for x in e0[1]))
        pg.bring_to_front()
        pg.locator('[data-el=works] [data-act=mx-wts-accept]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
        pg.locator('[data-el=works] [data-act=mx-defaults]').first.evaluate('b => b.click()'); pg.wait_for_timeout(300)
        c0 = [pg.evaluate(LINE), pg.evaluate(HINTS), [x for x in pg.evaluate(LOGS) if 'suggestion taken' in x],
              pg.evaluate("(document.querySelector('[data-el=works] select[data-f=work-type]') || {}).value"),
              pg.evaluate("[...document.querySelectorAll('[data-el=works] [data-el=works-defaults] .dci-lang-chip')].map(x => x.firstChild.textContent.trim())")]
        pg.locator('[data-el=works] [data-act=mx-defaults]').first.evaluate('b => b.click()'); pg.wait_for_timeout(300)
        c1 = stage(pg)
        print('C) angenommen:', c0, '| gestaged:', c1)
        results.append(c0[0] is None and c0[1] == [] and c0[2] == ['New works: Song · English – the suggestion taken (each work can still be changed)'] and c0[3] == '17' and c0[4] == ['English']
                       and len(c1) == 3 and all(x[1] == 17 and x[2] == [120] for x in c1))
        print('Fehler:', errs, errs2, errs3)
        results.append(not errs and not errs2 and not errs3)
        b.close()
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const T = [{ id: 17, name: 'Song' }, { id: 1, name: 'Aria' }], L = [{ id: 120, name: 'English' }, { id: 486, name: '[No lyrics]' }];
const w = (type, ...l) => ({ type, languages: l.filter(Boolean) });
const f = (xs, codes) => m.suggestFromWorks(xs, T, L, codes);
console.log(JSON.stringify([f([w('', 'zxx'), w('', 'zxx'), w('', 'zxx'), w('Song', 'eng'), w('Song', 'zxx')]), f([w('Song', 'eng'), w('Song', 'eng')]),
  f([w('Song', 'eng'), w('Song', 'eng'), w('Aria', 'eng'), w('', 'eng')]), f([w('Song', 'eng'), w('Aria', 'zxx'), w('', 'deu')]),
  f([w('Opera', 'deu'), w('Opera', 'deu'), w('Opera', 'deu')]), f([w('Song', ''), w('Song', ''), w('Song', 'eng')]),
  f([{ type: 'Song' }, { type: 'Song' }, { type: 'Song' }, w('Aria', 'eng')]), f([w('Song', 'eng', 'zxx'), w('Song', 'zxx', 'eng'), w('Aria', 'eng')]),
  f([w('Song', 'isl'), w('Song', 'isl'), w('Song', 'isl')], { isl: 120 })]));
"""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    got = json.loads(js.stdout) if not js.returncode else {'error': js.stderr[-400:]}
    print('D)', got)
    # (review) several languages of a work together; a work whose languages are not known (a record of 3.51.0) not counted; a code of the
    # page's languages (linkedEntities) beyond the built-in list
    results.append(got == [{'typeId': '', 'langIds': ['486'], 'nType': 3, 'nLang': 4, 'of': 5, 'ofLang': 5}, None, {'langIds': ['120'], 'nType': 0, 'nLang': 4, 'of': 4, 'ofLang': 4},
                           None, None, {'typeId': '17', 'langIds': [], 'nType': 3, 'nLang': 2, 'of': 3, 'ofLang': 3}, {'typeId': '17', 'nType': 3, 'nLang': 0, 'of': 4, 'ofLang': 1},
                           {'typeId': '17', 'langIds': ['120', '486'], 'nType': 2, 'nLang': 2, 'of': 3, 'ofLang': 3}, {'typeId': '17', 'langIds': ['120'], 'nType': 3, 'nLang': 3, 'of': 3, 'ofLang': 3}])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_wts397():
    """Credits Importer 3.97.0 (collected item Z-WTS2; rule S153): the work type and lyrics languages of each work as a label beside it.
    Track 2 "Alpha / Beta", track 3 "Gamma (Instrumental)"; the works of Test Band suggest "Song · English" (as in wts).
    A) Beside "＋ New ▾" of each track without a work: the label "[work type · languages]" (what is filled in) with a yellow "?" (its
       tooltip names the suggestion); track 3: "[– · [No lyrics]]" with S153; the work of track 1 (MusicBrainz): "[no work type]", only
       shown.
    B) "Song" chosen in the defaults by hand: the suggestion and the "?" go (until 3.96.0 they stayed and looked like the values), the log
       says so; the labels say "[Song]", track 3 "[Song · [No lyrics]]".
    C) Track 2 split (medley): each part its own label "[Song]"; part 2 set to no type and English by its label.
    D) Staged: Alpha Song without a language, Beta without a type in English, Gamma Song in [No lyrics], track 4 Song."""
    TB = H.uid('dddddddd', 61)
    H.RELEASE_AC[:] = [(TB, 'Test Band', 'Test Band', '')]
    H.ARTIST_WORKS.update({TB: [{'id': H.uid('cccccccc', 130 + k), 'title': f'Elsewhere {k}', 'type': t, 'languages': [lg], 'aliases': []}
                                for k, (t, lg) in enumerate([('Song', 'eng'), ('Song', 'eng'), ('Aria', 'zxx'), ('Song', 'eng')])]})
    H.TITLES[1] = 'Alpha / Beta'
    H.TITLES[2] = 'Gamma (Instrumental)'
    H.attr(757, 'medley', 757)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (757,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    LABELS = """[...document.querySelectorAll('.dci-matrix tr[data-work]')].map(tr => [tr.dataset.work,
      [...tr.querySelectorAll('.dci-mx-wlabel')].map(x => x.textContent.trim() + (x.tagName === 'SPAN' ? ' (ro)' : '')),
      [...tr.querySelectorAll('.dci-mx-wtsrow')].map(x => x.textContent.trim() + ' ' + x.title),
      [...tr.querySelectorAll('.dci-ruleref')].map(x => x.textContent.trim())])"""
    LINE = "!!document.querySelector('[data-el=works] [data-el=works-suggest]')"
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 278 && !r.entity1.gid).map(r => [r.entity1.name, r.entity1.typeID,
      (r.entity1.languages || []).map(l => l.language.id)]).sort())()"""
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
        a0 = [pg.evaluate(LINE), pg.evaluate(LABELS)]
        print('A)', a0)
        rows = {x[0]: x[1:] for x in a0[1]}
        results.append(a0[0] and rows['0'][0] == ['[no work type] (ro)'] and rows['0'][1] == []
                       and rows['1'][0] == ['[work type · languages]'] and len(rows['1'][1]) == 1 and rows['1'][1][0].startswith('? ') and 'Song · English' in rows['1'][1][0]
                       and rows['2'][0] == ['[– · [No lyrics]]'] and 'S153' in rows['2'][2] and rows['3'][0] == ['[work type · languages]'])
        pg.locator('[data-el=works] [data-act=mx-defaults]').first.evaluate('b => b.click()'); pg.wait_for_timeout(300)
        pg.select_option('[data-el=works] select[data-f=work-type]', '17'); pg.wait_for_timeout(400)
        pg.locator('[data-el=works] [data-act=mx-defaults]').first.evaluate('b => b.click()'); pg.wait_for_timeout(300)
        b0 = [pg.evaluate(LINE), pg.evaluate(LABELS), [x for x in pg.evaluate(LOGS) if 'chosen by hand' in x]]
        print('B)', b0)
        rows = {x[0]: x[1:] for x in b0[1]}
        results.append(not b0[0] and rows['1'][0] == ['[Song]'] and rows['1'][1] == [] and rows['3'][0] == ['[Song]'] and rows['2'][0] == ['[Song · [No lyrics]]']
                       and b0[2] == ['New works: Song – the defaults chosen by hand (the suggestion is not used)'])
        pg.locator('.dci-matrix tr[data-work="1"] [data-act=medley-mark]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
        pg.locator('.dci-matrix tr[data-work="1"] [data-act=work-pending]').evaluate('b => b.click()'); pg.wait_for_timeout(800)
        c0 = pg.evaluate(LABELS)
        pg.locator('.dci-matrix tr[data-work="1"] .dci-mx-wlabel').nth(1).evaluate('b => b.click()'); pg.wait_for_timeout(300)
        pg.select_option('.dci-matrix tr[data-work="1"] .dci-row-opts select[data-f=mx-type]', ''); pg.wait_for_timeout(300)
        pg.select_option('.dci-matrix tr[data-work="1"] .dci-row-opts select[data-f=work-lang-add]', '120'); pg.wait_for_timeout(300)
        c1 = [x for x in pg.evaluate(LABELS) if x[0] == '1']
        print('C)', c0, '\n  ', c1)
        results.append([x[1] for x in c0 if x[0] == '1'] == [['[Song]'], ['[Song]']] and [x[1] for x in c1] == [['[Song]'], ['[– · English]']])
        pg.locator('[data-el=works] [data-act=works-pending-all]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
        H.stage_click(pg, least=3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(300)
        d0 = pg.evaluate(STAGED)
        print('D)', d0)
        results.append(d0 == [['Alpha', 17, []], ['Beta', None, [120]], ['Gamma (Instrumental)', 17, [486]], ['Song Four', 17, []]])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_snw383():
    """Credits Importer 3.83.0 (collected item Z-SNW, rule S125): "＋ New works" while track 2 ("Song Two", Writer W) has a work of the same
    title in MusicBrainz – three answers in the works matrix (until 3.82.0 a question of the browser: the others or none).
    A) The box names Song Two; "Cancel": nothing planned.
    B) "for the other tracks": tracks 3 and 4 get new works, track 2 none (it is to be linked).
    C) Taken back, "for all tracks anyway": track 2 too; staged, the edit note names the work of the same title (its link).
    D) ⚙ Settings → Staging → "Edit note": the switch off – the line is gone from the edit note.
    E) (review) "Reset" of the topic Staging: the switch on again (until the review stored as reset, shown as off), the line back.
    (review) Esc in the question closes the question, not the dashboard; the focus goes back to "＋ New works"."""
    WW = H.ARTISTS[3007][0]
    SAME = H.uid('cccccccc', 3830)
    H.WORK_SEARCH[:] = [{'id': SAME, 'title': 'Song Two', 'type': 'Song', 'aliases': [], 'relations': [{'target-type': 'artist', 'type': 'writer', 'artist': {'id': WW, 'name': 'Writer W'}}]}]
    PEND = "[...document.querySelectorAll('.dci-matrix tr[data-work]')].filter(tr => /new work/i.test((tr.querySelector('.dci-mx-line') || {}).textContent || '')).map(tr => Number(tr.dataset.work) + 1)"
    NOTE = "document.getElementById('edit-note-text').value"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 90)
        H.wait_still(pg, "document.body.innerHTML", 15, 300)
        click = lambda sel: pg.locator(sel).first.evaluate('b => b.click()')
        click('[data-el=works] [data-act=works-pending-all]')
        H.wait_for(pg, "!!document.querySelector('[data-el=works-dupask]')", 10)
        a0 = pg.evaluate("document.querySelector('[data-el=works-dupask]').textContent.replace(/\\s+/g, ' ').trim()")
        # (review) Esc: the question closed, not the dashboard; the focus on "＋ New works"
        pg.locator('[data-act=mx-dup-answer][data-answer=others]').focus()
        pg.keyboard.press('Escape')
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        esc = pg.evaluate("[!!document.querySelector('[data-el=works-dupask]'), !!document.querySelector('.dci-panel') && document.querySelector('.dci-panel').getClientRects().length > 0, (document.activeElement || {}).dataset ? document.activeElement.dataset.act : '']")
        print('A) Esc', esc)
        results.append(esc == [False, True, 'works-pending-all'])
        click('[data-el=works] [data-act=works-pending-all]')
        H.wait_for(pg, "!!document.querySelector('[data-el=works-dupask]')", 10)
        click('[data-act=mx-dup-answer][data-answer=cancel]')
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        a1 = [pg.evaluate("!!document.querySelector('[data-el=works-dupask]')"), pg.evaluate(PEND)]
        print('A)', a0, '|', a1)
        results.append('Song Two' in a0 and 'for the other tracks' in a0 and 'for all tracks anyway' in a0 and a1 == [False, []])
        click('[data-el=works] [data-act=works-pending-all]')
        H.wait_for(pg, "!!document.querySelector('[data-el=works-dupask]')", 10)
        click('[data-act=mx-dup-answer][data-answer=others]')
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        b0 = pg.evaluate(PEND)
        print('B)', b0)
        results.append(b0 == [3, 4])
        for i in (2, 3):
            un = pg.locator(f'.dci-matrix tr[data-work="{i}"] [data-act=work-unplan]')
            if un.count():
                un.first.evaluate('b => b.click()')
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
        click('[data-el=works] [data-act=works-pending-all]')
        H.wait_for(pg, "!!document.querySelector('[data-el=works-dupask]')", 10)
        click('[data-act=mx-dup-answer][data-answer=all]')
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        c0 = pg.evaluate(PEND)
        pg.click('[data-act=apply]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Staging complete/.test(li.textContent))", 30)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        H.wait_still(pg, "document.getElementById('edit-note-text').value", 10, 300)
        note = pg.evaluate(NOTE)
        line = [l for l in note.splitlines() if 'same title' in l]
        print('C)', c0, '|', line)
        results.append(c0 == [2, 3, 4] and len(line) == 1 and '“Song Two”' in line[0] and f'/work/{SAME}' in line[0])
        H.open_settings(pg, 'staging')
        d0 = pg.evaluate("!!document.querySelector('[data-el=settings] [data-el=set-editnote]')")
        pg.locator('[data-el=settings] [data-f=note-dup]').uncheck()
        H.wait_still(pg, "document.getElementById('edit-note-text').value", 10, 300)
        d1 = [l for l in pg.evaluate(NOTE).splitlines() if 'same title' in l]
        print('D)', d0, d1, pg.evaluate("localStorage.getItem('dci-note-dup')"))
        results.append(d0 and d1 == [] and pg.evaluate("localStorage.getItem('dci-note-dup')") == 'false')
        # E) (review) "Reset" of the topic: the switch on again – stored and shown (the edit note names the work again)
        click('[data-el=settings] [data-act=settings-reset][data-topic=staging]')
        H.wait_still(pg, "document.getElementById('edit-note-text').value", 10, 300)
        e0 = [pg.evaluate("localStorage.getItem('dci-note-dup')"), pg.evaluate("document.querySelector('[data-el=settings] [data-f=note-dup]').checked"),
              len([l for l in pg.evaluate(NOTE).splitlines() if 'same title' in l])]
        print('E)', e0)
        results.append(e0 == [None, True, 1])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_bwv3138():
    """Credits Importer 3.138.0 (collected item Z-BWV, rule S224): a track without a work of its title whose title has a catalogue number
    is looked up by the number among the works of its composer (Johann Sebastian Bach, composer of tracks 2–4).
    A) "Bach Adagio From The Sonata For Violin Solo In G Minor BWV1001" → the movement "… BWV 1001: I. Adagio" only (not the sonata, not
       BWV 1002), the list says "with BWV 1001"; the query "work:"bwv 1001"" with Bach's MBID.
    B) "Sonata in G minor, BWV 1001" (no movement named) → the sonata itself. C) "Fuga (BWV 1001)" → "II. Fuga".
    D) S224 off (and S333, which from 3.189.0 offers the sonata as a similar title): nothing found for them."""
    BACH = H.uid('dddddddd', 401)
    H.ARTISTS[3201] = (BACH, 'Johann Sebastian Bach')
    S1001 = H.uid('eeeeeeee', 401)
    MV = {k: H.uid('eeeeeeee', 402 + n) for n, k in enumerate(['I. Adagio', 'II. Fuga', 'III. Siciliana', 'IV. Presto'])}
    P1002 = H.uid('eeeeeeee', 410)
    comp = [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': BACH, 'name': 'Johann Sebastian Bach'}}]
    sonata = 'Sonata for Violin solo no. 1 in G minor, BWV 1001'
    works = [{'id': S1001, 'title': sonata, 'aliases': [], 'type': 'Sonata', 'relations': comp}]
    works += [{'id': g, 'title': f'{sonata}: {k}', 'aliases': [], 'type': '', 'relations': comp} for k, g in MV.items()]
    works += [{'id': P1002, 'title': 'Partita for Violin solo no. 1 in B minor, BWV 1002: I. Allemanda', 'aliases': [], 'type': '', 'relations': comp}]
    orig = H.discogs_release
    H.TITLES[:] = ['Song One', 'Bach Adagio From The Sonata For Violin Solo In G Minor BWV1001', 'Sonata in G minor, BWV 1001', 'Fuga (BWV 1001)']

    def rel():
        d = orig()
        for t, title in zip(d['tracklist'], H.TITLES):
            t['title'] = title
            t['extraartists'] = []
        d['extraartists'] = [{'name': 'Johann Sebastian Bach', 'anv': '', 'role': 'Composed By', 'tracks': '2 to 4', 'id': 3201, 'join': ''}]
        d['companies'] = []
        return d
    H.discogs_release = rel
    PICKS = """(i) => [...document.querySelectorAll(`[data-el=works] tr[data-work="${i}"] .dci-same [data-act=work-pick]`)].map(b => b.dataset.title)"""
    results = []

    def run(off):
        H.WORK_SEARCH[:] = works
        H.WORK_QUERIES[:] = []
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            if off:
                ctx.add_init_script("if (/musicbrainz/.test(location.hostname)) localStorage.setItem('dci-rules-off', JSON.stringify(['S224', 'S333']))")
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(800)
            picks = [pg.evaluate(f"({PICKS})({i})") for i in (1, 2, 3)]
            head = pg.evaluate("(document.querySelector('[data-el=works] tr[data-work=\"1\"] .dci-same strong') || {}).textContent || ''")
            log = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'found by' in x]
            b.close()
            return picks, head, log, [q for q in H.WORK_QUERIES if 'work:"bwv' in q.lower()], errs
    picks, head, log, qs, errs = run(False)
    print('A-C)', picks, '|', head, '|', log[:1], '|', qs[:1])
    results.append(picks[0] == [f'{sonata}: I. Adagio'] and 'with BWV 1001' in head and any('work:"bwv 1001"' in q and BACH in q for q in qs))
    results.append(picks[1] == [sonata])
    results.append(picks[2] == [f'{sonata}: II. Fuga'])
    results.append(not errs)
    picks2, _h, _l, qs2, errs2 = run(True)
    print('D) aus:', picks2, qs2)
    results.append(picks2 == [[], [], []] and not qs2 and not errs2)
    H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_onework3138():
    """Credits Importer 3.138.0 (collected item Z-ONEWORK, rule S225): only some works – in the head of the works matrix.
    A) "＋ New works (3)": tracks 2–4 new works. ☝ opens a list of the four tracks; track 3 picked – only its new work stays, the others
       "no work"; the log says so; ↺ appears and brings the three back.
    B) 🔗 Existing works only: the new works gone (track 1, linked, stays); ↺ back.
    C) ✍ Writing credits only: the new works of the tracks with writing credits stay, the others gone.
    D) "Symbols: Text": words instead of the symbols – short ones from 3.161.0, "All" first from 3.165.0 ("All", "Credits", "In MB", "One"; the full names
       stay the buttons' accessible names)."""
    PENDING = "[...document.querySelectorAll('[data-el=works] tr[data-work]')].filter(tr => tr.querySelector('.dci-badge-plan')).map(tr => Number(tr.dataset.work))"
    CREDITS = "[...new Set([...document.querySelectorAll('[data-el=works] tr[data-work]')].filter(tr => tr.querySelector('.dci-mxchip')).map(tr => Number(tr.dataset.work)))]"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(500)
        withCredits = pg.evaluate(CREDITS)
        pg.click('[data-el=works] [data-act=works-pending-all]')
        pg.wait_for_timeout(500)
        p0 = pg.evaluate(PENDING)
        pg.click('[data-el=works] [data-act=wone-open]')
        pg.wait_for_timeout(300)
        items = pg.locator('[data-el=works-one] [data-act=wone-pick]').count()
        pg.click('[data-el=works-one] [data-act=wone-pick][data-i="2"]')
        pg.wait_for_timeout(400)
        p1 = pg.evaluate(PENDING)
        logl = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'Works matrix – ' in x]
        undo = pg.locator('[data-el=works] [data-act=wone-undo]').count()
        pg.click('[data-el=works] [data-act=wone-undo]')
        pg.wait_for_timeout(400)
        p2 = pg.evaluate(PENDING)
        print('A)', p0, items, p1, logl[-1:], undo, p2)
        results.append(p0 == [1, 2, 3] and items == 4 and p1 == [2] and logl and 'tracks with a work 2 of 4' in logl[-1] and undo == 1 and p2 == [1, 2, 3])
        pg.click('[data-el=works] [data-act=wone-existing]')
        pg.wait_for_timeout(400)
        b1 = [pg.evaluate(PENDING), pg.evaluate("document.querySelector('[data-el=works] [data-act=wone-existing]').getAttribute('aria-pressed')"),
              pg.evaluate("!!document.querySelector('[data-el=works] tr[data-work=\"0\"] .dci-badge-ok')")]
        pg.click('[data-el=works] [data-act=wone-undo]')
        pg.wait_for_timeout(400)
        b2 = pg.evaluate(PENDING)
        print('B)', b1, b2)
        results.append(b1 == [[], 'true', True] and b2 == [1, 2, 3])
        pg.click('[data-el=works] [data-act=wone-credits]')
        pg.wait_for_timeout(400)
        c1 = pg.evaluate(PENDING)
        print('C) mit Credits:', withCredits, '→', c1)
        results.append(c1 == [i for i in [1, 2, 3] if i in withCredits] and len(c1) < 3)
        H.open_settings(pg, 'appearance')
        pg.click('.dci-set-pane [data-act=emoji-mode][data-mode=text]')
        pg.wait_for_timeout(400)
        d = pg.evaluate("[...document.querySelectorAll('[data-el=works] .dci-wone-btn')].map(b => b.textContent.trim())")
        print('D)', d)
        results.append(d == ['All', 'Credits', 'In MB', 'One'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_bwv3138r():
    """Credits Importer 3.138.0 (review of Z-BWV): the movement after ": " (not the colon of "Hob. I:104"), "No. 15" as a pair, no small words.
    A) "Symphony No. 104 in D major, Hob. I:104" (no movement named) → the symphony only, not its movements.
    B) "Prelude No. 15 in D-flat Major, Op. 28" → "24 Préludes, Op. 28: No. 15 in D-flat major “Raindrop”" only (not every prelude).
    C) "Requiem in D minor, Op. 48" → the Requiem, not "VII. In paradisum".
    D) ↺ of ✍ 🔗 ☝ takes back only what they did: a new work planned by hand afterwards on a track they dropped stays."""
    X = H.uid('dddddddd', 402)
    H.ARTISTS[3202] = (X, 'Ann Composer')
    comp = [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': X, 'name': 'Ann Composer'}}]
    titles = ['Symphony no. 104 in D major, Hob. I:104 “London”', 'Symphony no. 104 in D major, Hob. I:104 “London”: I. Adagio – Allegro',
              'Symphony no. 104 in D major, Hob. I:104 “London”: II. Andante', '24 Préludes, Op. 28', '24 Préludes, Op. 28: No. 14 in E-flat minor',
              '24 Préludes, Op. 28: No. 15 in D-flat major “Raindrop”', '24 Préludes, Op. 28: No. 16 in B-flat minor', 'Requiem in D minor, Op. 48',
              'Requiem in D minor, Op. 48: I. Introït et Kyrie', 'Requiem in D minor, Op. 48: VII. In paradisum']
    works = [{'id': H.uid('eeeeeeee', 450 + k), 'title': t, 'aliases': [], 'type': '', 'relations': comp} for k, t in enumerate(titles)]
    orig = H.discogs_release
    H.TITLES[:] = ['Song One', 'Symphony No. 104 in D major, Hob. I:104', 'Prelude No. 15 in D-flat Major, Op. 28', 'Requiem in D minor, Op. 48']

    def rel():
        d = orig()
        for t, title in zip(d['tracklist'], H.TITLES):
            t['title'] = title
            t['extraartists'] = []
        d['extraartists'] = [{'name': 'Ann Composer', 'anv': '', 'role': 'Composed By', 'tracks': '2 to 4', 'id': 3202, 'join': ''}]
        d['companies'] = []
        return d
    H.discogs_release = rel
    H.WORK_SEARCH[:] = works
    PICKS = """(i) => [...document.querySelectorAll(`[data-el=works] tr[data-work="${i}"] .dci-same [data-act=work-pick]`)].map(b => b.dataset.title)"""
    PENDING = "[...document.querySelectorAll('[data-el=works] tr[data-work]')].filter(tr => tr.querySelector('.dci-badge-plan')).map(tr => Number(tr.dataset.work))"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(800)
        picks = [pg.evaluate(f"({PICKS})({i})") for i in (1, 2, 3)]
        print('A-C)', picks)
        results.append(picks[0] == [titles[0]])
        results.append(picks[1] == [titles[5]])
        results.append(picks[2] == [titles[7]])
        # D) ☝ track 2 (all new works first, without the question of works of the same title: "all" anyway)
        pg.click('[data-el=works] [data-act=works-pending-all]')
        pg.wait_for_timeout(400)
        if pg.locator('[data-act=mx-dup-answer][data-answer=all]').count():
            pg.click('[data-act=mx-dup-answer][data-answer=all]')
            pg.wait_for_timeout(400)
        d0 = pg.evaluate(PENDING)
        pg.click('[data-el=works] [data-act=wone-open]')
        pg.wait_for_timeout(200)
        pg.click('[data-el=works-one] [data-act=wone-pick][data-i="1"]')
        pg.wait_for_timeout(400)
        d1 = pg.evaluate(PENDING)
        pg.click('[data-el=works] tr[data-work="3"] [data-act=work-pending]')
        pg.wait_for_timeout(400)
        d2 = pg.evaluate(PENDING)
        pg.click('[data-el=works] [data-act=wone-undo]')
        pg.wait_for_timeout(400)
        d3 = pg.evaluate(PENDING)
        focus = pg.evaluate("document.activeElement.dataset.act || ''")
        print('D) alle neu:', d0, '| ☝ 1.2:', d1, '| von Hand 1.4:', d2, '| ↺:', d3, '| Fokus:', focus)
        results.append(d0 == [1, 2, 3] and d1 == [1] and d2 == [1, 3] and d3 == [1, 2, 3] and focus == 'wone-open')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_magic3155():
    """Credits Importer 3.155.0 (collected item Z-WORKMAGIC, rule S284): "✨ Answer all" at the works matrix. MusicBrainz's search finds
    "Song Two" by Writer W (the writer of track 2); track 3 (Writer Z) none; track 4 no writers.
    A) Careful (the default): the preview names one answer – track 2 linked to "Song Two" (the title and all writers) –; nothing set yet.
    B) "Answer these": track 2's work planned, ✨ at its track (its tooltip the answer), a line in the log; "↺ Undo magic" there.
    C) "↺ Undo magic": the plan gone, no ✨, the log says so.
    D) ▾ Balanced (stored): the preview adds new works for tracks 3 and 4; ⓘ shows the table of the eight kinds of questions by level.
    E) ⚙ Settings → Works: "Works" switched off – the preview names nothing of works, says it is off."""
    FOUND = H.uid('cccccccc', 3155)
    WW = H.ARTISTS[3007][0]
    H.JS_WORKS[FOUND] = (7155, 'Song Two')
    H.WORK_SEARCH[:] = [{'id': FOUND, 'title': 'Song Two', 'type': 'Song', 'relations': [
        {'target-type': 'artist', 'type': 'composer', 'direction': 'backward', 'attributes': [], 'artist': {'id': WW, 'name': 'Writer W'}}]}]
    PREVIEW = """(() => { const p = document.querySelector('[data-el=magic-preview]'); return p ? { items: [...p.querySelectorAll('[data-el=magic-item]')].map(x => [x.dataset.kind, x.textContent.trim()]),
      text: p.textContent.replace(/\\s+/g, ' ').trim() } : null; })()"""
    PLAN = f"""(() => [...document.querySelectorAll('.dci-matrix tr[data-work="1"]')].map(tr => tr.textContent.includes('Song Two') && !!tr.querySelector('[data-act=work-unplan]')).some(Boolean))()"""
    MARK = "(() => { const m = document.querySelector('.dci-matrix tr[data-work=\"1\"] [data-el=magic-mark]'); return m ? m.title : null; })()"
    LOG = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9)).filter(t => t.startsWith('✨'))"
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_for(pg, f"!!document.querySelector('tr[data-work=\"1\"] [data-act=work-pick][data-gid=\"{FOUND}\"]')", 30)
            open_preview = lambda: (pg.locator('[data-act=magic-open]').evaluate('b => b.click()'), H.wait_for(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30))
            open_preview()
            a = pg.evaluate(PREVIEW)
            print('A)', a)
            results.append(bool(a) and a['items'] == [['work', '1.2 – work “Song Two” linked (the title and all writers)']] and 'Careful' in a['text'] and not pg.evaluate(PLAN))
            pg.locator('[data-act=magic-apply]').evaluate('b => b.click()')
            H.wait_for(pg, "!!document.querySelector('[data-act=magic-undo]')", 20)
            pg.wait_for_timeout(400)
            b1 = [pg.evaluate(PLAN), pg.evaluate(MARK), pg.evaluate(LOG)]
            print('B)', b1)
            results.append(b1[0] and b1[1] and 'Song Two' in b1[1] and any('Works: 1.2' in x for x in b1[2]) and any('Answer all (Careful): 1 answer' in x for x in b1[2]))
            pg.locator('[data-act=magic-undo]').evaluate('b => b.click()')
            pg.wait_for_timeout(500)
            c1 = [pg.evaluate(PLAN), pg.evaluate(MARK), pg.evaluate(LOG)[-1:], pg.evaluate("!!document.querySelector('[data-act=magic-undo]')")]
            print('C)', c1)
            results.append(not c1[0] and c1[1] is None and c1[2] == ['✨ Undo magic: 1 answer taken back'] and not c1[3])
            # D) Balanced at ▾; ⓘ
            pg.locator('[data-act=magic-menu]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            pg.locator('[data-act=magic-level][data-level=balanced]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            stored = pg.evaluate("localStorage.getItem('dci-magic-level')")
            open_preview()
            d1 = pg.evaluate(PREVIEW)
            pg.locator('[data-act=magic-info]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            info = pg.evaluate("[...document.querySelectorAll('[data-el=magic-info] tbody tr')].map(tr => tr.querySelector('th').textContent.trim())")
            cur = pg.evaluate("(document.querySelector('[data-el=magic-info] .dci-mx-magiccur') || {}).textContent || ''")
            print('D)', stored, d1, '| ⓘ:', info, cur)
            kinds = [k for k, _ in (d1 or {'items': []})['items']]
            results.append(stored == '"balanced"' and bool(d1) and kinds.count('work') == 3 and any('1.3 – new work' in t for _, t in d1['items']) and any('1.4 – new work' in t for _, t in d1['items'])
                           and info == ['Suites', 'Works', 'Medleys', 'Live', 'Cover', 'Publishers', 'Column dates', 'Dedications'] and cur == 'Balanced')
            # E) the kind "Works" switched off
            H.open_settings(pg, 'works')
            pg.locator('[data-el=settings] [data-set=magic-kind][data-kind=work]').uncheck(); pg.wait_for_timeout(300)
            off = pg.evaluate("localStorage.getItem('dci-magic-off')")
            pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            open_preview()
            e1 = pg.evaluate(PREVIEW)
            print('E)', off, e1)
            results.append(off == '["work"]' and bool(e1) and not any(k == 'work' for k, _ in e1['items']) and 'Switched off: Works' in e1['text'])
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.WORK_SEARCH[:] = []
        H.JS_WORKS.pop(FOUND, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suiteprefix3189():
    """Credits Importer 3.189.0 (collected items Z-SUITEPREFIX, Z-SUITENO; rules S330, S331). MusicBrainz's titles: "Trisect: Introduction"
    (has a work), "Trisect: Phase 1", "Trisect: Phase 2 – Coda I–II", "Other".
    A) The works matrix asks "tracks 1–3: parts of the suite “Trisect”?" – "from the titles in MusicBrainz"; the answers "✓ Yes",
       "✕ No suite", "✓ Yes, with this name".
    B) "✨ Answer all" (careful): the preview names the suite, with a tick; unticked, "Answer" counts one less; ticked again and applied:
       track 2 "Trisect: Phase 1", track 3 one part "Trisect: Phase 2 – Coda I–II" (no suite within the suite).
    C) Undone; "✕ No suite": kept for the release – after the page is loaded again the question is not asked ("no suite “Trisect”",
       "↺ ask again"); "↺": asked again, and no longer kept.
    D) In Node: a catalogue number or a medium names no suite ("105-2", "ECM 1064", "CD 2"; "BWV 1004", "Symphony 5" may), whatever
       the offer is from; a suite named as the release's own catalogue number is none either.
    E) Rule S330 off: no question from MusicBrainz's titles."""
    import json, subprocess
    old = H.TITLES[:]
    H.TITLES[:] = ['Trisect: Introduction', 'Trisect: Phase 1', 'Trisect: Phase 2 – Coda I–II', 'Other']
    ASK = """(() => { if (!document.querySelector('[data-el=works] table.dci-matrix')) return null; return [...document.querySelectorAll('[data-el=works] [data-suite]')].map(x => [
      x.querySelector('strong') ? x.querySelector('strong').textContent.trim() : x.textContent.replace(/\\s+/g, ' ').trim(), [...x.querySelectorAll('button')].map(y => y.textContent.trim()),
      x.textContent.replace(/\\s+/g, ' ').includes('from the titles in MusicBrainz')]); })()"""
    PARTS = """(i) => [...document.querySelectorAll(`.dci-matrix tr[data-work="${i}"]`)].map(tr => [(tr.querySelector('.dci-mx-part') || {textContent: ''}).textContent.trim(),
      (tr.querySelector('.dci-mx-line strong') || tr.querySelector('.dci-mx-line .dci-mblink') || {textContent: ''}).textContent.trim()])"""
    PREVIEW = """(() => { const p = document.querySelector('[data-el=magic-preview]'); return p ? { items: [...p.querySelectorAll('[data-el=magic-item]')].map(x => [x.dataset.kind, x.textContent.trim(),
      (x.querySelector('input') || {}).checked]), btn: (p.querySelector('[data-act=magic-apply]') || {}).textContent, dis: (p.querySelector('[data-act=magic-apply]') || {}).disabled } : null; })()"""
    results = []
    try:
        def start(p, off=None):
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            if off:
                pg.evaluate(f"localStorage.setItem('dci-rules-off', JSON.stringify({json.dumps(off)}))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            return b, pg, errs
        with sync_playwright() as p:
            b, pg, errs = start(p)
            a = pg.evaluate(ASK)
            print('A)', a)
            results.append(bool(a) and len(a) == 1 and a[0][0] == 'tracks 1–3: parts of the suite “Trisect”?' and a[0][1] == ['✓ Yes', '✕ No suite', '✓ Yes, with this name'] and a[0][2])
            pg.locator('[data-act=magic-open]').evaluate('b => b.click()'); H.wait_for(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
            p0 = pg.evaluate(PREVIEW)
            pg.locator('[data-el=magic-item][data-kind=suite] input[type=checkbox]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            p1 = pg.evaluate(PREVIEW)
            pg.locator('[data-el=magic-item][data-kind=suite] input[type=checkbox]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            p2 = pg.evaluate(PREVIEW)
            pg.locator('[data-act=magic-apply]').evaluate('b => b.click()')
            H.wait_for(pg, "!!document.querySelector('[data-act=magic-undo]')", 20)
            pg.wait_for_timeout(400)
            parts = [pg.evaluate(PARTS, i) for i in range(4)]
            print('B)', p0, '\n  ', p1, '\n  ', p2, '\n  ', parts)
            su = lambda q: [x for x in q['items'] if x[0] == 'suite']
            n = lambda q: int(''.join(c for c in q['btn'] if c.isdigit()) or 0)
            results.append(bool(p0) and len(su(p0)) == 1 and 'suite “Trisect”' in su(p0)[0][1] and su(p0)[0][2] is True and su(p1)[0][2] is False and n(p1) == n(p0) - 1
                           and n(p2) == n(p0) and parts[1] == [['', 'Trisect: Phase 1']] and parts[2] == [['', 'Trisect: Phase 2 – Coda I–II']] and not any('Trisect' in x[1] for x in parts[3]))
            pg.locator('[data-act=magic-undo]').evaluate('b => b.click()'); pg.wait_for_timeout(500)
            pg.click('[data-el=works] [data-act=suite-no]'); pg.wait_for_timeout(400)
            st = pg.evaluate("localStorage.getItem('dci-suite-no')")
            pg.reload(); pg.add_script_tag(content=H.MAIN)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            c0 = pg.evaluate(ASK)
            pg.click('[data-el=works] [data-act=suite-undo]'); pg.wait_for_timeout(400)
            c1 = [pg.evaluate(ASK), pg.evaluate("localStorage.getItem('dci-suite-no')")]
            print('C)', st, c0, c1)
            results.append(bool(st) and 'prefix|Trisect|0,1,2' in st and bool(c0) and 'no suite “Trisect”' in c0[0][0] and len(c0[0][1]) == 1
                           and c1[0][0][0] == 'tracks 1–3: parts of the suite “Trisect”?' and c1[1] is None and not errs)
            b.close()
        node = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const tr4 = [{ title: 'a' }, { title: 'b' }, { title: 'c' }, { title: 'd' }];
console.log(JSON.stringify([['105-2', 'ECM 1064', 'CD 2', 'Side B', 'BWV 1004', 'Symphony 5'].map((x) => m.headingKind(x)),
  m.suiteOffers({ title: 'X', tracks: tr4, headings: [{ at: 0, title: '105-2' }, { at: 2, title: 'Real Suite' }], companies: [] }).map((o) => o.name),
  m.suiteOffers({ title: 'X', tracks: tr4, headings: [{ at: 0, title: 'Real Suite' }], companies: [{ catno: 'Real Suite' }] }).map((o) => o.name),
  m.suiteOffers({ title: 'X', tracks: tr4.map((t, i) => ({ ...t, work: i < 2 ? 'CD 2' : 'Suite Two' })), headings: [], companies: [] }).map((o) => o.name)]));
"""
        o = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
        res = json.loads(o.stdout) if o.returncode == 0 else o.stderr[-300:]
        print('D)', res)
        results.append(res == [['catno', 'catno', 'medium', 'medium', 'name', 'name'], ['Real Suite'], [], ['Suite Two']])
        with sync_playwright() as p:
            b, pg, errs = start(p, off=['S330'])
            e = pg.evaluate(ASK)
            print('E)', e)
            results.append(e == [])
            b.close()
    finally:
        H.TITLES[:] = old
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_rowcolor3189():
    """Credits Importer 3.189.0 (collected item Z-WORKROWCOLOR, rule S332): the rows of the works matrix by the state of their work.
    A) Track 1 (its work is in MusicBrainz): "linked", a green stripe; tracks 2–4 without a work: "none", no stripe, no tint.
    B) Track 2's work chosen from the search: "found" – turquoise; track 3 "＋ New": "new" – amber; the three stripes differ, each row
       has its tint over the cells, the words "found, will be linked" and "new work" stay.
    C) ⚙ Settings → Appearance: the tick off (stored) – no stripes, no tint; on again; the colour for "new work" changed (stored): the
       stripe of track 3 has it.
    D) Rule S332 off: no colours, no setting.
    E) (3.191.0, Z-WORKROWDARK) In the light and in the dark theme: the texts of each coloured row on its tinted ground at least
       4.5 : 1, its stripe against the ground at least 3 : 1."""
    import json
    FOUND = H.uid('cccccccc', 3189)
    WW = H.ARTISTS[3007][0]
    H.JS_WORKS[FOUND] = (7189, 'Song Two')
    H.WORK_SEARCH[:] = [{'id': FOUND, 'title': 'Song Two', 'type': 'Song', 'relations': [
        {'target-type': 'artist', 'type': 'composer', 'direction': 'backward', 'attributes': [], 'artist': {'id': WW, 'name': 'Writer W'}}]}]
    ROWS = """(() => [...document.querySelectorAll('.dci-matrix tr[data-work]')].map(tr => { const f = tr.querySelector('.dci-mx-front'); const cs = getComputedStyle(f);
      return [tr.dataset.work, tr.dataset.wstate, cs.boxShadow === 'none' ? '' : (cs.boxShadow.match(/rgba?\\([^)]*\\)/) || [''])[0], cs.backgroundImage !== 'none',
        (tr.querySelector('.dci-badge') || {textContent: ''}).textContent.trim()]; }))()"""
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_for(pg, f"!!document.querySelector('tr[data-work=\"1\"] [data-act=work-pick][data-gid=\"{FOUND}\"]')", 30)
            a = pg.evaluate(ROWS)
            print('A)', a)
            results.append(len(a) == 4 and a[0][1] == 'linked' and a[0][2] and a[0][3] and all(x[1] == 'none' and not x[2] and not x[3] for x in a[1:]))
            pg.locator(f'tr[data-work="1"] [data-act=work-pick][data-gid="{FOUND}"]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
            pg.locator('tr[data-work="2"] [data-act=work-pending]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
            b1 = pg.evaluate(ROWS)
            print('B)', b1)
            results.append(b1[1][1] == 'found' and b1[2][1] == 'new' and len({b1[0][2], b1[1][2], b1[2][2]}) == 3 and all(x[3] for x in b1[:3])
                           and b1[1][4] == 'found, will be linked' and b1[2][4] == 'new work' and b1[3][1] == 'none')
            H.open_settings(pg, 'appearance')
            pg.locator('[data-el=settings] [data-set=workrow-colors]').uncheck(); pg.wait_for_timeout(300)
            c0 = [pg.evaluate("localStorage.getItem('dci-workrow-colors')"), pg.evaluate(ROWS)]
            pg.locator('[data-el=settings] [data-set=workrow-colors]').check(); pg.wait_for_timeout(300)
            pg.locator('[data-el=settings] [data-set=workrow-color][data-state=new]').evaluate("el => { el.value = '#aa00aa'; el.dispatchEvent(new Event('change', { bubbles: true })); }")
            pg.wait_for_timeout(300)
            c1 = [pg.evaluate("localStorage.getItem('dci-workrow-colors')"), pg.evaluate("localStorage.getItem('dci-workrow-palette')"), pg.evaluate(ROWS)]
            print('C)', c0, '\n  ', c1)
            results.append(c0[0] == 'false' and all(not x[2] and not x[3] for x in c0[1]) and c1[0] is None and c1[1] == '{"new":"#aa00aa"}' and c1[2][2][2] == 'rgb(170, 0, 170)'
                           and c1[2][1][2] == b1[1][2] and not errs)
            b.close()
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S332']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1000)
            d0 = pg.evaluate(ROWS)
            H.open_settings(pg, 'appearance')
            d1 = pg.evaluate("!!document.querySelector('[data-el=settings] [data-set=workrow-colors]')")
            print('D)', d0, d1)
            results.append(all(not x[2] and not x[3] for x in d0) and not d1)
            b.close()
        # E) [Z-WORKROWDARK] (3.191.0) light and dark: the text of each coloured row on its tinted ground at least 4.5 : 1 (the title and
        # the small grey text), the stripe against the ground at least 3 : 1
        CON = """(() => { const rgb = (s) => (s.match(/[\\d.]+/g) || []).map(Number); const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
            return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); }; const con = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
          const ground = (el) => { let e = el; while (e) { const c = rgb(getComputedStyle(e).backgroundColor); if (c.length === 3 || (c.length === 4 && c[3] === 1)) return c.slice(0, 3); e = e.parentElement; } return [255, 255, 255]; };
          return [...document.querySelectorAll('.dci-matrix tr[data-work]')].filter(tr => tr.dataset.wstate !== 'none').map(tr => { const f = tr.querySelector('.dci-mx-front'); const cs = getComputedStyle(f);
            const g = ground(f); const t = rgb((cs.backgroundImage.match(/rgba?\\([^)]*\\)/) || [''])[0]); const al = t.length === 4 ? t[3] : 0;
            const bg = g.map((v, k) => v * (1 - al) + (t[k] || 0) * al); const stripe = rgb((cs.boxShadow.match(/rgba?\\([^)]*\\)/) || [''])[0]).slice(0, 3);
            const texts = [...f.querySelectorAll('strong, a, .dci-sub, .dci-badge, span')].filter(e => e.getClientRects().length && e.textContent.trim() && !e.children.length).map(e => { const c = getComputedStyle(e);
              const own = rgb(c.backgroundColor); const on = own.length === 3 || (own.length === 4 && own[3] > 0.5) ? own.slice(0, 3) : bg; return con(rgb(c.color).slice(0, 3), on); });
            return [tr.dataset.wstate, Math.round(Math.min(...texts, 99) * 100) / 100, Math.round(con(stripe, bg) * 100) / 100]; }); })()"""
        for theme in ('light', 'dark'):
            with sync_playwright() as p:
                b = p.chromium.launch(args=H.LAUNCH_ARGS)
                ctx = H.new_context(b)
                ctx.add_init_script("if (location.host === 'musicbrainz.org') { localStorage.setItem('dci-theme-window', JSON.stringify('%s')); }" % theme)
                pg, errs = H.open_mb_edit(ctx, companion=False)
                pg.on('dialog', lambda d: d.accept())
                pg.wait_for_selector('#dci-open', timeout=20000)
                H.open_dashboard(pg)
                H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
                H.wait_for(pg, f"!!document.querySelector('tr[data-work=\"1\"] [data-act=work-pick][data-gid=\"{FOUND}\"]')", 30)
                pg.locator(f'tr[data-work="1"] [data-act=work-pick][data-gid="{FOUND}"]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
                pg.locator('tr[data-work="2"] [data-act=work-pending]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
                e0 = pg.evaluate(CON)
                print('E)', theme, e0)
                results.append(len(e0) == 3 and all(x[1] >= 4.5 and x[2] >= 3 for x in e0) and not errs)
                b.close()
    finally:
        H.WORK_SEARCH[:] = []
        H.JS_WORKS.pop(FOUND, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_workfind3189():
    """Credits Importer 3.189.0 (collected item Z-WORKFIND, rule S333): classical titles compared by what names the work.
    Heinrich Biber composed tracks 2 and 3, Johann Sebastian Bach track 4.
    A) "Passacaglia in G minor": no work of that title; offered in yellow "Passacaglia for Violin solo in G minor, C 105" ("similar
       title – check"), the list says "similar title"; the search asked for the kind of work in several languages; the log names it.
    B) "Sonata No. 3": "Sonate Nr. 3 F-Dur" (not "Sonate Nr. 4 D-Dur").
    C) "Chaconne From the D Minor Partita, BWV1004": the movement "… BWV 1004: V. Ciaccona" (by the catalogue number; no yellow).
    D) "✨ Answer all" (balanced): neither links the similar works nor plans new works for tracks 2 and 3.
    E) Rule S333 off: nothing for tracks 2 and 3; track 4 the partita itself (as until 3.188.0).
    F) (3.191.0, Z-WORKFINDHEAD, S340) The source credits no composer for tracks 2 and 3; MusicBrainz credits track 2 to Biber, its
       recording to who plays: his Passacaglia is offered all the same."""
    BIBER, BACH = H.uid('dddddddd', 511), H.uid('dddddddd', 512)
    H.ARTISTS[3211] = (BIBER, 'Heinrich Ignaz Franz von Biber')
    H.ARTISTS[3212] = (BACH, 'Johann Sebastian Bach')
    cb = [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': BIBER, 'name': 'Heinrich Ignaz Franz von Biber'}}]
    cj = [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': BACH, 'name': 'Johann Sebastian Bach'}}]
    partita = 'Partita for Violin solo no. 2 in D minor, BWV 1004'
    PASS = 'Passacaglia for Violin solo in G minor, C 105'
    names = [(PASS, cb), ('Sonate Nr. 3 F-Dur', cb), ('Sonate Nr. 4 D-Dur', cb), (partita, cj), (f'{partita}: I. Allemanda', cj), (f'{partita}: V. Ciaccona', cj)]
    works = [{'id': H.uid('eeeeeeee', 520 + n), 'title': ti, 'aliases': [], 'type': '', 'relations': rel} for n, (ti, rel) in enumerate(names)]
    orig = H.discogs_release
    old = H.TITLES[:]
    H.TITLES[:] = ['Song One', 'Passacaglia in G minor', 'Sonata No. 3', 'Chaconne From the D Minor Partita, BWV1004']
    state = {'nobiber': False}

    def rel():
        d = orig()
        for tk, title in zip(d['tracklist'], H.TITLES):
            tk['title'] = title
            tk['extraartists'] = []
        d['extraartists'] = ([] if state['nobiber'] else [{'name': 'Heinrich Ignaz Franz von Biber', 'anv': '', 'role': 'Composed By', 'tracks': '2 to 3', 'id': 3211, 'join': ''}]) + [
                             {'name': 'Johann Sebastian Bach', 'anv': '', 'role': 'Composed By', 'tracks': '4', 'id': 3212, 'join': ''}]
        d['companies'] = []
        return d
    H.discogs_release = rel
    PICKS = """(i) => [...document.querySelectorAll(`[data-el=works] tr[data-work="${i}"] .dci-same li`)].map(li => [li.querySelector('[data-act=work-pick]').dataset.title, !!li.querySelector('[data-el=work-loose]'), li.classList.contains('dci-mx-wloose')])"""
    results = []

    def run(off):
        H.WORK_SEARCH[:] = works
        H.WORK_QUERIES[:] = []
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            ctx.add_init_script("if (/musicbrainz/.test(location.hostname)) { localStorage.setItem('dci-magic-level', '\"balanced\"');" + (" localStorage.setItem('dci-rules-off', JSON.stringify(['S333']));" if off else '') + " }")
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(800)
            picks = [pg.evaluate(f"({PICKS})({i})") for i in (1, 2, 3)]
            head = pg.evaluate("(document.querySelector('[data-el=works] tr[data-work=\"1\"] .dci-same strong') || {}).textContent || ''")
            btn = pg.evaluate("!!document.querySelector('[data-el=works] tr[data-work=\"1\"] .dci-mx-wloosebtn')")
            log = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'similar by kind' in x]
            pg.locator('[data-act=magic-open]').evaluate('b => b.click()'); H.wait_for(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
            magic = pg.evaluate("[...document.querySelectorAll('[data-el=magic-preview] [data-el=magic-item]')].map(x => [x.dataset.kind, x.textContent.trim().slice(0, 30)])")
            b.close()
            return picks, head, btn, log, magic, [q for q in H.WORK_QUERIES if 'passacaille' in q.lower()], errs
    try:
        picks, head, btn, log, magic, qs, errs = run(False)
        print('A)', picks[0], '|', head, btn, '|', log[:1], '|', qs[:1])
        results.append(picks[0] == [[PASS, True, True]] and 'similar title' in head and btn and any('1.2' in x and PASS in x for x in log) and any(BIBER in q for q in qs))
        print('B)', picks[1], '\nC)', picks[2])
        results.append(picks[1] == [['Sonate Nr. 3 F-Dur', True, True]])
        results.append(picks[2] == [[f'{partita}: V. Ciaccona', False, False]])
        print('D)', magic)
        results.append(not any(k == 'work' and (x.startswith('1.2') or x.startswith('1.3')) for k, x in magic) and not errs)
        picks2, _h, btn2, _l, _m, qs2, errs2 = run(True)
        print('E) aus:', picks2, qs2)
        results.append(picks2[0] == [] and picks2[1] == [] and picks2[2] == [[partita, False, False]] and not qs2 and not errs2)
        # F) [Z-WORKFINDHEAD] (3.191.0, S340) no composer credited by the source for tracks 2 and 3; MusicBrainz credits track 2 to Biber
        # and its recording to who plays (classical crediting): his Passacaglia is offered all the same; track 3 (no such credit) nothing
        state['nobiber'] = True
        H.TRACK_AC[1] = [(BIBER, 'Heinrich Ignaz Franz von Biber')]
        H.REC_AC[1] = [(H.ARTISTS[3007][0], 'Writer W')]
        picks3, _h3, _b3, _l3, _m3, qs3, errs3 = run(False)
        print('F)', picks3[0], picks3[1], qs3[:1])
        results.append(picks3[0] == [[PASS, True, True]] and picks3[1] == [] and any(BIBER in q for q in qs3) and not errs3)
    finally:
        H.TRACK_AC.pop(1, None); H.REC_AC.pop(1, None)
        H.discogs_release = orig
        H.TITLES[:] = old
        H.WORK_SEARCH[:] = []
        H.ARTISTS.pop(3211, None); H.ARTISTS.pop(3212, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suitegate3191():
    """Credits Importer 3.191.0 (collected items Z-SUITEPROMPT, Z-DEDSUITE, Z-DEDMUST, Z-SUITENAMEDASH; rules S336–S338). MusicBrainz's
    titles: "Trisect For Cecil Taylor: Introduction" (has a work), "…: Phase 1", "…: Phase 2", "Other"; MusicBrainz has one artist
    Cecil Taylor.
    A) The titles "… For Cecil Taylor: …" give one row "dedicated to" on the works of tracks 1–3 (one column of the works matrix, on
       these three tracks); the entry has no question that must be answered (no instrument asked for "For").
    B) "✨ Answer all": the suite; its line is a yellow field that must be answered – "＋ Create …", "✕ No suite", "↺".
    C) "Stage": nothing is staged – the form of the suite opens, prefilled with the name, the type Suite and "dedicated to" Cecil
       Taylor. The form closed: nothing staged, a message says why.
    D) "Stage" again, the suite created in the form: staging goes on by itself – the parts are staged, the suite is linked.
    E) In Node: "-", "–", "***" are no heading of a suite; the index track below such a line names it.
    F) "✕ No suite" at the field: the parts are plain works, "Stage" stages without a form. Rule S338 off: staged at once."""
    import json, subprocess, urllib.parse
    CT = H.uid('dddddddd', 3800)
    SUITE = H.uid('cccccccc', 191)
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 846: ('26131498-00e8-4136-b937-22a4be01a63d', 'dedication', 'artist', 'work')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.ARTISTS[3800] = (CT, 'Cecil Taylor')
    old = H.TITLES[:]
    NAME = 'Trisect For Cecil Taylor'
    H.TITLES[:] = [f'{NAME}: Introduction', f'{NAME}: Phase 1', f'{NAME}: Phase 2', 'Other']
    LINE = """(() => [...document.querySelectorAll('[data-el=works] [data-suite]')].map(x => [x.className, x.textContent.replace(/\\s+/g, ' ').trim().slice(0, 90),
      [...x.querySelectorAll('button')].map(y => y.dataset.act), !!x.querySelector('a.dci-suite-mb')]))()"""
    ADDED = "MB.relationshipEditor.state.added.length"
    DED = """(() => { const h = [...document.querySelectorAll('.dci-matrix [data-colhead]')].find(x => /Cecil Taylor/.test(x.textContent)); const g = [...document.querySelectorAll('section.dci-group')].find(x => /Cecil Taylor/.test(x.querySelector('.dci-gname strong').textContent));
      return { cols: [...document.querySelectorAll('.dci-matrix [data-colhead]')].filter(x => /Cecil Taylor/.test(x.textContent)).length,
        tracks: h ? [...new Set([...document.querySelectorAll(`.dci-matrix td.dci-mx-cell.dci-mx-on[data-col="${h.dataset.colhead}"]`)].map(td => Number(td.dataset.mrow.split(':')[1]) + 1))] : [],
        must: g ? g.querySelectorAll('.dci-yell-must').length : -1, guess: g ? /is no instrument/.test(g.textContent) : null }; })()"""
    results = []

    def start(p, off=None):
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        if off:
            pg.evaluate(f"localStorage.setItem('dci-rules-off', JSON.stringify({json.dumps(off)}))")
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(2500)
        return b, pg, errs

    def magic(pg):
        pg.locator('[data-act=magic-open]').evaluate('b => b.click()'); H.wait_for(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
        pg.locator('[data-act=magic-apply]').evaluate('b => b.click()'); H.wait_for(pg, "!!document.querySelector('[data-act=magic-undo]')", 20)
        pg.wait_for_timeout(1200)
    try:
        with sync_playwright() as p:
            b, pg, errs = start(p)
            a = pg.evaluate(DED)
            print('A)', a)
            results.append(a['cols'] == 1 and sorted(a['tracks']) == [1, 2, 3] and a['must'] == 0 and a['guess'] is False)
            magic(pg)
            b0 = pg.evaluate(LINE)
            print('B)', b0)
            results.append(len(b0) == 1 and 'dci-mx-suite-must' in b0[0][0] and 'is not in MusicBrainz yet' in b0[0][1] and b0[0][2] == ['suite-rename', 'suite-create', 'suite-naming1', 'suite-drop', 'suite-undo'])  # ([Z-SUITENAMES] 3.197.0)
            n0 = pg.evaluate(ADDED)
            pg.click('[data-act=apply]')
            H.wait_for(pg, "!!document.querySelector('[data-el=sub-frame]') && /work\\/create/.test(document.querySelector('[data-el=sub-frame]').src)", 20)
            q = urllib.parse.parse_qs(urllib.parse.urlparse(pg.evaluate("document.querySelector('[data-el=sub-frame]').src")).query)
            rels = [(q.get(f'rels.{k}.target', [''])[0], q.get(f'rels.{k}.type', [''])[0]) for k in range(6) if f'rels.{k}.target' in q]
            pg.click('[data-act=sub-close]'); pg.wait_for_timeout(600)
            msg = pg.evaluate("[...document.querySelectorAll('.dci-msg, [data-el=messages] *')].map(x => x.textContent).join(' ')")
            c0 = [q.get('edit-work.name'), q.get('edit-work.type_id'), rels, pg.evaluate(ADDED) - n0, 'Nothing staged' in msg]
            print('C)', c0)
            results.append(c0[0] == [NAME] and c0[1] == ['6'] and (CT, '846') in rels and c0[3] == 0 and c0[4])
            pg.click('[data-act=apply]')
            H.wait_for(pg, "!!document.querySelector('[data-el=sub-frame]') && /work\\/create/.test(document.querySelector('[data-el=sub-frame]').src)", 20)
            H.COMPANIES[7191] = ('work', SUITE, NAME)
            H.WORK_TITLES[SUITE] = NAME
            pg.evaluate(f"document.querySelector('[data-el=sub-frame]').src = 'https://musicbrainz.org/work/{SUITE}'")
            H.wait_for(pg, "!!document.querySelector('[data-el=works] a.dci-suite-mb')", 20)
            H.wait_for(pg, f"{ADDED} > {n0}", 30)
            pg.wait_for_timeout(1500)
            d0 = [pg.evaluate(ADDED) - n0, pg.evaluate(LINE), pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity1 && /^Trisect For Cecil Taylor: Phase/.test(r.entity1.name || '')).length")]
            print('D)', d0, errs)
            results.append(d0[0] > 0 and d0[1][0][3] and 'dci-mx-suite-must' not in d0[1][0][0] and d0[2] >= 2 and not errs)
            b.close()
        node = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const tr4 = [0, 1, 2, 3].map((i) => ({ title: 't' + i, work: i < 3 ? 'Odes For X' : '' }));
console.log(JSON.stringify([['-', '–', '***', '…', '- A -', 'A'].map((x) => m.headingKind(x)),
  m.suiteOffers({ title: 'R', tracks: tr4, headings: [{ at: 0, title: '-' }], companies: [] }).map((o) => [o.name, o.from, o.tracks])]));
"""
        o = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
        res = json.loads(o.stdout) if o.returncode == 0 else o.stderr[-300:]
        print('E)', res)
        results.append(res == [['none', 'none', 'none', 'none', 'name', 'name'], [['Odes For X', 'index', [0, 1, 2]]]])
        with sync_playwright() as p:
            b, pg, errs = start(p)
            magic(pg)
            n0 = pg.evaluate(ADDED)
            pg.click('[data-el=works] [data-act=suite-drop]'); pg.wait_for_timeout(500)
            f0 = pg.evaluate(LINE)
            H.stage_click(pg, least=3000)
            f1 = [pg.evaluate(ADDED) - n0, pg.evaluate("(f => !!f && /type_id=6/.test(f.src))(document.querySelector('[data-el=sub-frame]'))")]
            b.close()
            b, pg, errs2 = start(p, off=['S338'])
            magic(pg)
            n1 = pg.evaluate(ADDED)
            H.stage_click(pg, least=3000)
            f2 = [pg.evaluate(ADDED) - n1, pg.evaluate("(f => !!f && /type_id=6/.test(f.src))(document.querySelector('[data-el=sub-frame]'))")]
            print('F)', f0, f1, f2)
            results.append('no suite' in f0[0][1] and f1[0] > 0 and not f1[1] and f2[0] > 0 and not f2[1] and not errs and not errs2)
            b.close()
    finally:
        H.TITLES[:] = old
        for i in added_lts:
            H.LTS.pop(i, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
        H.ARTISTS.pop(3800, None)
        H.COMPANIES.pop(7191, None)
        H.WORK_TITLES.pop(SUITE, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_head3161():
    """Credits Importer 3.161.0 (collected items Z-WHBTNROUND, Z-MAGICBTN, Z-WONEEMO): the head of the works matrix.
    A) "＋ New works" and "✨ Answer all" have round corners; "Answer all" is the larger one, white on a gradient from purple to orange
       (its text at least 4.5 : 1 on both ends), its ▾ the round end beside it.
    B) The three "works to keep" are emojis – ✍️ 🔗 👆 – (from 3.165.0 with their word, after "All"), each with its tooltip and its name for
       screen readers.
    C) ⚙ Settings → Appearance → Symbols: Text – the words "Credits", "In MB", "One", the tooltips the same."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(600)
        INFO = """(() => { const w = document.querySelector('#dci-overlay [data-el=works]'); const cs = (e) => getComputedStyle(e);
          const lum = (c) => { const [r, g, b] = c.match(/\\d+/g).map(Number).map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
          const ratio = (a, b) => { const x = lum(a), y = lum(b); return Math.round((Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05) * 100) / 100; };
          const nw = w.querySelector('[data-act=works-pending-all]'); const mg = w.querySelector('[data-act=magic-open]'); const lv = w.querySelector('[data-act=magic-menu]');
          const stops = (cs(mg).backgroundImage.match(/rgb\\([^)]*\\)/g) || []);
          return { nwRadius: parseFloat(cs(nw).borderTopLeftRadius), mgRadius: [parseFloat(cs(mg).borderTopLeftRadius), parseFloat(cs(mg).borderTopRightRadius)], lvRadius: [parseFloat(cs(lv).borderTopLeftRadius), parseFloat(cs(lv).borderTopRightRadius)],
            sizes: [parseFloat(cs(nw).fontSize), parseFloat(cs(mg).fontSize)], heights: [nw.offsetHeight, mg.offsetHeight], color: cs(mg).color, stops,
            contrast: stops.map(s => ratio('rgb(255, 255, 255)', s)),
            wone: [...w.querySelectorAll('.dci-wone-btn')].slice(1, 4).map(x => [x.textContent.trim(), !!x.title, x.getAttribute('aria-label')]) }; })()"""
        a = pg.evaluate(INFO)
        print('A)', {k: v for k, v in a.items() if k != 'wone'})
        results.append(a['nwRadius'] >= 10 and a['mgRadius'][0] >= 10 and a['mgRadius'][1] == 0 and a['lvRadius'] == [0, a['lvRadius'][1]] and a['lvRadius'][1] >= 10
                       and a['sizes'][1] > a['sizes'][0] and a['heights'][1] >= a['heights'][0] and a['color'] == 'rgb(255, 255, 255)' and len(a['stops']) >= 2 and min(a['contrast']) >= 4.5)
        print('B)', a['wone'])
        results.append([x[0] for x in a['wone']] == ['✍️ Credits', '🔗 In MB', '👆 One'] and all(x[1] for x in a['wone'])
                       and [x[2] for x in a['wone']] == ['Writing credits only', 'Existing works only', 'Only one …'])
        pg.evaluate("localStorage.setItem('dci-emoji-text', JSON.stringify(true))")
        pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(600)
        c = pg.evaluate(INFO)
        print('C)', c['wone'])
        results.append([x[0] for x in c['wone']] == ['Credits', 'In MB', 'One'] and all(x[1] for x in c['wone']))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_compact3165():
    """Credits Importer 3.165.0 (proposals W-HEADSLIM, W-COLHEAD, W-CELL): the works matrix compact by default.
    A) The head: "＋ New works", "Answer all" and ⋯ on the right – the defaults of new works and "Search works" are under ⋯; "Skip works" is a
       quiet link (no orange ground); the choice "Keep" – All (pressed) · Credits · In MB · One; a legend of four looks below the head.
    B) A column's head: its name and its roles – "credited as" and "all works" are in its menu ▾, not in the head; the corner has no
       "MusicBrainz names for all" (it is under ⋯).
    C) ⋯ → "Everything in the open": all of it back in the heads, stored; ⋯ → "Compact heads": compact again, the storage empty.
    D) The ▾ of a filled cell shows only under the pointer or with the focus."""
    H.MX_HEADS = None
    results = []
    INFO = """(() => { const w = document.querySelector('[data-el=works]'); const vis = (e) => !!e && e.getBoundingClientRect().width > 0;
      const r = w.querySelector('.dci-wh-r'); const head = w.querySelector('th[data-colhead]:not(.dci-mx-locked) .dci-mx-card');
      const skip = w.querySelector('.dci-wh-skip'); const keep = [...w.querySelectorAll('.dci-wone-btn')];
      return { right: [...r.querySelectorAll('button')].map(b => b.dataset.act), skipBg: getComputedStyle(skip).backgroundColor,
        keep: [(w.querySelector('.dci-wone-label') || {}).textContent, keep.map(b => [b.textContent.trim(), b.getAttribute('aria-pressed'), b.disabled])],
        legend: [...w.querySelectorAll('[data-el=works-legend] .dci-mx-legenditem')].map(x => x.textContent.trim().replace(/\\s+/g, ' ')),
        headCredit: vis(head.querySelector('[data-f=mx-credit]')), headAll: vis(head.querySelector('[data-act=mx-col-allworks]')),
        corner: vis(w.querySelector('thead [data-act=mx-clear-credits]')), stored: localStorage.getItem('dci-mx-heads') }; })()"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_selector('[data-el=works] th[data-colhead]', timeout=20000)
        pg.wait_for_timeout(600)
        a = pg.evaluate(INFO)
        print('A)', a['right'], a['skipBg'], a['keep'], a['legend'])
        results.append('mx-defaults' not in a['right'] and 'works-search-all' not in a['right'] and 'works-pending-all' in a['right'] and 'magic-open' in a['right']
                       and a['right'][-1] == 'mx-more' and a['skipBg'] == 'rgba(0, 0, 0, 0)'
                       and a['keep'][0] == 'Keep' and a['keep'][1][0] == ['All', 'true', True] and [x[0] for x in a['keep'][1][1:]] == ['✍️ Credits', '🔗 In MB', '👆 One']
                       and a['legend'] == ['role will be entered', 'role already in MusicBrainz', 'role a suggestion', 'role waits for a work'])
        pg.click('[data-el=works] [data-act=mx-more]')
        pg.wait_for_selector('[data-el=works-more] [data-act=mx-defaults]', timeout=5000)
        more = pg.evaluate("[...document.querySelectorAll('[data-el=works-more] button')].map(b => b.dataset.act)")
        print('A) ⋯:', more)
        results.append(all(x in more for x in ['mx-defaults', 'works-search-all', 'mx-clear-credits', 'mx-heads']))
        print('B)', a['headCredit'], a['headAll'], a['corner'])
        pg.keyboard.press('Escape')
        pg.locator('[data-el=works] th[data-colhead]:not(.dci-mx-locked) [data-act=mx-colmenu]').first.click()
        pg.wait_for_selector('[data-el=works] .dci-mx-colmenu [data-f=mx-credit]', timeout=5000)
        menu = pg.evaluate("[!!document.querySelector('[data-el=works] .dci-mx-colmenu [data-f=mx-credit]'), !!document.querySelector('[data-el=works] .dci-mx-colmenu [data-act=mx-col-allworks]')]")
        print('B) ▾:', menu)
        results.append(not a['headCredit'] and not a['headAll'] and not a['corner'] and menu == [True, True])
        pg.locator('[data-el=works] .dci-mx-colmenu [data-act=mx-colmenu]').first.click()
        pg.click('[data-el=works] [data-act=mx-more]')
        pg.click('[data-el=works-more] [data-act=mx-heads]')
        pg.wait_for_timeout(400)
        full = pg.evaluate(INFO)
        pg.click('[data-el=works] [data-act=mx-more]')
        pg.click('[data-el=works-more] [data-act=mx-heads]')
        pg.wait_for_timeout(400)
        back = pg.evaluate(INFO)
        print('C)', full['right'], full['headCredit'], full['headAll'], full['corner'], full['stored'], '→', back['headCredit'], back['stored'])
        results.append('mx-defaults' in full['right'] and full['headCredit'] and full['headAll'] and full['corner'] and full['stored'] == '"full"'
                       and not back['headCredit'] and back['stored'] is None)
        d = pg.evaluate("""(() => { const c = document.querySelector('[data-el=works] td.dci-mx-cell.dci-mx-on:not(.dci-mx-locked) .dci-mx-more'); return c ? getComputedStyle(c).opacity : null; })()""")
        pg.locator('[data-el=works] td.dci-mx-cell.dci-mx-on:not(.dci-mx-locked)').first.hover()
        d2 = pg.evaluate("""(() => { const c = document.querySelector('[data-el=works] td.dci-mx-cell.dci-mx-on:not(.dci-mx-locked) .dci-mx-more'); return c ? getComputedStyle(c).opacity : null; })()""")
        print('D)', d, d2)
        results.append(d == '0' and d2 == '1')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    H.MX_HEADS = 'full'
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_rowstate3166():
    """Credits Importer 3.166.0 (proposals W-ROWSTATE, W-STICKY with W-SCROLL, W-MODEL step one).
    A) A track without a work says once in its row what waits for the work ("2 credits wait for a work", "1 credit waits …"); the linked
       track says nothing of the kind.
    B) A window narrower than the matrix: the matrix scrolls to the right inside its frame (the page does not), and the first column
       – track and work – stays where it is while the columns move under it.
    C) The drawing reads the matrix once: what the matrix shows is the same as before (the roles of every cell), and "＋ New works"
       still plans a work for each of the three tracks."""
    H.MX_HEADS = None
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = b.new_context(viewport={'width': 900, 'height': 1400})
        H.install_routes(ctx)
        H.add_mapping(ctx)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_selector('[data-el=works] th[data-colhead]', timeout=20000)
        pg.wait_for_timeout(600)
        a = pg.evaluate("""[...document.querySelectorAll('[data-el=works] tbody tr')].map(tr => [(tr.querySelector('.dci-mx-title strong') || {}).textContent,
          ((tr.querySelector('[data-el=row-wait]') || {}).textContent || '').trim()]).filter(x => x[0])""")
        print('A)', a)
        results.append(a == [['Song One', ''], ['Song Two', '2 credits wait for a work'], ['Song Three', '1 credit waits for a work'], ['Song Four', '']])
        B = """(() => { const w = document.querySelector('[data-el=works] .dci-mx-wrap'); const first = w.querySelector('tbody tr td, tbody tr th');
          const col = w.querySelector('th[data-colhead]');
          return { wide: w.scrollWidth > w.clientWidth + 20, page: document.querySelector('#dci-overlay .dci-body, #dci-overlay .dci-panel').scrollWidth,
            left: Math.round(first.getBoundingClientRect().left), col: Math.round(col.getBoundingClientRect().left), sl: Math.round(w.scrollLeft) }; })()"""
        b0 = pg.evaluate(B)
        pg.evaluate("document.querySelector('[data-el=works] .dci-mx-wrap').scrollLeft = 260")
        pg.wait_for_timeout(300)
        b1 = pg.evaluate(B)
        print('B)', b0, '→', b1)
        results.append(b0['wide'] and b1['sl'] >= 200 and b1['left'] == b0['left'] and b1['col'] <= b0['col'] - 200)
        cells = pg.evaluate("""[...document.querySelectorAll('[data-el=works] tbody tr')].map(tr => [...tr.querySelectorAll('td.dci-mx-cell')].map(td => [...td.querySelectorAll('.dci-mxchip')].map(c => c.textContent.trim().replace(/\\s+/g, ' ')).join('+')))""")
        pg.click('[data-el=works] [data-act=works-pending-all]')
        pg.wait_for_timeout(600)
        planned = pg.evaluate("[...document.querySelectorAll('[data-el=works] tbody tr')].filter(tr => /new work|New work/.test(tr.textContent)).length")
        waits = pg.evaluate("document.querySelectorAll('[data-el=works] [data-el=row-wait]').length")
        print('C)', cells[:3], planned, waits)
        results.append(cells[0][0].startswith('composer') and 'writer' in cells[1][0] and 'composer' in cells[2][1] and planned == 3 and waits == 0)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    H.MX_HEADS = 'full'
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_done3167():
    """Credits Importer 3.167.0 (proposals W-DIFFONLY, W-DATES). MusicBrainz has the works of tracks 1–3 linked, the source names no writers.
    A) Compact: the three tracks are one line – "3 works complete in MusicBrainz" –, only "Song Four" (no work yet) is a row.
    B) "Show": all four rows, the line says "Hide"; "Hide": one row again.
    C) Everything in the open (the heads full): no such line, four rows.
    D) A role with a date of its own shows the date in its chip ("writer ⌚ 1974")."""
    orig, orig_ws = H.discogs_release, H.ws_release
    W = [H.WORK1, H.uid('cccccccc', 2), H.uid('cccccccc', 3)]

    def rel(writers=False):
        d = orig()
        d['notes'] = ''
        d['companies'] = [c for c in d['companies'] if c['entity_type_name'] != 'Published By']
        for k, t in enumerate(d['tracklist']):
            t['extraartists'] = [x for x in t['extraartists'] if writers and k == 3] + ([{'name': 'Writer W', 'anv': '', 'role': 'Written-By', 'tracks': '', 'id': 3007, 'join': ''}] if writers and k == 3 else [])
        return d

    def ws(full=False):
        d = orig_ws(full)
        for m in d['media']:
            for t in m.get('tracks', []):
                i = t['position'] - 1
                if i in (1, 2) and 'relations' in t['recording']:
                    t['recording']['relations'].append({'target-type': 'work', 'type': 'performance', 'type-id': H.LTS[278]['gid'], 'attributes': [],
                                                        'work': {'id': W[i], 'title': H.TITLES[i], 'relations': []}})
        return d
    ROWS = """(() => { const w = document.querySelector('[data-el=works]');
      return { rows: [...w.querySelectorAll('tbody tr[data-work]')].map(tr => (tr.querySelector('.dci-mx-title strong') || {}).textContent),
        done: ((w.querySelector('[data-el=works-done]') || {}).textContent || '').replace(/\\s+/g, ' ').trim() }; })()"""
    results = []
    try:
        H.ws_release = ws
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            for heads in (None, 'full'):
                H.MX_HEADS = heads
                H.discogs_release = lambda: rel(False)
                ctx = H.new_context(b)
                pg, errs = H.open_mb_edit(ctx, companion=False)
                pg.wait_for_selector('#dci-open', timeout=20000)
                H.open_dashboard(pg)
                pg.wait_for_selector('[data-el=works] tbody tr[data-work]', timeout=20000)
                pg.wait_for_timeout(800)
                a = pg.evaluate(ROWS)
                if heads is None:
                    print('A)', a)
                    results.append(a['rows'] == ['Song Four'] and a['done'].startswith('3 works complete in MusicBrainz') and a['done'].endswith('Show'))
                    pg.click('[data-el=works] [data-act=mx-done]')
                    pg.wait_for_timeout(300)
                    b1 = pg.evaluate(ROWS)
                    pg.click('[data-el=works] [data-act=mx-done]')
                    pg.wait_for_timeout(300)
                    b2 = pg.evaluate(ROWS)
                    print('B)', b1, '→', b2['rows'])
                    results.append(len(b1['rows']) == 4 and b1['done'].endswith('Hide') and b2['rows'] == ['Song Four'])
                else:
                    print('C)', a)
                    results.append(len(a['rows']) == 4 and a['done'] == '')
                print('Fehler:', errs)
                results.append(not errs)
                ctx.close()
            # D) a date of its own in the chip
            H.MX_HEADS = None
            H.discogs_release = lambda: rel(True)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            pg.wait_for_selector('[data-el=works] tbody tr[data-work] td.dci-mx-cell.dci-mx-on', timeout=20000)
            cell = pg.locator('[data-el=works] tbody tr[data-work] td.dci-mx-cell.dci-mx-on').first
            cell.hover()
            cell.locator('[data-act=mx-menu]').click()
            pg.wait_for_selector('[data-el=works] .dci-mx-menu', timeout=5000)
            fields = pg.evaluate("[...document.querySelectorAll('[data-el=works] .dci-mx-menu .dci-mx-date input')].map(i => i.dataset.f || i.name || i.className)")
            pg.locator('[data-el=works] .dci-mx-menu .dci-mx-date input').first.fill('1974')
            pg.click('[data-el=works] .dci-mx-menu [data-act=mx-celldate-apply]')
            pg.wait_for_timeout(500)
            chips = pg.evaluate("[...document.querySelectorAll('[data-el=works] td.dci-mx-cell .dci-mxchip')].map(c => [c.textContent.replace(/\\s+/g, ' ').trim(), (c.querySelector('.dci-mxchip-date') || {}).textContent || ''])")
            print('D)', fields[:4], chips, errs)
            results.append(any(c[1].startswith('1974') for c in chips) and not errs)
            b.close()
    finally:
        H.discogs_release, H.ws_release = orig, orig_ws
        H.MX_HEADS = 'full'
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_same3168():
    """Credits Importer 3.168.0 (W-SAMEFORALL; W-MODEL: the row model). The source names "Written-By – Writer W" for the whole release, no
    track has a work in MusicBrainz, the titles are found nowhere.
    A) Compact: one row – "All 4 tracks", "no work yet", the column "Writer W" with "writer" once – and "Show per track".
    B) "Show per track": four rows and a line that offers "One row for all"; that brings the one row back.
    C) "＋ New works (4)" in the row plans a work for each track: one row still, "4 new works", the role no longer waiting.
    D) A track that differs (a second writer on track 2 only): the matrix stays a matrix (four rows, no such row).
    E) Everything in the open: four rows."""
    orig, orig_ws = H.discogs_release, H.ws_release
    ex = lambda name, role, i: {'name': name, 'anv': '', 'role': role, 'tracks': '', 'id': i, 'join': ''}  # noqa: E731

    def rel(extra=False):
        d = orig()
        d['notes'] = ''
        d['companies'] = [c for c in d['companies'] if c['entity_type_name'] != 'Published By']
        for k, t in enumerate(d['tracklist']):
            t['extraartists'] = [ex('Writer Z', 'Composed By', 3008)] if extra and k == 1 else []
        d['extraartists'] = [x for x in d['extraartists'] if 'Writ' not in x['role'] and 'Compos' not in x['role']] + [ex('Writer W', 'Written-By', 3007)]
        return d

    def ws(full=False):
        d = orig_ws(full)
        for m in d['media']:
            for t in m.get('tracks', []):
                t['recording']['relations'] = [r for r in t['recording'].get('relations', []) if r.get('target-type') != 'work']
        return d
    ROWS = """(() => { const w = document.querySelector('[data-el=works]'); const same = w.querySelector('tr.dci-mx-samerow');
      return { rows: w.querySelectorAll('tbody tr[data-work]').length, same: same ? same.querySelector('th').textContent.replace(/\\s+/g, ' ').trim() : '',
        cells: same ? [...same.querySelectorAll('td.dci-mx-cell')].map(td => [...td.querySelectorAll('.dci-mxchip')].map(c => [c.textContent.trim(), c.className.replace('dci-mxchip ', '')])) : [],
        bar: ((w.querySelector('tr.dci-mx-samebar') || {}).textContent || '').replace(/\\s+/g, ' ').trim() }; })()"""
    results = []

    def open_pg(b):
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_selector('[data-el=works] tbody tr', timeout=20000)
        pg.wait_for_timeout(1500)
        return ctx, pg, errs
    try:
        H.ws_release = ws
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            H.MX_HEADS = None
            H.discogs_release = lambda: rel(False)
            ctx, pg, errs = open_pg(b)
            a = pg.evaluate(ROWS)
            print('A)', a)
            results.append(a['rows'] == 0 and a['same'].startswith('All 4 tracks') and 'no work yet' in a['same'] and 'Show per track' in a['same']
                           and [c for c in a['cells'] if c] == [[['writer', 'dci-mxchip-wait']]])
            pg.evaluate("document.querySelector('[data-el=works] tr.dci-mx-samerow [data-act=mx-same]').click()")  # (the log window of the test page lies over the row)
            pg.wait_for_timeout(300)
            b1 = pg.evaluate(ROWS)
            pg.evaluate("document.querySelector('[data-el=works] tr.dci-mx-samebar [data-act=mx-same]').click()")  # (the log window of the test page lies over the row)
            pg.wait_for_timeout(300)
            b2 = pg.evaluate(ROWS)
            print('B)', b1['rows'], b1['bar'], '→', b2['rows'], b2['same'][:14])
            results.append(b1['rows'] == 4 and b1['bar'].endswith('One row for all') and b2['rows'] == 0 and b2['same'].startswith('All 4 tracks'))
            pg.evaluate("document.querySelector('[data-el=works] tr.dci-mx-samerow [data-act=works-pending-all]').click()")  # (the log window of the test page lies over the row)
            pg.wait_for_timeout(800)
            c = pg.evaluate(ROWS)
            print('C)', c)
            results.append(c['rows'] == 0 and '4 new works' in c['same'] and [x for x in c['cells'] if x] == [[['writer', 'dci-mxchip-on']]])
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
            H.discogs_release = lambda: rel(True)
            ctx, pg, errs = open_pg(b)
            d = pg.evaluate(ROWS)
            print('D)', d['rows'], d['same'], errs)
            results.append(d['rows'] == 4 and d['same'] == '' and not errs)
            ctx.close()
            H.MX_HEADS = 'full'
            H.discogs_release = lambda: rel(False)
            ctx, pg, errs = open_pg(b)
            e = pg.evaluate(ROWS)
            print('E)', e['rows'], e['same'], errs)
            results.append(e['rows'] == 4 and e['same'] == '' and not errs)
            b.close()
    finally:
        H.discogs_release, H.ws_release = orig, orig_ws
        H.MX_HEADS = 'full'
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_samework3192():
    """Credits Importer 3.192.0 (collected item Z-SAMEWORK, rule S342): tracks 2–4 of one title – "Song Two", "Song Two (Alternate
    Take)", "Song Two - Live" – are one work (track 1 has its work in MusicBrainz).
    A) Above the first of them, one yellow question "the same work “Song Two”?" with "✓ One work" and "✕ Separate works".
    B) "✓ One work" (none has a work): the line says so and that the form opens at "Stage". "Stage": nothing staged – the form of the work
       opens, prefilled with "Song Two" (without "Alternate Take"); closed: nothing staged, a message says why. "Stage" again, the work
       created: staging goes on – all three recordings linked with it.
    C) "↺ ask again" brings the question back; "✕ Separate works" answers it.
    D) "✨ Answer all": "careful" a new work for the first track only; "balanced" the same (the titles differ); "bold" one new work for
       all three.
    E) In Node: the endings of versions are left out ("(Alternate Take 2) [Mono]", "- Live at …", "(Dub Mix)"), not "(Reprise)",
       "(Part 2)".
    F) Rule S342 off: no question.
    G) Track 1 "Song One" has its work in MusicBrainz, track 2 is "Song One (Take 2)": "✓ One work" links that work with track 2 – "Stage"
       stages it at once, no form."""
    import json, subprocess, urllib.parse
    WG = H.uid('cccccccc', 192)
    orig = H.discogs_release
    old = H.TITLES[:]
    H.TITLES[:] = ['Intro', 'Song Two', 'Song Two (Alternate Take)', 'Song Two - Live']

    def rel():
        d = orig()
        for tk, title in zip(d['tracklist'], H.TITLES):
            tk['title'] = title
        return d
    H.discogs_release = rel
    ROW = """(() => [...document.querySelectorAll('[data-el=works] [data-sameworkrow]')].map(x => [x.textContent.replace(/\\s+/g, ' ').trim().slice(0, 120),
      [...x.querySelectorAll('button')].map(y => y.dataset.act), !!x.querySelector('.dci-mx-ask')]))()"""
    ADDED = "MB.relationshipEditor.state.added.length"
    results = []

    def start(p, level=None, off=None):
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        init = ''
        if level:
            init += f" localStorage.setItem('dci-magic-level', '\"{level}\"');"
        if off:
            init += f" localStorage.setItem('dci-rules-off', JSON.stringify({json.dumps(off)}));"
        if init:
            ctx.add_init_script("if (/musicbrainz/.test(location.hostname)) {" + init + " }")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)
        return b, pg, errs

    def preview(pg):
        pg.locator('[data-act=magic-open]').evaluate('b => b.click()'); H.wait_for(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
        out = pg.evaluate("[...document.querySelectorAll('[data-el=magic-preview] [data-el=magic-item]')].map(x => [x.dataset.kind, x.textContent.replace(/\\s+/g, ' ').trim()])")
        pg.locator('[data-act=magic-cancel]').evaluate('b => b.click()')
        return [x for x in out if x[0] == 'work']
    try:
        with sync_playwright() as p:
            b, pg, errs = start(p)
            a = pg.evaluate(ROW)
            print('A)', a)
            results.append(len(a) == 1 and 'the same work “Song Two”?' in a[0][0] and '2–4' in a[0][0] and a[0][1] == ['samework-one', 'samework-apart'] and a[0][2])
            pg.locator('[data-sameworkrow] [data-act=samework-one]').evaluate('b => b.click()'); pg.wait_for_timeout(600)
            b1 = pg.evaluate(ROW)
            n0 = pg.evaluate(ADDED)
            pg.click('[data-act=apply]')
            H.wait_for(pg, "!!document.querySelector('[data-el=sub-frame]') && /work\\/create/.test(document.querySelector('[data-el=sub-frame]').src)", 20)
            q = urllib.parse.parse_qs(urllib.parse.urlparse(pg.evaluate("document.querySelector('[data-el=sub-frame]').src")).query)
            pg.click('[data-act=sub-close]'); pg.wait_for_timeout(600)
            msg = pg.evaluate("[...document.querySelectorAll('.dci-msg, [data-el=messages] *')].map(x => x.textContent).join(' ')")
            print('B)', b1, q.get('edit-work.name'), pg.evaluate(ADDED) - n0, 'Nothing staged' in msg)
            ok_b = len(b1) == 1 and 'one work “Song Two”' in b1[0][0] and 'form opens at “Stage”' in b1[0][0] and not b1[0][2] and q.get('edit-work.name') == ['Song Two'] and pg.evaluate(ADDED) == n0 and 'Nothing staged' in msg
            pg.click('[data-act=apply]')
            H.wait_for(pg, "!!document.querySelector('[data-el=sub-frame]') && /work\\/create/.test(document.querySelector('[data-el=sub-frame]').src)", 20)
            H.COMPANIES[7192] = ('work', WG, 'Song Two')
            H.WORK_TITLES[WG] = 'Song Two'
            pg.evaluate(f"document.querySelector('[data-el=sub-frame]').src = 'https://musicbrainz.org/work/{WG}'")
            H.wait_for(pg, f"{ADDED} > {n0}", 30)
            pg.wait_for_timeout(1500)
            linked = pg.evaluate(f"MB.relationshipEditor.state.added.filter(r => JSON.stringify(r).includes('{WG}')).length")
            print('B2)', linked, errs)
            results.append(ok_b and linked >= 3 and not errs)
            b.close()
            b, pg, errs = start(p)
            pg.locator('[data-sameworkrow] [data-act=samework-one]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
            pg.locator('[data-sameworkrow] [data-act=samework-undo]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
            c1 = pg.evaluate(ROW)
            pg.locator('[data-sameworkrow] [data-act=samework-apart]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
            c2 = pg.evaluate(ROW)
            print('C)', c1, c2)
            results.append(c1[0][2] and 'separate works' in c2[0][0] and not c2[0][2] and not errs)
            b.close()
            d = []
            for lv in ('careful', 'balanced', 'bold'):
                b, pg, errs = start(p, level=lv)
                d.append(preview(pg))
                b.close()
            print('D)', d)
            results.append(len(d[0]) == 1 and 'first of its tracks only' in d[0][0][1] and len(d[1]) == 1 and 'first of its tracks only' in d[1][0][1]
                           and any('one new work “Song Two” for 3 tracks' in x[1] for x in d[2]))
            b, pg, errs = start(p, off=['S342'])
            f = pg.evaluate(ROW)
            print('F)', f)
            results.append(f == [] and not errs)
            b.close()
            H.TITLES[:] = ['Song One', 'Song One (Take 2)', 'Song Three', 'Song Four']
            b, pg, errs = start(p)
            g0 = pg.evaluate(ROW)
            pg.locator('[data-sameworkrow] [data-act=samework-one]').evaluate('b => b.click()'); pg.wait_for_timeout(600)
            n0 = pg.evaluate(ADDED)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(2500)
            frame = pg.evaluate("!!document.querySelector('[data-el=sub-frame]') && /work\\/create/.test(document.querySelector('[data-el=sub-frame]').src)")
            w1 = pg.evaluate(f"MB.relationshipEditor.state.added.filter(r => JSON.stringify(r).includes('{H.WORK1}')).length")
            print('G)', g0, frame, pg.evaluate(ADDED) - n0, w1, errs)
            results.append(len(g0) == 1 and 'has this work in MusicBrainz' in g0[0][0] and not frame and w1 >= 1 and not errs)
            b.close()
        js = ("global.localStorage={getItem:()=>null,setItem(){},removeItem(){},key:()=>null,length:0};const m=require(process.argv[1]);"
              "console.log(JSON.stringify(['Song (Alternate Take 2) [Mono]','Song - Live at the Fillmore','Song (Dub Mix)','Song (Reprise)','Song (Part 2)'].map(t=>m.sameWorkBase(t).base)))")
        e = json.loads(subprocess.run(['node', '-e', js, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True).stdout)
        print('E)', e)
        results.append(e == ['Song', 'Song', 'Song', 'Song (Reprise)', 'Song (Part 2)'])
    finally:
        H.discogs_release = orig
        H.TITLES[:] = old
        H.COMPANIES.pop(7192, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_notesparts3192():
    """Credits Importer 3.192.0 (collected item Z-NOTESPARTS, rules S343, S344): the notes of the release name the parts of track 2
    ("Track 2:" and "I. …", "II. …", "III. …") and a subtitle of track 1.
    A) "Suites from notes" off (default): no suite asked; a grey line at track 2 "might be a suite?" with "Read suites from notes"; at
       track 1 its subtitle as a hint. No entry from these lines (no "Cliff Hectopasil", no "Peter").
    B) "Read suites from notes": the suite "Big Piece" of track 2 asked (from the notes of the track); "✓ Yes": 3 parts.
    C) "✨ Answer all": the suite on "bold" only (not on "balanced").
    D) Rule S344 off: no grey lines."""
    import json
    orig = H.discogs_release
    old = H.TITLES[:]
    H.TITLES[:] = ['Song One', 'Big Piece', 'Song Three', 'Song Four']
    NOTES = ("Recorded at Abbey Road Studios.\n\nSubtitles / annotations / dedications for:\nTrack 1:\nDurch Dick und Dünn mit Gunning Günter\n"
             "Track 2:\nI. Die Turnbulle - am Reck: Cliff Hectopasil, Tret-Schelle für Peter\nII. China-Frühling im Hochgebirg\n"
             "III. Freiheitskämpfer auf dem Weg zur Arbeit (Günter backt\nPlätzchen in Untersuhl)\nTrack 3:\nFor my Daughter")

    def rel():
        d = orig()
        for tk, title in zip(d['tracklist'], H.TITLES):
            tk['title'] = title
        d['notes'] = NOTES
        return d
    H.discogs_release = rel
    NOTE = "[...document.querySelectorAll('[data-el=works] tr.dci-mx-noterow')].map(x => [x.dataset.noterow, x.textContent.replace(/\\s+/g, ' ').trim().slice(0, 300)])"
    SUITE = "[...document.querySelectorAll('[data-el=works] [data-suite]')].map(x => x.textContent.replace(/\\s+/g, ' ').trim().slice(0, 140))"
    results = []

    def start(p, level=None, off=None):
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        init = ''
        if level:
            init += f" localStorage.setItem('dci-magic-level', '\"{level}\"');"
        if off:
            init += f" localStorage.setItem('dci-rules-off', JSON.stringify({json.dumps(off)}));"
        if init:
            ctx.add_init_script("if (/musicbrainz/.test(location.hostname)) {" + init + " }")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(2000)
        return b, pg, errs

    def preview(pg):
        pg.locator('[data-act=magic-open]').evaluate('b => b.click()'); H.wait_for(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
        out = pg.evaluate("[...document.querySelectorAll('[data-el=magic-preview] [data-el=magic-item]')].map(x => x.dataset.kind)")
        pg.locator('[data-act=magic-cancel]').evaluate('b => b.click()')
        return out
    try:
        with sync_playwright() as p:
            b, pg, errs = start(p)
            a = [pg.evaluate(NOTE), pg.evaluate(SUITE), pg.evaluate("[...document.querySelectorAll('section.dci-group .dci-gname strong')].map(x => x.textContent)")]
            print('A)', a)
            results.append(any(r[0] == '1' and 'might be a suite?' in r[1] and 'Read suites from notes' in r[1] for r in a[0])
                           and any(r[0] == '0' and 'Durch Dick und Dünn' in r[1] for r in a[0]) and a[1] == []
                           and not any(re.search(r'Cliff|Peter|Hectopasil', x) for x in a[2]))
            pg.locator('[data-act=notes-suites]').evaluate('b => b.click()'); pg.wait_for_timeout(600)
            b1 = pg.evaluate(SUITE)
            pg.locator('[data-suite] [data-act=suite-yes]').first.evaluate('b => b.click()'); pg.wait_for_timeout(600)
            b2 = pg.evaluate(SUITE)
            print('B)', b1, b2, errs)
            results.append(len(b1) == 1 and '“Big Piece”' in b1[0] and 'from the notes of the track' in b1[0] and '3' in b2[0] and not errs)
            b.close()
            c = []
            for lv in ('balanced', 'bold'):
                b, pg, errs = start(p, level=lv)
                pg.locator('[data-act=notes-suites]').evaluate('b => b.click()'); pg.wait_for_timeout(500)
                c.append(preview(pg))
                b.close()
            print('C)', c)
            results.append('suite' not in c[0] and 'suite' in c[1])
            b, pg, errs = start(p, off=['S344'])
            d = pg.evaluate(NOTE)
            print('D)', d)
            results.append(d == [] and not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.TITLES[:] = old
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_parthead3196():
    """Credits Importer 3.196.0 (collected items Z-PARTHEADS, Z-SUITERENAME, Z-SUITECLICKS, Z-WORKIDS; rules S353–S355): the Discogs track
    list has the headings "Part I" (tracks 1, 2) and "Part II" (tracks 3, 4); the release in MusicBrainz is called "Bosque de Niebla".
    A) One yellow question: "Suite “Bosque de Niebla” with 2 parts (Part I: …, Part II: …)?" – not two suites "Part I", "Part II".
    B) "✨ Answer all" on "careful": no suite; on "balanced" the suite, its name changeable in the preview ("Bosque de niebla" → "Bosque").
    C) Accepted: one line, the suite and its parts "Bosque, Part I", "Bosque, Part II"; "✎" changes the name back ("Bosque de Niebla":
       the parts follow).
    D) "Stage": the form of the suite first (name, type Suite); created, the form of "Bosque de Niebla, Part I" – with "part of" the
       suite (its MBID, the type "parts"); then Part II; then staging goes on: the works of tracks 1, 2 parts of Part I, of 3, 4 of Part II.
    E) The MBIDs kept for the release (localStorage): a new import accepts the suite again – nothing to create."""
    import json, urllib.parse
    TOP, P1, P2 = H.uid('cccccccc', 1961), H.uid('cccccccc', 1962), H.uid('cccccccc', 1963)
    # (MusicBrainz's link type "parts" of two works, with "movement"; the type "Suite" in the form)
    H.attr(1105, 'movement', 1105)
    H.lt(281, 'ca8d3642-ce5f-49f8-91f2-125d72524e6a', 'parts', 'work', 'work', (1105,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    if '<option value="6">Suite</option>' not in H.WORK_FORM:
        H.WORK_FORM = H.WORK_FORM.replace('<option value="1">Aria</option>', '<option value="1">Aria</option><option value="6">Suite</option>')
    orig = H.discogs_release
    old = H.TITLES[:]
    H.TITLES[:] = ['Entre Helechos', 'Fantasmas', 'Bejuco Del Alma', 'Musguito']

    def rel():
        d = orig()
        tl = d['tracklist']
        for tk, title in zip(tl, H.TITLES):
            tk['title'] = title
        d['tracklist'] = [{'position': '', 'type_': 'heading', 'title': 'Part I', 'duration': ''}] + tl[:2] + [{'position': '', 'type_': 'heading', 'title': 'Part II', 'duration': ''}] + tl[2:]
        return d
    H.discogs_release = rel
    orig_ws = H.ws_release

    def ws(full=False):
        d = orig_ws(full)
        d['title'] = 'Bosque de Niebla'
        return d
    H.ws_release = ws
    LINE = """(() => [...document.querySelectorAll('[data-el=works] [data-suite]')].map(x => [x.textContent.replace(/\\s+/g, ' ').trim().slice(0, 260),
      [...x.querySelectorAll('button')].map(y => y.dataset.act), !!x.querySelector('.dci-mx-ask')]))()"""
    SRC = "document.querySelector('[data-el=sub-frame]') ? document.querySelector('[data-el=sub-frame]').src : ''"
    ADDED = "MB.relationshipEditor.state.added"
    results = []

    def start(p, level=None, keep=None):
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        init = ''
        if level:
            init += f" localStorage.setItem('dci-magic-level', '\"{level}\"');"
        if keep:
            init += f" localStorage.setItem('dci-created-suites:{H.REL}', JSON.stringify({json.dumps(keep)}));"
        if init:
            ctx.add_init_script("if (/musicbrainz/.test(location.hostname)) {" + init + " }")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(2500)
        return b, pg, errs

    def preview(pg):
        pg.locator('[data-act=magic-open]').evaluate('b => b.click()'); H.wait_for(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
        return pg.evaluate("[...document.querySelectorAll('[data-el=magic-preview] [data-el=magic-item]')].map(x => [x.dataset.kind, x.textContent.replace(/\\s+/g, ' ').trim(), !!x.querySelector('[data-f=magic-suite-name]')])")

    def create(pg, gid, title):
        H.wait_for(pg, f"/work\\/create/.test({SRC})", 20)
        q = urllib.parse.parse_qs(urllib.parse.urlparse(pg.evaluate(SRC)).query)
        H.WORK_TITLES[gid] = title
        H.COMPANIES[int(gid[-4:])] = ('work', gid, title)
        pg.evaluate(f"document.querySelector('[data-el=sub-frame]').src = 'https://musicbrainz.org/work/{gid}'")
        pg.wait_for_timeout(1500)
        rels = [(q.get(f'rels.{k}.target', [''])[0], q.get(f'rels.{k}.type', [''])[0], q.get(f'rels.{k}.backward', [''])[0]) for k in range(8) if f'rels.{k}.target' in q]
        return [q.get('edit-work.name', [''])[0], q.get('edit-work.type_id', [''])[0], rels]
    try:
        with sync_playwright() as p:
            b, pg, errs = start(p)
            a = pg.evaluate(LINE)
            print('A)', a)
            results.append(len(a) == 1 and 'suite-yes' in a[0][1] and 'Suite “Bosque de Niebla” with 2 parts (Part I: ' in a[0][0] and 'Part II: ' in a[0][0])
            c0 = preview(pg)
            pg.locator('[data-act=magic-cancel]').evaluate('b => b.click()')
            b.close()
            b, pg, errs = start(p, level='balanced')
            c1 = preview(pg)
            print('B)', c0, c1)
            pg.fill('[data-f=magic-suite-name]', 'Bosque')
            pg.locator('[data-act=magic-apply]').evaluate('b => b.click()'); H.wait_for(pg, "!!document.querySelector('[data-act=magic-undo]')", 20)
            pg.wait_for_timeout(1200)
            results.append(not any(k == 'suite' for k, _, _ in c0) and any(k == 'suite' and 'with 2 parts' in t and f for k, t, f in c1))
            cc = pg.evaluate(LINE)
            pg.locator('[data-act=suite-rename]').first.evaluate('b => b.click()'); pg.wait_for_timeout(300)
            pg.fill('[data-f=suite-rename]', 'Bosque de Niebla')
            pg.press('[data-f=suite-rename]', 'Enter'); pg.wait_for_timeout(500)
            cd = pg.evaluate(LINE)
            print('C)', cc, '\n  ', cd)
            results.append('Suite “Bosque” with 2 parts' in cc[0][0] and 'Bosque, Part I' in cc[0][0] and 'Bosque, Part II' in cc[0][0]
                           and 'Suite “Bosque de Niebla” with 2 parts' in cd[0][0] and 'Bosque de Niebla, Part II' in cd[0][0])
            n0 = len(pg.evaluate(ADDED))
            pg.click('[data-act=apply]')
            d1 = create(pg, TOP, 'Bosque de Niebla')
            d2 = create(pg, P1, 'Bosque de Niebla, Part I')
            d3 = create(pg, P2, 'Bosque de Niebla, Part II')
            H.wait_for(pg, f"{ADDED}.length > {n0}", 30)
            pg.wait_for_timeout(1500)
            parts = pg.evaluate(f"{ADDED}.filter(r => r.linkTypeID === 281).map(r => [(r.entity0 || {{}}).gid, (r.entity1 || {{}}).name])")
            print('D)', d1, d2, d3, '\n   parts:', parts, errs)
            p_lt = str(next(k for k, v in H.LTS.items() if v['name'] == 'parts' and v['type0'] == 'work' and v['type1'] == 'work')) if any(v.get('name') == 'parts' for v in H.LTS.values()) else None
            results.append(d1[0] == 'Bosque de Niebla' and d1[1] == '6' and d2[0] == 'Bosque de Niebla, Part I' and (TOP, '281', '1') in d2[2]
                           and d3[0] == 'Bosque de Niebla, Part II' and (TOP, '281', '1') in d3[2]
                           and sorted(x[0] for x in parts) == sorted([P1, P1, P2, P2]) and not errs)
            kept = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-created-suites:{H.REL}') || '[]').map(x => [x.title, x.gid, x.parent || '', x.partNo])")
            b.close()
            b, pg, errs = start(p, keep=[{'kind': 'suite', 'key': k[0], 'title': k[0], 'gid': k[1], 'parent': k[2], 'partNo': k[3]} for k in kept])
            pg.locator('[data-act=suite-yes]').first.evaluate('b => b.click()'); pg.wait_for_timeout(800)
            e = pg.evaluate(LINE)
            print('E)', kept, e)
            results.append(len(kept) == 3 and kept[0][1] == TOP and kept[1][2] == TOP and 'suite-create' not in e[0][1] and 'Suite in MusicBrainz: Bosque de Niebla' in e[0][0])
            b.close()
    finally:
        H.discogs_release = orig
        H.ws_release = orig_ws
        H.TITLES[:] = old
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suite3197():
    """Credits Importer 3.197.0 (collected items Z-SUITEDUP, Z-BGLOAD, Z-SUITECASE, Z-SUITENAMES, Z-PARTATTR; rules S356–S360): Discogs
    writes the titles "Entre Helechos", "Bejuco Del Alma" below the headings "Part I", "Part II"; MusicBrainz "Entre helechos", "Bejuco del alma".
    A) Accepted (track 1 has its work): the works of the tracks named as MusicBrainz writes them ("Bosque de niebla, Part II: Bejuco del
       alma"); the line has "Names:",
       the attribute of its parts' suites (none) and of their tracks (movement); no part is looked up in MusicBrainz (only the suite).
    B) "Names:" clicked: the works by the part alone ("Fantasmas"); once more: back.
    C) "Stage": the form of the suite – while it is open the line says "Its form is open …" and has no "＋ Create"; the parts' suites as
       "movement" (chosen): the form of Part I has the attribute; the works of the tracks without one (chosen: none)."""
    import urllib.parse
    TOP, P1, P2 = H.uid('cccccccc', 1971), H.uid('cccccccc', 1972), H.uid('cccccccc', 1973)
    H.attr(1105, 'movement', 1105)
    H.lt(281, 'ca8d3642-ce5f-49f8-91f2-125d72524e6a', 'parts', 'work', 'work', (1105,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    if '<option value="6">Suite</option>' not in H.WORK_FORM:
        H.WORK_FORM = H.WORK_FORM.replace('<option value="1">Aria</option>', '<option value="1">Aria</option><option value="6">Suite</option>')
    orig, orig_ws, old = H.discogs_release, H.ws_release, H.TITLES[:]
    H.TITLES[:] = ['Entre helechos', 'Fantasmas', 'Bejuco del alma', 'Musguito']

    def rel():
        d = orig()
        tl = d['tracklist']
        for tk, title in zip(tl, ['Entre Helechos', 'Fantasmas', 'Bejuco Del Alma', 'Musguito']):
            tk['title'] = title
        d['tracklist'] = [{'position': '', 'type_': 'heading', 'title': 'Part I', 'duration': ''}] + tl[:2] + [{'position': '', 'type_': 'heading', 'title': 'Part II', 'duration': ''}] + tl[2:]
        return d

    def ws(full=False):
        d = orig_ws(full)
        d['title'] = 'Bosque de niebla'
        return d
    H.discogs_release, H.ws_release = rel, ws
    LINE = "(() => { const x = document.querySelector('[data-el=works] [data-suite]'); return x ? [x.textContent.replace(/\\s+/g, ' ').trim(), [...x.querySelectorAll('button')].map(y => y.dataset.act), [...x.querySelectorAll('select[data-f=suite-attr]')].map(y => [y.dataset.level, y.value])] : null; })()"
    SRC = "document.querySelector('[data-el=sub-frame]') ? document.querySelector('[data-el=sub-frame]').src : ''"
    ADDED = "MB.relationshipEditor.state.added"
    results = []
    searches = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(2500)
            pg.on('request', lambda r: searches.append(urllib.parse.unquote(r.url)) if '/ws/2/work?query' in r.url else None)
            pg.locator('[data-act=suite-yes]').first.evaluate('b => b.click()')
            pg.wait_for_timeout(4000)
            a = pg.evaluate(LINE)
            print('A)', a, '\n   searches:', searches)
            results.append(a and '“Bosque de niebla, Part I: Fantasmas” ⇄ “Fantasmas”' in a[0] and ['up', ''] in a[2] and ['', 'movement'] in a[2]
                           and not any('Entre helechos' in x or 'Bejuco' in x for x in searches))
            pg.locator('[data-act=suite-naming1]').evaluate('b => b.click()'); pg.wait_for_timeout(500)
            b1 = pg.evaluate(LINE)
            pg.locator('[data-act=suite-naming1]').evaluate('b => b.click()'); pg.wait_for_timeout(500)
            b2 = pg.evaluate(LINE)
            print('B)', b1[0][-160:], '\n  ', b2[0][-160:])
            results.append('“Fantasmas” ⇄ “Bosque de niebla, Part I: Fantasmas”' in b1[0] and '“Bosque de niebla, Part I: Fantasmas” ⇄' in b2[0])
            pg.select_option('select[data-f=suite-attr][data-level=up]', 'movement'); pg.wait_for_timeout(300)
            pg.select_option('select[data-f=suite-attr][data-level=""]', ''); pg.wait_for_timeout(300)
            n0 = len(pg.evaluate(ADDED))
            pg.click('[data-act=apply]')
            H.wait_for(pg, f"/work\\/create/.test({SRC})", 20)
            c0 = pg.evaluate(LINE)
            pg.locator('[data-act=apply]').evaluate('b => b.click()'); pg.wait_for_timeout(800)
            src_before = pg.evaluate(SRC)

            def create(gid, title):
                H.wait_for(pg, f"/work\\/create/.test({SRC})", 20)
                q = urllib.parse.parse_qs(urllib.parse.urlparse(pg.evaluate(SRC)).query)
                H.WORK_TITLES[gid] = title
                H.COMPANIES[int(gid[-4:])] = ('work', gid, title)
                pg.evaluate(f"document.querySelector('[data-el=sub-frame]').src = 'https://musicbrainz.org/work/{gid}'")
                pg.wait_for_timeout(1500)
                return q
            q1 = create(TOP, 'Bosque de niebla')
            q2 = create(P1, 'Bosque de niebla, Part I')
            create(P2, 'Bosque de niebla, Part II')
            H.wait_for(pg, f"{ADDED}.length > {n0}", 30)
            pg.wait_for_timeout(1500)
            parts = pg.evaluate(f"{ADDED}.filter(r => r.linkTypeID === 281).map(r => [(r.entity1 || {{}}).name, (r.attributes || []).length])")
            mv = H.ATTRS[1105]['gid']
            k_up = next((k for k in range(8) if q2.get(f'rels.{k}.target') == [TOP]), None)
            up_attr = q2.get(f'rels.{k_up}.attributes.0.type') if k_up is not None else None
            print('C)', c0, k_up, up_attr, parts, errs)
            results.append('Its form is open' in c0[0] and 'suite-create' not in c0[1] and q1.get('edit-work.name') == ['Bosque de niebla'] and src_before
                           and up_attr == [mv] and parts and all(n == 0 for _, n in parts)
                           and any(t == 'Bosque de niebla, Part II: Bejuco del alma' for t, _ in parts) and not errs)
            b.close()
    finally:
        H.discogs_release, H.ws_release = orig, orig_ws
        H.TITLES[:] = old
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

run_cases(globals())
