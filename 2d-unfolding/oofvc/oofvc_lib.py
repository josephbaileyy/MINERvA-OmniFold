"""OOFVC's pure functions (OOFVC-DECLARATION.md): the exact join, the moved rows, N's factor, the distance and the
readings. numpy only, so the tests run without ROOT; the cluster tools (oofvc_join.py, oofvc_run.py) and the scorer
(oofvc_score.py) call these and nothing else decides."""
from __future__ import annotations

import numpy as np

# ------------------------------------------------------------------------------------------------ the grid


def bin_index(x, edges) -> np.ndarray:
    """TH1's bin as 0..n-1, -1 outside: lower edge in, upper edge out (ref_c2c1.bin_index, the same rule)."""
    e = np.asarray(edges, float)
    i = np.searchsorted(e, np.asarray(x, float), side="right") - 1
    return np.where((i >= 0) & (i < e.size - 1), i, -1)


def global_index(pt, pz, pt_edges, pz_edges) -> np.ndarray:
    """(pT bin) x n_pz + (p|| bin), -1 outside (ref_c2c1.global_index)."""
    ip, iz = bin_index(pt, pt_edges), bin_index(pz, pz_edges)
    return np.where((ip >= 0) & (iz >= 0), ip * (len(pz_edges) - 1) + iz, -1)


def in_bins(pt, pz, pt_edges, pz_edges) -> np.ndarray:
    """In a ROOT cell of the grid: lower edges in, upper edges out (global_index >= 0). The moved and appended sets
    use this, so they agree with the binned M, T and O (codex-school r1 #3)."""
    return global_index(pt, pz, pt_edges, pz_edges) >= 0


def in_rectangle(pt, pz, pt_edges, pz_edges) -> np.ndarray:
    """The driver's closed rectangle, pt_lo <= pT <= pt_hi and pz_lo <= p|| <= pz_hi (re2_driver.in_truth_phase_space
    without its angle cut, and the reco gate of collect_signal_arrays_2d)."""
    pt, pz = np.asarray(pt, float), np.asarray(pz, float)
    return (np.isfinite(pt) & np.isfinite(pz) & (pt_edges[0] <= pt) & (pt <= pt_edges[-1])
            & (pz_edges[0] <= pz) & (pz <= pz_edges[-1]))


# ------------------------------------------------------------------------------------------------ the join


class JoinStop(RuntimeError):
    """C-JOIN or C-SIGW refused: the join is not one-to-one under the director's rule."""


def _row_keys(cols) -> np.ndarray:
    """Exact keys: the float64 bit patterns of the columns, one void scalar per row (so -0.0 and 0.0 differ, and
    no tolerance enters)."""
    if isinstance(cols, np.ndarray) and cols.ndim == 2:  # rows x columns
        a = np.ascontiguousarray(cols.astype(np.float64))
    else:  # a sequence of 1D columns
        a = np.ascontiguousarray(np.column_stack([np.asarray(c, np.float64) for c in cols]))
    return a.view(np.dtype((np.void, a.dtype.itemsize * a.shape[1]))).ravel()


def exact_join(left_key, right_key, right_event, right_values, left_weight, *, max_copies=2):
    """One-to-one join of `left` rows (the production tree's) to `right` rows (the dump's) on the exact key.

    The director's rulings (2026-11-26) on ruling 1:
      - each key's counts must be equal on both sides, else STOP (an unmatched row or a count mismatch);
      - a key held by more than one row (a tie) is allowed only if every right row of the group carries the same
        dump event key (`right_event`, rows of (mc_run, mc_subrun, mc_nthEvtInFile)) and bit-identical values
        (`right_values`, the dump's columns), with equal counts on both sides: one event filled twice;
      - STOP if any group has more than `max_copies` copies;
      - the weight bound (0.1% of the moved weight) is check_tie_bound's, applied once the moved rows are known.
    Returns {"right_of_left": index into right for each left row, "tied_left": the left rows in tied groups,
    "n_tied_groups", "n_tied_rows", "tied_weight"}."""
    lk, rk = _row_keys(left_key), _row_keys(right_key)
    nl, nr = lk.size, rk.size
    allk = np.concatenate([lk, rk])
    uniq, inv = np.unique(allk, return_inverse=True)
    inv = inv.ravel()
    cl = np.bincount(inv[:nl], minlength=uniq.size)
    cr = np.bincount(inv[nl:], minlength=uniq.size)
    bad = np.flatnonzero(cl != cr)
    if bad.size:
        raise JoinStop(f"{bad.size} keys with unequal counts (left-only rows {int(np.maximum(cl - cr, 0).sum())}, "
                       f"right-only rows {int(np.maximum(cr - cl, 0).sum())})")
    tied = np.flatnonzero(cl > 1)
    if tied.size and int(cl[tied].max()) > max_copies:
        raise JoinStop(f"a tied group has {int(cl[tied].max())} copies (> {max_copies})")
    li = np.argsort(inv[:nl], kind="stable")
    ri = np.argsort(inv[nl:], kind="stable")
    right_of_left = np.empty(nl, np.int64)
    right_of_left[li] = ri  # the same key order on both sides; within a tied group, in order
    if tied.size:
        ev = _row_keys(right_event)
        vals = _row_keys(right_values)
        group_of_right = inv[nl:]
        tied_set = np.isin(group_of_right, tied)
        for g in tied:
            members = np.flatnonzero(group_of_right == g)
            if np.unique(ev[members]).size != 1 or np.unique(vals[members]).size != 1:
                raise JoinStop("a tie between different events or non-identical dump rows")
        tied_left = np.isin(inv[:nl], tied)
    else:
        tied_set = np.zeros(nr, bool)
        tied_left = np.zeros(nl, bool)
    tied_weight = float(np.asarray(left_weight, float)[tied_left].sum())
    return {"right_of_left": right_of_left, "tied_left": tied_left, "n_tied_groups": int(tied.size),
            "n_tied_rows": int(tied_set.sum()), "tied_weight": tied_weight}


def check_tie_bound(tied_weight: float, reference_weight: float, frac: float = 1e-3) -> None:
    """The director's bound: STOP if the tied groups' weight exceeds `frac` (0.1%) of the reference (the moved weight
    for C-JOIN, the joined signal weight for C-SIGW)."""
    if tied_weight == 0:  # no tie: nothing to bound (codex-school r1 #9)
        return
    if not (np.isfinite(tied_weight) and np.isfinite(reference_weight) and reference_weight > 0):
        raise JoinStop(f"tied weight {tied_weight} against a reference weight {reference_weight}")
    if tied_weight > frac * reference_weight:
        raise JoinStop(f"tied groups carry {tied_weight:.6g}, more than {frac:g} of {reference_weight:.6g}")


# ------------------------------------------------------------------------------------------------ the moved rows


def is_numu_cc(nu_pdg, current) -> np.ndarray:
    """The truth signal definition, truth::IsNeutrino (analysis PDG 14) and truth::IsCC (current 1)."""
    return (np.asarray(nu_pdg) == 14) & (np.asarray(current) == 1)


def moved_mask(nu_pdg, current, true_pt, true_pz, pt_edges, pz_edges) -> np.ndarray:
    """The rows that move under R (section 1.3): nu_mu CC background rows whose true muon is in a cell of the grid
    (in_bins). nu_mu CC rows with a true muon outside it stay background (the director's ruling 3)."""
    return is_numu_cc(nu_pdg, current) & in_bins(true_pt, true_pz, pt_edges, pz_edges)


# ------------------------------------------------------------------------------------------------ N


def n_factor(sum_m, o) -> np.ndarray:
    """N's per-truth-bin factor sum_i M_ij / (sum_i M_ij + O_j); 1 where sum_i M_ij is 0 (section 2.1)."""
    sum_m, o = np.asarray(sum_m, float), np.asarray(o, float)
    if np.any(o < 0) or np.any(sum_m < 0):
        raise ValueError("N: negative sums")
    return np.divide(sum_m, sum_m + o, out=np.ones_like(sum_m), where=sum_m > 0)


def o_vector(truth_pt, truth_pz, w, pt_edges, pz_edges) -> np.ndarray:
    """O_j: the weights binned at their truth cell (outside the grid dropped)."""
    g = global_index(truth_pt, truth_pz, pt_edges, pz_edges)
    n = (len(pt_edges) - 1) * (len(pz_edges) - 1)
    ok = g >= 0
    return np.bincount(g[ok], weights=np.asarray(w, float)[ok], minlength=n)


def dagostini(M, T, y, ks) -> dict:
    """ref_c2c1.dagostini, the same update (tests compare the two; the runner uses ref_c2c1's own)."""
    R = np.divide(M, T[None, :], out=np.zeros_like(M), where=T[None, :] > 0)
    eff = R.sum(axis=0)
    u = T.astype(float).copy()
    out = {}
    for k in range(1, max(ks) + 1):
        fold = R @ u
        ratio = np.divide(y, fold, out=np.zeros_like(y), where=fold > 0)
        u = np.divide(u * (R.T @ ratio), eff, out=np.zeros_like(u), where=eff > 0)
        if k in ks:
            out[k] = u.copy()
    return out


def unfold_selected(M, y, K) -> np.ndarray:
    """compare.py's unfold_selected (the exploratory replay): IBU to selected events, prior sum_i M_ij."""
    def divide(a, b):
        return np.divide(a, b, out=np.zeros(np.broadcast_shapes(a.shape, b.shape)), where=b > 0)
    prior = M.sum(axis=0)
    response = divide(M, prior)
    for _ in range(K):
        prior = prior * (response.T @ divide(y, response @ prior))
    return prior


# ------------------------------------------------------------------------------------------------ scoring


def distance(x, pub, cov) -> tuple[float, int]:
    """D: chi2(x - pub) / ndf under the published covariance, ndf = the cells with a positive diagonal, the
    pseudo-inverse on that mask (tier1/score_t1.py, compare_to_paper_fullcov.chi2_with_cov's convention)."""
    x, pub, cov = np.asarray(x, float), np.asarray(pub, float), np.asarray(cov, float)
    mask = np.diag(cov) > 0
    ci = np.linalg.pinv(cov[np.ix_(mask, mask)])
    d = (x - pub)[mask]
    ndf = int(mask.sum())
    return float(d @ ci @ d) / ndf, ndf


def column_ratio(x, pub, pt_edges, pz_edges, column) -> float:
    """The area-weighted ratio ours / published over one true p|| column (compare.py:106-107, :149)."""
    npz = len(pz_edges) - 1
    area = np.diff(np.asarray(pt_edges, float)) * (pz_edges[column + 1] - pz_edges[column])
    idx = np.arange(len(pt_edges) - 1) * npz + column
    return float(np.dot(area, np.asarray(x, float)[idx]) / np.dot(area, np.asarray(pub, float)[idx]))


BANDS = (("LOWER", lambda r: r <= 0.80), ("HIGHER", lambda r: r >= 1.25),
         ("LITTLE CHANGE", lambda r: 0.95 <= r <= 1 / 0.95))


def band(r: float) -> str:
    """Section 2.4's bands, fixed before any number: LOWER r <= 0.80; HIGHER r >= 1.25; LITTLE CHANGE
    0.95 <= r <= 1/0.95; INTERMEDIATE otherwise."""
    if not np.isfinite(r) or r < 0:
        raise ValueError(f"ratio {r} is not a distance ratio")
    for name, test in BANDS:
        if test(r):
            return name
    return "INTERMEDIATE"


def primary_statement(b_ibu: str, b_er: str) -> str:
    """Section 2.4's primary table (R): the statement the result supports."""
    if b_ibu == "HIGHER" or b_er == "HIGHER":
        which = " and ".join(n for n, b in (("the binned IBU's", b_ibu), ("the OmniFold central value's", b_er))
                             if b == "HIGHER")
        return f"The reclassification increases {which} distance"
    if b_ibu == "LOWER" and b_er == "LOWER":
        return ("Under MINERvA's reclassification, both central values are closer to the published result by this "
                "metric")
    if b_ibu == "LOWER":
        return ("The reclassification moves the binned IBU's distance; at this scale it does not move the OmniFold "
                "central value's")
    if b_ibu == "LITTLE CHANGE":
        return "At this scale the binned IBU's distance does not depend on the reclassification"
    return "No statement of the declared table: the binned IBU's change is INTERMEDIATE"


def n_statement(b_n: str) -> str:
    """Section 2.4's secondary table (N, IBU only)."""
    return {"LOWER": "Counting selected events in the efficiency numerator wherever they reconstruct moves the binned "
                     "IBU's distance down",
            "LITTLE CHANGE": "At this scale the binned IBU's distance does not depend on the numerator's scope",
            "HIGHER": "The numerator's scope increases the distance"}.get(
        b_n, "No statement of the declared table: the change under N is INTERMEDIATE")
