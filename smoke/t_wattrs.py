"""Works matrix attributes of the recording–work links (ac, co, de, in, ka, li, me, pa): the release group is Live in
MusicBrainz → "li" preselected only on new links (S021); the link that exists in MusicBrainz is only offered "li?"
(a deliberate click adds it as an edit). Works with an attribute (set or offered) are always open, others closed
(▸ opens, "open all rows"); "Attributes for all" in the head; "spell out" is remembered. Staged: the existing link
gets "cover", the new link "live". "Music And Lyrics By" for the whole release (R098): writer, "Song" preselected
for new works (S020), R098 in the column head."""
from playwright.sync_api import sync_playwright
import harness as H

for i, n in [(567, 'cover'), (578, 'live'), (750, 'medley'), (579, 'partial'), (580, 'instrumental')]:
    H.attr(i, n, i)
H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578, 750, 579, 580))
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
orig_ws, orig_rel = H.ws_release, H.discogs_release


def ws():
    d = orig_ws()
    d['release-group']['secondary-types'] = ['Live']
    return d


def rel():
    d = orig_rel()
    d['extraartists'].append({'name': 'Writer Z', 'anv': '', 'role': 'Music And Lyrics By', 'tracks': '', 'id': 3009, 'join': ''})
    return d


H.ws_release, H.discogs_release = ws, rel
# [label, state, title] of the attribute buttons of a matrix row ('' when closed)
PILLS = """(sel) => [...document.querySelectorAll(sel + ' .dci-wattrs .dci-wpill')].map(b => [b.textContent.trim(),
  (b.className.match(/dci-wpill-(\\w+)/) || [])[1], b.title.slice(0, 90)])"""
SUM = "(sel) => (document.querySelector(sel + ' .dci-wattr-sum') || {}).textContent ? document.querySelector(sel + ' .dci-wattr-sum').textContent.replace(/\\s+/g, ' ').trim() : ''"
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    w1 = 'tr[data-work="0"][data-mrow^="w:0"]'
    p2 = 'tr[data-work="1"][data-mrow^="p:1"]'
    p3 = 'tr[data-work="2"][data-mrow^="p:2"]'
    pills = lambda sel: pg.evaluate(PILLS, sel)
    state = lambda sel: {x[0].rstrip('?✎✓'): x[1] for x in pills(sel)}

    # A) the existing link: "li?" offered, not set; the row is open; short forms sorted
    a1 = pills(w1)
    print('A1) Track 1 (Werk in MB):', a1)
    ok_a = [x[0] for x in a1] == ['co', 'in', 'li?', 'me', 'pa'] and state(w1)['li'] == 'hint' and 'Live release' in a1[2][2]
    head = pg.evaluate("[...document.querySelectorAll('.dci-wattrs-all .dci-wpill')].map(b => [b.textContent.trim(), (b.className.match(/dci-wpill-(\\w+)/) || [])[1]])")
    print('    Kopf „Attribute für alle“:', head)
    ok_a = ok_a and [h[0] for h in head] == ['co', 'in', 'li', 'me', 'pa'] and all(h[1] == 'off' for h in head)
    r098 = pg.evaluate("[...document.querySelectorAll('[data-colhead]')].filter(h => h.textContent.includes('Writer Z')).map(h => (h.querySelector('[data-rule=R098]') || {}).title || '')")
    wtype = pg.evaluate("(() => { const s = document.querySelector('[data-f=work-type]'); return [s.options[s.selectedIndex].text, (s.parentElement.querySelector('.dci-ruleref') || {}).textContent || '']; })()")
    print('A2) Spalte Writer Z, R098:', r098, '| Typ neuer Werke:', wtype)
    ok_a = ok_a and any('Music and lyrics in one credit' in x for x in r098) and wtype == ['Song', 'S020']
    results.append(ok_a)

    # B) a click on "co" adds it (✎, an edit); "li?" clicked and clicked again: back to offered
    pg.click(f'{w1} .dci-wpill[data-attr=cover]'); pg.wait_for_timeout(200)
    pg.click(f'{w1} .dci-wpill[data-attr=live]'); pg.wait_for_timeout(200)
    mid = state(w1)['li']
    pg.click(f'{w1} .dci-wpill[data-attr=live]'); pg.wait_for_timeout(200)
    b1 = pills(w1)
    print('B1) Track 1 nach co, li, li:', b1, '| li zwischendurch:', mid)
    ok_b = state(w1)['co'] == 'on' and b1[0][0] == 'co✎' and mid == 'on' and state(w1)['li'] == 'hint'
    # new works for tracks 2 and 3: "li" preselected (S021); track 3 unticked → closed
    pg.click('tr[data-work="1"] [data-act=work-pending]'); pg.wait_for_timeout(300)
    pg.click('tr[data-work="2"] [data-act=work-pending]'); pg.wait_for_timeout(300)
    b2 = pills(p2)
    print('B2) Track 2 (neues Werk):', [x[:2] for x in b2], '|', b2[2][2][:60])
    ok_b = ok_b and state(p2)['li'] == 'on' and 'preselected (rule S021)' in b2[2][2]
    pg.click(f'{p3} .dci-wpill[data-attr=live]'); pg.wait_for_timeout(200)
    closed = (pills(p3), pg.evaluate(SUM, p3))
    pg.click(f'{p3} [data-act=mx-wattr-open]'); pg.wait_for_timeout(200)
    opened = [x[0] for x in pills(p3)]
    pg.click(f'{p3} [data-act=mx-wattr-open]'); pg.wait_for_timeout(200)
    pg.click('[data-act=mx-wattr-openall]'); pg.wait_for_timeout(200)
    all_open = [x[0] for x in pills(p3)]
    pg.click('[data-act=mx-wattr-openall]'); pg.wait_for_timeout(200)
    print('B3) Track 3 ohne Attribut: zu', closed, '| ▸ auf:', opened, '| alle Zeilen auf:', all_open, '| wieder zu:', pills(p3))
    ok_b = ok_b and closed[0] == [] and 'none' in closed[1] and len(opened) == 5 and len(all_open) == 5 and pills(p3) == []
    # Attributes for all: "me" on for all, then off again
    pg.click('.dci-wattrs-all .dci-wpill[data-attr=medley]'); pg.wait_for_timeout(200)
    on_all = [state(s).get('me') for s in (w1, p2, p3)]
    pg.click('.dci-wattrs-all .dci-wpill[data-attr=medley]'); pg.wait_for_timeout(200)
    off_all = [state(s).get('me') for s in (w1, p2)] + [pills(p3)]
    print('B4) „me“ für alle:', on_all, '| wieder aus:', off_all)
    ok_b = ok_b and on_all == ['on', 'on', 'on'] and off_all == ['off', 'off', []]
    # spell out: names instead of short forms, remembered
    pg.click('[data-act=mx-wattr-long]'); pg.wait_for_timeout(200)
    long_ = [x[0] for x in pills(w1)]
    stored = pg.evaluate("localStorage.getItem('dci-wattr-long')")
    pg.click('[data-act=mx-wattr-long]'); pg.wait_for_timeout(200)
    print('B5) ausgeschrieben:', long_, '| gespeichert:', stored, '| wieder kurz:', [x[0] for x in pills(w1)])
    ok_b = ok_b and long_[0] == 'cover✎' and long_[2] == 'live?' and stored == 'true' and pg.evaluate("localStorage.getItem('dci-wattr-long')") is None
    results.append(ok_b)

    # C) staging: the existing link gets "cover" (not "live"), the new links: track 2 "live", track 3 nothing
    pg.evaluate(f"""() => {{ const re = MB.relationshipEditor;
      re.state = {{ ...re.state, existingRels: [{{ id: 9101, linkTypeID: 278, entity0: {{ gid: '{H.REC[0]}', entityType: 'recording', id: 5001, name: 'Song One' }},
        entity1: {{ gid: '{H.WORK1}', entityType: 'work', id: 7001, name: 'Song One' }}, begin_date: null, end_date: null, ended: false,
        attributes: null, entity0_credit: '', entity1_credit: '', _status: 0 }}] }}; }}""")
    if not pg.locator('[data-f=editnote]').is_checked():
        pg.check('[data-f=editnote]')
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
    pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
    st = pg.evaluate("""(() => { const ids = (r) => r && r.attributes && r.attributes.__tree ? r.attributes.__tree.map(a => a.typeID || a.type.id) : [];
      const added = MB.relationshipEditor.state.added;
      const ex = added.find(x => x.id === 9101);
      const nl = added.filter(x => x.linkTypeID === 278 && x.id !== 9101);
      return { existing: ex ? [ids(ex), ex._status] : null, newLinks: nl.map(x => [x.entity0.gid.slice(-1), ids(x)]).sort() }; })()""")
    note = pg.evaluate("document.getElementById('edit-note-text').value")
    print('C1) Editor:', st)
    print('    Bearbeitungsnotiz:', [l[-90:] for l in note.splitlines() if 'attribute' in l])
    print('    Track 1 danach:', pills(w1)[0])
    ok_c = st['existing'] == [[567], 2] and st['newLinks'] == [['2', [578]], ['3', []]] \
        and any('added attributes (live, cover …) to 1 existing link between recording and work' in l for l in note.splitlines()) \
        and pills(w1)[0][0] == 'co✎✓'
    results.append(ok_c)
    print('Fehler:', errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
