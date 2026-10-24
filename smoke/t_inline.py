"""The dashboard in the page instead of a window: switched in the page bar before opening, placed below the
import button, the page scrolls with it (dates block and footer stay in view), switched back in the dashboard
header, remembered after a reload, back to the window with "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults")."""
from playwright.sync_api import sync_playwright
import harness as H

with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    seg = pg.locator('#dci-launcher .dci-place-seg button')
    print('Schalter in der Seitenleiste:', seg.all_inner_texts(), [seg.nth(i).get_attribute('aria-pressed') for i in range(2)])
    pg.click('#dci-launcher [data-place=page]')
    pg.wait_for_timeout(200)
    # 3.5.1: the switch shows the choice at once, before the dashboard was opened
    pressed0 = [seg.nth(i).get_attribute('aria-pressed') for i in range(2)]
    print('0) Schalter nach dem Klick (Dashboard noch zu):', pressed0)
    H.open_dashboard(pg)
    pg.wait_for_timeout(400)
    where = pg.evaluate("""(() => { const o = document.getElementById('dci-overlay'); const panel = o.querySelector('.dci-panel');
      return { afterBar: document.getElementById('dci-pagebar').nextElementSibling === o, inline: o.classList.contains('dci-inline'),
        position: getComputedStyle(panel).position, bodyOverflow: getComputedStyle(o.querySelector('.dci-body')).overflowY,
        head: o.querySelector('[data-act=place-toggle]').textContent.trim() }; })()""")
    print('1) in der Seite:', where)
    ok1 = where['afterBar'] and where['inline'] and where['position'] == 'relative' and where['bodyOverflow'] == 'visible' and pressed0 == ['false', 'true']
    # 2) the page scrolls; the dates block ([3.18.0] with the line "Add entry manually") sticks to the top, the footer to the bottom
    pg.evaluate("window.scrollTo(0, document.querySelector('[data-el=companies]').getBoundingClientRect().top + window.scrollY - 200)")
    pg.wait_for_timeout(300)
    pos = pg.evaluate("""(() => ({ y: Math.round(window.scrollY), dates: Math.round(document.querySelector('[data-el=stick]').getBoundingClientRect().top),
      foot: Math.round(window.innerHeight - document.querySelector('.dci-foot').getBoundingClientRect().bottom) }))()""")
    print('2) gescrollt:', pos)
    ok2 = pos['y'] > 300 and pos['dates'] == 0 and pos['foot'] == 0
    # 3) dragging the head moves nothing
    box = pg.locator('.dci-head h2').bounding_box()
    pg.mouse.move(box['x'] + 5, box['y'] + 5); pg.mouse.down(); pg.mouse.move(box['x'] + 200, box['y'] + 100); pg.mouse.up()
    style = pg.evaluate("document.querySelector('.dci-panel').getAttribute('style') || ''")
    print('3) Kopf gezogen → Stil:', repr(style))
    ok3 = 'left' not in style
    # 4) back to a window in the dashboard header; remembered
    pg.click('[data-act=place-toggle]'); pg.wait_for_timeout(300)
    back = pg.evaluate("""(() => { const o = document.getElementById('dci-overlay'); return { parent: o.parentNode === document.body,
      position: getComputedStyle(o.querySelector('.dci-panel')).position, stored: localStorage.getItem('dci-place') }; })()""")
    print('4) zurück als Fenster:', back)
    ok4 = back['parent'] and back['position'] == 'fixed' and back['stored'] is None
    pg.click('[data-act=place-toggle]'); pg.wait_for_timeout(200)
    pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000)
    pressed = pg.locator('#dci-launcher [data-place=page]').get_attribute('aria-pressed')
    pg.click('#dci-open'); pg.wait_for_selector('.dci-inline .dci-pools-head', timeout=30000)
    print('5) nach Neuladen: in der Seite gedrückt', pressed, '| Dashboard in der Seite:', pg.locator('#dci-overlay.dci-inline').count())
    ok5 = pressed == 'true' and pg.locator('#dci-overlay.dci-inline').count() == 1
    # 6) "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults"): window again
    H.open_reset(pg); pg.click('[data-act=reset-do]'); pg.wait_for_timeout(500)
    print('6) nach ↺ Standard: Fenster', pg.locator('#dci-overlay.dci-inline').count() == 0, '| Seitenleiste:', pg.locator('#dci-launcher [data-place=window]').get_attribute('aria-pressed'))
    ok6 = pg.locator('#dci-overlay.dci-inline').count() == 0 and pg.locator('#dci-launcher [data-place=window]').get_attribute('aria-pressed') == 'true'
    print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4, ok5, ok6]) else 'FEHLER', [ok1, ok2, ok3, ok4, ok5, ok6], '| Fehler:', errs)
    b.close()
