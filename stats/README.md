# Global statistics (alpha)

**Collected item Z-GST.** How MB x Vibecode: Credits Importer is used on MusicBrainz as a whole – not yet shown in the script; this
alpha is to see what can be read.

- **Source:** MusicBrainz's edit dump `mbdump-edit.tar.bz2` of the latest full export (MetaBrainz, twice a week:
  `https://data.metabrainz.org/pub/musicbrainz/data/fullexport/LATEST`). It holds every edit, its data and its edit notes.
- **What counts:** the edits whose editor wrote the script's edit note on them (the line `Script: MB x Vibecode: Credits Importer v…`;
  before 3.1.0 `MB x Vibecode: Import Discogs credits`) – a voter quoting it does not count. An edit note "Simple" still counts;
  with "No note" an edit cannot be found. A **submission** is the same note of one editor within 30 minutes (MusicBrainz sends one
  "Enter edit" in parts – 25 edits a request, new works first, live comments later); its "Done:" line is counted once.
- **Result:** [`mb-vibecode-credits-importer-global.json`](mb-vibecode-credits-importer-global.json) – totals (edits, submissions,
  different editors), per month, per version, per edit type, status (applied, open, failed …), auto-edit or voted, the relationship
  types, the sources and supplements, and what the "Done:" lines of the notes say (credit relationships per level, works linked,
  role credits and dates added).
- **Privacy:** only numbers. No editor names or ids, no edits, no releases, no URLs; "editors" is how many different ones.
- **Safety:** an archive cut off or without the tables is an error – nothing is written or committed.
- **How:** `global_stats.py` reads the archive as a stream (nothing on disk): the table `edit` (the edits from `--since` on, by
  default 2026-09-01 – the first version is of 2026-09-28), `edit_data` (the relationship type of those edits), `edit_note` (the
  notes of the script). `test_global_stats.py` runs it on a small made-up dump.
- **When:** the GitHub Action `.github/workflows/global-stats.yml` – by hand (Actions → "Global statistics (alpha)" → Run), on a push
  of the script on its branch, and (once on the default branch) on Thursdays and Sundays. It commits the result back to its branch.
