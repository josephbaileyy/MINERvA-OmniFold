"""locate.py TEXFILE 'substring' -> line number and enclosing (sub)section heading of the first match
(whitespace-insensitive match against the raw source, comments removed)."""
import re, sys
path, needle = sys.argv[1], sys.argv[2]
lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
flat, owners = '', []
for i, l in enumerate(lines):
    l2 = re.sub(r'(?<!\\)%.*', '', l)
    for ch in l2 + ' ':
        flat += ch; owners.append(i)
norm = lambda s: re.sub(r'\s+', ' ', s)
f2, own2, prev = '', [], ''
for ch, o in zip(flat, owners):
    if ch.isspace():
        if prev == ' ': continue
        ch = ' '
    f2 += ch; own2.append(o); prev = ch
k = f2.find(norm(needle))
if k < 0:
    print('NOT FOUND'); sys.exit(1)
ln = own2[k]
sec = sub = abstract = None
for j in range(ln, -1, -1):
    m = re.search(r'\\(sub)?section\*?\{(.*)', lines[j])
    if m and m.group(1) and sub is None and sec is None: sub = m.group(2)[:70]
    if m and not m.group(1): sec = m.group(2)[:70]; break
    if re.search(r'\\begin\{abstract\}|\\abstract\{|AtlasAbstract', lines[j]): abstract = True; break
print(f'{path.split("/x/")[0].split("/")[-1]}:{ln + 1}  sec={"ABSTRACT" if abstract and not sec else sec} sub={sub}')
