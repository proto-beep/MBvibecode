# MB x Vibecode – Code changes

What changed **in the code** with each version of both scripts, newest first. It is meant for whoever works on the scripts (the maintainer, or the AI that writes them): which parts, functions, stored data, texts and tests a version touched. What a version means **for users** is in the [changelog](mb-vibecode-credits-importer-CHANGELOG.md).

- **Import** = MB x Vibecode: Credits Importer (`mb-vibecode-credits-importer.user.js`; until 3.3.0 `mb-discogs-credits-import.user.js`)
- **Companion** = MB x Vibecode: Credits Importer Companion (`mb-vibecode-credits-importer-companion.user.js`; until 1.6.0 `mb-discogs-credits-sync.user.js`)

## How this file is kept

From 3.5.0 on, every change to the code comes as a pull request that also adds an entry here, at the top: the version, then what changed in the code – parts and functions (new, changed, removed), state (`S`), browser storage, texts (i18n keys), rules of the register, CSS, event handlers, edit note, tests – and anything to watch out for. Functions are named as in the code, so they can be found with a search.

How far back the entries go:

| Versions | Source | Detail |
|---|---|---|
| Import 3.0.0 – 3.50.0, Companion 1.6.0 – 1.13.0 | the working sessions | written by hand, per version |
| Import 2.17.0 – 2.19.1 | the working session, and a comparison of the code of 2.16.0 and 2.19.1 | short notes for 2.19.x, otherwise the comparison |
| Import 0.9.2 – 2.16.0, Companion 0.2.2 – 1.5.0 | the versions uploaded to this repository (19 of the main script, 14 of the companion) | reconstructed: a comparison of the code from one upload to the next; versions in between are named, the changelog says what they do |
| Import 0.1.0 – 0.9.1, Companion 0.1.0 – 0.2.1 | none: the code of these versions was not kept | only the changelog |

**Texts (from 3.27.1):** a new text is added in English only (`tools/i18n_add.py` with `{"en": {…}}`); German, Spanish and French follow in a translation round every few versions – until then `tr()` shows the English text. `smoke/t_i18n.py` fails on a key the code names without an English text, on a left-over translation, on a placeholder English does not have and on a French plain space before ":", ";", "?", "!" (or inside « »), and reports what each language still lacks (`LIST=1` lists the keys). **From 3.34.0** German, Spanish and French are in `mb-vibecode-credits-importer-languages.json`; the tools write there.

The comparisons were made with a small script: functions and constants of the main level of the script are compared by their text (a "changed" function may have changed only in a comment), texts by their English keys, storage keys where the code reads, writes or lists them, rule ids where the register defines them.

## Import 3.50.0 · 2026-11-04

Block 7 – Z-PRO, Z-TAR.

- **`TEXT.parse`:** [S079] **`proseCredits(text)`** (new; `proseName`, `playRoles`): "… <instruments> (<names>), with (special) guest(s) <name> <instruments> [and …], and <name> …" → `{ credits: [[name, role, guest]], lead }` – the longest end of the words before the brackets that is instruments or voices; the guests split at commas and at "and" before two capitalised words, a part of only instruments the name's before; `lead` the words before "with" when they are no "(names)". `readUnit` reads it before the clauses (guests `[Guest]`), `lead` with `readUnit` again (not recognized: listed).
- **`personCase`:** [S059] a word `^\p{Lu}\p{Lu}\p{Ll}{2,}$` (not `MC…`, `D…`, `O…`) in normal case ("SHelley").
- **Dashboard:** `S.mbTracks[i].trackArtistNames` (the artist credit's names, `nameKey`); [S078] **`applyTrackArtistTracks()`** (new; after `applyPerformerTracks` in the import and on a change of S078): rows `dAllTracks`, level recording, a performing type (`PERFORMING_TYPES`), no company, hand-made, supplement or S046 row – the chosen tracks whose artist credit names the entry (`name`, `rawName`, `caseFrom`, `mbName`, or `mbid`), when some but not all; `s078` keeps the tracks before, `tarPositions` the label (`.dci-tartracks` below the role, `ruleIdsOf` S078); log `tarTracks`.
- **Rules:** S078, S079 (new), S059's note.
- **Texts:** `role.tarTracks`, `log.tarTracks`.
- **Tests:** `t_text_lists.py` **prose**, **trackartists**; `register_golden.json` anew (the rules).
- **Review of Block 7:** `proseCredits`: the words before "with" split (`proseSplit`, commas in brackets kept) – each part "<instruments> (<names>)" read (the words before the instruments aside only in the first and only a few plain words; names in brackets of two words or of a release artist), the other parts the `lead` (with brackets or digits: null); guests by **`proseGuest`** ("Name (roles)", "Name on X", else the longest name with the instruments after it in small letters); `proseName` without `PROSE_NOT_NAME` words, `PROPER_WORDS`, `TEXT_NOT_NAME`, `TEXT_PLACE_WORDS`, regions; `readUnit` counts the lead's parts. `personCase`: not `\p{Lu}J…`, `Ó…`. `applyTrackArtistTracks`: `TAR_TYPES` (instrument, vocal, performer), the entry's name variations and the row's `anv`, `s078.set` (switched off: back only while the row has those tracks; a row of S046: its `s046` gets them), **`rebaseFields(row, keys)`** (new; `TAR_FIELDS`), run once more after `resolveArtists`; **`copyRuleTracks(from, to)`** (new; `cloneRow`, `copyRowForEvent`: `s046`, `s078` with sets of their own). Edit note: "Tracks from the artist credits of the tracks in MusicBrainz: NAME (role): tracks" for rows staged.
- **Tests (review):** `t_text_lists.py` **prose2**, **trackartists2** (new).

## Import 3.49.0 · 2026-11-04

Block 6 – Z-RTL, Z-ROL, Z-RPB, Z-EXC.

- **`TEXT.parse` → `readLine0(raw, sub)`:** [Z-RTL] a "Name – …" line whose roles end each in their own track list (`SPEC`) is read part by part (`sub`: the same `line0`). [Z-ROL] "X sample(s)" beside X (or Xs) of the same name → "sampler". [Z-EXC] `exceptHead` ("All compositions|music|songs|lyrics [and lyrics|music|words] by NAMES except:"), `titleBlock` (a line `resolveTitles` resolves – ignored 'exceptTitle'; its lines take its track as their scope, up to an empty line), `covers` ("Originally performed by …", ignored 'cover'), `quotes` ("End quote from W by N", ignored 'quote'); after the lines the names of the head on the other tracks (`trackCount`; all when unknown); a cover with an arranger credit on its track `arranged`. `parse` and the text and Bandcamp releases return `covers`, `quotes`; `sourceContext` and the Bandcamp parses pass `trackCount`.
- **`readClause`:** [Z-RPB] "… by NAMES between A and B": `inArea` for A and B with the verb; the verb skips `additional|extra|further|live|location`.
- **`STATUS_MARKS`:** several marks, also without a space after them.
- **Mapping file:** R026 `production`, `instrumental production`; R003 `composition(s)`; R011 `overtone singing`, `harmonic overtone singing`, `throat singing`; **R109** (new) `<vocal|drum|guitar|…> sample(s)` → samples from artist; `INSTRUMENT_ALIASES` `juno`, `roland juno`, `evi`, `highland bagpipes`, `highland pipes`; `FIXED_ROLE_CREDITS` Juno / Roland Juno → analog synthesizer.
- **Dashboard:** `IDX.arrangementLt`, `IDX.quoteLt`; **`setWorkNotes(rel)`** (new; after "Import complete"; `S.textCovers`, `S.textQuotes`, `S.workRels` by the MusicBrainz track of the title), **`writerNamesOf(i)`**, **`findWorkRels()`** (new; `work:"title" AND (artist:"name" …)`, the same title by one of the names), **`workNotesHtml(i)`** (new; below the track's title in the works matrix, `.dci-mx-wnote`); `coverAutoNow` – a cover of the text "cover", an arrangement not; plan items **`work-rel`** (`wrel|kind|from|to`; the track's first work, new ones too) and their staging (`dispatchAddRelationship`, the original entity0 for "arrangement", the quoting work entity0 for "lyrical quotation"); `describeItem`, the preview (`preview.arrangementOf`, `preview.quotesFrom`); the edit note lines "Cover: …", "Arrangement: …", "… – not found in MusicBrainz".
- **Texts:** `ignored.why.exceptTitle`, `ignored.why.cover`, `ignored.why.quote`, `wnote.cover`, `wnote.arranged`, `wnote.arrangementOf`, `wnote.quotesFrom`, `wnote.staged`, `wnote.needWork`, `wnote.notFound`, `wnote.search`, `preview.arrangementOf`, `preview.quotesFrom`.
- **Tests:** `t_text_lists.py` rolesplit, roles, places, oldmarks, exceptread, exceptworks; `harness.py` (`JS_WORKS`; the work search also by `artist:"name"`); `register_golden.json` anew.
- **Review of Block 6:** plan items `work-rel` – never `from === to`, never a key of `S.existing.loose` (`work|work|type`), a new work only with its own link (`link|recording|work` seen, staged, applied or in MusicBrainz, like the suite parts); staged with `noteKind: 'workRels'` and `S.noteStats.workRels` (edit note "linked N works with the works they arrange or quote"). **`findWorkRels`**: `lucenePhrase`, `arid:` of the linked writers (**`writerEntriesOf(i)`**), no search without a name (`state 'noWriter'`), a failed one `state 'error'`; the arrangement's title `workTitleOf(track title)`. **`workNotesHtml`**: `wnote.needOwn` (the track's work is the original), `wnote.exists`, `wnote.noWriter`, `wnote.error`. **`setWorkNotes(rel)`** → reset and **`addWorkNotes(rel)`** (new; tracks with a cover or quote keep theirs; `applySupplement` calls it); `setWorkNotes(null)` at the start of each import. Edit note: covers and "not found" only for tracks chosen with the works matrix in use, a cover while one of its links has "cover". `TEXT.parse`: **`exceptHeads`** (each header its `blocks`; several headers), a title (its number, quotation marks, colon aside) starts a block inside a block too, an empty line ends a block only after one of its lines (`titleBlock.n`), **`blockScope()`** for `readBlock`, `readHeading`, `readStacked`; a header without blocks or without `trackCount` → `unrecognized`; covers – any line "originally/first performed|recorded …", "original (version|artist) by", "original artist:", "as performed by" – are ignored, the name without "(…)" and a year; quotes split at the last " by ". [Z-RTL] parts without a leading "and"/"&", each credit with `part` (its text) and `pi` (its number), a part not read `line → ? “part”`. [Z-ROL] no sampler for vocal, voice, choir … words. [Z-RPB] "between" only when `areaOf` finds both. `patternText`: `\s`, `\s+`, `\s*` as a space (`register_golden.json`: R084, R109). `DK_SEMANTIC` (3.48.0): each rule on one line (`t_ui_settings.py theme` G: the lines of the dark sheet are its rules).
- **Tests (review):** `t_text_lists.py` **exceptlayouts**, **rolesplit2**, **exceptworks2** (new), exceptworks C (the original entity0 by its id, the edit note's count); `harness.py` `WS_FAIL['worksearch']` (work searches answer 400).

## Import 3.48.0 · Companion 1.13.0 · 2026-11-04

Block 5 – Z-MCP, Z-DMY, Z-HYP, Z-IGN, Z-LIN.

- **`TEXT.parse` → `readLine`:** [Z-HYP] a line "Name -roles" (no " – " in it, a dash before a letter, at most 5 words before it) becomes "Name - roles". [Z-IGN] `ignored` with `why` 'heading' (`credits`, `liner notes`, `personnel`, `musicians`, `line-up`, `Besetzung`, `Mitwirkende` alone), 'releaseDate' (`released|published|veröffentlicht` + a date), 'definition' (`Word (n.)` … and, `definitionNext`, the next line without a credit sign). [Z-LIN] `linerNotes` after "Notes by NAME:" (`line0`): a line of 20 words or more, or of 6 or more ending as a sentence without a credit sign (`Role:`, ` – `, ` by `), is left out ('linerNotes').
- **Mapping file:** `TEXT_THANKS` (and with it `TEXT_IGNORE_LINE`) – gratitude: "infinite / endless / eternal / deep(est) / much / all my / love and gratitude", "gratitude to", "(so / forever) grateful to".
- **Dark theme:** **`DK_SEMANTIC`** (new; appended by `darkCss`): `--sugg-*`, `--date-*`, `--track-*` (and their `-dkg`) by hand on `#dci-overlay`; `color: var(--sugg-ink)` on the suggestion grounds whose text comes from elsewhere (`.dci-date-chip.dci-pchip-sugg` and its parts, `.dci-dm-cell.dci-dm-auto`, `.dci-em-chip-ask`, `.dci-mx-newworks`, `.dci-row.dci-unmapped > td`); the yellow grounds written as colours (`.dci-waiting`, `input.dci-from-dg`, `.dci-foot-chip-warn` …) as `--sugg-bg` / `--sugg-line` / `--sugg-ink`.
- **Texts:** `ignored.why.heading`, `ignored.why.releaseDate`, `ignored.why.definition`, `ignored.why.linerNotes`.
- **Companion 1.13.0:** `.dci-dg-mark` `user-select: none`; **`copyWithoutMarks()`** (new; from `ensureStyle`): on "copy" a selection with marks is copied without them (plain text laid out off the screen, and HTML).
- **Tests:** `t_text_lists.py` (new: hyphen, ignorelines, linernotes), `t_ui_settings.py darkmeaning`, `t_companion_discogs.py copymarks2`.
- **Review of Block 5:** `readLine` is now a wrapper of **`readLine0`**: after "Notes by NAME:" (`linerNotes`) and on the line after a definition (`definitionNext`, reset by an empty line) what a line gives as not recognized – and nothing else – goes to `ignored` ('linerNotes' / 'definition'); the word-count rules are gone. Definition: `(n.)`, `(v.)`, `(adj.)`, `(adv.)`, `(noun)`, `(verb)` … and an optional `/…/` to the end of the line. Heading, release date and definition set `pubBlock = null` (a heading also `linerNotes = false`); "liner notes" no heading. Hyphen: no colon, no ` by | at | in `, the first item after the dash a role (`isRole`) or in small letters. Companion `copyWithoutMarks`: the text by `sel.toString()` with `html.dci-copying .dci-dg-mark { display: none }`, the HTML of the detached copy with absolute `href` / `src`. `DK_SEMANTIC`: `--sugg-line` #b8922f, `--date-line` #8a83cc, `--track-line` #c47a4e; the suggestion text only on `.dci-chip-main` (chips, cells). `smoke/register_golden.json` written anew (T030 shows the gratitude words).
- **Tests (review):** `t_text_lists.py` hyphen (colon, "Mary -Kate", "by" line), ignorelines (a credit after a definition, "Björk (v)", publishers), linernotes (credits among the notes); `t_companion_discogs.py copymarks2` (several lines, hidden text, a selection without marks, absolute links); `t_ui_settings.py darkmeaning` (the line, the grip).

## Import 3.47.0 · 2026-11-04

Block 4 – Z-GST.

- **`STATS_SCOPE_KEY`** ('dci-stats-scope': 'global', else this browser; `S.statsScope`; in `TOPIC_KEYS.statistics`, `SETTINGS_KEYS`, `resetSettings`, `resetTopic('statistics')`), **`GLOBAL_STATS_URL`** (raw.githubusercontent.com, branch `stats`, `stats/mb-vibecode-credits-importer-global.json`), `GLOBAL_STATS_CACHE_KEY` ('dci-stats-global': { at, data }), `GLOBAL_STATS_MAX_AGE` (a day).
- **`globalStatsLoad(force)`** (new; `httpGet`, the copy when younger than a day; a failure keeps the copy, `S.globalErr`), **`globalStatsHtml()`** (new: head with the date of the dump and "Load again", tiles `data-stat="g-…"`, `[data-el=stats-global-months]`, lists `stats-global-versions|sources|types|levels|edits|status`). `renderStats`: the switch `data-act="stats-scope"` in the head ("this browser only" only there); click cases `stats-scope`, `stats-global-reload`. CSS `.dci-stats-scope`.
- **Texts:** `stats.scope`, `stats.scope.local`, `stats.scope.localTitle`, `stats.scope.global`, `stats.scope.globalTitle`, `stats.global.head`, `stats.global.privacy`, `stats.global.old`, `stats.global.none`, `stats.global.reload`, `stats.global.edits|submissions|editors|credits|works`, `stats.global.top.versions|sources|types|levels|edits|status`, `stats.global.st.open|applied|failed_vote|failed_dependency|error|failed_prerequisite|no_votes|deleted`.
- **Repository:** `.github/workflows/global-stats.yml`, `stats/global_stats.py`, `stats/test_global_stats.py`, `stats/README.md` (pull request of their own, from the alpha #68).
- **Tests:** `t_ui_settings.py globalstats`.
- **Review of Block 4:** **`globalStatsClean(d)`** (new: each section an object of numbers, months and versions objects of numbers, at most 200 entries; null without totals) for the file and the copy; `globalStatsHtml` → try/catch around **`globalStatsView()`**; sources mapped to the script's names (`pasted text` → text, `cover art text` → ocr) and merged by label, status and level labels fall back to the key (`lbl`), versions compared over all their parts; `renderStats` restores focus with `data-scope`; the copy fresh only when `at <= now`; while loading anew the copy is shown; "Load again" with `?t=<now>`; files over 2 MB refused; the loading view has "Load again". `conn.X010` names the global statistics.
- **Tests (review):** `t_ui_settings.py globalstats` E (a file with gaps), F (keyboard focus), G (a copy older than a day).

## Import 3.46.0 · Companion 1.12.0 · 2026-11-04

Block 3 – Z-DM.

- **Themes:** `THEME_WIN_KEY` ('dci-theme-window', default 'auto'), `THEME_PAGE_KEY` ('dci-theme-page', default 'light'), `THEMES`; `themeSetting(where)`, `systemDark()`, `themeDark(where)`, `setTheme(where, v)`; **`applyTheme()`** (new): a class `dci-dk-<root>` on `<html>` per part – `DARK_ROOTS` = the dashboard (`#dci-overlay`: the page's theme with `inPage()`, else the windows'), the log (docked: the page's), the rules (docked: the dashboard's), `DARK_WIN_ROOTS` (OCR window and peeks, line peek), `DARK_PAGE_ROOTS` (page bar, launcher, controls, the buttons, notice, language box); when a class changes, `applyLevelColors` / `applyKindColors`. Called by `injectStyles` (and a matchMedia change listener), `applyPlacement`, `renderLogPlace`, `placeRules`, `resetTopic('appearance')`.
- **Dark stylesheet:** `injectStyles` adds `style#dci-styles-dark` = **`darkCss(css)`** (new): comments and `@keyframes` left out, `@media`/`@container`/`@supports` walked; each rule's colour declarations (`DK_COLOR_PROPS`, custom properties with a colour or a var()) repeated – also without a colour, so that the order stays –, colours by **`darkColor(c, kind)`** (text: lightness at least 0.7, white kept; ground: turned round, 0.11 + (1 − l) · 0.82, dark grounds 0.18 + l · 0.6, colours of their own l · 0.9; shadows as they are; white text on a background of its own colour kept); selectors by **`darkSelector(x)`** (a root id: `html.dci-dk-<root> x`; else `:where(<dark roots>) x` and, for a compound selector, `x:where(<dark roots>)`); `color-scheme: dark` on the dark roots. Helpers `dkParse`, `dkHsl`, `dkRgb`, `dkOut`, `dkAccent`, `mixHex`, `DARK_GROUND`.
- **Palettes:** `darkTone(hex, minL)`, `darkToneOf(what, hex)` (levels lightness ≥ 0.62, kinds ≥ 0.38); `DARK_COLORS_KEY` ('dci-dark-colors'), `LEVEL_PALETTE_DARK_KEY`, `KIND_PALETTE_DARK_KEY`; `S.darkColors`, `S.levelPaletteDark`, `S.kindPaletteDark` (only colours chosen), `darkPaletteColor(what, k)`, `saveDarkPalette(what)`, `overlayDark()`. `applyLevelColors` / `applyKindColors`: dark → those colours, the kind background mixed with `DARK_GROUND` (0.2); `inkOn(hex, dark)` – dark: the threshold of equal contrast (0.21).
- **Settings:** Appearance – two rows `data-el="theme-window|page"` (`data-act="theme-set"`), `data-set="dark-colors"`, while on two rows of pickers (`level-color-dark`, `kind-color-dark`; preview on input) with `data-act="dark-colors-reset"`. The five keys in `TOPIC_KEYS.appearance` and `SETTINGS_KEYS`.
- **Texts:** `settings.themeWindow`, `settings.themeWindowTitle`, `settings.themePage`, `settings.themePageTitle`, `settings.theme.auto`, `settings.theme.light`, `settings.theme.dark`, `settings.darkColors`, `settings.darkColorsTitle`, `settings.levelColorDark`, `settings.kindColorDark`, `settings.darkColorsReset`.
- **Companion 1.12.0:** `siteDark()` (YouTube `html[dark]`; a "dark" class or `data-theme` / `data-color-mode` / `data-color-scheme` on html or body, its own `dci-…` classes left out; else the luminance of the first background of `ytd-app`, `#pgBd`, body, html below 0.2), `watchSiteDark()` (class `dci-site-dark` on html; a MutationObserver on the attributes of html and body, matchMedia; 120 ms later); `ensureStyle` – rules for `html.dci-site-dark`, calls `watchSiteDark`; `initSourceSide` calls `ensureStyle`; the box of several imports (`#dci-multi`) after `ensureStyle`.
- **Tests:** `t_ui_settings.py theme` (A defaults and the light theme unchanged, B as a window dark with a contrast scan, C in the page, D Auto live, E colours of their own, F defaults of the topic), `t_companion_discogs.py sitedark`.
- **Review of Block 3:** `resetSettings` – `darkColors`, `levelPaletteDark`, `kindPaletteDark` cleared, `applyTheme()`. `darkCss`: a text variable (`DK_TEXT_VARS`) gets `<name>-dkg` (its colour as a ground) beside it, `background*` declarations use it (`var(--ok)` → `var(--ok-dkg)`); `@keyframes` with colours get a dark copy `<name>-dk`, `animation`/`animation-name` switch to it; selectors split by **`splitTop`** (new; not at commas in brackets or quotes); `dkParse` reads % and alpha in %. `darkSelector`: regexes made once (`DK_ROOT_RES`), "in a dark part" only the parts not inside another (`DARK_TOP_ROOTS`, `DK_IN_ANY`), the part itself all (`DK_IS_ANY`). **`ensureDarkSheet()`** (new): `applyTheme` makes `#dci-styles-dark` when a part is first dark and sets `disabled` while none is (`injectStyles` no longer makes it). `DARK_PAGE_ROOTS` without the boxes of other MusicBrainz pages (no stylesheet there; their colours inline) and `dci-twice`, `dci-room`; `settings.themePageTitle` says so. **`darkChipStyle(what, k)`** (new): the tags beside the dark pickers with their dark colours (inline variables; on input too). Companion: `siteDark` – whole class words (`DARK_CLASSES`), the theme attributes "dark" / "…-dark", **`rgbOf(css)`** (new; through a canvas: oklch(), lab() …); `ensureStyle` appends to `document.head || document.documentElement`.
- **Tests (review):** `t_ui_settings.py theme` G (no dark stylesheet before; written = read; off again; light as at the start; dark keyframes), H (white text on a text colour: best match, "Apply" hovered), I (tags beside the dark pickers), J ("Reset all settings"); `t_companion_discogs.py sitedark` (oklch(), "header-dark", "darkblue-light", data-theme taken away).

## Import 3.45.0 · 2026-11-04

Block 2 – Z-STD.

- **`STATS_TIME_KEY`** ('dci-stats-time': 'mean', else the median), **`STATS_IDLE_KEY`** ('dci-stats-idle', 300 s), `statIdleMs()`; both in `SETTINGS_KEYS`, `TOPIC_KEYS.statistics` / `.cache`. ⚙ Cache: `data-set="stats-idle"` beside `stats-on` (empty = default).
- **`statActivity(e)`** (new; `initOnce` adds it once for click, keydown, pointerdown (capture), wheel, touchmove (capture, passive) and visibilitychange): a gap since `S.statLastAct` (or `S.statStart`) of at least the threshold adds to `S.statIdle`; hidden: the pause starts then.
- **Records:** `idle: S.statIdle` in `statSnapshot`; at the confirmation `work = armedAt − start − idle` (beside `ms`). **`statTime(r)`** (new): `work`, else `ms` – used by `statAgg` (perRelease, perRel, per period) and `statMore` (fastest). `statMore` collects `m.srcTime` (source → release → { ms, rels, supp }).
- **`statSourcesHtml(m, top, srcName)`** (new): the switch (`data-act="stats-time-view"`), a table `.dci-stats-srct` (source, releases, per release, per relationship, with supplement: n · per release); `statMedian`, `statMean`. Click case `stats-time-view`.
- **Texts:** `stats.timeView`, `stats.time.median`, `stats.time.mean`, `stats.srcT.n`, `stats.srcT.perRelease`, `stats.srcT.perRel`, `stats.srcT.supp`, `settings.statsIdle`, `settings.statsIdleTitle`.
- **Tests:** `t_ui_settings.py statstime` (A a pause of 3 s with the threshold 2: idle and work in the record; B the table, Median and Average, remembered).
- **Review of Block 2:** `statSnapshot` closes the open gap first (`statActivity({ type: 'snapshot' })` – the arm listener runs before `statActivity` on the same click). `statActivity` ignores events with `isTrusted === false`, reads the threshold only for a gap of a second or more; listeners now click, keydown, pointerdown (capture) and wheel, touchmove (capture, passive) instead of scroll. `runStatJob`: `work` only when the job's `rec` has `idle` (not for jobs armed by 3.44.x); confirmed on the editor's page (`!final`) and `S.statStart === rec.start`: `S.statStart = armedAt`, `S.statIdle −= rec.idle`, `S.statLastAct` at least `armedAt`. `statMore`: `m.srcRel`, `m.suppRel` (source → Set of mbids); `statSourcesHtml` rows by releases, "with supplement" from `m.suppRel`, Average per relationship Σms / Σrels; `stats.withSupp` from `m.suppRel`. `stats-idle` and `alias-max`: `el.value` set to the stored value.
- **Tests (review):** `t_ui_settings.py statstime` C (a pause with the script's scrolling, then straight "Enter edit"; the second record from the first "Enter edit" on), D (a release submitted twice; Average per relationship pooled; "with a supplement: 1"), E (100000 → 86400); `t_ui_settings.py statsmore` and `t_sources_bandcamp.py youtube` read the card "Sources" as its table.

## Import 3.44.1 · 2026-11-04

Block 1, part 2 – Z-CAT, Z-ALC.

- **`notesTrackCredits`** (S022): no group when the brackets follow a code without a space (`/[A-Za-z]+[-\s]?\d[\w.-]*$/` and "(" right after it) or the name has a word of a sentence (states, says, lists, reads, shows, website, site, page, according, mentions, notes).
- **`ALIAS_MAX_KEY`** ('dci-alias-max', 12), `aliasMax()`; in `TOPIC_KEYS.sources` and `SETTINGS_KEYS`; ⚙ Sources number field `data-set="alias-max"` (0 – 200).
- **`resolveViaAliases(list, source, { one })`:** sorted by the number of rows (then the dashboard's order), at most `aliasMax()`; the rest get `a.aliasLater` (also those after a 429); `setBusy('busy.aliases', { i, n })` while it asks, `busy.artists` again after; `msg.aliasesLater` / `log.aliasesLater`. **`suggestStackHtml`**: "Discogs aliases …" (`data-act="aliases-fetch"`) for `aliasLater` entries; click case `aliases-fetch` (one entry; `log.aliasesNone` without a hit).
- **Texts:** `busy.aliases`, `msg.aliasesLater`, `log.aliasesLater`, `log.aliasesNone`, `match.aliasFetch`, `match.aliasFetchTitle`, `settings.aliasMax`, `settings.aliasMaxTitle`.
- **Tests:** `t_sources.py aliascap`, `t_notes_dates.py catno`.
- **Review of Block 1:** `skippedEv(r)` (new: `emSkipEv` and on skip and no `scopeLevel`/`mxSkipped`/`entrySkip`) in `entryModel` and `rowsInEvent`; `emTick` – a `skip|` key: ✕ takes the rows out of it, the spare row never one of a skipped event (`delete row.emSkipEv`); the drop target excludes `th.dci-em-evskip`, `emDropDate` returns for `skip|`; chips of a skipped event not draggable; `evHeadHtml` passes `a` to the skip head's button. `emEventSkip` back: `levelOf(r, was)`, `emEventMoved`, then `emEventLevel(a, eventKeyOf(rows[0]), to)`; to Skip closes `S.emEvOpen` of that event. `em-evlevel-next` focuses the button of the new key of the rows clicked. `remapRow`: a row of a skipped event resolves its type on the level it comes back to. `resolveViaAliases`: `aliasLater` deleted only after an answer, set again on a failure; `looked` counted and returned; message when any has `aliasLater`; returns early when `importSeq` moved on; `aliases-fetch` logs `aliasesNone` only with an answer. `DISCOGS.pace()` chained (`paceChain`). `alias-max`: empty → default. `notesTrackCredits`: the sentence words case-sensitive, without page/site/notes.
- **Tests (review):** `t_entries.py levelclick` D (focus after sorting anew), E (tick into another event, the skipped event keeps its row); `t_sources.py aliascap` (a failed lookup keeps its button, the count); `t_entries.py evhead` – the opened event offers Skip (3.44.0).

## Import 3.44.0 · 2026-11-04

Block 1, part 1 – Z-CLV.

- **`entryModel`:** rows on "Skip" with `emSkipEv` (the key of their event before) make an event `{ key: 'skip|<key>', level: 'skip', skip: true, from, orig }`, sorted at the place of its level before; the lines' `ev` maps hold them; `b.others` without them.
- **`rowsInEvent`:** a `skip|` key gives the rows skipped with it. **`evLevels(a, e)`** (new): recording/release/release_group/work that MB has for the event's rows (`typeOnLevel`), then 'skip'; **`evLevelNext`** (new): the next one, after 'skip' the first. **`evLevelBtn(e, a)`** (new): `button.dci-cl-level.dci-em-lvbtn[data-act=em-evlevel-next][data-ev][data-n]` with the tooltip. **`emEventSkip(a, evKey, to)`** (new): to 'skip' (`levelOf(r, 'skip')`, `r.emSkipEv = evKey`) or back onto `to` (rows that cannot be there onto the level they had; recordings without tracks get all).
- **`levelOf`** clears `emSkipEv`. **`evHeadHtml`**, **`evShortHtml(e, a)`**: the level a button; a skipped event's head only its number and the button (`th.dci-em-evskip`); compact line of a skipped event `.dci-em-cl.dci-em-skip[data-emskip]` (no drop target). Ticks of a skipped event `td.dci-em-c-skip`, disabled. **`emEventHtml`** levels from `evLevels` (work, skip). Click cases `em-evlevel` ('skip' → `emEventSkip`) and `em-evlevel-next` (new; focus back on the event's number).
- **CSS:** `.dci-em-evskip`, `.dci-em-c-skip`, `.dci-em-evchip-skip`, `.dci-cl-level[data-level="skip"]`. **Texts:** `em.skipTick`, `em.levelBack`, `em.levelNextWork`, `log.emEvSkip`, `log.emEvBack`.
- **Tests:** `t_entries.py levelclick` (compact circle with Skip at its place, the arranger to Work, the full matrix head, ticks and the opened event).

## Import 3.43.5 · 2026-11-04

Full review, package P6 (rendering, events, dashboard).

- **`removeRow`:** an entry as a matrix (`mxOn && (mxEntry || mxCompact)`) → `rerenderGroup(artist)`.
- **`onInput`:** `text-src`/`text-origin` → `S.textForm.text/origin`; `discogs-input`/`supp-url` → `S.srcDraft.other/supp` (new, drawn back by `renderSource`/`suppBarHtml`).
- **`setLanguage`:** `#dci-rules` removed before `rebuildDashboard`, `openRules()` again when it was shown; `renderOcr()` with `S.ocr`.
- **`pool-save`:** guards `fromRow.date` and the plan's `date`.
- **Tests:** `t_entries.py review43` (A line removed, B text kept, C rules window in German).
- **Counter-review:** `places()` keeps the text whole when a piece after "and" has " at " or a lower-case verb; the by-path splits `right` into "name at place" pairs (`\s+(?:and|&)\s+(?=[^,]+\s+at\s+)`) before `at2`. The in/for/with cut only before a lower-case word or a format word. `remapRow`: `row.levelImportFrom` (the rule's level when `levelImport` was set) – the import's level counts only while `m.level === row.levelImportFrom`; `mxSkipped`/`s046Out` rows keep 'skip' (`s046Out.level` follows). `lineLead` is a list; `contWho.names`. S071 prefix list only without a studio word. `rememberFresh(rows)` registers rows added later; called after `loadSeries` for the new rows. `resolveViaAliases` returns when `importSeq` moved on. `splitBy` masks brackets. `roleThenName` strips a trailing bracket. `setLanguage` passes `rulesAsWindow` through. `syncCreatedWorks` prefers the stored index when its recording still fits. Companion `pickTab`: `fresh(t)` (visible or beat < 90 s) sorts first. Corpus: 7 lines (3.43.5).

## Import 3.43.4 · 2026-11-04

Full review, package P5 (staging, edit note, storage, statistics) and P6's first finding.

- **`applyPlan`:** the staged records carry `noteKind` (the target's kind, or 'workLinks') and `noteOrigin`; `uncount(st)` (new) takes a record off `S.noteStats` (also `newWorkLinks`/`pendingWorks`) and sets `noteChanged`; `forget()` calls it (once for a joined group); the edit note is written when `added || fills || linkAttrN || ((noteChanged || updated) && S.lastNoteBlock)`.
- **`saveLiveJob`:** an armed job counts as blocking only while `!had.error && Date.now() - had.armedAt < LIVE_JOB_MAX_MS`. **`statExtras`:** `live.comments` only from a job of this release that is not dead.
- **`SETTINGS_KEYS`** + `EDIT_NOTE_KEY`; **`resetSettings`** also sets `entriesView: 'matrix', joinAuto: true, evShared: 3, emShow: 8, emByDefault: 'event'`.
- **`readMappingImport`:** own rules checked for `level` ∈ RULE_LEVELS ∪ {skip}, `on` boolean, `detailsMode` ∈ {any, exact}, `type` (role) / `instrument` (instrument) present.
- **Tests:** `t_ui_settings.py editnote` E (Photo Guy skipped and back: n, n+1), `reset` (edit note, matrix, joining), `t_rules_window.py mappingio` C (U002 with "foo" not imported).

## Import 3.43.3 · 2026-11-04

Full review, package P4 (works, dates, creating) and P5's first finding.

- **`emEventDateValue`:** the pool entry is reused only with `!!d.ended === !!value.ended`.
- **`syncCreatedWorks`:** entries matched by `rec` (`S.mbTracks.find`), `x.i` refreshed from `track.idx`; entries whose recording is not among the tracks are kept (not planned); the list is written only when something changed; the function returns the planned ones (the message counts those).
- **`savePoolForm`:** the confirm declined → the using rows get `poolId: null, mx: false`, the plans `poolId: null`; `renderWorks()`.
- **`onPaste`** (event date box): `ed-ended` is ticked from the parsed period.
- **Tests:** `t_entries.py evdatefields` F (paste "from 2015 to ????"; two pool entries 1998 with and without "ended"); `t_works_matrix.py review43` (created works by recording, a ghost kept); `t_notes_dates.py review43` (pool edit declined: rows their own, "0 rows").

## Import 3.43.2 · 2026-11-04

Full review, package P3 (flow and state).

- **`remapRow`:** `row.levelImport` (new, set by `addCreditRows` for a producer/creative direction named for tracks and by the S006 loop in `loadRelease`) wins over the rule's level; a row with `srcOff`/`aboutHidden`/`notesHidden` keeps `level: 'skip'` and gets the level to come back to (`srcOffLevel`/`aboutLevel`/`notesLevel`) from the rule. The role-edit remap (`setRowRole`, section 9) keeps a switched-off row too.
- **`loadRelease`:** `saveRememberNow()` right after `source.release()` (before `dropWorkChoices`/`applyMediaChoice`); `if (seq !== importSeq) return;` after `resolveArtists`, `loadSeries` and `computePublisherEvidence`.
- **`rememberSnapshot`:** rows of entries with `srcSeries` are skipped.
- **Create callbacks** (artist, series/event, label/place, the person-as-label merge): `matchTouched: true` with `status: 'created'`, so `rememberSnapshot` stores the match.
- **Tests:** `t_rules_window.py review43` (levels through a quick switch; a created artist remembered after a reload; one series row after a reload); `t_ui_place.py keepplace` forgets the remembered release before its second page (the created artist would come back).

## Import 3.43.1 · 2026-11-04

Full review, package P2 (sources, release page, companion); Companion 1.11.1.

- **`completeMedia`:** the rebuilt tracks carry `'artist-credit'` from `t.artistCredit.names` (gid, name, joinPhrase) → `trackArtists` in `init`, so `performersOf`/`coverAutoNow` see them.
- **DISCOGS:** `PACE_KEY` ('dci-gap-last'), `pace()` (new) – `getJson` waits for 2.5 s since the last request; a 429 throws an error with `status: 429`. `aliases(id)` goes through `getJson` (no silent `[]`). `gapDiscogs` no longer paces itself. `resolveViaAliases`: a failure is logged (`log.aliasFailed`, new text) and after a 429 the loop stops.
- **Companion messaging:** `syncPageId` (new, per page); the jump id is `${syncPageId}:c<n>`, kept in `S.sync.sent` (a Set of the last 50); `onFromDiscogs` ignores a `result` whose id this tab did not send.
- **`sendDiscogsStatus`:** returns early when `S.autostartFrom === 'count'`.
- **Companion 1.11.1:** `liveTabs` keeps a tab whose last beat said `visible: false` for `BEAT_HIDDEN_MS`; the key is deleted only after `BEAT_HIDDEN_MS + 60 s`.
- **Tests:** `t_companion_discogs.py review43` (A hidden tab, B foreign result, C count tab); `t_works_more.py coverworks` D "Track-Artist, Medium nachgeladen" (`WS_NO_RELS`); `harness.py js_tracks` gives `artistCredit`.

## Import 3.43.0 · 2026-11-04

Full review (Q-cx), package P1 – the text adapter; rules S074 – S077 in the register (`TEXT_RULES`); corpus lines for every finding.

- **`TEXT`:** `NAME_TRACKS`, `EXCEPT_TRACKS` (new constants). `splitBy(c)` (new, S075): a clause is split before a second "<verb> by" joined with and/&/slash; `clauses()` maps through it. `placeOf`: a trailing `(…)` without digits becomes the area.
- **`parse`:** `namesScoped(side)` (new) replaces the inner work of `names()`: brackets mask commas/&/and before the split, a release artist (`bandNames`) is kept whole or joined back (S077), the track list in brackets after a name is resolved (S074) → `[{ name, scope }]`; `names()` maps to the names. `places(verb, tail)` (new): the tail after "at" split at ", <verb> at" (own verb) and " and <Two Capitalised Words>" (same verb), each through `place()`; used by both at-paths of the by-sentence and the "verb … at" sentence. By-path: `namesScoped(right)` with per-name scopes; a name with " in/for/with " is cut there, the rest to `unknownParts` (S075). `byRoles`: a phrase with a separator is read part by part first, the whole phrase as a fallback (`whole()`). `readClause`: ≥ 2 bracket groups → `namesWithRoles(clause)` (S076); S055 items split after ")" too; the left side of "Name – roles" through `names()` (`lefts`, S077; `lineLead` only for one name); "Role: names" with per-name scopes. `readUnit`: a clause that gives nothing goes to `unknownParts` when the line has several (S075). `roleThenName`: a name with `:`, `–`, `—`, ` - ` or `(` is skipped. `readLine`: an `EXCEPT_TRACKS` line with a track word (or "except/not" before a number) → `unrecognized` (S074); S071 studio line: not a role (`isRole`, `… By`, additional/live/field/… first), its own `scope` first; "and Name" line: `namesScoped`, scope of the name, then of the line, then of the line above. `headingLists`: the name-above check only for instrument headings (`!h.role`).
- **Tests:** `smoke/text_corpus.json` 24 lines (3.43.0), `register_golden.json` renewed (S074 – S077); `t_sources_bandcamp.py labelpage` B: "Jane Roe & Friends" on Jane Roe's page is one credit of the band with its link (S077; until 3.42.8 cut at "&").

## Import 3.42.8 · 2026-11-03

Block BG, part 9 – collected item Z-YTC (Q-de), with Companion 1.11.0.

- **The YouTube adapter:** `companion: 'youtube'` (until 3.42.7 none) – the companion shows it.
- **`viewSite()`** 'youtube' for it, `VIEW_NAMES.youtube`; **`textSite(site)`** (new): Bandcamp and YouTube, whose credits are lines of a text – `sendDiscogsStatus` sends their places (`refs`: line, part, pi, n) for both, `showSourceOf` jumps to the lines for both (`bandcampPayloadForRows`).
- **`syncSite()`:** a companion that reports no YouTube tabs (before 1.11.0) is old for YouTube (`need: '1.11.0'`); `syncStatusHtml` says so with the new text `sync.oldSiteV` ("needs the companion script {version} or later"); `COMPANION_NEEDED` stays 1.10.0.
- **Texts:** `sync.oldSiteV` (English); the "…Site" texts of the view name YouTube.
- **Tests:** `t_companion_bandcamp.py` new case `ytview` (fails on 3.42.7 / 1.10.1); `smoke/harness.py` `yt_desc_html` (the description drawn as YouTube does: folded, "#expanded", "…more", "Show less"), `yt_page(…, dom=True)`, `open_youtube`.
- **The independent review of Block BG** (11 findings; 10 fixed here, 1 a question – Discogs "Horns"):
  - **`restoreRemembered`:** the de-dup of 3.42.4 only for rows of words given an entry (`una`) – such a row added before takes the place of the row the import gives its entry now (`used`); a copy made on purpose (another event, another instrument of the same role, "＋ Another role") stays (it was left out).
  - **Words given an entry are remembered:** `unaBuild(it, { replay })` (new, out of `unaApply`), `S.unaItems` (the words of this import: name, kind, role, line, tracks, words), the snapshot's `una`, **`unaReplay(repeat)`** (new) in `loadRelease` before `rememberFresh` – the entries come again as the source's, their changes with them (until then lost: "remembered changes left out"); not twice when the import has the entry with that role already (an own rule of texts).
  - **`etcCycle`:** a search that comes back after another kind was clicked keeps its suggestions for its kind (the ones of the kind shown are shown), the timer's id cleared with it, the wait of a newer search kept; chosen meanwhile: no wait.
  - **S073 `prosePart`:** a sentence only when its second or third word is a word in small letters that is no word between names (`JOIN_WORD`) – "With Oliver Lake, Kenny Wheeler and members of the Berlin Philharmonic" gives both guests again.
  - **S071 `STUDIO_LINE`:** recording, studio(s), sound – not "Recordings", "Sounds" (names of labels: "Warp Recordings" below "Mastered by …" no place), nor a line of `TEXT_LABEL_LINE`.
  - **`autoSource`:** a single new link of the release editor is loaded at once only if it is no video or the release links to nothing else (YouTube last).
  - **`evHeadHtml`, `evDateBoxHtml(e, inline, a)`:** what was typed and its error belong to that entry's event and that box (`S.emEvDate.inline`): events of several entries share their key; an error in the fields below opens no second box in the head.
  - **Own rules of texts:** their kind goes with the company (`entity` → `groupCompanies` → `addCompanyEntry`: `setCompanyEntityType` when a row has a type of it) – a place "mastered at" is a place, not a label.
  - **Companion:** see 1.11.0.
- **Tests (review):** `t_text_places.py` new cases `unaremember`, `kindrace` (the places answer late), `ownrulekind`; `t_entries.py` `evdatefields` E; `t_sources_bandcamp.py` `ytlinks` C; `t_companion_bandcamp.py` `ytview` H; `text_corpus.json` "With Oliver Lake, Kenny Wheeler and members of …" and "Mastered by Joe Lambert / Warp Recordings" – each fails before the fix.

## Companion 1.11.0 · 2026-11-03

YouTube (collected item Z-YTC; Q-de: everything the other sources have).

- **`@match` `*://www.youtube.com/*`, `*://m.youtube.com/*`**; `isYoutube`; `SITES` with `youtube`; `mayOpen` opens YouTube videos (`/watch?`) too; `@description` names YouTube.
- **New `YOUTUBE_SIDE`:** `releaseId` = the video id of the page (`ytVideoId`, '' elsewhere), `pageFor` the video's page, `locate` (`youtubeLocate`, six tries – the description comes later), `renderStatus` (`renderYoutubeStatus`: marks before each part of a line, the part greyed when all its credits are off; `ytPlaced`), `stale` (the marks drawn before are gone: YouTube drew the description anew) and `onNavigate` (`yt-navigate-finish`: another video without loading).
- **New `ytDescription()`** (the unfolded description – `#description-inline-expander #expanded yt-attributed-string`, else the folded one and older forms) and **`ytExpand()`** (a click on "…more", `#expand`).
- **`bcStream(root, { nl })`:** with `nl` a "\n" of the text ends a line (YouTube has no `<br>`); `textRoots` gives YouTube's description as the part `notes`; `renderTextMarks` unfolds it.
- **`initSourceSide`:** every 3 s `showMap(side.stale(shownMap))` (drawn again when stale), `side.onNavigate` → beat and marks at once.
- **Review:** `stale` also while nothing was placed yet (a few tries, `ytTries` – the description comes after the page or another video); `onNavigate` takes the line marked by a jump away (`bcUnwrap(BC_HL)`); a description folded by the user ("Show less", `ytFolded`) is not unfolded again when the marks are drawn anew (a jump still unfolds it); the video id without `URLSearchParams` (lint).
- **Version:** `@version` and `COMPANION_VERSION` 1.11.0.

## Import 3.42.7 · 2026-11-03

Block BG, part 8 – collected item Z-YTL (Q-da).

- **The YouTube adapter:** `releaseLinks(relations)` (until 3.42.6 none) – every link of the release to a video (`videoId`: www.youtube.com/watch?v=…, youtu.be/…, shorts …), each video once, as `{ id: <video id>, url: videoUrl(id) }`.
- **`LINKED_SOURCES`** with `youtube`; **`SOURCE_ORDER_DEFAULT`** with YouTube last for physical and digital media (`readSourceOrder` adds it to the end of an order stored before). So the videos are linked sources: `S.sourceLinks`, the picker of **Source ▾**, a pick remembered for the release (`keepSourcePick`), the links of the release editor and of Harmony.
- **`sourceLinkLabel`:** a link named by its address (`url`), as `afterEditLinkLabel` (a video: "YouTube www.youtube.com/watch?v=…").
- **Tests:** `t_sources_bandcamp.py` new case `ytlinks` (fails on 3.42.6); `bandcamp` C: the lists with YouTube last.

## Import 3.42.6 · 2026-11-03

Block BG, part 7 – collected item Z-STG2 (Q-dj, Q-do).

- **The Bandcamp adapter:** `pageTags(html)` (new, exported for the tests) – the album's tag links (`a.tag`), else the `keywords` of its JSON-LD, without the tag of the artist's place (the page's `span.location`, also its first part: "Nashville" of "Nashville, Tennessee"), each once; `release()` passes them to `toRelease`, the neutral release has them as **`bcTags`** (Discogs's `tags` – words of the format – unchanged).
- **The statistics:** `statExtras` stores `genres` (Discogs's genres and styles) and `bcTags` (Bandcamp's tags), each from the source read and the one supplementing it (`statRels`, new); `statsData` counts `m.bcTags` and `m.genresAll` (both, the same word once a release, any case).
- **`statGenresHtml(m, …)`** (new; the card "Genres and styles"): "Combined | Separate" (`data-act=stats-genres-view`; stored in `dci-stats-genres`, `STATS_GENRES_KEY` – only "separate", Combined is the default; a setting of the statistics, reset with the others) – one list, its sources in each item's tooltip ("Discogs 3 · Bandcamp 1"), or a list for each source.
- **Texts:** `stats.genresView`, `stats.genres.combined`, `stats.genres.separate` (English). **CSS:** `.dci-stats-gview`, `h5.dci-stats-gsrc`.
- **Tests:** `t_ui_settings.py` new case `statsgenres` (fails on 3.42.5); `statsmore2` B: the record's `x` has `bcTags` too.

## Import 3.42.5 · 2026-11-03

Block BG, part 6 – collected item Z-ETC (Q-dd).

- **`kindTagHtml(a)`:** an entry not linked (a company without `mbid`) whose rows have relationships for more than one kind (`etcKinds`: of `ETC_KINDS` – label, place, area, artist – those with a type in `typeOptions`) shows its kind as a button (`button.dci-kind-tag.dci-kind-cycle`, `data-act=kind-cycle`, "Label ↻" – ↻ drawn by `::after`, so the tag's text stays the kind's name, as the readers of the heads and the register's golden file read it; its title names the next kind and the order), with "searching in a second …" (`.dci-etc-wait`) while a search waits.
- **`etcCycle(a)`** (new): the next kind – `setCompanyEntityType`; the suggestions of each kind kept in `a.etcHits` (those of the import too): a kind found before shows them again without a request, else `suggestByName([a])` runs once no click followed for a second (`a.etcTimer`; MusicBrainz's limit of one request a second as for every search, `mbWs`); log `etcSearched`.
- **`updateGroupHeader`:** the note of the wait replaced with the tag.
- **Texts:** `etc.title`, `etc.wait`, `log.etcSearched` (English). **CSS:** `button.dci-kind-tag.dci-kind-cycle`.
- **Tests:** `t_text_places.py` new case `kindcycle` (the requests counted; fails on 3.42.4).

## Import 3.42.4 · 2026-11-03

Block BG, part 5 – collected item Z-UNA (Q-dn, Q-dr).

- **The list "… lines not recognized"** (`renderSource`): each word a `span.dci-una-w` (`data-act=una-word`, `unaWordsHtml`), the words chosen `.dci-una-sel`, those given an entry `.dci-una-done` (`S.unaDone`: line → word indexes); the list stays open once a word was clicked (`S.unaOpen`).
- **New:** `unaPick(btn, extend)` (a click; ⇧ extends `S.una` to the word clicked in the same line), `unaName` (the words without the signs around them), `unaFormHtml(line)` (name, kind – artist, label, place, area, series –, role: free text for a person, `UNA_ROLES` filtered by `mapCompanyRole` for the others, "part of" for a series; the tracks of the line – `unaScope` with the text adapter's new `TEXT.lineTracks(line, resolveTracks)` – or the whole release; "Remember as a rule of my own", not ticked), `unaApply()` (a person: `groupCredits` → `newPersonEntry`/the entry of that name → `addCreditRows`; a label, place or area: `groupCompanies` → **`addCompanyEntry(g, rel, leftOutKeys)`** – moved out of `loadRelease`, unchanged – → `setCompanyEntityType`; a series: an entry of its own with "part of" on the release; then `resolveArtists({ only })` and, without suggestions, `suggestByName`). Click cases `una-word`, `una-apply`, `una-close`; change `una-*` in `onChangeInner`.
- **Own rules of texts** (kind `text`: `phrase`, `entity`, `role`, `tracks`): stored with the own rules (`dci-user-rules`), listed in "Mapping rules" (on/off, delete; `data-urule-kind=text`), taken by the import/export of your changes (`OWN_FIELDS`); `sourceContext()` passes them (`ownTexts`), `TEXT.parse` reads a phrase of a part not recognized as its entry (`readOwnTexts`, after the units of a line: the part or the words not recognized are gone).
- **`suggestByName`:** a series looked up by its name (`series?query=series:(…) OR alias:(…)`; the web service's list `series`).
- **`restoreRemembered`:** a row added by hand then that the source gives now itself (the same entry, role, level and tracks) is not added again.
- **Texts:** `una.*` (15), `log.unaAdded`, `log.unaRule`, `rules.kindText`, `rules.textTracksLine` (English). **CSS:** `.dci-una-w`, `.dci-una-sel`, `.dci-una-done`, `.dci-una-form`.
- **Tests:** `t_text_places.py` new case `unawords` (fails on 3.42.3); `smoke/harness.py` searches series (`/ws/2/series`).

## Import 3.42.3 · 2026-11-03

Block BG, part 4 – collected items Z-GON (a – i; Q-dg, Q-dh, Q-di, Q-dm) and Z-BZ.

- **The text adapter (`TEXT.parse`), new rules S069 – S073:**
  - **S069** `STATUS_MARKS`, `STATUS_BANG`: the companion's status marks (✓ ● ○ ✗, "!" first) are taken out of each line before it is read (a text copied from a page the companion marked).
  - **S070** `BULLET`: the tracks after "•" / "·" at the end of a line ("— saxophones • 1, 8"), after `NUMBERS` and before `LEAD_POS` in `readLine`; `lineLead` (set in `readClause` by "Name – roles" and by the branch of some known roles) gives `contWho` – a line below it only of roles (`listRoles`, else `playList` with words to ask, 137d), without colon, dash or "by", gives that name its roles with the line's tracks; an empty line, a heading (S067), a pair (S058) or a block (S051) ends it.
  - **S071** `prevBy` (`{ verb, roles, scope }`, or `{ ignored }`): after one sentence of "by" credits of one name, the next line may go on – `STUDIO_LINE` (capitals, then recording(s) / studio(s) / sound(s)) is the place of its verb (`<Verb> At`, a company of the line), "and Name" one more name of its roles (or left out with a website).
  - **S072** `WEBSITE_BY`, `NOWHERE`: "Website by …" and "Recorded all over the place" are left out (`ignored`, why `website` / `nowhere`).
  - **S073:** in the "With …" branch (S061) a part after a comma that is prose (`prosePart`: five words or more, three in small letters, no roles) gives no credit; `addCredit` gives no person whose name is in `titleNames` (the release's and the tracks' titles; not when it is a name of the release's artist too). `sourceContext()` passes `titleNames` (`S.releaseTitleMb`, new, from the web service, and MB's track titles), the Bandcamp adapter adds the album's title and its tracks'.
- **Mapping:** T021 `TEXT_WHAT_WORDS` with "all (of) (the)" in front ("All songs mixed by X": mixed by, no detail "All songs"); T001 `INSTRUMENT_ALIASES` "horns" → horn, brass (was brass), "sampling" → sampler; new question **Q013** ("horns": horn · brass, credited "horns", `preset: 'horn'`).
- **Instrument questions:** `questionAsks(q, row)` (new) – a question with `preset` asks also while one of its answers is set; `instrumentAskHtml` shows it then as "“horns” is set as horn (credited “horns”) – or as: brass" (the other answers only); `chipAnswers` gives the other answers marked `preset` – the chip's ▾ offers them, without "?" (`emChipHtml`).
- **Texts:** `ignored.why.website`, `ignored.why.nowhere`, `instrAsk.preset` (English).
- **Tests:** `t_text_languages.py` new cases `gondola` (the text as on the page and with ○; the horns) and `blackzenith` (pasted, and as Bandcamp's "about" text) – both fail on 3.42.2; `text_corpus.json` the two Gondola texts and Black Zenith (the instruments of `t_textcorpus.py` with organ, percussion, zither, pedal steel, Wurlitzer, horns, sampling, synthesizer and plurals); `register_golden.json` renewed (S069 – S073, Q013, T001, T021; Discogs "Horns" → horn, "Arranged By [Horns]" → horn arranger); `smoke/harness.py` `REL_TITLE`.

## Import 3.42.2 · 2026-11-03

Block BG, part 3 – collected item Z-FRD (Q-df: one entry a line).

- **The text adapter (S062):** a field recording with a period gives its credit `dateName` ("Ambisonic recordings", the kind of T057) and `dateKey` (the line); `groupCredits` keeps them with the date.
- **`addCreditRows`:** a date with a name of its own goes into the date pool (`poolDateFor(value, null, dateKey, dateName)` – one entry a line) and the row takes it (`poolId`); until 3.42.1 the period stood only at the row.
- **Tests:** `t_text_basics.py` new case `fieldpool` (fails on 3.42.1); `cloudpond` reads the row's date from its chip of the pool.

## Import 3.42.1 · 2026-11-03

Block BG, part 2 – collected items Z-TP and Z-EDM (Q-db).

- **Z-TP:** `renderDates` puts the date pool (with its form) and the track pool (with its form) into `.dci-pools-pair` – two columns (`.dci-pools-col`, `flex: 1 1 auto`) that wrap: side by side when both lines fit, one below the other otherwise; the bar kept while the block is folded likewise.
- **Z-EDM:** the head of an event (`evHeadHtml(e, open, a)`) shows its date as a button (`data-act=em-evdate-open`); **`evDateBoxHtml(e, inline)`** (new) holds MusicBrainz's fields (`mbDateFields('ed', …, true)`: begin, end, ended, ⇣), "Apply" (`em-evdate-apply`, checked by `validateDateFields`, the error shown in the box), "no date" (`em-evdate-clear`) and ✕ – below the head (`S.emEvDate`), and inline in the opened event (`emEventHtml`); **`emEventDateValue(a, ev, value)`** (new, from `emEventDate`, which read the text field and is gone with it, as is `em.badDate`); `ed-copy` copies the begin into the end; `onPaste` fills the fields of `ed-…` in their box.
- **Tests:** `smoke/harness.py` `EV_DATES`, `ev_date()`; `t_entries.py` new case `evdatefields`, and `dates`, `evhead`, `companies` with the fields (the readers of the heads leave the date button out); `t_dates_matrix.py` new case `poolside`. Both new cases fail on 3.42.0.

## Import 3.42.0 · 2026-11-03

Block BG, part 1 – collected items Z-EN2 (Q-dk), Z-CONS (Q-dl), Z-DS.

- **Z-EN2 – no "None" for the edit note:** the segment in ⚙ Settings → Staging is "Full | Simple"; a "none" stored by 3.41.9 – 3.41.15 is read as "simple" (`S.editNoteMode`); `clearEditNote` and the branches for "none" (staging, the live job, `formEditNote`) are gone; texts `settings.editNote.none`, `settings.editNote.noneTitle` removed.
- **Z-CONS – the connections in groups:** **`CONN_GROUPS`** (new; Sources – also X015, images by their address –, Websites, Tools & scripts, Resources, Userscript managers, Links); `connectionsHtml` draws a `<tbody data-conn-group>` per group with a heading row (`.dci-conn-group`, texts `conn.group.*`), by number within; the README table likewise.
- **Z-DS – "Delete statistics …" in ⚙ Settings → Cache:** next to "Collect statistics", with the number of submissions counted (`[data-el=stats-stored]`; `statsLoad` when not loaded yet, the settings drawn anew when it is); deleted: the settings drawn anew. The statistics themselves have no button any more.
- **Tests:** `t_ui_settings.py` new cases `conngroups`, `statsdelete`; `editnote` (Full | Simple, a stored "none" is Simple); `settabs` counts the rows of connections (`tr[data-conn]`). All three new or changed cases fail on 3.41.15.

## Import 3.41.15 · 2026-11-03

Block BF, part 9 – the findings of the independent check of the block (eight), each with a test that fails on 3.41.14.

- **Z-SUB:** a position of a split index stands for all its tracks – **`positionGroups(tracks)`** (new; the `group` of each sub-track: the index's position and the base of its sub-tracks), used by DISCOGS `parseTrackSpec` (a credit for "3" or "1 to 3") and by `tracksInText` ("track 3" in the notes). Until 3.41.14 such a credit went to the first sub-track only, or was not resolved at all. **`gapDiscogs(dId, ws)`:** the line of the release page reads Discogs with MusicBrainz's tracks too (it read the index as one track).
- **Z-SUM:** `addSuite` refuses tracks that are in another suite or split as a medley (`suite.addTaken`); `acceptSuite` leaves the parts of a track that belongs to another suite or medley as they are (until 3.41.14 they were taken over, and undoing the new suite left the track without a work).
- **Z-EN:** choosing an option of "Edit note" rewrites a block written before at once (`clearEditNote` for "None", `writeEditNote` otherwise) – until 3.41.14 only the next staging did, and "Enter edit" in between sent the old block.
- **Q-cn:** "skip the role" leaves the row without a type; `remapRow` keeps a row skipped by an answer on "Skip" without a type; `levelOf` asks the question again when such a row gets a level (until 3.41.14 it kept an earlier answer's type while "skip" showed as chosen).
- **Statistics:** the works of a record from the links it holds (`statExtras(rels)`: linked, created in MusicBrainz's form, new in the editor), the gaps from the supplemented relationships it holds (`statFill(…, kind)` – credits, dates, attrs –, the relationship's `f`), the decisions once a row (`x.decisions`: `statAnswers` of every row, also of one an answer put on "Skip"); a part linked with its suite counts as `noteStats.suiteParts` (the edit note: "linked n parts with their suites"), no longer as a work linked with a recording.
- **Z-YT:** `jsonAfter` finds the data at its assignment ("ytInitialPlayerResponse = {"), not at the first mention of the name.
- **Texts (English):** `suite.addTaken`.
- **Tests:** `t_works_more.py` `subtracks` (a credit for the index), `suiteadd` (overlap), `suiteparts` (the edit note); `t_ui_settings.py` `editnote` (at once), `statsmore2` (decisions once a row; the works of a real record); `t_text_basics.py` `hostask` (skip, then back); `t_sources_bandcamp.py` `youtube` (the name before its assignment); `t_works_matrix.py` new case `statgaps`; `t_start.py` new case `gapsplit`.

## Import 3.41.14 · 2026-11-03

Block BF, part 8 – the statistics of collected items Z-STS, Z-STA, Z-STW, Z-STG, Z-STQ, Z-STL, Z-STV, Z-STC (Q-cv: all proposals; Q-cw: for everyone).

- **Records v 2** (`statSnapshot`): per relationship `a` (its attributes other than instruments and voices); per import `x` from **`statExtras()`** (new): suites (`n`, `created`, `found`, `manual`, `parts`, `medleys`), works (`linked`, `created`, `pending` – of `S.noteStats`), genres (Discogs's genres and styles, at most 12), live (`comments`: the items of the live job), gaps (`credits`, `dates`, `attrs` – of `S.noteStats`).
- **DISCOGS `toRelease`:** `styles` too.
- **`statMore`:** counts `x` (records with it: `m.x`), the attributes, "parts" relationships, live links (attribute live on a work link), the answers `q` (since 3.38.2), the genres once a release, the people of each release (all its submissions) and the pairs of them (at most 40 people a release).
- **`statsMore2Html`** (new, after "Own rules"): the cards Suites and medleys, Attributes, Works, Genres and styles, Decisions, Live, Gaps closed, Worked together (pairs from two releases); "Counted from 3.41.14 on" (`stats.since`) on the cards that need `x` or `a` while older records are there.
- **Texts (English):** `stats.more.suites`, `.attrs`, `.works2`, `.genres`, `.decisions`, `.live`, `.gaps`, `.together`; `stats.suites.*`, `stats.works2.*`, `stats.live.*`, `stats.gaps.*`, `stats.decisionsN`, `stats.since`.
- **Tests:** `t_ui_settings.py` new case `statsmore2` (fails on 3.41.13).

## Import 3.41.13 · 2026-11-03

Block BF, part 7 – collected item Z-YT: the description of a YouTube video as a source.

- **Source adapter `YOUTUBE`** (new; `SOURCES.youtube`): `videoId(text)` (watch?v=, youtu.be/, shorts/, live/, embed/, m. and music.), `videoUrl(id)`, `pageData(html)` (the JSON "ytInitialPlayerResponse" of the page, found by counting its braces outside strings: `videoDetails` title, author, shortDescription), `toRelease(data, id, ctx)` (the description through `TEXT.toRelease`, the video as source, `noteSource` its address), `release(id, ctx)` (the page by `ctx.httpGet`; `err.youtubeData` without a description). `usesMbTracks`, `nameSearch`, no companion, no linked releases (only by address for now).
- **"another source"** (`discogs-load`) and **"+ Supplement"** (`supp-url`): a YouTube address picks `YOUTUBE`.
- **Header:** `@connect youtube.com`; **CONNECTIONS:** X017 YouTube (`conn.X017`).
- **Statistics:** `stats.src.youtube` ("YouTube") in the sources; `statSuppKinds` knows "YT".
- **Texts:** new `err.youtubeData`, `conn.X017`, `stats.src.youtube` (English); `source.other`, `supp.urlPh`, `msg.badDiscogsId` name YouTube videos (in all four languages).
- **Tests:** `smoke/harness.py` `YT_PAGES`, `yt_page()` and the route of www.youtube.com; `t_sources_bandcamp.py` new case `youtube` (fails on 3.41.12); `t_ui_settings.py` `settabs`: 17 connections.

## Import 3.41.12 · 2026-11-03

Block BF, part 6 – collected item Z-SUB (Q-cm): sub-tracks of Discogs that are tracks of their own in MusicBrainz.

- **DISCOGS `subTrackSplit(d, mb)`** (new, exported): the index tracks (of the parts of one track) whose sub-tracks are tracks of their own in MusicBrainz – read alongside MusicBrainz's titles (`titlesFit`): split when the first sub-track and most of them fit the next tracks; without titles that fit, all of them when that gives MusicBrainz's number of tracks.
- **DISCOGS `toRelease(d, id, { split })`:** an index of `split` gives a track per sub-track (the index's credits on all of them, the sub-track's on its own, the index's title as `work`, the index's position as an alias of the first).
- **DISCOGS `release(id, ctx)`:** when MusicBrainz (`ctx.tracks`) has more tracks, reads the release split if that gives MusicBrainz's number (`subTracksSplit` on the release); **`loadRelease`** logs it (`log.subTracksSplit`).
- **Tests:** `t_works_more.py` new case `subtracks` (fails on 3.41.11).

## Import 3.41.11 · 2026-11-03

Block BF, part 5 – collected item Z-SUM (Q-ck, Q-cq): a suite added by hand.

- **State:** `S.suiteManual` (key → `{ key, name, from: 'manual', tracks }`; cleared by `dropWorkChoices`) and `S.suiteAdd` (the box open: from, to, name, error).
- **`suiteAddHtml()`** (new; below the questions in `[data-el=suites]`): "＋ Suite …" (`data-act=suite-add-open`), open the yellow box `[data-el=suite-add]` with `mx-suite-from`, `mx-suite-to` (the tracks of the works matrix), `mx-suite-name`, ✓ Yes (`suite-add-yes`), Cancel (`suite-add-cancel`) and an error line; `matrixChange` keeps the fields in `S.suiteAdd` without drawing anew.
- **`addSuite(from, to, name)`** (new): the tracks of the matrix between them; a name is needed; the offer (key `manual|name|tracks`) goes into `S.suiteManual` and is accepted with `acceptSuite`. **`suiteAsks`** lists the suites added by hand; **`undoSuite`** removes one from `S.suiteManual` (it is not asked again).
- **Texts (English):** `suite.add`, `suite.addTitle`, `suite.addAsk`, `suite.addFrom`, `suite.addTo`, `suite.addName`, `suite.addCancel`, `suite.addNoName`, `suite.addNoTracks`, `suite.from.manual`, `log.suiteAdded`.
- **Tests:** `t_works_more.py` new case `suiteadd` (fails on 3.41.10); `suiteask` reads only the questions (not the line "＋ Suite …").

## Import 3.41.10 · 2026-11-03

Block BF, part 4 – collected item Z-SB2 (the user's screenshot: "44 new relationships · Preview · ⚙ Options · Stage in the relationship editor · ⓘ" cut off at the bottom).

- **`viewW()`, `viewH()`** (new): the room of the windows – `document.documentElement.clientWidth/clientHeight`, the browser window without its scroll bars; `defaultGeom` and `placeWindow` use them instead of `window.innerWidth/innerHeight`, which count the scroll bars (a window at the bottom edge ended under the page's horizontal bar).
- **A scroll bar that comes later** (the page grows wider, no "resize"): an invisible box fixed to the room (`#dci-room`, `position: fixed; inset: 0`) is watched by a ResizeObserver; when the room changes, the windows are moved into view (`clampWindow`).
- **CSS:** `.dci-panel` `max-width` / `max-height` 100 % (of the room) instead of 100vw / 100vh.
- **Tests:** `t_ui_view.py` new case `footbar` (a browser of its own with classic scroll bars; fails on 3.41.9).

## Import 3.41.9 · 2026-11-03

Block BF, part 3 – collected item Z-EN (Q-cp): the edit note is set in ⚙ Settings only.

- **`S.editNoteMode`** ('full' | 'simple' | 'none', `EDIT_NOTE_KEY` 'dci-edit-note', only "simple" and "none" stored; in `TOPIC_KEYS.staging`, its reset and "reset all") replaces `S.editNote` (a session switch of the footer).
- **⚙ Settings → Staging:** a segment "Edit note: Full | Simple | None" (`data-act=edit-note-mode`); the tooltip of each option lists the lines it writes (`settings.editNote.*Title`).
- **The footer:** the checkbox "edit note" (`data-f=editnote`) and its handler are gone; `footer.editNote`, `footer.editNoteShort` removed (all languages), `footer.optionsTitle` without "Edit note".
- **`editNoteBlock`:** "simple" ends after "Source", "Also from" and "Script". **Staging:** "none" writes nothing and takes the block written before out again (**`clearEditNote`**, new); the job of live comments gets the block unless "none".
- **`formEditNote(sources, prefilled)`** (new): the edit note of the forms of artists, labels, places, series, works and suites – "full" as before, "simple" "Source: …" and "Script: … v…", "none" none (the parameter left out).
- **`roleCreditHint`:** "goes into the edit note only" only with "full".
- **Tests:** `t_ui_settings.py` new case `editnote` (fails on 3.41.8); `t_ui_view.py` `foot` (two checkboxes, "fill role credits" toggled), `t_works_matrix.py` `wattrs` (no checkbox to tick).

## Import 3.41.8 · 2026-11-03

Block BF, part 2 – collected item Q-cn ("Host: Cheryl Waters").

- **Mapping file:** new rule **R108** `^(host|hosts|hosted by)$` (no type, `askType`; before R012, which no longer has "host" and "hosted by") and question **Q012** (`typeAsk.askHost`): spoken vocals credited "host" (`instrument`, `credit: "host"`), miscellaneous support (`task: "host"`), skip the role (`level: "skip"`).
- **`roleRules`:** R108 as R097 (no type, the note `askType`).
- **`pickType`:** an answer with the level "skip" puts the row on "Skip" (its type kept, `levelTouched`), logged as the others.
- **Texts (English):** `typeAsk.askHost`.
- **Tests:** `t_text_basics.py` new case `hostask` (fails on 3.41.7); `register_golden.json` renewed (R012, R108, Q012).

## Import 3.41.7 · 2026-11-03

Block BF, part 1 – collected items Z-AM, Z-CAM, Q-co, Z-LG (the credits of a YouTube video description).

- **The text adapter, `shareTail(parts)`** (new, used by `listRoles`): the last word of a role of a list is given to each part before it that is no role by itself while the joined words are one ("Audio & Mixing Engineer" → "Audio Engineer", "Mixing Engineer"; "Mixed & Mastered By" → "Mixed By", "Mastered By").
- **Mapping file, R095:** also "camera", "cameras", "camera crew", "camera operators" (miscellaneous support, the role as task); "cinematographer" and "editor" were there already.
- **Languages file:** `settings.entries.legacy` is "Legacy" in de, es, fr (was Klassisch, Clásica, Classique), and so in `ms.3.35.0`.
- **Tests:** `t_text_basics.py` new case `ytroles` (fails on 3.41.6); `t_static.py` new case `legacy` (fails on 3.41.6); `register_golden.json` renewed (R095).

## Import 3.41.6 · 2026-11-03

Collected item Z-SUW (user report): MusicBrainz's relationship editor does not create a new work that is linked by "parts" only – "Enter edit" ended with "An error occurred: unknown Work id:". The suite is created in MusicBrainz first.

- **`startSuiteCreate(sw)`** (new): MusicBrainz's form for a new work in the dashboard (`openCreateDialog`, as `startWorkCreate`), prefilled by `buildWorkSeed` with the suite's name, the type "Suite" (`S.workOptions.types`, else 6), no language and **`suiteWriters(sw)`** (new: the writers – `WRITER_TYPES` – credited for every track of the suite); its edit note as for a work. Created: the suite's entry in `S.suiteWorks` takes the MBID (`origin 'created'`), a message, the log (`suiteCreated`).
- **`searchSuite(sw)`** (new, called by `acceptSuite`): the suite looked up among the works of its writers (`searchWorks`); one work of exactly its name (or alias) is offered (`sw.offer`), not taken by itself.
- **`suiteAskHtml`:** the line of an accepted suite has **"＋ Create the suite in MusicBrainz …"** (`data-act=suite-create`), the offer **"Link “…”"** (`suite-pick`) and "Its “parts” wait …" while the suite is pending; then a link "Suite in MusicBrainz: …" (`a.dci-suite-mb`). The click handler of the suite's buttons knows `suite-create` and `suite-pick`.
- **`computePlan`:** no `suite-part` item while the suite's gid is pending (the parts and their links with the recordings as before). **The stage loop:** the suite always with `fetchJsEntity`. **`pendingWorkEntity`:** the branch of a pending suite ("pending:s1") is gone.
- **Texts (English):** `suite.createBtn`, `suite.createBtnTitle`, `suite.wait`, `suite.pickTitle`, `suite.inMb`, `suite.createTitle`, `suite.createNoWriters`, `suite.createAfter`, `suite.created`, `log.suiteFound`, `log.suiteForm`, `log.suiteCreated`, `log.suitePicked`.
- **Tests:** `smoke/harness.py` `WORK_TITLES` (the title `/ws/2/work/<gid>` answers for a work a test knows). `t_works_more.py` `suiteparts` anew (no "parts" before the suite exists; the form: name, type 6, Writer W – not Writer Z; created: the link, the message; staged: "parts" from the work of MusicBrainz), `suiterestage` (created, staged; undone and accepted again: "Link “Trisect”" offered and taken; every "parts" from that work), `suiteask` (the line with the button); all three fail on 3.41.5.

## Import 3.41.5 · 2026-11-03

Block BE, translation round F-6: every text added in English since Block AL in German, Spanish and French.

- **`mb-vibecode-credits-importer-languages.json`:** 762 texts more in each of de, es, fr (1688 → 2450; 100 % of the script's English texts): the blocks AL – BD (notes credits, the release page line, the compact entries, Skip, Repeat import, statistics and cache, text from cover art, suites and medleys …). Written with `tools/i18n_add.py` (anchor `title`), the terms of the file kept (vormerken / Beziehung / Eintrag …; labels of MusicBrainz's own pages such as "Enter edit" stay English); the feature "Text from cover art" named alike everywhere (Text aus Cover-Art · Texto del arte de portada · Texte des illustrations). French with a no-break space before : ; ? ! and inside « ».
- **The script:** no change but its version.
- **Tests:** `t_static.py` new case `round6` (a sample of each block in de, es, fr – not the English, symbols kept, French spacing); fails on 3.41.4.

## Import 3.41.4 · 2026-11-03

Fixes after the check of Block BD (an independent review; collected item Z-SU).

- **Keys of parts:** "pending:<track>.<k>.<n>" – each acceptance, split and renaming of a staged part its own (`S.suiteSeq`); `pendingWorkEntity` reads the track from any such key. Until 3.41.3 a part staged, undone and accepted again kept the old link and its entity, and the suite's "parts" pointed to a second new work. **`renameSuiteParts`** (from `setSuiteNaming` and `resetSettings`): a part already in the editor gets a new key instead of a name changed in the editor's entity.
- **`suite-part`:** planned only with the part's own link (planned, staged or in MusicBrainz) – a link held back by an invalid date holds it back too; staged only while the recording's medium is loaded (as the links).
- **`acceptSuite`:** a work of MusicBrainz chosen or created for a track is its part (`kept`), no new work instead of it.
- **`suiteAsks`:** the key from the offer before the tracks are filtered (a medium filter does not ask again); offers whose tracks all have works in MusicBrainz are not asked; answered ones stay; a suite of another source of the release keeps its line with "↺".
- **`suiteOffers`:** the release's title only when at least half of the tracks have parts; of two headings before the same track the one next to the tracks. **`headingKind`:** "bonus" anywhere. **T061** + DVD, Blu-ray, SACD, Digital, Remixes (register renewed).
- **`searchParts`:** offers the work found (`p.offer`; button `part-pick` "Link “…”" with its MB link at the part) instead of taking it – as every work found for a track (180), and no plan changes while staging.
- **`allWorkGids`** with the parts; the summary's count of work relationships without `suite-part`; the focus after "Suite: Part | Suite, Part"; the hint of the question visible in it.
- **Texts (English):** `suite.partPick`, `suite.partPickTitle`, `log.partPicked`; `log.partsFound` changed ("MusicBrainz has works for {n} of its parts – offered at them").
- **Tests:** `t_works_more.py` new case `suiterestage` (undone and accepted again, named anew after staging: one link per part, no "parts" to a work without its recording); `medley` (no suite asked for one "A / B" among four; the work found offered, then linked); `suitedata` D (bonus anywhere, DVD, the release's title only from half the tracks, two headings before one track). They fail on 3.41.3.

## Import 3.41.3 · 2026-11-03

Medleys, and the parts looked up in MusicBrainz (collected item Z-SU; Q-cb, Q-cd, Q-cg).

- **New `medleyParts(i)`** (the parts of a track without a work in MusicBrainz), **`splitMedley(i)`** (each part a part plan with the flag "medley" and `medley: true`, a work planned before kept in `before`), **`joinMedley(i)`**. Handlers `medley-split`, `medley-join`.
- **`workFrontCell`:** "Split into n works (medley)" (`.dci-mx-split`) in the line of a track without a work and next to one new work, when its title has parts; a part of a medley "medley k of n", the first with "↺ one work". The flag "medley" goes onto the link through `linkAttrsOf` (the plan's flags), the order through `linkOrder` (3.41.1).
- **New `searchParts(i)`:** each new part looked up with `searchWorks` among the works of the track's writers (`writerMbidsOfTrack`) – for a part of a suite also "Suite: Part", "Suite, Part" and the part alone; one work of exactly that title or alias: taken (`origin: 'search'`). After `acceptSuite` and `splitMedley`.
- **Texts (English):** `medley.split`, `medley.splitTitle`, `medley.join`, `medley.joinTitle`, `medley.partOf`, `medley.partTitle`, `log.medleySplit`, `log.medleyJoined`, `log.partsFound`.
- **Tests:** `t_works_more.py` new case `medley` (✕ No, the offer; split – a part found in MusicBrainz; staged with "medley" in the order of the title; one work again); fails on 3.41.2.

## Import 3.41.2 · 2026-11-03

The suite itself: a new work of the type "Suite" with "parts" to its parts, in their order (collected item Z-SU; Q-bv).

- **State:** `S.suiteWorks` (key of the suite → { gid "pending:s<n>", title, key, tracks }), `S.suiteSeq`; `acceptSuite` adds it, `undoSuite` and `dropWorkChoices` take it away.
- **`idx().partsLt`** (work – work "parts"). **The plan:** after the links of the works, an item `suite-part` per part (key `suite|<suite>|<part>`): the parts planned of the suite's tracks and the one work in MusicBrainz of a track of the suite, in their order (`linkOrder` 1 … n), with "movement" where the type allows it; target `{ kind: 'work', work }`.
- **Staging:** `suite-part` dispatched from the part (in the editor with its recording) to the suite (`enteredFirst`: the suite is entity0), with its `linkOrder`. **`pendingWorkEntity`** also for "pending:s<n>": the type "Suite" (from the work form's types), no language. `describeItem`, the preview ("part n of the suite “…”") know the kind.
- **Texts (English):** `preview.suitePart`.
- **Tests:** `t_works_more.py` new case `suiteparts` (the suite with "parts" to 7 parts in their order, type Suite, movement, entity0, no recording with it; the preview; nothing after ↺); the harness types "parts" (281), "movement", the work type "Suite" there only. Fails on 3.41.1.

## Import 3.41.1 · 2026-11-03

The question of a suite and its parts as works of their own (collected item Z-SU; Q-bt, Q-bu, Q-bv, Q-cc, Q-ci).

- **State:** `S.workParts` (track → [part plan { gid "pending:<track>.<k>", title, part, k, origin, flags, suite, suiteName, before }]), `S.suiteAnswers` (key → { yes, name }).
- **`worksForTrack`:** the parts of a track instead of its one planned work. New **`planOf(i, gid)`** (the plan of a planned work: a part or the one work) – used by `linkAttrsOf`, `setLinkAttr`, the "cover" pill, `coverCandidates`, `coverAutoNow`, `workFrontCell`; new **`planEntries()`** (every planned work) for the links staged.
- **New `suiteAsks()`** (the suites offered for the tracks of the matrix, each with a key), **`suitePartName`**, **`setSuiteNaming`**, **`acceptSuite(o, name)`** (each track without a work in MusicBrainz: its parts – `trackPartsOf` of the source track, else the track – as new works; a work planned before kept in `before`), **`undoSuite(o)`**, **`suiteAskHtml(o)`** (the yellow question at the top of the matrix, `[data-el=suites]`; answered: a line with "↺"). Handlers `suite-yes`, `suite-yes-name`, `suite-no`, `suite-undo`, `suite-naming`.
- **`workFrontCell`:** a part: "part k of n" (from two parts), its name; the track's head only on its first line. `matrixRows` passes `k`; `matrixTrack` counts tracks with parts.
- **Staging:** the link of each part with `linkOrder` k (from two parts of a track); **`dispatchAddRelationship(…, linkOrder)`** (until 3.41.0 always 0); **`pendingWorkEntity(ref)`** by the work's key ("pending:4", "pending:4.2"), a part without a work type.
- **Setting:** `SUITE_NAMING_KEY = 'dci-suite-naming'` (only "comma" stored), ⚙ Works, in `TOPIC_KEYS.works`, `SETTINGS_KEYS`, its ↺, `resetSettings`. `dropWorkChoices` ("Start afresh") clears the parts and answers too.
- CSS `.dci-mx-suite` (yellow), `.dci-mx-part`.
- **Texts (English):** `suite.ask`, `suite.yes`, `suite.noBtn`, `suite.other`, `suite.yesName`, `suite.hint`, `suite.from.heading/index/release`, `suite.done`, `suite.undo`, `suite.undoTitle`, `suite.no`, `suite.askAgain`, `suite.askAgainTitle`, `suite.partOf`, `suite.partTitle`, `log.suiteYes`, `log.suiteUndone`, `log.suiteNo`, `log.suiteNaming`, `settings.suiteNaming`, `settings.suiteNaming.colon/comma`, `settings.suiteNamingTitle`.
- **Tests:** `t_works_more.py` new case `suiteask` (the question; ✓ Yes – the parts in the matrix; staged in their order without a type; ⚙ "Suite, Part" and its ↺; undo, ✕ No, another name); fails on 3.41.0.

## Import 3.41.0 · 2026-11-03

Block BD, suites and medleys (collected item Z-SU) – first what they are made of (Q-bt, Q-ca, Q-ch).

- **The neutral release:** `headings` ([{ title, at }], the headings of the track list, `at` the track that follows); a track's `parts` (the titles of its sub-tracks) and `indexTitle`.
- **DISCOGS `toRelease`:** keeps the headings (until 3.40.17 `continue`), and for an index of the parts of one track the titles of its sub-tracks as `parts`.
- **New `titleParts(title)`** (" / " with spaces), **`trackPartsOf(t)`**, **`headingKind(title)`** ("medium" by T061, "recording" by `HEADING_RECORDING`, "name"), **`suiteOffers(rel)`** ([{ name, from: heading | index | release, tracks }]); exported for Node.
- **Mapping:** list `SUITE_SKIP_HEADINGS` (T061, ✎ as words): Side, CD, Disc, Disk, LP, Record, Vinyl, Tape, Cassette, Medium, Bonus, Bonus Tracks, Bonus Track, Bonus Disc, Bonus CD, Hidden Track, Volume, Vol., Encore, Extras; its register entry; `register_golden.json` renewed.
- **Tests:** `t_works_more.py` new case `suitedata` (Node: headings and parts from Discogs, the kinds of headings, the suites offered); fails on 3.40.17. `t_rules_window.py` `ruleedit`: T061 among the lists with ✎.

## Import 3.40.17 · 2026-11-03

"cover" set by itself for a composer with only writing credits (collected item Z-CV; Q-by).

- **DISCOGS `toRelease`:** `genres` (Discogs's genres in lower case); the neutral release names the field (none: [] or left out).
- **`coverComposers`** split: **`coverCandidates(i, work)`** (the composer of a work chosen among his works who performs nothing on the track – without the check whether "cover" is set) and `coverComposers` (only while "cover" is not set). **New `coverAuto(i, work)`:** a planned link to a work of MusicBrainz with such a composer, the composer an entry of the source (not added by hand) whose rows of the source are all `WRITER_TYPES`, the release not of the genre "classical".
- **`linkAttrsOf`:** "cover" in the set while `coverAuto` and not taken off (`S.linkAttrOff`) – so the link is staged with it. **`linkAttrsHtml`:** such a "cover" (not set by hand) as the new pill state `auto` (`.dci-wpill-auto`, yellow, ticked) with `matrix.coverAuto`; a click takes it off as any attribute ("co?" again).
- **Texts (English):** `matrix.coverAuto`.
- **Tests:** `t_works_more.py` `coverworks` B (set by itself, staged with "cover" 567, a click: "co?", another: on), D (where it was "co?": set by itself), new E (classical; Monk with a credit Liner Notes: "co?" only); the work of Monk known to `/ws/js/entity` (harness `COMPANIES`). Fails on 3.40.16.

**After the check of Block BC (an independent review):**

- **Entry skip and the other kinds of "Skip"** (Z-SK): `setScope`, `setWorksRowsSkipped(false)`, `setAboutRowsHidden(false)`, `setNotesRowsHidden(false)` and "mx-col-restore" put the level that comes back into `entrySkip` (new `entrySkipLevel`) instead of onto a row skipped with its entry – "all relationships" brought such rows back. **`unskipEntry`** places the level by what holds now (a credit switched off, text or notes left out, the works matrix skipped, the scope; a level skipped then by the scope or the works matrix: the level before those). New **`dropStaleEntrySkip`** (in `renderGroups`, `refresh`): a row put on a level another way (`bulk-level` …) loses `entrySkip`. **`rowFieldsOf`:** a row skipped with its entry is remembered on "Skip".
- **Repeat import** (Z-RI): the snapshot or "afresh" goes with its import – `loadRelease(…, { repeat })` → `finishRemember(seq, repeat)` (until now `S.repeatSnap`/`S.repeatFresh`, which an import started meanwhile could take); "afresh" also drops the choices of the works matrix (new `dropWorkChoices`, after the source was read; the works created through the dashboard stay); the focus back on "↻ Repeat import"; "Delete stored import …" closes its question, an import and `forgetImport` too.
- **`coverAuto`** worked out once per drawing (`coverMemo`, `S.coverPass` counted up in `refresh`, `renderWorks` and with each answer of `bandLinks`).
- **`resetSettings`:** `skipHide`, `poolsFoldApply` back. **`openSettingsAt`:** `onlyHint('settings')` and the number of works kept, as ⚙ of the head. **`renderLiveComments`:** the box focused keeps the focus when the list is drawn anew.
- **Tests:** `t_ui_view.py` new case `entryskipmodes` (scope and entry skip both ways; all rows on a level and back on "Skip"); `t_sources.py` `repeat` (a new work kept or dropped; one question at a time). Both fail before these fixes.

## Import 3.40.16 · 2026-11-03

"↻ Repeat import" in the head (collected item Z-RI; Q-bw).

- **`renderSource`:** `button.dci-repeat-btn[data-act=repeat-open]` after "Source ▾" (with a release); its question `repeatAskHtml()` (`[data-el=repeat]`, radios `data-f=repeat-keep` "keep" preselected / "fresh", `repeat-do`, `repeat-cancel`) first among the panels below the head. The choice is kept in `S.repeatKeep` while the head is drawn anew (change handler `repeat-keep`), "keep" again for the next question.
- **New `repeatImport(keep)`:** `S.repeatSnap = rememberSnapshot()` (keep) or `S.repeatFresh` (afresh), `entityCache.clear()` (the entities of MusicBrainz fetched anew), `loadRelease(S.release.id, { source: S.source, confirmed: true })`; both cleared afterwards.
- **`finishRemember`:** takes `S.repeatSnap` (also with ⚙ Settings → Cache off) or, with `S.repeatFresh`, nothing remembered; **`restoreRemembered(snapIn)`** takes a snapshot given to it instead of the stored one.
- CSS `.dci-repeat-btn`, `.dci-repeat-opts`.
- **Texts (English):** `repeat.button`, `repeat.title`, `repeat.ask`, `repeat.what`, `repeat.keep`, `repeat.keepTitle`, `repeat.fresh`, `repeat.freshTitle`, `repeat.do`, `log.repeatKeep`, `log.repeatFresh`.
- **Tests:** `t_sources.py` new case `repeat` (the button after "Source ▾", the question, Cancel; kept: the source read again with a new credit, the changes kept, "Dates & tracks" open again after a fold by "Apply" – Z-PF2 within the page; afresh: the changes gone, the choice kept while the head is drawn anew); fails on 3.40.15.

## Import 3.40.15 · 2026-11-03

"⊘ Skip" for a whole entry, and a setting to take skipped entries out of the dashboard (collected item Z-SK; Q-bx, Q-ce).

- **New `entrySkipped(a)`, `entrySkipHtml(a, rows)`, `skipEntry(a)`, `unskipEntry(a)`, `afterEntrySkip(a)`, `renderSkippedList(list)`:** "⊘ Skip" (`data-act=entry-skip`, `data-skipkey`) puts every row of the entry (`artistKey`) on "Skip" through `levelOf` and keeps on it `entrySkip = { level, touched, mx, scope }`; "↺ Take again" (`entry-unskip`) restores the level, `levelTouched`, `mxSkipped`, `scopeLevel`. Skipped while every row is on "Skip" and one has `entrySkip`. **`levelOf`** deletes `entrySkip` (a level chosen ends it for that row). `entrySkip` is a field of the row, so "Remember per release" keeps it.
- **`groupHtml`:** `.dci-ghead-r` in every entry (until 3.40.14 only compact, with "by event | by role"), the button in it; the class `dci-gskipped`. **`refresh`** toggles the class and swaps the button when the state changed (a level chosen for a row). **`updateGroupHeader`** keeps `dci-gcompact`, `dci-about-hidden`, `dci-gskipped` (it dropped them before).
- **`renderGroups`:** with `S.skipHide` the skipped entries are left out and listed in the new `[data-el=skipped]` (below "Other entries"): "n skipped entries ▸" (`skipped-toggle`, `S.skippedOpen`), each with `entry-unskip`.
- **Setting:** `SKIP_HIDE_KEY = 'dci-skip-hide'` (only on stored), ⚙ Appearance `data-set=skip-hide`, in `TOPIC_KEYS.appearance`, `SETTINGS_KEYS`, its ↺.
- CSS `.dci-ghead-r` inline-flex with a gap; `.dci-gskip`, `.dci-gskip-back`, `.dci-gskipped`, `.dci-skipped`, `.dci-skipped-list`.
- **Texts (English):** `group.skip`, `group.skipTitle`, `group.unskip`, `group.unskipTitle`, `group.skippedN.one/other`, `group.skippedTitle`, `log.entrySkipped.one/other`, `log.entryTaken.one/other`, `settings.skipHide`, `settings.skipHideTitle`.
- **Tests:** `t_ui_view.py` new cases `entryskip` (the button in every head; skipped and back; a level chosen by hand before kept; a level chosen while skipped ends it; the setting and the line at the bottom; matrix, compact) and `entryskipkeep` (remembered); both fail on 3.40.14.

## Import 3.40.14 · 2026-11-03

"Collect statistics" in ⚙ Settings → Cache, Log | Statistics · ⚙ next to "Import credits …" (collected items Z-SC, Z-LS; Q-bz).

- **`statsHtml`:** no box any more; at the top `p.dci-sub.dci-stats-where[data-el=stats-where]` (`stats.whereOn` / `stats.whereOff`) with `button[data-act=stats-where]` (`stats.whereBtn`). The handler **`stats-where`** calls the new **`openSettingsAt(topic, focusSel)`** (⚙ Settings open at a topic, stored as a click on its tab, the statistics and the docked rules closed, the focus on `focusSel` or the tab).
- **⚙ Settings → Cache:** the box `data-set=stats-on` (handler `settingsChange` unchanged). **`TOPIC_KEYS`:** `STATS_ON_KEY` from `statistics` to `cache` (its ↺).
- **`insertLauncher`:** `span.dci-launch-tools` – `#dci-log-open` (now `.dci-launch-ico` with `ico('log')`, `aria-pressed`), `.dci-launch-sep`, `#dci-stats-open` (`ico('stats')`), `#dci-set-open` (`ico('gear')`); **`renderLauncher`** sets their `aria-label` and `title` (`log.title`; `stats.title`, `stats.buttonTitle`; `settings.title`, `settings.buttonTitle`) and calls `syncLogBtn`. **`syncLogBtn`** also presses `#dci-log-open` (before the check for the dashboard).
- **`openFromBar(what)`:** `openDashboard({ settingsOnly: true, only: what })` when it is closed, then the statistics (read anew, ⚙ and the docked rules closed, the focus on their heading) or `openSettingsAt` at the remembered tab. **`openDashboard`:** with `only: 'stats'` the message `statsOnly.hint`; one of the two messages at most. **`onlyHint(what)`** (before the import): the message names what is open – also from `stats-open` and `settings-open` of the head.
- CSS `#dci-launcher .dci-launch-tools`, `.dci-launch-ico`, `.dci-launch-sep`.
- **Texts (English):** `stats.whereOn`, `stats.whereOff`, `stats.whereBtn`, `statsOnly.hint`.
- **Tests:** `t_ui_settings.py` new case `statswhere`; `stats` A/E and `statsbutton` B with the box in ⚙ → Cache; `t_ui_head.py` new case `launchtools` (without the companion: the three symbols; Log pressed; Statistics and ⚙ without the import, the message; "Start import"). Both new cases fail on 3.40.13.

## Import 3.40.13 · 2026-11-03

The fold after "Apply" for one import only, "＋ Another role" a button in the full view, one box for all live comments (collected items Z-PF2, Z-AB, Z-LC; Q-br, Q-bs).

- **`foldPoolsAfterApply`:** sets `S.poolsFoldApply` instead of `S.poolsOpen = false` and no longer writes `dci-pools-open`; **`poolsOpen`** false while it is set (after the forms and the waiting suggestions); **`loadRelease`** clears it (a new import with dates shows "Dates & tracks" open again), **`pools-toggle`** too ("▲ fold" / "▼ show" by hand is remembered as before).
- **`groupHtml`:** in the full view `button.dci-addrole-btn.dci-addrole-full` with `group.addRoleBtn` ("＋ Another role for {name}") instead of the text button with `group.addRole` (still the tooltip of "＋ role").
- **`renderLiveComments`:** a `thead` row `tr.dci-livecom-all` with a box `data-f=livecom-on data-all=1 data-recs=…` for all proposals that can be ticked (not those with another comment in MusicBrainz), from two of them; ticked when all are, `indeterminate` (set after `innerHTML`, `data-mixed`) when some are. The handler `livecom-on` unchanged (it takes `data-recs`). CSS `.dci-livecom-all td`.
- **Texts (English):** `livecom.all`, `livecom.allAria`.
- **Tests:** `t_dates_matrix.py` `foldapply` B nothing stored, new G (folded by "Apply", loaded again: open; "▲ fold" by hand, loaded again: folded); `t_ui_view.py` new case `addrolebtn`; `t_works_more.py` new case `liveall` (all ticked, mixed, all on and off), `livecom` "All" without the track MusicBrainz has another comment for. Each fails on 3.40.12.

## Import 3.40.12 · 2026-11-03

The notes of "Assist" (Discogs 3749161): a place instead of the area of its city, and the dates of areas (collected item Z-AP).

- **`DATE_GROUPS`:** `recorded in` in Performance, `mixed in` in Mix, `mastered in` in Mastering and Remastering (its `only` also for `mastered in`) – the date of a row of an area ("Recorded In – Hiroshima") was in no column, "Apply" left it out.
- **`TEXT.parse`:** context `placeNames` (the names of places the source lists itself); `placeIn`'s `isPlace` also true for such a name – "in Tokyo, Shinjuku Pit Inn" is that place in Tokyo, not the area "Tokyo (Shinjuku Pit Inn)". **`addNotesCompanies`** passes the release's companies with a role "… At".
- **Mapping:** T051 `TEXT_PLACE_WORDS` + `cent(?:er|re)`, `kaikan`; its register note.
- **Tests:** `t_notes_dates.py` new case `assistnotes` (A the area Hiroshima, the places Meguro Fukushi Center and Zojoji Hall, no area Tokyo; B "Apply": each row its date, the area too; C a place Discogs lists without a word of places; fails on 3.40.11); `harness.py` the type `recorded in` (area – recording, as on MusicBrainz); `register_golden.json` renewed (T051).

## Import 3.40.11 · 2026-11-03

⚙ Settings → Appearance "Compact entries: notes beside the lines | in the lines" – B, lower still (collected item Z-KH, mockup B; Q-bi, Q-bo, Q-bp, Q-bg).

- **State and storage:** `S.emSide` (`EM_SIDE_KEY` `dci-em-side`, `beside` by default, only `lines` stored); in `TOPIC_KEYS.appearance`, `SETTINGS_KEYS`, `resetTopic('appearance')` (the entries drawn anew) and `resetSettings`.
- **Settings:** the toggle `data-act="em-side"` after "Entries: Matrix | Legacy" (`settings.emSide`, `settings.emSide.beside`, `settings.emSide.lines` and their titles); handler `em-side`: stored, logged (`emSideSet`), `renderGroups`, `renderSettings`, `refresh`.
- **`groupHtml`:** `inLines` (compact and `S.emSide === 'lines'`): "✎ works ↓" (`button.dci-works-goto[data-act=works-goto]`, `group.worksGoto`, its title `group.workNote`) after the match in the head instead of the note; `entryCompactHtml(a, rows, notes, inLines)`.
- **`entryCompactHtml`:** `withTail` puts **new `emTailHtml(a)`** – the count (`data-emcount` with `data-emshort`: `em.countShort` "n to stage") and `button.dci-addrole-btn.dci-addrole-short[data-act=add-role]` ("＋ role", title and label `group.addRole`) – at the end of the last line (by event: of the events, not of "Taken out"; by role: the last role line; no line: a line of its own); no `.dci-em-side`; other notes (rows skipped with the works matrix) below the lines.
- **`refresh`:** `data-emshort` → `em.countShort`. **`matchHtml`:** a linked entry compact "in the lines": `match.linkedShort` ("✓ link"), the whole text as its title.
- **Handler `works-goto`:** the works matrix (`[data-el=works]`) in view (below what stays in view), `dci-flash` for 2.5 s.
- **CSS:** `.dci-em-tail`, `.dci-em-inlines .dci-work-note`, `.dci-works-goto`.
- **Texts (English):** `settings.emSide`, `settings.emSide.beside`, `settings.emSide.besideTitle`, `settings.emSide.lines`, `settings.emSide.linesTitle`, `group.addRoleShort`, `group.worksGoto`, `em.countShort`, `match.linkedShort`, `log.emSideSet`.
- **Tests:** `t_entries.py` new case `compactlines` (A the setting, beside by default; B in the lines: no column, the tail of the last line, "✓ link" and "✎ works ↓" with their tooltips; C by role; D "✎ works ↓" brings the works matrix into view; E "＋ role"; F full view as before; G ↺ of Appearance). README: the settings table names "Fold bar after Apply" (3.40.9) and "Compact entries".

**After the review of block BB** (an independent agent; fixed here):

- **"Fold bar after Apply" (3.40.9):** `dmChanged` sets `S.dmFoldWait` only for a change made in the bar (`:hover` or the focus in `[data-el="dates"]` – not from ⚙ Settings → Dates or the source menu, which folded an open bar at the next focus anywhere); `watchPoolsLeave` folds only while "apply automatically" is on and nothing waits for "Apply" (`dm().dirty`), else it drops the wait; the `dm-auto` handler (off) and `pools-toggle` drop it too (a change, "apply automatically" off and another change: the bar folded over the change not applied yet; "▲ fold" by hand and opened again: it folded at the next leave). `foldPoolsAfterApply` also not while cells wait for a choice (`c.alt`) or one is being edited (`S.dmEdit`). Only "off" stored (`el.checked ? null : false`).
- **`withTail` (3.40.11):** a function as replacement – "Joey Bada$$" kept its "$$" (`$$`, `$&` of a replacement string).
- **`sourceElOf`:** not the toggle (`.dci-ghead-r`) nor "✎ works ↓" (`.dci-works-goto`) in the head – a click there no longer makes the source tab jump to the entry.
- **`works-goto`:** a folded works matrix unfolds first (`S.worksFolded`).
- **CSS:** `.dci-em-cl:has(.dci-em-tail) .dci-status` without `margin-left: auto` (a status and the tail both pushed right: the status stood in the middle of the line).
- **Tests:** `t_dates_matrix.py` `foldapply` F (the bar left without a change; "apply automatically" off with a change waiting; a change from ⚙ Settings; stored only when off); `t_entries.py` `compactside` D (an entry folded in the full view: the column and the toggle), `compactlines` H ("Joey Bada$$", a line "Taken out" without the tail).

## Import 3.40.10 · 2026-11-03

A compact entry lower: "by event | by role" in its head, its notes and "＋ Another role" beside its lines (collected item Z-KH, mockup C; Q-bi, Q-bk, Q-bf).

- **New `emBySegHtml(a)`** (the toggle, until now inside `entryCompactHtml` in `.dci-em-chead`) and **`emSideHtml(a, notes)`**: `.dci-em-side` – the count `data-emcount` (filled by `refresh` as before), the notes, `button.dci-addrole-btn[data-act=add-role]` (`group.addRoleBtn`).
- **`entryCompactHtml(a, all, notes)`:** no `.dci-em-chead` and no `.dci-em-foot`; the lines in `.dci-em-cwrap` beside `emSideHtml`.
- **`groupHtml`:** `compact` (`mxCompact` and not `mxEntry`): the toggle in `.dci-ghead-r` at the right of the head; `notes` (the work note – compact: `group.workNoteShort`, its tooltip `group.workNote` – and `group.mxHidden`) go into the column; the link "+ Another role" below only outside the compact view (the full matrix and the rows as before).
- **CSS:** `.dci-ghead-r`, `.dci-em-cwrap` (wraps: the column below the lines in a narrow dashboard), `.dci-em-side`, `.dci-addrole-btn`.
- **Texts (English):** `group.addRoleBtn`, `group.workNoteShort`.
- **Tests:** `t_entries.py` new case `compactside` (A the toggle in the head, the column beside the lines with count, note and its tooltip, the button, no link below; B by role the same; C the button: the full matrix with a new line; D full view: as before).

## Import 3.40.9 · 2026-11-03

"Fold bar after Apply" next to "apply automatically" (collected item Z-PF; Q-bl, Q-bn).

- **State and storage:** `S.dmFold` (`DM_FOLD_KEY` `dci-dm-fold`, default on – stored `false` when off; defined before its first read), `S.dmFoldWait`; in `TOPIC_KEYS.dates`, `SETTINGS_KEYS`, `resetTopic('dates')` and `resetSettings`.
- **`matrixHtml`:** the box `data-f="dm-fold"` after "apply automatically"; ⚙ Settings → Dates and tracks the same box. Change handler `dm-fold`: stored, logged (`dmFoldSwitch`), the bar drawn anew when switched in ⚙.
- **New `foldPoolsAfterApply(focus)`:** folds "Dates & tracks" as `pools-toggle` does (`S.poolsOpen` false, stored; `S.poolsForce` null; log `poolsFolded`); not while a form of the pools is open (`poolForm`, `trackForm`, `poolClear`); with `focus` the focus onto "▼ show". Called by `dm-apply`.
- **`dmChanged`:** with "apply automatically" `S.dmFoldWait` after `applyMatrix`. **New `watchPoolsLeave(el, overlay)`** (in `buildOverlay`, on `[data-el="dates"]`): `mouseleave`, `focusout` to outside the bar, and a `focusin` outside it (the bar is drawn anew after each change, so the focus may have gone with the field) fold while `dmFoldWait`.
- **Texts (English):** `dm.fold`, `dm.foldTitle`, `log.dmFoldSwitch`, `log.poolsFolded`; `reset.what` names the box (English only until the translation round).
- **Tests:** `t_dates_matrix.py` new case `foldapply` (A box below the matrix and in ⚙, on; B "Apply" folds, focus, log; C off: stays open; D with "apply automatically": open while the pointer is in the bar, folded when it leaves; by keyboard, a field outside focused: folded; E ↺ of the topic: on again). `harness.py` `DM_FOLD` (False: `dci-dm-fold` stored off before the script starts – the cases written before work on in the open bar after "Apply"; `foldapply` sets True).

## Companion 1.10.1 · 2026-11-03

Marks at "Copyright ©" and "Phonographic Copyright ℗" on Discogs, and the jump to their line (collected item Z-CR).

- **New `roleNorm(s)`:** `norm` with © → (c), ℗ → (p), ™ → (tm) – Discogs's data write "Copyright (c)", "Phonographic Copyright (p)", its page the signs. Used wherever a role is looked for in a line: `lineOf`, `findCreditAt`, `findCredit` (role and full role), `locate` (until 1.10.0 `norm`: the role "(p)" was not in "Phonographic Copyright ℗ – …", `findCredit` scored below 3 – no mark; `locate` highlighted only the name).
- **Version:** `@version` and `COMPANION_VERSION` 1.10.1 (the main script still needs 1.10.0: `COMPANION_NEEDED` unchanged).
- **Tests:** `harness.py` `discogs_page` writes "Phonographic Copyright ℗" as the real page (the data stay "(p)"); `t_companion_discogs.py` new case `copymarks` (Sony with ℗ and ©: a mark on each line; a click on the row "Copyright (c)": its line highlighted; fails with 1.10.0). `t_release`'s comparison log keeps "● Sony" / "✓ Sony" – with 1.10.0 and the new page Sony would have no mark.

## Import 3.40.8 · 2026-11-03

Room for a scroll bar drawn over the content (collected item Z-SB): an overlay scroll bar (macOS, Windows 11) covered the last line of a table that scrolls sideways – "written “Recorded By”" below the role field of the matrix.

- **New `barRoomNeeded(el)`:** whether a box needs `.dci-barroom` – it scrolls sideways (`overflow-x` `auto` / `scroll`), its content is wider than it (`scrollWidth > clientWidth + 1`) and its bar takes no room (`offsetHeight − clientHeight − borders < 1`); a classic bar takes room of its own – nothing changes there.
- **New `watchBarRoom(root)`:** a `ResizeObserver` on each box that scrolls sideways (`.dci-em-scroll`, `.dci-tablewrap`, `.dci-dm-grid`) and on its first child (its content) – each box once, all read before any is changed –, a `MutationObserver` on `root` for the boxes drawn later; a box no longer in the page is no longer observed. Called once in `buildOverlay`.
- **CSS:** `.dci-barroom` – `padding-bottom: 16px` (in px: the size of a scroll bar does not follow A− A+).
- **Tests:** `t_entries.py` new case `barroom` (FluentOverlayScrollbar of Chromium: a wide dashboard no room, 700 px the room and "written “Drums”" above the bar, only boxes that scroll, wide again none; a classic bar: no room); `caserun.py` new `launch_own(**kw)` – a browser of its own for a case that needs other launch options.

**After the review of block BA** (an independent agent; fixed here):

- **Scroll bars (3.40.8):** `overflow-x` checked (a `.dci-rowswrap` does not scroll); each box once, all read before any is changed (no layout per box) – both in the bullets above.
- **T059 (3.40.5):** `EDITABLE_LISTS.T059` `emptyValue: true`, `hint: 'mapping.linesRegions'`. **`asPair(x, tid)`**: a word takes the area of the same region in the file (a word "West Coast" added in 3.39.x, a whole register of 3.40.4); `rawListItems`, `effectiveRaw`, the register's `show` pass the list. **`checkListChange`**: for T059 a word or `[region, '']` too (a file of changes of 3.40.4 was skipped). **`listFromLines`**: "region" and "region =" (a region without an area; saving ✎ T059 failed). **`showItem`**: a pair without a value shows the key alone. `listEditHtml`: `L.hint` before the hint of the shape.
- **Region credit (3.40.5):** the suggestion keeps MusicBrainz's disambiguation (`disambiguation: hit.disambiguation`; until now the explanation, which became `mbComment` once chosen); the explanation is the tooltip (`titleOf`). `name-use` sets **`a.regionPick`** `{ mbid, region }`; **`sourceCreditFor`** returns the region while `regionPick.mbid === a.mbid` (until now `syncSourceCredits` put the source's spelling back with S008 / S036); new **`dropRegionCredit(a)`** (in `name-use` and `setArtistManually`): another entry chosen – the region's credit goes from the rows not credited by hand (with S036 off it stayed). `regionPick` remembered with the entry (`x.match.region`).
- **⧉ (3.40.7):** the symbol drawn by CSS (`::before`), the button without text and without the space before it – the text of the entry's head stays its name (four test files read it); if `navigator.clipboard.writeText` refuses, a selected text and `execCommand('copy')` (as `copyLog`); refused too: `.dci-copyfail` (⚠) for 3 s; `aria-label` follows the title.
- **Head (3.40.6):** `.dci-head-sep` with a negative margin (each separator takes 3 instead of 11 px); `.dci-head-tools` `flex-wrap: wrap` – at 400 px a second line instead of ✕ outside the dashboard.
- **Texts (English):** `mapping.linesRegions`.
- **Tests:** `t_sources_bandcamp.py` `cloudpondbc` B (the explanation in the tooltip, no disambiguation in the head), C (another area chosen by hand: the credit goes), D (S036 off: credited all the same; another area: it goes – fails on 3.40.7); `t_rules_window.py` new case `regionlist` (a file of changes with words, ✎ T059 with "Lake Region" and "Delta =", a whole register of 3.40.4); `t_ui_head.py` `copyname` D (the clipboard refuses: through a selected text ✓, refused too ⚠), new case `headnarrow`.

## Import 3.40.7 · 2026-11-03

⧉ next to the name of an entry without a MusicBrainz entry chosen: copies the name of the source (collected item Z-CP; Q-av, Q-aw).

- **New `copyNameHtml(a)`** in `entryNameHtml` (both returns, after the name): `.dci-copyname` (`data-act="name-copy"`, `data-name` `a.name`, the name of the entry at the source – at Discogs the artist name without its number, not the spelling of the release shown in the head), `hidden` while `a.mbid` is set; none for a placeholder entry. Every kind of entry: people, companies, places, also those with suggestions only (a suggestion is not a chosen entry).
- **`updateGroupHeader`:** shows or hides the ⧉ of the entry when an MB entry is chosen or dropped (`hidden = !!a.mbid`).
- **Handler `name-copy`:** `navigator.clipboard.writeText(name)`; the button gets `.dci-copied` (✓) and the title `group.copiedName` for 1.5 s, then ⧉ and its title again; if the browser refuses, the title `group.copyFailed` (nothing else changes).
- **CSS:** `.dci-copyname`, its symbol `::before` (⧉; ✓ with `.dci-copied`) – the button has no text, so the text of the entry's head stays its name (code and tests that read it).
- **Texts (English):** `group.copyName`, `group.copiedName`, `group.copyFailed`.
- **Tests:** `t_ui_head.py` new case `copyname` (⧉ at the one entry of the release not linked, not at the linked ones; a click: the name in the clipboard, ✓, ⧉ again; a pasted text: ⧉ also at a name with a suggestion, gone once it is chosen).

## Import 3.40.6 · 2026-11-03

The head of the dashboard in groups, "this browser only" at the statistics (collected items Z-HB, Z-ST; Q-ay, Q-au).

- **`buildOverlay`:** the buttons of `.dci-head-tools` in groups with `.dci-head-sep` between them – ☰, A− A+, ⤢ | Mapping rules, Log | Statistics, ⌨, ⚙ | ✕ (until 3.40.5: ☰, A− A+, ⚙, Statistics, Mapping rules, Log, ⌨, ⤢, ✕).
- **`renderStats`:** `.dci-stats-local` after the heading – `stats.local`, its tooltip `stats.localTitle`.
- **CSS:** `.dci-head-sep`, `.dci-stats-local`.
- **Texts (English):** `stats.local`, `stats.localTitle`.
- **Tests:** `t_ui_head.py` `head` (the order and the groups); `t_ui_settings.py` `statsbutton` (Statistics · ⌨ · ⚙; "this browser only" and its tooltip).

## Import 3.40.5 · 2026-11-03

Regions suggest the area they lie in (collected item Z-RG; Q-az, Q-ba).

- **Mapping:** `TEXT_REGIONS` (T059) pairs `[region, area]` – Pacific Coast, West Coast, East Coast → United States (until 3.40.4 words); `EDITABLE_LISTS.T059` shape `pairs`.
- **New `regionOf(name)`** (the region of T059 however written, `[region, area]`, also from a list of words of an older file) and **`asPair(x)`** (`rawListItems` and `effectiveRaw`: a word of a list become pairs – your changes to T059 of 3.39.x – gets an empty area). **`areaOf`** uses `regionOf`.
- **`suggestByName`:** an area entry that is a region of T059 – MusicBrainz's area of its area's name (`area:(…) OR alias:(…)`, the same name) first among `nameHits` (`region`, `similar`, disambiguation `area.regionHit`), log `regionSuggested`; the log `nameSuggested` without it. Only suggested (Q-az).
- **`name-use`:** a hit with `region` credits the entry's rows as the region of the list (a credit typed by hand stays; Q-ba). The mark of the suggestion `match.markRegion`.
- **Register:** T059 – its note and its pairs shown.
- **Texts (English):** `area.regionHit`, `log.regionSuggested`, `match.markRegion`.
- **Tests:** `t_sources_bandcamp.py` `cloudpondbc` B ("Pacific coast": United States first among the suggestions, not set; chosen: "as “Pacific Coast”"); `t_mapping.py` `oldfile` C (a file whose T059 is a list of words: the region read); `register_golden.json` anew.

## Import 3.40.4 · 2026-11-03

Entries that share a link are all looked up (collected item Z-LU; Q-ax).

- **`resolveArtists`:** `byUrl` holds a list of entries per address (until 3.40.3 one: a second entry of the same address – the person Robert Rich and "©2026 Robert Rich" of his own Bandcamp page – took the place of the first, which was never looked up and stayed "Looking up MB artist …" with its rows on "Choose type …"); `found` per kind (`artist`, `label`) and address (until then one map: the answer of the label lookup could replace the artist's).
- **Tests:** `t_sources_bandcamp.py` new case `cloudpondbc` (the credits of Robert Rich's "Cloud Pond Sky River" from his own page: both entries "Robert Rich" found through the link, none waiting; fails on 3.40.3).

## Import 3.40.3 · 2026-11-02

"Credited as" in the head of a block of the entries matrix (collected item Z-AK; Q-ak – Q-aq).

- **New `emBlockAcHtml(a, b, title)`:** in `emBlockHtml`, in the head of a block of several lines (`many`): a field `data-f="em-bac"` with `data-rows` (all rows of all its lines, also those on Skip), `list="dci-ac-<key>"` (the entry's spellings), prefilled with the spelling all its rows carry; several: empty, placeholder `em.blockAcSeveral`, the spellings in its tooltip (`em.blockAcSeveralTitle`).
- **New `emBlockAc(a, rows, value)`:** credit and `creditTouched` for all the rows (lines of one role with two spellings join, `lineKeyOf`); `S.emUndo` with `{ id, fields }` and the message `em.blockAcSet` / `em.blockAcClear` with ↶ (`em-undo`); nothing when nothing changes. **`emUndoDrop`** restores `fields` too.
- **`entryMatrixChange`:** `em-bac` → `emBlockAc` (the field's `change`: left or Enter); **`onKeydown`:** Enter in an unchanged `em-bac` applies it too ("several" left empty: the MusicBrainz name for all) – a changed one only through its `change` (once).
- **CSS:** `.dci-em-bac`.
- **Texts (English):** `em.blockAcLabel`, `em.blockAcTitle`, `em.blockAcSeveral`, `em.blockAcSeveralTitle`, `em.blockAcSet`, `em.blockAcClear`.
- **After the independent review of block AZ (3.40.1 – 3.40.3):**
  - **"Import credits …" of the line** imports the source it counted: the autostart entry has `force`, `S.editorLinks` sets `S.gapCountLink` from it, and `startSource` takes it first (until then the order of the sources chose – the Discogs release without credits, or the dialog of several Bandcamp pages).
  - **The dashboard's number per source:** new `gapExactKey(mbid, kind)` – Bandcamp's in `dci-gap-exact:<MBID>:bandcamp` (an import of the empty Discogs release took its place); `gapCount` listens to the key of its source.
  - **Discogs 404:** Bandcamp steps in too (`dgEmpty.missing`, `gap.dgMissing`); `gap.dgNone` / `gap.dgNoneNotes` "no credits to import" (also credits that are all left out). The Bandcamp page of 3.40.0 (`dci-gap:<MBID>` with `bId`) is taken over into `:bandcamp`, its ✕ with it.
  - **"co?":** the other names' own "is person" names count too (two performance names of one person, no lookup more); at most five other names looked up.
  - **Z-AK:** the field only with several roles (`emRoleKey`; not one role in two spellings); `emBlockAc` – Undo for the rows changed, as they were (`creditTouched` and `caseCredit`; undefined removed again), only for rows that still carry the value set (`set`); `caseCredit` false (↺ in capitals no longer takes it back); the message counts the roles changed; a draft of what is typed (`S.emBacDraft`, `onInput`) and `data-dirty` – Enter in an unchanged field only after typing in it; `rerenderGroup` gives the focus back to the field of the same block (`.dci-em-block[data-block]`).
- **Tests:** `t_ui_head.py` new case `blockac` (Oliver Lake's instruments: the field with "several"; "Lake" + Enter – the flutes join, the message with ↶; Undo; a line changed by hand keeps its own, also against the older ↶; emptied – typed in, cleared, Enter: the MusicBrainz name, the focus in the field again; Carl Allen's blocks of one role: none; compact: no field, the chips with their "as …"); after the review also `t_start.py` `gapmore` E ("Import credits …" imports Bandcamp; Discogs 404: Bandcamp; the number per source), `t_works_more.py` `coverworks` d8 (two performance names of one person), its waits longer under load (45 s for "co?", the lookups up to 30 s, the button of the works first, the list opened again when a redraw closed it), `workpick` clicks "Link" once more when a redraw took the first click; `t_entries.py` reads the head of a block without its new field.

## Import 3.40.2 · 2026-11-02

The line of the release page: Bandcamp in place of a Discogs release without credits, several Bandcamp pages (collected items Z-AD, Z-AE; Q-ad, Q-ae, Q-ag).

- **New `gapRead(src, prev, ws)`:** the credits of one page of a source kept a week – read again when older, a failed answer kept (404 a week, else an hour) – `{ kept, changed, failed }`, or null when the request was broken off; the `since` of 3.40.0 kept with the same credits. Until 3.40.1 inline in `initReleaseGap`.
- **`initReleaseGap`:** Discogs first (`dci-gap:<MBID>`, as before); a Discogs release read without credits → `dgEmpty` (`{ notes }`) and Bandcamp steps in; Discogs failed → no line (as before). Bandcamp: all its pages linked (three at most), each kept in `dci-gap:<MBID>:bandcamp` (`{ at, pages: { <url>: kept } }`; pages no longer linked dropped; until 3.40.1 one page in `dci-gap:<MBID>` with `bId`), the one with the most credits counts (`others`: the rest, with their number of credits or null when not read). The dismissal (✕) through `use.dismiss` – on the Discogs entry or the Bandcamp page counted.
- **`showReleaseGap(opts)`:** `opts.key` replaced by `opts.dismiss`; new `opts.dgEmpty` (the text first: `gap.dgNone`, `gap.dgNoneNotes`) and `opts.others` (under ▸: `gap.bc.other`, `gap.bc.otherFailed`).
- **Texts (English):** `gap.dgNone`, `gap.dgNoneNotes`, `gap.bc.other`, `gap.bc.otherFailed`.
- **Tests:** `t_start.py` `gapmore` E (a Discogs release without credits, its notes kept: Bandcamp with the text first; three Bandcamp pages – a label's with one credit, the artist's, one not found: the artist's counted, the others under ▸, all three kept; ✕ holds over a reload); D reads the Bandcamp page from `dci-gap:<MBID>:bandcamp`.

## Import 3.40.1 · 2026-11-02

"co?" and "is person" (collected item Z-AF; Q-af, Q-ah).

- **`bandLinks`:** `S.bandOf` holds `{ band, person }` per artist (until 3.40.0 a Set of "member of band"): the same answer of `artist/<mbid>?inc=artist-rels` gives "is person" too (`person`), either way.
- **`coverComposers`:** the composer's names – the composer and its "is person" names: one of them a performer → no "co?"; their groups looked up too (`bandLinks(others)`, one lookup each; no "co?" while one waits), a group of one of them performing → no "co?".
- **Tests:** `harness.IS_PERSON` (legal name → performance names, both directions in `/ws/2/artist/`); `t_works_more.py` `coverworks` D – the release's artist the composer's other name, the other name a member of the release's band (the lookups of both names counted), the control: the other name in no band of the release ("co?"); `pill_with` waits for the lookups.

## Import 3.40.0 · 2026-11-02

The line of the release page: only when something is missing, Bandcamp, "Count exactly" (block AY: Q-g, Q-n, Q-o, Q-x).

- **Release page (before the dispatch of `PAGE_KIND`; only what is defined before it or hoisted is used there):**
  - New constants `GAP_NONE_KEY` (`dci-gap-none`), `GAP_COUNT_PREFIX` (`dci-gap-count:`), `GAP_COUNT_HASH` (`dci-count`), `GAP_COUNT_MAX_MS` (five minutes).
  - **`initReleaseGap`** – the page's links and MusicBrainz's: Discogs, else exactly one Bandcamp page (`src = { kind, id, url }`); the kept credits by `dId` or `bId` (one key `dci-gap:<MBID>` as before); the release lookup asks `artist-credits` too. No line without credits (`kept.credits` empty) nor when nothing is missing – `est.total` 0, or an exact number 0 not older than the credits (`exact.at >= kept.at`) –, unless `dci-gap-none` is true. A failed request of the source is also written to the console.
  - New **`gapDiscogs(dId)`** (the 2.5 s between the line's Discogs requests, as before inline), **`gapBandcampCtx(ws)`** (the context of `BANDCAMP.release` on the release page: `httpGet`, `isRole` `gapIsRole`, `isCompanyRole` inline, `resolveTracks` `gapTracksIn`, no `resolveTitles`, `bandcampTracks` false, `artistNames` of the release's artist credit), **`gapIsRole(phrase)`** (the register's roles; an instrument by its looks – `typesFor`/`isKnownRole` are in their temporal dead zone there), **`gapTracksIn(spec, srcTracks)`** (numbers and ranges), **`gapExactOf(exact, src)`** (the dashboard's number for this source; a number of 3.39.x without `src` counts for Discogs), **`gapExactWrite(mbid, pending, n)`**.
  - **`showReleaseGap(opts)`** – one object (`{ mbid, src, est, exact, key, notes }`); `data-src` on the line, the text in `[data-gap-text]`; the texts of Bandcamp; new button **Count exactly** (`data-gap="count"`).
  - New **`gapCount(opts, box)`** – writes `dci-gap-count:<MBID>` (`{ links, at }`), opens `/release/<MBID>/edit-relationships#dci-count` with `GM_openInTab` (`active: false, insert: true, setParent: true`; without it `window.open`), listens to `storage` of `dci-gap-exact:<MBID>`: the last number of the source, 2.5 s after it (the dashboard writes at the end of the import and again with its next summary) → `close()` of the tab, the line drawn again with it; five minutes without: `gap.countLate`, the flag removed.
  - **`gapSweep`:** flags of "Count exactly" older than five minutes.
- **Relationship editor:** `S.editorLinks` – the address `#dci-count` (taken off): the flag of the release (taken, at most five minutes old) → `S.autostartFrom = 'count'`, `S.gapCountLink`; **`startSource`** takes `S.gapCountLink` first (also when the release has other sources); the log `fromCount`. **`S.gapExactPending`** is `{ src, id }` for Discogs and Bandcamp (was the Discogs id); written with `gapExactWrite` (the summary: when `SOURCES[pending.src]` is the current source).
- **Settings:** ⚙ Sources – the row of `dci-gap-on` with the new texts, new row `gap-none` (`data-set`); `TOPIC_KEYS.sources`, `SETTINGS_KEYS` with `GAP_NONE_KEY`.
- **Texts (English):** `gap.bc.missing`, `gap.bc.none`, `gap.bc.incomplete`, `gap.bc.how`, `gap.count`, `gap.countTitle`, `gap.counting`, `gap.countLate`, `gap.countFailed`, `gap.exactOpen`, `log.fromCount`, `settings.gapLine`, `settings.gapLineTitle`, `settings.gapNone`, `settings.gapNoneTitle`; removed `settings.gapOn`, `settings.gapOnTitle`.
- **After the independent review of block AY:** the tab of "Count exactly" without the dialog of the media (`chooseMedia`: all media when `S.autostartFrom === 'count'`; until then a release of two media never came back) and with `S.rememberHold` (it neither restores nor writes `dci-remember:<MBID>`); the dashboard writes `open` with its number (`S.lastSumOpen`: rows with issues – no MusicBrainz entry, no type …; `gapExactWrite(mbid, p, n, open)`) and "nothing missing" needs `open === 0` (a count of 0 with names not chosen yet hid the line), the line names them (`gap.exactOpen`); an import without entries writes 0 / 0, an import that fails in that tab writes `{ failed }` on the flag (`gap.countFailed`); `gapCount` closes the tab also on failure, after five minutes and on `pagehide`, ✕ while it counts keeps the line away; kept credits have `since` (the same credits read again keep it – the dashboard's count of 0 held only a week); `gapIsRole` by names – new `gapInstrumentWords()` (MusicBrainz's instruments and voices kept by `idx()` in `dci-gap-instruments`, `GAP_INSTR_KEY`, a month; T048, T001, T058) and kinds (`INSTRUMENT_MODIFIER`) – no longer by looks ("Jane Roe – Electric Guitar" read "Jane" as the role; "Stream: …", "Length: …" were credits); new `gapTracksByTitles` (`resolveTitles` of the Bandcamp context). `gapCreditsOf` keeps the role (`role`): two roles of one person on the same tracks count twice (until then once).
- **Tests:** `t_start.py` new case `gapmore` (no credits; nothing missing, the setting, one missing, the dashboard counted none – with rows open: the line, the same credits a week later; "Count exactly" for Discogs (two media) and Bandcamp, an import that fails – the tab opened as a page of its own, as a popup of `window.open` keeps the window of its about:blank without the script –; Bandcamp's rough estimate and its parts; an album page without credits); `common_rows.drag` asks for the elements again for up to 3 s (a matrix drawn anew by a result of the background took them for a moment – `mxdrop` failed once in the full run, K-7); `mxdrop` waits up to 10 s for a drop to be drawn (4 s before); `t_ui_settings.py` `reset`: `dci-gap-instruments` is data, no setting (kept by "Reset all settings").

## Import 3.39.9 · 2026-11-02

"co?" and who performs a track (collected item K-9; Q-e, Q-m, Q-w).

- **New `PERFORMING_TYPES`** (instrument, vocal, performer, conductor, performing orchestra, orchestra, chorus master, concertmaster).
- **The import:** `S.mbTracks[i].trackArtists` (the track's artist credit) and `mbPerformers` (MusicBrainz's performers of the recording, `PERFORMING_TYPES`).
- **`performersOf(i)`:** also the track's artists and MusicBrainz's performers; the dashboard's rows of all `PERFORMING_TYPES`.
- **New `bandLinks(ids)`:** "member of band" of each artist (`artist/<mbid>?inc=artist-rels`, `mbWsIdle`), once (`S.bandOf`: mbid → Set or 'wait'); the works matrix drawn again when they are there.
- **`coverComposers`:** no "co?" while a lookup waits, nor when the composer is linked by "member of band" with a performer (either way).
- **Tests:** `harness.BAND_MEMBERS` (group → members, both directions in `/ws/2/artist/`), `harness.TRACK_AC` (a track's artist credit); `t_works_more.py` `coverworks` D (without them "co?"; a member of the release's band, the pianist of the recording in MusicBrainz, the track's artist: none), B waits for the lookups.
- **After the independent review of block AX:** `bandLinks` – one lookup, the composer's own (the relationship "member of band" is one of both artists: its bands and its members), one loop for all lookups (`S.bandQueue`, `S.bandRunning`), the matrix drawn again with `renderWorksBackground` (not while typing in it or dragging; until then `renderWorks`), an answer that failed asked again after five minutes (`{ failAt }`); new `S.mbReleasePerformers` – MusicBrainz's performers of the whole release count too (`performersOf`). Test: `coverworks` D the lookups counted (the composer's only), the other direction (the composer's band, the release's artist a member of it), MusicBrainz's pianist of the release.

## Import 3.39.8 · 2026-11-02

Several names below a heading, the release's artist as a title line (collected item Z-1; Q-y).

- **`TEXT.parse`:** new `headingOf(raw)` (a line of instruments or voices – `stackInstr` –, or a role ending in "by" of four words at most, a colon at the end allowed), `headingLists(lines)` (rule **S067**: a heading and two or more `stackName` lines below it – a role heading one or more –, single empty lines between them) and `readHeading(h)`; the lines of a heading are blanked for `stackPairs` (S058) and read first. Rule **S068** in `readLine`: a line that is only a release artist's name → `ignored` (why `releaseArtist`).
- **Register:** rules S067, S068.
- **Texts (English):** `ignored.why.releaseArtist`.
- **After the independent review of block AW (3.39.7 – 3.39.8):** S067 – no heading right below a name (names above their instruments stay pairs of S058, which could be read the other way round with ⇅; until then the heading took the names of the next instrument), below a role heading only the names right below it, no track title and – after an empty line – no release artist as a name (`notListName`), a role with a colon as heading ("Producer:"); S068 not within a block of publishers (S043; until then "Publishers: / Robert Rich" lost him). `initialsUse` – the works matrix drawn again, a credit typed by hand kept, `matchTouched` reset when the entry becomes the name, a row taken out before and brought back goes to the entry chosen (`S.entryMoved`, `restoreRow`), the choice remembered with the release (`rememberSnapshot` `initials`, chosen again first in `restoreRemembered`; `S.initialsChosen`).
- **Tests:** `t_text_basics.py` new case `booklets` (two booklet pages built for the test – stacked and in one line –, read with Tesseract 5.3, the text as read: the same entries, the title left out); `register_golden.json` anew; after the review: new case `initialsmemo` (the name chosen remembered over a reload), `text_corpus.json` the cases of the review (names above with two players, a role heading followed by titles or the release's artist, "Producer:", a block of publishers with the release's artist).

## Import 3.39.7 · 2026-11-02

Initials to click, "R.R.", more words and regions (collected items K-8, K-11; Q-j, Q-ac).

- **`initialsOf`:** initials with dots between the letters get their last dot back ("R.R" → "R.R."), also as the name of an entry of several names.
- **`groupCredits`:** `group.initials` every spelling once, joined ("RR, R.R.").
- **`initialsHtml`:** `group.initialsOf` and a button per name (`data-act="initials-use"`, `group.initialsUseTitle`); new **`initialsUse(a, name)`** – the rows go to the entry of that name (credited and `anv` the initials; the entry of the initials removed) or the entry becomes that name (`initials`, `status` pending, `resolveArtists({ only })`); log `initialsUsed`.
- **Mapping:** `INSTRUMENT_ASK` (T058) "found objects", "household objects" → percussion; "toys", "toy instruments" → percussion, electronic instruments; `TEXT_REGIONS` (T059) "West Coast", "East Coast".
- **Texts (English):** `group.initialsOf`, `group.initialsUseTitle`, `log.initialsUsed`; removed `group.initialsMany`.
- **Tests:** `t_text_basics.py` `cloudpond` (D: "Jane Roe" clicked; K-11 "Layout by R.R."); `t_mapping.py` new case `toys`; `text_corpus.json` "… 2020 East coast"; `register_golden.json` anew; `t_rules_window.py` `wqedit` Q003 with creative direction on the release group (the change of 3.39.6).

## Import 3.39.6 · 2026-11-02

Roles of companies at a person, table words, the Bandcamp tag, the test `mxdrop` (collected items K-6, K-7, K-13; Q-i).

- **`mapRole`:** rule **S066** – a person's role that is no rule's: `PERSON_AT_ROLE` ("Mixed At" …) → the mapping of "<verb> By" with the note `atPerson`; `PERSON_COMPANY_SKIP` ("Pressed By", "Distributed By", "Licensed To" …) → level `skip`, note `companyPerson`, rule S066 (both patterns may be missing in an older mapping file: nothing then).
- **Mapping:** new patterns `PERSON_AT_ROLE`, `PERSON_COMPANY_SKIP` (T060).
- **`applyMappingChanges`:** a table of shape `map` (T001, T058) with its words in lower case (`norm`), as the code looks them up.
- **CSS:** `.dci-src-bc` `#3a7a89` with an inner rim `#629aa9`.
- **Register:** rule S066, table T060.
- **After the independent review of block AV (3.39.4 – 3.39.6):** a role typed by hand as a type's name (`applyRoleText`) drops the `prefix` (until then "Assistant Engineer" typed again as "engineer" ticked "assistant" anew); the role credit of the word (`roleCreditForInner`) comes before the rules that give none (an instrument technician, creative direction – "Assistant Creative Director" into the edit note as the row says), of the task after an answered type question ("co-director"), without a final "by" (`prefixCredit(p, rest)`); `prefixNoteHtml` says "credited" or "edit note" by where the role credit really goes (`roleCreditTarget`); the word also after an en dash ("Co–Arranger"); Q003 (Directed By) answered creative direction goes to the release group (MusicBrainz has no such type on the release); `TEXT_COMPANY_RE` with "printed by" (a pasted text's "Printed by X" a company, not a person S066 would leave out).
- **Texts (English):** `note.atPerson`, `note.companyPerson`.
- **Tests:** `t_mapping.py` new cases `companyperson` (mix, recording, mastering on the release, the note, no place; pressed / distributed left out; licensor) and `listkeys` (T001 changed with "Lap Steel2", in Node); `t_sources_bandcamp.py` `bcspell` the tag's colours; `t_works_matrix.py` `mxdrop` waits for the import and reads a drop again until it is drawn (K-7: under load it read too early); `register_golden.json` anew; after the review: `assistants` a row added by hand and typed again, `voices` "Assistant Creative Director" and "Directed By" answered creative direction, `text_corpus.json` "Printed by Druckerei Fischer" (a company; the corpus's company roles with "printed"); `t_works_matrix.py` `matrixcols` creative direction of the test page on the release group, as on MusicBrainz (Q003 answers it there).

## Import 3.39.5 · 2026-11-02

Countertenor, liner notes translated, creative direction (collected items K-3 – K-5).

- **`roleRules`:** new `voiceWord` ("Counter-tenor" → countertenor, "Mezzo Soprano", "Bass Baritone") and `VOICE_RANGES`; **R009** also a voice alone that no instrument is named after (countertenor, contralto, mezzo-soprano, bass-baritone); **R018** a voice as detail ("Vocals [Tenor]") → `primaryCands` "tenor vocals", the detail consumed.
- **`roleCreditForInner`:** no role credit for R009 when the role is the voice without "vocals"; none for R081 on MusicBrainz's creative direction.
- **Mapping:** R081 level `release_group` (with a note).
- **Import (`addCreditRows`):** creative direction for single tracks goes onto those recordings, as a producer role does.
- **K-4:** "Liner Notes [Translation]" ticks translator through `applyDetailFlags` already; only a test.
- **Tests:** `t_mapping.py` new case `voices` (countertenor, "Vocals [Tenor]", liner notes with translator, creative direction on the release group and on a recording, no edit note); `register_golden.json` anew (Countertenor, "Vocals [Soprano]", Creative Direction / Director).

## Import 3.39.4 · 2026-11-02

A word before the role: "Assistant Engineer", "Co-Arranger" (collected items K-1, K-2; Q-s, Q-u).

- **`mapRole`:** rule **S065** – a role that is no rule's (fallback / R096) beginning with "Assistant", "Asst.", "Associate" or "Co-": the rest mapped (`mapRole`), its `flags` with assistant / associate / co, `prefix` { flag, word, rest }. New `prefixCredit(p)` ("assistant arranger", "co-composer").
- **Rows:** `makeRow` and the role changed by hand keep `prefix` (`prefixCredit` false); `applyDetailFlags` – with a type: the flag where the type has the attribute, else `row.prefixCredit` (the flag removed); `roleCreditForInner` – `prefixCredit` gives the role credit (details before it); `REMAP_FIELDS` with `prefix`, `prefixCredit`.
- **New `prefixNoteHtml(row)`** in `roleCell` (both forms): `note.prefixCredit` (the type has a role credit) or `note.prefixNote` (edit note only; `canRoleCredit`), with the rule id S065.
- **R051** (arranger): the details "co" / "associate" are its attributes (`has`), no instrument candidates of them.
- **Register:** rule S065.
- **Texts (English):** `note.prefixCredit`, `note.prefixNote`.
- **Tests:** `t_mapping.py` new case `assistants` (engineer, mix, arranger with co, "Arranged By [Co]", "Assistant Producer"; "Assistant Arranger" edit note only with the preview; "Assistant Photographer" credited); `register_golden.json` anew ("Assistant Engineer" engineer with assistant, rule S065); `t_ui_settings.py` `cache` waits for the import after a reload (the tab's log kept the old "Import complete", so the rows were now and then read before what was remembered had been taken over – a race of the test).

## Import 3.39.3 · 2026-11-02

The statistics with their own button in the head (collected item 189).

- **Head:** `headBtn('stats-open', 'stats', …)` after ⚙ (new symbol `ICONS.stats`, a bar chart); the body a new `.dci-settings.dci-stats-dock` `data-el="stats"` after the settings.
- **New `renderStats()`** (after `renderSettings`): `S.statsOpen`, `aria-expanded` of the button, the heading (`data-act="stats-fold"`) and `statsHtml()`; the focus kept. Called by `rebuildDashboard`, `statsLoad` (instead of `renderSettings` with the tab "statistics"), `stats-period`, `stats-delete`.
- **Handlers:** `stats-open` (toggles, reads the records anew, closes ⚙ / "Reset all settings" and the docked rules), `stats-fold`; `settings-open` and `openRules` (docked) close the statistics.
- **Settings:** `SETTING_TOPICS` without `statistics`, its body gone (a remembered tab "statistics" shows "General"); `TOPIC_KEYS.statistics` stays for "Reset all settings"; `settings-open` and `settings-topic` no longer empty `S.statsData`.
- **Texts (English):** `stats.title`, `stats.buttonTitle`, `stats.foldTitle`.
- **Tests:** `harness.open_stats(pg)`; `t_ui_settings.py` new case `statsbutton` (the button after ⚙, pressed, one of the three open, the heading, only "Collect statistics", no tab), `stats`, `statsmore`, `statsdev` through the button, the lists of the topics without "statistics" (also `cache`); `t_coverart.py` the tabs; `t_ui_head.py` `head` the buttons of the head.

## Import 3.39.2 · 2026-11-02

"lap steel", "objects", "Pacific coast", a line "With …" from Bandcamp (collected items 186 – 188).

- **`TEXT.parse`:** `artistNames` each name once (by `norm`; Bandcamp passes its album's artist besides the release's – S061's `ours.length === 1` failed and the guesses went to `unknownParts`).
- **`areaOf`:** a first part that is a region of `TEXT_REGIONS` (T059), in any case, gives that region's spelling as the area (`{ name: region, area }`), also when it would not read as a place ("Pacific coast").
- **`guessInstrument`:** the instruments of `INSTRUMENT_ASK` (T058) for the word first (`findChildAttr` of the root; those MusicBrainz has), then `similarInstruments`; `row.instrGuess.offered` (kept by `copyRowForEvent`). New `guessOffered(g, name)`, `guessLabel(g, name)` (an offered instrument as "percussion “objects”"); `guessSpelling` 'own' for an offered one (credited as written), `guessNoteHtml` none for it; `instrGuessHtml` asks `instrGuess.askAs`; the answers of a chip (`chipAnswers`), its note (`chipNoteText`) and the compact line's question (`clineHtml`, `cl.instrGuessAs`) with `guessLabel`.
- **Mapping:** `INSTRUMENT_ALIASES` "lap steel" → lap steel guitar; new map `INSTRUMENT_ASK` (T058, editable: `EDITABLE_LISTS`, shape map) "objects" → percussion; new list `TEXT_REGIONS` (T059, editable) "Pacific Coast".
- **Register:** lists T058, T059.
- **Texts (English):** `instrGuess.askAs`, `cl.instrGuessAs`.
- **After the independent review of block AU (3.39.1 and 3.39.2):** `areaOf` looks for a region before `TEXT_NOT_AREA` and without a leading "the" ("2021 the Pacific coast"); `guessInstrument` finds the key of T058 in any case (a changes file imported as written) and offers "other instruments" only once (its own answer); the badge of the match (`matchHtml`: `match.linked`, `match.noLink`, `match.noLinkCompany`) and the tag of a role credit taken from the source (`attrCell`) name the entry's source (a supplement's entry its own); a mapping file of an older version without a list of `EDITABLE_LISTS` (the script installed before its file): the list empty (after `MAP`), `applyMappingChanges` and `rawListItems` skip it – until now an error on loading with changes of your own.
- **Tests:** `t_text_basics.py` `withline` ("lap steel" without an other name of MusicBrainz's; "objects" asked with percussion first, percussion chosen: credited "objects", no note), `cloudpond` ("Pacific coast" the area Pacific Coast, recorded in, nothing not recognized); `t_sources_bandcamp.py` `bcspell` C (the line "With …" from Bandcamp: the release's artist's, "objects" asked, nothing not recognized); `t_rules_window.py` the editable lists with T058, T059; `register_golden.json` anew; `t_mapping.py` new case `oldfile` (a mapping file without T058 / T059 and changes of your own, in Node); `text_corpus.json` two lines ("… 2022-2025 Pacific coast", "… 2021 the Pacific coast"); `t_text_basics.py` `withline` with T058 changed as a file would ("Objects", with other instruments); `t_static.py` also checks the keys of `trSrcOf` (and their …Any form) and both keys of `log(level, a ? 'k1' : 'k2')`; `t_start.py` `gapline` counts the requests to Discogs of the whole browser context (under load the first one came before the page's listener: a race of the test, seen once in the full suite).

## Import 3.39.1 · 2026-11-02

The spelling and the tag of an entry's source (collected item 185).

- **New (after `trSrc`):** `entrySource(a)` (`a.src` of a supplement's entry, else `S.source`), `sourceLabel(src)` ("pasted text" for `TEXT`), `trSrcOf(src, key, params)` (`trSrc` for a given source: the text as it is for Discogs, else its `…Any` form with `{src}`), `srcTagClass(src)` (`dci-src-dg` / `dci-src-bc` / `dci-src-tx`).
- **`entryNameHtml`, `creditChipHtml`:** `group.discogsName`, `group.anvStar`, `group.creditedSpelling`, `group.creditedSpellingTitle` through `trSrcOf` with the entry's source; **the import** logs `anvCreditsAny` (with `src`) unless all those entries are Discogs'.
- **The head of an entry (`groupHtml`):** the tag of the source link `srcTagClass` of the entry's source, its tooltip `link.discogsTitle` with that source's name (until now `SOURCE_NAME`); **`attrCell`:** the tag "from the source" of a role credit and the tooltip of its field through `trSrc` / `srcTagClass(S.source)` (the field's tooltip said "Taken from Discogs" with every source); **`seriesLabelHtml`:** the tag `srcTagClass(S.source)`.
- **CSS:** `.dci-src-bc` (Bandcamp's blue `#629aa9`), `.dci-src-tx` (grey), the ↗ after a Bandcamp tag in a darker blue.
- **Texts (English):** `group.discogsNameAny`, `group.creditedSpellingAny`, `group.creditedSpellingTitleAny`, `group.anvStarAny`, `log.anvCreditsAny`.
- **Tests:** `t_sources_bandcamp.py` new case `bcspell` (Robert Rich credited "RR" from Bandcamp: the chip, the tooltips, the log, the tag's colours and tooltip, no "Discogs" in the head).

## Import 3.39.0 · 2026-11-02

The release page: relationships of the Discogs credits not on MusicBrainz yet (collected item 172).

- **New (before the page dispatch, so the release page has them):** `initReleaseGap(mbid)` (from `initReleasePageHook`; only on `/release/<MBID>`, setting `GAP_ON_KEY`): `/ws/2/release/<MBID>?inc=url-rels+artist-rels+label-rels+place-rels+recordings+recording-level-rels+work-rels+work-level-rels` by `fetch`; its Discogs link (`sourceLinksOf` – what is Discogs stays in its adapter); `DISCOGS.release(id)` → `gapCreditsOf(rel)` (each role of a credit – `mapRole`, companies `mapCompanyRole` – with its level, names – the name and the credited name, `gapName` – and tracks), kept in `dci-gap:<MBID>` a week (`GAP_KEEP_MS`) with `dismissed`; `gapMbNames(ws)` (names on the release, each recording, its works); `gapEstimate` (per credit and track: missing when none of its names is there; parts recordings, release, works, companies); `showReleaseGap` (`.dci-gapline` after the `h1` of `#content`, inline styles: ▸ the parts, "Import credits …" – `AUTOSTART_KEY` and the relationship editor –, ✕ – `dismissed`).
- **The summary of the footer:** the number of new relationships of a release from Discogs into `dci-gap-exact:<MBID>` (`{ n, at }`, when it changes – `S.gapExactLast`).
- **Settings:** ⚙ Settings → Sources `data-set="gap-on"` (`settings.gapOn`); `GAP_ON_KEY` among the keys of the topic and of "Reset all settings".
- **Texts (English):** `gap.missing` (one / other), `gap.missingNotes` (one / other), `gap.none`, `gap.noneNotes`, `gap.incomplete`, `gap.exact` (one / other), `gap.partsLabel`, `gap.recordings`, `gap.release`, `gap.works`, `gap.companies`, `gap.how`, `gap.import`, `gap.closeTitle`, `settings.gapOn`, `settings.gapOnTitle`.
- **After the independent review of block AS:** "Import credits …" hands over the link as the dashboard takes it (`sourceLinksOf`; until then the dashboard chose its source by itself); a release MusicBrainz does not answer in full (fewer tracks than its `track-count`, recordings without relationships – as `completeMedia` knows) gets no number (`gap.incomplete`); the release group's relationships count for the release (`release-groups+release-group-level-rels`); the page's own links first (a page with links but none of Discogs asks nothing); a failed Discogs request kept (an hour, a week for 404) and 2.5 s between the line's Discogs requests in every tab (`dci-gap-last`); old entries swept (`gapSweep`: Discogs credits after four weeks, all after thirteen, at most 300); the dashboard's number written once per import (at "Import complete" and the summary after it, `S.gapExactPending`, with the Discogs id – shown only for that release), not after staging or changes by hand; a release with Discogs notes says they are not counted (`gap.missingNotes`, `gap.noneNotes`); plural texts, the date in the browser's format, the line after `.releaseheader`, its text colour; the same credit once (`gapCreditsOf`); not started while the page goes on to the relationship editor.
- **Tests:** `t_start.py` new case `gapline` (the line and its parts, the dashboard's number, kept Discogs credits, ✕ and the number changing, the setting off, "Import credits …" and the number the dashboard keeps; after the review: the Discogs link handed over, the number with its Discogs id, the notes not counted); `t_ui_settings.py` reset: the keys of the line are release data, no settings. A request to Discogs broken off (the page left) is not kept as a failure.

## Import 3.38.18 · 2026-11-02

Field recordings, initials, cover and photo (collected items 182 – 184).

- **`TEXT.parse` (readClause, at its start):** rule **S064** – "Cover ©", "Cover art ©", "Cover image ©", "Cover painting ©", "Artwork ©", "Photo(s) ©", "Photograph(s) ©" + names: `Artwork` / `Photography By` with `roleCredit` "cover" / "photo"; a tail "detail used with permission", "courtesy" … into `ignored` (why `permission`). Rule **S062** – "<kind> recordings by X [year[–year]] [rest]" with a kind of `TEXT_FIELD_KINDS` (T057): `Field Recordings By` (R085) with `date` { by, ey }; the rest into the parts not recognized.
- **`byRoles`:** verbs one after another are each a role ("Recorded Mixed" → Recorded By, Mixed By; until 3.38.17 `byRole` made "Mixed By [Recorded]").
- **New `initialsOf(credits, artistNames)`** (S063, at the end of the parse): a name of two to four capitals (dots allowed) that are the initials of exactly one release artist or one name of the text with two words or more → that name, `credited` and `initials` the initials; of several → `initialsFor`.
- **`groupCredits`:** a role keeps `date` and `roleCredit`; the group `initials` / `initialsFor`; **`addCreditRows`:** `row.date` (open) and `row.roleCredit`; **`newPersonEntry`:** `initials`, `initialsFor`; **`entryNameHtml`:** new `initialsHtml(a)` (`.dci-initials`: `group.initials`, `group.initialsMany`).
- **Mapping:** new list `TEXT_FIELD_KINDS` (T057, editable).
- **Register:** rules S062, S063, S064, list T057.
- **Texts (English):** `ignored.why.permission`, `group.initials`, `group.initialsMany`.
- **After the independent review of block AT:** S062 – a name of several words without a year is whole (the rest only after a year; until then "Field recordings by Jane Roe" gave "Jane", a regression of R085), the years in order, an area after them "Recorded In" (`areaOf`); S064 – the tail only after a separator ("Focused" is no "used"), "all rights reserved", "by kind permission" and `TEXT_PC_STRIP` out, no name that is a sentence (`TEXT_NOT_NAME`); the role credit of the text kept as one typed (`roleCreditTouched`); initials stay as written (no S060 for `initials` / `initialsFor`), the names compared without case (`personCase`); register notes of S061, S062 corrected.
- **Tests:** `t_text_basics.py` new case `cloudpond` (all lines of "Cloud Pond Sky River" and more; after the review: a two-word field recordist, "Focused", "all rights reserved", "AJ"); `register_golden.json` anew (the rules and lists).

## Import 3.38.17 · 2026-11-02

A line "With …" of a text (collected item 181).

- **`TEXT.parse` (readClause):** new rule **S061** before S055 – a clause "With …" split at commas and and / & / und / et / y; music software (`isSoftware`, list T056) left out (`ignored`, why `software`); "Name on X" / "Name (X)" with instruments a guest (the roles with the detail Guest); an instrument or voice (`playable`) the release's artist's (`artistNames`: one – `addCredit`, several – `addPlaceholder`, offered to each); a name of two to four words in capitals a guest performer; words that may be instruments (`maybePlayable`) with `guess` when there are no more of them than instruments; the rest not recognized. Only when an instrument or a guest was found (else the clause is read as before).
- **Mapping:** new list `TEXT_SOFTWARE` (T056, editable: `EDITABLE_LISTS`); `INSTRUMENT_ALIASES` "sequential px", "sequential prophet x" → Sequential Prophet X, Prophet X, synthesizer; `PROPER_WORDS` "Sequential PX", "Sequential Prophet X".
- **Register:** rule S061, list T056.
- **Texts (English):** `ignored.why.software`.
- **After the independent review of block AT:** the parts of the line at commas outside brackets – a part "Name on A and B" or "Name (A, B)" one guest with all its instruments (until then the instruments after "and" went to the release's artist), the instruments right after a name his ("with Kenny Wheeler, trumpet"); software also by its start ("Apple Logic Pro"), a line only of software left out; no guest with a make of T052 before the name, no rule for a line with a colon; with several release artists words that may be instruments are not recognized (until then they were lost). (The clause is split at semicolons before, by `clauses`.)
- **Tests:** `t_text_basics.py` new case `withline` (after the review: a guest's two instruments, "Name, instrument", software by its start); `register_golden.json` anew (S061, T056, the aliases and proper words).

## Import 3.38.16 · 2026-11-02

Works of a track's composer (collected item 179, 179b, F-179b – F-179d).

- **New (main level, exported for Node):** `titleComposerNames(title)` (names in brackets – also "… cover" – or after "by" / "after", one to four words in capitals, version words left out; `{ name, full }`), `similarWorkTitle(trackTitle, workTitles, names)` (via `titleWithoutComposer`: the names – in brackets, after by / of / after, after a dash at the end – and all brackets out; equal within one letter, or the work's title whole in the track's title from two words or six letters). `normTitle` is a function now (until 3.38.15 a const – not reachable in Node before it).
- **New:** `titleComposersOf(i)` (a full name from `S.titleComposerCache`, a surname only when one artist of the release has it; logs `titleComposer` once per track and artist), `resolveTitleComposers()` (looks the full names up, `artist?query=artist:"…"`, an exact name or alias; at the start of `runArtistWorks`). `artistWorkTargets` adds them (`why: 'title'`).
- **`matchArtistWorks`:** per track its composers (`creditedWritersOf` and `titleComposersOf`); their works also by `similarWorkTitle` (names: theirs and their surnames); the hit's text `works.viaComposer` / `works.viaTitleComposer`, and `composer` / `composerName`, which `work-pick` keeps in the plan (`data-composer`, `data-composer-name`).
- **"co?":** new `performersOf(i)` (the release's artists, instrument / vocal / performer rows on the track) and `coverComposers(i, work)` (a planned work chosen with a composer who is none of them, "cover" not set, not a new work); `linkAttrsOpen` and `linkAttrsHtml` offer the pill (state `hint`, `matrix.coverOffer`); a click sets it as any attribute.
- **Texts (English):** `works.viaComposer`, `works.viaTitleComposer`, `log.titleComposer`, `matrix.coverOffer`.
- **After the independent review of block AR:**
  - "co?" only for a work found through its composer – a song by a similar title, or the composer named in the title (until then also a writer's work of the track's own title); the composers of a track are its writing roles only (`composersOfTrack`: composer, lyricist, writer, librettist – not arrangers); a work the search found too gets what the works of the artists know of it (`sameNamed`).
  - A similar title only when none of the composer's works has the track's title (`exact`); the cleaned titles once per names (`namePatterns` – the patterns of a set of names, a cache on the function, reachable in Node –, `similarCleaned`, `S.wtCache`, emptied with each import): a release of 50 tracks against 4,000 works no longer takes seconds each time.
  - `runArtistWorks`: the look-up of names in titles runs as part of the run (`S.artistWorksRunning` set before it; a refresh meanwhile runs it again after) – until then the works were read several times at once; `resolveTitleComposers`: `artist:"…" OR alias:"…"`, exactly one hit (two of the same name: none), an artist of the release of that name without a request, a failed request not kept, stopped when the works matrix rests; `titleComposersOf` logs only from the run (`logIt`), surnames only of writers, musicians and the release's artists; `S.titleComposerLogged` anew with each import.
  - `titleComposerNames`: more words that are no names (by, after, for, to, from, vs, ft, prod, session, title, credits, act, tribute, dub, skit, medley, prelude …, Roman numerals); no name after "produced / prod. / remix / mixed / arranged / edited / conducted / performed … by"; after "by" the words in capitals up to the first that is none ("Theme By Monk For Piano" → Monk); particles inside a name ("Ludwig van Beethoven"); "BY" in capitals too.
  - From 3.38.15: `setWorksList(i, open)`, `closeWorksList()` open and close the list in the page (no redraw: a click elsewhere closes it and does what it was on – until then the first click on "＋ New work" or the fold only closed the list); Esc only while a list is shown and no dialog is open; `S.mxWorksOpen` anew with each import; after **Link** the focus on the track's "remove" button.
- **Tests:** `t_works_more.py` new case `coverworks` (the three tracks, the log, "co?" and a click, Node: titleComposerNames and similarWorkTitle; after the review: a writer's own work without "co?", one comparison only, the titles that are no names); `workpick`: a click on "＋ New work" with a list open acts at once.

## Import 3.38.15 · 2026-11-02

The works found for a track as a choice (collected item 180).

- **`workFrontCell`:** with works found (`sameNamed(i)`: the search, the works of the artists) a button `[data-act=mx-works]` ("n works ▾", `matrix.worksPick`, `aria-expanded`, `aria-controls`) in the line of the track, right after the badge; the list (`.dci-same.dci-mx-wlist`, its id `dci-mx-wlist-<i>`) below the line, `hidden` while closed (until 3.38.14 always shown). New state `S.mxWorksOpen` (one track at a time).
- **`onClick`:** `mx-works` opens or closes it (the focus back on the button after drawing); a click outside the list and the button closes it; `work-pick` closes it. **Escape:** closes it, the focus on its button.
- **CSS:** `.dci-mx-wpickbtn` (yellow like the list), `.dci-mx-wlist` (shadow; `[hidden]` none).
- **Texts (English):** `matrix.worksPick.one` / `.other`.
- **Tests:** `t_works_more.py` new case `workpick` (the button in the line, hidden list, opened below the line, closed by a click elsewhere and Esc with the focus back, one at a time, a single work not set, Link plans it).

## Import 3.38.14 · 2026-11-02

Names in capitals (Q-a) and the head of a block (Q-c).

- **`personCase`:** in a name all in capitals (S060) a word of two letters with a vowel is written in normal case too (the minimum is 2 letters there, 3 in a name with words in normal case, S059, as until now); without a vowel it stays.
- **`emBlockHtml`:** the head is the block as MusicBrainz names it – one line: `roleLabel(r0)` (its text, its tooltip "from …: …"); several lines of instruments or voices: "n instruments" / "n voices"; several lines of another type: `mbPhraseOf(lt0)` with the source's roles of all its rows (not added by hand) in the tooltip (`role.fromSource`); then "· from n rows · n events" (until 3.38.13 "<source's role> → <MusicBrainz's>").
- **Tests:** `t_ui_head.py` capsnames D (personCase in Node: "AL DI MEOLA" → "Al di Meola", "DJ SHADOW", "MC SOLAAR", "MF DOOM", particles, "ED O'BRIEN", "J. DOE", "BMS", "Go KUROSAWA"); `t_entries.py` matrix ("3 instruments · from 3 rows", the tooltip) and companies ("recorded at", its tooltip "from Discogs: Recorded At").

## Import 3.38.13 · 2026-11-02

The surface (collected item 178, F-1, F-2, F-3).

- **`renderDates`:** the head (`.dci-pools-head`) is drawn last, after the body and the foot (or the pools kept in the bar) and the question of "Clear …" (`poolClearHtml`, until 3.38.12 below the head), in three parts – `.dci-pools-l` (the title button with `.dci-chev` ▲ open / ▼ folded – until 3.38.12 ▶ turned by CSS –, the counts, what is pending), `.dci-pools-c` ("▲ fold" / "▼ show"), `.dci-pools-r` (the tools); CSS grid `minmax(0, 1fr) auto minmax(0, 1fr)` (the fold in the middle), the rotation and the transition of `.dci-chev` gone; `.dci-pools-body` and `.dci-pools-kept` without their top margin (they open the block now).
- **Live comments:** `.dci-livecom-head` purple with white text (hover: darker, `:focus-visible`); `liveWhatText` returns `parts` in the order of medium and track (`{ at, media | tracks, n }`), `liveWhatLabel` joins them so – tracks one after another between media one part with "track(s)".
- **Footer:** `renderFootChips` gives the chip "stage-done" the class `dci-foot-chip-flash` once per text (`S.footFlashed`); `@keyframes dci-chip-flash` (0.9 s, once; none with `prefers-reduced-motion`).
- **After the independent review of block AQ:**
  - The flash class is taken off the chip at `animationend` (and after 1.2 s, for `prefers-reduced-motion`, where no animation runs), and out of `box.dataset.html` – drawn again (the dashboard closed and opened again, `display` back), the chip no longer flashes again; while it flashes, a footer drawn again keeps the chip's element (only the class differs).
  - `pools-toggle`: after `renderDates` the focus goes back to the same button (`.dci-pools-toggle` or `.dci-pools-fold`, `preventScroll`, then `scrollIntoView({ block: 'nearest' })`) – the line moved with the body.
  - `liveWhatText`: the parts sorted by medium and the index of the first track (`[medium, a]`; until now its `number`, which is "A1" on vinyl), a medium named whole first (`[from, -1]`).
  - README: the sentence of 3.37.15 ("▲ fold … right after the title") as history; the place of "keep the pools …" and of the question "Clear …?"; CHANGELOG likewise.
- **README:** its head names the version and the day again (it stayed at 3.34.2 · 2026-10-28).
- **Tests:** `t_ui_head.py` poolbar (the head the last line, the fold in its middle ±2 px, the arrow ▲ / ▼); `t_works_more.py` livegroup ("track 1.2, CD 2", "1.2, CD 2", the heading purple); `t_ui_view.py` foot (the chip flashes once: one `animationstart`, none after the dashboard is closed and opened again, the class gone after it).

## Import 3.38.12 · 2026-11-01

Names in capitals (F-4) and ⇅ in the dashboard (F-5).

- **New `personCase(n, { mixed, all })`** (main level; S059 for a name with words in normal case, as `normalCaseName` of the text adapter did – which calls it now –, S060 for a name all in capitals: every word of three letters or more with a vowel, without the rule for the first word) and **`personCaseOf(n)`** (`{ name, from }` by the rules switched on).
- **`groupCredits`:** a person's name (not a placeholder) by `personCaseOf` – `caseFrom` the source's spelling (or `who.caseFrom` of the text adapter, whose S059 came first) –, each name variation too (`anvFrom` of the role); **`newPersonEntry`, `applySupplement`:** the entry `caseFrom`; **`addCreditRows`, `suppRow`:** the row `anvFrom`. Text adapter `addCredit`: `who.caseFrom` when S059 changed the name.
- **Head:** new `mbCaps(a)` (linked to an all-capitals MusicBrainz name the source writes so: that name shown, `data-name` the entry's), `caseBackHtml(a)` ("↺ in capitals" / "↺ normal case", `data-act="case-back"`, `aria-pressed`), new `toggleCase(a)` (the name, the rows' `anv` and – taken as typed, `caseCredit` – their credit; back: `sourceCreditFor` when linked, else the spelling); after the import the log `caseNormal`; `rulesOfRow` names S060 at its rows (instead of S031 for a spelling that differed only in its case, "VALFAR").
- **⇅ (S058):** `TEXT.parse(text, ctx0)` reads a text with blocks whose order was not clear once more the other way round (`noAlt`) – `stackAlt` (its credits of those blocks), `stackAltUnrec` (its lines not recognized); `toRelease`, the Bandcamp adapter (with the track pages' lines) and `addNotesCompanies` (notes: Discogs's entry of a name, `fromNotes`) pass them on; the import keeps `S.stackCur` / `S.stackAlt` / `S.stackAltUnrec`. New **`flipStacks()`** (`stack-flip`; until 3.38.11 `loadRelease` again): the rows `stackAmbig` out, those of the other reading in (`groupCredits` → the entry of the same Discogs id or name, else `newPersonEntry`, `resolveArtists` for the new ones), entries left without a row out, the readings and the lines not recognized swapped; without the other reading (an import of before) as until now. The row building of `loadRelease` moved to **`newPersonEntry(g)`** and **`addCreditRows(artist, g, rel, source, leftOutKeys)`** (unchanged).
- **After the independent review of block AP:**
  - ⇅ and "remember per release": `flipStacks` takes the rows it removes out of `S.freshRows` and adds those it makes (as the import would note them); the snapshot keeps `stackUp` (new `rememberedStackUp(src)`: a new import of a release remembered with ⇅ reads it so again) and the entries `caseUp` (restored with `setCaseUp(a, true, false)`).
  - A credit of lines whose order was not clear is a row of its own (`groupCredits`: `|stack` in the role's key) – ⇅ never takes a clear credit of the same role with it (the same relationship of both is staged once, `seen`). `flipStacks` hides new rows of the "about" text / the notes left out and puts those switched off at the source on Skip (S046 not again).
  - The notes' other reading goes through `addNotesPersons` (on a copy of the release's credits, `{ quiet }`): a credit Discogs lists already gives no second row. Bandcamp: the other reading of the "about" text and of each track page too (their lines not recognized by track page).
  - Bandcamp (strict names): the exact match and the spelling check compare the source's spelling (`caseFrom`), not the one in normal case.
  - New `caseSpellingOf(a)`: a name or a spelling of its rows in capitals (until now only the name) – "↺ in capitals" for "LAKE" too, the log names the spellings; `setCaseUp(a, up, rows)` (from `toggleCase`) leaves a "credited as" typed by hand alone; `mbCaps(a)`: any MusicBrainz name all in capitals ("MF DOOM"), and `sourceCreditFor` then takes the source's capitals ("DOOM", not "Doom").
  - `personCase`: a particle between the names of a name all in capitals small ("PACO DE LUCÍA" → "Paco de Lucía", first: "De la Soul"), signs before or after a word kept ("SMITH, JOHN" → "Smith, John"), vowels of other scripts ("ЕГОР ЛЕТОВ" → "Егор Летов"); exported for Node.
  - From 3.38.10: the preview names text attributes the phrase does not have again ("task: “cover”"); `roleLabel` names a supplement's own source (`suppName`) and nothing for a row added by hand; "Credited as for all roles" for series and events; `rowShort`, "Row removed", `em.tickNo`, `em.levelKept`, an E4 chip without its instrument ("instruments") and the chip's tooltip ("from Discogs: …") by MusicBrainz's names.
- **Register:** rule S060 (rules window, "special"); S059's place.
- **Texts (English):** `case.back`, `case.backTitle`, `case.normal`, `case.normalTitle`, `log.caseNormal`, `log.caseUp`, `log.caseDown`; changed: `stack.flipTitle`, `log.stackFlipUp`, `log.stackFlipDown` (no "read again").
- **Tests:** `t_ui_head.py` new case `capsnames` (Discogs names in capitals, ABBA linked to "ABBA", "LAKE", the log, ↺ in capitals and back with the credit); `t_text_basics.py` stacked: ⇅ without a new import, Max Mix put on Skip stays, "ABBA – piano" → Abba; `register_golden.json` anew (the texts' `stackAlt` / `stackAltUnrec`, the section "special" with S060); `t_text_languages.py` nordic and `t_text_basics.py` textcredit: "VALFAR", "KUNST MANN", "JOHN DOE" in normal case from the start (S060 at the rows); `t_text_basics.py` new case `stackflip` (a clear and an unclear credit of one role, ⇅ and back, ⇅ and imported again, the notes with a credit Discogs lists); `capsnames` C ("LAKE", "MF DOOM", a credit typed by hand).

## Import 3.38.11 · 2026-11-01

Spellings and "credited as" (collected items 175, 176).

- **New `commonSpelling(a)`:** the name variation all rows of an entry from the source carry ("*" left out), else ''. **`releaseSpelling(a)`** shows only that one (until 3.38.10 the most frequent one of its rows; `others` stays empty).
- **New `creditAllHtml(a)`** (from `variantsHtml`): the field for all roles, prefilled with `commonSpelling` (until 3.38.10 `anvs[0]` when the entry had one name variation); persons `group.creditAll`, companies (labels, places, areas) `group.creditAllOther` – their head gets `.dci-variants.dci-variants-co` with it (until 3.38.10 none); the list: its names (companies) or `artistVariants`.
- **`creditChipHtml`:** one credit not on all rows that are not on Skip: `group.creditedAsFor` with the names of those rows (`rowPhrase`; two, then "…").
- **`artist-credit-all`:** the rows `creditTouched` (until 3.38.10 `syncSourceCredits` set a linked entry's rows back to the source's spelling).
- **E4:** a column `.dci-em-c-ac` "Credited as" (`em.colAc`) after the role credit – `data-f="em-ac"` (the line's `credit`, `creditTouched`; on input and on change; the list `dci-ac-<entry>`); `cols` + 1. A spelling of its own is a line of its own already (`lineKeyOf` has `credit`). `emChipHtml`: `.dci-em-chipas` "as “…”" with the line's credit.
- **Texts (English):** `group.creditAllOther`, `group.creditAllOtherAria`, `group.creditedAsFor`, `em.colAc`, `em.acLabel`.
- **Tests:** `t_ui_head.py` new case `spellings` (Oliver Lake as on "Boston Duets": head, chip, field, column, own line, compact chip, lines joined, "for writer"; Carl Allen "C. Allen*" in all roles; the place Abbey Road Studios: "Credited as for all roles", set for all); `entryhead` reads "as “Bassman” for bass" (one row of two).

## Import 3.38.10 · 2026-11-01

The names of MusicBrainz everywhere (collected item 177).

- **New `linkPhraseOf(lt, level, values, enteredFirst, plain)`** (main level; exported for Node): the reverse link phrase when the level is the type's second entity (artist → recording), else the forward one (of one kind on both sides: the reverse one when the page's entity was entered first; `plain`: the reverse one), its placeholders `{name}`, `{name:text}`, `{name:text|otherwise}` and `%` filled from `values` (root attribute name → values; several "a, b and c"), spaces squeezed.
- **New `mbPhraseOf(lt, row, attrs)`:** the staged attributes (`{ type, text_value }`) by the name of their root attribute → `linkPhraseOf`. **New `rowPhrase(row)`:** `buildAttrs` of its current type (on Skip: the type it had, on the level of that type); when that fails (an instrument or voice MusicBrainz does not know, a flag not allowed), the typed instrument as the value of the type's root attribute and the flags the type allows. **New `roleLabel(row)`:** `{ text, title }` – the phrase, the title "from {source}: {raw}" (`role.fromSource`; the supplement's source for its rows); without a type the source's role and "→ no type".
- **`roleCell`:** `.dci-drole` with the phrase, `data-raw` the source's role, the title; the refresh of a row keeps text and title in step. **`typeCell`:** options `mbPhraseOf(l, row) || l.name`, `data-name` the type's name.
- **E4:** `.dci-em-role` the phrase (`data-raw`, title; "→ no type" only without a type); `emChipHtml` names a row that is not of a root attribute by `rowPhrase`; the head of a block "→ mixer", "→ instruments" (`mbPhraseOf(lt0)`); compact by role: the chip only ("→ no type" without a type; until 3.38.9 "→ type" after each chip).
- **Compact line (`clineHtml`):** `.dci-cl-role` the phrase (`data-raw`, title; until 3.38.9 the source's role, then "→ type · instrument"); `.dci-cl-type` only "→ no type" (`ltOf`: a row on Skip keeps its type) and the role credit.
- **`renderPreview`, `describeItem`** (log "Staged: …", "Date added …", the lists of the result): the phrase with the item's attributes (a joined relationship with all its instruments: "piano and organ"; a link recording → work "recording of").
- **Works matrix:** `roleCode(typeName, sub, label)` – with "names" the label (" (sub)" added only when it does not say so); new `workTypePhrase(name, entityType, attrNames)` for the relationships already in MusicBrainz and the dates added to them; the chips' tooltips, the column head and its tooltip by `rowPhrase`; the cell menu's roles by `mbPhraseOf`, "sub" by `linkPhraseOf` with `sub` ("sub-publisher").
- **Log:** `emOut`, `emIn`, `emOrder`, `matrixColumn`, `manualAdded` name the row by `rowPhrase`. Messages and questions about a credit of the source (`srcOff`, `dgFocus`, `typeAsk.*`, `matrix.liveWhy.*` …) keep the source's role.
- **Texts (English):** `role.fromSource`.
- **Tests:** new `tools/mb_link_types.py` writes `smoke/mb_link_types.json` – MusicBrainz's 698 relationship types (names and phrases from `po/relationships.pot`, entity types and parents from `t/sql/initial.sql` – 427 of them; the newer ones without), 126 attributes; from metabrainz/musicbrainz-server bade3a5 (2026-10-21). `t_register.py` D): every corpus role's name by the first of its types MusicBrainz has between an artist and its level (golden `node.phrases`: type, ids, name; a type without known entity types lists all of that name). `harness.py`: instrument and vocal with MusicBrainz's phrase, the bare form the type's name (`PHRASE_OF`: "{additional} {guest} {solo} {instrument:%|instrument}" – rows are named by their instrument, the list of types reads as before); `t_ui_view.py` compact, ui301, clineask read the new compact line (clineask with MusicBrainz's conductor type); `t_mapping.py` new case `mbnames` (MusicBrainz's phrases for all types of the test page from that file, the attribute "re"; rows, tooltip, types, compact line, preview, entry matrix, works matrix and its menu, log). 13 more test files read the source's role from `data-raw` of `.dci-drole` instead of its text.

## Import 3.38.9 · Companion 1.10.0 · 2026-11-01

Several imports at once (collected item 173).

- **Companion – storage per release, a beat per page:** `statusMap:<mbid>` (until 1.9.2 the map shown was the one `statusMap` of all; the per-release copy was only for "Keep marks" and the release page), `statusBeat:<mbid>:<page>` (was one `statusBeat`; one per page, so that two editors or an editor and the release page of one release do not overwrite each other's beat) with `used` (when the page was last in front and worked with: `focus`, `pointerdown`, `keydown`, `visibilitychange`; not on every beat – two tabs of a split view are both visible), `site` and `releaseId` (of its map), `statusPing` `{ key, ts }` after each change; `mapKey(map, pageId)` (`mbRelease`, else `page-<id>`), `pingStatus(key)`, `beatKeys(key)`, `dropBeats(key)`; `keepPerRelease(map, key)` also removes the maps and beats of releases dropped from the index (30); the old `statusMap` and `statusBeat` are deleted once.
- **Companion – `initMusicBrainzSide`:** `status-map` → `keepPerRelease` + beat + ping (no `statusMap` any more); a use of the page (`markUsed`) beats and pings at once (at most once a second) – the Discogs tab follows the import worked with; `pagehide` → its beat deleted and a ping (the map stays for "Keep marks"); `forget-release` removes the map and all beats of the release; `fromDiscogs` messages of another release (`mbRelease`) are not passed on; each `status` message carries `version` (`COMPANION_VERSION`; no message of its own – a dashboard opened later knows it too).
- **Companion – `initSourceSide`:** new `alive`, `liveReleases()` (one pass over the stored beats: per release the newest beat and the latest use, for this page's site and release; beats long gone are deleted), `liveMaps()` (the maps of those releases for this page's release, the one used last first – a map switched off counts too, so that another import's marks are not shown instead), `showMulti(n, map)` (`#dci-multi`, the dashboard's label `multi`), `current()`; `showMap(force)` draws only when what is shown changed (signature with `mbRelease`); listens to `statusPing` (was `statusMap`); the check every 3 s and after 1.5 / 4 s stay; `senderAlive` and `isHere` removed; messages back carry `mbRelease`.
- **Companion – `lineOf(el, role)`:** never takes the table cell as the line (it holds every credit of the track: "Written-By – Bass*" of an artist also in "Flute – Bass Man" put its mark before the title); stops at the cell, at more than 400 characters and at an `li`.
- **Companion – `initReleasePage`:** its map is that of its release (`statusMap:<mbid>`), its beat its own (`statusBeat:<mbid>:release-<mbid>`, with `used`, `site`, `releaseId`); the checked map → `statusMap:<mbid>` + ping; `pagehide` → beat deleted + ping.
- **Import:** `onFromDiscogs` takes `version` from `status` (`S.sync.companionVersion`); 6 s after the first `status` without a version: log `companionOld` (warn) and message `msg.companionOld` (`COMPANION_NEEDED` = 1.10.0); the status map's labels have `multi` (`dgStatus.multi`).
- **Texts (English):** `dgStatus.multi`, `log.companionOld`, `msg.companionOld`.
- **Tests:** `t_companion_discogs.py` new case `multi` (two other imports send their status every 2 s: the marks on the Discogs tab stay 10 s – with companion 1.9.2 none; the dashboard opened 8 s after the page: no "older companion"; the same release in another import used later: its marks and the note, a click there does not reach the first; the first used again: its marks, a click reaches it; closed: the note goes); `trackcells` with "Written-By – Bass*" of the same artist in the same cell; `t_companion_bandcamp.py` new case `multibc` (this dashboard imports a Bandcamp album, two other editors a Discogs release and another one: for 10 s the marks on the Bandcamp tab and the Discogs tab stay – with companion 1.9.2 both go); `relcheck`, `t_release.py`, `t_works_matrix.py` read the status of the release (`statusMap:<REL>`, `statusBeat:<REL>:release-<REL>`).

## Import 3.38.8 · Companion 1.9.2 · 2026-11-01

The tracklist of Discogs no longer broken by status marks (collected item 174). The import changes only its version.

- **Companion `lineOf(el, role)`:** climbs at most to the closest `td`, `th` or `li` (was: on to the table row); without the role there, that cell or item (was `closest('li, tr')`).
- **Companion `findCreditAt(cmd, position)`:** a link of the artist in the track's row counts only on a line with the role (score 3); without one, no mark on that track (before: score 1, and its line was the row).
- **Companion `renderStatus` (`place`):** never inserts a mark into `tr`, `tbody`, `thead`, `tfoot` or `table`.
- **Tests:** `t_companion_discogs.py` new case `trackcells` (a tracklist as a table with credits on tracks: marks before "Flute – Bass Man" and "Composed By – Writer Z" inside the cell, none for "Lyrics By" where the page shows only "Written-By"; no mark in a row, three cells each). Fails with companion 1.9.1 (a mark as the first child of the row, four cells).

## Import 3.38.7 · 2026-10-31

Names above (or below) their instruments, names in capitals (collected item 167; rules S058, S059).

- **`TEXT`:** new `normalCaseName(n)` (S059: an all-caps word of three letters or more with a vowel beside a word with small letters, first in the name from four letters – `-` and `'` parts each capitalized); `addCredit` gives it to the credits of persons (not to companies). `parse` takes `stackUp`; new `STACK_PARTICLE`, `stackInstr(raw)` (no digit, `:`, brackets, `by`/`at`/…; every part of `splitRoles` `playable`), `stackName(raw)` (2 – 4 words starting in capitals or a particle between them, `looksLikeName`, no sign, no word `playable` or a role, no `TEXT_PLACE_WORDS`, not `creditLike`, not `TEXT_IGNORE_LINE`), `stackPairs(lines)` (S058: runs of N/I lines with both kinds; `pair('N','I')` and `pair('I','N')`; wholly paired one way → that way, else ambiguous → `stackUp` decides; → Map index → `{ name, instr, up, ambig, lines }` and the other line → null), `readStacked(pr)` (`startLine` with "line / line", a credit per part with `stacked` and `stackAmbig`). The main loop goes through `allLines` with their indexes: a line of a pair flushes the block of S051 and is read with its pair.
- **Core:** `sourceContext().stackUp` (`S.stackUp`); `groupCredits` carries `stackAmbig` to the role, the row gets `row.stackAmbig`; after "Import complete" the log `stackAmbig` / `stackAmbigUp` (warn) with the names; new `stackNoteHtml(rows)` (`.dci-stack-note` in `groupHtml` after `coverFromEntryHtml`: `stack.noteDown` / `stack.noteUp`, button `data-act="stack-flip"`, rule id S058); case `stack-flip` (`S.stackUp` toggled, log `stackFlipUp` / `stackFlipDown`, `loadRelease` of the same release – with its question); `loadRelease` sets `S.stackUp` false for another release or text.
- **Register:** S058, S059.
- **Texts (English):** `log.stackAmbig`, `log.stackAmbigUp`, `log.stackFlipUp`, `log.stackFlipDown`, `stack.noteDown`, `stack.noteUp`, `stack.flipUp`, `stack.flipDown`, `stack.flipTitle`.
- **Tests:** `t_text_basics.py` new case `stacked` (the example; the instruments above; not clear – the note, the log, ⇅ and back to another text; one line with S059 – "KUROSAWA Go", "DJ Shadow", "ABBA", "BMS Illustration"; the Discogs notes); `register_golden.json` written anew (UPDATE=1): only the section "Special handling" gained S058 and S059.

## Import 3.38.6 · 2026-10-31

ⓘ at a chip (collected item 163b).

- **New** `chipNoteText(r)`: the notes of a row whose answer is applied, a line each – `instrGuess` (`instrGuess.none`; `instrGuess.chosen` / `instrGuess.noneOr` with the instrument, `instrGuess.other` or `instrGuess.misc` chosen; with `guessNoteHtml` the spelling `instrGuess.typo` / `instrGuess.own`), `caseNoteHtml` (`caseNote.small` with `caseNote.word`, `caseNote.kept`), the type answered (`typeQuestionFor`, new text `em.chipNoteType`), `voiceCreditHtml` (`voiceCredit.from` + `voiceCredit.use`).
- **`emChipHtml`:** without a question (`ask`), `span.dci-em-chipinfo` "ⓘ" (`role="img"`, `tabindex="0"`, the notes as `title` and `aria-label`) right after `.dci-em-chipname`.
- **CSS:** `.dci-em-chipinfo` (grey, `cursor: help`), its `:focus-visible`.
- **Texts (English):** `em.chipNoteType`.
- **Tests:** `t_entries.py` new case `chipinfo` (no ⓘ while asking; "Buddha Machine" none is like it; taishōgoto chosen – three notes; double bass none; "Directed By" conductor).

## Import 3.38.5 · 2026-10-31

"Developer mode" (collected item 171).

- **New** `DEV_KEY` (`dci-dev`, off), `DEV_OLD_KEYS` (`dci-log-diag`, `dci-stats-dev`: when one is stored, `DEV_KEY` is set to true if one of them was true and `DEV_KEY` was not stored; both removed), `S.devMode` – in place of `LOG_DIAG_KEY` / `S.logDiag` (3.36.2) and `STATS_DEV_KEY` (3.38.2), both removed.
- **`renderLog`:** "Start diagnosis" with `S.devMode`. **`statsHtml`:** the switch `stats-dev` removed; `statsDevHtml` with `S.devMode`. **Settings → General:** `data-set="dev-mode"` (`settings.dev`, `settings.devTitle`) in place of `log-diag`. **`settingsChange`:** `dev-mode` (stored, a running diagnosis stops when off, the log redrawn) in place of `log-diag` and `stats-dev`.
- **Reset:** `TOPIC_KEYS.general` with `DEV_KEY`, `TOPIC_KEYS.statistics` without `STATS_DEV_KEY`; `resetTopic('general')` and `resetSettings` set `S.devMode` false; `SETTINGS_KEYS` with `DEV_KEY` in place of the two.
- **Texts (English):** new `settings.dev`, `settings.devTitle`; removed `settings.logDiag`, `settings.logDiagTitle`, `stats.dev`, `stats.devTitle` (all languages).
- **Tests:** `t_ui_settings.py` `logdiag` ("Developer mode", `dci-dev`; new E: taken over from `dci-stats-dev` or `dci-log-diag` true, not from false; the old keys gone) and `statsdev` (shown in Developer mode, no switch of its own) adapted.

## Import 3.38.4 · 2026-10-31

The footer compact (collected item 169).

- **Markup** (`buildOverlay`): `footer.dci-foot` holds `[data-el=livecom]` (first), `.dci-foot-bar` (`.dci-jump`, `[data-el=sum]`, new `[data-el=foot-chips]` with `role="status"`, `.dci-foot-actions`: panic, `[data-act=preview]` with `footer.previewShort` and the old text as tooltip, new `.dci-foot-opts[data-el=foot-opts]` – button `[data-act=foot-opts]` "⚙ Options ▾" and `#dci-foot-optlist` with the three checkboxes (short labels `footer.editNoteShort`, `footer.fillShort`, `footer.capShort`; the long texts in `title`, the cap's label `[data-el=cap-check]`) –, `[data-act=apply]`, new `.dci-foot-info` ⓘ with `footer.hint`), then `[data-el=rounds]`, `[data-el=waiting]`, `[data-el=stage-done]` (no `role="status"` any more – the chips have it); `p.dci-hint` removed.
- **New** `FOOT_MSGS`, **`renderFootChips()`** (`S.footMsgs` – `rounds`, `waiting`, `stage-done`: `{ text, chip }` –, the chips `button.dci-foot-chip.dci-foot-chip-info|warn|ok[data-act=foot-msg][data-msg]` with the text as `title`; the paragraph of `S.footMsgOpen` shown with its text, the others hidden), **`setFootOpts(open)`** (`S.footOptsOpen`, `.dci-open`, `aria-expanded`).
- **`refresh`:** the rounds and the waiting tracks into `S.footMsgs` (`footer.chipRounds`, `footer.chipWaiting`), then `renderFootChips()`; the summary in one line – `strong.dci-sum-new` with the levels as `title` (and `tabindex="0"`), the parts joined by `span.dci-sum-sep` " · " (was `<br>`). **`applyPlan`:** what was staged into `S.footMsgs['stage-done']` (`footer.chipDone`, the time of `msg.stageDone`). **`syncSharedSwitches`:** `footer.capShort` and the cap's tooltip.
- **Handlers:** `onClick` closes "⚙ Options ▾" on a click outside `.dci-foot-opts`; cases `foot-opts`, `foot-msg`; Escape closes "⚙ Options ▾" first (focus back on its button); `S.footOptsOpen = false` when the overlay is built.
- **CSS:** `.dci-foot` a column with `container-type: inline-size`; `.dci-foot-bar` (flex, wrap), `.dci-sum-new[title]`, `.dci-sum-sep`, `.dci-foot-chips`, `.dci-foot-chip` (`-warn`, `-info`, `-ok`), `.dci-foot-actions` (`margin-left: auto`), `.dci-foot-opts`, `.dci-foot-optbtn` (hidden), `.dci-foot-optlist`, `.dci-foot-info`; `@container (max-width: 1099px)`: the button shown, the list a box above it (`.dci-open`); `.dci-rounds`, `.dci-waiting`, `.dci-stage-done`, `.dci-livecom` without margins; `.dci-hint` and `.dci-livecom-full` (3.38.3) removed – `renderLiveComments` no longer sets it.
- **Texts (English):** `footer.previewShort`, `footer.editNoteShort`, `footer.fillShort`, `footer.capShort`, `footer.options`, `footer.optionsTitle`, `footer.chipRounds`, `footer.chipWaiting.one/.other`, `footer.chipDone.one/.other`.
- **Tests:** `t_ui_view.py` new case `foot` (1500 px one line ≤ 60 px, the summary, the levels, the chip and its message, the short checkboxes and their tooltips, Stage and ⓘ at the right; 900 px two lines, "⚙ Options ▾" above, ticked there, closed by a click elsewhere and Esc; 600 px Stage whole; staged: the chip "✓ 30 in the editor"; in the page one line at the bottom); `t_dates_matrix.py` `dragdates`: the date dropped onto Keys Guy with `drag` (from the middle) – with the lower footer its field lay near the bottom edge, where the dashboard scrolls while dragging; `t_rules_window.py` `rowrules` and `t_notes_companies.py` `facets` click the rule id and "new work" in the page – the row and the button may now lie below the log window of the test, and Playwright would scroll before its click.

## Import 3.38.3 · 2026-10-31

The comments of live recordings in short and in groups (collected items 168, 170).

- **New** `liveWhatText(idxs)` (with `multiMedium()`: whole media – every chosen track with a recording live – in runs of the same format from `S.mediaInfo` ("CD 1–5"; without a format `livecom.medium`); the other tracks as ranges of the list's positions (`medium.number` with several media); returns `{ media, tracks, n }`), **`liveWhatLabel(idxs, { prefix })`** (media, then `livecom.tracksPart` or the bare ranges), **`liveGroups(list)`** (key `1|rec` for a proposal with `warn`, `other`, `same` or `pending`, else `g|on|text`; in the order of the tracks).
- **`renderLiveComments`:** the offer `livecom.offerMedia` when media are named, else `livecom.offer` with the ranges; the list is a `div.dci-livecom-box` (no `<details>` any more) – `.dci-livecom-body` (`max-height` a third of `S.overlay`'s height, at least 120 px) above `.dci-livecom-headrow` with the button `.dci-livecom-head` (`data-act="livecom-toggle"`, `aria-expanded`); a group is `tr[data-livecom-group=recs]` (checkbox and text with `data-recs`, button `data-act="livecom-group"`), its tracks `tr.dci-livecom-sub[data-livecom]` while `S.liveComGroupOpen` (Set, first recording) has it; the element gets `.dci-livecom-full` whenever the list is shown (a line of its own, open or folded).
- **Handlers:** `livecom-on` / `livecom-text` set each recording of `data-recs` (or `data-rec`); new cases `livecom-toggle` (`S.liveComOpen`, focus back on the heading) and `livecom-group`; the `toggle` listener of the old `<details>` removed.
- **CSS:** `.dci-livecom-full`, `.dci-livecom-box` (flex column; folded: `width: fit-content; margin-left: auto`), `.dci-livecom-body` (`overflow: auto`), `.dci-livecom-headrow`, `.dci-livecom-head`, `.dci-livecom-sub`, `.dci-livecom-gbtn`; `.dci-livecom-box > summary` removed.
- **Texts (English):** `livecom.title` "Live disambiguation comments: {n} of {m}" (de/es/fr of the old wording removed), new `livecom.medium`, `livecom.tracksPart.one/.other`, `livecom.offerMedia`, `livecom.groupN.one/.other`, `livecom.groupOnAria`, `livecom.groupTextAria`.
- **Tests:** `t_works_more.py` new case `livegroup` (two media: "CD 2, track 1.2"; one group of three, its text and tick for all; the heading last, at the right, below the list, at the same place folded; the list ≤ a third of the dashboard); `livecom` (the group "2–3 · ▸ 2 tracks", the heading) and `liveoffer` ("Tracks 2–4") adapted.

## Import 3.38.2 · 2026-10-31

The developer statistics (E8).

- **New** `STATS_DEV_KEY` (`dci-stats-dev`, off), **`statHand(row)`** (compared with `S.freshRows` / `rowFieldsOf`: `type` – only after `row.statTypeHand` –, `instrument` / `level` – touched and no answer –, `roleCredit`, `artistCredit` – touched –, `tracks` – not with a date of the matrix –, `attributes` (`flags`), `date` – by hand, not of the matrix –; `added` for `row.manual` or a row not in `S.freshRows`), **`statAnswers(row)`** (`{ q: 'guess', a: 'similar' | 'typo' | 'same' | 'other' | 'misc' }`; `{ q: Q…, a: the instrument }` when `primaryText` is one of the question's options; `{ q: Q…, a: the type }` with `typeAnswer`), **`statUnrec()`** (the words in “…” of `unrecognized`, else the line – of the source and the supplement –, roles with `unknownRole`, `instrGuess.word`; in small letters, 200 at most), **`statDev(recs)`** (per relationship with `h`; `unrec` and `dupes` once per release), **`statsDevHtml(recs)`** (`.dci-stats-dev`, boxes `stats-dev-auto`, `-rules`, `-unrec`, `-answers`, `-dupes`).
- **`statSnapshot`:** per relationship `h`, `q`; the record `dev: { unrec, dupes }` (`dupes`: rows with `existingAll`).
- **Handlers:** `case 'type'` sets `row.statTypeHand`; `data-set="stats-dev"`. `TOPIC_KEYS.statistics` and `SETTINGS_KEYS` with `STATS_DEV_KEY`.
- **Texts (English only):** `stats.dev`, `stats.devTitle`, `stats.dev.*`.
- **Tests:** `t_ui_settings.py` new case `statsdev`.

## Import 3.38.1 · 2026-10-31

The further statistics (E8).

- **New** `statMore(recs)` (per submission in time order: sources, supplements, weekday and hour of the relationships, relationships per day and per release, the fastest per relationship from 5 at once; the release at its first submission: decade, formats, country, labels; text from cover art; own rules – the newest `own`; per relationship: how its entity was found – each `tg` once –, dates, places, levels, works, the first use and the count of each instrument, rules `U…`), `statStreaks(days)` (now – ending today or yesterday –, the longest), **`statsMoreHtml(recs)`** (boxes `.dci-stats-card[data-el=stats-<key>]`: sources, found, dates, levels, releases, when, instruments, ocr, own; bars `.dci-stats-cols`); `statsHtml` shows it below the top lists.
- **`statSnapshot`:** `own` = `userRules().length`.
- **CSS:** `.dci-stats-cards`, `.dci-stats-card`, `.dci-stats-kv`, `.dci-stats-cols`, `.dci-stats-col`, `.dci-stats-colbar`, `.dci-stats-collbl`.
- **Texts (English only):** `stats.more.*`, `stats.withSupp`, `stats.src.*`, `stats.found.*`, `stats.dated`, `stats.prec.*`, `stats.dsrc.*`, `stats.places`, `stats.works`, `stats.decade`, `stats.format`, `stats.country`, `stats.label`, `stats.weekdays`, `stats.hours`, `stats.streak`, `stats.rec.*`, `stats.instrN`, `stats.instrNew`, `stats.instrOnce`, `stats.ocr.*`, `stats.own`.
- **Tests:** `t_ui_settings.py` new case `statsmore` (records stored in IndexedDB, helpers `STAT_SEED`, `stat_rel`).

## Import 3.38.0 · 2026-10-31

Milestone "Statistics" (E8): collected when MusicBrainz confirms a submission, shown in ⚙ Settings → Statistics. (Checked before the commit by a separate review; its findings are fixed: relationships MusicBrainz had, the time until the confirmation, nothing to look up, the lock, old jobs, removed or undone ones, the time per release.)

- **New (all pages of a release, before the dashboard):** `STATS_ON_KEY` (`dci-stats-on`), `STATS_PERIOD_KEY` (`dci-stats-period`), `STAT_JOB_PREFIX` (`dci-stat-job:<MBID>`), `STAT_JOB_MAX_MS` (30 min), `STATS_DB` (IndexedDB `dci-stats`, store `subs`, keyPath `id`); `statsOn()`, `statDb()`, `statStore()`, `statPut` / `statAll` / `statClear`; `STAT_FRESH_MS` (2 min); **`statCount(c, data, recs)`**, **`statSeenAll(rels, data, recs)`** (a new relationship on the release – `data.relationships` – or on a recording: there when MusicBrainz has more of its `linkTypeID` to its target gid than `c.n0`, one more for each new one of the same kind; `null` for what cannot be looked up there); `statJobsSweep()` (jobs older than 30 min go, of every release); **`runStatJob(mbid, { tries, final, logFn })`** (like `runLiveJob`: `/ws/js/release/<mbid>?inc=rels recordings`, 3 s apart; kept when every one that can be looked up is there, at the last try what is there, with none to look up on the release page within `STAT_FRESH_MS` of "Enter edit" at once; the record without `c`, `id` = `<mbid>:<armedAt>` – written twice it stays one –, `at`, `ms` = confirmation − `start`: now on the editor's page, `performance.timeOrigin` of the release page shown within 2 min, else `armedAt`; log `statsKept` / `statsFailed` through `liveLog`); **`initStatJobArm(mbid, snapshot, logFn)`** (the submission of the form with the edit note or a click on its submit button; not when `statsOn()` is off; the job `{ armedAt, rec }` – not stored: log `statsJobFailed` –, then `runStatJob` with 30 tries). `initReleasePageHook` runs `runStatJob(mbid, { tries: 5, final: true })`.
- **New (dashboard):** `statAttrRoot(typeId)`, `statLinkOf(a)` (`link` / `search` / `hand` / `created`), `statDatePrec(d)`, `statDateSrc(row)` (`notes`: a pool date found in the notes or the text; `hand`), `statSourceKind()` (`ocr` for the text from cover art), `statSuppKinds()`, `statOcrInfo(text, supp)` (images read, lines, words not as read), `statReleaseInfo(ws)` (title, year, country, formats, labels, `before`: the relationships of the release and its recordings without URLs), `statFill(state, row, source)` (`S.statFills`), **`statSnapshot()`** (the states of `S.staged` – `k: 'n'` – and of `S.statFills` – `k: 's'` – still in the editor, `findRelationshipStates`, not `_status` 3 and no supplement with `_status` 0; `statExisting(re.state)` – the relationships with positive ids per "source|type|target", both directions – gives `c.n0`; per relationship `lt`, `lv` (the source's entity type), `et`, `tg`, `tn`, `i` (instruments), `v` (vocals), `d` (date precision), `ds`, `rc`, `ac`, `ru` (`row.ruleId`), `lk`, `nw`, and `c` to look it up; the record `{ v: 1, mbid, start, rel, src, supp, ocr, rels }`), `statPeriodKey(ms, period)` (day, ISO week, month, year; local time), **`statAgg(recs)`** (`perRelease`: the times of a release's submissions together, per release; before / empty from its first record with `rel`), `statTop`, `statPct`, `statDur`, `statNum`, `statsLoad()`, **`statsHtml()`**.
- **State `S`:** `statFills` (Map), `statStart` (the first `initOnce` of the page), `statRel` (in `init`, after `indexExistingRelationships`), `statOcr` (`ocrImport`), `statsPeriod`, `statsData` (null: read again – when ⚙ opens or the tab is chosen), `statsLoading`, `resetKeepStats`.
- **`applyPlan`:** `statFill` in the branches `attrFill`, `fillDate` and `fill`.
- **Settings:** `SETTING_TOPICS` with `statistics` before `connections`; `TOPIC_KEYS.statistics` (the switch, the period); `SETTINGS_KEYS` with both; `bodies.statistics`; `data-set="stats-on"`; `case 'stats-period'`, `case 'stats-delete'` (confirm, `statClear`); `resetTopic('statistics')`. **Reset all:** `reset-keepstats` (ticked; `S.resetKeepStats` kept across redraws in `settingsAfterEvent`), `resetSettings({ …, stats })` deletes them only unticked (log `statsDeleted`).
- **CSS:** `.dci-stats-tiles`, `.dci-stats-tile`, `.dci-stats-num`, `.dci-stats-lbl`, `.dci-stats-h`, `.dci-stats-table`, `.dci-stats-bar`, `.dci-stats-lists`, `.dci-stats-list`.
- **Texts (English only):** `settings.t.statistics`, `stats.*` (hint, on, onTitle, loading, empty, t.*, subs, newSuppN, beforeN, overTime, period, period.*, col.*, top.*, delete, deleteAsk, stored, sec, min, hour), `reset.keepStats`, `log.statsKept`, `log.statsFailed`, `log.statsDeleted`, `log.statsJobFailed`.
- **Tests:** `t_ui_settings.py` new case `stats` (helpers `ENTER_EDIT`, `STAT_COUNT`, `js_release_of`; F: a relationship MusicBrainz had, F2: nothing to look up); the tab lists of `settabs`, `settings`, `pressed`, `cache` and `t_coverart.py` `ocrsetting` with "statistics".

## Import 3.37.15 · 2026-10-30

"+ New" in folded pools (165); the fold buttons at a fixed place (166).

- **`datePoolHtml`:** the button `pool-new` (`date.poolNew`) as `add`, also in the folded bar and in the kept bar. **`trackPoolHtml`:** `add` (the button `tg-new`, or with several media the list `tg-new-pick`) computed first; the folded and the kept bar end with it.
- **`renderDates`:** the head has `.dci-pools-fold` (`data-act="pools-toggle"`, `aria-expanded`) right after `.dci-pools-toggle` – "▲ fold" open, "▼ show" folded (`pools.show`); the foot keeps only `pools-keep`. The kept bar (`S.poolsKeep` and a pool not empty) now shows both pools (until 3.37.14 only the ones with chips).
- **New** `groupFoldHtml(a)` (the arrow `group-fold`, from `variantsHtml`): in the full view the first child of `.dci-ghead`, before `.dci-gname` (not for companies; the name's text stays without it); `variantsHtml` keeps it in the compact view only.
- **Fixed** `case 'pool-fold'`: by `poolFolded(pool)` – shown folded: unfolded (`S.poolFold[pool]` removed); shown open: `S.poolFold[pool] = true` and `S.poolsForce[pool]` removed (until 3.37.14 a pool forced open and not remembered folded only got the memory, and stayed open).
- **CSS:** `.dci-pools-head .dci-pools-fold` (min-width, centred), `.dci-ghead > .dci-gfold` (margin-right −12 px: 6 px to the name).
- **Texts (English only):** `pools.show`.
- **Tests:** `t_ui_head.py` new case `poolbar`; `t_ui_view.py` `fold` A) expects the arrow first in the head, at the same x for two entries.

## Import 3.37.14 · 2026-10-30

The answers of a question at its chip (163).

- **New** `chipAnswers(r)` (the answers of the first row of a line: instrument question – `questionRuleFor`, as `instrumentAskHtml`; a guess not answered – options, "other instruments “…”", misc; a type question with `typeAnswer == null`; each `{ act, attr, value, text }`), **`chipNotesOpen(l)`** (`unmappedHtml`, `bothAskHtml`, `levelKeptHtml`).
- **Changed** `emChipHtml(l, e, a)` (the entry as third argument, from `entryCompactHtml`): `ask` = answers or open notes (until 3.37.13 `!!lineAskHtml(l)`); with answers ▾ `data-act="em-chipask"` `data-ask="<entry>|<line>|<event>"`; open (`S.emChipAsk`) – `.dci-em-chipmenu.dci-em-ask[data-rows]` with the answer buttons (`instr-pick`, `instr-misc`, `type-pick`), so the `EM_LINE_ACTS` branch answers for all rows of the line.
- **State:** `S.emChipAsk` (null; the key of the open chip).
- **Handlers:** `case 'em-chipask'` (toggles, `rerenderGroup`, focus on the first answer or back on ▾); the `EM_LINE_ACTS` branch clears `S.emChipAsk` for an answer from the list; Escape closes the list first (after `dmPick`), focus back on ▾.
- **CSS:** `.dci-em-chip { position: relative }`, `.dci-em-chipq`, `.dci-em-chip-open`, `.dci-em-chipmenu` (absolute below the chip, z-index 6).
- **Texts (English only):** `em.chipAsk`.
- **Tests:** `t_entries.py` new case `chipask`.

## Import 3.37.13 · 2026-10-30

A typo or a spelling of its own after a guess; ✕ at the role credit (164).

- **New** `slipDistance(a, b)` (optimal string alignment: a swap of neighbours counts as one), **`guessSpelling(g, name)`** (`foldWord` of the word and the instrument: `'same'` – only case or accents apart; `'typo'` – distance 1; `'own'` – 2 or more; `g.typoAs = { name, typo }` turns it round for that instrument), **`guessTypoSet(row, typo)`** (sets `typoAs`, `roleCreditTouched = false`, `refreshRowDetails`; logs `instrTypo` / `instrOwn`), **`guessNoteHtml(row)`** (below "… – chosen:" in `instrGuessHtml`: `.dci-guess-spell[data-spell-as]` with `data-act="instr-typo"` `data-typo="0|1"`), **`rcClearHtml()`**.
- **Changed** `roleCreditForInner`: with `row.instrGuess` (not misc) – "other instruments" as before; a valid instrument chosen gets `guessCredit(g)` when `guessSpelling` is `'own'`, otherwise `''` (until 3.37.12 always `''`). `pickInstrument` logs `instrTypo` for a typo.
- **Handlers:** `case 'instr-typo'`; `EM_LINE_ACTS['instr-typo']` (the lines of an entry's matrix); `case 'rc-clear'` – a row (`rerenderRow`) or, inside `tr.dci-em-line[data-rows]`, all rows of the line (`lineRows`, `rerenderGroup`); `roleCredit = ''`, `roleCreditTouched = true`; the field gets the focus.
- **Markup:** `rcClearHtml()` after the role credit inputs of `roleCell` (`role-credit`, also the free text attribute of other entities) and of `emLineHtml` (`em-credit`).
- **CSS:** `.dci-rc-clear`, `.dci-em-c-credit { white-space: nowrap }`, `.dci-c-attr .dci-credit:has(.dci-rc-clear)` (a third grid column), `.dci-guess-spell`.
- **Texts (English only):** `instrGuess.typo`, `instrGuess.keepWord`, `instrGuess.own`, `instrGuess.isTypo`, `roleCredit.clear`, `log.instrTypo`, `log.instrOwn`.
- **Tests:** `t_text_basics.py` new case `typonote`; `instrguess` B) and `unknownask` A) expect chimes credited "chaims".

## Import 3.37.12 · 2026-10-30

A period of the matrix or the pool split into its days (162).

- **New** `splittable(d)` (2 – 31 single days, `singleDaysOf`), **`periodMenuHtml(c)`** (a cell without `lcdOf` whose entry is such a period: ▾ `dm-lcd-menu`, the options `data-act="dm-period"` – `single`: a cell per day with the cell's track groups and studios; `lcd`: `commonDate` through `poolDateFor` – and `dm.periodMenu`); `matrixCellHtml` shows it where `lcdMenuHtml` does not apply. Log `dmChosen`.
- **Date pool:** the chip of such a period has `data-act="pool-split"` (`pools.split`, `pools.splitTitle`) while one of its days is not in the pool; the click adds them (`singleDaysOf` creating them), log `dateSplit`.
- **Texts (English only):** `dm.periodMenu`, `pools.split`, `pools.splitTitle`, `log.dateSplit`.
- **Tests:** `t_notes_dates.py` new case `periodsplit`; `lcdmenu` B) notes the ▾ the period keeps.

## Import 3.37.11 · 2026-10-30

The Discogs spelling shown as the artist credit in MusicBrainz (161).

- **`creditChipHtml`:** when every credit of the entry is the spelling shown in the head (`releaseSpelling`), the chip `.dci-gcredit-anv` "artist credit in MusicBrainz: …" (`group.creditedSpelling`, tooltip `group.creditedSpellingTitle`) – until 3.37.10 no chip then. **`entryNameHtml`:** the tooltip adds `group.anvStar` while the spelling is a credit.
- **Import:** after the lookups, the log `anvCredits` with these entries ("Kenneth Ansell (Ken Ansell)").
- **Texts (English only):** `group.creditedSpelling`, `group.creditedSpellingTitle`, `group.anvStar`, `log.anvCredits`.
- **Tests:** `t_ui_head.py` new case `anvcredit` (the matrix view); `entryhead` B) expects the chip and the tooltip.

## Import 3.37.10 · 2026-10-30

℗ / © of a person Discogs lists as a label (160).

- **New (S057):** `PC_TYPES`, `personCopyright(a)` (a company entry with a person's name, `personLikeName`, and only ℗ / © rows), **`mergePersonCopyrights()`** (after `resolveArtists`; Discogs entries without an MB entity): a person of the dashboard with the same name (`entryNames`, `looseName`) takes the rows (`entityType` artist, the types of `typeOptions.artist` – C001 / C002 –, `pcFromCompany`, `pcWhere` – the person's other roles –, `pcFromKey`); else an artist of `S.linked` with that name becomes the entry's MB entity (`setCompanyEntityType` artist); log `pcOfPerson`. **`pcAsLabel(row)`** (`data-act="pc-as-label"`, log `pcAsLabel`): the rows back to the label entry (`pcBack`).
- **`suggestByName`:** such a Discogs entry is searched by its name (`pubByName`), MusicBrainz's artists of that name beside its labels (`asArtist`; the suggestions name their kind as before).
- **Display:** `roleCell` (company rows) the note `.dci-pcfrom` with the button; `emLineHtml` ⓘ (`dci-pcfrom`) and the button; rule chip S057.
- **Texts (English only):** `role.pcFromCompany`, `role.pcAsLabel`, `role.pcAsLabelTitle`, `log.pcOfPerson`, `log.pcAsLabel`. **Register:** S057.
- **Tests:** `t_notes_companies.py` new case `pcperson`.

## Import 3.37.9 · 2026-10-30

The date group Artwork; the concert's date for its photographs (159).

- **`DATE_GROUPS`:** `artwork` (Artwork; design/illustration, illustration, design, graphic design, art direction, artwork; `releaseOnly`) – a column of the matrix (`.dci-dm-grid` six columns now). **`DATE_HINTS`** (mapping file): `artwork` (cover painting / art / illustration / drawing / design, painting, illustration, drawing, artwork, Gemälde, Zeichnung, peinture, pintura; not photographs). **D016:** after such a word in its line the year after a title in quotation marks is a date (`single`), otherwise skipped as before.
- **R078** (mapping file): also "painted by", "cover painting(s)".
- **New:** `CONCERT_PHOTO`, `concertDate()` (the one day of the Performance cells, else of the pool's Performance dates), **`rowDateSugg(row)`** → `{ entry, title }` (the liner notes as before, `linerDateSugg`; a photography row whose role, attributes or line say concert/live: the concert's date). `dateCell` and the flags of the compact view use it; ✕ sets `dateSuggOff` too.
- **Texts (English only):** `date.suggConcert`.
- **Register:** D016 extended, T015/T016 show the new group and words (`register_golden.json` written anew).
- **Tests:** `t_notes_dates.py` new case `artwork`; `t_textcorpus.py` – "Cover art: “Madison” 1988 by Albert Irvin" gives 1988 now (the artwork's year).

## Import 3.37.8 · 2026-10-30

Dates with a comma after the month, "the" before places, festival recordings and a colour for events (158).

- **`DATE_MATCHERS`:** `${P.M},?\s+…` in D004, D006, D007 (both months), D013. **`placeOf`:** a "the" written small before a name in capitals goes.
- **Kinds:** `KIND_PALETTE_DEFAULT.event` (#8a4f7d), `groupKindOf` (an "other" entry of an event: `event`), `columnKind`, CSS `.dci-kind-event`; text `kind.event`; `settings.kindColorsTitle` names it (English).
- **New (S056):** `TEXT_FESTIVAL_WORDS` (mapping file, T055); `festivalName(before, word, after)` (the words in capitals and small particles around the word, up to a comma; an abbreviation such as "Ltd." ends it), `dayKey` / `lsKey`, **`findFestivals(seq)`** (after the import; each festival once, not one with a word of places; the first date of its sentence; `event?query=event:(…)` with every word, offered when the life-span overlaps the date; at most 5; log `festivalFound`), **`festivalHtml()`** (in `srcpanels`, above the lines not recognized), `data-act="festival-add"` (log `festivalAdded`). `S.festivals` reset at each import.
- **`addEntryByMbid(mbid, roleText)`** (from `addManualEntry`, which calls it): an entry of any kind by its MBID with its row.
- **Texts (English only):** `kind.event`, `festival.title`, `festival.hint`, `festival.hintNone`, `festival.offers`, `festival.add`, `festival.addTitle`, `log.festivalFound`, `log.festivalAdded`; `settings.kindColorsTitle` (English changed).
- **Register:** D004 extended, T055, S056 (`register_golden.json` written anew). **Harness:** `/ws/2/event` searched like the others (`MB_SEARCH['event']`).
- **Tests:** `t_notes_companies.py` new case `festival`; `t_ui_view.py kindcolors` expects the colour Event.

## Import 3.37.7 · 2026-10-30

A side alone after "Track(s)", the place after its city (157).

- **`tracksInText`:** the token after a word for tracks may be a letter A–H alone (`(?![\w])`); in capitals it is the source's position, else the tracks of that side (`sideTracks`); a small letter is left out. **`trackRefsIn`** the same.
- **`TEXT.parse`:** `SPEC_W` (positions with a letter alone) for `PREFIX` / `SUFFIX` (`NUMBERS` keeps `SPEC`: "(C)" at the end of a line is no side); `LEAD_TRACK_WORD` – a word for tracks before `LEAD_POS` (S053).
- **`placeIn`:** the first part a place as before; else the last of 2 – 4 parts when it is a place and the parts before it an area ("Tokyo, Zojoji Hall"). **`readClause`:** "VERB <date> in …" (only dates and "on" between, `noDates`) like "VERB in …".
- **Register:** S053, T051 extended (`register_golden.json` written anew – only these texts).
- **Tests:** `t_notes_dates.py` new case `trackside`.

## Import 3.37.6 · 2026-10-30

"Remove nonsensical words and signs" in the window "Text from cover art" (156).

- **New** `OCR_KEEP_SIGNS`, `OCR_SEP_SIGNS`, `OCR_VOWEL`, `OCR_SHORT_WORDS`, `ocrCore`; **`ocrNonsenseWord(tok)`** (a word read uncertainly – in `pt.unsure` – that is no word: signs among its letters, digits among letters except numbers, positions, years, "2nd"; one letter except an initial; no vowel; three same letters), **`ocrSignJunk(tok, i, toks)`** (signs without letters or digits, not those kept; • · | only between two words).
- **`ocrCutText(pt)`** → `{ text, cut }`: per line the tokens dropped, as runs `{ n, before, after, text }` (the kept neighbours) and whole lines `gone: [{ n, text }]`; `cut.n` the number. **`ocrUncutText(pt)`**: the lines put back first, then each run between its neighbours (line n first, then the others), else after the word before it, before the word after it, at the end of line n. **`ocrNonsense(results, on)`** (`r.clean`, `pt.cut`; named so beside the corrector `ocrClean`), **`ocrCleanSync()`** (the text fields, the switches, "n removed", the struck buttons `dci-ocr-word-cut`, without drawing the window anew), `ocrCutWords`, `ocrCleanCount`, `ocrCleanNote`.
- **`ocrResultHtml`:** below each image's name `.dci-ocr-cleanbox` with `data-ocr-clean="i"` (aria-pressed) and `data-ocr-cleann="i"`; in the foot `data-ocr="clean-all"` with `data-ocr-cleann="all"`. **`ocrPartHtml`:** a word taken out struck through. **`ocrClick`:** both switches. **Store of the window** (3.37.5): `clean` per result, `cut` per part.
- **CSS:** `.dci-ocr-word-cut`, `.dci-ocr-cleanbox`, `.dci-ocr-clean[aria-pressed="true"]`.
- **Texts (English only):** `ocr.clean`, `ocr.cleanTitle`, `ocr.cleanAll`, `ocr.cleanN.one/other`, `ocr.cleanNone`.
- **Tests:** `t_coverart.py` new case `ocrnonsense`.

## Import 3.37.5 · 2026-10-30

The window "Text from cover art" kept, and stored while remembering (155).

- **`closeOcr(discard)`:** without `discard` (✕, Esc, "Cancel", the import) `S.ocr` stays, `hidden`, and is stored (`ocrStateSave`); stopped while reading, the results done stay (step result, else pick). With `discard` (the beta off, its reset, resetting all settings, "Start over", "Delete stored import") as before: the local addresses revoked, the PDFs destroyed, `S.ocr` null. **`openOcr`:** a kept window shown again (log `ocrBack`); **`renderOcr`** draws nothing while hidden. **`openFromCoverArt`** calls `openOcr` alone.
- **New store** `OCR_STATE_KEY` (`dci-ocr:<MBID>`, prefix `ocr` in `REL_PREFIXES`: counted, forgotten with the release; written only while remembering, via `relWrite`): `{ v, t, step, langs, size, frameFirst, cur, imgs, res }` – `ocrImgEntry` (key `ocrFrameKey`, tick, mode, frames and turn as parts of the image; what adds it again: an address, a Discogs image, the name and size of a file, the file / address and page of a PDF page), `ocrResEntry` (the parts with their places, texts, lines and words read uncertainly, places as parts of the image: `ocrToFrac` / `ocrFromFrac`). Written when the window is hidden, after reading, on `pagehide`; nothing chosen or read: removed. Not pasted images (`pasted` on own files now).
- **`ocrStateRestore(images)`** (in `openOcr` after `ocrList`; a store none of whose images are there and without own ones is left aside): the release's images ticked as then (`ocrTakeEntry` → `saved`, put back by `ocrRestoreFrames` with the canvas), images by address and Discogs images made again, own files and PDF pages as cards `missing` (no image, `ocrChosen` leaves them out, the card disabled: `ocr.missingCard`), the results (`ocrResFromEntry`; their places on the canvas once it is made: `ocrResBoxes`, called in `ocrCanvasLoad`), the step (`restoredStep`); log `ocrRestored`. In the result step the images of the texts are loaded and drawn. **`ocrTakeBack(images)`** (`ocrAddFiles`, `ocrAddPdf`): a file of the same name (a PDF page: file and page) fills its waiting card; only such files: the step stays. **`ocrMissingHtml`** (pick and result step: the names, a button and its own file field). **`ocrFrameKey`** of a file: `size0` while its card waits.
- **"↺ Start over"** (`data-ocr="restart"`, `ocrRestart`: `confirm` when something would be lost; `closeOcr(true)`, the store removed, `openOcr`; log `ocrRestart`), **"To the texts read →"** (`data-ocr="toresult"`); an own image removed takes its results; `ocrZoomDraw` waits for a part's place. **`ocrStateDropAll`** at ⚙ Beta → Reset and "Reset all settings". **CSS:** `.dci-ocr-goneimg`, `.dci-ocr-gone`, `.dci-ocr-missing`, `.dci-ocr-restart`.
- **After a review** (an agent that had not seen the work): nothing is stored before the stored window was taken over (`restoreTried` – a list of the release that failed would have erased it); own files added while the list loads fill their cards; nothing taken over while remembering waits for a reload (`S.rememberHold`); a PDF by its address can be added again (its cards are no duplicate); cards waiting for their files are not loaded ahead (`ocrToLoad`), filled their load state starts anew; nothing new is loaded ahead while the window is hidden; another image size keeps the places of the texts read (`ocrResToFrac`), an image turned after reading keeps none (`ocrResUnplace`); the images of the texts are loaded one after the other (`ocrResultLoad`); "All images" / "All shown" leave the waiting cards alone; "read small" waits for the image's size.
- **Texts (English only):** `ocr.restart`, `ocr.restartTitle`, `ocr.restartAsk`, `ocr.missing.one/other`, `ocr.missingCard`, `ocr.toResult`, `log.ocrBack`, `log.ocrRestored`, `log.ocrRestart`.
- **Tests:** `t_coverart.py` new case `ocrkeep`; `ocrpdf` E, `ocrload` C, `ocrmore` E and `ocrremember` B start over first (the frames stored stay), `ocrauto` D expects the window as left.

## Import 3.37.4 · 2026-10-30

The lines not recognized and left out, from the cover art: their cut-outs on hover (154).

- **`ocrCrop(canvas, box, wide)`:** `wide` – a margin of 0.9 × the line's height (at least 10 px), at most `OCR_PEEK_LINE_W` × `OCR_PEEK_LINE_H` (720 × 280). **`ocrLineOrigins`:** each hit with a crop keeps `box` and `canvas` (in memory, as the crops); the wide cut-out is made when first shown (`hit.wide`).
- **New `linePeekHits(line)`** (only while the text of `S.ocrLines` is the source; "… → ? “x”" without its tail; a sentence: the lines that contain it), `linePeekAttrs`, `linePeekShow` / `linePeekHide` / `linePeekOver` / `linePeekOut` (one `#dci-line-peek` on the page, below the line or above it, within the window; 250 ms on hover, at once on focus; hidden on scroll). **`renderSource`:** the `li` of `.dci-unrec` and `.dci-ignored` with `data-line-peek` and `tabindex="0"`, the hint `cover.linePeekHint`. Listeners on the overlay (mouseover/out, focusin/out, scroll). **CSS:** `#dci-line-peek`, the dotted underline of such lines.
- **Texts (English only):** `cover.linePeekHint`.
- **Tests:** `t_coverart.py` new case `ocrlinepeek`.

## Import 3.37.3 · 2026-10-30

Comments of live recordings offered while the setting is off (150b).

- **`S.liveComOffer`** (null / 'yes' / 'no', for the page; "Delete stored import" sets it back) and **`liveComOn()`** (`S.liveCom` or 'yes'): `saveLiveJob` takes the comments with `liveComOn()`; the area lookups re-render while the setting is on or the offer is not declined.
- **`renderLiveComments`:** proposals unless declined; without `liveComOn()` the line `.dci-livecom-offer` (`livecom.offer` with the positions and the first proposal, tooltip `livecom.offerTitle`) and the buttons `data-act="livecom-yes"` / `"livecom-no"` (log `liveOfferYes` / `liveOfferNo`; a waiting job is saved anew). **CSS:** `.dci-livecom-offer`.
- **Texts (English only):** `livecom.offer.one/other`, `livecom.offerYes`, `livecom.offerNo`, `livecom.offerTitle`, `log.liveOfferYes`, `log.liveOfferNo`.
- **Tests:** `t_works_more.py` new case `liveoffer`; `livecom` A) expects the offer while the setting is off.

## Import 3.37.2 · 2026-10-30

The text reader: ℗ / © twice on a line, credits between » «, guests (151 – 153).

- **`sentencesOf`:** a line split at `TEXT_CREDIT_SEPS` (T054, » « • · |) when every part is a credit ("Role: …", "… by …"); a line starting with ℗ / © split before a sign again after a name (`PC_START`, `PC_AGAIN`, T033).
- **`readClause`:** new (S055) "HEAD: …" with `TEXT_GUEST_HEAD` / `TEXT_FEAT_HEAD` (T053): the items after the colon ("NAME on X and Y", "NAME – X", "NAME (X)", names only), the roles of a guest head with the mod "Guest" (`Saxophone [Guest]` – the attribute guest via the rules as a Discogs bracket), a name without roles "Guest" (performer, guest); and "NAME on X and Y" when every role is an instrument or a voice (`playable`).
- **`mapRole`:** a hyphen between two letters read as a space when only so a rule knows the role ("Cover-Photo" → R068, photography "cover photo").
- **Mapping file:** `TEXT_GUEST_HEAD`, `TEXT_FEAT_HEAD`, `TEXT_CREDIT_SEPS` (after `TEXT_AUX_WORDS`). **Register:** S055, T053, T054; T033 extended.
- **Tests:** `t_text_basics.py` new case `guests`; `register_golden.json` written anew (only the register's texts – no result of the corpus changed).

## Import 3.37.1 · 2026-10-30

Suggestions linked in this release first (E5a).

- **New `linkedInRelease(ws)`** (`S.linked`, made with `S.existing` when the release is read): mbid → `{ name, where }` from the release's artist credit and labels, the artist credits of tracks and recordings, the relationships of the release, its recordings and their works (not urls, works, recordings, releases); `where` as "mix on the release", "composer on “Song One”", "track artist 1.3", "release artist", "label of the release".
- **`suggestByName`:** after the web hits, the hits linked in this release (and one of the same name the search did not give) first, `linked` (up to three places) – only of the entry's kind (a person: artists; a company: its entity type or the types its rows allow; `linkedInRelease` keeps each one's type – after a review: a label "℗ 2021 Jane Doe" was offered the artist Jane Doe as a label); log `linkedSuggested`.
- **`suggestStackHtml`:** `dci-sugg-linked` and the mark `match.markLinked` (instead of "release artist"), tooltip `match.linkedTitle`. **CSS:** solid green border, light green, bold.
- **Texts (English only):** `match.markLinked`, `match.linkedTitle`, `match.inRelease.ac/label/track/rel/release`, `log.linkedSuggested`.
- **Tests:** `t_notes_companies.py` new case `linkedsugg` (also: the label of the same name gets no linked artist); `t_sources_bandcamp.py labelpage` and `t_text_basics.py freetext` expect the new mark ("in this release: release artist", "… composer on “Song One”").

## Import 3.37.0 · 2026-10-30

Milestone: the Discogs notes read in full (E5, S054).

- **New `addNotesPersons(rel, res)`** (from `addNotesCompanies`, which now runs with S042 or S054): the credits of `TEXT.parse` of the notes (not those without a name); `kindOf` / `sameKind` (`mapRole`: the same first type, the same attributes – "Executive Producer" is no "Producer" – and the same instrument or voice – "Instruments" is no "Piano") and the names of Discogs's credits (name, raw name, as credited, `looseName`) decide: a twin is left out – Discogs's credit for the whole release gets the notes' tracks, of all lines of the notes (`tracks`, `notesIdx`, `notesLine`); the same credit in two lines of the notes is one, with the tracks of both; a name of a company of the release ("Mastered by Sterling Sound" with "Mastered At – Sterling Sound") is no person; the same name with another role takes Discogs's `who` (joins its entry); a new name `who.id` 0; pushed with `fromNotes`, `notesLine`. Logs `notesCredits`, `notesCreditTracks`. With S054 `addNotesCompanies` takes every company of the notes (`wanted`), each with its `line`; **`plainNotesName`**: no name with brackets or of numbers only, as a track list of the notes leaves them ("Pub Co (1" of "Published by Pub Co (1, 3); Ghostpub (4)" – S022 reads those lines).
- **`groupCredits`:** `group.fromNotes` (only while every credit is from the notes and has no Discogs id), per role `fromNotes`, `notesLine`. **Entries:** `fromNotes` → searched by name (as S042). **Rows:** `fromNotes`, `notesCredit` (its line); Discogs's credit with tracks from the notes: `notesTracks` (only the tracks of the notes, `notesIdx`), `notesFrom` (ⓘ as S043). **Companion:** rows from the notes are not sent as Discogs credits in `status-map` (their mark would land on another role of the name). **`groupCompanies`:** per role `fromNotes` → company rows `fromNotes`, `notesCredit`.
- **Display:** `notesLineInfo(row)` (ⓘ with the line, class `dci-notesline`); `roleCell` – a person's row "From the Discogs notes" instead of "Discogs: whole release" / its tracks, a company's ⓘ after its source; `emLineHtml` ⓘ next to the role of a line from the notes.
- **Per release:** `NOTES_OFF_KEY` (`dci-notes-off:<MBID>`, in `REL_PREFIXES`), `S.notesOff`; **`setNotesRowsHidden(hide)`** (`notesHidden`, `notesLevel`; works skipped: `notesLevel` work), **`setNotesOff(off)`**; the menu Source ▾ `data-f="notes-off"` for a Discogs import whose notes gave rows; at the import hidden again; "Delete stored import" sets it back. Hidden like the "about" text (`dci-about-hidden`).
- **S022:** no "only a track group" when the entry's row from the notes (or with tracks from the notes) has these tracks.
- **Settings:** ⚙ Texts `data-set="rule-on" data-rule="S054"`; ↺ of Texts switches S054 on again. **Register:** S054. **Milestone** 3.37.0 (`MILESTONES`, `ms.3.37.0`).
- **Texts (English only):** `notes.credit`, `notes.creditLine`, `notes.off`, `notes.offTitle`, `log.notesCredits`, `log.notesCreditTracks`, `log.notesOff`, `log.notesOn`, `settings.notesCredits`, `settings.notesCreditsTitle`, `ms.3.37.0`.
- **Checked by an independent review before the commit** (three findings fixed: lines of the notes merged, kinds of roles compared strictly, the type of a linked suggestion – that one in 3.37.1 – and smaller ones).
- **Tests:** `t_notes_companies.py` new case `notescredits` (new entries and rows marked, nothing twice – also two lines, "Executive producer", a studio's name –, tracks onto Discogs's credit, Source ▾ left out and back, the rule off and on); `t_ui_settings.py notice` the three newest milestones 3.37.0, 3.36.0, 3.35.0; `t_works_matrix.py mxdrop`: Nobody Here an entry from the notes (strings arranger, 2, 4), no name from a track list; `register_golden.json` written anew (only S054 added).

## Import 3.36.7 · 2026-10-30

Places of the Discogs notes on their tracks (150, S053).

- **TEXT:** new `LEAD_POS` (`LEAD_POS_ONE`: "A1", "D", "AA", "12", "1.2"; joined by "to", "–", ",", "&", "and") – positions in front of a sentence before its verb ("… recorded …"); `readLine` tries it after `PREFIX`, `SUFFIX`, `NUMBERS` (rule S053), `useScope` only when the positions name tracks.
- **`addNotesCompanies`:** the notes are parsed with `resolveTracks` / `resolveTitles` against the Discogs tracks (`rel.tracks`; before: MusicBrainz's numbers – "A1" named nothing); with S053 a company Discogs lists for the whole release (same name, same role) gets the tracks of a line of the notes (`notesLine`, set, ⓘ) – before only publishers below a heading (S043); a company only in the notes keeps its line too. Its own log line: `notesCompanyTracks` (publishers: `notesPubTracks` as before).
- **Row:** with tracks from the notes `role.companyNotesTracks` ("Companies, etc. (the tracks from the notes)") or `role.notesOnly` instead of "(whole release)".
- **Register:** S053 (in the window "Mapping rules", can be switched off there).
- **Texts (English only):** `role.companyNotesTracks`, `role.notesOnly`, `log.notesCompanyTracks`.
- **Tests:** `t_notes_companies.py` new case `facets` (13 tracks on three LPs, Discogs's place and one from the notes, the dates after "Apply", "li" and the live comment, a pasted text); `register_golden.json` written anew (only S053 added – no result of the corpus changed); `t_notes_dates.py facets` C: the places of the notes with their tracks (before: none expected).

## Import 3.36.6 · 2026-10-30

The attributes of the matrix lines a column each (148).

- **`emBlockHtml`:** the head has a `th.dci-em-c-flag` per attribute (`flagNames`; none: one empty cell) instead of one `th.dci-em-c-flags` with spans; `cols` = 2 + max(1, attributes) + events (+ 1 for "＋ Event") + 1.
- **`emLineHtml`:** a `td.dci-em-c-flag` per attribute (its checkbox, or empty where the type has no such attribute) instead of one `td.dci-em-c-flags`.
- **CSS:** `.dci-em-c-flags` (inline blocks of 34 units) → `.dci-em-grid th/td.dci-em-c-flag` centred, no wrapping, at least 22 units; `.dci-em-c-flag input { margin: 0 }`.
- **Tests:** `t_entries.py` new case `flagcols` (every word's centre over its checkboxes' within 2 px, not wider than its cell, at 100 % and A+ ×3).

## Import 3.36.5 · 2026-10-30

The symbols of the head and the switches show their state; no bridge, no ⓘ in the head (147, 149).

- **New `syncLogBtn()`** (in `setLogVisible` and `renderAll`): `aria-pressed` of the head's log symbol (`headBtn('log', …, 'aria-pressed="false"')`), styled by the existing `.dci-headbtn[aria-pressed="true"]`.
- **Bridge removed** (3.30.4): `placeBridges` → **`alignPanes()`** (only `alignSettingsPane`); `setVar`, the classes `dci-bridged` / `dci-bridged-box`, the custom properties `--dci-bridge-*` and their CSS gone; the scroll listener and the ResizeObserver of the head gone (those of the body and the settings stay, for the pane).
- **ⓘ removed:** `headBtn('connections-open', 'info', …)`, the case `connections-open`, `ICONS.info` and the text `connections.open` (all languages, `i18n_del.py`).
- **CSS:** `.dci-seg button[aria-pressed="true"]` (also `:hover`, `:disabled`) `#736dab` with white text; the rules with `[data-level]` and `[data-sync-mode]` (more specific) keep theirs.
- **Tests:** `t_ui_settings.py` case `bridge` → **`pressed`** (⚙ and rules pressed without a bridge, the log pressed while shown, ⌨, A−/A+/⤢ never, the tabs joined as before, "Entries" and "by event | by role" filled); `settabs` D through ⚙ → Connections; `t_ui_head.py head` without `connections-open`.

## Import 3.36.4 · 2026-10-30

The choices of the works matrix remembered per release (146).

- **New `worksSnapshot()`** (in `rememberSnapshot`, key `works`): `plan` (`S.workPlan`, only `origin` search and pending, without `entity`), `on` / `off` (`S.linkAttrOn` / `S.linkAttrOff`, the non-empty ones), `fills` (`S.dateFills`, `fromCol` by entry), `colDate` (`S.mxColDate`), `removed` (`S.mxRemoved`: name, MBID, entity type, entry, row ids), `collapsed` (`S.mxCollapsed`), `opts` (`S.workRowOpts`), `defaults` (`S.workDefaults`, when chosen). A column of an entry (`k:<key>`, the key changes with each import) is stored by the entry (`e:<entry id>`, **`colKeyOut`** / **`colKeyIn`**).
- **New `restoreWorks(w, entries, ids)`** (at the end of `restoreRemembered`): sets only what this import lacks; the row ids of a column taken out mapped to this import's rows; returns how many (they count in "rememberRestored").
- **Stored after a change:** `renderWorks()` calls `scheduleRemember()`; also the type of a new work (`mx-type`) and the type for all new works (`work-type`).
- **Tests:** `t_works_matrix.py` new case `remember` (attribute, new work, column taken out and brought back, column date, type of new works after the page is loaded again); `t_works_more.py worksskip` C: taken again after the page was loaded again, the new works planned before the skip come back (nothing looked up), their plans taken back before D.

## Import 3.36.3 · 2026-10-29

⌨ in the head: the keyboard shortcuts.

- **Head:** `headBtn('keys-open', 'keys', …)` before ⓘ (new icon `ICONS.keys`), `aria-expanded`, `aria-controls="dci-keys"`; the panel `div.dci-keys#dci-keys[data-el=keys]` after the settings in the body.
- **New `IS_MAC`** (`navigator.userAgentData.platform`, else `navigator.platform` / the user agent), **`keysHtml()`** (one table: the groups as `tbody` with a heading row, each shortcut a `kbd` per key – `keys.k.*`, on a Mac the `…Mac` variants of alt, ctrl, enter, paste), **`setKeysOpen(open)`**, **`renderKeys()`** (also in `renderAll`). State `S.keysOpen` (not stored).
- **`onClick`:** `keys-open` (the head button and ✕). **Esc** (the global handler): the shortcuts close first after "Text from cover art" and "Mapping rules", the focus back on ⌨.
- **CSS:** `.dci-keys`, `.dci-keys-head`, `.dci-keys h3`, `.dci-keys-table`, `.dci-keys kbd`.
- **Texts (English only):** `keys.open`, `keys.title`, `keys.system`, `keys.systemMac`, `keys.g.page/editor/dashboard/media/ocr`, `keys.toggle`, `keys.esc`, `keys.enterEdit`, `keys.enter`, `keys.tabs`, `keys.lines`, `keys.shiftDrop`, `keys.pasteDate`, `keys.mediaEnter`, `keys.ocrPaste`, `keys.ocrUrl`, `keys.ocrZoom`, `keys.k.alt/altMac/ctrl/ctrlMac/shift/enter/enterMac/paste/pasteMac/esc/home/end/wheel`.
- **Tests:** `t_ui_head.py` new case `keys` (opened with the groups and keys, Esc and ✕ close it, as a Mac); `head` with ⌨ among the buttons.

## Import 3.36.2 · 2026-10-29

The diagnosis in the log as a setting (off).

- **New `LOG_DIAG_KEY`** 'dci-log-diag' (true while on), `S.logDiag`. `renderLog` draws `data-log-act="diag"` only with `S.logDiag` (or while a diagnosis runs).
- **Settings:** ⚙ General `data-set="log-diag"`; the handler stops a running diagnosis (`stopDiag`) when switched off and draws the log anew; in `TOPIC_KEYS.general`, `SETTINGS_KEYS`; `resetTopic('general')` and `resetSettings` switch it off (and stop a diagnosis).
- **Texts (English only):** `settings.logDiag`, `settings.logDiagTitle`.
- **Tests:** `t_ui_settings.py` new case `logdiag` (no button by default, on, a running diagnosis stops when switched off, ↺ of General).

## Import 3.36.1 · 2026-10-29

Fixes of 3.36.0 (and two of 3.35.4 / 3.35.6) after an independent review of the code of Block AH.

- **`S.rememberRead`** (the tab read the stores when it was opened) and **`S.rememberHold`**: `setRemember(true)` in a tab that did not read them, for a release with something stored (**new `hasRemembered(id)`**) – nothing of the release is written (`relWrite`, `relMapWrite`, `saveRememberNow` return), message `remember.hold` with the action `remember-reload` (`location.reload()`); otherwise `rememberNow()` as before, and the about stash only when the tab holds it (`S.aboutStash`).
- **`REMEMBER_ROWS_KEY`** holds `{ v: 2, by: { <source>: snapshot } }` (the 3 used last; a stored `v: 1` snapshot is read too) – `saveRememberNow` merges, `restoreRemembered` takes the one of `S.importSrc`.
- **`rememberSnapshot`:** rows of the source removed with ✕ as `{ k, i, x: 1 }` (restored: they stay removed); a level set by hand in this import always in `d` (with `existingAll` taken off on restore); `media` (new **`mediaSig()`**) – with another media choice the tracks of the diffs are not taken over, and own rows keep only tracks of the selection (none left: left out). `ROW_OWN_FIELDS` with `differ`, `confirmedBy`, `suppTook`, `redrawLater`, `dateEdit`.
- **`loadRelease`:** `rememberFresh()` before `resolveArtists` (rows added meanwhile are rows of their own); new **`finishRemember(seq)`** – rows whose touch fields (`levelTouched`, `primaryTouched`, `roleCreditTouched`, `creditTouched`, `typeAnswer`) did not change get the state after the lookups as their baseline; restore in `try` (an error: rows and entries as before, log `rememberError`); also for an import without entries.
- **`restoreRemembered`:** references to rows (`splitFrom`, `mxOrigin`) only on rows that got them from the snapshot, mapped to the new ids or removed; entries: the remembered entity type set directly (no `setCompanyEntityType`); the order: a removed row's entry without rows no longer throws (`byEntry.get(…) || []`).
- **New `rebaseFresh(row)`** (`REMAP_FIELDS`), called in `applyRulesChange` after `remapRow`.
- **`name-use` / `alias-use`** set `matchTouched`.
- **`rememberedReleases`:** releases not in the index by the time of `dci-source-pick` / `dci-media-sel` / `dci-ocr-frames` (`at`, `t`), the most recent first. **`remember-max`:** no `touchRemembered()` at the change (the next store trims). **`forgetAllRemembered`** clears the pending store.
- **`clearPools('tracks')`:** `S.workGroupsStash = null`. **`emEventLevel`:** `matrixDateForLevel` once per date group of the moved rows.
- **Texts (English only):** `remember.hold`, `remember.reload`, `log.rememberError`.
- **Tests:** `t_ui_settings.py` new case `cache2` (a removed row stays removed, a text does not replace the Discogs state, switched on in a tab opened while off: the message, nothing written over, back after loading again); `cache` F: the other release goes when something is stored next; `t_entries.py` new case `remember` (order, an opened event's tracks, one row each – back after loading again, staged the same); `t_ui_view.py compact` F: Guitar Guy's row removed with ✕ stays removed after loading again.

## Import 3.36.0 · 2026-10-29

Milestone "Remember per release": the stores of a release only with the new switch, its rows and entries remembered too (collected item 146).

- **Storage layer (before `LOG_KEY`):** `REMEMBER_ON_KEY` 'dci-remember-on' (true while on), `REMEMBER_MAX_KEY` 'dci-remember-max' (0 – 100, 50 not stored), `REMEMBER_INDEX_KEY` 'dci-remember-index' ([[mbid, time] …], the most recent first), `REMEMBER_ROWS_KEY` `dci-remember:<MBID>`; `S.rememberOn`, `S.rememberMax`, **`remembering()`**. `REL_PREFIXES` / `REL_KEY_RE` (the stores of one release: date-pool, track-pool, date-matrix, about-off, bc-off, src-off, works-skip, remember), `REL_MAPS` (dci-source-pick, dci-media-sel, dci-ocr-frames), `relMem` (those maps in this tab while nothing is remembered). New **`relRead`**, **`relMapRead`**, **`relMapWrite`**, **`relWrite`** (only while remembering; the storage full: `dropOldestRemembered` and again, then the message `remember.full` once), **`rememberedReleases`** (the index, then releases found in the storage), **`touchRemembered`** (once a minute; beyond `S.rememberMax` → `forgetRelease`), **`forgetRelease(id)`**, **`dropOldestRemembered`**, **`storageSizes`** (bytes as UTF-16 of the releases' stores and of every `dci-…` key), **`bytesText`** (KB / MB, one decimal, `Intl.NumberFormat(LANG)`), **`forgetAllRemembered`**.
- **The stores read and written through it:** `S.datePool`, `savePool`, `S.aboutOff`, `S.srcOff`, `S.trackPool`, `saveTrackPool`, `saveMatrix`, `dm()`, `ocrSavedFor` / `ocrSaveFrames`, `keepSourcePick` / `startSource`, `chooseMedia` (read and write), `saveSrcOff`, `setAboutOff` (its stash also in `S.aboutStash` – before it was read back from the storage), `S.worksSkip`, `applyWorksChoice`, `setWorksSkip`. Writing `null` for them stays direct where something is deleted (`forgetImport`, `resetSettings` with the pools – now also those of this release).
- **Rows and entries:** new `ROW_OWN_FIELDS` (not stored: id, entry, open, and what MusicBrainz or "Stage: …" made of a row – `existingChecked`, `existingAll`, `levelBeforeSkip`, `scopeLevel`; `rowFieldsOf` takes the level before them), `encField` / `decField` (JSON, Sets and Maps also inside), **`rowFieldsOf`**, **`entryIdOf`** (an entry by its source id and name, an entry added by hand by its MusicBrainz id), **`rowBaseKey`** (the line of the source: entry, raw, base, dSpec, anv, company, dSplitFrom, artTask, fromAbout), **`rememberFresh`** (`S.freshRows`: key with its number among equal ones, base, fields), **`rememberSnapshot`** (`{ v: 1, at, src, rows, entries, manual }` – a row of the source with how it differs, `{ k, i, d }`; a row of its own whole, `{ e, b, i, f }`; supplements left out), **`scheduleRemember`** (a second after a change, from `refresh()`), **`saveRememberNow`** (also on `pagehide` and at the start of the next import), **`restoreRemembered`** (only with the same `S.importSrc`; rows of the source get their differences, rows of their own come back if their line is still there or they were added by hand, entries added by hand anew; the order: the entries as the source gives them, the rows of an entry as remembered, new lines after them; `splitFrom` mapped to the new ids; join, by, the entity chosen by hand; log `rememberRestored`, `rememberLost` and the message `remember.lost`).
- **`loadRelease`:** `importSeq` – only the last import started counts (an import started while another still ran met its rows at its end); `S.importSrc` = `<source>:<id>`; at the end (after `computePublisherEvidence`) `rememberFresh()`, `restoreRemembered()` while remembering, `S.rememberReady`. `artist-pick` and `setArtistManually` mark `matchTouched`.
- **Settings:** `SETTING_TOPICS` with `cache` (after `beta`); its body: the switch `data-set="remember"`, the number `data-set="remember-max"`, `data-act="remember-forget"` (confirm) with `data-el="remember-size"`. New **`setRemember(on)`** (on with 0 → 50) and **`rememberNow()`** (switched on: pools, matrix, switched-off credits, about, works skip, the maps of this tab and the rows stored at once); the number 0 switches off. `TOPIC_KEYS.cache`, `SETTINGS_KEYS`, `resetTopic('cache')`, `resetSettings`.
- **Media dialog:** while not remembered, "Remember this choice for this release (in this tab)" with a tooltip.
- **Milestone:** `MILESTONES` 3.36.0, `ms.3.36.0`.
- **Texts (English only):** `settings.t.cache`, `settings.cacheHint`, `settings.remember`, `settings.rememberTitle`, `settings.rememberMax`, `settings.rememberMaxTitle`, `settings.rememberMaxHint`, `settings.rememberForget`, `settings.rememberSize.one/.other`, `settings.rememberAll`, `settings.rememberAsk.one/.other`, `remember.full`, `remember.lost.one/.other`, `remember.forgot.one/.other`, `media.rememberTabOnly`, `media.rememberTab`, `log.rememberFull`, `log.rememberDropped`, `log.rememberForgot.one/.other`, `log.rememberRestored.one/.other`, `log.rememberLost.one/.other`, `ms.3.36.0`.
- **Tests:** `harness.REMEMBER` (True: switched on before the script starts – the files written before expect the stores remembered) and `REMEMBER_PRESET` in `open_mb_edit` / `open_mb_any`; `t_ui_settings.py` new case `cache` (the default off, the changes gone after a reload, switched on and back, the source changed, 0 and 50, another release forgotten with 1, forget all), `settabs` / `settings` / `bridge` with the tab Cache, `reset` (the stores of rows are no settings), `notice` (3.36.0, 3.35.0, 3.34.0); `t_coverart.py ocrsetting` (Cache before ⓘ Connections); `t_entries.py order` with `REMEMBER = False` (the order holds until the next import while not remembered); `t_register.py` waits for the import of the release before the text (before, the text met the end of that import – "Strings arranged by Zoe Q" and Kim's arrangement stayed on the recordings by chance; now S006 puts them into the works matrix), `register_golden.json` written anew.

## Import 3.35.6 · 2026-10-29

The works of the source as track groups, with a box in the track pool and a setting (collected item 145b).

- **New `sourceWorks()`:** the tracks of `S.srcTracks` with `work` (the parts of an index track of Discogs, `DISCOGS.toRelease` 3.35.1), by work, only tracks of the MusicBrainz release. **New `placeWorkGroups()`:** each work a group `{ id, name, tracks, found: true, work: true }` (a suggestion, `trackGroupSuggested`), none if a group has the same tracks.
- **New `applyWorkGroups({ quiet })`:** wanted (`S.workGroupsOn` and not `S.workGroupsOff`) – **new `unstashWorkGroups()`** puts back what was left out, then `placeWorkGroups`; not wanted – the groups with `work` leave `S.trackPool`, the cells of the date matrix lose their ids in `tgs` (a cell only on them is removed), all kept in `S.workGroupsStash = { groups, cells: [{ id, ids }], removed }`. Log `workGroupsIn` / `workGroupsOut`; `dmChanged` (quiet: `saveMatrix` only).
- **Storage:** `saveTrackPool` and `saveMatrix` store the pool and the matrix with what is in the stash (leaving the works out holds until the next import). The import calls `unstashWorkGroups()` and sets `S.workGroupsOff = false` where it takes the new `S.srcTracks`, and `applyWorkGroups({ quiet: true })` after `placeTitleDates()`; `reloadPools` places them anew.
- **Track pool:** `trackPoolHtml` – the box `data-f="work-groups-pool"` ("n works as track groups", ticked = not `S.workGroupsOff`) while the setting is on and the source has works; `onChange` → `applyWorkGroups()`.
- **Setting:** new `WORK_GROUPS_KEY` 'dci-work-groups' (false while off), `S.workGroupsOn`; ⚙ Settings → Dates & tracks `data-set="work-groups"`; in `TOPIC_KEYS.dates`, `SETTINGS_KEYS`, `resetTopic('dates')`, `resetSettings`.
- **Texts (English only):** `settings.workGroups`, `settings.workGroupsTitle`, `trackpool.works.one/.other`, `trackpool.worksTitle`, `log.workGroupsIn.one/.other`, `log.workGroupsOut.one/.other`.
- **Tests:** `t_dates_matrix.py` new case `workgroups` (two works in the pool as suggestions, one on a date of the matrix, the box off and on with the date, the setting off and on, a new import ticks it again with the date, the setting off stored).

## Import 3.35.5 · 2026-10-29

Companies, places, areas and other entries as a matrix too, when their rows offer a date or tracks (AE-4).

- **`mxPerson` renamed `mxOn`** (all 4 callers): persons as before; companies (`a.company`) and other entries (`a.other`) when one of their rows (`inEntry`, not `s046Out`) offers an event – **new `offersEvent(r)`**: not on works, and on recordings or of a type without `has_dates === false` (also a row taken out: `ltOf`). `mxEntry` / `mxCompact` follow.
- No other change: their roles are lines of their own blocks (`lineKindOf` '' – nothing to join), the rows of works (publishing) stay below the matrix as before.
- **Tests:** `t_entries.py` new case `companies` (Abbey Road Studios and Sony as matrices, Pub Co with its rows, compact, staged the same as in the legacy view, a date typed into the place's event).

## Import 3.35.4 · 2026-10-29

An event of an entry's matrix opened: level, date and tracks for all its rows (AE-3).

- **`evHeadHtml(e, open)`:** ▸ / ▾ (`data-act="em-evopen"`, `data-ev`) before ①; opened: class `dci-em-evopen`. `emBlockHtml` passes whether the event is the one opened in this block and draws **new `emEventHtml(a, e)`** below its table.
- **State:** `S.emEvOpen` (Map entry key → `{ block, ev }`, one event per entry; not stored).
- **New `emEventHtml`:** the levels (`recording`, `release`, `release_group` – those `typeOnLevel` has for a row of the event, and its own), the date field (`data-f="em-evdate"`, as in the head), the dates of the pool (`data-act="em-evpool"`, `data-id`; '' = no date), on recordings the tracks (`data-f="em-evtrack"`, `data-i`), media (`em-evmedium`), track groups (`em-evtg`), all (`em-evall`), ✕ (`em-evopen`).
- **New `emEventLevel(a, evKey, level)`:** rows whose type is on the level → new **`levelOf(row, level)`** (the part of `setLevel` without drawing; `setLevel` uses it), from release to recording with all tracks of the selection if they had none; `matrixDateForLevel`; the others get `row.emLevelKept = level`. **New `emEventPool`**, **`emEventTracks`** (at least one track, else the message `em.evNoTracks`). All mark the rows `dateKeyed` and call **new `emEventMoved(a, rows)`**: two rows of one line in the same event – the later ones to Skip; the opened event follows the rows' new key. `emEventDate` calls it too.
- **New `levelKeptHtml(l)`** in `lineAskHtml`: the yellow note of a row with `emLevelKept`, "ok" (`em-keptok`) takes it off the line's rows; a row in the event again loses it.
- **`entryMatrixChange`:** `em-evtrack`. **`onClick`:** `em-evopen`, `em-evlevel`, `em-evpool`, `em-evall`, `em-evtg`, `em-evmedium`, `em-keptok`. **`rerenderGroup`:** a field of the opened event keeps the focus (its key changes): the same `data-f` (and `data-i`) in `.dci-em-evedit`.
- **CSS:** `.dci-em-evtoggle`, `.dci-em-ev.dci-em-evopen`, `.dci-em-evedit`, `.dci-em-evrow`, `.dci-em-evtop`, `.dci-em-evlab`, `.dci-em-evpool`.
- **Texts (English only):** `em.evOpen`, `em.evClose`, `em.evEditTitle`, `em.evLevel`, `em.evDate`, `em.evPool`, `em.evTracks`, `em.evGroups`, `em.evNoTracks`, `em.levelKept`, `em.keptOk`, `log.emEvLevel`, `log.emEvTracks`.
- **Tests:** `t_entries.py` new case `evhead` (opened, a track added with the focus, the last track stays, all – two events one, a date typed / none / of the pool, Release and back with the note and "ok", ✕, staged with the date); `BLOCKS` leaves ▸ out of the event heads' text.

## Import 3.35.3 · 2026-10-29

Lines of an entry's matrix in another order (AE-2).

- **`emLineHtml`:** a block of more than one line – ⠿ (`button.dci-em-grip`, `data-drag="em-line"`, `data-id` the line, `data-block` its block, draggable) before the role.
- **New `emMoveLine(a, lineId, targetId, after)`:** the block's line order changed (before / after the target line, or by a number: ±1); the entry's lines in the new order (the block's lines in the places its lines had among all lines); the rows of those lines put in that order into the places they had in `S.rows` (other rows stay). Log `emOrder`.
- **Drag and drop:** `onDragStart` keeps `block` and `group` for `em-line`; `dmTargetOf` – kind `em-line` onto another `tr.dci-em-line` of the same block and entry → target `em-order`; `onDragOver` toggles `dci-em-after` (new `emAfter(el, e)`: the lower half); `onDropOn` `em-order` → `emMoveLine`, `rerenderGroup`. `dmDragEnd` now removes every `dci-dm-drag-…` class of the overlay (before, `dci-dm-drag-em-chip` stayed after a chip was dragged) and `dci-em-after`.
- **`onKeydown`:** Alt+↑ / Alt+↓ on `.dci-em-grip` – `emMoveLine` by one, focus back on the line's ⠿.
- **CSS:** `.dci-em-grip`; while a line is dragged (`dci-dm-drag-em-line`) the line under the pointer shows a mark above it, or below it with `dci-em-after`.
- **Texts (English only):** `em.gripTitle`, `em.gripLabel`, `log.emOrder`.
- **Tests:** `t_entries.py` new case `order` (dragged before and after with the mark, Alt+↑ with the focus, not onto another entry's line, no ⠿ in a block of one line, the compact view, staged as before, a new import in the order of the source).

## Import 3.35.2 · 2026-10-29

Proper names of several words in T052, the note offers words one after another as a whole (collected item 144).

- **New `properPhrases(keep)`:** the entries with spaces of `PROPER_WORDS` (T052) and of the row's `keepCase`, each `{ re, spelling }` (a regular expression with the words separated by `\s+`, bounded by start/end or the separators of `caseCredit`), the longest first; cached by their text (`phraseCache`).
- **`caseCredit`:** first finds the phrases (not overlapping) and writes each as a whole in its spelling; the text between them word by word as before. New: with `caseCtx.runs`, words noted as written small that follow each other with only spaces between them are noted as a run ("Les Paul"); a phrase or any other word ends a run.
- **`roleCreditFor`:** `caseCtx` gets `runs: []`; new `row.creditPhrases` – the runs still in the credit.
- **`caseNoteHtml`:** the runs (`row.creditPhrases`) before the words, with the same buttons (`case-keep`, `case-always` with the whole as `data-word`). The compact line's "keep" buttons: the runs first. `caseKeep`/`caseAlways` unchanged (the key of `keepCase` is the lower-case text, with spaces for a phrase).
- **Register:** T052 note names the phrases; `where` with `properPhrases`. **Mapping file:** "Gibson Les Paul" and "Les Paul" in `PROPER_WORDS` (after "Gibson").
- **Texts:** none new (the note's texts take the whole as `{word}`).
- **Tests:** `t_text_basics.py` `casenote` now with "Guitar [Gretsch Duo Jet]" (Gibson Les Paul is a proper name of the register itself now; the run "Duo Jet" offered first); new case `casephrase` (Gibson Les Paul from the register, "Les Paul Junior", "Paul Reed Smith" offered as a whole, keep / write small again / always, a "Les" in a text stays small). `smoke/register_golden.json` written anew (T052).

## Import 3.35.1 · 2026-10-29

Index tracks of Discogs whose parts are tracks of their own (collected item 145).

- **`DISCOGS.toRelease`:** new `partOf(position)` ("C1a", "C1.b", "3-b" → C1, C1, 3; positions without a part letter unchanged – "A1", "D", "AA", "1-1"). An index track (`type_: 'index'`) without a position of its own whose sub-tracks have more than one base position: a track per base position (position the base, title the part's – of several parts of one base their titles joined with " / " –, the other positions as aliases, `work` the index's title), the index's `extraartists` on each of them, a part's on its own. With one base: one track as before, its position now the base when the index has none.
- **Tests:** `t_sources.py` new case `indextracks` (the release as on Discogs – 13 tracks, credits on the right ones –, the cases that stay one track, "AA"/"AB", in the dashboard four parts of one work on the four recordings).

## Import 3.35.0 · 2026-10-29 · milestone "Entries as a matrix"

Block AE (E4), the last step: an entry compact as a matrix.

- **`mxPerson(a)`, `mxEntry(a)`** (now also an entry in `S.emWide`: its full matrix in the compact view), **`mxCompact(a)`** (a person in the matrix view, compact or folded, not wide). `groupHtml`: `dci-em-centry` and `entryCompactHtml`; the arrow in the head of such an entry is `emWideHtml` (instead of `openAllHtml`). `rerenderRow`, `revealRow` (opens it wide), `add-role` (opens it wide), `updateGroupHeader` follow.
- **New:** `emWideHtml(a)`, `evShortHtml(e)`, **`emChipHtml(l, e)`** (`data-drag="em-chip"`, `data-ev`; a question with "?" and the word as written), **`entryCompactHtml(a, all)`** (by event: a line `.dci-em-cl[data-emev]` per event with its chips, `S.emShow` and "+ n more" – `S.emMore` key `e:<event>` –, "Taken out:"; by role: a line per role with its events), **`emMoveChip(a, lineId, fromEv, toEv, both)`**.
- **Drag & drop:** `onDragStart` keeps the event and the entry of a chip (`S.dmDrag.ev`, `.group`); `dmTargetOf` – a chip onto `.dci-em-cl[data-emev]` of another event of the same entry (`em-chip-ev`); `onDropOn` → `emMoveChip(…, e.shiftKey)`.
- **Clicks:** `em-by` (`S.emBy` per entry), `em-by-default` (`EM_BY_KEY` `dci-em-by`, `S.emByDefault`, ⚙ Staging), `em-wide` (`S.emWide`), `em-chip` (wide, the line flashes), `em-chipout` (`emTick` off). **`updateEntryMatrixStatus`:** `[data-emrows]` – the issues of the rows of a compact line.
- **Summary:** `sum.joined` (`data-el="sum-joined"`) – the relationships a row per instrument would be (the rows of the joined items).
- **Milestone:** `MILESTONES` 3.35.0, text `ms.3.35.0`.
- **CSS:** `.dci-em-compact`, `.dci-em-cl`, `.dci-em-chip` (`-ask`, `-chipx`), `.dci-em-sep`, `.dci-em-evchip`.
- **Texts (English only):** `em.wide`, `em.narrow`, `em.chipTitle`, `em.chipAskTitle`, `em.chipOut`, `em.by.event`, `em.by.role`, `em.noEvent`, `em.moreChips`, `em.out`, `settings.emBy`, `sum.joined`, `ms.3.35.0`.
- **Fixes after a review (an agent that had not seen the work read the new code):**
  - `joinPlan`: groups of staged relationships – joined ones (`joined`) and single ones with a `jkey` (`s:<key>`; `joinableKind(it)` gives every item of that kind its `jkey`, also in the legacy view); dirty also when the decision changed (a joined one no longer `joinable`, or singles of one `jkey` that are joinable now); a dirty group's items get `rejoinOf`, its removal `restage` (the keys of its rows staged anew). `joinable` = `joinableKind` + `joinOn`.
  - `applyPlan`: `restage` (a group changed in the editor itself – `relSig` – is left: its rows are not staged anew, `changedInMb`); a removal with `restage` only once all its keys hold a new staged entry; `forget` deletes a single key only if it still holds the old entry; `appliedKeys` not for the `join|…` key; staged singles keep `jkey`.
  - `emTick`: a spare row loses `scopeLevel`/`mxSkipped`; all rows of the line `dateKeyed`. `emEventDate`: its rows `dateKeyed`. `emDropDate`: the rows of a block from `entryModel(a, shownRowsOf(a))` (also behind "▸ n more" and folded); the tracks the date has (`inter`): all – it moves, part – a row of its own with those tracks and the original loses them, ⇧ – a row of its own (`emBoth`); `dateKeyed`; ↶ restores tracks and `dateKeyed`. `emBothAnswer`: the release level skips the row without a date. `lineAskHtml`, `emLineHtml`, `emChipHtml`: the first row not taken out. `emMoveChip`: `shownRowsOf`.
  - `onClick` (answers of a line): only rows not taken out; with rows on several levels each keeps its own where its type is there (`findRowType`). `onChange`: a field of a row opened below a line redraws the entry (`rerenderGroupSoon`). `rerenderGroup`: the focused field keeps the focus (the same `data-f` of the same row, line or event). The setting "Join …" also draws the entries anew.
- **Tests:** `t_entries.py` new case `compact` (the lines per event, a chip dragged onto another event, ✕, by role, ▸ / ▾, a chip clicked, the default by role, the summary), new case `restage` (One row each and Join in one block after staging; a joined relationship changed in the editor stays, the others are staged anew), `dates` E2 (a block with hidden lines); `join` C2 – a row taken out of a staged join (its tick off): the join staged anew without it; `t_ui_settings.py notice` – the three newest milestones are 3.35.0, 3.34.0, 3.33.0.

## Import 3.34.31 · 2026-10-29

Block AE (E4), step 3: dates in an entry's matrix.

- **`evHeadHtml`:** the date an input (`data-f="em-evdate"`, the pool's name above it); title `em.evTitle`. **`entryModel`:** events sorted also by their date (without first, then the earlier – `when(e)`), so their numbers stay.
- **New:** `rowsInEvent(a, evKey)`, **`emEventDate(a, evKey, text)`** (`parseDatePeriod`, `single`; rows with one date of the pool → that pool entry changes, all its rows and work links follow; else a pool date with that value or a new one – `newPoolId`; empty: no date; `savePool`, log `emEvDate`), **`emDropDate(t, entry, both)`** (onto `em-ev` / `em-line` / `em-block`: a row covered by the date – no cell of the date matrix for its date group, or all its tracks in it – gets the date; covered in part or with ⇧: `copyRowForEvent` with the date (and the cell's tracks), `dateKeyed`, `emBoth` with ⇧; `S.emUndo`, message `em.dateDropped` with the action `em-undo`, log `emDateDrop`), `emUndoDrop(id)`, **`bothAskHtml(l)`**, **`emBothAnswer(row, only)`**. `lineAskHtml` takes the line (with `bothAskHtml`).
- **Handlers:** `entryMatrixChange` `em-evdate`; `onClick` `em-undo`, `em-only`, `em-both`; **`dmTargetOf`**: `th.dci-em-ev[data-evhead]`, `.dci-em-bhead`, `tr.dci-em-line` for a dragged pool date; **`onDropOn`**: those → `emDropDate(t, entry, e.shiftKey)`.
- **CSS:** the date field of the head, the targets while a date is dragged (`.dci-dm-drag-date`), `.dci-dm-over`.
- **Texts (English only):** `em.evTitle`, `em.evDateLabel`, `em.badDate`, `em.dateDropped`, `em.undo`, `em.bothAsk`, `em.bothOnly`, `em.bothKeep`, `log.emEvDate`, `log.emDateDrop`.
- **Tests:** `t_entries.py` new case `dates` (a date onto a line – it moves –, ↶, onto the head of an event, typed into two heads – a new pool date, the pool's own date changed –, with ⇧ onto a block: both, the questions answered, what is staged); `matrix`: the event heads without "no date" (a field now).

## Import 3.34.30 · 2026-10-29

Block AE (E4), step 2: an entry as a matrix in the full view.

- **New section "[E4] (3.34.30) An entry as a matrix"** before `groupHtml`: `mxEntry(a)` (matrix, full view, not folded, persons only), `ltOf(r)` (the type of a skipped row too), `dateKeyOf`, `eventKeyOf` (level · tracks · date), `lineKeyOf` (type, instrument, role credit, flags, artist credit; rows without a type each their own), `lineKindOf`, `circled`, **`entryModel(a, rows)`** (lines with their rows per event, events sorted – recordings first, more tracks first –, blocks: instruments / voices joined when `joinOn(a)`, else each line; per block its events: all up to `S.evShared`, else its own and `S.emBlockEv`), `evHeadHtml`, `typeOnLevel`, `lineAskHtml`, `emLineHtml`, `emBlockHtml`, **`entryMatrixHtml(a, rows)`** (work-level rows stay rows below), `lineRows(el)` (`data-rows`), `copyRowForEvent`, **`emTick(a, rows, evKey, on)`** (on: a skipped row of the line or a copy takes the event's level, tracks, date, `dateKeyed`; off: Skip), `entryMatrixChange(f, el)` (`em-tick`, `em-flag`, `em-primary`, `em-credit`, `em-addev`), `entryMatrixInput`, `EM_LINE_ACTS` (type-pick, instr-pick, instr-misc, voice-credit, case-keep, case-small – for all rows of the line), `updateEntryMatrixStatus(rowInfo, items)` (`data-emstatus`, `data-emcount`), `rerenderGroupSoon(a)`.
- **`groupHtml`:** `dci-em-entry` and `entryMatrixHtml` for a matrix entry instead of the table; `updateGroupHeader` keeps the class. **`rerenderRow`:** a row of a matrix entry redraws its entry (soon). **`revealRow`:** opens the line's rows. **`add-role`:** the new row's line open. **`refresh`:** `updateEntryMatrixStatus`. **`onChangeInner`:** `em-…` → `entryMatrixChange` (not `mx-…`, which is the works matrix). **`onInput`:** `em-primary`, `em-credit`. **`onClick`:** answers of `.dci-em-ask` for all rows; `em-detail`, `em-remove`, `em-more`, `em-fold`, `em-join`, `em-split` (`artist.join`).
- **State and settings:** `S.emOpen`, `S.emMore`, `S.emFold`, `S.emBlockEv`; `EV_SHARED_KEY` `dci-ev-shared` (`S.evShared`, 1–12, 3), `EM_SHOW_KEY` `dci-em-show` (`S.emShow`, 1–50, 8) in ⚙ Staging (`data-set="ev-shared"`, `"em-show"`), `clampInt`.
- **CSS:** `.dci-em`, `.dci-em-block`, `.dci-em-bhead`, `.dci-em-grid` (the role column sticky), `.dci-em-ev`, `.dci-em-skip`, `.dci-em-ask`, `.dci-em-detail-row`, `.dci-em-foot` …
- **Texts (English only):** `em.*` (31), `settings.evShared`, `settings.evSharedAfter`, `settings.evSharedTitle`, `settings.emShow`, `log.emOut`, `log.emIn`, `log.emJoin`, `log.emSplit`.
- **Tests:** `t_entries.py` new case `matrix` (the block of Multi Man, ▸ rows, guest ticked, more events than shared – fold, One row each, ＋ Event, a tick –, a line taken out, One row each, what is staged); `join` types the role credit in the line. `harness.py`: `ENTRIES_PRESET` also sets the generation of the stored data (`dci-store-epoch`) – without it the script cleared "legacy" at its start for the cases that open the page without a view (`view=None`). `t_ui_view.py levels`: the ↺ of Appearance sets the entries back to the matrix; the case switches to Legacy again.

## Import 3.34.29 · 2026-10-29

Block AE (E4), step 1: the entries as a matrix the default, "Legacy" as before; joining when staged.

- **Settings:** `ENTRIES_VIEW_KEY` `dci-entries-view` (`S.entriesView` 'matrix' | 'legacy', only 'legacy' stored; ⚙ Appearance, segment `data-act="entries-view"`, `setEntriesView(view)`: `renderGroups`, `refresh`, `renderSettings`), `JOIN_KEY` `dci-join` (`S.joinAuto`, only off stored; ⚙ Staging `data-set="join"`, disabled in legacy). Both in `TOPIC_KEYS` (appearance, staging; their ↺ set them back) and `SETTINGS_KEYS`.
- **New section "[E4] Entries as a matrix"** after `computePlan`: `matrixOn()`, `joinOn(artist)` (`artist.join` true/false wins over the setting – for the buttons of later steps), `primaryAttrsOf(it)` (attributes under the type's own root), `joinable(it)` (a new credit item of type instrument or vocal on a recording, the release or its group, with an instrument or voice), `joinKeyOf(it)` (target, entry, type, date, artist credit, other attributes, direction), **`joinPlan(items, removals, stagedItems)`**.
- **`joinPlan`:** (1) joined relationships staged before (`S.staged` entries with `joined`, `jkey`) are "dirty" when an item updates or replaces one of their rows, a row of them is to be removed, or a new joinable item has their `jkey`: those items become fresh adds (`rejoin`), the unchanged rows' items (`stagedItems`, recorded in `planTarget` when the staged sig is the same) are added again, and one removal per dirty join (`{ key, staged, joined }`) replaces the removals of its rows. (2) With `matrixOn()`: joinable items are bucketed by `joinKeyOf`, a bucket takes no attribute twice (a second bucket instead); a bucket of several becomes one item with `joinedItems`, `jkey`, the attributes of all, `key` `join|…`.
- **`computePlan`:** `stagedItems`; returns `joinPlan(items, removals, stagedItems)`. **`applyPlan`:** a joined item is staged once and stored under each row's key (`joined: 'j<state id>'`, `jkey`, the row's own sig); edit-note lines of all rows; removals of a join forget all keys of that join (`forget`), not those staged anew in another join just now. **`describeItem`:** a joined item names its instruments.
- **Texts (English only):** `settings.entries`, `settings.entries.matrix`, `settings.entries.legacy`, `settings.entries.matrixTitle`, `settings.entries.legacyTitle`, `settings.join`, `settings.joinTitle`.
- **Tests:** new file `smoke/t_entries.py` (case `join`: the matrix joins – 20 relationships instead of 33 –, a role credit typed after staging stages the joins anew, the legacy view stages the same instruments apart, the switches). `harness.py`: `ENTRIES_VIEW` ('legacy' for the files written before E4) and `ENTRIES_PRESET` (`dci-entries-view` before the script starts).

## Import 3.34.28 · 2026-10-29

Unknown words in lower case also in Discogs brackets, with a note at the row; proper names of the register (S052a/b, T052).

- **Mapping file:** new list `PROPER_WORDS` (before `ART_TYPES`), table T052, editable (`EDITABLE_LISTS` shape `words`, spelling kept).
- **New `properSpelling(w, keep)`** (a word kept at the row, else T052), **`knownWord(w, vocab)`** (T002, MusicBrainz's instrument words, `SMALL_ENGLISH`), **`lowerWord(word, vocab, keep)`** (proper names of T052 and MusicBrainz, digits; a whole hyphenated word first, then its parts). `caseWord` gets `keep` and checks T052 first.
- **`caseCredit(text, vocab, { lowerUnknown, quiet })`:** with `lowerUnknown` through `lowerWord`; a word written wholly small that is not known is pushed to `caseCtx.lowered` unless `quiet`. **`caseCtx`** (module level) is set by `roleCreditFor` for the row: `{ lowered, keep: row.keepCase }`; `roleCreditFor` stores `row.creditLowered` (the noted words still in the credit).
- **`creditCasing(lt)`:** `lowerUnknown` also with S052 (before: only voices, S034). **`wordingCredit`:** `lowerUnknown` with S052, quiet. **`lowerCredit(text, { off, quiet })`:** quiet for R086 and for the task of a role the register knows (noted only with the note `unknownRole`).
- **UI:** `caseNoteHtml(row)` in `.dci-case-slot` below the role credit field ("Written small – …" with `case-keep` / `case-always`, "Kept as written: …" with `case-small`); `updateCaseNote(row)` after typing; the compact line gets `.dci-cl-case` with `case-keep`. **New `caseKeep(row, word, keep)`** (`row.keepCase = { lower: Written }`), **`caseAlways(row, word)`** (`putListChange` on T052, `mappingChanged('T052')`, log `caseAlways`). CSS `.dci-case-note`, `.dci-cl-case`.
- **Rules:** S052 and S011 notes, new T052 in TABLES.
- **Texts (English only):** `caseNote.small`, `caseNote.word`, `caseNote.keep`, `caseNote.always`, `caseNote.alwaysTitle`, `caseNote.kept`, `caseNote.smallAgain`, `caseNote.clTitle`, `cl.caseSmall`, `log.caseAlways`.
- **Tests:** new case `t_text_basics.py casenote` (Discogs "Guitar [Gibson Les Paul]": note, compact line, keep, write small again, always – stored in T052 and used by a second row; a text: "Sticks-And-Stones" noted, "Buddha machine" kept; a known role without note); `instrguess`: "Buddha machine" again with its capital; `t_rules_window.py ruleedit`: T052 among the editable lists; `register_golden.json` rewritten (82 wordings in lower case, "Fender Rhodes" and "Hammond B3" now with their capitals, S011, S052, T052).

## Import 3.34.27 · 2026-10-29

Role credits and tasks in lower case, proper names keep their capitals (rule S052, maintainer's rule of 2026-10-29).

- **New `lowerCredit(text, { off })`:** `caseCredit(text, instrumentVocabulary(), { lowerUnknown: true })` – only the proper names of MusicBrainz's instruments (`vocab.proper`) and words with digits keep their capitals. S052 off: `norm` (`off: 'lower'`, the default) or the text as written (`off: 'written'`).
- **New `creditCasing(lt)`:** the casing of the details as role credit for a relationship type (S011 artwork in lower case, S034 voices with `lowerUnknown`, otherwise `caseCredit`), taken out of `roleCreditForInner` unchanged; also used for the suggestions of the field.
- **`roleCreditForInner`:** the credit of "other instruments" for a word MusicBrainz does not know is `guessCredit(row.instrGuess)` (before: `instrGuess.word` as written); the task (`creditFromRole`) and the credit of R086 go through `lowerCredit` (before: `norm`).
- **New `guessCredit(g)`, `guessTask(g)`:** the role credit and the task of such a word as they are set; `instrGuessHtml` and the compact line (`clineAskHtml` "instr") name them in the buttons "other instruments “…”" and "miscellaneous support (task “…”)" – the question itself keeps the word as written.
- **`roleCreditOptions(raw, base, mods, suggestion, typeName, cased)`:** new last parameter `cased` (default: the text as it is – the node run of `t_register.py` and its golden are unchanged); the field passes `creditCasing(lt)` when S052 is on (before: the Discogs variants exactly as written).
- **Rules:** new S052 in SPECIAL_RULES (after S051).
- **Texts (English only):** `instrGuess.none` names the credit with the new placeholder `{credit}`; `instrGuess.noneOr` without "– as written".
- **Tests:** `t_text_basics.py instrguess` – "other instruments" credited "chaims", "buddha machine"; `unknownask` – the buttons and credits in lower case (A, B), new D ("Tambourine [Additional, Toy]": the suggestions of the field `toy · additional, toy · additional · additional tambourine · toy tambourine`) and E ("Hammond Manager" with the attribute "Hammond organ": other instruments “Hammond manager”, after "miscellaneous support" the task "Hammond manager"). `register_golden.json` rewritten (only the row of S052 is new).

## Import 3.34.26 · 2026-10-29

Words that are no instrument ask everywhere, with "miscellaneous support" as the last answer (collected item 137d (c)).

- **`TEXT.parse`, "Name – roles":** the unknown parts that `maybePlayable` passes – when the line has at least as many instruments known (`playable`) – are credits with `guess: true`, in their order; the others stay unknown parts (not recognized). With S051.
- **`makeRow`:** an R096 role that is no instrument of MusicBrainz goes through `guessInstrument(row, { word })` (before: `makeMiscRow`); `remapRow` keeps a question asked (and "miscellaneous support" if chosen) or asks it.
- **`guessInstrument`:** `row.instrGuess` gets `misc` (offered; not for technicians), `level` and `chose`; new **`guessMisc(row)`** (action `instr-misc`, also `\u0000misc` from the compact line's list) – `makeMiscRow` with the word as task – and **`guessUnMisc(row)`** (in `pickInstrument`: an instrument row again, on its level). **`instrGuessHtml`:** the answer "miscellaneous support (task “…”)" (`instrGuess.misc`), with none like it the answers other instruments (chosen) · miscellaneous support (`instrGuess.noneOr`). **`roleCreditForInner`:** with "miscellaneous support" chosen the task as before.
- **Texts:** new `instrGuess.misc`, `instrGuess.noneOr` (English only).
- **Header / files:** `@version 3.34.26`, `?v=3.34.26`, both files' `version`.
- **Tests:** `t_text_basics.py` – new case `unknownask`, `names` (B: "sticks-and-stones" a row of its own); `text_corpus.json` – 3 lines; `register_golden.json` written anew (the dashboard of the register: trumpet, clarinet and sticks-and-stones rows instead of not recognized).

## Import 3.34.25 · 2026-10-29

"Voice" from every source with four answers (collected item 137e); instrument technicians with their instrument (137f). Rule (maintainer): the mapping is the same for every source, exceptions only where a site needs them (Q007 stays Bandcamp's).

- **Q011** (mapping file): a fourth answer "spoken vocals “voice”", its note. **`askVoice(row)`** for every source (not companies) – also Discogs – and in `suppRow` for a supplement.
- **R086** (mapping file): its pattern also "bass, drum(s), keyboard(s), synth, organ, percussion, strings … technician / tech", its note; its code takes the instrument from the word before "technician" / "tech" / "tuner" (not "instrument") or from a detail (consumed) as `primaryCands` (`instrumentCandidates(…, { head: false })`: T001 spellings); "tuner" keeps its credit. **`roleCreditForInner`:** an R086 row with an instrument gets no role credit but the tuner's. New **`askTechnician(row)`** – an instrument MusicBrainz does not know asks through `guessInstrument(row, { word, misc: false })` (new options `word`, `misc`: no miscellaneous support).
- **`suppRow`:** `guess` into `makeRow`; `askVoice`, `guessInstrument`, `askTechnician` as in the import.
- **Header / files:** `@version 3.34.25`, `?v=3.34.25`, both files' `version`.
- **Tests:** `t_text_basics.py` – new case `voicetech` (Discogs); `register_golden.json` written anew (R086, Q011).

## Import 3.34.24 · 2026-10-29

Text from cover art (beta): the origin in the head of an entry (collected item 130d).

- **New:** `coverHits(refs)` (the images and crops of lines of the text read, none for another text) and `coverFromLine(hits, key, act, most)` (the line with ⓘ and the crops while `key` is in `S.cropOpen`) – `coverFromHtml(row)` uses them now (4 crops); new **`coverFromEntryHtml(a, rows)`** below the head of an entry (`.dci-gcoverfrom`, the lines of all its rows but supplements, 6 crops, key `g:<entry>`), action `cover-crop-entry` (`rerenderGroup`). Crops shown once for the same crop.
- **CSS:** `.dci-gcoverfrom`.
- **Header / files:** `@version 3.34.24`, `?v=3.34.24`, both files' `version`.
- **Tests:** `t_coverart.py` – new case `ocrentry`.

## Import 3.34.23 · 2026-10-29

An arrow at the compact view (collected item 143); "in front" of the cover art window as a setting (138b).

- **New:** `HINT_COMPACT_KEY` (`dci-hint-compact`: true once seen and switched or closed; set at the start when the compact view is stored), `compactHintOn()`, **`renderCompactHint()`** (after `buildOverlay` and ↺ of Appearance: `.dci-hint-compact` after `[data-act=view-toggle]` – a zero-size anchor with `.dci-hint-bubble` below, `pointer-events: none` but ✕), **`compactHintDone()`** (the actions `view-toggle`, `view` – when the view changes – and `hint-compact-close`; not `setView` itself, so resets do not count). The key in `TOPIC_KEYS.appearance` and `SETTINGS_KEYS`.
- **New:** `OCR_FRONT_KEY` (`dci-ocr-front`, false when off), `S.ocrFront`; `ocrKeepOnTop` does nothing when off; ⚙ Settings → Beta `data-set="ocr-front"` (`settings.ocrFront`); in `TOPIC_KEYS.beta`, `SETTINGS_KEYS`, the resets.
- **CSS:** `.dci-head:has(.dci-hint-compact)` (above the content), `.dci-hint-compact`, `.dci-hint-bubble` (with its tip), `@keyframes dci-hint-in` (none with reduced motion).
- **Texts:** new `hint.compact`, `hint.close`, `settings.ocrFront`, `settings.ocrFrontTitle` (English only).
- **Header / files:** `@version 3.34.23`, `?v=3.34.23`, both files' `version`.
- **Tests:** `harness.py` – `VIEW_PRESET` also stores the arrow as seen (it stands below the head); `t_ui_head.py` – new case `compacthint`; `t_coverart.py` ocrwindow – part E.

## Import 3.34.22 · 2026-10-29

Text from cover art (beta): the image and the place of each row's line (collected item 130c).

- **New:** `OCR_CROP_W` 640, `OCR_CROP_H` 160, `ocrLineKey(t)` (the line in small letters, spaces joined), **`ocrCrop(canvas, box)`** (the line with a margin as a JPEG `data:` address, '' if it cannot be: try/catch), **`ocrLineOrigins(text)`** (every line of the parts as checked → `[{ what: ocrTypes(img), crop, text }]`, its place by `ocrLineFor` on `pt.lines` of 3.34.12).
- **`ocrImport`:** `S.ocrLines = ocrLineOrigins(text)` before the window closes (not for a supplement); in memory only.
- **Rows:** new **`coverFromHtml(row)`** in `roleCell` (people and companies) – while `S.source` is TEXT and `S.textInput.text` is the text of `S.ocrLines`: the images of the row's lines (`row.srcRefs[].line`), "From the cover art · …" (`cover.from`), ⓘ (`data-act="cover-crop"`, `aria-expanded`) for the crops; `S.cropOpen` (row ids with their crops shown), action `cover-crop`.
- **Texts:** new `cover.from`, `cover.cropTitle` (English only). **CSS:** `.dci-coverfrom`, `.dci-coverfrom-crops`.
- **Header / files:** `@version 3.34.22`, `?v=3.34.22`, both files' `version`.
- **Tests:** `t_coverart.py` – new case `ocrorigin`.

## Import 3.34.21 · 2026-10-29

Mapping rules: wording rules and questions of your own – "＋ New rule" (collected item 121b).

- **Stored:** in your changes (`dci-mapping-changes`) as `rules[id] = { set: all fields, was: {}, add: 'wording' | 'question' }`; ids `OWN_DATA_ID` (W901 …, Q901 …; `nextOwnDataId(kind)`); new `OWN_DATA_KEYS`, `isOwnDataId(id)`, `ownDataKind(id, changes)` (also the last answer of `ruleKindOf`).
- **`effectiveRaw`:** the rules of your own (`ownDataKind`) go before the built-in ones of `WORDING_RULES` / `QUESTION_RULES`, in the order of their ids; **`applyMappingChanges`:** the three arrays of W and Q in the order of the effective register (the objects of built-in rules kept, the rules of your own come and go).
- **Checks:** `checkRuleSet(id, set, kind = ruleKindOf(id))`; new `checkOwnRule(id, kind, set)` (all fields: a wording rule its words – the credit may be empty –, a question its word and instruments); `putRuleChange(…, add)` keeps a rule of your own whole.
- **Window:** `sect(…, extra)` – **"＋ New rule"** (`data-redit-new="wording" | "question"`, `openNewRule(kind)`: `S.ruleEdit = { id, draft, error, add }`) in the headings; the form of a rule not saved yet below its table (`data-rnew`); `noteOf(r)` ("your rule"); `ruleEditHtml`, `dataRuleEditHtml` (legend `mapping.ownTitle`, `mapping.ownHint`), `saveRuleEdit` (a rule of your own through `checkOwnRule`), `ruleEditActions` and `changesHtml` ("✕ delete this rule", "your rule" with its fields), `editToolsHtml` (tag "yours", `.dci-own`), `resetMappingChange` (asks `mapping.deleteOwnAsk`).
- **Import:** `takeRule(id, set, was, add)` – a rule of your own with `add` (its id must fit its kind) through `checkOwnRule`; from a whole register the W9xx / Q9xx of its wording rules and questions; `planImport` passes `add`; the preview takes the fields of a rule only the import has.
- **Rows:** `isKnownRole` – a word a question asks about is a role (texts: "Key Man – keys"); `makeRow` – no "miscellaneous support" for a word a question asks about (the row stays an instrument and asks).
- **Texts:** new `mapping.newRule`, `mapping.newWordingTitle`, `mapping.newQuestionTitle`, `mapping.ownTitle`, `mapping.ownHint`, `mapping.ownTag`, `mapping.ownNote`, `mapping.ownChange`, `mapping.deleteOwn`, `mapping.deleteOwnAsk` (English only). **CSS:** `.dci-changed.dci-own`, `.dci-mchg-own`, `h3 .dci-rnew-btn`.
- **Header / files:** `@version 3.34.21`, `?v=3.34.21`, both files' `version`.
- **Tests:** `t_rules_window.py` – new case `wqnew`; `register_golden.json` written anew (the headings with "＋ New rule").

## Import 3.34.20 · 2026-10-29

Texts: words that are no instrument of MusicBrainz, "Voice", more spellings (collected item 137d).

- **`TEXT.parse`:** a word of a list of instruments (S051: blocks, one line, "X plays …") that is no known instrument is a credit with `guess: true` (before: listed as not recognized); the parts of a one-line list in their order (`playList` gives `parts`).
- **`groupCredits`:** `entry.guess`; **`makeRow`** – new option `guess` (no "miscellaneous support" for it); after the row of a text or Bandcamp credit: `askVoice(row)` and, for a guess, `guessInstrument(row)`.
- **New `editDistance(a, b, max)`, `similarInstruments(word, most = 5)`** (the children of the instrument root of `idx()`, names and aliases: 2 letters off from 6 letters, 1 from 4; a word of a name so, + 0.5; not "other instruments"), **`guessInstrument(row)`** (`row.instrGuess = { word, options, other }`; none like it: `primaryText` "other instruments"; without that in MusicBrainz and without options: `makeMiscRow` as before), **`instrGuessHtml(row)`** (`.dci-instr-guess`, `data-act="instr-pick"` – `pickInstrument` as for Q001), the compact line asks too (`cl.instrGuess`).
- **`roleCreditForInner`:** a guess – the word for "other instruments", none for a similar instrument; `askVoice` – none until answered or for plain vocals.
- **Q011** (mapping file, `TYPE_QUESTIONS`: rule R015, `flag` askVoice, new `keep` – `blankForQuestion` keeps the type; options with the new `plain` – `pickType` clears the voice), **`askVoice(row)`** (R015, base "voice" without details, text or Bandcamp; plain vocals until answered); **`voiceCreditHtml(row)`** in `.dci-voice-slot`, **`updateVoiceCredit(row)`** after the voice or the role credit typed; action `voice-credit` (role credit "voice", touched).
- **T001:** bongo → bongos, woodblock(s), wood blocks → wood block.
- **Texts:** new `instrGuess.ask`, `instrGuess.chosen`, `instrGuess.other`, `instrGuess.none`, `cl.instrGuess`, `voiceCredit.from`, `voiceCredit.use`, `typeAsk.askVoice`, `typeAsk.pendingVoice` (English only).
- **Header / files:** `@version 3.34.20`, `?v=3.34.20`, both files' `version`.
- **Tests:** `t_text_basics.py` – new case `instrguess` (the harness gets chimes, wind chimes, tubular bells "orchestral chimes", other instruments, other vocals), `playedby` – nothing not recognized now; `t_textcorpus.py` – a guess marked "asked: no known instrument" (1 line changed); `register_golden.json` written anew (T001, Q011).

## Import 3.34.19 · 2026-10-29

Texts: instruments and the name they are played by (collected item 137a, new rule S051; word lists T049, T050).

- **New word lists** (mapping file, with register entries): **T049 `TEXT_PLAY_VERBS`** (played, performed, sung, plays, performs, sings, sang) and **T050 `TEXT_AUX_WORDS`** (are, is, were, was, been, all, both).
- **`TEXT.parse`, new helpers:** `playable(x)` (a known role the register maps to instrument or vocal only), `maybePlayable(x)` (up to three words of letters, no role of another kind), `playList(side)` (`{ known, unknown }` – at least one instrument, no fewer than unknown words), `chainOf(t)` (the verbs before "by" at the end of a phrase, one of T049, the words of T050 before them left out → `{ before, roles }`, the roles of the other verbs via `roleOf`), `playedList(t)`, `PLAYS_LIST` ("X plays …").
- **One line:** the "… by …" branch of `readClause` reads `playedList` of the phrase as written (before `TEXT_CONTRIBUTION`; not with titles, not with `TEXT_WHAT_WORDS`): each instrument and each other role for each name, the unknown words as unknown parts. New clause check before "Name – roles": `PLAYS_LIST` with a name in capitals and `playList`.
- **Blocks:** the line loop is now `readLine(raw)` (the former body; `continue` → `return`) with `startLine(raw)` (line0, n0, part0); a line of `blockLine` (only instruments or unknown short words; no digit, ":", brackets, dash, "by", "at", "in" …) is held in `roleBlock`, empty lines with it; `readBlock(held, linkRaw)` with `linkOf` ("(all instruments | all of the above …) (are …) played, mixed … by X") – from the first line with an instrument (the lines before it through `readLine`), at least as many instruments as unknown words: each instrument a credit of each name (its own line as `line`), a line with unknown words listed (whole, or "→ ? “…”"), the other roles on the linking line; any other line (and the end) reads the held lines with `readLine` first (`flushBlock`).
- **`byRole`:** `AUX_BEFORE_VERB` – the words of T050 before a verb are left out ("are played" → "Played By", before "Played By [Are]").
- **Register:** new rule **S051**.
- **Header / files:** `@version 3.34.19`, `?v=3.34.19`, both files' `version`.
- **Tests:** `t_text_basics.py` – new case `playedby` (the text of Go Kurosawa, `GK_TEXT`, with instruments of MusicBrainz `GK_INSTRUMENTS`; in one line); `text_corpus.json` – 6 lines; `register_golden.json` written anew (S051, T049, T050).

## Import 3.34.18 · 2026-10-29

Texts: a place after "in", the year before the month (collected items 137b, 137c); the window "Text from cover art" stays in front (138).

- **New `ocrKeepOnTop()`:** `#dci-ocr`, while open, gets `++topZ` (its larger view `#dci-ocr-peek` above it); called by `bringToFront(kind)` for every kind but `ocr` (dashboard, log, rules) and by `renderRules` when the rules open as a window of their own.
- **New word list T051 `TEXT_PLACE_WORDS`** (mapping file; `(?<![\p{L}])(?:studios?|hall|church|chapel|cathedral|abbey|basilica|club|theat(?:re|er)|auditorium|arena|ballroom|caf[eé]|venue|tavern|pub|lounge)(?![\p{L}])`, flags `iu`), with its register entry.
- **`TEXT.parse`:** new `placeIn(verb, text)` – the first part of `text` (before a comma; a date of T047 cut off, "the" left out) has a word of T051 and a word in capitals besides it → `place(verb, placeOf(text))` ("Recorded At" with the area). Tried before `inArea` in the three places an "in …" is read (`inL` "Recorded in X by Y", `inR` "Recorded by Y in X", the clause "Recorded in X" alone); new: the clause "Recorded in the X" (only as a place). `place()` returns whether it added the place.
- **T047 `PLACE_DATE_TAIL`** (mapping file): a second form – a date with its year first right after the area, without a preposition (`\s+(?=\d{4},?\s+<month>\b)`); its register note says so.
- **New date rule D024** (`DATE_RULES`, `DATE_MATCHERS`): year, month, day – month, day; year, month, day – day; year, month – month (also "and", "&", "/") – these before D017; one month after its year after D008 – the year only when a word in capitals follows on the same line (not after a dot) or for "may" written small.
- **Header / files:** `@version 3.34.18`, `?v=3.34.18`, both files' `version`.
- **Tests:** `t_coverart.py` ocrwindow – part D (in front after a click into the dashboard, the rules as a window – `dci-rules-place` – and a click into them and into the log; z-index the highest), ocrauto – the window closed before it is opened again from the menu of the dashboard (it is in front of it now); `t_text_places.py` – new case `recordedin`; `text_corpus.json` – 7 lines (places after "in", D024 after an area); `register_golden.json` written anew (D024, T047, T051).

## Import 3.34.17 · 2026-10-28

Text from cover art (beta): frames remembered for each release and image (collected item 133).

- **New:** `OCR_FRAMES_KEY` (`dci-ocr-frames`: { release MBID: { t, imgs: { key: { f: [[x, y, w, h] as parts 0 … 1], turn, mode } } } }), `OCR_FRAMES_MAX` 50; **`ocrFrameKey(img)`** (`caa:<id>`, `file:<name>:<size>`, `url:<address>`, `pdf:<address or file>:<page>`), `ocrSavedFor(img)`, **`ocrSaveFrames(img)`** (after a frame drawn, changed or removed, a turn, "whole"/"frames"; nothing left: the entry goes; the oldest releases beyond 50 go), `ocrTakeSaved(images)` (when images come into the window: `img.saved`, "whole" at once), **`ocrRestoreFrames(img)`** (when a canvas is made: turned as stored, frames from their parts).
- **Changed:** `ocrCanvasLoad` sets `turn: 0` for every new canvas and restores (also after another image size: the frames come back); the small images beside the frames count the stored frames of an image not loaded yet; `forgetImport` drops the release's entry; `OCR_FRAMES_KEY` in `TOPIC_KEYS.beta` and `SETTINGS_KEYS`.
- **Header / files:** `@version 3.34.17`, `?v=3.34.17`, both files' `version`.
- **Tests:** `t_coverart.py` – new case `ocrremember`.

## Import 3.34.16 · 2026-10-28

Text from cover art (beta): large collections 12 at a time (collected item 131).

- **New:** `OCR_BATCH` 12; each image has `shown` – the release's first 12 (`openOcr` after `ocrList`), of each batch of own files, Discogs images and PDF pages the first 12, an address added at once; `ocrPickHtml` marks every image ticked as shown and draws only those shown, with **"Load n more (m not shown yet)"** `[data-ocr=more]` (the next 12 shown) and **"All shown (n)"** `[data-ocr-shown]` (while some are not shown; half ticked like "All images"; `ocrChange` ticks or unticks those shown).
- **Frames step:** the small images 12 at a time (`S.ocr.thumbsShown`; the one shown always), `[data-ocr=morethumbs]` shows 12 more.
- **`ocrCreditText`:** "Role by Name" is also looked up as "Role By" ("Mastered By" in the register) – a PDF page with "Mastered by Bob Producer" was not picked by Auto-select (3.34.15).
- **Texts (English, OCR):** new `ocr.allShown`, `ocr.more`. **CSS:** `.dci-ocr-more`.
- **Header / files:** `@version 3.34.16`, `?v=3.34.16`, both files' `version`.
- **Tests:** `t_coverart.py` – new case `ocrmore`.

## Import 3.34.15 · 2026-10-28

Text from cover art (beta): no image ticked at first, "Auto-select"; loading off by default, at most 24 ahead, after "Next"; a line zoomed in on (collected items 136, 128b, 130b).

- **Auto-select:** `OCR_AUTO_KEY` (`dci-ocr-auto`), `S.ocrAuto` (off by default); new **`ocrCreditText(text)`** (℗/©, or a line "Role – Name", "Name – role", "Role: Name", "Role by Name" whose role `isKnownRole` knows), **`ocrAutoPick(im)`** (the release's images of `OCR_CREDIT_TYPES`, PDF pages with their own text that has credits), **`ocrAutoApply(images)`** (ticks them, `autoSel`), **`ocrSetAuto(on)`** (stores it; on – applied at once; off – the images with `autoSel` unticked; the settings' checkbox follows). `ocrList` ticks nothing (`sel: false`) and applies Auto-select when it is on; PDF pages keep their own text (`pdfText`, at most 20,000 letters), are not ticked, Auto-select applied; Discogs images `sel: false`. A tick changed by hand (one image, "All images") clears `autoSel`. The switch: `[data-ocr=auto]` (`aria-pressed`) in the head of the choice; ⚙ Settings → Beta `data-set="ocr-auto"` (while the beta is on), in `TOPIC_KEYS.beta`, `SETTINGS_KEYS`, the defaults and `resetTopic('beta')`.
- **Loading:** new **`ocrFile(img, { ahead })`** (the file loaded once and kept as `fileBlob` with `fileSize`; its state shown; `filePromise` shared), `ocrHasFile`, `ocrHasCanvas`; `ocrCanvas` makes the canvas from `ocrFile` (`ocrCanvasLoad`). `OCR_PRELOAD_MAX` 24; `S.ocrPreload` off by default (stored `true` when on); new **`ocrLoadQueue()`** (choosing: the first 24 ticked if loading ahead is on; frames: all to be read, the one shown first; reading: those still to come) and `ocrToLoad(im)` (not a PDF page, nothing there or on its way); `ocrPreloadPump` loads the files of the queue, two at a time (in every step but the result); `ocrPreloadDrop` also stops a file loaded ahead; "waiting to load" for the images in the queue; another image size drops the release's files.
- **Line zoomed in on:** `ocrZoomTo(key, box, fw, fh)` (a word 0.5 / 0.34 of the view, a line 0.95 / 0.5); `ocrLocateLine` zooms in on the line; `ocrZoomShow` is gone.
- **Texts (English, OCR):** new `ocr.auto`, `ocr.autoTitle`, `settings.ocrAuto`, `settings.ocrAutoTitle`; changed (English only) `ocr.pickHint`, `settings.ocrPreloadTitle`.
- **CSS:** `.dci-ocr-auto[aria-pressed="true"]`.
- **Header / files:** `@version 3.34.15`, `?v=3.34.15`, both files' `version`.
- **Tests:** `t_coverart.py` – new case `ocrauto`; `beta_on` switches Auto-select on (unless `auto=False`); `ocrpdf` (the drawn page ticked by hand), `ocrdiscogs` (not ticked), `ocrload` (loading ahead switched on for A and B; after "Next" the others too), `ocrlocate` (lines zoomed in on).

## Import 3.34.14 · 2026-10-28

Text from cover art (beta): the window keeps its size, is moved and resized; text fields by their text; a plain background (collected items 134, 130, 135).

- **Window:** `GEOM_KEYS.ocr` (`dci-geom:ocr`), `defaultGeom('ocr')` (1400 px × its unit at most, 92 % high, 4 % from the top, centred), `bringToFront('ocr')`; `renderOcr` calls `makeMovable(el, '.dci-ocr-head', 'ocr')` when it makes the window (placed, moved by the head, size remembered, put back by ⤢ `window-reset` and the reset of all settings) and watches its size (`ocrResize`, a ResizeObserver: the frames view or the parts fitted again; disconnected in `closeOcr`). The class `dci-ocr-wide` and its rule are gone. CSS: `#dci-ocr` without `left: 50%`/`transform`, `height: 92vh`, `resize: both; overflow: hidden`, minimum 420 × 320 px; its head `cursor: move`.
- **Frames step:** `ocrCurrent` scales to `S.ocr.viewBox` (measured) instead of `OCR_VIEW` (only until then); new **`ocrFitView()`** (the room in `.dci-ocr-stage` measured, the view canvas sized to it, drawn); `ocrDraw` sets `data-k` on the view (its scale – the tests drag in the image's pixels). CSS: the frames body in one row, the stage `flex: 1 1 0`, the side 300 px and scrolling on its own; below 700 px one above the other. "Next image →" stays, disabled on the last image.
- **Text fields:** `OCR_TEXT_LINES` 20, new **`ocrFitText(ta)`** (as high as its text, scrolls beyond); called by `ocrZoomAll` and on input; `rows` from the text (2 – 20); the `minHeight` of 3.34.11 in `ocrZoomDraw` is gone.
- **Plain background:** `OCR_BUSY_SHARE` 0.25, `OCR_BUSY_MIN` 4; `ocrRun` gives each part read by Tesseract `wordsN`, `shakyN`, `busy`; `ocrResultHtml` – the yellow box `[data-ocr-busy]` with a button `[data-ocr-goto="i:j"]` for each part (`ocrClick` scrolls to it); `ocrPartHtml` – class `dci-ocr-busypart` and the line `.dci-ocr-busyline`; the hint `[data-ocr-plain]` in the steps "pick" and "frames". CSS `.dci-ocr-busy`, `.dci-ocr-busypart`, `.dci-ocr-busyline`.
- **Texts (English, OCR):** new `ocr.plainHint`, `ocr.busyTitle`, `ocr.busyHint`, `ocr.busyPart`.
- **Header / files:** `@version 3.34.14`, `?v=3.34.14`, both files' `version`.
- **Tests:** `t_coverart.py` – new cases `ocrwindow`, `ocrtextfit`; new helper `drag_img` (frames dragged in the image's pixels); `ocrframes`, `ocrpdf` check the view's proportions instead of 560 px; `ocrzoom` without the class `dci-ocr-wide`.

## Import 3.34.13 · 2026-10-28

Text from cover art (beta): the images beside the frames can be chosen (collected item 132).

- **`ocrClick`:** a small image of the frames step (`[data-ocr-cur]`) is handled before the check for `[data-ocr]` – the small images have no `data-ocr`, so from 3.34.2 the function returned before it came to them. They are buttons: Enter and Space choose them too.
- **Header / files:** `@version 3.34.13`, `?v=3.34.13`, both files' `version`.
- **Tests:** `t_coverart.py` – new case `ocrthumbs` (fails with 3.34.12).

## Import 3.34.12 · 2026-10-28

Text from cover art (beta): where a line or a word is in the image (collected item 130b).

- **Places read:** new `tessLayout(data)` – Tesseract's lines and words (`data.lines` / `data.words` of 5.x; else from `data.blocks`). `ocrRun` keeps for each part its `lines` ([{ text, box }], the text corrected like the part's text with `ocrClean`) and `unsureAt` (the words read uncertainly with their places); a place in a piece goes back to the canvas by the piece's box and `ocrPieceScale`. Each part has a `mark` (none at first).
- **PDF:** new `pdfBox(pts)` (pieces of text: from 0.9 of their size above the baseline to 0.25 below); `pdfLines` gives { text, box } a line; `ocrPdfText` gives { text, lines } a frame (or for the whole page, its lines as the PDF ends them).
- **New:** `ocrLikeness(a, b)` (the pairs of letters shared, 0 … 1), `ocrLineFor(lines, text, n)` (the line read most like it, its n-th line +0.15, at least 0.45), `ocrZoomShow(key, box)` (a zoomed view moved so the place is in sight), `ocrZoomTo(key, box)` (zoomed in on a place: half the view's width, a third of its height, at most `OCR_ZOOM_MAX`), **`ocrLocateLine(ta)`** (the caret's line marked), **`ocrLocateWord(btn)`** (a word read uncertainly: its next place selected and marked; `data-ocr-n` counts).
- **`ocrZoomDraw`:** draws the mark (a line in the frames' violet, a word in the yellow of its button); the canvas tells `data-mark`, `data-mark-kind`, `data-view` and `data-box` (places on the image's canvas).
- **Events:** `ocrClick` – a word read uncertainly goes to `ocrLocateWord`, a click into a part's text to `ocrLocateLine`; `keyup` in a part's text – `ocrLocateLine`.
- **Texts (English, OCR only):** `ocr.resultHint` and `ocr.unsure` name the marks.
- **Header / files:** `@version 3.34.12`, `?v=3.34.12`, both files' `version`.
- **Tests:** `harness.py` – the stand-in Tesseract also gives `lines`; `t_coverart.py` – new case `ocrlocate`.

## Import 3.34.11 · 2026-10-28

Text from cover art (beta): each part beside its text, with zoom (collected item 130).

- **Reading in parts:** new `ocrBoxes(img)` (the frames, else the whole canvas), `ocrPieceScale(img)`; `ocrPieces` uses them. `ocrRun` loads the canvas also for a PDF page read from its own text (it stands beside the text) and gives each result `parts` – [{ box, text, unsure, fixes, view }], a part per frame –, cleaned part by part; the result's `fixes` and `unsure` sum them up (`res.text` is gone). `ocrPdfText` returns a text per frame (one for the whole page). `ocrText` joins the parts' texts.
- **New:** `OCR_ZOOM_H` 300, `OCR_ZOOM_MAX` 8, **`ocrPartHtml(r, i, pt, j)`** (`[data-ocr-part="i:j"]`: a canvas `[data-ocr-zoom]` with + / − / ⤢ `[data-ocr-z][data-ocr-zfor]` and a hint, beside the text `[data-ocr-text="i:j"]` and its words read uncertainly), `ocrPartOf(key)`, `ocrZoomFit`, `ocrZoomClamp` (within the part when larger than the view, centred when smaller), **`ocrZoomDraw(key)`** (the width of its column, at most `OCR_ZOOM_H` high, sharp with `devicePixelRatio`; only the part, the rest dark; the text field as high), **`ocrZoomBy(key, f, at)`** (at a place of the view; between fitted and 8×), `ocrZoomAll` (also on `resize`), **`ocrZoomDrag(e)`**.
- **Window:** the class `dci-ocr-wide` in the step `result` (`min(1400px, 98vw)`); `pointerdown` – a zoomed part first, else the frames; `wheel` with Ctrl, `dblclick`; the text of a part is kept in `pt.text`; `ocrClick` – the zoom buttons.
- **CSS:** `#dci-ocr.dci-ocr-wide`, `.dci-ocr-part` (two columns, one below 760 px), `.dci-ocr-zoom`, `.dci-ocr-zoomtools`, `.dci-ocr-parttext`.
- **Texts:** new (English) `ocr.part`, `ocr.partOf`, `ocr.zoomLabel`, `ocr.zoomIn`, `ocr.zoomOut`, `ocr.zoomFit`, `ocr.zoomHint`.
- **Header / files:** `@version 3.34.11`, `?v=3.34.11`, both files' `version`.
- **Tests:** `t_coverart.py` – new case `ocrzoom`; `ocrrun` edits the part `2:0`; `ocrload` lets go of the requests it held (`unroute_all`).

## Import 3.34.10 · 2026-10-28

Text from cover art (beta): how far the images have come, and loading them ahead (collected item 128).

- **`httpFetch(url, { blob, progress, ctl })`:** `progress(loaded, total)` – GM: `onprogress`; fetch: the body read piece by piece (`content-length` as total) –, `ctl.abort()` (GM: the request's `abort`, fetch: an `AbortController`; the promise fails with `aborted`); blobs wait 180 s (was 60).
- **`ocrCanvas(img, { ahead })`** is no longer `async`: one load per image (`img.loadPromise`, shared by the frames, the reading and the loading ahead; a caller that is not ahead clears `img.ahead`), `img.ctl`, `img.load` ({ state: load | ready | error, loaded, total }), `img.loadError`; the work itself is `ocrCanvasLoad(img)` (the size kept as asked when it started); `ocrBlob` passes the progress and `ctl` (an abort is passed on, not turned into a message).
- **New:** `OCR_PRELOAD_KEY` (`dci-ocr-preload`, `S.ocrPreload`, on by default), `OCR_PRELOAD_AT_ONCE` 2, `mb(n)`, `ocrLoadText(img)` ("waiting to load", "loading …", "45 % · 2.1 / 4.7 MB", "2.1 MB", "loaded", "could not be loaded"), `ocrLoadPct`, `ocrLoadShown(img, ready)` ("loaded" only on the tiles), **`ocrLoadHtml(img, ready)`** (`[data-ocr-load]` with a bar and its text, the reason of a failure as its title), **`ocrLoadState(img, load)`** (painted in place – the window is not drawn anew for each piece), **`ocrPreloadPump()`** (the images ticked not loaded yet, two at a time; not while listing, reading or checking), **`ocrPreloadDrop(img)`** (one being loaded ahead stops), `ocrPreviewsCount()` (`[data-ocr-previews]`, the previews' `load`/`error` caught on the window), `ocrPdfStatus(text)` (`[data-ocr-pdfstatus]`: "page n of m", the MB of a PDF by its address).
- **Changed:** the tiles (`loading="lazy"` gone: the previews are counted), the small images beside the frames, the view while it loads (`.dci-ocr-viewwait` with the bar; `img.viewWait` instead of `img.loading`), the list while reading (status `load`) show `ocrLoadHtml`; `ocrChange` drops images unticked (one or "All images") and on another size stops the release's loads; `closeOcr` stops all loads; `renderOcr` counts the previews and pumps the queue; `.dci-ocr-pickhead`.
- **Settings:** ⚙ Settings → Beta – "Load the images ticked ahead" (`data-set="ocr-preload"`, shown while the beta is on; off stops the loads ahead), `TOPIC_KEYS.beta`, `resetTopic('beta')`, `resetSettings`, `SETTINGS_KEYS` + `OCR_PRELOAD_KEY`; switching the beta draws the settings anew.
- **CSS:** `.dci-ocr-load`, `.dci-ocr-loadbar` (green when loaded, none on an error), the view's wait in a column.
- **Texts:** new (English) `ocr.loadQueued`, `ocr.loadReady`, `ocr.loadFailed`, `ocr.loadPart`, `ocr.loadSome`, `ocr.loadStart`, `ocr.previews`, `ocr.pdfPages`, `ocr.pdfFetching`, `ocr.pdfFetchingOf`, `settings.ocrPreload`, `settings.ocrPreloadTitle`.
- **Header / files:** `@version 3.34.10`, `?v=3.34.10`, both files' `version`.
- **Tests:** `t_coverart.py` – new case `ocrload` (requests held and let go); `ocrpdf` waits for `[data-ocr-pdfstatus]`.

## Import 3.34.9 · 2026-10-28

Text from cover art (beta): images in their proportions, larger on mouse-over (collected item 129).

- **CSS:** `.dci-ocr-card img`, `.dci-ocr-thumb img`, `.dci-ocr-runs img` – `object-fit: contain` on a light ground (was `cover`), the tiles square as before; new `#dci-ocr-peek` (fixed, outside the window – the window's `transform` would hold a fixed child – no pointer events).
- **New:** `OCR_PEEK` 480, `ocrImageById`, **`ocrPeekSrc(img)`** (the 1200 px image of the CAA, an own file or address as it is, a PDF page drawn once at 720 px – `img.peek`), **`ocrPeekShow(thumb)`** (the small image at once, then the larger; sized to its proportions with its longer side `OCR_PEEK`, at most 44 % × 80 % of the browser's window; right of the small image, else left), `ocrPeekHide`, `ocrPeekOver` (300 ms), `ocrPeekOut`.
- **Changed:** the small images get `data-ocr-peek="<image id>"` (choice, frames, reading); `renderOcr` – `mouseover`/`mouseout`/`scroll` listeners; a larger view open is shown again at its image after the window is drawn anew; `closeOcr` hides it.
- **Header / files:** `@version 3.34.9`, `?v=3.34.9`, both files' `version`.
- **Tests:** `t_coverart.py` – new case `ocrpeek`.

## Import 3.34.8 · 2026-10-28

"… from cover art" beside "Import credits …" (collected item 124).

- **Page bar:** `insertLauncher` – a button `#dci-open-ocr` (hidden) after `#dci-open`, its click `openFromCoverArt`; `renderLauncher` shows it while `S.betaOcr` (its text and a "beta" tag, its title); CSS `#dci-open-ocr` (joined: `margin-left: -13px`, `#dci-open:has(+ #dci-open-ocr:not([hidden]))` square on the right).
- **New `openFromCoverArt()`:** `openDashboard({ ocrFirst: true })`, then `openOcr()` (or the open window to the front). `openDashboard`: `ocrFirst` – no `initOnce`, the message `ocrStart.hint` with "Start import" (`start-import`).
- **`ocrImport`:** before the import (`!S.initialized`) the text goes to `S.startText` and `initOnce()` runs; **`startImport`** loads `S.startText` as the source (TEXT, `S.textInput`) before any linked source.
- **The beta switched (⚙ Settings → Beta, its ↺, "Reset all settings"):** `renderLauncher()`.
- **Header / files:** `@version 3.34.8`, `?v=3.34.8`, both files' `version`.
- **Texts:** new (English) `launcher.ocr`, `launcher.ocrTitle`, `ocrStart.hint`.
- **Tests:** `t_coverart.py` – new case `ocrstart`.

## Import 3.34.7 · 2026-10-28

Text from cover art (beta): Discogs images on request (collected item 123).

- **Discogs adapter (`DISCOGS`):** `releaseIdInUrl(u)` (www.discogs.com/[xx/]release/<id>), **`pageImages(id)`** (the release's page through `httpFetch`; the addresses of i.discogs.com whose file – the base64 parts after the options, decoded – is "R-<id>-…", each file once at its largest `w:`/`h:`) – the Discogs knowledge stays in the adapter (`t_sources.py` adapter).
- **New in the block of the text from cover art:** **`ocrAddDiscogs(id)`** (cards `src: 'discogs'`, `discogs: id`, "Discogs r<id> · n", ticked; not twice, also not while loading – `o.discogsLoading`; `ocr.discogsNone`; log `ocrOwnAdded`), **`ocrDiscogsLinks()`** (the linked Discogs releases from `S.sourceLinks`; without an import asked of MusicBrainz once – `release/<mbid>?inc=url-rels` in the background – `o.discogsAsked`, `o.discogsLinks`).
- **Changed:** `ocrAddUrl` sends a Discogs release address to `ocrAddDiscogs`; `ocrOwnHtml` a button `[data-ocr-discogs]` per linked release (off while loading or loaded) and "Loading the images from Discogs …"; `ocrClick`; the card says "from Discogs"; `ocrText` origin "images of Discogs release https://www.discogs.com/release/<id>".
- **Header / files:** `@version 3.34.7`, `?v=3.34.7`, both files' `version` (no new permission: discogs.com is read through `@connect *`, X015).
- **Texts:** new (English) `ocr.discogsLoad`, `ocr.discogsHint`, `ocr.discogsLoading`, `ocr.discogsNone`, `ocr.discogsImage`, `ocr.ownDiscogs`; changed (English only so far) `ocr.ownHint`.
- **Tests:** `t_coverart.py` – new case `ocrdiscogs` (with `discogs_image(rel, n, size)`: addresses as Discogs writes them).

## Import 3.34.6 · 2026-10-28

Text from cover art (beta): booklets as PDF (collected item 123).

- **New constants:** `PDFJS_VERSION` 6.2.108, `PDFJS_ROOT`, `PDFJS_URL` (`legacy/build/pdf.min.mjs`), `PDFJS_WORKER_URL`, `OCR_PDF_PX` 2400, `OCR_PDF_PAGES` 60, `OCR_PDF_TEXT` 20.
- **New:** **`loadPdfJs()`** (once: an inline script in the page `import()`s the module, sets `GlobalWorkerOptions.workerSrc` – pdf.js wraps the cross-origin worker itself – and names it `window.pdfjsLib`, then the event `dci-pdfjs` on `document`; 60 s at most; `ocr.errNoPdf`), `isPdfFile`, **`ocrPdfRender(page, px)`** (a white canvas, the page drawn with `render({ canvas, viewport })`, `dciScale`), **`ocrAddPdf(blob, name, from)`** (`getDocument({ url: object URL, cMapUrl, standardFontDataUrl, wasmUrl })`, each page a card `src: 'pdf'` with `file`, `from`, `page`, `pdfPage`, `textLayer` (≥ 20 letters of its own text), a 300 px thumbnail; `o.pdfDocs`, `o.pdfLoading`; `ocr.pdfLong`, `ocr.errPdf`; log `ocrPdfAdded`), **`pdfLines(pts)`** (pieces in lines by their height, left to right, a space at a gap), **`ocrPdfText(img)`** (no frames: the text in its order, lines as the PDF ends them – `hasEOL`; frames: per frame the pieces starting inside it, in lines by their place), `ocrDirect(img)` (a PDF page with its own text, not turned).
- **Changed:** `ocrAddFiles` opens PDFs (other files still named), `ocrAddUrl` fetches an address ending in .pdf and opens it (not twice: `from`); `ocrCanvas` renders a PDF page at `OCR_PDF_PX` (`pdfScale`, `turn` 0); `ocrRotate` counts `turn`; `ocrRun` starts the text recognition only for the first image that needs it (`recognizer()`), reads a direct page with `ocrPdfText` (its canvas only when it has frames), `res.direct`; `ocrText` origin "PDF name (p. …)" by file or address; `closeOcr` destroys the PDFs and revokes their object URLs; the cards say "PDF page with its own text" / "PDF page (an image)"; the result of a direct page says so (`ocr.fromPdf`); `accept` with PDFs; "Opening the PDF …" while one opens.
- **Connections:** X016 pdf.js (kind `library`, cdn.jsdelivr.net).
- **Header / files:** `@version 3.34.6`, `?v=3.34.6`, both files' `version`.
- **Texts:** new (English) `ocr.pdfPage`, `ocr.pdfLoading`, `ocr.pdfText`, `ocr.pdfScan`, `ocr.pdfLong`, `ocr.errPdf`, `ocr.errNoPdf`, `ocr.fromPdf`, `log.ocrPdfAdded`, `conn.X016`; changed (English only so far) `ocr.chooseFiles`, `ocr.notImage`, `ocr.ownHint`.
- **Harness:** `PDFJS_DIR` (a local pdfjs-dist from npm), the jsDelivr route serves its files for `pdfjs-dist@…` (`PDFJS_REQUESTS`); **`pdf_of(pages)`** writes a small PDF (lines in Helvetica, or a page with only a drawing).
- **Tests:** `t_coverart.py` – new case `ocrpdf` (with the real pdf.js); `t_ui_settings.py` (settabs) 16 connections.

## Import 3.34.5 · 2026-10-28

Text from cover art (beta): "All images" (collected item 125), own images – files and addresses (collected item 123).

- **Header:** `@connect *` (after the known sites, which keep Tampermonkey from asking for them); `@version 3.34.5`, `?v=3.34.5`, both files' `version`.
- **Connections:** X015 (kind `site`, no name of its own – `conn.X015.name` –, hosts `['*']`, `@connect *`).
- **New in the block of the text from cover art:** `OCR_IMAGE_FILE`, `ocrIsCaa(img)` (an image of the release: `src` 'caa' or none), `ocrUrlName(u)` ("site/…/file"), **`ocrOwnImage(src, value, pasted)`** (`src` 'file': `name`, `blob`, `local` object URL as thumb/big/orig; 'url': `name`, `url`), **`ocrAddFiles(files, pasted)`** (images only, others named in `o.error` – `ocr.notImage`; log `ocrOwnAdded`; to the step `pick`), **`ocrAddUrl(text)`** (http/https, not twice), **`ocrPaste(e)`** (on `document` while the window is open: image files; an address when not typing in a field), **`ocrBlob(img)`** (an own file as it is; an address through `httpFetch`, a failure → `ocr.errUrl`).
- **Changed:** `ocrList` images get `src: 'caa'`; `ocrCanvas` keeps an own image's canvas whatever the size chosen, a blob that is no image → `ocr.errImage`; `ocrRun` always calls `ocrCanvas` (it keeps what is loaded); `ocrText` origin: "Cover Art Archive images (…)", "own image files (…)", "images from …" joined with "; " (only the release's: as before); `openOcr` keeps own images added while the list loads, a failed list is `o.listError`; `closeOcr` revokes the object URLs, removes the paste listener; `ocrTypes` the name of an own image.
- **`ocrPickHtml`:** "All images (n)" `[data-ocr-all]` (indeterminate set in `renderOcr`), cards `data-ocr-card` – own ones `.dci-ocr-owncard` with "your file" / "by its address" and `[data-ocr-remove]` –, new **`ocrOwnHtml()`** (`[data-ocr=files]` + hidden `input[type=file][data-ocr-files]` multiple `accept="image/*"`, `[data-ocr-url]` + `[data-ocr=url]`), the image size only with images of the release, no CAA images: `ocr.none` above the own images (before: only a "Close").
- **Handlers:** `ocrChange` (`ocrAll`, `ocrFiles`), `ocrClick` (`files`, `url`, `[data-ocr-remove]`), `renderOcr` (Enter in the address field, `dragover`/`drop` of files or `text/uri-list`, the class `dci-ocr-drop`, the paste listener), the head counts the release's images.
- **CSS:** `.dci-ocr-owncard`, `.dci-ocr-all`, `.dci-ocr-own`, `.dci-ocr-ownrow`, `#dci-ocr.dci-ocr-drop`.
- **Texts:** new (English) `log.ocrOwnAdded.one/.other`, `ocr.all`, `ocr.own`, `ocr.chooseFiles`, `ocr.dropHint`, `ocr.urlLabel`, `ocr.addUrl`, `ocr.ownHint`, `ocr.ownFile`, `ocr.ownUrl`, `ocr.remove`, `ocr.removeImage`, `ocr.pastedImage`, `ocr.notImage`, `ocr.badUrl`, `ocr.urlTwice`, `ocr.errUrl`, `conn.X015.name`, `conn.X015`.
- **Tests:** `t_coverart.py` – new case `ocrown`; `t_ui_settings.py` (settabs) 15 connections.

## Import 3.34.4 · 2026-10-28

✎ at the wording rules and the questions (collected item 121).

- **Section 2· (your changes):** new `WORDING_RULE_FIELDS` (phrases, credit), `QUESTION_RULE_FIELDS` (base, credit, options), `TYPE_QUESTION_FIELDS` (options), `OPTION_FIELDS` (type, level, instrument, task, label, credit, suggested – the order a changed choice is written in), `LIMITS.phrases` 40; `rawWordingRule`, `rawQuestionRule`, `rawTypeQuestion`, `rawDataRule`, **`ruleKindOf(id, raw)`** (role | company | wording | question | typeq | ''), `RULE_FIELDS` by kind. `builtinField` reads those rules too; `effectiveRaw` sets their changed fields (a copy); `applyMappingChanges` refills `WORDING_RULES`, `QUESTION_RULES`, `TYPE_QUESTIONS` rule by rule in place.
- **Rules window:** `ruleEditable` (+ W and Q), `ruleFieldsOf` by kind, `encJson` compares with the keys of objects in order (`sortedKeys`: a choice saved by ✎ equals the file's whatever the order of its keys); new **`checkDataField(kind, f, v)`** (phrases in lower case, 1 – 40; a role credit, empty = none; the word of a question; its instruments 1 – 8; the choices of a type question 1 – 8, each type + level, instrument/task/label, credit true or a text, suggested), used by `checkRuleSet` for those kinds; `fieldText` (phrases " | ", choices with `optionText`), `fieldChangeHtml` (words added and taken away also for phrases and the instruments of a question), `ruleConflicts` ('gone' by `ruleKindOf`).
- **Form:** `choiceDraft`, `dataRuleDraft(kind, v)`, `dataRuleSet(kind, d)`, `isDataKind`; `openRuleEdit` and `saveRuleEdit` branch (the old body is `patternRuleSet(id, d)`); new **`dataRuleEditHtml(id, kind)`** (W: textarea `phrases`, `creditMode` none/text + `credit`; Q: `base`, `credit`, textarea `options`; type question: a table of choices `[data-redit-o][data-redit-of]` with ↑ ↓ ✕ `[data-redit-omove][data-dir]`, `[data-redit-odel]`, `＋ [data-redit-oadd]`), `ruleEditActions(id)` shared. Handlers: `change` and `input` of `data-redit-of`, clicks of omove/odel/oadd; ✎ focuses the pattern, else the first field.
- **`rulesTables`:** wording and question rows with `editRow` (✎ cell; one more column).
- **`mappingChanged`:** a row's answer to a type question (the index of a choice) is kept by its choice (type, level, instrument) across the change, removed when that choice is gone.
- **Import (`readMappingImport`):** unknown ids by `ruleKindOf`; a whole register compares `WORDING_RULES`, `QUESTION_RULES`, `TYPE_QUESTIONS` field by field (other fields such as notes are not taken over); those keys no longer count as lists that cannot be changed. The changes format stays version 2 (an older script skips W/Q ids as unknown).
- **CSS:** textarea in a label, `.dci-redit-choices` (table, fields), `.dci-redit-omove`.
- **Texts:** new (English) `mapping.field.phrases`, `.base`, `.options`, `mapping.phrasesHint`, `mapping.optionsHint`, `mapping.choicesHint`, `mapping.choice.type/.level/.instrument/.task/.label/.credit/.suggested`, `mapping.choiceUp`, `.choiceDown`, `.choiceDel`, `.choiceAdd`; changed in all four languages `mapping.badField` (names the words and choices of W and Q).
- **Header / files:** `@version 3.34.4`, `?v=3.34.4`, both files' `version`.
- **Tests:** `t_rules_window.py` – new case `wqedit`.

## Import 3.34.3 · 2026-10-28

Settings: scrolling with ⓘ Connections (collected item 122), the bridge from ⚙ in line (126), the content as high as it can be (127), words in the languages file (119, 120).

- **`alignSettingsPane()`** works the margin of `.dci-set-pane` out without taking it away first (the tab's place does not depend on it) and writes it only when it changes; it is now the smallest margin with which the chosen tab still lies within the pane's side, with the pane's lower corner radius + 2px below it – `max(0, min(tabTop, tabBottom + below − paneHeight))` – instead of the tab's top; the class `dci-set-joined-top` when the tab joins at the top (only with the tabs in a column). Until 3.34.2 `pane.style.marginTop = ''` and the new value on every call – every scroll event, through `placeBridges` – made the browser's scroll anchoring scroll back by the margin (278px at ⓘ Connections, reproduced with "Dates & tracks" open).
- **`placeBridges()`:** `--dci-bridge-x`, `-w`, `-h` and `--dci-bridge-down` in fractions of a pixel (`px()`, three decimals; until 3.34.2 `Math.round`), x from the box's computed `border-left-width` instead of `clientLeft` (rounded), `--dci-bridge-down` = head bottom − button bottom + 3 (the `::after` starts 2px above the button's lower edge – `top: 100% − 1px` of its padding box – and ends 1px below the head, over its `border-bottom`; before + 1, rounded, it ended 1px short). New **`setVar(el, name, value)`**: a custom property only set when it changes.
- **`buildOverlay`:** a `ResizeObserver` on `[data-el="settings"]` calls `bridgesLater` (the content's place follows its height).
- **CSS:** `.dci-set-pane` `border-radius: 4px` (was `0 4px 4px 4px`), `.dci-set-pane.dci-set-joined-top { border-top-left-radius: 0 }`.
- **Languages file:** de/es/fr `rules.quick` "Quick switches"; `ms.3.32.0`, `ms.3.33.0` the same word; es `quick.S045`, `ms.3.31.0`, `ms.3.32.0` "entidad de gestión colectiva" ("una lista de las entidades"); fr `quick.S045`, `ms.3.31.0`, `ms.3.32.0` "société de gestion des droits d’auteur" (13 texts).
- **Header / files:** `@version 3.34.3`, `?v=3.34.3`, both files' `version`.
- **Tests:** `t_ui_settings.py` – `bridge` (A, C exact to 0.01px, the part at the symbol 1px below the head; B the new place of the content: Connections from the top with its tab in the middle, General joined at the top, a short one just low enough, the corner), new case `settingsscroll` (Connections and "Dates & tracks" open, scrolled up in 15px steps: never back down, up to 0; no change of the content's style while scrolling).

## Import 3.34.2 · 2026-10-28

Text from cover art (beta): frames around the credits (collected item E3).

- **New in the block of the text from cover art:** `ocrChosen()`, `ocrToRead()` (without those left out), `OCR_VIEW` (560 × 620), `ocrCurrent()` (the image shown and the scale of its view), **`ocrDraw()`** (the view: the image, outside the frames darkened – `fill('evenodd')` –, each frame dashed with its corners and "n · w × h px" in the image's pixels), **`ocrPointerDown(e)`** (pointer events: a corner → its size, inside → moved, else a new frame; under 8 px of the view nothing; `pointermove`/`pointerup` on the window), `ocrRotate(img, dir)` (a canvas turned by 90°, the frames go), **`ocrFramesHtml()`** (the view `[data-ocr-view]`, the images `[data-ocr-cur]` with their state, what is read `[data-ocr-mode]` frames | whole | skip, Remove the frames, ↺ ↻, Next image →, Recognize text).
- **State:** `S.ocr.frameFirst` (true), `cur`, `drag`; an image's `mode`, `frames` (on its canvas), `loading`.
- **Changed:** `ocrPickHtml` (the box "Before reading" `[data-ocr-framefirst]`, the button `data-ocr="frames"` "Next: frames for n images →" while ticked; images left out read again once ticked here), `renderOcr` (the step `frames`: the image loaded first, then `ocrDraw`; `pointerdown` on the window; the head names image i of n), `ocrClick` (frames, next, an image, clear, rotl/rotr), `ocrChange` (`data-ocr-framefirst`, `data-ocr-mode`; another image size: the canvases and frames go), `ocrRun` (`ocrToRead()`).
- **Header / files:** `@version 3.34.2`, `?v=3.34.2`, both files' `version`.
- **CSS:** `.dci-ocr-frames`, `-stage`, `-view` (crosshair, `touch-action: none`), `-viewwait`, `-side`, `-thumbs`, `-thumb`, `-tools`, `.dci-small:disabled`.
- **Texts:** new (English) `ocr.before`, `ocr.frameFirst`, `ocr.frameFirstHint`, `ocr.toFrames.one/.other`, `ocr.step.frames`, `ocr.loadingImage`, `ocr.viewLabel`, `ocr.mode`, `ocr.modeFrames`, `ocr.modeWhole`, `ocr.modeSkip`, `ocr.clear`, `ocr.rotl`, `ocr.rotr`, `ocr.framesHint`, `ocr.nFrames.one/.other`, `ocr.noFrame`, `ocr.wholeImage`, `ocr.leftOut`, `ocr.nextImage`.
- **Tests:** `t_coverart.py` – new case `ocrframes` (two frames drawn, one changed at a corner, one moved; turned and read whole; left out; the sizes read; back to the images); `ocrrun`, `ocrerror` untick the frames (the whole images); `ocrpick` expects "Next: frames for n images →".

## Import 3.34.1 · 2026-10-28

Text from cover art as a beta (collected item E3).

- **New block "Text from cover art (beta)"** (before `buildLogWindow`): `BETA_OCR_KEY` (`dci-beta-ocr`), `S.betaOcr`, `S.ocr` (the window's state: `step` list | pick | run | result, `images` [{ id, types, comment, thumb, big, orig, sel, mode, frames, canvas, w, h }], `langs`, `size` orig | 1200, `results`, `error`, `run`), `CAA_URL`, `TESSERACT_VERSION` 5.1.1, `TESSERACT_URL` (jsDelivr), `OCR_CREDIT_TYPES` (Back, Booklet, Liner, Tray: ticked), `OCR_LANGS` (en eng, de deu, es spa, fr fra), `OCR_SMALL` 1000 (×3 below), `OCR_MAX` 3000, `OCR_UNSURE` 60; **`httpFetch(url, { blob })`** (`GM_xmlhttpRequest` / `GM.xmlHttpRequest` with `responseType`, else fetch → { status, body }), **`loadTesseract()`** (once: a script element into the page, `pageWindow.Tesseract`), **`ocrList()`** (`/release/<mbid>` of the Cover Art Archive, http → https, 404: none), **`ocrCanvas(img)`** (the image as a canvas, `createImageBitmap` else an `Image`, at most `OCR_MAX`), **`ocrPieces(img)`** (frames or the whole image, ×3 when small), **`ocrClean(text)`** (℗, dashes, empty lines → { text, fixes }), `ocrTypes`, `openOcr()`, `closeOcr()`, **`ocrRun()`** (one worker for the languages, `recognize` per piece, words under `OCR_UNSURE`, `terminate`; errors into the window and the log), `ocrText()` (the texts and their origin "Cover Art Archive images (…), read with text recognition"), `ocrImport(supp)` (`loadRelease(…, { source: TEXT })` or `loadSupplement(TEXT, …)`), `renderOcrProgress()`, `ocrPickHtml()`, `ocrRunHtml()`, `ocrResultHtml()`, **`renderOcr()`** (`#dci-ocr`, a window above the dashboard), `ocrClick`, `ocrChange`.
- **"Source ▾":** the item `ocr-open` (with `.dci-beta-tag`) while the beta is on; the click opens the window. **Escape** closes it first.
- **⚙ Settings:** `SETTING_TOPICS` + `beta` (before connections), `TOPIC_KEYS.beta`, the body (`settings.betaHint`, the switch `data-set="beta-ocr"`, `settings.betaOcrWhat`), `settingsChange` (stored, the menu drawn anew, the window closed when off), `resetTopic('beta')`, `resetSettings` (`betaOcr: false`, the window closed), `SETTINGS_KEYS` + `BETA_OCR_KEY`.
- **Header:** `@connect coverartarchive.org`, `@connect archive.org`; `@version 3.34.1`, the `?v=` of both files, their `version` 3.34.1.
- **Connections:** X013 Cover Art Archive (site), X014 Tesseract.js (kind `library`, new text `conn.kind.library`).
- **CSS:** `.dci-beta-tag`, `#dci-ocr` and its parts (`.dci-ocr-head`, `-body`, `-grid`, `-card`, `-type`, `-opts`, `-foot`, `-err`, `-warn`, `-runs`, `-barbox`, `-bar`, `-res`, `-word`, its buttons and fields).
- **Texts:** new (English) `settings.t.beta`, `settings.betaHint`, `settings.betaOcr`, `settings.betaOcrTitle`, `settings.betaOcrWhat`, `ocr.*` (menu, menuTitle, title, step.list, step.pick.one/.other, step.run, step.result, caaLink, loading, none, listFailed, pickHint, rarely, noType, langs, langsHint, size, sizeOrig, size1200, sizeHint, chosen, run.one/.other, runHint, state.wait/.load/.read/.done, resultHint, small, textOf, unsure, fixed, fixPc, fixDash, back, copy, copied, supp, import, errNoLib, errImage), `log.ocrOpen`, `log.ocrDone.one/.other`, `log.ocrFailed`, `log.ocrImported`, `conn.kind.library`, `conn.X013`, `conn.X014`.
- **Harness:** `COVER_ART` (the release's images: id, types, comment, size), `CAA_REQUESTS`, route `coverartarchive.org` (the list, 404 without images; PNGs of the size, `png_of(w, h)`), `TESSERACT_FAKE` / `FAKE_TESSERACT` (a stand-in of Tesseract.js served as from jsDelivr: `window.__ocrTexts` per piece, `window.__ocr` records languages, sizes read, workers), `TESSERACT_REQUESTS`; `GM_XHR_SHIM` answers `responseType: 'blob'`.
- **Tests:** new file `t_coverart.py` – cases `ocrsetting`, `ocrpick`, `ocrrun`, `ocrerror`; `t_ui_settings.py`: the tab `beta`, 14 connections.

## Import 3.34.0 · 2026-10-28 – milestone "Languages file"

German, Spanish and French in `mb-vibecode-credits-importer-languages.json` (collected item E6, Block X), and the translation round.

- **New file `mb-vibecode-credits-importer-languages.json`** (format 1, `version`, `about`, `de`, `es`, `fr`: {key: text}, one text a line – the layout of `tools/i18n_add.py`'s `write_languages`). The blocks `de`, `es`, `fr` of `const I18N` moved there unchanged (1,452 texts each); the script keeps `en` (1.75 MB → 1.37 MB).
- **Section 1c (new, after `I18N`):** `LANGUAGES_FILE`, `LANGUAGES_FORMAT`, `LANGUAGES_URL`, `LANGUAGES_STORE_KEY` (`dci-languages:<version>`), `OTHER_LANGS`, `SCRIPT_DOWNLOAD_URL` (moved here from section 2), `languagesOk(raw)`; shared with the mapping file: **`scriptFileNow(resource, file, storeKey, ok)`** (Node: the file next to the script; `GM_getResourceText`; the kept copy), **`fetchScriptFile(resource, url, storeKey, ok)`** (`GM.getResourceUrl`, else `GM_xmlhttpRequest` / `GM.xmlHttpRequest` / fetch of `url?v=`; kept), **`reloadForFile(reloadKey)`** (once per version and tab), **`fileMissingMessage(id, head, text, button, url)`** (now with ✕; waits for the body). `const LANGUAGES = scriptFileNow('languages', …)`; `I18N.de/.es/.fr` from it (or `{}`: English); missing: fetched – English chosen: its texts at once, else the page once more (`dci-languages-reload`) –, failing that `#dci-languages-missing` (English texts).
- **Section 2·:** `mappingNow`, `mappingMissing`, `mappingMissingMessage` now through these helpers (same behaviour, same ids).
- **Header:** `@version 3.34.0`, `@resource languages https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-vibecode-credits-importer-languages.json?v=3.34.0`, `@resource mapping …?v=3.34.0`; the mapping file's `version` 3.34.0.
- **Start (`init`):** log `languagesLoaded` (info), `languagesVersion` (warn), `languagesMissing` (warn, only with another language than English).
- **Connections:** X010 `perms` + `@resource languages`, its text in all four languages.
- **Milestone** 3.34.0 (`MILESTONES`, `ms.3.34.0`); the notice names 3.34.0, 3.33.0, 3.32.0.
- **Texts:** new `languages.missing`, `languages.missingText`, `log.languagesLoaded`, `log.languagesVersion`, `log.languagesMissing`, `ms.3.34.0`; **translation round:** the 238 texts English only until now in German, Spanish and French (texts of 3.27.1 – 3.33.1; prepared per language against the existing translations as glossary, checked: same placeholders, French no-break spaces).
- **Tools:** `i18n_add.py` (English into the script, the others into the file: `en_block`, `read_languages`, `write_languages`, `insert_after`), `i18n_del.py` (both).
- **Harness:** `LANGUAGES_TEXT`, `LANGUAGES_SHIM_OFF`; `add_mapping(ctx)` gives `GM_getResourceText` both files.
- **Tests:** new cases `languagesfile` (`t_static.py`: the file, its layout, only English in the script, the header, Node) and `languagesload` (`t_start.py`: from the manager, fetched with one reload, English chosen – fetched quietly, German at once –, missing – message, English, log); `t_static.py` i18n reads English from the script and the rest from the file (it reports nothing missing now); `t_ui_settings.py` notice: 3.34.0, 3.33.0, 3.32.0.

## Import 3.33.1 · 2026-10-27

✎ at built-in rules, your changes of the register, export and import (collected item E7, Block W part 2).

- **Section 2, new block "2·. Your changes of the register: three layers"** (after `const MAP`): `MAPPING_CHANGES_KEY` (`dci-mapping-changes` in localStorage: `{ rules: { id: { set, was } }, lists: { T…: { add, remove } }, base }` – values as in the file; `was` the built-in value of each field when it was changed), `CHANGES_FORMAT` (`mb-vibecode-credits-importer-mapping-changes`), `CHANGES_VERSION` 2, `CHANGES_FILE`, `RULE_LEVELS`, `ROLE_RULE_FIELDS` (re, types, level, credit, primaryCands), `COMPANY_RULE_FIELDS` (re, label, place, area, artist, level), **`EDITABLE_LISTS`** (T001 `INSTRUMENT_ALIASES` map, T002 `GENERIC_WORDS` set, T003 `ART_TYPES`, T038 `TITLE_SMALL_WORDS` set, T045 `RIGHTS_SOCIETIES` pairs – `reload`: `SOCIETY_ALT` is built at the start –, T048 `ROLE_WORDS`), `LIMITS`, `readMappingChanges()`, `let mappingChanges`, `saveMappingChanges()` (removes the key when empty), `rawRoleRule`, `rawCompanyRule`, `builtinField(id, field)`, `listKey`, `rawListItems(raw, tid)`, **`effectiveRaw(changes)`** (a copy of `MAPPING.raw` with the changes; `work` follows `level`), **`applyMappingChanges()`** (the effective register into `MAP` in place – rule objects field by field, `COMPANY_ROLES` pairs, lists; the code holds `MAP`'s objects), run at the start only when there are changes.
- **`roleRules`:** each rule gets `hasCode` (code in `code`, or kind special) – only those without get ✎.
- **Rules window, new block "✎ built-in data rules, your changes, export and import":** `RULE_PROBE`, `isRoleRuleId`, `ruleEditable`, `encJson`, `fieldWith(changes, id, field)`, `ruleFieldsOf`, `escRe`, `wordsSource(words)`, `showItem`, `patternForm(v)` (role words where the pattern round-trips, else the expression), `checkPattern(v)` (not empty, ≤ 400, flags `imsu`, compiled in try/catch), `checkRuleSet(id, set)`, **`putRuleChange(changes, id, set, wasOld)`**, **`putListChange(changes, tid, items)`**, `listWith(changes, tid)`, `checkListChange`, `listLines`, `listFromLines(tid, text)`, `fieldText`, `fieldChangeHtml` (+ / − words of a pattern), `ruleFieldsText`, **`ruleConflicts(id)`** (`['gone']` for a rule no longer in the file), **`mappingChanged(what)`** (store, `applyMappingChanges`, `roleVocabCache`/`ruleNotesCache` emptied, `applyRulesChange`), `mappedWith(changes, fn)` (the preview's after), `S.ruleEdit`, `S.listEdit`, `openRuleEdit`, `switchPatternMode`, `saveRuleEdit`, `ruleEditHtml`, `openListEdit`, `saveListEdit`, `listEditHtml`, `editToolsHtml(id, { list, code })`, **`changesHtml()`**, `resetMappingChange(id)` (asks), `keepMappingChange(id)`, `S.mioWhat`, `S.mImport`, `S.mPaste`, `S.mPasteOpen`, `S.mioStatus`, **`registerFileText(raw)`** (the layout of the mapping file, as `extract.js` writes it), `mappingExportText(what)`, `exportWhatText`, `saveMappingExport()`, `copyMappingExport()` (`navigator.clipboard`), **`readMappingImport(text)`** (v1 `mb-x-vibecode-rules`, changes v ≤ 2, a whole register → what differs; skipped with reasons; own rules only with their fields), **`planImport(imp, mode)`** (merge / replace; a whole register leaves own rules and switches), **`importPreviewHtml()`**, `startMappingImport(text, name)`, `importRules(file)` (new: the preview), `applyMappingImport()`, `mappingIoHtml()`, `renderMappingIo()`. **Removed:** `exportRules()`, the old `importRules(file)`, the line `.dci-urule-io` in `ownRulesHtml`.
- **`rulesTables`:** `editRow` (a cell with ✎ / "code" / "changed", the form in a row below, `tr.dci-rchanged`), `sect(…, tid)` with ✎ and the form for T001, T002 (sections) and `data-ledit-anchor`; the lists T003, T038, T045, T048 the same in their heads; the role and company tables one column more.
- **Window:** `[data-rf=changes]`, `[data-rf=io]` below `[data-rf=own]`; `renderRulesBody` fills them and the line of the file (`mappingSourceText()`, with "your changes: n"); the search leaves `tr.dci-redit-row` alone; click handlers for `data-redit-open`, `-save`, `-cancel`, `data-ledit-*`, `data-mchg-reset`, `-keep`, `-resetall` (asks), `-goto`, `data-mio-save`, `-copy`, `-read`, `data-mimport-apply`, `-cancel`; change for `data-redit-f` (pmode and creditMode redraw), `data-mio=what`, `data-mimport-mode`; input for the form, the list and the pasted text; **dragover/drop** of a file onto the window (`dci-rules-drop`). `focusRule` also finds `[data-ledit-anchor]`.
- **Start (`init`):** log `mappingChangesOn` (info) and `mappingConflicts` (warn).
- **Reset (`resetSettings` with rules):** your changes too; `reset.rules` gets `{c}`.
- **CSS:** `.dci-redit-*`, `.dci-changed`, `.dci-conflict`, `.dci-codetag`, `tr.dci-rchanged`, `.dci-redit`, `.dci-redit-err`, `#dci-rules textarea`, `.dci-mchg*`, `.dci-mio-*`, `.dci-mprev*`, `#dci-rules.dci-rules-drop`.
- **Header / file:** `@version 3.33.1`, `@resource … ?v=3.33.1`; the mapping file's `version` 3.33.1 (no other change).
- **Texts:** new (English) `mapping.changesN.one/.other`, `mapping.badPattern`, `mapping.empty`, `mapping.tooLong`, `mapping.badValue`, `mapping.badField`, `mapping.tooMany`, `mapping.badLine`, `mapping.credit.none/.role/.text`, `mapping.field.re/.types/.level/.credit/.primaryCands/.label/.place/.area/.artist`, `mapping.editTitle`, `mapping.editRuleTitle`, `mapping.editListTitle`, `mapping.editList`, `mapping.patternMode`, `mapping.pmode.words/.re`, `mapping.builtinIs`, `mapping.namesHint`, `mapping.toBuiltin`, `mapping.linesWords/.linesPairs/.linesMap`, `mapping.reloadHint`, `mapping.codeTag`, `mapping.codeOnly`, `mapping.changedTag`, `mapping.changedTitle`, `mapping.conflictTag`, `mapping.changes`, `mapping.changesEmpty`, `mapping.changesHint`, `mapping.gone`, `mapping.conflict`, `mapping.keepMine`, `mapping.discard`, `mapping.resetAll`, `mapping.resetAsk`, `mapping.resetAllAsk`, `mapping.resetAllWhat`, `mapping.io`, `mapping.export`, `mapping.exportChanges`, `mapping.exportRegister`, `mapping.exportChangesHint`, `mapping.exportRegisterHint`, `mapping.saveFile`, `mapping.copy`, `mapping.saved`, `mapping.copied`, `mapping.copyFailed`, `mapping.clipboard`, `mapping.importFile`, `mapping.importHint`, `mapping.paste`, `mapping.read`, `mapping.pasted`, `mapping.notJson`, `mapping.newerFile`, `mapping.tooBig`, `mapping.skipUnknown`, `mapping.skipCode`, `mapping.skipList`, `mapping.preview`, `mapping.kind.v1/.changes/.register`, `mapping.merge`, `mapping.replace`, `mapping.replaceData`, `mapping.prev.new/.changed/.removed/.on/.off/.skipped`, `mapping.prevConflict`, `mapping.prevNothing`, `mapping.apply`, `mapping.imported.one/.other`, `mapping.importWhat`, `log.mappingExported`, `log.mappingImported.one/.other`, `log.mappingChangesOn.one/.other`, `log.mappingConflicts`; **changed in all four languages:** `rules.lists` (no "read only"), `rules.listsHint` (names the lists ✎ changes), `reset.rules` (`{c}`); **removed:** `rules.export`, `rules.import`, `rules.ioHint`, `rules.imported`, `log.rulesExported`.
- **Tests:** new cases `ruleedit`, `mappingio`, `mappingconflict` (`t_rules_window.py`); `t_register.py` hides ✎, "code" and the forms before reading the sections (the register only), golden file rewritten for the sections `own` (without the old export line), `lists` (the new heading and hint) and the new `changes`, `io` – roles, companies, dates, dashboard unchanged. Harness: `VERSION` (the script's `@version`); `t_start.py` mappingload and the new cases name the version through it (before: 3.33.0 written in).

## Import 3.33.0 · 2026-10-27 – milestone "Mapping file"

The data of the mapping register in `mb-vibecode-credits-importer-mapping.json` (collected item E7, Block W part 1).

- **New file `mb-vibecode-credits-importer-mapping.json`** (format 1, `version`, `about`): 81 lists, in the order of the script – every `const` of section 2 whose value is pure data (no function, no other constant; except the storage keys, `SPECIAL_RULES` and `DATE_RULES` – notes of rules with code –, `DAYP` and `COPYRIGHT_SIGN` – parts of the date code), plus `ROLE_RULE_DATA` (with `DESIGN_TYPES` written out) and `QUICK_SWITCHES`. Encoded: `{"$re", "$flags"}`, `{"$set"}`, `{"$map"}`. Made with a small Node tool (acorn) from 3.32.10; from now on the file is where these lists are changed.
- **Section 2:** each of them `const X = MAP.X;` (their comments stay). **New before them:** `MAPPING_FILE`, `MAPPING_FORMAT`, `MAPPING_URL` (GitHub main), `MAPPING_STORE_KEY` (`dci-mapping:<version>` in localStorage), `SCRIPT_DOWNLOAD_URL`, `mappingOk(raw)`, **`mappingNow()`** (Node: the file next to the script; `GM_getResourceText('mapping')`; the kept copy → `{ raw, from }`), **`mappingRevive(v)`**, **`mappingMissing()`** (`GM.getResourceUrl` → fetch; else `GM_xmlhttpRequest` / `GM.xmlHttpRequest` / fetch of `MAPPING_URL?v=`; kept, the page loaded again – once per version and tab, `dci-mapping-reload` in sessionStorage), **`mappingMissingMessage(why)`** (`#dci-mapping-missing`, "Update script" opens `SCRIPT_DOWNLOAD_URL`); `const MAPPING = mappingNow()` – without it the script stops there (Node: an error); `const MAP = mappingRevive(MAPPING.raw)`.
- **Header:** `@grant GM_getResourceText`, `@grant GM.getResourceUrl`, `@connect raw.githubusercontent.com`, `@resource mapping https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-vibecode-credits-importer-mapping.json?v=3.33.0` (the `?v=` makes the manager load it again with each version); `/* global */` with `GM_getResourceText` (`GM` is known to the lint config; the `no-undef` directives at the new lines are not needed).
- **Rules window:** `[data-rf=mapping-src]` (where the data comes from); **log** `mappingLoaded`, `mappingVersion` (warn) at the start.
- **Connections:** X010 perms and text (all four languages: the mapping file).
- **Milestone** 3.33.0 (`MILESTONES`, `ms.3.33.0`).
- **Texts:** new `mapping.missing`, `mapping.missingText`, `mapping.update`, `mapping.source`, `mapping.from.manager`, `mapping.from.fetched`, `mapping.from.file`, `log.mappingLoaded`, `log.mappingVersion`, `ms.3.33.0` (English only); `conn.X010` changed in all four languages.
- **Harness:** `MAPPING_TEXT`, `MAPPING_SHIM_OFF`, **`add_mapping(ctx)`** (`GM_getResourceText` unless off; `new_context` calls it, so do the contexts made by hand: another browser language in `t_ui_head.py` case head, `shot_colors.py`), `RAW_GITHUB`, `RAW_REQUESTS` (route raw.githubusercontent.com).
- **Tests:** new cases `mappingfile` (`t_static.py`: the file, its lists against the script, the header, Node) and `mappingload` (`t_start.py`: from the manager, fetched from GitHub with one reload, missing with the message); `notice` expects 3.33.0, 3.32.0, 3.31.0. The register and text golden tests are unchanged.

## Import 3.32.10 · 2026-10-27

Comments of live recordings: entered after "Enter edit" (collected item 113, part 2).

- **New (section 3b, before the pages are told apart – also on the release page): `LIVE_JOB_PREFIX` (`dci-live-job:<MBID>` in localStorage), `LIVE_JOB_MAX_MS` (30 min), `SEED_NOTE_TEXT`, `liveAscii`, `liveLog(mbid, level, key, params, logFn)`** (the dashboard's `log`, else an entry in `dci-log:<MBID>` of the tab), **`liveAreaOfMb(area)`, `liveAreaFormatMb(chain)`** (MusicBrainz's own area data: `typeID`, `containment`, `primary_code`, `country_code`), **`liveCommentFromMb(rels)`** (as the seed script: 693 place – credit or name, area; else 698 area; dates of 698, 693, 278; conflicts), **`liveNotice(lines)`** (`#dci-livecom-notice`), **`runLiveJob(mbid, { tries, logFn })`** (an armed job, at most 30 min old: `/ws/js/release/<MBID>?inc=rels recordings` until every recording has its place; `running` against a second page; live per MB – 278 with attribute 578, else the release group's secondary type 6; the comment from MB unless changed by hand; a changed credit of the place → `liveCreditChanged` (error, once per place), a hand-made comment takes the new credit; MB's comment: the same → nothing, "live" or empty → set, another → `liveOther` (error); POST `/ws/js/edit/create` `{ edits: [{ edit_type: 72, to_edit, comment }], editNote, makeVotable: false }`; `done`), **`initLiveJobArm(mbid, logFn)`** (capture listeners `submit` and `click` on the form with the edit note → `armedAt`, `runLiveJob` with 30 tries).
- **Dashboard:** `SEED_NOTE` = `SEED_NOTE_TEXT`; new **`saveLiveJob({ quiet })`** (the ticked comments with recording, position, `manual`, the place `{ mbid, credit, name }`; the note `editNoteBlock()` when the edit note is written, and the seed line), called after staging and from `livecom-on` / `livecom-text` while a job waits (not once armed); `initLiveJobArm` after the log is read. **`initReleasePageHook`:** `runLiveJob(mbid, { tries: 5 })`.
- **Connections:** new X011 (murdos, "Set recording comments for a release"), X012 (ROpdebee, the seed script).
- **Texts:** new `log.liveSaved`, `log.liveArmed`, `log.liveNotLive`, `log.liveConflict`, `log.liveCreditChanged`, `log.liveOther`, `log.liveSet`, `log.liveFailed`, `log.liveNone`, `livecom.noticeTitle`, `conn.X011`, `conn.X012` (English only).
- **Tests:** new case `livecomrun` in `t_works_more.py` (the job at staging, "Enter edit" on the editor's page with the relationships saved and a changed credit, the POST, the red log, the box; the release page with a hand-made comment and another comment of MB).

## Import 3.32.9 · 2026-10-27

Comments of live recordings: the proposals (collected item 113, part 1).

- **New `LIVE_COM_KEY` (`dci-live-comments`), `SEED_NOTE`, `S.liveCom`** (setting, off; in `TOPIC_KEYS.staging`, `SETTINGS_KEYS`, reset of the tab and of all settings), `S.liveComChoice` (recording gid → `{ on, text }`), `S.liveComOpen`, `S.liveAreas`.
- **New `liveDateText(v)`** (as the seed script: U+2010, "begin–end"), **`liveAreaFormat(chain)`** (city/municipality, the outermost subdivision as its code for US/CA, country "USA"/"UK"/name), **`liveAreaText(kind, mbid)`** (in the background: `place/<mbid>`, then `area/<id>?inc=area-rels` up to the country, cached; draws the list again), **`liveProposals()`** (live: "live" on a link to a work – `linkAttrsOf`, MB's `linkAttrs` – else the release group's secondary type Live; the rows "recorded at" (place) or "recorded in" (area) of the track – credit or name, area, the dates of the rows; conflicts, MB's comment via `recordingComment`), **`liveChoice(p)`**, **`renderLiveComments()`** (in `refresh`; `[data-el=livecom]` above the footer actions, `<details class="dci-livecom-box">`; not while a comment is typed in).
- **`init`:** `S.mbTracks[].recordingComment` (MB's disambiguation; also when tracks are read from the relationship editor's data, `completeMedia`).
- **Handlers:** `onChange` `livecom-on`, `livecom-text`; the toggle listener remembers the folding; `settingsChange` `live-comments`.
- **Fixed:** `SETTINGS_KEYS` lacked `KIND_COLORS_KEY`, `KIND_PALETTE_KEY` (3.32.4) – "Reset all settings" now forgets them.
- **CSS:** `.dci-livecom`, `.dci-livecom-box`, `.dci-livecom-table`, `.dci-livecom-pos`, `.dci-livecom-warn`.
- **Texts:** new `settings.liveComments`, `settings.liveCommentsTitle`, `livecom.title`, `livecom.hint`, `livecom.onAria`, `livecom.textAria`, `livecom.unassigned`, `livecom.places`, `livecom.dates`, `livecom.existing`, `livecom.same`, `livecom.pending`, `livecom.manual` (English only).
- **Harness:** `PLACE_AREAS`, `AREA_INFO` (routes `/ws/2/place/<gid>` and a richer `/ws/2/area/<gid>`), `WS_JS_RELEASE`, `EDITS_POSTED` (routes `/ws/js/release/<REL>` and POST `/ws/js/edit/create`, used from 3.32.10).
- **Tests:** new case `livecom` in `t_works_more.py`.

## Import 3.32.8 · 2026-10-27

The quick switches as buttons in a box; "To the date matrix" (collected items 116, 109b).

- **`quickSwitchesHtml`:** `.dci-quick` with a head `.dci-quick-h` (title, `rules.quickHint`) and a grid `.dci-quick-grid`; each switch `.dci-qbtn-wrap` = a button `.dci-qbtn` (`data-qs-toggle`, `aria-pressed`, `.dci-qled` slider, `.dci-qlabel`, `.dci-qstate` – "on"/"off" for screen readers) and the id `.dci-qid` (`data-qs-goto`, as before). No checkboxes `data-rule-on` at the top any more (the lists keep theirs).
- **Rules window click handler:** `[data-qs-toggle]` → `setRuleOn(id, !ruleOn(id))`, `applyRulesChange(id)` (which redraws the quick switches), the focus back on the button.
- **CSS:** `#dci-rules .dci-quick` and its parts anew (frame #b9b5cf, corners 4 px, a light shadow; on: #5b55a0).
- **`autoPlaceFoundDates`:** the message `dm.autoPlaced` with the action `dm-goto` (`dm.goto`). **New handler `dm-goto`:** opens the dashboard if needed, `S.poolsForce` (when "Dates & tracks" is folded), `renderDates`, the matrix (`[data-el=dm]`) scrolled into view with `.dci-flash` for 2.5 s.
- **Texts:** new `rules.quickHint`, `dm.goto` (English only).
- **Tests:** `t_rules_window.py` case `quickswitch` reads the buttons (`aria-pressed`) and the box, switches by click; new case `dmgoto` in `t_dates_matrix.py`.

## Import 3.32.7 · 2026-10-27

Poems: the type follows the level; ▾ at a cell of D022 (collected items 104b, 118).

- **New `POEM_RULES` (R105, R106, R107), `POEM_LEVELS` (work, recording, release), `isPoemRow(row)`, `poemTypeForLevel(row, level)`** (`row.poemLevels`; works: lyricist, recordings: vocal with `primaryText` "spoken vocals", release: `row.poemRelease` or no type; the role credit set once from the role word if empty – `optionCredit`).
- **New question Q010** (`rules: [R105, R106, R107]`, `flag: 'poemLevels'`, `level: 'release'`; lyricist · vocal spoken vocals · liner notes, all release, credit). **Q009** gets `unless: 'poemLevels'`. **`typeQuestionFor`:** `rules` (several rules), `unless`, `level`.
- **`setLevel`:** a row of poems takes the type of the level before `resolveRowType`. **`remapRow`:** keeps it (and the release answer). **`pickType`:** Q010 keeps its answer in `row.poemRelease` (an answer without instrument clears `primaryText`). **`rowLevels`:** all levels for a row of poems; **`nextLevel`:** works → recordings → release → skip for them. **`inEntry`:** rows of poems stay in their entry on the works level.
- **New `singleDaysOf(src, { create })`** (the single days of separate days from the pool – `found` without ":range" – or each day of a period, 2 – 62; pool entries `found` "…:dayN" only with `create`), **`lcdMenuHtml(c)`** (▾ `dm-lcd-menu`, `S.dmLcdMenu`, options `dm-lcd` with `data-pick` single · range · lcd); `matrixCellHtml` shows it for a cell with `lcdOf`. Handlers `dm-lcd-menu`, `dm-lcd` (single: a cell per day as "dm-choose" does; range: the cell takes `lcdOf`, which goes; lcd: `auto` off), log `dmChosen`.
- **CSS:** `.dci-dm-lcdbtn`, `.dci-dm-lcdmenu`, `.dci-dm-date:has(.dci-dm-lcdmenu)`.
- **Texts:** new `typeAsk.askPoemsRelease`, `dm.lcdMenu`, `dm.lcdSingle` (English only).
- **Tests:** new case `poemlevels` in `t_mapping.py`, `poems` adapted (the lyricist row stays in its entry); new case `lcdmenu` in `t_notes_dates.py`; `t_text_places.py` `placedate`: "engineered at" with its own id (694 is "mixed at" in the harness); register golden written anew (Q010, Q009).

## Import 3.32.6 · 2026-10-27

The credits of Bandcamp's "about" text, liner notes signed above them (collected items 115a, 115b).

- **`BANDCAMP.toRelease`:** with rule S049 (`ruleOn('S049')`, on by default) all credits and companies of `aboutRes` are taken, marked `fromAbout` (the members of the band, S041, as before unmarked); its `unrecognized` stay out. `linerNotes` gets `creditLines` (the lines of `aboutRes` that gave a credit) and `artistNames` (the context's and the band's name).
- **`linerNotes(about, { creditLines, artistNames })`:** skips empty lines and credit lines at the end before looking for the signature; new **`artistSignature(line, artistNames)`** – after a sign, one to four words with small letters or digits that are an artist's name or at most two letters off it.
- **New `nameClose(a, b)`** (before the Node export): the same, or a Levenshtein distance of at most two, both of five letters or more (`norm`).
- **`resolveArtists` (name search):** a release artist whose name is `nameClose` to the entry's (not the same) is the first suggestion too, `similar: true`, `release: true`.
- **Rules:** new S049 (special rule). **⚙ Settings → Texts:** `data-set="rule-on" data-rule="S049"` above S050; `resetTopic('texts')` switches both on.
- **Texts:** new `settings.aboutCredits`, `settings.aboutCreditsTitle` (English only).
- **Tests:** new case `aboutcredits` in `t_sources_bandcamp.py` (Node: the credits with S049 on and off, the signature; dashboard: the rows from the "about" text, the composer column with S050, the similar release artist first; the switch); register golden written anew (S049).

## Import 3.32.5 · 2026-10-27

A place with a date after it, typos in role words (collected items 117, 115c).

- **New `PLACE_DATE_TAIL` (T047):** a preposition followed at once by a date (a digit, a month word, a season) up to the end; `placeOf` cuts it off before splitting at commas (before, the part with the date – and the place in it – was dropped for its digits).
- **`TEXT_MONTHS`:** only month words (whole, or three/four letters, `sept`) – "Marseille", "Augsburg" are no months any more (`noDates` took them out of an area).
- **New `ROLE_WORDS` (T048), `roleVocab()`** (ROLE_WORDS plus the words of MB's link types and attributes from `idx()`, cached once MB data is there; in Node only ROLE_WORDS), **`oneEditApart(a, b)`** (Damerau: one swap of neighbours, one letter missing, extra or wrong), **`fixRoleTypo(phrase, check)`** (each unknown word of five letters or more with words one edit apart, tried in combinations of at most 24 – a word may stay – until `check` knows the phrase → `{ phrase, typos: [{ written, read }] }`). Defined before the Node export (used by the text adapter).
- **`TEXT.parse`:** parameters renamed `isRoleKnown`, `isCompanyRoleKnown`; new `typoMode`, `typoCache`, `typoFix(phrase, kind)`, wrappers `isRole`, `isCompanyRole` (typo-tolerant only in typo mode), `readRole(role)`; `addCredit`, `addPlaceholder`, `place`, `inArea` push the role as read and `typos`. In `readUnit` the clause loop body is now `readClause(clause, ci)` (`continue` → `return`): a clause that gave nothing is read again in typo mode (rule S050; its unknown parts of the first reading are dropped); the "role then name" fallback (`roleThenName`) likewise.
- **`groupCredits` / `groupCompanies`:** carry `typos` (per role, once per written word); rows get `row.typos`. **New `typoHtml(row)`** in `roleCell` (`.dci-typo`, `role.typoRead`, rule id S050); `columnHeadHtml`: an **S050** id with the text as title when a row of the column has typos.
- **Rules:** new S050 (special rule), T047, T048 (tables).
- **⚙ Settings → Texts:** `data-set="rule-on" data-rule="S050"` (the rule's own switch: `setRuleOn`, `applyRulesChange`, `renderRulesBody`); `resetTopic('texts')` switches S050 on again.
- **CSS:** `.dci-typo`.
- **Texts:** new `role.typoRead`, `settings.typos`, `settings.typosTitle` (English only).
- **Tests:** text corpus + 5 lines (El Studio, Studio Sol in Marseille, "Muisc and cover art by j4vaman", "Gutiar – Ann Lee", "Recordd at Studio X."; the corpus prints "written …" for a typo, knows "engineered at"); new case `placedate` in `t_text_places.py`; register golden written anew (S050, T047, T048).

## Import 3.32.4 · 2026-10-27

The colours of the kinds: the heads of the works matrix, a setting (collected items 107, 108).

- **New `KIND_COLORS_KEY` (`dci-kind-colors`), `KIND_PALETTE_KEY` (`dci-kind-palette`), `KIND_PALETTE_DEFAULT`; `S.kindColors`, `S.kindPalette`; new `kindPaletteRead()`, `tintOf(hex, share)`, `applyKindColors()`** (CSS variables `--dci-kind-<kind>` and `--dci-kind-<kind>-bg` on the dashboard, class `dci-kindc`; off: all as "other"), **`saveKindPalette()`**; both keys in `TOPIC_KEYS.appearance`; `resetTopic('appearance')` and the reset of all settings set them back; `buildOverlay` applies them.
- **CSS:** `.dci-group` and `.dci-kind-*` take the variables (new `.dci-kind-other`); the heads of the works matrix `th.dci-mx-col.dci-kind-*` with a top bar and light background (paler with `.dci-mx-locked`), `.dci-mx-kind`.
- **`columnHeadHtml`:** new `columnKind(col)`, `columnKindTag(col)` – the class and the tag of the kind in front of the name (also for columns only in MusicBrainz).
- **⚙ Settings → Appearance:** `data-set="kind-colors"` and `data-set="kind-color"` (`data-kind`; shown while chosen in `onInput`, stored in `settingsChange`).
- **Texts:** new `settings.kindColors`, `settings.kindColorsTitle`, `settings.kindColor`, `kind.artist`, `kind.label`, `kind.place`, `kind.area`, `kind.other` (English only).
- **Tests:** new case `kindcolors` in `t_ui_view.py`.

## Import 3.32.3 · 2026-10-27

Questions in the compact line, whole and to click (collected item 102).

- **New `pickInstrument(row, name)`, `pickType(row, i)`:** what the click handlers `instr-pick` and `type-pick` did (they call them now).
- **New `clineAskHtml(kind, label, opts)`:** in `clineHtml` the questions are no `row-open` buttons any more but a `.dci-cl-flag.dci-cl-ask.dci-cl-askq` with buttons (`instr-pick` with `data-instr`, `type-pick` with `data-opt`; up to four) or a list (`data-f="cl-pick"`, `data-kind`; from five – handled in `onChange`).
- **CSS:** `.dci-cl-askq`, `.dci-cl-pick`.
- **Texts:** new `cl.pickList` (English only).
- **Tests:** `t_ui_view.py` case `compact` (the question with its possibilities; answered in the line, the row stays closed), new case `clineask` (Q003 "Directed By": four buttons, "conductor" chosen in the line); `t_rules_window.py` case `quickswitch` reads only the names of the column heads (ready for 3.32.4, whose heads have the tag of their kind before the name).

## Import 3.32.2 · 2026-10-27

The spelling of the release in the head of an entry (collected item 100).

- **New `releaseSpelling(a)`:** for an entry from Discogs (no company), the most frequent name variation (`anv`, without "*") of its rows that differs from the entry's name (without "(n)") – `{ shown, others, base }` or null. **New `entryNameHtml(a)`:** the head's name as `<strong class="dci-gname-anv" data-name="…">` with "*" and a tooltip (`group.discogsName`, `group.otherSpellings`); `groupHtml` uses it.
- **`creditChipHtml`:** leaves out the spelling the head shows.
- **Texts:** new `group.discogsName`, `group.otherSpellings` (English only).
- **Tests:** `t_ui_head.py` case `entryhead`: "B. Man*" with the tooltip "Discogs: Bass Man", no chip; a row credited otherwise: "as “Bassman”"; `t_text_basics.py` (`textcredit`) and `t_text_languages.py` (`nordic`) find an entry by its name (`data-name`) – the head shows "VALFAR*", "M. Mann*".

## Import 3.32.1 · 2026-10-27

"Skip works", the track group form, "Dates & tracks" for waiting suggestions (collected items 106, 90b, 109).

- **Texts, all four languages:** `matrix.skip`, `media.works.skip` ("Skip works", "Werke überspringen", "Omitir obras", "Ignorer les œuvres"), `matrix.unskip` ("Take works again", "Werke wieder nehmen", "Volver a tomar las obras", "Reprendre les œuvres"), `level.workSkipped` (names the button). New `log.poolsOpened` (English only).
- **`trackFormHtml`:** "Name:" and "Tracks:" in a new row `.dci-tg-namerow` (flex, wraps).
- **New `S.poolsForce`** (`{ dates, tracks }` or null; not stored): set in `runImport` after the dates were placed when a cell of the date matrix is `auto`; then `openDashboard()` if the dashboard is closed. `poolsOpen()` is true with it; new `poolFolded(pool)` (the remembered fold, unless forced open) in `poolLabelHtml`, the date pool and the track pool; `pools-toggle` clears it; `pool-fold` of a pool forced open folds it again as remembered.
- **`applyMatrix`:** also takes away the message `dm.titlePlaced`.
- **Tests:** `t_works_more.py` case `worksskip`, `t_media_choice.py` (docstring): the new names; new case `poolsopen` in `t_dates_matrix.py`; there case `pools`: loaded again, the block is open for that import ("folded" stays stored), case `poolsmx` applies the notes' suggestions first.

## Import 3.32.0 · 2026-10-27 · milestone "Quick switches"

Quick switches, a rights society after a writer's name, Performance on several days as what they have in common (collected item 97d).

- **New `QUICK_SWITCHES`, `quickSwitchesHtml()`:** at the top of the body of "Mapping rules" (new container `data-rf="quick"`, drawn in `renderRulesBody`): a checkbox per rule (`data-rule-on`, the change handler of the window: `setRuleOn`, `applyRulesChange`) and its id (`data-qs-goto` → `focusRule`); CSS `.dci-quick`, `.dci-quick-sw`.
- **S045** (new special rule): `TEXT.parse` – new `SOC_AFTER`, `stripWriterSocieties(text)` before `readUnit`, for sentences with a word of writers (new `WRITER_WORDS_IN`): the society after a name goes to `addSociety`, the name stays without it.
- **D022** (new date rule): `placeSeparateDays` (auto, Performance, with a common date of D014): a cell of the common date (new field `lcdOf`) instead of the "choose" cell; `autoPlaceFoundDates`: a period of Performance with a common date – the cell takes the common date (`lcdOf`). New `replaceNotesSuggestions()`: after D022 or D014 was switched, the notes' cells not applied yet (`auto`, not from titles) go and are placed anew (`applyRulesChange`). `autoPlaceFoundDates`: the days and the period of such a cell do not count as "without a group" (`dm.autoPooled`); `usedTextMarks`: the date of the notes is also underlined when the matrix uses its common date (found key `notes:<i>:lcd`).
- **Milestone:** `MILESTONES` with 3.32.0, text `ms.3.32.0` (English only).
- **Texts:** new `rules.quick`, `rules.quickTitle`, `quick.S045`, `quick.D022`, `quick.S021`, `quick.S031`, `quick.S007`, `quick.D023`, `quick.S046` (English only).
- **Tests:** new case `quickswitch` in `t_rules_window.py`; case `notice` (`t_ui_settings.py`): the newest milestones 3.32.0, 3.31.0, 3.29.0; `harness.py`: new `RULES_OFF` (built-in rules switched off before the script starts) – the cases about periods and "choose" run without D022 (`choose`, `trackpool`, `reldate` in `t_notes_dates.py`, `dragdates` in `t_dates_matrix.py`); `datewords`, `discnotes` (`t_notes_companies.py`) and `levels` (`t_ui_view.py`) expect the common month (D022); `titledates` and `perftracks` take the switch of the list (there is one at the top too); `register_golden.json` written anew.

## Import 3.31.8 · 2026-10-27

Performers on tracks, instruments for the release (collected item 111).

- **New `applyPerformerTracks()`, `PERFORMER_WORDS`** (S046): per person (no company, no row by hand, no supplement) the rows of R060 "Performer" (also "Musician", "Performed By", "Played By"; without other details) that are not for the whole release, and the instrument and vocal rows on the recording level for the whole release; on: the instrument rows get the performers' tracks (`s046` keeps tracks and suggestions before, new field `perfPositions`), the performer rows go to "Skip" and out of their entry (`s046Out` with level and tracks); off: both back. Called in `runImport` after `mergePersonPublishers` and in `applyRulesChange` when S046 is switched. Log `perfTracks`.
- **`shownRowsOf`, `groupHtml`:** rows with `s046Out` are not shown. **`roleCell`:** `role.perfTracks` at an instrument row (`.dci-perftracks`); `rulesOfRow` names S046.
- **Register:** new special rule **S046**; `DEFAULT_OFF_RULES` with S046.
- **Texts:** new `role.perfTracks`, `log.perfTracks` (English only).
- **Tests:** new case `perftracks` in `t_mapping.py`; `register_golden.json` written anew (S046 in the window); `t_works_matrix.py` case `mxdrop` waits a moment after a track group was dropped onto a role (under load it read too early now and then).

## Import 3.31.7 · 2026-10-27

Dates in the titles of the tracks (collected item 110).

- **Rules off by default:** new `DEFAULT_OFF_RULES` (`D023`); `ruleOn(id)` is true for them only when the stored list (`dci-rules-off`) holds `+<id>`; new `setRuleOn(id, on)` (the rules window's checkboxes; the quick switches of 3.32.0 will use it too); the reset counts only the rules switched off (`reset.rules`). Export and import keep the list as it is (with `+<id>`).
- **Register:** new date rule **D023** (DATE_RULES).
- **New `placeTitleDates({ force })`:** the titles of the source (`S.srcTracks`, else `S.mbTracks`) through `findDates` – the first date with a day of each title; per date a pool entry (`poolDateFor`, found key `notes:title:<date>`, named as written), a track group (`ensureTrackGroup`, `found`, new field `title`) and an `auto` cell under Performance (new field `title`); once per release and titles (`dm().titleFound`); message `dm.titlePlaced`, log `titleDates`. Called in `runImport` after `autoPlaceFoundDates`, in `reloadPools` (force), and in `applyRulesChange` when D023 is switched on.
- **New `removeTitleDates()`:** D023 switched off – the `auto` cells from titles, their pool entries no row uses, their track groups no cell uses.
- **Texts:** new `dm.titlePlaced.one`/`.other`, `log.titleDates` (English only).
- **Tests:** new case `titledates` in `t_dates_matrix.py`; `register_golden.json` written anew (D023 in the window).

## Import 3.31.6 · 2026-10-27

Tracks from the notes set, with ⓘ (collected item 97c).

- **`applyNotesTrackCredits`** (S022): the rows of the named entry get `tracks`, `notesTracks` and the new field `notesFrom` (the line of the notes); no `suggest` (deleted), no `confirmed` any more.
- **`runImport`, companies** (S043): a publisher's tracks from the notes set `notesTracks` and `notesFrom` instead of `suggest` (source `'notes'`) and `confirmed`.
- **New `notesFromHtml(row)`:** at the row (`roleCell`, both kinds): ⓘ with `matrix.notesFrom` as its title, `role.notesTracks`; a company row with such tracks does not repeat them as `role.source`.
- **`columnHeadHtml`:** ⓘ (`.dci-mx-notesinfo`) with the lines of its rows; **`cellHtml`:** a chip of such a track has `matrix.notesReason` in its title.
- **Texts:** new `matrix.notesFrom`, `role.notesTracks` (English only); `log.notesPubTracks` changed (English only, as before).
- **Tests:** `t_works_matrix.py` case `mxdrop` (Pub Co 1, 3 set, ⓘ, a click takes track 3 out), `t_notes_companies.py` case `publishers` (the tracks set, ⓘ at the row).

## Import 3.31.5 · 2026-10-27

A person as publisher (collected item 97b), publishers on the works or on the release (collected item 112).

- **New `mergePersonPublishers()`** (S044, called in `runImport` after the companies, before the entries left without rows are removed): the publishing rows (C031) of a company whose name (`entryNames`, `looseName`) is that of a person entry go to the person – `entityType: 'artist'`, `types` from `typeOptions.artist`, new field `pubFromCompany`; the company entry is removed when no row is left; log `pubOfPerson` (text changed). **Removed** `personPublishers()` and the column fields `ofPerson`, `personName`, `hasPub`, the CSS `.dci-mx-subcol`, `.dci-mx-hassub`, `.dci-mx-subcell`, `.dci-mx-pubof`, the texts `matrix.pubOfPerson`, `matrix.pubOfPersonTitle`.
- **`computePublisherEvidence`:** a column of an artist with a publishing row: evidence = the tracks the person writes (its own work rows of a writer type, or MusicBrainz's writers of the track), `pubEvidence.state` `'self'`; `cellState`: `unclear` only for publishers that are no artist; `cellHtml` title `matrix.reasonSelf`; `columnHeadHtml` status `matrix.pubSelf`.
- **New `personLikeName(name)`, `NAME_PARTICLES`, `COMPANY_NAME_WORD`, `personPublisher(a)`** (S048): `suggestByName` puts MusicBrainz's artists (`asArtist`, `entityType: 'artist'`) first and sets the new field `personHit` (an artist of exactly that name) – then it drops label hits that are not of the type "Publisher"; `matchHtmlInner`: "Create artist …" (`company-create` with `data-et="artist"`), with `personHit` without "Create label …" and with the search link of the type artist; `startCompanyCreate(company, 'artist')`: the artist form, without the source's label page, texts `artistDlg.title`/`artistDlg.check`. Click handler `name-use`: `renderWorks()` when the company has work rows.
- **Register:** C031 label types `['publishing', 'published']`; `GROUPING_TYPES` with `publishing` (label–release "publishing" has no description; label–work and artist–work "publishing" keep theirs); S044 note new; new special rule **S048**.
- **New `inEntry(row)`:** `shownRowsOf`, `groupHtml` show a publishing row of the work level in its entry too (its level buttons; in the compact view `level-next`); `group.workNote` only for other work rows. `rulesOfRow` names S044 (`pubFromCompany`) and S048.
- **Company rows:** new field `dSpecTracks` – the tracks of a text or the notes shown with `role.source`/`role.tracks`, not as a catalog number (`role.catno`).
- **Texts:** new `role.pubFromCompany`, `matrix.pubSelf`, `matrix.reasonSelf` (English only); `log.pubOfPerson` changed (English only, as before); removed `matrix.pubOfPerson`, `matrix.pubOfPersonTitle`.
- **Tests:** `harness.py` with MusicBrainz's artist–work "publishing" (161), label–release "published" (32) and its grouping "publishing" (359, no description); `t_notes_companies.py` case `publishers` changed (one entry and one column for Tomas Fujiwara; in the pasted text the artist as suggestion, "Create artist …"), new case `personpub`; `register_golden.json` written anew (C031, S044, S048; the page rows of "Big Songs").

## Import 3.31.4 · 2026-10-27

Poems and poetry (collected item 104).

- **Register, role rules:** R005 without "poetry by" and "poem by" (note added); new **R105** (`/^(poems|poetry|poem)( written)? by$/` → lyricist, writer on the works; code: the role credit is the word without "(written) by"), **R106** (recitation, recited by, reciter, poetry reading(s), "poems/poetry/poem read/recited by", and "Poems"/"Poetry"/"Poem" with a bracket "Read By", "Reading", "Recited By", "Recitation", "Spoken" … → vocal, `primaryCands: ['spoken vocals']`, role credit the poem word or "recitation"), **R107** (`/^(poems|poetry|poem)$/` → no type, `notes: ['askType']`, like R100). R106 comes right after R015, R105 right after R005.
- **Register, type questions:** new **Q009** (rule R107; options lyricist (work), liner notes (release), vocal with the instrument spoken vocals; each `credit: true`).
- **New `optionCredit(o, row)`:** the role credit an option gives – its `task` (misc, Q003/Q007), with `credit: true` the role word in lower case without "(written) by", or a fixed `credit` text; used by `remapRow` and the click handler `type-pick` (before: `o.task || ''`).
- **Texts:** new `typeAsk.askPoems` (English only).
- **Tests:** new case `poems` in `t_mapping.py`; `register_corpus.json` eleven roles more ("Poems By", "Poems", "Poetry", "Poem", "Poetry [Read By]", "Poems [Recited By]", "Recitation", "Recited By", "Poetry Reading", "Poems Read By", "Poetry Written By"), `register_golden.json` written anew (changed: "Poem By", "Poetry By" and their lower-case forms; R005, R105–R107, Q009 in the window); `text_corpus.json` a line more ("Poems: Jane Doe. Poetry by John Roe. Recitation: Ann Poe.").

## Import 3.31.3 · 2026-10-27

The kind of engineer said twice (collected item 101). (The fix of item 105 needed only the companion, 1.9.1.)

- **`mapRoleInner(baseIn, modsIn0)`:** for an engineer ("Engineer", "Engineered By", "Engineering") a bracket ending in "engineer" is shortened (`modsIn`, the bracket as written kept in `stripped`): "Recording Engineer" → "Recording"; `out()` lists both as `consumed` (no role credit from the bracket as written).
- **Register:** new special rule **S047**.
- **Tests:** new case `engineers` in `t_mapping.py`; `register_corpus.json` five roles more ("Engineer [Recording Engineer]", "[Mix Engineer]", "[Mastering Engineer]", "[Assistant Engineer]", "[Sound Engineer]"); `register_golden.json` written anew.

## Companion 1.9.1 · 2026-10-27

Status marks and cover box no longer go and come (collected item 105).

- **`BEAT_HIDDEN_MS`** 75000 → 600000 (a page in a background tab counts as open for ten minutes); new constant **`BEAT_VISIBLE_MS`** (8000, as before) in `senderAlive`.
- **`initMusicBrainzSide`:** a `ping` of the dashboard (every 3 s) beats too (`statusBeat`) once a status map came; new `leaving` (set in `pagehide`): no beat while the page goes (a "hidden" beat from `visibilitychange` during closing would count for ten minutes).
- **`initReleasePage`:** the same `leaving` for its `beat`.
- **Tests:** `t_companion_discogs.py` case `relcheck` C: a page in the background five minutes ago keeps the marks (before: 30 s ago), one in front 30 s ago does not.

## Import 3.31.2 · 2026-10-27

Places looked up by name, days with commas only (collected items 98b and 114).

- **`suggestByName` (places):** `areaParts` – the area of the source split at commas, the query uses only its first part (`place:(…) AND area:(West AND Orange)`); without a hit of that name, `place:(…) OR alias:(…)` (name only); a name whose last word is an area (MusicBrainz's area search, name or alias equal by `nameKey`) is also looked up as the rest of the name in that area (`viaArea`, always "similar"; `placeArea` becomes the entry's `area` when it found something); `placeFit`: a place of the same name outside the areas the source names is "similar"; hits in such an area first (`inArea`).
- **`resolveArtists`:** an entry from the Discogs notes (`fromNotes`) logs `nameLookup` instead of `artistMissing`.
- **Dates:** new `DAYLIST_C` (two or more days with commas only); the first two D013 matchers take `DAYLIST` or `DAYLIST_C` (month name and year right after: "November 7, 8, 2016", "7, 8, 9 November 2016", "7., 8. November 2016"); D013's note says so.
- **Tests:** new case `placesearch` in `t_notes_companies.py`; `text_corpus.json` one line more ("Recorded November 7, 8, 2016, at Loft Köln."); `register_golden.json` written anew (D013).

## Import 3.31.1 · 2026-10-25

The smoke tests merged (collected item 103, block R). The script changes only its version (`@version`, `VERSION`).

- **New `smoke/caserun.py`:** `run_cases(globals())` runs the functions `case_<name>()` of a test file in order (or those named on the command line); a stand-in `sync_playwright` gives every case the one browser of the file (`launch()` returns a proxy whose `close()` closes only the case's contexts; `PW = sync_playwright().start()` … `PW.stop()` works the same); what a case changes in `harness` (module values, dicts, lists, sets, reassigned functions such as `discogs_release`) and the shared storage `STORE` are set back after it; each case gets "== name: OK/FEHLER (n s)" from the line "Ergebnis: …" it printed (an exception: its traceback, the case failed); the file ends with "Ergebnis: OK [n Fälle]" or the names of the failed cases.
- **Topic files** (21): `t_text_basics`, `t_text_languages`, `t_text_places`, `t_notes_companies`, `t_notes_dates`, `t_dates_matrix`, `t_works_matrix`, `t_works_more`, `t_mapping`, `t_rules_window`, `t_ui_head`, `t_ui_settings`, `t_ui_view`, `t_ui_place`, `t_sources`, `t_sources_bandcamp`, `t_media_choice`, `t_start`, `t_companion_discogs`, `t_companion_bandcamp`, `t_static` – each case the former `t_<name>.py`, its code unchanged (indented; its docstring as the case's), the imports of `sync_playwright` and `harness` once per file. Kept as files of their own: `t_register.py`, `t_textcorpus.py` (golden tests) and `t_ar`, `t_artwork`, `t_basic`, `t_focus`, `t_release` (compared with logs of an older version). The 89 former files are removed.
- **`harness.py`:** `MB_GAP` (environment `DCI_MB_GAP`, default 25 ms; 0 = the script's own 1100 ms): the copy of the script the tests load (`MAIN`) asks the mock MusicBrainz with that gap – an import takes ~1 s instead of ~11 s; `MAIN_SLOW` is the script unchanged. With the script's gap: the cases `artistworks` (a message after 10 s, no redraw while typing) and `logplace` (the last line of the log), and the five comparisons with older logs.
- **`t_textcorpus.py` / `text_corpus.json`:** a line may name the release's artists (`artists`, S041) and its number of tracks (`tracks`: "1, 3" are tracks then; the companies show their tracks); the company roles of the test also know "rights society"; six lines more (Sounds, band members, ℗ / ©, places from the notes with "Including a 52 p. booklet.", the publishers block, "Published by Z Songs (ASCAP)" and "BIEM/GEMA").
- **`README-tests.md`** written anew: the files with their cases (the former descriptions), running single cases, the gap, a table "former test → file and case".

## Import 3.31.0 · 2026-10-25

Milestone "Text recognition, part 4": publishers and rights societies (collected item 97), a person as publisher.

- **Register:** new special rules **S043** (publishers below a heading, rights societies; `TEXT.parse`, `addNotesCompanies`, `resolveArtists`) and **S044** (a person as publisher; `matrixColumns` → new `personPublishers`, `columnHeadHtml`, `cellHtml`); new tables **T045** (`RIGHTS_SOCIETIES` with `societyForms`, `SOCIETY_ALT`, `SOCIETY_AFTER_NAME`, `SOCIETY_LINE`, `SOCIETY_WORD`, `societyName`, and `PUBLISHER_HEAD`) and **T046** (`NUMBER_WORDS`, `COMPANY_KIND_END`; new `digitWords`, `apartNames`, `sameCompanyName`). `TEXT_COMPANY_RE` (T013, the company roles of texts) also has "rights society".
- **`TEXT.parse`:** a block state `pubBlock` (heading `PUBLISHER_HEAD`, its "(all BMI)" society, ended by an empty line after its items or a line that names no publisher); new `societiesIn`, `addSociety` (company "Rights Society", `society: true`), `PUB_TAIL` and `publisherOf` (name, societies, tracks – "Name (BMI): 1, 4, 6" without track words too; tracks not on the release → not recognized), `addPublisher` (company "Published By" with `pubBlock: true` and the tracks); a line of societies only (`SOCIETY_LINE`); in the "by" branch a society after a publisher's name ("Published by X (BMI)") is taken out of the name and added.
- **`addNotesCompanies`:** also `pubBlock` and `society` companies (S043); the comparison is `sameCompanyName` (before: `looseName` and the generic `looseName` without a guard for names of generic words only); the same role at Discogs: a publisher's tracks from the notes go onto Discogs's company (`tracks`, `notesLine`, the notes' spelling as `who.altNames`); new log `notesPubTracks`.
- **`groupCompanies`** keeps `altNames` and a role's `notesLine`; **`loadRelease`** gives the company entry `altNames` and a row with `notesLine` and tracks `notesTracks` and `suggest: { source: 'notes', text }`; after the import it logs `pubOfPerson` for each person's publisher.
- **`resolveArtists`:** publishers and rights societies with a Discogs link that is not in MusicBrainz are searched by name too (`pubByName`). **`suggestByName`:** `apartNames` of the name and `altNames` searched as phrases; a rights society also by alias, those of the type Rights Society first; `fitOf` adds "similar" for the same `looseName(digitWords(…))`.
- **`roleCell`:** a row of an entry from the notes says "from the notes" (`role.companyNotes`).
- **CSS:** `.dci-mx-hassub` (dashed line to its part), `.dci-mx-subcol` (card with a violet edge, tinted), `.dci-mx-subcell`, `.dci-mx-pubof`.
- **Milestone:** `MILESTONES` 3.31.0, `ms.3.31.0`.
- **Texts (English only):** `log.notesPubTracks`, `log.pubOfPerson`, `matrix.pubOfPerson`, `matrix.pubOfPersonTitle`, `role.companyNotes`, `ms.3.31.0`; `log.notesCompanies` reworded (English only so far: it lists places, labels, publishers and societies).
- **Tests:** new `t_publishers.py`; `t_notice.py` (the notice after a reset lists 3.31.0, 3.29.0, 3.27.0); `register_golden.json` written anew (S043, S044, T045, T046, the company roles of texts).

## Import 3.30.9 · 2026-10-25

The label of ℗ / © lines (collected item 99).

- **Texts:** `TEXT_PC_STRIP` also takes off a year (or years) after the name ("© & ℗ TUM Records Oy 2021" was not recognized – the name kept "2021"); T033 note.
- **`addNotesCompanies`:** also "Phonographic Copyright (p)" and "Copyright (c)" (the signs as named); **`groupCompanies`** passes `fromNotes` to the entry (only without a Discogs id), the entry keeps it; such an entry is searched by name (`suggestByName` for `source.nameSearch || a.fromNotes`) and says "not assigned yet (no link)" (`match.byName`).
- **Register:** new table **T044** `COMPANY_FORM` with **`withoutCompanyForm(name)`** (Oy, Oyj, AB, AS, ASA, A/S, ApS, Ltd, Limited, GmbH, KG, OHG, AG, Inc., LLC, Corp., Co., PLC, Pty, S.A., S.L., S.r.l., B.V., N.V., SAS, SARL, e.K., S.p.A., K.K., Sp. z o.o.); `suggestByName` for a company also searches the name without it, and offers MusicBrainz names that are the same without their legal form (as "similar").
- **Tests:** new `t_pcline.py`; `register_golden.json` written anew (T033, T044); `t_v217.py` 3: four incomplete rows (the label of "©© Fuzzoramarecords 2005" from the notes is not in MusicBrainz).

## Import 3.30.8 · 2026-10-25

Dates per disc, places from the Discogs notes (collected item 98).

- **Register:** new date rule **D021** (in `findDates`: a date without a group right after another one – between them only a bracket and a comma / "and" / "&" – takes its group(s); `MEDIUM_AFTER_DATE` in `datesWithContext`: "(Disc N)", "(CD N)", "(LP N)" right after a date on a release with several media → the tracks of that medium, `x.medium`; another date of the sentence with its own medium, this one none → no tracks); `autoPlaceFoundDates` names such a track group `mediumGroupName` ("Medium 2 · CD"). New special rule **S042** with the new **`addNotesCompanies(rel)`** (in `loadRelease` for Discogs: `TEXT.parse` of the notes, places "… At" not yet in `rel.companies` with that role; same name (`looseName`, also without generic words) with another role → Discogs's `who`; `fromNotes: true`; log `notesCompanies`).
- **Texts:** `TEXT_WHAT_PREFIX` ("All music recorded ... at X": the words for the music, "was/were" and the dots before the verb) for the place branch; `placeOf` splits "Studios in West Orange, New Jersey" also when a part follows the comma; `TEXT_PACKAGE` (T030: "Including a 52 p. booklet.") → `ignored` with `why: 'package'`.
- **Fix:** the count of dates without a group in `autoPlaceFoundDates` leaves out the shared month or year of separate days (`:lcd`, a cell's `lcd`).
- **Texts (English only):** `ignored.why.package`, `log.notesCompanies`.
- **Tests:** new `t_discnotes.py`; `register_golden.json` written anew (D021, S042, T030); `t_msgs.py` and `t_ui301.py` add a date without a group to the harness notes ("The band met on 4 July 2000.") – the shared month of "March 1–3, 2001" no longer gives the second message.

## Import 3.30.7 · 2026-10-25

The members of a band (collected item 96).

- **Register:** new special rule **S041**, new table **T043** (`TEXT_MEMBERS`: "<subject> are / is / consists of / comprises / features / were / was …" (also sind, ist, besteht aus, son, es, sont, est); `TEXT_BAND_SELF`: "the band", "the trio", "we" …).
- **`TEXT.parse(text, { …, artistNames })`:** `isTheBand(subject)` (the names of the release's artist, or `TEXT_BAND_SELF`); in `readUnit`, before the "by" clauses: the names after the verb, each a person (≤ 4 words, capitals, particles like van, de, da) → `addCredit(name, 'Performer', scope, { members: true })` (`addCredit` takes extra fields).
- **`sourceContext`:** `artistNames` from `S.releaseCredit`. **`BANDCAMP.toRelease`:** the credits and the "about" text with the band's name as artist too; from the "about" text, besides places, the credits marked `members`.
- **Tests:** new `t_members.py`; `register_golden.json` written anew (S041, T043).

## Import 3.30.6 · 2026-10-25

"Sounds" asks (collected item 85).

- **Register:** new rule **R104** (`/^sounds$/` → performer, recording); new type question **Q008** (`TYPE_QUESTIONS`: performer · instrument effects; `pending: 'typeAsk.pendingSounds'` – the row keeps its type until answered, unlike Q003/Q005/Q006); `typeAskHtml` shows `q.pending`. **T041** `PROSE_ROLE_WORDS`: sounds → "Sounds" (before "Performer"). `GENERIC_WORDS` + sounds (the role credit "sounds" in lower case).
- **Texts (English only):** `typeAsk.askSounds`, `typeAsk.pendingSounds`.
- **Tests:** new `t_sounds.py`; `t_prose.py` A, `text_corpus.json` (K.M. "Sounds"), `register_golden.json` written anew (R104, Q008, T041).

## Import 3.30.5 · 2026-10-25

Settings without the import, "Source pages", tracks typed into a track group (collected items 88, 90).

- **`openDashboard(opts)`:** `{ settingsOnly }` (⚙ in `#dci-controls`, `data-nav-settings`) – not initialized: no `init()`, a message `settingsOnly.hint` with the action `start-import` instead. New **`initOnce()`** (`init()` once, `S.importStarting` against a second start) for `openDashboard` and the click handler `start-import`. (Careful: `startImport` is already the import of the source inside `init` – a first draft of this version reused the name and stopped every import; `t_ui305.py` B caught it.)
- **Texts:** `settings.t.discogs` "Source pages" in all four languages (de "Quellseiten", es "Páginas de origen", fr "Pages sources"); `nav.settingsTitle` (English) names it; new (English only): `settingsOnly.hint`, `settingsOnly.start`, `trackpool.text`, `trackpool.textPlaceholder`, `trackpool.textBad`.
- **New `tracksFromText(text)`** (ranges, Discogs positions via `positionIndex`, "medium.track", track numbers of the first chosen medium; only tracks of `selTracks()`; `bad` for the rest), **`applyTrackText`** (`onInput` of `data-f="tg-text"`: the ticks and the message without drawing the form anew), **`syncTrackText`** (ticks changed, `onChange` of `tg-track`; `tg-medium` too). `trackFormHtml`: the field "Tracks:" (`f.text`, else `trackListLabel(f.tracks)`). `saveTrackForm` refuses unknown tracks typed in. Enter in `tg-name` / `tg-text` saves.
- **CSS (3.30.3 follow-up):** the lower scroll bar of the works matrix sits at the very lower edge of the window's body (`bottom: -28 u`: sticky boxes keep off the body's padding; it stood above two rows of the matrix).
- **Tests:** new `t_ui305.py`; `t_bcview.py` G (the name of the tab); `t_poolsmx.py` C checks the lower bar at the lower edge.

## Import 3.30.4 · 2026-10-25

Settings join their tabs, bridges from the symbols (collected item 87).

- **New `alignSettingsPane()`:** the top margin of `.dci-set-pane` = the distance of the chosen tab from the top of `.dci-set-wrap` (tabs in a column only; in a row, or with the reset question, none).
- **New `placeBridges()`:** for ⚙ / `[data-el=settings]` and the rules symbol / `[data-el=rules-dock]` (docked and open): the class `dci-bridged` on the symbol with `--dci-bridge-down` (to the lower edge of the head), `dci-bridged-box` on the box with `--dci-bridge-x`, `-w`, `-h` (left edge and width of the symbol, distance from the head) – only while the box is below the head; calls `alignSettingsPane`. Called by `renderSettings`, `syncRulesBtn` (place, open, close of the rules), and – one frame later – on scrolling the body and when the head or the body change size (`ResizeObserver`s in `buildOverlay`).
- **CSS:** the chosen tab overlaps by `-14 u - 1px` (the gap, before fixed −15 px); `.dci-headbtn[aria-expanded="true"]` looks pressed; `.dci-bridged::after` and `.dci-bridged-box::before` draw the strip (tint #ecebf6, purple sides); `.dci-settings` and `.dci-rules-dock` are positioned.
- **Tests:** new `t_bridge.py`.

## Import 3.30.3 · 2026-10-25

Pools fold on their own, scroll bars of the works matrix (collected items 93, 94).

- **State and storage:** `S.poolFold` (`dci-pool-fold`, `POOL_FOLD_KEY`: `{ dates: true, tracks: true }` while folded, nothing when open; `SETTINGS_KEYS`, `resetSettings`).
- **New `poolLabelHtml(pool, n)`:** the name of a pool as a button `data-act="pool-fold" data-pool` (▾/▸, "(n)" when folded); `datePoolHtml` and `trackPoolHtml` (open and kept) use it and return only it while folded. Click handler `pool-fold` (stored, `renderDates`, focus back).
- **Works matrix:** `<div class="dci-mx-hs dci-mx-hs-top" data-mxhs="top">` before `.dci-mx-wrap`, `data-mxhs="bottom"` (sticky at the bottom; in the page above the footer, `--dci-foot-h` from `updatePageScrollPadding`) and `.dci-mx-end` after it. New **`setupMxScroll()`** (called by `renderWorks`): the inner width so that the bars scroll as far as the matrix, scroll positions kept together (a lock against loops), a `ResizeObserver` on the matrix, an `IntersectionObserver` on `.dci-mx-end` (root: the body of the window, the page in the page) shows the lower bar only while the lower edge is out of view; the observers of the drawing before are disconnected (`S.mxScrollObs`).
- **CSS:** `button.dci-pool-fold`, `.dci-pool-n`; `.dci-mx-hs` (always a scroll bar, a light strip), `-top`, `-bottom`, `.dci-mx-end`.
- **Texts (English only):** `pools.foldOne`, `pools.unfoldOne`.
- **Tests:** new `t_poolsmx.py`.

## Import 3.30.2 · 2026-10-25

Rule ids at rows open a window, the arrow in the head of an entry (collected items 75b, 82b).

- **State and storage:** `S.rulesRowPlace` (`dci-rules-rowplace`, `RULES_ROW_KEY`: "window" by default, only "symbol" stored; `TOPIC_KEYS.appearance`, `SETTINGS_KEYS`, `resetSettings`, `resetTopic`), `S.rulesAsWindow` (this time opened from a row as a window; `rulesDocked()` is false then).
- **`openRules(focusId, { fromRow })`:** `fromRow` and "window" and the place "dashboard" → `S.rulesAsWindow`; the handlers `rule-info` / `rule-goto` pass `fromRow`. `setRulesPlace` clears `S.rulesAsWindow` ("Into the dashboard" in such a window docks them). New `setRulesRowPlace`, click handler `rules-rowplace`, row in Settings → Appearance.
- **New `shownRowsOf(a)`, `openAllHtml(a, rows)`, `openAllOfGroup(a)`, `syncOpenAll(a)`:** the button `data-act="group-openall"` (`.dci-gopen`, ▸/▾) first in `.dci-gname` in the compact view; `setRowOpen` updates it; click handler `group-openall`.
- **Texts (English only):** `settings.rulesRowPlace` (+ `.window`, `.symbol`), `group.openAll`, `group.closeAll`.
- **Tests:** new `t_rowrules.py`; `t_rulesdock.py` F (a rule id opens a window now).

## Import 3.30.1 · 2026-10-25

Small fixes (collected items 86, 89, 91, 92, 95).

- **CSS:** `.dci-msgs:not(:empty)` – a bottom margin of 18 u against the −14 u of `.dci-stick` (it covered "▸ 2 messages"), −5 u at the top; `.dci-onlyworks`, `.dci-scope > .dci-sub` (on the line of the buttons); `[data-level="only-works"]` takes the colour of work; `#dci-overlay.dci-inline` – `max-width: var(--dci-inline-max, 100%)`, `min-width: 0`, `box-sizing`.
- **New `fitInline()`:** in the page, `--dci-inline-max` = the width of the browser window from the left edge of the dashboard (minus 12 px); called in `applyPlacement`, `revealDashboard` and on `resize`; the window removes it.
- **`clineHtml`:** the type part ("→ type · instrument", role credit, "credited as") also on skipped lines; "credited as" counts the row's own credit (`entryCredits` leaves skipped rows out).
- **Toolbar:** "only works" (`data-level="only-works"`) in a `.dci-seg.dci-onlyworks` of its own after the levels.
- **`syncModeHtml`:** `title` with `syncMode.hoverTitle` / `syncMode.clickTitle` (English only).
- **Tests:** new `t_ui301.py`; `t_compact.py` E (the skipped line keeps its type).

## Import 3.30.0 · 2026-10-24

"Mapping rules" in the dashboard (collected item 75).

- **State and storage:** `S.rulesPlace` (`dci-rules-place`, `RULES_PLACE_KEY`: "dashboard" by default, only "window" stored); in `TOPIC_KEYS.appearance`, `SETTINGS_KEYS`, `resetSettings`, `resetTopic('appearance')`.
- **New:** `rulesDocked()`, `rulesShown()`, `rulesHeadToolsHtml()` (`data-rules-place`, ✕), **`placeRules()`** (docked: `#dci-rules` moved into the new `<div class="dci-rules-dock" data-el="rules-dock">` after `[data-el=settings]`, class `dci-rules-docked`, `role=region`, no inline geometry; window: back into `document.body`, `role=dialog`, the stored geometry or `defaultGeom('rules')`, to the front), `syncRulesBtn()` (`aria-expanded` of the head symbol), `closeRules()`, `setRulesPlace(place)` (stored, logged, stays open).
- **`openRules`:** the element starts hidden; its head has `<span data-rf="head-tools">`; in the dashboard ⚙ Settings (and the reset question) close; `placeRules`, then the body; scrolled into view, the test field focused without scrolling. Click listener: `data-rules-close` → `closeRules` (focus back on the head symbol when docked), `data-rules-place` → `setRulesPlace`.
- **Click handler:** `rules` toggles from the head (opens elsewhere, e.g. ⚙ Settings → Texts); new `rules-place` (Appearance); `settings-open` closes the docked rules. **Escape:** `rulesShown()` / `closeRules()` instead of the window only.
- **`rebuildDashboard`:** the rules element is taken out of the old dashboard and placed again. **`makeMovable`, `clampWindow`, `resetWindows`:** a docked rules element is neither moved, measured nor reset.
- **Settings → Appearance:** "Mapping rules: in the dashboard | as a window" (`data-act="rules-place" data-place`).
- **CSS:** `.dci-rules-dock[hidden]`, `#dci-rules.dci-rules-docked` (static, full width, at most 72vh, resizable in height, the look of ⚙ Settings), `.dci-rules-tools`.
- **Texts (English only):** `rules.toWindow`, `rules.toWindowTitle`, `rules.toDock`, `rules.toDockTitle`, `settings.rulesPlace`, `settings.rulesPlace.dashboard`, `settings.rulesPlace.window`.
- **Tests:** new `t_rulesdock.py`.

## Import 3.29.3 · 2026-10-24

One entry compact in the full view (collected item 82).

- **State:** `S.groupCompact` (a `Set` of entry keys; cleared with `S.rowOpen` on a new import and when the import is forgotten – not stored).
- **New `groupFolded(key)`** (full view and in the set), **`compactFor(row)`** (compact view or its entry folded) – used by `clineHtml`, `setRowOpen`, `revealRow` and the line update in `refresh` instead of `S.view === 'compact'`; **`foldGroup(a)`** (full view: in or out of the set, the rows of the entry closed; compact view: its open rows closed; `rerenderGroup`, `refresh`, the focus back on the arrow or the first line).
- **`variantsHtml`:** the button `data-act="group-fold"` (`.dci-gfold`, ▾/▸, `aria-expanded`, tooltip `group.fold` / `group.unfold` / `group.foldOpen`) right before "Artist credit for all roles"; **`groupHtml`:** the class `dci-gcompact` on a folded entry; click handler `group-fold`.
- **CSS:** `#dci-overlay .dci-gcompact …` – the rules of the compact view for the rows of one entry (the `.dci-variants` stay visible); `.dci-gfold`.
- **Texts (English only):** `group.fold`, `group.unfold`, `group.foldOpen`.
- **Tests:** new `t_fold.py`.

## Import 3.29.2 · 2026-10-24

Colours of the levels, the level of the compact line by a click, the tab "Appearance" (collected items 79, 81).

- **New `rowLevels(row)`** (`{ levels, names }`, out of `levelCell`), **`workLevelOff(row, level)`** (works matrix skipped), **`nextLevel(row)`** (the row's levels without a switched-off Work, then skip, round). `levelCell` uses them.
- **`clineHtml`:** the level is a `<button class="dci-cl-level" data-act="level-next" data-level data-next>` with the tooltip `cl.levelNext` (a `<span>` when there is no other level); every `.dci-cl-level` has `data-level`. **Click handler `level-next`:** `creditOn` when a row switched off at its source leaves skip, `setLevel(row, next)` (dates of the matrix via `matrixDateForLevel` as before), the focus back on the new button.
- **Settings:** `SETTING_TOPICS` + `appearance` after `general`; the body `appearance` (zoom, place, view – out of `general` – and new: `data-set="level-colors"`, colour inputs `data-set="level-color" data-level`, each with a level pill as preview); `TOPIC_KEYS.general` = lang and log, `TOPIC_KEYS.appearance` = `dci-scale`, `dci-place`, `dci-view`, `dci-level-colors`, `dci-level-palette`; `resetTopic('appearance')` (scale, place, view, colours); `settingsChange` `level-colors`, `level-color`; `onInput` shows a colour while it is chosen (stored on change); `SETTINGS_KEYS` and `resetSettings` know both keys.
- **State and storage:** `S.levelColors` (`dci-level-colors`, only `false` stored), `S.levelPalette` (`dci-level-palette`, only the colours that differ from `LEVEL_PALETTE_DEFAULT`: recording #2f6db5, release #2e8b57, release_group #b0700c, work #8a4f9e; `LEVEL_SKIP_COLOR` #8b8898); `levelPaletteRead`, `saveLevelPalette`, `inkOn(hex)` (dark or white text by luminance), **`applyLevelColors()`** (class `dci-lvlc` on the overlay, CSS variables `--dci-lvl-<level>` and `--dci-lvl-<level>-ink`; called in `buildOverlay`).
- **CSS:** `#dci-overlay.dci-lvlc [data-level=…]` sets `--lvl`/`--lvl-ink`; pressed level buttons filled, the others `box-shadow: inset 0 -3px 0 var(--lvl)`; `.dci-cl-level[data-level]` filled; `button.dci-cl-level`; `.dci-lvl-pick`.
- **Texts (English only):** `settings.t.appearance`, `settings.levelColors`, `settings.levelColorsTitle`, `settings.levelColor`, `cl.levelNext`.
- **Tests:** new `t_levels.py`; `t_settabs.py`, `t_settings.py` (nine tabs, ↓ from General to Appearance), `t_inline.py`, `t_compact.py` (place and view under Appearance).

## Import 3.29.1 · 2026-10-24

Noises, electronics, field recordings (answers of 20:26).

- **`INSTRUMENT_ALIASES`:** `noise`, `noises` → effects, `electronic` → electronic instruments (`electronics` had it already). **`GENERIC_WORDS`:** noise, noises, electronics (lower case in role credits).
- **`PROSE_ROLE_WORDS` (T041):** noises/noise → Noises, electronics → Electronics, field recording(s) → Field Recording(s) (before: noises → Performer).
- **R085:** also "field recordings by", "field recorded by".
- **Tests:** `t_prose.py` F; `register_golden.json` written anew (the aliases, T041, R085, the word list).


## Import 3.29.0 · 2026-10-24 (milestone "Text recognition, part 3")

Credits in prose, places of joined verbs, lists of kinds (collected items 70, 71, 77).

- **Register:** new rule **R103** (`/^cover artwork( by)?$/` → artwork, credit "cover artwork"); new tables **T041** `PROSE_ROLE_WORDS` (sounds/noises → Performer, words/lyrics/texts → Lyrics By, voice/voices/vocals → Vocals, music → Music By) and **T042** `PROSE_FILLER_VERB`, `PROSE_FILLER_BEFORE_NAME`; special rules **S038** – **S040**.
- **`TEXT.parse`:** in the "by" branch – no role before "by": a filler verb at its end is taken off and the role read again (T042); the words before the name ("the guided hand of") are taken off; still no role: new **`namesWithRoles(side)`** (S038: `NAME (roles) & NAME (roles)`, every word in T041 or a role of the register, every name with brackets, an initial keeps its dot) gives the credits. The place without a person: verbs joined by `,`, "and", "&", "+" before "at" each give the place (S039; `placeOf` drops a bracket with digits). **`splitRoles`:** a list of single kinds before the last part also with commas only (`kindsOnly`), and the shared noun in the singular when the kind with it is a role (S040).
- **Milestone:** `MILESTONES` gets 3.29.0 (label with Companion 1.9.0), text `ms.3.29.0` (English only).
- **Tests:** new `t_prose.py`; `text_corpus.json` with the seven lines (the two instrument lists as this test's few instruments read them); `t_notice.py` (milestones 3.29.0, 3.27.0, 3.22.0); `register_golden.json` written anew (only R103, S038 – S040, T041, T042 added).


## Import 3.28.6 · 2026-10-24

Track groups in the notes (collected items 64b, 64c).

- **`tracksInText`:** the vinyl pattern takes a side letter alone at either end (`[A-H]\d{0,2}`, not both bare); a bare letter that is no position of its own becomes the first (start) or last (end) track of that side (`sideOf`, `endOf`). **`trackRefsIn`** has the same pattern (and skips two bare letters).
- **Live:** new **`LIVE_NOTES`** ("recorded/performed live", "live recording", "in/at/during (a) live concert/performance", "live in concert", "recorded in concert") and **`liveNotesTracks(notes)`** (the tracks of the sentences that say live; empty when one of them names no tracks). `applyLiveDefault`: release-level reason `notes` only without such tracks; the tracks get the new reason **`notesTracks`** (`liveOfferText` treats it as the track's own). Text (English only): `matrix.liveWhy.notesTracks`.
- **Tests:** new `t_facets.py` (sides A–F with a side D of one track, three dated track groups in the matrix, "live" offered for track 1 only, no places from the notes).


## Import 3.28.5 · 2026-10-24

Dates in the notes (collected items 64a, 64d, 80, 71/76 for the dates).

- **`DATE_MATCHERS`:** a D013 matcher for days in numbers (`DAYLIST` + month in numbers + year: "19 & 20. 01. 2009", "19./20.01.2009", through `multiDays`), D002 allows a space after each dot, new **D017** (year, month name, day; before D004).
- **`DATE_HINTS`:** new key **`issue`** (issued, released, reissued, first published/released, veröffentlicht, erschienen, publicado, editado, publié, sorti).
- **`findDates`:** the hint is searched only from the new **`sentenceStartAt(src, a)`** on (D019: the cuts of `sentenceAround`; a line ending in ":" counts for the next line); every hint word is kept (`words`), and words joined by `,`, "and", "&", "und", "y", "et", "+", "/" before the closest one form a chain (D020) – returned as **`hints`** when more than one (`[]` otherwise; "©©" gives `['copyright']`); a closest word `issue` drops the date (D018) unless the chain has another group, which becomes the hint.
- **`autoPlaceFoundDates`:** places a find in each of `[hint, ...hints]` – the first with the key `notes:i`, the others with `notes:i~<group>` (their own pool entry, named for the group; `usedTextMarks` finds them by value).
- **Rules:** D017 – D020 new; the notes of D002 and D013 name the new forms.
- **Tests:** new `t_datewords.py`; `t_dragdates.py` takes "Dedicated to the band, 1975." as its date without a group (its "Originally released 1975." is a release year now, D018); `register_golden.json` written anew (the dates carry `hints`; the dashboard's pool has May 2025 under Mix too, for "Mixed and mastered by Jane Roe in May 2025").


## Import 3.28.4 · 2026-10-24

Credited as from a text, the design of a part of the package, joined design tasks (collected items 83, 84; answers of 19:33).

- **`syncSourceCredits`:** no longer only for entries with a Discogs id – an entry without one (a text, Bandcamp: `(a.src || S.source).nameSearch`) gets `sourceCreditFor` with the new rule **S036** (not for `a.placeholder`, not for supplement rows); Discogs entries keep S008. `rulesOfRow` names S036 for them.
- **R062 (design rule):** with the new **S037** and **`DESIGN_PARTS`** (cover, sleeve, booklet, package, packaging, digipak, digipack, inlay, insert) a part among the other words (with only artwork/art/graphics/and besides) gives the credit "`<part> design`".
- **`splitArtTasks`:** tasks whose terms map to the same first type (`mapRole(…).types[0]`) give one role `{ raw: as at the source, base: the first term's, splitBase, artTask, artCredit }` – `artCredit` is the tasks in English joined with "and" (the detail of a term, else its role without "by"). `makeRow(…, { artCredit })` sets `row.artCredit` and `creditFromRole`; `remapRow` keeps it. `rulesOfRow`: S033 for `artCredit`, S037 for an R062 row credited "`<part> design`".
- **`variantsHtml`:** "Artist credit for all roles" is empty when the one name variation differs from the MusicBrainz name only in its case (new **`caseOnlyAnv(a, anv)`**, S031).
- **Tests:** new `t_textcredit.py`; `register_golden.json` written anew (seven roles: "Cover Design", "Design [Cover]", "Package Design", "Sleeve Design" … now "… design"; the notes of S033, S036, S037).


## Import 3.28.3 · Companion 1.9.0 · 2026-10-24

The dates and track groups the dashboard uses, underlined at the source (collected item 63).

- **Import:** new **`trackRefsIn(text)`** (the track references of a text with their place and tracks – the patterns of `tracksInText`, one by one) and **`usedTextMarks()`**: for each date of `dateFinds().notes` (not of a left-out "about" text) its pool entries (`found` `notes:i`, `notes:i:range`, or a notes date of the same value); used when the date matrix has it (`date`, `lcd`, `alt`) or a row not skipped has it as `date.poolId`; the track references of its sentence whose track group (`S.trackPool`, same tracks) is in a cell's `tgs`. Each as `{ kind: 'date' | 'tracks', part: 'notes' | 'credits' | 'about', text, line, ln, ni, n, title }` – `line`: its line, `ln`: how many same lines come before it, `ni`: how often the same text (lower case, single spaces) comes before it in the line, `n`: in the whole part (Bandcamp: credits before `aboutAt`, "about" after). `sendDiscogsStatus` sends them as **`texts`** in the `status-map` (only with `S.dgStatus`).
- **Texts (English only):** `textMark.dateMatrix`, `textMark.dateRow`, `textMark.tracks`.
- **`rulesOfRow`:** `dSplitFrom` gives S033 with `row.artTask`, else S018; new S032 (a translated base in `ROLE_INDEX` or such a detail; a translation through T034 S025), S034 (vocal with remaining details), S035 (`byHeadNoun`), S031 (new **`caseOnlyName(row, a)`**: no credit, not typed, only the case differs).
- **Companion 1.9.0:** new **`TXT_MARK`**, **`textRoots(side)`** (Discogs: `#release-notes`, else a section headed "Notes"; Bandcamp: `bcCredits()`, `bcAbout()`) and **`renderTextMarks(map, side)`** (each text in its line – `bcFindLine(st, line, ln)`, there the `ni`-th time –, else the `n`-th place in `bcStream` of its root, else the last; wrapped from the end with `bcWrap` in `.dci-txt-date` / `.dci-txt-tracks` with the tooltip; overlapping ones left out; Bandcamp: only on the release's own page, `bcPageIn`, after `bcExpand`). `showMap` unwraps them (`bcUnwrap`) before `side.renderStatus` and draws them after. CSS: dashed underline, 2px, purple `#736dab` / orange `#eb743b`. `findCredit` and `locate`: +2 for a line that has the whole role with its details (`cmd.role`), so "Vocals [Clean]" and "Vocals [Screams]" of one artist find their own lines.
- **Tests:** `t_nordic.py` F (the rule ids at the rows); new `t_textmarks.py` (Discogs notes: dates and "Tracks 1-2" underlined, a pool date only after it is dropped onto a row, status off/on; Bandcamp credits and "about"; the two "Vocals" lines).


## Import 3.28.2 · 2026-10-24

Roles in Norwegian, Swedish and Danish, case-only names, an instrument by its last word (collected items 58, 59, 78).

- **Register, tables:** new **`ROLE_TERMS`** (T039: roles `word@no|sv|da` → the English role) and **`ART_TASKS`** (T040: the tasks of an artwork credit → `Design [Logo]`, `Artwork [Art]`, …), indexed by the new **`termIndex(table)`** as **`ROLE_INDEX`**, **`ART_TASK_INDEX`** (`foldWord` as T034). `INSTRUMENT_ALIASES`: `steel drum(s)`, `steel pan(s)` → steelpan.
- **Rules:** new special rules **S031** (`sourceCreditFor`: only the case differs → `''`), **S032** (`mapRole`: a base in `ROLE_INDEX` is mapped as its English term with `translated`; `repeatedDetails`: a detail in `ROLE_INDEX` whose English role has the row's type counts as repeated; `roleCreditForInner`: `translated` gives no credit with S025 or S032), **S033** (new **`splitArtTasks(role)`**, after `splitEngineerTasks` in `parseRoles` and `groupCredits`: one detail – or a role without details – of artwork tasks joined by og/och/and/und/et/y/&/+, every part in T040, at least two different roles → one role per task with `splitFrom`, `splitBase` and `artTask`; a detail only on a role of the artwork types), **S034** (`caseCredit(text, vocab, { lowerUnknown })`, used for vocal types), **S035** (new **`headNounCands(base, { bare })`** – the words before with the last word's other spellings, then the last word alone – appended by `instrumentCandidates(base, mods, { head })`; **`byHeadNoun(base, primary, mods)`**: found only by the last word alone → `roleCreditForInner` returns the wording in lower case; `isKnownRole` refuses that for a name-like phrase, and takes an artwork credit that `splitArtTasks` splits).
- **Rows:** `makeRow(…, { artTask })` → `row.artTask` (S019 does not drop its detail: "Artwork [Art]" keeps "art"); `row.dSplitBase` (the role as written at the source) is the `base` of the status items and of the jump payload, so the companion finds the line "Artwork [Logo Og Kunst]".
- **Tests:** new `t_nordic.py` (Windir-like Discogs credits, the marks of the split line, case-only names and a typed one, "Wood Flute", a pasted text); `register_golden.json` written anew: only instrument candidates were added (the head-noun ones, last), the rules list gained S031 – S035 and T039, T040, the dashboard reads "tenor & soprano sax" now (soprano saxophone through its last word).


## Import 3.28.1 · Companion 1.8.4 · 2026-10-24

A Bandcamp track page as the release, a text, long texts in the settings (collected items 55, 73, 74).

- **`BANDCAMP`:** `ALBUM_RE` → **`PAGE_RE`** (`/album/` or `/track/`); `albumUrl` → **`pageUrl`** (host and kind in lower case, the slug as written; exported as `BANDCAMP.pageUrl`), new **`isTrackPage(u)`**; `releaseLinks` and `parseReleaseId` take track pages – so do the release editor's button (`sourceLinksOf`), Harmony's `src` (`harmonySourceUrls` already wrote `…/track/…`), the release page's links, `discogs-load`, `supp-url` and `testBandcampPage` (which now calls `pageUrl` too). `release()`: with "track pages too" on, a track page is not asked for again (`!isTrackPage(id)`); `testBandcampPage` reports 0 track pages for one.
- **CSS:** `.dci-set-pane .dci-check { white-space: normal; align-items: baseline }`, `.dci-set-pane .dci-check > input { flex: none }` – `.dci-check` stays `nowrap` elsewhere (head, bars).
- **Texts (all four languages – changed texts, not new):** `bc.tracks` ("… the Bandcamp track pages too"), `source.other`, `supp.urlPh`, `bc.testPh`, `bc.testBadUrl`, `msg.badDiscogsId`, `conn.X003`; `@description` names "album or track".
- **Companion 1.8.4:** `bandcampPage()` also returns `trackUrl` (a track page: `https://host/track/slug`); `BANDCAMP_SIDE.releaseId()` is the album or else the track page, new **`releaseIds()`** (album and track page); the heartbeat stores `releaseIds`, `pickTab`/`status` use them (**`tabReleases(t)`**, older tabs: `[releaseId]`), `forHere(map)` matches any of them, and the messages back (`focus-row`, `toggle-credit`, `hover-track`) carry the release of the marks shown (`currentReleaseId()` from `lastMap`). New **`bcPageIn(releaseId)`**: a track page that is the release counts as the release's own page (`''`) for `renderBandcampStatus` and `bandcampLocate` (its title is its one track). `pageFor` loads a track release's page itself.
- **Tests:** new `t_bctrack.py` (a track release from the link, credits once, the tab connected with marks; a track page of an album via "Other source" and "Load the release there"; Node: `parseReleaseId`, `releaseLinks`, `isTrackPage`; "Test page"; the text and the wrapping of the settings in a narrow dashboard).


## Import 3.28.0 · 2026-10-24

The head of an entry, the bar below "Import credits …" (collected items 61, 66).

- **`groupHtml`:** the source link `.dci-dglink` holds the tag and `.dci-dglink-ico` ↗ only (tooltip `link.discogsTitle` with the raw name); new **`entryCredits(a)`** (the distinct "credited as" of the entry's rows, skipped ones left out) and **`creditChipHtml(a)`** (`.dci-gcredit`: `group.creditedAs` / `group.creditedAsMore`, tooltip `group.creditedAsTitle`; hidden without a credit) after the link; `refresh()` redraws the chip of each entry. `clineHtml`: `.dci-cl-as` with the row's credit when the entry has more than one.
- **`renderControls`:** `updateSyncArea(bar, false, false)` – no `syncModeHtml()` in the bar any more; a button `.dci-nav-set` `[data-nav-settings]` (⚙, tooltip `nav.settingsTitle`) added after the status; the document's click handler opens the dashboard (if needed) with ⚙ Settings at `discogs`.
- **CSS:** `a.dci-dglink`, `.dci-dglink-ico`, `.dci-gcredit`, `.dci-cl-as`; `#dci-controls .dci-syncstatus` as a badge with purple buttons (↻ framed), `#dci-controls .dci-nav-set`.
- **Texts (English only):** new `group.creditedAs`, `group.creditedAsMore`, `group.creditedAsTitle`, `nav.settings`, `nav.settingsTitle`.
- **Tests:** new `t_entryhead.py` (only the tag as link; the chip, "(+1)" and the credits in the compact lines; the bar without switches, ⚙ → settings at Discogs and Bandcamp view); new helper `harness.nav_switch(pg, attr)` (a switch in ⚙ Settings) for `t_artwork.py`, `t_bcview.py`, `t_keepmarks.py`; `t_adapter.py` C1 (the link text "Discogs↗"); the baseline of `t_basic.py` (it prints the heads of the entries) is the new head.


## Import 3.27.3 · 2026-10-24

Messages close and fold (collected item 56).

- **`renderMessages`:** each message gets an id when first shown (`msgSeq`, `m.id`), `data-msg`, and a button `.dci-msg-x` `data-act="msg-close"` with the symbol ✕ (an SVG – the text of the message is unchanged); from two messages a line `.dci-msgs-head` with `[data-act="msgs-fold"]` ("▾ / ▸ n messages", `aria-expanded`); folded (`S.msgsFolded`), no message is drawn; a new `warn` or `error` unfolds. `clearMessages` (a new import) unfolds.
- **`onClick`:** `msg-close` (removes the message from `S.messages`), `msgs-fold`. After staging the focus goes to a button of a message (`.dci-inline-btn`), not to its ✕.
- **CSS:** `.dci-msg` with room for ✕, `.dci-msg-x`, `.dci-msgs-head`, `.dci-msgs-fold`.
- **Texts (English only):** new `msgs.count` (one/other), `msgs.fold`, `msgs.unfold`, `msgs.close`.
- **Tests:** new `t_msgs.py` (two messages with ✕ and the fold line, one closed, folded and unfolded by a new error, a fresh import shows its messages again).


## Import 3.27.2 · 2026-10-24

Full view by default, the compact view as a symbol in the head, the heading of the settings, the buttons of the status (collected items 72, 60, 57, 65).

- **View (item 72):** `S.view` defaults to `full`; `VIEW_KEY` (`dci-view`) stores only `compact` (a stored `full` of 3.27.0 reads as full); `setView`, `resetSettings`, `resetTopic('general')` go back to full.
- **Head (item 60):** new `headBtn('view-toggle', 'compact', …)` first in `.dci-head-tools` (new icon `ICONS.compact`), `aria-pressed` while compact, its tooltip `view.toCompact` / `view.toFull` (updated in `applyView`); `onClick` `view-toggle`. `viewToggleHtml()` only in ⚙ Settings → General – no longer in the toolbar.
- **Settings (item 57):** the heading is a button `.dci-set-title` `data-act="settings-fold"` (tooltip `settings.foldTitle`); `onClick` `settings-fold` closes the settings (and the reset question) and focuses ⚙.
- **Status (item 65):** CSS `#dci-overlay .dci-syncstatus button` filled purple, `[data-sync-reload]` purple framed; `.dci-head .dci-headbtn[aria-pressed="true"]`, `.dci-set-title`.
- **Texts (English only, item 68):** new `view.toCompact`, `view.toFull`, `settings.foldTitle` – German, Spanish and French show them in English until the next translation round.
- **Tests:** `t_compact.py` (full at first, ☰ switches and remembers compact, the settings switch back to full); `t_head.py` (the symbol first in the tools; I – with the companion and no Discogs tab, "open in background" purple); `t_settabs.py` (G – the heading folds the settings in, focus on ⚙). The harness still sets `dci-view` = full for the other tests (harmless now).


## Import 3.27.1 · 2026-10-24

Languages: English first, no language list next to the import button, French spaces (collected items 68, 67, 69).

- **Texts:** `tr()` unchanged (it already falls back to English, also for plurals); the rule for new texts is English only (see "How this file is kept"). All 1,457 texts of the four languages are there; no text added or removed.
- **French:** 210 texts with a plain space before ":", ";", "?", "!", "»" or after "«" now have a no-break space (`\u00a0`).
- **Page bar (`insertLauncher`, `renderLauncher`):** the language list (`.dci-bar-lang`, `[data-dci-lang]`) and its CSS are gone; `setLanguage(code, 'bar')` (from the question after the installation) no longer focuses a list.
- **Tools:** `tools/i18n_add.py` takes English alone (other languages left out are skipped; English is required).
- **Tests:** new `t_i18n.py` (keys of the code in English, no left-overs, no foreign placeholders, French spaces, the English fallback in German through Node, a report of the missing translations); `t_connections.py` needs the texts in English only; `t_bar.py` chooses the language in the question after the installation, then in the settings.


## Import 3.27.0 · 2026-10-24 · milestone

The compact view of the entries (collected item 31).

- **Rows (`rowHtml`):** a first cell **`td.dci-c-cline`** with **`clineHtml(row, info)`** (only in the compact view; `.dci-cline`: `.dci-cl-tgl` ▸, `.dci-cl-role`, `.dci-cl-type` – `rowTypeName`, `primaryText`, role credit –, `.dci-cl-level`, `.dci-cl-tracks` with **`tracksShort(row)`** – runs of consecutive tracks, `medium.number` with several media –, `.dci-cl-date` – pool label or `fieldsText` –, the marks `.dci-cl-flag` `.dci-cl-bad` – `info.issues`, `isUnmapped` – / `.dci-cl-ask` – `questionRuleFor` unanswered, `typeQuestionFor` without `typeAnswer` – / `.dci-cl-sugg` – `linerDateSugg` –; on a skipped row `.dci-cl-x` `data-act="remove-row"`); every button of the line `data-act="row-open"`. In the role cell `.dci-cl-close` "▴ compact". `tr.dci-row` and `tr.dci-tracksrow` get `.dci-open` from **`S.rowOpen`**. The compact cell is inside `tr[data-row]`, so `rowOf`, `rerenderRow`, `removeRow` and every query `tr[data-row="…"]` stay as they were.
- **New:** `setRowOpen(row, open, focus)` (classes, focus into the type field or back to ▸), `revealRow(row)` (in `gotoIncomplete`, the companion's `focus-row`, a manual entry added), `setView(view)`, `applyView()` (`#dci-overlay.dci-compact`, `aria-pressed`), `viewToggleHtml(small)`. `refresh()` redraws each compact cell from `rowInfo` when its HTML changed (`data-html`). `add-role` opens the new row. `dmTargetOf`: `tr[data-row] .dci-cl-tracks` (track groups) and `tr[data-row] .dci-cl-date` (pool dates) are drop targets.
- **State / storage:** `S.view` (from the new `VIEW_KEY` = `dci-view`; compact not stored, `full` stored), `S.rowOpen` (not stored; emptied by a new import and by `forgetImport`); `dci-view` in `TOPIC_KEYS.general` and `SETTINGS_KEYS`; `resetTopic('general')`, `resetSettings` back to compact. `onClick`: `row-open`, `view`.
- **UI:** "Compact | Full" (`.dci-viewseg`, `data-act="view"`) first in the toolbar and in ⚙ Settings → General.
- **CSS:** `.dci-c-cline` hidden except in `.dci-compact` for closed rows (the other cells and the track list hidden there), `.dci-cline`, `.dci-cl-*` (tracks in the colours of tracks, date in those of dates, marks red / yellow, skipped rows grey), drag outlines for the compact targets, the "credited as" block (`.dci-variants`) only when a row of the entry is open (`:has`), smaller gaps between cards.
- **Milestone:** `MILESTONES` 3.27.0, `ms.3.27.0` (4 languages).
- **Texts (4 languages):** new `view.label`, `view.title`, `view.compact`, `view.full`, `log.viewSet`, `cl.openTitle`, `cl.close`, `cl.closeTitle`, `cl.noType`, `cl.tracksTitle`, `cl.dateTitle`, `cl.noDate`, `cl.unmapped`, `cl.instrAsk`, `cl.typeAsk`, `cl.dateSugg`, `cl.removeTitle`, `cl.noTracks`, `cl.allTracks`, `cl.track`, `cl.tracks`, `ms.3.27.0`; French no-break spaces in `supp.openTitle` and `log.langAsked` (3.26.0).
- **Tests:** new `t_compact.py` (the default compact: lines, marks, hidden fields; open / close with focus; a track group and a pool date dropped onto the line; the question answered; a skipped row grey with ✕ and back after reloading; "Full" remembered and in the settings; a new incomplete row and the jump to it). **`harness.open_mb_edit(…, view='full')`** sets `dci-view` (and the storage generation) before the script starts, so the other tests keep the full view; `open_mb_any` the same; `view=None` for the default. `t_notice.py`: the three latest milestones 3.27.0, 3.22.0, 3.21.0.


## Import 3.26.0 · 2026-10-24

The head of the dashboard in one line, the language asked after the installation (collected item 30).

- **Head (`buildOverlay`):** without the language select (`data-f="lang"`, now only in ⚙ Settings → General), the place button (`place-toggle`, now only in the settings and the page bar) and "⚙ Settings" as text; new constant **`ICONS`** (own SVG paths: gear, rules, log, info, fit, close, down, plus), `ico(name)` and **`headBtn(act, icon, label, title, extra, cls)`** (symbol, `aria-label` = name, tooltip, the name in `.dci-hlabel`). The order: zoom, `settings-open`, `rules`, `log`, `connections-open`, `window-reset`, `close` (`.dci-close` stays for the focus).
- **`renderSource`:** the line only – the current source, the menu (`.dci-srcwrap` with `[data-act="srcmenu"]` and `.dci-srcmenu` `#dci-srcmenu`: `discogs-pick`, `discogs-input` + `discogs-load`, `.dci-menuitem` `text-open`, `srcorder-toggle`, `bc-toggle`, `about-off`, `forget-open`) and `[data-act="supp-open"]` (`.dci-supp-open`, `.dci-on` and the short mark while a supplement is loaded); everything they open – the question "Delete …", the order of the sources, the Bandcamp settings, the bar "Supplement with", the lines not recognized and left out, the text field – goes to the new **`[data-el="srcpanels"]`** at the top of the body (hidden when empty).
- **State:** `S.srcMenuOpen`, `S.suppOpen`; new `suppIsOpen()` (asked for, a supplement loaded, or its text field open), **`closeSrcMenu(focusBtn)`** (hides the menu without drawing anew). `onClick`: `srcmenu` (toggles, focus on its first field), `supp-open` (toggles; with a supplement loaded only brings the bar into view), an entry of the menu closes it; `supp-remove` closes the bar. `onChange`: a select or checkbox in the menu closes it (a text field not – its change comes before the click on "Load"). A `pointerdown` listener on the document closes the menu outside `.dci-srcwrap`; Escape closes it first (the dashboard stays open). `makeMovable` ignores `.dci-srcmenu`.
- **Status:** `updateSyncArea(el, withDetails, withSwitches = true)` – the head without `syncModeHtml()` (`renderSync` passes `false`); the switches stay in the page bar and ⚙ Settings. `applyPlacement` no longer writes the text of a head button (it would have hit the settings' own `place-toggle`) and draws the settings anew.
- **Language asked (new):** `LANG_ASK_KEY` = `dci-lang-ask`, set once by `markLangAsk()` when nothing of the script is stored (no `dci-notice-version`, `dci-updated-from`, `dci-lang`); `browserLang()`, `trIn(code, key)`, **`renderLangAsk()`** (`#dci-langask` in the page bar after the update notice: radios, OK, hint in the chosen language; OK writes `dci-lang`, removes the key, `setLanguage(code, 'bar')`, log `langAsked`), called from `renderLauncher`.
- **CSS:** `.dci-head` (`container-type: inline-size`, smaller paddings), `.dci-source` (`flex: 0 1 auto`, the link shortened with an ellipsis), `.dci-ibtn`, `.dci-ico`, `.dci-hlabel` (shown with `@container (min-width: 1600px)`), `.dci-srcwrap`, `.dci-srcmenu`, `.dci-srcmenu-row`, `.dci-menuitem`, `.dci-supp-open.dci-on`, `.dci-supp-mark`, `.dci-srcpanels`, `.dci-head .dci-syncstatus` (a badge), `#dci-langask`; `.dci-lang` removed.
- **Texts (4 languages):** new `srcmenu.button`, `srcmenu.title`, `supp.open`, `supp.openTitle`, `langAsk.hint`, `langAsk.ok`, `log.langAsked`; removed `settings.button`, `place.toWindow`, `place.toPage`, `place.toWindowTitle`, `place.toPageTitle`.
- **Tests:** new `t_head.py` (one line, symbols, no language/place/switches in the head, names only when wide; the menu with Escape, a click elsewhere, "Paste text …" below the head; "+ Supplement"; the language question – en preselected, German hint, OK, gone after reloading, fr-FR, no question after an update –; the language in the settings). New helpers `harness.src_menu(pg, act)`, `open_supp(pg)`, `toggle_place(pg)`, `open_settings(pg, tab)`; `t_*` that pasted a text, entered a source, chose a linked source, opened the order of the sources, Bandcamp or "Delete stored import …", ticked "Leave out the about text" go through the menu; `t_supp.py` opens the bar first (A: closed before); `t_inline.py`, `t_jump.py`, `t_manualtop.py` switch window/page in the settings or the page bar; `t_bar.py`, `t_reset.py` choose the language in the settings (`t_reset.py`: `dci-lang-ask` is no setting – a test starts as a first installation); `t_artwork.py`, `t_bcview.py`, `t_keepmarks.py` use the switches of the page bar; the baseline of `t_basic.py` (it prints the head's status) is the new head.


## Import 3.25.0 · 2026-10-24

The settings as tabs, "Reset all" in them, the connections (collected items 42, 41, 40).

- **Settings (`settingsHtml`):** the topics are a tab list instead of folding sections – `.dci-set-wrap` with `.dci-set-side` (`.dci-set-tabs` `role="tablist"`, buttons `.dci-set-tab` `role="tab"` `data-act="settings-topic"` `data-topic`, `aria-selected`, roving `tabindex`; below them `.dci-set-resetall` `data-act="reset-open"`) and `.dci-set-pane` (`role="tabpanel"`: the chosen topic and its "↺" when `TOPIC_KEYS` has keys; with `S.resetOpen` instead `resetHtml()`). No close button inside: only the gear (`settings-open`) folds the settings in and out. `SETTING_TOPICS` gets `texts` and `connections`; `TOPIC_KEYS.sources` without `dci-weblinks-show`, new `TOPIC_KEYS.texts` (`dci-weblinks-show`), `TOPIC_KEYS.connections` empty; `resetTopic('texts')`.
- **State / storage:** `S.settingsTab` (read from the new `SETTINGS_TAB_KEY` = `dci-settings-tab`, `general` not stored) instead of `S.settingsTopics`; `S.resetRules`, `S.resetPools` keep the two boxes of "Reset all" when the settings are drawn anew (`settingsAfterEvent` on `change`). `resetSettings` sets `settingsTab` back and clears `SETTINGS_TAB_KEY` (in `SETTINGS_KEYS`).
- **Reset all (item 41):** the standalone `[data-el="reset"]` below the head is gone; new `resetHtml()` (the same question, boxes, "Reset", "Cancel") inside the pane; `renderReset()` opens the settings and redraws them; `reset-open` toggles and focuses "Cancel", `reset-cancel` focuses "↺ Reset all settings …" again. The head button `reset-open` ("↺ Defaults") is removed; `reset.button` removed (the log of the rules uses `reset.title`).
- **Handlers:** `settings-topic` (chooses and stores the tab, focus on it), new `connections-open` (the ⓘ of the head: settings open at `connections`); `onKeydown`: ↑ ↓ ← → Home End on `.dci-set-tab`. `renderSettings` keeps the focus also on a button (`data-act` + `data-topic`) when it draws anew.
- **Connections (item 40):** new constant **`CONNECTIONS`** (X001 – X010: `id`, `kind` – site, source, tool, script, manager, links –, `name`, `home`, `more`, `hosts`, `perms`, `since`), exported for Node; `connectionsHtml()` – the table `.dci-conn` (name with link, kind, `conn.<id>`, permissions, since); head button `.dci-headbtn` `data-act="connections-open"` "ⓘ".
- **CSS:** `.dci-set-wrap`, `.dci-set-side`, `.dci-set-tabs`, `.dci-set-tab` (vertical, the chosen one joined to the pane), `.dci-set-pane`, `.dci-set-resetall`, `.dci-conn`; `.dci-settings { container-type: inline-size }` with `@container (max-width: 560px)`: the tabs in a row.
- **Texts (4 languages):** new `settings.t.texts`, `settings.t.connections`, `settings.textsHint`, `settings.resetAll`, `connections.open`, `conn.intro`, `conn.th.*`, `conn.kind.*`, `conn.X001` – `conn.X010`, `conn.X004.name`, `conn.X009.name`; removed `reset.button`.
- **Watch out:** the boundary test of the adapters (`t_adapter.py` A) counts `discogs.com/` outside the Discogs adapter – the home page of X002 is written without the last slash.
- **Tests:** new `t_settabs.py` (tabs, keys, remembered tab, Texts, ⓘ → Connections, reset in the pane, narrow), new `t_connections.py` (Node: every address of the header and the code belongs to `CONNECTIONS`, ids unique, texts in 4 languages); `t_settings.py` one tab at a time (`open_set(pg, topic)`); new helper `harness.open_reset(pg)` for `t_reset.py`, `t_inline.py`, `t_logplace.py`; `t_textcorpus.py` (F) and `t_bcview.py` (G) read the tab Texts / the pane.


## Import 3.24.1 · 2026-10-24

The tracks of a source compared with MusicBrainz's on every import and in the dialog of several releases (collected item 52).

- **Register:** new table **T038** (`TITLE_SMALL_WORDS` – en, de, es, fr, it, pt, nl –, `TITLE_NOTE`), new special rule **S030**.
- **Core:** new `titleWordsOf(t)`, **`titlesFit(a, b)`** (same words, `withinOne`, one in the other, more than half of the words of the shorter; numbers must match; placeholders and empty titles fit), **`trackFit(srcTracks, mbTracks)`** → `{ d, m, differ, compared, ok }` (ok: same number and ≥ 80 % fitting), `trackFitText`, `trackFitList`; exported for Node (`titleWordsOf`, `titlesFit`, `trackFit`). `loadRelease`: instead of the count-only warning a message of the new kind `tracks` (`.dci-msg-tracks`, the yellow of suggestions) and the log `tracksDiffer` for every source with tracks of its own (not `usesMbTracks`). `chooseLink`: `counts[i].fit`, a yellow note per row (`[data-lel="tracks"]`, `.dci-link-warn`, the titles as tooltip; log `linkTracksDiffer`), `markBest` among the fitting ones, the mark `links.bestFit` when another has more data.
- **Texts (4 languages):** new `trackFit.count`, `trackFit.titles`, `links.tracksDiffer`, `links.bestFit`, `msg.tracksDiffer`, `log.tracksDiffer`, `log.linkTracksDiffer`; removed `msg.trackMismatch`, `log.trackMismatch`.
- **Watch out:** `tools/i18n_add.py` replaces a key that exists – a first name `tracks.count` would have hidden the plural `tracks.count.one/.other` of the rows; the new keys are `trackFit.*`.
- **Tests:** new `t_tracksfit.py`; register golden (S030, T038).


## Import 3.24.0 · 2026-10-24

A dialog for several linked releases of one source (collected item 51).

- **New `chooseLink(links)`** (a sub-dialog `[data-el="links"]` next to the media dialog, built like it): radio buttons per link (`sourceLinkLabel`, ↗ to its page), the links read one after another with `source.release(id, ctx)` (`sourceContext()` with `bandcampTracks: false`) and counted (`title`, `credits`, `companies`, `tracks`, `notes` length; logs `linkCounted` / `linkCountFailed`); `markBest` – most credits + companies, then the longer notes – bold (`.dci-link-best`), "most data" (`.dci-link-bestmark`), preselected unless a choice was made by hand; "Open all in background tabs" (`GM_openInTab` not active, else `window.open`; log `linksTabs`); OK remembers with `keepSourcePick` unless unticked; `S.subDialog` handle for Escape. **`startImport`:** `start.multi` → `chooseLink`, then `loadRelease` (log `linkChosen`); cancelled → the message `msg.multiLinks` as before.
- **CSS:** `.dci-link-list`, `.dci-link-opt`, `.dci-link-best`, `.dci-link-bestmark`.
- **Texts (4 languages):** `links.title`, `links.intro`, `links.introBc`, `links.counting`, `links.count`, `links.countFailed`, `links.best`, `links.openOne`, `links.tabs`, `links.tabsTitle`, `links.remember`, `links.ok`, `log.linkChosen`, `log.linkCounted`, `log.linkCountFailed`, `log.linksTabs`.
- **Tests:** new `t_links.py`; `t_adapter.py` C8 goes through the dialog.


## Import 3.23.0 · 2026-10-24

The button "Enter edit & import credits" in the release editor instead of the tick (collected item 50).

- **`initReleaseEditorHook`:** the tick is gone; `#dci-after-edit` is now only the note (a span) for a release editor that goes on elsewhere (Harmony with the background tab off, another tool). New `ensureGoBtn()` – the button `#dci-enter-import` right after `#enter-edit`, with MusicBrainz's classes copied and `AFTER_EDIT_BTN_COLOR` (orange `#eb743b`, border/hover `#c55a24`, white text), `disabled` mirrored; new `go()` (sets `goRequested` for 3 s, then clicks `#enter-edit`); `markGo` acts on `goRequested` instead of the tick (and clears it); a `keydown` handler (capture) for Ctrl+Alt+Enter where the button is shown. Text: `afterEdit.button` with `{enter}` = MusicBrainz's own button text; tooltip `afterEdit.buttonTitle` / `afterEdit.buttonTitleBg` with `afterEdit.keys` / `afterEdit.keysMac`. The old stored tick `dci-after-edit` is removed on the release editor.
- **Storage / settings:** new `AFTER_EDIT_BTN_KEY` (`dci-after-edit-btn`, on unless `false`) in ⚙ Settings → Sources (`data-set="after-edit"`, text `settings.afterEdit`), in `TOPIC_KEYS.sources` and the reset list instead of `AFTER_EDIT_KEY`.
- **Texts (4 languages):** new `afterEdit.button`, `afterEdit.buttonTitle`, `afterEdit.buttonTitleBg`, `afterEdit.keys`, `afterEdit.keysMac`; changed `settings.afterEdit`, `log.fromEditor`; removed `afterEdit.label`, `afterEdit.title`, `afterEdit.labelBg`, `afterEdit.titleBg`.
- **Tests:** `t_afteredit.py` rebuilt (button only on "Edit note", right after "Enter edit", orange, tooltip with links and keys; plain "Enter edit" stays plain; the button and Ctrl+Alt+Enter go on; an error; German; setting off; the old tick removed); `t_harmony.py` with the button (background tab, error, note, settings).


## Import 3.22.3 · 2026-10-24

"Kontrabass" without role credit (collected item 47, answer of the maintainer).

- **Register:** `WORDING_RULES` **W003** credit '' (3.22.2: "contrabass"; before: "Kontrabass"), its note.
- **Tests:** `t_v3222.py` part A ("Kontrabass" in a text and from Discogs without credit, "Contrabass" with "contrabass"); register golden (W003).


## Import 3.22.2 · 2026-10-24

Fixed credit pairs (collected item 47), more areas and their larger area (48), role credit of recording checked (49), patterns in the rules window (45).

- **Register:** `WORDING_RULES` **W003** credit "contrabass" (was "Kontrabass"), new **W008** (violoncello → credit "violoncello"); `COMPANY_ROLES` **C041** produced in, **C042** remixed in, **C043** engineered in (area); `TEXT_COMPANY_RE` with "(recorded|overdubbed|mixed|mastered|produced|remixed|engineered) in"; notes of T037 and S028.
- **`patternText`:** the outer brackets (also "(?:") go only when they enclose the whole pattern (a small scan of the brackets, escapes and character classes skipped).
- **Areas:** new **`areaParent(mbid)`** (`area/<MBID>?inc=area-rels`, the backward "part of" relation, `S.areaParents` per session); `suggestByName` adds it to the disambiguation of the shown area suggestions (`SUGG_VISIBLE`).
- **Role credit of recording:** no code change – W007 already gives none; a test now covers the wordings.
- **Tests:** new `t_v3222.py`; `harness.py`: `/ws/2/area/<MBID>` with `AREA_PARENTS`; `t_textcorpus` mirrors the new area roles ("Produced by Pat Prod in Berlin" gives the area); register golden (W003, W008, C041 – C043, the patterns).


## Import 3.22.1 · 2026-10-24

An album on a label's Bandcamp page (collected item 46); people not found through their own link are searched by name.

- **Bandcamp adapter:** `unescapeHtml` (from `pageData`), new **`bandPageName(html)`** (the account's name from "data-band", else "og:site_name"; exported on the adapter), `foldName`, **`ownPage(page, artist)`** (same name without case, accents, punctuation and a leading "The", or the artist's name contains it – as Harmony's Bandcamp provider decides); `toRelease(data, url, trackCredits, ctx, { pageName })` gives `band: { name, url, page, own }`; `linkBand` links the band's name only on its own page, on another page the credit gets `who.pageOf: { name, url }` (no id). `release()` passes `bandPageName(html)`.
- **Core:** `groupCredits` and the artist entries keep `pageOf`; new **`bandPageInfo(rel)`** (log `bcPageOther`; `lookupUrls` of the page as a label → `band.label: { mbid, name, ofRelease }`, log `bcPageLabel` / `bcPageLabelOfRelease`), called in `loadRelease` after `S.release`; the release lookup includes `labels` → new `S.releaseLabels`; new **`pageOfHtml(a)`** below the head of such an entry (`.dci-pageof`), `renderSource` adds "on the Bandcamp page of …" (`.dci-bcpage`). The name search (`suggestByName`) now also runs for people with a source id whose link found nothing (not companies, not after a spelling miss); in `suggestByName` an artist of `S.releaseCredit` with the same name (or found the same) comes first with `release: true` – the stack marks it with `match.markRelease`.
- **Register:** new special rule **S029**.
- **Texts (4 languages):** `bcPage.notOwn`, `bcPage.mbLabel`, `bcPage.ofRelease`, `bcPage.source`, `log.bcPageOther`, `log.bcPageLabel`, `log.bcPageLabelOfRelease`.
- **Tests:** new `t_labelpage.py`; `harness.bc_page(data, band=None)` writes "data-band" and "og:site_name"; register golden (S029).


## Import 3.22.0 · 2026-10-23

Milestone "Text recognition, part 2": tracks named by their titles (collected item 33e), the area where it was recorded (33d).

- **Register:** new tables **T036** (`TEXT_TITLE_Q`, `TEXT_TITLE_SCOPE`, `TEXT_CONTRIBUTION`) and **T037** (`TEXT_AREA_PARTICLE`, `TEXT_NOT_AREA`), new special rules **S027** (titles → tracks) and **S028** (area entries); `COMPANY_ROLES` **C038** recorded/overdubbed in, **C039** mixed in, **C040** mastered in with `area` type options (shown in the rules window); `mapCompanyRole` gives `typeOptions.area` and `prefer: 'area'`; `TEXT_COMPANY_RE` with "(recorded|overdubbed|mixed|mastered) in".
- **Text adapter (`TEXT.parse`):** new parameter `resolveTitles`; `tracksOf` keeps `scope.unresolved`; new `titleScope(phrase)` (the role before "in/on ‘A' and 'B'", the scope with the resolved tracks and the titles not found); `readUnit` has a scope per clause (`cScope`) – the "by" branch strips `TEXT_CONTRIBUTION` and reads the titles before masking quotations, the list branch ("Role: names", "Name – roles") reads them on either side; new `areaOf(text)` beside `placeOf`; new closures `areaRole`, `inArea(verb, where)` (an area company `{ who: { name, area }, role: 'Recorded In' … }`; a verb without an area type: the name without it, `in …` to the unknown parts); in the "by" branch an area on the left (`inL`, after "live/again") or after the name (`inR`), "in <anything else>" before "by" as an unknown part (`inOther`); a new branch for "Recorded in X, Y" without a person.
- **Core:** new **`tracksByTitles(titles, srcTracks)`** (`normTitle` + `workTitleOf` without accents, then `withinOne`), in `sourceContext` as `resolveTitles`; the Bandcamp adapter passes `resolveTitles` for its album tracks and keeps the areas of the "about" text (`/\b(?:at|in)$/`).
- **Area entries:** `groupKindOf` gives the kind `area` (CSS `.dci-kind-area`); `suggestByName` searches areas with `area:(…) OR alias:(…)`, the suggestion names its type and the area it is part of (new `areaContext(x)`: the backward "part of" relation); `matchHtmlInner` shows no **Create** for areas but the hint `match.areaNoCreate`.
- **Texts (4 languages):** `match.areaNoCreate`, milestone `ms.3.22.0`; `MILESTONES` entry 3.22.0.
- **Tests:** new `t_areas.py` (area entry, suggestion via alias, no create, titles → tracks with "not matched", staged "recorded in", Bandcamp titles and about area); `harness.py`: `/ws/2/area` search (and "area:" there is the name, not a place's area); `text_corpus.json` +11 lines, no "later" lines, `t_textcorpus` prints the titles ("on …") and the larger areas ("(Asturies, Spain)"); `register_corpus.json` + "Recorded In", "Mixed In", "Mastered In" and a text with titles and areas, golden updated; `t_notice` expects 3.22.0, 3.21.0, 3.18.0 (not 3.17.0).
- **Watch out:** the area link types are taken from MusicBrainz's relationship editor like all others ("recorded in", "mixed in": area–recording; "mastered in": area–release); a level without the type falls back as for places. `TEXT_NOT_AREA` keeps "Dolby Atmos", seasons, "Studio …" and the like from becoming areas.


## Import 3.21.4 · 2026-10-23

The medium of the release decides (collected item 39), "Translated by" on Bandcamp asks (33h), reasons of the lines left out.

- **Register:** new table **T035** (`MEDIUM_WORDS` vinyl / cd / cassette / digital, `mediumKindOf(text)`, `formatKind(format)`), new special rule **S026**, new question **Q007** (`TYPE_QUESTIONS`, rule R004, `flag: 'askTranslation'`; options liner notes – `suggested`, `task: 'translation'` – and translator); `typeQuestionFor` honours `q.flag`; new **`blankForQuestion(row)`** (no type until answered, on the first option's level; also in `remapRow`); `typeAskHtml` marks a `suggested` option (`.dci-type-sugg`, `typeAsk.suggested`, `typeAsk.suggestedTitle`). `TEXT_THANKS` and `TEXT_COURTESY_LINE` name the reason of a line of `TEXT_IGNORE_LINE`.
- **Text adapter:** `withMedium(t)` (leading medium words, "for vinyl", "(vinyl)"; "master" → Mastering) gives `Role [Medium]`; used by `byRoles` and `listRoles` when the plain roles are none; "Mastered by X (vinyl)" puts the medium on the role; the verb of a place skips medium words and turns "-ing" into "-ed" ("Vinyl LP mastering … at X": Mastered At); a place of roles that are all for one medium gets `medium` (carried by `groupCompanies`). `ignored` entries are `{ text, why }` (`thanks`, `endorsement`, `courtesy`, `web`; Bandcamp track pages with their position).
- **Core:** new `askTranslation(row)` (Bandcamp rows of R004 without details; also for a Bandcamp supplement), `releaseMediaKinds()`, `mediumMissing(kind)` (only when every medium has a known format), `releaseFormats()`, `noteLeftOut()`, `mediumOfRow(row)` (a detail naming a medium, or a lacquer cut), `leftOutForMedium(row, rel, text, fromText)` (left out with `{ why: 'medium', medium, release }` in `rel.ignored`, log `mediumLeftOut`; a fitting medium word of a text is removed from the details), `companyLeftOutForMedium()`; `loadRelease` drops such rows and entries left without one (`leftOutKeys`), `suppRow` and the supplement list too.
- **`renderSource`:** each left-out line `.dci-ign-text` with `.dci-ign-why` (`ignored.why.*`).
- **Texts (4 languages):** `ignored.why.thanks|endorsement|courtesy|web|medium`, `typeAsk.askTranslation`, `typeAsk.suggested`, `typeAsk.suggestedTitle`, `log.mediumLeftOut`.
- **Tests:** new `t_medium.py`; `t_textrules`, `t_freetext`, `t_bandcamp`, `t_textcorpus` read `.dci-ign-text`; `text_corpus.json` +7 lines (left-out entries with their reason, places with their medium); `t_register` golden updated (T035, S026, Q007, "Thanks to everybody" with its reason).


## Import 3.21.3 · 2026-10-23

Links next to names: streaming pages, profiles of labels and places, shown only with a setting (collected items 37b, 37c, answer on 37).

- **T032:** `SOCIAL_HOSTS` with open.spotify.com, music.apple.com, deezer.com, tidal.com, music.youtube.com, qobuz.com, music.amazon.*; new `STREAM_URL`; **`webProfile`** gives their artist pages in MusicBrainz's form (URLCleanup: Spotify without "intl-xx" and query, Apple Music with its country or "us", Deezer without the language, Tidal without "browse", YouTube Music channels, Qobuz "interpreter" pages, Amazon Music "artists/<ASIN>").
- **`parse`:** `giveLinks` also gets the companies of the sentence (`k0`); **`groupCompanies`** merges the links of a name without an id.
- **`webLinkHits`:** leaves out `STREAM_URL` (only for "Create artist …").
- **`startCompanyCreate`:** the web links of a company without a source id as `edit-<type>.url.<n>.text`; the dialog text without a source link via `artistDlg.prefilled` (name, `part.webUrls`).
- **State and setting:** `S.webLinksShow` (`dci-weblinks-show`, off; in `TOPIC_KEYS.sources`, `SETTINGS_KEYS`, `resetTopic('sources')`, `resetSettings`), checkbox `data-set="weblinks-show"` in ⚙ → Sources (`settings.webLinksShow`, title `settings.webLinksShowTitle`), `settingsChange` redraws the entries; **`groupHtml`** shows `.dci-weblink` only with it.
- **Texts (4 languages):** `settings.webLinksShow`, `settings.webLinksShowTitle`; es/fr texts name "Crear artista…", "Créer l’artiste…" as the buttons do.
- **Tests:** `t_textcorpus.py` part F (links hidden at first, the setting, Spotify only for "Create artist", "Create place …" with Studio Sol's profile; companies with their links in the corpus output), `text_corpus.json` +5 lines; `t_register` golden updated (only T032).


## Import 3.21.2 · 2026-10-23

Instruments and voices in German, Spanish and French (collected item 43).

- **Register:** new table **T034** `FOREIGN_TERMS` (English term as Discogs writes it → `"spelling@lang; spelling@lang,lang; …"`), `foldWord()` (lower case, no accents, ß → ss, ’ → ') and `FOREIGN_INDEX` (folded spelling → { term, word, langs }); new special rule **S025** (translations get no role credit); new role rule **R102** (`/^alto$/`, special, `askType`, `translated: 'alto'`) with **Q006** in `TYPE_QUESTIONS` (options with `instrument`: viola, alto saxophone, alto vocals; `ask: 'typeAsk.askAlto'`); **T011** shows `INSTRUMENT_MODIFIER_AFTER` (new) beside `INSTRUMENT_MODIFIER`; **T009** with "y" (`TEXT_ROLE_SEP` `\s+y\s+`, `TEXT_AND_SEP`, new `TEXT_NAME_SEP_Y` – lower case only).
- **`mapRole(base, mods, { noTranslation })`:** a spelling of `FOREIGN_INDEX` is mapped as its term (`noTranslation` for that call, no loop when term and spelling fold alike) and returns `base` (as written), `translated`, `translatedBase`, `langs`.
- **Rows:** `makeRow`, `remapRow` and the role typed by hand carry `translated` / `translatedBase`; **`roleCreditForInner`** returns '' for a translation after the details (S025; a wording rule such as W "Kontrabass" still comes first); **`questionRuleFor`** compares `translatedBase || base` ("bajo" asks like "Bass"); **`instrumentAskHtml`** says so (`instrAsk.otherwiseTr`); a chosen option with `instrument` sets `primaryText` (type-pick and `remapRow`).
- **`isKnownRole`:** the candidates of `mapRole` too (a translation's English term).
- **Text adapter:** `splitRoles` with "y" and the kind after the instrument (`INSTRUMENT_MODIFIER_AFTER`, "saxo tenor y soprano"); `names()` splits at " y ".
- **Texts (4 languages):** `typeAsk.askAlto`, `instrAsk.otherwiseTr`.
- **Tests:** new `t_foreign.py`; `text_corpus.json` +13 lines (de/es/fr), `t_textcorpus.py` stores the English term of a translation ("= Drums", "= ? (asked, R102)"); `t_register` golden updated (only "Coro" → choir without credit, "Kontrabass" via T034, R102, Q006, S025, T034, T011, T009).


## Import 3.21.1 · 2026-10-23

Media: MB's real toggle in the relationship editor, media without a tracklist, tracks the web service leaves out (collected item 44). Checked with musicbrainz-server (`common/hooks/usePagedMediumTable.js`, `release/components/MediumRelationshipEditor.js`, `MediumToolbox.js`, `Controller/WS/js.pm` `tracks`, `Controller/WS/2/Release.pm`) and the release lookup of "Eternal" (57095656-…, 14 CDs, tracks on CD 1 and 14 only).

- **`findMediumToggle(m)`:** first MB's own link `#disc<position>` (`a.expand-medium`, text "2 ▶ CD", no `aria-expanded`); the heading heuristic stays as fallback. New **`mediumFolded(el)`** (`.expand-triangle` ▶) and **`mediumMoreLink(toggle)`** (`a.load-tracks` in the next tbody).
- **`loadMediaInEditor`:** `#expand-all-mediums` when every unloaded medium is in the list; a toggle is clicked only when folded; while waiting, "Load all tracks..." is clicked once it appears; time per medium `max(20 s, 0.2 s × tracks)`.
- **`loadRelease`:** `loadMediaInEditor([...choice.media], { quiet: true })` before `source.release` (was after `applyMediaChoice`).
- **New `pageMediums()`** (the media of MB's page data: id, position, format, name, `track_count`, tracks or null), **`fetchMediumTracks(id)`** (`/ws/js/tracks/<id>?page=N`, all pages, 250 ms apart, with their `linked_entities`), **`wsRelOf(r, linked)`** (a relationship of the editor's JSON in the form of the web service: `target-type`, `type`, `type-id` (link type gid), attribute names, `attribute-values`, `attribute-credits`, `target-credit`, `begin`/`end`, the target with its own relations) and **`completeMedia(ws)`** (called in `init` right after the release lookup: media missing in `ws.media` are added from the page data; a medium with fewer tracks than its `track-count` / `track_count`, or with recordings without `relations`, gets its tracks from `fetchMediumTracks`, converted, so `S.mbTracks`, works and `indexExistingRelationships` work unchanged; logs `mbMediaPartial`, `mbMediumRead`, `mbMediumReadFailed`).
- **`init`:** `S.mediaInfo` with `count`; media without tracks logged (`mbMediaEmpty`).
- **`chooseMedia`:** `empty` (media of `S.mediaInfo` without tracks) named below the intro (`[data-mel=empty]`, `media.empty`); `media.intro` counts all media.
- **Texts (4 languages):** `media.empty.one|other`, `log.mbMediaEmpty.one|other`, `log.mbMediaPartial`, `log.mbMediumRead.one|other`, `log.mbMediumReadFailed`, `err.noMediumId`.
- **Tests:** `t_mediaload.py` rebuilt: MB's editor as MusicBrainz builds it (`a.expand-medium#disc<n>`, hidden tbody, `#expand-all-mediums`, a medium in part with `a.load-tracks`), four media (1, 2, 1, 0 tracks), parts D (media 1 and 3: own toggle) and E (the lookup leaves out medium 2's tracks and medium 1's relationships: read from `/ws/js/tracks`). Harness: `split_media` gives medium ids (4500 + position) and `track-count` / `track_count`; `WS_DROP_TRACKS`, `WS_NO_RELS`, `JS_TRACKS_PAGE`, `JS_TRACKS_CALLS`, `ws_to_js_rel`, `js_tracks`, route `/ws/js/tracks/<id>`, `ws_release(full=False)` with `trim_medium`.


## Import 3.21.0 · 2026-10-19 · milestone

Text recognition, part 1 (collect items 33a, 33b, 33c, 33f, 33g and 37): sentences of a line, ℗ and © together, web addresses, "Logo by", titles in quotation marks and "courtesy of", "Text", lines left out on purpose. Milestone (`ms.3.21.0`, `MILESTONES`).

- **Text adapter (`TEXT`, section 3):**
  - **`parse`** restructured: per line the track list and `TEXT_LABEL_LINE` as before, then **`sentencesOf(line)`** (new) and per sentence **`readUnit(unit, scope, pi)`** (new; the former body of the line loop: ℗ / ©, clauses, "by", places, "Name – roles", "Role: names", "Photography Tom Barrett"). `pi0` runs over all parts of the line (the companion marks each part). Not recognized: the whole line when nothing of it gave a credit, else each sentence that gave none. Returns `ignored` too.
  - **New `sentencesOf(line)`** (T029): splits at `. ! ?` before a capital letter, ℗ / © or a quotation mark – not after an initial, a word of `TEXT_ABBREV` or a word with dots (an address ends a sentence); only when a later sentence is `creditLike` (new: `Role: …`, `… by …`, ℗ / ©, `Name – …`, or a line of T030).
  - **New `takeUrls(s)`** and **`webProfile(u)`** (T032): `WEB_ADDRESS` (TLD list) and e-mail addresses out of the sentence; a profile on `SOCIAL_HOSTS` in MusicBrainz's own form (after `URLCleanup.js`: `https://www.instagram.com/<n>/`, `https://twitter.com/<n>` for x.com too, `https://soundcloud.com/<n>`, `https://www.youtube.com/@<n>`, `https://www.tiktok.com/@<n>`, `https://bsky.app/profile/<n>`, `https://www.threads.com/@<n>`, `https://www.mixcloud.com/<n>/`, `https://vimeo.com/<n>`, `https://myspace.com/<n>`, `https://<n>.bandcamp.com/`; posts and other paths: none) with the text before it; **`giveLinks`** gives it to the credits of the last name before it (`who.links`). Linktree and any other address: left out. A sentence of only addresses, or with a word of `WEB_LABEL` ("Contact: …", "Follow us: …"): `ignored`.
  - **℗ / ©:** `TEXT_PC_SIGNS` (T033) instead of the inline pattern: `P + ©`, `℗ & ©`, `(P) & (C)`, `©©`, year ranges → both company roles; `TEXT_PC_STRIP` takes " · …", " – CAT 123", SPARS codes (`AAD|ADD|DDD|DAD`, capitals only) and "All rights reserved" off the name.
  - **"by":** the match runs on the clause with titles in quotation marks masked (`TEXT_QUOTED_TITLE`, T031: a "by" inside a title does not count); the title with its year is removed from the left side; the right side is cut at `TEXT_COURTESY`. `firstSentence` no longer cuts after a word of `TEXT_ABBREV`.
  - **`TEXT_IGNORE_LINE`** (T030): thanks in several languages at the start, "plays/uses exclusively/only …", "plays/uses … strings/cymbals/reeds/sticks …", "appears courtesy of", "endorse(s/d)" → `ignored` (per sentence; a line of one sentence as it is).
  - **`toRelease`** (text) and the Bandcamp **`toRelease`** pass `ignored` (track pages with their position in front). Neutral release comment: `ignored`, `who.links` of a name without an id.
- **Register:** new **R100** (special, `/^text$/`, no type, `askType`; impl in the special rules) with **Q005** in `TYPE_QUESTIONS` (liner notes · release, lyricist · work; new field `ask: 'typeAsk.askText'`, read by `typeAskHtml`); new **R101** (`logo`, `logo by`, `logo design`, `logo designed by` → design, graphic design, credit `logo`), "logo" out of R073; new date rule **D016** (`DATE_RULES`, matcher before D010: a year right after a closing quotation mark → `skip`); new tables **T029–T033** (`TEXT_ABBREV`, `TEXT_IGNORE_LINE`, `TEXT_COURTESY` + `TEXT_QUOTED_TITLE`, `WEB_ADDRESS` + `SOCIAL_HOSTS` + `WEB_LABEL`, `TEXT_PC_SIGNS` + `TEXT_PC_STRIP`).
- **`groupCredits`:** a name without an id collects the links of all its credits.
- **Suggestions:** new **`webLinkHits(a)`** (`lookupUrls` with each address with and without "/" at the end, keyed in lower case) for artists without an id; **`suggestByName`** puts them first in `a.nameHits` (`viaWeb`), log `webSuggested`. **`suggestStackHtml`:** mark `match.markWeb` ("via instagram.com"), title `match.webUseTitle`. Still only suggestions.
- **`groupHtml`:** a name without an id shows its web profiles (`.dci-weblink`, `webShort()`, title `link.webTitle`).
- **`startArtistCreate`:** without a source id and person data, the entry's web links as `person.urls` (`buildArtistSeed`); the dialog names them `part.webUrls`.
- **`renderSource`:** `<details class="dci-ignored">` (`ignored.title`, `ignored.hint`) after the list of lines not recognized.
- **`type-pick`:** a work level while the works matrix is skipped → `skip`; at work level `renderWorks()` too (before, the matrix was not drawn again – no question had a work level until Q005).
- **CSS:** `.dci-ignored` (summary, ol), `.dci-weblink`.
- **Texts (4 languages):** `ignored.title.one|other`, `ignored.hint`, `link.webTitle`, `match.markWeb`, `match.webUseTitle`, `log.webSuggested`, `typeAsk.askText`, `part.webUrls.one|other`, `ms.3.21.0`.
- **Tests:** new `t_textcorpus.py` with `text_corpus.json` (29 lines from real releases and cases around them, golden; `UPDATE=1`); harness `WEB_URLS` (profiles MusicBrainz has, for `/ws/2/url`); `t_register` golden updated (only R073/R100/R101, Logo, Q005, D016, T029–T033 and "Thanks to everybody" → left out); `t_textrules`, `t_freetext`, `t_bandcamp` (thanks now left out on purpose), `t_recheck` and `t_supp` (another line not recognized instead of the thanks; a supplement does not list lines left out), `t_notice` (3.21.0, 3.18.0, 3.17.0).


## Import 3.20.0 · 2026-10-19

The media dialog: the chosen media loaded in MB's editor in the background, the works question there (collect item 34).

- **`chooseMedia`:** new tick `data-mf="load"` (title `media.loadTitle`, `dci-media-load`, in `SETTINGS_KEYS`) with `[data-mel=load]` (`media.loadState` / `media.loadDone`: the chosen media whose recordings `pageRecordings()` does not have); the box `[data-mel=works]` (`media.worksN` with the title `matrix.askCountTitle`, `media.worksTime`, `data-mact="works"` `data-w` yes/no/skip) shown while the tracks without a work of the chosen media reach `S.awAsk` (not when the matrix is skipped or the lookups were already started); both follow the choice in `sync()`. The result gets `load` and `works` (null when not asked).
- **`loadRelease`:** after `applyMediaChoice`: `applyWorksChoice(choice.works)` and `loadMediaInEditor([...choice.media], { quiet: true })` (not awaited).
- **New `applyWorksChoice(w)`:** logs `worksChosen`; `skip` sets `S.worksSkip`/`S.worksFolded` and `WORKS_SKIP_KEY` (the rows follow at the import), otherwise `S.worksLookups` `yes`/`no`.
- **`loadMediaInEditor(list = null, { quiet })`:** given media (only those not loaded), quiet without the busy line (log `mediaLoadBackground`); waits per medium on its own recordings (before: the media of the filter).
- **CSS:** `.dci-media-works`.
- **Texts (4 languages):** `media.load`, `media.loadTitle`, `media.loadState`, `media.loadDone`, `media.worksN`, `media.worksTime`, `media.works.yes|no|skip`, `log.mediaLoadBackground`, `log.worksChosen`.
- **Tests:** new `t_mediaload.py` (media 2 and 3 of the mock editor not loaded, with toggles).


## Import 3.19.3 · 2026-10-19

A tooltip for what the works question counts (collect item 35), a setting for the rows skipped with the works matrix (item 36).

- **State and storage:** `S.mxSkipRows` (`dci-mx-skiprows`, on; only `false` is stored; in `TOPIC_KEYS.works`, `SETTINGS_KEYS`, `resetTopic('works')`, `resetSettings`).
- **`groupHtml`:** rows with `mxSkipped` only when `S.mxSkipRows`; the hidden ones counted in `group.mxHidden`; `group.workNote` now when the entry has rows on the works level (before: whenever rows were left out).
- **`renderWorksInner`:** the question's `<strong>` has the title `matrix.askCountTitle`; **settings:** the label of `awAsk` has it too, new check `data-set="mx-skiprows"` (`settingsChange`: stores, logs `settingValue`, `renderGroups`).
- **Texts (4 languages):** `matrix.askCountTitle`, `settings.mxSkipRows`, `group.mxHidden`.
- **Tests:** `t_worksskip.py` (D: the tooltips; G: the setting off and on).


## Import 3.19.2 · 2026-10-19

The relationship editor in a background tab after an import with Harmony (collect item 32), the note reworded (item 38).

- **Header:** `@grant GM_openInTab`; `@date` 2026-10-19; `/* global … GM_openInTab */`.
- **Section 3b:** `AFTER_EDIT_BG_KEY` (`dci-after-edit-bg`, localStorage, default on: only `false` is stored), `OPEN_HASH` (`dci-open`).
- **`initReleaseEditorHook`:** with a redirect to Harmony and the setting on, the checkbox is shown (`data-bg="1"`, `afterEdit.labelBg`, title `afterEdit.titleBg`); otherwise the note (`afterEdit.toHarmony`, reworded; `afterEdit.toOther`). `markGo` with such a redirect: sets `#dci-open` on `MB.releaseEditor.redirectURI` (the plain one kept in `plainRedirect`, back with `restoreRedirect()` when `submissionInProgress` turns false), writes no `AFTER_EDIT_GO_KEY`.
- **`initHarmonyHook`:** new inner `openBackground()` – with `#dci-open`: the sign taken off (`history.replaceState`), `GM_openInTab(href, { active: false, insert: true, setParent: true })` (else `GM.openInTab(href, true)`), the text `harmony.opened` after the link; called after the action is placed.
- **Settings:** topic `sources` gets `data-set="after-edit"` and `data-set="after-edit-bg"` (`settingsChange`, log `settingValue`); `TOPIC_KEYS.sources` and `SETTINGS_KEYS` with both keys.
- **Texts (4 languages):** `afterEdit.toHarmony` (changed), `afterEdit.labelBg`, `afterEdit.titleBg`, `settings.afterEdit`, `settings.afterEditBg`, `harmony.opened`.
- **Harness:** `open_mb_any` records `GM_openInTab` calls in `window.__gmTabs`.
- **Tests:** `t_harmony.py` (A: note with the setting off; A2: tick and background tab; A3: error – return address as before; E: settings).


## Import 3.19.1 · 2026-10-19

The link "Edit relationships with Credits Importer" on Harmony's "Release Actions" (collect item 29).

- **Header:** `@match https://harmony.pulsewidth.org.uk/release/actions*`.
- **Section 3b:** `HARMONY_HOST_RE`, `IMPORT_HASH` (`dci-import`); new `importUrl(base, mbid, urls)` (`…/release/<MBID>/edit-relationships#dci-import&src=…`), `harmonySourceUrls(params)` (Harmony's `bandcamp=band/title` and `band/track/title`, `discogs=<id>`, `url=…`), `initHarmonyHook()` (with `release_mbid`: `div.action#dci-harmony` – Harmony's sprite icon `database-edit`, a link with target `_blank`, text `harmony.link`, title `harmony.title`/`harmony.titleNone` – after the action of "Add cover art", else of "Open in MusicBrainz", else at the end of `main`; the MusicBrainz origin taken from those links when it is `*.musicbrainz.org`; a `MutationObserver` for 30 s if the page is not built yet).
- **Section 4:** on Harmony's host only `initHarmonyHook()` (on `/release/actions`), before anything else.
- **`initReleaseEditorHook`:** new `redirect()` (`MB.releaseEditor.redirectURI`); with one, the checkbox is hidden and the label says `afterEdit.toHarmony` or `afterEdit.toOther` (`{host}`), `data-redirect` the host; `markGo` notes nothing then.
- **Relationship editor:** `S.autostartFrom` (`'editor'` or `'link'`); `S.editorLinks` also from `#dci-import&src=…` (through `sourceLinksOf`, the # taken off with `history.replaceState`); the logs `fromLink`/`sourceFromLink` instead of `fromEditor`/`sourceFromEditor` for a link.
- **Texts (4 languages):** `afterEdit.toHarmony`, `afterEdit.toOther`, `harmony.link`, `harmony.title`, `harmony.titleNone`, `log.fromLink`, `log.sourceFromLink`.
- **Harness:** `EDITOR_REDIRECT` (a seeded `redirectURI` per kind; "Enter edit" then goes there with `release_mbid` as MusicBrainz does), a route for Harmony's `/release/actions` (actions as `div.action`), `open_mb_any(…, all_tabs=True)` (the script in every tab of the context; also on Harmony).
- **Tests:** new `t_harmony.py`.


## Import 3.19.0 · 2026-10-18

The tick "open relationship editor and start import dashboard" in the release editor (collect item 18).

- **Header:** `@match *://musicbrainz.org/release/*` and `*://*.musicbrainz.org/release/*` instead of `…/release/*/edit-relationships*`.
- **New section 3b** (before "4. MusicBrainz access"): `AFTER_EDIT_KEY` (`dci-after-edit`, localStorage, the tick; in `SETTINGS_KEYS`), `AFTER_EDIT_GO_KEY` (`dci-after-edit-go`, sessionStorage: `{ release: MBID or 'new', links, at }`), `AUTOSTART_KEY` (`dci-autostart`, sessionStorage: `{ release, links, at }`), `AFTER_EDIT_MAX_MS` (10 min); `releasePageKind(path)` (`relationships`, `editor` for `/release/add` and `/release/<MBID>/edit`, `release`, else `null`), `sourceLinksOf(urls)` (through `SOURCES[k].releaseLinks`), `afterEditLinkLabel(l)`.
- **`initReleaseEditorHook()`:** the label `#dci-after-edit` (checkbox, `afterEdit.label`, title `afterEdit.title` with the links) before `#enter-edit`; shown (`inline-flex`) only while the button is visible and `#external-links-editor tr.external-link-item` has a Discogs release or Bandcamp album (`a.url` without `rel-remove`, or the `input.value`); updated by a `MutationObserver` and `input`/`change` (150 ms). Submission: `MB.releaseEditor.submissionInProgress.subscribe` – true writes `AFTER_EDIT_GO_KEY` (ticked, shown, with links), false (an error) removes it; without the observable a click on `#enter-edit` (capture) writes it.
- **`initReleasePageHook()`:** reads and removes `AFTER_EDIT_GO_KEY`; within 10 minutes and for this release (a new release: `document.referrer` from `/release/add`) it writes `AUTOSTART_KEY` and goes to `/release/<MBID>/edit-relationships` (`location.assign`).
- **Section 4:** after `releaseMbid` the page kind decides: `editor` → `initReleaseEditorHook`, `release` → `initReleasePageHook`, other than `relationships` → nothing (return before anything of the dashboard).
- **Relationship editor:** `S.editorLinks` (read once from `AUTOSTART_KEY` for this release, within 10 minutes), `S.autostart`; `init` logs `fromEditor`; `startSource` merges `S.editorLinks` into `S.sourceLinks` and returns a single link MusicBrainz does not have (`fromEditor`, logged as `sourceFromEditor` in `startImport`); new `openWhenReady()` (waits for `MB.linkedEntities.link_type`, up to 30 s) is called after `insertLauncher` when `S.autostart`.
- **Texts (4 languages):** `afterEdit.label`, `afterEdit.title`, `log.fromEditor`, `log.sourceFromEditor`.
- **Harness:** `EDITOR_LINKS`, `mb_release_editor_page(kind)` (tabs, `#external-links-editor`, `#enter-edit`, `MB.releaseEditor.submissionInProgress`, `__tab`, `__submit`), routes `/release/<REL>/edit` and `/release/add`, `open_mb_any(ctx, url)` (the main script on every MusicBrainz page of the tab, also after navigations).
- **Tests:** new `t_afteredit.py`.


## Import 3.18.0 · 2026-10-18

Milestone. Skip and fold the works matrix, the question before long work lookups (collect item 26); "Add entry manually" as one line in the sticky block above the date pool (collect item 25).

- **State and storage:** `S.worksSkip` (stored per release, `WORKS_SKIP_KEY` = `dci-works-skip:<MBID>`, cleared by `forgetImport`), `S.worksFolded` (not stored; starts as `S.worksSkip`), `S.worksLookups` (`null` not decided, `'ask'` question shown, `'yes'`, `'no'` – for the page). New setting `AW_SETTINGS.awAsk` (`dci-aw-ask`, 100, 0–10000, 0 = never; in `TOPIC_KEYS.works`, `SETTINGS_KEYS` and the resets through `AW_SETTINGS`); `settingsChange`: a changed `awAsk` while the question is open asks anew (or starts the lookups).
- **New functions:** `worksResting()` (skipped, `'no'` or `'ask'`), `worksLookupsAllowed()` (the gate of both lookups: resting → false; with `S.awAsk` and `tracksWithoutWork().length >= S.awAsk` it sets `'ask'`, logs `worksAsk` and draws the works section), `worksLookupMinutes()` (tracks + 3 per artist target, 1.1 s each), `setWorksLookups(yes)`, `setWorksRowsSkipped(skip)` (rows on the works level → `skip` with `row.mxSkipped`; back: `level 'work'`, or `srcOffLevel`/`aboutLevel` = `'work'` for rows switched off at the source or hidden with the about text), `setWorksSkip(skip)` (stores, folds, rows, stops a running search, logs `worksSkipped`/`worksTaken`, draws; taken again it starts both lookups).
- **Lookups:** `autoSearchWorks` and `runArtistWorks` return unless `worksLookupsAllowed()`; their loops stop when `worksResting()`; `loadArtistWorks` stops between two requests (`entry.stopped`, not stored, not kept in `S.artistWorks`); `checksDone`/`artistWorksDone` are not logged after a stop.
- **`computePlan`:** with `S.worksSkip` no links to works from `S.workPlan` (also not in `planned`, so staged links become removals), no attribute fills of existing links, no date fills (`S.dateFills`), no "waiting" tracks; a row on the works level meanwhile gets the issue `issue.worksSkipped` and nothing staged.
- **Rows:** `loadRelease` applies the skip after the about/source switches and again after S006; `applySupplement` too; `toggleCredit` keeps `mxSkipped` (a work row switched on again stays on "Skip" while skipped), `setAboutRowsHidden(false)` too; explicit level choices (`setLevel`, `bulk-level`, `type-pick`, `mx-col-remove`) delete `mxSkipped`. `levelCell`: the "Work" button is disabled while skipped (title `level.workSkipped`).
- **`renderWorksInner`:** a head `.dci-works-head` with the fold button (`mx-fold`, `aria-expanded`), `mx-skip` (`data-on`), the badge `.dci-works-skipped` and, folded, what it holds (`[data-el=works-folded]`: tracks · works · columns or rows on "Skip"); the hint `matrix.skippedHint`; the question `.dci-mx-ask` (`[data-el=works-ask]`, `mx-lookups` with `data-on`) and after "Not now" `[data-el=works-lookups-off]`. Folded: only the head. Skipped and unfolded: no bars, the matrix `inert` and dimmed (`.dci-works-off`). `matrixAction`: `mx-fold`, `mx-skip`, `mx-lookups`.
- **"Add entry manually":** the overlay has a sticky wrapper `[data-el=stick]` (`.dci-stick`, the sticky rules of `.dci-dates` moved there; `.dci-stick:not(:has(> :not([hidden])))` hidden) with `[data-el=manual]` (one flex line: `.dci-manual-title` with `manual.hint` as title, the entry field with the same title, role, "Add", `manual-search` "?" toggling `[data-el=manual-search]`) above `[data-el=dates]`. The move of the manual block before the works is gone. The `ResizeObserver`, `updatePageScrollPadding` and `dragAutoScroll` measure the wrapper. `addManualEntry` lights the new row up (`dci-flash`).
- **CSS:** `.dci-works-head`, `.dci-works-fold`, `.dci-works-skipped`, `.dci-works-off`, `.dci-mx-ask`, `.dci-stick`, the new `.dci-manual` rules (old `.dci-manual h3`, `.dci-manual-form` removed), `#dci-overlay.dci-inline .dci-stick`.
- **Texts (4 languages):** `matrix.fold`, `matrix.unfold`, `matrix.skip`, `matrix.skipTitle`, `matrix.skipped`, `matrix.unskip`, `matrix.skippedHint`, `matrix.skippedRows`, `matrix.cols`, `matrix.askLookups`, `matrix.askTime`, `matrix.lookupsYes`, `matrix.lookupsNo`, `matrix.lookupsOff`, `matrix.lookupsNow`, `issue.worksSkipped`, `level.workSkipped`, `settings.awAsk`, `settings.awAskTracks`, `settings.aria.awAsk`, `manual.searchTitle`, `log.worksAsk`, `log.worksLookupsOn`, `log.worksLookupsOff`, `log.worksSkipped`, `log.worksTaken`, `ms.3.18.0`; `MILESTONES` with 3.18.0.
- **Header:** `@date` 2026-10-18.
- **Tests:** new `t_worksskip.py`, `t_manualtop.py`; `t_inline.py` (the sticky wrapper at the top), `t_notice.py` (3.18.0, 3.17.0, 3.16.0, not 3.15.0).


## Import 3.17.6 · 2026-10-18

The date of the liner notes as a suggestion at their row (collect item 21).

- **`autoPlaceFoundDates`:** the pool entry of a date inside the liner notes' signature gets `liner` (the name).
- **New `linerDateSugg(row)`:** the pool entry with `liner` for the liner notes row of that name (`fromAbout`, role "Liner Notes", not `row.linerDateOff`).
- **`dateCell`:** without a date, the suggestion as `.dci-datechip.dci-datechip-sugg` (title `date.suggLiner`) with ✓ (`date-take`, `data-pool`) and ✕ (`date-sugg-off`) before "+ Date".
- **`onClick`:** `date-take` → `applyPoolToRow` + `refresh`; `date-sugg-off` → `row.linerDateOff`, `rerenderRow`.
- **CSS:** `.dci-datechip-sugg` (dashed, the colours of suggestions).
- **Texts (4 languages):** `date.suggLiner`, `date.take`, `date.dropSugg`.
- **Tests:** `t_linernotes.py` E (the suggestion at the row, ✓ takes it).


## Import 3.17.5 · Companion 1.8.3 · 2026-10-18

A click on a mark switches its credit, also on Discogs (collect item 20); marks kept after the editor is closed (collect item 23).

- **Renamed and generalized (3.17.1 → 3.17.5):** `S.bcOff` → `S.srcOff` (entries `source|name|role`), `BC_OFF_KEY` kept only to take over its entries (as `bandcamp|…`) and cleared, new `SRC_OFF_KEY` (`dci-src-off:<MBID>`), `bcOffKey` → `srcOffKey`, `saveBcOff` → `saveSrcOff`, `bcCreditOn` → `creditOn`, `toggleBcCredit` → `toggleCredit`, `bcOffHtml` → `srcOffHtml` (`.dci-srcoff`, `bc.offNote` with `{site}`), `row.bcOff`/`bcOffLevel` → `row.srcOff`/`srcOffLevel`. `loadRelease` restores switched-off rows for any source the companion shows (not manual, not of a supplement). Logs `log.srcOff`/`log.srcOn` with `{site}` (`log.bcOff`/`log.bcOn` removed).
- **`sendDiscogsStatus`:** Discogs items get `off` too; label `hover`; the map gets `toggle` (`S.clickToggle`) and `keepAfterClose` (`S.keepMarks`).
- **`onFromDiscogs`:** `focus-row` with `hover` only in an open dashboard and without a log line; `toggle-credit` for both sites, only with `S.clickToggle`.
- **New settings:** `S.clickToggle` (`dci-click-toggle`, default on, stored only when off), `S.keepMarks` (`dci-keep-marks`, default off); buttons `data-click-toggle` / `data-keep-marks` in `syncModeHtml` (navigation, dashboard head, settings topic), pressed states in `updateSyncArea`, document click handler (log `log.clickToggle` / `log.keepMarks`, `sendDiscogsStatus`); `TOPIC_KEYS.discogs`, `SETTINGS_KEYS`, topic reset and `resetSettings`.
- **Texts (4 languages):** `sync.clickToggle`, `sync.clickToggleTitle`, `sync.keepMarks`, `sync.keepMarksTitle`, `dgStatus.hover`, `log.srcOff`, `log.srcOn`, `log.clickToggle`, `log.keepMarks`; changed `dgStatus.off`, `dgStatus.on` ("click: skip this credit …" / "click: take this credit again"), `bc.offNote`.
- **Companion 1.8.3:** MB side stores `keepMarks` from the status map (GM). `initSourceSide`: `forHere(map)`, `keptMap()` (with `keepMarks`: the per-release map `statusMap:<MBID>` of this page from `statusMapIndex`), `showMap` shows the live map or the kept one (`shownMap`, `live`, `shownSig`; the 3-second check compares the signature); click on `.dci-dg-mark`: nothing when not `live`, `toggle-credit` with `shownMap.toggle` (off = the mark is not `.dci-mark-off`), else `focus-row`; mouse resting on a mark (`MARK_HOVER_MS` 450) → `focus-row` with `hover`. New `markTitle(map, item, status, note, where)` for Discogs and Bandcamp marks. Discogs `renderStatus`: `.dci-mark-off`, the credit's `li` greyed (`.dci-dg-offline`) when all its marks are off. Bandcamp: no ⊘ (`.dci-bc-markwrap`, `.dci-bc-off` gone), `.dci-mark-off` instead of `.dci-bc-isoff`. Release page: a checked map is also written to `statusMap:<MBID>` (kept marks show the checked state).
- **Tests:** `t_bcoff.py` adapted (a click on the mark; resting the pointer shows the row; `dci-src-off`), `t_bcview.py` D with "Click switches" off; new `t_keepmarks.py` (A–C: Discogs hover → row, click off/on with greyed line, "Click switches" off → row, "Keep marks" off/on, kept marks do not send clicks).


## Import 3.17.4 · 2026-10-18

The source in the navigation bar (collect item 22), links at name suggestions (collect item 24).

- **New `srcLinkHtml()`:** `a.dci-srclink` to `S.release.url` (https only, a source the companion knows), "↗ " + `VIEW_NAMES[viewSite()]`, title `sync.srcLinkTitle`.
- **`syncStatusHtml(withDetails)`:** the link after every status; "open in background" (`sync-open`) and "Load the release there" (`sync-load`) also without `withDetails` (navigation bar); `withDetails` now only adds the last jump's result.
- **New `syncAction(act)`** (from the `onClick` cases `sync-open` / `sync-load`); the document click handler calls it for those buttons inside `#dci-controls` (outside the dashboard).
- **`suggestStackHtml`:** each suggestion wrapped by `item(btn, type, mbid)` in `.dci-suggitem` with `a.dci-sugglink` (`/<type>/<mbid>`, new tab, `match.openNew`); type: `artist` for alias hits, `h.entityType` (else label/artist) for name hits.
- **CSS:** `.dci-suggitem`, `.dci-sugglink` (joined to the suggestion box), buttons of `#dci-controls .dci-syncstatus`, `.dci-srclink`.
- **Texts (4 languages):** `sync.srcLinkTitle`, `match.openNew`.
- **Tests:** new `t_navlink.py` (A–D: bar with link and "open in background", "Load the release there" from the bar, Discogs link, ↗ at artist and label suggestions).


## Import 3.17.3 · Companion 1.8.2 · 2026-10-18

The release page keeps its result (collect item 27), distribution (collect item 28).

- **Companion 1.8.2, `initReleasePage`:** `checkOnce` returns `false` without writing when the release cannot be read (`!res.ok` or an error) – before, it wrote the dashboard's items unchecked (`checked: 0`); `check` retries after `RECHECK_MS` (15 s, at most 8 times), `retries` reset after a check that read MusicBrainz. Beat also on `visibilitychange`.
- **Companion 1.8.2, beats:** `statusBeat` of the edit page and of the release page carries `hidden` (`document.visibilityState`); the edit page beats again on `visibilitychange` and sets its beat to 0 on `pagehide` (as the release page did); `senderAlive` allows `BEAT_HIDDEN_MS` (75 s) for a hidden sender, 8 s otherwise.
- **Register:** new table **T028** `TEXT_DISTRIBUTION` (distribution, distributor, distributed, vertrieb, distribución, distribué … ) in `TABLES`.
- **`TEXT.parse`:** `distribution(t)` (T028, a trailing by/par/por/da/durch/via left out) → `['Distributed By']`; used first in `byRoles` ("Distribution by X") and `listRoles` ("Distribution - X", "Distribution: X"); a clause "<word> par/por/da/durch/via/through X" whose word is in T028 adds X with "Distributed By" (before the place rules). The company role itself is C006 as before.
- **Tests:** new `t_relcheck.py` (A–C: ✓ after "Enter edit", a failing check keeps ✓ and is retried, a hidden sender's beat counts 75 s; with companion 1.8.1 B shows ● – the reported fault), new `t_distrib.py` (A in Node: 11 variants and a sentence without; B in the dashboard: "!K7" with "Distributed By", label → release distributed, only suggested); harness `WS_FAIL` (`{'release': n}`: the next n lookups of the release answer 503). Golden file written anew: only T028 added (sections `lists` and `tables`).


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

The mapping register in one section (collect item 4, step 1).

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
