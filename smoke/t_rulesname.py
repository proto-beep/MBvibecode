"""Import 3.13.2: the window "Mapping rules" names Discogs only while Discogs is the loaded source.
A) Discogs loaded: "Try a Discogs role:", the column "Discogs", "Discogs role → MusicBrainz", the hint with "as on Discogs".
B) A pasted text loaded while the window is open: the window follows at once – "Try a role:", column "Role",
   "Role → MusicBrainz", "Role (without details)", the hint "as the source writes it".
C) Discogs again: the Discogs words are back."""
from playwright.sync_api import sync_playwright
import harness as H

STATE = """(() => { const w = document.getElementById('dci-rules'); return {
  label: w.querySelector('[data-rf=test-label]').textContent.trim(),
  col: w.querySelector('[data-rsect=roles] thead th:nth-child(3)').textContent.trim(),
  kind: [...w.querySelectorAll('[data-uf=kind] option')].map(o => o.textContent.trim()),
  field: w.querySelector('[data-uf=discogs]').closest('label').textContent.trim(),
  hint: w.querySelector('[data-rf=result]').textContent.trim() }; })()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.locator('[data-act=rules]').first.click()
    pg.wait_for_selector('#dci-rules [data-rsect=roles]')
    a = pg.evaluate(STATE)
    print('A)', a)
    results.append(a['label'] == 'Try a Discogs role:' and a['col'] == 'Discogs' and a['kind'][0] == 'Discogs role → MusicBrainz'
                   and a['field'].startswith('Discogs role (without details)') and 'as on Discogs' in a['hint'])
    pg.click('[data-act=text-open]')
    pg.fill('[data-f=text-src]', 'Bass Man – bass')
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(500)
    bb = pg.evaluate(STATE)
    print('B)', bb)
    results.append(bb['label'] == 'Try a role:' and bb['col'] == 'Role' and bb['kind'] == ['Role → MusicBrainz', 'Spelling → MB instrument']
                   and bb['field'].startswith('Role (without details)') and 'as the source writes it' in bb['hint'])
    pg.fill('[data-f=discogs-input]', '1234')
    pg.click('[data-act=discogs-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 3", 90)
    pg.wait_for_timeout(500)
    c = pg.evaluate(STATE)
    print('C)', c['label'], c['col'])
    results.append(c['label'] == 'Try a Discogs role:' and c['col'] == 'Discogs')
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
