"""View: the compact view, folding, the colours of the levels, small fixes, the suggestions, rows (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: compact, fold, levels, ui301, suggstack, rows – each the former smoke/t_<case>.py, unchanged; `python3 t_ui_view.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_compact():
    """Credits Importer 3.27.0: the compact view of the entries (collected item 31; milestone). [3.27.2] Full is the default
    again (item 72), the symbol in the head switches (item 60).
    A) Full at first (nothing stored); the symbol in the head (not pressed) switches to compact – pressed, stored "compact"
       (until 3.27.1: compact by default, "Compact | Full" above the entries); one line per row – the role as written
       → type and instrument, level, tracks in short, date (or "no date"), what is open in colour (yellow "Bass: which
       instrument? electric bass guitar · double bass · acoustic bass guitar", [3.32.3] the possibilities to click); the
       fields of the full row and the "credited as" block hidden.
    B) A click on the line opens the full row (its type field focused); "▴ compact" closes it again.
    C) The tracks and the date of the compact line are still drop targets: a track group ("Side A", tracks 1–2) dropped
       onto it gives "tracks 1–2", a date of the pool shows on the line.
    D) The question answered ("double bass") – [3.32.3] in the compact line itself, the row stays closed (item 102; until
       3.32.2 the line said "Bass: which instrument?" and the question was in the opened row): the line says so, the yellow
       mark is gone.
    E) A skipped row: grey, with ✕ – out of the dashboard; the next import brings it back. [3.30.1] Its type stays on the
       line (grey), so the level does not move.
    F) "Compact" remembered after reloading (3.36.1: Guitar Guy's row removed with ✕ stays removed – the release is remembered); ⚙ Settings → General ([3.29.2] Appearance) has the same switch: "Full" – every row with its fields,
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
        results.append(a_full == [False, 'false', 0, True] and a0 == [True, 'true', 0, '"compact"'] and bass and bass[0]['text'].startswith('▸ Bass → instrument · bass Recording all 4 tracks no date')
                       # [3.32.3] the question whole, its possibilities to click (item 102)
                       and bass[0]['flags'] == [['dci-cl-ask dci-cl-askq', 'Bass: which instrument? electric bass guitar · double bass · acoustic bass guitar']] and not bass[0]['typeVisible'])
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
        drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', f'tr[data-row="{guitar}"] .dci-cl-tracks')
        c1 = line('Guitar Guy')[0]
        date = pg.evaluate("document.querySelector('.dci-pools-body .dci-pchip-date').dataset.id")
        dlabel = pg.evaluate(f"document.querySelector('.dci-pools-body .dci-pchip-date[data-id=\"{date}\"] .dci-chip-main').textContent.replace(/\\s+/g, ' ').trim()")
        drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', f'tr[data-row="{guitar}"] .dci-cl-date')
        c2 = line('Guitar Guy')[0]
        print('C) Trackgruppe:', c1['text'], '| Datum', repr(dlabel[:30]), '→', c2['text'], c2['hasDate'])
        results.append('tracks 1–2' in c1['text'] and c2['hasDate'] and dlabel.split(' · ')[0] in c2['text'] and not c2['open'])
        # D) [3.32.3] the question answered in the compact line itself (until 3.32.2: in the opened row); the row stays closed
        pg.click(f'tr[data-row="{rid}"] .dci-cl-askq [data-act=instr-pick][data-instr="double bass"]')
        pg.wait_for_timeout(400)
        d1 = line('Bass Man')[0]
        print('D) beantwortet:', d1['text'], d1['flags'], '| offen:', d1['open'])
        results.append('→ instrument · double bass' in d1['text'] and d1['flags'] == [] and not d1['open'])
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
        results.append(e1['text'].startswith('▸ Guitar → instrument · guitar Skip') and e1['x'] and e1['bg'] != 'rgb(255, 255, 255)' and e2[0] is None and bool(e2[1]))
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
        results.append(f1 == [True, False, '"compact"'] and f2 == [True, True, True] and f3 == [['compact', 'true'], ['full', 'false']] and f4 == [False, None, 'false', True])
        pg.click('.dci-head [data-act=settings-open]')
        # G) a new row ("+ Another role") is open; closed and incomplete, a jump to it (› in the summary) opens it again
        pg.click('section.dci-group:has(.dci-gname strong:text-is("Bass Man")) [data-act=add-role]')
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
    answer of 2026-10-24 19:33: "nur bis zum nächsten Import").
    A) Full view: the arrow ▾ of "Bass Man" folds his rows to compact lines (▸, the tooltip says so); "Artist credit for
       all roles" stays; the other entries keep their fields; the focus stays on the arrow.
    B) A click on a line of the folded entry opens that row with all its fields; "▴ compact" closes it again.
    C) ▸ shows the rows with their fields again.
    D) Folded, then imported again: every entry full again.
    E) Compact view: the arrow of an entry with an open row closes its open rows."""
    SEC = "section.dci-group:has(.dci-gname strong:text-is('{name}'))"
    STATE = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; const a = g.querySelector('[data-act=group-fold]'); const v = g.querySelector('.dci-variants');
  return { folded: g.classList.contains('dci-gcompact'), arrow: a ? [a.textContent.trim(), a.getAttribute('aria-expanded'), a.title] : null,
    arrowNextToCredit: !!(a && a.nextElementSibling && a.nextElementSibling.classList.contains('dci-credit')),
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
        results.append(a0['arrow'][:2] == ['▾', 'true'] and a0['arrowNextToCredit'] and not a0['folded'] and all(r[2] and not r[1] for r in a0['rows'])
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
        matrix_back = pg.evaluate("[localStorage.getItem('dci-entries-view'), document.querySelectorAll('section.dci-em-entry').length > 0]")
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
                       and seq[2][2] == '→ instrument · bass')
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        # D)
        d1 = pg.evaluate("""(() => { const ow = document.querySelector('[data-act=bulk-level][data-level=only-works]');
      const lv = document.querySelector('[data-act=bulk-level][data-level=skip]'); const st = document.querySelector('.dci-scope > .dci-sub');
      const sb = document.querySelector('.dci-scope button'); const c = (e) => { const r = e.getBoundingClientRect(); return r.top + r.height / 2; };
      return [ow.parentElement === lv.parentElement, getComputedStyle(ow).boxShadow, Math.round(Math.abs(c(st) - c(sb))),
        Math.round(ow.getBoundingClientRect().left - lv.getBoundingClientRect().right)]; })()""")
        print('D) only works – in der Ebenen-Gruppe, Schatten, „Stage:“ Abweichung, Abstand:', d1)
        results.append(not d1[0] and 'rgb(138, 79, 158)' in d1[1] and d1[2] <= 2 and d1[3] >= 4)
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
    A) The head line: the red mark, the field and the buttons; below it the suggestions as a block of their own, side by side
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
        results.append(h['order'][:2] == ['mark', 'input:artist-input'] and h['order'][-1] == 'stack' and h['below'] and h['flow'] == 'row wrap'
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
        n_before = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0.name === 'Keys Guy').length")
        grp('Keys Guy').locator('[data-act=remove-row]').click(); pg.wait_for_timeout(300)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
        removed = pg.evaluate("window.__removed.map(r => r.entity0.name)")
        n_after = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0.name === 'Keys Guy').length")
        print('2) Keys Guy im Editor vorher/nachher:', n_before, n_after, '| herausgenommen:', removed)
        # 3) "Skip" all, then "only works": work relationships come back, all else stays skipped
        pg.click('[data-act=bulk-level][data-level=skip]'); pg.wait_for_timeout(300)
        pg.click('[data-act=bulk-level][data-level=only-works]'); pg.wait_for_timeout(500)
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
        pg.click('[data-act=bulk-level][data-level=only-works]'); pg.wait_for_timeout(500)
        print('4) Ohne vorheriges Übernehmen, Plan:', pg.inner_text('[data-el=sum]').replace('\n', ' ')[:120])
        pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
        kinds = pg.evaluate("[...new Set(MB.relationshipEditor.state.added.map(r => r.linkTypeID))].sort((a, b) => a - b)")
        print('   Im Editor (Typ-IDs):', kinds, '| Ergebnis:', 'OK' if kinds and all(k in (165, 167, 168, 208, 278, 297) for k in kinds) else 'FEHLER', '| Fehler:', errs)
        b.close()


def case_clineask():
    """Credits Importer 3.32.3: a type question in the compact line (collected item 102; maintainer: "die Abfragen wie "Bass:
    which instrument?" in der kompakt Ansicht sollen komplett dargestellt und klickbar sein", "ok ab 5"): "Directed By"
    (Q003) shows "type to choose" with its four possibilities as buttons; "conductor" clicked → the row is conductor, the
    question gone, the row still closed."""
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'].append({'name': 'Drum Guy', 'anv': '', 'role': 'Directed By', 'tracks': '', 'id': 3004, 'join': ''})
        return d

    H.discogs_release = rel
    LINE = """() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Drum Guy');
  const tr = [...g.querySelectorAll('tr.dci-row')].find(r => /Directed By/.test(r.querySelector('.dci-cl-role').textContent));
  const q = tr.querySelector('.dci-cl-askq');
  return { id: tr.dataset.row, open: tr.classList.contains('dci-open'), type: (tr.querySelector('.dci-cl-type') || {}).textContent.replace(/\\s+/g, ' ').trim(),
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
    """Credits Importer 3.32.4: the colours of the kinds (collected items 107, 108; maintainer: "die farblogik von artists und
    labels sollte auch in der work-matrix erhalten bleiben", "ja bitte blasser", a setting for the colours).
    A) Works matrix: the head of Writer W in the colour of artists, with the tag "Artist"; Pub Co in the colour of labels,
       "Label"; the cells stay neutral.
    B) ⚙ Settings → Appearance: "Colours for the kinds of entries" (on) and a colour per kind (artist, label, place, area,
       other); the artist colour changed to #aa0000 → the bar of Bass Man and the head of Writer W follow, stored as an own
       colour; off → grey for both; ↺ of the tab → back to the defaults."""
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
        results.append(app == [True, [['artist', '#5b6f8c'], ['label', '#2a8a8a'], ['place', '#4e8a3e'], ['area', '#8a6a3e'], ['other', '#8a8799']]]
                       and b1 == ['rgb(170, 0, 0)', 'rgb(170, 0, 0)', '{"artist":"#aa0000"}']
                       and b2 == ['rgb(138, 135, 153)', 'rgb(138, 135, 153)', 'false'] and b3 == ['rgb(91, 111, 140)', [None, None]])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
