"""Import 3.14.1: ▲ ▼ in the footer jump to the top and the bottom of the dashboard – in the window (its own scrolling)
and in the page (the page scrolls)."""
from playwright.sync_api import sync_playwright
import harness as H

results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    body = "document.querySelector('[data-el=body]')"
    pg.locator('[data-act=jump-bottom]').evaluate('b => b.click()'); pg.wait_for_timeout(1200)
    down = pg.evaluate(f"(() => {{ const b = {body}; return [Math.round(b.scrollTop), b.scrollHeight - b.clientHeight]; }})()")
    pg.locator('[data-act=jump-top]').evaluate('b => b.click()'); pg.wait_for_timeout(1200)
    up = pg.evaluate(f"{body}.scrollTop")
    print('Fenster: ▼', down, '| ▲', up)
    results.append(down[1] > 100 and abs(down[0] - down[1]) <= 2 and up == 0)
    # in the page
    H.toggle_place(pg); pg.wait_for_timeout(300)
    inline = pg.evaluate("!!document.querySelector('.dci-inline')")
    pg.locator('[data-act=jump-bottom]').evaluate('b => b.click()'); pg.wait_for_timeout(1500)
    y1 = pg.evaluate("[Math.round(scrollY), Math.round(document.documentElement.scrollHeight - innerHeight)]")
    foot = pg.evaluate("Math.round(document.querySelector('.dci-panel').getBoundingClientRect().bottom - innerHeight)")
    pg.locator('[data-act=jump-top]').evaluate('b => b.click()'); pg.wait_for_timeout(1500)
    top = pg.evaluate("Math.round(document.querySelector('.dci-panel').getBoundingClientRect().top)")
    print('Seite:', inline, '| ▼ scrollY', y1, 'Ende des Dashboards zum Fensterrand:', foot, '| ▲ Anfang des Dashboards:', top)
    results.append(inline and y1[0] > 200 and -40 <= foot <= 20 and 0 <= top <= 20)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
