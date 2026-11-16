"""Control C0 for t2a_g2r.py: its cov2d-mode record must equal the committed fd/tier2-20261110/t2a/t2a_<T>.json on
every field except the path-valued ones (inputs_paths, figure.path), which name where each run wrote. Equal means
JSON-equal: numbers compared exactly, as written. Prints each differing key path; exit 0 only if none differ.
    python3 -I c0_compare.py <run record> <committed record>
"""
import json
import sys

SKIP = {("inputs_paths",), ("figure", "path")}


def flat(o, p=()):
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            out.update(flat(v, p + (k,)))
        return out
    return {p: o}


a, b = (json.load(open(x)) for x in sys.argv[1:3])
fa, fb = flat(a), flat(b)
keys = sorted(set(fa) | set(fb))
skip = lambda k: any(k[:len(s)] == s for s in SKIP)
diff = [k for k in keys if not skip(k) and fa.get(k, "<absent>") != fb.get(k, "<absent>")]
for k in diff:
    print("DIFF", "/".join(k), repr(fa.get(k, "<absent>"))[:120], repr(fb.get(k, "<absent>"))[:120])
print(f"C0 {sys.argv[1]}: {len(keys)} leaf keys, {len([k for k in keys if skip(k)])} path-valued skipped, {len(diff)} differ")
print("C0", "PASS" if not diff else "FAIL")
sys.exit(1 if diff else 0)
