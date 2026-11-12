"""Texts from Bandcamp's credits of 2026-11 ("Intentions", "Throats"; Credits Importer 3.48.0 –): lines read in Node with the text
adapter, as t_textcorpus.py does (the roles: the register and a few instruments as MusicBrainz has them).

Cases: hyphen, ignorelines, linernotes (3.48.0), rolesplit, roles, places, oldmarks, exceptread, exceptworks, exceptlayouts, rolesplit2,
exceptworks2 (3.49.0); prose, trackartists, prose2, trackartists2 (3.50.0); placecredit (3.51.0); `python3 t_text_lists.py <case> …` runs only those."""
import json
import subprocess
import harness as H  # noqa: F401 – used by the cases
H.NO_ANIM = True  # [3.77.0] (Z-FLK) reading and mapping: no transitions or animations to wait for
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser

NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const isRole = (phrase) => { const p = m.parseRoleNotation(phrase)[0]; if (!p || !p.base || /\d/.test(p.base)) return false;
  const r = m.mapRole(p.base, p.mods); return !!(r.rule && r.rule !== 'R096' && !r.fallback) || !!r.translated
  || /^(?:additional\s+)?(piano|bass|guitar|drums|vocals|synth|synths|saxophone|trumpet|flute|harp|rhodes|percussion|jaw harp|highland bagpipes|bagpipes|sampler|analog synthesizer|electronic valve instrument|juno|evi|double bass|bass guitar|baritone electric guitar)$/i.test(p.base); };
const isCompanyRole = (role) => /copyright|phonographic|published|rights society|distributed|recorded at|mixed at|mastered at|recorded in|mixed in|produced in|broadcast by/i.test(role) && !!m.mapCompanyRole(role).rule;
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
  (c.off || []).forEach((id) => m.setRuleOff && m.setRuleOff(id, true));
  const r = m.SOURCES.text.parse(c.text, { isRole, isCompanyRole, resolveTracks: trackSet(c.tracks || 14), artistNames: c.artists || [], titleNames: c.titles || [] });
  return { credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),
    companies: r.companies.map((x) => [x.who.name, x.role, ...(x.entity ? [x.entity] : [])]), unrecognized: r.unrecognized, ignored: r.ignored.map((i) => [i.why, i.text]) };
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


def case_rolesplit():
    """Credits Importer 3.49.0 (collected item Z-RTL): several roles with their own tracks in one line – "ghalani of Greenwood - bass
    (3, 7, 8, 9), additional bass (11)", "megiapa - production (2-14), vocals (1-14)": each role on its tracks; one track list for
    all ("Will Miller - trumpet, EVI, additional piano (7)") stays as it was."""
    got = read([{'text': 'ghalani of Greenwood - bass (3, 7, 8, 9), additional bass (11)'}, {'text': 'megiapa - production (2-14), vocals (1-14)'},
                {'text': 'Will Miller - trumpet, EVI, additional piano (7)'}])
    for g in got:
        print('  ', g and g['credits'], g and g['unrecognized'])
    ok = got[0]['credits'] == [['ghalani of Greenwood', 'bass', '3, 7, 8, 9'], ['ghalani of Greenwood', 'additional bass', '11']] \
        and got[1]['credits'] == [['megiapa', 'production', '2-14'], ['megiapa', 'vocals', '1-14']] \
        and got[2]['credits'] == [['Will Miller', 'trumpet', '7'], ['Will Miller', 'EVI', '7'], ['Will Miller', 'additional piano', '7']] \
        and not any(g['unrecognized'] for g in got)
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_roles():
    """Credits Importer 3.49.0 (collected item Z-ROL; Q-eu, Q-fa, Q-fe): production and instrumental production – producer; composition –
    composer; "vocal sample" – samples from artist (R109; "contains samples by"); "drums / drum sample" of one person – drums and
    sampler; harmonic overtone singing – a voice (R011); Juno – analog synthesizer, credited "Juno" ([3.81.0] by R113, a model – its
    alias first); EVI – electronic valve instrument;
    highland bagpipes – Great Highland bagpipe."""
    node = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const out = ['production', 'instrumental production', 'composition', 'vocal sample', 'harmonic overtone singing', 'Juno', 'EVI', 'highland bagpipes'].map((r) => {
  const p = m.parseRoleNotation(r)[0]; const x = m.mapRole(p.base, p.mods); return [r, x.rule, x.types, (x.primaryCands || [])[0] || ''];
});
out.push(['juno credit', m.fixedRoleCredit('Juno', 'analog synthesizer')]);
console.log(JSON.stringify(out));
"""
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1200:])
    got = json.loads(js.stdout) if not js.returncode else []
    for g in got:
        print('  ', g)
    lines = read([{'text': 'Mekala Session - drums / drum sample (2, 11,13)'}, {'text': 'Juliana Markwardt - vocal sample (2)'}])
    print('  ', lines[0]['credits'], lines[1]['credits'])
    want = [['production', 'R026', ['producer'], ''], ['instrumental production', 'R026', ['producer'], ''], ['composition', 'R003', ['composer', 'writer'], ''],
            ['vocal sample', 'R109', ['samples from artist'], ''], ['harmonic overtone singing', 'R011', ['vocal'], 'harmonic overtone singing'],
            ['Juno', 'R113', ['instrument'], 'analog synthesizer'], ['EVI', 'R096', ['instrument'], 'electronic valve instrument'],
            ['highland bagpipes', 'R096', ['instrument'], 'great highland bagpipe'], ['juno credit', 'Juno']]
    ok = got == want and lines[0]['credits'] == [['Mekala Session', 'drums', '2, 11,13'], ['Mekala Session', 'sampler', '2, 11,13']] \
        and lines[1]['credits'] == [['Juliana Markwardt', 'vocal sample', '2']]
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_places():
    """Credits Importer 3.49.0 (collected item Z-RPB): "Recorded and produced by megiapa between Chicago and Los Angeles" – megiapa recorded
    and produced, Chicago and Los Angeles recorded in (no names "megiapa between Chicago", "Los Angeles"); "Additional recording by Viraj
    Gandhi at Chakram's Aarti HQ" – the place recorded at (the verb after "additional"); "Artwork and photos by megiapa"."""
    got = read([{'text': 'Recorded and produced by megiapa between Chicago and Los Angeles'}, {'text': "Additional recording by Viraj Gandhi at Chakram's Aarti HQ"},
                {'text': 'Artwork and photos by megiapa'}])
    for g in got:
        print('  ', g and g['credits'], g and g['companies'], g and g['unrecognized'])
    ok = got[0]['credits'] == [['megiapa', 'Recorded By'], ['megiapa', 'Produced By']] and got[0]['companies'] == [['Chicago', 'Recorded In'], ['Los Angeles', 'Recorded In']] \
        and got[1]['credits'] == [['Viraj Gandhi', 'Additional recording']] and got[1]['companies'] == [["Chakram's Aarti HQ", 'Recorded At']] \
        and got[2]['credits'] == [['megiapa', 'Artwork By'], ['megiapa', 'Photos By']]
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_oldmarks():
    """Credits Importer 3.49.0 (S069, from Z-BUL): a text copied with the companion's marks before 1.13.0 kept them out – several and
    without a space ("○○○○Telemakus - harp (8)", "○Aankha Neal - additional vocals (5,13)", "✓●Bass Man - bass"): the names without
    them."""
    got = read([{'text': '○○○○Telemakus - harp (8)\n○Aankha Neal - additional vocals (5,13)\n✓●Bass Man - bass'}])[0]
    print('  ', got and got['credits'])
    ok = got is not None and [c[0] for c in got['credits']] == ['Telemakus', 'Aankha Neal', 'Bass Man'] and not got['unrecognized']
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


EXCEPT_TEXT = """All compositions and lyrics by Writer W except:

Song Two
Written by Kevin Toney
Originally performed by The Blackbyrds

Song Three
End quote from Space Is the Place by Sun Ra

Song Four
Written by Charles Stepney and Richard Rudolph
Originally performed by The New Rotary Connection
Arranged by Mocky

Recorded and produced by Writer W between Chicago and Los Angeles"""


TITLES_NODE_SCOPE = "resolveTracks: trackSet(c.tracks || 14), trackCount: c.count || 0, resolveTitles: c.titles ? ((ts) => { const ix = new Set(); const un = []; ts.forEach((t) => { const k = c.titles.findIndex((x) => x.toLowerCase() === t.toLowerCase()); if (k >= 0) ix.add(k); else un.push(t); }); return { indexes: ix, unresolved: un }; }) : null,"


def read_titles(cases):
    """Like read, with the titles of the tracks (c.titles) and their number (c.count) – credits with their track indexes ('all'), their
    part and its number, covers and quotes."""
    node = NODE.replace("resolveTracks: trackSet(c.tracks || 14),", TITLES_NODE_SCOPE)
    node = node.replace("credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),",
                        "credits: r.credits.map((x) => [x.who.name, x.role, x.tracks && x.tracks.indexes ? x.tracks.indexes.join(',') : 'all']), parts: r.credits.map((x) => [x.part, x.pi]), covers: r.covers.map((x) => [x.title, x.by, x.arranged]), quotes: r.quotes.map((x) => [x.title, x.work, x.by]),")
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(cases)], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
        return [None] * len(cases)
    return json.loads(js.stdout)


def case_exceptlayouts():
    """Review of 3.49.0 (collected item Z-EXC): the blocks of "All … by X except:" in other layouts, in Node.
    A) blocks without empty lines between them – each title starts its block ("Song Three" no line not recognized, B on track 3 only);
    B) an empty line between a title and its credits – they stay with it (A not on all tracks);
    C) the title with its number, in quotation marks, with a colon ("2. “Song Two”:");
    D) two headers ("All music by A except:" … "All lyrics by B except:") – each with its own blocks, A not lost;
    E) a title of no track of the release – the header not read (listed as not recognized), X on no track;
    F) "Originally recorded by The Blackbyrds in 1975", "… (1975)": a cover, never a credit of this release; "End quote from Stand by Me
       by Ben E. King" – the work up to the last "by"; "Original Mix" no cover."""
    T = ['Song One', 'Song Two', 'Song Three', 'Song Four']
    texts = ['All compositions by X except:\nSong Two\nWritten by A\nSong Three\nWritten by B',
             'All compositions by X except:\nSong Two\n\nWritten by A',
             'All compositions by X except:\n2. “Song Two”:\nWritten by A',
             'All music by A except:\nSong Two\nComposed by C\n\nAll lyrics by B except:\nSong Three\nLyrics by D',
             'All compositions by X except:\nSong Nine\nWritten by A',
             'All compositions by X except:\nSong Two\nOriginally recorded by The Blackbyrds in 1975\nOriginally performed by The Blackbyrds (1975)\nEnd quote from Stand by Me by Ben E. King\n\nSong Three\nOriginal Mix']
    got = read_titles([{'text': t, 'titles': T, 'count': 4} for t in texts])
    for g in got:
        print('  ', g and g['credits'], g and g['unrecognized'], g and g['covers'], g and g['quotes'])
    if None in got:
        print('Ergebnis: FEHLER', [False])
        return
    srt = lambda g: sorted(g['credits'])
    ok = [srt(got[0]) == [['A', 'Written By', '1'], ['B', 'Written By', '2'], ['X', 'Composed By', '0,3']] and not got[0]['unrecognized'],
          srt(got[1]) == [['A', 'Written By', '1'], ['X', 'Composed By', '0,2,3']],
          srt(got[2]) == [['A', 'Written By', '1'], ['X', 'Composed By', '0,2,3']],
          srt(got[3]) == [['A', 'Composed By', '0,2,3'], ['B', 'Lyrics By', '0,1,3'], ['C', 'Composed By', '1'], ['D', 'Lyrics By', '2']],
          not any(c[0] == 'X' for c in got[4]['credits']) and 'All compositions by X except:' in got[4]['unrecognized'],
          srt(got[5]) == [['X', 'Composed By', '0,3']] and got[5]['covers'] == [['Song Two', 'The Blackbyrds', False], ['Song Two', 'The Blackbyrds', False]]
          and got[5]['quotes'] == [['Song Two', 'Stand by Me', 'Ben E. King']] and got[5]['unrecognized'] == ['Original Mix']]
    print('Ergebnis:', 'OK' if all(ok) else 'FEHLER', ok)


def case_rolesplit2():
    """Review of 3.49.0 (collected item Z-RTL): each part of the line marked where it stands (its own text and number – the companion
    finds it in the line: before, "Name - additional bass" was found nowhere); a part not read named ("→ ? “guitar (2019)”", before
    the whole line); "vocals (1), and backing vocals (2)" – both (before: backing vocals lost). [Z-ROL] "vocals, vocal samples": material
    sampled (R109), no sampler. [Z-RPB] "between Takes at Studio X and Home": no areas – the place recorded at stays (as in 3.48.0)."""
    got = read_titles([{'text': 'ghalani of Greenwood - bass (3, 7, 8, 9), additional bass (11)', 'tracks': 14},
                       {'text': 'Jane Roe - guitar (2019), bass (3)', 'tracks': 14},
                       {'text': 'Jane Roe - vocals (1), and backing vocals (2)', 'tracks': 14},
                       {'text': 'Jane Roe - vocals, vocal samples', 'tracks': 14},
                       {'text': 'Recorded by X between Takes at Studio X and Home', 'tracks': 14}])
    for g in got:
        print('  ', g and g['credits'], g and g['parts'], g and g['companies'], g and g['unrecognized'])
    if None in got:
        print('Ergebnis: FEHLER', [False])
        return
    ok = [got[0]['parts'] == [['ghalani of Greenwood - bass (3, 7, 8, 9)', 0], ['additional bass (11)', 1]],
          got[1]['credits'] == [['Jane Roe', 'bass', '2']] and got[1]['unrecognized'] == ['Jane Roe - guitar (2019), bass (3) → ? “guitar (2019)”'],
          got[2]['credits'] == [['Jane Roe', 'vocals', '0'], ['Jane Roe', 'backing vocals', '1']],
          [c[1] for c in got[3]['credits']] == ['vocals', 'vocal samples'],
          not any(c[1] == 'Recorded In' for c in got[4]['companies']) and ['Studio X and Home', 'Recorded At'] in got[4]['companies']]
    print('Ergebnis:', 'OK' if all(ok) else 'FEHLER', ok)


def case_exceptread():
    """Credits Importer 3.49.0 (collected item Z-EXC; Q-ev, Q-fb, Q-fg, Q-fi): "All compositions and lyrics by X except:" and the blocks
    of the tracks below it, in Node. X composer and lyricist of the other tracks only; "Written by" in a block for its track;
    "Originally performed by …" no credit (a cover of the track; with "Arranged by" on its track an arrangement); "End quote from
    Space Is the Place by Sun Ra" no credit (a quote of the track); the titles and those lines left out as such. [Z-RPB] "between
    Chicago and Los Angeles": two areas recorded in, the name without them."""
    titles = ['Song One', 'Song Two', 'Song Three', 'Song Four']
    node = NODE.replace("resolveTracks: trackSet(c.tracks || 14),", "resolveTracks: trackSet(c.tracks || 14), trackCount: c.count || 0, resolveTitles: c.titles ? ((ts) => { const ix = new Set(); const un = []; ts.forEach((t) => { const k = c.titles.findIndex((x) => x.toLowerCase() === t.toLowerCase()); if (k >= 0) ix.add(k); else un.push(t); }); return { indexes: ix, unresolved: un }; }) : null,")
    node = node.replace("credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),",
                        "credits: r.credits.map((x) => [x.who.name, x.role, x.tracks && x.tracks.indexes ? x.tracks.indexes.join(',') : 'all']), covers: r.covers.map((x) => [x.title, x.by, x.arranged]), quotes: r.quotes.map((x) => [x.title, x.work, x.by]),")
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps([{'text': EXCEPT_TEXT, 'titles': titles, 'count': 4}])], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout)[0] if not js.returncode else None
    print('  ', g)
    ok = g is not None and sorted(g['credits']) == sorted([['Kevin Toney', 'Written By', '1'], ['Charles Stepney', 'Written By', '3'], ['Richard Rudolph', 'Written By', '3'],
                                                         ['Mocky', 'Arranged By', '3'], ['Writer W', 'Recorded By', 'all'], ['Writer W', 'Produced By', 'all'],
                                                         ['Writer W', 'Composed By', '0'], ['Writer W', 'Lyrics By', '0']]) \
        and g['covers'] == [['Song Two', 'The Blackbyrds', False], ['Song Four', 'The New Rotary Connection', True]] and g['quotes'] == [['Song Three', 'Space Is the Place', 'Sun Ra']] \
        and sorted(g['companies']) == [['Chicago', 'Recorded In'], ['Los Angeles', 'Recorded In']] and not g['unrecognized'] \
        and [i[0] for i in g['ignored']] == ['exceptTitle', 'cover', 'exceptTitle', 'quote', 'exceptTitle', 'cover']
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_exceptworks():
    """Credits Importer 3.49.0 (collected item Z-EXC; Q-ev, Q-ff, Q-fg, Q-fh, Q-fi): the same text pasted in the dashboard.
    A) Writer W composer and lyricist only of track 1 (the works matrix), Kevin Toney writer of track 2, the writers and the arranger of
       track 4 on it; The Blackbyrds and The New Rotary Connection no entry (no performers of this release).
    B) The works matrix: track 2 "Cover – originally performed by The Blackbyrds"; track 3 "Quotes lyrics from “Space Is the Place”
       (Sun Ra)" with the work found in MusicBrainz; track 4 an arrangement – "Arrangement of “Song Four”" with the original found.
    C) New works for tracks 2–4, staged: track 2's link with "cover" (567), track 4's without; the work of track 3 "quotes lyrics
       from" Space Is the Place (1047, it is entity0), the original of track 4 "has arrangement" its new work (350, the original is
       entity0); the edit note names the covers and the arrangement. (Review of 3.49.0: the original entity0 by its id – the new work has
       its name too –, the quoting work entity0; the edit note counts both: "linked 2 works with the works they arrange or quote".)"""
    SUNRA = H.uid('5a5a5a5a', 1)
    SPACE = H.uid('cccccccc', 90)
    ORIG4 = H.uid('cccccccc', 91)
    STEPNEY = H.uid('5a5a5a5a', 2)
    H.lt(350, '51975ed8-bbfa-486b-9f28-5947f4370299', 'arrangement', 'work', 'work', ())
    H.lt(1047, 'c8283596-6ad1-4e09-8d49-3a7f7a1b1047', 'lyrical quotation', 'work', 'work', ())
    for i, n in [(567, 'cover'), (578, 'live')]:
        H.attr(i, n, i)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.WORK_SEARCH[:] = [{'id': SPACE, 'title': 'Space Is the Place', 'aliases': [], 'relations': [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': SUNRA, 'name': 'Sun Ra'}}]},
                        {'id': ORIG4, 'title': 'Song Four', 'aliases': [], 'relations': [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': STEPNEY, 'name': 'Charles Stepney'}}]}]
    H.JS_WORKS.update({SPACE: (7090, 'Space Is the Place'), ORIG4: (7091, 'Song Four')})
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    ENTRIES = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [(g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()),
      [...g.querySelectorAll('tr.dci-row')].map(tr => [tr.querySelector('.dci-drole').dataset.raw.trim(), (tr.querySelector('[data-tcount]') || { textContent: '' }).textContent.trim()])])))()"""
    NOTES = "[...document.querySelectorAll('tr[data-work] .dci-mx-wnote')].map(n => [n.closest('tr').dataset.work, n.dataset.wnote, n.dataset.wstate || '', n.textContent.replace(/\\s+/g, ' ').trim()])"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', EXCEPT_TEXT)
        pg.click('[data-act=text-load]')
        H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= 2", 60)
        pg.wait_for_timeout(2500)
        e = pg.evaluate(ENTRIES)
        mx = pg.evaluate("(() => { const heads = [...document.querySelectorAll('th.dci-mx-col')].map(t => t.textContent.replace(/\\s+/g, ' ').trim()); return { heads, rows: [...document.querySelectorAll('tr[data-work]')].map(tr => [tr.dataset.work, [...tr.querySelectorAll('td[data-col]')].map(td => td.className + '|' + td.textContent.trim())]) }; })()")
        on = lambda word: sorted(r[0] for r in mx['rows'] if any('dci-mx-on' in c.split('|')[0] and c.split('|')[1].startswith(word) for c in r[1]))
        print('A) Einträge:', sorted(e), '| Werke-Matrix composer+lyricist:', on('composerlyricist'), '| writer:', on('writer'), '| arranger:', on('arranger'))
        results.append('The Blackbyrds' not in e and 'The New Rotary Connection' not in e and on('composerlyricist') == ['0'] and on('writer') == ['1', '3'] and on('arranger') == ['3'])
        H.wait_for(pg, f"{NOTES}.every(n => n[2] !== 'search')", 30)
        n = pg.evaluate(NOTES)
        print('B)', n)
        results.append([x[:3] for x in n] == [['1', 'cover', ''], ['2', 'quote', 'found'], ['3', 'cover', ''], ['3', 'arrangement', 'found']]
                       and 'The Blackbyrds' in n[0][3] and 'Space Is the Place' in n[1][3])
        for i in (1, 2, 3):
            btn = pg.query_selector(f'tr[data-work="{i}"] [data-act=work-pending]')
            if btn:
                btn.click()
                pg.wait_for_timeout(400)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(800)
        st = pg.evaluate(f"""(() => {{ const ids = (r) => r && r.attributes && r.attributes.__tree ? r.attributes.__tree.map(a => a.typeID || a.type.id) : [];
          const added = MB.relationshipEditor.state.added;
          return {{ links: added.filter(x => x.linkTypeID === 278).map(x => [x.entity1 && x.entity1.name, ids(x)]),
            wrel: added.filter(x => x.linkTypeID === 350 || x.linkTypeID === 1047).map(x => [x.linkTypeID, x.entity0 && x.entity0.name, x.entity1 && x.entity1.name]),
            wrel0: added.filter(x => x.linkTypeID === 350 || x.linkTypeID === 1047).map(x => [x.linkTypeID, x.entity0 && x.entity0.gid]),
            note: (document.getElementById('edit-note-text') || {{ value: '' }}).value }}; }})()""")
        print('C)', st['links'], st['wrel'], '| Notiz:', [ln for ln in st['note'].split('\n') if any(w in ln for w in ('Cover', 'Arrangement', 'Quotes'))])
        links = dict((a, b2) for a, b2 in st['links'])
        # ((3.49.0, review) the direction by the original's id: both works are named "Song Four")
        print('   entity0:', st['wrel0'])
        results.append(links.get('Song Two') == [567] and links.get('Song Four') == [] and sorted(st['wrel']) == sorted([[1047, 'Song Three', 'Space Is the Place'], [350, 'Song Four', 'Song Four']])
                       and [ORIG4] == [g for t, g in st['wrel0'] if t == 350] and SPACE not in [g for t, g in st['wrel0']]
                       and 'linked 2 works with the works they arrange or quote' in st['note']
                       and 'Cover: “Song Two” – originally performed by The Blackbyrds' in st['note'] and 'Arrangement: “Song Four”' in st['note'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_exceptworks2():
    """Review of 3.49.0 (collected item Z-EXC): what is not staged.
    A) Track 3's work in MusicBrainz quotes Space Is the Place already, track 4 is linked to the original itself: neither is staged
       (no work with itself, no relationship twice) – the notes say so ("already", "a work of its own").
    B) An arranged cover without a writer in its block: not looked up by its title alone ("look for the original by hand"); a search that
       fails is no "not found" (the edit note does not say so).
    C) A text without entries pasted after it ("Thanks to all our friends."): nothing of the first one stays (notes, edit note).
    D) The text as a supplement ("＋ Text …" after "Mastered by Jane Roe"): its covers and quotes are taken over with its credits."""
    SUNRA = H.uid('5a5a5a5a', 1)
    SPACE = H.uid('cccccccc', 90)
    ORIG4 = H.uid('cccccccc', 91)
    W3 = H.uid('cccccccc', 92)
    STEPNEY = H.uid('5a5a5a5a', 2)
    H.lt(350, '51975ed8-bbfa-486b-9f28-5947f4370299', 'arrangement', 'work', 'work', ())
    H.lt(1047, 'c8283596-6ad1-4e09-8d49-3a7f7a1b1047', 'lyrical quotation', 'work', 'work', ())
    for i, n in [(567, 'cover'), (578, 'live')]:
        H.attr(i, n, i)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.WORK_SEARCH[:] = [{'id': SPACE, 'title': 'Space Is the Place', 'aliases': [], 'relations': [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': SUNRA, 'name': 'Sun Ra'}}]},
                        {'id': ORIG4, 'title': 'Song Four', 'aliases': [], 'relations': [{'target-type': 'artist', 'type': 'composer', 'artist': {'id': STEPNEY, 'name': 'Charles Stepney'}}]}]
    H.JS_WORKS.update({SPACE: (7090, 'Space Is the Place'), ORIG4: (7091, 'Song Four'), W3: (7092, 'Song Three')})
    H.WORK_TITLES.update({ORIG4: 'Song Four', W3: 'Song Three'})
    perf = lambda w, title, rels: {'target-type': 'work', 'type': 'performance', 'type-id': H.LTS[278]['gid'], 'attributes': [], 'work': {'id': w, 'title': title, 'relations': rels}}
    H.MB_EXTRA[H.REC[2]] = [perf(W3, 'Song Three', [{'target-type': 'work', 'type': 'lyrical quotation', 'type-id': H.LTS[1047]['gid'], 'direction': 'forward', 'attributes': [],
                                                       'work': {'id': SPACE, 'title': 'Space Is the Place'}}])]
    H.MB_EXTRA[H.REC[3]] = [perf(ORIG4, 'Song Four', [{'target-type': 'artist', 'type': 'composer', 'type-id': H.LTS[168]['gid'], 'attributes': [], 'artist': {'id': STEPNEY, 'name': 'Charles Stepney'}}])]
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    NOTES = "[...document.querySelectorAll('tr[data-work] .dci-mx-wnote')].map(n => [n.closest('tr').dataset.work, n.dataset.wnote, n.dataset.wstate || '', n.textContent.replace(/\\s+/g, ' ').trim()])"
    ADDED = """(() => { const added = MB.relationshipEditor.state.added; return { wrel: added.filter(x => x.linkTypeID === 350 || x.linkTypeID === 1047).map(x => [x.linkTypeID, x.entity0 && x.entity0.name]),
      note: (document.getElementById('edit-note-text') || { value: '' }).value }; })()"""
    TEXT_B = """All compositions and lyrics by Writer W except:

Song Two
Originally performed by The Blackbyrds
Arranged by Mocky

Song Three
End quote from Space Is the Place by Sun Ra
"""
    results = []

    def paste(pg, text, n):
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', text)
        pg.click('[data-act=text-load]')
        if n:
            H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= {n}", 60)
        pg.wait_for_timeout(2500 if n else 6000)

    def apply(pg, track='1'):
        # (a new work for a track: something to stage, the edit note written)
        pg.evaluate("(t) => document.querySelectorAll('[data-act=work-pending]').forEach((x) => { if (x.closest('tr').dataset.work === t) x.click(); })", track)
        pg.wait_for_timeout(600)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(800)
        return pg.evaluate(ADDED)

    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        paste(pg, EXCEPT_TEXT, 2)
        H.wait_for(pg, f"{NOTES}.every(n => n[2] !== 'search')", 30)
        n = pg.evaluate(NOTES)
        print('A)', n)
        st = apply(pg)
        print('   gestaged:', st['wrel'])
        q = [x for x in n if x[1] == 'quote']
        a = [x for x in n if x[1] == 'arrangement']
        results.append(q and q[0][2] == 'found' and 'already' in q[0][3] and a and a[0][2] == 'found' and 'a work of its own' in a[0][3] and st['wrel'] == [])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    H.MB_EXTRA.pop(H.REC[2], None)
    H.MB_EXTRA.pop(H.REC[3], None)
    H.WS_FAIL['worksearch'] = 3
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.WORK_QUERIES[:] = []
        paste(pg, TEXT_B, 2)
        H.wait_for(pg, f"{NOTES}.every(n => n[2] !== 'search')", 30)
        n = pg.evaluate(NOTES)
        print('B)', n, '| Suchen:', [x for x in H.WORK_QUERIES if 'Song Two' in x or 'Space' in x])
        st = apply(pg)
        lines = [ln for ln in st['note'].split('\n') if 'not found' in ln]
        print('   Notiz:', lines)
        results.append([x[:3] for x in n if x[1] != 'cover'] == [['1', 'arrangement', 'noWriter'], ['2', 'quote', 'error']]
                       and not any('Song Two' in x for x in H.WORK_QUERIES) and not lines)
        paste(pg, 'Thanks to all our friends.', 0)
        n2 = pg.evaluate(NOTES)
        st2 = apply(pg, '2')
        tail = st2['note'].split('Script:')[-1]
        print('C)', n2, [ln for ln in tail.split('\n') if 'Cover' in ln or 'Arrangement' in ln or 'Quotes' in ln])
        results.append(n2 == [] and 'Cover:' not in tail and 'Arrangement:' not in tail)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    H.WS_FAIL['worksearch'] = 0
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        paste(pg, 'Mastered by Jane Roe', 2)
        H.open_supp(pg)
        pg.click('[data-act=supp-text]')
        pg.wait_for_timeout(300)
        pg.fill('[data-f=text-src]', EXCEPT_TEXT)
        pg.click('[data-act=supp-text-load]')
        H.wait_for(pg, "!!document.querySelector('[data-act=supp-apply]')", 30)
        pg.wait_for_timeout(800)
        pg.click('[data-act=supp-apply]')
        pg.wait_for_timeout(1500)
        H.wait_for(pg, f"{NOTES}.length > 0 && {NOTES}.every(n => n[2] !== 'search')", 30)
        n3 = pg.evaluate(NOTES)
        print('D)', [x[:3] for x in n3])
        results.append([x[:3] for x in n3] == [['1', 'cover', ''], ['2', 'quote', 'found'], ['3', 'cover', ''], ['3', 'arrangement', 'found']])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_prose():
    """Credits Importer 3.50.0 (collected item Z-PRO, S079): "Experimental highland bagpipes (David Watson), with guests Makigami Koichi vocal
    and jaw harp, and SHelley Hirsch vocal." – David Watson highland bagpipes, Makigami Koichi vocal and jaw harp as a guest, Shelley Hirsch
    (S059: two capitals before small letters a slip – "SHelley") vocal as a guest; "Recorded live at Café Oto, with special guests …" – the
    words before "with" read as usual (the place); "with guests from all over the world" no credit; names as "DAngelo" stay."""
    got = read([{'text': 'Experimental highland bagpipes (David Watson), with guests Makigami Koichi vocal and jaw harp, and SHelley Hirsch vocal.'},
                {'text': 'Recorded live at Café Oto, with special guests Jane Roe saxophone and John Doe piano and drums.'},
                {'text': 'A record with guests from all over the world.'}, {'text': 'DAngelo Smith - vocals'}, {'text': 'JOhn Doe - bass'}])
    for g in got:
        print('  ', g and g['credits'], g and g['companies'], g and g['unrecognized'])
    if None in got:
        print('Ergebnis: FEHLER', [False])
        return
    ok = [got[0]['credits'] == [['David Watson', 'highland bagpipes'], ['Makigami Koichi', 'vocal [Guest]'], ['Makigami Koichi', 'jaw harp [Guest]'], ['Shelley Hirsch', 'vocal [Guest]']]
          and not got[0]['unrecognized'],
          got[1]['credits'] == [['Jane Roe', 'saxophone [Guest]'], ['John Doe', 'piano [Guest]'], ['John Doe', 'drums [Guest]']] and got[1]['companies'] == [['Café Oto', 'Recorded At']],
          not got[2]['credits'] and bool(got[2]['unrecognized']),
          got[3]['credits'] == [['DAngelo Smith', 'vocals']] and got[4]['credits'] == [['John Doe', 'bass']]]
    print('Ergebnis:', 'OK' if all(ok) else 'FEHLER', ok)


def case_trackartists():
    """Credits Importer 3.50.0 (collected item Z-TAR, S078; the maintainer: "die artists teil der recording artists sind und daher leicht den
    korrekten tracks zugeordnet werden können"): the Throats credits pasted on a release whose tracks name their artists – David Watson on
    all, Makigami Koichi on tracks 2 and 4, Ayako Koichi on track 3.
    A) Makigami Koichi's harmonic overtone singing and jaw harp on tracks 2 and 4, Ayako Koichi's jaw harp on track 3 (said at the row,
       rule S078); David Watson's highland bagpipes and composition on all four.
    B) S078 switched off: all on all tracks again; on: as in A."""
    WATSON, MAKIGAMI, AYAKO = H.uid('7a7a7a7a', 1), H.uid('7a7a7a7a', 2), H.uid('7a7a7a7a', 3)
    H.TRACK_AC.update({0: [(WATSON, 'David Watson')], 1: [(WATSON, 'David Watson'), (MAKIGAMI, 'Makigami Koichi')],
                       2: [(WATSON, 'David Watson'), (AYAKO, 'Ayako Koichi')], 3: [(WATSON, 'David Watson'), (MAKIGAMI, 'Makigami Koichi')]})
    TEXT = 'David Watson - highland bagpipes, composition\nMakigami Koichi -harmonic overtone singing, jaw harp\nAyako Koichi -jaw harp'
    H.attr(9201, 'jaw harp', 14, 14)
    H.attr(9202, 'Great Highland bagpipe', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    ROWS = """(() => [...document.querySelectorAll('section.dci-group')].flatMap(g => [...g.querySelectorAll('tr.dci-row')].map(tr => [
      (g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()), tr.querySelector('.dci-drole').dataset.raw.trim(),
      (tr.querySelector('[data-tcount]') || { textContent: '' }).textContent.trim(),
      (tr.querySelector('.dci-tartracks') || { textContent: '' }).textContent.trim()])))()"""
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
        H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= 2", 60)
        pg.wait_for_timeout(1500)
        r = pg.evaluate(ROWS)
        print('A)', r)
        by = {(n, role): (t, note) for n, role, t, note in r}
        a_ok = by.get(('Makigami Koichi', 'harmonic overtone singing'), ('', ''))[0] == '2 of 4 tracks' and by.get(('Makigami Koichi', 'jaw harp'), ('', ''))[0] == '2 of 4 tracks' \
            and 'artist: 2, 4 (rule S078)' in by.get(('Makigami Koichi', 'jaw harp'), ('', ''))[1] \
            and by.get(('Ayako Koichi', 'jaw harp'), ('', ''))[0] == '1 of 4 tracks' and 'artist: 3 (rule S078)' in by.get(('Ayako Koichi', 'jaw harp'), ('', ''))[1] \
            and by.get(('David Watson', 'highland bagpipes'), ('', ''))[0] == '4 of 4 tracks' and not by.get(('David Watson', 'highland bagpipes'), ('', 'x'))[1] \
            and by.get(('David Watson', 'composition'), ('', ''))[0] != '2 of 4 tracks'
        results.append(a_ok)
        pg.click('[data-act=rules]'); pg.wait_for_timeout(300)
        box = '#dci-rules [data-rf=tables] [data-rule-on=S078]'
        pg.locator(box).scroll_into_view_if_needed()
        pg.uncheck(box); pg.wait_for_timeout(800)
        r2 = pg.evaluate(ROWS)
        pg.check(box); pg.wait_for_timeout(800)
        r3 = pg.evaluate(ROWS)
        print('B) aus:', r2, '\n   an:', r3)
        results.append(all(t in ('4 of 4 tracks', '') and not note for n, role, t, note in r2) and r3 == r)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_prose2():
    """Review of 3.50.0 (collected item Z-PRO, S079; S059): what the sentence reader must not do.
    A) the words before "with" hold credits – "Highland bagpipes (David Watson), drums (Ann Lee), with guests …" keeps David Watson's
       bagpipes; "Recorded at Loft, Cologne by Jane Roe; drums (Ann Lee), with guests …" keeps the recording credit and the place;
    B) no place, event or make as a person: "Solo piano (Tokyo)", "(Live At The Village Vanguard)", "… and Fender Rhodes", "Gibson Les Paul
       guitar", "Jane Bass vocals" – not read (the line as before); "Highland bagpipes (tracks 1-2), …" no person "tracks 1-2";
    C) a guest not read – "… and Tim Berne" – nothing of the sentence (all or nothing);
    D) more forms of guests: "With special guests: Jane Roe (bass, vocals), John Doe (guitar)", "With guests Oliver Lake on saxophone",
       "Drums (Ann Lee) – with guests …";
    E) S059: Dutch IJ and names as "TJay" stay ("Rob IJzerman", "IJsbrand Kok", "TJay Smith"), "SHelley" → "Shelley"."""
    cases = ['Highland bagpipes (David Watson), drums (Ann Lee), with guests Bob Fay piano',
             'Recorded at Loft, Cologne by Jane Roe; drums (Ann Lee), with guests Bob Fay piano',
             'Solo piano (Tokyo), with guests Ann Lee drums', 'An evening of piano (Live At The Village Vanguard), with guests Ann Lee drums',
             'with guests John Doe piano and Fender Rhodes', 'A set with guests Gibson Les Paul guitar', 'With guest Jane Bass vocals',
             'Highland bagpipes (tracks 1-2), with guests Bob Fay piano',
             'A night with guests Jane Roe saxophone and Tim Berne',
             'With special guests: Jane Roe (bass, vocals), John Doe (guitar)', 'With guests Oliver Lake on saxophone', 'Drums (Ann Lee) – with guests Bob Fay piano',
             'Rob IJzerman - bass', 'IJsbrand Kok - piano', 'TJay Smith - drums', 'SHelley Hirsch - vocals']
    got = read([{'text': t} for t in cases])
    for c, g in zip(cases, got):
        print('  ', c[:50].ljust(50), '|', g and g['credits'], g and g['companies'], g and g['unrecognized'])
    if None in got:
        print('Ergebnis: FEHLER', [False])
        return
    names = lambda g: sorted(set(c[0] for c in g['credits']))
    ok = [['David Watson', 'Highland bagpipes'] in got[0]['credits'] and ['Ann Lee', 'drums'] in got[0]['credits'],
          ['Jane Roe', 'Recorded By'] in got[1]['credits'] and ['Loft', 'Recorded At'] in got[1]['companies'],
          all('Tokyo' not in names(g) and 'Fender' not in names(g) and 'Gibson Les Paul' not in names(g) and 'Jane' not in names(g)
              and not any(n.startswith('Live At') or n.startswith('tracks') for n in names(g)) for g in got[2:8]),
          got[8]['credits'] == [] and got[8]['unrecognized'],
          got[9]['credits'] == [['Jane Roe', 'bass [Guest]'], ['Jane Roe', 'vocals [Guest]'], ['John Doe', 'guitar [Guest]']]
          and got[10]['credits'] == [['Oliver Lake', 'saxophone [Guest]']] and got[11]['credits'] == [['Ann Lee', 'Drums'], ['Bob Fay', 'piano [Guest]']],
          [g['credits'][0][0] for g in got[12:]] == ['Rob IJzerman', 'IJsbrand Kok', 'TJay Smith', 'Shelley Hirsch']]
    ok = [bool(x) for x in ok]
    print('Ergebnis:', 'OK' if all(ok) else 'FEHLER', ok)


def case_trackartists2():
    """Review of 3.50.0 (collected item Z-TAR, S078).
    A) Not for other roles: Ayako Koichi's recording (an engineer) stays on all tracks, her jaw harp on track 3.
    B) Tracks changed by hand stay when S078 is switched off (Makigami Koichi's jaw harp on track 2 only); the other rows go back to all.
    C) Linked and staged: the edit note says where the tracks come from ("Tracks from the artist credits of the tracks in MusicBrainz:
       Ayako Koichi (jaw harp): 3")."""
    WATSON, MAKIGAMI, AYAKO = H.uid('7a7a7a7a', 1), H.uid('7a7a7a7a', 2), H.uid('7a7a7a7a', 3)
    H.TRACK_AC.update({0: [(WATSON, 'David Watson')], 1: [(WATSON, 'David Watson'), (MAKIGAMI, 'Makigami Koichi')],
                       2: [(WATSON, 'David Watson'), (AYAKO, 'Ayako Koichi')], 3: [(WATSON, 'David Watson'), (MAKIGAMI, 'Makigami Koichi')]})
    H.attr(9201, 'jaw harp', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.ARTISTS[9303] = (AYAKO, 'Ayako Koichi')  # (her entity for the relationship editor)
    TEXT = 'Makigami Koichi -jaw harp\nAyako Koichi -jaw harp, recording'
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    ROWS = """(() => [...document.querySelectorAll('section.dci-group')].flatMap(g => [...g.querySelectorAll('tr.dci-row')].map(tr => [
      (g.querySelector('.dci-gname strong').dataset.name || g.querySelector('.dci-gname strong').textContent.trim()), tr.querySelector('.dci-drole').dataset.raw.trim(),
      (tr.querySelector('[data-tcount]') || { textContent: '' }).textContent.trim(), (tr.querySelector('.dci-tartracks') || { textContent: '' }).textContent.trim(), tr.dataset.row])))()"""
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
        H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= 2", 60)
        pg.wait_for_timeout(1500)
        r = pg.evaluate(ROWS)
        print('A)', [x[:4] for x in r])
        by = {(x[0], x[1]): x for x in r}
        results.append(by[('Ayako Koichi', 'recording')][2] == '4 of 4 tracks' and by[('Ayako Koichi', 'jaw harp')][2] == '1 of 4 tracks'
                       and by[('Makigami Koichi', 'jaw harp')][2] == '2 of 4 tracks')
        rid = by[('Makigami Koichi', 'jaw harp')][4]
        pg.click(f'tr[data-row="{rid}"] [data-act=tracks-toggle]'); pg.wait_for_timeout(200)
        pg.click(f'tr[data-tracksrow="{rid}"] input[data-f=track][data-i="3"]'); pg.wait_for_timeout(300)
        pg.click('[data-act=rules]'); pg.wait_for_timeout(300)
        box = '#dci-rules [data-rf=tables] [data-rule-on=S078]'
        pg.locator(box).scroll_into_view_if_needed()
        pg.uncheck(box); pg.wait_for_timeout(800)
        r2 = {(x[0], x[1]): x for x in pg.evaluate(ROWS)}
        print('B)', [x[:4] for x in r2.values()])
        results.append(r2[('Makigami Koichi', 'jaw harp')][2] == '1 of 4 tracks' and r2[('Ayako Koichi', 'jaw harp')][2] == '4 of 4 tracks'
                       and not any(x[3] for x in r2.values()))
        pg.check(box); pg.wait_for_timeout(800)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        pg.evaluate("document.querySelectorAll('#dci-rules [data-act=rules-close], #dci-rules .dci-close').forEach(b => b.click())")
        pg.wait_for_timeout(300)
        pg.evaluate("""[...document.querySelectorAll('section.dci-group')].filter(g => /Ayako/.test(g.textContent)).forEach(g => { const b = g.querySelector('[data-act=name-use]'); if (b) b.click(); })""")
        pg.wait_for_timeout(2500)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(800)
        note = pg.evaluate("(document.getElementById('edit-note-text') || { value: '' }).value")
        line = [ln for ln in note.split('\n') if 'artist credits of the tracks' in ln]
        print('C)', line)
        results.append(line == ['Tracks from the artist credits of the tracks in MusicBrainz: Ayako Koichi (jaw harp): 3.'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_placecredit():
    """Credits Importer 3.51.0 (collected item Z-PCR, S080; Q-gd): the "credited as" of a place or label linked to MusicBrainz, in Node
    (sourceCreditFor): "Sound Development Studio, Zürich" for MusicBrainz's "Sound Development Studio" – none (before: the whole name);
    "Sound Development Studios, Zürich" with the area Zürich – "Sound Development Studios"; "Studio, Zürich" for "Studio Zürich" – kept
    (the town is part of MusicBrainz's name); "Loft, Cologne, Germany" for "Loft" – none; another name ("Other Name") – kept whole.
    Review of 3.51.0: no legal form, "Jr.", room or single letter is an area ("Blue Note, Inc.", "Power Station, Studio A", "Sammy Davis,
    Jr.", "Studio A, B, C" kept); a venue named after its town ("Sydney Opera House, Sydney") – none; "Loft, Cologne (DE)" – none; a
    comma at the end ("Studio X,") – none; an artist (no company: "Davis, Sammy") untouched."""
    js = subprocess.run(['node', '-e', """
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const c = (name, mb, area) => m.sourceCreditFor({}, { company: true, name, mbName: mb, area });
const r = (name, mb) => m.sourceCreditFor({}, { company: false, name, mbName: mb });
console.log(JSON.stringify([c('Sound Development Studio, Zürich', 'Sound Development Studio'), c('Sound Development Studios, Zürich', 'Sound Development Studio', 'Zürich'),
  c('Studio, Zürich', 'Studio Zürich'), c('Loft, Cologne, Germany', 'Loft'), c('Sound Development Studio, Zürich', 'Other Name'),
  c('Blue Note, Inc.', 'Blue Note'), c('Power Station, Studio A', 'Power Station'), c('Sammy Davis, Jr.', 'Sammy Davis'), c('Studio A, B, C', 'Studio A'),
  c('Sydney Opera House, Sydney', 'Sydney Opera House'), c('Loft, Cologne (DE)', 'Loft'), c('Studio X,', 'Studio X'), r('Davis, Sammy', 'Sammy Davis')]));
""", str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
        print('Ergebnis: FEHLER', [False])
        return
    got = json.loads(js.stdout)
    print('  ', got)
    ok = got == ['', 'Sound Development Studios', 'Studio, Zürich', '', 'Sound Development Studio, Zürich',
                 'Blue Note, Inc.', 'Power Station, Studio A', 'Sammy Davis, Jr.', 'Studio A, B, C', '', '', '', 'Davis, Sammy']
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])



def case_namesroles():
    """Credits Importer 3.59.0 (collected item Z-TBY; S085, S087), in Node: a name and its roles without a dash, the heading of a group.
    "The Quartet:" a group's heading (its members the names below it up to "+"), "Special guests:" and "Strings:" not; "Jane Roe piano",
    "John Doe tenor saxophone, flute", "Mary Major vocals on “Bonu”" (the title: its track), "Ann Ray piano (vocals on “Bumper”)" (two
    credits, vocals on track 3 only); "Recorded live at Studio X" and "Thanks to Bob Stone" are no names with roles; "Special guests:"
    left out as a heading of the credits."""
    text = ('The Quartet:\nJane Roe piano\nJohn Doe tenor saxophone, flute\n+\nSpecial guests:\nMary Major vocals on “Bonu”\n'
            'Ann Ray piano (vocals on “Bumper”)\nRecorded live at Studio X\nThanks to Bob Stone\nStrings:')
    titles = ['Blessed Ones The Eternal Truth', 'Bonu', 'Bumper', 'Dance Of The Evil Toys']
    node = NODE.replace("resolveTracks: trackSet(c.tracks || 14),", "resolveTracks: trackSet(c.tracks || 14), trackCount: c.count || 0, resolveTitles: c.titles ? ((ts) => { const ix = new Set(); const un = []; ts.forEach((t) => { const k = c.titles.findIndex((x) => x.toLowerCase() === t.toLowerCase()); if (k >= 0) ix.add(k); else un.push(t); }); return { indexes: ix, unresolved: un }; }) : null,")
    node = node.replace("credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),",
                        "credits: r.credits.map((x) => [x.who.name, x.role, x.tracks && x.tracks.indexes ? x.tracks.indexes.join(',') : 'all']), groups: r.groups,")
    node = node.replace("|baritone electric guitar)$/i.test(p.base); };", "|baritone electric guitar|tenor saxophone|strings?)$/i.test(p.base); };")
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps([{'text': text, 'titles': titles, 'count': 4}])], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout)[0] if not js.returncode else None
    print('  ', g)
    ok = g is not None and sorted(g['credits']) == sorted([['Jane Roe', 'piano', 'all'], ['John Doe', 'tenor saxophone', 'all'], ['John Doe', 'flute', 'all'],
                                                         ['Mary Major', 'vocals', '1'], ['Ann Ray', 'piano', 'all'], ['Ann Ray', 'vocals', '2']]) \
        and [x['name'] for x in g['groups']] == ['The Quartet'] and g['groups'][0]['members'] == ['Jane Roe', 'John Doe'] \
        and ['groupHeading', 'The Quartet:'] in g['ignored'] and ['separator', '+'] in g['ignored'] \
        and ['heading', 'Special guests:'] in g['ignored'] and g['unrecognized'] == ['Strings:'] and 'Strings:' not in [i[1] for i in g['ignored'] if i[0] == 'groupHeading'] \
        and 'Recorded live at Studio X' not in [c[0] for c in g['credits']] \
        and not any(c[0].startswith('Thanks') for c in g['credits'])
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])



def case_namesroles2():
    """Credits Importer 3.59.0 (review of Z-TBY), in Node – what must stay as before: the title of an "except" block ("Song Two:") is no
    group; "Go Kurosawa plays guitar, bass and drums" keeps its name; "Eric Revis bass and Nasheet Waits drums" is not one person with an
    instrument "Nasheet Waits drums"; "Fender Rhodes organ" is no artist; "organ" after a separator is no role of the name above;
    "Volume 2:" is no group, "Besetzung:" a heading; the members of a group are its players ("Recorded by Joe Engineer" is none)."""
    titles = ['Song One', 'Song Two', 'Song Three', 'Song Four']
    cases = [
        'All songs written by megiapa except:\nSong Two:\nWritten by John Roe',
        'Go Kurosawa plays guitar, bass and drums',
        'Eric Revis bass and Nasheet Waits drums',
        'Fender Rhodes organ',
        'Eric Revis - piano\n+\norgan',
        'Volume 2:\nJane Roe piano\n\nBesetzung:\nJohn Doe bass',
        'The Trio:\nJane Roe piano\nRecorded by Joe Engineer',
    ]
    node = NODE.replace("resolveTracks: trackSet(c.tracks || 14),", "resolveTracks: trackSet(c.tracks || 14), trackCount: c.count || 0, resolveTitles: c.titles ? ((ts) => { const ix = new Set(); const un = []; ts.forEach((t) => { const k = c.titles.findIndex((x) => x.toLowerCase() === t.toLowerCase()); if (k >= 0) ix.add(k); else un.push(t); }); return { indexes: ix, unresolved: un }; }) : null,")
    node = node.replace("credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),",
                        "credits: r.credits.map((x) => [x.who.name, x.role, x.tracks && x.tracks.indexes ? x.tracks.indexes.join(',') : 'all']), groups: r.groups,")
    node = node.replace("|baritone electric guitar)$/i.test(p.base); };", "|baritone electric guitar|organ)$/i.test(p.base); };")
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps([{'text': t, 'titles': titles, 'count': 4} for t in cases])], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    for x in g or []:
        print('  ', x)
    names = lambda k: [c[0] for c in g[k]['credits']]
    ok = g is not None and ['John Roe', 'Written By', '1'] in g[0]['credits'] and not g[0]['groups'] \
        and 'Go Kurosawa -' not in names(1) and 'Eric Revis' not in names(2) and 'Fender Rhodes' not in names(3) \
        and g[4]['credits'] == [['Eric Revis', 'piano', 'all']] \
        and not g[5]['groups'] and ['heading', 'Besetzung:'] in g[5]['ignored'] and 'Volume 2:' in g[5]['unrecognized'] \
        and [x['members'] for x in g[6]['groups']] == [['Jane Roe']]
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])



def case_tcpread():
    """Credits Importer 3.60.0 (collected item Z-TCP, rule S088), in Node: a track list with the composers in brackets after the titles.
    "1 Blessed Ones The Eternal Truth (Orrin Evans)", "2 Bonu (Oliver Lake)", "3. Bumper (Tarbaby)", "Dance Of The Evil Toys (Eric Revis /
    Nasheet Waits)" – each name writes its track (marked as such); "Bonu (live)", "Song Nine (Jane Roe)" (no track of the release) and
    "Bumper (Jane Roe, vocals)" are not read so."""
    text = ('1 Blessed Ones The Eternal Truth (Orrin Evans)\n2 Bonu (Oliver Lake)\n3. Bumper (Tarbaby)\nDance Of The Evil Toys (Eric Revis / Nasheet Waits)\n'
            'Bonu (live)\nSong Nine (Jane Roe)\nBumper (Jane Roe, vocals)')
    titles = ['Blessed Ones The Eternal Truth', 'Bonu', 'Bumper', 'Dance Of The Evil Toys']
    node = NODE.replace("resolveTracks: trackSet(c.tracks || 14),", "resolveTracks: trackSet(c.tracks || 14), trackCount: c.count || 0, resolveTitles: c.titles ? ((ts) => { const ix = new Set(); const un = []; ts.forEach((t) => { const k = c.titles.findIndex((x) => x.toLowerCase() === t.toLowerCase()); if (k >= 0) ix.add(k); else un.push(t); }); return { indexes: ix, unresolved: un }; }) : null,")
    node = node.replace("credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),",
                        "credits: r.credits.map((x) => [x.who.name, x.role, x.tracks && x.tracks.indexes ? x.tracks.indexes.join(',') : 'all', !!x.titleComposer]),")
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps([{'text': text, 'titles': titles, 'count': 4}])], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout)[0] if not js.returncode else None
    print('  ', g)
    ok = g is not None and g['credits'] == [['Orrin Evans', 'Written-By', '0', True], ['Oliver Lake', 'Written-By', '1', True], ['Tarbaby', 'Written-By', '2', True],
                                            ['Eric Revis', 'Written-By', '3', True], ['Nasheet Waits', 'Written-By', '3', True]] \
        and g['unrecognized'] == ['Bonu (live)', 'Song Nine (Jane Roe)', 'Bumper (Jane Roe, vocals)']
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])



def case_tcpread2():
    """Credits Importer 3.60.0 (review of Z-TCP), in Node: brackets after a title that are no composers stay as before – a place
    ("Bonu (Tokyo)"), "(Hidden Track)", "(Traditional)", "(Inspired By John Coltrane)"; a rights society is left out ("(Oliver Lake/BMI)"
    → Oliver Lake); single words joined by "&" are one name ("(Earth, Wind & Fire)", "(Simon & Garfunkel)"); a length after it is fine
    ("(Oliver Lake) 6:12"); a single word only in a numbered list ("Bonu (Tokyo)" none); the members of the band after a track named
    after it are no composers ("Tarbaby (Orrin Evans, Eric Revis)");
    a title only by its start is not enough ("Blessed Ones (Village Vanguard)")."""
    titles = ['Blessed Ones The Eternal Truth', 'Bonu', 'Bumper', 'Tarbaby', 'Paix']
    cases = ['Bonu (Tokyo)', 'Bonu (Hidden Track)', 'Bumper (Traditional)', 'Bumper (Inspired By John Coltrane)', 'Paix (Oliver Lake/BMI)',
             'Bonu (Earth, Wind & Fire)', 'Bumper (Simon & Garfunkel)', '2 Bonu (Oliver Lake) 6:12', 'Tarbaby (Orrin Evans, Eric Revis)', 'Blessed Ones (Village Vanguard)']
    node = NODE.replace("resolveTracks: trackSet(c.tracks || 14),", "resolveTracks: trackSet(c.tracks || 14), trackCount: c.count || 0, resolveTitles: c.titles ? ((ts) => { const ix = new Set(); const un = []; ts.forEach((t) => { const k = c.titles.findIndex((x) => x.toLowerCase() === t.toLowerCase()); if (k >= 0) ix.add(k); else un.push(t); }); return { indexes: ix, unresolved: un }; }) : null,")
    node = node.replace("credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),",
                        "credits: r.credits.map((x) => [x.who.name, x.tracks && x.tracks.indexes ? x.tracks.indexes.join(',') : 'all', !!x.titleComposer]),")
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'),
                         json.dumps([{'text': t, 'titles': titles, 'count': 5, 'artists': ['Tarbaby']} for t in cases])], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    tc = [[c[:2] for c in x['credits'] if c[2]] for x in g] if g else None
    for t, x in zip(cases, tc or []):
        print('  ', t, '→', x)
    ok = tc == [[], [], [], [], [['Oliver Lake', '4']], [['Earth, Wind & Fire', '1']], [['Simon & Garfunkel', '2']], [['Oliver Lake', '1']], [], []]
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])



def case_tcplabel3117():
    """Credits Importer 3.117.0 (collected items Z-TCPMULTI, Z-TCPLEN, Z-TCPNEXT, Z-TCPWRAP, Z-OCRTITLE, Z-OCRP; rules S179 – S182), in Node:
    the labels of "You Ain't No Friend Of Mine!" as the cover's reading gives them.
    A) Side A: "(Scott - Carter)" two names; lengths 5'54 and 533 (after the bracket) and 7'26 left out.
    B) Side B: the release's title "YOU AIN'T NO FRIEND OF MINE |" left out as such; "(H. Bullock)" on the line below its track; a title
       over two lines with its length in between ("… where did we go 506" / "wrong ? (Idris Muhammad)"); "P1978 – Fantasy Records" ℗.
    C) Not joined: a track line and a publisher's bracket below it ("(Harms Inc.-ASCAP)"); "7. Boeing 747" keeps its number (the track
       is "Boeing 747") and gets "(Jane Roe)" below it; a name with a dash in it stays one ("(Jean-Luc Ponty)"); "Ortega y Gasset" one name."""
    titles = ['Disco Man', 'Seesaw', 'The Doc', 'You Ain’t No Friend of Mine!', 'Tell Me, Where Did We Go Wrong?', 'Big Foot', 'Boeing 747', 'Alpha', 'Gamma']
    a = "1. Disco man (Scott - Carter) 5'54\n2. Seesaw (G. T'Nig) 533\n3. The doc (Mike Wolff) 7'26"
    b = ("YOU AIN'T NO FRIEND OF MINE |\n1. You ain't no friend of mine! 645\n(H. Bullock)\n2. Tell me, where did we go 506\nwrong ? (Idris Muhammad)\n"
         "3. Big foot (Sakinah Muhammad) 7'47\nP1978 – Fantasy Records")
    c = "1. Alpha\n(Harms Inc.-ASCAP)\n\n7. Boeing 747\n(Jane Roe)\n\n9. Gamma (Jean-Luc Ponty; José Ortega y Gasset)"
    node = NODE.replace("resolveTracks: trackSet(c.tracks || 14),", "resolveTracks: trackSet(c.tracks || 14), trackCount: c.count || 0, releaseTitle: c.releaseTitle || '', "
                        "resolveTitles: c.titles ? ((ts) => { const k = (x) => String(x).toLowerCase().replace(/[^a-z0-9]+/g, ''); const ix = new Set(); const un = []; ts.forEach((t) => { const i = c.titles.findIndex((x) => k(x) === k(t)); if (i >= 0) ix.add(i); else un.push(t); }); return { indexes: ix, unresolved: un }; }) : null,")
    node = node.replace("credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),",
                        "credits: r.credits.map((x) => [x.who.name, x.tracks && x.tracks.indexes ? x.tracks.indexes.map((i) => i + 1).join(',') : x.tracks && x.tracks.set ? [...x.tracks.set].map((i) => i + 1).join(',') : 'all']),")
    base = {'titles': titles, 'count': len(titles), 'releaseTitle': 'You Ain’t No Friend of Mine!'}
    cases = [dict(base, text=a), dict(base, text=b), dict(base, text=c)]
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(cases)], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    for x in g or []:
        print('  ', x)
    ok = g is not None and g[0]['credits'] == [['Scott', '1'], ['Carter', '1'], ["G. T'Nig", '2'], ['Mike Wolff', '3']] and not g[0]['unrecognized'] \
        and g[1]['credits'] == [['H. Bullock', '4'], ['Idris Muhammad', '5'], ['Sakinah Muhammad', '6']] and ['Fantasy Records', 'Phonographic Copyright (p)'] in [x[:2] for x in g[1]['companies']] \
        and ['releaseTitle', "YOU AIN'T NO FRIEND OF MINE |"] in g[1]['ignored'] and not g[1]['unrecognized'] \
        and ['Jean-Luc Ponty', '9'] in g[2]['credits'] and ['José Ortega y Gasset', '9'] in g[2]['credits'] and ['Jane Roe', '7'] in g[2]['credits'] \
        and not any(x[0].startswith('Harms') for x in g[2]['credits']) and '(Harms Inc.-ASCAP)' in g[2]['unrecognized']
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])



def case_liccourt3118():
    """Credits Importer 3.118.0 (collected items Z-LICCOURT, Z-PCSPLIT; rules S183, S184), in Node: Bandcamp's credits of Wewantsounds.
    A) "℗ 2026 James Quinlan © 2026 WEWANTSOUNDS. Licensed Courtesy of James Quinlan and the Don Cherry Estate.": ℗ James Quinlan,
       © WEWANTSOUNDS, a licensor each: James Quinlan, Don Cherry Estate ("the" left out).
    B) "© 2026 WEWANTSOUNDS. See you on tour.": the © read, the sentence after it alone not recognized.
    C) "Licensed by courtesy of Sony Music Entertainment" a licensor; "Licensed to Ace Records" and "Courtesy of Blue Note Records" as before."""
    texts = ['℗ 2026 James Quinlan © 2026 WEWANTSOUNDS. Licensed Courtesy of James Quinlan and the Don Cherry Estate. ', '© 2026 WEWANTSOUNDS. See you on tour.',
             'Licensed by courtesy of Sony Music Entertainment\nLicensed to Ace Records\nCourtesy of Blue Note Records']
    g = read([{'text': t} for t in texts])
    for x in g or []:
        print('  ', x)
    # (the licensors among the credits or the companies: this test's role check of companies does not know "licensed")
    co = lambda k: sorted([x[:2] for x in g[k]['companies']] + [x[:2] for x in g[k]['credits']])
    ok = g is not None and co(0) == sorted([['James Quinlan', 'Phonographic Copyright (p)'], ['WEWANTSOUNDS', 'Copyright (c)'], ['James Quinlan', 'Licensed From'], ['Don Cherry Estate', 'Licensed From']]) \
        and not g[0]['unrecognized'] and co(1) == [['WEWANTSOUNDS', 'Copyright (c)']] and g[1]['unrecognized'] == ['See you on tour'] \
        and co(2) == sorted([['Sony Music Entertainment', 'Licensed From'], ['Ace Records', 'Licensed to']]) and 'Courtesy of Blue Note Records' in g[2]['unrecognized']
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])



def case_ocrc3120():
    """Credits Importer 3.120.0 (collected item Z-OCRC, S187), in Node: "C1978 – Fantasy Records" and "C 1978 Fantasy Records" (a cover's ©
    read as C) are © 1978 Fantasy Records; "C 2000 Watt Amp 5" (digits after the name) and "Cole 1978 X" stay as they are."""
    g = read([{'text': t} for t in ['C1978 – Fantasy Records', 'C 1978 Fantasy Records', 'C 2000 Watt Amp 5', 'Cole 1978 X']])
    for x in g or []:
        print('  ', x)
    ok = g is not None and [x['companies'] for x in g[:2]] == [[['Fantasy Records', 'Copyright (c)']]] * 2 \
        and not g[2]['companies'] and not g[3]['companies'] and g[2]['unrecognized'] == ['C 2000 Watt Amp 5']
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])



def case_studio3120r():
    """Credits Importer 3.120.0 (review of Z-STUDIO, S188, and Z-DESCON, S186), in Node: a studio this text names as a place too
    ("Recorded at Foo Studios, London." / "Photography by Foo Studios") keeps its art role as a credit (a recording studio is no label);
    "Cover Photography by Bar Studio" a label with photography, "Design [Graphic] by Baz Studio" with graphic design. R062 takes
    "graphic" only for a design role with nothing else in its details: "Art Direction [Graphic Design]" stays art direction (R080),
    "Logo Design [Graphic]" design credited "logo" (R101), "Design [Graphic, Cover]" stays R077."""
    g = read([{'text': t} for t in ['Recorded at Foo Studios, London.\nPhotography by Foo Studios', 'Cover Photography by Bar Studio', 'Design [Graphic] by Baz Studio']])
    for x in g or []:
        print('  ', x)
    ok = g is not None and g[0]['credits'] == [['Foo Studios', 'Photography By']] and g[0]['companies'] == [['Foo Studios', 'Recorded At']] \
        and g[1]['companies'] == [['Bar Studio', 'Photography By', 'label']] and g[2]['companies'] == [['Baz Studio', 'Graphic Design By', 'label']]
    js = subprocess.run(['node', '-e', """const m = require(process.argv[1]); console.log(JSON.stringify([['Design Concept', ['Graphic Concept']], ['Art Direction', ['Graphic Design']],
      ['Logo Design', ['Graphic']], ['Design', ['Graphic', 'Cover']]].map(([b, d]) => { const r = m.mapRole(b, d); return [r.rule, r.types[0], r.credit || '']; })));""",
                         str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    roles = json.loads(js.stdout) if not js.returncode else None
    print('   R062:', roles)
    ok2 = roles == [['R062', 'graphic design', ''], ['R080', 'art direction', ''], ['R101', 'design', 'logo'], ['R077', 'design', '']]
    print('Ergebnis:', 'OK' if ok and ok2 else 'FEHLER', [ok, ok2])


def case_dtrk3121r():
    """Credits Importer 3.121.0 (review of Z-DTRK, S189), in Node: "1-1 to 1-2 recorded September 3rd, 1964" / "Live at Club Montmartre,
    Copenhagen, Denmark" – the place on 1-1, 1-2; "1-1 to 1-2 produced by Teo Macero" / "Live at Birdland, New York" – a producer, the
    place not joined to his line (no "recorded live by"); "1-1 to 1-2 recorded May 1, 1964" / "In Memory Of John Coltrane" – no place."""
    cases = ['1-1 to 1-2 recorded September 3rd, 1964\nLive at Club Montmartre, Copenhagen, Denmark',
             '1-1 to 1-2 produced by Teo Macero\nLive at Birdland, New York',
             '1-1 to 1-2 recorded May 1, 1964\nIn Memory Of John Coltrane']
    node = NODE.replace("resolveTracks: trackSet(c.tracks || 14),", "resolveTracks: (spec) => (/^1-1\\s+to\\s+1-2$/.test(String(spec).trim()) ? Object.assign(new Set([0, 1]), { spec }) : null),")
    node = node.replace("companies: r.companies.map((x) => [x.who.name, x.role, ...(x.entity ? [x.entity] : [])]),",
                        "companies: r.companies.map((x) => [x.who.name, x.role, x.tracks ? [...(x.tracks.indexes || x.tracks.set || [])].join(',') : 'all']),")
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps([{'text': t} for t in cases])], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    for t, x in zip(cases, g or []):
        print('  ', t.replace('\n', ' / ')[:60], '→', x['credits'], x['companies'], x['unrecognized'])
    ok = g is not None and g[0]['companies'] == [['Club Montmartre', 'Recorded At', '0,1']] \
        and [c[:2] for c in g[1]['credits']] == [['Teo Macero', 'Produced By']] and not any('live' in c[1].lower() for c in g[1]['credits']) \
        and not any('Memory' in c[0] for c in g[2]['companies'])
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_prodfor3122r():
    """Credits Importer 3.122.0 (review of Z-PRODFOR, S191, and Z-RSD, S192), in Node, DISCOGS.toRelease: "Producer [Assistant, For Radio
    Bremen (2)]" stays an assistant producer (Radio Bremen a label); "Executive-Producer [For Atlantic]" executive; "Producer [For VARA,
    For BBC]" both; "Producer [For The Album \"Foo\"]", "Production Manager [For EMI]", "Mixed By [For X Records]" no label; VARA Radio
    listed under "Companies, etc." as "Produced For" not twice. Format "RSD Black Friday" and "Cassette Store Day": both series, no
    "Limited Edition", "Reissue"."""
    js = subprocess.run(['node', '-e', r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {} };
const M = require(process.argv[1]);
const tl = []; for (let i = 1; i <= 22; i++) tl.push({ position: String(i), title: 'T' + i, type_: 'track' });
const ex = (name, id, role, tracks = '') => ({ name, id, role, tracks, anv: '', join: '' });
const d = { id: 1, title: 'x', tracklist: tl, extraartists: [ex('Aad Bos', 11, 'Producer [Session Originally Produced For VARA Radio By]', '16 to 21'),
  ex('Pete', 13, 'Producer [Assistant, For Radio Bremen (2)]'), ex('Exec', 14, 'Executive-Producer [For Atlantic]'), ex('Two', 21, 'Producer [For VARA, For BBC]'),
  ex('Al', 20, 'Producer [For The Album "Foo"]'), ex('PM', 19, 'Production Manager [For EMI]'), ex('Mix', 18, 'Mixed By [For X Records]')],
  companies: [{ name: 'VARA Radio', id: 99, entity_type_name: 'Produced For', catno: '' }],
  formats: [{ name: 'Vinyl', descriptions: ['LP', 'Limited Edition', 'Reissue'], text: 'RSD Black Friday' }, { name: 'Cassette', descriptions: ['Cassette Store Day'], text: '' }], released: '2025-11-28' };
const r = M.DISCOGS.toRelease(d, 1);
console.log(JSON.stringify({ credits: r.credits.map((c) => [c.who.name, c.role]), companies: r.companies.map((c) => [c.who.name, c.role]), series: r.series.map((x) => x.name) }));
""", str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    print('  ', g)
    cr = dict((n, r) for n, r in (g or {}).get('credits', []))
    co = (g or {}).get('companies', [])
    ok = g is not None and cr.get('Pete') == 'Producer [Assistant]' and cr.get('Aad Bos') == 'Producer' and cr.get('Exec') == 'Executive-Producer' and cr.get('Two') == 'Producer' \
        and sorted(n for n, r in co if r.endswith('For')) == ['Atlantic', 'BBC', 'Radio Bremen', 'VARA', 'VARA Radio'] and [n for n, r in co].count('VARA Radio') == 1 \
        and ['Atlantic', 'Executive Produced For'] in co and not any(n in ('The Album "Foo"', 'EMI', 'X Records') for n, r in co) \
        and sorted(g['series']) == ['Cassette Store Day', 'Record Store Day']
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_text3128r():
    """Credits Importer 3.128.0 (collected items Z-PROSE, Z-MASTERAT, Z-MIXMASTERAT, Z-TRACKLINE, Z-TITLELINE, Z-LIMITED, Z-BILING, Z-PHOTOS,
    Z-SUPPORTED, Z-PROSETEXT; S202–S208), in Node – each line on its own:
    A) "… to be replaced by newer tracks more in keeping with …" no credit (left out as prose); B) "Mixing & Mastering by Ferran Conangla at
    FCM Studio, Barcelona" – FCM Studio mixed at and mastered at; C) "1. String Fables 9,14", "5. Agora 7, 49", "Total Time: 59,41",
    "3. Flying Teapot - including: …" (a title of the release) left out as a track list; D) "Limited to 100 copies." left out (edition);
    E) "Inspelad live på Skjul Fyra Sex i Göteborg/recorded live at Skjul Fyra Sex in Gothenburg, Sweden." – recorded at Skjul Fyra Sex,
    the Swedish half left out (translation); F) "Photos: Barry Guy by Francesca Pfeffer, Jordina Millà by Aina Lesan" – two photographers,
    credited "photo of …"; G) "Supported by: Departament de Cultura … & Gesellschaft …" – two labels, credited "support"; H) "Liner notes:
    Maciej Lewenstein" and "Maciej Lewenstein" below – its signature."""
    titles = ['String Fables', 'Nuc', 'Flying Teapot - Including: In a Session Not C ~ IAO Chant From the Melting Paraiso U.F.O.', 'Decodification', 'Agora']
    node = NODE.replace("artistNames: c.artists || [], titleNames: c.titles || [] });",
                        "artistNames: c.artists || [], titleNames: c.titles || [], trackTitles: c.titles || null, trackCount: (c.titles || []).length });")
    node = node.replace("companies: r.companies.map((x) => [x.who.name, x.role, ...(x.entity ? [x.entity] : [])]),",
                        "companies: r.companies.map((x) => [x.who.name, x.role, x.roleCredit || '']), ignoredWhy: r.ignored.map((x) => x.why),")
    node = node.replace("credits: r.credits.map((x) => [x.who.name, x.role",
                        "credits: r.credits.map((x) => [x.who.name, x.role, x.roleCredit || ''")
    cases = ['A few of the tracks originally performed at Roadburn have been lost along the way, to be replaced by newer tracks more in keeping with the rest of the album’s mood.',
             'Mixing & Mastering by Ferran Conangla at FCM Studio, Barcelona',
             '1. String Fables 9,14\n5. Agora 7, 49\nTotal Time: 59,41\n3. Flying Teapot - including: In A session Not C ~ IAO Chant From The Melting Paraiso U.F.O.',
             'Limited to 100 copies.',
             'Inspelad live på Skjul Fyra Sex i Göteborg/recorded live at Skjul Fyra Sex in Gothenburg, Sweden.',
             'Photos: Barry Guy by Francesca Pfeffer, Jordina Millà by Aina Lesan',
             'Supported by: Departament de Cultura de la Generalitat de Catalunya & Gesellschaft zur Verwetrung von Leistungsschutzrechten',
             'Liner notes: Maciej Lewenstein\nMaciej Lewenstein']
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps([{'text': t, 'titles': titles} for t in cases])],
                        capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    for t, x in zip(cases, g or []):
        print('  ', t[:60].replace('\n', ' / '), '→', x['credits'], x['companies'], x['ignoredWhy'], x['unrecognized'])
    ok = g is not None
    if ok:
        co = lambda k: [c[:2] for c in g[k]['companies']]
        ok = (not g[0]['credits'] and g[0]['ignoredWhy'] == ['prose'] and not g[0]['unrecognized']
              and ['FCM Studio', 'Mixed At'] in co(1) and ['FCM Studio', 'Mastered At'] in co(1)
              and g[2]['ignoredWhy'] == ['tracklist'] * 4 and not g[2]['unrecognized']
              and g[3]['ignoredWhy'] == ['edition']
              and co(4) == [['Skjul Fyra Sex', 'Recorded At']] and g[4]['ignoredWhy'] == ['translation']
              and sorted(c[:3] for c in g[5]['companies'] + g[5]['credits']) == [['Aina Lesan', 'Photography By', 'photo of Jordina Millà'], ['Francesca Pfeffer', 'Photography By', 'photo of Barry Guy']]
              and [c[1:] for c in g[6]['companies']] == [['Supported By', 'support']] * 2 and len(g[6]['companies']) == 2
              and g[7]['ignoredWhy'] == ['signature'] and not g[7]['unrecognized'])
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_members3129():
    """Credits Importer 3.129.0 (Z-MEMBERBLOCK S211, Z-FANTASYROLE S212, Z-MEMBERCREATE S213, Z-DEDPLACE S214), in Node: A) "HIBUSHIBIRE are",
    an empty line, three members with their roles – a group of three, "speed guru" left out as fantasy, Jane Doe guitar; B) "Acid Mothers Temple
    & The Melting Paraiso U.F.O. -at the time of this live recording were:" – one group, "&" in its name; C) "Qien Pudiera are Camila Chapelle
    and Lucia Reyes" – the group with both; D) 'Dedicated to ~Namba~ ~Bears"~' – left out as a dedication, nothing not recognized; E) "John
    Roe: Bass/Vocal/Mermaid Mountain" – "Mermaid Mountain" left out as fantasy, bass and vocals kept."""
    node = NODE.replace("unrecognized: r.unrecognized, ignored: r.ignored.map((i) => [i.why, i.text]) };",
                        "unrecognized: r.unrecognized, ignored: r.ignored.map((i) => [i.why, i.text]), groups: (r.groups || []).map((g) => [g.name, g.members]) };")
    cases = [{'text': 'HIBUSHIBIRE are\n\nJane Doe - guitar\nJohn Roe - bass, speed guru\nMax Moe - drums', 'artists': ['HIBUSHIBIRE']},
             {'text': 'Acid Mothers Temple & The Melting Paraiso U.F.O. -at the time of this live recording were:\nJane Doe - guitar\nJohn Roe - drums'},
             {'text': 'Qien Pudiera are Camila Chapelle and Lucia Reyes', 'artists': ['Qien Pudiera']},
             {'text': 'Recorded live at Namba Bears, Osaka\nDedicated to ~Namba~ ~Bears"~'},
             {'text': 'John Roe: Bass/Vocal/Mermaid Mountain'}]
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(cases)], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    for c, x in zip(cases, g or []):
        print('  ', c['text'][:50].replace('\n', ' / '), '→', x['credits'][:6], x['groups'], [i[0] for i in x['ignored']], x['unrecognized'])
    ok = g is not None
    if ok:
        grp = lambda k, name: next((m for n, m in g[k]['groups'] if n == name), None)
        why = lambda k: [i[0] for i in g[k]['ignored']]
        ok = (sorted(grp(0, 'HIBUSHIBIRE') or []) == ['Jane Doe', 'John Roe', 'Max Moe'] and 'fantasy' in why(0)
              and ['Jane Doe', 'guitar'] in [c[:2] for c in g[0]['credits']] and not g[0]['unrecognized']
              and grp(1, 'Acid Mothers Temple & The Melting Paraiso U.F.O.') is not None
              and sorted(grp(2, 'Qien Pudiera') or []) == ['Camila Chapelle', 'Lucia Reyes']
              and 'dedication' in why(3) and not g[3]['unrecognized']
              and 'fantasy' in why(4) and {c[1].lower() for c in g[4]['credits'] if c[0] == 'John Roe'} >= {'bass'}
              and not any('Mermaid' in c[1] for c in g[4]['credits']))
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_members3129r():
    """Credits Importer 3.129.0 (review of S211, S212, S214), in Node: A) "The songs are" and "Live Sound Crew were:" no heading of a group;
    B) "Guitar – John Doe ~ Jane Roe ~ Max Moe": the tildes between names stay (no name "John Doe  Jane Roe  Max Moe"); C) "John Doe (piano, synth, Buddha
    machine)" nothing left out as fantasy; D) a sentence "… on the Pacific coast" no fantasy."""
    node = NODE.replace("unrecognized: r.unrecognized, ignored: r.ignored.map((i) => [i.why, i.text]) };",
                        "unrecognized: r.unrecognized, ignored: r.ignored.map((i) => [i.why, i.text]), groups: (r.groups || []).map((g) => [g.name, g.members]) };")
    cases = [{'text': 'The songs are\nJane Doe - guitar\nJohn Roe - bass\n\nLive Sound Crew were:\nMax Moe - drums'},
             {'text': 'Guitar – John Doe ~ Jane Roe ~ Max Moe'},
             {'text': 'John Doe (piano, synth, Buddha machine)'},
             {'text': 'Jane Doe - field recordings, guitar\nAll field recordings were made by Jane Doe on the Pacific coast'}]
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(cases)], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    for c, x in zip(cases, g or []):
        print('  ', c['text'][:50].replace('\n', ' / '), '→', x['credits'][:6], x['groups'], [i[0] for i in x['ignored']], x['unrecognized'])
    ok = g is not None
    if ok:
        why = lambda k: [i[0] for i in g[k]['ignored']]
        ok = (not g[0]['groups'] and 'groupHeading' not in why(0)
              and not any('Doe  Jane' in c[0] or 'Doe Jane' in c[0] for c in g[1]['credits'])
              and 'fantasy' not in why(2) and 'fantasy' not in why(3))
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_text3128rr():
    """Credits Importer 3.128.0 (review of S203–S208), in Node: A) "Recorded and mixed by Jane Doe at Studio X/Mastered by John Roe at Studio
    Y" – no half left out as a translation (two English halves); B) "1. Song Two (Jane Doe) 5:32" no line of a track list; C) "Limited
    edition of 300 copies, cover art by Jane Doe" – not left out as an edition; D) "Supported by Jane Doe on drums" – no label "Jane Doe on drums";
    E) "all songs written, performed and recorded by sophie in her bedroom over the winter of the year" – "sophie" kept; F) "Jane Doe (alto
    saxophone, flute, …)" with 20 words – no prose."""
    node = NODE.replace("artistNames: c.artists || [], titleNames: c.titles || [] });",
                        "artistNames: c.artists || [], titleNames: c.titles || [], trackTitles: c.titles || null, trackCount: (c.titles || []).length });")
    node = node.replace("companies: r.companies.map((x) => [x.who.name, x.role, ...(x.entity ? [x.entity] : [])]),",
                        "companies: r.companies.map((x) => [x.who.name, x.role]), ignoredWhy: r.ignored.map((x) => x.why),")
    cases = ['Recorded and mixed by Jane Doe at Studio X/Mastered by John Roe at Studio Y',
             '1. Song Two (Jane Doe) 5:32',
             'Limited edition of 300 copies, cover art by Jane Doe',
             'Supported by Jane Doe on drums',
             'all songs written, performed and recorded by sophie in her bedroom over the winter of the year',
             'Jane Doe (alto saxophone, flute, clarinet, bass clarinet, piccolo, recorder, tin whistle, oboe, english horn, bassoon, contrabassoon, soprano saxophone)']
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps([{'text': t, 'titles': ['Song One', 'Song Two']} for t in cases])],
                        capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    for t, x in zip(cases, g or []):
        print('  ', t[:50], '→', x['credits'][:4], x['companies'], x['ignoredWhy'], x['unrecognized'])
    ok = g is not None
    if ok:
        ok = ('translation' not in g[0]['ignoredWhy']
              and 'tracklist' not in g[1]['ignoredWhy']
              and 'edition' not in g[2]['ignoredWhy']
              and not any(c[1] == 'Supported By' for c in g[3]['companies'])
              and any(c[0] == 'sophie' for c in g[4]['credits'])
              and 'prose' not in g[5]['ignoredWhy'])
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_rmx3126r():
    """Credits Importer 3.126.0 (review of Z-RMXTITLE, S200), in Node – remixParts: the names of remixers in titles. "(Stereo Remix)",
    "(2009 Stereo Remix)", "(The Remix)", "(In Dub)", "(Disco Dub)", "(Acoustic Remix)", "(2nd Remix)", "(Remix)", "(Extended Mix)",
    "(Radio Edit)", "(Live)" no name; "(Extended TVAM Remix)" TVAM; "(Radio Edit - TVAM Remix)" TVAM; "(Above & Beyond Remix)" one name;
    "[Remix by Jane Roe & John Doe]" two; "(X feat. Y Remix)" X; "(Moby's Remix)" Moby; "(Dub Syndicate Remix)" Dub Syndicate."""
    titles = ['A (Stereo Remix)', 'A (2009 Stereo Remix)', 'A (The Remix)', 'A (In Dub)', 'A (Disco Dub)', 'A (Acoustic Remix)', 'A (2nd Remix)',
              'A (Remix)', 'A (Extended Mix)', 'A (Radio Edit)', 'A (Live)', 'A (Extended TVAM Remix)', 'A (Radio Edit - TVAM Remix)',
              'A (Above & Beyond Remix)', 'A [Remix by Jane Roe & John Doe]', 'A (X feat. Y Remix)', "A (Moby's Remix)", 'A (Dub Syndicate Remix)']
    want = [[]] * 7 + [[], None, None, None, ['TVAM'], ['TVAM'], ['Above & Beyond'], ['Jane Roe', 'John Doe'], ['X'], ['Moby'], ['Dub Syndicate']]
    node = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
console.log(JSON.stringify(JSON.parse(process.argv[2]).map((t) => { const p = m.remixParts(t); return p ? p.names : null; })));
"""
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(titles)], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    got = json.loads(js.stdout) if not js.returncode else None
    for t, g, w in zip(titles, got or [], want):
        print('  ', t, '→', g, '' if g == w else f'(erwartet {w})')
    ok = got == want
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_exc3125r():
    """Credits Importer 3.125.0 (review of Z-EXCEPTC, S199), in Node – tracks "A", "Salt and Pepper", "This Is Us", "A (X Remix)":
    lower-case credit lines one below the other stay apart; "Music by Jane Doe, written for Radio Birdman" keeps Jane Doe's credit;
    "This piece was commissioned by John Smith" no label; "Composed for the Holland Festival." at the start a commission (all tracks
    but the remix); "All except 'Salt and Pepper' and 'This Is Us' were commissioned for the Roadburn Festival 2025" – track 1 only;
    "All tracks composed by Jane Doe and commissioned by the BBC" no commission of a label "BBC"."""
    titles = ['A', 'Salt and Pepper', 'This Is Us', 'A (X Remix)']
    node = NODE.replace("artistNames: c.artists || [], titleNames: c.titles || [] });",
                        "artistNames: c.artists || [], titleNames: c.titles || [], trackCount: c.titles ? c.titles.length : 0, trackTitles: c.titles || null, resolveTitles: c.titles ? ((ts) => { const ix = new Set(); const un = []; ts.forEach((t) => { const k = c.titles.findIndex((x) => x.toLowerCase() === t.toLowerCase()); if (k >= 0) ix.add(k); else un.push(t); }); return { indexes: ix, unresolved: un }; }) : null });")
    node = node.replace("companies: r.companies.map((x) => [x.who.name, x.role, ...(x.entity ? [x.entity] : [])]),",
                        "companies: r.companies.map((x) => [x.who.name, x.role, x.tracks ? [...(x.tracks.indexes || [])].map((i) => i + 1).join(',') : 'all', (x.date || {}).by || '']),")
    cases = ['jane doe - guitar and vocals and the\nbob roe - drums and percussion',
             'Music by Jane Doe, written for Radio Birdman',
             'This piece was commissioned by John Smith',
             'Composed for the Holland Festival.',
             "All except 'Salt and Pepper' and 'This Is Us' were commissioned for the Roadburn Festival 2025",
             'All tracks composed by Jane Doe and commissioned by the BBC']
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps([{'text': t, 'titles': titles} for t in cases])],
                        capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    for t, x in zip(cases, g or []):
        print('  ', t.replace('\n', ' / '), '→', x['credits'], x['companies'], x['unrecognized'])
    ok = g is not None
    if ok:
        ok = [x[0] for x in g[0]['credits']] == ['jane doe', 'bob roe'] or len({x[0] for x in g[0]['credits']}) == 2
        ok = ok and any(x[0] == 'Jane Doe' for x in g[1]['credits']) \
            and not any(x[1] == 'Commissioned By' for x in g[2]['companies']) \
            and g[3]['companies'] == [['Holland Festival', 'Commissioned By', '1,2,3', '']] \
            and g[4]['companies'] == [['Roadburn Festival', 'Commissioned By', '1', '2025']] \
            and not any(x[0] == 'BBC' and x[1] == 'Commissioned By' and x[2] != 'all' for x in g[5]['companies']) and any(x[0] == 'Jane Doe' for x in g[5]['credits'])
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_qp3124r():
    """Credits Importer 3.124.0 (review of Z-QPBAND, Z-CPYEAR, Z-CATNO, Z-INMEM, Z-WEBDOM), in Node:
    names with a dot stay names ("Mixed by J.Media", "Mastered by Studio.One"); "Special guest John Smith : vocals (3)" – vocals
    [Guest] on track 3; "Guest Vocals : Jane Doe" – no name "Jane Doe [Guest]"; "The band is joined by Jane Doe : vocals" – no members;
    "Copyright 2026" alone not read as ©; the catalogue number "001": "2001" is none (left out as before: no letters), "001" is;
    "In memory of John Doe, who played drums on track 3" no dedication-only line; "castlesin.space" a website."""
    node = NODE.replace("artistNames: c.artists || [], titleNames: c.titles || [] });", "artistNames: c.artists || [], titleNames: c.titles || [], catnos: c.catnos || [] });")
    node = node.replace("credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),",
                        "credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : []), ...((x.details || []).length ? [x.details.join('+')] : [])]),")
    cases = [{'text': 'Mixed by J.Media\nMastered by Studio.One'},
             {'text': 'Special guest John Smith : vocals (3)'},
             {'text': 'Guest Vocals : Jane Doe'},
             {'text': 'The band is joined by Jane Doe : vocals', 'artists': ['The Band']},
             {'text': 'Copyright 2026', 'catnos': ['001']},
             {'text': '2001\n001', 'catnos': ['001']},
             {'text': 'castlesin.space'}]
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(cases)], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    for c, x in zip(cases, g or []):
        print('  ', c['text'].replace('\n', ' / '), '→', x['credits'], x['companies'], x['unrecognized'], x['ignored'])
    ok = g is not None
    if ok:
        ok = [x[0] for x in g[0]['credits']] == ['J.Media', 'Studio.One'] \
            and any(x[0] == 'John Smith' and 'Guest' in (x[-1] if len(x) > 2 else '') for x in g[1]['credits']) and not g[1]['unrecognized'] \
            and not any('[Guest]' in x[0] for x in g[2]['credits']) \
            and not any(i[0] == 'members' for i in g[3]['ignored']) \
            and not g[4]['companies'] \
            and [i[1] for i in g[5]['ignored'] if i[0] == 'catno'] == ['001'] \
            and [i[0] for i in g[6]['ignored']] == ['web']
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_tbl392r():
    """Credits Importer 3.92.0 (review of Z-TBL, rule S145), in Node: the block of a track's title holds its "Name: roles" lines only.
    A tracklist above the credits ("1. Opening" …, "Side A" / "A1 Opening" …, bare titles) opens no block – the credits below are of all
    tracks; a line that is no "Name: roles" ("Mixed by …") ends a block; a band's name above its members ("Black Sabbath", a track of
    that name) opens none; a position beyond the tracks ("12.") none; a quoted title of no track ends the block before it."""
    titles = ['Opening', 'Love', 'Closing', 'Black Sabbath']
    cases = ['Tracklist:\n1. Opening\n2. Love\n3. Closing\n\nCredits:\nJohn Smith: guitar\nMixed by Bob Roe',
             '"Opening"\nJohn Smith: guitar\n"Love"\nJane Doe: piano\n\nMixed by Bob Roe\nMastered by Carl Poe',
             'Side A\nA1 Opening\nA2 Love\nSide B\nB1 Closing\n\nJohn Smith: guitar',
             'Love\nPeace\nClosing\n\nJohn Smith: guitar',
             'Black Sabbath\nOzzy Osbourne: vocals\nTony Iommi: guitar',
             '12. "Bonus Song"\nJohn Smith: guitar',
             '"Opening"\nJohn Smith: guitar\n\n"Bonus Song"\nJane Doe: piano']
    node = NODE.replace("resolveTracks: trackSet(c.tracks || 14),", "resolveTracks: trackSet(c.tracks || 14), trackCount: c.count || 0, resolveTitles: c.titles ? ((ts) => { const ix = new Set(); const un = []; ts.forEach((t) => { const k = c.titles.findIndex((x) => x.toLowerCase() === t.toLowerCase()); if (k >= 0) ix.add(k); else un.push(t); }); return { indexes: ix, unresolved: un }; }) : null,")
    node = node.replace("credits: r.credits.map((x) => [x.who.name, x.role, ...(x.tracks && x.tracks.spec ? [x.tracks.spec] : [])]),",
                        "credits: r.credits.map((x) => [x.who.name, x.tracks ? [...(x.tracks.set || x.tracks.indexes || [])].map((i) => i + 1).join(',') || 'all' : 'all']),")
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'),
                         json.dumps([{'text': t, 'titles': titles, 'count': 4} for t in cases])], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    g = json.loads(js.stdout) if not js.returncode else None
    got = [x['credits'] for x in g] if g else None
    for t, x in zip(cases, got or []):
        print('  ', t.replace('\n', ' / ')[:70], '→', x)
    ok = got == [[['John Smith', 'all'], ['Bob Roe', 'all']], [['John Smith', '1'], ['Jane Doe', '2'], ['Bob Roe', 'all'], ['Carl Poe', 'all']],
                 [['John Smith', 'all']], [['John Smith', 'all']], [['Ozzy Osbourne', 'all'], ['Tony Iommi', 'all']], [['John Smith', 'all']],
                 [['John Smith', '1'], ['Jane Doe', 'all']]]
    print('Ergebnis:', 'OK' if ok else 'FEHLER', [ok])


def case_z381():
    """Credits Importer 3.81.0 (collected items Z-OTR, Z-SLD, Z-SYN, Z-POR, Z-RAD, Z-YTT; rules S119 – S121, R112, R113).
    A) "Andy Becker - Baritone Electric Guitar on track 2 & 6, Synth on track 2", "Joe Davin - Bass Guitar on track 2,4,6, Double Bass
       on track 3": each role with its tracks (S120; until 3.80.0 "? “Bass Guitar on track 2”, “4”, “6”").
    B) Roles (Node): "Juno 101", "Korg Minilogue" – synthesizer (R113), "Roland TR-808" – drum machine, "Akai MPC 2000XL" – sampler, each
       credited as written; "Appalachian/Hammered Dulcimer" – Appalachian dulcimer and hammered dulcimer (S119); "Piano/Keys" stays two;
       "Album portraits", "Portraits" – photography on the release, credited "album portraits" / "portraits" (R112).
    C) "This was recorded by Norwegian State radio, at …": the radio a label – recording and broadcast (S121), no "This was" (until 3.80.0
       its role credit); "It was mixed by Jane Roe": Jane Roe mix, no detail.
    D) Songs of a video (Z-YTT): "Anoyo Drive 00:32" / "Melting 13:37" / "Iyo no Hito 23:16" (the time last, no heading) – three songs;
       "Doors 19:00" / "Support 20:00" / "Main act 21:00" – a schedule, no songs."""
    got = read([{'text': 'Andy Becker - Baritone Electric Guitar on track 2 & 6, Synth on track 2'},
                {'text': 'Joe Davin - Bass Guitar on track 2,4,6, Double Bass on track 3'},
                {'text': 'This was recorded by Norwegian State radio, at the Hennie-Onstad art centre outside Oslo on September 11th 1983.'},
                {'text': 'It was mixed by Jane Roe.'},
                {'text': 'Album portraits by Selina Mayer'}])
    for g in got:
        print('  ', g and g['credits'], g and g['companies'], g and g['unrecognized'])
    a = got[0]['credits'] == [['Andy Becker', 'Baritone Electric Guitar', '2 & 6'], ['Andy Becker', 'Synth', '2']] \
        and got[1]['credits'] == [['Joe Davin', 'Bass Guitar', '2,4,6'], ['Joe Davin', 'Double Bass', '3']] and not got[0]['unrecognized'] and not got[1]['unrecognized']
    c = ['Norwegian State radio', 'Recorded By', 'label'] in got[2]['companies'] and ['Norwegian State radio', 'Broadcast By', 'label'] in got[2]['companies'] \
        and not any('This was' in x[1] for x in got[2]['credits'] + got[2]['companies']) and got[3]['credits'] == [['Jane Roe', 'Mixed By']]
    por = got[4]['credits'] == [['Selina Mayer', 'Album portraits By']]
    node = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const one = (r) => { const p = m.parseRoleNotation(r)[0]; const x = m.mapRole(p.base, p.mods); return [r, x.rule, x.types, (x.primaryCands || []).slice(-1)[0] || '', x.credit, x.level]; };
const isRole = (phrase) => { const p = m.parseRoleNotation(phrase)[0]; return !!p && /^(appalachian dulcimer|hammered dulcimer|piano|keys|dulcimer)$/i.test(p.base); };
const split = m.SOURCES.text.parse('Tsinder Ash - Appalachian/Hammered Dulcimer, Piano/Keys', { isRole, isCompanyRole: () => false, resolveTracks: () => null, artistNames: [], titleNames: [] });
console.log(JSON.stringify({ roles: ['Juno 101', 'Korg Minilogue', 'Roland TR-808', 'Akai MPC 2000XL', 'Album portraits by', 'Portraits', 'Piano'].map(one),
  split: split.credits.map((x) => x.role) }));
"""
    js = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    b0 = json.loads(js.stdout) if not js.returncode else {'roles': [], 'split': []}
    for r in b0['roles']:
        print('  ', r)
    print('   split:', b0['split'])
    want = [['Juno 101', 'R113', ['instrument'], 'synthesizer', 'Juno 101', 'recording'], ['Korg Minilogue', 'R113', ['instrument'], 'synthesizer', 'Korg Minilogue', 'recording'],
            ['Roland TR-808', 'R113', ['instrument'], 'drum machine', 'Roland TR-808', 'recording'], ['Akai MPC 2000XL', 'R113', ['instrument'], 'sampler', 'Akai MPC 2000XL', 'recording'],
            ['Album portraits by', 'R112', ['photography'], '', 'Album portraits by', 'release'], ['Portraits', 'R112', ['photography'], '', 'Portraits', 'release'],
            ['Piano', 'R096', ['instrument'], 'piano', '', 'recording']]
    b = b0['roles'] == want and b0['split'] == ['Appalachian Dulcimer', 'Hammered Dulcimer', 'Piano', 'Keys']
    songs = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const ctx = { isRole: () => false, isCompanyRole: () => false, resolveTracks: () => null, artistNames: [], titleNames: [], songs: true };
console.log(JSON.stringify(['Anoyo Drive 00:32\nMelting 13:37\nIyo no Hito 23:16', 'Doors 19:00\nSupport 20:00\nMain act 21:00'].map((t) => m.SOURCES.text.parse(t, ctx).songs)));
"""
    js2 = subprocess.run(['node', '-e', songs, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    d0 = json.loads(js2.stdout) if not js2.returncode else None
    print('   songs:', d0, js2.stderr[-300:])
    d = d0 == [['Anoyo Drive', 'Melting', 'Iyo no Hito'], []]
    print('A)', a, '| B)', b, '| C)', c, '| portraits:', por, '| D)', d)
    print('Ergebnis:', 'OK' if a and b and c and por and d else 'FEHLER', [a, b, c, por, d])


def case_improv3133():
    """Credits Importer 3.133.0 (collected item Z-IMPROV, S222): a pasted text "All music was improvised by Anna Neu and Bob Roe" – both
    composers of the works (rows "Composed By" on the work level, columns of the works matrix), marked "improvisation" at the head of their
    entries, their columns and each track of the matrix (the line quoted); a track titled "Improvisation III" alone is marked too (by its title).
    B) S222 off: the line left out ("improvisations"), no composer, no mark."""
    H.TITLES[:] = ['Song One', 'Improvisation III', 'Song Three', 'Song Four']
    TEXT = "All music was improvised by Anna Neu and Bob Roe\nAnna Neu – piano\nBob Roe – drums"
    ROWS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  return g ? [!!g.querySelector('.dci-gname .dci-improv-mark'), ...[...g.querySelectorAll('tr.dci-row')].map(r => r.querySelector('.dci-drole').dataset.raw.trim())] : null; }"""
    MX = "[...document.querySelectorAll('[data-el=works] tr[data-work]')].map(tr => [tr.dataset.work, (tr.querySelector('.dci-mx-title .dci-improv-mark') || {}).title || ''])"
    COLS = "[...document.querySelectorAll('[data-el=works] th[data-colhead]')].map(th => [th.querySelector('.dci-mx-colname').textContent.replace(/\\s+/g, ' ').trim(), !!th.querySelector('.dci-improv-mark')])"
    results = []
    for off in (False, True):
        H.RULES_OFF[:] = ['S083'] + (['S222'] if off else [])
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
            pg.wait_for_timeout(2500)
            anna = pg.evaluate(ROWS, 'Anna Neu')
            mx = pg.evaluate(MX)
            ign = pg.evaluate("[...document.querySelectorAll('.dci-ign-why')].map(x => x.textContent.replace(/^–\\s*/, '').trim())")
            cols = pg.evaluate(COLS)
            print('B)' if off else 'A)', 'Anna Neu:', anna, '| Matrix:', mx, '| Spalten:', cols, '| ausgelassen:', ign)
            if not off:
                results.append(anna is not None and anna[0] and any('Anna Neu' in n and m for n, m in cols) and any('Bob Roe' in n and m for n, m in cols)
                               and len(mx) == 4 and all('All music was improvised by Anna Neu and Bob Roe' in t for _, t in mx))
            else:
                results.append(anna is not None and not anna[0] and not any('Anna Neu' in n for n, m in cols) and not any(t for _, t in mx)
                               and 'improvisations (no works: switched off)' in ign)
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    H.RULES_OFF[:] = ['S083']
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_improvtitle3133():
    """Credits Importer 3.133.0 (Z-IMPROV, S222): without a line of improvisations, a track titled "Improvisation III" (and "Impro 2") is marked
    "improvisation" in the works matrix by its title; "Improvisation in Blue" and ((review) "Improvisation Civil" are no such titles."""
    H.TITLES[:] = ['Improvisation Civil', 'Improvisation III', 'Impro 2', 'Improvisation in Blue']
    TEXT = "Anna Neu – piano\nBob Roe – drums"
    MX = "[...document.querySelectorAll('[data-el=works] tr[data-work]')].map(tr => (tr.querySelector('.dci-mx-title .dci-improv-mark') || {}).title || '')"
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
        pg.wait_for_timeout(2000)
        mx = pg.evaluate(MX)
        print('A) Matrix:', mx)
        results.append(mx == ['', 'Improvisation – by its title: “Improvisation III”', 'Improvisation – by its title: “Impro 2”', ''])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_dgexcl3134():
    """Credits Importer 3.134.0 (collected items Z-DGEXCL, Z-LINEUPALL; rules S150, S159, S175, S054, S217 for every free text), a pasted text:
    A) "Arranged by Cid Doe" – the arranger on the works (a column of the works matrix; until 3.133.0 on the recordings: Discogs only).
    B) "Producer: Anna Neu" and "Produced by Anna Neu" – one row (nothing twice; until 3.133.0 two).
    C) "Recorded at Tonart Studio" and "Mixed at Tonart" – one place Tonart Studio with both rows (no entry "Tonart").
    D) "Design: Cyclical Dreams" with "℗ 2024 Cyclical Dreams" – the label Cyclical Dreams (artwork of a label; until 3.133.0 Discogs only).
    E) The lineup (Anna Neu bass, Bob Roe drums, Cid Doe guitar) and lines of tracks ("Track 2: Anna Neu – double bass", "Track 3: Bob Roe –
       drums, Cid Doe – guitar"): the question "Lineup and track credits (pasted text)" (until 3.133.0 Discogs only).
    (review) "Design: Cyclical Dreams" becomes the label only as MusicBrainz's label (a text's ℗ line may name a person)."""
    H.TITLES[:] = ['One', 'Two', 'Three', 'Four']
    H.COMPANIES[913401] = ('place', H.uid('eeeeeeee', 9134), 'Tonart Studio')
    H.COMPANIES[913402] = ('label', H.uid('1abe1000', 9134), 'Cyclical Dreams')
    import copy
    lts0, linked0 = copy.deepcopy(H.LTS), copy.deepcopy(H.LINKED.get('link_type'))
    for i, name in ((1170, 'artwork'), (1171, 'design'), (1172, 'graphic design'), (1173, 'illustration'), (1174, 'art direction'), (1175, 'photography')):
        H.lt(i, H.uid('1aaa0000', i), name, 'label', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    TEXT = """Anna Neu – bass
Bob Roe – drums
Cid Doe – guitar
Track 2: Anna Neu – double bass
Track 3: Bob Roe – drums, Cid Doe – guitar
Arranged by Cid Doe
Producer: Anna Neu
Produced by Anna Neu
Recorded at Tonart Studio
Mixed at Tonart
Design: Cyclical Dreams
℗ 2024 Cyclical Dreams
Photography: Jane Doe
© 2024 Jane Doe"""
    ROWS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  return g ? { kind: (g.className.match(/dci-kind-(\\w+)/) || [])[1] || '', rows: [...g.querySelectorAll('tr.dci-row')].map(r => [r.querySelector('.dci-drole').dataset.raw.trim(),
    (r.querySelector('[data-f=credit]') || { value: '' }).value, (r.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level || '']) } : null; }"""
    COLS = "[...document.querySelectorAll('[data-el=works] th[data-colhead] .dci-mx-colname')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())"
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
        pg.wait_for_timeout(2500)
        pg.evaluate("document.querySelectorAll('tr.dci-row [data-act=row-open], tr.dci-row .dci-row-open').forEach(b => b.click())")
        pg.wait_for_timeout(500)
        cols = pg.evaluate(COLS)
        anna = pg.evaluate(ROWS, 'Anna Neu')
        place = pg.evaluate(ROWS, 'Tonart Studio')
        tonart = pg.evaluate(ROWS, 'Tonart')
        cd = pg.evaluate(ROWS, 'Cyclical Dreams')
        jd = pg.evaluate(ROWS, 'Jane Doe')
        box = pg.evaluate("(document.querySelector('[data-el=dglineup] strong') || {}).textContent || ''")
        print('A) Spalten:', cols)
        print('B) Anna Neu:', anna)
        print('C) Tonart Studio:', place, '| Tonart:', tonart, pg.evaluate("[...document.querySelectorAll('section.dci-group')].filter(g => /Tonart/.test(g.textContent)).map(g => g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').slice(0, 120) + ' | ' + [...g.querySelectorAll('tr.dci-row')].map(r => r.textContent.replace(/\\s+/g, ' ').slice(0, 100)).join(' # '))"))
        print('D) Cyclical Dreams:', cd, '| Cid Doe:', pg.evaluate(ROWS, 'Cid Doe'))
        print('E) Frage:', box)
        results.append(any('Cid Doe' in c for c in cols))
        results.append(bool(anna) and sum(1 for r in anna['rows'] if r[0] in ('Producer', 'Produced By')) == 1)
        results.append(bool(place) and place['kind'] == 'place' and sorted(r[0] for r in place['rows']) == ['Mixed At', 'Recorded At'] and not tonart)
        print('   Jane Doe:', jd)
        results.append(bool(cd) and cd['kind'] == 'label' and bool(jd) and jd['kind'] == 'artist')
        results.append(box == 'Lineup and track credits (pasted text)')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    H.LTS.clear()
    H.LTS.update(lts0)
    H.LINKED['link_type'] = linked0
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_dgexcl3134r():
    """Credits Importer 3.134.0 (review of Z-DGEXCL, Z-LINEUPALL), a pasted text: "Produced by John Smith (track 1)" and "Producer: John Smith
    (track 3)" two rows (lines of tracks of one text); "Photography: Ann Lee" and "Cover photo: Ann Lee" two (another role credit); "Michael Novak" and
    "Michal Novak" two people; lines of tracks that only add ("Track 2: Anna Neu – vocals", "Track 3: Bob Roe – percussion") ask no lineup
    question; "Vocals on tracks 2, 4 by Jane Doe, arranged by Writer Z" – the arranger stays on the recordings."""
    H.TITLES[:] = ['One', 'Two', 'Three', 'Four']
    TEXT = """Produced by John Smith (track 1)
Producer: John Smith (track 3)
Photography: Ann Lee
Cover photo: Ann Lee
Michael Novak – piano
Michal Novak – piano
Anna Neu – bass
Bob Roe – drums
Track 2: Anna Neu – vocals
Track 3: Bob Roe – percussion
Vocals on tracks 2, 4 by Jane Doe, arranged by Writer Z"""
    ROWS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  return g ? [...g.querySelectorAll('tr.dci-row')].map(tr => [tr.querySelector('.dci-drole').dataset.raw.trim(),
    [...document.querySelectorAll(`tr[data-tracksrow="${tr.dataset.row}"] input[data-f=track]:checked`)].map(c => Number(c.dataset.i) + 1)]) : null; }"""
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
        pg.wait_for_timeout(2500)
        pg.evaluate("document.querySelectorAll('tr.dci-row [data-act=row-open], tr.dci-row .dci-row-open').forEach(b => b.click())")
        pg.wait_for_timeout(500)
        js = pg.evaluate(ROWS, 'John Smith')
        al = pg.evaluate(ROWS, 'Ann Lee')
        names = pg.evaluate("[...document.querySelectorAll('section.dci-group .dci-gname strong')].map(x => x.textContent.trim())")
        box = pg.evaluate("!!document.querySelector('[data-el=dglineup]')")
        wz = pg.evaluate(ROWS, 'Writer Z')
        print('A) John Smith:', js, '| Ann Lee:', al, '| Novak:', [n for n in names if 'Novak' in n], '| Frage:', box, '| Writer Z:', wz)
        # ((3.134.0) two lines of tracks of one text stay two credits – the blocks of tracks of a text name a person per track)
        results.append(js is not None and len(js) == 2 and sorted(r[1] for r in js) == [[1], [3]])
        results.append(al is not None and len(al) == 2)
        results.append(sorted(n for n in names if 'Novak' in n) == ['Michael Novak', 'Michal Novak'])
        results.append(not box)
        results.append(wz is not None and any(r[0] == 'Arranged By' for r in wz))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
