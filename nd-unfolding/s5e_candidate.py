#!/usr/bin/env python3
"""s5e candidate runs: ``s5n_pseudo.main`` (experiments, bootstraps with refinement refit, real data,
row-permutation and estimator-seed probes) under one frozen candidate definition.

    s5e_candidate.py --candidate R -- <s5n_pseudo.py arguments>

The only candidate this module defines is the one frozen by contract amendment 3:

* ``B0``: the s5n family N exactly (nothing is patched; for paired references).
* ``R``: B0 with the Stay-Positive refinement classifier at n_estimators 400, num_leaves 31 (the other
  F2 refinement settings and random_state = estimator_seed + 3 unchanged). The override is merged into
  ``s5n_pseudo.refine_params``, so ``s5n_pseudo.refine`` still verifies every parameter of the
  classifier it actually built against the merged set, and each product's refinement evidence records
  them.

Truth ``ratio_nd`` (the multi-dimensional withheld deformations W2, W3) is available through
``s5e_deform.install_ratio_truth`` with the ratio file passed as ``--eavail-ratio``.

MEASURES: the candidate's products. CANNOT AUTHORIZE: a verdict by itself (the frozen criteria of
amendment 3 are evaluated by s5e_analyze_candidate.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s5e_deform  # noqa: E402
import s5n_pseudo  # noqa: E402

CANDIDATES = {"B0": {}, "R": {"n_estimators": 400, "num_leaves": 31}}


def install(candidate: str) -> dict:
    override = CANDIDATES[candidate]
    s5e_deform.install_ratio_truth(s5n_pseudo)
    base_params, base_digests = s5n_pseudo.refine_params, s5n_pseudo.code_digests

    def refine_params(estimator_seed, threads):
        return {**base_params(estimator_seed, threads), **override}

    def code_digests():
        return {**base_digests(), "s5e_candidate.py": s5n_pseudo.sha256_path(Path(__file__).resolve()),
                "s5e_deform.py": s5n_pseudo.sha256_path(_ND / "s5e_deform.py"), "candidate": candidate,
                "candidate_refine_override": override}

    s5n_pseudo.refine_params = refine_params
    s5n_pseudo.code_digests = code_digests
    return override


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 3 or argv[0] != "--candidate" or argv[2] != "--" or argv[1] not in CANDIDATES:
        print(f"usage: s5e_candidate.py --candidate {{{','.join(CANDIDATES)}}} -- <s5n_pseudo.py args>", file=sys.stderr)
        return 2
    install(argv[1])
    return s5n_pseudo.main(argv[3:])


if __name__ == "__main__":
    sys.exit(main())
