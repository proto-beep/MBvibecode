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
from playwright.sync_api import sync_playwright
import harness as H

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
    pg.click('[data-act=text-open]')
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
