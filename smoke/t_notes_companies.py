"""Discogs notes: places, ℗ / © and publishers named in the notes (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: discnotes, pcline, publishers, personpub, placesearch, facets (3.36.7), notescredits (3.37.0), linkedsugg (3.37.1), festival (3.37.8), pcperson (3.37.10) – each the former smoke/t_<case>.py, unchanged, [3.74.0] dedbox; `python3 t_notes_companies.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
H.NO_ANIM = True  # [3.77.0] (Z-FLK) reading and mapping: no transitions or animations to wait for
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
  [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.dataset.raw), ((g.querySelector('.dci-gname .dci-sub') || {}).textContent || '').trim()]))()"""
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
    2026-10-25 08:55).
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
  return g ? { roles: [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.dataset.raw), sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.dataset.mbid) } : null; }"""
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
  [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.dataset.raw), [...g.querySelectorAll('[data-act=name-use]')].map(b => b.dataset.mbid),
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
    """Credits Importer 3.31.5: a publisher's level, a publisher with a person's name (collected items 112 and 97b).
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
    114).
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
    """Credits Importer 3.36.7 (collected item 150, S053).
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
  [...g.querySelectorAll('tr.dci-row')].filter(r => !r.className.includes('dci-lv-skip')).map(r => [(r.querySelector('.dci-drole') || { dataset: { raw: '' } }).dataset.raw,
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
        # ([3.38.4] clicked in the page: with the lower footer the button may lie below the log window)
        pg.locator('tr[data-work="1"] [data-act=work-pending]').evaluate('b => b.click()')
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
  .flatMap(g => [...g.querySelectorAll('tr.dci-row')]).map(r => [(r.querySelector('.dci-drole') || { dataset: { raw: '' } }).dataset.raw, ((r.textContent.match(/(\\d+) of 13 tracks/) || [])[1] || '')])""", 'Abbey Road Studios')
        print('D) Text:', d1)
        results.append(d1 == [['Recorded At', '2']])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_notescredits():
    """Credits Importer 3.37.0 (E5, rule S054). The Discogs notes read in full:
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
  [...g.querySelectorAll('tr.dci-row')].filter(r => !r.classList.contains('dci-about-hidden')).map(r => [(r.querySelector('.dci-drole') || { dataset: { raw: '' } }).dataset.raw.trim(), (r.textContent.match(/(\\d+) of 4 tracks/) || [])[1] || '',
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
    """Credits Importer 3.37.1 (E5a): a name searched in
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
        # ([3.144.0] S242 off: the suggestions only – with it, Ann Mix is linked as in this release, noidname3144)
        pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['D023', 'S046', 'D026', 'S114', 'S155', 'S160', 'S242']))")
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
    Ltd. International Jazz Festival Vancouver" as on Discogs 1565448 "Cascades" (collected item 158).
    A) The date 1993-06-26 (until 3.37.7: 1993); the place from the notes "Western Front Lodge" (Vancouver) – without "the".
    B) Above the entries: "Festival recording: “International Jazz Festival Vancouver” (1993-06-26). MusicBrainz prefers the event
       to the place …"; offered: the event of that name whose time holds the date (1993-06-25 – 1993-07-04) – not the one of
       1994 –, nothing set (no entry of it).
    C) Its button: the event an entry, in the colour of events (plum); the log says so – from 3.85.0 (S130) the hint goes then (until
       3.84.0 the button greyed out). ⚙ Appearance has the colour "Event".
    D) A pasted text "Recorded live at the Montreux Jazz Festival." (no date): the hint without events ((3.128.0, Z-FESTCTX) its sentence quoted); "the Royal Festival Hall"
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
        # ([Z-FEV] 3.85.0, S130) the hint goes once its event is an entry (until 3.84.0 its button greyed out)
        results.append(ev == [True, 'rgb(138, 79, 125)'] and f2 is None and any('Event added' in t for t in logs)
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
        results.append(bool(d) and d['text'].replace('From:', ' From:') == 'Festival recording: “Montreux Jazz Festival”. MusicBrainz prefers the event to the place – the event is linked to its place. Add the event with its MBID (“Add entry manually”). From: “Recorded live at the Montreux Jazz Festival.”'
                       and d['offers'] == [] and d['n'] == 1)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_pcperson():
    """Credits Importer 3.37.10: ℗ / © of a person Discogs lists as a label (collected item 160, S057).
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
      .map(g => [(g.querySelector('.dci-kind-tag') || {}).textContent, [...g.querySelectorAll('tr.dci-row')].map(r => [(r.querySelector('.dci-drole') || { dataset: { raw: '' } }).dataset.raw.trim(),
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

def case_dedications():
    """Credits Importer 3.67.0 (collected item Z-DED, rule S097): dedications and tributes.
    A) The Discogs notes "Dedicated to Cecil Taylor and to my mother. Song Two is in memory of Bass Man.": Cecil Taylor (MusicBrainz has
       one artist of that name) – "dedicated to" on the release group, the row names "Dedicated to Cecil Taylor" in the Discogs notes;
       Bass Man – "dedicated to" on the work of track 2 (the sentence names its title); "my mother": nothing (no such entry).
    B) One click "⇄ tribute to": Cecil Taylor's row a tribute (release group); staged: the release group "dedicated to" Bass Man on the
       work … and the tribute to Cecil Taylor.
    C) The release's title "Odes And Meditations For Cecil Taylor" (no notes): a tribute to Cecil Taylor from the start.
    D) Rule S097 off: no such rows.
    E) (review) The page loaded again after the switch to "tribute to": the row is a tribute again (kept for this release), no
       "remembered change left out"; a change of the rules (S007 off) leaves its type as it is."""
    import json
    CT = H.uid('dddddddd', 3800)
    RG = None
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 65: ('5e2907db-49ec-4a48-9f11-dfb99d2603ff', 'tribute', 'artist', 'release_group'),
                 846: ('26131498-00e8-4136-b937-22a4be01a63d', 'dedication', 'artist', 'work')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    # (an artist MusicBrainz has – found by the search over the known ones, its entity for staging)
    H.ARTISTS[3800] = (CT, 'Cecil Taylor')
    orig_dg, orig_ws = H.discogs_release, H.ws_release
    notes = {'v': ''}
    title = {'v': None}

    def dg():
        d = orig_dg()
        d['notes'] = notes['v']
        return d

    def ws(full=False):
        d = orig_ws(full)
        if title['v']:
            d['title'] = title['v']
        return d
    H.discogs_release, H.ws_release = dg, ws
    ROWS = """[...document.querySelectorAll('[data-group] tr.dci-row')].filter(tr => tr.querySelector('.dci-ded')).map(tr => ({
      name: tr.closest('[data-group]').querySelector('.dci-gname strong').textContent.trim(), raw: tr.querySelector('.dci-drole').dataset.raw,
      level: (tr.querySelector('[data-act=level][aria-pressed=true]') || {}).dataset ? tr.querySelector('[data-act=level][aria-pressed=true]').dataset.level : null,
      type: (s => s ? s.options[s.selectedIndex].text : null)(tr.querySelector('[data-f=type]')), ded: tr.querySelector('.dci-ded').textContent.replace(/\\s+/g, ' ').trim(), row: tr.dataset.row,
      status: (tr.querySelector('.dci-status') || {}).textContent }))"""
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.entity0 && r.entity1 && [868, 65, 846].includes(r.linkTypeID)).map(r => [r.entity0.gid || r.entity0.name, r.linkTypeID, r.entity1.gid || r.entity1.name, r.entity1.entityType || r.entity0.entityType]))()"""
    results = []

    def run(off=False, toggle=False):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S083', 'S097']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(2500)
            out = {'mx': pg.evaluate("""(() => { const h = [...document.querySelectorAll('.dci-matrix [data-colhead]')].find(x => /Bass Man/.test(x.textContent)); if (!h) return null;
              return [...document.querySelectorAll(`.dci-matrix td.dci-mx-cell.dci-mx-on[data-col="${h.dataset.colhead}"]`)].map(td => Number(td.dataset.mrow.split(':')[1]) + 1); })()"""),
                   'rows': pg.evaluate(ROWS), 'log': [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'mother' in x or 'tribute to' in x or 'dedicated to' in x]}
            if toggle:
                ct = next((r for r in out['rows'] if r['name'] == 'Cecil Taylor'), None)
                if ct:
                    pg.locator(f'tr[data-row="{ct["row"]}"] [data-act=ded-toggle]').evaluate('b => b.click()')
                    pg.wait_for_timeout(500)
                out['after'] = pg.evaluate(ROWS)
                pg.click('[data-act=apply]')
                pg.wait_for_timeout(3000)
                pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
                pg.wait_for_timeout(500)
                out['staged'] = pg.evaluate(STAGED)
                # E) the page again (the same browser)
                pg.reload(); pg.add_script_tag(content=H.MAIN)
                pg.wait_for_selector('#dci-open', timeout=20000)
                H.open_dashboard(pg)
                H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
                pg.wait_for_timeout(2500)
                out['again'] = pg.evaluate(ROWS)
                out['lost'] = pg.evaluate("[...document.querySelectorAll('#dci-log li, [data-el=msgs] *')].some(e => /left out/.test(e.textContent) && /remembered/.test(e.textContent))")
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S083', 'S007']))")
                pg.evaluate("window.dispatchEvent(new StorageEvent('storage', { key: 'dci-rules-off' }))")
                pg.wait_for_timeout(800)
                out['rules'] = pg.evaluate(ROWS)
            out['errs'] = errs
            b.close()
            return out

    try:
        notes['v'] = 'Dedicated to Cecil Taylor and to my mother. Song Two is in memory of Bass Man.'
        o = run(toggle=True)
        print('A)', json.dumps(o['rows'], ensure_ascii=False), '| Matrix Bass Man:', o['mx'], '\n   log:', o['log'])
        by = {r['name']: r for r in o['rows']}
        ct = by.get('Cecil Taylor')
        results.append(ct and ct['level'] == 'release_group' and ct['type'] == 'dedicated to' and 'Dedicated to Cecil Taylor' in ct['ded'] and 'Discogs notes' in ct['ded']
                       # (Bass Man on the works level: in the works matrix – its column on track 2)
                       and o['mx'] == [2] and any(x.startswith('Bass Man: dedicated to – from “in memory of”') for x in o['log']) and not any('mother' in x for x in o['log']) and not o['errs'])
        aft = {r['name']: r for r in o['after']}
        print('B)', aft.get('Cecil Taylor'), '\n   staged:', o['staged'])
        results.append(aft.get('Cecil Taylor') and aft['Cecil Taylor']['type'] == 'tribute' and aft['Cecil Taylor']['level'] == 'release_group'
                       and any(x[1] == 65 and CT in (x[0], x[2]) for x in o['staged']) and any(x[1] == 846 for x in o['staged']) and not any(x[1] == 868 and CT in (x[0], x[2]) for x in o['staged']))
        ag = {r['name']: r for r in o['again']}
        print('E) wieder:', ag.get('Cecil Taylor'), '| verloren:', o['lost'], '| Regeln:', [r['type'] for r in o['rules']])
        results.append(ag.get('Cecil Taylor') and ag['Cecil Taylor']['type'] == 'tribute' and not o['lost'] and all(r['type'] in ('tribute', 'dedicated to') for r in o['rules']))
        notes['v'] = ''
        title['v'] = 'Odes And Meditations For Cecil Taylor'
        o2 = run()
        print('C)', o2['rows'])
        results.append(len(o2['rows']) == 1 and o2['rows'][0]['name'] == 'Cecil Taylor' and o2['rows'][0]['type'] == 'tribute' and "release's title" in o2['rows'][0]['ded'])
        o3 = run(off=True)
        print('D)', o3['rows'])
        results.append(o3['rows'] == [])
    finally:
        H.discogs_release, H.ws_release = orig_dg, orig_ws
        for i in added_lts:
            H.LTS.pop(i, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
        H.ARTISTS.pop(3800, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_dedfor():
    """Credits Importer 3.71.0 (collected item Z-DED2, rule S107): "for …" in a sentence. The notes: "This record is for Cecil Taylor.
    Song Two was composed for Ireland. Mixed for Sony. Thanks for Bass Man."
    A) Cecil Taylor: "dedicated to" on the release group (an artist MusicBrainz has once); Ireland (a country): "dedication" on the
       work of track 2 (the sentence names "Song Two"); "Mixed for Sony" (a production) and "Thanks for Bass Man": nothing.
    B) Rule S107 off: none of them."""
    import json
    CT, IE = H.uid('dddddddd', 3800), H.uid('abababab', 40)
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 846: ('26131498-00e8-4136-b937-22a4be01a63d', 'dedication', 'artist', 'work'),
                 914: (H.uid('91491491', 1), 'dedication', 'area', 'work')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.ARTISTS[3800] = (CT, 'Cecil Taylor')
    H.MB_SEARCH['area'] = [{'id': IE, 'name': 'Ireland', 'type': 'Country', 'score': 100}]
    orig, orig_js = H.discogs_release, H.js_entity
    # (the area as the editor's entity)
    H.js_entity = lambda gid: {'entityType': 'area', 'id': 4040, 'gid': IE, 'name': 'Ireland', 'comment': ''} if gid == IE else orig_js(gid)

    def dg():
        d = orig()
        d['notes'] = 'This record is for Cecil Taylor. Song Two was composed for Ireland. Mixed for Sony. Thanks for Bass Man.'
        return d
    H.discogs_release = dg
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.entity0 && r.entity1 && [868, 846, 914].includes(r.linkTypeID)).map(r => [r.entity0.gid || r.entity0.name, r.linkTypeID, r.entity1.gid || r.entity1.name]))()"""
    results = []

    def run(off=False):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S083', 'S107']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(2500)
            log = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'dedicated to' in x]
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(3000)
            pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
            pg.wait_for_timeout(500)
            staged = pg.evaluate(STAGED)
            b.close()
            return log, staged, errs

    try:
        log, staged, errs = run()
        print('A)', log, staged, errs)
        results.append(any(x[0] == CT and x[1] == 868 for x in staged) and any(x[0] == IE and x[1] == 914 and x[2] == 'Song Two' for x in staged)
                       and not any('Sony' in x or 'Bass Man' in x for x in log) and len(staged) == 2 and not errs)
        log2, staged2, _ = run(off=True)
        print('B)', log2, staged2)
        results.append(staged2 == [])
    finally:
        H.discogs_release, H.js_entity = orig, orig_js
        for i in added_lts:
            H.LTS.pop(i, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
        H.ARTISTS.pop(3800, None)
        H.MB_SEARCH.pop('area', None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_dedbox():
    """Credits Importer 3.74.0 (collected items Z-DEDQ, Z-FRM; rule S109): the box "Dedications & tributes" above the works matrix.
    Notes: "This record is for Cecil Taylor. In memory of Peter Kowald. Written for Ireland." – MusicBrainz has one Cecil Taylor, two
    entries "Peter Kowald", Ireland a country (a single word after "for": no track named).
    A) The entries, the box and the works matrix each in a narrow frame, the box between them; in it "dedicated to Cecil Taylor"
       (on the release group, added by itself); a suggestion "In memory of Peter Kowald" with both entries as buttons (the second
       "(German painter)"); a suggestion "for Ireland" ("the work of which track?"); "Create …" only at "In memory of Nobody Known"
       (MusicBrainz has none of the name: 3.124.0, Z-INMEM – until 3.123.0 nowhere in the box). C2) (3.128.0, Z-DEDBACK) a suggestion left
       out listed below the box with "↺ back", which brings it back.
    B) "Peter Kowald (German painter)": his row "dedicated to" on the release group, listed in the box, the suggestion gone.
    C) "for Ireland": the work of track 2 chosen, the MBID of the area pasted, "Add": a row of the area on the work of track 2.
    D) "＋ Dedication | Tribute" – the half "Tribute": a form; the link of Bass Man: his row "tribute to" on the release group.
       "Tribute" with the area: "MusicBrainz has no “tribute to” from area to a release group".
    E) ⚙ Settings → Appearance "Show the box …" off: the box gone (on: back). Rule S109 off: no box, no suggestions.
    (review) A2) what is typed into a suggestion stays when its kind is switched (a tribute: the level is the release group);
    "In memory of Nobody Known" (none): "leave out". F) Loaded again: the picked, the chosen and the added ones are back, what was
    left out stays out."""
    CT, PK1, PK2, IE = H.uid('dddddddd', 3800), H.uid('dddddddd', 3801), H.uid('dddddddd', 3802), H.uid('abababab', 41)
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 846: ('26131498-00e8-4136-b937-22a4be01a63d', 'dedication', 'artist', 'work'),
                 914: (H.uid('91491491', 1), 'dedication', 'area', 'work'),
                 9440: (H.uid('94409440', 1), 'tribute', 'artist', 'release_group')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.ARTISTS[3800] = (CT, 'Cecil Taylor')
    H.ARTISTS[3801] = (PK1, 'Peter Kowald')
    H.MB_SEARCH['artist'] = [{'id': PK2, 'name': 'Peter Kowald', 'disambiguation': 'German painter', 'score': 100}]
    H.MB_SEARCH['area'] = [{'id': IE, 'name': 'Ireland', 'type': 'Country', 'score': 100}]
    orig, orig_js = H.discogs_release, H.js_entity
    H.js_entity = lambda gid: ({'entityType': 'area', 'id': 4041, 'gid': IE, 'name': 'Ireland', 'comment': ''} if gid == IE
                               else {'entityType': 'artist', 'id': 3802, 'gid': PK2, 'name': 'Peter Kowald', 'comment': 'German painter'} if gid == PK2 else orig_js(gid))

    def dg():
        d = orig()
        d['notes'] = 'This record is for Cecil Taylor. In memory of Peter Kowald. Written for Ireland. In memory of Nobody Known.'
        return d
    H.discogs_release = dg
    BOX = """(() => { const b = document.querySelector('[data-el=dedbox]'); if (!b || b.hidden) return null;
      return { list: [...b.querySelectorAll('.dci-dedlist li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim()),
        sugg: [...b.querySelectorAll('.dci-dedsugg:not(.dci-dedform)')].map(x => [x.querySelector('strong').textContent.trim(), x.querySelector('.dci-sub').textContent.trim(),
          [...x.querySelectorAll('[data-act=ded-pick]')].map(y => y.textContent.replace(/\\s+/g, ' ').trim())]),
        create: [...b.querySelectorAll('.dci-dedsugg')].filter(x => x.querySelector('[data-el=ded-create]')).map(x => x.querySelector('strong').textContent.trim()), err: (b.querySelector('[data-el=ded-err]') || {}).textContent || '' }; })()"""
    FRAMES = """(() => { const f = (sel) => { const el = document.querySelector(sel); if (!el || el.hidden) return null; const cs = getComputedStyle(el);
      return [cs.borderTopWidth, cs.borderTopStyle, Math.round(el.getBoundingClientRect().top)]; };
      return [f('[data-el=entries-frame]'), f('[data-el=dedbox]'), f('[data-el=works]')]; })()"""
    results = []

    def open_page(p, off=None):
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        if off:
            H.RULES_OFF = off
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(2500)
        return pg, errs

    try:
        with sync_playwright() as p:
            pg, errs = open_page(p)
            a, fr = pg.evaluate(BOX), pg.evaluate(FRAMES)
            print('A)', a, '\n   Rahmen:', fr)
            results.append(a and any(x.startswith('dedicated to Cecil Taylor on the release group') for x in a['list'])
                           and ['“In memory of Peter Kowald”', 'several entries of exactly that name in MusicBrainz – which one? (from the Discogs notes)',
                                ['Peter Kowald', 'Peter Kowald (German painter)']] in a['sugg']
                           and any(x[0] == '“for Ireland”' and x[1].startswith('the work of which track?') and not x[2] for x in a['sugg']) and a['create'] == ['“In memory of Nobody Known”']
                           and all(x and x[0] == '1px' and x[1] == 'solid' for x in fr) and fr[0][2] < fr[1][2] < fr[2][2])
            # (review) what is typed stays when the kind is switched
            k1 = pg.evaluate("[...document.querySelectorAll('[data-el=dedbox] .dci-dedsugg')].find(x => /Ireland/.test(x.textContent)).dataset.key")
            pg.fill(f'[data-el=dedbox] [data-f=ded-mbid][data-key="{k1}"]', 'typed text')
            pg.click(f'[data-el=dedbox] [data-act=ded-sugg-kind][data-key="{k1}"][data-kind=tribute]')
            pg.wait_for_timeout(200)
            kept = [pg.input_value(f'[data-el=dedbox] [data-f=ded-mbid][data-key="{k1}"]'), pg.evaluate(f"document.querySelector('[data-el=dedbox] [data-f=ded-level][data-key=\"{k1}\"]').disabled")]
            pg.click(f'[data-el=dedbox] [data-act=ded-sugg-kind][data-key="{k1}"][data-kind=dedicated]')
            pg.wait_for_timeout(200)
            print('A2) getippt nach ⇄:', kept)
            results.append(kept == ['typed text', True])
            pg.click('[data-el=dedbox] [data-act=ded-pick]:has-text("German painter")')
            pg.wait_for_timeout(1200)
            b1 = pg.evaluate(BOX)
            print('B)', b1)
            results.append(b1 and any(x.startswith('dedicated to Peter Kowald on the release group') for x in b1['list']) and not any('Peter Kowald' in x[0] for x in b1['sugg']))
            key = k1
            pg.select_option(f'[data-el=dedbox] [data-f=ded-level][data-key="{key}"]', 'work:1')
            pg.fill(f'[data-el=dedbox] [data-f=ded-mbid][data-key="{key}"]', f'https://musicbrainz.org/area/{IE}')
            pg.click(f'[data-el=dedbox] [data-act=ded-take][data-key="{key}"]')
            pg.wait_for_timeout(1200)
            c1 = pg.evaluate(BOX)
            print('C)', c1)
            results.append(c1 and any(x.startswith('dedicated to Ireland on the work of track 2') for x in c1['list']) and [x[0] for x in c1['sugg']] == ['“In memory of Nobody Known”'])
            # (review) "leave out"
            pg.click('[data-el=dedbox] [data-act=ded-dismiss]')
            pg.wait_for_timeout(300)
            results.append(pg.evaluate(BOX)['sugg'] == [])
            # ([Z-DEDBACK] 3.128.0) listed below the box as left out – "↺ back" brings it back (until 3.127.0 it was gone for good)
            left = pg.evaluate("(document.querySelector('[data-el=ded-left]') || {}).textContent || ''")
            pg.click('[data-el=dedbox] [data-act=ded-back]')
            pg.wait_for_timeout(300)
            back = [x[0] for x in pg.evaluate(BOX)['sugg']]
            print('C2) ausgelassen:', left.strip(), '| zurück:', back)
            results.append('“In memory of Nobody Known”' in left and back == ['“In memory of Nobody Known”'])
            pg.click('[data-el=dedbox] [data-act=ded-dismiss]')
            pg.wait_for_timeout(300)
            pg.click('[data-el=dedbox] .dci-dedbox-head [data-act=ded-add][data-kind=tribute]')
            pg.wait_for_timeout(300)
            pg.fill('[data-el=dedbox] [data-f=ded-mbid][data-key=form]', f'https://musicbrainz.org/area/{IE}')
            pg.click('[data-el=dedbox] [data-act=ded-take][data-key=form]')
            pg.wait_for_timeout(800)
            d0 = pg.evaluate(BOX)['err']
            pg.fill('[data-el=dedbox] [data-f=ded-mbid][data-key=form]', f'https://musicbrainz.org/artist/{H.ARTISTS[3001][0]}')
            pg.click('[data-el=dedbox] [data-act=ded-take][data-key=form]')
            pg.wait_for_timeout(1200)
            d1 = pg.evaluate(BOX)
            print('D) Fehler:', d0, '|', d1)
            results.append(d0 == 'MusicBrainz has no “tribute to” from area to a release group' and any(x.startswith('tribute to Bass Man on the release group') for x in d1['list'])
                           and not pg.evaluate("!!document.querySelector('[data-el=dedbox] .dci-dedform')"))
            H.open_settings(pg, 'appearance')
            pg.locator('[data-el=settings] [data-set=ded-box]').evaluate('b => b.click()')
            pg.wait_for_timeout(300)
            e0 = [pg.evaluate(BOX), pg.evaluate("localStorage.getItem('dci-ded-box')")]
            pg.locator('[data-el=settings] [data-set=ded-box]').evaluate('b => b.click()')
            pg.wait_for_timeout(300)
            e1 = pg.evaluate(BOX) is not None
            print('E) aus:', e0, '| an:', e1, '| Fehler:', errs)
            results.append(e0 == [None, 'false'] and e1 and not errs)
            # F) (review) loaded again: what was picked or added by hand is back, what was left out stays out
            pg.reload()
            pg.add_script_tag(content=H.MAIN)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(2500)
            f1 = pg.evaluate(BOX)
            print('F) wieder geladen:', f1)
            results.append(f1 and len(f1['list']) == 4 and any(x.startswith('dedicated to Peter Kowald') for x in f1['list']) and any(x.startswith('dedicated to Ireland on the work of track 2') for x in f1['list'])
                           and any(x.startswith('tribute to Bass Man') for x in f1['list']) and f1['sugg'] == [])
        with sync_playwright() as p:
            pg, errs = open_page(p, off=['S083', 'S109'])
            e2 = [pg.evaluate(BOX), pg.evaluate("document.querySelector('[data-el=dedbox]').hidden")]
            print('E) S109 aus:', e2)
            results.append(e2 == [None, True])
    finally:
        H.discogs_release, H.js_entity = orig, orig_js
        for i in added_lts:
            H.LTS.pop(i, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
        for k in (3800, 3801):
            H.ARTISTS.pop(k, None)
        H.MB_SEARCH.pop('artist', None)
        H.MB_SEARCH.pop('area', None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_fev385():
    """Credits Importer 3.85.0 (collected items Z-FEV, Z-FPL, Z-EVA; rules S130 – S132): the notes of case festival ("… at the Western
    Front Lodge, Vancouver … during the du Maurier, Ltd. International Jazz Festival Vancouver"), the place Western Front Lodge linked.
    A) The festival hint above the entries, and at the linked place (S131).
    B) The event offered taken: the hint above goes (S130 – the event's name alike); at the place both named with "Place → Skip"; the
       event's row "recorded at" on the recordings at once (S132).
    C) "Place → Skip": the place's rows on Skip, the button gone.
    D) (review) It is the entry's own Skip (greyed, ↺ Take again); the event's row taken out: the hint above comes back."""
    NOTES = ('Recorded June, 26, 1993 at the Western Front Lodge, Vancouver, B.C., Canada during the du Maurier, Ltd. International Jazz Festival Vancouver.')
    E1, P1 = H.uid('fefefefe', 1), H.uid('fefefefe', 385)
    H.MB_SEARCH['event'] = [{'id': E1, 'name': 'du Maurier Ltd. International Jazz Festival Vancouver 1993', 'disambiguation': '', 'type': 'Festival',
                             'life-span': {'begin': '1993-06-25', 'end': '1993-07-04'}}]
    H.COMPANIES[1030] = ('event', E1, 'du Maurier Ltd. International Jazz Festival Vancouver 1993')
    H.COMPANIES[1033] = ('place', P1, 'Western Front Lodge')
    H.PLACE_AREAS['Western Front Lodge'] = 'Vancouver'
    H.lt(9001, H.uid('9e9e9e9e', 1), 'recorded at', 'event', 'recording', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release

    def rel():
        d = orig()
        d['notes'] = NOTES
        d['companies'] = [c for c in d['companies'] if c['entity_type_name'] != 'Recorded At']
        return d

    H.discogs_release = rel
    PLACE = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Western Front Lodge/.test(x.querySelector('.dci-gname').textContent));
      if (!g) return null; const n = g.querySelector('[data-el=fest-place]');
      return { note: n ? n.textContent.replace(/\\s+/g, ' ').trim() : '', skip: !!g.querySelector('[data-act=fest-place-skip]'),
        levels: [...g.querySelectorAll('tr.dci-row')].map(r => (r.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level || '') }; })()"""
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
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        uses = pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Western Front Lodge/.test(x.querySelector('.dci-gname').textContent)); return g ? [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()) : null; })()")
        linked = uses
        pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Western Front Lodge/.test(x.querySelector('.dci-gname').textContent)); const b = g && g.querySelector('[data-act=name-use]'); if (b) b.click(); })()")
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        a = pg.evaluate(PLACE)
        hint = pg.evaluate("!!document.querySelector('.dci-festival')")
        print('A)', linked, a, hint)
        results.append(hint and a and a['note'].startswith('Festival recording “International Jazz Festival Vancouver”') and not a['skip'])
        pg.click('.dci-festival [data-act=festival-add]')
        H.wait_for(pg, "[...document.querySelectorAll('section.dci-group')].some(g => /du Maurier/.test(g.textContent))", 20)
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        bb = pg.evaluate(PLACE)
        hint2 = pg.evaluate("!!document.querySelector('.dci-festival')")
        evrow = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /du Maurier/.test(x.querySelector('.dci-gname').textContent));
          const r = g && g.querySelector('tr.dci-row'); const t = r && r.querySelector('[data-f=type]');
          return r ? [(t && t.selectedOptions[0] || {}).text, (r.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level] : null; })()""")
        print('B)', bb, hint2, evrow)
        results.append(not hint2 and bb and bb['note'].startswith('The event “du Maurier Ltd. International Jazz Festival Vancouver 1993” is linked') and bb['skip']
                       and evrow == ['recorded at', 'recording'])
        pg.click('[data-act=fest-place-skip]')
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        c = pg.evaluate(PLACE)
        print('C)', c)
        results.append(c and c['levels'] and all(x == 'skip' for x in c['levels']) and not c['skip'])
        # D) (review) the entry's own Skip (↺ Take again); the event's row taken out: the hint above back
        took = pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Western Front Lodge/.test(x.querySelector('.dci-gname').textContent)); return !!g && g.classList.contains('dci-gskipped'); })()")
        pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /du Maurier/.test(x.querySelector('.dci-gname').textContent)); g.querySelectorAll('[data-act=remove-row]').forEach(b => b.click()); })()")
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        back = pg.evaluate("!!document.querySelector('.dci-festival')")
        print('D)', took, back)
        results.append(took and back)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def _fest388(pg_setup):
    """The release of case festival (notes with the festival), with `pg_setup(H)` before the page opens."""
    NOTES = ('Recorded June, 26, 1993 at the Western Front Lodge, Vancouver, B.C., Canada during the du Maurier, Ltd. International Jazz Festival Vancouver.')
    E1 = H.uid('fefefefe', 1)
    H.MB_SEARCH['event'] = [{'id': E1, 'name': 'du Maurier Ltd. International Jazz Festival Vancouver 1993', 'disambiguation': '', 'type': 'Festival',
                             'life-span': {'begin': '1993-06-25', 'end': '1993-07-04'}}]
    H.COMPANIES[1030] = ('event', E1, 'du Maurier Ltd. International Jazz Festival Vancouver 1993')
    H.lt(9001, H.uid('9e9e9e9e', 1), 'recorded at', 'event', 'recording', ())
    H.lt(9003, H.uid('9e9e9e9e', 3), 'video shot at', 'event', 'recording', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release

    def rel():
        d = orig()
        d['notes'] = NOTES
        d['companies'] = [c for c in d['companies'] if c['entity_type_name'] != 'Recorded At']
        return d

    H.discogs_release = rel
    pg_setup(E1)
    return E1


def case_evr388():
    """Credits Importer 3.88.0 (collected item Z-EVR, rule S137): the notes of case festival; MusicBrainz already has the festival's
    event ("du Maurier Ltd. International Jazz Festival Vancouver 1993", "recorded at").
    A) On all four recordings: no festival hint – a message where it was ("already linked"), and in the log.
    B) On tracks 1 and 2 only: the message names them, the hint (with its offer) stays for the others."""
    results = []
    for part in ([0, 1, 2, 3], [0, 1]):
        def setup(E1, part=part):
            for i in part:
                H.MB_EXTRA[H.REC[i]] = H.MB_EXTRA.get(H.REC[i], []) + [{'target-type': 'event', 'type': 'recorded at', 'type-id': H.LTS[9001]['gid'], 'attributes': [],
                                                                     'event': {'id': E1, 'name': 'du Maurier Ltd. International Jazz Festival Vancouver 1993'}}]
        _fest388(setup)
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_for(pg, "!!document.querySelector('.dci-festival')", 20)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            msg = pg.evaluate("(document.querySelector('[data-el=fest-inmb]') || {}).textContent || ''")
            hint = pg.evaluate("!!document.querySelector('.dci-festival [data-act=festival-add]')")
            logged = pg.evaluate("[...document.querySelectorAll('#dci-log li')].some(li => /MusicBrainz already has the event/.test(li.textContent))")
            print('A)' if len(part) == 4 else 'B)', msg[:120], hint, logged)
            if len(part) == 4:
                results.append('already linked with the event' in msg and not hint and logged)
            else:
                results.append('tracks 1, 2 are already linked' in msg and hint and logged)
            results.append(not errs)
            b.close()
        for i in part:
            H.MB_EXTRA[H.REC[i]] = [x for x in H.MB_EXTRA.get(H.REC[i], []) if x.get('target-type') != 'event']
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_evl388():
    """Credits Importer 3.88.0 (collected items Z-EVL, Z-FPL2; rules S136, S131): the notes of case festival, track 2 a video.
    A) The event pasted into "Add entry manually" with the role "launch event", then again without a role: its new row at once –
       "recorded at" on the recordings 1, 3, 4 and "video shot at" on 2; no question (until 3.87.0 "which relationship?"); (review)
       the row "launch event" stays.
    B) The place Western Front Lodge linked, the festival's event taken, MusicBrainz has another place for the event ("Vogue
       Theatre"): no "Place → Skip" at the place, it says the place keeps its relationship.
    C) MusicBrainz has Western Front Lodge for the event: "Place → Skip" as before.
    D) MusicBrainz has no place for the event: said so, no "Place → Skip"."""
    import common_rows as C
    results = []
    P1, P2 = H.uid('fefefefe', 385), H.uid('fefefefe', 386)

    def setup(E1):
        H.VIDEO_TRACKS.add(1)
    E1 = _fest388(setup)
    H.lt(9004, H.uid('9e9e9e9e', 4), 'launch event', 'event', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    TYPES = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname').textContent.includes(name));
      return g ? [...g.querySelectorAll('tr.dci-row')].map(r => { const t = r.querySelector('[data-f=type]'); return [(t && t.selectedOptions[0] || {}).text || '',
        (r.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level || '']; }) : null; }"""

    def open_page(p):
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        return b, pg, errs

    with sync_playwright() as p:
        H.ENTRIES_VIEW = 'legacy'
        b, pg, errs = open_page(p)
        for role in ('launch event', ''):
            pg.evaluate("document.querySelector('[data-el=manual]').hidden = false")
            pg.fill('[data-f=manual-artist]', f'https://musicbrainz.org/event/{E1}')
            pg.fill('[data-f=manual-role]', role)
            pg.click('[data-act=add-manual]')
            H.wait_for(pg, "[...document.querySelectorAll('section.dci-group')].some(x => /du Maurier/.test(x.querySelector('.dci-gname').textContent))", 20)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
        pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(x => /du Maurier/.test(x.textContent)).querySelectorAll('[data-act=row-open], [data-act=tracks-open]').forEach(b => b.click())")
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        rows = pg.evaluate(TYPES, 'du Maurier')
        tracks = C.tracks_of_rows(pg, 'du Maurier')
        ask = pg.evaluate("(() => { const q = document.querySelector('[data-el=manual-evq]'); return !!q && !q.hidden && !!q.querySelector('button'); })()")
        print('A)', rows, tracks, ask)
        results.append(rows is not None and sorted(r[0] + '|' + r[1] for r in rows) == ['launch event|release', 'recorded at|recording', 'video shot at|recording']
                       and [1, 3, 4] in tracks and [2] in tracks and not ask)
        results.append(not errs)
        b.close()
    H.COMPANIES[1033] = ('place', P1, 'Western Front Lodge')
    H.PLACE_AREAS['Western Front Lodge'] = 'Vancouver'
    PLACE = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Western Front Lodge/.test(x.querySelector('.dci-gname').textContent));
      if (!g) return null; const n = g.querySelector('[data-el=fest-place]');
      return { note: n ? n.textContent.replace(/\\s+/g, ' ').trim() : '', skip: !!g.querySelector('[data-act=fest-place-skip]') }; })()"""
    for part, places in (('B', [(P2, 'Vogue Theatre')]), ('C', [(P1, 'Western Front Lodge')]), ('D', [])):
        H.EVENT_INFO[E1] = {'name': 'du Maurier Ltd. International Jazz Festival Vancouver 1993', 'begin': '1993-06-25', 'end': '1993-07-04', 'places': places}
        with sync_playwright() as p:
            b, pg, errs = open_page(p)
            H.wait_for(pg, "!!document.querySelector('.dci-festival [data-act=festival-add]')", 20)
            pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Western Front Lodge/.test(x.querySelector('.dci-gname').textContent)); const b = g && g.querySelector('[data-act=name-use]'); if (b) b.click(); })()")
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            pg.click('.dci-festival [data-act=festival-add]')
            H.wait_for(pg, "[...document.querySelectorAll('section.dci-group')].some(g => /du Maurier/.test(g.textContent))", 20)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            x = pg.evaluate(PLACE)
            print(part + ')', x)
            if part == 'B':
                results.append(x and not x['skip'] and 'MusicBrainz has another place for it (Vogue Theatre)' in x['note'] and 'keeps its own relationship' in x['note'])
            elif part == 'C':
                results.append(x and x['skip'] and x['note'].startswith('The event “du Maurier Ltd. International Jazz Festival Vancouver 1993” is linked – MusicBrainz links'))
            else:
                results.append(x and not x['skip'] and 'has no place for it yet' in x['note'])
            results.append(not errs)
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_camd388():
    """Credits Importer 3.88.0 (collected item Z-CAMD2, rule S138): the notes of case festival as a live recording ("Recorded live June,
    26, 1993"), track 2 a video, the festival's event pasted into "Add entry manually".
    A) Its row "video shot at" (track 2) has the performance's date as a suggestion (yellow, ✓ / ✕) – not set.
    B) ✓ takes it.
    C) Rule S138 off: no suggestion."""
    results = []

    def setup(E1):
        H.VIDEO_TRACKS.add(1)
    E1 = _fest388(setup)
    fest = H.discogs_release

    def live():
        d = fest()
        d['notes'] = d['notes'].replace('Recorded June', 'Recorded live June')
        return d
    H.discogs_release = live
    SUGG = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /du Maurier/.test(x.querySelector('.dci-gname').textContent));
      if (!g) return null; const r = [...g.querySelectorAll('tr.dci-row')].find(r => { const t = r.querySelector('[data-f=type]'); return t && (t.selectedOptions[0] || {}).text === 'video shot at'; });
      if (!r) return 'no row'; const c = r.querySelector('.dci-datechip-sugg');
      return { sugg: c ? c.querySelector('.dci-datechip-text').textContent.trim() : '', title: c ? c.title : '', id: r.dataset.row }; })()"""
    for off in (False, True):
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S138']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            pg.evaluate("document.querySelector('[data-el=manual]').hidden = false")
            pg.fill('[data-f=manual-artist]', f'https://musicbrainz.org/event/{E1}')
            pg.click('[data-act=add-manual]')
            H.wait_for(pg, "[...document.querySelectorAll('section.dci-group')].some(x => /du Maurier/.test(x.querySelector('.dci-gname').textContent))", 20)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(x => /du Maurier/.test(x.textContent)).querySelectorAll('[data-act=row-open]').forEach(b => b.click())")
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            a = pg.evaluate(SUGG)
            if not off:
                print('A)', a)
                results.append(isinstance(a, dict) and '1993-06-26' in a['sugg'] and 'performance' in a['title'].lower())
                if isinstance(a, dict) and a['sugg']:
                    pg.evaluate(f'document.querySelector(\'tr[data-row="{a["id"]}"] .dci-datechip-sugg [data-act=date-take]\').click()')
                    H.wait_still(pg, "document.body.innerHTML", 10, 300)
                bb = pg.evaluate(f"""(() => {{ const r = document.querySelector('tr[data-row="{a['id'] if isinstance(a, dict) else ''}"]'); if (!r) return null;
                  return [...r.querySelectorAll('[data-f^=rd-]')].map(x => x.value).filter(Boolean).join('-') || (r.querySelector('.dci-datechip:not(.dci-datechip-sugg) .dci-datechip-text') || {{textContent: ''}}).textContent.trim(); }})()""")
                print('B)', bb)
                results.append(bool(bb) and '1993' in bb)
            else:
                print('C)', a)
                results.append(isinstance(a, dict) and a['sugg'] == '')
            results.append(not errs)
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_plt389():
    """Credits Importer 3.89.0 (collected item Z-PLT; R114, C046, S141): "Plated By – Pete Plater" (a person) and the company "Plated
    By – Plate Co" (no artist of that name in MusicBrainz).
    A) A 12" vinyl: Pete Plater miscellaneous support on the release, the task "vinyl plating"; Plate Co left out on purpose – its row on
       Skip, said at the row.
    B) A CD: Pete Plater left out (for vinyl plating – this release: CD), no entry."""
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'].append({'name': 'Pete Plater', 'anv': '', 'role': 'Plated By', 'tracks': '', 'id': 3389, 'join': ''})
        d['companies'].append({'name': 'Plate Co', 'entity_type_name': 'Plated By', 'id': 1389, 'catno': ''})
        return d
    H.discogs_release = rel
    H.lt(1131, '0b63af5e-85b2-4891-8234-bddab251399d', 'misc', 'artist', 'release', (1150,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    ROWS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname').textContent.includes(name));
      return g ? [...g.querySelectorAll('tr.dci-row')].map(r => { const t = r.querySelector('[data-f=type]'); const c = r.querySelector('[data-f=role-credit]');
        return [(t && t.selectedOptions[0] || {}).text || '', (r.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level || '',
          c ? c.value : (r.textContent.includes('vinyl plating') ? 'vinyl plating' : ''), [...r.querySelectorAll('.dci-note')].map(n => n.textContent.slice(0, 40))]; }) : null; }"""
    results = []
    for fmt in ('12" Vinyl', 'CD'):
        H.MEDIA_FORMAT = fmt
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 400)
            pg.evaluate("document.querySelectorAll('section.dci-group [data-act=row-open]').forEach(b => b.click())")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            pete, co = pg.evaluate(ROWS, 'Pete Plater'), pg.evaluate(ROWS, 'Plate Co')
            ign = pg.evaluate("[...document.querySelectorAll('.dci-ignored li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim())")
            print('A)' if fmt != 'CD' else 'B)', pete, co, [x for x in ign if 'Plat' in x], pg.evaluate("(g => g ? [g.className, g.querySelectorAll('[data-act=name-use]').length] : null)([...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname').textContent.includes('Plate Co')))"))
            if fmt != 'CD':
                results.append(pete is not None and len(pete) == 1 and pete[0][0] == 'misc' and pete[0][1] == 'release' and pete[0][2] == 'vinyl plating'
                               and co is not None and co and all(r[1] == 'skip' for r in co) and any(n.startswith('“Plated By”: MusicBrainz') for r in co for n in r[3]))
            else:
                results.append(pete is None and any('Pete Plater' in x and 'vinyl plating' in x for x in ign))
            results.append(not errs)
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_pldup3111():
    """Credits Importer 3.111.0 (collected item Z-PLDUP, S175): Discogs lists "Recorded At – Loft, Köln" and "Mixed At – Tonart Studio,
    Kerpen-Horrem" (on MusicBrainz "Tonart Studio Kerpen"); the notes: "Mixed in January 2016 at Tonart Studio." and "Recorded at
    Tonart on November 9, 2016."
    A) No entry "Tonart" or "Tonart Studio" of its own (until 3.110.0 "Tonart" – the notes' "recorded at" – searched as a new place);
       Discogs's entry has mixed at and recorded at.
    B) Its credits as the notes write it: mixed at "Tonart Studio", recorded at "Tonart".
    C) (review) "Mastered at Sterling Road Studios" of the notes is not "Mastered At – Sterling Sound" of Discogs: an entry of its own."""
    orig, comp0 = H.discogs_release, dict(H.COMPANIES)
    H.COMPANIES[277541] = ('place', H.uid('eeeeeeee', 277), 'Tonart Studio Kerpen')
    H.COMPANIES[2771] = ('place', H.uid('eeeeeeee', 278), 'Loft')

    def rel():
        d = orig()
        d['notes'] = ('Recorded November 7, 8, 2016, at Loft Köln.\nMixed in January 2016 at Tonart Studio.\nRecorded at Tonart on November 9, 2016.\n'
                      'Mastered at Sterling Road Studios.')
        d['companies'] = [{'name': 'Loft, Köln', 'entity_type_name': 'Recorded At', 'id': 2771, 'catno': ''},
                          {'name': 'Sterling Sound', 'entity_type_name': 'Mastered At', 'id': 2772, 'catno': ''},
                          {'name': 'Tonart Studio, Kerpen-Horrem', 'entity_type_name': 'Mixed At', 'id': 277541, 'catno': ''}]
        return d
    H.discogs_release = rel
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            ent = pg.evaluate("""[...document.querySelectorAll('section.dci-group')].map(g => g.querySelector('.dci-gname strong').textContent.trim()).filter(n => /Tonart|Loft|Sterling/.test(n))""")
            rows = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Tonart Studio, Kerpen/.test(x.querySelector('.dci-gname strong').textContent));
              return g ? [...g.querySelectorAll('tr.dci-row')].map(r => [(r.querySelector('.dci-drole') || {}).textContent.trim(), (r.querySelector('[data-f=credit]') || {}).value]) : null; })()""")
            print('A)', ent, '\\nB)', rows)
            results.append(sorted(ent) == ['Loft, Köln', 'Sterling Road Studios', 'Sterling Sound', 'Tonart Studio, Kerpen-Horrem'])
            results.append(bool(rows) and sorted(rows) == [['mixed at', 'Tonart Studio'], ['recorded at', 'Tonart']])
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.COMPANIES.clear()
        H.COMPANIES.update(comp0)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_dedplace3129():
    """Credits Importer 3.129.0 (collected item Z-DEDPLACE; rule S214): Discogs notes "Recorded live at Namba Bears, Osaka. Dedicated to
    ~Namba~ ~Bears~." – the tildes read as set-off words.
    A) The box "Dedications & tributes": a note that "Namba Bears" is a place of this release (no dedication to a place in MusicBrainz) –
       no suggestion "Namba Bears", nothing with a tilde; the place an entry.
    B) Rule S214 off: no such note."""
    orig, roff = H.discogs_release, H.RULES_OFF

    def dg():
        d = orig()
        d['notes'] = 'Recorded live at Namba Bears, Osaka. Dedicated to ~Namba~ ~Bears~.'
        return d
    H.discogs_release = dg
    BOX = """(() => { const b = document.querySelector('[data-el=dedbox]'); if (!b || b.hidden) return null;
      return { place: [...b.querySelectorAll('[data-el=ded-place]')].map(x => x.textContent.trim()),
        sugg: [...b.querySelectorAll('.dci-dedsugg strong')].map(x => x.textContent.trim()), text: b.textContent.replace(/\\s+/g, ' ') }; })()"""
    NAMES = "[...document.querySelectorAll('section.dci-group .dci-gname strong')].map(s => s.textContent.trim())"
    results = []

    def run(off):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            H.RULES_OFF = off
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(2500)
            r = pg.evaluate(BOX), pg.evaluate(NAMES), errs
            b.close()
            return r
    try:
        box, names, errs = run(roff)
        print('A)', box, '| Einträge:', names)
        results.append(bool(box) and len(box['place']) == 1 and 'Namba Bears' in box['place'][0] and 'place of this release' in box['place'][0]
                       and not any('Namba' in x for x in box['sugg']) and '~' not in box['text'] and 'Namba Bears' in names and not errs)
        box2, _, _ = run([*(roff or []), 'S214'])
        print('B) aus:', box2)
        results.append(not (box2 or {}).get('place'))
    finally:
        H.discogs_release = orig
        H.RULES_OFF = roff
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_lcnote3111():
    """Credits Importer 3.111.0 (collected item Z-LCNOTE, S176): Discogs gives "Label Code: LC 12345".
    A) The release's label Sony on MusicBrainz without a code: a note "… Sony has no label code on MusicBrainz", ＋ to Sony's edit page
       with ?dci-lc=12345.
    B) Sony with LC 999: "… Sony has LC 999 on MusicBrainz".
    C) Sony with LC 12345: no note.
    D) Two labels without a code, the notes "LC 12345 (Other Label)": Other Label's note; without the bracket: one note, no ＋."""
    orig, ws0, rl0 = H.discogs_release, H.ws_release, list(H.RELEASE_LABELS)
    state = {'codes': {}, 'notes': ''}

    def rel():
        d = orig()
        d['identifiers'] = [{'type': 'Label Code', 'value': 'LC 12345'}]
        if state['notes']:
            d['notes'] = state['notes']
        return d

    def ws(full=False):
        d = ws0(full)
        for li in d.get('label-info', []):
            c = state['codes'].get(li['label']['name'])
            if c:
                li['label']['label-code'] = c
        return d
    H.discogs_release, H.ws_release = rel, ws
    NOTE = """[...document.querySelectorAll('[data-el=lcnote] p')].map(p => [p.textContent.replace(/\\s+/g, ' ').trim(), (p.querySelector('.dci-lc-add') || {}).getAttribute?.('href') || ''])"""
    results = []

    def run(label, labels, codes, notes=''):
        H.RELEASE_LABELS[:] = labels
        state['codes'], state['notes'] = codes, notes
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            n = pg.evaluate(NOTE)
            print(label, n, errs)
            b.close()
            return n, errs
    try:
        sony, other = (H.uid('eeeeeeee', 1), 'Sony'), (H.uid('eeeeeeee', 9), 'Other Label')
        a, ea = run('A)', [sony], {})
        results.append(len(a) == 1 and 'LC 12345' in a[0][0] and 'Sony has no label code' in a[0][0] and a[0][1] == f'/label/{sony[0]}/edit?dci-lc=12345' and not ea)
        bb, eb = run('B)', [sony], {'Sony': 999})
        results.append(len(bb) == 1 and 'Sony has LC 999' in bb[0][0] and not eb)
        c, ec = run('C)', [sony], {'Sony': 12345})
        results.append(c == [] and not ec)
        d1, e1 = run('D1)', [sony, other], {}, 'Distributed by X. LC 12345 (Other Label)')
        d2, e2 = run('D2)', [sony, other], {})
        results.append(len(d1) == 1 and 'Other Label has no label code' in d1[0][0] and d1[0][1].startswith(f'/label/{other[0]}/edit')
                       and len(d2) == 1 and 'no label of this release' in d2[0][0] and d2[0][1] == '' and not e1 and not e2)
    finally:
        H.discogs_release, H.ws_release = orig, ws0
        H.RELEASE_LABELS[:] = rl0
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_prodfor3122():
    """Credits Importer 3.122.0 (collected item Z-PRODFOR, S191): Discogs 31535431 (Albert Ayler), "Producer [Session Originally Produced
    For VARA Radio By] – Aad Bos, Michiel De Ruyter (tracks: 3 to 4)" and "Executive Producer [For Radio Bremen] – Jane Roe".
    A) Aad Bos and Michiel De Ruyter producers on tracks 3–4, no role credit (until 3.121.0 "session originally produced for VARA
       radio by" as their credit).
    B) VARA Radio one label entry (searched by its name: MusicBrainz's "VARA" suggested) with "produced for" on the recordings 3–4 (its
       tracks known); Radio Bremen "produced for" on the release (executive)."""
    VARA = H.uid('eeeeeeee', 3122)
    H.MB_SEARCH['label'] = [{'id': VARA, 'name': 'VARA Radio', 'disambiguation': 'Dutch broadcaster', 'score': 100}]
    H.lt(950, H.uid('1a1a1a1a', 950), 'produced for', 'label', 'recording', ())
    H.lt(951, H.uid('1a1a1a1a', 951), 'produced for', 'label', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release

    def rel():
        d = orig()
        ex = lambda name, role, i, tracks='': {'name': name, 'anv': '', 'role': role, 'tracks': tracks, 'id': i, 'join': ''}
        d['extraartists'] = d['extraartists'] + [ex('Aad Bos', 'Producer [Session Originally Produced For VARA Radio By]', 3412, '3 to 4'),
                                                 ex('Michiel De Ruyter', 'Producer [Session Originally Produced For VARA Radio By]', 3413, '3 to 4'),
                                                 ex('Jane Roe', 'Executive Producer [For Radio Bremen]', 3414)]
        return d

    H.discogs_release = rel
    GROUPS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), {
  kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1] || '',
  rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); return [t ? (t.options[t.selectedIndex] || {}).text : '',
    ((tr.className.match(/dci-lv-(\\w+)/) || [])[1]) || '', (tr.querySelector('[data-f=role-credit]') || {}).value || '', (tr.dataset.tracks || '')]; }) }])))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1200)
        g = pg.evaluate(GROUPS)
        for k in ('Aad Bos', 'Michiel De Ruyter', 'Jane Roe', 'VARA Radio', 'Radio Bremen'):
            print('  ', k, g.get(k))
        tracks = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'VARA Radio');
          return g ? g.innerText.replace(/\\s+/g, ' ') : ''; })()""")
        prod = [g.get(n, {'rows': []})['rows'] for n in ('Aad Bos', 'Michiel De Ruyter')]
        results.append(all(len(r) == 1 and r[0][0] == 'producer' and r[0][2] == '' for r in prod))
        vara = g.get('VARA Radio') or {'rows': [], 'kind': ''}
        bremen = g.get('Radio Bremen') or {'rows': [], 'kind': ''}
        print('   VARA:', tracks[:300])
        results.append(vara['kind'] == 'label' and [r[:2] for r in vara['rows']] == [['produced for', 'recording']] and ('3–4' in tracks or '3-4' in tracks or '2 of 4' in tracks))
        results.append(bremen['kind'] == 'label' and [r[:2] for r in bremen['rows']] == [['produced for', 'release']])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_rsd3122():
    """Credits Importer 3.122.0 (collected item Z-RSD, S192): Discogs's format "Vinyl, LP, Limited Edition – Record Store Day".
    A) Released 2025-11-28 (Black Friday): the series "Record Store Day Black Friday 2025" of MusicBrainz linked at once, the release
       part of it (until 3.121.0 no series).
    B) Released 2025-04-12 (April): "Record Store Day 2025" at once.
    C) Released 2025-08-10: no series chosen – an entry "Record Store Day 2025" with MusicBrainz's series of that year suggested;
       "Limited Edition" gives no series."""
    BF, R25, R24 = H.uid('5e5e5e5e', 1), H.uid('5e5e5e5e', 2), H.uid('5e5e5e5e', 3)
    H.MB_SEARCH['series'] = [{'id': BF, 'name': 'Record Store Day Black Friday 2025', 'type': 'Release series', 'disambiguation': '', 'score': 100},
                             {'id': R25, 'name': 'Record Store Day 2025', 'type': 'Release series', 'disambiguation': '', 'score': 100},
                             {'id': R24, 'name': 'Record Store Day 2024', 'type': 'Release series', 'disambiguation': '', 'score': 100}]
    H.lt(741, H.uid('1a1a1a1a', 741), 'part of', 'release', 'series', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release
    when = {'d': ''}

    def rel():
        d = orig()
        d['formats'] = [{'name': 'Vinyl', 'qty': '1', 'text': 'Record Store Day', 'descriptions': ['LP', 'Album', 'Limited Edition']}]
        d['released'] = when['d']
        return d

    H.discogs_release = rel
    SER = """[...document.querySelectorAll('section.dci-group')].filter(g => /Record Store|Limited/.test(g.querySelector('.dci-gname strong').textContent)).map(g => [
      g.querySelector('.dci-gname strong').textContent.trim(), (g.querySelector('.dci-mblink') || {}).href || '', [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()),
      [...g.querySelectorAll('tr.dci-row')].map(tr => ((tr.className.match(/dci-lv-(\\w+)/) || [])[1]) || '')])"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        for run, d in (('A', '2025-11-28'), ('B', '2025-04-12'), ('C', '2025-08-10')):
            when['d'] = d
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda dl: dl.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1200)
            g = pg.evaluate(SER)
            print(f'{run})', d, g)
            if run == 'A':
                results.append(len(g) == 1 and g[0][0] == 'Record Store Day Black Friday 2025' and BF in g[0][1] and g[0][3] == ['release'])
            elif run == 'B':
                results.append(len(g) == 1 and g[0][0] == 'Record Store Day 2025' and R25 in g[0][1] and g[0][3] == ['release'])
            else:
                results.append(len(g) == 1 and g[0][0] == 'Record Store Day 2025' and not g[0][1] and any('Record Store Day 2025' in x for x in g[0][2])
                               and any('Black Friday 2025' in x for x in g[0][2]))
            print('Fehler:', errs)
            results.append(not errs)
            pg.close()
            ctx.close()
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


LJ_NOTES = """Recorded live in Berlin, Haus der Berliner Festspiele, Grosse Bühne, November 1, 2025, by Bernd Bechtold and Peter Schladebach, assisted by Henrike Zeller and Benedikt Jäger, Ulrich Hieber (Schnitt). Mixed and mastered in September 2026 by Ferran Conangla
at FCM Studios Barcelona.

℗ + © 2025 Rundfunk Berlin-Brandenburg.
Lizenz durch rbb media GmbH

Our thanks go to Nadine Deventer, the artistic director of the Jazzfest Berlin and to Peter Margasak for inviting us to present Double Trouble III on the main stage.

Thanks also to Silke Kaminski (rbb) for her help with the licensing.

And we are very grateful that underwriting support was provided by the Robert D. Bielecki Foundation.

Cover art: András Wolsky, "Random-Etude", 2025

Barry Guy plays exclusively on Thomastik-Infeld bass strings

℗ + © 2026 Maya Recordings"""

# the rows of the dashboard as the script holds them (its state through a hook of the test only)
LJ_ROWS = """() => window.__S.rows.map(r => { const a = window.__S.artists.get(r.artistKey) || {}; return { name: a.name, raw: r.raw, types: r.types || [],
  flags: [...(r.flags || [])], credit: r.roleCredit || '', primary: r.primaryText || '', level: r.level, notes: r.notes || [], area: a.area || '',
  alt: a.altNames || [], ask: r.abbrAsk ? r.abbrAsk.options : null, solo: !!(r.abbrAsk && r.abbrAsk.solo) }; })"""


def lj_discogs(notes):
    """Discogs 38896542 (London Jazz Composers Orchestra, "Double Trouble III"): its credits and companies as the page lists them."""
    orig = H.discogs_release

    def rel():
        d = orig()
        ex = lambda name, role, i: {'name': name, 'anv': '', 'role': role, 'tracks': '', 'id': i, 'join': ''}
        d['notes'] = notes
        d['companies'] = [
            {'name': 'rbb Media GmbH', 'entity_type_name': 'Licensed Through', 'id': 1101, 'catno': ''},
            {'name': 'Robert D. Bielecki Foundation', 'entity_type_name': 'Funded By', 'id': 1102, 'catno': ''},
            {'name': 'Maya Recordings', 'entity_type_name': 'Phonographic Copyright (p)', 'id': 1103, 'catno': ''},
            {'name': 'Maya Recordings', 'entity_type_name': 'Copyright (c)', 'id': 1103, 'catno': ''},
            {'name': 'Rundfunk Berlin-Brandenburg', 'entity_type_name': 'Phonographic Copyright (p)', 'id': 1104, 'catno': ''},
            {'name': 'Rundfunk Berlin-Brandenburg', 'entity_type_name': 'Copyright (c)', 'id': 1104, 'catno': ''},
            {'name': 'Haus der Berliner Festspiele', 'entity_type_name': 'Recorded At', 'id': 1105, 'catno': ''},
            {'name': 'FCM Studios', 'entity_type_name': 'Mixed At', 'id': 1106, 'catno': ''},
            {'name': 'FCM Studios', 'entity_type_name': 'Mastered At', 'id': 1106, 'catno': ''}]
        d['extraartists'] = [
            ex('Barry Guy', 'Bass, Directed By [Director]', 4001), ex('Ulrich Hieber', 'Edited By [Schnitt]', 4003),
            ex('Ferran Conangla', 'Mixed By, Mastered By', 4005), ex('John Sharpe', 'Photography By [Photo (Marilyn Crispell)]', 4006),
            ex('Camille Blake', 'Photography By [Photos]', 4007), ex('Marilyn Crispell', 'Piano [Piano Soloist], Soloist [Piano Soloist]', 4008),
            ex('Angelica Sanchez', 'Piano [Piano Soloist], Soloist [Piano Soloist]', 4009),
            ex('Bernd Bechtold', 'Recorded By', 4010), ex('Peter Schladebach', 'Recorded By', 4011),
            ex('Benedikt Jäger', 'Recorded By [Recorded By Bernd Bechtold And Peter Schladebach, Assisted By]', 4012),
            ex('Henrike Zeller', 'Recorded By [Recorded By Bernd Bechtold And Peter Schladebach, Assisted By]', 4013)]
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    return rel


def case_ljdiscogs3140():
    """Credits Importer 3.140.0: Discogs 38896542 (London Jazz Composers Orchestra, "Double Trouble III"; collected items Z-SOLOIST,
    Z-PHOTOOF, Z-ASSISTBR, Z-SCHNITT, Z-LICTHRU, Z-FUNDED, Z-PCLABEL, Z-LJTEXT; answers of 2026-11-13 10:57 – 12:28).
    A) "Piano [Piano Soloist], Soloist [Piano Soloist]": one row, piano with the attribute solo (no row "Soloist", no credit "piano soloist").
    B) "Photography By [Photo (Marilyn Crispell)]": credited "photo of Marilyn Crispell".
    C) "Recorded By [Recorded By Bernd Bechtold And Peter Schladebach, Assisted By]": recording with assistant, no role credit.
    D) "Edited By [Schnitt]": editor without the credit "schnitt".
    E) "Licensed Through – rbb Media GmbH": licensor; the notes' "Lizenz durch rbb media GmbH" joins it (one row).
    F) "Funded By – Robert D. Bielecki Foundation": credited "support" – the notes say "underwriting support was provided by …";
       without that sentence "funding".
    G) The notes' "Haus der Berliner Festspiele, Grosse Bühne": Discogs's place named "Haus der Berliner Festspiele: Grosse Bühne"
       (searched as the house too) – one entry; "“Random-Etude”" no entry.
    H) The ℗ / © dates of the notes in the date matrix: "label: Maya Recordings" (until 3.139.0 "studio: …").
    I) "Jazzfest Berlin" only in the thanks: its event found by the date of the recording (2025-11-01) – offered, said so."""
    E1 = H.uid('fefefefe', 11)
    H.MB_SEARCH['event'] = [{'id': E1, 'name': 'Jazzfest Berlin 2025', 'disambiguation': '', 'type': 'Festival', 'life-span': {'begin': '2025-10-30', 'end': '2025-11-02'}}]
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            for run, notes in (('A', LJ_NOTES), ('F2', LJ_NOTES.replace('And we are very grateful that underwriting support was provided by the Robert D. Bielecki Foundation.', ''))):
                H.discogs_release = lj_discogs(notes)
                ctx = H.new_context(b)
                pg, errs = H.open_mb_edit(ctx, companion=False)
                pg.on('dialog', lambda d: d.accept())
                pg.wait_for_selector('#dci-open', timeout=20000)
                H.open_dashboard(pg)
                H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
                pg.wait_for_timeout(1500)
                rows = pg.evaluate(LJ_ROWS)
                of = lambda n: [r for r in rows if r['name'] == n]
                fund = of('Robert D. Bielecki Foundation')
                if run == 'F2':
                    print('F) ohne den Satz:', fund)
                    results.append(len(fund) == 1 and fund[0]['credit'] == 'funding' and fund[0]['notes'] == ['fundingLabel'])
                    results.append(not errs)
                    pg.close()
                    ctx.close()
                    continue
                mc = of('Marilyn Crispell')
                print('A)', [(r['raw'], r['types'], r['flags'], r['credit'], r['primary']) for r in mc + of('Angelica Sanchez')])
                results.append(len(mc) == 1 and mc[0]['primary'] == 'piano' and mc[0]['flags'] == ['solo'] and mc[0]['credit'] == ''
                               and len(of('Angelica Sanchez')) == 1 and of('Angelica Sanchez')[0]['flags'] == ['solo'])
                js = of('John Sharpe')
                print('B)', [(r['raw'], r['credit']) for r in js])
                results.append([r['credit'] for r in js] == ['photo of Marilyn Crispell'])
                ass = of('Benedikt Jäger') + of('Henrike Zeller')
                print('C)', [(r['types'], r['flags'], r['credit']) for r in ass])
                results.append(len(ass) == 2 and all('recording' in r['types'] and r['flags'] == ['assistant'] and r['credit'] == '' for r in ass))
                uh = of('Ulrich Hieber')
                print('D)', [(r['types'], r['credit']) for r in uh])
                results.append(len(uh) == 1 and uh[0]['types'] == ['editor'] and uh[0]['credit'] == '')
                rbb = [r for r in rows if 'rbb' in r['name'].lower()]
                print('E)', [(r['name'], r['raw'], r['types']) for r in rbb])
                results.append(len(rbb) == 1 and rbb[0]['types'] == ['licensor'])
                print('F)', [(r['raw'], r['types'], r['credit'], r['level'], r['notes']) for r in fund])
                results.append(len(fund) == 1 and fund[0]['credit'] == 'support' and fund[0]['level'] == 'release' and fund[0]['types'] == [])
                haus = [r for r in rows if 'Festspiele' in r['name']]
                names = pg.evaluate("[...document.querySelectorAll('section.dci-group .dci-gname strong')].map(x => x.textContent.trim())")
                print('G)', [(r['name'], r['raw'], r['alt']) for r in haus], '| Random:', [n for n in names if 'Random' in n])
                results.append(len(haus) == 1 and haus[0]['name'] == 'Haus der Berliner Festspiele: Grosse Bühne' and 'Haus der Berliner Festspiele' in haus[0]['alt']
                               and not any('Random' in n for n in names))
                H.wait_for(pg, "!!document.querySelector('.dci-festival [data-act=festival-add]')", 20)
                fest = pg.evaluate("(() => { const f = document.querySelector('.dci-festival'); return f ? f.textContent.replace(/\\s+/g, ' ').trim() : ''; })()")
                print('I)', fest[:400])
                results.append('Jazzfest Berlin' in fest and 'Jazzfest Berlin 2025 (2025-10-30 – 2025-11-02)' in fest and 'found by the date of the recording' in fest
                               and 'only mentioned' not in fest)
                dates = pg.evaluate("[...document.querySelectorAll('.dci-tg-tag')].map(x => x.textContent.trim()).filter(t => /:/.test(t))")
                print('H)', dates)
                results.append('label: Maya Recordings' in dates and any(t.startswith('label: Rundfunk Berlin') for t in dates))
                results.append(not any(t.startswith('studio: Maya') for t in dates))
                print('Fehler:', errs)
                results.append(not errs)
                pg.close()
                ctx.close()
            b.close()
    finally:
        H.MAIN = main0
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_soloist3140():
    """Credits Importer 3.140.0 (collected item Z-SOLOIST; answer of 2026-11-13 12:28): "Soloist" without an instrument.
    A) The person has one instrument on the release ("Saxophone"): that row gets the attribute solo, no row "Soloist".
    B) Two ("Piano", "Guitar"): the row asks "“Soloist” without an instrument – which one of the person’s?" with piano and guitar;
       the answer piano: the piano row gets solo, the row of the question goes (one row less).
    C) None: a role MusicBrainz does not know, as before (miscellaneous support, its task the word)."""
    orig = H.discogs_release

    def rel():
        d = orig()
        ex = lambda name, role, i: {'name': name, 'anv': '', 'role': role, 'tracks': '', 'id': i, 'join': ''}
        d['notes'] = ''
        d['extraartists'] = [ex('Olga Organ', 'Saxophone', 5001), ex('Olga Organ', 'Soloist', 5001), ex('Pia Twokeys', 'Piano, Guitar', 5002),
                             ex('Pia Twokeys', 'Soloist', 5002), ex('Nora None', 'Soloist', 5003), ex('Nora None', 'Liner Notes', 5003)]
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1200)
            rows = pg.evaluate(LJ_ROWS)
            of = lambda n: [(r['raw'], r['primary'], r['flags'], r['ask'], r['solo'], r['types']) for r in rows if r['name'] == n]
            print('A)', of('Olga Organ'))
            results.append(of('Olga Organ') == [('Saxophone', 'saxophone', ['solo'], None, False, ['instrument'])])
            pt = of('Pia Twokeys')
            print('B)', pt)
            results.append(len(pt) == 3 and [x for x in pt if x[0] == 'Soloist'][0][3] == ['piano', 'guitar'] and [x for x in pt if x[0] == 'Soloist'][0][4])
            ask = pg.evaluate("[...document.querySelectorAll('[data-el=abbr-ask]')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())")
            print('B) Frage:', ask)
            results.append(any('“Soloist” without an instrument – which one of the person’s?' in a for a in ask))
            pg.click("[data-el=abbr-ask] [data-act=instr-pick][data-instr=piano]")
            pg.wait_for_timeout(600)
            rows = pg.evaluate(LJ_ROWS)
            pt2 = [(r['raw'], r['primary'], r['flags']) for r in rows if r['name'] == 'Pia Twokeys']
            print('B) nach der Antwort:', pt2)
            results.append(sorted(pt2) == [('Guitar', 'guitar', []), ('Piano', 'piano', ['solo'])])
            nn = of('Nora None')
            print('C)', nn)
            results.append(any(x[0] == 'Soloist' and x[5] == ['misc'] for x in nn))
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.MAIN = main0
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_ljreview3140():
    """Credits Importer 3.140.0 (review of Z-SOLOIST, Z-FUNDED, Z-LICTHRU): Discogs credits and notes.
    A) "Piano" on all tracks and "Soloist [Piano Soloist]" on track 2: the piano row without solo, the soloist's own piano row (track 2)
       with solo – not solo on every track.
    B) "Funded By – Kunststiftung NRW", the notes "Mit freundlicher Unterstützung der Kunststiftung NRW.": credited "support".
    C) The notes "Recorded by Jane Roe with the kind support of Bayerischer Rundfunk": Jane Roe still read (recording) – the sentence is
       no line of support alone.
    D) "Licensed through an agreement with Sony Music", "Lizenz: Creative Commons BY-NC-SA": no licensor.
    E) A rule switched (applyRulesChange – remapRow): the solo of B's joined row stays."""
    NOTES = """Mit freundlicher Unterstützung der Kunststiftung NRW.
Recorded by Jane Roe with the kind support of Bayerischer Rundfunk
Licensed through an agreement with Sony Music
Lizenz: Creative Commons BY-NC-SA"""
    orig = H.discogs_release

    def rel():
        d = orig()
        ex = lambda name, role, i, tr='': {'name': name, 'anv': '', 'role': role, 'tracks': tr, 'id': i, 'join': ''}
        d['notes'] = NOTES
        d['companies'] = [{'name': 'Kunststiftung NRW', 'entity_type_name': 'Funded By', 'id': 1201, 'catno': ''}]
        d['extraartists'] = [ex('Pia Solo', 'Piano', 6001), ex('Pia Solo', 'Soloist [Piano Soloist]', 6001, '2'), ex('Sam Same', 'Saxophone', 6002),
                             ex('Sam Same', 'Soloist [Saxophone Soloist]', 6002)]
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1200)
            ROWS = LJ_ROWS.replace("solo: !!(r.abbrAsk && r.abbrAsk.solo) }", "solo: !!(r.abbrAsk && r.abbrAsk.solo), tracks: [...r.tracks].sort() }")
            rows = pg.evaluate(ROWS)
            pia = sorted((r['raw'], r['flags'], r['tracks']) for r in rows if r['name'] == 'Pia Solo')
            print('A)', pia)
            results.append(pia == [('Piano', [], [0, 1, 2, 3]), ('Soloist [Piano Soloist]', ['solo'], [1])])
            kun = [(r['raw'], r['credit'], r['notes']) for r in rows if r['name'] == 'Kunststiftung NRW']
            print('B)', kun)
            results.append(kun == [('Funded By', 'support', ['supportLabel'])])
            jr = [(r['raw'], r['types']) for r in rows if r['name'] == 'Jane Roe']
            print('C)', jr)
            results.append(len(jr) == 1 and 'recording' in jr[0][1])
            lic = [(r['name'], r['raw']) for r in rows if 'Licensed' in r['raw'] or 'Creative' in (r['name'] or '') or 'agreement' in (r['name'] or '')]
            print('D)', lic)
            results.append(not lic)
            pg.click('[data-act=rules]')
            pg.wait_for_timeout(300)
            box = '#dci-rules [data-rule-on=R095]'
            pg.locator(box).first.scroll_into_view_if_needed()
            pg.locator(box).first.uncheck()
            pg.wait_for_timeout(800)
            sam = [(r['raw'], r['flags']) for r in pg.evaluate(ROWS) if r['name'] == 'Sam Same']
            print('E)', sam)
            results.append(sam == [('Saxophone', ['solo'])])
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.MAIN = main0
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
