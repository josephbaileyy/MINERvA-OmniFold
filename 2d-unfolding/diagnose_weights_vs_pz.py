#!/usr/bin/env python3
"""
Option 1 — MnvTune-v1 reweighter chain audit on the combined per-event
weight (w_truth, w_reco) as a function of truth p_||.

The 1A event-loop output trees only expose the combined product of all
MnvTune-v1 reweighters (FluxAndCV * GENIE * LowRecoil2p2h *
MINOSEfficiency * RPA). We cannot decompose into individual factors
without re-running the C++ event loop. But the question we need to
answer first is: does the combined weight have a low-p_|| shape bias
that could explain the 1.41x truth-shape deficit found in Step 2?

If <w_truth> is flat in truth p_||, the reweighter chain is innocent
and option 1 is closed. If it is not flat — and especially if it dips
at low p_|| — then a reweighter is the gradient driver and we need to
go decompose by recompiling.

Read-only. Writes JSON + PNG.
"""

import argparse
import json
import os
import tempfile

os.environ.setdefault(
    "MPLCONFIGDIR",
    os.path.join(tempfile.gettempdir(), "minerva101-mplconfig"),
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)

from unfold_2d_omnifold_unbinned import PT_EDGES, PZ_EDGES

DEFAULT_INPUT = "2d-unfolding/runEventLoopOmniFold_1A_minos_fix.root"
DEFAULT_OUT_PREFIX = "2d-unfolding/weights_vs_pz_1A"


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default=DEFAULT_INPUT)
    p.add_argument("--out-prefix", default=DEFAULT_OUT_PREFIX)
    return p.parse_args()


def load_tree(path, tname, branches):
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open {path}")
    t = f.Get(tname)
    if not t:
        raise RuntimeError(f"missing {tname} in {path}")
    # Use RDataFrame to read each branch with its native dtype, then cast.
    rdf = ROOT.RDataFrame(t)
    out = {}
    for b in branches:
        col = rdf.AsNumpy([b])[b]
        # Bool_t branches come back as numpy object arrays of single-byte
        # bytes; map "\x01"/"\x00" to 1/0 and then cast to float.
        if col.dtype == object:
            arr = np.fromiter(
                (1 if (x and (x != b"\x00")) else 0 for x in col),
                count=len(col),
                dtype=np.float64,
            )
            out[b] = arr
        else:
            out[b] = np.asarray(col, dtype=float)
    f.Close()
    return out


def in_phase(pt, pz):
    return (pt >= 0.0) & (pt <= 4.5) & (pz >= 1.5) & (pz <= 60.0)


def strip_stats(pz, w, edges):
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (pz >= lo) & (pz < hi)
        n = int(m.sum())
        if n == 0:
            out.append({"pz_low": float(lo), "pz_high": float(hi),
                        "n": 0, "mean_w": None, "median_w": None,
                        "rms_w": None, "sum_w": 0.0})
            continue
        ww = w[m]
        out.append({
            "pz_low": float(lo),
            "pz_high": float(hi),
            "n": n,
            "mean_w": float(ww.mean()),
            "median_w": float(np.median(ww)),
            "rms_w": float(ww.std()),
            "sum_w": float(ww.sum()),
        })
    return out


def main():
    args = parse_args()

    # truth tree: pt = MC, pz = MC_pz, weight = w_truth
    print("[INFO] loading mc_truth_denom ...")
    truth = load_tree(args.input, "mc_truth_denom",
                      ["MC", "MC_pz", "w_truth"])
    pt_t = truth["MC"]
    pz_t = truth["MC_pz"]
    w_t = truth["w_truth"]
    mask_t = in_phase(pt_t, pz_t)
    print(f"[INFO] truth: {len(pt_t)} entries, {mask_t.sum()} in phase")

    # reco-passing signal tree: pt = MC, pz = MC_pz, w = w_reco, pass = sim_pass
    print("[INFO] loading mc_signal_reco ...")
    sig = load_tree(args.input, "mc_signal_reco",
                    ["MC", "MC_pz", "sim_pass", "w_reco", "w_truth"])
    pt_s = sig["MC"]
    pz_s = sig["MC_pz"]
    w_r = sig["w_reco"]
    pass_r = sig["sim_pass"] > 0.5
    mask_s = in_phase(pt_s, pz_s) & pass_r
    print(f"[INFO] sig: {len(pt_s)} entries, "
          f"{mask_s.sum()} in phase + pass_reco")

    # Strip stats over PZ_EDGES = paper p_|| binning
    truth_strips = strip_stats(pz_t[mask_t], w_t[mask_t], PZ_EDGES)
    reco_strips = strip_stats(pz_s[mask_s], w_r[mask_s], PZ_EDGES)

    # Reference: pz>=20 GeV plateau average
    plateau_truth = [s for s in truth_strips if s["pz_low"] >= 20.0]
    plateau_reco = [s for s in reco_strips if s["pz_low"] >= 20.0]

    def avg(strips, key):
        vals = [s[key] for s in strips if s[key] is not None]
        return float(np.mean(vals)) if vals else None

    ref_truth = avg(plateau_truth, "mean_w")
    ref_reco = avg(plateau_reco, "mean_w")

    summary = {
        "input": args.input,
        "n_truth_in_phase": int(mask_t.sum()),
        "n_reco_in_phase_passing": int(mask_s.sum()),
        "ref_mean_w_truth_pz_ge_20": ref_truth,
        "ref_mean_w_reco_pz_ge_20": ref_reco,
        "interpretation": (
            "<w_truth> is the combined MnvTune-v1 weight on truth-only "
            "events (no reco selection). <w_reco> is the same product "
            "but only for events that pass reco selection. Each row "
            "below shows the mean and median weight per truth-p_|| "
            "strip, plus the ratio relative to the high-p_|| (>=20 GeV) "
            "plateau. If these ratios are ~1 across all p_||, the "
            "reweighter chain is not the source of the low-p_|| truth "
            "shape deficit; the gradient lives elsewhere "
            "(option 2: pass_reco definition; option 3: AnaTuple cuts)."
        ),
        "truth_strips": truth_strips,
        "reco_strips": reco_strips,
    }

    out_json = f"{args.out_prefix}_summary.json"
    out_png = f"{args.out_prefix}_strips.png"
    with open(out_json, "w") as fout:
        json.dump(summary, fout, indent=2, sort_keys=True)
        fout.write("\n")

    pz_mid = 0.5 * (np.array(PZ_EDGES[:-1]) + np.array(PZ_EDGES[1:]))
    pz_w = np.diff(PZ_EDGES)

    def column(strips, key):
        return np.array([
            (s[key] if s[key] is not None else np.nan) for s in strips
        ], dtype=float)

    mw_t = column(truth_strips, "mean_w")
    mw_r = column(reco_strips, "mean_w")
    n_t = column(truth_strips, "n")
    n_r = column(reco_strips, "n")

    fig, axs = plt.subplots(2, 1, figsize=(9.0, 8.0), sharex=True)
    axs[0].errorbar(pz_mid, mw_t, xerr=pz_w / 2.0, fmt="o-",
                    color="#1f77b4", capsize=2,
                    label=r"$\langle w_{\rm truth} \rangle$")
    axs[0].errorbar(pz_mid, mw_r, xerr=pz_w / 2.0, fmt="s-",
                    color="#d62728", capsize=2,
                    label=r"$\langle w_{\rm reco} \rangle$ (pass_reco)")
    if ref_truth is not None:
        axs[0].axhline(ref_truth, color="#1f77b4", lw=0.8, ls=":",
                       alpha=0.6)
    if ref_reco is not None:
        axs[0].axhline(ref_reco, color="#d62728", lw=0.8, ls=":",
                       alpha=0.6)
    axs[0].set_ylabel("mean per-event MnvTune-v1 weight")
    axs[0].grid(True, alpha=0.25)
    axs[0].legend(frameon=False)

    if ref_truth and ref_truth > 0:
        rel_t = mw_t / ref_truth
        axs[1].errorbar(pz_mid, rel_t, xerr=pz_w / 2.0, fmt="o-",
                        color="#1f77b4", capsize=2,
                        label="<w_truth> / plateau")
    if ref_reco and ref_reco > 0:
        rel_r = mw_r / ref_reco
        axs[1].errorbar(pz_mid, rel_r, xerr=pz_w / 2.0, fmt="s-",
                        color="#d62728", capsize=2,
                        label="<w_reco> / plateau")
    axs[1].axhline(1.0, color="#555555", lw=1.0, ls="--")
    axs[1].set_xlabel(r"$p_{\parallel}$ (GeV/c)")
    axs[1].set_ylabel("weight / high-p_|| plateau")
    axs[1].grid(True, alpha=0.25)
    axs[1].legend(frameon=False)
    fig.suptitle("MnvTune-v1 combined weight vs truth p_|| (1A)")
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)

    print(f"[INFO] truth ref <w> at p||>=20: {ref_truth}")
    print(f"[INFO] reco  ref <w> at p||>=20: {ref_reco}")
    print(f"{'pz':>11}  {'n_t':>8}  {'<w_t>':>8}  {'rel':>6}  "
          f"{'n_r':>8}  {'<w_r>':>8}  {'rel':>6}")
    for st, sr in zip(truth_strips, reco_strips):
        wt = st["mean_w"]
        wr = sr["mean_w"]
        rt = (wt / ref_truth) if (wt and ref_truth) else float("nan")
        rr = (wr / ref_reco) if (wr and ref_reco) else float("nan")
        print(f"  {st['pz_low']:4.1f}-{st['pz_high']:4.1f}  "
              f"{st['n']:8d}  {wt or 0:8.4f}  {rt:6.3f}  "
              f"{sr['n']:8d}  {wr or 0:8.4f}  {rr:6.3f}")
    print(f"[INFO] wrote {out_json}")
    print(f"[INFO] wrote {out_png}")


if __name__ == "__main__":
    main()
