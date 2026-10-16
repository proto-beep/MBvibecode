"""Separate days ("Recorded June 16 & 19, 1980 at …"): the pool keeps both days as Discogs gives them and gets
the period as well; the matrix asks "choose" and applies nothing until then; choosing the period puts it on
the rows; a group button moves the entry; without its period the single days stay."""
import re
from playwright.sync_api import sync_playwright
import harness as H
import zooid
from common_rows import lib, cells

zooid.setup('Recorded June 16 & 19, 1980 at Scholes Street Studio, Brooklyn, New York.')
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(300)
    pool = [re.sub(r'\s+', ' ', c) for c in pg.locator('.dci-pchip-date .dci-chip-main').all_inner_texts()]
    print('1) Pool:', pool)
    print('   Matrix:', cells(pg)['performance'])
    print('   Kopf:', re.sub(r'\s+', ' ', pg.locator('.dci-pools-head').inner_text()))
    pg.click('[data-el=datefind] summary')
    item = re.sub(r'\s+', ' ', pg.locator('[data-el=datefind-list] li').first.inner_text())
    print('   Fundliste:', item[:150])
    ok1 = len(pool) == 4 and 'Performance 1–2 · 1980-06-16 – 1980-06-19' in pool[2] and 'Performance 1–2 (month) · 1980-06' in pool[3] \
        and cells(pg)['performance'][0][0].startswith('choose: 2 dates as on Discogs: 1980-06-16 · 1980-06-19') and 'month only: 1980-06' in cells(pg)['performance'][0][0] \
        and 'also as a period: 1980-06-16 – 1980-06-19' in item and '1 to choose' in pg.locator('.dci-pools-head').inner_text()
    # 2) Apply before choosing: nothing on the rows
    pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(300)
    print('2) vor der Wahl – Liberty:', lib(pg))
    ok2 = lib(pg) == [(list(range(1, 11)), '')]
    # 3) a group button moves the entry (Mix), then back to Performance
    pg.locator('[data-el=datefind-list] li').first.locator('[data-act=datefind-use][data-group=mix]').click(); pg.wait_for_timeout(200)
    moved = (len(cells(pg)['mix']), len(cells(pg)['performance']))
    pg.evaluate("document.querySelector('[data-el=datefind]').open = true")
    pg.locator('[data-el=datefind-list] li').first.locator('[data-act=datefind-use][data-group=performance]').click(); pg.wait_for_timeout(200)
    print('3) per Knopf nach Mix (Mix, Performance):', moved, '| zurück:', (len(cells(pg)['mix']), len(cells(pg)['performance'])), '| Pool:', pg.locator('.dci-pchip-date').count())
    ok3 = moved == (1, 0) and len(cells(pg)['performance']) == 1 and pg.locator('.dci-pchip-date').count() == 4
    # 4) choose the period: it goes onto the rows (the studio too)
    pg.click('.dci-dm-choose [data-act=dm-choose][data-pick=range]'); pg.wait_for_timeout(200)
    pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(400)
    print('4) Zeitraum gewählt:', cells(pg)['performance'], '| Liberty:', lib(pg), '| Scholes:', lib(pg, 'Scholes'))
    ok4 = lib(pg) == [(list(range(1, 11)), '1980-06-16 – 1980-06-19')] and lib(pg, 'Scholes') == [(list(range(1, 11)), '1980-06-16 – 1980-06-19')] \
        and lib(pg, 'Brooklyn') == [(list(range(1, 11)), '')]
    # 5) a fresh entry to choose; the period leaves the pool: the single days stay in the matrix
    pg.locator('.dci-dm-col[data-dmcol=performance] [data-act=dm-remove]').first.click(); pg.wait_for_timeout(150)
    pg.evaluate("document.querySelector('[data-el=datefind]').open = true")
    pg.locator('[data-el=datefind-list] li').first.locator('[data-act=datefind-use][data-group=performance]').click(); pg.wait_for_timeout(200)
    rid = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].find(c => c.textContent.includes('1–2')).dataset.id")
    pg.click(f'[data-act=pool-edit][data-id="{rid}"]'); pg.wait_for_timeout(150)
    pg.on('dialog', lambda d: d.accept())
    pg.click('[data-act=pool-remove]'); pg.wait_for_timeout(300)
    print('5) Zeitraum aus dem Pool gelöscht → Matrix:', cells(pg)['performance'])
    ok5 = [c[0] for c in cells(pg)['performance']] == ['Performance 1 · 1980-06-16', 'Performance 2 · 1980-06-19']
    print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4, ok5]) else 'FEHLER', [ok1, ok2, ok3, ok4, ok5], '| Fehler:', errs)
    b.close()
