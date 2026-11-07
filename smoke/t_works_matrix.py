"""Works matrix: track groups and notes, columns, dates of cells, attributes, publishers (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: mxdrop, matrixcols, fill, wattrs, pub, remember – each the former smoke/t_<case>.py, unchanged; `python3 t_works_matrix.py <case> …` runs only those."""
import time
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_mxdrop():
    """Works matrix and track groups. From the Discogs notes (S022): "Published by Pub Co (1, 3)" → track group and
    the tracks in the column of Pub Co (ahead of the personal publisher evidence, which gives 1, 2; [3.31.6] set, not
    suggested – ⓘ in the head and in the cells' titles names the line, item 97c); "Ghostpub (4)" matches "Ghost Pub"
    (spaces); "Written by Writer W (1, 2)" is in the Discogs track credits already (no change); "Strings arranged by
    Nobody Here (4)" is no entry (only the track group) – [3.37.0] (E5, S054) the notes read in full: Nobody Here is an entry from them,
    the strings arranger of tracks 2 and 4 (its column), and nothing of the track lists becomes a name ("Pub Co (1"). A click on a
    cell takes a track out.
    Dropped (S023): onto a column head – all its roles only for the group's tracks; onto a role – only
    that role; onto an attribute in the head of the track column – the links of the group's tracks (MB's own stay). ([3.78.0] Z-DND)
    Those replace with ⇧ Shift; a drop without it adds (the hint says so: "＋ adds the works of these tracks (⇧ Shift: only these)")."""
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
        # (3.39.6, K-7) the import complete and the matrix drawn – under load 1.5 s were not always enough
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent)) && !!document.querySelector('.dci-matrix th[data-colhead]')", 60)
        pg.wait_for_timeout(800)
        cols = lambda: pg.evaluate(COLS)

        def settle(read, want, ms=10000):
            # (3.39.6, K-7) after a drop: read again until it is as expected or the time is up (the drop is drawn later under load;
            # 3.40.0: 10 s instead of 4 – a full run missed a row once)
            got = read()
            for _ in range(ms // 200):
                if got == want:
                    break
                pg.wait_for_timeout(200)
                got = read()
            return got
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
            and any('Writer W' in x and 'only a track group' in x for x in logs) \
            and c0.get('Nobody Here') == ['2', '4'] and any('Nobody Here (arranger) on tracks 2, 4' in x for x in logs) and not any('(' in k for k in c0)
        pg.click(f'{cell("Pub Co", 3)} [data-act=mx-cell]')
        # ([3.78.0] Z-FLK) the cell drawn anew, not a time
        c1 = {'Pub Co': settle(lambda: cols().get('Pub Co'), ['1'])}
        print('A2) Track 3 weggeklickt:', c1.get('Pub Co'))
        ok_a = ok_a and c1.get('Pub Co') == ['1']
        results.append(ok_a)

        # B) a track group onto a column head, with Shift, onto one role
        pg.click('[data-act=tg-new]'); pg.fill('[data-f=tg-name]', 'Side A')
        pg.check('[data-f=tg-track][data-i="0"]'); pg.check('[data-f=tg-track][data-i="1"]'); pg.click('[data-act=tg-save]'); pg.wait_for_timeout(200)
        gid = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Side A')).dataset.id")
        wz = colkey('Writer Z')
        print('B0) Writer Z vorher:', cols().get('Writer Z'))
        drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', f'[data-colhead="{wz}"] .dci-mx-card .dci-mx-credit', shift=True)
        b1 = settle(lambda: cols().get('Writer Z'), ['1+', '2+'])
        # without Shift: the group of track 4 added (synthetic events; the hint with and without the Shift key)
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
      dst.dispatchEvent(new DragEvent('drop', {{ bubbles: true, cancelable: true, dataTransfer: dt }}));
      src.dispatchEvent(new DragEvent('dragend', {{ bubbles: true, dataTransfer: dt }}));
      return out; }})()""")
        pg.wait_for_timeout(300)
        b2 = settle(lambda: cols().get('Writer Z'), ['1+', '2+', '4+'])
        print('B1) „Side A“ mit Umschalt auf Writer Z:', b1, '| ohne Umschalt Track 4 dazu:', b2, '| Hinweise:', hints)
        ok_b = b1 == ['1+', '2+'] and b2 == ['1+', '2+', '4+'] and hints[0] == 'dashed' and 'adds the works of these tracks (⇧ Shift: only these)' in hints[1] \
            and 'only the works of these tracks' in hints[2] and 'adds' not in hints[2]
        # onto one role: lyricist only on the works of track 1 (group "Pub Co · 1, 3" → track 1 has a work, 3 waits)
        g13 = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Pub Co')).dataset.id")
        lyr = pg.evaluate(f"[...document.querySelectorAll('[data-colhead=\"{wz}\"] [data-tgrole]')].find(r => r.textContent.trim() === 'lyricist').dataset.tgrole")
        drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{g13}"] .dci-chip-main', f'[data-colhead="{wz}"] [data-tgrole="{lyr}"]', shift=True)
        # [3.31.8] a moment for the drop to be drawn (under load the reading came too early now and then)
        pg.wait_for_timeout(400)
        roles = settle(lambda: pg.evaluate(f"""[1, 2, 3, 4].map(t => [...document.querySelectorAll('.dci-matrix tr[data-work="' + (t - 1) + '"] .dci-mx-cell[data-col="{wz}"] .dci-mxchip')].map(c => c.textContent.trim().split(' ')[0]).sort())"""),
                       [['composer', 'lyricist'], ['composer'], ['lyricist'], ['composer']])
        print('B2) „Pub Co · 1, 3“ auf die Rolle lyricist – Rollen je Track:', roles)
        ok_b = ok_b and roles == [['composer', 'lyricist'], ['composer'], ['lyricist'], ['composer']]
        results.append(ok_b)

        # C) onto an attribute in the head of the track column: "li" for the works of "Side A" (tracks 1, 2)
        pg.click('tr[data-work="1"] [data-act=work-pending]')
        H.wait_ok(pg, "!document.querySelector('tr[data-work=\"1\"] [data-act=work-pending]')", 10)
        pg.click('tr[data-work="2"] [data-act=work-pending]')
        H.wait_ok(pg, "!document.querySelector('tr[data-work=\"2\"] [data-act=work-pending]')", 10)
        drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', '.dci-wattrs-all [data-tgattr=live]', shift=True)
        live = settle(lambda: pg.evaluate("""[...document.querySelectorAll('.dci-matrix tbody tr[data-mrow]')].filter(tr => tr.dataset.mrow.match(/^[wp]:/))
      .map(tr => [Number(tr.dataset.work) + 1, [...tr.querySelectorAll('.dci-wpill-on, .dci-wpill-mb')].map(b => b.textContent.trim())])"""), [[1, ['li✎']], [2, ['li']], [3, []]])
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
    # (3.39.6) as on MusicBrainz: creative direction on the release group, not on the release (Q003 answers it there)
    H.lt(146, '0e2d1e4b-1d3a-4f7e-8f2c-6a5b4c3d2e10', 'creative direction', 'artist', 'release_group', (1,))
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
        row = lambda: pg.locator('tr.dci-row').filter(has=pg.locator('.dci-drole[data-raw="Directed By"]')).first
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
        ok_a = ok_a and picks[0][:2] == ('chorus master', 'recording') and picks[1][:2] == ('creative direction', 'release_group') \
            and picks[2][0] == 'misc' and picks[2][2] == 'director' and 'miscellaneous support' in picks[2][3]
        results.append(ok_a)

        # B) take a column out and back
        WK = pg.evaluate("[...document.querySelectorAll('[data-colhead]')].find(h => h.textContent.includes('Writer W')).dataset.colhead")
        writer_rows = lambda: pg.evaluate("""[...document.querySelectorAll('.dci-group')].filter(g => (g.querySelector('.dci-gname') || {textContent: ''}).textContent.includes('Writer W'))
      .flatMap(g => [...g.querySelectorAll('tr.dci-row')]).map(tr => (tr.className.match(/dci-lv-(\\w+)/) || [])[1])""")
        before = writer_rows()
        pg.click(f'[data-colhead="{WK}"] [data-act=mx-colmenu]'); pg.wait_for_timeout(200)  # ([Z-WMX] 3.52.0: « and ✕ in the menu)
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
        pg.click(f'[data-colhead="{mbcol}"] [data-act=mx-colmenu]'); pg.wait_for_timeout(200)  # ([Z-WMX] 3.52.0: ✕ in the menu)
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
    pg.locator('tr[data-work="2"] [data-act=work-pending]').evaluate('b => b.click()'); pg.wait_for_timeout(400)   # track 3: a new work in the editor
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
    pg.wait_for_timeout(1500)
    # (the Discogs page of the test has no line for Writer Z, so the status the companion keeps is looked at)
    z = lambda: [(i['status'], i.get('note')) for i in (H.STORE.data.get(f'statusMap:{H.REL}') or {}).get('items', []) if i['artistId'] == 3009]
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
    items = [(i['role'], i['status'], i.get('note'), i.get('mb')) for i in H.STORE.data[f'statusMap:{H.REL}']['items'] if i['artistId'] == 3009]
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
        pg.click('[data-act=mx-defaults]'); pg.wait_for_timeout(200)  # ([Z-WMX] 3.52.0: the defaults of new works in their popover)
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
        if not pg.locator('[data-act=mx-wattr-openall]').count():  # ([Z-WMX] 3.52.0: behind ⋯ in the corner)
            pg.click('[data-act=mx-cornermore]'); pg.wait_for_timeout(200)
        pg.click('[data-act=mx-wattr-openall]'); pg.wait_for_timeout(200)
        all_open = [x[0] for x in pills(p3)]
        if not pg.locator('[data-act=mx-wattr-openall]').count():  # ([Z-WMX] 3.52.0: behind ⋯ in the corner)
            pg.click('[data-act=mx-cornermore]'); pg.wait_for_timeout(200)
        pg.click('[data-act=mx-wattr-openall]'); pg.wait_for_timeout(200)
        print('B3) Track 3 ohne Attribut: zu', closed, '| ▸ auf:', opened, '| alle Zeilen auf:', all_open, '| wieder zu:', pills(p3))
        ok_b = ok_b and closed[0] == [] and 'attribute' in closed[1] and len(opened) == 5 and len(all_open) == 5 and pills(p3) == []
        # Attributes for all: "me" on for all, then off again
        pg.click('.dci-wattrs-all .dci-wpill[data-attr=medley]'); pg.wait_for_timeout(200)
        on_all = [state(s).get('me') for s in (w1, p2, p3)]
        pg.click('.dci-wattrs-all .dci-wpill[data-attr=medley]'); pg.wait_for_timeout(200)
        off_all = [state(s).get('me') for s in (w1, p2)] + [pills(p3)]
        print('B4) „me“ für alle:', on_all, '| wieder aus:', off_all)
        ok_b = ok_b and on_all == ['on', 'on', 'on'] and off_all == ['off', 'off', []]
        # spell out: names instead of short forms, remembered
        if not pg.locator('[data-act=mx-wattr-long]').count():  # ([Z-WMX] 3.52.0: behind ⋯ in the corner; a click elsewhere closes it)
            pg.click('[data-act=mx-cornermore]'); pg.wait_for_timeout(200)
        pg.click('[data-act=mx-wattr-long]'); pg.wait_for_timeout(200)
        long_ = [x[0] for x in pills(w1)]
        stored = pg.evaluate("localStorage.getItem('dci-wattr-long')")
        if not pg.locator('[data-act=mx-wattr-long]').count():  # ([Z-WMX] 3.52.0: behind ⋯ in the corner; a click elsewhere closes it)
            pg.click('[data-act=mx-cornermore]'); pg.wait_for_timeout(200)
        pg.click('[data-act=mx-wattr-long]'); pg.wait_for_timeout(200)
        print('B5) ausgeschrieben:', long_, '| gespeichert:', stored, '| wieder kurz:', [x[0] for x in pills(w1)])
        ok_b = ok_b and long_[0] == 'cover✎' and long_[2] == 'live?' and stored == 'true' and pg.evaluate("localStorage.getItem('dci-wattr-long')") is None
        results.append(ok_b)

        # C) staging: the existing link gets "cover" (not "live"), the new links: track 2 "live", track 3 nothing
        pg.evaluate(f"""() => {{ const re = MB.relationshipEditor;
      re.state = {{ ...re.state, existingRels: [{{ id: 9101, linkTypeID: 278, entity0: {{ gid: '{H.REC[0]}', entityType: 'recording', id: 5001, name: 'Song One' }},
        entity1: {{ gid: '{H.WORK1}', entityType: 'work', id: 7001, name: 'Song One' }}, begin_date: null, end_date: null, ended: false,
        attributes: null, entity0_credit: '', entity1_credit: '', _status: 0 }}] }}; }}""")
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


def case_remember():
    """Credits Importer 3.36.4 (146): the choices of the works matrix of a remembered release after the
    page is loaded again (⚙ Settings → Cache on): an attribute set on the link in MusicBrainz ("co"), a new work planned for
    track 2, the column Writer W taken out (its rows still on "Skip"; brought back, they are not), a column date, the type of
    new works – all as before."""
    import re
    for i, n in [(567, 'cover'), (578, 'live'), (750, 'medley')]:
        H.attr(i, n, i)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578, 750))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.REMEMBER = True
    PILLS = """(sel) => [...document.querySelectorAll(sel + ' .dci-wattrs .dci-wpill')].map(b => [b.textContent.trim(),
  (b.className.match(/dci-wpill-(\\w+)/) || [])[1]])"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())

        def load():
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)

        w1 = 'tr[data-work="0"][data-mrow^="w:0"]'
        p2 = 'tr[data-work="1"][data-mrow^="p:1"]'
        writer_rows = lambda: pg.evaluate("""[...document.querySelectorAll('.dci-group')].filter(g => (g.querySelector('.dci-gname') || {textContent: ''}).textContent.includes('Writer W'))
      .flatMap(g => [...g.querySelectorAll('tr.dci-row')]).map(tr => (tr.className.match(/dci-lv-(\\w+)/) || [])[1])""")

        def state():
            other = pg.evaluate("[...document.querySelectorAll('[data-colhead^=\"k:\"]')].filter(h => !h.textContent.includes('Writer W')).map(h => h.dataset.colhead)[0] || ''")
            cd = ''
            if other:
                pg.click(f'[data-colhead="{other}"] [data-act=mx-colmenu]'); pg.wait_for_timeout(300)
                cd = pg.locator(f'[data-colhead="{other}"] [data-f=cd-by]').input_value()
                pg.click(f'[data-colhead="{other}"] [data-act=mx-colmenu]'); pg.wait_for_timeout(200)
            stub = pg.locator('th.dci-mx-removed [data-act=mx-col-restore]')
            if not pg.locator('[data-f=work-type]').count():  # ([Z-WMX] 3.52.0: the defaults of new works in their popover)
                pg.click('[data-act=mx-defaults]'); pg.wait_for_timeout(200)
            wtype = pg.evaluate("(() => { const s = document.querySelector('[data-f=work-type]'); return s ? s.options[s.selectedIndex].text : ''; })()")
            return {'co': dict((x[0].rstrip('?✎✓'), x[1]) for x in pg.evaluate(PILLS, w1)).get('co'), 'neu': pg.locator(p2).count(),
                    'raus': stub.get_attribute('title') if stub.count() else '', 'zeilen': writer_rows(), 'datum': cd, 'typ': wtype}

        load()
        # (a row without an attribute is closed: ▸ opens it)
        if not pg.locator(f'{w1} .dci-wpill[data-attr=cover]').count():
            pg.click(f'{w1} [data-act=mx-wattr-open]'); pg.wait_for_timeout(200)
        pg.click(f'{w1} .dci-wpill[data-attr=cover]'); pg.wait_for_timeout(200)
        pg.click('tr[data-work="1"] [data-act=work-pending]'); pg.wait_for_timeout(300)
        wk = pg.evaluate("[...document.querySelectorAll('[data-colhead]')].find(h => h.textContent.includes('Writer W')).dataset.colhead")
        pg.click(f'[data-colhead="{wk}"] [data-act=mx-colmenu]'); pg.wait_for_timeout(200)  # ([Z-WMX] 3.52.0: « and ✕ in the menu)
        pg.click(f'[data-colhead="{wk}"] [data-act=mx-col-remove]'); pg.wait_for_timeout(300)
        other = pg.evaluate("[...document.querySelectorAll('[data-colhead^=\"k:\"]')].filter(h => !h.textContent.includes('Writer W')).map(h => h.dataset.colhead)[0] || ''")
        if other:
            pg.click(f'[data-colhead="{other}"] [data-act=mx-colmenu]'); pg.wait_for_timeout(300)
            pg.fill(f'[data-colhead="{other}"] [data-f=cd-by]', '1999'); pg.wait_for_timeout(200)
            pg.click(f'[data-colhead="{other}"] [data-act=mx-colmenu]'); pg.wait_for_timeout(200)
        if not pg.locator('[data-f=work-type]').count():  # ([Z-WMX] 3.52.0: the defaults of new works in their popover)
            pg.click('[data-act=mx-defaults]'); pg.wait_for_timeout(200)
        sel = pg.locator('[data-f=work-type]')
        label = 'Aria'
        sel.select_option(label=label); pg.wait_for_timeout(200)
        pg.wait_for_timeout(1600)
        before = state()
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        load()
        after = state()
        print('vorher:', before)
        print('nachher:', after)
        ok = before == after and before['co'] == 'on' and before['neu'] == 1 and 'Writer W' in before['raus'] and before['zeilen'] \
            and all(x == 'skip' for x in before['zeilen']) and before['datum'] == '1999' and before['typ'] == label
        results.append(bool(ok))
        # the column brought back: its rows (mapped to this import's rows) no longer skipped
        pg.click('th.dci-mx-removed [data-act=mx-col-restore]'); pg.wait_for_timeout(300)
        back = writer_rows()
        head = pg.locator(f'[data-colhead="{wk}"]').count()
        print('zurückgeholt:', back, '| Spaltenkopf:', head)
        results.append(back == [] and head == 1)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_statgaps():
    """Credits Importer 3.41.15 (the check of Block BF, Z-STV): "Gaps closed" of the statistics from what is submitted. The link of
    track 1 with its work exists in MusicBrainz; "co" (cover) clicked, staged, "Enter edit": the record holds that relationship as
    supplemented ("s") with what was added ("attrs"), and gaps.attrs 1 (until 3.41.14 the stagings were counted – a supplement taken
    out in the editor counted all the same)."""
    for i, n in [(567, 'cover'), (578, 'live')]:
        H.attr(i, n, i)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    ENTER_EDIT = """(() => { if (document.getElementById('test-enter-edit')) return; const ta = document.getElementById('edit-note-text'); const f = document.createElement('form');
  f.addEventListener('submit', (e) => e.preventDefault()); ta.parentNode.insertBefore(f, ta); f.appendChild(ta); const btn = document.createElement('button');
  btn.type = 'submit'; btn.className = 'submit positive'; btn.textContent = 'Enter edit'; btn.id = 'test-enter-edit'; f.appendChild(btn); })()"""
    STAT_COUNT = """() => new Promise((res) => { const q = indexedDB.open('dci-stats', 1); q.onupgradeneeded = () => q.result.createObjectStore('subs', { keyPath: 'id' });
  q.onsuccess = () => { const tx = q.result.transaction('subs', 'readonly'); const g = tx.objectStore('subs').getAll(); g.onsuccess = () => res(g.result); g.onerror = () => res(null); };
  q.onerror = () => res(null); })"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(500)
        w1 = 'tr[data-work="0"][data-mrow^="w:0"]'
        if not pg.locator(f'{w1} .dci-wpill[data-attr=cover]').count():
            pg.click(f'{w1} [data-act=mx-wattr-open]'); pg.wait_for_timeout(200)
        pg.click(f'{w1} .dci-wpill[data-attr=cover]'); pg.wait_for_timeout(200)
        pg.evaluate(f"""() => {{ const re = MB.relationshipEditor;
      re.state = {{ ...re.state, existingRels: [{{ id: 9101, linkTypeID: 278, entity0: {{ gid: '{H.REC[0]}', entityType: 'recording', id: 5001, name: 'Song One' }},
        entity1: {{ gid: '{H.WORK1}', entityType: 'work', id: 7001, name: 'Song One' }}, begin_date: null, end_date: null, ended: false,
        attributes: null, entity0_credit: '', entity1_credit: '', _status: 0 }}] }}; }}""")
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(500)
        # MusicBrainz's /ws/js/release after "Enter edit": the relationships staged (as t_ui_settings.py does)
        added = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0 && r.entity1).map(r => ({ lt: r.linkTypeID, e0: r.entity0.gid, e1: r.entity1.gid }))")
        recs0 = {g: [] for g in H.REC}
        rel0 = []
        for x in added:
            for e, f in ((x['e0'], x['e1']), (x['e1'], x['e0'])):
                if e in recs0:
                    recs0[e].append({'linkTypeID': x['lt'], 'target': {'gid': f}})
                    break
                if e == H.REL:
                    rel0.append({'linkTypeID': x['lt'], 'target': {'gid': f}})
                    break
        H.WS_JS_RELEASE.clear()
        H.WS_JS_RELEASE.update({'gid': H.REL, 'relationships': rel0, 'releaseGroup': {'secondaryTypeIDs': []},
                                'mediums': [{'position': 1, 'tracks': [{'number': str(i + 1), 'recording': {'gid': g, 'comment': '', 'relationships': recs0[g]}} for i, g in enumerate(H.REC)]}]})
        pg.evaluate(ENTER_EDIT)
        pg.evaluate("document.getElementById('test-enter-edit').click()")
        pg.wait_for_timeout(2500)
        recs = pg.evaluate(STAT_COUNT) or []
        r = recs[0] if recs else {}
        sup = [[it.get('lt'), it.get('f')] for it in r.get('rels', []) if it.get('k') == 's']
        print('A) Datensätze:', len(recs), '| ergänzt:', sup, '| gaps:', (r.get('x') or {}).get('gaps'))
        results.append(len(recs) == 1 and sup == [['performance', ['attrs']]] and (r.get('x') or {}).get('gaps') == {'credits': 0, 'dates': 0, 'attrs': 1})
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_review43():
    """Credits Importer 3.43.3 (full review, packages P4/P5): the list of works created in this browser and not linked yet.
    A) An entry stored with the index of another track (the tracklist changed: `i` 1, the recording of track 4) – matched by its
       recording: the work is planned on track 4 and the entry kept with the index refreshed (until 3.43.2 it was dropped from the
       list for good).
    B) An entry whose recording is not among the tracks read (a medium that could not be read): kept in the list, not planned."""
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    GHOST = H.uid('cccccccc', 4301)
    W1, W2 = H.uid('cccccccc', 4302), H.uid('cccccccc', 4303)
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.evaluate(f"""localStorage.setItem('dci-created-works:{H.REL}', JSON.stringify([
          {{ i: 1, rec: '{H.REC[3]}', gid: '{W1}', title: 'Made Here', discogsId: '', ts: 1 }},
          {{ i: 2, rec: '{GHOST}', gid: '{W2}', title: 'Elsewhere', discogsId: '', ts: 1 }}]))""")
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
        pg.wait_for_timeout(1500)
        stored = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-created-works:{H.REL}') || '[]').map(x => [x.i, x.gid])")
        planned = pg.evaluate("document.querySelector('tr[data-work=\"3\"]').textContent.replace(/\\s+/g, ' ').trim().slice(0, 120)")
        pend = [x for x in pg.evaluate(LOGS) if 'created work' in x or 'created works' in x]
        print('A/B) gespeichert:', stored, '| Track 4:', planned, '| Protokoll:', pend, '| Fehler:', errs)
        results.append(stored == [[3, W1], [2, W2]] and 'Made Here' in planned and not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_wmx():
    """Credits Importer 3.52.0 (collected item Z-WMX; mockup, Q-fp, Q-fw, Q-fz): the works matrix tidied up.
    A) The head in one line: "▾ Works matrix", the counts as chips ("4 tracks", "1 work", "3 without a work") and ⓘ on the left (its
       popover: the explanation that stood above the matrix); "Skip works" in the middle (filled, a colour of its own) with "＋ Suite …";
       on the right the defaults for new works, "Search works", "＋ New works (3)" and ⋯ (spell out, open all, clear all dates, top).
       No band "3 tracks have no work yet", no paragraph of explanation.
    B) A column head: the name whole in a line of its own (its tooltip the name), ⚠ (not linked; a click: the entry) and ▾ in the line of
       the roles; "credited as" always there; « and ✕ only in the ▾ menu.
    C) The corner: "All artists credited as: ↺ MusicBrainz names for all" – every "credited as" of the matrix emptied.
    D) A track without a work: "○ no work yet", the split button "＋ New ▾" – its menu: "Search MusicBrainz", "via form …"; "＋ attribute"
       at each row; a cell waiting for a work: a chip with an hourglass ("waits for a work" for screen readers and in the tooltip).
    E) The last column head "＋ Add a column": an MBID of an artist (a long name: smaller, whole, its tooltip) with a role adds its column;
       a place: "A column holds an artist or a label – this is a place."; no MBID: the error. (review) Its cells off (as for an entry of
       the dashboard); a label with "composer" (an artist's role) and an artist that is a column already: refused; a label with
       "publishing" (the roles of an artist and of a label apart): its column.
    F) (review) The popovers: a click elsewhere closes ⓘ; Esc closes ⋯ and the focus is on its button again (the dashboard stays);
       a click inside the defaults keeps them open; "＋ Suite …" opens and closes its box."""
    LONG = H.uid('dddddddd', 140)
    H.ARTISTS[3140] = (LONG, 'Maximilian Alexander von Hohenberg')
    PUBH = H.uid('eeeeeeee', 140)
    H.COMPANIES[1140] = ('label', PUBH, 'Pub House')
    for i, n in [(567, 'cover'), (578, 'live')]:
        H.attr(i, n, i)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "!!document.querySelector('[data-el=works] table.dci-matrix')", 60)
        pg.add_style_tag(content='#dci-log { display: none !important; }')
        pg.wait_for_timeout(600)
        a0 = pg.evaluate("""(() => { const w = document.querySelector('[data-el=works]'); const h = w.querySelector('.dci-wh');
          const box = (x) => x ? x.getBoundingClientRect() : null; const l = box(h.querySelector('.dci-wh-l')), c = box(h.querySelector('.dci-wh-c')), r = box(h.querySelector('.dci-wh-r'));
          const skip = h.querySelector('.dci-wh-c [data-act=mx-skip]'); const sb = box(skip); const hb = box(h);
          return { chips: [...h.querySelectorAll('.dci-wh-chip')].map(x => x.textContent.trim()), oneLine: Math.abs(l.top - c.top) < 6 && Math.abs(c.top - r.top) < 6,
            skip: skip ? [skip.textContent.trim(), getComputedStyle(skip).backgroundColor, Math.abs((sb.left + sb.right) / 2 - (hb.left + hb.right) / 2) < hb.width * 0.2] : null,
            suite: !!h.querySelector('.dci-wh-c [data-act=suite-add-open]'),
            right: [...h.querySelectorAll('.dci-wh-r > button, .dci-wh-r > * > button')].map(x => x.dataset.act),
            text: w.textContent.includes('have no work yet'), para: w.textContent.includes('One row per work') }; })()""")
        pg.locator('[data-el=works] [data-act=mx-help]').evaluate('b => b.click()'); pg.wait_for_timeout(200)
        a1 = pg.evaluate("(document.querySelector('[data-el=works] [data-el=works-help]') || {}).textContent || ''")
        pg.locator('[data-el=works] [data-act=mx-more]').evaluate('b => b.click()'); pg.wait_for_timeout(200)
        a2 = pg.evaluate("[...document.querySelectorAll('[data-el=works] [data-el=works-more] button')].map(x => x.dataset.act)")
        print('A)', a0, '| ⓘ:', a1[:80], '| ⋯:', a2)
        results.append(a0['chips'] == ['4 tracks', '1 work', '3 without work'] and a0['oneLine'] and a0['skip'] and a0['skip'][0] == 'Skip works'
                       and a0['skip'][1] not in ('rgba(0, 0, 0, 0)', 'rgb(255, 255, 255)') and a0['skip'][2] and a0['suite']
                       and a0['right'][:1] == ['mx-defaults'] and 'works-search-all' in a0['right'] and 'works-pending-all' in a0['right'] and 'mx-more' in a0['right']
                       and not a0['text'] and not a0['para'] and 'One row per work' in a1
                       and {'works-create-all', 'works-open-all', 'mx-clear-dates', 'mx-top'} <= set(a2))
        HEADS = """[...document.querySelectorAll('.dci-matrix thead th[data-colhead]')].map(th => { const n = th.querySelector('.dci-mx-name'); const roles = th.querySelector('.dci-mx-roles');
          return [n ? n.textContent.replace(/^MB/, '').trim() : null, n ? n.title : null, n ? n.className : null, !!(roles && roles.querySelector('[data-act=mx-goto]')), !!(roles && roles.querySelector('[data-act=mx-colmenu]')),
            !!th.querySelector('input[data-f=mx-credit], input[data-f=col-credit], .dci-mx-credit input'), !!th.querySelector('[data-act=mx-collapse]'), !!th.querySelector('[data-act=mx-col-remove]')]; })"""
        b0 = pg.evaluate(HEADS)
        print('B)', b0)
        pw = [x for x in b0 if x[0] == 'Writer W']
        gp = [x for x in b0 if x[0] == 'Ghost Pub']
        pg.locator('.dci-matrix thead th[data-colhead]').first.locator('[data-act=mx-colmenu]').first.evaluate('b => b.click()'); pg.wait_for_timeout(200)
        b1 = pg.evaluate("(m => m ? [!!m.querySelector('[data-act=mx-collapse]'), !!m.querySelector('[data-act=mx-col-remove]')] : null)(document.querySelector('.dci-matrix .dci-mx-colmenu'))")
        pg.locator('.dci-matrix .dci-mx-colmenu [data-act=mx-colmenu]').last.evaluate('b => b.click()'); pg.wait_for_timeout(200)
        print('B) Menü:', b1)
        results.append(bool(pw) and pw[0][1] == 'Writer W' and not pw[0][3] and pw[0][4] and pw[0][5] and not pw[0][6] and not pw[0][7]
                       and bool(gp) and gp[0][3] and all(x[5] for x in b0) and b1 == [True, True])
        # C) the corner: all "credited as" to the MusicBrainz names
        pg.fill('.dci-matrix thead input[data-f=mx-credit] >> nth=0', 'W. W.'); pg.locator('.dci-matrix thead input[data-f=mx-credit] >> nth=0').dispatch_event('change'); pg.wait_for_timeout(300)
        c0 = pg.evaluate("[...document.querySelectorAll('.dci-matrix thead input[data-f=mx-credit]')].map(x => x.value)")
        corner = pg.evaluate("(x => x ? x.textContent.replace(/\\s+/g, ' ').trim() : null)(document.querySelector('.dci-matrix thead .dci-mx-creditsall'))")
        pg.locator('.dci-matrix thead [data-act=mx-clear-credits]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
        c1 = pg.evaluate("[...document.querySelectorAll('.dci-matrix thead input[data-f=mx-credit]')].map(x => x.value)")
        print('C)', corner, c0, c1)
        results.append(corner == 'All artists credited as: ↺ MusicBrainz names for all' and c0[0] == 'W. W.' and not any(c1))
        # D) a track without a work
        ROW = """(i) => { const tr = document.querySelector(`.dci-matrix tr[data-work="${i}"]`); const m = tr.querySelector('.dci-mx-newmenu');
          return [(tr.querySelector('.dci-mx-line .dci-badge') || {}).textContent, [...tr.querySelectorAll('.dci-split button')].map(b => b.textContent.trim()), m ? [...m.querySelectorAll('button')].map(b => b.dataset.act) : null,
            !!tr.querySelector('.dci-wattr-add'), [...tr.querySelectorAll('td .dci-mxwait')].map(x => [x.textContent, !!x.closest('td').querySelector('.dci-hourglass'), x.closest('[title]') ? x.closest('[title]').title : ''])]; }"""
        d0 = pg.evaluate(ROW, 1)
        pg.locator('.dci-matrix tr[data-work="1"] [data-act=mx-newmenu]').evaluate('b => b.click()'); pg.wait_for_timeout(200)
        d1 = pg.evaluate(ROW, 1)
        att = [pg.evaluate("!!document.querySelector('.dci-matrix tr[data-work=\"0\"] .dci-wattr-add')")]
        pg.locator('.dci-matrix tr[data-work="1"] [data-act=work-pending]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
        att.append(pg.evaluate("(b => b ? b.textContent.trim() : null)(document.querySelector('.dci-matrix tr[data-work=\"1\"] .dci-wattr-add'))"))
        print('D)', d0, d1, '| ＋ attribute (mit Werk, neues Werk):', att)
        # (a track without any work has no link to carry attributes: "＋ attribute" once it has one, a new one too)
        results.append(d0[0] == '○ no work yet' and d0[1] == ['＋ New', '▾'] and d0[2] is None and d1[2][:2] == ['work-search', 'work-create'] and not d0[3]
                       and att == [True, '＋ attribute'] and d0[4] and all(x[0] == 'waits for a work' and x[1] and x[2].endswith('waits for a work') for x in d0[4]))
        # E) "＋ Add a column"
        pg.locator('.dci-matrix thead [data-act=mx-addcol-open]').evaluate('b => b.click()')
        pg.wait_for_selector('.dci-mx-addcol-pop [data-f=mx-addcol-mbid]', timeout=15000)
        pg.fill('.dci-mx-addcol-pop [data-f=mx-addcol-mbid]', 'nothing here')
        pg.locator('.dci-mx-addcol-pop [data-act=mx-addcol]').evaluate('b => b.click()')
        # ((3.77.0, review) the message, not a time)
        H.wait_ok(pg, "/No MBID/.test((document.querySelector('[data-el=addcol-err]') || {}).textContent || '')", 15)
        e0 = pg.evaluate("(document.querySelector('[data-el=addcol-err]') || {}).textContent || null")
        place_err = "/place/.test((document.querySelector('[data-el=addcol-err]') || {}).textContent || '')"
        pg.fill('.dci-mx-addcol-pop [data-f=mx-addcol-mbid]', f'https://musicbrainz.org/place/{H.COMPANIES[1002][1]}')
        pg.locator('.dci-mx-addcol-pop [data-act=mx-addcol]').evaluate('b => b.click()')
        # ([3.77.0] Z-FLK) the answer of the lookup, not a time. ((review) It waits in the queue of MusicBrainz requests behind the
        # personal publishers and works looked up in the background: under load more than 15 s)
        t_e1 = time.time()
        H.wait_ok(pg, place_err, 60)
        print('E) Antwort nach', round(time.time() - t_e1, 1), 's')
        e1 = pg.evaluate("(document.querySelector('[data-el=addcol-err]') || {}).textContent || null")
        pg.fill('.dci-mx-addcol-pop [data-f=mx-addcol-mbid]', f'https://musicbrainz.org/artist/{LONG}')
        pg.select_option('.dci-mx-addcol-pop [data-f=mx-addcol-role]', label='composer')
        pg.locator('.dci-mx-addcol-pop [data-act=mx-addcol]').evaluate('b => b.click()')
        H.wait_ok(pg, "[...document.querySelectorAll('.dci-matrix thead th[data-colhead] .dci-mx-name')].some(x => /Maximilian/.test(x.textContent))", 15)
        e2 = [x for x in pg.evaluate(HEADS) if x[0] and x[0].startswith('Maximilian')]
        e3 = pg.evaluate("!!document.querySelector('.dci-mx-addcol-pop')")
        CELLS = """(name) => { const ths = [...document.querySelectorAll('.dci-matrix thead th[data-colhead]')]; const k = ths.findIndex(th => (th.querySelector('.dci-mx-name') || {}).textContent?.replace(/^MB/, '').trim() === name);
          if (k < 0) return null; return [...document.querySelectorAll('.dci-matrix tbody tr[data-work]')].map(tr => tr.children[k + 1] ? tr.children[k + 1].querySelectorAll('.dci-chip-on, .dci-mx-on, [aria-pressed=true]').length : -1); }"""
        e4 = pg.evaluate(f"({CELLS})('Maximilian Alexander von Hohenberg')")
        print('E)', e0, '|', e1, '|', e2, '| offen:', e3, '| Zellen:', e4)
        results.append(e0 == 'No MBID recognized. Paste the link of an artist or label page of MusicBrainz, or its MBID.' and e1 == 'A column holds an artist or a label – this is a place.'
                       and len(e2) == 1 and e2[0][0] == 'Maximilian Alexander von Hohenberg' and e2[0][1] == 'Maximilian Alexander von Hohenberg' and 'dci-mx-name-xs' in e2[0][2] and not e3
                       and e4 is not None and not any(e4))

        def addcol(url, group, role):
            pg.locator('.dci-matrix thead [data-act=mx-addcol-open]').evaluate('b => b.click()'); pg.wait_for_timeout(200)
            pg.fill('.dci-mx-addcol-pop [data-f=mx-addcol-mbid]', url)
            pg.evaluate("""([g, r]) => { const s = document.querySelector('.dci-mx-addcol-pop [data-f=mx-addcol-role]');
              const o = [...s.querySelectorAll(`optgroup[label="${g}"] option`)].find(x => x.textContent.trim() === r); s.value = o ? o.value : ''; }""", [group, role])
            pg.locator('.dci-mx-addcol-pop [data-act=mx-addcol]').evaluate('b => b.click()'); pg.wait_for_timeout(1500)
            return pg.evaluate("(document.querySelector('[data-el=addcol-err]') || {}).textContent || null")

        e5 = addcol(f'https://musicbrainz.org/label/{PUBH}', 'artist', 'composer')
        pg.locator('.dci-matrix thead [data-act=mx-addcol-open]').evaluate('b => b.click()'); pg.wait_for_timeout(200)
        e6 = addcol(f'https://musicbrainz.org/artist/{LONG}', 'artist', 'composer')
        pg.locator('.dci-matrix thead [data-act=mx-addcol-open]').evaluate('b => b.click()'); pg.wait_for_timeout(200)
        e7 = addcol(PUBH, 'label', 'publishing')
        e8 = [x[0] for x in pg.evaluate(HEADS)]
        print('E2) Label als composer:', e5, '| schon Spalte:', e6, '| Label publishing:', e7, e8)
        results.append(e5 == '“composer” is not a role of a label – choose one of its roles.'
                       and e6 == 'Maximilian Alexander von Hohenberg is a column of the matrix already – its roles are in the ▾ of its cells.'
                       and e7 is None and 'Pub House' in e8)
        # F) the popovers
        HELP = "!!document.querySelector('[data-el=works] [data-el=works-help]')"
        pg.locator('[data-el=works] [data-act=mx-help]').click(); pg.wait_for_timeout(200)
        f0 = pg.evaluate(HELP)
        pg.locator('.dci-matrix thead .dci-mx-frontcard strong').first.click(); pg.wait_for_timeout(200)
        f1 = pg.evaluate(HELP)
        pg.locator('[data-el=works] [data-act=mx-more]').click(); pg.wait_for_timeout(200)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        f2 = [pg.evaluate("!!document.querySelector('[data-el=works] [data-el=works-more]')"), pg.evaluate("document.activeElement && document.activeElement.dataset.act"),
              pg.evaluate("!document.querySelector('#dci-overlay').hidden")]
        pg.locator('[data-el=works] .dci-wh-r [data-act=mx-defaults]').click(); pg.wait_for_timeout(200)
        pg.locator('[data-el=works] [data-el=works-defaults]').click(position={'x': 4, 'y': 4}); pg.wait_for_timeout(200)
        f3 = pg.evaluate("!!document.querySelector('[data-el=works] [data-el=works-defaults]')")
        pg.locator('[data-el=works] .dci-wh-c [data-act=suite-add-open]').evaluate('b => b.click()'); pg.wait_for_timeout(200)
        f4 = pg.evaluate("!!document.querySelector('[data-el=suite-add]')")
        pg.locator('[data-el=works] .dci-wh-c [data-act=suite-add-open]').evaluate('b => b.click()'); pg.wait_for_timeout(200)
        f5 = pg.evaluate("!!document.querySelector('[data-el=suite-add]')")
        print('F) ⓘ:', f0, f1, '| Esc ⋯:', f2, '| Standards:', f3, '| Suite:', f4, f5)
        results.append(f0 and not f1 and f2 == [False, 'mx-more', True] and f3 and f4 and not f5)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_cwr():
    """Credits Importer 3.56.0 (collected item Z-CWR, rule S082): never writer beside a more exact type of the same person on a work.
    Writer W is "Written-By" on tracks 1 and 2 (MusicBrainz has Writer W as composer of the work of track 1) and "Music By" on track 2;
    Writer Z is "Composed By", "Lyrics By" and "Written-By" on track 3; new works for tracks 2 and 3.
    A) The matrix: the writer of Writer W on tracks 1 and 2 and of Writer Z on track 3 struck through (its tooltip says why).
    B) Staged: no writer of Writer W on the work of track 1 (composer in MusicBrainz) nor on the new work of track 2 (composer);
       Writer Z composer and lyricist on the work of track 3, no writer.
    C) Rule S082 switched off: the writers are staged (as before).
    D) (review) A work found by the search and picked for track 2: MusicBrainz has Writer W as its composer – the writer of
       Writer W there struck through and not staged (until the review the relationships of a picked work were not known).
    F) (review) The form of a new work for track 3: Writer Z as composer and lyricist, not as writer.
    [3.57.0] With rule S083 off throughout: existing works are not supplemented at all otherwise (case nwa)."""
    results = []
    orig = H.discogs_release

    def rel(music_by=True):
        d = orig()
        ex = lambda name, role, i: {'name': name, 'anv': '', 'role': role, 'tracks': '', 'id': i, 'join': ''}
        if music_by:
            d['tracklist'][1]['extraartists'] = d['tracklist'][1]['extraartists'] + [ex('Writer W', 'Music By', 3007)]
        d['tracklist'][2]['extraartists'] = d['tracklist'][2]['extraartists'] + [ex('Writer Z', 'Lyrics By', 3009), ex('Writer Z', 'Written-By', 3009)]
        return d
    H.discogs_release = rel
    WW, WZ = H.ARTISTS[3007][0], H.ARTISTS[3009][0]
    LT = {167: 'writer', 168: 'composer', 165: 'lyricist'}
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.entity0 && r.entity1 && [165, 167, 168].includes(r.linkTypeID))
      .map(r => [r.entity0.gid, r.linkTypeID, r.entity1.gid || r.entity1.name]))()"""
    CHIPS = """(() => [...document.querySelectorAll('.dci-matrix .dci-mxchip-cwr')].map(c => [c.closest('tr').dataset.work, c.textContent.trim(), c.title]))()"""

    def run(rule_off):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.evaluate(f"localStorage.setItem('dci-rules-off', JSON.stringify({['S083', 'S082'] if rule_off else ['S083']}))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(800)
            for k in (1, 2):
                pg.locator(f'.dci-matrix tr[data-work="{k}"] [data-act=work-pending]').evaluate('b => b.click()')
                pg.wait_for_timeout(300)
            chips = pg.evaluate(CHIPS)
            status = pg.evaluate("[...document.querySelectorAll('.dci-status')].some(x => /writer left out/.test(x.textContent))")
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(3000)
            pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
            pg.wait_for_timeout(500)
            staged = pg.evaluate(STAGED)
            b.close()
            return chips, status, staged, errs

    chips, status, staged, errs = run(False)
    who = lambda g: 'W' if g == WW else 'Z' if g == WZ else g
    st = sorted((who(a), LT.get(lt, lt), 'WORK1' if w == H.WORK1 else 'new') for a, lt, w in staged)
    print('A)', chips, '\nB)', st, '| Hinweis:', status, '| Fehler:', errs)
    results.append(sorted((x[0], x[1]) for x in chips) == [('0', 'writer'), ('1', 'writer'), ('2', 'writer')] and all('more exact type' in x[2] for x in chips))
    results.append(not any(x[0] in ('W', 'Z') and x[1] == 'writer' for x in st) and ('W', 'composer', 'new') in st
                   and ('Z', 'composer', 'new') in st and ('Z', 'lyricist', 'new') in st and not errs)
    chips2, _, staged2, errs2 = run(True)
    st2 = sorted((who(a), LT.get(lt, lt), 'WORK1' if w == H.WORK1 else 'new') for a, lt, w in staged2)
    print('C)', chips2, st2)
    results.append(not chips2 and ('W', 'writer', 'WORK1') in st2 and ('Z', 'writer', 'new') in st2 and not errs2)
    # D) a picked work of the search, Writer W its composer in MusicBrainz (Writer W only "Written-By" on track 2); F) the form of a new work
    H.discogs_release = lambda: rel(False)
    FOUND = H.uid('cccccccc', 77)
    H.JS_WORKS[FOUND] = (7077, 'Song Two')
    H.WORK_SEARCH[:] = [{'id': FOUND, 'title': 'Song Two', 'type': 'Song', 'relations': [
        {'target-type': 'artist', 'type': 'composer', 'direction': 'backward', 'attributes': [], 'artist': {'id': WW, 'name': 'Writer W'}}]}]
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs3 = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S083']))")
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_for(pg, f"!!document.querySelector('tr[data-work=\"1\"] [data-act=work-pick][data-gid=\"{FOUND}\"]')", 30)
        before = pg.evaluate(CHIPS)
        pg.locator(f'tr[data-work="1"] [data-act=work-pick][data-gid="{FOUND}"]').evaluate('b => b.click()')
        pg.wait_for_timeout(600)
        chips3 = pg.evaluate(CHIPS)
        # F) the form of a new work for track 3
        pg.locator('tr[data-work="2"] [data-act=mx-newmenu]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
        pg.locator('tr[data-work="2"] [data-act=work-create]').first.evaluate('b => b.click()')
        pg.wait_for_selector('[data-el=sub]:not([hidden])', timeout=20000)
        info = pg.evaluate("document.querySelector('[data-el=sub-info]').textContent")
        pg.click('[data-act=sub-close]'); pg.wait_for_timeout(300)
        pg.click('[data-act=apply]')
        pg.wait_for_timeout(3000)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(500)
        staged3 = pg.evaluate(STAGED)
        b.close()
    H.WORK_SEARCH[:] = []
    H.JS_WORKS.pop(FOUND, None)
    st3 = sorted((who(a), LT.get(lt, lt), 'FOUND' if w == FOUND else 'WORK1' if w == H.WORK1 else w) for a, lt, w in staged3)
    print('D) vorher:', [x[:2] for x in before], '| nach der Wahl:', [x[:2] for x in chips3], '|', st3, '| Fehler:', errs3)
    results.append(('1', 'writer') not in [tuple(x[:2]) for x in before] and ('1', 'writer') in [tuple(x[:2]) for x in chips3]
                   and not any(x[0] == 'W' and x[2] == 'FOUND' for x in st3) and not errs3)
    print('F) Formular:', info)
    results.append('composer: Writer Z' in info and 'lyricist: Writer Z' in info and 'writer: Writer Z' not in info)
    H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_nwa():
    """Credits Importer 3.57.0 (collected item Z-NWA, rule S083): an existing work is not supplemented.
    Track 1 is linked with WORK1 in MusicBrainz; for track 2 a work of the search (FOUND) is chosen; track 3 gets a new work.
    Writer Z is "Lyrics By" on track 1 and "Music By" on track 2 (besides "Composed By" on track 3).
    A) The rows of WORK1 and FOUND have the lock; their cells are struck through and locked (a click changes nothing); the row
       of the new work not.
    B) Staged: the link of track 2 with FOUND (performance) – but no writer, composer or lyricist on WORK1 or FOUND; Writer Z
       composer of the new work. The status of the rows says why.
    C) Rule S083 switched off: Writer Z lyricist on WORK1 and composer on FOUND are staged (as before).
    D) (review) WORK1 made with the form in this browser (in "dci-own-works"): one's own work – not locked, Writer Z lyricist staged;
       FOUND still locked."""
    results = []
    orig = H.discogs_release

    def rel():
        d = orig()
        ex = lambda name, role, i: {'name': name, 'anv': '', 'role': role, 'tracks': '', 'id': i, 'join': ''}
        d['tracklist'][0]['extraartists'] = d['tracklist'][0]['extraartists'] + [ex('Writer Z', 'Lyrics By', 3009)]
        d['tracklist'][1]['extraartists'] = d['tracklist'][1]['extraartists'] + [ex('Writer Z', 'Music By', 3009)]
        return d
    H.discogs_release = rel
    WW, WZ = H.ARTISTS[3007][0], H.ARTISTS[3009][0]
    FOUND = H.uid('cccccccc', 78)
    H.JS_WORKS[FOUND] = (7078, 'Song Two')
    H.WORK_SEARCH[:] = [{'id': FOUND, 'title': 'Song Two', 'type': 'Song', 'relations': [
        {'target-type': 'artist', 'type': 'writer', 'direction': 'backward', 'attributes': [], 'artist': {'id': WW, 'name': 'Writer W'}}]}]
    LT = {167: 'writer', 168: 'composer', 165: 'lyricist', 278: 'performance'}
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.entity0 && r.entity1 && [165, 167, 168, 278].includes(r.linkTypeID))
      .map(r => [r.entity0.gid || r.entity0.name, r.linkTypeID, r.entity1.gid || r.entity1.name]))()"""
    CHIPS = """(() => [...document.querySelectorAll('.dci-matrix .dci-mxchip-nwa')].map(c => [c.closest('tr').dataset.work, c.textContent.trim()]))()"""
    LOCKS = """(() => [...document.querySelectorAll('.dci-matrix tr[data-work]')].filter(tr => tr.querySelector('.dci-mx-wlock')).map(tr => tr.dataset.work))()"""

    def run(rule_off, own=False):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            # (the harness switches S083 off by default: here it is on unless asked)
            pg.evaluate(f"localStorage.setItem('dci-rules-off', JSON.stringify({['S083'] if rule_off else []}))")
            if own:
                pg.evaluate(f"localStorage.setItem('dci-own-works', JSON.stringify(['{H.WORK1}']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_for(pg, f"!!document.querySelector('tr[data-work=\"1\"] [data-act=work-pick][data-gid=\"{FOUND}\"]')", 30)
            pg.locator(f'tr[data-work="1"] [data-act=work-pick][data-gid="{FOUND}"]').evaluate('b => b.click()')
            pg.wait_for_timeout(400)
            pg.locator('.dci-matrix tr[data-work="2"] [data-act=work-pending]').evaluate('b => b.click()')
            pg.wait_for_timeout(500)
            chips = pg.evaluate(CHIPS)
            locks = pg.evaluate(LOCKS)
            # a click on a locked cell changes nothing (it has no button)
            buttons = pg.evaluate("[...document.querySelectorAll('.dci-matrix td.dci-mx-wlocked [data-act=mx-cell], .dci-matrix td.dci-mx-wlocked [data-act=mx-menu]')].length")
            status = pg.evaluate("[...document.querySelectorAll('.dci-status')].some(x => /the work exists in MusicBrainz/.test(x.textContent))")
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(3000)
            pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
            pg.wait_for_timeout(500)
            staged = pg.evaluate(STAGED)
            b.close()
            return chips, locks, buttons, status, staged, errs

    name = lambda g: 'W' if g == WW else 'Z' if g == WZ else 'WORK1' if g == H.WORK1 else 'FOUND' if g == FOUND else 'rec' if g in H.REC else g
    chips, locks, buttons, status, staged, errs = run(False)
    st = sorted((name(a), LT.get(lt, lt), name(w)) for a, lt, w in staged)
    print('A) gestrichen:', chips, '| Schloss:', locks, '| Knöpfe in gesperrten Zellen:', buttons, '\nB)', st, '| Hinweis:', status, '| Fehler:', errs)
    results.append(sorted(set(locks)) == ['0', '1'] and ('0', 'lyricist') in [tuple(x) for x in chips] and ('1', 'composer') in [tuple(x) for x in chips]
                   and not any(x[0] == '2' for x in chips) and buttons == 0)
    results.append(('rec', 'performance', 'FOUND') in st and not any(x[2] in ('WORK1', 'FOUND') and x[1] != 'performance' for x in st)
                   and ('Z', 'composer', 'Song Three') in st and status and not errs)
    chips2, locks2, _, _, staged2, errs2 = run(True)
    st2 = sorted((name(a), LT.get(lt, lt), name(w)) for a, lt, w in staged2)
    print('C)', chips2, locks2, st2)
    results.append(not chips2 and not locks2 and ('Z', 'lyricist', 'WORK1') in st2 and ('Z', 'composer', 'FOUND') in st2 and not errs2)
    _, locks4, _, _, staged4, errs4 = run(False, own=True)
    st4 = sorted((name(a), LT.get(lt, lt), name(w)) for a, lt, w in staged4)
    print('D)', locks4, st4)
    results.append(locks4 == ['1'] and ('Z', 'lyricist', 'WORK1') in st4 and ('Z', 'composer', 'FOUND') not in st4 and not errs4)
    H.WORK_SEARCH[:] = []
    H.JS_WORKS.pop(FOUND, None)
    H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_creditskip():
    """Credits Importer 3.64.0 (collected item Z-WSK, rule S093): "Skip credits" beside the work of a track in the works matrix.
    Track 1 is linked with WORK1 (Writer Z "Lyrics By" there); track 3 gets a new work (Writer Z composer).
    A) "Skip credits" on track 1: its cells struck through and locked, the button now "↺ Take credits"; staged: nothing on WORK1
       (no lyricist, no writer) – the recording credits of track 1 stay, the new work of track 3 keeps Writer Z composer.
    B) "↺ Take credits" again: Writer Z lyricist of WORK1 staged as before.
    C) Rule S093 off: no button.
    D) (review) The tracks without a work skipped: the footer no longer counts them as waiting for a work; the form of a new work for
       one of them carries no writers."""
    results = []
    orig = H.discogs_release

    def rel():
        d = orig()
        d['tracklist'][0]['extraartists'] = d['tracklist'][0]['extraartists'] + [{'name': 'Writer Z', 'anv': '', 'role': 'Lyrics By', 'tracks': '', 'id': 3009, 'join': ''}]
        return d
    H.discogs_release = rel
    WZ = H.ARTISTS[3009][0]
    REC1 = H.REC[0]
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.entity0 && r.entity1)
      .map(r => [r.entity0.gid || r.entity0.name, r.linkTypeID, r.entity1.gid || r.entity1.name]))()"""

    def run(clicks, off=False):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S083', 'S093']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.locator('.dci-matrix tr[data-work="2"] [data-act=work-pending]').evaluate('b => b.click()')
            pg.wait_for_timeout(400)
            nbtn = pg.evaluate("document.querySelectorAll('.dci-matrix [data-act=mx-creditskip]').length")
            for _ in range(clicks):
                pg.locator('.dci-matrix tr[data-work="0"] [data-act=mx-creditskip]').evaluate('b => b.click()')
                pg.wait_for_timeout(400)
            st = pg.evaluate("""(() => { const tr = document.querySelector('.dci-matrix tr[data-work="0"]'); const b = tr.querySelector('[data-act=mx-creditskip]');
              return { btn: b ? [b.textContent.trim(), b.getAttribute('aria-pressed')] : null, skipped: tr.querySelectorAll('td.dci-mx-cskipped').length,
                       toggles: tr.querySelectorAll('td.dci-mx-cskipped [data-act=mx-cell]').length, struck: [...tr.querySelectorAll('.dci-mxchip-nwa')].map(c => c.textContent.trim()) }; })()""")
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(3000)
            pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
            pg.wait_for_timeout(500)
            staged = pg.evaluate(STAGED)
            b.close()
            return nbtn, st, staged, errs

    nbtn, st, staged, errs = run(1)
    onW1 = [x for x in staged if x[2] == H.WORK1 and x[1] != 278]
    onRec1 = [x for x in staged if x[2] == REC1]
    newZ = [x for x in staged if x[0] == WZ and x[1] == 168]
    print('A) Knöpfe:', nbtn, '|', st, '| auf WORK1:', onW1, '| Aufnahme 1:', len(onRec1), '| Writer Z composer:', newZ, '| Fehler:', errs)
    results.append(nbtn >= 3 and st['btn'] == ['↺ Take credits', 'true'] and st['skipped'] >= 1 and st['toggles'] == 0 and 'lyricist' in st['struck'])
    results.append(not onW1 and len(onRec1) >= 1 and newZ and not errs)
    _, st2, staged2, _ = run(2)
    print('B)', st2['btn'], [x for x in staged2 if x[2] == H.WORK1 and x[1] != 278])
    results.append(st2['btn'] == ['Skip credits', 'false'] and [WZ, 165, H.WORK1] in staged2)
    nbtn3, _, _, _ = run(0, off=True)
    print('C) Knöpfe:', nbtn3)
    results.append(nbtn3 == 0)
    # (review) the tracks without a work skipped: no question about works for it on "Stage", and the form of a new work without its writers
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.dismiss())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        before = pg.evaluate("[...document.querySelectorAll('#dci-overlay *')].some(e => e.children.length === 0 && /^\\d+ tracks? without a work$|writing credits but no work yet/.test(e.textContent.trim()))")
        for k in ('1', '2', '3'):
            pg.locator(f'.dci-matrix tr[data-work="{k}"] [data-act=mx-creditskip]').evaluate('b => b.click()')
            pg.wait_for_timeout(300)
        waiting = pg.evaluate("[...document.querySelectorAll('#dci-overlay *')].some(e => e.children.length === 0 && /^\\d+ tracks? without a work$|writing credits but no work yet/.test(e.textContent.trim()))")
        pg.locator('.dci-matrix tr[data-work="2"] [data-act=mx-newmenu]').evaluate('b => b.click()')
        pg.wait_for_timeout(300)
        pg.locator('.dci-matrix tr[data-work="2"] [data-act=work-create]').evaluate('b => b.click()')
        pg.wait_for_timeout(800)
        src = pg.evaluate("(() => { const f = [...document.querySelectorAll('iframe')].find(x => /work\\/create/.test(x.src)); return f ? f.src : ''; })()")
        b.close()
    print('D) wartet vorher:', before, '| nachher:', waiting, '| Formular:', src[:160], '| rels:', 'rels.0' in src)
    results.append(before and not waiting and '/work/create' in src and 'rels.0' not in src)
    H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_publevel():
    """Credits Importer 3.64.0 (collected item Z-PUB, rule S094): each publishing row of a label switches in its column of the works
    matrix between "Work" and "Release".
    A) The column of Pub Co ("Published By") has "Work | Release", Work pressed.
    B) "Release": the row is on the release (type "published"), the column stays with Release pressed; staged: Pub Co – release
       "published", nothing of Pub Co on works.
    C) "Work" again: Pub Co – work "publishing" staged as before.
    D) Rule S094 off: no such buttons."""
    PUB = H.COMPANIES[1003][1]
    COL = """(() => { const h = [...document.querySelectorAll('.dci-matrix [data-colhead]')].find(x => /Pub Co/.test(x.textContent));
      return h ? [...h.querySelectorAll('[data-act=mx-pub-level]')].map(b => b.dataset.level + (b.getAttribute('aria-pressed') === 'true' ? '*' : '')) : null; })()"""
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.entity0 && r.entity1).map(r => [r.entity0.gid || r.entity0.name, r.linkTypeID, r.entity1.gid || r.entity1.name]))()"""
    results = []

    def run(levels, off=False):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S083', 'S094']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            out = {'start': pg.evaluate(COL)}
            for lv in levels:
                pg.evaluate(f"""(() => {{ const h = [...document.querySelectorAll('.dci-matrix [data-colhead]')].find(x => /Pub Co/.test(x.textContent));
                  h.querySelector('[data-act=mx-pub-level][data-level={lv}]').click(); }})()""")
                pg.wait_for_timeout(500)
                out[lv] = pg.evaluate(COL)
            out['type'] = pg.evaluate("""(() => { const tr = [...document.querySelectorAll('[data-group] tr.dci-row')].find(t => t.closest('[data-group]').querySelector('.dci-gname').textContent.includes('Pub Co'));
              const sel = tr && tr.querySelector('[data-f=type]'); return sel ? sel.options[sel.selectedIndex].text : null; })()""")
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(3000)
            pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
            pg.wait_for_timeout(500)
            out['staged'] = [x for x in pg.evaluate(STAGED) if x[0] == PUB]
            out['errs'] = errs
            b.close()
            return out

    o = run(['release'])
    print('A)', o['start'], '\nB)', o['release'], o['type'], o['staged'], o['errs'])
    results.append(o['start'] == ['work*', 'release'])
    results.append(o['release'] == ['work', 'release*'] and o['type'] == 'published' and any(x[1] == 32 for x in o['staged'])
                   and not any(x[1] == 208 for x in o['staged']) and not o['errs'])
    o2 = run(['release', 'work'])
    print('C)', o2['work'], o2['type'], o2['staged'])
    results.append(o2['work'] == ['work*', 'release'] and any(x[1] == 208 for x in o2['staged']) and not any(x[1] == 32 for x in o2['staged']))
    o3 = run([], off=True)
    print('D)', o3['start'])
    results.append(o3['start'] == [])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_addcolumn():
    """Credits Importer 3.68.0 (collected items Z-MXO, Z-ACO, Z-ACR, Z-MRC; rules S098–S100): "＋ Add a column".
    A) The list: "People of the release" first (the performers Bass Man, Drum Guy …), then "Labels" with the personal publisher of
       Drum Guy MusicBrainz has (Drum Pub) and that of Writer W (a column already: Hidden Pub), then "Other entries" (Bob Producer, the
       place Abbey Road Studios …).
    B) Its menu is above the head of the tracks ("Track and work") – until 3.67.0 below it (the menu was covered where it reached it);
       from 3.83.0 (review) out of the matrix (fixed, its own stacking order).
    C) Bass Man chosen: the role set by the rules (the most common writing role of the matrix: writer).
    D) "Drum Pub" chosen: publishing; added: a column of Drum Pub.
    E) The column of Writer W: "Another role" publishing – a second role on the tracks of its cells; a cell's menu says several roles
       can be ticked.
    F) Rules S098–S100 off: one list as before, the first role, no "Another role"."""
    DP = H.uid('eeeeeeee', 12)
    H.PERSONAL_PUBLISHERS.append({'label': DP, 'lname': 'Drum Pub', 'artist': H.ARTISTS[3004][0], 'name': 'Drum Guy'})
    H.COMPANIES[1012] = ('label', DP, 'Drum Pub')
    results = []
    LIST = """(() => { const sel = document.querySelector('.dci-mx-addcol-pop [data-f=mx-addcol-entry]'); if (!sel) return null;
      const gs = [...sel.querySelectorAll('optgroup')]; return gs.length ? gs.map(g => [g.label, [...g.querySelectorAll('option')].map(o => o.textContent.trim())]) : [['', [...sel.options].slice(1).map(o => o.textContent.trim())]]; })()"""
    ROLE = "(() => { const s = document.querySelector('.dci-mx-addcol-pop [data-f=mx-addcol-role]'); return s ? s.options[s.selectedIndex].text : null; })()"

    def run(off=False):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S083', 'S098', 'S099', 'S100']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.locator('.dci-matrix thead [data-act=mx-addcol-open]').evaluate('b => b.click()')
            pg.wait_for_timeout(1500)
            out = {'list': pg.evaluate(LIST)}
            pg.evaluate("document.querySelector('.dci-matrix thead [data-act=mx-addcol-open]').scrollIntoView({ block: 'end', inline: 'nearest' })")
            pg.wait_for_timeout(300)
            out['top'] = pg.evaluate("""(() => { const m = document.querySelector('.dci-mx-addcol-pop'); if (!m) return null; const r = m.getBoundingClientRect();
              const x = Math.max(r.left + 10, 0), y = r.top + Math.min(40, r.height / 2); const el = document.elementFromPoint(x, y);
              return el && m.contains(el) && !m.closest('.dci-mx-wrap'); })()""")
            sel = '.dci-mx-addcol-pop [data-f=mx-addcol-entry]'
            key = pg.evaluate(f"[...document.querySelector('{sel}').options].find(o => o.textContent.trim() === 'Bass Man').value")
            pg.select_option(sel, key)
            pg.wait_for_timeout(400)
            out['role'] = pg.evaluate(ROLE)
            if not off:
                v = pg.evaluate(f"[...document.querySelector('{sel}').options].find(o => /Drum Pub/.test(o.textContent)).value")
                pg.select_option(sel, v)
                pg.wait_for_timeout(400)
                out['pubrole'] = pg.evaluate(ROLE)
                pg.locator('.dci-mx-addcol-pop [data-act=mx-addcol]').evaluate('b => b.click()')
                pg.wait_for_timeout(1500)
                out['cols'] = pg.evaluate("[...document.querySelectorAll('.dci-matrix [data-colhead]')].map(h => (h.querySelector('.dci-mx-name') || h).textContent.trim())")
            # E) Writer W: another role
            ww = pg.evaluate("[...document.querySelectorAll('.dci-matrix [data-colhead]')].find(h => /Writer W/.test(h.textContent)).dataset.colhead")
            pg.locator(f'.dci-matrix [data-colhead="{ww}"] [data-act=mx-colmenu]').first.evaluate('b => b.click()')
            pg.wait_for_timeout(300)
            out['addrole'] = pg.locator(f'[data-f=mx-col-newrole][data-col="{ww}"]').count()
            if out['addrole']:
                pub = pg.evaluate(f"[...document.querySelector('[data-f=mx-col-newrole][data-col=\"{ww}\"]').options].find(o => /publish/.test(o.textContent)).value")
                pg.select_option(f'[data-f=mx-col-newrole][data-col="{ww}"]', pub)
                pg.locator(f'[data-act=mx-col-addrole][data-col="{ww}"]').evaluate('b => b.click()')
                pg.wait_for_timeout(500)
                out['roles'] = pg.evaluate(f"[...document.querySelectorAll('.dci-matrix [data-colhead=\"{ww}\"] .dci-mx-role')].map(r => (r.getAttribute('title') || r.textContent).toLowerCase())")
                pg.keyboard.press('Escape')
                pg.wait_for_timeout(200)
                pg.locator('.dci-matrix td.dci-mx-cell.dci-mx-on [data-act=mx-menu]').first.scroll_into_view_if_needed()
                pg.locator('.dci-matrix td.dci-mx-cell.dci-mx-on [data-act=mx-menu]').first.click(force=True)
                pg.wait_for_timeout(300)
                out['menu'] = pg.evaluate("(() => { const m = document.querySelector('.dci-mx-menu'); return m ? m.textContent.includes('Several roles can be ticked') : [document.querySelectorAll('.dci-matrix td.dci-mx-cell.dci-mx-on [data-act=mx-menu]').length, document.querySelectorAll('.dci-mx-menu, [class*=mx-menu]').length]; })()")
            out['errs'] = errs
            b.close()
            return out

    try:
        o = run()
        print('A)', o['list'], '\nB)', o['top'], '| C)', o['role'], '| D)', o.get('pubrole'), o.get('cols'), '\nE)', o['addrole'], o.get('roles'), o.get('menu'), o['errs'])
        heads = [g[0] for g in (o['list'] or [])]
        people = dict(o['list'] or []).get('People of the release (writers, artists, performers)', [])
        labels = dict(o['list'] or []).get('Labels', [])
        others = dict(o['list'] or []).get('Other entries', [])
        results.append(heads[:2] == ['People of the release (writers, artists, performers)', 'Labels'] and 'Bass Man' in people and 'Drum Guy' in people
                       and any('Drum Pub' in x and 'Drum Guy' in x for x in labels) and 'Bob Producer' in others and 'Bob Producer' not in people
                       # ((review) also the personal publisher of a writer who is a column already; places among the others
                       and any('Hidden Pub' in x and 'Writer W' in x for x in labels) and 'Abbey Road Studios · place' in others)
        results.append(o['top'] is True)
        results.append(o['role'] == 'writer')
        results.append(o.get('pubrole') == 'publishing' and 'Drum Pub' in ' | '.join(o.get('cols') or []))
        results.append(o['addrole'] == 1 and any('publish' in r for r in (o.get('roles') or [])) and o.get('menu') is True and not o['errs'])
        o2 = run(off=True)
        print('F)', o2['list'], o2['role'], o2['addrole'])
        # (off: the first role of the list, as before)
        results.append(len(o2['list']) == 1 and o2['addrole'] == 0 and o2['role'] == 'arranger')
    finally:
        H.PERSONAL_PUBLISHERS.pop()
        H.COMPANIES.pop(1012, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_mxarrows():
    """Credits Importer 3.70.0 (collected item Z-MXK, rule S106): the arrow keys in the works matrix.
    A) The focus on the cell of track 1 in the first column: → the next column's cell of track 1, ↓ that of track 2, ← back to the
       first column, ← once more the front of track 2 (its first button); ↑ from the first row: the head of the column.
    B) Rule S106 off: the arrows move nothing."""
    WHERE = """(() => { const a = document.activeElement; const c = a && a.closest('.dci-matrix td.dci-mx-cell, .dci-matrix th.dci-mx-front, .dci-matrix th.dci-mx-col');
      if (!c) return null; const tr = c.closest('tr'); const cells = [...tr.children].filter(x => x.matches('td.dci-mx-cell, th.dci-mx-front, th.dci-mx-col'));
      return [tr.dataset.work != null ? Number(tr.dataset.work) : 'head', cells.indexOf(c)]; })()"""
    results = []

    def run(off=False):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S083', 'S106']))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(500)
            pg.evaluate("document.querySelector('.dci-matrix tr[data-work=\"0\"] td.dci-mx-cell [data-act=mx-cell]').focus()")
            seen = [pg.evaluate(WHERE)]
            for k in ['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowLeft', 'ArrowUp', 'ArrowUp']:
                pg.keyboard.press(k)
                pg.wait_for_timeout(150)
                seen.append(pg.evaluate(WHERE))
            b.close()
            return seen, errs

    seen, errs = run()
    print('A)', seen, errs)
    results.append(seen == [[0, 1], [0, 2], [1, 2], [1, 1], [1, 0], [0, 0], ['head', 0]] and not errs)
    seen2, _ = run(off=True)
    print('B)', seen2)
    results.append(seen2[0] == [0, 1] and seen2[1] == [0, 1])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_amx383():
    """Credits Importer 3.83.0 (collected item Z-AMX): the box of "＋ Add a column" whole in view – the page 760 px wide, the matrix scrolled
    to its left end, the box opened: its left and right edges inside the window (until 3.82.0 it ran out of the matrix to the left);
    the matrix scrolled while it is open: still whole in view; its field takes text.
    C) (review) The dashboard's window moved and made smaller: the box inside it and nothing over it (until the review it kept to the
       browser's window and the bars of the dashboard that stay on top were drawn over it)."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.set_viewport_size({'width': 760, 'height': 900})
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "!!document.querySelector('.dci-matrix thead [data-act=mx-addcol-open]')", 30)
        H.wait_still(pg, "document.body.innerHTML", 15, 300)
        pg.locator('.dci-matrix thead [data-act=mx-addcol-open]').scroll_into_view_if_needed()
        pg.evaluate("document.querySelector('.dci-mx-wrap').scrollLeft = 0")
        pg.locator('.dci-matrix thead [data-act=mx-addcol-open]').evaluate('b => b.click()')
        H.wait_for(pg, "!!document.querySelector('.dci-mx-addcol-pop')", 10)
        H.wait_still(pg, "JSON.stringify(document.querySelector('.dci-mx-addcol-pop').getBoundingClientRect())", 5, 200)
        BOX = "(() => { const r = document.querySelector('.dci-mx-addcol-pop').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.top), Math.round(r.bottom), innerWidth, innerHeight]; })()"
        a = pg.evaluate(BOX)
        print('A) Kasten:', a)
        results.append(a[0] >= 0 and a[1] <= a[4] and a[2] >= 0 and a[3] <= a[5])
        pg.evaluate("document.querySelector('.dci-mx-wrap').scrollLeft = 99999")
        H.wait_still(pg, "JSON.stringify(document.querySelector('.dci-mx-addcol-pop') && document.querySelector('.dci-mx-addcol-pop').getBoundingClientRect())", 5, 200)
        b0 = pg.evaluate(BOX) if pg.evaluate("!!document.querySelector('.dci-mx-addcol-pop')") else None
        field = pg.locator('.dci-mx-addcol-pop input[type=text]').first
        field.fill('https://musicbrainz.org/artist/00000000-0000-4000-8000-000000000000')
        print('B) gescrollt:', b0, '| Feld:', field.input_value()[:30])
        results.append(b0 is not None and b0[0] >= 0 and b0[1] <= b0[4] and field.input_value().startswith('https://'))
        # C) (review) the dashboard's window moved and made smaller: the box inside it, nothing drawn over it (the bars that stay on top)
        pg.set_viewport_size({'width': 1200, 'height': 1000})
        pg.evaluate("Object.assign(document.querySelector('.dci-panel').style, { left: '320px', top: '20px', width: '860px', height: '960px' })")
        pg.wait_for_timeout(200)
        pg.evaluate("document.querySelector('.dci-mx-wrap').scrollLeft = 99999; document.querySelector('.dci-matrix thead [data-act=mx-addcol-open]').scrollIntoView({ block: 'end', inline: 'nearest' })")
        H.wait_still(pg, "JSON.stringify(document.querySelector('.dci-mx-addcol-pop').getBoundingClientRect())", 5, 200)
        c0 = pg.evaluate("""(() => { const m = document.querySelector('.dci-mx-addcol-pop'); const r = m.getBoundingClientRect();
          const p = document.querySelector('.dci-panel').getBoundingClientRect();
          const pts = [[r.left + 6, r.top + 6], [r.right - 6, r.top + 6], [r.left + 6, r.bottom - 6], [r.right - 6, r.bottom - 6]];
          return [r.left >= p.left - 1 && r.right <= p.right + 1 && r.top >= p.top - 1 && r.bottom <= p.bottom + 1,
            pts.every(([x, y]) => { const el = document.elementFromPoint(x, y); return !!el && m.contains(el); }), getComputedStyle(m).visibility]; })()""")
        print('C) im Fenster, frei:', c0)
        results.append(c0 == [True, True, 'visible'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
