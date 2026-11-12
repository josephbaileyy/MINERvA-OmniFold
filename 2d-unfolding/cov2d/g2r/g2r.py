"""COV2D-G2R (COV2D-G2R-DECLARATION.md): the pure functions behind the misses-approximation rebuild and the regrade.

No file is opened here. The prepare (g2r_prepare.py) and the readout (g2r_readout.py) do the reads; this module holds
what they compute, so each rule is tested on synthetic arrays.

* The miss map (§1, §9; P5's build_miss_override.py, extended): in each playlist block of $UNI, the appended truth-only
  miss rows of ``mc_signal_reco`` are the block's last ``nTruthOnlyMisses`` rows, an ordered subsequence of the block's
  ``mc_truth_denom`` rows with identical (MC, MC_pz, w_truth). ``build_map`` finds that subsequence by exact key, with
  P5's fail-closed checks, and returns one universe-independent map: global miss-row indices and the matching global
  truth-row indices. ``universe_check`` adds P5's per-universe checks for one universe column, and ``override`` turns
  the map plus one universe's truth column into P5's ``w_override`` (NaN except on miss rows). For any universe this
  equals what P5's builder writes for it (``test_g2r.Map.test_override_equals_p5_builder_semantics``).
* The readings (§3): ``epsilon`` (the covariance-normalized change in the retained eigensystem, the consult's item C),
  the coupling to the discarded directions, ``corr_change`` and ``rank``.
* C_T' (§4): ``c_t_prime`` rebuilds the universe block from corrected universe bands with the rollup's own
  ``universe_block`` and keeps every other block of a committed blocks_<T>.npz, in cov2d_blocks.assemble's arithmetic.
"""
from __future__ import annotations

import numpy as np

SCHEMA = "cov2d-g2r/1"
N_CELLS = 205
RANK_REL = 1e-12          # the grade's non-null rule (COV2D-DECLARATION §5.1; fd_1b_null.RANK_REL)
RANKS = (73, 139)         # the truncation readings (T2A; the declaration §3)
SENTINEL = -9999.0        # a miss row's sim (P5 DESIGN §2, check 1)


class Refusal(RuntimeError):
    """An input is not what the step is defined on: INVALID, reported unrepaired."""


# ----------------------------------------------------------------------------------------------------------- the map
def keys(cols) -> np.ndarray:
    """Rows of float64 columns as fixed-width void keys, so equality is bitwise (P5's ``keys``)."""
    a = np.ascontiguousarray(np.stack([np.asarray(c, np.float64) for c in cols], axis=1))
    return a.view(f"V{8 * a.shape[1]}").ravel()


def sorted_equal(a: np.ndarray, b: np.ndarray) -> bool:
    return a.size == b.size and bool(np.array_equal(np.sort(a), np.sort(b)))


def build_map(S: dict, T: dict, blocks: list) -> tuple[np.ndarray, np.ndarray, dict]:
    """The miss map. ``S``: mc_signal_reco's MC, MC_pz, w_truth, w_reco, sim, sim_pass (int); ``T``: mc_truth_denom's
    MC, MC_pz, w_truth; ``blocks``: [(name, n_entries, n_misses)] in hadd order. Raises Refusal on any failed check;
    returns (miss_rows, truth_rows, report)."""
    rep = {"blocks": [], "checks": {}}

    def check(name, ok, value=None):
        rep["checks"][name] = {"pass": bool(ok), **({"value": value} if value is not None else {})}
        if not ok:
            raise Refusal(f"miss map: {name} failed ({value})")

    N = len(S["MC"])
    check("n_signal_eq_n_truth", N == len(T["MC"]), [N, len(T["MC"])])
    check("n_signal_eq_sum_blocks", N == sum(n for _, n, _ in blocks), [N, sum(n for _, n, _ in blocks)])
    miss_rows, truth_rows = [], []
    o = 0
    for name, n, m in blocks:
        if not (0 <= m <= n):
            check(f"{name}_misses_within_block", False, [n, m])
        r = n - m
        tail = slice(o + r, o + n)
        head = slice(o, o + r)
        check(f"{name}_tail_sim_pass_0", bool(np.all(np.asarray(S["sim_pass"][tail]) == 0)))
        check(f"{name}_tail_sim_sentinel", bool(np.all(np.asarray(S["sim"][tail], np.float64) == SENTINEL)))
        check(f"{name}_tail_w_reco_eq_w_truth", bool(np.array_equal(np.asarray(S["w_reco"][tail], np.float64),
                                                                    np.asarray(S["w_truth"][tail], np.float64))))
        tk = keys([T["MC"][o:o + n], T["MC_pz"][o:o + n], T["w_truth"][o:o + n]])
        sk = keys([S["MC"][tail], S["MC_pz"][tail], S["w_truth"][tail]])
        order = np.argsort(tk, kind="stable")
        tks = tk[order]
        check(f"{name}_truth_keys_unique", bool(np.all(tks[1:] != tks[:-1])))
        pos = np.minimum(np.searchsorted(tks, sk), max(n - 1, 0))
        found = (tks[pos] == sk) if n else np.zeros(0, bool)
        check(f"{name}_every_miss_found", bool(found.all()), int((~found).sum()))
        tidx = order[pos] if m else np.zeros(0, np.int64)
        check(f"{name}_subsequence_order", bool(np.all(np.diff(tidx) > 0)))
        comp = np.ones(n, bool)
        comp[tidx] = False
        check(f"{name}_complement_eq_reco_rows_cv", sorted_equal(
            keys([T["MC"][o:o + n][comp], T["MC_pz"][o:o + n][comp], T["w_truth"][o:o + n][comp]]),
            keys([S["MC"][head], S["MC_pz"][head], S["w_truth"][head]])))
        rep["blocks"].append({"file": name, "offset": o, "n": int(n), "misses": int(m),
                              "head_sim_pass_0": int(np.sum(np.asarray(S["sim_pass"][head]) == 0))})
        miss_rows.append(np.arange(o + r, o + n, dtype=np.int64))
        truth_rows.append(o + np.asarray(tidx, np.int64))
        o += n
    mr = np.concatenate(miss_rows) if miss_rows else np.zeros(0, np.int64)
    tr = np.concatenate(truth_rows) if truth_rows else np.zeros(0, np.int64)
    rep["n_signal"], rep["n_miss"] = int(N), int(mr.size)
    return mr, tr, rep


def universe_check(S: dict, T: dict, wt_sig_u, wr_sig_u, wt_truth_u, miss_rows, truth_rows, blocks: list) -> dict:
    """P5's per-universe checks for one universe column: the miss rows carry the proxy (w_truth_<u> = w_reco_<u> =
    w_truth on every miss row of mc_signal_reco), and per block the truth rows outside the map equal the reco-loop rows
    as exact multisets of (MC, MC_pz, w_truth, w_truth_<u>). Returns the record; raises Refusal on a failure."""
    wt_s, wr_s, wt_t = (np.asarray(a, np.float64) for a in (wt_sig_u, wr_sig_u, wt_truth_u))
    w = np.asarray(S["w_truth"], np.float64)
    if not (np.array_equal(wt_s[miss_rows], w[miss_rows]) and np.array_equal(wr_s[miss_rows], w[miss_rows])):
        raise Refusal("universe check: a miss row's universe weight is not the CV proxy")
    is_miss = np.zeros(len(w), bool)
    is_miss[miss_rows] = True
    in_map = np.zeros(len(wt_t), bool)
    in_map[truth_rows] = True
    o = 0
    for name, n, m in blocks:
        sl = slice(o, o + n)
        t_rest = ~in_map[sl]
        s_head = ~is_miss[sl]
        if not sorted_equal(
                keys([np.asarray(T["MC"][sl])[t_rest], np.asarray(T["MC_pz"][sl])[t_rest],
                      np.asarray(T["w_truth"][sl])[t_rest], wt_t[sl][t_rest]]),
                keys([np.asarray(S["MC"][sl])[s_head], np.asarray(S["MC_pz"][sl])[s_head], w[sl][s_head],
                      wt_s[sl][s_head]])):
            raise Refusal(f"universe check: {name}'s complement differs from its reco rows on the universe column")
        o += n
    true = wt_t[truth_rows]
    proxy = w[miss_rows]
    changed = true != proxy
    return {"n_miss": int(miss_rows.size), "n_changed": int(np.count_nonzero(changed)),
            "identity": bool(not changed.any()),
            "sum_true_over_proxy": float(true.sum() / proxy.sum()) if proxy.size and proxy.sum() != 0 else None}


def override(miss_rows, truth_rows, wt_truth_u, n_signal: int) -> np.ndarray:
    """P5's w_override for one universe: NaN on every signal row except the miss rows, which carry the universe truth
    weight of the same event from mc_truth_denom."""
    out = np.full(int(n_signal), np.nan)
    out[np.asarray(miss_rows, np.int64)] = np.asarray(wt_truth_u, np.float64)[np.asarray(truth_rows, np.int64)]
    return out


def p5_override(S: dict, T: dict, blocks: list, truth_u) -> np.ndarray:
    """P5's build_miss_override.py loop (state/2d-closeout/stageB/diagnostics/p5/build_miss_override.py, blob
    7f346e1a), transcribed without its checks: per block, the tail rows matched by exact key to the truth rows, and
    w_override = the truth tree's universe column there. The reference the map's override is compared with (G11)."""
    N = len(S["MC"])
    w = np.full(N, np.nan)
    truth_u = np.asarray(truth_u, np.float64)
    o = 0
    for _, n, m in blocks:
        r = n - m
        tk = keys([T["MC"][o:o + n], T["MC_pz"][o:o + n], T["w_truth"][o:o + n]])
        sk = keys([S["MC"][o + r:o + n], S["MC_pz"][o + r:o + n], S["w_truth"][o + r:o + n]])
        order = np.argsort(tk, kind="stable")
        pos = np.minimum(np.searchsorted(tk[order], sk), max(n - 1, 0))
        w[o + r:o + n] = truth_u[o:o + n][order[pos]]
        o += n
    return w


def spot_check(S: dict, T: dict, blocks: list, miss_rows, truth_rows, columns: dict) -> dict:
    """G11 (the director's condition on amendment 1 §2): for each named truth column, the map's override equals P5's
    builder loop bitwise (the NaN pattern and every finite value). Raises Refusal on any difference."""
    out = {}
    N = len(S["MC"])
    for name, col in columns.items():
        a = override(miss_rows, truth_rows, col, N)
        b = p5_override(S, T, blocks, col)
        same_nan = bool(np.array_equal(np.isnan(a), np.isnan(b)))
        equal = same_nan and bool(np.array_equal(a[~np.isnan(a)], b[~np.isnan(b)]))
        out[name] = {"equal": equal, "n_finite": int(np.isfinite(a).sum())}
        if not equal:
            raise Refusal(f"G11: the map's override differs from P5's builder for {name}")
    return out


# ------------------------------------------------------------------------------------------------------ the readings
def retained(C: np.ndarray, rel: float = RANK_REL) -> tuple[np.ndarray, np.ndarray]:
    """C's eigenpairs on its non-null subspace (eigenvalues above rel x the largest), by descending eigenvalue."""
    C = np.asarray(C, np.float64)
    lam, V = np.linalg.eigh(0.5 * (C + C.T))
    keep = lam > rel * lam.max()
    order = np.argsort(lam[keep])[::-1]
    return lam[keep][order], V[:, keep][:, order]


def epsilon(C: np.ndarray, dC: np.ndarray, k: int | None = None) -> dict:
    """The consult's item C: eps = || L^-1/2 U^T dC U L^-1/2 ||_2 on C's retained eigensystem (or its k largest
    directions), and the coupling to the discarded directions, || P_perp dC U L^-1/2 ||_2, beside it."""
    lam, U = retained(C)
    if k is not None:
        if k > lam.size:
            raise Refusal(f"epsilon: {k} directions requested, {lam.size} retained")
        lam, U = lam[:k], U[:, :k]
    dC = np.asarray(dC, np.float64)
    W = U / np.sqrt(lam)
    M = W.T @ dC @ W
    P = np.eye(C.shape[0]) - U @ U.T
    return {"directions": int(lam.size), "eps": float(np.linalg.norm(0.5 * (M + M.T), 2)),
            "coupling_to_discarded": float(np.linalg.norm(P @ dC @ W, 2))}


def corr(C: np.ndarray) -> np.ndarray:
    s = np.sqrt(np.diag(np.asarray(C, np.float64)))
    return np.asarray(C, np.float64) / np.outer(s, s)


def corr_change(C_old: np.ndarray, C_new: np.ndarray) -> dict:
    d = np.abs(corr(C_new) - corr(C_old))
    iu = np.triu_indices(d.shape[0], 1)
    return {"max_abs_delta_rho": float(d[iu].max()), "median_abs_delta_rho": float(np.median(d[iu]))}


def rank(C: np.ndarray, rel: float = RANK_REL) -> int:
    return int(retained(C, rel)[0].size)


def readings(C_old: np.ndarray, C_new: np.ndarray, metrics=None, x=None, F=None) -> dict:
    """§3's readings of C_new against C_old: eps at the retained rank and at RANKS, off-diagonal changes, rank, and, if
    ``metrics`` (re2c_build_q.metrics) is given, the median per-cell and integrated relative sigma before and after."""
    dC = np.asarray(C_new, np.float64) - np.asarray(C_old, np.float64)
    out = {"eps": {"retained": epsilon(C_old, dC)}, "corr": corr_change(C_old, C_new),
           "rank": {"before": rank(C_old), "after": rank(C_new)}}
    for k in RANKS:
        out["eps"][str(k)] = epsilon(C_old, dC, k)
    if metrics is not None:
        b, a = metrics(C_old, x, F), metrics(C_new, x, F)
        out["sigma"] = {"median_pct": [b["median_pct"], a["median_pct"]],
                        "integral_sigma_pct": [b["integral_sigma_pct"], a["integral_sigma_pct"]]}
    return out


# ------------------------------------------------------------------------------------------------------------ C_T'
def c_t_prime(B: dict, universe_bands: dict, universe_block, cells, order, lateral_bands, norm_key: str,
              c_model_minus=None) -> dict:
    """The blocks at T with the universe block rebuilt from ``universe_bands`` ({band: (n_u, 205)} for every band of
    ``order``) and every other block taken from the committed blocks_<T>.npz ``B``, in cov2d_blocks.assemble's
    arithmetic. ``universe_block`` is re2c_rollup.universe_block and ``cells`` a cov2d_blocks.CellsT(rep, x_T). The
    lateral and normalization blocks it recomputes must equal B's bitwise, or it refuses."""
    if set(universe_bands) != set(order):
        raise Refusal(f"c_t_prime: the universe bands {sorted(set(universe_bands) ^ set(order))} differ from the order")
    bands = {b: np.asarray(universe_bands[b], np.float64) for b in order}
    for b in lateral_bands:
        bands[b] = np.asarray(B[f"band__{b}"], np.float64)
    ublocks, tot = universe_block(cells, bands, B["w_flux"], B["minos_x"])
    C_univ = sum(ublocks[b] for b in sorted(order))
    C_lat = sum(ublocks[b] for b in sorted(lateral_bands))
    C_norm = ublocks[norm_key]
    if not (np.array_equal(C_lat, B["C_lat"]) and np.array_equal(C_norm, B["C_norm"])):
        raise Refusal("c_t_prime: the recomputed lateral or normalization block differs from the committed one")
    C_T = C_univ + B["C_lat"] + B["C_norm"] + B["C_stat"] + B["C08"] + B["C_model_abs"]
    out = {"C_univ": C_univ, "C_lat": B["C_lat"], "C_norm": B["C_norm"], "C_stat": B["C_stat"], "C08": B["C08"],
           "C_model_abs": B["C_model_abs"], "C_T": C_T, "bands": bands}
    if c_model_minus is not None:
        x_T = np.asarray(B["x_T"], np.float64)
        out["C_T_minus"] = C_T - B["C_model_abs"] + x_T[:, None] * np.asarray(c_model_minus, np.float64) * x_T[None, :]
    return out


def blocks_npz_arrays(B: dict, new: dict) -> dict:
    """The arrays of a blocks_<T>.npz in phase N's layout (cov2d_readout.phase_null), with the rebuilt blocks."""
    arrays = {k: new[k] for k in ("C_T", "C_univ", "C_lat", "C_norm", "C_stat", "C08", "C_model_abs")}
    if "C_T_minus" in new:
        arrays["C_T_minus"] = new["C_T_minus"]
    for k in ("x_T", "x_R", "rep", "minos_x", "w_flux"):
        arrays[k] = np.asarray(B[k])
    arrays.update({f"band__{b}": v for b, v in new["bands"].items()})
    return arrays
