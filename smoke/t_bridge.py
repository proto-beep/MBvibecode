"""Credits Importer 3.30.4: the settings join their tabs, a bridge from ⚙ and "Mapping rules" to what they opened
(collected item 87; the maintainer's screenshots of 2026-10-25 01:59).
A) ⚙ Settings open: ⚙ pressed (tinted), a bridge from it to the box of the settings – below the symbol down to the head's
   lower edge, from there to the box, as wide as the symbol.
B) Every tab: the content starts at the height of the chosen tab and the tab reaches into its frame – at 100 % and at
   90 % text size (until 3.30.3 the tabs below the content had nothing to join, at 90 % the tab stood out).
C) "Mapping rules" in the dashboard: their symbol has the bridge, ⚙ not.
D) The box scrolled away: only the part at the symbol stays; back: the whole bridge.
E) Both closed: no bridge, nothing pressed."""
from playwright.sync_api import sync_playwright
import harness as H

BR = """(act) => { const btn = document.querySelector('.dci-head [data-act=' + act + ']'); const box = act === 'rules' ? document.querySelector('[data-el=rules-dock]') : document.querySelector('[data-el=settings]');
  const head = document.querySelector('.dci-head').getBoundingClientRect(); const b = btn.getBoundingClientRect(); const p = box.getBoundingClientRect(); const cs = getComputedStyle(box);
  const v = (k) => parseFloat(cs.getPropertyValue(k)) || 0;
  return { expanded: btn.getAttribute('aria-expanded'), bg: getComputedStyle(btn).backgroundColor, btnBridge: btn.classList.contains('dci-bridged'),
    down: parseFloat(getComputedStyle(btn).getPropertyValue('--dci-bridge-down')) || 0, downOk: Math.abs(b.bottom - 1 + (parseFloat(getComputedStyle(btn).getPropertyValue('--dci-bridge-down')) || 0) - head.bottom) <= 2,
    boxBridge: box.classList.contains('dci-bridged-box'), xOk: Math.abs(p.left + box.clientLeft + v('--dci-bridge-x') - b.left) <= 1, wOk: Math.abs(v('--dci-bridge-w') - b.width) <= 1,
    hOk: Math.abs(p.top - v('--dci-bridge-h') - head.bottom) <= 1 }; }"""
TABS = """(() => { const el = document.querySelector('[data-el=settings]'); const pane = el.querySelector('.dci-set-pane').getBoundingClientRect();
  const sel = el.querySelector('.dci-set-tab[aria-selected=true]').getBoundingClientRect();
  return [Math.round(pane.top - sel.top), Math.round(sel.right - pane.left)]; })()"""
TOPICS = ['general', 'appearance', 'sources', 'texts', 'discogs', 'works', 'staging', 'dates', 'connections']
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.set_viewport_size({'width': 1400, 'height': 900})
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(600)
    # A)
    H.open_settings(pg, 'general')
    pg.wait_for_timeout(300)
    a1 = pg.evaluate(BR, 'settings-open')
    print('A) ⚙:', a1)
    results.append(a1['expanded'] == 'true' and a1['bg'] == 'rgb(236, 235, 246)' and a1['btnBridge'] and a1['down'] > 0 and a1['downOk']
                   and a1['boxBridge'] and a1['xOk'] and a1['wOk'] and a1['hOk'])
    # B)
    b1 = {}
    for t in TOPICS:
        H.open_settings(pg, t)
        pg.wait_for_timeout(150)
        b1[t] = pg.evaluate(TABS)
    pg.click('[data-act=zoom-out]')
    pg.wait_for_timeout(300)
    b2 = {}
    for t in ('discogs', 'staging', 'dates'):
        H.open_settings(pg, t)
        pg.wait_for_timeout(150)
        b2[t] = pg.evaluate(TABS)
    a2 = pg.evaluate(BR, 'settings-open')
    pg.click('[data-act=zoom-in]')
    pg.wait_for_timeout(300)
    print('B) Inhalt − Reiter oben, Überlappung (100 %):', b1, '\n   90 %:', b2, '| Brücke 90 %:', [a2['xOk'], a2['hOk'], a2['downOk']])
    results.append(all(abs(d) <= 1 and 0 <= o <= 3 for d, o in list(b1.values()) + list(b2.values())) and a2['xOk'] and a2['hOk'] and a2['downOk'])
    # C)
    pg.click('.dci-head [data-act=rules]')
    pg.wait_for_timeout(400)
    c1, c2 = pg.evaluate(BR, 'rules'), pg.evaluate(BR, 'settings-open')
    print('C) Regeln:', c1, '| ⚙:', [c2['expanded'], c2['btnBridge']])
    results.append(c1['expanded'] == 'true' and c1['btnBridge'] and c1['boxBridge'] and c1['xOk'] and c1['hOk'] and c2['expanded'] == 'false' and not c2['btnBridge'])
    # D) scrolled away
    pg.evaluate("document.querySelector('#dci-overlay .dci-body').scrollTop = 400")
    pg.wait_for_timeout(300)
    d1 = pg.evaluate(BR, 'rules')
    pg.evaluate("document.querySelector('#dci-overlay .dci-body').scrollTop = 0")
    pg.wait_for_timeout(300)
    d2 = pg.evaluate(BR, 'rules')
    print('D) weggescrollt:', [d1['btnBridge'], d1['boxBridge']], '| zurück:', [d2['btnBridge'], d2['boxBridge'], d2['hOk']])
    results.append(d1['btnBridge'] and not d1['boxBridge'] and d2['btnBridge'] and d2['boxBridge'] and d2['hOk'])
    # E)
    pg.click('.dci-head [data-act=rules]')
    pg.wait_for_timeout(300)
    e1, e2 = pg.evaluate(BR, 'rules'), pg.evaluate(BR, 'settings-open')
    print('E) zu:', [e1['expanded'], e1['btnBridge'], e2['expanded'], e2['btnBridge'], e1['bg']])
    results.append(e1['expanded'] == 'false' and not e1['btnBridge'] and not e2['btnBridge'] and e1['bg'] == 'rgb(255, 255, 255)')
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
