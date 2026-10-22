"""Split the note's pdftotext dump into blinded rating pieces.

usage: python3 -I split_note.py NOTE_TXT OUTDIR
Line ranges are 1-based, half-open [start, end), taken from heads.py output on the r12 note build
(sha256 c6fd1ebe...). Each range must begin on its expected heading (asserted). Blinding:
  dropped ranges: title page/author block (1-14), table of contents (238-402), Acknowledgments (8331-8354),
                  References (11942-EOF); author e-mail footnotes (lines 44-46);
  in-body substitutions: the author's repository URL -> "[repository]"; the deposit placeholder clause
                  ", identified at deposit: [snapshot identifier pending deposit]" -> removed (a hold, as in the paper's rater copy);
  page numbers: a bare 1-3 digit line immediately before a form feed.
Writes OUTDIR/<id>.txt and OUTDIR/pieces.json, and prints a coverage audit (every line is in exactly one piece or
one dropped range).
"""
import json, re, sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
raw = src.read_text(encoding="utf-8")
L = raw.split("\n")
n = len(L)
page, pg = 1, []
for l in L:
    page += l.count("\f"); pg.append(page)

DROPS = [("title page and author block", 1, 15), ("table of contents", 238, 403),
         ("Acknowledgments", 8331, 8355), ("References", 11942, n + 1)]
PIECES = [  # id, title, [(start, end, expected heading regex at start or start+2)]
    ("N01", "Abstract, Executive summary, Sec. 1 Introduction and motivation", [(15, 238, r"^Abstract$"), (403, 520, r"^Introduction and motivation$")]),
    ("N02", "Sec. 2 Experiment, data and simulation; Sec. 3 The unbinned OmniFold procedure", [(520, 1562, r"^The MINERvA experiment")]),
    ("N03", "Sec. 4 Uncertainty quantification: constructing the covariance blocks", [(1562, 2051, r"^Uncertainty quantification")]),
    ("N04", "Sec. 5 Validation of the two-dimensional measurement", [(2051, 2517, r"^Validation of the two-dimensional")]),
    ("N05", "Sec. 6 Results", [(2517, 4546, r"^Results$")]),
    ("N06", "Sec. 7 Higher-dimensional extensions: available energy and momentum transfer", [(4546, 5545, r"^Higher-dimensional extensions")]),
    ("N07", "Sec. 8 Fifth axis: W and the (Eavail, W) plane", [(5545, 6129, r"^Fifth axis")]),
    ("N08", "Sec. 9 Five-dimensional estimator: validation and uncertainty", [(6129, 7003, r"^Five-dimensional estimator")]),
    ("N09", "Sec. 10 Calibrated joint tests of generator predictions", [(7003, 7860, r"^Calibrated joint tests")]),
    ("N10", "Sec. 11 Extended fiducial phase-space study; Sec. 12 Summary and outlook", [(7860, 8331, r"^Extended fiducial")]),
    ("N11", "Guide to the appendices; App. A Statistical methods and the 2D comparison", [(8355, 9509, r"^Guide to the appendices$")]),
    ("N12", "App. B Statistical methods for the multidimensional results; App. C Negative-weight background subtraction", [(9509, 10072, r"^Statistical methods for the multidimensional")]),
    ("N13", "App. D Response-mismatch closure; App. E Dimensionality survey; App. F Point clouds; App. G Provenance", [(10072, 10577, r"^Detector-response-mismatch")]),
    ("N14", "App. H Result package and fixed identities; App. I Codebase layout and terminology", [(10577, 10846, r"^Result package")]),
    ("N15", "App. J Superseded values and withdrawn results", [(10846, 11942, r"^Superseded values and withdrawn results$")]),
]
EMAIL_LINES = {44, 45, 46}  # '∗ †' marker line and the two e-mail lines (checked below)
REPO = [r"github\.com/josephbaileyy/MINERvA-?\s*OmniFold", r"github\.com/josephbaileyy/MINERvA\S*"]
HOLD = r",? identified at deposit:\s*\[snapshot identifier pending deposit\]"

owner = [None] * (n + 1)
def claim(a, b, who):
    for i in range(a, b):
        if i <= n:
            assert owner[i] is None, f"line {i} claimed twice ({owner[i]}, {who})"
            owner[i] = who
for name, a, b in DROPS:
    claim(a, b, "DROP:" + name)
for pid, _, rngs in PIECES:
    for a, b, rx in rngs:
        claim(a, b, pid)
missing = [i for i in range(1, n + 1) if owner[i] is None]
assert not missing, f"unclaimed lines: {missing[:20]} ..."
for i in EMAIL_LINES:
    assert re.search(r"(@stanford\.edu|^[∗†\s]*$)", L[i - 1]), (i, L[i - 1])

meta = []
for pid, title, rngs in PIECES:
    lines, p0, p1 = [], None, None
    for a, b, rx in rngs:
        head = [L[a - 1].strip(), L[a + 1].strip() if a + 1 < n else ""]
        assert any(re.search(rx, h) for h in head), (pid, a, head)
        for i in range(a, b):
            if i in EMAIL_LINES:
                continue
            lines.append(L[i - 1])
            if L[i - 1].strip():
                p0 = pg[i - 1] if p0 is None else p0
                p1 = pg[i - 1]
    t = "\n".join(lines)
    t = re.sub(r"\n[ \t]*\d{1,3}[ \t]*\n(?=\s*\f)", "\n", t)  # page number before a page break
    t = re.sub(r"\f[ \t]*\d{1,3}[ \t]*\n", "\f\n", t)
    if pid == "N01":  # page 1 footer sits before the first form feed after the e-mail lines
        t = re.sub(r"\n[ \t]*1[ \t]*\n(?=\s*\fwith a biased estimator)", "\n", t)
    nrepo = 0
    for rx in REPO:
        t, k = re.subn(rx, "[repository]", t); nrepo += k
    t, nhold = re.subn(HOLD, "", t)
    t = t.replace("\f", "\n")
    t = re.sub(r"\n{3,}", "\n\n", t).strip() + "\n"
    bad = re.findall(r"Bailey|Nachman|Stanford|stanford\.edu|josephbaileyy|HOLD|pending deposit", t)
    assert not bad, (pid, bad)
    (out / f"{pid}.txt").write_text(t, encoding="utf-8")
    m = dict(id=pid, title=title, pages=f"{p0}-{p1}", lines=[[a, b] for a, b, _ in rngs], words=len(t.split()),
             repo_subs=nrepo, holds_removed=nhold)
    meta.append(m)
    print(f"{pid}\tpp {p0}-{p1}\t{m['words']:6d} words\trepo->{nrepo} hold->{nhold}\t{title}")
(out / "pieces.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
dropped = sum(1 for i in range(1, n + 1) if owner[i].startswith("DROP"))
print(f"coverage: {n} lines, {dropped} dropped, {n - dropped} in pieces; total piece words {sum(m['words'] for m in meta)}")
