"""Companion on Discogs: marks switched by a click, the check on the release page, marks on track lines (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: keepmarks, relcheck, trackmarks – each the former smoke/t_<case>.py, unchanged –, trackcells (3.38.8), multi (3.38.9), [Companion 1.10.1] copymarks, [3.43.1] review43, [Companion 1.12.0] sitedark, [1.13.0] copymarks2; `python3 t_companion_discogs.py <case> …` runs only those."""
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
       status of a visible page for 8 s as before. [Companion 1.9.1] ten minutes in the background (collected item 105): a
       page in the background 5 minutes ago keeps the marks, one in front 30 seconds ago does not."""
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
        checked0 = H.STORE.data[f'statusMap:{H.REL}'].get('checked')  # [companion 1.10.0] per release
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
        poll(dg, f"(() => {{ const m = GM_getValue('statusMap:{H.REL}'); return m && m.checked > {checked0}; }})()", 30)
        b2 = dg.evaluate(MARKS)
        print('   erneut versucht:', b2)
        results.append(H.WS_FAIL.get('release') == 0 and b1 == a and b2 == a)
        # C) a page in the background: its last beat counts for 75 s; [Companion 1.9.1] ten minutes (collected item 105);
        #    [companion 1.10.0] a beat per page (statusBeat:<release>:<page>)
        pg.close()
        poll(dg, f"{MARKS}.length === 0", 15)
        now = int(time.time() * 1000)
        H.STORE.set(f'statusBeat:{H.REL}:release-{H.REL}', {'pageId': f'release-{H.REL}', 'release': H.REL, 'ts': now - 300000, 'hidden': True})
        poll(dg, f"{MARKS}.length > 0", 10)
        c1 = len(dg.evaluate(MARKS))
        H.STORE.set(f'statusBeat:{H.REL}:release-{H.REL}', {'pageId': f'release-{H.REL}', 'release': H.REL, 'ts': now - 30000, 'hidden': False})
        poll(dg, f"{MARKS}.length === 0", 10)
        print('C) Hintergrund-Seite vor 5 min:', c1, 'Marken | sichtbare Seite vor 30 s: keine')
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


def case_trackcells():
    """Companion 1.9.2 (Credits Importer 3.38.8; collected item 174, Discogs 2631299 "Boston Duets"): the tracklist
    is a table, tracks have credits of their own.
    A) Track 3 "Flute – Bass Man", "Composed By – Writer Z" and "Written-By – Bass*" (the same artist again): each mark on its own
       line, inside the title's cell – [companion 1.10.0] Written-By not before the title (the cell has every credit of the track).
    B) Track 1 has "Written-By – Writer W" on the page, Discogs (its data) also "Lyrics By" for Writer W there: no mark for it in
       the line of "Written-By" (until 1.9.1 a mark as the first child of the table row – a cell of its own, the columns shifted).
    C) No mark is a child of a table row; every row keeps its three cells, the title in the second."""
    orig_rel, orig_page = H.discogs_release, H.discogs_page

    def rel():
        d = orig_rel()
        ex = lambda name, role, i: {'name': name, 'anv': '', 'role': role, 'tracks': '', 'id': i, 'join': ''}
        d['tracklist'][0]['extraartists'].append(ex('Writer W', 'Lyrics By', 3007))
        d['tracklist'][2]['extraartists'].append(ex('Bass Man', 'Flute', 3001))
        d['tracklist'][2]['extraartists'].append(dict(ex('Bass Man', 'Written-By', 3001), anv='Bass'))
        return d

    def page():
        rows = ''
        for i, t in enumerate(H.TITLES):
            lines = []
            if i < 2:
                lines.append('<div>Written-By – <a href="/artist/3007-Writer-W">Writer W</a></div>')
            if i == 2:
                lines += ['<div>Flute – <a href="/artist/3001-Bass-Man">Bass Man</a></div>', '<div>Composed By – <a href="/artist/3009-Writer-Z">Writer Z</a></div>',
                          '<div>Written-By – <a href="/artist/3001-Bass-Man">Bass</a>*</div>']
            rows += f'<tr data-track-position="{i + 1}"><td>{i + 1}</td><td><span>{t}</span>{"".join(lines)}</td><td>3:00</td></tr>'
        html = orig_page()
        return html[:html.index('<section id="release-tracklist">')] + f'<section id="release-tracklist"><table>{rows}</table></section>' + html[html.index('<section id="release-credits">'):]

    H.discogs_release, H.discogs_page = rel, page
    TRACKS = """[...document.querySelectorAll('#release-tracklist tr')].map(tr => ({ pos: tr.dataset.trackPosition, cells: tr.children.length,
      tds: [...tr.children].every(c => c.tagName === 'TD'), second: tr.children[1] ? tr.children[1].querySelector('span') && tr.children[1].querySelector('span').textContent : '',
      marks: [...tr.querySelectorAll('.dci-dg-mark')].map(m => [m.parentElement.tagName, m.parentElement.textContent.replace(m.textContent, '').replace(/\\s+/g, ' ').trim()]) }))"""
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            dg, dgerr = H.open_discogs(ctx)
            pg, errs = H.open_mb_edit(ctx)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
            dg.wait_for_timeout(2500)
            t = dg.evaluate(TRACKS)
            for x in t:
                print('  ', x)
            in_row = dg.evaluate("[...document.querySelectorAll('.dci-dg-mark')].filter(m => m.parentElement.tagName === 'TR').length")
            t3 = next(x for x in t if x['pos'] == '3')
            t1 = next(x for x in t if x['pos'] == '1')
            ok_a = sorted(x[1] for x in t3['marks']) == ['Composed By – Writer Z', 'Flute – Bass Man', 'Written-By – Bass*'] and all(x[0] == 'DIV' for x in t3['marks'])
            ok_b = [x[1] for x in t1['marks']] == ['Written-By – Writer W']
            ok_c = in_row == 0 and all(x['cells'] == 3 and x['tds'] and x['second'] == H.TITLES[int(x['pos']) - 1] for x in t)
            print('A)', ok_a, '| B)', ok_b, '| C)', ok_c, '| Marken in Zeilen:', in_row)
            results += [ok_a, ok_b, ok_c]
            print('Fehler:', errs, dgerr)
            results.append(not errs and not dgerr)
            b.close()
    finally:
        H.discogs_release, H.discogs_page = orig_rel, orig_page
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_multi():
    """Companion 1.10.0 (Credits Importer 3.38.9; collected item 173): status and beat per release.
    A) The dashboard (its Discogs release in a tab): the marks there.
    B) Two more imports of other releases open (their editors send their status every 2 s, as a dashboard does): the marks on the
       Discogs tab stay for 10 s – never gone, never another number (until 1.9.2 they went off and on).
    C) Another import of the same Discogs release, used later: its marks (✓) and the note "2 imports of this release are open –
       …"; a click on a mark there does not reach the first dashboard; the first one used again (a click into it): its marks at
       once, a click on a mark reaches it (Skip); the other closed: no note (at once in a browser; in the test after its last
       beat ran out).
    D) The dashboard, opened 8 s after the page, says nothing about an old companion (1.10.0 sends its version with each status)."""
    OTHER = [H.uid('dededede', 1), H.uid('dededede', 2), H.uid('dededede', 3)]
    MARKS = "[...document.querySelectorAll('.dci-dg-mark')].map(m => m.textContent)"
    SEND = """(m) => { const send = (x) => document.dispatchEvent(new CustomEvent('dci:to-discogs', { detail: JSON.stringify(x) }));
      send(m); window.__t = setInterval(() => { send({ type: 'ping' }); send(Object.assign({}, m)); }, 2000); }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg, dgerr = H.open_discogs(ctx)
        pg, errs = H.open_mb_edit(ctx)
        pg.wait_for_selector('#dci-open', timeout=20000)
        # (the dashboard opened only after 8 s: the companion's version came with its status – no "older companion")
        pg.wait_for_timeout(8000)
        H.open_dashboard(pg)
        H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
        dg.wait_for_timeout(2500)
        a = dg.evaluate(MARKS)
        print('A) Marken:', len(a), sorted(set(a)))
        ok_a = len(a) > 3

        def fake(mbid, map_):
            fp = ctx.new_page()
            fp.route(f'https://musicbrainz.org/release/{mbid}/edit-relationships', lambda r: r.fulfill(body='<!doctype html><html><body><p>other import</p></body></html>', content_type='text/html'))
            fp.goto(f'https://musicbrainz.org/release/{mbid}/edit-relationships')
            H.with_companion(fp)
            fp.evaluate(SEND, map_)
            return fp

        base = {'type': 'status-map', 'enabled': True, 'artwork': True, 'labels': {}, 'texts': [], 'targets': [], 'keepOnRelease': False, 'toggle': True, 'keepAfterClose': False}
        f1 = fake(OTHER[0], dict(base, site='discogs', releaseId='4242', mbRelease=OTHER[0], items=[{'row': 'r1', 'artistId': 3001, 'role': 'Bass', 'base': 'Bass', 'positions': [], 'status': 'mb'}]))
        f2 = fake(OTHER[1], dict(base, site='bandcamp', releaseId='https://band.bandcamp.com/album/x', mbRelease=OTHER[1], items=[]))
        seen = []
        for _ in range(40):
            dg.wait_for_timeout(250)
            seen.append(len(dg.evaluate(MARKS)))
        print('B) Anzahl der Marken in 10 s:', sorted(set(seen)))
        ok_b = set(seen) == {len(a)}
        # C) the same Discogs release in another import, used later
        same = H.STORE.data[f'statusMap:{H.REL}']
        items = [dict(i, status='mb', byPos=[dict(x, status='mb') for x in (i.get('byPos') or [])] or None) for i in same['items']]
        f3 = fake(OTHER[2], dict(base, site='discogs', releaseId=str(same['releaseId']), mbRelease=OTHER[2], items=items, labels=same.get('labels', {})))
        dg.wait_for_timeout(4500)
        c1, note1 = dg.evaluate(MARKS), dg.evaluate("(document.getElementById('dci-multi') || {}).textContent || ''")
        LEVEL = "(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man'); const lv = g && g.querySelector('tr.dci-row [data-act=level][aria-pressed=true]'); return lv ? lv.dataset.level : null; })()"
        lv0 = pg.evaluate(LEVEL)
        # a click on a mark of the other import (Bass Man's): not this dashboard's
        dg.evaluate("[...document.querySelectorAll('#release-credits li')].find(l => l.textContent.includes('Bass Man')).querySelector('.dci-dg-mark').click()")
        dg.wait_for_timeout(1500)
        lv1 = pg.evaluate(LEVEL)
        pg.bring_to_front()
        pg.mouse.click(5, 5)
        dg.wait_for_timeout(2500)
        c2 = dg.evaluate(MARKS)
        # its own marks: a click reaches it (Bass Man to "Skip"), again: back
        dg.evaluate("[...document.querySelectorAll('#release-credits li')].find(l => l.textContent.includes('Bass Man')).querySelector('.dci-dg-mark').click()")
        dg.wait_for_timeout(1500)
        lv2 = pg.evaluate(LEVEL)
        dg.evaluate("[...document.querySelectorAll('#release-credits li')].find(l => l.textContent.includes('Bass Man')).querySelector('.dci-dg-mark').click()")
        dg.wait_for_timeout(1500)
        f3.close()
        # (in the test the page's last words while closing are lost – a synchronous request then is refused –: its beat runs out
        # after 8 s)
        dg.wait_for_timeout(11000)
        note3 = dg.evaluate("(document.getElementById('dci-multi') || {}).textContent || ''")
        print('C) anderer Import:', sorted(set(c1)), '|', note1, '| Klick dort, Bass Man hier:', lv0, '→', lv1, '\n   erster wieder benutzt:', sorted(set(c2)), '| Klick:', lv2,
              '| geschlossen, Hinweis:', repr(note3))
        ok_c = set(c1) == {'✓'} and len(c1) == len(a) and note1 == 'MB x Vibecode: 2 imports of this release are open – the marks are those of the one used last' \
            and lv1 == lv0 and sorted(c2) == sorted(a) and lv2 == 'skip' and note3 == ''
        old = pg.evaluate("[...document.querySelectorAll('#dci-log li')].some(li => /companion is older/.test(li.textContent))")
        ok_d = not old
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c, '| D)', ok_d)
        results += [ok_a, ok_b, ok_c, ok_d]
        f1.close(); f2.close()
        print('Fehler:', errs, dgerr)
        results.append(not errs and not dgerr)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_copymarks():
    """Companion 1.10.1 (collected item Z-CR): Discogs's data write "Copyright (c)" and "Phonographic Copyright (p)", its page
    "Copyright ©" and "Phonographic Copyright ℗" – the lines of the copyrights get their marks too (until 1.10.0 none), and a
    click on such a row in the dashboard shows its line on Discogs (not only the name).
    A) Sony with "Phonographic Copyright ℗" and "Copyright ©" on the page: a mark on each line, before the role.
    B) A click on the role of Sony's row "Copyright (c)": the line "Copyright © – Sony" highlighted."""
    MARK = """(r) => { const li = [...document.querySelectorAll('#release-credits li')].find(l => l.textContent.includes(r));
  const m = li && li.querySelector('.dci-dg-mark'); return m ? [m.textContent, li.firstChild === m] : null; }"""
    orig_page, orig_rel = H.discogs_page, H.discogs_release

    def page():
        return orig_page().replace('<li><span>Recorded At</span>', '<li><span>Copyright ©</span> – <a href="/label/1001-x">Sony</a></li><li><span>Recorded At</span>', 1)

    def rel():
        d = orig_rel()
        d['companies'].insert(1, {'name': 'Sony', 'entity_type_name': 'Copyright (c)', 'id': 1001, 'catno': ''})
        return d
    H.discogs_page, H.discogs_release = page, rel
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            dg, dgerr = H.open_discogs(ctx)
            pg, errs = H.open_mb_edit(ctx)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
            for _ in range(100):
                if dg.evaluate(f"({MARK})('Bass Man')"):
                    break
                dg.wait_for_timeout(200)
            dg.wait_for_timeout(1200)
            a = {r: dg.evaluate(f"({MARK})('{r}')") for r in ('Phonographic Copyright ℗', 'Copyright © –', 'Recorded At')}
            print('A) Marken:', a)
            results.append(all(v and v[1] for v in a.values()))
            rid = pg.evaluate("""() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Sony');
              const tr = g && [...g.querySelectorAll('tr.dci-row')].find(t => t.querySelector('.dci-drole').dataset.raw.trim() === 'Copyright (c)'); return tr ? tr.dataset.row : null; }""")
            pg.locator(f'tr[data-row="{rid}"] .dci-drole').click()
            for _ in range(60):
                if dg.evaluate("!!document.querySelector('.dci-discogs-highlight')"):
                    break
                dg.wait_for_timeout(200)
            hl = dg.evaluate("(h => h ? [h.tagName, h.textContent.replace(/\\s+/g, ' ').trim()] : null)(document.querySelector('.dci-discogs-highlight'))")
            print('B) Zeile:', rid, hl)
            results.append(bool(hl) and hl[0] == 'LI' and 'Copyright © – Sony' in hl[1] and 'Phonographic' not in hl[1])
            real = [e for e in errs + dgerr if 'Synchronous XHR in page dismissal' not in e]
            print('Fehler:', real)
            results.append(not real)
            b.close()
    finally:
        H.discogs_page, H.discogs_release = orig_page, orig_rel
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_review43():
    """Credits Importer 3.43.1 / Companion 1.11.1 (full review, package P2).
    A) A Discogs tab in the background (its beat throttled by the browser – 30 s old, "visible: false") still counts as open:
       "connected" (until 1.11.0 a tab was "closed" after 7 s).
    B) The result of a jump another dashboard sent (an id this tab never sent) is not shown nor logged (the companion relays
       results to every open dashboard).
    C) The editor "Count exactly" opens in the background (#dci-count) sends no marks to the Discogs tab: no status map of the
       release in the shared storage after its import (until 3.43.0 it replaced the marks of the editor you work in)."""
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    SYNC = "document.querySelector('[data-el=sync]').textContent"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 90)
        pg.wait_for_timeout(2500)
        a0 = pg.evaluate(SYNC)
        # A) a tab of the Discogs release, last beat 30 s ago, in the background
        pg.evaluate(f"""() => GM_setValue('tab:fake30', {{ id: 'fake30', site: 'discogs', ts: Date.now() - 30000, visible: false, lastVisible: Date.now() - 30000,
          releaseId: '{H.DISCOGS_ID}', releaseIds: ['{H.DISCOGS_ID}'] }})""")
        try:
            H.wait_for(pg, f"/connected/.test({SYNC})", 15)
        except Exception:
            pass
        a1 = pg.evaluate(SYNC)
        print('A) ohne Tab:', a0, '| Tab im Hintergrund, 30 s alt:', a1)
        results.append('no Discogs tab' in a0 and 'connected' in a1)
        # B) a result of a jump of another dashboard
        n0 = len(pg.evaluate(LOGS))
        pg.evaluate("document.dispatchEvent(new CustomEvent('dci:from-discogs', { detail: JSON.stringify({ type: 'result', id: 'other:c7', found: 'credit' }) }))")
        pg.wait_for_timeout(800)
        b1 = [x for x in pg.evaluate(LOGS)[n0:] if 'Discogs view' in x]
        b2 = pg.evaluate(SYNC)
        print('B) fremdes Ergebnis – Protokoll:', b1, '| Anzeige:', b2)
        results.append(not b1 and 'credit highlighted' not in b2)
        pg.evaluate("GM_deleteValue('tab:fake30')")
        # C) the count tab: its import, then no status map of the release
        pg.evaluate("[...GM_listValues()].filter(k => k.startsWith('statusMap:')).forEach(k => GM_deleteValue(k))")
        ct = ctx.new_page()
        cerrs = H.errors_of(ct)
        ct.goto(f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
        ct.evaluate(f"localStorage.setItem('dci-gap-count:{H.REL.lower()}', JSON.stringify({{ at: Date.now(), links: [{{ source: 'discogs', id: {H.DISCOGS_ID} }}] }}))")
        ct.goto(f'https://musicbrainz.org/release/{H.REL}/edit-relationships#dci-count')
        ct.evaluate(H.VIEW_PRESET, 'full')
        H.with_companion(ct)
        ct.add_script_tag(content=H.MAIN)
        H.wait_for(ct, f"{LOGS}.some(x => /Import complete/.test(x))", 90)
        ct.wait_for_timeout(4000)
        c1 = ct.evaluate(f"[...GM_listValues()].filter(k => k === 'statusMap:{H.DISCOGS_ID}')")
        c2 = [x for x in ct.evaluate(LOGS) if 'Count exactly' in x]
        print('C) Zähl-Tab – Marken im Speicher:', c1, '| Start:', c2[:1], '| Fehler:', errs, cerrs)
        results.append(not c1 and len(c2) == 1 and not errs and not cerrs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_sitedark():
    """Companion 1.12.0 (Credits Importer 3.46.0, collected item Z-DM; Q-eg): the marks follow the dark theme of each site.
    Discogs: a dark background of the page (as a dark-mode extension or Discogs' own theme) → html.dci-site-dark, the mark "skip"
    dark grey with light text; back to white → light again; data-theme="dark" on html → dark. YouTube: html[dark] → dark (live).
    Review of 1.12.0: a near-white oklch() background, a class "header-dark", data-theme="darkblue-light" – light; data-theme taken away
    – light again."""
    results = []
    MARK = """(() => { let m = document.getElementById('t-mark'); if (!m) { m = document.createElement('span'); m.id = 't-mark'; m.className = 'dci-dg-mark dci-dg-skip'; m.textContent = '○'; document.body.appendChild(m); }
      const cs = getComputedStyle(m); return [document.documentElement.classList.contains('dci-site-dark'), cs.backgroundColor, cs.color]; })()"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg, dgerr = H.open_discogs(ctx)
        dg.wait_for_timeout(1200)
        a = dg.evaluate(MARK)
        dg.evaluate("document.body.style.background = '#181818'")
        dg.wait_for_timeout(400)
        b1 = dg.evaluate(MARK)
        dg.evaluate("document.body.style.background = '#ffffff'")
        dg.wait_for_timeout(400)
        c = dg.evaluate(MARK)
        dg.evaluate("document.body.style.background = ''; document.documentElement.setAttribute('data-theme', 'dark')")
        dg.wait_for_timeout(400)
        d = dg.evaluate(MARK)
        print('Discogs: hell', a, '| dunkler Hintergrund', b1, '| weiß', c, '| data-theme', d)
        results.append(a == [False, 'rgb(196, 196, 196)', 'rgb(51, 51, 51)'] and b1 == [True, 'rgb(92, 90, 102)', 'rgb(236, 235, 242)'] and not c[0] and d[0] and not dgerr)
        fp = []
        for js in ("document.documentElement.removeAttribute('data-theme')", "document.body.style.background = 'oklch(0.985 0 0)'",
                   "document.body.style.background = ''; document.body.classList.add('header-dark')",
                   "document.body.classList.remove('header-dark'); document.documentElement.setAttribute('data-theme', 'darkblue-light')",
                   "document.documentElement.setAttribute('data-theme', 'theme-dark')"):
            dg.evaluate(js)
            dg.wait_for_timeout(400)
            fp.append(dg.evaluate(MARK)[0])
        print('Discogs: ohne data-theme, oklch fast weiß, header-dark, darkblue-light, theme-dark:', fp)
        results.append(fp == [False, False, False, False, True])
        yt, yterr = H.open_youtube(ctx, 'https://www.youtube.com/watch?v=Dy-ChUlAg9B')
        yt.wait_for_timeout(1500)
        y0 = yt.evaluate("document.documentElement.classList.contains('dci-site-dark')")
        yt.evaluate("document.documentElement.setAttribute('dark', '')")
        yt.wait_for_timeout(400)
        y1 = yt.evaluate("document.documentElement.classList.contains('dci-site-dark')")
        print('YouTube: hell', y0, '| html[dark]', y1, '| Fehler', yterr)
        results.append(y0 is False and y1 is True and not yterr)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_copymarks2():
    """Companion 1.13.0 (Credits Importer 3.48.0, collected item Z-MCP; Q-ex): text copied from the page comes without the marks –
    a line of the credits with its mark "○" selected and copied: the text (plain and HTML) has no mark, the page keeps it; the mark
    cannot be selected (user-select: none).
    Review of 1.13.0: several lines with marks – each line kept, no mark; text hidden on the page stays out; a selection without marks
    is copied by the browser as always (not taken over); the links of the HTML with their whole addresses."""
    COPY = """(() => { const li = document.querySelector('#release-credits li'); const m = document.createElement('span'); m.className = 'dci-dg-mark dci-dg-open'; m.textContent = '○'; li.prepend(m);
      const r = document.createRange(); r.selectNodeContents(li); const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
      const dt = new DataTransfer(); const ev = new ClipboardEvent('copy', { clipboardData: dt, bubbles: true, cancelable: true }); document.dispatchEvent(ev);
      return [dt.getData('text/plain').trim(), dt.getData('text/html').includes('dci-dg-mark'), ev.defaultPrevented, getComputedStyle(m).userSelect, li.textContent.includes('○'), li.textContent.replace('○', '').replace(/\\s+/g, ' ').trim()]; })()"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg, dgerr = H.open_discogs(ctx)
        dg.wait_for_timeout(1200)
        c = dg.evaluate(COPY)
        MORE = """(() => { const ul = document.querySelector('#release-credits ul') || document.querySelector('#release-credits'); const lis = [...ul.querySelectorAll('li')].slice(0, 3);
          lis.forEach((li) => { if (!li.querySelector('.dci-dg-mark')) { const m = document.createElement('span'); m.className = 'dci-dg-mark dci-dg-mb'; m.textContent = '✓'; li.prepend(m); } });
          const hid = document.createElement('span'); hid.textContent = 'HIDDEN'; hid.style.display = 'none'; lis[1].appendChild(hid);
          const copy = (node) => { const r = document.createRange(); r.selectNodeContents(node); const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
            const dt = new DataTransfer(); const ev = new ClipboardEvent('copy', { clipboardData: dt, bubbles: true, cancelable: true }); document.dispatchEvent(ev); return [dt.getData('text/plain'), dt.getData('text/html'), ev.defaultPrevented]; };
          const a = copy(ul);
          const plain = document.createElement('p'); plain.textContent = 'No marks here'; document.body.appendChild(plain);
          const b = copy(plain);
          return { lines: a[0].split('\\n').map((x) => x.trim()).filter(Boolean).length, marks: /[○✓●]/.test(a[0]), hidden: a[0].includes('HIDDEN'), abs: /href="https:\\/\\//.test(a[1]), rel: /href="\\//.test(a[1]), plainTaken: b[2] }; })()"""
        m = dg.evaluate(MORE)
        print('Kopiert:', c, '| mehrere Zeilen:', m, '| Fehler:', dgerr)
        ok = c[0] == c[5] and '○' not in c[0] and c[1] is False and c[2] is True and c[3] == 'none' and c[4] is True \
            and m['lines'] >= 3 and not m['marks'] and not m['hidden'] and m['abs'] and not m['rel'] and m['plainTaken'] is False and not dgerr
        b.close()
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


run_cases(globals())
