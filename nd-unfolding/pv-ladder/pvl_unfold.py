#!/usr/bin/env python3
"""PV ladder: one data (or closure) unfold of one rung through the s5 stack, with the prior reweighted by a
pvl-ratio/1 file and the classifier features optionally restricted (DECLARATION.md §2).

    pvl_unfold.py --rung L-EW --arm e --features eavail,W --ratio ratios/L-EW/nuwro.json --out X.npz \
        --npz ... --bkg ... --expect-npz-sha256 ... --expect-bkg-sha256 ...

Arms (docs/analysis-note/sec_method.tex:231-257):
  e  s5e candidate R: deterministic LightGBM 100/8, negative-weight background with the Stay-Positive refinement at
     400/31 (s5e_candidate.install("R"); the measured side is s5e_trace.measured_side, as s5p_numerics.unfold_one);
  c  deterministic LightGBM 100/8 with the npz's purity weights (s5n_pseudo --bkg-mode purity --data).
With --features all and no --ratio this is the path of RE-1's P3/P4/P5 (arm e) and P3c/P4c/P5c (arm c).

--features restricts what every classifier sees (the OmniFold steps, and for arm e the refinement) to the named
columns of the MC truth, MC reco, data and template; the unfolded per-event weights are still histogrammed on the
npz's full grid and the cross section is extracted there, so only the conditioning changes.

--closure replaces the data by the noise-free signal-only closure at the ratio (pvl_lib.closure_inputs) and
unfolds it with the NOMINAL prior; the product also carries the truth reference xtrue_flat.

MEASURES: one unfold. CANNOT AUTHORIZE: any verdict (pvl_analyze.py applies the declared rules).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
for _p in (str(_HERE), str(_ND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import pvl_lib as L  # noqa: E402
import omnifold_nn_core as onc  # noqa: E402
import s5c_unfold  # noqa: E402
from xsec_nd import extract_cross_section_nd  # noqa: E402

EXP_KEYS = ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco",
            "denom_nd", "flux", "data_pot", "n_nucleons", "edges")


def unfold(d: dict, cols, seed: int, threads: int, iters: int) -> tuple[np.ndarray, list]:
    """s5c_unfold.unfold ("deterministic"), with the classifiers given only the columns ``cols`` (None = all). With
    cols None the arrays are passed unchanged, so the path is s5c_unfold.unfold's exactly."""
    record: list = []
    extra = s5c_unfold.config_params("deterministic", threads)

    def take(a):
        return a if cols is None else np.ascontiguousarray(a[:, cols])

    with s5c_unfold.estimator_config(extra, record):
        _, wpush = onc.omnifold_loop(
            take(d["MCgen"]), take(d["MCreco"]), d["measured"], d["pass_reco"], d["pass_truth"],
            np.ones(len(d["measured"]), bool), iters, kind="lgbm",
            MCgen_weights=d["w_truth"], MCreco_weights=d["w_reco"],
            measured_weights=d["measured_weights"], seed=seed, verbose=False)
    if len(record) != 1:
        raise RuntimeError(f"expected one estimator-factory call, saw {len(record)}")
    for params in record[0]:
        for key, value in extra.items():
            if params.get(key) != value:
                raise RuntimeError(f"estimator parameter {key}={params.get(key)!r}, wanted {value!r}")
    m = d["pass_truth"]
    edges = d["edges"]
    samp = np.column_stack([d["MCgen"][m, i] for i in range(d["MCgen"].shape[1])])
    unf, _ = np.histogramdd(samp, bins=edges, weights=wpush * d["w_truth"][m])
    ofin, _ = np.histogramdd(samp, bins=edges, weights=d["w_truth"][m])
    dn = d["denom_nd"]
    comp = np.zeros_like(ofin)
    nz = dn > 0
    comp[nz] = ofin[nz] / dn[nz]
    xs, _ = extract_cross_section_nd(unf, comp, d["flux"], float(d["data_pot"]), float(d["n_nucleons"]), edges)
    return xs, record[0]


def measured_negweight(exp: dict, cols, seed: int, threads: int):
    """s5e_trace.measured_side on the restricted columns of the observed and template rows."""
    import s5e_trace

    e = dict(exp)
    if cols is not None:
        e["obs"] = np.ascontiguousarray(exp["obs"][:, cols])
        e["tmpl"] = np.ascontiguousarray(exp["tmpl"][:, cols])
    return s5e_trace.measured_side(e, seed, threads, None, np.float32)


def measured_purity(exp: dict, cols) -> np.ndarray:
    """Arm (c)'s measured side: the npz's data coordinates, restricted to ``cols`` (None = unchanged)."""
    return exp["measured"] if cols is None else np.ascontiguousarray(exp["measured"][:, cols])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--rung", required=True, choices=sorted(L.RUNGS))
    ap.add_argument("--arm", required=True, choices=("e", "c"))
    ap.add_argument("--features", required=True, help="'all' or a comma list of the npz's axis names")
    ap.add_argument("--ratio", type=Path, required=True, help="pvl-ratio/1 file (tune_v1.json = the nominal prior)")
    ap.add_argument("--expect-ratio-sha256", required=True)
    ap.add_argument("--closure", action="store_true")
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--bkg", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--expect-bkg-sha256", required=True)
    ap.add_argument("--estimator-seed", type=int, default=42)
    ap.add_argument("--threads", type=int, default=32)
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    if a.closure and a.arm != "e":
        print("--closure is declared for arm e only", file=sys.stderr)
        return 2
    t0 = time.time()
    npz_sha, bkg_sha = L.sha256_path(a.npz), L.sha256_path(a.bkg)
    if npz_sha != a.expect_npz_sha256 or bkg_sha != a.expect_bkg_sha256:
        print(f"input digests {npz_sha} / {bkg_sha} differ from the expected ones", file=sys.stderr)
        return 4
    z = np.load(a.npz, allow_pickle=True)
    names = L.npz_axes(z)
    npz_axes, _, rung_features = L.RUNGS[a.rung]
    if names != npz_axes:
        print(f"the npz's axes {names} are not {a.rung}'s {npz_axes}", file=sys.stderr)
        return 4
    features = names if a.features == "all" else tuple(a.features.split(","))
    if features not in (names, rung_features):
        print(f"--features {features} is neither all of {names} nor {a.rung}'s declared {rung_features}",
              file=sys.stderr)
        return 2
    cols = None if features == names else [names.index(f) for f in features]
    inputs = s5c_unfold.load_inputs(a.npz)
    bz = np.load(a.bkg, allow_pickle=True)
    if json.loads(str(bz["meta"]))["npz_sha256"] != npz_sha:
        print("refusing: background dump was made against a different npz", file=sys.stderr)
        return 4
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}

    guard = None
    ratio_sha = L.sha256_path(a.ratio)
    if ratio_sha != a.expect_ratio_sha256:
        print(f"ratio sha256 {ratio_sha} differs from the expected one", file=sys.stderr)
        return 4
    ratio = L.load_json(a.ratio)
    if tuple(ratio["axes"]) != L.RUNGS[a.rung][1]:
        print(f"the ratio's axes {ratio['axes']} are not {a.rung}'s reweight axes", file=sys.stderr)
        return 4
    r = L.row_weight(inputs["MCgen"], names, ratio, inputs["pass_truth"])

    import s5e_candidate
    import s5n_pseudo

    if a.arm == "e":
        s5e_candidate.install("R")
    x_true = None
    if a.closure:
        exp, x_true = L.closure_inputs(inputs, r)
        info = {"closure": True, "n_pseudo_rows": int(exp["obs"].shape[0])}
    else:
        ui, guard = L.prior_inputs(inputs, r)
        if a.arm == "e":
            exp = s5n_pseudo.build_data(ui, bkg)
            info = {"n_observed": int(exp["obs"].shape[0]), "n_template": int(exp["tmpl"].shape[0])}
        else:
            exp = dict(ui)
            info = {"measured_weight_sum": float(inputs["measured_weights"].sum())}
    t1 = time.time()
    if a.arm == "e":
        feat, w_ref, ev = measured_negweight(exp, cols, a.estimator_seed, a.threads)
        unf_in = {k: exp[k] for k in EXP_KEYS}
        unf_in["measured"], unf_in["measured_weights"] = feat, w_ref
    else:
        unf_in = dict(exp)
        unf_in["measured"] = measured_purity(exp, cols)
        ev = {"ran": False, "reason": "purity baseline"}
    xs, params = unfold(unf_in, cols, a.estimator_seed, a.threads, a.iters)
    import lightgbm
    import s5e_trace

    code = {**s5n_pseudo.code_digests(), "pvl_unfold.py": L.sha256_path(__file__),
            "pvl_lib.py": L.sha256_path(L.__file__), "s5e_trace.py": L.sha256_path(Path(s5e_trace.__file__)),
            "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "lightgbm": lightgbm.__version__}}
    meta = {"schema": "pvl-unfold/1", "rung": a.rung, "arm": a.arm, "features": list(features),
            "closure": a.closure, "ratio_file": str(a.ratio), "ratio_sha256": ratio_sha,
            "r_in_grid_weighted_mean": float(np.average(
                r[inputs["pass_truth"]], weights=np.asarray(inputs["w_truth"], float)[inputs["pass_truth"]])),
            "completeness_guard": guard, "estimator_seed": a.estimator_seed, "threads": a.threads,
            "iters": a.iters, "input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha, "experiment": info,
            "refinement": ev, "estimator_params": params, "code_sha256": code,
            "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_step": os.environ.get("SLURM_STEP_ID"),
            "seconds_load": round(t1 - t0, 3), "seconds_unfold": round(time.time() - t1, 3)}
    arrays = {"xsec_flat": xs.ravel(order="C"), "shape": np.array(xs.shape)}
    if x_true is not None:
        arrays["xtrue_flat"] = x_true.ravel(order="C")
    rc = s5n_pseudo.write_product(a.out, arrays, meta)
    print(json.dumps({"out": a.out.name, "rc": rc, "seconds_unfold": meta["seconds_unfold"],
                      "completeness_guard": guard, "refined_over_signed": ev.get("refined_over_signed")}))
    return rc


if __name__ == "__main__":
    sys.exit(main())
