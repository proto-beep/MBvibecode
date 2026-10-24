"""Credits Importer 3.28.2: roles in Norwegian, Swedish and Danish, case-only names, an instrument by its last word
(collected items 58, 59, 78; Windir "1184" as on Discogs, "Antifascist Freedom Music" as on Bandcamp).
A) Discogs: "Graphics [Grafisk Utforming]" graphic design, "Mastered By [Mastering Av]" mastering, "Mixed By [Miksa Av]"
   mix, "Producer [Produsert Av]" producer – the bracket only names the role in Norwegian: no role credit (S032);
   "Vocals [Clean]", "Vocals [Screams]" with the credits "clean", "screams" in lower case (S034).
B) "Artwork [Logo Og Kunst]" (Norwegian: logo and art) is two rows: design with the credit "logo" and artwork with the
   credit "art"; each says the role as written on Discogs (S033). On the Discogs page (companion) its line has two marks.
C) Only the case differs from MusicBrainz: "VALFAR" (credited as, ANV) for Valfar, "KUNST MANN" for Kunst Mann, the
   label "Voices Of Wonder" (Distributed By) for Voices of Wonder – no "credited as" (S031); "M. Mann" for Master Mann
   stays. Typed in by hand, "VALFAR" stays.
D) "Wood Flute" (Discogs) is the instrument flute with the role credit "wood flute" (S035).
E) A pasted text: "Drums, percussion, and wood flutes" – flute credited "wood flutes" (S035); "Miksa av: X" mix without
   role credit (S032); "Logo og kunst: Y" design "logo" and artwork "art" (S033)."""
from playwright.sync_api import sync_playwright
import harness as H

H.attr(9122, 'flute', 14, 14)
H.attr(9123, 'percussion', 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
for i, gid, name, t0, lvl, attrs in [(1201, '1d4c0b5b-0000-4000-8000-000000001201', 'graphic design', 'artist', 'release', (1, 526, 1150)),
                                     (1202, '1d4c0b5b-0000-4000-8000-000000001202', 'artwork', 'artist', 'release', (1, 1150)),
                                     (1203, '1d4c0b5b-0000-4000-8000-000000001203', 'distributed', 'label', 'release', ())]:
    H.lt(i, gid, name, t0, lvl, attrs)
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
for i, n in [(3011, 'Grafik Mann'), (3012, 'Master Mann'), (3013, 'Mix Mann'), (3014, 'Kunst Mann'), (3015, 'Valfar'), (3016, 'Flute Frau')]:
    H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
H.COMPANIES[1006] = ('label', H.uid('eeeeeeee', 6), 'Voices of Wonder')
CREDITS = [('Grafik Mann', 'Graphics [Grafisk Utforming]', 3011, ''), ('Master Mann', 'Mastered By [Mastering Av]', 3012, 'M. Mann'),
           ('Mix Mann', 'Mixed By [Miksa Av]', 3013, ''), ('KUNST MANN', 'Artwork [Logo Og Kunst]', 3014, ''),
           ('Bob Producer', 'Producer [Produsert Av]', 3005, ''), ('Valfar', 'Vocals [Clean]', 3015, 'VALFAR'),
           ('Valfar', 'Vocals [Screams]', 3015, 'VALFAR'), ('Flute Frau', 'Wood Flute', 3016, '')]
orig = H.discogs_release


def rel():
    d = orig()
    d['extraartists'] = [{'name': n, 'anv': anv, 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i, anv in CREDITS]
    d['companies'] = [{'name': 'Voices Of Wonder', 'entity_type_name': 'Distributed By', 'id': 1006, 'catno': ''}]
    for t in d['tracklist']:
        t['extraartists'] = []
    return d


def page():
    lis = ''.join(f'<li><span>{r}</span> – <a href="/artist/{i}-{n.replace(" ", "-")}">{anv or n}</a></li>' for n, r, i, anv in CREDITS)
    rows = ''.join(f'<tr data-track-position="{i + 1}"><td>{i + 1}</td><td>{t}</td></tr>' for i, t in enumerate(H.TITLES))
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>Discogs</title></head><body><h1>Test Band – Testalbum</h1>'
            f'<section id="release-tracklist"><table>{rows}</table></section><section id="release-credits"><ul>{lis}</ul>'
            '<h2>Companies, etc.</h2><ul><li><span>Distributed By</span> – <a href="/label/1006-x">Voices Of Wonder</a></li></ul></section></body></html>')


H.discogs_release = rel
H.discogs_page = page
TEXT = """Richard Gilman-Opalsky: Drums, percussion, and wood flutes
Miksa av: Ola Nordmann
Logo og kunst: Kari Nordmann"""
ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const p = tr.querySelector('[data-f=primary]');
    const c = tr.querySelector('[data-f=role-credit]'); const cr = tr.querySelector('[data-f=credit]'); const sp = [...tr.querySelectorAll('.dci-sub')].find(x => /one row per task/.test(x.textContent));
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', p ? p.value : '', c ? c.value : '-', cr ? cr.value : '-',
      sp ? sp.textContent.trim() : '']; })])))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg, dgerr = H.open_discogs(ctx)
    pg, errs = H.open_mb_edit(ctx, companion=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(1500)
    g = pg.evaluate(ROWS)
    for k, v in g.items():
        print('   ', k, v)
    row = lambda name, i=0: ((g.get(name) or []) + [['', '', '', '', '', '']] * (i + 1))[i]
    # A)
    a = [row('Grafik Mann'), row('Master Mann'), row('Mix Mann'), row('Bob Producer'), row('Valfar', 0), row('Valfar', 1)]
    print('A) nordisch:', [x[:4] for x in a])
    results.append(a[0][1] == 'graphic design' and a[0][3] in ('', '-') and a[1][1] == 'mastering' and a[1][3] in ('', '-')
                   and a[2][1] == 'mix' and a[2][3] in ('', '-') and a[3][1] == 'producer' and a[3][3] in ('', '-')
                   and a[4][:4] == ['Vocals [Clean]', 'vocal', a[4][2], 'clean'] and a[5][:4] == ['Vocals [Screams]', 'vocal', a[5][2], 'screams'])
    # B)
    k = g.get('Kunst Mann') or g.get('KUNST MANN') or []
    poll = lambda js: H.wait_for(dg, js, 20)
    poll("document.querySelectorAll('#release-credits .dci-dg-mark').length >= 9")
    marks = dg.evaluate("""[...document.querySelectorAll('#release-credits li')].map(li => [li.querySelector('span').textContent, li.querySelectorAll('.dci-dg-mark').length])""")
    print('B) Kunst:', k, '| Zeichen auf Discogs:', marks)
    results.append([x[:4] for x in k] == [['Design [Logo]', 'design', '', 'logo'], ['Artwork [Art]', 'artwork', '', 'art']]
                   and all('Artwork [Logo Og Kunst]' in x[5] for x in k) and dict(marks).get('Artwork [Logo Og Kunst]') == 2)
    # C) case only
    vow = g.get('Voices Of Wonder') or g.get('Voices of Wonder') or []
    c1 = [row('Valfar', 0)[4], row('Valfar', 1)[4], [x[4] for x in k], [x[4] for x in vow], row('Master Mann')[4]]
    sec = "section.dci-group:has(.dci-gname strong:text-is('Valfar'))"
    f = pg.locator(f'{sec} tr.dci-row').nth(0).locator('[data-f=credit]')
    f.fill('VALFAR')
    f.dispatch_event('change')
    pg.wait_for_timeout(600)
    c2 = pg.evaluate(ROWS).get('Valfar')[0][4]
    print('C) credited as – Valfar, Kunst, Voices of Wonder, Master Mann:', c1, '| von Hand:', c2)
    results.append(c1 == ['', '', ['', ''], [''], 'M. Mann'] and c2 == 'VALFAR')
    # D)
    d1 = row('Flute Frau')
    print('D) Wood Flute:', d1[:4])
    results.append(d1[:4] == ['Wood Flute', 'instrument', 'flute', 'wood flute'])
    # E) a pasted text
    H.src_menu(pg, 'text-open')
    pg.fill('[data-f=text-src]', TEXT)
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(1500)
    e = pg.evaluate(ROWS)
    for k2, v in e.items():
        print('   ', k2, v)
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    ro = e.get('Richard Gilman-Opalsky') or []
    print('E) Text:', [x[:4] for x in ro], '| Ola:', [x[:4] for x in e.get('Ola Nordmann') or []], '| Kari:', [x[:4] for x in e.get('Kari Nordmann') or []], '| nicht erkannt:', unrec)
    results.append([x[:4] for x in ro][-1:] == [['wood flutes', 'instrument', 'flute', 'wood flutes']] and len(ro) == 3
                   and [x[:2] + [x[3]] for x in e.get('Ola Nordmann') or []] in ([['Miksa av', 'mix', '']], [['Miksa av', 'mix', '-']])
                   and [x[:4] for x in e.get('Kari Nordmann') or []] == [['Design [Logo]', 'design', '', 'logo'], ['Artwork [Art]', 'artwork', '', 'art']]
                   and not unrec)
    print('Fehler:', errs, dgerr)
    results.append(not errs and not dgerr)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
