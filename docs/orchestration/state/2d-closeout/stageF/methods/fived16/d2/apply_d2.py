r"""usage: python3 -I apply_d2.py ANALYSIS_NOTE_DIR [1|2|all] -- the d2 edits (DECISION-20261028-joseph-final-draft-d), as exact
old -> new pairs, whitespace-tolerant, each matching exactly once.

Stage 1, decided by Joseph:
- T1, item 1: the title is T1 (WORDING-PACKET.md, the round-3 choice). main_note.tex's title is the note's own
  ("Analysis Note: Unbinned OmniFold analysis …") and does not follow the paper's, so it is unchanged.
- H1, item 5: IV H takes PRD read r6's sol2 r2 form (154 words), already read in r6 and SAME in agy (c1a/agy/r6).
  CHECK_H1 asserts that the new paragraph prints exactly as r6's form."""
import json
import re
import sys
from pathlib import Path

TITLE = [("T1", r"\title{Performance and limitations of multidimensional OmniFold unfolding with MINERvA open data}",
          r"\title{Simultaneous measurement of the $\nu_{\mu}$ charged-current inclusive cross section on hydrocarbon in five observables from MINERvA open data}")]
H1_OLD = r"Two GENIE~v3 tunes, \fvval{f1-tune-g18} and \fvval{f1-tune-ar23}, were generated for this test and held out of the analysis. Each reweights the simulated truth by the tune's shape ratio to GENIE CV, built as for the $C_{\mathrm{model}}$ components; the detector response is the simulation's and is not probed. For each tune, \fvval{f1-n} Poisson pseudo-experiments and a noise-free closure are compared with the truth using the full reported covariance. Both tunes satisfy both bias criteria: the pseudo-experiment means give $\chi^2=\fvval{f1-g18-chi2}$ ($p=\fvval{f1-g18-p}$) and \fvval{f1-ar23-chi2} ($p=\fvval{f1-ar23-p}$), respectively, with $|z|\leq\fvval{f1-zmax-ceil}$ in every cell of the means and closures. Both are GENIE tunes and use the same quasielastic cross-section model; \fvval{f1-tune-g18} also uses a Valencia-family MEC model, as does the GENIE + MEC component of $C_{\mathrm{model}}$. They provide partial evidence and are not independent tests. Omitting that component gives $\chi^2=\fvval{f1-g18-sens-chi2}$ ($p=\fvval{f1-g18-sens-p}$) and \fvval{f1-ar23-sens-chi2} ($p=\fvval{f1-ar23-sens-p}$), respectively, as a descriptive comparison. These tests assess bias, not coverage: only event counts fluctuate, without variation of systematic parameters, so interval widths cannot be tested."
H1_NEW = r"Two GENIE~v3 tunes, \fvval{f1-tune-g18} and \fvval{f1-tune-ar23}, were generated for this test and held out of the analysis. Each reweights the simulated truth using its shape ratio to GENIE CV, constructed as for the $C_{\mathrm{model}}$ components. The simulated detector response is not probed. For each tune, \fvval{f1-n} Poisson pseudo-experiments and a noise-free closure are compared with the truth using the full reported covariance. Both tunes satisfy the bias criteria: the pseudo-experiment means give $\chi^2=\fvval{f1-g18-chi2}$ ($p=\fvval{f1-g18-p}$) and \fvval{f1-ar23-chi2} ($p=\fvval{f1-ar23-p}$), respectively, with $|z|\leq\fvval{f1-zmax-ceil}$ in every cell of the means and closures. The tunes share a quasielastic cross-section model; \fvval{f1-tune-g18} and the GENIE + MEC component of $C_{\mathrm{model}}$ also use Valencia-family MEC models. These tests provide partial evidence and are not independent. Omitting that $C_{\mathrm{model}}$ component gives $\chi^2=\fvval{f1-g18-sens-chi2}$ ($p=\fvval{f1-g18-sens-p}$) and \fvval{f1-ar23-sens-chi2} ($p=\fvval{f1-ar23-sens-p}$), respectively, as a descriptive comparison. The tests assess bias, not coverage: only event counts fluctuate, with systematic parameters fixed, so interval widths cannot be tested."
PAPER1 = [("H1", H1_OLD, H1_NEW)]

# Stage 2, the independent raters' choices (d2/raters, d2/raters-v2; d2/REPORT.md), after the truth column:
# - ABS-P: the paper abstract is candidate PB (8 of 8 runs over the two reads);
# - ABS-N: the note abstract is candidate NA (v2; 3 of 4, sol2's two runs split by order);
# - O3: the qualified form (B3; sol2 2 of 2, gemini 0 of 2: the models split, so sol2's true form, round 3's rule);
# - R11: the R11 sentence in IV H (B9, 4 of 4).
# The abstract pairs are built from d2/candidates.json: OLD is the printed abstract's own sentences, NEW the candidate.
D2 = Path(__file__).resolve().parent
_C = json.loads((D2 / "candidates.json").read_text(encoding="utf-8"))
ABS_P = ("ABS-P", " ".join(_C["paper"]["sentences"]), _C["paper"]["candidates"]["PB"]["tex"])
ABS_N = ("ABS-N", " ".join(_C["note"]["sentences"]), _C["note"]["candidates"]["NA"]["tex"])
sys.path.insert(0, str(D2))
import options as _OP  # noqa: E402
PAPER2 = [("O3", _OP.O3["K"], _OP.O3["Q"]), ("R11", _OP.R11["K"], _OP.R11["C"])]


def pat(s):
    return re.compile(r"\s+".join(re.escape(w) for w in s.split()))


def apply(path, edits):
    t = open(path, encoding="utf-8").read()
    for k, old, new in edits:
        m = list(pat(old).finditer(t))
        if len(m) != 1:
            sys.exit(f"{k}: {len(m)} matches in {path}")
        t = t[:m[0].start()] + new + t[m[0].end():]
    open(path, "w", encoding="utf-8").write(t)


def check_h1(worktree):
    """The new paragraph must print exactly as PRD read r6's sol2 r2 form."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "final-draft"))
    import texplain
    texplain.init(worktree)
    r6 = (Path(__file__).resolve().parents[1] / "prd-read/r6/runs/PR6__r2__sol2.txt").read_text()
    form = re.search(r"^H1: VERDICT: SHORTEN\nSHORTER-FORM: (.*)$", r6, re.M).group(1).strip()
    assert texplain.plain(H1_NEW, "paper") == form, "H1_NEW does not print as r6's form"


if __name__ == "__main__":
    D = sys.argv[1]
    check_h1(Path(D).resolve().parents[1])
    stage = sys.argv[2] if len(sys.argv) > 2 else "all"
    if stage in ("1", "all"):
        apply(f"{D}/main_paper.tex", TITLE)
        apply(f"{D}/paper_body.tex", PAPER1)
        print("d2 stage 1 applied: T1, H1")
    if stage in ("2", "all"):
        apply(f"{D}/main_paper.tex", [ABS_P])
        apply(f"{D}/main_note.tex", [ABS_N])
        apply(f"{D}/paper_body.tex", PAPER2)
        print("d2 stage 2 applied: ABS-P (PB), ABS-N (NA), O3, R11")
