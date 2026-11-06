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
  tools/mb_link_types.py              [3.38.10] writes smoke/mb_link_types.json from a checkout of metabrainz/musicbrainz-server
                                      (po/relationships.pot and t/sql/initial.sql are enough: git sparse-checkout)
  smoke/harness.py                    mock MusicBrainz, Discogs and Bandcamp, shared GM storage, helpers; [3.38.10] link phrases: the
                                      type's name, instrument and vocal with MusicBrainz's phrase ("{additional} {guest} {solo}
                                      {instrument:%|instrument}": rows named "bass", "guest saxophone"; the bare form the type's name)
                                      [Companion 1.10.1] the Discogs page writes "Phonographic Copyright ℗" as the real one (the
                                      data "(p)")
                                      [3.40.12] the type "recorded in" (area – recording)
  smoke/zooid.py                      scenario after Discogs release 38282688 (10 tracks, two sessions, two studios)
  smoke/common_rows.py                helpers for the date tests: rows (tracks, date), matrix cells, staging, drag with the mouse
                                      (the target is scrolled to the middle first: near the edges the dashboard scrolls while dragging);
                                      [3.34.29] ENTRIES_VIEW: the entries as before ('legacy') for every file but t_entries.py – the matrix
                                      (E4, the script's default) is tested there; [3.34.30] with the generation of the stored data;
                                      [3.36.0] REMEMBER: True – ⚙ Settings → Cache "Remember … per release" switched on before the
                                      script starts (the files written before expect the stores of a release kept); False in
                                      t_ui_settings.py cache and t_entries.py order (the script's default: off)
                                #   statsdur: 3.65.0 (Z-DUR, S095): the time of creating an entry in the record (cr); the times without / with it,
                                #     remembered; no switch in Global nor with S095 off
                                #   globalgroups: 3.65.0 (Z-GLB): Global's head line (ⓘ, fold / open all), its groups, "+ n more"
                                #   statscompact: 3.61.0 (Z-STL, Z-RDU2): the head in one line, the flat bar, the groups, cards and groups folded
                                #     (remembered), fold / open all, "+ n more", the bars, the streaks in one line, Recording | Release
                                      [3.40.9] DM_FOLD: False – "Fold bar after Apply" stored off before the script starts (the files
                                      written before work on in the open bar after "Apply"); True in t_dates_matrix.py foldapply
                                      date_field(row, f): a date field of a row – opens a date chip (3.9.0) first
  smoke/caserun.py                    [3.31.1] runs the cases of a topic file: one shared browser, what a case changes in the
                                      harness set back after it, one result per case and one for the file
                                      [3.40.8] launch_own(**kw): a browser of its own (other launch options, e.g. overlay
                                      scroll bars); the case closes it
  smoke/t_*.py                        tests: topic files with cases (case_<name>, each the former t_<name>.py), and seven
                                      files of their own (golden tests, comparisons with older logs); each ends with
                                      "Ergebnis: OK/FEHLER"; [3.38.10] a row's role as the source wrote it is `data-raw` of
                                      `.dci-drole` (its text is MusicBrainz's name)
  smoke/register_corpus.json          frozen input of the register's golden test (t_register.py)
  smoke/register_golden.json          its expected results (written with UPDATE=1)
  smoke/mb_link_types.json            [3.38.10] MusicBrainz's relationship types: names and link phrases (all 698), entity types and
                                      parents (427: those of the server's test database; newer ones without), attributes, the commit
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
                                # texts only after the import of the release is complete – before, their end depended on the timing;
                                # 3.38.10: D) every role's name as MusicBrainz shows it – the first of its types MusicBrainz has between an
                                # artist and its level, the link phrase with flags and instrument or voice from mb_link_types.json, golden
                                # "phrases": "Engineer [Recording]" → recording engineer, "Co-producer" → co-producer)
python3 t_text_lists.py         # Texts from Bandcamp's credits of 2026-11 (Intentions, Throats), in Node (3.48.0 –)
                                #   tcpread: 3.60.0 (Z-TCP, Node): "2 Bonu (Oliver Lake)" and the like – each name writes its track
                                #   tcpread2: 3.60.0 (review): brackets that are no composers (a place, "Hidden Track", "Traditional", the band's members)
                                #   namesroles: 3.59.0 (Z-TBY, Node): a group "The …", "Special guests:" a heading, two credits from one line
                                #   namesroles2: 3.59.0 (review): "except" titles, "plays …", two names in a line, a make, "Volume 2:" – as before
                                #   hyphen, ignorelines, linernotes: 3.48.0 (Z-HYP, Z-IGN, Z-LIN); review: false positives (colon, "by" lines, credits among notes, "Björk (v)", publishers)
                                #   rolesplit, roles, places, oldmarks, exceptread, exceptworks: 3.49.0 (Z-RTL, Z-ROL, Z-RPB, S069, Z-EXC – dashboard: covers, arrangement, quote)
                                #   exceptlayouts, rolesplit2, exceptworks2: review of 3.49.0 (other layouts of the blocks, the parts' marks; nothing
                                #   staged twice or with itself, no search without a writer, a failed search, a later import, a supplement)
                                #   prose, trackartists: 3.50.0 (Z-PRO "with guests …", "SHelley"; Z-TAR the tracks of the track artists, S078)
                                #   placecredit: 3.51.0 (Z-PCR, the area after a comma)
                                #   prose2, trackartists2: review of 3.50.0 (credits before "with", no place or make as a name, IJ names;
                                #   other roles, tracks changed by hand, the edit note)
python3 t_textcorpus.py         # text recognition, part 1 (3.21.0): the corpus text_corpus.json through the text adapter (golden), then the
                                # Maya Recordings credits in the dashboard – four sentences in one line, "P + ©", thanks and strings left out
                                # on purpose, 1988 in the pool (3.37.9: the artwork's year; before: none); "Logo by … instagram.com/…" (design, "logo", the profile, a suggestion via
                                # it), "Create artist …" with the profile (not Linktree), "Text" answered with lyricist → works matrix
                                # 3.21.3: links hidden at first, shown with the setting, Spotify only for "Create artist …", "Create place …"
                                # with a studio's profile
                                # 3.42.3: "Gondola" (as on the page and with "○") and "Black Zenith" in the corpus (Z-GON, Z-BZ)
                                # 3.43.0 (full review, P1 – S074 – S077): 24 lines – a track list after each name, "except" lines,
                                #   a second "by" clause, role lists, several "Name (roles)", names before a dash split, a release artist
                                #   never split, places with their area in brackets and a second place
                                # 3.43.5 (counter-review): 7 lines – name-and-place pairs, a sentence after "and", "Tears for Fears", a studio with a role
                                #   word, role lines below "A & B – vocals", a "by" in brackets, a bracket after a name
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
                                #   guests: 3.37.2 (151 – 153): "(P) 1998 loudsprecher (c) 1998 loudsprecher" both roles; credits split at » « ("Cover-Photo"
                                #     = cover photo, cover design); "Special Guest: M. Osswald on Sax and Piano" – guest on both, "Guest: Jane Roe"
                                #     performer guest, "featuring:" without guest, "NAME on X and Y"
                                #   typonote: 3.37.13 (164): "Sxaophone" → saxophone a typo (no role credit, note, log), turned round → "sxaophone"
                                #     and back; "Taischigoto" → taishōgoto credited "taischigoto"; ✕ empties a row's role credit (stays empty when
                                #     the instrument is set again) and a matrix line's (staged without credit). instrguess / unknownask: chimes "chaims"
                                #   stacked: 3.38.7 (167, S058, S059): "Torben SNEKKESTAD / SAXOPHONES & TRUMPET / Agusti FERNANDEZ / PIANO / Barry
                                #     GUY / DOUBLE BASS" – three entries in normal case; the instruments above; "Jane Roe / PIANO / John Doe" not
                                #     clear: the note, the log, ⇅ (John Doe), another text (Jane Roe again); one line with capitals; the Discogs notes;
                                #     3.38.12 (F-5): ⇅ in the dashboard – no new import, Max Mix put on Skip stays; "ABBA – piano" → Abba (S060)
                                #   withline: 3.38.17 (181, S061): "With Apple Logic, Sequential PX, flutes …" – the release artist's instruments,
                                #     "objects" asked, software left out; "with Oliver Lake" guest, "Jane Roe on saxophone" guest saxophone;
                                #     3.39.2 (186, 187): "lap steel" lap steel guitar (T001), "objects" asked "as which one?" – percussion
                                #     “objects” (T058) first; percussion chosen: credited "objects", no note of a spelling; T058 changed as
                                #     a file would ("Objects", with other instruments): other instruments once
                                #   cloudpond: 3.38.18 (182 – 184): "Ambisonic recordings by RR 2022-2025 …" field recordist with the period,
                                #     "Pacific coast" the area Pacific Coast (3.39.2, 188, T059); RR = Robert Rich (initials, credited "RR"), "Recorded Mixed and Mastered";
                                #     3.39.7 (K-8, K-11): "JR" – Jane Roe clicked, the liner notes hers credited "JR"; "R.R." with its dot
                                #     "Cover © X" artwork "cover", "Photos © X" photography "photo", the permission left out; "JR" of two names
                                #   booklets: 3.39.8 (Z-1, S067, S068): two booklet pages read with Tesseract 5.3 – "VIOLIN / Anna Berg / Clara Stein /
                                #     Ben Holt" stacked and "Violins: …" in one line give the same entries; the title (the release's artist) left out
                                #   initialsmemo: 3.39.8 (K-8, review): "JR" → Jane Roe chosen, remembered: after a reload and the same text at once
                                #   stackflip: 3.38.12 (F-5, after the review): a clear and an unclear credit of one role – ⇅ and back, ⇅ and
                                #     imported again (remembered), the Discogs notes with a credit Discogs lists (no second row)
                                #   hostask: 3.41.8 (Q-cn): "Host" / "Hosted By" asked (Q012): spoken vocals "host", misc "host", skip the role;
                                #     "Presenter" stays spoken vocals
                                #   fieldpool: 3.42.2 (Z-FRD): the periods of field recordings in the date pool, one a line, named after the kind
                                #   ytroles: 3.41.7 (Z-AM, Z-CAM, Q-co): "Audio & Mixing Engineer" → audio, mix; "Mixed & Mastered By" → mix,
                                #     mastering; "Cameras" misc "cameras", "Camera Operator", "Cinematographer" each their own; "Editor" misc "editor"

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
                                #   gondola: 3.42.3 (Z-GON, S069 – S072, Q013): Ross McReynolds "Gondola" – "• 1, 8" the tracks, lines of roles below a
                                #     name his, en dash, "All songs mixed by" (no "All songs"), "Skinny Elephant recording" mixed at, website and "all
                                #     over the place" left out, plurals/sampling/pedal steel/Wurlitzer; the same with "○" before each line; horns →
                                #     horn "horns", brass chosen
                                #   blackzenith: 3.42.3 (Z-BZ, S073): "With Black Zenith, Stellarium turns toward …" no guest (pasted and as
                                #     Bandcamp's "about" text); the release's and a track's title no person

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
                                #   unawords: 3.42.4 (Z-UNA): words of lines not recognized clicked (⇧) – a place mixed at (with an own rule of texts,
                                #     in the rules window), a place on the tracks of the line, a person (a role needed), a series; read again: the rule
                                #   kindcycle: 3.42.5 (Z-ETC): "Label ↻" of an entry not linked – label → place → artist (an area alone: no button),
                                #     one search after the clicks (counted), what was found before again without a search, the label chosen
                                #   unaremember, kindrace, ownrulekind: 3.42.8 (review): words given an entry come back with "Remember changes …",
                                #     a hand copy of a source's role stays; a late search keeps its kind; an own rule of texts keeps its kind

python3 t_notes_companies.py    # Discogs notes: places, ℗ / © and publishers named in the notes
                                #   dedications: 3.67.0 (Z-DED, S097): "Dedicated to" / "in memory of" in the notes – release group, the work of a
                                #     track the sentence names; "to my mother" left out; ⇄ tribute to; the release's title a tribute; off
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
                                #   facets: 3.36.7 (150, S053): Discogs 3139201 "Facets" (3 LPs, 13 tracks): "A1 to B2 recorded … in live concert at
                                #     Goldsmith's College, London" – Discogs's place for the whole release only on A1–B2 (ⓘ), Heiman Recording
                                #     Studios from the notes on C1–D and E1–F2; after "Apply" one date each (1981 / 1979 / 1980); "li" on A2's new
                                #     link, its live comment; "1.1 to 1.2 recorded … at …" in a pasted text
                                #   notescredits: 3.37.0 (E5, S054): the Discogs notes read in full – new names entries, a new role of a Discogs
                                #     name a row of its entry, "From the Discogs notes" with ⓘ; nothing twice (producer – its two lines merged –, bass, a
                                #     studio's name; "Executive producer" a role of its own); Discogs's
                                #     guitar for the whole release gets the notes' tracks; Source ▾ "Leave out the credits of the notes" and back;
                                #     ⚙ Texts: the rule off and on
                                #   linkedsugg: 3.37.1 (E5a): a name whose artist MusicBrainz links to this release (mix on the release) – that
                                #     artist first among the suggestions, solid green and bold, "in this release: …", before a namesake; the log; a label of
                                #     the same name not offered the artist
                                #   festival: 3.37.8: "Recorded June, 26, 1993 at the Western Front Lodge, … during the … International Jazz
                                #     Festival Vancouver" – the day, the place without "the"; the hint, the event of 1993 offered (not 1994),
                                #     nothing set; its button: an event entry in plum; ⚙ Appearance "Event"; a pasted festival without a
                                #     date: the hint alone, "Royal Festival Hall" none
                                #   pcperson: 3.37.10: ℗ / © of the Discogs label "Martin Davidson" (unknown to MB) – the producer Martin Davidson
                                #     takes them (hint, "As the label instead" gives them back); linked in MB only: the entry is that artist;
                                #     neither: artist and label of that name offered, each named

python3 t_notes_dates.py        # Discogs notes: dates and track groups found in the notes ([3.32.0] choose, trackpool, reldate without
                                #   catno: 3.44.1 (Z-CAT): "Music & Arts website states CD-4853(1)" in the notes gives no track group, "Pub Co (1, 3)" still does
                                #   review43: 3.43.3 (full review P4): a pool entry edited, "update n rows?" declined – the rows their own ("0 rows")
                                #   D022 – harness.RULES_OFF –, as they are about periods and "choose"; datewords with D022: the month)
                                #   datewords: 3.28.5: "19 & 20. 01. 2009", "20. 01. 2009", "1973 October 19", issue years left out, the group only from
                                #     the date's sentence, "mixed and mastered" → Mix and Mastering (Node and the date matrix)
                                #   facets: 3.28.6: "C1 to D" (side D one track) and the other ranges of "Facets" as dated track groups in the matrix,
                                #     "in live concert" → "live" for the tracks of that sentence only; 3.36.7: the places of the notes on their
                                #     tracks (before: no places from the notes)
                                #   choose: separate days ("June 16 & 19"): both days and the period in the pool, "Choose" in the matrix
                                #   trackpool: dates for some tracks: suggestions in the matrix, Apply splits rows, applying again, several days
                                #   reldate: date matrix "Release level" (3.10.0): applied (recordings March, release June), switching the level
                                #     takes the matching date, a date typed by hand stays, the mark stored with the matrix
                                #   trackside: 3.37.7: "Track B recorded on 12 November 1985 in Tokyo, Zojoji Hall" (A1, A2, A3, B) – the date on
                                #     track B only, Zojoji Hall (Tokyo) from the notes on B; listed by Discogs: its entry with B; a pasted
                                #     "Tracks A2 & B:" on tracks 2 and 4
                                #   assistnotes: 3.40.12 (Z-AP): the three lines of "Assist" – the area Hiroshima, the places Meguro Fukushi
                                #     Center (Tokyo) and Zojoji Hall (Tokyo), no area Tokyo; "Apply": each its date, the area too; a place
                                #     Discogs lists without a word of places ("Shinjuku Pit Inn"): that place, no area Tokyo
                                #   artwork: 3.37.9: "Cover Painting: “View at Nice” (1992)" – the column Artwork, applied to Mary Vernon's
                                #     illustration (R078), not to the photographer; "Photography By [Live Photos]": the concert's date suggested, ✓
                                #   lcdmenu: 3.32.7: ▾ at the month D022 placed – single days (a cell each; Apply: a row per day), the period
                                #     (one cell; opening ▾ adds nothing to the pool), the month
                                #   periodsplit: 3.37.12: "19 & 20. 01. 2009" – the period chosen keeps a ▾ (2 single days, the month) → two
                                #     cells; a period of the pool: "⇢ 2 days" adds its days (log)

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
                                #   foldapply: 3.40.9 (Z-PF): "Fold bar after Apply" below the matrix and in ⚙ (on); "Apply" folds (stored,
                                #     focus on "▼ show", log); off: stays open; with "apply automatically": open while the pointer is in the
                                #     bar, folded when it leaves; by keyboard, a field outside focused: folded; ↺ of the topic: on again;
                                #     3.40.11 (review): left without a change, "apply automatically" off with a change waiting, a change from
                                #     ⚙ – open; stored only when off; 3.40.13 (Z-PF2): nothing stored by "Apply", loaded again: open; "▲ fold"
                                #     by hand, loaded again: folded
                                #   poolside: 3.42.1 (Z-TP): date pool and track pool side by side at 1500 px, below each other at 600 px or when
                                #     too long (Zooid)

python3 t_works_matrix.py       # Works matrix: track groups and notes, columns, dates of cells, attributes, publishers
                                #   review43: 3.43.3 (full review P4/P5): the list of created works matched by the recording (index refreshed), an
                                #     entry of a recording not read kept, not planned
                                #   mxdrop: track lists from the Discogs notes as track groups and set ([3.31.6] with ⓘ; before suggestions), generous names;
                                #     [3.37.0] the strings arranger of the notes an entry (E5), nothing of a track list a name;
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
                                #   statgaps: 3.41.15 (review, Z-STV): "co" on a link MusicBrainz has, staged, "Enter edit" – the record holds it as
                                #     supplemented with "attrs", gaps.attrs 1
                                #   nwa: 3.57.0 (Z-NWA, S083): an existing work (linked in MusicBrainz, or found and chosen) – its cells locked and
                                #     struck through, only the link of the recording staged; a new work as before; S083 off: as before
                                #     (review) a work made with the form in this browser stays open; cwr runs with S083 off
                                #   addcolumn: 3.68.0 (Z-MXO, Z-ACO, Z-ACR, Z-MRC, S098–S100): the list of "＋ Add a column" in groups (with a personal
                                #     publisher), its menu above the head of the tracks, the role by the rules, "Another role"; off
                                #   creditskip: 3.64.0 (Z-WSK, S093): "Skip credits" beside a work – its work credits left out, the
                                #     recording credits stay; "↺ Take credits"; off: no button
                                #   publevel: 3.64.0 (Z-PUB, S094): "Work | Release" for a label's publishing row in its column; off
                                #     (the harness switches S083 off by default – RULES_OFF; nwa and cwr set the rules themselves)
                                #   cwr: 3.56.0 (Z-CWR, S082): no writer beside composer / lyricist / librettist of the same person on a work
                                #     (MusicBrainz's composer, "Music By", "Lyrics By"); S082 off: as before
                                #     (review) a picked work of the search with the composer in MusicBrainz; the form of a new work without writer
                                #   wmx: 3.52.0 (Z-WMX): the head in one line (chips, ⓘ, "Skip works" in the middle, defaults · search · new works · ⋯),
                                #     column heads (the name whole with its tooltip, ⚠, ▾ with « and ✕), "All artists credited as: ↺ …", "＋ New ▾",
                                #     "＋ attribute", the hourglass chip, "＋ Add a column" by MBID (a long name smaller; a place refused)

python3 t_works_more.py         # Works: the works of the artists, skipping the works matrix, comments of live recordings
                                #   livedate: 3.62.0 (Z-PDT, Z-LVD, S089): "Performed in … on …" under Performance, the live comment without it before the matrix is applied, the hint naming it; off
                                #   wts: 3.52.0 (Z-WTS): the suggestion of a work type and a language from the works of the artists (yellow, "Accept");
                                #     not accepted: the new works without either; accepted: Song in English; in Node suggestFromWorks (majorities, < 3 works)
                                #   artistworks: works of the artists (3.15.0): a release artist's work, a performer's cover, no duplicate with the
                                #     writers' search, the order, read once per session, 2,500 recordings (message after 10 s, capped at
                                #     2,000), no redraw while typing in the works matrix (takes about 3 minutes)
                                #   worksskip: the works matrix (3.18.0): fold / unfold (not kept), "Skip works matrix" (rows on "Skip", nothing of it planned,
                                #     no works level, kept across a reload, no lookups), taken again (3.36.4: the new works planned before come
                                #     back with it, nothing looked up), the question from N tracks ("Not now", later);
                                #     3.19.3: the tooltips of what is counted, the setting for the skipped rows
                                #   livecom: 3.32.9: comments of live recordings – the setting (Staging, off; 3.37.3 the offer), the list above "Stage …": live
                                #     tracks of a Live release group, "live, 2001‐03: Iridium, New York, NY, USA" (credited as, area, date),
                                #     another comment of MB not tickable, changed by hand, unticked; 3.38.3: tracks 2–3 one group line, the heading
                                #   livecomrun: 3.32.10: the job at staging (with the seed line in the note), "Enter edit" → once MB has the
                                #     relationships one POST to /ws/js/edit/create (type 72, the credit changed in the editor: red log, the new
                                #     credit), done; the release page enters an armed job (hand-made comment, another comment of MB in red);
                                #     (3.66.0, Z-LCP, S096) the box: how many, each comment with its tracks, "Not entered:" by reason
                                #   livetracks: 3.66.0 (Z-LCP, Node): the tracks of a comment in short ("2–4, 6", "1.1–1.3, 2.1")
                                #   liveoffer: 3.37.3: the setting off – the offer above "Stage …" (tracks, the first proposal, the tooltip naming
                                #     the setting), ✓ the list for the release (setting not stored, the job at staging), loaded again: the offer
                                #     back, ✕ hides it (log, the job gone); 3.38.3: "Tracks 2–4"
                                #   livegroup: 3.38.3: two media – "Live recordings: CD 2, track 1.2", one group line of three (▸ the tracks, its
                                #     text and tick for all), the heading at the bottom right (also folded, the same place), the list ≤ a third;
                                #     3.38.13: "track 1.2, CD 2" (F-2, by positions – the track's index, not its number), the heading purple (F-1)
                                #   liveall: 3.40.13 (Z-LC): "All" above the list – ticked, mixed (a track of the group unticked), all on and off;
                                #     in livecom without the track MB has another comment for
                                #   workpick: 3.38.15 (180): "n works ▾" in the track's line, the list hidden; opened below the line, closed by a
                                #     click elsewhere and Esc (focus back), one at a time; "1 work ▾" not set; Link plans the work
                                #   coverworks: 3.38.16 (179): works of the track's composer by a similar title ("By Monk", "(… cover)"), a full
                                #     name of the title looked up, a surname only of an artist of the release, the log; "co?" and its click; Node
                                #     (3.43.1, full review P2) D: a track of a medium read from /ws/js/tracks keeps its artists – no "cover" by itself
                                #     3.39.9 (K-9): no "co?" when Monk is a member of the release's band (or the release's artist a member of his), the
                                #     pianist in MusicBrainz (of the recording or of the release) or the track's artist; one lookup, the composer's;
                                #     3.40.1 (Z-AF): "is person" – the release's artist Monk's other name, the other name a member of the release's
                                #     band (both looked up), the control without a band ("co?"); 3.40.3: two performance names of one person
                                #     3.40.17 (Z-CV): Monk with only writing credits – "cover" set by itself (yellow "co", staged), a click: "co?";
                                #     E: classical, or Monk with Liner Notes too – "co?" only
                                #   suitedata: 3.41.0 (Z-SU): in Node – Discogs headings and sub-tracks as parts, " / " parts, the kinds of headings
                                #     (T061, a recording, a name), the suites offered (heading, index, the release's title, none)
                                #   suiteask: 3.41.1 (Z-SU): "Trisect" – the yellow question, ✓ Yes: the parts as new works (part k of n), staged in
                                #     their order without a type; ⚙ "Suite, Part" and ↺; undo, ✕ No, another name; 3.52.0: the question a row of the
                                #     matrix above its tracks, the tracks indented
                                #   suiteparts: 3.41.2: the suite "Trisect" (type Suite) with "parts" (movement) to 7 parts in their order, entity0,
                                #     no recording with it; the preview; nothing after ↺; 3.41.6 (Z-SUW): no "parts" before the suite is created in
                                #     MB's form (name, type 6, the writer of all tracks), then from the work of MB
                                #   medley: 3.41.3: "Alpha / Beta" – ✕ No, the offer "Split into 2 works (medley)"; split: Beta found in MB; staged with
                                #     "medley" in the order of the title; "↺ one work"; 3.41.4: no suite asked (one of four), Beta offered, then linked
                                #   suiteadd: 3.41.11 (Z-SUM): "＋ Suite …" – the yellow box (tracks from – to, name), without a name an error,
                                #     "Trisect" for tracks 2–4 accepted as a found suite (parts, create button, log); ↺ undo: gone; Cancel
                                #   subtracks: 3.41.12 (Z-SUB): an index "Suite X" with 3a, 3b on two MB tracks – four tracks (log, no message),
                                #     Bass Man on track 4, the suite offered for tracks 3–4; Node: subTrackSplit by titles, by count, not
                                #   suiterestage: 3.41.4 (review): staged, undone, accepted again / named anew: one link per part, no "parts" to a
                                #     new work without its recording; 3.41.6: the suite created first, then found in MB ("Link “Trisect”")

python3 t_mapping.py            # Mapping: roles, questions, suggestions, mastering, special artists, fixes
                                #   dedphrases: 3.67.0 (Z-DED, Node): the phrases of dedications and tributes, names joined, a title
                                #   coverdetail: 3.62.0 (Z-CVA, S090, Node): "Cover [Cover Art]" → "cover art", the exceptions of COVER_DETAIL, the dashboard's role credit
                                #   photoname: 3.63.0 (Z-PHN, S091): "Photography By [Bass Man]" credited "Bass Man"; off
                                #   perfhints: 3.62.0 (Z-PDT review, Node): performance hints, not premieres or rights lines
                                #   dbr: 3.58.0 (Z-DBR, S084): "Piano [Acoustic]" → piano credited "acoustic piano" (marked; a click: "acoustic"),
                                #     "Piano [Acoustic Piano]" without a word twice, "Vocals [Backing]" → "backing vocals", Moog / two details kept; S084 off
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
                                #   mbnames: 3.38.10 (177): MusicBrainz's names – the phrases of all types of the test page from mb_link_types.json:
                                #     rows ("recording engineer", "guest saxophone", "remastering"), tooltip "from Discogs: …", types, "additional"
                                #     ticked, compact line, preview, entry matrix and chip, works matrix ("additional composer", menu
                                #     "sub-publisher"), the log "Staged: …"
                                #   assistants: 3.39.4 (K-1, K-2, S065): "Assistant Engineer" engineer + assistant, "Asst. Mixing Engineer", "Co-Arranger",
                                #     "Arranged By [Co]" arranger + co; "Assistant Arranger" edit note only (row note, preview); "Assistant
                                #     Photographer" credited "assistant photographer"
                                #   voices: 3.39.5 (K-3 – K-5): "Countertenor" countertenor vocals, "Vocals [Tenor]"; "Liner Notes [Translation]"
                                #     with translator; "Creative Direction" on the release group, for one track on its recording, no edit note
                                #   companyperson: 3.39.6 (K-6, S066): "Mixed At" / "Recorded At" / "Mastered At" at a person – what the person did, the
                                #     note, no place; "Pressed By", "Distributed By" left out (Skip, note); "Licensed From" licensor
                                #   listkeys: 3.39.6 (K-13): T001 changed with "Lap Steel2" (as an imported file writes it) is found (Node)
                                #   toys: 3.39.7 (T058): "Toys" asks percussion · electronic instruments · other instruments “toys”; "Found Objects"
                                #   oldfile: 3.39.2 (review): a mapping file without T058 / T059 and changes of your own (Node, files copied):
                                #     the script loads, "Pacific coast" not recognized; T059 changed by hand → the region again;
                                #     3.40.5 (Z-RG): a file whose T059 is a list of words (3.40.4) – the region read

python3 t_rules_window.py       # The window "Mapping rules": its words, in the dashboard, rule ids at rows, quick switches, ✎, export and import
                                #   review43: 3.43.2 (full review P3): levels through a quick switch; an artist created in the form still the
                                #     entry's after a reload ("Remember changes …"); one "part of" row of a Discogs series after a reload
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
                                #     (3.43.4, full review P5) C: an own rule with a level the editor never allows ("foo") is not imported
                                #     differs), export of my changes (format, versions) and the clipboard; pasted import with a preview (new,
                                #     list, own rule, switch, skipped: unknown / code / wrong pattern / list, a conflict), "Take over", "Keep
                                #     mine"; an old rules file chosen and dropped onto the window; a whole register replacing my changes
                                #   mappingconflict: 3.33.1: a stored change whose built-in value changed with an update – the log warns, "changed
                                #     · ⚠", built-in value then and now, Keep mine / Discard; a rule no longer in the file; reset with own rules
                                #   regionlist: 3.40.8 (review, Z-RG): T059 – a file of changes with words ("Gulf Coast" alone, "West Coast" keeps
                                #     United States), ✎ T059 "Lake Region" and "Delta =" saved without an area, its own hint; a whole register
                                #     of 3.40.4 (words): no change

python3 t_ui_head.py            # Dashboard: its head, the head of an entry, "Add entry manually", messages, the page bar, ▲ ▼
                                #   head: the head in one line (3.26.0; 3.27.2: ☰ first, "open in background" purple; 3.40.6, Z-HB: in groups – ☰ A− A+ ⤢ |
                                #     Mapping rules, Log | Statistics, ⌨, ⚙ | ✕): symbols with names (words only when wide), no language / place / switches in
                                #     the head; "Source ▾" (Escape, a click elsewhere, "Paste text …" below the head); "+ Supplement"; the language
                                #     asked after the installation (en / fr-FR preselected, OK, gone after reloading, not after an update);
                                #     3.36.5: no ⓘ among the symbols
                                #   entryhead: the head of an entry and the bar below the button (3.28.0): only the tag links to the source (↗), [3.32.2] the
                                #     release's spelling "B. Man*" in the head (tooltip "Discogs: Bass Man") instead of the chip "as “B. Man”",
                                #     a row credited otherwise "as “Bassman”", the credits in the compact lines; the bar: status and ⚙ only, ⚙ → the settings
                                #     3.37.11: the chip "artist credit in MusicBrainz: “B. Man” (the Discogs spelling *)", the * explained
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
                                #   anvcredit: 3.37.11: "Kenneth Ansell*" (Ken Ansell) in the matrix view – the chip "artist credit in MusicBrainz:
                                #     “Kenneth Ansell” (the Discogs spelling *)", the field, the log; emptied: no chip
                                #   spellings: 3.38.11 (175, 176): Oliver Lake "Lake*" only in the writing credits – head "Oliver Lake", chip
                                #     "as “Lake” (+1)" / "for writer", field empty; "C. Allen*" in all roles; matrix column "Credited as", a line
                                #     per spelling, compact "as “O. Lake”", lines joined; a place: "Credited as for all roles", set for all
                                #   capsnames: 3.38.12 (F-4, S060): Discogs names in capitals in normal case ("TORBEN SNEKKESTAD", "DJ SHADOW"),
                                #     ABBA linked to "ABBA" as MusicBrainz writes it, "LAKE" → credited "Lake", the log; "↺ in capitals" and back;
                                #     "LAKE" with ↺, "DOOM" linked to "MF DOOM" credited "DOOM", a credit typed by hand stays;
                                #     3.38.14 (Q-a, Q-b): personCase in Node – "AL DI MEOLA" → "Al di Meola", "DJ SHADOW" stays "DJ", particles
                                #   blockac: 3.40.3 (Z-AK): "Credited as" in the head of a block of several roles – "several", "Lake" + Enter (the
                                #     flutes join, the message with ↶ Undo), Undo, a line by hand keeps its own (also against the older ↶), emptied
                                #     with Enter: MusicBrainz's name, the focus back; blocks of one role: none; compact: no field, the chips' "as …"
                                #   copyname: 3.40.7 (Z-CP): ⧉ at the entry not linked, none at the linked; a click: the name in the clipboard,
                                #     ✓, ⧉ again (drawn by CSS: the head's text stays the name); a pasted text: ⧉ also at a name with a
                                #     suggestion, gone once the suggestion is chosen; 3.40.8 (review): the clipboard refuses – through a
                                #     selected text ✓; refused too: ⚠, tooltip and label
                                #   headnarrow: 3.40.8 (review, Z-HB): one line at 1500 and 600 px; at 400 px two lines, ✕ inside the dashboard
                                #   launchtools: 3.40.14 (Z-LS): Log | Statistics · ⚙ as symbols next to "Import credits …" (no companion);
                                #     Log pressed while shown; Statistics and ⚙ open the dashboard without the import (its message names what
                                #     is open, one only); "Start import"
                                #   poolbar: 3.37.15 (165, 166): a pool open for the import's suggestions folds at one click; "▲ fold" in the
                                #     head after the title, "▼ show" folded at the same x, none at the foot; folded pools with "+ New date" (form,
                                #     saved: counted) and "+ New track group"; the kept bar with both, "+ New date" opens the block, Cancel folds;
                                #     3.38.13 (178): the head the last line of the block, "▲ fold" / "▼ show" in its middle, the arrow ▲ / ▼,
                                #     the focus on the button again after a click

python3 t_ui_settings.py        # Settings: tabs, the menu, the head symbols pressed (until 3.36.4 the bridge to ⚙), settings without an import, reset, the update notice
                                #   statstime: 3.45.0 (Z-STD): pauses not counted (threshold in ⚙ Cache), work in the record; the times per source, Median | Average; review: the pause right before "Enter edit", the script's scrolling no work, the second record on a page, releases counted once, Average pooled, the field normalised
                                #   theme: 3.46.0 (Z-DM): the dark theme – as a window and in the page (Auto | Light | Dark, Auto live), the light theme unchanged, contrast ≥ 3 in the dark one, colours of their own for it, ↺; review: the dark stylesheet only when needed (written = read), white text on text colours, the tags beside the dark pickers, „Reset all“
                                #   globalstats: 3.47.0 (Z-GST): This browser | Global – the file of the workflow, once a day, "Load again", without network the copy, Reset all; review: a file with gaps, keyboard focus, a copy older than a day
                                #   darkmeaning: 3.48.0 (Z-DMY): the colours of meaning in the dark theme by hand (variant A)
                                #   statsb10: 3.53.0 (Block 10): days / weeks / months in a row, the most active weekday (relationships, "Enter edit"),
                                #     role credits and credited as, aliases, media and types, language and script, recording lengths (Median | Average),
                                #     "Show when you work" off, "Show “Global”" off (nothing loaded) – the clock fixed on 2026-06-17
                                #   statsrec: 3.53.0: what a record holds of the release (media, types, language, script, lengths) and per relationship
                                #   globalcore: 3.55.0 (Z-AGS): "Global" with the section of the core dump (artists, releases, language and
                                #     script, lengths, role credits) and "credited as"; a file without them: a line instead
                                #   statsart: 3.54.0 (Z-AST, Z-PLS): the artists of the relationships (type, gender, decade, country, town, centuries,
                                #     posthumous), labels and places used most (by MBID); the lookups in the dashboard (off: none; kept ones not again), deleted
                                #   versions: 3.51.0 (Z-VER): the versions of script, mapping file and companion in the head, ⚠ and the link when GitHub has a newer one (once a day)
                                #   settabs: the settings as tabs (3.25.0; 3.27.2: the heading folds them in): only the gear folds them out and in, eight tabs (3.29.2: nine, "Appearance" after General; General chosen), ↓ / End /
                                #     Home, the tab remembered after reloading ("Texts" with the web links and "Mapping rules"), "ⓘ Connections"
                                #     (3.36.5: through ⚙, the ⓘ in the head is gone; Harmony with its home page), "↺ Reset all settings …" below the tabs shows
                                #     the question in the settings ("Cancel" back to the tab), no "↺ Defaults" in the head, narrow: tabs in a row
                                #   settings: the menu "Settings" (3.16.0): topics, shared switches both ways, values in steps, a topic's "↺",
                                #     the works of the artists kept across a reload (IndexedDB), clearing them, switched off
                                #     3.25.0: the topics as tabs, one shown at a time
                                #   pressed (until 3.36.4 "bridge", 3.30.4 – 3.34.3): 3.36.5 (147, 149): ⚙, the rules symbol, the log and ⌨ pressed while
                                #     open (tinted), no bridge any more, A−, A+, ⤢ never pressed, no ⓘ; the content of every tab joined by the tab
                                #     (100 % and 90 %), as high as it can be (ⓘ Connections at the top, its tab in the middle; a short one just low
                                #     enough), its corner square only where the tab joins at the top; switches show their choice filled purple
                                #     ("Entries: Matrix | Legacy", "by event | by role")
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
                                #     stops when switched off; ↺ of General; 3.38.5: "Developer mode" (dci-dev), taken over from dci-stats-dev or
                                #     dci-log-diag on (the old keys gone)
                                #   stats: 3.38.0 (E8): tab "Statistics" after "Cache" (on, empty); staged + "Enter edit" with the relationships in
                                #     /ws/js/release: counted once (log, job gone, one record in IndexedDB dci-stats with the time); the tiles, months
                                #     and days, the top lists; "Reset all" keeps them with "keep statistics", unticked deletes; off: no job; the
                                #     release page counts a waiting job (a relationship not in MusicBrainz left out, and one it had before – n0);
                                #     F2: a job with nothing to look up counts at once on the release page; 3.40.14: switched off in ⚙ → Cache
                                #   statsmore: 3.38.1: three stored submissions → the boxes: sources, how found, dates and places, levels and
                                #     works, the releases, when (7 + 24 bars, days in a row, records), instruments, text from cover art, own rules
                                #   statsdev: 3.38.2: a real submission records per relationship what was changed by hand (a role credit typed;
                                #     an answer is none) and the answers (Q002); not shown by default; in Developer mode (3.38.5): taken over /
                                #     changed by hand, the rules changed most, not recognized (once per release), the answers, duplicates avoided
                                #   statsbutton: 3.39.3 (189): the statistics' own button after ⚙ (bar chart), pressed while open; one of ⚙, the
                                #     docked rules and the statistics open; their heading folds them in; only "Collect statistics"; no tab
                                #     3.40.6 (Z-HB, Z-ST): the button before ⌨ and ⚙; "this browser only" in their head, its tooltip;
                                #     3.40.14: no switch in the statistics
                                #   statswhere: 3.40.14 (Z-SC): "Collect statistics" in ⚙ → Cache; the grey line at the top of the statistics
                                #     (on / off) leads there (tab remembered, focus on the box); ↺ of Cache: on again
                                #   statsmore2: 3.41.14 (Z-STS … Z-STC): the new cards from four records (one v 1) – suites, attributes, works,
                                #     genres, decisions, live, gaps, worked together, "Counted from 3.41.14 on"; a real record v 2 with x and a
                                #   conngroups: 3.42.0 (Z-CONS): ⓘ Connections in groups (Sources, Websites, Tools & scripts, Resources, managers, Links)
                                #   statsdelete: 3.42.0 (Z-DS): "Delete statistics …" in ⚙ Cache with the number; none in the statistics
                                #   editnote: 3.41.9 (Z-EN), 3.42.0 (Z-EN2: no None, a stored "none" is Simple): no "edit note" in the footer; ⚙ Staging → Edit note Full | Simple (tooltips list
                                #     (3.43.4, full review P5) E: "Done:" after a relationship was taken out (n) and staged again (n+1)
                                #     the lines); Full: Done; Simple: Source + Script only, also in the work form; None: the block goes, no form note
                                #   statsgenres: 3.42.6 (Z-STG2): Bandcamp's tags (pageTags: links or JSON-LD, without the place's tag) – "Genres and
                                #     styles" Combined (sources in the tooltip) | Separate, remembered

python3 t_ui_view.py            # View: the compact view, folding, the colours of the levels, small fixes, the suggestions, rows, the footer
                                #   compact: the compact view (3.27.0, milestone; 3.27.2: full by default, ☰ in the head switches and remembers compact):
                                #     a line per row, marks in colour, fields hidden,
                                #     open / "▴ compact", a track group and a pool date dropped onto the line, the question answered ([3.32.3] in the
                                #     line itself, its possibilities to click), a skipped
                                #     row grey with ✕ (back after reloading), "Full" remembered and in the settings, the jump to an incomplete row
                                #   fold: 3.29.3: the arrow next to "Artist credit for all roles" – one entry folded to compact lines in the full
                                #     view (a line opens its row, ▸ back, full again after the next import), its open rows closed in the
                                #     compact view; 3.37.15 (166): in the full view the arrow first in the head, the same x for two entries
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
                                #     3.37.8: the colour Event (plum) among them
                                #   foot: 3.38.4: the footer – 1500 px one line (≤ 60 px: ▲▼, the summary with the levels as tooltip, the chip
                                #     "2 tracks without a work" and its message on a click, Preview, the short checkboxes with their tooltips,
                                #     Stage and ⓘ at the right), 900 px two lines with "⚙ Options ▾" (above, ticked there, closed by a click
                                #     elsewhere and Esc), 600 px Stage whole, staged: "✓ 30 in the editor", in the page one line at the bottom;
                                #     3.38.13 (F-3): the green chip flashes once (not again when its text is opened and closed or the
                                #     dashboard closed and opened again: one animationstart; the class gone after the flash)
                                #   addrolebtn: 3.40.13 (Z-AB): "＋ Another role for Bass Man" a framed button below his rows (full view), a new row
                                #   entryskip: 3.40.15 (Z-SK): "⊘ Skip" in every head; all rows on Skip, grey, "↺ Take again" (the level chosen
                                #     before back); a level chosen while skipped ends it; "Remove skipped entries …": "1 skipped entry ▸" at
                                #     the bottom, ↺ there; matrix, compact: beside "by event | by role"
                                #   entryskipkeep: 3.40.15: remembered with the release (Cache on), loaded again still skipped, ↺ back
                                #   entryskipmodes: 3.40.17 (review): scope "only work" and ⊘ Skip both ways (stays skipped; ↺ inside the scope:
                                #     stays on Skip, "all": back); "Level for all rows" Recording, then Skip: "⊘ Skip", no stale "↺"
                                #   footbar: 3.41.10 (Z-SB2): classic scroll bars of a page wider and longer than the window – the dashboard at the
                                #     bottom edge ends above / left of them (its footer wholly visible), also when the page grows wider later

python3 t_ui_overlap.py         # 3.51.0 (Z-OVL, Z-IML): no two texts on each other – statistics, settings, the import (window, page), the bar of
                                #   "Edit relationships" (one line, below only when narrow); the check itself (detector); review: in the order
                                #   the page is drawn, scrolled through, fields; views (compact, 150 %, narrow, dark, Mapping rules, log)
python3 t_ui_place.py           # Window or page, the log, staying in place after a form, texts that name the source
                                #   inline: dashboard in the page instead of a window: placement, sticky dates/footer, switch, reset
                                #   logplace: log next to the edit note: right / left (width and height), above (height kept), too narrow → above,
                                #     edit note drawn anew, remembered after reloading, "↺ Defaults" → window
                                #   keepplace: after "Create artist …" the dashboard stays at the entry (window and page, without scroll anchoring)
                                #   srctexts: texts that named Discogs say "the source" with another source (3.16.2)

python3 t_entries.py            # Entries as a matrix (E4, Block AE, from 3.34.29; the default of the script)
                                #   levelclick: 3.44.0 (Z-CLV): the level of an event a button – Recording → Release → Skip (at its place) → Recording; an
                                #     arranger to Work (works matrix); the head of the full matrix, ticks of a skipped event, "Skip" in the opened event
                                #   review43: 3.43.5 (full review P6): "Remove" in a matrix line; pasted text through a redraw; the rules window in German
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
                                #   companies: 3.35.5 (AE-4): a place ("Recorded At") and a label (℗) as matrices (3.38.14, Q-c: the block
                                #     "recorded at", "from Discogs: Recorded At" in its tooltip), publishing on works keeps its
                                #     rows, compact, staged the same as legacy, a date typed into the place's event
                                #   flagcols: 3.36.6 (148): add. / guest / solo a column each, every word centred over its checkboxes (±2 px)
                                #     and not wider than its cell, at 100 % and A+ ×3
                                #   chipask: 3.37.14 (163): compact – "? bass ▾" lists electric bass guitar · double bass · acoustic bass guitar
                                #     (focus on the first, visible), double bass chosen: "double bass “bass”" without "?"; "? Taischigoto ▾", Esc
                                #     closes (focus on ▾), taishōgoto chosen; "? Directed By ▾" conductor; the chip's name opens the full matrix
                                #   chipinfo: 3.38.6 (163b): ⓘ after a chip's name with its applied notes as tooltip – none while "?"; "Buddha
                                #     Machine" (none is like it); taishōgoto chosen (chosen, a spelling of its own, written small); double bass
                                #     none; "Directed By" – chosen: conductor
                                #   barroom: 3.40.8 (Z-SB): overlay scroll bars (Chromium's FluentOverlayScrollbar, a browser of its own –
                                #     caserun.launch_own): a wide dashboard no room; 700 px: 16 px below the last line, "written “Drums”" above
                                #     the bar, only boxes that scroll (review); wide again (⤢): none; a classic bar (it takes room): no room
                                #   compactside: 3.40.10 (Z-KH, mockup C): compact – "by event | by role" in the head, count, "Writing
                                #     credits: in the works matrix" (tooltip) and the button "＋ Another role for …" beside the lines, no link
                                #     below; by role the same; the button opens the full matrix with a new line; full view as before;
                                #     (review) an entry folded in the full view: the column and the toggle
                                #   viewbits: 3.69.0 (Z-WRL, Z-CIN, Z-CRY, Z-CMK, S101–S104): no "whole release", the chips of an event one below
                                #     the other, "Create artist …" yellow, a click into a compact line jumps on Discogs; off
                                #   compactlines: 3.40.11 (Z-KH, mockup B): ⚙ Appearance "Compact entries: notes beside the lines | in the
                                #     lines" – in the lines: no column, "n to stage" and "＋ role" at the end of the last line (by event, by
                                #     role), "✓ link" and "✎ works ↓" in the head (tooltips), "✎ works ↓" brings the works matrix into view,
                                #     "＋ role", full view as before, ↺ of Appearance: beside again; (review) "Joey Bada$$" kept, "Taken out"
                                #     without the tail
                                #   evdatefields: 3.42.1 (Z-EDM): the date of an event a button; MB's fields below it (begin, end, ended, ⇣),
                                #     (3.43.3, full review P4) F: "from 2015 to ????" pasted ticks "ended"; 1998 with and without "ended" are two pool entries
                                #     Apply, a wrong month, a period pasted, ✕, no date
                                #     (3.42.8, review) E: another entry's event below shows nothing typed in Solo Man's head; an error below no second box

python3 t_sources.py            # Sources: the adapter, several linked releases, supplementing, the tracks of a source
                                #   aliascap: 3.44.1 (Z-ALC): at most 2 alias lookups (⚙ Sources), the one with the most rows first, the message, "Discogs aliases …" at the third
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
                                #   repeat: 3.40.16 (Z-RI): "↻ Repeat import" after "Source ▾", the question ("Keep my changes" preselected),
                                #     Cancel; kept: the source read again (a new credit there), "fretless" and the row taken out kept, "Dates &
                                #     tracks" open again after a fold by "Apply" (Z-PF2); afresh: the changes gone, the choice kept on a redraw;
                                #     3.40.17 (review): a new work kept / dropped, one question at a time

python3 t_sources_bandcamp.py   # Bandcamp: as a source, the "about" text, leaving it out, liner notes, label pages, track pages, credits of the "about" text, the spelling of the source
                                #   titlecomposers: 3.60.0 (Z-TCP, S088): names in brackets after the titles of a track list – writer, the switch,
                                #     a work found by name offered, jazz in the tags → composer; off
                                #   tcpsingle: 3.63.0 (Z-TCP2, S092): a single word in brackets – exactly one artist of that name an entry,
                                #     else no entry and the works found offered (also by surname); off
                                #   tarbaby: 3.59.0 (Z-TBY, S085–S087): the Tarbaby text on a label's page – names with roles without a dash, vocals by
                                #     the start of a title, the group heading and "+" left out, an info on the member MusicBrainz lacks; off: six lines
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
                                #   bcspell: 3.39.1 (185): Robert Rich credited "RR" from Bandcamp – "(the Bandcamp spelling *)", the tooltips
                                #     and the log name Bandcamp, no "Discogs" in the head; the tag "Bandcamp" in Bandcamp's blue (#629aa9);
                                #     3.39.2 (187): the line "With …" from Bandcamp – the release's artist's, "objects" asked, nothing not recognized
                                #   cloudpondbc: 3.40.4 (Z-LU): "Cloud Pond Sky River" from Robert Rich's own page – two entries "Robert Rich" with
                                #     the same link (the person, "©2026 Robert Rich"): both found, none "Looking up MB artist …"; 3.40.5 (Z-RG):
                                #     "Pacific coast" – United States first among the suggestions, not set; chosen: "as “Pacific Coast”";
                                #     3.40.8 (review): the explanation the tooltip, no disambiguation once chosen; another area by hand (✎): the
                                #     credit goes; S036 off: credited all the same, another area: it goes
                                #   youtube: 3.41.13 (Z-YT): a youtu.be address in "another source" – the video page read, its description as
                                #     credits (audio, mix, cameras, editor, Host asked), the edit note's Source; no description, no video; statistics
                                #   ytlinks: 3.42.7 (Z-YTL): the videos a release links to as sources (each once, after Discogs), one alone loaded
                                #     at once; the order with YouTube last (also an order stored before); (3.42.8, review) from the release editor
                                #     with a new video only: Discogs

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
                                #   gapline: 3.39.0 (172): the line of the release page (estimate, parts, the dashboard's number), Discogs kept,
                                #     ✕ until the number changes, the setting off, "Import credits …" → the dashboard (its number kept)
                                #   gapmore: 3.40.0 (AY): no line without credits or when nothing is missing (setting dci-gap-none, one missing, the
                                #     dashboard counted none – rows open: the line –, the same credits a week later); "Count exactly" (Discogs with two
                                #     media, Bandcamp): the tab #dci-count imports and counts, the line takes the number, the tab is closed; an import
                                #     that fails; Bandcamp's rough estimate, its parts, instruments in capitals; a page without credits ("Stream: …");
                                #     3.40.2 (Z-AD, Z-AE): Discogs without credits → Bandcamp with the text first; three Bandcamp pages → the one with
                                #     more credits, the others under ▸, ✕ holds; 3.40.3: "Import credits …" imports Bandcamp, Discogs 404 → Bandcamp
                                #   languagesload: 3.34.0: the languages file from the manager (German); fetched from GitHub (kept, one reload);
                                #     English chosen → fetched quietly, German at once from ⚙; missing → message, English, the log warns
                                #   gapsplit: 3.41.15 (review, Z-SUB): the release page reads an index whose sub-tracks are MB tracks as them –
                                #     Bass Man on track 4 is there: "the credits of its list seem to be on MusicBrainz"

python3 t_coverart.py           # Text from cover art (beta, 3.34.1, item E3): ⚙ Settings → Beta, the Cover Art Archive, Tesseract.js (stand-in)
                                #   ocrsetting: the tab "Beta" before "ⓘ Connections", the switch off by default, "Source ▾" gets the item only
                                #     while it is on (stored); the connections X013, X014; [3.38.0] the tabs from "Beta": Cache, Statistics, ⓘ Connections
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
                                #     3.37.5: E) opened again as it was left (the three texts), "↺ Start over" first
                                #   ocrdiscogs: 3.34.7: "Load Discogs images" (nothing fetched before), the release's page: its images once at
                                #     600 px, not another release's; a Discogs address typed (twice refused); read ×3, the source
                                #   ocrstart: 3.34.8: "… from cover art" only with the beta, joined to "Import credits …"; the dashboard without the
                                #     import (nothing of Discogs), the message, the window; the read text the source; beta off: gone
                                #   ocrpeek: 3.34.9: tiles alike with the whole image; the larger view after a pause (1200 px image, its
                                #     proportions, 480 px), gone on leaving; an own narrow file larger; in the frames step too
                                #   ocrload: 3.34.10: previews counted; the ticked images loaded ahead two at a time (held requests), the third
                                #     waiting; unticked: out of the queue, one loading ahead stopped; "loaded"; loading ahead off (stored):
                                #     nothing ahead, the frames step shows its own loading
                                #     3.37.5: C) opened again as it was left – "↺ Start over" first
                                #   ocrlocate: 3.34.12: an uncertain word clicked – selected, marked, zoomed in on (again: its next place);
                                #     the caret in a line marks it (brought into sight), ⤢ keeps the mark, a line replaced: none; a Tray read
                                #     ×3 – its place on the canvas; a PDF page's own text – the place of its line on the page drawn
                                #   ocrzoom: 3.34.11: two frames on the Back, the Booklet whole – wider window, a part per frame beside its text
                                #     (the image there); +, −, Ctrl + wheel, double click, drag, ⤢; a part's text changed and imported
                                #   ocrremember: 3.34.17: two frames on the Back, the Booklet turned and whole – stored; opened again:
                                #     "Back 2 frames", read as left; the 1200 px copy: the frames fit (×0.8); forgotten with "Delete stored
                                #     import …" and the reset of Beta
                                #     3.37.5: B) "↺ Start over" first – the frames stored stay
                                #   ocrmore: 3.34.16: 30 images – 12 shown (12 previews), "Load 12 more", "All shown (24)"; 12 small images
                                #     beside the frames, then 24; Auto-select with 30 booklet pages – all shown; a PDF of 15 pages – 12
                                #     3.37.5: E) "↺ Start over" before each PDF; a store of other images (D) left aside
                                #   ocrorigin: 3.34.22: Back and Tray read and imported – "From the cover art · Back" / "… · Tray" at the rows, ⓘ shows
                                #     the crop of the line (JPEG, at most 640 × 160) and hides it again; a line changed: no ⓘ; another text: nothing
                                #   ocrentry: 3.34.24: Bob Lee on the Back and the Tray – the head of his entry "From the cover art · Back, Tray", ⓘ the
                                #     crops of both lines, hidden again; an entry of a pasted text afterwards: nothing
                                #   ocrlinepeek: 3.37.4: lines not recognized / left out of the Back – marked, the hint; the mouse on one: its
                                #     cut-out below it (JPEG, about a line around it, "Back: …"), away: gone; the keyboard focus the same; a
                                #     pasted text afterwards: no cut-outs
                                #   ocrkeep: 3.37.5: the window kept – read (Back, an own file), a text changed, imported, opened again: as left
                                #     (nothing read again, both drawn); the page loaded again (remembering on): the texts, the Back drawn,
                                #     "An own file was used: credits.png – add it again", added: its card back, ticked; "To the texts read";
                                #     1200 px: the places fit; the list of the release failing after a reload erases nothing;
                                #     "↺ Start over": as at first, nothing stored; remembering off: kept only until the reload
                                #   ocrnonsense: 3.37.6: "Remove nonsensical words and signs" – the Back's switch: "~", "|" at a line's end, a
                                #     line of signs, uncertain words without a vowel go ("7 removed", struck), » | between words, ℗, sure words
                                #     stay; a word added by hand, off: all back in place, the word stays; the switch for all (8); imported on
                                #   ocrauto: 3.34.15: nothing ticked at first; "Auto-select" ticks Back, Booklet, Tray; off – its ticks go,
                                #     those set by hand stay; switched on in ⚙ Settings with the window open – ticked at once, and when
                                #     opened again; 30 booklet pages, loading ahead on: 2 load, 22 wait, 6 not ahead
                                #     3.37.5: D) the window as it was left (the Front ticked by hand stays), opened again: the same
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
                                #   trackcells: 3.38.8 / companion 1.9.2 (174): a tracklist as a table with credits on tracks – marks inside the
                                #     cell before the line with the role, none where the role is not on the line, no mark in a row (three cells);
                                #     [1.10.0] "Written-By – Bass*" of an artist also in "Flute – Bass Man": its own line, not before the title
                                #   multi: 3.38.9 / companion 1.10.0 (173): two other imports send their status – the marks on the Discogs tab stay;
                                #     the dashboard opened late: no "older companion"; the same release in another import used later: its marks
                                #     and the note "2 imports …", a click there does not reach the first; the first used again: its marks, a
                                #     click reaches it; closed: no note
                                #   copymarks: companion 1.10.1 (Z-CR): the page writes "Copyright ©" / "Phonographic Copyright ℗" (the data
                                #     "(c)" / "(p)") – a mark on each line, a click on the row "Copyright (c)" highlights its line
                                #   review43: 3.43.1 / companion 1.11.1 (full review P2): a Discogs tab in the background (beat 30 s old) still
                                #     "connected"; the result of another dashboard's jump not shown; the "Count exactly" editor sends no marks
                                #   sitedark: companion 1.12.0 (Z-DM): the marks follow the site's dark theme (Discogs: a dark background, data-theme; YouTube: html[dark]); review: oklch(), "header-dark", "darkblue-light" stay light
                                #   copymarks2: companion 1.13.0 (Z-MCP): copied text without the marks

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
                                #   multibc: 3.38.9 / companion 1.10.0 (173): three imports, two sources (a Bandcamp album here, a Discogs release
                                #     and another one in two other editors) – for 10 s the marks on the Bandcamp tab and the Discogs tab stay
                                #   ytview: 3.42.8 / companion 1.11.0 (Z-YTC): a YouTube tab – no tab, another video, "Load the release there",
                                #     marks in the unfolded description, a click shows the row, jump, off and on, another video without loading and
                                #     back, the description drawn anew; an old companion: "needs 1.11.0"; (review) the jump's line goes with another
                                #     video, a description coming later gets its marks, folded by the user stays folded

python3 t_static.py             # Without a browser: the texts of the script, the list of connections, the mapping file, the languages file
                                #   i18n: the texts (3.27.1; 3.34.0: English from the script, de / es / fr from the languages file): every key
                                #     the code names in English, no left-over translations, no foreign
                                #     placeholders, French no-break spaces, the English fallback (Node); reports the missing translations;
                                #     3.39.2: also the keys of trSrcOf (with their …Any form) and both keys of log(level, a ? 'k1' : 'k2')
                                #     per language (LIST=1: all keys) – not an error
                                #   connections: the connections (3.25.0, Node): every address of @match / @connect and of the code belongs to an entry of
                                #     CONNECTIONS, the ids are unique, every entry has its texts in English (3.27.1; before: four languages)
                                #   mappingfile: 3.33.0: mb-vibecode-credits-importer-mapping.json – format, version, its lists against `MAP.X` of the
                                #     script, patterns compile, @resource / @grant / @connect, read in Node
                                #   languagesfile: 3.34.0: mb-vibecode-credits-importer-languages.json – format, version, de / es / fr, its layout
                                #     (that of i18n_add.py), only English in the script, @resource languages, read in Node (German, else English)
```
                                #   round6: 3.41.5 (BE): translation round F-6 – a sample of the blocks AL – BD in de, es, fr (not English, symbols,
                                #     the French no-break space)
                                #   legacy: 3.41.7 (Z-LG): the view "Legacy" named "Legacy" in de, es, fr too (and in the note of 3.35.0)

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
| t_bridge.py | t_ui_settings.py | pressed (until 3.36.4: bridge) |
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
