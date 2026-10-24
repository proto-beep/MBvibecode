# MB x Vibecode – test tools

Browser tests for **MB x Vibecode: Credits Importer** and its **Companion** (until 3.0.0 / 1.5.0 “Import Discogs credits”
and “… COMPANION”), run with Playwright (Python) and Chromium. MusicBrainz, Discogs and Bandcamp are not reached:
`harness.py` serves a mock relationship editor (`MB.relationshipEditor`, `MB.linkedEntities`, `MB.tree`), the
MusicBrainz web service (lookups and the search), the MusicBrainz release page, the Discogs API, a Discogs release page
and Bandcamp album and track pages. The userscript manager's shared storage (`GM_setValue` …) is replaced by a small local HTTP
server, so the companion shares its values between pages as it does in Tampermonkey.

## Layout

```
MBvibecode/ (this repository)
  mb-vibecode-credits-importer.user.js             main script
  mb-vibecode-credits-importer-companion.user.js   companion
  tools/i18n_add.py                   adds or replaces texts in the embedded translations (en, de, es, fr)
  tools/i18n_del.py                   removes texts from the embedded translations (all languages, with plural forms)
  smoke/harness.py                    mock MusicBrainz, Discogs and Bandcamp, shared GM storage, helpers
  smoke/zooid.py                      scenario after Discogs release 38282688 (10 tracks, two sessions, two studios)
  smoke/common_rows.py                helpers for the date tests: rows (tracks, date), matrix cells, staging, drag with the mouse
                                      (the target is scrolled to the middle first: near the edges the dashboard scrolls while dragging);
                                      date_field(row, f): a date field of a row – opens a date chip (3.9.0) first
  smoke/t_*.py                        tests (each prints OK/FEHLER lines)
  smoke/register_corpus.json          frozen input of the register's golden test (t_register.py)
  smoke/register_golden.json          its expected results (written with UPDATE=1)
  smoke/text_corpus.json              credits lines from real releases and cases around them, with their stored reading
                                      ('expect', written with UPDATE=1 by t_textcorpus.py; 'later': still read wrong, planned)
```

## Running

```
pip install playwright && python -m playwright install chromium   # once
# t_adapter.py also needs Node.js (its part B loads the script in Node)
cd smoke
python3 t_basic.py        # dashboard loads, companion connected, status marks on Discogs
python3 t_focus.py        # typing in every date field keeps cursor and text
python3 t_release.py      # MusicBrainz release page checks what arrived (✓ / ✗), marks go when closed
python3 t_pub.py          # publishers ticked only where a writer has them as personal publisher
python3 t_ar.py           # A&R with task on the release group
python3 t_trackpool.py    # dates for some tracks: suggestions in the matrix, Apply splits rows, applying again, several days
python3 t_media.py        # release with two media: "CD2, tracks 1–3", "Disc 1", medium headings, track group per medium
python3 t_artwork.py      # cover miniature on the Discogs page: shown when connected, click, fold, drag, place kept
python3 t_rows.py         # remove a row (and undo), removal after staging, "only works"
python3 t_matrix.py       # date matrix by hand: drag & drop, grip + "place here", editor, auto apply, stamp, after reload
python3 t_pools.py        # "Dates & tracks" folds (remembered), clear all track groups / dates (also other releases)
python3 t_reset.py        # "↺ Reset all settings …" (⚙ Settings, 3.25.0; before "↺ Defaults" in the head): settings, own
                          # rules, pools of all releases, cover box on Discogs
python3 t_choose.py       # separate days ("June 16 & 19"): both days and the period in the pool, "Choose" in the matrix
python3 t_inline.py       # dashboard in the page instead of a window: placement, sticky dates/footer, switch, reset
python3 t_dragdates.py    # pool dates dragged onto rows / works matrix, dates joined into periods, pools loaded again, "Cover Art"
python3 t_notice.py       # update notice (milestones, closed, language) and the one-time resets of stored data (generations 2 to 4, also companion;
                          # generation 4 clears the list of created works too)
python3 t_bar.py          # language before opening (3.27.1: the question after the installation, then the settings), fold at the
                          # bottom, date pool kept when folded, common month/year, horns, producer
python3 t_tracksdrop.py   # track groups dragged onto rows (Shift adds, release level moves), track pool kept when folded,
                          # works matrix cells that cannot take a date, work credits checked on the works (release page)
python3 t_fill.py         # dates added to MB's dateless relationships from the works matrix (edit, ×, edit note),
                          # status marks of credits on works that were new in the editor (found through the recording)
python3 t_rules.py        # Mix / Recording / Engineer [Mix, Recording] / Trumpet [Pocket Trumpet] without role credit,
                          # rule ids open "Mapping rules" at the rule, autoscroll while dragging (0.2 s, as in browsers)
python3 t_matrixcols.py   # "Directed By" asked, works matrix columns taken out / back, column dates for MB's dateless relationships
python3 t_trackmarks.py   # a status mark on each Discogs track line, checked per track on the release page
python3 t_v217.py         # "Mixed By [Mixing]" (S019), "Bass Guitar" asked (Q004), "[Additonal Musicians]" (S002), "All Music By",
                          # "©© Label 2005" (D015), ‹ › through the incomplete rows, Escape closes "Mapping rules" first, text size 50 %
python3 t_wattrs.py       # works matrix attributes as short forms (ac co de in ka li me pa): "li" preselected only on new links,
                          # "li?" offered on the existing one, open/closed rows, "Attributes for all", "spell out", staging;
                          # "Music And Lyrics By" → writer, "Song" preselected (R098, S020)
python3 t_mxdrop.py       # track lists from the Discogs notes as track groups and suggestions (✓ / ×), generous names;
                          # track groups dropped onto a column head (Shift adds), a role, an attribute of the works matrix
python3 t_mediasel.py     # media choice before the import (three media): all = as before, media 2-3 without the release level,
                          # "Choose media …", remembered choice preselected, unknown media, cancel / Escape
python3 t_logplace.py     # log next to the edit note: right / left (width and height), above (height kept), too narrow → above,
                          # edit note drawn anew, remembered after reloading, "↺ Defaults" → window
python3 t_keepplace.py    # after "Create artist …" the dashboard stays at the entry (window and page, without scroll anchoring)
python3 t_adapter.py      # source adapter (3.0.0): no Discogs data outside the adapter; the neutral release in Node (headings,
                          # index tracks, "A1 to A3", grouping, S018); through the adapter in the dashboard: aliases, series and
                          # parent label, forms for artist / label / series / work, edit notes, live from the format, US dates,
                          # Discogs tab, release picker; update from 2.19.1 without reset (PARTS=C: only the dashboard part)
python3 t_v219.py         # suggestions yellow and dashed everywhere (date and works matrix, "li?", unused pool entries from the
                          # notes), "mixed" half filled, "waits" dotted; "Commissioned By" (person, label; without and with tracks),
                          # "Live Recording By" → recording without credit and "live" only on new links of its tracks; staging
python3 t_freetext.py     # credits from a pasted text (3.2.0): "Name – roles", "Role: names", two clauses in a line, places
                          # ("Recorded live at …", "Mastered by A at Studio"), tracks ("Tracks 3–4: …", "(1, 3)"), ℗, lines not
                          # recognized; works matrix; names only suggested (dashed, yellow), a click assigns; edit note
python3 t_bandcamp.py     # Bandcamp as a source (3.3.0, 3.3.1): physical media → Discogs first, Bandcamp chosen in the picker (album and
                          # track pages through GM_xmlhttpRequest, band linked by its page, choice kept after a reload, edit note),
                          # digital media → Bandcamp first, order changed in the list, the Bandcamp menu (track pages off,
                          # "Test page"), a band not credited so on the release only suggested; the spelling compared
                          # with the release's artist credit, not with the MB artist's name (rule 4); the spelling check line
python3 t_supp.py         # a second source supplements the loaded one (3.5.0): only on request, the list "Supplements from …"
                          # (new role, new entries with suggestions, "differs", not recognized), marks DG BC / BC ≠, take over
                          # selected, edit note ("Also from", added only, differs); "Delete stored import …"; the old script
                          # on the page (stays out / warns); G: supplement with a typed Bandcamp URL (3.8.0)
python3 t_names.py        # texts (3.6.0): "tenor & soprano sax, trumpet and clarinet" (shared instrument word), "bass & electric
                          # guitar" stays two; a list with an unknown part ("→ ? “sticks-and-stones”"); name suggestions without
                          # accents ("Agusti" → "Agustí") and "similar name" with a middle name ("Barry Guy" → "Barry John Guy")
python3 t_about.py        # Bandcamp "about" text (3.7.0): "recorded at Loft in Cologne, june 16/17 2018" → place Loft (Cologne),
                          # places suggested only in that area, the period in the date pool; "Studio Nord, Bremen" in the credits;
                          # "mixed at home in Oslo", "at the same time", "at last" give no entry (3.13.1)
python3 t_reldate.py      # date matrix "Release level" (3.10.0): applied (recordings March, release June), switching the level
                          # takes the matching date, a date typed by hand stays, the mark stored with the matrix
python3 t_register.py     # the mapping register stays the same (3.11.0, golden test): a frozen corpus (register_corpus.json:
                          # ~1,200 roles, ~100 company roles, ~50 date phrases, pasted texts) through the register in Node, the
                          # texts in the dashboard and the window "Mapping rules" – compared with register_golden.json;
                          # UPDATE=1 python3 t_register.py writes the golden file anew after a change of the register that is meant
python3 t_recheck.py      # fixes of 3.12.1: "n lines not recognized" opens in the window; same-named works searched again when
                          # a text's writer is assigned (found then), not without a change; a new import searches anew
python3 t_initials.py     # name suggestions for names with an initial (3.13.0): "T. Snekkestad" → Torben Snekkestad, "Barry J. Guy"
                          # → Barry John Guy, "K. Tanaka" → Kenji (not Hiro) Tanaka, no second search without an initial
python3 t_rulesname.py    # "Mapping rules" says "Discogs" only with Discogs loaded, "role" with a text (3.13.2), follows at once
python3 t_textrules.py    # rules for free credits texts (3.14.0): "Music played and recorded by X in March and April 2025",
                          # "Mixed and mastered by X in May 2025", "Photography Sam Lee", "mastering john doe", the label line
                          # left out, "… created by a human" → the release's artist suggested; the period 2025-03 – 2025-04
python3 t_jump.py         # ▲ ▼ in the status bar jump to the top and bottom of the dashboard, in the window and in the page (3.14.1)
python3 t_special.py      # special purpose artists (3.15.1): Various Artists and "[soundtrack]" are not asked for their works,
                          # logged once; table T026 in "Mapping rules"
python3 t_mastering.py    # mastering only on the release level (3.15.1): two engineers for CD 1 / CD 2, no "Recording", no
                          # "Release level" in the column, the track group decides which mastering row takes a date
python3 t_suggstack.py    # suggestions as a block below the red mark (3.15.2, 3.15.3: side by side, wrapping): eight artists of one name, 5 shown + "+ 3 more",
                          # explanations as tooltips
python3 t_aboutoff.py     # "Leave out the about text" (3.16.1): place and dates of the about text out and back, with the changes,
                          # kept across a reload, reset by "Delete stored import"
python3 t_srctexts.py     # texts that named Discogs say "the source" with another source (3.16.2)
python3 t_settings.py     # the menu "Settings" (3.16.0): topics, shared switches both ways, values in steps, a topic's "↺",
                          # the works of the artists kept across a reload (IndexedDB), clearing them, switched off
                          # 3.25.0: the topics as tabs, one shown at a time
python3 t_bcview.py       # the Bandcamp view of the companion (3.17.0 / 1.8.0): "no Bandcamp tab" → open in background, another page →
                          # "Load the release there", marks before each part of a line (none in the about text, shortened texts
                          # opened), mark → row, jumps (part of a line, sentence of the about text, track both ways), track
                          # pages (link, loaded, own marks), ● after staging and ✓ on the release page, menu, old companion
python3 t_bcoff.py        # credits switched off on Bandcamp (3.17.1; 3.17.5: a click on the mark, the pointer shows the row): off → "Skip" with a note and greyed, a
                          # group of marks, on again with its level, kept across a reload, a level chosen, "Delete stored import"
python3 t_linernotes.py   # liner notes in Bandcamp's about text (3.17.2): the three places of the name, five sentences over several
                          # paragraphs, cases without (4 sentences, "Special Thanks" …), entry as suggestion, pool name, jump, left out,
                          # 3.17.6: the date as a suggestion at the row, ✓ takes it
python3 t_relcheck.py     # the release page keeps its check (1.8.2): ✓ after "Enter edit", a check without answer keeps ✓ and is
                          # retried, a background page's beat counts 75 s
python3 t_distrib.py      # "Distribution - !K7" and variants (3.17.3, T028): company "Distributed By", label → release distributed
python3 t_navlink.py      # the source in the navigation bar (3.17.4): link, "open in background", "Load the release there"; ↗ at suggestions
python3 t_keepmarks.py    # a click on a Discogs mark switches its credit, the pointer shows its row, "Click switches" off, "Keep marks" (3.17.5)
python3 t_worksskip.py    # the works matrix (3.18.0): fold / unfold (not kept), "Skip works matrix" (rows on "Skip", nothing of it planned,
                          # no works level, kept across a reload, no lookups), taken again, the question from N tracks ("Not now", later);
                          # 3.19.3: the tooltips of what is counted, the setting for the skipped rows
python3 t_manualtop.py    # "Add entry manually" as one line above the date pool (3.18.0): tooltip, "?", in view when scrolled (window and
                          # page), an entry added from there is shown
python3 t_afteredit.py    # start from the release editor (3.19.0; 3.23.0: the button "Enter edit & import credits" instead of the tick): only
                          # on "Edit note" with a Discogs/Bandcamp link, right after "Enter edit", orange; "Enter edit" stays plain; the
                          # button and Ctrl+Alt+Enter → relationship editor with the dashboard, an error, "Add release" with a Bandcamp
                          # link typed in (German, loaded at once), the setting off, other release pages untouched
python3 t_medium.py       # the medium of the release decides (3.21.4): vinyl mastering, "(vinyl)", lacquer cut on Digital Media left out
                          # with the reason (and a studio only for it), the digital half kept; "Translated by" on Bandcamp asks
python3 t_foreign.py      # instruments and voices in German, Spanish, French (3.21.2): mapped as the English term without role credit,
                          # "saxo tenor y soprano", "y" between names, "bajo" asks like "Bass", "Alto" asks (viola …), T034 in the window
python3 t_textcorpus.py   # text recognition, part 1 (3.21.0): the corpus text_corpus.json through the text adapter (golden), then the
                          # Maya Recordings credits in the dashboard – four sentences in one line, "P + ©", thanks and strings left out
                          # on purpose, no 1988 in the pool; "Logo by … instagram.com/…" (design, "logo", the profile, a suggestion via
                          # it), "Create artist …" with the profile (not Linktree), "Text" answered with lyricist → works matrix
                          # 3.21.3: links hidden at first, shown with the setting, Spotify only for "Create artist …", "Create place …"
                          # with a studio's profile
                          # 3.22.0: the corpus with titles ("on “A”, “B”") and areas ("(Asturies, Spain)"), no "later" lines
python3 t_v3222.py        # 3.22.2: "Kontrabass" → double bass (3.22.3: without role credit; text and Discogs), "Contrabass" credited
                          # "contrabass", "Violoncello" → cello "violoncello";
                          # produced / remixed / engineered in (areas with the area they are part of); recording without role credit
                          # (also with a task field); the rules window's patterns ("(manufactured | made) (by | at)")
python3 t_entryhead.py    # the head of an entry and the bar below the button (3.28.0): only the tag links to the source (↗), the chip
                          # "as “B. Man”" (+1), the credits in the compact lines; the bar: status and ⚙ only, ⚙ → the settings
python3 t_msgs.py         # messages (3.27.3): ✕ on each, "▾ n messages" folds them, a new error unfolds, a fresh import shows them again
python3 t_bctrack.py      # a Bandcamp track page as the release (3.28.1 / companion 1.8.4): loaded from the link, its credits once,
                          # the tab "connected" with marks; a track of an album via "Other source", "Load the release there"; Test page;
                          # the text "… Bandcamp track pages too", long settings texts wrap
python3 t_nordic.py       # Norwegian, Swedish and Danish roles (3.28.2): no role credit for a translation in brackets or a text, "Artwork
                          # [Logo Og Kunst]" → design "logo" + artwork "art" (two marks on Discogs), vocals "screams"/"clean", case-only
                          # names without "credited as" (typed in: kept), "Wood Flute"/"wood flutes" → flute credited so;
                          # 3.28.3: the rules named at the rows (S031 – S035, S033 not S018)
python3 t_textmarks.py    # used dates and track groups underlined at the source (3.28.3 / companion 1.9.0): Discogs notes (matrix,
                          # a row, not the pool), status off/on, Bandcamp credits (a year also in "released …") and "about";
                          # two "Vocals [...]" lines of one artist
python3 t_textcredit.py   # 3.28.4: "Cover/Sleeve/Booklet/Package Design" → design "… design", "Artwork [Design And Layout]" one row
                          # "design and layout", "Artist credit for all roles" empty for a case-only spelling, a text's name linked:
                          # credited as written (not when only the case differs)
python3 t_datewords.py    # 3.28.5: "19 & 20. 01. 2009", "20. 01. 2009", "1973 October 19", issue years left out, the group only from
                          # the date's sentence, "mixed and mastered" → Mix and Mastering (Node and the date matrix)
python3 t_facets.py       # 3.28.6: "C1 to D" (side D one track) and the other ranges of "Facets" as dated track groups in the matrix,
                          # "in live concert" → "live" for the tracks of that sentence only, no places from the notes
python3 t_prose.py        # 3.29.0 (milestone): ekstasis' prose credits (K.M. (sounds, words) & E. (voice), "channeled by", "the
                          # guided hand of"), "Mixed and mastered at TQA.HQ (July 2026)", "Tenor, alto, soprano saxophones",
                          # "wood flutes", "Mixed and mastered by … in March 2026" – rows, places and the date matrix;
                          # 3.29.1: "(noises, electronics)" → effects "noises", electronic instruments "electronics", "(field
                          # recordings)" → field recordist
python3 t_levels.py       # 3.29.2: the colours of the levels (full rows and compact line), the level of the compact line by a click
                          # (Recording → Release with the June date of the matrix → Skip → Recording with the March dates), the tab
                          # "Appearance" (text size, place, view, colours: own colour, off, ↺)
python3 t_i18n.py         # the texts (3.27.1): every key the code names in English, no left-over translations, no foreign
                          # placeholders, French no-break spaces, the English fallback (Node); reports the missing translations
                          # per language (LIST=1: all keys) – not an error
python3 t_compact.py      # the compact view (3.27.0, milestone; 3.27.2: full by default, ☰ in the head switches and remembers compact):
                          # a line per row, marks in colour, fields hidden,
                          # open / "▴ compact", a track group and a pool date dropped onto the line, the question answered, a skipped
                          # row grey with ✕ (back after reloading), "Full" remembered and in the settings, the jump to an incomplete row
python3 t_head.py         # the head in one line (3.26.0; 3.27.2: ☰ first, "open in background" purple): symbols with names (words only when wide), no language / place / switches in
                          # the head; "Source ▾" (Escape, a click elsewhere, "Paste text …" below the head); "+ Supplement"; the language
                          # asked after the installation (en / fr-FR preselected, OK, gone after reloading, not after an update)
python3 t_settabs.py      # the settings as tabs (3.25.0; 3.27.2: the heading folds them in): only the gear folds them out and in, eight tabs (3.29.2: nine, "Appearance" after General; General chosen), ↓ / End /
                          # Home, the tab remembered after reloading ("Texts" with the web links and "Mapping rules"), the ⓘ in the head
                          # opens "ⓘ Connections" (ten rows, Harmony with its home page), "↺ Reset all settings …" below the tabs shows
                          # the question in the settings ("Cancel" back to the tab), no "↺ Defaults" in the head, narrow: tabs in a row
python3 t_connections.py  # the connections (3.25.0, Node): every address of @match / @connect and of the code belongs to an entry of
                          # CONNECTIONS, the ids are unique, every entry has its texts in English (3.27.1; before: four languages)
python3 t_tracksfit.py    # tracks compared with MusicBrainz (3.24.1): in the dialog a release with a bonus track yellow, the one with the
                          # most data among the fitting ones preselected ("most data with matching tracks"); the yellow message after
                          # the import (number, titles with the differing ones); small differences ("(Remastered)", "The …") fit
python3 t_links.py        # several linked releases of one source (3.24.0): the dialog counts each (one cannot be read), the one with the
                          # most data bold and preselected, all in background tabs, "Import" (remembered, loaded at once next time),
                          # another one by hand without remembering, "Cancel" (the message as before)
python3 t_labelpage.py    # an album on a label's Bandcamp page (3.22.1): no link for the artist, searched by name (the release's artist
                          # first, "release artist"), the hint with the page and MB's label ("a label of this release ✓"), the source
                          # line, the log; the account's name from "data-band" / "og:site_name" (Node); Discogs: a person without MB
                          # link gets same-named suggestions
python3 t_areas.py        # text recognition, part 2 (3.22.0): "Recorded by X in Xixon, Asturies, Spain" – X and an area entry (kind Area,
                          # Gijón suggested by its alias "Xixón", no "Create", "recorded in" staged on the recordings); tracks by their
                          # titles ("Piano in ‘A' and 'B' is a contribution by X", one letter off, "Not matched"); Bandcamp: titles of the
                          # album, the area of the "about" text
python3 t_mediaload.py    # the media dialog (3.20.0, 3.21.1): load the chosen media in the editor in the background – MB's editor built
                          # as MusicBrainz builds it (a.expand-medium#disc<n>, "Expand all mediums", "Load all tracks..."), a medium
                          # without a tracklist named, the works question there ("Not now", "Skip works matrix"), media 1 and 3 only,
                          # tracks and relationships the release lookup leaves out read from /ws/js/tracks
python3 t_harmony.py      # Harmony (3.19.1): a release editor seeded by Harmony (a note, no button, "Enter edit" → Harmony's Release
                          # Actions), there "Edit relationships with Credits Importer" below "Add cover art", the link opens the dashboard
                          # and loads the Bandcamp album; no release, "discogs=", another tool's redirect; 3.19.2 (3.23.0: the button
                          # instead of the tick): a background tab (opened once by Harmony's page), an error, the settings
python3 t_artistworks.py  # works of the artists (3.15.0): a release artist's work, a performer's cover, no duplicate with the
                          # writers' search, the order, read once per session, 2,500 recordings (message after 10 s, capped at
                          # 2,000), no redraw while typing in the works matrix (takes about 3 minutes)
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
artist with an MB entry twice in the background (one request a second), so a test that counts MusicBrainz requests
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
written for the full rows; `view=None` keeps the default (compact, `t_compact.py`); `open_mb_any` sets "Full" too. Every test starts as a first installation, so
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
English alone (`{"en": {…}}`) is enough, the other languages follow in a translation round (`t_i18n.py` lists what is missing).
