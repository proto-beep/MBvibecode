# MB x Vibecode – Changelog

All notable changes to both userscripts in this repository, newest first. Releases published together are listed together.

What changed in the code with each version (functions, stored data, texts, tests) is in the [code changes](mb-vibecode-credits-importer-CODE-CHANGES.md).

- **Import** = MB x Vibecode: Credits Importer (`mb-vibecode-credits-importer.user.js`), called “MB x Vibecode: Import Discogs credits” (`mb-discogs-credits-import.user.js`) until 3.3.0
- **COMPANION** = MB x Vibecode: Credits Importer Companion (`mb-vibecode-credits-importer-companion.user.js`), called “MB x Vibecode: Import Discogs credits COMPANION” (`mb-discogs-credits-sync.user.js`) until 1.6.0

The names changed on 2026-10-13 (Import 3.1.0, COMPANION 1.6.0), because the main script reads more than Discogs now; the files followed with Import 3.3.1 and COMPANION 1.6.1, so both scripts are installed anew from their new URLs. The column names below stay.

## Overview

| Date | Import | COMPANION |
|---|---|---|
| 2026-10-17 | 3.11.0 – 3.17.0 | 1.8.0 |
| 2026-10-16 | 3.5.1 – 3.10.0 | – |
| 2026-10-13 | 3.1.0 – 3.5.0 | 1.6.0 – 1.7.0 |
| 2026-10-12 | 2.17.0 – 3.0.0 | – |
| 2026-10-11 | 2.8.0 – 2.16.0 | 1.4.1 – 1.5.0 |
| 2026-10-10 | 2.4.3 – 2.7.0 | 1.3.0 – 1.4.0 |
| 2026-10-09 | 2.4.2 | 1.2.0 |
| 2026-10-07 | 2.1.0 – 2.4.1 | 1.0.3 – 1.1.0 |
| 2026-10-06 | 2.0.0 – 2.0.1 | – |
| 2026-10-05 | 1.6.0 – 1.9.2 | 1.0.0 – 1.0.2 |
| 2026-10-04 | 1.2.0 – 1.5.4 | – |
| 2026-10-03 | 1.0.5 – 1.1.0 | – |
| 2026-10-02 | 1.0.0 – 1.0.4 | – |
| 2026-10-01 | 0.8.0 – 0.9.8 | 0.2.1 – 0.3.0 |
| 2026-09-30 | 0.5.0 – 0.7.1 | 0.2.0 |
| 2026-09-29 | 0.3.0 – 0.4.0 | 0.1.0 – 0.1.1 |
| 2026-09-28 | 0.1.0 – 0.2.0 | – |

## Milestones

| Date | Version | Milestone |
|---|---|---|
| 2026-10-17 | Import 3.17.0 · COMPANION 1.8.0 | Bandcamp view in the companion: a Bandcamp tab follows the dashboard like a Discogs tab – status marks before each part of a credits line (album and track pages), a click on a mark shows its row, a row jumps to its line (from the "about" text: to its sentence), track highlight both ways, status on the MusicBrainz release page; "open in background" and "Load the release there" for Bandcamp too. Rows from track pages link to them |
| 2026-10-17 | Import 3.16.0 | A menu "⚙ Settings" with all settings by topic (General, Sources, Discogs view, Works, Staging, Dates & tracks), each with its own "↺"; the switches stay where they are too. Works of the artists: on or off, how many works and recordings per artist are read (4,000), when a large catalogue is named, and how long the works read are kept – now beyond reloading the page (7 days) |
| 2026-10-17 | Import 3.15.0 | Works matrix: the tracks without a work are compared with all works of the release's artists, its writers and its musicians – works linked to them and works of their recordings (also covers), in the background, read once per session; a large catalogue is named. Pasted texts and Bandcamp credits: credits in sentences ("Music played and recorded by … in September and October 2026"), "Role Name" lines and "… of this release were created by a human" (the release's artists suggested) are recognized. Arrows in the status bar jump to the top or bottom of the dashboard |
| 2026-10-17 | Import 3.12.0 | Rebuilt inside: all mapping rules and word lists in one place of the script (the mapping register), the role rules as plain data; what the script makes of a source stays the same (checked with about 1,200 roles, 100 company roles, 50 date phrases and pasted texts). "Mapping rules" lists the tables and word lists (read only) and shows the right level for 27 rules |
| 2026-10-16 | Import 3.10.0 | The rows of an entry rearrange with the width of the dashboard (relationship above attributes, level above date above tracks), with captions instead of the table head; a date from the pool or the matrix is a chip, its fields open with ✎, begin above end. Dates of the date matrix can be marked "Release level"; a row switched to the release level takes that date. Texts: "tenor & soprano sax", recording place and dates in Bandcamp's "about" text, places with their area, name suggestions without accents and with middle names; supplement with any Discogs or Bandcamp URL |
| 2026-10-13 | Import 3.5.0 · COMPANION 1.7.0 | Supplement with a second source, on request only: another linked source or a pasted text is compared with the rows; what it adds (new roles, new entries) and where it differs is listed to take over by choice, rows it confirms get its mark (variant B). "Delete stored import …" starts the import of a release afresh. The Bandcamp spelling next to the release's artist credit and MusicBrainz. A fresh start: all stored data reset once |
| 2026-10-13 | Import 3.3.0 · COMPANION 1.6.0 | New names: Credits Importer and Credits Importer Companion. Besides Discogs the main script reads Bandcamp albums (credits of the album, optionally of each track page) and pasted texts (booklet, liner notes, a list of musicians); names from there are only suggested. A preference list for physical and digital media decides which linked source is loaded, for digital releases Bandcamp first; a source chosen for a release is remembered |
| 2026-10-12 | Import 3.0.0 | Rebuilt inside: Discogs is read by a source adapter that delivers a neutral list of credits (person with links, role as written, details, tracks, source); the rest of the script works only with that list. Nothing changes for you; it prepares other sources |
| 2026-10-12 | Import 2.19.0 | Suggestions look the same everywhere: dashed and yellow (date matrix, works matrix, “li?”, entries from the Discogs notes not used yet in the pools); “Commissioned By” → commissioned on the works; “Live Recording By” → recording engineer and a hint for “live” |
| 2026-10-12 | Import 2.18.0 | Works matrix in the look of the date matrix and more compact: column heads as cards, roles as chips, attributes (live, cover …) as short forms below each work; track groups can be dropped onto column heads, roles and attributes; track lists from the Discogs notes (“XYZ Publishing (1, 4, 6)”) as suggestions; “live” preselected only on new links |
| 2026-10-12 | Import 2.17.0 | Choose the media before importing a release with several media; attributes (live, cover …) of the recording–work links in the works matrix, “live” preselected on live releases; “Music and lyrics by” → writer with “Song” preselected; the log can sit next to the edit note |
| 2026-10-11 | Import 2.16.0 · COMPANION 1.5.0 | Status marks on every Discogs track line, each with the status of its track; “Directed By” is asked instead of assumed; columns can be taken out of the works matrix; column dates also go onto relationships MusicBrainz has without a date |
| 2026-10-11 | Import 2.14.0 · COMPANION 1.4.4 | Works matrix: a date dropped onto a relationship already in MusicBrainz without a date is added to it (an edit); status marks also for credits of works that were new in the editor |
| 2026-10-11 | Import 2.13.0 · COMPANION 1.4.3 | Track groups by drag & drop onto the tracks of rows; dates and track groups stay in the folded bar; status marks of work credits (composer, publisher) are checked on the works too |
| 2026-10-11 | Import 2.11.0 | After an update, a message shows the milestones of the new version |
| 2026-10-11 | Import 2.10.0 | Pool dates by drag & drop onto rows and onto each other (periods); pools load again from the Discogs notes |
| 2026-10-11 | Import 2.9.0 | The dashboard in the page as an alternative to the window |
| 2026-10-11 | Import 2.8.0 | Date matrix: dates in columns per date group, track groups on dates, applied with one button; "Dates & tracks" folds; all settings back to defaults |
| 2026-10-10 | Import 2.5.0 | Track pool: dates for some tracks, rows split by tracks and dates |
| 2026-10-07 | Import 2.4.0 | Dates found in free text and the Discogs notes, with date rules in the register |
| 2026-10-07 | Import 2.3.0 | Own mapping rules: create, switch any rule on or off, “★ always” from a row, export and import |
| 2026-10-06 | Import 2.0.0 | Central mapping register for all Discogs → MusicBrainz rules, with the "Mapping rules" overview and test field |
| 2026-10-05 | Import 1.9.0 | Role credits added to relationships that already exist in MusicBrainz |
| 2026-10-05 | Import 1.7.0 · COMPANION 1.0.0 | Discogs status marks on the Discogs page and navigation back to the dashboard |
| 2026-10-04 | Import 1.5.0 | Large releases: one medium at a time, loading media in the editor, staging in rounds |
| 2026-10-04 | Import 1.2.0 | Updating what was staged: coming back to the dashboard after "Stage" |
| 2026-10-03 | Import 1.1.0 | New works created in the relationship editor, like "Batch-add new works", together with their writers and publishers |
| 2026-10-02 | Import 1.0.0 | Works matrix, date groups, publisher evidence and Discogs series |
| 2026-10-01 | Import 0.9.0 | Any MusicBrainz entry can be added by hand (artists, labels, places, series, events …) |
| 2026-09-30 | Import 0.7.0 | Relationships already in MusicBrainz are recognised and skipped |
| 2026-09-30 | Import 0.6.0 | Dates in MusicBrainz format with a date pool |
| 2026-09-30 | Import 0.5.0 | "Companies, etc.": labels, studios and other places from Discogs |
| 2026-09-29 | COMPANION 0.1.0 | Discogs view: the Discogs tab shows where each credit comes from |
| 2026-09-29 | Import 0.4.0 | Dashboard in English, German, Spanish and French |
| 2026-09-29 | Import 0.3.0 | Works: linked works checked, existing works found, new works created |
| 2026-09-28 | Import 0.1.0 | First version: the credits of the linked Discogs release in the release relationship editor |

## 2026-10-17

### Import 3.17.0 · COMPANION 1.8.0

#### Added

- **Bandcamp view in the companion** (collected item 4; decisions of the maintainer on 2026-10-17: "gleiche Einstellungen wie die Discogs-Ansicht", marks "nur im Credits-Feld … vor jedem Teil einer Zeile", from the "about" text "nur den Satz markieren", "kein Cover-Kästchen", only `*.bandcamp.com`, marks on track pages too). With Bandcamp as the loaded source, a Bandcamp tab – an album page or a track page – is connected with the dashboard like a Discogs tab:
  - **Status marks** (✓ ● ○ – ! ✗) only in the credits, before each part of a line: "Written by A, mixed by B" gets two marks, "Mixed and mastered by C" two marks at the same place (one for each credit). The "about" text gets none. On a track page only the credits of that track get marks. A click on a mark shows its row in the dashboard ("From Bandcamp: Bob Mix – Mixed By").
  - **Jump to source** (on mouse-over or on click, as set): a row marks its part of the line; a credit of a track page loads that track page; a place from the "about" text marks only its sentence. Texts Bandcamp shortened ("more") are opened first. An entry's head marks all of its lines.
  - **Track highlight** both ways: a track of the works matrix highlights its line in Bandcamp's track list, the pointer on a track there its row in the works matrix.
  - **Status on the release page:** after "Enter edit" the MusicBrainz release page checks the staged credits – ✓ or ✗ on Bandcamp, as on Discogs.
  - **In the dashboard:** rows from track pages say "From the track page: 2" with a link to it; places from the "about" text say "From the “about” text".
- **"open in background" and "Load the release there" for Bandcamp** (collected item 7): without a Bandcamp tab the album opens in a background tab; a Bandcamp tab on another page loads the album.

#### Changed

- The texts of the view name the site of the loaded source ("Bandcamp view: connected", "Bandcamp status", "From Bandcamp: …"); with Discogs they are as before. The settings topic is called "Discogs and Bandcamp view"; the switch "Artwork" is only shown for Discogs.
- An older companion (before 1.8.0) only connects Discogs: with Bandcamp loaded, the view says "needs the companion script 1.8.0 or later".
- COMPANION 1.8.0 runs on `*.bandcamp.com` too (the script manager asks once); every tab reports its site, and the dashboard's commands go to a tab of the loaded source's site; Bandcamp pages may be opened in the background.

#### Fixed

- A company named on two track pages (e.g. "Recorded at Studio X" on the pages of tracks 1 and 3) is one row for both tracks again – since 3.16.1 only the tracks of its first place were taken.
- COMPANION: on a Discogs (or Bandcamp) page just loaded, the status marks could fall back to an older state a second or two later – the status stored when the page opened replaced a newer one that had arrived meanwhile (found with the Bandcamp test: ✓ after "Enter edit" turned back into ○).


### Import 3.16.2

#### Changed

- **Texts that named Discogs say "the source" when another source is loaded** (collected on 2026-10-17, as "Mapping rules" in 3.13.2): the question for an instrument ("The source (pasted text) only says “Guitar”. Do you know which one it is?"), "The source (Bandcamp) names no writers for this track", the tag of a role credit taken over ("from the source", tooltip "Taken from the source (pasted text)"), the empty works matrix, "What was imported from the source (…)", "↻ load again from the source (…)", the dates "as the source gives them". With Discogs loaded they are as before. The placeholder of "Add entry manually" says "a role as the source writes it" for every source.


### Import 3.16.1

#### Added

- **"Leave out the “about” text"** – a checkbox next to "Delete stored import …", for a Bandcamp release with an "about" text (asked for by the maintainer: "eine Checkbox … um den about-Text zu ignorieren, die direkt wirkt", "nur für dieses Release"). Ticked, the places from the "about" text are hidden (their rows go to "Skip" and out of sight) and its dates leave the date pool and the date matrix – at once, without a new import; the credits field is not touched. Ticked off again, everything is back as it was, with what you changed in those rows; the dates come back from where they were kept. The choice is stored for the release (also after loading the page again) and reset by "Delete stored import". The log says what was left out ("“about” text left out (rows hidden: 1, dates out of the pool: 2)").


### Import 3.16.0

#### Added

- **A menu "⚙ Settings"** in the head of the dashboard (next to "↺ Defaults"; asked for by the maintainer: "ein aufklappbares Einstellungsmenü mit verschiedenen Themen"). All settings in one place, by topic, each topic folded and with its own **"↺ Defaults of this topic"** (after a question):
  - **General:** language, text size, the dashboard as a window or in the page, show the log, place of the log.
  - **Sources:** the order of the sources (physical / digital media), the credits of the Bandcamp track pages.
  - **Discogs view:** jump to source on mouse-over or click, Discogs status, track highlight, status on the release page, artwork.
  - **Works:** the comparison with the works of the artists (new settings, below), the role codes, the attributes spelled out.
  - **Staging:** role credits for existing relationships, staging in rounds and – new – how many relationships per round (50 – 2,000, default 500).
  - **Dates & tracks:** apply automatically, keep the pools in the bar.

  The switches stay where they are too (the menu was asked for "erstmal zusätzlich"); a switch changed in one place shows the same in the other.
- **Settings of the comparison with the works of the artists** (topic "Works"): on or off; at most so many works and recordings per artist, **together** (100 – 10,000, default **4,000**; the menu shows what it costs: "= 40 requests, about 44 s per artist"); a large catalogue is named after so many seconds (default 10) and from so many entries to read (default 900); the works read are kept so many days (1 – 90, default 7).
- **The works read are kept beyond reloading the page** (in the browser's IndexedDB of musicbrainz.org, per artist, with the day they were read): loaded again within the days of the setting, the artist is not asked again – the log says "Works of Test Band: 1 work from the store (read 2026-10-17)". Works read with a lower limit than the one set now are read again. A work chosen for a track ("Link") or created through the dashboard goes into the stored works of the artists credited on that track at once. **Clear the stored works** (topic "Works", after a question with the number of artists) empties the store; "↺ Defaults" does too. Without IndexedDB (a browser that does not allow it) the works are kept for the page only, as before.

#### Changed

- The limit counts the works linked to an artist and the works of its recordings together: the linked works first, the recordings with the rest (3.15.0: up to 2,000 of each).

#### Fixed

- The linked works of an artist with more than 2,000 of them were cut off without a word; now the message names the limit for works too ("… has 4,500 works and recordings; only the first 4,000 were compared with the tracks").


### Import 3.15.3

#### Changed

- **The suggestions are a block below the head line of the entry** (asked for by the maintainer: "sie können nebeneinander und untereinander dargestellt werden"): the red mark, the field and the buttons stay in one line; below them the suggestions lie side by side and wrap into more lines when there are many or the dashboard is narrow. In 3.15.2 they were one per line. Five, then "+ n more", tooltips and marks as in 3.15.2.


### Import 3.15.2

#### Changed

- **Suggestions right below the red mark, stacked:** an entry without a match shows its red mark ("not assigned yet …"), directly below it the suggestions one per line, and next to them the field and the buttons. The explanations ("Same name in MusicBrainz …", "Suggestion from a Discogs alias", "Found via the Bandcamp link, but spelled differently …", "The text names no one here …") are tooltips now, of the stack and of each suggestion. Where the reason matters, a short mark stays on the suggestion: "similar name", "via Discogs alias …", new **"spelled differently"** and **"release artist"**. Five suggestions are shown; the rest is behind a clearly visible **"+ n more"** (a button of its own, bold with a solid frame), which turns into "− fewer". All hits of the name search are kept now (up to 25; before, only 5).
- **The rows of an entry are boxes** (variant B): each row has a frame, a gap to the next and a stripe on the left in the colour of the entry's kind; every second row is tinted in that colour. An open track list belongs to the box of its row. Before, every second row was tinted so lightly that the rows were hard to tell apart.

#### Fixed

- In a wide dashboard the columns of the rows of an entry did not line up: the column "Level" took the width of its buttons ("Recording · Skip" or "Recording · Release · Skip"). It has a fixed width now.


### Import 3.15.1

#### Changed

- **Mastering only on the release level, as MusicBrainz has it** (on recordings the type is deprecated – "Please add mastering engineers at the release level" – and "mastered at" does not exist there). In the date matrix the columns **Mastering** and **Remastering** have no checkbox "Release level" any more: every date of these columns goes to the mastering rows, also a date with a track group. A track group now only says which mastering row a date belongs to – CD 1 mastered by X in May, CD 2 by Y in June: X takes May, Y June; a date without a group goes to all mastering rows. Before, a mastering date with a track group reached a release-level row only after ticking "Release level". The column ℗/© keeps the checkbox (℗ can be on recordings or the release).
- A row that MusicBrainz allows on one level only shows that on mouse-over of its level ("MusicBrainz has this relationship only on this level (Release)").
- **Special purpose artists are left out of the comparison with the works of the artists:** Various Artists, [unknown], [anonymous], [traditional], [no artist], [data], [dialogue], [Disney], [theatre], [church chimes], [language instruction] and MusicBrainz Test Artist (their MBIDs, checked on MusicBrainz's page "Special purpose artist"), and any name entirely in square brackets ("[soundtrack]"). Their catalogues are huge and say nothing about a release. The log says so once per import ("Various Artists: a special purpose artist … – its works are not compared"); the list is table T026 in "Mapping rules".

#### Fixed

- A work found by the comparison with the works of the artists (background) does not draw the works matrix anew while something is dragged (a track group, a date) – the drop would be lost; it is drawn a moment after the drop.


### Import 3.15.0

#### Added

- **Existing works of the artists in the works matrix** (asked for with the release "Invisible Places": "alle Werke, die der Artist schon einmal verknüpft hat, also auch Cover"). The tracks without a work are compared with all works of
  - the release's artists (its artist credit),
  - the writers of the tracks (composer, lyricist, writer … with an MB artist),
  - its musicians (instrument, vocal, performer rows with an MB artist),

  in this order: the works linked to the artist (every artist–work relationship) and the works of the artist's recordings – so a cover the artist recorded before is found too. A work with the title of a track (or an alias; one letter may differ, digits must match, as with the same-named works) is listed under the track, with where it comes from: "work of Test Band", "recorded by Bass Man ("Song Three (live)")". It is linked with "Link" like a work found by the search; nothing is linked by itself, and a track with such a work is not planned as a new work by "＋ New work" for all tracks.
- **In the background:** the works are read while the dashboard's own requests (search, checks) are not waiting, one request a second as MusicBrainz asks; once per artist and session (a second import, e.g. a pasted text after Discogs, compares again without asking MusicBrainz again). A new name assigned later (a suggestion, an alias, a URL) is compared a moment later.
- **A large catalogue:** when one artist takes longer than 10 seconds because more than 900 works or recordings are to be read, a message says why ("… takes a while: a large catalogue (2500 recordings, 900 read so far). It goes on in the background."). At most 2,000 recordings are read per artist; a message says so. The log names the works read of each artist and the result ("Works of the artists compared: 3 works with the same title as a track (1.2, 1.3, 1.4)"). The works matrix is drawn anew only when something new was found, and not while you type in one of its fields (then once you leave it).

#### Changed

- The heading of the list says where the works come from: "… by these writers" when only the writers' search found them, "(of the writers, the release's artists or its musicians)" when the comparison found some. The question before "＋ New work" for a track with such a work no longer says "by these writers".

### Import 3.14.1

#### Added

- **Two arrows in the status bar** (bottom of the dashboard): ▲ jumps to the top, ▼ to the bottom – of the window in the window, of the page in the page.

### Import 3.14.0

#### Added

- **Rules for free credits texts, for every source** (a pasted text, Bandcamp's credits; found with the credits of the album "Invisible Places", but meant for any text):
  - **Credits in sentences:** "Music played and recorded by X in September and October 2026." → X: played by (performer) and recorded by (recording engineer); "Mixed and mastered by X in October 2026." → mixed by, mastered by. Words that only say what was done ("Music", "Songs", "The album" … before the verb) are left out of the role (T021); the time after a name ("in October 2026", "during the summer of 1980") is cut off the name (T020) – the date goes into the date pool. Only the first sentence of a line counts for the name.
  - **Two months of one year** are one period: "September and October 2026", "Sept/Oct 2026", "septiembre y octubre de 2026" → 2026-09 – 2026-10 (date rule D007).
  - **"Role Name" without a separator:** "Photography Tom Barrett", "mastering john doe" (names in small letters too) – when the line gives nothing else: a role of 1–3 words that the register knows, then a name of 2–4 words without words like "the", "of", "this", "release" (T025).
  - **"… were created by a human":** "Music and artwork of this release were entirely created by a (cat assisted) human." names roles (the words before "of this release" and the verb, T022) but no one: for "a human", "me", "us", "the band", "the artist", "himself" … (T023) the release's artists are offered, as an entry of its own with a suggestion ("The text names no one here ("a human") – the release's artist? A suggestion, check before assigning"). Nothing is assigned by itself.
  - **The label line is left out:** "An Echo Elberfeld release.", "Released on X Records" (T024) – the label is set in the release editor; ℗ and © lines stay credits.
  - "played by" maps to performer (rule R060).
- The new word lists T020 – T025 are shown in "Mapping rules" (Tables and word lists).

### Import 3.13.2

#### Changed

- **"Mapping rules" names Discogs only while Discogs is the loaded source.** With Bandcamp, a pasted text or no source it says "Try a role:", "Role", "Role → MusicBrainz", "Spelling → MB instrument", "Role (without details)", "Spelling", and the hint asks for a role "as the source writes it" ("Bass [Upright]" or "tenor sax"). The rules are the same for every source. An open window follows when another source is loaded.

### Import 3.13.1

#### Fixed

- **What follows "at" without being a place gives no entry:** "recorded at the same time as …", "mixed at last", "at night", "at the end of the session", "at first" (new word list T019 in the register, shown in "Mapping rules"). "first" and "last" count only alone or before a word of time ("first week", "last day"), so "First Avenue, Minneapolis" stays a place; "The End Studios" and "All Saints Church" stay places too. Place names in small letters are still read ("recorded at loft in cologne"). A date in such a line still goes into the date pool; the line is listed as not recognized (in Bandcamp's "about" text it is passed over).

### Import 3.13.0

#### Added

- **Name suggestions for names with an initial:** MusicBrainz's search needs every word of a name, and "T" is no word of "Torben" – so a name with an initial is also searched with its written-out words. "T. Snekkestad" finds "Torben Snekkestad", "Barry J. Guy" finds "Barry John Guy", "T. J. Snekkestad" would find "Torben Jon Snekkestad" – each marked "similar name". The initials must fit the first and middle names in their order ("K. Tanaka" finds "Kenji Tanaka", not "Hiro Tanaka"). One more request per such name; nothing is assigned by itself.

### Import 3.12.1

#### Fixed

- **"n lines not recognized" could not be opened** in the window (it could "in the page"): the source sits in the head of the window, with which the window is moved, and a press on the list started moving the window instead. Reported with the Bandcamp album "Invisible Places" (phelios).
- **The works matrix found no existing works after a second import:** the same-named works of the import before stayed, and the tracks of the new source were never searched – e.g. Discogs loaded first, then Bandcamp or a pasted text chosen. A new import searches anew.
- **Same-named works are looked up again when the writers of a track change:** a name of Bandcamp or a text is only a suggestion at the import, so its tracks had no writers and nothing was searched; after you assigned the name (a suggestion, an alias, a URL, a new artist), nothing was searched either. Now the tracks whose writers changed are searched again a moment later; the log says so ("The writers of 2 tracks changed – their same-named works are looked up again").

### Import 3.12.0

#### Changed

- **The role rules are plain data** (asked for by the maintainer: "das Mapping-Register soll an einem Ort zusammengelegt werden"). Each rule R001 … is one line of a table: its pattern, the MusicBrainz types and level it leads to, and what goes with it (a credit on the works, checkboxes, the role as role credit, an instrument or vocal). Only the rules that need more – 25 special rules and 5 simple ones (e.g. "A&R Consultant" → task "consultant") – have code. Before, the pattern of each simple rule was written twice, once for "Mapping rules" and once for the mapping itself.
- What the script makes of a source is the same as in 3.10.0. A new test checks it: about 1,200 roles as Discogs writes them, 100 company roles, 50 date phrases and pasted texts give exactly the same results.

#### Fixed

- **"Mapping rules" showed the wrong level for 27 rules**, because what it showed and what the rule did were written separately: "Written-By", "Composed By", "Lyrics By", "Translated By", "Libretto By" said "recording" but go onto the works; artwork, photography, design, illustration, art direction, liner notes, booklet editor, video and audio director, booking, legal representation, copyright, phonographic copyright, publishing and licensor said "recording" but go onto the release; "A&R" goes onto the release group; the design rules R064–R067 (sleeve, lithography, cover concept, cover design) listed no type. The mapping itself was always right; only the overview was wrong.

### Import 3.11.0

#### Changed

- **The mapping register in one place:** every rule and word list the sources are read with is now one section of the script (section 2, before the sources): the role notation, your own rules and switched-off rules, the rule lists (W, S, Q, C, R), the tables and word lists, the functions that apply them, and the dates (D). Before, parts of it were spread over the script – the word lists of pasted texts in the text adapter, the date groups next to the date matrix, "live" in titles in the works matrix, roles in the notes next to the publisher evidence. Nothing changes in what the script does.
- The word lists got ids, T005 … T018: details that tick checkboxes (T005), words that are no role credit (T006), fixed role credits (T007), engineer tasks (T008), the separators of texts (T009), track words (T010), instrument prefixes such as tenor, soprano, acoustic (T011), private places (T012), company roles of texts (T013), month names and ordinal words (T014), words that name a date group (T015), the date groups (T016), "live" in titles (T017), roles in the notes (T018).

#### Added

- **"Mapping rules" lists the tables and word lists** in a new section **Tables and word lists (read only)**: T003 and T005 … T018 with what they hold – a list of words, pairs, or the pattern as the script uses it. They cannot be switched off; they change with an update of the script.

## 2026-10-16

### Import 3.10.0

#### Added

- **Release level in the date matrix:** every date of the date matrix has a checkbox **Release level** (next to its track groups). A date marked so is only for rows on the release level (release, release group); rows on recordings and works take the other dates of the column. Example: the performance dates of the studio days (March) and of a release concert (June) in one column, June marked "Release level" – "Apply" gives the instrument rows on recordings the March dates and a row on the release level the June date.
- **Switching the level takes the matching matrix date:** a row whose date came from the matrix and that is switched to the release level gets the date marked "Release level" of its column at once; switched back to recordings, the dates of its tracks again. The log says so ("Bass Man: new level – date from the matrix column Performance: …"). A date entered by hand stays.
- The mark is stored with the matrix (`dci-date-matrix:<release>`, field `rel` of a cell).

### Import 3.9.0

#### Changed

- **The rows of an entry rearrange with the width of the dashboard** (as in the mockup of 2026-10-16):
  - From about 1150 px wide: everything in one line, as before.
  - Narrower: three columns – role | MusicBrainz relationship above attributes & credits | level above date above tracks.
  - Below about 700 px: two columns, below about 460 px: one.
  - It follows the width of the dashboard (window or in the page), not of the screen; widening it rearranges the rows again.
- **Captions instead of the table head:** each field has its caption above it ("MB relationship", "Attributes & credits", "Level", "Date", "Tracks"), a little bolder and darker than before; the table head is gone.
- **A date from the pool or the date matrix is a compact chip** ("Performance 1 · 2001-03-01 – 2001-03-03"), with "from the matrix" or "from the date pool" below it. **✎** opens its fields, **done** closes them again, **✕** removes the date.
- **Begin and end exactly one above the other:** the open date fields are a grid with "Begin" and "End" in front – year above year, month above month, day above day.

### Import 3.8.0

#### Added

- **Supplement with a source the release does not link to:** next to the buttons of "Supplement with" a field for any Discogs release (URL or ID) or Bandcamp album URL, with **Supplement**. It works like a linked source; while loaded it shows as "Bandcamp … ✓ supplemented" with "remove". The source loaded already is refused ("That is the source loaded already."). Enter in the field loads it too.

### Import 3.7.0

#### Added

- **Recording place and dates in Bandcamp's "about" text:** "recorded at Loft in Cologne, june 16/17 2018" gives an entry **Loft** (Cologne) with "Recorded At", and the dates go into the date pool as a period (2018-06-16 – 2018-06-17) that can be split into the single days. Only the places of the about text are taken (roles ending in "at"); its prose is neither read as credits nor listed as not recognized. A private place is no place: "recorded at home", "at home in Oslo", "at my place", "in their living room" give no entry.
- **Places with their area:** "Loft, Cologne" and "Loft in Cologne" (in a text and in Bandcamp credits) are the place "Loft" in the area "Cologne". MusicBrainz places of that name are suggested only in that area (a "Loft" in New York is not), with the area next to the name; the entry shows the area too ("Loft (Cologne)"). A company with an area is always a place (not a label).
- **More date forms:** "june 16/17 2018" and "16/17 June 2018" (two days with "/") like "June 16 & 17, 2018".

### Import 3.6.0

#### Added

- **A shared instrument word:** "tenor & soprano sax, trumpet and clarinet" → tenor saxophone, soprano saxophone, trumpet, clarinet. The noun after the last word goes to the words before when they only name a kind of the instrument (tenor, soprano, alto, baritone, acoustic, electric, fretless, upright …): "acoustic & electric guitar" → acoustic guitar, electric guitar; "bass & electric guitar" stays bass and electric guitar.
- **Lists with an unknown part:** "Barry Guy – double bass, sticks-and-stones" takes double bass and lists the line as not recognized with the part it does not know ("→ ? “sticks-and-stones”"). "and" separates only as a word between spaces ("sticks-and-stones" stays one).

#### Changed

- **Name suggestions are more flexible:**
  - Accents, case and punctuation do not count: "Agusti Fernández" finds "Agustí Fernández" (same name).
  - A middle name or an initial more or less is a **similar name**: "Barry Guy" finds "Barry John Guy" (and an initial such as "Barry J. Guy" counts as well). Similar names come after same names and are marked "similar name" (a check before assigning).
  - Names are searched by their words (aliases too), up to 25 hits, the best 5 shown. Nothing is assigned by itself.

### Import 3.5.1

#### Fixed

- **"Window / in the page" could not be switched** before the dashboard was open: the switch stayed on "window". It changes the launcher at once now.

## 2026-10-13

### Import 3.5.0

#### Added

- **Supplement with a second source** (stage 2, variant B of the mockup). The dashboard still imports one source; a second one only supplements it, and only on request, one after another:
  - **Supplement with** below the source: a button per other linked source ("＋ Bandcamp …", "＋ Discogs …") and "＋ Text …" (a pasted text, with "Read text and supplement"). Nothing is read before the click.
  - The second source is compared with the rows, row by row: the same entry (the same MusicBrainz entry, else the same name – case, accents and punctuation do not count), the same MusicBrainz relationship and instrument or vocal, the same tracks.
  - **The same:** the row gets the mark of the second source next to the mark of its own (**DG BC**).
  - **Only in the second source:** a suggestion in the list **Supplements from …**: a **new role** of an entry, or a **new entry** (with what MusicBrainz has for it: via its link, or entries of the same name – only shown).
  - **Different tracks:** **differs**, with both track lists; until chosen the loaded source stays (row mark "BC ≠").
  - Lines of a text that gave no credit: **not recognized**.
  - A checkbox per suggestion (new roles and entries ticked, "differs" not), **select all**, **Take over selected**, **Discard all**. What is taken over goes into the entries with its mark (BC); new entries are looked up as the second source looks them up (Bandcamp: rule 4, names as suggestions). "differs", when ticked, gives the row the tracks of the second source.
  - **remove** ends the supplement; what was taken over stays. A new import of the main source starts without supplements. Nothing of a supplement is stored.
  - Edit note: "Also from: <URL>" below "Source:", and after "Done" what the second source confirmed, what was added from it only and where the sources differ (only rows with a MusicBrainz entry).
  - The text source remembers the line each credit comes from ("Bandcamp says" in the list).

### Import 3.4.0 · COMPANION 1.7.0

#### Added

- **Delete stored import …** next to the source: after a question, forgets what the script stored for the import of this release – date pool, track pool and date matrix, the source chosen for it, its media choice, the supplements, its log and, with the companion, its status marks – and imports the source anew, as the first time. What is staged in the relationship editor stays, and so does the safety list of created works.
- COMPANION 1.7.0: "Delete stored import" also deletes the status of that release kept for the release page.

#### Changed

- **A fresh start** (asked for by the maintainer): the storage generation goes up to 4. With the update all stored settings and data of the main script are cleared once – this time the safety list of created works too – and the companion clears its shared storage and the cover box settings on Discogs. The update notice says so.

### Import 3.3.2

#### Added

- **Spelling check for Bandcamp:** an entry found through its Bandcamp link shows its name on Bandcamp, in the release's artist credit (below the title) and in MusicBrainz side by side; spellings that differ from Bandcamp's are underlined and the line is yellow and dashed ("differs – please check: spelling on the artwork, a typo, or does MusicBrainz name it differently?"). It replaces "No alternative spelling on Bandcamp".
- **The old script on the same page:** if "MB x Vibecode: Import Discogs credits" (or a second copy) runs too, a note above the import button says so and asks to delete it; the new script stays out when the old one started first.

#### Changed

- Entries keep the source they came from (for their link and the "by name" note).

### Import 3.3.1 · COMPANION 1.6.1

#### Changed

- **New file names**, so everybody installs anew: `mb-vibecode-credits-importer.user.js` and `mb-vibecode-credits-importer-companion.user.js` (READMEs and this changelog as `mb-vibecode-credits-importer-…`). The old files `mb-discogs-credits-import.user.js` and `mb-discogs-credits-sync.user.js` get no more updates; delete the old scripts in the script manager, because the old and the new main script would both put a dashboard on the page. Settings, pools, rules and the list of created works stay (no reset).
- Rule 4 for Bandcamp names: the band found through its Bandcamp link is compared with the **release's artist credit** (the name below the release title), not with the name of the MusicBrainz artist. "Test Band" on Bandcamp, "The Test Band" in MusicBrainz, credited "Test Band" on the release: assigned. Credited differently, or not part of the release's artist credit: a suggestion. The release is read with its artist credit for this (`inc=artist-credits`). Companies (labels found through a Bandcamp link) are still compared with their MusicBrainz name.
- A suggestion found through a link says so: "Found via the Bandcamp link, but spelled differently (how the release names it) – a suggestion …" instead of "Same name in MusicBrainz"; the log says "the release names it differently in its artist credit (…)".

### Import 3.3.0 · COMPANION 1.6.0

#### Added

- **Bandcamp as a source** (E2). The main script reads it itself; the companion is not needed for it.
  - Found through any link of the release to a Bandcamp album page (purchase for download, streaming …); another album can be entered in the source field (`https://artist.bandcamp.com/album/name`).
  - The page is loaded with `GM_xmlhttpRequest` (new permissions: `@grant GM_xmlhttpRequest`, `@connect bandcamp.com`; the script manager asks once). The script reads the album data Bandcamp puts into the page: title, track list, the credits text and the "about" text.
  - The credits text is read like a pasted text (see 3.2.0). With **Read the credits of the track pages too** (on by default) each track page is loaded as well; its credits count only for that track, and its lines that are not understood are listed with the track number.
  - Rule 4 for names: only the band itself has a link (its Bandcamp page). A MusicBrainz artist found through that link is assigned only when MusicBrainz spells it exactly as Bandcamp does; otherwise it is a suggestion and the log says "MusicBrainz spells it differently". Every other name is found by name and suggested.
  - The edit note names the album page as its source ("Source: https://…bandcamp.com/album/…", "from Bandcamp (…)").
- **Order of the sources**: a small foldable list under the source field, one for physical media and one for digital media (a release counts as digital when all its media are "Digital Media"). Drag & drop or ▲▼ change the order; the list that applies to this release is marked "(this release)". The first source in the list that the release links to is loaded. Defaults: physical Discogs, Bandcamp; digital Bandcamp, Discogs. Remembered in `dci-source-order`.
- A source chosen for a release by hand (in the picker or the field) is remembered for that release and comes before the list (`dci-source-pick`, the last 200 releases); the log says so.
- **Bandcamp menu** (foldable, under the source field): the switch for the track pages (`dci-bc-tracks`), and **Test page** – loads a Bandcamp album URL and says what it found ("Read: “Title”, 9 tracks, 12 lines of credits, 9 track pages (via GM_xmlhttpRequest)"), for checking whether Bandcamp can be reached from the browser at all.
- "↺ Defaults" also resets the order of the sources, the chosen sources and the track pages switch.

#### Changed

- The source picker lists every linked source ("Discogs 1234", "Bandcamp artist.bandcamp.com/album/name"); without a link: "This release is not linked to Discogs or Bandcamp yet. Enter a URL above or paste a text."
- Texts that named Discogs as the source name the loaded source now (role column, "whole release", the reasons in the matrices, messages, the log).
- COMPANION 1.6.0: only the new name (see 3.1.0). It shows Discogs releases only; with Bandcamp or a text as the source it stays idle.

### Import 3.2.0

#### Added

- **Credits from a pasted text** (E1): **Paste text …** under the source field opens a field for the text and one for where it is from (booklet, a URL …, for the edit note); **Read text** makes it the source of the dashboard. It understands one credit per line:
  - "Name – guitar, vocals", "Name: bass, vocals", "Name (roles)"; "Guitar: Name, Name"; roles from the mapping register, in the same notation as Discogs ("Arranged By [Strings]").
  - "Written by A, mixed by B" (two clauses in one line), "Mixed and mastered by X", "Strings arranged by Z" (→ "Arranged By [Strings]"), "Music and lyrics by Y".
  - Places: "Recorded live at Place, City, 12 May 2019 by Name" (a person and the place), "Mastered by A at Studio", "Recorded 12–14 May 2019 at Studio X".
  - Tracks: "Tracks 3–5: …", "… (tracks 1, 4)", "… on track 2", "… (1, 3)" – only when they name tracks of this release (the MusicBrainz tracks); otherwise the line is for the whole release.
  - "℗ 2019 Label" and "© 2019 Label"; companies such as "Published by X" with their tracks (they reach the works matrix like track lists in the notes, S022).
  - Lines without credits are listed under the source as "n lines not recognized", to add by hand or to rewrite and read again.
- Names from a text have no links. The script looks for the same name in MusicBrainz (artists, labels, places; also aliases) and offers the hits as suggestions (dashed and yellow); a click assigns one. Nothing is assigned by itself.
- Edit note: "Source: <where it is from>" and "… from a pasted text (…)".

#### Changed

- Track lists in the text are read with the credits, not again as notes (S022).
- The personal publisher evidence (S014) leaves a company alone that the source gives for some tracks only.

### Import 3.1.0 · COMPANION 1.6.0

#### Changed

- New names: **MB x Vibecode: Credits Importer** (before: "Import Discogs credits") and **MB x Vibecode: Credits Importer Companion** (before: "… COMPANION"). The dashboard title, the button ("Import credits …"), the edit notes and the message after an update use them.
- Script managers know a script by its name: the new version may be installed next to the old one. Then delete the old scripts once. Settings, pools, rules and the list of created works stay (they are stored in the browser, not in the script); the companion keeps the place of its cover box, and the status marks of the last releases come back when their dashboards are opened again. No reset.

## 2026-10-12

### Import 3.0.0

#### Changed

- Built in two parts (no visible change, no reset: settings, pools, rules and the list of created works stay):
  - **Source adapter (Discogs):** the only part that reads Discogs – its API (releases, artists, labels), its JSON, its URLs, numbered names ("Name (2)"), headings and index tracks, track specifications ("A1 to A3"), the parent label of a series, aliases, members and groups of an artist. It delivers a **neutral release**: tracks; credits as "who (id, name, name as written, links) – role as written with role and details – name as credited – tracks (whole release, a list with what could not be resolved, or one track)"; companies with catalog number; series; notes and format words.
  - **Core:** everything else works with the neutral release only – entries and rows (grouping per person, engineer tasks split by S018), finding MB entries through the links (also through aliases), dates and the date matrix, track lists in the notes, "live", series, the forms for new artists, labels, series and works, edit notes, the release picker, the Discogs tab of the companion.
- Checked against 2.19.1: the same entries, roles, tracks and companies for the test releases; all browser tests give the same results, also with data stored by 2.19.1.

### Import 2.19.1

#### Changed

- "li?" and the preselected "live" say more exactly why when a track is a live recording: "Live recording – Discogs credits “Live Recording By” (Name) for this track" (or "for the whole release" when the credit names no tracks), with the Discogs role as written ("Recorded Live By" …) and the name. A track title saying live is a live recording too. "Live release" stays for the release group, the format and the notes.

### Import 2.19.0

#### Added

- "Commissioned By" → the work relationship commissioned ("was commissioned by"), for persons (rule R099) and labels (companies, rule C037), as a column of the works matrix. Without tracks it is a suggestion on every work (rule S024; × takes it out of a work, ✓ keeps it, the rest is staged); with tracks it is set on the works of those tracks. The cells say why. "Commissioned by X (2)" in the Discogs notes works like the other track lists (S022). "Funded By" stays as it was.
- "Live Recording By" (also "Live Recording", "Live Recorded By", "Recorded Live By", "Live Recording Engineer", "Engineer [Live Recording]") → recording (recording engineer) on the recording level, without role credit (R031, W007). It is a hint for "live" (S021): preselected only on the new links of its tracks (the whole release when it names no tracks); a link already in MusicBrainz is only offered "li?".
- Dates and track groups from the Discogs notes are suggestions in the pools until they are used: dropped onto a row, the matrix or a date, or placed by hand (the dates also when a row uses them). "Load again from Discogs" makes them suggestions again.
- Every column of the works matrix with suggested cells counts them in its head ("4 suggestions"), not only publishers.

#### Changed

- One look for all suggestions: yellow with an amber dashed border, the coloured left edge stays (date matrix purple, works matrix blue). This covers the suggested dates in the date matrix, the suggested cells of the works matrix (publisher evidence, Discogs notes, "Commissioned By"), the offered "li?" and the unused entries from the Discogs notes in the pools. The help of the date matrix and the messages say "dashed and yellow".
- What is dashed but no suggestion looks different now: "some works have it" in "Attributes for all" is half filled; "… waits for a work" is grey dotted. Dashed outlines while dragging stay.
- "Commissioned By" is no longer "miscellaneous support" (R095).

### Import 2.18.0

#### Added

- Track lists in the Discogs notes (rule S022): "XYZ Publishing (1, 4, 6)", "Published by X (tracks 1–3)", "Written by Y (2, 5)", "Tracks 1, 4 & 6 published by Z" become track groups in the pool; when the name is an entry of the dashboard, its work-level roles get these tracks as suggestions, ahead of the personal publisher evidence. Names are compared generously (case, accents, spaces, hyphens, punctuation, "&"/"and", Ltd./GmbH/Inc. …, one typo; as a last step without generic words like Publishing, Music, Verlag – marked "similar name"). Credits Discogs gives on these tracks already are left alone; names that are no entry only give the track group.
- Track groups dropped onto the works matrix (rule S023): onto a column head (all its roles only for the works of the group's tracks), onto one role in the head, or onto an attribute in the head of the first column; Shift adds instead. MusicBrainz's own relationships and attributes stay.
- Suggested cells (publisher evidence, Discogs notes) are dashed, with ✓ (keep) and × (take out).
- "Spell out" in the head of the works matrix: the attribute names instead of the short forms (remembered, `dci-wattr-long`; "↺ Defaults" sets it back). "Open all rows" opens the attributes of every work.

#### Changed

- Works matrix in the look of the date matrix, much more compact:
  - Column heads are cards: name and ▾ (menu) « (fold) ✕ (take out); the roles as chips with the number of works; the column date as a date chip; "credited as" stays visible. The column date fields, "all works" and the publisher tools ("for all works", "check evidence", personal publishers to add as a column) are in the ▾ menu, which closes with a click elsewhere. A pool date dropped onto the head sets the column date.
  - Cells show the roles as chips: green with a lock – in MusicBrainz; solid – planned; dashed – suggested; grey dashed – waits for a work; an empty cell a dotted "+".
  - The first column: the track in one line (Discogs position on the right), the work in the next (linked, new, found – or ＋ New work · Search · via form … with ⓘ for the search result); the work type and languages of a new work in short ("▸ Song · English"), opened with a click.
- Attributes of the links recording → work as two-letter short forms below each work (ac, co, de, in, ka, li, me, pa) instead of checkboxes. A work with an attribute (in MusicBrainz, set, preselected or offered) always shows them all; one without any is closed ("none ▸ Attributes"). "Attributes for all" in the head of the first column (dashed: some works have it).
- "live" (rule S021) is preselected only on new links (a new work, or a work linked here). Links that exist in MusicBrainz keep their attributes – live albums often have studio tracks; "live" is only offered there ("li?").
- Publisher evidence (personal publisher, S014) ticks its works as suggestions (dashed) instead of plain ticks.

### Import 2.17.0

#### Added

- Media choice before every import of a release with several media: a button per medium, All / None and a text field ("1-4, 5, 8") that follow each other, and "Also import relationships on the release level (release and release group)". Only the credits of the chosen media come in; credits without track information go onto their tracks; release and release group credits only with the checkbox. The works matrix, the dates from the Discogs notes, the track pool's media and the medium list cover only the chosen media. "Remember this choice for this release" preselects it next time (still asked); "Choose media …" in the toolbar asks again and imports anew after a confirmation. All media with the release level (preselected) is the import as before.
- Works matrix: attributes of the link between recording and work (live, cover, medley, partial, instrumental … – those MusicBrainz offers), per row and "all:" in the head. Planned links get them when staged; for links already in MusicBrainz an attribute ticked here is added to the link (an edit, ✎, ✎✓ once staged; edit note line "added attributes (live, cover …) to … existing links").
- "live" preselected on the links (rule S021): for all of them when the release group is Live in MusicBrainz, a Discogs format says Live or the notes say "recorded live"; for one when its track title says so ("(Live)", "[Live]", "(Live at …)", "– Live"). Shown with the reason; unticking takes it back.
- "Music And Lyrics By", "Words And Music By", "Songs By" and the like → writer (rule R098); the column head of the works matrix says "Music and lyrics in one credit: MusicBrainz “writer”" with R098. New works get the type "Song" preselected (rule S020) – for all new works when the credit is for the whole release, otherwise for its tracks; a type chosen by hand stays.
- "Bass Guitar" asks bass guitar · electric bass guitar · acoustic bass guitar (question Q004); without a choice it stays bass guitar.
- The log can sit in the page next to MusicBrainz's edit note: "Place:" in the log's head – window (default), left of / right of the edit note (the edit note keeps its place and gets the rest of its width, the log takes its height) or above it (height can be dragged, remembered). Too narrow beside it → above, with a note. Remembered; "↺ Defaults" sets it back.
- "n rows incomplete" in the summary: ‹ and › (or a click on the count) jump through the incomplete rows ("1/2") and light up what is missing (artist match, type, date or instrument).
- Copyright dates written "©©" on Discogs (rule D015): "©© Fuzzoramarecords 2005" → ℗/© 2005.

#### Changed

- Instrument questions (Q001 "Bass", Q002 "Guitar", Q004 "Bass Guitar"): without a choice the row has no role credit any more – it would only repeat the instrument. With a choice the Discogs word stays the role credit ("electric bass guitar" credited as "bass").
- A detail that only repeats the role is no role credit (rule S019): "Mixed By [Mixing]" → mix without credit.
- "All Music By" and "All Music" → composer (rule R003).
- "Additional Musicians", "Additional Personnel" and misspellings such as "Additonal" tick "additional" (rule S002): "Trombone [Additonal Musicians]" → trombone, additional, no credit.
- Date keywords count as whole words only ("Fuzzoramarecords" is no "record"), and capitalised words after ℗/© in the same sentence belong to a name.
- Text size down to 50 % (was 80 %).
- Escape closes the "Mapping rules" window first; the dashboard stays open.
- After creating an artist, label, place, series or work through a form, the dashboard stays at the entry or works matrix row you came from (also after it is redrawn), unless you scrolled.
- The medium list says "1 track" instead of "1 tracks".

## 2026-10-11

### Import 2.16.0

#### Added

- Status marks for credits on Discogs track lines: the dashboard sends a status for each line (each track: staged, open, in MusicBrainz, or switched off in the row) and the targets of that track, so the companion marks every line, not only the first (COMPANION 1.5.0).
- "Directed By" is asked instead of being conductor: "please choose" conductor, chorus master, creative direction or miscellaneous support (task "director"); until then the row has no type and is not added; the level follows the choice (rule R097, question Q003). A choice stays when the rules change.
- Works matrix: ✕ in a column header takes the column out – its rows go to "Skip", the column stays as a folded stub that brings them back with a click; columns "only in MusicBrainz" are folded. Not stored.
- Works matrix: the column date also plans dates for the column's relationships that MusicBrainz has without a date (an edit of each, as for a cell); a cell's own date and staged ones stay, clearing the column date takes back what it planned. Columns "only in MusicBrainz" get a column date for this.

#### Changed

- Autoscroll while dragging works as in browsers: it starts after the pointer stayed 0.2 s in an edge zone (anew after leaving it) and gets faster near the edge, with a gentle start; the rule "only after the pointer was further down once" is gone.

### COMPANION 1.5.0

#### Added

- A mark on each Discogs track line of a credit, with the status of that track; on the release page each line is checked on its own (its works or recordings). Older dashboards keep the single mark.

### Import 2.15.0

#### Added

- The rule ids next to ⓘ in a row ("ⓘ R033 · W006 · S018") can be clicked one by one: "Mapping rules" opens at that rule and highlights it (a search that hid it is cleared); ⓘ itself opens it with the row's Discogs role in the test field, as before.
- "Engineer [Mix, Recording]" is one row per task – mix and recording – each with the other details ("Assistant" …); the row shows the role as Discogs writes it (rule S018).

#### Changed

- "Mix", "Mixed By", "Engineer [Mix]" … are mix, "Recording", "Recorded By", "Engineer [Recording]" … are recording (recording engineer), always without role credit (W006, W007); the word "engineer" is no role credit for mix, recording and mastering.
- Dragging a pool chip out of "Dates & tracks": the list scrolls up only after the pointer was further down once and then stays just below the block for 0.3 s, so it no longer jumps up as soon as the chip leaves the block.

#### Fixed

- "Trumpet [Pocket Trumpet]" gave the role credit "pocket trumpet trumpet"; a detail that already names the whole instrument is now no role credit (pocket trumpet, without credit).

### COMPANION 1.4.5

#### Changed

- The cover box on Discogs has a frame in MusicBrainz colours (purple to orange).

### Import 2.14.0

#### Added

- Works matrix: a date dropped onto a cell (or set with ▾ "own date") is also added to the relationships of the cell that MusicBrainz has without any date – an edit of the existing relationship, staged like "add role credits to existing relationships". The cell shows the planned date with × (taken back until staged) and ✓ once staged; the preview marks it with ✎; the edit note counts it ("added dates to … existing relationships without a date"). Dates MusicBrainz already has are not changed (a message says so). Cells of columns "only in MusicBrainz" take such a date as well.
- While a track group is dragged, the places on rows say what a drop does: "drop: replace · ⇧ Shift: add"; the place under the pointer says "replaces the tracks of this row" or, with Shift held, "adds to the tracks of this row".
- Status marks: credits of works that are new in the editor (no MBID yet) are sent with the recording of their track, so the companion can find them on the work MusicBrainz links to it (COMPANION 1.4.4).

#### Fixed

- The edit note mentioned role credits added to existing relationships only when works were linked in the same step, and counted them only at the next "Stage"; it is now written after those checks.

### COMPANION 1.4.4

#### Changed

- Release page: credits of works that were new in the editor are found through their recording (any work linked to it that has the credit); while the link is an open edit they show ✗ with "0/1". Before, such credits kept the mark the dashboard sent (● or ○).

### Import 2.13.0

#### Added

- Track groups by drag & drop onto "Tracks and status" of a row or onto its open track list: the row gets exactly the group's tracks; with Shift held while dropping they are added to the row's own. A row on the level "Release" moves to "Recording" (with a message). The places a group can go onto are outlined while dragging, and the list scrolls at its edges as with dates.
- Folded, the track groups stay in the bar too: "keep the pools in the bar when folded" (formerly "keep the date pool …", same setting `dci-pools-keep`, on by default).
- Works matrix: a date dropped onto a cell that cannot take it says why – the cell only holds relationships already in MusicBrainz (whose dates the dashboard does not change), or no role is switched on in it yet.
- Status marks: work credits are flagged for the companion, which then also checks them on the works themselves (COMPANION 1.4.3).

#### Changed

- Stored data has generation 3: this update clears all settings and stored data once more (whichever version it comes from); the list of created works stays, and the update notice says so.

### COMPANION 1.4.3

#### Changed

- Release page: composer, lyricist, publisher and other work credits that the release lookup does not show (for example while the link between recording and work is still an open edit) are looked up on the works themselves, one request per second, at most 40 works. A check that is still running is not started a second time, and a status the dashboard sent meanwhile is not overwritten.
- Clears its stored data once more (generation 3), together with Import 2.13.0.

### Import 2.12.0

#### Added

- Language next to the import button: "Language:" with a list, also before the dashboard is opened; it follows the one in the dashboard header and the other way round.
- "Dates & tracks" folds at its bottom too ("▲ fold", always in view below the scrolling part). "keep the date pool in the bar when folded" (on by default, remembered): the dates stay in the folded bar and can be dragged onto rows while scrolling.
- "⠿ drag" next to the date pool and the track pool, with a tooltip on where their chips can go.
- Recording dates given as a period or as separate days within one year also put what they have in common into the pool – the month ("2001-01-20 – 2001-01-25" → 2001-01) or the year ("2012-03-01 – 2012-09-30" → 2012); nothing across years (rule D014). Separate days offer it in "Choose" as "month only" / "year only".
- Periods of months across years: "December 2003 to January 2004" (rule D007).

#### Changed

- "Produced By" is always producer, also written "Produced-By" or "Produced", and as "Produced By" / "Producer" of a person in "Companies, etc." (rules R020, R026, C036).
- "Horn [French]" and "French Horn" → instrument French horn, "Flugel Horn" → flugelhorn, both without role credit (W004, W005); a spelling that differs from the instrument only in spaces or hyphens is no role credit (S017).
- Unused variables removed.
- The one-time reset of stored data (from 2.11.0) also applies when updating from 2.10.0 or older straight to this version.

### Import 2.11.0

#### Added

- Update notice: after an update, a message above the import button lists the milestones since the version used before (from the changelog's table "Milestones", translated into the dashboard's languages), with a link to the changelog; × closes it until the next update. A first installation shows none.
- Stored data has a generation: an update that raises it clears all settings and stored data once and says so in the update notice. 2.11.0 does this – language, switches, windows, own mapping rules and switched-off rules, pools and matrices of all releases; only the safety list of created works stays.

#### Removed

- Unused code: texts of the old works list (before the works matrix), CSS of the old works table, "★ always" and a page lock, the release language read from MusicBrainz but never used, the group mode of the function that puts a dropped date onto some tracks of a row, the takeover of stored data from 0.5.x and 2.7.x, and the old stamp setting in the list of "↺ Defaults" (the one-time reset clears it).

### COMPANION 1.4.2

#### Changed

- Clears its stored data once (shared storage with status marks and connection, and on Discogs the place and folding of the cover box), together with Import 2.11.0.

### Import 2.10.0

#### Added

- Pool dates by drag & drop onto the date field of a row, of a planned link between recording and work, or of the works matrix (column date, cell); the row gets the date, replacing one it had. A date with track groups in the row's column of the matrix goes only onto those tracks. The fields a date can go onto are outlined while dragging; the list scrolls at its edge.
- A date dragged onto another date makes a new pool date for the period of both ("Performance 1" + "Performance 2" → "Performance 1–2"), again and again; both stay. In the matrix, a date dragged onto a date there makes that entry the period (a dragged matrix entry goes into it with its track groups).
- "↻ load again from Discogs" in "Dates & tracks": the dates and track groups from the Discogs notes are made anew, as at the first import; optionally the ones made by hand go too.
- All dates in the Discogs notes go into the date pool; those without a word naming their group are not placed in the matrix, a message says so.

#### Changed

- The date stamp is replaced by drag & drop: a click on a pool date now edits it; the stamp line ("apply to all rows with type …", "overwrite existing dates") is gone.
- "Cover Art" keeps "cover art" as wording (rule R070).
- README: "in MusicBrainz a festival primarily is an event, not a place".

#### Fixed

- After "clear all dates" (or "clear all track groups") the Discogs notes were not read again when the release was opened later, so the pools stayed empty. Now the notes are read again whenever none of their dates is left in the pool.

### Import 2.9.0

#### Added

- The dashboard in the page: the switch "window | in the page" next to the import button (and "▤ In the page" / "⧉ As window" in the dashboard header) puts the dashboard below the button, in the page's full width, instead of a window. The page scrolls with it; the head of "Dates & tracks" stays at the top and the footer with the stage button at the bottom. Window is the default; the choice is remembered and reset by "↺ Defaults".
- Separate days ("Recorded June 16 & 19, 1980", rule D013): the pool keeps both days as Discogs gives them and also gets the period from the first to the last day ("Performance 1–2"). In the matrix they stand as one entry marked "Choose" – the days as on Discogs or the period; "Apply" leaves it out until you choose, and "1 to choose" shows in the head of "Dates & tracks".

#### Changed

- The head of "Dates & tracks" stands out: a bar from date purple to track orange with a round arrow.
- "Find dates in text" is now "Find dates in free text" (German "Daten in Fließtext finden", Spanish "Buscar fechas en texto libre", French "Trouver des dates dans un texte libre").

### Import 2.8.0

#### Added

- Date matrix in the date pool: one column per date group (Performance, Mix, Remastering, Mastering, ℗/©). Dates are dragged from the date pool into a column, track groups onto a date; a date without a track group applies to all tracks, several track groups on one date count together, a date can be in several columns. "Apply" puts the dates onto the rows: per track the dates of all entries covering it count, rows are split by tracks and get one copy per date, release-level rows take only the dates for all tracks, dates naming studios go only onto those studios. Applying again starts from the rows before the previous run, so the rows follow every change of the matrix. "apply automatically" (off by default, remembered) applies every change at once; "not applied yet" shows open changes.
- Dates in the Discogs notes with a word naming their group are placed in the pool and the matrix as dashed suggestions, with their track groups and studios, once per release; a message says so.
- Small editor for an entry of the matrix (column, track groups, studios, confirm, edit date, remove); entries and track groups can be dragged between columns and dates. Without a mouse: the grip ⠿ of a chip, then "+ place here" / "+ tracks here"; Esc cancels.
- "Dates & tracks": date pool, track pool, matrix and "Find dates in text" fold together into one line with the counts; open by default when there are dates, the choice is remembered; opened, the block scrolls on its own.
- "clear all dates" and "clear all track groups" for this release, with the option to clear the stored pools of all other releases; rows keep the dates they already have as their own.
- "+ new track group" on releases with several media: choose tracks, a whole medium, or all media (one group per medium).
- "↺ Defaults" in the dashboard header: all settings back to their defaults (language, text size, windows, navigation switches, footer options, stamp, matrix, folding, role codes, log window, and through the companion the cover box on Discogs); own mapping rules and the stored pools of all releases only when ticked; the safety list of created works never.
- README: section "Settings" with every setting of both scripts, its default and where it is stored.

#### Changed

- Colour code: dates in MusicBrainz purple, tracks in MusicBrainz orange throughout (pools, matrix, track buttons and numbers, tags). Entry cards: artist blue-grey, label teal, place green. The chosen level button is dark on every level.
- A row's date keeps "save to pool" (now also suggesting the date in the matrix for the row's group and tracks) and a small ✕ to remove it; "save to pool and copy to similar relationships" is replaced by the matrix.
- Group buttons in "Find dates in text" and the ℗/© suggestion put the date into the matrix instead of onto the rows at once; "as single dates" replaces the suggestion of the period.
- Stamping a date that has track groups in the row's column of the matrix puts it only on those tracks.
- The stamp is one slim line.
- "Find dates in text" is smaller and folded at the end of "Dates & tracks".

#### Removed

- The "Dates ↔ tracks" table of 2.7.0 and the track group of a single pool date (both are now the matrix; existing links become dashed suggestions in the matrix).

#### Fixed

- The log entry for a relationship that could not be staged showed its text key instead of a message.

### COMPANION 1.4.1

#### Added

- "↺ Defaults" of the dashboard (Import 2.8.0) also resets the place and folding of the cover box on Discogs – in open tabs at once, in others when they are opened next.

## 2026-10-10

### Import 2.7.0

#### Added

- "Dates ↔ tracks" in the date pool: a table of all pool dates with their track group (or all tracks) and "apply" for a date group, which puts the date on the rows of that group only on those tracks (rows covering more tracks are split). Chips show the links: "↔ Overdubs" on a date, "2 dates" on a track group; an automatic name follows the track group.
- Stamping a pool date that has a track group onto a row puts it only on those tracks of the row (the row is split); a row without any of them is left alone, with a note.

### Import 2.6.0

#### Added

- "Remove row" under every role, also for rows from Discogs: the row leaves the dashboard, relationships already staged for it are taken out of the editor at the next "Stage", and "undo" in the message brings it back.
- "only works" next to Recording · Release · Skip: skips everything except the work relationships of the works matrix (writers, publishers, arrangers …), also bringing back work relationships set to Skip before.

#### Changed

- Entries are cards with a coloured bar, a label and a tinted header per kind: artist purple, label teal, place orange, others grey; rows alternate in shade, entries have more room between them. Not found in MusicBrainz stays a red bar.

### COMPANION 1.4.0

#### Added

- The cover miniature on the Discogs page can be dragged anywhere in the window; its place is remembered. Dragging does not open the image view.

### Import 2.5.0

#### Added

- Track pool: named groups of tracks ("Tracks 1–5") next to the date pool, made from dates in the text or by hand (tracks grouped by medium); a pool date can belong to a track group, and the track list of a row can take a group's tracks.
- Dates for some tracks: "Find dates in text" shows the tracks (rule S015: "Tracks 1 to 5", "tracks 6, 8 and 10", "A1 to A3", "side B", "CD2, tracks 1–5", "Disc 2") and studios (rule S016) named in a date's sentence. A group button creates the track group and a pool date named after it ("Performance 1 (Tracks 1–5)") and puts the date only on those tracks: rows covering more tracks are split (with a message), studios named in the sentence get exactly these tracks, other studios are left alone, rows with a date of their own stay.
- Several days (rule D013): "June 23 and 24, 2025", "23 and 27 June 2025", "23. und 24. Juni 2025". Consecutive days give one period ("as single dates" splits it); other days are separate dates, each with a pool entry and a copy of each row, so every date becomes a relationship of its own.
- "Apply to these tracks" in the form of a pool date with a track group.
- Navigation: "Artwork" switch for the cover miniature on the Discogs page (with Companion 1.3.0).

#### Changed

- A&R: the word after "A&R" becomes the task of the relationship on the release group ("A & R Consultant" → task "consultant").
- Import button and navigation form one block with room and a thin line below it on the MusicBrainz page.

### COMPANION 1.3.0 · needs Import 2.5.0 or later

#### Added

- Cover miniature: while the Discogs tab is connected, a small picture of the cover stays at the top right of the Discogs page when scrolling; a click opens Discogs' image view, "–" folds it, "🖼" shows it again.

### Import 2.4.3

#### Fixed

- Publishers in the works matrix were not limited to the works of their writers: the dashboard looked for MusicBrainz relationships named "publishing", but MusicBrainz calls the artist–label relationship "personal publisher", so it never found any; and a publisher not in MusicBrainz was ticked on every work. Now a publisher is ticked only on works written by an artist it is the personal publisher of (rule S014); all other publishers stay in the matrix with their cells off, to tick by hand. The suggestions of further publishers for a writer use the same relationship.

## 2026-10-09

### Import 2.4.2

#### Added

- The status map sent to the Discogs tab names, for each credit, its MusicBrainz entry, relationship type and targets, so the MusicBrainz release page can check what arrived (with Companion 1.2.0).

#### Fixed

- With a date stamp active, a click into a date field stamped the row and redrew it, so the cursor was gone and every further click stamped again – typing a date was impossible. The cursor now stays in the clicked field with the stamped value selected; each row is stamped once per stamp, after that it is edited as usual (also "remove date" and the other buttons of the cell). With "overwrite existing dates" off, a click into a filled field is no longer intercepted.

### COMPANION 1.2.0 · needs Import 2.4.2 or later for the check on the release page

#### Added

- MusicBrainz release page: the Discogs status marks of the release are shown again and checked against what MusicBrainz now has – ✓ arrived, ✗ staged but not (yet) in MusicBrainz (with "found/total" in the tooltip); checked on opening, after 20 seconds and after a minute. Works also when the release page is opened later: the last status of up to 30 releases is kept.

#### Fixed

- On the release page the marks only repeated the state from before "Enter edit" (● staged), so they could not show whether a relationship arrived; when the page is closed, they now go at once.

## 2026-10-07

### Import 2.4.1

#### Added

- "Overwrite existing dates" in the stamp bar (on by default) and "all rows" as a stamp target; switched off, the stamp only fills rows without a date.
- Navigation: "Status on the release page" keeps the Discogs status marks while the MusicBrainz release page is open (e.g. after "Enter edit"); they go once the release page and the editor are closed (with Companion 1.1.0).
- "↑ top" next to the works matrix scrolls it back to its first row.
- Date rule D012: month and year as numbers ("3/1996", "03.1996"); "Rec." counts as "recorded".

#### Changed

- The role credit tag reads "from Discogs".
- A&R ("A & R Consultant", "A&R Coordinator" …) goes on the release group, without role credit.

#### Removed

- The "★ always" button at the rows (own rules are made in "Mapping rules").

#### Fixed

- The role credit field offered the Discogs role itself as a suggestion ("Produced By", with "by" and brackets); it now offers only real wordings, never a word form of the MusicBrainz role, "by" or Discogs brackets. "Photographed By" is photography.
- Pool lists of rows missed pool entries made after the row was drawn; all lists are now kept up to date (every pool entry can be chosen for every row).
- A pool list could close right after opening when the row was redrawn at that moment; rows are now redrawn once the list has closed.
- The works matrix jumped back to its first row when a date was added to a single work or stamped; it now keeps its place.
- The release group level button did not look pressed when chosen.

### Companion 1.1.0

#### Added

- Runs on MusicBrainz release pages too: while the release page of the release is open, it keeps the Discogs status marks alive (if "Status on the release page" is on).

### Import 2.4.0

#### Added

- Dates in text: "Find dates in text" in the date pool lists the dates of pasted text and of the Discogs notes in MusicBrainz form, with buttons for the date groups (creating the pool entry and filling the group) and "pool only"; keywords nearby highlight the likely group.
- Date rules D001 … in the mapping register (switchable, shown in "Mapping rules", tried in the test field): ISO/MusicBrainz, numbers with dots or slashes, month names and abbreviations in four languages, ordinal words, days within a month, periods across months or years, month and year, seasons (the year), a year alone; decades are left out. Slash dates: a number over 12 decides, otherwise the Discogs release country (US: month/day, elsewhere day/month), with a note and the other reading to choose.
- Rule origin per row: "ⓘ" lists the rules that made the row (R/U/C, W, Q, S); hovering shows their notes, a click puts the row's Discogs role into the test field.

### Import 2.3.0

#### Added

- Own mapping rules (U001 …), stored in the browser and tried before the built-in ones: "Discogs role → MusicBrainz" (type, level incl. skip, instrument, fixed role credit; details containing or exactly matching a text) and "Discogs spelling → MusicBrainz instrument"; with edit and delete in "Mapping rules".
- Every rule can be switched on and off, own ones as well as built-in ones (R, W, Q, C, S); after each change the rows are mapped again, keeping levels, instruments and credits set by hand.
- "★ always" next to a role in the dashboard turns the row into an own rule for that Discogs role with exactly its details.
- Export and import of the own rules and the switched-off built-in rules as a file.

#### Changed

- The main button "Import Discogs credits …" sits above the navigation.

#### Fixed

- The "Discogs status" and "Track highlight" buttons in the bar of the MusicBrainz page had white text on a white background when switched on.
- An instrument chosen in the instrument question (e.g. double bass) counts as set by hand and stays when rules change.
- The README left out every section added since 1.2.0 (updating what was staged, keyboard, large releases, stage only some relationships, role credits for existing relationships, names and Discogs aliases, mapping rules, diagnosis); it now contains all of them.

### Import 2.2.1

#### Fixed

- Rows set to another level or to Skip with the toolbar's buttons after "Stage: only …" had hidden them were still treated as only hidden, so their staged relationships stayed in the editor. A level chosen with the buttons now always counts: staged relationships of the old level are taken out of the editor, those of the new level are added (e.g. recordings → release).

### Import 2.2.0

#### Added

- Relationships staged before that are no longer wanted in the dashboard are taken out of the editor again on the next "Stage", with MusicBrainz's own "remove-relationship" (as used by the relationship editor's developer in his own userscript), as long as they still look as the dashboard left them; the preview lists them.
- Typewriter apostrophes become typographic ones (' → ’) in role credits and artist credits, from Discogs and typed by hand (rule S012).

#### Fixed

- The "Mapping rules" window could not be resized and did not remember its place; it now works like the other windows.

### Import 2.1.1

#### Fixed

- "Discogs view: connected" was shown as soon as any Discogs page was open, and the button to open the release disappeared. "Connected" now means that a Discogs tab shows this release; otherwise the dashboard says that the tab is on another page and offers "Load the release there" and "open in background" (with Companion 1.0.3).

### Companion 1.0.3

#### Changed

- Reports which releases the open Discogs tabs show, prefers a tab that already shows the release, and can load the release in the tab without pointing at anything.

### Import 2.1.0

#### Added

- Instrument questions in the mapping register (Q001 …): plain "Guitar" from Discogs keeps "guitar" as role credit and asks electric guitar · acoustic guitar, like plain "Bass" (electric bass guitar · double bass · acoustic bass guitar). One click sets the instrument; the role credit stays. "Mapping rules" lists the questions, and the test field shows them.

## 2026-10-06

### Import 2.0.1

#### Changed

- Every rule can be found in the code by its id: special rules (S001 …) and wordings (W001 …) are marked where they act and name their function in the register; "Companies, etc." rules have ids C001 …, the tables T001 … (instrument spellings, words in lower case, artwork types, company roles), which now sit in the register section.
- "Mapping rules" shows the code location of each rule and lists the tables; the test field also names the special rules that took part (e.g. S009 for "Coordinator [Tour]").

### Import 2.0.0

#### Added

- Mapping register: every rule that turns a Discogs role into a MusicBrainz relationship is kept in one place, with an id (R001 … for roles, W001 … for wordings, S001 … for special handling), a note, the Discogs pattern and the MusicBrainz types and level. Each row knows the rule that produced it.
- "Mapping rules" next to "Log" in the dashboard header: the register as searchable tables (roles, role credit wordings, special handling, "Companies, etc.", instrument spellings, words in lower case) and a field to try a Discogs role, showing type, level, instrument, checkboxes, role credit and the rules applied.
- Upright Bass, Contrabass and Kontrabass, also as details of "Bass" ("Bass [Upright]"), become double bass with "upright bass", "contrabass" or "Kontrabass" (German, with a capital letter) as role credit.
- The bass question offers acoustic bass guitar as a third choice: electric bass guitar · double bass · acoustic bass guitar.

#### Changed

- Role credits never contain Discogs brackets: details come before the role ("Coordinator [Tour]" → "tour coordinator").

## 2026-10-05

### Import 1.9.2

#### Changed

- "Credited as" always holds the name Discogs shows when it differs from the MusicBrainz name (empty when they are the same), for artists and for studios, labels and the other "Companies, etc."; before, only Discogs name variations were taken over. Credits typed by hand stay.
- Discogs aliases are only suggested ("Suggestion from a Discogs alias"), never assigned without a click.

### Import 1.9.1

#### Added

- Discogs aliases: an artist not found by its own Discogs link is looked up through its Discogs aliases ("found via Discogs alias …").
- ↻ next to "Discogs view: connected" reloads the connected Discogs tab (with Companion 1.0.2).

#### Changed

- "Add entry manually" sits above the works matrix.

#### Fixed

- An existing relationship that differs only by a missing text attribute (e.g. design without task) was taken for another relationship: a second one was staged next to it. It now counts as the same; with "add role credits to existing relationships" the task is added to it (status "edited", as confirmed by a diagnosis on the live editor).

### Companion 1.0.2

#### Added

- Reloads the connected Discogs tab on request from the dashboard.

### Import 1.9.0

#### Added

- "Add role credits to existing relationships" (footer, off by default): existing relationships that match a row exactly but lack its role credit or "credited as" get them added in the editor, shown as changed (yellow); recording and release level. A check afterwards confirms that MusicBrainz took them as changed.
- Track picker: medium headings with format and MusicBrainz name; a click switches all tracks of that medium on or off.

#### Changed

- "design" anywhere in a Discogs role or its details always means the type design, with the other words (without "design", "by") as wording: "Cover [Cover Design]" → "cover", "CD Designed By" → "cd". Graphic design keeps its own type. "Cover Design" is now credited as "cover".
- A medium in front of a role ("CD Produced By", "LP Mastered By") puts the relationship on the release.
- "Editor [Publications Editor]" and other editors of texts become miscellaneous support with the task in lower case.

#### Fixed

- The "Discogs" tag of a role credit stretched into a black bar over the field column.
- The top-left corner of the works matrix overlapped the date pool while scrolling.

### Import 1.8.0

#### Added

- "Navigation" groups the switches: jump to source (on mouse-over / on click), Discogs status and the new "Track highlight" switch for the highlighting of works-matrix rows from the Discogs tracklist.
- Works matrix: "use MusicBrainz names" clears every "credited as".

#### Changed

- Entries in "Companies, etc." whose name contains "Festival" are not taken over (in MusicBrainz a festival is an event, not a place).

### Companion 1.0.1

#### Changed

- The status marks on the Discogs page are shown only while the MusicBrainz edit page that sent them is open; they disappear when it is closed (at the latest after 10 seconds) and come back when it reports again.

### Import 1.7.0

#### Added

- "Discogs status" switch next to "on mouse-over / on click": the companion marks every credit on the Discogs page as already in MusicBrainz, staged, open, skipped or not mapped (not mapped lines in yellow); the marks follow every change.
- A click on a mark on the Discogs page shows its row in the dashboard (work credits: their column in the works matrix).
- The pointer on a track on the Discogs page highlights its row in the works matrix.

### Companion 1.0.0

#### Added

- Status marks on the Discogs page (needs Import 1.7.0 or later), with clicks on a mark and the track under the pointer reported back to the dashboard.

### Import 1.6.0

#### Added

- Works matrix: "Add a column" with any entry already in the dashboard and a role of your choice (composer, writer, arranger …); "all works" in a column header switches the column on for every work shown.
- Works matrix: a box for tracks without a work ("New works for all N tracks", created with "Enter edit") and a "＋ New work" button in each row; "clear all dates" empties every date in the matrix.
- A planned link between recording and work takes the recording date by default (the track's performance date); "own date" sets another one.
- A row added by hand gets the date its date group currently uses as soon as it has its role.
- A role credit taken from Discogs is marked ("Discogs" tag, yellow field).
- Lithography → design, with "lithography" (or the bracket details) as wording.

#### Changed

- Arrangement credits named together with writing credits on Discogs go to the works matrix instead of the recordings.
- Level buttons are offered only where MusicBrainz has the row's relationship type (no "Work" for producer or mix credits).
- Works matrix: track titles in bold, the Discogs position set apart below.

#### Fixed

- The bass question and the "bass" role credit were missing for "Bass" with checkbox details such as "Bass [Additional]".
- "Save to pool and copy to similar relationships" reused the pool entry of another group (e.g. "Performance 1" on a ℗ row) instead of creating one for the row's own group.

## 2026-10-04

### Import 1.5.4

#### Fixed

- Staging again after changing the instrument, an attribute or the relationship type of a row ("bass" → "double bass") added a second relationship next to the first one. The relationship staged before is now changed in the editor instead (same relationship, no duplicate), as long as it was not changed in the editor itself.

### Import 1.5.3

#### Changed

- Works matrix: from MusicBrainz, arrangers (arranger, instrument arranger, vocal arranger, orchestrator) and labels (publishers) are shown again, besides writing and lyrics credits; dedications and other relationships stay hidden.

### Import 1.5.2

#### Changed

- Works matrix: from MusicBrainz only writing and lyrics credits are shown (composer, lyricist, writer, librettist); arrangers, dedications and other relationships of linked works are left out, except where a column from Discogs or added by hand has that role (e.g. a publisher already in MusicBrainz).

### Import 1.5.1

#### Added

- Rounds with the limit per staging: above the stage button the dashboard says how many rounds the plan needs ("3 rounds of at most 500 each. Next: round 1 of 3"); progress, confirmation and messages show "round 1 of 3", and after the last round "All staged in 3 rounds".
- The medium list shows each medium's format and name ("Medium 2 · CD · Nocturnes (21 tracks)").

#### Changed

- Works matrix: dedications ("dedicated to") from MusicBrainz are not shown.

### Import 1.5.0

#### Added

- Large releases: a medium list in the toolbar shows one medium at a time (dashboard, works matrix and staging); from 50 tracks on several media the dashboard starts with medium 1 by itself. Release-level relationships are always included.
- "Load medium … in the editor" opens media that MusicBrainz's relationship editor has not loaded yet, one after another, and waits for their recordings.
- At most 500 relationships per staging (footer, on by default, can be switched off); the rest is taken by the next "Stage".
- Progress: "Staging 120 of 500 …", and the search for same-named works shows how many tracks are checked and can be stopped; it only runs for the medium shown.
- "Bass" from Discogs is credited as "bass", and the row asks whether it is an electric bass guitar or a double bass; one click sets the instrument and keeps "bass" as role credit.

#### Changed

- Works matrix only: tracks titled only with information in square brackets ("[untitled]", "[unknown]" …) are left out (no work search, no new work); in other titles such information is left out of the work title.

#### Fixed

- Relationships staged before that were only hidden (by the medium list or "stage only …") were listed as "to remove by hand".

### Import 1.4.0

#### Changed

- The publishing label of a series is only filled into the form of a series created with "Create series …"; the button for existing series and the check of their relationships are gone.
- Dates in the works matrix: "BD" and "ED" (begin date, end date as tooltip) in a grid with year, month and day exactly one above the other.

#### Fixed

- "Stage in the relationship editor" stayed greyed out when the only things to stage were writing credits on tracks without a work. A hint now counts these tracks, the button stays usable, and staging offers to mark them as new works (same-named works of the writers are left out for linking).

### Import 1.3.0

#### Added

- Publishing label of a series: Discogs' "Parent Label" of a series is looked up, matched to an MB label by its Discogs link and checked against the series' existing relationships. MusicBrainz's "publishes series" can't be staged in the release relationship editor (it joins a label and a series), so "Add 'publishing label' to the series …" opens the series' edit form prefilled with it, and "Create series …" includes it.
- Toolbar "Stage: all relationships · only work relationships · only non-work relationships": the rest goes to Skip (links to works included) and comes back with "all relationships".
- Log milestones: "Import complete" when all Discogs credits are in the dashboard, "Checks complete" when the background search for same-named works has finished, "Staging complete" with a summary after every staging.

#### Fixed

- The dashboard's form dialog closed as soon as an edit page (not a create page) had loaded.

### Import 1.2.0

#### Added

- Updating after staging: back in the dashboard, changes to relationships staged before (dates, role credits, credited-as) are updated in the editor on the next "Stage", but only where the relationship still looks as the dashboard left it; relationships changed or removed in the editor itself are left alone and named. Relationships no longer wanted are listed for removal by hand. The preview marks updates with ↻.
- Confirmation right next to "Stage in the relationship editor" when staging has finished.
- Date buttons in this order: "save to pool and copy to similar relationships" (pool entry named after the date group, copied to every similar row without a date: the date group, otherwise the same relationship type), "save to pool", "remove date".
- "Create series …" (also for events and recordings added by hand) opens MusicBrainz's form prefilled with name, Discogs link and edit note; afterwards the entry is assigned and a Discogs series row becomes active with its number.
- Keyboard: Esc closes the dashboard from anywhere on the page unless MusicBrainz needs the key; Alt+Shift+D (Option+Shift+D) opens or hides it.

#### Changed

- Dates are no longer copied automatically when a date field is left, pasted, picked from the pool or stamped; copying happens only with the new button. Before, a group was filled as soon as the begin date was typed.
- "[No lyrics]" is always first in both lyrics-language lists. It is the language code zxx, whose ISO name "No linguistic content" MusicBrainz's page data uses; MusicBrainz shows it as "[No lyrics]" for works. The list from the page data no longer shows a warning when it is complete.
- Instrument words in credits: each part of a hyphenated word is checked on its own ("Tenor-Sax" → tenor-sax), and common Discogs abbreviations (Sax, Bari, Vibes, Tpt …) are written in lower case.

#### Fixed

- A staged relationship with a duplicate row (e.g. the same studio from Discogs and by hand) was taken for changed.

## 2026-10-03

### Import 1.1.0

#### Added

- "New work" in the works matrix marks a new work in the relationship editor, built like the works of MusicBrainz's own "Batch-add new works" (negative id, work type, lyrics languages). The link with the recording and every role of the matrix row (writers, publishers) are attached to it, and MusicBrainz creates it together with them on "Enter edit". "Mark all missing works as new" does this for every track without a work. The edit note says how many works were created this way. Based on two diagnosis runs on the live relationship editor.

#### Changed

- Creating a work through MusicBrainz's form is now "via form …"; the one-by-one queue is "Create missing works one by one via form …".

#### Fixed

- Removing the link to a work created through the form also removes it from the list the emergency reset uses, so it is not linked again.

### Import 1.0.7

#### Changed

- Diagnosis records works that only exist in the editor in full (including their lyrics languages) and every relationship at such works, e.g. a composer added with "Batch-add a relationship to works".

### Import 1.0.6

#### Added

- Diagnosis in the log window: records what the relationship editor does while its own tools are used (e.g. "Batch-create new works"), as a basis for creating works and their relationships in one "Enter edit". Observes only.

### Import 1.0.5

#### Added

- The recording engineer (relationship "recording") belongs to the date group Performance.
- Dates in the works matrix (column and cell) use the MusicBrainz fields Begin date and End date with "ended", ⇣, the date pool and pasting, like everywhere else.
- The work search tolerates one missing, added or different letter in a title ("Trak 1" = "Track 1"); digits must match.

#### Changed

- The role credit field is offered only where MusicBrainz can store one (instruments, vocals, text attributes such as a task); for mastering, design, liner notes and the like it is no longer shown.
- Role credits of artwork relationships (artwork, art direction, design, design/illustration, graphic design, illustration, photography) are entirely in lower case, including details from brackets.
- A trailing "by" is no longer taken over into tasks and role credits.
- "Text By" from Discogs becomes liner notes.
- Phonographic copyright (℗) goes on the recordings by default.
- "[No lyrics]" is always offered as lyrics language.

#### Fixed

- "Save to pool" from a row of a date group suggested the relationship type as name (e.g. "instrument"); it now suggests "Performance 1" etc. and fills the group.

## 2026-10-02

### Import 1.0.4

#### Fixed

- Work suggestions included works by people Discogs does not name: without a hit for title and writers, the search fell back to the title alone. Now only the works of the people credited for writing the track are searched, and a work is offered only if one of them is credited on it in MusicBrainz and its title or an alias matches. Tracks without writing credits get no suggestions, only a link to search MusicBrainz.

### Import 1.0.3

#### Fixed

- "Additional" at the start of a Discogs role ("Additional Synths", "Additional Vocals", "Additional Engineering" …) now ticks MusicBrainz's "additional" checkbox and maps the rest of the role; before, such roles were not recognized and kept "additional" in the role credit.
- Plural instrument names find their MusicBrainz instrument ("Synths" → synthesizer).

### Import 1.0.2

#### Changed

- The works matrix shows the MusicBrainz names of the roles by default; CISAC and GEMA codes remain available in the list above the matrix. Several roles in one cell are stacked, so the matrix keeps its width.

### Import 1.0.1

#### Added

- Release group as a fourth level: the release relationship editor also edits the relationships of the release group, so rows whose type exists there get a "Release group" level button. Existing release group relationships are recognized.

#### Changed

- Release group series from Discogs are now added as "part of" on the release group, with their number, instead of only being shown with a link.

### Import 1.0.0

#### Added

- Works matrix in place of the works section: one row per work (medleys get several rows), one column per person or publisher with credits on level "Work", roles as codes in the cells. Click a cell to switch its roles; ▾ shows all roles and a date of its own for the cell. Column header with MB match, disambiguation, "credited as" and a column date. Relationships already in MusicBrainz are green and locked; writers known only in MusicBrainz get locked columns. Header row and first column stay in place while scrolling; columns can be collapsed.
- Role codes after the international CISAC standard (C, A, CA, AR, TR, E, SE), switchable to the GEMA codes (K, T, K+T, B, V, SV) or the MusicBrainz names.
- Publishers with evidence: a publisher from Discogs is ticked only for works whose writers it publishes according to MusicBrainz's artist–label "publishing" relationships, with the reason shown; other works are marked unclear, and "for all works" ticks them all. Relationships outside the release date are shown as hints. Publishers MusicBrainz knows for a writer are offered as columns.
- Same-named works by the writers of a row are looked up automatically and offered for linking; creating a new work warns about them, and "Create missing works one by one" leaves those tracks out.
- Several lyrics languages per new work, as in MusicBrainz ("Lyrics languages"); work type and languages can be set per row. The complete language list is also read from the form's page data when MusicBrainz offers languages through a search field.
- Date groups Performance, Mix, Mastering, Remastering and ℗/©: a date on one row goes into the pool ("Performance 1" …) and onto every row of the group, roles and places in both directions, without overwriting dates entered by hand; a warning names the rows that keep their own date. The ℗/© suggestion fills the ℗/© group directly.
- Unmapped roles are marked yellow with research links (MB instruments, MB relationship types, Discogs credit roles); the toolbar counts them and can show only those.
- Series from Discogs with their number, if the series exists in MusicBrainz with its Discogs link: release series as "part of" on the release; release group series with a link to the release group; others are only shown.
- "Remastered At/By" from Discogs companies: mastering marked as remaster.

#### Changed

- Writing credits on level "Work" are shown only in the works matrix; the artist list keeps the match and a note.
- Only Producer and Co-Producer go on the recordings by default; Executive, Associate, Assistant and Additional Producer on the release (unless Discogs names single tracks).
- Cover credits: Cover → artwork, Sleeve and Cover Concept → design, Cover Photo → photography, Cover Painting → illustration, each keeping the Discogs wording for the edit note.
- Work type and lyrics languages are labelled as in MusicBrainz.

#### Fixed

- "Additional Producer" without brackets did not tick "additional".

## 2026-10-01

### Import 0.9.8

#### Changed

- Credits keep proper names capitalized and write generic words in lower case, also in details from brackets: "Drums [Brushes]" is credited as "brushes", "Electric Piano [Fender Rhodes]" links the instrument Rhodes piano credited as "Fender Rhodes", "Synthesizer [Roland Jupiter-8]" is credited as "Roland Jupiter-8". MusicBrainz's own instrument names decide which words are generic (lower case there) and which are proper names (capitalized there, like "Rhodes"); words MusicBrainz does not know, such as brand and model names, are kept as Discogs writes them.

### Import 0.9.7

#### Changed

- The Discogs wording is kept, in lower case, wherever MusicBrainz names an instrument or role differently: "Synth" becomes the instrument synthesizer credited as "synth", "Backing Vocals" background vocals credited as "backing vocals", "Layout" the relationship design with "layout". Where the relationship type has no field for it, the wording goes into the edit note. Grammatical variants such as "Mixed By" (mix) or "Remastered By" (mastering) are not credited. Details in brackets still come first.
- Tasks of "miscellaneous support" are written in lower case.

### Import 0.9.6

#### Added

- Dates for the planned links between recordings and works, with the same rules as for credits: Begin date and End date fields as in MusicBrainz, picking from the date pool, stamping, pasting a date as MusicBrainz shows it, and applying a pool date to all planned work links at once. The dates are checked in the editor after staging, and the dates of newly created works survive an emergency reset.

### Import 0.9.5

#### Changed

- Work type and language for new works: the lists now always come from MusicBrainz's own "Add work" form, so they contain every work type and every language, named as in your MusicBrainz interface. Languages are grouped as there, with the frequently used ones first, and include "[Multiple languages]" and "[No lyrics]". The page's own data and a built-in list are only fallbacks; a warning says when the complete lists could not be read.
- Nothing is preselected any more (before: "Song" and the release language). The choice is filled into every new work until it is changed.

### Import 0.9.4 · needs COMPANION 0.3.0 for background tabs

#### Added

- MusicBrainz disambiguation of matched artists, labels, places and other entries, shown next to the MB link in each group header.
- Links to Discogs and MusicBrainz in the group headers are visually distinct ("Discogs" and "MB" tags).
- Works can be opened in background tabs: all linked and planned works from the Works section, the new works after "Create missing works one by one", or a single newly created work. Needs the companion script 0.3.0 or later.

#### Fixed

- The mode switch in the dashboard header was rebuilt every few seconds, so a click on it could get lost.
- Jumping to the source on Discogs: a pending jump to another row could still fire after the pointer had moved back, and clicking the same row again never jumped again after scrolling on Discogs.

### COMPANION 0.3.0 · background tabs need Import 0.9.4 or later

#### Added

- Opens pages in background tabs on request of the dashboard, e.g. the works of a release (main script 0.9.4 or later). At most 50 at once.

#### Security

- Only MusicBrainz and Discogs pages are opened. Before, any other script on the MusicBrainz page could have made the companion open any address.

### Import 0.9.3

#### Fixed

- "Create missing works one by one": only the first new work got its writers. After it was created, the writer row counted as already on MusicBrainz and was set to Skip. A row now only counts as complete when every selected track has a work.

### Import 0.9.2

#### Changed

- Renamed to "MB x Vibecode: Import Discogs credits" (script manager, edit notes, documentation). The translated script names were removed.
- The script header carries the release date of the version (`@date`).

### COMPANION 0.2.2

#### Changed

- Renamed to "MB x Vibecode: Import Discogs credits COMPANION". The translated script names were removed.
- The script header carries the release date of the version (`@date`).

### Import 0.9.1

#### Changed

- Repository, issue tracker and update addresses point to https://github.com/proto-beep/MBvibecode.
- License changed to CC0 1.0 to match the repository.
- Edit notes link the repository.
- Documentation: section on the creation with AI.

### COMPANION 0.2.1

#### Changed

- Repository, issue tracker and update addresses point to https://github.com/proto-beep/MBvibecode.
- License changed to CC0 1.0 to match the repository.

### Import 0.9.0

#### Added

- "Add entry manually" accepts any MusicBrainz entry that can be related to the release, its recordings or works: areas, events, series, recordings, releases, works and more, taken from MusicBrainz's own relationship types. New section "Other entries" for them.
- Direction choice for relationships between two entries of the same kind (recording–recording, release–release, work–work), shown as sentences.
- Text attributes such as a series number get their own labelled field.
- Existing relationships are recognized for all these kinds of entries.

### Import 0.8.0

#### Added

- "Add entry manually" for artists, labels and places, with a role list of all MusicBrainz relationship types for that kind of entry.
- Dates can be pasted as MusicBrainz shows them, e.g. "from 2015-01-26 until 2015-01-27", "in 2015-01", "on 2015-01-26".
- "Dashboard" button in the log window to bring the dashboard back from anywhere on the page.

#### Changed

- Every Discogs role is kept: roles without a specific MusicBrainz relationship are added as "miscellaneous support" with the Discogs role as task instead of being skipped. Unknown roles that are no MusicBrainz instrument become "miscellaneous support" too.

#### Fixed

- The Discogs role was never passed on as task for "miscellaneous support".
- Two relationships that differed only in a text attribute (e.g. two tasks) were treated as one.

## 2026-09-30

### Import 0.7.1

#### Added

- Discogs details in brackets tick the matching MusicBrainz checkboxes where the relationship type has them, e.g. [Remaster] → re, [Pre-master] → pre, [Associate] → associate. "Remastered By" and "Pre-Mastered By" set re and pre.
- Checkboxes show MusicBrainz's explanation on hover.

### Import 0.7.0

#### Added

- Relationships that already exist on MusicBrainz are highlighted and set to Skip; rows that exist only partly get a lighter highlight.
- Dashboard and log are movable and resizable windows; position and size are remembered and fitted to the screen.
- Text size control; all sizes follow the browser's font size setting.

#### Changed

- The dashboard no longer darkens or blocks the page.
- Tables scroll sideways instead of squeezing their columns.

#### Fixed

- Rows scrolled into view could end up under the sticky date pool.
- After switching the language, the dashboard could open at a tiny size.

### Import 0.6.0

#### Changed

- Dates rebuilt: every row has Begin date and End date fields as in MusicBrainz; a date pool keeps dates for reuse, which can be picked in a row, stamped onto rows or applied to all rows of one relationship type.
- After staging, the dates are read back from the relationship editor and checked.

### Import 0.5.3

#### Added

- Persons listed under "Companies, etc." can be linked as MusicBrainz artists.
- Phonographic copyright (℗) can be added to recordings.

#### Changed

- The Discogs view switch is hidden when the companion script is not installed.

### Import 0.5.2

#### Fixed

- A Discogs detail in brackets now always wins over the fixed credit: "Drums [Brushes]" is credited as "Brushes".

### Import 0.5.1

#### Added

- Discogs "Drums" mapped to "drums (drum set)" is credited as "drums".

#### Removed

- Release dates are no longer suggested as dates.

### Import 0.5.0 · Discogs view of companies needs COMPANION 0.2.0

#### Added

- "Companies, etc." from Discogs: labels and places (studios, plants, rights holders) matched via their Discogs links, with "Create label …" and "Create place …".
- Dates for relationships, with a date store.
- Switch to make the Discogs tab follow the dashboard on mouse-over or on click.

### COMPANION 0.2.0

#### Added

- Highlights companies from "Companies, etc." on Discogs via their label links.

## 2026-09-29

### Import 0.4.0

#### Added

- Dashboard in English, German, Spanish and French (English by default).
- Emergency reset: discards all unsaved changes in the editor and stages only the links to newly created works.
- Works created through the dashboard are remembered until they are linked.
- Edit note with the Discogs source, the script name and a short summary.
- Log window documenting every step.

### COMPANION 0.1.1

#### Changed

- English script name with translated names for German, Spanish and French.

### Import 0.3.0

#### Added

- Works: check linked works, search existing works by title and writers, create new works with MusicBrainz's form prefilled (writers, work type, language).
- Create missing artists with MusicBrainz's form prefilled from Discogs (web links, group members).
- Connection to the companion script for a Discogs tab next to the editor.

#### Changed

- Works with Violentmonkey and Tampermonkey.

### COMPANION 0.1.0 · needs Import 0.3.0 or later

#### Added

- First version: connects the import dashboard with a Discogs tab, for example the other half of a split view. Loads the Discogs release there and highlights where each credit, track or artist comes from.

## 2026-09-28

### Import 0.2.0

#### Added

- Discogs details in brackets and artist name variations as editable role and artist credits.

### Import 0.1.0

#### Added

- First version: import dashboard in the release relationship editor. Reads the credits of the linked Discogs release, matches artists via their Discogs links, maps roles to MusicBrainz relationship types, lets you choose level and tracks for each row, and stages everything in the editor. Submitting is always left to the user.
