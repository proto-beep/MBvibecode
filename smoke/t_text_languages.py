"""Texts, part 2: other languages and prose – German, Spanish, French, Nordic roles, prose credits, "sounds", band members (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: foreign, nordic, prose, sounds, members – each the former smoke/t_<case>.py, unchanged; gondola, blackzenith (3.42.3); `python3 t_text_languages.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
H.NO_ANIM = True  # [3.77.0] (Z-FLK) reading and mapping: no transitions or animations to wait for
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_foreign():
    """Credits Importer 3.21.2: instruments and voices in German, Spanish and French (collected item 43; T034, S025, R102, Q006).
    A pasted text with "Guitarra eléctrica", "Schlagzeug", "contrebasse, voix", "saxo tenor y soprano" (the kind after the
    instrument, shared), "Flügel", "Batterie", "Coros: Lucía y Marta" ("y" between names), "bajo" and "Alto".
    A) Each is mapped as its English term – electric guitar, drums (drum set), double bass, vocal, tenor and soprano
       saxophone, grand piano, background vocals – and gets no role credit (a translation: MusicBrainz's own names; "Batterie"
       is not credited "drums").
    B) "bajo" asks like "Bass" (which bass?), saying that it is a translation and gets no role credit.
    C) "Alto" alone asks: viola, alto saxophone or alto vocals – nothing assumed; "viola" sets the instrument, no role credit.
    D) The window "Mapping rules" lists T034 with the spellings and their languages; its search "@fr" finds the French ones."""
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
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const p = tr.querySelector('[data-f=primary]');
    const c = tr.querySelector('[data-f=role-credit]');
    return [tr.querySelector('.dci-drole').dataset.raw.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', p ? p.value : '', c ? c.value : '',
      (tr.querySelector('.dci-bass-ask') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim()]; })])))()"""
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
        sec = "[...document.querySelectorAll('section.dci-group')].find(s => (s.querySelector('.dci-gname strong').dataset.name || s.querySelector('.dci-gname strong').textContent.trim()) === 'Pierre Leroux')"
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


def case_nordic():
    """Credits Importer 3.28.2: roles in Norwegian, Swedish and Danish, case-only names, an instrument by its last word
    (collected items 58, 59, 78; Windir "1184" as on Discogs, "Antifascist Freedom Music" as on Bandcamp).
    A) Discogs: "Graphics [Grafisk Utforming]" graphic design, "Mastered By [Mastering Av]" mastering, "Mixed By [Miksa Av]"
       mix, "Producer [Produsert Av]" producer – the bracket only names the role in Norwegian: no role credit (S032);
       "Vocals [Clean]", "Vocals [Screams]" with the credits "clean", "screams" in lower case (S034).
    B) "Artwork [Logo Og Kunst]" (Norwegian: logo and art) is two rows: design with the credit "logo" and artwork with the
       credit "art"; each says the role as written on Discogs (S033). On the Discogs page (companion) its line has two marks.
    C) Only the case differs from MusicBrainz: "VALFAR" (credited as, ANV) for Valfar, "KUNST MANN" for Kunst Mann, the
       label "Voices Of Wonder" (Distributed By) for Voices of Wonder – no "credited as" (S031); "M. Mann" for Master Mann
       stays. Typed in by hand, "VALFAR" stays. [3.38.12] (F-4, S060) "VALFAR" and "KUNST MANN" are in normal case from the start
       (the rows name S060 instead of S031).
    D) "Wood Flute" (Discogs) is the instrument flute with the role credit "wood flute" (S035).
    E) A pasted text: "Drums, percussion, and wood flutes" – flute credited "wood flutes" (S035); "Miksa av: X" mix without
       role credit (S032); "Logo og kunst: Y" design "logo" and artwork "art" (S033).
    F) [3.28.3] The rules at the rows (before C types a credit): S032 (Grafik Mann), S033 and not S018 (Kunst Mann), S034 and
       S031 (Valfar), S035 (Flute Frau)."""
    H.attr(9122, 'flute', 14, 14)
    H.attr(9123, 'percussion', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    for i, gid, name, t0, lvl, attrs in [(1201, '1d4c0b5b-0000-4000-8000-000000001201', 'graphic design', 'artist', 'release', (1, 526, 1150)),
                                         (1202, '1d4c0b5b-0000-4000-8000-000000001202', 'artwork', 'artist', 'release', (1, 1150)),
                                         (1203, '1d4c0b5b-0000-4000-8000-000000001203', 'distributed', 'label', 'release', ())]:
        H.lt(i, gid, name, t0, lvl, attrs)
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    for i, n in [(3011, 'Grafik Mann'), (3012, 'Master Mann'), (3013, 'Mix Mann'), (3014, 'Kunst Mann'), (3015, 'Valfar'), (3016, 'Flute Frau')]:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    H.COMPANIES[1006] = ('label', H.uid('eeeeeeee', 6), 'Voices of Wonder')
    CREDITS = [('Grafik Mann', 'Graphics [Grafisk Utforming]', 3011, ''), ('Master Mann', 'Mastered By [Mastering Av]', 3012, 'M. Mann'),
               ('Mix Mann', 'Mixed By [Miksa Av]', 3013, ''), ('KUNST MANN', 'Artwork [Logo Og Kunst]', 3014, ''),
               ('Bob Producer', 'Producer [Produsert Av]', 3005, ''), ('Valfar', 'Vocals [Clean]', 3015, 'VALFAR'),
               ('Valfar', 'Vocals [Screams]', 3015, 'VALFAR'), ('Flute Frau', 'Wood Flute', 3016, '')]
    orig = H.discogs_release


    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': anv, 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i, anv in CREDITS]
        d['companies'] = [{'name': 'Voices Of Wonder', 'entity_type_name': 'Distributed By', 'id': 1006, 'catno': ''}]
        for t in d['tracklist']:
            t['extraartists'] = []
        return d


    def page():
        lis = ''.join(f'<li><span>{r}</span> – <a href="/artist/{i}-{n.replace(" ", "-")}">{anv or n}</a></li>' for n, r, i, anv in CREDITS)
        rows = ''.join(f'<tr data-track-position="{i + 1}"><td>{i + 1}</td><td>{t}</td></tr>' for i, t in enumerate(H.TITLES))
        return (f'<!doctype html><html><head><meta charset="utf-8"><title>Discogs</title></head><body><h1>Test Band – Testalbum</h1>'
                f'<section id="release-tracklist"><table>{rows}</table></section><section id="release-credits"><ul>{lis}</ul>'
                '<h2>Companies, etc.</h2><ul><li><span>Distributed By</span> – <a href="/label/1006-x">Voices Of Wonder</a></li></ul></section></body></html>')


    H.discogs_release = rel
    H.discogs_page = page
    TEXT = """Richard Gilman-Opalsky: Drums, percussion, and wood flutes
Miksa av: Ola Nordmann
Logo og kunst: Kari Nordmann"""
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const p = tr.querySelector('[data-f=primary]');
    const c = tr.querySelector('[data-f=role-credit]'); const cr = tr.querySelector('[data-f=credit]'); const sp = [...tr.querySelectorAll('.dci-sub')].find(x => /one row per task/.test(x.textContent));
    return [tr.querySelector('.dci-drole').dataset.raw.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', p ? p.value : '', c ? c.value : '-', cr ? cr.value : '-',
      sp ? sp.textContent.trim() : '']; })])))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg, dgerr = H.open_discogs(ctx)
        pg, errs = H.open_mb_edit(ctx, companion=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)
        g = pg.evaluate(ROWS)
        for k, v in g.items():
            print('   ', k, v)
        row = lambda name, i=0: ((g.get(name) or []) + [['', '', '', '', '', '']] * (i + 1))[i]
        RULES = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => (s.querySelector('.dci-gname strong').dataset.name || s.querySelector('.dci-gname strong').textContent.trim()) === name);
      return g ? [...g.querySelectorAll('tr.dci-row')].map(tr => [...tr.querySelectorAll('.dci-ruleid')].map(b => b.textContent.trim())) : null; }"""
        # [3.38.12] (F-4, S060) "KUNST MANN" is "Kunst Mann"
        f1 = {n: pg.evaluate(RULES, n) for n in ('Grafik Mann', 'Kunst Mann', 'Valfar', 'Flute Frau')}
        # A)
        a = [row('Grafik Mann'), row('Master Mann'), row('Mix Mann'), row('Bob Producer'), row('Valfar', 0), row('Valfar', 1)]
        print('A) nordisch:', [x[:4] for x in a])
        results.append(a[0][1] == 'graphic design' and a[0][3] in ('', '-') and a[1][1] == 'mastering' and a[1][3] in ('', '-')
                       and a[2][1] == 'mix' and a[2][3] in ('', '-') and a[3][1] == 'producer' and a[3][3] in ('', '-')
                       and a[4][:4] == ['Vocals [Clean]', 'vocal', a[4][2], 'clean'] and a[5][:4] == ['Vocals [Screams]', 'vocal', a[5][2], 'screams'])
        # B)
        k = g.get('Kunst Mann') or g.get('KUNST MANN') or []
        poll = lambda js: H.wait_for(dg, js, 20)
        poll("document.querySelectorAll('#release-credits .dci-dg-mark').length >= 9")
        marks = dg.evaluate("""[...document.querySelectorAll('#release-credits li')].map(li => [li.querySelector('span').textContent, li.querySelectorAll('.dci-dg-mark').length])""")
        print('B) Kunst:', k, '| Zeichen auf Discogs:', marks)
        results.append([x[:4] for x in k] == [['Design [Logo]', 'design', '', 'logo'], ['Artwork [Art]', 'artwork', '', 'art']]
                       and all('Artwork [Logo Og Kunst]' in x[5] for x in k) and dict(marks).get('Artwork [Logo Og Kunst]') == 2)
        # C) case only
        vow = g.get('Voices Of Wonder') or g.get('Voices of Wonder') or []
        c1 = [row('Valfar', 0)[4], row('Valfar', 1)[4], [x[4] for x in k], [x[4] for x in vow], row('Master Mann')[4]]
        # [3.32.2] the head showed "VALFAR*" (the release's spelling); [3.38.12] (S060) "Valfar" – its spelling in normal case
        sec = "section.dci-group:has(.dci-gname strong:text-is('Valfar'))"
        f = pg.locator(f'{sec} tr.dci-row').nth(0).locator('[data-f=credit]')
        f.fill('VALFAR')
        f.dispatch_event('change')
        pg.wait_for_timeout(600)
        c2 = pg.evaluate(ROWS).get('Valfar')[0][4]
        print('C) credited as – Valfar, Kunst, Voices of Wonder, Master Mann:', c1, '| von Hand:', c2)
        results.append(c1 == ['', '', ['', ''], [''], 'M. Mann'] and c2 == 'VALFAR')
        # D)
        d1 = row('Flute Frau')
        print('D) Wood Flute:', d1[:4])
        results.append(d1[:4] == ['Wood Flute', 'instrument', 'flute', 'wood flute'])
        # F) [3.28.3] the rules named at the rows (read before C)
        print('F) Regeln an den Zeilen:', f1)
        results.append('S032' in f1['Grafik Mann'][0] and all('S033' in r and 'S018' not in r and 'S060' in r for r in f1['Kunst Mann'])
                       and all('S034' in r and 'S060' in r for r in f1['Valfar']) and 'S035' in f1['Flute Frau'][0])
        # E) a pasted text
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1500)
        e = pg.evaluate(ROWS)
        for k2, v in e.items():
            print('   ', k2, v)
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        ro = e.get('Richard Gilman-Opalsky') or []
        print('E) Text:', [x[:4] for x in ro], '| Ola:', [x[:4] for x in e.get('Ola Nordmann') or []], '| Kari:', [x[:4] for x in e.get('Kari Nordmann') or []], '| nicht erkannt:', unrec)
        results.append([x[:4] for x in ro][-1:] == [['wood flutes', 'instrument', 'flute', 'wood flutes']] and len(ro) == 3
                       and [x[:2] + [x[3]] for x in e.get('Ola Nordmann') or []] in ([['Miksa av', 'mix', '']], [['Miksa av', 'mix', '-']])
                       and [x[:4] for x in e.get('Kari Nordmann') or []] == [['Design [Logo]', 'design', '', 'logo'], ['Artwork [Art]', 'artwork', '', 'art']]
                       and not unrec)
        print('Fehler:', errs, dgerr)
        results.append(not errs and not dgerr)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_prose():
    """Credits Importer 3.29.0 (milestone "Text recognition, part 3"): credits in prose, places of joined verbs, lists of kinds
    (collected items 70, 71, 76, 77; the texts of ekstasis, Erosion and Antifascist Freedom Music on Bandcamp, pasted).
    A) "A chronicle of rabid deeds, dutifully unearthed from accursed crossroads' soil by K.M. (sounds, words) & E. (voice)."
       → K.M. performer and lyricist, E. vocals (S038, T041; [3.30.6] the performer row is "Sounds", asked – Q008); "Cover artwork channeled by Drahmarduk." → artwork credited
       "cover artwork" (R103, T042); "Logo carved by the guided hand of BMS Illustration." → BMS Illustration, design
       credited "logo" (T042).
    B) "Mixed and mastered at TQA.HQ (July 2026). Thanks to EXEcentrer and Isohyet." → TQA.HQ mixed at and mastered at (S039),
       July 2026 in the date matrix under Mix and under Mastering (D020); the thanks left out.
    C) "Frank Trompeter: Tenor, alto, soprano saxophones" → tenor, alto and soprano saxophone, no role credit (S040);
       "Richard Gilman-Opalsky: Drums, percussion, and wood flutes" → flute credited "wood flutes".
    D) "Mixed and mastered by Brandon Carnes in March 2026." → mix and mastering, March 2026 under Mix and Mastering.
    E) Nothing listed as not recognized.
    F) [3.29.1] "Assembled by Kai Lurk (noises, electronics) & Fen Field (field recordings)." → Kai Lurk effects credited
       "noises" and electronic instruments credited "electronics", Fen Field field recordist (T041)."""
    for i, n in [(9130, 'tenor saxophone'), (9131, 'soprano saxophone'), (9122, 'flute'), (9123, 'percussion'), (9124, 'effects'), (9125, 'electronic instruments')]:
        H.attr(i, n, 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.lt(1202, '1d4c0b5b-0000-4000-8000-000000001202', 'artwork', 'artist', 'release', (1, 1150))
    H.lt(1204, '1d4c0b5b-0000-4000-8000-000000001204', 'mastered at', 'place', 'release', ())
    H.lt(1205, '1d4c0b5b-0000-4000-8000-000000001205', 'field recordist', 'artist', 'recording', (1,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    TEXT = """A chronicle of rabid deeds, dutifully unearthed from accursed crossroads' soil by K.M. (sounds, words) & E. (voice).
Cover artwork channeled by Drahmarduk.
Logo carved by the guided hand of BMS Illustration.
Mixed and mastered at TQA.HQ (July 2026). Thanks to EXEcentrer and Isohyet.
Frank Trompeter: Tenor, alto, soprano saxophones
Richard Gilman-Opalsky: Drums, percussion, and wood flutes
Mixed and mastered by Brandon Carnes in March 2026.
Assembled by Kai Lurk (noises, electronics) & Fen Field (field recordings)."""
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const p = tr.querySelector('[data-f=primary]');
    const c = tr.querySelector('[data-f=role-credit]');
    return [tr.querySelector('.dci-drole').dataset.raw.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', p ? p.value : '', c ? c.value : '-']; })])))()"""
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
        pg.wait_for_timeout(1500)
        g = pg.evaluate(ROWS)
        for k, v in g.items():
            print('   ', k, v)
        cols = pg.evaluate("[...document.querySelectorAll('[data-colhead]')].map(x => x.textContent.replace(/\\s+/g, ' ').trim().slice(0, 40))")
        role = lambda n: [x[0] for x in g.get(n, [])]
        # A)
        a1 = [role('K.M.'), g.get('E.'), g.get('Drahmarduk'), g.get('BMS Illustration')]
        print('A) Prosa:', a1, '| Werke-Spalten:', cols)
        results.append('Sounds' in role('K.M.') and ['Sounds', 'performer'] in [x[:2] for x in g.get('K.M.', [])] and any('K.M.' in c for c in cols) and (g.get('E.') or [[]])[0][:2] == ['Vocals', 'vocal']
                       and (g.get('Drahmarduk') or [[]])[0][1:4:2] == ['artwork', 'cover artwork'] and (g.get('BMS Illustration') or [[]])[0][1:4:2] == ['design', 'logo'])
        # B) + D) places and dates
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]')")
        mx = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-matrix:{H.REL}') || '{{}}')")
        byId = {d['id']: d for d in pool}
        # (the cells of the text: those of 2026 – the Discogs release loaded before it has 2001)
        cells = sorted(x for x in ((c['col'], '-'.join(str(y) for y in (byId[c['date']]['begin']['year'], byId[c['date']]['begin']['month']))) for c in mx.get('cells', [])) if x[1].startswith('2026'))
        print('B/D) TQA.HQ:', g.get('TQA.HQ'), '| Matrix:', cells)
        results.append([x[0] for x in g.get('TQA.HQ', [])] == ['Mixed At', 'Mastered At']
                       and cells == [('mastering', '2026-3'), ('mastering', '2026-7'), ('mix', '2026-3'), ('mix', '2026-7')])
        # C)
        c1 = [x[1:] for x in g.get('Frank Trompeter', [])]
        c2 = g.get('Richard Gilman-Opalsky', [])
        print('C) Saxophone:', c1, '| wood flutes:', c2)
        results.append(c1 == [['instrument', 'tenor saxophone', ''], ['instrument', 'alto saxophone', ''], ['instrument', 'soprano saxophone', '']]
                       and c2[-1][1:] == ['instrument', 'flute', 'wood flutes'] and len(c2) == 3)
        d1 = role('Brandon Carnes')
        print('D) Brandon Carnes:', d1)
        results.append(d1 == ['Mixed By', 'Mastered By'])
        # F) [3.29.1]
        f1 = [g.get('Kai Lurk'), g.get('Fen Field')]
        print('F) Kai Lurk, Fen Field:', f1)
        results.append([x[1:] for x in (f1[0] or [])] == [['instrument', 'effects', 'noises'], ['instrument', 'electronic instruments', 'electronics']]
                       and [x[1] for x in (f1[1] or [])] == ['field recordist'])
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        print('E) nicht erkannt:', unrec)
        results.append(not unrec)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_sounds():
    """Credits Importer 3.30.6: "Sounds" – performer or effects, asked (collected item 85; the maintainer's answers of
    2026-10-25 01:59 and 02:28).
    A) Discogs "Sounds": a performer row (R104) with the question "performer, or the instrument effects credited “sounds”?"
       – until answered it stays performer (and would be staged as such); the rule Q008 at the row.
    B) "effects" chosen: the instrument effects with the role credit "sounds" (lower case); "performer" chosen again: back.
    C) A pasted text: "… by K.M. (sounds, words)" and "Sounds: Jane Doe" – both performer with the question."""
    H.attr(9124, 'effects', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.ARTISTS[3050] = (H.uid('dddddddd', 50), 'Sound Person')
    orig = H.discogs_release


    def rel():
        d = orig()
        d['extraartists'].append({'name': 'Sound Person', 'anv': '', 'role': 'Sounds', 'tracks': '', 'id': 3050, 'join': ''})
        return d


    H.discogs_release = rel
    ROW = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => (s.querySelector('.dci-gname strong').dataset.name || s.querySelector('.dci-gname strong').textContent.trim()) === name);
  if (!g) return null; const tr = [...g.querySelectorAll('tr.dci-row')].find(r => /sounds/i.test(r.querySelector('.dci-drole').dataset.raw)) || g.querySelector('tr.dci-row');
  const t = tr.querySelector('[data-f=type]'); const ask = tr.querySelector('.dci-type-ask'); const p = tr.querySelector('[data-f=primary]'); const c = tr.querySelector('[data-f=role-credit]');
  return { id: tr.dataset.row, role: tr.querySelector('.dci-drole').dataset.raw.trim(), type: t ? (t.options[t.selectedIndex] || {}).text : '', primary: p ? p.value : '', credit: c ? c.value : '',
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


def case_members():
    """Credits Importer 3.30.7: the members of a band (collected item 96; https://visionfortune.bandcamp.com/album/iii).
    A) A pasted text, the release's artist Vision Fortune: "Vision Fortune are AC Williams, Alex Townend and Andres Ayerbe" –
       each of the three a performer (S041, T043); "The band is now a trio." and "Vision Fortune is back with a new album."
       give no entry.
    B) Bandcamp, the sentence in the "about" text (which otherwise gives only places): the three performers again; "Vision
       Fortune is back with a new album." there neither."""
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); return [tr.querySelector('.dci-drole').dataset.raw.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', (tr.querySelector('[data-tcount]') || {}).textContent]; })])))()"""
    MEMBERS = ['AC Williams', 'Alex Townend', 'Andres Ayerbe']
    VF = (H.uid('dddddddd', 60), 'Vision Fortune')
    H.ARTISTS[3060] = VF
    H.RELEASE_AC[:] = [(VF[0], 'Vision Fortune', 'Vision Fortune', '')]
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(600)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Vision Fortune are AC Williams, Alex Townend and Andres Ayerbe\nThe band is now a trio.\nVision Fortune is back with a new album.')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        g = pg.evaluate(ROWS)
        a1 = {n: [x[1] for x in g.get(n, [])] for n in MEMBERS}
        print('A) Text:', a1, '| Einträge:', list(g))
        results.append(all(v == ['performer'] for v in a1.values()) and not any(('trio' in k or 'back' in k) for k in g))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()

    # B) Bandcamp, the "about" text
    BAND = 'https://visionfortune.bandcamp.com'
    ALBUM = f'{BAND}/album/iii'
    H.BC_ARTISTS[BAND + '/'] = VF
    TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
    ABOUT = ('Vision Fortune is back with a new album.\nRecorded in a cottage in rural Wales.\n'
             'Vision Fortune are AC Williams, Alex Townend and Andres Ayerbe')
    H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Vision Fortune', 'current': {'title': 'III', 'credits': '', 'about': ABOUT, 'release_date': '02 Oct 2026 00:00:00 GMT'},
                                   'trackinfo': TRACKS}, ALBUM)
    for t in TRACKS:
        url = f'{BAND}{t["title_link"]}'
        H.BC_PAGES[url] = H.bc_html({'artist': 'Vision Fortune', 'album_url': '/album/iii', 'current': {'title': t['title'], 'credits': ''}, 'trackinfo': [t]}, url)
    orig_ws = H.ws_release


    def ws(full=False):
        d = orig_ws(full)
        d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d


    H.ws_release = ws
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(1500)
        g = pg.evaluate(ROWS)
        b1 = {n: [x[1] for x in g.get(n, [])] for n in MEMBERS}
        print('B) Bandcamp „about“:', b1, '| Einträge:', list(g))
        results.append(all(v == ['performer'] for v in b1.values()) and not any('back' in k for k in g))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


GONDOLA = """Chris Lippincott — pedal steel • 3 

Matt Glassmeyer — saxophones • 1, 8 
Wurlitzer • 1, 8 
organ • 1 
horns • 8 
percussion • 1, 4 

Raymond Joseph — synthesizer, bass • 6 

Rich Ruth — synthesizer • 2 

Juan Solorzano — guitars • 2, 7 
zither • 7 

Ross McReynolds – drum programming • 1, 3, 8 
drums • 2 
sampling • 3 
synthesizers • 1, 3, 4, 6, 7, 8, 9 
percussion • 4, 5 
piano • 5 
bass • 8 
guitar • 9 

All songs mixed by Dylan Alledridge, 
Skinny Elephant recording 
All songs mastered by Trevor Richardson 
Recorded all over the place 
Artwork by Micah Mathewson 
Website by Max Helgemo 
and Jacob Dawson-Daley"""
# the rows of each entry: [type, instrument, role credit, tracks]
GON_ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
  [...g.querySelectorAll('tr.dci-row')].map(r => [(r.querySelector('[data-f=type]') || {}).selectedOptions?.[0]?.text || '', (r.querySelector('[data-f=primary]') || {}).value || '',
    (r.querySelector('[data-f=role-credit]') || {}).value || '',
    [...document.querySelectorAll(`tr[data-tracksrow="${r.dataset.row}"] input[data-f=track]:checked`)].map(x => Number(x.dataset.i) + 1).join(',')])])))()"""


def gon_setup():
    H.REC[:] = [H.uid('bbbbbbbb', i) for i in range(1, 10)]
    H.TITLES[:] = ['Song One', 'Song Two', 'Song Three', 'Song Four'] + [f'Piece {i}' for i in range(5, 10)]
    RM = (H.uid('dddddddd', 61), 'Ross McReynolds')
    H.ARTISTS[3061] = RM
    H.RELEASE_AC[:] = [(RM[0], 'Ross McReynolds', 'Ross McReynolds', '')]
    for i, n in [(9310, 'pedal steel guitar'), (9311, 'Wurlitzer electric piano'), (9312, 'organ'), (9313, 'horn'), (9314, 'brass'),
                 (9315, 'percussion'), (9316, 'zither'), (9317, 'sampler')]:
        H.attr(i, n, 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.lt(9993, H.uid('1a1a1a1a', 9993), 'artwork', 'artist', 'release', (1150,))
    H.lt(9995, H.uid('1a1a1a1a', 9995), 'programming', 'artist', 'recording', (1, 526))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}


def gon_read(pg, text):
    H.src_menu(pg, 'text-open')
    pg.fill('[data-f=text-src]', text)
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(1200)
    pg.evaluate("[...document.querySelectorAll('tr.dci-row [data-act=row-open], tr.dci-row .dci-row-open')].forEach(b => b.click())")
    pg.wait_for_timeout(600)
    g = pg.evaluate(GON_ROWS)
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(l => l.textContent.trim())")
    ign = pg.evaluate("[...document.querySelectorAll('.dci-ignored li')].map(l => l.textContent.replace(/\\s+/g, ' ').trim())")
    return g, unrec, ign


def case_gondola():
    """Credits Importer 3.42.3 (collected item Z-GON; rules S069 – S072, question Q013): the credits of Ross McReynolds "Gondola"
    (Bandcamp, https://rossmcreynolds.bandcamp.com/album/gondola) as a pasted text, nine tracks, the release's artist Ross McReynolds.
    A) As on the page: every line read (until 3.42.2 four credits, 22 lines not recognized) – the tracks after "•" (S070), the lines
       of roles below a name his until an empty line ("Wurlitzer • 1, 8" … of Matt Glassmeyer), the en dash like the em dash (Ross
       McReynolds), "All songs mixed by Dylan Alledridge," mix on all tracks without the role credit "All songs", "Skinny Elephant
       recording" below it the place mixed at (S071); "Recorded all over the place", "Website by Max Helgemo" and "and Jacob
       Dawson-Daley" left out on purpose (S072); plurals the instruments of MusicBrainz (saxophone, guitar, synthesizer), sampling →
       sampler, pedal steel → pedal steel guitar, Wurlitzer → Wurlitzer electric piano, horns → horn credited "horns" (Q013: set at
       once, brass to choose); nothing not recognized.
    B) The same text with the companion's status mark "○" before each line (S069): the same entries and rows.
    C) "brass" chosen at the horns: brass, still credited "horns"; the question then offers horn."""
    gon_setup()
    marked = '\n'.join(('○ ' + l) if l.strip() else l for l in GONDOLA.split('\n'))
    ALL = ','.join(str(i) for i in range(1, 10))
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        seen = []
        for label, text in (('A', GONDOLA), ('B', marked)):
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            g, unrec, ign = gon_read(pg, text)
            keep = {k: v for k, v in g.items() if k not in ('Drum Guy', 'Writer W')}
            for k, v in keep.items():
                print(f'  {label}) {k}:', v)
            print(f'  {label}) nicht erkannt:', unrec, '| weggelassen:', ign)
            seen.append(keep)
            prim = lambda n: sorted((r[1] or r[0], r[3]) for r in keep.get(n, []))
            mg = {r[1]: r for r in keep.get('Matt Glassmeyer', [])}
            rm = {(r[1] or r[0]): r for r in keep.get('Ross McReynolds', [])}
            results.append(prim('Chris Lippincott') == [('pedal steel guitar', '3')]
                           and sorted(mg) == ['Wurlitzer electric piano', 'horn', 'organ', 'percussion', 'saxophone']
                           and [mg['saxophone'][3], mg['Wurlitzer electric piano'][3], mg['organ'][3], mg['horn'][3], mg['percussion'][3]] == ['1,8', '1,8', '1', '8', '1,4']
                           and mg['horn'][2] == 'horns'
                           and prim('Raymond Joseph') == [('bass', '6'), ('synthesizer', '6')] and prim('Rich Ruth') == [('synthesizer', '2')]
                           and prim('Juan Solorzano') == [('guitar', '2,7'), ('zither', '7')]
                           and sorted(rm) == ['bass', 'drums (drum set)', 'guitar', 'percussion', 'piano', 'programming', 'sampler', 'synthesizer']
                           and [rm['programming'][3], rm['drums (drum set)'][3], rm['sampler'][3], rm['synthesizer'][3], rm['percussion'][3], rm['piano'][3], rm['bass'][3], rm['guitar'][3]]
                           == ['1,3,8', '2', '3', '1,3,4,6,7,8,9', '4,5', '5', '8', '9'])
            results.append([r[0] for r in keep.get('Dylan Alledridge', [])] == ['mix'] and not any('all songs' in r[2].lower() for r in keep.get('Dylan Alledridge', []))
                           and [r[0] for r in keep.get('Trevor Richardson', [])] == ['mastering'] and [r[0] for r in keep.get('Micah Mathewson', [])] == ['artwork']
                           and [r[0] for r in keep.get('Skinny Elephant recording', [])] == ['mixed at']
                           and not unrec and len(ign) == 3 and ign[0].startswith('Recorded all over the place') and 'no place named' in ign[0]
                           and ign[1].startswith('Website by Max Helgemo') and 'a website' in ign[1] and ign[2].startswith('and Jacob Dawson-Daley')
                           and not any(n in keep for n in ('Max Helgemo', 'Jacob Dawson-Daley', 'All songs')))
            if label == 'A':
                # C) the horns: brass chosen
                ask = pg.evaluate("""(() => { const d = document.querySelector('.dci-bass-ask[data-question=Q013]'); return d ? { text: d.textContent.replace(/\\s+/g, ' ').trim(), btns: [...d.querySelectorAll('button')].map(x => x.textContent.trim()) } : null; })()""")
                pg.evaluate("document.querySelector('.dci-bass-ask[data-question=Q013] [data-act=instr-pick][data-instr=brass]').click()")
                pg.wait_for_timeout(600)
                g2 = pg.evaluate(GON_ROWS)
                ask2 = pg.evaluate("""(() => { const d = document.querySelector('.dci-bass-ask[data-question=Q013]'); return d ? [...d.querySelectorAll('button')].map(x => x.textContent.trim()) : null; })()""")
                horn = [r for r in g2.get('Matt Glassmeyer', []) if r[3] == '8']
                print('C) Frage:', ask, '| brass gewählt:', horn, '| danach:', ask2)
                results.append(bool(ask) and ask['text'].startswith('“horns” is set as horn (credited “horns”) – or as:') and ask['btns'] == ['brass']
                               and [r[1:3] for r in horn] == [['brass', 'horns']] and ask2 == ['horn'])
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        results.append(len(seen) == 2 and seen[0] == seen[1])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


BLACK_ZENITH = """With Black Zenith, Stellarium turns toward the dark geometry of the cosmos, where distant suns dissolve, moons become unfamiliar worlds, and the boundaries of observation begin to blur. From the shifting stars of Mira to the depths of Fornax, these eight compositions trace an enigmatic course through the celestial unknown. At its center lies the black zenith: a point of perfect obscuration, where light and darkness meet, and the universe reveals itself through what it conceals."""


def case_blackzenith():
    """Credits Importer 3.42.3 (collected item Z-BZ; rule S073): the liner notes of Stellarium "Black Zenith" (Bandcamp,
    https://exospheremusic.bandcamp.com/album/black-zenith) – "With Black Zenith, Stellarium turns toward …".
    A) Pasted as a text, the release "Black Zenith" by Stellarium: no entry "Black Zenith" (until 3.42.2 a guest performer) – the line
       is prose; "Special Guest: Black Zenith" gives none either (the release's title is no person), "Special Guest: Mira" none (a
       track's title), "Special Guest: Jane Roe" a guest performer.
    B) Bandcamp, the text as the "about" text of the album "Black Zenith": no entry "Black Zenith" either."""
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
      [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); return t ? (t.options[t.selectedIndex] || {}).text : ''; })])))()"""
    ST = (H.uid('dddddddd', 62), 'Stellarium')
    H.ARTISTS[3062] = ST
    H.RELEASE_AC[:] = [(ST[0], 'Stellarium', 'Stellarium', '')]
    H.REL_TITLE = 'Black Zenith'
    H.TITLES[:] = ['Mira', 'Fornax', 'Song Three', 'Song Four']
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
        pg.fill('[data-f=text-src]', BLACK_ZENITH + '\nSpecial Guest: Black Zenith\nSpecial Guest: Mira\nSpecial Guest: Jane Roe')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        g = pg.evaluate(ROWS)
        print('A) Text:', {k: v for k, v in g.items() if k not in ('Drum Guy', 'Writer W')})
        results.append('Black Zenith' not in g and 'Mira' not in g and g.get('Jane Roe') == ['performer'] and not any('Zenith' in k for k in g))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()

    # B) Bandcamp, the "about" text of the album
    BAND = 'https://exospheremusic.bandcamp.com'
    ALBUM = f'{BAND}/album/black-zenith'
    H.BC_ARTISTS[BAND + '/'] = ST
    TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
    H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Stellarium', 'current': {'title': 'Black Zenith', 'credits': '', 'about': BLACK_ZENITH, 'release_date': '02 Oct 2026 00:00:00 GMT'},
                                   'trackinfo': TRACKS}, ALBUM)
    for t in TRACKS:
        url = f'{BAND}{t["title_link"]}'
        H.BC_PAGES[url] = H.bc_html({'artist': 'Stellarium', 'album_url': '/album/black-zenith', 'current': {'title': t['title'], 'credits': ''}, 'trackinfo': [t]}, url)
    orig_ws = H.ws_release

    def ws(full=False):
        d = orig_ws(full)
        d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d

    H.ws_release = ws
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        # (nothing to import: no "Import complete")
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Bandcamp read/.test(li.textContent))", 90)
        pg.wait_for_timeout(1500)
        g = pg.evaluate(ROWS)
        read = pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(l => l.textContent).find(t => /Bandcamp read/.test(t)) || ''")
        print('B) Bandcamp „about“:', {k: v for k, v in g.items() if k not in ('Drum Guy', 'Writer W')}, '|', read[9:])
        results.append(not any('Zenith' in k for k in g) and 'Bandcamp read: 0 entries' in read)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
