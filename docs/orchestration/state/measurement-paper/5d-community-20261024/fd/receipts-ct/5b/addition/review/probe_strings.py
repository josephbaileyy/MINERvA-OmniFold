import json, sys, re, collections
from pathlib import Path
WT = Path(sys.argv[1]); sys.path.insert(0, str(WT / "nd-unfolding"))
import fd_cpl_addition as A
EX = ("/argv", "/code_sha256", "/code", "/versions")
for k in A.READOUTS:
    r = json.loads((WT / A.COMMITTED[k][0]).read_text())
    pat = collections.Counter()
    ex = {}
    for p, v in A.string_leaves(r):
        if A.skipped(p, EX) or p.startswith("/labels"):
            continue
        q = re.sub(r"/\d+", "/*", p)
        pat[q] += 1
        ex.setdefault(q, v[:60])
    print(f"== {k}: {len(pat)} string-leaf patterns")
    for q, n in pat.most_common():
        if re.search(r"label|/what$|/rule$|/note$|/file$|/path$|sha256|/how$|/role$", q):
            continue
        print(f"   {n:5d} {q}  e.g. {ex[q]!r}")
