"""Credits Importer 3.28.5: dates in the notes (collected items 64a, 64d, 80, 71, 76).
A) In Node: "Recorded 19 & 20. 01. 2009." → 2009-01-19 – 2009-01-20 (D013, as "June 16 & 19"); "20. 01. 2009" (D002 with
   spaces); "Recorded: London - 1973 October 19" → 1973-10-19 (D017); "originally issued on LP in 1974" and "Released
   2003" give no date (D018); "Mixed May 2001. Released 2003." – no group from the sentence before (D019); "Mixed and
   mastered by Brandon Carnes in March 2026." → Mix and Mastering, "Recorded, mixed and mastered 2001" → all three (D020);
   "Recorded at X:" on the line before "12 June 2001" still names the group.
B) The dashboard: Discogs notes "Recorded 19 & 20. 01. 2009. Mixed and mastered in March 2010. Originally issued on LP in
   2011." – the date matrix has 2009-01-19 – 2009-01-20 under Performance and March 2010 under Mix and under Mastering
   (each its own pool entry, named for its group); 2011 is not in the pool."""
import json
import subprocess
from playwright.sync_api import sync_playwright
import harness as H

NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const T = ['Recorded 19 & 20. 01. 2009.', 'Recorded 20. 01. 2009.', 'Recorded: London - 1973 October 19', 'Tracks 1-4 originally issued on LP in 1974.', 'Released 2003',
  'Mixed May 2001. Released 2003. Dedicated to Jim, 1999.', 'Mixed and mastered by Brandon Carnes in March 2026.', 'Recorded, mixed and mastered 2001', 'Recorded at X:\n12 June 2001'];
const v = (d) => [d.value.begin, d.value.end].map((x) => [x.year, x.month, x.day].filter((y) => y != null).join('-')).join('/');
console.log(JSON.stringify(T.map((t) => m.findDates(t).map((d) => [d.text, d.rule, v(d), d.hint, d.hints]))));
"""
a = json.loads(subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True, check=True).stdout)
for x in a:
    print('   ', x)
results = []
want = [[['19 & 20. 01. 2009', 'D013', '2009-1-19/2009-1-20', 'performance', []]],
        [['20. 01. 2009', 'D002', '2009-1-20/2009-1-20', 'performance', []]],
        [['1973 October 19', 'D017', '1973-10-19/1973-10-19', 'performance', []]],
        [], [],
        [['May 2001', 'D008', '2001-5/2001-5', 'mix', []], ['1999', 'D010', '1999/1999', '', []]],
        [['March 2026', 'D008', '2026-3/2026-3', 'mastering', ['mix', 'mastering']]],
        [['2001', 'D010', '2001/2001', 'mastering', ['performance', 'mix', 'mastering']]],
        [['12 June 2001', 'D004', '2001-6-12/2001-6-12', 'performance', []]]]
print('A) Node:', a == want)
results.append(a == want)
orig = H.discogs_release


def rel():
    d = orig()
    d['notes'] = 'Recorded 19 & 20. 01. 2009. Mixed and mastered in March 2010. Originally issued on LP in 2011.'
    return d


H.discogs_release = rel
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(1500)
    pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]')")
    mx = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-matrix:{H.REL}') || '{{}}')")
    byId = {d['id']: d for d in pool}
    fmt = lambda d: '/'.join('-'.join(str(x) for x in (e['year'], e['month'], e['day']) if x) for e in (d['begin'], d['end']))
    cells = sorted((c['col'], byId[c['date']]['name'], fmt(byId[c['date']])) for c in mx.get('cells', []))
    names = sorted((d['name'], fmt(d)) for d in pool)
    print('B) Matrix:', cells, '| Pool:', names)
    results.append(cells == [('mastering', 'Mastering 1', '2010-3/2010-3'), ('mix', 'Mix 1', '2010-3/2010-3'), ('performance', 'Performance 1', '2009-1-19/2009-1-20')]
                   and not any('2011' in n[1] for n in names))
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
