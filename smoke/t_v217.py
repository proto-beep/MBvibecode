"""Import 2.17.0, mapping and small things: "Mixed By [Mixing]" → mix without role credit (S019); "Bass Guitar" asks
bass guitar · electric bass guitar · acoustic bass guitar, without a choice it stays bass guitar without credit
(Q004); "Trombone [Additonal Musicians]" → additional (S002); "All Music By" → composer (R003); "©© Fuzzoramarecords
2005" in the notes is a copyright date (D015), the label name gives no "recorded" hint; "‹ n rows incomplete ›" goes
through the incomplete rows (1/2, 2/2) and marks what is missing; Escape closes "Mapping rules" first, then the
dashboard; the text size goes down to 50 %."""
import re
from playwright.sync_api import sync_playwright
import harness as H

for i, n in [(9110, 'bass guitar'), (9111, 'trombone')]:
    H.attr(i, n, 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
orig = H.discogs_release


def rel():
    d = orig()
    ex = lambda name, role, i: {'name': name, 'anv': '', 'role': role, 'tracks': '', 'id': i, 'join': ''}
    d['extraartists'] += [ex('Keys Guy', 'Mixed By [Mixing]', 3003), ex('Guitar Guy', 'Bass Guitar', 3002),
                          ex('Bass Man', 'Trombone [Additonal Musicians]', 3001), ex('Writer W', 'All Music By', 3007),
                          ex('Drum Guy', 'Directed By', 3004), ex('Nobody Known', 'Vocals', 3999)]
    d['notes'] += ' ©© Fuzzoramarecords 2005.'
    return d


H.discogs_release = rel
ROWS = """[...document.querySelectorAll('section.dci-group tr.dci-row')].map(tr => { const v = (f) => { const e = tr.querySelector('[data-f=' + f + ']');
  return e ? (e.tagName === 'SELECT' ? (e.options[e.selectedIndex] || {}).text : e.value) : '-'; };
  return [tr.querySelector('.dci-drole').textContent.trim(), v('type'), v('primary'), v('role-credit'),
    [...tr.querySelectorAll('input[data-f=flag]:checked')].map(c => c.value).join(','), [...tr.querySelectorAll('.dci-ruleid')].map(x => x.textContent).join(' '),
    (tr.querySelector('.dci-bass-ask:not(.dci-type-ask)') || {}).innerText || '']; })"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    by = {r[0]: r for r in pg.evaluate(ROWS)}
    for k in ['Mixed By [Mixing]', 'Bass Guitar', 'Trombone [Additonal Musicians]', 'Bass']:
        print('  ', by.get(k))
    mix, bg, tb, bass = by.get('Mixed By [Mixing]'), by.get('Bass Guitar'), by.get('Trombone [Additonal Musicians]'), by.get('Bass')
    ok1 = mix and mix[1] == 'mix' and mix[3] in ('', '-') and 'S019' in mix[5] \
        and bg and bg[2] == 'bass guitar' and bg[3] == '' and 'Q004' in bg[5] and 'bass guitar · electric bass guitar · acoustic bass guitar' in bg[6] and 'without a role credit' in bg[6] \
        and tb and tb[2] == 'trombone' and 'additional' in tb[4] and 'S002' in tb[5] \
        and bass and bass[2] == 'bass' and bass[3] == '' and 'Q001' in bass[5]
    # a choice: electric bass guitar, credited as "bass guitar"
    row = pg.locator('tr.dci-row').filter(has=pg.locator('.dci-drole', has_text='Bass Guitar')).first
    row.locator('[data-act=instr-pick]', has_text='electric bass guitar').click(); pg.wait_for_timeout(300)
    bg2 = {r[0]: r for r in pg.evaluate(ROWS)}['Bass Guitar']
    print('1b) gewählt:', bg2[:4])
    ok1 = ok1 and bg2[2] == 'electric bass guitar' and bg2[3] == 'bass guitar'
    # R003: "All Music By" → composer (works matrix)
    wcol = pg.evaluate("[...document.querySelectorAll('[data-colhead]')].filter(h => h.textContent.includes('Writer W')).map(h => h.innerText.replace(/\\s+/g, ' ').slice(0, 60))")
    print('1c) Spalte Writer W:', wcol)
    ok1 = ok1 and any('composer' in x for x in wcol)
    print('1) Mapping:', ok1)
    results.append(ok1)

    # 2) D015: "©© Fuzzoramarecords 2005" is a copyright date
    pg.click('[data-el=datefind] summary')
    items = [re.sub(r'\s+', ' ', i) for i in pg.locator('[data-el=datefind-list] li').all_inner_texts()]
    print('2) Gefunden:', items)
    hit = [i for i in items if '2005' in i]
    ok2 = len(hit) == 1 and '(D010 · D015)' in hit[0] and 'in the matrix: ℗/©' in hit[0] and not any('in the matrix: Performance' in i and '2005' in i for i in items)
    results.append(bool(ok2))

    # 3) incomplete rows: "Directed By" (choose a type) and an artist not in MusicBrainz
    s = lambda: re.sub(r'\s+', ' ', pg.locator('[data-el=sum]').inner_text())
    print('3) Zusammenfassung:', s())
    seen = []
    for _ in range(3):
        pg.evaluate("document.querySelectorAll('.dci-flash').forEach(e => e.classList.remove('dci-flash'))")
        pg.click('[data-el=sum] [data-act=inc-next] >> nth=-1'); pg.wait_for_timeout(300)
        fl = pg.evaluate("""[...document.querySelectorAll('.dci-flash')].map(e => e.matches('tr.dci-row') ? 'row:' + e.querySelector('.dci-drole').textContent.trim()
          : e.matches('[data-match]') ? 'artist' : e.className.split(' ').find(c => c.startsWith('dci-c-')) || e.tagName)""")
        seen.append((re.search(r'\d/\d', s()).group(0) if re.search(r'\d/\d', s()) else '', sorted(fl)))
    print('   ›, ›, ›:', seen)
    pg.click('[data-el=sum] [data-act=inc-prev]'); pg.wait_for_timeout(300)
    back = re.search(r'\d/\d', s()).group(0)
    print('   ‹:', back)
    ok3 = '2 rows incomplete' in s() and [x[0] for x in seen] == ['1/2', '2/2', '1/2'] and back == '2/2' \
        and {tuple(x[1]) for x in seen[:2]} == {('artist', 'row:Vocals'), ('dci-c-type', 'row:Directed By')}
    results.append(ok3)

    # 4) Escape: "Mapping rules" first, then the dashboard; text size down to 50 %
    for _ in range(9):
        pg.click('[data-act=zoom-out]')
    zoom = pg.locator('[data-el=zoom]').inner_text()
    pg.click('[data-act=rules]'); pg.wait_for_timeout(200)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    e1 = [pg.locator('#dci-rules').is_hidden(), pg.locator('#dci-overlay').is_visible()]
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    e2 = pg.locator('#dci-overlay').is_hidden()
    print('4) Zoom:', zoom, '| Escape 1 (Regeln zu, Dashboard offen):', e1, '| Escape 2 (Dashboard zu):', e2)
    results.append(zoom == '50 %' and e1 == [True, True] and e2)
    print('Fehler:', errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
