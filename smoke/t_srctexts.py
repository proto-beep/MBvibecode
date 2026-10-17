"""Import 3.16.2: texts that named Discogs say "the source" when another source is loaded (as "Mapping rules" in 3.13.2).
A) Discogs loaded: the question for "Guitar" says "Discogs only says “Guitar”", a role credit taken over is tagged "from
   Discogs"; the placeholder of "Add entry manually" says "a role as the source writes it" (for any source).
B) A pasted text loaded: "The source (pasted text) only says “Guitar”", the tag "from the source" (tooltip "Taken from
   the source (pasted text)"), and a track without writers says "The source (pasted text) names no writers for this
   track"."""
from playwright.sync_api import sync_playwright
import harness as H

LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
TEXTS = """(() => ({ ask: [...document.querySelectorAll('.dci-bass-ask')].map(x => x.textContent.replace(/\\s+/g, ' ').trim().slice(0, 60)),
  ph: (document.querySelector('[data-f=manual-role]') || {}).placeholder || '',
  tag: [...document.querySelectorAll('.dci-credit-name .dci-src')].map(x => [x.textContent.trim(), x.title]),
  writers: [...document.querySelectorAll('tr[data-work] .dci-info')].map(x => x.title) }))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Checks complete/.test(x))", 90)
    pg.wait_for_timeout(500)
    a = pg.evaluate(TEXTS)
    print('A) Discogs:', a['ask'][:1], '|', a['ph'], '|', a['tag'][:1])
    results.append(any(x.startswith('Discogs only says “Guitar”') for x in a['ask']) and 'a role as the source writes it' in a['ph']
                   and a['tag'] and a['tag'][0] == ['from Discogs', 'Taken from Discogs'])
    pg.click('[data-act=text-open]')
    pg.fill('[data-f=text-src]', 'Guitar – John Smith\nLayout by Jane Roe')
    pg.click('[data-act=text-load]')
    H.wait_for(pg, f"{LOGS}.filter(x => /Checks complete/.test(x)).length >= 2", 90)
    pg.wait_for_timeout(500)
    t = pg.evaluate(TEXTS)
    print('B) Text:', t['ask'][:1], '|', t['ph'], '|', t['tag'][:1], '|', t['writers'][:1])
    results.append(any(x.startswith('The source (pasted text) only says “Guitar”') for x in t['ask'])
                   and t['tag'] and t['tag'][0] == ['from the source', 'Taken from the source (pasted text)']
                   and any(w.startswith('The source (pasted text) names no writers for this track') for w in t['writers']))
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
