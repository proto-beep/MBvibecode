"""Credits Importer 3.30.6: "Sounds" – performer or effects, asked (collected item 85; the maintainer's answers of
2026-10-25 01:59 and 02:28).
A) Discogs "Sounds": a performer row (R104) with the question "performer, or the instrument effects credited “sounds”?"
   – until answered it stays performer (and would be staged as such); the rule Q008 at the row.
B) "effects" chosen: the instrument effects with the role credit "sounds" (lower case); "performer" chosen again: back.
C) A pasted text: "… by K.M. (sounds, words)" and "Sounds: Jane Doe" – both performer with the question."""
from playwright.sync_api import sync_playwright
import harness as H

H.attr(9124, 'effects', 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
H.ARTISTS[3050] = (H.uid('dddddddd', 50), 'Sound Person')
orig = H.discogs_release


def rel():
    d = orig()
    d['extraartists'].append({'name': 'Sound Person', 'anv': '', 'role': 'Sounds', 'tracks': '', 'id': 3050, 'join': ''})
    return d


H.discogs_release = rel
ROW = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; const tr = [...g.querySelectorAll('tr.dci-row')].find(r => /sounds/i.test(r.querySelector('.dci-drole').textContent)) || g.querySelector('tr.dci-row');
  const t = tr.querySelector('[data-f=type]'); const ask = tr.querySelector('.dci-type-ask'); const p = tr.querySelector('[data-f=primary]'); const c = tr.querySelector('[data-f=role-credit]');
  return { id: tr.dataset.row, role: tr.querySelector('.dci-drole').textContent.trim(), type: t ? (t.options[t.selectedIndex] || {}).text : '', primary: p ? p.value : '', credit: c ? c.value : '',
    ask: ask ? ask.textContent.replace(/\\s+/g, ' ').trim() : null, opts: ask ? [...ask.querySelectorAll('[data-act=type-pick]')].map(b => b.textContent.trim()) : [],
    rules: [...tr.querySelectorAll('.dci-ruleid')].map(b => b.textContent.trim()) }; }"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(800)
    # A)
    a1 = pg.evaluate(ROW, 'Sound Person')
    print('A)', a1)
    results.append(a1 and a1['type'] == 'performer' and a1['opts'] == ['performer', 'effects (credited “sounds”)'] and 'stays performer' in a1['ask']
                   and 'R104' in a1['rules'] and 'Q008' in a1['rules'])
    # B)
    pg.click(f'tr[data-row="{a1["id"]}"] [data-act=type-pick][data-opt="1"]')
    pg.wait_for_timeout(400)
    b1 = pg.evaluate(ROW, 'Sound Person')
    pg.click(f'tr[data-row="{a1["id"]}"] [data-act=type-pick][data-opt="0"]')
    pg.wait_for_timeout(400)
    b2 = pg.evaluate(ROW, 'Sound Person')
    print('B) effects:', [b1['type'], b1['primary'], b1['credit']], '| performer:', [b2['type'], b2['credit']])
    results.append(b1['type'] == 'instrument' and b1['primary'] == 'effects' and b1['credit'] == 'sounds' and b2['type'] == 'performer' and b2['credit'] in ('', '-'))
    # C) a pasted text
    H.src_menu(pg, 'text-open')
    pg.fill('[data-f=text-src]', 'A chronicle of rabid deeds, dutifully unearthed from accursed soil by K.M. (sounds, words).\nSounds: Jane Doe')
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(1200)
    c1, c2 = pg.evaluate(ROW, 'K.M.'), pg.evaluate(ROW, 'Jane Doe')
    print('C) K.M.:', c1, '\n   Jane Doe:', c2)
    results.append(c1 and c1['type'] == 'performer' and len(c1['opts']) == 2 and c2 and c2['type'] == 'performer' and len(c2['opts']) == 2)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
