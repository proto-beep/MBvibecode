from playwright.sync_api import sync_playwright
import harness as H
# [3.31.1] compared with a log of an older version: with the script's own gap between requests to MusicBrainz
H.MAIN = H.MAIN_SLOW
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg, dgerr = H.open_discogs(ctx)
    pg, errs = H.open_mb_edit(ctx)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    print('Gruppen:', pg.locator('.dci-group .dci-gname').all_inner_texts())
    print('Log:', [l[9:90] for l in pg.locator('#dci-log li').all_inner_texts()][-6:])
    H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
    print('Sync:', pg.inner_text('[data-el=sync]').replace('\n', ' ')[:160])
    pg.wait_for_timeout(2500)
    print('Zeichen auf Discogs:', dg.locator('.dci-dg-mark').all_inner_texts())
    print('Fehler MB:', errs, '| Discogs:', dgerr)
    b.close()
