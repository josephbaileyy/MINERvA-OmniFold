#!/usr/bin/env python3
"""Legend names (RESTYLE AMENDMENT 2): is every legend entry its series identity's one name?

usage: python3 -I names.py RUN_DIR --styles STYLES.tsv [--other OTHER.tsv] [--figures a.png,b.png] [--gate]
capture.py writes each saved figure's legend entries to capture/<step>/<figure>.legend.tsv. Every entry must be the
name of an identity in STYLES.tsv (its last column), or an entry OTHER.tsv declares for that figure (a legend entry that
names no series, such as a reference line's). With --figures, each named figure must have a legend record, so that a
figure the capture missed fails instead of passing with nothing read. Prints every entry that is neither; with --gate,
exits 1 if there is one, or if a named figure has no record."""
import ast
import sys
from pathlib import Path


def opt(name):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else None


def table(path):
    rows = [l.split("\t") for l in Path(path).read_text().splitlines() if l.strip() and not l.startswith("#")]
    return rows[1:]  # a header row first


def main():
    run = Path(sys.argv[1])
    names = {r[3] for r in table(opt("--styles"))}
    other = {(r[0], r[1]) for r in table(opt("--other"))} if opt("--other") else set()
    want = [x for x in (opt("--figures") or "").split(",") if x]
    recs = {p.name[:-len(".legend.tsv")]: p for p in (run / "capture").glob("*/*.legend.tsv")}
    fails, n = [], 0
    for w in want:
        if w not in recs:
            fails.append(f"{w}: no legend record in {run}/capture")
    for fig, p in sorted(recs.items()):
        if want and fig not in want:
            continue
        stem = fig[:-len(".png")] if fig.endswith(".png") else fig
        for line in p.read_text().splitlines()[1:]:
            axes, text = line.split("\t", 1)
            text = ast.literal_eval(text)
            n += 1
            if text not in names and (stem, text) not in other:
                fails.append(f"{fig}: legend entry {text!r} (axes {axes}) is not an identity's name in styles.tsv")
    for f in fails:
        print("  FAIL", f)
    print(f"NAMES :: {'PASS' if not fails else 'FAIL'} ({n} legend entries in {len(recs) if not want else len(want)} "
          f"figures)")
    return 1 if fails and "--gate" in sys.argv else 0


if __name__ == "__main__":
    sys.exit(main())
