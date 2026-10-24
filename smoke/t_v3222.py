"""Credits Importer 3.22.2 (3.22.3): fixed credit pairs, more areas, no role credit for recording, patterns in the rules window
(collected items 47, 48, 49, 45).
A) [3.22.3] "Kontrabass" (a pasted text and Discogs) is double bass without role credit (W003: German, a translation;
   3.22.2 "contrabass"), the English "Contrabass" keeps "contrabass" (W002); "Violoncello" is cello with "violoncello" (W008).
B) "Produced by X in Berlin", "Remixed in Paris by Y", "Engineered in Gijon by Z": areas with produced in, remixed in,
   engineered in (C041 – C043); the suggestion names the area it is part of, read from MusicBrainz ("City, Asturias").
C) "Recorded by", "Recorded live by", "Live Recording By", "Recording engineer", "Recorded & produced by", "Recorded,
   mixed and mastered by" – recording (recording engineer) without role credit, also with a "task" field at the type.
D) The rules window: "(manufactured | made) (by | at)" (C010), "(recorded | overdubbed) at" (C023), lists without
   outer brackets ("phonographic copyright", C001)."""
from playwright.sync_api import sync_playwright
import harness as H

H.attr(9150, 'cello', 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
# recording with a free-text task, as a type may have it on MusicBrainz
H.lt(128, 'a01ee869-80a8-45ef-9447-c59e91aa7926', 'recording', 'artist', 'recording', (1, 526, 1150))
for i, gid, name, lvl in [(1101, '1d4c0b5b-0000-4000-8000-000000001101', 'produced in', 'recording'),
                          (1102, '1d4c0b5b-0000-4000-8000-000000001102', 'remixed in', 'recording'),
                          (1103, '1d4c0b5b-0000-4000-8000-000000001103', 'engineered in', 'recording')]:
    H.lt(i, gid, name, 'area', lvl, ())
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
BERLIN, PARIS, GIJON = H.uid('eeeeeeee', 71), H.uid('eeeeeeee', 72), H.uid('eeeeeeee', 73)
H.MB_SEARCH['area'] = [{'id': BERLIN, 'name': 'Berlin', 'type': 'City', 'disambiguation': '', 'score': 100, 'aliases': []},
                       {'id': PARIS, 'name': 'Paris', 'type': 'City', 'disambiguation': '', 'score': 100, 'aliases': []},
                       {'id': GIJON, 'name': 'Gijón', 'type': 'City', 'disambiguation': '', 'score': 100, 'aliases': [{'name': 'Xixón'}]}]
H.AREA_PARENTS.update({GIJON: 'Asturias', PARIS: 'Île-de-France'})
TEXT = """Kontrabass: Karl Bass
Contrabass: Connie Bass
Violoncello: Vera Cello
Produced by Pat Prod in Berlin
Remixed in Paris by Rita Remix
Engineered in Gijon by Eddie Eng
Recorded by Pat One
Recorded live by Pat Two
Live Recording By: Pat Three
Recording engineer: Pat Four
Recorded & produced by Pat Five
Recorded, mixed and mastered by Pat Six"""
ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  { sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()),
    rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const p = tr.querySelector('[data-f=primary]');
      const c = tr.querySelector('[data-f=role-credit]');
      return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', p ? p.value : '', c ? c.value : '-']; }) }])))()"""
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
    pg.wait_for_timeout(1500)
    g = pg.evaluate(ROWS)
    for k, v in g.items():
        print('   ', k, v)
    row = lambda name, i=0: ((g.get(name) or {'rows': []})['rows'] + [['', '', '', '']] * (i + 1))[i]
    # A)
    ok_a = row('Karl Bass') == ['Kontrabass', 'instrument', 'double bass', ''] and row('Connie Bass') == ['Contrabass', 'instrument', 'double bass', 'contrabass'] \
        and row('Vera Cello') == ['Violoncello', 'instrument', 'cello', 'violoncello']
    print('A) Kontrabass:', row('Karl Bass'), '| Contrabass:', row('Connie Bass'), '| Violoncello:', row('Vera Cello'), ok_a)
    # B)
    area = lambda name: (g.get(name) or {'rows': [['', '']], 'sugg': []})
    ok_b = row('Berlin')[:2] == ['Produced In', 'produced in'] and row('Paris')[:2] == ['Remixed In', 'remixed in'] and row('Gijon')[:2] == ['Engineered In', 'engineered in'] \
        and area('Gijon')['sugg'][:1] == ['Gijón (City, Asturias) – area'] and area('Paris')['sugg'][:1] == ['Paris (City, Île-de-France) – area'] \
        and area('Berlin')['sugg'][:1] == ['Berlin (City) – area'] and row('Pat Prod')[:2] == ['Produced By', 'producer'] and row('Rita Remix')[0] == 'Remixed By' \
        and row('Eddie Eng')[0] in ('Engineered By', 'Engineer') and not any('in Berlin' in x for x in pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)"))
    print('B) Gebiete:', [(n, row(n)[:2], area(n)['sugg'][:1]) for n in ('Berlin', 'Paris', 'Gijon')], ok_b)
    # C)
    rec = [row(n, i) for n, i in [('Pat One', 0), ('Pat Two', 0), ('Pat Three', 0), ('Pat Four', 0), ('Pat Five', 0), ('Pat Six', 0)]]
    ok_c = all(r[1] == 'recording' and r[3] == '' for r in rec)
    print('C) Aufnahme:', rec, ok_c)
    # D) the rules window
    pg.click('[data-act=rules]')
    pg.wait_for_timeout(400)
    rules = pg.evaluate("Object.fromEntries([...document.querySelectorAll('[data-rf] tr')].map(tr => [tr.cells[1] ? tr.cells[1].textContent.trim() : '', tr.cells[2] ? tr.cells[2].textContent.replace(/\\s+/g, ' ').trim() : '']).filter(x => /^C0(01|10|23|38|41)$/.test(x[0])))")
    print('D) Regelfenster:', rules)
    ok_d = rules.get('C010') == '(manufactured | made) (by | at)' and rules.get('C023') == '(recorded | overdubbed) at' and rules.get('C001') == 'phonographic copyright' \
        and rules.get('C041') == 'produced in'
    print('A)', ok_a, '| B)', ok_b, '| C)', ok_c, '| D)', ok_d)
    results += [ok_a, ok_b, ok_c, ok_d]
    print('Fehler:', errs)
    results.append(not errs)
    pg.close()

    # A2) Discogs "Kontrabass"
    orig_dg = H.discogs_release

    def dg():
        d = orig_dg()
        d['extraartists'].append({'name': 'Karl Bass', 'anv': '', 'role': 'Kontrabass', 'tracks': '', 'id': 3061, 'join': ''})
        return d

    H.discogs_release = dg
    ctx2 = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx2, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
    pg.wait_for_timeout(800)
    kb = ((pg.evaluate(ROWS).get('Karl Bass') or {'rows': [['']]})['rows'] or [['']])[0]
    ok_a2 = kb == ['Kontrabass', 'instrument', 'double bass', '']
    print('A2) Discogs Kontrabass:', kb, ok_a2)
    results.append(ok_a2)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
