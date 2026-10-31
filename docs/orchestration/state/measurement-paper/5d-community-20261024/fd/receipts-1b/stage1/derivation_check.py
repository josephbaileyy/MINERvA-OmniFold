#!/usr/bin/env python3
"""1B stage 1's derivation check on the real inputs (FD-1B-DECLARATION.md section 8 item 5; "Reads in stage 1: the
code, the committed records, and S1's assembly npz and lateral unfolds for the derivation"). Login node, 0 node-h.

It calls the committed toy mode and scorer on the pinned inputs and prints DERIVATION facts only, never a
cross-section value:
* S1's npz digest and block set; the drawn matrix M_d against C_e; the surrogates' share of C_e's trace;
* the lateral Delta_b from the 10 lateral unfolds (X01 applied) reproduce S1's lateral blocks, (1/4) Delta Delta^T;
* M_d and the reported matrix are positive definite in relative form (4A's refusal would not fire at f);
* the real bank's interaction bands are S1's 33 and its Flux universes 0-99; the flux probabilities' n_eff;
* both test truths' ratios carry the committed F1 prep digests;
* the expected over-coverage per cell, erf(r / sqrt 2) with r = sigma_reported / sigma_drawn (context only).

    python3 derivation_check.py --deploy D
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

P = Path("/pscratch/sd/j/josephrb")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--deploy", type=Path, required=True)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(a.deploy / "nd-unfolding"))
    import fd_1b_score as fs
    import fd_1b_toys as toys
    import s1_assemble as sa

    s1 = fs.load_s1(P / "s1-20261024/s1_assembly.npz")
    f = s1["f"]
    rel = lambda C: C / np.outer(f, f)  # noqa: E731
    M_d, R = fs.drawn_matrix(s1), fs.reported_matrix(s1)
    out = {"label": "DERIVATION", "s1_npz_sha256": fs.S1_NPZ_SHA256, "blocks": len(s1["blocks"]),
           "seed_block_max_abs_rel": float(np.abs(rel(s1["blocks"]["seed"])).max()),
           "M_d_equals_C_e_minus_seed_rel": float(np.abs(rel(M_d + s1["blocks"]["seed"] - s1["C_e"])).max()),
           "surrogate_share_of_C_e_trace": fs.surrogate_share(s1)}
    deltas = fs.lateral_deltas(s1, P / "s5p-20260926/runs/s3/latunf",
                               a.deploy / "nd-unfolding/pv-ladder/readouts/h2_definition.json",
                               P / "MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",
                               P / "2d-closeout-c04repair-20261012/build/minos_rescaled.npz",
                               a.deploy / "docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt")
    out["lateral_blocks_reproduced_rtol_1e-10"] = sorted(deltas)
    for name, M in (("M_d", M_d), ("reported", R)):
        e = np.linalg.eigvalsh(rel(M))
        out[f"{name}_relative_eigen"] = {"min": float(e.min()), "max": float(e.max()), "cond": float(e.max() / e.min())}
        np.linalg.cholesky(rel(M))
    r = np.sqrt(np.diag(R) / np.diag(M_d))
    out["expected_overcoverage_context_only"] = {
        "c1_mean": float(np.mean([math.erf(x / math.sqrt(2)) for x in r])),
        "c1_min": float(min(math.erf(x / math.sqrt(2)) for x in r)),
        "c2_mean": float(np.mean([math.erf(2 * x / math.sqrt(2)) for x in r])),
        "sigma_ratio_min": float(r.min()), "sigma_ratio_max": float(r.max())}
    bank = P / "MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware"
    g = toys.interaction_groups(bank)
    out["bank_interaction_bands"] = len(g)
    out["bank_groups_equal_scorer_groups"] = g == fs.declared_groups()
    out["bank_flux_ids_0_99"] = toys.flux_ids(bank) == list(range(100))
    p = toys.flux_probabilities(P / "MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/"
                                    "sorted_NuEConstraint_FHC_RHC_IMD.txt")
    out["flux_probabilities"] = {"sum": float(p.sum()), "n_eff": float(1.0 / np.sum(p ** 2)), "max": float(p.max())}
    prep = P / "fd-f1-20261027/f1b3/prep"
    out["truth_ratio_sha256"] = {t: toys.truth_ratio(t, prep)[1] for t in ("genie_v3_g18", "genie_v3_ar23")}
    out["numpy"] = np.__version__
    out["python"] = sys.version.split()[0]
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
