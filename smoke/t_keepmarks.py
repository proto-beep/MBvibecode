"""Credits Importer 3.17.5 / Companion 1.8.3: a click on a mark switches its credit, also on Discogs (collected item 20),
and the marks can stay after the editor is closed (collected item 23).
A) Discogs: the pointer resting on a mark shows its row in the dashboard (no line in the log); a click on the mark
   switches the credit off ("Skip", the mark greyed –, its line greyed), another click on again (its level back).
B) "Click switches" off (navigation): a click on a mark shows its row (as before), nothing is switched.
C) "Keep marks" off (default): the marks go when the editor is closed. On: they stay with the last state after the
   editor is closed; a click on them does nothing then; switched off again (in a dashboard), they go."""
from playwright.sync_api import sync_playwright
import harness as H

LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
MARK = """(n) => { const li = [...document.querySelectorAll('#release-credits li')].find(l => l.textContent.includes(n));
  const m = li && li.querySelector('.dci-dg-mark'); return m ? [m.textContent, m.classList.contains('dci-mark-off'), li.classList.contains('dci-dg-offline'), m.title] : null; }"""
LEVEL = """(n) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === n);
  const lv = g && g.querySelector('tr.dci-row [data-act=level][aria-pressed=true]'); return lv ? lv.dataset.level : null; }"""
MARKS = "document.querySelectorAll('.dci-dg-mark').length"
results = []


def poll(pg, js, timeout=20):
    for _ in range(timeout * 5):
        try:
            if pg.evaluate(js):
                return True
        except Exception:
            pass
        pg.wait_for_timeout(200)
    raise TimeoutError(js)


def editor(ctx):
    pg, errs = H.open_mb_edit(ctx)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
    return pg, errs


mark = lambda dg, n: dg.evaluate(f"({MARK})('{n}')")
level = lambda pg, n: pg.evaluate(f"({LEVEL})('{n}')")
real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg, dgerr = H.open_discogs(ctx)
    pg, errs = editor(ctx)
    poll(dg, f"({MARK})('Bass Man') !== null")
    # A) hover shows the row, a click switches
    lv0 = level(pg, 'Bass Man')
    dg.locator('#release-credits li', has_text='Bass Man').locator('.dci-dg-mark').hover()
    H.wait_for(pg, "document.querySelectorAll('tr.dci-flash').length > 0", 10)
    a0 = [pg.evaluate("[...document.querySelectorAll('tr.dci-flash')].map(t => t.closest('section').querySelector('.dci-gname strong').textContent.trim())"),
          [x for x in pg.evaluate(LOGS) if 'From Discogs' in x]]
    dg.mouse.move(5, 5)
    dg.locator('#release-credits li', has_text='Bass Man').locator('.dci-dg-mark').click()
    poll(dg, f"(({MARK})('Bass Man') || [])[1] === true")
    a1 = [level(pg, 'Bass Man'), mark(dg, 'Bass Man')[:3], [x for x in pg.evaluate(LOGS) if 'switched off' in x]]
    dg.locator('#release-credits li', has_text='Bass Man').locator('.dci-dg-mark').click()
    poll(dg, f"(({MARK})('Bass Man') || [])[1] === false")
    a2 = [level(pg, 'Bass Man'), mark(dg, 'Bass Man')[:3]]
    print('A) Zeiger → Zeile:', a0, '| Klick:', a1, '| noch ein Klick:', a2, '(vorher', lv0, ')')
    results.append(a0 == [['Bass Man'], []] and a1[0] == 'skip' and a1[1] == ['–', True, True] and a1[2] == ['Discogs: Bass Man – Bass switched off (“Skip”)']
                   and a2[0] == lv0 and a2[1][1:] == [False, False])
    # B) "Click switches" off: a click shows the row
    pg.locator('#dci-controls [data-click-toggle]').evaluate('b => b.click()')
    poll(dg, f"!(({MARK})('Guitar Guy') || [''])[3].includes('skip')")
    title = mark(dg, 'Guitar Guy')[3]
    dg.locator('#release-credits li', has_text='Guitar Guy').locator('.dci-dg-mark').click()
    H.wait_for(pg, f"{LOGS}.some(x => /From Discogs: Guitar Guy/.test(x))", 10)
    b1 = [level(pg, 'Guitar Guy'), mark(dg, 'Guitar Guy')[1], title]
    print('B) „Klick schaltet“ aus:', b1)
    results.append(b1[0] != 'skip' and b1[1] is False and 'click to show it in the dashboard' in b1[2])
    pg.locator('#dci-controls [data-click-toggle]').evaluate('b => b.click()')
    # C) keep marks: off – they go; on – they stay
    pg.wait_for_timeout(1200)
    pg.close()
    poll(dg, f"{MARKS} === 0", 15)
    pg, errs2 = editor(ctx)
    poll(dg, f"{MARKS} > 0")
    pg.locator('#dci-controls [data-keep-marks]').evaluate('b => b.click()')
    H.wait_for(pg, f"{LOGS}.some(x => /Marks kept after the editor is closed: on/.test(x))", 10)
    pg.wait_for_timeout(1500)
    n0 = dg.evaluate(MARKS)
    pg.close()
    dg.wait_for_timeout(12000)
    c1 = dg.evaluate(MARKS)
    before = len(H.STORE.changes)
    dg.locator('#release-credits li', has_text='Bass Man').locator('.dci-dg-mark').click()
    dg.wait_for_timeout(800)
    sent = [c for c in H.STORE.changes[before:] if c['k'] == 'fromDiscogs']
    H.STORE.set('keepMarks', False)
    poll(dg, f"{MARKS} === 0", 10)
    print('C) aus: Marken weg | an: vorher', n0, 'nach dem Schließen', c1, '| Klick sendet:', len(sent), '| wieder aus: weg')
    results.append(n0 > 0 and c1 == n0 and not sent)
    print('Fehler:', real(errs), real(errs2), real(dgerr))
    results.append(not real(errs) and not real(errs2) and not real(dgerr))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
