# MB x Vibecode: Credits Importer

A userscript for [MusicBrainz](https://musicbrainz.org). It reads the credits of a release – from Discogs, Bandcamp, YouTube, Wikipedia, a pasted text or a scanned booklet – and stages them as relationships in MusicBrainz's release relationship editor.

**It never submits anything.** It only stages; you review and click "Enter edit".

> Created with AI: the script and its documentation were written by Claude (Anthropic). Check what it stages before you submit.

## Install

1. Install [Violentmonkey](https://violentmonkey.github.io/) or [Tampermonkey](https://www.tampermonkey.net/).
2. Open the script and your script manager offers to install it:
   [mb-vibecode-credits-importer.user.js](https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-vibecode-credits-importer.user.js)
3. Optional, the companion – it shows on the Discogs, Bandcamp or YouTube page what was taken over:
   [mb-vibecode-credits-importer-companion.user.js](https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-vibecode-credits-importer-companion.user.js)

Updates come by themselves through the script manager.

## Use

1. Open a release on MusicBrainz → **Edit relationships**.
2. Click **Import credits …**. The linked source is read; without one, choose it in **Source ▾**.
3. Check the entries: link the people, labels and places to MusicBrainz, answer what is marked orange.
4. **Stage**, look at the result in the editor, then **Enter edit**.

The footer counts what is still open: **must** (orange) before staging, **may** (yellow) suggestions.

## What it does

- **Sources:** Discogs, Bandcamp (also the texts of its editions), YouTube descriptions, Wikipedia's infobox, any pasted text, text from cover art. A second source can be added; contradictions are shown.
- **Entries as a matrix:** each person, label or place with its roles and the events (date, tracks, level).
- **Works matrix:** works found, linked or created, with their writers and publishers; **✨ Answer all** for the open questions.
- **Dates and tracks:** dates from every text, by drag & drop onto roles and works.
- **Compared with MusicBrainz:** what is there already is skipped; dates are supplemented, conflicts shown.
- **Fill empty recordings:** tracks without relationships get the credits the other tracks share.
- **Mapping rules:** every rule can be switched; quick switches for the common ones; profiles.
- In English, German, Spanish and French; light or dark.

## What's new

| Version | |
|---|---|
| 3.177 | Classical track lists: composers as headings, works as suites, soloists and authors in a track’s line |
| 3.176 | Booklets are read: lineups without a sign between name and role, tracks by medium, German role words, parts of an opera |
| 3.157 | Missing links of the entries, with a link to the edit page; Bandcamp editions read with the credits |
| 3.155 | “✨ Answer all” at the works matrix: its open questions answered by a level, with a preview and undo |
| 3.150 | “Fill empty recordings”: the tracks without relationships get the credits the other tracks share |

All milestones and every version: [changelog](mb-vibecode-credits-importer-CHANGELOG.md).

## More

- [Full reference](mb-vibecode-credits-importer-v3.178.0-README.md) – every feature and setting in detail; long, written to be searched (and for AI assistants working on the code).
- [Companion](mb-vibecode-credits-importer-companion-v1.22.0-README.md)
- [Changelog](mb-vibecode-credits-importer-CHANGELOG.md) · [Code changes](mb-vibecode-credits-importer-CODE-CHANGES.md)
- Problems and ideas: [issues](https://github.com/proto-beep/MBvibecode/issues)

## License

Public domain, [CC0 1.0](LICENSE).
