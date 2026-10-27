"""Dates & tracks: the date matrix, dragging dates and track groups, the pools (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: matrix, dragdates, pools, poolsmx, tracksdrop – each the former smoke/t_<case>.py, unchanged; `python3 t_dates_matrix.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_matrix():
    """Date matrix by hand: drag a date into a column and a track group onto it, apply; the click alternative
    (grip, then "place here"); the cell editor (column, track groups); moving a cell; a date with track groups
    in the matrix dropped onto a row; "apply automatically"; the matrix is still there after a reload."""
    import re
    import zooid
    from common_rows import lib, cells, stage

    zooid.setup('No dates here.')
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        head = lambda: re.sub(r'\s+', ' ', pg.locator('.dci-pools-head').inner_text())
        print('Ohne Daten eingeklappt:', pg.locator('.dci-pools-toggle').get_attribute('aria-expanded'), '|', head())
        pg.click('.dci-pools-toggle'); pg.wait_for_timeout(150)

        def new_date(name, y, m, d):
            pg.click('[data-act=pool-new]')
            pg.fill('[data-f=pf-name]', name); pg.fill('[data-f=pf-by]', y); pg.fill('[data-f=pf-bm]', m); pg.fill('[data-f=pf-bd]', d)
            pg.click('[data-act=pf-copy]')
            pg.click('[data-act=pool-save]'); pg.wait_for_timeout(200)

        def new_group(name, tracks):
            pg.click('[data-act=tg-new]')
            if name:
                pg.fill('[data-f=tg-name]', name)
            for i in tracks:
                pg.check(f'[data-f=tg-track][data-i="{i - 1}"]')
            pg.click('[data-act=tg-save]'); pg.wait_for_timeout(200)
        new_date('Session A', '2025', '06', '25')
        new_date('Overdub', '2025', '07', '02')
        new_group('', [1, 2, 3, 4, 5])
        new_group('Overdubs', [7, 8])
        ids = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => c.dataset.id)")
        tgs = pg.evaluate("[...document.querySelectorAll('.dci-pchip-tg')].map(c => c.dataset.id)")
        # 1) drag & drop: "Session A" into Performance, "Tracks 1–5" onto it
        pg.drag_and_drop(f'.dci-pchip-date[data-id="{ids[0]}"]', '[data-dmdrop=performance]'); pg.wait_for_timeout(200)
        pg.drag_and_drop(f'.dci-pchip-tg[data-id="{tgs[0]}"]', '.dci-dm-col[data-dmcol=performance] .dci-dm-cell'); pg.wait_for_timeout(200)
        print('1) nach Ziehen:', cells(pg)['performance'], '| Hinweis:', pg.locator('.dci-dm-foot .dci-dm-pending').count())
        ok1 = cells(pg)['performance'] == [['Session A · 2025-06-25', ['Tracks 1–5'], False]] and lib(pg)[0][1] == ''
        pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(400)
        print('   nach „Anwenden“ – Liberty:', lib(pg))
        ok1 = ok1 and lib(pg) == [([1, 2, 3, 4, 5], '2025-06-25'), ([6, 7, 8, 9, 10], '')]
        # 2) click alternative: grip of "Overdub", then "place here" in Mix; grip of "Overdubs", then "tracks here"
        pg.click(f'.dci-pchip-date[data-id="{ids[1]}"] [data-act=dm-pick]'); pg.wait_for_timeout(150)
        focus = pg.evaluate("document.activeElement.dataset.act + ':' + (document.activeElement.dataset.col || '')")
        pg.click('[data-act=dm-drop-here][data-col=mix]'); pg.wait_for_timeout(150)
        pg.click(f'.dci-pchip-tg[data-id="{tgs[1]}"] [data-act=dm-pick]'); pg.wait_for_timeout(150)
        pg.locator('.dci-dm-col[data-dmcol=mix] [data-act=dm-drop-here]').click(); pg.wait_for_timeout(150)
        print('2) per Klick: Fokus danach', focus, '| Mix:', cells(pg)['mix'])
        ok2 = focus == 'dm-drop-here:performance' and cells(pg)['mix'] == [['Overdub · 2025-07-02', ['Overdubs'], False]]
        # 3) the editor moves "Overdub" to Performance (select), a cell is moved back by dragging
        pg.locator('.dci-dm-col[data-dmcol=mix] [data-act=dm-edit]').first.click(); pg.wait_for_timeout(150)
        pg.select_option('.dci-dm-editor [data-f=dm-col]', 'performance'); pg.wait_for_timeout(200)
        print('3) Editor → Performance:', cells(pg)['performance'])
        ok3 = len(cells(pg)['performance']) == 2 and cells(pg)['mix'] == []
        pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(400)
        print('   Liberty (Overdub auf 7–8 dazu):', lib(pg))
        ok3 = ok3 and sorted(lib(pg)) == sorted([([1, 2, 3, 4, 5], '2025-06-25'), ([6, 9, 10], ''), ([7, 8], '2025-07-02')])
        cell = pg.evaluate("document.querySelectorAll('.dci-dm-col[data-dmcol=performance] .dci-dm-cell')[1].dataset.id")
        pg.drag_and_drop(f'.dci-dm-cell[data-id="{cell}"]', '[data-dmdrop=mastering]'); pg.wait_for_timeout(200)
        ok3 = ok3 and len(cells(pg)['mastering']) == 1
        print('   gezogen nach Mastering:', cells(pg)['mastering'])
        # 4) "apply automatically": the change goes onto the rows at once
        pg.check('[data-f=dm-auto]'); pg.wait_for_timeout(400)
        print('4) automatisch an – Liberty:', lib(pg), '| noch offen:', pg.locator('.dci-dm-foot .dci-dm-pending').count())
        ok4 = sorted(lib(pg)) == sorted([([1, 2, 3, 4, 5], '2025-06-25'), ([6, 7, 8, 9, 10], '')])
        pg.locator('.dci-dm-col[data-dmcol=performance] [data-act=dm-tg-remove]').first.click(); pg.wait_for_timeout(400)
        print('   Track-Gruppe weg → Session A für alle:', lib(pg))
        ok4 = ok4 and lib(pg) == [(list(range(1, 11)), '2025-06-25')]
        pg.uncheck('[data-f=dm-auto]')
        # 5) a date with track groups in the row's column dropped onto a row: only on those tracks
        pg.drag_and_drop(f'.dci-pchip-tg[data-id="{tgs[0]}"]', '.dci-dm-col[data-dmcol=performance] .dci-dm-cell'); pg.wait_for_timeout(200)
        pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(300)
        grp = pg.locator('.dci-group').filter(has=pg.locator('.dci-gname strong', has_text='Henry Threadgill')).first
        rows_before = lib(pg, 'Henry Threadgill')
        grp.locator('tr.dci-row').nth(1).locator('.dci-c-date').scroll_into_view_if_needed()
        pg.drag_and_drop(f'.dci-pchip-date[data-id="{ids[0]}"]', '.dci-group:has(.dci-gname strong:text("Henry Threadgill")) tr.dci-row >> nth=1 >> .dci-c-date'); pg.wait_for_timeout(300)
        warn = [m for m in pg.locator('.dci-msg').all_inner_texts() if 'none of the tracks' in m]
        print('5) „Session A“ auf Zeile 6–10 gezogen:', warn[-1][:80] if warn else 'keine Meldung', '| unverändert:', lib(pg, 'Henry Threadgill') == rows_before)
        ok5 = bool(warn) and lib(pg, 'Henry Threadgill') == rows_before
        stage(pg)
        staged = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0.name === 'Liberty Ellman').map(r => r.entity1.name.replace('Piece ', '#') + (r.begin_date ? ' ' + r.begin_date.month + '-' + r.begin_date.day : ''))")
        print('   Liberty vorgemerkt:', sorted(staged, key=lambda x: int(x.split()[0][1:])))
        # 6) after a reload the matrix is still there; the folding is remembered
        pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open'); pg.wait_for_selector('.dci-dm-cell', timeout=30000); pg.wait_for_timeout(300)
        print('6) nach Neuladen:', {k: v for k, v in cells(pg).items() if v}, '| offen:', pg.locator('.dci-pools-toggle').get_attribute('aria-expanded'))
        ok6 = cells(pg)['performance'] == [['Session A · 2025-06-25', ['Tracks 1–5'], False]] and len(cells(pg)['mastering']) == 1
        print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4, ok5, ok6]) and len(staged) == 10 else 'FEHLER', [ok1, ok2, ok3, ok4, ok5, ok6], '| Fehler:', errs)
        b.close()


def case_dragdates():
    """Pool dates by drag & drop (the stamp is gone): onto the date field of a row (also one with a date of its own),
    onto the column date and a cell of the works matrix; a date onto another date makes a period (pool and matrix);
    all dates of the Discogs notes go into the pool; cleared pools come back when the release is opened again;
    "load again from Discogs" (with and without the dates made by hand); "Cover Art" keeps "cover art" as wording."""
    H.RULES_OFF = ['D022']  # [3.32.0] about the period and "choose": without D022 (what the days have in common at once)
    import re
    from common_rows import cells, drag, date_field

    orig = H.discogs_release


    def rel():
        d = orig()
        # (a year without a word naming its group; [3.28.5] "Originally released 1975" is a release year now and left out, D018)
        d['notes'] = 'Dedicated to the band, 1975.\n' + d['notes']
        d['extraartists'].append({'name': 'Photo Guy', 'anv': '', 'role': 'Cover Art', 'tracks': '', 'id': 3006, 'join': ''})
        return d


    H.discogs_release = rel
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(300)
        chips = lambda: [re.sub(r'\s+', ' ', c) for c in pg.locator('.dci-pchip-date .dci-chip-main').all_inner_texts()]
        ids = lambda: pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => c.dataset.id)")
        idof = lambda text: pg.evaluate(f"[...document.querySelectorAll('.dci-pchip-date')].find(c => c.querySelector('.dci-chip-main').textContent.trim().startsWith({text!r})).dataset.id")
        row = lambda name: pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text=name)).first.locator('tr.dci-row').first
        dcell = lambda name: f'tr[data-row="{row(name).get_attribute("data-row")}"] .dci-c-date'
        val = lambda name, f: date_field(row(name), f)
        msgs = [m[:90] for m in pg.locator('.dci-msg').all_inner_texts()]
        print('1) Pool:', chips(), '| Meldungen:', msgs)
        ok1 = len(chips()) == 4 and any('1975' in c for c in chips()) and any(c.startswith('Performance 1 (month) · 2001-03') for c in chips()) \
            and any('no word naming' in m for m in msgs) and pg.locator('[data-act=pool-stamp]').count() == 0
        # 2) onto a row with a date of its own: replaced
        row('Guitar Guy').locator('[data-act=date-open]').click(); pg.keyboard.type('1999'); pg.wait_for_timeout(300)
        perf = idof('Performance 1 ·')
        drag(pg, f'.dci-pchip-date[data-id="{perf}"] .dci-chip-main', dcell('Guitar Guy'))
        pg.drag_and_drop(f'.dci-pchip-date[data-id="{perf}"]', dcell('Keys Guy')); pg.wait_for_timeout(300)
        print('2) Guitar Guy:', val('Guitar Guy', 'rd-by'), val('Guitar Guy', 'rd-bm'), val('Guitar Guy', 'rd-bd'), '| Keys Guy:', val('Keys Guy', 'rd-by'), val('Keys Guy', 'rd-bm'))
        ok2 = (val('Guitar Guy', 'rd-by'), val('Guitar Guy', 'rd-bm'), val('Guitar Guy', 'rd-bd')) == ('2001', '03', '01') and val('Keys Guy', 'rd-bm') == '03'
        # 3) works matrix: column date and the date of a cell
        head = pg.locator('[data-colhead] .dci-mx-card').first
        head.scroll_into_view_if_needed()
        # a pool date dropped onto the head of a column: the column date (its fields are in the ▾ menu)
        pg.drag_and_drop(f'.dci-pchip-date[data-id="{perf}"]', '[data-colhead] .dci-mx-card >> nth=0'); pg.wait_for_timeout(400)
        chip = pg.locator('[data-colhead] .dci-mx-datechip').first.inner_text() if pg.locator('[data-colhead] .dci-mx-datechip').count() else ''
        pg.locator('[data-colhead] [data-act=mx-colmenu]').first.click(); pg.wait_for_timeout(300)
        cd = pg.locator('[data-colhead] [data-f=cd-by]').first.input_value()
        pg.locator('[data-colhead] [data-act=mx-colmenu]').first.click(); pg.wait_for_timeout(200)
        print('   Datum im Spaltenkopf:', chip)
        on = pg.locator('.dci-mx-cell.dci-mx-on').first
        mix = idof('Mix 1')
        pg.drag_and_drop(f'.dci-pchip-date[data-id="{mix}"]', '.dci-mx-cell.dci-mx-on >> nth=0'); pg.wait_for_timeout(400)
        own = pg.locator('.dci-mx-cell.dci-mx-on sup').count()
        print('3) Spaltendatum Jahr:', cd, '| Zellen mit eigenem Datum (⌚):', own)
        ok3 = cd == '2001' and own >= 1
        # 4) a date onto another date in the pool: a period of both
        pg.drag_and_drop(f'.dci-pchip-date[data-id="{mix}"]', f'.dci-pchip-date[data-id="{perf}"]'); pg.wait_for_timeout(300)
        print('4) Pool nach Zusammenziehen:', chips())
        ok4 = any('2001-03-01 – 2001-05' in c and '+' in c for c in chips()) and len(chips()) == 5
        # 5) in the matrix: "Mix 1" (cell) onto "Performance 1" (cell) → one cell with the period, the mix cell goes
        perf_cell = pg.locator('.dci-dm-col[data-dmcol=performance] .dci-dm-cell').first
        pg.drag_and_drop('.dci-dm-col[data-dmcol=mix] .dci-dm-cell', '.dci-dm-col[data-dmcol=performance] .dci-dm-cell .dci-dm-date'); pg.wait_for_timeout(300)
        print('5) Matrix:', {k: v for k, v in cells(pg).items() if v}, '| Pool:', len(chips()))
        ok5 = cells(pg)['mix'] == [] and cells(pg)['performance'][0][0].endswith('2001-03-01 – 2001-05') and len(chips()) == 5
        # 6) cleared pools come back when the release is opened again
        pg.click('[data-act=pool-clear][data-what=dates]'); pg.click('[data-act=pool-clear-do]'); pg.wait_for_timeout(200)
        pg.click('[data-act=pool-clear][data-what=tracks]') if pg.locator('[data-act=pool-clear][data-what=tracks]:not([disabled])').count() else None
        if pg.locator('[data-act=pool-clear-do]').count():
            pg.click('[data-act=pool-clear-do]')
        print('6) geleert:', len(chips()))
        pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open'); pg.wait_for_selector('.dci-pchip-date', timeout=30000); pg.wait_for_timeout(600)
        print('   nach Neuladen der Seite:', chips(), '| Matrix:', {k: len(v) for k, v in cells(pg).items() if v})
        ok6 = len(chips()) == 4 and len(cells(pg)['performance']) == 1 and len(cells(pg)['mix']) == 1
        # 7) "load again from Discogs": own dates stay unless ticked
        pg.click('[data-act=pool-new]'); pg.fill('[data-f=pf-name]', 'Mine'); pg.fill('[data-f=pf-by]', '2003'); pg.click('[data-act=pf-copy]'); pg.click('[data-act=pool-save]'); pg.wait_for_timeout(200)
        pg.locator('.dci-dm-col[data-dmcol=mix] [data-act=dm-remove]').first.click(); pg.wait_for_timeout(150)
        pg.click('[data-act=pool-clear][data-what=reload]'); pg.wait_for_timeout(100)
        print('7) Rückfrage:', re.sub(r'\s+', ' ', pg.locator('.dci-pool-clear').inner_text())[:160])
        pg.click('[data-act=pool-reload-do]'); pg.wait_for_timeout(300)
        after1 = (chips(), {k: len(v) for k, v in cells(pg).items() if v})
        pg.click('[data-act=pool-clear][data-what=reload]'); pg.check('[data-f=pool-reload-all]'); pg.click('[data-act=pool-reload-do]'); pg.wait_for_timeout(300)
        after2 = chips()
        print('   neu geladen:', after1, '| mit „auch eigene“:', after2)
        ok7 = len(after1[0]) == 5 and any('Mine' in c for c in after1[0]) and after1[1].get('mix') == 1 and len(after2) == 4 and not any('Mine' in c for c in after2)
        # 8) "Cover Art": artwork with the wording "cover art"
        pg.click('[data-act=rules]'); pg.wait_for_timeout(200)
        pg.fill('#dci-rules [data-rf=test]', 'Cover Art'); pg.wait_for_timeout(200)
        res = re.sub(r'\s+', ' ', pg.locator('#dci-rules [data-rf=result]').inner_text())
        print('8) Regeltest „Cover Art“:', res[:220])
        ok8 = 'cover art' in res.lower().replace('cover art', 'X', 1).lower() or res.lower().count('cover art') >= 2
        print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8]) else 'FEHLER', [ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8], '| Fehler:', errs)
        b.close()


def case_pools():
    """Dates & tracks as one block: open when dates were found, folded state remembered; clearing all track
    groups (dates in the matrix become dashed suggestions for all tracks) and all dates (also of other
    releases), rows keep their dates as their own; the list of created works stays."""
    import re
    import zooid
    from common_rows import lib, cells

    zooid.setup(zooid.NOTES_TWO_DAYS)
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.evaluate("""() => { localStorage.setItem('dci-date-pool:other', '[{"id":"d1","name":"X","begin":{"year":1999},"end":{"year":1999},"ended":true}]');
      localStorage.setItem('dci-date-matrix:other', '{"cells":[],"found":"x"}'); localStorage.setItem('dci-track-pool:other', '[{"id":"t1","name":"T","tracks":[0]}]');
      localStorage.setItem('dci-created-works:other', '[{"i":0,"gid":"g"}]'); }""")
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(300)
        store = lambda: pg.evaluate("Object.keys(localStorage).filter(k => k.endsWith(':other')).sort()")
        print('1) offen (Daten gefunden):', pg.locator('.dci-pools-toggle').get_attribute('aria-expanded'))
        ok1 = pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') == 'true'
        pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
        applied = lib(pg)
        # 2) all track groups go: the dates stay in the matrix, dashed, for all tracks; rows keep their dates
        pg.click('[data-act=pool-clear][data-what=tracks]'); pg.wait_for_timeout(150)
        print('2) Rückfrage:', re.sub(r'\s+', ' ', pg.locator('.dci-pool-clear').inner_text())[:200])
        pg.click('[data-act=pool-clear-do]'); pg.wait_for_timeout(300)
        print('   Matrix:', cells(pg)['performance'], '| Meldung:', [m[:70] for m in pg.locator('.dci-msg').all_inner_texts() if 'track groups' in m])
        print('   Liberty:', lib(pg), '| Speicher anderer Releases:', store())
        ok2 = all(c[2] and not c[1] for c in cells(pg)['performance']) and lib(pg) == applied and 'dci-track-pool:other' in store()
        # 3) all dates go, also those of other releases; rows keep their dates; "Apply" leaves them alone
        pg.click('[data-act=pool-clear][data-what=dates]'); pg.wait_for_timeout(150)
        print('3) Rückfrage:', re.sub(r'\s+', ' ', pg.locator('.dci-pool-clear').inner_text())[:220])
        pg.check('[data-f=pool-clear-all]')
        pg.click('[data-act=pool-clear-do]'); pg.wait_for_timeout(300)
        print('   Pool:', pg.locator('.dci-pchip-date').count(), '| Matrix:', sum(len(v) for v in cells(pg).values()), '| Speicher anderer Releases:', store())
        pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(300)
        print('   Liberty nach „Anwenden“ mit leerer Matrix:', lib(pg))
        ok3 = pg.locator('.dci-pchip-date').count() == 0 and lib(pg) == applied and store() == ['dci-created-works:other', 'dci-track-pool:other']
        # 4) folded: one line with the counts; remembered after a reload
        pg.click('.dci-pools-toggle'); pg.wait_for_timeout(150)
        print('4) eingeklappt:', re.sub(r'\s+', ' ', pg.locator('.dci-pools-head').inner_text()), '| Matrix sichtbar:', pg.locator('.dci-dm').count())
        ok4 = pg.locator('.dci-dm').count() == 0
        pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open'); pg.wait_for_selector('.dci-pools-head', timeout=30000); pg.wait_for_timeout(1500)
        print('   nach Neuladen offen?', pg.locator('.dci-pools-toggle').get_attribute('aria-expanded'))
        ok4 = ok4 and pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') == 'false'
        print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4]) else 'FEHLER', [ok1, ok2, ok3, ok4], '| Fehler:', errs)
        b.close()


def case_poolsmx():
    """Credits Importer 3.30.3: the date pool and the track pool fold on their own, scroll bars of the works matrix
    (collected items 93, 94; 2026-10-25).
    A) "Dates & tracks" folded with "keep the pools in the bar": "▾ Date pool" folds the date pool in – "▸ Date pool (3)",
       no chips, stored; the track pool stays; after reloading still folded; "▸ Date pool" shows it again (nothing stored).
    B) Open block: the same button folds the track pool there ("▸ Track pool (1)"), and shows it again.
    C) Works matrix, 1000 px wide: a scroll bar above the matrix (it is wider than the window); moving it moves the matrix,
       moving the matrix moves it. The lower edge of the matrix out of view: a second bar at the bottom of the visible
       area (at its very lower edge, [3.30.5]); the lower edge in view: no second bar."""
    KEPT = """(() => { const b = document.querySelector('[data-el=dates]'); const lab = (sel) => { const x = b.querySelector(sel + ' [data-act=pool-fold]'); return x ? x.textContent.replace(/\\s+/g, ' ').trim() : null; };
  return { dates: lab('.dci-pool-dates'), tracks: lab('.dci-tracks-bar'), dchips: b.querySelectorAll('.dci-pchip-date').length, tchips: b.querySelectorAll('.dci-pchip-tg').length,
    stored: localStorage.getItem('dci-pool-fold') }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.set_viewport_size({'width': 1000, 'height': 700})
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        # a track group, so that both pools have chips
        pg.evaluate(f"localStorage.setItem('dci-track-pool:{H.REL}', JSON.stringify([{{ id: 'tg1', name: 'Side A', tracks: [0, 1] }}]))")
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "document.querySelector('.dci-pools-toggle') && document.querySelector('.dci-mx-wrap')", 60)
        pg.wait_for_timeout(800)
        st = lambda: pg.evaluate(KEPT)
        # A) the folded block with the kept pools
        if pg.evaluate("document.querySelector('.dci-pools-toggle').getAttribute('aria-expanded')") == 'true':
            pg.click('.dci-pools-toggle')
            pg.wait_for_timeout(300)
        a0 = st()
        pg.click('[data-el=dates] .dci-pool-dates [data-act=pool-fold]')
        pg.wait_for_timeout(300)
        a1 = st()
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "document.querySelector('.dci-pools-toggle')", 60)
        pg.wait_for_timeout(800)
        a2 = st()
        pg.click('[data-el=dates] .dci-pool-dates [data-act=pool-fold]')
        pg.wait_for_timeout(300)
        a3 = st()
        print('A) Leiste:', a0, '\n   Date pool zu:', a1, '\n   neu geladen:', a2, '\n   wieder auf:', a3)
        results.append(a0['dates'] == '▾ Date pool' and a0['dchips'] >= 1 and a0['tchips'] == 1 and a1['dates'] == '▸ Date pool (%d)' % a0['dchips'] and a1['dchips'] == 0
                       and a1['tchips'] == 1 and a1['stored'] == '{"dates":true}' and a2['dates'] == a1['dates'] and a3['dates'] == '▾ Date pool' and a3['dchips'] == a0['dchips']
                       and a3['stored'] is None)
        # B) the open block
        pg.click('.dci-pools-toggle')
        pg.wait_for_timeout(300)
        pg.click('[data-el=dates] .dci-pools-body .dci-tracks-bar [data-act=pool-fold]')
        pg.wait_for_timeout(300)
        b1 = st()
        pg.click('[data-el=dates] .dci-pools-body .dci-tracks-bar [data-act=pool-fold]')
        pg.wait_for_timeout(300)
        b2 = st()
        print('B) offen – Track pool zu:', b1, '| wieder auf:', b2)
        results.append(b1['tracks'] == '▸ Track pool (1)' and b1['tchips'] == 0 and b2['tracks'] == '▾ Track pool' and b2['tchips'] == 1)
        pg.click('.dci-pools-toggle')
        pg.wait_for_timeout(300)
        # C) the scroll bars of the works matrix
        MX = """(() => { const w = document.querySelector('.dci-mx-wrap'); const t = document.querySelector('[data-mxhs=top]'); const bt = document.querySelector('[data-mxhs=bottom]');
      const body = document.querySelector('#dci-overlay .dci-body').getBoundingClientRect();
      return { over: w.scrollWidth > w.clientWidth, top: !t.hidden, bottom: !bt.hidden, wl: Math.round(w.scrollLeft), tl: Math.round(t.scrollLeft), bl: Math.round(bt.scrollLeft),
        bottomIn: !bt.hidden && bt.getBoundingClientRect().bottom <= body.bottom + 1 && bt.getBoundingClientRect().top >= body.top,
        atEdge: !bt.hidden && Math.abs(bt.getBoundingClientRect().bottom - body.bottom) <= 2 }; })()"""
        pg.evaluate("document.querySelector('.dci-mx-wrap').scrollIntoView({ block: 'start' })")
        pg.wait_for_timeout(300)
        c0 = pg.evaluate(MX)
        pg.evaluate("(() => { const t = document.querySelector('[data-mxhs=top]'); t.scrollLeft = 200; t.dispatchEvent(new Event('scroll')); })()")
        pg.wait_for_timeout(300)
        c1 = pg.evaluate(MX)
        pg.evaluate("(() => { const w = document.querySelector('.dci-mx-wrap'); w.scrollLeft = 60; w.dispatchEvent(new Event('scroll')); })()")
        pg.wait_for_timeout(300)
        c2 = pg.evaluate(MX)
        # the matrix starts near the bottom of the visible area: its lower edge out of view
        pg.evaluate("""(() => { const body = document.querySelector('#dci-overlay .dci-body'); const w = document.querySelector('.dci-mx-wrap');
      body.scrollTop += w.getBoundingClientRect().top - body.getBoundingClientRect().bottom + 160; })()""")
        pg.wait_for_timeout(500)
        c3 = pg.evaluate(MX)
        pg.evaluate("document.querySelector('.dci-mx-end').scrollIntoView({ block: 'center' })")
        pg.wait_for_timeout(500)
        c4 = pg.evaluate(MX)
        print('C) Matrix:', c0, '\n   oben 200:', c1, '\n   Matrix 60:', c2, '\n   unterer Rand außer Sicht:', c3, '\n   in Sicht:', c4)
        results.append(c0['over'] and c0['top'] and c1['wl'] == 200 and c2['tl'] == 60 and c3['bottom'] and c3['bottomIn'] and c3['atEdge'] and c3['bl'] == 60 and not c4['bottom'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_tracksdrop():
    """Track groups by drag & drop onto "Tracks and status" of rows (the row gets the group's tracks; with Shift
    they are added; the places say so while dragging; a release-level row moves to the recording level); folded,
    the track pool stays in the bar with the date pool; a date dropped onto an empty cell of the works matrix says
    why it was not set, onto MB's dateless relationship it is planned as an edit; the release page checks work
    credits (composer, publisher) on the works themselves when the release lookup lacks them."""
    import re
    import zooid
    from common_rows import drag, tracks_of_rows

    PW = sync_playwright().start()
    results = []


    def open_mb(companion=False):
        b = PW.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg = None
        if companion:
            dg, _ = H.open_discogs(ctx)
        pg, errs = H.open_mb_edit(ctx, companion=companion)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        return b, pg, dg, errs


    def rid(pg, name):
        return pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text=name)).first.locator('tr.dci-row').first.get_attribute('data-row')


    def tracks(pg, name):
        return tracks_of_rows(pg, name)[0]


    def group_id(pg, text, where='.dci-pools-body'):
        return pg.evaluate(f"[...document.querySelectorAll('{where} .dci-pchip-tg')].find(c => c.textContent.includes({text!r})).dataset.id")


    # --- B) default release: a release-level row moves to "Recording"; works matrix cells that cannot take a date
    b, pg, _, errs = open_mb()
    pg.click('[data-act=tg-new]'); pg.fill('[data-f=tg-name]', 'Side A')
    pg.check('[data-f=tg-track][data-i="0"]'); pg.check('[data-f=tg-track][data-i="1"]'); pg.click('[data-act=tg-save]'); pg.wait_for_timeout(200)
    rel_row = pg.locator('tr.dci-row.dci-lv-release').first
    rel_id = rel_row.get_attribute('data-row')
    role = re.sub(r'\s+', ' ', rel_row.locator('.dci-c-role').inner_text())[:40]
    gid = group_id(pg, 'Side A')
    drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', f'tr[data-row="{rel_id}"] .dci-c-tracks')
    moved = pg.locator(f'tr[data-row="{rel_id}"]').get_attribute('class')
    msg = [m[:110] for m in pg.locator('.dci-msg').all_inner_texts() if 'Release' in m and 'Recording' in m]
    tsel = pg.evaluate(f"[...document.querySelectorAll('tr[data-tracksrow=\"{rel_id}\"] input[data-f=track]:checked')].map(c => Number(c.dataset.i) + 1)")
    print('B1) Release-Zeile', role, '→', moved, '| Tracks:', tsel, '| Meldung:', msg)
    ok_b1 = 'dci-lv-recording' in moved and tsel == [1, 2] and len(msg) == 1
    # works matrix: an empty cell, and a cell with only a relationship already in MusicBrainz
    date = pg.evaluate("document.querySelector('.dci-pools-body .dci-pchip-date').dataset.id")
    empty = '.dci-mx-cell[data-col="k:a17"][data-mrow^="w:0"]'
    drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', empty)
    m1 = [m for m in pg.locator('.dci-msg').all_inner_texts() if 'no role switched on' in m]
    ww = '.dci-mx-cell[data-col="k:a15"][data-mrow^="w:0"]'
    pg.click(f'{ww} [data-act=mx-cell]'); pg.wait_for_timeout(200)
    cell_now = re.sub(r'\s+', ' ', pg.locator(ww).inner_text())
    drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', ww)
    m2 = [re.sub(r'\s+', ' ', x) for x in pg.locator(f'{ww} .dci-mx-fill').all_inner_texts()]   # MB's composer has no date: it is added (edit)
    # a cell with a role of its own still takes the date
    drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', '.dci-mx-cell[data-col="k:a15"][data-mrow="n:1"]')
    own = pg.locator('.dci-mx-cell[data-col="k:a15"][data-mrow="n:1"] sup').count()
    print('B2) leere Zelle:', m1[:1], '| nur MB (Zelle jetzt:', cell_now, '): geplant', m2[:1], '| Zelle mit eigener Rolle ⌚:', own)
    ok_b2 = len(m1) == 1 and len(m2) == 1 and 'composer' in m2[0] and own == 1
    results += [ok_b1, ok_b2]
    print('Fehler B:', errs)
    b.close()

    # --- C) release page: work credits found on the work itself ----------------------------------------------
    H.MB_EXTRA.clear()
    H.WORK_RELS_DIRECT_ONLY = True
    b, pg, dg, errs = open_mb(companion=True)
    H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
    H.submit_staged(pg)
    pg.goto(f'https://musicbrainz.org/release/{H.REL}')
    H.with_companion(pg)
    dg.wait_for_timeout(6000)
    marks = dg.evaluate("[...document.querySelectorAll('.dci-dg-mark')].map(m => m.textContent + ' ' + m.closest('li, tr').querySelector('a').textContent)")
    print('C) Release-Seite (Werk-Beziehungen nur am Werk):', marks, '| Werk-Abfragen:', len(H.WORK_LOOKUPS))
    ok_c = '✓ Pub Co' in marks and '✓ Writer W' in marks and H.WORK1 in H.WORK_LOOKUPS and not any(m.startswith('✗') for m in marks)
    results.append(ok_c)
    print('Fehler C:', errs)
    H.WORK_RELS_DIRECT_ONLY = False
    b.close()
    # --- A) Zooid: two track groups from the notes ------------------------------------------------------------
    zooid.setup(zooid.NOTES_TWO_DAYS)
    b, pg, _, errs = open_mb()
    names = [re.sub(r'\s+', ' ', x) for x in pg.locator('.dci-pools-body .dci-pchip-tg .dci-chip-main').all_inner_texts()]
    print('A1) Track-Pool:', names, '| Hinweis:', pg.locator('.dci-tracks-bar .dci-drag-hint').get_attribute('title')[:90])
    g2 = group_id(pg, '6')   # tracks 6–10
    g1 = pg.evaluate(f"[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].map(c => c.dataset.id).find(id => id !== {g2!r})")
    print('    Henry Threadgill vorher:', tracks(pg, 'Henry Threadgill'))
    drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{g2}"] .dci-chip-main', f'tr[data-row="{rid(pg, "Henry Threadgill")}"] .dci-c-tracks')
    after = tracks(pg, 'Henry Threadgill')
    count = pg.locator(f'[data-tcount="{rid(pg, "Henry Threadgill")}"]').inner_text()
    print('    nach Ablegen von Tracks 6–10:', after, '|', count)
    ok_a1 = after == [6, 7, 8, 9, 10] and '5' in count
    # with Shift: added to the row's own tracks
    # (Playwright's mouse drag carries no modifier keys, so the drop with Shift is dispatched as events)
    # The places on rows say what a drop does: replace, with Shift add (shown while a track group is dragged)
    hints = pg.evaluate(f"""(() => {{
  const src = document.querySelector('.dci-pools-body .dci-pchip-tg[data-id="{g1}"]');
  const dst = document.querySelector('tr[data-row="{rid(pg, "Henry Threadgill")}"] .dci-c-tracks');
  const other = document.querySelector('tr[data-row="{rid(pg, "Liberty Ellman")}"] .dci-c-tracks');
  const after = (el) => getComputedStyle(el, '::after').content;
  const dt = new DataTransfer();
  src.dispatchEvent(new DragEvent('dragstart', {{ bubbles: true, dataTransfer: dt }}));
  dst.dispatchEvent(new DragEvent('dragover', {{ bubbles: true, cancelable: true, dataTransfer: dt }}));
  const out = [after(other), after(dst)];
  dst.dispatchEvent(new DragEvent('dragover', {{ bubbles: true, cancelable: true, dataTransfer: dt, shiftKey: true }}));
  out.push(after(dst));
  dst.dispatchEvent(new DragEvent('drop', {{ bubbles: true, cancelable: true, dataTransfer: dt, shiftKey: true }}));
  src.dispatchEvent(new DragEvent('dragend', {{ bubbles: true, dataTransfer: dt }}));
  out.push(after(dst));
  return out;
}})()""")
    pg.wait_for_timeout(200)
    added = tracks(pg, 'Henry Threadgill')
    print('A2) Hinweise beim Ziehen (andere Zeile | darüber | mit Umschalt | danach):', hints)
    print('    mit Umschalt Tracks 1–5 dazu:', added)
    ok_a2 = added == list(range(1, 11)) and 'Shift: add' in hints[0] and 'replaces the tracks' in hints[1] and 'adds to the tracks' in hints[2] \
        and hints[3] in ('none', 'normal', '')
    # the open track list of a row is a target too
    r = rid(pg, 'Liberty Ellman')
    pg.click(f'tr[data-row="{r}"] [data-act=tracks-toggle]'); pg.wait_for_timeout(150)
    drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{g1}"] .dci-chip-main', f'tr[data-tracksrow="{r}"] .dci-chips')
    print('    auf die offene Trackliste von Liberty Ellman:', tracks(pg, 'Liberty Ellman'))
    ok_a2 = ok_a2 and tracks(pg, 'Liberty Ellman') == [1, 2, 3, 4, 5]
    # folded: the track pool stays in the bar and can be dragged from there
    pg.click('.dci-pools-fold'); pg.wait_for_timeout(200)
    kept_tg = pg.locator('.dci-pools-kept .dci-pchip-tg').count()
    kept_dates = pg.locator('.dci-pools-kept .dci-pchip-date').count()
    print('A3) eingeklappt oben – Track-Gruppen:', kept_tg, '| Daten:', kept_dates, '| Option:', pg.evaluate("document.querySelector('[data-el=dates]').textContent.includes('keep') ? 'x' : ''"))
    drag(pg, f'.dci-pools-kept .dci-pchip-tg[data-id="{g2}"] .dci-chip-main', f'tr[data-row="{rid(pg, "Liberty Ellman")}"] .dci-c-tracks')
    print('    aus der Leiste auf Liberty Ellman:', tracks(pg, 'Liberty Ellman'))
    ok_a3 = kept_tg == 2 and kept_dates >= 1 and tracks(pg, 'Liberty Ellman') == [6, 7, 8, 9, 10]
    log = pg.evaluate("[...document.querySelectorAll('#dci-log li')].slice(-3).map(l => l.textContent.slice(9))")
    print('    Protokoll:', log)
    ok_a3 = ok_a3 and any('Track group' in x and 'put on a row: 5 tracks' in x for x in log)
    results += [ok_a1, ok_a2, ok_a3]
    print('Fehler A:', errs)
    b.close()

    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
    PW.stop()


def case_titledates():
    """Credits Importer 3.31.7: dates in the titles of the tracks (collected item 110; maintainer, Bandcamp "At Iridium 2004":
    "wir brauchen eine option um daten von tracknamen in den datums/trackpool aufzunehmen. die Tracknummern hat man dann ja
    direkt. diese option soll im mapping ebenfalls an und abstellbar sein (Quick Switches). standardeinstellung = aus").
    Titles "March 23, 2004 (Set 1)", "March 23, 2004 (Set 2)", "March 24, 2004 (Set 1)", "March 24, 2004 (Set 2)".
    A) D023 is off by default: no date from the titles.
    B) Switched on in "Mapping rules": the date pool gets March 23 and 24, 2004, the track pool "March 23, 2004 · 1–2" and
       "March 24, 2004 · 3–4", the date matrix both as suggestions under Performance, a message says so; stored as "+D023".
    C) Switched off again: the suggestions go (pool entries, track groups, cells).
    D) On again and "Apply": Bass Man's row (all tracks) is split – tracks 1–2 on 2004-03-23, 3–4 on 2004-03-24."""
    from common_rows import lib, cells
    H.TITLES[:] = ['March 23, 2004 (Set 1)', 'March 23, 2004 (Set 2)', 'March 24, 2004 (Set 1)', 'March 24, 2004 (Set 2)']
    orig = H.discogs_release

    def rel():
        d = orig()
        d['notes'] = ''
        return d

    H.discogs_release = rel
    POOL = """[[...document.querySelectorAll('.dci-pchip-date .dci-chip-main')].map(c => c.textContent.trim()),
      [...new Set([...document.querySelectorAll('.dci-pchip-tg .dci-chip-main')].map(c => c.textContent.replace(/\\s+/g, ' ').trim()))]]"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        if pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') != 'true':
            pg.click('.dci-pools-toggle'); pg.wait_for_timeout(200)
        a = [pg.evaluate(POOL), cells(pg).get('performance')]
        print('A) aus:', a)
        results.append(a[0] == [[], []] and a[1] == [])
        pg.click('[data-act=rules]'); pg.wait_for_timeout(300)
        box = '#dci-rules [data-rf=tables] [data-rule-on=D023]'  # [3.32.0] also a quick switch at the top
        on0 = pg.locator(box).is_checked()
        pg.locator(box).scroll_into_view_if_needed()
        pg.check(box); pg.wait_for_timeout(800)
        b1 = [pg.evaluate(POOL), cells(pg).get('performance')]
        msg = pg.evaluate("[...document.querySelectorAll('#dci-msgs li, .dci-msg')].map(x => x.textContent).join(' | ')")
        stored = pg.evaluate("localStorage.getItem('dci-rules-off')")
        print('B) an (vorher an:', on0, '):', b1, '\n   Meldung:', msg[:200], '| gespeichert:', stored)
        results.append(not on0 and [x.split(' 0 rows')[0] for x in b1[0][0]] == ['March 23, 2004 · 2004-03-23', 'March 24, 2004 · 2004-03-24']
                       and b1[0][1] == ['March 23, 2004 · 1–2 2 tracks', 'March 24, 2004 · 3–4 2 tracks']
                       and [c[0] for c in b1[1]] == ['March 23, 2004 · 2004-03-23', 'March 24, 2004 · 2004-03-24'] and all(c[2] for c in b1[1])
                       and [c[1] for c in b1[1]] == [['March 23, 2004 · 1–2'], ['March 24, 2004 · 3–4']]
                       and 'titles of the tracks' in msg and '+D023' in (stored or ''))
        pg.uncheck(box); pg.wait_for_timeout(800)
        c1 = [pg.evaluate(POOL), cells(pg).get('performance')]
        print('C) wieder aus:', c1)
        results.append(c1[0] == [[], []] and c1[1] == [])
        pg.check(box); pg.wait_for_timeout(800)
        pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(600)
        d1 = lib(pg, 'Bass Man')
        print('D) nach „Anwenden“ – Bass Man:', d1)
        results.append(sorted(d1) == [([1, 2], '2004-03-23'), ([3, 4], '2004-03-24')])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
