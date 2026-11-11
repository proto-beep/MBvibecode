"""View: the compact view, folding, the colours of the levels, small fixes, the suggestions, rows (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: compact, fold, levels, ui301, suggstack, rows – each the former smoke/t_<case>.py, unchanged –, clineask, kindcolors, foot (3.38.4), addrolebtn (3.40.13), entryskip, entryskipkeep (3.40.15), entryskipmodes (3.40.17), footbar; `python3 t_ui_view.py <case> …` runs only those.

3.72.0: also the cases of the former t_ui_place.py – inline, logplace, keepplace, srctexts (window or page, the log, the place after a form)."""
import harness as H  # noqa: F401 – used by the cases
from caserun import launch_own, run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_compact():
    """Credits Importer 3.27.0: the compact view of the entries (collected item 31; milestone). [3.27.2] Full is the default
    again (item 72), the symbol in the head switches (item 60).
    A) Full at first (nothing stored; (3.73.0, Z-CPV) the browser has used the script before – the full view kept); the symbol in the
       head (not pressed) switches to compact – pressed, ((3.73.0) compact is the default: nothing stored; until 3.72.0) stored "compact"
       (until 3.27.1: compact by default, "Compact | Full" above the entries); one line per row – the role as written
       → type and instrument, level, tracks in short, date (or "no date"), what is open in colour (yellow "Bass: which
       instrument? electric bass guitar · double bass · acoustic bass guitar" ([3.97.0] · bass guitar), [3.32.3] the possibilities to click); the
       fields of the full row and the "credited as" block hidden.
    B) A click on the line opens the full row (its type field focused); "▴ compact" closes it again.
    C) The tracks and the date of the compact line are still drop targets: a track group ("Side A", tracks 1–2) dropped
       onto it gives "tracks 1, 2" ([Z-TRR] 3.93.0), a date of the pool shows on the line.
    D) The question answered ("double bass") – [3.32.3] in the compact line itself, the row stays closed (item 102; until
       3.32.2 the line said "Bass: which instrument?" and the question was in the opened row): the line says so, the yellow
       mark is gone.
    E) A skipped row: grey, with ✕ – out of the dashboard; the next import brings it back. [3.30.1] Its type stays on the
       line (grey), so the level does not move.
    F) "Compact" remembered after reloading ((3.73.0) as the default; "Full" stored) (3.36.1: Guitar Guy's row removed with ✕ stays removed – the release is remembered); ⚙ Settings → General ([3.29.2] Appearance) has the same switch: "Full" – every row with its fields,
       nothing stored.
    G) A jump to an incomplete row (› in the summary) opens it ([3.31.5] › until it gets there: the row of the publisher
       Ghost Pub, not in MusicBrainz, is incomplete too and shows in its entry – item 112)."""
    import re
    from common_rows import drag

    LINE = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; return [...g.querySelectorAll('tr.dci-row')].map(tr => { const c = tr.querySelector('.dci-cline');
    return { id: tr.dataset.row, open: tr.classList.contains('dci-open'), text: c ? [...c.children].map(x => x.textContent.replace(/\\s+/g, ' ').trim()).join(' ') : '',
      flags: c ? [...c.querySelectorAll('.dci-cl-flag')].map(f => [f.className.replace('dci-cl-flag ', ''), f.textContent.trim()]) : [],
      typeVisible: !!tr.querySelector('[data-f=type]') && tr.querySelector('[data-f=type]').offsetParent !== null,
      hasDate: !!(c && c.querySelector('.dci-cl-date.dci-cl-has')), x: !!(c && c.querySelector('.dci-cl-x')), bg: getComputedStyle(tr).backgroundColor }; }); }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, view=None)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(800)
        line = lambda name: pg.evaluate(LINE, name)
        # A) full at first; the symbol in the head
        VIEWBTN = '.dci-head [data-act=view-toggle]'
        a_full = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-compact')"), pg.locator(VIEWBTN).get_attribute('aria-pressed'),
                  pg.evaluate("document.querySelectorAll('.dci-toolbar [data-act=view]').length"), line('Bass Man')[0]['typeVisible']]
        pg.click(VIEWBTN)
        pg.wait_for_timeout(400)
        a0 = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-compact')"), pg.locator(VIEWBTN).get_attribute('aria-pressed'),
              pg.evaluate("[...document.querySelectorAll('.dci-variants')].filter(v => v.offsetParent !== null).length"),
              pg.evaluate("localStorage.getItem('dci-view')")]
        bass = line('Bass Man')
        print('A) zuerst voll:', a_full, '| nach dem Symbol:', a0, '\n   Bass Man:', bass)
        results.append(a_full == [False, 'false', 0, True] and a0 == [True, 'true', 0, None] and bass and ' '.join(bass[0]['text'].split()).startswith('▸ bass Recording all 4 tracks no date')
                       # [3.32.3] the question whole, its possibilities to click (item 102)
                       and bass[0]['flags'] == [['dci-cl-ask dci-cl-askq', 'Bass: which instrument? electric bass guitar · double bass · acoustic bass guitar · bass guitar']] and not bass[0]['typeVisible'])
        # B) open, close
        rid = bass[0]['id']
        pg.click(f'tr[data-row="{rid}"] .dci-cl-role')
        pg.wait_for_timeout(200)
        b1 = [line('Bass Man')[0]['open'], line('Bass Man')[0]['typeVisible'], pg.evaluate("document.activeElement.dataset.f"),
              pg.evaluate("[...document.querySelectorAll('.dci-variants')].filter(v => v.offsetParent !== null).length")]
        pg.click(f'tr[data-row="{rid}"] .dci-cl-close')
        pg.wait_for_timeout(200)
        b2 = [line('Bass Man')[0]['open'], pg.evaluate("document.activeElement.classList.contains('dci-cl-tgl')")]
        print('B) offen, Typ sichtbar, Fokus, „credited as“:', b1, '| wieder zu, Fokus:', b2)
        results.append(b1 == [True, True, 'type', 1] and b2 == [False, True])
        # C) drops onto the compact line
        pg.click('[data-act=tg-new]')
        pg.fill('[data-f=tg-name]', 'Side A')
        pg.check('[data-f=tg-track][data-i="0"]')
        pg.check('[data-f=tg-track][data-i="1"]')
        pg.click('[data-act=tg-save]')
        pg.wait_for_timeout(200)
        guitar = line('Guitar Guy')[0]['id']
        gid = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Side A')).dataset.id")
        # ([3.78.0] Z-DND) with ⇧ Shift: the row gets the group's tracks only (without it they are added)
        drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', f'tr[data-row="{guitar}"] .dci-cl-tracks', shift=True)
        c1 = line('Guitar Guy')[0]
        date = pg.evaluate("document.querySelector('.dci-pools-body .dci-pchip-date').dataset.id")
        dlabel = pg.evaluate(f"document.querySelector('.dci-pools-body .dci-pchip-date[data-id=\"{date}\"] .dci-chip-main').textContent.replace(/\\s+/g, ' ').trim()")
        drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', f'tr[data-row="{guitar}"] .dci-cl-date')
        c2 = line('Guitar Guy')[0]
        print('C) Trackgruppe:', c1['text'], '| Datum', repr(dlabel[:30]), '→', c2['text'], c2['hasDate'])
        results.append('tracks 1, 2' in c1['text'] and c2['hasDate'] and dlabel.split(' · ')[0] in c2['text'] and not c2['open'])
        # D) [3.32.3] the question answered in the compact line itself (until 3.32.2: in the opened row); the row stays closed
        pg.click(f'tr[data-row="{rid}"] .dci-cl-askq [data-act=instr-pick][data-instr="double bass"]')
        pg.wait_for_timeout(400)
        d1 = line('Bass Man')[0]
        print('D) beantwortet:', d1['text'], d1['flags'], '| offen:', d1['open'])
        # [3.38.10] the line says MusicBrainz's name of the relationship (collected item 177): the instrument
        results.append(' '.join(d1['text'].split()).startswith('▸ double bass “bass” Recording') and d1['flags'] == [] and not d1['open'])
        # E) a skipped row: grey with ✕
        pg.click(f'tr[data-row="{guitar}"] .dci-cl-role')
        pg.click(f'tr[data-row="{guitar}"] [data-act=level][data-level=skip]')
        pg.wait_for_timeout(300)
        pg.click(f'tr[data-row="{guitar}"] .dci-cl-close')
        pg.wait_for_timeout(300)
        e1 = line('Guitar Guy')[0]
        pg.click(f'tr[data-row="{guitar}"] .dci-cl-x')
        pg.wait_for_timeout(300)
        e2 = [line('Guitar Guy'), [m for m in pg.locator('.dci-msg').all_inner_texts() if 'Guitar Guy' in m][:1]]
        print('E) Skip:', e1['text'], e1['x'], e1['bg'], '| ✕:', e2)
        results.append(' '.join(e1['text'].split()).startswith('▸ guitar Skip') and e1['x'] and e1['bg'] != 'rgb(255, 255, 255)' and e2[0] is None and bool(e2[1]))
        # F) compact remembered, full in the settings
        f1 = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-compact')"), line('Bass Man')[0]['typeVisible'], pg.evaluate("localStorage.getItem('dci-view')")]
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 60)
        pg.wait_for_timeout(800)
        # [3.36.1] Guitar Guy's row removed with ✕ stays removed (the release is remembered in the tests: harness.REMEMBER)
        f2 = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-compact')"), line('Bass Man') is not None, line('Guitar Guy') is None]
        H.open_settings(pg, 'appearance')  # [3.29.2] the view is under "Appearance" now
        f3 = pg.evaluate("[...document.querySelectorAll('[data-el=settings] [data-act=view]')].map(b => [b.dataset.view, b.getAttribute('aria-pressed')])")
        pg.click('[data-el=settings] [data-act=view][data-view=full]')
        pg.wait_for_timeout(300)
        f4 = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-compact')"), pg.evaluate("localStorage.getItem('dci-view')"),
              pg.locator(VIEWBTN).get_attribute('aria-pressed'), line('Bass Man')[0]['typeVisible']]
        pg.click('[data-el=settings] [data-act=view][data-view=compact]')
        pg.wait_for_timeout(300)
        print('F) kompakt:', f1, '| neu geladen:', f2, '| Einstellungen:', f3, '| voll dort:', f4)
        results.append(f1 == [True, False, None] and f2 == [True, True, True] and f3 == [['compact', 'true'], ['full', 'false']] and f4 == [False, '"full"', 'false', True])
        pg.click('.dci-head [data-act=settings-open]')
        # G) a new row ("+ Another role") is open; closed and incomplete, a jump to it (› in the summary) opens it again
        pg.click('section.dci-group:has(.dci-gname strong:text-is("Bass Man")) [data-act=add-role]')
        pg.click('[data-el=arq] [data-act=arq-free]')  # ([Z-ARQ] 3.86.0) the role typed by hand
        pg.wait_for_timeout(300)
        rows = line('Bass Man')
        new_row = rows[-1]
        pg.click(f'tr[data-row="{new_row['id']}"] .dci-cl-close')
        pg.wait_for_timeout(300)
        g0 = [new_row['open'], line('Bass Man')[-1]['open'], line('Bass Man')[-1]['flags'][:1]]
        for _ in range(3):
            pg.click('.dci-incomplete .dci-textbtn[data-act=inc-next]')
            pg.wait_for_timeout(400)
            g1 = line('Bass Man')[-1]['open']
            if g1:
                break
        print('G) neue Zeile offen, zu, Markierung:', g0, '| nach ›:', g1)
        results.append(g0[0] and not g0[1] and g0[2] and g0[2][0][0] == 'dci-cl-bad' and g1)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_fold():
    """Credits Importer 3.29.3: the arrow next to "Artist credit for all roles" (collected item 82; the maintainer's
    answer of 2026-10-24 19:33).
    A) Full view: the arrow ▾ of "Bass Man" folds his rows to compact lines (▸, the tooltip says so); "Artist credit for
       all roles" stays; the other entries keep their fields; the focus stays on the arrow.
    B) A click on a line of the folded entry opens that row with all its fields; "▴ compact" closes it again.
    C) ▸ shows the rows with their fields again.
    D) Folded, then imported again: every entry full again.
    E) Compact view: the arrow of an entry with an open row closes its open rows.
    3.37.15 (collected item 166): in the full view
    the arrow is the first thing of the entry's head, before the name, at the same place in every entry (before: after
    "Spelling on Discogs: …", next to "Artist credit for all roles")."""
    SEC = "section.dci-group:has(.dci-gname strong:text-is('{name}'))"
    STATE = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; const a = g.querySelector('[data-act=group-fold]'); const v = g.querySelector('.dci-variants');
  return { folded: g.classList.contains('dci-gcompact'), arrow: a ? [a.textContent.trim(), a.getAttribute('aria-expanded'), a.title] : null,
    front: !!(a && a.parentElement.classList.contains('dci-ghead') && a === a.parentElement.firstElementChild), x: a ? Math.round(a.getBoundingClientRect().left) : null,
    variants: !!(v && v.offsetParent !== null),
    rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const c = tr.querySelector('.dci-c-cline'); const t = tr.querySelector('[data-f=type]');
      return [tr.dataset.row, !!(c && c.offsetParent !== null && c.textContent.trim()), !!(t && t.offsetParent !== null), tr.classList.contains('dci-open')]; }),
    focus: document.activeElement && document.activeElement.dataset.act === 'group-fold' && g.contains(document.activeElement) }; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(800)
        st = lambda name: pg.evaluate(STATE, name)
        a0 = st('Bass Man')
        pg.click(f"{SEC.format(name='Bass Man')} [data-act=group-fold]")
        pg.wait_for_timeout(400)
        a1, g1 = st('Bass Man'), st('Guitar Guy')
        print('A) vorher:', a0, '\n   eingeklappt:', a1, '\n   Guitar Guy:', g1)
        results.append(a0['arrow'][:2] == ['▾', 'true'] and a0['front'] and g1['front'] and a0['x'] == g1['x'] and not a0['folded'] and all(r[2] and not r[1] for r in a0['rows'])
                       and a1['folded'] and a1['arrow'][:2] == ['▸', 'false'] and 'Bass Man' in a1['arrow'][2] and a1['variants'] and a1['focus']
                       and all(r[1] and not r[2] for r in a1['rows']) and not g1['folded'] and all(r[2] for r in g1['rows']))
        # B) a line opens its row
        rid = a1['rows'][0][0]
        pg.click(f'tr[data-row="{rid}"] .dci-cl-role')
        pg.wait_for_timeout(300)
        b1 = st('Bass Man')['rows'][0]
        pg.click(f'tr[data-row="{rid}"] .dci-cl-close')
        pg.wait_for_timeout(300)
        b2 = st('Bass Man')['rows'][0]
        print('B) geöffnet:', b1, '| wieder zu:', b2)
        results.append(b1[2] and b1[3] and b2[1] and not b2[2] and not b2[3])
        # C) unfolded
        pg.click(f"{SEC.format(name='Bass Man')} [data-act=group-fold]")
        pg.wait_for_timeout(400)
        c1 = st('Bass Man')
        print('C) ausgeklappt:', c1)
        results.append(not c1['folded'] and c1['arrow'][:2] == ['▾', 'true'] and all(r[2] for r in c1['rows']))
        # D) folded, imported again
        pg.click(f"{SEC.format(name='Bass Man')} [data-act=group-fold]")
        pg.wait_for_timeout(300)
        d0 = st('Bass Man')['folded']
        H.src_menu(pg)
        pg.fill('[data-f=discogs-input]', f'https://www.discogs.com/release/{H.DISCOGS_ID}-x')
        pg.click('[data-act=discogs-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 60)
        pg.wait_for_timeout(800)
        d1 = st('Bass Man')
        print('D) eingeklappt:', d0, '| nach dem Import:', d1['folded'], [r[2] for r in d1['rows']])
        results.append(d0 and not d1['folded'] and all(r[2] for r in d1['rows']))
        # E) compact view: the arrow closes the open rows
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(400)
        rid = st('Bass Man')['rows'][0][0]
        pg.click(f'tr[data-row="{rid}"] .dci-cl-role')
        pg.wait_for_timeout(300)
        e0 = st('Bass Man')
        pg.click(f"{SEC.format(name='Bass Man')} [data-act=group-fold]")
        pg.wait_for_timeout(400)
        e1 = st('Bass Man')
        print('E) kompakt, offen:', e0['rows'][0], e0['arrow'], '| nach dem Pfeil:', e1['rows'][0], e1['variants'])
        results.append(e0['rows'][0][3] and e0['arrow'][1] == 'true' and 'Close the open roles' in e0['arrow'][2] and not e1['rows'][0][3] and e1['rows'][0][1] and not e1['variants'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_levels():
    """Credits Importer 3.29.2: the colours of the levels, the level in the compact line switched by a click, the tab
    "Appearance" (collected items 79, 81; the maintainer's answers of 2026-10-24 17:42 and 19:23).
    The Discogs notes give two performance dates; the June date of the column "Performance" is marked "Release level"
    (as in t_reldate.py).
    A) Colours on by default: the chosen level of a row filled in its colour (recording blue, release green), the other
       levels underlined in theirs; in the compact view the level of the line in the same colour.
    B) Compact: a click on the level of "Bass Man" (Recording, a tooltip names the next one) switches to Release – the
       date of the line follows (June 5); further clicks go through the levels the row can have, then Skip, then back to
       Recording with the March dates. The focus stays on the level.
    C) ⚙ Settings → Appearance (after "General"): text size, place, view and the colours (General has neither any more).
       A colour chosen for Release: stored, the line in it (white text on a dark colour); colours off: the chosen level
       dark as before 3.29.2, stored; "↺" of the tab: colours on again, the own colour gone."""
    H.lt(44, '67555849-61e5-455b-96e3-29733f0115f5', 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release


    def release():
        d = orig()
        d['notes'] = 'Recorded March 1–3, 2001 at Abbey Road Studios. Recorded live at the release concert June 5, 2001.'
        return d


    H.discogs_release = release
    SEC = "[...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === '{name}')"
    PRESSED = """(name) => { const g = """ + SEC.replace("'{name}'", 'name') + """; const tr = g.querySelector('tr.dci-row');
  const on = tr.querySelector('[data-act=level][aria-pressed=true]'); const off = tr.querySelector('[data-act=level]:not([aria-pressed=true])');
  return [on.dataset.level, getComputedStyle(on).backgroundColor, off ? getComputedStyle(off).boxShadow : '']; }"""
    PILL = """(name) => { const g = """ + SEC.replace("'{name}'", 'name') + """; const tr = g.querySelector('tr.dci-row');
  const b = tr.querySelector('.dci-cl-level'); const d = tr.querySelector('.dci-cl-date');
  return [b.dataset.level, b.textContent.trim(), b.title || '', getComputedStyle(b).backgroundColor, getComputedStyle(b).color, d ? d.textContent.trim() : '',
    b.tagName, document.activeElement && document.activeElement.dataset.act === 'level-next']; }"""
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
        cells = pg.evaluate("[...document.querySelectorAll('.dci-dm-col[data-dmcol=performance] .dci-dm-cell')].map(c => [c.dataset.id, c.querySelector('.dci-chip-main').textContent.trim()])")
        june = next(cid for cid, t in cells if '2001-06-05' in t)
        pg.check(f'[data-f=dm-rel][data-cell="{june}"]')
        pg.wait_for_timeout(300)
        pg.evaluate("(() => { const g = " + SEC.format(name='Guitar Guy') + "; g.querySelector('tr.dci-row [data-act=level][data-level=release]').click(); })()")
        pg.wait_for_timeout(300)
        pg.locator('[data-el=dates] .dci-apply').first.evaluate('b => b.click()')
        pg.wait_for_timeout(800)
        # A) full view
        a1 = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-lvlc')"), pg.evaluate(PRESSED, 'Bass Man'), pg.evaluate(PRESSED, 'Guitar Guy')]
        print('A) Farben an, Bass Man, Guitar Guy:', a1)
        results.append(a1[0] and a1[1][:2] == ['recording', 'rgb(47, 109, 181)'] and a1[2][:2] == ['release', 'rgb(46, 139, 87)'] and 'inset' in a1[1][2])
        # B) compact: the level by a click
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(400)
        seq = [pg.evaluate(PILL, 'Bass Man')]
        for _ in range(6):
            pg.locator("section.dci-group:has(.dci-gname strong:text-is('Bass Man')) tr.dci-row .dci-cl-level").first.click()
            pg.wait_for_timeout(400)
            seq.append(pg.evaluate(PILL, 'Bass Man'))
            if seq[-1][0] == 'recording':
                break
        for x in seq:
            print('   ', x)
        levels = [x[0] for x in seq]
        print('B) Ebenen nacheinander:', levels)
        results.append(levels[:2] == ['recording', 'release'] and levels[-2:] == ['skip', 'recording'] and len(set(levels)) == len(levels) - 1
                       and seq[0][2] == 'Level – a click switches to “Release”' and seq[0][3] == 'rgb(47, 109, 181)' and seq[0][6] == 'BUTTON'
                       # [3.32.0] the March days as their common month (D022)
                       and seq[0][5].endswith('· 2001-03') and seq[1][5].endswith('2001-06-05') and seq[1][3] == 'rgb(46, 139, 87)'
                       and seq[-1][5].endswith('· 2001-03') and seq[-2][5] == '' and all(x[7] for x in seq[1:]))
        # C) the tab "Appearance"
        H.open_settings(pg, 'general')
        gen = pg.evaluate("[!!document.querySelector('.dci-set-pane [data-act=zoom-in]'), !!document.querySelector('.dci-set-pane [data-act=view]'), !!document.querySelector('.dci-set-pane [data-f=lang]')]")
        H.open_settings(pg, 'appearance')
        app = pg.evaluate("""[!!document.querySelector('.dci-set-pane [data-act=zoom-in]'), !!document.querySelector('.dci-set-pane [data-act=view]'),
      !!document.querySelector('.dci-set-pane [data-act=place-toggle]'), document.querySelector('.dci-set-pane [data-set=level-colors]').checked,
      [...document.querySelectorAll('.dci-set-pane [data-set=level-color]')].map(x => [x.dataset.level, x.value]),
      document.querySelector('[data-el=settings] .dci-set-tab[aria-selected=true]').textContent.trim()]""")
        print('C) Allgemein (Zoom, Ansicht, Sprache):', gen, '| Darstellung:', app)
        results.append(gen == [False, False, True] and app[:4] == [True, True, True, True] and app[5] == 'Appearance'
                       and app[4] == [['recording', '#2f6db5'], ['release', '#2e8b57'], ['release_group', '#b0700c'], ['work', '#8a4f9e']])
        pg.evaluate("""(() => { const x = document.querySelector('.dci-set-pane [data-set=level-color][data-level=release]'); x.value = '#aa0000';
      x.dispatchEvent(new Event('input', { bubbles: true })); x.dispatchEvent(new Event('change', { bubbles: true })); })()""")
        pg.wait_for_timeout(300)
        pg.locator("section.dci-group:has(.dci-gname strong:text-is('Bass Man')) tr.dci-row .dci-cl-level").first.click()
        pg.wait_for_timeout(400)
        c1 = [pg.evaluate("localStorage.getItem('dci-level-palette')"), pg.evaluate(PILL, 'Bass Man')[:5:3] + pg.evaluate(PILL, 'Bass Man')[4:5]]
        pg.locator('.dci-set-pane [data-set=level-colors]').click()
        pg.wait_for_timeout(300)
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(400)
        c2 = [pg.evaluate("localStorage.getItem('dci-level-colors')"), pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-lvlc')"),
              pg.evaluate(PRESSED, 'Bass Man')[:2], pg.evaluate("document.querySelector('.dci-set-pane [data-set=level-color]').disabled")]
        pg.click('[data-el=settings] [data-act=settings-reset][data-topic=appearance]')
        pg.wait_for_timeout(500)
        # [3.34.29] the ↺ of Appearance also sets the entries back to the matrix (E4, the default): this case looks at the rows
        # as before, so "Legacy" again
        matrix_back = pg.evaluate("[localStorage.getItem('dci-entries-view'), document.querySelectorAll('section.dci-em-entry, section.dci-em-centry').length > 0]")
        pg.click('.dci-set-pane [data-act=entries-view][data-view=legacy]')
        pg.wait_for_timeout(500)
        c3 = [pg.evaluate("[localStorage.getItem('dci-level-colors'), localStorage.getItem('dci-level-palette')]"),
              pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-lvlc')"), pg.evaluate(PRESSED, 'Bass Man')[:2]]
        print('C) eigene Farbe:', c1, '| aus:', c2, '| ↺:', c3, '| Matrix wieder:', matrix_back)
        results.append(c1 == ['{"release":"#aa0000"}', ['release', 'rgb(170, 0, 0)', 'rgb(255, 255, 255)']]
                       and c2 == ['false', False, ['release', 'rgb(61, 58, 79)'], True]
                       and c3 == [[None, None], True, ['release', 'rgb(46, 139, 87)']] and matrix_back == [None, True])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ui301():
    """Credits Importer 3.30.1: small fixes of the dashboard (collected items 86, 89, 91, 92, 95; 2026-10-25).
    A) Two messages (dates from the notes), open and folded: the bar below ("Add entry manually") no longer covers
       "▾ 2 messages" / "▸ 2 messages" or the last message.
    B) ⚙ Settings → Discogs and Bandcamp view ([3.30.5] Source pages): "on mouse-over" and "on click" have tooltips.
    C) Compact: the level of a line switched by clicks (Recording → Release → Skip → Recording) stays at the same place; on
       Skip the line still shows its type (grey).
    D) "only works": a button of its own next to the levels, underlined in the colour of works; "Stage:" on the line of
       its buttons.
    E) In the page, inside a page of MusicBrainz that is 2400 px wide: the dashboard is no wider than the browser window."""
    # [3.30.8] the shared month of "March 1–3, 2001" no longer counts as a date without a group: a date that really has none
    _orig_rel = H.discogs_release


    def _rel():
        d = _orig_rel()
        d['notes'] += ' The band met on 4 July 2000.'
        return d


    H.discogs_release = _rel

    # instruments on the release level exist in MusicBrainz too (as in t_levels.py)
    H.lt(44, '67555849-61e5-455b-96e3-29733f0115f5', 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    GAP = """(() => { const m = document.querySelector('[data-el=msgs]'); const s = document.querySelector('[data-el=stick]');
  const last = m.lastElementChild; return [Math.round(s.getBoundingClientRect().top - last.getBoundingClientRect().bottom), last.className]; })()"""
    PILL = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man');
  const tr = g.querySelector('tr.dci-row'); const b = tr.querySelector('.dci-cl-level'); const t = tr.querySelector('.dci-cl-type');
  return [b.dataset.level, Math.round(b.getBoundingClientRect().left), t ? t.textContent.replace(/\\s+/g, ' ').trim() : null]; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.set_viewport_size({'width': 1300, 'height': 900})
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        # A)
        a1 = pg.evaluate(GAP)
        pg.click('[data-act=msgs-fold]')
        pg.wait_for_timeout(300)
        a2 = pg.evaluate(GAP)
        print('A) Abstand zur Leiste – offen:', a1, '| eingeklappt:', a2)
        results.append(a1[0] >= 0 and a2[0] >= 0 and a2[1] == 'dci-msgs-head')
        # B)
        H.open_settings(pg, 'discogs')
        b1 = pg.evaluate("[...document.querySelectorAll('[data-el=settings] [data-sync-mode]')].map(x => [x.dataset.syncMode, x.title])")
        pg.click('.dci-head [data-act=settings-open]')
        print('B) Tooltips:', b1)
        results.append(len(b1) == 2 and all(t for _, t in b1) and 'rests on a row' in b1[0][1] and 'Only a click' in b1[1][1])
        # C)
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(400)
        seq = [pg.evaluate(PILL)]
        for _ in range(4):
            pg.locator("section.dci-group:has(.dci-gname strong:text-is('Bass Man')) tr.dci-row .dci-cl-level").first.click()
            pg.wait_for_timeout(350)
            seq.append(pg.evaluate(PILL))
            if seq[-1][0] == 'recording':
                break
        print('C) Ebene, x, Typ:', seq)
        results.append([x[0] for x in seq] == ['recording', 'release', 'skip', 'recording'] and len({x[1] for x in seq}) == 1
                       and seq[2][2] == '')
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        # D)
        # ([Z-SCOPE] 3.112.0) no "only works" any more; "Works: with | only | without" in the line, its label beside it
        d1 = pg.evaluate("""(() => { const ow = document.querySelector('[data-act=bulk-level][data-level=only-works]');
      const st = document.querySelector('.dci-scope-label'); const sb = document.querySelector('.dci-scope button'); const c = (e) => { const r = e.getBoundingClientRect(); return r.top + r.height / 2; };
      return [!!ow, Math.round(Math.abs(c(st) - c(sb))), [...document.querySelectorAll('.dci-scope button')].map(b => b.textContent.trim()), st.textContent.trim()]; })()""")
        print('D) only works da, „Works:“ Abweichung, Knöpfe:', d1)
        results.append(not d1[0] and d1[1] <= 2 and d1[2] == ['with', 'only', 'without'] and d1[3] == 'Works:')
        # E) in the page, inside a wide page
        pg.evaluate("document.getElementById('content').style.width = '2400px'")
        H.open_settings(pg, 'appearance')
        pg.click('[data-el=settings] [data-act=place-toggle]')
        pg.wait_for_timeout(600)
        e1 = pg.evaluate("""(() => { const o = document.getElementById('dci-overlay'); const r = o.getBoundingClientRect();
      return [o.classList.contains('dci-inline'), Math.round(r.left), Math.round(r.right), document.documentElement.clientWidth,
        Math.round(document.getElementById('content').getBoundingClientRect().width)]; })()""")
        pg.set_viewport_size({'width': 1000, 'height': 900})
        pg.wait_for_timeout(400)
        e2 = pg.evaluate("(() => { const r = document.getElementById('dci-overlay').getBoundingClientRect(); return [Math.round(r.right), document.documentElement.clientWidth]; })()")
        print('E) in der Seite (in Seite, links, rechts, Fenster, Seite):', e1, '| schmaler:', e2)
        results.append(e1[0] and e1[2] <= e1[3] and e1[4] >= 2400 and e2[0] <= e2[1])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_suggstack():
    """Import 3.15.2/3.15.3: the suggestions of an entry without a match are a block right below its red mark.
    A pasted text names "John Smith"; MusicBrainz has eight artists of that name.
    A) The head line: the red mark, ([Z-MBSEARCH] 3.123.0) the kind of the entry, the field and the buttons; below it the suggestions as a block of their own, side by side
       and wrapping into more lines (3.15.3; 3.15.2 had one per line); no explanation as visible text – it is the tooltip of
       the block and of each suggestion.
    B) Five suggestions are shown, then a clearly visible "+ 3 more" (a button of its own); a click shows all eight and
       "− fewer"; in a narrow dashboard the block takes more lines.
    C) A click on a suggestion assigns it, as before."""
    IDS = [H.uid('dddddddd', 70 + k) for k in range(8)]
    H.MB_SEARCH['artist'] = [{'id': g, 'name': 'John Smith', 'disambiguation': f'singer no. {k + 1}', 'score': 100} for k, g in enumerate(IDS)]
    HEAD = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'John Smith');
  const m = g.querySelector('.dci-gmatch'); const st = m.querySelector('.dci-sugg-stack');
  const bad = m.querySelector('.dci-badge-bad'); const rb = bad.getBoundingClientRect(); const rs = st ? st.getBoundingClientRect() : null;
  const chips = st ? [...st.querySelectorAll('.dci-suggbtn')].map(c => Math.round(c.getBoundingClientRect().top)) : [];
  return { order: [...m.children].map(c => c.matches('.dci-sugg-stack') ? 'stack' : c.matches('.dci-badge-bad') ? 'mark' : c.tagName.toLowerCase() + (c.dataset.f ? ':' + c.dataset.f : c.dataset.act ? ':' + c.dataset.act : '')),
    below: rs ? rs.top >= rb.bottom - 1 && Math.abs(rs.left - rb.left) < 3 : false, lines: new Set(chips).size,
    shown: st ? [...st.querySelectorAll('[data-act=name-use]')].length : 0, more: (m.querySelector('[data-act=sugg-more]') || {}).textContent || '',
    flow: st ? getComputedStyle(st).flexDirection + ' ' + getComputedStyle(st).flexWrap : '', tip: st ? st.title : '', text: m.innerText }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Mixed by John Smith')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        H.wait_for(pg, "[...document.querySelectorAll('section.dci-group')].some(s => s.querySelector('[data-act=name-use]'))", 30)
        pg.wait_for_timeout(500)
        h = pg.evaluate(HEAD)
        print('A) Reihenfolge:', h['order'], '| darunter:', h['below'], '| Fluss:', h['flow'], '| Zeilen:', h['lines'])
        print('   Tooltip:', h['tip'][:90], '| sichtbarer Erklärtext:', 'Same name in MusicBrainz' in h['text'])
        results.append(h['order'][:3] == ['mark', 'select:match-kind', 'input:artist-input'] and h['order'][-1] == 'stack' and h['below'] and h['flow'] == 'row wrap'
                       and h['lines'] == 1 and 'Same name in MusicBrainz' in h['tip'] and 'Same name in MusicBrainz' not in h['text'])
        # B) five, then "+ 3 more"
        style = pg.evaluate("(() => { const b = document.querySelector('[data-act=sugg-more]'); const cs = getComputedStyle(b); return [cs.fontWeight, cs.borderTopStyle, cs.borderTopWidth]; })()")
        pg.locator('[data-act=sugg-more]').first.click(); pg.wait_for_timeout(300)
        h2 = pg.evaluate(HEAD)
        # many: the block spreads into more lines (a narrow dashboard)
        w0 = pg.evaluate("(() => { const p = document.querySelector('.dci-panel'); const w = p.style.width; p.style.width = '560px'; return w; })()"); pg.wait_for_timeout(500)
        h3 = pg.evaluate(HEAD)
        pg.evaluate(f"document.querySelector('.dci-panel').style.width = {w0!r}"); pg.wait_for_timeout(300)
        print('B) sichtbar:', h['shown'], h['more'], style, '| nach Klick:', h2['shown'], h2['more'], '| Zeilen breit:', h2['lines'], '| schmal:', h3['lines'])
        results.append(h['shown'] == 5 and h['more'] == '+ 3 more' and int(style[0]) >= 600 and style[1] == 'solid'
                       and h2['shown'] == 8 and h2['more'] == '− fewer' and h3['lines'] > h2['lines'])
        # C) assign the fourth
        pg.locator(f'[data-act=name-use][data-mbid="{IDS[3]}"]').first.evaluate('b => b.click()'); pg.wait_for_timeout(500)
        st = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'John Smith');
      return [g.className.match(/dci-st-(\\w+)/)[1], (g.querySelector('.dci-gmatch .dci-mblink') || {}).textContent || '', !!g.querySelector('.dci-sugg-stack')]; })()""")
        print('C) nach Klick:', st)
        results.append(st[0] == 'manual' and 'John Smith' in st[1] and not st[2])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_rows():
    def names(pg):
        return pg.locator('.dci-group .dci-gname strong').all_inner_texts()

    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        grp = lambda n: pg.locator('.dci-group').filter(has=pg.locator('.dci-gname strong', has_text=n)).first
        # 1) remove a row from Discogs and bring it back
        grp('Bob Producer').locator('[data-act=remove-row]').click(); pg.wait_for_timeout(300)
        gone = 'Bob Producer' not in names(pg)
        msg = [m for m in pg.locator('.dci-msg').all_inner_texts() if 'removed' in m.lower()]
        pg.locator('.dci-msg [data-act=row-restore]').last.click(); pg.wait_for_timeout(300)
        back = 'Bob Producer' in names(pg)
        print('1) Entfernt:', gone, msg[-1:] if msg else '', '| zurückgeholt:', back)
        # 2) remove a staged row: it is taken out of the editor at the next "Stage"
        pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        n_before = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0.name === 'Bob Producer').length")
        grp('Bob Producer').locator('[data-act=remove-row]').click(); pg.wait_for_timeout(300)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
        removed = pg.evaluate("window.__removed.map(r => r.entity0.name)")
        n_after = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0.name === 'Bob Producer').length")
        print('2) Bob Producer im Editor vorher/nachher:', n_before, n_after, '| herausgenommen:', removed)
        # 3) "Skip" all, then ([Z-SCOPE] 3.112.0) "Works: only" (was "only works"): work relationships come back, all else stays skipped
        pg.click('[data-act=bulk-level][data-level=skip]'); pg.wait_for_timeout(300)
        pg.click('[data-act=scope][data-scope=work]'); pg.wait_for_timeout(500)
        levels = pg.evaluate("""[...document.querySelectorAll('.dci-group')].map(g => g.querySelector('.dci-gname strong').textContent + ':' +
      ([...g.querySelectorAll('tr.dci-row [data-act=level][aria-pressed=true]')].map(x => x.dataset.level).join(',') || (g.querySelector('.dci-work-note') ? 'work' : '-')))""")
        print('3) Ebenen nach „nur Werke“:', levels)
        cols = pg.locator('.dci-matrix th[data-colhead] .dci-mx-colname').all_inner_texts()
        print('   Matrix-Spalten:', [c.split('\n')[0] for c in cols])
        plan = pg.evaluate("[...document.querySelectorAll('[data-el=sum]')].map(e => e.textContent).join(' ')")
        print('   Plan:', plan[:120])
        pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
        kinds = pg.evaluate("[...new Set(MB.relationshipEditor.state.added.map(r => r.linkTypeID))].sort((a, b) => a - b)")
        print('   Nach erneutem Übernehmen im Editor (Typ-IDs):', kinds, '(165 lyricist, 167 writer, 168 composer, 208 publishing, 278 performance, 297 arranger)')
        ok_kinds = all(k in (165, 167, 168, 208, 278, 297) for k in kinds) and 167 in kinds
        ok = ok_kinds and gone and back and n_before > 0 and n_after == 0 and all(l.endswith(':skip') or l.endswith(':work') for l in levels)
        print('Ergebnis:', 'OK' if ok else 'FEHLER', '| Fehler:', errs)
        b.close()

    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.click('[data-act=scope][data-scope=work]'); pg.wait_for_timeout(500)
        print('4) Ohne vorheriges Übernehmen, Plan:', pg.inner_text('[data-el=sum]').replace('\n', ' ')[:120])
        pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
        kinds = pg.evaluate("[...new Set(MB.relationshipEditor.state.added.map(r => r.linkTypeID))].sort((a, b) => a - b)")
        print('   Im Editor (Typ-IDs):', kinds, '| Ergebnis:', 'OK' if kinds and all(k in (165, 167, 168, 208, 278, 297) for k in kinds) else 'FEHLER', '| Fehler:', errs)
        b.close()


def case_clineask():
    """Credits Importer 3.32.3: a type question in the compact line (collected item 102): "Directed By"
    (Q003) shows "type to choose" with its four possibilities as buttons; "conductor" clicked → the row is conductor, the
    question gone, the row still closed."""
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'].append({'name': 'Drum Guy', 'anv': '', 'role': 'Directed By', 'tracks': '', 'id': 3004, 'join': ''})
        return d

    H.discogs_release = rel
    # [3.38.10] conductor as on MusicBrainz (the line names the type chosen by MusicBrainz's relationship type)
    H.lt(151, '234670ce-5f22-4fd0-921b-ef1662695c5d', 'conductor', 'artist', 'recording', (1,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    LINE = """() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Drum Guy');
  const tr = [...g.querySelectorAll('tr.dci-row')].find(r => /Directed By/.test(r.querySelector('.dci-cl-role').dataset.raw));
  const q = tr.querySelector('.dci-cl-askq');
  return { id: tr.dataset.row, open: tr.classList.contains('dci-open'), type: (tr.querySelector('.dci-cl-role').textContent + ' ' + (tr.querySelector('.dci-cl-type') || {}).textContent).replace(/\\s+/g, ' ').trim(),
    ask: q ? [...q.querySelectorAll('[data-act=type-pick]')].map(b => b.textContent.trim()) : null }; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, view='compact')
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        a = pg.evaluate(LINE)
        print('A) Zeile:', a)
        results.append(a['ask'] == ['conductor', 'chorus master', 'creative direction', 'miscellaneous support (task “director”)'] and not a['open'])
        pg.click(f'tr[data-row="{a["id"]}"] .dci-cl-askq [data-act=type-pick][data-opt="0"]')
        pg.wait_for_timeout(400)
        b1 = pg.evaluate(LINE)
        print('B) gewählt:', b1)
        results.append(b1['ask'] is None and 'conductor' in b1['type'] and not b1['open'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_kindcolors():
    """Credits Importer 3.32.4: the colours of the kinds (collected items 107, 108, a setting for the colours).
    A) Works matrix: the head of Writer W in the colour of artists, with the tag "Artist"; Pub Co in the colour of labels,
       "Label"; the cells stay neutral.
    B) ⚙ Settings → Appearance: "Colours for the kinds of entries" (on) and a colour per kind (artist, label, place, area,
       other); the artist colour changed to #aa0000 → the bar of Bass Man and the head of Writer W follow, stored as an own
       colour; off → grey for both; ↺ of the tab → back to the defaults.
    [3.37.8] Events have their own colour (plum, collected item 158)."""
    HEAD = """(name) => { const th = [...document.querySelectorAll('.dci-matrix th[data-colhead]')].find(t => (t.querySelector('.dci-mblink, strong') || {}).textContent.replace(/^MB/, '').trim() === name);
  if (!th) return null; const card = th.querySelector('.dci-mx-card'); const tag = th.querySelector('.dci-mx-kind');
  const cell = document.querySelector(`.dci-mx-cell[data-col="${th.dataset.colhead}"]`);
  return [[...th.classList].find(c => c.startsWith('dci-kind-')) || '', tag ? tag.textContent.trim() : '', getComputedStyle(card).borderTopColor, cell ? getComputedStyle(cell).backgroundColor : '']; }"""
    BAR = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  return g ? getComputedStyle(g).borderLeftColor : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1500)
        a = [pg.evaluate(HEAD, 'Writer W'), pg.evaluate(HEAD, 'Pub Co')]
        print('A) Köpfe:', a)
        results.append(a[0][:3] == ['dci-kind-artist', 'Artist', 'rgb(91, 111, 140)'] and a[1][:3] == ['dci-kind-label', 'Label', 'rgb(42, 138, 138)']
                       and a[0][3] in ('rgba(0, 0, 0, 0)', 'rgb(255, 255, 255)'))
        H.open_settings(pg, 'appearance')
        app = pg.evaluate("""[document.querySelector('.dci-set-pane [data-set=kind-colors]').checked,
      [...document.querySelectorAll('.dci-set-pane [data-set=kind-color]')].map(x => [x.dataset.kind, x.value])]""")
        pg.evaluate("""(() => { const x = document.querySelector('.dci-set-pane [data-set=kind-color][data-kind=artist]'); x.value = '#aa0000';
      x.dispatchEvent(new Event('input', { bubbles: true })); x.dispatchEvent(new Event('change', { bubbles: true })); })()""")
        pg.wait_for_timeout(300)
        b1 = [pg.evaluate(BAR, 'Bass Man'), pg.evaluate(HEAD, 'Writer W')[2], pg.evaluate("localStorage.getItem('dci-kind-palette')")]
        pg.locator('.dci-set-pane [data-set=kind-colors]').click()
        pg.wait_for_timeout(300)
        b2 = [pg.evaluate(BAR, 'Bass Man'), pg.evaluate(HEAD, 'Pub Co')[2], pg.evaluate("localStorage.getItem('dci-kind-colors')")]
        pg.click('[data-el=settings] [data-act=settings-reset][data-topic=appearance]')
        pg.wait_for_timeout(500)
        b3 = [pg.evaluate(BAR, 'Bass Man'), pg.evaluate("[localStorage.getItem('dci-kind-colors'), localStorage.getItem('dci-kind-palette')]")]
        print('B) Einstellung:', app, '| eigene Farbe:', b1, '| aus:', b2, '| ↺:', b3)
        results.append(app == [True, [['artist', '#5b6f8c'], ['label', '#2a8a8a'], ['place', '#4e8a3e'], ['area', '#8a6a3e'], ['event', '#8a4f7d'], ['other', '#8a8799']]]
                       and b1 == ['rgb(170, 0, 0)', 'rgb(170, 0, 0)', '{"artist":"#aa0000"}']
                       and b2 == ['rgb(138, 135, 153)', 'rgb(138, 135, 153)', 'false'] and b3 == ['rgb(91, 111, 140)', [None, None]])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_foot():
    """Credits Importer 3.38.4: the footer compact (collected item 169).
    A) 1500 px (window): one line, at most 60 px high (until 3.38.3 about 200; [Z-YELL] 3.110.0: with the counters of what is open
       two lines, at most 90 px) – ▲▼, the summary in one line ("24 new relationships ·
       ‹ 1 row incomplete › · 1 already on MB"; the levels in the tooltip), the chip "2 tracks without a work" (the whole message in
       its tooltip; clicked: shown below, again: hidden), "Preview", the short checkboxes (the long texts in their tooltips),
       "Stage …" at the right, ⓘ "Nothing is submitted …"; no "⚙ Options" ([3.56.0, Z-CWR] 24: the writer of Writer W on WORK1
       is left out beside the composer in MusicBrainz).
    B) 900 px: two lines (at most 90 px) – the checkboxes in "⚙ Options ▾": it opens above, inside the dashboard, a box ticked there
       counts; a click elsewhere and Esc close it.
    C) 600 px: "Stage …" whole and inside the dashboard, at most 120 px.
    D) Staged: the chip "✓ 30 in the editor (…)", its tooltip "… Check them there and click “Enter edit”." (at most 120 px);
       [3.38.13] (F-3) it flashes once when it comes (its text opened and closed, the dashboard closed and opened again: not again;
       the class gone after the flash).
    E) In the page (1500 px): one line, stuck to the bottom."""
    M = """(() => { const f = document.querySelector('.dci-foot'); const r = (e) => { const x = e.getBoundingClientRect(); return [Math.round(x.left), Math.round(x.top), Math.round(x.right), Math.round(x.bottom)]; };
      const vis = (e) => !!e && e.getClientRects().length > 0; const panel = document.querySelector('.dci-panel');
      return { h: Math.round(f.getBoundingClientRect().height), foot: r(f), panel: r(panel), stage: r(f.querySelector('[data-act=apply]')), info: r(f.querySelector('.dci-foot-info')),
        infoTitle: f.querySelector('.dci-foot-info').title, optbtn: vis(f.querySelector('[data-act=foot-opts]')), boxes: [...f.querySelectorAll('.dci-foot-optlist label')].map(l => [l.textContent.trim(), vis(l), l.title.slice(0, 40)]),
        sum: f.querySelector('[data-el=sum]').textContent.replace(/\\s+/g, ' ').trim(), levels: (f.querySelector('.dci-sum-new') || {}).title || '',
        preview: f.querySelector('[data-act=preview]').textContent.trim(), chips: [...f.querySelectorAll('.dci-foot-chip')].map(c => [c.textContent.trim(), c.title]),
        tops: [...new Set([...f.querySelectorAll('.dci-foot-bar > *')].filter(vis).map(e => Math.round(e.getBoundingClientRect().top + e.getBoundingClientRect().height / 2)))],
        msg: [...f.querySelectorAll('.dci-waiting, .dci-rounds, .dci-stage-done')].filter(vis).map(e => e.textContent.trim()) }; })()"""
    LIST = "(() => { const l = document.querySelector('.dci-foot-optlist'); const x = l.getBoundingClientRect(); return l.getClientRects().length ? [Math.round(x.left), Math.round(x.top), Math.round(x.right), Math.round(x.bottom)] : null; })()"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.add_style_tag(content='#dci-log { display: none !important; }')
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1500)
        # A) wide
        a = pg.evaluate(M)
        pg.click('.dci-foot-chip[data-msg=waiting]'); pg.wait_for_timeout(200)
        a_open = pg.evaluate(M)['msg']
        pg.click('.dci-foot-chip[data-msg=waiting]'); pg.wait_for_timeout(200)
        a_shut = pg.evaluate(M)['msg']
        print('A) 1500:', a, '\n   Meldung:', a_open, a_shut)
        spread = max(a['tops']) - min(a['tops'])
        # ([Z-YELL] 3.110.0) the counters of what is open ("● 1 must", "● 3 can") take the place left: the actions on a second line
        ok_a = a['h'] <= 90 and spread <= 40 and a['sum'] == '24 new relationships · ‹ 1 row incomplete › · 1 already on MB' and 'on recordings' in a['levels'] \
            and a['chips'] == [['2 tracks without a work', '2 tracks have writing credits but no work yet. “Stage” offers to mark them as new works.']] \
            and a_open == ['2 tracks have writing credits but no work yet. “Stage” offers to mark them as new works.'] and a_shut == [] \
            and a['preview'] == 'Preview' and not a['optbtn'] and [x[:2] for x in a['boxes']] == [['fill role credits', True], ['≤ 500 per staging', True]] \
            and a['boxes'][0][2].startswith('add role credits') and a['boxes'][1][2].startswith('at most 500 per staging') \
            and a['infoTitle'].startswith('Nothing is submitted.') and a['stage'][2] < a['info'][0] and a['foot'][2] - a['info'][2] <= 30
        # B) medium
        pg.set_viewport_size({'width': 900, 'height': 1000}); pg.wait_for_timeout(500)
        b1 = pg.evaluate(M)
        note0 = pg.locator('[data-f=fill-credits]').is_checked()
        pg.click('[data-act=foot-opts]'); pg.wait_for_timeout(200)
        lst = pg.evaluate(LIST)
        pg.click('.dci-foot-optlist [data-f=fill-credits]'); pg.wait_for_timeout(200)
        note1 = pg.locator('[data-f=fill-credits]').is_checked()
        still = pg.evaluate(LIST)
        pg.click('.dci-foot [data-el=sum] strong'); pg.wait_for_timeout(200)
        shut1 = pg.evaluate(LIST)
        pg.click('[data-act=foot-opts]'); pg.wait_for_timeout(200)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        shut2, open_dash = pg.evaluate(LIST), pg.evaluate("!document.getElementById('dci-overlay').hidden")
        pg.click('[data-act=foot-opts]'); pg.click('.dci-foot-optlist [data-f=fill-credits]'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        print('B) 900:', b1, '\n   Menü:', lst, '| fill role credits:', note0, '→', note1, '| bleibt:', bool(still), '| Klick daneben:', shut1, '| Esc:', shut2, open_dash)
        ok_b = b1['h'] <= 90 and len(b1['tops']) == 2 and b1['optbtn'] and all(not x[1] for x in b1['boxes']) and lst is not None \
            and lst[3] <= b1['stage'][1] and lst[0] >= b1['panel'][0] and lst[2] <= b1['panel'][2] and note1 is (not note0) and still is not None \
            and shut1 is None and shut2 is None and open_dash
        # C) narrow
        pg.set_viewport_size({'width': 600, 'height': 1000}); pg.wait_for_timeout(500)
        c = pg.evaluate(M)
        print('C) 600:', c)
        ok_c = c['h'] <= 120 and c['stage'][0] >= c['panel'][0] and c['stage'][2] <= c['panel'][2] and c['info'][2] <= c['panel'][2]
        # D) staged (the dashboard stays as narrow as the window was)
        pg.set_viewport_size({'width': 1500, 'height': 1000}); pg.wait_for_timeout(400)
        # [3.38.13] (F-3) the chip of what was staged flashes once: count the chips that come with the class (and their animation)
        pg.evaluate("""(() => { window.__flash = []; new MutationObserver(() => document.querySelectorAll('.dci-foot-chip-flash').forEach(c => {
          if (!c.__seen) { c.__seen = 1; window.__flash.push(getComputedStyle(c).animationName); } })).observe(document.querySelector('.dci-foot'), { childList: true, subtree: true });
          window.__anim = 0; document.addEventListener('animationstart', (e) => { if (e.animationName === 'dci-chip-flash') window.__anim++; }, true); })()""")
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(1500)
        d = pg.evaluate(M)
        done = [x for x in d['chips'] if x[0].startswith('✓')]
        # (clicked: its text below; again: hidden – no second flash)
        pg.click('.dci-foot-chip[data-msg=stage-done]'); pg.wait_for_timeout(300)
        pg.click('.dci-foot-chip[data-msg=stage-done]'); pg.wait_for_timeout(300)
        flash = pg.evaluate('window.__flash')
        pg.wait_for_timeout(1000)
        cls_gone = pg.evaluate("!document.querySelector('.dci-foot-chip-flash')")
        # (the dashboard closed and opened again: the chip is still there, it does not flash again)
        pg.click('.dci-head [data-act=close]'); pg.wait_for_timeout(400)
        pg.click('#dci-open'); pg.wait_for_timeout(1500)
        again = pg.evaluate("[!document.getElementById('dci-overlay').hidden, !!document.querySelector('.dci-foot-chip[data-msg=stage-done]'), window.__anim]")
        print('D) gestagt:', d['chips'], '| Höhe:', d['h'], d['tops'], '| aufgeblinkt:', flash, '| Klasse weg:', cls_gone, '| wieder geöffnet [offen, Chip, animationstart]:', again)
        ok_d = len(done) == 1 and ' in the editor (' in done[0][0] and done[0][1].startswith('✓ ') and done[0][1].endswith('Check them there and click “Enter edit”.') and d['h'] <= 120 \
            and flash == ['dci-chip-flash'] and cls_gone and again == [True, True, 1]
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c, '| D)', ok_d)
        results += [ok_a, ok_b, ok_c, ok_d]
        b.close()
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs2 = H.open_mb_edit(ctx, companion=False)
        pg.add_style_tag(content='#dci-log { display: none !important; }')
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-launcher [data-place=page]'); pg.wait_for_timeout(200)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1500)
        pg.evaluate("window.scrollTo(0, document.querySelector('[data-el=companies]').getBoundingClientRect().top + window.scrollY - 200)")
        pg.wait_for_timeout(300)
        e = pg.evaluate(M)
        bottom = pg.evaluate("Math.round(window.innerHeight - document.querySelector('.dci-foot').getBoundingClientRect().bottom)")
        print('E) in der Seite:', e['h'], e['tops'], '| Abstand unten:', bottom)
        ok_e = e['h'] <= 60 and max(e['tops']) - min(e['tops']) <= 6 and bottom == 0
        print('E)', ok_e)
        results.append(ok_e)
        print('Fehler:', errs, errs2)
        results.append(not errs and not errs2)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_addrolebtn():
    """Credits Importer 3.40.13 (collected item Z-AB; Q-bs): "＋ Another role for …" a button in the full view too (until 3.40.12 a
    link "+ Another role for …" there; a button in the compact entries from 3.40.10).
    A) Full view: below the rows of Bass Man the button "＋ Another role for Bass Man" (framed, not a text link); (3.73.0, Z-ARL)
       "＋ Another role", the name in its tooltip ("+ Another role for Bass Man").
    B) Clicked: a new row for him."""
    BTN = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong') && s.querySelector('.dci-gname strong').textContent === 'Bass Man');
      const x = g && g.querySelector(':scope > [data-act=add-role]'); if (!x) return null; const st = getComputedStyle(x);
      return [x.textContent.trim(), x.classList.contains('dci-addrole-btn'), x.classList.contains('dci-textbtn'), st.borderTopStyle, g.querySelectorAll('tr.dci-row').length]; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1000)
        a0 = pg.evaluate(BTN)
        print('A)', a0)
        # ([Z-ARL] 3.73.0) "＋ Another role" without the name, the name in its tooltip
        a0t = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong') && s.querySelector('.dci-gname strong').textContent === 'Bass Man');
          const b = g && g.querySelector(':scope > [data-act=add-role]'); return b ? b.title : null; })()""")
        print('   Tooltip:', a0t)
        results.append(a0 is not None and a0[:4] == ['＋ Another role', True, False, 'solid'] and a0t == '+ Another role for Bass Man')
        pg.click('section.dci-group:has(.dci-gname strong:text-is("Bass Man")) > [data-act=add-role]')
        pg.click('[data-el=arq] [data-act=arq-free]')  # ([Z-ARQ] 3.86.0) the role typed by hand
        pg.wait_for_timeout(300)
        b0 = pg.evaluate(BTN)
        print('B)', b0)
        results.append(b0 is not None and a0 is not None and b0[4] == a0[4] + 1)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_entryskip():
    """Credits Importer 3.40.15 (collected item Z-SK; Q-bx, Q-ce): "⊘ Skip" in the head of each entry.
    A) Full view: every entry has "⊘ Skip" at the right of its head (also a writer, whose rows are in the works matrix). Bass Man: a
       click – his row on "Skip", the entry grey, "↺ Take again" instead (focused), fewer new relationships, the log says so.
    B) Bob Producer's row on "Release" by hand, then "⊘ Skip" and "↺ Take again": "Release" again (the level he had), the summary as before.
    C) Bass Man skipped, then a level chosen for his row ("Recording"): no longer skipped – not grey, "⊘ Skip" again.
    D) ⚙ Settings → Appearance → "Remove skipped entries from the dashboard" (off; on: stored): Bass Man skipped – not in the list;
       at the bottom "1 skipped entry ▸"; ▸ lists him with "↺ Take again"; clicked: he is back in his place, the line gone.
    E) Entries as a matrix, compact: "⊘ Skip" in the head beside "by event | by role"; clicked: the entry grey, its lines'
       rows on "Skip"."""
    SEC = "section.dci-group:has(.dci-gname strong:text-is(\"{}\"))"
    INFO = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong') && s.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; const b = g.querySelector('.dci-ghead-r .dci-gskip'); const head = g.querySelector('.dci-ghead').getBoundingClientRect();
      return { btn: b ? b.textContent.trim() : null, act: b ? b.dataset.act : null, grey: g.classList.contains('dci-gskipped'), focus: document.activeElement === b,
        right: b ? Math.round(head.right - b.getBoundingClientRect().right) : null,
        levels: [...g.querySelectorAll('tr.dci-row')].map(tr => (tr.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level),
        op: b ? getComputedStyle(g.querySelector('.dci-gname')).opacity : null }; }"""
    SUM = "(document.querySelector('.dci-foot [data-el=sum] strong') || {textContent: ''}).textContent.trim()"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        counts = pg.evaluate("""[[...document.querySelectorAll('section.dci-group')].length,
          [...document.querySelectorAll('section.dci-group .dci-ghead-r [data-act=entry-skip]')].length]""")
        sum0 = pg.evaluate(SUM)
        a0 = pg.evaluate(INFO, 'Bass Man')
        pg.click(SEC.format('Bass Man') + ' [data-act=entry-skip]')
        pg.wait_for_timeout(400)
        a1 = pg.evaluate(INFO, 'Bass Man')
        sum1 = pg.evaluate(SUM)
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'skipped:' in x]
        print('A) Köpfe/Knöpfe:', counts, '| vorher:', a0, sum0, '\n   ⊘:', a1, sum1, logs)
        results.append(counts[0] == counts[1] and counts[0] > 3 and a0['btn'] == '⊘ Skip' and a0['right'] < 40 and a0['levels'] == ['recording']
                       and a1['btn'] == '↺ Take again' and a1['grey'] and a1['focus'] and a1['levels'] == ['skip'] and float(a1['op']) < 0.6
                       and int(sum1.split()[0]) < int(sum0.split()[0]) and logs == ['Bass Man skipped: 1 row on “Skip”'])
        pg.click(SEC.format('Bass Man') + ' [data-act=entry-unskip]')
        pg.wait_for_timeout(400)
        # B)
        pg.click(SEC.format('Bob Producer') + ' tr.dci-row [data-act=level][data-level=release]')
        pg.wait_for_timeout(300)
        sumb = pg.evaluate(SUM)
        pg.click(SEC.format('Bob Producer') + ' [data-act=entry-skip]')
        pg.wait_for_timeout(300)
        b1 = pg.evaluate(INFO, 'Bob Producer')
        pg.click(SEC.format('Bob Producer') + ' [data-act=entry-unskip]')
        pg.wait_for_timeout(300)
        b2 = [pg.evaluate(INFO, 'Bob Producer'), pg.evaluate(INFO, 'Bass Man'), pg.evaluate(SUM)]
        print('B) ⊘:', b1, '| ↺:', b2, sumb)
        results.append(b1['levels'] == ['skip'] and b2[0]['levels'] == ['release'] and not b2[0]['grey'] and b2[0]['btn'] == '⊘ Skip'
                       and b2[1]['levels'] == ['recording'] and b2[2] == sumb)
        # C)
        pg.click(SEC.format('Bass Man') + ' [data-act=entry-skip]')
        pg.wait_for_timeout(300)
        pg.click(SEC.format('Bass Man') + ' tr.dci-row [data-act=level][data-level=recording]')
        pg.wait_for_timeout(300)
        c0 = pg.evaluate(INFO, 'Bass Man')
        print('C)', c0)
        results.append(c0['levels'] == ['recording'] and not c0['grey'] and c0['btn'] == '⊘ Skip')
        # D)
        H.open_settings(pg, 'appearance')
        box = pg.locator('[data-el=settings] [data-set=skip-hide]')
        d0 = [box.is_checked(), box.evaluate("b => b.closest('label').textContent.trim()")]
        box.check()
        pg.wait_for_timeout(300)
        stored = pg.evaluate("localStorage.getItem('dci-skip-hide')")
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
        pg.wait_for_timeout(200)
        pg.click(SEC.format('Bass Man') + ' [data-act=entry-skip]')
        pg.wait_for_timeout(400)
        LINE = "(el => el && !el.hidden ? [el.querySelector('.dci-skipped-toggle').textContent.trim(), [...el.querySelectorAll('li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim())] : null)(document.querySelector('[data-el=skipped]'))"
        d1 = [pg.evaluate(INFO, 'Bass Man'), pg.evaluate(LINE), pg.evaluate("document.activeElement && document.activeElement.className")]
        pg.click('[data-el=skipped] [data-act=skipped-toggle]')
        pg.wait_for_timeout(200)
        d2 = pg.evaluate(LINE)
        pg.click('[data-el=skipped] [data-act=entry-unskip]')
        pg.wait_for_timeout(400)
        d3 = [pg.evaluate(INFO, 'Bass Man'), pg.evaluate(LINE)]
        print('D) Box:', d0, stored, '| ⊘:', d1, '| ▸:', d2, '| ↺:', d3)
        results.append(d0 == [False, 'Remove skipped entries from the dashboard'] and stored == 'true' and d1[0] is None and d1[1] == ['1 skipped entry ▸', []]
                       and 'dci-skipped-toggle' in (d1[2] or '') and d2 == ['1 skipped entry ▾', ['ArtistBass Man ↺ Take again']]
                       and d3[0] is not None and d3[0]['levels'] == ['recording'] and d3[1] is None)
        # E) as a matrix, compact
        H.open_settings(pg, 'appearance')
        pg.click('[data-el=settings] [data-act=entries-view][data-view=matrix]')
        pg.wait_for_timeout(300)
        pg.locator('[data-el=settings] [data-set=skip-hide]').uncheck()
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
        pg.wait_for_timeout(200)
        if pg.evaluate("!document.getElementById('dci-overlay').classList.contains('dci-compact')"):
            pg.locator('.dci-head [data-act=view-toggle]').evaluate('b => b.click()')
            pg.wait_for_timeout(400)
        ES = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong') && s.querySelector('.dci-gname strong').textContent.trim() === name);
          if (!g) return null; const r = g.querySelector('.dci-ghead-r'); return { centry: g.classList.contains('dci-em-centry'), parts: r ? [...r.children].map(x => x.className.split(' ')[0] === 'dci-seg' ? 'seg' : x.textContent.trim()) : null,
            grey: g.classList.contains('dci-gskipped') }; }"""
        e0 = pg.evaluate(ES, 'Guitar Guy')
        pg.click(SEC.format('Guitar Guy') + ' [data-act=entry-skip]')
        pg.wait_for_timeout(400)
        e1 = [pg.evaluate(ES, 'Guitar Guy'), pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(x => x.textContent).filter(t => /Guitar Guy skipped/.test(t)).length")]
        print('E)', e0, e1)
        results.append(e0 is not None and e0['centry'] and e0['parts'] == ['seg', '⊘ Skip'] and e1[0]['grey'] and e1[0]['parts'] == ['seg', '↺ Take again'] and e1[1] == 1)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_entryskipkeep():
    """Credits Importer 3.40.15 (collected item Z-SK): an entry skipped is remembered with the release (⚙ Settings → Cache on):
    loaded again, Bass Man is still skipped (grey, "↺ Take again"), and "↺ Take again" brings his row back on "Recording"."""
    H.REMEMBER = True
    INFO = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong') && s.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; const b = g.querySelector('.dci-ghead-r .dci-gskip');
      return [b ? b.textContent.trim() : null, g.classList.contains('dci-gskipped'), [...g.querySelectorAll('tr.dci-row')].map(tr => (tr.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level)]; }"""
    SEC = 'section.dci-group:has(.dci-gname strong:text-is("Bass Man"))'
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
            pg.wait_for_timeout(1200)
        load()
        pg.click(SEC + ' [data-act=entry-skip]')
        pg.wait_for_timeout(1600)
        pg.reload(); pg.add_script_tag(content=H.MAIN)
        load()
        a0 = pg.evaluate(INFO, 'Bass Man')
        pg.click(SEC + ' [data-act=entry-unskip]')
        pg.wait_for_timeout(400)
        a1 = pg.evaluate(INFO, 'Bass Man')
        print('neu geladen:', a0, '| ↺:', a1)
        results.append(a0 == ['↺ Take again', True, ['skip']] and a1 == ['⊘ Skip', False, ['recording']])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_entryskipmodes():
    """Credits Importer 3.40.17 (the check of Block BC): "⊘ Skip" of an entry with the other ways of skipping.
    A) "Stage: only work relationships", then Bass Man "⊘ Skip", then "all relationships": he stays skipped (until 3.40.16 his row
       came back); "↺ Take again": "Recording".
    B) Bass Man skipped, "only work relationships", "↺ Take again": his row stays on "Skip" (it is no work relationship); "all
       relationships": "Recording".
    C) Bass Man skipped, "Level for all rows: Recording", then "Skip": "⊘ Skip" in his head, not "↺ Take again" (until 3.40.16 the
       skip of before came back with it)."""
    INFO = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong') && s.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; const b = g.querySelector('.dci-ghead-r .dci-gskip');
      return [b ? b.dataset.act : null, g.classList.contains('dci-gskipped'), [...g.querySelectorAll('tr.dci-row')].map(tr => (tr.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level)]; }"""
    SEC = 'section.dci-group:has(.dci-gname strong:text-is("Bass Man"))'
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        scope = lambda v: (pg.click(f'[data-act=scope][data-scope={v}]'), pg.wait_for_timeout(400))
        # A)
        scope('work')
        pg.click(SEC + ' [data-act=entry-skip]'); pg.wait_for_timeout(300)
        scope('all')
        a0 = pg.evaluate(INFO, 'Bass Man')
        pg.click(SEC + ' [data-act=entry-unskip]'); pg.wait_for_timeout(300)
        a1 = pg.evaluate(INFO, 'Bass Man')
        print('A) Bereich wieder alle:', a0, '| ↺:', a1)
        results.append(a0 == ['entry-unskip', True, ['skip']] and a1 == ['entry-skip', False, ['recording']])
        # B)
        pg.click(SEC + ' [data-act=entry-skip]'); pg.wait_for_timeout(300)
        scope('work')
        pg.click(SEC + ' [data-act=entry-unskip]'); pg.wait_for_timeout(300)
        b0 = pg.evaluate(INFO, 'Bass Man')
        scope('all')
        b1 = pg.evaluate(INFO, 'Bass Man')
        print('B) ↺ im Bereich „work“:', b0, '| alle:', b1)
        results.append(b0 is not None and b0[2] == ['skip'] and not b0[1] and b1 == ['entry-skip', False, ['recording']])
        # C)
        pg.click(SEC + ' [data-act=entry-skip]'); pg.wait_for_timeout(300)
        pg.click('[data-act=bulk-level][data-level=recording]'); pg.wait_for_timeout(400)
        pg.click('[data-act=bulk-level][data-level=skip]'); pg.wait_for_timeout(400)
        c0 = pg.evaluate(INFO, 'Bass Man')
        print('C) alle Recording, dann Skip:', c0)
        results.append(c0 == ['entry-skip', False, ['skip']])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_footbar():
    """Credits Importer 3.41.10 (collected item Z-SB2; the user's screenshot of 2026-11-03): the scroll bars of the page never cover
    the dashboard window. The page wider and longer than the browser window (both scroll bars, 1500 × 1000 px):
    A) The dashboard as it was left at the bottom edge (y 200, height 800): it ends above the horizontal scroll bar and left of the
       vertical one – its footer ("Stage in the relationship editor", ⓘ) wholly visible (until 3.41.9 the window counted the scroll
       bars: 15 px of the footer under the bar).
    B) The page becomes wider only later (the dashboard open, no "resize"): the window is moved into view again."""
    results = []
    VIEW = "[document.documentElement.clientWidth, document.documentElement.clientHeight, window.innerWidth, window.innerHeight]"
    BOX = """(() => { const r = (e) => { const x = e.getBoundingClientRect(); return [Math.round(x.left), Math.round(x.top), Math.round(x.right), Math.round(x.bottom)]; };
      return { panel: r(document.querySelector('.dci-panel')), foot: r(document.querySelector('.dci-foot')), stage: r(document.querySelector('.dci-foot [data-act=apply]')),
        info: r(document.querySelector('.dci-foot-info')) }; })()"""
    # (scroll bars as on Windows, that take room: a browser of its own without "--hide-scrollbars")
    b = launch_own(args=list(H.LAUNCH_ARGS), ignore_default_args=['--hide-scrollbars'])
    try:
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.evaluate("localStorage.setItem('dci-geom:panel', JSON.stringify({ x: 100, y: 200, w: 1400, h: 800 }))")
        # the page wider and longer than the window: both scroll bars
        pg.evaluate("(() => { const d = document.createElement('div'); d.id = 'wide'; d.style.cssText = 'width: 2600px; height: 3000px'; document.body.appendChild(d); })()")
        pg.wait_for_timeout(200)
        v0 = pg.evaluate(VIEW)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        a0 = pg.evaluate(BOX)
        print('A) Fenster ohne / mit Bildlaufleisten:', v0, '| Dashboard:', a0)
        results.append(v0[1] < v0[3] and v0[0] < v0[2] and a0['panel'][3] <= v0[1] and a0['foot'][3] <= v0[1] and a0['stage'][3] <= v0[1]
                       and a0['panel'][2] <= v0[0] and a0['info'][2] <= v0[0])
        # B) the page made narrow again, the window put at the bottom, then the page wider (no resize event)
        pg.evaluate("document.getElementById('wide').style.width = '100px'"); pg.wait_for_timeout(300)
        v1 = pg.evaluate(VIEW)
        pg.evaluate("(() => { const p = document.querySelector('.dci-panel'); p.style.top = `${document.documentElement.clientHeight - p.offsetHeight}px`; })()")
        pg.wait_for_timeout(100)
        b0 = pg.evaluate(BOX)
        pg.evaluate("document.getElementById('wide').style.width = '2600px'"); pg.wait_for_timeout(500)
        v2 = pg.evaluate(VIEW)
        b1 = pg.evaluate(BOX)
        print('B) ohne Leiste:', v1, b0['panel'], '| mit Leiste:', v2, b1['panel'], b1['foot'])
        results.append(v1[1] > v2[1] and b0['panel'][3] == v1[1] and b1['panel'][3] <= v2[1] and b1['foot'][3] <= v2[1])
        print('Fehler:', errs)
        results.append(not errs)
    finally:
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


# --- [3.72.0] the cases of the former t_ui_place.py (collected item Z-TST) ----------------------------------------


def case_inline():
    """The dashboard in the page instead of a window: switched in the page bar before opening, placed below the
    import button, the page scrolls with it (dates block and footer stay in view), switched back in ⚙ Settings → General
    (3.26.0; before: in the dashboard header), remembered after a reload, back to the window with "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults")."""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        seg = pg.locator('#dci-launcher .dci-place-seg button')
        print('Schalter in der Seitenleiste:', seg.all_inner_texts(), [seg.nth(i).get_attribute('aria-pressed') for i in range(2)])
        pg.click('#dci-launcher [data-place=page]')
        pg.wait_for_timeout(200)
        # 3.5.1: the switch shows the choice at once, before the dashboard was opened
        pressed0 = [seg.nth(i).get_attribute('aria-pressed') for i in range(2)]
        print('0) Schalter nach dem Klick (Dashboard noch zu):', pressed0)
        H.open_dashboard(pg)
        pg.wait_for_timeout(400)
        where = pg.evaluate("""(() => { const o = document.getElementById('dci-overlay'); const panel = o.querySelector('.dci-panel');
      return { afterBar: document.getElementById('dci-pagebar').nextElementSibling === o, inline: o.classList.contains('dci-inline'),
        position: getComputedStyle(panel).position, bodyOverflow: getComputedStyle(o.querySelector('.dci-body')).overflowY }; })()""")
        print('1) in der Seite:', where)
        ok1 = where['afterBar'] and where['inline'] and where['position'] == 'relative' and where['bodyOverflow'] == 'visible' and pressed0 == ['false', 'true']
        # 2) the page scrolls; the dates block ([3.18.0] with the line "Add entry manually") sticks to the top, the footer to the bottom
        pg.evaluate("window.scrollTo(0, document.querySelector('[data-el=companies]').getBoundingClientRect().top + window.scrollY - 200)")
        pg.wait_for_timeout(300)
        pos = pg.evaluate("""(() => ({ y: Math.round(window.scrollY), dates: Math.round(document.querySelector('[data-el=stick]').getBoundingClientRect().top),
      foot: Math.round(window.innerHeight - document.querySelector('.dci-foot').getBoundingClientRect().bottom) }))()""")
        print('2) gescrollt:', pos)
        ok2 = pos['y'] > 300 and pos['dates'] == 0 and pos['foot'] == 0
        # 3) dragging the head moves nothing
        box = pg.locator('.dci-head h2').bounding_box()
        pg.mouse.move(box['x'] + 5, box['y'] + 5); pg.mouse.down(); pg.mouse.move(box['x'] + 200, box['y'] + 100); pg.mouse.up()
        style = pg.evaluate("document.querySelector('.dci-panel').getAttribute('style') || ''")
        print('3) Kopf gezogen → Stil:', repr(style))
        ok3 = 'left' not in style
        # 4) back to a window – [3.26.0] in ⚙ Settings → General (the head has no switch any more); remembered
        H.open_settings(pg, 'appearance')  # [3.29.2] the place is under "Appearance" now
        pg.click('[data-el=settings] [data-act=place-toggle]'); pg.wait_for_timeout(300)
        back = pg.evaluate("""(() => { const o = document.getElementById('dci-overlay'); return { parent: o.parentNode === document.body,
      position: getComputedStyle(o.querySelector('.dci-panel')).position, stored: localStorage.getItem('dci-place') }; })()""")
        print('4) zurück als Fenster:', back)
        ok4 = back['parent'] and back['position'] == 'fixed' and back['stored'] is None
        pg.click('[data-el=settings] [data-act=place-toggle]'); pg.wait_for_timeout(200)
        pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000)
        pressed = pg.locator('#dci-launcher [data-place=page]').get_attribute('aria-pressed')
        pg.click('#dci-open'); pg.wait_for_selector('.dci-inline .dci-pools-head', timeout=30000)
        print('5) nach Neuladen: in der Seite gedrückt', pressed, '| Dashboard in der Seite:', pg.locator('#dci-overlay.dci-inline').count())
        ok5 = pressed == 'true' and pg.locator('#dci-overlay.dci-inline').count() == 1
        # 6) "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults"): window again
        H.open_reset(pg); pg.click('[data-act=reset-do]'); pg.wait_for_timeout(500)
        print('6) nach ↺ Standard: Fenster', pg.locator('#dci-overlay.dci-inline').count() == 0, '| Seitenleiste:', pg.locator('#dci-launcher [data-place=window]').get_attribute('aria-pressed'))
        ok6 = pg.locator('#dci-overlay.dci-inline').count() == 0 and pg.locator('#dci-launcher [data-place=window]').get_attribute('aria-pressed') == 'true'
        print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4, ok5, ok6]) else 'FEHLER', [ok1, ok2, ok3, ok4, ok5, ok6], '| Fehler:', errs)
        b.close()


def case_logplace():
    """Log placement ("Place:" in the log's head): beside the edit note (right / left: the edit note keeps its place and
    gets the rest of its width, the log takes its height and follows it), above it (full width, the dragged height is
    remembered) or its own window again. Too narrow beside it → above, with a hint; MusicBrainz drawing the edit note
    anew → the log follows; the place is remembered after reloading; "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults") → window."""
    H.MAIN = H.MAIN_SLOW  # [3.31.1] the time matters here: the script's own gap between requests to MusicBrainz
    # MusicBrainz's edit note is as wide as the form
    CSS = '#edit-note-text { width: 100%; height: 90px; box-sizing: border-box; }'
    GEOM = """(() => { const r = (el) => { const b = el.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height)]; };
  const log = document.getElementById('dci-log'); const note = document.getElementById('edit-note-text');
  return { log: r(log), note: r(note), cls: log.className, parent: log.parentElement.id || log.parentElement.tagName, before: note.previousElementSibling === log,
    pos: getComputedStyle(log).position, float: getComputedStyle(log).cssFloat, clear: !!document.getElementById('dci-log-clear'),
    noteW: note.style.width, stored: localStorage.getItem('dci-log-place') }; })()"""
    results = []


    def place(pg, value):
        pg.evaluate(f"""() => {{ const s = document.querySelector('#dci-log [data-log-f=place]'); s.value = '{value}';
      s.dispatchEvent(new Event('change', {{ bubbles: true }})); }}""")
        pg.wait_for_timeout(300)
        return pg.evaluate(GEOM)


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.add_style_tag(content=CSS)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        g0 = pg.evaluate(GEOM)
        opts = pg.locator('#dci-log [data-log-f=place] option').all_inner_texts()
        print('0) Fenster:', g0['pos'], g0['parent'], '| Auswahl:', opts)
        ok0 = g0['pos'] == 'fixed' and g0['parent'] == 'BODY' and opts == ['window', 'left of edit note', 'right of edit note', 'above edit note']

        # A) right of the edit note
        g = place(pg, 'right')
        print('A1) rechts:', g)
        ok_a = g['before'] and 'dci-log-dock-right' in g['cls'] and g['float'] == 'right' and g['pos'] == 'relative' and g['clear'] \
            and g['note'][0] + g['note'][2] <= g['log'][0] and abs(g['note'][1] - g['log'][1]) <= 2 and g['log'][3] == 140 and g['stored'] == '"right"'
        pg.evaluate("document.getElementById('edit-note-text').style.height = '260px'"); pg.wait_for_timeout(300)
        g2 = pg.evaluate(GEOM)
        print('A2) Bearbeitungsnotiz höher gezogen → Protokoll:', g2['log'][3], '| Notiz:', g2['note'][3])
        ok_a = ok_a and abs(g2['log'][3] - g2['note'][3]) <= 1
        log_txt = pg.locator('#dci-log li').last.inner_text()
        print('A3) Protokoll:', log_txt)
        ok_a = ok_a and 'Log shown: right of edit note' in log_txt
        results.append(ok0 and ok_a)

        # B) left, then above, then the window again
        g = place(pg, 'left')
        print('B1) links:', g['log'], g['note'], g['float'])
        ok_b = g['float'] == 'left' and g['log'][0] + g['log'][2] <= g['note'][0] and abs(g['note'][1] - g['log'][1]) <= 2
        g = place(pg, 'above')
        print('B2) darüber:', g['log'], g['note'], '| Breite Notiz:', repr(g['noteW']), '| clear:', g['clear'])
        ok_b = ok_b and g['before'] and g['float'] == 'none' and g['log'][1] + g['log'][3] <= g['note'][1] and abs(g['log'][2] - g['note'][2]) <= 1 \
            and g['noteW'] == '' and not g['clear'] and g['log'][3] == 180
        # the dragged height above the edit note is remembered
        pg.evaluate("document.getElementById('dci-log').style.height = '230px'"); pg.wait_for_timeout(800)
        stored_h = pg.evaluate("localStorage.getItem('dci-log-dock-h')")
        print('B3) Höhe gezogen → gespeichert:', stored_h)
        ok_b = ok_b and stored_h == '230'
        g = place(pg, 'window')
        print('B4) Fenster:', g['pos'], g['parent'], '| Breite Notiz:', repr(g['noteW']), '| gespeichert:', g['stored'])
        ok_b = ok_b and g['pos'] == 'fixed' and g['parent'] == 'BODY' and g['noteW'] == '' and g['stored'] is None
        results.append(ok_b)

        # C) too narrow beside it → above (hint); wider again → right; MB draws the edit note anew → the log follows
        place(pg, 'right')
        # ([3.78.0] Z-LOG) beside it from 300 + 240 px (and the gap) on: narrower than that
        pg.set_viewport_size({'width': 500, 'height': 900}); pg.wait_for_timeout(500)
        g = pg.evaluate(GEOM)
        hint = pg.evaluate("[document.querySelector('#dci-log [data-log-f=place]').title, document.querySelector('#dci-log [data-log-f=place]').className, document.querySelector('#dci-log [data-log-f=place]').value]")
        print('C1) schmal:', g['cls'], '| Hinweis:', hint)
        ok_c = 'dci-log-dock-above' in g['cls'] and 'Not enough room' in hint[0] and 'dci-log-place-off' in hint[1] and hint[2] == 'right' and g['noteW'] == ''
        pg.set_viewport_size({'width': 1500, 'height': 1000}); pg.wait_for_timeout(500)
        g = pg.evaluate(GEOM)
        print('C2) wieder breit:', g['cls'])
        ok_c = ok_c and 'dci-log-dock-right' in g['cls']
        pg.evaluate("""() => { const old = document.getElementById('edit-note-text'); const n = document.createElement('textarea');
      n.id = 'edit-note-text'; n.value = old.value; document.getElementById('content').appendChild(n); old.remove(); }""")
        pg.wait_for_timeout(400)
        g = pg.evaluate(GEOM)
        print('C3) Notiz neu gezeichnet → Protokoll davor:', g['before'], g['cls'])
        ok_c = ok_c and g['before'] and 'dci-log-dock-right' in g['cls']
        results.append(ok_c)

        # D) remembered after reloading; "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults") → window
        pg.reload()
        pg.add_style_tag(content=CSS)
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        g = pg.evaluate(GEOM)
        print('D1) nach Neuladen:', g['cls'], g['before'])
        ok_d = 'dci-log-dock-right' in g['cls'] and g['before']
        H.open_reset(pg); pg.wait_for_timeout(200)
        pg.click('[data-act=reset-do]'); pg.wait_for_timeout(600)
        g = pg.evaluate(GEOM)
        print('D2) Standard:', g['pos'], g['parent'], g['stored'], '| Breite Notiz:', repr(g['noteW']))
        ok_d = ok_d and g['pos'] == 'fixed' and g['parent'] == 'BODY' and g['stored'] is None and g['noteW'] == ''
        results.append(ok_d)
        print('Fehler:', errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_keepplace():
    """After creating an entry through MusicBrainz's form ("Create artist …"), the dashboard stays where it was: the
    entry you came from keeps its place on the screen, although a message is added at the top and the dashboard is
    redrawn (window and page). Scroll anchoring is switched off, as in browsers without it (Safari) and where the
    entry itself is drawn anew."""
    orig = H.discogs_release
    NEW = H.uid('dddddddd', 77)


    def rel():
        d = orig()
        d['extraartists'] += [{'name': 'Nobody Known', 'anv': '', 'role': 'Vocals', 'tracks': '', 'id': 3999, 'join': ''}]
        return d


    H.discogs_release = rel
    results = []


    NO_ANCHOR = '* { overflow-anchor: none !important; }'


    def run(pg, inpage):
        pg.add_style_tag(content=NO_ANCHOR)
        key = pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(g => g.querySelector('.dci-gname strong').textContent === 'Nobody Known').dataset.group")
        sel = f'section.dci-group[data-group="{key}"]'
        # the entry in the middle of the screen
        pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{ block: 'center' }})")
        pg.wait_for_timeout(300)
        # 3.9.0: the button scrolled into view first (the click would scroll it), then the place is measured
        pg.locator(f'{sel} [data-act=artist-create]').scroll_into_view_if_needed()
        pg.wait_for_timeout(200)
        top0 = pg.evaluate(f"document.querySelector('{sel}').getBoundingClientRect().top")
        msgs0 = pg.locator('[data-el=msgs] > *').count()
        pg.click(f'{sel} [data-act=artist-create]')
        pg.wait_for_selector('[data-el=sub]:not([hidden])', timeout=20000)
        pg.wait_for_timeout(300)
        # the form was submitted: MusicBrainz shows the new artist
        pg.evaluate(f"document.querySelector('[data-el=sub-frame]').src = 'https://musicbrainz.org/artist/{NEW}'")
        pg.wait_for_timeout(2600)
        top1 = pg.evaluate(f"document.querySelector('{sel}').getBoundingClientRect().top")
        msgs1 = pg.locator('[data-el=msgs] > *').count()
        status = pg.evaluate(f"document.querySelector('{sel}').className")
        print(('In der Seite' if inpage else 'Fenster') + ':', 'Eintrag oben vorher', round(top0), '| nachher', round(top1), '| Nachrichten', msgs0, '→', msgs1, '|', status)
        return abs(top1 - top0) <= 3 and msgs1 > msgs0 and 'dci-st-created' in status


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        results.append(run(pg, False))
        # in the page
        pg2, errs2 = H.open_mb_edit(ctx, companion=False)
        # (3.43.2) the artist created in the window comes back with the release ("Remember changes …"): forgotten here, so the page
        # starts with "Create artist …" again
        pg2.evaluate(f"localStorage.setItem('dci-place', JSON.stringify('page')); localStorage.removeItem('dci-remember:{H.REL}')")
        pg2.reload()
        pg2.add_script_tag(content=H.MAIN)
        pg2.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg2)
        pg2.wait_for_timeout(500)
        results.append(run(pg2, True))
        print('Fehler:', errs, errs2)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_srctexts():
    """Import 3.16.2: texts that named Discogs say "the source" when another source is loaded (as "Mapping rules" in 3.13.2).
    A) Discogs loaded: the question for "Guitar" says "Discogs only says “Guitar”", a role credit taken over is tagged "from
       Discogs"; the placeholder of "Add entry manually" says "a role as the source writes it" (for any source).
    B) A pasted text loaded: "The source (pasted text) only says “Guitar”", the tag "from the source" (tooltip "Taken from
       the source (pasted text)"), and a track without writers says "The source (pasted text) names no writers for this
       track"."""
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    TEXTS = """(() => ({ ask: [...document.querySelectorAll('.dci-bass-ask')].map(x => x.textContent.replace(/\\s+/g, ' ').trim().slice(0, 60)),
  ph: (document.querySelector('[data-f=manual-role]') || {}).placeholder || '',
  tag: [...document.querySelectorAll('.dci-credit-name .dci-src')].map(x => [x.textContent.trim(), x.title]),
  writers: [...document.querySelectorAll('tr[data-work] .dci-info')].map(x => x.title) }))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Checks complete/.test(x))", 90)
        pg.wait_for_timeout(500)
        a = pg.evaluate(TEXTS)
        print('A) Discogs:', a['ask'][:1], '|', a['ph'], '|', a['tag'][:1])
        results.append(any(x.startswith('Discogs only says “Guitar”') for x in a['ask']) and 'a role as the source writes it' in a['ph']
                       and a['tag'] and a['tag'][0] == ['from Discogs', 'Taken from Discogs'])
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Guitar – John Smith\nLayout by Jane Roe')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, f"{LOGS}.filter(x => /Checks complete/.test(x)).length >= 2", 90)
        pg.wait_for_timeout(500)
        t = pg.evaluate(TEXTS)
        print('B) Text:', t['ask'][:1], '|', t['ph'], '|', t['tag'][:1], '|', t['writers'][:1])
        results.append(any(x.startswith('The source (pasted text) only says “Guitar”') for x in t['ask'])
                       and t['tag'] and t['tag'][0] == ['from the source', 'Taken from the source (pasted text)']
                       and any(w.startswith('The source (pasted text) names no writers for this track') for w in t['writers']))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_lognarrow():
    """Credits Importer 3.78.0 (collected item Z-LOG): the log beside a narrow edit note.
    A) An edit note 600 px wide (MusicBrainz's is narrower than the window): "left of edit note" puts the log beside it (until 3.77
       it went above it below 640 px); the edit note keeps at least 300 px, the log at least 240.
    B) The edit note dragged to 320 px beside the log: remembered (dci-log-note-w), the log takes the rest.
    C) The log back in its window: the edit note gets its own width again; "right of edit note" again: 320 px, as dragged.
    D) An edit note of 500 px: too narrow for both (300 + 240 + the gap) – the log goes above it, with the hint."""
    CSS = '#edit-note-text { width: 600px; height: 90px; box-sizing: border-box; }'
    GEOM = """(() => { const log = document.getElementById('dci-log'); const note = document.getElementById('edit-note-text');
  const r = (el) => Math.round(el.getBoundingClientRect().width);
  return { cls: log.className.replace('dci-window', '').trim(), log: r(log), note: r(note), noteW: note.style.width, kept: localStorage.getItem('dci-log-note-w') }; })()"""
    results = []

    def place(pg, value):
        pg.evaluate(f"""() => {{ const s = document.querySelector('#dci-log [data-log-f=place]'); s.value = '{value}';
      s.dispatchEvent(new Event('change', {{ bubbles: true }})); }}""")
        pg.wait_for_timeout(300)
        return pg.evaluate(GEOM)

    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.add_style_tag(content=CSS)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        a = place(pg, 'left')
        print('A) links, Notiz 600 px:', a)
        results.append('dci-log-dock-left' in a['cls'] and a['note'] >= 300 and a['log'] >= 240 and a['note'] + a['log'] <= 600)
        pg.evaluate("document.getElementById('edit-note-text').style.width = '320px'")
        H.wait_ok(pg, "localStorage.getItem('dci-log-note-w') === '320'", 5)
        pg.wait_for_timeout(200)
        g = pg.evaluate(GEOM)
        print('B) Notiz auf 320 px gezogen:', g)
        results.append(g['kept'] == '320' and g['note'] == 320 and g['log'] >= 240 and g['log'] > a['log'])
        c1 = place(pg, 'window')
        c2 = place(pg, 'right')
        print('C) Fenster:', c1, '| rechts wieder:', c2)
        results.append(c1['note'] == 600 and c1['noteW'] == '' and 'dci-log-dock-right' in c2['cls'] and c2['note'] == 320)
        pg.evaluate("localStorage.removeItem('dci-log-note-w')")
        place(pg, 'window')
        pg.add_style_tag(content='#edit-note-text { width: 500px !important; }')
        d = place(pg, 'left')
        hint = pg.evaluate("document.querySelector('#dci-log [data-log-f=place]').title")
        print('D) 500 px:', d, '| Hinweis:', hint[:60], '| Fehler:', errs)
        results.append('dci-log-dock-above' in d['cls'] and 'Not enough room' in hint and not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_mbsearch3123():
    """Credits Importer 3.123.0 (collected item Z-MBSEARCH, S193): "Design by Jane Nine", pasted; MusicBrainz has five artists "Jane Nine"
    and a label "Jane Nine Design".
    A) "Jane Nine" typed into the entry's field, Enter: MusicBrainz's artists of that name – 3 shown, "+ 2 more" shows the others (until
       3.122.0 "not an MBID").
    B) The kind "label" before the field: the entry a label, its row "design" on the release; the label searched in the field and
       chosen: linked to it.
    C) Linked, "Change", the kind "artist": a question (accepted) – the link let go, the entry an artist again with its row as before.
    D) Settings: 1 hit at first – a search shows one and "+ 1 more"."""
    IDS = [H.uid('dddddddd', 3123 + k) for k in range(5)]
    LAB = H.uid('eeeeeeee', 3123)
    H.MB_SEARCH['artist'] = [{'id': g, 'name': 'Jane Nine', 'disambiguation': f'designer no. {k + 1}', 'score': 100} for k, g in enumerate(IDS)]
    H.MB_SEARCH['label'] = [{'id': LAB, 'name': 'Jane Nine Design', 'type': 'Production', 'disambiguation': '', 'score': 100}]
    H.lt(1171, H.uid('1a1a1a1a', 1171), 'design', 'label', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    SEC = "[...document.querySelectorAll('section.dci-group')].find(s => /Jane Nine/.test(s.querySelector('.dci-gname strong').textContent))"
    STATE = f"""(() => {{ const g = {SEC}; if (!g) return null; const m = g.querySelector('.dci-gmatch');
      return {{ kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1] || '', hits: [...g.querySelectorAll('.dci-mbs li')].length, more: (g.querySelector('[data-act=mbs-more]') || {{}}).textContent || '',
        sel: (g.querySelector('[data-f=match-kind]') || {{}}).value || '', link: (g.querySelector('.dci-mblink') || {{}}).href || '',
        rows: [...g.querySelectorAll('tr.dci-row')].map(tr => {{ const t = tr.querySelector('[data-f=type]'); return [t ? (t.options[t.selectedIndex] || {{}}).text : '', ((tr.className.match(/dci-lv-(\\w+)/) || [])[1]) || '']; }}) }}; }})()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        dialogs = []
        pg.on('dialog', lambda d: (dialogs.append(d.message), d.accept()))
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Design by Jane Nine')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(800)
        sec = lambda: pg.locator('section.dci-group', has=pg.locator('.dci-gname strong', has_text='Jane Nine')).first

        def search(q):
            sec().locator('[data-f=artist-input]').fill(q)
            sec().locator('[data-f=artist-input]').press('Enter')
            H.wait_for(pg, f"(() => {{ const g = {SEC}; return !!g && !!g.querySelector('.dci-mbs') && !g.querySelector('.dci-mbs .dci-badge'); }})()", 20)
            pg.wait_for_timeout(200)
        search('Jane Nine')
        a1 = pg.evaluate(STATE)
        sec().locator('[data-act=mbs-more]').click(); pg.wait_for_timeout(300)
        a2 = pg.evaluate(STATE)
        print('A)', a1, '| mehr:', a2['hits'], a2['more'])
        results.append(a1['hits'] == 3 and a1['more'] == '+ 2 more' and a1['kind'] != 'label' and a2['hits'] == 5 and not a2['more'])
        # B) a label
        dialogs.clear()  # (the question of loading the text)
        sec().locator('[data-f=match-kind]').select_option('label'); pg.wait_for_timeout(800)
        b1 = pg.evaluate(STATE)
        search('Jane Nine')
        sec().locator('[data-act=mbs-use]').first.click(); pg.wait_for_timeout(600)
        b2 = pg.evaluate(STATE)
        print('B)', b1, '→', b2)
        results.append(b1['kind'] == 'label' and b1['rows'] == [['design', 'release']] and not dialogs and LAB in b2['link'] and b2['kind'] == 'label')
        # C) linked: back to an artist after a question
        sec().locator('[data-act=artist-edit]').first.click(); pg.wait_for_timeout(300)
        sec().locator('[data-f=match-kind]').select_option('artist'); pg.wait_for_timeout(800)
        c1 = pg.evaluate(STATE)
        print('C)', c1, '| Rückfrage:', dialogs)
        results.append(len(dialogs) == 1 and 'Jane Nine Design' in dialogs[0] and c1['kind'] != 'label' and not c1['link'] and [r[0] for r in c1['rows']] == ['design'])
        # D) one hit at first
        pg.evaluate("localStorage.setItem('dci-mb-hits', '1')")
        search('Jane Nine')
        d1 = pg.evaluate(STATE)
        print('D)', d1['hits'], d1['more'])
        results.append(d1['hits'] == 1 and d1['more'] == '+ 1 more')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_mbsearch3123r():
    """Credits Importer 3.123.0 (review of Z-MBSEARCH, S193): Discogs credits "Design – Jane Nine" (an artist not in MusicBrainz); made a
    label by hand and linked to MusicBrainz's label "Jane Nine Design" – after a reload of the page and the dashboard opened again
    the entry is that label, linked, with its row "design" (until the review an artist with a label's rows)."""
    LAB = H.uid('eeeeeeee', 3124)
    H.MB_SEARCH['label'] = [{'id': LAB, 'name': 'Jane Nine Design', 'type': 'Production', 'disambiguation': '', 'score': 100}]
    H.lt(1171, H.uid('1a1a1a1a', 1171), 'design', 'label', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = d['extraartists'] + [{'name': 'Jane Nine', 'anv': '', 'role': 'Design', 'tracks': '', 'id': 3416, 'join': ''}]
        return d

    H.discogs_release = rel
    SEC = "[...document.querySelectorAll('section.dci-group')].find(s => /Jane Nine/.test(s.querySelector('.dci-gname strong').textContent))"
    STATE = f"""(() => {{ const g = {SEC}; if (!g) return null;
      return {{ kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1] || '', link: (g.querySelector('.dci-mblink') || {{}}).href || '',
        rows: [...g.querySelectorAll('tr.dci-row')].map(tr => {{ const t = tr.querySelector('[data-f=type]'); return [t ? (t.options[t.selectedIndex] || {{}}).text : '', ((tr.className.match(/dci-lv-(\\w+)/) || [])[1]) || '']; }}) }}; }})()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(800)
        sec = lambda: pg.locator('section.dci-group', has=pg.locator('.dci-gname strong', has_text='Jane Nine')).first
        sec().locator('[data-f=match-kind]').select_option('label'); pg.wait_for_timeout(800)
        sec().locator('[data-f=artist-input]').fill('Jane Nine')
        sec().locator('[data-f=artist-input]').press('Enter')
        H.wait_for(pg, f"(() => {{ const g = {SEC}; return !!g && !!g.querySelector('[data-act=mbs-use]'); }})()", 20)
        sec().locator('[data-act=mbs-use]').first.click(); pg.wait_for_timeout(800)
        a = pg.evaluate(STATE)
        done = pg.evaluate("[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length")
        pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length > {done}", 60)
        pg.wait_for_timeout(1200)
        b2 = pg.evaluate(STATE)
        print('vorher:', a, '| nach dem Neuladen:', b2)
        results.append(a['kind'] == 'label' and LAB in a['link'] and bool(b2) and b2['kind'] == 'label' and LAB in b2['link'] and b2['rows'] == [['design', 'release']])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
