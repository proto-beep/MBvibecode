"""Credits Importer 3.29.3: the arrow next to "Artist credit for all roles" (collected item 82; the maintainer's
answer of 2026-10-24 19:33: "nur bis zum nächsten Import").
A) Full view: the arrow ▾ of "Bass Man" folds his rows to compact lines (▸, the tooltip says so); "Artist credit for
   all roles" stays; the other entries keep their fields; the focus stays on the arrow.
B) A click on a line of the folded entry opens that row with all its fields; "▴ compact" closes it again.
C) ▸ shows the rows with their fields again.
D) Folded, then imported again: every entry full again.
E) Compact view: the arrow of an entry with an open row closes its open rows."""
from playwright.sync_api import sync_playwright
import harness as H

SEC = "section.dci-group:has(.dci-gname strong:text-is('{name}'))"
STATE = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; const a = g.querySelector('[data-act=group-fold]'); const v = g.querySelector('.dci-variants');
  return { folded: g.classList.contains('dci-gcompact'), arrow: a ? [a.textContent.trim(), a.getAttribute('aria-expanded'), a.title] : null,
    arrowNextToCredit: !!(a && a.nextElementSibling && a.nextElementSibling.classList.contains('dci-credit')),
    variants: !!(v && v.offsetParent !== null),
    rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const c = tr.querySelector('.dci-c-cline'); const t = tr.querySelector('[data-f=type]');
      return [tr.dataset.row, !!(c && c.offsetParent !== null && c.textContent.trim()), !!(t && t.offsetParent !== null), tr.classList.contains('dci-open')]; }),
    focus: document.activeElement && document.activeElement.dataset.act === 'group-fold' && g.contains(document.activeElement) }; }"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(800)
    st = lambda name: pg.evaluate(STATE, name)
    a0 = st('Bass Man')
    pg.click(f"{SEC.format(name='Bass Man')} [data-act=group-fold]")
    pg.wait_for_timeout(400)
    a1, g1 = st('Bass Man'), st('Guitar Guy')
    print('A) vorher:', a0, '\n   eingeklappt:', a1, '\n   Guitar Guy:', g1)
    results.append(a0['arrow'][:2] == ['▾', 'true'] and a0['arrowNextToCredit'] and not a0['folded'] and all(r[2] and not r[1] for r in a0['rows'])
                   and a1['folded'] and a1['arrow'][:2] == ['▸', 'false'] and 'Bass Man' in a1['arrow'][2] and a1['variants'] and a1['focus']
                   and all(r[1] and not r[2] for r in a1['rows']) and not g1['folded'] and all(r[2] for r in g1['rows']))
    # B) a line opens its row
    rid = a1['rows'][0][0]
    pg.click(f'tr[data-row="{rid}"] .dci-cl-role')
    pg.wait_for_timeout(300)
    b1 = st('Bass Man')['rows'][0]
    pg.click(f'tr[data-row="{rid}"] .dci-cl-close')
    pg.wait_for_timeout(300)
    b2 = st('Bass Man')['rows'][0]
    print('B) geöffnet:', b1, '| wieder zu:', b2)
    results.append(b1[2] and b1[3] and b2[1] and not b2[2] and not b2[3])
    # C) unfolded
    pg.click(f"{SEC.format(name='Bass Man')} [data-act=group-fold]")
    pg.wait_for_timeout(400)
    c1 = st('Bass Man')
    print('C) ausgeklappt:', c1)
    results.append(not c1['folded'] and c1['arrow'][:2] == ['▾', 'true'] and all(r[2] for r in c1['rows']))
    # D) folded, imported again
    pg.click(f"{SEC.format(name='Bass Man')} [data-act=group-fold]")
    pg.wait_for_timeout(300)
    d0 = st('Bass Man')['folded']
    H.src_menu(pg)
    pg.fill('[data-f=discogs-input]', f'https://www.discogs.com/release/{H.DISCOGS_ID}-x')
    pg.click('[data-act=discogs-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 60)
    pg.wait_for_timeout(800)
    d1 = st('Bass Man')
    print('D) eingeklappt:', d0, '| nach dem Import:', d1['folded'], [r[2] for r in d1['rows']])
    results.append(d0 and not d1['folded'] and all(r[2] for r in d1['rows']))
    # E) compact view: the arrow closes the open rows
    pg.click('.dci-head [data-act=view-toggle]')
    pg.wait_for_timeout(400)
    rid = st('Bass Man')['rows'][0][0]
    pg.click(f'tr[data-row="{rid}"] .dci-cl-role')
    pg.wait_for_timeout(300)
    e0 = st('Bass Man')
    pg.click(f"{SEC.format(name='Bass Man')} [data-act=group-fold]")
    pg.wait_for_timeout(400)
    e1 = st('Bass Man')
    print('E) kompakt, offen:', e0['rows'][0], e0['arrow'], '| nach dem Pfeil:', e1['rows'][0], e1['variants'])
    results.append(e0['rows'][0][3] and e0['arrow'][1] == 'true' and 'Close the open roles' in e0['arrow'][2] and not e1['rows'][0][3] and e1['rows'][0][1] and not e1['variants'])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
