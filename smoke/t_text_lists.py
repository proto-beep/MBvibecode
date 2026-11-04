"""Texts from Bandcamp's credits of 2026-11 ("Intentions", "Throats"; Credits Importer 3.48.0 –): lines read in Node with the text
adapter, as t_textcorpus.py does (the roles: the register and a few instruments as MusicBrainz has them).

Cases: hyphen, ignorelines, linernotes (3.48.0), rolesplit, roles, places, oldmarks, exceptread, exceptworks, exceptlayouts, rolesplit2,
exceptworks2 (3.49.0); `python3 t_text_lists.py <case> …` runs only those."""
import json
import subprocess
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser

NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const isRole = (phrase) => { const p = m.parseRoleNotation(phrase)[0]; if (!p || !p.base || /\d/.test(p.base)) return false;
  const r = m.mapRole(p.base, p.mods); return !!(r.rule && r.rule !== 'R096' && !r.fallback) || !!r.translated
  || /^(?:additional\s+)?(piano|bass|guitar|drums|vocals|synth|synths|saxophone|trumpet|flute|harp|rhodes|percussion|jaw harp|highland bagpipes|bagpipes|sampler|analog synthesizer|electronic valve instrument|juno|evi)$/i.test(p.base); };
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
    sampler; harmonic overtone singing – a voice (R011); Juno – analog synthesizer, credited "Juno"; EVI – electronic valve instrument;
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
            ['Juno', 'R096', ['instrument'], 'analog synthesizer'], ['EVI', 'R096', ['instrument'], 'electronic valve instrument'],
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


run_cases(globals())
