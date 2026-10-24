"""Credits Importer 3.30.0: "Mapping rules" in the dashboard (collected item 75; the maintainer's answer of
2026-10-24 17:42: "ja standardmäßig im Dashboard und ja soll sich die Einstellung merken. ja nur eines öffnen und das
andere schließen").
A) By default the symbol "Mapping rules" in the head opens them in the dashboard below its head (not a window of their
   own; the symbol pressed, the test field focused, "⧉ As window" in their head).
B) ⚙ Settings opened: the rules close; "Mapping rules" again: the settings close.
C) "⧉ As window": the rules float as a window (stored "window"), still open; ⚙ Settings leave the window open.
D) Reloaded: they open as a window again; ⚙ Settings → Appearance says "as a window"; "in the dashboard" there brings
   them back (nothing stored).
E) The symbol closes them again, Escape too.
F) A rule id at a row opens them in the dashboard at that rule (highlighted, in view)."""
from playwright.sync_api import sync_playwright
import harness as H

STATE = """(() => { const r = document.getElementById('dci-rules'); const dock = document.querySelector('#dci-overlay [data-el=rules-dock]');
  const set = document.querySelector('[data-el=settings]'); const b = document.querySelector('.dci-head [data-act=rules]');
  return { open: !!(r && !r.hidden && r.offsetParent !== null) || !!(r && !r.hidden && getComputedStyle(r).position === 'fixed'),
    docked: !!(r && dock && dock.contains(r) && r.classList.contains('dci-rules-docked')), dockShown: !!(dock && !dock.hidden),
    position: r ? getComputedStyle(r).position : '', pressed: b.getAttribute('aria-expanded'), settings: !!(set && !set.hidden),
    place: r ? (r.querySelector('[data-rules-place]') || {}).textContent : '', focus: !!(document.activeElement && document.activeElement.dataset.rf === 'test'),
    stored: localStorage.getItem('dci-rules-place') }; })()"""
RULES = '.dci-head [data-act=rules]'
GEAR = '.dci-head [data-act=settings-open]'
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(500)
    st = lambda: pg.evaluate(STATE)
    # A)
    pg.click(RULES)
    pg.wait_for_timeout(300)
    a1 = st()
    print('A) geöffnet:', a1)
    results.append(a1['open'] and a1['docked'] and a1['dockShown'] and a1['position'] == 'static' and a1['pressed'] == 'true' and a1['focus']
                   and a1['place'].strip() == '⧉ As window' and a1['stored'] is None)
    # B) only one of both
    pg.click(GEAR)
    pg.wait_for_timeout(300)
    b1 = st()
    pg.click(RULES)
    pg.wait_for_timeout(300)
    b2 = st()
    print('B) ⚙ auf:', [b1['open'], b1['settings'], b1['pressed']], '| Regeln wieder:', [b2['open'], b2['settings']])
    results.append(not b1['open'] and b1['settings'] and b1['pressed'] == 'false' and b2['open'] and not b2['settings'])
    # C) as a window
    pg.click('#dci-rules [data-rules-place=window]')
    pg.wait_for_timeout(300)
    c1 = st()
    pg.click(GEAR)
    pg.wait_for_timeout(300)
    c2 = st()
    print('C) als Fenster:', c1, '| ⚙ dazu:', [c2['open'], c2['settings']])
    results.append(c1['open'] and not c1['docked'] and not c1['dockShown'] and c1['position'] == 'fixed' and c1['stored'] == '"window"'
                   and c1['place'].strip() == 'Into the dashboard' and c2['open'] and c2['settings'])
    pg.click(GEAR)
    # D) remembered
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(800)
    pg.click(RULES)
    pg.wait_for_timeout(300)
    d1 = st()
    H.open_settings(pg, 'appearance')
    d2 = pg.evaluate("[...document.querySelectorAll('.dci-set-pane [data-act=rules-place]')].map(x => [x.dataset.place, x.getAttribute('aria-pressed')])")
    pg.click('.dci-set-pane [data-act=rules-place][data-place=dashboard]')
    pg.wait_for_timeout(300)
    d3 = st()
    print('D) neu geladen:', [d1['open'], d1['docked'], d1['position']], '| Darstellung:', d2, '| im Dashboard:', [d3['open'], d3['docked'], d3['stored'], d3['settings']])
    results.append(d1['open'] and not d1['docked'] and d1['position'] == 'fixed' and d2 == [['dashboard', 'false'], ['window', 'true']]
                   and d3['open'] and d3['docked'] and d3['stored'] is None and not d3['settings'])
    # E) closed by the symbol, by Escape
    pg.click(RULES)
    pg.wait_for_timeout(300)
    e1 = st()
    pg.click(RULES)
    pg.wait_for_timeout(300)
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(300)
    e2 = st()
    print('E) Symbol:', [e1['open'], e1['dockShown'], e1['pressed']], '| Escape:', [e2['open'], e2['dockShown'], pg.evaluate("!document.getElementById('dci-overlay').hidden")])
    results.append(not e1['open'] and not e1['dockShown'] and e1['pressed'] == 'false' and not e2['open'] and not e2['dockShown']
                   and pg.evaluate("!document.getElementById('dci-overlay').hidden"))
    # F) a rule id at a row
    rid = pg.evaluate("(document.querySelector('tr.dci-row [data-act=rule-goto]') || {}).dataset.rule")
    pg.locator(f'tr.dci-row [data-act=rule-goto][data-rule="{rid}"]').first.click()
    pg.wait_for_timeout(500)
    f1 = pg.evaluate("""(() => { const r = document.querySelector('#dci-rules tr.dci-rule-hit'); if (!r) return null;
      const body = document.querySelector('#dci-rules .dci-rules-body').getBoundingClientRect(); const rb = r.getBoundingClientRect();
      return [r.dataset.rid, rb.top >= body.top - 1 && rb.bottom <= body.bottom + 1]; })()""")
    print('F) Regel', rid, '→', f1, st()['docked'])
    results.append(f1 == [rid, True] and st()['docked'])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
