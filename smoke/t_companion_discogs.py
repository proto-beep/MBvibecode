"""Companion on Discogs: marks switched by a click, the check on the release page, marks on track lines (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: keepmarks, relcheck, trackmarks – each the former smoke/t_<case>.py, unchanged; `python3 t_companion_discogs.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_keepmarks():
    """Credits Importer 3.17.5 / Companion 1.8.3: a click on a mark switches its credit, also on Discogs (collected item 20),
    and the marks can stay after the editor is closed (collected item 23).
    A) Discogs: the pointer resting on a mark shows its row in the dashboard (no line in the log); a click on the mark
       switches the credit off ("Skip", the mark greyed –, its line greyed), another click on again (its level back).
    B) "Click switches" off (navigation): a click on a mark shows its row (as before), nothing is switched.
    C) "Keep marks" off (default): the marks go when the editor is closed. On: they stay with the last state after the
       editor is closed; a click on them does nothing then; switched off again (in a dashboard), they go."""
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    MARK = """(n) => { const li = [...document.querySelectorAll('#release-credits li')].find(l => l.textContent.includes(n));
  const m = li && li.querySelector('.dci-dg-mark'); return m ? [m.textContent, m.classList.contains('dci-mark-off'), li.classList.contains('dci-dg-offline'), m.title] : null; }"""
    LEVEL = """(n) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === n);
  const lv = g && g.querySelector('tr.dci-row [data-act=level][aria-pressed=true]'); return lv ? lv.dataset.level : null; }"""
    MARKS = "document.querySelectorAll('.dci-dg-mark').length"
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


    def editor(ctx):
        pg, errs = H.open_mb_edit(ctx)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
        return pg, errs


    mark = lambda dg, n: dg.evaluate(f"({MARK})('{n}')")
    level = lambda pg, n: pg.evaluate(f"({LEVEL})('{n}')")
    real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg, dgerr = H.open_discogs(ctx)
        pg, errs = editor(ctx)
        poll(dg, f"({MARK})('Bass Man') !== null")
        # A) hover shows the row, a click switches
        lv0 = level(pg, 'Bass Man')
        dg.locator('#release-credits li', has_text='Bass Man').locator('.dci-dg-mark').hover()
        H.wait_for(pg, "document.querySelectorAll('tr.dci-flash').length > 0", 10)
        a0 = [pg.evaluate("[...document.querySelectorAll('tr.dci-flash')].map(t => t.closest('section').querySelector('.dci-gname strong').textContent.trim())"),
              [x for x in pg.evaluate(LOGS) if 'From Discogs' in x]]
        dg.mouse.move(5, 5)
        dg.locator('#release-credits li', has_text='Bass Man').locator('.dci-dg-mark').click()
        poll(dg, f"(({MARK})('Bass Man') || [])[1] === true")
        a1 = [level(pg, 'Bass Man'), mark(dg, 'Bass Man')[:3], [x for x in pg.evaluate(LOGS) if 'switched off' in x]]
        dg.locator('#release-credits li', has_text='Bass Man').locator('.dci-dg-mark').click()
        poll(dg, f"(({MARK})('Bass Man') || [])[1] === false")
        a2 = [level(pg, 'Bass Man'), mark(dg, 'Bass Man')[:3]]
        print('A) Zeiger → Zeile:', a0, '| Klick:', a1, '| noch ein Klick:', a2, '(vorher', lv0, ')')
        results.append(a0 == [['Bass Man'], []] and a1[0] == 'skip' and a1[1] == ['–', True, True] and a1[2] == ['Discogs: Bass Man – Bass switched off (“Skip”)']
                       and a2[0] == lv0 and a2[1][1:] == [False, False])
        # B) "Click switches" off: a click shows the row
        H.nav_switch(pg, 'data-click-toggle')
        poll(dg, f"!(({MARK})('Guitar Guy') || [''])[3].includes('skip')")
        title = mark(dg, 'Guitar Guy')[3]
        dg.locator('#release-credits li', has_text='Guitar Guy').locator('.dci-dg-mark').click()
        H.wait_for(pg, f"{LOGS}.some(x => /From Discogs: Guitar Guy/.test(x))", 10)
        b1 = [level(pg, 'Guitar Guy'), mark(dg, 'Guitar Guy')[1], title]
        print('B) „Klick schaltet“ aus:', b1)
        results.append(b1[0] != 'skip' and b1[1] is False and 'click to show it in the dashboard' in b1[2])
        H.nav_switch(pg, 'data-click-toggle')
        # C) keep marks: off – they go; on – they stay
        pg.wait_for_timeout(1200)
        pg.close()
        poll(dg, f"{MARKS} === 0", 15)
        pg, errs2 = editor(ctx)
        poll(dg, f"{MARKS} > 0")
        H.nav_switch(pg, 'data-keep-marks')
        H.wait_for(pg, f"{LOGS}.some(x => /Marks kept after the editor is closed: on/.test(x))", 10)
        pg.wait_for_timeout(1500)
        n0 = dg.evaluate(MARKS)
        pg.close()
        dg.wait_for_timeout(12000)
        c1 = dg.evaluate(MARKS)
        before = len(H.STORE.changes)
        dg.locator('#release-credits li', has_text='Bass Man').locator('.dci-dg-mark').click()
        dg.wait_for_timeout(800)
        sent = [c for c in H.STORE.changes[before:] if c['k'] == 'fromDiscogs']
        H.STORE.set('keepMarks', False)
        poll(dg, f"{MARKS} === 0", 10)
        print('C) aus: Marken weg | an: vorher', n0, 'nach dem Schließen', c1, '| Klick sendet:', len(sent), '| wieder aus: weg')
        results.append(n0 > 0 and c1 == n0 and not sent)
        print('Fehler:', real(errs), real(errs2), real(dgerr))
        results.append(not real(errs) and not real(errs2) and not real(dgerr))
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_relcheck():
    """Companion 1.8.2 (with Credits Importer 3.17.3): the check on the MusicBrainz release page keeps its result.
    A) After "Enter edit" the release page checks the staged credits: ✓ on Discogs.
    B) Its next check (after 20 s) cannot read MusicBrainz (503): the marks stay ✓ – before, the unchecked marks (●) came
       back; it is tried again after 15 s and then reads MusicBrainz again (the check is newer).
    C) A page in a background tab beats only about once a minute: its status counts as alive for 75 s ("hidden"), the
       status of a visible page for 8 s as before."""
    import time

    MARKS = "[...document.querySelectorAll('.dci-dg-mark')].map(m => m.textContent)"
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
        dg, dgerr = H.open_discogs(ctx)
        pg, errs = H.open_mb_edit(ctx)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
        pg.click('[data-act=apply]')
        poll(dg, f"{MARKS}.includes('●')")
        staged = dg.evaluate(MARKS).count('●')
        H.submit_staged(pg)
        pg.goto(f'https://musicbrainz.org/release/{H.REL}')
        H.with_companion(pg)
        # A) checked: ✓
        poll(dg, f"(() => {{ const m = {MARKS}; return m.includes('✓') && !m.includes('●'); }})()", 30)
        a = dg.evaluate(MARKS)
        checked0 = H.STORE.data['statusMap'].get('checked')
        print('A) nach „Enter edit“:', a, '| vorgemerkt waren', staged)
        results.append(a.count('✓') >= 1 and '●' not in a)
        # B) the check after 20 s cannot read MusicBrainz
        H.WS_FAIL['release'] = 1
        t0 = time.time()
        while H.WS_FAIL.get('release', 0) > 0 and time.time() - t0 < 40:
            dg.wait_for_timeout(500)
        dg.wait_for_timeout(2500)
        b1 = dg.evaluate(MARKS)
        print('B) Prüfung ohne Antwort:', b1, '| nach', round(time.time() - t0), 's')
        poll(dg, f"(() => {{ const m = GM_getValue('statusMap'); return m && m.checked > {checked0}; }})()", 30)
        b2 = dg.evaluate(MARKS)
        print('   erneut versucht:', b2)
        results.append(H.WS_FAIL.get('release') == 0 and b1 == a and b2 == a)
        # C) a page in the background: its last beat counts for 75 s
        pg.close()
        poll(dg, f"{MARKS}.length === 0", 15)
        now = int(time.time() * 1000)
        H.STORE.set('statusBeat', {'pageId': f'release-{H.REL}', 'release': H.REL, 'ts': now - 30000, 'hidden': True})
        poll(dg, f"{MARKS}.length > 0", 10)
        c1 = len(dg.evaluate(MARKS))
        H.STORE.set('statusBeat', {'pageId': f'release-{H.REL}', 'release': H.REL, 'ts': now - 30000, 'hidden': False})
        poll(dg, f"{MARKS}.length === 0", 10)
        print('C) Hintergrund-Seite vor 30 s:', c1, 'Marken | sichtbare Seite vor 30 s: keine')
        results.append(c1 == len(a))
        print('Fehler:', real(errs), real(dgerr))
        results.append(not real(errs) and not real(dgerr))
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_trackmarks():
    """Status marks on Discogs for credits on track lines: one mark on each line, with the status of that track
    ("Written-By – Writer W" under tracks 1 and 2: two marks). On the release page each line is checked on its own:
    track 2's work is new in the editor and its link still open → ✗ there, ✓ on track 1; once the work is linked,
    ✓ on both."""
    WRITER = H.ARTISTS[3007][0]
    results = []


    def marks(dg):
        return dg.evaluate("""[...document.querySelectorAll('.dci-dg-mark')].filter(m => m.closest('[data-track-position]'))
      .map(m => [m.closest('[data-track-position]').dataset.trackPosition, m.textContent, m.closest('div, li').querySelector('a').textContent, m.title.slice(0, 40)])""")


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg, dgerr = H.open_discogs(ctx)
        pg, errs = H.open_mb_edit(ctx)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
        dg.wait_for_timeout(1500)
        m0 = marks(dg)
        print('1) vor dem Übernehmen (Track-Zeilen):', m0)
        ok1 = sorted((x[0], x[2]) for x in m0) == [('1', 'Writer W'), ('2', 'Writer W')] and all(x[1] == '○' for x in m0)
        # track 2 gets a new work in the editor; everything is staged
        pg.click('tr[data-work="1"] [data-act=work-pending]'); pg.wait_for_timeout(400)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        dg.wait_for_timeout(2000)
        m1 = marks(dg)
        print('2) nach Übernehmen:', m1)
        ok1 = ok1 and sorted(x[1] for x in m1) == ['●', '●'] and any(x[3].startswith('1:') for x in m1)
        results.append(ok1)
        H.submit_staged(pg)
        # the link of the new work (track 2) is still an open edit
        pg.goto(f'https://musicbrainz.org/release/{H.REL}')
        H.with_companion(pg)
        dg.wait_for_timeout(6000)
        m2 = dict((x[0], x[1]) for x in marks(dg))
        print('3) Release-Seite, Werk-Link von Track 2 noch offen:', m2)
        pg.close()
        # MusicBrainz linked the new work with its writer
        H.MB_EXTRA[H.REC[1]] = [{'target-type': 'work', 'type': 'performance', 'type-id': H.LTS[278]['gid'], 'attributes': [],
                                 'work': {'id': H.uid('cccccccc', 44), 'title': 'Song Two', 'relations': [
                                     {'target-type': 'artist', 'type': 'writer', 'type-id': H.LTS[167]['gid'], 'attributes': [], 'artist': {'id': WRITER, 'name': 'Writer W'}}]}}]
        dg.wait_for_timeout(9000)
        pr, _ = H.open_mb_release(ctx)
        dg.wait_for_timeout(6000)
        m3 = dict((x[0], x[1]) for x in marks(dg))
        print('4) Werk verknüpft:', m3)
        results.append(m2 == {'1': '✓', '2': '✗'} and m3 == {'1': '✓', '2': '✓'})
        print('Fehler:', errs, dgerr)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
