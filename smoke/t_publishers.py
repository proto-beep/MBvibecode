"""Credits Importer 3.31.0: publishers and rights societies (collected item 97; Nate Wooley / Taylor Ho Bynum, "The Throes",
Discogs 6303626: "[Publishers & Rights Societies] • Tomas Fujiwara-BMI : tracks 1, 6, 8 • FlizmoMusic-BMI : tracks 2, 4, 5 •
4WordSeaMusic-BMI : tracks 2, 3, 6, 10 • ThobulousMusic-BMI : tracks 4, 7, 8, 9" – Discogs lists "Published By – Tomas
Fujiwara", "Flizmo Music", "Fourwordseamusic", "Thobulous Music"; answers of 2026-10-25 08:44 and 08:55).
A) Discogs notes with such a block (here on 4 tracks), Discogs lists Tomas Fujiwara, Flizmo Music and Fourwordseamusic, not
   Thobulous Music: no second entry for "FlizmoMusic" or "4WordSeaMusic" (S043, T046: written together, a number as a word);
   ThobulousMusic an entry from the notes; BMI once, rights society (release level, T045).
B) Works matrix: the tracks of the notes as suggestions in each publisher's column (dashed, yellow) – Flizmo Music 2, 4;
   Fourwordseamusic 2, 3; ThobulousMusic 4; the publisher Tomas Fujiwara 1, 3 as a part of the column of the person Tomas
   Fujiwara (right after it, S044); the log names both.
C) MusicBrainz's suggestions by name (the publishers have no MB link): "Flizmo Music", "Four Word Sea Music" (similar, for
   Fourwordseamusic – the notes' "4WordSeaMusic" written apart), "Thobulous Music" (for ThobulousMusic), the label "Tomas
   Fujiwara" for the publisher; for BMI the rights society first (before "BMI Records" with its alias BMI); "Word Sea
   Records" not.
D) Pasted as a text: the same publishers (their tracks set, not suggested), BMI; "Published by Z Songs (ASCAP)" → Z Songs
   and ASCAP; "BIEM/GEMA" → GEMA; nothing listed as not recognized. (The publishers' rows are on the work level: they show
   in the works matrix, not as rows of the entries.)"""
from playwright.sync_api import sync_playwright
import harness as H

NOTES = """[Publishers & Rights Societies]
• Tomas Fujiwara-BMI : tracks 1, 3
• FlizmoMusic-BMI : tracks 2, 4
• 4WordSeaMusic-BMI : tracks 2, 3
• ThobulousMusic-BMI : tracks 4

Barcode: 786497575220"""
TF = H.uid('dddddddd', 71)
H.ARTISTS[3101] = (TF, 'Tomas Fujiwara')
FLIZ, FOUR, THOB, TFL, BMI, BMIR, OTHER = (H.uid('eeeeeeee', k) for k in range(31, 38))
H.MB_SEARCH['label'] = [{'id': FLIZ, 'name': 'Flizmo Music', 'disambiguation': '', 'score': 100},
                        {'id': FOUR, 'name': 'Four Word Sea Music', 'disambiguation': '', 'score': 100},
                        {'id': THOB, 'name': 'Thobulous Music', 'disambiguation': '', 'score': 100},
                        {'id': TFL, 'name': 'Tomas Fujiwara', 'disambiguation': 'publisher', 'score': 100},
                        {'id': BMIR, 'name': 'BMI Records', 'disambiguation': '', 'score': 100, 'aliases': [{'name': 'BMI'}]},
                        {'id': BMI, 'name': 'BMI', 'disambiguation': 'USA rights society', 'type': 'Rights Society', 'score': 100},
                        {'id': OTHER, 'name': 'Word Sea Records', 'disambiguation': '', 'score': 90}]
H.lt(349, '1d4c0b5b-0000-4000-8000-000000000349', 'rights society', 'label', 'release', ())
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
orig = H.discogs_release


def rel():
    d = orig()
    d['notes'] = NOTES
    d['companies'] = [c for c in d['companies'] if c['entity_type_name'] != 'Published By']
    d['companies'] += [{'name': n, 'entity_type_name': 'Published By', 'id': i, 'catno': ''}
                       for n, i in (('Tomas Fujiwara', 1101), ('Flizmo Music', 1102), ('Fourwordseamusic', 1103))]
    d['extraartists'].append({'name': 'Tomas Fujiwara', 'anv': '', 'role': 'Drums', 'tracks': '', 'id': 3101, 'join': ''})
    d['tracklist'][0]['extraartists'].append({'name': 'Tomas Fujiwara', 'anv': '', 'role': 'Written-By', 'tracks': '', 'id': 3101, 'join': ''})
    return d


H.discogs_release = rel
GROUPS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim()), [...g.querySelectorAll('[data-act=name-use]')].map(b => b.dataset.mbid)]))()"""
COLS = """(() => [...document.querySelectorAll('.dci-matrix th[data-colhead]')].map((th) => {
  const name = ((th.querySelector('.dci-mx-colname .dci-mblink, .dci-mx-colname strong') || {}).textContent || '').replace(/^MB/, '').trim();
  const cells = [...document.querySelectorAll(`.dci-mx-cell[data-col="${th.dataset.colhead}"]`)].filter(c => c.classList.contains('dci-mx-on'))
    .map(c => (Number(c.closest('tr').dataset.work) + 1) + (c.classList.contains('dci-mx-sugg') ? 's' : ''));
  return [name, th.classList.contains('dci-mx-subcol') ? 'sub' : th.classList.contains('dci-mx-hassub') ? 'person' : '', cells,
    ((th.querySelector('.dci-mx-pubof') || {}).textContent || '').trim()]; }))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
    pg.wait_for_timeout(1500)
    g = pg.evaluate(GROUPS)
    names = [x[0] for x in g]
    role = {x[0]: x[1] for x in g}
    print('A) Einträge:', names)
    print('   Rollen:', {n: role[n] for n in names if n in ('Flizmo Music', 'Fourwordseamusic', 'ThobulousMusic', 'BMI', 'Tomas Fujiwara')})
    results.append(not any(n in names for n in ('FlizmoMusic', '4WordSeaMusic', 'Thobulous Music')) and names.count('BMI') == 1
                   and role.get('BMI') == ['Rights Society'] and names.count('Tomas Fujiwara') == 2
                   and all(n in names for n in ('ThobulousMusic', 'Flizmo Music', 'Fourwordseamusic')))
    cols = pg.evaluate(COLS)
    print('B) Spalten:', cols)
    by = {(c[0], c[1]): c[2] for c in cols}
    order = [(c[0], c[1]) for c in cols]
    k = order.index(('Tomas Fujiwara', 'person')) if ('Tomas Fujiwara', 'person') in order else -1
    logs = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'as publisher' in x or 'tracks of publishers' in x]
    print('   Protokoll:', [x[9:160] for x in logs])
    results.append(by.get(('Flizmo Music', '')) == ['2s', '4s'] and by.get(('Fourwordseamusic', '')) == ['2s', '3s'] and by.get(('ThobulousMusic', '')) == ['4s']
                   and k >= 0 and order[k + 1] == ('Tomas Fujiwara', 'sub') and by.get(('Tomas Fujiwara', 'sub')) == ['1s', '3s']
                   and by.get(('Tomas Fujiwara', 'person')) == ['1'] and 'Tomas Fujiwara as publisher' in cols[k + 1][3]
                   and any('Tomas Fujiwara as publisher' in x and 'column of Tomas Fujiwara' in x for x in logs)
                   and any('Flizmo Music' in x and 'Fourwordseamusic' in x for x in logs))
    sugg = {x[0]: x[2] for x in g}
    tfc = [x for x in g if x[0] == 'Tomas Fujiwara'][1:]
    print('C) Vorschläge:', {n: [m[-2:] for m in sugg[n]] for n in ('Flizmo Music', 'Fourwordseamusic', 'ThobulousMusic', 'BMI')}, '| Verlag T. F.:', [m[-2:] for m in (tfc[0][2] if tfc else [])])
    results.append(sugg['Flizmo Music'][:1] == [FLIZ] and FOUR in sugg['Fourwordseamusic'] and OTHER not in sugg['Fourwordseamusic']
                   and sugg['ThobulousMusic'][:1] == [THOB] and sugg['BMI'][:1] == [BMI] and bool(tfc) and TFL in tfc[0][2])
    print('Fehler:', errs)
    results.append(not errs)

    # D) the same as a pasted text
    text = NOTES.replace('Barcode: 786497575220', 'Published by Z Songs (ASCAP)\nBIEM/GEMA')
    H.src_menu(pg, 'text-open')
    pg.fill('[data-f=text-src]', text)
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(1500)
    g2 = pg.evaluate(GROUPS)
    role2 = {x[0]: x[1] for x in g2}
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    cols2 = {(c[0], c[1]): c[2] for c in pg.evaluate(COLS)}
    print('D) Text:', role2, '| nicht erkannt:', unrec)
    print('   Spalten:', cols2)
    results.append(all(n in role2 for n in ('Tomas Fujiwara', 'FlizmoMusic', '4WordSeaMusic', 'ThobulousMusic', 'Z Songs'))
                   and all(role2.get(n) == ['Rights Society'] for n in ('BMI', 'ASCAP', 'GEMA')) and 'BIEM' not in role2 and not unrec
                   and cols2.get(('Tomas Fujiwara', '')) == ['1', '3'] and cols2.get(('FlizmoMusic', '')) == ['2', '4']
                   and cols2.get(('4WordSeaMusic', '')) == ['2', '3'] and cols2.get(('ThobulousMusic', '')) == ['4'] and ('Z Songs', '') in cols2)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
