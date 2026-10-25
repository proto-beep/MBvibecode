"""Credits Importer 3.30.1: small fixes of the dashboard (collected items 86, 89, 91, 92, 95; 2026-10-25).
A) Two messages (dates from the notes), open and folded: the bar below ("Add entry manually") no longer covers
   "▾ 2 messages" / "▸ 2 messages" or the last message.
B) ⚙ Settings → Discogs and Bandcamp view ([3.30.5] Source pages): "on mouse-over" and "on click" have tooltips.
C) Compact: the level of a line switched by clicks (Recording → Release → Skip → Recording) stays at the same place; on
   Skip the line still shows its type (grey).
D) "only works": a button of its own next to the levels, underlined in the colour of works; "Stage:" on the line of
   its buttons.
E) In the page, inside a page of MusicBrainz that is 2400 px wide: the dashboard is no wider than the browser window."""
from playwright.sync_api import sync_playwright
import harness as H

# instruments on the release level exist in MusicBrainz too (as in t_levels.py)
H.lt(44, '67555849-61e5-455b-96e3-29733f0115f5', 'instrument', 'artist', 'release', (14, 1, 194, 596))
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
GAP = """(() => { const m = document.querySelector('[data-el=msgs]'); const s = document.querySelector('[data-el=stick]');
  const last = m.lastElementChild; return [Math.round(s.getBoundingClientRect().top - last.getBoundingClientRect().bottom), last.className]; })()"""
PILL = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man');
  const tr = g.querySelector('tr.dci-row'); const b = tr.querySelector('.dci-cl-level'); const t = tr.querySelector('.dci-cl-type');
  return [b.dataset.level, Math.round(b.getBoundingClientRect().left), t ? t.textContent.replace(/\\s+/g, ' ').trim() : null]; })()"""
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
    # A)
    a1 = pg.evaluate(GAP)
    pg.click('[data-act=msgs-fold]')
    pg.wait_for_timeout(300)
    a2 = pg.evaluate(GAP)
    print('A) Abstand zur Leiste – offen:', a1, '| eingeklappt:', a2)
    results.append(a1[0] >= 0 and a2[0] >= 0 and a2[1] == 'dci-msgs-head')
    # B)
    H.open_settings(pg, 'discogs')
    b1 = pg.evaluate("[...document.querySelectorAll('[data-el=settings] [data-sync-mode]')].map(x => [x.dataset.syncMode, x.title])")
    pg.click('.dci-head [data-act=settings-open]')
    print('B) Tooltips:', b1)
    results.append(len(b1) == 2 and all(t for _, t in b1) and 'rests on a row' in b1[0][1] and 'Only a click' in b1[1][1])
    # C)
    pg.click('.dci-head [data-act=view-toggle]')
    pg.wait_for_timeout(400)
    seq = [pg.evaluate(PILL)]
    for _ in range(4):
        pg.locator("section.dci-group:has(.dci-gname strong:text-is('Bass Man')) tr.dci-row .dci-cl-level").first.click()
        pg.wait_for_timeout(350)
        seq.append(pg.evaluate(PILL))
        if seq[-1][0] == 'recording':
            break
    print('C) Ebene, x, Typ:', seq)
    results.append([x[0] for x in seq] == ['recording', 'release', 'skip', 'recording'] and len({x[1] for x in seq}) == 1
                   and seq[2][2] == '→ instrument · bass')
    pg.click('.dci-head [data-act=view-toggle]')
    pg.wait_for_timeout(300)
    # D)
    d1 = pg.evaluate("""(() => { const ow = document.querySelector('[data-act=bulk-level][data-level=only-works]');
      const lv = document.querySelector('[data-act=bulk-level][data-level=skip]'); const st = document.querySelector('.dci-scope > .dci-sub');
      const sb = document.querySelector('.dci-scope button'); const c = (e) => { const r = e.getBoundingClientRect(); return r.top + r.height / 2; };
      return [ow.parentElement === lv.parentElement, getComputedStyle(ow).boxShadow, Math.round(Math.abs(c(st) - c(sb))),
        Math.round(ow.getBoundingClientRect().left - lv.getBoundingClientRect().right)]; })()""")
    print('D) only works – in der Ebenen-Gruppe, Schatten, „Stage:“ Abweichung, Abstand:', d1)
    results.append(not d1[0] and 'rgb(138, 79, 158)' in d1[1] and d1[2] <= 2 and d1[3] >= 4)
    # E) in the page, inside a wide page
    pg.evaluate("document.getElementById('content').style.width = '2400px'")
    H.open_settings(pg, 'appearance')
    pg.click('[data-el=settings] [data-act=place-toggle]')
    pg.wait_for_timeout(600)
    e1 = pg.evaluate("""(() => { const o = document.getElementById('dci-overlay'); const r = o.getBoundingClientRect();
      return [o.classList.contains('dci-inline'), Math.round(r.left), Math.round(r.right), document.documentElement.clientWidth,
        Math.round(document.getElementById('content').getBoundingClientRect().width)]; })()""")
    pg.set_viewport_size({'width': 1000, 'height': 900})
    pg.wait_for_timeout(400)
    e2 = pg.evaluate("(() => { const r = document.getElementById('dci-overlay').getBoundingClientRect(); return [Math.round(r.right), document.documentElement.clientWidth]; })()")
    print('E) in der Seite (in Seite, links, rechts, Fenster, Seite):', e1, '| schmaler:', e2)
    results.append(e1[0] and e1[2] <= e1[3] and e1[4] >= 2400 and e2[0] <= e2[1])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
