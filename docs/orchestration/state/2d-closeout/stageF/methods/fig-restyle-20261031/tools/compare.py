#!/usr/bin/env python3
"""Compare the before and after runs (DECLARATION.md §3 checks 3-5). Exit 1 on any difference.

usage: python3 -I compare.py BEFORE AFTER [--figures a.png,b.png,...] [--outputs rel1,rel2,...]
                             [--strip OLD=NEW ...]
BEFORE and AFTER are run directories, each with capture/<step>/ (capture.py's records) and the producers' outputs.
  - Check 3: for every capture/<step>/<figure>.json in BEFORE, the same file in AFTER must hold the same multiset of
    item hashes (artists.py). With --figures, exactly those figures must be present in both.
  - Check 4: each --outputs path (relative to the run directory) must be byte-identical, after each --strip OLD=NEW
    substitution (for example the run directory's own path, which a printout may name) and after dropping lines that
    report a wall time ("elapsed", "took", "seconds", "Real time", "CPU time").
  - Check 5: each step's opened.tsv must list the same (kind, path, sha256) rows, after the same substitutions.
RESTYLE AMENDMENT 1 (AMENDMENT-1.md): with --recolour RECOLOUR.tsv --palette PALETTE.tsv, check 3 compares the
multisets of the items' colour-free hashes ("dhash"), still bit for bit, and then each paired item's colours: a colour
the recolour table maps for that figure (figure, before RGB, identity) must become the palette's colour for that
identity, at its own alpha, and every other colour must stay exactly as it was. --rebin FIGURE (repeatable) names the
figures whose Axes.hist patches (gid "restyle-hist") may change: they are left out of the dhash comparison, while the
values hist was given ("hist-input" items) stay in it, bit for bit. Only the figures named are excepted.
Prints one line per check and a final COMPARE :: PASS or FAIL."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

TIMING = re.compile(r"elapsed|took|seconds|Real time|CPU time", re.I)


def opt(name):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else None


def strips():
    a, out = sys.argv, []
    for i, x in enumerate(a):
        if x == "--strip":
            old, new = a[i + 1].split("=", 1)
            out.append((old, new))
    return out


def norm(text, subs):
    for old, new in subs:
        text = text.replace(old, new)
    return "\n".join(l for l in text.splitlines() if not TIMING.search(l))


def table(path):
    rows = [l.split("\t") for l in Path(path).read_text().splitlines() if l.strip() and not l.startswith("#")]
    return rows[1:]  # a header row first


def recolour_maps():
    if "--recolour" not in sys.argv:
        return None, None
    pal = {r[0]: r[1].upper() for r in table(opt("--palette"))}
    rec = {(r[0], r[1].upper()): r[2] for r in table(opt("--recolour"))}
    return pal, rec


def expected(colours, fig, pal, rec):
    """The colours an after-item must have, given its before-item's colours."""
    def one(c):
        if not isinstance(c, str) or not c.startswith("#"):
            return c
        ident = rec.get((fig, c[:7].upper()))
        return c if ident is None else pal[ident] + c[7:]
    return {k: ([one(c) for c in v] if isinstance(v, list) else one(v)) for k, v in colours.items()}


def figures(run):
    return {p.relative_to(run / "capture"): p for p in (run / "capture").glob("*/*.json") if p.name != "capture-done.json"}


def check_figures(b, a, want):
    pal, rec = recolour_maps()
    if pal is not None:
        return check_figures_recoloured(b, a, want, pal, rec)
    fails, fb, fa = [], figures(b), figures(a)
    if want:
        for w in want:
            for side, f in (("before", fb), ("after", fa)):
                if not any(k.name == w + ".json" for k in f):
                    fails.append(f"figure {w}: no capture in the {side} run")
        for side, f in (("before", fb), ("after", fa)):
            for k in sorted(f):
                if k.name[:-len(".json")] not in want:
                    fails.append(f"figure {k.name[:-len('.json')]}: not named by --figures ({side} run)")
    for k in sorted(fb):
        if k not in fa:
            fails.append(f"figure {k}: captured before, not after")
            continue
        ib, ia = json.loads(fb[k].read_text()), json.loads(fa[k].read_text())
        cb, ca = Counter(x["hash"] for x in ib), Counter(x["hash"] for x in ia)
        if cb != ca:
            gone = [x for x in ib if (cb - ca)[x["hash"]]]
            new = [x for x in ia if (ca - cb)[x["hash"]]]
            desc = lambda xs: "; ".join(f"{x['kind']} on axes {x['axes']} {x['label']!r}" for x in xs[:4])
            fails.append(f"figure {k}: {len(gone)} item(s) only before ({desc(gone)}), "
                         f"{len(new)} only after ({desc(new)})")
        else:
            print(f"  equal  {k}: {len(ib)} data artists")
    for k in sorted(set(fa) - set(fb)):
        fails.append(f"figure {k}: captured after, not before")
    return fails


def check_figures_recoloured(b, a, want, pal, rec):
    fails, fb, fa = [], figures(b), figures(a)
    rebin = {sys.argv[i + 1] for i, x in enumerate(sys.argv) if x == "--rebin"}
    if want:
        for side, f in (("before", fb), ("after", fa)):
            for w in want:
                if not any(k.name == w + ".json" for k in f):
                    fails.append(f"figure {w}: no capture in the {side} run")
            for k in sorted(f):
                if k.name[:-len(".json")] not in want:
                    fails.append(f"figure {k.name[:-len('.json')]}: not named by --figures ({side} run)")
    for k in sorted(fb):
        if k not in fa:
            fails.append(f"figure {k}: captured before, not after")
            continue
        fig = k.name[:-len(".png.json")]
        keep = (lambda x: not (x["kind"] == "patch" and x.get("gid") == "restyle-hist")) if k.name[:-len(".json")] in rebin \
            else (lambda x: True)
        ib = [x for x in json.loads(fb[k].read_text()) if keep(x)]
        ia = [x for x in json.loads(fa[k].read_text()) if keep(x)]
        cb, ca = Counter(x["dhash"] for x in ib), Counter(x["dhash"] for x in ia)
        if cb != ca:
            gone = [x for x in ib if (cb - ca)[x["dhash"]]]
            new = [x for x in ia if (ca - cb)[x["dhash"]]]
            desc = lambda xs: "; ".join(f"{x['kind']} on axes {x['axes']} {x['label']!r}" for x in xs[:4])
            fails.append(f"figure {k}: {len(gone)} item(s) only before ({desc(gone)}), "
                         f"{len(new)} only after ({desc(new)})")
            continue
        bad = 0
        for dh in cb:
            want_c = sorted(json.dumps(expected(x["colours"], fig, pal, rec), sort_keys=True) for x in ib if x["dhash"] == dh)
            got_c = sorted(json.dumps(x["colours"], sort_keys=True) for x in ia if x["dhash"] == dh)
            if want_c != got_c:
                bad += 1
                x = next(x for x in ia if x["dhash"] == dh)
                fails.append(f"figure {k}: {x['kind']} on axes {x['axes']} {x['label']!r} has colours {got_c[0][:120]}, "
                             f"the palette and recolour table give {want_c[0][:120]}")
        if not bad:
            print(f"  equal  {k}: {len(ib)} data artists, colours as the palette maps them"
                  + (" (bins free: hist values equal)" if k.name[:-len(".json")] in rebin else ""))
    for k in sorted(set(fa) - set(fb)):
        fails.append(f"figure {k}: captured after, not before")
    return fails


def check_outputs(b, a, rels, subs):
    fails = []
    for r in rels:
        pb, pa = b / r, a / r
        if not pb.is_file() or not pa.is_file():
            fails.append(f"output {r}: missing ({'before' if not pb.is_file() else 'after'})")
        elif norm(pb.read_text(errors="replace"), subs) != norm(pa.read_text(errors="replace"), subs):
            fails.append(f"output {r}: differs")
        else:
            print(f"  equal  output {r}")
    return fails


def check_opened(b, a, subs):
    fails = []
    for pb in sorted((b / "capture").glob("*/opened.tsv")):
        pa = a / pb.relative_to(b)
        rows = lambda p: Counter(norm(p.read_text(), subs).splitlines()) if p.is_file() else None
        if rows(pa) is None:
            fails.append(f"inputs {pb.parent.name}: no opened.tsv after")
        elif rows(pb) != rows(pa):
            fails.append(f"inputs {pb.parent.name}: the opened files differ")
        else:
            print(f"  equal  inputs {pb.parent.name}: {sum(rows(pb).values())} rows")
    return fails


def main():
    b, a = Path(sys.argv[1]), Path(sys.argv[2])
    want = [x for x in (opt("--figures") or "").split(",") if x]
    rels = [x for x in (opt("--outputs") or "").split(",") if x]
    subs = strips()
    fails = check_figures(b, a, want) + check_outputs(b, a, rels, subs) + check_opened(b, a, subs)
    for f in fails:
        print("  FAIL", f)
    print("COMPARE ::", "PASS" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
