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
RESTYLE AMENDMENT 2 (AMENDMENT-2.md): with --styles STYLES.tsv --restyle RESTYLE.tsv as well, check 3 pairs the items
by their hashes with colours and line styles left out ("xhash"), still bit for bit, and then requires each paired
item's colours as above and its line style and marker: an item the restyle table maps (figure, before RGB, before
linestyle, before marker; identity) must take its identity's declared linestyle and marker (STYLES.tsv), and every
other item's linestyle, marker and drawstyle must stay exactly as they were. A drawstyle never changes.
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


def restyle_maps():
    if "--styles" not in sys.argv:
        return None, None
    sty = {r[0]: {"linestyle": r[1], "marker": r[2]} for r in table(opt("--styles"))}
    res = {(r[0], r[1].upper(), r[2], r[3]): r[4] for r in table(opt("--restyle"))}
    unknown = sorted({i for i in res.values() if i not in sty})
    if unknown:
        sys.exit(f"compare.py: the restyle table names identities {unknown} that the styles table does not declare")
    return sty, res


def expected_style(colours, style, fig, sty, res):
    """The line style an after-item must have, given its before-item's colours and style."""
    if not style:
        return style
    c = colours.get("color")
    c = (c[0] if isinstance(c, list) and c else c) or ""
    ident = res.get((fig, c[:7].upper(), style.get("linestyle"), style.get("marker")))
    return style if ident is None else dict(style, **sty[ident])


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
    sty, res = restyle_maps()
    if sty is not None:
        if pal is None:
            sys.exit("compare.py: --styles needs --recolour and --palette")
        return check_figures_recoloured(b, a, want, pal, rec, sty, res)
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


def check_figures_recoloured(b, a, want, pal, rec, sty=None, res=None):
    fails, fb, fa = [], figures(b), figures(a)
    hk = "dhash" if sty is None else "xhash"          # amendment 2: the hash with colours and line styles left out

    def look(x):                                       # what the comparison requires of an item beyond its data
        return {"colours": x["colours"]} if sty is None else {"colours": x["colours"], "style": x["style"]}

    def want_look(x, fig):
        out = {"colours": expected(x["colours"], fig, pal, rec)}
        if sty is not None:
            out["style"] = expected_style(x["colours"], x["style"], fig, sty, res)
        return out
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
        cb, ca = Counter(x[hk] for x in ib), Counter(x[hk] for x in ia)
        if cb != ca:
            gone = [x for x in ib if (cb - ca)[x[hk]]]
            new = [x for x in ia if (ca - cb)[x[hk]]]
            desc = lambda xs: "; ".join(f"{x['kind']} on axes {x['axes']} {x['label']!r}" for x in xs[:4])
            fails.append(f"figure {k}: {len(gone)} item(s) only before ({desc(gone)}), "
                         f"{len(new)} only after ({desc(new)})")
            continue
        bad = 0
        for dh in cb:
            want_c = sorted(json.dumps(want_look(x, fig), sort_keys=True) for x in ib if x[hk] == dh)
            got_c = sorted(json.dumps(look(x), sort_keys=True) for x in ia if x[hk] == dh)
            if want_c != got_c:
                bad += 1
                x = next(x for x in ia if x[hk] == dh)
                fails.append(f"figure {k}: {x['kind']} on axes {x['axes']} {x['label']!r} has {got_c[0][:160]}, "
                             f"the palette{'' if sty is None else ', styles'} and recolour table give {want_c[0][:160]}")
        if not bad:
            print(f"  equal  {k}: {len(ib)} data artists, colours as the palette maps them"
                  + ("" if sty is None else ", line styles as declared")
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
