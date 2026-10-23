"""Extract labelled metadata rows from saved arXiv abs pages.

Prints, per file: title, version line, the labelled 'Journal reference' row (or ABSENT),
and the labelled 'Related DOI' row (or ABSENT). Reads only the <td> pairs of the
metatable, so a report number can never be taken for a journal reference.
"""
import html, re, sys

def rows(text):
    out = {}
    for m in re.finditer(r'<td class="tablecell label">(.*?)</td>\s*<td class="tablecell ([a-z\- ]+)">(.*?)</td>', text, re.S):
        lab = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).replace('\xa0', ' ').strip().rstrip(':').strip()
        val = html.unescape(re.sub(r'<[^>]+>', ' ', m.group(3)))
        out[lab] = re.sub(r'\s+', ' ', val).strip()
    return out

for p in sys.argv[1:]:
    t = open(p, encoding='utf-8', errors='replace').read()
    title = re.search(r'<title>(.*?)</title>', t, re.S)
    ver = re.search(r'\[Submitted on[^\]]*\]', re.sub(r'<[^>]+>', '', t))
    r = rows(t)
    print('FILE', p)
    print('  title  :', html.unescape(title.group(1)).strip() if title else '?')
    print('  version:', re.sub(r'\s+', ' ', ver.group(0)) if ver else '?')
    print('  journal-ref row:', r.get('Journal reference', 'ABSENT'))
    print('  related-DOI row:', r.get('Related DOI', 'ABSENT'))
    print('  labels seen    :', sorted(r))
