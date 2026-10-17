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
python3 t_reset.py        # "↺ Defaults": settings, own rules, pools of all releases, cover box on Discogs
python3 t_choose.py       # separate days ("June 16 & 19"): both days and the period in the pool, "Choose" in the matrix
python3 t_inline.py       # dashboard in the page instead of a window: placement, sticky dates/footer, switch, reset
python3 t_dragdates.py    # pool dates dragged onto rows / works matrix, dates joined into periods, pools loaded again, "Cover Art"
python3 t_notice.py       # update notice (milestones, closed, language) and the one-time resets of stored data (generations 2 to 4, also companion;
                          # generation 4 clears the list of created works too)
python3 t_bar.py          # language in the page bar, fold at the bottom, date pool kept when folded, common month/year, horns, producer
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
python3 t_artistworks.py  # works of the artists (3.15.0): a release artist's work, a performer's cover, no duplicate with the
                          # writers' search, the order, read once per session, 2,500 recordings (message after 10 s, capped at
                          # 2,000), no redraw while typing in the works matrix (takes about 3 minutes)
```

**Golden test of the register:** `register_corpus.json` was made once from Import 3.10.0 and stays as it is (more roles
can be added; then write the golden file anew). `register_golden.json` holds the results. A refactoring of the register
must leave `t_register.py` OK without `UPDATE=1`; a change of a rule that is meant shows exactly the roles it changes –
check them, then write the file anew and say so in the code changes.

The rows of the dashboard rearrange with its width (3.9.0) and a pool or matrix date is a chip: tests that type into a
row's date fields use `common_rows.date_field(row, f)`, `rows_of` reads the chip's `data-date`. A button the floating
log window may cover in the 1500 × 1000 test window ("Apply" of the date matrix) is clicked by script
(`locator.evaluate('b => b.click()')`).

`harness.DG_API` gives a test its own answers of the Discogs API (path → JSON, `None`: 404), e.g.
`H.DG_API['/artists/3030'] = {...}` for an artist with members or aliases.

Bandcamp: `harness.BC_PAGES` maps a page URL to its HTML; `harness.bc_page(data)` builds a page with `data` in its
`data-tralbum` attribute (`current.title/credits/about`, `trackinfo[].track_num/title/title_link`, `artist`).
`harness.BC_ARTISTS` maps a band URL (`https://band.bandcamp.com/`) to an MB artist `(mbid, name)` for the URL lookup;
`harness.RELEASE_AC` is the release's artist credit, `[(mbid, MB name, name as credited, join phrase)]`.
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

Relationship types of the mock are made with `harness.lt(id, gid, name, type0, type1, attrs, dates, deprecated)`; as on
MusicBrainz, artist–recording "mastering" is deprecated (the dashboard leaves it out) and artist–release "mastering" (42)
exists (3.15.1).

`harness.WORK_RELS_DIRECT_ONLY = True` leaves the submitted relationships of the work out of the release lookup, as
while its link to the recording is still an open edit; `/ws/2/work/<id>` still has them (`harness.WORK_LOOKUPS`
records these lookups). A test can put relationships that are already in MusicBrainz into the mock editor's state as
`existingRels`; an update of one of them moves it to `added`, as MusicBrainz shows it as changed.

Chromium is started with `harness.LAUNCH_ARGS` (web security off), so the pages may call the local storage server.
Texts are added with `python3 tools/i18n_add.py <anchor key> <file.json>`; the JSON holds `{lang: {key: text}}`.
