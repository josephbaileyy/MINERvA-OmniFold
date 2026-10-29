#!/usr/bin/env python3
"""The cheap tier's 3b (state/measurement-paper/5d-community-20261024/FD-CT-3B-DECLARATION.md): one response-mismatch
closure of configuration (e), noise-free and signal-only. The pseudo-data are a SHIFTED lateral dump's own signal reco
rows at the nominal truth; the unfolding uses the ZERO dump's MC response. With the zero dump as both, it is
pv-ladder's noise-free closure at the nominal prior (pvl_lib.closure_inputs with r = 1).

    fd_ct_closure.py --variant proton_p1 --response-npz lat_zero.npz --expect-response-sha256 ... \
        --pseudo-npz lat_proton_p1.npz --expect-pseudo-sha256 ... --out closure_proton_p1.npz

* The two dumps must describe the same MC events at the same truth: MCgen, w_truth, pass_truth, w_reco, pass_reco,
  denom_nd, flux, data_pot, n_nucleons and the edges are required bitwise equal, so only the reconstructed
  coordinates MCreco differ (a lateral dump's shifted response). Otherwise it refuses (exit 4), and writes nothing.
* The pseudo-data are the pseudo dump's reco- and truth-passing rows inside the reco window at w_reco, with no
  background and no template, as pvl_lib.closure_inputs builds them; so the Stay-Positive refinement does not run.
* The truth reference xtrue_flat is the zero dump's, through its own completeness.
* The unfold is pv-ladder's arm (e) (pvl_unfold.unfold and measured_negweight, s5e candidate R installed), with all
  the npz's columns.

MEASURES: one unfold. CANNOT AUTHORIZE: any verdict; the readout (fd_ct_readers.py mismatch) states no threshold.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
for _p in (str(_ND / "pv-ladder"), str(_ND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import pvl_lib as L  # noqa: E402
import pvl_unfold as PU  # noqa: E402
import s5c_unfold  # noqa: E402

AXES = ("pt", "pz", "eavail", "q3", "W")
SAME = ("MCgen", "w_truth", "pass_truth", "w_reco", "pass_reco", "denom_nd", "flux", "data_pot", "n_nucleons")


def truth_side_problems(resp: dict, pseudo: dict) -> list[str]:
    """Every key of SAME, and the edges, that is not bitwise equal (shape, dtype and bytes) between the two dumps."""
    bad = []
    for k in SAME:
        a, b = np.asarray(resp[k]), np.asarray(pseudo[k])
        if a.shape != b.shape or a.dtype != b.dtype or not np.array_equal(a, b):
            bad.append(k)
    if len(resp["edges"]) != len(pseudo["edges"]) or any(
            not np.array_equal(x, y) for x, y in zip(resp["edges"], pseudo["edges"])):
        bad.append("edges")
    if np.asarray(resp["MCreco"]).shape != np.asarray(pseudo["MCreco"]).shape:
        bad.append("MCreco shape")
    return bad


def mismatch_inputs(resp: dict, pseudo: dict):
    """The experiment: the zero dump's MC response with the pseudo dump's signal reco rows as the observed data (the
    rows pvl_lib.closure_inputs keeps: reco- and truth-passing, inside the reco window, w_reco > 0, no fakes), no
    template; and the zero dump's truth reference. With pseudo = resp this is pvl_lib.closure_inputs at r = 1."""
    ones = np.ones(np.asarray(resp["MCgen"]).shape[0])
    exp, x_true = L.closure_inputs(resp, ones)
    edges = resp["edges"]
    reco = np.asarray(pseudo["MCreco"])
    keep = np.asarray(pseudo["pass_reco"], bool) & np.asarray(pseudo["pass_truth"], bool)
    for k, e in enumerate(edges):
        keep &= (reco[:, k] >= e[0]) & (reco[:, k] < e[-1])
    w = np.asarray(pseudo["w_reco"], float)
    keep &= w > 0
    exp["obs"], exp["obs_counts"] = reco[keep], w[keep]
    return exp, x_true


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--variant", required=True)
    ap.add_argument("--response-npz", type=Path, required=True)
    ap.add_argument("--expect-response-sha256", required=True)
    ap.add_argument("--pseudo-npz", type=Path, required=True)
    ap.add_argument("--expect-pseudo-sha256", required=True)
    ap.add_argument("--estimator-seed", type=int, default=42)
    ap.add_argument("--threads", type=int, default=32)
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    t0 = time.time()
    shas = {"response": L.sha256_path(a.response_npz), "pseudo": L.sha256_path(a.pseudo_npz)}
    if (shas["response"], shas["pseudo"]) != (a.expect_response_sha256, a.expect_pseudo_sha256):
        print(f"input digests {shas} differ from the expected ones", file=sys.stderr)
        return 4
    for p in (a.response_npz, a.pseudo_npz):
        names = L.npz_axes(np.load(p, allow_pickle=True))
        if names != AXES:
            print(f"{p.name}: axes {names} are not {AXES}", file=sys.stderr)
            return 4
    resp = s5c_unfold.load_inputs(a.response_npz)
    pseudo = resp if a.pseudo_npz.resolve() == a.response_npz.resolve() else s5c_unfold.load_inputs(a.pseudo_npz)
    bad = truth_side_problems(resp, pseudo)
    if bad:
        print(f"refusing: the two dumps differ in {bad}; a mismatch closure needs the same events at the same truth",
              file=sys.stderr)
        return 4
    reco_identical = bool(np.array_equal(resp["MCreco"], pseudo["MCreco"]))
    import s5e_candidate
    import s5n_pseudo

    s5e_candidate.install("R")
    exp, x_true = mismatch_inputs(resp, pseudo)
    info = {"closure": True, "n_pseudo_rows": int(exp["obs"].shape[0]), "pseudo_reco_identical": reco_identical}
    t1 = time.time()
    feat, w_ref, ev = PU.measured_negweight(exp, None, a.estimator_seed, a.threads)
    unf_in = {k: exp[k] for k in PU.EXP_KEYS}
    unf_in["measured"], unf_in["measured_weights"] = feat, w_ref
    xs, params = PU.unfold(unf_in, None, a.estimator_seed, a.threads, a.iters)
    import lightgbm
    import s5e_trace

    code = {**s5n_pseudo.code_digests(), "fd_ct_closure.py": L.sha256_path(__file__),
            "pvl_unfold.py": L.sha256_path(PU.__file__), "pvl_lib.py": L.sha256_path(L.__file__),
            "s5e_trace.py": L.sha256_path(Path(s5e_trace.__file__)),
            "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "lightgbm": lightgbm.__version__}}
    meta = {"schema": "fd-ct-closure/1", "variant": a.variant, "construction": "mismatch-closure", "truth": "nominal",
            "arm": "e", "features": list(AXES), "response_npz_sha256": shas["response"],
            "pseudo_npz_sha256": shas["pseudo"], "estimator_seed": a.estimator_seed, "threads": a.threads,
            "iters": a.iters, "experiment": info, "refinement": ev, "estimator_params": params, "code_sha256": code,
            "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_step": os.environ.get("SLURM_STEP_ID"),
            "seconds_load": round(t1 - t0, 3), "seconds_unfold": round(time.time() - t1, 3)}
    arrays = {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": x_true.ravel(order="C"), "shape": np.array(xs.shape)}
    rc = s5n_pseudo.write_product(a.out, arrays, meta)
    print(json.dumps({"out": a.out.name, "rc": rc, "seconds_unfold": meta["seconds_unfold"],
                      "n_pseudo_rows": info["n_pseudo_rows"], "refinement_ran": ev.get("ran")}))
    return rc


if __name__ == "__main__":
    sys.exit(main())
