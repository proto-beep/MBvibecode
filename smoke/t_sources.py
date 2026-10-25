"""Sources: the adapter, several linked releases, supplementing, the tracks of a source (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: adapter, links, supp, tracksfit – each the former smoke/t_<case>.py, unchanged; `python3 t_sources.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_adapter():
    """Import 3.0.0: the source adapter. Only the Discogs adapter reads Discogs; it delivers a neutral release
    (tracks, credits as "who – role as written – details – tracks", companies, series, notes, format words), and the
    core works with that alone.
    A) Boundary: outside the adapter the script touches no Discogs data (no Discogs API or URLs, no Discogs JSON).
    B) The adapter on its own (Node): the neutral release of a Discogs release with headings, an index track, track
       lists ("A1 to A3", an unknown position), name variations and numbered names; the core groups it (S018 splits
       engineer tasks, a person's identical roles are merged across tracks); the "Add artist" seed.
    C) In the dashboard, everything that goes through the adapter: aliases, a series with its parent label, the forms
       for a new artist (members, URLs), label, series and work with their edit notes, the edit note's source, "live"
       from the format, the US date order, the Discogs tab; choosing among two linked releases, a typed URL, a
       release Discogs does not have, a typed text without a release.
    D) Update from 2.19.1 (generation 3): no reset in 3.0.0; since 3.5.0 the fresh start (generation 4) resets once, the
       notice shows the milestones from 3.0.0 on and says so. An update within generation 4 resets nothing.
    PARTS=C runs only C (C passes on Import 2.19.1 too: nothing visible changed)."""
    import json
    import os
    import re
    import subprocess
    import urllib.parse

    PARTS = os.environ.get('PARTS', 'ABCD')
    results = []

    # --- A) boundary --------------------------------------------------------------------------------------
    if 'A' in PARTS:
        src = H.MAIN
        a0 = src.index('// --- Source adapter: Discogs')
        a1 = src.index('// --- From the neutral release to the dashboard')
        i18n_end = src.index('  // 2. Mapping register')
        outside = src[i18n_end:a0] + src[a1:]
        code = '\n'.join(l for l in outside.splitlines() if not l.strip().startswith(('//', '*', '/*')))
        hits = {w: len(re.findall(w, code)) for w in [r'api\.discogs\.com', r'discogs\.com/', r'extraartists', r'entity_type_name', r'tracklist',
                                                      r'sub_tracks', r'\bea\.', r'S\.discogs\b', r'S\.discogsId', r'fetchDiscogs', r'cleanDiscogsName']}
        print('A) Discogs außerhalb des Adapters:', {k: v for k, v in hits.items() if v} or 'nichts')
        results.append(not any(hits.values()))

    # --- B) the adapter on its own (Node) ------------------------------------------------------------------
    if 'B' in PARTS:
        ex = lambda name, role, i, tracks='', anv='': {'name': name, 'anv': anv, 'role': role, 'tracks': tracks, 'id': i, 'join': ''}
        fixture = {
            'id': 77, 'title': 'Edge', 'country': 'US', 'notes': 'Recorded live at X.',
            'formats': [{'name': 'Vinyl', 'descriptions': ['LP', 'Live'], 'text': 'Gatefold'}],
            'series': [{'name': 'Series A', 'id': 501, 'catno': 'Vol. 3'}, {'name': 'No Id', 'catno': '1'}],
            'extraartists': [ex('Eng (2)', 'Engineer [Mix, Recording, Assistant], Producer', 11), ex('Nobody', 'Guitar', 0), ex('', 'Bass', 0),
                             ex('Ranger', 'Drums', 12, 'A1 to A3, B9'), ex('Ranger', 'Drums', 12, 'B1'), ex('NoRole', '', 13),
                             ex('Anv Guy', 'Vocals', 14, '', 'A. Guy'), ex('Sub', 'Piano', 15, 'C1a')],
            'tracklist': [
                {'position': '', 'title': 'Side A', 'type_': 'heading'},
                {'position': 'A1', 'title': 'One', 'type_': 'track', 'extraartists': [ex('Ranger', 'Drums', 12)]},
                {'position': 'A2', 'title': 'Two', 'type_': 'track', 'extraartists': [ex('Eng (2)', 'Engineer [Mix, Recording]', 11)]},
                {'position': 'A3', 'title': 'Three', 'type_': 'track'},
                {'position': 'B1', 'title': 'Four', 'type_': 'track', 'extraartists': [ex('Ranger', 'Drums', 12)]},
                {'position': 'C1', 'title': 'Suite', 'type_': 'index', 'sub_tracks': [
                    {'position': 'C1a', 'title': 'a', 'extraartists': [ex('Sub2', 'Viola', 16)]}, {'position': 'C1b', 'title': 'b'}]},
                {'position': '', 'title': 'NoPos', 'type_': 'track', 'extraartists': [ex('P', 'Flute', 17)]},
            ],
            'companies': [{'name': 'Pub (3)', 'entity_type_name': 'Published By', 'id': 21, 'catno': ' X1 '},
                          {'name': 'Pub (3)', 'entity_type_name': 'Copyright (c)', 'id': 21},
                          {'name': 'NoId Co', 'entity_type_name': 'Recorded At', 'id': 0},
                          {'name': '', 'entity_type_name': 'Pressed By', 'id': 22}, {'name': 'NoRole', 'entity_type_name': '', 'id': 23}],
        }
        js = """
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const d = JSON.parse(process.argv[2]);
const rel = m.DISCOGS.toRelease(d, 77);
const ser = (x) => JSON.parse(JSON.stringify(x, (k, v) => (v instanceof Set ? [...v] : v instanceof Map ? [...v.keys()] : v)));
const groups = m.groupCredits(rel.credits).map((g) => ({ ...g, roles: [...g.roles.values()].map((r) => ({ raw: r.role.raw, anv: r.anv, all: r.allTracks,
  idx: [...r.indexes].sort(), specs: r.specs, pos: r.positions, un: r.unresolved, split: r.role.splitFrom || '' })) }));
const seed = m.buildArtistSeed({ name: 'X', sourceUrl: 'https://www.discogs.com/artist/5', sourceLinkTypeId: 180,
  person: { name: 'Y', urls: ['https://y.example', 'no url', 'https://www.discogs.com/artist/5'] }, typeId: 2,
  rels: [{ mbid: 'm1', linkTypeId: 103, backward: true, ended: true }], editNote: 'note' });
console.log(JSON.stringify({ rel: ser(rel), groups: ser(groups), companies: ser(m.groupCompanies(rel.companies)), seed,
  links: m.DISCOGS.releaseLinks([{ 'target-type': 'url', url: { resource: 'https://www.discogs.com/release/12-X' } }, { 'target-type': 'url', url: { resource: 'https://www.discogs.com/master/5' } }]),
  ids: ['https://www.discogs.com/release/12563517-Peter-Evans', 'r99', '42', 'abc'].map(m.DISCOGS.parseReleaseId),
  keys: ['http://discogs.com/artist/7-Name', 'https://www.discogs.com/label/9', 'https://example.org/artist/1'].map(m.DISCOGS.urlKey) }));
"""
        out = json.loads(subprocess.run(['node', '-e', js, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(fixture)],
                                        capture_output=True, text=True, check=True).stdout)
        rel, groups, comps = out['rel'], out['groups'], out['companies']
        cred = lambda name, role: next((c for c in rel['credits'] if c['who']['rawName'] == name and c['role'] == role), None)
        eng, rng, sub, sub2, flute = cred('Eng (2)', 'Engineer [Mix, Recording, Assistant]'), cred('Ranger', 'Drums'), cred('Sub', 'Piano'), cred('Sub2', 'Viola'), cred('P', 'Flute')
        print('B1) Tracks:', [(t['position'], t['aliases']) for t in rel['tracks']])
        print('    Eng:', eng, '\n    Ranger:', rng['tracks'], '| Sub:', sub['tracks'], '| Sub2:', sub2['tracks'], '| P:', flute['tracks'])
        print('    tags', rel['tags'], '| series', rel['series'], '| url', rel['url'], '| ohne Rolle:', cred('NoRole', ''))
        ok_b = [t['position'] for t in rel['tracks']] == ['A1', 'A2', 'A3', 'B1', 'C1', ''] and rel['tracks'][4]['aliases'] == ['C1a', 'C1b'] \
            and eng['who'] == {'id': 11, 'name': 'Eng', 'rawName': 'Eng (2)', 'links': ['https://www.discogs.com/artist/11']} \
            and eng['base'] == 'Engineer' and eng['details'] == ['Mix', 'Recording', 'Assistant'] and eng['tracks'] == {'all': True} \
            and rng['tracks'] == {'indexes': [0, 1, 2], 'spec': 'A1 to A3, B9', 'unresolved': ['B9']} and sub['tracks']['indexes'] == [4] \
            and sub2['tracks'] == {'indexes': [4], 'position': 'C1'} and flute['tracks'] == {'indexes': [5], 'position': '6'} \
            and cred('NoRole', '') is not None and not any(c['who']['rawName'] == '' for c in rel['credits']) \
            and cred('Anv Guy', 'Vocals')['credited'] == 'A. Guy' and rel['tags'] == ['vinyl', 'lp', 'live', 'gatefold'] \
            and rel['series'] == [{'id': 501, 'name': 'Series A', 'number': 'Vol. 3', 'links': ['https://www.discogs.com/label/501']}] \
            and rel['url'] == 'https://www.discogs.com/release/77' and rel['id'] == '77' and rel['country'] == 'US'
        g = {x['rawName']: x for x in groups}
        print('B2) Gruppen:', {k: [(r['raw'], r['anv'], r['pos'] or r['specs'] or 'all') for r in v['roles']] for k, v in g.items()})
        ok_b = ok_b and [r['raw'] for r in g['Eng (2)']['roles']] == ['Engineer [Mix, Assistant]', 'Engineer [Recording, Assistant]', 'Producer', 'Engineer [Mix]', 'Engineer [Recording]'] \
            and g['Eng (2)']['roles'][0]['split'] == 'Engineer [Mix, Recording, Assistant]' and g['Eng (2)']['roles'][3]['pos'] == ['A2'] \
            and len(g['Ranger']['roles']) == 1 and g['Ranger']['roles'][0]['idx'] == [0, 1, 2, 3] and g['Ranger']['roles'][0]['specs'] == ['A1 to A3, B9', 'B1'] \
            and g['Ranger']['roles'][0]['pos'] == ['A1', 'B1'] and g['Ranger']['roles'][0]['un'] == ['B9'] and not g['Ranger']['roles'][0]['all'] \
            and g['NoRole']['roles'] == [] and g['Nobody']['dId'] == 0 and g['Nobody']['links'] == [] and '' not in g
        # 3.17.0: "refs" – where a company is at its source (lines of a text or Bandcamp; none from Discogs)
        print('B3) Firmen:', [(c['name'], c['rawName'], c['links'], c['roles']) for c in comps])
        ok_b = ok_b and [(c['name'], c['dId']) for c in comps] == [('Pub', 21), ('NoId Co', 0)] \
            and comps[0]['roles'] == [{'role': 'Published By', 'catno': 'X1', 'tracks': None, 'refs': []}, {'role': 'Copyright (c)', 'catno': '', 'tracks': None, 'refs': []}] and comps[1]['links'] == []
        seed = dict((k, v) for k, v in out['seed'])
        print('B4) Seed:', out['seed'], '\n    Links:', out['links'], '| IDs:', out['ids'], '| URL-Schlüssel:', out['keys'])
        ok_b = ok_b and seed.get('edit-artist.name') == 'Y' and seed.get('edit-artist.url.0.text') == 'https://www.discogs.com/artist/5' \
            and seed.get('edit-artist.url.0.link_type_id') == '180' and seed.get('edit-artist.url.1.text') == 'https://y.example' and 'edit-artist.url.2.text' not in seed \
            and seed.get('rels.0.backward') == '1' and seed.get('rels.0.ended') == '1' and seed.get('edit-artist.edit_note') == 'note' \
            and out['links'] == [{'id': '12', 'url': 'https://www.discogs.com/release/12-X'}] and out['ids'] == ['12563517', '99', '42', ''] \
            and out['keys'] == ['https://www.discogs.com/artist/7', 'https://www.discogs.com/label/9', '']
        results.append(bool(ok_b))

    # --- C) in the dashboard --------------------------------------------------------------------------------
    if 'C' in PARTS:
        H.ARTISTS[3021] = (H.uid('dddddddd', 21), 'Real Name')
        ex = lambda name, role, i, tracks='': {'name': name, 'anv': '', 'role': role, 'tracks': tracks, 'id': i, 'join': ''}
        orig_rel = H.discogs_release

        def rel():
            d = orig_rel()
            d['country'] = 'US'
            d['formats'] = [{'name': 'CD', 'qty': '1', 'descriptions': ['Album', 'Live']}]
            d['series'] = [{'name': 'Test Series', 'id': 601, 'catno': 'Vol. 3'}]
            d['extraartists'] += [ex('Alias Guy', 'Guitar', 3020), ex('New Group (2)', 'Bass', 3030)]
            return d

        H.discogs_release = rel
        H.DG_API['/artists/3020'] = {'id': 3020, 'name': 'Alias Guy', 'aliases': [{'id': 3021, 'name': 'Real Name'}]}
        H.DG_API['/artists/3030'] = {'id': 3030, 'name': 'New Group (2)', 'aliases': [], 'urls': ['https://newgroup.example', 'no url'],
                                     'members': [{'id': 3001, 'name': 'Bass Man', 'active': False}, {'id': 3998, 'name': 'Ghost (3)', 'active': True}]}
        H.DG_API['/labels/601'] = {'id': 601, 'name': 'Test Series', 'parent_label': {'id': 1003, 'name': 'Pub Co'}}
        for i, n in [(578, 'live')]:
            H.attr(i, n, i)
        H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (578,))
        H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
        H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
        group = lambda pg, name: pg.evaluate(f"[...document.querySelectorAll('section.dci-group')].find(g => g.querySelector('.dci-gname strong').textContent === {name!r}).dataset.group")

        def form(pg, sel):
            pg.click(sel)
            pg.wait_for_selector('[data-el=sub]:not([hidden])', timeout=20000)
            url = pg.evaluate("document.querySelector('[data-el=sub-frame]').src")
            info = pg.evaluate("document.querySelector('[data-el=sub-info]').innerHTML")
            pg.click('[data-act=sub-close]')
            pg.wait_for_timeout(200)
            q = urllib.parse.urlparse(url)
            return q.path, dict(urllib.parse.parse_qsl(q.query)), info

        note_ok = lambda note, src: note.startswith(f'Source: {src}\nPrefilled by MB x Vibecode: Credits Importer v') and note.endswith(' from Discogs.')
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=True)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            pg.wait_for_timeout(800)
            logs = pg.locator('#dci-log li').all_inner_texts()
            # C1) aliases
            ag = group(pg, 'Alias Guy')
            alias = pg.evaluate(f"[...document.querySelectorAll('section[data-group=\"{ag}\"] [data-act=alias-use]')].map(b => b.dataset.mbid)")
            src_link = pg.evaluate(f"(() => {{ const a = document.querySelector('section[data-group=\"{ag}\"] .dci-dglink'); return [a.href, a.textContent]; }})()")
            print('C1) Alias:', alias, '| Protokoll:', [x[9:] for x in logs if 'Alias Guy' in x][-1:], '| Link:', src_link)
            ok1 = alias == [H.ARTISTS[3021][0]] and src_link == ['https://www.discogs.com/artist/3020', 'Discogs↗']  # [3.28.0] only the tag (item 61)
            # C2) series with its parent label, and its form
            sg = group(pg, 'Test Series')
            slabel = pg.evaluate(f"(() => {{ const s = document.querySelector('section[data-group=\"{sg}\"] .dci-series-label'); return s ? [...s.querySelectorAll('a')].map(a => [a.href, a.textContent]) : null; }})()")
            path, q, _ = form(pg, f'section[data-group="{sg}"] [data-act=other-create]')
            print('C2) Serie:', slabel, '|', path, {k: v for k, v in q.items() if k != 'edit-series.edit_note'})
            ok2 = slabel and slabel[0] == ['https://www.discogs.com/label/1003', 'DiscogsPub Co'] and slabel[1][0].endswith(f'/label/{H.COMPANIES[1003][1]}') \
                and path == '/series/create' and q.get('edit-series.name') == 'Test Series' and q.get('edit-series.url.0.text') == 'https://www.discogs.com/label/601' \
                and 'edit-series.url.0.link_type_id' not in q and q.get('rels.0.target') == H.COMPANIES[1003][1] and q.get('rels.0.backward') == '1' \
                and note_ok(q.get('edit-series.edit_note', ''), 'https://www.discogs.com/label/601')
            # C3) a new artist (a group): members, URLs, edit note
            ng = group(pg, 'New Group')
            path, q, info = form(pg, f'section[data-group="{ng}"] [data-act=artist-create]')
            print('C3) Artist:', path, {k: v for k, v in q.items() if k != 'edit-artist.edit_note'}, '| nicht in MB:', re.findall(r'href="([^"]+)"[^>]*>([^<]+)<', info))
            ok3 = path == '/artist/create' and q.get('edit-artist.name') == 'New Group' and q.get('edit-artist.type_id') == '2' \
                and q.get('edit-artist.url.0.text') == 'https://www.discogs.com/artist/3030' and q.get('edit-artist.url.0.link_type_id') == '180' \
                and q.get('edit-artist.url.1.text') == 'https://newgroup.example' and 'edit-artist.url.2.text' not in q \
                and q.get('rels.0.target') == H.ARTISTS[3001][0] and q.get('rels.0.backward') == '1' and q.get('rels.0.ended') == '1' \
                and note_ok(q.get('edit-artist.edit_note', ''), 'https://www.discogs.com/artist/3030') \
                and ('https://www.discogs.com/artist/3998', 'Ghost') in re.findall(r'href="([^"]+)"[^>]*>([^<]+)<', info)
            # C4) a new label
            gp = group(pg, 'Ghost Pub')
            path, q, _ = form(pg, f'section[data-group="{gp}"] [data-act=company-create][data-et=label]')
            print('C4) Label:', path, {k: v for k, v in q.items() if k != 'edit-label.edit_note'})
            ok4 = path == '/label/create' and q.get('edit-label.name') == 'Ghost Pub' and q.get('edit-label.url.0.text') == 'https://www.discogs.com/label/1005' \
                and q.get('edit-label.url.0.link_type_id') == '217' and note_ok(q.get('edit-label.edit_note', ''), 'https://www.discogs.com/label/1005')
            # C5) a new work: edit note with the release
            path, q, _ = form(pg, 'tr[data-work="1"] [data-act=work-create]')
            print('C5) Werk:', path, q.get('edit-work.name'), repr(q.get('edit-work.edit_note', '')[:140]))
            ok5 = path == '/work/create' and q.get('edit-work.edit_note', '').startswith('Source: https://www.discogs.com/release/1234\nPrefilled by') \
                and q.get('edit-work.edit_note', '').endswith('; writers from Discogs credits.')
            # C6) live from the format; the US date order (rule test)
            hint = pg.evaluate("(document.querySelector('tr[data-work=\"0\"] .dci-wpill[data-attr=live]') || {}).title || ''")
            pg.click('[data-act=rules]'); pg.wait_for_timeout(200)
            pg.fill('#dci-rules [data-rf=test]', 'Recorded 1/11/2022'); pg.wait_for_timeout(200)
            res = re.sub(r'\s+', ' ', pg.locator('#dci-rules [data-rf=result]').inner_text())
            pg.click('#dci-rules [data-rules-close]')
            print('C6) li?:', hint[:80], '| Datum (US):', res[:90])
            ok6 = 'Discogs calls the release live (format)' in hint and '2022-01-11' in res
            # C7) source, edit note, Discogs tab
            src = pg.evaluate("(() => { const a = document.querySelector('[data-el=source] a'); return [a.href, a.textContent.trim()]; })()")
            pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
            pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
            note = pg.evaluate("document.getElementById('edit-note-text').value")
            opened_before = pg.evaluate("(window.__opened || []).length")
            pg.click('[data-el=sync] [data-act=sync-open]'); pg.wait_for_timeout(600)
            opened = pg.evaluate("window.__opened || []")
            print('C7) Quelle:', src, '| Notiz:', [l for l in note.splitlines() if l.startswith('Source') or 'from Discogs' in l][:2], '| Discogs-Tab:', opened[opened_before:])
            ok7 = src[0] == 'https://www.discogs.com/release/1234' and 'Testalbum' in src[1] and 'Source: https://www.discogs.com/release/1234' in note.splitlines() \
                and any(re.search(r'added \d+ credit relationships? from Discogs \(', l) for l in note.splitlines()) \
                and opened[opened_before:] == ['https://www.discogs.com/release/1234']
            print('    Fehler:', errs)
            results.append(all([ok1, ok2, ok3, ok4, ok5, ok6, ok7]) and not errs)
            print('    C1–C7:', [ok1, ok2, ok3, ok4, ok5, ok6, ok7])

            # C8) two linked releases: choose one, a typed URL, a release Discogs does not have, text without a release
            orig_ws = H.ws_release

            def ws():
                d = orig_ws()
                d['relations'].append({'target-type': 'url', 'type': 'discogs', 'url': {'resource': 'https://www.discogs.com/release/999'}})
                return d

            H.ws_release = ws
            pg2, errs2 = H.open_mb_edit(ctx, companion=False)
            pg2.on('dialog', lambda d: d.accept())
            pg2.wait_for_selector('#dci-open', timeout=20000)
            pg2.click('#dci-open')
            # [3.24.0] two linked Discogs releases: the dialog – 999 cannot be read, 1234 is preselected
            pg2.wait_for_selector('[data-el=links]:not([hidden])', timeout=20000)
            H.wait_for(pg2, "![...document.querySelectorAll('[data-el=links] [data-lel=count]')].some(s => /counting/.test(s.textContent))", 60)
            best = pg2.evaluate("[...document.querySelectorAll('[data-el=links] .dci-link-best .dci-link-name')].map(s => s.textContent.trim())")
            pg2.click('[data-el=links] [data-lf=remember]')
            pg2.click('[data-el=links] [data-lact=ok]')
            pg2.wait_for_selector('[data-f=discogs-pick]', timeout=20000, state='attached')
            opts = pg2.evaluate("[...document.querySelectorAll('[data-f=discogs-pick] option')].map(o => o.textContent.trim())")
            H.wait_for(pg2, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 60)
            rows = pg2.locator('tr.dci-row').count()
            H.src_menu(pg2)
            pg2.fill('[data-f=discogs-input]', 'https://www.discogs.com/release/999-Some-Title')
            pg2.click('[data-act=discogs-load]'); pg2.wait_for_timeout(1500)
            err999 = [m for m in pg2.locator('.dci-msg').all_inner_texts() if '999' in m]
            H.src_menu(pg2)
            pg2.fill('[data-f=discogs-input]', 'no release here')
            pg2.click('[data-act=discogs-load]'); pg2.wait_for_timeout(500)
            msgs = pg2.locator('.dci-msg').all_inner_texts()
            print('C8) Dialog vorgewählt:', best, '| Auswahl:', opts, '| Zeilen nach Wahl:', rows, '| 999:', err999[:1], '| Text ohne Release:', [m[:60] for m in msgs][-1:])
            ok8 = opts == ['Choose a Discogs release …', 'Discogs 1234', 'Discogs 999'] or (opts[1:] == ['Discogs 1234', 'Discogs 999'])
            ok8 = ok8 and best == ['Discogs 1234'] and rows > 5 and err999 and len(msgs) >= 1 and not errs2
            results.append(bool(ok8))
            b.close()
    # --- D) update from 2.19.1: the fresh start of 3.5.0 (generation 4); within generation 4 no reset -------------
    if 'D' in PARTS:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.wait_for_selector('#dci-open', timeout=20000)
            pg.evaluate("""() => { const set = (k, v) => localStorage.setItem(k, JSON.stringify(v));
          set('dci-notice-version', '2.19.1'); localStorage.setItem('dci-store-epoch', '3'); set('dci-lang', 'en'); set('dci-wattr-long', true);
          set('dci-user-rules', [{ id: 'U001', kind: 'instrument', discogs: 'gtr', instrument: 'guitar' }]); set('dci-date-pool:x', [{ id: 'd1' }]); }""")
            before = pg.evaluate("Object.keys(localStorage).filter(k => k.startsWith('dci-')).sort()")
            pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000); pg.wait_for_timeout(300)
            after = pg.evaluate("Object.keys(localStorage).filter(k => k.startsWith('dci-')).sort()")
            n = re.sub(r'\s+', ' ', pg.locator('#dci-notice').inner_text()) if pg.locator('#dci-notice').count() else ''
            print('D) Update von 2.19.1 – Speicher vorher:', before, '| nachher:', after)
            print('   Nachricht:', n[:220])
            ok_d = after == ['dci-notice-version', 'dci-store-epoch', 'dci-updated-from'] and 'Import 3.0.0' in n and 'Credits Importer 3.5.0' in n \
                and 'Import 2.19.0' not in n and 'reset once' in n and pg.evaluate("localStorage.getItem('dci-store-epoch')") == '4'
            # within generation 4 (as if 3.5.0 ran before): nothing is reset
            pg.evaluate("""() => { const set = (k, v) => localStorage.setItem(k, JSON.stringify(v)); localStorage.removeItem('dci-updated-from');
          set('dci-notice-version', '3.5.0'); set('dci-wattr-long', true); set('dci-date-pool:x', [{ id: 'd1' }]); }""")
            before2 = pg.evaluate("Object.keys(localStorage).filter(k => k.startsWith('dci-')).sort()")
            pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000); pg.wait_for_timeout(300)
            after2 = pg.evaluate("Object.keys(localStorage).filter(k => k.startsWith('dci-')).sort()")
            print('   innerhalb Generation 4 – vorher:', before2, '| nachher:', after2)
            results.append(ok_d and set(before2) <= set(after2) and not errs)
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_links():
    """Credits Importer 3.24.0: several linked releases of one source (collected item 51).
    A release linked to three Discogs releases: 1234, 1240 (more credits) and 999 (Discogs does not have it).
    A) The dialog "This release is linked to 3 Discogs releases" lists them; each is read in the background and counted
       (credits, companies, tracks); 999 "could not be read"; 1240 has the most data: bold, "most data", preselected.
    B) "Open all in background tabs": the three Discogs pages in background tabs (GM_openInTab, not active).
    C) "Import": Discogs 1240 is loaded, the log says it was chosen from three, the choice is remembered for this release;
       opened again, the dashboard loads 1240 at once (no dialog).
    D) Another choice by hand (1234, "Remember" unticked): 1234 is loaded, nothing remembered. E) "Cancel": the message
       "… Choose one above.", nothing loaded."""
    dg = H.discogs_release()
    more = dict(dg, id=1240, title='Testalbum (deluxe)')
    more['extraartists'] = dg['extraartists'] + [{'name': 'Keys Guy', 'anv': '', 'role': 'Piano', 'tracks': '', 'id': 3003, 'join': ''},
                                                 {'name': 'Guitar Guy', 'anv': '', 'role': 'Mandolin', 'tracks': '', 'id': 3002, 'join': ''},
                                                 {'name': 'Bass Man', 'anv': '', 'role': 'Arranged By', 'tracks': '', 'id': 3001, 'join': ''}]
    H.DG_API['/releases/1240'] = more
    H.DG_API['/releases/999'] = None
    orig_ws = H.ws_release


    def ws(full=False):
        d = orig_ws(full)
        d['relations'] += [{'target-type': 'url', 'type': 'discogs', 'url': {'resource': 'https://www.discogs.com/release/1240'}},
                           {'target-type': 'url', 'type': 'discogs', 'url': {'resource': 'https://www.discogs.com/release/999'}}]
        return d


    H.ws_release = ws
    DLG = """(() => { const d = document.querySelector('[data-el=links]'); if (!d || d.hidden) return null;
  return { title: d.querySelector('h3').textContent.trim(), rows: [...d.querySelectorAll('.dci-link-opt')].map(r => ({ name: r.querySelector('.dci-link-name').textContent.trim(),
    count: r.querySelector('[data-lel=count]').textContent.trim(), best: r.classList.contains('dci-link-best') && !r.querySelector('.dci-link-bestmark').hidden,
    bold: getComputedStyle(r.querySelector('.dci-link-name')).fontWeight, checked: r.querySelector('input').checked })) }; })()"""
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    SOURCE = "document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').slice(0, 40)"
    results = []


    def open_dlg(pg):
        pg.evaluate("() => { window.__tabs = []; window.GM_openInTab = (u, o) => { window.__tabs.push([u, o]); }; }")
        pg.click('#dci-open')
        pg.wait_for_selector('[data-el=links]:not([hidden])', timeout=20000)
        H.wait_for(pg, "![...document.querySelectorAll('[data-el=links] [data-lel=count]')].some(s => /counting/.test(s.textContent))", 60)
        pg.wait_for_timeout(300)
        return pg.evaluate(DLG)


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        # A)
        d = open_dlg(pg)
        print('A)', d['title'])
        for r in d['rows']:
            print('   ', r)
        rows = {r['name']: r for r in d['rows']}
        ok_a = d['title'] == 'This release is linked to 3 Discogs releases' and list(rows) == ['Discogs 1234', 'Discogs 1240', 'Discogs 999'] \
            and rows['Discogs 1240']['best'] and rows['Discogs 1240']['checked'] and rows['Discogs 1240']['bold'] == '700' \
            and not rows['Discogs 1234']['best'] and rows['Discogs 1234']['bold'] != '700' \
            and rows['Discogs 1240']['count'].startswith('“Testalbum (deluxe)” – credits: ') and 'tracks: 4' in rows['Discogs 1240']['count'] \
            and rows['Discogs 999']['count'].startswith('could not be read')
        results.append(ok_a)
        # B)
        pg.click('[data-el=links] [data-lact=tabs]')
        pg.wait_for_timeout(300)
        tabs = pg.evaluate('window.__tabs')
        print('B) Hintergrund-Tabs:', tabs)
        results.append([t[0] for t in tabs] == ['https://www.discogs.com/release/1234', 'https://www.discogs.com/release/1240', 'https://www.discogs.com/release/999']
                       and all(t[1] and t[1].get('active') is False for t in tabs))
        # C)
        pg.click('[data-el=links] [data-lact=ok]')
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
        pg.wait_for_timeout(500)
        src = pg.evaluate(SOURCE)
        chosen = [x for x in pg.evaluate(LOGS) if 'Chosen from' in x]
        kept = pg.evaluate(f"(JSON.parse(localStorage.getItem('dci-source-pick') || '{{}}')['{H.REL}'] || {{}}).id")
        print('C) Quelle:', src, '| Protokoll:', chosen, '| gemerkt:', kept)
        ok_c = 'Discogs 1240' in src and chosen == ['Chosen from 3 linked Discogs releases: Discogs 1240'] and kept == '1240'
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        H.wait_for(pg, f"{LOGS}.some(x => /Source chosen for this release before/.test(x))", 60)
        H.wait_for(pg, "/Discogs 1240/.test(document.querySelector('[data-el=source]').innerText)", 60)
        pg.wait_for_timeout(500)
        again = [pg.evaluate(SOURCE), pg.evaluate("!document.querySelector('[data-el=links]') || document.querySelector('[data-el=links]').hidden"),
                 [x for x in pg.evaluate(LOGS) if 'chosen' in x.lower()]]
        print('   neu geöffnet:', again)
        ok_c = ok_c and 'Discogs 1240' in again[0] and again[1] and any('Source chosen for this release before: Discogs' in x for x in again[2])
        results.append(ok_c)
        # D) another choice, not remembered
        pg.evaluate("localStorage.removeItem('dci-source-pick')")
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        open_dlg(pg)
        pg.click("[data-el=links] input[name=dci-link-pick][value='0']")
        pg.click('[data-el=links] [data-lf=remember]')
        pg.click('[data-el=links] [data-lact=ok]')
        H.wait_for(pg, "/Discogs 1234/.test(document.querySelector('[data-el=source]').innerText)", 60)
        pg.wait_for_timeout(800)
        d1 = [pg.evaluate(SOURCE), pg.evaluate("localStorage.getItem('dci-source-pick')")]
        print('D) von Hand 1234, nicht gemerkt:', d1)
        results.append('Discogs 1234' in d1[0] and d1[1] is None)
        # E) cancel
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        open_dlg(pg)
        pg.click('[data-el=links] [data-lact=cancel]')
        pg.wait_for_timeout(500)
        msgs = pg.locator('.dci-msg').all_inner_texts()
        e1 = [any('linked to 3 Discogs releases. Choose one above.' in m for m in msgs), pg.locator('tr.dci-row').count()]
        print('E) Abbrechen:', e1)
        results.append(e1 == [True, 0])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_supp():
    """Import 3.5.0 (stage 2, variant B): a second source supplements the loaded one, on request only.
    A) Discogs is loaded (physical media); "Supplement with" offers the linked Bandcamp album and a text; nothing is read
       from Bandcamp and no marks are shown before a click.
    B) "＋ Bandcamp …": the list "Supplements from Bandcamp" – a new role for an entry (Guitar Guy, trumpet on track 2), new
       entries (Anna Viola, all tracks; Test Band, found via its Bandcamp link), a row that differs (Keys Guy, synth: Discogs track 2,
       Bandcamp 1–2; not selected: Discogs stays), a line not recognized; Bass Man's bass is confirmed: marks DG BC.
    C) Test Band unticked, "Take over selected": Guitar Guy gets the trumpet row (mark BC), Anna Viola becomes an entry
       with a name suggestion; Test Band, the differing row and the line not recognized stay in the list.
    D) Staged: the edit note names the album ("Also from"), what came only from Bandcamp and where the sources differ.
    E) "Delete stored import …": the source chosen for the release, the supplement and the log go, the source is imported
       anew (no marks, no list).
    F) The old script on the page: this one stays out and says so; started second, it warns after 3 s.
    G) Import 3.8.0: a source the release does not link to, typed into the field of "Supplement with" (another Bandcamp
       album): it supplements like a linked one; the loaded source itself is refused."""
    import re

    H.attr(9120, 'trumpet', 14, 14)
    H.attr(9121, 'viola', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    ALBUM = 'https://testband.bandcamp.com/album/testalbum'
    BAND = 'https://testband.bandcamp.com/'
    H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
    H.BC_ARTISTS[BAND] = H.ARTISTS[3040]
    H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
    H.MB_SEARCH['artist'] = [{'id': H.uid('dddddddd', 42), 'name': 'Anna Viola', 'disambiguation': 'violist', 'score': 100}]
    CREDITS = 'Bass Man – bass\nTrumpet: Guitar Guy (track 2)\nKeys Guy – synth (tracks 1–2)\nViola: Anna Viola\nTest Band – guitar\nSee you on tour.'
    OTHER = 'https://otherband.bandcamp.com/album/live'
    H.BC_PAGES[OTHER] = H.bc_page({'artist': 'Other Band', 'current': {'title': 'Live', 'credits': 'Bass Man – bass\nTrumpet: Drum Guy (track 3)', 'about': ''},
                                   'trackinfo': [{'track_num': i + 1, 'title': t} for i, t in enumerate(H.TITLES)]})
    H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': CREDITS, 'about': ''},
                                   'trackinfo': [{'track_num': i + 1, 'title': t} for i, t in enumerate(H.TITLES)]})
    orig_ws = H.ws_release


    def ws():
        d = orig_ws()
        d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}})
        return d


    H.ws_release = ws
    logs = lambda pg, pat: [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if re.search(pat, x)]
    done = lambda pg, n: H.wait_for(pg, f"[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= {n}", 90)
    SUPP = """[...document.querySelectorAll('.dci-supp-row')].map(tr => [tr.querySelector('.dci-supp-kind').textContent.trim(),
  (tr.children[2].querySelector('strong') || tr.children[2]).textContent.trim(), tr.querySelector('input').checked, tr.children[5].textContent.replace(/\\s+/g, ' ').trim()])"""
    MARKS = """(name, role) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; const tr = [...g.querySelectorAll('tr.dci-row')].find(t => t.querySelector('.dci-drole').textContent.trim() === role);
  return tr ? [...tr.querySelectorAll('.dci-srcmark')].map(m => m.textContent.trim()) : 'no row'; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        # A) on request only; [3.26.0] the bar only on "+ Supplement" in the head
        closed = pg.evaluate("[!document.querySelector('.dci-suppbar'), document.querySelector('.dci-head [data-act=supp-open]').getAttribute('aria-expanded')]")
        H.open_supp(pg)
        print('A) vor „Ergänzen“ zu:', closed)
        bar = pg.evaluate("[...document.querySelectorAll('.dci-suppbar .dci-supp-btn')].map(b => b.textContent.trim())")
        a_ok = closed == [True, 'false'] and bar == ['＋ Bandcamp testband.bandcamp.com/album/testalbum', '＋ Text …'] and pg.evaluate("document.querySelector('[data-el=supp]').hidden") \
            and not pg.evaluate("window.__gmXhr.length") and not pg.locator('.dci-srcmark').count()
        print('A) Leiste:', bar, '| Bandcamp-Abrufe:', pg.evaluate("window.__gmXhr.length"), '| Marken:', pg.locator('.dci-srcmark').count())
        results.append(a_ok)
        # B) the list
        pg.click('[data-act=supp-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Supplement from Bandcamp/.test(li.textContent))", 60)
        H.wait_for(pg, "!document.querySelector('[data-el=busy]').textContent", 30)
        pg.wait_for_timeout(500)
        items = pg.evaluate(SUPP)
        summary = pg.locator('.dci-supp-head span').first.inner_text()
        hints = pg.evaluate("[...document.querySelectorAll('.dci-supp-row-entry')].map(tr => tr.children[6].textContent.replace(/\\s+/g, ' ').trim())")
        m_bass = pg.evaluate(f"({MARKS})('Bass Man', 'Bass')")
        m_keys = pg.evaluate(f"({MARKS})('Keys Guy', 'Synth')")
        print('B)', summary, '\n  ', items, '\n   Hinweise:', hints, '| Bass Man:', m_bass, '| Keys Guy:', m_keys)
        kinds = {(k, n): (sel, t) for k, n, sel, t in items}
        b_ok = kinds.get(('new role', 'Guitar Guy')) == (True, '2') and kinds.get(('new entry', 'Anna Viola')) == (True, 'all') \
            and kinds.get(('new entry', 'Test Band')) == (True, 'all') and kinds.get(('differs', 'Keys Guy'), (None, ''))[0] is False \
            and '1, 2' in kinds.get(('differs', 'Keys Guy'), (None, ''))[1] and ('not recognized', 'See you on tour.') not in kinds \
            and any(k == 'not recognized' for k, *_ in items) and summary.startswith('confirmed: 1 · new: 3 · differing: 1 · not recognized: 1') \
            and m_bass == ['DG', 'BC'] and m_keys == ['DG', 'BC ≠'] and any('suggestion: Anna Viola (violist)' in h for h in hints) \
            and any('via the Bandcamp link: Test Band' in h for h in hints)
        results.append(b_ok)
        # C) Test Band unticked, take over
        pg.evaluate("[...document.querySelectorAll('.dci-supp-row')].find(tr => tr.textContent.includes('Test Band')).querySelector('input').click()")
        pg.wait_for_timeout(200)
        pg.click('[data-act=supp-apply]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Taken over from Bandcamp: 2/.test(li.textContent))", 30)
        # the name search of the new entry runs after MusicBrainz's rate limit (slower when many tests run at once)
        H.wait_for(pg, "[...document.querySelectorAll('section.dci-group')].some(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Anna Viola' && s.querySelector('[data-act=name-use]'))", 30)
        pg.wait_for_timeout(500)
        m_gg = pg.evaluate(f"({MARKS})('Guitar Guy', 'Trumpet')")
        anna = pg.evaluate("[...document.querySelectorAll('section.dci-group')].filter(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Anna Viola').map(s => [s.className.match(/dci-st-(\\w+)/)[1], [...s.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.trim())])")
        left = pg.evaluate(SUPP)
        print('C) Guitar Guy Trumpet:', m_gg, '| Anna Viola:', anna, '| bleibt:', [(k, n) for k, n, *_ in left])
        c_ok = m_gg == ['BC'] and anna and anna[0][0] == 'missing' and anna[0][1] == ['Anna Viola (violist)'] \
            and [(k, n) for k, n, *_ in left] == [('differs', 'Keys Guy'), ('new entry', 'Test Band'), ('not recognized', '–')]
        results.append(c_ok)
        # D) staged: the edit note
        pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Anna Viola').querySelector('[data-act=name-use]').click()")
        pg.wait_for_timeout(300)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        note = pg.evaluate("document.getElementById('edit-note-text').value").splitlines()
        print('D) Notiz:', [l for l in note if not l.startswith('Script')][:6])
        d_ok = note[0] == 'Source: https://www.discogs.com/release/1234' and note[1] == f'Also from: {ALBUM}' \
            and any(l.startswith('1 credit also in Bandcamp; added from Bandcamp only: Guitar Guy, trumpet (tracks 2); Anna Viola, viola (all tracks).') for l in note) \
            and any(l.startswith('Sources differ: Keys Guy, synthesizer – Discogs: 2, Bandcamp: 1, 2; kept Discogs') for l in note)
        results.append(d_ok)
        # G) a typed source that is not linked
        H.open_supp(pg)
        pg.fill('[data-f=supp-url]', 'https://www.discogs.com/release/1234')
        pg.click('[data-act=supp-url]'); pg.wait_for_timeout(400)
        same = pg.locator('.dci-msg').all_inner_texts()
        H.open_supp(pg)
        pg.fill('[data-f=supp-url]', OTHER + '?from=x')
        pg.click('[data-act=supp-url]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Supplement from Bandcamp/.test(li.textContent)).length >= 2", 60)
        H.wait_for(pg, "!document.querySelector('[data-el=busy]').textContent", 30)
        pg.wait_for_timeout(500)
        chip = pg.locator('.dci-supp-on').all_inner_texts()
        items_g = pg.evaluate(SUPP)
        print('G) gleiche Quelle:', [m for m in same if 'already' in m][:1], '| Chip:', chip, '| Liste:', [(k, n, t) for k, n, _, t in items_g])
        g_ok = any('That is the source loaded already.' in m for m in same) and chip and 'otherband.bandcamp.com/album/live' in chip[0] \
            and ('new role', 'Drum Guy', '3') in [(k, n, t) for k, n, _, t in items_g]
        results.append(g_ok)
        # E) delete the stored import
        H.src_menu(pg)
        pg.select_option('[data-f=discogs-pick]', 'discogs|1234')
        done(pg, 2)
        pg.wait_for_timeout(500)
        picked = pg.evaluate(f"Object.keys(JSON.parse(localStorage.getItem('dci-source-pick') || '{{}}'))")
        H.src_menu(pg, 'forget-open')
        asked = pg.locator('.dci-forget strong').inner_text()
        pg.click('[data-act=forget-do]')
        done(pg, 1)
        pg.wait_for_timeout(800)
        after = pg.evaluate("localStorage.getItem('dci-source-pick')")
        first = pg.locator('#dci-log li').first.inner_text()
        print('E) gewählt vorher:', picked, '|', asked, '| nachher:', after, '| Protokoll beginnt:', first[9:80], '| Liste:',
              pg.evaluate("document.querySelector('[data-el=supp]').hidden"), '| Marken:', pg.locator('.dci-srcmark').count())
        e_ok = picked == [H.REL] and asked == 'Delete the stored import of this release?' and after is None and 'Stored import of this release deleted' in first \
            and pg.evaluate("document.querySelector('[data-el=supp]').hidden") and not pg.locator('.dci-srcmark').count() \
            and not logs(pg, 'Supplement from') and bool(logs(pg, 'Import complete'))
        results.append(e_ok)
        print('Fehler:', errs)
        results.append(not errs)
        # F) the old script on the page
        old = ctx.new_page()
        old.goto(f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
        old.add_script_tag(content="const s = document.createElement('style'); s.id = 'dci-styles'; document.head.appendChild(s);")
        old.add_script_tag(content=H.MAIN)
        old.wait_for_timeout(800)
        f1 = [old.locator('#dci-twice').count(), old.locator('#dci-open').count()]
        second, _ = H.open_mb_edit(ctx, companion=False)
        second.wait_for_selector('#dci-open', timeout=20000)
        second.evaluate("const s = document.createElement('style'); s.id = 'dci-styles'; document.head.appendChild(s);")
        second.wait_for_timeout(3500)
        f2 = second.locator('#dci-twice').inner_text() if second.locator('#dci-twice').count() else ''
        print('F) zuerst das alte:', f1, '| danach:', f2[:90])
        results.append(f1 == [1, 0] and f2.startswith('Two importer scripts are running on this page'))
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_tracksfit():
    """Credits Importer 3.24.1: the tracks of a source compared with MusicBrainz's – their number and their titles (collected
    item 52; S030, T038).
    A) The dialog of three linked Discogs releases: 1240 has the most credits but five tracks – yellow "differs from the
       MusicBrainz release: 5 tracks instead of 4"; preselected (bold) is 1234, the most data among those whose tracks fit,
       marked "most data with matching tracks"; 999 cannot be read.
    B) 1240 imported anyway: the yellow message in the dashboard ("… 5 tracks instead of 4 …") and in the log.
    C) Every import: titles with small differences ("Song One (Remastered)", "The Song Two", "Song Three – Live",
       "song four") fit – no message; D) two titles quite different ("Intro", "Outro") – "2 of 4 titles differ", with the
       titles in the message."""
    import copy

    dg = H.discogs_release()
    more = copy.deepcopy(dg)
    more.update(id=1240, title='Testalbum (deluxe)')
    more['extraartists'] += [{'name': 'Keys Guy', 'anv': '', 'role': 'Piano', 'tracks': '', 'id': 3003, 'join': ''},
                             {'name': 'Guitar Guy', 'anv': '', 'role': 'Mandolin', 'tracks': '', 'id': 3002, 'join': ''}]
    more['tracklist'].append({'position': '5', 'title': 'Bonus Track', 'type_': 'track', 'duration': '3:00', 'extraartists': []})
    H.DG_API['/releases/1240'] = more
    H.DG_API['/releases/999'] = None
    near = copy.deepcopy(dg)
    near.update(id=1250)
    for t, title in zip(near['tracklist'], ['Song One (Remastered)', 'The Song Two', 'Song Three – Live', 'song four']):
        t['title'] = title
    H.DG_API['/releases/1250'] = near
    far = copy.deepcopy(dg)
    far.update(id=1260)
    for t, title in zip(far['tracklist'], ['Intro', 'Outro', 'Song Three', 'Song Four']):
        t['title'] = title
    H.DG_API['/releases/1260'] = far
    orig_ws = H.ws_release
    LINKS = [1240, 999]


    def ws(full=False):
        d = orig_ws(full)
        d['relations'] = [r for r in d['relations'] if not (LINKS and LINKS[0] in (1250, 1260))] + \
            [{'target-type': 'url', 'type': 'discogs', 'url': {'resource': f'https://www.discogs.com/release/{i}'}} for i in LINKS]
        return d


    H.ws_release = ws
    DLG = """(() => { const d = document.querySelector('[data-el=links]'); if (!d || d.hidden) return null;
  return [...d.querySelectorAll('.dci-link-opt')].map(r => ({ name: r.querySelector('.dci-link-name').textContent.trim(),
    warn: r.querySelector('[data-lel=tracks]').hidden ? '' : r.querySelector('[data-lel=tracks]').textContent.trim(),
    warnBg: getComputedStyle(r.querySelector('[data-lel=tracks]')).backgroundColor,
    best: r.classList.contains('dci-link-best') ? r.querySelector('.dci-link-bestmark').textContent.trim() : '', checked: r.querySelector('input').checked })); })()"""
    MSG = "[...document.querySelectorAll('.dci-msg-tracks')].map(m => [m.textContent.replace(/\\s+/g, ' ').trim(), getComputedStyle(m).backgroundColor])"
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    results = []


    def dashboard(ctx, links):
        LINKS[:] = links
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        return pg, errs


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        # A)
        pg, errs = dashboard(ctx, [1240, 999])
        pg.click('#dci-open')
        pg.wait_for_selector('[data-el=links]:not([hidden])', timeout=20000)
        H.wait_for(pg, "![...document.querySelectorAll('[data-el=links] [data-lel=count]')].some(s => /counting/.test(s.textContent))", 60)
        pg.wait_for_timeout(300)
        rows = {r['name']: r for r in pg.evaluate(DLG)}
        for r in rows.values():
            print('   ', r)
        ok_a = rows['Discogs 1240']['warn'] == 'differs from the MusicBrainz release: 5 tracks instead of 4' and rows['Discogs 1240']['warnBg'] == 'rgb(255, 248, 219)' \
            and rows['Discogs 1234']['best'] == 'most data with matching tracks' and rows['Discogs 1234']['checked'] and not rows['Discogs 1240']['best'] \
            and rows['Discogs 1234']['warn'] == '' and rows['Discogs 999']['warn'] == ''
        print('A)', ok_a)
        results.append(ok_a)
        # B) 1240 anyway
        pg.click("[data-el=links] input[name=dci-link-pick][value='1']")
        pg.click('[data-el=links] [data-lf=remember]')
        pg.click('[data-el=links] [data-lact=ok]')
        H.wait_for(pg, "/Discogs 1240/.test(document.querySelector('[data-el=source]').innerText)", 60)
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
        msg = pg.evaluate(MSG)
        logs = [x for x in pg.evaluate(LOGS) if 'Tracks differ' in x or 'tracks differ' in x]
        print('B) Meldung:', msg, '\n   Protokoll:', logs)
        ok_b = len(msg) == 1 and msg[0][0].startswith('Discogs differs from the MusicBrainz release: 5 tracks instead of 4. Tracks are matched in order') \
            and msg[0][1] == 'rgb(255, 248, 219)' and any('Discogs 1240: tracks differ from MusicBrainz – 5 tracks instead of 4' in x for x in logs) \
            and any(x.startswith('Tracks differ from MusicBrainz: Discogs – 5 tracks instead of 4') for x in logs)
        results.append(ok_b)
        print('Fehler:', errs)
        results.append(not errs)
        pg.close()
        # C) small differences: no message; D) two titles quite different
        for name, links in [('C', [1250]), ('D', [1260])]:
            pg, errs = dashboard(ctx, links)
            pg.evaluate("localStorage.removeItem('dci-source-pick')")
            pg.click('#dci-open')
            H.wait_for(pg, f"/Discogs {links[0]}/.test(document.querySelector('[data-el=source]').innerText)", 60)
            H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
            msg = pg.evaluate(MSG)
            print(f'{name}) Discogs {links[0]}:', msg)
            if name == 'C':
                results.append(msg == [])
            else:
                results.append(len(msg) == 1 and 'Discogs differs from the MusicBrainz release: 2 of 4 titles differ (1: “Intro” ≠ “Song One”; 2: “Outro” ≠ “Song Two”)' in msg[0][0])
            print('Fehler:', errs)
            results.append(not errs)
            pg.close()
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
