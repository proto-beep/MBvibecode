"""Release with two media: "CD2, tracks 1–3", "Disc 1", medium headings in the track form, and "+ new track
group" with a whole medium or one group per medium."""
import re
from playwright.sync_api import sync_playwright
import harness as H
import zooid
from common_rows import cells
zooid.setup('CD2, tracks 1–3 recorded May 1, 2020 at Brooklyn Recording.\nDisc 1 recorded April 4, 2020.')
H.MEDIA = [5, 5]
orig = H.discogs_release


def rel():
    d = orig()
    for i, t in enumerate(d['tracklist']):
        t['position'] = f'{1 + i // 5}-{1 + i % 5}'
    for e in d['extraartists']:
        if e['tracks']:
            e['tracks'] = '2-1 to 2-5'
    return d


H.discogs_release = rel
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.click('[data-el=datefind] summary')
    items = [re.sub(r'\s+', ' ', i)[:90] for i in pg.locator('[data-el=datefind-list] li').all_inner_texts()]
    print('Gefunden:', items)
    print('Matrix (Vorschläge):', cells(pg)['performance'])
    print('Track-Pool:', pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts())
    opts = pg.locator('[data-f=tg-new-pick] option').all_inner_texts()
    print('Auswahl „+ neue Track-Gruppe“:', opts)
    pg.select_option('[data-f=tg-new-pick]', 'pick'); pg.wait_for_timeout(200)
    print('Medium-Überschriften im Formular:', pg.locator('.dci-track-form [data-act=tg-medium]').all_inner_texts())
    pg.locator('.dci-track-form [data-act=tg-medium]').nth(1).click(); pg.wait_for_timeout(200)
    checked = pg.evaluate("[...document.querySelectorAll('.dci-track-form input[data-f=tg-track]:checked')].map(c => Number(c.dataset.i))")
    print('Klick auf Medium 2 hakt an (Index):', checked)
    pg.click('[data-act=tg-cancel]'); pg.wait_for_timeout(100)
    pg.select_option('[data-f=tg-new-pick]', 'all'); pg.wait_for_timeout(200)
    groups = [re.sub(r'\s+', ' ', g) for g in pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts()]
    print('Nach „alle Medien“ (Medium 1 gibt es schon als „Tracks 1-1–1-5“):', groups)
    pg.select_option('[data-f=tg-new-pick]', 'm:2'); pg.wait_for_timeout(200)
    again = len(pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts())
    ok = ('tracks 2-1–2-3' in items[0] and checked == [5, 6, 7, 8, 9] and len(opts) == 5 and len(groups) == 3
          and 'Medium 2 · CD 5 tracks' in groups and again == len(groups)
          and [c[1] for c in cells(pg)['performance']] == [['Tracks 2-1–2-3'], ['Tracks 1-1–1-5']])
    print('Ergebnis:', 'OK' if ok else 'FEHLER', '| Fehler:', errs)
    b.close()
