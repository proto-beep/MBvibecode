"""Dates & tracks as one block: open when dates were found, folded state remembered; clearing all track
groups (dates in the matrix become dashed suggestions for all tracks) and all dates (also of other
releases), rows keep their dates as their own; the list of created works stays."""
import re
from playwright.sync_api import sync_playwright
import harness as H
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
