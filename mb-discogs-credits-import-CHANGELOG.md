# MB x Vibecode – Changelog

All notable changes to both userscripts in this repository, newest first. Releases published together are listed together.

- **Import** = MB x Vibecode: Import Discogs credits (`mb-discogs-credits-import.user.js`)
- **COMPANION** = MB x Vibecode: Import Discogs credits COMPANION (`mb-discogs-credits-sync.user.js`)

## Overview

| Date | Import | COMPANION |
|---|---|---|
| 2026-10-05 | 1.6.0 – 1.9.2 | 1.0.0 – 1.0.2 |
| 2026-10-04 | 1.2.0 – 1.5.4 | – |
| 2026-10-03 | 1.0.5 – 1.1.0 | – |
| 2026-10-02 | 1.0.0 – 1.0.4 | – |
| 2026-10-01 | 0.8.0 – 0.9.8 | 0.2.1 – 0.3.0 |
| 2026-09-30 | 0.5.0 – 0.7.1 | 0.2.0 |
| 2026-09-29 | 0.3.0 – 0.4.0 | 0.1.0 – 0.1.1 |
| 2026-09-28 | 0.1.0 – 0.2.0 | – |

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
