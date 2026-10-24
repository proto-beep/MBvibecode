"""Credits Importer 3.25.0: the settings as tabs (collected items 42, 41, 40).
A) "⚙ Settings" folds the settings out and in (only the gear: no "Close" inside); eight tabs, "General" chosen.
B) Keys: ↓ the next tab (chosen, focused), End the last, Home the first.
C) The tab is remembered (here "Texts", with "Show the web links …" and a button to "Mapping rules"); after reloading
   the settings open on it.
D) The ⓘ in the head opens the settings at "ⓘ Connections": a table of ten connections (Harmony with its home page,
   kind, what the script does, permissions, since).
E) "↺ Reset all settings …" below the tabs shows the question in the settings (no tab chosen); "Cancel" goes back to
   the tab. The head has no "↺ Defaults" any more.
F) A narrow dashboard: the tabs stand in a row above the content."""
from playwright.sync_api import sync_playwright
import harness as H

SET = "document.querySelector('[data-el=settings]')"
TABS = f"[...{SET}.querySelectorAll('.dci-set-tab')].map(b => [b.dataset.topic, b.getAttribute('aria-selected'), document.activeElement === b])"
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    # A)
    gear = '.dci-head [data-act=settings-open]'
    pg.click(gear)
    pg.wait_for_timeout(300)
    t1 = pg.evaluate(TABS)
    a = [pg.evaluate(f"!{SET}.hidden"), pg.evaluate(f"{SET}.querySelectorAll('[data-act=settings-open]').length"), pg.locator(gear).get_attribute('aria-expanded')]
    pg.click(gear)
    pg.wait_for_timeout(200)
    a.append(pg.evaluate(f"{SET}.hidden"))
    print('A) Tabs:', [(t, s) for t, s, _ in t1], '| offen, Schließen innen, aria, wieder zu:', a)
    results.append([t for t, _, _ in t1] == ['general', 'sources', 'texts', 'discogs', 'works', 'staging', 'dates', 'connections']
                   and [t for t, s, _ in t1 if s == 'true'] == ['general'] and a == [True, 0, 'true', True])
    # B) keys
    pg.click(gear)
    pg.wait_for_timeout(200)
    pg.focus('[data-el=settings] .dci-set-tab[data-topic=general]')
    pg.keyboard.press('ArrowDown')
    pg.wait_for_timeout(150)
    k1 = [(t, f) for t, s, f in pg.evaluate(TABS) if s == 'true']
    pg.keyboard.press('End')
    pg.wait_for_timeout(150)
    k2 = [(t, f) for t, s, f in pg.evaluate(TABS) if s == 'true']
    pg.keyboard.press('Home')
    pg.wait_for_timeout(150)
    k3 = [(t, f) for t, s, f in pg.evaluate(TABS) if s == 'true']
    print('B) ↓:', k1, '| Ende:', k2, '| Pos1:', k3)
    results.append(k1 == [('sources', True)] and k2 == [('connections', True)] and k3 == [('general', True)])
    # C) remembered
    pg.click('[data-el=settings] .dci-set-tab[data-topic=texts]')
    pg.wait_for_timeout(200)
    c1 = [pg.evaluate("localStorage.getItem('dci-settings-tab')"), pg.evaluate(f"!!{SET}.querySelector('.dci-set-pane [data-set=weblinks-show]')"),
          pg.evaluate(f"!!{SET}.querySelector('.dci-set-pane [data-act=rules]')")]
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.click(gear)
    pg.wait_for_timeout(300)
    c2 = [t for t, s, _ in pg.evaluate(TABS) if s == 'true']
    print('C) gespeichert, Links-Einstellung, Regeln-Knopf:', c1, '| nach Neuladen gewählt:', c2)
    results.append(c1 == ['"texts"', True, True] and c2 == ['texts'])
    pg.click(gear)
    # D) the ⓘ in the head
    pg.click('.dci-head [data-act=connections-open]')
    pg.wait_for_timeout(300)
    d1 = pg.evaluate(f"""(() => {{ const rows = [...{SET}.querySelectorAll('.dci-conn tbody tr')];
      const h = rows.find(r => r.dataset.conn === 'X005');
      return [rows.length, h ? [...h.cells].map(c => c.textContent.trim().slice(0, 40)) : null, h ? h.querySelector('a').href : '',
        [...{SET}.querySelectorAll('.dci-set-tab')].filter(b => b.getAttribute('aria-selected') === 'true').map(b => b.dataset.topic)]; }})()""")
    print('D) Verbindungen:', d1)
    results.append(d1[0] == 10 and d1[1][0] == 'Harmony' and d1[1][1] == 'Tool' and d1[1][2].startswith('Adds “Edit relationships with Credits')
                   and d1[1][3].startswith('@match harmony.pulsewidth.org.uk') and d1[1][4] == '3.19.1' and d1[2] == 'https://harmony.pulsewidth.org.uk/'
                   and d1[3] == ['connections'])
    # E) reset all, in the settings
    pg.click('[data-el=settings] .dci-set-tab[data-topic=works]')
    pg.click('[data-el=settings] [data-act=reset-open]')
    pg.wait_for_timeout(200)
    e1 = [pg.evaluate(f"!!{SET}.querySelector('.dci-set-pane [data-el=reset] [data-act=reset-do]')"),
          [t for t, s, _ in pg.evaluate(TABS) if s == 'true'], pg.evaluate("document.activeElement.dataset.act")]
    pg.click('[data-el=settings] [data-act=reset-cancel]')
    pg.wait_for_timeout(200)
    e2 = [pg.evaluate(f"!!{SET}.querySelector('[data-el=reset]')"), [t for t, s, _ in pg.evaluate(TABS) if s == 'true'],
          pg.evaluate("document.querySelectorAll('.dci-head [data-act=reset-open]').length")]
    print('E) Frage in den Einstellungen, gewählt, Fokus:', e1, '| nach Abbrechen:', e2)
    results.append(e1 == [True, [], 'reset-cancel'] and e2 == [False, ['works'], 0])
    # F) narrow
    tops = f"[...{SET}.querySelectorAll('.dci-set-tab')].slice(0, 2).map(b => Math.round(b.getBoundingClientRect().top))"
    wide = pg.evaluate(tops)
    pg.evaluate("(() => { const p = document.querySelector('#dci-overlay .dci-panel'); p.style.width = '470px'; })()")
    pg.wait_for_timeout(400)
    narrow = pg.evaluate(tops)
    print('F) breit (oben):', wide, '| schmal:', narrow)
    results.append(wide[0] != wide[1] and narrow[0] == narrow[1])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
