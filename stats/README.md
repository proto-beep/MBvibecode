# Global statistics

**Collected item Z-GST.** How MB x Vibecode: Credits Importer is used on MusicBrainz as a whole. The script shows it in its
statistics (**This browser | Global**, from Credits Importer 3.47.0).

- **Source:** MusicBrainz's edit dump `mbdump-edit.tar.bz2` of the latest full export (MetaBrainz, twice a week:
  `https://data.metabrainz.org/pub/musicbrainz/data/fullexport/LATEST`). It holds every edit, its data and its edit notes.
- **What counts:** the edits whose editor wrote the script's edit note on them (the line `Script: MB x Vibecode: Credits Importer v…`;
  before 3.1.0 `MB x Vibecode: Import Discogs credits`) – a voter quoting it does not count. An edit note "Simple" still counts;
  with "No note" an edit cannot be found. A **submission** is the same note of one editor within 30 minutes (MusicBrainz sends one
  "Enter edit" in parts – 25 edits a request, new works first, live comments later); its "Done:" line is counted once.
- **Result:** `stats/mb-vibecode-credits-importer-global.json` on the data branch **`stats`**
  (`https://raw.githubusercontent.com/proto-beep/MBvibecode/stats/stats/mb-vibecode-credits-importer-global.json`) – totals (edits,
  submissions, different editors), per month, per version, per edit type, status, auto-edit or voted, the relationship types, the
  sources and supplements, and what the "Done:" lines say (credit relationships per level, works linked, role credits and dates
  added).
- **Privacy:** only numbers. No editor names or ids, no edits, no releases, no URLs; "editors" is how many different ones.
- **Safety:** an archive cut off or without the tables is an error – nothing is written or committed.
- **How:** `global_stats.py` reads the archive as a stream (nothing on disk): the table `edit` (the edits from `--since` on, by
  default 2026-09-01 – the first version is of 2026-09-28), `edit_data` (the relationship type of those edits), `edit_note` (the
  notes of the script). `test_global_stats.py` runs it on a small made-up dump. A run takes about an hour.
- **When:** the GitHub Action `.github/workflows/global-stats.yml` – on Thursdays and Sundays (after the dumps of Wednesday and
  Saturday; nothing is done when the dump is the one read last), by hand (Actions → "Global statistics" → Run workflow), and once
  after a change of the script on `main`. The first run makes the branch `stats`.
- **Once a week – the core dump** (from Credits Importer 3.55.0, collected item Z-AGS; Q-fl, Q-fr): on Sundays (or by hand,
  "Run workflow" with **core**) the workflow also reads `mbdump.tar.bz2` of the same export as a stream – the tables `area`,
  `artist`, `artist_type`, `gender`, `iso_3166_1`, `language`, `link_attribute_type`, `medium`, `recording`, `release`,
  `release_group` and its types, `script`, `track` (from 3.61.0: the whole length of each release) – for the artists and recordings of the relationships the script added (open or applied) and the release of each submission (the one
  most of its edits are linked with in `edit_release` – MusicBrainz links an edit of a recording's or a work's relationship with every
  release of it) (the edit pass writes
  them to a file of the run, `--facts`, which is not committed). The result gets a section **`core`**: the artists (how many, their
  type, gender, decade of their begin, country, the town they began in, the centuries they were there, posthumous relationships –
  by the date of the relationship), the releases (single or several media, the primary and secondary types of their release
  groups, language and script), the lengths of the recordings (median, average) and, from 3.61.0, the whole length of each release whose every track has a length (median, average; `releases`, `release_median_ms`, `release_mean_ms`) and the role credits (of the relationships with an
  instrument or vocal attribute). On the other days the section of before is kept (`--keep-core`) – the core pass also runs when it is missing or 6 days old; a failed
  core pass (at most 150 minutes) keeps it too, with a warning.
  **Per release** (from Credits Importer 3.91.0, collected item Z-SRR): every run gives `per_release` – the credit relationships of each
  release (all its submissions, from their "Done:" lines; also by level), as the average and the median of the releases; the core pass
  adds `core.per_release` – the recordings of each of those releases (each once; not data tracks or a pregap) and the relationships on its
  recordings per recording (average, median). Only numbers.
  Besides, every run counts the **"credited as"** of the relationships the script added with an artist, a label or a place
  (section `credits`). Still only numbers (and the names of types, languages, scripts, countries and towns).
- **The tree of instruments** (from Credits Importer 3.107.0, collected item Z-ITREE): MusicBrainz's relationship editor offers its
  instruments as one flat list – which instrument is a kind of which (soprano saxophone "type of" saxophone) is only in the
  relationships between the instruments themselves. The core pass also reads the tables `instrument`, `l_instrument_instrument` and
  `link` and writes `stats/mb-vibecode-credits-importer-instruments.json` on the branch `stats`: every instrument (`[gid, name]`,
  sorted by name) and every "type of" relationship (link type 736 "subtype": `[parent, child]`, as indexes into that list), with
  `changes` – what the dump changed since the file of before (instruments new, gone, renamed, moved to another parent; the last 12
  weeks with a change). The script reads it for the common group of several instruments, a more precise instrument than
  MusicBrainz's and the kinds of an instrument (rules S170, S173, S174, Q014); a week's copy is kept in the browser. A run without the
  file reads the core dump at once. Only MusicBrainz's public instrument data.
