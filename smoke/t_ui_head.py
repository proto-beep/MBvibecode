"""Dashboard: its head, the head of an entry, "Add entry manually", messages, the page bar, ▲ ▼ (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: head, entryhead, manualtop, msgs, bar, jump – each the former smoke/t_<case>.py, unchanged –, [3.34.23] compacthint, [3.36.3] keys, [3.37.11] anvcredit, [3.37.15] poolbar, [3.40.3] blockac, [3.40.7] copyname, [3.40.8] headnarrow, [3.40.14] launchtools, [3.72.0] focusfields (the former t_focus.py), [3.73.0] evask; `python3 t_ui_head.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_head():
    """Credits Importer 3.26.0: the head of the dashboard in one line (collected item 30).
    A) One line: title · the source (link) · "Source ▾" · "+ Supplement" · the status of the view · text size · ⚙, Mapping
       rules, Log, ⌨, ⤢, ✕ with own symbols ([3.36.5] no ⓘ) (aria-label and tooltip); no language, no window/page switch, no switches of
       the navigation in the head; the words next to the symbols only in a wide dashboard.
    B) "Source ▾": a menu with another source, "Paste text …", order of the sources, Bandcamp, "Delete stored import …";
       Escape and a click elsewhere close it (the dashboard stays open); "Paste text …" closes it and opens the text below
       the head.
    C) "+ Supplement" opens and closes the bar "Supplement with".
    D) After the installation the page bar asks for the language once (the browser's preselected: English; fr-FR:
       Français); the hint follows the choice; OK stores it and the question is gone, also after reloading. An update
       (the version of the update notice known) does not ask.
    E) The language in ⚙ Settings → General: Español – the dashboard in Spanish, the settings still open at General.
    I) [3.27.2] With the companion and no Discogs tab: "open in background" in the status stands out (purple, white, bold).
    [3.27.2] The symbol of the compact view first in the tools of the head (item 60)."""
    HEAD = """(() => { const h = document.querySelector('.dci-head'); const kids = [...h.children].filter(k => k.offsetParent !== null);
  const tops = kids.map(k => Math.round(k.getBoundingClientRect().top + k.getBoundingClientRect().height / 2));
  const btns = [...h.querySelectorAll('.dci-head-tools .dci-ibtn')].map(b => [b.dataset.act, !!b.querySelector('svg.dci-ico'), b.getAttribute('aria-label'), b.title]);
  // (3.40.6) the groups: what stands between the separators
  const groups = [...h.querySelector('.dci-head-tools').children].reduce((g, k) => { if (k.classList.contains('dci-head-sep')) g.push([]); else g[g.length - 1].push(k.dataset.act || k.className); return g; }, [[]]);
  const label = h.querySelector('.dci-hlabel');
  return { spread: Math.max(...tops) - Math.min(...tops), btns, groups, zoom: h.querySelector('[data-el=zoom]').textContent.trim(),
    lang: h.querySelectorAll('[data-f=lang]').length, place: h.querySelectorAll('[data-act=place-toggle]').length,
    switches: h.querySelectorAll('[data-sync-mode], [data-dg-status], [data-click-toggle]').length, status: !!h.querySelector('.dci-syncstatus'),
    label: getComputedStyle(label).display }; })()"""
    MENU = """(() => { const m = document.querySelector('.dci-srcmenu'); return { open: !m.hidden, aria: document.querySelector('[data-act=srcmenu]').getAttribute('aria-expanded'),
  items: [...m.querySelectorAll('[data-act], [data-f]')].map(e => e.dataset.act || e.dataset.f) }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        # D) the question of the language (first installation)
        d0 = pg.evaluate("""(() => { const q = document.getElementById('dci-langask'); return q ? [q.querySelector('input:checked').value,
      q.querySelector('.dci-langask-hint').textContent, localStorage.getItem('dci-lang-ask')] : null; })()""")
        pg.check('#dci-langask input[value=de]')
        d1 = [pg.locator('#dci-langask .dci-langask-hint').inner_text(), pg.locator('#dci-langask .dci-langask-ok').inner_text()]
        pg.click('#dci-langask .dci-langask-ok')
        pg.wait_for_timeout(300)
        d2 = [pg.evaluate("localStorage.getItem('dci-lang')"), pg.evaluate("localStorage.getItem('dci-lang-ask')"), pg.locator('#dci-langask').count(),
              pg.locator('#dci-open').inner_text()]
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        d3 = [pg.locator('#dci-langask').count(), pg.locator('#dci-open').inner_text()]
        print('D) Frage:', d0, '| Deutsch gewählt:', d1, '| OK:', d2, '| neu geladen:', d3)
        results.append(d0 and d0[0] == 'en' and d0[1].startswith('Choose the language of the Credits Importer') and d0[2] == 'true'
                       and d1[0].startswith('Wähle die Sprache des Credits Importers') and d2 == ['"de"', None, 0, 'Credits importieren …'] and d3 == [0, 'Credits importieren …'])
        pg.evaluate("localStorage.setItem('dci-lang', JSON.stringify('en'))")
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(500)
        # A) one line
        a1 = pg.evaluate(HEAD)
        pg.evaluate("(() => { const p = document.querySelector('#dci-overlay .dci-panel'); p.style.width = '1700px'; p.style.left = '0px'; })()")
        pg.set_viewport_size({'width': 1800, 'height': 1000})
        pg.wait_for_timeout(300)
        a2 = pg.evaluate(HEAD)
        print('A) Kopf:', {k: v for k, v in a1.items() if k != 'btns'}, '\n   Knöpfe:', a1['btns'], '\n   breit:', a2['spread'], a2['label'])
        # [3.27.2] the symbol of the compact view first, left of the text size (item 60); [3.36.3] ⌨ the keyboard shortcuts;
        # [3.36.5] no ⓘ any more (collected item 147c: ⚙ → ⓘ Connections); [189] (3.39.3) the statistics after ⚙; [Z-HB] (3.40.6) in groups:
        # the view | the work | help and settings | ✕ (Q-ay)
        print('   Gruppen:', a1['groups'])
        results.append(a1['spread'] <= 6 and [x[0] for x in a1['btns']] == ['view-toggle', 'window-reset', 'rules', 'log', 'stats-open', 'keys-open', 'settings-open', 'close']
                       and a1['groups'] == [['view-toggle', 'dci-zoom', 'window-reset'], ['rules', 'log'], ['stats-open', 'keys-open', 'settings-open'], ['close']]
                       and all(x[1] and x[2] and x[3] for x in a1['btns']) and a1['btns'][6][2] == 'Settings' and a1['btns'][0][2] == 'Compact' and a1['zoom'] == '100 %'
                       and a1['lang'] == 0 and a1['place'] == 0 and a1['switches'] == 0 and a1['status'] and a1['label'] == 'none'
                       and a2['spread'] <= 6 and a2['label'] != 'none')
        pg.set_viewport_size({'width': 1500, 'height': 1000})
        pg.click('.dci-head [data-act=window-reset]')
        pg.wait_for_timeout(300)
        # B) the menu
        b0 = pg.evaluate(MENU)
        pg.click('.dci-head [data-act=srcmenu]')
        pg.wait_for_timeout(150)
        b1 = pg.evaluate(MENU)
        b1f = pg.evaluate("document.activeElement.dataset.f")
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(150)
        b2 = [pg.evaluate(MENU)['open'], pg.evaluate("document.activeElement.dataset.act"), pg.evaluate("!document.getElementById('dci-overlay').hidden")]
        H.src_menu(pg)
        pg.click('.dci-head h2')
        pg.wait_for_timeout(150)
        b3 = pg.evaluate(MENU)['open']
        H.src_menu(pg, 'text-open')
        b4 = [pg.evaluate(MENU)['open'], pg.evaluate("!!document.querySelector('[data-el=srcpanels] [data-f=text-src]')"), pg.evaluate("!document.querySelector('.dci-head [data-f=text-src]')")]
        pg.click('[data-act=text-cancel]')
        print('B) zu:', b0, '| offen:', b1, b1f, '| Escape:', b2, '| Klick daneben offen:', b3, '| Text:', b4)
        results.append(not b0['open'] and b0['aria'] == 'false' and b1['open'] and b1['aria'] == 'true' and b1f == 'discogs-input'
                       and b1['items'] == ['discogs-input', 'discogs-load', 'text-open', 'srcorder-toggle', 'bc-toggle', 'forget-open']
                       and b2 == [False, 'srcmenu', True] and b3 is False and b4 == [False, True, True])
        # C) + Supplement
        c0 = pg.evaluate("!!document.querySelector('.dci-suppbar')")
        pg.click('.dci-head [data-act=supp-open]')
        pg.wait_for_timeout(150)
        c1 = [pg.evaluate("!!document.querySelector('[data-el=srcpanels] .dci-suppbar')"), pg.locator('.dci-head [data-act=supp-open]').get_attribute('aria-expanded')]
        pg.click('.dci-head [data-act=supp-open]')
        pg.wait_for_timeout(150)
        c2 = pg.evaluate("!!document.querySelector('.dci-suppbar')")
        print('C) Leiste vorher:', c0, '| auf:', c1, '| wieder zu:', not c2)
        results.append(not c0 and c1 == [True, 'true'] and not c2)
        # E) the language in the settings
        H.open_settings(pg, 'general')
        pg.select_option('[data-el=settings] [data-f=lang]', 'es')
        pg.wait_for_timeout(500)
        e1 = [pg.locator('.dci-head [data-act=settings-open]').get_attribute('aria-label'), pg.evaluate("!document.querySelector('[data-el=settings]').hidden"),
              pg.evaluate("[...document.querySelectorAll('.dci-set-tab')].filter(t => t.getAttribute('aria-selected') === 'true').map(t => t.dataset.topic)"),
              pg.locator('.dci-head [data-act=srcmenu]').inner_text().strip()]
        print('E) Spanisch:', e1)
        results.append(e1 == ['Ajustes', True, ['general'], 'Fuente'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
        b = p.chromium.launch(args=H.LAUNCH_ARGS)

        # I) [3.27.2] with the companion and no Discogs tab: "open in background" stands out (item 65)
        ctx4 = H.new_context(b)
        pg4, errs4 = H.open_mb_edit(ctx4, companion=True)
        pg4.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg4)
        H.wait_for(pg4, "!!document.querySelector('.dci-head .dci-syncstatus [data-act=sync-open]')", 30)
        i1 = pg4.evaluate("""(() => { const b = document.querySelector('.dci-head .dci-syncstatus [data-act=sync-open]'); const st = getComputedStyle(b);
      return [b.textContent.trim(), st.backgroundColor, st.color, st.fontWeight]; })()""")
        print('I) Status-Knopf:', i1)
        results.append(i1[0] == 'open in background' and i1[1] == 'rgb(115, 109, 171)' and i1[2] == 'rgb(255, 255, 255)' and i1[3] in ('600', '700'))
        pg4.close()

        # D2) another browser language; D3) an update does not ask
        ctx2 = b.new_context(viewport={'width': 1500, 'height': 1000}, locale='fr-FR')
        H.install_routes(ctx2)
        H.add_mapping(ctx2)
        pg2, errs2 = H.open_mb_edit(ctx2, companion=False)
        pg2.wait_for_selector('#dci-open', timeout=20000)
        f1 = pg2.evaluate("(() => { const q = document.getElementById('dci-langask'); return q ? [q.querySelector('input:checked').value, q.querySelector('.dci-langask-hint').textContent.slice(0, 30)] : null; })()")
        ctx3 = H.new_context(b)
        ctx3.add_init_script("localStorage.setItem('dci-notice-version', JSON.stringify('3.25.0')); localStorage.setItem('dci-store-epoch', '4');")
        pg3, errs3 = H.open_mb_edit(ctx3, companion=False)
        pg3.wait_for_selector('#dci-open', timeout=20000)
        f2 = [pg3.locator('#dci-langask').count(), pg3.evaluate("localStorage.getItem('dci-lang-ask')")]
        print('D2) fr-FR:', f1, '| D3) Update:', f2)
        results.append(f1 == ['fr', 'Choisissez la langue du Credit'] and f2 == [0, None])
        results.append(not errs2 and not errs3)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_entryhead():
    """Credits Importer 3.28.0: the head of an entry and the bar below "Import credits …" (collected items 61, 66).
    A) Only the tag of the source links to it (with ↗; its tooltip names the source's name) – the name is not repeated.
    B) How the dashboard credits the entry: [3.32.2] the head shows the release's spelling "B. Man*" (Discogs credits Bass
       Man as "B. Man" on this release; collected item 100), its tooltip "Discogs: Bass Man", no chip "as “B. Man”" (until
       3.32.1: the name "Bass Man" and the chip) – [3.37.11] the chip "artist credit in MusicBrainz: “B. Man” (the Discogs
       spelling *)" instead, and the tooltip says what * means (collected item 161); the MusicBrainz name (no "credited as") – no chip. A row credited otherwise:
       "as “Bassman”" at the head (the spelling of the head not again; [3.38.11] "… for bass": only that row), the compact line of
       each row names its own credit.
    C) The bar below "Import credits …" (with the companion): the status as a badge (source link, "open in background")
       and ⚙ – no switches of the navigation any more; ⚙ opens the settings of the dashboard at "Discogs and Bandcamp view" ([3.30.5] "Source pages")."""
    orig = H.discogs_release


    def rel():
        d = orig()
        for ea in d['extraartists']:
            if ea['name'] == 'Bass Man':
                ea['anv'] = 'B. Man'
        d['extraartists'].append({'name': 'Bass Man', 'anv': 'B. Man', 'role': 'Vocals', 'tracks': '', 'id': 3001, 'join': ''})
        return d


    H.discogs_release = rel
    HEAD = """(name) => { const nm = (s) => { const x = s.querySelector('.dci-gname strong'); return x.dataset.name || x.textContent.trim(); };
  const g = [...document.querySelectorAll('section.dci-group')].find(s => nm(s) === name);
  if (!g) return null; const a = g.querySelector('.dci-dglink'); const c = g.querySelector('.dci-gcredit'); const st = g.querySelector('.dci-gname strong');
  return { link: a ? [a.textContent, a.getAttribute('href'), a.title] : null, chip: c && !c.hidden ? [c.textContent.trim(), c.title] : null,
    shown: [st.textContent.trim(), st.title || ''] }; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        head = lambda name: pg.evaluate(HEAD, name)
        # A)
        a1 = head('Guitar Guy')
        print('A) Guitar Guy:', a1)
        results.append(a1['link'] == ['Discogs↗', 'https://www.discogs.com/artist/3002', 'Open on Discogs: Guitar Guy'] and a1['chip'] is None)
        # B)
        b1 = head('Bass Man')
        sec = "section.dci-group:has(.dci-gname strong[data-name='Bass Man'])"
        rows = pg.locator(f'{sec} tr.dci-row')
        print('B) Bass Man:', b1, '| Zeilen:', rows.count())
        first = rows.nth(0).locator('[data-f=credit]')
        first.fill('Bassman')
        first.dispatch_event('change')
        pg.wait_for_timeout(500)
        b2 = head('Bass Man')
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(400)
        lines = pg.evaluate(f"document.querySelector(\"{sec}\").querySelectorAll('.dci-cl-as').length")
        pg.click('.dci-head [data-act=view-toggle]')
        print('   anders credited:', b2, '| Zeilen mit eigenem Credit (kompakt):', lines)
        results.append(b1['shown'][0] == 'B. Man*' and b1['shown'][1].startswith('Discogs: Bass Man\n* – credited so on Discogs')
                       and b1['chip'] and b1['chip'][0] == 'artist credit in MusicBrainz: “B. Man” (the Discogs spelling *)'
                       and b1['chip'][1].startswith('Discogs credits “Bass Man” on this release as “B. Man”')
                       and b2['chip'] and b2['chip'][0] == 'as “Bassman” for bass' and lines == 2)
        # C) the bar below "Import credits …"
        pg.click('.dci-head [data-act=close]')
        pg.wait_for_timeout(300)
        c1 = pg.evaluate("""(() => { const bar = document.getElementById('dci-controls'); return [!bar.hidden, bar.querySelectorAll('[data-sync-mode], [data-dg-status], [data-dg-hover], [data-click-toggle], [data-keep-marks], [data-dg-artwork]').length,
      !!bar.querySelector('.dci-syncstatus'), (bar.querySelector('.dci-syncstatus') || {}).textContent, !!bar.querySelector('[data-nav-settings]')]; })()""")
        pg.locator('#dci-controls [data-nav-settings]').click()
        pg.wait_for_timeout(600)
        c2 = [pg.evaluate("!document.getElementById('dci-overlay').hidden"), pg.evaluate("!document.querySelector('[data-el=settings]').hidden"),
              pg.evaluate("[...document.querySelectorAll('.dci-set-tab')].filter(t => t.getAttribute('aria-selected') === 'true').map(t => t.dataset.topic)"),
              pg.evaluate("!!document.querySelector('[data-el=settings] .dci-set-pane [data-dg-status]')")]
        print('C) Leiste:', c1, '| ⚙ →', c2)
        results.append(c1[0] and c1[1] == 0 and c1[2] and 'Discogs view' in c1[3] and c1[4] and c2 == [True, True, ['discogs'], True])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_evask():
    """Credits Importer 3.73.0 (collected item Z-EVQ, rule S108): an event pasted into "Add entry manually" without a role.
    A) Right below the line: "The event “Vancouver Jazz Festival 1993, Day 2”: which relationship?" – "recorded at", "choose later"
       (no "video shot at": the release has no videos).
    B) "recorded at": the row is "recorded at" on the recordings (not the release), the entry folded to its compact lines; the
       question gone; the log says so.
    C) A release with a video (track 2): the question offers "video shot at" too (from 3.85.0 first both, by media type); "choose
       later" leaves the row as it was.
    D) Rule S108 off: no question.
    (From 3.88.0 with rule S136 off – on, an event without a role gets its rows at once.)"""
    EV = H.uid('fefefefe', 11)
    H.COMPANIES[1031] = ('event', EV, 'Vancouver Jazz Festival 1993, Day 2')
    H.lt(9001, H.uid('9e9e9e9e', 1), 'recorded at', 'event', 'recording', ())
    H.lt(9002, H.uid('9e9e9e9e', 2), 'recorded at', 'event', 'release', ())
    H.lt(9003, H.uid('9e9e9e9e', 3), 'video shot at', 'event', 'recording', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    ASK = """(() => { const q = document.querySelector('[data-el=manual-evq]'); return q && !q.hidden ? { text: q.querySelector('span').textContent.trim(),
      btns: [...q.querySelectorAll('button')].map(b => b.textContent.trim()) } : null; })()"""
    ROW = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Vancouver Jazz Festival/.test(x.querySelector('.dci-gname').textContent));
      if (!g) return null; const r = g.querySelector('tr.dci-row'); const t = r.querySelector('[data-f=type]');
      return { type: t ? (t.selectedOptions[0] || {}).text : null, level: (r.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level || null,
        folded: g.classList.contains('dci-gcompact'), cline: !!r.querySelector('.dci-cline') && getComputedStyle(r.querySelector('td.dci-c-cline') || r).display !== 'none' }; })()"""
    results = []

    def open_page(p, off=False):
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        # ([Z-EVL] 3.88.0) the question only with rule S136 off (on: at once, case evl388 of t_notes_companies.py)
        pg.evaluate(f"localStorage.setItem('dci-rules-off', JSON.stringify({['S083', 'S108', 'S136'] if off else ['S136']}))")
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.evaluate("document.querySelector('[data-el=manual]').hidden = false")
        pg.fill('[data-f=manual-artist]', f'https://musicbrainz.org/event/{EV}')
        pg.click('[data-act=add-manual]')
        H.wait_for(pg, "[...document.querySelectorAll('section.dci-group')].some(x => /Vancouver Jazz Festival/.test(x.textContent))", 20)
        pg.wait_for_timeout(300)
        return pg, errs

    with sync_playwright() as p:
        pg, errs = open_page(p)
        a = pg.evaluate(ASK)
        print('A)', a)
        results.append(a == {'text': 'The event “Vancouver Jazz Festival 1993, Day 2”: which relationship?', 'btns': ['recorded at', 'choose later']})
        pg.click('[data-el=manual-evq] [data-type="recorded at"]')
        pg.wait_for_timeout(400)
        r = pg.evaluate(ROW)
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if x[9:].startswith('Event ')]
        print('B)', r, '| Frage:', pg.evaluate(ASK), '| Log:', logs)
        results.append(r and r['type'] == 'recorded at' and r['level'] == 'recording' and r['folded'] and pg.evaluate(ASK) is None
                       and logs == ['Event Vancouver Jazz Festival 1993, Day 2: recorded at (on the recordings; the level changes with a click)'] and not errs)
    H.VIDEO_TRACKS.add(1)
    with sync_playwright() as p:
        pg, errs = open_page(p)
        c = pg.evaluate(ASK)
        pg.click('[data-el=manual-evq] [data-act=manual-evq-later]')
        pg.wait_for_timeout(300)
        r2 = pg.evaluate(ROW)
        print('C)', c, '| danach:', pg.evaluate(ASK), r2)
        # ([Z-EVA] 3.85.0, S132) audio and video: "both" first – a row for each by media type
        results.append(c and c['btns'] == ['recorded at + video shot at (by media type)', 'recorded at', 'video shot at', 'choose later'] and pg.evaluate(ASK) is None and r2 and r2['type'] != 'recorded at' and not errs)
    with sync_playwright() as p:
        pg, errs = open_page(p, off=True)
        d = pg.evaluate(ASK)
        print('D)', d)
        results.append(d is None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_manualtop():
    """Credits Importer 3.18.0: "Add entry manually" as one line, always in view above the date pool (collected item 25).
    A) The line (title, entry, role, "Add", "?") stands in the sticky block, above "Dates & tracks"; the explanation is the
       tooltip of its title and of the entry field (no paragraph any more); the search links come with "?".
    B) Scrolled down to the works matrix (window): the line is still at the top of the dashboard, the pool below it.
    C) An entry added from there: its row is shown where it was added (scrolled into view below the sticky block, lit up).
    D) In the page (setting "In the page"): the block with the line sticks to the top of the browser window."""
    EXTRA = H.uid('dddddddd', 31)
    H.ARTISTS[3031] = (EXTRA, 'Extra Person')
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    LINE = """(() => { const st = document.querySelector('[data-el=stick]'); const m = st && st.querySelector('[data-el=manual]');
  if (!m) return null; const kids = [...st.children].map(c => c.dataset.el);
  const t = m.querySelector('.dci-manual-title'); const s = m.querySelector('[data-el=manual-search]');
  return { kids, hidden: m.hidden, title: t.textContent.trim(), tip: t.title, fieldTip: m.querySelector('[data-f=manual-artist]').title,
    fields: [...m.querySelectorAll('input, button')].map(x => x.dataset.f || x.dataset.act), paragraph: !!m.querySelector('p, h3'),
    search: s.hidden, links: s.querySelectorAll('a[target=_blank]').length }; })()"""
    POS = """(() => { const body = document.querySelector('[data-el=body]'); const m = document.querySelector('[data-el=manual]');
  const d = document.querySelector('[data-el=dates]'); const b = body.getBoundingClientRect();
  return { scrolled: Math.round(body.scrollTop), manual: Math.round(m.getBoundingClientRect().top - b.top), dates: Math.round(d.getBoundingClientRect().top - m.getBoundingClientRect().bottom),
    pad: body.style.scrollPaddingTop }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        # A)
        a1 = pg.evaluate(LINE)
        pg.locator('[data-el=manual] [data-act=manual-search]').evaluate('b => b.click()')
        a2 = pg.evaluate(LINE)
        exp = pg.locator('[data-el=manual] [data-act=manual-search]').get_attribute('aria-expanded')
        pg.locator('[data-el=manual] [data-act=manual-search]').evaluate('b => b.click()')
        print('A) Zeile:', a1)
        print('   „?“:', a2['search'], a2['links'], exp)
        results.append(a1 is not None and a1['kids'] == ['manual', 'dates'] and not a1['hidden'] and a1['title'] == 'Add entry manually'
                       and a1['tip'].startswith('Add any MusicBrainz entry') and a1['fieldTip'] == a1['tip'] and not a1['paragraph']
                       and a1['fields'] == ['manual-artist', 'manual-role', 'add-manual', 'manual-search'] and a1['search'] and a1['links'] == 11
                       and a2['search'] is False and exp == 'true')
        # B) scrolled down
        pg.evaluate("document.querySelector('[data-el=works]').scrollIntoView({ block: 'start' })")
        pg.wait_for_timeout(300)
        b1 = pg.evaluate(POS)
        print('B) gescrollt:', b1)
        results.append(b1['scrolled'] > 300 and -2 <= b1['manual'] <= 2 and 0 <= b1['dates'] <= 2 and b1['pad'].endswith('px'))
        # C) add from there
        pg.fill('[data-f=manual-artist]', f'https://musicbrainz.org/artist/{EXTRA}')
        pg.fill('[data-f=manual-role]', 'Mixed By')
        pg.locator('[data-act=add-manual]').evaluate('b => b.click()')
        H.wait_for(pg, f"{LOGS}.some(x => /Extra Person/.test(x))", 20)
        pg.wait_for_timeout(300)
        c1 = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Extra Person');
      const tr = g && g.querySelector('tr.dci-row'); if (!tr) return null; const st = document.querySelector('[data-el=stick]').getBoundingClientRect();
      const r = tr.getBoundingClientRect(); const body = document.querySelector('[data-el=body]').getBoundingClientRect();
      return [tr.classList.contains('dci-flash'), Math.round(r.top - st.bottom) >= 0, r.bottom <= body.bottom + 1,
        document.querySelector('[data-f=manual-artist]').value, document.querySelector('[data-f=manual-role]').value]; })()""")
        print('C) hinzugefügt:', c1, [x for x in pg.evaluate(LOGS) if 'Extra Person' in x])
        results.append(c1 is not None and c1[:3] == [True, True, True] and c1[3:] == ['', ''])
        # D) in the page
        H.toggle_place(pg)
        pg.wait_for_timeout(500)
        pg.evaluate("window.scrollTo(0, document.querySelector('[data-el=works]').getBoundingClientRect().top + window.scrollY - 300)")
        pg.wait_for_timeout(300)
        d1 = pg.evaluate("""(() => { const st = document.querySelector('[data-el=stick]'); const m = st.querySelector('[data-el=manual]');
      return [Math.round(window.scrollY), Math.round(st.getBoundingClientRect().top), Math.round(m.getBoundingClientRect().top), document.documentElement.style.scrollPaddingTop]; })()""")
        print('D) in der Seite:', d1)
        results.append(d1[0] > 300 and d1[1] == 0 and d1[2] >= 0 and d1[2] <= 2 and d1[3].endswith('px'))
        H.toggle_place(pg)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_msgs():
    """Credits Importer 3.27.3: the messages at the top close and fold (collected item 56).
    A) After the import two messages (dates from the notes): a line "▾ 2 messages" above them, each with ✕ (a symbol – the
       text of the message stays as it was).
    B) ✕ closes one; with one message left the fold line is gone.
    C) Two messages again (an error: "no Discogs release or Bandcamp album recognized"): "▾ 2 messages" folds them in –
       "▸ 2 messages", nothing else shown; a new warning or error unfolds them.
    D) A new import ("Delete stored import …", the release imported afresh) shows its messages again, unfolded: closed means
       until the next import."""
    # [3.30.8] the shared month of "March 1–3, 2001" no longer counts as a date without a group: a date that really has none
    _orig_rel = H.discogs_release


    def _rel():
        d = _orig_rel()
        d['notes'] += ' The band met on 4 July 2000.'
        return d


    H.discogs_release = _rel

    MSGS = """(() => { const el = document.querySelector('[data-el=msgs]'); const head = el.querySelector('.dci-msgs-fold');
  return { head: head ? head.textContent.replace(/\\s+/g, ' ').trim() : null, expanded: head ? head.getAttribute('aria-expanded') : null,
    msgs: [...el.querySelectorAll('.dci-msg')].map(m => [m.textContent.trim().slice(0, 40), !!m.querySelector('.dci-msg-x svg')]) }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        st = lambda: pg.evaluate(MSGS)
        # A)
        a1 = st()
        print('A)', a1)
        results.append(a1['head'] == '▾ 2 messages' and a1['expanded'] == 'true' and len(a1['msgs']) == 2 and all(x[1] for x in a1['msgs'])
                       and a1['msgs'][0][0].startswith('2 dates from the notes were placed'))
        # B)
        pg.click('[data-el=msgs] .dci-msg >> nth=0 >> .dci-msg-x')
        pg.wait_for_timeout(200)
        b1 = st()
        print('B) eine geschlossen:', b1)
        results.append(b1['head'] is None and len(b1['msgs']) == 1 and b1['msgs'][0][0].startswith('1 date from the notes has no word'))
        # C) an error: two again; fold; a new error unfolds
        H.src_menu(pg)
        pg.fill('[data-f=discogs-input]', 'no release here')
        pg.click('[data-act=discogs-load]')
        pg.wait_for_timeout(300)
        c1 = st()
        pg.click('[data-act=msgs-fold]')
        pg.wait_for_timeout(200)
        c2 = st()
        H.src_menu(pg)
        pg.fill('[data-f=discogs-input]', 'still nothing')
        pg.click('[data-act=discogs-load]')
        pg.wait_for_timeout(300)
        c3 = st()
        print('C) zwei:', c1['head'], '| eingeklappt:', c2, '| neuer Fehler:', c3['head'], c3['expanded'], len(c3['msgs']))
        results.append(c1['head'] == '▾ 2 messages' and c2 == {'head': '▸ 2 messages', 'expanded': 'false', 'msgs': []}
                       and c3['head'] == '▾ 3 messages' and c3['expanded'] == 'true' and len(c3['msgs']) == 3)
        pg.click('[data-act=msgs-fold]')
        pg.wait_for_timeout(200)
        # D) a new import from scratch ("Delete stored import …"): its messages again, unfolded
        H.src_menu(pg, 'forget-open')
        pg.click('[data-act=forget-do]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        d1 = st()
        print('D) neuer Import:', d1)
        results.append(d1['head'] == '▾ 2 messages' and d1['expanded'] == 'true' and any(m[0].startswith('2 dates from the notes were placed') for m in d1['msgs']))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_bar():
    """Page bar and pools: the language is chosen before the dashboard is opened – [3.27.1] in the question after the
    installation (the page bar has no language list any more), later in ⚙ Settings → General; "Dates & tracks"
    folds also at its bottom; folded, the date pool stays in the bar (on by default) and its dates can be dragged
    onto rows from there; drag hints; the common month/year of recording periods (D014); "Horn [French]",
    "Flugel Horn" without role credit; "Produced By" in "Companies, etc." is producer."""
    import re
    from common_rows import drag, date_field

    for i, n in [(9110, 'French horn'), (9111, 'horn'), (9112, 'flugelhorn')]:
        H.attr(i, n, 14, 14)
        H.LINKED['link_attribute_type'][str(i)] = H.ATTRS[i]
    orig = H.discogs_release


    def rel():
        d = orig()
        d['notes'] += '\nOverdubs recorded June 3 to September 30, 2002.\nStrings recorded December 2003 to January 2004.'
        ex = lambda name, role, i: {'name': name, 'anv': '', 'role': role, 'tracks': '', 'id': i, 'join': ''}
        d['extraartists'] += [ex('Keys Guy', 'Horn [French], Flugel Horn', 3003)]
        d['companies'].append({'name': 'Bob Producer', 'entity_type_name': 'Produced By', 'id': 1006, 'catno': ''})
        return d


    H.discogs_release = rel
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        # 1) [3.27.1] the language: the question after the installation (no language list in the page bar), then the settings
        lab = lambda: re.sub(r'\s+', ' ', pg.locator('#dci-launcher').inner_text())
        print('1) Seitenleiste:', lab()[:120], '| Liste:', pg.locator('#dci-launcher [data-dci-lang]').count())
        ok1 = pg.locator('#dci-launcher [data-dci-lang]').count() == 0 and 'Language' not in lab()
        pg.check('#dci-langask input[value=de]')
        pg.click('#dci-langask .dci-langask-ok'); pg.wait_for_timeout(300)
        print('   nach „Deutsch“ + OK:', lab()[:120], '| gespeichert:', pg.evaluate("localStorage.getItem('dci-lang')"))
        ok1 = ok1 and 'Credits importieren' in lab() and 'Sprache' not in lab() and pg.locator('#dci-overlay').count() == 0
        H.open_dashboard(pg)
        pg.wait_for_timeout(300)
        H.open_settings(pg, 'general')  # [3.26.0] the language is only in the settings
        ok1 = ok1 and pg.locator('#dci-title').inner_text() == 'Credits Importer' and pg.locator('[data-f=lang]').input_value() == 'de'
        pg.select_option('[data-f=lang]', 'en'); pg.wait_for_timeout(300)
        ok1 = ok1 and 'Import credits' in lab()
        print('   Dashboard Deutsch, in den Einstellungen zurück auf Englisch → Seitenleiste:', lab()[:40], ok1)
        # 2) D014: common month / year of recording periods
        chips = [re.sub(r'\s+', ' ', c) for c in pg.locator('.dci-pchip-date .dci-chip-main').all_inner_texts()]
        print('2) Pool:', chips)
        # names are made when the dates are found – here the dashboard was in German
        ok2 = any(c.startswith('Performance 1 (Monat) · 2001-03') for c in chips) and any(c.startswith('Performance 2 (Jahr) · 2002 ') for c in chips) \
            and any(c.startswith('Performance 3 · 2003-12 – 2004-01') for c in chips) and len(chips) == 6
        # 3) drag hints; folding at the bottom; folded, the date pool stays and its dates can be dragged onto rows
        hints = pg.locator('.dci-drag-hint').count()
        pg.click('.dci-pools-fold'); pg.wait_for_timeout(200)
        kept = pg.locator('.dci-pools-kept .dci-pchip-date').count()
        print('3) Hinweise:', hints, '| unten eingeklappt → offen:', pg.locator('.dci-pools-toggle').get_attribute('aria-expanded'), '| oben behalten:', kept)
        row = pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text='Drum Guy')).first.locator('tr.dci-row').first
        rid = row.get_attribute('data-row')
        perf = pg.evaluate("[...document.querySelectorAll('.dci-pools-kept .dci-pchip-date')].find(c => c.textContent.includes('Performance 1 ·')).dataset.id")
        drag(pg, f'.dci-pools-kept .dci-pchip-date[data-id="{perf}"] .dci-chip-main', f'tr[data-row="{rid}"] .dci-c-date')
        year = date_field(row, 'rd-by')
        print('   eingeklappt auf Drum Guy gezogen:', year)
        ok3 = hints == 1 and pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') == 'false' and kept == len(chips) and year == '2001'
        pg.click('.dci-pools-toggle'); pg.wait_for_timeout(150)
        pg.uncheck('[data-f=pools-keep]'); pg.click('.dci-pools-fold'); pg.wait_for_timeout(150)
        ok3 = ok3 and pg.locator('.dci-pools-kept').count() == 0 and pg.evaluate("localStorage.getItem('dci-pools-keep')") == 'false'
        print('   „oben behalten“ aus → Pool eingeklappt weg:', pg.locator('.dci-pools-kept').count() == 0)
        # 4) instruments and producer
        def rowinfo(raw):
            tr = pg.locator('tr.dci-row').filter(has=pg.locator(f'.dci-drole[data-raw="{raw}"]')).first
            typ = tr.locator('[data-f=type]').evaluate("s => s.options[s.selectedIndex] ? s.options[s.selectedIndex].text : ''")
            prim = tr.locator('[data-f=primary]').input_value() if tr.locator('[data-f=primary]').count() else ''
            rc = tr.locator('[data-f=role-credit]').input_value() if tr.locator('[data-f=role-credit]').count() else ''
            return typ, prim, rc
        horn, flugel, prod = rowinfo('Horn [French]'), rowinfo('Flugel Horn'), rowinfo('Produced By')
        comp = pg.locator('[data-el=companies] .dci-group').filter(has=pg.locator('.dci-gname', has_text='Bob Producer')).first.locator('tr.dci-row').first
        ctype = comp.locator('[data-f=type]').evaluate("s => s.options[s.selectedIndex] ? s.options[s.selectedIndex].text : ''")
        print('4) Horn [French]:', horn, '| Flugel Horn:', flugel, '| Produced By:', prod, '| Companies „Produced By“:', ctype)
        ok4 = horn == ('instrument', 'French horn', '') and flugel == ('instrument', 'flugelhorn', '') and prod[0] == 'producer' and ctype == 'producer'
        print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4]) else 'FEHLER', [ok1, ok2, ok3, ok4], '| Fehler:', errs)
        b.close()


def case_jump():
    """Import 3.14.1: ▲ ▼ in the footer jump to the top and the bottom of the dashboard – in the window (its own scrolling)
    and in the page (the page scrolls)."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        body = "document.querySelector('[data-el=body]')"
        # ([3.77.0] Z-FLK) waits for the state, not for a time: at the end, at the top (a busy computer scrolls later)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        # ((review) what is drawn after the import has its height first; ▼ again if the end grew meanwhile)
        H.wait_still(pg, f"{body}.scrollHeight", 15, 300)
        at_end = f"(() => {{ const b = {body}; return b.scrollHeight - b.clientHeight > 100 && Math.abs(b.scrollTop - (b.scrollHeight - b.clientHeight)) <= 2; }})()"
        for _ in range(3):
            pg.locator('[data-act=jump-bottom]').evaluate('b => b.click()')
            if H.wait_ok(pg, at_end, 5) and H.wait_still(pg, f"{body}.scrollTop") and pg.evaluate(at_end):
                break
        down = pg.evaluate(f"(() => {{ const b = {body}; return [Math.round(b.scrollTop), b.scrollHeight - b.clientHeight]; }})()")
        pg.locator('[data-act=jump-top]').evaluate('b => b.click()')
        H.wait_ok(pg, f"{body}.scrollTop === 0", 15)
        up = pg.evaluate(f"{body}.scrollTop")
        print('Fenster: ▼', down, '| ▲', up)
        results.append(down[1] > 100 and abs(down[0] - down[1]) <= 2 and up == 0)
        # in the page
        H.toggle_place(pg); pg.wait_for_timeout(300)
        inline = pg.evaluate("!!document.querySelector('.dci-inline')")
        pg.locator('[data-act=jump-bottom]').evaluate('b => b.click()')
        # ((review) in range, and the smooth scroll ended: a jump past the end would show)
        H.wait_ok(pg, "(() => { const r = document.querySelector('.dci-panel').getBoundingClientRect().bottom - innerHeight; return scrollY > 200 && r >= -40 && r <= 20; })()", 15)
        H.wait_still(pg, "scrollY")
        y1 = pg.evaluate("[Math.round(scrollY), Math.round(document.documentElement.scrollHeight - innerHeight)]")
        foot = pg.evaluate("Math.round(document.querySelector('.dci-panel').getBoundingClientRect().bottom - innerHeight)")
        pg.locator('[data-act=jump-top]').evaluate('b => b.click()')
        H.wait_ok(pg, "(() => { const t = document.querySelector('.dci-panel').getBoundingClientRect().top; return t >= 0 && t <= 20; })()", 15)
        H.wait_still(pg, "scrollY")
        top = pg.evaluate("Math.round(document.querySelector('.dci-panel').getBoundingClientRect().top)")
        print('Seite:', inline, '| ▼ scrollY', y1, 'Ende des Dashboards zum Fensterrand:', foot, '| ▲ Anfang des Dashboards:', top)
        results.append(inline and y1[0] > 200 and -40 <= foot <= 20 and 0 <= top <= 20)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_compacthint():
    """Credits Importer 3.34.23: an arrow at "Compact | Full" (collected item 143). (3.73.0, Z-CPV) The compact view is the default:
    the arrow points to the full view now.
    A) The compact view, nothing stored about the arrow: the dashboard's head shows the arrow below the symbol (its tip below the
       symbol), the text says what the full view is ("Try the full view …"); what lies below it can still be clicked.
    B) The symbol switches to full: the arrow is gone, stored; back to compact and a new page: still gone.
    C) ⚙ Settings → "Reset all settings": the compact view and the arrow are back; ✕ closes it for good (stored), ↺ of Appearance
       brings it back.
    D) (3.73.0) Who used the script before (its storage generation set) and never chose a view: the full view kept, no arrow; a
       browser that never ran the script: the compact view with the arrow; a view chosen before: no arrow."""
    results = []
    HINT = """(() => { const h = document.querySelector('.dci-head .dci-hint-compact'); const b = document.querySelector('.dci-head [data-act=view-toggle]');
      if (!h) return null; const r = h.querySelector('.dci-hint-bubble').getBoundingClientRect(); const br = b.getBoundingClientRect();
      const tip = getComputedStyle(h.querySelector('.dci-hint-bubble'), '::before');
      return { text: h.querySelector('.dci-hint-text').textContent, below: r.top >= br.bottom - 2, near: r.right >= br.left && r.left <= br.right + 40,
        through: getComputedStyle(h).pointerEvents === 'none', tip: tip.content !== 'none' }; })()"""
    VIEW = "document.getElementById('dci-overlay').classList.contains('dci-compact') ? 'compact' : 'full'"
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, view='compact')
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.evaluate("localStorage.removeItem('dci-hint-compact')")
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        a = pg.evaluate(HINT)
        print('A) Pfeil:', a)
        results.append(bool(a) and a['text'].startswith('Try the full view') and a['below'] and a['near'] and a['through'] and a['tip'])
        # B) switched
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        b1 = [pg.evaluate(HINT), pg.evaluate("localStorage.getItem('dci-hint-compact')"), pg.evaluate(VIEW)]
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        b2 = pg.evaluate(HINT)
        pg.close()
        pg, errs2 = H.open_mb_edit(ctx, companion=False, view='compact')
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        b3 = pg.evaluate(HINT)
        print('B) nach dem Umschalten:', b1, '| wieder kompakt:', b2, '| neue Seite:', b3)
        results.append(b1 == [None, 'true', 'full'] and b2 is None and b3 is None)
        # C) reset all settings, ✕, ↺ of Appearance
        H.open_settings(pg)
        pg.click('[data-el=settings] [data-act=reset-open]')
        pg.wait_for_timeout(200)
        pg.click('[data-act=reset-do]')
        pg.wait_for_timeout(2500)
        c1 = [bool(pg.evaluate(HINT)), pg.evaluate(VIEW)]
        pg.click('.dci-head .dci-hint-compact [data-act=hint-compact-close]')
        pg.wait_for_timeout(300)
        c2 = [pg.evaluate(HINT), pg.evaluate("localStorage.getItem('dci-hint-compact')")]
        H.open_settings(pg, 'appearance')
        pg.locator('[data-el=settings] [data-act=settings-reset]').first.evaluate('b => b.click()')
        pg.wait_for_timeout(500)
        c3 = pg.evaluate(HINT)
        print('C) nach „Reset all“:', c1, '| ✕:', c2, '| ↺ Appearance:', bool(c3))
        results.append(c1 == [True, 'compact'] and c2 == [None, 'true'] and bool(c3))
        print('Fehler:', errs + errs2)
        results.append(not errs and not errs2)
        pg.close()
        # D) the default for who used the script before, a new browser, a view chosen before
        d = []
        for init in ("localStorage.setItem('dci-store-epoch', '4')", "", "localStorage.setItem('dci-store-epoch', '4'); localStorage.setItem('dci-view', JSON.stringify('compact'))"):
            c = H.new_context(b)
            if init:
                c.add_init_script(f"if (!localStorage.getItem('dci-view-kept') && !sessionStorage.getItem('t-init')) {{ sessionStorage.setItem('t-init', '1'); {init}; }}")
            if init:
                pg, e3 = H.open_mb_edit(c, companion=False, view=None)
            else:
                # (a browser that never ran the script: none of the harness's presets – they set its storage generation)
                pg = c.new_page()
                e3 = H.errors_of(pg)
                pg.goto(f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
                pg.add_script_tag(content=H.MAIN)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            pg.wait_for_timeout(800)
            d.append([pg.evaluate(VIEW), bool(pg.evaluate(HINT)), not e3])
            # ((review) a second start: the same – the fresh browser stays compact)
            pg.reload()
            pg.add_script_tag(content=H.MAIN)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            pg.wait_for_timeout(800)
            d[-1].append(pg.evaluate(VIEW))
            c.close()
        print('D) vorher benutzt, neu, gewählt:', d)
        results.append(d == [['full', False, True, 'full'], ['compact', True, True, 'compact'], ['compact', False, True, 'compact']])
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_keys():
    """Credits Importer 3.36.3: ⌨ in the head.
    A) ⌨ (before ⤢; until 3.36.4 before ⓘ) opens the shortcuts below the head: the groups (the pages, the release editor, the dashboard, the media
       choice, the window "Text from cover art"), Alt+⇧ Shift+D, Esc, Ctrl+Alt+Enter, Alt+↑ / Alt+↓ … – the keys of this
       computer (Linux here: "Windows, Linux").
    B) Esc closes them (the dashboard stays open), the focus back on ⌨; ⌨ opens them again, ✕ closes them.
    C) As a Mac ("MacIntel"): ⌥ Option, ⌃ Control, ⌘ Command, ↩ Return."""
    KEYS = """(() => { const el = document.querySelector('#dci-overlay [data-el=keys]'); const b = document.querySelector('.dci-head [data-act=keys-open]');
      return { shown: !!el && !el.hidden, expanded: b ? b.getAttribute('aria-expanded') : null, title: b ? b.title : '',
        groups: el ? [...el.querySelectorAll('h3')].map(h => h.textContent.trim()) : [], system: el && el.querySelector('.dci-keys-head .dci-sub') ? el.querySelector('.dci-keys-head .dci-sub').textContent : '',
        keys: el ? [...el.querySelectorAll('tr th[scope=row]')].map(t => t.textContent.replace(/\\s+/g, ' ').trim()) : [] }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.click('.dci-head [data-act=keys-open]')
        pg.wait_for_timeout(300)
        a = pg.evaluate(KEYS)
        print('A)', a)
        results.append(a['shown'] and a['expanded'] == 'true' and a['title'] == 'Keyboard shortcuts' and a['system'] == 'the keys of this computer (Windows, Linux)'
                       and a['groups'] == ['On the pages of MusicBrainz with the script', 'In the release editor (Add release, Edit release)', 'In the dashboard',
                                           'In the media choice', 'In the window “Text from cover art”']
                       and a['keys'][:3] == ['Alt+⇧ Shift+D', 'Esc', 'Ctrl+Alt+Enter'] and 'Alt+↑ / Alt+↓' in a['keys'] and 'Ctrl+mouse wheel' in a['keys'])
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
        b1 = [pg.evaluate(KEYS)['shown'], pg.evaluate("!document.getElementById('dci-overlay').hidden"), pg.evaluate("(document.activeElement || {}).dataset ? document.activeElement.dataset.act : ''")]
        pg.click('.dci-head [data-act=keys-open]')
        pg.wait_for_timeout(200)
        pg.click('#dci-overlay [data-el=keys] .dci-keys-head [data-act=keys-open]')
        pg.wait_for_timeout(200)
        b2 = pg.evaluate(KEYS)
        print('B) Esc:', b1, '| ✕:', b2['shown'], b2['expanded'])
        results.append(b1 == [False, True, 'keys-open'] and b2['shown'] is False and b2['expanded'] == 'false')
        ctx.close()
        ctx = H.new_context(b)
        ctx.add_init_script("Object.defineProperty(navigator, 'platform', { get: () => 'MacIntel' }); try { Object.defineProperty(navigator, 'userAgentData', { get: () => undefined }); } catch (e) {}")
        pg, errs2 = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.click('.dci-head [data-act=keys-open]')
        pg.wait_for_timeout(300)
        c = pg.evaluate(KEYS)
        print('C) Mac:', c['system'], c['keys'])
        results.append(c['system'] == 'the keys of this computer (Mac)' and c['keys'][:3] == ['⌥ Option+⇧ Shift+D', 'Esc', '⌃ Control+⌥ Option+↩ Return']
                       and '⌘ Command+V' in c['keys'] and '⌥ Option+↑ / ⌥ Option+↓' in c['keys'])
        print('Fehler:', errs, errs2)
        results.append(not errs and not errs2)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_anvcredit():
    """Credits Importer 3.37.11: the Discogs spelling as the artist credit in MusicBrainz, in the matrix view (collected item 161).
    A) "Ken Ansell" credited "Kenneth Ansell" on the release: the head "Kenneth Ansell*" with the chip "artist credit in MusicBrainz:
       “Kenneth Ansell” (the Discogs spelling *)"; the field "Artist credit for all roles" has it; the log names it.
    B) The credit emptied in that field: the chip goes (the MusicBrainz name), the * stays (the spelling of the release)."""
    H.ENTRIES_VIEW = 'matrix'
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'].append({'name': 'Ken Ansell', 'anv': 'Kenneth Ansell', 'role': 'Engineer', 'tracks': '', 'id': 1373157, 'join': ''})
        return d

    H.discogs_release = rel
    HEAD = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => (s.querySelector('.dci-gname strong').dataset.name || '') === 'Ken Ansell');
      if (!g) return null; const c = g.querySelector('.dci-gcredit'); const st = g.querySelector('.dci-gname strong');
      return { shown: st.textContent.trim(), chip: c && !c.hidden ? c.textContent.trim() : null, field: (g.querySelector('[data-f=artist-credit-all]') || {}).value }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        a = pg.evaluate(HEAD)
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'Discogs spellings' in x]
        print('A)', a, '| Protokoll:', logs)
        results.append(a == {'shown': 'Kenneth Ansell*', 'chip': 'artist credit in MusicBrainz: “Kenneth Ansell” (the Discogs spelling *)', 'field': 'Kenneth Ansell'}
                       and logs == ['Artist credits from the Discogs spellings (*): Kenneth Ansell (Ken Ansell)'])
        sec = "section.dci-group:has(.dci-gname strong[data-name='Ken Ansell'])"
        pg.fill(f'{sec} [data-f=artist-credit-all]', '')
        pg.click(f'{sec} [data-act=artist-credit-all]')
        pg.wait_for_timeout(500)
        b2 = pg.evaluate(HEAD)
        print('B)', b2)
        results.append(b2 and b2['shown'] == 'Kenneth Ansell*' and b2['chip'] is None)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_spellings():
    """Credits Importer 3.38.11 (collected items 175, 176).
    A) Oliver Lake – Written-By "Lake*" on tracks 1–2, Flute and Soprano Saxophone as "Oliver Lake", Flute on track 3 as "O. Lake*":
       the head "Oliver Lake" (no "Lake*"), the chip "as “Lake” (+1)"; "Artist credit for all roles" empty.
    B) Carl Allen credited "C. Allen*" in all his roles: the head "C. Allen*", the field "C. Allen" (as before).
    C) The matrix of Oliver Lake: a column "Credited as"; flute (empty, the MusicBrainz name), soprano saxophone (empty), flute
       "O. Lake" – a line of its own.
    D) Compact: the chip of that flute "flute as “O. Lake”".
    E) "O. Lake" emptied in its line: the two flute lines join; the chip in the head "as “Lake” for writer" (only the works carry it).
    F) The place Abbey Road Studios: "Credited as for all roles"; "Abbey Road" set for all: its rows credit "Abbey Road" (until 3.38.10
       "Set for all" was taken back at the next check for a linked entry: syncSourceCredits)."""
    H.ENTRIES_VIEW = 'matrix'
    orig = H.discogs_release
    H.ARTISTS[3301] = (H.uid('dddddddd', 3301), 'Oliver Lake')
    H.ARTISTS[3302] = (H.uid('dddddddd', 3302), 'Carl Allen')
    H.attr(9201, 'flute', 14, 14)
    H.attr(9202, 'soprano saxophone', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    ex = lambda name, role, i, anv='', tracks='': {'name': name, 'anv': anv, 'role': role, 'tracks': tracks, 'id': i, 'join': ''}

    def rel():
        d = orig()
        d['extraartists'] += [ex('Oliver Lake', 'Flute', 3301), ex('Oliver Lake', 'Soprano Saxophone', 3301), ex('Carl Allen', 'Drums', 3302, 'C. Allen'),
                              ex('Carl Allen', 'Producer', 3302, 'C. Allen')]
        for i in (0, 1):
            d['tracklist'][i]['extraartists'].append(ex('Oliver Lake', 'Written-By', 3301, 'Lake'))
        d['tracklist'][2]['extraartists'].append(ex('Oliver Lake', 'Flute', 3301, 'O. Lake'))
        return d

    H.discogs_release = rel
    SEC = "(name) => [...document.querySelectorAll('section.dci-group')].find(s => { const st = s.querySelector('.dci-gname strong'); return (st.dataset.name || st.textContent.trim()) === name; })"
    HEAD = """(name) => { const g = (%s)(name); if (!g) return null; const c = g.querySelector('.dci-gcredit'); const st = g.querySelector('.dci-gname strong');
      const f = g.querySelector('[data-f=artist-credit-all]'); return { shown: st.textContent.trim(), chip: c && !c.hidden ? c.textContent.trim() : null,
      field: f ? f.value : null, label: f ? f.closest('label').textContent.replace(/\\s+/g, ' ').trim() : null }; }""" % SEC
    LINES = """(name) => { const g = (%s)(name); if (!g) return null; return { head: [...g.querySelectorAll('.dci-em-grid thead th')].map(t => t.textContent.trim()).filter(Boolean).slice(0, 3),
      lines: [...g.querySelectorAll('tr.dci-em-line')].map(tr => [(tr.querySelector('[data-f=em-primary]') || {}).value, (tr.querySelector('[data-f=em-ac]') || {}).value]) }; }""" % SEC
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        a, b_ = pg.evaluate(HEAD, 'Oliver Lake'), pg.evaluate(HEAD, 'Carl Allen')
        print('A)', a, '\nB)', b_)
        results.append(a and a['shown'] == 'Oliver Lake' and a['chip'] == 'as “Lake” (+1)' and a['field'] == '' and a['label'] == 'Artist credit for all roles')
        results.append(b_ and b_['shown'] == 'C. Allen*' and b_['field'] == 'C. Allen')
        c = pg.evaluate(LINES, 'Oliver Lake')
        print('C)', c)
        results.append(c and c['head'][1:3] == ['Role credit', 'Credited as'] and sorted(c['lines']) == [['flute', ''], ['flute', 'O. Lake'], ['soprano saxophone', '']])
        # D) compact
        pg.click('.dci-head [data-act=view-toggle]'); pg.wait_for_timeout(600)
        chips = pg.evaluate("(name) => { const g = (%s)(name); return g ? [...g.querySelectorAll('.dci-em-chipname')].map(x => x.textContent.replace(/\\s+/g, ' ').trim()) : null; }" % SEC, 'Oliver Lake')
        pg.click('.dci-head [data-act=view-toggle]'); pg.wait_for_timeout(600)
        print('D) kompakt:', chips)
        results.append(bool(chips) and 'flute as “O. Lake”' in chips and 'flute' in chips)
        # E) emptied: the lines join
        sec = "section.dci-group:has(.dci-gname strong:text-is('Oliver Lake'))"
        target = pg.evaluate("(name) => { const g = (%s)(name); return [...g.querySelectorAll('tr.dci-em-line [data-f=em-ac]')].findIndex(x => x.value === 'O. Lake'); }" % SEC, 'Oliver Lake')
        f = pg.locator(f'{sec} tr.dci-em-line [data-f=em-ac]').nth(target)
        f.fill('')
        f.press('Tab')
        pg.wait_for_timeout(600)
        e = pg.evaluate(LINES, 'Oliver Lake')
        e2 = pg.evaluate(HEAD, 'Oliver Lake')
        print('E) geleert:', e, '| Kopf:', e2)
        results.append(e and sorted(e['lines']) == [['flute', ''], ['soprano saxophone', '']] and e2['shown'] == 'Oliver Lake' and e2['chip'] == 'as “Lake” for writer')
        # F) the place
        fa = pg.evaluate(HEAD, 'Abbey Road Studios')
        psec = "section.dci-group:has(.dci-gname strong:text-is('Abbey Road Studios'))"
        pg.fill(f'{psec} [data-f=artist-credit-all]', 'Abbey Road')
        pg.click(f'{psec} [data-act=artist-credit-all]')
        pg.wait_for_timeout(500)
        fb = pg.evaluate("(name) => { const g = (%s)(name); return [...g.querySelectorAll('[data-f=em-ac], [data-f=credit]')].map(x => x.value); }" % SEC, 'Abbey Road Studios')
        print('F) Ort:', fa, '→', fb)
        results.append(fa and fa['label'] == 'Credited as for all roles' and fa['field'] == '' and fb and set(fb) == {'Abbey Road'})
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_blockac():
    """Credits Importer 3.40.3 (collected item Z-AK; Q-ak – Q-aq): "Credited as" in the head of a block of the entries matrix.
    A) Oliver Lake – Flute and Soprano Saxophone as "Oliver Lake", Flute on track 3 as "O. Lake": the head of his instruments (three
       lines) has the field, empty with "several" and the spellings in its tooltip; Carl Allen (drums, producer – a role each block):
       none.
    B) "Lake" + Enter: every line "Lake" – the two flutes join –, the field "Lake"; the message "Credited as “Lake” for 2 roles of
       Oliver Lake" with ↶ Undo.
    C) ↶ Undo: the spellings back (flute, flute "O. Lake", soprano saxophone).
    D) "Lake" again, then a line changed by hand ("Ollie" for soprano saxophone): it keeps its own, the field "several" again;
       (review) the older ↶ then: the flutes get their spellings back, "Ollie" stays; emptied in the head (typed in, cleared, Enter):
       every line the MusicBrainz name ("Credited as the MusicBrainz name for 2 roles of Oliver Lake"), the focus in the field again.
    E) Compact: no field, the chips with their "as …" ("flute as “Lake”", "soprano saxophone as “Ollie”"; Q-an)."""
    H.ENTRIES_VIEW = 'matrix'
    orig = H.discogs_release
    H.ARTISTS[3301] = (H.uid('dddddddd', 3301), 'Oliver Lake')
    H.ARTISTS[3302] = (H.uid('dddddddd', 3302), 'Carl Allen')
    H.attr(9201, 'flute', 14, 14)
    H.attr(9202, 'soprano saxophone', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    ex = lambda name, role, i, anv='', tracks='': {'name': name, 'anv': anv, 'role': role, 'tracks': tracks, 'id': i, 'join': ''}

    def rel():
        d = orig()
        d['extraartists'] += [ex('Oliver Lake', 'Flute', 3301), ex('Oliver Lake', 'Soprano Saxophone', 3301), ex('Carl Allen', 'Drums', 3302, 'C. Allen'),
                              ex('Carl Allen', 'Producer', 3302, 'C. Allen')]
        d['tracklist'][2]['extraartists'].append(ex('Oliver Lake', 'Flute', 3301, 'O. Lake'))
        return d

    H.discogs_release = rel
    SEC = "(name) => [...document.querySelectorAll('section.dci-group')].find(s => { const st = s.querySelector('.dci-gname strong'); return (st.dataset.name || st.textContent.trim()) === name; })"
    STATE = """(name) => { const g = (%s)(name); if (!g) return null; const f = [...g.querySelectorAll('[data-f=em-bac]')];
      return { fields: f.map(x => [x.value, x.placeholder, x.title.split('\\n').pop()]),
        lines: [...g.querySelectorAll('tr.dci-em-line')].map(tr => [(tr.querySelector('[data-f=em-primary]') || {}).value, (tr.querySelector('[data-f=em-ac]') || {}).value]).sort(),
        msg: [...document.querySelectorAll('[data-act=em-undo]')].map(x => x.closest('.dci-msg').textContent.replace(/\\s+/g, ' ').trim()) }; }""" % SEC
    sec = "section.dci-group:has(.dci-gname strong:text-is('Oliver Lake'))"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        a = pg.evaluate(STATE, 'Oliver Lake')
        ca = pg.evaluate(STATE, 'Carl Allen')
        print('A)', a, '| Carl Allen:', ca and ca['fields'])
        results.append(a and a['fields'] == [['', 'several', 'Several spellings in this block: Oliver Lake, “O. Lake”']]
                       and a['lines'] == [['flute', ''], ['flute', 'O. Lake'], ['soprano saxophone', '']] and ca and ca['fields'] == [])
        f = pg.locator(f'{sec} [data-f=em-bac]')
        f.fill('Lake')
        f.press('Enter')
        pg.wait_for_timeout(600)
        bb = pg.evaluate(STATE, 'Oliver Lake')
        print('B) Lake:', bb)
        results.append(bb and bb['lines'] == [['flute', 'Lake'], ['soprano saxophone', 'Lake']] and bb['fields'][0][0] == 'Lake'
                       and bb['msg'] and bb['msg'][-1].startswith('Credited as “Lake” for 2 roles of Oliver Lake') and bb['msg'][-1].endswith('↶ Undo'))
        pg.locator('[data-act=em-undo]').last.click()
        pg.wait_for_timeout(600)
        c = pg.evaluate(STATE, 'Oliver Lake')
        print('C) Undo:', c)
        results.append(c and c['lines'] == [['flute', ''], ['flute', 'O. Lake'], ['soprano saxophone', '']] and c['fields'][0][1] == 'several' and not c['msg'])
        f = pg.locator(f'{sec} [data-f=em-bac]')
        f.fill('Lake')
        f.press('Tab')
        pg.wait_for_timeout(600)
        i = pg.evaluate("(name) => { const g = (%s)(name); return [...g.querySelectorAll('tr.dci-em-line')].findIndex(tr => tr.querySelector('[data-f=em-primary]').value === 'soprano saxophone'); }" % SEC, 'Oliver Lake')
        lf = pg.locator(f'{sec} tr.dci-em-line').nth(i).locator('[data-f=em-ac]')
        lf.fill('Ollie')
        lf.press('Tab')
        pg.wait_for_timeout(600)
        d1 = pg.evaluate(STATE, 'Oliver Lake')
        # E) compact: no field, each chip with its "as …" (Q-an)
        pg.click('.dci-head [data-act=view-toggle]'); pg.wait_for_timeout(600)
        e = pg.evaluate("(name) => { const g = (%s)(name); return g ? [g.querySelectorAll('[data-f=em-bac]').length, [...g.querySelectorAll('.dci-em-chipname')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())] : null; }" % SEC, 'Oliver Lake')
        pg.click('.dci-head [data-act=view-toggle]'); pg.wait_for_timeout(600)
        # (review) the older ↶ after a change in a line: the flutes get their spellings back, the line changed by hand keeps "Ollie"
        pg.locator('[data-act=em-undo]').last.click()
        pg.wait_for_timeout(600)
        d1u = pg.evaluate(STATE, 'Oliver Lake')
        # emptied in the head – "several" shown empty: typed in and cleared, Enter
        f = pg.locator(f'{sec} [data-f=em-bac]')
        f.fill('x')
        f.fill('')
        f.press('Enter')
        pg.wait_for_timeout(600)
        d2 = pg.evaluate(STATE, 'Oliver Lake')
        focus = pg.evaluate("document.activeElement && document.activeElement.dataset.f")
        print('D) eine Zeile von Hand:', d1, '\n   älteres Undo danach:', d1u, '\n   geleert:', d2, '| Fokus:', focus, '\nE) kompakt:', e)
        results.append(d1 and d1['lines'] == [['flute', 'Lake'], ['soprano saxophone', 'Ollie']] and d1['fields'][0][:2] == ['', 'several']
                       and d1u and d1u['lines'] == [['flute', ''], ['flute', 'O. Lake'], ['soprano saxophone', 'Ollie']]
                       and d2 and d2['lines'] == [['flute', ''], ['soprano saxophone', '']] and d2['msg'] and d2['msg'][-1].startswith('Credited as the MusicBrainz name for 2 roles of Oliver Lake')
                       and focus == 'em-bac')
        results.append(e and e[0] == 0 and 'flute as “Lake”' in e[1] and 'soprano saxophone as “Ollie”' in e[1])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_copyname():
    """Credits Importer 3.40.7 (collected item Z-CP; Q-av, Q-aw): ⧉ next to the name of an entry without a MusicBrainz entry chosen.
    A) After the import: ⧉ at every entry not linked (also companies and places), none shown at those linked; its tooltip names it.
    B) A click: the name of the source in the clipboard (without Discogs's number), "✓" for a moment; the symbols drawn by CSS –
       the text of the head stays the name (the other test files read it).
    C) A pasted text: its names only suggested – ⧉ still shown (a suggestion is not a chosen entry); one suggestion chosen: its ⧉ goes.
    D) (3.40.8, review) The browser's clipboard refuses: copied through a selected text (as "Copy" of the log) – ✓; that refused
       too: ⚠, the tooltip and the label say so, then ⧉ again."""
    results = []
    STATE = """(() => [...document.querySelectorAll('section.dci-group')].map(g => { const b = g.querySelector('.dci-gname .dci-copyname');
      return [g.querySelector('.dci-gname strong').textContent.trim(), (g.className.match(/dci-st-(\\w+)/) || [])[1], b ? !b.hidden : null, b ? b.dataset.name : '', b ? b.title : '']; }))()"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://musicbrainz.org')
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(800)
        a = pg.evaluate(STATE)
        linked = [x for x in a if x[1] in ('linked', 'manual')]
        open_ = [x for x in a if x[1] not in ('linked', 'manual')]
        print('A) verknüpft:', [(x[0], x[2]) for x in linked], '\n   ohne:', [(x[0], x[1], x[2], x[3]) for x in open_])
        results.append(bool(linked) and bool(open_) and all(x[2] is False for x in linked) and all(x[2] is True and x[3] == x[0].rstrip('*') for x in open_)
                       and all(x[4].startswith(f'Copy “{x[3]}”') for x in open_))
        name = open_[0][0]
        sec = f"section.dci-group:has(.dci-gname strong:text-is('{name}'))"
        pg.locator(f'{sec} .dci-gname .dci-copyname').click()
        pg.wait_for_timeout(200)
        clip = pg.evaluate("navigator.clipboard.readText()")
        mark = pg.locator(f'{sec} .dci-gname .dci-copyname').evaluate("b => getComputedStyle(b, '::before').content.replace(/\"/g, '')")
        pg.wait_for_timeout(1800)
        back = pg.locator(f'{sec} .dci-gname .dci-copyname').evaluate("b => getComputedStyle(b, '::before').content.replace(/\"/g, '')")
        head = pg.locator(f'{sec} .dci-gname').evaluate("g => g.textContent.replace(/\\s+/g, ' ').trim()")
        print('B) kopiert:', name, '→', repr(clip), '| Zeichen:', mark, '→', back, '| Text des Kopfs:', repr(head))
        results.append(clip == open_[0][3] and mark == '✓' and back == '⧉' and '⧉' not in head and '✓' not in head)
        # C) a pasted text: names are only suggested, a suggestion is not a chosen entry; once chosen, its ⧉ goes
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Bass Man: bass\nNobody Known: guitar')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(800)
        c0 = {x[0]: x for x in pg.evaluate(STATE)}
        bm = pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(g => g.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man').dataset.group")
        pg.click(f'section[data-group="{bm}"] [data-act=name-use]')
        pg.wait_for_timeout(500)
        c1 = {x[0]: x for x in pg.evaluate(STATE)}
        print('C) vorher:', {k: c0[k][1:3] for k in ('Bass Man', 'Nobody Known') if k in c0}, '| nach der Wahl:', {k: c1[k][1:3] for k in ('Bass Man', 'Nobody Known') if k in c1})
        results.append('Bass Man' in c0 and c0['Bass Man'][2] is True and c0.get('Nobody Known', [0, 0, None])[2] is True
                       and c1['Bass Man'][1] == 'manual' and c1['Bass Man'][2] is False and c1['Nobody Known'][2] is True)
        # D) the clipboard refuses
        nk = "section.dci-group:has(.dci-gname strong:text-is('Nobody Known')) .dci-gname .dci-copyname"
        SYMS = "b => [getComputedStyle(b, '::before').content.replace(/\"/g, ''), b.title, b.getAttribute('aria-label')]"
        pg.evaluate("""() => { navigator.clipboard.writeText = () => Promise.reject(new Error('no'));
          window.__copied = []; document.execCommand = (c) => { window.__copied.push(document.activeElement && document.activeElement.value); return window.__copyOk; }; window.__copyOk = true; }""")
        pg.locator(nk).click()
        pg.wait_for_timeout(200)
        d1 = pg.locator(nk).evaluate(SYMS) + [pg.evaluate('window.__copied')]
        pg.wait_for_timeout(1700)
        pg.evaluate('window.__copyOk = false')
        pg.locator(nk).click()
        pg.wait_for_timeout(200)
        d2 = pg.locator(nk).evaluate(SYMS)
        pg.wait_for_timeout(3200)
        d3 = pg.locator(nk).evaluate(SYMS)
        print('D) über markierten Text:', d1, '\n   abgelehnt:', d2, '\n   danach:', d3)
        results.append(d1[0] == '✓' and d1[3] == ['Nobody Known'] and d1[1] == 'Copied: “Nobody Known”' and d1[2] == d1[1]
                       and d2[0] == '⚠' and d2[1] == 'The browser did not allow copying “Nobody Known”' and d2[2] == d2[1]
                       and d3[0] == '⧉' and d3[1].startswith('Copy “Nobody Known”') and d3[2] == d3[1])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_headnarrow():
    """Credits Importer 3.40.8 (review of block BA, Z-HB): the symbols of the head in a narrow dashboard – one line while they fit
    (1500 and 600 px), two lines at 400 px with ✕ inside the dashboard (until 3.40.7 it was pushed out of it)."""
    results = []
    HEAD = """(() => { const panel = document.querySelector('#dci-overlay .dci-panel').getBoundingClientRect();
      const x = document.querySelector('.dci-head [data-act=close]').getBoundingClientRect();
      const lines = new Set([...document.querySelectorAll('.dci-head-tools > button')].map(b => Math.round(b.getBoundingClientRect().top))).size;
      return { inside: x.right <= panel.right + 0.5 && x.left >= panel.left, lines }; })()"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        out = {}
        for w in (1500, 600, 400):
            pg.set_viewport_size({'width': w, 'height': 900})
            pg.wait_for_timeout(500)
            out[w] = pg.evaluate(HEAD)
        print('Kopf:', out, '| Fehler:', errs)
        results.append(out[1500] == {'inside': True, 'lines': 1} and out[600] == {'inside': True, 'lines': 1} and out[400]['inside'] and out[400]['lines'] == 2)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_capsnames():
    """Credits Importer 3.38.12 (F-4, rule S060).
    A) Discogs credits "TORBEN SNEKKESTAD" (Saxophone), "DJ SHADOW" (Scratches), "ABBA" (linked: MusicBrainz "ABBA"), Oliver Lake
       credited "LAKE": the heads "Torben Snekkestad" with "↺ in capitals", "DJ Shadow", "ABBA" (MusicBrainz's spelling, no button),
       "Lake*" credited "Lake" (all its roles carry it); the log "Names in capitals written in normal case (5): …" (the spellings too).
    B) "↺ in capitals" at Torben Snekkestad: the head "TORBEN SNEKKESTAD", "↺ normal case", its line credited "TORBEN SNEKKESTAD"; once
       more: "Torben Snekkestad", credited as empty again (the MusicBrainz name).
    C) Oliver Lake credited "LAKE" (head "Lake*"): "↺ in capitals" too – "LAKE*", credited "LAKE"; "DOOM" linked to MusicBrainz "MF
       DOOM" (all in capitals): the head "MF DOOM", no ↺, credited "DOOM"; a "credited as" typed by hand ("T. S.") stays at "↺ in
       capitals".
    D) In Node, personCase ([Q-a], [Q-b] 3.38.14): "AL DI MEOLA" → "Al di Meola", "DJ SHADOW" → "DJ Shadow", "MC SOLAAR" → "MC
       Solaar", "MF DOOM" → "MF Doom", "PACO DE LUCÍA" → "Paco de Lucía", "DE LA SOUL" → "De la Soul", "ED O'BRIEN" → "Ed O'Brien",
       "J. DOE" → "J. Doe", "BMS" stays, "Go KUROSAWA" → "Go Kurosawa" (normal case beside: two letters stay as they are)."""
    H.ENTRIES_VIEW = 'matrix'
    orig = H.discogs_release
    H.ARTISTS[3401] = (H.uid('dddddddd', 3401), 'ABBA')
    H.ARTISTS[3405] = (H.uid('dddddddd', 3405), 'MF DOOM')
    H.attr(9203, 'scratches', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    ex = lambda name, role, i, anv='': {'name': name, 'anv': anv, 'role': role, 'tracks': '', 'id': i, 'join': ''}

    def rel():
        d = orig()
        d['extraartists'] += [ex('TORBEN SNEKKESTAD', 'Saxophone', 3402), ex('DJ SHADOW', 'Scratches', 3403), ex('ABBA', 'Vocals', 3401),
                              ex('Oliver Lake', 'Saxophone', 3404, 'LAKE'), ex('DOOM', 'Vocals', 3405)]
        return d

    H.discogs_release = rel
    SEC = "(name) => [...document.querySelectorAll('section.dci-group')].find(s => { const st = s.querySelector('.dci-gname strong'); return [st.dataset.name, st.textContent.trim()].includes(name); })"
    HEAD = """(name) => { const g = (%s)(name); if (!g) return null; const b = g.querySelector('[data-act=case-back]');
      return { shown: g.querySelector('.dci-gname strong').textContent.trim(), btn: b ? b.textContent.trim() : null, title: b ? b.title : null,
        ac: [...g.querySelectorAll('[data-f=em-ac]')].map(x => x.value) }; }""" % SEC
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
        a = {n: pg.evaluate(HEAD, n) for n in ('Torben Snekkestad', 'DJ Shadow', 'ABBA', 'Oliver Lake')}
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'normal case' in x]
        for k, v in a.items():
            print('A)', k, v)
        print('   Protokoll:', logs)
        ok_a = a['Torben Snekkestad'] and a['Torben Snekkestad']['shown'] == 'Torben Snekkestad' and a['Torben Snekkestad']['btn'] == '↺ in capitals' \
            and a['Torben Snekkestad']['title'].startswith('The source writes “TORBEN SNEKKESTAD”') and a['Torben Snekkestad']['ac'] == [''] \
            and a['DJ Shadow'] and a['DJ Shadow']['shown'] == 'DJ Shadow' and a['ABBA'] and a['ABBA']['shown'] == 'ABBA' and a['ABBA']['btn'] is None and a['ABBA']['ac'] == [''] \
            and a['Oliver Lake'] and a['Oliver Lake']['ac'] == ['Lake'] \
            and logs == ['Names in capitals written in normal case (5): TORBEN SNEKKESTAD → Torben Snekkestad, DJ SHADOW → DJ Shadow, ABBA → Abba, LAKE → Lake, DOOM → Doom – “↺ in capitals” at the entry takes the spelling of the source']
        results.append(bool(ok_a))
        sec = "section.dci-group:has(.dci-gname strong:text-is('Torben Snekkestad'))"
        pg.click(f'{sec} [data-act=case-back]')
        pg.wait_for_timeout(600)
        b1 = pg.evaluate(HEAD, 'TORBEN SNEKKESTAD')
        sec2 = "section.dci-group:has(.dci-gname strong:text-is('TORBEN SNEKKESTAD'))"
        pg.click(f'{sec2} [data-act=case-back]')
        pg.wait_for_timeout(600)
        b2 = pg.evaluate(HEAD, 'Torben Snekkestad')
        print('B) in Großbuchstaben:', b1, '| zurück:', b2)
        results.append(b1 and b1['shown'] == 'TORBEN SNEKKESTAD' and b1['btn'] == '↺ normal case' and b1['ac'] == ['TORBEN SNEKKESTAD']
                       and b2 and b2['shown'] == 'Torben Snekkestad' and b2['btn'] == '↺ in capitals' and b2['ac'] == [''])
        # C) [3.38.12] (review) a spelling in capitals ("LAKE"): ↺ too; "DOOM" linked to MusicBrainz "MF DOOM": its spelling, credited
        #    "DOOM"; a "credited as" typed by hand stays at "↺ in capitals"
        lsec = "section.dci-group:has(.dci-gname strong[data-name='Oliver Lake'])"
        c0 = pg.evaluate(HEAD, 'Oliver Lake')
        pg.click(f'{lsec} [data-act=case-back]'); pg.wait_for_timeout(600)
        c1 = pg.evaluate(HEAD, 'Oliver Lake')
        pg.click(f'{lsec} [data-act=case-back]'); pg.wait_for_timeout(600)
        doom = pg.evaluate(HEAD, 'MF DOOM')
        acf = pg.locator(f'{sec} [data-f=em-ac]').first
        acf.fill('T. S.'); acf.press('Tab'); pg.wait_for_timeout(500)
        pg.click(f'{sec} [data-act=case-back]'); pg.wait_for_timeout(600)
        c2 = pg.evaluate(HEAD, 'TORBEN SNEKKESTAD')
        pg.click(f"section.dci-group:has(.dci-gname strong:text-is('TORBEN SNEKKESTAD')) [data-act=case-back]"); pg.wait_for_timeout(600)
        print('C) LAKE:', c0, '→', c1, '| DOOM:', doom, '| von Hand:', c2)
        results.append(c0 and c0['btn'] == '↺ in capitals' and c0['title'].startswith('The source writes “LAKE”') and c0['ac'] == ['Lake']
                       and c1 and c1['shown'] == 'LAKE*' and c1['ac'] == ['LAKE'] and c1['btn'] == '↺ normal case' and c1['title'] == 'Back to normal case: “Lake”'
                       and doom and doom['shown'] == 'MF DOOM' and doom['btn'] is None and doom['ac'] == ['DOOM']
                       and c2 and c2['ac'] == ['T. S.'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    # D) [Q-a], [Q-b] (3.38.14) personCase in Node
    import json
    import subprocess
    NAMES = ['AL DI MEOLA', 'DJ SHADOW', 'MC SOLAAR', 'MF DOOM', 'PACO DE LUCÍA', 'DE LA SOUL', "ED O'BRIEN", 'J. DOE', 'BMS', 'Go KUROSAWA']
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
console.log(JSON.stringify(JSON.parse(process.argv[2]).map((n) => m.personCase(n))));
"""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(NAMES)], capture_output=True, text=True)
    got = json.loads(js.stdout) if not js.returncode else js.stderr[-500:]
    print('D) personCase:', got)
    results.append(got == ['Al di Meola', 'DJ Shadow', 'MC Solaar', 'MF Doom', 'Paco de Lucía', 'De la Soul', "Ed O'Brien", 'J. Doe', 'BMS', 'Go Kurosawa'])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_poolbar():
    """Credits Importer 3.37.15 (collected items 165, 166).
    A) "▲ fold" of "Dates & tracks" is in its head (no longer at its foot below the matrix); folded it reads "▼ show" at the same
       place (±1 px); the foot keeps "keep the pools in the bar when folded". [178] (3.38.13) The head is the last line of the block
       (open and folded), "▲ fold" / "▼ show" in its middle (±2 px), the arrow at the title ▲ open, ▼ folded (until 3.38.12 the head
       at the top, the fold right after the title, the arrow ▶ turned); after a click on it the focus is on it again.
    B) The date pool folded ("▸ Date pool (n)"): "+ New date" is in its bar; it opens the form below, the pool stays folded; a date
       saved there is counted. The track pool folded: "+ New track group" in its bar.
    A0) While suggestions of this import wait ("not applied yet"), the date pool folds at the first click (until 3.37.14 the
       first click did nothing visible, the second folded it).
    C) "Dates & tracks" folded with the pools kept in the bar: both pools there with "+ New date" / "+ New track group"; "+ New
       date" opens "Dates & tracks" with the form, "Cancel" folds it again."""
    HEAD = """(() => { const h = document.querySelector('.dci-pools-head .dci-pools-fold'); const t = document.querySelector('.dci-pools-toggle');
      const line = document.querySelector('.dci-pools-head'); const c = (e) => { const x = e.getBoundingClientRect(); return Math.round(x.left + x.width / 2); };
      return { head: h ? [h.textContent.trim(), h.getAttribute('aria-expanded'), Math.round(h.getBoundingClientRect().left)] : null,
        middle: h && line ? Math.abs(c(h) - c(line)) : null, last: !!(line && line === line.parentElement.lastElementChild),
        chev: t ? t.querySelector('.dci-chev').textContent.trim() : null, foot: document.querySelectorAll('.dci-pools-foot .dci-pools-fold').length,
        keep: !!document.querySelector('.dci-pools-foot [data-f=pools-keep]'), open: t ? t.getAttribute('aria-expanded') : null,
        focus: !!(document.activeElement && document.activeElement.classList.contains('dci-pools-fold')) }; })()"""
    BARS = """(() => [...document.querySelectorAll('.dci-dates-bar')].map(b => ({ cls: b.className, label: (b.querySelector('.dci-pool-label') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim(),
      kept: !!b.closest('.dci-pools-kept'), add: [...b.querySelectorAll('[data-act=pool-new], [data-act=tg-new], [data-f=tg-new-pick]')].map(x => x.dataset.act || x.dataset.f) })))()"""
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
        if pg.evaluate(HEAD)['open'] != 'true':
            pg.click('.dci-pools-toggle')
            pg.wait_for_timeout(300)
        # A0) the date pool, open for the suggestions of this import, folds at the first click
        forced = pg.evaluate("document.querySelector('.dci-pools-head').textContent.includes('not applied yet')")
        pg.click('[data-act=pool-fold][data-pool=dates]')
        pg.wait_for_timeout(300)
        f1 = pg.evaluate("!!document.querySelector('.dci-pools-body .dci-pool-dates.dci-pool-folded')")
        pg.click('[data-act=pool-fold][data-pool=dates]')
        pg.wait_for_timeout(300)
        f2 = pg.evaluate("!!document.querySelector('.dci-pools-body .dci-pool-dates.dci-pool-folded')")
        print('A0) Vorschläge offen:', forced, '| ein Klick eingeklappt:', f1, '| wieder offen:', not f2)
        results.append(forced and f1 and not f2)
        a0 = pg.evaluate(HEAD)
        pg.click('.dci-pools-head .dci-pools-fold')
        pg.wait_for_timeout(300)
        a1 = pg.evaluate(HEAD)
        pg.click('.dci-pools-head .dci-pools-fold')
        pg.wait_for_timeout(300)
        a2 = pg.evaluate(HEAD)
        print('A) offen:', a0, '| eingeklappt:', a1, '| wieder offen:', a2)
        # [178] (3.38.13) the line at the bottom of the block, "▲ fold" / "▼ show" in its middle, the arrow ▲ open, ▼ folded
        results.append(bool(a0['head']) and a0['head'][:2] == ['▲ fold', 'true'] and a0['last'] and a0['middle'] <= 2 and a0['chev'] == '▲' and a0['foot'] == 0 and a0['keep']
                       and a1['head'][:2] == ['▼ show', 'false'] and abs(a1['head'][2] - a0['head'][2]) <= 1 and a1['last'] and a1['middle'] <= 2 and a1['chev'] == '▼'
                       and a1['open'] == 'false' and a2['head'][:2] == ['▲ fold', 'true'] and a1['focus'] and a2['focus'])
        # B) a pool folded
        n0 = pg.evaluate("document.querySelectorAll('.dci-pools-body .dci-pchip-date').length")
        pg.click('[data-act=pool-fold][data-pool=dates]')
        pg.wait_for_timeout(300)
        b0 = [x for x in pg.evaluate(BARS) if not x['kept']]
        pg.click('.dci-pools-body .dci-pool-folded [data-act=pool-new]')
        pg.wait_for_timeout(300)
        form = pg.locator('[data-f=pf-by]').count()
        still = pg.evaluate("!!document.querySelector('.dci-pools-body .dci-pool-dates.dci-pool-folded')")
        pg.fill('[data-f=pf-by]', '1999')
        pg.click('[data-act=pool-save]')
        pg.wait_for_timeout(300)
        b1 = [x for x in pg.evaluate(BARS) if not x['kept']]
        pg.click('[data-act=pool-fold][data-pool=tracks]')
        pg.wait_for_timeout(300)
        b2 = [x for x in pg.evaluate(BARS) if not x['kept']]
        print('B) Daten eingeklappt:', b0, '| Formular:', form, still, '| gespeichert:', b1, '| Tracks eingeklappt:', b2)
        dates = lambda bars: next((x for x in bars if 'dci-pool-dates' in x['cls']), {})
        tracks = lambda bars: next((x for x in bars if 'dci-tracks-bar' in x['cls']), {})
        results.append('dci-pool-folded' in dates(b0).get('cls', '') and dates(b0).get('add') == ['pool-new'] and form == 1 and still
                       and dates(b1).get('label') == f'▸ Date pool ({n0 + 1})' and 'dci-pool-folded' in tracks(b2).get('cls', '')
                       and tracks(b2).get('add') in (['tg-new'], ['tg-new-pick']))
        pg.click('[data-act=pool-fold][data-pool=dates]')
        pg.click('[data-act=pool-fold][data-pool=tracks]')
        pg.wait_for_timeout(300)
        # C) all folded, the pools kept in the bar
        if not pg.is_checked('[data-f=pools-keep]'):
            pg.check('[data-f=pools-keep]')
        pg.click('.dci-pools-head .dci-pools-fold')
        pg.wait_for_timeout(300)
        c0 = [x for x in pg.evaluate(BARS) if x['kept']]
        pg.click('.dci-pools-kept .dci-pool-dates [data-act=pool-new]')
        pg.wait_for_timeout(300)
        c1 = pg.evaluate("[!!document.querySelector('.dci-pools-body'), document.querySelectorAll('[data-f=pf-by]').length, document.activeElement && document.activeElement.dataset.f]")
        pg.click('[data-act=pool-cancel]')
        pg.wait_for_timeout(300)
        c2 = pg.evaluate("[!!document.querySelector('.dci-pools-body'), !!document.querySelector('.dci-pools-kept')]")
        print('C) Leiste:', c0, '| + New date:', c1, '| Cancel:', c2)
        results.append(dates(c0).get('add') == ['pool-new'] and tracks(c0).get('add') in (['tg-new'], ['tg-new-pick'])
                       and c1 == [True, 1, 'pf-by'] and c2 == [False, True])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_launchtools():
    """Credits Importer 3.40.14 (collected item Z-LS; Q-bz): Log | Statistics · ⚙ as symbols next to "Import credits …".
    A) Without the companion: after "Import credits …", ([Z-QSP] 3.75.0) the profile and "Window | Page" three buttons with a symbol and no word – Log (until 3.40.13
       the word "Log"), a line, Statistics, ⚙ – their names as label and tooltip; the bar below (navigation) hidden.
    B) Log: the log shown and hidden, the button pressed while it is shown (as the one of the dashboard's head).
    C) Statistics: the dashboard opens with the statistics, the import not started ("Only the statistics are open – …", "Start
       import"), the focus on their heading.
    D) ⚙ (the dashboard open): ⚙ Settings open, the statistics closed, the message "Only the settings are open – …"; the dashboard
       closed, ⚙ again: open with the settings, one message only.
    E) "Start import": the import runs."""
    BAR = """(() => { const t = document.querySelector('#dci-launcher .dci-launch-tools'); if (!t) return null;
      const kids = [...t.children].map(e => e.id || e.className); const btns = [...t.querySelectorAll('button')];
      const all = [...document.querySelectorAll('#dci-launcher > *')].map(e => e.id || e.className.split(' ').slice(-1)[0]);
      return { kids, all, svg: btns.map(b => !!b.querySelector('svg.dci-ico')), text: btns.map(b => b.textContent.trim()), label: btns.map(b => b.getAttribute('aria-label')),
        title: btns.map(b => b.title.slice(0, 24)), controls: document.getElementById('dci-controls').hidden }; })()"""
    STATE = """(() => { const o = document.getElementById('dci-overlay'); const st = document.querySelector('[data-el=stats]'), se = document.querySelector('[data-el=settings]');
      return { open: !!o && !o.hidden, stats: !!st && !st.hidden, settings: !!se && !se.hidden, msgs: [...document.querySelectorAll('[data-el=msgs] .dci-msg')].map(m => m.textContent.replace(/\\s+/g, ' ').trim().slice(0, 60)),
        focus: document.activeElement && (document.activeElement.dataset.act || document.activeElement.id), rows: document.querySelectorAll('tr.dci-row').length }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.wait_for_timeout(500)
        a0 = pg.evaluate(BAR)
        print('A)', a0)
        results.append(a0 is not None and a0['kids'] == ['dci-log-open', 'dci-launch-sep', 'dci-stats-open', 'dci-set-open'] and a0['all'][:5] == ['dci-open', 'dci-open-ocr', 'dci-profile', 'dci-place-seg', 'dci-launch-tools']
                       and a0['svg'] == [True, True, True] and a0['text'] == ['', '', ''] and a0['label'] == ['Log', 'Statistics', 'Settings']
                       and a0['title'][1].startswith('Statistics:') and a0['title'][2].startswith('All settings') and a0['controls'] is True)
        PRESSED = "document.getElementById('dci-log-open').getAttribute('aria-pressed')"
        LOGVIS = "(l => !!l && !l.hidden)(document.getElementById('dci-log'))"
        pg.click('#dci-log-open'); pg.wait_for_timeout(300)
        b0 = [pg.evaluate(LOGVIS), pg.evaluate(PRESSED)]
        pg.click('#dci-log-open'); pg.wait_for_timeout(300)
        b1 = [pg.evaluate(LOGVIS), pg.evaluate(PRESSED)]
        print('B) an:', b0, '| aus:', b1)
        results.append(b0 == [True, 'true'] and b1 == [False, 'false'])
        pg.click('#dci-stats-open'); pg.wait_for_timeout(800)
        c0 = pg.evaluate(STATE)
        print('C)', c0)
        results.append(c0['open'] and c0['stats'] and not c0['settings'] and c0['msgs'] and c0['msgs'][0].startswith('Only the statistics are open')
                       and c0['focus'] == 'stats-fold' and c0['rows'] == 0)
        # (the window of the dashboard over the bar)
        pg.locator('#dci-set-open').evaluate('b => b.click()'); pg.wait_for_timeout(500)
        d0 = pg.evaluate(STATE)
        pg.locator('#dci-overlay .dci-head [data-act=close]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
        pg.locator('#dci-set-open').evaluate('b => b.click()'); pg.wait_for_timeout(600)
        d1 = pg.evaluate(STATE)
        print('D) ⚙:', d0, '\n   zu, ⚙:', d1)
        results.append(d0['open'] and d0['settings'] and not d0['stats'] and d0['msgs'] and d0['msgs'][0].startswith('Only the settings are open')
                       and d1['open'] and d1['settings'] and len(d1['msgs']) == 1 and d1['rows'] == 0)
        pg.click('[data-el=msgs] [data-act=start-import]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Checks complete/.test(li.textContent))", 60)
        e0 = pg.evaluate(STATE)
        print('E) Zeilen:', e0['rows'])
        results.append(e0['rows'] > 0)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_focusfields():
    """Credits Importer 3.72.0 (collected item Z-TST): the former smoke/t_focus.py (until 3.71.0 compared with an old log), with its
    checks: typing slowly into a field keeps the focus there while the dashboard redraws – the date of a row (year, month, day),
    the date of a matrix column (its ▾ menu), the date of a matrix cell (its menu: 8 fields), the field "Find dates"."""
    def check(pg, label, sel, text, scope=None):
        loc = (scope or pg).locator(sel).first
        loc.click()
        pg.keyboard.type(text, delay=120)
        pg.wait_for_timeout(1800)
        st = pg.evaluate("""() => { const a = document.activeElement; return { f: a && a.dataset ? a.dataset.f : a && a.tagName, v: a && a.value }; }""")
        ok = st['v'] is not None and text in str(st['v'])
        print(f'{"OK " if ok else "FEHLER"} {label}: aktiv={st["f"]} Wert={st["v"]!r}')
        return ok

    # (with the script's own gap, as before: the lookups in the background still run while it types)
    H.MAIN = H.MAIN_SLOW
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        H.open_discogs(ctx)
        pg, errs = H.open_mb_edit(ctx)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)

        def row(name):
            return pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text=name)).first.locator('tr.dci-row').first
        row('Bass Man').locator('[data-act=date-open]').click()
        results.append(check(pg, 'Zeile Jahr', '[data-f=rd-by]', '2001', row('Bass Man')))
        results.append(check(pg, 'Zeile Monat', '[data-f=rd-bm]', '03', row('Bass Man')))
        results.append(check(pg, 'Zeile Tag', '[data-f=rd-bd]', '02', row('Bass Man')))
        # the column date is in the ▾ menu of the column head
        pg.locator('[data-colhead] [data-act=mx-colmenu]').first.click(); pg.wait_for_timeout(300)
        results.append(check(pg, 'Matrix-Spalte Jahr', '[data-f=cd-by]', '1999'))
        pg.locator('[data-colhead] [data-act=mx-colmenu]').first.click(); pg.wait_for_timeout(300)
        pg.locator('[data-act=mx-menu]').first.click(); pg.wait_for_timeout(400)
        n = pg.locator('[data-f^=xd-]').count()
        print('Zellmenü-Felder:', n)
        results.append(n == 8)
        if n:
            results.append(check(pg, 'Matrix-Zelle Jahr', '[data-f=xd-by]', '1998'))
        pg.click('#dci-overlay .dci-head h2'); pg.wait_for_timeout(300)
        pg.evaluate("document.querySelector('[data-el=datefind]').open = true")
        results.append(check(pg, 'Daten-Suchfeld', '[data-f=datefind]', 'Recorded 1 May 2002'))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_eva385():
    """Credits Importer 3.85.0 (collected item Z-EVA, rule S132): an event on a release with audio and videos – track 2 a video
    (MusicBrainz's flag), track 3 "Song Three (Official Video)" without the flag.
    A) The question offers "recorded at + video shot at (by media type)" first.
    B) Chosen: two rows – "recorded at" on tracks 1 and 4, "video shot at" on tracks 2 and 3; a message names track 3 (its title says
       video, MusicBrainz has an audio recording).
    C) (review) Another event, "video shot at" chosen as such: the hint for track 3 too."""
    import common_rows as C
    EV = H.uid("fefefefe", 12)
    H.COMPANIES[1032] = ('event', EV, 'Club Night 2020')
    H.lt(9001, H.uid('9e9e9e9e', 1), 'recorded at', 'event', 'recording', ())
    H.lt(9002, H.uid('9e9e9e9e', 2), 'recorded at', 'event', 'release', ())
    H.lt(9003, H.uid('9e9e9e9e', 3), 'video shot at', 'event', 'recording', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.VIDEO_TRACKS.add(1)
    old = H.TITLES[2]
    H.TITLES[2] = 'Song Three (Official Video)'
    ROWS = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => /Club Night 2020/.test(x.querySelector('.dci-gname').textContent));
      return g ? [...g.querySelectorAll('tr.dci-row')].map(r => { const t = r.querySelector('[data-f=type]'); return (t ? (t.selectedOptions[0] || {}).text : '') + ' ' + (r.querySelector('[data-tcount]') || {textContent: ''}).textContent.trim(); }) : null; })()"""
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S136']))")  # ([Z-EVL] 3.88.0) the question
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.evaluate("document.querySelector('[data-el=manual]').hidden = false")
            pg.fill('[data-f=manual-artist]', f'https://musicbrainz.org/event/{EV}')
            pg.click('[data-act=add-manual]')
            H.wait_for(pg, "[...document.querySelectorAll('section.dci-group')].some(x => /Club Night 2020/.test(x.textContent))", 20)
            pg.wait_for_timeout(300)
            btns = pg.evaluate("[...document.querySelectorAll('[data-el=manual-evq] button')].map(b => b.dataset.type || b.dataset.act)")
            print('A)', btns)
            results.append(btns[:1] == ['both'])
            pg.click('[data-el=manual-evq] [data-type=both]')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(x => /Club Night 2020/.test(x.textContent)).querySelectorAll('[data-act=row-open], [data-act=tracks-open]').forEach(b => b.click())")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            rows = pg.evaluate(ROWS)
            tracks = C.tracks_of_rows(pg, 'Club Night 2020')
            msgs = pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(m => m.textContent.replace(/\\s+/g, ' ')).filter(t => /looks like a video/.test(t))")
            print('B)', rows, tracks, msgs)
            results.append(rows is not None and len(rows) == 2 and rows[0].startswith('recorded at') and rows[1].startswith('video shot at')
                           and (not tracks or tracks == [[1, 4], [2, 3]]) and len(msgs) == 1 and 'Song Three (Official Video)' in msgs[0])
            # C) (3.85.0 review) "video shot at" chosen as such: the hint for the title-only video too
            EV2 = H.uid('fefefefe', 13)
            H.COMPANIES[1034] = ('event', EV2, 'Club Night 2021')
            pg.evaluate("document.querySelector('[data-el=manual]').hidden = false")
            pg.fill('[data-f=manual-artist]', f'https://musicbrainz.org/event/{EV2}')
            pg.click('[data-act=add-manual]')
            H.wait_for(pg, "!!document.querySelector('[data-el=manual-evq] [data-type=\"video shot at\"]')", 20)
            pg.evaluate("document.querySelectorAll('.dci-msg').forEach(m => m.remove())")
            pg.click('[data-el=manual-evq] [data-type="video shot at"]')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            c = pg.evaluate("[...document.querySelectorAll('.dci-msg')].some(m => /looks like a video/.test(m.textContent))")
            print('C)', c)
            results.append(c)
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.TITLES[2] = old
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
