"""The held-out record of the staged 1B declaration (FD-1B-STAGED-DECLARATION.md section 3): where the GENIE v3
tunes G18_10a_02_11b and AR23_20i_00_000 appear in the repository, against when C_model, S1's assembly and the
estimator were fixed. Every query and its exit status are printed; an empty search is printed as empty with its
pattern and scope, never summarised as an absence beyond them.

    python3 -I docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/provenance.py

run from the repository root; the output is ``provenance.out`` beside this file.
"""
from __future__ import annotations

import subprocess
import sys

TUNES = r"G18|AR23|g18|ar23|G1810a|AR2320i"
ESTIMATOR_AND_COVARIANCE = [
    "nd-unfolding/pv-ladder/build_cmodel5d.py", "nd-unfolding/pv-ladder/config.json",
    "nd-unfolding/pv-ladder/readouts/cmodel_5d.json", "nd-unfolding/pv-ladder/readouts/h2_definition.json",
    "nd-unfolding/s1_assemble.py", "nd-unfolding/s5c_unfold.py", "nd-unfolding/s5c_pseudo.py",
    "nd-unfolding/s5n_pseudo.py", "nd-unfolding/s5e_candidate.py", "nd-unfolding/omnifold_nn_core.py",
    "nd-unfolding/xsec_nd.py", "nd-unfolding/s5p_universe.py", "nd-unfolding/s5p_nullexp.py",
]


def run(args: list[str]) -> None:
    p = subprocess.run(args, capture_output=True, text=True)
    print("$ " + " ".join(args))
    print(p.stdout.rstrip() if p.stdout.strip() else "(empty)")
    print(f"rc={p.returncode}\n")


def main() -> int:
    run(["git", "rev-parse", "HEAD"])
    # (1) the tunes in C_model's builder, S1's assembly and the estimator's code
    run(["git", "grep", "-n", "-E", TUNES, "--", *ESTIMATOR_AND_COVARIANCE])
    # (2) the C_model vertices
    run(["git", "grep", "-n", "-E", r"^VERTICES|for k in \(", "--", "nd-unfolding/pv-ladder/build_cmodel5d.py"])
    # (3) first-add and last-change dates
    for path in ESTIMATOR_AND_COVARIANCE[:5] + ESTIMATOR_AND_COVARIANCE[5:10]:
        run(["git", "log", "--diff-filter=A", "--format=%h %ad first-add", "--date=short", "--", path])
        run(["git", "log", "-1", "--format=%h %ad last-change", "--date=short", "--", path])
    for path in ("3d-unfolding/genie/gen5d_v3.py", "nd-unfolding/fd_f1_prep.py"):
        run(["git", "log", "--diff-filter=A", "--format=%h %ad first-add", "--date=short", "--", path])
    # (4) the earliest commits whose diffs name either tune
    for s in ("G18_10a", "AR23_20i", "genie_v3_g18"):
        run(["git", "log", "--all", f"-S{s}", "--format=%h %ad %s", "--date=short", "--reverse"])
    # (5) does a decision record or the measurement code cite the October inelastic study that first named them?
    run(["git", "grep", "-n", "-l", "inelastic-high-region-20261011", "--", "docs/orchestration/DECISION-*",
         "nd-unfolding"])
    run(["git", "grep", "-n", "-E", "authorizes nothing|names G18_10a", "--",
         "docs/orchestration/state/inelastic-high-region-20261011/REPORT.md"])
    # (6) the paper's statement of the tunes and of the qualifier
    run(["git", "grep", "-n", "-o", "-E", r"held out of (the analysis|its construction)", "--",
         "docs/analysis-note/paper_body.tex"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
