"""COV2D clipping probe C2 (the director's requests of 2026-11-03, after C1, its erratum and the Sonnet consult):
descriptive, no verdict. Login node, nice 19, 0 node-h; the same reads and pins as clip_probe.py, every one through
O_NOATIME. The reading in ``reading`` (c2_reading.txt) was fixed before the run and decides only what the director
recommends to Joseph.

Per declared draw (300 per tune) and truth cell c, at the expected counts of COV2D-DECLARATION.md section 4.2:
* S_c      signed lambda over the reco-kept signal rows whose truth lies in c (lambda = w_reco,D x r_T x s);
* m_seen,c |sum lambda-| over the same rows: the mass lambda+ adds to the pseudo-data;
* N_c      the composite truth count, sum w_truth,D x r_T x s over mc_truth_denom's rows in c;
* m_all,c  |its negative part|: the mass that clipping the truth tree row by row would add to the truth.

(i)   option (a), the truth keeps its negative weights: o_a = m_seen / S (C1 printed m_seen / N, superseded here);
(ii)  option (1), the truth tree clipped row by row too: R = o_a - m_all / N, signed;
(iii) the nominal efficiency eps_c and N / S;
(iv)  the background: o_b = m_bkg / S_reco, the mass lambda+ adds to the background rows of reco cell c over the
      signed signal lambda of that reco cell. The background has no truth to clip, so o_b is the same under both
      options; it is put on the same-index (pT, p_par) cell's sigma (a diagonal-response approximation);
(v)   per cell, var over the 300 draws of the truth count under three compositions, first order, option (1) clipped,
      and multiplicative w = a_CV prod_j (a_uj / a_CV) with single-universe weights <= 0 floored at 0 (rows with
      a_CV <= 0 give 0; both counted), over the truth-level image of C_T's drawn blocks, sum_b Var_b(h_c): each band's
      truth-count variance under its own draw law (C_T itself does not exist before the blocks are remade). First
      order gives 1 up to the draws' sampling error, about sqrt(2/299) = 0.08, a control on the probe. Also the mean
      shift of the clipped truth, m_all / N, in sigma_Q;
(vi)  the reco/truth row match: each truth-tree row and each signal-tree row with truth in the phase space is keyed by
      a 64-bit hash of (MC, MC_pz, MC_eavail, MC_q3, MC_W, w_truth); rows of either tree beyond the other's multiplicity
      of their key are unmatched. Their counts and w_truth share per cell;
(vii) the coherent offset b^T Q_R^-1 b per draw, b = offset x E_R on the 205 cells, for o_a and for R.
Fractions are divided by the relative sigma of Q_R's stat block and of Q_R (cov2d_Q_205.npz) and summarized over each
tune's draws: median, 90th percentile and max of the magnitude, and the signed median.

  python clip_probe2.py --out clip2.json [--uni PATH] [--prep DIR] [--constraint PATH] [--q205 PATH] [--chunk N]

MEASURES: first-order offsets and variances at the expected counts. CANNOT AUTHORIZE: a verdict, a remedy, a cause.
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
sys.path.insert(0, str(HERE))
import clip_probe as cp  # noqa: E402  (its path setup puts cov2d, nd-unfolding and pv-ladder on sys.path)

c, rc = cp.c, cp.rc
N_CELLS = cp.N_CELLS
KEYS = ("MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W", "w_truth")

# The reading (c2_reading.txt), from the consult's Q3 (ANSWER-2.txt:45-47), with one number fixed where it gives a range.
R1_MEDIAN, R1_P90, R1_P90_SHARE = 0.2, 0.4, 0.90
POS_MEDIAN, POS_SHARE, POS_P90 = 0.3, 0.10, 0.6
OPT3_MEDIAN, OPT3_SHARE = 0.7, 0.20
VAR_GATE, VAR_SHARE = 0.20, 0.95
MISMATCH_BOUND = 0.05


def stats(v: np.ndarray, rel: np.ndarray) -> dict:
    """v (205 cells, draws) of signed fractions; per cell in units of rel: |v| median, p90, max and signed median."""
    z = v / rel[:, None]
    a = np.abs(z)
    med, p90, mx = np.nanmedian(a, axis=1), np.nanpercentile(a, 90, axis=1), np.nanmax(a, axis=1)
    return {"abs_median": med.tolist(), "abs_p90": p90.tolist(), "abs_max": mx.tolist(),
            "signed_median": np.nanmedian(z, axis=1).tolist(),
            "over_cells": {"largest_abs_median": float(np.nanmax(med)), "largest_abs_p90": float(np.nanmax(p90)),
                           "largest_abs_max": float(np.nanmax(mx)),
                           **{f"cells_abs_median_above_{t}": int(np.sum(med > t)) for t in (0.2, 0.3, 0.5, 0.7, 1.0)},
                           **{f"cells_abs_p90_above_{t}": int(np.sum(p90 > t)) for t in (0.4, 0.6)},
                           **{f"cells_abs_max_above_{t}": int(np.sum(mx > t)) for t in (0.5, 1.0)}}}


def row_hash(cols: list[np.ndarray]) -> np.ndarray:
    """A 64-bit key per row from the columns' float64 bit patterns (splitmix-style mixing; wraps by design)."""
    h = np.zeros(cols[0].size, np.uint64)
    with np.errstate(over="ignore"):
        for x in cols:
            h ^= np.ascontiguousarray(x, np.float64).view(np.uint64)
            h *= np.uint64(0x9E3779B97F4A7C15)
            h ^= h >> np.uint64(31)
    return h


def unmatched(ha: np.ndarray, hb: np.ndarray) -> np.ndarray:
    """For each row of a, True when it lies beyond b's multiplicity of its key (rank within equal keys, in row order)."""
    order = np.argsort(ha, kind="stable")
    hs = ha[order]
    first = np.searchsorted(hs, hs, side="left")
    rank = np.arange(hs.size) - first
    ub, cb = np.unique(hb, return_counts=True)
    pos = np.searchsorted(ub, hs)
    pos_ok = (pos < ub.size) & (ub[np.minimum(pos, ub.size - 1)] == hs)
    mult = np.where(pos_ok, cb[np.minimum(pos, ub.size - 1)], 0)
    out = np.empty(ha.size, bool)
    out[order] = rank >= mult
    return out


def band_reference(h_u: np.ndarray, w_flux: np.ndarray) -> np.ndarray:
    """sum_b Var_b of the per-universe truth counts (rows: universes in cov2d.ORDER), each with its draw law."""
    ref, k = np.zeros(h_u.shape[1]), 0
    for b in c.ORDER:
        n = c.BANDS[b]
        X = h_u[k:k + n]
        p = (w_flux / w_flux.sum()) if b == c.FLUX else np.full(n, 1.0 / n)
        mu = p @ X
        ref += p @ (X - mu) ** 2
        k += n
    return ref


def chi2_coherent(F: np.ndarray, x: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """b^T Q^-1 b per draw for b = F[:, d] * x (F: 205 x draws of fractions), by Cholesky."""
    L = np.linalg.cholesky(Q)
    B = np.nan_to_num(F) * x[:, None]
    Z = np.linalg.solve(L, B)
    return np.sum(Z * Z, axis=0)


def q3(v) -> dict:
    v = np.asarray(v, float)
    return {"median": float(np.nanmedian(v)), "p90": float(np.nanpercentile(v, 90)), "max": float(np.nanmax(v))}


def reading(rec: dict) -> dict:
    """The fixed reading, per tune and overall (c2_reading.txt). Its outcome is a recommendation to Joseph only."""
    out = {}
    worst = rec["vi"]["largest_cell_unmatched_share"]
    bounded = worst is not None and worst <= MISMATCH_BOUND
    for t, b in rec["b"].items():
        R = b["option_1"]["sigma_Q"]
        med, p90 = np.array(R["abs_median"]), np.array(R["abs_p90"])
        vr = {k: np.array(v) for k, v in b["variance_ratio"].items()}
        gate = {k: float(np.mean(np.abs(v - 1) <= VAR_GATE)) >= VAR_SHARE for k, v in vr.items()}
        q1 = bool(np.all(med <= R1_MEDIAN) and np.mean(p90 <= R1_P90) >= R1_P90_SHARE and gate["option_1_clipped"])
        pos = bool((np.mean(med > POS_MEDIAN) > POS_SHARE or np.any(p90 > POS_P90)) and gate["multiplicative"])
        opt3 = bool((np.mean(med >= OPT3_MEDIAN) >= OPT3_SHARE and not (gate["option_1_clipped"]
                                                                        or gate["multiplicative"])) or not bounded)
        pick = ("option (3)" if opt3 else "option (1)" if q1 else
                "positivity-preserving (multiplicative) composition" if pos else "no rule of the reading fires")
        out[t] = {"option_1_qualifies": q1, "positivity_preferred": pos, "option_3_applies": opt3,
                  "variance_gate_passes": gate, "mismatch_bounded": bounded, "reads": pick}
    picks = {v["reads"] for v in out.values()}
    out["overall"] = picks.pop() if len(picks) == 1 else "the tunes read differently: " + "; ".join(
        f"{t} {v['reads']}" for t, v in out.items())
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--uni", default=rc.UNI)
    ap.add_argument("--prep", default=rc.PREP)
    ap.add_argument("--constraint", default=c.CONSTRAINT)
    ap.add_argument("--q205", default=cp.Q205)
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
    if not args.no_pins and sha != cp.Q205_SHA256:
        raise c.Refusal(f"cov2d_Q_205.npz sha256 {sha}")
    q = np.load(io.BytesIO(qbytes))
    cells205, x205, Q205 = np.asarray(q["cells"], int), np.asarray(q["x"], float), np.asarray(q["Q"], float)
    rel = {k: np.sqrt(np.diag(q[k])) / x205 for k in ("stat", "Q")}

    tunes = list(rc.TUNES)
    idx = {t: rc.draw_index(c.declared_draws(t, w_flux)) for t in tunes}
    S = {t: rc.selection(idx[t], c.N_UNIVERSES) for t in tunes}
    nd_ = {t: idx[t].shape[0] for t in tunes}
    edges = [pvl_lib.FINE[a] for a in pvl_lib.AXES5]

    with rc.open_noatime(args.uni) as fh:
        f = uproot.open(fh)
        s = float(f["dataPOTUsed"].member("fVal")) / float(f["mcPOTUsed"].member("fVal"))
        rec["pot_scale"] = s
        td, ts, tb = f["mc_truth_denom"], f["mc_signal_reco"], f["mc_background"]
        a = td.arrays(list(KEYS), library="np")
        key_d = [np.asarray(a[k], np.float64) for k in KEYS]
        gen_d = np.stack(key_d[:5], axis=1)
        w_d = key_d[5]
        cell_d = rc.truth_cell(gen_d[:, 0], gen_d[:, 1])
        h_d = row_hash(key_d)
        del a, key_d
        a = ts.arrays(list(KEYS) + ["sim", "sim_pz", "sim_pass"], library="np")
        key_s = [np.asarray(a[k], np.float64) for k in KEYS]
        gen_s = np.stack(key_s[:5], axis=1)
        wt_s = key_s[5]
        tcell_s = rc.truth_cell(gen_s[:, 0], gen_s[:, 1])
        kept_s, rcell_s = cp.reco_cell(np.asarray(a["sim"], float), np.asarray(a["sim_pz"], float), a["sim_pass"])
        h_s = row_hash(key_s)
        del a, key_s

        # (vi) the row match, truth tree against the signal tree's rows with truth in the phase space
        in_ps = tcell_s >= 0
        um_d = unmatched(h_d, h_s[in_ps])
        um_s = np.zeros(h_s.size, bool)
        um_s[in_ps] = unmatched(h_s[in_ps], h_d)
        del h_d, h_s
        wd, ws = np.nan_to_num(w_d), np.nan_to_num(wt_s)
        tot_d = np.bincount(cell_d[cell_d >= 0], weights=wd[cell_d >= 0], minlength=N_CELLS)
        tot_s = np.bincount(tcell_s[in_ps], weights=ws[in_ps], minlength=N_CELLS)
        sh_d = np.bincount(cell_d[um_d & (cell_d >= 0)], weights=wd[um_d & (cell_d >= 0)], minlength=N_CELLS)
        sh_s = np.bincount(tcell_s[um_s], weights=ws[um_s], minlength=N_CELLS)
        with np.errstate(invalid="ignore", divide="ignore"):
            share_d, share_s = (sh_d / tot_d)[cells205], (sh_s / tot_s)[cells205]
        worst = float(np.nanmax(np.abs(np.concatenate([share_d, share_s]))))
        n_keys = um_d.size + int(in_ps.sum())
        rec["vi"] = {"truth_rows": int(um_d.size), "truth_rows_unmatched": int(um_d.sum()),
                     "signal_rows_in_phase_space": int(in_ps.sum()), "signal_rows_unmatched": int(um_s.sum()),
                     "truth_unmatched_share_per_cell": share_d.tolist(),
                     "signal_unmatched_share_per_cell": share_s.tolist(),
                     "largest_cell_unmatched_share": worst if np.isfinite(worst) else None,
                     "hash": f"64-bit; expected chance collisions about {n_keys ** 2 / 2 ** 65:.1e}"}

        seen = np.where(kept_s, tcell_s, -1)
        eps_num = np.bincount(seen[seen >= 0], weights=ws[seen >= 0], minlength=N_CELLS)
        nd = gen_d.shape[0]
        gen = np.concatenate([gen_d, gen_s])
        del gen_d, gen_s, wt_s, ws
        wcat = np.concatenate([w_d, np.zeros(gen.shape[0] - nd)])
        r_d, r_s = {}, {}
        for t in tunes:
            r = s5e_deform.ratio_weight(gen, edges, wcat, ratios[t], 1.0)
            r_d[t], r_s[t] = r[:nd], r[nd:]
        del gen, wcat

        keys = ("S", "m_seen", "N", "m_all", "N_mult", "S_reco", "m_bkg", "bkg")
        acc = {t: {k: np.zeros((N_CELLS, nd_[t])) for k in keys} for t in tunes}
        h_u = {t: np.zeros((c.N_UNIVERSES, N_CELLS)) for t in tunes}
        mult_rows = {"cv_nonpositive": 0, "a_universe_floored": 0}
        a = tb.arrays(["sim_background", "sim_background_pz", "sim_background_pass"], library="np")
        kept_b, rcell_b = cp.reco_cell(np.asarray(a["sim_background"], float),
                                       np.asarray(a["sim_background_pz"], float), a["sim_background_pass"])
        del a
        ones_b = {t: np.ones(tb.num_entries) for t in tunes}
        for tree, pre, cellv, rr, key_sum, key_neg, keep, cell2, key2 in (
                (td, "w_truth", cell_d, r_d, "N", "m_all", None, None, None),
                (ts, "w_reco", seen, r_s, "S", "m_seen", kept_s, rcell_s, "S_reco"),
                (tb, "w_bkg", rcell_b, ones_b, "bkg", "m_bkg", kept_b, None, None)):
            cols = [pre] + rc.universe_columns(pre)
            for start in range(0, tree.num_entries, args.chunk):
                stop = min(start + args.chunk, tree.num_entries)
                a = tree.arrays(cols, entry_start=start, entry_stop=stop, library="np")
                W = np.stack([np.nan_to_num(np.asarray(a[k], np.float64), nan=0.0, posinf=0.0, neginf=0.0)
                              for k in cols], axis=1)
                cv, U = W[:, 0], W[:, 1:]
                M = cp.onehot(cellv[start:stop])
                if key_sum == "N":
                    pos = cv > 0
                    mult_rows["cv_nonpositive"] += int(np.sum(~pos))
                    mult_rows["a_universe_floored"] += int(np.sum(pos & np.any(U <= 0, axis=1)))
                    with np.errstate(divide="ignore", invalid="ignore"):
                        L = np.where(pos[:, None] & (U > 0), np.log(np.where(U > 0, U, 1.0)) -
                                     np.log(np.where(pos, cv, 1.0))[:, None], 0.0)
                    Z = (pos[:, None] & (U <= 0)).astype(np.float64)
                for t in tunes:
                    rs_ = (rr[t][start:stop] * s)
                    lam = (cv[:, None] + (U - cv[:, None]) @ S[t]) * rs_[:, None]
                    if keep is not None:
                        lam[~keep[start:stop]] = 0.0
                    acc[t][key_sum] += M @ lam
                    acc[t][key_neg] -= M @ np.minimum(lam, 0.0)
                    if cell2 is not None:
                        acc[t][key2] += cp.onehot(cell2[start:stop]) @ lam
                    if key_sum == "N":
                        prod = np.where(pos[:, None] & ((Z @ S[t]) == 0),
                                        np.exp(np.log(np.where(pos, cv, 1.0))[:, None] + L @ S[t]), 0.0)
                        acc[t]["N_mult"] += M @ (prod * rs_[:, None])
                        h_u[t] += (M @ (U * rs_[:, None])).T
    rec["v_multiplicative_rows"] = mult_rows

    eps_den = np.bincount(cell_d[cell_d >= 0], weights=np.nan_to_num(w_d)[cell_d >= 0], minlength=N_CELLS)
    rec["efficiency"] = {"eps_c": (eps_num / np.where(eps_den > 0, eps_den, np.nan))[cells205].tolist(),
                         "cells205": cells205.tolist()}
    rec["b"] = {}
    for t in tunes:
        A = {k: v[cells205] for k, v in acc[t].items()}
        with np.errstate(invalid="ignore", divide="ignore"):
            o_a = A["m_seen"] / A["S"]
            o_1 = o_a - A["m_all"] / A["N"]
            o_b = A["m_bkg"] / A["S_reco"]
            n_over_s = A["N"] / A["S"]
            ref = band_reference(h_u[t], w_flux)[cells205]
            vr = {"first_order": np.var(A["N"], axis=1, ddof=1) / ref,
                  "option_1_clipped": np.var(A["N"] + A["m_all"], axis=1, ddof=1) / ref,
                  "multiplicative": np.var(A["N_mult"], axis=1, ddof=1) / ref}
            shift = np.mean(A["m_all"] / A["N"], axis=1) / rel["Q"]
        rec["b"][t] = {
            "option_a": {"sigma_stat": stats(o_a, rel["stat"]), "sigma_Q": stats(o_a, rel["Q"])},
            "option_1": {"sigma_stat": stats(o_1, rel["stat"]), "sigma_Q": stats(o_1, rel["Q"])},
            "background_both_options": {"sigma_stat": stats(o_b, rel["stat"]), "sigma_Q": stats(o_b, rel["Q"])},
            "N_over_S_median": np.nanmedian(n_over_s, axis=1).tolist(),
            "variance_ratio": {k: v.tolist() for k, v in vr.items()},
            "variance_ratio_summary": {k: {"median": float(np.nanmedian(v)), "min": float(np.nanmin(v)),
                                           "max": float(np.nanmax(v)),
                                           "share_within_20pct": float(np.mean(np.abs(v - 1) <= VAR_GATE))}
                                       for k, v in vr.items()},
            "clipped_truth_mean_shift_sigma_Q": {"per_cell": shift.tolist(), **q3(np.abs(shift))},
            "vii_chi2_coherent_Q": {"option_a": q3(chi2_coherent(o_a, x205, Q205)),
                                    "option_1": q3(chi2_coherent(o_1, x205, Q205))}}
    rec["reading"] = reading(rec)
    after = {p: rc.atime(p) for p in reads}
    rec["atime_moved"] = [p for p in reads if after[p] != before[p]]
    rec["seconds"] = round(time.time() - t0, 1)
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"COV2D-CLIP-PROBE2 done atime_moved={rec['atime_moved']} seconds={rec['seconds']} pot_scale={s:.6g}")
    e = np.array(rec["efficiency"]["eps_c"])
    print(f"(iii) eps_c over the 205 cells: min {np.nanmin(e):.3f} median {np.nanmedian(e):.3f} max {np.nanmax(e):.3f}")
    print(f"(vi) {({k: v for k, v in rec['vi'].items() if not k.endswith('per_cell')})}")
    print(f"(v) multiplicative rows: {mult_rows}")
    for t, b in rec["b"].items():
        for opt in ("option_a", "option_1", "background_both_options"):
            for unit in ("sigma_stat", "sigma_Q"):
                print(f"{t} {opt} {unit}: {b[opt][unit]['over_cells']}")
        print(f"{t} (v) variance ratio: {b['variance_ratio_summary']}")
        print(f"{t} (v) clipped truth mean shift, sigma_Q: { {k: v for k, v in b['clipped_truth_mean_shift_sigma_Q'].items() if k != 'per_cell'} }")
        print(f"{t} (vii) b^T Q^-1 b: {b['vii_chi2_coherent_Q']}")
    print(f"C2-READING {json.dumps(rec['reading'], sort_keys=True)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
