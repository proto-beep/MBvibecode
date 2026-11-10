"""Texts, part 3: titles and areas, credit pairs, the medium of the release, names with initials (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: areas, v3222, medium, initials, placedate (3.32.5), recordedin (3.34.18) – each the former smoke/t_<case>.py, unchanged; unawords (3.42.4), kindcycle (3.42.5), unaremember, kindrace, ownrulekind (3.42.8); `python3 t_text_places.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
H.NO_ANIM = True  # [3.77.0] (Z-FLK) reading and mapping: no transitions or animations to wait for
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
  rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const v = (s) => { const e = tr.querySelector(s); return e ? (e.dataset && e.dataset.raw !== undefined ? e.dataset.raw : e.value !== undefined ? e.value : e.textContent.trim()) : ''; };
    const lv = tr.querySelector('[data-act=level][aria-pressed=true]'); const t = tr.querySelector('[data-f=type]');
    return [v('.dci-drole'), t ? (t.options[t.selectedIndex] || {}).text : '', v('[data-f=primary]'), lv ? lv.dataset.level : '', v('[data-tcount]') || v('.dci-c-tracks .dci-muted'),
      ((d) => d.parentElement.textContent.replace(d.textContent, d.dataset.raw))(tr.querySelector('.dci-drole')).replace(/\\s+/g, ' ').trim()].map(x => String(x).replace(/\\s+/g, ' ').trim()); }) })))()"""
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
      return [tr.querySelector('.dci-drole').dataset.raw.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', p ? p.value : '', c ? c.value : '-']; }) }])))()"""
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
    B) "Translated by Ana Ruiz" (Bandcamp): (Z-ENGTR 3.109.0) liner notes on the release at once, no role credit (until 3.108.0 no
       type until chosen, the task "translation"); the question offers liner notes (translator; suggested) and translator (lyrics) and
       stays; liner notes clicked keeps it.
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
    return [tr.querySelector('.dci-drole').dataset.raw.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', c ? c.value : '',
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
        ok_b = ana[1] == 'liner notes' and ana[2] == '' and ana[4] == 'Release' and 'mostly the translation of the liner notes' in ana[3] \
            and opts == [['liner notes (translator) suggested', True], ['translator (lyrics)', False]] and after[1] == 'liner notes' and after[2] == '' and after[4] == 'Release'
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
    return [tr.querySelector('.dci-drole').dataset.raw.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', (tr.querySelector('.dci-typo') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim()]; }) }])))()"""
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
        ok_b = bool(head) and head[1] == 'Read as “Music” (written “Muisc”)' and head[0].lstrip('⚠ ').startswith('composer') \
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


def case_recordedin():
    """Credits Importer 3.34.18: "Recorded in" with a word of places, the year before the month (collected items 137b, 137c;
    T051, T047, D024; the text of Go Kurosawa's "soft shakes" on Bandcamp).
    A) In Node: "2024 January - July", "2024 January–July", "2024 Jan - Jul" → 2024-01 – 2024-07; "2024 March" → 2024-03;
       "2024 March 3" → 2024-03-03 (D017); "2024 March 3–5", "2024 March 30 – April 2" periods; "© 2019 March Records" →
       2019 only; "in 1998 may be" → 1998 only; "March 2024" stays D008.
    B) The dashboard, a pasted text "Recorded in Guruguru Brain studio, Rotterdam, 2024 January - July" and "Mixed at Studio
       Sol, Marseille 2023 March": the place Guruguru Brain studio with its area "(Rotterdam)" – recorded at (before: not
       recognized) – and Studio Sol "(Marseille)" – mixed at (before, the area was left out with the date); the date pool has
       2024-01 – 2024-07 and 2023-03; "Recorded in Berlin" (no word of places) stays the area Berlin, recorded in."""
    import json
    import subprocess

    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const T = ['2024 January - July', '2024 January–July', '2024 Jan - Jul', '2024 March', '2024 March 3', '2024 March 3–5', '2024 March 30 – April 2', '© 2019 March Records', 'in 1998 may be', 'March 2024'];
const v = (d) => [d.value.begin, d.value.end].map((x) => [x.year, x.month, x.day].filter((y) => y != null).join('-')).join('/');
console.log(JSON.stringify(T.map((t) => m.findDates(t).map((d) => [d.rule, v(d)]))));
"""
    a = json.loads(subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True, check=True).stdout)
    want = [[['D024', '2024-1/2024-7']], [['D024', '2024-1/2024-7']], [['D024', '2024-1/2024-7']], [['D024', '2024-3/2024-3']],
            [['D017', '2024-3-3/2024-3-3']], [['D024', '2024-3-3/2024-3-5']], [['D024', '2024-3-30/2024-4-2']], [['D024', '2019/2019']],
            [['D024', '1998/1998']], [['D008', '2024-3/2024-3']]]
    print('A) Node:', a, a == want)
    results = [a == want]
    H.lt(698, '37ef3a0c-cac3-4172-b09a-4ca98d2857fc', 'recorded in', 'area', 'recording', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    TEXT = """Recorded in Guruguru Brain studio, Rotterdam, 2024 January - July
Mixed at Studio Sol, Marseille 2023 March
Recorded in Berlin"""
    GROUPS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), {
  head: g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(), kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1],
  rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); return t ? (t.options[t.selectedIndex] || {}).text : ''; }) }])))()"""
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
        g = pg.evaluate(GROUPS)
        for k, v in g.items():
            print('   ', k, v['kind'], v['head'], v['rows'])
        none = {'rows': [], 'head': '', 'kind': ''}
        gk = g.get('Guruguru Brain studio') or none
        sol = g.get('Studio Sol') or none
        ber = g.get('Berlin') or none
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => JSON.stringify([d.begin, d.end]))")
        print('B) Guruguru:', gk, '| Studio Sol:', sol, '| Berlin:', ber, '| nicht erkannt:', unrec, '| Pool:', pool)
        day = lambda y, m: '{"year":%d,"month":%d,"day":null}' % (y, m)
        results.append(gk['kind'] == 'place' and '(Rotterdam)' in gk['head'] and gk['rows'] == ['recorded at']
                       and sol['kind'] == 'place' and '(Marseille)' in sol['head'] and sol['rows'] == ['mixed at']
                       and ber['kind'] == 'area' and ber['rows'] == ['recorded in'] and not unrec
                       and '[%s,%s]' % (day(2024, 1), day(2024, 7)) in pool and '[%s,%s]' % (day(2023, 3), day(2023, 3)) in pool)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_unawords():
    """Credits Importer 3.42.4 (collected item Z-UNA; Q-dn, Q-dr): words of a line not recognized given an entry. A pasted text of
    four lines no rule reads: "Skinny Elephant recording", "Tracks 2–3: Fable Hall", "Kim Lowe made the sounds", "Part of the Quiet
    Rooms series".
    A) Each word can be clicked; "Skinny", then ⇧ "recording": the three chosen, the form below the line has the name "Skinny Elephant
       recording"; kind place, role "Mixed At", "Remember as a rule of my own" ticked (not ticked at first) → the entry Skinny Elephant
       recording, mixed at on all tracks (the line names none), looked up by its name (MusicBrainz's place offered); its words struck
       through; the own rule U001 (kind "text") stored and listed in "Mapping rules".
    B) "Fable", ⇧ "Hall" (Tracks 2–3): place, "Recorded At", the tracks of the line (2, 3) offered and chosen → recorded at on tracks 2, 3.
    C) "Kim", ⇧ "Lowe": artist (the first kind), no role → "A role is needed."; "Producer" → Kim Lowe producer.
    D) "Quiet", ⇧ "Rooms": series, "part of" → the entry Quiet Rooms, a series – MusicBrainz's series of that name offered.
    E) The text read again: "Skinny Elephant recording" is no line not recognized now – the own rule gives the place, mixed at."""
    H.lt(9996, H.uid('1a1a1a1a', 9996), 'part of', 'release', 'series', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.MB_SEARCH['place'] = H.MB_SEARCH.get('place', []) + [{'id': H.uid('eeeeeeee', 71), 'name': 'Skinny Elephant Recording', 'disambiguation': '', 'score': 100}]
    H.MB_SEARCH['series'] = [{'id': H.uid('eeeeeeee', 72), 'name': 'Quiet Rooms', 'disambiguation': '', 'score': 100}]
    TEXT = """Skinny Elephant recording
Tracks 2–3: Fable Hall
Kim Lowe made the sounds
Part of the Quiet Rooms series"""
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), {
      kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1] || '', sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.trim()).slice(0, 2),
      rows: [...g.querySelectorAll('tr.dci-row')].map(r => [(r.querySelector('[data-f=type]') || {}).selectedOptions?.[0]?.text || '',
        [...document.querySelectorAll(`tr[data-tracksrow="${r.dataset.row}"] input[data-f=track]:checked`)].map(x => Number(x.dataset.i) + 1).join(',')]) }])))()"""
    UNREC = "[...document.querySelectorAll('.dci-unrec li')].map(l => l.textContent.replace(/\\s+/g, ' ').trim())"

    def word(pg, li, text, shift=False):
        pg.evaluate("""([li, text, shift]) => { const w = [...document.querySelectorAll('.dci-unrec li')][li].querySelectorAll('.dci-una-w');
          const el = [...w].find(x => x.textContent === text); el.dispatchEvent(new MouseEvent('click', { bubbles: true, shiftKey: shift })); }""", [li, text, shift])
        pg.wait_for_timeout(300)

    def form(pg):
        return pg.evaluate("""(() => { const f = document.querySelector('.dci-una-form'); if (!f) return null;
          return { name: f.querySelector('[data-f=una-name]').value, kind: f.querySelector('[data-f=una-kind]').value,
            role: (f.querySelector('[data-f=una-role]') || {}).value, roles: [...f.querySelectorAll('select[data-f=una-role] option')].map(o => o.value),
            tracks: [...f.querySelectorAll('[data-f=una-tracks]')].map(x => x.parentElement.textContent.trim() + (x.checked ? ' ✓' : '')),
            rule: f.querySelector('[data-f=una-rule]') ? f.querySelector('[data-f=una-rule]').checked : null,
            sel: [...document.querySelectorAll('.dci-una-sel')].map(x => x.textContent), err: (f.querySelector('.dci-warn') || {}).textContent || '' }; })()""")

    def choose(pg, kind=None, role=None, tracks=None, rule=None):
        if kind:
            pg.select_option('.dci-una-form [data-f=una-kind]', kind)
            pg.wait_for_timeout(300)
        if role is not None:
            if pg.evaluate("document.querySelector('.dci-una-form [data-f=una-role]').tagName") == 'SELECT':
                pg.select_option('.dci-una-form [data-f=una-role]', role)
            else:
                pg.fill('.dci-una-form [data-f=una-role]', role)
        if tracks:
            pg.check(f'.dci-una-form [data-f=una-tracks][value={tracks}]')
        if rule:
            pg.check('.dci-una-form [data-f=una-rule]')

    def add(pg):
        pg.click('.dci-una-form [data-act=una-apply]')
        pg.wait_for_timeout(1500)

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
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=text-load]')
        # (nothing recognized: no "Import complete")
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Text read/.test(li.textContent))", 90)
        pg.wait_for_timeout(1000)
        pg.evaluate("document.querySelector('.dci-unrec').open = true")
        u0 = pg.evaluate(UNREC)
        nwords = pg.evaluate("document.querySelectorAll('.dci-unrec .dci-una-w').length")
        print('Zeilen:', u0, '| Wörter:', nwords)
        results.append(u0 == ['Skinny Elephant recording', 'Tracks 2–3: Fable Hall', 'Kim Lowe made the sounds', 'Part of the Quiet Rooms series'] and nwords == 18)
        # A)
        word(pg, 0, 'Skinny')
        word(pg, 0, 'recording', shift=True)
        fa = form(pg)
        choose(pg, kind='place', role='Mixed At', rule=True)
        fa2 = form(pg)
        add(pg)
        g = pg.evaluate(ROWS)
        done = pg.evaluate("[...document.querySelectorAll('.dci-unrec .dci-una-done')].map(x => x.textContent)")
        rules = pg.evaluate("JSON.parse(localStorage.getItem('dci-user-rules') || '[]')")
        print('A) Form:', fa, '→', fa2, '\n   Eintrag:', g.get('Skinny Elephant recording'), '| erledigt:', done, '| Regeln:', rules)
        results.append(fa and fa['name'] == 'Skinny Elephant recording' and fa['sel'] == ['Skinny', 'Elephant', 'recording'] and fa['kind'] == 'artist' and fa['rule'] is False
                       and fa2['roles'][:3] == ['Recorded At', 'Mixed At', 'Mastered At'] and fa2['tracks'] == []
                       and (g.get('Skinny Elephant recording') or {}).get('rows') == [['mixed at', '1,2,3,4']]
                       and 'Skinny Elephant Recording' in ' '.join((g.get('Skinny Elephant recording') or {}).get('sugg', []))
                       and done == ['Skinny', 'Elephant', 'recording']
                       and [(r['id'], r['kind'], r['phrase'], r['entity'], r['role'], r['tracks']) for r in rules] == [('U001', 'text', 'Skinny Elephant recording', 'place', 'Mixed At', 'release')])
        # B)
        word(pg, 1, 'Fable')
        word(pg, 1, 'Hall', shift=True)
        choose(pg, kind='place', role='Recorded At')
        fb = form(pg)
        choose(pg, tracks='line')
        add(pg)
        g = pg.evaluate(ROWS)
        print('B) Form:', fb, '| Eintrag:', g.get('Fable Hall'))
        results.append(fb['tracks'] == ['the tracks of the line (2, 3) ✓', 'the whole release'] and (g.get('Fable Hall') or {}).get('rows') == [['recorded at', '2,3']])
        # C)
        word(pg, 2, 'Kim')
        word(pg, 2, 'Lowe', shift=True)
        add(pg)
        fc = form(pg)
        choose(pg, role='Producer')
        add(pg)
        g = pg.evaluate(ROWS)
        print('C) ohne Rolle:', fc, '| Eintrag:', g.get('Kim Lowe'))
        results.append(fc and fc['err'] == 'A role is needed.' and (g.get('Kim Lowe') or {}).get('rows') == [['producer', '1,2,3,4']])
        # D)
        word(pg, 3, 'Quiet')
        word(pg, 3, 'Rooms', shift=True)
        choose(pg, kind='series')
        fd = form(pg)
        add(pg)
        g = pg.evaluate(ROWS)
        print('D) Form:', fd, '| Eintrag:', g.get('Quiet Rooms'))
        q = g.get('Quiet Rooms') or {}
        results.append(fd['roles'] == ['part of'] and fd['rule'] is None and q.get('kind') == 'other' and [r[0] for r in q.get('rows', [])] == ['part of']
                       and any('Quiet Rooms' in x for x in q.get('sugg', [])))
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'added from a line not recognized' in x or 'Own rule U001' in x]
        # the rules window lists the own rule of texts
        pg.locator('[data-act=rules]').first.click()
        pg.wait_for_selector('#dci-rules [data-rsect=own]')
        own = pg.evaluate("[...document.querySelectorAll('#dci-rules [data-rsect=own] tr[data-urule-kind=text] td')].map(t => t.textContent.trim()).filter(Boolean)")
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
        print('   Log:', logs, '| Regelfenster:', own)
        results.append(len(logs) == 5 and own == ['U001', 'Text phrase → entry', '“Skinny Elephant recording”', 'place · Mixed At', 'delete'])
        # E) read again: the own rule
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Text read/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        g = pg.evaluate(ROWS)
        u1 = pg.evaluate(UNREC)
        print('E) wieder gelesen:', g.get('Skinny Elephant recording'), '| nicht erkannt:', u1)
        results.append((g.get('Skinny Elephant recording') or {}).get('rows') == [['mixed at', '1,2,3,4']] and not any('Skinny' in x for x in u1) and len(u1) == 3)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_kindcycle():
    """Credits Importer 3.42.5 (collected item Z-ETC; Q-dd): the kind of an entry not linked tried in turn. A pasted text "Mastered at
    Quiet Lab" (mastered at: a label, a place or an artist – mastering) and "Recorded in Elsewhere Town" (an area only); MusicBrainz has
    a label Quiet Lab.
    A) The head of Quiet Lab has the button "Label ↻" (↻ drawn by the style: its text "Label"; its title names the kinds in turn: label → place → artist), the label offered;
       Elsewhere Town keeps the tag "Area" (no other kind has its role).
    B) A click: "Place ↻" and "searching in a second …"; a second click within the second: "Artist ↻" – then one search, of artists
       (none of places); the row is mastering.
    C) A click: "Label ↻" – the label of the import offered again, no search; a click: "Place ↻", searched as a place.
    D) Two clicks (artist, label): no search – what was found before; the label chosen: the entry linked, the tag no button."""
    H.MB_SEARCH['label'] = H.MB_SEARCH.get('label', []) + [{'id': H.uid('eeeeeeee', 81), 'name': 'Quiet Lab', 'disambiguation': '', 'score': 100}]
    TEXT = """Mastered at Quiet Lab
Recorded in Elsewhere Town"""
    HEAD = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name); if (!g) return null;
      const t = g.querySelector('.dci-kind-tag'); return { tag: t.textContent.trim(), button: t.tagName === 'BUTTON', title: t.title || '', wait: !!g.querySelector('.dci-etc-wait'),
        sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.trim()),
        rows: [...g.querySelectorAll('tr.dci-row')].map(r => (r.querySelector('[data-f=type]') || {}).selectedOptions?.[0]?.text || '') }; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        searches = []
        pg.on('request', lambda r: searches.append(r.url.split('/ws/2/')[1].split('?')[0]) if '/ws/2/' in r.url and 'query=' in r.url else None)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1500)
        a = pg.evaluate(HEAD, 'Quiet Lab')
        e = pg.evaluate(HEAD, 'Elsewhere Town')
        print('A)', a, '|', e)
        results.append(a and a['button'] and a['tag'] == 'Label' and 'label → place → artist' in a['title'] and a['sugg'] == ['Quiet Lab – label']
                       and e and not e['button'] and e['tag'] == 'Area')
        click = lambda: pg.click('section.dci-group .dci-kind-cycle')
        n0 = len(searches)
        click()
        pg.wait_for_timeout(300)
        b1 = pg.evaluate(HEAD, 'Quiet Lab')
        click()
        pg.wait_for_timeout(300)
        b2 = pg.evaluate(HEAD, 'Quiet Lab')
        pg.wait_for_timeout(2500)
        b3 = pg.evaluate(HEAD, 'Quiet Lab')
        print('B)', b1['tag'], b1['wait'], '|', b2['tag'], b2['wait'], '|', b3, '| Suchen:', searches[n0:])
        results.append(b1['tag'] == 'Place' and b1['wait'] and b2['tag'] == 'Artist' and b3['tag'] == 'Artist' and not b3['wait'] and b3['rows'] == ['mastering']
                       and searches[n0:] == ['artist'])
        n1 = len(searches)
        click()
        pg.wait_for_timeout(1500)
        c1 = pg.evaluate(HEAD, 'Quiet Lab')
        s_c1 = searches[n1:]
        click()
        pg.wait_for_timeout(2800)
        c2 = pg.evaluate(HEAD, 'Quiet Lab')
        print('C)', c1['tag'], c1['sugg'], s_c1, '|', c2['tag'], '| Suchen:', searches[n1:])
        results.append(c1['tag'] == 'Label' and c1['sugg'] == ['Quiet Lab – label'] and not c1['wait'] and s_c1 == []
                       and c2['tag'] == 'Place' and searches[n1:][:1] == ['place'] and 'label' not in searches[n1:] and 'artist' not in searches[n1:])
        n2 = len(searches)
        click()
        pg.wait_for_timeout(200)
        click()
        pg.wait_for_timeout(1500)
        d0 = pg.evaluate(HEAD, 'Quiet Lab')
        pg.locator('section.dci-group [data-act=name-use]', has_text='Quiet Lab').first.click()
        pg.wait_for_timeout(800)
        d = pg.evaluate(HEAD, 'Quiet Lab')
        print('D)', d0['tag'], d0['sugg'], '→', d, '| Suchen:', searches[n2:])
        results.append(d0['tag'] == 'Label' and searches[n2:] == [] and d and not d['button'] and d['tag'] == 'Label')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_unaremember():
    """Credits Importer 3.42.8 (review of Block BG): what was done with "Remember changes …" (⚙ Cache) on, the page loaded again and
    the same text pasted again:
    A) The words given an entry come back – Fable Hall recorded at on the tracks of its line (2, 3; track 3 taken out before: so
       again, track 2), the series Quiet Rooms (until 3.42.7 both were lost, "remembered changes left out"); their words struck through.
    B) A row added by hand with the role of a row of the source ("＋ Another role" at Bob Mix: "Mixed By" a second time) stays (from
       3.42.4 until the review it was taken as the same and left out).
    C) Nothing "left out" in the log."""
    H.REMEMBER = True
    H.lt(9996, H.uid('1a1a1a1a', 9996), 'part of', 'release', 'series', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.MB_SEARCH['series'] = [{'id': H.uid('eeeeeeee', 72), 'name': 'Quiet Rooms', 'disambiguation': '', 'score': 100}]
    TEXT = """Tracks 2–3: Fable Hall
Part of the Quiet Rooms series
Mixed by Bob Mix"""
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), {
      kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1] || '',
      rows: [...g.querySelectorAll('tr.dci-row')].map(r => [(r.querySelector('[data-f=type]') || {}).selectedOptions?.[0]?.text || '', (r.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level || '',
        [...document.querySelectorAll(`tr[data-tracksrow="${r.dataset.row}"] input[data-f=track]:checked`)].map(x => Number(x.dataset.i) + 1).join(',')]) }])))()"""

    def word(pg, li, text, shift=False):
        pg.evaluate("""([li, text, shift]) => { const w = [...document.querySelectorAll('.dci-unrec li')][li].querySelectorAll('.dci-una-w');
          [...w].find(x => x.textContent === text).dispatchEvent(new MouseEvent('click', { bubbles: true, shiftKey: shift })); }""", [li, text, shift])
        pg.wait_for_timeout(300)

    def paste(pg, n):
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, f"[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= {n}", 90)
        pg.wait_for_timeout(1500)
        pg.evaluate("document.querySelector('.dci-unrec') && (document.querySelector('.dci-unrec').open = true)")
        pg.evaluate("[...document.querySelectorAll('tr.dci-row [data-act=row-open], tr.dci-row .dci-row-open')].forEach(b => { if (b.getAttribute('aria-expanded') !== 'true') b.click(); })")
        pg.wait_for_timeout(500)

    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())

        def start():
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        start()
        paste(pg, 2)
        word(pg, 0, 'Fable')
        word(pg, 0, 'Hall', shift=True)
        pg.select_option('.dci-una-form [data-f=una-kind]', 'place')
        pg.wait_for_timeout(300)
        pg.select_option('.dci-una-form [data-f=una-role]', 'Recorded At')
        pg.check('.dci-una-form [data-f=una-tracks][value=line]')
        pg.click('.dci-una-form [data-act=una-apply]')
        pg.wait_for_timeout(1500)
        word(pg, 1, 'Quiet')
        word(pg, 1, 'Rooms', shift=True)
        pg.select_option('.dci-una-form [data-f=una-kind]', 'series')
        pg.wait_for_timeout(300)
        pg.click('.dci-una-form [data-act=una-apply]')
        pg.wait_for_timeout(1500)
        # Fable Hall's row without track 3 (a change of it)
        pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Fable Hall');
          const r = g && g.querySelector('tr.dci-row'); const c = r && document.querySelector(`tr[data-tracksrow="${r.dataset.row}"] input[data-f=track][data-i="2"]`); if (c) c.click(); })()""")
        pg.wait_for_timeout(400)
        # B) "＋ Another role" at Bob Mix: "Mixed By" once more
        key = pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bob Mix').dataset.group")
        pg.click(f'section.dci-group[data-group="{key}"] [data-act=add-role]')
        pg.click('[data-el=arq] [data-act=arq-free]')  # ([Z-ARQ] 3.86.0) the role typed by hand
        pg.wait_for_timeout(400)
        pg.locator(f'section.dci-group[data-group="{key}"] [data-f=role-text]').last.fill('Mixed By')
        pg.locator(f'section.dci-group[data-group="{key}"] [data-f=role-text]').last.press('Tab')
        pg.wait_for_timeout(800)
        a0 = pg.evaluate(ROWS)
        pg.wait_for_timeout(2000)
        print('vorher:', {k: v for k, v in a0.items() if k in ('Fable Hall', 'Quiet Rooms', 'Bob Mix')})
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        start()
        paste(pg, 2)
        a1 = pg.evaluate(ROWS)
        done = pg.evaluate("[...document.querySelectorAll('.dci-unrec .dci-una-done')].map(x => x.textContent)")
        lost = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'left out' in x]
        print('nachher:', {k: v for k, v in a1.items() if k in ('Fable Hall', 'Quiet Rooms', 'Bob Mix')}, '| erledigt:', done, '| ausgelassen:', lost)
        fh, qr, bm = a1.get('Fable Hall') or {}, a1.get('Quiet Rooms') or {}, a1.get('Bob Mix') or {}
        results.append(fh.get('rows') == [['recorded at', 'recording', '2']] and (a0.get('Fable Hall') or {}).get('rows') == [['recorded at', 'recording', '2']])
        results.append(qr.get('kind') == 'other' and [r[0] for r in qr.get('rows', [])] == ['part of'] and done == ['Fable', 'Hall', 'Quiet', 'Rooms'])
        results.append([r[0] for r in bm.get('rows', [])] == ['mix', 'mix'] and not lost)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_kindrace():
    """Credits Importer 3.42.8 (review of Block BG): a search of the kind cycle that comes back after the kind was clicked on. "Mastered at
    Quiet Lab" (MusicBrainz has a label and a place of that name; the places answer after 2.5 s): Label → Place (searched), → Artist,
    → Label (found before) while the places are still on their way – then still the label offered (until the review the places were
    shown under "Label" and kept for it), no "searching" left; Place again: the places, no new search."""
    H.MB_SEARCH['label'] = H.MB_SEARCH.get('label', []) + [{'id': H.uid('eeeeeeee', 81), 'name': 'Quiet Lab', 'disambiguation': '', 'score': 100}]
    H.MB_SEARCH['place'] = H.MB_SEARCH.get('place', []) + [{'id': H.uid('eeeeeeee', 82), 'name': 'Quiet Lab', 'disambiguation': '', 'score': 100}]
    HEAD = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name); if (!g) return null;
      const t = g.querySelector('.dci-kind-tag'); return { tag: t.textContent.trim(), wait: !!g.querySelector('.dci-etc-wait'), sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.trim()) }; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        searches = []
        pg.on('request', lambda r: searches.append(r.url.split('/ws/2/')[1].split('?')[0]) if '/ws/2/' in r.url and 'query=' in r.url else None)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Mastered at Quiet Lab')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1500)
        # the places answer late
        pg.evaluate("""(() => { const f = window.fetch; window.fetch = (u, o) => (/\\/ws\\/2\\/place\\?query/.test(String(u)) ? new Promise((r) => setTimeout(r, 2500)).then(() => f(u, o)) : f(u, o)); })()""")
        a0 = pg.evaluate(HEAD, 'Quiet Lab')
        click = lambda: pg.click('section.dci-group .dci-kind-cycle')
        click()
        pg.wait_for_timeout(1400)
        click()
        pg.wait_for_timeout(150)
        click()
        pg.wait_for_timeout(300)
        a1 = pg.evaluate(HEAD, 'Quiet Lab')
        pg.wait_for_timeout(3500)
        a2 = pg.evaluate(HEAD, 'Quiet Lab')
        n = len(searches)
        click()
        pg.wait_for_timeout(1800)
        a3 = pg.evaluate(HEAD, 'Quiet Lab')
        print('A)', a0, '| gleich danach:', a1, '| nach den Orten:', a2, '| Place wieder:', a3, searches[n:])
        results.append(a0['tag'] == 'Label' and a1['tag'] == 'Label' and a2['tag'] == 'Label' and a2['sugg'] == ['Quiet Lab – label'] and not a2['wait']
                       and a3['tag'] == 'Place' and a3['sugg'] == ['Quiet Lab – place'] and searches[n:] == [])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ownrulekind():
    """Credits Importer 3.42.8 (review of Block BG): an own rule of texts with its kind – "Quiet Lab" as a place, mastered at (a role a
    label has too): the entry of a text naming it is a place (until the review the role decided: a label)."""
    TEXT = 'Quiet Lab'
    HEAD = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      return g ? [g.querySelector('.dci-kind-tag').textContent.trim(), [...g.querySelectorAll('tr.dci-row')].map(r => (r.querySelector('[data-f=type]') || {}).selectedOptions?.[0]?.text || '')] : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("""localStorage.setItem('dci-user-rules', JSON.stringify([{ id: 'U001', kind: 'text', on: true, discogs: 'quiet lab', phrase: 'Quiet Lab', entity: 'place', role: 'Mastered At', tracks: 'release' }]))""")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1500)
        a = pg.evaluate(HEAD, 'Quiet Lab')
        print('A)', a)
        results.append(a is not None and a[0] == 'Place')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_z379():
    """Credits Importer 3.79.0 (collected items Z-KXP, Z-CAM2, Z-VEN, Z-MEM, Z-PHC).
    A) In Node (D027): "9/17/26" → 2026-09-17 (the 17 decides: month first), "17/9/26" → 2026-09-17, "9/17/99" → 1999-09-17.
    B) The description of a KEXP video: "… performing live in the KEXP studio. Recorded April 8, 2025." gives the place KEXP Studio
       (recorded at, S112 – before: not recognized); "Cameras: Jim Beckmann, Carlos Cruz & Scott Holpainen with Luke Knecht": four
       names (S116), each miscellaneous support on the recordings with the task "cameras" (R110); its levels Recording | Release only.
    C) "venue: industry city" / "brooklyn, NY" / "9/17/26" (S115): the place Industry City "(Brooklyn)", recorded at; the pool has
       2026-09-17 (and the city as the area of the place); the lines are not listed as not recognized.
    D) "Salisman Communal Orchestration:" with four names below it (S113): three of them asked "performer on the recordings, or no
       relationship?" (nothing added before), the fourth – guitar elsewhere in the text – not; answered "performer": the row is a
       performer on the recordings. The group itself only with S114 (E).
    E) S114 on: the group asked too.
    F) D026 on: "Photography [Live]: Jane Photo" with a concert "Recorded live at Café Oto, London, 12 May 2019": the row of the
       photographs has the concert's date (without D026 only suggested – t_notes_dates.py artkinds)."""
    import json
    import subprocess

    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const v = (d) => [d.value.begin].map((x) => [x.year, x.month, x.day].filter((y) => y != null).join('-')).join('/');
console.log(JSON.stringify(['9/17/26', '17/9/26', '9/17/99'].map((t) => m.findDates(t).map((d) => [d.rule, v(d)]))));
"""
    a = json.loads(subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True, check=True).stdout)
    print('A) Node:', a)
    results = [a == [[['D027', '2026-9-17']], [['D027', '2026-9-17']], [['D027', '1999-9-17']]]]
    GROUPS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), {
  head: g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(), kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1],
  rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); return { type: t ? (t.options[t.selectedIndex] || {}).text : '',
    level: ((tr.className.match(/dci-lv-(\\w+)/) || [])[1]) || '', levels: [...tr.querySelectorAll('[data-act=level]')].map(x => x.dataset.level),
    credit: (tr.querySelector('[data-f=role-credit]') || {}).value || '', ask: (tr.querySelector('.dci-type-ask') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim().slice(0, 90),
    q: (tr.querySelector('.dci-type-ask') || { dataset: {} }).dataset.question || '' }; }) }])))()"""
    UNREC = "[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)"
    # (MusicBrainz names the type of miscellaneous support "misc")
    H.lt(129, H.LTS[129]['gid'], 'misc', 'artist', 'recording', (1150,))
    H.lt(63, H.LTS[63]['gid'], 'misc', 'artist', 'release', (1150,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}

    def load(pg, text):
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', text)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, f"[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= {load.n}", 90)
        load.n += 1
        pg.wait_for_timeout(800)
        return pg.evaluate(GROUPS)

    KEXP = """http://KEXP.ORG presents maya ongaku performing live in the KEXP studio. Recorded April 8, 2025.

Cameras: Jim Beckmann, Carlos Cruz & Scott Holpainen with Luke Knecht"""
    VENUE = """venue: industry city
brooklyn, NY
9/17/26"""
    MEM = """Salisman Communal Orchestration:
Sean Burke
Paul Foreman
Kevin Pulaski
Travis Salisbury

Paul Foreman - guitar"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        load.n = 2
        g = load(pg, KEXP)
        ks = g.get('KEXP Studio') or {'kind': '', 'rows': []}
        cams = {n: (g.get(n) or {'rows': [{}]})['rows'][0] for n in ['Jim Beckmann', 'Carlos Cruz', 'Scott Holpainen', 'Luke Knecht']}
        unrec = pg.evaluate(UNREC)
        print('B) KEXP Studio:', ks, '| Kameras:', cams, '| nicht erkannt:', unrec)
        results.append(ks['kind'] == 'place' and [r['type'] for r in ks['rows']] == ['recorded at'] and not any('KEXP' in x for x in unrec)
                       and all(c.get('type') in ('misc', 'miscellaneous support') and c.get('level') == 'recording' and c.get('credit') == 'cameras' and c.get('levels') == ['recording', 'release', 'skip'] for c in cams.values()))
        g = load(pg, VENUE)
        ic = g.get('Industry City') or {'kind': '', 'rows': [], 'head': ''}
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => [d.begin.year, d.begin.month, d.begin.day].join('-'))")
        unrec = pg.evaluate(UNREC)
        print('C) Industry City:', ic, '| Pool:', pool, '| nicht erkannt:', unrec)
        results.append(ic['kind'] == 'place' and '(Brooklyn' in ic['head'] and [r['type'] for r in ic['rows']] == ['recorded at'] and '2026-9-17' in pool and not unrec)
        g = load(pg, MEM)
        asked = {n: (g.get(n) or {'rows': [{}]})['rows'] for n in ['Sean Burke', 'Paul Foreman', 'Kevin Pulaski', 'Travis Salisbury', 'Salisman Communal Orchestration']}
        print('D) Mitglieder:', {n: [(r.get('q'), r.get('level'), r.get('type')) for r in rows] for n, rows in asked.items()})
        ok_d = all(len(asked[n]) == 1 and asked[n][0].get('q') == 'Q013' and 'performer on the recordings' in asked[n][0].get('ask', '') for n in ['Sean Burke', 'Kevin Pulaski', 'Travis Salisbury']) \
            and [r.get('q') for r in asked['Paul Foreman']] == [''] and not g.get('Salisman Communal Orchestration')
        row = pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text='Sean Burke')).first.locator('tr.dci-row').first
        row.locator('.dci-type-ask [data-act=type-pick][data-opt="0"]').click()
        pg.wait_for_timeout(500)
        sean = pg.evaluate(GROUPS).get('Sean Burke', {'rows': [{}]})['rows'][0]
        print('   Sean Burke beantwortet:', sean)
        results.append(ok_d and sean.get('type') == 'performer' and sean.get('level') == 'recording')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
        # E) S114 on; F) D026 on
        H.RULES_OFF = ['S083', '+S114', '+D026']
        # (one concert: no dates of the Discogs notes beside it)
        orig = H.discogs_release

        def rel():
            d = orig()
            d['notes'] = ''
            return d
        H.discogs_release = rel
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        load.n = 2
        g = load(pg, MEM)
        grp = (g.get('Salisman Communal Orchestration') or {'rows': [{}]})['rows']
        print('E) S114 – die Gruppe:', [(r.get('q'), r.get('ask')) for r in grp])
        results.append(len(grp) == 1 and grp[0].get('q') == 'Q013')
        g = load(pg, "Recorded live at Café Oto, London, 12 May 2019\nPhotography [Live]: Jane Photo")
        ph = pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text='Jane Photo')).first.locator('tr.dci-row').first
        from common_rows import date_field
        f = (date_field(ph, 'rd-by'), date_field(ph, 'rd-bm'), date_field(ph, 'rd-bd'))
        print('F) D026 – Fotos des Konzerts:', f, '| Fehler:', errs)
        results.append(f == ('2019', '05', '12') and not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_z381ui():
    """Credits Importer 3.81.0 (collected items Z-RAD, Z-POR, Z-SYN, Z-SLD) in the dashboard, from a pasted text.
    A) "This was recorded by Norwegian State radio, at the Hennie-Onstad art centre outside Oslo on September 11th 1983. …": Norwegian
       State radio a label (S121) with two rows – recording and broadcast, on the recordings; no role credit "This was" (until 3.80.0
       a person "recording" credited "This was"); "… Rutherford and Guy. At the time …" gives no Guy; the place Hennie-Onstad art centre
       (its area Oslo).
    B) "Album portraits by Selina Mayer": photography on the release, credited "album portraits" (R112).
    C) "Tsinder Ash - Juno 101, Korg Minilogue, Roland TR-808, Appalachian/Hammered Dulcimer": synthesizer credited "Juno 101", synthesizer
       credited "Korg Minilogue", drum machine credited "Roland TR-808" (R113); Appalachian dulcimer and hammered dulcimer (S119);
       nothing not recognized."""
    GROUPS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), {
  kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1] || '', etype: (g.querySelector('.dci-gname .dci-sub') || { textContent: '' }).textContent.trim(),
  rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); return [t ? (t.options[t.selectedIndex] || {}).text : '',
    ((tr.className.match(/dci-lv-(\\w+)/) || [])[1]) || '', (tr.querySelector('[data-f=primary]') || {}).value || '', (tr.querySelector('[data-f=role-credit]') || {}).value || '']; }) }])))()"""
    UNREC = "[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)"
    for i, n in ((9381, 'Appalachian dulcimer'), (9382, 'hammered dulcimer'), (9383, 'drum machine'), (9384, 'sampler')):
        H.attr(i, n, 14, 14)
    H.lt(9385, H.uid('1a1a1a1a', 9385), 'recording', 'label', 'recording', ())
    H.lt(9386, H.uid('1a1a1a1a', 9386), 'broadcast', 'label', 'recording', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    TEXT = """This was recorded by Norwegian State radio, at the Hennie-Onstad art centre outside Oslo on September 11th 1983. The first time I played with Rutherford and Guy. At the time I played soprano and tenor sax.

Album portraits by Selina Mayer

Tsinder Ash - Juno 101, Korg Minilogue, Roland TR-808, Appalachian/Hammered Dulcimer"""
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
        H.wait_still(pg, "document.body.innerHTML", 15, 300)
        g = pg.evaluate(GROUPS)
        unrec = pg.evaluate(UNREC)
        for k, v in g.items():
            print('  ', k, v)
        print('   nicht erkannt:', unrec)
        credited = pg.evaluate("[...document.querySelectorAll('section.dci-group [data-f=credit]')].map(x => x.value).filter(Boolean)")
        print('   Credited as:', credited)
        radio = g.get('Norwegian State radio') or {'rows': [], 'kind': ''}
        # (the names after "by" end with their sentence: no Guy; the place "outside Oslo" with its area)
        results.append('Guy' not in g and 'Hennie-Onstad art centre' in g and not any('This was' in x for x in credited) and radio['kind'] == 'label')
        results.append(sorted(r[0] for r in radio['rows']) == ['broadcast', 'recording'] and all(r[1] == 'recording' and r[3] == '' for r in radio['rows'])
                       and not any('This was' in r[3] for v in g.values() for r in v['rows']))
        sm = (g.get('Selina Mayer') or {'rows': [[]]})['rows']
        results.append(sm == [['photography', 'release', '', 'album portraits']])
        ta = sorted(((g.get('Tsinder Ash') or {'rows': []})['rows']), key=lambda r: (r[2], r[3]))
        results.append(ta == sorted([['instrument', 'recording', 'synthesizer', 'Juno 101'], ['instrument', 'recording', 'synthesizer', 'Korg Minilogue'],
                                     ['instrument', 'recording', 'drum machine', 'Roland TR-808'], ['instrument', 'recording', 'Appalachian dulcimer', ''],
                                     ['instrument', 'recording', 'hammered dulcimer', '']], key=lambda r: (r[2], r[3])) and not any('Tsinder' in u for u in unrec))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_btw384():
    """Credits Importer 3.84.0 (collected items Z-WPR, Z-BTW, Z-DEDN, Z-PGF; rules S126 – S128, D007, C045): the text of a Bandcamp
    album (cyclicaldreams, "Inner Space"), pasted.
    A) "All tracks written, performed and recorded by Wojciech Stecko": writer, performer, recording – "All tracks" no part of the
       credit; "Music production, mix, mastering: Wojciech Stecko (Mindheal)": producer (R026 "music production"), mix, mastering.
    B) "(Mindheal)" his artist name: the entry is Wojciech Stecko (the name as written), MusicBrainz's "Mindheal" a similar
       suggestion, a note says an artist under the full name may be cleaner.
    C) "Tracks were composed and produced between February 2025 and April 2026 in Rzeszow, Poland.": Rzeszow composed in (works,
       C045) and produced in (recordings); the date one period 2025-02 – 2026-04 (D007; until 3.83.0 two months of their own) for
       the groups Composition and Production – columns of the date matrix now ([Z-DPD] 3.95.0: one entry of the pool for both,
       "Production · Composition 1").
    D) "This album is dedicated to my lovely daughter and son.": left out on purpose, "a dedication without a name" (S128).
    E) The bar on the release page has a frame on all four sides (Z-PGF; until 3.83.0 a line below it)."""
    H.lt(875, '1d4c0b5b-0000-4000-8000-000000000875', 'composed in', 'area', 'work', ())
    H.lt(1101, '1d4c0b5b-0000-4000-8000-000000001101', 'produced in', 'area', 'recording', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    RZ, MH = H.uid('eeeeeeee', 384), H.uid('dddddddd', 384)
    H.MB_SEARCH['area'] = [{'id': RZ, 'name': 'Rzeszów', 'type': 'City', 'disambiguation': '', 'score': 100, 'aliases': [{'name': 'Rzeszow'}]}]
    H.ARTISTS[3384] = (MH, 'Mindheal')
    H.COMPANIES[3385] = ('area', RZ, 'Rzeszów')
    TEXT = """This album is dedicated to my lovely daughter and son.
All tracks written, performed and recorded by Wojciech Stecko
Music production, mix, mastering: Wojciech Stecko (Mindheal)
Tracks were composed and produced between February 2025 and April 2026 in Rzeszow, Poland."""
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  { sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()),
    aka: (g.querySelector('[data-el=aka-note]') || {}).textContent || '',
    rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); return [tr.querySelector('.dci-drole').dataset.raw.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', tr.dataset.level || '']; }) }])))()"""
    import common_rows as C
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        e0 = pg.evaluate("(() => { const c = getComputedStyle(document.getElementById('dci-pagebar')); return [c.borderTopWidth, c.borderLeftWidth, c.borderRightWidth, c.borderBottomWidth, c.borderTopLeftRadius]; })()")
        H.open_dashboard(pg)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        H.wait_still(pg, "document.body.innerHTML", 15, 300)
        g = pg.evaluate(ROWS)
        for k, v in g.items():
            print('   ', k, v)
        ws = g.get('Wojciech Stecko') or {'rows': [], 'sugg': [], 'aka': ''}
        types = sorted(r[1] for r in ws['rows'])
        print('A)', types)
        mx = pg.evaluate("[...document.querySelectorAll('.dci-matrix thead .dci-mx-card')].map(h => h.textContent.replace(/\\s+/g, ' ').trim())")
        print('   Matrix:', [x[:50] for x in mx])
        results.append(types == sorted(['performer', 'recording', 'producer', 'mix', 'mastering']) and not any('All tracks' in r[0] for r in ws['rows'])
                       and any('Wojciech Stecko' in x and 'writer' in x for x in mx))
        print('B)', ws['sugg'][:3], '|', ws['aka'][:90])
        results.append(any('Mindheal' in x for x in ws['sugg']) and 'Mindheal' in ws['aka'] and 'full name' not in ws['aka'] and 'artist of his or her own' in ws['aka'])
        rz = g.get('Rzeszow') or {'rows': []}
        dm = C.cells(pg)
        print('C)', rz['rows'], '|', dm.get('composition'), dm.get('production'))
        pg.locator('[data-act=dm-apply]').evaluate('b => b.click()')
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        prod = [r for r in C.rows_of(pg, 'Wojciech Stecko')]
        # (linked: Wojciech Stecko as Mindheal for the test, Rzeszow as Rzeszów – then staged)
        for nm in ('Wojciech Stecko', 'Rzeszow'):
            pg.evaluate(f"[...document.querySelectorAll('section.dci-group')].find(g => g.querySelector('.dci-gname strong').textContent.trim() === '{nm}').querySelector('[data-act=name-use]').click()")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
        pg.locator('[data-act=apply]').evaluate('b => b.click()')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Staging complete/.test(li.textContent))", 30)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        rels = pg.evaluate("""MB.relationshipEditor.state.added.map(r => [r.linkTypeID, [r.begin_date, r.end_date].map(d => d ? [d.year, d.month].join('-') : '').join(' – ')])""")
        dated = sorted(set(tuple(x) for x in rels if x[0] in (167, 875, 141, 1101)))
        print("   Zeilen:", prod, "| gestaged:", dated)
        results.append(any(r[:2] == ['Produced In', 'produced in'] for r in rz['rows']) and any('Rzeszow' in x and 'composed in' in x for x in mx)
                       and dm.get('composition', [[None]])[0][0] == 'Production · Composition 1 · 2025-02 – 2026-04' and dm.get('production', [[None]])[0][0] == 'Production · Composition 1 · 2025-02 – 2026-04'
                       and dated == [(141, '2025-2 – 2026-4'), (167, '2025-2 – 2026-4'), (875, '2025-2 – 2026-4'), (1101, '2025-2 – 2026-4')])
        ign = pg.evaluate("[...document.querySelectorAll('.dci-ignored li, [data-el=ignored] li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim())")
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim())")
        print('D)', ign, '| nicht erkannt:', unrec)
        results.append(any('daughter' in x and 'a dedication without a name' in x for x in ign) and not unrec)
        print('E)', e0)
        results.append(e0[:4] == ['1px'] * 4 and e0[4] != '0px')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_prd395():
    """Credits Importer 3.95.0 (Z-PRD, Z-DPD; rules D029, D030), a pasted text, no dates from Discogs's notes:
    A) "Tracks were composed and produced between February 2025 and April 2026.": one entry of the date pool, "Production · Composition 1"
       (until 3.94.0 "Production 1" and "Composition 1"), in the columns Composition, Production and – no date of the recording in the
       text – Performance; applied, Jane Doe's performer row has it (until 3.94.0 none).
    B) Its date changed in the cell of Composition ("Edit date", another year saved): that cell gets a date of its own ("Composition 1 ·
       2020-02 – 2026-04"), Production and Performance keep the shared one; (review) opening the form alone changes nothing.
    C) "Recorded in 2024 by Jane Doe" in the same text: Performance has 2024 only – the date of the production is not the recording's.
    D) (review) Two dates of composition and production: "Production · Composition 1" and "… 2"; E) "composed" alone with the same date:
       one cell in Composition."""
    import common_rows as C
    orig = H.discogs_release

    def rel():
        d = orig()
        d['notes'] = ''
        return d
    H.discogs_release = rel
    results = []

    def run(text, edit=False):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.src_menu(pg, 'text-open')
            pg.fill('[data-f=text-src]', text)
            pg.click('[data-act=text-load]')
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
            H.wait_still(pg, "document.body.innerHTML", 15, 300)
            pool = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date .dci-chip-main')].map(x => x.textContent.replace(/\\s+/g, ' ').trim().replace(/ \\d+ rows?$/, ''))")
            dm = C.cells(pg)
            out = {'pool': pool, 'dm': {k: [c[0] for c in v] for k, v in dm.items() if v}}
            if edit:
                pg.locator('.dci-dm-col[data-dmcol=composition] [data-act=dm-edit]').first.evaluate('b => b.click()')
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
                pg.locator('.dci-dm-col[data-dmcol=composition] [data-act=pool-edit]').first.evaluate('b => b.click()')
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
                # ((review) the date of its own once another date is saved – not on opening the form
                out['pool1'] = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date .dci-chip-main')].length")
                pg.fill('[data-f=pf-by]', '2020')
                pg.locator('[data-act=pool-save]').evaluate('b => b.click()')
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
                out['pool2'] = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date .dci-chip-main')].map(x => x.textContent.replace(/\\s+/g, ' ').trim().replace(/ \\d+ rows?$/, ''))")
                out['dm2'] = {k: [c[0] for c in v] for k, v in C.cells(pg).items() if v}
            else:
                pg.locator('[data-act=dm-apply]').evaluate('b => b.click()')
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
                out['jane'] = C.rows_of(pg, 'Jane Doe')
            out['errs'] = errs
            b.close()
            return out

    try:
        SHARED = 'Production · Composition 1 · 2025-02 – 2026-04'
        a = run('All tracks performed by Jane Doe\nTracks were composed and produced between February 2025 and April 2026.')
        print('A)', a)
        results.append([x for x in a['pool'] if '2025' in x] == [SHARED]
                       and a['dm'].get('composition') == [SHARED] and a['dm'].get('production') == [SHARED] and a['dm'].get('performance') == [SHARED]
                       and any('2025-02 – 2026-04' in r for r in a['jane']) and not a['errs'])
        b2 = run('All tracks performed by Jane Doe\nTracks were composed and produced between February 2025 and April 2026.', edit=True)
        print('B)', b2.get('pool2'), b2.get('dm2'))
        results.append(b2['pool1'] == 1 and sorted(x for x in b2['pool2'] if '202' in x) == sorted([SHARED, 'Composition 1 · 2020-02 – 2026-04'])
                       and b2['dm2'].get('composition') == ['Composition 1 · 2020-02 – 2026-04'] and b2['dm2'].get('production') == [SHARED]
                       and b2['dm2'].get('performance') == [SHARED])
        c = run('Recorded in 2024 by Jane Doe\nTracks were composed and produced in 2025.')
        print('C)', c)
        results.append([x for x in c['dm'].get('performance', [])] == ['Performance 1 · 2024'] and c['dm'].get('production') == ['Production · Composition 1 · 2025'])
        # (review) two such dates: numbered one after the other; a date of one group alone the same as the shared one: no second cell
        d = run('All tracks performed by Jane Doe\nTracks 1 and 2 were composed and produced in 2019. Tracks 3 and 4 were composed and produced in 2021.')
        e = run('All tracks performed by Jane Doe\nTracks were composed and produced in 2025. The songs were composed in 2025.')
        print('D)', d['pool'], '| E)', e['dm'].get('composition'))
        results.append(sorted(x for x in d['pool'] if '20' in x) == ['Production · Composition 1 · 2019', 'Production · Composition 2 · 2021']
                       and len(e['dm'].get('composition') or []) == 1)
    finally:
        H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_rdst3105():
    """Credits Importer 3.105.0 (collected item Z-RDST, rule S171): a place right after the date of a sentence of recording, without "at",
    by a word of places – "Recorded May, 6. 7, 2007 Studio des deutschen Filmorchesters Babelsberg." Studio des deutschen Filmorchesters
    Babelsberg (recorded at), "Recorded June 2010 Abbey Road Studios, London." Abbey Road Studios, "Recorded live March 3, 2001, Konzerthaus
    Berlin." Konzerthaus Berlin (the word at the end of a word); not "Recorded 2001 Hans Meier played the drums." nor "Recorded 2001. Studio
    work by X." (another sentence); (review) nor "Hall & Oates producing", "Church Street", "Producer Tom House", "Bauhaus", "In The Studio"; a
    text with a photo of the concert read without an error (the release page)."""
    import json
    import subprocess
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const isRole = (phrase) => { const p = m.parseRoleNotation(phrase)[0]; if (!p || !p.base) return false; const r = m.mapRole(p.base, p.mods); return !!(r.rule && r.rule !== 'R096' && !r.fallback); };
const ctx = { isRole, isCompanyRole: (x) => /recorded at|recorded in/i.test(x), resolveTracks: () => null, resolveTitles: (ts) => ({ indexes: new Set(), unresolved: ts }), trackCount: 4 };
console.log(JSON.stringify(['Recorded May, 6. 7, 2007 Studio des deutschen Filmorchesters Babelsberg.', 'Recorded June 2010 Abbey Road Studios, London.',
  'Recorded live March 3, 2001, Konzerthaus Berlin.', 'Recorded 2001 Hans Meier played the drums.', 'Recorded 2001. Studio work by X.',
  'Recorded 2001 Hall & Oates producing', 'Recorded live 1999, Church Street', 'Recorded 2019 Producer Tom House', 'Recorded live 1982 Bauhaus', 'Recorded 2007 In The Studio',
  'Recorded live 2019. Photos taken 2019 live at the club by Jane Doe']
  .map((t) => m.SOURCES.text.parse(t, ctx).companies.map((c) => [c.who.name, c.role]))));
"""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    out = json.loads(js.stdout) if not js.returncode else js.stderr[-300:]
    print('A)', out)
    ok = out == [[['Studio des deutschen Filmorchesters Babelsberg', 'Recorded At']], [['Abbey Road Studios', 'Recorded At']], [['Konzerthaus Berlin', 'Recorded At']], [], [], [], [], [], [], [], []]
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])



def case_una3108():
    """Credits Importer 3.108.0 (collected item Z-UNA2): the words of a line not recognized in groups of sense. "Kara D. Rusch made the
    sounds at Fable Hall Studio with Drum Guy":
    A) A click on "Kara" chooses "Kara D. Rusch" (the name with its initial), kind artist; a click again on "D." only "D.".
    B) "Hall": "Fable Hall Studio", kind place (its words).
    C) ⇧-click from "Kara" to "sounds" (the words up to it, as before). D) "Drum Guy" – an entry of the import – marked as known; the
       words' tooltip names the click again and ⇧."""
    TEXT = "Kara D. Rusch made the sounds at Fable Hall Studio with Drum Guy"

    def word(pg, text, shift=False):
        pg.evaluate("""([text, shift]) => { const el = [...document.querySelectorAll('.dci-unrec .dci-una-w')].find(x => x.textContent === text);
          el.dispatchEvent(new MouseEvent('click', { bubbles: true, shiftKey: shift })); }""", [text, shift])
        pg.wait_for_timeout(300)
    FORM = """(() => { const f = document.querySelector('.dci-una-form'); return f ? [f.querySelector('[data-f=una-name]').value, f.querySelector('[data-f=una-kind]').value,
      [...document.querySelectorAll('.dci-una-sel')].map(x => x.textContent)] : null; })()"""
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
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Text read/.test(li.textContent))", 90)
        pg.wait_for_timeout(1000)
        pg.evaluate("document.querySelector('.dci-unrec').open = true")
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(l => l.textContent.replace(/\\s+/g, ' ').trim())")
        word(pg, 'Kara')
        a1 = pg.evaluate(FORM)
        word(pg, 'D.')
        a2 = pg.evaluate(FORM)
        word(pg, 'Hall')
        b1 = pg.evaluate(FORM)
        word(pg, 'Kara')
        word(pg, 'sounds', shift=True)
        c1 = pg.evaluate(FORM)
        known = pg.evaluate("[...document.querySelectorAll('.dci-unrec .dci-una-known')].map(x => x.textContent.trim())")
        tip = pg.evaluate("(document.querySelector('.dci-unrec .dci-una-w') || {}).title || ''")
        print('Zeilen:', unrec, '\nA)', a1, a2, '\nB)', b1, '\nC)', c1, '\nD)', known, tip, '| Fehler:', errs)
        results.append(unrec == [TEXT] and a1 == ['Kara D. Rusch', 'artist', ['Kara', 'D.', 'Rusch']] and a2 and a2[2] == ['D.']
                       and b1 == ['Fable Hall Studio', 'place', ['Fable', 'Hall', 'Studio']] and c1 and c1[2] == ['Kara', 'D.', 'Rusch', 'made', 'the', 'sounds']
                       and known == ['Drum Guy'] and 'again' in tip and '⇧' in tip and not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

run_cases(globals())
