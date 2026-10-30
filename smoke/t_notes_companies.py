"""Discogs notes: places, ℗ / © and publishers named in the notes (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: discnotes, pcline, publishers, personpub, placesearch, facets (3.36.7), notescredits (3.37.0), linkedsugg (3.37.1), festival (3.37.8), pcperson (3.37.10) – each the former smoke/t_<case>.py, unchanged; `python3 t_notes_companies.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_discnotes():
    """Credits Importer 3.30.8: dates per disc and places from the Discogs notes (collected item 98; Wadada Leo Smith with
    Milford Graves and Bill Laswell, "Sacred Ceremonies", Discogs 18973900, three CDs; answers of 2026-10-25 08:55).
    Notes: "All music recorded ... at Orange Music Sound Studios in West Orange, New Jersey, on May 27, 2016 (Disc 1), May 26,
    2016 (Disc 2) and December 11 & 12, 2015 (Disc 3) / All music mastered ... at Turtle Tone Studio in New York City /
    Including a 52 p. booklet. / © & ℗ TUM Records Oy 2021".
    A) Each of the three dates goes under Performance (D021) with the tracks of its disc ("Medium 2 · CD"); December 11 & 12,
       2015 is [3.32.0] their common month, 2015-12 (D022; before: a period); no message about dates without a group (until 3.30.7 only the first date
       had a group, all three the tracks of disc 1).
    B) The places of the notes (S042): Orange Music Sound Studios (recorded at; West Orange, New Jersey) and Turtle Tone Studio
       (mastered at; New York City) – Discogs does not list them.
    C) Discogs lists "Recorded At – Orange Music Sound Studios" and "Mixed At – Turtle Tone Studio": no second entry, no second
       "Recorded At" row; "Mastered At" from the notes joins Discogs's entry of Turtle Tone Studio.
    D) Pasted as a text: the place line is recognized, "Including a 52 p. booklet." is left out on purpose ("about the
       package")."""
    H.MEDIA = [2, 1, 1]
    NOTES = """All music recorded ... at Orange Music Sound Studios in West Orange, New Jersey, on May 27, 2016 (Disc 1), May 26, 2016 (Disc 2) and December 11 & 12, 2015 (Disc 3)
All music mastered ... at Turtle Tone Studio in New York City

Including a 52 p. booklet.

© & ℗ TUM Records Oy 2021"""
    H.COMPANIES[1011] = ('place', H.uid('eeeeeeee', 11), 'Orange Music Sound Studios')
    H.COMPANIES[1012] = ('place', H.uid('eeeeeeee', 12), 'Turtle Tone Studio')
    H.lt(1206, '1d4c0b5b-0000-4000-8000-000000001206', 'mastered at', 'place', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    WITH_COMPANIES = [False]
    orig = H.discogs_release


    def rel():
        d = orig()
        for i, t in enumerate(d['tracklist']):
            t['position'] = ['1-1', '1-2', '2-1', '3-1'][i]
        d['notes'] = NOTES
        d['companies'] = [c for c in d['companies'] if c['entity_type_name'] not in ('Recorded At', 'Phonographic Copyright (p)')]
        if WITH_COMPANIES[0]:
            d['companies'] += [{'name': 'Orange Music Sound Studios', 'entity_type_name': 'Recorded At', 'id': 1011, 'catno': ''},
                               {'name': 'Turtle Tone Studio', 'entity_type_name': 'Mixed At', 'id': 1012, 'catno': ''}]
        return d


    H.discogs_release = rel
    GROUPS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim()), ((g.querySelector('.dci-gname .dci-sub') || {}).textContent || '').trim()]))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        pool = {d['id']: d for d in pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]')")}
        tgs = {g['id']: g for g in pg.evaluate(f"JSON.parse(localStorage.getItem('dci-track-pool:{H.REL}') || '[]')")}
        cells = pg.evaluate(f"(JSON.parse(localStorage.getItem('dci-date-matrix:{H.REL}') || '{{}}').cells || [])")
        day = lambda d: '-'.join(str(x) for x in (d['begin']['year'], d['begin']['month'], d['begin']['day'])) + ('/' + str(d['end']['day']) if d['end'].get('day') != d['begin'].get('day') else '')
        perf = sorted((day(pool[c['date']]), [(tgs[t]['name'], tgs[t]['tracks']) for t in c['tgs']], len(c.get('alt') or [])) for c in cells if c['col'] == 'performance')
        msgs = pg.locator('.dci-msg').all_inner_texts()
        print('A) Performance:', perf, '| Meldungen:', [m[:70] for m in msgs])
        results.append([x[:2] for x in perf] == [('2015-12-None', [('Medium 3 · CD', [3])]), ('2016-5-26', [('Medium 2 · CD', [2])]), ('2016-5-27', [('Medium 1 · CD', [0, 1])])]
                       and not any('no word naming' in m for m in msgs))
        g = pg.evaluate(GROUPS)
        places = [x for x in g if x[0] in ('Orange Music Sound Studios', 'Turtle Tone Studio')]
        print('B) Orte:', places)
        results.append(places == [['Orange Music Sound Studios', ['Recorded At'], '(West Orange, New Jersey)'], ['Turtle Tone Studio', ['Mastered At'], '(New York City)']])
        # D) the same as a pasted text
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', NOTES)
        pg.click('[data-act=text-load]')
        H.answer_media(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        left = pg.evaluate("[...document.querySelectorAll('.dci-unrec, .dci-ignored, details')].map(x => x.textContent.replace(/\\s+/g, ' ')).join(' | ')")
        g2 = [x[0] for x in pg.evaluate(GROUPS)]
        print('D) Text – nicht erkannt:', unrec, '| Einträge:', g2, '| ausgelassen:', 'about the package' in left)
        results.append(not any('Orange Music' in u or 'booklet' in u for u in unrec) and 'Orange Music Sound Studios' in g2 and 'about the package' in left)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()

    # C) Discogs lists the places already
    WITH_COMPANIES[0] = True
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        g = pg.evaluate(GROUPS)
        places = [x[:2] for x in g if x[0] in ('Orange Music Sound Studios', 'Turtle Tone Studio')]
        print('C) mit Discogs-Firmen:', places)
        results.append(places == [['Orange Music Sound Studios', ['Recorded At']], ['Turtle Tone Studio', ['Mixed At', 'Mastered At']]])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_pcline():
    """Credits Importer 3.30.9: "© & ℗ TUM Records Oy 2021" – the label for ℗ and © (collected item 99; answers of
    2026-10-25 08:55: "nur wenn P und C auch erwähnt sind. falls nur P oder nur C einzeln erwähnt sind soll jeweils nur das
    angeboten werden").
    A) Discogs notes "© & ℗ TUM Records Oy 2021", Discogs lists no ℗/©: the entry TUM Records Oy with phonographic copyright
       and copyright (the year stays a date of the pool); MusicBrainz's TUM Records Oy and TUM Records are both suggested
       (T044: without the legal form "Oy"), another label not.
    B) Discogs lists "Copyright (c) – TUM Records Oy": only ℗ comes from the notes, onto Discogs's entry.
    C) A pasted text: "℗ 2020 Solo P Records" only phonographic copyright, "© Solo C Records 2019" only copyright,
       "© & ℗ TUM Records Oy 2021" both."""
    NOTES = 'Recorded in Helsinki.\n\n© & ℗ TUM Records Oy 2021'
    TUM_OY, TUM, OTHER = H.uid('eeeeeeee', 21), H.uid('eeeeeeee', 22), H.uid('eeeeeeee', 23)
    H.MB_SEARCH['label'] = [{'id': TUM_OY, 'name': 'TUM Records Oy', 'disambiguation': '', 'score': 100},
                            {'id': TUM, 'name': 'TUM Records', 'disambiguation': '', 'score': 100},
                            {'id': OTHER, 'name': 'TUM Recordings Ltd', 'disambiguation': '', 'score': 90}]
    H.COMPANIES[1021] = ('label', H.uid('eeeeeeee', 24), 'TUM Records Oy (linked)')
    C_LISTED = [False]
    orig = H.discogs_release


    def rel():
        d = orig()
        d['notes'] = NOTES
        d['companies'] = [c for c in d['companies'] if 'Copyright' not in c['entity_type_name']]
        if C_LISTED[0]:
            d['companies'].append({'name': 'TUM Records Oy', 'entity_type_name': 'Copyright (c)', 'id': 1021, 'catno': ''})
        return d


    H.discogs_release = rel
    GROUP = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  return g ? { roles: [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim()), sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.dataset.mbid) } : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1500)
        a1 = pg.evaluate(GROUP, 'TUM Records Oy')
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => [d.name, d.begin.year])")
        print('A) TUM Records Oy:', a1, '| Pool:', pool)
        results.append(a1 and a1['roles'] == ['Phonographic Copyright (p)', 'Copyright (c)'] and TUM_OY in a1['sugg'] and TUM in a1['sugg'] and OTHER not in a1['sugg']
                       and any(y == 2021 for _, y in pool))
        # C) a pasted text
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', '℗ 2020 Solo P Records\n© Solo C Records 2019\n© & ℗ TUM Records Oy 2021')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        c1 = {n: (pg.evaluate(GROUP, n) or {}).get('roles') for n in ('Solo P Records', 'Solo C Records', 'TUM Records Oy')}
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        print('C) Text:', c1, '| nicht erkannt:', unrec)
        results.append(c1 == {'Solo P Records': ['Phonographic Copyright (p)'], 'Solo C Records': ['Copyright (c)'], 'TUM Records Oy': ['Phonographic Copyright (p)', 'Copyright (c)']}
                       and not unrec)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()

    # B) Discogs lists the copyright already
    C_LISTED[0] = True
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1500)
        names = pg.evaluate("[...document.querySelectorAll('section.dci-group .dci-gname strong')].map(x => x.textContent.trim())")
        b1 = [(n, pg.evaluate(GROUP, n)['roles']) for n in names if 'TUM' in n]
        print('B) Discogs listet ©:', b1)
        results.append(len(b1) == 1 and b1[0][1] == ['Copyright (c)', 'Phonographic Copyright (p)'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_publishers():
    """Credits Importer 3.31.0: publishers and rights societies (collected item 97; Nate Wooley / Taylor Ho Bynum, "The Throes",
    Discogs 6303626: "[Publishers & Rights Societies] • Tomas Fujiwara-BMI : tracks 1, 6, 8 • FlizmoMusic-BMI : tracks 2, 4, 5 •
    4WordSeaMusic-BMI : tracks 2, 3, 6, 10 • ThobulousMusic-BMI : tracks 4, 7, 8, 9" – Discogs lists "Published By – Tomas
    Fujiwara", "Flizmo Music", "Fourwordseamusic", "Thobulous Music"; answers of 2026-10-25 08:44 and 08:55).
    A) Discogs notes with such a block (here on 4 tracks), Discogs lists Tomas Fujiwara, Flizmo Music and Fourwordseamusic, not
       Thobulous Music: no second entry for "FlizmoMusic" or "4WordSeaMusic" (S043, T046: written together, a number as a word);
       ThobulousMusic an entry from the notes; BMI once, rights society (release level, T045). [3.31.5] The publisher Tomas
       Fujiwara is the person Tomas Fujiwara (S044): one entry with Drums and Published By (the row says that Discogs lists it
       as a company), no company entry. (From 3.31.5 a publisher's row shows in its entry too, for its level – item 112.)
    B) Works matrix: the tracks of the notes in each publisher's column – [3.31.6] set, not suggested, ⓘ at the row names the
       line (item 97c) – Flizmo Music 2, 4; Fourwordseamusic 2, 3; ThobulousMusic 4; [3.31.5] Tomas Fujiwara one column:
       writer on 1, publishing on 1 and 3 (artist–work "publishing"); the log names it (before 3.31.5: a part of the person's
       column with a label of its own).
    C) MusicBrainz's suggestions by name (the publishers have no MB link): "Flizmo Music", "Four Word Sea Music" (similar, for
       Fourwordseamusic – the notes' "4WordSeaMusic" written apart), "Thobulous Music" (for ThobulousMusic); for BMI the
       rights society first (before "BMI Records" with its alias BMI); "Word Sea Records" not.
    D) Pasted as a text: the same publishers (their tracks set, not suggested), BMI; "Published by Z Songs (ASCAP)" → Z Songs
       and ASCAP; "BIEM/GEMA" → GEMA; nothing listed as not recognized. [3.31.5] Tomas Fujiwara has no person entry here: the
       publisher with a person's name gets MusicBrainz's artist Tomas Fujiwara as suggestion, not the label of that name
       (no type "Publisher"), and "Create artist …" (S048)."""
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
  [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim()), [...g.querySelectorAll('[data-act=name-use]')].map(b => b.dataset.mbid),
  [...g.querySelectorAll('[data-act=company-create]')].map(b => b.dataset.et), [...g.querySelectorAll('tr.dci-row .dci-sub')].map(x => x.textContent.replace(/\\s+/g, ' ').trim()).join(' | ')]))()"""
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
        tfrow = [x[4] for x in g if x[0] == 'Tomas Fujiwara']
        print('   Tomas Fujiwara:', tfrow)
        results.append(not any(n in names for n in ('FlizmoMusic', '4WordSeaMusic', 'Thobulous Music')) and names.count('BMI') == 1
                       and role.get('BMI') == ['Rights Society'] and names.count('Tomas Fujiwara') == 1 and role.get('Tomas Fujiwara') == ['Drums', 'Published By']
                       and 'Discogs lists it as a company' in tfrow[0] and 'S044' in tfrow[0]
                       and all(n in names for n in ('ThobulousMusic', 'Flizmo Music', 'Fourwordseamusic')))
        cols = pg.evaluate(COLS)
        print('B) Spalten:', cols)
        by = {(c[0], c[1]): c[2] for c in cols}
        order = [(c[0], c[1]) for c in cols]
        logs = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'as publisher' in x or 'tracks of publishers' in x]
        print('   Protokoll:', [x[9:160] for x in logs])
        fl = [x[4] for x in g if x[0] == 'Flizmo Music']
        print('   Flizmo Music:', fl)
        results.append(by.get(('Flizmo Music', '')) == ['2', '4'] and by.get(('Fourwordseamusic', '')) == ['2', '3'] and by.get(('ThobulousMusic', '')) == ['4']
                       and order.count(('Tomas Fujiwara', '')) == 1 and by.get(('Tomas Fujiwara', '')) == ['1', '3'] and not any(c[1] for c in cols)
                       and 'Tracks 2, 4 from the notes' in fl[0]
                       and any('Tomas Fujiwara as publisher is the person Tomas Fujiwara' in x for x in logs)
                       and any('Flizmo Music' in x and 'Fourwordseamusic' in x for x in logs))
        sugg = {x[0]: x[2] for x in g}
        print('C) Vorschläge:', {n: [m[-2:] for m in sugg[n]] for n in ('Flizmo Music', 'Fourwordseamusic', 'ThobulousMusic', 'BMI')})
        results.append(sugg['Flizmo Music'][:1] == [FLIZ] and FOUR in sugg['Fourwordseamusic'] and OTHER not in sugg['Fourwordseamusic']
                       and sugg['ThobulousMusic'][:1] == [THOB] and sugg['BMI'][:1] == [BMI])
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
        tf2 = [x for x in g2 if x[0] == 'Tomas Fujiwara']
        print('D) Text:', role2, '| nicht erkannt:', unrec, '| Tomas Fujiwara:', tf2)
        print('   Spalten:', cols2)
        results.append(all(n in role2 for n in ('Tomas Fujiwara', 'FlizmoMusic', '4WordSeaMusic', 'ThobulousMusic', 'Z Songs'))
                       and all(role2.get(n) == ['Rights Society'] for n in ('BMI', 'ASCAP', 'GEMA')) and 'BIEM' not in role2 and not unrec
                       and cols2.get(('Tomas Fujiwara', '')) == ['1', '3'] and cols2.get(('FlizmoMusic', '')) == ['2', '4']
                       and cols2.get(('4WordSeaMusic', '')) == ['2', '3'] and cols2.get(('ThobulousMusic', '')) == ['4'] and ('Z Songs', '') in cols2
                       and len(tf2) == 1 and tf2[0][2] == [TF] and tf2[0][3] == ['artist'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_personpub():
    """Credits Importer 3.31.5: a publisher's level, a publisher with a person's name (collected items 112 and 97b; maintainer:
    "bei publishing relationships von Labeln muss auch angeboten werden, dass sie auf release oder work ebene stattfinden
    können. wir haben ja bereits die möglichkeit in der kompakt info das durchzuklicken. so soll das laufen.", "ja bitte. es
    ist ja einfach ihn nicht zu verwenden"; "bitte nicht create label für personen anbieten!").
    A) Full view: the label Pub Co ("Published By") shows its row in its entry too, on "Works" (default); its level buttons
       offer the release; "Release" → the label–release "published", the column of Pub Co leaves the works matrix; "Works"
       again → back.
    B) Compact view: a click on the level of the row's line goes on to the next level (Works → Skip → Release → Works).
    C) "Published By – Jane Roe" (no entry of the dashboard, no MusicBrainz link; S048): MusicBrainz's artist Jane Roe first,
       the label "Jane Roe" of the type Publisher too, the label "Jane Roe" without that type not; "Create artist …", no
       "Create label …" (MusicBrainz has an artist of exactly that name); the artist chosen → the column of Jane Roe links an
       artist, its role publishing (artist–work). "Ghost Pub" (a name like a person's, but no artist of that name in
       MusicBrainz): "Create artist …" and "Create label …"."""
    JR, JRP, JRL = H.uid('dddddddd', 81), H.uid('eeeeeeee', 81), H.uid('eeeeeeee', 82)
    H.ARTISTS[3181] = (JR, 'Jane Roe')
    H.MB_SEARCH['label'] = [{'id': JRP, 'name': 'Jane Roe', 'disambiguation': 'publisher', 'type': 'Publisher', 'score': 100},
                            {'id': JRL, 'name': 'Jane Roe', 'disambiguation': 'a shop', 'score': 100}]
    orig = H.discogs_release

    def rel():
        d = orig()
        d['companies'].append({'name': 'Jane Roe', 'entity_type_name': 'Published By', 'id': 1181, 'catno': ''})
        return d

    H.discogs_release = rel
    ROW = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; const tr = g.querySelector('tr.dci-row'); if (!tr) return { rows: 0 };
  const t = tr.querySelector('[data-f=type]'); const lv = tr.querySelector('[data-act=level][aria-pressed=true]');
  return { rows: g.querySelectorAll('tr.dci-row').length, id: tr.dataset.row, type: t ? (t.options[t.selectedIndex] || {}).text : '',
    level: lv ? lv.dataset.level : '', levels: [...tr.querySelectorAll('[data-act=level]')].map(b => b.dataset.level),
    cl: ((tr.querySelector('.dci-cl-level') || {}).dataset || {}).level || '',
    sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.dataset.mbid), create: [...g.querySelectorAll('[data-act=company-create]')].map(b => b.dataset.et) }; }"""
    COLS = """(() => Object.fromEntries([...document.querySelectorAll('.dci-matrix th[data-colhead]')].map(th => {
  const a = th.querySelector('.dci-mx-colname .dci-mblink, .dci-mx-colname strong');
  return [a.textContent.replace(/^MB/, '').trim(), [a.getAttribute('href') || '', [...th.querySelectorAll('.dci-mx-role')].map(x => x.textContent.trim())]]; })))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(1200)
        # A)
        a0, c0 = pg.evaluate(ROW, 'Pub Co'), pg.evaluate(COLS)
        pg.click(f'tr[data-row="{a0["id"]}"] [data-act=level][data-level=release]')
        pg.wait_for_timeout(500)
        a1, c1 = pg.evaluate(ROW, 'Pub Co'), pg.evaluate(COLS)
        pg.click(f'tr[data-row="{a0["id"]}"] [data-act=level][data-level=work]')
        pg.wait_for_timeout(500)
        a2, c2 = pg.evaluate(ROW, 'Pub Co'), pg.evaluate(COLS)
        print('A) Pub Co:', a0, '| Spalte:', 'Pub Co' in c0, '\n   Release:', [a1['type'], a1['level']], 'Pub Co' in c1, '| Works:', [a2['type'], a2['level']], 'Pub Co' in c2)
        results.append(a0['rows'] == 1 and a0['level'] == 'work' and a0['levels'] == ['release', 'work', 'skip'] and 'Pub Co' in c0
                       and [a1['type'], a1['level']] == ['published', 'release'] and 'Pub Co' not in c1
                       and [a2['type'], a2['level']] == ['publishing', 'work'] and 'Pub Co' in c2)
        # C)
        j0, g0 = pg.evaluate(ROW, 'Jane Roe'), pg.evaluate(ROW, 'Ghost Pub')
        print('C) Jane Roe:', j0['sugg'], j0['create'], '| Ghost Pub:', g0['create'])
        results.append(j0['sugg'] == [JR, JRP] and j0['create'] == ['artist'] and g0['create'] == ['artist', 'label'])
        pg.click(f'section.dci-group:has(.dci-gname strong:text-is("Jane Roe")) [data-act=name-use][data-mbid="{JR}"]')
        pg.wait_for_timeout(800)
        c3, j1 = pg.evaluate(COLS), pg.evaluate(ROW, 'Jane Roe')
        print('   gewählt:', c3.get('Jane Roe'), j1['type'])
        results.append(c3.get('Jane Roe', ['', []])[0] == f'/artist/{JR}' and j1['type'] == 'publishing' and c3['Jane Roe'][1] == ['publishing'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    # B) the compact view
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, view='compact')
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(1200)
        seq = []
        for _ in range(4):
            r = pg.evaluate(ROW, 'Pub Co')
            seq.append(r['cl'])
            if len(seq) < 4:
                pg.click(f'tr[data-row="{r["id"]}"] [data-act=level-next]')
                pg.wait_for_timeout(400)
        print('B) kompakt:', seq)
        results.append(seq == ['work', 'skip', 'release', 'work'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_placesearch():
    """Credits Importer 3.31.2: places from the notes and from texts get MusicBrainz's suggestions (collected items 98b and
    114; maintainer, Discogs 18973900: "die orte kommen als vorschläge in "Companies, etc.". allerdings werden sie wohl
    nicht mit den places abgeglichen? … die places liegen in MB vor."; "daten wie "Recorded November 7, 8, 2016, at Loft
    Köln." müssen erkannt werden").
    A) Discogs notes "… at Orange Music Sound Studios in West Orange, New Jersey …" and "… at Turtle Tone Studio in New York
       City": MusicBrainz's place in West Orange is suggested (the first part of the area); Turtle Tone Studio, in
       Manhattan, is found by its name alone and offered as similar; the log says "looking for the same name" (before: "no
       MB artist with this Discogs link").
    B) A pasted text "Recorded November 7, 8, 2016, at Loft Köln.": the date pool has 2016-11-07 – 2016-11-08 (D013 with
       commas only; before: only 2016); the entry "Loft Köln" gets MusicBrainz's "Loft" in Cologne (alias Köln) as similar,
       its area "(Köln)"."""
    NOTES = """All music recorded ... at Orange Music Sound Studios in West Orange, New Jersey, on May 27, 2016
All music mastered ... at Turtle Tone Studio in New York City"""
    P1, P2, P3, P4, A1 = (H.uid('eeeeeeee', k) for k in (61, 62, 63, 64, 65))
    H.MB_SEARCH['place'] = [{'id': P1, 'name': 'Orange Music Sound Studios', 'disambiguation': '', 'score': 100, 'area': {'name': 'West Orange'}},
                            {'id': P2, 'name': 'Turtle Tone Studio', 'disambiguation': '', 'score': 100, 'area': {'name': 'Manhattan'}},
                            {'id': P3, 'name': 'Loft', 'disambiguation': '', 'score': 100, 'area': {'name': 'Cologne'}},
                            {'id': P4, 'name': 'Loft', 'disambiguation': '', 'score': 90, 'area': {'name': 'Berlin'}}]
    H.MB_SEARCH['area'] = [{'id': A1, 'name': 'Cologne', 'disambiguation': '', 'score': 100, 'aliases': [{'name': 'Köln'}]}]
    H.lt(1206, '1d4c0b5b-0000-4000-8000-000000001206', 'mastered at', 'place', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release

    def rel():
        d = orig()
        d['notes'] = NOTES
        d['companies'] = [c for c in d['companies'] if c['entity_type_name'] != 'Recorded At']
        return d

    H.discogs_release = rel
    GROUP = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
      return g ? { head: g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(),
        sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => [b.dataset.mbid, !!b.querySelector('.dci-similar')]) } : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(800)
        o = pg.evaluate(GROUP, 'Orange Music Sound Studios')
        t = pg.evaluate(GROUP, 'Turtle Tone Studio')
        logs = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'Studio' in x]
        print('A) Orange:', o, '| Turtle:', t)
        print('   Protokoll:', [x[9:] for x in logs])
        results.append(o and o['sugg'][:1] == [[P1, False]] and t and t['sugg'][:1] == [[P2, True]]
                       and not any('no MB artist' in x for x in logs) and any('looking for the same name' in x for x in logs))
        # B) a pasted text
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Recorded November 7, 8, 2016, at Loft Köln.')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1000)
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').filter(d => d.begin.year === 2016).map(d => [d.begin.month, d.begin.day, d.end.day])")
        loft = pg.evaluate(GROUP, 'Loft Köln')
        print('B) Pool 2016:', pool, '| Loft Köln:', loft)
        results.append([11, 7, 8] in pool and loft and loft['sugg'][:1] == [[P3, True]] and P4 not in [x[0] for x in loft['sugg']] and '(Köln)' in loft['head'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_facets():
    """Credits Importer 3.36.7 (collected item 150, S053; maintainer, about Discogs 3139201 "Facets" – MB ad8fe956-…: "warum wird bei
    dem Facets release … Goldsmiths College 2x angeboten und dann auch noch an den falschen tracks und ohne date? das muss gefixt
    werden"; "in live concert": "ja das muss dann eine live Work Verknüpfung generieren und als disambiguation übernommen werden").
    Three LPs, 13 tracks; Discogs lists "Recorded At – Goldsmiths College" for the whole release; the notes: "A1 to B2 recorded 22nd
    May 1981 in live concert at Goldsmith's College, London / C1 to D recorded 4th October 1979 at Heiman Recording Studios, London /
    E1 to F2 recorded 2nd May 1980 at Heiman Recording Studios, London".
    A) Goldsmiths College only on A1–B2 (set, ⓘ shows the line; until 3.36.6 on all 13 tracks), Heiman Recording Studios (London) a
       place from the notes on C1–D and E1–F2 (until 3.36.6 not read: the date between "recorded" and "at", the positions without
       "Tracks").
    B) After "Apply" of the date matrix: Goldsmiths one row with 1981-05-22; Heiman two – 1979-10-04 on C1–D, 1980-05-02 on E1–F2
       (until 3.36.6 Goldsmiths got all three dates).
    C) "in live concert": the new work of A2 has "li" preselected (S021), the existing link of A1 offers it; with ⚙ Settings → Staging
       "live comments" on, A2's comment is "live, 1981‐05‐22: Goldsmiths College".
    D) Pasted as a text: "1.1 to 1.2 recorded 3rd June 2001 at Abbey Road Studios, London" – the place on these two tracks."""
    import re
    POS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D', 'E1', 'E2', 'E3', 'E4', 'F1', 'F2']
    H.REC[:] = [H.uid('bbbbbbbb', i) for i in range(1, 14)]
    H.TITLES[:] = ['Song One', 'Song Two', 'Song Three', 'Song Four'] + [f'Piece {i}' for i in range(5, 14)]
    H.MEDIA = [4, 3, 6]
    for i, n in [(567, 'cover'), (578, 'live'), (750, 'medley')]:
        H.attr(i, n, i)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578, 750))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    NOTES = """A1 to B2 recorded 22nd May 1981 in live concert at Goldsmith's College, London
C1 to D recorded 4th October 1979 at Heiman Recording Studios, London
E1 to F2 recorded 2nd May 1980 at Heiman Recording Studios, London"""
    H.COMPANIES[1013] = ('place', H.uid('eeeeeeee', 13), 'Goldsmiths College')
    orig = H.discogs_release

    def rel():
        d = orig()
        for i, t in enumerate(d['tracklist']):
            t['position'] = POS[i]
        d['notes'] = NOTES
        d['companies'] = [c for c in d['companies'] if c['entity_type_name'] != 'Recorded At'] + [
            {'name': 'Goldsmiths College', 'entity_type_name': 'Recorded At', 'id': 1013, 'catno': ''}]
        return d

    H.discogs_release = rel
    PLACES = """(() => [...document.querySelectorAll('section.dci-group')].filter(g => /Goldsmith|Heiman|Abbey/.test(g.querySelector('.dci-gname strong').textContent)).map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row')].filter(r => !r.className.includes('dci-lv-skip')).map(r => [(r.querySelector('.dci-drole') || {}).textContent,
    [...r.querySelectorAll('[data-f=track]:checked, input[data-i]:checked')].length || (r.querySelector('.dci-c-tracks, .dci-tracks') || {textContent: ''}).textContent.replace(/\\s+/g, ' ').trim().slice(0, 40),
    ((r.querySelector('.dci-notesfrom') || {}).textContent || '').replace(/\\s+/g, ' ').trim(), ((r.querySelector('.dci-notesfrom .dci-info') || {}).title || '').slice(0, 80),
    (r.textContent.match(/Performance \\d · [\\d-]+/) || [''])[0]])]))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)
        # tracks of a row, from its selection (1.1 … 3.6)
        TRK = """(name) => [...document.querySelectorAll('section.dci-group')].filter(g => g.querySelector('.dci-gname strong').textContent.trim() === name)
  .flatMap(g => [...g.querySelectorAll('tr.dci-row')]).filter(r => !r.className.includes('dci-lv-skip')).map(r => [(r.querySelector('.dci-trk-sum, .dci-tracks-sum, .dci-c-tracks') || {textContent: ''}).textContent.replace(/\\s+/g, ' ').trim().slice(0, 30),
    ((r.querySelector('.dci-notesfrom') || {}).textContent || '').replace(/\\s+/g, ' ').trim(), ((r.querySelector('.dci-notesfrom .dci-info') || {}).title || ''),
    (r.textContent.match(/Performance \\d · [\\d-]+/) || [''])[0]])"""
        a1 = pg.evaluate(TRK, 'Goldsmiths College')
        a2 = pg.evaluate(TRK, 'Heiman Recording Studios')
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'notes' in x.lower()]
        print('A) Goldsmiths:', a1, '\n   Heiman:', a2, '\n   Protokoll:', logs)
        results.append(len(a1) == 1 and 'A1–B2' in a1[0][1] and 'Goldsmith' in a1[0][2] and len(a2) == 1 and 'C1–D, E1–F2' in a2[0][1]
                       and any('Heiman Recording Studios (Recorded At)' in x for x in logs) and any('Goldsmiths College (1.1–1.4)' in x for x in logs))
        # B) the date matrix applied
        pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()')
        pg.wait_for_timeout(1500)
        b1 = pg.evaluate(TRK, 'Goldsmiths College')
        b2 = pg.evaluate(TRK, 'Heiman Recording Studios')
        n_tracks = pg.evaluate("""(name) => [...document.querySelectorAll('section.dci-group')].filter(g => g.querySelector('.dci-gname strong').textContent.trim() === name)
  .flatMap(g => [...g.querySelectorAll('tr.dci-row')]).filter(r => !r.className.includes('dci-lv-skip')).map(r => ((r.textContent.match(/(\\d+) of 13 tracks/) || [])[1] || '') + ' ' + ((r.textContent.match(/Performance \\d · [\\d-]+/) || [''])[0]))""", 'Heiman Recording Studios')
        g_tracks = pg.evaluate("""(name) => [...document.querySelectorAll('section.dci-group')].filter(g => g.querySelector('.dci-gname strong').textContent.trim() === name)
  .flatMap(g => [...g.querySelectorAll('tr.dci-row')]).filter(r => !r.className.includes('dci-lv-skip')).map(r => ((r.textContent.match(/(\\d+) of 13 tracks/) || [])[1] || '') + ' ' + ((r.textContent.match(/Performance \\d · [\\d-]+/) || [''])[0]))""", 'Goldsmiths College')
        print('B) Goldsmiths:', g_tracks, '| Heiman:', n_tracks)
        results.append(g_tracks == ['4 Performance 1 · 1981-05-22'] and sorted(n_tracks) == ['3 Performance 2 · 1979-10-04', '6 Performance 3 · 1980-05-02'])
        # C) live: a new work for A2, its link "li"; the comment (⚙ Settings → Staging: live comments on)
        pg.click('tr[data-work="1"] [data-act=work-pending]')
        pg.wait_for_timeout(500)
        H.open_settings(pg, 'staging')
        pg.check('[data-el=settings] [data-set=live-comments]')
        pg.wait_for_timeout(300)
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
        pg.wait_for_timeout(500)
        pills = pg.evaluate("""[0, 1].map(i => [...document.querySelectorAll('.dci-matrix tbody tr[data-work="' + i + '"] .dci-wpill-on, .dci-matrix tbody tr[data-work="' + i + '"] .dci-wpill-hint')].map(b => b.textContent.trim()))""")
        com = pg.evaluate("[...document.querySelectorAll('.dci-livecom-table [data-f=livecom-text]')].map(x => x.value)")
        print('C) li an A1, A2:', pills, '| Kommentar:', com)
        results.append(pills[0] == ['li?'] and pills[1] == ['li'] and com == ['live, 1981‐05‐22: Goldsmiths College'])
        # D) pasted as a text
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', '1.1 to 1.2 recorded 3rd June 2001 at Abbey Road Studios, London')
        pg.click('[data-act=text-load]')
        if pg.locator('[data-el=media] [data-mact=ok]').count():
            H.answer_media(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        d1 = pg.evaluate("""(name) => [...document.querySelectorAll('section.dci-group')].filter(g => g.querySelector('.dci-gname strong').textContent.trim().startsWith(name))
  .flatMap(g => [...g.querySelectorAll('tr.dci-row')]).map(r => [(r.querySelector('.dci-drole') || {}).textContent, ((r.textContent.match(/(\\d+) of 13 tracks/) || [])[1] || '')])""", 'Abbey Road Studios')
        print('D) Text:', d1)
        results.append(d1 == [['Recorded At', '2']])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_notescredits():
    """Credits Importer 3.37.0 (E5, rule S054; maintainer: "dann nimm E5 bitte auch in die Sammelliste auf", "gleich als Eintrag mit
    Transparenzhinweis", "also alle informationen die sonst noch nicht per relationships vorhanden sind sollen abgegriffen werden. (es
    soll sich nichts doppeln)", "ja bitte mit schalter. und vielleicht auch noch bei der quelle (falls discogs import) ein quick
    switch?"). The Discogs notes read in full:
    A) New names an entry each – Ann Blow (saxophone, track 3), Jane Notes (liner notes), Nobody Here (strings arranged, 2, 4) –,
       a new role of a Discogs name a row of its entry (Bass Man: backing vocals), each "From the Discogs notes" with ⓘ and the
       line; nothing twice: Bob Producer ("Produced by" = "Produced By" – its two lines give it tracks 1 and 3, ⓘ), Bass Man's bass,
       Abbey Road Studios ("Recorded … at"; "Mastered by Abbey Road Studios" is no person); "Executive producer: Bob Producer" is a
       role of its own (3.37.0, after a review: the kinds of roles compared strictly); Guitar Guy's guitar (whole release on Discogs)
       gets the tracks of the notes (1, 3; ⓘ). The log names them.
    B) Source ▾ "Leave out the credits of the notes": their rows hidden (also the entries made of them), stored for the release;
       ticked off: back with what was changed in them.
    C) ⚙ Settings → Texts "Discogs: read the credits in the notes" off (the rule S054) and imported again: none of them, Guitar Guy
       on all tracks; on again: back."""
    import json
    NOTES = """Recorded March 1–3, 2001 at Abbey Road Studios.
Strings arranged by Nobody Here (2, 4).
Produced by Bob Producer (1).
Produced by Bob Producer (3).
Executive producer: Bob Producer
Mastered by Abbey Road Studios
Bass Man – bass, backing vocals
Guitar Guy – guitar (tracks 1, 3)
Saxophone: Ann Blow (3)
Liner notes by Jane Notes"""
    orig = H.discogs_release

    def rel():
        d = orig()
        d['notes'] = NOTES
        return d

    H.discogs_release = rel
    GROUPS = """(() => [...document.querySelectorAll('section.dci-group')].filter(g => !g.classList.contains('dci-about-hidden')).map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row')].filter(r => !r.classList.contains('dci-about-hidden')).map(r => [(r.querySelector('.dci-drole') || {}).textContent.trim(), (r.textContent.match(/(\\d+) of 4 tracks/) || [])[1] || '',
    ((r.querySelector('.dci-notesline') || {}).title || '').replace(/^From the Discogs notes: /, ''), /From the Discogs notes/.test(r.textContent),
    ((r.querySelector('.dci-notesfrom') || {}).textContent || '').replace(/\\s+/g, ' ').trim()])]))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())

        def load():
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
        load()
        g = {n: rows for n, rows in pg.evaluate(GROUPS)}
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'notes' in x.lower()]
        print('A)', json.dumps({k: g.get(k) for k in ('Ann Blow', 'Jane Notes', 'Nobody Here', 'Bass Man', 'Guitar Guy', 'Bob Producer', 'Abbey Road Studios')}, ensure_ascii=False))
        print('   Protokoll:', logs)
        ok_a = (g.get('Ann Blow') == [['Saxophone', '1', '“Saxophone: Ann Blow (3)”', True, '']]
                and g.get('Jane Notes') == [['Liner notes', '', '“Liner notes by Jane Notes”', True, '']]
                and 'Nobody Here' in g
                and [r[0] for r in g.get('Bass Man', [])] == ['Bass', 'backing vocals'] and g['Bass Man'][1][3] and not g['Bass Man'][0][3]
                and g.get('Guitar Guy') == [['Guitar', '2', '', False, 'ⓘ Tracks 1, 3 from the notes']]
                and g.get('Bob Producer') == [['Produced By', '2', '', False, 'ⓘ Tracks 1, 3 from the notes'],
                                              ['Executive producer', '', '“Executive producer: Bob Producer”', True, '']]
                and [r[0] for r in g.get('Abbey Road Studios', [])] == ['Recorded At']
                and any('credits not listed by Discogs (5)' in x and 'Ann Blow (Saxophone)' in x for x in logs)
                and any('Guitar Guy – Guitar (1, 3)' in x for x in logs) and not any('Ann Blow' in x and 'only a track group' in x for x in logs))
        results.append(ok_a)
        # B) left out for this release, from the menu Source ▾
        H.src_menu(pg, None)
        box = pg.locator('[data-f=notes-off]')
        has = box.count()
        if has:
            box.check()
            pg.wait_for_timeout(500)
        b1 = {n: rows for n, rows in pg.evaluate(GROUPS)}
        stored = pg.evaluate(f"localStorage.getItem('dci-notes-off:{H.REL}')")
        H.src_menu(pg, None)
        pg.locator('[data-f=notes-off]').uncheck()
        pg.wait_for_timeout(500)
        b2 = {n: rows for n, rows in pg.evaluate(GROUPS)}
        print('B) Menü:', has, '| aus:', sorted(b1), '| Bass Man:', [r[0] for r in b1.get('Bass Man', [])], '| gespeichert:', stored, '| wieder:', 'Ann Blow' in b2, [r[0] for r in b2.get('Bass Man', [])])
        results.append(has == 1 and 'Ann Blow' not in b1 and 'Jane Notes' not in b1 and [r[0] for r in b1.get('Bass Man', [])] == ['Bass'] and stored == 'true'
                       and 'Ann Blow' in b2 and [r[0] for r in b2.get('Bass Man', [])] == ['Bass', 'backing vocals'])
        # C) the rule off in the settings, imported again
        H.open_settings(pg, 'texts')
        pg.uncheck('[data-el=settings] [data-set=rule-on][data-rule=S054]')
        pg.wait_for_timeout(300)
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        load()
        c1 = {n: rows for n, rows in pg.evaluate(GROUPS)}
        H.open_settings(pg, 'texts')
        pg.check('[data-el=settings] [data-set=rule-on][data-rule=S054]')
        pg.wait_for_timeout(300)
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        load()
        c2 = {n: rows for n, rows in pg.evaluate(GROUPS)}
        print('C) Regel aus:', sorted(c1), '| Guitar Guy:', c1.get('Guitar Guy'), '| wieder an:', 'Ann Blow' in c2)
        results.append('Ann Blow' not in c1 and 'Jane Notes' not in c1 and [r[0] for r in c1.get('Bass Man', [])] == ['Bass'] and c1.get('Guitar Guy', [[0, '']])[0][1] == '4'
                       and 'Ann Blow' in c2)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_linkedsugg():
    """Credits Importer 3.37.1 (E5a; maintainer: "wenn der name im text schon an anderer stelle im datensatz verknüpft ist mit
    musicbrainz soll der vorschlag stärker hervorgehoben werden als andere namensvorschläge", "überall"): a name searched in
    MusicBrainz (a pasted text, the Discogs notes …) whose artist MusicBrainz links to this release already – Ann Mix mixed the
    release there – has that artist first among its suggestions, highlighted (solid green, bold) and marked "in this release: mix on
    the release", before a namesake MusicBrainz's search gives first; the log says so. A name nobody in the release has: its
    suggestions as before (dashed). A label of the same name ("℗ 2001 Ann Mix") is not offered the artist."""
    ANN = H.uid('dddddddd', 92)
    H.MB_EXTRA[H.REL] = H.MB_EXTRA.get(H.REL, []) + [{'target-type': 'artist', 'type': 'mix', 'type-id': 'aaaaaaaa-0000-4000-8000-00000000mix1', 'attributes': [],
                                                       'artist': {'id': ANN, 'name': 'Ann Mix'}}]
    H.MB_SEARCH['artist'] = [{'id': H.uid('dddddddd', 90), 'name': 'Ann Mix', 'disambiguation': 'another', 'score': 100},
                             {'id': ANN, 'name': 'Ann Mix', 'disambiguation': '', 'score': 100},
                             {'id': H.uid('dddddddd', 91), 'name': 'Sax Lady', 'disambiguation': '', 'score': 100}]
    SUGG = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
  return g ? [...g.querySelectorAll('.dci-suggbtn[data-act=name-use]')].map(b => [b.dataset.mbid.slice(-2), b.classList.contains('dci-sugg-linked'), b.textContent.replace(/\\s+/g, ' ').trim(),
    getComputedStyle(b).borderTopStyle, getComputedStyle(b).fontWeight]) : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Mixed by Ann Mix\nSaxophone: Sax Lady\n℗ 2001 Ann Mix')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1500)
        d = pg.evaluate(SUGG, 'Ann Mix')
        sx = pg.evaluate(SUGG, 'Sax Lady')
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'in this release' in x]
        # the label "Ann Mix" (℗) gets no artist as its linked suggestion (after a review of 3.37.1: the kind of entry counts)
        links = pg.evaluate("[...document.querySelectorAll('.dci-suggitem')].filter(i => i.querySelector('.dci-sugg-linked')).map(i => i.querySelector('.dci-sugglink').getAttribute('href'))")
        print('Ann Mix:', d, '\nSax Lady:', sx, '\nProtokoll:', logs, '\nhervorgehoben:', links)
        results.append(bool(d) and d[0][0] == '92' and d[0][1] and 'in this release: mix on the release' in d[0][2] and d[0][3] == 'solid' and d[0][4] == '700'
                       and len(d) == 2 and d[1][0] == '90' and not d[1][1] and d[1][3] == 'dashed'
                       and sx == [['91', False, 'Sax Lady', 'dashed', '400']] and any('Ann Mix' in x and 'mix on the release' in x for x in logs)
                       and links == [f'/artist/{ANN}'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_festival():
    """Credits Importer 3.37.8: "Recorded June, 26, 1993 at the Western Front Lodge, Vancouver, B.C., Canada during the du Maurier,
    Ltd. International Jazz Festival Vancouver" as on Discogs 1565448 "Cascades" (collected item 158; maintainer: "aus "Recorded
    June, 26, 1993" wird nur 1993 als Datum ausgegeben", "aus texteinträgen kann bei freitext und dann auch discogs text zumindest
    ein hinweis ausgegeben werden …", "vielleicht dann wirklich nur bei festivals, wo der name passt und die sich im Zeitraum (Date
    period) befinden. und immer nur als angebot, nie vorbelegt.", "also brauchen wir dafür auch eine farbe").
    A) The date 1993-06-26 (until 3.37.7: 1993); the place from the notes "Western Front Lodge" (Vancouver) – without "the".
    B) Above the entries: "Festival recording: “International Jazz Festival Vancouver” (1993-06-26). MusicBrainz prefers the event
       to the place …"; offered: the event of that name whose time holds the date (1993-06-25 – 1993-07-04) – not the one of
       1994 –, nothing set (no entry of it).
    C) Its button: the event an entry, in the colour of events (plum); the button greyed out; the log says so. ⚙ Appearance has
       the colour "Event".
    D) A pasted text "Recorded live at the Montreux Jazz Festival." (no date): the hint without events; "the Royal Festival Hall"
       (a place) gives none."""
    NOTES = ('Recorded June, 26, 1993 at the Western Front Lodge, Vancouver, B.C., Canada during the du Maurier, Ltd. International Jazz Festival Vancouver.')
    E1, E2 = H.uid('fefefefe', 1), H.uid('fefefefe', 2)
    H.MB_SEARCH['event'] = [{'id': E1, 'name': 'du Maurier Ltd. International Jazz Festival Vancouver 1993', 'disambiguation': '', 'type': 'Festival',
                             'life-span': {'begin': '1993-06-25', 'end': '1993-07-04'}},
                            {'id': E2, 'name': 'International Jazz Festival Vancouver 1994', 'disambiguation': '', 'type': 'Festival',
                             'life-span': {'begin': '1994-06-24', 'end': '1994-07-03'}}]
    H.COMPANIES[1030] = ('event', E1, 'du Maurier Ltd. International Jazz Festival Vancouver 1993')
    H.lt(9001, H.uid('9e9e9e9e', 1), 'recorded at', 'event', 'recording', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release

    def rel():
        d = orig()
        d['notes'] = NOTES
        d['companies'] = [c for c in d['companies'] if c['entity_type_name'] != 'Recorded At']
        return d

    H.discogs_release = rel
    FEST = """(() => { const f = document.querySelector('.dci-festival'); return f ? { text: f.querySelector('p').textContent.replace(/\\s+/g, ' ').trim(), n: f.querySelectorAll('p').length,
      offers: [...f.querySelectorAll('[data-act=festival-add]')].map(b => [b.textContent.trim(), b.disabled]) } : null; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_for(pg, "!!document.querySelector('.dci-festival [data-act=festival-add]')", 20)
        pool = [(d['begin'], d.get('found')) for d in pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]')")]
        names = pg.evaluate("[...document.querySelectorAll('section.dci-group')].map(g => g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim())")
        print('A) Pool:', pool, '| Einträge:', names)
        results.append(pool == [({'year': 1993, 'month': 6, 'day': 26}, 'notes:0')] and any(n.startswith('PlaceWestern Front Lodge (Vancouver)') for n in names)
                       and not any('the Western' in n for n in names))
        f = pg.evaluate(FEST)
        print('B)', f)
        results.append(bool(f) and f['text'].startswith('Festival recording: “International Jazz Festival Vancouver” (1993-06-26). MusicBrainz prefers the event to the place')
                       and f['offers'] == [['+ du Maurier Ltd. International Jazz Festival Vancouver 1993 (1993-06-25 – 1993-07-04)', False]]
                       and not any('du Maurier' in n for n in names))
        pg.click('.dci-festival [data-act=festival-add]')
        H.wait_for(pg, "[...document.querySelectorAll('section.dci-group')].some(g => /du Maurier/.test(g.textContent))", 20)
        pg.wait_for_timeout(300)
        ev = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /du Maurier/.test(x.querySelector('.dci-gname').textContent));
          return g ? [g.classList.contains('dci-kind-event'), getComputedStyle(g).borderLeftColor] : null; })()""")
        f2 = pg.evaluate(FEST)
        logs = pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => li.textContent).filter(t => /Event added|Festival recording/.test(t))")
        H.open_settings(pg, 'appearance')
        kinds = pg.evaluate("[...document.querySelectorAll('[data-el=settings] [data-set=kind-color]')].map(i => [i.dataset.kind, i.value])")
        print('C) Eintrag:', ev, '| Knopf:', f2 and f2['offers'], '| Protokoll:', logs, '| Farben:', kinds)
        results.append(ev == [True, 'rgb(138, 79, 125)'] and f2 and f2['offers'][0][1] is True and any('Event added' in t for t in logs)
                       and ['event', '#8a4f7d'] in kinds)
        H.open_settings(pg)
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
        # D) a pasted text without a date
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Recorded live at the Montreux Jazz Festival.\nMixed at the Royal Festival Hall, London.')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "(() => { const f = document.querySelector('.dci-festival'); return !!f && /Montreux/.test(f.textContent); })()", 40)
        d = pg.evaluate(FEST)
        print('D)', d)
        results.append(bool(d) and d['text'] == 'Festival recording: “Montreux Jazz Festival”. MusicBrainz prefers the event to the place – the event is linked to its place. Add the event with its MBID (“Add entry manually”).'
                       and d['offers'] == [] and d['n'] == 1)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_pcperson():
    """Credits Importer 3.37.10: ℗ / © of a person Discogs lists as a label (collected item 160, S057; maintainer: "… soll der an
    anderer Stelle verknüpfte Martin Davidson auf artist ebene für die Copyrights eingetragen werden mit hinweis darauf, dass
    Discogs das als label führt und das hier ein vorschlag aus anderen Discogs relationships ist.", "primär bei treffer im release,
    ansonsten vorschläge. wenn MB ein Label gleichen namens hat muss das auch in die auswahl. dass es sich label oder artist handelt
    muss in solchen seltenen fällen erkennbar sein.").
    A) "Copyright © – Martin Davidson", "Phonographic Copyright ℗ – Martin Davidson" (Discogs label 294844, MusicBrainz has no label
       with its link) and "Producer – Martin Davidson" (Discogs artist): one entry Martin Davidson – his producer row and both ℗ / ©
       rows as an artist, each saying "Discogs lists it as a label (“Martin Davidson”) – here the artist of the same name of this
       release (Producer); a suggestion"; no label entry; the log says so.
    B) "As the label instead": both rows back in a label entry Martin Davidson.
    C) No producer credit, MusicBrainz links an artist Martin Davidson to this release: the label entry has that artist as its
       entity (an artist now), with the hint.
    D) Neither: the label entry's suggestions – the artist and the label of that name, each named as such."""
    MD_A, MD_L = H.uid('dddddddd', 293), H.uid('eeeeeeee', 294)
    mode = {'producer': True}
    orig = H.discogs_release

    def rel():
        d = orig()
        d['companies'] += [{'name': 'Martin Davidson', 'entity_type_name': 'Copyright (c)', 'id': 294844, 'catno': ''},
                           {'name': 'Martin Davidson', 'entity_type_name': 'Phonographic Copyright (p)', 'id': 294844, 'catno': ''}]
        if mode['producer']:
            d['extraartists'].append({'name': 'Martin Davidson', 'anv': '', 'role': 'Producer', 'tracks': '', 'id': 293824, 'join': ''})
        return d

    H.discogs_release = rel
    ENTRY = """(name) => [...document.querySelectorAll('section.dci-group')].filter(g => g.querySelector('.dci-gname strong').textContent.trim() === name)
      .map(g => [(g.querySelector('.dci-kind-tag') || {}).textContent, [...g.querySelectorAll('tr.dci-row')].map(r => [(r.querySelector('.dci-drole') || {}).textContent.trim(),
        ((r.querySelector('.dci-pcfrom') || {}).textContent || '').replace(/\\s+/g, ' ').trim()]),
        [...g.querySelectorAll('.dci-suggbtn[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()), g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ')])"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        for run in ('A', 'C', 'D'):
            mode['producer'] = run == 'A'
            H.MB_EXTRA.pop(H.REL, None)
            H.MB_SEARCH.pop('artist', None)
            H.MB_SEARCH.pop('label', None)
            if run == 'C':
                H.MB_EXTRA[H.REL] = [{'target-type': 'artist', 'type': 'producer', 'type-id': 'aaaaaaaa-0000-4000-8000-0000000prod', 'attributes': [],
                                      'artist': {'id': MD_A, 'name': 'Martin Davidson'}}]
            if run == 'D':
                H.MB_SEARCH['artist'] = [{'id': MD_A, 'name': 'Martin Davidson', 'disambiguation': 'producer', 'score': 100}]
                H.MB_SEARCH['label'] = [{'id': MD_L, 'name': 'Martin Davidson', 'disambiguation': '', 'score': 100}]
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            e = pg.evaluate(ENTRY, 'Martin Davidson')
            hint = 'Discogs lists it as a label (“Martin Davidson”) – here the artist of the same name of this release'
            if run == 'A':
                logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if '℗ / ©' in x]
                print('A)', e, '\n   Protokoll:', logs)
                rows = e[0][1] if len(e) == 1 else []
                results.append(len(e) == 1 and e[0][0] == 'Artist' and len(rows) == 3 and rows[0] == ['Producer', '']
                               and all(r[1].startswith(f'{hint} (Producer); a suggestion') for r in rows[1:]) and any('given to the artist' in x for x in logs))
                pg.locator('[data-act=pc-as-label]').first.click()
                pg.wait_for_timeout(500)
                e2 = pg.evaluate(ENTRY, 'Martin Davidson')
                print('B)', e2)
                results.append(len(e2) == 2 and sorted(x[0] for x in e2) == ['Artist', 'Label']
                               and [len(x[1]) for x in e2 if x[0] == 'Label'] == [2] and all(r[1] == '' for x in e2 for r in x[1]))
            elif run == 'C':
                print('C)', e)
                results.append(len(e) == 1 and len(e[0][1]) == 2 and all(r[1].startswith(hint) for r in e[0][1]) and 'Martin Davidson' in e[0][3])
            else:
                print('D)', e)
                results.append(len(e) == 1 and sorted(e[0][2]) == ['Martin Davidson (producer) – artist', 'Martin Davidson – label'] and all(r[1] == '' for r in e[0][1]))
            print('Fehler:', errs)
            results.append(not errs)
            pg.close()
            ctx.close()
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

run_cases(globals())
