"""Dashboard: its head, the head of an entry, "Add entry manually", messages, the page bar, ▲ ▼ (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: head, entryhead, manualtop, msgs, bar, jump – each the former smoke/t_<case>.py, unchanged –, [3.34.23] compacthint, [3.36.3] keys; `python3 t_ui_head.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_head():
    """Credits Importer 3.26.0: the head of the dashboard in one line (collected item 30).
    A) One line: title · the source (link) · "Source ▾" · "+ Supplement" · the status of the view · text size · ⚙, Mapping
       rules, Log, ⓘ, ⤢, ✕ with own symbols (aria-label and tooltip); no language, no window/page switch, no switches of
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
  const label = h.querySelector('.dci-hlabel');
  return { spread: Math.max(...tops) - Math.min(...tops), btns, zoom: h.querySelector('[data-el=zoom]').textContent.trim(),
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
        # [3.27.2] the symbol of the compact view first, left of the text size (item 60); [3.36.3] ⌨ the keyboard shortcuts before ⓘ
        results.append(a1['spread'] <= 6 and [x[0] for x in a1['btns']] == ['view-toggle', 'settings-open', 'rules', 'log', 'keys-open', 'connections-open', 'window-reset', 'close']
                       and all(x[1] and x[2] and x[3] for x in a1['btns']) and a1['btns'][1][2] == 'Settings' and a1['btns'][0][2] == 'Compact' and a1['zoom'] == '100 %'
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
       3.32.1: the name "Bass Man" and the chip); the MusicBrainz name (no "credited as") – no chip. A row credited otherwise:
       "as “Bassman”" at the head (the spelling of the head not again), the compact line of each row names its own credit.
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
        results.append(b1['shown'] == ['B. Man*', 'Discogs: Bass Man'] and b1['chip'] is None
                       and b2['chip'] and b2['chip'][0] == 'as “Bassman”' and lines == 2)
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
            tr = pg.locator('tr.dci-row').filter(has=pg.locator('.dci-drole', has_text=raw)).first
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
        pg.locator('[data-act=jump-bottom]').evaluate('b => b.click()'); pg.wait_for_timeout(1200)
        down = pg.evaluate(f"(() => {{ const b = {body}; return [Math.round(b.scrollTop), b.scrollHeight - b.clientHeight]; }})()")
        pg.locator('[data-act=jump-top]').evaluate('b => b.click()'); pg.wait_for_timeout(1200)
        up = pg.evaluate(f"{body}.scrollTop")
        print('Fenster: ▼', down, '| ▲', up)
        results.append(down[1] > 100 and abs(down[0] - down[1]) <= 2 and up == 0)
        # in the page
        H.toggle_place(pg); pg.wait_for_timeout(300)
        inline = pg.evaluate("!!document.querySelector('.dci-inline')")
        pg.locator('[data-act=jump-bottom]').evaluate('b => b.click()'); pg.wait_for_timeout(1500)
        y1 = pg.evaluate("[Math.round(scrollY), Math.round(document.documentElement.scrollHeight - innerHeight)]")
        foot = pg.evaluate("Math.round(document.querySelector('.dci-panel').getBoundingClientRect().bottom - innerHeight)")
        pg.locator('[data-act=jump-top]').evaluate('b => b.click()'); pg.wait_for_timeout(1500)
        top = pg.evaluate("Math.round(document.querySelector('.dci-panel').getBoundingClientRect().top)")
        print('Seite:', inline, '| ▼ scrollY', y1, 'Ende des Dashboards zum Fensterrand:', foot, '| ▲ Anfang des Dashboards:', top)
        results.append(inline and y1[0] > 200 and -40 <= foot <= 20 and 0 <= top <= 20)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_compacthint():
    """Credits Importer 3.34.23: an arrow at "Compact | Full" (collected item 143; maintainer: "falls man das skript zum ersten
    mal startet soll ein pfeil auf den kompaktmodus hinweisen. er soll verschwinden sobald zum ersten mal umgestellt wird", "ja
    auch für alle die es schon haben. und auch zurücksetzen bitte", "ja ok").
    A) Nothing stored about it: the dashboard's head shows the arrow below the symbol (its tip below the symbol), the text says
       what the compact view is; what lies below it can still be clicked (the pointer goes through, only ✕ is a button).
    B) The symbol switches to compact: the arrow is gone, stored; back to full and a new page: still gone.
    C) ⚙ Settings → "Reset all settings": the arrow is back; ✕ closes it for good (stored), ↺ of Appearance brings it back.
    D) The compact view stored before (an older version): no arrow, also after switching to full."""
    results = []
    HINT = """(() => { const h = document.querySelector('.dci-head .dci-hint-compact'); const b = document.querySelector('.dci-head [data-act=view-toggle]');
      if (!h) return null; const r = h.querySelector('.dci-hint-bubble').getBoundingClientRect(); const br = b.getBoundingClientRect();
      const tip = getComputedStyle(h.querySelector('.dci-hint-bubble'), '::before');
      return { text: h.querySelector('.dci-hint-text').textContent, below: r.top >= br.bottom - 2, near: r.right >= br.left && r.left <= br.right + 40,
        through: getComputedStyle(h).pointerEvents === 'none', tip: tip.content !== 'none' }; })()"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.evaluate("localStorage.removeItem('dci-hint-compact')")
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        a = pg.evaluate(HINT)
        print('A) Pfeil:', a)
        results.append(bool(a) and a['text'].startswith('Try the compact view') and a['below'] and a['near'] and a['through'] and a['tip'])
        # B) switched
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        b1 = [pg.evaluate(HINT), pg.evaluate("localStorage.getItem('dci-hint-compact')")]
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        b2 = pg.evaluate(HINT)
        pg.close()
        pg, errs2 = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        b3 = pg.evaluate(HINT)
        print('B) nach dem Umschalten:', b1, '| wieder voll:', b2, '| neue Seite:', b3)
        results.append(b1 == [None, 'true'] and b2 is None and b3 is None)
        # C) reset all settings, ✕, ↺ of Appearance
        H.open_settings(pg)
        pg.click('[data-el=settings] [data-act=reset-open]')
        pg.wait_for_timeout(200)
        pg.click('[data-act=reset-do]')
        pg.wait_for_timeout(2500)
        c1 = pg.evaluate(HINT)
        pg.click('.dci-head .dci-hint-compact [data-act=hint-compact-close]')
        pg.wait_for_timeout(300)
        c2 = [pg.evaluate(HINT), pg.evaluate("localStorage.getItem('dci-hint-compact')")]
        H.open_settings(pg, 'appearance')
        pg.locator('[data-el=settings] [data-act=settings-reset]').first.evaluate('b => b.click()')
        pg.wait_for_timeout(500)
        c3 = pg.evaluate(HINT)
        print('C) nach „Reset all“:', bool(c1), '| ✕:', c2, '| ↺ Appearance:', bool(c3))
        results.append(bool(c1) and c2 == [None, 'true'] and bool(c3))
        print('Fehler:', errs + errs2)
        results.append(not errs and not errs2)
        pg.close()
        # D) the compact view stored before
        ctx2 = H.new_context(b)
        ctx2.add_init_script("if (localStorage.getItem('dci-view') === null) { localStorage.setItem('dci-store-epoch', '4'); localStorage.setItem('dci-view', JSON.stringify('compact')); }")
        pg, errs3 = H.open_mb_edit(ctx2, companion=False, view=None)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        d1 = [pg.evaluate(HINT), pg.evaluate("localStorage.getItem('dci-hint-compact')")]
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        d2 = pg.evaluate(HINT)
        print('D) kompakt gespeichert:', d1, '| voll:', d2, '| Fehler:', errs3)
        results.append(d1 == [None, 'true'] and d2 is None and not errs3)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_keys():
    """Credits Importer 3.36.3 (maintainer: "Bitte einen neuen Infoknopf oben in der Leiste der die aktuelle Tastaturbelegung aller
    shortcuts zeigt."): ⌨ in the head.
    A) ⌨ (before ⓘ) opens the shortcuts below the head: the groups (the pages, the release editor, the dashboard, the media
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


run_cases(globals())
