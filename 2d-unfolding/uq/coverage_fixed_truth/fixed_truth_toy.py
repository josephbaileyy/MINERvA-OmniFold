#!/usr/bin/env python3
"""One fixed-truth 2D coverage toy (or the no-fluctuation equivalence run).

Pre-registration: ``docs/orchestration/PREREG-20261005-2d-fixed-truth-coverage.md``.

This driver reuses the production 2D driver's helpers unchanged
(``unfold_2d_omnifold_unbinned.py`` is imported, never edited, because its sha256 is
bound by other receipts) and repeats its ``--closure --use-weights`` path
(``main()``, purity background mode, which in closure uses ``w_reco`` as the
measured weights). Two modes:

``--toy T``
    Pseudo-data ``k_i ~ Poisson(w_reco_i)`` on the closure events, the production
    MC bootstrap stream ``b_i ~ Poisson(1)`` on ``w_truth``/``w_reco``, and the
    unfluctuated truth written to ``hTruthFixedXSec2D``.
``--no-fluctuation``
    Pseudo-data weights ``w_reco`` on every closure event and no MC bootstrap. With
    the same estimator and ``--seed`` this must reproduce
    ``unfold_2d_omnifold_unbinned.py --closure --use-weights`` (``hXSec2D`` and
    ``hTruthXSec2D``); it is the check that this file repeats the production path.

Provenance (``n2/execution.py``). The toy design, the driver's helpers and the OmniFold helper are
executed from hashed bytes of the checkout this file is in, before any input is read; a module of
the same name imported from elsewhere is refused (exit 3). The output records every executed file's
path, sha256 and git blob, HEAD, the guard's state, the effective estimator arguments, the
environment and the inputs (``producerProvenance``, plus the driver's ``runConfig``,
``omnifoldHelperFile`` and ``omnifoldHelperSha256``). ``--expect`` refuses on any contradiction;
``--require-provenance`` also refuses on anything unknown and reserves ``--out`` exclusively
(an existing one is refused). Without it,
an existing ``--out`` is recreated as before, for the resume-guarded launchers.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

_SELF_BYTES = Path(__file__).read_bytes()

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
DRIVER_DIR = HERE.parents[1]
REPO = HERE.parents[2]
# The OmniFold backend of THIS checkout: the production driver's main() inserts the same relative
# path of the canonical checkout, so on that checkout the two are equal. Deriving it is the OI-136
# repair; a hardcoded root here executed the canonical checkout's helper from every tree.
OMNIFOLD_PY = REPO / "unbinned_unfolding" / "python"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(DRIVER_DIR))

from n2 import execution as gx  # noqa: E402

# Loaded by load_code() from hashed bytes, before any input is read.
toy_design = u2d = ROOT = ohf = None
CODE = (("toy_design", HERE / "toy_design.py"),
        ("unfold_2d_omnifold_unbinned", DRIVER_DIR / "unfold_2d_omnifold_unbinned.py"),
        ("omnifold", OMNIFOLD_PY / "omnifold.py"))
INPUTS = ("omnifile", "mcfile")


def load_code(expectations):
    """Execute the toy's repository code from verified bytes; return the executed-file records."""
    global toy_design, u2d, ROOT, ohf
    records = [gx.file_record(__file__, _SELF_BYTES, REPO),
               gx.bootstrap_record(sys.modules["n2"], REPO), gx.bootstrap_record(gx, REPO)]
    loaded = {}
    for name, path in CODE:
        rel = path.resolve().relative_to(REPO).as_posix()
        loaded[name], rec = gx.load_verified(name, path, REPO, expectations["modules"].get(rel))
        records.append(rec)
    toy_design, u2d = loaded["toy_design"], loaded["unfold_2d_omnifold_unbinned"]
    ROOT = u2d.ROOT
    if str(OMNIFOLD_PY) not in sys.path:
        sys.path.insert(0, str(OMNIFOLD_PY))
    ohf = loaded["omnifold"].OmniFold_helper_functions
    return records


def fill_th2d(name, title, pt, pz, w):
    h = u2d.make_th2d(name, title, u2d.PT_EDGES, u2d.PZ_EDGES)
    for x, y, v in zip(pt, pz, w):
        h.Fill(float(x), float(y), float(v))
    return h


def unit_completeness():
    h = u2d.make_th2d("hOFCompleteness2D", "Completeness = 1 (closure)",
                      u2d.PT_EDGES, u2d.PZ_EDGES)
    for ix in range(1, h.GetNbinsX() + 1):
        for iy in range(1, h.GetNbinsY() + 1):
            h.SetBinContent(ix, iy, 1.0)
    return h


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--toy", type=int, help="toy index (seeds from toy_design.toy_seeds)")
    mode.add_argument("--no-fluctuation", action="store_true",
                      help="deterministic closure, for the equivalence check")
    ap.add_argument("--omnifile", required=True)
    ap.add_argument("--mcfile", required=True, help="flux MC file (as the production driver)")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--estimator", default="lgbm", choices=["exact", "hist", "xgb", "lgbm"])
    ap.add_argument("--seed", type=int, default=1, help="GBDT seed, as the production replicas")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--no-mc-bootstrap", action="store_true",
                    help="KNOWN_ISSUES 85 arms T and B: keep the MC unresampled (b = 1)")
    ap.add_argument("--data-bootstrap", type=int, default=None, metavar="S",
                    help="KNOWN_ISSUES 85 arm B: Poisson(k) per event on toy --toy's pseudo-data, "
                         "seed toy_design.bootstrap_seed(S); requires --no-mc-bootstrap")
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect", metavar="JSON",
                    help="expected commit, module digests (by repo-relative path) and input "
                         "digests (keys omnifile, mcfile); any mismatch refuses before output")
    ap.add_argument("--require-provenance", action="store_true",
                    help="refuse unless run under mnv_guarded_run.py on this checkout, with every "
                         "executed file at HEAD, every digest stated by --expect, and --out new")
    ap.add_argument("--hash-inputs", action="store_true",
                    help="record the sha256 of the input files even when --expect states none")
    args = ap.parse_args()
    if args.no_fluctuation and (args.no_mc_bootstrap or args.data_bootstrap is not None):
        ap.error("--no-mc-bootstrap and --data-bootstrap need --toy")
    if args.data_bootstrap is not None and not args.no_mc_bootstrap:
        ap.error("--data-bootstrap is a data-only bootstrap: pass --no-mc-bootstrap")

    try:
        expectations = gx.load_expectations(args.expect)
        identity = gx.finalize(REPO, load_code(expectations), expectations,
                               args.require_provenance)
        if args.require_provenance:
            missing = [k for k in INPUTS if k not in expectations["inputs"]]
            if missing:
                raise gx.ProvenanceRefusal(f"strict provenance needs input digests for {missing}")
        inputs = {k: gx.input_record(getattr(args, k), expectations["inputs"].get(k),
                                     args.hash_inputs) for k in INPUTS}
        if args.require_provenance:
            gx.reserve_output(args.out)
    except gx.ProvenanceRefusal as exc:
        print(f"[REFUSED] {exc}", file=sys.stderr)
        sys.exit(gx.REFUSAL_EXIT)
    helper = next(r for r in identity["executed"] if r["relpath"].endswith("python/omnifold.py"))
    print(f"[INFO] omnifold helper {helper['path']} sha256 {helper['sha256']}")

    t0 = time.time()
    pt_edges, pz_edges = u2d.PT_EDGES, u2d.PZ_EDGES
    pt_lo, pt_hi, pz_lo, pz_hi = pt_edges[0], pt_edges[-1], pz_edges[0], pz_edges[-1]

    f_in = ROOT.TFile.Open(args.omnifile, "READ")
    if not f_in or f_in.IsZombie():
        raise RuntimeError(f"Could not open {args.omnifile}")
    t_sig = f_in.Get("mc_signal_reco")
    if not t_sig:
        raise RuntimeError("Missing mc_signal_reco")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f_in)
    n_nucleons = u2d.TRACKER_FIDUCIAL_N_NUCLEONS
    flux_bins, h_flux = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_edges)
    print(f"[INFO] POT data={data_pot:.6g} mc={mc_pot:.6g} scale={pot_scale:.6g}")

    sig = u2d.collect_signal_arrays_2d(t_sig, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                                       use_weights=True, verbose=True)
    f_in.Close()
    n_fake = int((sig["pass_reco"] & ~sig["pass_truth"]).sum())
    closure = sig["pass_reco"] & sig["pass_truth"]
    reco_pt_c = sig["reco_pt"][closure]
    reco_pz_c = sig["reco_pz"][closure]
    w_reco_c = sig["w_reco"][closure].copy()

    # The fixed truth: unfluctuated MC truth marginal, built before any draw.
    pt_in = sig["truth_pt"][sig["pass_truth"]]
    pz_in = sig["truth_pz"][sig["pass_truth"]]
    h_truth_fixed = fill_th2d("hTruthFixed2D", "Unfluctuated MC truth (fixed truth)",
                              pt_in, pz_in, sig["w_truth"][sig["pass_truth"]])
    h_comp = unit_completeness()
    h_truth_fixed_xs = u2d.extract_cross_section_2d(
        h_truth_fixed, h_comp, flux_bins, data_pot, n_nucleons, pt_edges, pz_edges)
    h_truth_fixed_xs.SetName("hTruthFixedXSec2D")
    h_truth_fixed_xs.SetTitle("Fixed truth cross section (unfluctuated MC truth)")

    meta = {"mode": "no-fluctuation" if args.no_fluctuation else "toy",
            "omnifile": os.path.abspath(args.omnifile), "mcfile": os.path.abspath(args.mcfile),
            "estimator": args.estimator, "gbdt_seed": args.seed, "iters": args.iters,
            "data_pot": data_pot, "mc_pot": mc_pot, "pot_scale": pot_scale,
            "n_signal": int(sig["w_truth"].size), "n_pass_truth": int(sig["pass_truth"].sum()),
            "n_closure": int(closure.sum()), "n_fake": n_fake,
            "sum_w_reco_closure": float(w_reco_c.sum()),
            "max_w_reco_closure": float(w_reco_c.max()),
            "sum_w_truth_pass_truth": float(sig["w_truth"][sig["pass_truth"]].sum())}

    if args.no_fluctuation:
        meas_pt, meas_pz, meas_w = reco_pt_c.copy(), reco_pz_c.copy(), w_reco_c
    else:
        data_seed, mc_seed = toy_design.toy_seeds(args.toy)
        counts = toy_design.draw_pseudo_data_counts(w_reco_c, data_seed)
        meta.update({"toy": int(args.toy), "data_seed": data_seed, "sum_k_toy": float(counts.sum())})
        if args.data_bootstrap is not None:
            boot_seed = toy_design.bootstrap_seed(args.data_bootstrap)
            counts = toy_design.draw_data_bootstrap(counts, boot_seed)
            meta.update({"data_bootstrap": int(args.data_bootstrap), "boot_seed": boot_seed})
        if args.no_mc_bootstrap:
            meta.update({"mc_seed": None, "mc_bootstrap": False})
        else:
            b = toy_design.draw_mc_bootstrap(sig["w_truth"].size, mc_seed)
            sig["w_truth"] = sig["w_truth"] * b
            sig["w_reco"] = sig["w_reco"] * b
            meta.update({"mc_seed": mc_seed, "mc_bootstrap": True,
                         "sum_b": float(b.sum()), "n_b": int(b.size)})
        meas_pt, meas_pz, meas_w = toy_design.compress_pseudo_data(reco_pt_c, reco_pz_c, counts)
        meta.update({"sum_k": float(counts.sum()), "n_pseudo_rows": int(meas_w.size),
                     "max_k": float(counts.max())})
    print("[INFO] " + json.dumps(meta))

    h_pseudo = fill_th2d("hPseudoReco2D", "Pseudo-data (reco)", meas_pt, meas_pz, meas_w)

    c1 = {"random_state": int(args.seed)}
    c2 = {"random_state": int(args.seed) + 1}
    rg = {"random_state": int(args.seed) + 2}
    step1_w, step2_w = ohf.omnifold(
        np.column_stack([sig["truth_pt"], sig["truth_pz"]]),
        np.column_stack([sig["reco_pt"], sig["reco_pz"]]),
        np.column_stack([meas_pt, meas_pz]),
        sig["pass_reco"], sig["pass_truth"],
        np.ones(meas_pt.shape[0], dtype=bool),
        int(args.iters),
        MCgen_weights=sig["w_truth"],
        MCreco_weights=sig["w_reco"],
        measured_weights=meas_w,
        classifier1_params=c1, classifier2_params=c2, regressor_params=rg,
        parameter_format="dict", estimator=args.estimator, device=args.device,
    )

    w_in = sig["w_truth"][sig["pass_truth"]]
    if step2_w.shape[0] != w_in.shape[0]:
        raise RuntimeError(f"step2 size {step2_w.shape[0]} != truth-pass {w_in.shape[0]}")
    h_prior = fill_th2d("hTruth2D", "MC truth prior (this toy's MC weights)", pt_in, pz_in, w_in)
    h_unfold = fill_th2d("hUnfold2D", "Unfolded (2D OmniFold)", pt_in, pz_in, step2_w * w_in)
    h_xs = u2d.extract_cross_section_2d(h_unfold, h_comp, flux_bins, data_pot, n_nucleons,
                                        pt_edges, pz_edges)
    h_prior_xs = u2d.extract_cross_section_2d(h_prior, h_comp, flux_bins, data_pot, n_nucleons,
                                              pt_edges, pz_edges)
    h_prior_xs.SetName("hTruthXSec2D")
    h_prior_xs.SetTitle("MC truth prior cross section (fluctuates with the MC bootstrap)")
    meta["wall_s"] = time.time() - t0
    try:
        identity = gx.recheck(REPO, identity)
    except gx.ProvenanceRefusal as exc:
        print(f"[REFUSED] {exc}", file=sys.stderr)
        sys.exit(gx.REFUSAL_EXIT)

    f_out = ROOT.TFile.Open(args.out, "RECREATE")
    if not f_out or f_out.IsZombie():
        raise RuntimeError(f"Could not create {args.out}")
    for h in (h_xs, h_truth_fixed_xs, h_prior_xs, h_unfold, h_truth_fixed, h_prior,
              h_pseudo, h_flux):
        h.Write()
    ROOT.TNamed("toyMetadata", json.dumps(meta, sort_keys=True)).Write()
    provenance = dict(identity, inputs=inputs, environment=gx.environment_record(),
                      run_config=vars(args),
                      estimator={"estimator": args.estimator, "device": args.device,
                                 "iters": int(args.iters), "classifier1_params": c1,
                                 "classifier2_params": c2, "regressor_params": rg,
                                 "parameter_format": "dict"})
    for name, value in (("runConfig", json.dumps(vars(args), sort_keys=True)),
                        ("omnifoldHelperFile", helper["path"]),
                        ("omnifoldHelperSha256", helper["sha256"]),
                        ("producerProvenance", json.dumps(provenance, sort_keys=True))):
        ROOT.TNamed(name, value).Write()
    f_out.Close()
    print(f"[OK] wrote {args.out} in {meta['wall_s']:.0f} s")


if __name__ == "__main__":
    main()
