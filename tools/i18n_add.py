"""Adds or replaces texts in the embedded translations of the main script.

Usage: python3 i18n_add.py <anchor key> <json file {lang: {key: text}}>
New keys go after the anchor key of each language block; existing keys are replaced in place.
From Credits Importer 3.27.1 a file with English only is enough: the other languages show the English text until the
next translation round (the case i18n of smoke/t_static.py lists what is not translated yet). Watch out: a key that exists is replaced.
"""
import json
import re
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / 'mb-vibecode-credits-importer.user.js'
LANGS = ['en', 'de', 'es', 'fr']


def blocks(s):
    start = s.index('  const I18N = {')
    out = []
    for lang in LANGS:
        m = re.compile(r'\n    ' + lang + r': \{\n').search(s, start)
        if not m:
            raise SystemExit(f'language block {lang} not found')
        end = s.index('\n    },', m.end())
        out.append((lang, m.end(), end))
        start = end
    return out


def apply(anchor, texts):
    s = SCRIPT.read_text()
    if 'en' not in texts:
        raise SystemExit('English texts are needed (the other languages fall back to them)')
    for lang, a, b in reversed(blocks(s)):
        if lang not in texts:
            continue
        body = s[a:b]
        add = []
        for k, v in texts[lang].items():
            line = f'      {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)},'
            pat = re.compile(r'      ' + re.escape(json.dumps(k)) + r': .*,\n')
            if pat.search(body + '\n'):
                body = pat.sub(lambda m: line + '\n', body + '\n', count=1)[:-1] if not body.endswith('\n') else pat.sub(lambda m: line + '\n', body, count=1)
            else:
                add.append(line)
        if add:
            al = re.search(r'      ' + re.escape(json.dumps(anchor)) + r': .*,\n', body + '\n')
            if not al:
                raise SystemExit(f'anchor {anchor} not found in {lang}')
            pos = al.end()
            body = (body + '\n')[:pos] + '\n'.join(add) + '\n' + (body + '\n')[pos:]
            body = body[:-1]
        s = s[:a] + body + s[b:]
    SCRIPT.write_text(s)
    keys = [len(re.findall(r'^      "', s[a:b], re.M)) for _, a, b in blocks(s)]
    print('entries per language:', keys)


if __name__ == '__main__':
    apply(sys.argv[1], json.loads(Path(sys.argv[2]).read_text()))
