"""Import 3.12.1: two fixes.
A) "n lines not recognized" opens in the window too (the source sits in the head of the window, which moves it; a
   press on the list started moving the window, so the list never opened).
B) Same-named works are looked up again when the writers of a track change: a pasted text names "Written by Agusti
   Fernández (2, 3)"; the name is only a suggestion, so at the import the tracks have no writers and nothing is
   searched. A click on the suggestion assigns him – his work with the title of track 2 is found then.
C) Without a writer change nothing is searched again (no second query).
D) A new import starts the work search anew: the results of the import before (here the linked Discogs release,
   loaded first) do not stay – the text import searches its tracks itself (it did not, before 3.12.1)."""
from playwright.sync_api import sync_playwright
import harness as H

AG = H.uid('dddddddd', 50)
GID = H.uid('eeeeeeee', 70)
H.MB_SEARCH['artist'] = [{'id': AG, 'name': 'Agustí Fernández', 'disambiguation': 'pianist', 'score': 100}]
H.WORK_SEARCH.append({'id': GID, 'title': H.TITLES[1], 'aliases': [], 'type': 'Song',
                      'relations': [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': AG, 'name': 'Agustí Fernández'}}]})
TEXT = """Written by Agusti Fernández (2, 3)
Bass Man – bass
thanks to everybody"""
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
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 30)
    pg.wait_for_timeout(500)
    # A) the list opens in the window
    inline = pg.evaluate("!!document.querySelector('.dci-inline')")
    pg.click('.dci-unrec summary'); pg.wait_for_timeout(300)
    opened = pg.evaluate("document.querySelector('.dci-unrec').open")
    lines = pg.locator('.dci-unrec li').all_inner_texts()
    print('A) im Fenster:', not inline, '| aufgeklappt:', opened, '|', lines)
    results.append(not inline and opened and lines == ['thanks to everybody'])
    # D) the text import searched itself (two "Checks complete": Discogs, then the text), nothing "again" yet
    checks = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'Checks complete' in x]
    again0 = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'looked up again' in x]
    print('D) Prüfungen:', [c[9:] for c in checks], '| neu gesucht vor dem Klick:', len(again0))
    ok_d = len(checks) == 2 and not again0
    # B) before: no writers, no query with him; after the click: searched, found
    before = [q for q in H.WORK_QUERIES if AG in q]
    same0 = pg.locator(f'.dci-same [data-act=work-pick][data-gid="{GID}"]').count()
    pg.locator('[data-act=name-use]').first.click()
    H.wait_for(pg, f"!!document.querySelector('.dci-same [data-act=work-pick][data-gid=\"{GID}\"]')", 20)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Checks complete/.test(li.textContent)).length >= 2", 20)
    pg.wait_for_timeout(1500)

    after = [q for q in H.WORK_QUERIES if AG in q]
    log = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'looked up again' in x]
    print('B) vorher Anfragen:', len(before), 'gefunden:', same0, '| nachher Anfragen:', len(after), '|', log)
    results.append(not before and same0 == 0 and len(after) == 2 and log == ['The writers of 2 tracks changed – their same-named works are looked up again'])
    # C) nothing changes → no further query
    n = len(H.WORK_QUERIES)
    bass = pg.locator('section.dci-group').filter(has=pg.locator('.dci-gname strong', has_text='Bass Man')).first
    bass.locator('[data-act=level][data-level=skip]').first.click(); pg.wait_for_timeout(300)
    bass.locator('[data-act=level][data-level=recording]').first.click(); pg.wait_for_timeout(1500)
    print('C) weitere Anfragen nach Ebenen-Wechsel eines Instruments:', len(H.WORK_QUERIES) - n)
    results.append(len(H.WORK_QUERIES) == n)
    results.append(ok_d)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
