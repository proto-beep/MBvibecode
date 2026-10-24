# MB x Vibecode – Code changes

What changed **in the code** with each version of both scripts, newest first. It is meant for whoever works on the scripts (the maintainer, or the AI that writes them): which parts, functions, stored data, texts and tests a version touched. What a version means **for users** is in the [changelog](mb-vibecode-credits-importer-CHANGELOG.md).

- **Import** = MB x Vibecode: Credits Importer (`mb-vibecode-credits-importer.user.js`; until 3.3.0 `mb-discogs-credits-import.user.js`)
- **Companion** = MB x Vibecode: Credits Importer Companion (`mb-vibecode-credits-importer-companion.user.js`; until 1.6.0 `mb-discogs-credits-sync.user.js`)

## How this file is kept

From 3.5.0 on, every change to the code comes as a pull request that also adds an entry here, at the top: the version, then what changed in the code – parts and functions (new, changed, removed), state (`S`), browser storage, texts (i18n keys), rules of the register, CSS, event handlers, edit note, tests – and anything to watch out for. Functions are named as in the code, so they can be found with a search.

How far back the entries go:

| Versions | Source | Detail |
|---|---|---|
| Import 3.0.0 – 3.27.0, Companion 1.6.0 – 1.8.3 | the working sessions | written by hand, per version |
| Import 2.17.0 – 2.19.1 | the working session, and a comparison of the code of 2.16.0 and 2.19.1 | short notes for 2.19.x, otherwise the comparison |
| Import 0.9.2 – 2.16.0, Companion 0.2.2 – 1.5.0 | the versions uploaded to this repository (19 of the main script, 14 of the companion) | reconstructed: a comparison of the code from one upload to the next; versions in between are named, the changelog says what they do |
| Import 0.1.0 – 0.9.1, Companion 0.1.0 – 0.2.1 | none: the code of these versions was not kept | only the changelog |

The comparisons were made with a small script: functions and constants of the main level of the script are compared by their text (a "changed" function may have changed only in a comment), texts by their English keys, storage keys where the code reads, writes or lists them, rule ids where the register defines them.

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
