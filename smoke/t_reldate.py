"""Import 3.10.0: a date of the date matrix only for the release level.
The Discogs notes give two performance dates (the studio days in March, a release concert in June). In the column
"Performance" the June date is marked "Release level".
A) Applied: the rows on recordings take only the March dates (no copy for June), a row on the release level takes June.
B) A row switched from recording to the release level takes the June date at once; switched back, the March dates.
C) A date typed into a row by hand stays when the row changes its level.
D) The mark is stored with the matrix (after loading the dashboard again it is still there)."""
from playwright.sync_api import sync_playwright
import harness as H
from common_rows import rows_of

# instruments on the release level exist in MusicBrainz too
H.lt(44, '67555849-61e5-455b-96e3-29733f0115f5', 'instrument', 'artist', 'release', (14, 1, 194, 596))
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
orig = H.discogs_release


def release():
    d = orig()
    d['notes'] = 'Recorded March 1–3, 2001 at Abbey Road Studios. Recorded live at the release concert June 5, 2001.'
    return d


H.discogs_release = release
level = lambda pg, name, lv: pg.evaluate(f"""(() => {{ const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === '{name}');
  g.querySelector('tr.dci-row [data-act=level][data-level={lv}]').click(); }})()""")
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    cells = pg.evaluate("[...document.querySelectorAll('.dci-dm-col[data-dmcol=performance] .dci-dm-cell')].map(c => [c.dataset.id, c.querySelector('.dci-chip-main').textContent.trim()])")
    print('Spalte Performance:', cells)
    june = next(cid for cid, t in cells if '2001-06-05' in t)
    pg.check(f'[data-f=dm-rel][data-cell="{june}"]'); pg.wait_for_timeout(300)
    level(pg, 'Guitar Guy', 'release'); pg.wait_for_timeout(300)
    pg.locator('[data-el=dates] .dci-apply').first.evaluate('b => b.click()'); pg.wait_for_timeout(800)
    bass, guitar = rows_of(pg, 'Bass Man'), rows_of(pg, 'Guitar Guy')
    print('A) Bass Man:', bass, '| Guitar Guy (Release):', guitar)
    ok_a = bass == ['4 of 4 tracks | 2001-03-01 – 2001-03-03'] and guitar and guitar[0].endswith('| 2001-06-05')
    results.append(ok_a)
    # B) switching the level
    level(pg, 'Bass Man', 'release'); pg.wait_for_timeout(400)
    up = rows_of(pg, 'Bass Man')
    level(pg, 'Bass Man', 'recording'); pg.wait_for_timeout(400)
    back = rows_of(pg, 'Bass Man')
    logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'new level' in x]
    print('B) Bass Man → Release:', up, '| zurück:', back, '|', logs[-1:])
    ok_b = up and up[0].endswith('| 2001-06-05') and back == ['4 of 4 tracks | 2001-03-01 – 2001-03-03'] and len(logs) >= 2
    results.append(ok_b)
    # C) a date typed by hand stays
    g = pg.locator('section.dci-group').filter(has=pg.locator('.dci-gname strong', has_text='Keys Guy')).first
    g.locator('[data-act=date-edit]').first.click(); pg.wait_for_timeout(200)
    g.locator('[data-f=rd-by]').first.fill('1999'); g.locator('[data-f=rd-by]').first.dispatch_event('input'); pg.wait_for_timeout(200)
    level(pg, 'Keys Guy', 'release'); pg.wait_for_timeout(400)
    keys = rows_of(pg, 'Keys Guy')
    print('C) Keys Guy (eigenes Datum) → Release:', keys)
    ok_c = keys and keys[0].split(' | ')[1].startswith('1999')
    results.append(ok_c)
    # D) stored with the matrix, and still there after the dashboard was loaded again
    pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    stored = pg.evaluate(f"(JSON.parse(localStorage.getItem('dci-date-matrix:{H.REL}')).cells || []).filter(c => c.rel).map(c => c.date)")
    june_id = pg.evaluate(f"(JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}')) || []).filter(d => d.begin && d.begin.month === 6).map(d => d.id)")
    print('D) nach Neuladen als Release-Ebene markiert:', stored, '| Juni-Datum:', june_id)
    ok_d = len(stored) == 1 and stored[0] in june_id
    results.append(ok_d)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
