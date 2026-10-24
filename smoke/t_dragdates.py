"""Pool dates by drag & drop (the stamp is gone): onto the date field of a row (also one with a date of its own),
onto the column date and a cell of the works matrix; a date onto another date makes a period (pool and matrix);
all dates of the Discogs notes go into the pool; cleared pools come back when the release is opened again;
"load again from Discogs" (with and without the dates made by hand); "Cover Art" keeps "cover art" as wording."""
import re
from playwright.sync_api import sync_playwright
import harness as H
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
