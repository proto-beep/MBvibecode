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
from playwright.sync_api import sync_playwright
import harness as H

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
        ok1 = alias == [H.ARTISTS[3021][0]] and src_link == ['https://www.discogs.com/artist/3020', 'DiscogsAlias Guy']
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
        pg2.wait_for_selector('[data-f=discogs-pick]', timeout=20000)
        opts = pg2.evaluate("[...document.querySelectorAll('[data-f=discogs-pick] option')].map(o => o.textContent.trim())")
        pg2.select_option('[data-f=discogs-pick]', 'discogs|1234')
        H.wait_for(pg2, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 60)
        rows = pg2.locator('tr.dci-row').count()
        pg2.fill('[data-f=discogs-input]', 'https://www.discogs.com/release/999-Some-Title')
        pg2.click('[data-act=discogs-load]'); pg2.wait_for_timeout(1500)
        err999 = [m for m in pg2.locator('.dci-msg').all_inner_texts() if '999' in m]
        pg2.fill('[data-f=discogs-input]', 'no release here')
        pg2.click('[data-act=discogs-load]'); pg2.wait_for_timeout(500)
        msgs = pg2.locator('.dci-msg').all_inner_texts()
        print('C8) Auswahl:', opts, '| Zeilen nach Wahl:', rows, '| 999:', err999[:1], '| Text ohne Release:', [m[:60] for m in msgs][-1:])
        ok8 = opts == ['Choose a Discogs release …', 'Discogs 1234', 'Discogs 999'] or (opts[1:] == ['Discogs 1234', 'Discogs 999'])
        ok8 = ok8 and rows > 5 and err999 and len(msgs) >= 1 and not errs2
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
