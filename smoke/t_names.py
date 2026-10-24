"""Import 3.6.0: lists of instruments and names in a text, as Bandcamp writes them (example: "The Swiftest Traveler",
trost records).
A) "Torben Snekkestad: tenor & soprano sax, trumpet and clarinet" – the shared word "sax" goes to "tenor" too: tenor
   saxophone, soprano saxophone, trumpet, clarinet. "acoustic & electric guitar" likewise; "bass & electric guitar" stays
   two instruments (bass is no modifier).
B) A list with a part it does not know: the known roles are taken, the line is listed as not recognized with the
   unknown part ("Barry Guy – double bass, sticks-and-stones" → double bass; "? “sticks-and-stones”").
C) Name suggestions: accents do not count ("Agusti Fernández" → MB "Agustí Fernández", same name); a middle name more
   or less is a similar name, marked as such ("Barry Guy" → MB "Barry John Guy"); nothing is assigned by itself."""
from playwright.sync_api import sync_playwright
import harness as H

for i, n in [(9120, 'trumpet'), (9121, 'clarinet'), (9122, 'tenor saxophone'), (9123, 'soprano saxophone')]:
    H.attr(i, n, 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
H.MB_SEARCH['artist'] = [
    {'id': H.uid('dddddddd', 50), 'name': 'Agustí Fernández', 'disambiguation': 'pianist', 'score': 100},
    {'id': H.uid('dddddddd', 51), 'name': 'Barry John Guy', 'disambiguation': 'bassist', 'score': 100},
    {'id': H.uid('dddddddd', 52), 'name': 'Torben Snekkestad', 'disambiguation': '', 'score': 100},
]
TEXT = """Torben Snekkestad: tenor & soprano sax, trumpet and clarinet
Agusti Fernández – piano
Barry Guy – double bass, sticks-and-stones
Gene Pick – acoustic & electric guitar
Bo Strum – bass & electric guitar"""
ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [[...g.querySelectorAll('tr.dci-row')].map(tr => { const p = tr.querySelector('[data-f=primary]'); return p ? p.value : tr.querySelector('.dci-drole').textContent.trim(); }),
   [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()), g.className.match(/dci-st-(\\w+)/)[1]]])))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.src_menu(pg, 'text-open')
    pg.fill('[data-f=text-src]', TEXT)
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(800)
    g = pg.evaluate(ROWS)
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    for k, v in g.items():
        print('   ', k, v)
    print('   nicht erkannt:', unrec)
    # A) shared instrument word
    ok_a = g['Torben Snekkestad'][0] == ['tenor saxophone', 'soprano saxophone', 'trumpet', 'clarinet'] \
        and g['Gene Pick'][0] == ['acoustic guitar', 'electric guitar'] and g['Bo Strum'][0] == ['bass', 'electric guitar']
    results.append(ok_a)
    # B) partly known
    ok_b = g['Barry Guy'][0] == ['double bass'] and unrec == ['Barry Guy – double bass, sticks-and-stones → ? “sticks-and-stones”']
    results.append(ok_b)
    # C) name suggestions
    sim = pg.evaluate("(() => { const b = [...document.querySelectorAll('[data-act=name-use]')].find(x => /Barry John Guy/.test(x.textContent)); return b ? [b.title, !!b.querySelector('.dci-similar')] : null; })()")
    print('   ähnlich:', sim)
    ok_c = g['Agusti Fernández'][1] == ['Agustí Fernández (pianist)'] and g['Barry Guy'][1] == ['Barry John Guy (bassist) similar name'] \
        and g['Torben Snekkestad'][1] == ['Torben Snekkestad'] and all(v[2] == 'missing' for v in g.values()) \
        and sim and sim[1] and 'similar name' in sim[0].lower()
    results.append(ok_c)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
