import re
from playwright.sync_api import sync_playwright
import harness as H
# [3.31.1] compared with a log of an older version: with the script's own gap between requests to MusicBrainz
H.MAIN = H.MAIN_SLOW

def check(pg, label, sel, text, scope=None):
    loc = (scope or pg).locator(sel).first
    loc.click()
    pg.keyboard.type(text, delay=120)
    pg.wait_for_timeout(1800)
    st = pg.evaluate("""() => { const a = document.activeElement; return { f: a && a.dataset ? a.dataset.f : a && a.tagName, v: a && a.value }; }""")
    ok = st['v'] is not None and text in str(st['v'])
    print(f'{"OK " if ok else "FEHLER"} {label}: aktiv={st["f"]} Wert={st["v"]!r}')
    return ok

with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg, _ = H.open_discogs(ctx)
    pg, errs = H.open_mb_edit(ctx)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
    row = lambda name: pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text=name)).first.locator('tr.dci-row').first
    res = []
    row('Bass Man').locator('[data-act=date-open]').click()
    res.append(check(pg, 'Zeile Jahr', '[data-f=rd-by]', '2001', row('Bass Man')))
    res.append(check(pg, 'Zeile Monat', '[data-f=rd-bm]', '03', row('Bass Man')))
    res.append(check(pg, 'Zeile Tag', '[data-f=rd-bd]', '02', row('Bass Man')))
    # the column date is in the ▾ menu of the column head
    pg.locator('[data-colhead] [data-act=mx-colmenu]').first.click(); pg.wait_for_timeout(300)
    res.append(check(pg, 'Matrix-Spalte Jahr', '[data-f=cd-by]', '1999'))
    pg.locator('[data-colhead] [data-act=mx-colmenu]').first.click(); pg.wait_for_timeout(300)
    pg.locator('[data-act=mx-menu]').first.click(); pg.wait_for_timeout(400)
    print('Zellmenü-Felder:', pg.locator('[data-f^=xd-]').count())
    if pg.locator('[data-f=xd-by]').count():
        res.append(check(pg, 'Matrix-Zelle Jahr', '[data-f=xd-by]', '1998'))
    pg.click('#dci-overlay .dci-head h2'); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector('[data-el=datefind]').open = true")
    res.append(check(pg, 'Daten-Suchfeld', '[data-f=datefind]', 'Recorded 1 May 2002'))
    print('Fehler:', errs)
    b.close()
