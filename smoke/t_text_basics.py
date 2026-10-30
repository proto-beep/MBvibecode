"""Texts, part 1: a pasted text, the rules for free texts, lists of names, "credited as", distribution (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: freetext, textrules, names, textcredit, distrib, playedby (3.34.19), instrguess (3.34.20, 3.34.27), voicetech (3.34.25), unknownask (3.34.26, 3.34.27), casenote (3.34.28, 3.35.2), casephrase (3.35.2), guests (3.37.2) – each the former smoke/t_<case>.py, unchanged; `python3 t_text_basics.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_freetext():
    """Import 3.2.0 (E1): credits from a pasted text. "Paste text …" opens a field for the text and where it is from;
    "Read text" makes it the source. Lines become rows: "Name – instrument", "Name: roles", "Role: names",
    "Written by A, mixed by B" (two clauses), "Recorded live at Place, City, date by Name" (a person and a place),
    "Mastered by A at Studio", "Tracks 3–4: Strings arranged by Z" (tracks, "Arranged By [Strings]"),
    "Published by X (1, 3)" (a company for tracks 1 and 3), "℗ 2019 Label"; a line without credits is listed as not
    recognized ([3.21.0] thanks: listed apart as left out on purpose). Names have no links: MusicBrainz entries of the same name are only suggested (dashed, yellow), a click
    assigns one ([3.37.1] Writer W, composer of "Song One" in MusicBrainz, marked "in this release: …", E5a). Track lists are not
    read again as notes (S022). The edit note names the text's origin."""
    import re

    H.attr(9120, 'trumpet', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    TEXT = """Peter Evans – trumpet
Bass Man: bass, vocals
Guitar: Guitar Guy, Nobody Known
Written by Writer W, mixed by Jane Roe
Recorded live at Abbey Road Studios, London, 12 May 2019 by John Doe
Mastered by Jane Roe at Mastering House
Tracks 3–4: Strings arranged by Writer Z
Artwork: Max Mustermann
Published by Pub Co (1, 3)
℗ 2019 Sony
Thanks to everyone who came."""
    ROWS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const p = tr.querySelector('[data-f=primary]');
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', p ? p.value : '',
      (tr.querySelector('[data-tcount]') || { textContent: '' }).textContent.trim()]; }),
  [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.trim())]))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        # A) paste the text
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', TEXT)
        pg.fill('[data-f=text-origin]', 'Booklet')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(800)
        groups = {g[0]: g for g in pg.evaluate(ROWS)}
        for name, g in groups.items():
            print('   ', name, '|', g[1], '| Vorschläge:', g[2])
        src = pg.evaluate("document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').slice(0, 120)")
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        ign = pg.evaluate("[...document.querySelectorAll('.dci-ignored li .dci-ign-text')].map(li => li.textContent)")
        print('A) Quelle:', src, '| nicht erkannt:', unrec, '| ausgelassen:', ign)
        roles = lambda name: [r[0] for r in groups.get(name, ['', [], []])[1]]
        ok_a = 'Text: Booklet' in src and unrec == [] and ign == ['Thanks to everyone who came.'] \
            and roles('Peter Evans') == ['trumpet'] and roles('Bass Man') == ['bass', 'vocals'] \
            and roles('Guitar Guy') == ['Guitar'] and roles('Nobody Known') == ['Guitar'] \
            and roles('John Doe') == ['Recorded live By'] and sorted(roles('Jane Roe')) == ['Mastered By', 'Mixed By'] \
            and roles('Max Mustermann') == ['Artwork'] and 'Abbey Road Studios' in groups and 'Mastering House' in groups and 'Sony' in groups
        # B) the work level: writer W, arranger Z on tracks 3–4, publisher Pub Co on tracks 1 and 3
        cols = pg.evaluate("""(() => { const out = {}; document.querySelectorAll('.dci-matrix th[data-colhead]').forEach((th) => {
      const name = (th.querySelector('.dci-mx-colname .dci-mblink, .dci-mx-colname strong') || {}).textContent.replace(/^MB/, '').trim();
      if (out[name]) return;
      out[name] = [...document.querySelectorAll(`.dci-mx-cell[data-col="${th.dataset.colhead}"]`)].filter(c => c.classList.contains('dci-mx-on'))
        .map(c => (Number(c.closest('tr').dataset.work) + 1) + (c.classList.contains('dci-mx-sugg') ? 's' : '')); }); return out; })()""")
        print('B) Werk-Matrix:', {k: v for k, v in cols.items() if k in ('Writer W', 'Writer Z', 'Pub Co')})
        ok_b = cols.get('Writer W') == ['1', '2', '3', '4'] and cols.get('Writer Z') == ['3', '4'] and cols.get('Pub Co') == ['1', '3']
        # C) names: suggestions only; a click assigns
        sugg = {k: v[2] for k, v in groups.items() if v[2]}
        status = pg.evaluate("[...document.querySelectorAll('section.dci-group')].filter(g => (g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()) === 'Bass Man').map(g => g.className)[0]")
        look = pg.evaluate("(() => { const b = document.querySelector('[data-act=name-use]'); const s = getComputedStyle(b); return [s.borderTopStyle, s.backgroundColor]; })()")
        bm = pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(g => (g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()) === 'Bass Man').dataset.group")
        pg.click(f'section[data-group="{bm}"] [data-act=name-use]'); pg.wait_for_timeout(300)
        after = pg.evaluate(f"document.querySelector('section[data-group=\"{bm}\"]').className")
        link = pg.evaluate(f"(document.querySelector('section[data-group=\"{bm}\"] .dci-mblink') || {{}}).href || ''")
        print('C) Vorschläge:', sugg, '| Bass Man vorher:', status, '| Stil:', look, '| nach Klick:', after, link)
        ok_c = sugg.get('Bass Man') == ['Bass Man'] and sugg.get('Writer W') == ['Writer W in this release: composer on “Song One”'] and 'Peter Evans' not in sugg and 'dci-st-missing' in status \
            and look == ['dashed', 'rgb(255, 248, 219)'] and 'dci-st-manual' in after and link.endswith(H.ARTISTS[3001][0]) \
            and any('Sony' in k for k in sugg) and any('Abbey Road' in k for k in sugg)
        # D) staging: the edit note names the text's origin
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        note = pg.evaluate("document.getElementById('edit-note-text').value")
        added = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0 && r.entity0.name === 'Bass Man').length")
        print('D) Notiz:', [l for l in note.splitlines() if l.startswith('Source') or 'from a pasted text' in l], '| Bass Man vorgemerkt:', added)
        ok_d = 'Source: Booklet' in note.splitlines() and any('from a pasted text (' in l for l in note.splitlines()) and added >= 1
        results += [ok_a, ok_b, ok_c, ok_d]
        print('Fehler:', errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_textrules():
    """Import 3.14.0: rules for free credits texts (any source: a pasted text, Bandcamp credits).
    A) "Music played and recorded by X in March and April 2025" → X played by (performer) and recorded by; the time is cut
       off the name. "Mixed and mastered by X in May 2025" → mixed by, mastered by. "Layout by X" (the role is "Layout").
       "Photography Sam Lee" (a role, then a name, no separator); "mastering john doe" (small letters).
    B) The dates: "March and April 2025" is one period 2025-03 – 2025-04; "May 2025".
    C) "A Northern Echo release." is left out (not listed as not recognized); prose stays not recognized; [3.21.0] thanks are
       listed apart as left out on purpose.
    D) "Music and artwork of this release were entirely created by a (cat assisted) human. No AI tools were used.": no name
       – the release's artist is offered for music and artwork, as its own entry with a suggestion; nothing is assigned."""
    JR = H.uid('dddddddd', 60)
    H.RELEASE_AC[:] = [(JR, 'Jane Roe', 'Jane Roe', '')]
    H.MB_SEARCH['artist'] = [{'id': JR, 'name': 'Jane Roe', 'disambiguation': '', 'score': 100}]
    TEXT = """Music played and recorded by Jane Roe in March and April 2025.

Mixed and mastered by Jane Roe in May 2025.

Photography Sam Lee.
Layout by Jane Roe.
mastering john doe

Music and artwork of this release were entirely created by a (cat assisted) human. No AI tools were used.

A Northern Echo release.
We had a great time together
Thanks to the cat for keeping us company"""
    GROUPS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
  [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim()),
  // 3.15.2: the explanation of the suggestions is the stack's tooltip
  (g.querySelector('.dci-sugg-stack') || {}).title || '',
  [...g.querySelectorAll('[data-act=name-use]')].map(b => b.dataset.mbid), g.className.match(/dci-st-(\\w+)/)[1]]))()"""
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
        pg.wait_for_timeout(800)
        g = pg.evaluate(GROUPS)
        for x in g:
            print('   ', x)
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        ign = pg.evaluate("[...document.querySelectorAll('.dci-ignored li .dci-ign-text')].map(li => li.textContent)")
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => [JSON.stringify(d.begin), JSON.stringify(d.end)].join(' '))")
        print('   nicht erkannt:', unrec, '| ausgelassen:', ign)
        print('   Pool:', pool)
        named = [x for x in g if x[0] == 'Jane Roe' and 'names no one' not in x[2]]
        ok_a = bool(named) and named[0][1] == ['Played By', 'Recorded By', 'Mixed By', 'Mastered By', 'Layout'] \
            and ['Sam Lee', ['Photography By']] in [x[:2] for x in g] and ['john doe', ['Mastering']] in [x[:2] for x in g]
        ok_b = '{"year":2025,"month":3,"day":null} {"year":2025,"month":4,"day":null}' in pool and '{"year":2025,"month":5,"day":null} {"year":2025,"month":5,"day":null}' in pool
        ok_c = unrec == ['We had a great time together'] and ign == ['Thanks to the cat for keeping us company']
        ph = [x for x in g if x[0] == 'Jane Roe' and 'names no one' in x[2]]
        ok_d = bool(ph) and 'a human' in ph[0][2] and ph[0][3] == [JR] and ph[0][4] == 'missing' and ph[0][1] == ['Artwork']
        mark = pg.evaluate("[...document.querySelectorAll('.dci-sugg-stack [data-act=name-use] .dci-similar')].map(x => x.textContent)")
        print('   Marken an Vorschlägen:', mark)
        ok_d = ok_d and 'release artist' in mark
        works = pg.evaluate("[...document.querySelectorAll('[data-el=works] .dci-mx-colhead, [data-el=works] th')].map(x => x.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /Jane Roe/.test(t))")
        print('   Werke-Matrix (Jane Roe):', works[:2])
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c, '| D)', ok_d)
        results += [ok_a, ok_b, ok_c, ok_d, bool(works)]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_names():
    """Import 3.6.0: lists of instruments and names in a text, as Bandcamp writes them (example: "The Swiftest Traveler",
    trost records).
    A) "Torben Snekkestad: tenor & soprano sax, trumpet and clarinet" – the shared word "sax" goes to "tenor" too: tenor
       saxophone, soprano saxophone, trumpet, clarinet. "acoustic & electric guitar" likewise; "bass & electric guitar" stays
       two instruments (bass is no modifier).
    B) A list with a part it does not know: the known roles are taken, the line is listed as not recognized with the
       unknown part ("Barry Guy – double bass, sticks-and-stones" → double bass; "? “sticks-and-stones”"). [3.34.26] The unknown
       part is a row of its own that asks (137d) – here, without "other instruments" and similar ones, miscellaneous support.
    C) Name suggestions: accents do not count ("Agusti Fernández" → MB "Agustí Fernández", same name); a middle name more
       or less is a similar name, marked as such ("Barry Guy" → MB "Barry John Guy"); nothing is assigned by itself."""
    for i, n in [(9120, 'trumpet'), (9121, 'clarinet'), (9122, 'tenor saxophone'), (9123, 'soprano saxophone')]:
        H.attr(i, n, 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.MB_SEARCH['artist'] = [
        {'id': H.uid('dddddddd', 50), 'name': 'Agustí Fernández', 'disambiguation': 'pianist', 'score': 100},
        {'id': H.uid('dddddddd', 51), 'name': 'Barry John Guy', 'disambiguation': 'bassist', 'score': 100},
        {'id': H.uid('dddddddd', 52), 'name': 'Torben Snekkestad', 'disambiguation': '', 'score': 100},
    ]
    TEXT = """Torben Snekkestad: tenor & soprano sax, trumpet and clarinet
Agusti Fernández – piano
Barry Guy – double bass, sticks-and-stones
Gene Pick – acoustic & electric guitar
Bo Strum – bass & electric guitar"""
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
  [[...g.querySelectorAll('tr.dci-row')].map(tr => { const p = tr.querySelector('[data-f=primary]'); return p ? p.value : tr.querySelector('.dci-drole').textContent.trim(); }),
   [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()), g.className.match(/dci-st-(\\w+)/)[1]]])))()"""
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
        pg.wait_for_timeout(800)
        g = pg.evaluate(ROWS)
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        for k, v in g.items():
            print('   ', k, v)
        print('   nicht erkannt:', unrec)
        # A) shared instrument word
        ok_a = g['Torben Snekkestad'][0] == ['tenor saxophone', 'soprano saxophone', 'trumpet', 'clarinet'] \
            and g['Gene Pick'][0] == ['acoustic guitar', 'electric guitar'] and g['Bo Strum'][0] == ['bass', 'electric guitar']
        results.append(ok_a)
        # B) partly known
        # [3.34.26] the unknown part a row of its own that asks (137d; here no "other instruments": miscellaneous support)
        ok_b = g['Barry Guy'][0] == ['double bass', 'sticks-and-stones'] and unrec == []
        results.append(ok_b)
        # C) name suggestions
        sim = pg.evaluate("(() => { const b = [...document.querySelectorAll('[data-act=name-use]')].find(x => /Barry John Guy/.test(x.textContent)); return b ? [b.title, !!b.querySelector('.dci-similar')] : null; })()")
        print('   ähnlich:', sim)
        ok_c = g['Agusti Fernández'][1] == ['Agustí Fernández (pianist)'] and g['Barry Guy'][1] == ['Barry John Guy (bassist) similar name'] \
            and g['Torben Snekkestad'][1] == ['Torben Snekkestad'] and all(v[2] == 'missing' for v in g.values()) \
            and sim and sim[1] and 'similar name' in sim[0].lower()
        results.append(ok_c)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_textcredit():
    """Credits Importer 3.28.4: "credited as" from a text, the design of a part of the package, joined design tasks
    (collected items 83, 84 and the maintainer's answers of 2026-10-24 19:33).
    A) Discogs: "Cover Design", "Design [Sleeve]", "Artwork [Cover Design]", "Booklet Design", "Package Design" are design
       credited "cover design", "sleeve design", "cover design", "booklet design", "package design" (S037).
    B) "Artwork [Design And Layout]": one row design credited "design and layout" (both tasks are design; S033) – not two;
       "Artwork [Logo Og Kunst]" stays two rows (design "logo", artwork "art"). Both name S033 at the row.
    C) The field "Artist credit for all roles": empty for "VALFAR" (only the case differs from Valfar), "M. Mann" for Master
       Mann.
    D) A pasted text: "Produced by Jane Roe" linked to the suggestion Jane A. Roe → credited "Jane Roe" (as in the text,
       S036); "Mixed by JOHN DOE" linked to John Doe → no "credited as" (only the case differs, S031); the row names S036."""
    H.lt(1202, '1d4c0b5b-0000-4000-8000-000000001202', 'artwork', 'artist', 'release', (1, 1150))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    CREDITS = [('Cover Guy', 'Cover Design', 3031, ''), ('Sleeve Guy', 'Design [Sleeve]', 3032, ''), ('Art Guy', 'Artwork [Cover Design]', 3033, ''),
               ('Booklet Guy', 'Booklet Design', 3034, ''), ('Pack Guy', 'Package Design', 3035, ''), ('Lay Guy', 'Artwork [Design And Layout]', 3036, ''),
               ('Kunst Guy', 'Artwork [Logo Og Kunst]', 3037, ''), ('Valfar', 'Vocals', 3015, 'VALFAR'), ('Master Mann', 'Mastered By', 3012, 'M. Mann')]
    for n, r, i, anv in CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release


    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': anv, 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i, anv in CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d


    H.discogs_release = rel
    JANE, JOHN = H.uid('dddddddd', 80), H.uid('dddddddd', 81)
    H.MB_SEARCH['artist'] = [{'id': JANE, 'name': 'Jane A. Roe', 'disambiguation': '', 'score': 100, 'aliases': []},
                             {'id': JOHN, 'name': 'John Doe', 'disambiguation': '', 'score': 100, 'aliases': []}]
    ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
  { all: (g.querySelector('[data-f=artist-credit-all]') || {}).value, rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]');
    const c = tr.querySelector('[data-f=role-credit]'); const cr = tr.querySelector('[data-f=credit]');
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', c ? c.value : '-', cr ? cr.value : '-',
      [...tr.querySelectorAll('.dci-ruleid')].map(b => b.textContent.trim())]; }) }])))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)
        g = pg.evaluate(ROWS)
        for k, v in g.items():
            print('   ', k, v)
        first = lambda n: (g.get(n) or {'rows': [['', '', '', '', []]]})['rows'][0]
        # A)
        a1 = [first(n)[1:3] for n in ('Cover Guy', 'Sleeve Guy', 'Art Guy', 'Booklet Guy', 'Pack Guy')]
        print('A) Design-Teile:', a1)
        results.append(a1 == [['design', 'cover design'], ['design', 'sleeve design'], ['design', 'cover design'], ['design', 'booklet design'], ['design', 'package design']]
                       and all('S037' in first(n)[4] for n in ('Cover Guy', 'Sleeve Guy', 'Booklet Guy')))
        # B)
        lay, kunst = g.get('Lay Guy')['rows'], g.get('Kunst Guy')['rows']
        print('B) Design And Layout:', lay, '| Logo Og Kunst:', [x[:3] for x in kunst])
        results.append(len(lay) == 1 and lay[0][:3] == ['Artwork [Design And Layout]', 'design', 'design and layout'] and 'S033' in lay[0][4]
                       and [x[:3] for x in kunst] == [['Design [Logo]', 'design', 'logo'], ['Artwork [Art]', 'artwork', 'art']])
        # C)
        c1 = [g.get('Valfar')['all'], g.get('Master Mann')['all'], first('Valfar')[3]]
        print('C) Feld „für alle Rollen“ – Valfar, Master Mann; credited as Valfar:', c1)
        results.append(c1 == ['', 'M. Mann', ''])
        # D) a pasted text
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Produced by Jane Roe\nMixed by JOHN DOE')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1500)
        for name, mbid in [('Jane Roe', JANE), ('JOHN DOE', JOHN)]:
            # [3.32.2] an entry with a name variation shows it in its head ("VALFAR*"); its name is in data-name
            key = pg.evaluate("(n) => [...document.querySelectorAll('section.dci-group')].find(s => { const x = s.querySelector('.dci-gname strong'); return (x.dataset.name || x.textContent.trim()) === n; }).dataset.group", name)
            sec = f'section.dci-group[data-group="{key}"]'
            pg.locator(f'{sec} [data-act=name-use][data-mbid="{mbid}"]').first.click()
            pg.wait_for_timeout(800)
        e = pg.evaluate(ROWS)
        d1 = [(e.get('Jane Roe') or {'rows': [[]]})['rows'][0], (e.get('JOHN DOE') or {'rows': [[]]})['rows'][0]]
        print('D) Text:', d1)
        results.append(d1[0][3] == 'Jane Roe' and 'S036' in d1[0][4] and d1[1][3] == '')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_distrib():
    """Credits Importer 3.17.3: "Distribution - !K7" and its variants (T028) – a label that distributes the release.
    A) In Node: "Distribution - X", "Distribution: X", "Distribution by X", "Distributor: X", "Distributed by X",
       "Distributed through X", "Vertrieb: X", "Vertrieben durch X", "Distribución: X", "Distribuido por X", "Distribué par X"
       all give the company X with the role "Distributed By"; "Distribution of the songs was slow." gives nothing.
    B) In the dashboard (a pasted text): "!K7" is an entry for a label with the row "Distributed By" (label → release
       "distributed", release level); the MusicBrainz label of that name is only suggested."""
    import json
    import subprocess

    H.lt(361, 'c74dee45-3f43-4b5e-9a5c-6e0a1b2c3d61', 'distributed', 'label', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.MB_SEARCH.setdefault('label', []).append({'id': H.uid('eeeeeeee', 77), 'name': '!K7', 'aliases': []})
    LINES = ['Distribution - !K7', 'Distribution: !K7 Records', 'Distribution by !K7', 'Distributor: Rough Trade', 'Distributed by !K7',
             'Distributed through The Orchard', 'Vertrieb: Indigo', 'Vertrieben durch Indigo', 'Distribución: Altafonte',
             'Distribuido por Altafonte', 'Distribué par Pias', 'Distribution of the songs was slow.']
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const isCompanyRole = (r) => /distributed by/i.test(r);
const isRole = (r) => /^(Distributed By)$/i.test(r);
const out = JSON.parse(process.argv[2]).map((t) => {
  const r = m.SOURCES.text.parse(t, { isRole, isCompanyRole, resolveTracks: () => null });
  return [t, r.companies.map((c) => [c.who.name, c.role]), r.credits.length, r.unrecognized.length];
});
console.log(JSON.stringify(out));
"""
    results = []
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(LINES)], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    got = json.loads(js.stdout) if not js.returncode else []
    for line, comps, ncred, nunrec in got:
        print('A)', line, '→', comps, '| Credits', ncred, '| nicht erkannt', nunrec)
    want = ['!K7', '!K7 Records', '!K7', 'Rough Trade', '!K7', 'The Orchard', 'Indigo', 'Indigo', 'Altafonte', 'Altafonte', 'Pias']
    results.append(len(got) == len(LINES) and all(g[1] == [[w, 'Distributed By']] for g, w in zip(got, want)) and got[-1][1] == [] and got[-1][3] == 1)

    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    ENTRY = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => (s.querySelector('.dci-gname strong').dataset.name || s.querySelector('.dci-gname strong').textContent.trim()) === '!K7');
  if (!g) return null; const tr = g.querySelector('tr.dci-row'); const sel = tr.querySelector('[data-f=type]'); const lv = tr.querySelector('[data-act=level][aria-pressed=true]');
  return [tr.querySelector('.dci-drole').textContent.trim(), sel ? sel.options[sel.selectedIndex].textContent.trim() : '', lv ? lv.dataset.level : '',
    g.className.match(/dci-st-(\\w+)/)[1], g.querySelectorAll('[data-act=name-use]').length]; })()"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Distribution - !K7')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= 2", 60)
        pg.wait_for_timeout(1500)
        e = pg.evaluate(ENTRY)
        print('B) Eintrag !K7:', e)
        results.append(e is not None and e[0] == 'Distributed By' and 'distributed' in e[1] and e[2] == 'release' and e[3] != 'linked' and e[4] >= 1)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


GK_TEXT = """Electric guitar
Acoustic guitar
Electric bass
Drums
Piano
Organ
Keyboards
Trumpet
Clarinet
Marimba
Shaker
Tambourine
Bongo
Melodica
Chaims
Whistle
Woodblock
Cowbell
Buddha machine
Voice

are played, mixed and produced by Go Kurosawa

Recorded in Guruguru Brain studio, Rotterdam, 2024 January - July"""
# instruments of MusicBrainz for the text of Go Kurosawa (3.34.19, 3.34.20)
GK_INSTRUMENTS = [(9110, 'organ'), (9111, 'keyboard'), (9140, 'trumpet'), (9112, 'clarinet'), (9113, 'marimba'), (9114, 'shaker'), (9115, 'tambourine'),
                  (9116, 'bongos'), (9117, 'melodica'), (9118, 'whistle'), (9119, 'wood block'), (9120, 'cowbell'), (9121, 'chimes'), (9122, 'wind chimes'),
                  (9123, 'tubular bells')]
GK_ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), {
  kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1], head: g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(),
  rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const i = tr.querySelector('[data-f=primary]');
    const c = tr.querySelector('[data-f=role-credit]');
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', i ? (i.value || (i.options && i.options[i.selectedIndex] || {}).text || '') : '', c ? c.value : '-',
      (tr.querySelector('.dci-type-ask') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim()]; }) }])))()"""


def case_playedby():
    """Credits Importer 3.34.19: instruments and the name they are played by (collected item 137a, S051; T049, T050; the text of
    Go Kurosawa's "soft shakes" on Bandcamp).
    A) The text pasted – twenty lines with an instrument each, an empty line, "are played, mixed and produced by Go Kurosawa":
       Go Kurosawa has a row per instrument MusicBrainz knows (Electric guitar … Voice), "Mixed By" (mix) and "Produced By"
       (producer) – no "Played By" (before: "Played By [Are]", mixed, produced and the twenty lines not recognized); [3.34.20]
       also the words MusicBrainz does not know ("Chaims", "Buddha machine": they ask – instrguess), nothing not recognized;
       the place of "Recorded in …".
    B) In one line: "Electric guitar, acoustic guitar and piano are played by Jane Roe" – three rows; "Bass Man plays bass and
       drums" – two rows; "are mixed by John Doe" alone – "Mixed By" (not "[Are]")."""
    for i, n in GK_INSTRUMENTS:
        H.attr(i, n, 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)

        def load(text):
            H.src_menu(pg, 'text-open')
            pg.fill('[data-f=text-src]', text)
            n = pg.evaluate("[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length")
            pg.click('[data-act=text-load]')
            H.wait_for(pg, f"[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length > {n}", 90)
            pg.wait_for_timeout(1200)
            return pg.evaluate(GK_ROWS), pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")

        g, unrec = load(GK_TEXT)
        for k, v in g.items():
            print('   ', k, v['kind'], v['rows'])
        gk = [r[0] for r in (g.get('Go Kurosawa') or {'rows': []})['rows']]
        types = {r[0]: r[1] for r in (g.get('Go Kurosawa') or {'rows': []})['rows']}
        place = g.get('Guruguru Brain studio') or {'kind': '', 'rows': []}
        print('A) Go Kurosawa:', gk, '| nicht erkannt:', unrec, '| Ort:', place['kind'], place['rows'])
        results.append(all(x in gk for x in ['Electric guitar', 'Acoustic guitar', 'Drums', 'Piano', 'Organ', 'Trumpet', 'Clarinet', 'Marimba', 'Shaker',
                                              'Tambourine', 'Melodica', 'Whistle', 'Cowbell', 'Voice', 'Mixed By', 'Produced By'])
                       and not any(x.startswith('Played By') for x in gk) and types.get('Mixed By') == 'mix' and types.get('Produced By') == 'producer'
                       and types.get('Piano') == 'instrument' and types.get('Voice') == 'vocal'
                       and 'Chaims' in gk and 'Buddha machine' in gk and not unrec
                       and place['kind'] == 'place' and [r[1] for r in place['rows']] == ['recorded at'])
        g2, unrec2 = load('Electric guitar, acoustic guitar and piano are played by Jane Roe\nBass Man plays bass and drums\nare mixed by John Doe')
        rows = lambda n: [r[0] for r in (g2.get(n) or {'rows': []})['rows']]
        print('B) Jane Roe:', rows('Jane Roe'), '| Bass Man:', rows('Bass Man'), '| John Doe:', rows('John Doe'), '| nicht erkannt:', unrec2)
        results.append(rows('Jane Roe') == ['Electric guitar', 'acoustic guitar', 'piano'] and rows('Bass Man') == ['bass', 'drums']
                       and rows('John Doe') == ['Mixed By'] and not unrec2)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_instrguess():
    """Credits Importer 3.34.20: instruments MusicBrainz names otherwise, "Voice", words that are no instrument (collected item
    137d; T001, Q011; the text of Go Kurosawa's "soft shakes").
    A) Spellings (T001): Bongo → bongos, Woodblock → wood block, Keyboards → keyboard, Electric bass → electric bass guitar,
       Drums → drums (drum set) – each credited as written (Woodblock not: only the space differs).
    B) "Chaims" (no instrument of MusicBrainz): an instrument row asking "did you mean: chimes · wind chimes · tubular bells ·
       other instruments “Chaims”" (tubular bells by its other name "orchestral chimes"), nothing chosen – incomplete; in the
       compact line too. "chimes" chosen: no role credit; "other instruments …": credited "chaims" (3.34.27, S052: in lower
       case; before "Chaims"). "Buddha machine" (none like it): other instruments credited "Buddha machine" at once ("Buddha" a
       proper name of the register, T052, from 3.34.28). Nothing is listed as not recognized.
    C) "Voice" asks (Q011): vocals · other vocals “voice” · lead vocals “voice”, until then vocals without role credit;
       "lead vocals “voice”" → lead vocals credited "voice"; "vocals" → no role credit; a voice typed by hand (lead vocals)
       then offers "use “voice” as role credit", which sets it."""
    for i, n in GK_INSTRUMENTS:
        H.attr(i, n, 14, 14, aliases=['orchestral chimes'] if n == 'tubular bells' else None)
    H.attr(9124, 'other instruments', 14, 14)
    H.attr(9125, 'other vocals', 3, 3)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', GK_TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)

        def rows():
            g = pg.evaluate(GK_ROWS)
            return {r[0]: r for r in (g.get('Go Kurosawa') or {'rows': []})['rows']}

        r = rows()
        for k, v in r.items():
            print('   ', v)
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        a = [r.get(k, [k, '', '', ''])[1:4] for k in ('Bongo', 'Woodblock', 'Keyboards', 'Electric bass', 'Drums')]
        print('A) Schreibweisen:', a)
        results.append(a == [['instrument', 'bongos', 'bongo'], ['instrument', 'wood block', ''], ['instrument', 'keyboard', 'keyboards'],
                             ['instrument', 'electric bass guitar', 'electric bass'], ['instrument', 'drums (drum set)', 'drums']])
        # B) Chaims and Buddha machine
        CH = """(() => { const tr = [...document.querySelectorAll('tr.dci-row')].find(t => t.querySelector('.dci-drole').textContent.trim() === %s); const q = tr && tr.querySelector('.dci-instr-guess');
          return tr ? [q ? q.textContent.replace(/\\s+/g, ' ').trim() : '', q ? [...q.querySelectorAll('[data-act=instr-pick]')].map(b => [b.dataset.instr, b.getAttribute('aria-pressed')]) : [], tr.dataset.row] : null; })()"""
        ch = pg.evaluate(CH % '"Chaims"')
        bm = pg.evaluate(CH % '"Buddha machine"')
        issue = pg.evaluate("(() => { const tr = [...document.querySelectorAll('tr.dci-row')].find(t => t.querySelector('.dci-drole').textContent.trim() === 'Chaims'); return tr ? tr.textContent.includes('unknown') : null; })()")
        print('B) Chaims:', ch, '| unbekannt markiert:', issue, '| Buddha machine:', r.get('Buddha machine'), bm, '| nicht erkannt:', unrec)
        ok_b1 = bool(ch) and ch[0].startswith('“Chaims” is no instrument of MusicBrainz – did you mean:') \
            and [x[0] for x in ch[1]] == ['chimes', 'wind chimes', 'tubular bells', 'other instruments'] and all(x[1] == 'false' for x in ch[1]) \
            and r.get('Buddha machine', [''] * 4)[1:4] == ['instrument', 'other instruments', 'Buddha machine'] and 'none is like it' in (bm or [''])[0] and not unrec
        # the compact line asks too
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        cl = pg.evaluate("(() => { const tr = document.querySelector('tr.dci-row[data-row=\"%s\"] .dci-cline'); return tr ? tr.textContent.replace(/\\s+/g, ' ').trim() : ''; })()" % ch[2]) if ch else ''
        print('   kompakte Zeile:', cl)
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        sec = f'tr.dci-row[data-row="{ch[2]}"]' if ch else 'tr.none'
        pg.click(f'{sec} .dci-instr-guess [data-act=instr-pick][data-instr="chimes"]')
        pg.wait_for_timeout(300)
        r1 = rows().get('Chaims')
        pg.click(f'{sec} .dci-instr-guess [data-act=instr-pick][data-instr="other instruments"]')
        pg.wait_for_timeout(300)
        r2 = rows().get('Chaims')
        print('   chimes gewählt:', r1, '| other instruments:', r2)
        ok_b = ok_b1 and 'did you mean' in cl and r1[1:4] == ['instrument', 'chimes', ''] and r2[1:4] == ['instrument', 'other instruments', 'chaims']
        results.append(ok_b)
        # C) Voice
        VO = """(() => { const tr = [...document.querySelectorAll('tr.dci-row')].find(t => t.querySelector('.dci-drole').textContent.trim() === 'Voice'); const q = tr && tr.querySelector('.dci-type-ask'); const v = tr && tr.querySelector('.dci-voice-credit');
          return tr ? [q ? q.textContent.replace(/\\s+/g, ' ').trim() : '', tr.dataset.row, v ? v.textContent.replace(/\\s+/g, ' ').trim() : ''] : null; })()"""
        v0 = pg.evaluate(VO)
        c0 = rows().get('Voice')
        vsec = f'tr.dci-row[data-row="{v0[1]}"]' if v0 else 'tr.none'
        pg.click(f'{vsec} .dci-type-ask [data-act=type-pick][data-opt="2"]')
        pg.wait_for_timeout(300)
        c1 = rows().get('Voice')
        pg.click(f'{vsec} .dci-type-ask [data-act=type-pick][data-opt="0"]')
        pg.wait_for_timeout(300)
        c2 = rows().get('Voice')
        v2 = pg.evaluate(VO)
        # a voice by hand: the field of the voice
        pg.fill(f'{vsec} [data-f=primary]', 'lead vocals')
        pg.press(f'{vsec} [data-f=primary]', 'Tab')
        pg.wait_for_timeout(400)
        v3 = pg.evaluate(VO)
        btn = pg.locator(f'{vsec} [data-act=voice-credit]')
        has_btn = btn.count() > 0
        if has_btn:
            btn.click()
            pg.wait_for_timeout(300)
        c4 = rows().get('Voice')
        print('C) Frage:', v0[0] if v0 else None, '| vorher:', c0, '| lead vocals “voice”:', c1, '| vocals:', c2, v2, '| von Hand:', v3, has_btn, '| danach:', c4)
        results.append(bool(v0) and 'other vocals “voice”' in v0[0] and 'lead vocals “voice”' in v0[0] and c0[1:4] == ['vocal', '', '']
                       and c1[1:4] == ['vocal', 'lead vocals', 'voice'] and c2[1:4] == ['vocal', '', ''] and v2[2] == ''
                       and 'use “voice” as role credit' in v3[2] and c4[1:4] == ['vocal', 'lead vocals', 'voice'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_voicetech():
    """Credits Importer 3.34.25: "Voice" asks from every source with four answers, instrument technicians get their instrument
    (collected items 137e, 137f; maintainer: "generell soll das mapping wirklich gleich behandelt werden", "alle vier rollen sollen
    angeboten werden", "wenn vocals da steht, dann immer vocals ohne credit", "ja genau").
    A) Discogs "Voice": asks vocals · other vocals “voice” · lead vocals “voice” · spoken vocals “voice” – until then vocal without
       voice and role credit (before: spoken vocals at once); "spoken vocals “voice”" → spoken vocals credited "voice".
       "Vocals": vocal without a question and without role credit.
    B) "Technician [Guitar]" → instrument technician · guitar, "Drum Technician" → drums (drum set), no role credit (before:
       without instrument, "guitar" as role credit); "Technician [Chaims]" asks "did you mean: chimes · wind chimes · …"."""
    for i, n in GK_INSTRUMENTS:
        H.attr(i, n, 14, 14)
    H.attr(9124, 'other instruments', 14, 14)
    H.attr(9125, 'other vocals', 3, 3)
    H.attr(9126, 'spoken vocals', 3, 3)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.lt(986, 'bd780597-0b67-4b97-a4a0-671a70e1182d', 'instrument technician', 'artist', 'release', (14,))
    H.lt(987, H.uid('eeeeeeee', 987), 'instrument technician', 'artist', 'recording', (14,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    CREDITS = [('Vee Speaker', 'Voice', 3041), ('Plain Singer', 'Vocals', 3042), ('Tech One', 'Technician [Guitar]', 3043),
               ('Tech Two', 'Drum Technician', 3044), ('Tech Three', 'Technician [Chaims]', 3045)]
    for n, r, i in CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d

    H.discogs_release = rel
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)
        g = pg.evaluate(GK_ROWS)
        first = lambda n: (g.get(n) or {'rows': [['', '', '', '', '']]})['rows'][0]
        for n, _, _ in CREDITS:
            print('   ', n, first(n))
        v0 = first('Vee Speaker')
        sec = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Vee Speaker');
          return g ? g.querySelector('tr.dci-row').dataset.row : ''; })()""")
        opts = pg.evaluate(f"[...document.querySelectorAll('tr.dci-row[data-row=\"{sec}\"] .dci-type-ask [data-act=type-pick]')].map(b => b.textContent.trim())")
        pg.click(f'tr.dci-row[data-row="{sec}"] .dci-type-ask [data-act=type-pick][data-opt="3"]')
        pg.wait_for_timeout(400)
        g = pg.evaluate(GK_ROWS)
        v1 = first('Vee Speaker')
        print('A) Voice:', v0[1:4], opts, '→', v1[1:4], '| Vocals:', first('Plain Singer')[1:5])
        results.append(v0[1:4] == ['vocal', '', ''] and opts == ['vocals', 'other vocals “voice”', 'lead vocals “voice”', 'spoken vocals “voice”']
                       and v1[1:4] == ['vocal', 'spoken vocals', 'voice'] and first('Plain Singer')[1:5] == ['vocal', '', '', ''])
        t1, t2, t3 = first('Tech One'), first('Tech Two'), first('Tech Three')
        ask = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Tech Three');
          const q = g && g.querySelector('.dci-instr-guess'); return q ? [...q.querySelectorAll('[data-act=instr-pick]')].map(b => b.dataset.instr) : null; })()""")
        print('B) Techniker:', t1[1:4], t2[1:4], t3[1:4], '| Chaims:', ask)
        results.append(t1[1:4] == ['instrument technician', 'guitar', ''] and t2[1:4] == ['instrument technician', 'drums (drum set)', '']
                       and t3[1] == 'instrument technician' and ask == ['chimes', 'wind chimes', 'other instruments'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_unknownask():
    """Credits Importer 3.34.26: words that are no instrument ask in every source (collected item 137d, (c); maintainer: "also c.
    sticks-and-stones bspw. könnte auch einfach "other instruments" werden. wir wollen das auf keinen fall verlieren", "behalte das
    als letzte Antwort bei. auch bei discogs other instruments. aber miscellaneous support auch anbieten", "passt").
    A) Discogs "Chaims" (before: miscellaneous support at once) asks chimes · wind chimes · tubular bells · other instruments
       “Chaims” · miscellaneous support (task “Chaims”), nothing chosen; "miscellaneous support" chosen – type miscellaneous
       support with the task "chaims" (in small letters, as before); then "chimes" – an instrument row again (recording), chimes, no role credit.
    B) Discogs "Sticks-And-Stones" (none like it): other instruments credited "Sticks-And-Stones" at once, "miscellaneous support"
       offered.
    C) A pasted text "Barry Guy – double bass, sticks-and-stones": double bass and other instruments “sticks-and-stones” (before:
       "→ ? “sticks-and-stones”" not recognized); "Jane Roe – guitar, kalimba, buddha machine" (more unknown words than
       instruments): guitar, the rest not recognized as before.
    3.34.27 (S052; maintainer: "instrumente und role credits immer kleinschreiben außer bei eigennamen"): the credit and the task
    of such a word in lower case – "other instruments “chaims”", "miscellaneous support (task “chaims”)", Sticks-And-Stones
    credited "sticks-and-stones" (before: as written); D) "Tambourine [Additional, Toy]": the suggestions of the role credit
    field written like the credit (toy · additional, toy · additional · additional tambourine · toy tambourine; before: "Additional,
    Toy", "Toy Tambourine" …); E) "Hammond Manager" (no role of the register, no instrument like it): other instruments credited
    "Hammond manager" – the proper name of a MusicBrainz instrument ("Hammond organ") keeps its capital –, "miscellaneous support"
    chosen: the task "Hammond manager" (before: "hammond manager")."""
    for i, n in GK_INSTRUMENTS:
        H.attr(i, n, 14, 14, aliases=['orchestral chimes'] if n == 'tubular bells' else None)
    H.attr(9124, 'other instruments', 14, 14)
    H.attr(9102, 'double bass', 14, 14)
    H.attr(9125, 'Hammond organ', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.lt(1130, 'b367fae0-c4b0-48b9-a40c-f3ae4c02cf10', 'misc', 'artist', 'recording', (1150,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    CREDITS = [('Chime Man', 'Chaims', 3051), ('Stick Man', 'Sticks-And-Stones', 3052), ('Tam Man', 'Tambourine [Additional, Toy]', 3053),
               ('Ham Man', 'Hammond Manager', 3054)]
    for n, r, i in CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d

    H.discogs_release = rel
    Q = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      const tr = g && g.querySelector('tr.dci-row'); const q = tr && tr.querySelector('.dci-instr-guess'); const t = tr && tr.querySelector('[data-f=type]');
      const p = tr && tr.querySelector('[data-f=primary]'); const c = tr && tr.querySelector('[data-f=role-credit]');
      const dl = c && c.list ? [...c.list.querySelectorAll('option')].map(o => o.value) : null;
      return tr ? { row: tr.dataset.row, type: t ? (t.options[t.selectedIndex] || {}).text : '', instr: p ? p.value : '', credit: c ? c.value : '-', level: (tr.className.match(/dci-lv-(\\w+)/) || [])[1], dl,
        opts: q ? [...q.querySelectorAll('button')].map(b => [b.textContent.trim(), b.getAttribute('aria-pressed')]) : null } : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)
        a0 = pg.evaluate(Q, 'Chime Man')
        sec = f'tr.dci-row[data-row="{a0["row"]}"]' if a0 else 'tr.none'
        pg.click(f'{sec} .dci-instr-guess [data-act=instr-misc]')
        pg.wait_for_timeout(400)
        a1 = pg.evaluate(Q, 'Chime Man')
        pg.click(f'{sec} .dci-instr-guess [data-act=instr-pick][data-instr=chimes]')
        pg.wait_for_timeout(400)
        a2 = pg.evaluate(Q, 'Chime Man')
        print('A) Chaims:', a0, '| misc:', a1, '| chimes:', a2)
        results.append(bool(a0) and [o[0] for o in a0['opts']] == ['chimes', 'wind chimes', 'tubular bells', 'other instruments “chaims”', 'miscellaneous support (task “chaims”)']
                       and all(o[1] == 'false' for o in a0['opts']) and a0['type'] == 'instrument'
                       and a1['type'] == 'misc' and a1['credit'] == 'chaims' and a1['opts'][-1] == ['miscellaneous support (task “chaims”)', 'true']
                       and a2['type'] == 'instrument' and a2['instr'] == 'chimes' and a2['credit'] == '' and a2['level'] == 'recording')
        b0 = pg.evaluate(Q, 'Stick Man')
        print('B) Sticks-And-Stones:', b0)
        results.append(bool(b0) and b0['type'] == 'instrument' and b0['instr'] == 'other instruments' and b0['credit'] == 'sticks-and-stones'
                       and [o[0] for o in b0['opts']] == ['other instruments “sticks-and-stones”', 'miscellaneous support (task “sticks-and-stones”)'])
        d0 = pg.evaluate(Q, 'Tam Man')
        e0 = pg.evaluate(Q, 'Ham Man')
        if e0:
            pg.click(f'tr.dci-row[data-row="{e0["row"]}"] .dci-instr-guess [data-act=instr-misc]')
            pg.wait_for_timeout(400)
        e1 = pg.evaluate(Q, 'Ham Man')
        print('D) Tambourine [Additional, Toy]:', d0, '| E) Hammond Manager:', e0, '| misc:', e1)
        results.append(bool(d0) and d0['instr'] == 'tambourine' and d0['credit'] == 'toy'
                       and d0['dl'] == ['toy', 'additional, toy', 'additional', 'additional tambourine', 'toy tambourine'])
        results.append(bool(e0) and e0['instr'] == 'other instruments' and e0['credit'] == 'Hammond manager'
                       and [o[0] for o in e0['opts']] == ['other instruments “Hammond manager”', 'miscellaneous support (task “Hammond manager”)']
                       and e1['type'] == 'misc' and e1['credit'] == 'Hammond manager')
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Barry Guy – double bass, sticks-and-stones\nJane Roe – guitar, kalimba, buddha machine')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1000)
        g = pg.evaluate(GK_ROWS)
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        barry = [r[1:4] for r in (g.get('Barry Guy') or {'rows': []})['rows']]
        jane = [r[0] for r in (g.get('Jane Roe') or {'rows': []})['rows']]
        print('C) Barry Guy:', barry, '| Jane Roe:', jane, '| nicht erkannt:', unrec)
        results.append(barry == [['instrument', 'double bass', ''], ['instrument', 'other instruments', 'sticks-and-stones']] and jane == ['guitar']
                       and unrec == ['Jane Roe – guitar, kalimba, buddha machine → ? “kalimba”, “buddha machine”'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_casenote():
    """Credits Importer 3.34.28 (S052a/b; maintainer: ""Buddha" ist natürlich ein eigenname also großgeschrieben. generell müssen
    instrumente kleingeschrieben werden. also vielleicht deutlich machen, dass gerade etwas lowercased wurde wenn die rolle oder das
    instrument nicht bekannt ist", "S052b, Discogs-Klammern (S011): klein schreiben").
    A) Discogs "Guitar [Gretsch Duo Jet]" (until 3.35.2 "Gibson Les Paul", now a proper name of the register itself, item 144):
       guitar credited "Gretsch duo jet" (Gretsch a proper name of the register, T052), the row says "Written small – unknown to
       MusicBrainz: Duo Jet → duo jet · keep “Duo Jet” · always write “Duo Jet” · Duo → duo · keep “Duo” · … · Jet → jet …" (the
       two words one after another as a whole first, 3.35.2), the suggestions of the field written so too; in the compact line
       "written small: Duo → duo, Jet → jet" with "keep" (the whole first). B) "keep “Jet”": "Gretsch duo Jet", the note "Kept as
       written: Jet · write small again"; "write small again": "Gretsch duo jet". C) "always write “Duo”": "Duo" in the changes
       of T052 (stored), the credit "Gretsch Duo jet"; a second row with the same detail "Gretsch Duo jet" too. D) A text "Barry Guy – double bass, Sticks-And-Stones": other
       instruments “sticks-and-stones” with the note; "Jane Roe – guitar, Buddha machine": “Buddha machine” (T052), no note.
       E) Discogs "Tour Manager" (a role the register knows): no note."""
    import json
    H.attr(9124, 'other instruments', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.lt(1130, 'b367fae0-c4b0-48b9-a40c-f3ae4c02cf10', 'misc', 'artist', 'recording', (1150,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    CREDITS = [('Les Man', 'Guitar [Gretsch Duo Jet]', 3061), ('Les Two', 'Guitar [Gretsch Duo Jet]', 3062), ('Tour Man', 'Tour Manager', 3063)]
    for n, r, i in CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d

    H.discogs_release = rel
    Q = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      const tr = g && g.querySelector('tr.dci-row'); const c = tr && tr.querySelector('[data-f=role-credit]');
      const notes = tr ? [...tr.querySelectorAll('.dci-case-note')].map(n => [n.dataset.case, n.textContent.replace(/\\s+/g, ' ').trim()]) : [];
      const dl = c && c.list ? [...c.list.querySelectorAll('option')].map(o => o.value) : null;
      return tr ? { row: tr.dataset.row, credit: c ? c.value : '-', notes, dl, instr: (tr.querySelector('[data-f=primary]') || {}).value || '' } : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)
        a0 = pg.evaluate(Q, 'Les Man')
        print('A) Gretsch Duo Jet:', a0)
        results.append(bool(a0) and a0['credit'] == 'Gretsch duo jet' and len(a0['notes']) == 1 and a0['notes'][0][0] == 'small'
                       and a0['notes'][0][1] == 'Written small – unknown to MusicBrainz: Duo Jet → duo jet keep “Duo Jet” · always write “Duo Jet” · Duo → duo keep “Duo” · always write “Duo” · Jet → jet keep “Jet” · always write “Jet”'
                       and 'Gretsch duo jet guitar' in (a0['dl'] or []) and all(o == o[:1] + o[1:].lower() or o.startswith('Gretsch') for o in (a0['dl'] or [])))
        sec = f'tr.dci-row[data-row="{a0["row"]}"]' if a0 else 'tr.none'
        # the compact line
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        cl = pg.evaluate("(sel) => { const c = document.querySelector(sel + ' .dci-cl-case'); return c ? c.textContent.replace(/\\s+/g, ' ').trim() : ''; }", sec)
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        print('   kompakte Zeile:', cl)
        results.append(cl == 'written small: Duo → duo, Jet → jet keep “Duo Jet” · keep “Duo” · keep “Jet”')
        # B) keep "Jet", then small again
        pg.click(f'{sec} .dci-case-note [data-act=case-keep][data-word="Jet"]')
        pg.wait_for_timeout(300)
        b1 = pg.evaluate(Q, 'Les Man')
        pg.click(f'{sec} .dci-case-note [data-act=case-small][data-word="Jet"]')
        pg.wait_for_timeout(300)
        b2 = pg.evaluate(Q, 'Les Man')
        print('B) keep Jet:', b1, '| klein:', b2)
        results.append(bool(b1) and b1['credit'] == 'Gretsch duo Jet' and [n[0] for n in b1['notes']] == ['small', 'kept']
                       and b1['notes'][1][1].startswith('Kept as written: Jet write small again') and b2['credit'] == 'Gretsch duo jet')
        # C) always "Duo"
        pg.click(f'{sec} .dci-case-note [data-act=case-always][data-word="Duo"]')
        pg.wait_for_timeout(600)
        c1 = pg.evaluate(Q, 'Les Man')
        c2 = pg.evaluate(Q, 'Les Two')
        stored = pg.evaluate("(() => { try { return JSON.parse(localStorage.getItem('dci-mapping-changes')).lists.T052; } catch (e) { return null; } })()")
        print('C) always Duo:', c1, '| zweite Zeile:', c2, '| gespeichert:', stored)
        results.append(bool(c1) and c1['credit'] == 'Gretsch Duo jet' and c2['credit'] == 'Gretsch Duo jet' and bool(stored) and stored.get('add') == ['Duo']
                       and all('Duo →' not in n[1] for n in c1['notes']))
        e0 = pg.evaluate(Q, 'Tour Man')
        print('E) Tour Manager:', e0)
        results.append(bool(e0) and e0['notes'] == [])
        # D) texts
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Barry Guy – double bass, Sticks-And-Stones\nJane Roe – guitar, Buddha machine')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1000)
        RQ = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
          return g ? [...g.querySelectorAll('tr.dci-row')].map(tr => [(tr.querySelector('[data-f=primary]') || {}).value || '', (tr.querySelector('[data-f=role-credit]') || {}).value || '',
            [...tr.querySelectorAll('.dci-case-note')].map(n => n.textContent.replace(/\\s+/g, ' ').trim())]) : null; }"""
        barry = pg.evaluate(RQ, 'Barry Guy')
        jane = pg.evaluate(RQ, 'Jane Roe')
        print('D) Barry Guy:', barry, '| Jane Roe:', jane)
        results.append(barry == [['double bass', '', []], ['other instruments', 'sticks-and-stones',
                                  ['Written small – unknown to MusicBrainz: Sticks-And-Stones → sticks-and-stones keep “Sticks-And-Stones” · always write “Sticks-And-Stones”']]]
                       and jane == [['guitar', '', []], ['other instruments', 'Buddha machine', []]])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_casephrase():
    """Credits Importer 3.35.2 (item 144; maintainer: ""Gibson Les Paul" in dieser Groß- und Kleinschreibung bitte zu Ausnahmen
    hinzufügen, das ist ja der korrekte name.", on the hint offering the whole: "ja bitte").
    A) Discogs "Guitar [Gibson Les Paul]": the credit "Gibson Les Paul" (a proper name of several words in T052), no note.
    B) "Guitar [Les Paul Junior]": "Les Paul junior" – the name as a whole, "Junior" written small with its own note (a name of
       the register ends the words one after another). C) "Guitar [Paul Reed Smith]": "paul reed smith", the note offers the three
       words as a whole first ("Paul Reed Smith → paul reed smith · keep “Paul Reed Smith” · always write “Paul Reed Smith” ·
       Paul → paul …"), the compact line "keep “Paul Reed Smith”" first. D) "keep “Paul Reed Smith”": "Paul Reed Smith" with the
       note "Kept as written: Paul Reed Smith"; "write small again": back. E) "always write “Paul Reed Smith”": stored in the
       changes of T052, both rows with this detail "Paul Reed Smith". F) A text "Jane Roe – guitar, Les Machine": a "Les" outside
       a name of the register stays small (other instruments "les machine", the note for "Les")."""
    H.attr(9124, 'other instruments', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    CREDITS = [('Les Man', 'Guitar [Gibson Les Paul]', 3061), ('Junior Man', 'Guitar [Les Paul Junior]', 3062),
               ('Reed Man', 'Guitar [Paul Reed Smith]', 3063), ('Reed Two', 'Guitar [Paul Reed Smith]', 3064)]
    for n, r, i in CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d

    H.discogs_release = rel
    Q = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      const tr = g && g.querySelector('tr.dci-row'); const c = tr && tr.querySelector('[data-f=role-credit]');
      const notes = tr ? [...tr.querySelectorAll('.dci-case-note')].map(n => [n.dataset.case, n.textContent.replace(/\\s+/g, ' ').trim()]) : [];
      return tr ? { row: tr.dataset.row, credit: c ? c.value : '-', notes } : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)
        a0 = pg.evaluate(Q, 'Les Man')
        b0 = pg.evaluate(Q, 'Junior Man')
        print('A) Gibson Les Paul:', a0)
        print('B) Les Paul Junior:', b0)
        results.append(bool(a0) and a0['credit'] == 'Gibson Les Paul' and a0['notes'] == [])
        results.append(bool(b0) and b0['credit'] == 'Les Paul junior'
                       and b0['notes'] == [['small', 'Written small – unknown to MusicBrainz: Junior → junior keep “Junior” · always write “Junior”']])
        c0 = pg.evaluate(Q, 'Reed Man')
        print('C) Paul Reed Smith:', c0)
        results.append(bool(c0) and c0['credit'] == 'paul reed smith' and len(c0['notes']) == 1
                       and c0['notes'][0][1] == 'Written small – unknown to MusicBrainz: Paul Reed Smith → paul reed smith keep “Paul Reed Smith” · always write “Paul Reed Smith” · Paul → paul keep “Paul” · always write “Paul” · Reed → reed keep “Reed” · always write “Reed” · Smith → smith keep “Smith” · always write “Smith”')
        sec = f'tr.dci-row[data-row="{c0["row"]}"]' if c0 else 'tr.none'
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        cl = pg.evaluate("(sel) => { const c = document.querySelector(sel + ' .dci-cl-case'); return c ? c.textContent.replace(/\\s+/g, ' ').trim() : ''; }", sec)
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        print('   kompakte Zeile:', cl)
        results.append(cl == 'written small: Paul → paul, Reed → reed, Smith → smith keep “Paul Reed Smith” · keep “Paul” · keep “Reed” · keep “Smith”')
        # D) keep the whole, then small again
        pg.click(f'{sec} .dci-case-note [data-act=case-keep][data-word="Paul Reed Smith"]')
        pg.wait_for_timeout(300)
        d1 = pg.evaluate(Q, 'Reed Man')
        pg.click(f'{sec} .dci-case-note [data-act=case-small][data-word="Paul Reed Smith"]')
        pg.wait_for_timeout(300)
        d2 = pg.evaluate(Q, 'Reed Man')
        print('D) keep:', d1, '| klein:', d2)
        results.append(bool(d1) and d1['credit'] == 'Paul Reed Smith' and [n[0] for n in d1['notes']] == ['kept']
                       and d1['notes'][0][1].startswith('Kept as written: Paul Reed Smith write small again') and d2['credit'] == 'paul reed smith')
        # E) always the whole
        pg.click(f'{sec} .dci-case-note [data-act=case-always][data-word="Paul Reed Smith"]')
        pg.wait_for_timeout(600)
        e1 = pg.evaluate(Q, 'Reed Man')
        e2 = pg.evaluate(Q, 'Reed Two')
        stored = pg.evaluate("(() => { try { return JSON.parse(localStorage.getItem('dci-mapping-changes')).lists.T052; } catch (e) { return null; } })()")
        print('E) always:', e1, '| zweite Zeile:', e2, '| gespeichert:', stored)
        results.append(bool(e1) and e1['credit'] == 'Paul Reed Smith' and e1['notes'] == [] and bool(e2) and e2['credit'] == 'Paul Reed Smith'
                       and bool(stored) and stored.get('add') == ['Paul Reed Smith'])
        # F) "Les" outside a name of the register
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Jane Roe – guitar, Les Machine')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1000)
        RQ = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
          return g ? [...g.querySelectorAll('tr.dci-row')].map(tr => [(tr.querySelector('[data-f=primary]') || {}).value || '', (tr.querySelector('[data-f=role-credit]') || {}).value || '',
            [...tr.querySelectorAll('.dci-case-note')].map(n => n.textContent.replace(/\\s+/g, ' ').trim())]) : null; }"""
        jane = pg.evaluate(RQ, 'Jane Roe')
        print('F) Jane Roe:', jane)
        results.append(jane == [['guitar', '', []], ['other instruments', 'les machine', ['Written small – unknown to MusicBrainz: Les → les keep “Les” · always write “Les”']]])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_guests():
    """Credits Importer 3.37.2 (collected items 151 – 153): lines a pasted text (a booklet, the cover art) did not give before.
    A) "(P) 1998 loudsprecher (c) 1998 loudsprecher" – one entry with phonographic copyright and copyright (T033; until 3.37.1
       not recognized).
    B) "Cover-Photo: Photorama International » Photos: Dirk Glawe « Cover Design: Payola « Layout: Bernd Struckmeyer" – four
       credits (T054); "Cover-Photo" as "Cover Photo": photography "cover photo"; cover design: design "cover design".
    C) "Special Guest: M. Osswald on Sax and Piano" – M. Osswald (not "Special Guest") with saxophone ("sax") and piano, both with
       the attribute guest (S055, T053); "Guest: Jane Roe" – performer, guest; "featuring: Ann Blow on Saxophone" – saxophone,
       no guest; "Bob Blue on Piano and Saxophone" – both instruments."""
    TEXT = """(P) 1998 loudsprecher (c) 1998 loudsprecher
Cover-Photo: Photorama International » Photos: Dirk Glawe « Cover Design: Payola « Layout: Bernd Struckmeyer
Special Guest: M. Osswald on Sax and Piano
Guest: Jane Roe
featuring: Ann Blow on Saxophone
Bob Blue on Piano and Saxophone"""
    GROUPS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row')].map(r => [(r.querySelector('.dci-drole') || {}).textContent.trim(), (r.querySelector('[data-f=type]') || {}).selectedOptions?.[0]?.text || '',
    (r.querySelector('[data-f=role-credit]') || {}).value || '', (r.querySelector('[data-f=primary]') || {}).value || '',
    [...r.querySelectorAll('input[data-f=flag]:checked')].map(x => x.value).join(',')])])))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        # the row's attributes are in its open details
        pg.evaluate("[...document.querySelectorAll('tr.dci-row [data-act=row-open], tr.dci-row .dci-row-open')].forEach(b => b.click())")
        pg.wait_for_timeout(500)
        g = pg.evaluate(GROUPS)
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(l => l.textContent.trim())")
        for k in ('loudsprecher', 'Photorama International', 'Dirk Glawe', 'Payola', 'Bernd Struckmeyer', 'M. Osswald', 'Jane Roe', 'Ann Blow', 'Bob Blue', 'Special Guest'):
            print(f'  {k}:', g.get(k))
        print('nicht erkannt:', unrec)
        results.append(g.get('loudsprecher') and [r[1] for r in g['loudsprecher']] == ['phonographic copyright', 'copyright'])
        results.append(g.get('Photorama International', [[0, '', '']])[0][1:3] == ['photography', 'cover photo'] and g.get('Dirk Glawe', [[0, '']])[0][1] == 'photography'
                       and g.get('Payola', [[0, '', '']])[0][1:3] == ['design', 'cover design'] and g.get('Bernd Struckmeyer', [[0, '']])[0][1] == 'design')
        osw = g.get('M. Osswald') or []
        results.append('Special Guest' not in g and [(r[3], r[2]) for r in osw] == [('saxophone', 'sax'), ('piano', '')]
                       and all('guest' in r[4].split(',') for r in osw)
                       and (g.get('Jane Roe') or [[0, '']])[0][1] == 'performer' and 'guest' in (g.get('Jane Roe') or [[0, 0, 0, 0, '']])[0][4]
                       and [(r[3], 'guest' in r[4]) for r in g.get('Ann Blow') or []] == [('saxophone', False)]
                       and [r[3] for r in g.get('Bob Blue') or []] == ['piano', 'saxophone'] and not unrec)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
