"""Credits Importer 3.29.2: the colours of the levels, the level in the compact line switched by a click, the tab
"Appearance" (collected items 79, 81; the maintainer's answers of 2026-10-24 17:42 and 19:23).
The Discogs notes give two performance dates; the June date of the column "Performance" is marked "Release level"
(as in t_reldate.py).
A) Colours on by default: the chosen level of a row filled in its colour (recording blue, release green), the other
   levels underlined in theirs; in the compact view the level of the line in the same colour.
B) Compact: a click on the level of "Bass Man" (Recording, a tooltip names the next one) switches to Release – the
   date of the line follows (June 5); further clicks go through the levels the row can have, then Skip, then back to
   Recording with the March dates. The focus stays on the level.
C) ⚙ Settings → Appearance (after "General"): text size, place, view and the colours (General has neither any more).
   A colour chosen for Release: stored, the line in it (white text on a dark colour); colours off: the chosen level
   dark as before 3.29.2, stored; "↺" of the tab: colours on again, the own colour gone."""
from playwright.sync_api import sync_playwright
import harness as H

H.lt(44, '67555849-61e5-455b-96e3-29733f0115f5', 'instrument', 'artist', 'release', (14, 1, 194, 596))
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
orig = H.discogs_release


def release():
    d = orig()
    d['notes'] = 'Recorded March 1–3, 2001 at Abbey Road Studios. Recorded live at the release concert June 5, 2001.'
    return d


H.discogs_release = release
SEC = "[...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === '{name}')"
PRESSED = """(name) => { const g = """ + SEC.replace("'{name}'", 'name') + """; const tr = g.querySelector('tr.dci-row');
  const on = tr.querySelector('[data-act=level][aria-pressed=true]'); const off = tr.querySelector('[data-act=level]:not([aria-pressed=true])');
  return [on.dataset.level, getComputedStyle(on).backgroundColor, off ? getComputedStyle(off).boxShadow : '']; }"""
PILL = """(name) => { const g = """ + SEC.replace("'{name}'", 'name') + """; const tr = g.querySelector('tr.dci-row');
  const b = tr.querySelector('.dci-cl-level'); const d = tr.querySelector('.dci-cl-date');
  return [b.dataset.level, b.textContent.trim(), b.title || '', getComputedStyle(b).backgroundColor, getComputedStyle(b).color, d ? d.textContent.trim() : '',
    b.tagName, document.activeElement && document.activeElement.dataset.act === 'level-next']; }"""
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
    cells = pg.evaluate("[...document.querySelectorAll('.dci-dm-col[data-dmcol=performance] .dci-dm-cell')].map(c => [c.dataset.id, c.querySelector('.dci-chip-main').textContent.trim()])")
    june = next(cid for cid, t in cells if '2001-06-05' in t)
    pg.check(f'[data-f=dm-rel][data-cell="{june}"]')
    pg.wait_for_timeout(300)
    pg.evaluate("(() => { const g = " + SEC.format(name='Guitar Guy') + "; g.querySelector('tr.dci-row [data-act=level][data-level=release]').click(); })()")
    pg.wait_for_timeout(300)
    pg.locator('[data-el=dates] .dci-apply').first.evaluate('b => b.click()')
    pg.wait_for_timeout(800)
    # A) full view
    a1 = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-lvlc')"), pg.evaluate(PRESSED, 'Bass Man'), pg.evaluate(PRESSED, 'Guitar Guy')]
    print('A) Farben an, Bass Man, Guitar Guy:', a1)
    results.append(a1[0] and a1[1][:2] == ['recording', 'rgb(47, 109, 181)'] and a1[2][:2] == ['release', 'rgb(46, 139, 87)'] and 'inset' in a1[1][2])
    # B) compact: the level by a click
    pg.click('.dci-head [data-act=view-toggle]')
    pg.wait_for_timeout(400)
    seq = [pg.evaluate(PILL, 'Bass Man')]
    for _ in range(6):
        pg.locator("section.dci-group:has(.dci-gname strong:text-is('Bass Man')) tr.dci-row .dci-cl-level").first.click()
        pg.wait_for_timeout(400)
        seq.append(pg.evaluate(PILL, 'Bass Man'))
        if seq[-1][0] == 'recording':
            break
    for x in seq:
        print('   ', x)
    levels = [x[0] for x in seq]
    print('B) Ebenen nacheinander:', levels)
    results.append(levels[:2] == ['recording', 'release'] and levels[-2:] == ['skip', 'recording'] and len(set(levels)) == len(levels) - 1
                   and seq[0][2] == 'Level – a click switches to “Release”' and seq[0][3] == 'rgb(47, 109, 181)' and seq[0][6] == 'BUTTON'
                   and seq[0][5].endswith('2001-03-01 – 2001-03-03') and seq[1][5].endswith('2001-06-05') and seq[1][3] == 'rgb(46, 139, 87)'
                   and seq[-1][5].endswith('2001-03-01 – 2001-03-03') and seq[-2][5] == '' and all(x[7] for x in seq[1:]))
    # C) the tab "Appearance"
    H.open_settings(pg, 'general')
    gen = pg.evaluate("[!!document.querySelector('.dci-set-pane [data-act=zoom-in]'), !!document.querySelector('.dci-set-pane [data-act=view]'), !!document.querySelector('.dci-set-pane [data-f=lang]')]")
    H.open_settings(pg, 'appearance')
    app = pg.evaluate("""[!!document.querySelector('.dci-set-pane [data-act=zoom-in]'), !!document.querySelector('.dci-set-pane [data-act=view]'),
      !!document.querySelector('.dci-set-pane [data-act=place-toggle]'), document.querySelector('.dci-set-pane [data-set=level-colors]').checked,
      [...document.querySelectorAll('.dci-set-pane [data-set=level-color]')].map(x => [x.dataset.level, x.value]),
      document.querySelector('[data-el=settings] .dci-set-tab[aria-selected=true]').textContent.trim()]""")
    print('C) Allgemein (Zoom, Ansicht, Sprache):', gen, '| Darstellung:', app)
    results.append(gen == [False, False, True] and app[:4] == [True, True, True, True] and app[5] == 'Appearance'
                   and app[4] == [['recording', '#2f6db5'], ['release', '#2e8b57'], ['release_group', '#b0700c'], ['work', '#8a4f9e']])
    pg.evaluate("""(() => { const x = document.querySelector('.dci-set-pane [data-set=level-color][data-level=release]'); x.value = '#aa0000';
      x.dispatchEvent(new Event('input', { bubbles: true })); x.dispatchEvent(new Event('change', { bubbles: true })); })()""")
    pg.wait_for_timeout(300)
    pg.locator("section.dci-group:has(.dci-gname strong:text-is('Bass Man')) tr.dci-row .dci-cl-level").first.click()
    pg.wait_for_timeout(400)
    c1 = [pg.evaluate("localStorage.getItem('dci-level-palette')"), pg.evaluate(PILL, 'Bass Man')[:5:3] + pg.evaluate(PILL, 'Bass Man')[4:5]]
    pg.locator('.dci-set-pane [data-set=level-colors]').click()
    pg.wait_for_timeout(300)
    pg.click('.dci-head [data-act=view-toggle]')
    pg.wait_for_timeout(400)
    c2 = [pg.evaluate("localStorage.getItem('dci-level-colors')"), pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-lvlc')"),
          pg.evaluate(PRESSED, 'Bass Man')[:2], pg.evaluate("document.querySelector('.dci-set-pane [data-set=level-color]').disabled")]
    pg.click('[data-el=settings] [data-act=settings-reset][data-topic=appearance]')
    pg.wait_for_timeout(500)
    c3 = [pg.evaluate("[localStorage.getItem('dci-level-colors'), localStorage.getItem('dci-level-palette')]"),
          pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-lvlc')"), pg.evaluate(PRESSED, 'Bass Man')[:2]]
    print('C) eigene Farbe:', c1, '| aus:', c2, '| ↺:', c3)
    results.append(c1 == ['{"release":"#aa0000"}', ['release', 'rgb(170, 0, 0)', 'rgb(255, 255, 255)']]
                   and c2 == ['false', False, ['release', 'rgb(61, 58, 79)'], True]
                   and c3 == [[None, None], True, ['release', 'rgb(46, 139, 87)']])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
