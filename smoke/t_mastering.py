"""Import 3.15.1: mastering only on the release level (as MusicBrainz has it: on recordings the type is deprecated).
Discogs names two mastering engineers: Mia Master for tracks 1–2 (CD 1, say), Max Master for tracks 3–4; the notes give
May, June and July 2001 for mastering (cells of the column "Mastering"). May gets the track group "CD 1" (tracks 1–2),
June "CD 2" (tracks 3–4), July none (all tracks).
A) The rows of both are on the release level; the only other choice is "Skip" (no "Recording"), and the level says why
   on mouse-over.
B) The cells of the column "Mastering" have no checkbox "Release level"; the column "Performance" still has it.
C) Applied: Mia Master takes May and July, Max Master June and July – the track group only says which mastering row a
   date belongs to; no date is lost for a release-level row because of a track group."""
import json
from playwright.sync_api import sync_playwright
import harness as H
from common_rows import rows_of

orig = H.discogs_release


def release():
    d = orig()
    ex = lambda name, role, i, tracks='': {'name': name, 'anv': '', 'role': role, 'tracks': tracks, 'id': i, 'join': ''}
    d['extraartists'] = d['extraartists'] + [ex('Mia Master', 'Mastered By', 3021, '1, 2'), ex('Max Master', 'Mastered By', 3022, '3, 4')]
    d['notes'] = 'Recorded March 2001. Mastered May 2001. Mastered June 2001. Mastered July 2001.'
    return d


H.discogs_release = release
H.ARTISTS[3021] = (H.uid('dddddddd', 21), 'Mia Master')
H.ARTISTS[3022] = (H.uid('dddddddd', 22), 'Max Master')
TRACKS = [{'id': 't12', 'name': 'CD 1', 'tracks': [0, 1]}, {'id': 't34', 'name': 'CD 2', 'tracks': [2, 3]}]
CELLS = "[...document.querySelectorAll('.dci-dm-col[data-dmcol=mastering] .dci-dm-cell')].map(c => [c.dataset.id, c.querySelector('.dci-chip-main').textContent.trim()])"


def group_on(pg, month, tg):
    cid = next(c for c, t in pg.evaluate(CELLS) if f'2001-{month}' in t)
    pg.locator(f'[data-act=dm-edit][data-cell="{cid}"]').first.evaluate('b => b.click()'); pg.wait_for_timeout(200)
    pg.locator(f'[data-f=dm-tg][data-cell="{cid}"][value="{tg}"]').check(); pg.wait_for_timeout(200)
    pg.locator(f'.dci-dm-editor [data-act=dm-edit][data-cell="{cid}"]').first.evaluate('b => b.click()'); pg.wait_for_timeout(200)


results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    # two track groups (read when the script starts: stored, then the page loaded again)
    pg.evaluate(f"localStorage.setItem('dci-track-pool:{H.REL}', {json.dumps(json.dumps(TRACKS))})")
    pg.reload(); pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(800)
    print('Spalte Mastering:', pg.evaluate(CELLS))
    group_on(pg, '05', 't12')
    group_on(pg, '06', 't34')
    # A) levels
    lv = pg.evaluate("""[...document.querySelectorAll('section.dci-group')].filter(g => /Mia Master|Max Master/.test(g.querySelector('.dci-gname').textContent))
      .map(g => { const seg = g.querySelector('tr.dci-row .dci-seg'); return [g.querySelector('.dci-gname strong').textContent.trim(),
        [...seg.querySelectorAll('[data-act=level]')].map(x => x.dataset.level + (x.getAttribute('aria-pressed') === 'true' ? '*' : '')), seg.title,
        g.querySelector('tr.dci-row [data-f=type]').value]; })""")
    print('A) Ebenen:', lv)
    results.append(len(lv) == 2 and all(x[1] == ['release*', 'skip'] and 'only on this level (Release)' in x[2] for x in lv))
    # B) no "Release level" in the mastering column, still in the performance column
    rel = pg.evaluate("Object.fromEntries(['mastering', 'performance'].map(k => [k, document.querySelectorAll(`.dci-dm-col[data-dmcol=${k}] [data-f=dm-rel]`).length]))")
    cells = pg.evaluate("document.querySelectorAll('.dci-dm-col[data-dmcol=mastering] .dci-dm-cell').length")
    print('B) Checkbox „Release-Ebene“:', rel, '| Zellen Mastering:', cells)
    results.append(rel == {'mastering': 0, 'performance': 1} and cells >= 3)
    # C) applied
    pg.locator('[data-el=dates] .dci-apply').first.evaluate('b => b.click()'); pg.wait_for_timeout(800)
    mia, mx = rows_of(pg, 'Mia Master'), rows_of(pg, 'Max Master')
    print('C) Mia Master:', mia, '| Max Master:', mx)
    results.append(sorted(x.split(' | ')[1] for x in mia) == ['2001-05', '2001-07'] and sorted(x.split(' | ')[1] for x in mx) == ['2001-06', '2001-07'])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
