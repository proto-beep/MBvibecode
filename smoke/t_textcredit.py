"""Credits Importer 3.28.4: "credited as" from a text, the design of a part of the package, joined design tasks
(collected items 83, 84 and the maintainer's answers of 2026-10-24 19:33).
A) Discogs: "Cover Design", "Design [Sleeve]", "Artwork [Cover Design]", "Booklet Design", "Package Design" are design
   credited "cover design", "sleeve design", "cover design", "booklet design", "package design" (S037).
B) "Artwork [Design And Layout]": one row design credited "design and layout" (both tasks are design; S033) – not two;
   "Artwork [Logo Og Kunst]" stays two rows (design "logo", artwork "art"). Both name S033 at the row.
C) The field "Artist credit for all roles": empty for "VALFAR" (only the case differs from Valfar), "M. Mann" for Master
   Mann.
D) A pasted text: "Produced by Jane Roe" linked to the suggestion Jane A. Roe → credited "Jane Roe" (as in the text,
   S036); "Mixed by JOHN DOE" linked to John Doe → no "credited as" (only the case differs, S031); the row names S036."""
from playwright.sync_api import sync_playwright
import harness as H

H.lt(1202, '1d4c0b5b-0000-4000-8000-000000001202', 'artwork', 'artist', 'release', (1, 1150))
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
CREDITS = [('Cover Guy', 'Cover Design', 3031, ''), ('Sleeve Guy', 'Design [Sleeve]', 3032, ''), ('Art Guy', 'Artwork [Cover Design]', 3033, ''),
           ('Booklet Guy', 'Booklet Design', 3034, ''), ('Pack Guy', 'Package Design', 3035, ''), ('Lay Guy', 'Artwork [Design And Layout]', 3036, ''),
           ('Kunst Guy', 'Artwork [Logo Og Kunst]', 3037, ''), ('Valfar', 'Vocals', 3015, 'VALFAR'), ('Master Mann', 'Mastered By', 3012, 'M. Mann')]
for n, r, i, anv in CREDITS:
    H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
orig = H.discogs_release


def rel():
    d = orig()
    d['extraartists'] = [{'name': n, 'anv': anv, 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i, anv in CREDITS]
    d['companies'] = []
    for t in d['tracklist']:
        t['extraartists'] = []
    return d


H.discogs_release = rel
JANE, JOHN = H.uid('dddddddd', 80), H.uid('dddddddd', 81)
H.MB_SEARCH['artist'] = [{'id': JANE, 'name': 'Jane A. Roe', 'disambiguation': '', 'score': 100, 'aliases': []},
                         {'id': JOHN, 'name': 'John Doe', 'disambiguation': '', 'score': 100, 'aliases': []}]
ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  { all: (g.querySelector('[data-f=artist-credit-all]') || {}).value, rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]');
    const c = tr.querySelector('[data-f=role-credit]'); const cr = tr.querySelector('[data-f=credit]');
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', c ? c.value : '-', cr ? cr.value : '-',
      [...tr.querySelectorAll('.dci-ruleid')].map(b => b.textContent.trim())]; }) }])))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(1500)
    g = pg.evaluate(ROWS)
    for k, v in g.items():
        print('   ', k, v)
    first = lambda n: (g.get(n) or {'rows': [['', '', '', '', []]]})['rows'][0]
    # A)
    a1 = [first(n)[1:3] for n in ('Cover Guy', 'Sleeve Guy', 'Art Guy', 'Booklet Guy', 'Pack Guy')]
    print('A) Design-Teile:', a1)
    results.append(a1 == [['design', 'cover design'], ['design', 'sleeve design'], ['design', 'cover design'], ['design', 'booklet design'], ['design', 'package design']]
                   and all('S037' in first(n)[4] for n in ('Cover Guy', 'Sleeve Guy', 'Booklet Guy')))
    # B)
    lay, kunst = g.get('Lay Guy')['rows'], g.get('Kunst Guy')['rows']
    print('B) Design And Layout:', lay, '| Logo Og Kunst:', [x[:3] for x in kunst])
    results.append(len(lay) == 1 and lay[0][:3] == ['Artwork [Design And Layout]', 'design', 'design and layout'] and 'S033' in lay[0][4]
                   and [x[:3] for x in kunst] == [['Design [Logo]', 'design', 'logo'], ['Artwork [Art]', 'artwork', 'art']])
    # C)
    c1 = [g.get('Valfar')['all'], g.get('Master Mann')['all'], first('Valfar')[3]]
    print('C) Feld „für alle Rollen“ – Valfar, Master Mann; credited as Valfar:', c1)
    results.append(c1 == ['', 'M. Mann', ''])
    # D) a pasted text
    H.src_menu(pg, 'text-open')
    pg.fill('[data-f=text-src]', 'Produced by Jane Roe\nMixed by JOHN DOE')
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(1500)
    for name, mbid in [('Jane Roe', JANE), ('JOHN DOE', JOHN)]:
        sec = f"section.dci-group:has(.dci-gname strong:text-is('{name}'))"
        pg.locator(f'{sec} [data-act=name-use][data-mbid="{mbid}"]').first.click()
        pg.wait_for_timeout(800)
    e = pg.evaluate(ROWS)
    d1 = [(e.get('Jane Roe') or {'rows': [[]]})['rows'][0], (e.get('JOHN DOE') or {'rows': [[]]})['rows'][0]]
    print('D) Text:', d1)
    results.append(d1[0][3] == 'Jane Roe' and 'S036' in d1[0][4] and d1[1][3] == '')
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
