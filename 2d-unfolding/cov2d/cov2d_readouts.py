"""COV2D's descriptive readouts at a truth (COV2D-DECLARATION.md section 6; no verdict): the spread alone, the bias,
the predicted offset of the un-centred draws, the leave-out-MEC variant C_T- (the director's R3), the realization
check, and the redesign decision's additions applied to 2D: (i) the cross terms (a login-node CLI here, over the 600
declared draws) and (ii) the clipping residual R_c with its fixed 0.5 sigma_c reading.

* C_T-'s C_model- is "constructed from the committed shift matrix, not a named part-C product" (cov2d_blocks.c_model);
  it is graded with 1B's ``fd_1b_mc.grade`` against its own null and changes no verdict.
* (i) "product composition" is C2's: a_CV prod_j (a_uj / a_CV) on rows with a_CV > 0 and every drawn universe weight
  > 0, and 0 elsewhere (clip_probe2.py:19-20, 273-292).
* (ii) R_c = m_seen,c / S_c - m_all,c / N_c per toy and truth cell, in sigma_c as R_c x_true,c / sigma_c; missing where
  S_c <= 0 or N_c <= 0 (counted). A flagged cell whose median |R_c| over its toys exceeds 0.5 sigma_c reads "the
  clipping may explain this cell's flag"; the verdict is unchanged. C2 predicts the reading will not fire (its largest
  per-cell median is 0.043 sigma_Q at G18 and 0.042 sigma_Q at AR23).

MEASURES: descriptive quantities. CANNOT AUTHORIZE: a verdict, or a change to C_T or the rule.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, REPO / "nd-unfolding"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402

READING_SIGMA = 0.5
C2_PREDICTION = {"G18": 0.043, "AR23": 0.042}   # C2's largest per-cell median |R|, in sigma_Q (c2_reading.txt)
GENIE_MEC_READING = "its coverage in cells {cells} rests on the GENIE + MEC shift"


def spread_alone(E: np.ndarray, C_T: np.ndarray, C_model_abs: np.ndarray) -> dict:
    """Pulls and the in-interval fraction against C_T without C_model."""
    sigma = np.sqrt(np.diag(C_T - C_model_abs))
    z = E / sigma
    return {"p_hat": np.mean(np.abs(E) <= sigma, axis=0).tolist(), "pull_mean": z.mean(axis=0).tolist(),
            "pull_sd": z.std(axis=0, ddof=1).tolist()}


def bias(E: np.ndarray, sigma: np.ndarray) -> list:
    """The toys' mean error per cell in sigma_c."""
    return (E.mean(axis=0) / sigma).tolist()


def predicted_offset(bands: dict, w_flux: np.ndarray, x_hat_T: np.ndarray) -> np.ndarray:
    """-sum_b sum_u p_u (x_hat_u(T) - x_hat_T) over the drawn universe bands, with their draw probabilities (1B §5.4).
    The lateral surrogate is centred by construction and adds nothing."""
    off = np.zeros_like(np.asarray(x_hat_T, np.float64))
    for b in c.ORDER:
        X = np.asarray(bands[b], np.float64)
        p = np.asarray(w_flux, float) / np.sum(w_flux) if b == c.FLUX else np.full(X.shape[0], 1.0 / X.shape[0])
        off += p @ X - x_hat_T
    return -off


def leave_out_mec(E, blocks: dict, bands: dict, minos_x, w_flux, grade_CT: dict, cells, n_mc: int | None = None) -> dict:
    """C_T- graded against its own null; the GENIE + MEC reading where C_T covers and C_T- flags."""
    import cov2d_null as cn
    import fd_1b_mc as mc
    import fd_1b_null as nl
    C_minus = blocks["C_T_minus"]
    model_minus_abs = C_minus - (blocks["C_T"] - blocks["C_model_abs"])
    gauss = blocks["C_stat"] + blocks["C_norm"] + blocks["C08"] + model_minus_abs
    null = nl.null_contents(cn.laws_at_T(bands, minos_x, w_flux), gauss, C_minus,
                            n_mc=n_mc or nl.N_MC, seed=c.NULL_SEED)
    g = mc.grade(E, C_minus, null)
    cells = [int(x) for x in cells]
    newly = [cells[i] for i in range(len(cells)) if g["cell_flag"][i] and not grade_CT["cell_flag"][i]]
    out = {"grade": g, "flagged_under_minus_not_under_C_T": newly, "changes_no_verdict": True}
    if grade_CT["verdict"] == "COVERS" and g["verdict"] == "UNDER-COVERS":
        out["reading"] = GENIE_MEC_READING.format(cells=newly)
    return out


def realization_check(x_hat_T: np.ndarray, x_true_T: np.ndarray, sigma: np.ndarray) -> dict:
    d = (np.asarray(x_hat_T, float) - np.asarray(x_true_T, float)) / sigma
    return {"per_cell_sigma": d.tolist(), "max_abs": float(np.abs(d).max()), "median_abs": float(np.median(np.abs(d)))}


def clipping_residual(cells_npz: dict, toy_index: list, rep: np.ndarray, x_true: np.ndarray, sigma: np.ndarray,
                      C_T: np.ndarray, flagged_cells: list, truth: str) -> dict:
    """Section 6 (ii) over a truth's toys. ``cells_npz`` holds step A's per-nature arrays on the 224 flat cells;
    ``toy_index`` their rows for the toys, in seed order; ``rep`` E_R's 205 flat cells; ``x_true`` (toys x 205)."""
    import fd_1b_null as nl
    rep = np.asarray(rep, int)
    S, m_seen = cells_npz["S"][toy_index][:, rep], cells_npz["m_seen"][toy_index][:, rep]
    N, m_all = cells_npz["N"][toy_index][:, rep], cells_npz["m_all"][toy_index][:, rep]
    ok = (S > 0) & (N > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        R = np.where(ok, m_seen / np.where(S > 0, S, 1.0) - m_all / np.where(N > 0, N, 1.0), np.nan)
    Rs = R * x_true / sigma
    med = np.array([np.nanmedian(np.abs(Rs[:, i])) if ok[:, i].any() else np.nan for i in range(rep.size)])
    vec = np.where(ok, R * x_true, 0.0)          # R = (R_c x_true,c); a missing R_c enters as 0, counted below
    coherent = nl.chi2_nonnull(vec, C_T)[0]
    added_b = -cells_npz["neg_reco_background"][toy_index][:, rep]
    S_reco = cells_npz["S_reco"][toy_index][:, rep]
    with np.errstate(divide="ignore", invalid="ignore"):
        ob = np.where(S_reco > 0, added_b / np.where(S_reco > 0, S_reco, 1.0), np.nan) * x_true / sigma
    cells = [int(x) for x in rep]
    fires = [cl for cl in flagged_cells if cl in cells and np.nan_to_num(med[cells.index(cl)]) > READING_SIGMA]
    out = {"median_abs_R_sigma": med.tolist(), "missing_per_cell": (~ok).sum(axis=0).tolist(),
           "missing_total": int((~ok).sum()), "coherent_offset": {"median": float(np.median(coherent)),
                                                                   "max": float(coherent.max())},
           "background_offset_sigma": {"median_abs": float(np.nanmedian(np.abs(ob))), "max_abs": float(np.nanmax(np.abs(ob)))},
           "reading_fires_in": fires, "reading": {cl: "the clipping may explain this cell's flag" for cl in fires},
           "c2_prediction_sigma_Q": C2_PREDICTION[truth],
           "c2_prediction": "C2 predicts this reading will not fire"}
    if c.OUTLIER_CELL in cells:
        col = np.abs(Rs[:, cells.index(c.OUTLIER_CELL)])
        out["outlier_cell"] = {"cell": c.OUTLIER_CELL, "max_abs_R_sigma": float(np.nanmax(col)) if np.any(~np.isnan(col)) else None,
                               "median_abs_R_sigma": float(np.nanmedian(col)) if np.any(~np.isnan(col)) else None}
    return out


def product_compose(cv: np.ndarray, univ: list) -> np.ndarray:
    """C2's product composition: a_CV prod_j (a_uj / a_CV) where a_CV > 0 and every drawn a_uj > 0, else 0."""
    cv = np.asarray(cv, np.float64)
    U = np.stack([np.asarray(u, np.float64) for u in univ])
    ok = (cv > 0) & np.all(U > 0, axis=0)
    out = np.zeros_like(cv)
    out[ok] = cv[ok] * np.prod(U[:, ok] / cv[ok], axis=0)
    return out


def main(argv=None) -> int:
    """(i) on a login node: python cov2d_readouts.py cross-terms --out FILE (reads $UNI once, O_NOATIME, both truths)."""
    import cov2d_pseudo as ps
    import cov2d_receipt as rc
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("cross-terms")
    p.add_argument("--out", required=True)
    p.add_argument("--uni", default=rc.UNI)
    p.add_argument("--prep", default=rc.PREP)
    p.add_argument("--constraint", default=c.CONSTRAINT)
    p.add_argument("--chunk", type=int, default=rc.CHUNK)
    p.add_argument("--no-pins", action="store_true", help="tests only")
    a = ap.parse_args(argv)
    import uproot
    import clip_probe as cp
    import fd_1b_toys
    t0 = time.time()
    reads = [a.uni, a.constraint] + [str(Path(a.prep) / fd_1b_toys.TRUTHS[rc.TUNES[t]]) for t in rc.TUNES]
    before = {q: os.stat(q).st_atime_ns for q in reads}
    text, sha = rc.read_noatime(a.constraint)
    if not a.no_pins and sha != c.CONSTRAINT_SHA256:
        raise c.Refusal(f"constraint sha256 {sha}")
    w_flux = c.flux_weights(text.decode())
    ratios = {}
    for t in rc.TUNES:
        data, sha = rc.read_noatime(str(Path(a.prep) / fd_1b_toys.TRUTHS[rc.TUNES[t]]))
        if not a.no_pins and sha != fd_1b_toys.committed_ratio_sha256(rc.TUNES[t]):
            raise c.Refusal(f"{t} ratio sha256 {sha}")
        ratios[t] = json.loads(data)
    draws = {t: c.declared_draws(t, w_flux) for t in rc.TUNES}
    pos = ps.column_positions()
    n_cells = cp.N_CELLS
    acc = {t: {"first": np.zeros((len(draws[t]), n_cells)), "product": np.zeros((len(draws[t]), n_cells))}
           for t in rc.TUNES}
    with rc.open_noatime(a.uni) as fh:
        f = uproot.open(fh)
        s = ps.read_pot(f)
        s = s[0] / s[1]
        ts, tt, tb = f["mc_signal_reco"], f["mc_truth_denom"], f["mc_background"]
        gt = tt.arrays(list(ps.TRUTH_VARS) + ["w_truth"], library="np")
        gen_t = np.stack([np.asarray(gt[k], np.float64) for k in ps.TRUTH_VARS], axis=1)
        w_t, _ = ps.finite(np.asarray(gt["w_truth"], np.float64))
        gs = ts.arrays(list(ps.TRUTH_VARS) + list(ps.SIG_RECO), library="np")
        gen_s = np.stack([np.asarray(gs[k], np.float64) for k in ps.TRUTH_VARS], axis=1)
        r_s = {t: ps.r_rows(ratios[t], gen_t, w_t, gen_s)[1] for t in rc.TUNES}
        kept_s, rcell_s = cp.reco_cell(np.asarray(gs["sim"], float), np.asarray(gs["sim_pz"], float), gs["sim_pass"])
        gb = tb.arrays(list(ps.BKG_RECO), library="np")
        kept_b, rcell_b = cp.reco_cell(np.asarray(gb["sim_background"], float),
                                       np.asarray(gb["sim_background_pz"], float), gb["sim_background_pass"])
        del gt, gen_t, gs, gen_s, gb
        for tree, prefix, kept, rcell in ((ts, "w_reco", kept_s, rcell_s), (tb, "w_bkg", kept_b, rcell_b)):
            cols = [prefix] + rc.universe_columns(prefix)
            for start in range(0, tree.num_entries, a.chunk):
                stop = min(start + a.chunk, tree.num_entries)
                arr = tree.arrays(cols, entry_start=start, entry_stop=stop, library="np")
                cv, _ = ps.finite(np.asarray(arr[prefix], np.float64))
                U, _ = ps.finite(np.stack([np.asarray(arr[k], np.float64) for k in cols[1:]], axis=1))
                del arr
                cell = np.where(kept[start:stop], rcell[start:stop], -1)
                okc = cell >= 0
                for t in rc.TUNES:
                    r = r_s[t][start:stop] if prefix == "w_reco" else np.ones(stop - start)
                    for k, d in enumerate(draws[t]):
                        univ = [U[:, pos[u]] for u in d.universes]
                        first = c.compose(cv, univ) * r * s
                        prod = product_compose(cv, univ) * r * s
                        acc[t]["first"][k] += np.bincount(cell[okc], weights=first[okc], minlength=n_cells)
                        acc[t]["product"][k] += np.bincount(cell[okc], weights=prod[okc], minlength=n_cells)
    rec = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "host": os.uname().nodename, "draws": {}}
    for t in rc.TUNES:
        F, P = acc[t]["first"], acc[t]["product"]
        with np.errstate(divide="ignore", invalid="ignore"):
            z = np.where(F > 0, (P - F) / np.sqrt(np.where(F > 0, F, 1.0)), np.nan)
        rec["draws"][t] = {"n": int(F.shape[0]), "median_abs": float(np.nanmedian(np.abs(z))),
                           "p90_abs": float(np.nanpercentile(np.abs(z), 90)), "max_abs": float(np.nanmax(np.abs(z))),
                           "per_cell_median_abs": np.nanmedian(np.abs(z), axis=0).tolist()}
    after = {q: os.stat(q).st_atime_ns for q in reads}
    rec["atime_moved"] = [q for q in reads if after[q] != before[q]]
    rec["seconds"] = round(time.time() - t0, 1)
    Path(a.out).write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"COV2D-CROSS-TERMS draws={sum(v['n'] for v in rec['draws'].values())} atime_moved={len(rec['atime_moved'])}")
    return 0 if not rec["atime_moved"] else 3


if __name__ == "__main__":
    sys.exit(main())
