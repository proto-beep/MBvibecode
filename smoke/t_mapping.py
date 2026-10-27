"""Mapping: roles, questions, suggestions, mastering, special artists, fixes (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: rules, v217, v219, mastering, special, recheck, engineers – each the former smoke/t_<case>.py, unchanged; `python3 t_mapping.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_rules():
    """Mapping: "Mix", "Recording", "Engineer [Mix]", "Engineer [Recording]" without role credit (W006, W007);
    "Engineer [Mix, Recording, Assistant]" is one row per task (S018); "Trumpet [Pocket Trumpet]" is the instrument
    pocket trumpet without role credit. Rule ids next to ⓘ open "Mapping rules" at that rule (highlighted, also
    when a search hid it). Dragging out of the dates block: the list scrolls up only after the pointer was further
    down once and then stays below the block a moment."""
    import re

    for i, n in [(9120, 'trumpet'), (9121, 'pocket trumpet')]:
        H.attr(i, n, 14, 14)
        H.LINKED['link_attribute_type'][str(i)] = H.ATTRS[i]
    # as in MusicBrainz: mix, recording and producer have a "task" attribute (where a role credit would go)
    for i in (143, 128, 141):
        H.LTS[i]['attributes']['1150'] = {'min': 0, 'max': None}
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release
    ROLES = ['Mix', 'Recording', 'Engineer [Mix, Recording, Assistant]', 'Trumpet [Pocket Trumpet]']


    def rel():
        d = orig()
        d['extraartists'] += [{'name': 'Keys Guy', 'anv': '', 'role': ', '.join(ROLES), 'tracks': '', 'id': 3003, 'join': ''}]
        return d


    H.discogs_release = rel
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(400)
        rows = pg.evaluate("""[...document.querySelectorAll('[data-group] tr.dci-row')].filter(tr => tr.closest('[data-group]').querySelector('.dci-gname').textContent.includes('Keys Guy'))
      .map(tr => { const v = (f) => { const e = tr.querySelector('[data-f=' + f + ']'); return e ? (e.tagName === 'SELECT' ? (e.options[e.selectedIndex] || {}).text : e.value) : '-'; };
        return [tr.querySelector('.dci-drole').textContent.trim(), v('type'), v('primary'), v('role-credit'),
          [...tr.querySelectorAll('input[data-f=flag]:checked')].map(c => c.value).join(','), tr.querySelector('.dci-c-role').textContent.replace(/\\s+/g, ' ').trim()]; })""")
        for r in rows:
            print('  ', r[:5], '|', r[5][:110])
        by = {r[0]: r for r in rows}
        mix, rec = by.get('Mix'), by.get('Recording')
        emix, erec = by.get('Engineer [Mix, Assistant]'), by.get('Engineer [Recording, Assistant]')
        tp = by.get('Trumpet [Pocket Trumpet]')
        ok1 = mix and mix[1] == 'mix' and mix[3] == '' and rec and rec[1] == 'recording' and rec[3] == '' \
            and emix and emix[1] == 'mix' and emix[3] == '' and 'assistant' in emix[4] and 'S018' in emix[5] and 'Engineer [Mix, Recording, Assistant]' in emix[5] \
            and erec and erec[1] == 'recording' and erec[3] == '' and 'assistant' in erec[4] \
            and tp and tp[2] == 'pocket trumpet' and tp[3] == ''
        print('1) Mapping:', ok1)
        results.append(ok1)

        # 2) a rule id opens "Mapping rules" at that rule, also when a search hid it
        pg.click('[data-act=rules]'); pg.wait_for_timeout(200)
        pg.fill('#dci-rules [data-rf=search]', 'pocket'); pg.wait_for_timeout(150)
        pg.click('#dci-rules [data-rules-close]')
        tr = pg.locator('tr.dci-row').filter(has=pg.locator('.dci-drole', has_text='Engineer [Mix, Assistant]')).first
        ids = tr.locator('.dci-ruleid').all_inner_texts()
        tr.locator('.dci-ruleid', has_text='W006').click(); pg.wait_for_timeout(400)
        hit = pg.evaluate("""(() => { const r = document.querySelector('#dci-rules tr.dci-rule-hit'); if (!r) return null;
      const box = document.querySelector('#dci-rules').getBoundingClientRect(); const rb = r.getBoundingClientRect();
      return [r.dataset.rid, !r.hidden, rb.top >= box.top && rb.bottom <= box.bottom, document.querySelector('#dci-rules [data-rf=test]').value,
        document.querySelector('#dci-rules [data-rf=search]').value]; })()""")
        print('2) Regeln der Zeile:', ids, '| Klick auf W006 →', hit)
        tr.locator('.dci-ruleid', has_text='R033').click(); pg.wait_for_timeout(300)
        hit2 = pg.evaluate("[...document.querySelectorAll('#dci-rules tr.dci-rule-hit')].map(r => r.dataset.rid)")
        print('   dann R033 →', hit2)
        ok2 = ids == ['R033', 'W006', 'S018', 'S019'] and hit and hit[0] == 'W006' and hit[1] and hit[2] and hit[3] == 'Engineer [Mix, Assistant]' and hit[4] == '' and hit2 == ['R033']
        results.append(ok2)
        pg.click('#dci-rules [data-rules-close]')

        # 3) autoscroll as in browsers: only after 0.2 s in an edge zone (anew after leaving it), then gently faster
        pg.evaluate("document.querySelector('#dci-overlay [data-el=body]').scrollTop = 600")
        pg.wait_for_timeout(100)
        res = pg.evaluate("""async () => {
      const body = document.querySelector('#dci-overlay [data-el=body]');
      const dates = document.querySelector('#dci-overlay [data-el=dates]');
      const chip = document.querySelector('.dci-pchip-date');
      const y0 = dates.getBoundingClientRect().bottom + 10;          // just below the dates block
      const yb = body.getBoundingClientRect().bottom - 5;            // at the lower edge
      const dt = new DataTransfer();
      const over = (y) => body.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt, clientX: 300, clientY: y }));
      const wait = (ms) => new Promise((r) => setTimeout(r, ms));
      const stay = async (y, ms) => { const t = Date.now(); while (Date.now() - t < ms) { over(y); await wait(40); } };
      chip.dispatchEvent(new DragEvent('dragstart', { bubbles: true, dataTransfer: dt }));
      const start = body.scrollTop;
      await stay(y0, 150); over(y0 + 200);                           // out of the block: passes the zone in 150 ms
      const passed = body.scrollTop;
      await stay(y0, 150); over(y0 + 200); await stay(y0, 150);      // in, out, in again: the wait starts anew
      const anew = body.scrollTop;
      await stay(y0, 500);                                           // stays: scrolls up
      const up = body.scrollTop;
      over(y0 + 200); const a = body.scrollTop;
      await stay(yb, 600);                                           // lower edge: scrolls down after the wait
      const down = body.scrollTop;
      chip.dispatchEvent(new DragEvent('dragend', { bubbles: true, dataTransfer: dt }));
      return [start, passed, anew, up, a, down];
    }""")
        print('3) scrollTop: Start, durchgezogen (150 ms), erneut kurz, länger oben, …, unten länger:', res)
        ok3 = res[0] > 0 and res[1] == res[0] and res[2] == res[0] and res[3] < res[0] and res[5] > res[4]
        results.append(ok3)
        print('Fehler:', errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_v217():
    """Import 2.17.0, mapping and small things: "Mixed By [Mixing]" → mix without role credit (S019); "Bass Guitar" asks
    bass guitar · electric bass guitar · acoustic bass guitar, without a choice it stays bass guitar without credit
    (Q004); "Trombone [Additonal Musicians]" → additional (S002); "All Music By" → composer (R003); "©© Fuzzoramarecords
    2005" in the notes is a copyright date (D015), the label name gives no "recorded" hint; "‹ n rows incomplete ›" goes
    through the incomplete rows (1/4 … 4/4; [3.30.9] the label of "©©" from the notes, not in MusicBrainz, has two) and
    marks what is missing; Escape closes "Mapping rules" first, then the
    dashboard; the text size goes down to 50 %."""
    import re

    for i, n in [(9110, 'bass guitar'), (9111, 'trombone')]:
        H.attr(i, n, 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    orig = H.discogs_release


    def rel():
        d = orig()
        ex = lambda name, role, i: {'name': name, 'anv': '', 'role': role, 'tracks': '', 'id': i, 'join': ''}
        d['extraartists'] += [ex('Keys Guy', 'Mixed By [Mixing]', 3003), ex('Guitar Guy', 'Bass Guitar', 3002),
                              ex('Bass Man', 'Trombone [Additonal Musicians]', 3001), ex('Writer W', 'All Music By', 3007),
                              ex('Drum Guy', 'Directed By', 3004), ex('Nobody Known', 'Vocals', 3999)]
        d['notes'] += ' ©© Fuzzoramarecords 2005.'
        return d


    H.discogs_release = rel
    ROWS = """[...document.querySelectorAll('section.dci-group tr.dci-row')].map(tr => { const v = (f) => { const e = tr.querySelector('[data-f=' + f + ']');
  return e ? (e.tagName === 'SELECT' ? (e.options[e.selectedIndex] || {}).text : e.value) : '-'; };
  return [tr.querySelector('.dci-drole').textContent.trim(), v('type'), v('primary'), v('role-credit'),
    [...tr.querySelectorAll('input[data-f=flag]:checked')].map(c => c.value).join(','), [...tr.querySelectorAll('.dci-ruleid')].map(x => x.textContent).join(' '),
    (tr.querySelector('.dci-bass-ask:not(.dci-type-ask)') || {}).innerText || '']; })"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        by = {r[0]: r for r in pg.evaluate(ROWS)}
        for k in ['Mixed By [Mixing]', 'Bass Guitar', 'Trombone [Additonal Musicians]', 'Bass']:
            print('  ', by.get(k))
        mix, bg, tb, bass = by.get('Mixed By [Mixing]'), by.get('Bass Guitar'), by.get('Trombone [Additonal Musicians]'), by.get('Bass')
        ok1 = mix and mix[1] == 'mix' and mix[3] in ('', '-') and 'S019' in mix[5] \
            and bg and bg[2] == 'bass guitar' and bg[3] == '' and 'Q004' in bg[5] and 'bass guitar · electric bass guitar · acoustic bass guitar' in bg[6] and 'without a role credit' in bg[6] \
            and tb and tb[2] == 'trombone' and 'additional' in tb[4] and 'S002' in tb[5] \
            and bass and bass[2] == 'bass' and bass[3] == '' and 'Q001' in bass[5]
        # a choice: electric bass guitar, credited as "bass guitar"
        row = pg.locator('tr.dci-row').filter(has=pg.locator('.dci-drole', has_text='Bass Guitar')).first
        row.locator('[data-act=instr-pick]', has_text='electric bass guitar').click(); pg.wait_for_timeout(300)
        bg2 = {r[0]: r for r in pg.evaluate(ROWS)}['Bass Guitar']
        print('1b) gewählt:', bg2[:4])
        ok1 = ok1 and bg2[2] == 'electric bass guitar' and bg2[3] == 'bass guitar'
        # R003: "All Music By" → composer (works matrix)
        wcol = pg.evaluate("[...document.querySelectorAll('[data-colhead]')].filter(h => h.textContent.includes('Writer W')).map(h => h.innerText.replace(/\\s+/g, ' ').slice(0, 60))")
        print('1c) Spalte Writer W:', wcol)
        ok1 = ok1 and any('composer' in x for x in wcol)
        print('1) Mapping:', ok1)
        results.append(ok1)

        # 2) D015: "©© Fuzzoramarecords 2005" is a copyright date
        pg.click('[data-el=datefind] summary')
        items = [re.sub(r'\s+', ' ', i) for i in pg.locator('[data-el=datefind-list] li').all_inner_texts()]
        print('2) Gefunden:', items)
        hit = [i for i in items if '2005' in i]
        ok2 = len(hit) == 1 and '(D010 · D015)' in hit[0] and 'in the matrix: ℗/©' in hit[0] and not any('in the matrix: Performance' in i and '2005' in i for i in items)
        results.append(bool(ok2))

        # 3) incomplete rows: "Directed By" (choose a type) and an artist not in MusicBrainz
        s = lambda: re.sub(r'\s+', ' ', pg.locator('[data-el=sum]').inner_text())
        print('3) Zusammenfassung:', s())
        seen = []
        for _ in range(3):
            pg.evaluate("document.querySelectorAll('.dci-flash').forEach(e => e.classList.remove('dci-flash'))")
            pg.click('[data-el=sum] [data-act=inc-next] >> nth=-1'); pg.wait_for_timeout(300)
            fl = pg.evaluate("""[...document.querySelectorAll('.dci-flash')].map(e => e.matches('tr.dci-row') ? 'row:' + e.querySelector('.dci-drole').textContent.trim()
          : e.matches('[data-match]') ? 'artist' : e.className.split(' ').find(c => c.startsWith('dci-c-')) || e.tagName)""")
            seen.append((re.search(r'\d/\d', s()).group(0) if re.search(r'\d/\d', s()) else '', sorted(fl)))
        print('   ›, ›, ›:', seen)
        pg.click('[data-el=sum] [data-act=inc-prev]'); pg.wait_for_timeout(300)
        back = re.search(r'\d/\d', s()).group(0)
        print('   ‹:', back)
        # [3.30.9] "©© Fuzzoramarecords 2005" gives the label (℗ and ©, S042) – not in MusicBrainz: two rows more
        ok3 = '4 rows incomplete' in s() and [x[0] for x in seen] == ['1/4', '2/4', '3/4'] and back == '2/4' \
            and {tuple(x[1]) for x in seen[:2]} == {('artist', 'row:Vocals'), ('dci-c-type', 'row:Directed By')} and seen[2][1] == ['artist', 'row:Phonographic Copyright (p)']
        results.append(ok3)

        # 4) Escape: "Mapping rules" first, then the dashboard; text size down to 50 %
        for _ in range(9):
            pg.click('[data-act=zoom-out]')
        zoom = pg.locator('[data-el=zoom]').inner_text()
        pg.click('[data-act=rules]'); pg.wait_for_timeout(200)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        e1 = [pg.locator('#dci-rules').is_hidden(), pg.locator('#dci-overlay').is_visible()]
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        e2 = pg.locator('#dci-overlay').is_hidden()
        print('4) Zoom:', zoom, '| Escape 1 (Regeln zu, Dashboard offen):', e1, '| Escape 2 (Dashboard zu):', e2)
        results.append(zoom == '50 %' and e1 == [True, True] and e2)
        print('Fehler:', errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_v219():
    """Import 2.19.0. Suggestions look the same everywhere: yellow with an amber dashed border, the coloured left edge
    stays (date matrix: purple, works matrix: blue); "li?" too; dates and track groups from the Discogs notes in the
    pools until they are used (dropped somewhere). Not suggestions: "mixed" in "Attributes for all" is half filled,
    "waits for a work" grey dotted. "Commissioned By" → commissioned on the works (R099, companies C037): without a track
    list a suggestion on all works (S024; × takes one out, the others are staged), with tracks set on those works.
    "Live Recording By" → recording (R031, no role credit) and a hint for "live" (S021): "li?" on the existing link of
    its tracks, "li" preselected on their new links, nothing on other tracks."""
    import re
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


def case_mastering():
    """Import 3.15.1: mastering only on the release level (as MusicBrainz has it: on recordings the type is deprecated).
    Discogs names two mastering engineers: Mia Master for tracks 1–2 (CD 1, say), Max Master for tracks 3–4; the notes give
    May, June and July 2001 for mastering (cells of the column "Mastering"). May gets the track group "CD 1" (tracks 1–2),
    June "CD 2" (tracks 3–4), July none (all tracks).
    A) The rows of both are on the release level; the only other choice is "Skip" (no "Recording"), and the level says why
       on mouse-over.
    B) The cells of the column "Mastering" have no checkbox "Release level"; the column "Performance" still has it.
    C) Applied: Mia Master takes May and July, Max Master June and July – the track group only says which mastering row a
       date belongs to; no date is lost for a release-level row because of a track group."""
    import json
    from common_rows import rows_of

    orig = H.discogs_release


    def release():
        d = orig()
        ex = lambda name, role, i, tracks='': {'name': name, 'anv': '', 'role': role, 'tracks': tracks, 'id': i, 'join': ''}
        d['extraartists'] = d['extraartists'] + [ex('Mia Master', 'Mastered By', 3021, '1, 2'), ex('Max Master', 'Mastered By', 3022, '3, 4')]
        d['notes'] = 'Recorded March 2001. Mastered May 2001. Mastered June 2001. Mastered July 2001.'
        return d


    H.discogs_release = release
    H.ARTISTS[3021] = (H.uid('dddddddd', 21), 'Mia Master')
    H.ARTISTS[3022] = (H.uid('dddddddd', 22), 'Max Master')
    TRACKS = [{'id': 't12', 'name': 'CD 1', 'tracks': [0, 1]}, {'id': 't34', 'name': 'CD 2', 'tracks': [2, 3]}]
    CELLS = "[...document.querySelectorAll('.dci-dm-col[data-dmcol=mastering] .dci-dm-cell')].map(c => [c.dataset.id, c.querySelector('.dci-chip-main').textContent.trim()])"


    def group_on(pg, month, tg):
        cid = next(c for c, t in pg.evaluate(CELLS) if f'2001-{month}' in t)
        pg.locator(f'[data-act=dm-edit][data-cell="{cid}"]').first.evaluate('b => b.click()'); pg.wait_for_timeout(200)
        pg.locator(f'[data-f=dm-tg][data-cell="{cid}"][value="{tg}"]').check(); pg.wait_for_timeout(200)
        pg.locator(f'.dci-dm-editor [data-act=dm-edit][data-cell="{cid}"]').first.evaluate('b => b.click()'); pg.wait_for_timeout(200)


    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        # two track groups (read when the script starts: stored, then the page loaded again)
        pg.evaluate(f"localStorage.setItem('dci-track-pool:{H.REL}', {json.dumps(json.dumps(TRACKS))})")
        pg.reload(); pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        print('Spalte Mastering:', pg.evaluate(CELLS))
        group_on(pg, '05', 't12')
        group_on(pg, '06', 't34')
        # A) levels
        lv = pg.evaluate("""[...document.querySelectorAll('section.dci-group')].filter(g => /Mia Master|Max Master/.test(g.querySelector('.dci-gname').textContent))
      .map(g => { const seg = g.querySelector('tr.dci-row .dci-seg'); return [g.querySelector('.dci-gname strong').textContent.trim(),
        [...seg.querySelectorAll('[data-act=level]')].map(x => x.dataset.level + (x.getAttribute('aria-pressed') === 'true' ? '*' : '')), seg.title,
        g.querySelector('tr.dci-row [data-f=type]').value]; })""")
        print('A) Ebenen:', lv)
        results.append(len(lv) == 2 and all(x[1] == ['release*', 'skip'] and 'only on this level (Release)' in x[2] for x in lv))
        # B) no "Release level" in the mastering column, still in the performance column
        rel = pg.evaluate("Object.fromEntries(['mastering', 'performance'].map(k => [k, document.querySelectorAll(`.dci-dm-col[data-dmcol=${k}] [data-f=dm-rel]`).length]))")
        cells = pg.evaluate("document.querySelectorAll('.dci-dm-col[data-dmcol=mastering] .dci-dm-cell').length")
        print('B) Checkbox „Release-Ebene“:', rel, '| Zellen Mastering:', cells)
        results.append(rel == {'mastering': 0, 'performance': 1} and cells >= 3)
        # C) applied
        pg.locator('[data-el=dates] .dci-apply').first.evaluate('b => b.click()'); pg.wait_for_timeout(800)
        mia, mx = rows_of(pg, 'Mia Master'), rows_of(pg, 'Max Master')
        print('C) Mia Master:', mia, '| Max Master:', mx)
        results.append(sorted(x.split(' | ')[1] for x in mia) == ['2001-05', '2001-07'] and sorted(x.split(' | ')[1] for x in mx) == ['2001-06', '2001-07'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_special():
    """Import 3.15.1: special purpose artists are left out of the comparison with the works of the artists.
    A) The release's artist credit names Various Artists (its MBID, T026), "[soundtrack]" (any name in square brackets) and
       Test Band: only Test Band is asked for its works; Various Artists' work with the title of track 4 is not offered,
       Test Band's work with the title of track 3 is.
    B) The log names each special artist once – also after the dashboard is drawn anew (a level changed).
    C) "Mapping rules" lists the table T026."""
    VA = '89ad4ac3-39f7-470e-963a-56509c546377'
    ST = H.uid('dddddddd', 61)
    TB = H.uid('dddddddd', 60)
    W3, W4 = H.uid('cccccccc', 83), H.uid('cccccccc', 84)
    H.RELEASE_AC[:] = [(VA, 'Various Artists', 'Various Artists', ' & '), (ST, '[soundtrack]', '[soundtrack]', ' & '),
                       (TB, 'Test Band', 'Test Band', '')]
    H.ARTIST_WORKS.update({VA: [{'id': W4, 'title': H.TITLES[3], 'type': 'Song', 'aliases': []}],
                           ST: [{'id': W4, 'title': H.TITLES[3], 'type': 'Song', 'aliases': []}],
                           TB: [{'id': W3, 'title': H.TITLES[2], 'type': 'Song', 'aliases': []}]})
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
        pg.wait_for_timeout(300)
        asked = sorted({a for _, a, _ in H.BROWSES})
        offered = {i: pg.evaluate(f"[...document.querySelectorAll('tr[data-work=\"{i}\"] .dci-same [data-act=work-pick]')].map(b => b.dataset.gid)") for i in (2, 3)}
        print('A) gefragt:', ['VA' if a == VA else 'soundtrack' if a == ST else 'Test Band' if a == TB else a[-3:] for a in asked], '| Track 3:', offered[2], '| Track 4:', offered[3])
        results.append(VA not in asked and ST not in asked and TB in asked and offered[2] == [W3] and offered[3] == [])
        # B) drawn anew: no second log line
        bass = pg.locator('section.dci-group').filter(has=pg.locator('.dci-gname strong', has_text='Bass Man')).first
        bass.locator('[data-act=level][data-level=skip]').first.click(); pg.wait_for_timeout(1200)
        bass.locator('[data-act=level][data-level=recording]').first.click(); pg.wait_for_timeout(1200)
        special = [x for x in pg.evaluate(LOGS) if 'special purpose' in x]
        print('B) Protokoll:', special)
        results.append(special == ['Various Artists: a special purpose artist (Various Artists, [unknown] …) – its works are not compared',
                                   '[soundtrack]: a special purpose artist (Various Artists, [unknown] …) – its works are not compared'])
        # C) the table in "Mapping rules"
        pg.locator('[data-act=rules]').first.click()
        pg.wait_for_selector('#dci-rules [data-rsect=lists]', timeout=10000)
        t026 = pg.evaluate("[...document.querySelectorAll('#dci-rules [data-rsect=lists] *')].some(e => /T026/.test(e.textContent) && /89ad4ac3-39f7-470e-963a-56509c546377/.test(e.textContent))")
        print('C) T026 im Regelfenster:', t026)
        results.append(t026)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_recheck():
    """Import 3.12.1: two fixes.
    A) "n lines not recognized" opens in the window too (the source sits in the head of the window, which moves it; a
       press on the list started moving the window, so the list never opened).
    B) Same-named works are looked up again when the writers of a track change: a pasted text names "Written by Agusti
       Fernández (2, 3)"; the name is only a suggestion, so at the import the tracks have no writers and nothing is
       searched. A click on the suggestion assigns him – his work with the title of track 2 is found then.
    C) Without a writer change nothing is searched again (no second query).
    D) A new import starts the work search anew: the results of the import before (here the linked Discogs release,
       loaded first) do not stay – the text import searches its tracks itself (it did not, before 3.12.1)."""
    AG = H.uid('dddddddd', 50)
    GID = H.uid('eeeeeeee', 70)
    H.MB_SEARCH['artist'] = [{'id': AG, 'name': 'Agustí Fernández', 'disambiguation': 'pianist', 'score': 100}]
    H.WORK_SEARCH.append({'id': GID, 'title': H.TITLES[1], 'aliases': [], 'type': 'Song',
                          'relations': [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': AG, 'name': 'Agustí Fernández'}}]})
    TEXT = """Written by Agusti Fernández (2, 3)
Bass Man – bass
see you all next time"""
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
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 30)
        pg.wait_for_timeout(500)
        # A) the list opens in the window
        inline = pg.evaluate("!!document.querySelector('.dci-inline')")
        pg.click('.dci-unrec summary'); pg.wait_for_timeout(300)
        opened = pg.evaluate("document.querySelector('.dci-unrec').open")
        lines = pg.locator('.dci-unrec li').all_inner_texts()
        print('A) im Fenster:', not inline, '| aufgeklappt:', opened, '|', lines)
        results.append(not inline and opened and lines == ['see you all next time'])
        # D) the text import searched itself (two "Checks complete": Discogs, then the text), nothing "again" yet
        checks = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'Checks complete' in x]
        again0 = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'looked up again' in x]
        print('D) Prüfungen:', [c[9:] for c in checks], '| neu gesucht vor dem Klick:', len(again0))
        ok_d = len(checks) == 2 and not again0
        # B) before: no writers, no query with him; after the click: searched, found
        before = [q for q in H.WORK_QUERIES if AG in q]
        same0 = pg.locator(f'.dci-same [data-act=work-pick][data-gid="{GID}"]').count()
        pg.locator('[data-act=name-use]').first.click()
        H.wait_for(pg, f"!!document.querySelector('.dci-same [data-act=work-pick][data-gid=\"{GID}\"]')", 20)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Checks complete/.test(li.textContent)).length >= 2", 20)
        pg.wait_for_timeout(1500)

        after = [q for q in H.WORK_QUERIES if AG in q]
        log = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'looked up again' in x]
        print('B) vorher Anfragen:', len(before), 'gefunden:', same0, '| nachher Anfragen:', len(after), '|', log)
        results.append(not before and same0 == 0 and len(after) == 2 and log == ['The writers of 2 tracks changed – their same-named works are looked up again'])
        # C) nothing changes → no further query
        n = len(H.WORK_QUERIES)
        bass = pg.locator('section.dci-group').filter(has=pg.locator('.dci-gname strong', has_text='Bass Man')).first
        bass.locator('[data-act=level][data-level=skip]').first.click(); pg.wait_for_timeout(300)
        bass.locator('[data-act=level][data-level=recording]').first.click(); pg.wait_for_timeout(1500)
        print('C) weitere Anfragen nach Ebenen-Wechsel eines Instruments:', len(H.WORK_QUERIES) - n)
        results.append(len(H.WORK_QUERIES) == n)
        results.append(ok_d)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_engineers():
    """Credits Importer 3.31.3: the kind of engineer said twice (collected item 101; maintainer: "ich habe einen Fall gefunden
    wo "Recording Engineer" in der Discogs note zu engineer stand. das muss natürlich einfach nur nach relationship
    recording engineer und nicht mit der Role Credit "Recording Engineer" die auch noch groß geschrieben ist.").
    Discogs: "Engineer [Recording Engineer]", "Engineer [Mix Engineer]", "Engineer [Mastering Engineer]", "Engineer
    [Assistant Engineer]" → recording, mix, mastering and engineer with "assistant" – each without role credit (S047; before:
    engineer with the role credit "Recording Engineer" …)."""
    H.lt(140, '5dcc52af-7064-4051-8d62-7d80f4c3c907', 'engineer', 'artist', 'recording', (1, 526))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release
    roles = {'Rec Eng': 'Engineer [Recording Engineer]', 'Mix Eng': 'Engineer [Mix Engineer]', 'Mas Eng': 'Engineer [Mastering Engineer]',
             'Ass Eng': 'Engineer [Assistant Engineer]'}

    def rel():
        d = orig()
        d['extraartists'] += [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': 3300 + k, 'join': ''} for k, (n, r) in enumerate(roles.items())]
        return d

    H.discogs_release = rel
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
      [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const c = tr.querySelector('[data-f=role-credit]');
        return [t ? (t.options[t.selectedIndex] || {}).text : '', c ? c.value : null, [...tr.querySelectorAll('[data-f=flag]:checked, input[type=checkbox]:checked')].map(x => x.value || x.dataset.flag || '').filter(Boolean)]; })])))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        g = pg.evaluate(ROWS)
        got = {n: g.get(n) for n in roles}
        print('Zeilen:', got)
        # (no role credit: its field is empty or not there)
        results.append([(got[n][0][0], bool(got[n][0][1])) for n in roles] == [('recording', False), ('mix', False), ('mastering', False), ('engineer', False)]
                       and got['Ass Eng'][0][2] == ['assistant'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_poems():
    """Credits Importer 3.31.4: poems and poetry (collected item 104; maintainer: "bitte Dichter immer zu lyricist", "ja das
    nachfragen kann man machen").
    A) Discogs "Poems By" → lyricist on the works (a column of the works matrix, R105); "Poetry [Read By]" and "Recitation"
       → vocal spoken vocals with the role credit "poetry" / "recitation" (R106).
    B) "Poems" alone: no type until chosen, the question (Q009) with lyricist · liner notes · spoken vocals; liner notes →
       on the release with the role credit "poems"; spoken vocals → vocal spoken vocals, credited "poems"; lyricist → it leaves the entry
       for a column of the works matrix.
    C) A pasted text: "Poems: Jane Doe" asks the same; "Poetry by John Roe" → a column of the works matrix."""
    H.attr(9130, 'spoken vocals', 3, 3)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    for i, n in [(3061, 'Poet A'), (3062, 'Reader B'), (3063, 'Poet C'), (3064, 'Reciter D')]:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 3000), n)
    orig = H.discogs_release
    roles = [('Poet A', 'Poems By', 3061), ('Reader B', 'Poetry [Read By]', 3062), ('Poet C', 'Poems', 3063), ('Reciter D', 'Recitation', 3064)]

    def rel():
        d = orig()
        d['extraartists'] += [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in roles]
        return d

    H.discogs_release = rel
    ROW = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; const tr = g.querySelector('tr.dci-row'); if (!tr) return { rows: 0 };
  const t = tr.querySelector('[data-f=type]'); const ask = tr.querySelector('.dci-type-ask'); const p = tr.querySelector('[data-f=primary]'); const c = tr.querySelector('[data-f=role-credit]');
  const lv = tr.querySelector('[data-act=level][aria-pressed=true]');
  return { rows: g.querySelectorAll('tr.dci-row').length, id: tr.dataset.row, type: t ? (t.options[t.selectedIndex] || {}).text : '', primary: p ? p.value : '', credit: c ? c.value : '',
    level: lv ? lv.dataset.level : '', ask: ask ? ask.textContent.replace(/\\s+/g, ' ').trim() : null, opts: ask ? [...ask.querySelectorAll('[data-act=type-pick]')].map(b => b.textContent.trim()) : [],
    rules: [...tr.querySelectorAll('.dci-ruleid')].map(b => b.textContent.trim()) }; }"""
    COLS = """[...document.querySelectorAll('.dci-matrix th[data-colhead]')].map(th => (th.querySelector('.dci-mx-colname .dci-mblink, .dci-mx-colname strong') || {}).textContent.replace(/^MB/, '').trim())"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        # A)
        cols = pg.evaluate(COLS)
        rb, rd = pg.evaluate(ROW, 'Reader B'), pg.evaluate(ROW, 'Reciter D')
        print('A) Spalten:', cols, '\n   Reader B:', rb, '\n   Reciter D:', rd)
        results.append('Poet A' in cols and [rb['type'], rb['primary'], rb['credit']] == ['vocal', 'spoken vocals', 'poetry'] and 'R106' in rb['rules']
                       and [rd['type'], rd['primary'], rd['credit']] == ['vocal', 'spoken vocals', 'recitation'])
        # B)
        c0 = pg.evaluate(ROW, 'Poet C')
        print('B) Poet C:', c0)
        results.append(c0 and c0['opts'] == ['lyricist (the words of the works)', 'liner notes (poems in the booklet)', 'spoken vocals (read out)']
                       and 'R107' in c0['rules'] and 'Q009' in c0['rules'] and 'please choose' in c0['ask'] and 'Poet C' not in cols)
        pg.click(f'tr[data-row="{c0["id"]}"] [data-act=type-pick][data-opt="1"]')
        pg.wait_for_timeout(400)
        c1 = pg.evaluate(ROW, 'Poet C')
        pg.click(f'tr[data-row="{c0["id"]}"] [data-act=type-pick][data-opt="2"]')
        pg.wait_for_timeout(400)
        c2 = pg.evaluate(ROW, 'Poet C')
        pg.click(f'tr[data-row="{c0["id"]}"] [data-act=type-pick][data-opt="0"]')
        pg.wait_for_timeout(800)
        c3, cols3 = pg.evaluate(ROW, 'Poet C'), pg.evaluate(COLS)
        print('   liner notes:', [c1['type'], c1['level'], c1['credit']], '| spoken vocals:', [c2['type'], c2['primary'], c2['credit']], '| lyricist:', c3, cols3)
        results.append([c1['type'], c1['level'], c1['credit']] == ['liner notes', 'release', 'poems'] and [c2['type'], c2['primary'], c2['credit']] == ['vocal', 'spoken vocals', 'poems']
                       and (c3 is None or c3['rows'] == 0) and 'Poet C' in cols3)
        # C) a pasted text
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Poems: Jane Doe\nPoetry by John Roe')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        j, cols4 = pg.evaluate(ROW, 'Jane Doe'), pg.evaluate(COLS)
        print('C) Jane Doe:', j, '\n   Spalten:', cols4)
        results.append(j and len(j['opts']) == 3 and 'Q009' in j['rules'] and 'John Roe' in cols4)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
