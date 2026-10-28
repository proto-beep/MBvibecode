"""Removes texts in all languages: English in the main script, German, Spanish and French in the languages file.

Usage: python3 i18n_del.py <key> [<key> …]   (a key without ".one"/".other" also removes its plural forms)
"""
import re
import sys

from i18n_add import OTHER, SCRIPT, en_block, read_languages, write_languages

PLURAL = re.compile(r'\.(?:zero|one|two|few|many|other)$')


def main(keys):
    s = SCRIPT.read_text(encoding='utf-8')
    a, b = en_block(s)
    body = s[a:b]
    n = 0
    for k in keys:
        pat = re.compile(r'^      "' + re.escape(k) + r'(?:\.(?:zero|one|two|few|many|other))?": .*,\n', re.M)
        body, c = pat.subn('', body + '\n')
        body = body[:-1]
        n += c
    SCRIPT.write_text(s[:a] + body + s[b:], encoding='utf-8')
    data = read_languages()
    for lang in OTHER:
        before = len(data[lang])
        data[lang] = {k: v for k, v in data[lang].items() if k not in keys and PLURAL.sub('', k) not in keys}
        n += before - len(data[lang])
    write_languages(data)
    print('texts removed:', n)


if __name__ == '__main__':
    main(sys.argv[1:])
