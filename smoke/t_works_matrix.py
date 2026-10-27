"""Works matrix: track groups and notes, columns, dates of cells, attributes, publishers (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: mxdrop, matrixcols, fill, wattrs, pub – each the former smoke/t_<case>.py, unchanged; `python3 t_works_matrix.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_mxdrop():
    """Works matrix and track groups. From the Discogs notes (S022): "Published by Pub Co (1, 3)" → track group and
    the tracks in the column of Pub Co (ahead of the personal publisher evidence, which gives 1, 2; [3.31.6] set, not
    suggested – ⓘ in the head and in the cells' titles names the line, item 97c); "Ghostpub (4)" matches "Ghost Pub"
    (spaces); "Written by Writer W (1, 2)" is in the Discogs track credits already (no change); "Strings arranged by
    Nobody Here (4)" is no entry (only the track group). A click on a cell takes a track out.
    Dropped (S023): onto a column head – all its roles only for the group's tracks; Shift adds; onto a role – only
    that role; onto an attribute in the head of the track column – the links of the group's tracks (MB's own stay)."""
    import re
    from common_rows import drag

    for i, n in [(567, 'cover'), (578, 'live'), (750, 'medley')]:
        H.attr(i, n, i)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578, 750))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    orig_rel = H.discogs_release


    def rel():
        d = orig_rel()
        d['notes'] += ('\nPublished by Pub Co (1, 3); Ghostpub (4).\nWritten by Writer W (1, 2).'
                       '\nStrings arranged by Nobody Here (2, 4).')
        # Writer Z also writes the lyrics (a second role in the column)
        d['extraartists'].append({'name': 'Writer Z', 'anv': '', 'role': 'Lyrics By', 'tracks': '', 'id': 3009, 'join': ''})
        return d


    H.discogs_release = rel
    COLS = """(() => { const out = {};
  document.querySelectorAll('.dci-matrix th[data-colhead]').forEach((th) => {
    const name = (th.querySelector('.dci-mx-colname .dci-mblink, .dci-mx-colname strong') || {}).textContent.replace(/^MB/, '').trim();
    out[name] = [...document.querySelectorAll(`.dci-mx-cell[data-col="${th.dataset.colhead}"]`)].filter(c => c.classList.contains('dci-mx-on'))
      .map(c => (Number(c.closest('tr').dataset.work) + 1) + (c.classList.contains('dci-mx-sugg') ? 's' : '') + (c.querySelectorAll('.dci-mxchip-on, .dci-mxchip-sugg, .dci-mxchip-wait').length > 1 ? '+' : ''));
  }); return out; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1500)
        cols = lambda: pg.evaluate(COLS)
        colkey = lambda name: pg.evaluate(f"[...document.querySelectorAll('.dci-matrix th[data-colhead]')].find(th => th.textContent.includes({name!r})).dataset.colhead")
        cell = lambda name, track: f'.dci-matrix tr[data-work="{track - 1}"] .dci-mx-cell[data-col="{colkey(name)}"]'
        pool = lambda: pg.evaluate("[...new Set([...document.querySelectorAll('.dci-pchip-tg')].map(c => c.textContent.replace(/\\s+/g, ' ').trim()))]")

        # A) from the notes
        c0 = cols()
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'Notes:' in x]
        print('A1) Track-Pool:', pool())
        print('    Spalten (s = Vorschlag):', c0)
        print('    Protokoll:', logs)
        info = pg.evaluate(f"(document.querySelector('[data-colhead=\"{colkey('Pub Co')}\"] .dci-mx-notesinfo') || {{}}).title || ''")
        ctitle = pg.evaluate(f"document.querySelector('{cell('Pub Co', 1)} .dci-mxchip').title")
        print('    ⓘ Pub Co:', info, '| Zelle 1:', ctitle)
        ok_a = c0.get('Pub Co') == ['1', '3'] and c0.get('Ghost Pub') == ['4'] and c0.get('Writer W') == ['1', '2'] \
            and info == 'Tracks from the Discogs notes: “Published by Pub Co (1, 3)”' and 'from the notes: “Published by Pub Co (1, 3)”' in ctitle \
            and any('Pub Co · 1, 3' in x for x in pool()) and any('Ghostpub · 4' in x for x in pool()) and any('Nobody Here · 2, 4' in x for x in pool()) \
            and any('Nobody Here' in x and 'only a track group' in x for x in logs) and any('Writer W' in x and 'only a track group' in x for x in logs)
        pg.click(f'{cell("Pub Co", 3)} [data-act=mx-cell]'); pg.wait_for_timeout(200)
        c1 = cols()
        print('A2) Track 3 weggeklickt:', c1.get('Pub Co'))
        ok_a = ok_a and c1.get('Pub Co') == ['1']
        results.append(ok_a)

        # B) a track group onto a column head, with Shift, onto one role
        pg.click('[data-act=tg-new]'); pg.fill('[data-f=tg-name]', 'Side A')
        pg.check('[data-f=tg-track][data-i="0"]'); pg.check('[data-f=tg-track][data-i="1"]'); pg.click('[data-act=tg-save]'); pg.wait_for_timeout(200)
        gid = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Side A')).dataset.id")
        wz = colkey('Writer Z')
        print('B0) Writer Z vorher:', cols().get('Writer Z'))
        drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', f'[data-colhead="{wz}"] .dci-mx-card .dci-mx-credit')
        b1 = cols().get('Writer Z')
        # Shift: the group of track 4 added (synthetic events carry the Shift key)
        g4 = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Ghostpub')).dataset.id")
        hints = pg.evaluate(f"""(() => {{
      const src = document.querySelector('.dci-pools-body .dci-pchip-tg[data-id="{g4}"] .dci-chip-main').closest('[data-drag]');
      const dst = document.querySelector('[data-colhead="{wz}"] .dci-mx-card');
      const after = (el) => getComputedStyle(el, '::after').content;
      const dt = new DataTransfer();
      src.dispatchEvent(new DragEvent('dragstart', {{ bubbles: true, dataTransfer: dt }}));
      const out = [getComputedStyle(dst).outlineStyle];
      dst.dispatchEvent(new DragEvent('dragover', {{ bubbles: true, cancelable: true, dataTransfer: dt }}));
      out.push(after(dst));
      dst.dispatchEvent(new DragEvent('dragover', {{ bubbles: true, cancelable: true, dataTransfer: dt, shiftKey: true }}));
      out.push(after(dst));
      dst.dispatchEvent(new DragEvent('drop', {{ bubbles: true, cancelable: true, dataTransfer: dt, shiftKey: true }}));
      src.dispatchEvent(new DragEvent('dragend', {{ bubbles: true, dataTransfer: dt }}));
      return out; }})()""")
        pg.wait_for_timeout(300)
        b2 = cols().get('Writer Z')
        print('B1) „Side A“ auf Writer Z:', b1, '| mit Umschalt Track 4 dazu:', b2, '| Hinweise:', hints)
        ok_b = b1 == ['1+', '2+'] and b2 == ['1+', '2+', '4+'] and hints[0] == 'dashed' and 'only the works of these tracks' in hints[1] and 'adds the works' in hints[2]
        # onto one role: lyricist only on the works of track 1 (group "Pub Co · 1, 3" → track 1 has a work, 3 waits)
        g13 = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Pub Co')).dataset.id")
        lyr = pg.evaluate(f"[...document.querySelectorAll('[data-colhead=\"{wz}\"] [data-tgrole]')].find(r => r.textContent.trim() === 'lyricist').dataset.tgrole")
        drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{g13}"] .dci-chip-main', f'[data-colhead="{wz}"] [data-tgrole="{lyr}"]')
        roles = pg.evaluate(f"""[1, 2, 3, 4].map(t => [...document.querySelectorAll('.dci-matrix tr[data-work="' + (t - 1) + '"] .dci-mx-cell[data-col="{wz}"] .dci-mxchip')].map(c => c.textContent.trim().split(' ')[0]).sort())""")
        print('B2) „Pub Co · 1, 3“ auf die Rolle lyricist – Rollen je Track:', roles)
        ok_b = ok_b and roles == [['composer', 'lyricist'], ['composer'], ['lyricist'], ['composer']]
        results.append(ok_b)

        # C) onto an attribute in the head of the track column: "li" for the works of "Side A" (tracks 1, 2)
        pg.click('tr[data-work="1"] [data-act=work-pending]'); pg.wait_for_timeout(300)
        pg.click('tr[data-work="2"] [data-act=work-pending]'); pg.wait_for_timeout(300)
        drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', '.dci-wattrs-all [data-tgattr=live]')
        live = pg.evaluate("""[...document.querySelectorAll('.dci-matrix tbody tr[data-mrow]')].filter(tr => tr.dataset.mrow.match(/^[wp]:/))
      .map(tr => [Number(tr.dataset.work) + 1, [...tr.querySelectorAll('.dci-wpill-on, .dci-wpill-mb')].map(b => b.textContent.trim())])""")
        print('C1) „Side A“ auf „li“:', live)
        ok_c = live == [[1, ['li✎']], [2, ['li']], [3, []]]
        results.append(ok_c)
        print('Fehler:', errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_matrixcols():
    """Works matrix: ✕ takes a column out (its rows on "Skip", the column stays folded, a click brings it back; MB-only
    columns are only folded); the column date also plans dates for the column's relationships that MusicBrainz has
    without a date (also in a column "only in MusicBrainz"), clearing it takes them back. "Directed By" is asked:
    conductor, chorus master, creative direction or miscellaneous support (task "director"), nothing assumed."""
    import re
    from common_rows import drag

    LYRIC = H.uid('dddddddd', 50)
    H.lt(158, '91fa6e73-0b22-4f35-a9ab-8a7d1e8c7b02', 'chorus master', 'artist', 'recording', (1,))
    H.lt(927, 'df4b4d3e-0b5c-4f8e-9a7b-1c2d3e4f5a60', 'conductor', 'artist', 'recording', (1,))
    H.lt(146, '0e2d1e4b-1d3a-4f7e-8f2c-6a5b4c3d2e10', 'creative direction', 'artist', 'release', (1,))
    H.lt(1130, 'b367fae0-c4b0-48b9-a40c-f3ae4c02cf10', 'misc', 'artist', 'recording', (1150,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig_rel, orig_ws = H.discogs_release, H.ws_release


    def rel():
        d = orig_rel()
        d['extraartists'].append({'name': 'Keys Guy', 'anv': '', 'role': 'Directed By', 'tracks': '', 'id': 3003, 'join': ''})
        return d


    def ws():
        d = orig_ws()
        work = d['media'][0]['tracks'][0]['recording']['relations'][0]['work']
        # a lyricist MusicBrainz knows but Discogs does not name: a column "only in MusicBrainz"
        work['relations'] = work['relations'] + [{'target-type': 'artist', 'type': 'lyricist', 'type-id': H.LTS[165]['gid'], 'attributes': [],
                                                  'artist': {'id': LYRIC, 'name': 'Lyric Only'}}]
        return d


    H.discogs_release, H.ws_release = rel, ws
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)

        # A) "Directed By": please choose; nothing staged until then
        row = lambda: pg.locator('tr.dci-row').filter(has=pg.locator('.dci-drole', has_text='Directed By')).first
        typ = lambda: row().locator('[data-f=type]').evaluate("s => s.options[s.selectedIndex] ? s.options[s.selectedIndex].text : ''")
        ask = re.sub(r'\s+', ' ', row().locator('.dci-type-ask').inner_text())
        planned = lambda: pg.evaluate("[...document.querySelectorAll('[data-status]')].length") and row().locator('.dci-status').inner_text()
        print('A1) Directed By:', ask[:160], '| Typ:', typ(), '| Status:', planned()[:60], '| Regeln:', row().locator('.dci-ruleid').all_inner_texts())
        ok_a = 'please choose' in ask and typ().startswith('Choose') and 'Q003' in row().locator('.dci-ruleid').all_inner_texts()
        picks = []
        for label in ['chorus master', 'creative direction', 'miscellaneous support']:
            row().locator('[data-act=type-pick]', has_text=label).click(); pg.wait_for_timeout(200)
            rc = row().locator('[data-f=role-credit]').input_value() if row().locator('[data-f=role-credit]').count() else ''
            picks.append((typ(), row().get_attribute('class').split('dci-lv-')[1].split()[0], rc, row().locator('.dci-type-ask [aria-pressed=true]').inner_text()))
        print('A2) gewählt:', picks)
        ok_a = ok_a and picks[0][:2] == ('chorus master', 'recording') and picks[1][:2] == ('creative direction', 'release') \
            and picks[2][0] == 'misc' and picks[2][2] == 'director' and 'miscellaneous support' in picks[2][3]
        results.append(ok_a)

        # B) take a column out and back
        WK = pg.evaluate("[...document.querySelectorAll('[data-colhead]')].find(h => h.textContent.includes('Writer W')).dataset.colhead")
        writer_rows = lambda: pg.evaluate("""[...document.querySelectorAll('.dci-group')].filter(g => (g.querySelector('.dci-gname') || {textContent: ''}).textContent.includes('Writer W'))
      .flatMap(g => [...g.querySelectorAll('tr.dci-row')]).map(tr => (tr.className.match(/dci-lv-(\\w+)/) || [])[1])""")
        before = writer_rows()
        pg.click(f'[data-colhead="{WK}"] [data-act=mx-col-remove]'); pg.wait_for_timeout(300)
        out = writer_rows()
        stub = pg.locator('th.dci-mx-removed [data-act=mx-col-restore]')
        stub_title = stub.get_attribute('title') if stub.count() else ''
        print('B1) Writer W Ebenen vorher:', before, '| nach ✕:', out, '| Spalte:', stub_title)
        stub.click(); pg.wait_for_timeout(300)
        back = writer_rows()
        print('    zurückgeholt:', back, '| Spaltenkopf wieder da:', pg.locator(f'[data-colhead="{WK}"]').count())
        # (work-level rows live in the works matrix; in the list they show only while skipped)
        ok_b = before == [] and out == ['skip'] and 'Writer W' in stub_title and back == [] and pg.locator(f'[data-colhead="{WK}"]').count() == 1
        mbcol = f'mb:{LYRIC}'
        pg.click(f'[data-colhead="{mbcol}"] [data-act=mx-col-remove]'); pg.wait_for_timeout(200)
        folded = pg.locator(f'th.dci-mx-collapsed [data-act=mx-collapse][data-col="{mbcol}"]').count()
        print('B2) Spalte „nur in MusicBrainz“ ✕ → eingeklappt:', folded)
        ok_b = ok_b and folded == 1
        pg.click(f'[data-act=mx-collapse][data-col="{mbcol}"]'); pg.wait_for_timeout(200)
        results.append(ok_b)

        # C) column dates for relationships already in MusicBrainz without a date
        date = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-date')].find(c => c.textContent.includes('Performance 1 ·')).dataset.id")
        drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', f'[data-colhead="{WK}"] .dci-mx-card')
        w0 = f'.dci-mx-cell[data-col="{WK}"][data-mrow^="w:0"] .dci-mx-fill'
        f1 = [re.sub(r'\s+', ' ', x) for x in pg.locator(w0).all_inner_texts()]
        drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', f'[data-colhead="{mbcol}"] .dci-mx-card')
        f2 = [re.sub(r'\s+', ' ', x) for x in pg.locator(f'.dci-mx-cell[data-col="{mbcol}"][data-mrow^="w:0"] .dci-mx-fill').all_inner_texts()]
        print('C1) Spaltendatum Writer W → bestehender Composer:', f1, '| Spalte nur in MB → Lyricist:', f2)
        # clearing the column date takes back what it planned (its fields are in the ▾ menu)
        pg.click(f'[data-colhead="{mbcol}"] [data-act=mx-colmenu]'); pg.wait_for_timeout(300)
        yb = pg.locator(f'[data-colhead="{mbcol}"] [data-f=cd-by]')
        yb.fill(''); yb.dispatch_event('input'); pg.wait_for_timeout(200)
        for f in ('cd-bm', 'cd-bd', 'cd-ey', 'cd-em', 'cd-ed'):
            x = pg.locator(f'[data-colhead="{mbcol}"] [data-f={f}]')
            if x.count():
                x.fill(''); x.dispatch_event('input')
        pg.wait_for_timeout(200)
        ended = pg.locator(f'[data-colhead="{mbcol}"] [data-f=cd-ended]')
        if ended.count() and ended.is_checked():
            ended.uncheck()
        pg.wait_for_timeout(300)
        f3 = pg.locator(f'.dci-mx-cell[data-col="{mbcol}"][data-mrow^="w:0"] .dci-mx-fill').count()
        print('    Spaltendatum geleert → geplant:', f3)
        ok_c = len(f1) == 1 and 'composer' in f1[0] and '2001-03-01' in f1[0] and len(f2) == 1 and 'lyricist' in f2[0] and f3 == 0
        # staging: the existing composer gets the date (the editor knows it)
        pg.evaluate(f"""() => {{ const re = MB.relationshipEditor;
      re.state = {{ ...re.state, existingRels: [{{ id: 9001, linkTypeID: 168, entity0: {{ gid: '{H.ARTISTS[3007][0]}', entityType: 'artist', id: 3007, name: 'Writer W' }},
        entity1: {{ gid: '{H.WORK1}', entityType: 'work', id: 7001, name: 'x' }}, begin_date: null, end_date: null, ended: false,
        attributes: null, entity0_credit: '', entity1_credit: '', _status: 0 }}] }}; }}""")
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
        st = pg.evaluate("(() => { const r = MB.relationshipEditor.state.added.find(x => x.id === 9001); return r && [r.begin_date, r._status]; })()")
        print('C2) im Editor:', st)
        ok_c = ok_c and st and st[0] == {'year': 2001, 'month': 3, 'day': 1} and st[1] == 2
        results.append(ok_c)
        print('Fehler:', errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_fill():
    """Works matrix: a date dropped onto a cell with a relationship already in MusicBrainz without a date is added to
    it as an edit (× takes it back before staging; a date MusicBrainz already has stays); the edit note says so.
    Release page: credits of works that were new in the editor (no MBID yet) are found through their recording,
    also when the dashboard showed them as staged (●)."""
    import re
    from common_rows import drag

    PW = sync_playwright().start()
    results = []
    WRITER_W = H.ARTISTS[3007][0]
    WRITER_Z = H.ARTISTS[3009][0]


    def open_mb(companion=False):
        b = PW.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg = None
        if companion:
            dg, _ = H.open_discogs(ctx)
        pg, errs = H.open_mb_edit(ctx, companion=companion)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        return b, pg, dg, errs


    # --- E) dates for relationships already in MusicBrainz ------------------------------------------------------
    b, pg, _, errs = open_mb()
    # the relationship editor knows the existing composer relationship of Writer W on work 1 (no date)
    pg.evaluate(f"""() => {{ const re = MB.relationshipEditor;
  re.state = {{ ...re.state, existingRels: [{{ id: 9001, linkTypeID: 168, entity0: {{ gid: '{WRITER_W}', entityType: 'artist', id: 3007, name: 'Writer W' }},
    entity1: {{ gid: '{H.WORK1}', entityType: 'work', id: 7001, name: 'x' }}, begin_date: null, end_date: null, ended: false,
    attributes: null, entity0_credit: '', entity1_credit: '', _status: 0 }}] }}; }}""")
    ww = '.dci-mx-cell[data-col="k:a15"][data-mrow^="w:0"]'
    pg.click(f'{ww} [data-act=mx-cell]'); pg.wait_for_timeout(200)          # the Discogs writer off: only MB's composer is left
    date = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-date')].find(c => c.textContent.includes('Performance 1 ·')).dataset.id")
    drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', ww)
    fill = re.sub(r'\s+', ' ', pg.locator(f'{ww} .dci-mx-fill').inner_text()) if pg.locator(f'{ww} .dci-mx-fill').count() else ''
    print('E1) grüne Zelle (nur MB-Composer) – geplant:', fill, '| data-fill:', pg.locator(ww).get_attribute('data-fill'))
    ok_e1 = '2001-03-01' in fill and pg.locator(f'{ww} [data-act=mx-fill-remove]').count() == 1
    pg.click(f'{ww} [data-act=mx-fill-remove]'); pg.wait_for_timeout(150)
    gone = pg.locator(f'{ww} .dci-mx-fill').count() == 0
    drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', ww)
    print('    × nimmt es zurück:', gone)
    ok_e1 = ok_e1 and gone
    # staging: the existing relationship is changed (date, status "edited"), the edit note says so
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
    pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
    st = pg.evaluate("(() => { const r = MB.relationshipEditor.state.added.find(x => x.id === 9001); return r && [r.begin_date, r.end_date, r._status]; })()")
    note = pg.locator('#edit-note-text').input_value()
    msgs = [m[:100] for m in pg.locator('.dci-msg').all_inner_texts() if 'existing relationship' in m]
    staged_fill = re.sub(r'\s+', ' ', pg.locator(f'{ww} .dci-mx-fill').inner_text()) if pg.locator(f'{ww} .dci-mx-fill').count() else ''
    print('E2) im Editor:', st, '| Meldung:', msgs, '| Zelle:', staged_fill)
    print('    Bearbeitungsnotiz:', [l for l in note.split('\n') if 'existing' in l or 'Dates' in l])
    ok_e2 = st and st[0] == {'year': 2001, 'month': 3, 'day': 1} and st[1] and st[1].get('day') == 3 and st[2] == 2 \
        and 'added dates to 1 existing relationship without a date' in note and '✓' in staged_fill and any('Date added to 1 existing' in m for m in msgs)
    # a second "Stage" does not change it again
    n_before = pg.evaluate("window.__dispatched.filter(a => a.oldRelationshipState && a.oldRelationshipState.id === 9001).length")
    pg.click('[data-act=apply]') if pg.locator('[data-act=apply]:not([disabled])').count() else None
    pg.wait_for_timeout(1500)
    n_after = pg.evaluate("window.__dispatched.filter(a => a.oldRelationshipState && a.oldRelationshipState.id === 9001).length")
    print('    zweites „Übernehmen“: Änderungen an der Beziehung', n_before, '→', n_after)
    ok_e2 = ok_e2 and n_before == n_after == 1
    results += [ok_e1, ok_e2]
    print('Fehler E:', errs)
    b.close()

    # a date MusicBrainz already has stays: the cell says so
    orig_ws = H.ws_release


    def ws_dated():
        d = orig_ws()
        rel = d['media'][0]['tracks'][0]['recording']['relations'][0]['work']['relations'][0]
        rel['begin'] = '1970'
        rel['end'] = '1970'
        return d


    H.ws_release = ws_dated
    b, pg, _, errs = open_mb()
    pg.click(f'{ww} [data-act=mx-cell]'); pg.wait_for_timeout(200)
    date = pg.evaluate("document.querySelector('.dci-pools-body .dci-pchip-date').dataset.id")
    drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', ww)
    m = [x[:120] for x in pg.locator('.dci-msg').all_inner_texts() if 'with a date' in x]
    print('E3) MB-Beziehung hat schon ein Datum:', m, '| geplant:', pg.locator(f'{ww} .dci-mx-fill').count())
    results.append(len(m) == 1 and pg.locator(f'{ww} .dci-mx-fill').count() == 0)
    H.ws_release = orig_ws
    b.close()

    # --- D) release page: credits of a work that was new in the editor --------------------------------------------
    H.MB_EXTRA.clear()
    b, pg, dg, errs = open_mb(companion=True)
    H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
    pg.click('tr[data-work="2"] [data-act=work-pending]'); pg.wait_for_timeout(400)   # track 3: a new work in the editor
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
    pg.wait_for_timeout(1500)
    # (the Discogs page of the test has no line for Writer Z, so the status the companion keeps is looked at)
    z = lambda: [(i['status'], i.get('note')) for i in (H.STORE.data.get('statusMap') or {}).get('items', []) if i['artistId'] == 3009]
    print('D1) nach Übernehmen – Writer Z:', z())
    H.submit_staged(pg)
    NEW = H.uid('cccccccc', 33)
    link = lambda rels: {'target-type': 'work', 'type': 'performance', 'type-id': H.LTS[278]['gid'], 'attributes': [],
                         'work': {'id': NEW, 'title': 'Song Three', 'relations': rels}}
    # the link of the new work is still an open edit: not part of the release yet
    pg.goto(f'https://musicbrainz.org/release/{H.REL}')
    H.with_companion(pg)
    dg.wait_for_timeout(6000)
    open_edit = z()
    print('D2) Link noch offen – Writer Z:', open_edit)
    pr = pg
    pr.close()
    # applied: MusicBrainz made the work (new MBID) with its composer
    H.MB_EXTRA[H.REC[2]] = [link([{'target-type': 'artist', 'type': 'composer', 'type-id': H.LTS[168]['gid'], 'attributes': [],
                                  'artist': {'id': WRITER_Z, 'name': 'Writer Z'}}])]
    dg.wait_for_timeout(9000)
    pr, _ = H.open_mb_release(dg.context)
    dg.wait_for_timeout(6000)
    done = z()
    items = [(i['role'], i['status'], i.get('note'), i.get('mb')) for i in H.STORE.data['statusMap']['items'] if i['artistId'] == 3009]
    print('D3) Werk angelegt – Writer Z:', done, '| Einträge:', items)
    results.append(open_edit == [('pending', '0/1')] and done == [('mb', '')] and items and items[0][3].get('r') and not items[0][3].get('t'))
    print('Fehler D:', errs)
    b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
    PW.stop()


def case_wattrs():
    """Works matrix attributes of the recording–work links (ac, co, de, in, ka, li, me, pa): the release group is Live in
    MusicBrainz → "li" preselected only on new links (S021); the link that exists in MusicBrainz is only offered "li?"
    (a deliberate click adds it as an edit). Works with an attribute (set or offered) are always open, others closed
    (▸ opens, "open all rows"); "Attributes for all" in the head; "spell out" is remembered. Staged: the existing link
    gets "cover", the new link "live". "Music And Lyrics By" for the whole release (R098): writer, "Song" preselected
    for new works (S020), R098 in the column head."""
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


def case_pub():
    def ticks(pg):
        return pg.evaluate("""() => {
      const out = {};
      document.querySelectorAll('.dci-matrix th[data-colhead]').forEach((th) => {
        const name = th.querySelector('.dci-mx-colname .dci-mblink, .dci-mx-colname strong').textContent.trim();
        const key = th.dataset.colhead;
        out[name] = [...document.querySelectorAll(`.dci-mx-cell[data-col="${key}"]`)]
          .filter((c) => c.classList.contains('dci-mx-on'))
          .map((c) => Number(c.closest('tr').dataset.work) + 1);
      });
      return out;
    }""")

    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1500)
        print('Log Verlage:', [l[9:100] for l in pg.locator('#dci-log li').all_inner_texts() if 'ublisher' in l])
        print('Spalten:', pg.locator('.dci-matrix th[data-colhead] .dci-mx-colname').all_inner_texts())
        t = ticks(pg)
        print('Angehakte Tracks je Spalte:', t)
        print('Verlagsstatus:', pg.evaluate("[...document.querySelectorAll('.dci-matrix th[data-colhead]')].map(th => th.querySelector('.dci-mx-colname').textContent.trim().split('\\n')[0] + ': ' + ([...th.querySelectorAll('.dci-sub')].map(x => x.textContent.trim()).filter(Boolean).join(' | ')))"))
        b.close()

    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1500)
        col = lambda name: pg.evaluate(f"[...document.querySelectorAll('.dci-matrix th[data-colhead]')].find(th => th.textContent.includes('{name}')).dataset.colhead")
        cell = lambda name, track: pg.locator(f'.dci-matrix tr[data-work="{track - 1}"] .dci-mx-cell[data-col="{col(name)}"]')
        print('Tooltip Pub Co, Track 1:', cell('Pub Co', 1).get_attribute('title'))
        print('Tooltip Other Pub, Track 1:', cell('Other Pub', 1).get_attribute('title'))
        cell('Other Pub', 1).locator('[data-act=mx-cell]').click(); pg.wait_for_timeout(300)
        cell('Ghost Pub', 4).locator('[data-act=mx-cell]').click(); pg.wait_for_timeout(300)
        # "check evidence" is in the ▾ menu of a publisher column
        pg.locator(f'[data-colhead="{col("Pub Co")}"] [data-act=mx-colmenu]').first.click(); pg.wait_for_timeout(300)
        pg.locator('[data-act=mx-pub-check]').first.click(); pg.wait_for_timeout(2500)
        t = ticks(pg)
        print('Nach Handauswahl + „Belege prüfen“:', {k.replace('MB', '').split(' not')[0]: v for k, v in t.items()})
        ok = t.get('MBOther Pub') == [1] and t.get('MBPub Co') == [1, 2]
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
        pub = pg.evaluate("window.__dispatched.filter(a => a.newRelationshipState && a.newRelationshipState.linkTypeID === 208).map(a => a.newRelationshipState.entity0.name + ' → ' + a.newRelationshipState.entity1.name)")
        print('Im Editor vorgemerkte Verlagsbeziehungen:', pub)
        print('Ergebnis:', 'OK' if ok and pub == ['Pub Co → Song One', 'Other Pub → Song One'] or ok and sorted(pub) == sorted(['Pub Co → Song One', 'Other Pub → Song One']) else 'PRÜFEN', '| Fehler:', errs)
        b.close()


run_cases(globals())
