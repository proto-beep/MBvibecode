"""Texts, part 3: titles and areas, credit pairs, the medium of the release, names with initials (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: areas, v3222, medium, initials, placedate (3.32.5) – each the former smoke/t_<case>.py, unchanged; `python3 t_text_places.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_areas():
    """Credits Importer 3.22.0: text recognition, part 2 – tracks named by their titles (collected item 33e; T036, S027) and
    the area where it was recorded (33d; T037, S028, C038 …).
    A) A pasted text: "Recorded by Yunclas in Xixon, Asturies, Spain in the Spring/Summer, 2017" gives Yunclas (recording)
       and an entry of the kind "Area" – Xixon with "(Asturies, Spain)", type "recorded in" on the recordings; MusicBrainz is
       searched with the other names too: Gijón (alias "Xixón") is the first suggestion, with its type and the area it is
       part of; nothing assigned, no "Create", a hint instead. The date pool has 2017.
    B) "Piano in ‘Song One' and 'Song Four' is a contribution by Juanjo Infraser Haller": piano on tracks 1 and 4, the row
       names the titles; "Guitar on “Song Too”: Keith Richards" (one letter off): track 2; "Ana Ruiz – trumpet on 'Song Three'
       and 'Missing Song'": track 3, "Missing Song" not matched.
    C) The suggestion used and staged: MusicBrainz gets "recorded in" between Gijón and the four recordings.
    D) Bandcamp: "Saxophone on 'Song Two' was played by Sam Sax" in the album credits – the album's track 2; "Recorded in
       Berlin, Germany in 2019." in the about text – an area entry (left out with the about text like its places)."""
    GIJON = H.uid('eeeeeeee', 10)
    BERLIN = H.uid('eeeeeeee', 11)
    H.COMPANIES[1010] = ('area', GIJON, 'Gijón')
    H.MB_SEARCH['area'] = [
        {'id': GIJON, 'name': 'Gijón', 'type': 'City', 'disambiguation': '', 'score': 100, 'aliases': [{'name': 'Xixón'}],
         'relations': [{'type': 'part of', 'direction': 'backward', 'area': {'name': 'Asturias'}}]},
        {'id': H.uid('eeeeeeee', 12), 'name': 'Xinxiang', 'type': 'City', 'disambiguation': '', 'score': 60, 'aliases': []},
        {'id': BERLIN, 'name': 'Berlin', 'type': 'City', 'disambiguation': '', 'score': 100, 'aliases': []},
    ]
    H.lt(698, '37ef3a0c-cac3-4172-b09a-4ca98d2857fc', 'recorded in', 'area', 'recording', ())
    H.lt(757, '30adb2d7-dbcb-4393-9230-2098510dd757', 'mastered in', 'area', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.attr(9140, 'trumpet', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    TEXT = """Recorded by Yunclas in Xixon, Asturies, Spain in the Spring/Summer, 2017
Piano in ‘Song One' and 'Song Four' is a contribution by Juanjo Infraser Haller
Guitar on “Song Too”: Keith Richards
Ana Ruiz – trumpet on 'Song Three' and 'Missing Song'"""
    GROUPS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => ({ key: g.dataset.group, kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1],
  name: g.querySelector('.dci-gname strong').textContent.trim(), head: g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(),
  sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()),
  create: g.querySelectorAll('[data-act=company-create]').length, text: g.textContent.replace(/\\s+/g, ' '),
  rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const v = (s) => { const e = tr.querySelector(s); return e ? (e.value !== undefined ? e.value : e.textContent.trim()) : ''; };
    const lv = tr.querySelector('[data-act=level][aria-pressed=true]'); const t = tr.querySelector('[data-f=type]');
    return [v('.dci-drole'), t ? (t.options[t.selectedIndex] || {}).text : '', v('[data-f=primary]'), lv ? lv.dataset.level : '', v('[data-tcount]') || v('.dci-c-tracks .dci-muted'),
      tr.querySelector('.dci-drole').parentElement.textContent.replace(/\\s+/g, ' ').trim()].map(x => String(x).replace(/\\s+/g, ' ').trim()); }) })))()"""
    results = []


    def groups(pg):
        return {x['name']: x for x in pg.evaluate(GROUPS)}


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
        pg.wait_for_timeout(1200)
        g = groups(pg)
        for k, v in g.items():
            print('   ', k, v['kind'], v['sugg'], v['rows'])
        # A)
        xi = g.get('Xixon') or {'rows': [], 'sugg': [], 'head': '', 'create': 1, 'kind': '', 'text': ''}
        pool = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => c.textContent.replace(/\\s+/g, ' ').trim())")
        yun = (g.get('Yunclas') or {'rows': [['']]})['rows']
        print('A) Xixon:', xi['kind'], xi['head'], '| Vorschläge:', xi['sugg'], '| Anlegen:', xi['create'], '| Zeilen:', xi['rows'], '| Yunclas:', yun, '| Pool:', pool)
        ok_a = xi['kind'] == 'area' and 'Area' in xi['head'] and '(Asturies, Spain)' in xi['head'] and xi['sugg'][:1] and xi['sugg'][0].startswith('Gijón') \
            and 'City, Asturias' in xi['sugg'][0] and not any('Xinxiang' in s for s in xi['sugg']) and xi['create'] == 0 \
            and "added by MusicBrainz's area editors only" in xi['text'] and 'dci-st-missing' in pg.evaluate(f"document.querySelector('section[data-group=\"{xi.get('key', '')}\"]').className") \
            and xi['rows'] and xi['rows'][0][:2] == ['Recorded In', 'recorded in'] and xi['rows'][0][3] == 'recording' \
            and yun and yun[0][:2] == ['Recorded By', 'recording'] and any('2017' in x for x in pool)
        # B)
        jj = (g.get('Juanjo Infraser Haller') or {'rows': [['', '', '', '', '', '']]})['rows'][0]
        kr = (g.get('Keith Richards') or {'rows': [['', '', '', '', '', '']]})['rows'][0]
        ana = (g.get('Ana Ruiz') or {'rows': [['', '', '', '', '', '']]})['rows'][0]
        tracks = lambda name: pg.evaluate(f"""(() => {{ const s = [...document.querySelectorAll('section.dci-group')].find(g => g.querySelector('.dci-gname strong').textContent.trim() === '{name}');
      return s ? [...s.querySelectorAll('tr.dci-row [data-trk].dci-on, tr.dci-row .dci-tchip.dci-on')].map(e => e.dataset.trk || e.textContent.trim()) : null; }})()""")
        print('B) Juanjo:', jj, '\n   Keith:', kr, '\n   Ana:', ana)
        ok_b = jj[:3] == ['Piano', 'instrument', 'piano'] and jj[4] == '2 of 4 tracks' and '“Song One”, “Song Four”' in jj[5] \
            and kr[:3] == ['Guitar', 'instrument', 'guitar'] and kr[4] == '1 of 4 tracks' and '“Song Too”' in kr[5] \
            and ana[:3] == ['trumpet', 'instrument', 'trumpet'] and ana[4] == '1 of 4 tracks' and 'Not matched: “Missing Song”' in ana[5]
        # C) the suggestion used, staged
        pg.click(f"section[data-group=\"{xi.get('key', '')}\"] [data-act=name-use]")
        pg.wait_for_timeout(400)
        pg.click('[data-act=apply]')
        pg.wait_for_timeout(3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        staged = pg.evaluate("""MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 698)
      .map(r => { const a = [r.entity0, r.entity1].find(e => e && e.entityType === 'area'); const o = [r.entity0, r.entity1].find(e => e && e.entityType === 'recording');
        return [a ? a.gid : '', o ? o.name : '']; })""")
        print('C) vorgemerkt „recorded in“:', staged)
        ok_c = len(staged) == 4 and all(s[0] == GIJON for s in staged) and sorted(s[1] for s in staged) == sorted(H.TITLES)
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        pg.close()

        # D) Bandcamp
        ALBUM = 'https://testband.bandcamp.com/album/testalbum'
        H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': "Saxophone on 'Song Two' was played by Sam Sax",
                                       'about': 'Recorded in Berlin, Germany in 2019.', 'release_date': '01 Jan 2020 00:00:00 GMT'},
                                       'trackinfo': [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]})
        for i, t in enumerate(H.TITLES):
            H.BC_PAGES[f'https://testband.bandcamp.com/track/song-{i + 1}'] = H.bc_page({'current': {'title': t, 'credits': ''}})
        orig_ws = H.ws_release

        def ws(full=False):
            d = orig_ws(full)
            d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
            for m in d['media']:
                m['format'] = 'Digital Media'
            return d

        H.ws_release = ws
        ctx2 = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx2, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(1200)
        g = groups(pg)
        for k, v in g.items():
            print('   ', k, v['kind'], v['sugg'], v['rows'])
        sam = (g.get('Sam Sax') or {'rows': [['', '', '', '', '', '']]})['rows'][0]
        be = g.get('Berlin') or {'rows': [], 'sugg': [], 'kind': '', 'head': ''}
        print('D) Sam Sax:', sam, '| Berlin:', be['kind'], be['head'], be['sugg'], be['rows'])
        ok_d = sam[:3] == ['Saxophone', 'instrument', 'saxophone'] and sam[4] == '1 of 4 tracks' and '“Song Two”' in sam[5] \
            and be['kind'] == 'area' and '(Germany)' in be['head'] and be['sugg'][:1] and be['sugg'][0].startswith('Berlin') \
            and be['rows'] and be['rows'][0][:2] == ['Recorded In', 'recorded in']
        print('D)', ok_d)
        results.append(ok_d)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_v3222():
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
        H.src_menu(pg, 'text-open')
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


def case_medium():
    """Credits Importer 3.21.4: credits for a medium the release does not have (collected item 39; S026, T035), "Translated by" in
    Bandcamp credits (33h; Q007), the reasons of the lines left out on purpose.
    A release of Digital Media with a Bandcamp album whose credits name vinyl mastering, a lacquer cut and a translation.
    A) Left out (no entry, no row), each with its reason in "… left out on purpose": "Vinyl LP mastering by Sean Price at
       Misery Loves Co." (also the studio, which is only for the vinyl), "Mastered by Max Vinyl (vinyl)", "Lacquer cut by Lou
       Lacquer", "Vinyl master: Vic Master". "Vinyl LP mastering and digital mastering by Dana Digital at Sound House": Dana
       Digital keeps the digital mastering (without "digital" as role credit), Sound House stays.
    B) "Translated by Ana Ruiz" (Bandcamp): no type until chosen, the question offers liner notes (suggested) and translator
       (lyrics); liner notes puts it on the release.
    C) The reasons: "Thanks Mom." – thanks; the vinyl lines – "for Vinyl LP – this release: Digital Media"."""
    H.attr(9120, 'trumpet', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    ALBUM = 'https://testband.bandcamp.com/album/testalbum'
    CREDITS = """Vinyl LP mastering by Sean Price at Misery Loves Co.
Vinyl LP mastering and digital mastering by Dana Digital at Sound House
Mastered by Max Vinyl (vinyl)
Lacquer cut by Lou Lacquer
Vinyl master: Vic Master
Translated by Ana Ruiz
Trumpet: Peter Evans
Thanks Mom."""
    H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': CREDITS, 'about': '', 'release_date': '01 Jan 2020 00:00:00 GMT'},
                                   'trackinfo': [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]})
    for i, t in enumerate(H.TITLES):
        H.BC_PAGES[f'https://testband.bandcamp.com/track/song-{i + 1}'] = H.bc_page({'current': {'title': t, 'credits': ''}})
    orig_ws = H.ws_release


    def ws(full=False):
        d = orig_ws(full)
        d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d


    H.ws_release = ws
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const c = tr.querySelector('[data-f=role-credit]');
    const lv = tr.querySelector('.dci-c-level [aria-pressed=true]');
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', c ? c.value : '',
      (tr.querySelector('.dci-type-ask') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim(), lv ? lv.textContent.trim() : '']; })])))()"""
    IGN = "[...document.querySelectorAll('.dci-ignored li')].map(li => [li.querySelector('.dci-ign-text').textContent, (li.querySelector('.dci-ign-why') || {}).textContent || ''])"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(800)
        src = pg.evaluate("document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').slice(0, 60)")
        g = pg.evaluate(ROWS)
        for k, v in g.items():
            print('   ', k, v)
        ign = pg.evaluate(IGN)
        print('   ausgelassen:', ign)
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'left out' in x]
        print('   Protokoll:', logs)
        # A)
        gone = [n for n in ('Sean Price', 'Misery Loves Co.', 'Max Vinyl', 'Lou Lacquer', 'Vic Master') if n in g]
        dana = g.get('Dana Digital') or []
        ok_a = 'Bandcamp' in src and not gone and len(dana) == 1 and dana[0][1] == 'mastering' and dana[0][2] == '' and 'Sound House' in g \
            and 'Peter Evans' in g and len(logs) == 6
        print('A) Quelle:', src, '| noch da:', gone, '| Dana Digital:', dana, '| Sound House:', 'Sound House' in g, ok_a)
        # B)
        ana = (g.get('Ana Ruiz') or [['', '', '', '', '']])[0]
        sec = "[...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Ana Ruiz')"
        opts = pg.evaluate(f"(() => {{ const s = {sec}; return s ? [...s.querySelectorAll('.dci-type-ask [data-act=type-pick]')].map(b => [b.textContent.replace(/\\s+/g, ' ').trim(), b.classList.contains('dci-type-sugg')]) : []; }})()")
        if opts:
            pg.evaluate(f"{sec}.querySelector('.dci-type-ask [data-act=type-pick][data-opt=\"0\"]').click()")
            pg.wait_for_timeout(500)
        after = (pg.evaluate(ROWS).get('Ana Ruiz') or [['']])[0]
        print('B) Ana Ruiz:', ana[:2], ana[3][:90], '| Wahl:', opts, '| nach „liner notes“:', after[:3], after[4])
        ok_b = ana[1] in ('Choose type …', '') and 'mostly the translation of the liner notes' in ana[3] \
            and opts == [['liner notes suggested', True], ['translator (lyrics)', False]] and after[1] == 'liner notes' and after[2] == 'translation' and after[4] == 'Release'
        # C)
        why = dict(ign)
        ok_c = why.get('Thanks Mom.') == '– thanks' \
            and why.get('Vinyl LP mastering by Sean Price at Misery Loves Co.') == '– for Vinyl LP – this release: Digital Media' \
            and why.get('Mastered by Max Vinyl (vinyl)') == '– for vinyl – this release: Digital Media' \
            and why.get('Lacquer cut by Lou Lacquer') == '– for lacquer cut – this release: Digital Media' \
            and why.get('Vinyl LP mastering and digital mastering by Dana Digital at Sound House') == '– for Vinyl LP – this release: Digital Media' \
            and why.get('Vinyl master: Vic Master') == '– for Vinyl – this release: Digital Media'
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_initials():
    """Import 3.13.0: name suggestions for names with an initial. MusicBrainz's search needs every word of a name, and
    "T" is no word of "Torben" – so a name with an initial is searched with its written-out words too; the comparison
    (same / similar name) decides, a middle name or initial more or less counts as similar.
    A) "T. Snekkestad" → "Torben Snekkestad" (similar name); "Barry J. Guy" → "Barry John Guy" (similar name).
    B) Another first name is no suggestion: "K. Tanaka" → "Kenji Tanaka", not "Hiro Tanaka".
    C) Nothing is assigned by itself; names without an initial need no second search."""
    H.MB_SEARCH['artist'] = [
        {'id': H.uid('dddddddd', 52), 'name': 'Torben Snekkestad', 'disambiguation': '', 'score': 100},
        {'id': H.uid('dddddddd', 51), 'name': 'Barry John Guy', 'disambiguation': 'bassist', 'score': 100},
        {'id': H.uid('dddddddd', 53), 'name': 'Kenji Tanaka', 'disambiguation': '', 'score': 100},
        {'id': H.uid('dddddddd', 54), 'name': 'Hiro Tanaka', 'disambiguation': '', 'score': 100},
        {'id': H.uid('dddddddd', 55), 'name': 'Agustí Fernández', 'disambiguation': 'pianist', 'score': 100},
    ]
    TEXT = """T. Snekkestad – guitar
Barry J. Guy – double bass
K. Tanaka – drums
Agusti Fernández – piano"""
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [[...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()), g.className.match(/dci-st-(\\w+)/)[1]]])))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        queries = []
        pg.on('request', lambda r: queries.append(r.url) if '/ws/2/artist?' in r.url else None)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(800)
        g = pg.evaluate(ROWS)
        for k, v in g.items():
            print('   ', k, v)
        ok_a = g['T. Snekkestad'][0] == ['Torben Snekkestad similar name'] and g['Barry J. Guy'][0] == ['Barry John Guy (bassist) similar name']
        ok_b = g['K. Tanaka'][0] == ['Kenji Tanaka similar name']
        ag = [q for q in queries if 'Fern' in q or 'fern' in q]
        print('A)', ok_a, '| B)', ok_b, '| Anfragen für Agusti:', len(ag))
        ok_c = all(v[1] == 'missing' for v in g.values()) and len(ag) == 1 and g['Agusti Fernández'][0] == ['Agustí Fernández (pianist)']
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_placedate():
    """Credits Importer 3.32.5: a place with a date after it, typos in role words (collected items 117, 115c; S050, T047, T048).
    A) A pasted text "All songs recorded and engineered at El Studio in San Francisco on September 3rd and 4th 2016." gives the
       place El Studio with its area "(San Francisco)" – "recorded at" and "engineered at" (before: nothing, the date took the
       place with it); the date pool has the days (Performance). "Recorded at Studio Sol in Marseille." keeps its area
       (before, "Marseille" was taken for a month and left out).
    B) "Muisc and cover art by Jo Vaman": Jo Vaman with "Music By" (read as Music: composer, a column of the works matrix whose
       head has the rule id S050 with "Read as “Music” (written “Muisc”)") and "Cover art"; nothing not recognized.
    C) ⚙ Settings → Texts: "Typos in role words" is on; switched off (the rule S050 off, stored) and the text loaded again:
       "Muisc …" gives no "Music By" any more and is listed as not recognized; on again (↺ of the tab) → stored as on."""
    H.lt(695, H.uid('eeeeeeee', 695), 'engineered at', 'place', 'recording', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    TEXT = """All songs recorded and engineered at El Studio in San Francisco on September 3rd and 4th 2016.
Recorded at Studio Sol in Marseille.
Muisc and cover art by Jo Vaman"""
    GROUPS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), {
  head: g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(), kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1],
  rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]');
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', (tr.querySelector('.dci-typo') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim()]; }) }])))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)

        def load():
            H.src_menu(pg, 'text-open')
            pg.fill('[data-f=text-src]', TEXT)
            n = pg.evaluate("[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length")
            pg.click('[data-act=text-load]')
            H.wait_for(pg, f"[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length > {n}", 90)
            pg.wait_for_timeout(1200)
            return pg.evaluate(GROUPS)

        g = load()
        for k, v in g.items():
            print('   ', k, v['kind'], v['head'], v['rows'])
        el = g.get('El Studio') or {'rows': [], 'head': '', 'kind': ''}
        sol = g.get('Studio Sol') or {'rows': [], 'head': '', 'kind': ''}
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => d.name + ' ' + JSON.stringify(d.begin) + JSON.stringify(d.end))")
        print('A) El Studio:', el['kind'], el['head'], el['rows'], '| Studio Sol:', sol['head'], '| Pool:', pool)
        ok_a = el['kind'] == 'place' and '(San Francisco)' in el['head'] and sorted(r[1] for r in el['rows']) == ['engineered at', 'recorded at'] \
            and '(Marseille)' in sol['head'] and any('"year":2016,"month":9,"day":3' in x and '"day":4' in x for x in pool)
        jo = (g.get('Jo Vaman') or {'rows': []})['rows']
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        # "Music By" is a role of the works (composer): its rows are in the works matrix – the column head says it
        head = pg.evaluate("""(() => { const th = [...document.querySelectorAll('th.dci-mx-col')].find(t => /Jo Vaman/.test(t.textContent));
          const b = th && th.querySelector('[data-rule=S050]'); return th ? [th.querySelector('.dci-mx-roles').textContent.replace(/\\s+/g, ' ').trim(), b ? b.title : ''] : null; })()""")
        print('B) Jo Vaman:', jo, '| Werk-Matrix:', head, '| nicht erkannt:', unrec)
        ok_b = bool(head) and head[1] == 'Read as “Music” (written “Muisc”)' and head[0].startswith('composer') \
            and any(r[0] == 'Cover art' for r in jo) and not any('Muisc' in u for u in unrec)
        # C) ⚙ Settings → Texts
        H.open_settings(pg, 'texts')
        sw = pg.locator('[data-el=settings] [data-set=rule-on][data-rule=S050]')
        on0 = sw.is_checked()
        sw.uncheck()
        pg.wait_for_timeout(300)
        off = pg.evaluate("JSON.parse(localStorage.getItem('dci-rules-off') || '[]')")
        g2 = load()
        jo2 = (g2.get('Jo Vaman') or {'rows': []})['rows']
        unrec2 = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        H.open_settings(pg, 'texts')
        pg.click('[data-el=settings] [data-act=settings-reset]') if pg.locator('[data-el=settings] [data-act=settings-reset]').count() else None
        pg.wait_for_timeout(300)
        off2 = pg.evaluate("JSON.parse(localStorage.getItem('dci-rules-off') || '[]')")
        print('C) Schalter an:', on0, '| aus gespeichert:', off, '| danach Jo Vaman:', jo2, '| nicht erkannt:', unrec2, '| nach ↺:', off2)
        ok_c = on0 and 'S050' in off and not any(r[0] == 'Music By' for r in jo2) and any('Muisc' in u for u in unrec2) and 'S050' not in off2
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
