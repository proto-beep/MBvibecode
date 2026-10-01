// ==UserScript==
// @name         MB x Vibecode: Import Discogs credits
// @namespace    https://github.com/proto-beep/MBvibecode
// @version      0.9.2
// @date         2026-10-01
// @description  Import dashboard for the release relationship editor: review the credits of the linked Discogs release, match artists via their Discogs links, map roles, choose level and tracks, and stage them as relationships. Submitting ("Enter edit") is always left to you.
// @description:de Import-Dashboard im Release-Beziehungseditor: Credits des verknüpften Discogs-Releases prüfen, Artists über Discogs-Links zuordnen, Rollen, Ebene und Tracks wählen und als Beziehungen vormerken. Abschicken („Enter edit“) machst du selbst.
// @description:es Panel de importación en el editor de relaciones de la publicación: revisa los créditos de la publicación de Discogs enlazada, asigna artistas mediante sus enlaces de Discogs, elige roles, nivel y pistas y prepáralos como relaciones. El envío («Enter edit») siempre lo haces tú.
// @description:fr Tableau d'import dans l'éditeur de relations de la parution : vérifiez les crédits de la parution Discogs liée, associez les artistes via leurs liens Discogs, choisissez rôles, niveau et pistes et préparez-les comme relations. L'envoi (« Enter edit ») reste toujours à vous.
// @author       proto-beep
// @license      CC0-1.0
// @homepageURL  https://github.com/proto-beep/MBvibecode
// @supportURL   https://github.com/proto-beep/MBvibecode/issues
// @downloadURL  https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-discogs-credits-import.user.js
// @updateURL    https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-discogs-credits-import.user.js
// @match        *://musicbrainz.org/release/*/edit-relationships*
// @match        *://*.musicbrainz.org/release/*/edit-relationships*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

/* global GM_info, unsafeWindow, module */
(function () {
  'use strict';

  // ===========================================================================
  // 1. Basics
  // ===========================================================================

  const VERSION = (typeof GM_info !== 'undefined' && GM_info.script && GM_info.script.version) || '0.9.2';
  const EDIT_NOTE_SCRIPT_NAME = 'MB x Vibecode: Import Discogs credits';
  const SCRIPT_URL = 'https://github.com/proto-beep/MBvibecode';
  const MBID_RE = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
  const IS_NODE_TEST = typeof module !== 'undefined' && module.exports && typeof window === 'undefined';

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const norm = (s) => String(s == null ? '' : s).toLowerCase().replace(/\s+/g, ' ').trim();
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[c]);
  const uniq = (arr) => [...new Set(arr)];
  let idCounter = 0;
  const nextId = (prefix) => `${prefix}${++idCounter}`;
  const cleanDiscogsName = (name) => String(name || '').replace(/\s\(\d+\)$/, '').trim();
  const discogsArtistUrl = (id) => `https://www.discogs.com/artist/${id}`;
  const discogsLabelUrl = (id) => `https://www.discogs.com/label/${id}`;

  // ===========================================================================
  // 1b. Translations (dashboard UI; edit notes stay English)
  // ===========================================================================

  const LANGS = { en: 'English', de: 'Deutsch', es: 'Español', fr: 'Français' };

  let LANG = (() => {
    try {
      const stored = JSON.parse(window.localStorage.getItem('dci-lang'));
      return LANGS[stored] ? stored : 'en';
    } catch (e) {
      return 'en';
    }
  })();

  /* eslint-disable quote-props */
  const I18N = {
    en: {
      "title": "Import Discogs credits",
      "launcher.open": "Import Discogs credits …",
      "launcher.status.one": "{n} relationship from Discogs staged, not submitted yet.",
      "launcher.status.other": "{n} relationships from Discogs staged, not submitted yet.",
      "lang.label": "Language",
      "common.close": "Close",
      "common.cancel": "Cancel",
      "common.quoted": "“{text}”",
      "raw": "{text}",
      "source.current": "{title} (Discogs {id})",
      "source.none": "No Discogs release loaded yet",
      "source.pick": "Choose linked Discogs release …",
      "source.other": "Other Discogs release URL or ID",
      "source.load": "Load",
      "sync.off": "Discogs view: off",
      "sync.offTitle": "The companion script “MB x Vibecode: Import Discogs credits COMPANION” is not installed or not active.",
      "sync.noTab": "Discogs view: no Discogs tab",
      "sync.openTab": "open in background",
      "sync.connected": "Discogs view: connected ({where})",
      "sync.visible": "visible tab",
      "sync.background": "background tab",
      "sync.jumping": "jumping to the source …",
      "sync.found.credit": "credit highlighted",
      "sync.found.track": "track highlighted",
      "sync.found.artist": "artist highlighted",
      "sync.found.loading": "Discogs is loading the release …",
      "sync.found.none": "source not found on Discogs",
      "sync.found.no-tab": "no Discogs tab",
      "toolbar.levelAll": "Level for all rows:",
      "toolbar.onlyMissing": "Only show artists without an MB match",
      "toolbar.roleCredits": "Role credits:",
      "toolbar.artistCredits": "Artist credits:",
      "toolbar.asOnDiscogs": "as on Discogs",
      "toolbar.clearAll": "clear all",
      "level.recording": "Recording",
      "level.release": "Release",
      "level.work": "Work",
      "level.skip": "Skip",
      "th.role": "Discogs role",
      "th.type": "MB relationship",
      "th.attrs": "Attributes and credits",
      "th.level": "Level",
      "th.tracks": "Tracks and status",
      "th.track": "Track",
      "th.work": "Work",
      "th.action": "Action",
      "group.spelling": "Spelling on Discogs:",
      "group.noVariant": "No alternative spelling on Discogs",
      "group.creditAll": "Artist credit for all roles",
      "group.creditAllAria": "Artist credit for all roles of {name}",
      "group.setAll": "Set for all",
      "group.addRole": "+ Another role for {name}",
      "match.searching": "Looking up MB artist …",
      "match.linked": "found via Discogs link",
      "match.manual": "set manually",
      "match.created": "newly created",
      "match.change": "change",
      "match.changeLabel": "change MB artist",
      "match.placeholder": "MB artist URL or MBID",
      "match.inputAria": "MusicBrainz artist for {name}",
      "match.apply": "Apply",
      "match.search": "Search MB",
      "match.create": "Create artist …",
      "match.ambiguous": "several MB artists have this Discogs link",
      "match.pick": "Please choose …",
      "match.noLink": "no MB artist with this Discogs link",
      "match.noId": "no Discogs ID",
      "role.placeholder": "e.g. Keyboards",
      "role.aria": "Role",
      "role.remove": "Remove row",
      "role.source": "Discogs: {where}",
      "role.tracks": "track {list}",
      "role.wholeRelease": "Discogs: whole release",
      "role.unresolved": "Not matched: {list}",
      "note.uncredited": "According to Discogs not named on the release (Uncredited).",
      "note.featuring": "“Featuring” is usually part of the artist credit already. Please check.",
      "note.misc": "MusicBrainz has no specific relationship for this role. It is added as “miscellaneous support” with the Discogs role as task; set it to Skip if you do not want it.",
      "type.skipped": "not applied",
      "type.choose": "Choose type …",
      "type.aria": "MusicBrainz relationship type",
      "attr.optional": "{name} (optional)",
      "mark.known": "known",
      "mark.unknown": "unknown",
      "roleCredit.label": "Role credit",
      "roleCredit.placeholder": "none",
      "artistCredit.label": "Artist credit",
      "credit.placeholder": "empty = MB name",
      "dest.credit": "stored as credit for “{name}”",
      "dest.text": "stored in the attribute “{name}”",
      "dest.note": "no matching MB field, goes into the edit note only",
      "dest.none": "no matching MB field, not applied",
      "tracks.count.one": "{sel} of {n} track",
      "tracks.count.other": "{sel} of {n} tracks",
      "tracks.worksOf": "works of these tracks",
      "tracks.wholeRelease": "whole release",
      "picker.all": "All",
      "picker.none": "None",
      "picker.invert": "Invert",
      "picker.discogs": "Discogs suggestion",
      "picker.legend": "Numbers marked with {dot} come from Discogs.",
      "picker.medium": "Medium {n}",
      "picker.dpos": "Discogs position {pos}",
      "picker.noDpos": "no Discogs counterpart",
      "status.new.one": "{n} new",
      "status.new.other": "{n} new",
      "status.existing.one": "{n} already exists",
      "status.existing.other": "{n} already exist",
      "status.applied.one": "{n} staged",
      "status.applied.other": "{n} staged",
      "status.noWork.one": "{n} track without a work",
      "status.noWork.other": "{n} tracks without a work",
      "status.loose": "{n}× the type exists with other attributes",
      "status.nothing": "nothing new",
      "issue.searching": "looking up MB artist",
      "issue.missingArtist": "MB artist missing",
      "issue.chooseType": "choose a relationship type",
      "issue.noTracks": "no tracks selected",
      "issue.noWork": "the selected tracks have no work yet",
      "issue.unknownAttr": "{root} “{value}” unknown",
      "issue.requiredAttr": "required attribute “{name}” missing",
      "sum.new.one": "{n} new relationship",
      "sum.new.other": "{n} new relationships",
      "kind.recording": "{n} on recordings",
      "kind.release": "{n} on the release",
      "kind.work": "{n} on works",
      "kind.workLink.one": "{n} work link",
      "kind.workLink.other": "{n} work links",
      "sum.incomplete.one": "{n} row incomplete",
      "sum.incomplete.other": "{n} rows incomplete",
      "sum.existing.one": "{n} already on MB",
      "sum.existing.other": "{n} already on MB",
      "footer.preview": "Preview all relationships",
      "footer.editNote": "Write source and summary to the edit note",
      "footer.apply": "Stage in the relationship editor",
      "footer.hint": "Nothing is submitted. You review the changes in the editor and click “Enter edit” yourself.",
      "panic.button.one": "Emergency: link only the new work",
      "panic.button.other": "Emergency: link only the {n} new works",
      "panic.title": "Discards all unsaved changes in the relationship editor and stages only the links to works created here.",
      "panic.confirm.one": "Emergency reset\n\nAll unsaved changes in the relationship editor will be discarded, including changes you made by hand, and the dashboard starts over.\nAfterwards only the link to the newly created work is staged again, so it does not stay unlinked.\n\nThe page will reload. Continue?",
      "panic.confirm.other": "Emergency reset\n\nAll unsaved changes in the relationship editor will be discarded, including changes you made by hand, and the dashboard starts over.\nAfterwards only the links to the {n} newly created works are staged again, so they do not stay unlinked.\n\nThe page will reload. Continue?",
      "panic.done.one": "Emergency reset done: {n} link to a newly created work is staged, everything else was reset. Submit it with “Enter edit” so the work does not stay unlinked.",
      "panic.done.other": "Emergency reset done: {n} links to newly created works are staged, everything else was reset. Submit them with “Enter edit” so the works do not stay unlinked.",
      "preview.empty": "No relationship ready yet.",
      "preview.release": "Release",
      "preview.work": "Work: {title}",
      "preview.linkWork": "Link work: {title}",
      "preview.attrCredit": "{name} as “{credit}”",
      "preview.artistCredit": "artist credit “{credit}”",
      "preview.noteOnly": "edit note only: “{text}”",
      "manual.title": "Add entry manually",
      "manual.artistAria": "MusicBrainz entry",
      "manual.rolePlaceholder": "MB relationship type or Discogs role, e.g. artwork or Guitar [Electric]",
      "manual.add": "Add",
      "works.title": "Works",
      "works.missing.one": "{n} track has no work yet.",
      "works.missing.other": "{n} tracks have no work yet.",
      "works.allDone": "Every track has a work or a staged link.",
      "works.explain": "Found or newly created works are linked to the recordings when you stage. Writing credits on level “Work” go onto these works.",
      "works.type": "Work type for new works",
      "works.lang": "Language",
      "works.none": "none",
      "works.searchAll": "Search works for all tracks without one",
      "works.createAll": "Create missing works one by one …",
      "works.linked": "linked",
      "works.plannedFound": "found, will be linked",
      "works.plannedCreated": "newly created, will be linked",
      "works.unplan": "Remove link",
      "works.noWork": "no work linked",
      "works.search": "Search",
      "works.create": "Create work …",
      "works.searching": "Searching …",
      "works.basisWriters": "Searched by title and {names}",
      "works.basisTitle": "Searched by title only (no writing credits matched)",
      "works.link": "Link",
      "works.noResults": "No matching works found.",
      "sub.window": "Open in separate window",
      "sub.frameTitle": "MusicBrainz form",
      "sub.blocked": "The form cannot be embedded here. Open it with “Open in separate window”.",
      "sub.popupBlocked": "The browser blocked the window.",
      "sub.popupOpen": "The form is open in its own window. After you submit it, the dashboard picks up the result.",
      "artistDlg.title": "Create artist: {name}",
      "artistDlg.prefilled": "Prefilled from Discogs: {list}.",
      "part.name": "name",
      "part.type": "type {type}",
      "type.group": "group",
      "type.person": "person",
      "part.urls.one": "{n} web link (including the Discogs link)",
      "part.urls.other": "{n} web links (including the Discogs link)",
      "part.members.one": "a “member of band” relationship to {names}",
      "part.members.other": "{n} “member of band” relationships to {names}",
      "artistDlg.notInMb": "Not in MusicBrainz and therefore not linked: {list}.",
      "artistDlg.loadFailed": "Discogs data not loaded: {msg}",
      "artistDlg.check": "Check the form and click “Enter edit” at the bottom yourself. The dashboard then picks up the new artist automatically. Web links without a detected type must be assigned in the form.",
      "artistDlg.done": "Artist “{name}” has been created and is assigned in the dashboard.",
      "workDlg.title": "Create work: {title}",
      "workDlg.prefilled": "Prefilled: {list}.",
      "part.title": "title “{title}”",
      "part.workType": "work type {name}",
      "part.language": "language {name}",
      "workDlg.noWriters": "No writing credits for this track in the dashboard. You can add them in the form or later on level “Work”.",
      "workDlg.after": "After you submit, the new work is linked with track {track} (staged, not submitted).",
      "workDlg.done": "Work “{title}” has been created. The link with track {track} is staged.",
      "busy.mb": "Loading tracks and existing relationships from MusicBrainz …",
      "busy.discogs": "Loading Discogs release {id} …",
      "busy.artists": "Looking up MB artists via their Discogs links …",
      "busy.discogsArtist": "Loading Discogs data for {name} …",
      "busy.apply.one": "Staging {n} relationship in the editor …",
      "busy.apply.other": "Staging {n} relationships in the editor …",
      "msg.noDiscogsLink": "This release is not linked to Discogs yet. Enter a Discogs release URL above.",
      "msg.multiLinks": "This release is linked to {n} Discogs releases. Choose one above.",
      "msg.trackMismatch": "Discogs lists {d} tracks, MusicBrainz {m}. Tracks are matched in order. Check the track selection of recording and work relationships.",
      "msg.noCredits": "Discogs has no credits for this release. You can add entries manually below.",
      "msg.confirmDiscard": "The current selection in the dashboard will be discarded. Continue?",
      "msg.badDiscogsId": "No Discogs release ID recognized. Example: https://www.discogs.com/release/1234567",
      "msg.badMbid": "No MBID recognized. Paste the URL of an MB artist page or an MBID.",
      "msg.notArtist": "This MBID does not belong to an artist.",
      "msg.editorNotReady": "The relationship editor is not ready yet. Wait until the page has fully loaded and try again.",
      "msg.applied.one": "{n} relationship is staged in the editor but not submitted. Check it in the editor and click “Enter edit” yourself.",
      "msg.applied.other": "{n} relationships are staged in the editor but not submitted. Check them in the editor and click “Enter edit” yourself.",
      "msg.notLoaded.one": "{n} relationship skipped because medium {media} is not loaded in the editor yet. Expand the medium in the editor and stage again; anything already staged is left out.",
      "msg.notLoaded.other": "{n} relationships skipped because medium {media} is not loaded in the editor yet. Expand the medium in the editor and stage again; anything already staged is left out.",
      "msg.errors.one": "Error with {n} relationship: {list}",
      "msg.errors.other": "Errors with {n} relationships: {list}",
      "msg.noteMissing": "The edit note field was not found. Please add the Discogs source yourself.",
      "msg.pendingWorks.one": "{n} work created here earlier is not linked to its recording in MusicBrainz yet. Its link is staged in the dashboard again.",
      "msg.pendingWorks.other": "{n} works created here earlier are not linked to their recordings in MusicBrainz yet. Their links are staged in the dashboard again.",
      "msg.toEditor": "To the editor",
      "err.mbHttp": "The MusicBrainz API responded with HTTP {status}.",
      "err.mbBusy": "The MusicBrainz API is busy (HTTP 503). Please try again shortly.",
      "err.entity": "Entry {mbid} not found (HTTP {status}).",
      "err.discogsLimit": "Discogs rate limit reached. Please wait a minute and try again.",
      "err.discogsMissing": "Discogs release {id} does not exist.",
      "err.discogsHttp": "The Discogs API responded with HTTP {status}.",
      "err.typesMissing": "MusicBrainz relationship types are not loaded yet. Wait until the editor is fully built and open the dashboard again.",
      "err.releaseMissing": "The release was not found via the MusicBrainz API.",
      "err.treeMissing": "MB.tree is not available, so attributes cannot be set.",
      "log.title": "Log",
      "log.copy": "Copy",
      "log.copied": "Copied",
      "log.clear": "Clear",
      "log.hide": "Hide",
      "log.start": "Dashboard opened for release {mbid}",
      "log.mbLoaded.one": "MusicBrainz loaded: {n} track ({works} with a work), Discogs links: {links}",
      "log.mbLoaded.other": "MusicBrainz loaded: {n} tracks ({works} with a work), Discogs links: {links}",
      "log.trackMismatch": "Track count differs: Discogs {d}, MusicBrainz {m}",
      "log.discogsLoaded.one": "Discogs release {id} loaded: {artists} artists, {n} role",
      "log.discogsLoaded.other": "Discogs release {id} loaded: {artists} artists, {n} roles",
      "log.artistLinked": "{name}: found via Discogs link → {mb}",
      "log.artistAmbiguous": "{name}: {n} MB artists share the Discogs link",
      "log.artistMissing": "{name}: no MB artist with this Discogs link",
      "log.artistManual": "{name}: set manually → {mb}",
      "log.artistForm": "Create-artist form opened: {name}",
      "log.artistCreated": "Artist created: {name} ({mbid})",
      "log.manualAdded": "Manual entry added: {name}, {role}",
      "log.formCancelled": "Form closed without creating anything",
      "log.workForm": "Create-work form opened for track {track}",
      "log.workCreated": "Work created for track {track}: {title} ({mbid})",
      "log.workSearch.one": "Work search for track {track}: {n} result",
      "log.workSearch.other": "Work search for track {track}: {n} results",
      "log.workPicked": "Track {track}: work “{title}” chosen for linking",
      "log.workUnplanned": "Track {track}: planned work link removed",
      "log.applyStart.one": "Staging {n} relationship in the editor …",
      "log.applyStart.other": "Staging {n} relationships in the editor …",
      "log.staged": "Staged: {text}",
      "log.skippedNotLoaded": "Skipped, medium not loaded: {text}",
      "log.error": "Error: {text}",
      "log.noteWritten": "Edit note updated",
      "log.noteMissing": "Edit note field not found",
      "log.editorNotReady": "Relationship editor not ready",
      "log.pendingWorks.one": "{n} created work not linked yet; its link is staged in the dashboard again",
      "log.pendingWorks.other": "{n} created works not linked yet; their links are staged in the dashboard again",
      "log.panic.one": "Emergency reset requested: the page reloads and keeps {n} work link",
      "log.panic.other": "Emergency reset requested: the page reloads and keeps {n} work links",
      "log.panicDone.one": "Emergency reset: {n} link to a newly created work staged",
      "log.panicDone.other": "Emergency reset: {n} links to newly created works staged",
      "log.discogsJump": "Discogs view: {result}",
      "syncMode.label": "Discogs view – jump to the source:",
      "syncMode.hover": "on mouse-over",
      "syncMode.click": "on click",
      "log.syncMode": "Discogs view follows the dashboard {mode}",
      "companies.title": "Companies, etc.",
      "companies.explain": "Labels, studios and plants from Discogs. They are matched to MB labels or places via their Discogs links. Discogs lists persons here as labels too: paste an MB artist to link one as a person.",
      "entity.artist": "artist",
      "entity.label": "label",
      "entity.place": "place",
      "role.asEntity": "as MB {type}",
      "role.companyWhole": "Discogs: Companies, etc. (whole release)",
      "role.catno": "Catalog number on Discogs: {catno}",
      "role.companyPlaceholder": "e.g. Pressed By",
      "credit.companyLabel": "Credited as",
      "issue.missingCompany": "MB label, place or artist missing",
      "match.noLinkCompany": "no MB label, place or artist with this Discogs link",
      "match.placeholderCompany": "URL or MBID of an MB label, place or artist",
      "match.createLabel": "Create label …",
      "match.createPlace": "Create place …",
      "msg.notCompany": "This MBID is not an artist, and not a label or place that fits these roles.",
      "companyDlg.titleLabel": "Create label: {name}",
      "companyDlg.titlePlace": "Create place: {name}",
      "companyDlg.prefilled": "Prefilled from Discogs: name and Discogs link.",
      "companyDlg.checkLabel": "Check the form, add type and area if you know them, and click “Enter edit” at the bottom yourself. The dashboard then picks up the new label automatically.",
      "companyDlg.checkPlace": "Check the form, add the place type (e.g. studio) and the area, and click “Enter edit” at the bottom yourself. The dashboard then picks up the new place automatically.",
      "companyDlg.done": "“{name}” has been created and is assigned in the dashboard.",
      "log.companyForm": "Create form opened ({type}): {name}",
      "log.companyCreated": "Created: {name} ({mbid})",
      "date.title": "Date pool",
      "date.used.one": "{n} row",
      "date.used.other": "{n} rows",
      "date.suggestions": "Suggestions:",
      "date.sugg.copyright": "℗/© year in the Discogs notes {date}",
      "date.formTitle": "Edit date",
      "date.begin": "Begin date",
      "date.end": "End date",
      "date.save": "Save",
      "date.remove": "Delete",
      "date.formHint": "As in MusicBrainz: year, month and day in separate fields; month and day can stay empty. For a single day or year (e.g. ℗ 1998), enter the same begin and end date (⇣ copies it). You can also paste a date as MusicBrainz shows it, e.g. “from 2015-01-26 until 2015-01-27”, “in 2015-01” or “on 2015-01-26”.",
      "date.errBegin": "The begin date is not valid.",
      "date.errEnd": "The end date is not valid.",
      "date.errOrder": "The end date is before the begin date.",
      "date.notAllowed": "this type has no dates",
      "date.untitled": "Date",
      "preview.date": "date {date}",
      "log.dateSaved": "Date saved: {date}",
      "log.dateRemoved": "Date deleted: {date}",
      "match.searchArtist": "Search artists",
      "th.date": "Date",
      "date.poolNew": "+ New date",
      "date.poolExplain": "Save dates here once and reuse them: pick one in a row, click one to stamp it onto rows, or apply it to all rows with one relationship type.",
      "date.editEntry": "Edit or delete",
      "date.stampTitle": "Use as stamp: then click the date field of a row",
      "date.ended": "This relationship has ended",
      "date.name": "Name",
      "date.namePlaceholder": "optional, e.g. Session 2",
      "date.copyTitle": "Copy begin date to end date",
      "date.addRow": "+ Date",
      "date.fromPool": "from pool …",
      "date.toPool": "save to pool",
      "date.clear": "remove date",
      "date.fromPoolName": "from pool: {name}",
      "date.endedOnly": "ended, no date",
      "date.errEmpty": "Enter at least a year.",
      "date.stampActive": "Stamp: {date}. Click the date field of a row to apply it.",
      "date.stampAllType": "or apply to",
      "date.stampAllEmpty": "all rows without a date",
      "date.stampApply": "Apply",
      "date.stampEnd": "End stamp",
      "date.updateRows.one": "{n} row uses this date. Change it too?",
      "date.updateRows.other": "{n} rows use this date. Change them too?",
      "issue.badDate": "date not valid",
      "log.dateStamp": "Stamp selected: {date}",
      "log.dateApplied.one": "Date {date} set in {n} row",
      "log.dateApplied.other": "Date {date} set in {n} rows",
      "log.datesVerified.one": "Checked in the editor: the date of {n} relationship arrived",
      "log.datesVerified.other": "Checked in the editor: the dates of all {n} relationships arrived",
      "log.datesMismatch.one": "In the editor {n} relationship has a different date: {list}",
      "log.datesMismatch.other": "In the editor {n} relationships have a different date: {list}",
      "log.datesUnverifiable": "The dates could not be checked in the editor",
      "msg.datesMismatch.one": "{n} relationship in the editor does not have the date from the dashboard: {list}. Please check it in the editor.",
      "msg.datesMismatch.other": "{n} relationships in the editor do not have the date from the dashboard: {list}. Please check them in the editor.",
      "zoom.label": "Text size",
      "zoom.smaller": "Smaller text",
      "zoom.larger": "Larger text",
      "window.reset": "Reset position and size of the dashboard and the log",
      "status.skippedExisting": "already on MusicBrainz – set to Skip",
      "legend.exists": "already on MusicBrainz",
      "legend.existsSome": "partly on MusicBrainz",
      "log.existingSkipped.one": "{n} row is already on MusicBrainz and was set to Skip: {list}",
      "log.existingSkipped.other": "{n} rows are already on MusicBrainz and were set to Skip: {list}",
      "manual.hint": "Add any MusicBrainz entry that can be related to this release, its recordings or works: artist, label, place, area, event, series, recording, release, work and more. The kind of entry is recognized from the URL or MBID. The role list shows all MB relationship types for that kind; for artists, a role as Discogs writes it (e.g. Guitar [Electric]) works too.",
      "manual.entityPlaceholder": "URL or MBID of any MusicBrainz entry",
      "manual.search": "Search MB:",
      "msg.badMbidAny": "No MBID recognized. Paste the URL of an MB artist, label or place page, or an MBID.",
      "note.unknownRole": "Not an instrument known to MusicBrainz. Added as “miscellaneous support” with the Discogs role as task; choose a better type if there is one.",
      "date.pasteTitle": "You can paste a date as MusicBrainz shows it, e.g. “from 2015-01-26 until 2015-01-27”, “in 2015-01” or “on 2015-01-26”.",
      "log.datePasted": "Date pasted: {date}",
      "log.dashboard": "Dashboard",
      "log.dashboardTitle": "Open the dashboard or bring it back into view",
      "entity.area": "area",
      "entity.event": "event",
      "entity.series": "series",
      "entity.recording": "recording",
      "entity.release": "release",
      "entity.work": "work",
      "entity.release_group": "release group",
      "entity.instrument": "instrument",
      "entity.genre": "genre",
      "others.title": "Other entries",
      "others.explain": "Areas, events, series, recordings, releases, works and other MusicBrainz entries you added by hand.",
      "msg.urlNotHere": "URLs are not added here; use “External links” in the release editor.",
      "msg.noRelTypes": "MusicBrainz has no relationship type between the entity type “{type}” and a release, recording or work.",
      "msg.wrongEntityType": "This MBID is not of the type “{type}”.",
      "match.placeholderOther": "URL or MBID of an MB {type}",
      "dir.label": "Direction",
      "dir.release": "this release",
      "dir.recording": "each selected recording",
      "dir.work": "each work of the selected tracks",
    },
    de: {
      "title": "Discogs-Credits importieren",
      "launcher.open": "Discogs-Credits importieren …",
      "launcher.status.one": "{n} Beziehung aus Discogs vorgemerkt, noch nicht abgeschickt.",
      "launcher.status.other": "{n} Beziehungen aus Discogs vorgemerkt, noch nicht abgeschickt.",
      "lang.label": "Sprache",
      "common.close": "Schließen",
      "common.cancel": "Abbrechen",
      "common.quoted": "„{text}“",
      "raw": "{text}",
      "source.current": "{title} (Discogs {id})",
      "source.none": "Noch kein Discogs-Release geladen",
      "source.pick": "Verknüpftes Discogs-Release wählen …",
      "source.other": "Andere Discogs-Release-URL oder ID",
      "source.load": "Laden",
      "sync.off": "Discogs-Ansicht: aus",
      "sync.offTitle": "Das Zusatzscript „MB x Vibecode: Import Discogs credits COMPANION“ ist nicht installiert oder nicht aktiv.",
      "sync.noTab": "Discogs-Ansicht: kein Discogs-Tab",
      "sync.openTab": "im Hintergrund öffnen",
      "sync.connected": "Discogs-Ansicht: verbunden ({where})",
      "sync.visible": "sichtbarer Tab",
      "sync.background": "Tab im Hintergrund",
      "sync.jumping": "springe zur Stelle …",
      "sync.found.credit": "Stelle markiert",
      "sync.found.track": "Track markiert",
      "sync.found.artist": "Artist markiert",
      "sync.found.loading": "Discogs lädt das Release …",
      "sync.found.none": "Stelle auf Discogs nicht gefunden",
      "sync.found.no-tab": "kein Discogs-Tab",
      "toolbar.levelAll": "Ebene für alle Zeilen:",
      "toolbar.onlyMissing": "Nur Artists ohne MB-Zuordnung zeigen",
      "toolbar.roleCredits": "Rollen-Credits:",
      "toolbar.artistCredits": "Artist-Credits:",
      "toolbar.asOnDiscogs": "wie auf Discogs",
      "toolbar.clearAll": "alle leeren",
      "level.recording": "Recording",
      "level.release": "Release",
      "level.work": "Werk",
      "level.skip": "Überspringen",
      "th.role": "Discogs-Rolle",
      "th.type": "MB-Beziehung",
      "th.attrs": "Attribute und Credits",
      "th.level": "Ebene",
      "th.tracks": "Tracks und Status",
      "th.track": "Track",
      "th.work": "Werk",
      "th.action": "Aktion",
      "group.spelling": "Schreibweise auf Discogs:",
      "group.noVariant": "Auf Discogs ohne abweichende Schreibweise",
      "group.creditAll": "Artist-Credit für alle Rollen",
      "group.creditAllAria": "Artist-Credit für alle Rollen von {name}",
      "group.setAll": "Für alle setzen",
      "group.addRole": "+ Weitere Rolle für {name}",
      "match.searching": "Suche MB-Artist …",
      "match.linked": "über Discogs-Link gefunden",
      "match.manual": "manuell gesetzt",
      "match.created": "neu angelegt",
      "match.change": "ändern",
      "match.changeLabel": "MB-Artist ändern",
      "match.placeholder": "MB-Artist-URL oder MBID",
      "match.inputAria": "MusicBrainz-Artist für {name}",
      "match.apply": "Übernehmen",
      "match.search": "Auf MB suchen",
      "match.create": "Artist anlegen …",
      "match.ambiguous": "mehrere MB-Artists mit diesem Discogs-Link",
      "match.pick": "Bitte wählen …",
      "match.noLink": "kein MB-Artist mit diesem Discogs-Link",
      "match.noId": "ohne Discogs-ID",
      "role.placeholder": "z. B. Keyboards",
      "role.aria": "Rolle",
      "role.remove": "Zeile entfernen",
      "role.source": "Discogs: {where}",
      "role.tracks": "Track {list}",
      "role.wholeRelease": "Discogs: ganzes Release",
      "role.unresolved": "Nicht zuordenbar: {list}",
      "note.uncredited": "Laut Discogs auf dem Release nicht genannt (Uncredited).",
      "note.featuring": "„Featuring“ steht meist schon in der Artist-Credit. Bitte prüfen.",
      "note.misc": "Für diese Rolle hat MusicBrainz keine eigene Beziehung. Sie wird als „miscellaneous support“ mit der Discogs-Rolle als Aufgabe übernommen; stell sie auf Überspringen, wenn du sie nicht willst.",
      "type.skipped": "wird nicht übernommen",
      "type.choose": "Typ wählen …",
      "type.aria": "MusicBrainz-Beziehungstyp",
      "attr.optional": "{name} (optional)",
      "mark.known": "bekannt",
      "mark.unknown": "unbekannt",
      "roleCredit.label": "Rollen-Credit",
      "roleCredit.placeholder": "keiner",
      "artistCredit.label": "Artist-Credit",
      "credit.placeholder": "leer = MB-Name",
      "dest.credit": "wird als Credit für „{name}“ gespeichert",
      "dest.text": "wird im Attribut „{name}“ gespeichert",
      "dest.note": "kein passendes MB-Feld, landet nur in der Edit-Notiz",
      "dest.none": "kein passendes MB-Feld, wird nicht übernommen",
      "tracks.count.one": "{sel} von {n} Track",
      "tracks.count.other": "{sel} von {n} Tracks",
      "tracks.worksOf": "Werke dieser Tracks",
      "tracks.wholeRelease": "ganzes Release",
      "picker.all": "Alle",
      "picker.none": "Keine",
      "picker.invert": "Umkehren",
      "picker.discogs": "Discogs-Vorschlag",
      "picker.legend": "Mit {dot} markierte Nummern stammen aus der Discogs-Angabe.",
      "picker.medium": "Medium {n}",
      "picker.dpos": "Discogs-Position {pos}",
      "picker.noDpos": "keine Discogs-Entsprechung",
      "status.new.one": "{n} neu",
      "status.new.other": "{n} neu",
      "status.existing.one": "{n} schon vorhanden",
      "status.existing.other": "{n} schon vorhanden",
      "status.applied.one": "{n} übernommen",
      "status.applied.other": "{n} übernommen",
      "status.noWork.one": "{n} Track ohne Werk",
      "status.noWork.other": "{n} Tracks ohne Werk",
      "status.loose": "{n}× gibt es den Typ schon mit anderen Attributen",
      "status.nothing": "nichts Neues",
      "issue.searching": "MB-Artist wird gesucht",
      "issue.missingArtist": "MB-Artist fehlt",
      "issue.chooseType": "Beziehungstyp wählen",
      "issue.noTracks": "keine Tracks gewählt",
      "issue.noWork": "die gewählten Tracks haben noch kein Werk",
      "issue.unknownAttr": "{root} „{value}“ unbekannt",
      "issue.requiredAttr": "Pflichtattribut „{name}“ fehlt",
      "sum.new.one": "{n} neue Beziehung",
      "sum.new.other": "{n} neue Beziehungen",
      "kind.recording": "{n} auf Recordings",
      "kind.release": "{n} auf dem Release",
      "kind.work": "{n} auf Werken",
      "kind.workLink.one": "{n} Werkverknüpfung",
      "kind.workLink.other": "{n} Werkverknüpfungen",
      "sum.incomplete.one": "{n} Zeile unvollständig",
      "sum.incomplete.other": "{n} Zeilen unvollständig",
      "sum.existing.one": "{n} schon auf MB vorhanden",
      "sum.existing.other": "{n} schon auf MB vorhanden",
      "footer.preview": "Vorschau aller Beziehungen",
      "footer.editNote": "Quelle und Zusammenfassung in die Edit-Notiz schreiben",
      "footer.apply": "In den Beziehungseditor übernehmen",
      "footer.hint": "Es wird nichts abgeschickt. Du prüfst die Änderungen im Editor und klickst selbst auf „Enter edit“.",
      "panic.button.one": "Notfall: nur das neue Werk verknüpfen",
      "panic.button.other": "Notfall: nur die {n} neuen Werke verknüpfen",
      "panic.title": "Verwirft alle ungespeicherten Änderungen im Beziehungseditor und merkt nur die Verknüpfungen zu hier angelegten Werken wieder vor.",
      "panic.confirm.one": "Notfall-Reset\n\nAlle ungespeicherten Änderungen im Beziehungseditor werden verworfen, auch die, die du von Hand gemacht hast, und das Dashboard beginnt neu.\nDanach wird nur die Verknüpfung zum neu angelegten Werk wieder vorgemerkt, damit es nicht unverknüpft bleibt.\n\nDie Seite wird neu geladen. Fortfahren?",
      "panic.confirm.other": "Notfall-Reset\n\nAlle ungespeicherten Änderungen im Beziehungseditor werden verworfen, auch die, die du von Hand gemacht hast, und das Dashboard beginnt neu.\nDanach werden nur die Verknüpfungen zu den {n} neu angelegten Werken wieder vorgemerkt, damit sie nicht unverknüpft bleiben.\n\nDie Seite wird neu geladen. Fortfahren?",
      "panic.done.one": "Notfall-Reset erledigt: {n} Verknüpfung zu einem neu angelegten Werk ist vorgemerkt, alles andere wurde zurückgesetzt. Schick sie mit „Enter edit“ ab, damit das Werk nicht unverknüpft bleibt.",
      "panic.done.other": "Notfall-Reset erledigt: {n} Verknüpfungen zu neu angelegten Werken sind vorgemerkt, alles andere wurde zurückgesetzt. Schick sie mit „Enter edit“ ab, damit die Werke nicht unverknüpft bleiben.",
      "preview.empty": "Noch keine Beziehung bereit.",
      "preview.release": "Release",
      "preview.work": "Werk: {title}",
      "preview.linkWork": "Werk verknüpfen: {title}",
      "preview.attrCredit": "{name} als „{credit}“",
      "preview.artistCredit": "Artist-Credit „{credit}“",
      "preview.noteOnly": "nur Edit-Notiz: „{text}“",
      "manual.title": "Eintrag manuell hinzufügen",
      "manual.artistAria": "MusicBrainz-Eintrag",
      "manual.rolePlaceholder": "MB-Beziehungstyp oder Discogs-Rolle, z. B. artwork oder Guitar [Electric]",
      "manual.add": "Hinzufügen",
      "works.title": "Werke",
      "works.missing.one": "{n} Track hat noch kein Werk.",
      "works.missing.other": "{n} Tracks haben noch kein Werk.",
      "works.allDone": "Alle Tracks haben ein Werk oder eine vorgemerkte Verknüpfung.",
      "works.explain": "Gefundene oder neu angelegte Werke werden beim Übernehmen mit den Recordings verknüpft. Schreib-Credits auf Ebene „Werk“ landen auf diesen Werken.",
      "works.type": "Werkart für neue Werke",
      "works.lang": "Sprache",
      "works.none": "keine",
      "works.searchAll": "Werke für alle Tracks ohne Werk suchen",
      "works.createAll": "Fehlende Werke nacheinander anlegen …",
      "works.linked": "verknüpft",
      "works.plannedFound": "gefunden, wird verknüpft",
      "works.plannedCreated": "neu angelegt, wird verknüpft",
      "works.unplan": "Verknüpfung entfernen",
      "works.noWork": "kein Werk verknüpft",
      "works.search": "Suchen",
      "works.create": "Werk anlegen …",
      "works.searching": "Suche läuft …",
      "works.basisWriters": "Gesucht nach Titel und {names}",
      "works.basisTitle": "Gesucht nur nach Titel (keine Schreib-Credits zugeordnet)",
      "works.link": "Verknüpfen",
      "works.noResults": "Keine passenden Werke gefunden.",
      "sub.window": "In eigenem Fenster öffnen",
      "sub.frameTitle": "MusicBrainz-Formular",
      "sub.blocked": "Das Formular lässt sich hier nicht einbetten. Öffne es mit „In eigenem Fenster öffnen“.",
      "sub.popupBlocked": "Der Browser hat das Fenster blockiert.",
      "sub.popupOpen": "Das Formular ist im eigenen Fenster geöffnet. Nach dem Abschicken übernimmt das Dashboard das Ergebnis.",
      "artistDlg.title": "Artist anlegen: {name}",
      "artistDlg.prefilled": "Vorausgefüllt aus Discogs: {list}.",
      "part.name": "Name",
      "part.type": "Typ {type}",
      "type.group": "Gruppe",
      "type.person": "Person",
      "part.urls.one": "{n} Weblink (inklusive Discogs-Link)",
      "part.urls.other": "{n} Weblinks (inklusive Discogs-Link)",
      "part.members.one": "eine „member of band“-Beziehung zu {names}",
      "part.members.other": "{n} „member of band“-Beziehungen zu {names}",
      "artistDlg.notInMb": "Nicht in MusicBrainz und daher nicht verknüpft: {list}.",
      "artistDlg.loadFailed": "Discogs-Daten nicht geladen: {msg}",
      "artistDlg.check": "Prüfe das Formular und klicke unten selbst auf „Enter edit“. Das Dashboard übernimmt den neuen Artist danach automatisch. Weblinks ohne erkannten Typ musst du im Formular noch zuordnen.",
      "artistDlg.done": "Artist „{name}“ ist angelegt und im Dashboard zugeordnet.",
      "workDlg.title": "Werk anlegen: {title}",
      "workDlg.prefilled": "Vorausgefüllt: {list}.",
      "part.title": "Titel „{title}“",
      "part.workType": "Werkart {name}",
      "part.language": "Sprache {name}",
      "workDlg.noWriters": "Keine Schreib-Credits für diesen Track im Dashboard. Du kannst sie im Formular ergänzen oder später auf Ebene „Werk“ übernehmen.",
      "workDlg.after": "Nach dem Abschicken wird das neue Werk mit Track {track} verknüpft (vorgemerkt, nicht abgeschickt).",
      "workDlg.done": "Werk „{title}“ ist angelegt. Die Verknüpfung mit Track {track} ist vorgemerkt.",
      "busy.mb": "Lade Tracks und vorhandene Beziehungen von MusicBrainz …",
      "busy.discogs": "Lade Discogs-Release {id} …",
      "busy.artists": "Suche MB-Artists über ihre Discogs-Links …",
      "busy.discogsArtist": "Lade Discogs-Daten für {name} …",
      "busy.apply.one": "Übernehme {n} Beziehung in den Editor …",
      "busy.apply.other": "Übernehme {n} Beziehungen in den Editor …",
      "msg.noDiscogsLink": "Dieses Release ist noch nicht mit Discogs verknüpft. Gib oben eine Discogs-Release-URL ein.",
      "msg.multiLinks": "Dieses Release ist mit {n} Discogs-Releases verknüpft. Wähle oben eines aus.",
      "msg.trackMismatch": "Discogs listet {d} Tracks, MusicBrainz {m}. Die Zuordnung erfolgt der Reihe nach. Prüfe bei Recording- und Werk-Beziehungen die Trackauswahl.",
      "msg.noCredits": "Auf Discogs sind für dieses Release keine Credits eingetragen. Du kannst unten Einträge manuell anlegen.",
      "msg.confirmDiscard": "Die aktuelle Auswahl im Dashboard wird verworfen. Fortfahren?",
      "msg.badDiscogsId": "Keine Discogs-Release-ID erkannt. Beispiel: https://www.discogs.com/release/1234567",
      "msg.badMbid": "Keine MBID erkannt. Füge die URL einer MB-Artist-Seite oder die MBID ein.",
      "msg.notArtist": "Diese MBID gehört nicht zu einem Artist.",
      "msg.editorNotReady": "Der Beziehungseditor ist noch nicht bereit. Warte, bis die Seite vollständig geladen ist, und versuche es erneut.",
      "msg.applied.one": "{n} Beziehung ist im Editor vorgemerkt, aber noch nicht abgeschickt. Prüfe sie im Editor und klicke selbst auf „Enter edit“.",
      "msg.applied.other": "{n} Beziehungen sind im Editor vorgemerkt, aber noch nicht abgeschickt. Prüfe sie im Editor und klicke selbst auf „Enter edit“.",
      "msg.notLoaded.one": "{n} Beziehung übersprungen, weil Medium {media} im Editor noch nicht geladen ist. Klappe das Medium im Editor auf und übernimm erneut. Bereits Übernommenes wird dabei ausgelassen.",
      "msg.notLoaded.other": "{n} Beziehungen übersprungen, weil Medium {media} im Editor noch nicht geladen ist. Klappe das Medium im Editor auf und übernimm erneut. Bereits Übernommenes wird dabei ausgelassen.",
      "msg.errors.one": "Fehler bei {n} Beziehung: {list}",
      "msg.errors.other": "Fehler bei {n} Beziehungen: {list}",
      "msg.noteMissing": "Das Edit-Notiz-Feld wurde nicht gefunden. Bitte die Discogs-Quelle selbst eintragen.",
      "msg.pendingWorks.one": "{n} hier früher angelegtes Werk ist in MusicBrainz noch nicht mit seinem Recording verknüpft. Die Verknüpfung ist im Dashboard wieder vorgemerkt.",
      "msg.pendingWorks.other": "{n} hier früher angelegte Werke sind in MusicBrainz noch nicht mit ihren Recordings verknüpft. Die Verknüpfungen sind im Dashboard wieder vorgemerkt.",
      "msg.toEditor": "Zum Editor",
      "err.mbHttp": "Die MusicBrainz-API antwortet mit HTTP {status}.",
      "err.mbBusy": "Die MusicBrainz-API ist gerade ausgelastet (HTTP 503). Bitte gleich noch einmal versuchen.",
      "err.entity": "Eintrag {mbid} nicht gefunden (HTTP {status}).",
      "err.discogsLimit": "Discogs-Limit erreicht. Bitte eine Minute warten und erneut versuchen.",
      "err.discogsMissing": "Discogs-Release {id} existiert nicht.",
      "err.discogsHttp": "Die Discogs-API antwortet mit HTTP {status}.",
      "err.typesMissing": "Die Beziehungstypen von MusicBrainz sind noch nicht geladen. Warte, bis der Editor fertig aufgebaut ist, und öffne das Dashboard erneut.",
      "err.releaseMissing": "Das Release wurde über die MusicBrainz-API nicht gefunden.",
      "err.treeMissing": "MB.tree ist nicht verfügbar, Attribute können nicht gesetzt werden.",
      "log.title": "Protokoll",
      "log.copy": "Kopieren",
      "log.copied": "Kopiert",
      "log.clear": "Leeren",
      "log.hide": "Ausblenden",
      "log.start": "Dashboard geöffnet für Release {mbid}",
      "log.mbLoaded.one": "MusicBrainz geladen: {n} Track ({works} mit Werk), Discogs-Links: {links}",
      "log.mbLoaded.other": "MusicBrainz geladen: {n} Tracks ({works} mit Werk), Discogs-Links: {links}",
      "log.trackMismatch": "Trackzahl weicht ab: Discogs {d}, MusicBrainz {m}",
      "log.discogsLoaded.one": "Discogs-Release {id} geladen: {artists} Artists, {n} Rolle",
      "log.discogsLoaded.other": "Discogs-Release {id} geladen: {artists} Artists, {n} Rollen",
      "log.artistLinked": "{name}: über Discogs-Link gefunden → {mb}",
      "log.artistAmbiguous": "{name}: {n} MB-Artists teilen sich den Discogs-Link",
      "log.artistMissing": "{name}: kein MB-Artist mit diesem Discogs-Link",
      "log.artistManual": "{name}: manuell gesetzt → {mb}",
      "log.artistForm": "Formular „Artist anlegen“ geöffnet: {name}",
      "log.artistCreated": "Artist angelegt: {name} ({mbid})",
      "log.manualAdded": "Manueller Eintrag hinzugefügt: {name}, {role}",
      "log.formCancelled": "Formular ohne Anlegen geschlossen",
      "log.workForm": "Formular „Werk anlegen“ geöffnet für Track {track}",
      "log.workCreated": "Werk für Track {track} angelegt: {title} ({mbid})",
      "log.workSearch.one": "Werksuche für Track {track}: {n} Treffer",
      "log.workSearch.other": "Werksuche für Track {track}: {n} Treffer",
      "log.workPicked": "Track {track}: Werk „{title}“ zum Verknüpfen gewählt",
      "log.workUnplanned": "Track {track}: geplante Werkverknüpfung entfernt",
      "log.applyStart.one": "Übernehme {n} Beziehung in den Editor …",
      "log.applyStart.other": "Übernehme {n} Beziehungen in den Editor …",
      "log.staged": "Vorgemerkt: {text}",
      "log.skippedNotLoaded": "Übersprungen, Medium nicht geladen: {text}",
      "log.error": "Fehler: {text}",
      "log.noteWritten": "Edit-Notiz aktualisiert",
      "log.noteMissing": "Edit-Notiz-Feld nicht gefunden",
      "log.editorNotReady": "Beziehungseditor nicht bereit",
      "log.pendingWorks.one": "{n} angelegtes Werk noch nicht verknüpft; Verknüpfung im Dashboard wieder vorgemerkt",
      "log.pendingWorks.other": "{n} angelegte Werke noch nicht verknüpft; Verknüpfungen im Dashboard wieder vorgemerkt",
      "log.panic.one": "Notfall-Reset angefordert: Seite lädt neu, {n} Werkverknüpfung bleibt erhalten",
      "log.panic.other": "Notfall-Reset angefordert: Seite lädt neu, {n} Werkverknüpfungen bleiben erhalten",
      "log.panicDone.one": "Notfall-Reset: {n} Verknüpfung zu neu angelegtem Werk vorgemerkt",
      "log.panicDone.other": "Notfall-Reset: {n} Verknüpfungen zu neu angelegten Werken vorgemerkt",
      "log.discogsJump": "Discogs-Ansicht: {result}",
      "syncMode.label": "Discogs-Ansicht – zur Stelle springen:",
      "syncMode.hover": "beim Überfahren",
      "syncMode.click": "beim Klicken",
      "log.syncMode": "Discogs-Ansicht folgt dem Dashboard {mode}",
      "companies.title": "Companies, etc. (Firmen)",
      "companies.explain": "Labels, Studios und Presswerke aus Discogs. Sie werden über ihre Discogs-Links MB-Labels oder -Orten zugeordnet. Discogs führt hier auch Personen als Labels: Füge einen MB-Artist ein, um sie als Person zu verknüpfen.",
      "entity.artist": "Artist",
      "entity.label": "Label",
      "entity.place": "Ort",
      "role.asEntity": "als MB-{type}",
      "role.companyWhole": "Discogs: Companies, etc. (ganzes Release)",
      "role.catno": "Katalognummer auf Discogs: {catno}",
      "role.companyPlaceholder": "z. B. Pressed By",
      "credit.companyLabel": "Genannt als",
      "issue.missingCompany": "MB-Label, -Ort oder -Artist fehlt",
      "match.noLinkCompany": "kein MB-Label, -Ort oder -Artist mit diesem Discogs-Link",
      "match.placeholderCompany": "URL oder MBID eines MB-Labels, -Orts oder -Artists",
      "match.createLabel": "Label anlegen …",
      "match.createPlace": "Ort anlegen …",
      "msg.notCompany": "Diese MBID gehört weder zu einem Artist noch zu einem Label oder Ort, der zu diesen Rollen passt.",
      "companyDlg.titleLabel": "Label anlegen: {name}",
      "companyDlg.titlePlace": "Ort anlegen: {name}",
      "companyDlg.prefilled": "Vorausgefüllt aus Discogs: Name und Discogs-Link.",
      "companyDlg.checkLabel": "Prüfe das Formular, ergänze Typ und Gebiet, falls bekannt, und klicke unten selbst auf „Enter edit“. Das Dashboard übernimmt das neue Label danach automatisch.",
      "companyDlg.checkPlace": "Prüfe das Formular, ergänze die Art des Orts (z. B. Studio) und das Gebiet und klicke unten selbst auf „Enter edit“. Das Dashboard übernimmt den neuen Ort danach automatisch.",
      "companyDlg.done": "„{name}“ ist angelegt und im Dashboard zugeordnet.",
      "log.companyForm": "Anlegeformular geöffnet ({type}): {name}",
      "log.companyCreated": "Angelegt: {name} ({mbid})",
      "date.title": "Datums-Pool",
      "date.used.one": "{n} Zeile",
      "date.used.other": "{n} Zeilen",
      "date.suggestions": "Vorschläge:",
      "date.sugg.copyright": "℗/©-Jahr in den Discogs-Notizen {date}",
      "date.formTitle": "Datum bearbeiten",
      "date.begin": "Begin date",
      "date.end": "End date",
      "date.save": "Speichern",
      "date.remove": "Löschen",
      "date.formHint": "Wie in MusicBrainz: Jahr, Monat und Tag in eigenen Feldern; Monat und Tag dürfen leer bleiben. Für einen einzelnen Tag oder ein Jahr (z. B. ℗ 1998) Beginn und Ende gleich eintragen (⇣ kopiert). Du kannst ein Datum auch so einfügen, wie MusicBrainz es anzeigt, z. B. „from 2015-01-26 until 2015-01-27“, „in 2015-01“ oder „on 2015-01-26“.",
      "date.errBegin": "Das Anfangsdatum ist ungültig.",
      "date.errEnd": "Das Enddatum ist ungültig.",
      "date.errOrder": "Das Enddatum liegt vor dem Beginn.",
      "date.notAllowed": "dieser Typ hat keine Daten",
      "date.untitled": "Datum",
      "preview.date": "Datum {date}",
      "log.dateSaved": "Datum gespeichert: {date}",
      "log.dateRemoved": "Datum gelöscht: {date}",
      "match.searchArtist": "Artists suchen",
      "th.date": "Datum",
      "date.poolNew": "+ Neues Datum",
      "date.poolExplain": "Lege Daten hier einmal an und nutze sie wieder: in einer Zeile auswählen, per Klick als Stempel auf Zeilen setzen oder auf alle Zeilen mit einem Beziehungstyp anwenden.",
      "date.editEntry": "Bearbeiten oder löschen",
      "date.stampTitle": "Als Stempel verwenden: dann auf das Datumsfeld einer Zeile klicken",
      "date.ended": "Diese Beziehung ist beendet",
      "date.name": "Name",
      "date.namePlaceholder": "optional, z. B. Session 2",
      "date.copyTitle": "Beginn in das Ende kopieren",
      "date.addRow": "+ Datum",
      "date.fromPool": "aus dem Pool …",
      "date.toPool": "in den Pool",
      "date.clear": "Datum entfernen",
      "date.fromPoolName": "aus dem Pool: {name}",
      "date.endedOnly": "beendet, ohne Datum",
      "date.errEmpty": "Bitte mindestens ein Jahr eingeben.",
      "date.stampActive": "Stempel: {date}. Klicke auf das Datumsfeld einer Zeile, um es zu setzen.",
      "date.stampAllType": "oder anwenden auf",
      "date.stampAllEmpty": "alle Zeilen ohne Datum",
      "date.stampApply": "Anwenden",
      "date.stampEnd": "Stempel beenden",
      "date.updateRows.one": "{n} Zeile nutzt dieses Datum. Dort auch ändern?",
      "date.updateRows.other": "{n} Zeilen nutzen dieses Datum. Dort auch ändern?",
      "issue.badDate": "Datum ungültig",
      "log.dateStamp": "Stempel gewählt: {date}",
      "log.dateApplied.one": "Datum {date} in {n} Zeile gesetzt",
      "log.dateApplied.other": "Datum {date} in {n} Zeilen gesetzt",
      "log.datesVerified.one": "Im Editor geprüft: das Datum von {n} Beziehung ist angekommen",
      "log.datesVerified.other": "Im Editor geprüft: die Daten aller {n} Beziehungen sind angekommen",
      "log.datesMismatch.one": "Im Editor hat {n} Beziehung ein anderes Datum: {list}",
      "log.datesMismatch.other": "Im Editor haben {n} Beziehungen ein anderes Datum: {list}",
      "log.datesUnverifiable": "Die Daten konnten im Editor nicht geprüft werden",
      "msg.datesMismatch.one": "{n} Beziehung im Editor hat nicht das Datum aus dem Dashboard: {list}. Bitte im Editor prüfen.",
      "msg.datesMismatch.other": "{n} Beziehungen im Editor haben nicht das Datum aus dem Dashboard: {list}. Bitte im Editor prüfen.",
      "zoom.label": "Schriftgröße",
      "zoom.smaller": "Kleinere Schrift",
      "zoom.larger": "Größere Schrift",
      "window.reset": "Position und Größe von Dashboard und Protokoll zurücksetzen",
      "status.skippedExisting": "schon in MusicBrainz – auf Überspringen gestellt",
      "legend.exists": "schon in MusicBrainz",
      "legend.existsSome": "teilweise in MusicBrainz",
      "log.existingSkipped.one": "{n} Zeile ist schon in MusicBrainz und wurde auf Überspringen gestellt: {list}",
      "log.existingSkipped.other": "{n} Zeilen sind schon in MusicBrainz und wurden auf Überspringen gestellt: {list}",
      "manual.hint": "Füge jeden MusicBrainz-Eintrag hinzu, der mit diesem Release, seinen Recordings oder Werken verknüpft werden kann: Artist, Label, Ort, Gebiet, Event, Serie, Recording, Release, Werk und mehr. Die Art des Eintrags wird an URL oder MBID erkannt. Die Rollenliste zeigt alle MB-Beziehungstypen für diese Art; bei Artists geht auch eine Rolle wie bei Discogs (z. B. Guitar [Electric]).",
      "manual.entityPlaceholder": "URL oder MBID eines beliebigen MusicBrainz-Eintrags",
      "manual.search": "Auf MB suchen:",
      "msg.badMbidAny": "Keine MBID erkannt. Füge die URL einer MB-Seite eines Artists, Labels oder Orts oder eine MBID ein.",
      "note.unknownRole": "Kein Instrument, das MusicBrainz kennt. Übernommen als „miscellaneous support“ mit der Discogs-Rolle als Aufgabe; wähle einen besseren Typ, falls es einen gibt.",
      "date.pasteTitle": "Du kannst ein Datum so einfügen, wie MusicBrainz es anzeigt, z. B. „from 2015-01-26 until 2015-01-27“, „in 2015-01“ oder „on 2015-01-26“.",
      "log.datePasted": "Datum eingefügt: {date}",
      "log.dashboard": "Dashboard",
      "log.dashboardTitle": "Dashboard öffnen oder zurück ins Bild holen",
      "entity.area": "Gebiet",
      "entity.event": "Event",
      "entity.series": "Serie",
      "entity.recording": "Recording",
      "entity.release": "Release",
      "entity.work": "Werk",
      "entity.release_group": "Release-Gruppe",
      "entity.instrument": "Instrument",
      "entity.genre": "Genre",
      "others.title": "Weitere Einträge",
      "others.explain": "Gebiete, Events, Serien, Recordings, Releases, Werke und andere MusicBrainz-Einträge, die du von Hand hinzugefügt hast.",
      "msg.urlNotHere": "URLs werden hier nicht hinzugefügt; nutze „External links“ im Release-Editor.",
      "msg.noRelTypes": "MusicBrainz hat keinen Beziehungstyp zwischen der Art „{type}“ und einem Release, Recording oder Werk.",
      "msg.wrongEntityType": "Diese MBID gehört nicht zur Art „{type}“.",
      "match.placeholderOther": "URL oder MBID (MB-{type})",
      "dir.label": "Richtung",
      "dir.release": "dieses Release",
      "dir.recording": "jedes gewählte Recording",
      "dir.work": "jedes Werk der gewählten Tracks",
    },
    es: {
      "title": "Importar créditos de Discogs",
      "launcher.open": "Importar créditos de Discogs…",
      "launcher.status.one": "{n} relación de Discogs preparada, aún sin enviar.",
      "launcher.status.other": "{n} relaciones de Discogs preparadas, aún sin enviar.",
      "lang.label": "Idioma",
      "common.close": "Cerrar",
      "common.cancel": "Cancelar",
      "common.quoted": "«{text}»",
      "raw": "{text}",
      "source.current": "{title} (Discogs {id})",
      "source.none": "Aún no se ha cargado ninguna publicación de Discogs",
      "source.pick": "Elige la publicación de Discogs enlazada…",
      "source.other": "Otra URL o ID de publicación de Discogs",
      "source.load": "Cargar",
      "sync.off": "Vista de Discogs: desactivada",
      "sync.offTitle": "El script complementario «MB x Vibecode: Import Discogs credits COMPANION» no está instalado o no está activo.",
      "sync.noTab": "Vista de Discogs: ninguna pestaña de Discogs",
      "sync.openTab": "abrir en segundo plano",
      "sync.connected": "Vista de Discogs: conectada ({where})",
      "sync.visible": "pestaña visible",
      "sync.background": "pestaña en segundo plano",
      "sync.jumping": "saltando al origen…",
      "sync.found.credit": "crédito resaltado",
      "sync.found.track": "pista resaltada",
      "sync.found.artist": "artista resaltado",
      "sync.found.loading": "Discogs está cargando la publicación…",
      "sync.found.none": "origen no encontrado en Discogs",
      "sync.found.no-tab": "ninguna pestaña de Discogs",
      "toolbar.levelAll": "Nivel para todas las filas:",
      "toolbar.onlyMissing": "Mostrar solo artistas sin coincidencia en MB",
      "toolbar.roleCredits": "Créditos de rol:",
      "toolbar.artistCredits": "Créditos de artista:",
      "toolbar.asOnDiscogs": "como en Discogs",
      "toolbar.clearAll": "vaciar todos",
      "level.recording": "Grabación",
      "level.release": "Publicación",
      "level.work": "Obra",
      "level.skip": "Omitir",
      "th.role": "Rol en Discogs",
      "th.type": "Relación en MB",
      "th.attrs": "Atributos y créditos",
      "th.level": "Nivel",
      "th.tracks": "Pistas y estado",
      "th.track": "Pista",
      "th.work": "Obra",
      "th.action": "Acción",
      "group.spelling": "Grafía en Discogs:",
      "group.noVariant": "Sin grafía alternativa en Discogs",
      "group.creditAll": "Crédito de artista para todos los roles",
      "group.creditAllAria": "Crédito de artista para todos los roles de {name}",
      "group.setAll": "Aplicar a todos",
      "group.addRole": "+ Otro rol para {name}",
      "match.searching": "Buscando artista en MB…",
      "match.linked": "encontrado por enlace de Discogs",
      "match.manual": "asignado manualmente",
      "match.created": "recién creado",
      "match.change": "cambiar",
      "match.changeLabel": "cambiar artista de MB",
      "match.placeholder": "URL o MBID del artista en MB",
      "match.inputAria": "Artista de MusicBrainz para {name}",
      "match.apply": "Aplicar",
      "match.search": "Buscar en MB",
      "match.create": "Crear artista…",
      "match.ambiguous": "varios artistas de MB tienen este enlace de Discogs",
      "match.pick": "Elige…",
      "match.noLink": "ningún artista de MB con este enlace de Discogs",
      "match.noId": "sin ID de Discogs",
      "role.placeholder": "p. ej. Keyboards",
      "role.aria": "Rol",
      "role.remove": "Quitar fila",
      "role.source": "Discogs: {where}",
      "role.tracks": "pista {list}",
      "role.wholeRelease": "Discogs: toda la publicación",
      "role.unresolved": "Sin correspondencia: {list}",
      "note.uncredited": "Según Discogs, no aparece acreditado en la publicación (Uncredited).",
      "note.featuring": "«Featuring» suele estar ya en el crédito de artista. Compruébalo.",
      "note.misc": "MusicBrainz no tiene una relación específica para este rol. Se añade como «miscellaneous support» con el rol de Discogs como tarea; ponlo en Omitir si no lo quieres.",
      "type.skipped": "no se aplica",
      "type.choose": "Elige un tipo…",
      "type.aria": "Tipo de relación de MusicBrainz",
      "attr.optional": "{name} (opcional)",
      "mark.known": "conocido",
      "mark.unknown": "desconocido",
      "roleCredit.label": "Crédito de rol",
      "roleCredit.placeholder": "ninguno",
      "artistCredit.label": "Crédito de artista",
      "credit.placeholder": "vacío = nombre en MB",
      "dest.credit": "se guarda como crédito de «{name}»",
      "dest.text": "se guarda en el atributo «{name}»",
      "dest.note": "sin campo adecuado en MB, solo va a la nota de edición",
      "dest.none": "sin campo adecuado en MB, no se aplica",
      "tracks.count.one": "{sel} de {n} pista",
      "tracks.count.other": "{sel} de {n} pistas",
      "tracks.worksOf": "obras de estas pistas",
      "tracks.wholeRelease": "toda la publicación",
      "picker.all": "Todas",
      "picker.none": "Ninguna",
      "picker.invert": "Invertir",
      "picker.discogs": "Sugerencia de Discogs",
      "picker.legend": "Los números marcados con {dot} proceden de Discogs.",
      "picker.medium": "Medio {n}",
      "picker.dpos": "Posición en Discogs: {pos}",
      "picker.noDpos": "sin equivalente en Discogs",
      "status.new.one": "{n} nueva",
      "status.new.other": "{n} nuevas",
      "status.existing.one": "{n} ya existe",
      "status.existing.other": "{n} ya existen",
      "status.applied.one": "{n} preparada",
      "status.applied.other": "{n} preparadas",
      "status.noWork.one": "{n} pista sin obra",
      "status.noWork.other": "{n} pistas sin obra",
      "status.loose": "{n}× el tipo ya existe con otros atributos",
      "status.nothing": "nada nuevo",
      "issue.searching": "buscando artista de MB",
      "issue.missingArtist": "falta el artista de MB",
      "issue.chooseType": "elige un tipo de relación",
      "issue.noTracks": "ninguna pista seleccionada",
      "issue.noWork": "las pistas seleccionadas aún no tienen obra",
      "issue.unknownAttr": "{root} «{value}» desconocido",
      "issue.requiredAttr": "falta el atributo obligatorio «{name}»",
      "sum.new.one": "{n} relación nueva",
      "sum.new.other": "{n} relaciones nuevas",
      "kind.recording": "{n} en grabaciones",
      "kind.release": "{n} en la publicación",
      "kind.work": "{n} en obras",
      "kind.workLink.one": "{n} enlace de obra",
      "kind.workLink.other": "{n} enlaces de obra",
      "sum.incomplete.one": "{n} fila incompleta",
      "sum.incomplete.other": "{n} filas incompletas",
      "sum.existing.one": "{n} ya existe en MB",
      "sum.existing.other": "{n} ya existen en MB",
      "footer.preview": "Vista previa de todas las relaciones",
      "footer.editNote": "Escribir el origen y un resumen en la nota de edición",
      "footer.apply": "Preparar en el editor de relaciones",
      "footer.hint": "No se envía nada. Revisas los cambios en el editor y pulsas «Enter edit» tú mismo.",
      "panic.button.one": "Emergencia: enlazar solo la obra nueva",
      "panic.button.other": "Emergencia: enlazar solo las {n} obras nuevas",
      "panic.title": "Descarta todos los cambios no guardados del editor de relaciones y vuelve a preparar solo los enlaces a las obras creadas aquí.",
      "panic.confirm.one": "Reinicio de emergencia\n\nSe descartarán todos los cambios no guardados del editor de relaciones, también los que hiciste a mano, y el panel empezará de nuevo.\nDespués solo se volverá a preparar el enlace a la obra recién creada, para que no quede sin enlazar.\n\nLa página se recargará. ¿Continuar?",
      "panic.confirm.other": "Reinicio de emergencia\n\nSe descartarán todos los cambios no guardados del editor de relaciones, también los que hiciste a mano, y el panel empezará de nuevo.\nDespués solo se volverán a preparar los enlaces a las {n} obras recién creadas, para que no queden sin enlazar.\n\nLa página se recargará. ¿Continuar?",
      "panic.done.one": "Reinicio de emergencia completado: {n} enlace a una obra recién creada está preparado; todo lo demás se ha restablecido. Envíalo con «Enter edit» para que la obra no quede sin enlazar.",
      "panic.done.other": "Reinicio de emergencia completado: {n} enlaces a obras recién creadas están preparados; todo lo demás se ha restablecido. Envíalos con «Enter edit» para que las obras no queden sin enlazar.",
      "preview.empty": "Todavía no hay ninguna relación lista.",
      "preview.release": "Publicación",
      "preview.work": "Obra: {title}",
      "preview.linkWork": "Enlazar obra: {title}",
      "preview.attrCredit": "{name} como «{credit}»",
      "preview.artistCredit": "crédito de artista «{credit}»",
      "preview.noteOnly": "solo nota de edición: «{text}»",
      "manual.title": "Añadir entrada manualmente",
      "manual.artistAria": "Entrada de MusicBrainz",
      "manual.rolePlaceholder": "Tipo de relación de MB o rol de Discogs, p. ej. artwork o Guitar [Electric]",
      "manual.add": "Añadir",
      "works.title": "Obras",
      "works.missing.one": "{n} pista aún no tiene obra.",
      "works.missing.other": "{n} pistas aún no tienen obra.",
      "works.allDone": "Todas las pistas tienen una obra o un enlace preparado.",
      "works.explain": "Las obras encontradas o recién creadas se enlazan con las grabaciones al preparar. Los créditos de autoría en el nivel «Obra» van a estas obras.",
      "works.type": "Tipo para obras nuevas",
      "works.lang": "Idioma",
      "works.none": "ninguno",
      "works.searchAll": "Buscar obras para todas las pistas sin obra",
      "works.createAll": "Crear las obras que faltan una por una…",
      "works.linked": "enlazada",
      "works.plannedFound": "encontrada, se enlazará",
      "works.plannedCreated": "recién creada, se enlazará",
      "works.unplan": "Quitar enlace",
      "works.noWork": "ninguna obra enlazada",
      "works.search": "Buscar",
      "works.create": "Crear obra…",
      "works.searching": "Buscando…",
      "works.basisWriters": "Búsqueda por título y {names}",
      "works.basisTitle": "Búsqueda solo por título (sin créditos de autoría asignados)",
      "works.link": "Enlazar",
      "works.noResults": "No se encontraron obras adecuadas.",
      "sub.window": "Abrir en ventana aparte",
      "sub.frameTitle": "Formulario de MusicBrainz",
      "sub.blocked": "El formulario no se puede incrustar aquí. Ábrelo con «Abrir en ventana aparte».",
      "sub.popupBlocked": "El navegador bloqueó la ventana.",
      "sub.popupOpen": "El formulario está abierto en su propia ventana. Cuando lo envíes, el panel recogerá el resultado.",
      "artistDlg.title": "Crear artista: {name}",
      "artistDlg.prefilled": "Prerrellenado desde Discogs: {list}.",
      "part.name": "nombre",
      "part.type": "tipo {type}",
      "type.group": "grupo",
      "type.person": "persona",
      "part.urls.one": "{n} enlace web (incluido el enlace de Discogs)",
      "part.urls.other": "{n} enlaces web (incluido el enlace de Discogs)",
      "part.members.one": "una relación «member of band» con {names}",
      "part.members.other": "{n} relaciones «member of band» con {names}",
      "artistDlg.notInMb": "No están en MusicBrainz y por eso no se enlazan: {list}.",
      "artistDlg.loadFailed": "No se cargaron los datos de Discogs: {msg}",
      "artistDlg.check": "Revisa el formulario y pulsa tú mismo «Enter edit» abajo. Después, el panel recoge automáticamente el nuevo artista. Los enlaces web sin tipo detectado debes asignarlos en el formulario.",
      "artistDlg.done": "El artista «{name}» se ha creado y está asignado en el panel.",
      "workDlg.title": "Crear obra: {title}",
      "workDlg.prefilled": "Prerrellenado: {list}.",
      "part.title": "título «{title}»",
      "part.workType": "tipo de obra {name}",
      "part.language": "idioma {name}",
      "workDlg.noWriters": "No hay créditos de autoría para esta pista en el panel. Puedes añadirlos en el formulario o más tarde en el nivel «Obra».",
      "workDlg.after": "Después de enviarlo, la nueva obra se enlazará con la pista {track} (preparado, no enviado).",
      "workDlg.done": "La obra «{title}» se ha creado. El enlace con la pista {track} está preparado.",
      "busy.mb": "Cargando pistas y relaciones existentes de MusicBrainz…",
      "busy.discogs": "Cargando la publicación de Discogs {id}…",
      "busy.artists": "Buscando artistas de MB mediante sus enlaces de Discogs…",
      "busy.discogsArtist": "Cargando datos de Discogs para {name}…",
      "busy.apply.one": "Preparando {n} relación en el editor…",
      "busy.apply.other": "Preparando {n} relaciones en el editor…",
      "msg.noDiscogsLink": "Esta publicación aún no está enlazada con Discogs. Introduce arriba una URL de publicación de Discogs.",
      "msg.multiLinks": "Esta publicación está enlazada con {n} publicaciones de Discogs. Elige una arriba.",
      "msg.trackMismatch": "Discogs lista {d} pistas y MusicBrainz {m}. Las pistas se asignan por orden. Revisa la selección de pistas en las relaciones de grabación y de obra.",
      "msg.noCredits": "Discogs no tiene créditos para esta publicación. Puedes añadir entradas manualmente abajo.",
      "msg.confirmDiscard": "Se descartará la selección actual del panel. ¿Continuar?",
      "msg.badDiscogsId": "No se reconoce ningún ID de publicación de Discogs. Ejemplo: https://www.discogs.com/release/1234567",
      "msg.badMbid": "No se reconoce ningún MBID. Pega la URL de una página de artista de MB o un MBID.",
      "msg.notArtist": "Este MBID no pertenece a un artista.",
      "msg.editorNotReady": "El editor de relaciones aún no está listo. Espera a que la página termine de cargar e inténtalo de nuevo.",
      "msg.applied.one": "{n} relación está preparada en el editor, pero aún no se ha enviado. Revísala en el editor y pulsa tú mismo «Enter edit».",
      "msg.applied.other": "{n} relaciones están preparadas en el editor, pero aún no se han enviado. Revísalas en el editor y pulsa tú mismo «Enter edit».",
      "msg.notLoaded.one": "Se omitió {n} relación porque el medio {media} aún no está cargado en el editor. Despliega el medio en el editor y vuelve a preparar; lo ya preparado se omitirá.",
      "msg.notLoaded.other": "Se omitieron {n} relaciones porque el medio {media} aún no está cargado en el editor. Despliega el medio en el editor y vuelve a preparar; lo ya preparado se omitirá.",
      "msg.errors.one": "Error en {n} relación: {list}",
      "msg.errors.other": "Errores en {n} relaciones: {list}",
      "msg.noteMissing": "No se encontró el campo de la nota de edición. Añade tú mismo el origen de Discogs.",
      "msg.pendingWorks.one": "{n} obra creada aquí anteriormente aún no está enlazada con su grabación en MusicBrainz. Su enlace vuelve a estar preparado en el panel.",
      "msg.pendingWorks.other": "{n} obras creadas aquí anteriormente aún no están enlazadas con sus grabaciones en MusicBrainz. Sus enlaces vuelven a estar preparados en el panel.",
      "msg.toEditor": "Ir al editor",
      "err.mbHttp": "La API de MusicBrainz respondió con HTTP {status}.",
      "err.mbBusy": "La API de MusicBrainz está ocupada (HTTP 503). Inténtalo de nuevo en un momento.",
      "err.entity": "No se encontró la entrada {mbid} (HTTP {status}).",
      "err.discogsLimit": "Se alcanzó el límite de Discogs. Espera un minuto e inténtalo de nuevo.",
      "err.discogsMissing": "La publicación de Discogs {id} no existe.",
      "err.discogsHttp": "La API de Discogs respondió con HTTP {status}.",
      "err.typesMissing": "Los tipos de relación de MusicBrainz aún no se han cargado. Espera a que el editor termine de construirse y vuelve a abrir el panel.",
      "err.releaseMissing": "No se encontró la publicación mediante la API de MusicBrainz.",
      "err.treeMissing": "MB.tree no está disponible, así que no se pueden fijar atributos.",
      "log.title": "Registro",
      "log.copy": "Copiar",
      "log.copied": "Copiado",
      "log.clear": "Vaciar",
      "log.hide": "Ocultar",
      "log.start": "Panel abierto para la publicación {mbid}",
      "log.mbLoaded.one": "MusicBrainz cargado: {n} pista ({works} con obra), enlaces de Discogs: {links}",
      "log.mbLoaded.other": "MusicBrainz cargado: {n} pistas ({works} con obra), enlaces de Discogs: {links}",
      "log.trackMismatch": "El número de pistas difiere: Discogs {d}, MusicBrainz {m}",
      "log.discogsLoaded.one": "Publicación de Discogs {id} cargada: {artists} artistas, {n} rol",
      "log.discogsLoaded.other": "Publicación de Discogs {id} cargada: {artists} artistas, {n} roles",
      "log.artistLinked": "{name}: encontrado por enlace de Discogs → {mb}",
      "log.artistAmbiguous": "{name}: {n} artistas de MB comparten el enlace de Discogs",
      "log.artistMissing": "{name}: ningún artista de MB con este enlace de Discogs",
      "log.artistManual": "{name}: asignado manualmente → {mb}",
      "log.artistForm": "Formulario «Crear artista» abierto: {name}",
      "log.artistCreated": "Artista creado: {name} ({mbid})",
      "log.manualAdded": "Entrada manual añadida: {name}, {role}",
      "log.formCancelled": "Formulario cerrado sin crear nada",
      "log.workForm": "Formulario «Crear obra» abierto para la pista {track}",
      "log.workCreated": "Obra creada para la pista {track}: {title} ({mbid})",
      "log.workSearch.one": "Búsqueda de obras para la pista {track}: {n} resultado",
      "log.workSearch.other": "Búsqueda de obras para la pista {track}: {n} resultados",
      "log.workPicked": "Pista {track}: obra «{title}» elegida para enlazar",
      "log.workUnplanned": "Pista {track}: enlace de obra previsto eliminado",
      "log.applyStart.one": "Preparando {n} relación en el editor…",
      "log.applyStart.other": "Preparando {n} relaciones en el editor…",
      "log.staged": "Preparado: {text}",
      "log.skippedNotLoaded": "Omitido, medio no cargado: {text}",
      "log.error": "Error: {text}",
      "log.noteWritten": "Nota de edición actualizada",
      "log.noteMissing": "Campo de nota de edición no encontrado",
      "log.editorNotReady": "Editor de relaciones no listo",
      "log.pendingWorks.one": "{n} obra creada aún sin enlazar; su enlace vuelve a estar preparado en el panel",
      "log.pendingWorks.other": "{n} obras creadas aún sin enlazar; sus enlaces vuelven a estar preparados en el panel",
      "log.panic.one": "Reinicio de emergencia solicitado: la página se recarga y conserva {n} enlace de obra",
      "log.panic.other": "Reinicio de emergencia solicitado: la página se recarga y conserva {n} enlaces de obra",
      "log.panicDone.one": "Reinicio de emergencia: {n} enlace a una obra recién creada preparado",
      "log.panicDone.other": "Reinicio de emergencia: {n} enlaces a obras recién creadas preparados",
      "log.discogsJump": "Vista de Discogs: {result}",
      "syncMode.label": "Vista de Discogs – saltar al origen:",
      "syncMode.hover": "al pasar el ratón",
      "syncMode.click": "al hacer clic",
      "log.syncMode": "La vista de Discogs sigue al panel {mode}",
      "companies.title": "Companies, etc. (empresas)",
      "companies.explain": "Sellos, estudios y fábricas de Discogs. Se asignan a sellos o lugares de MB mediante sus enlaces de Discogs. Discogs también lista aquí personas como sellos: pega un artista de MB para enlazarla como persona.",
      "entity.artist": "artista",
      "entity.label": "sello",
      "entity.place": "lugar",
      "role.asEntity": "como {type} de MB",
      "role.companyWhole": "Discogs: Companies, etc. (toda la publicación)",
      "role.catno": "Número de catálogo en Discogs: {catno}",
      "role.companyPlaceholder": "p. ej. Pressed By",
      "credit.companyLabel": "Acreditado como",
      "issue.missingCompany": "falta el sello, lugar o artista de MB",
      "match.noLinkCompany": "ningún sello, lugar o artista de MB con este enlace de Discogs",
      "match.placeholderCompany": "URL o MBID de un sello, lugar o artista de MB",
      "match.createLabel": "Crear sello…",
      "match.createPlace": "Crear lugar…",
      "msg.notCompany": "Este MBID no es un artista, ni un sello o lugar adecuado para estos roles.",
      "companyDlg.titleLabel": "Crear sello: {name}",
      "companyDlg.titlePlace": "Crear lugar: {name}",
      "companyDlg.prefilled": "Prerrellenado desde Discogs: nombre y enlace de Discogs.",
      "companyDlg.checkLabel": "Revisa el formulario, añade tipo y zona si los conoces y pulsa tú mismo «Enter edit» abajo. Después, el panel recoge automáticamente el nuevo sello.",
      "companyDlg.checkPlace": "Revisa el formulario, añade el tipo de lugar (p. ej. estudio) y la zona y pulsa tú mismo «Enter edit» abajo. Después, el panel recoge automáticamente el nuevo lugar.",
      "companyDlg.done": "«{name}» se ha creado y está asignado en el panel.",
      "log.companyForm": "Formulario de creación abierto ({type}): {name}",
      "log.companyCreated": "Creado: {name} ({mbid})",
      "date.title": "Fechas guardadas",
      "date.used.one": "{n} fila",
      "date.used.other": "{n} filas",
      "date.suggestions": "Sugerencias:",
      "date.sugg.copyright": "año ℗/© en las notas de Discogs {date}",
      "date.formTitle": "Editar fecha",
      "date.begin": "Fecha de inicio",
      "date.end": "Fecha de fin",
      "date.save": "Guardar",
      "date.remove": "Eliminar",
      "date.formHint": "Como en MusicBrainz: año, mes y día en campos separados; mes y día pueden quedar vacíos. Para un solo día o año (p. ej. ℗ 1998), pon la misma fecha de inicio y de fin (⇣ la copia). También puedes pegar una fecha tal como la muestra MusicBrainz, p. ej. «from 2015-01-26 until 2015-01-27», «in 2015-01» u «on 2015-01-26».",
      "date.errBegin": "La fecha de inicio no es válida.",
      "date.errEnd": "La fecha de fin no es válida.",
      "date.errOrder": "La fecha de fin es anterior a la de inicio.",
      "date.notAllowed": "este tipo no admite fechas",
      "date.untitled": "Fecha",
      "preview.date": "fecha {date}",
      "log.dateSaved": "Fecha guardada: {date}",
      "log.dateRemoved": "Fecha eliminada: {date}",
      "match.searchArtist": "Buscar artistas",
      "th.date": "Fecha",
      "date.poolNew": "+ Nueva fecha",
      "date.poolExplain": "Guarda aquí las fechas una vez y reutilízalas: elige una en una fila, haz clic en una para estamparla en filas o aplícala a todas las filas con un tipo de relación.",
      "date.editEntry": "Editar o eliminar",
      "date.stampTitle": "Usar como sello: luego haz clic en el campo de fecha de una fila",
      "date.ended": "Esta relación ha terminado",
      "date.name": "Nombre",
      "date.namePlaceholder": "opcional, p. ej. Sesión 2",
      "date.copyTitle": "Copiar la fecha de inicio en la de fin",
      "date.addRow": "+ Fecha",
      "date.fromPool": "de las guardadas…",
      "date.toPool": "guardar fecha",
      "date.clear": "quitar fecha",
      "date.fromPoolName": "fecha guardada: {name}",
      "date.endedOnly": "terminada, sin fecha",
      "date.errEmpty": "Introduce al menos un año.",
      "date.stampActive": "Sello: {date}. Haz clic en el campo de fecha de una fila para aplicarlo.",
      "date.stampAllType": "o aplicar a",
      "date.stampAllEmpty": "todas las filas sin fecha",
      "date.stampApply": "Aplicar",
      "date.stampEnd": "Terminar sello",
      "date.updateRows.one": "{n} fila usa esta fecha. ¿Cambiarla también?",
      "date.updateRows.other": "{n} filas usan esta fecha. ¿Cambiarlas también?",
      "issue.badDate": "fecha no válida",
      "log.dateStamp": "Sello elegido: {date}",
      "log.dateApplied.one": "Fecha {date} puesta en {n} fila",
      "log.dateApplied.other": "Fecha {date} puesta en {n} filas",
      "log.datesVerified.one": "Comprobado en el editor: la fecha de {n} relación ha llegado",
      "log.datesVerified.other": "Comprobado en el editor: las fechas de las {n} relaciones han llegado",
      "log.datesMismatch.one": "En el editor {n} relación tiene otra fecha: {list}",
      "log.datesMismatch.other": "En el editor {n} relaciones tienen otra fecha: {list}",
      "log.datesUnverifiable": "No se pudieron comprobar las fechas en el editor",
      "msg.datesMismatch.one": "{n} relación del editor no tiene la fecha del panel: {list}. Compruébala en el editor.",
      "msg.datesMismatch.other": "{n} relaciones del editor no tienen la fecha del panel: {list}. Compruébalas en el editor.",
      "zoom.label": "Tamaño del texto",
      "zoom.smaller": "Texto más pequeño",
      "zoom.larger": "Texto más grande",
      "window.reset": "Restablecer posición y tamaño del panel y del registro",
      "status.skippedExisting": "ya está en MusicBrainz – puesto en Omitir",
      "legend.exists": "ya en MusicBrainz",
      "legend.existsSome": "en parte en MusicBrainz",
      "log.existingSkipped.one": "{n} fila ya está en MusicBrainz y se puso en Omitir: {list}",
      "log.existingSkipped.other": "{n} filas ya están en MusicBrainz y se pusieron en Omitir: {list}",
      "manual.hint": "Añade cualquier entrada de MusicBrainz que pueda relacionarse con esta publicación, sus grabaciones u obras: artista, sello, lugar, zona, evento, serie, grabación, publicación, obra y más. El tipo de entrada se reconoce por la URL o el MBID. La lista de roles muestra todos los tipos de relación de MB para ese tipo; para artistas también vale un rol como en Discogs (p. ej. Guitar [Electric]).",
      "manual.entityPlaceholder": "URL o MBID de cualquier entrada de MusicBrainz",
      "manual.search": "Buscar en MB:",
      "msg.badMbidAny": "No se reconoce ningún MBID. Pega la URL de la página de un artista, sello o lugar de MB, o un MBID.",
      "note.unknownRole": "No es un instrumento conocido por MusicBrainz. Se añade como «miscellaneous support» con el rol de Discogs como tarea; elige un tipo mejor si lo hay.",
      "date.pasteTitle": "Puedes pegar una fecha tal como la muestra MusicBrainz, p. ej. «from 2015-01-26 until 2015-01-27», «in 2015-01» u «on 2015-01-26».",
      "log.datePasted": "Fecha pegada: {date}",
      "log.dashboard": "Panel",
      "log.dashboardTitle": "Abrir el panel o traerlo de vuelta a la vista",
      "entity.area": "zona",
      "entity.event": "evento",
      "entity.series": "serie",
      "entity.recording": "grabación",
      "entity.release": "publicación",
      "entity.work": "obra",
      "entity.release_group": "grupo de publicaciones",
      "entity.instrument": "instrumento",
      "entity.genre": "género",
      "others.title": "Otras entradas",
      "others.explain": "Zonas, eventos, series, grabaciones, publicaciones, obras y otras entradas de MusicBrainz añadidas a mano.",
      "msg.urlNotHere": "Las URL no se añaden aquí; usa «External links» en el editor de la publicación.",
      "msg.noRelTypes": "MusicBrainz no tiene ningún tipo de relación entre el tipo «{type}» y una publicación, grabación u obra.",
      "msg.wrongEntityType": "Este MBID no es del tipo «{type}».",
      "match.placeholderOther": "URL o MBID ({type} de MB)",
      "dir.label": "Dirección",
      "dir.release": "esta publicación",
      "dir.recording": "cada grabación seleccionada",
      "dir.work": "cada obra de las pistas seleccionadas",
    },
    fr: {
      "title": "Importer les crédits Discogs",
      "launcher.open": "Importer les crédits Discogs…",
      "launcher.status.one": "{n} relation Discogs préparée, pas encore envoyée.",
      "launcher.status.other": "{n} relations Discogs préparées, pas encore envoyées.",
      "lang.label": "Langue",
      "common.close": "Fermer",
      "common.cancel": "Annuler",
      "common.quoted": "« {text} »",
      "raw": "{text}",
      "source.current": "{title} (Discogs {id})",
      "source.none": "Aucune parution Discogs chargée pour l’instant",
      "source.pick": "Choisir la parution Discogs liée…",
      "source.other": "Autre URL ou ID de parution Discogs",
      "source.load": "Charger",
      "sync.off": "Vue Discogs : désactivée",
      "sync.offTitle": "Le script complémentaire « MB x Vibecode: Import Discogs credits COMPANION » n’est pas installé ou pas actif.",
      "sync.noTab": "Vue Discogs : aucun onglet Discogs",
      "sync.openTab": "ouvrir en arrière-plan",
      "sync.connected": "Vue Discogs : connectée ({where})",
      "sync.visible": "onglet visible",
      "sync.background": "onglet en arrière-plan",
      "sync.jumping": "saut vers la source…",
      "sync.found.credit": "crédit mis en évidence",
      "sync.found.track": "piste mise en évidence",
      "sync.found.artist": "artiste mis en évidence",
      "sync.found.loading": "Discogs charge la parution…",
      "sync.found.none": "source introuvable sur Discogs",
      "sync.found.no-tab": "aucun onglet Discogs",
      "toolbar.levelAll": "Niveau pour toutes les lignes :",
      "toolbar.onlyMissing": "Afficher uniquement les artistes sans correspondance MB",
      "toolbar.roleCredits": "Crédits de rôle :",
      "toolbar.artistCredits": "Crédits d’artiste :",
      "toolbar.asOnDiscogs": "comme sur Discogs",
      "toolbar.clearAll": "tout vider",
      "level.recording": "Enregistrement",
      "level.release": "Parution",
      "level.work": "Œuvre",
      "level.skip": "Ignorer",
      "th.role": "Rôle Discogs",
      "th.type": "Relation MB",
      "th.attrs": "Attributs et crédits",
      "th.level": "Niveau",
      "th.tracks": "Pistes et état",
      "th.track": "Piste",
      "th.work": "Œuvre",
      "th.action": "Action",
      "group.spelling": "Graphie sur Discogs :",
      "group.noVariant": "Pas de graphie différente sur Discogs",
      "group.creditAll": "Crédit d’artiste pour tous les rôles",
      "group.creditAllAria": "Crédit d’artiste pour tous les rôles de {name}",
      "group.setAll": "Appliquer à tous",
      "group.addRole": "+ Autre rôle pour {name}",
      "match.searching": "Recherche de l’artiste MB…",
      "match.linked": "trouvé via le lien Discogs",
      "match.manual": "défini manuellement",
      "match.created": "nouvellement créé",
      "match.change": "modifier",
      "match.changeLabel": "modifier l’artiste MB",
      "match.placeholder": "URL ou MBID de l’artiste MB",
      "match.inputAria": "Artiste MusicBrainz pour {name}",
      "match.apply": "Appliquer",
      "match.search": "Chercher sur MB",
      "match.create": "Créer l’artiste…",
      "match.ambiguous": "plusieurs artistes MB ont ce lien Discogs",
      "match.pick": "Veuillez choisir…",
      "match.noLink": "aucun artiste MB avec ce lien Discogs",
      "match.noId": "sans ID Discogs",
      "role.placeholder": "p. ex. Keyboards",
      "role.aria": "Rôle",
      "role.remove": "Supprimer la ligne",
      "role.source": "Discogs : {where}",
      "role.tracks": "piste {list}",
      "role.wholeRelease": "Discogs : toute la parution",
      "role.unresolved": "Sans correspondance : {list}",
      "note.uncredited": "Selon Discogs, non mentionné sur la parution (Uncredited).",
      "note.featuring": "« Featuring » figure généralement déjà dans le crédit d’artiste. Veuillez vérifier.",
      "note.misc": "MusicBrainz n’a pas de relation spécifique pour ce rôle. Il est ajouté comme « miscellaneous support » avec le rôle Discogs comme tâche ; mettez-le sur Ignorer si vous n’en voulez pas.",
      "type.skipped": "non appliqué",
      "type.choose": "Choisir un type…",
      "type.aria": "Type de relation MusicBrainz",
      "attr.optional": "{name} (facultatif)",
      "mark.known": "connu",
      "mark.unknown": "inconnu",
      "roleCredit.label": "Crédit de rôle",
      "roleCredit.placeholder": "aucun",
      "artistCredit.label": "Crédit d’artiste",
      "credit.placeholder": "vide = nom MB",
      "dest.credit": "enregistré comme crédit pour « {name} »",
      "dest.text": "enregistré dans l’attribut « {name} »",
      "dest.note": "aucun champ MB adapté, va uniquement dans la note de modification",
      "dest.none": "aucun champ MB adapté, non appliqué",
      "tracks.count.one": "{sel} sur {n} piste",
      "tracks.count.other": "{sel} sur {n} pistes",
      "tracks.worksOf": "œuvres de ces pistes",
      "tracks.wholeRelease": "toute la parution",
      "picker.all": "Toutes",
      "picker.none": "Aucune",
      "picker.invert": "Inverser",
      "picker.discogs": "Suggestion Discogs",
      "picker.legend": "Les numéros marqués de {dot} proviennent de Discogs.",
      "picker.medium": "Support {n}",
      "picker.dpos": "Position Discogs : {pos}",
      "picker.noDpos": "pas d’équivalent Discogs",
      "status.new.one": "{n} nouvelle",
      "status.new.other": "{n} nouvelles",
      "status.existing.one": "{n} existe déjà",
      "status.existing.other": "{n} existent déjà",
      "status.applied.one": "{n} préparée",
      "status.applied.other": "{n} préparées",
      "status.noWork.one": "{n} piste sans œuvre",
      "status.noWork.other": "{n} pistes sans œuvre",
      "status.loose": "{n}× le type existe déjà avec d’autres attributs",
      "status.nothing": "rien de nouveau",
      "issue.searching": "recherche de l’artiste MB",
      "issue.missingArtist": "artiste MB manquant",
      "issue.chooseType": "choisissez un type de relation",
      "issue.noTracks": "aucune piste sélectionnée",
      "issue.noWork": "les pistes sélectionnées n’ont pas encore d’œuvre",
      "issue.unknownAttr": "{root} « {value} » inconnu",
      "issue.requiredAttr": "attribut obligatoire « {name} » manquant",
      "sum.new.one": "{n} nouvelle relation",
      "sum.new.other": "{n} nouvelles relations",
      "kind.recording": "{n} sur des enregistrements",
      "kind.release": "{n} sur la parution",
      "kind.work": "{n} sur des œuvres",
      "kind.workLink.one": "{n} lien d’œuvre",
      "kind.workLink.other": "{n} liens d’œuvre",
      "sum.incomplete.one": "{n} ligne incomplète",
      "sum.incomplete.other": "{n} lignes incomplètes",
      "sum.existing.one": "{n} existe déjà sur MB",
      "sum.existing.other": "{n} existent déjà sur MB",
      "footer.preview": "Aperçu de toutes les relations",
      "footer.editNote": "Écrire la source et un résumé dans la note de modification",
      "footer.apply": "Préparer dans l’éditeur de relations",
      "footer.hint": "Rien n’est envoyé. Vous vérifiez les modifications dans l’éditeur et cliquez vous-même sur « Enter edit ».",
      "panic.button.one": "Urgence : lier uniquement la nouvelle œuvre",
      "panic.button.other": "Urgence : lier uniquement les {n} nouvelles œuvres",
      "panic.title": "Annule toutes les modifications non enregistrées de l’éditeur de relations et prépare de nouveau uniquement les liens vers les œuvres créées ici.",
      "panic.confirm.one": "Réinitialisation d’urgence\n\nToutes les modifications non enregistrées de l’éditeur de relations seront annulées, y compris celles faites à la main, et le tableau recommence à zéro.\nEnsuite, seul le lien vers l’œuvre nouvellement créée sera de nouveau préparé, pour qu’elle ne reste pas sans lien.\n\nLa page va être rechargée. Continuer ?",
      "panic.confirm.other": "Réinitialisation d’urgence\n\nToutes les modifications non enregistrées de l’éditeur de relations seront annulées, y compris celles faites à la main, et le tableau recommence à zéro.\nEnsuite, seuls les liens vers les {n} œuvres nouvellement créées seront de nouveau préparés, pour qu’elles ne restent pas sans lien.\n\nLa page va être rechargée. Continuer ?",
      "panic.done.one": "Réinitialisation d’urgence terminée : {n} lien vers une œuvre nouvellement créée est préparé, tout le reste a été réinitialisé. Envoyez-le avec « Enter edit » pour que l’œuvre ne reste pas sans lien.",
      "panic.done.other": "Réinitialisation d’urgence terminée : {n} liens vers des œuvres nouvellement créées sont préparés, tout le reste a été réinitialisé. Envoyez-les avec « Enter edit » pour que les œuvres ne restent pas sans lien.",
      "preview.empty": "Aucune relation prête pour l’instant.",
      "preview.release": "Parution",
      "preview.work": "Œuvre : {title}",
      "preview.linkWork": "Lier l’œuvre : {title}",
      "preview.attrCredit": "{name} comme « {credit} »",
      "preview.artistCredit": "crédit d’artiste « {credit} »",
      "preview.noteOnly": "note de modification uniquement : « {text} »",
      "manual.title": "Ajouter une entrée manuellement",
      "manual.artistAria": "Entrée MusicBrainz",
      "manual.rolePlaceholder": "Type de relation MB ou rôle Discogs, p. ex. artwork ou Guitar [Electric]",
      "manual.add": "Ajouter",
      "works.title": "Œuvres",
      "works.missing.one": "{n} piste n’a pas encore d’œuvre.",
      "works.missing.other": "{n} pistes n’ont pas encore d’œuvre.",
      "works.allDone": "Chaque piste a une œuvre ou un lien préparé.",
      "works.explain": "Les œuvres trouvées ou nouvellement créées sont liées aux enregistrements lors de la préparation. Les crédits d’écriture au niveau « Œuvre » vont sur ces œuvres.",
      "works.type": "Type pour les nouvelles œuvres",
      "works.lang": "Langue",
      "works.none": "aucun",
      "works.searchAll": "Chercher des œuvres pour toutes les pistes sans œuvre",
      "works.createAll": "Créer les œuvres manquantes une par une…",
      "works.linked": "liée",
      "works.plannedFound": "trouvée, sera liée",
      "works.plannedCreated": "nouvellement créée, sera liée",
      "works.unplan": "Retirer le lien",
      "works.noWork": "aucune œuvre liée",
      "works.search": "Chercher",
      "works.create": "Créer l’œuvre…",
      "works.searching": "Recherche en cours…",
      "works.basisWriters": "Recherche par titre et {names}",
      "works.basisTitle": "Recherche par titre uniquement (aucun crédit d’écriture associé)",
      "works.link": "Lier",
      "works.noResults": "Aucune œuvre correspondante trouvée.",
      "sub.window": "Ouvrir dans une fenêtre séparée",
      "sub.frameTitle": "Formulaire MusicBrainz",
      "sub.blocked": "Le formulaire ne peut pas être intégré ici. Ouvrez-le avec « Ouvrir dans une fenêtre séparée ».",
      "sub.popupBlocked": "Le navigateur a bloqué la fenêtre.",
      "sub.popupOpen": "Le formulaire est ouvert dans sa propre fenêtre. Après l’envoi, le tableau récupère le résultat.",
      "artistDlg.title": "Créer l’artiste : {name}",
      "artistDlg.prefilled": "Prérempli depuis Discogs : {list}.",
      "part.name": "nom",
      "part.type": "type {type}",
      "type.group": "groupe",
      "type.person": "personne",
      "part.urls.one": "{n} lien web (lien Discogs compris)",
      "part.urls.other": "{n} liens web (lien Discogs compris)",
      "part.members.one": "une relation « member of band » avec {names}",
      "part.members.other": "{n} relations « member of band » avec {names}",
      "artistDlg.notInMb": "Absents de MusicBrainz et donc non liés : {list}.",
      "artistDlg.loadFailed": "Données Discogs non chargées : {msg}",
      "artistDlg.check": "Vérifiez le formulaire et cliquez vous-même sur « Enter edit » en bas. Le tableau récupère ensuite automatiquement le nouvel artiste. Les liens web sans type détecté doivent être attribués dans le formulaire.",
      "artistDlg.done": "L’artiste « {name} » a été créé et est associé dans le tableau.",
      "workDlg.title": "Créer l’œuvre : {title}",
      "workDlg.prefilled": "Prérempli : {list}.",
      "part.title": "titre « {title} »",
      "part.workType": "type d’œuvre {name}",
      "part.language": "langue {name}",
      "workDlg.noWriters": "Aucun crédit d’écriture pour cette piste dans le tableau. Vous pouvez les ajouter dans le formulaire ou plus tard au niveau « Œuvre ».",
      "workDlg.after": "Après l’envoi, la nouvelle œuvre sera liée à la piste {track} (préparé, non envoyé).",
      "workDlg.done": "L’œuvre « {title} » a été créée. Le lien avec la piste {track} est préparé.",
      "busy.mb": "Chargement des pistes et des relations existantes depuis MusicBrainz…",
      "busy.discogs": "Chargement de la parution Discogs {id}…",
      "busy.artists": "Recherche des artistes MB via leurs liens Discogs…",
      "busy.discogsArtist": "Chargement des données Discogs pour {name}…",
      "busy.apply.one": "Préparation de {n} relation dans l’éditeur…",
      "busy.apply.other": "Préparation de {n} relations dans l’éditeur…",
      "msg.noDiscogsLink": "Cette parution n’est pas encore liée à Discogs. Saisissez une URL de parution Discogs ci-dessus.",
      "msg.multiLinks": "Cette parution est liée à {n} parutions Discogs. Choisissez-en une ci-dessus.",
      "msg.trackMismatch": "Discogs liste {d} pistes, MusicBrainz {m}. Les pistes sont associées dans l’ordre. Vérifiez la sélection des pistes pour les relations d’enregistrement et d’œuvre.",
      "msg.noCredits": "Discogs n’a aucun crédit pour cette parution. Vous pouvez ajouter des entrées manuellement ci-dessous.",
      "msg.confirmDiscard": "La sélection actuelle du tableau sera abandonnée. Continuer ?",
      "msg.badDiscogsId": "Aucun ID de parution Discogs reconnu. Exemple : https://www.discogs.com/release/1234567",
      "msg.badMbid": "Aucun MBID reconnu. Collez l’URL d’une page d’artiste MB ou un MBID.",
      "msg.notArtist": "Ce MBID n’appartient pas à un artiste.",
      "msg.editorNotReady": "L’éditeur de relations n’est pas encore prêt. Attendez que la page soit entièrement chargée et réessayez.",
      "msg.applied.one": "{n} relation est préparée dans l’éditeur mais pas encore envoyée. Vérifiez-la dans l’éditeur et cliquez vous-même sur « Enter edit ».",
      "msg.applied.other": "{n} relations sont préparées dans l’éditeur mais pas encore envoyées. Vérifiez-les dans l’éditeur et cliquez vous-même sur « Enter edit ».",
      "msg.notLoaded.one": "{n} relation ignorée, car le support {media} n’est pas encore chargé dans l’éditeur. Dépliez le support dans l’éditeur et préparez de nouveau ; ce qui est déjà préparé sera ignoré.",
      "msg.notLoaded.other": "{n} relations ignorées, car le support {media} n’est pas encore chargé dans l’éditeur. Dépliez le support dans l’éditeur et préparez de nouveau ; ce qui est déjà préparé sera ignoré.",
      "msg.errors.one": "Erreur pour {n} relation : {list}",
      "msg.errors.other": "Erreurs pour {n} relations : {list}",
      "msg.noteMissing": "Le champ de la note de modification est introuvable. Veuillez ajouter vous-même la source Discogs.",
      "msg.pendingWorks.one": "{n} œuvre créée ici auparavant n’est pas encore liée à son enregistrement dans MusicBrainz. Son lien est de nouveau préparé dans le tableau.",
      "msg.pendingWorks.other": "{n} œuvres créées ici auparavant ne sont pas encore liées à leurs enregistrements dans MusicBrainz. Leurs liens sont de nouveau préparés dans le tableau.",
      "msg.toEditor": "Vers l’éditeur",
      "err.mbHttp": "L’API MusicBrainz a répondu avec HTTP {status}.",
      "err.mbBusy": "L’API MusicBrainz est surchargée (HTTP 503). Réessayez dans un instant.",
      "err.entity": "Entrée {mbid} introuvable (HTTP {status}).",
      "err.discogsLimit": "Limite Discogs atteinte. Attendez une minute et réessayez.",
      "err.discogsMissing": "La parution Discogs {id} n’existe pas.",
      "err.discogsHttp": "L’API Discogs a répondu avec HTTP {status}.",
      "err.typesMissing": "Les types de relation MusicBrainz ne sont pas encore chargés. Attendez que l’éditeur soit entièrement construit et rouvrez le tableau.",
      "err.releaseMissing": "La parution est introuvable via l’API MusicBrainz.",
      "err.treeMissing": "MB.tree n’est pas disponible, les attributs ne peuvent donc pas être définis.",
      "log.title": "Journal",
      "log.copy": "Copier",
      "log.copied": "Copié",
      "log.clear": "Vider",
      "log.hide": "Masquer",
      "log.start": "Tableau ouvert pour la parution {mbid}",
      "log.mbLoaded.one": "MusicBrainz chargé : {n} piste ({works} avec œuvre), liens Discogs : {links}",
      "log.mbLoaded.other": "MusicBrainz chargé : {n} pistes ({works} avec œuvre), liens Discogs : {links}",
      "log.trackMismatch": "Nombre de pistes différent : Discogs {d}, MusicBrainz {m}",
      "log.discogsLoaded.one": "Parution Discogs {id} chargée : {artists} artistes, {n} rôle",
      "log.discogsLoaded.other": "Parution Discogs {id} chargée : {artists} artistes, {n} rôles",
      "log.artistLinked": "{name} : trouvé via le lien Discogs → {mb}",
      "log.artistAmbiguous": "{name} : {n} artistes MB partagent le lien Discogs",
      "log.artistMissing": "{name} : aucun artiste MB avec ce lien Discogs",
      "log.artistManual": "{name} : défini manuellement → {mb}",
      "log.artistForm": "Formulaire « Créer l’artiste » ouvert : {name}",
      "log.artistCreated": "Artiste créé : {name} ({mbid})",
      "log.manualAdded": "Entrée manuelle ajoutée : {name}, {role}",
      "log.formCancelled": "Formulaire fermé sans rien créer",
      "log.workForm": "Formulaire « Créer l’œuvre » ouvert pour la piste {track}",
      "log.workCreated": "Œuvre créée pour la piste {track} : {title} ({mbid})",
      "log.workSearch.one": "Recherche d’œuvres pour la piste {track} : {n} résultat",
      "log.workSearch.other": "Recherche d’œuvres pour la piste {track} : {n} résultats",
      "log.workPicked": "Piste {track} : œuvre « {title} » choisie pour le lien",
      "log.workUnplanned": "Piste {track} : lien d’œuvre prévu retiré",
      "log.applyStart.one": "Préparation de {n} relation dans l’éditeur…",
      "log.applyStart.other": "Préparation de {n} relations dans l’éditeur…",
      "log.staged": "Préparé : {text}",
      "log.skippedNotLoaded": "Ignoré, support non chargé : {text}",
      "log.error": "Erreur : {text}",
      "log.noteWritten": "Note de modification mise à jour",
      "log.noteMissing": "Champ de la note de modification introuvable",
      "log.editorNotReady": "Éditeur de relations pas prêt",
      "log.pendingWorks.one": "{n} œuvre créée pas encore liée ; son lien est de nouveau préparé dans le tableau",
      "log.pendingWorks.other": "{n} œuvres créées pas encore liées ; leurs liens sont de nouveau préparés dans le tableau",
      "log.panic.one": "Réinitialisation d’urgence demandée : la page se recharge et conserve {n} lien d’œuvre",
      "log.panic.other": "Réinitialisation d’urgence demandée : la page se recharge et conserve {n} liens d’œuvre",
      "log.panicDone.one": "Réinitialisation d’urgence : {n} lien vers une œuvre nouvellement créée préparé",
      "log.panicDone.other": "Réinitialisation d’urgence : {n} liens vers des œuvres nouvellement créées préparés",
      "log.discogsJump": "Vue Discogs : {result}",
      "syncMode.label": "Vue Discogs – aller à la source :",
      "syncMode.hover": "au survol",
      "syncMode.click": "au clic",
      "log.syncMode": "La vue Discogs suit le tableau {mode}",
      "companies.title": "Companies, etc. (sociétés)",
      "companies.explain": "Labels, studios et usines de Discogs. Ils sont associés à des labels ou lieux MB via leurs liens Discogs. Discogs liste aussi des personnes comme labels : collez un artiste MB pour la lier comme personne.",
      "entity.artist": "artiste",
      "entity.label": "label",
      "entity.place": "lieu",
      "role.asEntity": "comme {type} MB",
      "role.companyWhole": "Discogs : Companies, etc. (toute la parution)",
      "role.catno": "Numéro de catalogue sur Discogs : {catno}",
      "role.companyPlaceholder": "p. ex. Pressed By",
      "credit.companyLabel": "Crédité comme",
      "issue.missingCompany": "label, lieu ou artiste MB manquant",
      "match.noLinkCompany": "aucun label, lieu ou artiste MB avec ce lien Discogs",
      "match.placeholderCompany": "URL ou MBID d’un label, lieu ou artiste MB",
      "match.createLabel": "Créer le label…",
      "match.createPlace": "Créer le lieu…",
      "msg.notCompany": "Ce MBID n’est ni un artiste, ni un label ou lieu adapté à ces rôles.",
      "companyDlg.titleLabel": "Créer le label : {name}",
      "companyDlg.titlePlace": "Créer le lieu : {name}",
      "companyDlg.prefilled": "Prérempli depuis Discogs : nom et lien Discogs.",
      "companyDlg.checkLabel": "Vérifiez le formulaire, ajoutez le type et la zone si vous les connaissez, puis cliquez vous-même sur « Enter edit » en bas. Le tableau récupère ensuite automatiquement le nouveau label.",
      "companyDlg.checkPlace": "Vérifiez le formulaire, ajoutez le type de lieu (p. ex. studio) et la zone, puis cliquez vous-même sur « Enter edit » en bas. Le tableau récupère ensuite automatiquement le nouveau lieu.",
      "companyDlg.done": "« {name} » a été créé et est associé dans le tableau.",
      "log.companyForm": "Formulaire de création ouvert ({type}) : {name}",
      "log.companyCreated": "Créé : {name} ({mbid})",
      "date.title": "Dates enregistrées",
      "date.used.one": "{n} ligne",
      "date.used.other": "{n} lignes",
      "date.suggestions": "Suggestions :",
      "date.sugg.copyright": "année ℗/© dans les notes Discogs {date}",
      "date.formTitle": "Modifier la date",
      "date.begin": "Date de début",
      "date.end": "Date de fin",
      "date.save": "Enregistrer",
      "date.remove": "Supprimer",
      "date.formHint": "Comme dans MusicBrainz : année, mois et jour dans des champs séparés ; mois et jour peuvent rester vides. Pour un seul jour ou une année (p. ex. ℗ 1998), saisissez la même date de début et de fin (⇣ la copie). Vous pouvez aussi coller une date telle que MusicBrainz l’affiche, p. ex. « from 2015-01-26 until 2015-01-27 », « in 2015-01 » ou « on 2015-01-26 ».",
      "date.errBegin": "La date de début n’est pas valide.",
      "date.errEnd": "La date de fin n’est pas valide.",
      "date.errOrder": "La date de fin est antérieure à la date de début.",
      "date.notAllowed": "ce type n’a pas de dates",
      "date.untitled": "Date",
      "preview.date": "date {date}",
      "log.dateSaved": "Date enregistrée : {date}",
      "log.dateRemoved": "Date supprimée : {date}",
      "match.searchArtist": "Chercher des artistes",
      "th.date": "Date",
      "date.poolNew": "+ Nouvelle date",
      "date.poolExplain": "Enregistrez les dates ici une fois et réutilisez-les : choisissez-en une dans une ligne, cliquez sur une date pour l’appliquer comme tampon ou appliquez-la à toutes les lignes d’un type de relation.",
      "date.editEntry": "Modifier ou supprimer",
      "date.stampTitle": "Utiliser comme tampon : cliquez ensuite sur le champ de date d’une ligne",
      "date.ended": "Cette relation est terminée",
      "date.name": "Nom",
      "date.namePlaceholder": "facultatif, p. ex. Session 2",
      "date.copyTitle": "Copier la date de début dans la date de fin",
      "date.addRow": "+ Date",
      "date.fromPool": "parmi les dates…",
      "date.toPool": "enregistrer la date",
      "date.clear": "retirer la date",
      "date.fromPoolName": "date enregistrée : {name}",
      "date.endedOnly": "terminée, sans date",
      "date.errEmpty": "Saisissez au moins une année.",
      "date.stampActive": "Tampon : {date}. Cliquez sur le champ de date d’une ligne pour l’appliquer.",
      "date.stampAllType": "ou appliquer à",
      "date.stampAllEmpty": "toutes les lignes sans date",
      "date.stampApply": "Appliquer",
      "date.stampEnd": "Arrêter le tampon",
      "date.updateRows.one": "{n} ligne utilise cette date. La modifier aussi ?",
      "date.updateRows.other": "{n} lignes utilisent cette date. Les modifier aussi ?",
      "issue.badDate": "date non valide",
      "log.dateStamp": "Tampon choisi : {date}",
      "log.dateApplied.one": "Date {date} appliquée à {n} ligne",
      "log.dateApplied.other": "Date {date} appliquée à {n} lignes",
      "log.datesVerified.one": "Vérifié dans l’éditeur : la date de {n} relation est arrivée",
      "log.datesVerified.other": "Vérifié dans l’éditeur : les dates des {n} relations sont arrivées",
      "log.datesMismatch.one": "Dans l’éditeur, {n} relation a une autre date : {list}",
      "log.datesMismatch.other": "Dans l’éditeur, {n} relations ont une autre date : {list}",
      "log.datesUnverifiable": "Les dates n’ont pas pu être vérifiées dans l’éditeur",
      "msg.datesMismatch.one": "{n} relation dans l’éditeur n’a pas la date du tableau : {list}. Veuillez la vérifier dans l’éditeur.",
      "msg.datesMismatch.other": "{n} relations dans l’éditeur n’ont pas la date du tableau : {list}. Veuillez les vérifier dans l’éditeur.",
      "zoom.label": "Taille du texte",
      "zoom.smaller": "Texte plus petit",
      "zoom.larger": "Texte plus grand",
      "window.reset": "Réinitialiser la position et la taille du tableau et du journal",
      "status.skippedExisting": "déjà dans MusicBrainz – mis sur Ignorer",
      "legend.exists": "déjà dans MusicBrainz",
      "legend.existsSome": "en partie dans MusicBrainz",
      "log.existingSkipped.one": "{n} ligne est déjà dans MusicBrainz et a été mise sur Ignorer : {list}",
      "log.existingSkipped.other": "{n} lignes sont déjà dans MusicBrainz et ont été mises sur Ignorer : {list}",
      "manual.hint": "Ajoutez toute entrée MusicBrainz qui peut être liée à cette parution, à ses enregistrements ou à ses œuvres : artiste, label, lieu, région, événement, série, enregistrement, parution, œuvre et plus. Le type d’entrée est reconnu à partir de l’URL ou du MBID. La liste des rôles montre tous les types de relation MB pour ce type ; pour les artistes, un rôle comme sur Discogs (p. ex. Guitar [Electric]) fonctionne aussi.",
      "manual.entityPlaceholder": "URL ou MBID de n’importe quelle entrée MusicBrainz",
      "manual.search": "Chercher sur MB :",
      "msg.badMbidAny": "Aucun MBID reconnu. Collez l’URL de la page d’un artiste, label ou lieu MB, ou un MBID.",
      "note.unknownRole": "Pas un instrument connu de MusicBrainz. Ajouté comme « miscellaneous support » avec le rôle Discogs comme tâche ; choisissez un meilleur type s’il y en a un.",
      "date.pasteTitle": "Vous pouvez coller une date telle que MusicBrainz l’affiche, p. ex. « from 2015-01-26 until 2015-01-27 », « in 2015-01 » ou « on 2015-01-26 ».",
      "log.datePasted": "Date collée : {date}",
      "log.dashboard": "Tableau",
      "log.dashboardTitle": "Ouvrir le tableau ou le ramener à l’écran",
      "entity.area": "région",
      "entity.event": "événement",
      "entity.series": "série",
      "entity.recording": "enregistrement",
      "entity.release": "parution",
      "entity.work": "œuvre",
      "entity.release_group": "groupe de parutions",
      "entity.instrument": "instrument",
      "entity.genre": "genre",
      "others.title": "Autres entrées",
      "others.explain": "Régions, événements, séries, enregistrements, parutions, œuvres et autres entrées MusicBrainz ajoutées à la main.",
      "msg.urlNotHere": "Les URL ne s’ajoutent pas ici ; utilisez « External links » dans l’éditeur de parution.",
      "msg.noRelTypes": "MusicBrainz n’a aucun type de relation entre le type « {type} » et une parution, un enregistrement ou une œuvre.",
      "msg.wrongEntityType": "Ce MBID n’est pas du type « {type} ».",
      "match.placeholderOther": "URL ou MBID ({type} MB)",
      "dir.label": "Sens",
      "dir.release": "cette parution",
      "dir.recording": "chaque enregistrement choisi",
      "dir.work": "chaque œuvre des pistes choisies",
    },
  };
  /* eslint-enable quote-props */

  /**
   * Translates a key and fills in {placeholders}. Keys with ".one"/".other" forms are
   * pluralized by params.n. Missing entries fall back to English, then to the key.
   */
  function tr(key, params = {}) {
    const dict = I18N[LANG] || I18N.en;
    let text = dict[key];
    if (text == null && (dict[`${key}.other`] != null || I18N.en[`${key}.other`] != null)) {
      let form = 'other';
      try {
        form = new Intl.PluralRules(LANG).select(Number(params.n) || 0);
      } catch (e) {
        form = Number(params.n) === 1 ? 'one' : 'other';
      }
      text = dict[`${key}.${form}`] ?? dict[`${key}.other`] ?? I18N.en[`${key}.${form}`] ?? I18N.en[`${key}.other`];
    }
    if (text == null) text = I18N.en[key] ?? key;
    return String(text).replace(/\{(\w+)\}/g, (m, name) => (params[name] != null ? String(params[name]) : m));
  }

  // ===========================================================================
  // 2. Reading Discogs data (pure functions, no DOM)
  // ===========================================================================

  /** Splits at commas that are not inside square brackets. */
  function splitTopLevel(str) {
    const parts = [];
    let depth = 0;
    let current = '';
    for (const ch of String(str || '')) {
      if (ch === '[') depth++;
      else if (ch === ']') depth = Math.max(0, depth - 1);
      if (ch === ',' && depth === 0) {
        parts.push(current);
        current = '';
      } else {
        current += ch;
      }
    }
    parts.push(current);
    return parts.map((p) => p.trim()).filter(Boolean);
  }

  /** "Guitar [Electric, Rhythm], Vocals" → [{raw, base: 'Guitar', mods: ['Electric', 'Rhythm']}, …] */
  function parseRoles(roleString) {
    return splitTopLevel(roleString).map((raw) => {
      const mods = [];
      const base = raw.replace(/\[([^\]]*)\]/g, (_, inner) => {
        mods.push(...splitTopLevel(inner));
        return ' ';
      }).replace(/\s+/g, ' ').trim();
      return { raw, base, mods };
    });
  }

  /** Tracks without headings; an index track counts as one track, its sub-tracks become aliases. */
  function flattenDiscogsTracks(tracklist) {
    const tracks = [];
    for (const t of tracklist || []) {
      if (t.type_ === 'heading') continue;
      const entry = {
        position: t.position || '',
        title: t.title || '',
        extraartists: [...(t.extraartists || [])],
        aliases: [],
      };
      if (t.type_ === 'index') {
        for (const sub of t.sub_tracks || []) {
          if (sub.position) entry.aliases.push(sub.position);
          entry.extraartists.push(...(sub.extraartists || []));
        }
      }
      tracks.push(entry);
    }
    return tracks;
  }

  const normPos = (p) => String(p || '').toUpperCase().replace(/\s+/g, '');

  function positionIndex(dTracks) {
    const map = new Map();
    dTracks.forEach((t, i) => {
      [t.position, ...t.aliases].filter(Boolean).forEach((p) => {
        const key = normPos(p);
        if (!map.has(key)) map.set(key, i);
      });
    });
    return map;
  }

  /** "A1 to A3, B2" → indexes into the flat Discogs track list */
  function parseTrackSpec(spec, posMap) {
    const indexes = new Set();
    const unresolved = [];
    for (const part of String(spec || '').split(',').map((s) => s.trim()).filter(Boolean)) {
      const range = part.split(/\s+to\s+/i);
      if (range.length === 2) {
        const a = posMap.get(normPos(range[0]));
        const b = posMap.get(normPos(range[1]));
        if (a !== undefined && b !== undefined) {
          for (let i = Math.min(a, b); i <= Math.max(a, b); i++) indexes.add(i);
          continue;
        }
      } else {
        const a = posMap.get(normPos(part));
        if (a !== undefined) {
          indexes.add(a);
          continue;
        }
      }
      unresolved.push(part);
    }
    return { indexes, unresolved };
  }

  /**
   * Collects all credits (release level and track level), grouped by Discogs artist,
   * merging identical roles of the same artist across multiple tracks.
   */
  function collectCredits(release, dTracks, posMap) {
    const groups = new Map();

    const add = (ea, { allTracks = false, indexes = [], spec = '', position = '', unresolved = [] }) => {
      const dId = Number(ea.id) || 0;
      const name = cleanDiscogsName(ea.name);
      if (!name && !dId) return;
      const gKey = dId ? `id:${dId}` : `name:${norm(name)}`;
      if (!groups.has(gKey)) groups.set(gKey, { dId, name, rawName: String(ea.name || '').trim(), roles: new Map() });
      const group = groups.get(gKey);
      const anv = String(ea.anv || '').trim();
      for (const role of parseRoles(ea.role)) {
        const rKey = `${norm(role.raw)}|${norm(anv)}`;
        if (!group.roles.has(rKey)) {
          group.roles.set(rKey, {
            role, anv, allTracks: false, indexes: new Set(), unresolved: [], specs: [], positions: [],
          });
        }
        const entry = group.roles.get(rKey);
        if (allTracks) entry.allTracks = true;
        indexes.forEach((i) => entry.indexes.add(i));
        unresolved.forEach((u) => entry.unresolved.includes(u) || entry.unresolved.push(u));
        if (spec && !entry.specs.includes(spec)) entry.specs.push(spec);
        if (position && !entry.positions.includes(position)) entry.positions.push(position);
      }
    };

    for (const ea of release.extraartists || []) {
      const spec = String(ea.tracks || '').trim();
      if (spec) {
        const { indexes, unresolved } = parseTrackSpec(spec, posMap);
        add(ea, { indexes: [...indexes], spec, unresolved });
      } else {
        add(ea, { allTracks: true });
      }
    }
    dTracks.forEach((t, i) => {
      for (const ea of t.extraartists || []) {
        add(ea, { indexes: [i], position: t.position || String(i + 1) });
      }
    });

    return [...groups.values()];
  }

  // ===========================================================================
  // 3. Discogs roles → MusicBrainz relationship types
  // ===========================================================================

  /** Discogs spelling → possible MB instrument names (tried in this order). */
  const INSTRUMENT_ALIASES = {
    'bass': ['bass'],
    'electric bass': ['electric bass guitar', 'bass guitar'],
    'acoustic bass': ['acoustic bass guitar', 'double bass'],
    'upright bass': ['double bass'],
    'contrabass': ['double bass'],
    'drums': ['drums (drum set)', 'drum set', 'drums'],
    'drum': ['drums (drum set)', 'drum set', 'drums'],
    'keyboards': ['keyboard'],
    'synth': ['synthesizer'],
    'synthesizers': ['synthesizer'],
    'rhodes': ['rhodes piano', 'fender rhodes', 'electric piano'],
    'fender rhodes': ['rhodes piano', 'fender rhodes', 'electric piano'],
    'rhodes electric piano': ['rhodes piano', 'electric piano'],
    'wurlitzer': ['wurlitzer electric piano', 'electric piano'],
    'wurlitzer electric piano': ['wurlitzer electric piano', 'electric piano'],
    'hammond organ': ['hammond organ', 'organ'],
    'congas': ['conga', 'congas'],
    'bongos': ['bongos', 'bongo'],
    'turntables': ['turntable(s)', 'turntables', 'turntable'],
    'scratches': ['turntable(s)', 'turntables', 'turntable'],
    'horns': ['brass'],
    'french horn': ['horn', 'french horn'],
    'sax': ['saxophone'],
    'tenor sax': ['tenor saxophone'],
    'alto sax': ['alto saxophone'],
    'baritone sax': ['baritone saxophone'],
    'soprano sax': ['soprano saxophone'],
    'pedal steel': ['pedal steel guitar'],
    'steel guitar': ['steel guitar', 'pedal steel guitar'],
    'vibes': ['vibraphone'],
    'claps': ['handclaps'],
    'hand claps': ['handclaps'],
    'electronics': ['electronic instruments', 'electronics'],
    'fiddle': ['fiddle', 'violin'],
    '12-string guitar': ['12 string guitar', '12-string guitar'],
    'twelve-string guitar': ['12 string guitar', '12-string guitar'],
  };

  function instrumentCandidates(base, mods) {
    const b = norm(base);
    const out = [];
    const push = (x) => {
      const n = norm(x);
      if (n && !out.includes(n)) out.push(n);
    };
    for (const m of mods.map(norm)) {
      push(`${m} ${b}`);
      (INSTRUMENT_ALIASES[`${m} ${b}`] || []).forEach(push);
      push(m);
      (INSTRUMENT_ALIASES[m] || []).forEach(push);
    }
    (INSTRUMENT_ALIASES[b] || []).forEach(push);
    push(b);
    if (b.length > 3 && b.endsWith('s')) push(b.slice(0, -1));
    return out;
  }

  /**
   * Returns a suggestion that can always be overridden in the dashboard:
   * types        – candidate MB relationship types (by name), the first available one wins
   * level        – 'recording' | 'release' | 'skip'
   * primaryCands – instrument or vocal attribute candidates
   * flags        – simple attributes such as additional, guest, solo, co, executive …
   * consumed     – bracket details already used for the mapping (not suggested as role credit)
   */
  function mapRole(baseIn, modsIn) {
    const b = norm(baseIn).replace(/[‐‑–]/g, '-');
    const flags = [];
    const ms = [];
    // Bracket details that are already used as an attribute or for the type
    // and are therefore not suggested as a role credit as well
    const consumed = new Set();
    let uncredited = false;
    for (const m of (modsIn || []).map(norm)) {
      if (['additional', 'guest', 'solo'].includes(m)) {
        flags.push(m);
        consumed.add(m);
      } else if (m === 'uncredited') {
        uncredited = true;
        consumed.add(m);
      } else {
        ms.push(m);
      }
    }
    // credit: true keeps the Discogs role as written as role credit (for roles without an exact MB type)
    const out = (types, extra = {}) => {
      const res = { types, level: 'recording', flags, primaryCands: [], notes: [], work: false, ...extra };
      res.credit = extra.credit === true ? String(baseIn || '').trim() : '';
      if (uncredited) res.notes = ['uncredited', ...res.notes];
      res.consumed = [...consumed];
      return res;
    };
    const has = (...xs) => {
      let hit = false;
      for (const m of ms) {
        if (xs.includes(m)) {
          consumed.add(m);
          hit = true;
        }
      }
      return hit;
    };
    const is = (re) => re.test(b);
    const withFlags = (...extra) => [...flags, ...extra];
    const engFlags = () => withFlags(
      ...(has('assistant') ? ['assistant'] : []),
      ...(has('associate') ? ['associate'] : []),
      ...(has('co') ? ['co'] : []),
      ...(has('executive') ? ['executive'] : []),
    );

    if (!b) return out([]);

    // Writing credits belong on works
    const wrk = { level: 'work', work: true };
    if (is(/^(written-by|written by|writer|songwriter|songwriters)$/)) return out(['writer', 'composer'], wrk);
    if (is(/^(composed by|composer|composition by|music by|music|score|score by|soundtrack)$/)) return out(['composer', 'writer'], wrk);
    if (is(/^(translated by|translation|translator|translations)$/)) return out(['translator'], wrk);
    if (is(/^(author|poetry by|poem by|story by|screenwriter|script by|created by)$/)) return out(['writer'], { ...wrk, credit: true });
    if (is(/^(lyrics by|lyricist|words by|text by|lyrics)$/)) return out(['lyricist', 'writer'], wrk);
    if (is(/^(libretto by|librettist)$/)) return out(['librettist', 'lyricist'], wrk);

    // Vocals
    if (is(/^(lead vocals?|lead vocalist)$/)) return out(['vocal'], { primaryCands: ['lead vocals'] });
    const range = b.match(/^(soprano|mezzo-soprano|alto|contralto|countertenor|tenor|baritone|bass-baritone|bass|treble) vocals?$/);
    if (range) return out(['vocal'], { primaryCands: [`${range[1]} vocals`] });
    if (is(/^solo vocals?$/)) return out(['vocal'], { flags: withFlags('solo') });
    if (is(/^(scat|yodeling|yodelling|humming|whistling|human beatbox|beatbox|vocal percussion|vocalese|toasting|overtone voice|joik|eefing|kakegoe|satsuma|caller|cantor|coro)$/)) {
      return out(['vocal'], { primaryCands: [b, 'other vocals'], credit: true });
    }
    if (is(/^(announcer|commentator|interviewee|interviewer|dialog|dialogue|read by|presenter|hosted by|host|compere|compère)$/)) {
      return out(['vocal'], { primaryCands: ['spoken vocals'], credit: true });
    }
    if (is(/^(backing vocals?|background vocals?|harmony vocals?|chorus|backing vocalist)$/)) return out(['vocal'], { primaryCands: ['background vocals'] });
    if (is(/^(choir|choir vocals?)$/)) return out(['vocal'], { primaryCands: ['choir vocals'] });
    if (is(/^(voice|narrator|spoken word|speech|spoken vocals?|voice actor)$/)) return out(['vocal'], { primaryCands: ['spoken vocals'] });
    if (is(/^guest$/)) return out(['performer'], { flags: withFlags('guest') });
    if (is(/^(rap|rapper|mc|rapping)$/)) return out(['vocal'], { primaryCands: ['rap', 'spoken vocals'] });
    if (is(/^(vocals?|vocalist|singer)$/)) {
      let cands = [];
      if (has('lead')) cands = ['lead vocals'];
      else if (has('backing', 'background', 'harmony')) cands = ['background vocals'];
      else if (has('choir')) cands = ['choir vocals'];
      return out(['vocal'], { primaryCands: cands });
    }
    if (is(/^featuring$/)) {
      return out(['performer', 'vocal'], {
        flags: withFlags('guest'),
        notes: ['featuring'],
      });
    }

    // Production
    if (is(/^(co-producer|co-produced by|coproducer)$/)) return out(['producer'], { flags: withFlags('co') });
    if (is(/^(executive-producer|executive producer|executive-produced by|executive produced by)$/)) return out(['producer'], { flags: withFlags('executive') });
    if (is(/^associate[- ]producer$/)) return out(['producer'], { flags: withFlags('associate') });
    if (is(/^assistant[- ]producer$/)) return out(['producer'], { flags: withFlags('assistant') });
    if (is(/^(compilation producer|reissue producer|recording supervisor|supervised by|supervisor|post production|post-production)$/)) {
      return out(['producer'], { level: is(/^(compilation|reissue)/) ? 'release' : 'recording', credit: true });
    }
    if (is(/^(producer|produced by|record producer)$/)) {
      return out(['producer'], {
        flags: withFlags(
          ...(has('co-producer', 'co') ? ['co'] : []),
          ...(has('executive', 'executive-producer') ? ['executive'] : []),
          ...(has('assistant') ? ['assistant'] : []),
          ...(has('associate') ? ['associate'] : []),
        ),
      });
    }

    // Engineering
    const engineer = is(/^(engineer|engineered by|engineering)$/);
    if (is(/^(overdubbed by|overdubs by)$/)) return out(['recording', 'engineer'], { flags: engFlags(), credit: true });
    if (is(/^(tape op|tape operator|restoration|restored by|daw|technical assistance)$/)) return out(['engineer'], { flags: engFlags(), credit: true });
    if (is(/^(transferred by|transfer|audio transfer|cd transfer|digital transfer)$/)) return out(['transfer', 'engineer'], { level: 'release', flags: engFlags() });
    if (is(/^(direct metal mastering by|dmm cut by|dmm)$/)) return out(['mastering'], { level: 'release', flags: engFlags(), credit: true });
    if (is(/^(recorded by|recording|recording engineer|tracking|tracked by|tracking by)$/) || (engineer && has('recording', 'tracking'))) {
      return out(['recording', 'engineer'], { flags: engFlags() });
    }
    if (is(/^(dj mix|dj-mix|dj)$/)) return out(['mix-dj'], { level: 'release' });
    if (is(/^(mixed by|mixing|mix engineer|mixing engineer|mix)$/) || (engineer && has('mix', 'mixing'))) {
      return out(['mix'], { flags: engFlags() });
    }
    if (is(/^(mastered by|mastering|mastering engineer)$/) || (engineer && has('mastering'))) {
      return out(['mastering'], { level: 'release', flags: engFlags() });
    }
    if (is(/^(pre-?mastered by|pre-?mastering|pre-?master)$/)) return out(['mastering'], { level: 'release', flags: withFlags('pre') });
    if (is(/^(remastered by|remastering|remaster)$/)) {
      return out(['mastering'], { level: 'release', flags: withFlags('re') });
    }
    if (is(/^(lathe cut by|lathe cut)$/)) return out(['lacquer cut'], { level: 'release', credit: true });
    if (is(/^(lacquer cut by|lacquer cut|cut by|cutting engineer|lacquer cutting)$/)) {
      return out(['lacquer cut'], { level: 'release' });
    }
    if (is(/^(sound engineer|sound)$/) || (engineer && has('sound'))) return out(['sound', 'engineer'], { flags: engFlags() });
    if (is(/^(sound designer|sound design|sound effects|sfx)$/)) return out(['sound effects', 'engineer'], { level: 'release', credit: !is(/^sound effects$/) });
    if (is(/^balance engineer$/) || (engineer && has('balance'))) return out(['balance', 'engineer'], { flags: engFlags() });
    if (is(/^audio engineer$/) || (engineer && has('audio'))) return out(['audio', 'engineer'], { flags: engFlags() });
    if (engineer) return out(['engineer'], { flags: engFlags() });
    if (is(/^(remix|remixed by|remixer|remix by)$/)) return out(['remixer']);
    if (is(/^(programmed by|programming|programmer|drum programming|programmed|sequenced by)$/)) return out(['programming']);
    // "Editor" on Discogs is an editorial role at the record company; "Edited By" is audio editing.
    if (is(/^(edited by|editing|edited)$/)) return out(['editor']);
    if (is(/^(compiled by|compiler|compilation by|selected by)$/)) return out(['compiler'], { level: 'release' });
    if (is(/^(collected by|curated by)$/)) return out(['compiler'], { level: 'release', credit: true });
    if (is(/^beats$/)) return out(['programming', 'producer'], { credit: true });

    // Arrangement, conducting, ensembles
    if (is(/^(arranged by|arranger|arrangement|arrangements|arrangements by)$/)) {
      if (has('vocals', 'vocal', 'choir', 'backing vocals')) return out(['vocal arranger']);
      if (ms.length) {
        return out(['instrument arranger', 'arranger'], {
          primaryCands: uniq(ms.flatMap((m) => instrumentCandidates(m, []))),
        });
      }
      return out(['arranger']);
    }
    if (is(/^(adapted by|transcription by|transcribed by)$/)) return out(['arranger'], { credit: true });
    if (is(/^(instrumentation by)$/)) return out(['orchestrator', 'arranger'], { credit: true });
    if (is(/^(orchestrated by|orchestration|orchestrator)$/)) return out(['orchestrator']);
    if (is(/^(conductor|conducted by)$/)) return out(['conductor']);
    if (is(/^(music director|musical director|directed by)$/)) return out(['conductor'], { credit: true });
    if (is(/^(chorus master|choirmaster|choir master|chorus director|choir director)$/)) return out(['chorus master']);
    if (is(/^(concertmaster|concertmistress)$/)) return out(['concertmaster']);
    if (is(/^(orchestra|performing orchestra)$/)) return out(['performing orchestra', 'orchestra']);
    if (is(/^(performer|musician|performed by|band|ensemble|accompanied by|backing band)$/)) return out(['performer']);
    if (is(/^(instruments|multi-instrumentalist|all instruments|instrumentation)$/)) return out(['instrument']);

    // Artwork and packaging (typically release level)
    const rel = { level: 'release' };
    if (is(/^(photography by|photography|photographer|photos by|photo|photos|photograph by|cover photo)$/)) return out(['photography'], rel);
    if (is(/^(graphic design|graphics|graphic designer)$/)) return out(['graphic design', 'design'], rel);
    if (is(/^(typography|lettering|logo|calligraphy|desk-top publishing|desktop publishing|realization|realisation)$/)) return out(['graphic design', 'design'], { ...rel, credit: true });
    if (is(/^(design concept)$/)) return out(['design'], { ...rel, credit: true });
    if (is(/^(drawing|drawings by)$/)) return out(['illustration'], { ...rel, credit: true });
    if (is(/^(film director|video director|director)$/)) return out(['video director'], rel);
    if (is(/^(design|designed by|design by|layout|cover design|sleeve design|package design|packaging)$/)) return out(['design', 'design/illustration', 'graphic design'], rel);
    if (is(/^(illustration|illustrated by|illustrations|drawings|painting|paintings|cover illustration)$/)) return out(['illustration', 'design/illustration'], rel);
    if (is(/^(artwork|artwork by|cover|cover art|sleeve|art)$/)) return out(['artwork', 'design/illustration'], rel);
    if (is(/^(art direction|art director|art directed by)$/)) return out(['art direction'], rel);
    if (is(/^(creative direction|creative director)$/)) return out(['creative direction', 'art direction'], { ...rel, credit: true });
    if (is(/^(liner notes|sleeve notes|notes|linernotes)$/)) return out(['liner notes'], rel);
    if (is(/^(booklet editor|booklet)$/)) return out(['booklet editor'], rel);
    if (is(/^(a&r|a & r|a&r direction|a&r coordinator)$/)) return out(['artists and repertoire', 'misc'], rel);

    // Miscellaneous
    if (is(/^(field recording|field recordings|field recordist)$/)) return out(['field recordist']);
    if (is(/^(technician|instrument technician|guitar technician|piano technician|drum technician|keyboard technician|tech|tuner|piano tuner)$/)) {
      return out(['instrument technician'], { credit: is(/^(tuner|piano tuner)$/) });
    }
    if (is(/^booking$/)) return out(['booking'], rel);
    if (is(/^(legal|lawyer|legal representation)$/)) return out(['legal representation'], rel);
    if (is(/^(coordinator|co-ordinator|coordination|co-ordination|production coordinator|project coordinator)$/)) return out(['production coordinator'], { ...rel, credit: !is(/^production coordinator$/) });
    if (is(/^(copyright|copyright \(c\))$/)) return out(['copyright'], rel);
    if (is(/^(phonographic copyright|phonographic copyright \(p\))$/)) return out(['phonographic copyright'], rel);
    if (is(/^(published by|publisher|publishing)$/)) return out(['publishing'], rel);
    if (is(/^(licensed from|licensor)$/)) return out(['licensor'], rel);
    if (is(/^audio director$/)) return out(['audio director'], rel);
    // Roles without an MB relationship type: added as "misc" with the Discogs role as task
    if (is(/^(management|management by|manager|other|crew|road crew|stage crew|tour manager|product manager|project manager|promotion|marketing|merchandising|public relations|administrator|advisor|consultant|music consultant|vocal coach|concept|concept by|research|editor|commissioned by|contractor|copyist|cadenza|musical assistance|leader|band leader|repetiteur|répétiteur|score editor|authoring|equipment|instrument builder|luthier|lathe designer|plated by|abridged by|adapted by \(text\)|choreography|dramaturge|music librarian|proofreader|animation|assemblage|camera operator|cameraman|cgi artist|cinematographer|costume designer|director of photography|film editor|film producer|film technician|filmed by|footage by|gaffer|grip|hair|image editor|lighting|lighting director|lithography|make-up|makeup|model|production manager|scenographer|screen printing|set designer|stage manager|stylist|video editor|video producer|video technician|videography|vj)$/)) {
      return out(['misc'], { ...rel, notes: ['misc'], credit: true });
    }

    // Everything else is treated as an instrument; if MB has no such instrument, the row becomes "misc" (see makeRow)
    return out(['instrument'], { primaryCands: instrumentCandidates(b, ms), fallback: true });
  }

  /**
   * Remaining bracket details = alternative designation according to Discogs.
   * Details that are already used (additional, Recording …) or contained in the
   * chosen instrument name (Guitar [Electric] → electric guitar) are not suggested.
   */
  /**
   * Discogs details (bracket parts) that stand for an MB yes/no attribute,
   * e.g. "Mastered By [Remaster]" → "re". MB's own attribute names are the targets.
   */
  const DETAIL_FLAGS = [
    [/^additional(ly)?$/, 'additional'],
    [/^guest$/, 'guest'],
    [/^solo(ist)?$/, 'solo'],
    [/^(assistant|assisted by|asst\.?)$/, 'assistant'],
    [/^associate$/, 'associate'],
    [/^co-?$/, 'co'],
    [/^executive$/, 'executive'],
    [/^re-?master(ed|ing)?$/, 're'],
    [/^pre-?master(ed|ing)?$/, 'pre'],
    [/^sub-?publish(er|ing|ed)?$/, 'sub'],
    [/^(translation|translated( by)?|translator)$/, 'translator'],
  ];

  function flagForDetail(detail) {
    const d = norm(detail).replace(/[‐‑–]/g, '-');
    const hit = DETAIL_FLAGS.find(([re]) => re.test(d));
    return hit ? hit[1] : '';
  }

  /**
   * Fixed role credits: MB names some instruments differently from how they are credited.
   * Used only when Discogs gives no detail in brackets: "Drums" → MB "drums (drum set)" credited as "drums",
   * while "Drums [Brushes]" keeps "Brushes".
   */
  const FIXED_ROLE_CREDITS = [
    { base: 'drums', instrument: 'drums (drum set)', credit: 'drums' },
  ];

  function fixedRoleCredit(base, primaryName) {
    const hit = FIXED_ROLE_CREDITS.find((f) => norm(base) === f.base && norm(primaryName) === f.instrument);
    return hit ? hit.credit : '';
  }

  function suggestRoleCredit(mods, consumed, primaryName) {
    const primary = ` ${norm(primaryName)} `;
    const used = new Set((consumed || []).map(norm));
    return (mods || []).filter((m) => {
      const n = norm(m);
      return n && !used.has(n) && !primary.includes(` ${n} `);
    }).join(', ');
  }

  /** Options for the role credit field: everything exactly as written on Discogs. */
  function roleCreditOptions(raw, base, mods, suggestion) {
    const out = [];
    const push = (x) => {
      const t = String(x || '').trim();
      if (t && !out.includes(t)) out.push(t);
    };
    push(suggestion);
    push((mods || []).join(', '));
    (mods || []).forEach(push);
    (mods || []).forEach((m) => push(`${m} ${base}`));
    push(raw);
    return out;
  }

  /** Escapes a phrase for use inside double quotes in a Lucene query. */
  // --- Companies, etc. ------------------------------------------------------------

  /** Discogs "Companies, etc." → one entry per company with all of its roles. */
  function collectCompanies(release) {
    const byKey = new Map();
    for (const c of (release && release.companies) || []) {
      const role = String(c.entity_type_name || '').trim();
      if (!role || !c.name) continue;
      const key = c.id ? `id:${c.id}` : `name:${norm(c.name)}`;
      if (!byKey.has(key)) {
        byKey.set(key, { dId: Number(c.id) || 0, name: cleanDiscogsName(c.name), rawName: c.name, roles: [] });
      }
      const g = byKey.get(key);
      if (!g.roles.some((r) => norm(r.role) === norm(role))) g.roles.push({ role, catno: String(c.catno || '').trim() });
    }
    return [...byKey.values()];
  }

  /**
   * Discogs company roles → MB relationship types, per MB entity type. Discogs lists studios,
   * pressing plants and rights holders all as "labels"; in MB they are labels or places.
   */
  const COMPANY_ROLES = [
    [/^phonographic copyright/, { label: ['phonographic copyright'], artist: ['phonographic copyright'], level: 'release' }],
    [/^copyright/, { label: ['copyright'], artist: ['copyright'], level: 'release' }],
    [/^licensed from/, { label: ['licensor'], artist: ['licensor'], level: 'release' }],
    [/^licensed (to|through)/, { label: ['licensee'], artist: ['licensee'], level: 'release' }],
    [/^marketed by/, { label: ['marketed'], level: 'release' }],
    [/^distributed (by|through)/, { label: ['distributed'], level: 'release' }],
    [/^exported by/, { label: ['exported'], level: 'release' }],
    [/^promoted by/, { label: ['promoted'], level: 'release' }],
    [/^manufactured for/, { label: ['manufactured for'], level: 'release' }],
    [/^(manufactured|made) (by|at)/, { label: ['manufactured'], place: ['manufactured at'], level: 'release' }],
    [/^printed by/, { label: ['printed'], level: 'release' }],
    [/^pressed (by|at)/, { label: ['pressed'], place: ['pressed at'], level: 'release' }],
    [/^glass mastered (by|at)/, { label: ['glass mastered'], place: ['glass mastered at'], level: 'release' }],
    [/^lacquer cut (by|at)/, { place: ['lacquer cut at'], artist: ['lacquer cut'], level: 'release' }],
    [/^mastered (by|at)/, { label: ['mastering'], place: ['mastered at'], artist: ['mastering'], level: 'release' }],
    [/^mastered for/, { label: ['mastered for'], level: 'release' }],
    [/^remixed at/, { place: ['remixed at'], level: 'recording' }],
    [/^mixed at/, { place: ['mixed at'], level: 'recording' }],
    [/^mixed by/, { label: ['mix'], artist: ['mix'], level: 'release' }],
    [/^recorded by/, { artist: ['recording'], level: 'recording' }],
    [/^mixed for/, { label: ['mixed for'], level: 'release' }],
    [/^(recorded|overdubbed) at/, { place: ['recorded at'], level: 'recording' }],
    [/^engineered at/, { place: ['engineered at'], level: 'recording' }],
    [/^produced at/, { place: ['produced at'], level: 'recording' }],
    [/^produced for/, { label: ['produced for'], level: 'release' }],
    [/^edited at/, { place: ['edited at'], level: 'recording' }],
    [/^edited for/, { label: ['edited for'], level: 'release' }],
    [/^arranged for/, { label: ['arranged for'], level: 'release' }],
    [/^transferred at/, { place: ['transferred at'], level: 'release' }],
    [/^published by/, { label: ['publishing'], artist: ['publishing'], level: 'work' }],
    [/^rights society/, { label: ['rights society'], level: 'release' }],
    [/^designed (by|at)/, { label: ['design'], artist: ['design'], level: 'release' }],
    [/^artwork by/, { label: ['artwork'], artist: ['artwork'], level: 'release' }],
    [/^photography by/, { label: ['photography'], artist: ['photography'], level: 'release' }],
  ];

  /** Maps a Discogs company role. "prefer" is the MB entity type assumed until the company is matched. */
  function mapCompanyRole(role) {
    const r = norm(role);
    const hit = COMPANY_ROLES.find(([re]) => re.test(r));
    // "artist" is always allowed: persons also appear here, and their type can be chosen by hand.
    if (!hit) return { typeOptions: { label: ['misc'], artist: [] }, level: 'skip', prefer: 'label', notes: ['misc'] };
    const spec = hit[1];
    const typeOptions = {};
    if (spec.label) typeOptions.label = spec.label;
    if (spec.place) typeOptions.place = spec.place;
    typeOptions.artist = spec.artist || [];
    const prefer = spec.place && (!spec.label || / at$/.test(r)) ? 'place' : spec.label ? 'label' : 'artist';
    return { typeOptions, level: spec.level, prefer, notes: [] };
  }

  // --- Dates --------------------------------------------------------------------------

  const pad2d = (n) => String(n).padStart(2, '0');

  /** "1998", "1998-05", "1998-05-12", "12.05.1998", "05.1998", "5/1998" → { year, month, day } or null. */
  function parseDate(text) {
    const s = String(text || '').trim();
    let m;
    let parts;
    if ((m = s.match(/^(\d{4})(?:-(\d{1,2})(?:-(\d{1,2}))?)?$/))) parts = [m[1], m[2], m[3]];
    else if ((m = s.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/))) parts = [m[3], m[2], m[1]];
    else if ((m = s.match(/^(\d{1,2})[./](\d{4})$/))) parts = [m[2], m[1], null];
    else return null;
    const date = { year: Number(parts[0]), month: parts[1] ? Number(parts[1]) : null, day: parts[2] ? Number(parts[2]) : null };
    // Discogs writes unknown parts as "00"
    if (date.month === 0) date.month = null;
    if (date.day === 0 || date.month == null) date.day = null;
    if (date.year < 1000 || date.year > 2999) return null;
    if (date.month != null && date.month > 12) return null;
    if (date.day != null && date.day > new Date(Date.UTC(date.year, date.month, 0)).getUTCDate()) return null;
    return date;
  }

  const formatDate = (d) => (d ? [String(d.year), d.month ? pad2d(d.month) : '', d.month && d.day ? pad2d(d.day) : ''].filter(Boolean).join('-') : '');
  const compareDates = (a, b) => (a.year - b.year) || ((a.month || 0) - (b.month || 0)) || ((a.day || 0) - (b.day || 0));

  /** "1998-03-02 – 1998-03-20", or a single date when begin and end are the same. */
  function formatDateRange(entry) {
    const begin = formatDate(entry.begin);
    const end = entry.end ? formatDate(entry.end) : '';
    return end && end !== begin ? `${begin} – ${end}` : begin;
  }

  /**
   * Checks MB-style date fields (year, month, day as in MB's relationship dialog).
   * Returns { error: '' | 'begin' | 'end' | 'order', value: { begin, end, ended } | null }.
   */
  function partFromFields(y, m, d) {
    const [ys, ms, ds] = [y, m, d].map((x) => String(x == null ? '' : x).trim());
    if (!ys && !ms && !ds) return { ok: true, date: null };
    if (!/^\d{1,4}$/.test(ys) || Number(ys) < 1) return { ok: false };
    if ((ms && !/^\d{1,2}$/.test(ms)) || (ds && !/^\d{1,2}$/.test(ds)) || (ds && !ms)) return { ok: false };
    const date = { year: Number(ys), month: ms ? Number(ms) : null, day: ds ? Number(ds) : null };
    if (date.month != null && (date.month < 1 || date.month > 12)) return { ok: false };
    if (date.day != null && (date.day < 1 || date.day > new Date(Date.UTC(date.year, date.month, 0)).getUTCDate())) return { ok: false };
    return { ok: true, date };
  }

  function validateDateFields(f) {
    const begin = partFromFields(f.by, f.bm, f.bd);
    const end = partFromFields(f.ey, f.em, f.ed);
    if (!begin.ok) return { error: 'begin', value: null };
    if (!end.ok) return { error: 'end', value: null };
    if (begin.date && end.date && compareDates(end.date, begin.date) < 0) return { error: 'order', value: null };
    // As in MB: a relationship with an end date has ended.
    const ended = !!end.date || !!f.ended;
    if (!begin.date && !end.date && !ended) return { error: '', value: null };
    return { error: '', value: { begin: begin.date, end: end.date, ended } };
  }

  /**
   * Reads a date period as MusicBrainz displays it, e.g. "from 2015-01-26 until 2015-01-27", "in 2015-01",
   * "on 2015-01-26", "from 2015", "until 2015" or "from 2015 to ????" (also German, French and Spanish
   * wording). Returns { period: { begin, end, ended } } for such text, { single: date } for one plain
   * date, or null.
   */
  function parseDatePeriod(text) {
    let s = String(text || '').trim().toLowerCase().replace(/^\(|\)$/g, '').trim();
    s = s.replace(/\s+[–—-]\s+/g, ' until ');
    const tokenRe = /\d{4}(?:-\d{1,2}(?:-\d{1,2})?)?|\?{4}(?:-\?{2}(?:-\?{2})?)?/g;
    const tokens = [];
    let m;
    let last = 0;
    while ((m = tokenRe.exec(s))) {
      const before = s.slice(last, m.index).trim().split(/\s+/).pop() || '';
      tokens.push({ text: m[0], before });
      last = m.index + m[0].length;
    }
    if (!tokens.length || tokens.length > 2) return null;
    const rest = s.replace(tokenRe, ' ').replace(/\b(from|von|ab|du|desde|de|until|till|to|bis|au|hasta|a|on|in|am|im|le|en|el)\b/g, ' ').trim();
    if (rest) return null;
    const role = (w) => (/^(from|von|ab|du|desde|de)$/.test(w) ? 'begin' : /^(until|till|to|bis|au|hasta|a)$/.test(w) ? 'end'
      : /^(on|in|am|im|le|en|el)$/.test(w) ? 'both' : '');
    const read = (t) => (t.text.startsWith('?') ? { unknown: true } : { date: parseDate(t.text) });
    if (tokens.length === 1 && !tokens[0].before) {
      const r = read(tokens[0]);
      return r.date ? { single: r.date } : null;
    }
    let begin = null;
    let end = null;
    let ended = false;
    tokens.forEach((t, i) => {
      const r = read(t);
      if (!r.unknown && !r.date) begin = end = undefined;
      const kind = role(t.before) || (tokens.length === 2 ? (i === 0 ? 'begin' : 'end') : 'both');
      if (kind === 'begin' || kind === 'both') begin = begin === undefined ? undefined : (r.date || null);
      if (kind === 'end' || kind === 'both') {
        end = end === undefined ? undefined : (r.date || null);
        ended = true;
      }
    });
    if (begin === undefined || end === undefined) return null;
    if (begin && end && compareDates(end, begin) < 0) return null;
    if (!begin && !end && !ended) return null;
    return { period: { begin, end, ended } };
  }

  /** Date value → MB-style field strings. */
  function fieldsFromDate(v) {
    const part = (d, prefix) => ({
      [`${prefix}y`]: d ? String(d.year) : '',
      [`${prefix}m`]: d && d.month ? pad2d(d.month) : '',
      [`${prefix}d`]: d && d.day ? pad2d(d.day) : '',
    });
    return { ...part(v && v.begin, 'b'), ...part(v && v.end, 'e'), ended: !!(v && v.ended) };
  }

  /** "1998-03-02 – 1998-03-20", "1998", "– 1998-03-20" or "" (ended without dates). */
  function formatDateValue(v) {
    if (!v) return '';
    const b = formatDate(v.begin);
    const e = formatDate(v.end);
    if (b && e && b !== e) return `${b} – ${e}`;
    if (b) return e ? b : `${b} –`;
    return e ? `– ${e}` : '';
  }

  /** Finds relationship states by id anywhere in MB's editor state (its structure is internal). */
  function findRelationshipStates(root, ids, maxSteps = 400000) {
    const found = new Map();
    const seen = new Set();
    const stack = [root];
    let steps = 0;
    while (stack.length && steps < maxSteps && found.size < ids.size) {
      const v = stack.pop();
      steps++;
      if (!v || typeof v !== 'object' || seen.has(v)) continue;
      seen.add(v);
      if (typeof v.id === 'number' && ids.has(v.id) && 'linkTypeID' in v) {
        found.set(v.id, v);
        continue;
      }
      if (v instanceof Map || v instanceof Set) {
        v.forEach((x) => stack.push(x));
      } else if (Array.isArray(v)) {
        v.forEach((x) => stack.push(x));
      } else {
        Object.keys(v).forEach((k) => stack.push(v[k]));
      }
    }
    return found;
  }

  /** True if a relationship state in the editor carries the expected date. */
  function stateHasDate(state, expected) {
    const same = (a, b) => formatDate(a && a.year ? a : null) === formatDate(b || null);
    return same(state.begin_date, expected.begin) && same(state.end_date, expected.end) && !!state.ended === !!expected.ended;
  }

  /** Date suggestions from Discogs: ℗/© years in the notes. */
  function dateSuggestions(discogsRelease) {
    const out = [];
    const notes = String((discogsRelease && discogsRelease.notes) || '');
    const re = /(℗|©|\(p\)|\(c\))(?:\s*(?:&|and|\+)\s*(?:℗|©|\(p\)|\(c\)))?\s*(\d{4})/gi;
    let m;
    const seen = new Set();
    while ((m = re.exec(notes))) {
      const year = Number(m[2]);
      if (year < 1000 || seen.has(year)) continue;
      seen.add(year);
      out.push({ source: 'copyright', begin: { year, month: null, day: null }, category: 'copyright' });
    }
    return out;
  }

  const lucenePhrase = (text) => `"${String(text || '').replace(/[\\"]/g, '\\$&')}"`;

  /** Work search: title plus (optionally) the MBIDs of the known writers. */
  function buildWorkQuery(title, writerMbids) {
    const parts = [`work:${lucenePhrase(title)}`];
    const ids = uniq((writerMbids || []).filter(Boolean));
    if (ids.length) parts.push(`(${ids.map((id) => `arid:${id}`).join(' OR ')})`);
    return parts.join(' AND ');
  }

  /** Person or group, derived from the Discogs artist resource. */
  function guessArtistType(discogsArtist) {
    if (!discogsArtist) return null;
    if ((discogsArtist.members || []).length) return 'group';
    if ((discogsArtist.groups || []).length || discogsArtist.realname) return 'person';
    return null;
  }

  /**
   * Query parameters for the MB "Add artist" form (see MB wiki: Development/Seeding/Artist Editor).
   * rels: [{ mbid, linkTypeId, backward, ended }]
   */
  function buildArtistSeed({ name, discogsId, discogsArtist, typeId, discogsLinkTypeId, rels, editNote }) {
    const params = [['edit-artist.name', cleanDiscogsName((discogsArtist && discogsArtist.name) || name)]];
    if (typeId) params.push(['edit-artist.type_id', String(typeId)]);
    const urls = [];
    if (discogsId) urls.push({ text: discogsArtistUrl(discogsId), type: discogsLinkTypeId });
    for (const u of (discogsArtist && discogsArtist.urls) || []) {
      const text = String(u || '').trim();
      if (/^https?:\/\//i.test(text) && !urls.some((x) => x.text === text)) urls.push({ text });
    }
    urls.slice(0, 25).forEach((u, i) => {
      params.push([`edit-artist.url.${i}.text`, u.text]);
      if (u.type) params.push([`edit-artist.url.${i}.link_type_id`, String(u.type)]);
    });
    (rels || []).forEach((r, i) => {
      params.push([`rels.${i}.target`, r.mbid], [`rels.${i}.type`, String(r.linkTypeId)]);
      if (r.backward) params.push([`rels.${i}.backward`, '1']);
      if (r.ended) params.push([`rels.${i}.ended`, '1']);
    });
    if (editNote) params.push(['edit-artist.edit_note', editNote]);
    return params;
  }

  /**
   * Query parameters for the MB "Add work" form. Writers are artist→work relationships;
   * seen from the work they point backward (the artist is entity0).
   * writers: [{ mbid, linkTypeId, credit }]
   */
  function buildWorkSeed({ title, typeId, languageId, writers, editNote }) {
    const params = [['edit-work.name', title]];
    if (typeId) params.push(['edit-work.type_id', String(typeId)]);
    if (languageId) params.push(['edit-work.languages.0', String(languageId)]);
    (writers || []).forEach((w, i) => {
      params.push([`rels.${i}.target`, w.mbid], [`rels.${i}.type`, String(w.linkTypeId)], [`rels.${i}.backward`, '1']);
      if (w.credit) params.push([`rels.${i}.target_credit`, w.credit]);
    });
    if (editNote) params.push(['edit-work.edit_note', editNote]);
    return params;
  }

  const toQuery = (params) => params.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join('&');

  if (IS_NODE_TEST) {
    module.exports = {
      splitTopLevel, parseRoles, flattenDiscogsTracks, positionIndex, parseTrackSpec,
      collectCredits, instrumentCandidates, mapRole, cleanDiscogsName, suggestRoleCredit, roleCreditOptions,
      lucenePhrase, buildWorkQuery, guessArtistType, buildArtistSeed, buildWorkSeed, toQuery,
      tr, I18N, LANGS, setLang: (code) => { LANG = code; },
      collectCompanies, mapCompanyRole, fixedRoleCredit, flagForDetail, parseDate, formatDate, formatDateRange, compareDates, dateSuggestions,
      partFromFields, validateDateFields, fieldsFromDate, formatDateValue, findRelationshipStates, stateHasDate, parseDatePeriod,
    };
    return;
  }

  // ===========================================================================
  // 4. MusicBrainz access (web service and page internals)
  // ===========================================================================

  const releaseMbid = (location.pathname.match(MBID_RE) || [])[0];
  if (!releaseMbid) return;

  const pageWindow = typeof unsafeWindow !== 'undefined' ? unsafeWindow : window;
  const getMB = () => pageWindow.MB;

  // MB allows one request per second on average.
  let mbQueue = Promise.resolve();
  let lastMbRequest = 0;
  function mbWs(path) {
    const run = async () => {
      for (let attempt = 0; attempt < 4; attempt++) {
        const wait = lastMbRequest + 1100 - Date.now();
        if (wait > 0) await sleep(wait);
        lastMbRequest = Date.now();
        const url = `/ws/2/${path}${path.includes('?') ? '&' : '?'}fmt=json`;
        const res = await fetch(url, { headers: { Accept: 'application/json' } });
        if (res.status === 503) {
          await sleep(1500 * (attempt + 1));
          continue;
        }
        if (res.status === 404) return null;
        if (!res.ok) throw new Error(tr('err.mbHttp', { status: res.status }));
        return res.json();
      }
      throw new Error(tr('err.mbBusy'));
    };
    const p = mbQueue.then(run, run);
    mbQueue = p.catch(() => {});
    return p;
  }

  const entityCache = new Map();
  function fetchJsEntity(mbid) {
    if (!entityCache.has(mbid)) {
      const p = fetch(`/ws/js/entity/${mbid}`).then((res) => {
        if (!res.ok) throw new Error(tr('err.entity', { mbid, status: res.status }));
        return res.json();
      });
      p.catch(() => entityCache.delete(mbid));
      entityCache.set(mbid, p);
    }
    return entityCache.get(mbid);
  }

  async function fetchDiscogsArtist(id) {
    const res = await fetch(`https://api.discogs.com/artists/${id}`);
    if (res.status === 429) throw new Error(tr('err.discogsLimit'));
    if (!res.ok) throw new Error(tr('err.discogsHttp', { status: res.status }));
    return res.json();
  }

  async function searchWorks(title, writerMbids) {
    const run = async (query) => {
      const data = await mbWs(`work?query=${encodeURIComponent(query)}&limit=10`);
      return ((data && data.works) || []).map((w) => ({
        gid: w.id,
        title: w.title,
        type: w.type || '',
        disambiguation: w.disambiguation || '',
        score: w.score,
        writers: uniq((w.relations || [])
          .filter((r) => r['target-type'] === 'artist' && r.artist)
          .map((r) => `${r.artist.name} (${r.type})`)),
      }));
    };
    let results = await run(buildWorkQuery(title, writerMbids));
    // Without matches for title + writer, fall back to the title alone.
    if (!results.length && (writerMbids || []).length) results = await run(buildWorkQuery(title, []));
    return results;
  }

  // Work types and languages exactly as offered by MusicBrainz: first from the page data,
  // then from MB's own "Add work" form, finally from a short built-in list.
  const FALLBACK_WORK_TYPES = [
    [17, 'Song'], [1, 'Aria'], [25, 'Audio drama'], [2, 'Ballet'], [3, 'Cantata'], [4, 'Concerto'],
    [20, 'Étude'], [30, 'Incidental music'], [7, 'Madrigal'], [8, 'Mass'], [9, 'Motet'], [29, 'Musical'],
    [10, 'Opera'], [24, 'Operetta'], [11, 'Oratorio'], [12, 'Overture'], [13, 'Partita'], [28, 'Play'],
    [21, 'Poem'], [23, 'Prose'], [14, 'Quartet'], [5, 'Sonata'], [15, 'Song-cycle'], [22, 'Soundtrack'],
    [6, 'Suite'], [18, 'Symphonic poem'], [16, 'Symphony'], [19, 'Zarzuela'],
  ];
  const FALLBACK_LANGUAGES = [
    [486, '[No lyrics]', 'zxx'], [284, '[Multiple languages]', 'mul'], [120, 'English', 'eng'], [145, 'German', 'deu'],
    [134, 'French', 'fra'], [393, 'Spanish', 'spa'], [195, 'Italian', 'ita'], [340, 'Portuguese', 'por'],
    [113, 'Dutch', 'nld'], [403, 'Swedish', 'swe'], [100, 'Danish', 'dan'], [309, 'Norwegian', 'nor'],
    [131, 'Finnish', 'fin'], [338, 'Polish', 'pol'], [98, 'Czech', 'ces'], [176, 'Hungarian', 'hun'],
    [353, 'Russian', 'rus'], [433, 'Turkish', 'tur'], [159, 'Greek', 'ell'], [18, 'Arabic', 'ara'],
    [198, 'Japanese', 'jpn'], [224, 'Korean', 'kor'], [76, 'Chinese', 'zho'], [238, 'Latin', 'lat'],
  ];

  async function loadWorkOptions() {
    const le = getMB() && getMB().linkedEntities;
    let types = Object.values((le && le.work_type) || {});
    let languages = Object.values((le && le.language) || {});
    types = dedupeById(types).map((t) => ({ id: t.id, name: t.l_name || t.name }));
    languages = dedupeById(languages).map((l) => ({ id: l.id, name: l.l_name || l.name, iso: l.iso_code_3 || '', frequency: l.frequency || 0 }));
    if (!types.length || !languages.length) {
      try {
        const html = await (await fetch('/work/create')).text();
        const doc = new DOMParser().parseFromString(html, 'text/html');
        const read = (sel) => [...doc.querySelectorAll(`${sel} option`)]
          .filter((o) => o.value && /^\d+$/.test(o.value))
          .map((o) => ({ id: Number(o.value), name: o.textContent.trim() }));
        if (!types.length) types = read('select[name="edit-work.type_id"]');
        if (!languages.length) languages = read('select[name^="edit-work.languages"]');
      } catch (e) {
        console.warn('[Discogs-Credits] work form not readable', e);
      }
    }
    if (!types.length) types = FALLBACK_WORK_TYPES.map(([id, name]) => ({ id, name }));
    if (!languages.length) languages = FALLBACK_LANGUAGES.map(([id, name, iso]) => ({ id, name, iso, frequency: 2 }));
    types.sort((a, b) => a.name.localeCompare(b.name));
    languages.sort((a, b) => (b.frequency || 0) - (a.frequency || 0) || a.name.localeCompare(b.name));
    return { types, languages };
  }

  async function fetchDiscogsRelease(id) {
    const res = await fetch(`https://api.discogs.com/releases/${id}`);
    if (res.status === 429) throw new Error(tr('err.discogsLimit'));
    if (res.status === 404) throw new Error(tr('err.discogsMissing', { id }));
    if (!res.ok) throw new Error(tr('err.discogsHttp', { status: res.status }));
    return res.json();
  }

  /**
   * Looks up Discogs artist or label URLs in MB. Returns Map(url → [{ mbid, name, disambiguation, entityType }]).
   * Discogs "labels" can belong to MB labels or places (studios, pressing plants).
   */
  async function lookupDiscogsUrls(urls, kind = 'artist') {
    const qs = urls.map((u) => `resource=${encodeURIComponent(u)}`).join('&');
    // Discogs "labels" may be MB labels or places, and sometimes persons (MB artists).
    const targetTypes = kind === 'label' ? ['label', 'place', 'artist'] : ['artist'];
    const data = await mbWs(`url?${qs}&inc=${targetTypes.map((x) => `${x}-rels`).join('+')}`);
    let list = [];
    if (data && Array.isArray(data.urls)) list = data.urls;
    else if (data && data.resource) list = [data];
    const out = new Map();
    const idRe = kind === 'label' ? /discogs\.com\/label\/(\d+)/ : /discogs\.com\/artist\/(\d+)/;
    for (const u of list) {
      const idMatch = String(u.resource || '').match(idRe);
      if (!idMatch) continue;
      const seen = new Set();
      const found = [];
      for (const r of u.relations || []) {
        const et = r['target-type'];
        const e = targetTypes.includes(et) && r[et];
        if (!e || seen.has(e.id)) continue;
        seen.add(e.id);
        found.push({ mbid: e.id, name: e.name, disambiguation: e.disambiguation || '', entityType: et });
      }
      out.set(kind === 'label' ? discogsLabelUrl(idMatch[1]) : discogsArtistUrl(idMatch[1]), found);
    }
    return out;
  }

  const lookupDiscogsArtistUrls = (urls) => lookupDiscogsUrls(urls, 'artist');

  // --- Relationship types and attributes from MB.linkedEntities ---------------

  let IDX = null;
  const GROUPING_TYPES = new Set(['performance', 'remixes and compilations', 'production']);

  function dedupeById(values) {
    const map = new Map();
    for (const v of values) if (v && typeof v === 'object' && v.id != null && !map.has(v.id)) map.set(v.id, v);
    return [...map.values()];
  }

  function idx() {
    if (IDX) return IDX;
    const le = getMB() && getMB().linkedEntities;
    const lts = dedupeById(Object.values((le && le.link_type) || {}));
    const ats = dedupeById(Object.values((le && le.link_attribute_type) || {}));
    if (!lts.length || !ats.length) {
      throw new Error(tr('err.typesMissing'));
    }
    const ltById = new Map(lts.map((l) => [l.id, l]));
    const atById = new Map(ats.map((a) => [a.id, a]));
    const rootIdOf = (a) => {
      if (a.root_id != null) return a.root_id;
      let cur = a;
      const seen = new Set();
      while (cur && cur.parent_id != null && !seen.has(cur.id)) {
        seen.add(cur.id);
        cur = atById.get(cur.parent_id);
      }
      return cur ? cur.id : a.id;
    };
    const children = new Map();
    for (const a of ats) {
      const root = rootIdOf(a);
      if (root === a.id) continue;
      if (!children.has(root)) children.set(root, new Map());
      const key = norm(a.name);
      if (!children.get(root).has(key)) children.get(root).set(key, a);
    }
    // Instrument aliases as a second chance
    for (const a of ats) {
      const root = rootIdOf(a);
      if (root === a.id || !Array.isArray(a.instrument_aliases)) continue;
      for (const alias of a.instrument_aliases) {
        if (typeof alias !== 'string') continue;
        const key = norm(alias);
        if (!children.get(root).has(key)) children.get(root).set(key, a);
      }
    }
    // Relationship types per "<entity type>:<level>", e.g. "artist:recording", "place:release", "series:release"
    // or "recording:recording". MB orders entity0/entity1 alphabetically, so the level can be on either side.
    // Grouping entries (e.g. artist "performance", which has no description) cannot be chosen; URLs are
    // edited in the release editor, not here.
    const byLevel = {};
    for (const l of lts) {
      if (l.deprecated || l.type0 === 'url' || l.type1 === 'url') continue;
      if (GROUPING_TYPES.has(norm(l.name)) && !l.description) continue;
      for (const level of ['recording', 'release', 'work']) {
        const other = l.type1 === level ? l.type0 : l.type0 === level ? l.type1 : null;
        if (other) (byLevel[`${other}:${level}`] = byLevel[`${other}:${level}`] || []).push(l);
      }
    }
    Object.values(byLevel).forEach((list) => list.sort((x, y) => String(x.name).localeCompare(String(y.name))));
    const relatableTypes = uniq(Object.keys(byLevel).map((k) => k.split(':')[0]));
    const findLt = (type0, type1, name) => lts.find((l) => l.type0 === type0 && l.type1 === type1 && norm(l.name) === name) || null;
    IDX = {
      ltById, atById, children, byLevel, relatableTypes,
      performanceLt: findLt('recording', 'work', 'performance'),
      // Fallback IDs are the values currently used on musicbrainz.org.
      memberLtId: (findLt('artist', 'artist', 'member of band') || { id: 103 }).id,
      discogsArtistUrlLtId: (findLt('artist', 'url', 'discogs') || { id: 180 }).id,
      discogsUrlLtId: {
        label: (findLt('label', 'url', 'discogs') || { id: 217 }).id,
        place: (findLt('place', 'url', 'discogs') || { id: 705 }).id,
      },
    };
    return IDX;
  }

  const typesFor = (level, entityType = 'artist') => idx().byLevel[`${entityType}:${level}`] || [];

  function ltAttrConfig(lt) {
    const a = lt && lt.attributes;
    if (!a) return {};
    if (Array.isArray(a)) {
      const o = {};
      a.forEach((x) => { o[x.typeID != null ? x.typeID : x.id] = x; });
      return o;
    }
    return a;
  }

  function allowedRoots(lt) {
    return Object.keys(ltAttrConfig(lt))
      .map((id) => idx().atById.get(Number(id)))
      .filter(Boolean)
      .map((attr) => ({ attr, hasChildren: (idx().children.get(attr.id) || new Map()).size > 0 }));
  }

  const primaryRootOf = (lt) => (allowedRoots(lt).find((r) => r.hasChildren) || {}).attr || null;
  const findChildAttr = (rootId, name) => (idx().children.get(rootId) || new Map()).get(norm(name)) || null;

  /**
   * Where the role credit goes:
   * credit – "credited as" on the instrument or vocal attribute
   * text   – free-text attribute of the relationship type (usually "task" in MB)
   * note   – no matching field, edit note only
   */
  function roleCreditTarget(row, lt) {
    if (!lt || !String(row.roleCredit || '').trim()) return null;
    const root = primaryRootOf(lt);
    const primary = root && norm(row.primaryText) ? findChildAttr(root.id, row.primaryText) : null;
    if (primary && primary.creditable !== false) return { kind: 'credit', attr: primary };
    const free = allowedRoots(lt).filter((r) => r.attr.free_text).map((r) => r.attr);
    const text = free.find((a) => norm(a.name) === 'task') || free[0];
    if (text) return { kind: 'text', attr: text };
    return { kind: 'note' };
  }

  function buildAttrs(row, lt) {
    const attrs = [];
    const credit = String(row.roleCredit || '').trim();
    const target = roleCreditTarget(row, lt);
    const root = primaryRootOf(lt);
    const text = norm(row.primaryText);
    if (root && text) {
      const found = findChildAttr(root.id, text);
      if (!found) return { error: tr('issue.unknownAttr', { root: root.name, value: row.primaryText }) };
      const withCredit = target && target.kind === 'credit' && norm(credit) !== norm(found.name);
      attrs.push(withCredit ? { type: found, credited_as: credit } : { type: found });
    }
    for (const { attr, hasChildren } of allowedRoots(lt)) {
      if (hasChildren || attr.free_text) continue;
      if (row.flags.has(norm(attr.name))) attrs.push({ type: attr });
    }
    if (target && target.kind === 'text') attrs.push({ type: target.attr, text_value: credit });
    for (const [id, cfg] of Object.entries(ltAttrConfig(lt))) {
      if (cfg && Number(cfg.min) >= 1) {
        const rootId = Number(id);
        const ok = attrs.some(({ type: a }) => a.id === rootId || a.root_id === rootId || a.parent_id === rootId);
        if (!ok) return { error: tr('issue.requiredAttr', { name: (idx().atById.get(rootId) || {}).name || id }) };
      }
    }
    return { attrs, noteText: target && target.kind === 'note' ? credit : '' };
  }

  // --- Relationship editor internals -------------------------------------------

  function pageRecordings() {
    const mb = getMB();
    const out = new Map();
    const addTracks = (tracks) => (tracks || []).forEach((t) => {
      if (t && t.recording && t.recording.gid) out.set(t.recording.gid, t.recording);
    });
    let release = null;
    try {
      release = typeof mb.getSourceEntityInstance === 'function' ? mb.getSourceEntityInstance() : null;
    } catch (e) { /* ignore */ }
    release = release || (mb.relationshipEditor && mb.relationshipEditor.state && mb.relationshipEditor.state.entity);
    ((release && release.mediums) || []).forEach((m) => addTracks(m.tracks));
    const loaded = mb.relationshipEditor && mb.relationshipEditor.state && mb.relationshipEditor.state.loadedTracks;
    if (loaded && typeof loaded.forEach === 'function') loaded.forEach((tracks) => addTracks(tracks));
    return out;
  }

  let fallbackRelId = -100000;
  const partialDate = (d) => (d ? { year: d.year, month: d.month || null, day: d.day || null } : null);

  function dispatchAddRelationship(source, target, linkTypeID, attrs, credit, date = null, enteredFirst = false) {
    const mb = getMB();
    const re = mb.relationshipEditor;
    let attributes = null;
    if (attrs.length) {
      if (!mb.tree || typeof mb.tree.fromDistinctAscArray !== 'function') {
        throw new Error(tr('err.treeMissing'));
      }
      attributes = mb.tree.fromDistinctAscArray(
        [...attrs]
          .sort((a, b) => a.type.id - b.type.id)
          .map((a) => {
            const attr = { type: a.type, typeID: a.type.id, typeName: a.type.name };
            if (a.credited_as) attr.credited_as = a.credited_as;
            if (a.text_value != null) attr.text_value = a.text_value;
            return attr;
          }),
      );
    }
    // As in the MB code: the entity whose type sorts first alphabetically is entity0. For two entities of the
    // same type (recording–recording, release–release, work–work) the row's direction decides.
    const backward = source.entityType === target.entityType ? !!enteredFirst : source.entityType > target.entityType;
    const action = {
      type: 'update-relationship-state',
      sourceEntity: source,
      batchSelectionCount: null,
      creditsToChangeForSource: '',
      creditsToChangeForTarget: '',
      oldRelationshipState: null,
      newRelationshipState: {
        _lineage: [],
        _original: null,
        _status: 1, // 1 = add new relationship
        attributes,
        begin_date: date ? partialDate(date.begin) : null,
        editsPending: false,
        end_date: date ? partialDate(date.end) : null,
        ended: !!(date && date.ended),
        entity0: backward ? target : source,
        entity1: backward ? source : target,
        entity0_credit: backward ? credit : '',
        entity1_credit: backward ? '' : credit,
        id: typeof re.getRelationshipStateId === 'function' ? re.getRelationshipStateId() : fallbackRelId--,
        linkOrder: 0,
        linkTypeID,
      },
    };
    re.dispatch(action);
    return action.newRelationshipState;
  }

  // ===========================================================================
  // 5. State
  // ===========================================================================

  const S = {
    overlay: null,
    initialized: false,
    discogsLinks: [],
    discogsId: null,
    discogs: null,
    dTracks: [],
    mbTracks: [],
    existing: { exact: new Set(), loose: new Set() },
    artists: new Map(),
    rows: [],
    plan: [],
    appliedKeys: new Set(),
    noteLines: new Set(),
    // Works: planned recording→work links (track index → { gid, title, origin, flags })
    workPlan: new Map(),
    workSearch: new Map(),
    workOptions: null,
    workDefaults: { typeId: '', languageId: '' },
    workQueue: [],
    releaseLanguage: '',
    // Connection to the companion script for the Discogs tab
    sync: { installed: false, tabs: 0, target: null, last: '' },
    // How the Discogs tab follows the dashboard: 'click' or 'hover'
    syncMode: 'click',
    // Date pool: [{ id, name, begin, end, ended }], the pool form, and the active stamp
    datePool: [],
    poolForm: null,
    stampId: null,
    dateSuggestions: [],
    noteDates: new Map(),
    // UI state that survives a rebuild of the dashboard (e.g. after switching the language)
    messages: [],
    busy: null,
    launchStatus: null,
    onlyMissing: false,
    log: [],
    logEl: null,
    // Edit note: what the script did in this session
    noteStats: { recording: 0, release: 0, work: 0, workLinks: 0, newWorkLinks: 0 },
    noteDiscogsId: '',
    lastNoteBlock: '',
    panicMode: false,
    editNote: true,
    previewOpen: false,
    lastFocus: null,
  };

  const $ = (name) => S.overlay.querySelector(`[data-el="${name}"]`);

  function addExistingArtistRels(existing, targetGid, rels) {
    (rels || []).forEach((r) => {
      const et = r['target-type'];
      const e = et && et !== 'url' && (r[et] || r[et.replace('_', '-')]);
      if (!e) return;
      const values = r['attribute-values'] || {};
      const attrs = (r.attributes || []).map((a) => (values[a] != null ? `${norm(a)}=${norm(values[a])}` : norm(a))).sort().join(',');
      existing.exact.add(`${targetGid}|${e.id}|${r['type-id']}|${attrs}`);
      existing.loose.add(`${targetGid}|${e.id}|${r['type-id']}`);
    });
  }

  function indexExistingRelationships(ws) {
    const existing = { exact: new Set(), loose: new Set(), workLinks: new Set() };
    addExistingArtistRels(existing, releaseMbid, ws.relations);
    (ws.media || []).forEach((m) => (m.tracks || []).forEach((t) => {
      if (!t.recording) return;
      addExistingArtistRels(existing, t.recording.id, t.recording.relations);
      for (const r of t.recording.relations || []) {
        if (r['target-type'] !== 'work' || !r.work) continue;
        existing.workLinks.add(`${t.recording.id}|${r.work.id}`);
        addExistingArtistRels(existing, r.work.id, r.work.relations);
      }
    }));
    return existing;
  }

  /** Works of a track: already linked in MB plus a link planned in the dashboard. */
  function worksForTrack(i) {
    const t = S.mbTracks[i];
    if (!t) return [];
    const works = t.works.map((w) => ({ ...w, planned: false }));
    const planned = S.workPlan.get(i);
    if (planned && !works.some((w) => w.gid === planned.gid)) works.push({ ...planned, planned: true });
    return works;
  }

  function findRowType(row, level) {
    const byName = new Map(typesFor(level, row.entityType).map((l) => [norm(l.name), l]));
    for (const name of row.types) {
      const lt = byName.get(norm(name));
      if (lt) return lt;
    }
    return null;
  }

  function resolveRowType(row) {
    if (row.level === 'skip') return;
    let lt = findRowType(row, row.level);
    // Company roles: if MB has no such type on the suggested level, use a level where it exists.
    if (!lt && row.company && !row.levelTouched) {
      for (const level of ['release', 'recording', 'work']) {
        lt = findRowType(row, level);
        if (lt) {
          row.level = level;
          break;
        }
      }
    }
    row.linkTypeId = lt ? lt.id : null;
  }

  function currentLinkType(row) {
    if (row.level === 'skip' || !row.linkTypeId) return null;
    const lt = idx().ltById.get(row.linkTypeId);
    const fits = lt && ((lt.type0 === row.entityType && lt.type1 === row.level) || (lt.type1 === row.entityType && lt.type0 === row.level));
    return fits ? lt : null;
  }

  /**
   * Ticks the MB yes/no attributes that Discogs expresses in brackets, as far as the chosen relationship
   * type offers them. Details used this way are not suggested as role credit as well.
   */
  function applyDetailFlags(row) {
    const lt = currentLinkType(row);
    row.flagMods = new Set();
    if (!lt || !row.mods || !row.mods.length) return;
    const allowed = new Set(allowedRoots(lt).filter((r) => !r.hasChildren && !r.attr.free_text).map((r) => norm(r.attr.name)));
    for (const m of row.mods) {
      const flag = flagForDetail(m);
      if (flag && allowed.has(flag)) {
        row.flags.add(flag);
        row.flagMods.add(norm(m));
      }
    }
  }

  /** Role credit: bracket details first; roles kept as task come with their details; then fixed credits. */
  function roleCreditFor(row) {
    const details = suggestRoleCredit(row.mods, [...(row.consumed || []), ...(row.flagMods || [])], row.primaryText);
    if (row.creditFromRole) return details ? `${row.creditFromRole} [${details}]` : row.creditFromRole;
    return details || fixedRoleCredit(row.base, row.primaryText);
  }

  /** After the type changed: tick matching attributes and, unless edited by hand, refresh the role credit. */
  function refreshRowDetails(row) {
    applyDetailFlags(row);
    row.roleCreditSuggest = roleCreditFor(row);
    if (!row.roleCreditTouched) row.roleCredit = row.roleCreditSuggest;
  }

  /** Switches all rows of a company to the MB entity type it was matched with (label or place). */
  function setCompanyEntityType(company, entityType) {
    company.entityType = entityType;
    for (const row of S.rows) {
      if (row.artistKey !== company.key || !row.company) continue;
      row.entityType = entityType;
      row.types = row.typeOptions[entityType] || [];
      if (!row.levelTouched && row.level !== 'skip') row.level = row.defaultLevel;
      resolveRowType(row);
    }
  }

  /** The row's date as entered in its MB-style fields: { value, error }. */
  function rowDateInfo(row, lt) {
    if (!row.date || (lt && lt.has_dates === false)) return { value: null, error: '' };
    return validateDateFields(row.date);
  }

  function pickPrimary(row) {
    if (!row.primaryCands.length) return '';
    const lt = currentLinkType(row);
    const root = lt ? primaryRootOf(lt) : null;
    if (root) {
      for (const c of row.primaryCands) {
        const a = findChildAttr(root.id, c);
        if (a) return a.name;
      }
    }
    return row.primaryCands[0];
  }

  function primaryIsValid(row) {
    const lt = currentLinkType(row);
    const root = lt ? primaryRootOf(lt) : null;
    if (!root || !norm(row.primaryText)) return true;
    return !!findChildAttr(root.id, row.primaryText);
  }

  function makeRow(artistKey, { raw = '', base = '', mods = [], manual = false, anv = '', company = null } = {}) {
    let m;
    if (company) {
      const c = mapCompanyRole(raw);
      const entityType = company.entityType || c.prefer;
      m = {
        types: c.typeOptions[entityType] || [], level: c.level, notes: c.notes, work: c.level === 'work',
        consumed: [], primaryCands: [], flags: [], typeOptions: c.typeOptions, entityType,
      };
    } else {
      m = mapRole(base, mods);
    }
    const row = {
      id: nextId('r'),
      artistKey,
      company: !!company,
      entityType: m.entityType || 'artist',
      typeOptions: m.typeOptions || null,
      defaultLevel: m.level,
      date: null,       // MB-style fields { by, bm, bd, ey, em, ed, ended, poolId }
      dateOpen: false,
      manual,
      raw,
      base,
      mods,
      consumed: m.consumed,
      anv,
      roleCredit: '',
      roleCreditSuggest: '',
      roleCreditTouched: false,
      types: m.types,
      level: m.level,
      levelTouched: false,
      notes: m.notes,
      work: m.work,
      primaryCands: m.primaryCands,
      primaryText: '',
      flags: new Set(m.flags.map(norm)),
      credit: anv,
      linkTypeId: null,
      tracks: new Set(),
      suggested: new Set(),
      dSpec: '',
      dPositions: [],
      unresolved: [],
      tracksOpen: false,
    };
    row.creditFromRole = m.credit || '';
    resolveRowType(row);
    row.primaryText = pickPrimary(row);
    if (m.fallback && !primaryIsValid(row)) {
      // Not an MB instrument either: keep the role as "miscellaneous support" with the Discogs role as task.
      makeMiscRow(row, String(raw || base).replace(/\s*\[.*$/, '').trim());
    }
    refreshRowDetails(row);
    return row;
  }

  function computePlan() {
    const items = [];
    const rowInfo = new Map();
    const seen = new Set();

    // Planned recording→work links come first: work credits below depend on them.
    const perf = idx().performanceLt;
    for (const [i, plan] of S.workPlan) {
      const t = S.mbTracks[i];
      if (!t || !perf) continue;
      const attrs = allowedRoots(perf)
        .filter((r) => !r.hasChildren && !r.attr.free_text && plan.flags.has(norm(r.attr.name)))
        .map((r) => ({ type: r.attr }));
      const key = `link|${t.recordingGid}|${plan.gid}`;
      if (S.existing.workLinks.has(`${t.recordingGid}|${plan.gid}`) || S.appliedKeys.has(key) || seen.has(key)) continue;
      seen.add(key);
      items.push({
        kind: 'work-link', lt: perf, attrs, noteText: '', key, credit: '', workGid: plan.gid, workTitle: plan.title, origin: plan.origin,
        target: { kind: 'recording', gid: t.recordingGid, label: `${t.medium}.${t.number} ${t.title}`, order: t.idx, track: t },
      });
    }

    for (const row of S.rows) {
      const info = { issues: [], ready: 0, existing: 0, applied: 0, loose: 0, noWork: 0 };
      rowInfo.set(row.id, info);
      if (row.level === 'skip') continue;
      const artist = S.artists.get(row.artistKey);
      if (!artist || !artist.mbid) {
        const missing = row.company ? 'issue.missingCompany' : 'issue.missingArtist';
        info.issues.push(tr(artist && artist.status === 'pending' ? 'issue.searching' : missing));
      }
      const lt = currentLinkType(row);
      if (!lt) info.issues.push(tr('issue.chooseType'));
      if (rowDateInfo(row, lt).error) info.issues.push(tr('issue.badDate'));
      let attrs = [];
      let noteText = '';
      if (lt) {
        const r = buildAttrs(row, lt);
        if (r.error) info.issues.push(r.error);
        else ({ attrs, noteText } = r);
      }
      let targets = [];
      if (row.level === 'release') {
        targets = [{ kind: 'release', gid: releaseMbid, label: 'Release', order: -1 }];
      } else if (row.level === 'work') {
        const byGid = new Map();
        for (const i of [...row.tracks].sort((a, b) => a - b)) {
          const works = worksForTrack(i);
          if (!works.length) info.noWork++;
          for (const w of works) {
            if (!byGid.has(w.gid)) {
              byGid.set(w.gid, { kind: 'work', gid: w.gid, label: tr('preview.work', { title: w.title }), order: 10000 + i, track: S.mbTracks[i], work: w });
            }
          }
        }
        targets = [...byGid.values()];
        if (!row.tracks.size) info.issues.push(tr('issue.noTracks'));
        else if (!targets.length) info.issues.push(tr('issue.noWork'));
      } else {
        targets = [...row.tracks].sort((a, b) => a - b).map((i) => S.mbTracks[i]).filter(Boolean).map((t) => ({
          kind: 'recording', gid: t.recordingGid, label: `${t.medium}.${t.number} ${t.title}`, order: t.idx, track: t,
        }));
        if (!targets.length) info.issues.push(tr('issue.noTracks'));
      }
      if (info.issues.length) continue;
      const attrKey = attrs.map((a) => (a.text_value != null ? `${norm(a.type.name)}=${norm(a.text_value)}` : norm(a.type.name))).sort().join(',');
      for (const target of targets) {
        const key = `${target.gid}|${artist.mbid}|${lt.gid}|${attrKey}`;
        if (S.appliedKeys.has(key)) { info.applied++; continue; }
        if (S.existing.exact.has(key)) { info.existing++; continue; }
        if (S.existing.loose.has(`${target.gid}|${artist.mbid}|${lt.gid}`)) info.loose++;
        if (seen.has(key)) continue;
        seen.add(key);
        items.push({ kind: 'credit', row, artist, lt, attrs, noteText, target, key, credit: row.credit.trim(), date: rowDateInfo(row, lt).value });
        info.ready++;
      }
    }
    return { items, rowInfo };
  }

  // ===========================================================================
  // 6. Log, messages, edit note, registry of created works
  // ===========================================================================

  const LOG_KEY = `dci-log:${releaseMbid}`;
  const POOL_KEY = `dci-date-pool:${releaseMbid}`;
  const OLD_DATES_KEY = `dci-dates:${releaseMbid}`;
  const CREATED_KEY = `dci-created-works:${releaseMbid}`;
  const PANIC_KEY = `dci-panic:${releaseMbid}`;

  function readJson(area, key, fallback) {
    try {
      const value = window[area].getItem(key);
      return value ? JSON.parse(value) : fallback;
    } catch (e) {
      return fallback;
    }
  }

  function writeJson(area, key, value) {
    try {
      if (value == null || (Array.isArray(value) && !value.length)) window[area].removeItem(key);
      else window[area].setItem(key, JSON.stringify(value));
    } catch (e) { /* storage blocked or full */ }
  }

  // --- Log window ----------------------------------------------------------------

  S.log = readJson('sessionStorage', LOG_KEY, []);
  S.datePool = readJson('localStorage', POOL_KEY, null);
  if (!S.datePool) {
    // 0.5.x stored single dates as begin only; MB wants the same begin and end for a single day.
    S.datePool = readJson('localStorage', OLD_DATES_KEY, [])
      .filter((d) => d && d.id && d.begin)
      .map((d) => ({ id: d.id, name: d.label || '', begin: d.begin, end: d.end || d.begin, ended: true }));
    writeJson('localStorage', POOL_KEY, S.datePool.length ? S.datePool : null);
    writeJson('localStorage', OLD_DATES_KEY, null);
  }
  S.syncMode = readJson('localStorage', 'dci-sync-mode', 'click') === 'hover' ? 'hover' : 'click';

  const savePool = () => writeJson('localStorage', POOL_KEY, S.datePool.length ? S.datePool : null);

  const pad2 = (n) => String(n).padStart(2, '0');
  const clock = (ts) => {
    const d = new Date(ts);
    return `${pad2(d.getHours())}:${pad2(d.getMinutes())}:${pad2(d.getSeconds())}`;
  };
  const logText = (entry) => tr(`log.${entry.key}`, entry.params);
  const logItemHtml = (entry) => `<li class="dci-log-${entry.level}"><time>${clock(entry.ts)}</time> ${esc(logText(entry))}</li>`;

  /** Adds a step to the log window; entries are stored as keys, so they follow the language setting. */
  function log(level, key, params = {}) {
    const entry = { ts: Date.now(), level, key, params };
    S.log.push(entry);
    if (S.log.length > 400) S.log.splice(0, S.log.length - 400);
    writeJson('sessionStorage', LOG_KEY, S.log);
    if (S.logEl) {
      S.logEl.querySelector('ol').insertAdjacentHTML('beforeend', logItemHtml(entry));
      scrollLog();
    }
  }

  function scrollLog() {
    const list = S.logEl && S.logEl.querySelector('ol');
    if (list) list.scrollTop = list.scrollHeight;
  }

  function buildLogWindow() {
    const el = document.createElement('section');
    el.id = 'dci-log';
    el.hidden = true;
    el.setAttribute('aria-labelledby', 'dci-log-title');
    el.addEventListener('click', (e) => {
      const b = e.target.closest('[data-log-act]');
      if (!b) return;
      if (b.dataset.logAct === 'dashboard') {
        showDashboard();
      } else if (b.dataset.logAct === 'hide') {
        setLogVisible(false);
      } else if (b.dataset.logAct === 'clear') {
        S.log = [];
        writeJson('sessionStorage', LOG_KEY, S.log);
        renderLog();
      } else if (b.dataset.logAct === 'copy') {
        copyLog(b);
      }
    });
    document.body.appendChild(el);
    S.logEl = el;
    renderLog();
    applyScale();
    makeMovable(el, '.dci-log-head', 'log');
  }

  function renderLog() {
    if (!S.logEl) return;
    S.logEl.innerHTML = `
      <div class="dci-log-head">
        <h2 id="dci-log-title">${esc(tr('log.title'))}</h2>
        <button type="button" data-log-act="dashboard" class="dci-log-dash" title="${esc(tr('log.dashboardTitle'))}">${esc(tr('log.dashboard'))}</button>
        <button type="button" data-log-act="copy">${esc(tr('log.copy'))}</button>
        <button type="button" data-log-act="clear">${esc(tr('log.clear'))}</button>
        <button type="button" data-log-act="hide">${esc(tr('log.hide'))}</button>
      </div>
      <ol aria-live="polite">${S.log.map(logItemHtml).join('')}</ol>`;
    scrollLog();
  }

  function setLogVisible(visible) {
    if (!S.logEl) buildLogWindow();
    S.logEl.hidden = !visible;
    writeJson('localStorage', 'dci-log-open', visible);
    if (visible) {
      clampWindow(S.logEl);
      bringToFront('log');
      scrollLog();
    }
  }

  async function copyLog(button) {
    const text = S.log.map((e) => `${clock(e.ts)} ${logText(e)}`).join('\n');
    try {
      await navigator.clipboard.writeText(text);
    } catch (e) {
      const area = document.createElement('textarea');
      area.value = text;
      document.body.appendChild(area);
      area.select();
      document.execCommand('copy');
      area.remove();
    }
    button.textContent = tr('log.copied');
    setTimeout(() => { button.textContent = tr('log.copy'); }, 1500);
  }

  // --- Messages and progress in the dashboard ----------------------------------------

  function showMessage(kind, key, params = {}, { closeButton = false } = {}) {
    S.messages.push({ kind, key, params, closeButton });
    renderMessages();
  }

  function showError(e) {
    showMessage('error', 'raw', { text: e.message });
    log('error', 'error', { text: e.message });
    console.error('[Discogs-Credits]', e);
  }

  function clearMessages() {
    S.messages = [];
    renderMessages();
  }

  function renderMessages() {
    if (!S.overlay) return;
    $('msgs').innerHTML = S.messages.map((m) => `
      <div class="dci-msg dci-msg-${m.kind}">${esc(tr(m.key, m.params))}${m.closeButton
        ? ` <button type="button" class="dci-inline-btn" data-act="close">${esc(tr('msg.toEditor'))}</button>` : ''}</div>`).join('');
  }

  function setBusy(key, params = {}) {
    S.busy = key ? { key, params } : null;
    renderBusy();
  }

  function renderBusy() {
    if (!S.overlay) return;
    const el = $('busy');
    el.textContent = S.busy ? tr(S.busy.key, S.busy.params) : '';
    el.hidden = !S.busy;
  }

  function setLaunchStatus(key, params = {}) {
    S.launchStatus = { key, params };
    renderLauncher();
  }

  // --- Edit note ------------------------------------------------------------------------
  // Always English: edit notes are read by editors worldwide.

  function editNoteBlock() {
    const st = S.noteStats;
    const lines = [];
    const discogsId = S.discogsId || S.noteDiscogsId;
    if (discogsId) lines.push(`Source: https://www.discogs.com/release/${discogsId}`);
    lines.push(`Script: ${EDIT_NOTE_SCRIPT_NAME} v${VERSION} (userscript, ${SCRIPT_URL})`);
    const done = [];
    const credits = st.recording + st.release + st.work;
    if (credits) {
      const parts = [['recording', st.recording], ['release', st.release], ['work', st.work]]
        .filter(([, n]) => n).map(([level, n]) => `${n} ${level}`);
      done.push(`added ${credits} credit relationship${credits === 1 ? '' : 's'} from Discogs (${parts.join(', ')})`);
    }
    if (st.workLinks) {
      done.push(`linked ${st.workLinks} work${st.workLinks === 1 ? '' : 's'} to recordings${st.newWorkLinks ? ` (${st.newWorkLinks} newly created)` : ''}`);
    }
    if (done.length) lines.push(`Done: ${done.join('; ')}.`);
    if (S.noteDates.size) lines.push(`Dates entered in the dashboard: ${[...S.noteDates.values()].join('; ')}.`);
    if (S.noteLines.size) {
      lines.push('Not stored in MB (Discogs wording):');
      S.noteLines.forEach((l) => lines.push(`- ${l}`));
    }
    return lines.join('\n');
  }

  /** Writes the block into the edit note, replacing the block this script wrote before. */
  function writeEditNote() {
    const el = document.getElementById('edit-note-text') || document.querySelector('textarea[name$="edit_note"]');
    if (!el) return false;
    const block = editNoteBlock();
    const current = el.value;
    const next = S.lastNoteBlock && current.includes(S.lastNoteBlock)
      ? current.replace(S.lastNoteBlock, () => block)
      : (current.trim() ? `${current.replace(/\s+$/, '')}\n\n` : '') + block;
    S.lastNoteBlock = block;
    if (next !== current) {
      const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
      setter.call(el, next);
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }
    return true;
  }

  // --- Works created in this browser but not yet linked in MB ------------------------------
  // New works exist in MB right after their form is submitted. Until the link to the recording
  // is submitted too, they are kept here (per release), so they cannot be forgotten.

  const readCreatedWorks = () => readJson('localStorage', CREATED_KEY, []);

  function rememberCreatedWork(i, gid, title) {
    const list = readCreatedWorks().filter((x) => x.gid !== gid);
    list.push({ i, rec: S.mbTracks[i].recordingGid, gid, title, discogsId: S.discogsId || '', ts: Date.now() });
    writeJson('localStorage', CREATED_KEY, list);
  }

  /** Drops works that are linked in MB by now and restores the others as planned links. */
  function syncCreatedWorks() {
    const list = readCreatedWorks().filter((x) => {
      const track = S.mbTracks[x.i];
      return track && track.recordingGid === x.rec && !S.existing.workLinks.has(`${x.rec}|${x.gid}`);
    });
    writeJson('localStorage', CREATED_KEY, list);
    for (const x of list) {
      if (!S.workPlan.has(x.i)) S.workPlan.set(x.i, { gid: x.gid, title: x.title, origin: 'created', flags: new Set() });
    }
    if (!S.noteDiscogsId) S.noteDiscogsId = (list.find((x) => x.discogsId) || {}).discogsId || '';
    return list;
  }

  // --- Emergency reset --------------------------------------------------------------------
  // Reloading is the only reliable way to discard unsaved changes in MB's editor. The created
  // works survive in localStorage; after the reload only their links are staged again.

  function startPanic() {
    const n = readCreatedWorks().length;
    if (!n || !confirm(tr('panic.confirm', { n }))) return;
    log('warn', 'panic', { n });
    writeJson('sessionStorage', PANIC_KEY, Date.now());
    location.reload();
  }

  function waitForEditor(timeoutMs = 30000) {
    const ready = () => {
      const mb = getMB();
      return mb && mb.relationshipEditor && typeof mb.relationshipEditor.dispatch === 'function'
        && mb.relationshipEditor.state && mb.linkedEntities && Object.keys(mb.linkedEntities.link_type || {}).length;
    };
    return new Promise((resolve) => {
      const started = Date.now();
      const check = () => {
        if (ready() || Date.now() - started > timeoutMs) resolve();
        else setTimeout(check, 300);
      };
      check();
    });
  }

  async function resumePanicIfRequested() {
    const requested = readJson('sessionStorage', PANIC_KEY, 0);
    if (!requested) return;
    writeJson('sessionStorage', PANIC_KEY, null);
    if (Date.now() - requested > 120000) return;
    S.panicMode = true;
    await waitForEditor();
    await openDashboard();
    const n = await applyPlan({ only: (it) => it.kind === 'work-link' && it.origin === 'created' });
    log('ok', 'panicDone', { n });
    S.messages = S.messages.filter((m) => m.key !== 'msg.applied');
    showMessage('ok', 'panic.done', { n }, { closeButton: true });
  }

  // ===========================================================================
  // 7. Flow: load, resolve artists, apply
  // ===========================================================================

  async function init() {
    try {
      clearMessages();
      idx();
      renderDatalists();
      setBusy('busy.mb');
      log('info', 'start', { mbid: releaseMbid });
      const ws = await mbWs(`release/${releaseMbid}?inc=recordings+artist-rels+label-rels+place-rels+area-rels+event-rels+series-rels`
        + '+instrument-rels+recording-rels+release-rels+release-group-rels+work-rels+recording-level-rels+work-level-rels+url-rels');
      if (!ws) throw new Error(tr('err.releaseMissing'));
      S.mbTracks = [];
      (ws.media || []).forEach((m) => (m.tracks || []).forEach((track) => {
        const rels = (track.recording && track.recording.relations) || [];
        S.mbTracks.push({
          idx: S.mbTracks.length,
          medium: m.position,
          number: track.number || String(track.position),
          title: track.title,
          recordingGid: track.recording && track.recording.id,
          works: rels.filter((r) => r['target-type'] === 'work' && r.work).map((r) => ({
            gid: r.work.id,
            title: r.work.title,
            writers: uniq((r.work.relations || [])
              .filter((x) => x['target-type'] === 'artist' && x.artist)
              .map((x) => `${x.artist.name} (${x.type})`)),
          })),
        });
      }));
      S.existing = indexExistingRelationships(ws);
      S.releaseLanguage = (ws['text-representation'] && ws['text-representation'].language) || '';
      S.workOptions = await loadWorkOptions();
      const lang = S.workOptions.languages.find((l) => l.iso && l.iso === S.releaseLanguage);
      const song = S.workOptions.types.find((x) => norm(x.name) === 'song');
      S.workDefaults = { typeId: song ? String(song.id) : '', languageId: lang ? String(lang.id) : '' };
      const links = new Map();
      for (const r of ws.relations || []) {
        const m = r['target-type'] === 'url' && r.url && String(r.url.resource).match(/discogs\.com\/release\/(\d+)/);
        if (m && !links.has(m[1])) links.set(m[1], { id: m[1], url: r.url.resource });
      }
      S.discogsLinks = [...links.values()];
      S.initialized = true;
      renderDates();
      const created = syncCreatedWorks();
      log('info', 'mbLoaded', {
        n: S.mbTracks.length,
        works: S.mbTracks.filter((x) => x.works.length).length,
        links: S.discogsLinks.length,
      });
      renderSource();
      renderWorks();
      renderPanic();
      $('manual').hidden = false;
      setBusy('');
      if (created.length && !S.panicMode) {
        showMessage('warn', 'msg.pendingWorks', { n: created.length });
        log('warn', 'pendingWorks', { n: created.length });
      }
      if (S.panicMode) return;
      if (S.discogsLinks.length === 1) {
        await loadDiscogs(S.discogsLinks[0].id);
      } else if (!S.discogsLinks.length) {
        showMessage('info', 'msg.noDiscogsLink');
      } else {
        showMessage('info', 'msg.multiLinks', { n: S.discogsLinks.length });
      }
    } catch (e) {
      setBusy('');
      showError(e);
    }
  }

  async function loadDiscogs(id) {
    if (S.rows.length && !confirm(tr('msg.confirmDiscard'))) {
      renderSource();
      return;
    }
    try {
      clearMessages();
      setBusy('busy.discogs', { id });
      const d = await fetchDiscogsRelease(id);
      S.discogsId = String(id);
      S.discogs = d;
      S.dTracks = flattenDiscogsTracks(d.tracklist);
      S.artists = new Map();
      S.rows = [];
      renderSource();

      if (S.dTracks.length !== S.mbTracks.length) {
        showMessage('warn', 'msg.trackMismatch', { d: S.dTracks.length, m: S.mbTracks.length });
        log('warn', 'trackMismatch', { d: S.dTracks.length, m: S.mbTracks.length });
      }

      for (const g of collectCredits(d, S.dTracks, positionIndex(S.dTracks))) {
        const artist = {
          key: nextId('a'), dId: g.dId, name: g.name, rawName: g.rawName, status: 'pending',
          mbid: null, mbName: '', candidates: [], editing: false, error: '',
          anvs: uniq([...g.roles.values()].map((c) => c.anv).filter(Boolean)),
        };
        S.artists.set(artist.key, artist);
        for (const c of g.roles.values()) {
          const row = makeRow(artist.key, { raw: c.role.raw, base: c.role.base, mods: c.role.mods, anv: c.anv });
          row.dSpec = c.specs.join(', ');
          row.dPositions = c.positions;
          row.unresolved = c.unresolved;
          const suggested = c.allTracks
            ? S.mbTracks.map((x) => x.idx)
            : [...c.indexes].filter((i) => i < S.mbTracks.length);
          row.suggested = new Set(suggested);
          row.tracks = new Set(suggested);
          S.rows.push(row);
        }
      }
      for (const g of collectCompanies(d)) {
        const company = {
          key: nextId('c'), dId: g.dId, name: g.name, rawName: g.rawName, status: 'pending', company: true,
          entityType: null, mbid: null, mbName: '', candidates: [], editing: false, error: '', anvs: [],
        };
        S.artists.set(company.key, company);
        for (const r of g.roles) {
          const row = makeRow(company.key, { raw: r.role, company });
          row.tracks = new Set(S.mbTracks.map((x) => x.idx));
          row.suggested = new Set(row.tracks);
          if (r.catno) row.dSpec = r.catno;
          S.rows.push(row);
        }
      }
      S.dateSuggestions = dateSuggestions(d);
      log('info', 'discogsLoaded', { id, artists: S.artists.size, n: S.rows.length });

      $('toolbar').hidden = !S.rows.length;
      if (!S.rows.length) showMessage('info', 'msg.noCredits');
      renderDates();
      renderGroups();
      renderWorks();
      refresh();

      if (S.artists.size) {
        setBusy('busy.artists');
        await resolveArtists();
      }
      setBusy('');
    } catch (e) {
      setBusy('');
      showError(e);
    }
  }

  async function resolveArtists() {
    const pending = [...S.artists.values()].filter((a) => a.status === 'pending');
    for (const a of pending.filter((x) => !x.dId)) {
      a.status = 'missing';
      updateGroupHeader(a);
      log('warn', 'artistMissing', { name: a.name });
    }
    const urlOf = (a) => (a.company ? discogsLabelUrl(a.dId) : discogsArtistUrl(a.dId));
    const byUrl = new Map(pending.filter((a) => a.dId).map((a) => [urlOf(a), a]));
    const found = new Map();
    for (const kind of ['artist', 'label']) {
      const urls = [...byUrl.keys()].filter((u) => u.includes(`/${kind}/`));
      for (let i = 0; i < urls.length; i += 50) {
        const chunk = urls.slice(i, i + 50);
        try {
          (await lookupDiscogsUrls(chunk, kind)).forEach((v, k) => found.set(k, v));
        } catch (e) {
          // If the batch lookup fails, look up URLs one by one
          for (const u of chunk) {
            try {
              (await lookupDiscogsUrls([u], kind)).forEach((v, k) => found.set(k, v));
            } catch (e2) {
              console.warn('[Discogs-Credits]', u, e2);
            }
          }
        }
      }
    }
    for (const [url, a] of byUrl) {
      a.candidates = found.get(url) || [];
      if (a.company) {
        // Only MB labels or places that fit at least one of this company's roles
        const usable = new Set(S.rows.filter((r) => r.artistKey === a.key).flatMap((r) => Object.keys(r.typeOptions || {})));
        a.candidates = a.candidates.filter((c) => usable.has(c.entityType));
      }
      if (a.candidates.length === 1) {
        a.status = 'linked';
        a.mbid = a.candidates[0].mbid;
        a.mbName = a.candidates[0].name;
        if (a.company) setCompanyEntityType(a, a.candidates[0].entityType);
        log('ok', 'artistLinked', { name: a.name, mb: a.mbName });
      } else if (a.candidates.length > 1) {
        a.status = 'ambiguous';
        log('warn', 'artistAmbiguous', { name: a.name, n: a.candidates.length });
      } else {
        a.status = 'missing';
        log('warn', 'artistMissing', { name: a.name });
      }
      if (a.company) rerenderGroup(a);
      else updateGroupHeader(a);
    }
    refresh();
  }

  async function setArtistManually(artist, value) {
    const mbid = (String(value || '').match(MBID_RE) || [])[0];
    if (!mbid) {
      artist.error = tr('msg.badMbid');
      updateGroupHeader(artist);
      return;
    }
    try {
      const e = await fetchJsEntity(mbid.toLowerCase());
      if (artist.other) {
        if (String(e.entityType).replace('-', '_') !== artist.entityType) throw new Error(tr('msg.wrongEntityType', { type: tr(`entity.${artist.entityType}`) }));
      } else if (artist.company) {
        const usable = e.entityType === 'artist' || S.rows.some((r) => r.artistKey === artist.key && r.typeOptions && r.typeOptions[e.entityType]);
        if (!usable) throw new Error(tr('msg.notCompany'));
      } else if (e.entityType !== 'artist') {
        throw new Error(tr('msg.notArtist'));
      }
      Object.assign(artist, { mbid: e.gid || mbid, mbName: e.name, status: 'manual', editing: false, error: '' });
      if (artist.company) setCompanyEntityType(artist, e.entityType);
      log('ok', 'artistManual', { name: artist.name, mb: e.name });
    } catch (err) {
      artist.error = err.message;
    }
    if (artist.company) rerenderGroup(artist);
    else updateGroupHeader(artist);
    refresh();
  }

  async function addManualEntry() {
    const entityInput = S.overlay.querySelector('[data-f="manual-artist"]');
    const roleInput = S.overlay.querySelector('[data-f="manual-role"]');
    const errEl = $('manual-err');
    errEl.textContent = '';
    const mbid = (entityInput.value.match(MBID_RE) || [])[0];
    if (!mbid) {
      errEl.textContent = tr('msg.badMbidAny');
      return;
    }
    try {
      const e = await fetchJsEntity(mbid.toLowerCase());
      const et = String(e.entityType || '').replace('-', '_');
      if (et === 'url') throw new Error(tr('msg.urlNotHere'));
      if (!idx().relatableTypes.includes(et)) throw new Error(tr('msg.noRelTypes', { type: tr(`entity.${et}`) }));
      const gid = e.gid || mbid.toLowerCase();
      const company = et === 'label' || et === 'place';
      const other = !company && et !== 'artist';
      let owner = [...S.artists.values()].find((a) => a.mbid === gid && (a.entityType || 'artist') === et);
      if (!owner) {
        owner = {
          key: nextId(company ? 'c' : other ? 'o' : 'a'), dId: 0, name: e.name, rawName: '', status: 'manual', manual: true,
          company, other, entityType: company || other ? et : undefined, mbid: gid, mbName: e.name,
          candidates: [], editing: false, error: '', anvs: [],
        };
        S.artists.set(owner.key, owner);
      }
      const row = makeRow(owner.key, { manual: true, company: company ? owner : null });
      if (company || other) row.entityType = et;
      if (other) Object.assign(row, { other: true, types: [], typeOptions: null, notes: [] });
      applyRoleText(row, roleInput.value);
      row.tracks = new Set(S.mbTracks.map((x) => x.idx));
      row.suggested = new Set(row.tracks);
      S.rows.push(row);
      renderGroups();
      log('info', 'manualAdded', { name: e.name, role: row.raw || '–' });
      $('toolbar').hidden = false;
      entityInput.value = '';
      roleInput.value = '';
      roleInput.setAttribute('list', 'dci-dl-roles-artist');
      refresh();
      const added = S.overlay.querySelector(`tr[data-row="${row.id}"]`);
      if (added) added.scrollIntoView({ block: 'nearest' });
    } catch (err) {
      errEl.textContent = err.message;
    }
  }

  function describeItem(it) {
    if (it.kind === 'work-link') return `${it.target.label} → ${it.workTitle} (${it.lt.name})`;
    const date = it.date ? ` [${formatDateValue(it.date) || tr('date.endedOnly')}]` : '';
    return `${it.artist.mbName || it.artist.name}: ${it.lt.name} → ${it.target.label}${date}`;
  }

  /**
   * Reads the staged relationships back from MB's editor state and checks their dates.
   * MB updates its exposed state after rendering, so this waits a moment first.
   */
  async function verifyStagedDates(staged) {
    if (!staged.length) return;
    await new Promise((r) => setTimeout(r, 400));
    const mb = getMB();
    const state = mb && mb.relationshipEditor && mb.relationshipEditor.state;
    const found = findRelationshipStates(state, new Set(staged.map((x) => x.id)));
    if (!found.size) {
      log('warn', 'datesUnverifiable');
      return;
    }
    const wrong = staged.filter((x) => found.has(x.id) && !stateHasDate(found.get(x.id), x.date));
    if (wrong.length) {
      const list = wrong.slice(0, 5).map((x) => x.text).join('; ') + (wrong.length > 5 ? ' …' : '');
      log('error', 'datesMismatch', { n: wrong.length, list });
      showMessage('error', 'msg.datesMismatch', { n: wrong.length, list });
    } else {
      log('ok', 'datesVerified', { n: found.size });
    }
  }

  /** Stages the planned relationships in MB's editor. Returns how many were added. */
  async function applyPlan({ only = null } = {}) {
    const mb = getMB();
    const re = mb && mb.relationshipEditor;
    if (!re || typeof re.dispatch !== 'function' || !re.state) {
      showMessage('error', 'msg.editorNotReady');
      log('error', 'editorNotReady');
      return 0;
    }
    let { items } = computePlan();
    if (only) items = items.filter(only);
    if (!items.length) return 0;
    const applyBtn = S.overlay.querySelector('[data-act="apply"]');
    applyBtn.disabled = true;
    clearMessages();
    setBusy('busy.apply', { n: items.length });
    log('info', 'applyStart', { n: items.length });

    const recordings = pageRecordings();
    const release = re.state.entity;
    let added = 0;
    const notLoaded = new Map();
    const errors = [];
    const stagedDates = [];

    for (const it of items) {
      const text = describeItem(it);
      try {
        let source = null;
        if (it.target.kind === 'release') {
          source = release;
        } else {
          // Recordings (and the works below them) only exist in the editor once their medium is loaded.
          const recording = recordings.get(it.target.track.recordingGid);
          if (!recording) {
            notLoaded.set(it.target.track.medium, (notLoaded.get(it.target.track.medium) || 0) + 1);
            log('warn', 'skippedNotLoaded', { text });
            continue;
          }
          if (it.target.kind === 'recording') {
            source = recording;
          } else {
            const rel = (recording.relationships || []).find((r) => r.target && r.target.gid === it.target.gid);
            source = rel ? rel.target : await fetchJsEntity(it.target.gid);
          }
        }
        const targetEntity = await fetchJsEntity(it.kind === 'work-link' ? it.workGid : it.artist.mbid);
        const newState = dispatchAddRelationship(source, targetEntity, it.lt.id, it.attrs, it.credit, it.date, !!(it.row && it.row.enteredFirst));
        if (it.date) {
          const pool = it.row.date && S.datePool.find((d) => d.id === it.row.date.poolId);
          const dateText = formatDateValue(it.date) || 'ended';
          S.noteDates.set(pool ? pool.id : dateText, pool && pool.name ? `${pool.name} ${dateText}` : dateText);
          if (newState && typeof newState.id === 'number') stagedDates.push({ id: newState.id, date: it.date, text });
        }
        S.appliedKeys.add(it.key);
        if (it.kind === 'work-link') {
          S.noteStats.workLinks++;
          if (it.origin === 'created') S.noteStats.newWorkLinks++;
        } else {
          S.noteStats[it.target.kind]++;
        }
        if (it.noteText) {
          S.noteLines.add(`${it.artist.mbName || it.artist.name}, ${it.lt.name}: "${it.noteText}" (Discogs: ${it.row.raw})`);
        }
        added++;
        log('ok', 'staged', { text });
      } catch (e) {
        errors.push(`${text}: ${e.message}`);
        log('error', 'error', { text: `${text}: ${e.message}` });
        console.error('[Discogs-Credits]', e);
      }
    }
    renderWorks();
    await verifyStagedDates(stagedDates);

    let noteOk = true;
    if (added && S.editNote) {
      noteOk = writeEditNote();
      if (noteOk) log('info', 'noteWritten');
    }
    setBusy('');

    if (added) {
      showMessage('ok', 'msg.applied', { n: added }, { closeButton: true });
      setLaunchStatus('launcher.status', { n: S.appliedKeys.size });
    }
    if (notLoaded.size) {
      showMessage('warn', 'msg.notLoaded', {
        n: [...notLoaded.values()].reduce((x, y) => x + y, 0),
        media: [...notLoaded.keys()].join(', '),
      });
    }
    if (errors.length) {
      showMessage('error', 'msg.errors', { n: errors.length, list: `${errors.slice(0, 5).join('; ')}${errors.length > 5 ? ' …' : ''}` });
    }
    if (!noteOk) {
      showMessage('warn', 'msg.noteMissing');
      log('warn', 'noteMissing');
    }
    refresh();
    $('body').scrollTop = 0;
    const focusTarget = $('msgs').querySelector('button') || S.overlay.querySelector('.dci-close');
    focusTarget.focus();
    return added;
  }

  // ===========================================================================
  // 8. Rendering
  // ===========================================================================

  function roleDatalists() {
    return idx().relatableTypes.map((et) => `<datalist id="dci-dl-roles-${et}">${mbTypeNames(et).map((n) => `<option value="${esc(n)}"></option>`).join('')}</datalist>`).join('');
  }

  function renderDatalists() {
    const roots = new Set();
    for (const level of ['recording', 'release', 'work']) {
      for (const lt of typesFor(level)) {
        const r = primaryRootOf(lt);
        if (r) roots.add(r.id);
      }
    }
    $('datalists').innerHTML = roleDatalists() + [...roots].map((rootId) => {
      const names = uniq([...(idx().children.get(rootId) || new Map()).values()].map((a) => a.name)).sort((a, b) => a.localeCompare(b));
      return `<datalist id="dci-dl-${rootId}">${names.map((n) => `<option value="${esc(n)}"></option>`).join('')}</datalist>`;
    }).join('');
  }

  function renderSource() {
    if (!S.overlay) return;
    const el = $('source');
    const current = S.discogsId
      ? `<a href="https://www.discogs.com/release/${esc(S.discogsId)}" target="_blank" rel="noopener">${esc(tr('source.current', { title: (S.discogs && S.discogs.title) || 'Discogs', id: S.discogsId }))}</a>`
      : `<span>${esc(tr('source.none'))}</span>`;
    const picker = S.discogsLinks.length > 1
      ? `<select data-f="discogs-pick" aria-label="${esc(tr('source.pick'))}">
          <option value="">${esc(tr('source.pick'))}</option>
          ${S.discogsLinks.map((l) => `<option value="${esc(l.id)}" ${l.id === S.discogsId ? 'selected' : ''}>Discogs ${esc(l.id)}</option>`).join('')}
        </select>`
      : '';
    el.innerHTML = `${current} ${picker}
      <span class="dci-other">
        <input type="text" data-f="discogs-input" placeholder="${esc(tr('source.other'))}" aria-label="${esc(tr('source.other'))}">
        <button type="button" data-act="discogs-load">${esc(tr('source.load'))}</button>
      </span>`;
  }

  /** MB entity types a company can be matched with, from the roles it has. */
  const companyTypes = (a) => uniq(S.rows.filter((r) => r.artistKey === a.key).flatMap((r) => Object.keys(r.typeOptions || {})))
    .filter((et) => et !== 'artist');

  const entityPath = (et) => String(et || 'artist').replace('_', '-');

  function matchHtml(a) {
    const searchType = a.other ? a.entityType : a.company ? (a.entityType || companyTypes(a)[0] || 'label') : 'artist';
    const searchUrl = `/search?query=${encodeURIComponent(a.name)}&type=${searchType}&method=indexed`;
    const createButtons = a.other ? '' : a.company
      ? companyTypes(a).map((et) => `<button type="button" data-act="company-create" data-et="${et}">${esc(tr(et === 'place' ? 'match.createPlace' : 'match.createLabel'))}</button>`).join(' ')
      : `<button type="button" data-act="artist-create">${esc(tr('match.create'))}</button>`;
    const editor = (labelKey) => `
      <span class="dci-badge dci-badge-bad">${esc(tr(labelKey))}</span>
      <input type="text" data-f="artist-input" placeholder="${esc(a.other ? tr('match.placeholderOther', { type: tr(`entity.${a.entityType}`) }) : tr(a.company ? 'match.placeholderCompany' : 'match.placeholder'))}" aria-label="${esc(tr('match.inputAria', { name: a.name }))}">
      <button type="button" data-act="artist-set">${esc(tr('match.apply'))}</button>
      <a href="${esc(searchUrl)}" target="_blank" rel="noopener">${esc(tr('match.search'))}</a>
      ${a.company && !a.other ? `<a href="/search?query=${encodeURIComponent(a.name)}&type=artist&method=indexed" target="_blank" rel="noopener">${esc(tr('match.searchArtist'))}</a>` : ''}
      ${createButtons}
      ${a.mbid ? `<button type="button" class="dci-textbtn" data-act="artist-cancel">${esc(tr('common.cancel'))}</button>` : ''}
      ${a.error ? `<div class="dci-err">${esc(a.error)}</div>` : ''}`;

    if (a.status === 'pending') return `<span class="dci-badge">${esc(tr('match.searching'))}</span>`;
    if (a.editing) return editor('match.changeLabel');
    if (a.status === 'linked' || a.status === 'manual' || a.status === 'created') {
      const path = entityPath(a.company || a.other ? a.entityType : 'artist');
      return `<span class="dci-badge dci-badge-ok">${esc(tr(`match.${a.status}`))}</span>
        ${a.company || a.other ? `<span class="dci-sub">${esc(tr(`entity.${a.entityType}`))}</span>` : ''}
        <a href="/${esc(path)}/${esc(a.mbid)}" target="_blank" rel="noopener">${esc(a.mbName)}</a>
        <button type="button" class="dci-textbtn" data-act="artist-edit">${esc(tr('match.change'))}</button>`;
    }
    if (a.status === 'ambiguous') {
      return `<span class="dci-badge dci-badge-bad">${esc(tr('match.ambiguous'))}</span>
        <select data-f="artist-pick" aria-label="${esc(tr('match.pick'))}">
          <option value="">${esc(tr('match.pick'))}</option>
          ${a.candidates.map((c) => `<option value="${esc(c.mbid)}">${esc(c.name)}${c.disambiguation ? ` (${esc(c.disambiguation)})` : ''}${a.company ? ` – ${esc(tr(`entity.${c.entityType}`))}` : ''}</option>`).join('')}
        </select>`;
    }
    return editor(!a.dId ? 'match.noId' : a.company ? 'match.noLinkCompany' : 'match.noLink');
  }

  function artistVariants(a) {
    return uniq([...(a.anvs || []), a.name, a.mbName].map((x) => String(x || '').trim()).filter(Boolean));
  }

  function variantsHtml(a) {
    const anvs = a.anvs || [];
    let spelled = '';
    if (anvs.length) {
      spelled = `${esc(tr('group.spelling'))} ${anvs.map((v) => `<span class="dci-anv">${esc(tr('common.quoted', { text: v }))}</span>`).join(', ')}`;
    } else if (a.dId) {
      spelled = esc(tr('group.noVariant'));
    }
    return `${spelled ? `<span>${spelled}</span>` : ''}
      <label class="dci-credit">${esc(tr('group.creditAll'))}
        <input type="text" data-f="artist-credit-all" list="dci-ac-${a.key}" value="${esc(anvs.length === 1 ? anvs[0] : '')}"
          placeholder="${esc(tr('credit.placeholder'))}" aria-label="${esc(tr('group.creditAllAria', { name: a.name }))}">
      </label>
      <button type="button" data-act="artist-credit-all">${esc(tr('group.setAll'))}</button>
      <datalist id="dci-ac-${a.key}">${artistVariants(a).map((v) => `<option value="${esc(v)}"></option>`).join('')}</datalist>`;
  }

  function groupHtml(a) {
    const rows = S.rows.filter((r) => r.artistKey === a.key);
    const discogsLink = a.dId
      ? `<span class="dci-muted">Discogs:</span> <a href="${a.company ? discogsLabelUrl(a.dId) : discogsArtistUrl(a.dId)}" target="_blank" rel="noopener">${esc(a.rawName || a.name)}</a>`
      : '';
    return `
      <section class="dci-group dci-st-${a.status}" data-group="${a.key}">
        <div class="dci-ghead">
          <div class="dci-gname"><strong>${esc(a.name)}</strong> ${discogsLink}</div>
          <div class="dci-gmatch" data-match="${a.key}">${matchHtml(a)}</div>
        </div>
        ${a.company ? '' : `<div class="dci-variants" data-variants="${a.key}">${variantsHtml(a)}</div>`}
        <div class="dci-tablewrap">
          <table class="dci-table">
            <thead><tr>
              <th scope="col">${esc(tr('th.role'))}</th>
              <th scope="col">${esc(tr('th.type'))}</th>
              <th scope="col">${esc(tr('th.attrs'))}</th>
              <th scope="col">${esc(tr('th.level'))}</th>
              <th scope="col">${esc(tr('th.date'))}</th>
              <th scope="col">${esc(tr('th.tracks'))}</th>
            </tr></thead>
            <tbody>${rows.map(rowHtml).join('')}</tbody>
          </table>
        </div>
        <button type="button" class="dci-textbtn" data-act="add-role">${esc(tr('group.addRole', { name: a.name }))}</button>
      </section>`;
  }

  function roleCell(row) {
    const notes = (row.notes || []).map((k) => `<div class="dci-note">${esc(tr(`note.${k}`))}</div>`).join('');
    const asType = row.company || row.other ? `<div class="dci-sub">${esc(tr('role.asEntity', { type: tr(`entity.${row.entityType}`) }))}</div>` : '';
    if (row.manual) {
      return `<input type="text" data-f="role-text" list="dci-dl-roles-${esc(row.entityType)}" value="${esc(row.raw)}" placeholder="${esc(tr(row.company ? 'role.companyPlaceholder' : 'role.placeholder'))}" aria-label="${esc(tr('role.aria'))}">
        <button type="button" class="dci-textbtn" data-act="remove-row">${esc(tr('role.remove'))}</button>${asType}${notes}`;
    }
    if (row.company) {
      return `<div class="dci-drole">${esc(row.raw)}</div>
        <div class="dci-sub">${esc(tr('role.companyWhole'))}</div>
        ${row.dSpec ? `<div class="dci-sub">${esc(tr('role.catno', { catno: row.dSpec }))}</div>` : ''}${asType}${notes}`;
    }
    const where = [];
    if (row.dSpec) where.push(row.dSpec);
    if (row.dPositions.length) where.push(tr('role.tracks', { list: row.dPositions.join(', ') }));
    const roleHtml = esc(row.raw).replace(/\[[^\]]*\]/g, (m) => `<span class="dci-bracket">${m}</span>`);
    return `<div class="dci-drole">${roleHtml}</div>
      <div class="dci-sub">${esc(where.length ? tr('role.source', { where: where.join('; ') }) : tr('role.wholeRelease'))}</div>
      ${row.unresolved.length ? `<div class="dci-note dci-warn">${esc(tr('role.unresolved', { list: row.unresolved.join(', ') }))}</div>` : ''}
      ${notes}`;
  }

  /** A relationship as a sentence, using MB's long link phrase without attribute placeholders. */
  function phraseSentence(lt, e0, e1) {
    const raw = String(lt.long_link_phrase || lt.link_phrase || lt.name);
    const explicit = /\{entity[01]\}/.test(raw);
    const text = raw.replace(/\{entity0\}/g, '\u0000').replace(/\{entity1\}/g, '\u0001').replace(/\{[^{}]*\}/g, '')
      .replace(/\s+/g, ' ').trim().replace(/\u0000/g, e0).replace(/\u0001/g, e1);
    return explicit ? text : `${e0} ${text} ${e1}`;
  }

  function directionHtml(row, lt) {
    if (!lt || lt.type0 !== lt.type1) return '';
    const artist = S.artists.get(row.artistKey);
    const entered = artist ? artist.mbName || artist.name : '';
    const here = tr(`dir.${row.level}`);
    const option = (value, text) => `<option value="${value}" ${(value === 'entered') === !!row.enteredFirst ? 'selected' : ''}>${esc(text)}</option>`;
    return `<label class="dci-direction"><span class="dci-sub">${esc(tr('dir.label'))}</span>
      <select data-f="direction" aria-label="${esc(tr('dir.label'))}">
        ${option('this', phraseSentence(lt, here, entered))}${option('entered', phraseSentence(lt, entered, here))}
      </select></label>`;
  }

  function typeCell(row) {
    if (row.level === 'skip') return `<span class="dci-muted">${esc(tr('type.skipped'))}</span>`;
    const options = typesFor(row.level, row.entityType).map((l) => `<option value="${l.id}" ${l.id === row.linkTypeId ? 'selected' : ''}>${esc(l.name)}</option>`).join('');
    return `<select data-f="type" aria-label="${esc(tr('type.aria'))}">
        <option value="">${esc(tr('type.choose'))}</option>${options}
      </select>${directionHtml(row, currentLinkType(row))}`;
  }

  const markText = (row) => (primaryIsValid(row) ? (norm(row.primaryText) ? tr('mark.known') : '') : tr('mark.unknown'));

  /** MB's description of an attribute (HTML) as plain text for a tooltip. */
  const attrHelp = (attr) => String((attr && attr.description) || '').replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();

  function attrCell(row) {
    const lt = currentLinkType(row);
    if (!lt) return '';
    const parts = [];
    const root = primaryRootOf(lt);
    if (root) {
      const valid = primaryIsValid(row);
      parts.push(`<div class="dci-primary">
        <input type="text" data-f="primary" list="dci-dl-${root.id}" value="${esc(row.primaryText)}"
          class="${valid ? '' : 'dci-invalid'}" placeholder="${esc(tr('attr.optional', { name: root.name }))}" aria-label="${esc(root.name)}">
        <span class="dci-mark ${valid ? 'dci-ok' : 'dci-bad'}" data-mark="${row.id}" aria-live="polite">${esc(markText(row))}</span>
      </div>`);
    }
    const flags = allowedRoots(lt).filter((r) => !r.hasChildren && !r.attr.free_text);
    if (flags.length) {
      parts.push(`<div class="dci-flags">${flags.map(({ attr }) => `
        <label class="dci-check" title="${esc(attrHelp(attr))}"><input type="checkbox" data-f="flag" value="${esc(norm(attr.name))}" ${row.flags.has(norm(attr.name)) ? 'checked' : ''}> ${esc(attr.name)}</label>`).join('')}
      </div>`);
    }
    if (row.other) {
      const free = allowedRoots(lt).filter((r) => r.attr.free_text).map((r) => r.attr)[0];
      if (free) {
        parts.push(`<label class="dci-credit">${esc(free.name)}
          <input type="text" data-f="role-credit" value="${esc(row.roleCredit)}" aria-label="${esc(free.name)}" title="${esc(attrHelp(free))}">
        </label>`);
      }
    }
    if (row.company || row.other) {
      parts.push(`<label class="dci-credit">${esc(tr('credit.companyLabel'))}
        <input type="text" data-f="credit" value="${esc(row.credit)}" placeholder="${esc(tr('credit.placeholder'))}" aria-label="${esc(tr('credit.companyLabel'))}">
      </label>`);
      return parts.join('');
    }
    const options = roleCreditOptions(row.raw, row.base, row.mods, row.roleCreditSuggest);
    parts.push(`<label class="dci-credit">${esc(tr('roleCredit.label'))}
        <input type="text" data-f="role-credit" list="dci-rc-${row.id}" value="${esc(row.roleCredit)}" placeholder="${esc(tr('roleCredit.placeholder'))}" aria-label="${esc(tr('roleCredit.label'))}">
      </label>
      <datalist id="dci-rc-${row.id}">${options.map((o) => `<option value="${esc(o)}"></option>`).join('')}</datalist>
      <div class="dci-dest" data-dest="${row.id}">${esc(roleCreditHint(row))}</div>`);
    parts.push(`<label class="dci-credit">${esc(tr('artistCredit.label'))}
        <input type="text" data-f="credit" list="dci-ac-${row.artistKey}" value="${esc(row.credit)}" placeholder="${esc(tr('credit.placeholder'))}" aria-label="${esc(tr('artistCredit.label'))}">
      </label>`);
    return parts.join('');
  }

  function roleCreditHint(row) {
    const lt = currentLinkType(row);
    const target = lt && roleCreditTarget(row, lt);
    if (!target) return '';
    if (target.kind === 'credit') return tr('dest.credit', { name: target.attr.name });
    if (target.kind === 'text') return tr('dest.text', { name: target.attr.name });
    return tr(S.editNote ? 'dest.note' : 'dest.none');
  }

  function updateHint(row) {
    const el = S.overlay.querySelector(`[data-dest="${row.id}"]`);
    if (el) el.textContent = roleCreditHint(row);
  }

  function levelCell(row) {
    const btn = (level) => `<button type="button" data-act="level" data-level="${level}" aria-pressed="${row.level === level}">${esc(tr(`level.${level}`))}</button>`;
    return `<div class="dci-seg" role="group" aria-label="${esc(tr('th.level'))}">
      ${btn('recording')}${btn('release')}${btn('work')}${btn('skip')}
    </div>`;
  }

  const poolLabel = (d) => `${d.name || tr('date.untitled')} · ${formatDateValue(d) || tr('date.endedOnly')}`;
  const hasDateInput = (d) => (!!d && ['by', 'bm', 'bd', 'ey', 'em', 'ed'].some((k) => String(d[k] || '').trim() !== '')) || !!(d && d.ended);

  function dateErrorText(error) {
    return error ? tr(error === 'order' ? 'date.errOrder' : error === 'end' ? 'date.errEnd' : 'date.errBegin') : '';
  }

  /** MB-style date fields: year, month and day for begin and end, plus "ended". */
  function mbDateFields(prefix, v) {
    const input = (key, placeholder, label) => `<input type="text" inputmode="numeric" data-f="${prefix}-${key}" value="${esc(v[key] || '')}"
      placeholder="${placeholder}" size="${placeholder.length}" maxlength="${placeholder.length}" class="dci-dp dci-dp-${placeholder.length}" aria-label="${esc(label)}" title="${esc(tr('date.pasteTitle'))}">`;
    const line = (which) => {
      const label = tr(which === 'b' ? 'date.begin' : 'date.end');
      return `<div class="dci-mbdate-line"><span class="dci-mbdate-label">${esc(label)}</span>
        ${input(`${which}y`, 'YYYY', `${label} YYYY`)}-${input(`${which}m`, 'MM', `${label} MM`)}-${input(`${which}d`, 'DD', `${label} DD`)}
        ${which === 'e' ? `<button type="button" class="dci-iconbtn" data-act="${prefix}-copy" title="${esc(tr('date.copyTitle'))}" aria-label="${esc(tr('date.copyTitle'))}">⇣</button>` : ''}</div>`;
    };
    const endSet = String(v.ey || '').trim() !== '';
    return `${line('b')}${line('e')}
      <label class="dci-check dci-mbdate-ended"><input type="checkbox" data-f="${prefix}-ended" ${v.ended || endSet ? 'checked' : ''} ${endSet ? 'disabled' : ''}> ${esc(tr('date.ended'))}</label>`;
  }

  function dateCell(row) {
    if (row.level === 'skip') return '';
    const lt = currentLinkType(row);
    if (lt && lt.has_dates === false) return `<span class="dci-muted">${esc(tr('date.notAllowed'))}</span>`;
    const d = row.date;
    if (!row.dateOpen && !hasDateInput(d)) {
      return `<button type="button" class="dci-textbtn dci-date-add" data-act="date-open">${esc(tr('date.addRow'))}</button>`;
    }
    const info = rowDateInfo(row, lt);
    const pool = d && d.poolId && S.datePool.find((x) => x.id === d.poolId);
    return `<div class="dci-mbdate">
      ${mbDateFields('rd', d || {})}
      <div class="dci-mbdate-tools">
        ${S.datePool.length ? `<select data-f="rd-pool" aria-label="${esc(tr('date.fromPool'))}"><option value="">${esc(tr('date.fromPool'))}</option>
          ${S.datePool.map((x) => `<option value="${esc(x.id)}">${esc(poolLabel(x))}</option>`).join('')}</select>` : ''}
        <button type="button" class="dci-textbtn" data-act="date-to-pool">${esc(tr('date.toPool'))}</button>
        <button type="button" class="dci-textbtn" data-act="date-clear">${esc(tr('date.clear'))}</button>
      </div>
      ${pool ? `<div class="dci-sub">${esc(tr('date.fromPoolName', { name: pool.name || formatDateValue(pool) }))}</div>` : ''}
      <div class="dci-err" data-date-err="${row.id}" aria-live="polite">${esc(dateErrorText(info.error))}</div>
    </div>`;
  }

  /** Refreshes the error text and the "ended" box of a row's date while typing, without re-rendering it. */
  function updateDateUi(row) {
    const tr1 = S.overlay.querySelector(`tr[data-row="${row.id}"]`);
    if (!tr1 || !row.date) return;
    const err = tr1.querySelector(`[data-date-err="${row.id}"]`);
    if (err) err.textContent = dateErrorText(rowDateInfo(row, currentLinkType(row)).error);
    const box = tr1.querySelector('[data-f="rd-ended"]');
    if (box) {
      const endSet = String(row.date.ey || '').trim() !== '';
      box.disabled = endSet;
      box.checked = endSet || !!row.date.ended;
    }
  }

  function applyPoolToRow(row, entry) {
    const lt = currentLinkType(row);
    if (row.level === 'skip' || (lt && lt.has_dates === false)) return false;
    row.date = { ...fieldsFromDate(entry), poolId: entry.id };
    row.dateOpen = true;
    rerenderRow(row);
    return true;
  }

  // --- Date pool (sticky bar at the top of the dashboard) ------------------------------------

  const poolUsage = (id) => S.rows.filter((r) => r.date && r.date.poolId === id && r.level !== 'skip').length;

  function poolSuggestions() {
    const inPool = new Set(S.datePool.map((d) => formatDateValue(d)));
    return S.dateSuggestions.filter((x) => !inPool.has(formatDateValue({ begin: x.begin, end: x.begin, ended: true })));
  }

  /** Relationship types present in rows that can take a date, for "apply to all rows with type …". */
  function stampTypeOptions() {
    const counts = new Map();
    for (const row of S.rows) {
      const lt = row.level !== 'skip' && currentLinkType(row);
      if (!lt || lt.has_dates === false) continue;
      const key = norm(lt.name);
      counts.set(key, { name: lt.name, n: ((counts.get(key) || {}).n || 0) + 1 });
    }
    return [...counts.entries()].sort((a, b) => a[1].name.localeCompare(b[1].name));
  }

  function poolFormHtml() {
    const f = S.poolForm;
    return `<div class="dci-date-form dci-mbdate" role="group" aria-label="${esc(tr('date.formTitle'))}">
      <label class="dci-pool-name">${esc(tr('date.name'))} <input type="text" data-f="pf-name" value="${esc(f.name)}" placeholder="${esc(tr('date.namePlaceholder'))}" size="16"></label>
      ${mbDateFields('pf', f)}
      <div class="dci-mbdate-tools">
        <button type="button" class="dci-apply dci-small" data-act="pool-save">${esc(tr('date.save'))}</button>
        ${f.id ? `<button type="button" class="dci-textbtn" data-act="pool-remove">${esc(tr('date.remove'))}</button>` : ''}
        <button type="button" class="dci-textbtn" data-act="pool-cancel">${esc(tr('common.cancel'))}</button>
      </div>
      <div class="dci-err" aria-live="polite">${esc(f.error || '')}</div>
      <p class="dci-sub">${esc(tr('date.formHint'))}</p>
    </div>`;
  }

  function renderDates() {
    if (!S.overlay) return;
    const el = $('dates');
    el.hidden = !S.initialized;
    if (el.hidden) return;
    S.overlay.classList.toggle('dci-stamping', !!S.stampId);
    const stamp = S.stampId && S.datePool.find((d) => d.id === S.stampId);
    const chips = S.datePool.map((d) => `
      <span class="dci-date-chip ${S.stampId === d.id ? 'dci-active' : ''}">
        <button type="button" class="dci-chip-main" data-act="pool-stamp" data-id="${esc(d.id)}" aria-pressed="${S.stampId === d.id}" title="${esc(tr('date.stampTitle'))}">
          ${esc(poolLabel(d))} <span class="dci-chip-count">${esc(tr('date.used', { n: poolUsage(d.id) }))}</span></button>
        <button type="button" class="dci-iconbtn" data-act="pool-edit" data-id="${esc(d.id)}" title="${esc(tr('date.editEntry'))}" aria-label="${esc(tr('date.editEntry'))}">✎</button>
      </span>`).join('');
    const suggestions = poolSuggestions();
    const suggHtml = suggestions.length ? `<span class="dci-date-sugg"><span class="dci-sub">${esc(tr('date.suggestions'))}</span>
      ${suggestions.map((x) => `<button type="button" class="dci-textbtn" data-act="pool-suggest" data-year="${esc(String(x.begin.year))}">${esc(tr(`date.sugg.${x.source}`, { date: formatDate(x.begin) }))}</button>`).join(' ')}</span>` : '';
    const types = stampTypeOptions();
    const stampBar = stamp ? `<div class="dci-stamp-bar" role="status">
        <span>${esc(tr('date.stampActive', { date: poolLabel(stamp) }))}</span>
        <label>${esc(tr('date.stampAllType'))}
          <select data-f="stamp-type"><option value="*empty">${esc(tr('date.stampAllEmpty'))}</option>
            ${types.map(([key, t]) => `<option value="${esc(key)}">${esc(`${t.name} (${t.n})`)}</option>`).join('')}</select></label>
        <button type="button" data-act="stamp-apply">${esc(tr('date.stampApply'))}</button>
        <button type="button" class="dci-textbtn" data-act="stamp-end">${esc(tr('date.stampEnd'))}</button>
      </div>` : '';
    el.innerHTML = `<div class="dci-dates-bar">
        <strong>${esc(tr('date.title'))}</strong>
        ${chips}
        <button type="button" class="dci-textbtn" data-act="pool-new">${esc(tr('date.poolNew'))}</button>
        ${suggHtml}
      </div>
      ${stampBar}
      ${S.poolForm ? poolFormHtml() : ''}
      ${!S.datePool.length && !S.poolForm ? `<p class="dci-sub">${esc(tr('date.poolExplain'))}</p>` : ''}`;
  }

  function openPoolForm(entry = null, preset = null) {
    const v = entry || preset;
    S.poolForm = { id: entry ? entry.id : null, name: v ? v.name || '' : '', ...fieldsFromDate(v), error: '' };
    renderDates();
    const input = S.overlay.querySelector('[data-f="pf-by"]');
    if (input) input.focus();
  }

  function savePoolForm() {
    const f = S.poolForm;
    const res = validateDateFields(f);
    f.error = res.error ? dateErrorText(res.error) : !res.value ? tr('date.errEmpty') : '';
    if (f.error) {
      renderDates();
      return;
    }
    const entry = {
      id: f.id || `d${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`,
      name: f.name.trim(), ...res.value,
    };
    const i = S.datePool.findIndex((d) => d.id === entry.id);
    if (i >= 0) {
      S.datePool[i] = entry;
      const using = S.rows.filter((r) => r.date && r.date.poolId === entry.id);
      if (using.length && confirm(tr('date.updateRows', { n: using.length }))) {
        using.forEach((r) => { r.date = { ...fieldsFromDate(entry), poolId: entry.id }; });
      }
    } else {
      S.datePool.push(entry);
    }
    savePool();
    S.poolForm = null;
    log('info', 'dateSaved', { date: poolLabel(entry) });
    renderDates();
    renderGroups();
    refresh();
  }

  function removePoolEntry(id) {
    const d = S.datePool.find((x) => x.id === id);
    if (!d) return;
    S.datePool = S.datePool.filter((x) => x.id !== id);
    // Rows keep their values, only the reference to the pool entry goes.
    S.rows.forEach((r) => { if (r.date && r.date.poolId === id) r.date.poolId = null; });
    if (S.stampId === id) S.stampId = null;
    savePool();
    S.poolForm = null;
    log('info', 'dateRemoved', { date: poolLabel(d) });
    renderDates();
    renderGroups();
    refresh();
  }

  function stampApplyAll(typeKey) {
    const entry = S.datePool.find((d) => d.id === S.stampId);
    if (!entry) return;
    let n = 0;
    for (const row of S.rows) {
      const lt = row.level !== 'skip' && currentLinkType(row);
      if (!lt || lt.has_dates === false) continue;
      const match = typeKey === '*empty' ? !hasDateInput(row.date) : norm(lt.name) === typeKey;
      if (match && applyPoolToRow(row, entry)) n++;
    }
    log('info', 'dateApplied', { n, date: poolLabel(entry) });
    renderDates();
    refresh();
  }

  function tracksCell(row) {
    let main = '';
    if (row.level === 'recording' || row.level === 'work') {
      main = `<button type="button" class="dci-tbtn" data-act="tracks-toggle" aria-expanded="${row.tracksOpen}">
        <span data-tcount="${row.id}">${esc(tr('tracks.count', { sel: row.tracks.size, n: S.mbTracks.length }))}</span></button>`;
      if (row.level === 'work') main += `<div class="dci-sub">${esc(tr('tracks.worksOf'))}</div>`;
    } else if (row.level === 'release') {
      main = `<span class="dci-muted">${esc(tr('tracks.wholeRelease'))}</span>`;
    }
    return `${main}<div class="dci-status" data-status="${row.id}"></div>`;
  }

  function tracksPicker(row) {
    const multiMedium = new Set(S.mbTracks.map((x) => x.medium)).size > 1;
    let lastMedium = null;
    const chips = S.mbTracks.map((x) => {
      const head = multiMedium && x.medium !== lastMedium ? `<div class="dci-medium">${esc(tr('picker.medium', { n: x.medium }))}</div>` : '';
      lastMedium = x.medium;
      const dPos = S.dTracks[x.idx] ? S.dTracks[x.idx].position : '';
      return `${head}<label class="dci-chip ${row.suggested.has(x.idx) ? 'dci-sugg' : ''}" title="${esc(dPos ? tr('picker.dpos', { pos: dPos }) : tr('picker.noDpos'))}">
        <input type="checkbox" data-f="track" data-i="${x.idx}" ${row.tracks.has(x.idx) ? 'checked' : ''}>
        <span class="dci-tn">${esc(x.number)}</span> <span class="dci-tt">${esc(x.title)}</span>
      </label>`;
    }).join('');
    const legend = esc(tr('picker.legend')).replace('{dot}', '<span class="dci-dot"></span>');
    return `<div class="dci-picker">
      <div class="dci-picker-actions">
        <button type="button" data-act="tracks-all">${esc(tr('picker.all'))}</button>
        <button type="button" data-act="tracks-none">${esc(tr('picker.none'))}</button>
        <button type="button" data-act="tracks-invert">${esc(tr('picker.invert'))}</button>
        <button type="button" data-act="tracks-discogs">${esc(tr('picker.discogs'))}</button>
        <span class="dci-muted">${legend}</span>
      </div>
      <div class="dci-chips">${chips}</div>
    </div>`;
  }

  function rowHtml(row) {
    const open = row.tracksOpen && (row.level === 'recording' || row.level === 'work');
    return `
      <tr class="dci-row dci-lv-${row.level}" data-row="${row.id}">
        <td class="dci-c-role">${roleCell(row)}</td>
        <td class="dci-c-type">${typeCell(row)}</td>
        <td class="dci-c-attr">${attrCell(row)}</td>
        <td class="dci-c-level">${levelCell(row)}</td>
        <td class="dci-c-date">${dateCell(row)}</td>
        <td class="dci-c-tracks">${tracksCell(row)}</td>
      </tr>
      <tr class="dci-tracksrow" data-tracksrow="${row.id}" ${open ? '' : 'hidden'}>
        <td colspan="6">${tracksPicker(row)}</td>
      </tr>`;
  }

  function renderGroups() {
    const withRows = [...S.artists.values()].filter((a) => S.rows.some((r) => r.artistKey === a.key));
    $('groups').innerHTML = withRows.filter((a) => !a.company && !a.other).map(groupHtml).join('');
    const others = withRows.filter((a) => a.other);
    const oel = $('others');
    oel.hidden = !others.length;
    oel.innerHTML = others.length
      ? `<h3>${esc(tr('others.title'))}</h3><p class="dci-muted">${esc(tr('others.explain'))}</p>${others.map(groupHtml).join('')}`
      : '';
    const companies = withRows.filter((a) => a.company);
    const el = $('companies');
    el.hidden = !companies.length;
    el.innerHTML = companies.length
      ? `<h3>${esc(tr('companies.title'))}</h3><p class="dci-muted">${esc(tr('companies.explain'))}</p>${companies.map(groupHtml).join('')}`
      : '';
  }

  function rerenderGroup(a) {
    const section = S.overlay && S.overlay.querySelector(`[data-group="${a.key}"]`);
    if (!section) return;
    const tmp = document.createElement('div');
    tmp.innerHTML = groupHtml(a);
    section.replaceWith(tmp.firstElementChild);
  }

  function updateGroupHeader(a) {
    if (!S.overlay) return;
    const section = S.overlay.querySelector(`[data-group="${a.key}"]`);
    if (!section) return;
    section.className = `dci-group dci-st-${a.status}`;
    section.querySelector(`[data-match="${a.key}"]`).innerHTML = matchHtml(a);
    const list = section.querySelector(`#dci-ac-${a.key}`);
    if (list) list.innerHTML = artistVariants(a).map((v) => `<option value="${esc(v)}"></option>`).join('');
  }

  function rerenderRow(row) {
    const tr1 = S.overlay.querySelector(`tr[data-row="${row.id}"]`);
    const tr2 = S.overlay.querySelector(`tr[data-tracksrow="${row.id}"]`);
    if (!tr1 || !tr2) return;
    const tmp = document.createElement('tbody');
    tmp.innerHTML = rowHtml(row);
    const [n1, n2] = Array.from(tmp.children);
    tr1.replaceWith(n1);
    tr2.replaceWith(n2);
  }

  function updateTrackUi(row) {
    S.overlay.querySelectorAll(`tr[data-tracksrow="${row.id}"] input[data-f="track"]`).forEach((cb) => {
      cb.checked = row.tracks.has(Number(cb.dataset.i));
    });
    const count = S.overlay.querySelector(`[data-tcount="${row.id}"]`);
    if (count) count.textContent = tr('tracks.count', { sel: row.tracks.size, n: S.mbTracks.length });
  }

  function updateMark(row) {
    const valid = primaryIsValid(row);
    const mark = S.overlay.querySelector(`[data-mark="${row.id}"]`);
    const input = S.overlay.querySelector(`tr[data-row="${row.id}"] input[data-f="primary"]`);
    if (mark) {
      mark.className = `dci-mark ${valid ? 'dci-ok' : 'dci-bad'}`;
      mark.textContent = markText(row);
    }
    if (input) input.classList.toggle('dci-invalid', !valid);
  }

  /**
   * Rows whose relationships all exist in MB already are set to "Skip" once and highlighted.
   * They stay in the list; choosing a level again brings them back.
   */
  function autoSkipExisting() {
    const candidates = S.rows.filter((r) => !r.existingChecked && !r.levelTouched && r.level !== 'skip');
    if (!candidates.length) return;
    const { rowInfo } = computePlan();
    const skipped = [];
    for (const row of candidates) {
      const info = rowInfo.get(row.id);
      // Decide only once the row is complete (artist found, type chosen, works present).
      if (!info || info.issues.length || (!info.ready && !info.existing)) continue;
      row.existingChecked = true;
      if (!info.ready && info.existing && !info.applied) {
        row.existingAll = true;
        row.level = 'skip';
        skipped.push(row);
      }
    }
    skipped.forEach(rerenderRow);
    if (skipped.length) {
      const list = skipped.slice(0, 6).map((r) => {
        const a = S.artists.get(r.artistKey);
        return `${a ? a.mbName || a.name : ''}: ${r.raw}`;
      }).join('; ') + (skipped.length > 6 ? ' …' : '');
      log('info', 'existingSkipped', { n: skipped.length, list });
    }
  }

  function refresh() {
    if (!S.overlay) return;
    autoSkipExisting();
    const { items, rowInfo } = computePlan();
    S.plan = items;
    let incomplete = 0;
    let existing = 0;
    for (const row of S.rows) {
      const el = S.overlay.querySelector(`[data-status="${row.id}"]`);
      const info = rowInfo.get(row.id);
      existing += info.existing;
      if (!el) continue;
      const rowEl = el.closest('tr');
      if (rowEl) {
        const allThere = row.existingAll || (info.existing > 0 && !info.ready && !info.issues.length);
        rowEl.classList.toggle('dci-exists', allThere);
        rowEl.classList.toggle('dci-exists-some', !allThere && (info.existing > 0 || info.loose > 0) && info.ready > 0);
      }
      el.className = 'dci-status';
      if (row.level === 'skip') {
        el.textContent = row.existingAll ? tr('status.skippedExisting') : '';
        if (row.existingAll) el.classList.add('dci-ok');
        continue;
      }
      if (info.issues.length) {
        incomplete++;
        el.classList.add('dci-bad');
        el.textContent = info.issues.join(', ');
        continue;
      }
      const parts = [];
      if (info.ready) parts.push(tr('status.new', { n: info.ready }));
      if (info.existing) parts.push(tr('status.existing', { n: info.existing }));
      if (info.applied) parts.push(tr('status.applied', { n: info.applied }));
      if (info.noWork) {
        parts.push(tr('status.noWork', { n: info.noWork }));
        el.classList.add('dci-warn');
      }
      if (info.loose) {
        parts.push(tr('status.loose', { n: info.loose }));
        el.classList.add('dci-warn');
      }
      if (!info.ready) el.classList.add('dci-muted');
      el.textContent = parts.join(', ') || tr('status.nothing');
    }

    const count = (fn) => items.filter(fn).length;
    const kinds = [
      ['kind.recording', count((i) => i.kind === 'credit' && i.target.kind === 'recording')],
      ['kind.release', count((i) => i.target.kind === 'release')],
      ['kind.work', count((i) => i.target.kind === 'work')],
      ['kind.workLink', count((i) => i.kind === 'work-link')],
    ].filter(([, n]) => n).map(([key, n]) => tr(key, { n }));
    const sum = [`<strong>${esc(tr('sum.new', { n: items.length }))}</strong>${kinds.length ? ` (${esc(kinds.join(', '))})` : ''}`];
    if (incomplete) sum.push(`<span class="dci-bad">${esc(tr('sum.incomplete', { n: incomplete }))}</span>`);
    if (existing) sum.push(`<span class="dci-muted">${esc(tr('sum.existing', { n: existing }))}</span>`);
    $('sum').innerHTML = sum.join('<br>');
    S.overlay.querySelectorAll('[data-group]').forEach((section) => {
      const rows = S.rows.filter((r) => r.artistKey === section.dataset.group);
      section.classList.toggle('dci-all-skip', rows.length > 0 && rows.every((r) => r.level === 'skip'));
    });
    S.overlay.querySelector('[data-act="apply"]').disabled = !items.length;
    renderPreview();
    renderPanic();
  }

  function renderPreview() {
    const el = $('preview');
    el.hidden = !S.previewOpen;
    if (!S.previewOpen) return;
    if (!S.plan.length) {
      el.innerHTML = `<p class="dci-muted">${esc(tr('preview.empty'))}</p>`;
      return;
    }
    const byTarget = new Map();
    for (const it of [...S.plan].sort((a, b) => a.target.order - b.target.order)) {
      const label = it.target.kind === 'release' ? tr('preview.release')
        : it.target.kind === 'work' ? tr('preview.work', { title: it.target.work.title }) : it.target.label;
      if (!byTarget.has(label)) byTarget.set(label, []);
      const attrText = it.attrs.map((a) => {
        if (a.credited_as) return tr('preview.attrCredit', { name: a.type.name, credit: a.credited_as });
        if (a.text_value != null) return `${a.type.name}: ${tr('common.quoted', { text: a.text_value })}`;
        return a.type.name;
      }).join(', ');
      const line = it.kind === 'work-link'
        ? [tr('preview.linkWork', { title: it.workTitle }) + (attrText ? ` (${attrText})` : '')]
        : [it.lt.type0 === it.lt.type1
          ? phraseSentence(it.lt, ...(it.row.enteredFirst ? [it.artist.mbName, label] : [label, it.artist.mbName])) + (attrText ? ` (${attrText})` : '')
          : `${it.artist.mbName}: ${it.lt.name}${attrText ? ` (${attrText})` : ''}`];
      if (it.credit) line.push(tr('preview.artistCredit', { credit: it.credit }));
      if (it.date) line.push(tr('preview.date', { date: formatDateValue(it.date) || tr('date.endedOnly') }));
      if (it.noteText) line.push(tr('preview.noteOnly', { text: it.noteText }));
      byTarget.get(label).push(esc(line.join(', ')));
    }
    el.innerHTML = [...byTarget].map(([label, lines]) => `
      <div class="dci-pv-target"><strong>${esc(label)}</strong><ul>${lines.map((l) => `<li>${l}</li>`).join('')}</ul></div>`).join('');
  }

  function renderPanic() {
    if (!S.overlay) return;
    const btn = S.overlay.querySelector('[data-act="panic"]');
    const n = readCreatedWorks().length;
    btn.hidden = !n;
    btn.textContent = tr('panic.button', { n });
  }

  // ===========================================================================
  // 8b. Creating entities in MB forms (artist, work)
  // ===========================================================================

  /**
   * Shows a seeded MB create form inside the dashboard. The user submits it;
   * once the frame (or the fallback window) lands on /<type>/<MBID>, onCreated runs.
   */
  function openCreateDialog({ title, url, entityType, infoHtml, onCreated, onCancel }) {
    const sub = $('sub');
    const frame = $('sub-frame');
    const created = new RegExp(`^/${entityType}/(${MBID_RE.source})(?:/|$)`, 'i');
    let done = false;
    let popup = null;
    let pollTimer = null;

    const cleanup = () => {
      clearInterval(pollTimer);
      if (popup && !popup.closed) popup.close();
      frame.onload = null;
      frame.src = 'about:blank';
      sub.hidden = true;
      S.subDialog = null;
    };
    const finish = (mbid) => {
      if (done) return;
      done = true;
      cleanup();
      onCreated(mbid.toLowerCase());
    };
    const check = (win) => {
      try {
        const path = win.location.pathname;
        if (!/\/create/.test(path)) {
          const m = path.match(created);
          if (m) finish(m[1]);
        }
        return true;
      } catch (e) {
        return false;
      }
    };

    $('sub-title').textContent = title;
    $('sub-info').innerHTML = infoHtml;
    sub.hidden = false;
    frame.onload = () => {
      if (!check(frame.contentWindow)) $('sub-info').insertAdjacentHTML('beforeend', `<p class="dci-bad">${esc(tr('sub.blocked'))}</p>`);
    };
    frame.src = url;

    S.subDialog = {
      cancel: () => {
        if (done) return;
        done = true;
        cleanup();
        if (onCancel) onCancel();
      },
      openWindow: () => {
        frame.src = 'about:blank';
        popup = window.open(url, 'dci-create', 'popup=yes,width=1100,height=900');
        if (!popup) {
          $('sub-info').insertAdjacentHTML('beforeend', `<p class="dci-bad">${esc(tr('sub.popupBlocked'))}</p>`);
          return;
        }
        $('sub-info').insertAdjacentHTML('beforeend', `<p>${esc(tr('sub.popupOpen'))}</p>`);
        pollTimer = setInterval(() => {
          if (popup.closed) {
            clearInterval(pollTimer);
            return;
          }
          check(popup);
        }, 700);
      },
    };
  }

  async function startArtistCreate(artist) {
    const x = idx();
    let discogsArtist = null;
    const warnings = [];
    const rels = [];
    const notInMb = [];
    if (artist.dId) {
      try {
        setBusy('busy.discogsArtist', { name: artist.name });
        discogsArtist = await fetchDiscogsArtist(artist.dId);
        // Members (for a group) or groups (for a person) that already exist in MB
        const related = [
          ...((discogsArtist.members || []).map((m) => ({ ...m, newIsGroup: true }))),
          ...((discogsArtist.groups || []).map((g) => ({ ...g, newIsGroup: false }))),
        ].filter((r) => r.id);
        if (related.length) {
          const found = new Map();
          const urls = related.map((r) => discogsArtistUrl(r.id));
          for (let i = 0; i < urls.length; i += 50) {
            (await lookupDiscogsArtistUrls(urls.slice(i, i + 50))).forEach((v, k) => found.set(k, v));
          }
          for (const r of related) {
            const matches = found.get(discogsArtistUrl(r.id)) || [];
            if (matches.length === 1) {
              // "member of band": the member is entity0. If the new artist is the group, the relationship points backward.
              rels.push({ mbid: matches[0].mbid, name: matches[0].name, linkTypeId: x.memberLtId, backward: r.newIsGroup, ended: r.active === false });
            } else {
              notInMb.push(r);
            }
          }
        }
      } catch (e) {
        warnings.push(tr('artistDlg.loadFailed', { msg: e.message }));
      } finally {
        setBusy('');
      }
    }
    const type = guessArtistType(discogsArtist);
    const params = buildArtistSeed({
      name: artist.name,
      discogsId: artist.dId,
      discogsArtist,
      typeId: type === 'group' ? 2 : type === 'person' ? 1 : null,
      discogsLinkTypeId: x.discogsArtistUrlLtId,
      rels,
      editNote: artist.dId ? `Source: ${discogsArtistUrl(artist.dId)}\nPrefilled by ${EDIT_NOTE_SCRIPT_NAME} v${VERSION} (userscript, ${SCRIPT_URL}) from Discogs.` : '',
    });
    const urlCount = params.filter(([k]) => /^edit-artist\.url\.\d+\.text$/.test(k)).length;
    const displayName = cleanDiscogsName((discogsArtist && discogsArtist.name) || artist.name);
    const prefilled = [tr('part.name')];
    if (type) prefilled.push(tr('part.type', { type: tr(`type.${type}`) }));
    if (urlCount) prefilled.push(tr('part.urls', { n: urlCount }));
    if (rels.length) prefilled.push(tr('part.members', { n: rels.length, names: rels.map((r) => r.name).join(', ') }));
    const info = [`<p>${esc(tr('artistDlg.prefilled', { list: prefilled.join(', ') }))}</p>`];
    if (notInMb.length) {
      const links = notInMb.map((r) => `<a href="${discogsArtistUrl(r.id)}" target="_blank" rel="noopener">${esc(cleanDiscogsName(r.name))}</a>`).join(', ');
      info.push(`<p class="dci-muted">${esc(tr('artistDlg.notInMb')).replace('{list}', links)}</p>`);
    }
    warnings.forEach((w) => info.push(`<p class="dci-bad">${esc(w)}</p>`));
    info.push(`<p>${esc(tr('artistDlg.check'))}</p>`);
    log('info', 'artistForm', { name: displayName });

    openCreateDialog({
      title: tr('artistDlg.title', { name: displayName }),
      url: `/artist/create?${toQuery(params)}`,
      entityType: 'artist',
      infoHtml: info.join(''),
      onCreated: async (mbid) => {
        let name = displayName;
        try {
          const e = await fetchJsEntity(mbid);
          name = e.name;
          Object.assign(artist, { mbid: e.gid || mbid, mbName: e.name, status: 'created', editing: false, error: '' });
        } catch (err) {
          Object.assign(artist, { mbid, mbName: displayName, status: 'created', editing: false, error: '' });
        }
        showMessage('ok', 'artistDlg.done', { name });
        log('ok', 'artistCreated', { name, mbid });
        updateGroupHeader(artist);
        refresh();
      },
      onCancel: () => log('info', 'formCancelled'),
    });
  }

  function startCompanyCreate(company, entityType) {
    const params = [[`edit-${entityType}.name`, company.name]];
    if (company.dId) {
      params.push([`edit-${entityType}.url.0.text`, discogsLabelUrl(company.dId)]);
      params.push([`edit-${entityType}.url.0.link_type_id`, String(idx().discogsUrlLtId[entityType])]);
    }
    params.push([`edit-${entityType}.edit_note`, [
      company.dId ? `Source: ${discogsLabelUrl(company.dId)}` : '',
      `Prefilled by ${EDIT_NOTE_SCRIPT_NAME} v${VERSION} (userscript, ${SCRIPT_URL}) from Discogs.`,
    ].filter(Boolean).join('\n')]);
    const info = `<p>${esc(tr('companyDlg.prefilled'))}</p><p>${esc(tr(entityType === 'place' ? 'companyDlg.checkPlace' : 'companyDlg.checkLabel'))}</p>`;
    log('info', 'companyForm', { name: company.name, type: tr(`entity.${entityType}`) });
    openCreateDialog({
      title: tr(entityType === 'place' ? 'companyDlg.titlePlace' : 'companyDlg.titleLabel', { name: company.name }),
      url: `/${entityType}/create?${toQuery(params)}`,
      entityType,
      infoHtml: info,
      onCreated: async (mbid) => {
        let name = company.name;
        let gid = mbid;
        try {
          const e = await fetchJsEntity(mbid);
          name = e.name;
          gid = e.gid || mbid;
        } catch (err) {
          console.warn('[Discogs-Credits]', err);
        }
        Object.assign(company, { mbid: gid, mbName: name, status: 'created', editing: false, error: '' });
        setCompanyEntityType(company, entityType);
        showMessage('ok', 'companyDlg.done', { name });
        log('ok', 'companyCreated', { name, mbid: gid });
        rerenderGroup(company);
        refresh();
      },
      onCancel: () => log('info', 'formCancelled'),
    });
  }

  /** Writers for a new work: work-level rows that cover this track and are complete. */
  function writersForTrack(i) {
    const out = [];
    for (const row of S.rows) {
      if (row.level !== 'work' || !row.tracks.has(i)) continue;
      const artist = S.artists.get(row.artistKey);
      const lt = currentLinkType(row);
      if (!artist || !artist.mbid || !lt) continue;
      if (!out.some((w) => w.mbid === artist.mbid && w.linkTypeId === lt.id)) {
        out.push({ mbid: artist.mbid, name: artist.mbName || artist.name, linkTypeId: lt.id, typeName: lt.name, credit: row.credit.trim() });
      }
    }
    return out;
  }

  const trackLabel = (track) => `${track.medium}.${track.number}`;

  function startWorkCreate(i) {
    const track = S.mbTracks[i];
    if (!track) return;
    const writers = writersForTrack(i);
    const typeName = (S.workOptions.types.find((x) => String(x.id) === S.workDefaults.typeId) || {}).name;
    const langName = (S.workOptions.languages.find((x) => String(x.id) === S.workDefaults.languageId) || {}).name;
    const discogsId = S.discogsId || S.noteDiscogsId;
    const params = buildWorkSeed({
      title: track.title,
      typeId: S.workDefaults.typeId,
      languageId: S.workDefaults.languageId,
      writers,
      editNote: [
        discogsId ? `Source: https://www.discogs.com/release/${discogsId}` : '',
        `Prefilled by ${EDIT_NOTE_SCRIPT_NAME} v${VERSION} (userscript, ${SCRIPT_URL})${writers.length ? '; writers from Discogs credits' : ''}.`,
      ].filter(Boolean).join('\n'),
    });
    const prefilled = [tr('part.title', { title: track.title })];
    if (typeName) prefilled.push(tr('part.workType', { name: typeName }));
    if (langName) prefilled.push(tr('part.language', { name: langName }));
    writers.forEach((w) => prefilled.push(`${w.typeName}: ${w.name}`));
    const info = [
      `<p>${esc(tr('workDlg.prefilled', { list: prefilled.join(', ') }))}</p>`,
      writers.length ? '' : `<p class="dci-muted">${esc(tr('workDlg.noWriters'))}</p>`,
      `<p>${esc(tr('workDlg.after', { track: trackLabel(track) }))}</p>`,
    ].join('');
    log('info', 'workForm', { track: trackLabel(track) });
    openCreateDialog({
      title: tr('workDlg.title', { title: track.title }),
      url: `/work/create?${toQuery(params)}`,
      entityType: 'work',
      infoHtml: info,
      onCreated: async (mbid) => {
        let title = track.title;
        try {
          // Writers entered in the form now exist; register them so the dashboard does not add them twice.
          const w = await mbWs(`work/${mbid}?inc=artist-rels`);
          if (w) {
            title = w.title;
            addExistingArtistRels(S.existing, mbid, w.relations);
          }
        } catch (e) {
          console.warn('[Discogs-Credits]', e);
        }
        S.workPlan.set(i, { gid: mbid, title, origin: 'created', flags: new Set() });
        rememberCreatedWork(i, mbid, title);
        showMessage('ok', 'workDlg.done', { title, track: trackLabel(track) });
        log('ok', 'workCreated', { title, track: trackLabel(track), mbid });
        renderWorks();
        refresh();
        continueWorkQueue();
      },
      onCancel: () => {
        S.workQueue = [];
        log('info', 'formCancelled');
      },
    });
  }

  function continueWorkQueue() {
    while (S.workQueue.length) {
      const next = S.workQueue.shift();
      if (!worksForTrack(next).length) {
        startWorkCreate(next);
        return;
      }
    }
  }

  async function runWorkSearch(i) {
    const track = S.mbTracks[i];
    if (!track) return;
    const writers = writersForTrack(i);
    S.workSearch.set(i, { state: 'loading', results: [], writers });
    renderWorkRow(i);
    try {
      const results = await searchWorks(track.title, writers.map((w) => w.mbid));
      S.workSearch.set(i, { state: 'done', results, writers });
      log('info', 'workSearch', { track: trackLabel(track), n: results.length });
    } catch (e) {
      S.workSearch.set(i, { state: 'error', results: [], writers, error: e.message });
      log('error', 'error', { text: e.message });
    }
    renderWorkRow(i);
  }

  // --- Works panel ---------------------------------------------------------------

  function workOptionsHtml(list, selected) {
    return `<option value="">${esc(tr('works.none'))}</option>${list.map((o) => `<option value="${o.id}" ${String(o.id) === String(selected) ? 'selected' : ''}>${esc(o.name)}</option>`).join('')}`;
  }

  function workRowHtml(track) {
    const i = track.idx;
    const planned = S.workPlan.get(i);
    const search = S.workSearch.get(i);
    const perf = idx().performanceLt;
    let status = '';
    let actions = '';
    if (track.works.length) {
      status = track.works.map((w) => `<div><span class="dci-badge dci-badge-ok">${esc(tr('works.linked'))}</span> <a href="/work/${w.gid}" target="_blank" rel="noopener">${esc(w.title)}</a>${w.writers.length ? ` <span class="dci-sub">${esc(w.writers.join(', '))}</span>` : ''}</div>`).join('');
    } else if (planned) {
      const flags = perf ? allowedRoots(perf).filter((r) => !r.hasChildren && !r.attr.free_text) : [];
      status = `<div><span class="dci-badge dci-badge-plan">${esc(tr(planned.origin === 'created' ? 'works.plannedCreated' : 'works.plannedFound'))}</span>
        <a href="/work/${planned.gid}" target="_blank" rel="noopener">${esc(planned.title)}</a></div>
        ${flags.length ? `<div class="dci-flags">${flags.map(({ attr }) => `<label class="dci-check" title="${esc(attrHelp(attr))}"><input type="checkbox" data-f="work-flag" value="${esc(norm(attr.name))}" ${planned.flags.has(norm(attr.name)) ? 'checked' : ''}> ${esc(attr.name)}</label>`).join('')}</div>` : ''}`;
      actions = `<button type="button" class="dci-textbtn" data-act="work-unplan">${esc(tr('works.unplan'))}</button>`;
    } else {
      status = `<span class="dci-muted">${esc(tr('works.noWork'))}</span>`;
      actions = `<button type="button" data-act="work-search">${esc(tr('works.search'))}</button> <button type="button" data-act="work-create">${esc(tr('works.create'))}</button>`;
      if (search && search.state === 'loading') {
        status += `<div class="dci-sub">${esc(tr('works.searching'))}</div>`;
      } else if (search && search.state === 'error') {
        status += `<div class="dci-bad">${esc(search.error)}</div>`;
      } else if (search && search.state === 'done') {
        status += `<div class="dci-sub">${esc(search.writers.length
          ? tr('works.basisWriters', { names: search.writers.map((w) => w.name).join(', ') })
          : tr('works.basisTitle'))}</div>`;
        status += search.results.length
          ? `<ul class="dci-candidates">${search.results.map((w) => `<li>
              <button type="button" data-act="work-pick" data-gid="${esc(w.gid)}" data-title="${esc(w.title)}">${esc(tr('works.link'))}</button>
              <a href="/work/${esc(w.gid)}" target="_blank" rel="noopener">${esc(w.title)}</a>${w.disambiguation ? ` <span class="dci-muted">(${esc(w.disambiguation)})</span>` : ''}
              <span class="dci-sub">${esc([w.type, w.writers.join(', ')].filter(Boolean).join(' – '))}</span>
            </li>`).join('')}</ul>`
          : `<div class="dci-muted">${esc(tr('works.noResults'))}</div>`;
      }
    }
    const dPos = S.dTracks[i] ? S.dTracks[i].position : '';
    return `<tr data-work="${i}">
      <td class="dci-w-track"><span class="dci-tn">${esc(trackLabel(track))}</span> ${esc(track.title)}${dPos ? `<div class="dci-sub">Discogs ${esc(dPos)}</div>` : ''}</td>
      <td class="dci-w-status">${status}</td>
      <td class="dci-w-actions">${actions}</td>
    </tr>`;
  }

  function renderWorks() {
    if (!S.overlay) return;
    const el = $('works');
    if (!S.mbTracks.length || !S.workOptions) {
      el.hidden = true;
      return;
    }
    el.hidden = false;
    const missing = S.mbTracks.filter((x) => !worksForTrack(x.idx).length).length;
    el.innerHTML = `
      <h3>${esc(tr('works.title'))}</h3>
      <p class="dci-muted">${esc(missing ? tr('works.missing', { n: missing }) : tr('works.allDone'))} ${esc(tr('works.explain'))}</p>
      <div class="dci-works-bar">
        <label>${esc(tr('works.type'))} <select data-f="work-type">${workOptionsHtml(S.workOptions.types, S.workDefaults.typeId)}</select></label>
        <label>${esc(tr('works.lang'))} <select data-f="work-lang">${workOptionsHtml(S.workOptions.languages, S.workDefaults.languageId)}</select></label>
        ${missing ? `<button type="button" data-act="works-search-all">${esc(tr('works.searchAll'))}</button>
        <button type="button" data-act="works-create-all">${esc(tr('works.createAll'))}</button>` : ''}
      </div>
      <div class="dci-tablewrap">
        <table class="dci-table dci-worktable">
          <thead><tr><th scope="col">${esc(tr('th.track'))}</th><th scope="col">${esc(tr('th.work'))}</th><th scope="col">${esc(tr('th.action'))}</th></tr></thead>
          <tbody>${S.mbTracks.map(workRowHtml).join('')}</tbody>
        </table>
      </div>`;
  }

  function renderWorkRow(i) {
    const row = S.overlay.querySelector(`tr[data-work="${i}"]`);
    if (!row) return renderWorks();
    const tmp = document.createElement('tbody');
    tmp.innerHTML = workRowHtml(S.mbTracks[i]);
    row.replaceWith(tmp.firstElementChild);
  }

  // --- Discogs tab (companion script) -----------------------------------------------

  const toDiscogs = (msg) => document.dispatchEvent(new CustomEvent('dci:to-discogs', { detail: JSON.stringify(msg) }));

  function syncStatusHtml(withDetails) {
    const st = S.sync;
    if (!st.installed) return `<span class="dci-muted" title="${esc(tr('sync.offTitle'))}">${esc(tr('sync.off'))}</span>`;
    if (!st.tabs) {
      return `${esc(tr('sync.noTab'))}${withDetails && S.discogsId ? ` <button type="button" data-act="sync-open">${esc(tr('sync.openTab'))}</button>` : ''}`;
    }
    const where = tr(st.target && st.target.visible ? 'sync.visible' : 'sync.background');
    return `${esc(tr('sync.connected', { where }))}${withDetails && st.last ? ` <span class="dci-sub">${esc(tr(`sync.${st.last}`))}</span>` : ''}`;
  }

  /** Switch: the Discogs tab follows the dashboard on mouse-over or on click. */
  function syncModeHtml() {
    const btn = (mode) => `<button type="button" data-sync-mode="${mode}" aria-pressed="${S.syncMode === mode}">${esc(tr(`syncMode.${mode}`))}</button>`;
    return `<span class="dci-syncmode"><span>${esc(tr('syncMode.label'))}</span>
      <span class="dci-seg dci-seg-small" role="group" aria-label="${esc(tr('syncMode.label'))}">${btn('hover')}${btn('click')}</span></span>`;
  }

  // The mode switch only makes sense with the companion script, so it is hidden without it.
  function renderSync() {
    renderControls();
    if (!S.overlay) return;
    $('sync').innerHTML = `${S.sync.installed ? syncModeHtml() : ''} <span class="dci-syncstatus">${syncStatusHtml(true)}</span>`;
  }

  function renderControls() {
    const bar = document.getElementById('dci-controls');
    if (!bar) return;
    bar.hidden = !S.sync.installed;
    bar.innerHTML = S.sync.installed ? `${syncModeHtml()} <span class="dci-syncstatus">${syncStatusHtml(false)}</span>` : '';
  }

  function setSyncMode(mode) {
    if (mode !== 'hover' && mode !== 'click') return;
    S.syncMode = mode;
    writeJson('localStorage', 'dci-sync-mode', mode);
    log('info', 'syncMode', { mode: tr(`syncMode.${mode}`) });
    renderSync();
  }

  function onFromDiscogs(e) {
    let msg;
    try {
      msg = JSON.parse(e.detail);
    } catch (err) {
      return;
    }
    if (msg.type === 'status') {
      Object.assign(S.sync, { installed: true, tabs: msg.tabs, target: msg.target });
    } else if (msg.type === 'result') {
      S.sync.installed = true;
      const known = ['credit', 'track', 'artist', 'loading', 'none', 'no-tab'];
      S.sync.last = known.includes(msg.found) ? `found.${msg.found}` : '';
      if (S.sync.last && msg.found !== 'loading') log(msg.found === 'none' || msg.found === 'no-tab' ? 'warn' : 'info', 'discogsJump', { result: tr(`sync.${S.sync.last}`) });
    }
    renderSync();
  }

  let lastShown = '';
  let showTimer = null;
  function showOnDiscogs(payload) {
    if (!S.sync.installed || !S.discogsId) return;
    const msg = { type: 'show', releaseId: S.discogsId, ...payload };
    const sig = JSON.stringify(msg);
    if (sig === lastShown) return;
    clearTimeout(showTimer);
    showTimer = setTimeout(() => {
      lastShown = sig;
      S.sync.last = 'jumping';
      renderSync();
      toDiscogs({ ...msg, id: nextId('c') });
    }, 250);
  }

  function discogsPayloadForRow(row) {
    const artist = S.artists.get(row.artistKey);
    if (row.company) {
      return { labelId: artist ? artist.dId : 0, artistId: 0, artistName: artist ? (artist.rawName || artist.name) : '', role: row.raw, base: row.raw, positions: [], spec: '' };
    }
    return {
      artistId: artist ? artist.dId : 0,
      artistName: artist ? (artist.rawName || artist.name) : '',
      anv: row.anv || '',
      role: row.raw,
      base: row.base,
      positions: row.dPositions,
      spec: row.dSpec,
    };
  }

  const sourceElOf = (target) => (target && target.closest ? target.closest('tr.dci-row, tr[data-work], .dci-ghead') : null);

  function onFocusSource(e) {
    const el = sourceElOf(e.target);
    if (el) showSourceOf(el);
  }

  // Mouse-over mode: jump only when the pointer rests on a row for a moment,
  // so moving across the dashboard does not make the Discogs tab scroll back and forth.
  const HOVER_DELAY = 450;
  let hoverEl = null;
  let hoverTimer = null;
  function onHover(e) {
    if (S.syncMode !== 'hover') return;
    const el = sourceElOf(e.target);
    if (el === hoverEl) return;
    hoverEl = el;
    clearTimeout(hoverTimer);
    if (el) hoverTimer = setTimeout(() => { if (hoverEl === el) showSourceOf(el); }, HOVER_DELAY);
  }
  function onHoverEnd() {
    hoverEl = null;
    clearTimeout(hoverTimer);
  }

  function showSourceOf(el) {
    if (el.matches('tr.dci-row')) {
      const row = rowOf(el);
      if (row && !row.manual) showOnDiscogs(discogsPayloadForRow(row));
    } else if (el.matches('tr[data-work]')) {
      const d = S.dTracks[Number(el.dataset.work)];
      if (d) showOnDiscogs({ positions: [d.position || ''], role: '', artistId: 0, artistName: '' });
    } else {
      const artist = artistOf(el);
      if (artist && artist.dId) {
        showOnDiscogs(artist.company
          ? { labelId: artist.dId, artistId: 0, artistName: artist.rawName || artist.name, role: '', positions: [] }
          : { artistId: artist.dId, artistName: artist.rawName || artist.name, role: '', positions: [] });
      }
    }
  }

  // ===========================================================================
  // 9. Events
  // ===========================================================================

  function rowOf(el) {
    const row = el.closest('[data-row],[data-tracksrow]');
    if (!row) return null;
    const id = row.dataset.row || row.dataset.tracksrow;
    return S.rows.find((r) => r.id === id) || null;
  }

  function artistOf(el) {
    const section = el.closest('[data-group]');
    return section ? S.artists.get(section.dataset.group) : null;
  }

  const workIndexOf = (el) => Number(el.closest('tr[data-work]').dataset.work);

  function setLevel(row, level) {
    row.level = level;
    row.levelTouched = true;
    resolveRowType(row);
    if (!primaryIsValid(row) || !norm(row.primaryText)) row.primaryText = pickPrimary(row);
    refreshRowDetails(row);
    rerenderRow(row);
    refresh();
  }

  function setType(row, id) {
    row.linkTypeId = id || null;
    const lt = currentLinkType(row);
    if (lt) row.types = [lt.name, ...row.types.filter((n) => norm(n) !== norm(lt.name))];
    if (!primaryIsValid(row) || !norm(row.primaryText)) row.primaryText = pickPrimary(row);
    refreshRowDetails(row);
    rerenderRow(row);
    refresh();
  }

  /** All MB relationship type names an entity type can have on any level, for the role list. */
  function mbTypeNames(entityType) {
    return uniq(['recording', 'release', 'work'].flatMap((l) => typesFor(l, entityType).map((lt) => lt.name)))
      .sort((a, b) => a.localeCompare(b));
  }

  const levelsOfType = (name, entityType) => ['recording', 'release', 'work']
    .filter((l) => typesFor(l, entityType).some((lt) => norm(lt.name) === norm(name)));

  /** Turns a row into "miscellaneous support" with its role as task, on a level where MB has that type. */
  function makeMiscRow(row, task) {
    Object.assign(row, { types: ['misc'], primaryCands: [], notes: [...row.notes, 'unknownRole'], creditFromRole: task });
    row.primaryText = '';
    const levels = levelsOfType('misc', row.entityType);
    if (levels.length && !levels.includes(row.level)) row.level = levels.includes('release') ? 'release' : levels[0];
    resolveRowType(row);
  }

  /**
   * Sets a manual row's role from text. An exact MB relationship type name (e.g. "artwork", "pressed")
   * is used as it is; anything else is read like a Discogs role (e.g. "Guitar [Electric]").
   */
  function applyRoleText(row, text) {
    const raw = String(text || '').trim();
    const exact = raw ? levelsOfType(raw, row.entityType) : [];
    let fallback = false;
    if (exact.length) {
      const name = typesFor(exact[0], row.entityType).find((lt) => norm(lt.name) === norm(raw)).name;
      let level = row.entityType === 'artist' && exact.includes('recording') ? 'recording' : exact.includes('release') ? 'release' : exact[0];
      if (row.entityType === 'artist') {
        const m = mapRole(raw, []);
        if (norm(m.types[0]) === norm(name) && exact.includes(m.level)) level = m.level;
      } else {
        const c = mapCompanyRole(raw);
        if ((c.typeOptions[row.entityType] || []).some((n) => norm(n) === norm(name)) && exact.includes(c.level)) level = c.level;
      }
      Object.assign(row, {
        raw, base: raw, mods: [], consumed: [], types: [name], notes: [], work: level === 'work', primaryCands: [],
        flags: new Set(), creditFromRole: '', defaultLevel: level,
        typeOptions: row.company ? { ...(row.typeOptions || {}), [row.entityType]: [name] } : row.typeOptions,
      });
      if (!row.levelTouched) row.level = level;
    } else if (row.other) {
      const levels = ['recording', 'release', 'work'].filter((l) => typesFor(l, row.entityType).length);
      Object.assign(row, { raw, base: raw, mods: [], consumed: [], types: [], notes: [], primaryCands: [], flags: new Set(), creditFromRole: '' });
      if (!row.levelTouched && levels.length && !levels.includes(row.level)) row.level = levels.includes('release') ? 'release' : levels[0];
    } else if (row.company) {
      const c = mapCompanyRole(raw);
      Object.assign(row, {
        raw, base: raw, mods: [], consumed: [], typeOptions: c.typeOptions, types: c.typeOptions[row.entityType] || [],
        notes: c.notes, defaultLevel: c.level, creditFromRole: '', flags: new Set(),
      });
      if (!row.levelTouched) row.level = c.level;
    } else {
      const parsed = parseRoles(raw)[0] || { raw: '', base: '', mods: [] };
      const m = mapRole(parsed.base, parsed.mods);
      fallback = !!m.fallback && !!raw;
      Object.assign(row, {
        raw, base: parsed.base, mods: parsed.mods, consumed: m.consumed, types: m.types, notes: m.notes, work: m.work,
        primaryCands: m.primaryCands, flags: new Set(m.flags.map(norm)), creditFromRole: m.credit || '', defaultLevel: m.level,
      });
      if (!row.levelTouched) row.level = m.level;
    }
    resolveRowType(row);
    row.primaryText = pickPrimary(row);
    if (fallback && !primaryIsValid(row)) makeMiscRow(row, row.base);
    refreshRowDetails(row);
  }

  function remapManualRow(row, text) {
    applyRoleText(row, text);
    rerenderRow(row);
    refresh();
  }

  function removeRow(row) {
    S.rows = S.rows.filter((r) => r.id !== row.id);
    const artist = S.artists.get(row.artistKey);
    if (artist && !S.rows.some((r) => r.artistKey === artist.key)) {
      const section = S.overlay.querySelector(`[data-group="${artist.key}"]`);
      if (section) section.remove();
      if (artist.manual) S.artists.delete(artist.key);
    } else {
      S.overlay.querySelectorAll(`tr[data-row="${row.id}"], tr[data-tracksrow="${row.id}"]`).forEach((n) => n.remove());
    }
    refresh();
  }

  /** While a stamp is active, clicking anywhere in a row's date cell applies it. */
  function onStampClick(e) {
    if (!S.stampId) return;
    const cell = e.target.closest && e.target.closest('.dci-c-date');
    const row = cell && rowOf(cell);
    const entry = S.datePool.find((d) => d.id === S.stampId);
    if (!row || !entry) return;
    e.preventDefault();
    if (applyPoolToRow(row, entry)) {
      log('info', 'dateApplied', { n: 1, date: poolLabel(entry) });
      renderDates();
      refresh();
    }
  }

  function onClick(e) {
    const btn = e.target.closest('[data-act]');
    if (!btn || !S.overlay.contains(btn)) return;
    const act = btn.dataset.act;
    const row = rowOf(btn);
    const artist = artistOf(btn);
    if (S.stampId && row && btn.closest('.dci-c-date')) return;  // handled by onStampClick

    switch (act) {
      case 'close':
        closeDashboard();
        break;
      case 'log':
        setLogVisible(!S.logEl || S.logEl.hidden);
        break;
      case 'zoom-in':
        setScale(S.scale + 0.1);
        break;
      case 'zoom-out':
        setScale(S.scale - 0.1);
        break;
      case 'window-reset':
        resetWindows();
        break;
      case 'panic':
        startPanic();
        break;
      case 'level':
        if (row) setLevel(row, btn.dataset.level);
        break;
      case 'bulk-level':
        for (const r of S.rows) {
          if ((r.work || r.company || r.other || r.existingAll) && btn.dataset.level !== 'skip') continue;
          r.level = btn.dataset.level;
          r.levelTouched = true;
          resolveRowType(r);
          if (!primaryIsValid(r) || !norm(r.primaryText)) r.primaryText = pickPrimary(r);
        }
        renderGroups();
        refresh();
        break;
      case 'tracks-toggle': {
        row.tracksOpen = !row.tracksOpen;
        btn.setAttribute('aria-expanded', String(row.tracksOpen));
        const tracksRow = S.overlay.querySelector(`tr[data-tracksrow="${row.id}"]`);
        if (tracksRow) tracksRow.hidden = !row.tracksOpen;
        break;
      }
      case 'tracks-all':
        row.tracks = new Set(S.mbTracks.map((x) => x.idx));
        updateTrackUi(row);
        refresh();
        break;
      case 'tracks-none':
        row.tracks = new Set();
        updateTrackUi(row);
        refresh();
        break;
      case 'tracks-invert':
        row.tracks = new Set(S.mbTracks.map((x) => x.idx).filter((i) => !row.tracks.has(i)));
        updateTrackUi(row);
        refresh();
        break;
      case 'tracks-discogs':
        row.tracks = new Set(row.suggested);
        updateTrackUi(row);
        refresh();
        break;
      case 'artist-edit':
        artist.editing = true;
        artist.error = '';
        updateGroupHeader(artist);
        S.overlay.querySelector(`[data-match="${artist.key}"] input`).focus();
        break;
      case 'artist-cancel':
        artist.editing = false;
        artist.error = '';
        updateGroupHeader(artist);
        break;
      case 'artist-set': {
        const input = S.overlay.querySelector(`[data-match="${artist.key}"] [data-f="artist-input"]`);
        setArtistManually(artist, input ? input.value : '');
        break;
      }
      case 'artist-create':
        if (artist) startArtistCreate(artist);
        break;
      case 'company-create':
        if (artist) startCompanyCreate(artist, btn.dataset.et);
        break;
      // Date fields of a row
      case 'date-open':
        row.dateOpen = true;
        row.date = row.date || { by: '', bm: '', bd: '', ey: '', em: '', ed: '', ended: false, poolId: null };
        rerenderRow(row);
        S.overlay.querySelector(`tr[data-row="${row.id}"] [data-f="rd-by"]`).focus();
        break;
      case 'rd-copy':
        Object.assign(row.date, { ey: row.date.by, em: row.date.bm, ed: row.date.bd, poolId: null });
        rerenderRow(row);
        refresh();
        break;
      case 'date-clear':
        row.date = null;
        row.dateOpen = false;
        rerenderRow(row);
        renderDates();
        refresh();
        break;
      case 'date-to-pool': {
        const res = rowDateInfo(row, currentLinkType(row));
        if (!res.value) {
          updateDateUi(row);
          break;
        }
        const lt = currentLinkType(row);
        openPoolForm(null, { ...res.value, name: lt ? lt.name : '' });
        S.poolForm.fromRow = row.id;
        break;
      }
      // Date pool
      case 'pool-new':
        openPoolForm();
        break;
      case 'pool-edit':
        openPoolForm(S.datePool.find((d) => d.id === btn.dataset.id));
        break;
      case 'pool-suggest': {
        const year = { year: Number(btn.dataset.year), month: null, day: null };
        openPoolForm(null, { name: '℗/©', begin: year, end: year, ended: true });
        break;
      }
      case 'pf-copy':
        Object.assign(S.poolForm, { ey: S.poolForm.by, em: S.poolForm.bm, ed: S.poolForm.bd });
        renderDates();
        break;
      case 'pool-save': {
        const fromRow = S.poolForm.fromRow && S.rows.find((r) => r.id === S.poolForm.fromRow);
        const before = S.datePool.length;
        savePoolForm();
        // "save to pool" from a row: the row now refers to the new entry
        if (fromRow && S.datePool.length > before) {
          fromRow.date.poolId = S.datePool[S.datePool.length - 1].id;
          rerenderRow(fromRow);
          renderDates();
        }
        break;
      }
      case 'pool-remove':
        if (S.poolForm && S.poolForm.id) removePoolEntry(S.poolForm.id);
        break;
      case 'pool-cancel':
        S.poolForm = null;
        renderDates();
        break;
      case 'pool-stamp': {
        S.stampId = S.stampId === btn.dataset.id ? null : btn.dataset.id;
        const entry = S.datePool.find((d) => d.id === S.stampId);
        if (entry) log('info', 'dateStamp', { date: poolLabel(entry) });
        renderDates();
        break;
      }
      case 'stamp-apply':
        stampApplyAll(S.overlay.querySelector('[data-f="stamp-type"]').value);
        break;
      case 'stamp-end':
        S.stampId = null;
        renderDates();
        break;
      case 'add-role': {
        const r = makeRow(artist.key, { manual: true, company: artist.company ? artist : null });
        if (artist.other) {
          Object.assign(r, { other: true, entityType: artist.entityType, types: [], typeOptions: null, notes: [] });
          applyRoleText(r, '');
        }
        r.tracks = new Set(S.mbTracks.map((x) => x.idx));
        S.rows.push(r);
        S.overlay.querySelector(`[data-group="${artist.key}"] tbody`).insertAdjacentHTML('beforeend', rowHtml(r));
        S.overlay.querySelector(`tr[data-row="${r.id}"] [data-f="role-text"]`).focus();
        refresh();
        break;
      }
      case 'remove-row':
        if (row) removeRow(row);
        break;
      case 'artist-credit-all': {
        const input = S.overlay.querySelector(`[data-variants="${artist.key}"] [data-f="artist-credit-all"]`);
        const value = input ? input.value.trim() : '';
        S.rows.filter((r) => r.artistKey === artist.key).forEach((r) => {
          r.credit = value;
          rerenderRow(r);
        });
        refresh();
        break;
      }
      case 'bulk-credit': {
        const fromDiscogs = btn.dataset.mode === 'discogs';
        for (const r of S.rows) {
          if (btn.dataset.kind === 'role') {
            r.roleCredit = fromDiscogs ? r.roleCreditSuggest : '';
            r.roleCreditTouched = !fromDiscogs;
          } else {
            r.credit = fromDiscogs ? r.anv : '';
          }
        }
        renderGroups();
        refresh();
        break;
      }
      case 'add-manual':
        addManualEntry();
        break;
      case 'discogs-load': {
        const input = S.overlay.querySelector('[data-f="discogs-input"]');
        const m = String(input.value).match(/(?:release\/|^r?)(\d+)/i);
        if (m) loadDiscogs(m[1]);
        else showMessage('error', 'msg.badDiscogsId');
        break;
      }
      case 'preview':
        S.previewOpen = !S.previewOpen;
        btn.setAttribute('aria-expanded', String(S.previewOpen));
        renderPreview();
        break;
      case 'apply':
        applyPlan();
        break;
      case 'sub-close':
        if (S.subDialog) S.subDialog.cancel();
        break;
      case 'sub-window':
        if (S.subDialog) S.subDialog.openWindow();
        break;
      case 'work-search':
        runWorkSearch(workIndexOf(btn));
        break;
      case 'work-create':
        S.workQueue = [];
        startWorkCreate(workIndexOf(btn));
        break;
      case 'work-pick': {
        const i = workIndexOf(btn);
        S.workPlan.set(i, { gid: btn.dataset.gid, title: btn.dataset.title, origin: 'search', flags: new Set() });
        log('info', 'workPicked', { track: trackLabel(S.mbTracks[i]), title: btn.dataset.title });
        renderWorks();
        refresh();
        break;
      }
      case 'work-unplan': {
        const i = workIndexOf(btn);
        S.workPlan.delete(i);
        log('info', 'workUnplanned', { track: trackLabel(S.mbTracks[i]) });
        renderWorks();
        refresh();
        break;
      }
      case 'works-search-all':
        (async () => {
          for (const x of S.mbTracks) {
            if (!worksForTrack(x.idx).length) await runWorkSearch(x.idx);
          }
        })();
        break;
      case 'works-create-all':
        S.workQueue = S.mbTracks.filter((x) => !worksForTrack(x.idx).length).map((x) => x.idx);
        continueWorkQueue();
        break;
      case 'sync-open':
        if (S.discogsId) toDiscogs({ type: 'open', url: `https://www.discogs.com/release/${S.discogsId}` });
        break;
      default:
        break;
    }
  }

  function onChange(e) {
    const el = e.target;
    const f = el.dataset && el.dataset.f;
    if (!f) return;
    const row = rowOf(el);
    switch (f) {
      case 'lang':
        setLanguage(el.value);
        break;
      case 'type':
        setType(row, Number(el.value));
        break;
      case 'flag':
        if (el.checked) row.flags.add(el.value);
        else row.flags.delete(el.value);
        refresh();
        break;
      case 'track': {
        const i = Number(el.dataset.i);
        if (el.checked) row.tracks.add(i);
        else row.tracks.delete(i);
        updateTrackUi(row);
        refresh();
        break;
      }
      case 'role-text':
        remapManualRow(row, el.value);
        break;
      case 'primary':
        row.primaryText = el.value;
        updateMark(row);
        updateHint(row);
        refresh();
        break;
      case 'credit':
        row.credit = el.value;
        refresh();
        break;
      case 'role-credit':
        row.roleCredit = el.value;
        row.roleCreditTouched = true;
        updateHint(row);
        refresh();
        break;
      case 'artist-pick': {
        const artist = artistOf(el);
        const c = artist.candidates.find((x) => x.mbid === el.value);
        if (c) {
          Object.assign(artist, { mbid: c.mbid, mbName: c.name, status: 'linked' });
          log('ok', 'artistLinked', { name: artist.name, mb: c.name });
          if (artist.company) {
            setCompanyEntityType(artist, c.entityType);
            rerenderGroup(artist);
          } else {
            updateGroupHeader(artist);
          }
          refresh();
        }
        break;
      }
      case 'direction':
        row.enteredFirst = el.value === 'entered';
        refresh();
        break;
      case 'rd-ended':
        row.date.ended = el.checked;
        row.date.poolId = null;
        refresh();
        break;
      case 'rd-pool': {
        const entry = S.datePool.find((d) => d.id === el.value);
        if (entry) {
          applyPoolToRow(row, entry);
          renderDates();
          refresh();
        }
        break;
      }
      case 'pf-ended':
        if (S.poolForm) S.poolForm.ended = el.checked;
        break;
      case 'filter-missing':
        S.onlyMissing = el.checked;
        S.overlay.classList.toggle('dci-only-missing', el.checked);
        break;
      case 'editnote':
        S.editNote = el.checked;
        S.rows.forEach(updateHint);
        break;
      case 'discogs-pick':
        if (el.value) loadDiscogs(el.value);
        break;
      case 'work-type':
        S.workDefaults.typeId = el.value;
        break;
      case 'work-lang':
        S.workDefaults.languageId = el.value;
        break;
      case 'work-flag': {
        const plan = S.workPlan.get(workIndexOf(el));
        if (plan) {
          if (el.checked) plan.flags.add(el.value);
          else plan.flags.delete(el.value);
          refresh();
        }
        break;
      }
      default:
        break;
    }
  }

  /** Pasting a date as MusicBrainz shows it fills begin, end and "ended" at once. */
  function onPaste(e) {
    const el = e.target;
    const f = (el.dataset && el.dataset.f) || (el.dataset && el.dataset.act === 'date-open' ? 'rd-by' : '');
    const m = f && f.match(/^(rd|pf)-([be])[ymd]$/);
    if (!m) return;
    const text = (e.clipboardData || window.clipboardData).getData('text');
    const parsed = parseDatePeriod(text);
    // A bare year is pasted normally, so month and day already typed stay.
    if (!parsed || (parsed.single && /^\s*\d{4}\s*$/.test(text))) return;
    e.preventDefault();
    const target = m[1] === 'pf' ? S.poolForm : null;
    const row = m[1] === 'rd' ? rowOf(el) : null;
    if (!target && !row) return;
    let fields;
    if (parsed.period) {
      fields = fieldsFromDate(parsed.period);
    } else {
      // One plain date: only the begin or end line it was pasted into
      const one = fieldsFromDate({ begin: parsed.single });
      fields = m[2] === 'b' ? { by: one.by, bm: one.bm, bd: one.bd } : { ey: one.by, em: one.bm, ed: one.bd };
    }
    if (target) {
      Object.assign(S.poolForm, fields);
      renderDates();
    } else {
      row.date = { ...(row.date || { by: '', bm: '', bd: '', ey: '', em: '', ed: '', ended: false }), ...fields, poolId: null };
      row.dateOpen = true;
      rerenderRow(row);
      renderDates();
      refresh();
    }
    log('info', 'datePasted', { date: formatDateValue(validateDateFields(target || row.date).value) || tr('date.endedOnly') });
  }

  let inputTimer = null;
  let manualTypeTimer = null;
  function onInput(e) {
    const el = e.target;
    const f = el.dataset && el.dataset.f;
    if (f === 'manual-artist') {
      const setList = (kind) => S.overlay.querySelector('[data-f="manual-role"]').setAttribute('list', `dci-dl-roles-${kind}`);
      const path = (el.value.match(/musicbrainz\.org\/(artist|label|place|area|event|series|recording|release-group|release|work|instrument)\//) || [])[1];
      const kind = path ? path.replace('-', '_') : '';
      setList(kind || 'artist');
      const mbid = !kind && (el.value.match(MBID_RE) || [])[0];
      clearTimeout(manualTypeTimer);
      if (mbid) {
        manualTypeTimer = setTimeout(async () => {
          try {
            const e = await fetchJsEntity(mbid.toLowerCase());
            const et = String(e.entityType || '').replace('-', '_');
            if (idx().relatableTypes.includes(et) && el.value.includes(mbid)) setList(et);
          } catch (err) { /* the add button reports invalid MBIDs */ }
        }, 400);
      }
      return;
    }
    // Pool form fields
    const pf = f && f.match(/^pf-(name|by|bm|bd|ey|em|ed)$/);
    if (pf && S.poolForm) {
      S.poolForm[pf[1]] = el.value;
      if (pf[1] === 'ey') {
        const box = S.overlay.querySelector('[data-f="pf-ended"]');
        if (box) {
          box.disabled = el.value.trim() !== '';
          box.checked = box.disabled || !!S.poolForm.ended;
        }
      }
      return;
    }
    // Date fields of a row: typing makes the date the row's own (no longer from the pool)
    const rd = f && f.match(/^rd-(by|bm|bd|ey|em|ed)$/);
    if (rd) {
      const row = rowOf(el);
      if (!row || !row.date) return;
      row.date[rd[1]] = el.value;
      row.date.poolId = null;
      updateDateUi(row);
      clearTimeout(inputTimer);
      inputTimer = setTimeout(() => { refresh(); renderDates(); }, 250);
      return;
    }
    if (f !== 'primary' && f !== 'credit' && f !== 'role-credit') return;
    const row = rowOf(el);
    if (!row) return;
    if (f === 'primary') {
      row.primaryText = el.value;
      updateMark(row);
      updateHint(row);
    } else if (f === 'role-credit') {
      row.roleCredit = el.value;
      row.roleCreditTouched = true;
      updateHint(row);
    } else {
      row.credit = el.value;
    }
    clearTimeout(inputTimer);
    inputTimer = setTimeout(refresh, 250);
  }

  function onKeydown(e) {
    if (e.key !== 'Enter') return;
    const f = e.target.dataset && e.target.dataset.f;
    const map = {
      'artist-credit-all': '[data-act="artist-credit-all"]',
      'artist-input': '[data-act="artist-set"]',
      'manual-artist': '[data-act="add-manual"]',
      'manual-role': '[data-act="add-manual"]',
      'discogs-input': '[data-act="discogs-load"]',
      'pf-name': '[data-act="pool-save"]',
      'pf-by': '[data-act="pool-save"]',
      'pf-bm': '[data-act="pool-save"]',
      'pf-bd': '[data-act="pool-save"]',
      'pf-ey': '[data-act="pool-save"]',
      'pf-em': '[data-act="pool-save"]',
      'pf-ed': '[data-act="pool-save"]',
    };
    if (map[f]) {
      e.preventDefault();
      const scope = f === 'artist-input' ? e.target.closest('[data-match]')
        : f === 'artist-credit-all' ? e.target.closest('[data-group]') : S.overlay;
      scope.querySelector(map[f]).click();
    } else if (f === 'role-text') {
      e.preventDefault();
      e.target.blur();
    }
  }

  // ===========================================================================
  // 10. Dashboard, launcher, language switch, entry point
  // ===========================================================================

  // --- Movable, resizable windows (dashboard and log) and text size ---------------------------

  const GEOM_KEYS = { panel: 'dci-geom:panel', log: 'dci-geom:log' };
  const movable = [];
  let topZ = 10002;
  S.scale = Number(readJson('localStorage', 'dci-scale', 1)) || 1;

  /** The browser's default font size ("medium"), independent of the page's own CSS. */
  function browserFontPx() {
    const probe = document.createElement('div');
    probe.style.cssText = 'position:absolute;visibility:hidden;font-size:medium;';
    document.documentElement.appendChild(probe);
    const px = parseFloat(getComputedStyle(probe).fontSize) || 16;
    probe.remove();
    return px;
  }

  /** 13 px at the usual 16 px browser default; follows the browser setting and the text size control. */
  const basePx = () => ((browserFontPx() * 13) / 16) * S.scale;

  function applyScale() {
    const fs = `${basePx().toFixed(2)}px`;
    [S.overlay, S.logEl].forEach((el) => { if (el) el.style.setProperty('--dci-fs', fs); });
  }

  function setScale(scale) {
    S.scale = Math.min(1.8, Math.max(0.8, Math.round(scale * 10) / 10));
    writeJson('localStorage', 'dci-scale', S.scale);
    applyScale();
    renderZoom();
    movable.forEach((m) => clampWindow(m.win));
  }

  function renderZoom() {
    const el = S.overlay && S.overlay.querySelector('[data-el="zoom"]');
    if (el) el.textContent = `${Math.round(S.scale * 100)} %`;
  }

  function defaultGeom(kind) {
    const W = window.innerWidth;
    const H = window.innerHeight;
    const unit = basePx() / 13;
    if (kind === 'panel') {
      const w = Math.min(W - 24, Math.round(1280 * unit));
      return { x: Math.round((W - w) / 2), y: 12, w, h: H - 24 };
    }
    const w = Math.min(W - 32, Math.round(420 * unit));
    const h = Math.min(H - 32, Math.round(240 * unit));
    return { x: 16, y: H - h - 16, w, h };
  }

  /**
   * Places a window. While dragging it may leave the screen partly, but its title bar stays reachable;
   * with "fit" (opening, screen changes) it is moved fully into view.
   */
  function placeWindow(win, g, fit = false) {
    const W = window.innerWidth;
    const H = window.innerHeight;
    const w = Math.max(160, Math.min(g.w, W));
    const h = Math.max(100, Math.min(g.h, H));
    const x = fit ? Math.min(Math.max(g.x, 0), W - w) : Math.min(Math.max(g.x, 80 - w), W - 80);
    const y = fit ? Math.min(Math.max(g.y, 0), H - h) : Math.min(Math.max(g.y, 0), H - 40);
    Object.assign(win.style, {
      left: `${Math.round(x)}px`, top: `${Math.round(y)}px`, width: `${Math.round(w)}px`, height: `${Math.round(h)}px`, right: 'auto', bottom: 'auto',
    });
  }

  const geomOf = (win) => {
    const r = win.getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height };
  };

  function clampWindow(win) {
    if (win.isConnected && win.getBoundingClientRect().width) placeWindow(win, geomOf(win), true);
  }

  function bringToFront(kind) {
    const el = kind === 'panel' ? S.overlay : S.logEl;
    if (el) el.style.zIndex = String(++topZ);
  }

  /** Drag by the title bar; the size is changed with the grip in the lower right corner. Both are remembered. */
  /** Saves a window's geometry, but only while it is on the page and visible. */
  function saveGeom(win, kind) {
    const g = geomOf(win);
    if (win.isConnected && g.w >= 100 && g.h >= 60) writeJson('localStorage', GEOM_KEYS[kind], g);
  }

  function makeMovable(win, handleSelector, kind) {
    const saved = readJson('localStorage', GEOM_KEYS[kind], null);
    const valid = saved && saved.w >= 160 && saved.h >= 100;
    placeWindow(win, valid ? saved : defaultGeom(kind), true);
    win.addEventListener('pointerdown', (e) => {
      bringToFront(kind);
      const handle = e.target.closest(handleSelector);
      if (!handle || e.button !== 0 || e.target.closest('button, input, select, textarea, a, label, option')) return;
      e.preventDefault();
      const start = geomOf(win);
      const dx = e.clientX - start.x;
      const dy = e.clientY - start.y;
      win.setPointerCapture(e.pointerId);
      win.classList.add('dci-moving');
      const move = (ev) => placeWindow(win, { ...start, x: ev.clientX - dx, y: ev.clientY - dy });
      const end = () => {
        win.removeEventListener('pointermove', move);
        win.removeEventListener('pointerup', end);
        win.removeEventListener('pointercancel', end);
        win.classList.remove('dci-moving');
        saveGeom(win, kind);
      };
      win.addEventListener('pointermove', move);
      win.addEventListener('pointerup', end);
      win.addEventListener('pointercancel', end);
    });
    let timer = null;
    const ro = new ResizeObserver(() => {
      if (!win.isConnected) {
        ro.disconnect();
        return;
      }
      if (!win.getBoundingClientRect().width || win.classList.contains('dci-moving')) return;
      clearTimeout(timer);
      timer = setTimeout(() => saveGeom(win, kind), 400);
    });
    ro.observe(win);
    for (let i = movable.length - 1; i >= 0; i--) if (!movable[i].win.isConnected) movable.splice(i, 1);
    movable.push({ win, kind });
  }

  function resetWindows() {
    for (const m of movable) {
      if (!m.win.isConnected) continue;
      writeJson('localStorage', GEOM_KEYS[m.kind], null);
      placeWindow(m.win, defaultGeom(m.kind));
    }
  }

  window.addEventListener('resize', () => movable.forEach((m) => clampWindow(m.win)));

  function buildOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'dci-overlay';
    overlay.hidden = true;
    overlay.lang = LANG;
    const levelBtn = (level) => `<button type="button" data-act="bulk-level" data-level="${level}">${esc(tr(`level.${level}`))}</button>`;
    overlay.innerHTML = `
      <div class="dci-panel" role="dialog" aria-labelledby="dci-title">
        <header class="dci-head">
          <h2 id="dci-title">${esc(tr('title'))}</h2>
          <div class="dci-source" data-el="source"></div>
          <div class="dci-sync" data-el="sync" aria-live="polite"></div>
          <div class="dci-head-tools">
            <label class="dci-lang">${esc(tr('lang.label'))}
              <select data-f="lang">${Object.entries(LANGS).map(([code, name]) => `<option value="${code}" ${code === LANG ? 'selected' : ''}>${name}</option>`).join('')}</select>
            </label>
            <span class="dci-zoom" role="group" aria-label="${esc(tr('zoom.label'))}">
              <button type="button" class="dci-headbtn" data-act="zoom-out" title="${esc(tr('zoom.smaller'))}" aria-label="${esc(tr('zoom.smaller'))}">A−</button>
              <span data-el="zoom" aria-live="polite">${Math.round(S.scale * 100)} %</span>
              <button type="button" class="dci-headbtn" data-act="zoom-in" title="${esc(tr('zoom.larger'))}" aria-label="${esc(tr('zoom.larger'))}">A+</button>
            </span>
            <button type="button" class="dci-headbtn" data-act="window-reset" title="${esc(tr('window.reset'))}" aria-label="${esc(tr('window.reset'))}">⤢</button>
            <button type="button" class="dci-headbtn" data-act="log">${esc(tr('log.title'))}</button>
            <button type="button" class="dci-close" data-act="close">${esc(tr('common.close'))}</button>
          </div>
        </header>
        <div class="dci-body" data-el="body">
          <div class="dci-busy" data-el="busy" role="status" hidden></div>
          <div class="dci-msgs" data-el="msgs" aria-live="polite"></div>
          <section class="dci-dates" data-el="dates" aria-label="${esc(tr('date.title'))}" hidden></section>
          <div class="dci-toolbar" data-el="toolbar" hidden>
            <span>${esc(tr('toolbar.levelAll'))}</span>
            <div class="dci-seg" role="group" aria-label="${esc(tr('toolbar.levelAll'))}">
              ${levelBtn('recording')}${levelBtn('release')}${levelBtn('skip')}
            </div>
            <label class="dci-check"><input type="checkbox" data-f="filter-missing" ${S.onlyMissing ? 'checked' : ''}> ${esc(tr('toolbar.onlyMissing'))}</label>
            <span class="dci-legend"><span class="dci-swatch dci-swatch-exists" aria-hidden="true"></span>${esc(tr('legend.exists'))}
              <span class="dci-swatch dci-swatch-some" aria-hidden="true"></span>${esc(tr('legend.existsSome'))}</span>
            <span class="dci-bulk">${esc(tr('toolbar.roleCredits'))}
              <button type="button" class="dci-textbtn" data-act="bulk-credit" data-kind="role" data-mode="discogs">${esc(tr('toolbar.asOnDiscogs'))}</button>
              <button type="button" class="dci-textbtn" data-act="bulk-credit" data-kind="role" data-mode="clear">${esc(tr('toolbar.clearAll'))}</button>
            </span>
            <span class="dci-bulk">${esc(tr('toolbar.artistCredits'))}
              <button type="button" class="dci-textbtn" data-act="bulk-credit" data-kind="artist" data-mode="discogs">${esc(tr('toolbar.asOnDiscogs'))}</button>
              <button type="button" class="dci-textbtn" data-act="bulk-credit" data-kind="artist" data-mode="clear">${esc(tr('toolbar.clearAll'))}</button>
            </span>
          </div>
          <div data-el="groups"></div>
          <section class="dci-companies" data-el="companies" hidden></section>
          <section class="dci-companies dci-others" data-el="others" hidden></section>
          <section class="dci-works" data-el="works" hidden></section>
          <div class="dci-manual" data-el="manual" hidden>
            <h3>${esc(tr('manual.title'))}</h3>
            <p class="dci-muted">${esc(tr('manual.hint'))}</p>
            <div class="dci-manual-form">
              <input type="text" data-f="manual-artist" placeholder="${esc(tr('manual.entityPlaceholder'))}" aria-label="${esc(tr('manual.artistAria'))}">
              <input type="text" data-f="manual-role" list="dci-dl-roles-artist" placeholder="${esc(tr('manual.rolePlaceholder'))}" aria-label="${esc(tr('role.aria'))}">
              <button type="button" data-act="add-manual">${esc(tr('manual.add'))}</button>
            </div>
            <div class="dci-sub">${esc(tr('manual.search'))}
              ${['artist', 'label', 'place', 'area', 'event', 'series', 'recording', 'release', 'release_group', 'work', 'instrument']
                .map((et) => `<a href="/search?type=${et}&method=indexed" target="_blank" rel="noopener">${esc(tr(`entity.${et}`))}</a>`).join(' · ')}</div>
            <div class="dci-err" data-el="manual-err"></div>
          </div>
          <div data-el="datalists"></div>
        </div>
        <div class="dci-preview" data-el="preview" hidden></div>
        <footer class="dci-foot">
          <div class="dci-sum" data-el="sum"></div>
          <div class="dci-foot-actions">
            <button type="button" class="dci-panic" data-act="panic" hidden title="${esc(tr('panic.title'))}"></button>
            <button type="button" class="dci-textbtn" data-act="preview" aria-expanded="${S.previewOpen}">${esc(tr('footer.preview'))}</button>
            <label class="dci-check"><input type="checkbox" data-f="editnote" ${S.editNote ? 'checked' : ''}> ${esc(tr('footer.editNote'))}</label>
            <button type="button" class="dci-apply" data-act="apply" disabled>${esc(tr('footer.apply'))}</button>
          </div>
          <p class="dci-hint">${esc(tr('footer.hint'))}</p>
        </footer>
      </div>
      <div class="dci-subdlg" data-el="sub" hidden>
        <div class="dci-sub-panel" role="dialog" aria-modal="true" aria-labelledby="dci-sub-title">
          <header class="dci-sub-head">
            <h3 id="dci-sub-title" data-el="sub-title"></h3>
            <button type="button" data-act="sub-window">${esc(tr('sub.window'))}</button>
            <button type="button" class="dci-close" data-act="sub-close">${esc(tr('common.cancel'))}</button>
          </header>
          <div class="dci-sub-info" data-el="sub-info"></div>
          <iframe class="dci-sub-frame" data-el="sub-frame" title="${esc(tr('sub.frameTitle'))}"></iframe>
        </div>
      </div>`;
    document.body.appendChild(overlay);
    overlay.classList.toggle('dci-only-missing', S.onlyMissing);
    overlay.addEventListener('click', onStampClick, true);
    overlay.addEventListener('click', onClick);
    overlay.addEventListener('change', onChange);
    overlay.addEventListener('input', onInput);
    overlay.addEventListener('paste', onPaste);
    overlay.addEventListener('keydown', onKeydown);
    S.overlay = overlay;
    applyScale();
    makeMovable(overlay.querySelector('.dci-panel'), '.dci-head', 'panel');
    // Rows scrolled into view (keyboard, jumps) must not end up under the sticky date pool.
    const body = overlay.querySelector('[data-el="body"]');
    const datesBar = overlay.querySelector('[data-el="dates"]');
    new ResizeObserver(() => { body.style.scrollPaddingTop = `${datesBar.offsetHeight + 8}px`; }).observe(datesBar);
    overlay.addEventListener('focusin', onFocusSource);
    overlay.addEventListener('click', onFocusSource);
    overlay.addEventListener('mouseover', onHover);
    overlay.addEventListener('mouseleave', onHoverEnd);
  }

  /** Re-creates everything that shows text, e.g. after switching the language. */
  function renderAll() {
    renderSource();
    renderSync();
    renderDates();
    renderMessages();
    renderBusy();
    if (S.initialized) {
      renderDatalists();
      $('manual').hidden = false;
    }
    $('toolbar').hidden = !S.rows.length;
    renderGroups();
    renderWorks();
    refresh();
  }

  function setLanguage(code) {
    if (!LANGS[code] || code === LANG) return;
    LANG = code;
    writeJson('localStorage', 'dci-lang', code);
    if (S.subDialog) S.subDialog.cancel();
    const wasOpen = S.overlay && !S.overlay.hidden;
    if (S.overlay) S.overlay.remove();
    S.overlay = null;
    buildOverlay();
    S.overlay.hidden = !wasOpen;
    renderAll();
    renderLog();
    renderLauncher();
    renderControls();
    const select = S.overlay.querySelector('[data-f="lang"]');
    if (select) select.focus();
  }

  async function openDashboard() {
    if (!S.overlay) buildOverlay();
    S.lastFocus = document.activeElement;
    S.overlay.hidden = false;
    clampWindow(S.overlay.querySelector('.dci-panel'));
    bringToFront('panel');
    S.overlay.querySelector('.dci-close').focus();
    if (!S.logEl) buildLogWindow();
    setLogVisible(readJson('localStorage', 'dci-log-open', true));
    renderSync();
    toDiscogs({ type: 'ping' });
    clearInterval(S.syncTimer);
    S.syncTimer = setInterval(() => toDiscogs({ type: 'ping' }), 3000);
    if (!S.initialized) await init();
  }

  /** Opens the dashboard, or brings it back into view and to the front if it is already open. */
  function showDashboard() {
    if (!S.overlay || S.overlay.hidden) {
      openDashboard();
      return;
    }
    const panel = S.overlay.querySelector('.dci-panel');
    clampWindow(panel);
    bringToFront('panel');
    S.overlay.querySelector('.dci-close').focus();
  }

  function closeDashboard() {
    if (!S.overlay || S.overlay.hidden) return;
    S.overlay.hidden = true;
    clearInterval(S.syncTimer);
    if (S.lastFocus && typeof S.lastFocus.focus === 'function') S.lastFocus.focus();
  }

  function renderLauncher() {
    const bar = document.getElementById('dci-launcher');
    if (!bar) return;
    bar.querySelector('#dci-open').textContent = tr('launcher.open');
    bar.querySelector('#dci-log-open').textContent = tr('log.title');
    bar.querySelector('#dci-launch-status').textContent = S.launchStatus ? tr(S.launchStatus.key, S.launchStatus.params) : '';
  }

  function insertLauncher() {
    if (document.getElementById('dci-launcher')) return;
    const controls = document.createElement('div');
    controls.id = 'dci-controls';
    const bar = document.createElement('div');
    bar.id = 'dci-launcher';
    bar.innerHTML = `<button type="button" id="dci-open"></button>
      <button type="button" id="dci-log-open" class="dci-textbtn"></button>
      <span id="dci-launch-status" aria-live="polite"></span>`;
    const anchor = document.querySelector('div.tabs');
    if (anchor) anchor.after(controls, bar);
    else (document.getElementById('content') || document.body).prepend(controls, bar);
    bar.querySelector('#dci-open').addEventListener('click', openDashboard);
    bar.querySelector('#dci-log-open').addEventListener('click', () => setLogVisible(!S.logEl || S.logEl.hidden));
    renderLauncher();
    renderControls();
    // Ask the companion (if installed) for its status, so the bar shows it before the dashboard is opened.
    toDiscogs({ type: 'ping' });
  }

  // The mode switch exists in the page bar and in the dashboard header.
  document.addEventListener('click', (e) => {
    const b = e.target.closest && e.target.closest('[data-sync-mode]');
    if (b) setSyncMode(b.dataset.syncMode);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape' || !S.overlay || S.overlay.hidden) return;
    // The dashboard does not block the page, so Escape only acts when the focus is inside it.
    if (!S.overlay.contains(document.activeElement)) return;
    if (S.stampId) {
      S.stampId = null;
      renderDates();
      return;
    }
    if (S.subDialog) S.subDialog.cancel();
    else closeDashboard();
  });

  function injectStyles() {
    const style = document.createElement('style');
    style.id = 'dci-styles';
    style.textContent = `
      #dci-launcher { display: flex; align-items: center; gap: 12px; margin: 10px 0 6px; }
      #dci-open { font: inherit; padding: 4px 12px; border: 1px solid #736dab; border-radius: 3px; background: #fff; color: #4b4585; cursor: pointer; }
      #dci-open:hover { background: #f1f0f8; }
      #dci-launch-status { color: #4b4585; }
      #dci-launcher .dci-textbtn { border: 0; background: none; color: #4b4585; text-decoration: underline; cursor: pointer; font: inherit; }
      #dci-controls { display: flex; align-items: center; flex-wrap: wrap; gap: 6px 12px; margin: 10px 0 0; font-size: 12px; color: #4b4585; }
      #dci-controls[hidden] { display: none; }
      #dci-controls .dci-syncstatus { color: #6d6a7c; }
      .dci-syncmode { display: inline-flex; align-items: center; gap: calc(var(--u, 1px) * 6); }
      .dci-seg.dci-seg-small button { padding: 1px calc(var(--u, 1px) * 8); font-size: calc(var(--u, 1px) * 12); }
      #dci-controls .dci-seg { display: inline-flex; border: 1px solid #c8c5d6; border-radius: 3px; overflow: hidden; }
      #dci-controls .dci-seg button { border: 0; background: #fff; color: #262430; cursor: pointer; font: inherit; }
      #dci-controls .dci-seg button + button { border-left: 1px solid #c8c5d6; }
      #dci-controls .dci-seg button[aria-pressed="true"] { background: #736dab; color: #fff; }
      #dci-log {
        --u: calc(var(--dci-fs, 13px) / 13);
        box-sizing: border-box; position: fixed; left: calc(var(--u, 1px) * 16); bottom: calc(var(--u, 1px) * 16); z-index: 10002; display: flex; flex-direction: column;
        width: calc(var(--u, 1px) * 420); height: calc(var(--u, 1px) * 240); min-width: calc(var(--u, 1px) * 260); min-height: calc(var(--u, 1px) * 120); max-width: calc(100vw - calc(var(--u, 1px) * 32)); max-height: calc(100vh - calc(var(--u, 1px) * 32));
        resize: both; overflow: hidden; background: #fff; color: #262430; border: 1px solid #c8c5d6; border-top: 3px solid #736dab;
        border-radius: 4px; box-shadow: 0 4px 16px rgba(38, 36, 48, 0.18); font-size: calc(var(--u, 1px) * 12); line-height: 1.4;
      }
      #dci-log[hidden] { display: none; }
      #dci-log .dci-log-head { display: flex; align-items: center; gap: calc(var(--u, 1px) * 6); padding: calc(var(--u, 1px) * 5) calc(var(--u, 1px) * 8); border-bottom: 1px solid #dddae8; background: #f7f6fb; }
      #dci-log h2 { margin: 0 auto 0 0; font-size: calc(var(--u, 1px) * 13); font-weight: 600; color: #4b4585; }
      #dci-log .dci-log-dash { border-color: #736dab; color: #4b4585; font-weight: 600; }
      #dci-log button { font: inherit; border: 1px solid #c8c5d6; background: #fff; border-radius: 3px; padding: 0 calc(var(--u, 1px) * 7); cursor: pointer; }
      #dci-log ol { flex: 1; margin: 0; padding: calc(var(--u, 1px) * 4) calc(var(--u, 1px) * 8); list-style: none; overflow: auto; font-variant-numeric: tabular-nums; }
      #dci-log li { padding: 1px 0; border-bottom: 1px solid #f1f0f6; }
      #dci-log time { color: #6d6a7c; margin-right: calc(var(--u, 1px) * 4); }
      #dci-log .dci-log-ok { color: #2f7a4b; }
      #dci-log .dci-log-warn { color: #9a5b00; }
      #dci-log .dci-log-error { color: #b3261e; }
      html.dci-lock, html.dci-lock body { overflow: hidden; }

      #dci-overlay {
        --ink: #262430; --muted: #6d6a7c; --line: #dddae8; --row: #efedf5; --soft: #f7f6fb;
        --purple: #736dab; --purple-d: #4b4585; --orange: #eb743b; --orange-d: #c55a24;
        --ok: #2f7a4b; --warn: #9a5b00; --err: #b3261e; --teal: #2f7571;
        /* All sizes follow --dci-fs: the browser's font size setting times the text size control */
        --u: calc(var(--dci-fs, 13px) / 13);
        position: fixed; inset: 0; z-index: 10000; pointer-events: none;
        color: var(--ink); font-size: var(--dci-fs, 13px); line-height: 1.45;
      }
      #dci-overlay[hidden], #dci-overlay [hidden] { display: none !important; }
      #dci-overlay * { box-sizing: border-box; }
      #dci-overlay :focus-visible { outline: 2px solid var(--purple); outline-offset: 1px; }
      #dci-overlay input[type="text"], #dci-overlay select {
        font: inherit; padding: 3px calc(var(--u, 1px) * 6); border: 1px solid #c8c5d6; border-radius: 3px; background: #fff; color: var(--ink); max-width: 100%;
      }
      #dci-overlay button { font: inherit; cursor: pointer; }
      #dci-overlay a { color: var(--purple-d); }

      .dci-panel {
        position: fixed; left: 2vw; top: 2vh; width: 96vw; height: 96vh; pointer-events: auto; display: flex; flex-direction: column;
        min-width: min(calc(var(--u, 1px) * 360), 100vw); min-height: min(calc(var(--u, 1px) * 240), 100vh); max-width: 100vw; max-height: 100vh;
        resize: both; overflow: hidden; background: #fff; border: 1px solid #c8c5d6; border-top: 4px solid var(--purple); border-radius: 4px;
        box-shadow: 0 8px 32px rgba(38, 36, 48, 0.28);
      }
      .dci-head, #dci-log .dci-log-head { cursor: move; touch-action: none; }
      .dci-moving { user-select: none; opacity: 0.97; }
      .dci-zoom { display: inline-flex; align-items: center; gap: 4px; color: var(--muted); font-size: calc(var(--u, 1px) * 12); font-variant-numeric: tabular-nums; }
      .dci-zoom [data-el="zoom"] { min-width: 3.4em; text-align: center; }
      .dci-head { display: flex; align-items: center; gap: calc(var(--u, 1px) * 8) calc(var(--u, 1px) * 20); flex-wrap: wrap; padding: calc(var(--u, 1px) * 12) calc(var(--u, 1px) * 20); border-bottom: 1px solid var(--line); }
      .dci-head h2 { margin: 0; font-size: calc(var(--u, 1px) * 18); font-weight: 600; color: var(--purple-d); }
      .dci-source { flex: 1 1 calc(var(--u, 1px) * 400); display: flex; align-items: center; gap: calc(var(--u, 1px) * 8) calc(var(--u, 1px) * 12); flex-wrap: wrap; color: var(--muted); }
      .dci-other { display: inline-flex; gap: calc(var(--u, 1px) * 6); }
      .dci-other input { width: calc(var(--u, 1px) * 240); }
      .dci-close, .dci-headbtn { border: 1px solid var(--line); background: #fff; border-radius: 3px; padding: calc(var(--u, 1px) * 4) calc(var(--u, 1px) * 10); }
      .dci-head-tools { display: flex; align-items: center; gap: calc(var(--u, 1px) * 8); margin-left: auto; }
      .dci-lang { display: inline-flex; align-items: center; gap: calc(var(--u, 1px) * 6); color: var(--muted); font-size: calc(var(--u, 1px) * 12); }
      .dci-panic { border: 1px solid var(--err); background: #fff; color: var(--err); border-radius: 3px; padding: calc(var(--u, 1px) * 5) calc(var(--u, 1px) * 10); font-weight: 600; }
      .dci-panic:hover { background: #fbeceb; }

      .dci-body { flex: 1; overflow: auto; padding: calc(var(--u, 1px) * 14) calc(var(--u, 1px) * 20) calc(var(--u, 1px) * 28); }
      .dci-busy { padding: calc(var(--u, 1px) * 6) 0 calc(var(--u, 1px) * 10); color: var(--purple-d); font-weight: 600; }
      .dci-msg { margin: 0 0 calc(var(--u, 1px) * 8); padding: calc(var(--u, 1px) * 8) calc(var(--u, 1px) * 12); border-left: 3px solid var(--purple); background: var(--soft); max-width: 80ch; }
      .dci-msg-warn { border-left-color: var(--warn); }
      .dci-msg-error { border-left-color: var(--err); }
      .dci-msg-ok { border-left-color: var(--ok); }
      .dci-inline-btn { margin-left: calc(var(--u, 1px) * 8); border: 1px solid var(--ok); background: #fff; color: var(--ok); border-radius: 3px; padding: 1px calc(var(--u, 1px) * 8); }

      .dci-toolbar { display: flex; align-items: center; gap: calc(var(--u, 1px) * 10) calc(var(--u, 1px) * 16); flex-wrap: wrap; margin: calc(var(--u, 1px) * 4) 0 calc(var(--u, 1px) * 16); }
      .dci-only-missing .dci-group:not(.dci-st-missing):not(.dci-st-ambiguous),
      .dci-only-missing .dci-group.dci-all-skip { display: none; }

      .dci-group { margin: 0 0 calc(var(--u, 1px) * 22); padding: 2px 0 calc(var(--u, 1px) * 6) calc(var(--u, 1px) * 14); border-left: 3px solid var(--line); }
      .dci-st-linked, .dci-st-manual { border-left-color: var(--purple); }
      .dci-st-missing, .dci-st-ambiguous { border-left-color: var(--err); }
      .dci-group.dci-all-skip { border-left-color: var(--line); }
      .dci-ghead { display: flex; align-items: baseline; gap: calc(var(--u, 1px) * 6) calc(var(--u, 1px) * 18); flex-wrap: wrap; margin-bottom: calc(var(--u, 1px) * 6); }
      .dci-gname strong { font-size: calc(var(--u, 1px) * 15); font-weight: 600; margin-right: calc(var(--u, 1px) * 6); }
      .dci-gmatch { display: flex; align-items: center; gap: calc(var(--u, 1px) * 6) calc(var(--u, 1px) * 10); flex-wrap: wrap; }
      .dci-gmatch input { width: calc(var(--u, 1px) * 260); }
      .dci-badge { display: inline-block; padding: 1px calc(var(--u, 1px) * 7); border-radius: 10px; background: var(--soft); color: var(--muted); font-size: calc(var(--u, 1px) * 12); }
      .dci-badge-ok { background: #e9f4ee; color: var(--ok); }
      .dci-badge-bad { background: #fbeceb; color: var(--err); }

      .dci-tablewrap { overflow-x: auto; }
      .dci-table { width: 100%; min-width: calc(var(--u, 1px) * 1180); border-collapse: collapse; }
      .dci-table.dci-worktable { min-width: calc(var(--u, 1px) * 620); }
      .dci-table th { padding: calc(var(--u, 1px) * 4) calc(var(--u, 1px) * 8); text-align: left; font-size: calc(var(--u, 1px) * 12); font-weight: 600; color: var(--muted); border-bottom: 1px solid var(--line); }
      .dci-table td { padding: calc(var(--u, 1px) * 7) calc(var(--u, 1px) * 8); vertical-align: top; border-bottom: 1px solid var(--row); }
      .dci-c-role { width: 16%; } .dci-c-type { width: 14%; } .dci-c-attr { width: 26%; } .dci-c-level { width: 15%; } .dci-c-date { width: 16%; } .dci-c-tracks { width: 13%; }
      .dci-c-type select { width: 100%; min-width: calc(var(--u, 1px) * 140); }
      .dci-row.dci-lv-skip td { background: var(--soft); }
      .dci-row.dci-lv-skip .dci-drole { color: var(--muted); }
      .dci-drole { font-weight: 600; }
      .dci-sub { color: var(--muted); font-size: calc(var(--u, 1px) * 12); }
      .dci-note { margin-top: 3px; font-size: calc(var(--u, 1px) * 12); color: var(--muted); }
      .dci-warn { color: var(--warn); }
      .dci-bad { color: var(--err); }
      .dci-ok { color: var(--ok); }
      .dci-muted { color: var(--muted); }
      .dci-err { margin-top: calc(var(--u, 1px) * 4); color: var(--err); font-size: calc(var(--u, 1px) * 12); flex-basis: 100%; }

      .dci-primary { display: flex; align-items: center; gap: calc(var(--u, 1px) * 6); margin-bottom: calc(var(--u, 1px) * 4); }
      .dci-primary input { flex: 1; min-width: 0; }
      #dci-overlay .dci-primary input.dci-invalid { border-color: var(--err); background: #fff7f6; }
      .dci-mark { font-size: calc(var(--u, 1px) * 12); min-width: calc(var(--u, 1px) * 60); }
      .dci-flags { display: flex; flex-wrap: wrap; gap: 2px calc(var(--u, 1px) * 12); margin-bottom: calc(var(--u, 1px) * 4); }
      .dci-check { display: inline-flex; align-items: center; gap: calc(var(--u, 1px) * 4); white-space: nowrap; }
      .dci-credit { display: flex; align-items: center; gap: calc(var(--u, 1px) * 6); margin-top: 3px; color: var(--muted); font-size: calc(var(--u, 1px) * 12); }
      .dci-credit input { flex: 1; min-width: 0; }
      .dci-c-attr .dci-credit { display: grid; grid-template-columns: calc(var(--u, 1px) * 92) 1fr; }
      .dci-dest { margin: 1px 0 2px calc(var(--u, 1px) * 98); font-size: calc(var(--u, 1px) * 12); color: var(--muted); }
      .dci-dest:empty { display: none; }
      .dci-bracket { font-weight: 400; color: var(--purple-d); }
      .dci-variants { display: flex; align-items: center; flex-wrap: wrap; gap: calc(var(--u, 1px) * 4) calc(var(--u, 1px) * 12); margin: 0 0 calc(var(--u, 1px) * 6); color: var(--muted); font-size: calc(var(--u, 1px) * 12); }
      .dci-variants .dci-anv { color: var(--ink); font-weight: 600; }
      .dci-variants .dci-credit { margin-top: 0; }
      .dci-variants input { width: calc(var(--u, 1px) * 200); }
      .dci-variants button { border: 1px solid #c8c5d6; background: #fff; border-radius: 3px; padding: 1px calc(var(--u, 1px) * 8); font-size: calc(var(--u, 1px) * 12); }
      .dci-bulk { display: inline-flex; align-items: center; gap: calc(var(--u, 1px) * 8); color: var(--muted); }
      .dci-st-created { border-left-color: var(--purple); }
      .dci-seg button[aria-pressed="true"][data-level="work"] { background: var(--teal); color: #fff; }
      .dci-badge-plan { background: #e6f2f1; color: var(--teal); }
      .dci-sync { font-size: calc(var(--u, 1px) * 12); color: var(--muted); display: flex; align-items: center; gap: calc(var(--u, 1px) * 6); }
      .dci-sync button, .dci-works-bar button, .dci-w-actions button:not(.dci-textbtn), .dci-candidates button, .dci-gmatch button:not(.dci-textbtn) {
        border: 1px solid #c8c5d6; background: #fff; border-radius: 3px; padding: 1px calc(var(--u, 1px) * 8); }
      .dci-works { margin: calc(var(--u, 1px) * 8) 0 calc(var(--u, 1px) * 22); padding: 2px 0 calc(var(--u, 1px) * 6) calc(var(--u, 1px) * 14); border-left: 3px solid var(--teal); }
      .dci-works h3 { margin: 0 0 calc(var(--u, 1px) * 4); font-size: calc(var(--u, 1px) * 15); font-weight: 600; }
      .dci-works > p { margin: 0 0 calc(var(--u, 1px) * 8); max-width: 80ch; }
      .dci-works-bar { display: flex; align-items: center; flex-wrap: wrap; gap: calc(var(--u, 1px) * 8) calc(var(--u, 1px) * 16); margin-bottom: calc(var(--u, 1px) * 8); }
      .dci-worktable { min-width: calc(var(--u, 1px) * 700); }
      .dci-w-track { width: 30%; } .dci-w-actions { width: 22%; white-space: nowrap; }
      .dci-candidates { list-style: none; margin: calc(var(--u, 1px) * 6) 0 0; padding: 0; }
      .dci-candidates li { display: flex; flex-wrap: wrap; align-items: baseline; gap: calc(var(--u, 1px) * 4) calc(var(--u, 1px) * 8); padding: 3px 0; border-top: 1px solid var(--row); }
      .dci-subdlg { pointer-events: auto; position: fixed; inset: 0; z-index: 10001; display: flex; align-items: center; justify-content: center; padding: calc(var(--u, 1px) * 24); background: rgba(38, 36, 48, 0.35); }
      .dci-sub-panel { display: flex; flex-direction: column; width: min(calc(var(--u, 1px) * 1100), 100%); height: 100%; background: #fff; border-top: 4px solid var(--orange); border-radius: 4px; overflow: hidden; }
      .dci-sub-head { display: flex; align-items: center; gap: calc(var(--u, 1px) * 10); padding: calc(var(--u, 1px) * 10) calc(var(--u, 1px) * 16); border-bottom: 1px solid var(--line); }
      .dci-sub-head h3 { margin: 0 auto 0 0; font-size: calc(var(--u, 1px) * 15); font-weight: 600; }
      .dci-sub-head button { border: 1px solid var(--line); background: #fff; border-radius: 3px; padding: 3px calc(var(--u, 1px) * 10); }
      .dci-sub-info { padding: calc(var(--u, 1px) * 8) calc(var(--u, 1px) * 16); background: var(--soft); border-bottom: 1px solid var(--line); max-height: 30vh; overflow: auto; }
      .dci-sub-info p { margin: 0 0 calc(var(--u, 1px) * 4); max-width: 90ch; }
      .dci-sub-frame { flex: 1; width: 100%; border: 0; }

      .dci-seg { display: inline-flex; border: 1px solid #c8c5d6; border-radius: 3px; overflow: hidden; }
      .dci-seg button { border: 0; background: #fff; color: var(--ink); padding: 3px calc(var(--u, 1px) * 8); }
      .dci-seg button + button { border-left: 1px solid #c8c5d6; }
      .dci-seg button:hover { background: var(--soft); }
      .dci-row.dci-exists > td { background: #e6f3ea; }
      .dci-row.dci-exists-some > td { background: #f3f9f4; }
      .dci-row.dci-exists > td:first-child { box-shadow: inset 4px 0 0 var(--ok); }
      .dci-row.dci-exists-some > td:first-child { box-shadow: inset 4px 0 0 #9fcfae; }
      .dci-legend { display: inline-flex; align-items: center; gap: calc(var(--u, 1px) * 6); color: var(--muted); font-size: calc(var(--u, 1px) * 12); }
      .dci-swatch { display: inline-block; width: calc(var(--u, 1px) * 14); height: calc(var(--u, 1px) * 14); border-radius: 2px; border: 1px solid #b7d9c1; }
      .dci-swatch-exists { background: #e6f3ea; box-shadow: inset 3px 0 0 var(--ok); }
      .dci-swatch-some { background: #f3f9f4; box-shadow: inset 3px 0 0 #9fcfae; margin-left: calc(var(--u, 1px) * 6); }
      .dci-sync { display: flex; align-items: center; flex-wrap: wrap; gap: calc(var(--u, 1px) * 4) calc(var(--u, 1px) * 10); }

      /* Date pool: stays visible at the top while scrolling */
      .dci-dates { position: sticky; top: calc(var(--u, 1px) * -14); z-index: 3; margin: calc(var(--u, 1px) * -14) calc(var(--u, 1px) * -20) calc(var(--u, 1px) * 14); padding: calc(var(--u, 1px) * 8) calc(var(--u, 1px) * 20); background: #fbfaff; border-bottom: 1px solid var(--line); box-shadow: 0 2px 4px rgba(38, 36, 48, 0.06); }
      .dci-dates-bar { display: flex; align-items: center; flex-wrap: wrap; gap: calc(var(--u, 1px) * 6) calc(var(--u, 1px) * 8); }
      .dci-date-chip { display: inline-flex; align-items: stretch; border: 1px solid #c8c5d6; border-radius: 12px; background: #fff; overflow: hidden; }
      .dci-date-chip button { border: 0; background: none; color: var(--ink); padding: 2px calc(var(--u, 1px) * 8); }
      .dci-date-chip .dci-chip-main { padding-left: calc(var(--u, 1px) * 10); }
      .dci-date-chip .dci-iconbtn { border-left: 1px solid #e4e2ec; }
      .dci-date-chip:hover { border-color: var(--purple); }
      .dci-date-chip.dci-active { border-color: var(--purple); background: var(--purple); }
      .dci-date-chip.dci-active button, .dci-date-chip.dci-active .dci-chip-count { color: #fff; }
      .dci-chip-count { color: var(--muted); font-size: calc(var(--u, 1px) * 11); }
      .dci-date-sugg { display: inline-flex; align-items: center; flex-wrap: wrap; gap: calc(var(--u, 1px) * 4) calc(var(--u, 1px) * 8); margin-left: calc(var(--u, 1px) * 8); }
      .dci-stamp-bar { display: flex; align-items: center; flex-wrap: wrap; gap: calc(var(--u, 1px) * 6) calc(var(--u, 1px) * 12); margin-top: calc(var(--u, 1px) * 8); padding: calc(var(--u, 1px) * 6) calc(var(--u, 1px) * 10); background: var(--row); border: 1px solid var(--purple); border-radius: 3px; }
      .dci-stamp-bar label { display: inline-flex; align-items: center; gap: calc(var(--u, 1px) * 6); }
      .dci-date-form { margin-top: calc(var(--u, 1px) * 8); padding: calc(var(--u, 1px) * 8) calc(var(--u, 1px) * 10); background: #fff; border: 1px solid var(--line); border-radius: 3px; max-width: calc(var(--u, 1px) * 520); }
      .dci-date-form .dci-sub, .dci-date-form .dci-err { margin: calc(var(--u, 1px) * 4) 0 0; }
      .dci-pool-name { display: flex; align-items: center; gap: calc(var(--u, 1px) * 6); margin-bottom: calc(var(--u, 1px) * 6); color: var(--muted); font-size: calc(var(--u, 1px) * 12); }
      .dci-apply.dci-small { padding: 3px calc(var(--u, 1px) * 12); }
      .dci-dates > .dci-sub { margin: calc(var(--u, 1px) * 4) 0 0; }
      .dci-iconbtn { border: 1px solid var(--line); background: #fff; border-radius: 3px; padding: 0 calc(var(--u, 1px) * 6); line-height: 1.6; }

      /* MB-style date fields (year, month, day) */
      .dci-c-date { min-width: calc(var(--u, 1px) * 190); }
      .dci-mbdate { font-size: calc(var(--u, 1px) * 12); }
      .dci-mbdate-line { display: flex; align-items: center; gap: 2px; margin-bottom: 3px; white-space: nowrap; }
      .dci-mbdate-label { display: inline-block; min-width: calc(var(--u, 1px) * 72); color: var(--muted); }
      .dci-dp { padding: 2px 3px; font-size: calc(var(--u, 1px) * 12); text-align: center; font-variant-numeric: tabular-nums; }
      .dci-dp-4 { width: 3.6em; }
      .dci-dp-2 { width: 2.7em; }
      .dci-mbdate-line .dci-iconbtn { margin-left: calc(var(--u, 1px) * 4); }
      .dci-mbdate-ended { font-size: calc(var(--u, 1px) * 12); margin-bottom: 3px; }
      .dci-mbdate-tools { display: flex; align-items: center; flex-wrap: wrap; gap: calc(var(--u, 1px) * 4) calc(var(--u, 1px) * 8); margin-top: 2px; }
      .dci-mbdate-tools select { max-width: calc(var(--u, 1px) * 170); font-size: calc(var(--u, 1px) * 12); }
      .dci-date-add { font-size: calc(var(--u, 1px) * 12); }
      #dci-overlay.dci-stamping .dci-c-date { cursor: copy; outline: 1px dashed var(--purple); outline-offset: -3px; background: #fbfaff; }
      #dci-overlay.dci-stamping .dci-c-date * { cursor: copy; }

      /* Companies, etc. */
      .dci-companies { margin: calc(var(--u, 1px) * 8) 0 calc(var(--u, 1px) * 22); padding-top: calc(var(--u, 1px) * 10); border-top: 1px solid var(--line); }
      .dci-companies > h3 { margin: 0 0 2px; font-size: calc(var(--u, 1px) * 15); }
      .dci-companies > p { margin: 0 0 calc(var(--u, 1px) * 12); }
      .dci-seg button[aria-pressed="true"][data-level="recording"] { background: var(--purple); color: #fff; }
      .dci-seg button[aria-pressed="true"][data-level="release"] { background: var(--orange); color: #fff; }
      .dci-seg button[aria-pressed="true"][data-level="skip"] { background: #e4e2ec; }
      #dci-overlay .dci-seg button[aria-pressed="true"][data-sync-mode] { background: var(--purple); color: #fff; }
      #dci-overlay .dci-sync .dci-seg button { border-radius: 0; border-top: 0; border-bottom: 0; border-right: 0; }

      .dci-tbtn { border: 1px solid var(--purple); background: #fff; color: var(--purple-d); border-radius: 3px; padding: 2px calc(var(--u, 1px) * 8); }
      .dci-tbtn[aria-expanded="true"] { background: var(--purple); color: #fff; }
      .dci-status { margin-top: calc(var(--u, 1px) * 4); font-size: calc(var(--u, 1px) * 12); }

      .dci-tracksrow > td { background: var(--soft); padding: calc(var(--u, 1px) * 10) calc(var(--u, 1px) * 12); }
      .dci-picker-actions { display: flex; align-items: center; flex-wrap: wrap; gap: calc(var(--u, 1px) * 6) calc(var(--u, 1px) * 8); margin-bottom: calc(var(--u, 1px) * 8); }
      .dci-picker-actions button { border: 1px solid #c8c5d6; background: #fff; border-radius: 3px; padding: 1px calc(var(--u, 1px) * 8); }
      .dci-chips { display: grid; grid-template-columns: repeat(auto-fill, minmax(calc(var(--u, 1px) * 230), 1fr)); gap: 2px calc(var(--u, 1px) * 14); }
      .dci-medium { grid-column: 1 / -1; margin-top: calc(var(--u, 1px) * 6); font-weight: 600; color: var(--muted); font-size: calc(var(--u, 1px) * 12); }
      .dci-chip { display: flex; align-items: baseline; gap: calc(var(--u, 1px) * 6); padding: 2px calc(var(--u, 1px) * 4); border-radius: 3px; cursor: pointer; min-width: 0; }
      .dci-chip:hover { background: #fff; }
      .dci-tn { font-variant-numeric: tabular-nums; min-width: 1.6em; color: var(--purple-d); }
      .dci-tt { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .dci-dot, .dci-sugg .dci-tn::after { display: inline-block; width: calc(var(--u, 1px) * 6); height: calc(var(--u, 1px) * 6); border-radius: 50%; background: var(--orange); vertical-align: middle; }
      .dci-sugg .dci-tn::after { content: ""; margin-left: calc(var(--u, 1px) * 4); }

      .dci-textbtn { border: 0; background: none; color: var(--purple-d); padding: 2px 0; text-decoration: underline; }
      .dci-manual { margin-top: calc(var(--u, 1px) * 10); padding-top: calc(var(--u, 1px) * 14); border-top: 1px solid var(--line); }
      .dci-manual h3 { margin: 0 0 calc(var(--u, 1px) * 8); font-size: calc(var(--u, 1px) * 14); font-weight: 600; }
      .dci-manual-form { display: flex; flex-wrap: wrap; gap: calc(var(--u, 1px) * 8); }
      .dci-manual-form input { width: calc(var(--u, 1px) * 300); }

      .dci-preview { max-height: 32vh; overflow: auto; padding: calc(var(--u, 1px) * 10) calc(var(--u, 1px) * 20); border-top: 1px solid var(--line); background: var(--soft); }
      .dci-preview[hidden] { display: none; }
      .dci-pv-target { margin-bottom: calc(var(--u, 1px) * 8); }
      .dci-pv-target ul { margin: 2px 0 0; padding-left: calc(var(--u, 1px) * 18); }

      .dci-foot { display: flex; align-items: center; justify-content: space-between; gap: calc(var(--u, 1px) * 10) calc(var(--u, 1px) * 20); flex-wrap: wrap; padding: calc(var(--u, 1px) * 10) calc(var(--u, 1px) * 20); border-top: 1px solid var(--line); }
      .dci-foot-actions { display: flex; align-items: center; gap: calc(var(--u, 1px) * 10) calc(var(--u, 1px) * 18); flex-wrap: wrap; }
      .dci-apply { border: 0; border-radius: 3px; padding: calc(var(--u, 1px) * 7) calc(var(--u, 1px) * 16); background: var(--orange); color: #fff; font-weight: 600; }
      .dci-apply:hover:not(:disabled) { background: var(--orange-d); }
      .dci-apply:disabled { background: #d9d6e3; color: #fff; cursor: not-allowed; }
      .dci-hint { flex-basis: 100%; margin: 0; color: var(--muted); font-size: calc(var(--u, 1px) * 12); }

      @media (max-width: 700px) {
        #dci-overlay { padding: 0; }
        .dci-panel { border-radius: 0; }
        .dci-other input, .dci-gmatch input, .dci-manual-form input { width: 100%; }
      }
    `;
    document.head.appendChild(style);
  }

  document.addEventListener('dci:from-discogs', onFromDiscogs);
  injectStyles();
  insertLauncher();
  resumePanicIfRequested();
})();
