"""Credits Importer 3.30.5: ⚙ below "Import credits …" opens only the settings, the tab "Source pages", tracks typed into
a track group (collected items 88, 90; the maintainer's answers of 2026-10-25 02:28).
A) Before any import: ⚙ in the bar below "Import credits …" opens the dashboard with its settings at "Source pages"
   (until 3.30.4 "Discogs and Bandcamp view"; the tab key stays "discogs") – the import does not start (no request to
   Discogs, nothing in the log about it); a message says so and offers "Start import". German: "Quellseiten".
B) "Start import" in the message: the import runs, the message is gone.
C) A new track group: the field "Tracks:" next to "Name" – "1-2, 4" ticks tracks 1, 2 and 4; ticks changed by hand show
   in the field ("1–3, 4" → "1–4"); "9" (no track of the release) is named in red and the group is not saved; "2-3"
   saves a group of tracks 2 and 3. Editing a group shows its tracks in the field."""
from playwright.sync_api import sync_playwright
import harness as H

results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=True)
    pg.on('dialog', lambda d: d.accept())
    reqs = []
    pg.on('request', lambda r: reqs.append(r.url))
    pg.wait_for_selector('#dci-open', timeout=20000)
    pg.wait_for_timeout(800)
    # A) settings only
    pg.locator('#dci-controls [data-nav-settings]').click()
    pg.wait_for_timeout(1500)
    a1 = pg.evaluate("""(() => { const o = document.getElementById('dci-overlay'); const tab = document.querySelector('.dci-set-tab[aria-selected=true]');
      return [!!o && !o.hidden, !document.querySelector('[data-el=settings]').hidden, tab ? [tab.dataset.topic, tab.textContent.trim()] : null,
        [...document.querySelectorAll('[data-el=msgs] .dci-msg')].map(m => [m.textContent.replace(/\\s+/g, ' ').trim().slice(0, 80), !!m.querySelector('[data-act=start-import]')]),
        document.querySelector('[data-el=toolbar]').hidden, [...document.querySelectorAll('#dci-log li')].some(li => /Import complete|Reading/.test(li.textContent))]; })()""")
    dg = [u for u in reqs if '/releases/' in u or 'discogs' in u.lower() and '/api' in u]
    print('A) nur Einstellungen:', a1, '| Anfragen an Discogs:', dg[:3])
    results.append(a1[0] and a1[1] and a1[2] == ['discogs', 'Source pages'] and len(a1[3]) == 1 and a1[3][0][1]
                   and 'has not started' in a1[3][0][0] and a1[4] and not a1[5] and not dg)
    # B) start the import from the message
    pg.click('[data-el=msgs] [data-act=start-import]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(800)
    b1 = pg.evaluate("[[...document.querySelectorAll('[data-el=msgs] .dci-msg')].some(m => /has not started/.test(m.textContent)), document.querySelectorAll('section.dci-group').length]")
    print('B) nach „Start import“ – Hinweis noch da, Einträge:', b1)
    results.append(not b1[0] and b1[1] > 3)
    # C) tracks typed into a track group
    if pg.evaluate("document.querySelector('.dci-pools-toggle').getAttribute('aria-expanded')") != 'true':
        pg.click('.dci-pools-toggle')
        pg.wait_for_timeout(300)
    pg.click('[data-act=tg-new]')
    pg.wait_for_timeout(300)
    TICKS = "[...document.querySelectorAll('.dci-track-form input[data-f=tg-track]')].filter(c => c.checked).map(c => Number(c.dataset.i) + 1)"
    f = pg.locator('.dci-track-form input[data-f=tg-text]')
    f.fill('1-2, 4')
    pg.wait_for_timeout(200)
    c1 = [pg.evaluate(TICKS), pg.evaluate("document.activeElement.dataset.f")]
    pg.locator('.dci-track-form input[data-f=tg-track][data-i="2"]').check()
    pg.wait_for_timeout(200)
    c2 = [pg.evaluate(TICKS), f.input_value()]
    f.fill('9')
    pg.wait_for_timeout(200)
    c3 = [pg.evaluate(TICKS), pg.locator('.dci-track-form .dci-err').inner_text()]
    pg.click('[data-act=tg-save]')
    pg.wait_for_timeout(300)
    c4 = [pg.evaluate("!!document.querySelector('.dci-track-form')"), pg.locator('.dci-track-form .dci-err').inner_text()]
    f = pg.locator('.dci-track-form input[data-f=tg-text]')
    f.fill('2-3')
    pg.wait_for_timeout(200)
    f.press('Enter')
    pg.wait_for_timeout(400)
    pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-track-pool:{H.REL}') || '[]').map(g => [g.name, g.tracks])")
    gid = pg.evaluate("(document.querySelector('[data-act=tg-edit]') || {dataset: {}}).dataset.id")
    pg.click(f'[data-act=tg-edit][data-id="{gid}"]')
    pg.wait_for_timeout(300)
    c5 = pg.locator('.dci-track-form input[data-f=tg-text]').input_value()
    print('C) „1-2, 4“:', c1, '| Häkchen 3 dazu:', c2, '| „9“:', c3, '| Speichern mit „9“:', c4, '| „2-3“ gespeichert:', pool, '| bearbeiten:', c5)
    results.append(c1 == [[1, 2, 4], 'tg-text'] and c2 == [[1, 2, 3, 4], '1–4'] and c3[0] == [1, 2, 3, 4] and '9' in c3[1]
                   and c4[0] and '9' in c4[1] and pool == [['Tracks 2–3', [1, 2]]] and c5 == '2–3')
    # German name of the tab
    pg.click('[data-act=tg-cancel]')
    H.open_settings(pg, 'general')
    pg.select_option('[data-el=settings] [data-f=lang]', 'de')
    pg.wait_for_timeout(600)
    de = pg.evaluate("document.querySelector('.dci-set-tab[data-topic=discogs]').textContent.trim()")
    print('   Deutsch:', de)
    results.append(de == 'Quellseiten')
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
