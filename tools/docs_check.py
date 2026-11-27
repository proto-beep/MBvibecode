#!/usr/bin/env python3
"""tools/docs_check.py [<repo dir> [<version>]]: README and changelog up to date for a version (3.231.0, Z-DOCSCHECK; the
version from the script's @version when not given; run before every release and by smoke/t_static.py docs3231).
Exit 1 (release stops) when:
- the changelog has no "### Import <V>" section, or the date heading above it is not the version's date (full README "**Version V** · DATE"),
- the changelog's overview table does not reach <V> in its first row,
- README.md does not link the full reference of <V>,
- README.md's "What's new" starts with an older version than the newest milestone of the changelog,
- the script's MILESTONES do not start with the changelog's newest milestone.
Prints the three newest milestones as a reminder: is the new version one (a new ability you notice without the docs)?"""
import re
import sys
from pathlib import Path

d = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
v = sys.argv[2] if len(sys.argv) > 2 else re.search(r'@version\s+(\S+)', (d / 'mb-vibecode-credits-importer.user.js').read_text()).group(1)
bad = []
cl = (d / 'mb-vibecode-credits-importer-CHANGELOG.md').read_text()
rd = (d / 'README.md').read_text()
full = d / f'mb-vibecode-credits-importer-v{v}-README.md'
date = ''
if not full.exists():
    bad.append(f'full README {full.name} missing')
else:
    m = re.search(r'\*\*Version ' + re.escape(v) + r'\*\* · (\d{4}-\d{2}-\d{2})', full.read_text())
    date = m.group(1) if m else ''
    if not date:
        bad.append('full README: no "**Version V** · DATE" line')
m = re.search(r'\n### Import ' + re.escape(v) + r'\b', cl)
if not m:
    bad.append(f'changelog: no "### Import {v}"')
else:
    heads = re.findall(r'\n## (\d{4}-\d{2}-\d{2})\n', cl[:m.start()])
    if not heads or (date and heads[-1] != date):
        bad.append(f'changelog: "### Import {v}" stands under "## {heads[-1] if heads else "-"}", not "## {date}"')
row = re.search(r'\| Date \| Import \| COMPANION \|\n\|---\|---\|---\|\n\| (\S+) \| ([^|]+) \|', cl)
if not row or not row.group(2).strip().endswith(v):
    bad.append(f'changelog overview: first row "{row.group(2).strip() if row else "-"}" does not end with {v}')
elif date and row.group(1) != date:
    bad.append(f'changelog overview: first row dated {row.group(1)}, the version {date}')
if f'mb-vibecode-credits-importer-v{v}-README.md' not in rd:
    bad.append(f'README.md does not link the full reference v{v}')
ms = re.findall(r'\n\| (\d{4}-\d{2}-\d{2}) \| (?:Import|Companion) (\d+\.\d+)\.\d+[^|]*\| ([^|]+)\|', cl[cl.index('## Milestones'):])
wn = re.search(r'\| Version \| \|\n\|---\|---\|\n\| (\d+\.\d+) \|', rd)
key = lambda s: tuple(int(x) for x in s.split('.'))
if ms and wn and key(wn.group(1)) < key(ms[0][1]):
    bad.append(f'README "What\'s new" starts with {wn.group(1)}, the changelog\'s newest milestone is {ms[0][1]}')
js = (d / 'mb-vibecode-credits-importer.user.js').read_text()
top = re.search(r"const MILESTONES = \[[^{]*\{ v: '(\d+\.\d+)\.\d+'", js)
if ms and top and top.group(1) != ms[0][1]:
    bad.append(f"the script's MILESTONES start with {top.group(1)}, the changelog's table with {ms[0][1]}")
print('docs: newest milestones –', '; '.join(f'{x[1]} {x[2].strip()[:60]}' for x in ms[:3]))
print(f'docs: is {v} a milestone? then into the changelog\'s table, README "What\'s new" and the script\'s MILESTONES')
for b in bad:
    print('docs ERROR:', b)
sys.exit(1 if bad else 0)
