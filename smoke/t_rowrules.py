"""Credits Importer 3.30.2: rule ids at rows open the mapping rules as a window, the arrow in the head of an entry
(collected items 75b, 82b; the maintainer's answers of 2026-10-25 01:59).
A) A rule id at a row opens the rules as a window (not in the dashboard, where the symbol opens them; nothing stored),
   at that rule; the row stays where it was on the screen.
B) The symbol in the head closes that window; the symbol again opens the rules in the dashboard.
C) "Into the dashboard" in such a window: in the dashboard (the place stays "in the dashboard", nothing stored).
D) ⚙ Settings → Appearance "Rule ids and ⓘ at rows open them: like the symbol" (stored "symbol"): a rule id opens them in
   the dashboard.
E) Compact view: the arrow ▸ in the head of an entry opens all its rows (▾); one row closed again: ▸; ▸ opens all,
   ▾ closes all."""
from playwright.sync_api import sync_playwright
import harness as H

STATE = """(() => { const r = document.getElementById('dci-rules'); const dock = document.querySelector('#dci-overlay [data-el=rules-dock]');
  return { open: !!(r && !r.hidden), docked: !!(r && dock && dock.contains(r) && r.classList.contains('dci-rules-docked')), position: r ? getComputedStyle(r).position : '',
    hit: (document.querySelector('#dci-rules tr.dci-rule-hit') || {dataset: {}}).dataset.rid || null, stored: [localStorage.getItem('dci-rules-place'), localStorage.getItem('dci-rules-rowplace')],
    pressed: document.querySelector('.dci-head [data-act=rules]').getAttribute('aria-expanded') }; })()"""
RULES = '.dci-head [data-act=rules]'
ROWID = "section.dci-group:has(.dci-gname strong:text-is('Bob Producer')) tr.dci-row [data-act=rule-goto]"
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.set_viewport_size({'width': 1300, 'height': 900})
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(600)
    st = lambda: pg.evaluate(STATE)
    # A)
    btn = pg.locator(ROWID).first
    btn.scroll_into_view_if_needed()
    rid = btn.get_attribute('data-rule')
    y0 = btn.evaluate('b => Math.round(b.getBoundingClientRect().top)')
    btn.click()
    pg.wait_for_timeout(500)
    a1 = st()
    y1 = pg.locator(ROWID).first.evaluate('b => Math.round(b.getBoundingClientRect().top)')
    print('A) Regel-ID', rid, '→', a1, '| Zeile vorher/nachher:', y0, y1)
    results.append(a1['open'] and not a1['docked'] and a1['position'] == 'fixed' and a1['hit'] == rid and a1['stored'] == [None, None] and abs(y1 - y0) <= 2)
    # B)
    pg.click(RULES)
    pg.wait_for_timeout(300)
    b1 = st()
    pg.click(RULES)
    pg.wait_for_timeout(300)
    b2 = st()
    print('B) Symbol schließt:', [b1['open'], b1['pressed']], '| Symbol öffnet:', [b2['open'], b2['docked']])
    results.append(not b1['open'] and b1['pressed'] == 'false' and b2['open'] and b2['docked'])
    pg.click(RULES)
    pg.wait_for_timeout(200)
    # C)
    pg.locator(ROWID).first.click()
    pg.wait_for_timeout(400)
    pg.click('#dci-rules [data-rules-place=dashboard]')
    pg.wait_for_timeout(300)
    c1 = st()
    print('C) „Into the dashboard“:', [c1['open'], c1['docked'], c1['stored']])
    results.append(c1['open'] and c1['docked'] and c1['stored'] == [None, None])
    pg.click(RULES)
    pg.wait_for_timeout(200)
    # D)
    H.open_settings(pg, 'appearance')
    d0 = pg.evaluate("[...document.querySelectorAll('.dci-set-pane [data-act=rules-rowplace]')].map(x => [x.dataset.place, x.getAttribute('aria-pressed')])")
    pg.click('.dci-set-pane [data-act=rules-rowplace][data-place=symbol]')
    pg.wait_for_timeout(200)
    pg.click('.dci-head [data-act=settings-open]')
    pg.locator(ROWID).first.click()
    pg.wait_for_timeout(400)
    d1 = st()
    print('D) Einstellung:', d0, '| wie das Symbol:', [d1['open'], d1['docked'], d1['stored']])
    results.append(d0 == [['window', 'true'], ['symbol', 'false']] and d1['open'] and d1['docked'] and d1['stored'] == [None, '"symbol"'])
    pg.click(RULES)
    pg.wait_for_timeout(200)
    # E) the arrow in the head (compact view): Bass Man with a second role
    sec = "section.dci-group:has(.dci-gname strong:text-is('Bass Man'))"
    pg.click(f'{sec} [data-act=add-role]')
    pg.wait_for_timeout(300)
    pg.click('.dci-head [data-act=view-toggle]')
    pg.wait_for_timeout(400)
    ARROW = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man');
      const a = g.querySelector('.dci-gname [data-act=group-openall]'); return [a ? a.textContent.trim() : null, a ? a.getAttribute('aria-expanded') : null,
      [...g.querySelectorAll('tr.dci-row')].map(tr => tr.classList.contains('dci-open'))]; })()"""
    pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man');
      g.querySelectorAll('tr.dci-row.dci-open .dci-cl-close').forEach(b => b.click()); })()""")
    pg.wait_for_timeout(300)
    e0 = pg.evaluate(ARROW)
    pg.click(f'{sec} .dci-gname [data-act=group-openall]')
    pg.wait_for_timeout(300)
    e1 = pg.evaluate(ARROW)
    pg.locator(f'{sec} tr.dci-row.dci-open .dci-cl-close').first.click()
    pg.wait_for_timeout(300)
    e2 = pg.evaluate(ARROW)
    pg.click(f'{sec} .dci-gname [data-act=group-openall]')
    pg.wait_for_timeout(300)
    e3 = pg.evaluate(ARROW)
    pg.click(f'{sec} .dci-gname [data-act=group-openall]')
    pg.wait_for_timeout(300)
    e4 = pg.evaluate(ARROW)
    print('E) Pfeil:', e0, e1, e2, e3, e4)
    results.append(e0 == ['▸', 'false', [False, False]] and e1 == ['▾', 'true', [True, True]] and e2[0] == '▸' and e2[2].count(True) == 1
                   and e3 == ['▾', 'true', [True, True]] and e4 == ['▸', 'false', [False, False]])
    pg.click('.dci-head [data-act=view-toggle]')
    pg.wait_for_timeout(300)
    e5 = pg.evaluate("document.querySelectorAll('.dci-gname [data-act=group-openall]').length")
    print('   volle Ansicht – Pfeile im Kopf:', e5)
    results.append(e5 == 0)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
