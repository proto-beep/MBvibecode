"""Track groups by drag & drop onto "Tracks and status" of rows (the row gets the group's tracks; with Shift
they are added; the places say so while dragging; a release-level row moves to the recording level); folded,
the track pool stays in the bar with the date pool; a date dropped onto an empty cell of the works matrix says
why it was not set, onto MB's dateless relationship it is planned as an edit; the release page checks work
credits (composer, publisher) on the works themselves when the release lookup lacks them."""
import re
from playwright.sync_api import sync_playwright
import harness as H
import zooid
from common_rows import drag, tracks_of_rows

PW = sync_playwright().start()
results = []


def open_mb(companion=False):
    b = PW.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg = None
    if companion:
        dg, _ = H.open_discogs(ctx)
    pg, errs = H.open_mb_edit(ctx, companion=companion)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    return b, pg, dg, errs


def rid(pg, name):
    return pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text=name)).first.locator('tr.dci-row').first.get_attribute('data-row')


def tracks(pg, name):
    return tracks_of_rows(pg, name)[0]


def group_id(pg, text, where='.dci-pools-body'):
    return pg.evaluate(f"[...document.querySelectorAll('{where} .dci-pchip-tg')].find(c => c.textContent.includes({text!r})).dataset.id")


# --- B) default release: a release-level row moves to "Recording"; works matrix cells that cannot take a date
b, pg, _, errs = open_mb()
pg.click('[data-act=tg-new]'); pg.fill('[data-f=tg-name]', 'Side A')
pg.check('[data-f=tg-track][data-i="0"]'); pg.check('[data-f=tg-track][data-i="1"]'); pg.click('[data-act=tg-save]'); pg.wait_for_timeout(200)
rel_row = pg.locator('tr.dci-row.dci-lv-release').first
rel_id = rel_row.get_attribute('data-row')
role = re.sub(r'\s+', ' ', rel_row.locator('.dci-c-role').inner_text())[:40]
gid = group_id(pg, 'Side A')
drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', f'tr[data-row="{rel_id}"] .dci-c-tracks')
moved = pg.locator(f'tr[data-row="{rel_id}"]').get_attribute('class')
msg = [m[:110] for m in pg.locator('.dci-msg').all_inner_texts() if 'Release' in m and 'Recording' in m]
tsel = pg.evaluate(f"[...document.querySelectorAll('tr[data-tracksrow=\"{rel_id}\"] input[data-f=track]:checked')].map(c => Number(c.dataset.i) + 1)")
print('B1) Release-Zeile', role, '→', moved, '| Tracks:', tsel, '| Meldung:', msg)
ok_b1 = 'dci-lv-recording' in moved and tsel == [1, 2] and len(msg) == 1
# works matrix: an empty cell, and a cell with only a relationship already in MusicBrainz
date = pg.evaluate("document.querySelector('.dci-pools-body .dci-pchip-date').dataset.id")
empty = '.dci-mx-cell[data-col="k:a17"][data-mrow^="w:0"]'
drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', empty)
m1 = [m for m in pg.locator('.dci-msg').all_inner_texts() if 'no role switched on' in m]
ww = '.dci-mx-cell[data-col="k:a15"][data-mrow^="w:0"]'
pg.click(f'{ww} [data-act=mx-cell]'); pg.wait_for_timeout(200)
cell_now = re.sub(r'\s+', ' ', pg.locator(ww).inner_text())
drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', ww)
m2 = [re.sub(r'\s+', ' ', x) for x in pg.locator(f'{ww} .dci-mx-fill').all_inner_texts()]   # MB's composer has no date: it is added (edit)
# a cell with a role of its own still takes the date
drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', '.dci-mx-cell[data-col="k:a15"][data-mrow="n:1"]')
own = pg.locator('.dci-mx-cell[data-col="k:a15"][data-mrow="n:1"] sup').count()
print('B2) leere Zelle:', m1[:1], '| nur MB (Zelle jetzt:', cell_now, '): geplant', m2[:1], '| Zelle mit eigener Rolle ⌚:', own)
ok_b2 = len(m1) == 1 and len(m2) == 1 and 'composer' in m2[0] and own == 1
results += [ok_b1, ok_b2]
print('Fehler B:', errs)
b.close()

# --- C) release page: work credits found on the work itself ----------------------------------------------
H.MB_EXTRA.clear()
H.WORK_RELS_DIRECT_ONLY = True
b, pg, dg, errs = open_mb(companion=True)
H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
H.submit_staged(pg)
pg.goto(f'https://musicbrainz.org/release/{H.REL}')
H.with_companion(pg)
dg.wait_for_timeout(6000)
marks = dg.evaluate("[...document.querySelectorAll('.dci-dg-mark')].map(m => m.textContent + ' ' + m.closest('li, tr').querySelector('a').textContent)")
print('C) Release-Seite (Werk-Beziehungen nur am Werk):', marks, '| Werk-Abfragen:', len(H.WORK_LOOKUPS))
ok_c = '✓ Pub Co' in marks and '✓ Writer W' in marks and H.WORK1 in H.WORK_LOOKUPS and not any(m.startswith('✗') for m in marks)
results.append(ok_c)
print('Fehler C:', errs)
H.WORK_RELS_DIRECT_ONLY = False
b.close()
# --- A) Zooid: two track groups from the notes ------------------------------------------------------------
zooid.setup(zooid.NOTES_TWO_DAYS)
b, pg, _, errs = open_mb()
names = [re.sub(r'\s+', ' ', x) for x in pg.locator('.dci-pools-body .dci-pchip-tg .dci-chip-main').all_inner_texts()]
print('A1) Track-Pool:', names, '| Hinweis:', pg.locator('.dci-tracks-bar .dci-drag-hint').get_attribute('title')[:90])
g2 = group_id(pg, '6')   # tracks 6–10
g1 = pg.evaluate(f"[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].map(c => c.dataset.id).find(id => id !== {g2!r})")
print('    Henry Threadgill vorher:', tracks(pg, 'Henry Threadgill'))
drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{g2}"] .dci-chip-main', f'tr[data-row="{rid(pg, "Henry Threadgill")}"] .dci-c-tracks')
after = tracks(pg, 'Henry Threadgill')
count = pg.locator(f'[data-tcount="{rid(pg, "Henry Threadgill")}"]').inner_text()
print('    nach Ablegen von Tracks 6–10:', after, '|', count)
ok_a1 = after == [6, 7, 8, 9, 10] and '5' in count
# with Shift: added to the row's own tracks
# (Playwright's mouse drag carries no modifier keys, so the drop with Shift is dispatched as events)
# The places on rows say what a drop does: replace, with Shift add (shown while a track group is dragged)
hints = pg.evaluate(f"""(() => {{
  const src = document.querySelector('.dci-pools-body .dci-pchip-tg[data-id="{g1}"]');
  const dst = document.querySelector('tr[data-row="{rid(pg, "Henry Threadgill")}"] .dci-c-tracks');
  const other = document.querySelector('tr[data-row="{rid(pg, "Liberty Ellman")}"] .dci-c-tracks');
  const after = (el) => getComputedStyle(el, '::after').content;
  const dt = new DataTransfer();
  src.dispatchEvent(new DragEvent('dragstart', {{ bubbles: true, dataTransfer: dt }}));
  dst.dispatchEvent(new DragEvent('dragover', {{ bubbles: true, cancelable: true, dataTransfer: dt }}));
  const out = [after(other), after(dst)];
  dst.dispatchEvent(new DragEvent('dragover', {{ bubbles: true, cancelable: true, dataTransfer: dt, shiftKey: true }}));
  out.push(after(dst));
  dst.dispatchEvent(new DragEvent('drop', {{ bubbles: true, cancelable: true, dataTransfer: dt, shiftKey: true }}));
  src.dispatchEvent(new DragEvent('dragend', {{ bubbles: true, dataTransfer: dt }}));
  out.push(after(dst));
  return out;
}})()""")
pg.wait_for_timeout(200)
added = tracks(pg, 'Henry Threadgill')
print('A2) Hinweise beim Ziehen (andere Zeile | darüber | mit Umschalt | danach):', hints)
print('    mit Umschalt Tracks 1–5 dazu:', added)
ok_a2 = added == list(range(1, 11)) and 'Shift: add' in hints[0] and 'replaces the tracks' in hints[1] and 'adds to the tracks' in hints[2] \
    and hints[3] in ('none', 'normal', '')
# the open track list of a row is a target too
r = rid(pg, 'Liberty Ellman')
pg.click(f'tr[data-row="{r}"] [data-act=tracks-toggle]'); pg.wait_for_timeout(150)
drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{g1}"] .dci-chip-main', f'tr[data-tracksrow="{r}"] .dci-chips')
print('    auf die offene Trackliste von Liberty Ellman:', tracks(pg, 'Liberty Ellman'))
ok_a2 = ok_a2 and tracks(pg, 'Liberty Ellman') == [1, 2, 3, 4, 5]
# folded: the track pool stays in the bar and can be dragged from there
pg.click('.dci-pools-fold'); pg.wait_for_timeout(200)
kept_tg = pg.locator('.dci-pools-kept .dci-pchip-tg').count()
kept_dates = pg.locator('.dci-pools-kept .dci-pchip-date').count()
print('A3) eingeklappt oben – Track-Gruppen:', kept_tg, '| Daten:', kept_dates, '| Option:', pg.evaluate("document.querySelector('[data-el=dates]').textContent.includes('keep') ? 'x' : ''"))
drag(pg, f'.dci-pools-kept .dci-pchip-tg[data-id="{g2}"] .dci-chip-main', f'tr[data-row="{rid(pg, "Liberty Ellman")}"] .dci-c-tracks')
print('    aus der Leiste auf Liberty Ellman:', tracks(pg, 'Liberty Ellman'))
ok_a3 = kept_tg == 2 and kept_dates >= 1 and tracks(pg, 'Liberty Ellman') == [6, 7, 8, 9, 10]
log = pg.evaluate("[...document.querySelectorAll('#dci-log li')].slice(-3).map(l => l.textContent.slice(9))")
print('    Protokoll:', log)
ok_a3 = ok_a3 and any('Track group' in x and 'put on a row: 5 tracks' in x for x in log)
results += [ok_a1, ok_a2, ok_a3]
print('Fehler A:', errs)
b.close()

print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
PW.stop()
