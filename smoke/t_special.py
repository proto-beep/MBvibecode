"""Import 3.15.1: special purpose artists are left out of the comparison with the works of the artists.
A) The release's artist credit names Various Artists (its MBID, T026), "[soundtrack]" (any name in square brackets) and
   Test Band: only Test Band is asked for its works; Various Artists' work with the title of track 4 is not offered,
   Test Band's work with the title of track 3 is.
B) The log names each special artist once – also after the dashboard is drawn anew (a level changed).
C) "Mapping rules" lists the table T026."""
from playwright.sync_api import sync_playwright
import harness as H

VA = '89ad4ac3-39f7-470e-963a-56509c546377'
ST = H.uid('dddddddd', 61)
TB = H.uid('dddddddd', 60)
W3, W4 = H.uid('cccccccc', 83), H.uid('cccccccc', 84)
H.RELEASE_AC[:] = [(VA, 'Various Artists', 'Various Artists', ' & '), (ST, '[soundtrack]', '[soundtrack]', ' & '),
                   (TB, 'Test Band', 'Test Band', '')]
H.ARTIST_WORKS.update({VA: [{'id': W4, 'title': H.TITLES[3], 'type': 'Song', 'aliases': []}],
                       ST: [{'id': W4, 'title': H.TITLES[3], 'type': 'Song', 'aliases': []}],
                       TB: [{'id': W3, 'title': H.TITLES[2], 'type': 'Song', 'aliases': []}]})
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
    pg.wait_for_timeout(300)
    asked = sorted({a for _, a, _ in H.BROWSES})
    offered = {i: pg.evaluate(f"[...document.querySelectorAll('tr[data-work=\"{i}\"] .dci-same [data-act=work-pick]')].map(b => b.dataset.gid)") for i in (2, 3)}
    print('A) gefragt:', ['VA' if a == VA else 'soundtrack' if a == ST else 'Test Band' if a == TB else a[-3:] for a in asked], '| Track 3:', offered[2], '| Track 4:', offered[3])
    results.append(VA not in asked and ST not in asked and TB in asked and offered[2] == [W3] and offered[3] == [])
    # B) drawn anew: no second log line
    bass = pg.locator('section.dci-group').filter(has=pg.locator('.dci-gname strong', has_text='Bass Man')).first
    bass.locator('[data-act=level][data-level=skip]').first.click(); pg.wait_for_timeout(1200)
    bass.locator('[data-act=level][data-level=recording]').first.click(); pg.wait_for_timeout(1200)
    special = [x for x in pg.evaluate(LOGS) if 'special purpose' in x]
    print('B) Protokoll:', special)
    results.append(special == ['Various Artists: a special purpose artist (Various Artists, [unknown] …) – its works are not compared',
                               '[soundtrack]: a special purpose artist (Various Artists, [unknown] …) – its works are not compared'])
    # C) the table in "Mapping rules"
    pg.locator('[data-act=rules]').first.click()
    pg.wait_for_selector('#dci-rules [data-rsect=lists]', timeout=10000)
    t026 = pg.evaluate("[...document.querySelectorAll('#dci-rules [data-rsect=lists] *')].some(e => /T026/.test(e.textContent) && /89ad4ac3-39f7-470e-963a-56509c546377/.test(e.textContent))")
    print('C) T026 im Regelfenster:', t026)
    results.append(t026)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
