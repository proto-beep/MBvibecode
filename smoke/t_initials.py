"""Import 3.13.0: name suggestions for names with an initial. MusicBrainz's search needs every word of a name, and
"T" is no word of "Torben" – so a name with an initial is searched with its written-out words too; the comparison
(same / similar name) decides, a middle name or initial more or less counts as similar.
A) "T. Snekkestad" → "Torben Snekkestad" (similar name); "Barry J. Guy" → "Barry John Guy" (similar name).
B) Another first name is no suggestion: "K. Tanaka" → "Kenji Tanaka", not "Hiro Tanaka".
C) Nothing is assigned by itself; names without an initial need no second search."""
from playwright.sync_api import sync_playwright
import harness as H

H.MB_SEARCH['artist'] = [
    {'id': H.uid('dddddddd', 52), 'name': 'Torben Snekkestad', 'disambiguation': '', 'score': 100},
    {'id': H.uid('dddddddd', 51), 'name': 'Barry John Guy', 'disambiguation': 'bassist', 'score': 100},
    {'id': H.uid('dddddddd', 53), 'name': 'Kenji Tanaka', 'disambiguation': '', 'score': 100},
    {'id': H.uid('dddddddd', 54), 'name': 'Hiro Tanaka', 'disambiguation': '', 'score': 100},
    {'id': H.uid('dddddddd', 55), 'name': 'Agustí Fernández', 'disambiguation': 'pianist', 'score': 100},
]
TEXT = """T. Snekkestad – guitar
Barry J. Guy – double bass
K. Tanaka – drums
Agusti Fernández – piano"""
ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [[...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()), g.className.match(/dci-st-(\\w+)/)[1]]])))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    queries = []
    pg.on('request', lambda r: queries.append(r.url) if '/ws/2/artist?' in r.url else None)
    pg.click('[data-act=text-open]')
    pg.fill('[data-f=text-src]', TEXT)
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(800)
    g = pg.evaluate(ROWS)
    for k, v in g.items():
        print('   ', k, v)
    ok_a = g['T. Snekkestad'][0] == ['Torben Snekkestad similar name'] and g['Barry J. Guy'][0] == ['Barry John Guy (bassist) similar name']
    ok_b = g['K. Tanaka'][0] == ['Kenji Tanaka similar name']
    ag = [q for q in queries if 'Fern' in q or 'fern' in q]
    print('A)', ok_a, '| B)', ok_b, '| Anfragen für Agusti:', len(ag))
    ok_c = all(v[1] == 'missing' for v in g.values()) and len(ag) == 1 and g['Agusti Fernández'][0] == ['Agustí Fernández (pianist)']
    results += [ok_a, ok_b, ok_c]
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
