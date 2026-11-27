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
       "live comments" on, A2's comment is "live, 1981‐05‐22: Goldsmith’s College" (since 3.153.0 the notes' spelling, S267).
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
        # [3.153.0] S267: the notes' spelling is the "credited as" of the place, and the comment takes it
        results.append(pills[0] == ['li?'] and pills[1] == ['li'] and com == ['live, 1981‐05‐22: Goldsmith’s College'])
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
    C) The release's title "Odes And Meditations For Cecil Taylor" (no notes): dedicated to Cecil Taylor from the start (3.189.0, S329;
       until then a tribute).
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
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S097']))")
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
                H.stage_click(pg, least=3000)
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
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S007']))")
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
        # ([Z-DEDTITLE] 3.189.0, S329: a dedication)
        results.append(len(o2['rows']) == 1 and o2['rows'][0]['name'] == 'Cecil Taylor' and o2['rows'][0]['type'] == 'dedicated to' and "release's title" in o2['rows'][0]['ded'])
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


def case_dedtitle3189():
    """Credits Importer 3.189.0 (collected item Z-DEDTITLE, rule S329): the release's title "Odes And Meditations For Cecil Taylor".
    A) View "by event": the entry of Cecil Taylor has the chip "dedicated to" with ▾; its list offers "⇄ tribute to"; one click:
       the row is a tribute; the list then offers "⇄ dedicated to".
    B) Rule S329 off: the title is a tribute as before."""
    import json
    CT = H.uid('dddddddd', 3800)
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 65: ('5e2907db-49ec-4a48-9f11-dfb99d2603ff', 'tribute', 'artist', 'release_group')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.ARTISTS[3800] = (CT, 'Cecil Taylor')
    orig_ws = H.ws_release

    def ws(full=False):
        d = orig_ws(full)
        d['title'] = 'Odes And Meditations For Cecil Taylor'
        return d
    H.ws_release = ws
    KIND = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Cecil Taylor/.test(x.querySelector('.dci-gname strong').textContent));
      if (!g) return null; return { chips: [...g.querySelectorAll('.dci-em-chipname')].map(x => x.textContent.trim()), q: g.querySelectorAll('.dci-em-chipq').length,
        ask: g.querySelectorAll('.dci-em-chip-ask').length, menu: [...g.querySelectorAll('.dci-em-chipmenu button')].map(x => x.textContent.trim()) }; })()"""
    results = []

    def run(off=False):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S329']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(2500)
            pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Cecil Taylor/.test(x.querySelector('.dci-gname strong').textContent)); const f = g && g.querySelector('[data-act=group-fold][aria-expanded=true]'); if (f) f.click(); })()")
            pg.wait_for_timeout(400)
            out = {'a': pg.evaluate(KIND)}
            if not off and out['a'] and out['a']['q']:
                pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Cecil Taylor/.test(x.querySelector('.dci-gname strong').textContent)); g.querySelector('.dci-em-chipq').click(); })()")
                pg.wait_for_timeout(300)
                out['open'] = pg.evaluate(KIND)
                pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Cecil Taylor/.test(x.querySelector('.dci-gname strong').textContent)); g.querySelector('.dci-em-chipmenu [data-act=ded-toggle]').click(); })()")
                pg.wait_for_timeout(500)
                out['b'] = pg.evaluate(KIND)
                pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Cecil Taylor/.test(x.querySelector('.dci-gname strong').textContent)); const q = g.querySelector('.dci-em-chipq'); if (q) q.click(); })()")
                pg.wait_for_timeout(300)
                out['open2'] = pg.evaluate(KIND)
            out['errs'] = errs
            b.close()
            return out

    try:
        H.ENTRIES_VIEW = 'matrix'
        o = run()
        print('A)', json.dumps(o, ensure_ascii=False))
        results.append(bool(o['a']) and o['a']['chips'] == ['dedicated to'] and o['a']['q'] == 1 and o['a']['ask'] == 0 and o.get('open', {}).get('menu') == ['⇄ tribute to']
                       and o['b']['chips'] == ['tribute'] and o['open2']['menu'] == ['⇄ dedicated to'] and not o['errs'])
        o2 = run(off=True)
        print('B)', json.dumps(o2, ensure_ascii=False))
        results.append(bool(o2['a']) and o2['a']['chips'] == ['tribute'] and o2['a']['q'] == 0)
    finally:
        H.ENTRIES_VIEW = 'legacy'
        H.ws_release = orig_ws
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
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S107']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(2500)
            log = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'dedicated to' in x]
            H.stage_click(pg, least=3000)
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
      return { list: [...b.querySelectorAll('.dci-dedlist li')].map(li => { const c = li.cloneNode(true); const sw = c.querySelector('.dci-dedsw');
        if (sw) sw.replaceWith(((sw.querySelector('.dci-on') || {}).dataset || {}).kind === 'tribute' ? 'tribute to' : 'dedicated to'); return c.textContent.replace(/\\s+/g, ' ').trim(); }),
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
            # ([3.173.0] F-TESTWAITS) until the box has its four lines (the lookups take longer on a busy computer), not a fixed 2.5 s
            H.wait_ok(pg, f"(() => {{ const b = ({BOX}); return !!b && b.list.length >= 4; }})()", 20)
            pg.wait_for_timeout(500)
            f1 = pg.evaluate(BOX)
            print('F) wieder geladen:', f1)
            results.append(f1 and len(f1['list']) == 4 and any(x.startswith('dedicated to Peter Kowald') for x in f1['list']) and any(x.startswith('dedicated to Ireland on the work of track 2') for x in f1['list'])
                           and any(x.startswith('tribute to Bass Man') for x in f1['list']) and f1['sugg'] == [])
        with sync_playwright() as p:
            pg, errs = open_page(p, off=['S109'])
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
            rows = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /^Tonart Studio(?:, Kerpen-Horrem)?$/.test(x.querySelector('.dci-gname strong').textContent.trim()));
              return g ? [...g.querySelectorAll('tr.dci-row')].map(r => [(r.querySelector('.dci-drole') || {}).textContent.trim(), (r.querySelector('[data-f=credit]') || {}).value]) : null; })()""")
            print('A)', ent, '\\nB)', rows)
            # ((3.212.0, S424) Discogs's place without its town: "Tonart Studio", Kerpen-Horrem its area; "Loft" alone stays as it is)
            results.append(sorted(ent) == ['Loft, Köln', 'Sterling Road Studios', 'Sterling Sound', 'Tonart Studio'])
            results.append(bool(rows) and sorted(rows) == [['mixed at', 'Tonart Studio'], ['recorded at', 'Tonart']])
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.COMPANIES.clear()
        H.COMPANIES.update(comp0)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_placedup3188():
    """Credits Importer 3.188.0 (collected items Z-PLACEDUP, Z-PLACECREDIT; rule S324): a release of two media (3 + 1 tracks). Discogs:
    "Recorded At – Alchemia (2)", "Mixed At – Hilversum, Holland" (MusicBrainz: Studio Hilversum), "Mixed At – Jazz Cellar" (the same
    place as Alchemia in MusicBrainz), "Produced For – Fundacja Słuchaj!", and "Producer [Produced For Fundacja Słuchaj] – Prod Guy";
    the notes: "CD 1 / Recorded: November 27-29, 2016 at Alchemia Club, Kraków / CD 2 / Recorded November 30, 2016 at Radio Kraków".
    A) One entry Alchemia (none "Alchemia Club"): recorded at on tracks 1–3 only, credited "Alchemia Club"; Radio Kraków on track 4.
    B) "Jazz Cellar" – the same place in MusicBrainz – is no entry of its own: its role stands at Alchemia; the log says so.
    C) One label Fundacja Słuchaj!, not two. D) "Hilversum, Holland" is credited "Hilversum"."""
    orig, comp0, media0 = H.discogs_release, dict(H.COMPANIES), H.MEDIA
    H.MEDIA = [3, 1]
    H.COMPANIES[2681] = ('place', H.uid('eeeeeeee', 2681), 'Alchemia')
    H.COMPANIES[2682] = ('place', H.uid('eeeeeeee', 2682), 'Studio Hilversum')
    H.COMPANIES[2684] = ('place', H.uid('eeeeeeee', 2681), 'Alchemia')
    H.COMPANIES[2683] = ('label', H.uid('eeeeeeee', 2683), 'Fundacja Słuchaj')
    H.ARTISTS[3395] = (H.uid('dddddddd', 3395), 'Prod Guy')

    def rel():
        d = orig()
        d['notes'] = 'CD 1\nRecorded: November 27-29, 2016 at Alchemia Club, Kraków\nCD 2\nRecorded November 30, 2016 at Radio Kraków'
        d['companies'] = [{'name': 'Alchemia (2)', 'entity_type_name': 'Recorded At', 'id': 2681, 'catno': ''},
                          {'name': 'Hilversum, Holland', 'entity_type_name': 'Mixed At', 'id': 2682, 'catno': ''},
                          {'name': 'Jazz Cellar', 'entity_type_name': 'Mixed At', 'id': 2684, 'catno': ''},
                          {'name': 'Fundacja Słuchaj!', 'entity_type_name': 'Produced For', 'id': 2683, 'catno': ''}]
        d['extraartists'] = [{'name': 'Prod Guy', 'anv': '', 'role': 'Producer [Produced For Fundacja Słuchaj]', 'tracks': '', 'id': 3395, 'join': ''}]
        return d
    H.discogs_release = rel
    ENT = """[...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
      [...g.querySelectorAll('tr.dci-row')].map(r => [(r.querySelector('.dci-drole') || { textContent: '' }).textContent.trim(), (r.querySelector('[data-f=credit]') || {}).value || '',
        (r.querySelector('[data-tcount]') || { textContent: '' }).textContent.trim(), (r.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level || ''])])"""
    results = []
    try:
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
            if pg.locator('[data-act=dm-apply]').count():
                pg.click('[data-act=dm-apply]')
                H.wait_still(pg, "document.body.innerHTML", 10, 400)
            ent = dict((n, r) for n, r in pg.evaluate(ENT))
            alch = {k: v for k, v in ent.items() if 'Alchemia' in k or 'Jazz Cellar' in k}
            print('A)', alch, '| Radio Kraków:', ent.get('Radio Kraków'))
            rec = [r for r in ent.get('Alchemia (2)', ent.get('Alchemia', [])) if r[0] == 'recorded at' and r[3] != 'skip']
            results.append(len([k for k in ent if 'Alchemia' in k]) == 1 and len(rec) == 1 and rec[0][1] == 'Alchemia Club' and rec[0][2] == '3 of 4 tracks'
                           and any(r[0] == 'recorded at' and r[2] == '1 of 4 tracks' for r in ent.get('Radio Kraków', [])))
            merged = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'is the same entry in MusicBrainz' in x]
            mast = [r for rows in alch.values() for r in rows if r[0].lower() == 'mixed at']
            print('B)', merged, mast)
            results.append('Jazz Cellar' not in ent and len(mast) == 1 and mast[0][1] == 'Jazz Cellar' and bool(merged))
            fund = [k for k in ent if 'Fundacja' in k]
            print('C)', fund)
            results.append(fund == ['Fundacja Słuchaj!'])
            hv = ent.get('Hilversum, Holland')
            print('D)', hv, '| Fehler:', errs)
            results.append(bool(hv) and hv[0][1] == 'Hilversum' and not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.MEDIA = media0
        H.COMPANIES.clear()
        H.COMPANIES.update(comp0)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_eventplace3190():
    """Credits Importer 3.190.0 (collected item Z-EVENTPLACE, rule S334): Discogs "Recorded At – Alchemia"; the recording of track 2 is
    linked to the event "Krakow Jazz Autumn 2016" in MusicBrainz.
    A) The row stands on the recordings: a question that must be answered – it names the event (its link, its date 2016-11-27), says "no place in the event" with the link to edit the event; the answers "✕ Don't link the place" and
       "Link it anyway"; the row counts as incomplete.
    B) "✕ Don't link the place": the row is left out; the log says so.
    C) The event held at Alchemia: the question says "held at this very place: Alchemia"; "Link it anyway": no question any more,
       the row stays on the recordings; the log says so.
    D) Rule S334 off: no question."""
    import json
    orig, comp0 = H.discogs_release, dict(H.COMPANIES)
    PL, EV = H.uid('eeeeeeee', 2691), H.uid('abababab', 2691)
    H.COMPANIES[2691] = ('place', PL, 'Alchemia')
    H.MB_EXTRA[H.REC[1]] = [{'target-type': 'event', 'type': 'recorded at', 'direction': 'forward', 'event': {'id': EV, 'name': 'Krakow Jazz Autumn 2016'}}]

    def rel():
        d = orig()
        d['notes'] = ''
        d['companies'] = [{'name': 'Alchemia', 'entity_type_name': 'Recorded At', 'id': 2691, 'catno': ''}]
        return d
    H.discogs_release = rel
    Q = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Alchemia/.test(x.querySelector('.dci-gname strong').textContent)); if (!g) return null;
      const q = g.querySelector('[data-el=evp-ask]'); const r = g.querySelector('tr.dci-row');
      return { level: (r.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level || '', q: q ? q.textContent.replace(/\\s+/g, ' ').trim() : null,
        links: q ? [...q.querySelectorAll('a')].map(a => a.getAttribute('href')) : [], btns: q ? [...q.querySelectorAll('button')].map(b => b.textContent.trim()) : [],
        must: document.querySelectorAll('.dci-yell-must').length }; })()"""
    LOG = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9)).filter(t => /Alchemia: (not )?linked to the recordings/.test(t))"
    results = []

    def run(places, off=False, answer='evp-skip'):
        H.EVENT_INFO[EV] = {'name': 'Krakow Jazz Autumn 2016', 'begin': '2016-11-27', 'end': '2016-11-27', 'places': places}
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S334']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 400)
            out = {'rel': pg.evaluate(Q)}
            pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Alchemia/.test(x.querySelector('.dci-gname strong').textContent)); g.querySelector('tr.dci-row [data-act=level][data-level=recording]').click(); })()")
            pg.wait_for_timeout(1500)
            out['rec'] = pg.evaluate(Q)
            out['inc'] = pg.evaluate("(document.querySelector('.dci-foot') || document.body).textContent.replace(/\\s+/g, ' ').match(/\\d+ rows? incomplete/) || []")
            if out['rec'] and out['rec']['q']:
                pg.evaluate(f"(() => {{ const g = [...document.querySelectorAll('section.dci-group')].find(x => /Alchemia/.test(x.querySelector('.dci-gname strong').textContent)); g.querySelector('[data-el=evp-ask] [data-act={answer}]').click(); }})()")
                pg.wait_for_timeout(600)
                out['after'] = pg.evaluate(Q)
            out['log'] = pg.evaluate(LOG)
            out['errs'] = errs
            b.close()
            return out
    try:
        o = run([])
        print('A)', json.dumps(o['rel'], ensure_ascii=False), '\n  ', json.dumps(o['rec'], ensure_ascii=False), o['inc'])
        r = o['rec']
        results.append(o['rel']['level'] == 'recording' and bool(o['rel']['q']) and r['level'] == 'recording' and bool(r['q']) and 'Krakow Jazz Autumn 2016 (2016-11-27)' in r['q']
                       and 'no place in the event' in r['q'] and f'/event/{EV}' in r['links'] and f'/event/{EV}/edit' in r['links']
                       and r['btns'] == ['✕ Don’t link the place', 'Link it anyway'] and r['must'] >= 1 and bool(o['inc']))
        print('B)', json.dumps(o['after'], ensure_ascii=False), o['log'])
        results.append(o['after']['level'] == 'skip' and o['after']['q'] is None and any('not linked to the recordings' in x for x in o['log']) and not o['errs'])
        o2 = run([(PL, 'Alchemia')], answer='evp-keep')
        print('C)', json.dumps(o2['rec'], ensure_ascii=False), '\n  ', json.dumps(o2['after'], ensure_ascii=False), o2['log'])
        results.append(bool(o2['rec']['q']) and 'held at this very place: Alchemia' in o2['rec']['q'] and o2['after']['level'] == 'recording' and o2['after']['q'] is None
                       and any('besides their event' in x for x in o2['log']) and not o2['errs'])
        o3 = run([], off=True)
        print('D)', json.dumps(o3['rec'], ensure_ascii=False))
        results.append(o3['rec']['level'] == 'recording' and o3['rec']['q'] is None)
    finally:
        H.discogs_release = orig
        H.MB_EXTRA.pop(H.REC[1], None)
        H.EVENT_INFO.pop(EV, None)
        H.COMPANIES.clear()
        H.COMPANIES.update(comp0)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_lclinks3190():
    """Credits Importer 3.190.0 (collected item Z-LCLINKS, rule S335): Discogs gives "Label Code: LC 12345"; the release's label Sony has
    no code in MusicBrainz. Discogs's page of the label: the links euphorium.de (MusicBrainz has it) and sony.bandcamp.com and
    sonymusic.example (it has not), "Contact Info" with "04229 Leipzig"; MusicBrainz has one city Leipzig.
    A) The note names what ＋ also fills in – the two addresses and "headquarters in Leipzig"; the ＋ opens the edit page with the code,
       "edit-label.url.0/1.text" (the own site with its link type), "rels.0.target" Leipzig, the type "headquarters", backward; the
       log says so.
    B) Two cities named Leipzig in MusicBrainz: the links only, no headquarters.
    C) Rule S335 off: the code only.
    D) In Node: the city of an address – after the postal code, before state and ZIP; two cities: none."""
    import json, subprocess
    from urllib.parse import unquote
    orig, rl0 = H.discogs_release, list(H.RELEASE_LABELS)
    sony = (H.uid('eeeeeeee', 1), 'Sony')
    LPZ = H.uid('acacacac', 1)
    H.lt(931, 'd9d5ecf4-0000-4000-8000-000000000931', 'headquarters', 'area', 'label', dates=True)
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}

    def rel():
        d = orig()
        d['identifiers'] = [{'type': 'Label Code', 'value': 'LC 12345'}]
        return d
    H.discogs_release = rel
    NOTE = """[...document.querySelectorAll('[data-el=lcnote] p')].map(p => [p.textContent.replace(/\\s+/g, ' ').trim(), (p.querySelector('.dci-lc-add') || {}).getAttribute?.('href') || '',
      (p.querySelector('[data-el=lc-extra]') || {textContent: ''}).textContent.trim()])"""
    results = []

    def run(areas, off=False):
        H.RELEASE_LABELS[:] = [sony]
        dg_id = next(k for k, v in H.COMPANIES.items() if v[1] == sony[0])
        H.DG_API[f'/labels/{dg_id}'] = {'id': dg_id, 'name': 'Sony', 'urls': ['http://www.euphorium.de', 'https://sony.bandcamp.com/', 'https://sonymusic.example/'],
                                        'contact_info': 'Sony Records\nBlümnerstr. 23\n04229 Leipzig\nGermany'}
        H.ENTITY_URLS[sony[0]] = ['https://euphorium.de/']
        H.MB_SEARCH['area'] = areas
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S335']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            n = pg.evaluate(NOTE)
            log = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'page of the label also gives' in x]
            b.close()
            return n, log, errs
    try:
        city = {'id': LPZ, 'name': 'Leipzig', 'type': 'City', 'score': 100}
        a, la, ea = run([city])
        href = unquote(a[0][1]) if a else ''
        print('A)', a[0][0] if a else a, '|', href, '|', la, ea)
        results.append(len(a) == 1 and '＋ also fills in: sony.bandcamp.com, sonymusic.example, headquarters in Leipzig' in a[0][2] and 'dci-lc=12345' in href
                       and 'edit-label.url.0.text=https://sony.bandcamp.com/' in href and 'edit-label.url.1.text=https://sonymusic.example/' in href
                       and 'edit-label.url.1.link_type_id=219' in href and 'edit-label.url.0.link_type_id' not in href and 'euphorium' not in href
                       and f'rels.0.target={LPZ}' in href and 'rels.0.type=931' in href and 'rels.0.backward=1' in href and bool(la) and not ea)
        bb, lb, eb = run([city, {'id': H.uid('acacacac', 2), 'name': 'Leipzig', 'type': 'City', 'score': 90}])
        hb = unquote(bb[0][1]) if bb else ''
        print('B)', bb[0][2] if bb else bb, '|', hb)
        results.append(len(bb) == 1 and 'headquarters' not in bb[0][2] and 'sony.bandcamp.com' in bb[0][2] and 'rels.0' not in hb and 'edit-label.url.0.text' in hb and not eb)
        c, lc, ec = run([city], off=True)
        hc = unquote(c[0][1]) if c else ''
        print('C)', c[0][2] if c else c, '|', hc)
        results.append(len(c) == 1 and c[0][2] == '' and 'dci-lc=12345' in hc and 'edit-label.url' not in hc and 'rels.0' not in hc and not lc and not ec)
        node = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
console.log(JSON.stringify(['Euphorium Records\nBlümnerstr. 23\n04229 Leipzig\nGermany', 'Label X, D-10115 Berlin, Germany', '123 Main St\nBrooklyn, NY 11201\nUSA',
  'Office: 10115 Berlin\nStudio: 04229 Leipzig', 'Tel. 0341 12345\ninfo@x.de'].map((x) => m.addressCity(x))));
"""
        o = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
        res = json.loads(o.stdout) if o.returncode == 0 else o.stderr[-300:]
        print('D)', res)
        results.append(res == ['Leipzig', 'Berlin', 'Brooklyn', '', ''])
    finally:
        H.discogs_release = orig
        H.RELEASE_LABELS[:] = rl0
        H.LTS.pop(931, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
        H.MB_SEARCH.pop('area', None)
        H.ENTITY_URLS.pop(sony[0], None)
        for k in [k for k in H.DG_API if k.startswith('/labels/')]:
            H.DG_API.pop(k)
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
        results.append(len(a) == 1 and 'LC 12345' in a[0][0] and 'Sony has no label code' in a[0][0] and a[0][1].startswith(f'/label/{sony[0]}/edit?dci-lc=12345')
                       and 'edit-label.edit_note=' in a[0][1] and 'Source' in a[0][1] and not ea)   # (3.184.0, Z-EDITNOTESRC: with the edit note)
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


def case_notesextras3163():
    """Credits Importer 3.163.0 (proposal F-NOTESRESULTS, rule S295): the Discogs notes give what every free text gives besides credits.
    Notes: "Jazz Masters Series No. 12" and "“Song Two” live at Café Oto, 12 May 2019".
    A) The log names what was taken besides the credits: the series and one live recording.
    B) The series of the notes is on the dashboard (Discogs lists none), the live recording is offered above the entries.
    C) The same notes pasted as a text give the same series and the same live recording (one function for all free texts).
    D) With S295 off the notes give neither (as until 3.162.0)."""
    NOTES = "Jazz Masters Series No. 12\n\n“Song Two” live at Café Oto, 12 May 2019"
    orig = H.discogs_release

    def rel():
        d = orig()
        d['notes'] = NOTES
        d.pop('series', None)
        return d
    H.discogs_release = rel
    SEEN = """(() => { const t = document.querySelector('#dci-overlay').textContent;
      return { series: /Jazz Masters Series/.test(t), live: !!document.querySelector('#dci-overlay [data-act=live-take]'),
        log: [...document.querySelectorAll('#dci-log li')].map(li => li.textContent).filter(x => /besides the credits/.test(x)) }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        a = pg.evaluate(SEEN)
        print('A)', a['log'])
        results.append(len(a['log']) == 1 and 'series: Jazz Masters Series' in a['log'][0] and 'live recordings named: 1' in a['log'][0])
        print('B)', a['series'], a['live'])
        results.append(a['series'] and a['live'])
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', NOTES + '\n\nProduced by Jane Roe')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        c = pg.evaluate(SEEN)
        print('C)', c['series'], c['live'])
        results.append(c['series'] and c['live'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("if (location.host === 'musicbrainz.org') localStorage.setItem('dci-rules-off', JSON.stringify(['S295']));")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        d = pg.evaluate(SEEN)
        print('D)', d)
        results.append(not d['series'] and not d['live'] and not d['log'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_tribute3206():
    """Credits Importer 3.206.0 (collected items Z-TRIBUTEWORKS, Z-DEDSEARCH; rules S401, S402): the release "We Play For Rollins"
    (as Joshua Redman, "If Ever You Would Leave Us (We Play For Rollins)"); MusicBrainz has no artist named "Rollins", but Sonny Rollins
    (composer of works titled as tracks 2 and 3; track 1 has its work), the Rollins Band (no works here) and four more of the name.
    A) The box: "“For Rollins”" offers Sonny Rollins by his works ("2 tracks …"), not the Rollins Band; a message says the name has
       many artists (6 > the 3 hits of the settings).
    B) Sonny Rollins picked: tracks 2 and 3 get his works in yellow ("work of Sonny Rollins – check"), not linked.
    C) "＋ Tribute", "Sonny" typed, Enter: MusicBrainz's artists of that name as buttons (Sonny Rollins among them).
    E) "✨ Answer all": on "careful" nothing of them; on "balanced" both linked (a work of the tribute's artist of exactly the title).
    D) S401 and S402 off: no offer (a single word after "For" is no name), a name typed gives "not a valid MBID"."""
    SR, RB = H.uid('dddddddd', 3900), H.uid('dddddddd', 3901)
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 9440: (H.uid('94409440', 1), 'tribute', 'artist', 'release_group')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.MB_SEARCH['artist'] = [{'id': SR, 'name': 'Sonny Rollins', 'disambiguation': 'jazz saxophonist', 'type': 'Person', 'score': 100},
                             {'id': RB, 'name': 'Rollins Band', 'disambiguation': '', 'type': 'Group', 'score': 100}] + [
        {'id': H.uid('dddddddd', 3910 + k), 'name': f'{n} Rollins', 'disambiguation': '', 'score': 90} for k, n in enumerate(['Ann', 'Bob', 'Cy', 'Dee'])]
    rel = lambda: [{'target-type': 'artist', 'type': 'composer', 'direction': 'backward', 'artist': {'id': SR, 'name': 'Sonny Rollins'}}]
    works0 = list(H.WORK_SEARCH)
    H.WORK_SEARCH[:] = [{'id': H.uid('3a3a3a3a', 1), 'title': H.TITLES[1], 'aliases': [], 'type': 'Song', 'relations': rel()},
                        {'id': H.uid('3a3a3a3a', 2), 'title': H.TITLES[2], 'aliases': [], 'type': 'Song', 'relations': rel()}]
    orig_ws, orig_js, orig_dg = H.ws_release, H.js_entity, H.discogs_release
    H.js_entity = lambda gid: ({'entityType': 'artist', 'id': 3900, 'gid': SR, 'name': 'Sonny Rollins', 'comment': 'jazz saxophonist'} if gid == SR else orig_js(gid))

    def ws(full=False):
        d = orig_ws(full)
        d['title'] = 'We Play For Rollins'
        return d
    H.ws_release = ws

    def dg():
        d = orig_dg()
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = dg
    BOX = """(() => { const b = document.querySelector('[data-el=dedbox]'); if (!b || b.hidden) return null;
      return { list: [...b.querySelectorAll('.dci-dedlist li')].map(li => { const c = li.cloneNode(true); const sw = c.querySelector('.dci-dedsw');
        if (sw) sw.replaceWith(((sw.querySelector('.dci-on') || {}).dataset || {}).kind === 'tribute' ? 'tribute to' : 'dedicated to'); return c.textContent.replace(/\\s+/g, ' ').trim(); }),
        sugg: [...b.querySelectorAll('.dci-dedsugg')].map(x => [((x.querySelector('strong') || {}).textContent || '').trim(), ((x.querySelector('.dci-sub') || {}).textContent || '').trim(),
          [...x.querySelectorAll('[data-act=ded-pick]')].map(y => y.textContent.replace(/\\s+/g, ' ').trim())]), err: (b.querySelector('[data-el=ded-err]') || {}).textContent || '' }; })()"""
    MSGS = "(document.querySelector('[data-el=msgs]') || {}).textContent || ''"
    TRIB = "[...document.querySelectorAll('[data-el=work-tribute]')].map(x => x.textContent.trim())"
    results = []

    def open_page(p, off=()):
        H.RULES_OFF = [*off, 'S471']  # (3.221.0) the message of the many artists stays to be read (S471 off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_ok(pg, f"(() => {{ const b = ({BOX}); return !!b && b.sugg.length >= 1; }})()", 30)
        pg.wait_for_timeout(800)
        return b, pg, errs

    try:
        with sync_playwright() as p:
            b, pg, errs = open_page(p)
            a, msgs = pg.evaluate(BOX), pg.evaluate(MSGS)
            print('A)', a, '| Meldung:', msgs[:160])
            s0 = a['sugg'][0] if a and a['sugg'] else ['', '', []]
            results.append(s0[0] == '“For Rollins”' and len(s0[2]) == 1 and s0[2][0].startswith('Sonny Rollins') and '2 tracks' in s0[2][0] and 'Rollins Band' not in ' '.join(s0[2])
                           and '“Rollins”: 6 artists in MusicBrainz' in msgs)
            pg.click('[data-el=dedbox] [data-act=ded-pick]')
            H.wait_ok(pg, f"{TRIB}.length >= 2", 30)
            t1 = pg.evaluate(TRIB)
            b1 = pg.evaluate(BOX)
            linked = pg.evaluate("[...document.querySelectorAll('[data-el=works] .dci-mx-wlist')].length")
            print('B)', t1, '| Liste:', b1['list'], '| Listen:', linked)
            results.append(len(t1) == 2 and all(x == 'cover of a work by Sonny Rollins?' for x in t1) and any(x.startswith('dedicated to Sonny Rollins') for x in b1['list']))
            # E) "✨ Answer all": "careful" leaves them, "balanced" links those of exactly the track's title
            PREV = "(() => { const p = document.querySelector('[data-el=magic-preview]'); return p ? [...p.querySelectorAll('[data-el=magic-item]')].map(x => x.textContent.trim()) : null; })()"
            pg.locator('[data-act=magic-open]').evaluate('b => b.click()')
            H.wait_for(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
            e1 = pg.evaluate(PREV)
            pg.locator('[data-act=magic-cancel]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            pg.locator('[data-act=magic-menu]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            pg.locator('[data-act=magic-level][data-level=balanced]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            if not pg.evaluate("!!document.querySelector('[data-act=magic-cancel]')"):
                pg.locator('[data-act=magic-open]').evaluate('b => b.click()')
                H.wait_for(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
            e2 = pg.evaluate(PREV)
            pg.locator('[data-act=magic-cancel]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
            print('E) careful:', e1, '| balanced:', e2)
            results.append(not any('Song Two' in x or 'Song Three' in x for x in (e1 or []))
                           and any('cover of “Song Two”' in x for x in (e2 or [])) and any('cover of “Song Three”' in x for x in (e2 or [])))  # (3.220.0, S467)
            pg.click('[data-el=dedbox] .dci-dedbox-head [data-act=ded-add][data-kind=tribute]')
            pg.wait_for_timeout(300)
            pg.fill('[data-el=dedbox] [data-f=ded-mbid][data-key=form]', 'Sonny')
            pg.press('[data-el=dedbox] [data-f=ded-mbid][data-key=form]', 'Enter')
            H.wait_ok(pg, "document.querySelectorAll('[data-el=dedbox] .dci-dedform [data-act=ded-pick]').length > 0", 20)
            c = pg.evaluate("[...document.querySelectorAll('[data-el=dedbox] .dci-dedform [data-act=ded-pick]')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())")
            print('C)', c, '| Fehler:', errs)
            results.append(any(x.startswith('Sonny Rollins') for x in c) and not errs)
            b.close()
            b, pg, errs = open_page(p, off=['S401', 'S402'])
            d = pg.evaluate(BOX)
            pg.click('[data-el=dedbox] .dci-dedbox-head [data-act=ded-add][data-kind=tribute]')
            pg.wait_for_timeout(300)
            pg.fill('[data-el=dedbox] [data-f=ded-mbid][data-key=form]', 'Sonny')
            pg.click('[data-el=dedbox] [data-act=ded-take][data-key=form]')
            pg.wait_for_timeout(600)
            d2 = pg.evaluate(BOX)
            print('D)', d, '|', d2['err'])
            results.append(d is not None and d['sugg'] == [] and d2['err'].startswith('No MBID') and not errs)
            b.close()
    finally:
        H.ws_release, H.js_entity, H.discogs_release = orig_ws, orig_js, orig_dg
        H.WORK_SEARCH[:] = works0
        H.MB_SEARCH.pop('artist', None)
        H.RULES_OFF = []
        for i in added_lts:
            H.LTS.pop(i, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_tribute3207():
    """Credits Importer 3.207.0 (collected items Z-TRIBUTETITLE, Z-TRIBUTEWORKS2, Z-DEDKINDSWITCH; S406 – S408): the release "If Ever You
    Would Leave Us (we play for Rollins)" (the name inside the closing bracket); the question "look works up for n tracks?" open (asked
    from 2 tracks on). Sonny Rollins wrote works titled as tracks 2 and 3 and recorded one titled as track 4 (a cover).
    A) The box offers Sonny Rollins (until 3.206.0 the bracket stopped it).
    B) Picked, with the question still open: his works are read all the same – tracks 2, 3 and 4 get them in yellow
       ("work of Sonny Rollins – check"), track 4 by his recording.
    C) "Dedication | Tribute" in the box: the row is a dedication (the title's "for", S329); a click on "Tribute" makes it a tribute.
    D) S406 off: no offer."""
    SR = H.uid('dddddddd', 3900)
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 9440: (H.uid('94409440', 1), 'tribute', 'artist', 'release_group')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.MB_SEARCH['artist'] = [{'id': SR, 'name': 'Sonny Rollins', 'disambiguation': 'jazz saxophonist', 'type': 'Person', 'score': 100}]
    rel = lambda: [{'target-type': 'artist', 'type': 'composer', 'direction': 'backward', 'artist': {'id': SR, 'name': 'Sonny Rollins'}}]
    works0 = list(H.WORK_SEARCH)
    W = lambda k: H.uid('3a3a3a3a', k)
    H.WORK_SEARCH[:] = [{'id': W(1), 'title': H.TITLES[1], 'aliases': [], 'type': 'Song', 'relations': rel()},
                        {'id': W(2), 'title': H.TITLES[2], 'aliases': [], 'type': 'Song', 'relations': rel()}]
    H.ARTIST_WORKS[SR] = [{'id': W(1), 'title': H.TITLES[1], 'aliases': []}, {'id': W(2), 'title': H.TITLES[2], 'aliases': []}]
    H.ARTIST_RECORDINGS[SR] = [{'title': H.TITLES[3], 'work': {'id': W(3), 'title': H.TITLES[3]}}]
    orig_ws, orig_js, orig_dg = H.ws_release, H.js_entity, H.discogs_release
    H.js_entity = lambda gid: ({'entityType': 'artist', 'id': 3900, 'gid': SR, 'name': 'Sonny Rollins', 'comment': 'jazz saxophonist'} if gid == SR else orig_js(gid))

    def ws(full=False):
        d = orig_ws(full)
        d['title'] = 'If Ever You Would Leave Us (we play for Rollins)'
        return d
    H.ws_release = ws

    def dg():
        d = orig_dg()
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = dg
    BOX = """(() => { const b = document.querySelector('[data-el=dedbox]'); if (!b || b.hidden) return null;
      return { list: [...b.querySelectorAll('.dci-dedlist li')].map(li => { const c = li.cloneNode(true); const sw = c.querySelector('.dci-dedsw');
        if (sw) sw.replaceWith(((sw.querySelector('.dci-on') || {}).dataset || {}).kind === 'tribute' ? 'tribute to' : 'dedicated to'); return c.textContent.replace(/\\s+/g, ' ').trim(); }),
        on: [...b.querySelectorAll('.dci-dedlist [data-act=ded-kind].dci-on')].map(x => x.dataset.kind),
        sugg: [...b.querySelectorAll('.dci-dedsugg')].map(x => [...x.querySelectorAll('[data-act=ded-pick]')].map(y => y.textContent.replace(/\\s+/g, ' ').trim())) }; })()"""
    TRIB = "[...document.querySelectorAll('[data-el=work-tribute]')].map(x => x.closest('[data-track], tr, .dci-mx-row, li') ? x.textContent.trim() : x.textContent.trim())"
    results = []

    def open_page(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("localStorage.setItem('dci-aw-ask', '2')")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(3000)
        return b, pg, errs

    try:
        with sync_playwright() as p:
            b, pg, errs = open_page(p)
            a = pg.evaluate(BOX)
            print('A)', a)
            results.append(bool(a) and a['sugg'] and a['sugg'][0] and a['sugg'][0][0].startswith('Sonny Rollins'))
            pg.click('[data-el=dedbox] [data-act=ded-pick]')
            H.wait_ok(pg, f"{TRIB}.length >= 3", 30)
            t = pg.evaluate(TRIB)
            ask = pg.evaluate("!!document.querySelector('[data-act=works-lookups-yes], [data-act=aw-ask-yes], [data-el=works-ask]')")
            print('B)', t, '| Frage offen:', ask)
            results.append(len(t) >= 3 and t.count('cover of a work by Sonny Rollins?') == 2 and t.count('cover of a song performed by Sonny Rollins?') == len(t) - 2)  # (3.220.0, S467)
            c0 = pg.evaluate(BOX)
            pg.click('[data-el=dedbox] [data-act=ded-kind][data-kind=tribute]')
            pg.wait_for_timeout(500)
            c1 = pg.evaluate(BOX)
            print('C)', c0['on'], '→', c1['on'], c1['list'], errs)
            results.append(c0['on'] == ['dedicated'] and c1['on'] == ['tribute'] and not errs)
            b.close()
            b, pg, errs = open_page(p, off=['S406'])
            d = pg.evaluate(BOX)
            print('D)', d)
            results.append((d is None or not d['sugg']) and not errs)
            b.close()
    finally:
        H.ws_release, H.js_entity, H.discogs_release = orig_ws, orig_js, orig_dg
        H.WORK_SEARCH[:] = works0
        H.ARTIST_WORKS.pop(SR, None)
        H.ARTIST_RECORDINGS.pop(SR, None)
        H.MB_SEARCH.pop('artist', None)
        H.RULES_OFF = []
        for i in added_lts:
            H.LTS.pop(i, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_cover3218():
    """Credits Importer 3.218.0 (collected item Z-COVERSHOW, S458): the release "If Ever You Would Leave Us (we play for Rollins)"; Sonny
    Rollins picked in the box – his works on tracks 2 and 3 in yellow; the one of track 2 taken.
    A) At track 2: "found, will be linked", "by Sonny Rollins", and "co?" offered in bold (Rollins performs nothing here).
    B) "✨ Answer all", level "balanced": the cover is one of its answers; level "careful": not (only offered).
    C) S458 off: no "by …", "co?" not in bold."""
    SR = H.uid('dddddddd', 3900)
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 9440: (H.uid('94409440', 1), 'tribute', 'artist', 'release_group')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    for k, n in [(567, 'cover'), (578, 'live')]:
        H.attr(k, n, k)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578))
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.MB_SEARCH['artist'] = [{'id': SR, 'name': 'Sonny Rollins', 'disambiguation': 'jazz saxophonist', 'type': 'Person', 'score': 100}]
    rel = lambda: [{'target-type': 'artist', 'type': 'composer', 'direction': 'backward', 'artist': {'id': SR, 'name': 'Sonny Rollins'}}]
    works0 = list(H.WORK_SEARCH)
    W = lambda k: H.uid('3a3a3a3a', k)
    H.WORK_SEARCH[:] = [{'id': W(1), 'title': H.TITLES[1], 'aliases': [], 'type': 'Song', 'relations': rel()},
                        {'id': W(2), 'title': H.TITLES[2], 'aliases': [], 'type': 'Song', 'relations': rel()}]
    H.ARTIST_WORKS[SR] = [{'id': W(1), 'title': H.TITLES[1], 'aliases': []}, {'id': W(2), 'title': H.TITLES[2], 'aliases': []}]
    H.ARTIST_RECORDINGS[SR] = [{'title': H.TITLES[3], 'work': {'id': W(3), 'title': H.TITLES[3]}}]
    orig_ws, orig_js, orig_dg = H.ws_release, H.js_entity, H.discogs_release
    H.js_entity = lambda gid: ({'entityType': 'artist', 'id': 3900, 'gid': SR, 'name': 'Sonny Rollins', 'comment': 'jazz saxophonist'} if gid == SR else orig_js(gid))

    def ws(full=False):
        d = orig_ws(full)
        d['title'] = 'If Ever You Would Leave Us (we play for Rollins)'
        return d
    H.ws_release = ws

    def dg():
        d = orig_dg()
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = dg
    BOX = """(() => { const b = document.querySelector('[data-el=dedbox]'); if (!b || b.hidden) return null;
      return { list: [...b.querySelectorAll('.dci-dedlist li')].map(li => { const c = li.cloneNode(true); const sw = c.querySelector('.dci-dedsw');
        if (sw) sw.replaceWith(((sw.querySelector('.dci-on') || {}).dataset || {}).kind === 'tribute' ? 'tribute to' : 'dedicated to'); return c.textContent.replace(/\\s+/g, ' ').trim(); }),
        on: [...b.querySelectorAll('.dci-dedlist [data-act=ded-kind].dci-on')].map(x => x.dataset.kind),
        sugg: [...b.querySelectorAll('.dci-dedsugg')].map(x => [...x.querySelectorAll('[data-act=ded-pick]')].map(y => y.textContent.replace(/\\s+/g, ' ').trim())) }; })()"""
    TRIB = "[...document.querySelectorAll('[data-el=work-tribute]')].map(x => x.closest('[data-track], tr, .dci-mx-row, li') ? x.textContent.trim() : x.textContent.trim())"
    results = []
    ROW = """(() => { const r = document.querySelector('tr[data-work="1"]'); if (!r) return null;
      const by = r.querySelector('.dci-mx-by'); const co = r.querySelector('.dci-wpill[data-attr=cover]');
      return [by ? by.textContent.trim() : '', co ? [co.textContent.trim(), co.classList.contains('dci-wstrong')] : null]; })()"""
    COVERS = "[...document.querySelectorAll('[data-el=magic-item][data-kind=cover]')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())"

    def open_page(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("localStorage.setItem('dci-aw-ask', '2'); localStorage.setItem('dci-magic-level', JSON.stringify('balanced'));")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(3000)
        pg.click('[data-el=dedbox] [data-act=ded-pick]')
        H.wait_ok(pg, "!!document.querySelector('tr[data-work=\"1\"] [data-act=work-pick]')", 30)
        pg.locator('tr[data-work="1"] [data-act=work-pick]').first.evaluate('b => b.click()')
        pg.wait_for_timeout(1500)
        if 'S458' not in off:
            H.wait_ok(pg, "!!document.querySelector('tr[data-work=\"1\"] .dci-wpill[data-attr=cover]')", 45)
        return b, pg, errs

    def magic(pg):
        pg.locator('[data-el=works] [data-act=magic-open]').first.evaluate('b => b.click()')
        pg.wait_for_timeout(800)
        got = pg.evaluate(COVERS)
        print('   Vorschau:', pg.evaluate("(document.querySelector('[data-el=magic-preview]') || {textContent: 'keine'}).textContent.replace(/\\s+/g, ' ').slice(0, 400)"))
        c = pg.locator('[data-act=magic-cancel]')
        if c.count():
            c.first.evaluate('b => b.click()')
        pg.wait_for_timeout(300)
        return got

    try:
        with sync_playwright() as p:
            b, pg, errs = open_page(p)
            a = pg.evaluate(ROW)
            print('A)', a)
            results.append(bool(a) and a[0] == 'by Sonny Rollins' and a[1] == ['co?', True])
            bal = magic(pg)
            pg.evaluate("localStorage.setItem('dci-magic-level', JSON.stringify('careful'))")
            pg.locator('[data-el=works] [data-act=magic-menu]').first.evaluate('b => b.click()')
            pg.wait_for_timeout(300)
            pg.locator('[data-act=magic-level][data-level=careful]').first.evaluate('b => b.click()')
            pg.wait_for_timeout(300)
            car = magic(pg)
            print('B) balanced:', bal, '| careful:', car)
            results.append(len(bal) == 1 and 'Sonny Rollins' in bal[0] and car == [])
            results.append(not errs)
            b.close()
            b, pg, errs = open_page(p, off=['S458'])
            c = pg.evaluate(ROW)
            print('C)', c)
            results.append(bool(c) and c[0] == '' and (c[1] is None or c[1][1] is False) and not errs)
            b.close()
    finally:
        H.ws_release, H.js_entity, H.discogs_release = orig_ws, orig_js, orig_dg
        H.WORK_SEARCH[:] = works0
        H.ARTIST_WORKS.pop(SR, None)
        H.ARTIST_RECORDINGS.pop(SR, None)
        H.MB_SEARCH.pop('artist', None)
        H.RULES_OFF = []
        for i in added_lts:
            H.LTS.pop(i, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_magicwords3220():
    """Credits Importer 3.220.0 (collected item Z-MAGICWORDS, S467): as cover3218, but track 2's work not taken by hand: "✨ Answer all",
    level "balanced".
    A) Tracks 2 and 3 (his works) under the heading "Covers of works by Sonny Rollins (2)", track 4 (a song he recorded) under "Covers of
       songs performed by Sonny Rollins (1)"; each one answer "cover of “Song Two”" (linked and cover); the yellow tag at track 2 asks
       "cover of a work by Sonny Rollins?".
    B) The word "cover" of track 2 clicked: struck through (aria-pressed false, focus kept); "Answer these": "Song Two" planned at track 2,
       no cover on it; track 3 linked with "cover" on.
    C) S467 off: the answer as until 3.219.0 (no heading of its reason, no cover button)."""
    SR = H.uid('dddddddd', 3900)
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 9440: (H.uid('94409440', 1), 'tribute', 'artist', 'release_group')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    for k, n in [(567, 'cover'), (578, 'live')]:
        H.attr(k, n, k)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578))
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.MB_SEARCH['artist'] = [{'id': SR, 'name': 'Sonny Rollins', 'disambiguation': 'jazz saxophonist', 'type': 'Person', 'score': 100}]
    rel = lambda: [{'target-type': 'artist', 'type': 'composer', 'direction': 'backward', 'artist': {'id': SR, 'name': 'Sonny Rollins'}}]
    works0 = list(H.WORK_SEARCH)
    W = lambda k: H.uid('3a3a3a3a', k)
    H.WORK_SEARCH[:] = [{'id': W(1), 'title': H.TITLES[1], 'aliases': [], 'type': 'Song', 'relations': rel()},
                        {'id': W(2), 'title': H.TITLES[2], 'aliases': [], 'type': 'Song', 'relations': rel()}]
    H.ARTIST_WORKS[SR] = [{'id': W(1), 'title': H.TITLES[1], 'aliases': []}, {'id': W(2), 'title': H.TITLES[2], 'aliases': []}]
    H.ARTIST_RECORDINGS[SR] = [{'title': H.TITLES[3], 'work': {'id': W(3), 'title': H.TITLES[3]}}]
    orig_ws, orig_js, orig_dg = H.ws_release, H.js_entity, H.discogs_release
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    H.js_entity = lambda gid: ({'entityType': 'artist', 'id': 3900, 'gid': SR, 'name': 'Sonny Rollins', 'comment': 'jazz saxophonist'} if gid == SR else orig_js(gid))

    def ws(full=False):
        d = orig_ws(full)
        d['title'] = 'If Ever You Would Leave Us (we play for Rollins)'
        return d
    H.ws_release = ws

    def dg():
        d = orig_dg()
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = dg
    BOX = """(() => { const b = document.querySelector('[data-el=dedbox]'); if (!b || b.hidden) return null;
      return { list: [...b.querySelectorAll('.dci-dedlist li')].map(li => { const c = li.cloneNode(true); const sw = c.querySelector('.dci-dedsw');
        if (sw) sw.replaceWith(((sw.querySelector('.dci-on') || {}).dataset || {}).kind === 'tribute' ? 'tribute to' : 'dedicated to'); return c.textContent.replace(/\\s+/g, ' ').trim(); }),
        on: [...b.querySelectorAll('.dci-dedlist [data-act=ded-kind].dci-on')].map(x => x.dataset.kind),
        sugg: [...b.querySelectorAll('.dci-dedsugg')].map(x => [...x.querySelectorAll('[data-act=ded-pick]')].map(y => y.textContent.replace(/\\s+/g, ' ').trim())) }; })()"""
    TRIB = "[...document.querySelectorAll('[data-el=work-tribute]')].map(x => x.closest('[data-track], tr, .dci-mx-row, li') ? x.textContent.trim() : x.textContent.trim())"
    results = []
    ROW = """(() => { const r = document.querySelector('tr[data-work="1"]'); if (!r) return null;
      const by = r.querySelector('.dci-mx-by'); const co = r.querySelector('.dci-wpill[data-attr=cover]');
      return [by ? by.textContent.trim() : '', co ? [co.textContent.trim(), co.classList.contains('dci-wstrong')] : null]; })()"""
    COVERS = "[...document.querySelectorAll('[data-el=magic-item][data-kind=cover]')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())"

    def open_page(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("localStorage.setItem('dci-aw-ask', '0'); localStorage.setItem('dci-magic-level', JSON.stringify('balanced'));")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(3000)
        pg.click('[data-el=dedbox] [data-act=ded-pick]')
        H.wait_ok(pg, "!!document.querySelector('tr[data-work=\"1\"] [data-act=work-pick]')", 30)
        pg.wait_for_timeout(1500)
        return b, pg, errs

    def magic(pg):
        pg.locator('[data-el=works] [data-act=magic-open]').first.evaluate('b => b.click()')
        pg.wait_for_timeout(800)
        got = pg.evaluate(COVERS)
        print('   Vorschau:', pg.evaluate("(document.querySelector('[data-el=magic-preview]') || {textContent: 'keine'}).textContent.replace(/\\s+/g, ' ').slice(0, 400)"))
        c = pg.locator('[data-act=magic-cancel]')
        if c.count():
            c.first.evaluate('b => b.click()')
        pg.wait_for_timeout(300)
        return got

    try:
        with sync_playwright() as p:
            b, pg, errs = open_page(p)
            H.wait_ok(pg, "window.__S.workSearch.size >= 2 && [...window.__S.workSearch.values()].every(v => ['done', 'noWriters'].includes(v.state))", 40)
            tag = pg.evaluate("[...document.querySelectorAll('tr[data-work=\"1\"] [data-el=work-tribute], tr[data-work=\"1\"] .dci-wtribute')].map(x => x.textContent.trim() + ' | ' + (x.title || ''))")
            pg.locator('[data-el=works] [data-act=magic-open]').first.evaluate('b => b.click()')
            H.wait_ok(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
            prev = pg.evaluate("(document.querySelector('[data-el=magic-preview]') || {textContent: ''}).textContent.replace(/\\s+/g, ' ').trim()")
            heads = pg.evaluate("[...document.querySelectorAll('[data-el=magic-preview] .dci-mx-magicgroup')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())")
            items = pg.evaluate("[...document.querySelectorAll('[data-el=magic-item]')].map(x => [x.dataset.kind, x.textContent.replace(/\\s+/g, ' ').replace(/\\s*↗/g, '').trim()])")
            print('A)', heads, items, '| Tag:', tag)
            print('   Vorschau:', prev[:400])
            two = [t for k, t in items if '1.2' in t]
            results.append(two == ['1.2 – cover of “Song Two”'] and len(heads) == 2 and heads[0].startswith('Covers of works by Sonny Rollins (2) 1.2')
                           and heads[1].startswith('Covers of songs performed by Sonny Rollins (1) 1.4') and tag == ['cover of a work by Sonny Rollins? | '])
            btn = pg.locator('[data-act=magic-nocover]')
            n = btn.count()
            if n:
                btn.first.evaluate('b => b.click()')
                pg.wait_for_timeout(300)
            st = pg.evaluate("(() => { const x = document.querySelector('[data-act=magic-nocover]'); return x ? [x.classList.contains('dci-struck'), x.getAttribute('aria-pressed'), document.activeElement === x] : null; })()")
            pg.locator('[data-act=magic-apply]').first.evaluate('b => b.click()')
            pg.wait_for_timeout(2500)
            row = pg.evaluate("""(() => { const r = [...document.querySelectorAll('.dci-matrix tr[data-work="1"]')]; return [r.some(tr => tr.textContent.includes('Song Two') && !!tr.querySelector('[data-act=work-unplan]')),
              r.some(tr => { const c = tr.querySelector('.dci-wpill[data-attr=cover]'); return c && (c.getAttribute('aria-pressed') === 'true' || c.classList.contains('dci-on')); })]; })()""")
            pills = pg.evaluate("[1, 2].map(k => [...document.querySelectorAll(`.dci-matrix tr[data-work='${k}'] .dci-wpill[data-attr=cover]`)].map(x => [x.textContent.trim(), x.className, x.getAttribute('aria-pressed')]))")
            print('B)', n, st, row, errs, pills)
            results.append(n >= 1 and st == [True, 'false', True] and row == [True, False] and pills[0][0][2] == 'false' and pills[1][0][2] == 'true' and not errs)
            b.close()
            b, pg, errs = open_page(p, off=['S467'])
            pg.locator('[data-el=works] [data-act=magic-open]').first.evaluate('b => b.click()')
            H.wait_ok(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
            heads2 = pg.evaluate("document.querySelectorAll('[data-el=magic-preview] .dci-mx-magicgroup').length")
            btn2 = pg.locator('[data-act=magic-nocover]').count()
            print('C)', heads2, btn2, pg.evaluate("[...document.querySelectorAll('[data-el=magic-item]')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())"))
            results.append(heads2 == 0 and btn2 == 0 and not errs)
            b.close()
    finally:
        H.ws_release, H.js_entity, H.discogs_release = orig_ws, orig_js, orig_dg
        H.MAIN = main0
        H.WORK_SEARCH[:] = works0
        H.ARTIST_WORKS.pop(SR, None)
        H.ARTIST_RECORDINGS.pop(SR, None)
        H.MB_SEARCH.pop('artist', None)
        H.RULES_OFF = []
        for i in added_lts:
            H.LTS.pop(i, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_pcyear3220():
    """Credits Importer 3.220.0 (collected item Z-PCYEARSUPP, S470): Discogs notes "Blue Note Records, ℗ © 2026 Creative Control Corp. under
    exclusive license to UMG Recordings, Inc." on a release of Blue Note Records (MusicBrainz's label).
    A) Creative Control Corp. ℗ and © (no line "℗" left out alone as signs without a name), UMG Recordings, Inc. licensed to – one entry, not "Inc";
       no entry "Blue Note Records".
    B) The rule off (as 3.219.0): not so.
    C) The way it was seen: the release imported without that line, Discogs release 39123408 typed as "+ Source" with the line in its notes:
       its ℗/© year 2026 is offered in the date pool ("℗/© year in the notes of Discogs 2026"; S478 off); off: not.
    D) (3.221.0, S478) the same way with S478: the year 2026 placed in the column ℗/© of the date matrix."""
    orig = H.discogs_release
    NOTES = 'Blue Note Records, ℗ © 2026 Creative Control Corp. under exclusive license to UMG Recordings, Inc.\n'

    def rel():
        d = orig()
        d['notes'] = NOTES
        d['companies'] = []
        return d
    main0, labels0 = H.MAIN, H.RELEASE_LABELS
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    H.RELEASE_LABELS = [(H.uid('eeeeeeee', 77), 'Blue Note Records', 'B0001')]
    ROWS = """() => window.__S.rows.map(r => [(window.__S.artists.get(r.artistKey) || {}).name, (r.types || []).join('|'), r.date ? [r.date.by, r.date.ey].join('/') : '', r.level])"""

    def supp(p, off=('S478',)):
        H.RULES_OFF = list(off)
        H.discogs_release = orig
        other = orig()
        other.update({'id': 39123408, 'notes': NOTES, 'companies': [], 'uri': 'https://www.discogs.com/release/39123408'})
        H.DG_API['/releases/39123408'] = other
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        before = pg.evaluate("(window.__S.dateSuggestions || []).map(x => x.begin.year)")
        H.open_supp(pg)
        pg.fill('[data-f=supp-url]', 'https://www.discogs.com/release/39123408')
        pg.click('[data-act=supp-url]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Added source: Discogs/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
        sugg = pg.evaluate("[...document.querySelectorAll('[data-act=pool-suggest]')].map(b => b.textContent.trim())")
        sugg += pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9)).filter(x => /column ℗\\/©/.test(x))")
        b.close()
        H.DG_API.pop('/releases/39123408', None)
        H.discogs_release = rel
        return before, sugg, errs

    def run(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
        rows = pg.evaluate(ROWS)
        ign = pg.evaluate("JSON.stringify((window.__S.release || {}).ignored || [])")
        b.close()
        return rows, ign, errs
    results = []
    H.discogs_release = rel
    try:
        with sync_playwright() as p:
            rows, ign, errs = run(p)
            names = sorted({r[0] for r in rows})
            cc = [r for r in rows if r[0] == 'Creative Control Corp.' or r[0] == 'Creative Control Corp']
            print('A)', cc, [r for r in rows if 'UMG' in r[0]], names, ign.count('copyrightYear'), errs)
            results.append(any('phonographic copyright' in r[1] for r in cc) and any(r[1] == 'copyright' for r in cc)
                           and any(r[0] == 'UMG Recordings, Inc' or r[0] == 'UMG Recordings, Inc.' for r in rows) and 'Inc' not in names
                           and 'Blue Note Records' not in names and not ign.count('copyrightYear') and not errs)
            rows2, ign2, errs2 = run(p, off=['S470'])
            names2 = sorted({r[0] for r in rows2})
            print('B)', names2, ign2.count('copyrightYear'))
            results.append(not any(r[0].startswith('UMG Recordings, Inc') for r in rows2) and 'Creative Control Corp' not in names2 and not errs2)
            before, sugg, errs3 = supp(p)
            before4, sugg4, _ = supp(p, off=['S470', 'S478'])
            before5, sugg5, errs5 = supp(p, off=())
            print('D)', before5, sugg5)
            results.append(any('2026' in x and 'column ℗/©' in x for x in sugg5) and not errs5)
            print('C)', before, sugg, errs3, '| aus:', sugg4)
            results.append(2026 not in before and any('notes of Discogs' in x and '2026' in x for x in sugg) and not any('2026' in x for x in sugg4) and not errs3)
    finally:
        H.discogs_release = orig
        H.MAIN = main0
        H.RELEASE_LABELS = labels0
        H.RULES_OFF = []
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suppfold3221():
    """Credits Importer 3.221.0 (collected items Z-NAMEONLY, Z-SUPPUNRECFOLD, Z-PCYEARAUTO; rules S474, S477, S478): the release imported from
    Discogs (Percy Pursglove trumpet); a Bandcamp album typed as "+ Source" with "Percy Pursglove (UK)" among lines "Name – role", five lines
    not recognized and "℗ © 2026 Creative Control Corp." in its credits.
    A) Percy Pursglove: no new role "performer" – his trumpet confirmed by the added source.
    B) The five lines not recognized at the end, folded: "▸ 5 lines not recognized"; a click shows them (▾), remembered.
    C) The ℗/© year 2026 of the added source placed in the column ℗/© of the date matrix (a suggestion, dashed).
    D) The rules off (as 3.220.0): a new role "performer", the lines unfolded, no cell in ℗/©."""
    ALBUM = 'https://pursglove.bandcamp.com/album/test'
    orig = H.discogs_release

    def rel():
        d = orig()
        d['notes'] = ''
        d['extraartists'] = d.get('extraartists', []) + [{'name': 'Percy Pursglove', 'anv': '', 'role': 'Trumpet', 'tracks': '', 'id': 3611, 'join': ''}]
        return d
    H.ARTISTS[3611] = (H.uid('dddddddd', 3611), 'Percy Pursglove')
    H.attr(9341, 'trumpet', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    credits = """Anna Bell – voice
Percy Pursglove (UK)
Carl Dee – piano
Flurp gnargle snoo
Wibble wobble wubble
Zorp zarp zirp zup
Quux quuz quuy
Plonk plink plank plunk

℗ © 2026 Creative Control Corp."""
    H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': credits, 'about': ''},
                                   'trackinfo': [{'track_num': i + 1, 'title': tt, 'duration': 180.0} for i, tt in enumerate(['Song One', 'Song Two', 'Song Three', 'Song Four'])]})
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    SUPP = """[...document.querySelectorAll('.dci-supp-row')].map(tr => [tr.querySelector('.dci-supp-kind').textContent.trim(), (tr.children[2].querySelector('strong') || tr.children[2]).textContent.trim(), tr.children[5].textContent.replace(/\\s+/g, ' ').trim()])"""
    FOLD = "(() => { const b = document.querySelector('[data-act=supp-unrec-fold]'); return b ? [b.textContent.trim(), b.getAttribute('aria-expanded')] : null; })()"
    CELL = "window.__S.dateMatrix ? 0 : 0"
    PC = "JSON.stringify((window.__S.dm || {}).cells || [])"

    def run(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.open_supp(pg)
        pg.fill('[data-f=supp-url]', ALBUM)
        pg.click('[data-act=supp-url]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Added source: Bandcamp/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
        items = pg.evaluate(SUPP)
        fold = pg.evaluate(FOLD)
        opened = None
        if fold:
            pg.click('[data-act=supp-unrec-fold]')
            pg.wait_for_timeout(300)
            opened = [pg.evaluate(FOLD), len([x for x in pg.evaluate(SUPP) if x[0] == 'not recognized']), pg.evaluate("localStorage.getItem('dci-supp-unrec-open')"),
                      pg.evaluate("document.activeElement.dataset.act || ''")]
        logs = pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9)).filter(x => /℗\\/©/.test(x))")
        b.close()
        return items, fold, opened, logs, errs
    results = []
    H.discogs_release = rel
    try:
        with sync_playwright() as p:
            items, fold, opened, logs, errs = run(p)
            print('A)', items)
            results.append(not any(n == 'Percy Pursglove' for k, n, _ in items) and not errs)
            print('B)', fold, opened)
            results.append(fold == ['▸ 5 lines not recognized', 'false'] and not any(k == 'not recognized' for k, _, _ in items)
                           and opened and opened[0] == ['▾ 5 lines not recognized', 'true'] and opened[1] == 5 and opened[2] == 'true' and opened[3] == 'supp-unrec-fold')
            print('C)', logs)
            results.append(any('2026' in x and 'column ℗/©' in x for x in logs))
            items2, fold2, _, logs2, errs2 = run(p, off=['S474', 'S477', 'S478'])
            print('D)', items2, fold2, logs2)
            results.append(any(n == 'Percy Pursglove' for k, n, _ in items2) and fold2 is None and sum(1 for k, _, _ in items2 if k == 'not recognized') == 5
                           and not any('column ℗/©' in x for x in logs2) and not errs2)
    finally:
        H.discogs_release = orig
        H.MAIN = main0
        H.RULES_OFF = []
        H.ARTISTS.pop(3611, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_awstop3220():
    """Credits Importer 3.220.0 (collected item Z-ARTWORKSSTOP2, S466): the release "If Ever You Would Leave Us (we play for Rollins)";
    "Rollins" the name of two artists in MusicBrainz (one hit in the settings) – the message "“Rollins”: 2 artists … this can take a while";
    Sonny Rollins with 2,500 recordings (a long reading).
    A) The message has "Stop" at once (as soon as it is shown).
    B) "Stop": the message has "Continue" and "Stop and discard"; the reading stops (no more requests of Sonny Rollins).
    C) "Continue": the reading goes on – the message has "Stop" again.
    D) S466 off: the message has no button.
    E) (3.221.0, S471) all read: the message is gone."""
    SR = H.uid('dddddddd', 3900)
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 9440: (H.uid('94409440', 1), 'tribute', 'artist', 'release_group')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    for k, n in [(567, 'cover'), (578, 'live')]:
        H.attr(k, n, k)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578))
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.MB_SEARCH['artist'] = [{'id': SR, 'name': 'Sonny Rollins', 'disambiguation': 'jazz saxophonist', 'type': 'Person', 'score': 100}]
    rel = lambda: [{'target-type': 'artist', 'type': 'composer', 'direction': 'backward', 'artist': {'id': SR, 'name': 'Sonny Rollins'}}]
    works0 = list(H.WORK_SEARCH)
    W = lambda k: H.uid('3a3a3a3a', k)
    H.WORK_SEARCH[:] = [{'id': W(1), 'title': H.TITLES[1], 'aliases': [], 'type': 'Song', 'relations': rel()},
                        {'id': W(2), 'title': H.TITLES[2], 'aliases': [], 'type': 'Song', 'relations': rel()}]
    H.ARTIST_WORKS[SR] = [{'id': W(1), 'title': H.TITLES[1], 'aliases': []}, {'id': W(2), 'title': H.TITLES[2], 'aliases': []}]
    H.ARTIST_RECORDINGS[SR] = [{'title': H.TITLES[3], 'work': {'id': W(3), 'title': H.TITLES[3]}}]
    orig_ws, orig_js, orig_dg = H.ws_release, H.js_entity, H.discogs_release
    H.js_entity = lambda gid: ({'entityType': 'artist', 'id': 3900, 'gid': SR, 'name': 'Sonny Rollins', 'comment': 'jazz saxophonist'} if gid == SR else orig_js(gid))

    def ws(full=False):
        d = orig_ws(full)
        d['title'] = 'If Ever You Would Leave Us (we play for Rollins)'
        return d
    H.ws_release = ws

    def dg():
        d = orig_dg()
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = dg
    H.MB_SEARCH['artist'] = H.MB_SEARCH['artist'] + [{'id': H.uid('dddddddd', 3901), 'name': 'Rollins Band', 'disambiguation': '', 'type': 'Group', 'score': 90}]
    H.ARTIST_RECORDINGS[SR] = 2500
    main0 = H.MAIN
    H.MAIN = H.MAIN_SLOW.replace('  const S = {', '  const S = window.__S = {', 1)
    MSG = """(() => { const m = document.querySelector('[data-msgkey="ded.manyNames"]'); return m ? [...m.querySelectorAll('button[data-act^=mx-aw]')].map(b => b.dataset.act + ':' + b.textContent.trim()) : null; })()"""
    results = []

    def open_page(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("localStorage.setItem('dci-aw-ask', '2'); localStorage.setItem('dci-mb-hits', '1');")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        H.wait_for(pg, "!!document.querySelector('[data-msgkey=\"ded.manyNames\"]')", 90)
        return b, pg, errs

    try:
        with sync_playwright() as p:
            b, pg, errs = open_page(p)
            a = pg.evaluate(MSG)
            print('A)', a)
            results.append(a == ['mx-aw-stop:Stop'])
            # Sonny Rollins picked in the box: his works are read (slowly)
            H.wait_ok(pg, "!!document.querySelector('[data-el=dedbox] [data-act=ded-pick]')", 30)
            pg.locator('[data-el=dedbox] [data-act=ded-pick]').first.evaluate('b => b.click()')
            for _ in range(60):
                if [x for x in H.BROWSES if x[1] == SR]:
                    break
                pg.wait_for_timeout(500)
            pg.click('[data-msgkey="ded.manyNames"] [data-act=mx-aw-stop]')
            pg.wait_for_timeout(2500)
            n1 = len([x for x in H.BROWSES if x[1] == SR])
            pg.wait_for_timeout(2500)
            n2 = len([x for x in H.BROWSES if x[1] == SR])
            bb = pg.evaluate(MSG)
            print('B)', bb, n1, n2)
            results.append(bb == ['mx-aw-go:Continue', 'mx-aw-stop:Stop and discard'] and n1 == n2 and n1 > 0)
            pg.click('[data-msgkey="ded.manyNames"] [data-act=mx-aw-go]')
            pg.wait_for_timeout(3000)
            n3 = len([x for x in H.BROWSES if x[1] == SR])
            c = pg.evaluate(MSG)
            print('C)', c, n3)
            results.append(n3 > n2 and c in (['mx-aw-stop:Stop'], []))
            # E) (3.221.0, S471) all read: the message is gone
            H.wait_ok(pg, "!window.__S.artistWorksRunning && !window.__S.awPaused", 120)
            pg.wait_for_timeout(500)
            e = pg.evaluate("!!document.querySelector('[data-msgkey=\"ded.manyNames\"]')")
            print('E) Meldung noch da:', e, pg.evaluate("[window.__S.artistWorksRunning, window.__S.awPaused, window.__S.awLong, window.__S.artistWorksAgain]"), errs[-3:])
            results.append(e is False)
            results.append(not errs)
            b.close()
            b, pg, errs = open_page(p, off=['S466'])
            d = pg.evaluate(MSG)
            print('D)', d)
            results.append(d == [] and not errs)
            b.close()
    finally:
        H.MAIN = main0
        H.ws_release, H.js_entity, H.discogs_release = orig_ws, orig_js, orig_dg
        H.WORK_SEARCH[:] = works0
        H.ARTIST_WORKS.pop(SR, None)
        H.ARTIST_RECORDINGS.pop(SR, None)
        H.MB_SEARCH.pop('artist', None)
        H.RULES_OFF = []
        for i in added_lts:
            H.LTS.pop(i, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_courvoisier3211():
    """Credits Importer 3.211.0 (collected items Z-EDITEDAT, Z-MASTEREDBYLATE, Z-PROSOCALL, Z-DESIGNSTUDIO, Z-PKGWALLET, Z-CREATENOTELINKS;
    rules S414 – S418): the credits of Sylvie Courvoisier's album as Discogs notes.
    A) Owen Mulholland edited by, the place "35 Street Studio" edited at (no entry "NYC"); Denis Blackham mastered by; Sylvie Courvoisier
       composer (works); Michael Dyer design, no entry "Remake"; Véronique Hoegger photography; the line of the package left out.
    B) "Create artist" for a name of the notes (no page of its own): the edit note names the Discogs release the notes are from.
    C) The rules off (as 3.210.0): "NYC" an entry, no Denis Blackham, "Remake" an entry, no source in the edit note."""
    import urllib.parse
    orig = H.discogs_release
    NOTES = ('Sylvie Courvoisier: piano, composition\nDan Weiss: drums\n\nAll compositions by Sylvie Courvoisier (SUISA, ASCAP)\n\n'
             'Recorded by Ryan Streber on April 22, 2025 at Oktaven Audio, Mount Vernon, NY\nEdited by Owen Mulholland at 35 Street Studio, NYC\n'
             'Mastered on January 28, 2026 at Skye Mastering by Denis Blackham\n\nDesign by Michael Dyer / Remake\nPortrait by Véronique Hoegger\n\n'
             'Compact Disc (CD): Six panel wallet and CD\n')

    def rel():
        d = orig()
        d['notes'] = NOTES
        d['companies'] = []
        d['extraartists'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    ROWS = """() => window.__S.rows.filter(r => r.level !== 'skip').map(r => [(window.__S.artists.get(r.artistKey) || {}).name, (r.types || []).join('|'), r.level])"""
    IGN = "[...document.querySelectorAll('[data-el=ignored] li, .dci-ign li, .dci-ignored li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim())"

    def run(p, off=()):
        H.RULES_OFF = list(off)
        H.ENTRIES_VIEW = 'legacy'
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
        rows = pg.evaluate(ROWS)
        ign = pg.evaluate("JSON.stringify(window.__S.notesResult ? window.__S.notesResult.ignored : null)") or ''
        body = pg.evaluate("document.body.innerText")
        note = None
        sel = [x for x in pg.evaluate("[...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), g.dataset.group])") if x[0] == 'Véronique Hoegger']
        if sel and pg.locator(f'section[data-group="{sel[0][1]}"] [data-act=artist-create]').count():
            pg.click(f'section[data-group="{sel[0][1]}"] [data-act=artist-create]')
            pg.wait_for_selector('[data-el=sub]:not([hidden])', timeout=20000)
            url = pg.evaluate("document.querySelector('[data-el=sub-frame]').src")
            note = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query)).get('edit-artist.edit_note', '')
        b.close()
        return rows, body, note, errs

    has = lambda rows, name, t: any(r[0] == name and t in r[1] for r in rows)
    results = []
    H.discogs_release = rel
    try:
        with sync_playwright() as p:
            rows, body, note, errs = run(p)
            names = sorted({r[0] for r in rows})
            print('A)', names, [r for r in rows if r[0] in ('35 Street Studio', 'Denis Blackham', 'Sylvie Courvoisier', 'Michael Dyer', 'Véronique Hoegger', 'Owen Mulholland')], errs)
            results.append(has(rows, '35 Street Studio', 'edited at') and 'NYC' not in names and has(rows, 'Denis Blackham', 'mastering') and has(rows, 'Sylvie Courvoisier', 'composer')
                           and has(rows, 'Michael Dyer', 'design') and 'Remake' not in names and has(rows, 'Véronique Hoegger', 'photography') and has(rows, 'Owen Mulholland', 'editor')
                           and 'Six panel wallet' not in [r[0] for r in rows] and not errs)
            print('B)', repr(note))
            results.append(bool(note) and note.startswith('Source: https://www.discogs.com/release/'))
            rows, body, note, errs = run(p, off=['S414', 'S415', 'S416', 'S417', 'S418'])
            names = sorted({r[0] for r in rows})
            print('C)', names, repr(note), errs)
            results.append('NYC' in names and 'Denis Blackham' not in names and 'Remake' in names and not (note or '').startswith('Source:') and not errs)
    finally:
        H.discogs_release = orig
        H.MAIN = main0
        H.RULES_OFF = []
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_kindofshadow3212():
    """Credits Importer 3.212.0 (collected items Z-RECBYLATE, Z-NAMEYEARAREA, Z-PLACECREDITAREA, Z-PUBYEAR, Z-PUBLABEL, Z-PUBLEVEL,
    Z-CREATEMEMBER2; rules S419, S420, S422, S424 – S426): Kind Of Shadow – the Discogs notes, "Recorded At – Agnieszka Osiecka Polish Radio
    Concert Hall, Warsaw", "Published By – Pub Co" (a label of the release), the release's artist a group of MusicBrainz.
    A) Kuba Sosulski recording; Artur Majewski mix, no entry "Wrocław"; Grzegorz Piwkowski mastering, the place "Hi End Studio", no entry
       "Warsaw"; the place "Agnieszka Osiecka Polish Radio Concert Hall" with its area Warsaw.
    B) Pub Co: publishing with the date 2023; its works the new ones (more tracks than with S425 off); the level switched to Release.
    C) "Create artist" for Arun Kumar (guitar): "member of" Test Band with guitar, said in the dialog; for Guest Person (vocals, guest): none.
    D) The rules off (as 3.211.0): an entry "Wrocław", no Kuba Sosulski, no "member of"."""
    import urllib.parse
    orig = H.discogs_release
    NOTES = ('Recorded 17 of October 2021 at Agnieszka Osiecka Polish Radio Concert Hall, Warsaw by Kuba Sosulski\n'
             'Mixed by Artur Majewski 2022, Wrocław\nMasterded by Grzegorz Piwkowski, Hi End Studio 2022, Warsaw\n\n'
             'All Rights Reserved Pub Co! FSR 01/2023\nPublished by Pub Co 2023\n')

    def rel():
        d = orig()
        d['notes'] = NOTES
        d['companies'] = [{'name': 'Pub Co', 'entity_type_name': 'Published By', 'id': 1003, 'catno': ''},
                          {'name': 'Agnieszka Osiecka Polish Radio Concert Hall, Warsaw', 'entity_type_name': 'Recorded At', 'id': 1099, 'catno': ''}]
        d['extraartists'] = [{'name': 'Arun Kumar', 'anv': '', 'role': 'Guitar', 'tracks': '', 'id': 999401, 'join': ''},
                             {'name': 'Guest Person', 'anv': '', 'role': 'Vocals [Guest]', 'tracks': '', 'id': 999402, 'join': ''},
                             {'name': 'Writer Z', 'anv': '', 'role': 'Composed By', 'tracks': '', 'id': 3009, 'join': ''}]
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    main0, ac0, rl0 = H.MAIN, list(H.RELEASE_AC), list(H.RELEASE_LABELS)
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    band = H.uid('dddddddd', 3212)
    ROWS = """() => window.__S.rows.filter(r => r.level !== 'skip').map(r => { const a = window.__S.artists.get(r.artistKey) || {};
      return [a.name, (r.types || []).join('|'), r.level, r.date ? r.date.by || '' : '', r.tracks ? r.tracks.size : 0, a.area || '', r.id]; })"""

    def create(pg, name):
        sel = [x for x in pg.evaluate("[...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), g.dataset.group])") if x[0] == name]
        if not sel or not pg.locator(f'section[data-group="{sel[0][1]}"] [data-act=artist-create]').count():
            return None, ''
        pg.click(f'section[data-group="{sel[0][1]}"] [data-act=artist-create]')
        pg.wait_for_selector('[data-el=sub]:not([hidden])', timeout=20000)
        url = pg.evaluate("document.querySelector('[data-el=sub-frame]').src")
        info = pg.evaluate("document.querySelector('[data-el=sub-info]').innerText")
        pg.click('[data-act=sub-close]')
        pg.wait_for_timeout(300)
        return dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query)), info

    def run(p, off=()):
        H.RULES_OFF = list(off)
        H.ENTRIES_VIEW = 'legacy'
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
        rows = pg.evaluate(ROWS)
        arun = create(pg, 'Arun Kumar')
        guest = create(pg, 'Guest Person')
        lvl = None
        pub = [r for r in rows if r[0] == 'Pub Co' and 'publish' in r[1]]
        if pub:
            g = pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(g => g.querySelector('.dci-gname strong').textContent.trim() === 'Pub Co').dataset.group")
            btn = pg.locator(f'section[data-group="{g}"] [data-act=level][data-level=release]')
            if btn.count():
                btn.first.click()
                pg.wait_for_timeout(500)
                lvl = pg.evaluate(f"(() => {{ const r = window.__S.rows.find(r => r.id === '{pub[0][6]}'); return r ? r.level : null; }})()")
        b.close()
        return rows, arun, guest, lvl, errs

    has = lambda rows, name, t: any(r[0] == name and t in r[1] for r in rows)
    results = []
    H.discogs_release = rel
    H.ARTISTS[3212] = (band, 'Test Band')
    H.RELEASE_AC[:] = [(band, 'Test Band', 'Test Band', '', 'Group')]
    H.RELEASE_LABELS[:] = [(H.COMPANIES[1003][1], 'Pub Co', 'FSR 01/2023')]
    try:
        with sync_playwright() as p:
            rows, arun, guest, lvl, errs = run(p)
            names = sorted({r[0] for r in rows})
            place = [r for r in rows if r[0] and r[0].startswith('Agnieszka')]
            print('A)', names, place[:1], errs)
            results.append(has(rows, 'Kuba Sosulski', 'recording') and has(rows, 'Artur Majewski', 'mix') and all('mixed in' in r[1] for r in rows if r[0] == 'Wrocław') and has(rows, 'Grzegorz Piwkowski', 'mastering')
                           and 'Hi End Studio' in names and 'Warsaw' not in names and place and place[0][0] == 'Agnieszka Osiecka Polish Radio Concert Hall' and 'Warsaw' in place[0][5] and not errs)
            pub = [r for r in rows if r[0] == 'Pub Co' and 'publish' in r[1]]
            print('B)', pub, lvl)
            n_on = max([r[4] for r in pub] or [0])
            q, info = arun
            gq, ginfo = guest
            print('C)', {k: v for k, v in (q or {}).items() if k.startswith('rels.')}, '|', info, '| guest:', {k: v for k, v in (gq or {}).items() if k.startswith('rels.')})
            results.append(bool(q) and q.get('rels.0.target') == band and q.get('rels.0.attributes.0.type') and 'member of Test Band' in info and gq is not None and 'rels.0.target' not in gq)
            rows2, arun2, guest2, lvl2, errs2 = run(p, off=['S419', 'S420', 'S422', 'S424', 'S425', 'S426'])
            names2 = sorted({r[0] for r in rows2})
            pub2 = [r for r in rows2 if r[0] == 'Pub Co' and 'publish' in r[1]]
            print('D)', names2, pub2, {k: v for k, v in (arun2[0] or {}).items() if k.startswith('rels.')})
            results.insert(1, any(r[3] == '2023' for r in pub) and n_on > max([r[4] for r in pub2] or [0]) and lvl == 'release')
            results.append(any(r[0] == 'Wrocław' and 'mix' in r[1] and 'mixed in' not in r[1] for r in rows2) and 'Kuba Sosulski' not in names2 and arun2[0] is not None and 'rels.0.target' not in arun2[0] and not errs2)
    finally:
        H.discogs_release = orig
        H.MAIN = main0
        H.RELEASE_AC[:] = ac0
        H.RELEASE_LABELS[:] = rl0
        H.RULES_OFF = []
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_videoplace3213():
    """Credits Importer 3.213.0 (collected item Z-VIDEOPLACE, rule S430): track 2 is a video in MusicBrainz (its recording's flag);
    Discogs "Recorded At – Abbey Road Studios" (a place).
    A) Abbey Road Studios: "recorded at" on tracks 1, 3, 4 and "video shot at" on track 2 (until 3.212.0 "recorded at" on all).
    B) S430 off: "recorded at" on all four tracks."""
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    H.lt(9006, H.uid('9e9e9e9e', 6), 'video shot at', 'place', 'recording', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.VIDEO_TRACKS.add(1)
    ROWS = """() => window.__S.rows.filter(r => r.level !== 'skip' && (window.__S.artists.get(r.artistKey) || {}).name === 'Abbey Road Studios')
      .map(r => [(r.types || [])[0] || '', [...r.tracks].sort()])"""

    def run(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
        out = sorted(pg.evaluate(ROWS))
        b.close()
        return out, errs
    results = []
    try:
        with sync_playwright() as p:
            a, errs = run(p)
            print('A)', a, errs)
            results.append(a == [['recorded at', [0, 2, 3]], ['video shot at', [1]]] and not errs)
            b2, errs2 = run(p, off=['S430'])
            print('B)', b2)
            results.append(b2 == [['recorded at', [0, 1, 2, 3]]] and not errs2)
    finally:
        H.MAIN = main0
        H.RULES_OFF = []
        H.VIDEO_TRACKS.discard(1)
        H.LTS.pop(9006, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_texts3215():
    """Credits Importer 3.215.0 (collected items Z-ANDPLACE, Z-LOWERCASECO, Z-DRAGONAUT, Z-RAMMSTEIN, Z-INSERTLINES, Z-SHIPP; rules S435 –
    S440, D041): lines of the Bandcamp texts as Discogs notes of a CD release.
    A) Places: "Friends and Neighbors" one place; "Abbey Road & Olympic Studios" two; "Electric Lady and Sear Sound" – MusicBrainz has
       both, not the whole – two entries; "Supported by: cnm" – CNM.
    B) Dragonaut: Bingy drums; recorded in Albuquerque and San Jose; Sub 80 engineered at; Sinai mixed at; Ventura mastered in; Kevin Gray
       (lacquer cut), Cohearent and Fidelity Record Press left out (a CD); the biography left out.
    C) Shipp: Jim Clouse recording, mix and mastering; Anna Yatskevich and the drawings of Florence Giroud left out (a CD), Florence Giroud
       lyricist; the editions and the sides left out.
    D) Rammstein: Paul Dugdale left out (no videos); no 2026 date in the pool; MusicBrainz's event of 1 October 2022 at Foro Sol offered
       (not the one of 3 October, nor one of another place).
    E) The rules off (as 3.214.0): "Friends" and "Neighbors" two places, no Bingy, no Jim Clouse, "cnm"."""
    orig = H.discogs_release
    NOTES = ('Mixed by Nathaniel Morgan at Friends and Neighbors, Brooklyn\nRecorded at Abbey Road & Olympic Studios, London\n'
             'Recorded by John Doe at Electric Lady and Sear Sound\nSupported by: cnm\n\n'
             'Al Cisneros bass & vocals\nBingy drums\n\n'
             'recorded Albuquerque & San Jose, 2024 & 2025\nengineer Andrew Seidel (Sub 80)\nmix Bassy (Sinai, Albuquerque)\nmastering JJ Golden (Ventura)\n'
             'lacquers Kevin Gray\n\nLacquer cut at 45rpm by Kevin Gray at Cohearent & audiophile vinyl pressed by Fidelity Record Press to ensure sound.\n'
             'Al Cisneros is a founding member of the bands Sleep & OM.\n\n'
             'Recorded (June 25, 2025), mixed, and mastered by Jim Clouse\nInsert photographs of Matthew & William by Anna Yatskevich\n'
             'drawings & texts by Florence Giroud\nVinyl LP: // Edition of 500 //\nLtd. Edition LP on Black Vinyl\n'
             'Side A: Deeper Fields / Notions of Order / Momenta\n\n'
             'It captures their three concerts at the Foro Sol in Mexico City on 1, 2 and 4 October 2022. The director is Paul Dugdale.\n'
             'Officially announced on 15 September 2026 after a long wait.\n')

    def rel():
        d = orig()
        d['notes'] = NOTES
        d['companies'] = []
        d['extraartists'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    ROWS = """() => window.__S.rows.filter(r => r.level !== 'skip').map(r => [(window.__S.artists.get(r.artistKey) || {}).name, (r.types || []).join('|'), r.raw || ''])"""
    pl = lambda i, n: {'id': H.uid('a1a1a1a1', i), 'name': n, 'score': 100, 'disambiguation': ''}
    ev = lambda i, n, day, place: {'id': H.uid('e2e2e2e2', i), 'name': n, 'score': 100, 'life-span': {'begin': day, 'end': day},
                                    'relations': [{'type': 'held at', 'place': {'id': H.uid('a1a1a1a1', 50 + i), 'name': place}}]}
    s0 = {k: list(v) for k, v in H.MB_SEARCH.items()}
    H.MB_SEARCH['place'] = [pl(1, 'Electric Lady'), pl(2, 'Sear Sound')]
    H.MB_SEARCH['event'] = [ev(1, 'Rammstein at Foro Sol', '2022-10-01', 'Foro Sol'), ev(2, 'Rammstein at Foro Sol (3)', '2022-10-03', 'Foro Sol'),
                            ev(3, 'Foro Sol Fest', '2022-10-02', 'Estadio Azteca')]

    def run(p, off=()):
        H.RULES_OFF = list(off)
        H.ENTRIES_VIEW = 'legacy'
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
        pg.wait_for_timeout(2500)
        rows = pg.evaluate(ROWS)
        pool = pg.evaluate("window.__S.datePool.map(d => d.begin ? d.begin.year : null)")
        fest = pg.evaluate("(window.__S.festivals || []).map(f => [f.name, f.offers.map(o => o.name)])")
        b.close()
        return rows, pool, fest, errs
    has = lambda rows, name, t: any(r[0] == name and t in r[1] for r in rows)
    results = []
    H.discogs_release = rel
    try:
        with sync_playwright() as p:
            rows, pool, fest, errs = run(p)
            names = sorted({r[0] for r in rows})
            print('A-C)', names)
            print('   ', rows)
            print('D)', pool, fest, errs)
            results.append('Friends and Neighbors' in names and 'Friends' not in names and {'Abbey Road', 'Olympic Studios', 'Electric Lady', 'Sear Sound', 'CNM'} <= set(names))
            results.append(has(rows, 'Bingy', 'instrument') and has(rows, 'Albuquerque', 'recorded in') and has(rows, 'San Jose', 'recorded in') and has(rows, 'Sub 80', 'engineered at')
                           and has(rows, 'Sinai', 'mixed at') and has(rows, 'Ventura', 'mastered in') and 'Kevin Gray' not in names and 'Cohearent' not in names
                           and 'Fidelity Record Press' not in names)
            results.append(has(rows, 'Jim Clouse', 'recording') and has(rows, 'Jim Clouse', 'mix') and has(rows, 'Jim Clouse', 'mastering') and 'Anna Yatskevich' not in names
                           and has(rows, 'Florence Giroud', 'lyricist') and not has(rows, 'Florence Giroud', 'illustration'))
            results.append('Paul Dugdale' not in names and 2026 not in pool and fest == [['Foro Sol', ['Rammstein at Foro Sol']]] and not errs)
            rows2, pool2, fest2, errs2 = run(p, off=['S435', 'S436', 'S437', 'S438', 'S439', 'S440', 'D041'])
            names2 = sorted({r[0] for r in rows2})
            print('E)', names2, pool2, fest2)
            results.append('Friends' in names2 and 'Bingy' not in names2 and 'Jim Clouse' not in names2 and 'cnm' in names2 and not errs2)
    finally:
        H.discogs_release = orig
        H.MAIN = main0
        H.RULES_OFF = []
        H.MB_SEARCH.clear(); H.MB_SEARCH.update(s0)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_krakow3216():
    """Credits Importer 3.216.0 (collected items Z-RECCONT, Z-DTSSTUDIO/Z-ELIDEDNAME, Z-COPYYEAR, Z-AMPNAME, Z-OVERDUBAT, Z-BONUSLINE,
    Z-LEGALNAME; rules S441 – S447, D042): Discogs notes of a release of four CDs (one track each).
    A) "Recorded: October 11-12, 2018 at the Alchemia Club, Kraków (CD#1, CD#2, CD#3)" / "October 13, 2018 at Radio Kraków (CD#4)":
       Alchemia Club on tracks 1–3, Radio Kraków on track 4; 2018-10-13 a date of Performance.
    B) "Recorded, mixed and mastered by [...] (DTS Studio)": Mix Guy (Discogs: Mixed By) recording, mix and mastering; DTS Studio recorded,
       mixed and mastered at; no entry "Elided Credited".
    C) "Andrew Diamond guitar & zither" (zither unknown here): Andrew Diamond guitar (no entry "& zither"); "Overdubs recorded at Electric
       Lady": Electric Lady recorded at, credited "overdubs".
    D) "Incl. Bonustracks "Curved Nothing" and "Song One"": a message names "Curved Nothing" (not on the release), not "Song One".
    E) The rules off (as 3.215.0): no Radio Kraków, no DTS Studio rows for Mix Guy's recording."""
    orig = H.discogs_release
    NOTES = ('Recorded: October 11-12, 2018 at the Alchemia Club, Kraków (CD#1, CD#2, CD#3)\nOctober 13, 2018 at Radio Kraków (CD#4)\n\n'
             'Recorded, mixed and mastered by [...] (DTS Studio)\n\n© ℗ 2022\n\nAl Cisneros bass & vocals\nAndrew Diamond guitar & zither\n\n'
             'Overdubs recorded at Electric Lady\nCompact Disc (CD): Incl. Bonustracks "Curved Nothing" and "Song One"\n')

    def rel():
        d = orig()
        d['notes'] = NOTES
        d['companies'] = []
        d['extraartists'] = [{'name': 'Mix Guy', 'anv': '', 'role': 'Mixed By', 'tracks': '', 'id': 3501, 'join': ''}]
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    main0, media0 = H.MAIN, H.MEDIA
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    H.MEDIA = [1, 1, 1, 1]
    H.ARTISTS[3501] = (H.uid('dddddddd', 3501), 'Mix Guy')
    ROWS = """() => window.__S.rows.filter(r => r.level !== 'skip').map(r => [(window.__S.artists.get(r.artistKey) || {}).name, (r.types || []).join('|'), [...(r.tracks || [])].sort(), r.roleCredit || ''])"""

    def run(p, off=()):
        H.RULES_OFF = list(off)
        H.ENTRIES_VIEW = 'legacy'
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
        rows = pg.evaluate(ROWS)
        pool = pg.evaluate("window.__S.datePool.map(d => [d.name, d.begin ? [d.begin.year, d.begin.month, d.begin.day].join('-') : ''])")
        msgs = pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(m => m.textContent)")
        ign = pg.evaluate("JSON.stringify((window.__S.release || {}).ignored || [])")
        b.close()
        return rows, pool, msgs, ign, errs
    has = lambda rows, name, t: any(r[0] == name and t in r[1] for r in rows)
    results = []
    H.discogs_release = rel
    try:
        with sync_playwright() as p:
            rows, pool, msgs, ign, errs = run(p)
            names = sorted({r[0] for r in rows})
            print('A)', [r for r in rows if r[0] in ('Alchemia Club', 'Radio Kraków')], pool)
            results.append(any(r[0] == 'Alchemia Club' and r[2] == [0, 1, 2] for r in rows) and any(r[0] == 'Radio Kraków' and r[2] == [3] for r in rows)
                           and any(x[1] == '2018-10-13' and x[0].startswith('Performance') for x in pool))
            print('B)', [r for r in rows if r[0] in ('Mix Guy', 'DTS Studio')], names, ign.count('copyrightYear'))
            results.append(has(rows, 'Mix Guy', 'recording') and has(rows, 'Mix Guy', 'mix') and has(rows, 'Mix Guy', 'mastering') and has(rows, 'DTS Studio', 'recorded at')
                           and has(rows, 'DTS Studio', 'mastered at') and 'Elided Credited' not in names)
            print('C)', [r for r in rows if r[0] in ('Andrew Diamond', 'Electric Lady')], [n for n in names if n.startswith('&')])
            results.append(has(rows, 'Andrew Diamond', 'instrument') and not [n for n in names if n.startswith('&')] and any(r[0] == 'Electric Lady' and r[3] == 'overdubs' for r in rows))
            print('D)', msgs, errs)
            results.append(any('Curved Nothing' in m and 'Song One' not in m for m in msgs) and not errs)
            rows2, pool2, msgs2, ign2, errs2 = run(p, off=['S441', 'S442', 'S443', 'S444', 'S445', 'S446', 'S447', 'D042'])
            names2 = sorted({r[0] for r in rows2})
            print('E)', names2)
            results.append('Radio Kraków' not in names2 and not has(rows2, 'Mix Guy', 'recording') and not errs2)
    finally:
        H.discogs_release = orig
        H.MAIN = main0
        H.MEDIA = media0
        H.RULES_OFF = []
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_legalname3216():
    """Credits Importer 3.216.0 (collected item Z-LEGALNAME, rule S442): the release artist Alio Die, whose other name in MusicBrainz is
    "Stefano Musso"; MusicBrainz has the person Stefano Musso too. The notes: "All music composed and recorded by Stefano Musso".
    A) The entry Stefano Musso: the first suggestion is Stefano Musso (the person), Alio Die after it, marked as another name in this release
       (until 3.215.0 Alio Die first, highlighted).
    B) S442 off: Alio Die first."""
    orig = H.discogs_release
    ALIO, SM = H.uid('abcdabcd', 1), H.uid('abcdabcd', 2)

    def rel():
        d = orig()
        d['notes'] = 'All music composed and recorded by Stefano Musso'
        d['companies'] = []
        d['extraartists'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    main0, ac0 = H.MAIN, list(H.RELEASE_AC)
    s0 = {k: list(v) for k, v in H.MB_SEARCH.items()}
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    H.RELEASE_AC[:] = [(ALIO, 'Alio Die', 'Alio Die', '')]
    H.MB_SEARCH['artist'] = [{'id': ALIO, 'name': 'Alio Die', 'disambiguation': 'Italian ambient', 'score': 100, 'aliases': [{'name': 'Stefano Musso'}]},
                             {'id': SM, 'name': 'Stefano Musso', 'disambiguation': 'Italian ambient producer', 'score': 100}]
    HITS = """() => { const a = [...window.__S.artists.values()].find(x => x.name === 'Stefano Musso'); return a ? (a.nameHits || []).map(h => [h.name, !!h.linked, !!h.linkedAs]) : null; }"""

    def run(p, off=()):
        H.RULES_OFF = list(off)
        H.ENTRIES_VIEW = 'legacy'
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
        hits = pg.evaluate(HITS)
        b.close()
        return hits, errs
    results = []
    H.discogs_release = rel
    try:
        with sync_playwright() as p:
            hits, errs = run(p)
            print('A)', hits, errs)
            results.append(bool(hits) and hits[0][0] == 'Stefano Musso' and ['Alio Die', False, True] in hits and not errs)
            hits2, errs2 = run(p, off=['S442'])
            print('B)', hits2)
            results.append(bool(hits2) and hits2[0][:2] == ['Alio Die', True] and not errs2)
    finally:
        H.discogs_release = orig
        H.MAIN = main0
        H.RELEASE_AC[:] = ac0
        H.MB_SEARCH.clear(); H.MB_SEARCH.update(s0)
        H.RULES_OFF = []
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suppgroups3225():
    """Credits Importer 3.225.0 (collected items Z-SUPPGROUPS, Z-OCRDATES; rules S535, S536): the release imported from Discogs; a text added as
    "+ Source" (typed): "Dreamtime is:" with "Zac Anderson - Guitar, Lead Vocals", "Cat Maddin - Bass, Lead Vocals" below it, and "Recorded and
    produced by Zac Anderson August 2016 at Eastland Studios".
    A) The group of the added text joins the groups checked (S536): Dreamtime with its two members.
    B) Its date is found (S535): 2016-08 in the date pool.
    C) Off (as 3.224.0): neither."""
    TEXT = ('Dreamtime is:\nZac Anderson - Guitar, Lead Vocals\nCat Maddin - Bass, Lead Vocals\n\n'
            'Recorded and produced by Zac Anderson August 2016 at Eastland Studios')
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)

    def run(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.open_supp(pg)
        pg.click('[data-act=supp-text]')
        pg.wait_for_timeout(300)
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=supp-text-load]')
        H.wait_for(pg, "!!document.querySelector('[data-act=supp-apply]')", 30)
        pg.wait_for_timeout(1500)
        groups = pg.evaluate("((window.__S.workNotesRel || {}).groups || []).map(g => [g.name, (g.members || []).length])")
        pool = pg.evaluate("window.__S.datePool.map(d => d.begin ? [d.begin.year, d.begin.month || ''].join('-') : '')")
        b.close()
        return groups, pool, errs
    results = []
    try:
        with sync_playwright() as p:
            groups, pool, errs = run(p)
            print('A)', groups)
            results.append(['Dreamtime', 2] in groups and not errs)
            print('B)', pool)
            results.append('2016-8' in pool)
            groups2, pool2, errs2 = run(p, off=['S535', 'S536'])
            print('C)', groups2, pool2)
            results.append(not any(g[0] == 'Dreamtime' for g in groups2) and '2016-8' not in pool2 and not errs2)
    finally:
        H.MAIN = main0
        H.RULES_OFF = []
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_timing3230():
    """Credits Importer 3.230.0 (collected item Z-TIMING; rule S557): once nothing runs any more after an import, the log says its
    times – "⏱ Times of this import: dashboard ready after …, all done after … — MusicBrainz (n requests, t): the release …, entries …"
    and Discogs; once only while nothing more runs. Off: no such line.
    (3.231.0) Discogs's step named ("the release", no "?" – its caller was lost after the wait for Discogs's pace)."""
    import re
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"

    def run(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
        pg.wait_for_timeout(6000)
        lines = [x for x in pg.evaluate(LOGS) if 'Times of this import' in x]
        b.close()
        return lines, errs
    results = []
    try:
        with sync_playwright() as p:
            lines, errs = run(p)
            print('A)', lines, errs)
            t = lines[-1] if lines else ''
            results.append(len(lines) >= 1 and 'dashboard ready after' in t and 'MusicBrainz (' in t and 'requests' in t and 'missing links' in t
                           and 'Discogs (1 request, ' in t and re.search(r'Discogs \(1 request, [^)]*\): the release 1 · ', t) and '?' not in t and not errs)
            lines2, errs2 = run(p, off=['S557'])
            print('B)', lines2)
            results.append(not lines2 and not errs2)
    finally:
        H.RULES_OFF = []
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ui3227():
    """Credits Importer 3.227.0 (collected items Z-CMPGROUP, Z-UNRECPENDING, Z-STICKYOVERLAP, Z-BCHIRES; rules S542 – S545): the release from
    Discogs; a text added as "+ Source" (typed): "Guitar Guy: vocals, organ, bells, flute" (four new roles of one line), and "Some odd words here".
    A) The comparison: one row for Guitar Guy, "4 new roles" with a tick each (S544); the group's tick takes all four off; ▸ shows the rows.
    B) While the import reads (S.unrecReading): the lines not recognized set off, ⏳ at the heading and each line (S542); after: neither.
    C) The bar "Add entry manually": no top margin pulling it upwards (S543); "High-resolution images" in the settings (S545), status-map with
       lang and hiRes.
    D) Off: a row per role, no mark, no setting."""
    TEXT = 'Guitar Guy: vocals, organ, bells, flute\nSome odd words here'
    for k, n in [(9191, 'organ'), (9194, 'bell'), (9195, 'flute')]:
        H.attr(k, n, 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1).replace('  function renderSource() {', '  window.__renderSource = () => renderSource();\n  function renderSource() {', 1)

    def run(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.open_supp(pg)
        pg.click('[data-act=supp-text]')
        pg.wait_for_timeout(300)
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=supp-text-load]')
        H.wait_for(pg, "!!document.querySelector('[data-act=supp-apply]')", 30)
        pg.wait_for_timeout(800)
        out = {'group': pg.evaluate("[...document.querySelectorAll('[data-el=supp-group]')].map(r => [r.dataset.n, r.textContent.replace(/\\s+/g, ' ').trim()])"),
               'rows': pg.evaluate("document.querySelectorAll('.dci-supp-row-role').length")}
        if __import__('os').environ.get('DBG'):
            print(pg.evaluate("JSON.stringify(window.__S.supp.items.map(x => [x.kind, x.name, x.rel, x.line, x.artistKey]))"))
        if out['group']:
            pg.locator('[data-f=supp-group]').first.evaluate('c => c.click()')
            pg.wait_for_timeout(300)
            out['sel'] = pg.evaluate("window.__S.supp.items.filter(x => x.kind === 'role').map(x => x.sel)")
            pg.locator('[data-act=supp-group-open]').first.evaluate('b => b.click()')
            pg.wait_for_timeout(300)
            out['open'] = pg.evaluate("document.querySelectorAll('.dci-supp-row-role').length")
        pg.evaluate("window.__S.release.unrecognized = ['Some odd words here']; window.__S.unrecReading = true; window.__renderSource()")
        out['pend'] = pg.evaluate("[!!document.querySelector('.dci-unrec.dci-unrec-pending'), document.querySelectorAll('.dci-unrec .dci-unrec-wait').length]")
        pg.evaluate("window.__S.unrecReading = false; window.__renderSource()")
        out['after'] = pg.evaluate("[!!document.querySelector('.dci-unrec.dci-unrec-pending'), document.querySelectorAll('.dci-unrec .dci-unrec-wait').length, !!document.querySelector('.dci-unrec')]")
        out['stick'] = pg.evaluate("(() => { const s = document.querySelector('[data-el=stick]'); return [s.classList.contains('dci-stick-gap'), getComputedStyle(s).marginTop]; })()")
        out['hires'] = pg.evaluate("document.querySelectorAll('[data-bc-hires]').length + '|' + window.__S.bcHiRes")
        b.close()
        return out, errs
    results = []
    try:
        with sync_playwright() as p:
            o, errs = run(p)
            print('A-C)', o, errs)
            results.append(len(o['group']) == 1 and o['group'][0][0] == '4' and '4 new roles' in o['group'][0][1] and 'Guitar Guy' in o['group'][0][1]
                           and o['rows'] == 0 and o.get('sel') == [False] * 4 and o.get('open') == 4)
            results.append(o['pend'] == [True, 2] and o['after'] == [False, 0, True])
            results.append(o['stick'] == [True, '0px'] and o['hires'].endswith('|true') and not errs)  # (the setting itself: in ⚙ Settings)
            o2, errs2 = run(p, off=['S542', 'S543', 'S544', 'S545'])
            print('D)', o2, errs2)
            results.append(not o2['group'] and o2['rows'] == 4 and o2['pend'][1] == 0 and not o2['stick'][0] and not errs2)
    finally:
        for k in (9191, 9194, 9195):
            H.ATTRS.pop(k, None)
        H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
        H.MAIN = main0
        H.RULES_OFF = []
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_covergroup3226():
    """Credits Importer 3.226.0 (collected items Z-COVERGROUP, Z-MAGICWORKLINKS, Z-AWONEWORDING; rules S540, S541, S539): as magicwords3220, the
    release by Joshua Redman, whose repertoire has "Song Three" (W2) too – it is found through him before the artist of the tribute.
    A) "✨ Answer all": track 3 under "Covers of works by Sonny Rollins" with tracks 2 – "cover of “Song Three”"; each work answer has a ↗ to
       /work/<gid> whose tip names where it was found.
    B) S540 off (as 3.225.0): track 3 not a cover – under its reason ("among the works of Joshua Redman", S539)."""
    SR = H.uid('dddddddd', 3900)
    added_lts = {868: ('b41e7530-cde4-459c-b8c5-dfef08fc8295', 'dedicated to', 'artist', 'release_group'),
                 9440: (H.uid('94409440', 1), 'tribute', 'artist', 'release_group')}
    for i, (g, n, t0, t1) in added_lts.items():
        H.lt(i, g, n, t0, t1, dates=False)
    for k, n in [(567, 'cover'), (578, 'live')]:
        H.attr(k, n, k)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578))
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.MB_SEARCH['artist'] = [{'id': SR, 'name': 'Sonny Rollins', 'disambiguation': 'jazz saxophonist', 'type': 'Person', 'score': 100}]
    rel = lambda: [{'target-type': 'artist', 'type': 'composer', 'direction': 'backward', 'artist': {'id': SR, 'name': 'Sonny Rollins'}}]
    works0 = list(H.WORK_SEARCH)
    W = lambda k: H.uid('3a3a3a3a', k)
    H.WORK_SEARCH[:] = [{'id': W(1), 'title': H.TITLES[1], 'aliases': [], 'type': 'Song', 'relations': rel()},
                        {'id': W(2), 'title': H.TITLES[2], 'aliases': [], 'type': 'Song', 'relations': rel()}]
    H.ARTIST_WORKS[SR] = [{'id': W(1), 'title': H.TITLES[1], 'aliases': []}, {'id': W(2), 'title': H.TITLES[2], 'aliases': []}]
    H.ARTIST_RECORDINGS[SR] = [{'title': H.TITLES[3], 'work': {'id': W(3), 'title': H.TITLES[3]}}]
    orig_ws, orig_js, orig_dg = H.ws_release, H.js_entity, H.discogs_release
    JR = H.uid('dddddddd', 3901)
    ac0 = list(H.RELEASE_AC)
    H.RELEASE_AC[:] = [(JR, 'Joshua Redman', 'Joshua Redman', '')]
    # Joshua Redman recorded "Song Three" before: the work is in his repertoire too
    H.ARTIST_WORKS[JR] = [{'id': W(2), 'title': H.TITLES[2], 'aliases': []}]
    H.WORK_SEARCH[:] = H.WORK_SEARCH[:1]  # "Song Three" only on the artists' pages
    main0 = H.MAIN
    H.MAIN = H.MAIN.replace('  const S = {', '  const S = window.__S = {', 1)
    H.js_entity = lambda gid: ({'entityType': 'artist', 'id': 3900, 'gid': SR, 'name': 'Sonny Rollins', 'comment': 'jazz saxophonist'} if gid == SR else orig_js(gid))

    def ws(full=False):
        d = orig_ws(full)
        d['title'] = 'If Ever You Would Leave Us (we play for Sonny Rollins)'
        return d
    H.ws_release = ws

    def dg():
        d = orig_dg()
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = dg
    BOX = """(() => { const b = document.querySelector('[data-el=dedbox]'); if (!b || b.hidden) return null;
      return { list: [...b.querySelectorAll('.dci-dedlist li')].map(li => { const c = li.cloneNode(true); const sw = c.querySelector('.dci-dedsw');
        if (sw) sw.replaceWith(((sw.querySelector('.dci-on') || {}).dataset || {}).kind === 'tribute' ? 'tribute to' : 'dedicated to'); return c.textContent.replace(/\\s+/g, ' ').trim(); }),
        on: [...b.querySelectorAll('.dci-dedlist [data-act=ded-kind].dci-on')].map(x => x.dataset.kind),
        sugg: [...b.querySelectorAll('.dci-dedsugg')].map(x => [...x.querySelectorAll('[data-act=ded-pick]')].map(y => y.textContent.replace(/\\s+/g, ' ').trim())) }; })()"""
    TRIB = "[...document.querySelectorAll('[data-el=work-tribute]')].map(x => x.closest('[data-track], tr, .dci-mx-row, li') ? x.textContent.trim() : x.textContent.trim())"
    results = []
    ROW = """(() => { const r = document.querySelector('tr[data-work="1"]'); if (!r) return null;
      const by = r.querySelector('.dci-mx-by'); const co = r.querySelector('.dci-wpill[data-attr=cover]');
      return [by ? by.textContent.trim() : '', co ? [co.textContent.trim(), co.classList.contains('dci-wstrong')] : null]; })()"""
    COVERS = "[...document.querySelectorAll('[data-el=magic-item][data-kind=cover]')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())"

    def open_page(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("localStorage.setItem('dci-aw-ask', '0'); localStorage.setItem('dci-magic-level', JSON.stringify('balanced'));")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(3000)
        pg.click('[data-el=dedbox] [data-act=ded-pick]')
        H.wait_ok(pg, "!!document.querySelector('tr[data-work=\"1\"] [data-act=work-pick]')", 30)
        pg.wait_for_timeout(1500)
        return b, pg, errs

    def magic(pg):
        pg.locator('[data-el=works] [data-act=magic-open]').first.evaluate('b => b.click()')
        pg.wait_for_timeout(800)
        got = pg.evaluate(COVERS)
        print('   Vorschau:', pg.evaluate("(document.querySelector('[data-el=magic-preview]') || {textContent: 'keine'}).textContent.replace(/\\s+/g, ' ').slice(0, 400)"))
        c = pg.locator('[data-act=magic-cancel]')
        if c.count():
            c.first.evaluate('b => b.click()')
        pg.wait_for_timeout(300)
        return got

    results = []
    HEADS = "[...document.querySelectorAll('[data-el=magic-preview] .dci-mx-magicgroup')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())"
    LINKS = "[...document.querySelectorAll('[data-el=magic-worklink]')].map(x => [x.closest('[data-el=magic-item]').textContent.replace(/\\s+/g, ' ').trim().slice(0, 4), x.getAttribute('href'), x.title])"

    def run(p, off=()):
        H.RULES_OFF = list(off)
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("localStorage.setItem('dci-aw-ask', '0'); localStorage.setItem('dci-magic-level', JSON.stringify('balanced'));")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(3000)
        if pg.locator('[data-el=dedbox] [data-act=ded-pick]').count():
            pg.click('[data-el=dedbox] [data-act=ded-pick]')
        H.wait_ok(pg, "!!document.querySelector('tr[data-work=\"1\"] [data-act=work-pick]')", 30)
        H.wait_ok(pg, "window.__S.workSearch.size >= 2 && [...window.__S.workSearch.values()].every(v => ['done', 'noWriters'].includes(v.state))", 40)
        pg.wait_for_timeout(1500)
        pg.locator('[data-el=works] [data-act=magic-open]').first.evaluate('b => b.click()')
        H.wait_ok(pg, "!!document.querySelector('[data-act=magic-cancel]')", 30)
        heads, links = pg.evaluate(HEADS), pg.evaluate(LINKS)
        if __import__('os').environ.get('DBG'):
            print(pg.evaluate("JSON.stringify([...window.__S.artistWorkHits.entries()].map(([i, ws]) => [i, ws.map(w => [w.title, w.tribute, w.coverOf, w.awArtist, w.writers])]))"))
            print(pg.evaluate("JSON.stringify([...window.__S.workSearch.entries()].map(([i, v]) => [i, v.state, (v.results || []).map(w => w.title)]))"))
        b.close()
        return heads, links, errs
    try:
        with sync_playwright() as p:
            heads, links, errs = run(p)
            print('A)', heads, links, errs)
            cov = [h for h in heads if h.startswith('Covers of works by Sonny Rollins')]
            results.append(len(cov) == 1 and '(2)' in cov[0] and '1.2' in cov[0] and '1.3 – cover of' in cov[0] and links
                           and all(h.startswith('/work/') for _, h, _ in links) and any('1.3' == k.strip() and W(2) in h and 'Joshua Redman' in t for k, h, t in links) and not errs)
            heads2, links2, errs2 = run(p, off=['S540'])
            print('B)', heads2, links2)
            results.append(not any(h.startswith('Covers of works by Sonny Rollins') and '1.3' in h for h in heads2)
                           and any('among the works of Joshua Redman' in h and '1.3' in h for h in heads2) and not errs2)
    finally:
        H.ws_release, H.js_entity, H.discogs_release = orig_ws, orig_js, orig_dg
        H.MAIN = main0
        H.RELEASE_AC[:] = ac0
        H.WORK_SEARCH[:] = works0
        H.ARTIST_WORKS.pop(SR, None)
        H.ARTIST_WORKS.pop(JR, None)
        H.ARTIST_RECORDINGS.pop(SR, None)
        H.MB_SEARCH.pop('artist', None)
        H.RULES_OFF = []
        for i in added_lts:
            H.LTS.pop(i, None)
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

run_cases(globals())
