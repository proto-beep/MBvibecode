"""Date matrix by hand: drag a date into a column and a track group onto it, apply; the click alternative
(grip, then "place here"); the cell editor (column, track groups); moving a cell; a date with track groups
in the matrix dropped onto a row; "apply automatically"; the matrix is still there after a reload."""
import re
from playwright.sync_api import sync_playwright
import harness as H
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
