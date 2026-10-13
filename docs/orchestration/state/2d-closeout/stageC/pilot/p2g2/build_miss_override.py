#!/usr/bin/env python3
"""P5: per-entry universe truth weights for the appended truth-only miss rows of mc_signal_reco.

Why this works without a new event loop (runEventLoopOmniFold.cpp at origin/main 3921dec4):
  - the truth-denominator loop fills mc_truth_denom and pushes the same event onto truthDenomCache in the same
    iteration (:637 fill, :667 push), so truth-tree row i of a playlist is cache entry i;
  - AppendTruthOnlyMisses walks the cache in order and appends one miss row per cache entry absent from the reco
    loop (:854-910), copying MC, MC_pz and w_truth from the cache and setting every universe weight to the CV
    w_truth (:862-863, the G2 proxy). mc_truth_denom's own universe weights are filled correctly (:801-803);
  - per playlist, mc_signal_reco and mc_truth_denom have the same entry count, and the misses are the last
    nTruthOnlyMisses signal rows; hadd concatenates both trees in the same playlist order.
So within each playlist block the miss rows are an ordered subsequence of the truth rows with identical
(MC, MC_pz, w_truth). This script finds that subsequence by exact key, proves it (unique keys, strictly increasing,
complement equal to the reco rows on (MC, MC_pz, w_truth, w_truth_<u>) as exact multisets), and writes the truth
tree's w_truth_<u> onto the miss rows.

  python build_miss_override.py --omnifile <merged.root> --blocks <per-playlist .root ...> \
      --universe MaRES:0 --out override.npz --report override.json
  (single-file mode for a per-playlist file: --blocks <the same file>)

Output npz: w_override (float64, len = mc_signal_reco entries; NaN except on miss rows), universe, n_signal,
omnifile, omnifile_size. Read-only on every input.
"""
import argparse
import json
import os
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)


def keys(cols):
    a = np.ascontiguousarray(np.stack(cols, axis=1).astype(np.float64))
    return a.view(f"V{8 * a.shape[1]}").ravel()


def sorted_equal(a, b):
    return a.size == b.size and np.array_equal(np.sort(a), np.sort(b))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--omnifile", required=True)
    ap.add_argument("--blocks", nargs="+", required=True,
                    help="the per-playlist omnifiles in hadd order (block sizes and miss counts)")
    ap.add_argument("--universe", required=True, help="BAND:IDX, e.g. MaRES:0")
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()
    band, idx = args.universe.split(":")
    U = f"w_truth_{band}_{int(idx)}"
    rep = {"omnifile": os.path.realpath(args.omnifile), "omnifile_size": os.path.getsize(args.omnifile),
           "universe": args.universe, "branch": U, "blocks": [], "checks": {}}

    def check(name, ok, value=None):
        rep["checks"][name] = {"pass": bool(ok), "value": value}
        print(f"[check] {name}: {'PASS' if ok else 'FAIL'} {'' if value is None else value}")
        if not ok:
            json.dump(rep, open(args.report, "w"), indent=1)
            sys.exit(2)

    sizes = []
    for b in args.blocks:
        f = ROOT.TFile.Open(b)
        n_s, n_t = f.Get("mc_signal_reco").GetEntries(), f.Get("mc_truth_denom").GetEntries()
        m = int(f.Get("nTruthOnlyMisses").GetVal())
        f.Close()
        check(f"block_{os.path.basename(b)}_signal_eq_truth", n_s == n_t, [n_s, n_t])
        sizes.append((os.path.basename(b), int(n_s), m))

    S = ROOT.RDataFrame("mc_signal_reco", args.omnifile).Define("sp", "(int)sim_pass").AsNumpy(
        ["MC", "MC_pz", "w_truth", "w_reco", U, "sp", "sim"])
    T = ROOT.RDataFrame("mc_truth_denom", args.omnifile).AsNumpy(["MC", "MC_pz", "w_truth", U])
    N = len(S["MC"])
    check("n_signal_eq_n_truth", N == len(T["MC"]), [N, len(T["MC"])])
    check("n_signal_eq_sum_blocks", N == sum(n for _, n, _ in sizes), [N, sum(n for _, n, _ in sizes)])
    fm = ROOT.TFile.Open(args.omnifile)
    pm = fm.Get("nTruthOnlyMisses")
    if pm:
        check("merged_nTruthOnlyMisses_eq_sum", int(pm.GetVal()) == sum(m for _, _, m in sizes),
              [int(pm.GetVal()), sum(m for _, _, m in sizes)])
    fm.Close()

    w_override = np.full(N, np.nan)
    o = 0
    tot_true, tot_proxy = 0.0, 0.0
    for name, n, m in sizes:
        r = n - m
        sl_head, sl_tail = slice(o, o + r), slice(o + r, o + n)
        blk = {"file": name, "offset": o, "n": n, "misses": m}
        check(f"{name}_tail_sim_pass_0", bool((S["sp"][sl_tail] == 0).all()))
        # Reco-loop rows that fail the selection also have sim_pass=0 (sim = -9999); they carry signal-loop
        # universe weights and are not misses. Recorded, not a check.
        blk["head_sim_pass_0"] = int((S["sp"][sl_head] == 0).sum())
        check(f"{name}_tail_sim_sentinel", bool((S["sim"][sl_tail] == -9999.0).all()))
        check(f"{name}_tail_proxy_weights", bool((S[U][sl_tail] == S["w_truth"][sl_tail]).all()
                                                 and (S["w_reco"][sl_tail] == S["w_truth"][sl_tail]).all()))
        tk = keys([T["MC"][o:o + n], T["MC_pz"][o:o + n], T["w_truth"][o:o + n]])
        sk = keys([S["MC"][sl_tail], S["MC_pz"][sl_tail], S["w_truth"][sl_tail]])
        order = np.argsort(tk, kind="stable")
        tks = tk[order]
        check(f"{name}_truth_keys_unique", bool(np.all(tks[1:] != tks[:-1])))
        pos = np.searchsorted(tks, sk)
        pos = np.minimum(pos, n - 1)
        found = tks[pos] == sk
        check(f"{name}_every_miss_found", bool(found.all()), int((~found).sum()))
        tidx = order[pos]
        check(f"{name}_subsequence_order", bool(np.all(np.diff(tidx) > 0)))
        comp = np.ones(n, bool)
        comp[tidx] = False
        check(f"{name}_complement_eq_reco_rows", sorted_equal(
            keys([T["MC"][o:o + n][comp], T["MC_pz"][o:o + n][comp], T["w_truth"][o:o + n][comp],
                  T[U][o:o + n][comp]]),
            keys([S["MC"][sl_head], S["MC_pz"][sl_head], S["w_truth"][sl_head], S[U][sl_head]])))
        wtrue = T[U][o:o + n][tidx]
        w_override[sl_tail] = wtrue
        blk["sum_true_over_proxy"] = float(wtrue.sum() / S["w_truth"][sl_tail].sum())
        tot_true += float(wtrue.sum())
        tot_proxy += float(S["w_truth"][sl_tail].sum())
        rep["blocks"].append(blk)
        o += n

    rep["n_signal"] = N
    rep["n_override"] = int(np.isfinite(w_override).sum())
    rep["sum_true_over_proxy"] = tot_true / tot_proxy
    ratio = w_override[np.isfinite(w_override)] / S["w_truth"][np.isfinite(w_override)]
    rep["per_event_true_over_proxy"] = {"min": float(ratio.min()), "median": float(np.median(ratio)),
                                        "max": float(ratio.max())}
    np.savez(args.out, w_override=w_override, universe=np.array(args.universe), n_signal=np.array(N),
             omnifile=np.array(rep["omnifile"]), omnifile_size=np.array(rep["omnifile_size"]))
    rep["ALL_PASS"] = all(c["pass"] for c in rep["checks"].values())
    json.dump(rep, open(args.report, "w"), indent=1)
    print(json.dumps({k: rep[k] for k in ("n_signal", "n_override", "sum_true_over_proxy",
                                          "per_event_true_over_proxy", "ALL_PASS")}, indent=1))


if __name__ == "__main__":
    main()
