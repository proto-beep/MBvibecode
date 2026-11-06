"""Works: covers of other works (Credits Importer 3.72.0: split off t_works_more.py, collected item Z-TST – its longest case on its own, so the suite's files end together).

Cases: coverworks (3.38.16)."""
import re
import urllib.parse
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_coverworks():
    """Credits Importer 3.38.16 (collected item 179, 179b, F-179b – F-179d): works of a track's composer by a similar title.
    A) Track 1.4 "Variants On A Theme By Monk", Discogs "Written-By [Theme] – Monk" (Thelonious Monk) on it: of Monk's four works
       only "Variants on a Theme of Thelonious Monk (Criss-Cross)" is offered ("… the composer of the track (similar title)") –
       not all his works. Track 1.3 "Round Midnight (Thelonious Monk cover)" (no credit of Monk): the full name of the title looked
       up in MusicBrainz – "'Round Midnight" offered ("the title names “Thelonious Monk”"). Track 1.2 "Epistrophy By Monk": the
       surname matches an artist of the release – "Epistrophy" offered. The log names the three titles (1.4: "By Monk" too).
    B) "Link" of Monk's work for track 1.4: the link offers "co?" (dashed; Monk is none of the performers), a click sets "cover";
       the credited writer's own work of the same title ("Epistrophy By Monk" by Writer W) gets no "co?"; the works of the artists are
       compared once (the name in the title looked up within the same run). [Z-CV] (3.40.17) Monk has only writing credits on the
       release (not classical): "cover" is set by itself – "co" yellow, ticked; a click takes it off ("co?" again), another sets it.
    D) (3.39.9, collected item K-9) no "co?" when Monk performs the track: a member of the release's band ("member of band" in
       MusicBrainz), the pianist of the recording in MusicBrainz, or the track's artist. (3.40.17: where it was "co?", "cover" set by
       itself; neither when he performs.)
    E) [Z-CV] (3.40.17) Not set by itself – "co?" only: the release of the genre "Classical" at Discogs; Monk with another credit
       on the release (Liner Notes).
    C) In Node: titleComposerNames – "(Thelonious Monk cover)" → Thelonious Monk (full), "By Monk" → Monk (surname), "(Live)",
       "(Theme)", "Stand By Me", "(Part 2)" → none; (3.38.16, review) "(Prod. By Metro Boomin)", "(Main Title)", "(Dub)", "Stand By Your
       Man", "(Act II)" → none, "Theme By Monk For Piano" → Monk, "(Ludwig van Beethoven cover)" → the full name, "BY MONK" → MONK; similarWorkTitle – the composer's names and brackets left out, a work's title
       whole in the track's title from two words or six letters ("Theme" alone not)."""
    import json
    import subprocess
    MONK = H.uid('dddddddd', 3410)
    TB = H.uid('dddddddd', 60)
    W6, W7, W8, W9, W10, W11 = (H.uid('cccccccc', n) for n in (86, 87, 88, 89, 90, 91))
    WW = H.ARTISTS[3007][0]
    H.ARTISTS[3410] = (MONK, 'Thelonious Monk')
    # [Z-CV] (3.40.17) Monk's work known to /ws/js/entity (it is staged)
    H.COMPANIES[7086] = ('work', H.uid('cccccccc', 86), 'Variants on a Theme of Thelonious Monk (Criss-Cross)')
    H.TITLES[1:4] = ['Epistrophy By Monk', 'Round Midnight (Thelonious Monk cover)', 'Variants On A Theme By Monk']
    H.RELEASE_AC[:] = [(TB, 'Test Band', 'Test Band', '')]
    for i, n in [(567, 'cover'), (578, 'live')]:
        H.attr(i, n, i)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.ARTIST_WORKS.update({MONK: [{'id': W6, 'title': 'Variants on a Theme of Thelonious Monk (Criss-Cross)', 'type': 'Song', 'aliases': []},
                                  {'id': W7, 'title': 'Criss Cross', 'type': 'Song', 'aliases': []},
                                  {'id': W8, 'title': "'Round Midnight", 'type': 'Song', 'aliases': []},
                                  {'id': W9, 'title': 'Epistrophy', 'type': 'Song', 'aliases': []}],
                           TB: [{'id': W10, 'title': 'Song One', 'type': 'Song', 'aliases': []}],
                           WW: [{'id': W11, 'title': 'Epistrophy By Monk', 'type': 'Song', 'aliases': []}]})
    orig = H.discogs_release

    def rel():
        d = orig()
        d['tracklist'][3]['extraartists'] = [{'name': 'Thelonious Monk', 'anv': 'Monk', 'role': 'Written-By [Theme]', 'tracks': '', 'id': 3410, 'join': ''}]
        return d

    H.discogs_release = rel
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    SAME = """(i) => { const tr = document.querySelector(`tr[data-work="${i}"]`); const s = tr && tr.querySelector('.dci-same');
      return s ? [...s.querySelectorAll('li')].map(li => [li.querySelector('[data-act=work-pick]').dataset.gid, li.querySelector('.dci-sub').textContent.trim()]) : null; }"""
    PILL = """(i) => { const tr = document.querySelector(`tr[data-work="${i}"]`); const p = tr && tr.querySelector('.dci-wpill[data-attr=cover]');
      return p ? [p.className.replace(/.*dci-wpill-(\\w+).*/, '$1'), p.textContent.trim(), p.title] : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
        pg.add_style_tag(content='#dci-log { display: none !important; }')
        pg.wait_for_timeout(400)
        same = lambda i: pg.evaluate(f"({SAME})({i})")
        s4, s3, s2 = same(3), same(2), same(1)
        logs = [x for x in pg.evaluate(LOGS) if 'the title names' in x]
        print('A) 1.4:', s4, '\n   1.3:', s3, '\n   1.2:', s2, '\n   Protokoll:', logs)
        results.append(s4 == [[W6, 'Song – work of Thelonious Monk, the composer of the track (similar title)']]
                       and s3 == [[W8, 'Song – work of Thelonious Monk – the title names “Thelonious Monk”']]
                       and sorted(s2 or []) == sorted([[W9, 'Song – work of Thelonious Monk – the title names “Monk”'], [W11, 'Song – work of Writer W']])
                       and len([x for x in pg.evaluate(LOGS) if 'Works of the artists compared' in x]) == 1
                       and sorted(logs) == sorted(['Track 1.3: the title names “Thelonious Monk” – the works of Thelonious Monk are compared',
                                                   'Track 1.2: the title names “Monk” – the works of Thelonious Monk are compared',
                                                   'Track 1.4: the title names “Monk” – the works of Thelonious Monk are compared']))
        pg.locator('tr[data-work="3"] [data-act=mx-works]').click(); pg.wait_for_timeout(300)
        pg.locator(f'tr[data-work="3"] .dci-mx-wlist [data-act=work-pick][data-gid="{W6}"]').click(); pg.wait_for_timeout(500)
        # [3.39.9] "co?" once MusicBrainz said who is a member of whom (looked up in the background; (3.40.3) 45 s under load)
        H.wait_for(pg, f"!!({PILL})(3)", 45)
        b0 = pg.evaluate(f"({PILL})(3)")
        # [Z-CV] (3.40.17) staged with "cover" (567)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        staged = pg.evaluate(f"""(() => {{ const ids = (r) => r && r.attributes && r.attributes.__tree ? r.attributes.__tree.map(a => a.typeID || a.type.id) : [];
          return MB.relationshipEditor.state.added.filter(x => x.linkTypeID === 278 && x.entity1 && x.entity1.gid === '{W6}').map(ids); }})()""")
        pg.wait_for_timeout(300)
        pg.locator('tr[data-work="3"] .dci-wpill[data-attr=cover]').click(); pg.wait_for_timeout(300)
        b1 = pg.evaluate(f"({PILL})(3)")
        # the credited writer's own work of the same title: no "co?" (a songwriter's song is no cover)
        pg.locator('tr[data-work="1"] [data-act=mx-works]').click(); pg.wait_for_timeout(300)
        pg.locator(f'tr[data-work="1"] .dci-mx-wlist [data-act=work-pick][data-gid="{W11}"]').click(); pg.wait_for_timeout(500)
        b2 = pg.evaluate(f"({PILL})(1)")
        pg.locator('tr[data-work="3"] .dci-wpill[data-attr=cover]').click(); pg.wait_for_timeout(300)
        b1b = pg.evaluate(f"({PILL})(3)")
        print('B) co:', b0, '| gestaged:', staged, '→', b1, '→', b1b, '| eigenes Werk von Writer W:', b2)
        # [Z-CV] (3.40.17) set by itself (until 3.40.16 offered: "co?", a click set it)
        results.append(b0 and b0[0] == 'auto' and b0[1] == 'co' and staged == [[567]] and b0[2].startswith('Cover – set by itself: the composer (Thelonious Monk) is none of the performers')
                       and b1 and b1[0] == 'hint' and b1[1] == 'co?' and b1[2].startswith('Cover? The composer (Thelonious Monk) is none of the performers')
                       and b1b and b1b[0] == 'on' and (b2 is None or b2[0] not in ('hint', 'auto')))
        print('Fehler:', errs)
        results.append(not errs)

        # D) (3.39.9, K-9, Q-m, Q-w) no "co?" when Monk performs: a member of the release's band, MusicBrainz's pianist of the
        # recording, or the track's artist
        def pill_with(setup, look=None):
            setup()
            c2 = H.new_context(b)
            # (3.39.9, review) the lookups of "member of band": the composer's only
            looked = []
            c2.on('request', lambda r: looked.append(re.search(r'/ws/2/artist/([0-9a-f-]{36})', r.url).group(1)) if re.search(r'/ws/2/artist/[0-9a-f-]{36}\?inc=artist-rels', r.url) else None)
            p2, e2 = H.open_mb_edit(c2, companion=False)
            p2.on('dialog', lambda d: d.accept())
            p2.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(p2)
            H.wait_for(p2, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
            p2.add_style_tag(content='#dci-log { display: none !important; }')
            p2.wait_for_timeout(400)
            # (3.40.3) under load: the button there first (60 s)
            p2.wait_for_selector('tr[data-work="3"] [data-act=mx-works]', timeout=60000)
            pick = p2.locator(f'tr[data-work="3"] .dci-mx-wlist [data-act=work-pick][data-gid="{W6}"]')
            for _ in range(3):
                p2.locator('tr[data-work="3"] [data-act=mx-works]').click(); p2.wait_for_timeout(300)
                if pick.is_visible():
                    break
                p2.wait_for_timeout(1500)
            pick.click()
            p2.wait_for_timeout(3000)
            # (3.40.1) the lookups (the composer's, (3.40.1) its other names'): until they are asked (30 s at most, under load), then a
            # moment for their answers and the matrix (the cases without a lookup wait as long as before)
            for _ in range(120):
                if len(looked) >= len(look or [MONK]):
                    break
                p2.wait_for_timeout(250)
            p2.wait_for_timeout(3000)
            out = p2.evaluate(f"({PILL})(3)")
            c2.close()
            return out, e2 + ([] if looked == (look or [MONK]) else [f'lookups: {looked}'])
        d0, e0 = pill_with(lambda: None)  # the same page without any of them: "cover" (so the three below say something)
        d1, e1 = pill_with(lambda: H.BAND_MEMBERS.update({TB: [MONK]}))
        H.BAND_MEMBERS.clear()
        # (review) the other direction: the band of the composer, the release's artist a member of it
        d1b, e1b = pill_with(lambda: H.BAND_MEMBERS.update({MONK: [TB]}))
        H.BAND_MEMBERS.clear()
        d2, e2 = pill_with(lambda: H.MB_EXTRA.setdefault(H.REC[3], []).append({'target-type': 'artist', 'type': 'instrument', 'type-id': H.LTS[148]['gid'],
                                                                                 'attributes': ['piano'], 'attribute-values': {}, 'artist': {'id': MONK, 'name': 'Thelonious Monk'}}))
        H.MB_EXTRA.pop(H.REC[3], None)
        d3, e3 = pill_with(lambda: H.TRACK_AC.update({3: [(MONK, 'Thelonious Monk')]}))
        H.TRACK_AC.clear()
        # (3.43.1, full review P2) the same track on a medium the web service answers without the recordings' relationships – the
        # tracks are read from MB's own pages of tracks (/ws/js/tracks): their artists count too (until 3.43.0 none: "cover" set by itself)
        d3b, e3b = pill_with(lambda: (H.TRACK_AC.update({3: [(MONK, 'Thelonious Monk')]}), H.WS_NO_RELS.add(1)))
        H.TRACK_AC.clear()
        H.WS_NO_RELS.clear()
        # (review) MusicBrainz's pianist of the whole release
        d4, e4 = pill_with(lambda: H.MB_EXTRA.setdefault(H.REL, []).append({'target-type': 'artist', 'type': 'instrument', 'type-id': '67555849-61e5-455b-96e3-29733f0115f5',
                                                                               'attributes': ['piano'], 'attribute-values': {}, 'artist': {'id': MONK, 'name': 'Thelonious Monk'}}))
        H.MB_EXTRA.pop(H.REL, None)
        # [Z-AF] (3.40.1) "is person": Monk's other name is the release's artist; Monk's other name is a member of the release's band
        # (Q-ah – the bands of the other name looked up too)
        ALIAS = H.uid('dddddddd', 3411)
        d5, e5 = pill_with(lambda: H.IS_PERSON.update({MONK: [TB]}))
        H.IS_PERSON.clear()
        d6, e6 = pill_with(lambda: (H.IS_PERSON.update({MONK: [ALIAS]}), H.BAND_MEMBERS.update({TB: [ALIAS]})), look=[MONK, ALIAS])
        H.IS_PERSON.clear()
        H.BAND_MEMBERS.clear()
        # the control: the other name in no band of the release – "cover" (after both lookups)
        d7, e7 = pill_with(lambda: H.IS_PERSON.update({MONK: [ALIAS]}), look=[MONK, ALIAS])
        H.IS_PERSON.clear()
        H.BAND_MEMBERS.clear()
        # (3.40.3, review) two performance names of one person: Monk and the release's artist both "is person" of LEGAL – from LEGAL's
        # answer, no lookup more
        LEGAL = H.uid('dddddddd', 3412)
        d8, e8 = pill_with(lambda: H.IS_PERSON.update({LEGAL: [MONK, TB]}), look=[MONK, LEGAL])
        H.IS_PERSON.clear()
        print('   is person:', d5, '| anderer Name in der Band:', d6, '| anderer Name, keine Band (Gegenprobe):', d7, '| zwei Künstlernamen:', d8, '| Fehler:', e5, e6, e7, e8)
        print('D) ohne:', d0, '| Mitglied der Band:', d1, '| Band des Komponisten:', d1b, '| Pianist in MB:', d2, '| Track-Artist:', d3, '| Track-Artist, Medium nachgeladen:', d3b, '| Pianist des Release:', d4, '| Fehler:', e0, e1, e1b, e2, e3, e3b, e4)
        no_co = lambda x: x is None or x[0] not in ('hint', 'auto')
        # d2, d3: performers known without a lookup – none asked then (the lookups list says [MONK] only where one is made)
        results.append(d0 is not None and d0[0] == 'auto' and no_co(d1) and no_co(d1b) and no_co(d2) and no_co(d3) and no_co(d3b) and no_co(d4)
                       and not (e0 or e1 or e1b) and all(not [x for x in e if not x.startswith('lookups')] for e in (e2, e3, e3b, e4)))
        results.append(no_co(d5) and no_co(d6) and d7 is not None and d7[0] == 'auto' and no_co(d8) and not (e5 or e6 or e7 or e8))

        # E) [Z-CV] (3.40.17) "co?" only: classical; another credit of Monk
        def with_rel(change):
            def setup():
                def r2():
                    d = rel()
                    change(d)
                    return d
                H.discogs_release = r2
            return setup
        f0, f0e = pill_with(with_rel(lambda d: d.update({'genres': ['Classical']})))
        f1, f1e = pill_with(with_rel(lambda d: d.update({'extraartists': d['extraartists'] + [{'name': 'Thelonious Monk', 'anv': '', 'role': 'Liner Notes', 'tracks': '', 'id': 3410, 'join': ''}]})))
        H.discogs_release = rel
        print('E) Classical:', f0, '| Liner Notes:', f1, '| Fehler:', f0e, f1e)
        results.append(f0 is not None and f0[0] == 'hint' and f1 is not None and f1[0] == 'hint' and not (f0e or f1e))
        b.close()
    TITLES = ['Round Midnight (Thelonious Monk cover)', 'Epistrophy By Monk', 'Song (Live)', 'Song (Theme)', 'Stand By Me', 'Song (Part 2)',
              'Money (Prod. By Metro Boomin)', 'Song (Main Title)', 'Song (Dub)', 'Theme By Monk For Piano', 'Ode (Ludwig van Beethoven cover)',
              'Stand By Your Man', 'Overture (Act II)', 'Theme BY MONK']
    SIM = [['Variants On A Theme By Monk', ['Variants on a Theme of Thelonious Monk (Criss-Cross)'], ['Thelonious Monk', 'Monk']],
           ['Round Midnight (Thelonious Monk cover)', ["'Round Midnight"], ['Thelonious Monk', 'Monk']],
           ['Variants On A Theme By Monk', ['Criss Cross'], ['Thelonious Monk', 'Monk']],
           ['A Theme For Ernie', ['Theme'], ['Fred Lacey', 'Lacey']],
           ['Blue Monk Live At Newport', ['Blue Monk'], ['Thelonious Monk', 'Monk']]]
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const t = JSON.parse(process.argv[2]).map((x) => m.titleComposerNames(x));
const s = JSON.parse(process.argv[3]).map(([a, b, c]) => m.similarWorkTitle(a, b, c));
console.log(JSON.stringify([t, s]));
"""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(TITLES), json.dumps(SIM)], capture_output=True, text=True)
    got = json.loads(js.stdout) if not js.returncode else [js.stderr[-500:], None]
    print('C) Namen:', got[0], '| ähnlich:', got[1])
    results.append(got[0] == [[{'name': 'Thelonious Monk', 'full': True}], [{'name': 'Monk', 'full': False}], [], [], [], [], [], [], [],
                              [{'name': 'Monk', 'full': False}], [{'name': 'Ludwig van Beethoven', 'full': True}], [], [], [{'name': 'MONK', 'full': False}]]
                   and got[1] == [True, True, False, False, True])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
