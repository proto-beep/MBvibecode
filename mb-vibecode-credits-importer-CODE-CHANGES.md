# MB x Vibecode – Code changes

What changed **in the code** with each version of both scripts, newest first. It is meant for whoever works on the scripts (the maintainer, or the AI that writes them): which parts, functions, stored data, texts and tests a version touched. What a version means **for users** is in the [changelog](mb-vibecode-credits-importer-CHANGELOG.md).

- **Import** = MB x Vibecode: Credits Importer (`mb-vibecode-credits-importer.user.js`; until 3.3.0 `mb-discogs-credits-import.user.js`)
- **Companion** = MB x Vibecode: Credits Importer Companion (`mb-vibecode-credits-importer-companion.user.js`; until 1.6.0 `mb-discogs-credits-sync.user.js`)

## How this file is kept

From 3.5.0 on, every change to the code comes as a pull request that also adds an entry here, at the top: the version, then what changed in the code – parts and functions (new, changed, removed), state (`S`), browser storage, texts (i18n keys), rules of the register, CSS, event handlers, edit note, tests – and anything to watch out for. Functions are named as in the code, so they can be found with a search.

How far back the entries go:

| Versions | Source | Detail |
|---|---|---|
| Import 3.0.0 – 3.17.2, Companion 1.6.0 – 1.8.1 | the working sessions | written by hand, per version |
| Import 2.17.0 – 2.19.1 | the working session, and a comparison of the code of 2.16.0 and 2.19.1 | short notes for 2.19.x, otherwise the comparison |
| Import 0.9.2 – 2.16.0, Companion 0.2.2 – 1.5.0 | the versions uploaded to this repository (19 of the main script, 14 of the companion) | reconstructed: a comparison of the code from one upload to the next; versions in between are named, the changelog says what they do |
| Import 0.1.0 – 0.9.1, Companion 0.1.0 – 0.2.1 | none: the code of these versions was not kept | only the changelog |

The comparisons were made with a small script: functions and constants of the main level of the script are compared by their text (a "changed" function may have changed only in a comment), texts by their English keys, storage keys where the code reads, writes or lists them, rule ids where the register defines them.

## Import 3.17.2 · 2026-10-17

Liner notes from Bandcamp's "about" text (collect item 19).

- **Register:** new table **T027** – `LINER_NOT_NAME` (a first word that makes the last line no name: "Special Thanks", "Listen …", articles and prepositions) and `LINER_PARTICLE` (particles inside a name: van, von, de …), in `TABLES`.
- **Bandcamp adapter:** new `signatureName(text)` (a leading sign taken off, ", place, date" after the name at most three short parts, the name 2–4 words with capitals or particles inside, no digits, no "thanks/notes/credits"), `sentenceCount(text)` (split at `. ! ? …` and line breaks, parts with at least three words), `LINER_MIN_SENTENCES` (5), **`linerNotes(about)`** → `{ name, line, part, pi, n, at, len }` or `null`: the last non-empty line is the signature (b, c), else a name after a sign at the end of the last line behind a finished sentence (a; `part` the name, `pi` 1). Exported as `BANDCAMP.linerNotes`. `toRelease` adds a credit "Liner Notes" (`parseRoleNotation`, all tracks, `fromAbout: true`, line/part/pi/n for the Bandcamp view) and `release.liner` `{ name, at, len }` (the signature's place in `notes`); `aboutAt` computed once.
- **`groupCredits`:** a role entry keeps `fromAbout` while all its credits come from the about text; rows get `row.fromAbout` (so `setAboutRowsHidden` takes them along).
- **`autoPlaceFoundDates`:** a date found inside the signature goes into the pool named `liner.poolName` ("Liner notes – Jane Roe").
- **`loadRelease`:** log `log.linerFound`.
- **Texts (4 languages):** `liner.poolName`, `log.linerFound`; `about.offTitle` names the liner notes.
- **Tests:** new `t_linernotes.py` (A in Node: three places of the name, multi-paragraph prose; four sentences, "Special Thanks", "Thanks to everyone", a name after a sign without a finished sentence, the real "Invisible Places" text → none; B–D in the dashboard: entry, suggestion only, hint, pool name, jump to the name's line, about text left out and back). Golden file written anew: the only change is T027 in the rules window (sections `lists` and `tables`).


## Import 3.17.1 · Companion 1.8.1 · 2026-10-17

Credits switched off and on on Bandcamp (collect item 5).

- **New:** `BC_OFF_KEY` (`dci-bc-off:<MBID>`, an array of "name|role"), `S.bcOff` (a Set), `bcOffKey(row)` (`norm` of the entry's name as written – `rawName`, else `name` or the placeholder – and of the role), `saveBcOff()`, `bcCreditOn(row)` (forgets the flags and the key, logs `log.bcOn`, returns the level to go back to: `bcOffLevel`, else `defaultLevel`), `toggleBcCredit(row, off)` (off: `row.bcOff`, `row.bcOffLevel`, key stored, `log.bcOff`, `setLevel(row, 'skip')`; on: `setLevel(row, bcCreditOn(row))`), `bcOffHtml(row)` (note `.dci-bcoff` in both branches of `roleCell`).
- **`loadRelease`:** with Bandcamp, rows with places whose key is in `S.bcOff` are set off right after the rows are made (level `skip`, the level kept). **`forgetImport`:** `BC_OFF_KEY` cleared, `S.bcOff` emptied.
- **Level buttons (`case 'level'`):** a level other than "Skip" on a row switched off calls `bcCreditOn` first.
- **`onFromDiscogs`:** new message `toggle-credit` `{ row, off, releaseId }` (only with Bandcamp loaded and the same release).
- **`sendDiscogsStatus`:** Bandcamp items get `off: true`; labels `off`, `on`, `isOff`.
- **Texts (4 languages):** `dgStatus.off`, `dgStatus.on`, `dgStatus.isOff`, `bc.offNote`, `log.bcOff`, `log.bcOn`.
- **Companion 1.8.1:** MB side relays `toggle-credit` from `fromDiscogs`; the click handler of `initSourceSide` sends `toggle-credit` for `.dci-bc-off` (before the marks). `renderBandcampStatus`: each mark in `.dci-bc-markwrap` with its ⊘ `.dci-bc-off` (`data-row`, `data-off`), `.dci-bc-isoff` and "(switched off here)" in the title for credits off; a place whose credits are all off gets its part wrapped in `.dci-bc-offtext` (`BC_OFF`) before its marks are put in front of it; old wrappers removed / unwrapped first. `BC_SKIP` skips `.dci-bc-markwrap`; `bcInsert` also steps out of `.dci-bc-offtext`. CSS: ⊘ shown on hover above its mark (absolute, no shift of the text), greyed marks and struck-through text.
- **Tests:** new `t_bcoff.py` (A–E: ⊘ on hover, off → "Skip" + note + grey, a group, on again with its level, kept after reload, a level chosen switches on, "Delete stored import"); `t_bcview.py` leaves ⊘ out of the text after a mark.


## Import 3.17.0 · Companion 1.8.0 · 2026-10-17

Bandcamp view in the companion (collect items 4 and 7), milestone.

- **Text adapter (`TEXT.parse`):** every credit and company also gets `part` (the clause of its line, from `clauses()`), `pi` (the number of that clause on the line, 0 = first) and `n` (which of the lines with the same text it is, counted in `lineCount`); `at()` adds them together with `line`. "Role Name" lines and ℗/© lines: the line is the part, `pi` 0.
- **Bandcamp adapter:** `companion: 'bandcamp'` (Discogs: `companion: 'discogs'`; `companionReleaseId()` unchanged); credits and companies of track pages get `page` (the track's `title_link`) and `pos` (its position).
- **New `addSrcRef(refs, c)`:** `{ page, line, part, pi, n, pos?, about? }`, once per place; `groupCredits` (`entry.refs`), `groupCompanies` (`role.refs`); rows get `row.srcRefs` in `loadRelease` (credits and companies).
- **Fixed in `groupCompanies`:** since 3.16.1 (`else if (!c.fromAbout) delete same.fromAbout;` in the else-if chain) the tracks of a role found again were joined only when the credit came from the about text; now `fromAbout` and the tracks are handled one after the other.
- **New:** `viewSite()` ('discogs' / 'bandcamp' from `S.source.companion`), `VIEW_NAMES`, `trView(key, params)` (`${key}Site` with `{site}` when that key exists, else `key`), `logView(level, key, params)` (`log.${key}Site`), `syncSite()` (the tabs of the site from `S.sync.sites`; without it Discogs = `S.sync`, Bandcamp `{ old: true }`).
- **`sendDiscogsStatus`:** Bandcamp items `{ row, role, status, unmapped, mb, refs: [{ page, line, part, pi, n, status, pos?, t?, r? }] }` – rows with places in the credits only (places in the about text and rows of a supplement left out); `ofTrack(pos)` gives the status and targets of one track, shared with the Discogs `byPos`. The message gets `site`; `artwork` only for Discogs.
- **`onFromDiscogs`:** `status` keeps `msg.sites` (`S.sync.sites`); `focus-row` and `result` log through `logView`, `result` with `trView`.
- **`showOnDiscogs`:** `site` in the command; for Bandcamp nothing without `S.sync.sites` (an old companion would send it to a Discogs tab). **New `bandcampPayloadForRows(rows)`** (`refs` of the rows, without supplements). **`showSourceOf`** for Bandcamp: a row → its places, an entry head → the places of all its rows; a track of the works matrix as before (`positions`).
- **`syncStatusHtml`, `syncModeHtml`, `updateSyncArea`:** `syncSite()`, `trView`; `sync.oldSite` for an old companion; the layout key includes the site (drawn anew when the source changes); `data-dg-artwork` only for Discogs. `sync-load` and `data-sync-reload` send `site`; the logs `dgStatus`, `dgRelease`, `dgReload`, `syncMode` go through `logView`.
- **New `srcRefsHtml(row)`** in both branches of `roleCell`: `bc.fromTrackPage` with links to the track pages (`.dci-bcpages`, origin from `BANDCAMP.urlKey`), `about.from` when all places are in the about text.
- **Texts (4 languages):** `…Site` forms of `sync.off`, `sync.noTab`, `sync.connected`, `sync.found.loading`, `sync.found.none`, `sync.found.no-tab`, `log.discogsJump`, `log.syncMode`, `sync.dgStatus`, `sync.dgStatusTitle`, `log.dgStatus`, `log.dgFocus`, `sync.trackHoverTitle`, `sync.reloadTitle`, `log.dgReload`, `sync.otherPage`, `sync.loadTitle`, `sync.dgReleaseTitle`, `log.dgRelease`; new `sync.oldSite`, `bc.fromTrackPage` (`.one`/`.other`), `bc.trackPageTitle`, `about.from`, `ms.3.17.0`; changed `settings.t.discogs` ("Discogs and Bandcamp view"), `settings.discogsHint`.
- **Milestone:** `MILESTONES` 3.17.0 ("Credits Importer 3.17.0 · Companion 1.8.0").
- **Companion 1.8.0:** `@match *://*.bandcamp.com/*`; `isBandcamp`, `SITES`, `siteOf(x)` (no site = Discogs). MB side: `pickTab(tabs, releaseId, site)`, `status()` with `sites` (and the Discogs fields as before, for older main scripts), `mayOpen` also `https://*.bandcamp.com/`, `show` and `reload` by `siteOf(msg)`. `initDiscogsSide` → **`initSourceSide(side)`** with `DISCOGS_SIDE` and `BANDCAMP_SIDE` (`id`, `artwork`, `releaseId()`, `pageFor(cmd)` – '' this page, a URL to load, `null` none –, `locate(cmd)`, `renderStatus(map)`, `trackAt(target)`); the heartbeat `tab:<id>` has `site`; commands and status maps of another site are left alone. Bandcamp: `bandcampPage()` (album URL from the path or `album_url` of `data-tralbum`, track page path, track number), `bcCredits()`, `bcAbout()`, `bcLow`, `bcNeedle`, `BC_SKIP`, `bcStream(root)` (the text with the place of each character, lines at `<br>`, without marks and Bandcamp's "..."/"more"), `bcFindLine`, `bcPartRange`, `bcSentence`, `bcInsert`, `bcWrap`/`bcUnwrap` (`.dci-bc-hl`), `bcExpand` (opens `.bcTruncateMore`: Bandcamp's link, else shown directly), `renderBandcampStatus` (marks inserted from the end, those of one place together as a fragment; `bcInsert` puts them before a marked stretch, not into it), `bandcampLocate`. **Fixed:** the delayed first `showMap` after the page opens uses `lastMap || GM_getValue('statusMap')` (it used the map read at the start and could replace a newer one). Release page: `refs` checked like `byPos` (`each`); a place without targets of its own takes the status of the whole credit. CSS `.dci-bc-hl`.
- **Tests:** new `t_bcview.py` (A–G); harness `bc_html()` (a Bandcamp album or track page built like real ones: track table, about, credits with `<br>` after "released …", Bandcamp's shortening) and `open_bandcamp()` (the companion in the top frame only, also after the tab loads another page); `t_register.py` leaves `part`/`pi`/`n` out of the golden data; `t_notice.py` (3.17.0). Checked locally on the maintainer's saved pages (Invisible Places, a Kungens Män track page): marks before each part, every row jumps to its credit.


## Import 3.16.2 · 2026-10-17

Neutral texts for other sources (collect item 17).

- **New:** `srcLabel()` (the source's name, "pasted text" for the text source: `src.textLabel`), `trSrc(key, params)` – the text as it is while Discogs is loaded (`S.release && S.source === DISCOGS`), else `${key}Any` with `{src}`.
- **Changed (now `trSrc`):** `instrAsk.ask` (`instrumentAskHtml`), `matrix.noWriters` and `matrix.empty` (works matrix), `roleCredit.fromDiscogs` / `roleCredit.fromTag` (role credit tag), `media.nowTitle`, `dm.chooseSingle` / `dm.chooseSingleTitle`, `datefind.alsoRangeTitle`, `pools.reload` (button and question). `manual.rolePlaceholder` is neutral in every language (manual entries do not depend on the source).
- **Looked through and left:** texts of the Discogs view (`sync.*`, `dgStatus.*`), Discogs series, Discogs aliases, the Discogs API errors, `log.discogsLoaded`, the milestones (history), `datefind.order*` (only with a Discogs release country).
- **Texts (4 languages):** `src.textLabel`, `instrAsk.askAny`, `matrix.emptyAny`, `matrix.noWritersAny`, `roleCredit.fromDiscogsAny`, `roleCredit.fromTagAny`, `media.nowTitleAny`, `dm.chooseSingleAny`, `dm.chooseSingleTitleAny`, `datefind.alsoRangeTitleAny`, `pools.reloadAny`; `manual.rolePlaceholder` changed.
- **Tests:** new `t_srctexts.py` (Discogs: the texts as before; a pasted text: question, role credit tag, "no writers").


## Import 3.16.1 · 2026-10-17

"Leave out the about text" (collect item 6).

- **Bandcamp adapter (`toRelease`):** companies from the "about" text get `fromAbout: true`; the release gets `aboutAt` (where the about text begins in `notes`: after the credits and two newlines, 0 without credits, `null` without an about text).
- **`groupCompanies`:** a role keeps `fromAbout` only while every credit of it comes from the about text; **`loadRelease`:** company rows of such roles get `row.fromAbout`; with `S.aboutOff` they are hidden right after the rows are made (`setAboutRowsHidden(true)`).
- **New:** `ABOUT_KEY` (`dci-about-off:<MBID>`, `{ stash: { pool, cells } }` while off), `S.aboutOff`, `fromAboutText(find)` (a date find at or after `aboutAt`), `setAboutRowsHidden(hide)` (`aboutHidden`, level to `skip` with `aboutLevel` kept, and back), `setAboutOff(off)` (rows; off: the pool entries of about-text finds – `found` `notes:<i>` or `notes:<i>:…` – and the matrix cells using them go into the stash; on: they come back from it; `savePool`, `dmChanged`, log `log.aboutOff` / `log.aboutOn`, renders).
- **Changed:** `autoPlaceFoundDates` skips about-text finds while off (else they would come back when no dates of the notes are left); `groupHtml` / `rowHtml` add `dci-about-hidden` (a group only when all its rows are hidden); `renderSource` shows the checkbox `data-f="about-off"` after "Delete stored import …" when `rel.aboutAt != null`; `onChangeInner` case `about-off`; `forgetImport` clears `ABOUT_KEY` and `S.aboutOff`.
- **CSS:** `#dci-overlay .dci-about-hidden` (and the track list of such a row) not shown.
- **Texts (4 languages):** `about.off`, `about.offTitle`, `log.aboutOff`, `log.aboutOn`.
- **Tests:** new `t_aboutoff.py` (the checkbox next to "Delete stored import", ticked: Loft hidden, Studio Nord stays, June dates out, March stays, stored; off again: back with "credited as" typed before; kept across a reload; reset by "Delete stored import").
- **Not covered:** a supplement from Bandcamp (its about-text places stay suggestions as before).
- **Docs:** the headings of the entries 3.15.0 – 3.16.0 in the changelog and in this file had been lost each time the next entry was added (3.15.0 and 3.15.1 also on `main` after PR #7); put back.


## Import 3.16.0 · 2026-10-17

The menu "Settings" (collect item 13) and the stored works of the artists (collect item 12). Milestone.

- **New (settings of the works comparison):** `AW_SETTINGS` (`awMax` 100–10,000 step 100 default 4,000; `awSlowSec` 1–120 default 10; `awSlowN` 100–10,000 step 100 default 900; `awDays` 1–90 default 7; keys `dci-aw-max`, `dci-aw-slow-s`, `dci-aw-slow-n`, `dci-aw-days`), `awValue(name, v)` (clamped, rounded to the step), `S.awOn` (`dci-aw-on`, stored only when off).
- **`loadArtistWorks`:** one budget `S.awMax` for linked works and recordings (`entry.max`, `entry.linkedRead`); `capped` also when linked works are left out; when the works use the whole budget one request `recording?artist=…&limit=1` gives the number of recordings for the message; the recording requests ask for `min(100, rest)`. `ARTIST_WORKS_MAX` is gone.
- **`runArtistWorks`:** returns at once (and clears the hits) when `S.awOn` is off; per target first `awGet` – a fresh record (`awFresh`: younger than `S.awDays`, not capped below `S.awMax`) becomes the entry (`awUnpack`, log `log.artistWorksStored`); else read, `readAt` set, `awPut(awPack(…))`; the slow message uses `S.awSlowSec` and `S.awSlowN`; the capped message `n` = linked + recordings, `max` = `e.max`.
- **New (store):** `AW_DB` (`dci-works`, store `artists`, keyPath `mbid`), `awDb()`, `awStore(mode, fn)`, `awGet`, `awPut`, `awCount`, `awClear`, `awPack(mbid, e, readAt)` (works as arrays `[gid, title, aliases, type, disambiguation, 'l'|'r', recording]`), `awUnpack(rec)`, `awFresh(rec)`; `rememberArtistWork(i, gid, title)` – called by `work-pick` and after a work was created (`rememberCreatedWork`): the release-credit artists and the artists of the rows on that track get the work (memory and store, `readAt` kept).
- **New (menu):** `SETTING_TOPICS`, `TOPIC_KEYS` (stored keys per topic), `SHARED_SWITCHES`, `settingsHtml()` (topics as `data-act="settings-topic"` buttons, `S.settingsTopics`; reuses `data-f` controls of the dashboard – `lang`, `bc-tracks`, `mx-codes`, `fill-credits`, `stage-cap`, `dm-auto`, `pools-keep`, `zoom-in/out`, `place-toggle`, `syncModeHtml()`, `sourceOrderHtml()` – and has fields of its own with `data-set`: `log-open`, `log-place`, `aw-on`, `awMax`, `awSlowSec`, `awSlowN`, `awDays`, `wattr-long`, `cap-limit`), `renderSettings()` (keeps the focus), `syncSharedSwitches()` (the dashboard's copies of shared switches, the footer's cap label `[data-el="cap-label"]`), `settingsAfterEvent(e)` (overlay click/change listener, after a `setTimeout` so that the document-level handlers of the Discogs view have run), `settingsChange(el)` (`onChange` hands `data-set` fields to it), `resetTopic(t)`.
- **Changed:** head button `data-act="settings-open"` and panel `[data-el="settings"]` (after the reset panel; opening one closes the other); `renderAll` calls `renderSettings`; click cases `settings-open` (counts the store with `awCount`), `settings-topic`, `settings-reset` (confirm), `aw-clear` (confirm, log `log.artistWorksCleared`). `SETTINGS_KEYS` gains `dci-aw-on` and the `AW_SETTINGS` keys; `resetSettings` sets them back and clears the store. The footer's cap text is a `span[data-el="cap-label"]`.
- **Texts (4 languages):** `settings.*` (button, title, hint, topics `settings.t.*`, `settings.resetTopic`, `settings.resetAsk`, `settings.place*`, `settings.logOpen`, `settings.logPlace`, `settings.discogsHint`, `settings.aw*`, `settings.awStored`/`settings.awClearAsk` one/other, `settings.wattrLong`, `settings.capOn`, `settings.capLimit`, `settings.aria.*`), `log.settingAw`, `log.settingValue`, `log.settingsTopicReset`, `log.artistWorksStored` and `log.artistWorksCleared` (one/other), `ms.3.16.0`; `msg.artistWorksCapped` and `log.artistWorksCapped` say "works and recordings". `MILESTONES` gains 3.16.0.
- **CSS:** `.dci-settings`, `.dci-set-head`, `.dci-set-topic`, `.dci-set-tgl`, `.dci-set-body`, `.dci-set-row`, `.dci-set-reset`.
- **Tests:** new `t_settings.py` (menu and topics, shared switches both ways, a value with steps, a topic's "↺" with its question, the store across a reload, clearing it, switched off, a Discogs-view button in the menu); `t_artistworks.py` D sets `dci-aw-max` = 2,000 (the default is 4,000 now), B checks the chosen work in the store of Bass Man; `t_notice.py` expects 3.16.0, 3.15.0, 3.12.0 and no longer 3.10.0.
- **Watch out:** the log of a release is kept across reloads – a test that waits for a log line after loading again must wait for one more than before.


## Import 3.15.3 · 2026-10-17

The suggestions as a wrapping block (addition to collect item 15).

- **Changed:** `matchHtml(a)` = `matchHtmlInner(a)` + `suggestStackHtml(a)` (the stack always after the head line); `matchHtmlInner` takes no stack any more, `editor()` shows the red badge alone again; `.dci-match-col` is gone.
- **CSS:** `.dci-sugg-stack` is `flex: 1 0 100%` (a line of its own in the flex-wrap `.dci-gmatch`) with `flex-wrap: wrap` in a row; `.dci-suggmore` without `align-self`.
- **Tests:** `t_suggstack.py` – order mark → field → buttons → block, the block below the mark and left-aligned with it, row + wrap, one line with 5, two with all 8, more when the panel is 560 px wide.


## Import 3.15.2 · 2026-10-17

Suggestions stacked (collect item 15), rows as boxes (collect item 16).

- **New:** `SUGG_VISIBLE` (5), `suggestStackHtml(a)` – alias hits (`data-act="alias-use"`) and name hits (`data-act="name-use"`) as one stack `.dci-sugg-stack`; its title = the heads (`match.aliasSuggest`, `match.nameSuggest` / `match.linkSuggest` / `match.placeholderSuggest`), each suggestion's title = head + its own title; marks `.dci-similar`: `match.viaAlias`, `match.similarName`, new `match.markSpelled` (`a.strictMiss`), `match.markRelease` (`a.releaseMbid`); more than 5: `<button class="dci-suggmore" data-act="sugg-more">` (`match.suggMore` / `match.suggLess`), state `a.suggOpen`.
- **Removed:** `aliasSuggestHtml`, `nameSuggestHtml` (replaced by the stack).
- **Changed:** `matchHtml(a)` passes the stack to `matchHtmlInner(a, stack)`; its `editor()` puts the red badge and the stack into `.dci-match-col` (not for `match.changeLabel`); other states append the stack. Click case `sugg-more` toggles `a.suggOpen` and calls `updateGroupHeader`. `suggestByName` keeps up to 25 hits (was 5); its log lists 5 and "… (+n)".
- **CSS:** `.dci-match-col`, `.dci-sugg-stack` (column), `.dci-suggmore` (2px solid, bold), `.dci-gmatch:has(.dci-match-col)` top-aligned. Rows: `.dci-rows tr.dci-row` with frame, left stripe `color-mix(var(--kind) 55%)`, radius, gap; every second row `color-mix(var(--kind) 7%)` (with a plain fallback colour first); an open `tr.dci-tracksrow` continues the box (`:has(+ …)`); the old td stripe `#faf9fd` is gone. Wide layout (`@container (min-width: 1150px)`): the level column `calc(var(--u) * 200)` instead of `auto`.
- **Texts (4 languages):** `match.markSpelled`, `match.markRelease`, `match.suggMore`, `match.suggLess`.
- **Tests:** new `t_suggstack.py` (eight artists of one name: order red mark → stack → field, tooltip instead of text, 5 + "+ 3 more" bold and solid, all 8 and "− fewer", assigning); `t_textrules.py` and `t_bandcamp.py` read the explanation from the stack's tooltip and a suggestion's name without its mark.


## Import 3.15.1 · 2026-10-17

Mastering only on the release level (collect item 14), special purpose artists left out (collect item 11).

- **New (section 2d):** `SPECIAL_ARTISTS` (T026, `[mbid, name]` of the 7 official special purpose artists, 4 subsets with an MBID and MusicBrainz Test Artist), `SPECIAL_ARTIST_NAME` (a name entirely in square brackets), `isSpecialArtist(mbid, ...names)`; `TABLES` entry T026 (`show()` as pairs).
- **`DATE_GROUPS`:** `releaseOnly: true` for `remastering` and `mastering`; T016's `show()` adds "– release level only".
- **`applyMatrixColumn`:** a row not on recording/work level in a `releaseOnly` group takes every cell of the column whose track groups touch the row's tracks (or that has none); the `rel` mark is not used there. Other groups unchanged.
- **`matrixCellHtml`:** no `dm-rel` checkbox in `releaseOnly` columns.
- **`levelCell`:** when only one level (besides "Skip") is offered for the row's MB type, the group has the title `level.onlyHere`. The levels themselves were already limited to those where MB has the type (`levelsOfType`, `buildIndex` leaves out deprecated types) – on MusicBrainz a mastering row has no "Recording".
- **`artistWorkTargets`:** special purpose artists go to `out.special` instead of the targets; `runArtistWorks` logs `log.artistWorksSpecial` once per import (`S.artistWorksSpecialLogged`, reset in `loadRelease`).
- **`renderWorksBackground`** (the redraw for hits of the works of the artists): waits while `S.dmDrag` is set (`S.worksRenderAfterDrag`), checks again every 300 ms. Tried and taken back: drawing the end of `autoSearchWorks` through it as well – deferred until a field of the matrix was left, that redraw came 400 ms after the mousedown of the next drag and lost the drop (`t_mxdrop.py` B2 failed in 4 of 5 runs side by side; with `renderWorks` as before 5 of 5 pass).
- **Texts (4 languages):** `log.artistWorksSpecial`, `level.onlyHere`.
- **Tests:** new `t_special.py` (Various Artists and "[soundtrack]" not browsed, Test Band is; logged once; T026 in the window), new `t_mastering.py` (two mastering rows on CD 1 / CD 2: only "Release" and "Skip" with the title, no "Release level" in the column, May/June by track group, July for both); harness: `lt(…, deprecated=False)`, artist–recording "mastering" (136) deprecated, artist–release "mastering" (42) added; `register_golden.json` written anew – the mastering rows of the pasted texts now have type 42 (was none: the mock had no release mastering), T016's notes, T026.


## Import 3.15.0 · 2026-10-17

The works of the artists in the works matrix (collect item 9b). Milestone.

- **New (section 4, after the same-named works):** `ARTIST_WORKS_MAX` (2,000), `artistWorkTargets()` (a `Map` MBID → `{ name, why }`: `S.releaseCredit` first, then rows with an MB artist whose type is in `WRITER_TYPES`, then instrument / vocal / performer rows; companies, "other" artists and skipped rows not), `tracksWithoutWork()` (`matrixTrack`, no placeholder title, no `worksForTrack`), `loadArtistWorks(mbid, name, onPage)` (browse `work?artist=…&inc=aliases` and `recording?artist=…&inc=work-rels`, 100 per request; `via: 'linked' | 'recorded'`, `recording` = the recording's title; `capped` when 2,000 recordings were read), `matchArtistWorks()` (title or alias `withinOne` the normalized track title, as `sameNamed`; a hit has `artistWork: true` and its origin in `writers`; returns true when the hits changed), `renderWorksBackground()` (draws the works matrix anew only when no input, select or textarea in it has the focus; otherwise 400 ms after that field is left – a background redraw took the focus in `t_focus.py` and stopped the smooth scroll of `t_jump.py`), `runArtistWorks()` (one run at a time, `S.artistWorksAgain` chains the next; draws anew only when `matchArtistWorks()` reports a change).
- **`mbWs(path, { background })`:** counts the dashboard's own requests (`mbForeground`); new `mbWsIdle(path)` waits (300 ms steps) while there are any, then queues a background request – the queue of one request per 1.1 s stays the same.
- **State:** `S.artistWorks` (MBID → what was read, kept for the page session, not reset by `loadRelease`), `S.artistWorkHits` (track index → hits) and `S.artistWorkTargets`, both reset by `loadRelease`; `S.artistWorksRunning`, `S.artistWorksAgain`, `S.worksRenderOnBlur`.
- **Changed:** `sameNamed(i)` = the writers' search results plus the artist hits not in them (so `works-pending`, `works-pending-all` and the "＋ New work" question count them too). `renderWorks` work cell: the list is shown whenever `sameNamed` has works (before: only with a finished writers' search), heading `matrix.sameArtists` when an artist hit is in it; the "no writers" mark only without works. `loadRelease` calls `runArtistWorks()` after `autoSearchWorks()`; `scheduleWorkRecheck` calls it when `artistWorkTargets()` has an MBID not compared yet.
- **Messages:** after 10 s for one artist with more than 900 works and recordings to read: `msg.artistWorksSlow` (once per artist); capped: `msg.artistWorksCapped`.
- **Texts (4 languages):** `matrix.sameArtists` (one/other), `works.viaLinked`, `works.viaRecorded`, `msg.artistWorksSlow`, `msg.artistWorksCapped`, `log.artistWorks` (one/other), `log.artistWorksSlow`, `log.artistWorksCapped`, `log.artistWorksDone` (one/other), `log.artistWorksNone`, `ms.3.15.0`; `matrix.dupWarn` and `matrix.dupWarnAll` without "by these writers". `MILESTONES` gains 3.15.0.
- **Tests:** new `t_artistworks.py` (A release artist's work, a performer's cover, no duplicate with the writers' search; B order and log, picking; C read once per session; D 2,500 recordings: the message after 10 s, capped at 2,000; E no redraw while a date field of the matrix is typed in, the hit shown after leaving it); harness: browse `work?artist=` from `ARTIST_WORKS`, `recording?artist=` from `ARTIST_RECORDINGS` (a number: that many recordings without works), recorded in `BROWSES` (not in `WORK_QUERIES`); `t_notice.py` expects 3.15.0, 3.12.0, 3.10.0 and no longer 3.5.0.
- **Watch out:** every import now makes two background requests per artist with an MBID (more for large catalogues); a dashboard request waits at most for the one background request already queued.

## Import 3.14.1 · 2026-10-17

Arrows in the status bar (collect item 8).

- **New:** `jumpDashboard(where)` – `'top' | 'bottom'`: in window mode the dashboard's body is scrolled, in page mode the page (to the dashboard's top or bottom).
- **Changed:** the footer gets `<span class="dci-jump">` with two buttons `data-act="jump-top"` / `"jump-bottom"` (▲ ▼); the click handler has the case. CSS `.dci-jump`.
- **Texts:** `footer.jump`, `footer.top`, `footer.bottom` (4 languages).
- **Tests:** new `t_jump.py` (window and page, clicked by `evaluate` as the log window may cover the footer).

## Import 3.14.0 · 2026-10-17

Rules for free credits texts, for all sources (collect item 10).

- **New tables (section 2d, each in `TABLES` with `show()`):** `TEXT_TIME_AFTER_NAME` (T020), `TEXT_WHAT_WORDS` (T021), `TEXT_MADE_BY` (T022), `PLACEHOLDER_WHO` (T023), `TEXT_LABEL_LINE` (T024), `TEXT_NOT_NAME` (T025).
- **Rules:** R060 pattern gains `played by`; date rule D007 also matches two months of one year (`${P.M}` and / & / und / y / et / "/" `${P.M}`, optional "de", `${P.Y}`), its note names "September and October 2026".
- **`TEXT.parse`:** new helpers `addPlaceholder(said, role, scope)` (a credit whose `who` has no name, `placeholder: said`), `roleOf(word)` ("played" → "Played By" when the register knows it), `firstSentence(t)`. `byRole` strips `TEXT_WHAT_WORDS`; `byRoles` also tries `cap(l)` without "By". The "… by" branch: a line in the made-by form (`TEXT_MADE_BY`) takes its roles from there; `right = firstSentence(right).replace(TEXT_TIME_AFTER_NAME, '')`; `PLACEHOLDER_WHO` → `addPlaceholder`. `TEXT_LABEL_LINE` lines are skipped (not listed as not recognized). "Role Name" lines only when nothing else matched: a role of 1–3 words (`isRole`), a name of 2–4 words without a `TEXT_NOT_NAME` word, not all words roles.
- **Core:** `groupCredits` keys placeholders `ph:<said>` and carries `placeholder`, `releaseMbid`; new `placeholderCredits(credits)` turns a placeholder credit into one credit per release-credit artist with an MBID (used in `loadRelease` and the supplement); the artist object keeps `placeholder` and `releaseMbid`; `suggestByName` puts the release artist into `nameHits`; `nameSuggestHtml` heads it with `match.placeholderSuggest`; log `log.placeholderSuggested`.
- **Texts:** `match.placeholderSuggest`, `log.placeholderSuggested` (4 languages); the notes of T020 – T025 are in English, as those of the other tables.
- **Tests:** new `t_textrules.py`; `register_corpus.json` gains a text in the form of the credits of "Invisible Places" (other names) and date phrases (now 7 texts, 55 dates); `register_golden.json` written anew – R060's pattern, D007's note, the new tables and the new corpus entries differ, nothing else.

## Import 3.13.2 · 2026-10-17

The rules window names Discogs only with Discogs (collect item 3).

- **New:** `RULES_ANY` (8 keys → their neutral variant), `trRules(key)` (the Discogs text while `S.release && S.source === DISCOGS`, else the neutral one), `refreshRulesWindow()` (label `[data-rf="test-label"]` and `renderRulesBody()`), called in `loadRelease` once the new source is set.
- **Changed:** the 8 uses in `rulesTables`, `ownRulesHtml`, the own-rule form check and `ruleTestHtml` use `trRules`; the label of the test field is a `<span data-rf="test-label">`.
- **Texts:** `rules.testAny`, `rules.testHintAny`, `rules.colRole`, `rules.kindRoleAny`, `rules.kindInstrumentAny`, `rules.fRoleAny`, `rules.fSpellingAny`, `rules.formIncompleteAny` (4 languages).
- **Tests:** new `t_rulesname.py` (Discogs → text → Discogs with the window open); `register_golden.json` written anew – only the column heads and own-rule texts of the window differ (its golden part is taken after a text import).

## Import 3.13.1 · 2026-10-17

Phrases after "at" that are no place (collect item 2).

- **New:** `NOT_A_PLACE` (T019, section 2d) – "the same time", "the time", "that/this/the point|stage|moment", "the end|beginning|start" (alone or before "of"), "once", "night", "dawn", "dusk", "midnight", "noon", "least", "all", "times", "first", "last" (alone), "first|last" before week, weekend, day(s), night(s), time, month, year, session(s), take(s). In `TABLES` with `show()`.
- **Changed:** `TEXT.placeOf` gives `null` for them (as for `PRIVATE_PLACE`), so `place()` adds nothing.
- **Tests:** `t_about.py` part E; `register_golden.json` written anew – the corpus lines "Mixed at last, in the summer of 1980" and "recorded at the same time as the album" give no place now (listed as not recognized), the window lists T019.

## Import 3.13.0 · 2026-10-17

Name suggestions for names with an initial (collect item 1).

- **Changed:** `suggestByName` – for a person whose `nameWords` include a one-letter word and at least one longer word, a second search `artist:(written words) OR alias:(…)` (`limit=25`); its hits are added to those of the first search (no duplicates), then `nameFit` decides as before ("similar" when the initials fit first and middle names in order).
- **Tests:** new `t_initials.py` (T. Snekkestad, Barry J. Guy, K. Tanaka vs. Kenji/Hiro, no second search without an initial).

## Import 3.12.1 · 2026-10-17

Two fixes (collect items 10 and 9a of 2026-10-17).

- **`makeMovable`:** a press on `summary` or inside `details` does not move the window (the list `.dci-unrec` in the head `.dci-head` could not be opened in window mode: `preventDefault` and `setPointerCapture` took the click).
- **`loadRelease`:** resets `S.workSearch` (it was never reset, so a second import kept the results of the first and `autoSearchWorks` skipped its tracks) and asks a running search to stop (`S.searchCancel`).
- **`autoSearchWorks`:** when a search is running, it sets `S.searchAgain` and the running one starts it again when it ends (no search lost between two imports).
- **New:** `writerSig(people)` (the MB writers of a track as text), `scheduleWorkRecheck()` – called by `refresh()`, 800 ms later it searches again the tracks without a work whose writers (`creditedWritersOf`) differ from those of their search; `runWorkSearch` stores `sig` with every state. Covers every way a writer gets an MBID or a writing role changes, without hooks in each handler.
- **Texts:** `log.workRecheck` (one/other, 4 languages).
- **Tests:** new `t_recheck.py` (A the list opens in the window, B a text writer assigned → searched and found, C no new query without a change, D a new import searches itself); harness: `/ws/2/work?query=` answered from `WORK_SEARCH` (a work is found when one of its artists is in the query's `arid:`), queries recorded in `WORK_QUERIES`.

## Import 3.12.0 · 2026-10-17

The role rules as data (collect item 4, step 2). Milestone.

- **New:** `ROLE_RULE_DATA` (section 2c) – all 99 role rules in their order (first hit wins): `id`, `kind`, `note`, `re`, `types`, `level`, R062 also `special: 'S004'`; a simple rule also `work`, `flags` (checkbox names), `eng` (engineer details → `engFlags()`), `credit` (`true` or a text), `primaryCands`, `notes`. `DESIGN_TYPES` (the types of R062, R064–R067).
- **Changed:** `roleRules(c)` builds the list from `ROLE_RULE_DATA`: `test` is `is(r.re)` and `run` is `out(r.types, extraOf(r))` unless the object `code` has them under the rule's id. `code` holds the 25 special rules (R001, R009, R011, R012, R018, R019, R025, R026, R031, R033, R034, R036, R038, R039, R041, R042, R043, R046, R051, R097, R062, R063, R086, R095, R096; their bodies unchanged) and 5 simple ones whose result needs code (R040 and R089: role credit only for some words; R065: "lithography" only without details; R069: the role as written; R084: the word after "A&R" as task). The pattern of a simple rule is written once now (before: `re` for the window and again in `test`). The local `wrk` is gone (only data used it).
- **Metadata = behaviour:** `types` and `level` of a simple rule are what it gives; before, 27 rules showed something else in "Mapping rules" (R002–R004, R006, R007: recording → work; R070–R072, R076–R080, R082, R083, R087, R088, R090–R094: recording → release; R084: recording → release_group; R064–R067: no types → `DESIGN_TYPES`). The mapping did not change.
- **Texts:** `ms.3.12.0`; `MILESTONES` gets 3.12.0.
- **Tests:** `register_golden.json` written anew – only the 27 rules' `level`/`types` and the "roles" section of the window differ from 3.10.0, every mapped role, company role, date and text is the same; `t_notice.py` (milestones 3.12.0 / 3.10.0 / 3.5.0).
- **Watch out:** a new simple rule is a data line; it needs code only when its test or result depends on more than its pattern. Keep the order (R098 before R003: "Music and lyrics by" before "Music by").

## Import 3.11.0 · 2026-10-17

The mapping register in one section (collect item 4, step 1; the maintainer: "vor den Punkten 1-3").

- **Sections:** new **2. Mapping register** before the sources (the sources are **3** now, the date and MusicBrainz form helpers that stayed behind them **3b**), with 2a role notation (`splitTopLevel`, `parseRoleNotation`, `parseRoles`, `splitEngineerTasks` – from the old section 2), 2b own rules and switches, 2c rule lists, 2d tables and word lists, 2e functions that apply the rules (`mapRole`, `mapCompanyRole`, wording, role credits …), 2f dates in free text (`DATE_MATCHERS`, `findDates`). Everything of the old sections 3/3a moved there unchanged; orphaned doc comments went to their functions (`mapRole`, `suggestRoleCredit`, `caseWord`, `COMPANY_ROLES`, `lucenePhrase`).
- **Moved into 2d:** from the text adapter `NAME_SEP`, `ROLE_SEP`, `AND_SEP`, `TRACK_WORDS`, `MONTHS` (renamed `TEXT_NAME_SEP`, `TEXT_ROLE_SEP`, `TEXT_AND_SEP`, `TEXT_TRACK_WORDS`, `TEXT_MONTHS`), `INSTRUMENT_MODIFIER`, `PRIVATE_PLACE`; `ENGINEER_TASK_RE` (from section 2); `TEXT_COMPANY_RE` (from the core; `isTextCompanyRole` stays there); `DATE_GROUPS` (from the date matrix); `LIVE_TITLE` (was local in `applyLiveDefault`); `NOTE_ROLES` (from the notes' track lists). The adapters read these directly (the register is defined before them); `isRole`/`isCompanyRole` still come through the context, as they need MusicBrainz.
- **`DATE_GROUPS` as data:** `types` (MusicBrainz type names) per group, `only`/`onlyNote` for Remastering; `test(n, row)` is made from them once at load (same results as the old functions).
- **Table ids T005–T018** in comments and in `TABLES`, which has `show()` for T003 and T005–T018 (words, pairs or a pattern).
- **Window "Mapping rules":** new section `lists` (`rules.lists`, `rules.listsHint`) with `patternWords(re)` (a plain pattern as a list of words, "track(s)") and `tableShowHtml(t)`; CSS `#dci-rules h4`, `.dci-rules-list`.
- **Texts:** `rules.lists`, `rules.listsHint` (4 languages).
- **Tests:** new `t_register.py` with `register_corpus.json` (frozen from 3.10.0: 1,204 roles, 101 company roles, 52 date phrases, 6 texts, 70 instrument names) and `register_golden.json` (A Node: `parseRoles`, `mapRole`, candidates, role credits, wording, questions, flags, the rule list, `mapCompanyRole`, `findDates`, `parseDate`, `parseDatePeriod`, the text adapter; B the texts in the dashboard; C the window "Mapping rules"). `UPDATE=1` writes the golden file anew. `t_adapter.py` part A: the boundary starts at "2. Mapping register".
- **Watch out:** a word list used while the script loads (e.g. `TEXT_TRACK_WORDS` in the adapter's `PREFIX`) must stay in section 2, before the sources.

## Import 3.10.0 · 2026-10-16

A date of the date matrix only for the release level (collect item 8 of 2026-10-16).

- **Matrix cells:** a cell gets `rel` (true: only for rows on the release level). `matrixCellHtml` shows a checkbox `data-f="dm-rel"` (`.dci-dm-rel`, label `dm.rel`, title `dm.relTitle`), passed to `cellTracksHtml(c, extra)` so it sits right after the track groups (no extra line per cell); the change handler sets `c.rel`, clears `c.auto` and calls `dmChanged()`. Stored with the matrix in `dci-date-matrix:<MBID>` (no new key; old cells without `rel` count as false).
- **`applyMatrixColumn(group, cells, report)`:** rows on the release level take the cells with `rel` when the column has any, else the cells without tracks as before; rows on recordings and works leave out the cells with `rel` (`!c.rel` in the per-track filter).
- **New:** `matrixDateForLevel(row)` – for a row with a matrix date (`row.date.mx`) and not "skip": applies the column of its date group again (`applyMatrixColumn` with an empty report, then `saveMatrix()`) and logs `dmRelDate`; true when it applied. A date typed by hand (`!row.date.mx`) is left alone, as `applyMatrixColumn` already does.
- **Changed:** `setLevel` calls `matrixDateForLevel(row)`; when true it draws groups, works matrix and dates again instead of only the row.
- **Texts:** `dm.rel`, `dm.relTitle`, `log.dmRelDate`, `ms.3.10.0`; `MILESTONES` gets 3.10.0 (the notice of a fresh install now shows 3.10.0, 3.5.0, 3.3.0).
- **Tests:** new `t_reldate.py` (A apply, B switching the level, C own date stays, D stored); `t_notice.py` (milestones 3.10.0 / 3.5.0 / 3.3.0); `t_pools.py` and `t_trackpool.py` click "Apply" by script (in the test window the floating log covered it once the cells got taller).
- **Watch out:** `compareVersions` compares the parts as numbers, so 3.10.0 comes after 3.5.0 (and after 3.9.x).

## Import 3.9.0 · 2026-10-16

Narrow rows (collect item 7, the mockup of 2026-10-16) and a compact date.

- **`groupHtml`:** the rows table is `<div class="dci-tablewrap dci-rowswrap"><table class="dci-table dci-rows"><tbody>` – no `thead` any more.
- **`rowHtml`:** each cell starts with its caption `<div class="dci-cap">` (texts `th.type`, `th.attrs`, `th.level`, `th.date`, `th.tracks`, reused); the cells get the classes `dci-c-role`, `dci-c-type`, `dci-c-attr`, `dci-c-level`, `dci-c-date`, `dci-c-tracks`.
- **CSS:** `.dci-rowswrap { container-type: inline-size }`; `tr.dci-row` is a CSS grid with `grid-template-areas` (default three columns: role | type above attr | level above date above tracks); `@container (min-width: 1150px)` one line, `(max-width: 699px)` two columns, `(max-width: 459px)` one. The table stays valid HTML (`tr`/`td` with `display: grid`/`block`). `.dci-cap` (12 px, 600, `#4a4658`), `.dci-datechip*`.
- **`dateCell(row)`:** a date with a pool entry (`d.poolId`) is a chip `<span class="dci-datechip" data-date="…">` with `poolLabel`, ✎ (`date-edit`) and ✕ (`date-clear`), and the line `date.fromMatrixShort` / `date.fromPoolShort`; with `row.dateEdit === d.poolId` the fields are shown, plus `date-done`. Dates without a pool entry show the fields as before.
- **`mbDateFields(prefix, v, compact)`:** `compact` may be `'rows'`: the grid of the works matrix (year above year, month above month, day above day) with the labels `date.beginRow` / `date.endRow` instead of "BD" / "ED".
- **New:** `fieldsText(d)` ("2001-03-01 – 2001-03-03", for `data-date`).
- **State:** row `dateEdit` (pool id whose fields are open; not stored).
- **Handlers:** click `date-edit` (`row.dateEdit = row.date && row.date.poolId`), `date-done` (deletes it).
- **Texts:** `date.edit`, `date.done`, `date.fromMatrixShort`, `date.fromPoolShort`, `date.beginRow`, `date.endRow`.
- **Tests:** `common_rows.py` – `rows_of` reads a chip's `data-date`, new `date_field(row, f)` (opens the chip when needed); `t_bar.py`, `t_dragdates.py` use it; `t_keepplace.py` scrolls the element into view before measuring (Playwright scrolled on click and the test saw 8 px).
- **Watch out:** tests that read `[data-f=rd-*]` of a pool-linked row must open the chip first (`date_field`).

## Import 3.8.0 · 2026-10-16

Supplement with a source the release does not link to (collect item 5).

- **`suppBarHtml`:** a field `data-f="supp-url"` (`supp.urlPh`) and a button `data-act="supp-url"` (`supp.urlLoad`) in `.dci-supp-url`; a loaded typed source shows as "… ✓ supplemented" (`typedOn`).
- **Handler `supp-url`:** `BANDCAMP.albumUrl(value)`, else `DISCOGS.parseReleaseId(value)`; nothing → `msg.badDiscogsId`; the loaded source → `supp.sameAsLoaded`; otherwise `loadSupplement(source, id, null, typed)` with `typed` = not among `S.sourceLinks`. Enter in the field clicks it (map of Enter keys).
- **Changed:** `loadSupplement(source, id, input, typed = false)`; `S.supp.typed`.
- **Texts:** `supp.urlPh`, `supp.urlLoad`, `supp.sameAsLoaded`.
- **Tests:** `t_supp.py` part G (a typed Bandcamp album); the selector for the bar buttons is `.dci-suppbar .dci-supp-btn` now (the new button has no such class).

## Import 3.7.0 · 2026-10-16

Recording place and dates in Bandcamp's "about" text; places with an area (collect item 2).

- **`TEXT.parse`:** new `placeOf(text)` → `{ name, area }` ("Loft in Cologne, june 16/17 2018", "Loft, Cologne"; parts with digits left out); the "by … at …" branch (`left.match(/^(.*?)\s+at\s+(.+)$/i)`) and the place-only form (`/^(\p{L}+)\b.*?\s+at\s+(.+)$/iu`) use it; `place(verb, where)` gives the company's `who` an `area`.
- **`groupCompanies`** keeps `area`; the company entry gets `area` (also an entry of a supplement).
- **`loadRelease`:** a company with an area whose roles allow a place becomes a place (`setCompanyEntityType(c, 'place')`, before "Media choice").
- **`suggestByName`:** places with an area are searched as `place:(words) AND area:(words)`; the area goes into the hit's disambiguation. The group header shows "(area)".
- **`BANDCAMP.toRelease`:** the about text is read with `TEXT.parse` too, but only its companies with a role ending in "at" are taken (`/\bat$/i`); its other lines are not listed as not recognized. The about text was already part of `notes` (dates).
- **Dates:** `DAYLIST` also takes "/" between days ("16/17"), so "june 16/17 2018" and "16/17 June 2018" are found like "June 16 & 17, 2018".
- **Tests:** new `t_about.py` (A place, B date, C "Studio Nord, Bremen", D "mixed at home in Oslo" gives no entry); harness `PLACE_AREAS` (areas of the mock places), `ws_search` filters by words and by `area:(…)`; `t_freetext.py` (Abbey Road with its area London).
- **New:** `PRIVATE_PLACE` – `placeOf` gives `null` for "home …" and "my / his / her / their / our (own) home, house, flat, place, studio …", so no place is made of them (found with a probe of "Recorded at home during lockdown").
- **Watch out:** "at" as a word is enough for a place ("recorded at …"); other prose after "at" in an about text still gives an entry – only a suggestion, nothing is assigned.

## Import 3.6.0 · 2026-10-16

Shared instrument words, lists with an unknown part, flexible name suggestions (collect items 1 and 3).

- **`TEXT.parse`:** new `AND_SEP`, `INSTRUMENT_MODIFIER` (soprano, alto, tenor, baritone, acoustic, electric, fretless, upright …; not "bass"), `splitRoles(side)` (splits by `,` `&` `+` `/` and by "and/und/et" only between spaces – lookbehind – and gives the noun of the last part to the modifiers before it, as long as the result is a known role), `roleParts(side)` (`parts`, `known`, `unknown`); `listRoles` uses `splitRoles`. New branch: name on the left, some roles on the right known → the known ones are credited, the line goes to `unrecognized` as "<line> → ? “unknown”" (`unknownParts`).
- **Names:** new `nameWords(x)` (no case, accents, ß → ss, punctuation), `nameFit(mbName, srcName)` → `'same'` / `'similar'` (same first and last word, middle names or initials more or less) / `''`, `luceneWords(name)` (all words required).
- **`suggestByName`:** people are searched as `artist:(words) OR alias:(words)`, companies as before by phrase; `limit=25`; hits (names and aliases) by `nameFit`, same before similar, the best 5; `nameHits[].similar`.
- **`nameSuggestHtml`:** a similar hit gets `<span class="dci-similar">` (`match.similarName`) and the title `match.similarTitle`; the log `nameSuggested` names it too.
- **Texts:** `match.similarName`, `match.similarTitle`.
- **Tests:** new `t_names.py` (A shared word, B unknown part, C suggestions); harness `fold()` (accents out) for `ws_search`.
- **Watch out:** the real MusicBrainz search does not find "T. Snekkestad" for "Torben Snekkestad" (Lucene has no prefix match here); `nameFit` would accept it, the search does not deliver it.

## Import 3.5.1 · 2026-10-16

- **`applyPlacement()`:** without the dashboard (`S.overlay` not yet built) it draws the launcher again (`renderLauncher()`) and returns; before, it returned early and the switch "Window / in the page" kept showing "window" (collect item 4).
- **Tests:** `t_inline.py` step 0 (the switch before the dashboard was opened).

## Import 3.5.0 · 2026-10-13

Stage 2: a second source supplements the loaded one, on request only (variant B of the mockup).

- **New, in section 7 ("Stage 2"):** `trackSetText` (tracks as "1–3, 5", several media "1.1–1.3"), `suppSig` (entity, relationship type, attribute of a row), `sameTracks`, `nameKey` (names without case, accents, punctuation), `rowRelText`, `suppEntryFor` (entry of the dashboard for a name: same MBID, else same name, also variants and aliases), `suppTracks`, `loadSupplement(source, id, input)`, `compareSupplement` (confirmed / new role / new entry / differs / not recognized; MB lookups of linked names, name search for new entries), `suppRow`, `applySupplement`, `discardSupplement`, `dropSupplementMarks`, `suppBarHtml`, `renderSupp`, `srcMarksHtml`, `sourceByShort`, `suppNoteLines`, `sourceLinkLabel`.
- **Changed:** `resolveArtists({ source, only })` – per call the source of the entries (URL lookups with `source.urlKey`, `strictNames`, `nameSearch`) and only the entries given; `resolveViaAliases(list, source)`; `loadRelease` resets the supplement and draws the source bar again once rows exist; `renderSource` (supplement bar, text form in supplement mode with `supp-text-load`); `roleCell` (marks); `editNoteBlock` ("Also from:", lines of `suppNoteLines` after "Done"); `groupCredits` keeps `lines`, `groupCompanies` keeps `line`; `TEXT.parse` gives each credit and company the `line` it comes from; each adapter has `short` (`DG`, `BC`, `TXT`); `groupHtml` and `matchHtmlInner` use the entry's own source (`a.src`).
- **State:** `S.supp` (`source`, `id`, `rel`, `open`, `items`, `url`, `confirmed`, `mismatch`), `S.suppSources` (Map short → `{ name, url }`); rows: `confirmedBy` (Set of shorts), `differ`, `supp`, `suppName`, `suppTook`; entries: `src`.
- **Storage:** none – supplements are not stored.
- **Texts:** `supp.*` (42), `busy.supp`, `log.suppLoaded`, `log.suppApplied`, `log.suppDiscarded`, `ms.3.5.0`; `MILESTONES` gets 3.5.0.
- **CSS:** `.dci-suppbar`, `.dci-supp*`, `.dci-srcmark*`, `.dci-vh`.
- **Handlers:** click `supp-load`, `supp-text`, `supp-text-load`, `supp-remove`, `supp-fold`, `supp-apply`, `supp-discard`; change `supp-sel`, `supp-all`.
- **Tests:** new `t_supp.py` (A–F); `t_notice.py` (milestones, generation 4), `t_adapter.py` part D (update from 2.19.1 now resets once; no reset within generation 4).
- **Watch out:** a row is "the same" only with the same MB relationship type and the same instrument or vocal (`suppSig`); "bass" and "bass guitar" count as different.

## Import 3.4.0 · Companion 1.7.0 · 2026-10-13

- **New:** `startImport()` (taken out of `init`: chosen source, else the preference list), `forgetImport()` ("Delete stored import": removes this release's entries in `dci-source-pick` and `dci-media-sel`, its date pool, track pool and date matrix, its log, the supplement, and asks the companion to forget its status, then calls `startImport`); button and confirmation panel in `renderSource` (`forget-open`, `forget-cancel`, `forget-do`).
- **Storage generation 4:** `STORE_EPOCH` 3 → 4 and `EPOCH_KEEPS_CREATED = false` – the update clears everything once, this time `dci-created-works:<MBID>` too (asked for by the maintainer). Text `notice.reset` says so.
- **Companion 1.7.0:** `STORE_EPOCH` 4; message `forget-release` deletes `statusMap:<MBID>`, takes it out of `statusMapIndex` and clears `statusMap` if it belongs to that release.
- **Texts:** `forget.*` (7), `log.importForgotten`.
- **Tests:** `t_notice.py` (generation 4, created works cleared, companion epoch 4), `t_supp.py` part E.

## Import 3.3.2 · 2026-10-13

- **Spelling check (rule 4):** `resolveArtists` stores `a.spell` (`src`, `srcName`, `release`, `mb`) for entries of a source with `strictNames`; new `spellHtml(a)`, shown in `variantsHtml` (`[data-spell]`) and refreshed by `updateGroupHeader`; "No alternative spelling on …" is left out for such sources. CSS `.dci-spell*`; texts `spell.*` (5).
- **The old script on the page:** `showTwiceWarning()`; at start the script stays out when `#dci-styles` already exists; 3 s after start it warns when a second `#dci-styles` appeared. Text `old.twice`.
- **Tests:** `t_bandcamp.py` part F (spelling line), `t_supp.py` part F.

## Import 3.3.1 · Companion 1.6.1 · 2026-10-13

- **New file names** (`@downloadURL`, `@updateURL`, `CHANGELOG_URL`); READMEs and changelog renamed.
- **Rule 4 against the release's artist credit:** the release is read with `inc=artist-credits` into `S.releaseCredit` (`mbid`, `name`, `join`); `releaseCreditName(mbid)`, `releaseCreditText()`; in `resolveArtists` an artist found through its link is assigned only when the release credits it exactly as the source names it (companies: their MB name); otherwise `a.strictMiss`, `a.strictSpelled`, log `artistCreditSpelling`, and `nameSuggestHtml` heads the suggestion with `match.linkSuggest`.
- **Tests:** harness `RELEASE_AC`; `t_bandcamp.py` parts E and F.

## Import 3.3.0 · Companion 1.6.0 · 2026-10-13

- **Bandcamp adapter** `BANDCAMP` (section 2): `albumUrl`, `bandUrl`, `pageData` (the `data-tralbum` JSON), `toRelease` (credits text read with `TEXT.parse`, track pages for their track only, the band linked to its page), `release` (track pages when `ctx.settings.bandcampTracks`). `httpGet(url)` (`GM_xmlhttpRequest`, else `fetch`). Header: `@grant GM_xmlhttpRequest`, `@grant unsafeWindow`, `@connect bandcamp.com`, `@sandbox raw`.
- **Order of the sources:** `SOURCE_ORDER_KEY` (`dci-source-order`), `SOURCE_PICK_KEY` (`dci-source-pick`, the last 200 releases), `SOURCE_ORDER_DEFAULT`, `readSourceOrder`, `keepSourcePick`, `moveSourceOrder`, `startSource`, `sourceOrderHtml`, drag & drop branch `srcorder` in `dmTargetOf` / `onDropOn`; `S.digital` (all media "Digital Media").
- **Bandcamp menu:** `bandcampSettingsHtml`, `testBandcampPage`, `dci-bc-tracks`.
- **Rule 4, first form:** adapter flag `strictNames` – a linked entry only with the exact name.
- `LINKED_SOURCES`; `SOURCES` gets `bandcamp`; picker values `source|id`.
- **Texts:** `srcorder.*`, `bc.*`, `err.bandcampData`, `err.pageHttp`, `err.pageNet`, `log.artistSpelling`, `log.sourceKept`, `log.sourceOrder`, `log.bcTest`, `ms.3.3.0`.
- **Tests:** new `t_bandcamp.py`; harness `BC_PAGES`, `BC_ARTISTS`, `bc_page`, `GM_XHR_SHIM`, `open_mb_edit(gm_xhr=True)`, `MB_SEARCH`, `ws_search`.

## Import 3.2.0 · 2026-10-13

- **Text adapter** `TEXT` (section 2): `parse(text, { isRole, isCompanyRole, resolveTracks })` (track lists before or after a line, ℗ / ©, clauses, "… by …" with "at Place", "Name – roles", "Role: names", "Name (roles)", "Strings arranged" → "Arranged By [Strings]") and `toRelease`; flags `readsTrackLists`, `nameSearch`, `usesMbTracks`.
- **Core:** `isKnownRole`, `isTextCompanyRole` (`TEXT_COMPANY_RE`), `mbTracksAsSource`, `tracksInText(text, srcTracks)`, `suggestByName`, `nameSuggestHtml`, handler `name-use`; the text form and the list of lines not recognized in `renderSource`; rule S014 leaves a company alone that the source gives for some tracks only (`row.dAllTracks === false`); edit note `noteSource`.
- **Texts:** `source.text*`, `textsrc.*`, `unrec.*`, `match.nameSuggest`, `match.nameUseTitle`, `match.byName`, `log.sourceLoaded`, `log.nameSuggested`, `log.nameLookup`, `msg.textEmpty`, `busy.source`.
- **Tests:** new `t_freetext.py`.

## Import 3.1.0 · Companion 1.6.0 · 2026-10-13

- New names: `@name`, `EDIT_NOTE_SCRIPT_NAME`, texts `title`, `launcher.open`, `notice.title`; companion descriptions.
- `tr()` passes `src` (the name of the loaded source, `SOURCE_NAME`) to every text; about 40 texts say `{src}` instead of "Discogs"; `msg.noDiscogsLink` removed.

## Import 3.0.0 · 2026-10-12

- **Adapters:** section 2 is new. The adapter `DISCOGS` is the only part that reads Discogs (`cleanName`, `getJson`, `parseTrackSpec`, `toRelease`, `personType`, `person`, `aliases`, `seriesParent`, `releaseLinks`, `parseReleaseId`) and delivers a neutral release (tracks, credits, companies, series, notes, format words). The core works with that only: `groupCredits`, `groupCompanies`, `lookupUrls(urls, kind, urlKey)`, `sourceUrlLtId`, `sourceContext`, `loadRelease(id, { source })`.
- **Removed from the core:** `cleanDiscogsName`, `collectCompanies`, `collectCredits`, `discogsArtistUrl`, `discogsCreditFor`, `discogsLabelUrl`, `discogsWritersOf`, `fetchDiscogsArtist`, `fetchDiscogsRelease`, `flattenDiscogsTracks`, `guessArtistType`, `loadDiscogs`, `lookupDiscogsArtistUrls`, `lookupDiscogsUrls`, `parseTrackSpec`, `syncDiscogsCredits`.
- **State:** `S.discogs`, `S.discogsId`, `S.discogsLinks`, `S.dTracks` → `S.source`, `S.release`, `S.sourceLinks`, `S.srcTracks`.
- No visible change, no reset.
- **Tests:** new `t_adapter.py` (A: no Discogs data outside the adapter; B: the adapter in Node; C: everything that goes through the adapter in the dashboard; D: update without reset).

## Import 3.0.0 – 3.5.0 together: comparison of the code of 2.19.1 and 3.5.0

- Size: 16,001 → 17,848 lines; functions and constants: 609 → 658
- New functions/constants (65): `applySupplement`, `BANDCAMP`, `bandcampSettingsHtml`, `companionReleaseId`, `compareSupplement`, `creditedWritersOf`, `discardSupplement`, `DISCOGS`, `dropSupplementMarks`, `EPOCH_KEEPS_CREATED`, `forgetImport`, `groupCompanies`, `groupCredits`, `httpGet`, `isKnownRole`, `isTextCompanyRole`, `keepSourcePick`, `LINKED_SOURCES`, `loadRelease`, `loadSupplement`, `lookupUrls`, `mbTracksAsSource`, `moveSourceOrder`, `nameKey`, `nameSuggestHtml`, `noteSourceUrl`, `parseRoleNotation`, `prefilledBy`, `readSourceOrder`, `releaseCreditName`, `releaseCreditText`, `renderSupp`, `rowRelText`, `sameTracks`, `showTwiceWarning`, `SOURCE_NAME`, `SOURCE_ORDER_DEFAULT`, `SOURCE_ORDER_KEY`, `SOURCE_PICK_KEY`, `sourceByShort` … (+25)
- Removed (16): `cleanDiscogsName`, `collectCompanies`, `collectCredits`, `discogsArtistUrl`, `discogsCreditFor`, `discogsLabelUrl`, `discogsWritersOf`, `fetchDiscogsArtist`, `fetchDiscogsRelease`, `flattenDiscogsTracks`, `guessArtistType`, `loadDiscogs`, `lookupDiscogsArtistUrls`, `lookupDiscogsUrls`, `parseTrackSpec`, `syncDiscogsCredits`
- Changed (85): `aliasSuggestHtml`, `applyLiveDefault`, `applyNotesTrackCredits`, `applyPlan`, `artistVariants`, `autoPlaceFoundDates`, `buildArtistSeed`, `buildOverlay`, `buildWorkQuery`, `CHANGELOG_URL`, `computePublisherEvidence`, `continueWorkQueue`, `dateFindListHtml`, `dateFinds`, `dateSuggestions`, `dmTargetOf`, `EDIT_NOTE_SCRIPT_NAME`, `editNoteBlock`, `entityPath`, `fetchJsEntity`, `groupHtml`, `I18N`, `idx`, `init`, `injectStyles`, `insertLauncher`, `loadSeries`, `loadSeriesLabel`, `loadWorkOptions`, `matchHtml` … (+55)
- Texts (English keys): 1008 → 1117; new: `supp.*` (42), `log.*` (13), `bc.*` (7), `forget.*` (7), `srcorder.*` (7), `textsrc.*` (6), `source.*` (5), `spell.*` (5), `match.*` (4), `err.*` (3), `ms.*` (3), `unrec.*` (3), `busy.*` (2), `msg.*` (2), `old.*` (1); removed: 1
- State `S`: new `bcOpen`, `bcTest`, `bcTracks`, `digital`, `release`, `source`, `sourceLinks`, `sourceOrder`, `srcOrderOpen`, `srcTracks`, `supp`, `suppSources`, `textForm`, `textInput`; removed `discogs`, `discogsId`, `discogsLinks`, `dTracks`
- Browser storage: new `dci-bc-tracks`, `dci-source-order`, `dci-source-pick`; removed –

## Companion 1.5.0 → 1.7.0

- Size: 806 → 815 lines; functions and constants: 29 → 29
- New functions/constants (0): –
- Removed (0): –
- Changed (3): `initMusicBrainzSide`, `norm`, `STORE_EPOCH`

## Import 2.19.1 · 2026-10-12

- `liveWhyText`: the reason for "live" names the source's role as written and the name (`matrix.liveWhy.credit`, `matrix.liveWhy.creditAll`); `matrix.liveOfferRec`.

## Import 2.19.0 · 2026-10-12

- One look for every suggestion: CSS variables `--sugg-bg`, `--sugg-line`, `--sugg-ink`, class `dci-suggbtn`.
- "Commissioned By" (rules R099, C037, S024) and "Live Recording By" (R031, W007, a hint for S021); entries of the notes stay suggestions in the pools until used (`markPoolUsed`); `row.dAllTracks` for credits without tracks.
- Tests: new `t_v219.py`.

## Reconstructed: main script 0.9.2 – 2.19.1

Compared snapshot by snapshot (the versions uploaded to this repository, and 2.19.1 kept from the working session). Versions between two snapshots are listed under "Covers"; what each of them does is in the [changelog](mb-vibecode-credits-importer-CHANGELOG.md).

### 2.16.0 → 2.19.1 · 2026-10-12

Covers Import 2.17.0, Import 2.18.0, Import 2.19.0, Import 2.19.1.

- Size: 14,334 → 16,001 lines; functions and constants: 540 → 609
- New functions/constants (69): `applyLiveDefault`, `applyLogPlace`, `applyMediaChoice`, `applyNotesTrackCredits`, `applySongDefault`, `ATTR_ABBR`, `attrAbbr`, `attrPillHtml`, `chooseMedia`, `COPYRIGHT_SIGN`, `dropTracksOnMatrix`, `editNoteEl`, `editNoteWidth`, `formatMediaList`, `gotoIncomplete`, `inPlacedCell`, `inSelection`, `isSuggestedCell`, `linkAttrsHeadHtml`, `linkAttrsHtml`, `linkAttrsOf`, `linkAttrsOpen`, `linkAttrsToggleHtml`, `linkAttrTypes`, `linkKey`, `liveHint`, `liveOfferText`, `liveReason`, `liveWhyText`, `LOCK_SVG`, `LOG_DOCK_MIN_H`, `LOG_DOCK_SIDE_SHARE`, `LOG_PLACES`, `LOG_SIDE_MIN_PX`, `logDocked`, `logPlaceFrame`, `logPlaceNow`, `looseName`, `markPoolUsed`, `matchEntry` … (+29)
- Removed (0): –
- Changed (74): `addManualEntry`, `applyPlan`, `autoPlaceFoundDates`, `buildLogWindow`, `buildOverlay`, `cellEntry`, `cellHtml`, `cellMenuHtml`, `clampWindow`, `columnDate`, `columnHeadHtml`, `COMPANY_ROLES`, `computePlan`, `computePublisherEvidence`, `DATE_HINTS`, `DATE_RULES`, `datePoolHtml`, `DETAIL_FLAGS`, `dmDragEnd`, `dmMarkOver`, `dmTargetOf`, `dropTracksOn`, `editNoteBlock`, `findDates`, `I18N`, `init`, `injectStyles`, `inMedium`, `loadDiscogs`, `makeMovable` … (+44)
- Texts (English keys): 909 → 1008; new: `matrix.*` (42), `media.*` (23), `log.*` (20), `msg.*` (4), `ms.*` (3), `sum.*` (3), `medium.*` (2), `note.*` (1), `pools.*` (1), `preview.*` (1); removed: 1
- State `S`: new `linkAttrOff`, `linkAttrOn`, `linkAttrStaged`, `liveAuto`, `mediaSel`, `mxColMenu`, `mxOptsOpen`, `wattrLong`, `wattrOpen`, `wattrOpenAll`; removed –
- Browser storage: new `dci-log-dock-h`, `dci-log-place`, `dci-media-sel`, `dci-wattr-long`; removed –
- New rule ids: `C037`, `D015`, `Q004`, `R098`, `R099`, `S019`, `S020`, `S021`, `S022`, `S023`, `S024`

### 2.15.0 → 2.16.0 · 2026-10-11

Covers Import 2.16.0.

- Size: 14,102 → 14,334 lines; functions and constants: 532 → 540
- New functions/constants (9): `AUTOSCROLL_DELAY_MS`, `AUTOSCROLL_MAX`, `AUTOSCROLL_RAMP_MS`, `AUTOSCROLL_ZONE`, `columnFills`, `planFill`, `TYPE_QUESTIONS`, `typeAskHtml`, `typeQuestionFor`
- Removed (1): `UP_DWELL_MS`
- Changed (24): `applyColumnDate`, `ARRANGER_TYPES`, `cellHtml`, `columnHeadHtml`, `computePlan`, `dragAutoScroll`, `fillKey`, `I18N`, `injectStyles`, `instrumentAskHtml`, `matrixAction`, `matrixColumns`, `MILESTONES`, `onClick`, `onDragStart`, `QUESTION_RULES`, `remapRow`, `roleRules`, `rowHtml`, `rulesOfRow`, `rulesTables`, `sendDiscogsStatus`, `setCellDate`, `VERSION`
- Texts (English keys): 897 → 909; new: `log.*` (4), `matrix.*` (4), `typeAsk.*` (3), `ms.*` (1); removed: 0
- New rule ids: `Q003`, `R097`

### 2.14.0 → 2.15.0 · 2026-10-11

Covers Import 2.15.0.

- Size: 14,032 → 14,102 lines; functions and constants: 528 → 532
- New functions/constants (4): `ENGINEER_TASK_RE`, `focusRule`, `splitEngineerTasks`, `UP_DWELL_MS`
- Removed (0): –
- Changed (16): `dragAutoScroll`, `I18N`, `injectStyles`, `loadDiscogs`, `onClick`, `onDragStart`, `openRules`, `parseRoles`, `roleCell`, `ruleInfoHtml`, `rulesOfRow`, `SPECIAL_RULES`, `VERSION`, `WORDING_RULES`, `WORDING_SYNONYMS`, `wordingCredit`
- Texts (English keys): 895 → 897; new: `role.*` (1), `rules.*` (1); removed: 0
- New rule ids: `S018`, `W006`, `W007`

### 2.12.0 → 2.14.0 · 2026-10-11

Covers Import 2.13.0, Import 2.14.0.

- Size: 13,760 → 14,032 lines; functions and constants: 522 → 528
- New functions/constants (6): `datelessExisting`, `dropTracksOn`, `fillKey`, `fillsOfCell`, `setCellDate`, `tracksDropFits`
- Removed (0): –
- Changed (25): `applyPlan`, `cellHtml`, `cellOwnDate`, `computePlan`, `datePoolHtml`, `discogsLabelUrl`, `dmMarkOver`, `dmTargetOf`, `dropDateOn`, `editNoteBlock`, `I18N`, `init`, `injectStyles`, `matrixAction`, `mergeDates`, `MILESTONES`, `onDragOver`, `onDragStart`, `onDrop`, `renderDates`, `renderPreview`, `sendDiscogsStatus`, `STORE_EPOCH`, `trackPoolHtml`, `VERSION`
- Texts (English keys): 873 → 895; new: `msg.*` (7), `log.*` (6), `matrix.*` (3), `tracks.*` (3), `ms.*` (2), `preview.*` (1); removed: 0
- State `S`: new `dateFills`, `filledDates`; removed –

### 2.10.0 → 2.12.0 · 2026-10-11

Covers Import 2.11.0, Import 2.12.0.

- Size: 13,539 → 13,760 lines; functions and constants: 513 → 522
- New functions/constants (11): `addCommonDate`, `applyDateToTracks`, `CHANGELOG_URL`, `commonDate`, `compareVersions`, `MILESTONES`, `NOTICE_KEY`, `noticeMilestones`, `renderNotice`, `STORE_EPOCH`, `versionParts`
- Removed (2): `applyDateToRows`, `OLD_DATES_KEY`
- Changed (40): `autoPlaceFoundDates`, `clearPools`, `cloneRow`, `closeDashboard`, `COMPANY_ROLES`, `DATE_MATCHERS`, `DATE_RULES`, `datePoolHtml`, `discogsLabelUrl`, `dispatchAddRelationship`, `dm`, `dmClean`, `dropDateOn`, `gripHtml`, `I18N`, `init`, `injectStyles`, `insertLauncher`, `INSTRUMENT_ALIASES`, `mapCompanyRole`, `matrixChooseHtml`, `onChangeInner`, `onClick`, `placeSeparateDays`, `poolDateFor`, `renderDates`, `renderLauncher`, `resetSettings`, `roleRules`, `saveMatrix` … (+10)
- Texts (English keys): 849 → 873; new: `ms.*` (22), `date.*` (4), `dm.*` (4), `notice.*` (4), `pools.*` (3), `trackpool.*` (2), `log.*` (1); removed: 16
- State `S`: new –; removed `releaseLanguage`
- Browser storage: new `dci-notice-version`, `dci-pools-keep`, `dci-store-epoch`, `dci-updated-from`; removed `dci-dates:<MBID>`, `dci-stamp-overwrite`
- New rule ids: `C036`, `D014`, `S017`, `W004`, `W005`

### 2.8.0 → 2.10.0 · 2026-10-11

Covers Import 2.9.0, Import 2.10.0.

- Size: 13,206 → 13,539 lines; functions and constants: 506 → 513
- New functions/constants (13): `applyPlacement`, `cellTracksHtml`, `dragAutoScroll`, `dropDateOn`, `inPage`, `matrixChooseHtml`, `mergeDates`, `placeSeparateDays`, `reloadPools`, `revealDashboard`, `scrollDashboardTop`, `setPlace`, `updatePageScrollPadding`
- Removed (6): `onStampClick`, `plannedLinks`, `refocusField`, `stampApplyAll`, `stampBarHtml`, `stampTypeOptions`
- Changed (47): `applyMatrix`, `applyMatrixColumn`, `applyPlan`, `ARRANGER_TYPES`, `autoPlaceFoundDates`, `buildOverlay`, `clampWindow`, `clearPools`, `closeDashboard`, `dateFindListHtml`, `datePoolHtml`, `dmClean`, `dmDragEnd`, `dmTargetOf`, `ensureTrackGroup`, `groupRowCounts`, `I18N`, `injectStyles`, `insertLauncher`, `makeMovable`, `matrixCellHtml`, `matrixHtml`, `mbUsesEscape`, `onChangeInner`, `onClick`, `onDragOver`, `onDragStart`, `onDrop`, `openDashboard`, `poolClearHtml` … (+17)
- Texts (English keys): 830 → 849; new: `dm.*` (12), `place.*` (8), `pools.*` (6), `log.*` (4), `datefind.*` (2), `date.*` (1); removed: 14
- State `S`: new –; removed `stampId`
- Browser storage: new `dci-place`; removed –

### 2.7.0 → 2.8.0 · 2026-10-11

Covers Import 2.8.0.

- Size: 12,307 → 13,206 lines; functions and constants: 470 → 506
- New functions/constants (42): `applyMatrix`, `applyMatrixColumn`, `autoPlaceFoundDates`, `cellEntry`, `cellTracks`, `clearPools`, `datePoolHtml`, `dm`, `dmAddTracks`, `dmChanged`, `dmClean`, `dmDragEnd`, `dmMarkOver`, `dmMessage`, `dmPlace`, `dmTargetOf`, `gripHtml`, `groupRowCounts`, `MATRIX_KEY`, `matrixCellHtml`, `matrixEditorHtml`, `matrixHtml`, `mediumGroupName`, `newCellId`, `newTrackGroupFrom`, `onDragOver`, `onDragStart`, `onDrop`, `otherPoolKeys`, `poolClearHtml`, `poolDateFor`, `poolsOpen`, `rebuildDashboard`, `renderReset`, `resetSettings`, `rowSig`, `saveMatrix`, `SETTINGS_KEYS`, `stampBarHtml`, `studioId` … (+2)
- Removed (6): `fillSimilar`, `guessDateGroup`, `linkPanelHtml`, `linkTagHtml`, `saveAndCopyDate`, `setDateTrackGroup`
- Changed (28): `autoGroupDate`, `buildOverlay`, `dateCell`, `dateFinderHtml`, `dateFindListHtml`, `ensureTrackGroup`, `I18N`, `injectStyles`, `loadDiscogs`, `mbUsesEscape`, `onChangeInner`, `onClick`, `onInput`, `onStampClick`, `openPoolForm`, `poolFormHtml`, `removePoolEntry`, `renderAll`, `renderDates`, `rowShort`, `savePoolForm`, `saveTrackPool`, `setLanguage`, `SPECIAL_RULES`, `trackPoolHtml`, `useFoundDate`, `VERSION`, `workDateCell`
- Texts (English keys): 787 → 830; new: `dm.*` (32), `pools.*` (16), `reset.*` (9), `log.*` (7), `trackpool.*` (2), `date.*` (1), `datefind.*` (1); removed: 25
- Browser storage: new `dci-date-matrix:<MBID>`, `dci-dm-auto`, `dci-pools-open`; removed –

### 2.6.0 → 2.7.0 · 2026-10-10

Covers Import 2.7.0.

- Size: 12,163 → 12,307 lines; functions and constants: 466 → 470
- New functions/constants (4): `guessDateGroup`, `linkPanelHtml`, `linkTagHtml`, `setDateTrackGroup`
- Removed (0): –
- Changed (9): `applyDateToRows`, `I18N`, `injectStyles`, `onChangeInner`, `onClick`, `onStampClick`, `renderDates`, `trackPoolHtml`, `VERSION`
- Texts (English keys): 773 → 787; new: `link.*` (13), `log.*` (1); removed: 0

### 2.5.0 → 2.6.0 · 2026-10-10

Covers Import 2.6.0.

- Size: 12,054 → 12,163 lines; functions and constants: 463 → 466
- New functions/constants (3): `groupKindOf`, `kindTagHtml`, `restoreRow`
- Removed (0): –
- Changed (11): `buildOverlay`, `groupHtml`, `I18N`, `injectStyles`, `onClick`, `remapManualRow`, `removeRow`, `roleCell`, `updateGroupHeader`, `variantsHtml`, `VERSION`
- Texts (English keys): 766 → 773; new: `log.*` (2), `msg.*` (2), `toolbar.*` (2), `role.*` (1); removed: 0

### 2.4.1 → 2.5.0 · 2026-10-10

Covers Import 2.4.2, Import 2.4.3, Import 2.5.0.

- Size: 11,440 → 12,054 lines; functions and constants: 443 → 463
- New functions/constants (20): `applyDateToRows`, `cloneRow`, `datesWithContext`, `DAYLIST`, `DAYP`, `ensureTrackGroup`, `isPersonalPublisherRel`, `multiDays`, `multiMedium`, `plainNo`, `refocusField`, `saveTrackForm`, `saveTrackPool`, `sentenceAround`, `studiosInText`, `trackFormHtml`, `trackListLabel`, `TRACKPOOL_KEY`, `trackPoolHtml`, `tracksInText`
- Removed (0): –
- Changed (35): `ARRANGER_TYPES`, `columnDate`, `computePlan`, `computePublisherEvidence`, `DATE_MATCHERS`, `DATE_RULES`, `dateFindListHtml`, `dateFinds`, `findDates`, `I18N`, `injectStyles`, `insertLauncher`, `nextGroupNumber`, `onChangeInner`, `onClick`, `onInput`, `onStampClick`, `openPoolForm`, `poolFormHtml`, `removeRow`, `renderDates`, `roleRules`, `savePool`, `savePoolForm`, `sendDiscogsStatus`, `span`, `SPECIAL_RULES`, `syncModeHtml`, `toQuery`, `tracksPicker` … (+5)
- Texts (English keys): 728 → 766; new: `trackpool.*` (16), `datefind.*` (7), `date.*` (5), `dgStatus.*` (5), `log.*` (3), `sync.*` (2); removed: 0
- Browser storage: new `dci-dg-artwork`, `dci-track-pool:<MBID>`; removed –
- New rule ids: `D013`, `S013`, `S014`, `S015`, `S016`

### 2.4.0 → 2.4.1 · 2026-10-07

Covers Import 2.4.1.

- Size: 11,336 → 11,440 lines; functions and constants: 440 → 443
- New functions/constants (3): `onChangeInner`, `refreshPoolSelects`, `renderWorksInner`
- Removed (0): –
- Changed (29): `ARRANGER_TYPES`, `attrCell`, `DATE_HINTS`, `DATE_MATCHERS`, `DATE_RULES`, `findDates`, `I18N`, `injectStyles`, `insertLauncher`, `instrumentVocabulary`, `matrixAction`, `onChange`, `onClick`, `onStampClick`, `questionRuleFor`, `renderDates`, `renderWorks`, `rerenderRow`, `roleCell`, `roleCreditOptions`, `roleRules`, `sendDiscogsStatus`, `stampApplyAll`, `suggestRoleCredit`, `syncModeHtml`, `updateSyncArea`, `VERSION`, `withoutBy`, `wordingCredit`
- Texts (English keys): 721 → 728; new: `date.*` (4), `matrix.*` (2), `sync.*` (2), `log.*` (1), `roleCredit.*` (1); removed: 3
- Browser storage: new `dci-dg-release`, `dci-stamp-overwrite`; removed –
- New rule ids: `D012`

### 2.1.0 → 2.4.0 · 2026-10-07

Covers Import 2.1.1, Import 2.2.0, Import 2.2.1, Import 2.3.0, Import 2.4.0.

- Size: 10,475 → 11,336 lines; functions and constants: 396 → 440
- New functions/constants (44): `aliasesFor`, `applyRulesChange`, `CHECKBOX_DETAILS`, `DATE_HINTS`, `DATE_MATCHERS`, `DATE_RULES`, `dateFinderHtml`, `dateFindListHtml`, `dateFinds`, `exportRules`, `findDates`, `importRules`, `loadStore`, `MONTH_BY_NAME`, `MONTH_NAMES`, `monthNo`, `nextUserRuleId`, `ORDINALS`, `ownRuleResult`, `ownRulesHtml`, `reAlt`, `remapRow`, `renderRulesBody`, `roleCreditForInner`, `ruleInfoHtml`, `ruleNotes`, `ruleNotesCache`, `ruleOn`, `RULES_OFF_KEY`, `rulesOff`, `rulesOffCache`, `rulesOfRow`, `saveRuleForm`, `saveRules`, `setRulesStatus`, `single`, `span`, `typo`, `usDateOrder`, `useFoundDate` … (+4)
- Removed (0): –
- Changed (38): `applyPlan`, `dateGroupOf`, `defaultGeom`, `discogsCreditFor`, `GEOM_KEYS`, `I18N`, `injectStyles`, `insertLauncher`, `instrumentCandidates`, `loadDiscogs`, `makeRow`, `manualTypeTimer`, `mapCompanyRole`, `mapRole`, `mapRoleInner`, `onChange`, `onClick`, `onFromDiscogs`, `onInput`, `openRules`, `primaryIsValid`, `questionRuleFor`, `relFields`, `renderDates`, `renderPreview`, `roleCell`, `roleCreditFor`, `roleRules`, `rulesTables`, `ruleTestHtml` … (+8)
- Texts (English keys): 662 → 721; new: `rules.*` (34), `datefind.*` (13), `msg.*` (4), `sync.*` (4), `log.*` (3), `preview.*` (1); removed: 0
- Browser storage: new `dci-geom:rules`, `dci-rules-off`, `dci-user-rules`; removed –
- New rule ids: `D001`, `D002`, `D003`, `D004`, `D005`, `D006`, `D007`, `D008`, `D009`, `D010`, `D011`, `S012`

### 1.9.2 → 2.1.0 · 2026-10-07

Covers Import 2.0.0, Import 2.0.1, Import 2.1.0.

- Size: 10,062 → 10,475 lines; functions and constants: 385 → 396
- New functions/constants (12): `instrumentAskHtml`, `openRules`, `patternText`, `QUESTION_RULES`, `questionRuleFor`, `roleRules`, `rulesTables`, `ruleTestHtml`, `SPECIAL_RULES`, `TABLES`, `WORDING_RULES`, `wordingRuleFor`
- Removed (1): `bassAskHtml`
- Changed (24): `ART_TYPES`, `bringToFront`, `buildOverlay`, `caseWord`, `collectCompanies`, `COMPANY_ROLES`, `entityPath`, `GENERIC_WORDS`, `I18N`, `injectStyles`, `INSTRUMENT_ALIASES`, `instrumentCandidates`, `instrumentVocabulary`, `loadDiscogs`, `mapRoleInner`, `onClick`, `remainingMods`, `roleCreditFor`, `rowHtml`, `sameWording`, `stopDiag`, `toQuery`, `unmappedHtml`, `VERSION`
- Texts (English keys): 636 → 662; new: `rules.*` (26), `instrAsk.*` (2), `log.*` (1); removed: 3
- New rule ids: `C001`, `C002`, `C003`, `C004`, `C005`, `C006`, `C007`, `C008`, `C009`, `C010`, `C011`, `C012`, `C013`, `C014`, `C015`, `C016`, `C017`, `C018`, `C019`, `C020`, `C021`, `C022`, `C023`, `C024`, `C025`, `C026`, `C027`, `C028`, `C029`, `C030`, `C031`, `C032`, `C033`, `C034`, `C035`, `Q001`, `Q002`, `R001`, `R002`, `R003` … (+111)

### 1.9.0 → 1.9.2 · 2026-10-05

Covers Import 1.9.1, Import 1.9.2.

- Size: 9,908 → 10,062 lines; functions and constants: 380 → 385
- New functions/constants (5): `aliasSuggestHtml`, `discogsCreditFor`, `matchHtmlInner`, `resolveViaAliases`, `syncDiscogsCredits`
- Removed (0): –
- Changed (21): `addExistingArtistRels`, `applyPlan`, `buildOverlay`, `computePlan`, `creditsToFill`, `entityPath`, `I18N`, `indexExistingRelationships`, `injectStyles`, `insertLauncher`, `loadDiscogs`, `matchHtml`, `matrixAction`, `matrixChange`, `onChange`, `onClick`, `onInput`, `refresh`, `resolveArtists`, `syncStatusHtml`, `VERSION`
- Texts (English keys): 629 → 636; new: `log.*` (3), `match.*` (3), `sync.*` (1); removed: 0

### 1.8.0 → 1.9.0 · 2026-10-05

Covers Import 1.9.0.

- Size: 9,703 → 9,908 lines; functions and constants: 376 → 380
- New functions/constants (4): `creditsToFill`, `mapRoleInner`, `mediumLabel`, `statesBetween`
- Removed (0): –
- Changed (21): `addExistingArtistRels`, `applyPlan`, `ARRANGER_TYPES`, `attrCell`, `autoSkipExisting`, `buildOverlay`, `computePlan`, `editNoteBlock`, `I18N`, `indexExistingRelationships`, `injectStyles`, `instrumentCandidates`, `makeRow`, `mapRole`, `onChange`, `onClick`, `renderMediumFilter`, `renderPreview`, `tracksCell`, `tracksPicker`, `VERSION`
- Texts (English keys): 618 → 629; new: `msg.*` (6), `footer.*` (2), `log.*` (1), `picker.*` (1), `preview.*` (1); removed: 0
- State `S`: new `fillCredits`, `filled`; removed –
- Browser storage: new `dci-fill-credits`; removed –

### 1.7.0 → 1.8.0 · 2026-10-05

Covers Import 1.8.0.

- Size: 9,649 → 9,703 lines; functions and constants: 376 → 376
- New functions/constants (0): –
- Removed (0): –
- Changed (10): `ARRANGER_TYPES`, `I18N`, `insertLauncher`, `loadDiscogs`, `matrixAction`, `onFromDiscogs`, `renderWorks`, `syncModeHtml`, `updateSyncArea`, `VERSION`
- Texts (English keys): 610 → 618; new: `log.*` (3), `matrix.*` (2), `sync.*` (2), `nav.*` (1); removed: 0
- Browser storage: new `dci-dg-hover`; removed –

### 1.5.4 → 1.7.0 · 2026-10-05

Covers Import 1.6.0, Import 1.7.0.

- Size: 9,322 → 9,649 lines; functions and constants: 369 → 376
- New functions/constants (7): `addColumnHtml`, `ARRANGER_TYPES`, `autoGroupDate`, `dgStatusTimer`, `recordingDateOf`, `remainingMods`, `sendDiscogsStatus`
- Removed (0): –
- Changed (30): `applyRoleText`, `attrCell`, `bassAskHtml`, `columnHeadHtml`, `computePlan`, `dateCell`, `I18N`, `injectStyles`, `insertLauncher`, `levelCell`, `loadDiscogs`, `mapRole`, `matrixAction`, `matrixChange`, `onFromDiscogs`, `openInBackground`, `planPendingWork`, `refresh`, `renderWorks`, `roleCreditFor`, `saveAndCopyDate`, `setLevel`, `setType`, `syncModeHtml`, `unmappedHtml`, `updateSyncArea`, `VERSION`, `workDateCell`, `workFrontCell`, `WRITER_TYPES`
- Texts (English keys): 579 → 610; new: `matrix.*` (14), `dgStatus.*` (6), `log.*` (4), `common.*` (2), `date.*` (2), `sync.*` (2), `roleCredit.*` (1); removed: 0
- Browser storage: new `dci-dg-status`; removed –

### 1.5.3 → 1.5.4 · 2026-10-04

Covers Import 1.5.4.

- Size: 9,279 → 9,322 lines; functions and constants: 369 → 369
- New functions/constants (0): –
- Removed (0): –
- Changed (5): `applyPlan`, `computePlan`, `I18N`, `renderPreview`, `VERSION`
- Texts (English keys): 578 → 579; new: `log.*` (1); removed: 0

### 0.9.2 → 1.5.3 · 2026-10-04

Covers Import 0.9.3, Import 0.9.4, Import 0.9.5, Import 0.9.6, Import 0.9.7, Import 0.9.8, Import 1.0.0, Import 1.0.1, Import 1.0.2, Import 1.0.3, Import 1.0.4, Import 1.0.5, Import 1.0.6, Import 1.0.7, Import 1.1.0, Import 1.2.0, Import 1.3.0, Import 1.4.0, Import 1.5.0, Import 1.5.1, Import 1.5.2, Import 1.5.3.

- Size: 6,438 → 9,279 lines; functions and constants: 262 → 369
- New functions/constants (108): `addCell`, `allWorkGids`, `applyColumnDate`, `applyPoolToPlan`, `ART_TYPES`, `autoSearchWorks`, `bassAskHtml`, `buildVocabulary`, `canRoleCredit`, `caseCredit`, `caseWord`, `cellHtml`, `cellMenuHtml`, `cellOwnDate`, `cellState`, `columnDate`, `columnHeadHtml`, `computePublisherEvidence`, `CREATABLE`, `DATE_GROUPS`, `dateGroupOf`, `defaultRowsOf`, `DIAG`, `diagDialog`, `diagEntity`, `diagLog`, `diagRel`, `diagScan`, `diagShape`, `diagTick`, `discogsWritersOf`, `emptyDate`, `fillSimilar`, `findMediumToggle`, `finishWorkRun`, `GENERIC_WORDS`, `inMedium`, `instrumentVocabulary`, `isPending`, `isPlaceholderTitle` … (+68)
- Removed (1): `workRowHtml`
- Changed (82): `addManualEntry`, `applyDetailFlags`, `applyPlan`, `attrCell`, `autoSkipExisting`, `buildLogWindow`, `buildOverlay`, `buildWorkQuery`, `buildWorkSeed`, `COMPANY_ROLES`, `computePlan`, `continueWorkQueue`, `dateCell`, `describeItem`, `dispatchAddRelationship`, `editNoteBlock`, `FALLBACK_LANGUAGES`, `fetchDiscogsArtist`, `flagForDetail`, `groupHtml`, `I18N`, `idx`, `init`, `injectStyles`, `insertLauncher`, `instrumentCandidates`, `levelCell`, `levelsOfType`, `loadDiscogs`, `loadWorkOptions` … (+52)
- Texts (English keys): 395 → 578; new: `matrix.*` (44), `log.*` (34), `msg.*` (28), `works.*` (22), `date.*` (9), `medium.*` (6), `unmapped.*` (6), `scope.*` (5), `busy.*` (3), `note.*` (3), `otherDlg.*` (3), `preview.*` (3), `seriesLabel.*` (3), `bass.*` (2), `footer.*` (2), `link.*` (2), `match.*` (2), `common.*` (1), `group.*` (1), `issue.*` (1), `kind.*` (1), `launcher.*` (1), `level.*` (1); removed: 0
- State `S`: new `capLimit`, `capOn`, `mediumFilter`, `staged`; removed –
- Browser storage: new `dci-role-codes`, `dci-stage-cap`, `dci-stage-cap-on`, `dci-work-options`; removed –

## Reconstructed: companion 0.2.2 – 1.5.0

The companion keeps most of its code inside two functions (MusicBrainz side and Discogs side), so "changed" often names only those.

### 1.4.5 → 1.5.0

Covers COMPANION 1.5.0.

- Size: 762 → 806 lines; functions and constants: 28 → 29
- New functions/constants (1): `findCreditAt`
- Removed (0): –
- Changed (2): `initReleasePage`, `renderStatus`

### 1.4.4 → 1.4.5

Covers COMPANION 1.4.5.

- Size: 760 → 762 lines; functions and constants: 28 → 28
- New functions/constants (0): –
- Removed (0): –
- Changed (1): `ensureStyle`

### 1.4.2 → 1.4.4

Covers COMPANION 1.4.3, COMPANION 1.4.4.

- Size: 698 → 760 lines; functions and constants: 28 → 28
- New functions/constants (0): –
- Removed (0): –
- Changed (3): `initReleasePage`, `norm`, `STORE_EPOCH`

### 1.4.1 → 1.4.2

Covers COMPANION 1.4.2.

- Size: 680 → 698 lines; functions and constants: 27 → 28
- New functions/constants (1): `STORE_EPOCH`
- Removed (0): –
- Changed (1): `norm`
- Browser storage: new `dci-store-epoch`; removed –

### 1.4.0 → 1.4.1

Covers COMPANION 1.4.1.

- Size: 658 → 680 lines; functions and constants: 26 → 27
- New functions/constants (1): `resetArt`
- Removed (0): –
- Changed (3): `initDiscogsSide`, `initMusicBrainzSide`, `renderArtwork`
- Browser storage: new `dci-art-reset`; removed –

### 1.3.0 → 1.4.0

Covers COMPANION 1.4.0.

- Size: 594 → 658 lines; functions and constants: 24 → 26
- New functions/constants (2): `makeArtMovable`, `placeArt`
- Removed (0): –
- Changed (2): `ensureStyle`, `renderArtwork`
- Browser storage: new `dci-art-pos`; removed –

### 1.1.0 → 1.3.0

Covers COMPANION 1.2.0, COMPANION 1.3.0.

- Size: 439 → 594 lines; functions and constants: 18 → 24
- New functions/constants (6): `artLabels`, `artworkUrl`, `keepPerRelease`, `openDiscogsImages`, `PER_RELEASE_MAX`, `renderArtwork`
- Removed (0): –
- Changed (9): `ensureStyle`, `initDiscogsSide`, `initMusicBrainzSide`, `initReleasePage`, `inTracklist`, `locateWithRetry`, `MARK_SYMBOL`, `norm`, `renderStatus`
- Browser storage: new `dci-art-collapsed`; removed –

### 1.0.3 → 1.1.0

Covers –.

- Size: 419 → 439 lines; functions and constants: 17 → 18
- New functions/constants (1): `initReleasePage`
- Removed (0): –
- Changed (3): `initDiscogsSide`, `initMusicBrainzSide`, `locateWithRetry`

### 1.0.2 → 1.0.3

Covers –.

- Size: 408 → 419 lines; functions and constants: 17 → 17
- New functions/constants (0): –
- Removed (0): –
- Changed (2): `initDiscogsSide`, `initMusicBrainzSide`

### 1.0.1 → 1.0.2

Covers –.

- Size: 401 → 408 lines; functions and constants: 17 → 17
- New functions/constants (0): –
- Removed (0): –
- Changed (2): `initDiscogsSide`, `initMusicBrainzSide`

### 1.0.0 → 1.0.1

Covers –.

- Size: 377 → 401 lines; functions and constants: 17 → 17
- New functions/constants (0): –
- Removed (0): –
- Changed (2): `initDiscogsSide`, `initMusicBrainzSide`

### 0.3.0 → 1.0.0

Covers COMPANION 1.0.0.

- Size: 284 → 377 lines; functions and constants: 14 → 17
- New functions/constants (3): `findCredit`, `MARK_SYMBOL`, `renderStatus`
- Removed (0): –
- Changed (4): `ensureStyle`, `initDiscogsSide`, `initMusicBrainzSide`, `inTracklist`

### 0.2.2 → 0.3.0

Covers COMPANION 0.3.0.

- Size: 275 → 284 lines; functions and constants: 14 → 14
- New functions/constants (0): –
- Removed (0): –
- Changed (1): `initMusicBrainzSide`

## Import 0.1.0 – 0.9.1, Companion 0.1.0 – 0.2.1

The code of these versions was not kept (the first upload to this repository is Import 0.9.2 with Companion 0.2.2). What they did is in the [changelog](mb-vibecode-credits-importer-CHANGELOG.md).
