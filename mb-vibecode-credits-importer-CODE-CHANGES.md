# MB x Vibecode – Code changes

What changed **in the code** with each version of both scripts, newest first. It is meant for whoever works on the scripts (the maintainer, or the AI that writes them): which parts, functions, stored data, texts and tests a version touched. What a version means **for users** is in the [changelog](mb-vibecode-credits-importer-CHANGELOG.md).

- **Import** = MB x Vibecode: Credits Importer (`mb-vibecode-credits-importer.user.js`; until 3.3.0 `mb-discogs-credits-import.user.js`)
- **Companion** = MB x Vibecode: Credits Importer Companion (`mb-vibecode-credits-importer-companion.user.js`; until 1.6.0 `mb-discogs-credits-sync.user.js`)

## How this file is kept

From 3.5.0 on, every change to the code comes as a pull request that also adds an entry here, at the top: the version, then what changed in the code – parts and functions (new, changed, removed), state (`S`), browser storage, texts (i18n keys), rules of the register, CSS, event handlers, edit note, tests – and anything to watch out for. Functions are named as in the code, so they can be found with a search.

How far back the entries go:

| Versions | Source | Detail |
|---|---|---|
| Import 3.0.0 – 3.34.28, Companion 1.6.0 – 1.9.1 | the working sessions | written by hand, per version |
| Import 2.17.0 – 2.19.1 | the working session, and a comparison of the code of 2.16.0 and 2.19.1 | short notes for 2.19.x, otherwise the comparison |
| Import 0.9.2 – 2.16.0, Companion 0.2.2 – 1.5.0 | the versions uploaded to this repository (19 of the main script, 14 of the companion) | reconstructed: a comparison of the code from one upload to the next; versions in between are named, the changelog says what they do |
| Import 0.1.0 – 0.9.1, Companion 0.1.0 – 0.2.1 | none: the code of these versions was not kept | only the changelog |

**Texts (from 3.27.1):** a new text is added in English only (`tools/i18n_add.py` with `{"en": {…}}`); German, Spanish and French follow in a translation round every few versions – until then `tr()` shows the English text. `smoke/t_i18n.py` fails on a key the code names without an English text, on a left-over translation, on a placeholder English does not have and on a French plain space before ":", ";", "?", "!" (or inside « »), and reports what each language still lacks (`LIST=1` lists the keys). **From 3.34.0** German, Spanish and French are in `mb-vibecode-credits-importer-languages.json`; the tools write there.

The comparisons were made with a small script: functions and constants of the main level of the script are compared by their text (a "changed" function may have changed only in a comment), texts by their English keys, storage keys where the code reads, writes or lists them, rule ids where the register defines them.

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
