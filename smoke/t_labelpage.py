"""Credits Importer 3.22.1: an album on a label's Bandcamp page (collected item 46), and people not found through their
own link are searched by name.
A) A Bandcamp album of Yunclas on the page of the label "Grabaciones Autobombo" (its "data-band"): Yunclas gets no
   Bandcamp link (the page is not his), so not "no MB artist with this Bandcamp link" – he is searched by name: the
   release's artist Yunclas first, marked "release artist", then the other Yunclas; nothing assigned. The entry says
   whose page it is (with a link) and names MusicBrainz's label with that page, "a label of this release ✓"; the source
   line says "on the Bandcamp page of Grabaciones Autobombo", the log too. A click on the suggestion assigns it.
B) In Node: the account's name from "data-band" (else "og:site_name"); the artist's own page ("The Test Band" for Test
   Band; "Jane Roe & Friends" on Jane Roe's page is hers) keeps the link of the band, a label's page does not.
C) Discogs: a person whose Discogs link MusicBrainz does not have ("no MB artist with this Discogs link") gets the
   same-named entries as suggestions, the release's artist first."""
import json
import os
import subprocess
from playwright.sync_api import sync_playwright
import harness as H

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, '..', 'mb-vibecode-credits-importer.user.js')
YUN = H.uid('dddddddd', 60)
YUN2 = H.uid('dddddddd', 61)
LABEL = H.uid('eeeeeeee', 60)
PAGE = 'https://grabacionesautobombo.bandcamp.com/'
ALBUM = PAGE + 'album/xixon'
H.RELEASE_AC[:] = [(YUN, 'Yunclas', 'Yunclas', '')]
H.MB_SEARCH['artist'] = [{'id': YUN, 'name': 'Yunclas', 'disambiguation': '', 'score': 100},
                         {'id': YUN2, 'name': 'Yunclas', 'disambiguation': 'Spanish rapper', 'score': 100}]
H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Yunclas', 'current': {'title': 'Xixón', 'credits': 'Recorded by Yunclas in Xixon, Asturies, Spain', 'about': '',
                                'release_date': '01 Jan 2020 00:00:00 GMT'},
                               'trackinfo': [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]},
                              band='Grabaciones Autobombo')
for i, t in enumerate(H.TITLES):
    H.BC_PAGES[f'{PAGE}track/song-{i + 1}'] = H.bc_page({'current': {'title': t, 'credits': ''}}, band='Grabaciones Autobombo')
orig_ws, orig_url = H.ws_release, H.ws_url


def ws(full=False):
    d = orig_ws(full)
    d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
    d['label-info'] = [{'catalog-number': 'GA01', 'label': {'id': LABEL, 'name': 'Grabaciones Autobombo'}}]
    for m in d['media']:
        m['format'] = 'Digital Media'
    return d


def ws_url(query):
    if PAGE in [x for x in __import__('urllib.parse').parse.parse_qs(query).get('resource', [])]:
        return {'urls': [{'resource': PAGE, 'relations': [{'target-type': 'label', 'label': {'id': LABEL, 'name': 'Grabaciones Autobombo', 'disambiguation': ''}}]}]}
    return orig_url(query)


H.ws_release = ws
H.ws_url = ws_url
GROUPS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => ({ key: g.dataset.group, cls: g.className,
  name: g.querySelector('.dci-gname strong').textContent.trim(), head: g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(),
  match: (g.querySelector('.dci-gmatch .dci-badge') || { textContent: '' }).textContent.trim(),
  sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()),
  page: (g.querySelector('.dci-pageof') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim(),
  pageLink: (g.querySelector('.dci-pageof a') || { href: '' }).href, mbLink: (g.querySelector('.dci-gname .dci-mblink, .dci-gmatch .dci-mblink') || { href: '' }).href })))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
    pg.wait_for_timeout(1000)
    g = {x['name']: x for x in pg.evaluate(GROUPS)}
    yun = g.get('Yunclas') or {'sugg': [], 'page': '', 'match': '', 'cls': '', 'head': '', 'pageLink': '', 'key': ''}
    src = pg.evaluate("document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').slice(0, 120)")
    logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'Bandcamp page' in x or 'with this Bandcamp link' in x]
    print('A) Yunclas:', yun['head'], '|', yun['match'], '| Vorschläge:', yun['sugg'])
    print('   Hinweis:', yun['page'], yun['pageLink'])
    print('   Quelle:', src, '\n   Protokoll:', logs)
    ok_a = 'Bandcamp' not in yun['head'] and 'not assigned yet (no link)' in yun['match'] and 'dci-st-missing' in yun['cls'] \
        and yun['sugg'][:2] == ['Yunclas release artist', 'Yunclas (Spanish rapper)'] \
        and 'The Bandcamp page of this album belongs to Grabaciones Autobombo – not Yunclas\'s own page' in yun['page'] and yun['pageLink'] == PAGE \
        and 'in MusicBrainz: label Grabaciones Autobombo – a label of this release ✓' in yun['page'] \
        and 'on the Bandcamp page of Grabaciones Autobombo' in src \
        and any('Yunclas: the album is on the Bandcamp page of Grabaciones Autobombo' in x for x in logs) \
        and any('label Grabaciones Autobombo in MusicBrainz – a label of this release' in x for x in logs) and not any('with this Bandcamp link' in x for x in logs)
    pg.click(f"section[data-group=\"{yun['key']}\"] [data-act=name-use]")
    pg.wait_for_timeout(400)
    after = {x['name']: x for x in pg.evaluate(GROUPS)}.get('Yunclas', {})
    print('   nach Klick:', after.get('cls'), after.get('mbLink'))
    ok_a = ok_a and 'dci-st-manual' in after.get('cls', '') and after.get('mbLink', '').endswith(YUN)
    results.append(ok_a)
    print('Fehler:', errs)
    results.append(not errs)
    pg.close()

    # B) in Node
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const bc = m.SOURCES.bandcamp;
const page = (band, meta) => `<html><head>${meta ? `<meta property="og:site_name" content="${meta}">` : ''}</head><body><script data-tralbum="{}"${band ? ` data-band="${band.replace(/"/g, '&quot;')}"` : ''}></script></body></html>`;
const names = [bc.bandPageName(page(JSON.stringify({ id: 1, name: 'Grabaciones Autobombo' }))), bc.bandPageName(page('', 'Jane Roe')), bc.bandPageName(page('', ''))];
const ctx = { isRole: (x) => /^guitar/i.test(x), isCompanyRole: () => false, resolveTracks: () => null, sig: () => 'x' };
const data = (artist) => ({ artist, current: { credits: `Guitar – ${artist}` }, trackinfo: [{ track_num: 1, title: 'A' }] });
const id = (artist, pageName) => { const r = bc.toRelease(data(artist), 'https://x.bandcamp.com/album/a', [], ctx, { pageName });
  const c = r.credits[0]; return [c.who.id || '', !!c.who.pageOf, r.band.own]; };
console.log(JSON.stringify({ names, own: id('Test Band', 'The Test Band'), friends: id('Jane Roe & Friends', 'Jane Roe'), label: id('Yunclas', 'Grabaciones Autobombo'), none: id('Test Band', '') }));
"""
    out = json.loads(subprocess.run(['node', '-e', NODE, SCRIPT], capture_output=True, text=True, check=True).stdout)
    print('B)', out)
    ok_b = out['names'] == ['Grabaciones Autobombo', 'Jane Roe', ''] and out['own'] == ['https://x.bandcamp.com/', False, True] \
        and out['friends'] == ['', False, True] and out['label'] == ['', True, False] and out['none'] == ['https://x.bandcamp.com/', False, True]
    results.append(ok_b)

    # C) Discogs: a person MusicBrainz does not have with this Discogs link
    H.ws_release, H.ws_url = orig_ws, orig_url
    orig_dg = H.discogs_release

    def dg():
        d = orig_dg()
        d['extraartists'].append({'name': 'Yunclas', 'anv': '', 'role': 'Mastered By', 'tracks': '', 'id': 3060, 'join': ''})
        return d

    H.discogs_release = dg
    ctx2 = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx2, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
    pg.wait_for_timeout(1000)
    g = {x['name']: x for x in pg.evaluate(GROUPS)}
    yd = g.get('Yunclas') or {'sugg': [], 'match': '', 'head': ''}
    others = {k: v['sugg'] for k, v in g.items() if k != 'Yunclas' and v['sugg']}
    print('C) Yunclas (Discogs):', yd['head'], '|', yd['match'], '| Vorschläge:', yd['sugg'], '| andere mit Vorschlägen:', others)
    ok_c = 'Discogs' in yd['head'] and 'no MB artist with this Discogs link' in yd['match'] and yd['sugg'][:2] == ['Yunclas release artist', 'Yunclas (Spanish rapper)'] \
        and not others
    results.append(ok_c)
    print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
