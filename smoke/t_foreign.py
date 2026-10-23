"""Credits Importer 3.21.2: instruments and voices in German, Spanish and French (collected item 43; T034, S025, R102, Q006).
A pasted text with "Guitarra eléctrica", "Schlagzeug", "contrebasse, voix", "saxo tenor y soprano" (the kind after the
instrument, shared), "Flügel", "Batterie", "Coros: Lucía y Marta" ("y" between names), "bajo" and "Alto".
A) Each is mapped as its English term – electric guitar, drums (drum set), double bass, vocal, tenor and soprano
   saxophone, grand piano, background vocals – and gets no role credit (a translation: MusicBrainz's own names; "Batterie"
   is not credited "drums").
B) "bajo" asks like "Bass" (which bass?), saying that it is a translation and gets no role credit.
C) "Alto" alone asks: viola, alto saxophone or alto vocals – nothing assumed; "viola" sets the instrument, no role credit.
D) The window "Mapping rules" lists T034 with the spellings and their languages; its search "@fr" finds the French ones."""
from playwright.sync_api import sync_playwright
import harness as H

for i, n in [(9130, 'viola'), (9131, 'grand piano'), (9132, 'tenor saxophone'), (9133, 'soprano saxophone')]:
    H.attr(i, n, 14, 14)
H.attr(9134, 'alto vocals', 3, 3)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
TEXT = """Guitarra eléctrica: Juan Pérez
Schlagzeug – Max Mustermann
Marie Dupont : contrebasse, voix
Ana López – saxo tenor y soprano
Flügel: Hans Meier
Batterie : Paul Martin
Coros: Lucía y Marta
José – bajo
Alto: Pierre Leroux"""
ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const p = tr.querySelector('[data-f=primary]');
    const c = tr.querySelector('[data-f=role-credit]');
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', p ? p.value : '', c ? c.value : '',
      (tr.querySelector('.dci-bass-ask') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim()]; })])))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.click('[data-act=text-open]')
    pg.fill('[data-f=text-src]', TEXT)
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(800)
    g = pg.evaluate(ROWS)
    for k, v in g.items():
        print('   ', k, v)
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    row = lambda name, i=0: (g.get(name) or [['', '', '', '', '']] * (i + 1))[i][:4]
    ok_a = row('Juan Pérez') == ['Guitarra eléctrica', 'instrument', 'electric guitar', ''] \
        and row('Max Mustermann') == ['Schlagzeug', 'instrument', 'drums (drum set)', ''] \
        and row('Marie Dupont') == ['contrebasse', 'instrument', 'double bass', ''] and row('Marie Dupont', 1)[:2] == ['voix', 'vocal'] and row('Marie Dupont', 1)[3] == '' \
        and row('Ana López') == ['saxo tenor', 'instrument', 'tenor saxophone', ''] and row('Ana López', 1) == ['saxo soprano', 'instrument', 'soprano saxophone', ''] \
        and row('Hans Meier') == ['Flügel', 'instrument', 'grand piano', ''] and row('Paul Martin') == ['Batterie', 'instrument', 'drums (drum set)', ''] \
        and row('Lucía') == ['Coros', 'vocal', 'background vocals', ''] and row('Marta') == ['Coros', 'vocal', 'background vocals', ''] and unrec == []
    print('A)', ok_a, '| nicht erkannt:', unrec)
    # B) bajo asks like Bass
    jose = (g.get('José') or [['', '', '', '', '']])[0]
    ok_b = jose[:4] == ['bajo', 'instrument', 'bass', ''] and 'only says “bajo”' in jose[4] and '“bajo” is a translation, so there is no role credit' in jose[4]
    print('B) bajo:', jose, ok_b)
    # C) Alto asks; viola sets the instrument
    sec = "[...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Pierre Leroux')"
    ask = pg.evaluate(f"(() => {{ const s = {sec}; return [...s.querySelectorAll('.dci-type-ask [data-act=type-pick]')].map(b => b.textContent.trim()); }})()")
    before = (g.get('Pierre Leroux') or [['']])[0]
    pg.evaluate(f"{sec}.querySelector('.dci-type-ask [data-act=type-pick][data-opt=\"0\"]').click()")
    pg.wait_for_timeout(500)
    after = pg.evaluate(ROWS).get('Pierre Leroux')
    print('C) Alto: Auswahl', ask, '| vorher:', before[:4], '| nach „viola“:', after)
    ok_c = ask == ['viola', 'alto saxophone', 'alto vocals'] and before[1] in ('Choose type …', '') and after and after[0][:4] == ['Alto', 'instrument', 'viola', '']
    # D) the mapping rules window
    pg.click('[data-act=rules]')
    pg.wait_for_timeout(400)
    t34 = pg.evaluate("[...document.querySelectorAll('[data-rf=tables] tr')].filter(tr => /Schlagzeug@de/.test(tr.textContent)).map(tr => tr.textContent.replace(/\\s+/g, ' ').trim())")
    pg.fill('[data-rf=search]', '@fr')
    pg.wait_for_timeout(300)
    shown = pg.evaluate("[...document.querySelectorAll('[data-rf=tables] tbody tr')].filter(tr => !tr.hidden).map(tr => tr.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /@/.test(t)).length")
    hidden_de_only = pg.evaluate("[...document.querySelectorAll('[data-rf=tables] tbody tr')].filter(tr => /Bratsche@de/.test(tr.textContent)).map(tr => tr.hidden)")
    print('D) T034:', t34[:1], '| mit „@fr“ sichtbar:', shown, '| nur deutsch (Bratsche) ausgeblendet:', hidden_de_only)
    ok_d = bool(t34) and 'Drums' in t34[0] and 'batería@es' in t34[0] and shown > 30 and hidden_de_only == [True]
    print('A)', ok_a, '| B)', ok_b, '| C)', ok_c, '| D)', ok_d)
    results += [ok_a, ok_b, ok_c, ok_d]
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
