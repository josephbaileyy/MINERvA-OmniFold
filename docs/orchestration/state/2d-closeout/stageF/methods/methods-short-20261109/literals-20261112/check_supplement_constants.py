#!/usr/bin/env python3
r"""The Supplement's typed decimals are design constants only (the director's D6 item, 2026-11-13).

usage: check_supplement_constants.py <worktree> [--write]

Every decimal literal printed in docs/analysis-note/supplemental_body.tex outside \fvval (comments stripped; table
column widths before \textwidth, \hsize or \linewidth excluded) must match a row of CONSTANTS below: its value
and a phrase of its own line (the first matching row names it). A printed result has a make_values_fived16.py key instead (supp_literal_values()). An
unlisted decimal, or a row that no longer matches, fails. --write regenerates supplement-constants.txt beside this file;
without it, the committed file must equal a fresh generation.
"""
import re
import sys
from pathlib import Path

# (value, a phrase on its line, class, why it stays typed)
CONSTANTS = [
    ("1.5", r"1.5 < \pPar", "phase space", "the muon phase-space cut, p|| > 1.5 GeV/c (ref. MINERvA:2021owq)"),
    ("4.5", r"\pT < \SI{4.5}", "phase space", "the muon phase-space cut, pT < 4.5 GeV/c"),
    ("3.2353", r"nucleons", "data constant", "the fiducial volume's nucleon count (the note's value)"),
    ("1.057", r"protons on targ", "data constant", "the exposure in POT (the note's value)"),
    ("2.5", r"\bar M=(1.5M_{n}+M_{p})/2.5", "definition", "the mean struck-nucleon mass's weights (1.5 M_n + M_p)/2.5"),
    ("1.17", r"1.17\times$ calorimetric", "definition", "the reconstructed Eavail calorimetric factor (CVUniverse.h)"),
    ("1.17", r"E_{\rm avail}^{\rm reco}=1.17", "definition", "the reconstructed Eavail calorimetric factor (CVUniverse.h)"),
    ("58.87", r"mrad", "definition", "the fixed beam axis's tilt from the detector axis (CVUniverse.h)"),
    ("99.9", r"for 99.9\%", "quantile level", "the residual's quoted central interval"),
    ("139.57", r"charged-pion mass", "physical constant", "the charged-pion mass, MeV"),
    ("4.57", r"charged-pion term", "physical constant", "139.57 - 135 MeV, the charged-pion term's offset"),
    ("0.1", r"[0,0.1,0.2,0.4,0.8,1.5,3.0,100]", "bin edges", "the extension axes' edges (Eavail, q3, W)"),
    ("0.2", r"[0,0.1,0.2,0.4,0.8,1.5,3.0,100]", "bin edges", "the extension axes' edges"),
    ("0.4", r"[0,0.1,0.2,0.4,0.8,1.5,3.0,100]", "bin edges", "the extension axes' edges"),
    ("0.8", r"[0,0.1,0.2,0.4,0.8,1.5,3.0,100]", "bin edges", "the extension axes' edges"),
    ("1.5", r"[0,0.1,0.2,0.4,0.8,1.5,3.0,100]", "bin edges", "the extension axes' edges"),
    ("3.0", r"[0,0.1,0.2,0.4,0.8,1.5,3.0,100]", "bin edges", "the extension axes' edges"),
    ("0.2", r"[0,0.2,0.4,0.6,0.8,1.2,2.0,100]", "bin edges", "the extension axes' edges"),
    ("0.4", r"[0,0.2,0.4,0.6,0.8,1.2,2.0,100]", "bin edges", "the extension axes' edges"),
    ("0.6", r"[0,0.2,0.4,0.6,0.8,1.2,2.0,100]", "bin edges", "the extension axes' edges"),
    ("0.8", r"[0,0.2,0.4,0.6,0.8,1.2,2.0,100]", "bin edges", "the extension axes' edges"),
    ("1.2", r"[0,0.2,0.4,0.6,0.8,1.2,2.0,100]", "bin edges", "the extension axes' edges"),
    ("2.0", r"[0,0.2,0.4,0.6,0.8,1.2,2.0,100]", "bin edges", "the extension axes' edges"),
    ("1.1", r"[0,1.1,1.4,1.8,2.2,3.0,100]", "bin edges", "the extension axes' edges"),
    ("1.4", r"[0,1.1,1.4,1.8,2.2,3.0,100]", "bin edges", "the extension axes' edges"),
    ("1.8", r"[0,1.1,1.4,1.8,2.2,3.0,100]", "bin edges", "the extension axes' edges"),
    ("2.2", r"[0,1.1,1.4,1.8,2.2,3.0,100]", "bin edges", "the extension axes' edges"),
    ("3.0", r"[0,1.1,1.4,1.8,2.2,3.0,100]", "bin edges", "the extension axes' edges"),
    ("0.07", r"$\pT=0.07$--0.15", "bin edges", "a cell's pT edges"),
    ("0.25", r"$\pT=0.25$--0.33", "bin edges", "a cell's pT edges"),
    ("1.1", r"for $W<\SI{1.1}{GeV}$", "bin edges", "the first fine W bin's upper edge"),
    ("0.1", r"learning rate 0.1", "hyperparameter", "the refinement classifier's learning rate"),
    ("0.1", r"learning rate $0.1$", "hyperparameter", "scikit-learn GradientBoosting's default learning rate"),
    ("3.6", r"$|t|>3.6$", "threshold", "the closure criterion's T_CRIT (s5n_analyze_dev.py)"),
    ("3.6", r"beyond 3.6 standard errors", "threshold", "the closure criterion's T_CRIT"),
    ("3.5", r"for protons", "input uncertainty", "the proton response's one-standard-deviation scale factor"),
    ("1.4", r"normalization \\", "input uncertainty", "the 1.4 % normalization uncertainty"),
    ("1.4", r"the 1.4\,\% normalization", "input uncertainty", "the 1.4 % normalization uncertainty"),
    ("0.5", r"scaled by 0, 0.5, 1 or 2", "design", "the run-period study's covariance scale factors"),
    ("0.05", r"$p<0.05$", "threshold", "the run-period study's test level"),
    ("0.95", r"the 0.95 and 0.997", "quantile level", "the bootstrap thresholds' levels"),
    ("0.997", r"the 0.95 and 0.997", "quantile level", "the bootstrap thresholds' levels"),
    ("0.997", r"the 0.997 quantile of $\chi^2_{16}$", "quantile level", "the alternative threshold's level"),
    ("0.997", r"its 0.997 Hotelling limit", "quantile level", "the alternative threshold's level"),
    ("0.5", r"$0.5\,|d_c|$", "threshold", "the bias-half rule's factor"),
    ("2.12", r"GENIE~2.12", "version", "the generator version"),
    ("21.09", r"NuWro~21.09", "version", "the generator version"),
    ("0.01", r"familywise rate of 0.01", "threshold", "the prior-retention study's familywise rate"),
]
NUM = re.compile(r"(?<![\w.-])\d+\.\d+(?![\w.])(?!\\textwidth|\\hsize|\\linewidth)")
HERE = Path(__file__).resolve().parent


def scan(wt):
    out = []
    for i, ln in enumerate((Path(wt) / "docs/analysis-note/supplemental_body.tex").read_text().split("\n"), 1):
        s = re.sub(r"\\fvval\{[^}]*\}", "", re.sub(r"(?<!\\)%.*$", "", ln))
        out += [(i, m.group(), s) for m in NUM.finditer(s)]
    return out


def main(argv):
    wt = argv[0]
    bad, used, rows = [], set(), []
    for i, val, s in scan(wt):
        hit = [k for k, (v, ph, *_) in enumerate(CONSTANTS) if v == val and ph in s]
        if not hit:
            bad.append(f"supplemental_body.tex:{i}: {val} is typed and listed nowhere (key it, or list it as a constant)")
            continue
        used.update(hit)
        c = CONSTANTS[hit[0]]
        rows.append(f"{val:>8}  {c[2]:<18} {c[3]}  [at: {c[1]}]")    # no line numbers: a reflow must not fail it
    bad += [f"row {k} ({CONSTANTS[k][0]}, {CONSTANTS[k][1]!r}) matches no typed decimal" for k in range(len(CONSTANTS)) if k not in used]
    if bad:
        print("SUPP-CONSTANTS :: FAIL\n  " + "\n  ".join(bad))
        return 1
    text = ("# The Supplement's typed decimals: design constants only (check_supplement_constants.py; the director's D6)\n"
            "# Printed results are keyed in make_values_fived16.py supp_literal_values(). Table column widths are excluded.\n"
            + "\n".join(rows) + "\n")
    f = HERE / "supplement-constants.txt"
    if argv[1:2] == ["--write"]:
        f.write_text(text)
    elif not f.exists() or f.read_text() != text:
        print("SUPP-CONSTANTS :: FAIL (supplement-constants.txt differs from a fresh generation; rerun with --write)")
        return 1
    print(f"SUPP-CONSTANTS :: PASS ({len(rows)} typed decimals, each a listed constant)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
