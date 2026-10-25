from playwright.sync_api import sync_playwright
import harness as H
# [3.31.1] compared with a log of an older version: with the script's own gap between requests to MusicBrainz
H.MAIN = H.MAIN_SLOW

def marks(dg):
    return dg.evaluate("[...document.querySelectorAll('.dci-dg-mark')].map(m => m.textContent + ' ' + m.closest('li, tr').querySelector('a').textContent)")

with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg, dgerr = H.open_discogs(ctx)
    pg, errs = H.open_mb_edit(ctx)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
    print('1) nach Übernehmen:', marks(dg))
    missing = H.submit_staged(pg, leave_out=1)
    print('   absichtlich nicht angekommen:', missing)
    pg.goto(f'https://musicbrainz.org/release/{H.REL}')   # "Enter edit" leads to the release page
    H.with_companion(pg)
    dg.wait_for_timeout(5000)
    print('2) Release-Seite:', marks(dg))
    t = dg.evaluate("[...document.querySelectorAll('.dci-dg-pending')].map(m => m.title)")
    print('   Tooltip ✗:', t[:1])
    items = H.STORE.data['statusMap']['items']
    print('   Einträge Bass Man:', [(i['role'], i['status'], i.get('note')) for i in items if i['artistId'] == 3001])
    pg.close()
    dg.wait_for_timeout(12000)
    print('3) Release-Seite geschlossen:', marks(dg))
    pr, _ = H.open_mb_release(ctx)
    dg.wait_for_timeout(5000)
    print('4) später wieder geöffnet:', marks(dg))
    print('Fehler:', errs, dgerr)
    b.close()
