#!/usr/bin/env python3
"""Measure the HOST-MEMORY high-water mark of build_fullevent_loaders vs input rows.

WHY. `fullevent_fps_dataloader.py:520-521` does

    reco_cloud, _ = build_reco_cloud(np.asarray(d["part_reco"])[imc])
    gen_cloud,  _ = build_truth_cloud(np.asarray(d["part_gen"])[imc])

so `np.asarray(...)` materializes the FULL signal array (49,152,885 rows in the real
G2 dump) before `[imc]` subsamples it, and `build_truth_cloud` then stacks
kin(4)+pdg+theta+cos-phi+sin-phi into an (n,12,8) cloud through several full-size
temporaries. `rank`/`size` only reach the DataLoader at `:612`, AFTER the clouds are
built -- so under `-np 4` every rank holds a full copy and the node sees ~4x the peak.

A hand estimate put the per-rank construction peak near 78 GiB at max_events=40M,
i.e. ~310 GiB across 4 ranks against a 251.6 GiB node (Delta gpuA100x4 and cpu both
report 257,630 MiB). That is a projection, not a measurement. This script measures it.

METHOD. Run one rung, record the peak at four checkpoints, and let the caller fit
peak-vs-rows and extrapolate. Single-process is sufficient and far cheaper than 4
real ranks: sharding happens after construction, so ranks are symmetric at the peak
and the node total is 4x one rank. Confirm that factor once at a small rung.

The frozen dataloader is NOT edited. Checkpoints come from wrapping its cloud
builders at runtime; `fullevent_fps_dataloader.py` is bound by sha256 in the Gate-2
canonical runtime receipt and must stay byte-identical.

NOT A PHYSICS RUN. Random fixture, and the ROOT-free sklearn refinement shim, so
`refinement_is_learned_production` is False by construction. Memory only.

  python3 measure_fullevent_host_memory.py --fixture G2_SYNTH.npz --rows 5000000 \
      --max-events 4069000 --out rung_5M.json
"""
import argparse
import json
import os
import resource
import sys

sys.path[:0] = [os.path.dirname(os.path.abspath(__file__)),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tests")]

import numpy as np                                            # noqa: E402
import fullevent_fps_dataloader as fe                         # noqa: E402

GIB = float(1 << 30)

# Real G2 dump inventory -- the ratios every rung preserves so the shape of the
# measurement matches the production case rather than an arbitrary mix.
REAL_SIG, REAL_DATA, REAL_BKG = 49152885, 4116128, 564591
REAL_MAXEV = 40_000_000
SUBSAMPLE_RATIO = REAL_MAXEV / REAL_SIG                       # 0.8138...


def fast_refine(feat, signed, **kw):
    """Memory-ladder refiner: the same closed form as tests/sklearn_refine
    (w~ = |w| * clip(2g-1, 0)), but a histogram GBDT fitted on a capped sample.

    WHY NOT sklearn_refine: it fits a plain GradientBoostingClassifier on EVERY
    measured row. At the 20M rung that is ~1.9M rows and the boosting, not the
    memory, would dominate the wall clock. This variant keeps the refinement in
    the code path (so the measured/background clouds and their concatenation are
    still built, which is what the peak has to include) while spending the rung's
    time on what is being measured.

    The loader validates only alignment + finite + non-negative, so this is
    sufficient. It is NOT a physics refinement -- see the module docstring."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    feat = np.asarray(feat, float); signed = np.asarray(signed, float)
    lab = (signed > 0).astype(int); absw = np.abs(signed)
    n = feat.shape[0]
    cap = int(kw.get("fit_cap", 200_000))
    idx = (np.random.default_rng(0).choice(n, cap, replace=False) if n > cap
           else np.arange(n))
    clf = HistGradientBoostingClassifier(random_state=0, max_iter=60)
    clf.fit(feat[idx], lab[idx], sample_weight=absw[idx])
    g = np.clip(clf.predict_proba(feat)[:, 1], 1e-6, 1.0 - 1e-6)
    return np.clip(absw * (2.0 * g - 1.0), 0.0, None), g, float(np.mean(2.0 * g - 1.0 < 0))


def peak_gib():
    """Process peak RSS. VmHWM is the kernel's own high-water mark (Linux); ru_maxrss
    is the portable fallback (KiB on Linux)."""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return float(line.split()[1]) / (1 << 20)   # kB -> GiB
    except OSError:
        pass
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 20)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fixture", required=True, help="g2-fullevent-v1 NPZ (synthetic)")
    p.add_argument("--rows", type=int, required=True, help="signal rows in the fixture (for the fit)")
    p.add_argument("--max-events", type=int, default=None,
                   help="training subsample; default = round(0.8138 * rows), the real 40M/49.15M ratio")
    p.add_argument("--bkg-mode", default="negweight-refined", choices=("negweight-refined", "purity"))
    p.add_argument("--refiner", default="fast", choices=("fast", "sklearn"),
                   help="fast = capped-fit histogram GBDT (default; see fast_refine); "
                        "sklearn = tests/sklearn_refine, faithful but fits every measured row")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    max_events = a.max_events if a.max_events is not None else int(round(SUBSAMPLE_RATIO * a.rows))

    marks = {"import": peak_gib()}
    counters = {"reco": 0, "truth": 0}
    real_reco, real_truth = fe.build_reco_cloud, fe.build_truth_cloud

    def reco_wrap(part_reco):
        out = real_reco(part_reco)
        counters["reco"] += 1
        marks[f"after_build_reco_cloud_{counters['reco']}"] = peak_gib()
        return out

    def truth_wrap(part_gen):
        out = real_truth(part_gen)
        counters["truth"] += 1
        marks[f"after_build_truth_cloud_{counters['truth']}"] = peak_gib()
        return out

    fe.build_reco_cloud, fe.build_truth_cloud = reco_wrap, truth_wrap

    kwargs = dict(max_events=max_events, seed=0, bkg_mode=a.bkg_mode)
    if a.bkg_mode == "negweight-refined":
        if a.refiner == "sklearn":
            from test_fullevent_gate2 import sklearn_refine    # ROOT-free, algorithm-identical
            kwargs["refine_fn"] = sklearn_refine
        else:
            kwargs["refine_fn"] = fast_refine

    try:
        data, mc, imc, cr, cg, meta = fe.build_fullevent_loaders(a.fixture, **kwargs)
        marks["after_build_fullevent_loaders"] = peak_gib()
        gen_shape = list(np.asarray(mc.gen).shape)
        reco_shape = list(np.asarray(mc.reco).shape)
        meas_rows = int(np.asarray(data.reco).shape[0])
        marks["after_shape_touch"] = peak_gib()
        err = None
    except Exception as exc:                                   # a rung that OOMs or trips a guard
        marks["at_failure"] = peak_gib()
        gen_shape = reco_shape = None
        meas_rows = None
        err = f"{type(exc).__name__}: {exc}"

    peak = max(marks.values())
    rec = {
        "schema": "fe-hostmem-rung-v1",
        "NOT_A_PHYSICS_RESULT": ("synthetic fixture + ROOT-free sklearn refinement shim; "
                                 "host-memory measurement only, never publication evidence"),
        "fixture": os.path.abspath(a.fixture),
        "fixture_bytes": (os.path.getsize(a.fixture) if os.path.exists(a.fixture) else None),
        "rows_signal": a.rows,
        "max_events": max_events,
        "subsample_ratio": max_events / float(a.rows),
        "bkg_mode": a.bkg_mode, "refiner": a.refiner,
        "n_mc_selected": (int(np.asarray(imc).shape[0]) if err is None else None),
        "gen_cloud_shape": gen_shape, "reco_cloud_shape": reco_shape,
        "measured_rows": meas_rows,
        "peak_rss_gib": peak,
        "peak_rss_gib_by_checkpoint": marks,
        "projected_4rank_node_gib": 4.0 * peak,
        "node_capacity_gib": 257630.0 / 1024.0,
        "refinement_is_learned_production": (
            meta["target"].get("refinement_is_learned_production")
            if err is None and a.bkg_mode == "negweight-refined" else None),
        "error": err,
    }
    with open(a.out, "w") as f:
        json.dump(rec, f, indent=2)

    print(f"[hostmem] rows={a.rows} max_events={max_events} peak={peak:.2f} GiB "
          f"4-rank={4.0 * peak:.1f} GiB vs node {rec['node_capacity_gib']:.1f} GiB")
    for k in sorted(marks, key=lambda k: marks[k]):
        print(f"[hostmem]   {k:34s} {marks[k]:8.2f} GiB")
    if err:
        print(f"[hostmem] FAILED: {err}")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
