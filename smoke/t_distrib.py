"""Credits Importer 3.17.3: "Distribution - !K7" and its variants (T028) – a label that distributes the release.
A) In Node: "Distribution - X", "Distribution: X", "Distribution by X", "Distributor: X", "Distributed by X",
   "Distributed through X", "Vertrieb: X", "Vertrieben durch X", "Distribución: X", "Distribuido por X", "Distribué par X"
   all give the company X with the role "Distributed By"; "Distribution of the songs was slow." gives nothing.
B) In the dashboard (a pasted text): "!K7" is an entry for a label with the row "Distributed By" (label → release
   "distributed", release level); the MusicBrainz label of that name is only suggested."""
import json
import subprocess
from playwright.sync_api import sync_playwright
import harness as H

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
ENTRY = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === '!K7');
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
    pg.click('[data-act=text-open]')
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
