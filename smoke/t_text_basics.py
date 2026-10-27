"""Texts, part 1: a pasted text, the rules for free texts, lists of names, "credited as", distribution (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: freetext, textrules, names, textcredit, distrib – each the former smoke/t_<case>.py, unchanged; `python3 t_text_basics.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_freetext():
    """Import 3.2.0 (E1): credits from a pasted text. "Paste text …" opens a field for the text and where it is from;
    "Read text" makes it the source. Lines become rows: "Name – instrument", "Name: roles", "Role: names",
    "Written by A, mixed by B" (two clauses), "Recorded live at Place, City, date by Name" (a person and a place),
    "Mastered by A at Studio", "Tracks 3–4: Strings arranged by Z" (tracks, "Arranged By [Strings]"),
    "Published by X (1, 3)" (a company for tracks 1 and 3), "℗ 2019 Label"; a line without credits is listed as not
    recognized ([3.21.0] thanks: listed apart as left out on purpose). Names have no links: MusicBrainz entries of the same name are only suggested (dashed, yellow), a click
    assigns one. Track lists are not read again as notes (S022). The edit note names the text's origin."""
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
        ok_c = sugg.get('Bass Man') == ['Bass Man'] and sugg.get('Writer W') == ['Writer W'] and 'Peter Evans' not in sugg and 'dci-st-missing' in status \
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
       unknown part ("Barry Guy – double bass, sticks-and-stones" → double bass; "? “sticks-and-stones”").
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
        ok_b = g['Barry Guy'][0] == ['double bass'] and unrec == ['Barry Guy – double bass, sticks-and-stones → ? “sticks-and-stones”']
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


run_cases(globals())
