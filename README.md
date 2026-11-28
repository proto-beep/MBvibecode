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

- **Sources:** Discogs, Bandcamp (also its track pages and the texts of its editions), YouTube descriptions, Wikipedia's infobox, any pasted text, text from cover art (booklets, back covers). More sources can be added; contradictions are shown, the sources of the release's other editions offered.
- **Entries as a matrix:** each person, label or place with its roles and the events (date, tracks, level).
- **Works matrix:** works found, linked or created, with their writers and publishers; **✨ Answer all** for the open questions.
- **Dates and tracks:** dates from every text, by drag & drop onto roles and works.
- **Compared with MusicBrainz:** what is there already is skipped; dates are supplemented, conflicts shown.
- **Fill empty recordings:** tracks without relationships get the credits the other tracks share.
- **Mapping rules:** every rule can be switched; quick switches for the common ones; profiles.
- **The log:** what was read, what was left out on purpose and why, and how long each step of an import took.
- In English, German, Spanish and French; light or dark.

## What's new

| Version | |
|---|---|
| 3.232 | More room for the entries: the head in one line, “＋ Entry” and the pools beside it, a slim head while scrolling |
| 3.231 | A click on “3 new relationships” goes to them one by one; the filter “Only new relationships”; the companion’s large image in MusicBrainz colours (companion 1.26) |
| 3.230 | The times of an import in the log: which steps took how long, per source |
| 3.227 | The companion in the dashboard’s language, Bandcamp’s artwork in high resolution (companion 1.25) |
| 3.226 | “✨ Answer all”: a tie decided by the recordings in MusicBrainz, each work to open with ↗ |
| 3.223 | The lines left out on purpose in one table, in the mapping file |
| 3.220 | “✨ Answer all” grouped by its reasons, covers of a tribute; ←/→ in the companion’s artwork |

All milestones and every version: [changelog](mb-vibecode-credits-importer-CHANGELOG.md).

## More

- [Full reference](mb-vibecode-credits-importer-v3.233.0-README.md) – every feature and setting in detail; long, written to be searched (and for AI assistants working on the code).
- [Companion](mb-vibecode-credits-importer-companion-v1.26.0-README.md)
- [Changelog](mb-vibecode-credits-importer-CHANGELOG.md) · [Code changes](mb-vibecode-credits-importer-CODE-CHANGES.md)
- Problems and ideas: [issues](https://github.com/proto-beep/MBvibecode/issues)

## License

Public domain, [CC0 1.0](LICENSE).
