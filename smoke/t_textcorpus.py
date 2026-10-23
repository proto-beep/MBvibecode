"""Credits Importer 3.21.0: text recognition, part 1 – a corpus of credits lines (text_corpus.json; golden test).
A) In Node: every line of the corpus through the text adapter (credits, companies, web links, not recognized, left out on
   purpose) equals its stored reading ('expect'; UPDATE=1 writes it anew after a change that is meant). Lines marked
   'later' (33d, 33e) are stored as they are read today. The dates: "“Madison” 1988" gives none (D016), "© 2023" does.
B) In the dashboard, the Maya Recordings credits pasted as a text: one line with four sentences gives Albert Irvin (cover
   art – the title and its year, "courtesy of …" left out), Jonas Schoder, Evan Parker ("Text": the question liner notes
   or lyrics, nothing assumed), Maya Homburger and Barry Guy (produced); "P + ©" gives ℗ and © for Maya Recordings
   (without the address, "DDD" and "· MCD 2301"); thanks and the strings are listed as left out on purpose, nothing as
   not recognized; the date pool has 2023 but not 1988.
C) "Logo by Cole Barrington instagram.com/blueeyedhorse84": the name without the address, design with the credit "logo";
   the profile is shown at the entry, MusicBrainz has an artist with it – the first suggestion, marked "via
   instagram.com", nothing assigned.
D) "Create artist …" for Jane Roe fills in her Instagram profile; for John Doe (only Linktree) no link.
E) "Text" answered with "lyricist": the row goes to the works matrix."""
import json
import os
import re
import subprocess
import urllib.parse
from playwright.sync_api import sync_playwright
import harness as H

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, 'text_corpus.json')
UPDATE = os.environ.get('UPDATE') == '1'
SCRIPT = os.path.join(HERE, '..', 'mb-vibecode-credits-importer.user.js')

NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const corpus = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
// roles as the dashboard knows them (the register; a few instruments as MusicBrainz has them)
const isRole = (phrase) => { const p = m.parseRoleNotation(phrase)[0]; if (!p || !p.base || /\d/.test(p.base)) return false;
  const r = m.mapRole(p.base, p.mods); return !!(r.rule && r.rule !== 'R096' && !r.fallback) || !!r.translated || /^(piano|bass|guitar|drums|vocals|synth|saxophone|viola|trumpet)$/i.test(p.base); };
const isCompanyRole = (role) => /copyright|phonographic|published|distributed|recorded at|mixed at|mastered at|pressed|manufactured|licensed/i.test(role) && !!m.mapCompanyRole(role).rule;
const out = corpus.lines.map((l) => {
  const r = m.SOURCES.text.parse(l.text, { isRole, isCompanyRole, resolveTracks: () => null });
  // [3.21.2] a translation (T034) with the English term it is mapped as
  const term = (c) => { const x = m.mapRole(c.base, c.details); return x.translated ? [x.translatedBase ? `= ${x.translatedBase}` : `= ? (asked, ${x.rule})`] : []; };
  return { credits: r.credits.map((c) => [c.who.name || `(${c.who.placeholder})`, c.role, ...(c.who.links.length ? [c.who.links] : []), ...term(c)]),
    companies: r.companies.map((c) => [c.who.name, c.role]), unrecognized: r.unrecognized, ignored: r.ignored };
});
const all = corpus.lines.map((l) => l.text).join('\n');
const dates = m.findDates(all).map((d) => `${d.rule} ${JSON.stringify((d.value || {}).begin || d.value)}`);
console.log(JSON.stringify({ out, dates }));
"""

corpus = json.load(open(CORPUS))
res = json.loads(subprocess.run(['node', '-e', NODE, SCRIPT, CORPUS], capture_output=True, text=True, check=True).stdout)
results = []
# A)
diff = []
for line, got in zip(corpus['lines'], res['out']):
    if UPDATE:
        line['expect'] = got
    elif line.get('expect') != got:
        diff.append((line['text'][:60], line.get('expect'), got))
if UPDATE:
    json.dump(corpus, open(CORPUS, 'w'), ensure_ascii=False, indent=2)
    open(CORPUS, 'a').write('\n')
    print('A) neu geschrieben:', len(corpus['lines']), 'Zeilen')
for d in diff:
    print('A) ABWEICHUNG:', d)
years = [d for d in res['dates'] if '"year":1988' in d]
print('A) Zeilen:', len(corpus['lines']), '| Abweichungen:', len(diff), '| Daten mit 1988:', years, '| mit 2023:', any('"year":2023' in d for d in res['dates']))
results.append(not diff and not years and any('"year":2023' in d for d in res['dates']))

COLE = H.uid('cccccccc', 77)
H.WEB_URLS['https://www.instagram.com/blueeyedhorse84/'] = (COLE, 'Cole Barrington')
TEXT = """Cover art: “Madison” 1988 by Albert Irvin, courtesy of the Albert Irvin Estate. Graphic design: Jonas Schoder. Text: Evan Parker. Produced by Maya Homburger and Barry Guy.
Thanks to Mike Eden, Romana Bellinger, Caroline Forbes, Victoria Long at Gimpel Fils, London, Celia Irvin and Priscilla Hashmi.
Barry Guy plays exclusively on Thomastik-Infeld bass strings.
www.maya-recordings.com P + © 2023 Maya Recordings DDD · MCD 2301
Logo by Cole Barrington instagram.com/blueeyedhorse84
Photography by Jane Roe https://www.instagram.com/janeroe/ and John Doe (linktr.ee/johndoe)"""
GROUPS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => ({ name: g.querySelector('.dci-gname strong').textContent.trim(),
  key: g.dataset.group, status: g.className.match(/dci-st-(\\w+)/)[1],
  rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const c = tr.querySelector('[data-f=role-credit]');
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', c ? c.value : '',
      (tr.querySelector('.dci-type-ask') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim()]; }),
  web: [...g.querySelectorAll('.dci-weblink')].map(a => [a.textContent, a.href]),
  sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => [b.dataset.mbid, (b.querySelector('.dci-similar') || { textContent: '' }).textContent]) })))()"""
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.click('[data-act=text-open]')
    pg.fill('[data-f=text-src]', TEXT)
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    pg.wait_for_timeout(800)
    g = {x['name']: x for x in pg.evaluate(GROUPS)}
    for x in g.values():
        print('   ', x['name'], x['status'], x['rows'], x['web'], x['sugg'])
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    ign = pg.evaluate("[...document.querySelectorAll('.dci-ignored li')].map(li => li.textContent)")
    ign_title = pg.evaluate("(document.querySelector('.dci-ignored summary') || {}).textContent")
    pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => JSON.stringify(d.begin))")
    print('B) nicht erkannt:', unrec, '| ausgelassen:', ign_title, ign, '| Pool:', pool)
    roles = lambda n: [r[0] for r in g.get(n, {'rows': []})['rows']]
    ok_b = roles('Albert Irvin') == ['Cover art'] and roles('Jonas Schoder') == ['Graphic design'] and roles('Evan Parker') == ['Text'] \
        and roles('Maya Homburger') == ['Produced By'] and roles('Barry Guy') == ['Produced By'] \
        and sorted(roles('Maya Recordings')) == ['Copyright (c)', 'Phonographic Copyright (p)'] \
        and 'liner notes' in g['Evan Parker']['rows'][0][3] and 'lyricist' in g['Evan Parker']['rows'][0][3] \
        and unrec == [] and ign_title == '2 lines left out on purpose' and ign[0].startswith('Thanks to Mike Eden') and ign[1].startswith('Barry Guy plays') \
        and any('"year":2023' in d for d in pool) and not any('"year":1988' in d for d in pool)
    # C) the logo, its profile and the suggestion through it
    cole = g.get('Cole Barrington', {})
    logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'web link' in x]
    print('C) Cole Barrington:', cole.get('rows'), cole.get('web'), cole.get('sugg'), cole.get('status'), '|', logs)
    ok_c = cole.get('rows') == [['Logo By', 'design', 'logo', '']] and cole.get('web') == [['instagram.com/blueeyedhorse84', 'https://www.instagram.com/blueeyedhorse84/']] \
        and (cole.get('sugg') or [[None]])[0] == [COLE, 'via instagram.com'] and cole.get('status') == 'missing' \
        and logs == ['Cole Barrington: MusicBrainz artist with the web link from the text (only a suggestion): Cole Barrington (instagram.com/blueeyedhorse84)']

    # D) "Create artist …" with the profile
    def form(key):
        pg.click(f'section[data-group="{key}"] [data-act=artist-create]')
        pg.wait_for_selector('[data-el=sub]:not([hidden])', timeout=20000)
        url = pg.evaluate("document.querySelector('[data-el=sub-frame]').src")
        info = pg.evaluate("document.querySelector('[data-el=sub-info]').textContent")
        pg.click('[data-act=sub-close]')
        pg.wait_for_timeout(200)
        q = urllib.parse.urlparse(url)
        return q.path, dict(urllib.parse.parse_qsl(q.query)), info
    jane = form(g['Jane Roe']['key'])
    john = form(g['John Doe']['key'])
    print('D) Jane Roe:', jane[0], jane[1], '|', re.sub(r'\s+', ' ', jane[2])[:120])
    print('   John Doe:', john[1])
    ok_d = jane[0] == '/artist/create' and jane[1].get('edit-artist.url.0.text') == 'https://www.instagram.com/janeroe/' and 'edit-artist.url.1.text' not in jane[1] \
        and '1 web link found next to the name in the text' in jane[2] \
        and not any(k.startswith('edit-artist.url') for k in john[1]) and g['Jane Roe']['web'] == [['instagram.com/janeroe', 'https://www.instagram.com/janeroe/']] \
        and g['John Doe']['web'] == []
    # E) "Text" → lyricist: to the works matrix
    pg.click(f"section[data-group=\"{g['Evan Parker']['key']}\"] [data-act=type-pick][data-opt='1']")
    pg.wait_for_timeout(800)
    after = {x['name']: x for x in pg.evaluate(GROUPS)}
    in_matrix = pg.evaluate("[...document.querySelectorAll('.dci-matrix th[data-colhead]')].some(th => /Evan Parker/.test(th.textContent))")
    print('E) Evan Parker danach:', after.get('Evan Parker', {}).get('rows'), '| in der Werk-Matrix:', in_matrix)
    ok_e = after.get('Evan Parker', {}).get('rows') == [] and in_matrix
    print('B)', ok_b, '| C)', ok_c, '| D)', ok_d, '| E)', ok_e)
    results += [ok_b, ok_c, ok_d, ok_e]
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
