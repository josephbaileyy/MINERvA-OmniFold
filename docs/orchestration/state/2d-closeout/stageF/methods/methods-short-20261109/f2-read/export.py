"""Export changed sentence pairs (base -> current) for an independent meaning read (the director, 2026-11-09).

usage: export_pairs.py <worktree> <outdir>
Paper (paper_body.tex, main_paper.tex): cb87c1832 -> working tree. Supplement (supplemental_body.tex): 531fefe42 ->
working tree. Comments are stripped and whitespace collapsed; sentences split as check_restyle splits them.
A pair is "decided" (written to decided.tsv, not pairs.tsv) only if every added word run of the current side, with
three words of context on either side, occurs inside a quoted span of a single ledger.md line that names a decision
(W-n, P-n, Joseph, the director, a DECISION file or a #PR). Base and current sentences pair only at a similarity
ratio of at least 0.6; below it they are exported as separate base-only and current-only rows. Anything else, including unpaired insertions and
deletions, is exported.
"""
import csv, difflib, re, subprocess, sys
from pathlib import Path

wt, out = Path(sys.argv[1]), Path(sys.argv[2])
NOTE = "docs/analysis-note"
LEDGER = wt / "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/ledger.md"
JOBS = [("paper_body.tex", "f9b32c850"), ("main_paper.tex", "f9b32c850"), ("supplemental_body.tex", "f9b32c850"), ("main_supplement.tex", "f9b32c850")]


def strip(t):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", l) for l in t.split("\n"))


def sentences(t):
    """(section, sentence) in order; the section is the last \\section/\\subsection/\\paragraph title seen."""
    s = strip(t)
    out, sec = [], ""
    for chunk in re.split(r"(\\(?:sub)*section\*?\{[^}]*\}|\\paragraph\{[^}]*\})", s):
        m = re.match(r"\\(?:sub)*section\*?\{([^}]*)\}|\\paragraph\{([^}]*)\}", chunk)
        if m:
            sec = (m.group(1) or m.group(2)).strip()
            continue
        c = re.sub(r"\s+", " ", chunk).strip()
        for x in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", c):
            if len(x.strip()) > 3:
                out.append((sec, x.strip()))
    return out


quotes = []          # (line number, line, [quoted spans])
for n, line in enumerate(LEDGER.read_text().split("\n"), 1):
    if re.search(r"\bW-\d+|\bP-\d+|Joseph|director|DECISION|#\d{3,}", line):
        qs = re.findall(r'"([^"]{3,})"|“([^”]{3,})”|`([^`]{3,})`', line)
        qs = [next(x for x in q if x) for q in qs]
        if qs:
            quotes.append((n, line, qs))


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[\\{}$~]", " ", s)).strip().lower()


def runs(a, b, ctx=3):
    """The removed runs of a and the added runs of b, word level, each with ctx words of context on either side."""
    aw, bw = a.split(), b.split()
    rem, add = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, aw, bw, autojunk=False).get_opcodes():
        if op in ("replace", "delete"):
            rem.append(" ".join(aw[max(0, i1 - ctx):i2 + ctx]))
        if op in ("replace", "insert"):
            add.append(" ".join(bw[max(0, j1 - ctx):j2 + ctx]))
    return rem, add


def decided(a, b):
    """A ledger line that quotes every changed run of b, with its context, and that names a decision; pure deletions
    and changes it does not quote in full are not attributed."""
    rem, add = runs(a, b)
    want = [norm(x) for x in add if norm(x)]
    if not want:
        return None
    for n, line, qs in quotes:
        nq = [norm(q) for q in qs]
        if all(any(w in q for q in nq) for w in want):
            row = re.match(r"\s*\|\s*([A-Z]+-\d+[a-z]?)", line)
            return f"ledger.md:{n}" + (f" ({row.group(1)})" if row else "")
    return None


pairs, dec = [], []
for f, base in JOBS:
    old = sentences(subprocess.run(["git", "-C", str(wt), "show", f"{base}:{NOTE}/{f}"], capture_output=True, text=True,
                                   check=True).stdout)
    new = sentences((wt / NOTE / f).read_text())
    ot, nt = [x for _, x in old], [x for _, x in new]
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ot, nt, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        A, B = list(range(i1, i2)), list(range(j1, j2))
        used, matched = set(), []
        for i in A:                                   # pair each base sentence with its most similar current one
            best = max(((difflib.SequenceMatcher(None, ot[i], nt[j]).ratio(), j) for j in B if j not in used), default=(0, None))
            if best[1] is not None and best[0] >= 0.6:
                used.add(best[1]); matched.append((i, best[1]))
            else:
                matched.append((i, None))
        matched += [(None, j) for j in B if j not in used]
        matched.sort(key=lambda x: (x[1] if x[1] is not None else (j1 - 0.5), x[0] or 0))
        for i, j in matched:
            a = ot[i] if i is not None else ""
            b = nt[j] if j is not None else ""
            if re.sub(r"\s+", " ", a) == re.sub(r"\s+", " ", b):
                continue
            sec = (new[j][0] if j is not None else old[i][0])
            ref = decided(a, b) if a and b else None
            (dec if ref else pairs).append({"file": f, "section": sec, "base": a, "current": b, "ledger": ref})

out.mkdir(parents=True, exist_ok=True)
with open(out / "pairs.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    w.writerow(["id", "file", "section", "base", "current"])
    for k, p in enumerate(pairs, 1):
        w.writerow([f"M{k:03d}", p["file"], p["section"], p["base"], p["current"]])
with open(out / "decided.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    w.writerow(["id", "file", "section", "ledger", "base", "current"])
    for k, p in enumerate(dec, 1):
        w.writerow([f"D{k:03d}", p["file"], p["section"], p["ledger"], p["base"], p["current"]])
from collections import Counter
print("pairs", len(pairs), dict(Counter(p["file"] for p in pairs)), "| decided", len(dec), dict(Counter(p["file"] for p in dec)))
print("unpaired: base-only", sum(1 for p in pairs if not p["current"]), "current-only", sum(1 for p in pairs if not p["base"]))
