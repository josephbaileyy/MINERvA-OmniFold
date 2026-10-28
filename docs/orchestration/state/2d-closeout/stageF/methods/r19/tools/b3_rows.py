"""usage: python3 b3_rows.py R19_DIR LIST_FILE UNCOVERED_FILE -- r19 b3: ledger rows for the sentences that leave with
Sec. VI and with K8, K9 and K13. Each removed base sentence is matched by its text to its row of move-pass/rows.tsv.
The row takes the note probes that the move pass verified (cov-*.tsv, PRINTS or PARTIAL with a probe). A paper-only
fact (P1-P4, P6, P7) takes its landing probe in N1 or N2. Prints ledger rows; the caller appends them and runs
check_ledger.py, which re-verifies every probe against the note."""
import csv, re, sys
R, LST, UNC = sys.argv[1:4]
norm = lambda s: re.sub(r"\s+", " ", s).strip()
lst = {}
for b in open(LST).read().split("\n\n"):
    m = re.match(r"(P\d+): (.*)", b.strip(), re.S)
    if m:
        lst[m.group(1)] = norm(m.group(2))
rows = list(csv.DictReader(open(f"{R}/move-pass/rows.tsv"), delimiter="\t"))
cov = {}
for g in "ABCD":
    for r in csv.DictReader(open(f"{R}/move-pass/cov-{g}.tsv"), delimiter="\t"):
        cov.setdefault(r["row"], []).append(r)
LAND = {  # paper-only facts: their landing probes in the note (N1, N2)
    "59": "`N:sec_joint.tex::For hypothesis tests the advantage is smaller.`",
    "60": "`N:sec_joint.tex::A test at reconstruction level would avoid the regularization bias, but it would still need the same response model.`",
    "61": "`N:sec_joint.tex::which is the hybrid construction of \\S\\ref{sec:joint5d-design}, with the same composition below the fine grid.`",
    "62": "`N:sec_joint.tex::so that the bias enters the null distribution rather than the decision.`",
    "63": "`N:sec_joint.tex::We have not compared their power with that of a reconstruction-level test.`",
    "95": "`N:sec_joint.tex::The error control applies to the decisions, not separately to the point estimates $(k+1)/(B+1)$.`",
}
HEAD = "`N:sec_joint.tex::\\section{Calibrated joint tests of generator predictions}`"
out = []
for u in [l.strip() for l in open(UNC) if l.strip()]:
    s = lst[u]
    hit = [r for r in rows if norm(r["paper_sentence"]) == s or (len(s) > 40 and (s in norm(r["paper_sentence"]) or norm(r["paper_sentence"]) in s))]
    if not hit:
        continue
    r = hit[0]; item = r["item"]
    if item not in ("VI", "VI-T6"):
        continue                                 # K8, K9 and K13 get hand rows
    probes = []
    for c in cov.get(r["row"], []):
        if c["verdict"] in ("PRINTS", "PARTIAL") and c["probe"].strip():
            p = f"`N:{c['note_file'].strip()}::{norm(c['probe'])}`"
            if p not in probes:
                probes.append(p)
    if r["row"] in LAND:
        probes.append(LAND[r["row"]])
    if not probes:
        probes = [HEAD]                          # a heading or a pointer: the note's section holds its content
    out.append(f"| B3-{u} | Sec. VI leaves (variant B): move-pass row {r['row']} ({item}) | {u} | MOVE→note (b3, VI) | sec_joint.tex | {' && '.join(probes[:4])} |")
print("\n".join(out))
