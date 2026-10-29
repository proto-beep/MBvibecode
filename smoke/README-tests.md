# MB x Vibecode – test tools

Browser tests for **MB x Vibecode: Credits Importer** and its **Companion** (until 3.0.0 / 1.5.0 “Import Discogs credits”
and “… COMPANION”), run with Playwright (Python) and Chromium. MusicBrainz, Discogs and Bandcamp are not reached:
`harness.py` serves a mock relationship editor (`MB.relationshipEditor`, `MB.linkedEntities`, `MB.tree`), the
MusicBrainz web service (lookups and the search), the MusicBrainz release page, the Discogs API, a Discogs release page
and Bandcamp album and track pages. The userscript manager's shared storage (`GM_setValue` …) is replaced by a small local HTTP
server, so the companion shares its values between pages as it does in Tampermonkey.
For the text from cover art (beta) it serves the Cover Art Archive (PNGs of the sizes given), a stand-in of Tesseract.js as
from jsDelivr and – from 3.34.6 – the real pdf.js as from jsDelivr, taken from a local copy of the npm package `pdfjs-dist`
(`PDFJS_DIR`: `/opt/npm-tools/node_modules`, `~/.npm-global/lib/node_modules` or `node_modules` next to the scripts; without
it the case `ocrpdf` fails); `pdf_of()` writes small PDFs.

## Layout

```
MBvibecode/ (this repository)
  mb-vibecode-credits-importer.user.js             main script
  mb-vibecode-credits-importer-companion.user.js   companion
  mb-vibecode-credits-importer-mapping.json     the data of the mapping register (3.33.0, @resource mapping)
  mb-vibecode-credits-importer-languages.json   German, Spanish, French (3.34.0, @resource languages; English in the script)
  tools/i18n_add.py                   adds or replaces texts: English in the script, de / es / fr in the languages file (3.34.0)
  tools/i18n_del.py                   removes texts in all languages (script and languages file, with plural forms)
  smoke/harness.py                    mock MusicBrainz, Discogs and Bandcamp, shared GM storage, helpers
  smoke/zooid.py                      scenario after Discogs release 38282688 (10 tracks, two sessions, two studios)
  smoke/common_rows.py                helpers for the date tests: rows (tracks, date), matrix cells, staging, drag with the mouse
                                      (the target is scrolled to the middle first: near the edges the dashboard scrolls while dragging);
                                      [3.34.29] ENTRIES_VIEW: the entries as before ('legacy') for every file but t_entries.py – the matrix
                                      (E4, the script's default) is tested there; [3.34.30] with the generation of the stored data;
                                      [3.36.0] REMEMBER: True – ⚙ Settings → Cache "Remember … per release" switched on before the
                                      script starts (the files written before expect the stores of a release kept); False in
                                      t_ui_settings.py cache and t_entries.py order (the script's default: off)
                                      date_field(row, f): a date field of a row – opens a date chip (3.9.0) first
  smoke/caserun.py                    [3.31.1] runs the cases of a topic file: one shared browser, what a case changes in the
                                      harness set back after it, one result per case and one for the file
  smoke/t_*.py                        tests: topic files with cases (case_<name>, each the former t_<name>.py), and seven
                                      files of their own (golden tests, comparisons with older logs); each ends with
                                      "Ergebnis: OK/FEHLER"
  smoke/register_corpus.json          frozen input of the register's golden test (t_register.py)
  smoke/register_golden.json          its expected results (written with UPDATE=1)
  smoke/text_corpus.json              credits lines from real releases and cases around them, with their stored reading
                                      ('expect', written with UPDATE=1 by t_textcorpus.py; 'later': still read wrong, planned)
```


## Running

```
pip install playwright && python -m playwright install chromium   # once
# Node.js is needed too: t_register.py, t_textcorpus.py, t_static.py and the case adapter of t_sources.py load the script in Node
cd smoke
```

Since 3.31.1 (collected item 103) the tests of a topic are cases of one file: `python3 t_text_languages.py` runs all its
cases, `python3 t_text_languages.py sounds members` only those. Each case is the former test file, unchanged: it prints its
own lines and its "Ergebnis: …"; `caserun.py` adds "== name: OK" / "== name: FEHLER" after each case and the result of
the file at the end ("Ergebnis: OK [n Fälle]", or the names of the cases that failed). One browser serves all cases of a
file (each opens its own context and pages); what a case changes in the harness – the Discogs data, the search
results, relationship types, the shared storage – is set back before the next one. The tests ask the mock MusicBrainz
every 25 ms instead of the script's 1.1 s (`harness.MB_GAP`, environment `DCI_MB_GAP`, 0 = the script's gap): an import
takes about 1 s. Cases whose checks depend on that time (artistworks, logplace) and the comparisons with
older logs set `H.MAIN = H.MAIN_SLOW` (the script with its own gap).

```
python3 t_basic.py              # dashboard loads, companion connected, status marks on Discogs
python3 t_focus.py              # typing in every date field keeps cursor and text
python3 t_release.py            # MusicBrainz release page checks what arrived (✓ / ✗), marks go when closed
python3 t_ar.py                 # A&R with task on the release group
python3 t_artwork.py            # cover miniature on the Discogs page: shown when connected, click, fold, drag, place kept
python3 t_register.py           # the mapping register stays the same (3.11.0, golden test): a frozen corpus (register_corpus.json:
                                # ~1,200 roles, ~100 company roles, ~50 date phrases, pasted texts) through the register in Node, the
                                # texts in the dashboard and the window "Mapping rules" – compared with register_golden.json;
                                # UPDATE=1 python3 t_register.py writes the golden file anew after a change of the register that is meant
                                # (3.33.1: ✎, "code" and the forms of the window are hidden before its sections are read; 3.36.0: the
                                # texts only after the import of the release is complete – before, their end depended on the timing)
python3 t_textcorpus.py         # text recognition, part 1 (3.21.0): the corpus text_corpus.json through the text adapter (golden), then the
                                # Maya Recordings credits in the dashboard – four sentences in one line, "P + ©", thanks and strings left out
                                # on purpose, no 1988 in the pool; "Logo by … instagram.com/…" (design, "logo", the profile, a suggestion via
                                # it), "Create artist …" with the profile (not Linktree), "Text" answered with lyricist → works matrix
                                # 3.21.3: links hidden at first, shown with the setting, Spotify only for "Create artist …", "Create place …"
                                # with a studio's profile
                                # 3.22.0: the corpus with titles ("on “A”, “B”") and areas ("(Asturies, Spain)"), no "later" lines
                                # 3.31.1: the lines of the cases sounds, members, pcline, discnotes and publishers; a line may name the
                                # release's artists ("artists") and its number of tracks ("tracks")

python3 t_text_basics.py        # Texts, part 1: a pasted text, the rules for free texts, lists of names, "credited as", distribution
                                #   freetext: credits from a pasted text (3.2.0): "Name – roles", "Role: names", two clauses in a line, places
                                #     ("Recorded live at …", "Mastered by A at Studio"), tracks ("Tracks 3–4: …", "(1, 3)"), ℗, lines not
                                #     recognized; works matrix; names only suggested (dashed, yellow), a click assigns; edit note
                                #   textrules: rules for free credits texts (3.14.0): "Music played and recorded by X in March and April 2025",
                                #     "Mixed and mastered by X in May 2025", "Photography Sam Lee", "mastering john doe", the label line
                                #     left out, "… created by a human" → the release's artist suggested; the period 2025-03 – 2025-04
                                #   names: texts (3.6.0): "tenor & soprano sax, trumpet and clarinet" (shared instrument word), "bass & electric
                                #     guitar" stays two; a list with an unknown part ("→ ? “sticks-and-stones”"); name suggestions without
                                #     accents ("Agusti" → "Agustí") and "similar name" with a middle name ("Barry Guy" → "Barry John Guy")
                                #   textcredit: 3.28.4: "Cover/Sleeve/Booklet/Package Design" → design "… design", "Artwork [Design And Layout]" one row
                                #     "design and layout", "Artist credit for all roles" empty for a case-only spelling, a text's name linked:
                                #     credited as written (not when only the case differs)
                                #   distrib: "Distribution - !K7" and variants (3.17.3, T028): company "Distributed By", label → release distributed
                                #   playedby: 3.34.19: Go Kurosawa's "soft shakes" – twenty lines of instruments, "are played, mixed and produced
                                #     by Go Kurosawa": a row per instrument, Mixed By, Produced By, no Played By, "Chaims" not recognized
                                #     (S051); in one line "… are played by Jane Roe", "Bass Man plays bass and drums"; "are mixed by" (T050)
                                #   instrguess: 3.34.20: Bongo → bongos, Woodblock → wood block … (T001); "Chaims" asks "did you mean: chimes ·
                                #     wind chimes · tubular bells · other instruments “chaims”" (also in the compact line), each choice and its
                                #     credit; "Buddha machine" other instruments credited "Buddha machine" at once (3.34.28: a proper name, T052);
                                #     "Voice" asks (Q011), "use “voice” as role
                                #     credit" after a voice typed in
                                #   voicetech: 3.34.25: Discogs "Voice" asks four answers (spoken vocals “voice” chosen), "Vocals" plain; "Technician
                                #     [Guitar]" → instrument technician · guitar, "Drum Technician" → drums (drum set), no credit; "[Chaims]" asks
                                #   unknownask: 3.34.26: Discogs "Chaims" asks with "miscellaneous support (task “chaims”)" last – chosen: misc with the
                                #     task, then chimes: an instrument row again; "Sticks-And-Stones": other instruments at once; "Barry Guy – double
                                #     bass, sticks-and-stones" – other instruments “sticks-and-stones”; more unknown words than instruments: not recognized;
                                #     3.34.27 (S052): credits and tasks in lower case ("chaims", "sticks-and-stones"), the field's suggestions too ("Tambourine
                                #     [Additional, Toy]": toy · … · toy tambourine), a proper name of MB's instruments kept ("Hammond manager")
                                #   casenote: 3.34.28 (S052a/b, T052): "Guitar [Gretsch Duo Jet]" (until 3.35.2 "Gibson Les Paul") → "Gretsch duo jet"
                                #     with the note "Written small – …: Duo Jet → duo jet · keep · always · Duo → duo …", in the compact line too; keep /
                                #     write small again / always (stored in T052, a second row follows); text "Sticks-And-Stones" noted, "Buddha
                                #     machine" kept; a known role without a note
                                #   casephrase: 3.35.2 (item 144): "Gibson Les Paul" from T052 as a whole, "Les Paul Junior" → "Les Paul junior" (only
                                #     "Junior" noted), "Paul Reed Smith" offered as a whole first (note and compact line), keep / small again / always
                                #     (stored, a second row follows), a "Les" in a text stays small

python3 t_text_languages.py     # Texts, part 2: other languages and prose – German, Spanish, French, Nordic roles, prose credits, "sounds", band members
                                #   foreign: instruments and voices in German, Spanish, French (3.21.2): mapped as the English term without role credit,
                                #     "saxo tenor y soprano", "y" between names, "bajo" asks like "Bass", "Alto" asks (viola …), T034 in the window
                                #   nordic: Norwegian, Swedish and Danish roles (3.28.2): no role credit for a translation in brackets or a text, "Artwork
                                #     [Logo Og Kunst]" → design "logo" + artwork "art" (two marks on Discogs), vocals "screams"/"clean", case-only
                                #     names without "credited as" (typed in: kept), "Wood Flute"/"wood flutes" → flute credited so;
                                #     3.28.3: the rules named at the rows (S031 – S035, S033 not S018)
                                #   prose: 3.29.0 (milestone): ekstasis' prose credits (K.M. (sounds, words) & E. (voice), "channeled by", "the
                                #     guided hand of"), "Mixed and mastered at TQA.HQ (July 2026)", "Tenor, alto, soprano saxophones",
                                #     "wood flutes", "Mixed and mastered by … in March 2026" – rows, places and the date matrix;
                                #     3.29.1: "(noises, electronics)" → effects "noises", electronic instruments "electronics", "(field
                                #     recordings)" → field recordist
                                #   sounds: 3.30.6: "Sounds" (Discogs, text, prose) – performer with the question performer · effects "sounds",
                                #     effects chosen gives the role credit "sounds"
                                #   members: 3.30.7: "Vision Fortune are AC Williams, Alex Townend and Andres Ayerbe" – three performers (pasted text
                                #     and the "about" text of Bandcamp); "The band is now a trio." and "… is back with a new album." nothing

python3 t_text_places.py        # Texts, part 3: titles and areas, credit pairs, the medium of the release, names with initials, places with a date
                                #   areas: text recognition, part 2 (3.22.0): "Recorded by X in Xixon, Asturies, Spain" – X and an area entry (kind Area,
                                #     Gijón suggested by its alias "Xixón", no "Create", "recorded in" staged on the recordings); tracks by their
                                #     titles ("Piano in ‘A' and 'B' is a contribution by X", one letter off, "Not matched"); Bandcamp: titles of the
                                #     album, the area of the "about" text
                                #   v3222: 3.22.2: "Kontrabass" → double bass (3.22.3: without role credit; text and Discogs), "Contrabass" credited
                                #     "contrabass", "Violoncello" → cello "violoncello";
                                #     produced / remixed / engineered in (areas with the area they are part of); recording without role credit
                                #     (also with a task field); the rules window's patterns ("(manufactured | made) (by | at)")
                                #   medium: the medium of the release decides (3.21.4): vinyl mastering, "(vinyl)", lacquer cut on Digital Media left out
                                #     with the reason (and a studio only for it), the digital half kept; "Translated by" on Bandcamp asks
                                #   initials: name suggestions for names with an initial (3.13.0): "T. Snekkestad" → Torben Snekkestad, "Barry J. Guy"
                                #     → Barry John Guy, "K. Tanaka" → Kenji (not Hiro) Tanaka, no second search without an initial
                                #   placedate: 3.32.5: "All songs recorded and engineered at El Studio in San Francisco on September 3rd and 4th
                                #     2016." – El Studio (San Francisco) recorded at + engineered at, the days in the pool; "Studio Sol in
                                #     Marseille" keeps its area; "Muisc and cover art by Jo Vaman" – Music By (S050, the column head of the
                                #     works matrix says "Read as “Music” (written “Muisc”)"); ⚙ Settings → Texts switches S050 off (stored),
                                #     the line is not recognized then; ↺ of the tab switches it on
                                #   recordedin: 3.34.18: the year before the month (D024: "2024 January - July", "2024 Jan - Jul", "2024 March",
                                #     "2024 March 3–5", "2024 March 30 – April 2"; "© 2019 March Records" the year only); "Recorded in Guruguru
                                #     Brain studio, Rotterdam, 2024 January - July" – the place (Rotterdam), recorded at (T051), 2024-01 –
                                #     2024-07 in the pool; "Mixed at Studio Sol, Marseille 2023 March" keeps its area; "Recorded in Berlin" an area

python3 t_notes_companies.py    # Discogs notes: places, ℗ / © and publishers named in the notes
                                #   discnotes: 3.30.8: Discogs notes of "Sacred Ceremonies" (three CDs) – each date with the tracks of its disc under
                                #     Performance, the places of the notes (not when "Companies, etc." lists them; another role joins its
                                #     entry), as a text: the place line recognized, "Including a 52 p. booklet." left out
                                #   pcline: 3.30.9: "© & ℗ TUM Records Oy 2021" from the Discogs notes – both roles, MusicBrainz's TUM Records Oy and
                                #     TUM Records suggested; Discogs lists © already: only ℗ joins its entry; a text: ℗ alone, © alone, both
                                #   publishers: 3.31.0: "[Publishers & Rights Societies] • FlizmoMusic-BMI : tracks 2, 4 …" in the Discogs notes – the tracks
                                #     onto Discogs's publishers as suggestions (also "4WordSeaMusic" = "Fourwordseamusic"), one not listed an
                                #     entry, BMI once as rights society; [3.31.5] the publisher Tomas Fujiwara a role of the person
                                #     (one entry, one column, S044); MB suggestions written apart ("Four Word Sea Music"), the society
                                #     first; as a text with "Published by X (ASCAP)" and "BIEM/GEMA" – there Tomas Fujiwara gets the
                                #     MB artist and "Create artist …" (S048)
                                #     [3.31.6] the tracks of the notes set, ⓘ at the row
                                #   personpub: 3.31.5: a publisher's row in its entry, on Works; Release → label–release "published", out of
                                #     the works matrix; compact view Works → Skip → Release → Works; "Published By – Jane Roe": the MB artist
                                #     first, the label of the type Publisher too, not the other one, only "Create artist …"; chosen → artist column;
                                #     "Ghost Pub" (no MB artist of that name): "Create artist …" and "Create label …"
                                #   placesearch: 3.31.2: places from the notes looked up in the first part of their area (West Orange) or by name alone
                                #     (Turtle Tone Studio in Manhattan, similar); "Recorded November 7, 8, 2016, at Loft Köln." – the period
                                #     2016-11-07 – 08, "Loft" in Cologne (alias Köln) for "Loft Köln", the entry's area "(Köln)"

python3 t_notes_dates.py        # Discogs notes: dates and track groups found in the notes ([3.32.0] choose, trackpool, reldate without
                                #   D022 – harness.RULES_OFF –, as they are about periods and "choose"; datewords with D022: the month)
                                #   datewords: 3.28.5: "19 & 20. 01. 2009", "20. 01. 2009", "1973 October 19", issue years left out, the group only from
                                #     the date's sentence, "mixed and mastered" → Mix and Mastering (Node and the date matrix)
                                #   facets: 3.28.6: "C1 to D" (side D one track) and the other ranges of "Facets" as dated track groups in the matrix,
                                #     "in live concert" → "live" for the tracks of that sentence only, no places from the notes
                                #   choose: separate days ("June 16 & 19"): both days and the period in the pool, "Choose" in the matrix
                                #   trackpool: dates for some tracks: suggestions in the matrix, Apply splits rows, applying again, several days
                                #   reldate: date matrix "Release level" (3.10.0): applied (recordings March, release June), switching the level
                                #     takes the matching date, a date typed by hand stays, the mark stored with the matrix
                                #   lcdmenu: 3.32.7: ▾ at the month D022 placed – single days (a cell each; Apply: a row per day), the period
                                #     (one cell; opening ▾ adds nothing to the pool), the month

python3 t_dates_matrix.py       # Dates & tracks: the date matrix, dragging dates and track groups, the pools
                                #   matrix: date matrix by hand: drag & drop, grip + "place here", editor, auto apply, stamp, after reload
                                #   dragdates: pool dates dragged onto rows / works matrix, dates joined into periods, pools loaded again, "Cover Art"
                                #   pools: "Dates & tracks" folds (remembered), clear all track groups / dates (also other releases)
                                #   poolsmx: 3.30.3: date pool and track pool fold on their own (folded bar and open block, remembered); the scroll
                                #     bars of the works matrix (above it; at the bottom while its lower edge is out of view), moving together
                                #   tracksdrop: track groups dragged onto rows (Shift adds, release level moves), track pool kept when folded,
                                #     works matrix cells that cannot take a date, work credits checked on the works (release page)
                                #   poolsopen: 3.32.1: "Dates & tracks" (and a folded date pool) open after an import whose suggestions wait for
                                #     "Apply" – for that import, the remembered state stays; "Tracks:" on the line of "Name:" in the form
                                #   titledates: 3.31.7: dates in the titles of the tracks (D023): off by default; on → pool, track groups, Performance
                                #     suggestions, stored "+D023"; off → gone; on and "Apply" → the row split by date
                                #   dmgoto: 3.32.8: "To the date matrix" in the message of dates placed – "Dates & tracks" folded by hand opens,
                                #     the matrix in view and lit up, the folding stays stored
                                #   workgroups: 3.35.6 (item 145b): the works of index tracks as track groups (suggestions), one on a date of the
                                #     matrix, the box of the track pool off / on (the date leaves and comes back), the setting off / on, a new
                                #     import ticks the box again, the setting stored

python3 t_works_matrix.py       # Works matrix: track groups and notes, columns, dates of cells, attributes, publishers
                                #   mxdrop: track lists from the Discogs notes as track groups and set ([3.31.6] with ⓘ; before suggestions), generous names;
                                #     track groups dropped onto a column head (Shift adds), a role, an attribute of the works matrix
                                #   matrixcols: "Directed By" asked, works matrix columns taken out / back, column dates for MB's dateless relationships
                                #   fill: dates added to MB's dateless relationships from the works matrix (edit, ×, edit note),
                                #     status marks of credits on works that were new in the editor (found through the recording)
                                #   wattrs: works matrix attributes as short forms (ac co de in ka li me pa): "li" preselected only on new links,
                                #     "li?" offered on the existing one, open/closed rows, "Attributes for all", "spell out", staging;
                                #     "Music And Lyrics By" → writer, "Song" preselected (R098, S020)
                                #   pub: publishers ticked only where a writer has them as personal publisher
                                #   remember (3.36.4, 146): with ⚙ Settings → Cache on, the choices of the works matrix after the page is
                                #     loaded again: an attribute set on a link, a new work planned, a column taken out (and brought back:
                                #     its rows no longer skipped), a column date, the type of new works

python3 t_works_more.py         # Works: the works of the artists, skipping the works matrix, comments of live recordings
                                #   artistworks: works of the artists (3.15.0): a release artist's work, a performer's cover, no duplicate with the
                                #     writers' search, the order, read once per session, 2,500 recordings (message after 10 s, capped at
                                #     2,000), no redraw while typing in the works matrix (takes about 3 minutes)
                                #   worksskip: the works matrix (3.18.0): fold / unfold (not kept), "Skip works matrix" (rows on "Skip", nothing of it planned,
                                #     no works level, kept across a reload, no lookups), taken again (3.36.4: the new works planned before come
                                #     back with it, nothing looked up), the question from N tracks ("Not now", later);
                                #     3.19.3: the tooltips of what is counted, the setting for the skipped rows
                                #   livecom: 3.32.9: comments of live recordings – the setting (Staging, off), the list above "Stage …": live
                                #     tracks of a Live release group, "live, 2001‐03: Iridium, New York, NY, USA" (credited as, area, date),
                                #     another comment of MB not tickable, changed by hand, unticked
                                #   livecomrun: 3.32.10: the job at staging (with the seed line in the note), "Enter edit" → once MB has the
                                #     relationships one POST to /ws/js/edit/create (type 72, the credit changed in the editor: red log, the new
                                #     credit), done; the release page enters an armed job (hand-made comment, another comment of MB in red)

python3 t_mapping.py            # Mapping: roles, questions, suggestions, mastering, special artists, fixes
                                #   rules: Mix / Recording / Engineer [Mix, Recording] / Trumpet [Pocket Trumpet] without role credit,
                                #     rule ids open "Mapping rules" at the rule, autoscroll while dragging (0.2 s, as in browsers)
                                #   v217: "Mixed By [Mixing]" (S019), "Bass Guitar" asked (Q004), "[Additonal Musicians]" (S002), "All Music By",
                                #     "©© Label 2005" (D015), ‹ › through the incomplete rows, Escape closes "Mapping rules" first, text size 50 %
                                #   v219: suggestions yellow and dashed everywhere (date and works matrix, "li?", unused pool entries from the
                                #     notes), "mixed" half filled, "waits" dotted; "Commissioned By" (person, label; without and with tracks),
                                #     "Live Recording By" → recording without credit and "live" only on new links of its tracks; staging
                                #   mastering: mastering only on the release level (3.15.1): two engineers for CD 1 / CD 2, no "Recording", no
                                #     "Release level" in the column, the track group decides which mastering row takes a date
                                #   special: special purpose artists (3.15.1): Various Artists and "[soundtrack]" are not asked for their works,
                                #     logged once; table T026 in "Mapping rules"
                                #   recheck: fixes of 3.12.1: "n lines not recognized" opens in the window; same-named works searched again when
                                #     a text's writer is assigned (found then), not without a change; a new import searches anew
                                #   engineers: 3.31.3: "Engineer [Recording Engineer]" → recording, "[Mix Engineer]" mix, "[Mastering Engineer]" mastering,
                                #     "[Assistant Engineer]" engineer with assistant – no role credit (S047)
                                #   poems: 3.31.4: "Poems By" → lyricist (a column of the works matrix, R105), "Poetry [Read By]", "Recitation"
                                #     → spoken vocals credited "poetry" / "recitation" (R106); "Poems" alone asks lyricist · liner notes · spoken
                                #     vocals (Q009, R107), each credited "poems"; the same in a pasted text ("Poems: …", "Poetry by …")
                                #   perftracks: 3.31.8: "Performer" on tracks, instruments for the release (S046): off by default; on → the
                                #     instruments on the performer tracks, no performer row (someone without an instrument keeps it); off → back;
                                #     on and loaded again → at the import already
                                #   poemlevels: 3.32.7: the type of poems follows the level – works lyricist, recordings spoken vocals, release the
                                #     question Q010 (lyricist · spoken vocals · liner notes, kept); the compact line goes works → recordings →
                                #     release → skip; "Poems" alone: Q009, then the level decides

python3 t_rules_window.py       # The window "Mapping rules": its words, in the dashboard, rule ids at rows, quick switches, ✎, export and import
                                #   rulesname: "Mapping rules" says "Discogs" only with Discogs loaded, "role" with a text (3.13.2), follows at once
                                #   rulesdock: 3.30.0: "Mapping rules" in the dashboard below its head (default), never together with ⚙ Settings,
                                #     "⧉ As window" (stored, ⚙ beside it), remembered after reloading, "in the dashboard" in Appearance,
                                #     closed by the symbol and Escape, a rule id at a row opens them at that rule
                                #   rowrules: 3.30.2: a rule id at a row opens the rules as a window (the row stays), the symbol closes it and opens
                                #     them in the dashboard, "Into the dashboard", the setting "like the symbol"; the arrow in the head of an
                                #     entry in the compact view opens / closes all its rows
                                #   quickswitch: 3.32.0 (milestone): the quick switches at the top of "Mapping rules" ([3.32.8] buttons in a box; order, on/off, the id shows the
                                #     rule, the same switch as in the list); D022 – the notes' "March 1–3, 2001" under Performance as 2001-03,
                                #     off → the period again; S045 – "Composed by X (BMI)", "Lyrics by Y / GEMA" → the societies on the release
                                #   ruleedit: 3.33.1: ✎ at role rules without code, company rules and T001/T002/T003/T038/T045/T048 ("code" at
                                #     the others); ✎ R071 – one more word and the credit "photos": test field, the row, "changed", your changes,
                                #     stored; a wrong pattern not saved; kept after reloading; ✎ T002 + "zither"; ↺ and ↺ all (asked first)
                                #   wqedit: 3.34.4: ✎ at every W and Q rule; W001 words and role credit (test field, your changes, stored);
                                #     Q002 + "resonator guitar" in the row's question at once, an empty word refused; Q003's choices removed,
                                #     moved, added (table, stored), a choice without a type refused; export; import skips a field that cannot
                                #     be changed and a wrong choice, a whole register takes over Q005 turned round; ↺ all
                                #   wqnew: 3.34.21: "＋ New rule" at the wording rules (W901: "fretless bass" → credit, first in its table, "yours") and at
                                #     the questions (Q901 "keys": keyboard · synthesizer · piano – a pasted "Key Man – keys" asks); your changes,
                                #     export (with "add"), import (Q902 new, W903 of the wrong kind skipped, W904 from a whole register), deleted
                                #   mappingio: 3.33.1: export of the whole register = the mapping file byte for byte (with a change: one line
                                #     differs), export of my changes (format, versions) and the clipboard; pasted import with a preview (new,
                                #     list, own rule, switch, skipped: unknown / code / wrong pattern / list, a conflict), "Take over", "Keep
                                #     mine"; an old rules file chosen and dropped onto the window; a whole register replacing my changes
                                #   mappingconflict: 3.33.1: a stored change whose built-in value changed with an update – the log warns, "changed
                                #     · ⚠", built-in value then and now, Keep mine / Discard; a rule no longer in the file; reset with own rules

python3 t_ui_head.py            # Dashboard: its head, the head of an entry, "Add entry manually", messages, the page bar, ▲ ▼
                                #   head: the head in one line (3.26.0; 3.27.2: ☰ first, "open in background" purple): symbols with names (words only when wide), no language / place / switches in
                                #     the head; "Source ▾" (Escape, a click elsewhere, "Paste text …" below the head); "+ Supplement"; the language
                                #     asked after the installation (en / fr-FR preselected, OK, gone after reloading, not after an update)
                                #   entryhead: the head of an entry and the bar below the button (3.28.0): only the tag links to the source (↗), [3.32.2] the
                                #     release's spelling "B. Man*" in the head (tooltip "Discogs: Bass Man") instead of the chip "as “B. Man”",
                                #     a row credited otherwise "as “Bassman”", the credits in the compact lines; the bar: status and ⚙ only, ⚙ → the settings
                                #   manualtop: "Add entry manually" as one line above the date pool (3.18.0): tooltip, "?", in view when scrolled (window and
                                #     page), an entry added from there is shown
                                #   msgs: messages (3.27.3): ✕ on each, "▾ n messages" folds them, a new error unfolds, a fresh import shows them again
                                #   bar: language before opening (3.27.1: the question after the installation, then the settings), fold at the
                                #     bottom, date pool kept when folded, common month/year, horns, producer
                                #   jump: ▲ ▼ in the status bar jump to the top and bottom of the dashboard, in the window and in the page (3.14.1)
                                #   compacthint: 3.34.23: the arrow at ☰ (nothing stored) below the symbol, the pointer goes through; gone after
                                #     switching (stored, also on a new page); back after "Reset all settings", ✕, back with ↺ of Appearance;
                                #     the compact view stored before – no arrow
                                #   keys: 3.36.3: ⌨ in the head shows all keyboard shortcuts (groups, the keys of this computer, as a Mac ⌥ ⌃ ⌘ ↩),
                                #     Esc and ✕ close them, the focus back on ⌨

python3 t_ui_settings.py        # Settings: tabs, the menu, the bridge to ⚙, settings without an import, reset, the update notice
                                #   settabs: the settings as tabs (3.25.0; 3.27.2: the heading folds them in): only the gear folds them out and in, eight tabs (3.29.2: nine, "Appearance" after General; General chosen), ↓ / End /
                                #     Home, the tab remembered after reloading ("Texts" with the web links and "Mapping rules"), the ⓘ in the head
                                #     opens "ⓘ Connections" (ten rows, Harmony with its home page), "↺ Reset all settings …" below the tabs shows
                                #     the question in the settings ("Cancel" back to the tab), no "↺ Defaults" in the head, narrow: tabs in a row
                                #   settings: the menu "Settings" (3.16.0): topics, shared switches both ways, values in steps, a topic's "↺",
                                #     the works of the artists kept across a reload (IndexedDB), clearing them, switched off
                                #     3.25.0: the topics as tabs, one shown at a time
                                #   bridge: 3.30.4: ⚙ pressed with a bridge to the settings (and the rules symbol to the docked rules), the content of
                                #     every tab joined by the tab (100 % and 90 %), the bridge scrolled away and closed; 3.34.3: the bridge exact in
                                #     fractions of a pixel, over the head's lower line; the content as high as it can be (ⓘ Connections at the top, its
                                #     tab in the middle; a short one just low enough), its corner square only where the tab joins at the top
                                #   settingsscroll: 3.34.3: ⓘ Connections and "Dates & tracks" open, scrolled down and up in small steps – never back
                                #     down, up to the top; scrolling does not touch the content's margin (until 3.34.2 it jumped back 278px)
                                #   ui305: 3.30.5: ⚙ below "Import credits …" before any import – only the settings ("Source pages"), no import, the
                                #     message "Start import" starts it; the field "Tracks:" of a track group (ranges, ticks, unknown tracks,
                                #     Enter saves, editing shows the tracks); German "Quellseiten"
                                #   reset: "↺ Reset all settings …" (⚙ Settings, 3.25.0; before "↺ Defaults" in the head): settings, own
                                #     rules, pools of all releases, cover box on Discogs
                                #   notice: update notice (milestones, closed, language) and the one-time resets of stored data (generations 2 to 4, also companion;
                                #     generation 4 clears the list of created works too)
                                #   cache: 3.36.0 (item 146, milestone): ⚙ Settings → Cache – remembering off by default (changes gone after a
                                #     reload, nothing stored), on (stored at once, rows and pool back after a reload, the log), the source changed
                                #     (changes of gone or changed lines left out, the message), the number 0 (off) and 50, another release
                                #     forgotten with 1, "Forget all remembered releases …" with the space shown
                                #   cache2: 3.36.1: a row removed with ✕ stays removed, a pasted text keeps its own state (the Discogs one stays),
                                #     switched on in a tab opened while off: the message "Load the page again", nothing written over, back after it
                                #   logdiag: 3.36.2: "Start diagnosis" only with ⚙ General "Diagnosis in the log" (off by default); a running one
                                #     stops when switched off; ↺ of General

python3 t_ui_view.py            # View: the compact view, folding, the colours of the levels, small fixes, the suggestions, rows
                                #   compact: the compact view (3.27.0, milestone; 3.27.2: full by default, ☰ in the head switches and remembers compact):
                                #     a line per row, marks in colour, fields hidden,
                                #     open / "▴ compact", a track group and a pool date dropped onto the line, the question answered ([3.32.3] in the
                                #     line itself, its possibilities to click), a skipped
                                #     row grey with ✕ (back after reloading), "Full" remembered and in the settings, the jump to an incomplete row
                                #   fold: 3.29.3: the arrow next to "Artist credit for all roles" – one entry folded to compact lines in the full
                                #     view (a line opens its row, ▸ back, full again after the next import), its open rows closed in the
                                #     compact view
                                #   levels: 3.29.2: the colours of the levels (full rows and compact line), the level of the compact line by a click
                                #     (Recording → Release with the June date of the matrix → Skip → Recording with the March dates), the tab
                                #     "Appearance" (text size, place, view, colours: own colour, off, ↺)
                                #   ui301: 3.30.1: the bar below the messages covers nothing, tooltips of "on mouse-over / on click", the level of
                                #     a compact line stays in place on Skip, "only works" apart and in the colour of works, in the page no
                                #     wider than the window (inside a 2400 px page)
                                #   suggstack: suggestions as a block below the red mark (3.15.2, 3.15.3: side by side, wrapping): eight artists of one name, 5 shown + "+ 3 more",
                                #     explanations as tooltips
                                #   rows: remove a row (and undo), removal after staging, "only works"
                                #   clineask: 3.32.3: a type question in the compact line ("Directed By": four buttons), chosen there, the row closed
                                #   kindcolors: 3.32.4: the heads of the works matrix in the colours of their kinds (Writer W artist, Pub Co label,
                                #     with the tag), ⚙ Settings → Appearance: own artist colour (entry and head follow, stored), off → grey, ↺

python3 t_ui_place.py           # Window or page, the log, staying in place after a form, texts that name the source
                                #   inline: dashboard in the page instead of a window: placement, sticky dates/footer, switch, reset
                                #   logplace: log next to the edit note: right / left (width and height), above (height kept), too narrow → above,
                                #     edit note drawn anew, remembered after reloading, "↺ Defaults" → window
                                #   keepplace: after "Create artist …" the dashboard stays at the entry (window and page, without scroll anchoring)
                                #   srctexts: texts that named Discogs say "the source" with another source (3.16.2)

python3 t_entries.py            # Entries as a matrix (E4, Block AE, from 3.34.29; the default of the script)
                                #   join: 3.34.29: the instruments and voices of an entry joined when staged (one relationship per recording,
                                #     date, artist credit and additional / guest / solo; "solo" apart) – 20 instead of 33; a role credit typed
                                #     after staging stages the joins anew (taken out, staged again, nothing twice; [3.35.0] also a row taken
                                #     out of a join); legacy stages the same
                                #     instruments apart; ⚙ Staging "Join …", ⚙ Appearance "Entries: Matrix | Legacy"
                                #   matrix: 3.34.30: an entry as blocks of lines with the events as columns (Multi Man: "3 instruments", ①, written
                                #     “Drums”), ▸ rows, add. / guest / solo, more events than shared (fold, One row each, ＋ Event ▾, a tick into ①),
                                #     a line out of ① (grey), One row each, what is staged after all of it
                                #   dates: 3.34.31: a pool date onto a line (it moves into the date's event; ↶), onto the head of an event, typed
                                #     into the heads (a new pool date; the pool's own date changed), with ⇧ onto a block (both, "only … · keep both"),
                                #     what is staged (lead and background vocals with the date joined, background vocals without); [3.35.0] a date onto
                                #     a block with lines behind "▸ n more"
                                #   compact: 3.35.0 (milestone): compact as a matrix – a line per event with the roles as chips, a chip dragged onto
                                #     another event (moved), ✕ (taken out), by role, ▸ / ▾ in the head, a chip clicked (full matrix at its line),
                                #     ⚙ Staging "An entry, compact, at first: by role", the summary "a relationship per instrument would be 33"
                                #   restage: 3.35.0: "One row each" and "Join in one block" after staging (joined ↔ singles in the editor), a joined
                                #     relationship changed in the editor itself stays (its rows not staged again), the others anew
                                #   order: 3.35.3 (AE-2): ⠿ drags a line before or after another of its block (the mark above / below), Alt+↑,
                                #     not onto another entry's line, no ⠿ in a block of one line, the compact view follows, staged as before, a new
                                #     import in the order of the source
                                #   evhead: 3.35.4 (AE-3): ▸ opens an event below its block – a track added (focus kept), the last track stays,
                                #     all (two events one), a date typed / none / of the pool, Release and back (Mastered By stays, the note, ok),
                                #     ✕, staged together with the date
                                #   remember: 3.36.0: a remembered release – the order dragged, an opened event's tracks, one row each: back after the
                                #     page is loaded again, staged the same
                                #   companies: 3.35.5 (AE-4): a place ("Recorded At") and a label (℗) as matrices, publishing on works keeps its
                                #     rows, compact, staged the same as legacy, a date typed into the place's event

python3 t_sources.py            # Sources: the adapter, several linked releases, supplementing, the tracks of a source
                                #   adapter: source adapter (3.0.0): no Discogs data outside the adapter; the neutral release in Node (headings,
                                #     index tracks, "A1 to A3", grouping, S018); through the adapter in the dashboard: aliases, series and
                                #     parent label, forms for artist / label / series / work, edit notes, live from the format, US dates,
                                #     Discogs tab, release picker; update from 2.19.1 without reset (PARTS=C: only the dashboard part)
                                #   links: several linked releases of one source (3.24.0): the dialog counts each (one cannot be read), the one with the
                                #     most data bold and preselected, all in background tabs, "Import" (remembered, loaded at once next time),
                                #     another one by hand without remembering, "Cancel" (the message as before)
                                #   supp: a second source supplements the loaded one (3.5.0): only on request, the list "Supplements from …"
                                #     (new role, new entries with suggestions, "differs", not recognized), marks DG BC / BC ≠, take over
                                #     selected, edit note ("Also from", added only, differs); "Delete stored import …"; the old script
                                #     on the page (stays out / warns); G: supplement with a typed Bandcamp URL (3.8.0)
                                #   tracksfit: tracks compared with MusicBrainz (3.24.1): in the dialog a release with a bonus track yellow, the one with the
                                #     most data among the fitting ones preselected ("most data with matching tracks"); the yellow message after
                                #     the import (number, titles with the differing ones); small differences ("(Remastered)", "The …") fit
                                #   indextracks: 3.35.1: index tracks of Discogs whose parts are tracks of their own (Discogs 3139201: 13 tracks,
                                #     not 3; the work's credit on its parts, "C1 to D, F2"), parts of one track ("C1a", "C1b") one track "C1",
                                #     "AA"/"AB", in the dashboard a credit on "B1" on the third recording, no message about the tracks

python3 t_sources_bandcamp.py   # Bandcamp: as a source, the "about" text, leaving it out, liner notes, label pages, track pages, credits of the "about" text
                                #   bandcamp: Bandcamp as a source (3.3.0, 3.3.1): physical media → Discogs first, Bandcamp chosen in the picker (album and
                                #     track pages through GM_xmlhttpRequest, band linked by its page, choice kept after a reload, edit note),
                                #     digital media → Bandcamp first, order changed in the list, the Bandcamp menu (track pages off,
                                #     "Test page"), a band not credited so on the release only suggested; the spelling compared
                                #     with the release's artist credit, not with the MB artist's name (rule 4); the spelling check line
                                #   about: Bandcamp "about" text (3.7.0): "recorded at Loft in Cologne, june 16/17 2018" → place Loft (Cologne),
                                #     places suggested only in that area, the period in the date pool; "Studio Nord, Bremen" in the credits;
                                #     "mixed at home in Oslo", "at the same time", "at last" give no entry (3.13.1)
                                #   aboutoff: "Leave out the about text" (3.16.1): place and dates of the about text out and back, with the changes,
                                #     kept across a reload, reset by "Delete stored import"
                                #   linernotes: liner notes in Bandcamp's about text (3.17.2): the three places of the name, five sentences over several
                                #     paragraphs, cases without (4 sentences, "Special Thanks" …), entry as suggestion, pool name, jump, left out,
                                #     3.17.6: the date as a suggestion at the row, ✓ takes it
                                #   labelpage: an album on a label's Bandcamp page (3.22.1): no link for the artist, searched by name (the release's artist
                                #     first, "release artist"), the hint with the page and MB's label ("a label of this release ✓"), the source
                                #     line, the log; the account's name from "data-band" / "og:site_name" (Node); Discogs: a person without MB
                                #     link gets same-named suggestions
                                #   bctrack: a Bandcamp track page as the release (3.28.1 / companion 1.8.4): loaded from the link, its credits once,
                                #     the tab "connected" with marks; a track of an album via "Other source", "Load the release there"; Test page;
                                #     the text "… Bandcamp track pages too", long settings texts wrap
                                #   aboutcredits: 3.32.6: the credits of the "about" text (S049; j4vaman "Ephemeral"): composer (S050, "Muisc"),
                                #     cover art and the liner notes "-j4vavaman" above the credit line, all "from the about text"; S049 off
                                #     → only the liner notes; the release artist j4vaman first suggestion for j4vavaman; ⚙ → Texts switch

python3 t_media_choice.py       # Media: a release with several media, loading media in the editor, the media choice
                                #   media: release with two media: "CD2, tracks 1–3", "Disc 1", medium headings, track group per medium
                                #   mediaload: the media dialog (3.20.0, 3.21.1): load the chosen media in the editor in the background – MB's editor built
                                #     as MusicBrainz builds it (a.expand-medium#disc<n>, "Expand all mediums", "Load all tracks..."), a medium
                                #     without a tracklist named, the works question there ("Not now", "Skip works matrix"), media 1 and 3 only,
                                #     tracks and relationships the release lookup leaves out read from /ws/js/tracks
                                #   mediasel: media choice before the import (three media): all = as before, media 2-3 without the release level,
                                #     "Choose media …", remembered choice preselected, unknown media, cancel / Escape

python3 t_start.py              # Starting: from the release editor, from Harmony, the source in the navigation
                                #   afteredit: start from the release editor (3.19.0; 3.23.0: the button "Enter edit & import credits" instead of the tick): only
                                #     on "Edit note" with a Discogs/Bandcamp link, right after "Enter edit", orange; "Enter edit" stays plain; the
                                #     button and Ctrl+Alt+Enter → relationship editor with the dashboard, an error, "Add release" with a Bandcamp
                                #     link typed in (German, loaded at once), the setting off, other release pages untouched
                                #   harmony: Harmony (3.19.1): a release editor seeded by Harmony (a note, no button, "Enter edit" → Harmony's Release
                                #     Actions), there "Edit relationships with Credits Importer" below "Add cover art", the link opens the dashboard
                                #     and loads the Bandcamp album; no release, "discogs=", another tool's redirect; 3.19.2 (3.23.0: the button
                                #     instead of the tick): a background tab (opened once by Harmony's page), an error, the settings
                                #   navlink: the source in the navigation bar (3.17.4): link, "open in background", "Load the release there"; ↗ at suggestions
                                #   mappingload: 3.33.0: the mapping file from the manager; fetched from GitHub (kept, one reload); missing → the
                                #     message with "Update script"
                                #   languagesload: 3.34.0: the languages file from the manager (German); fetched from GitHub (kept, one reload);
                                #     English chosen → fetched quietly, German at once from ⚙; missing → message, English, the log warns

python3 t_coverart.py           # Text from cover art (beta, 3.34.1, item E3): ⚙ Settings → Beta, the Cover Art Archive, Tesseract.js (stand-in)
                                #   ocrsetting: the tab "Beta" before "ⓘ Connections", the switch off by default, "Source ▾" gets the item only
                                #     while it is on (stored); the connections X013, X014
                                #   ocrpick: the images of the release – Back, Booklet, Tray ticked, Front and Medium not ("rarely has credits"),
                                #     English (German too with a German dashboard), the count on the button, Escape; a release without images
                                #   ocrrun: Tesseract.js loaded once, one worker; the 500 px image read ×3 with a warning; ℗, dashes and empty lines
                                #     corrected and named; a word read with little certainty selects itself; edited and imported as a text
                                #   ocrerror: the library cannot be loaded – the message in the window, the log
                                #   ocrown: 3.34.5: "All images" (half, all, none); own images – files chosen (a text file left out), pasted,
                                #     dropped, removed; an address (Enter; wrong and twice refused); a site that refuses named; the own images
                                #     read (a small one enlarged) and imported with their names in the source; no CAA images: only own ones
                                #   ocrpdf: 3.34.6: a PDF with the real pdf.js (a local copy, PDFJS_DIR): pages as cards (own text / an image),
                                #     a frame around one column, read – own text in order and by frame, a scanned page recognized –, the
                                #     source; a PDF by its address; a broken one named
                                #   ocrdiscogs: 3.34.7: "Load Discogs images" (nothing fetched before), the release's page: its images once at
                                #     600 px, not another release's; a Discogs address typed (twice refused); read ×3, the source
                                #   ocrstart: 3.34.8: "… from cover art" only with the beta, joined to "Import credits …"; the dashboard without the
                                #     import (nothing of Discogs), the message, the window; the read text the source; beta off: gone
                                #   ocrpeek: 3.34.9: tiles alike with the whole image; the larger view after a pause (1200 px image, its
                                #     proportions, 480 px), gone on leaving; an own narrow file larger; in the frames step too
                                #   ocrload: 3.34.10: previews counted; the ticked images loaded ahead two at a time (held requests), the third
                                #     waiting; unticked: out of the queue, one loading ahead stopped; "loaded"; loading ahead off (stored):
                                #     nothing ahead, the frames step shows its own loading
                                #   ocrlocate: 3.34.12: an uncertain word clicked – selected, marked, zoomed in on (again: its next place);
                                #     the caret in a line marks it (brought into sight), ⤢ keeps the mark, a line replaced: none; a Tray read
                                #     ×3 – its place on the canvas; a PDF page's own text – the place of its line on the page drawn
                                #   ocrzoom: 3.34.11: two frames on the Back, the Booklet whole – wider window, a part per frame beside its text
                                #     (the image there); +, −, Ctrl + wheel, double click, drag, ⤢; a part's text changed and imported
                                #   ocrremember: 3.34.17: two frames on the Back, the Booklet turned and whole – stored; opened again:
                                #     "Back 2 frames", read as left; the 1200 px copy: the frames fit (×0.8); forgotten with "Delete stored
                                #     import …" and the reset of Beta
                                #   ocrmore: 3.34.16: 30 images – 12 shown (12 previews), "Load 12 more", "All shown (24)"; 12 small images
                                #     beside the frames, then 24; Auto-select with 30 booklet pages – all shown; a PDF of 15 pages – 12
                                #   ocrorigin: 3.34.22: Back and Tray read and imported – "From the cover art · Back" / "… · Tray" at the rows, ⓘ shows
                                #     the crop of the line (JPEG, at most 640 × 160) and hides it again; a line changed: no ⓘ; another text: nothing
                                #   ocrentry: 3.34.24: Bob Lee on the Back and the Tray – the head of his entry "From the cover art · Back, Tray", ⓘ the
                                #     crops of both lines, hidden again; an entry of a pasted text afterwards: nothing
                                #   ocrauto: 3.34.15: nothing ticked at first; "Auto-select" ticks Back, Booklet, Tray; off – its ticks go,
                                #     those set by hand stay; switched on in ⚙ Settings with the window open – ticked at once, and when
                                #     opened again; 30 booklet pages, loading ahead on: 2 load, 22 wait, 6 not ahead
                                #   (from 3.34.15 beta_on also switches "Auto-select" on – as before, the images with credits are ticked)
                                #   ocrwindow: 3.34.14: the window the same size in every step (its foot bar in place, "Next image →" greyed
                                #     out at the end); the image beside the frames takes the room; smaller at its corner (remembered);
                                #     moved by its head, opened again at the same place; [3.34.18] in front after a click into the dashboard,
                                #     the rules (as a window) and the log
                                #     [3.34.23] ⚙ → Beta "Keep … in front" off: the dashboard comes in front with a click; on again
                                #   ocrtextfit: 3.34.14: "Reads best: text on a plain, even background …" while choosing and beside the
                                #     frames; a text field as high as its text, growing; many uncertain words – a yellow box names the part
                                #   (from 3.34.14 the cases drag frames in the pixels of the image: drag_img – the view follows the window)
                                #   ocrthumbs: 3.34.13: the small images beside the frames clicked (and Enter) – each shown, a frame drawn
                                #     on the Tray kept; read: Back and Booklet whole, the Tray's frame ×3
                                #   ocrframes: 3.34.2: frames by default – two drawn, one changed at a corner, one moved; an image turned and read
                                #     whole, one left out; the sizes read (frames in their order); back to the images, the frames stay

python3 t_companion_discogs.py  # Companion on Discogs: marks switched by a click, the check on the release page, marks on track lines
                                #   keepmarks: a click on a Discogs mark switches its credit, the pointer shows its row, "Click switches" off, "Keep marks" (3.17.5)
                                #   relcheck: the release page keeps its check (1.8.2): ✓ after "Enter edit", a check without answer keeps ✓ and is
                                #     retried, a background page's beat counts 75 s ([Companion 1.9.1] ten minutes: one 5 min old keeps the marks)
                                #   trackmarks: a status mark on each Discogs track line, checked per track on the release page

python3 t_companion_bandcamp.py # Companion on Bandcamp: the Bandcamp view, credits switched off, dates and track groups underlined
                                #   bcview: the Bandcamp view of the companion (3.17.0 / 1.8.0): "no Bandcamp tab" → open in background, another page →
                                #     "Load the release there", marks before each part of a line (none in the about text, shortened texts
                                #     opened), mark → row, jumps (part of a line, sentence of the about text, track both ways), track
                                #     pages (link, loaded, own marks), ● after staging and ✓ on the release page, menu, old companion
                                #   bcoff: credits switched off on Bandcamp (3.17.1; 3.17.5: a click on the mark, the pointer shows the row): off → "Skip" with a note and greyed, a
                                #     group of marks, on again with its level, kept across a reload, a level chosen, "Delete stored import"
                                #   textmarks: used dates and track groups underlined at the source (3.28.3 / companion 1.9.0): Discogs notes (matrix,
                                #     a row, not the pool), status off/on, Bandcamp credits (a year also in "released …") and "about";
                                #     two "Vocals [...]" lines of one artist

python3 t_static.py             # Without a browser: the texts of the script, the list of connections, the mapping file, the languages file
                                #   i18n: the texts (3.27.1; 3.34.0: English from the script, de / es / fr from the languages file): every key
                                #     the code names in English, no left-over translations, no foreign
                                #     placeholders, French no-break spaces, the English fallback (Node); reports the missing translations
                                #     per language (LIST=1: all keys) – not an error
                                #   connections: the connections (3.25.0, Node): every address of @match / @connect and of the code belongs to an entry of
                                #     CONNECTIONS, the ids are unique, every entry has its texts in English (3.27.1; before: four languages)
                                #   mappingfile: 3.33.0: mb-vibecode-credits-importer-mapping.json – format, version, its lists against `MAP.X` of the
                                #     script, patterns compile, @resource / @grant / @connect, read in Node
                                #   languagesfile: 3.34.0: mb-vibecode-credits-importer-languages.json – format, version, de / es / fr, its layout
                                #     (that of i18n_add.py), only English in the script, @resource languages, read in Node (German, else English)
```

### Former test → file and case (3.31.1)

| Former test | File | Case |
|---|---|---|
| t_about.py | t_sources_bandcamp.py | about |
| t_aboutoff.py | t_sources_bandcamp.py | aboutoff |
| t_adapter.py | t_sources.py | adapter |
| t_afteredit.py | t_start.py | afteredit |
| t_ar.py | t_ar.py | – (a file of its own) |
| t_areas.py | t_text_places.py | areas |
| t_artistworks.py | t_works_more.py | artistworks |
| t_artwork.py | t_artwork.py | – (a file of its own) |
| t_bandcamp.py | t_sources_bandcamp.py | bandcamp |
| t_bar.py | t_ui_head.py | bar |
| t_basic.py | t_basic.py | – (a file of its own) |
| t_bcoff.py | t_companion_bandcamp.py | bcoff |
| t_bctrack.py | t_sources_bandcamp.py | bctrack |
| t_bcview.py | t_companion_bandcamp.py | bcview |
| t_bridge.py | t_ui_settings.py | bridge |
| t_choose.py | t_notes_dates.py | choose |
| t_compact.py | t_ui_view.py | compact |
| t_connections.py | t_static.py | connections |
| t_datewords.py | t_notes_dates.py | datewords |
| t_discnotes.py | t_notes_companies.py | discnotes |
| t_distrib.py | t_text_basics.py | distrib |
| t_dragdates.py | t_dates_matrix.py | dragdates |
| t_entryhead.py | t_ui_head.py | entryhead |
| t_facets.py | t_notes_dates.py | facets |
| t_fill.py | t_works_matrix.py | fill |
| t_focus.py | t_focus.py | – (a file of its own) |
| t_fold.py | t_ui_view.py | fold |
| t_foreign.py | t_text_languages.py | foreign |
| t_freetext.py | t_text_basics.py | freetext |
| t_harmony.py | t_start.py | harmony |
| t_head.py | t_ui_head.py | head |
| t_i18n.py | t_static.py | i18n |
| t_initials.py | t_text_places.py | initials |
| t_inline.py | t_ui_place.py | inline |
| t_jump.py | t_ui_head.py | jump |
| t_keepmarks.py | t_companion_discogs.py | keepmarks |
| t_keepplace.py | t_ui_place.py | keepplace |
| t_labelpage.py | t_sources_bandcamp.py | labelpage |
| t_levels.py | t_ui_view.py | levels |
| t_linernotes.py | t_sources_bandcamp.py | linernotes |
| t_links.py | t_sources.py | links |
| t_logplace.py | t_ui_place.py | logplace |
| t_manualtop.py | t_ui_head.py | manualtop |
| t_mastering.py | t_mapping.py | mastering |
| t_matrix.py | t_dates_matrix.py | matrix |
| t_matrixcols.py | t_works_matrix.py | matrixcols |
| t_media.py | t_media_choice.py | media |
| t_mediaload.py | t_media_choice.py | mediaload |
| t_mediasel.py | t_media_choice.py | mediasel |
| t_medium.py | t_text_places.py | medium |
| t_members.py | t_text_languages.py | members |
| t_msgs.py | t_ui_head.py | msgs |
| t_mxdrop.py | t_works_matrix.py | mxdrop |
| t_names.py | t_text_basics.py | names |
| t_navlink.py | t_start.py | navlink |
| t_nordic.py | t_text_languages.py | nordic |
| t_notice.py | t_ui_settings.py | notice |
| t_pcline.py | t_notes_companies.py | pcline |
| t_pools.py | t_dates_matrix.py | pools |
| t_poolsmx.py | t_dates_matrix.py | poolsmx |
| t_prose.py | t_text_languages.py | prose |
| t_pub.py | t_works_matrix.py | pub |
| t_publishers.py | t_notes_companies.py | publishers |
| t_recheck.py | t_mapping.py | recheck |
| t_register.py | t_register.py | – (a file of its own) |
| t_relcheck.py | t_companion_discogs.py | relcheck |
| t_reldate.py | t_notes_dates.py | reldate |
| t_release.py | t_release.py | – (a file of its own) |
| t_reset.py | t_ui_settings.py | reset |
| t_rowrules.py | t_rules_window.py | rowrules |
| t_rows.py | t_ui_view.py | rows |
| t_rules.py | t_mapping.py | rules |
| t_rulesdock.py | t_rules_window.py | rulesdock |
| t_rulesname.py | t_rules_window.py | rulesname |
| t_settabs.py | t_ui_settings.py | settabs |
| t_settings.py | t_ui_settings.py | settings |
| t_sounds.py | t_text_languages.py | sounds |
| t_special.py | t_mapping.py | special |
| t_srctexts.py | t_ui_place.py | srctexts |
| t_suggstack.py | t_ui_view.py | suggstack |
| t_supp.py | t_sources.py | supp |
| t_textcorpus.py | t_textcorpus.py | – (a file of its own) |
| t_textcredit.py | t_text_basics.py | textcredit |
| t_textmarks.py | t_companion_bandcamp.py | textmarks |
| t_textrules.py | t_text_basics.py | textrules |
| t_trackmarks.py | t_companion_discogs.py | trackmarks |
| t_trackpool.py | t_notes_dates.py | trackpool |
| t_tracksdrop.py | t_dates_matrix.py | tracksdrop |
| t_tracksfit.py | t_sources.py | tracksfit |
| t_ui301.py | t_ui_view.py | ui301 |
| t_ui305.py | t_ui_settings.py | ui305 |
| t_v217.py | t_mapping.py | v217 |
| t_v219.py | t_mapping.py | v219 |
| t_v3222.py | t_text_places.py | v3222 |
| t_wattrs.py | t_works_matrix.py | wattrs |
| t_worksskip.py | t_works_more.py | worksskip |

```

**Text corpus (3.21.0):** `text_corpus.json` collects credits lines as they are written on releases. Each new case of
the text recognition goes there; `UPDATE=1 python3 t_textcorpus.py` writes the readings anew – check the changed lines
(the test prints each one that differs before) and say so in the code changes. `harness.WEB_URLS` (url → (gid, name)) gives
artists MusicBrainz has with a web profile, for `/ws/2/url`.

**Golden test of the register:** `register_corpus.json` was made once from Import 3.10.0 and stays as it is (more roles
can be added; then write the golden file anew). `register_golden.json` holds the results. A refactoring of the register
must leave `t_register.py` OK without `UPDATE=1`; a change of a rule that is meant shows exactly the roles it changes –
check them, then write the file anew and say so in the code changes.

The rows of the dashboard rearrange with its width (3.9.0) and a pool or matrix date is a chip: tests that type into a
row's date fields use `common_rows.date_field(row, f)`, `rows_of` reads the chip's `data-date`. A button the floating
log window may cover in the 1500 × 1000 test window ("Apply" of the date matrix) is clicked by script
(`locator.evaluate('b => b.click()')`).

MusicBrainz's media (3.21.1): `split_media` gives each medium an id (4500 + position) and its number of tracks;
`harness.WS_DROP_TRACKS` (positions whose tracks the release lookup leaves out) and `harness.WS_NO_RELS` (positions
whose recordings come without relationships) let a test do what MusicBrainz does with large releases; `/ws/js/tracks/<id>`
answers like MB's own pages of tracks (`JS_TRACKS_PAGE` tracks a page, calls in `JS_TRACKS_CALLS`).

`harness.DG_API` gives a test its own answers of the Discogs API (path → JSON, `None`: 404), e.g.
`H.DG_API['/artists/3030'] = {...}` for an artist with members or aliases.

Bandcamp: `harness.BC_PAGES` maps a page URL to its HTML; `harness.bc_page(data)` builds a page with `data` in its
`data-tralbum` attribute (`current.title/credits/about`, `trackinfo[].track_num/title/title_link`, `artist`).
`harness.bc_html(data, url, about_cut=None, credits_cut=None)` (3.17.0) builds a page like Bandcamp's own for the
companion: the track table (album pages), the "about" and "credits" texts with `<br>` between the lines (the credits after
"released …"), Bandcamp's shortening of long texts after so many characters ("..." and a hidden rest with "more"), and the
data in `data-tralbum`; `harness.open_bandcamp(ctx, url)` opens it as a Bandcamp tab with the companion (only in the top
frame, as `@noframes`), also after the tab loads another page.
`harness.BC_ARTISTS` maps a band URL (`https://band.bandcamp.com/`) to an MB artist `(mbid, name)` for the URL lookup;
`harness.WS_FAIL = {'release': n}` (3.17.3) lets the next n lookups of the release answer 503 (MusicBrainz busy).
`harness.RELEASE_AC` is the release's artist credit, `[(mbid, MB name, name as credited, join phrase)]`.
The release editor (3.19.0): `/release/<REL>/edit` and `/release/add` serve `harness.mb_release_editor_page(kind)` – tabs, the
external links editor with the links of `harness.EDITOR_LINKS[kind]`, "Enter edit" (`#enter-edit`, shown with `__tab('edit-note')`)
and `MB.releaseEditor.submissionInProgress`; a click on "Enter edit" goes to the release page (`window.__gid`, default the
mock release; `window.__fail = true`: an error instead). `harness.open_mb_any(ctx, url)` opens a MusicBrainz tab that gets the
main script on every page, also after the page navigated by itself. `harness.EDITOR_REDIRECT[kind]` (3.19.1) seeds a
`redirect_uri`: "Enter edit" then goes there with `release_mbid` as MusicBrainz does; Harmony's `/release/actions` is served
as a small page like Harmony's own; `open_mb_any(…, all_tabs=True)` puts the script into every tab of the context (a tab
opened by a click on a link still gets none – open its address in a new page instead).
`open_mb_any` records the tabs the script opens with `GM_openInTab` in `window.__gmTabs` (3.19.2).
`open_mb_edit(ctx, gm_xhr=True)` adds `harness.GM_XHR_SHIM`, a `GM_xmlhttpRequest` that fetches through the mock and
records the URLs in `window.__gmXhr` (without it the script falls back to `fetch`). The MusicBrainz search
(`/ws/2/artist|label|place?query=…`) finds the artists and companies of the mock whose name (or alias) has all the words
of the query – case and accents do not count (`harness.fold`) – and, for `area:(…)`, only places in that area;
`harness.MB_SEARCH[kind]` adds more entries to search (`{'id', 'name', 'aliases': [{'name'}], 'area': {'name'}}`),
`harness.PLACE_AREAS` gives the mock's own places an area (`{'Abbey Road Studios': 'London'}`).
The work search (`/ws/2/work?query=…`) answers from `harness.WORK_SEARCH` (`{'id', 'title', 'aliases', 'relations'}`; a work is
found when one of its artists is named in the query as `arid:`); `harness.WORK_QUERIES` records the queries.
The browse requests for the works of an artist (3.15.0) answer from `harness.ARTIST_WORKS` (`work?artist=…`: artist gid →
`[{'id', 'title', 'type', 'aliases'}]`) and `harness.ARTIST_RECORDINGS` (`recording?artist=…`: artist gid →
`[{'title', 'work': {'id', 'title'} or None}]`, or a number: that many recordings without works, a large catalogue);
`harness.BROWSES` records them as `(kind, artist, offset)` – they are not in `WORK_QUERIES`. Every import browses each
artist with an MB entry twice in the background (one request a second; in the tests every 25 ms, `MB_GAP`), so a test that counts MusicBrainz requests
should count only its own kind.

With several media (`harness.MEDIA = [2, 1, 1]` …) the dashboard asks for the media before the import:
`harness.open_dashboard(pg)` answers "All" with the release level (the import as before),
`open_dashboard(pg, media={'text': '2-3', 'release': False})` another choice, `media=False` leaves the question open.
`harness.open_reset(pg)` (3.25.0) opens ⚙ Settings and there "↺ Reset all settings …" (until 3.24 "↺ Defaults" in the head).
`harness.src_menu(pg, act=None)` (3.26.0) opens the menu "Source ▾" of the head and clicks `[data-act=act]` in it (pasting a text,
another source, a linked source, the order of the sources, Bandcamp, "Leave out the about text", "Delete stored import …");
`harness.open_supp(pg)` opens the bar "Supplement with"; `harness.toggle_place(pg)` switches window ⇄ page in the page bar;
`harness.open_settings(pg, tab=None)` opens ⚙ Settings (the language is only there). `harness.nav_switch(pg, attr)` (3.28.0) clicks a switch of the
navigation (`data-dg-artwork`, `data-click-toggle` …) in ⚙ Settings → Discogs and Bandcamp view – the bar below the button has none any more. `harness.open_mb_edit(ctx, …, view='full')`
(3.27.0) sets the view of the entries to "Full" (`dci-view`, with the storage generation) before the script starts – the tests were
written for the full rows; `view=None` keeps the default (compact, the case `compact` of `t_ui_view.py`); `open_mb_any` sets "Full" too. Every test starts as a first installation, so
the page bar shows the question of the language (`#dci-langask`); it does not stand in the way of the tests.

Relationship types of the mock are made with `harness.lt(id, gid, name, type0, type1, attrs, dates, deprecated)`; as on
MusicBrainz, artist–recording "mastering" is deprecated (the dashboard leaves it out) and artist–release "mastering" (42)
exists (3.15.1).

`harness.WORK_RELS_DIRECT_ONLY = True` leaves the submitted relationships of the work out of the release lookup, as
while its link to the recording is still an open edit; `/ws/2/work/<id>` still has them (`harness.WORK_LOOKUPS`
records these lookups). A test can put relationships that are already in MusicBrainz into the mock editor's state as
`existingRels`; an update of one of them moves it to `added`, as MusicBrainz shows it as changed.

Chromium is started with `harness.LAUNCH_ARGS` (web security off), so the pages may call the local storage server.
Texts are added with `python3 tools/i18n_add.py <anchor key> <file.json>`; the JSON holds `{lang: {key: text}}` – from 3.27.1
English alone (`{"en": {…}}`) is enough, the other languages follow in a translation round (the case `i18n` of `t_static.py` lists what is missing).
From 3.34.0 English goes into the script and German, Spanish and French into `mb-vibecode-credits-importer-languages.json` (one text a line).
