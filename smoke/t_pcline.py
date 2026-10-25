"""Credits Importer 3.30.9: "© & ℗ TUM Records Oy 2021" – the label for ℗ and © (collected item 99; answers of
2026-10-25 08:55: "nur wenn P und C auch erwähnt sind. falls nur P oder nur C einzeln erwähnt sind soll jeweils nur das
angeboten werden").
A) Discogs notes "© & ℗ TUM Records Oy 2021", Discogs lists no ℗/©: the entry TUM Records Oy with phonographic copyright
   and copyright (the year stays a date of the pool); MusicBrainz's TUM Records Oy and TUM Records are both suggested
   (T044: without the legal form "Oy"), another label not.
B) Discogs lists "Copyright (c) – TUM Records Oy": only ℗ comes from the notes, onto Discogs's entry.
C) A pasted text: "℗ 2020 Solo P Records" only phonographic copyright, "© Solo C Records 2019" only copyright,
   "© & ℗ TUM Records Oy 2021" both."""
from playwright.sync_api import sync_playwright
import harness as H

NOTES = 'Recorded in Helsinki.\n\n© & ℗ TUM Records Oy 2021'
TUM_OY, TUM, OTHER = H.uid('eeeeeeee', 21), H.uid('eeeeeeee', 22), H.uid('eeeeeeee', 23)
H.MB_SEARCH['label'] = [{'id': TUM_OY, 'name': 'TUM Records Oy', 'disambiguation': '', 'score': 100},
                        {'id': TUM, 'name': 'TUM Records', 'disambiguation': '', 'score': 100},
                        {'id': OTHER, 'name': 'TUM Recordings Ltd', 'disambiguation': '', 'score': 90}]
H.COMPANIES[1021] = ('label', H.uid('eeeeeeee', 24), 'TUM Records Oy (linked)')
C_LISTED = [False]
orig = H.discogs_release


def rel():
    d = orig()
    d['notes'] = NOTES
    d['companies'] = [c for c in d['companies'] if 'Copyright' not in c['entity_type_name']]
    if C_LISTED[0]:
        d['companies'].append({'name': 'TUM Records Oy', 'entity_type_name': 'Copyright (c)', 'id': 1021, 'catno': ''})
    return d


H.discogs_release = rel
GROUP = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  return g ? { roles: [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim()), sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.dataset.mbid) } : null; }"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(1500)
    a1 = pg.evaluate(GROUP, 'TUM Records Oy')
    pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => [d.name, d.begin.year])")
    print('A) TUM Records Oy:', a1, '| Pool:', pool)
    results.append(a1 and a1['roles'] == ['Phonographic Copyright (p)', 'Copyright (c)'] and TUM_OY in a1['sugg'] and TUM in a1['sugg'] and OTHER not in a1['sugg']
                   and any(y == 2021 for _, y in pool))
    # C) a pasted text
    H.src_menu(pg, 'text-open')
    pg.fill('[data-f=text-src]', '℗ 2020 Solo P Records\n© Solo C Records 2019\n© & ℗ TUM Records Oy 2021')
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(1200)
    c1 = {n: (pg.evaluate(GROUP, n) or {}).get('roles') for n in ('Solo P Records', 'Solo C Records', 'TUM Records Oy')}
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    print('C) Text:', c1, '| nicht erkannt:', unrec)
    results.append(c1 == {'Solo P Records': ['Phonographic Copyright (p)'], 'Solo C Records': ['Copyright (c)'], 'TUM Records Oy': ['Phonographic Copyright (p)', 'Copyright (c)']}
                   and not unrec)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()

# B) Discogs lists the copyright already
C_LISTED[0] = True
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(1500)
    names = pg.evaluate("[...document.querySelectorAll('section.dci-group .dci-gname strong')].map(x => x.textContent.trim())")
    b1 = [(n, pg.evaluate(GROUP, n)['roles']) for n in names if 'TUM' in n]
    print('B) Discogs listet ©:', b1)
    results.append(len(b1) == 1 and b1[0][1] == ['Copyright (c)', 'Phonographic Copyright (p)'])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
