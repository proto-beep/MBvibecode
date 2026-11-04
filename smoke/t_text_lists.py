"""Texts from Bandcamp's credits of 2026-11 ("Intentions", "Throats"; Credits Importer 3.48.0 –): lines read in Node with the text
adapter, as t_textcorpus.py does (the roles: the register and a few instruments as MusicBrainz has them).

Cases: hyphen, ignorelines, linernotes (3.48.0); `python3 t_text_lists.py <case> …` runs only those."""
import json
import subprocess
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser

NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const isRole = (phrase) => { const p = m.parseRoleNotation(phrase)[0]; if (!p || !p.base || /\d/.test(p.base)) return false;
  const r = m.mapRole(p.base, p.mods); return !!(r.rule && r.rule !== 'R096' && !r.fallback) || !!r.translated
  || /^(piano|bass|guitar|drums|vocals|synth|synths|saxophone|trumpet|flute|harp|rhodes|percussion|jaw harp|highland bagpipes|bagpipes|sampler|analog synthesizer|electronic valve instrument)$/i.test(p.base); };
const isCompanyRole = (role) => /copyright|phonographic|published|rights society|distributed|recorded at|mixed at|mastered at|recorded in|mixed in|produced in/i.test(role) && !!m.mapCompanyRole(role).rule;
const trackSet = (n) => (spec) => {
  const set = new Set();
  for (const part of String(spec).trim().split(/\s*(?:,|&|\band\b)\s*/)) {
    const r = part.match(/^(\d+)\s*(?:[-–—]|to)\s*(\d+)$/);
    const a = r ? Number(r[1]) : Number(part);
    const b = r ? Number(r[2]) : Number(part);
    if (!a || !b || b < a || b > n) return null;
    for (let i = a; i <= b; i++) set.add(i - 1);
  }
  return set.size ? set : null;
};
const out = JSON.parse(process.argv[2]).map((c) => {
  const r = m.SOURCES.text.parse(c.text, { isRole, isCompanyRole, resolveTracks: trackSet(c.tracks || 14), artistNames: c.artists || [], titleNames: c.titles || [] });
  return { credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),
    companies: r.companies.map((x) => [x.who.name, x.role]), unrecognized: r.unrecognized, ignored: r.ignored.map((i) => [i.why, i.text]) };
});
console.log(JSON.stringify(out));
"""


def read(cases):
    """Each case ({text, tracks?, artists?, titles?}) through the text adapter."""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(cases)], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
        return [None] * len(cases)
    return json.loads(js.stdout)


def case_hyphen():
    """Credits Importer 3.48.0 (collected item Z-HYP): "Name -roles" – a dash with a space only before it – is "Name – roles"
    ("Makigami Koichi -harmonic overtone singing, jaw harp", "Ayako Koichi -jaw harp"); names with a dash stay whole
    ("Jean-Pierre Dupont - piano").
    Review of 3.48.0: not with a colon ("Jean -Michel Jarre: piano" read as before), not when no role follows ("Mary -Kate Olsen,
    vocals" gives no role "Kate Olsen"), not in "by" lines ("Written by Lennon -McCartney" keeps the name)."""
    got = read([{'text': 'Makigami Koichi -jaw harp, piano'}, {'text': 'Ayako Koichi -jaw harp'}, {'text': 'Jean-Pierre Dupont - piano'},
                {'text': 'Jean -Michel Jarre: piano'}, {'text': 'Mary -Kate Olsen, vocals'}, {'text': 'Written by Lennon -McCartney'}])
    for g in got:
        print('  ', g and g['credits'], g and g['unrecognized'])
    ok = [g['credits'] for g in got] == [[['Makigami Koichi', 'jaw harp'], ['Makigami Koichi', 'piano']], [['Ayako Koichi', 'jaw harp']], [['Jean-Pierre Dupont', 'piano']],
                                         [['Jean -Michel Jarre', 'piano']], [], [['Lennon -McCartney', 'Written By']]]
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_ignorelines():
    """Credits Importer 3.48.0 (collected item Z-IGN): lines without credits are left out as such, not "not recognized": the heading
    "credits", Bandcamp's "released January 13, 2022" and "published January 13, 2022", a definition ("Intention (n.) /ɪnˈtɛnʃən/")
    and its explanation in the next line, a line of gratitude ("infinite gratitude to the family, friends … Mama, Dada …").
    Review of 3.48.0: a credit after a definition is read ("John Doe (guitar)"); "Björk (v)" of a jazz list is no definition
    ("Sjón (lyrics)" read); a block of publishers ends at "released …" ("John Doe - guitar" no publisher)."""
    text = """Intention (n.) /ɪnˈtɛnʃən/
A thing intended; purpose, determination, wish, desire, resolution, ambition, dream.

credits
 released January 13, 2022
published January 13, 2022

Mastered by David Allen

infinite gratitude to the family, friends, collaborators, cities, and scenes that have supported and shaped this journey... Mama, Dada, Augie"""
    g = read([{'text': text}])[0]
    print('  ', g)
    more = read([{'text': 'Intention (n.)\nJohn Doe (guitar)'}, {'text': 'Björk (v)\nSjón (lyrics)'}, {'text': 'Publishers:\nX Music (BMI)\nreleased January 13, 2022\nJohn Doe - guitar'}])
    for x in more:
        print('  ', x and x['credits'], x and x['ignored'])
    ok = g is not None and g['credits'] == [['David Allen', 'Mastered By']] and not g['unrecognized'] \
        and [i[0] for i in g['ignored']] == ['definition', 'definition', 'heading', 'releaseDate', 'releaseDate', 'thanks'] \
        and more[0]['credits'] == [['John Doe', 'guitar']] and more[1]['credits'] == [['Sjón', 'lyrics']] and more[2]['credits'] == [['John Doe', 'guitar']]
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_linernotes():
    """Credits Importer 3.48.0 (collected item Z-LIN): "Notes by Marcus J. Moore:" – liner notes of Marcus J. Moore; the text of the
    notes after it (sentences, also with "by" in a long one) is left out as such, not read as credits nor listed as not recognized;
    a credit line among it is read ("Mastered by David Allen").
    Review of 3.48.0: a long sentence with credits after it, "Recorded at Studio X, Berlin, in May 2021." and "John Doe played guitar."
    are read – only what gives nothing is left out."""
    text = """Notes by Marcus J. Moore:

The record is a warm and patient album that maps the ground between leaving a city, finding a new one and trusting the process.

The opening song, produced by a friend from the old neighbourhood, sets the tone with bright keys and a chime that never stops.

“What if I spend time with my music?” she remembers asking herself.

In the end the album becomes its own kind of freedom.
Mastered by David Allen"""
    g = read([{'text': text}])[0]
    print('  ', g)
    more = read([{'text': 'Notes by Marcus J. Moore:\nThe record is a warm and patient album that maps the ground between leaving a city and trusting the process.\n'
                          'Produced by Jane Roe and mixed by Bob Smith at Studio X in London in 2020 for the label of the old friends from the city.\n'
                          'Recorded at Studio X, Berlin, in May 2021.\nJohn Doe played guitar.'}])[0]
    print('  ', more)
    ok = g is not None and g['credits'] == [['Marcus J. Moore', 'Notes'], ['David Allen', 'Mastered By']] and not g['unrecognized'] \
        and [i[0] for i in g['ignored']] == ['linerNotes'] * 4 \
        and ['Jane Roe', 'Produced By'] in more['credits'] and ['Bob Smith', 'Mixed By'] in more['credits'] and ['John Doe', 'guitar'] in more['credits'] \
        and ['Studio X', 'Recorded At'] in more['companies'] and [i[0] for i in more['ignored']] == ['linerNotes']
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


run_cases(globals())
