"""Credits Importer 3.175.0 (F-PARSESTAGES, step 2): whole texts through the text reader, everything it returns compared with what is
stored (parse_golden.json) – the safety net for taking the helpers out of TEXT.parse.
A) Every text of parse_golden_texts.json (booklets, a track list of MusicBrainz, "Name-Role On Tracks", names above instruments in
   both orders and not clear – read twice, S058 –, an improvisation, prose with places and dates) and every line of text_corpus.json,
   each read three ways: as a credits text, with what the dashboard knows of the release (tracks with titles and lengths, places,
   labels, catalogue numbers, the title), and with the lines the other way round (stackUp; the lines of the corpus the first two ways) – every field of the
   result, in the order the reader gives.
B) The same with the rules S058, S222, S281, S298, S299 off.
UPDATE=1 writes the readings anew (after a change that is meant)."""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TEXTS = os.path.join(HERE, 'parse_golden_texts.json')
CORPUS = os.path.join(HERE, 'text_corpus.json')
GOLDEN = os.path.join(HERE, 'parse_golden.json')
SCRIPT = os.path.join(HERE, '..', 'mb-vibecode-credits-importer.user.js')
UPDATE = os.environ.get('UPDATE') == '1'

NODE = r"""
const off = JSON.parse(process.argv[4]);
global.localStorage = { getItem: (k) => (k === 'dci-rules-off' ? JSON.stringify(off) : null), setItem() {}, removeItem() {}, key: () => null, length: 0 };
const fs = require('fs');
const m = require(process.argv[1]);
const texts = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')).texts;
const corpus = JSON.parse(fs.readFileSync(process.argv[3], 'utf8')).lines;
const WORDS = /^(piano|bass|double bass|guitar|guitars|drums|vocals|synth|synths|saxophone|saxophones|viola|violin|cello|trumpet|trompete|posaune|horn|tuba|schlagzeug|euphonium|percussion|organ|recorder|recorders|oboe|bassoon|harpsichord|soprano|alto|tenor|flute|keyboards|computers|acoustic guitar|electric guitar|bass guitar|live drums|claviorganum|gemshorn)$/i;
const isRole = (phrase) => { const p = m.parseRoleNotation(phrase)[0]; if (!p || !p.base || /\d/.test(p.base)) return false;
  const r = m.mapRole(p.base, p.mods); return !!(r.rule && r.rule !== 'R096' && !r.fallback) || !!r.translated || WORDS.test(p.base); };
const isCompanyRole = (role) => /copyright|phonographic|published|rights society|distributed|recorded at|mixed at|mastered at|engineered at|recorded in|mixed in|mastered in|produced in|licensed|manufactured|pressed|printed/i.test(role);
const trackSet = (n) => (spec) => { const set = new Set();
  for (const part of String(spec).replace(/\b(?:tracks?)\b/gi, '').trim().split(/\s*(?:,|&|\band\b)\s*/)) { if (!part) continue;
    const r = part.match(/^(\d+)\s*(?:[-–—]|to)\s*(\d+)$/); const a = r ? Number(r[1]) : Number(part); const b = r ? Number(r[2]) : Number(part);
    if (!a || !b || b < a || b > n) return null; for (let i = a; i <= b; i++) set.add(i - 1); }
  return set.size ? set : null; };
// everything the reader returns, as it is: Sets and Maps as lists, functions and undefined left out
const plain = (v, depth = 0) => { if (depth > 12) return '…';
  if (v instanceof Set) return { $set: [...v].map((x) => plain(x, depth + 1)) };
  if (v instanceof Map) return { $map: [...v].map(([k, x]) => [plain(k, depth + 1), plain(x, depth + 1)]) };
  if (v instanceof RegExp) return String(v);
  if (Array.isArray(v)) return v.map((x) => plain(x, depth + 1));
  if (v && typeof v === 'object') { const o = {}; for (const k of Object.keys(v)) { if (typeof v[k] !== 'function' && v[k] !== undefined) o[k] = plain(v[k], depth + 1); } return o; }
  return typeof v === 'function' ? undefined : v; };
const read = (text, o, extra) => { try { return plain(m.SOURCES.text.parse(text, { isRole, isCompanyRole, resolveTracks: o.trackCount ? trackSet(o.trackCount) : () => null, resolveTitles: () => null,
  artistNames: o.artists || [], trackCount: o.trackCount || 0, ...extra })); } catch (e) { return { $error: String(e && e.message) }; } };
const out = {};
// the second reading: with what the dashboard knows of the release (its tracks with titles and lengths, places, labels, catalogue numbers, title)
const TITLES = ['Part One', 'Part Two', 'Part Three', 'Scherzo', 'Nocturne', 'March', 'Symphony', 'The Fairie Round', 'Vivace', 'Fuga', 'Andante', 'Allegro'];
const rich = (n) => ({ tracks: Array.from({ length: n || 12 }, (_, i) => ({ title: TITLES[i % TITLES.length] + (i >= TITLES.length ? ' ' + (i + 1) : ''), pos: String(i + 1), length: (180 + 37 * i) * 1000 })),
  placeNames: ['London', 'Berlin', 'Stockholm', 'Tampere', 'Hamburg'], labelNames: ['Red Priest Recordings', 'Linn', 'Virgin Records Ltd'], catnos: ['RP012', 'MCD 2301'],
  releaseTitle: 'Frag nicht nach Sonnenschein', titleNames: ['Flatlands'], ownTexts: [], players: ['Barry Guy'], oneTrack: false });
for (const t of texts) out['text: ' + t.name] = [read(t.text, t, {}), read(t.text, t, rich(t.trackCount)), read(t.text, t, { stackUp: true })];
corpus.forEach((l, i) => { out['corpus ' + i + ': ' + l.text.slice(0, 40).replace(/\n/g, ' ⏎ ')] = [read(l.text, { artists: l.artists, trackCount: 0 }, {}), read(l.text, { artists: l.artists, trackCount: 12 }, rich(12))]; });
console.log(JSON.stringify(out));
"""


def run(off):
    js = subprocess.run(['node', '-e', NODE, SCRIPT, TEXTS, CORPUS, json.dumps(off)], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-800:])
        return None
    return json.loads(js.stdout)


now = {'on': run([]), 'off': run(['S058', 'S222', 'S281', 'S298', 'S299'])}
if UPDATE:
    json.dump(now, open(GOLDEN, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('geschrieben:', GOLDEN, len(now['on'] or {}), 'Texte')
stored = json.load(open(GOLDEN, encoding='utf-8')) if os.path.exists(GOLDEN) else {}
results = []
for part, label in (('on', 'A'), ('off', 'B')):
    a, b = now.get(part) or {}, stored.get(part) or {}
    diff = [k for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
    errors = [k for k, v in a.items() if any(isinstance(x, dict) and '$error' in x for x in v)]
    print(f'{label}) Texte: {len(a)} | verschieden: {len(diff)} {diff[:5]} | Fehler beim Lesen: {errors[:5]}')
    for k in diff[:3]:
        x, y = json.dumps(a.get(k), ensure_ascii=False), json.dumps(b.get(k), ensure_ascii=False)
        i = next((n for n in range(min(len(x), len(y))) if x[n] != y[n]), min(len(x), len(y)))
        print('   ', k, '| jetzt:', x[max(0, i - 80):i + 120], '| gespeichert:', y[max(0, i - 80):i + 120])
    results.append(bool(a) and not diff and not errors)
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
