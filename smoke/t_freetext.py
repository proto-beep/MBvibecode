"""Import 3.2.0 (E1): credits from a pasted text. "Paste text …" opens a field for the text and where it is from;
"Read text" makes it the source. Lines become rows: "Name – instrument", "Name: roles", "Role: names",
"Written by A, mixed by B" (two clauses), "Recorded live at Place, City, date by Name" (a person and a place),
"Mastered by A at Studio", "Tracks 3–4: Strings arranged by Z" (tracks, "Arranged By [Strings]"),
"Published by X (1, 3)" (a company for tracks 1 and 3), "℗ 2019 Label"; a line without credits is listed as not
recognized ([3.21.0] thanks: listed apart as left out on purpose). Names have no links: MusicBrainz entries of the same name are only suggested (dashed, yellow), a click
assigns one. Track lists are not read again as notes (S022). The edit note names the text's origin."""
import re
from playwright.sync_api import sync_playwright
import harness as H

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
ROWS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
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
    pg.click('[data-act=text-open]')
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
    ign = pg.evaluate("[...document.querySelectorAll('.dci-ignored li')].map(li => li.textContent)")
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
    status = pg.evaluate("[...document.querySelectorAll('section.dci-group')].filter(g => g.querySelector('.dci-gname strong').textContent === 'Bass Man').map(g => g.className)[0]")
    look = pg.evaluate("(() => { const b = document.querySelector('[data-act=name-use]'); const s = getComputedStyle(b); return [s.borderTopStyle, s.backgroundColor]; })()")
    bm = pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(g => g.querySelector('.dci-gname strong').textContent === 'Bass Man').dataset.group")
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
