#!/usr/bin/env python3
"""Check the 5B text round's ledger: r22/step2/check_ledger.py, run with this round's base, ledger and abstract pairs.

The checks are step2/check_ledger.py's (one implementation; see its docstring). This round sets:
  - the base ac8fb9ae3 (origin/main at the round's start, after #614);
  - the ledger default 5b-text-20261031/ledger.md;
  - PROTECTED without the files this round changes by decision (DECISION-20261030 item 2, DECISION-20261031-joseph-j1-
    j2-and-protections-split.md): values_fived16.tex (generated, --check), paper_body.tex and main_paper.tex (checked by
    the ledger's P:: and N: probes, check_held.py and agy);
  - ABSTRACT: main_note.tex's source comment and its whole revised abstract (Joseph's choice, DECISION-20261031-joseph-abstracts-astra-without-exclusions-line.md, #632), each pinned by sha256 once Joseph approves the whole
    revised abstract (A4, DECISION-20261031 item 3). Unpinned, a pair allows nothing, so check 4 fails until then.
usage: as step2/check_ledger.py (--files, --list, --self-test, --no-n4-frozen)."""
import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_ledger2", HERE.parent / "r22" / "step2" / "check_ledger.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)
BASE = "ac8fb9ae3"
cl.PROTECTED = [p for p in cl.PROTECTED if p not in ("values_fived16.tex", "paper_body.tex", "main_paper.tex")]
cl.ABSTRACT = [
    ("5B-c", "\\begin{abstract}\n", "\\begin{abstract}\n" + "% DECISION-20261031-joseph-abstracts-astra-without-exclusions-line.md (#632): the astra consult's abstract (secondary-results/astra-consult-abstracts-coverage-20261031/answer.txt section 2) without its exclusions sentence, which stays in the body (paper_body.tex sec:limits; the note's own exclusion wording is sec_joint.tex's). Sources: the median, the run-period block and its timing, paper_body.tex sec:cov16 and values_fived16.tex (sigmed-reported); the chi2 range, ndf, GiBUU's value and cells, values_fived16.tex (g-ext-chi2int-*, g-gcv-total-ndf, g-gibuu-total-chi2int, g-gibuu-ncells-word); the thresholds predeclared: FD-DIRECTOR-RULINGS.md section 2 (bound 2026-10-25, 092702292) before F0 landed (28c4870f4), reused unchanged by F0b and the with-block chain; the listed truths, make_values_fived16.py LISTED_CLAIMS; the two held-out truths below the reported uncertainty, sec_fived16.tex (f1-bsig-ceil); coverage not validated, sec_fived16.tex sec:fived16-fd." + "\n"),
    ("5B-a", "We report a simultaneous measurement of the $\\nu_{\\mu}$ charged-current inclusive cross section in five observables: the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass. The cross section is unfolded without binning with OmniFold from MINERvA medium-energy open data. It is reported in sixteen cells, with a covariance whose median per-cell uncertainty is \\fvval{sigmed-C_total_resp}\\%. Three external generator predictions, compared on all sixteen cells, give $\\chi^{2}$ between \\fvval{g-ext-chi2int-min16} and \\fvval{g-ext-chi2int-max16} for 16 degrees of freedom. GiBUU, compared only on the 8 cells its sample covers, gives $\\chi^{2}=\\fvval{g-gibuu-total-chi2int}$ on those cells. The coverage of the result's intervals has not been validated; a bias test at two held-out GENIE~v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt.",
     'We present a simultaneous measurement of the inclusive muon-neutrino charged-current cross section in muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass. The measurement uses OmniFold to unfold MINERvA medium-energy open data without binning and reports cross sections and their covariance in sixteen cells. The median relative uncertainty per cell is \\fvval{sigmed-reported}\\%, including a run-period contribution estimated after differences between periods were observed. Three external generator predictions give $\\chi^{2}$ values of \\fvval{g-ext-chi2int-min16}--\\fvval{g-ext-chi2int-max16} for \\fvval{g-gcv-total-ndf} degrees of freedom; GiBUU gives \\fvval{g-gibuu-total-chi2int} on its \\fvval{g-gibuu-ncells-word} supported cells. Bias tests at two held-out GENIE~v3 truths find residuals below the reported uncertainty in every cell. At a GiBUU-like truth and a synthetic momentum-transfer tilt, residual bias exceeds predeclared uncertainty-based thresholds. The coverage of the reported uncertainty intervals has not been validated.'),
]
# set when Joseph approves the revised note abstract as a whole: sha256(old + "\0" + new)[:16] per pair
cl.ABSTRACT_PINS = {}
if __name__ == "__main__":
    if "--pins" in sys.argv:
        for i, old, new in cl.ABSTRACT:
            print(i, hashlib.sha256((old + "\0" + new).encode()).hexdigest()[:16])
        sys.exit(0)
    args = sys.argv[1:]
    if "--base" not in args:
        args += ["--base", BASE]
    if "--ledger" not in args:
        args += ["--ledger", str(HERE / "ledger.md")]
    sys.argv = [sys.argv[0]] + args
    sys.exit(cl.main())
