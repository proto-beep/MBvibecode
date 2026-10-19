"""Import 3.14.0: rules for free credits texts (any source: a pasted text, Bandcamp credits).
A) "Music played and recorded by X in March and April 2025" → X played by (performer) and recorded by; the time is cut
   off the name. "Mixed and mastered by X in May 2025" → mixed by, mastered by. "Layout by X" (the role is "Layout").
   "Photography Sam Lee" (a role, then a name, no separator); "mastering john doe" (small letters).
B) The dates: "March and April 2025" is one period 2025-03 – 2025-04; "May 2025".
C) "A Northern Echo release." is left out (not listed as not recognized); prose stays not recognized; [3.21.0] thanks are
   listed apart as left out on purpose.
D) "Music and artwork of this release were entirely created by a (cat assisted) human. No AI tools were used.": no name
   – the release's artist is offered for music and artwork, as its own entry with a suggestion; nothing is assigned."""
from playwright.sync_api import sync_playwright
import harness as H

JR = H.uid('dddddddd', 60)
H.RELEASE_AC[:] = [(JR, 'Jane Roe', 'Jane Roe', '')]
H.MB_SEARCH['artist'] = [{'id': JR, 'name': 'Jane Roe', 'disambiguation': '', 'score': 100}]
TEXT = """Music played and recorded by Jane Roe in March and April 2025.

Mixed and mastered by Jane Roe in May 2025.

Photography Sam Lee.
Layout by Jane Roe.
mastering john doe

Music and artwork of this release were entirely created by a (cat assisted) human. No AI tools were used.

A Northern Echo release.
We had a great time together
Thanks to the cat for keeping us company"""
GROUPS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim()),
  // 3.15.2: the explanation of the suggestions is the stack's tooltip
  (g.querySelector('.dci-sugg-stack') || {}).title || '',
  [...g.querySelectorAll('[data-act=name-use]')].map(b => b.dataset.mbid), g.className.match(/dci-st-(\\w+)/)[1]]))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.click('[data-act=text-open]')
    pg.fill('[data-f=text-src]', TEXT)
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(800)
    g = pg.evaluate(GROUPS)
    for x in g:
        print('   ', x)
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    ign = pg.evaluate("[...document.querySelectorAll('.dci-ignored li')].map(li => li.textContent)")
    pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => [JSON.stringify(d.begin), JSON.stringify(d.end)].join(' '))")
    print('   nicht erkannt:', unrec, '| ausgelassen:', ign)
    print('   Pool:', pool)
    named = [x for x in g if x[0] == 'Jane Roe' and 'names no one' not in x[2]]
    ok_a = bool(named) and named[0][1] == ['Played By', 'Recorded By', 'Mixed By', 'Mastered By', 'Layout'] \
        and ['Sam Lee', ['Photography By']] in [x[:2] for x in g] and ['john doe', ['Mastering']] in [x[:2] for x in g]
    ok_b = '{"year":2025,"month":3,"day":null} {"year":2025,"month":4,"day":null}' in pool and '{"year":2025,"month":5,"day":null} {"year":2025,"month":5,"day":null}' in pool
    ok_c = unrec == ['We had a great time together'] and ign == ['Thanks to the cat for keeping us company']
    ph = [x for x in g if x[0] == 'Jane Roe' and 'names no one' in x[2]]
    ok_d = bool(ph) and 'a human' in ph[0][2] and ph[0][3] == [JR] and ph[0][4] == 'missing' and ph[0][1] == ['Artwork']
    mark = pg.evaluate("[...document.querySelectorAll('.dci-sugg-stack [data-act=name-use] .dci-similar')].map(x => x.textContent)")
    print('   Marken an Vorschlägen:', mark)
    ok_d = ok_d and 'release artist' in mark
    works = pg.evaluate("[...document.querySelectorAll('[data-el=works] .dci-mx-colhead, [data-el=works] th')].map(x => x.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /Jane Roe/.test(t))")
    print('   Werke-Matrix (Jane Roe):', works[:2])
    print('A)', ok_a, '| B)', ok_b, '| C)', ok_c, '| D)', ok_d)
    results += [ok_a, ok_b, ok_c, ok_d, bool(works)]
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
