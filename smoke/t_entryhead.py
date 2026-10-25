"""Credits Importer 3.28.0: the head of an entry and the bar below "Import credits …" (collected items 61, 66).
A) Only the tag of the source links to it (with ↗; its tooltip names the source's name) – the name is not repeated.
B) How the dashboard credits the entry: "as “B. Man”" (Discogs credits Bass Man as "B. Man" on this release), the
   tooltip lists the credits; the MusicBrainz name (no "credited as") – no chip. A row credited otherwise: "as “B. Man”
   (+1)" at the head, the compact line of each row names its own credit.
C) The bar below "Import credits …" (with the companion): the status as a badge (source link, "open in background")
   and ⚙ – no switches of the navigation any more; ⚙ opens the settings of the dashboard at "Discogs and Bandcamp view" ([3.30.5] "Source pages")."""
from playwright.sync_api import sync_playwright
import harness as H

orig = H.discogs_release


def rel():
    d = orig()
    for ea in d['extraartists']:
        if ea['name'] == 'Bass Man':
            ea['anv'] = 'B. Man'
    d['extraartists'].append({'name': 'Bass Man', 'anv': 'B. Man', 'role': 'Vocals', 'tracks': '', 'id': 3001, 'join': ''})
    return d


H.discogs_release = rel
HEAD = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; const a = g.querySelector('.dci-dglink'); const c = g.querySelector('.dci-gcredit');
  return { link: a ? [a.textContent, a.getAttribute('href'), a.title] : null, chip: c && !c.hidden ? [c.textContent.trim(), c.title] : null }; }"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(600)
    head = lambda name: pg.evaluate(HEAD, name)
    # A)
    a1 = head('Guitar Guy')
    print('A) Guitar Guy:', a1)
    results.append(a1['link'] == ['Discogs↗', 'https://www.discogs.com/artist/3002', 'Open on Discogs: Guitar Guy'] and a1['chip'] is None)
    # B)
    b1 = head('Bass Man')
    sec = "section.dci-group:has(.dci-gname strong:text-is('Bass Man'))"
    rows = pg.locator(f'{sec} tr.dci-row')
    print('B) Bass Man:', b1, '| Zeilen:', rows.count())
    first = rows.nth(0).locator('[data-f=credit]')
    first.fill('Bassman')
    first.dispatch_event('change')
    pg.wait_for_timeout(500)
    b2 = head('Bass Man')
    pg.click('.dci-head [data-act=view-toggle]')
    pg.wait_for_timeout(400)
    lines = pg.evaluate(f"[...document.querySelectorAll(\"section.dci-group\")].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man')"
                        ".querySelectorAll('.dci-cl-as').length")
    pg.click('.dci-head [data-act=view-toggle]')
    print('   anders credited:', b2, '| Zeilen mit eigenem Credit (kompakt):', lines)
    results.append(b1['chip'] and b1['chip'][0] == 'as “B. Man”' and '“B. Man”' in b1['chip'][1]
                   and b2['chip'] and b2['chip'][0] in ('as “Bassman” (+1)', 'as “B. Man” (+1)') and lines == 2)
    # C) the bar below "Import credits …"
    pg.click('.dci-head [data-act=close]')
    pg.wait_for_timeout(300)
    c1 = pg.evaluate("""(() => { const bar = document.getElementById('dci-controls'); return [!bar.hidden, bar.querySelectorAll('[data-sync-mode], [data-dg-status], [data-dg-hover], [data-click-toggle], [data-keep-marks], [data-dg-artwork]').length,
      !!bar.querySelector('.dci-syncstatus'), (bar.querySelector('.dci-syncstatus') || {}).textContent, !!bar.querySelector('[data-nav-settings]')]; })()""")
    pg.locator('#dci-controls [data-nav-settings]').click()
    pg.wait_for_timeout(600)
    c2 = [pg.evaluate("!document.getElementById('dci-overlay').hidden"), pg.evaluate("!document.querySelector('[data-el=settings]').hidden"),
          pg.evaluate("[...document.querySelectorAll('.dci-set-tab')].filter(t => t.getAttribute('aria-selected') === 'true').map(t => t.dataset.topic)"),
          pg.evaluate("!!document.querySelector('[data-el=settings] .dci-set-pane [data-dg-status]')")]
    print('C) Leiste:', c1, '| ⚙ →', c2)
    results.append(c1[0] and c1[1] == 0 and c1[2] and 'Discogs view' in c1[3] and c1[4] and c2 == [True, True, ['discogs'], True])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
