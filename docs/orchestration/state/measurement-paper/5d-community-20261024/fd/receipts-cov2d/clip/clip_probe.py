"""COV2D clipping probe (the director's approval of 2026-11-03, after receipt R1's flag): descriptive, no verdict.
Login node, nice 19, 0 node-h. $UNI, the constraint file, F1's two ratio files and Q_R's 205-cell blocks are read only
through O_NOATIME descriptors, each pinned, with atime checked before and after.

(a) Per universe and array (w_reco on mc_signal_reco, w_truth on mc_truth_denom, w_bkg on mc_background): the rows with
    a_CV > 0 and a_u <= 0, the CV weight they carry and their universe weight.
(b) Per declared draw (300 per tune), the toys' Poisson means as COV2D-DECLARATION.md section 4.2 defines them:
    lambda = w_reco,D x r_T x s on signal rows and w_bkg,D x s on background rows, over the rows the driver keeps as
    measured events (pass flag, finite, inside the reco window). Printed and recorded:
    * sum(lambda-) / sum(lambda), signal and background;
    * per reco cell, |sum lambda-| over signal and background in units of the cell's data-statistical sigma,
      sqrt(sum lambda+);
    * per truth cell, |sum lambda-| of the signal rows binned by their truth cell, relative to the draw's composite truth
      count in that cell (sum w_truth,D x r_T x s over mc_truth_denom), then in units of the relative sigma of Q_R's stat
      block and of Q_R itself on the 205 cells (cov2d_Q_205.npz).
    Each per-cell quantity is summarized over the tune's 300 draws by its median, 90th percentile and maximum.

  python clip_probe.py --out clip.json [--uni PATH] [--prep DIR] [--constraint PATH] [--q205 PATH] [--chunk N]

MEASURES: the quantities above, at the expected counts, before any toy exists. CANNOT AUTHORIZE: a verdict, a remedy,
or any statement about the cause of the negative composites beyond (a)'s counts.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
for p in (REPO / "2d-unfolding" / "cov2d", REPO / "nd-unfolding", REPO / "nd-unfolding" / "pv-ladder"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402
import cov2d_receipt as rc  # noqa: E402

Q205 = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2/outA/cov2d_Q_205.npz"
Q205_SHA256 = "7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2"
GEN = ("MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W")
N_CELLS = 224
GUARD = 1e3


def reco_cell(pt: np.ndarray, pz: np.ndarray, passed: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(kept, cell): the rows fill_data_reco_2d keeps (pass, finite, |x| <= 1e3, inside the window, edges included),
    and each kept row's flat (pT, p_par) cell as a TH2D fills it (-1 for the upper-edge overflow and dropped rows)."""
    drv = rc.driver_phase_space()
    pe, ze = np.asarray(drv["PT_EDGES"], float), np.asarray(drv["PZ_EDGES"], float)
    with np.errstate(invalid="ignore"):
        kept = (np.asarray(passed) != 0) & np.isfinite(pt) & np.isfinite(pz) & (np.abs(pt) <= GUARD) & \
            (np.abs(pz) <= GUARD) & (pt >= pe[0]) & (pt <= pe[-1]) & (pz >= ze[0]) & (pz <= ze[-1])
    i = np.searchsorted(pe, pt, side="right") - 1
    j = np.searchsorted(ze, pz, side="right") - 1
    ok = kept & (i < pe.size - 1) & (j < ze.size - 1)
    return kept, np.where(ok, i * (ze.size - 1) + j, -1)


def onehot(cell: np.ndarray):
    from scipy import sparse
    ok = np.flatnonzero(cell >= 0)
    return sparse.csr_matrix((np.ones(ok.size), (cell[ok], ok)), shape=(N_CELLS, cell.size))


def summarize(z: np.ndarray) -> dict:
    """Per-cell median, 90th percentile and max over draws of z (cells, draws), NaN-free cells only."""
    return {"median": np.nanmedian(z, axis=1), "p90": np.nanpercentile(z, 90, axis=1), "max": np.nanmax(z, axis=1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--uni", default=rc.UNI)
    ap.add_argument("--prep", default=rc.PREP)
    ap.add_argument("--constraint", default=c.CONSTRAINT)
    ap.add_argument("--q205", default=Q205)
    ap.add_argument("--chunk", type=int, default=rc.CHUNK)
    ap.add_argument("--no-pins", action="store_true", help="tests only: skip the digest pins")
    args = ap.parse_args(argv)
    import uproot
    import fd_1b_toys
    import pvl_lib
    import s5e_deform

    t0 = time.time()
    rec = {"host": os.uname().nodename, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "nice": os.nice(0),
           "uproot": uproot.__version__, "numpy": np.__version__, "chunk": args.chunk}
    reads = [args.uni, args.constraint, args.q205] + [str(Path(args.prep) / fd_1b_toys.TRUTHS[t])
                                                      for t in rc.TUNES.values()]
    before = {p: rc.atime(p) for p in reads}

    text, sha = rc.read_noatime(args.constraint)
    if not args.no_pins and sha != c.CONSTRAINT_SHA256:
        raise c.Refusal(f"constraint sha256 {sha}")
    w_flux = c.flux_weights(text.decode())
    ratios = {}
    for tune, name in rc.TUNES.items():
        data, sha = rc.read_noatime(str(Path(args.prep) / fd_1b_toys.TRUTHS[name]))
        if not args.no_pins and sha != fd_1b_toys.committed_ratio_sha256(name):
            raise c.Refusal(f"{tune} ratio sha256 {sha}")
        ratios[tune] = json.loads(data)
    qbytes, sha = rc.read_noatime(args.q205)
    if not args.no_pins and sha != Q205_SHA256:
        raise c.Refusal(f"cov2d_Q_205.npz sha256 {sha}")
    q = np.load(io.BytesIO(qbytes))
    cells205 = np.asarray(q["cells"], int)
    rel = {k: np.sqrt(np.diag(q[k])) / q["x"] for k in ("stat", "Q")}

    tunes = list(rc.TUNES)
    draws = {t: c.declared_draws(t, w_flux) for t in tunes}
    idx = {t: rc.draw_index(draws[t]) for t in tunes}
    S = {t: rc.selection(idx[t], c.N_UNIVERSES) for t in tunes}
    edges = [pvl_lib.FINE[a] for a in pvl_lib.AXES5]
    out_a = {}

    with rc.open_noatime(args.uni) as fh:
        f = uproot.open(fh)
        s = float(f["dataPOTUsed"].member("fVal")) / float(f["mcPOTUsed"].member("fVal"))
        rec["pot_scale"] = s
        td, ts, tb = f["mc_truth_denom"], f["mc_signal_reco"], f["mc_background"]
        a = td.arrays(list(GEN) + ["w_truth"], library="np")
        gen_d = np.stack([np.asarray(a[k], np.float64) for k in GEN], axis=1)
        w_d = np.asarray(a["w_truth"], np.float64)
        cell_d = rc.truth_cell(gen_d[:, 0], gen_d[:, 1])
        a = ts.arrays(list(GEN) + ["sim", "sim_pz", "sim_pass"], library="np")
        gen_s = np.stack([np.asarray(a[k], np.float64) for k in GEN], axis=1)
        tcell_s = rc.truth_cell(gen_s[:, 0], gen_s[:, 1])
        kept_s, rcell_s = reco_cell(np.asarray(a["sim"], float), np.asarray(a["sim_pz"], float), a["sim_pass"])
        del a
        nd = gen_d.shape[0]
        gen = np.concatenate([gen_d, gen_s])
        del gen_d, gen_s
        wcat = np.concatenate([w_d, np.zeros(gen.shape[0] - nd)])
        r_d, r_s = {}, {}
        for t in tunes:   # one rescale constant, from mc_truth_denom's rows (section 4.1)
            r = s5e_deform.ratio_weight(gen, edges, wcat, ratios[t], 1.0)
            r_d[t], r_s[t] = r[:nd], r[nd:]
        del gen, wcat
        rec["r_signal_range"] = {t: [float(r_s[t].min()), float(r_s[t].max())] for t in tunes}

        def count_a(name, cv, U, start_acc):
            pos = cv > 0
            bad = pos[:, None] & (U <= 0)
            start_acc["rows"] += bad.sum(axis=0)
            start_acc["cv_weight"] += (bad * cv[:, None]).sum(axis=0)
            start_acc["u_weight"] += (bad * U).sum(axis=0)

        def acc_new():
            return {"rows": np.zeros(c.N_UNIVERSES, np.int64), "cv_weight": np.zeros(c.N_UNIVERSES),
                    "u_weight": np.zeros(c.N_UNIVERSES)}

        # truth counts per cell, per tune, per universe
        h = {t: np.zeros((1 + c.N_UNIVERSES, N_CELLS)) for t in tunes}
        acc = acc_new()
        cols = ["w_truth"] + rc.universe_columns("w_truth")
        for start in range(0, td.num_entries, args.chunk):
            stop = min(start + args.chunk, td.num_entries)
            a = td.arrays(cols, entry_start=start, entry_stop=stop, library="np")
            W = np.stack([np.nan_to_num(np.asarray(a[k], np.float64), nan=0.0, posinf=0.0, neginf=0.0)
                          for k in cols], axis=1)
            count_a("wt", W[:, 0], W[:, 1:], acc)
            for t in tunes:
                h[t] += rc.cell_hists(cell_d[start:stop], W * (r_d[t][start:stop] * s)[:, None], N_CELLS)
        out_a["wt"] = acc
        n_truth = {t: np.stack([c.compose(h[t][0], [h[t][1 + k] for k in d]) for d in idx[t]]).T for t in tunes}

        res = {t: {k: np.zeros((N_CELLS, len(draws[t]))) for k in ("reco_neg", "reco_pos", "truth_neg")} for t in tunes}
        tot = {t: {k: np.zeros(len(draws[t])) for k in ("sig_lam", "sig_neg", "bkg_lam", "bkg_neg")} for t in tunes}

        # signal rows
        acc = acc_new()
        cols = ["w_reco"] + rc.universe_columns("w_reco")
        for start in range(0, ts.num_entries, args.chunk):
            stop = min(start + args.chunk, ts.num_entries)
            a = ts.arrays(cols, entry_start=start, entry_stop=stop, library="np")
            W = np.stack([np.nan_to_num(np.asarray(a[k], np.float64), nan=0.0, posinf=0.0, neginf=0.0)
                          for k in cols], axis=1)
            cv, U = W[:, 0], W[:, 1:]
            count_a("wr", cv, U, acc)
            k = kept_s[start:stop]
            R, T = onehot(rcell_s[start:stop]), onehot(np.where(k, tcell_s[start:stop], -1))
            for t in tunes:
                A = cv[:, None] + (U - cv[:, None]) @ S[t]
                lam = A * (r_s[t][start:stop] * s)[:, None]
                lam[~k] = 0.0
                neg = np.minimum(lam, 0.0)
                tot[t]["sig_lam"] += lam.sum(axis=0)
                tot[t]["sig_neg"] += neg.sum(axis=0)
                res[t]["reco_neg"] += R @ neg
                res[t]["reco_pos"] += R @ np.maximum(lam, 0.0)
                res[t]["truth_neg"] += T @ neg
        out_a["wr"] = acc

        # background rows
        acc = acc_new()
        cols = ["w_bkg"] + rc.universe_columns("w_bkg")
        a = tb.arrays(["sim_background", "sim_background_pz", "sim_background_pass"], library="np")
        kept_b, rcell_b = reco_cell(np.asarray(a["sim_background"], float),
                                    np.asarray(a["sim_background_pz"], float), a["sim_background_pass"])
        for start in range(0, tb.num_entries, args.chunk):
            stop = min(start + args.chunk, tb.num_entries)
            a = tb.arrays(cols, entry_start=start, entry_stop=stop, library="np")
            W = np.stack([np.nan_to_num(np.asarray(a[k], np.float64), nan=0.0, posinf=0.0, neginf=0.0)
                          for k in cols], axis=1)
            cv, U = W[:, 0], W[:, 1:]
            count_a("bkgw", cv, U, acc)
            k = kept_b[start:stop]
            R = onehot(rcell_b[start:stop])
            for t in tunes:
                lam = (cv[:, None] + (U - cv[:, None]) @ S[t]) * s
                lam[~k] = 0.0
                neg = np.minimum(lam, 0.0)
                tot[t]["bkg_lam"] += lam.sum(axis=0)
                tot[t]["bkg_neg"] += neg.sum(axis=0)
                res[t]["reco_neg"] += R @ neg
                res[t]["reco_pos"] += R @ np.maximum(lam, 0.0)
        out_a["bkgw"] = acc

    names = rc.universe_columns("u")
    rec["a"] = {arr: [{"universe": names[k][2:], "rows": int(v["rows"][k]), "cv_weight": float(v["cv_weight"][k]),
                       "u_weight": float(v["u_weight"][k])}
                      for k in np.argsort(-v["rows"]) if v["rows"][k] > 0] for arr, v in out_a.items()}
    rec["b"] = {}
    for t in tunes:
        fs, fb = -tot[t]["sig_neg"] / tot[t]["sig_lam"], -tot[t]["bkg_neg"] / tot[t]["bkg_lam"]
        with np.errstate(invalid="ignore", divide="ignore"):
            z_reco = np.where(res[t]["reco_pos"] > 0, -res[t]["reco_neg"] / np.sqrt(res[t]["reco_pos"]), np.nan)
            frac = np.where(n_truth[t] > 0, -res[t]["truth_neg"] / n_truth[t], np.nan)[cells205]
        z_stat, z_q = frac / rel["stat"][:, None], frac / rel["Q"][:, None]
        sr, ss, sq = summarize(z_reco), summarize(z_stat), summarize(z_q)
        q3 = lambda v: {"median": float(np.median(v)), "p90": float(np.percentile(v, 90)), "max": float(np.max(v))}
        top = np.argsort(-sq["median"])[:10]
        rec["b"][t] = {
            "signal_clipped_fraction": q3(fs), "background_clipped_fraction": q3(fb),
            "reco_cells_z": {k: [None if np.isnan(x) else float(x) for x in v] for k, v in sr.items()},
            "truth_cells_frac_over_sigma_stat": {k: v.tolist() for k, v in ss.items()},
            "truth_cells_frac_over_sigma_Q": {k: v.tolist() for k, v in sq.items()},
            "cells205": cells205.tolist(),
            "top10_by_median_over_sigma_Q": [{"cell": int(cells205[i]), "median": float(sq["median"][i]),
                                              "p90": float(sq["p90"][i]), "max": float(sq["max"][i]),
                                              "median_over_sigma_stat": float(ss["median"][i])} for i in top],
            "over_cells": {"reco_z_median_max": float(np.nanmax(sr["median"])),
                           "reco_z_max_max": float(np.nanmax(sr["max"])),
                           "truth_over_sigma_Q_median_max": float(np.max(sq["median"])),
                           "truth_over_sigma_Q_max_max": float(np.max(sq["max"])),
                           "truth_over_sigma_stat_median_max": float(np.max(ss["median"])),
                           "cells_median_over_sigma_Q_above_0.5": int(np.sum(sq["median"] > 0.5)),
                           "cells_median_over_sigma_Q_above_0.2": int(np.sum(sq["median"] > 0.2))}}
    after = {p: rc.atime(p) for p in reads}
    rec["atime_moved"] = [p for p in reads if after[p] != before[p]]
    rec["seconds"] = round(time.time() - t0, 1)
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"COV2D-CLIP-PROBE done atime_moved={rec['atime_moved']} seconds={rec['seconds']} pot_scale={s:.6g}")
    for arr, rows in rec["a"].items():
        print(f"(a) {arr}: {len(rows)} universes with rows a_CV>0, a_u<=0; top: " +
              "; ".join(f"{x['universe']} rows={x['rows']} cv_w={x['cv_weight']:.4g} u_w={x['u_weight']:.4g}"
                        for x in rows[:8]))
    for t, b in rec["b"].items():
        print(f"(b) {t}: signal clipped fraction {b['signal_clipped_fraction']}, background "
              f"{b['background_clipped_fraction']}")
        print(f"(b) {t}: over cells {b['over_cells']}")
        for x in b["top10_by_median_over_sigma_Q"][:5]:
            print(f"(b) {t}: truth cell {x['cell']} |clipped|/N in sigma_Q median {x['median']:.3f} p90 "
                  f"{x['p90']:.3f} max {x['max']:.3f}; in sigma_stat median {x['median_over_sigma_stat']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
