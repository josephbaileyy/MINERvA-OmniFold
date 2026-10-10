#!/usr/bin/env python3
"""D-ID: the binned exact-response diagnostic of the scalar-5D GBDT residual (frozen driver).

Design: ``../gbdt/REPORT.md`` section 6, with the prospective amendments of ``REPORT.md`` section 3 in
this directory (each is coded here and named in a comment as ``AM-n``). Configuration, digests, grids,
tolerances and the CPU cap are in ``config.json``; nothing numerical is chosen in this file except
what that file or ``../gbdt/comparator.py`` fixes.

Reused, never re-implemented (each digest-pinned in ``config.json`` and checked before import):

* the truth reweights: ``s5n_pseudo.truth_weight`` after ``s5p_converge.install()``, the dispatch study K
  ran (``eavail_shape``, ``q3_given_eavail_w``, ``ratio_nd``) plus ``s5p_truths`` (``cond_ratio``, P2r);
* the 5D binning ``s5e_trace.flat_index``; the extraction ``xsec_nd.extract_cross_section_nd``;
* the 185 functional rows ``s5c_coverage.reported_functionals`` + ``s5p_converge.h2_rows`` (the rows
  study K recorded);
* the labels, branch aggregation and missed-event concentration of ``comparator.py``, and its
  thresholds.

MEASURES: per functional and departure, the residual an exact binned response iteration leaves at
matched iteration counts and at convergence, and the local Cramer-Rao width of the binned problem.
CANNOT AUTHORIZE: a measurement, an interval, an estimator, a coverage statement, or any statement
about real data. The real-data keys of the event file are never read (AM-17).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import resource
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
GBDT = HERE.parent / "gbdt"
CONFIG = HERE / "config.json"

MC_KEYS = ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco", "denom_nd", "flux",
           "data_pot", "n_nucleons", "nedges")
REAL_DATA_KEYS = ("measured", "measured_weights")  # AM-17: never read


class AdmissionFailure(RuntimeError):
    """A frozen admission check failed: everything after it stops (gbdt REPORT section 6)."""


class CapReached(RuntimeError):
    """The CPU cap would be exceeded by the next unit of work: stop, keep completed stages."""


def by_chunks(fn, coords: np.ndarray, edges: list, rows: np.ndarray | None = None, chunk: int = 2_000_000):
    """A row-wise committed function (``flat_index``, ``in_grid``) applied in row chunks: identical
    output, bounded temporaries (review M3)."""
    idx = np.arange(coords.shape[0]) if rows is None else rows
    return np.concatenate([fn(coords[idx[i:i + chunk]], edges) for i in range(0, idx.size, chunk)]) \
        if idx.size else fn(coords[idx], edges)


def sha256(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


# ------------------------------------------------------------------------------- pinned modules


def load_comparator(expect: str):
    path = GBDT / "comparator.py"
    if sha256(path) != expect:
        raise AdmissionFailure(f"{path} digest differs from config")
    spec = importlib.util.spec_from_file_location("did_gbdt_comparator", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass
class Committed:
    """The committed nd-unfolding modules, imported from this checkout after their digests match."""

    s5n_pseudo: object
    s5e_trace: object
    s5c_coverage: object
    s5p_converge: object
    xsec_nd: object
    s5e_geometry: object


def load_committed(expect: dict[str, str]) -> Committed:
    nd = REPO / "nd-unfolding"
    for name, digest in expect.items():
        if sha256(nd / name) != digest:
            raise AdmissionFailure(f"nd-unfolding/{name} digest differs from config")
    if str(nd) not in sys.path:
        sys.path.insert(0, str(nd))
    import s5c_coverage  # noqa: E402
    import s5e_geometry  # noqa: E402
    import s5e_trace  # noqa: E402
    import s5n_pseudo  # noqa: E402
    import s5p_converge  # noqa: E402
    import s5p_truths  # noqa: E402
    import xsec_nd  # noqa: E402

    for module in (s5c_coverage, s5e_geometry, s5e_trace, s5n_pseudo, s5p_converge, s5p_truths, xsec_nd):
        if Path(module.__file__).resolve().parent != nd.resolve():
            raise AdmissionFailure(f"{module.__name__} resolved outside this checkout: {module.__file__}")
    s5p_converge.install()  # study K's dispatch: ratio_nd (s5e_deform), and the H2 rows appended
    s5p_truths.install(s5n_pseudo)  # adds cond_ratio (P2r) without touching the others
    return Committed(s5n_pseudo, s5e_trace, s5c_coverage, s5p_converge, xsec_nd, s5e_geometry)


def expected_names(operand_names) -> list[str]:
    """The 185 study-K functional names, built from the committed operand names alone (M1): the 42 EW
    cells, EW_all_ones, the 109 supported J cells, total_integrated, then the 32 H2 cells."""
    names = [str(x) for x in operand_names]
    ew = [x for x in names if x.startswith("EW")]
    j = [x for x in names if x.startswith("J")]
    h2 = [x for x in names if x.startswith("H2_")]
    return ew + ["EW_all_ones"] + j + ["total_integrated"] + h2


# ------------------------------------------------------------------------------------ budget


class Budget:
    """Aggregate process CPU (all threads, plus any children) against the owner's cap (AM-16)."""

    def __init__(self, cap_core_hours: float, spent_before_s: float = 0.0, ram_bytes: float = np.inf):
        self.cap_s = 3600.0 * cap_core_hours
        self.ram_bytes = ram_bytes
        self.before = spent_before_s
        self.t0 = time.time()

    @staticmethod
    def process_cpu_s() -> float:
        own = resource.getrusage(resource.RUSAGE_SELF)
        kids = resource.getrusage(resource.RUSAGE_CHILDREN)
        return own.ru_utime + own.ru_stime + kids.ru_utime + kids.ru_stime

    def used_s(self) -> float:
        return self.before + self.process_cpu_s()

    def check(self, upcoming_s: float = 0.0) -> None:
        if self.used_s() + upcoming_s > self.cap_s:
            raise CapReached(f"used {self.used_s():.0f} s + next {upcoming_s:.0f} s > cap {self.cap_s:.0f} s")
        if self.peak_rss_bytes() > self.ram_bytes:  # M3: a peak cannot be pre-empted; stop at the first check
            raise CapReached(f"peak RSS {self.peak_rss_bytes()} B above the {self.ram_bytes:.0f} B cap")

    def peak_rss_bytes(self) -> int:
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(rss if sys.platform == "darwin" else rss * 1024)


# ------------------------------------------------------------------------------------- grids


def coarse_of_fine(fine_edges: list, coarse_edges: list) -> np.ndarray:
    """Flat C-order coarse cell of every fine cell by the fine-centre rule of the J/H2 rows."""
    for f, c in zip(fine_edges, coarse_edges, strict=True):
        if not all(np.any(np.isclose(np.asarray(f, float), x)) for x in c):
            raise ValueError("a coarse edge is not a fine edge")
    shape = tuple(len(e) - 1 for e in fine_edges)
    idx = np.unravel_index(np.arange(int(np.prod(shape))), shape)
    parts = []
    for k, (f, c) in enumerate(zip(fine_edges, coarse_edges, strict=True)):
        f, c = np.asarray(f, float), np.asarray(c, float)
        centres = 0.5 * (f[:-1] + f[1:])[idx[k]]
        parts.append(np.clip(np.searchsorted(c, centres, side="right") - 1, 0, len(c) - 2))
    return np.ravel_multi_index(parts, tuple(len(c) - 1 for c in coarse_edges))


def split_edges(fine: list, coarse: list) -> list:
    """T2: each coarse bin split at the interior fine edge nearest its midpoint (lower on a tie, AM-19);
    a bin without an interior fine edge is not split."""
    fine = np.asarray(fine, float)
    out = [float(coarse[0])]
    for a, b in zip(coarse[:-1], coarse[1:]):
        inner = fine[(fine > a) & (fine < b)]
        if inner.size:
            gap = np.abs(inner - 0.5 * (a + b))
            out.append(float(inner[np.flatnonzero(gap == gap.min())[0]]))
        out.append(float(b))
    return out


@dataclass
class Grid:
    """A truth grid: fine cell -> kept cell (-1 when the coarse cell is empty and dropped)."""

    name: str
    cell_of_fine: np.ndarray
    n_cells: int
    coarse_id: np.ndarray  # original coarse id of each kept cell
    dropped: list = field(default_factory=list)  # empty coarse ids, listed (gbdt section 6)


def make_grid(name: str, coarse_of: np.ndarray, n_coarse: int, u_nominal: np.ndarray) -> Grid:
    totals = np.bincount(coarse_of, weights=u_nominal, minlength=n_coarse)
    keep = totals > 0
    new = -np.ones(n_coarse, dtype=np.int64)
    new[keep] = np.arange(int(keep.sum()))
    return Grid(name, new[coarse_of], int(keep.sum()), np.flatnonzero(keep), np.flatnonzero(~keep).tolist())


# --------------------------------------------------------------------------- response algebra


@dataclass
class Pairs:
    """The distinct (reco cell, fine truth cell) pairs of the signal reco rows, and each row's pair."""

    reco: np.ndarray
    fine: np.ndarray
    of_row: np.ndarray

    @classmethod
    def build(cls, rcell: np.ndarray, tfine: np.ndarray, n_fine: int) -> "Pairs":
        keys = rcell.astype(np.int64) * n_fine + tfine.astype(np.int64)
        uniq, inverse = np.unique(keys, return_inverse=True)
        return cls(uniq // n_fine, uniq % n_fine, inverse.ravel())

    def sums(self, w: np.ndarray) -> np.ndarray:
        return np.bincount(self.of_row, weights=w, minlength=self.reco.size)


def coarse_sum(grid: Grid, u_fine: np.ndarray) -> np.ndarray:
    ok = grid.cell_of_fine >= 0
    return np.bincount(grid.cell_of_fine[ok], weights=u_fine[ok], minlength=grid.n_cells)


def response(grid: Grid, pairs: Pairs, pair_w: np.ndarray, u_fine: np.ndarray, n_reco: int) -> sparse.csr_matrix:
    """R[reco, cell] = reco-passing weight / truth weight of the cell, from one weighting's sums."""
    col = grid.cell_of_fine[pairs.fine]
    if np.any(col < 0):
        raise ValueError("a reco pair maps to a dropped (empty) truth cell")
    t = coarse_sum(grid, u_fine)
    r = sparse.coo_matrix((pair_w / t[col], (pairs.reco, col)), shape=(n_reco, grid.n_cells))
    return r.tocsr()


def share_matrix(grid: Grid, u_fine: np.ndarray) -> sparse.csr_matrix:
    """S[fine, cell]: a cell's estimate spread over its fine cells in proportion to u_fine (AM-4)."""
    t = coarse_sum(grid, u_fine)
    ok = (grid.cell_of_fine >= 0) & (u_fine != 0)
    rows = np.flatnonzero(ok)
    cols = grid.cell_of_fine[rows]
    return sparse.csr_matrix((u_fine[rows] / t[cols], (rows, cols)), shape=(u_fine.size, grid.n_cells))


def functional_matrix(rows_kappa: sparse.csr_matrix, grid: Grid, u_fine: np.ndarray) -> np.ndarray:
    """H[functional, cell] such that functional = H @ t for an estimate t on the grid (AM-4)."""
    return np.asarray((rows_kappa @ share_matrix(grid, u_fine)).todense())


@dataclass
class IBUResult:
    final: np.ndarray
    previous: np.ndarray  # the iterate before the last update
    iterations: int
    converged: bool | None
    last_rel_change: float
    trajectory: np.ndarray | None  # functionals at each recorded iteration


def ibu(r: sparse.csr_matrix, y: np.ndarray, b: np.ndarray, prior: np.ndarray, n_iter: int,
        maps: np.ndarray | None = None, record: tuple | None = None, tol: float | None = None,
        budget: Budget | None = None, check_every: int = 1000) -> IBUResult:
    """D'Agostini iterations with a known additive reco term ``b`` (AM-2).

    The update is ``comparator.ibu``'s. Cells with zero efficiency keep their prior (AM-3): the
    reference would refuse them. With ``tol`` the loop stops once the largest relative change of an
    active cell is below it (AM-18); otherwise it runs ``n_iter`` iterations. ``record`` lists the
    1-based iterations at which ``maps @ t`` is stored.
    """
    eff = np.asarray(r.sum(axis=0)).ravel()
    active = eff > 0
    rt = r.T.tocsr()
    t = np.asarray(prior, float).copy()
    rec = sorted(set(record or ()))
    prev = t
    traj = np.empty((len(rec), maps.shape[0])) if (maps is not None and rec) else None
    slot = {k: i for i, k in enumerate(rec)}
    change = np.inf
    for k in range(1, n_iter + 1):
        folded = r @ t + b
        ratio = np.divide(y, folded, out=np.zeros_like(y, dtype=float), where=folded > 0)
        new = t.copy()
        new[active] = t[active] * (rt @ ratio)[active] / eff[active]
        moving = active & (t > 0)
        change = float(np.max(np.abs(new[moving] - t[moving]) / t[moving])) if moving.any() else 0.0
        t, prev = new, t
        if traj is not None and k in slot:
            traj[slot[k]] = maps @ t
        if tol is not None and change < tol:
            return IBUResult(t, prev, k, True, change, traj)
        if budget is not None and k % check_every == 0:
            budget.check()
    return IBUResult(t, prev, n_iter, False if tol is not None else None, change, traj)


def functional_convergence(maps: np.ndarray, res: IBUResult, tol: float) -> tuple[np.ndarray, np.ndarray]:
    """AM-26 (review M2): a functional has converged when its own last-step relative change is below
    ``tol`` (or the whole run met the AM-18 rule). gbdt section 6 says "a T2 *functional* that has not
    converged", so one slow cell outside a functional must not remove it from branch B."""
    f, f_prev = maps @ res.final, maps @ res.previous
    step = np.divide(np.abs(f - f_prev), np.abs(f), out=np.full_like(f, np.inf), where=np.abs(f) > 0)
    return step, bool(res.converged) | (step < tol)


def fisher(r: sparse.csr_matrix, t: np.ndarray, b: np.ndarray) -> np.ndarray:
    """F = R^T diag(1 / (R t + b)) R over reco cells with positive expectation (AM-15)."""
    expected = r @ t + b
    keep = expected > 0
    w = sparse.diags(1.0 / np.sqrt(expected[keep])) @ r[keep]
    return np.asarray((w.T @ w).todense())


def widths_from_eig(values: np.ndarray, vectors: np.ndarray, maps: np.ndarray, rtol: float = 1e-12):
    """``comparator.cr_width`` on a precomputed eigendecomposition (equality tested in test_did.py)."""
    positive = values > rtol * values.max()
    coeff = maps @ vectors
    null = np.sqrt(np.sum(coeff[:, ~positive] ** 2, axis=1)) / np.linalg.norm(maps, axis=1)
    sigma = np.sqrt(np.sum(coeff[:, positive] ** 2 / values[positive], axis=1))
    return np.where(null > 1e-6, np.inf, sigma), null


def invisible_from_eig(values: np.ndarray, vectors: np.ndarray, residual: np.ndarray, maps: np.ndarray,
                       threshold: float = 1.0) -> np.ndarray:
    """``comparator.invisible_share`` on a precomputed eigendecomposition (equality tested)."""
    components = vectors.T @ residual
    weak = values * components**2 < threshold
    total = maps @ residual
    weak_part = maps @ (vectors[:, weak] @ components[weak])
    return np.divide(weak_part, total, out=np.zeros_like(total), where=np.abs(total) > 0)


def rel(estimate: np.ndarray, truth: np.ndarray) -> np.ndarray:
    return np.divide(estimate, truth, out=np.full_like(truth, np.nan, dtype=float), where=truth != 0) - 1.0


def receipt_series_deviation(fn: np.ndarray, true: np.ndarray, series: dict, groups: dict) -> tuple[float, int]:
    """A6: the largest relative deviation of the recomputed per-K median |residual| (percent, over each
    map's reported functionals) from a receipt's series; a NaN on one side only is an infinite deviation,
    on both sides it is counted and reported (it cannot arise when every reported truth is non-zero)."""
    worst, n_nan = 0.0, 0
    for k, metrics in series.items():
        rk = rel(fn[int(k) - 1], true)
        for grp, pos in groups.items():
            got = 100 * float(np.median(np.abs(rk[pos])))
            want = float(metrics[grp]["median_abs_pct"])
            if not (np.isfinite(got) and np.isfinite(want)):
                both = np.isnan(got) and np.isnan(want)
                n_nan += int(both)
                dev = 0.0 if both else np.inf
            else:
                dev = abs(got - want) / abs(want) if want > 1e-9 else abs(got - want)
            worst = max(worst, dev)
    return worst, n_nan


# ---------------------------------------------------------------------------- decision layer


def labels_for(cmp, r_gbdt: np.ndarray, r_ibu: np.ndarray, sigma_rel: np.ndarray) -> list[dict]:
    return cmp.classify(np.asarray(r_gbdt), np.asarray(r_ibu), np.asarray(sigma_rel))


def sensitive_flags(primary: list[dict], *others: list[dict] | None) -> np.ndarray:
    """AM-7: resolution-sensitive when the (iteration, identifiability) label differs between T1 and T2
    or between the nominal- and departure-weighted responses; an unavailable comparison is not a change
    but leaves the branch undeclared (stage rule)."""
    flags = np.zeros(len(primary), bool)
    for other in others:
        if other is None:
            continue
        flags |= np.array([a != b for a, b in zip(primary, other, strict=True)])
    return flags


def declare(cmp, labels: list[dict], r_gbdt: np.ndarray, r_inf: np.ndarray | None,
            sensitive: np.ndarray, converged: np.ndarray | None) -> dict:
    """The coded aggregation, with the stage-4 rule (#8): without r_IBU(inf) branch B is undeclarable,
    its candidates are listed, and C or A is still declared when it reaches the share on its own.
    Non-converged functionals cannot count toward B (they enter with r_IBU(inf) = inf)."""
    r_gbdt = np.asarray(r_gbdt, float)
    n = len(labels)
    inf_vec = np.full(n, np.inf)
    if r_inf is None:
        out = cmp.branch_outcome(labels, r_gbdt, inf_vec, sensitive)
        cands = [i for i in range(n) if (abs(r_gbdt[i]) > cmp.ELIGIBLE_RESIDUAL and not sensitive[i]
                                          and labels[i]["iteration"] == "iteration-faithful"
                                          and labels[i]["identifiability"] == "identified-at-target")]
        out["b_candidates"] = cands
        out["b_candidate_share"] = len(cands) / out["n_eligible"] if out["n_eligible"] else 0.0
        # m2: B needs its share of candidates; below it B is unreachable whatever stage 4 would give
        out["b_reachable"] = bool(out["n_eligible"] and out["b_candidate_share"] >= cmp.BRANCH_SHARE)
        if out["branch"] == "mixed" and out["b_reachable"]:
            out["branch"] = "B-undeclarable"
        out["stage4"] = "missing"
        return out
    r_eff = np.where(converged, r_inf, np.inf) if converged is not None else np.asarray(r_inf, float)
    out = cmp.branch_outcome(labels, r_gbdt, r_eff, sensitive)
    shares = out["shares"]
    out["tie"] = [k for k in ("C", "A", "B") if out["n_eligible"] and shares[k] >= cmp.BRANCH_SHARE]
    out["nonconverged_b_candidates"] = int(sum(
        1 for i in range(n) if converged is not None and not converged[i]
        and abs(r_gbdt[i]) > cmp.ELIGIBLE_RESIDUAL and not sensitive[i]
        and labels[i]["iteration"] == "iteration-faithful"
        and labels[i]["identifiability"] == "identified-at-target"))
    out["stage4"] = "complete"
    return out


def b_counted(cmp, labels, r_gbdt, r_eff, sensitive) -> np.ndarray:
    """Indices that ``branch_outcome`` counts toward B (same predicate, for the trace reading)."""
    out = []
    for i, lab in enumerate(labels):
        if (abs(r_gbdt[i]) > cmp.ELIGIBLE_RESIDUAL and not sensitive[i]
                and lab["identifiability"] == "identified-at-target"
                and lab["iteration"] == "iteration-faithful"
                and abs(r_eff[i]) <= cmp.CONVERGED_RATIO * abs(r_gbdt[i])):
            out.append(i)
    return np.array(out, dtype=int)


def trace_reading(cmp, r_gbdt_kmax: float | None, r_ibu_kmax: float | None, k_max: int | None) -> str:
    """AM-8, the branch-B route: what the existing receipt-limited study-K trace says about one
    B-counted functional at the last traced iteration. No extension, no new threshold: the frozen 0.3
    faithfulness tolerance and the 2% eligibility floor.

    * ``tracks``: at K_max the GBDT is still iteration-faithful to exact IBU, or both residuals are at
      or below the 2% floor;
    * ``departs``: at K_max it is not (the GBDT leaves the exact iteration's path inside the traced
      range, so more iterations of this estimator are not shown to remove the residual);
    * ``untraced``: no trace beyond K = 5 (W2).
    """
    if k_max is None or k_max <= 5 or r_gbdt_kmax is None:
        return "untraced"
    g, i = abs(r_gbdt_kmax), abs(r_ibu_kmax)
    if (g <= cmp.ELIGIBLE_RESIDUAL and i <= cmp.ELIGIBLE_RESIDUAL) or abs(r_ibu_kmax - r_gbdt_kmax) <= cmp.FAITHFUL_TOLERANCE * g:
        return "tracks"
    return "departs"


# ------------------------------------------------------------------------------ the diagnostic


@dataclass
class WeightSet:
    name: str
    truth: str
    amplitude: float
    ratio: str | None
    ratio_expect_sha256: str | None
    comparator: str  # "trace", "ensemble" (W2) or "none" (P1r-P3r, AM-14)


class Run:
    """All stages on one event file. State persists in ``self.out``; ``checkpoint`` writes it."""

    def __init__(self, cfg: dict, inputs: Path, outdir: Path, budget: Budget, cmp, com: Committed):
        self.cfg, self.inputs, self.outdir, self.budget, self.cmp, self.com = cfg, inputs, outdir, budget, cmp, com
        self.sets = [WeightSet(**w) for w in cfg["weight_sets"]]
        self.out: dict = {"schema": "d-id-results/1", "stages": {}, "admission": {}, "controls": {},
                          "missing": [], "excluded": [], "timing": {}}

    # ---------------------------------------------------------------- bookkeeping
    def stage_mark(self, name: str, status: str, note: str = "") -> None:
        self.out["stages"][name] = {"status": status, "note": note, "cpu_s": self.budget.used_s(),
                                    "wall_s": time.time() - self.budget.t0}
        self.checkpoint()

    def checkpoint(self) -> None:
        self.outdir.mkdir(parents=True, exist_ok=True)
        self.out["resources"] = {"cpu_s": self.budget.used_s(), "peak_rss_bytes": self.budget.peak_rss_bytes(),
                                 "wall_s": time.time() - self.budget.t0,
                                 "threads": {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                                                            "VECLIB_MAXIMUM_THREADS")}}
        tmp = self.outdir / "results.json.tmp"
        tmp.write_text(json.dumps(self.out, indent=1, sort_keys=True, default=_jsonable) + "\n")
        tmp.replace(self.outdir / "results.json")

    def admit(self, name: str, ok: bool, detail) -> None:
        self.out["admission"][name] = {"pass": bool(ok), "detail": detail}
        if not ok:
            self.checkpoint()
            raise AdmissionFailure(f"{name}: {detail}")

    # ---------------------------------------------------------------- stage 1: admission
    def check_records(self) -> None:
        """A2: the committed records and operands this run reads are the bytes the config pins."""
        items = dict(self.cfg["records"], operands=self.cfg["operands"])
        got = {k: sha256(REPO / v["path"]) for k, v in items.items()}
        self.admit("A2_records", all(got[k] == v["expect_sha256"] for k, v in items.items()),
                   {k: {"observed_sha256": g} for k, g in got.items()})

    def load_events(self) -> None:
        cfg = self.cfg["events"]
        path = self.inputs / cfg["file"]
        got = sha256(path)
        self.admit("A1_event_digest", got == cfg["expect_sha256"], {"observed_sha256": got, "bytes": path.stat().st_size})
        z = np.load(path, allow_pickle=True)  # the committed loader's setting, after the digest check
        if not set(MC_KEYS) <= set(z.files):
            self.admit("A1_event_keys", False, {"missing": sorted(set(MC_KEYS) - set(z.files))})
        d = {k: z[k] for k in MC_KEYS}
        d["edges"] = [np.asarray(z[f"edges_{i}"], float) for i in range(int(d["nedges"]))]
        self.out["admission"]["A10_keys_read"] = {"pass": True, "detail": {
            "read": list(MC_KEYS) + [f"edges_{i}" for i in range(int(d["nedges"]))],
            "present_not_read": sorted(set(z.files) - set(MC_KEYS) - {f"edges_{i}" for i in range(5)}),
            "real_data_keys_never_read": list(REAL_DATA_KEYS)}}
        fine = [np.asarray(self.cfg["fine_edges"][a], float) for a in ("pt", "pz", "eavail", "q3", "W")]
        diffs = [float(np.max(np.abs(a - b))) if a.shape == b.shape else np.inf for a, b in zip(d["edges"], fine)]
        self.admit("A9_edges", all(x <= 1e-6 for x in diffs), {"max_abs_diff": diffs})
        self.d = d
        self.edges = d["edges"]
        self.shape = tuple(len(e) - 1 for e in self.edges)
        self.n_fine = int(np.prod(self.shape))

    def build_rows(self) -> None:
        d, com = self.d, self.com
        n = d["MCgen"].shape[0]
        m = np.asarray(d["pass_truth"], bool)
        pr = np.asarray(d["pass_reco"], bool) & m
        rows = {"n_rows": int(n), "pass_truth": int(m.sum()), "pass_truth_and_reco": int(pr.sum())}
        self.m_idx = np.flatnonzero(m)
        self.tf = by_chunks(com.s5e_trace.flat_index, d["MCgen"], self.edges, self.m_idx).astype(np.int32)
        self.pr = np.asarray(d["pass_reco"], bool)[m]
        rf = -np.ones(self.m_idx.size, dtype=np.int32)
        rf[self.pr] = by_chunks(com.s5e_trace.flat_index, d["MCreco"], self.edges, self.m_idx[self.pr])
        self.rf_fine = rf
        self.wt = np.asarray(d["w_truth"], float)[m]
        self.wr = np.asarray(d["w_reco"], float)[m]
        # A8 is counted with the producer's own rule (s5e_geometry.in_grid, upper edge excluded, m1)
        geo = (np.asarray(d["pass_reco"], bool) & m & by_chunks(com.s5e_geometry.in_grid, d["MCgen"], self.edges)
               & by_chunks(com.s5e_geometry.in_grid, d["MCreco"], self.edges))
        rows["rows_eligible_s5e_rule"] = int(geo.sum())
        del geo, d["MCreco"]  # reco is binned; only the truth coordinates are needed again (reweights)
        rows.update({"truth_outside_grid": int((self.tf < 0).sum()),
                     "reco_outside_grid_of_reco_passing": int(((rf < 0) & self.pr).sum()),
                     "sentinel_rows": int(sum(np.any(d["MCgen"][self.m_idx[i:i + 2_000_000]] < -9000, axis=1).sum()
                                              for i in range(0, self.m_idx.size, 2_000_000))),
                     "negative_w_truth": int((self.wt < 0).sum()), "negative_w_reco": int((self.wr < 0).sum())})
        self.out["events"] = rows
        # completeness and kappa through the committed extraction (xsec per unit count, AM-4)
        ofin = np.bincount(self.tf[self.tf >= 0], weights=self.wt[self.tf >= 0], minlength=self.n_fine)
        dn = np.asarray(d["denom_nd"], float).ravel()
        comp = np.zeros(self.n_fine)
        comp[dn > 0] = ofin[dn > 0] / dn[dn > 0]
        kappa, good = com.xsec_nd.extract_cross_section_nd(
            np.ones(self.shape), comp.reshape(self.shape), d["flux"], float(d["data_pot"]),
            float(d["n_nucleons"]), self.edges)
        self.kappa = kappa.ravel(order="C")
        # M1: after s5p_converge.install() the committed function already returns the 185 study-K rows
        # (s5c's 153, then the 32 H2 cells); they are used as they come and their names are checked
        # against a list built independently from the committed operands
        U, names = com.s5c_coverage.reported_functionals(json.loads((REPO / self.cfg["s5c_contract"]).read_text()))
        op = np.load(REPO / self.cfg["operands"]["path"], allow_pickle=False)
        self.names = list(names)
        expected = expected_names(op["names"])
        self.admit("A4_functional_rows", self.names == expected and U.shape == (185, self.n_fine),
                   {"n_rows": int(U.shape[0]), "equal_to_expected": self.names == expected})
        self.U = sparse.csr_matrix(U)
        self.U_kappa = (self.U @ sparse.diags(self.kappa)).tocsr()
        self.f183 = [self.names.index(x) for x in op["names"]]
        self.groups = np.asarray(op["groups"])
        self.reported = np.asarray(op["reported"], bool)
        self.op = op

    def weights(self, ws: WeightSet) -> np.ndarray:
        """The committed truth reweight of every MC row (study K's call), restricted to pass_truth rows."""
        ratio = None
        if ws.ratio is not None:
            p = REPO / ws.ratio
            got = sha256(p)
            self.admit(f"A3_ratio_{ws.name}", got == ws.ratio_expect_sha256, {"ratio": ws.ratio, "observed_sha256": got})
            ratio = json.loads(p.read_text())
        inputs = {"MCgen": self.d["MCgen"], "edges": self.edges, "w_truth": self.d["w_truth"]}
        r = self.com.s5n_pseudo.truth_weight(ws.truth, inputs, ws.amplitude, ratio)
        return np.asarray(r, float)[self.m_idx]

    def histograms(self) -> None:
        """Per weight set: fine truth (all, missed), reco data, out-of-grid reco term, pair sums; and the
        same for the split halves (AM-2, AM-11)."""
        cfg = self.cfg
        in_t = self.tf >= 0
        sig_reco = self.pr & (self.rf_fine >= 0)
        pair_rows = sig_reco & in_t
        bkg_rows = sig_reco & ~in_t
        # A8: s5e geometry's "rows_eligible", by its own rule; the pair-row count (edges closed) beside it
        self.out["events"]["pair_rows"] = int(pair_rows.sum())
        self.admit("A8_rows", self.out["events"]["rows_eligible_s5e_rule"] == cfg["events"]["pair_rows_expected"],
                   self.out["events"])
        self.pairs = Pairs.build(self.rf_fine[pair_rows], self.tf[pair_rows], self.n_fine)
        # split (secondary): half B is the pseudo-data source, A the unfolding MC (s5n convention)
        key = int(cfg["split"]["key"])
        derived = self.com.s5n_pseudo.s5c_pseudo.split_key_for(int(cfg["split"]["seed"]))
        self.split_ok = derived == key
        is_b_all = self.com.s5n_pseudo.s5c_pseudo.half_mask(self.d["MCgen"].shape[0], key)
        is_b = is_b_all[self.m_idx]
        self.pairs_a = Pairs.build(self.rf_fine[pair_rows & ~is_b], self.tf[pair_rows & ~is_b], self.n_fine)
        self.h: dict[str, dict] = {}
        for ws in self.sets:
            self.budget.check(cfg["price_s"]["weights_and_histograms"])
            r = self.weights(ws)
            wtr, wrr = self.wt * r, self.wr * r
            h = {
                "u": np.bincount(self.tf[in_t], weights=wtr[in_t], minlength=self.n_fine),
                "u_miss": np.bincount(self.tf[in_t & ~self.pr], weights=wtr[in_t & ~self.pr], minlength=self.n_fine),
                "y": np.bincount(self.rf_fine[sig_reco], weights=wrr[sig_reco], minlength=self.n_fine),
                "b": np.bincount(self.rf_fine[bkg_rows], weights=wrr[bkg_rows], minlength=self.n_fine),
                "P": self.pairs.sums(wrr[pair_rows]),
                "r_outside_grid_max_dev": float(np.max(np.abs(r[~in_t] - 1.0))) if (~in_t).any() else 0.0,
            }
            a, bh = ~is_b, is_b
            h["split"] = {
                "u_a": 2.0 * np.bincount(self.tf[in_t & a], weights=wtr[in_t & a], minlength=self.n_fine),
                "u_b": 2.0 * np.bincount(self.tf[in_t & bh], weights=wtr[in_t & bh], minlength=self.n_fine),
                "y_b": 2.0 * np.bincount(self.rf_fine[sig_reco & bh], weights=wrr[sig_reco & bh], minlength=self.n_fine),
                "b_a": 2.0 * np.bincount(self.rf_fine[bkg_rows & a], weights=wrr[bkg_rows & a], minlength=self.n_fine),
                "P_a": 2.0 * self.pairs_a.sums(wrr[pair_rows & a]),
            }
            self.h[ws.name] = h
            self.admit(f"A11_reweight_is_one_outside_grid_{ws.name}", h["r_outside_grid_max_dev"] == 0.0,
                       {"max_abs_dev": h["r_outside_grid_max_dev"]})  # AM-2 rests on it (m4)
        halves = {"n_a": int((~is_b).sum()), "n_b": int(is_b.sum()), "disjoint_by_row_index": True,
                  "w_truth_sum_a": float(self.wt[~is_b].sum()), "w_truth_sum_b": float(self.wt[is_b].sum()),
                  "key": key, "key_from_seed": int(derived), "seed": cfg["split"]["seed"]}
        self.out["split"] = halves
        # reco cells: the occupied cells of the nominal fold (s5e's 10,499)
        y_nom = self.h["nominal"]["y"]
        self.reco_cells = np.flatnonzero(y_nom > 0)
        self.admit("A7_reco_cells", self.reco_cells.size == cfg["reco_cells_expected"],
                   {"n_reco_cells": int(self.reco_cells.size)})
        remap = -np.ones(self.n_fine, dtype=np.int64)
        remap[self.reco_cells] = np.arange(self.reco_cells.size)
        self.pairs.reco = remap[self.pairs.reco]
        self.pairs_a.reco = remap[self.pairs_a.reco]
        if np.any(self.pairs.reco < 0) or np.any(self.pairs_a.reco < 0):
            self.admit("A7_pairs_in_reco_cells", False, "a signal pair lies outside the occupied reco cells")
        for h in self.h.values():
            for key2 in ("y", "b"):
                h[key2] = h[key2][self.reco_cells]
            for key2 in ("y_b", "b_a"):
                h["split"][key2] = h["split"][key2][self.reco_cells]
        # free the row arrays: everything downstream is binned (M3)
        for k in ("MCgen", "pass_reco", "pass_truth", "w_truth", "w_reco", "denom_nd"):
            self.d.pop(k, None)
        del self.tf, self.rf_fine, self.wt, self.wr, self.pr, self.m_idx

    def f_true(self, u: np.ndarray) -> np.ndarray:
        return self.U_kappa @ u

    # ---------------------------------------------------------------- comparators
    def load_comparators(self) -> None:
        cfg, cmp_cfg = self.cfg, self.cfg["comparators"]
        self.g: dict[str, dict] = {}
        receipt = json.loads((REPO / cfg["records"]["stage2_receipt"]["path"]).read_text())["study_K"]
        for name, spec in cmp_cfg["traces"].items():
            p = self.inputs / spec["file"]
            got = sha256(p)
            self.admit(f"A4_trace_{name}", got == spec["expect_sha256"], {"trace": spec["file"], "observed_sha256": got})
            z = np.load(p, allow_pickle=False)
            fn = np.asarray(z["fn_push"], float)
            true = np.asarray(z["fn_true"] if "fn_true" in z.files else z["fn_true_A"], float)
            if fn.shape[1] != len(self.names):
                self.admit(f"A4_trace_{name}_width", False, {"fn_push": list(fn.shape)})
            if "meta" in z.files:
                meta = json.loads(str(z["meta"]))
                self.admit(f"A4_trace_{name}_names", meta["functional_names"] == self.names,
                           {"n": len(meta["functional_names"])})
                self.admit(f"A4_trace_{name}_input", meta["input_npz_sha256"] == cfg["events"]["expect_sha256"],
                           {"input_npz_sha256": meta["input_npz_sha256"]})
            k_receipt = int(receipt[spec["family"]]["runs"][spec["receipt_run"]]["K"])
            avail = fn.shape[0]
            # AM-8/N1: only the receipt-verified prefix is evidence; later iterations are excluded
            series = receipt[spec["family"]]["runs"][spec["receipt_run"]]["series"]
            groups = {grp: np.array(self.f183)[(self.groups == grp) & self.reported] for grp in ("EW", "J", "H2")}
            worst, n_nan = receipt_series_deviation(fn, true, series, groups)
            self.admit(f"A6_receipt_series_{name}", worst <= cfg["tolerances"]["receipt_series_rtol"],
                       {"worst_rel": worst, "n_nan_medians": n_nan, "K_receipt": k_receipt, "available": avail})
            rec = {"fn": fn[:k_receipt], "true": true, "K": k_receipt, "available": avail,
                   "family": spec["family"], "weight_set": spec["weight_set"]}
            if "xsec_flat" in z.files and avail == k_receipt:
                rec["xsec_final"] = np.asarray(z["xsec_flat"], float)
            self.g[name] = rec
        # s5e diag (secondaries + admission of the reco binning); AM-13: no committed byte digest
        self.s5e: dict[str, dict] = {}
        for name, spec in cmp_cfg["s5e"].items():
            p = self.inputs / spec["file"]
            z = np.load(p, allow_pickle=False)
            meta = json.loads(str(z["meta"]))
            self.admit(f"A4_s5e_{name}_input", meta["input_npz_sha256"] == cfg["events"]["expect_sha256"]
                       and meta["construction"] == spec["construction"],
                       {"observed_sha256": sha256(p), "input_npz_sha256": meta["input_npz_sha256"],
                        "construction": meta["construction"]})
            self.s5e[name] = {"z": {k: np.asarray(z[k]) for k in z.files if k != "meta"}, "meta": meta,
                              "sha256": sha256(p), "weight_set": spec["weight_set"]}
        self.d3: dict[str, list] = {}
        for name, spec in cmp_cfg["d3_sig"].items():
            runs = []
            for f in spec["files"]:
                p = self.inputs / f
                z = np.load(p, allow_pickle=False)
                meta = json.loads(str(z["meta"]))
                if meta["input_npz_sha256"] != cfg["events"]["expect_sha256"] or not meta["no_background"]:
                    self.out["missing"].append({"d3_sig": f, "reason": "input digest or signal-only flag differs"})
                    continue
                runs.append({"fn": np.asarray(z["fn_push"], float), "true": np.asarray(z["fn_true"], float),
                             "split_key": meta.get("split_key"), "pseudo_seed": meta.get("pseudo_seed"),
                             "sha256": sha256(p)})
            self.d3[name] = runs
        # AM-11: the split key is the first D3 signal-only E_avail trace's, reproduced bitwise
        first = self.d3.get(self.cfg["split"]["product"], [])
        recorded = first[0]["split_key"] if first else None
        self.split_ok = bool(self.split_ok and recorded == int(self.cfg["split"]["key"]))
        self.out["split"]["recorded_key"] = recorded
        self.out["split"]["reproduced"] = self.split_ok
        if not self.split_ok:
            self.out["missing"].append({"split_half": "all", "reason": "split key not reproduced bitwise"})
        # W2: the R K = 5 ensemble mean (AM-14), committed operands
        op = self.op
        est, tru = op[cmp_cfg["ensemble"]["W2"]["estimate"]], op[cmp_cfg["ensemble"]["W2"]["truth"]]
        self.w2_r5 = np.mean(est / tru - 1.0, axis=0)

    def admission_truths(self) -> None:
        """A5: the committed weights reproduce every comparator's own truth functionals; A7: S_dep and
        the GBDT fold chi-square reproduce the s5e receipt (gbdt section 6 'reco binning')."""
        tol = self.cfg["tolerances"]
        for name, rec in self.g.items():
            mine = self.f_true(self.h[rec["weight_set"]]["u"])
            ok = rec["true"] != 0
            worst = float(np.max(np.abs(mine[ok] / rec["true"][ok] - 1.0)))
            self.admit(f"A5_truth_{name}", worst <= tol["truth_rtol"] and np.all(mine[~ok] == 0), {"worst_rel": worst})
        for name, rec in self.s5e.items():
            mine = self.f_true(self.h[rec["weight_set"]]["u"])[: rec["z"]["fn_true"].size]
            t = rec["z"]["fn_true"]
            ok = t != 0
            worst = float(np.max(np.abs(mine[ok] / t[ok] - 1.0)))
            self.admit(f"A5_truth_s5e_{name}", worst <= tol["truth_rtol"], {"worst_rel": worst})
        rc = self.cfg["records"]["diag_receipt"]["targets"]
        y_nom = self.h["nominal"]["y"]
        for name, tgt in rc.items():
            ws = self.s5e[name]["weight_set"]
            y = self.h[ws]["y"]
            s_dep = float(np.sum((y_nom - y) ** 2 / y))
            file_true = self.s5e[name]["z"]["reco5d_true"][self.reco_cells]
            fold_dev = float(np.max(np.abs(y / file_true - 1.0)))
            lam = {}
            for k, want in tgt["lambda_5d"].items():
                push = self.s5e[name]["z"][f"reco5d_push_it{k}"].astype(float)[self.reco_cells]
                lam[k] = {"got": float(np.sum((push - y) ** 2 / y)), "want": want}
            lam_ok = all(abs(v["got"] / v["want"] - 1) <= tol["lambda_rtol"] for v in lam.values())
            self.admit(f"A7_sdep_lambda_{name}",
                       abs(s_dep / tgt["S_dep"] - 1) <= tol["s_dep_rtol"] and lam_ok and fold_dev <= tol["truth_rtol"],
                       {"S_dep": s_dep, "S_dep_want": tgt["S_dep"], "lambda_5d": lam, "fold_vs_file_max_rel": fold_dev})

    # ---------------------------------------------------------------- per grid work
    def grids(self) -> None:
        fine = self.edges
        j_edges = [self.cfg["J_edges"][a] for a in ("pt", "pz", "eavail", "q3", "W")]
        t2_edges = [split_edges(f, j) for f, j in zip(fine, j_edges)]
        u0 = self.h["nominal"]["u"]
        c1 = coarse_of_fine(fine, j_edges)
        c2 = coarse_of_fine(fine, t2_edges)
        n1 = int(np.prod([len(e) - 1 for e in j_edges]))
        n2 = int(np.prod([len(e) - 1 for e in t2_edges]))
        self.G = {"T1": make_grid("T1", c1, n1, u0), "T2": make_grid("T2", c2, n2, u0),
                  "T3": make_grid("T3", np.arange(self.n_fine), self.n_fine, u0)}
        self.out["grids"] = {g.name: {"n_cells": g.n_cells, "n_dropped_empty": len(g.dropped),
                                      "dropped_empty": g.dropped if g.name != "T3" else len(g.dropped)}
                             for g in self.G.values()}
        self.out["grids"]["T2"]["edges"] = t2_edges
        fisher_bytes = 8 * self.G["T2"].n_cells ** 2
        self.out["grids"]["T2"]["fisher_bytes"] = fisher_bytes
        if fisher_bytes > self.cfg["limits"]["t2_fisher_max_bytes"]:
            self.out["missing"].append({"grid": "T2", "reason": "Fisher above 6 GiB"})
            del self.G["T2"]

    def problem(self, grid: str, ws: str, role: str, weighting: str) -> dict:
        """Response, data, known reco term, prior, truth and functional map for one variant."""
        g, h, h0 = self.G[grid], self.h[ws], self.h["nominal"]
        n_reco = self.reco_cells.size
        if role == "same":
            u_w = h["u"] if weighting == "dep" else h0["u"]
            p_w = h["P"] if weighting == "dep" else h0["P"]
            r = response(g, self.pairs, p_w, u_w, n_reco)
            y, b = h["y"], h0["b"]  # y counts every signal reco row, b its out-of-grid-truth part
            prior = coarse_sum(g, h0["u"])
            truth_f = self.f_true(h["u"])
            t_bin = coarse_sum(g, h["u"])
        else:  # split: response, prior and known term from half A; data and truth from half B
            s, s0 = h["split"], h0["split"]
            u_w = s["u_a"] if weighting == "dep" else s0["u_a"]
            p_w = s["P_a"] if weighting == "dep" else s0["P_a"]
            r = response(g, self.pairs_a, p_w, u_w, n_reco)
            y, b = s["y_b"], s0["b_a"]  # half B's own out-of-grid rows are in its data
            prior = coarse_sum(g, s0["u_a"])
            truth_f = self.f_true(s["u_b"])
            t_bin = coarse_sum(g, s["u_b"])
        maps = functional_matrix(self.U_kappa, g, u_w)
        return {"R": r, "y": y, "b": b, "prior": prior, "truth_f": truth_f, "t_bin": t_bin, "maps": maps, "u_w": u_w}

    def run_trajectory(self, grid: str, ws: str, role: str, weighting: str, keep_all: bool) -> dict:
        self.budget.check(self.cfg["price_s"][f"trajectory_{grid}"])
        pb = self.problem(grid, ws, role, weighting)
        n_iter = self.cfg["iterations"]["trajectory"]
        record = range(1, n_iter + 1) if keep_all else self.cfg["iterations"]["record_subset"]
        res = ibu(pb["R"], pb["y"], pb["b"], pb["prior"], n_iter, maps=pb["maps"], record=tuple(record))
        rec_k = sorted(set(record))
        r_k = np.vstack([rel(row, pb["truth_f"]) for row in res.trajectory])
        return {"K": rec_k, "r": r_k}  # M3: no operands are retained

    def converge(self, grid: str, ws: str, weighting: str) -> dict:
        self.budget.check(self.cfg["price_s"][f"convergence_{grid}"])
        pb = self.problem(grid, ws, "same", weighting)
        it = self.cfg["iterations"]
        res = ibu(pb["R"], pb["y"], pb["b"], pb["prior"], it["convergence_max"], tol=it["convergence_tol"],
                  budget=self.budget)
        f = pb["maps"] @ res.final
        step, fconv = functional_convergence(pb["maps"], res, it["convergence_tol"])
        return {"pb": pb, "f": f, "r": rel(f, pb["truth_f"]), "iterations": res.iterations,
                "converged": bool(res.converged), "last_rel_change": res.last_rel_change,
                "functional_step": step, "functional_converged": fconv}

    def widths(self, grid: str, ws: str, weighting: str, residual_counts: np.ndarray | None = None) -> dict:
        self.budget.check(self.cfg["price_s"][f"fisher_{grid}"])
        pb = self.problem(grid, ws, "same", weighting)
        f = fisher(pb["R"], pb["t_bin"], pb["b"])
        values, vectors = np.linalg.eigh(f)
        norms = np.linalg.norm(pb["maps"], axis=1)
        sigma = np.full(pb["maps"].shape[0], np.nan)
        null = np.full(pb["maps"].shape[0], np.nan)
        ok = norms > 0
        sigma[ok], null[ok] = widths_from_eig(values, vectors, pb["maps"][ok])
        value = pb["maps"] @ pb["t_bin"]
        sig_rel = np.divide(sigma, np.abs(value), out=np.full_like(sigma, np.nan), where=np.abs(value) > 0)
        eff = np.asarray(pb["R"].sum(axis=0)).ravel()
        hole = np.abs(pb["maps"][:, eff <= 0]).sum(axis=1) > 0  # m6: weight on a zero-efficiency cell
        out = {"sigma_abs": sigma, "sigma_rel": sig_rel, "null_fraction": null, "acceptance_hole": hole,
               "n_zero_efficiency_cells": int(np.sum(eff <= 0)),
               "n_null_modes": int(np.sum(values <= 1e-12 * values.max())), "eig_min": float(values.min()),
               "eig_max": float(values.max())}
        if residual_counts is not None:
            share = np.full(pb["maps"].shape[0], np.nan)
            share[ok] = invisible_from_eig(values, vectors, coarse_sum(self.G[grid], residual_counts), pb["maps"][ok])
            out["invisible_share"] = share
        return out

    def gbdt_residual_counts(self, ws: str) -> tuple[np.ndarray | None, dict]:
        """AM-9: the GBDT's final fine-grid estimate in count units minus the truth, where kappa > 0."""
        spec = self.cfg["comparators"]["invisible_operand"].get(ws)
        if spec is None:
            return None, {"missing": "no fine-grid GBDT estimate for this departure"}
        if spec["source"] == "trace":
            xs, k = self.g[spec["name"]].get("xsec_final"), self.g[spec["name"]]["K"]
            check_fn = self.g[spec["name"]]["fn"][k - 1]
        else:
            z = self.s5e[spec["name"]]["z"]
            xs, k = np.asarray(z["xsec_flat"], float), int(self.s5e[spec["name"]]["meta"]["iters"])
            check_fn = np.asarray(z["fn_push"], float)[k - 1]
        if xs is None:
            return None, {"missing": "the trace carries no final fine-grid estimate"}
        good = self.kappa > 0
        u_hat = np.zeros(self.n_fine)
        u_hat[good] = xs[good] / self.kappa[good]
        resid = np.where(good, u_hat - self.h[ws]["u"], 0.0)
        back = (self.U_kappa @ u_hat)[: check_fn.size]
        ok = check_fn != 0
        dev = float(np.max(np.abs(back[ok] / check_fn[ok] - 1.0)))
        return resid, {"source": spec, "K": k, "functional_reproduction_max_rel": dev}

    def r_gbdt(self, ws: str, k: int) -> np.ndarray | None:
        """The GBDT comparator's relative residual on the 185 functionals at iteration k (None if none)."""
        spec = self.cfg["comparators"]["primary"].get(ws)
        if spec is None:
            return None
        if spec["source"] == "ensemble":
            if k != 5:
                return None
            out = np.full(len(self.names), np.nan)
            out[self.f183] = self.w2_r5
            return out
        rec = self.g[spec["name"]]
        if k > rec["K"]:
            return None
        return rel(rec["fn"][k - 1], rec["true"])


# ------------------------------------------------------------------------------------ stages


BRANCH_POPULATION = ("gibuu", "w1", "w3", "q3", "w2")  # gbdt section 6; P1r-P3r never vote
MAPS = ("EW", "J", "H2")


class Diagnostic(Run):
    """The priority-ordered stages of gbdt section 6 (AM-6) and the decision assembly."""

    def reported_positions(self, group: str | None = None) -> np.ndarray:
        sel = self.reported if group is None else (self.reported & (self.groups == group))
        return np.array(self.f183)[sel]

    # stage 1 --------------------------------------------------------------------------------
    def stage1(self) -> None:
        self.check_records()
        self.load_events()
        self.build_rows()
        self.histograms()
        self.load_comparators()
        self.admission_truths()
        self.grids()
        self.T: dict = {}
        pos = np.array(self.f183)
        for grid in self.G:  # C1, implementation control: same-sample nominal at every grid and K
            tr = self.run_trajectory(grid, "nominal", "same", "nom", keep_all=True)
            worst = float(np.nanmax(np.abs(tr["r"][:, pos])))
            self.out["controls"][f"C1_nominal_{grid}"] = {"max_abs_r_ibu": worst,
                                                          "pass": worst <= self.cfg["tolerances"]["nominal_control"]}
            self.T[(grid, "same", "nom", "nominal")] = tr
            if worst > self.cfg["tolerances"]["nominal_control"]:
                self.checkpoint()
                raise AdmissionFailure(f"implementation control failed at {grid}: {worst}")
        r_nom = self.r_gbdt("nominal", 5)
        self.out["controls"]["gbdt_nominal_K5_max_abs"] = float(np.nanmax(np.abs(r_nom[pos])))

    # stages 2 and 3 -------------------------------------------------------------------------
    def grid_stage(self, grid: str) -> None:
        cmp = self.cmp
        res = self.out.setdefault("per_grid", {}).setdefault(grid, {})
        for ws in self.sets:
            for weighting in ("nom", "dep"):
                key = (grid, "same", weighting, ws.name)
                if key not in self.T:
                    self.T[key] = self.run_trajectory(grid, ws.name, "same", weighting, keep_all=True)
                resid, info = (self.gbdt_residual_counts(ws.name) if weighting == "nom" else (None, None))
                w = self.widths(grid, ws.name, weighting, resid)
                if info is not None:
                    w["invisible_operand"] = info
                res.setdefault(ws.name, {})[f"widths_{weighting}"] = w
            if grid == "T1":
                res[ws.name]["inf_nom"] = slim(self.converge("T1", ws.name, "nom"))
                exact = self.converge("T1", ws.name, "dep")  # the exactness control (gating at T1)
                sig = res[ws.name]["widths_dep"]
                ident = sig["sigma_rel"] <= cmp.IDENTIFIED_SIGMA
                err = np.abs(exact["f"] - exact["pb"]["truth_f"])
                tol = self.cfg["tolerances"]["exactness_sigma_fraction"] * sig["sigma_abs"]
                pos = np.array(self.f183)
                sel = np.zeros(len(self.names), bool)
                sel[pos] = True
                sel &= ident
                bad = np.flatnonzero(sel & ~(err <= tol))
                ok = bad.size == 0  # the frozen criterion; non-convergence is reported beside it
                self.out["controls"][f"C2_exactness_T1_{ws.name}"] = {
                    "pass": bool(ok), "converged": exact["converged"], "iterations": exact["iterations"],
                    "n_identified": int(sel.sum()), "n_fail": int(bad.size),
                    "worst_err_over_sigma": float(np.max(err[sel] / sig["sigma_abs"][sel])) if sel.any() else None}
                res[ws.name]["inf_dep"] = slim(exact)
                if not ok:
                    self.checkpoint()
                    raise AdmissionFailure(f"exactness control failed at T1 for {ws.name}")

    def stage4(self) -> None:
        res = self.out["per_grid"]["T2"]
        for ws in self.sets:
            res[ws.name]["inf_nom"] = slim(self.converge("T2", ws.name, "nom"))

    def stage5(self) -> None:
        for ws in self.sets:  # T3 same-sample, both weightings
            for weighting in ("nom", "dep"):
                key = ("T3", "same", weighting, ws.name)
                if key not in self.T:
                    self.T[key] = self.run_trajectory("T3", ws.name, "same", weighting, keep_all=False)
        if self.split_ok:
            for grid in self.G:
                for ws in self.sets:
                    for weighting in ("nom", "dep"):
                        self.T[(grid, "split", weighting, ws.name)] = self.run_trajectory(
                            grid, ws.name, "split", weighting, keep_all=False)
        res = self.out["per_grid"].get("T2", {})
        for ws in self.sets:  # T2 exactness, reported only
            if ws.name in res:
                exact = self.converge("T2", ws.name, "dep")
                sig = res[ws.name]["widths_dep"]
                ident = sig["sigma_rel"] <= self.cmp.IDENTIFIED_SIGMA
                pos = np.zeros(len(self.names), bool)
                pos[np.array(self.f183)] = True
                sel = pos & ident
                err = np.abs(exact["f"] - exact["pb"]["truth_f"]) / sig["sigma_abs"]
                self.out["controls"][f"C2_exactness_T2_{ws.name}_reported"] = {
                    "converged": exact["converged"], "iterations": exact["iterations"],
                    "n_identified": int(sel.sum()),
                    "n_within_0p01_sigma": int(np.sum(err[sel] <= self.cfg["tolerances"]["exactness_sigma_fraction"])),
                    "worst_err_over_sigma": float(np.max(err[sel])) if sel.any() else None}
                res[ws.name]["inf_dep"] = slim(exact)

    # decision assembly ----------------------------------------------------------------------
    def r_ibu(self, grid, role, weighting, ws, k) -> np.ndarray | None:
        tr = self.T.get((grid, role, weighting, ws))
        if tr is None or k not in tr["K"]:
            return None
        return tr["r"][tr["K"].index(k)]

    def labels(self, grid: str, weighting: str, ws: str, idx: np.ndarray) -> list[dict] | None:
        g5, i5 = self.r_gbdt(ws, 5), self.r_ibu(grid, "same", weighting, ws, 5)
        w = self.out.get("per_grid", {}).get(grid, {}).get(ws, {}).get(f"widths_{weighting}")
        if g5 is None or i5 is None or w is None:
            return None
        return labels_for(self.cmp, g5[idx], i5[idx], w["sigma_rel"][idx])

    def assemble(self) -> None:
        cmp, st = self.cmp, self.out["stages"]
        done = {k: st.get(k, {}).get("status") == "complete" for k in ("1", "2", "3", "4", "5")}
        dec = {"stages_complete": done, "maps": {}, "per_departure": {}, "missed_concentration": {}}
        t2 = self.out.get("per_grid", {}).get("T2", {})
        for grp in MAPS:
            idx_all = self.reported_positions(grp)
            pooled = {"labels": [], "r_gbdt": [], "r_inf": [], "conv": [], "sens": [], "who": []}
            for ws in BRANCH_POPULATION:
                g5 = self.r_gbdt(ws, 5)
                if g5 is None:
                    continue
                idx = idx_all[np.isfinite(g5[idx_all])]
                primary = self.labels("T2", "nom", ws, idx) if done["3"] else None
                if primary is None:
                    continue
                sens = sensitive_flags(primary, self.labels("T1", "nom", ws, idx), self.labels("T2", "dep", ws, idx))
                inf = t2.get(ws, {}).get("inf_nom")
                r_inf = inf["r"][idx] if (inf is not None and done["4"]) else None
                conv = np.asarray(inf["functional_converged"])[idx] if (inf is not None and done["4"]) else None
                one = declare(cmp, primary, g5[idx], r_inf, sens, conv)
                dec["per_departure"].setdefault(ws, {})[grp] = one
                t1 = self.labels("T1", "nom", ws, idx)
                t2d = self.labels("T2", "dep", ws, idx)
                dec.setdefault("labels", {}).setdefault(ws, {})[grp] = [
                    {"functional": self.names[i], "r_gbdt_K5": float(g5[i]), "T2_nom": primary[n],
                     "T1_nom": t1[n] if t1 else None, "T2_dep": t2d[n] if t2d else None,
                     "sensitive": bool(sens[n]), "eligible": bool(abs(g5[i]) > cmp.ELIGIBLE_RESIDUAL and not sens[n]),
                     "acceptance_hole_T2": bool(self.out["per_grid"]["T2"][ws]["widths_nom"]["acceptance_hole"][i]),
                     "converged_T2": None if conv is None else bool(conv[n])}
                    for n, i in enumerate(idx)]
                pooled["labels"] += primary
                pooled["r_gbdt"] += list(g5[idx])
                pooled["r_inf"] += list(r_inf) if r_inf is not None else [np.nan] * idx.size
                pooled["conv"] += list(conv) if conv is not None else [False] * idx.size
                pooled["sens"] += list(sens)
                pooled["who"] += [(ws, self.names[i]) for i in idx]
                if done["3"]:
                    i5 = self.r_ibu("T2", "same", "nom", ws, 5)[idx]
                    u = self.h[ws]
                    frac = (self.U_kappa @ u["u_miss"])[idx] / (self.U_kappa @ u["u"])[idx]
                    dec["missed_concentration"].setdefault(ws, {})[grp] = {
                        **cmp.missed_concentration(np.abs(g5[idx] - i5), frac), "n": int(idx.size)}
            if not done["1"] or not done["2"] or not done["3"]:
                dec["maps"][grp] = {"branch": "INCONCLUSIVE", "reason": "stages 1-3 incomplete"}
                continue
            if not pooled["labels"]:
                dec["maps"][grp] = {"branch": "no-eligible-functional"}
                continue
            r_g = np.array(pooled["r_gbdt"])
            sens = np.array(pooled["sens"])
            r_inf = np.array(pooled["r_inf"]) if done["4"] else None
            conv = np.array(pooled["conv"]) if done["4"] else None
            out = declare(cmp, pooled["labels"], r_g, r_inf, sens, conv)
            if r_inf is not None:
                r_eff = np.where(conv, r_inf, np.inf)
                counted = b_counted(cmp, pooled["labels"], r_g, r_eff, sens)
                reading = []
                for i in counted:
                    ws, name = pooled["who"][i]
                    spec = self.cfg["comparators"]["primary"][ws]
                    k_max = self.g[spec["name"]]["K"] if spec["source"] == "trace" else None
                    j = self.names.index(name)
                    g_k = self.r_gbdt(ws, k_max)[j] if k_max else None
                    i_k = self.r_ibu("T2", "same", "nom", ws, k_max)[j] if k_max else None
                    reading.append({"departure": ws, "functional": name, "K_max": k_max,
                                    "r_gbdt_Kmax": g_k, "r_ibu_Kmax": i_k,
                                    "reading": trace_reading(cmp, g_k, i_k, k_max)})
                out["b_trace_reading"] = reading
                out["b_trace_reading_counts"] = {c: sum(1 for x in reading if x["reading"] == c)
                                                 for c in ("tracks", "departs", "untraced")}
            else:
                out["b_candidates"] = [pooled["who"][i] for i in out.get("b_candidates", [])]
            b_bound = out["shares"]["B"] if r_inf is not None else out.get("b_candidate_share", 0.0)
            small = out["n_eligible"] and max(out["shares"]["C"], out["shares"]["A"], b_bound) < 1.0 / 3.0
            out["all_three_sets_small"] = bool(small)  # AM-20; without stage 4, B's candidate share bounds it
            keep = np.array([w != "w2" for w, _ in pooled["who"]])  # m3: W2 is an R-ensemble comparator
            if keep.any():
                lab = [x for x, k in zip(pooled["labels"], keep) if k]
                alt = declare(cmp, lab, r_g[keep], r_inf[keep] if r_inf is not None else None, sens[keep],
                              conv[keep] if conv is not None else None)
                out["without_w2"] = {k: alt[k] for k in ("branch", "n_eligible", "shares")}
            dec["maps"][grp] = out
        self.out["decision"] = dec

    def tables(self) -> dict[str, np.ndarray]:
        """Full per-functional tables (no cell selection) and the trajectories, for the npz."""
        arrays: dict[str, np.ndarray] = {"names": np.array(self.names), "f183": np.array(self.f183),
                                         "groups183": self.groups, "reported183": self.reported}
        for (grid, role, weighting, ws), tr in self.T.items():
            dtype = np.float64 if (grid, role, weighting) == ("T2", "same", "nom") else np.float32
            arrays[f"traj/{grid}/{role}/{weighting}/{ws}/K"] = np.asarray(tr["K"])
            arrays[f"traj/{grid}/{role}/{weighting}/{ws}/r"] = tr["r"][:, self.f183].astype(dtype)
        for ws in self.sets:
            name = ws.name
            for k in sorted({1, 5, 10, 20, 30, 40, 200}):
                g = self.r_gbdt(name, k)
                if g is not None:
                    arrays[f"gbdt/{name}/K{k}"] = g[self.f183]
            u = self.h[name]
            arrays[f"missed_fraction/{name}"] = ((self.U_kappa @ u["u_miss"]) / (self.U_kappa @ u["u"]))[self.f183]
            for grid, res in self.out.get("per_grid", {}).items():
                for kind, w in res.get(name, {}).items():
                    if kind.startswith("widths_"):
                        for q in ("sigma_rel", "sigma_abs", "null_fraction", "invisible_share", "acceptance_hole"):
                            if q in w:
                                arrays[f"{grid}/{name}/{kind}/{q}"] = np.asarray(w[q])[self.f183]
                    elif kind.startswith("inf_"):
                        arrays[f"{grid}/{name}/{kind}/r"] = np.asarray(w["r"])[self.f183]
                        arrays[f"{grid}/{name}/{kind}/functional_step"] = np.asarray(w["functional_step"])[self.f183]
                        arrays[f"{grid}/{name}/{kind}/functional_converged"] = np.asarray(
                            w["functional_converged"])[self.f183]
        for name, rec in self.g.items():
            if rec["family"] == "cap10":
                for k in (5, 10):
                    if k <= rec["K"]:
                        arrays[f"cap10/{name}/K{k}"] = rel(rec["fn"][k - 1], rec["true"])[self.f183]
        for name, rec in self.s5e.items():
            z = rec["z"]
            n = z["fn_true"].size
            for k in (5, 10, 15, 20, 30):
                if k <= z["fn_push"].shape[0]:
                    arrays[f"s5e/{name}/K{k}"] = rel(z["fn_push"][k - 1], z["fn_true"])[[i for i in self.f183 if i < n]]
        for name, runs in self.d3.items():
            for k in (5, 10, 20):
                rs = [rel(r["fn"][k - 1], r["true"]) for r in runs if k <= r["fn"].shape[0]]
                if rs:
                    n = rs[0].size
                    arrays[f"d3_sig/{name}/K{k}/mean"] = np.mean(rs, axis=0)[[i for i in self.f183 if i < n]]
        return arrays

    def summaries(self) -> None:
        """Per departure x map x quantity: median / p90 / max of |value| over the reported functionals."""
        def stats(v):
            v = np.abs(np.asarray(v, float))
            v = v[np.isfinite(v)]
            return None if not v.size else {"median": float(np.median(v)), "p90": float(np.quantile(v, 0.9)),
                                             "max": float(v.max()), "n": int(v.size)}
        out = {}
        for ws in self.sets:
            for grp in MAPS:
                idx = self.reported_positions(grp)
                row = {}
                g5 = self.r_gbdt(ws.name, 5)
                if g5 is not None:
                    row["r_gbdt_K5"] = stats(g5[idx])
                for grid in ("T1", "T2", "T3"):
                    for weighting in ("nom", "dep"):
                        for k in (5, 200):
                            r = self.r_ibu(grid, "same", weighting, ws.name, k)
                            if r is not None:
                                row[f"r_ibu_{grid}_{weighting}_K{k}"] = stats(r[idx])
                    res = self.out.get("per_grid", {}).get(grid, {}).get(ws.name, {})
                    for weighting in ("nom", "dep"):
                        if f"inf_{weighting}" in res:
                            row[f"r_ibu_{grid}_{weighting}_inf"] = stats(res[f"inf_{weighting}"]["r"][idx])
                        w = res.get(f"widths_{weighting}")
                        if w is not None:
                            row[f"sigma_rel_{grid}_{weighting}"] = stats(w["sigma_rel"][idx])
                            if "invisible_share" in w:
                                row[f"invisible_share_{grid}"] = stats(w["invisible_share"][idx])
                for k in (5, 200):
                    a = self.r_ibu("T2", "same", "nom", ws.name, k)
                    b = self.r_ibu("T2", "same", "dep", ws.name, k)
                    if a is not None and b is not None:
                        row[f"binning_bias_T2_K{k}"] = stats((a - b)[idx])
                out.setdefault(ws.name, {})[grp] = row
        self.out["summaries"] = out
        conv = {}
        for grid, res in self.out.get("per_grid", {}).items():
            for name, r in res.items():
                for kind in ("inf_nom", "inf_dep"):
                    if kind in r:
                        conv[f"{grid}/{name}/{kind}"] = {k: r[kind][k] for k in ("iterations", "converged", "last_rel_change")}
        self.out["convergence"] = conv

    def finish(self) -> None:
        self.assemble()
        self.summaries()
        arrays = self.tables()
        np.savez_compressed(self.outdir / "tables.npz", **arrays)
        for grid, res in self.out.get("per_grid", {}).items():  # large vectors live in tables.npz only
            for name, r in res.items():
                for kind in list(r):
                    if kind.startswith("widths_"):
                        r[kind] = {k: v for k, v in r[kind].items() if not isinstance(v, np.ndarray)}
                    elif kind.startswith("inf_"):
                        r[kind] = {k: r[kind][k] for k in ("iterations", "converged", "last_rel_change")}
        self.checkpoint()

    def save_operands(self, path: Path) -> None:
        """Compact operands for the independent numerical verification (untracked scratch)."""
        arrays = {"reco_cells": self.reco_cells, "kappa": self.kappa, "names": np.array(self.names),
                  "f183": np.array(self.f183), "pairs_reco": self.pairs.reco, "pairs_fine": self.pairs.fine}
        for grid in ("T1", "T2"):
            if grid in self.G:
                arrays[f"grid/{grid}/cell_of_fine"] = self.G[grid].cell_of_fine
        for ws in self.sets:
            h = self.h[ws.name]
            for k in ("u", "u_miss", "y", "b", "P"):
                arrays[f"h/{ws.name}/{k}"] = h[k]
            g = self.r_gbdt(ws.name, 5)
            if g is not None:
                arrays[f"gbdt/{ws.name}/K5"] = g
        np.savez_compressed(path, **arrays)


def run(cfg: dict, inputs: Path, outdir: Path, operands_out: Path | None, spent_before_s: float) -> int:
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        if os.environ.get(var) is None or int(os.environ[var]) > cfg["limits"]["threads"]:
            print(f"refusing: {var} must be set to at most {cfg['limits']['threads']}", file=sys.stderr)
            return 2
    budget = Budget(cfg["limits"]["owner_cpu_core_hours"], spent_before_s, cfg["limits"]["ram_bytes"])
    cmp = load_comparator(cfg["code"]["comparator.py"])
    com = load_committed(cfg["code"]["nd-unfolding"])
    diag = Diagnostic(cfg, inputs, outdir, budget, cmp, com)
    diag.out["config_sha256"] = sha256(CONFIG)
    diag.out["driver_sha256"] = sha256(Path(__file__).resolve())
    plan = (("1", diag.stage1), ("2", lambda: diag.grid_stage("T1")), ("3", lambda: diag.grid_stage("T2")),
            ("4", diag.stage4), ("5", diag.stage5))
    rc = 0
    for name, fn in plan:
        if name in ("3", "4") and "T2" not in getattr(diag, "G", {"T2": None}):
            diag.stage_mark(name, "missing", "T2 dropped")
            continue
        try:
            fn()
        except CapReached as exc:
            diag.stage_mark(name, "cap", str(exc))
            for later, _ in plan[plan.index((name, fn)) + 1:]:
                diag.stage_mark(later, "not-started", "cap reached earlier")
            rc = 5
            break
        except AdmissionFailure as exc:
            diag.stage_mark(name, "failed", str(exc))
            for later, _ in plan[plan.index((name, fn)) + 1:]:
                diag.stage_mark(later, "not-started", "an admission check or control failed")
            rc = 4
            break
        except Exception as exc:  # noqa: BLE001  M3: record the failure, keep completed stages' results
            diag.stage_mark(name, "error", f"{type(exc).__name__}: {exc}")
            for later, _ in plan[plan.index((name, fn)) + 1:]:
                diag.stage_mark(later, "not-started", "an earlier stage raised")
            rc = 6
            break
        diag.stage_mark(name, "complete")
    if "1" in diag.out["stages"] and diag.out["stages"]["1"]["status"] == "complete":
        if operands_out is not None:
            diag.save_operands(operands_out)
        diag.finish()
    else:
        diag.checkpoint()
    return rc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config", type=Path, default=CONFIG)
    ap.add_argument("--inputs", type=Path, required=True, help="directory holding the copied inputs")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--operands-out", type=Path, default=None)
    ap.add_argument("--spent-before-s", type=float, default=0.0,
                    help="owner CPU already spent on earlier attempts of the real diagnostic (counted)")
    a = ap.parse_args(argv)
    cfg = json.loads(a.config.read_text())
    if (a.out / "results.json").exists():
        print(f"refusing to overwrite {a.out / 'results.json'}", file=sys.stderr)
        return 3
    return run(cfg, a.inputs, a.out, a.operands_out, a.spent_before_s)


def slim(conv: dict) -> dict:
    """A convergence result without its operands (they are rebuilt on demand)."""
    return {k: conv[k] for k in ("f", "r", "iterations", "converged", "last_rel_change", "functional_step",
                                 "functional_converged")}


def _jsonable(x):
    if isinstance(x, np.ndarray):
        return [None if (isinstance(v, float) and not np.isfinite(v)) else v for v in x.tolist()]
    if isinstance(x, (np.floating, np.integer, np.bool_)):
        v = x.item()
        return None if isinstance(v, float) and not np.isfinite(v) else v
    if isinstance(x, Path):
        return str(x)
    raise TypeError(type(x))


if __name__ == "__main__":
    sys.exit(main())
