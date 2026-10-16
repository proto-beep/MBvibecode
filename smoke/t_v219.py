"""Import 2.19.0. Suggestions look the same everywhere: yellow with an amber dashed border, the coloured left edge
stays (date matrix: purple, works matrix: blue); "li?" too; dates and track groups from the Discogs notes in the
pools until they are used (dropped somewhere). Not suggestions: "mixed" in "Attributes for all" is half filled,
"waits for a work" grey dotted. "Commissioned By" → commissioned on the works (R099, companies C037): without a track
list a suggestion on all works (S024; × takes one out, the others are staged), with tracks set on those works.
"Live Recording By" → recording (R031, no role credit) and a hint for "live" (S021): "li?" on the existing link of
its tracks, "li" preselected on their new links, nothing on other tracks."""
import re
from playwright.sync_api import sync_playwright
import harness as H
from common_rows import drag

for i, n in [(567, 'cover'), (578, 'live'), (750, 'medley')]:
    H.attr(i, n, i)
H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578, 750))
H.lt(889, 'b1d1d1d1-0000-4000-8000-000000000889', 'commissioned', 'artist', 'work', ())
H.lt(890, 'b1d1d1d1-0000-4000-8000-000000000890', 'commissioned', 'label', 'work', ())
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
H.ARTISTS[3010] = (H.uid('dddddddd', 10), 'Commissioner C')
H.ARTISTS[3011] = (H.uid('dddddddd', 11), 'Live Eng')
H.ARTISTS[3012] = (H.uid('dddddddd', 12), 'Commissioner D')
H.COMPANIES[1006] = ('label', H.uid('eeeeeeee', 6), 'BBC Proms')
orig_rel = H.discogs_release


def rel():
    d = orig_rel()
    d['notes'] += '\nPublished by Pub Co (1, 3).'
    ex = lambda name, role, i, tracks='': {'name': name, 'anv': '', 'role': role, 'tracks': tracks, 'id': i, 'join': ''}
    d['extraartists'] += [ex('Commissioner C', 'Commissioned By', 3010), ex('Commissioner D', 'Commissioned By', 3012, '2'),
                          ex('Live Eng', 'Live Recording By', 3011, '1, 2')]
    d['companies'].append({'name': 'BBC Proms', 'entity_type_name': 'Commissioned By', 'id': 1006, 'catno': ''})
    return d


H.discogs_release = rel
YELLOW = 'rgb(255, 248, 219)'
STYLE = """(el) => { if (!el) return null; const s = getComputedStyle(el);
  return { bg: s.backgroundColor, img: s.backgroundImage.slice(0, 15), top: s.borderTopStyle, topc: s.borderTopColor, left: s.borderLeftStyle, leftc: s.borderLeftColor }; }"""
COLS = """(() => { const out = {};
  document.querySelectorAll('.dci-matrix th[data-colhead]').forEach((th) => {
    const name = (th.querySelector('.dci-mx-colname .dci-mblink, .dci-mx-colname strong') || {}).textContent.replace(/^MB/, '').trim();
    out[name] = [...document.querySelectorAll(`.dci-mx-cell[data-col="${th.dataset.colhead}"]`)].filter(c => c.classList.contains('dci-mx-on'))
      .map(c => (Number(c.closest('tr').dataset.work) + 1) + (c.classList.contains('dci-mx-sugg') ? 's' : ''));
  }); return out; })()"""
PILLS = """(sel) => [...document.querySelectorAll(sel + ' .dci-wattrs .dci-wpill')].map(b => [b.textContent.trim(),
  (b.className.match(/dci-wpill-(\\w+)/) || [])[1], b.title])"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(1500)
    style = lambda sel: pg.evaluate(STYLE, pg.query_selector(sel))
    cols = lambda: pg.evaluate(COLS)
    colkey = lambda name: pg.evaluate(f"[...document.querySelectorAll('.dci-matrix th[data-colhead]')].find(th => th.textContent.includes({name!r})).dataset.colhead")
    cell = lambda name, track: f'.dci-matrix tr[data-work="{track - 1}"] .dci-mx-cell[data-col="{colkey(name)}"]'
    pills = lambda sel: pg.evaluate(PILLS, sel)
    chips = lambda: pg.evaluate("""[...document.querySelectorAll('.dci-pools-body .dci-pchip-date, .dci-pools-body .dci-pchip-tg')]
      .map(c => [c.querySelector('.dci-chip-main').textContent.replace(/\\s+/g, ' ').trim().slice(0, 28), c.classList.contains('dci-pchip-sugg')])""")

    # A) the look: suggestions yellow and dashed with their coloured left edge; "waits" grey dotted
    c0 = chips()
    sugg_tg = style('.dci-pools-body .dci-pchip-tg.dci-pchip-sugg')
    auto = style('.dci-dm-cell.dci-dm-auto')
    mxs = style(f'{cell("Commissioner C", 1)} .dci-mxchip-sugg')
    wait = style(f'{cell("Commissioner C", 4)} .dci-mxchip-wait')
    w1 = 'tr[data-work="0"][data-mrow^="w:0"]'
    li1 = [x for x in pills(w1) if x[0].startswith('li')]
    hint = style(f'{w1} .dci-wpill-hint')
    print('A1) Pools (Text, Vorschlag):', c0)
    print('    Track-Gruppe:', sugg_tg, '\n    Daten-Matrix:', auto)
    print('    Werk-Matrix Vorschlag:', mxs, '\n    wartet:', wait)
    print('    li? Track 1:', [x[:2] for x in li1], li1[0][2] if li1 else '', '|', hint)
    ok_a = all(s for _, s in c0) and len(c0) >= 3 and any('Pub Co' in t for t, _ in c0) \
        and sugg_tg['bg'] == YELLOW and sugg_tg['top'] == 'dashed' \
        and auto['bg'] == YELLOW and auto['top'] == 'dashed' and auto['left'] == 'solid' and auto['leftc'] == 'rgb(115, 109, 171)' \
        and mxs['bg'] == YELLOW and mxs['top'] == 'dashed' and mxs['left'] == 'solid' and mxs['leftc'] == 'rgb(61, 95, 158)' \
        and wait['top'] == 'dotted' and wait['bg'] == 'rgb(255, 255, 255)' \
        and li1 and li1[0][1] == 'hint' and li1[0][2].startswith('Live recording – Discogs credits “Live Recording By” (Live Eng) for this track.') \
        and 'Live release' not in li1[0][2] and hint['bg'] == YELLOW and hint['top'] == 'dashed'
    # new works for tracks 2 and 3: "li" preselected only on track 2 (Live Recording By on 1, 2); the head is "mixed"
    pg.click('tr[data-work="1"] [data-act=work-pending]'); pg.wait_for_timeout(300)
    pg.click('tr[data-work="2"] [data-act=work-pending]'); pg.wait_for_timeout(300)
    p2, p3 = 'tr[data-work="1"][data-mrow^="p:1"]', 'tr[data-work="2"][data-mrow^="p:2"]'
    li2 = [x for x in pills(p2) if x[0].startswith('li')]
    head = pg.evaluate("[...document.querySelectorAll('.dci-wattrs-all .dci-wpill')].map(b => [b.textContent.trim(), (b.className.match(/dci-wpill-(\\w+)/) || [])[1]])")
    mixed = style('.dci-wattrs-all .dci-wpill-mixed')
    print('A2) li Track 2:', [x[:2] for x in li2], li2[0][2][:120] if li2 else '', '| Track 3:', pills(p3))
    print('    Kopf:', head, '| gemischt:', mixed)
    ok_a = ok_a and li2 and li2[0][1] == 'on' and 'preselected (rule S021)' in li2[0][2] and '“Live Recording By” (Live Eng) for this track' in li2[0][2] \
        and pills(p3) == [] and ['li', 'mixed'] in head and mixed['top'] == 'solid' and mixed['img'].startswith('linear-gradient')
    results.append(bool(ok_a))

    # B) Commissioned By: without tracks a suggestion on all works (person and label), with tracks set
    c1 = cols()
    th = pg.evaluate(f"document.querySelector('[data-colhead=\"{colkey('Commissioner C')}\"] .dci-mx-roles').textContent.replace(/\\s+/g, ' ').trim()")
    title = pg.evaluate(f"document.querySelector('{cell('Commissioner C', 2)} .dci-mxchip-sugg').title")
    print('B1) Spalten:', {k: v for k, v in c1.items() if k in ('Commissioner C', 'Commissioner D', 'BBC Proms')})
    print('    Kopf Commissioner C:', th, '| Titel:', title)
    ok_b = c1.get('Commissioner C') == ['1s', '2s', '3s', '4s'] and c1.get('BBC Proms') == ['1s', '2s', '3s', '4s'] \
        and c1.get('Commissioner D') == ['2'] and th.startswith('commissioned') and '4 suggestions' in th \
        and 'commissioned' in title and 'without tracks' in title
    pg.click(f'{cell("Commissioner C", 1)} [data-act=mx-sugg-ok]'); pg.wait_for_timeout(200)
    pg.click(f'{cell("Commissioner C", 3)} [data-act=mx-sugg-no]'); pg.wait_for_timeout(200)
    c2 = cols().get('Commissioner C')
    print('B2) ✓ Track 1, × Track 3:', c2)
    ok_b = ok_b and c2 == ['1', '2s', '4s']
    # the rules: R099 (not R095 any more), R031 for the live recording, without role credit
    pg.click('[data-act=rules]'); pg.wait_for_timeout(200)
    pg.fill('#dci-rules [data-rf=test]', 'Commissioned By, Live Recording By, Recorded Live By, Engineer [Live Recording]'); pg.wait_for_timeout(200)
    res = re.sub(r'\s+', ' ', pg.locator('#dci-rules [data-rf=result]').inner_text())
    pg.click('#dci-rules [data-rules-close]')
    print('B3) Regeltest:', res[:400])
    live = pg.evaluate("""[...document.querySelectorAll('[data-group] tr.dci-row')].filter(tr => tr.closest('[data-group]').querySelector('.dci-gname').textContent.includes('Live Eng'))
      .map(tr => { const v = (f) => { const e = tr.querySelector('[data-f=' + f + ']'); return e ? (e.tagName === 'SELECT' ? (e.options[e.selectedIndex] || {}).text : e.value) : '-'; };
        return [v('type'), v('role-credit'), [...tr.querySelectorAll('.dci-ruleid')].map(x => x.textContent.trim())]; })""")
    print('B4) Zeile Live Eng:', live)
    ok_b = ok_b and 'R099' in res and res.count('R031') >= 3 and 'R095' not in res \
        and live and live[0][0] == 'recording' and live[0][1] in ('', '-') and 'R031' in live[0][2] and 'W007' in live[0][2]
    results.append(bool(ok_b))

    # C) pool entries from the notes: used once dropped somewhere (no longer a suggestion, also after a new render)
    bass = pg.evaluate("[...document.querySelectorAll('.dci-group')].find(g => g.querySelector('.dci-gname').textContent.includes('Bass Man')).querySelector('tr.dci-row').dataset.row")
    did = pg.evaluate("document.querySelector('.dci-pools-body .dci-pchip-date.dci-pchip-sugg').dataset.id")
    gid = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Pub Co')).dataset.id")
    drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{did}"] .dci-chip-main', f'tr[data-row="{bass}"] .dci-c-date')
    drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', f'tr[data-row="{bass}"] .dci-c-tracks')
    pg.click('[data-act=pools-toggle]'); pg.wait_for_timeout(150)
    pg.click('[data-act=pools-toggle]'); pg.wait_for_timeout(150)
    used = pg.evaluate(f"""[document.querySelector('.dci-pools-body .dci-pchip-date[data-id="{did}"]').classList.contains('dci-pchip-sugg'),
      document.querySelector('.dci-pools-body .dci-pchip-tg[data-id="{gid}"]').classList.contains('dci-pchip-sugg'),
      document.querySelectorAll('.dci-pools-body .dci-pchip-date.dci-pchip-sugg').length,
      JSON.parse(localStorage.getItem('dci-track-pool') || '[]').length]""")
    print('C1) nach dem Ziehen – Datum noch Vorschlag, Gruppe noch Vorschlag, weitere Daten als Vorschlag:', used[:3], '| Stil danach:', style(f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"]'))
    ok_c = used[0] is False and used[1] is False and used[2] >= 1
    results.append(ok_c)

    # D) staged: commissioned on the works of tracks 1, 2 (C; 3 taken out, 4 has no work), 2 (D), 1–3 (BBC Proms);
    # "live" only on the new link of track 2
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
    pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
    pg.wait_for_timeout(800)
    st = pg.evaluate("""(() => { const added = MB.relationshipEditor.state.added;
      const ids = (r) => r && r.attributes && r.attributes.__tree ? r.attributes.__tree.map(a => a.typeID || a.type.id) : [];
      const by = (lt) => added.filter(x => x.linkTypeID === lt).map(x => x.entity0.name || x.entity0.gid).sort();
      return { c889: by(889), c890: by(890), perf: added.filter(x => x.linkTypeID === 278).map(x => [x.entity0.gid.slice(-1), ids(x)]).sort() }; })()""")
    print('D1) Editor:', st)
    ok_d = st['c889'] == ['Commissioner C', 'Commissioner C', 'Commissioner D'] and st['c890'] == ['BBC Proms'] * 3 \
        and st['perf'] == [['2', [578]], ['3', []]]
    results.append(ok_d)
    print('Fehler:', errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
