"""Credits Importer 3.28.6: track groups in the notes, "Facets" as on Discogs (collected items 64b, 64c).
Sides A–F, side D one track without a number ("D"). The notes: "A1 to B1 recorded 22nd May 1981 in live concert at
Goldsmith's College, London" / "C1 to D recorded 4th October 1979 at Heiman Recording Studios, London" / "E1 to F1
recorded 2nd May 1980 at Heiman Recording Studios, London".
A) The date matrix: three dates under Performance, each with its track group – A1–B1 (tracks 1–2), C1–D (3–5: "D" is the
   end of the range), E1–F1 (6–7).
B) "in live concert" names tracks: "live" is offered for the existing link of track 1 (its sentence names A1–B1) with
   that reason – not for the whole release.
C) No places or areas from the notes (no entry for Goldsmith's College, Heiman Recording Studios or London)."""
from playwright.sync_api import sync_playwright
import harness as H

POS = ['A1', 'B1', 'C1', 'C2', 'D', 'E1', 'F1']
H.TITLES[:] = ['Part One', 'Part Two', 'Organic', 'Trisect', 'Ontology', 'Part Six', 'Part Seven']
H.REC[:] = [H.uid('bbbbbbbb', i) for i in range(1, 8)]
H.attr(578, 'live', 578)
H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (578,))
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
NOTES = ("A1 to B1 recorded 22nd May 1981 in live concert at Goldsmith's College, London\n"
         "C1 to D recorded 4th October 1979 at Heiman Recording Studios, London\n"
         "E1 to F1 recorded 2nd May 1980 at Heiman Recording Studios, London")
orig = H.discogs_release


def rel():
    d = orig()
    d['notes'] = NOTES
    d['tracklist'] = [{'position': p, 'title': t, 'type_': 'track', 'duration': '5:00', 'extraartists': []} for p, t in zip(POS, H.TITLES)]
    d['companies'] = [c for c in d['companies'] if c['entity_type_name'] != 'Recorded At']
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
    pg.wait_for_timeout(2000)
    pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]')")
    tgs = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-track-pool:{H.REL}') || '[]')")
    mx = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-matrix:{H.REL}') || '{{}}')")
    byId = {d['id']: d for d in pool}
    tgById = {g['id']: g for g in tgs}
    day = lambda d: '-'.join(str(x) for x in (d['begin']['year'], d['begin']['month'], d['begin']['day']))
    cells = sorted((c['col'], day(byId[c['date']]), [(tgById[t]['name'], tgById[t]['tracks']) for t in c['tgs']]) for c in mx.get('cells', []))
    print('A) Matrix:', cells)
    results.append(cells == [('performance', '1979-10-4', [('Tracks C1–D', [2, 3, 4])]), ('performance', '1980-5-2', [('Tracks E1–F1', [5, 6])]),
                             ('performance', '1981-5-22', [('Tracks A1–B1', [0, 1])])])
    # B) "live" offered on track 1's existing link, for its tracks
    live = pg.evaluate("""[...document.querySelectorAll('.dci-wpill[data-attr=live]')].map(x => [x.textContent.trim(), x.title])""")
    print('B) live:', live)
    results.append(any('li?' in t and 'these tracks were recorded live' in title and 'Live recording' in title for t, title in live))
    # C) no places or areas from the notes
    names = pg.evaluate("[...document.querySelectorAll('section.dci-group .dci-gname strong')].map(x => x.textContent.trim())")
    print('C) Einträge:', names)
    results.append(not any(n in names for n in ("Goldsmith's College", 'Heiman Recording Studios', 'London')))
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
