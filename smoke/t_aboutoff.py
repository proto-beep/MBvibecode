"""Import 3.16.1: "Leave out the “about” text" (Bandcamp, per release, at once, without a new import).
The credits name "Mastered at Studio Nord, Bremen, March 2019"; the "about" text "recorded at Loft in Cologne, june 16/17
2018".
A) The checkbox stands next to "Delete stored import …" (a Bandcamp release with an "about" text).
B) Ticked: the entry "Loft" (from the about text) is hidden, "Studio Nord" (credits) stays; the June dates leave the pool,
   March 2019 stays; the log says so; stored for the release.
C) Ticked off again: "Loft" is back with what was changed in it ("credited as" typed before), the June dates are back.
D) Kept for the release: ticked, the page loaded again – the box is ticked, "Loft" hidden, no June date in the pool.
E) "Delete stored import" sets it back."""
import json
from playwright.sync_api import sync_playwright
import harness as H

ALBUM = 'https://testband.bandcamp.com/album/swift'
H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Test Band', 'current': {
    'title': 'Swift', 'credits': 'Bass Man – bass\nMastered at Studio Nord, Bremen, March 2019',
    'about': 'An evening of improvised music.\nrecorded at Loft in Cologne, june 16/17 2018'},
    'trackinfo': [{'track_num': i + 1, 'title': t} for i, t in enumerate(H.TITLES)]})
orig_ws = H.ws_release


def ws():
    d = orig_ws()
    d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
    for m in d['media']:
        m['format'] = 'Digital Media'
    return d


H.ws_release = ws
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
STATE = f"""(() => {{ const vis = (re) => [...document.querySelectorAll('section.dci-group')].filter(g => re.test(g.querySelector('.dci-gname').textContent))
    .map(g => getComputedStyle(g).display !== 'none');
  const pool = JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => JSON.stringify(d.begin));
  const box = document.querySelector('[data-f=about-off]');
  return {{ box: box ? box.checked : null, loft: vis(/Loft/), nord: vis(/Studio Nord/), june: pool.some(x => /"month":6/.test(x)), march: pool.some(x => /"year":2019,"month":3/.test(x)),
    stored: localStorage.getItem('dci-about-off:{H.REL}') !== null }}; }})()"""
results = []


def imported(pg, n):
    H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= {n}", 90)
    pg.wait_for_timeout(1200)


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    pg.click('#dci-open')
    imported(pg, 1)
    s0 = pg.evaluate(STATE)
    near = pg.evaluate("(() => { const f = document.querySelector('[data-act=forget-open]'); const l = document.querySelector('[data-f=about-off]'); return !!(f && l && f.parentElement === l.closest('label').parentElement); })()")
    print('A)', s0, '| neben „Delete stored import“:', near)
    results.append(s0['box'] is False and s0['loft'] == [True] and s0['june'] and s0['march'] and near)
    # a change in the Loft row
    loft_credit = "[...document.querySelectorAll('section.dci-group')].find(g => /Loft/.test(g.querySelector('.dci-gname').textContent)).querySelector('tr.dci-row [data-f=credit]')"
    pg.evaluate(f"(() => {{ const i = {loft_credit}; i.value = 'The Loft'; i.dispatchEvent(new Event('input', {{ bubbles: true }})); i.dispatchEvent(new Event('change', {{ bubbles: true }})); }})()")
    pg.wait_for_timeout(300)
    # B) ticked
    H.src_menu(pg)
    pg.locator('[data-f=about-off]').check(); pg.wait_for_timeout(600)
    s1 = pg.evaluate(STATE)
    log = [x for x in pg.evaluate(LOGS) if '“about” text' in x]
    print('B)', s1, '|', log)
    results.append(s1['box'] is True and s1['loft'] == [False] and s1['nord'] == [True] and not s1['june'] and s1['march'] and s1['stored']
                   and log and log[-1] == '“about” text left out (rows hidden: 1, dates out of the pool: 2)')
    # C) off again: back, with the change
    H.src_menu(pg)
    pg.locator('[data-f=about-off]').uncheck(); pg.wait_for_timeout(600)
    s2 = pg.evaluate(STATE)
    kept = pg.evaluate(f"{loft_credit}.value")
    log = [x for x in pg.evaluate(LOGS) if '“about” text' in x]
    print('C)', s2, '| „credited as“:', kept, '|', log[-1:])
    results.append(s2['box'] is False and s2['loft'] == [True] and s2['june'] and not s2['stored'] and kept == 'The Loft' and log[-1] == '“about” text taken in again (rows back: 1, dates back: 2)')
    # D) kept for the release
    H.src_menu(pg)
    pg.locator('[data-f=about-off]').check(); pg.wait_for_timeout(600)
    pg.reload(); pg.add_script_tag(content=H.GM_XHR_SHIM); pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    pg.click('#dci-open')
    imported(pg, 2)
    s3 = pg.evaluate(STATE)
    print('D) nach Neuladen:', s3)
    results.append(s3['box'] is True and s3['loft'] == [False] and not s3['june'] and s3['march'])
    # E) "Delete stored import" sets it back
    H.src_menu(pg, 'forget-open')
    pg.click('[data-act=forget-do]')
    imported(pg, 1)  # the log of the release starts anew
    s4 = pg.evaluate(STATE)
    print('E) nach „Delete stored import“:', s4)
    results.append(s4['box'] is False and s4['loft'] == [True] and s4['june'] and not s4['stored'])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
