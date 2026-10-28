"""The window "Mapping rules": its words, in the dashboard, rule ids at rows (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: rulesname, rulesdock, rowrules – each the former smoke/t_<case>.py, unchanged; `python3 t_rules_window.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_rulesname():
    """Import 3.13.2: the window "Mapping rules" names Discogs only while Discogs is the loaded source.
    A) Discogs loaded: "Try a Discogs role:", the column "Discogs", "Discogs role → MusicBrainz", the hint with "as on Discogs".
    B) A pasted text loaded while the window is open: the window follows at once – "Try a role:", column "Role",
       "Role → MusicBrainz", "Role (without details)", the hint "as the source writes it".
    C) Discogs again: the Discogs words are back."""
    STATE = """(() => { const w = document.getElementById('dci-rules'); return {
  label: w.querySelector('[data-rf=test-label]').textContent.trim(),
  col: w.querySelector('[data-rsect=roles] thead th:nth-child(3)').textContent.trim(),
  kind: [...w.querySelectorAll('[data-uf=kind] option')].map(o => o.textContent.trim()),
  field: w.querySelector('[data-uf=discogs]').closest('label').textContent.trim(),
  hint: w.querySelector('[data-rf=result]').textContent.trim() }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.locator('[data-act=rules]').first.click()
        pg.wait_for_selector('#dci-rules [data-rsect=roles]')
        a = pg.evaluate(STATE)
        print('A)', a)
        results.append(a['label'] == 'Try a Discogs role:' and a['col'] == 'Discogs' and a['kind'][0] == 'Discogs role → MusicBrainz'
                       and a['field'].startswith('Discogs role (without details)') and 'as on Discogs' in a['hint'])
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Bass Man – bass')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(500)
        bb = pg.evaluate(STATE)
        print('B)', bb)
        results.append(bb['label'] == 'Try a role:' and bb['col'] == 'Role' and bb['kind'] == ['Role → MusicBrainz', 'Spelling → MB instrument']
                       and bb['field'].startswith('Role (without details)') and 'as the source writes it' in bb['hint'])
        H.src_menu(pg)
        pg.fill('[data-f=discogs-input]', '1234')
        pg.click('[data-act=discogs-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 3", 90)
        pg.wait_for_timeout(500)
        c = pg.evaluate(STATE)
        print('C)', c['label'], c['col'])
        results.append(c['label'] == 'Try a Discogs role:' and c['col'] == 'Discogs')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_rulesdock():
    """Credits Importer 3.30.0: "Mapping rules" in the dashboard (collected item 75; the maintainer's answer of
    2026-10-24 17:42: "ja standardmäßig im Dashboard und ja soll sich die Einstellung merken. ja nur eines öffnen und das
    andere schließen").
    A) By default the symbol "Mapping rules" in the head opens them in the dashboard below its head (not a window of their
       own; the symbol pressed, the test field focused, "⧉ As window" in their head).
    B) ⚙ Settings opened: the rules close; "Mapping rules" again: the settings close.
    C) "⧉ As window": the rules float as a window (stored "window"), still open; ⚙ Settings leave the window open.
    D) Reloaded: they open as a window again; ⚙ Settings → Appearance says "as a window"; "in the dashboard" there brings
       them back (nothing stored).
    E) The symbol closes them again, Escape too.
    F) A rule id at a row opens them at that rule (highlighted, in view) – [3.30.2] as a window (item 75b; t_rowrules.py)."""
    STATE = """(() => { const r = document.getElementById('dci-rules'); const dock = document.querySelector('#dci-overlay [data-el=rules-dock]');
  const set = document.querySelector('[data-el=settings]'); const b = document.querySelector('.dci-head [data-act=rules]');
  return { open: !!(r && !r.hidden && r.offsetParent !== null) || !!(r && !r.hidden && getComputedStyle(r).position === 'fixed'),
    docked: !!(r && dock && dock.contains(r) && r.classList.contains('dci-rules-docked')), dockShown: !!(dock && !dock.hidden),
    position: r ? getComputedStyle(r).position : '', pressed: b.getAttribute('aria-expanded'), settings: !!(set && !set.hidden),
    place: r ? (r.querySelector('[data-rules-place]') || {}).textContent : '', focus: !!(document.activeElement && document.activeElement.dataset.rf === 'test'),
    stored: localStorage.getItem('dci-rules-place') }; })()"""
    RULES = '.dci-head [data-act=rules]'
    GEAR = '.dci-head [data-act=settings-open]'
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
        st = lambda: pg.evaluate(STATE)
        # A)
        pg.click(RULES)
        pg.wait_for_timeout(300)
        a1 = st()
        print('A) geöffnet:', a1)
        results.append(a1['open'] and a1['docked'] and a1['dockShown'] and a1['position'] == 'static' and a1['pressed'] == 'true' and a1['focus']
                       and a1['place'].strip() == '⧉ As window' and a1['stored'] is None)
        # B) only one of both
        pg.click(GEAR)
        pg.wait_for_timeout(300)
        b1 = st()
        pg.click(RULES)
        pg.wait_for_timeout(300)
        b2 = st()
        print('B) ⚙ auf:', [b1['open'], b1['settings'], b1['pressed']], '| Regeln wieder:', [b2['open'], b2['settings']])
        results.append(not b1['open'] and b1['settings'] and b1['pressed'] == 'false' and b2['open'] and not b2['settings'])
        # C) as a window
        pg.click('#dci-rules [data-rules-place=window]')
        pg.wait_for_timeout(300)
        c1 = st()
        pg.click(GEAR)
        pg.wait_for_timeout(300)
        c2 = st()
        print('C) als Fenster:', c1, '| ⚙ dazu:', [c2['open'], c2['settings']])
        results.append(c1['open'] and not c1['docked'] and not c1['dockShown'] and c1['position'] == 'fixed' and c1['stored'] == '"window"'
                       and c1['place'].strip() == 'Into the dashboard' and c2['open'] and c2['settings'])
        pg.click(GEAR)
        # D) remembered
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        pg.click(RULES)
        pg.wait_for_timeout(300)
        d1 = st()
        H.open_settings(pg, 'appearance')
        d2 = pg.evaluate("[...document.querySelectorAll('.dci-set-pane [data-act=rules-place]')].map(x => [x.dataset.place, x.getAttribute('aria-pressed')])")
        pg.click('.dci-set-pane [data-act=rules-place][data-place=dashboard]')
        pg.wait_for_timeout(300)
        d3 = st()
        print('D) neu geladen:', [d1['open'], d1['docked'], d1['position']], '| Darstellung:', d2, '| im Dashboard:', [d3['open'], d3['docked'], d3['stored'], d3['settings']])
        results.append(d1['open'] and not d1['docked'] and d1['position'] == 'fixed' and d2 == [['dashboard', 'false'], ['window', 'true']]
                       and d3['open'] and d3['docked'] and d3['stored'] is None and not d3['settings'])
        # E) closed by the symbol, by Escape
        pg.click(RULES)
        pg.wait_for_timeout(300)
        e1 = st()
        pg.click(RULES)
        pg.wait_for_timeout(300)
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
        e2 = st()
        print('E) Symbol:', [e1['open'], e1['dockShown'], e1['pressed']], '| Escape:', [e2['open'], e2['dockShown'], pg.evaluate("!document.getElementById('dci-overlay').hidden")])
        results.append(not e1['open'] and not e1['dockShown'] and e1['pressed'] == 'false' and not e2['open'] and not e2['dockShown']
                       and pg.evaluate("!document.getElementById('dci-overlay').hidden"))
        # F) a rule id at a row
        rid = pg.evaluate("(document.querySelector('tr.dci-row [data-act=rule-goto]') || {}).dataset.rule")
        pg.locator(f'tr.dci-row [data-act=rule-goto][data-rule="{rid}"]').first.click()
        pg.wait_for_timeout(500)
        f1 = pg.evaluate("""(() => { const r = document.querySelector('#dci-rules tr.dci-rule-hit'); if (!r) return null;
      const body = document.querySelector('#dci-rules .dci-rules-body').getBoundingClientRect(); const rb = r.getBoundingClientRect();
      return [r.dataset.rid, rb.top >= body.top - 1 && rb.bottom <= body.bottom + 1]; })()""")
        print('F) Regel', rid, '→', f1, st()['docked'])
        results.append(f1 == [rid, True] and not st()['docked'] and st()['position'] == 'fixed')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_rowrules():
    """Credits Importer 3.30.2: rule ids at rows open the mapping rules as a window, the arrow in the head of an entry
    (collected items 75b, 82b; the maintainer's answers of 2026-10-25 01:59).
    A) A rule id at a row opens the rules as a window (not in the dashboard, where the symbol opens them; nothing stored),
       at that rule; the row stays where it was on the screen.
    B) The symbol in the head closes that window; the symbol again opens the rules in the dashboard.
    C) "Into the dashboard" in such a window: in the dashboard (the place stays "in the dashboard", nothing stored).
    D) ⚙ Settings → Appearance "Rule ids and ⓘ at rows open them: like the symbol" (stored "symbol"): a rule id opens them in
       the dashboard.
    E) Compact view: the arrow ▸ in the head of an entry opens all its rows (▾); one row closed again: ▸; ▸ opens all,
       ▾ closes all."""
    STATE = """(() => { const r = document.getElementById('dci-rules'); const dock = document.querySelector('#dci-overlay [data-el=rules-dock]');
  return { open: !!(r && !r.hidden), docked: !!(r && dock && dock.contains(r) && r.classList.contains('dci-rules-docked')), position: r ? getComputedStyle(r).position : '',
    hit: (document.querySelector('#dci-rules tr.dci-rule-hit') || {dataset: {}}).dataset.rid || null, stored: [localStorage.getItem('dci-rules-place'), localStorage.getItem('dci-rules-rowplace')],
    pressed: document.querySelector('.dci-head [data-act=rules]').getAttribute('aria-expanded') }; })()"""
    RULES = '.dci-head [data-act=rules]'
    ROWID = "section.dci-group:has(.dci-gname strong:text-is('Bob Producer')) tr.dci-row [data-act=rule-goto]"
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
        st = lambda: pg.evaluate(STATE)
        # A)
        btn = pg.locator(ROWID).first
        btn.scroll_into_view_if_needed()
        rid = btn.get_attribute('data-rule')
        y0 = btn.evaluate('b => Math.round(b.getBoundingClientRect().top)')
        btn.click()
        pg.wait_for_timeout(500)
        a1 = st()
        y1 = pg.locator(ROWID).first.evaluate('b => Math.round(b.getBoundingClientRect().top)')
        print('A) Regel-ID', rid, '→', a1, '| Zeile vorher/nachher:', y0, y1)
        results.append(a1['open'] and not a1['docked'] and a1['position'] == 'fixed' and a1['hit'] == rid and a1['stored'] == [None, None] and abs(y1 - y0) <= 2)
        # B)
        pg.click(RULES)
        pg.wait_for_timeout(300)
        b1 = st()
        pg.click(RULES)
        pg.wait_for_timeout(300)
        b2 = st()
        print('B) Symbol schließt:', [b1['open'], b1['pressed']], '| Symbol öffnet:', [b2['open'], b2['docked']])
        results.append(not b1['open'] and b1['pressed'] == 'false' and b2['open'] and b2['docked'])
        pg.click(RULES)
        pg.wait_for_timeout(200)
        # C)
        pg.locator(ROWID).first.click()
        pg.wait_for_timeout(400)
        pg.click('#dci-rules [data-rules-place=dashboard]')
        pg.wait_for_timeout(300)
        c1 = st()
        print('C) „Into the dashboard“:', [c1['open'], c1['docked'], c1['stored']])
        results.append(c1['open'] and c1['docked'] and c1['stored'] == [None, None])
        pg.click(RULES)
        pg.wait_for_timeout(200)
        # D)
        H.open_settings(pg, 'appearance')
        d0 = pg.evaluate("[...document.querySelectorAll('.dci-set-pane [data-act=rules-rowplace]')].map(x => [x.dataset.place, x.getAttribute('aria-pressed')])")
        pg.click('.dci-set-pane [data-act=rules-rowplace][data-place=symbol]')
        pg.wait_for_timeout(200)
        pg.click('.dci-head [data-act=settings-open]')
        pg.locator(ROWID).first.click()
        pg.wait_for_timeout(400)
        d1 = st()
        print('D) Einstellung:', d0, '| wie das Symbol:', [d1['open'], d1['docked'], d1['stored']])
        results.append(d0 == [['window', 'true'], ['symbol', 'false']] and d1['open'] and d1['docked'] and d1['stored'] == [None, '"symbol"'])
        pg.click(RULES)
        pg.wait_for_timeout(200)
        # E) the arrow in the head (compact view): Bass Man with a second role
        sec = "section.dci-group:has(.dci-gname strong:text-is('Bass Man'))"
        pg.click(f'{sec} [data-act=add-role]')
        pg.wait_for_timeout(300)
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(400)
        ARROW = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man');
      const a = g.querySelector('.dci-gname [data-act=group-openall]'); return [a ? a.textContent.trim() : null, a ? a.getAttribute('aria-expanded') : null,
      [...g.querySelectorAll('tr.dci-row')].map(tr => tr.classList.contains('dci-open'))]; })()"""
        pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man');
      g.querySelectorAll('tr.dci-row.dci-open .dci-cl-close').forEach(b => b.click()); })()""")
        pg.wait_for_timeout(300)
        e0 = pg.evaluate(ARROW)
        pg.click(f'{sec} .dci-gname [data-act=group-openall]')
        pg.wait_for_timeout(300)
        e1 = pg.evaluate(ARROW)
        pg.locator(f'{sec} tr.dci-row.dci-open .dci-cl-close').first.click()
        pg.wait_for_timeout(300)
        e2 = pg.evaluate(ARROW)
        pg.click(f'{sec} .dci-gname [data-act=group-openall]')
        pg.wait_for_timeout(300)
        e3 = pg.evaluate(ARROW)
        pg.click(f'{sec} .dci-gname [data-act=group-openall]')
        pg.wait_for_timeout(300)
        e4 = pg.evaluate(ARROW)
        print('E) Pfeil:', e0, e1, e2, e3, e4)
        results.append(e0 == ['▸', 'false', [False, False]] and e1 == ['▾', 'true', [True, True]] and e2[0] == '▸' and e2[2].count(True) == 1
                       and e3 == ['▾', 'true', [True, True]] and e4 == ['▸', 'false', [False, False]])
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        e5 = pg.evaluate("document.querySelectorAll('.dci-gname [data-act=group-openall]').length")
        print('   volle Ansicht – Pfeile im Kopf:', e5)
        results.append(e5 == 0)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_quickswitch():
    """Credits Importer 3.32.0 (milestone "Quick switches"): quick switches at the top of "Mapping rules" (collected item 97d;
    maintainer: "bitte lass das aber an- und abstellen. im mapping ganz oben evtl. (mit klickbarem verweis dann wo es verwendet
    wird)", "auf jeden fall noch die regel, dass performance dates die über mehrere tage hinweg gehen nach meinen regeln auf
    den kleinsten gemeinsamen nenner gekürzt werden").
    A) Seven switches in this order – S045, D022, S021, S031, S007 on, D023 and S046 off – each with its id. [3.32.8] In a box
       of their own (head, frame with round corners of 4 px), each switch a button (pressed = on; collected item 116).
    B) A click on an id shows that rule in the list below (highlighted).
    C) A quick switch and the rule's own switch are the same: S007 off at the top (a click on its button) → off in the list and
       stored; on again.
    D) D022: "Recorded March 1–3, 2001" in the notes → under Performance the month 2001-03 at once (the period stays in the
       pool); D022 off → the period again (the suggestions not applied yet are placed anew); on → the month.
    E) S045: a pasted text "Composed by Tomas Fujiwara (BMI)" and "Lyrics by Ann Poe / GEMA" → Tomas Fujiwara and Ann Poe
       without the society, BMI and GEMA as the release's rights societies."""
    from common_rows import cells
    # [3.32.8] each switch a button (aria-pressed) with its id next to it, in a box of its own (item 116)
    QS = """[...document.querySelectorAll('#dci-rules [data-rf=quick] .dci-qbtn-wrap')].map(x => [x.querySelector('[data-qs-goto]').textContent.trim(), x.querySelector('[data-qs-toggle]').getAttribute('aria-pressed') === 'true'])"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        if pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') != 'true':
            pg.click('.dci-pools-toggle'); pg.wait_for_timeout(200)
        perf0 = [c[0] for c in cells(pg).get('performance', [])]
        pool0 = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date .dci-chip-main')].map(c => c.textContent.trim())")
        pg.click('.dci-head [data-act=rules]'); pg.wait_for_timeout(300)
        a = pg.evaluate(QS)
        box = pg.evaluate("""(() => { const q = document.querySelector('#dci-rules [data-rf=quick] .dci-quick'); const st = getComputedStyle(q);
          return [!!q.querySelector('.dci-quick-h strong'), q.querySelectorAll('.dci-quick-grid > .dci-qbtn-wrap').length, st.borderTopStyle, st.borderTopLeftRadius,
            q.querySelector('[data-qs-toggle=S045]').textContent.replace(/\\s+/g, ' ').trim()]; })()""")
        print('A) Schalter:', a, '| Kasten:', box)
        results.append(a == [['S045', True], ['D022', True], ['S021', True], ['S031', True], ['S007', True], ['D023', False], ['S046', False]]
                       and box[:4] == [True, 7, 'solid', '4px'] and box[4].startswith('Rights society after a writer’s name'))
        pg.click('#dci-rules [data-qs-goto=S031]'); pg.wait_for_timeout(300)
        hit = pg.evaluate("[...document.querySelectorAll('#dci-rules tr.dci-rule-hit')].map(r => r.dataset.rid)")
        print('B) gezeigt:', hit)
        results.append(hit == ['S031'])
        pg.click('#dci-rules [data-rf=quick] [data-qs-toggle=S007]'); pg.wait_for_timeout(500)
        c1 = [pg.locator('#dci-rules [data-rf=tables] [data-rule-on=S007]').is_checked(), pg.evaluate("localStorage.getItem('dci-rules-off')")]
        pg.click('#dci-rules [data-rf=quick] [data-qs-toggle=S007]'); pg.wait_for_timeout(500)
        c2 = [pg.locator('#dci-rules [data-rf=tables] [data-rule-on=S007]').is_checked(), pg.evaluate("localStorage.getItem('dci-rules-off')")]
        print('C) S007 aus:', c1, '| wieder an:', c2)
        results.append(c1[0] is False and 'S007' in (c1[1] or '') and c2[0] is True and 'S007' not in (c2[1] or ''))
        pg.click('#dci-rules [data-rf=quick] [data-qs-toggle=D022]'); pg.wait_for_timeout(600)
        perf1 = [c[0] for c in cells(pg).get('performance', [])]
        pg.click('#dci-rules [data-rf=quick] [data-qs-toggle=D022]'); pg.wait_for_timeout(600)
        perf2 = [c[0] for c in cells(pg).get('performance', [])]
        print('D) Performance:', perf0, '| Pool:', pool0, '| D022 aus:', perf1, '| an:', perf2)
        results.append(perf0 == ['Performance 1 (month) · 2001-03'] and any('2001-03-01 – 2001-03-03' in x for x in pool0)
                       and perf1 == ['Performance 1 · 2001-03-01 – 2001-03-03'] and perf2 == perf0)
        # E) a pasted text
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Composed by Tomas Fujiwara (BMI)\nLyrics by Ann Poe / GEMA')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        groups = pg.evaluate("[...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim())])")
        # [3.32.4] the name only (the head has the tag of its kind before it)
        cols = pg.evaluate("[...document.querySelectorAll('.dci-matrix th[data-colhead] .dci-mx-colname')].map(x => (x.querySelector('.dci-mblink, strong') || x).textContent.replace(/^MB/, '').trim().split(/\\s/).slice(0, 2).join(' '))")
        print('E) Einträge:', groups, '| Spalten:', cols)
        names = [g[0] for g in groups]
        results.append('BMI' in names and 'GEMA' in names and dict(groups).get('BMI') == ['Rights Society'] and dict(groups).get('GEMA') == ['Rights Society']
                       and 'Tomas Fujiwara' in cols and 'Ann Poe' in cols and not any('BMI' in c or 'GEMA' in c for c in cols))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
