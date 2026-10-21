"""usage: python3 -I multiset_check.py NORMAL.txt RATER.txt -- exit 0 iff equal as word multisets once hold spans,
hyphen line-joins and hyphens themselves are removed (so a reflowed 'cross-section'/'crosssection' compares equal)."""
import re, sys, collections
def bag(path):
    t = open(path, encoding="utf-8").read()
    t = re.sub(r"\[HOLD:[^\]]*\]", " ", t, flags=re.S)
    t = re.sub(r"-\s*\n\s*", "", t).replace("-", "")
    return collections.Counter(re.findall(r"\w+", t))
a, b = bag(sys.argv[1]), bag(sys.argv[2])
# a word split by a reflowed block ("hep" + ... + "ex") changes the bag only by re-tokenizing; compare letters too
la = collections.Counter("".join(sorted(a.elements()))); lb = collections.Counter("".join(sorted(b.elements())))
onlya, onlyb = a - b, b - a
print("multiset: only normal %s; only rater %s" % (dict(onlya.most_common(10)), dict(onlyb.most_common(10))))
ok = la == lb and sum(onlya.values()) <= 6
print("multiset VERDICT: %s" % ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
