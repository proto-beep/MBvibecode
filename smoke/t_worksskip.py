"""Credits Importer 3.18.0: the works matrix can be skipped and folded (collected item 26), and with many tracks the
works section asks before the work lookups.
A) The head of the works matrix folds and unfolds it ("▾ Works matrix"): folded, only its head and what it holds are
   shown; the fold is not stored (after a reload the matrix is unfolded again).
B) "Skip works matrix": the matrix folds, says "skipped", its rows (writers, publishers) go to "Skip", nothing of it is
   staged (no links to works – also not of works marked as new – and no work relationships); the work lookups stop.
   Stored for this release: after a reload it is still skipped, its rows on "Skip" at once and no work is looked up.
   Meanwhile a row has no works level (the button says why). Before and after, the work rows are in the matrix.
C) "Take works matrix again": the rows come back to the works level, the matrix unfolds, the lookups run.
D) From so many tracks without a work (setting "Ask before the work lookups from …", 100; here 3) the works section
   asks first, with about how long it takes; nothing is looked up until then. "Not now" leaves out only the lookups
   (the matrix stays); "Look up now" starts them later. The setting is in the menu, topic Works (100 by default).
   [3.19.3] The question and the setting say in a tooltip what is counted (tracks without a work).
G) [3.19.3] Setting "Show the rows skipped with the works matrix with their entries" (on): off, their entry says how
   many are not shown; on again, they are back."""
from playwright.sync_api import sync_playwright
import harness as H

LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
HEAD = """(() => { const w = document.querySelector('[data-el=works]'); if (!w || w.hidden) return null;
  const f = w.querySelector('[data-act=mx-fold]'); const s = w.querySelector('[data-act=mx-skip]');
  return { fold: f ? [f.textContent.trim(), f.getAttribute('aria-expanded')] : null, skip: s ? [s.textContent.trim(), s.dataset.on] : null,
    table: !!w.querySelector('table.dci-matrix'), cols: w.querySelectorAll('thead th[data-col], thead .dci-mx-colhead').length,
    folded: (w.querySelector('[data-el=works-folded]') || {}).textContent || '', badge: (w.querySelector('.dci-works-skipped') || {}).textContent || '',
    off: w.classList.contains('dci-works-off'), ask: (w.querySelector('[data-el=works-ask]') || {}).textContent || '',
    later: (w.querySelector('[data-el=works-lookups-off]') || {}).textContent || '' }; })()"""
LEVEL = """(n) => { const g = [...document.querySelectorAll('section.dci-group, .dci-companies section, .dci-companies .dci-group')]
  .find(s => (s.querySelector('.dci-gname strong') || {}).textContent?.trim() === n);
  const lv = g && g.querySelector('tr.dci-row [data-act=level][aria-pressed=true]'); return lv ? lv.dataset.level : null; }"""
PLAN = """(() => { const b = document.querySelector('[data-act=preview]'); if (b.getAttribute('aria-expanded') !== 'true') b.click();
  return document.querySelector('[data-el=preview]').textContent.replace(/\\s+/g, ' '); })()"""
results = []


def click(pg, sel):
    pg.locator(sel).first.evaluate('b => b.click()')


def head(pg):
    return pg.evaluate(HEAD)


def level(pg, n):
    return pg.evaluate(f"({LEVEL})('{n}')")


def logs(pg, rx):
    return [x for x in pg.evaluate(LOGS) if __import__('re').search(rx, x)]


def start(ctx, wait='Checks complete'):
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    pg.click('#dci-open')
    H.wait_for(pg, f"{LOGS}.some(x => /{wait}/.test(x))", 60)
    pg.wait_for_timeout(1200)
    return pg, errs


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = start(ctx)
    # A) fold / unfold
    a0 = head(pg)
    click(pg, '[data-el=works] [data-act=mx-fold]')
    a1 = head(pg)
    click(pg, '[data-el=works] [data-act=mx-fold]')
    a2 = head(pg)
    print('A) offen:', a0)
    print('   zu:', a1)
    print('   wieder auf:', a2['fold'], a2['table'])
    results.append(a0['fold'] == ['▾ Works matrix', 'true'] and a0['table'] and a0['skip'] == ['Skip works matrix', '1']
                   and a1['fold'] == ['▸ Works matrix', 'false'] and not a1['table'] and '4 tracks' in a1['folded'] and 'column' in a1['folded']
                   and a2['fold'][1] == 'true' and a2['table'])
    # B) skip: mark new works first (links planned), then skip
    click(pg, '[data-el=works] [data-act=works-pending-all]')
    pg.wait_for_timeout(500)
    plan0 = pg.evaluate(PLAN)
    lv0 = [level(pg, 'Writer W'), level(pg, 'Pub Co')]
    q0 = len(H.WORK_QUERIES)
    click(pg, '[data-el=works] [data-act=mx-skip]')
    pg.wait_for_timeout(600)
    b1 = head(pg)
    plan1 = pg.evaluate(PLAN)
    lv1 = [level(pg, 'Writer W'), level(pg, 'Pub Co')]
    stored = pg.evaluate(f"localStorage.getItem('dci-works-skip:{H.REL}')")
    print('B) vorher:', lv0, '| Plan: Werk-Links', plan0.count('Link work'), '| Writer W', plan0.count('Writer W'), '| Pub Co', plan0.count('Pub Co'))
    print('   übersprungen:', b1, lv1, '| gespeichert:', stored)
    print('   Plan danach: Werk-Links', plan1.count('Link work'), '| Writer W', plan1.count('Writer W'), '| Pub Co', plan1.count('Pub Co'))
    print('   Protokoll:', logs(pg, 'Works matrix'))
    ok_b = (lv0 == [None, None] and 'Link work' in plan0 and 'Writer W' in plan0 and b1['badge'] == 'skipped' and b1['skip'] == ['Take works matrix again', '0']
            and not b1['table'] and b1['off'] and lv1 == ['skip', 'skip'] and stored == 'true'
            and 'Link work' not in plan1 and 'Writer W' not in plan1 and 'Pub Co' not in plan1)
    # no works level for a row while the matrix is skipped
    wbtn = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Writer Z');
      const b = g && g.querySelector('tr.dci-row [data-act=level][data-level=work]'); return b ? [b.disabled, b.title] : null; })()""")
    print('   Writer Z, Werk-Ebene:', wbtn)
    ok_b = ok_b and wbtn is not None and wbtn[0] and 'works matrix is skipped' in wbtn[1]
    pg.close()
    # stored: reload – still skipped, no work looked up
    H.BROWSES.clear()
    q1 = len(H.WORK_QUERIES)
    pg, errs2 = start(ctx, 'Import complete')
    pg.wait_for_timeout(2500)
    b2 = head(pg)
    lv2 = [level(pg, 'Writer W'), level(pg, 'Pub Co')]
    print('   neu geladen:', b2['badge'], b2['table'], lv2, '| Werk-Abfragen:', len(H.WORK_QUERIES) - q1, len(H.BROWSES))
    results.append(ok_b and b2['badge'] == 'skipped' and not b2['table'] and lv2 == ['skip', 'skip'] and len(H.WORK_QUERIES) == q1 and not H.BROWSES)
    # C) take it again
    click(pg, '[data-el=works] [data-act=mx-skip]')
    H.wait_for(pg, f"{LOGS}.some(x => /Checks complete/.test(x))", 60)
    pg.wait_for_timeout(800)
    c1 = head(pg)
    lv3 = [level(pg, 'Writer W'), level(pg, 'Pub Co')]
    stored = pg.evaluate(f"localStorage.getItem('dci-works-skip:{H.REL}')")
    print('C) wieder genommen:', c1['fold'], c1['table'], c1['badge'], lv3, '| gespeichert:', stored, '| Abfragen:', len(H.WORK_QUERIES) - q1)
    print('   Protokoll:', logs(pg, 'Works matrix'))
    results.append(c1['fold'][1] == 'true' and c1['table'] and not c1['badge'] and lv3 == [None, None] and stored is None and len(H.WORK_QUERIES) > q1)
    pg.close()
    # D) the question for many tracks
    pg = ctx.new_page()
    pg.goto(f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
    pg.evaluate("localStorage.setItem('dci-aw-ask', '3')")
    pg.close()
    H.BROWSES.clear()
    q2 = len(H.WORK_QUERIES)
    pg, errs3 = start(ctx, 'Import complete')
    pg.wait_for_timeout(2500)
    d1 = head(pg)
    n1 = [len(H.WORK_QUERIES) - q2, len(H.BROWSES)]
    tip = pg.evaluate("document.querySelector('[data-el=works-ask] strong').title")
    print('D) Frage:', d1['ask'], '| Abfragen bis dahin:', n1, '| Matrix:', d1['table'], '| Tooltip:', tip)
    click(pg, '[data-el=works] [data-act=mx-lookups][data-on=\"0\"]')
    pg.wait_for_timeout(600)
    d2 = head(pg)
    n2 = [len(H.WORK_QUERIES) - q2, len(H.BROWSES)]
    print('   „Jetzt nicht“:', d2['later'], '| Matrix:', d2['table'], '| Abfragen:', n2)
    click(pg, '[data-el=works] [data-el=works-lookups-off] [data-act=mx-lookups]')
    H.wait_for(pg, f"{LOGS}.some(x => /Checks complete/.test(x))", 60)
    d3 = head(pg)
    print('   später abgefragt:', len(H.WORK_QUERIES) - q2, '| Hinweis weg:', not d3['later'], '| Protokoll:', logs(pg, 'Work lookups|without a work'))
    results.append('Look up works for 3 tracks without a work?' in d1['ask'] and 'about 1 min' in d1['ask'] and n1 == [0, 0] and d1['table']
                   and 'Work lookups left out' in d2['later'] and d2['table'] and not d2['ask'] and n2 == [0, 0]
                   and len(H.WORK_QUERIES) > q2 and not d3['later'] and not d3['ask'])
    # the setting in the menu
    pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
    pg.wait_for_timeout(300)
    pg.locator('[data-act=settings-topic][data-topic=works]').evaluate('b => b.click()')
    pg.wait_for_timeout(300)
    f = pg.evaluate("(() => { const i = document.querySelector('[data-set=awAsk]'); return i ? [i.value, i.min, i.getAttribute('aria-label'), i.closest('label').textContent.replace(/\\s+/g, ' ').trim(), i.closest('label').title] : null; })()")
    pg.evaluate("localStorage.removeItem('dci-aw-ask')")
    print('   Einstellung:', f)
    results.append(f is not None and f[0] == '3' and f[1] == '0' and 'tracks without a work (0: never)' in f[3]
                   and tip.startswith('Counted are the tracks without a work') and f[4] == tip)
    # G) [3.19.3] the rows skipped with the works matrix: shown with their entries (setting, on) or not
    click(pg, '[data-el=works] [data-act=mx-skip]')
    pg.wait_for_timeout(500)
    GROUP = """(n) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === n);
      return g ? [g.querySelectorAll('tr.dci-row').length, [...g.querySelectorAll('.dci-work-note')].map(p => p.textContent.trim())] : null; }"""
    g1 = pg.evaluate(f"({GROUP})('Writer W')")
    pg.locator('[data-set=mx-skiprows]').evaluate('i => i.click()')
    pg.wait_for_timeout(400)
    g2 = [pg.evaluate(f"({GROUP})('Writer W')"), pg.evaluate("localStorage.getItem('dci-mx-skiprows')")]
    pg.locator('[data-set=mx-skiprows]').evaluate('i => i.click()')
    pg.wait_for_timeout(400)
    g3 = [pg.evaluate(f"({GROUP})('Writer W')"), pg.evaluate("localStorage.getItem('dci-mx-skiprows')")]
    click(pg, '[data-el=works] [data-act=mx-skip]')
    pg.wait_for_timeout(500)
    print('G) übersprungen, gezeigt:', g1, '| Einstellung aus:', g2, '| wieder an:', g3)
    results.append(g1 is not None and g1[0] >= 1 and g2[0][0] == 0 and g2[0][1] == ['1 row skipped with the works matrix is not shown (setting)'] and g2[1] == 'false'
                   and g3[0][0] == g1[0] and g3[1] is None)
    print('Fehler:', errs, errs2, errs3)
    results.append(not errs and not errs2 and not errs3)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
