"""Time one loader variant on one synthetic tree, in a fresh process.

Variants (all produce byte-identical arrays; ``test_prototypes.py`` checks that):

* ``pinned``  — the driver's ``collect_signal_arrays_2d``, every branch active
  (production behaviour);
* ``status``  — prototype 1: only the loader's branches active, same function;
* ``columnar`` — prototype 2: ``RDataFrame.AsNumpy`` plus array masks;
* ``truth``   — the driver's ``collect_truth_denom_arrays`` (3 branches), for its
  per-row cost only.

Also ``fill_loop`` / ``fill_n``: the driver's per-row ``TH2D.Fill`` pattern
against one ``TH2D.FillN`` call on the same arrays (contents, errors and stats
compared before timing is reported).

Every variant is single-threaded (no implicit MT; ``OMP_NUM_THREADS=1``). One
warm-up call, then ``--repeats`` timed calls, each on a freshly opened file;
the OS page cache is warm after the warm-up, so this times decompression and
Python work, not disk. Output: one JSON line on stdout.
"""

import argparse
import json
import os
import resource
import sys
import time

import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pinned  # noqa: E402

import ROOT  # noqa: E402

POT = 0.212405


def run_loader(variant, path, drv, bs, vl):
    f = ROOT.TFile.Open(path)
    t = f.Get("mc_signal_reco")
    lo_hi = (drv.PT_EDGES[0], drv.PT_EDGES[-1], drv.PZ_EDGES[0], drv.PZ_EDGES[-1])
    t0 = time.perf_counter()
    if variant == "pinned":
        out = drv.collect_signal_arrays_2d(t, *lo_hi, POT, use_weights=True)
    elif variant == "status":
        bs.restrict_active_branches(t, bs.signal_branches(True, None, t))
        out = drv.collect_signal_arrays_2d(bs.ActiveOnlyTree(t), *lo_hi, POT, use_weights=True)
    elif variant == "truth":
        # the 3-branch mc_truth_denom loop, emulated on the signal tree's MC/MC_pz/w_truth
        bs.restrict_active_branches(t, ["MC", "MC_pz", "w_truth"])
        out = drv.collect_truth_denom_arrays(bs.ActiveOnlyTree(t), *lo_hi, POT, use_weights=True)
    elif variant == "columnar":
        out = vl.collect_signal_arrays_columnar(
            t, ("MC", "MC_pz", "sim", "sim_pz", "w_truth", "w_reco"), *lo_hi, POT,
            use_weights=True)
    else:
        raise ValueError(variant)
    dt = time.perf_counter() - t0
    n = int(t.GetEntries())
    f.Close()
    return dt, n, int(out["truth_pt"].size)


def make_h(drv, name):
    h = drv.make_th2d(name, name, drv.PT_EDGES, drv.PZ_EDGES)
    h.Sumw2()
    return h


def run_fill(variant, path, drv, vl):
    f = ROOT.TFile.Open(path)
    t = f.Get("mc_signal_reco")
    lo_hi = (drv.PT_EDGES[0], drv.PT_EDGES[-1], drv.PZ_EDGES[0], drv.PZ_EDGES[-1])
    sig = vl.collect_signal_arrays_columnar(
        t, ("MC", "MC_pz", "sim", "sim_pz", "w_truth", "w_reco"), *lo_hi, POT, use_weights=True)
    f.Close()
    pt, pz, w = sig["truth_pt"], sig["truth_pz"], sig["w_truth"]
    h = make_h(drv, f"h_{variant}_{time.perf_counter_ns()}")
    t0 = time.perf_counter()
    if variant == "fill_loop":                      # the driver's pattern (e.g. hTruth2D)
        for a, b, c in zip(pt, pz, w):
            h.Fill(float(a), float(b), float(c))
    else:
        h.FillN(int(pt.size), np.ascontiguousarray(pt), np.ascontiguousarray(pz),
                np.ascontiguousarray(w))
    dt = time.perf_counter() - t0
    return dt, int(pt.size), h


def h_state(h):
    nx, ny = h.GetNbinsX() + 2, h.GetNbinsY() + 2
    cont = np.array([h.GetBinContent(i, j) for i in range(nx) for j in range(ny)])
    err2 = np.array([h.GetSumw2().At(h.GetBin(i, j)) for i in range(nx) for j in range(ny)])
    stats = np.zeros(13)
    h.GetStats(stats)
    return cont.tobytes() + err2.tobytes() + stats.tobytes() + np.float64(h.GetEntries()).tobytes()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", choices=["pinned", "status", "truth", "columnar", "fill_loop", "fill_n"])
    ap.add_argument("tree")
    ap.add_argument("--repeats", type=int, default=5)
    args = ap.parse_args()
    drv = pinned.load_driver()
    bs, vl = pinned.load_proto("branch_status"), pinned.load_proto("vector_loader")
    times, rows, kept, check = [], None, None, None
    for k in range(args.repeats + 1):
        if args.variant.startswith("fill"):
            dt, n, h = run_fill(args.variant, args.tree, drv, vl)
            ref = run_fill("fill_loop" if args.variant == "fill_n" else "fill_n", args.tree, drv, vl)[2]
            same = h_state(h) == h_state(ref)
            check = same if check is None else (check and same)
            rows = kept = n
        else:
            dt, rows, kept = run_loader(args.variant, args.tree, drv, bs, vl)
        if k:                                       # k == 0 is the warm-up
            times.append(dt)
    ru = resource.getrusage(resource.RUSAGE_SELF)
    rec = {"variant": args.variant, "tree": os.path.basename(args.tree), "rows": rows,
           "kept": kept, "repeats": args.repeats, "seconds": times,
           "us_per_row_min": 1e6 * min(times) / rows,
           "us_per_row_median": 1e6 * float(np.median(times)) / rows,
           "peak_rss_bytes": ru.ru_maxrss, "fill_equal_to_other_variant": check,
           "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
           "root": ROOT.gROOT.GetVersion(), "numpy": np.__version__,
           "python": sys.version.split()[0], "loadavg_end": os.getloadavg(),
           "driver_blob": drv.__pinned_blob__}
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
