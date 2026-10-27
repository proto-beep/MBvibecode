"""Adds or replaces texts: English in the main script, German, Spanish and French in the languages file.

Usage: python3 i18n_add.py <anchor key> <json file {lang: {key: text}}>
New keys go after the anchor key of each language; existing keys are replaced in place.
From Credits Importer 3.27.1 a file with English only is enough: the other languages show the English text until the
next translation round (the case i18n of smoke/t_static.py lists what is not translated yet). Watch out: a key that exists is replaced.
[3.34.0] German, Spanish and French are in mb-vibecode-credits-importer-languages.json (one text a line); English, the base of
the keys, stays in the script (const I18N = { en: { … } }).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'mb-vibecode-credits-importer.user.js'
LANGUAGES = ROOT / 'mb-vibecode-credits-importer-languages.json'
OTHER = ['de', 'es', 'fr']


def en_block(s):
    start = s.index('  const I18N = {')
    m = re.compile(r'\n    en: \{\n').search(s, start)
    if not m:
        raise SystemExit('language block en not found')
    return m.end(), s.index('\n    },', m.end())


def read_languages():
    return json.loads(LANGUAGES.read_text(encoding='utf-8'))


def write_languages(data):
    """The layout of the file: its head, then each language with one text a line (a pull request shows only what changed)."""
    head = [k for k in data if k not in OTHER]
    lines = ['{'] + [f'  {json.dumps(k, ensure_ascii=False)}: {json.dumps(data[k], ensure_ascii=False)},' for k in head]
    for i, lang in enumerate(OTHER):
        body = ',\n'.join(f'    {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}' for k, v in data[lang].items())
        lines.append(f'  "{lang}": {{\n{body}\n  }}{"," if i < len(OTHER) - 1 else ""}')
    lines.append('}')
    LANGUAGES.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def insert_after(d, anchor, new):
    """d with new keys after anchor (anchor missing: at the end), existing keys replaced in place."""
    out = {}
    rest = {k: v for k, v in new.items() if k not in d}
    for k, v in d.items():
        out[k] = new.get(k, v)
        if k == anchor:
            out.update(rest)
            rest = {}
    out.update(rest)
    return out


def apply(anchor, texts):
    if 'en' not in texts:
        raise SystemExit('English texts are needed (the other languages fall back to them)')
    s = SCRIPT.read_text(encoding='utf-8')
    a, b = en_block(s)
    body = s[a:b]
    add = []
    for k, v in texts['en'].items():
        line = f'      {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)},'
        pat = re.compile(r'^      ' + re.escape(json.dumps(k, ensure_ascii=False)) + r': .*,$', re.M)
        if pat.search(body):
            body = pat.sub(lambda m: line, body, count=1)
        else:
            add.append(line)
    if add:
        al = re.search(r'^      ' + re.escape(json.dumps(anchor, ensure_ascii=False)) + r': .*,$', body, re.M)
        if not al:
            raise SystemExit(f'anchor {anchor} not found in en')
        body = body[:al.end()] + '\n' + '\n'.join(add) + body[al.end():]
    s = s[:a] + body + s[b:]
    SCRIPT.write_text(s, encoding='utf-8')
    data = read_languages()
    for lang in OTHER:
        if lang in texts:
            data[lang] = insert_after(data[lang], anchor, texts[lang])
    write_languages(data)
    a, b = en_block(s)
    print('entries per language:', [len(re.findall(r'^      "', s[a:b], re.M))] + [len(data[lang]) for lang in OTHER])


if __name__ == '__main__':
    apply(sys.argv[1], json.loads(Path(sys.argv[2]).read_text(encoding='utf-8')))
