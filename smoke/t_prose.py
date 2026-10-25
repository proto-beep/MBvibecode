"""Credits Importer 3.29.0 (milestone "Text recognition, part 3"): credits in prose, places of joined verbs, lists of kinds
(collected items 70, 71, 76, 77; the texts of ekstasis, Erosion and Antifascist Freedom Music on Bandcamp, pasted).
A) "A chronicle of rabid deeds, dutifully unearthed from accursed crossroads' soil by K.M. (sounds, words) & E. (voice)."
   → K.M. performer and lyricist, E. vocals (S038, T041; [3.30.6] the performer row is "Sounds", asked – Q008); "Cover artwork channeled by Drahmarduk." → artwork credited
   "cover artwork" (R103, T042); "Logo carved by the guided hand of BMS Illustration." → BMS Illustration, design
   credited "logo" (T042).
B) "Mixed and mastered at TQA.HQ (July 2026). Thanks to EXEcentrer and Isohyet." → TQA.HQ mixed at and mastered at (S039),
   July 2026 in the date matrix under Mix and under Mastering (D020); the thanks left out.
C) "Frank Trompeter: Tenor, alto, soprano saxophones" → tenor, alto and soprano saxophone, no role credit (S040);
   "Richard Gilman-Opalsky: Drums, percussion, and wood flutes" → flute credited "wood flutes".
D) "Mixed and mastered by Brandon Carnes in March 2026." → mix and mastering, March 2026 under Mix and Mastering.
E) Nothing listed as not recognized.
F) [3.29.1] "Assembled by Kai Lurk (noises, electronics) & Fen Field (field recordings)." → Kai Lurk effects credited
   "noises" and electronic instruments credited "electronics", Fen Field field recordist (T041)."""
from playwright.sync_api import sync_playwright
import harness as H

for i, n in [(9130, 'tenor saxophone'), (9131, 'soprano saxophone'), (9122, 'flute'), (9123, 'percussion'), (9124, 'effects'), (9125, 'electronic instruments')]:
    H.attr(i, n, 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
H.lt(1202, '1d4c0b5b-0000-4000-8000-000000001202', 'artwork', 'artist', 'release', (1, 1150))
H.lt(1204, '1d4c0b5b-0000-4000-8000-000000001204', 'mastered at', 'place', 'release', ())
H.lt(1205, '1d4c0b5b-0000-4000-8000-000000001205', 'field recordist', 'artist', 'recording', (1,))
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
TEXT = """A chronicle of rabid deeds, dutifully unearthed from accursed crossroads' soil by K.M. (sounds, words) & E. (voice).
Cover artwork channeled by Drahmarduk.
Logo carved by the guided hand of BMS Illustration.
Mixed and mastered at TQA.HQ (July 2026). Thanks to EXEcentrer and Isohyet.
Frank Trompeter: Tenor, alto, soprano saxophones
Richard Gilman-Opalsky: Drums, percussion, and wood flutes
Mixed and mastered by Brandon Carnes in March 2026.
Assembled by Kai Lurk (noises, electronics) & Fen Field (field recordings)."""
ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const p = tr.querySelector('[data-f=primary]');
    const c = tr.querySelector('[data-f=role-credit]');
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', p ? p.value : '', c ? c.value : '-']; })])))()"""
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
    pg.wait_for_timeout(1500)
    g = pg.evaluate(ROWS)
    for k, v in g.items():
        print('   ', k, v)
    cols = pg.evaluate("[...document.querySelectorAll('[data-colhead]')].map(x => x.textContent.replace(/\\s+/g, ' ').trim().slice(0, 40))")
    role = lambda n: [x[0] for x in g.get(n, [])]
    # A)
    a1 = [role('K.M.'), g.get('E.'), g.get('Drahmarduk'), g.get('BMS Illustration')]
    print('A) Prosa:', a1, '| Werke-Spalten:', cols)
    results.append('Sounds' in role('K.M.') and ['Sounds', 'performer'] in [x[:2] for x in g.get('K.M.', [])] and any('K.M.' in c for c in cols) and (g.get('E.') or [[]])[0][:2] == ['Vocals', 'vocal']
                   and (g.get('Drahmarduk') or [[]])[0][1:4:2] == ['artwork', 'cover artwork'] and (g.get('BMS Illustration') or [[]])[0][1:4:2] == ['design', 'logo'])
    # B) + D) places and dates
    pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]')")
    mx = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-matrix:{H.REL}') || '{{}}')")
    byId = {d['id']: d for d in pool}
    # (the cells of the text: those of 2026 – the Discogs release loaded before it has 2001)
    cells = sorted(x for x in ((c['col'], '-'.join(str(y) for y in (byId[c['date']]['begin']['year'], byId[c['date']]['begin']['month']))) for c in mx.get('cells', [])) if x[1].startswith('2026'))
    print('B/D) TQA.HQ:', g.get('TQA.HQ'), '| Matrix:', cells)
    results.append([x[0] for x in g.get('TQA.HQ', [])] == ['Mixed At', 'Mastered At']
                   and cells == [('mastering', '2026-3'), ('mastering', '2026-7'), ('mix', '2026-3'), ('mix', '2026-7')])
    # C)
    c1 = [x[1:] for x in g.get('Frank Trompeter', [])]
    c2 = g.get('Richard Gilman-Opalsky', [])
    print('C) Saxophone:', c1, '| wood flutes:', c2)
    results.append(c1 == [['instrument', 'tenor saxophone', ''], ['instrument', 'alto saxophone', ''], ['instrument', 'soprano saxophone', '']]
                   and c2[-1][1:] == ['instrument', 'flute', 'wood flutes'] and len(c2) == 3)
    d1 = role('Brandon Carnes')
    print('D) Brandon Carnes:', d1)
    results.append(d1 == ['Mixed By', 'Mastered By'])
    # F) [3.29.1]
    f1 = [g.get('Kai Lurk'), g.get('Fen Field')]
    print('F) Kai Lurk, Fen Field:', f1)
    results.append([x[1:] for x in (f1[0] or [])] == [['instrument', 'effects', 'noises'], ['instrument', 'electronic instruments', 'electronics']]
                   and [x[1] for x in (f1[1] or [])] == ['field recordist'])
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    print('E) nicht erkannt:', unrec)
    results.append(not unrec)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
