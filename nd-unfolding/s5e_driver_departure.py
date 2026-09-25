#!/usr/bin/env python3
"""s5e diagnosis D1/D2(c): the UNMODIFIED 5D driver on a noise-free truth departure.

    s5e_driver_departure.py --truth eavail_shape --amplitude 1 --eavail-ratio R.json \
        --npz of_inputs_5d.npz --expect-npz-sha256 S --s5c-contract C --out D.npz \
        -- nd-unfolding/unfold_nd_omnifold_unbinned.py --closure --use-weights --axes eavail,q3,W \
           --iters 5 --estimator lgbm --seed 42 --omnifile ... --out X.root

The driver runs as itself (``runpy``), with:

* the F2 configuration merged into its OmniFold backend exactly as ``s5c_with_estimator.install``
  does it for every other driver arm (evidence recorded and verified the same way);
* in its own ``--closure`` mode (pseudo-data = the MC's reco-passing, truth-passing rows at w_reco;
  completeness 1), the declared truth deformation ``r`` multiplied onto the pseudo-data weights by a
  wrapper around the backend call. The wrapper first PROVES row alignment (measured equals
  ``MCreco[pass_reco & pass_truth]`` and measured weights equal ``MCreco_weights`` on those rows,
  bitwise) and computes ``r`` on the truth-passing rows with the same functions the npz path uses
  (``s5n_pseudo.truth_weight``), so both paths deform by one definition;
* the driver's own cross-section extraction captured, so the deformed truth is extracted with the
  driver's completeness, flux, exposure and edges.

It also compares the driver's arrays with the npz inputs (D2(c)): row counts, pass masks, weights and
the per-axis maximum of |driver float64 - npz float32| on the truth-passing rows, and the edges.

MEASURES: the driver path's response to a declared noise-free departure, and input parity with the npz
path. CANNOT AUTHORIZE: a statement about pseudo-experiments with noise, or any driver product for
publication.
"""
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s5c_unfold  # noqa: E402
import s5c_with_estimator  # noqa: E402  (also puts unbinned_unfolding/python on sys.path)
import s5n_pseudo  # noqa: E402
import xsec_nd  # noqa: E402


def input_parity(args, kwargs, npz: dict) -> dict:
    """The driver's backend arrays (truth-passing rows) against the npz inputs."""
    MCgen, MCreco, _, pass_reco, pass_truth = (np.asarray(x) for x in args[:5])
    pt = pass_truth.astype(bool)
    out = {"driver_rows": int(pt.size), "driver_pass_truth": int(pt.sum()), "npz_rows": int(npz["MCgen"].shape[0])}
    if pt.sum() != npz["MCgen"].shape[0]:
        out["aligned"] = False
        return out
    g, r = MCgen[pt], MCreco[pt]
    out["aligned"] = bool(np.array_equal(g.astype(np.float32), npz["MCgen"]))
    out["reco_float32_equal"] = bool(np.array_equal(r.astype(np.float32), npz["MCreco"]))
    out["max_abs_gen_f64_minus_npz"] = [float(np.max(np.abs(g[:, k] - npz["MCgen"][:, k].astype(float))))
                                        for k in range(g.shape[1])]
    out["max_abs_reco_f64_minus_npz"] = [float(np.max(np.abs(r[:, k] - npz["MCreco"][:, k].astype(float))))
                                         for k in range(r.shape[1])]
    out["pass_reco_equal"] = bool(np.array_equal(pass_reco[pt], npz["pass_reco"]))
    out["w_truth_equal"] = bool(np.array_equal(np.asarray(kwargs["MCgen_weights"])[pt], npz["w_truth"]))
    out["w_reco_equal"] = bool(np.array_equal(np.asarray(kwargs["MCreco_weights"])[pt], npz["w_reco"]))
    out["w_truth_sum"] = [float(np.asarray(kwargs["MCgen_weights"])[pt].sum()), float(npz["w_truth"].sum())]
    out["w_reco_sum_pass_reco"] = [float(np.asarray(kwargs["MCreco_weights"])[pt][pass_reco[pt]].sum()),
                                   float(npz["w_reco"][npz["pass_reco"]].sum())]
    return out


def install_departure(ohf, truth: str, amplitude: float, ratio, edges: list, npz: dict, state: dict) -> None:
    inner = ohf.omnifold

    def inject(*args, **kwargs):
        MCgen, MCreco, measured, pass_reco, pass_truth = (np.asarray(x) for x in args[:5])
        cm = pass_reco.astype(bool) & pass_truth.astype(bool)
        mw = np.asarray(kwargs["measured_weights"], float)
        if not (np.array_equal(measured, MCreco[cm]) and np.array_equal(mw, np.asarray(kwargs["MCreco_weights"])[cm])):
            raise RuntimeError("closure rows are not MCreco[pass_reco & pass_truth] at w_reco: refusing to deform")
        pt = pass_truth.astype(bool)
        wt = np.asarray(kwargs["MCgen_weights"], float)
        r = np.ones(pt.size)
        r[pt] = s5n_pseudo.truth_weight(truth, {"MCgen": MCgen[pt], "edges": edges, "w_truth": wt[pt]},
                                        amplitude, ratio)
        kwargs["measured_weights"] = mw * r[cm]
        state["parity"] = input_parity(args, kwargs, npz)
        state["r"] = {"min": float(r[pt].min()), "max": float(r[pt].max()),
                      "in_grid_weighted_mean": float((wt[pt] * r[pt]).sum() / wt[pt].sum())}
        out = inner(*args, **kwargs)
        state["truth_cols"] = MCgen[pt]
        state["truth_w"] = wt[pt] * r[pt]
        state["step2"] = np.asarray(out[1])
        state["called"] = state.get("called", 0) + 1
        return out

    ohf.omnifold = inject


def install_capture(state: dict) -> None:
    original = xsec_nd.extract_cross_section_nd

    def capture(counts, completeness, flux, data_pot, n_nucleons, axes_edges, flux_axis=0):
        out = original(counts, completeness, flux, data_pot, n_nucleons, axes_edges, flux_axis)
        if "step2" in state and "extraction" not in state:  # the driver's first call after the unfold
            state["extraction"] = (np.array(completeness, float), np.asarray(flux, float), float(data_pot),
                                   float(n_nucleons), [np.asarray(e, float) for e in axes_edges], out[0].copy())
        return out

    xsec_nd.extract_cross_section_nd = capture
    state["original_extraction"] = original


def main() -> int:
    if "--" not in sys.argv:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    cut = sys.argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth", choices=s5n_pseudo.TRUTHS, required=True)
    ap.add_argument("--amplitude", type=float, default=0.0)
    ap.add_argument("--eavail-ratio", type=Path, default=None)
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--s5c-contract", type=Path, required=True)
    ap.add_argument("--threads", type=int, default=32)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(sys.argv[1:cut])
    target = sys.argv[cut + 1:]
    if "--closure" not in target:
        print("the departure is injected in the driver's --closure mode only", file=sys.stderr)
        return 2
    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    sha = s5n_pseudo.sha256_path(a.npz)
    if sha != a.expect_npz_sha256:
        print(f"npz sha256 {sha} differs from the expected one", file=sys.stderr)
        return 4
    npz = s5c_unfold.load_inputs(a.npz)
    edges = npz["edges"]
    ratio = json.loads(a.eavail_ratio.read_text()) if a.eavail_ratio else None
    extra = s5c_unfold.config_params("deterministic", a.threads)
    record: list = []
    s5c_with_estimator.install(extra, record, None, target)
    from omnifold import OmniFold_helper_functions as ohf

    state: dict = {}
    install_departure(ohf, a.truth, a.amplitude, ratio, edges, npz, state)
    install_capture(state)
    sys.argv = target
    code = 0
    try:
        runpy.run_path(target[0], run_name="__main__")
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    problems = s5c_with_estimator.verify(extra, record, target)
    if state.get("called") != 1 or "extraction" not in state:
        problems.append(f"backend calls {state.get('called')}, extraction captured {'extraction' in state}")
    if code != 0 or problems:
        print(json.dumps({"target_exit": code, "problems": problems}), file=sys.stderr)
        return code or 7
    comp, flux, pot, nn, dedges, xs = state["extraction"]
    if not all(np.allclose(x, y, rtol=0, atol=0) for x, y in zip(dedges, edges)):
        problems.append("driver edges differ from the npz edges")
    unf_true, _ = np.histogramdd(state["truth_cols"], bins=dedges, weights=state["truth_w"])
    x_true, _ = state["original_extraction"](unf_true, comp, flux, pot, nn, dedges)
    import s5c_coverage

    U, names = s5c_coverage.reported_functionals(json.loads(a.s5c_contract.read_text()))
    meta = {"schema": "s5e-driver-departure/1", "truth": a.truth, "amplitude": a.amplitude,
            "eavail_ratio_sha256": s5n_pseudo.sha256_path(a.eavail_ratio) if a.eavail_ratio else None,
            "target": target, "estimator_evidence": record, "problems": problems, "r": state["r"],
            "input_parity": state["parity"], "functional_names": names, "input_npz_sha256": sha,
            "code_sha256": {"s5e_driver_departure.py": s5n_pseudo.sha256_path(Path(__file__).resolve()),
                            "unfold_nd_omnifold_unbinned.py": s5n_pseudo.sha256_path(_ND / "unfold_nd_omnifold_unbinned.py")}}
    arrays = {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": x_true.ravel(order="C"),
              "fn_unf": U @ xs.ravel(order="C"), "fn_true": U @ x_true.ravel(order="C")}
    rc = s5n_pseudo.write_product(a.out, arrays, meta)
    print(json.dumps({"out": a.out.name, "rc": rc, "problems": problems, "parity": state["parity"]}, default=str))
    return 7 if problems else rc


if __name__ == "__main__":
    sys.exit(main())
