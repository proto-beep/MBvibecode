"""Credits Importer 3.30.8: dates per disc and places from the Discogs notes (collected item 98; Wadada Leo Smith with
Milford Graves and Bill Laswell, "Sacred Ceremonies", Discogs 18973900, three CDs; answers of 2026-10-25 08:55).
Notes: "All music recorded ... at Orange Music Sound Studios in West Orange, New Jersey, on May 27, 2016 (Disc 1), May 26,
2016 (Disc 2) and December 11 & 12, 2015 (Disc 3) / All music mastered ... at Turtle Tone Studio in New York City /
Including a 52 p. booklet. / © & ℗ TUM Records Oy 2021".
A) Each of the three dates goes under Performance (D021) with the tracks of its disc ("Medium 2 · CD"); December 11 & 12,
   2015 is a period; no message about dates without a group (until 3.30.7 only the first date
   had a group, all three the tracks of disc 1).
B) The places of the notes (S042): Orange Music Sound Studios (recorded at; West Orange, New Jersey) and Turtle Tone Studio
   (mastered at; New York City) – Discogs does not list them.
C) Discogs lists "Recorded At – Orange Music Sound Studios" and "Mixed At – Turtle Tone Studio": no second entry, no second
   "Recorded At" row; "Mastered At" from the notes joins Discogs's entry of Turtle Tone Studio.
D) Pasted as a text: the place line is recognized, "Including a 52 p. booklet." is left out on purpose ("about the
   package")."""
from playwright.sync_api import sync_playwright
import harness as H

H.MEDIA = [2, 1, 1]
NOTES = """All music recorded ... at Orange Music Sound Studios in West Orange, New Jersey, on May 27, 2016 (Disc 1), May 26, 2016 (Disc 2) and December 11 & 12, 2015 (Disc 3)
All music mastered ... at Turtle Tone Studio in New York City

Including a 52 p. booklet.

© & ℗ TUM Records Oy 2021"""
H.COMPANIES[1011] = ('place', H.uid('eeeeeeee', 11), 'Orange Music Sound Studios')
H.COMPANIES[1012] = ('place', H.uid('eeeeeeee', 12), 'Turtle Tone Studio')
H.lt(1206, '1d4c0b5b-0000-4000-8000-000000001206', 'mastered at', 'place', 'release', ())
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
WITH_COMPANIES = [False]
orig = H.discogs_release


def rel():
    d = orig()
    for i, t in enumerate(d['tracklist']):
        t['position'] = ['1-1', '1-2', '2-1', '3-1'][i]
    d['notes'] = NOTES
    d['companies'] = [c for c in d['companies'] if c['entity_type_name'] not in ('Recorded At', 'Phonographic Copyright (p)')]
    if WITH_COMPANIES[0]:
        d['companies'] += [{'name': 'Orange Music Sound Studios', 'entity_type_name': 'Recorded At', 'id': 1011, 'catno': ''},
                           {'name': 'Turtle Tone Studio', 'entity_type_name': 'Mixed At', 'id': 1012, 'catno': ''}]
    return d


H.discogs_release = rel
GROUPS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim()), ((g.querySelector('.dci-gname .dci-sub') || {}).textContent || '').trim()]))()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(1200)
    pool = {d['id']: d for d in pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]')")}
    tgs = {g['id']: g for g in pg.evaluate(f"JSON.parse(localStorage.getItem('dci-track-pool:{H.REL}') || '[]')")}
    cells = pg.evaluate(f"(JSON.parse(localStorage.getItem('dci-date-matrix:{H.REL}') || '{{}}').cells || [])")
    day = lambda d: '-'.join(str(x) for x in (d['begin']['year'], d['begin']['month'], d['begin']['day'])) + ('/' + str(d['end']['day']) if d['end'].get('day') != d['begin'].get('day') else '')
    perf = sorted((day(pool[c['date']]), [(tgs[t]['name'], tgs[t]['tracks']) for t in c['tgs']], len(c.get('alt') or [])) for c in cells if c['col'] == 'performance')
    msgs = pg.locator('.dci-msg').all_inner_texts()
    print('A) Performance:', perf, '| Meldungen:', [m[:70] for m in msgs])
    results.append([x[:2] for x in perf] == [('2015-12-11/12', [('Medium 3 · CD', [3])]), ('2016-5-26', [('Medium 2 · CD', [2])]), ('2016-5-27', [('Medium 1 · CD', [0, 1])])]
                   and not any('no word naming' in m for m in msgs))
    g = pg.evaluate(GROUPS)
    places = [x for x in g if x[0] in ('Orange Music Sound Studios', 'Turtle Tone Studio')]
    print('B) Orte:', places)
    results.append(places == [['Orange Music Sound Studios', ['Recorded At'], '(West Orange, New Jersey)'], ['Turtle Tone Studio', ['Mastered At'], '(New York City)']])
    # D) the same as a pasted text
    H.src_menu(pg, 'text-open')
    pg.fill('[data-f=text-src]', NOTES)
    pg.click('[data-act=text-load]')
    H.answer_media(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(1200)
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    left = pg.evaluate("[...document.querySelectorAll('.dci-unrec, .dci-ignored, details')].map(x => x.textContent.replace(/\\s+/g, ' ')).join(' | ')")
    g2 = [x[0] for x in pg.evaluate(GROUPS)]
    print('D) Text – nicht erkannt:', unrec, '| Einträge:', g2, '| ausgelassen:', 'about the package' in left)
    results.append(not any('Orange Music' in u or 'booklet' in u for u in unrec) and 'Orange Music Sound Studios' in g2 and 'about the package' in left)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()

# C) Discogs lists the places already
WITH_COMPANIES[0] = True
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(1200)
    g = pg.evaluate(GROUPS)
    places = [x[:2] for x in g if x[0] in ('Orange Music Sound Studios', 'Turtle Tone Studio')]
    print('C) mit Discogs-Firmen:', places)
    results.append(places == [['Orange Music Sound Studios', ['Recorded At']], ['Turtle Tone Studio', ['Mixed At', 'Mastered At']]])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
