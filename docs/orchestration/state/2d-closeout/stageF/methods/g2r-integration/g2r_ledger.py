#!/usr/bin/env python3
"""The note's G2R re-key: every printed Q_R-derived value moved from RE-2 part C to RE-2-shapes run 2 (C_new).

usage:
  g2r_ledger.py build <repo>       write ledger.tsv beside this file from ANCHORS.tsv (needs the pre-G2R note text)
  g2r_ledger.py apply <repo>       replace each row's old value in the note sources, at the anchored position
  g2r_ledger.py check <repo>       verify the ledger against the tables and the note (exit 1 on any failure)
  g2r_ledger.py --self-test <repo> plant one bad row of each check and require each to fail

Authority: DECISION-20261114-joseph-d1-g2r-adopted.md (C_new adopted; item 3, every dependent result updated); the
director's rulings of 2026-11-15 (re-key every printed Q_R-derived value; equal to the paper's key wherever both
print).

OLD is RE-2 part C (re2/run/partc_r2/partc-r2/), NEW is RE-2-shapes run 2
(fd/receipts-cov2d/g2r/re2shapes/run2/g2r/, merged at main d58d0d18 by #1167). Each NEW file is checked against that
run's own SHA256SUMS.

ANCHORS.tsv rows, one per printed value:
  T <id> <file> <table row id> <anchor>                          a values_table.tsv row, field refined_rendered
  J <id> <file> <json file> <dotted key> <scale> <format> <anchor>  a value of a JSON product, format(scale * value)
<file> is relative to docs/analysis-note. <anchor> is printed text (LaTeX comments removed, whitespace collapsed)
that occurs exactly once in <file> before the re-key and contains the old value exactly once.

ledger.tsv rows (built):
  V <id> <file> <old> <new> <new context> <old context> <source> <key>
The old context is the anchor; the new context is the anchor with every re-keyed value inside it replaced.

check requires, for every row:
  - old equals OLD's value and new equals NEW's value (rendered as the row says);
  - the new context prints exactly once in its file;
  - when old != new, the old context prints in no posted file: the printed \\input closure of main_note, main_paper,
    main_primer and pet_note (the records document, main_records, is not posted and keeps its dated values);
  - every NEW file read is listed with its sha256 in the run's SHA256SUMS.
"""
import csv
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
M = "docs/orchestration/state/2d-closeout/stageF/methods/"
OLD_DIR = M + "re2/run/partc_r2/partc-r2/"
NEW_DIR = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/re2shapes/run2/g2r/"
NOTE = "docs/analysis-note/"
POSTED = ("main_note.tex", "main_paper.tex", "main_primer.tex", "pet_note.tex")


def printed_map(src):
    """Printed text of a LaTeX source (comments removed, whitespace runs collapsed) and, per printed character,
    its index in the source."""
    out, idx, i, n, ws = [], [], 0, len(src), False
    while i < n:
        c = src[i]
        if c == "%" and (i == 0 or src[i - 1] != "\\"):
            j = src.find("\n", i)
            i = n if j < 0 else j + 1      # a comment eats its newline
            continue
        if c.isspace():
            if not ws:
                out.append(" "); idx.append(i); ws = True
            i += 1
            continue
        ws = False
        out.append(c); idx.append(i); i += 1
    return "".join(out), idx


def printed(path):
    return printed_map(Path(path).read_text())[0]


def posted_files(repo):
    """The \\input closure of the posted builds."""
    seen, todo = set(), list(POSTED)
    while todo:
        f = todo.pop()
        p = repo / NOTE / f
        if f in seen or not p.exists():
            continue
        seen.add(f)
        for m in re.finditer(r"\\(?:input|include)\{([^}]+)\}", printed(p)):
            g = m.group(1)
            todo.append(g if g.endswith(".tex") else g + ".tex")
    return sorted(seen)


def table(path):
    return {r["id"]: r for r in csv.DictReader(open(path), delimiter="\t")}


def jget(path, key):
    p = Path(path)
    d = json.loads((p.read_bytes() if p.suffix != ".gz" else __import__("gzip").decompress(p.read_bytes())).decode())
    for k in key.split("."):
        d = d[int(k)] if isinstance(d, list) else d[k]
    return d


def values(repo, row, which):
    base = repo / (OLD_DIR if which == "old" else NEW_DIR)
    if row[0] == "T":
        return table(base / "values_table.tsv")[row[3]]["refined_rendered"], "values_table.tsv", row[3]
    _, _, _, jf, key, scale, fmt = row[:7]
    return format(float(scale) * jget(base / jf, key), fmt), jf, key


def anchors():
    rows = []
    for line in open(HERE / "ANCHORS.tsv"):
        if line.strip() and not line.startswith("#"):
            rows.append(line.rstrip("\n").split("\t"))
    return rows


def build(repo):
    rows, by_file = anchors(), {}
    for r in rows:
        f, anchor = r[2], r[-1]
        old, src, key = values(repo, r, "old")
        new = values(repo, r, "new")[0]
        t = printed(repo / NOTE / f)
        if t.count(anchor) != 1:
            raise SystemExit(f"BUILD {r[1]}: anchor prints {t.count(anchor)} times in {f}: {anchor!r}")
        if anchor.count(old) != 1:
            raise SystemExit(f"BUILD {r[1]}: old value {old} occurs {anchor.count(old)} times in its anchor")
        a = t.index(anchor)
        by_file.setdefault(f, []).append((a, a + anchor.index(old), old, new, anchor, src, key, r[1]))
    out = []
    for f, items in by_file.items():
        pos = sorted((p, o, nw) for _, p, o, nw, *_ in items)
        for (p1, o1, _), (p2, _, _) in zip(pos, pos[1:]):
            if p1 + len(o1) > p2:
                raise SystemExit(f"BUILD {f}: two rows overlap at printed position {p2}")
        for a, p, old, new, anchor, src, key, vid in items:
            ctx = anchor
            for q, o, nw in sorted(pos, reverse=True):     # every re-keyed value inside this anchor
                if a <= q and q + len(o) <= a + len(anchor):
                    ctx = ctx[: q - a] + nw + ctx[q - a + len(o):]
            out.append(["V", vid, f, old, new, ctx, anchor, src, key])
    with open(HERE / "ledger.tsv", "w") as fh:
        fh.write("# G2R fact ledger, built by g2r_ledger.py build from ANCHORS.tsv; columns: V id file old new "
                 "new-context old-context source key\n")
        for r in out:
            fh.write("\t".join(r) + "\n")
    print(f"[build] {len(out)} rows")


def ledger(path=None):
    return [l.rstrip("\n").split("\t") for l in open(path or HERE / "ledger.tsv") if l.startswith("V\t")]


def apply(repo):
    by_file = {}
    for r in ledger():
        by_file.setdefault(r[2], []).append(r)
    for f, rows in by_file.items():
        p = repo / NOTE / f
        src = p.read_text()
        t, idx = printed_map(src)
        edits = []
        for r in rows:
            anchor, old, new = r[6], r[3], r[4]
            if t.count(anchor) != 1:
                raise SystemExit(f"APPLY {r[1]}: anchor prints {t.count(anchor)} times in {f}")
            q = t.index(anchor) + anchor.index(old)
            s0 = idx[q]
            if src[s0:s0 + len(old)] != old:
                raise SystemExit(f"APPLY {r[1]}: the value is split in the source of {f}")
            edits.append((s0, old, new))
        for s0, old, new in sorted(edits, reverse=True):
            src = src[:s0] + new + src[s0 + len(old):]
        p.write_text(src)
        print(f"[apply] {f}: {len(edits)} values")


NOTE_TAG = "% G2R:"


def annotate(repo):
    """Append, once, to each source line that now carries a re-keyed value, a comment naming its ledger rows, so a
    source comment elsewhere that cites RE-2 part C for the earlier value is read as superseded. The appended text
    starts with a space, so the comment eats the newline without joining words; no line is added."""
    by_file = {}
    for r in ledger():
        if r[3] != r[4]:
            by_file.setdefault(r[2], []).append(r)
    for f, rows in by_file.items():
        p = repo / NOTE / f
        src = p.read_text()
        t, idx = printed_map(src)
        lines = src.split("\n")
        starts = [0]
        for ln in lines[:-1]:
            starts.append(starts[-1] + len(ln) + 1)
        per_line = {}
        for r in rows:
            ctx, old, new, anchor = r[5], r[3], r[4], r[6]
            if t.count(ctx) != 1:
                raise SystemExit(f"ANNOTATE {r[1]}: new context does not print once in {f}")
            if len(old) != len(new):     # then the anchor's offset of the value is also its offset in ctx
                raise SystemExit(f"ANNOTATE {r[1]}: old and new differ in length; locate it by hand")
            q = t.index(ctx) + anchor.index(old)
            s0 = idx[q]
            k = max(i for i, s in enumerate(starts) if s <= s0)
            per_line.setdefault(k, []).append(r[1])
        for k, ids in per_line.items():
            if NOTE_TAG in lines[k]:
                continue
            lines[k] += (f" {NOTE_TAG} RE-2-shapes run 2 (C_new), g2r-integration/ledger.tsv " + ", ".join(ids)
                         + "; a source comment citing RE-2 part C for this value gives the earlier value")
        p.write_text("\n".join(lines))
        print(f"[annotate] {f}: {len(per_line)} lines")


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check(repo, rows=None):
    fails = []
    sums = {}
    for line in open(repo / NEW_DIR / "SHA256SUMS"):
        h, name = line.split(None, 1)
        sums[name.strip().lstrip("./")] = h
    posted = posted_files(repo)
    ptext = {f: printed(repo / NOTE / f) for f in posted}
    arows = {r[1]: r for r in anchors()}
    used = set()
    for r in rows or ledger():
        vid, f, old, new, ctx, octx, src, key = r[1:9]
        a = arows.get(vid)
        if a is None:
            fails.append(f"{vid}: no ANCHORS row"); continue
        o, s, _ = values(repo, a, "old")
        nw = values(repo, a, "new")[0]
        used.add(s)
        if o != old:
            fails.append(f"{vid}: old {old} is not OLD's {o}")
        if nw != new:
            fails.append(f"{vid}: new {new} is not NEW's {nw}")
        t = printed(repo / NOTE / f)
        if t.count(ctx) != 1:
            fails.append(f"{vid}: the new context prints {t.count(ctx)} times in {f}: {ctx!r}")
        if old != new:
            for g, pt in ptext.items():
                if octx in pt:
                    fails.append(f"{vid}: the old context still prints in posted {g}: {octx!r}")
    for s in sorted(used):
        h = sums.get(s)
        if h is None:
            fails.append(f"{s}: not in the run's SHA256SUMS")
        elif h != sha256(repo / NEW_DIR / s):
            fails.append(f"{s}: sha256 differs from the run's SHA256SUMS")
    for x in fails:
        print("  FAIL " + x)
    n = len(rows or ledger())
    print(f"G2R-LEDGER :: {n} rows, {len(used)} NEW products sha-checked, {len(posted)} posted files swept -- "
          + ("PASS" if not fails else f"{len(fails)} failure(s)"))
    return fails


def self_test(repo):
    rows = ledger()
    bad_new = [list(r) for r in rows]; bad_new[0][4] = bad_new[0][4] + "9"; bad_new[0][5] += "9"
    stale = [list(r) for r in rows]
    i = next(k for k, r in enumerate(stale) if r[3] != r[4]); stale[i][6] = stale[i][5]   # old ctx = a printing one
    ok = not check(repo)
    f1 = any("is not NEW's" in x for x in check(repo, bad_new))
    f2 = any("still prints" in x for x in check(repo, stale))
    print(f"SELF-TEST :: real ledger {'silent' if ok else 'FAILS'}; wrong new value fires {f1}; "
          f"stale old context fires {f2}")
    return ok and f1 and f2


if __name__ == "__main__":
    cmd, repo = sys.argv[1], Path(sys.argv[2]).resolve()
    if cmd == "build":
        build(repo)
    elif cmd == "apply":
        apply(repo)
    elif cmd == "annotate":
        annotate(repo)
    elif cmd == "check":
        sys.exit(1 if check(repo) else 0)
    elif cmd == "--self-test":
        sys.exit(0 if self_test(repo) else 1)
    else:
        raise SystemExit(__doc__)
