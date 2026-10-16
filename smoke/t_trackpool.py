"""Dates for some tracks (Discogs notes of Zooid – Cut You Where You Was): found dates are placed in the date
matrix as suggestions with their track groups and studios; "Apply" splits the rows; applying again gives the
same rows; removing a date and applying again brings the rows back together."""
import re
from playwright.sync_api import sync_playwright
import harness as H
import zooid
from common_rows import lib, cells, stage

PW = sync_playwright().start()


def run(notes, label):
    zooid.setup(notes)
    b = PW.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    return b, pg, errs

# 1) two sessions, the second on two consecutive days
b, pg, errs = run(zooid.NOTES_TWO_DAYS, 'zwei Tage')
print('Meldung:', [m[:90] for m in pg.locator('.dci-msg').all_inner_texts()])
print('Matrix (Vorschläge):', cells(pg)['performance'])
print('Track-Pool:', pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts())
before = lib(pg)
pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(500)
for n in ['Liberty Ellman', 'Henry Threadgill', 'Jose Davila', 'Brooklyn Recording', 'Scholes Street Studio']:
    print(f'  {n}:', lib(pg, n))
want = sorted([([1, 2, 3, 4, 5], '2025-06-25'), ([6, 7, 8, 9, 10], '2025-06-23 – 2025-06-24')])
ok1 = sorted(lib(pg)) == want and before == [([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], '')] \
    and lib(pg, 'Brooklyn') == [([1, 2, 3, 4, 5], '2025-06-25')] and lib(pg, 'Scholes') == [([6, 7, 8, 9, 10], '2025-06-23 – 2025-06-24')] \
    and lib(pg, 'Jose Davila') == [([6, 7, 8, 9, 10], '2025-06-23 – 2025-06-24')] and not any(c[2] for c in cells(pg)['performance'])
# applying again gives the same rows (no further copies)
pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
ok1b = sorted(lib(pg)) == want
print('Zweites „Anwenden“ unverändert:', ok1b)
stage(pg)
staged = pg.evaluate("""MB.relationshipEditor.state.added.filter(r => ['Liberty Ellman', 'Scholes Street Studio', 'Brooklyn Recording'].includes(r.entity0.name)).length""")
print('Vorgemerkt (Liberty, Studios):', staged, '(erwartet 20)')
# 1b) the second date goes: Liberty's rows come back together, the second part loses its date
pg.locator('.dci-dm-col[data-dmcol=performance] .dci-dm-cell').nth(1).locator('[data-act=dm-remove]').first.click(); pg.wait_for_timeout(200)
print('Hinweis nach Entfernen:', pg.locator('[data-el=dates] .dci-dm-pending').first.inner_text())
pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
print('Nach Entfernen von Performance 2 + Anwenden – Liberty:', lib(pg), '| Scholes:', lib(pg, 'Scholes'))
ok1c = sorted(lib(pg)) == sorted([([1, 2, 3, 4, 5], '2025-06-25'), ([6, 7, 8, 9, 10], '')]) and lib(pg, 'Scholes') == [(list(range(1, 11)), '')]
print('[zwei Tage] Ergebnis:', 'OK' if ok1 and ok1b and ok1c and staged == 20 else 'FEHLER', [ok1, ok1b, ok1c], '| Fehler:', errs)
b.close()

# 2) the second session on two separate days: the matrix asks ("choose"); single days → two rows per track
b, pg, errs = run(zooid.NOTES_SEPARATE, 'getrennte Tage')
print('Matrix:', cells(pg)['performance'], '| Wählen:', [re.sub(r'\s+', ' ', x) for x in pg.locator('.dci-dm-choose .dci-dm-opt').all_inner_texts()])
print('Pool:', [re.sub(r'\s+', ' ', c) for c in pg.locator('.dci-pchip-date .dci-chip-main').all_inner_texts()])
pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
print('  vor der Wahl – Liberty:', lib(pg), '|', [m[:60] for m in pg.locator('.dci-msg').all_inner_texts() if 'choose' in m])
ok2a = lib(pg) == [([1, 2, 3, 4, 5], '2025-06-25'), ([6, 7, 8, 9, 10], '')] and pg.locator('.dci-pchip-date').count() == 5
pg.click('.dci-dm-choose [data-act=dm-choose][data-pick=single]'); pg.wait_for_timeout(200)
print('  gewählt „einzeln“:', cells(pg)['performance'])
pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
print('  Liberty Ellman:', lib(pg))
print('  Scholes Street Studio:', lib(pg, 'Scholes'))
stage(pg)
n_lib = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0.name === 'Liberty Ellman').length")
print('[getrennte Tage] Liberty vorgemerkt:', n_lib, '(erwartet 15: 5 + 5×2) |', 'OK' if n_lib == 15 and ok2a else 'FEHLER', '| Fehler:', errs)
b.close()

# 3) "as single dates" for the consecutive days: the period's suggestion is replaced by two single dates
b, pg, errs = run(zooid.NOTES_TWO_DAYS, 'einzelne Tage')
pg.click('[data-el=datefind] summary')
pg.locator('[data-el=datefind-list] li').nth(1).locator('[data-act=datefind-split]').click(); pg.wait_for_timeout(200)
pg.locator('[data-el=datefind-list] li').nth(1).locator('[data-act=datefind-use][data-group=performance]').click(); pg.wait_for_timeout(300)
m = cells(pg)['performance']
print('Matrix:', m)
print('Fundliste:', re.sub(r'\s+', ' ', pg.locator('[data-el=datefind-list] li').nth(1).inner_text())[:140])
pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
print('  Liberty Ellman:', lib(pg))
ok3 = len(m) == 3 and sorted(lib(pg)) == sorted([([1, 2, 3, 4, 5], '2025-06-25'), ([6, 7, 8, 9, 10], '2025-06-23'), ([6, 7, 8, 9, 10], '2025-06-24')])
print('[einzelne Tage] Ergebnis:', 'OK' if ok3 else 'FEHLER', '| Fehler:', errs)
b.close()
PW.stop()
