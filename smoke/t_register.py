"""The mapping register stays the same (golden test, Import 3.11.0).
A frozen corpus (register_corpus.json: ~1200 roles as Discogs writes them, ~100 company roles, ~50 date phrases,
pasted texts) goes through the register, and the results must equal the stored ones (register_golden.json):
A) In Node: parseRoles, mapRole, instrument candidates, role credit suggestions and options, wording, fixed credits,
   questions, detail checkboxes, the rules list (ids, kinds, patterns, types, levels, notes); mapCompanyRole; findDates
   (both orders), parseDate, parseDatePeriod; the text adapter on the texts (with the corpus' instrument names).
B) In the dashboard: the texts pasted as one source – entries, rows (role, MB type, instrument, level, tracks), not
   recognized, date pool.
C) The window "Mapping rules": every section as stored; the list of tables may only gain rows, new sections are named.
UPDATE=1 writes the results as the new golden file (after a change of the register that is meant)."""
import json
import os
import subprocess
from playwright.sync_api import sync_playwright
import harness as H

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, 'register_corpus.json')
GOLDEN = os.path.join(HERE, 'register_golden.json')
UPDATE = os.environ.get('UPDATE') == '1'

NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const corpus = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
const norm = (s) => String(s == null ? '' : s).toLowerCase().replace(/\s+/g, ' ').trim();
const ser = (x) => JSON.parse(JSON.stringify(x, (k, v) => (v instanceof Set ? [...v] : v instanceof Map ? [...v.entries()] : v instanceof RegExp ? String(v) : v)));
const sorted = (o) => Object.fromEntries(Object.entries(o).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)));
const instruments = new Set(corpus.instruments.map(norm));
const vocab = m.buildVocabulary(corpus.instruments);
const roles = {};
for (const raw of corpus.roles) {
  roles[raw] = m.parseRoles(raw).map((p) => {
    const r = m.mapRole(p.base, p.mods);
    const primary = (r.primaryCands || [])[0] || '';
    const type = (r.types || [])[0] || '';
    const suggestion = m.suggestRoleCredit(p.mods, r.consumed, primary);
    const row = { base: p.base, mods: p.mods, consumed: r.consumed, flagMods: [] };
    const q = m.questionRuleFor(row);
    const w = m.wordingRuleFor(row);
    return sorted({ raw: p.raw, base: p.base, mods: p.mods, map: sorted(ser(r)), cands: m.instrumentCandidates(p.base, p.mods),
      suggestion, options: m.roleCreditOptions(p.raw, p.base, p.mods, suggestion, type), wording: m.wordingCredit(p.base, p.mods, primary, type, vocab),
      fixed: m.fixedRoleCredit(p.base, primary), question: q ? q.id : '', wordingRule: w ? w.id : '', flags: p.mods.map(m.flagForDetail),
      cased: m.caseCredit(p.mods.join(', '), vocab) });
  });
}
const ctx0 = { b: '', ms: [], flags: [], consumed: new Set(), has: () => false, is: () => false, out: () => null, plainBase: '', modsIn: [], baseIn: '' };
const rules = m.roleRules(ctx0).map((r) => sorted({ id: r.id, kind: r.kind || '', note: r.note || '', re: r.re ? String(r.re) : '', types: r.types || [], level: r.level || '', special: r.special || '' }));
const companies = Object.fromEntries(corpus.companies.map((c) => [c, sorted(ser(m.mapCompanyRole(c)))]));
const dates = Object.fromEntries(corpus.dates.map((t) => [t, { eu: ser(m.findDates(t)), us: ser(m.findDates(t, { usOrder: true })), date: ser(m.parseDate(t)), period: ser(m.parseDatePeriod(t)) }]));
const isRole = (phrase) => {
  const p = m.parseRoleNotation(phrase)[0];
  if (!p || !p.base || /\d/.test(p.base) || p.base.split(' ').length > 6) return false;
  const r = m.mapRole(p.base, p.mods);
  if (r.rule && r.rule !== 'R096' && !r.fallback) return true;
  return m.instrumentCandidates(p.base, p.mods).some((c) => instruments.has(norm(c)));
};
const companyRe = new RegExp(corpus.textCompanyRe);
const isCompanyRole = (role) => companyRe.test(norm(role)) && !!m.mapCompanyRole(role).rule;
const resolveTracks = (spec) => {
  const nums = (String(spec).match(/\d+/g) || []).map(Number).filter((n) => n >= 1 && n <= 12);
  return nums.length ? new Set(nums.map((n) => n - 1)) : null;
};
// [3.17.0] where on its line a credit is (for the companion) is no output of the register: left out here
const noPlace = (c) => { const { part, pi, n, ...rest } = c; return rest; };
const texts = corpus.texts.map((t) => {
  const res = m.SOURCES.text.parse(t, { isRole, isCompanyRole, resolveTracks });
  return ser({ ...res, credits: res.credits.map(noPlace), companies: res.companies.map(noPlace) });
});
console.log(JSON.stringify({ roles, rules, companies, dates, texts }));
"""

ROWS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(),
  [...g.querySelectorAll('tr.dci-row')].map(tr => {
    const v = (s) => { const e = tr.querySelector(s); return e ? (e.value !== undefined ? e.value : e.textContent.trim()) : ''; };
    const lv = tr.querySelector('[data-act=level][aria-pressed=true]');
    return [v('.dci-drole'), v('[data-f=type]'), v('[data-f=primary]'), lv ? lv.dataset.level : '', v('[data-tcount]') || v('.dci-c-tracks .dci-muted')].map(x => String(x).replace(/\\s+/g, ' ').trim());
  })]))()"""


def node_part():
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), CORPUS], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-2000:])
        raise SystemExit(1)
    return json.loads(js.stdout)


def page_part():
    corpus = json.load(open(CORPUS))
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.click('[data-act=text-open]')
        pg.fill('[data-f=text-src]', '\n'.join(corpus['texts']))
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(800)
        rows = pg.evaluate(ROWS)
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => [d.name, d.begin, d.end])")
        pg.locator('[data-act=rules]').first.click()
        pg.wait_for_selector('#dci-rules [data-rsect]', timeout=10000)
        sects = pg.evaluate("Object.fromEntries([...document.querySelectorAll('#dci-rules [data-rsect]')].map(s => [s.dataset.rsect, s.innerText.split('\\n').map(x => x.replace(/\\s+/g, ' ').trim()).filter(Boolean)]))")
        b.close()
    return {'rows': rows, 'unrec': unrec, 'pool': pool}, sects, errs


def dump(obj, depth=0):
    """JSON with one entry per line down to the third level (a change shows as a changed line in a diff)."""
    one = lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True)
    if depth >= 3 or not isinstance(obj, (dict, list)) or not obj:
        return one(obj)
    pad = ' ' * (depth + 1)
    if isinstance(obj, dict):
        body = ',\n'.join(f'{pad}{one(k)}: {dump(v, depth + 1)}' for k, v in sorted(obj.items()))
        return '{\n' + body + '\n' + ' ' * depth + '}'
    return '[\n' + ',\n'.join(pad + dump(v, depth + 1) for v in obj) + '\n' + ' ' * depth + ']'


def diff_dict(name, old, new, limit=12):
    """Keys whose values differ (or are missing / new), printed with both sides."""
    bad = [k for k in sorted(set(old) | set(new)) if old.get(k) != new.get(k)]
    for k in bad[:limit]:
        print(f'   {name} ≠ {k!r}\n      vorher: {json.dumps(old.get(k), ensure_ascii=False)[:400]}\n      jetzt:  {json.dumps(new.get(k), ensure_ascii=False)[:400]}')
    if len(bad) > limit:
        print(f'   … und {len(bad) - limit} weitere')
    return not bad


a = node_part()
bpart, sects, errs = page_part()
now = {'node': a, 'page': bpart, 'rules': sects}
if UPDATE or not os.path.exists(GOLDEN):
    open(GOLDEN, 'w').write(dump(now) + '\n')
    print('Golden geschrieben:', GOLDEN, f"({len(a['roles'])} Rollen, {len(a['companies'])} Firmenrollen, {len(a['dates'])} Datumsangaben, {len(sects)} Abschnitte)")
    print('Ergebnis: OK [neu geschrieben]')
    raise SystemExit(0)
gold = json.load(open(GOLDEN))
results = []
# A) Node
ok_a = all([diff_dict('Rolle', gold['node']['roles'], a['roles']),
            diff_dict('Regel', {r['id']: r for r in gold['node']['rules']}, {r['id']: r for r in a['rules']}),
            [r['id'] for r in gold['node']['rules']] == [r['id'] for r in a['rules']] or print('   Reihenfolge der Regeln anders') is not None and False,
            diff_dict('Firma', gold['node']['companies'], a['companies']),
            diff_dict('Datum', gold['node']['dates'], a['dates']),
            diff_dict('Text', dict(enumerate(gold['node']['texts'])), dict(enumerate(a['texts'])))])
print('A) Node – Rollen', len(a['roles']), '| Regeln', len(a['rules']), '| Firmenrollen', len(a['companies']), '| Daten', len(a['dates']), '| Texte', len(a['texts']), '→', ok_a)
results.append(ok_a)
# B) dashboard
ok_b = diff_dict('Dashboard', gold['page'], bpart)
print('B) Dashboard – Einträge', len(bpart['rows']), '| nicht erkannt', len(bpart['unrec']), '| Pool', len(bpart['pool']), '→', ok_b)
results.append(ok_b)
# C) rules window: stored sections equal; the list of tables may gain rows; new sections named
old_s = gold['rules']
ok_c = True
for k, lines in old_s.items():
    cur = sects.get(k)
    if k == 'tables':
        missing = [x for x in lines if x not in (cur or [])]
        if missing:
            ok_c = False
            print('   Tabellenliste: fehlt', missing[:5])
    elif cur != lines:
        ok_c = False
        diff_dict('Abschnitt', {k: lines}, {k: cur})
new_s = [k for k in sects if k not in old_s]
print('C) Regelfenster – Abschnitte', len(sects), '| neu:', new_s, '→', ok_c)
results.append(ok_c)
print('Fehler:', errs)
results.append(not errs)
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
