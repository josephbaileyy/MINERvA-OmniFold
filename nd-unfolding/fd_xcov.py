#!/usr/bin/env python3
"""GENCMP X (state/measurement-paper/5d-community-20261024/FD-GENCMP-X-DECLARATION.md): the covariance between the
sixteen-cell result and the adopted 2D result (E_R with Q_R + C_model,2D), per (pT, p_par) quadrant, and step C's
comparison made a test with it. Route B of FD-GENCMP-XCOV-SCOPING.md, under the director's rulings (declaration header).

Subcommands, each writing one JSON readout (and its arrays) and refusing to overwrite:

* ``v0``    (login node) row order and the two joins. MC: the 2D CV omnifile's mc_signal_reco rows against
            of_inputs_5d's MCgen, position by position (sentinel rows excepted). The universe omnifile's mc_signal_reco
            rows likewise, for V1. Data: each 5D observed row (fiducial window) matched to its 2D window row by
            ordered subsequence on (pT, p_par) as float32. Background: each 5D template row matched to its
            mc_background entry the same way. Writes the maps j (data) and entry (background).
* ``v1``    (one CPU job) weight equivalence per universe: the 2D universe omnifile's w_truth_<B>_<i> / w_truth and
            w_reco_<B>_<i> / w_reco on mc_signal_reco against the 5D weight files' wt / w_truth and wr / w_reco, row by
            row (V0's alignment), each ratio to 1e-6 relative. A band passes only if every universe in it passes.
* ``boot``  (one CPU job) the paired 5D replicas: s5p_numerics.main as S1's stat replicas ran it, with
            s5n_pseudo.bootstrap_replica replaced by mapped_replica, whose draws are the 2D replicas' own (RE-2's
            default_rng(b), (b + 10,000,000), (b + 20,000,000) streams) carried to the 5D rows through V0's maps.
            ``--native`` runs the unreplaced function instead (control B0: b = 1 reproduces S1's data_b1_j101.npz).
* ``k``     (login node) the cross blocks and the rule (declaration sections 3-5).

Every pscratch or CFS input is opened with O_NOATIME (fd_gencmp.read_noatime) and checked against its pin.

MEASURES: arithmetic on the declared inputs. CANNOT AUTHORIZE: a reading, a paper edit or a claim.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
_REPO = _ND.parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_gencmp as gc  # noqa: E402  (read_noatime, load_pins, QUADRANTS, cell_matrix, Stop, report)
import s1_assemble as sa  # noqa: E402  (mat_cov, flux_weights, x01_scale, pt_index, functional_matrix, fine_map)

FD = _REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024"
INPUTS_E = FD / "fd/gencmp-e/INPUTS.sha256"          # cited at M = 6cd095d6 (blob 728e7812), never re-pinned here
INPUTS_X = FD / "fd/xcov/INPUTS.sha256"
INPUTS_E_SHA256 = "a5f8e3aee79a250f3b4f947a5fbc84448f0e92afcfa2d0bbe9494c1178403194"   # the file as merged at M (#657)
SEED_DATA, SEED_MC, SEED_BKG = 0, 10_000_000, 20_000_000      # re2_driver.py:2087-2088, :377 (P1_BKG_SEED_OFFSET)
N_2D_DATA, N_MC, N_2D_BKG = 4_091_707, 32_849_103, 658_227     # declaration section 1 (records cited there)
N_5D_OBS, N_5D_TMPL = 4_091_579, 621_445
PT_RANGE, PZ_RANGE, GUARD = (0.0, 4.5), (1.5, 60.0), 1e3       # re2_driver.fill_data_reco_2d's mask
SENTINEL = -9000.0                                             # s5p_universe.py:73 (npz MCgen sentinel rows)
SENTINEL_ROWS = 2801
RATIO_TOL = 1e-6
STAT_REPLICAS = tuple(range(1, 101))
P_MIN, Z_MAX = 0.05, 2.50                                      # the director's ruling 3
NPZ_NAME, BKG_NAME = "of_inputs_5d.npz", "bkg_dump.npz"       # staged by v0 under <run>/inputs/
PD_REL = 1e-12                                                 # V_d's smallest eigenvalue over its largest
K_TOL = 1e-10
NORM = 0.014
N_Q = 4
QNAMES = ("QA", "QB", "QC", "QD")
Stop, report = gc.Stop, gc.report


# ---------------------------------------------------------------- reading


def pins(paths=(INPUTS_E, INPUTS_X)) -> dict[str, str]:
    if INPUTS_E in paths and hashlib.sha256(INPUTS_E.read_bytes()).hexdigest() != INPUTS_E_SHA256:
        raise Stop("0", "fd/gencmp-e/INPUTS.sha256 is not the file amendment E's binding bound at M")
    out = {}
    for p in paths:
        for k, v in gc.load_pins(p).items():
            if out.get(k, v) != v:
                raise Stop("0", f"{k} is pinned twice, to different digests")
            out[k] = v
    return out


class Inputs(gc.Inputs):
    """fd_gencmp.Inputs over both inputs files; ``fileobj`` opens a large file O_NOATIME for streaming readers,
    after its digest is checked by ``verify``."""

    def __init__(self, pin_map=None):
        super().__init__(pins() if pin_map is None else pin_map)

    def fileobj(self, path: Path):
        key = str(path)
        if key not in self.pins:
            raise Stop("0", f"{path} is not pinned")
        if key not in self.record:
            raise Stop("0", f"{path} is opened before its digest was verified")
        flags = os.O_RDONLY | getattr(os, "O_NOATIME", 0)
        return os.fdopen(os.open(path, flags), "rb")

    def verify(self, path: Path, chunk: int = 1 << 24) -> None:
        """The digest of a file too large to hold, streamed through O_NOATIME."""
        key = str(path)
        if key not in self.pins:
            raise Stop("0", f"{path} is not pinned")
        before = os.stat(path).st_atime_ns
        h = hashlib.sha256()
        with os.fdopen(os.open(path, os.O_RDONLY | getattr(os, "O_NOATIME", 0)), "rb") as fh:
            for block in iter(lambda: fh.read(chunk), b""):
                h.update(block)
        got = h.hexdigest()
        self.record[key] = {"sha256": got, "pinned": self.pins[key], "atime_unchanged": os.stat(path).st_atime_ns == before}
        if got != self.pins[key]:
            raise Stop("0", f"{path}: sha256 {got} != pinned {self.pins[key]}")


# ---------------------------------------------------------------- V0: row order and the joins


def mask_2d_data(pt, pz, passed) -> np.ndarray:
    """re2_driver.fill_data_reco_2d's selection, row by row: pass, finite, |x| <= 1e3, inside the closed window."""
    pt, pz = np.asarray(pt, float), np.asarray(pz, float)
    ok = (np.asarray(passed) != 0) & np.isfinite(pt) & np.isfinite(pz) & (np.abs(pt) <= GUARD) & (np.abs(pz) <= GUARD)
    return ok & (pt >= PT_RANGE[0]) & (pt <= PT_RANGE[1]) & (pz >= PZ_RANGE[0]) & (pz <= PZ_RANGE[1])


def subsequence_join(big: np.ndarray, small: np.ndarray) -> tuple[np.ndarray, int]:
    """Map each row of ``small`` (n x 2, float32) to an index of ``big`` (m x 2), in order and injectively, by exact
    equality: the greedy earliest match, which embeds ``small`` in ``big`` whenever any order-preserving embedding
    exists. Returns (map, the number of ``small`` rows whose key occurs more than once anywhere in ``big``, so whose
    match may be another event with the same coordinates); refuses if ``small`` is not a subsequence."""
    big = np.ascontiguousarray(big, np.float32)
    small = np.ascontiguousarray(small, np.float32)
    bk = big.view(np.uint64).ravel() if big.shape[1] == 2 else None
    sk = small.view(np.uint64).ravel() if small.shape[1] == 2 else None
    if bk is None or sk is None:
        raise Stop("J", "the join takes two float32 columns")
    out = np.empty(sk.size, np.int64)
    i = 0
    for r in range(sk.size):
        while i < bk.size and bk[i] != sk[r]:
            i += 1
        if i == bk.size:
            raise Stop("J", f"row {r} of the 5D sample has no 2D match at or after the previous one")
        out[r] = i
        i += 1
    keys, counts = np.unique(bk, return_counts=True)
    dup = keys[counts > 1]
    return out, int(np.isin(sk, dup).sum())        # rows whose (pT, p_par) occurs more than once in the 2D sample


def mc_positional(pt2, pz2, mcgen, w2=None, w5=None) -> dict:
    """V0, MC: the 2D tree's (MC, MC_pz) equal the npz's MCgen columns 0-1 as float32 on every row but the sentinel
    rows; with weights, w5 / w2 is one constant (a POT scale) to RATIO_TOL."""
    mcgen = np.asarray(mcgen, np.float32)
    n = mcgen.shape[0]
    rec = {"rows_2d": int(np.asarray(pt2).size), "rows_5d": int(n)}
    if np.asarray(pt2).size != n:
        return {**rec, "pass": False, "why": "row counts differ"}
    sent = np.any(mcgen < SENTINEL, axis=1)
    same = (np.asarray(pt2, np.float32) == mcgen[:, 0]) & (np.asarray(pz2, np.float32) == mcgen[:, 1])
    rec.update(sentinel_rows=int(sent.sum()), differing_rows=int((~same & ~sent).sum()))
    ok = rec["differing_rows"] == 0 and rec["sentinel_rows"] == SENTINEL_ROWS   # the rows are the same events
    if w2 is not None:
        w2, w5 = np.asarray(w2, float), np.asarray(w5, float)
        use = (w2 != 0) & ~sent
        r = w5[use] / w2[use]
        scale = float(np.median(r))
        rel = float(np.max(np.abs(r / scale - 1))) if r.size else float("inf")
        rec.update(weight_scale=scale, weight_ratio_max_rel=rel, zero_weight_2d_rows=int((~use & ~sent).sum()),
                   zero_weight_mismatch=int(((w2 == 0) != (w5 == 0))[~sent].sum()),
                   weight_note="descriptive: the pairing needs the same events (the coordinates); the weights' ratio "
                               "is recorded, and V1 compares universe-to-CV ratios, which a per-row CV scale cancels")
    rec["pass"] = bool(ok)
    return rec


# ---------------------------------------------------------------- the draws


def draws_2d(b: int, n_data: int = N_2D_DATA, n_mc: int = N_MC, n_bkg: int = N_2D_BKG):
    """The three Poisson(1) streams RE-2's replica b drew (re2_driver.py:2087-2095, :2103; p1_draw_bkg_factors)."""
    d = np.random.default_rng(b + SEED_DATA).poisson(1.0, size=n_data).astype(float)
    m = np.random.default_rng(b + SEED_MC).poisson(1.0, size=n_mc).astype(float)
    g = np.random.default_rng(int(b) + SEED_BKG).poisson(1.0, size=int(n_bkg)).astype(float)
    return d, m, g


def replica_external(exp: dict, d_counts, m_draw, t_draw) -> dict:
    """s5n_pseudo.bootstrap_replica's arithmetic with the three draws given (s5n_pseudo.py:213-219)."""
    if not (len(d_counts) == exp["obs_counts"].shape[0] and len(m_draw) == exp["w_truth"].shape[0]
            and len(t_draw) == exp["tmpl_w"].shape[0]):
        raise Stop("B", "a draw's length is not its stream's row count")
    rep = dict(exp)
    rep["obs_counts"] = np.asarray(d_counts, float)
    pm = np.asarray(m_draw, float)
    rep["w_truth"] = exp["w_truth"] * pm
    rep["w_reco"] = exp["w_reco"] * pm
    rep["tmpl_w"] = exp["tmpl_w"] * np.asarray(t_draw)
    return rep


def native_draws(exp: dict, b: int):
    """The draws s5n_pseudo.bootstrap_replica makes (s5n_pseudo.py:210-218), so replica_external reproduces it."""
    d = np.random.default_rng(b).poisson(exp["obs_counts"]).astype(float)
    m = np.random.default_rng(b + 10_000_000).poisson(1.0, exp["w_truth"].shape[0]).astype(float)
    t = np.random.default_rng(b + 20_000_000).poisson(1.0, exp["tmpl_w"].shape[0])
    return d, m, t


def make_mapped_replica(j: np.ndarray, entry: np.ndarray, sizes=(N_2D_DATA, N_MC, N_2D_BKG)):
    """The replacement for s5n_pseudo.bootstrap_replica: replica b takes RE-2's replica-b draws, the data draw of each
    5D observed row from its 2D row j, the template draw from its mc_background entry, and the MC draw by position."""
    j, entry = np.asarray(j, np.int64), np.asarray(entry, np.int64)

    def mapped_replica(exp: dict, b: int) -> dict:
        d, m, g = draws_2d(int(b), *sizes)
        return replica_external(exp, d[j], m, g[entry])

    mapped_replica.maps_sha256 = hashlib.sha256(j.tobytes() + entry.tobytes()).hexdigest()
    return mapped_replica


def draw_sums_line(b: int, sizes=(N_2D_DATA, N_MC, N_2D_BKG)) -> dict:
    """The sums RE-2's log prints for replica b, regenerated (the draw check, against partb/logs/S1_<b>.log)."""
    d, m, g = draws_2d(b, *sizes)
    return {"data": f"data factor sum={d.sum():.6g} (n={d.size}", "mc": f"mc factor sum={m.sum():.6g} (n={m.size}",
            "bkg": f"bkg factor sum={g.sum():.6g} (n={g.size}"}


def p1_streams_record(xsec: bytes) -> dict | None:
    """The p1Streams TNamed RE-2 wrote into a replica's xsec.root (re2_driver.py:2221-2230, :2530-2531), parsed, or None
    if the file has none. In negweight-refined mode the log never prints the background sum (re2_driver.py:2123 is in
    the purity branch), so this record is the background leg's only source (addendum X-A1)."""
    import uproot
    f = uproot.open(io.BytesIO(xsec))
    if "p1Streams" not in f:
        return None
    return json.loads(f["p1Streams"].member("fTitle"))


def bkg_stream_check(rec: dict | None, b: int, n_bkg: int = N_2D_BKG) -> list[str]:
    """The draw check's background leg (addendum X-A1): replica b's p1Streams record names seed b, the background
    offset SEED_BKG and n_bkg factors, and its background sum is the regenerated stream's. Returns the failures."""
    if rec is None:
        return ["no p1Streams record"]
    _, _, g = draws_2d(int(b), 0, 0, n_bkg)
    want = {"bootstrap_seed": int(b), "seed_offsets.bkg": SEED_BKG, "n.bkg": int(n_bkg), "sum.bkg": float(g.sum())}
    got = {"bootstrap_seed": rec.get("bootstrap_seed"), "seed_offsets.bkg": rec.get("seed_offsets", {}).get("bkg"),
           "n.bkg": rec.get("n", {}).get("bkg"), "sum.bkg": rec.get("sum", {}).get("bkg")}
    return [f"{k}: record {got[k]!r} != regenerated {v!r}" for k, v in want.items() if got[k] != v]


# ---------------------------------------------------------------- K: the quadrant algebra


def quadrant_vectors(defn: dict, cells2d: np.ndarray, area: np.ndarray, e_pt, e_pz):
    """A (4 x 16): the reported cells of each quadrant (fd_gencmp.QUADRANTS, checked against the definition by
    fd_gencmp.quadrant_cells); B (4 x 205): each quadrant's 2D bins with their areas, by bin centre, as
    fd_gencmp.cmd_overlap forms them."""
    qc = gc.quadrant_cells(defn)
    A = np.zeros((N_Q, gc.N_CELLS))
    B = np.zeros((N_Q, len(cells2d)))
    ipt, ipz = np.unravel_index(np.asarray(cells2d, int), (len(e_pt) - 1, len(e_pz) - 1))
    cpt, cpz = 0.5 * (e_pt[ipt] + e_pt[ipt + 1]), 0.5 * (e_pz[ipz] + e_pz[ipz + 1])
    for i, q in enumerate(QNAMES):
        Qd = gc.QUADRANTS[q]
        if qc[q]["cells"] != Qd["cells"]:
            raise Stop("K", f"{q}'s cells are not the definition's")
        A[i, Qd["cells"]] = 1.0
        inq = (Qd["pt"][0] < cpt) & (cpt < Qd["pt"][1]) & (Qd["pz"][0] < cpz) & (cpz < Qd["pz"][1])
        B[i] = np.where(inq, area, 0.0)
    return A, B


def cross_cov(X16: np.ndarray, X2: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    """The cross block of one band between paired universes, by the rule each side's own block uses (MAT CalcCovMx,
    s1_assemble.mat_cov and build_repair.wcov): weighted mean-centred, normalised by the weight sum. X16 (n x 4) and X2
    (n x 4) are the quadrant sums of the same n universes; mat_cov(X) is cross_cov(X, X)."""
    X16, X2 = np.asarray(X16, float), np.asarray(X2, float)
    if X16.shape[0] != X2.shape[0]:
        raise Stop("K", "the two sides hold different universe counts")
    w = np.ones(X16.shape[0]) if w is None else np.asarray(w, float)
    m16, m2 = (w @ X16) / w.sum(), (w @ X2) / w.sum()
    return ((X16 - m16).T * w) @ (X2 - m2) / w.sum()


def outer_pairs(V16: list[np.ndarray], V2: list[np.ndarray]) -> np.ndarray:
    """sum_k v16_k v2_k^T over paired component vectors (quadrant sums): the cross term of two blocks built as sums of
    outer products over the same components (periods, generator vertices)."""
    if len(V16) != len(V2):
        raise Stop("K", "the two sides hold different component counts")
    return sum(np.outer(a, b) for a, b in zip(V16, V2))


def psd_sqrt(M: np.ndarray) -> np.ndarray:
    lam, V = np.linalg.eigh((M + M.T) / 2)
    return (V * np.sqrt(np.clip(lam, 0, None))) @ V.T


def chi2_sf4(x: float) -> float:
    """The chi2 survival function for 4 degrees of freedom: exp(-x/2)(1 + x/2), exact."""
    return float(np.exp(-x / 2) * (1 + x / 2))


def verdict(d: np.ndarray, Vd: np.ndarray) -> dict:
    """Ruling 3: agree iff the joint chi2_4 of the four d under Vd has p >= 0.05 AND every |z| <= 2.50. A quadrant
    with |z| > 2.50 is a named "differ"; a joint p < 0.05 with no quadrant over is a "differ" of the joint."""
    lam = np.linalg.eigvalsh((Vd + Vd.T) / 2)
    if lam.min() <= PD_REL * lam.max():
        raise Stop("K", f"V_d is not positive definite (eigenvalues {lam.min():.3e} .. {lam.max():.3e})")
    z = d / np.sqrt(np.diag(Vd))
    chi2 = float(d @ np.linalg.solve(Vd, d))
    p = chi2_sf4(chi2)
    over = [QNAMES[i] for i in range(N_Q) if abs(z[i]) > Z_MAX]
    out = {"z": z.tolist(), "chi2_4": chi2, "p": p, "quadrants_over": over}
    if over:
        out["outcome"], out["named"] = "differ", over
    elif p < P_MIN:
        out["outcome"], out["named"] = "differ", ["joint"]
    else:
        out["outcome"], out["named"] = "agree", []
    return out


def Vd_of(C16q, C2q, K) -> np.ndarray:
    """The covariance of d = S16 - S2D: C16 + C2D - K - K^T, all at quadrant level."""
    return C16q + C2q - K - K.T


def bound_matrix(S16: np.ndarray, S2: np.ndarray) -> np.ndarray:
    """An unpaired block's bounded cross term at r = 1: S16^1/2 S2D^1/2, which keeps the joint matrix
    [[S16, rM], [rM^T, S2D]] PSD for every r in [0, 1] (it is diag(S16^1/2, S2D^1/2) [[I, rI], [rI, I]] diag(...))."""
    return psd_sqrt(S16) @ psd_sqrt(S2)


def route_a(d, C16q, C2q, K_rest, M, grid: int = 10001) -> dict:
    """The fallback (ruling 1): the cross terms r * M (M the sum of bound_matrix over the unbounded-pairing blocks),
    read on the whole grid r in [0, 1]: one reading if it never changes, otherwise "<reading at 0> only if r < r*", r*
    the first change (every change is listed). This is a one-parameter family, not every admissible correlation."""
    rs = np.linspace(0, 1, grid)
    outs = [verdict(d, Vd_of(C16q, C2q, K_rest + r * M))["outcome"] for r in rs]
    changes = [float(rs[i]) for i in range(1, grid) if outs[i] != outs[i - 1]]
    out = {"r0": verdict(d, Vd_of(C16q, C2q, K_rest)), "r1": verdict(d, Vd_of(C16q, C2q, K_rest + M)),
           "r_star": changes[0] if changes else None, "changes_at": changes}
    if not changes:
        return {**out, "outcome": outs[0]}
    return {**out, "outcome": f"{outs[0]} only if r < r*"}


def stat_cross(S16_reps: np.ndarray, S2_reps: np.ndarray, sig16: np.ndarray, sig2: np.ndarray) -> dict:
    """Route B: the paired sample correlation R of the quadrant sums (n replicas x 4 each side), scaled by each side's
    stated statistical sigmas, K_stat = R * sig16 sig2^T; with the jackknife SE of the diagonal correlations."""
    n = S16_reps.shape[0]
    Z = np.corrcoef(np.hstack([S16_reps, S2_reps]), rowvar=False)
    R = Z[:N_Q, N_Q:]
    jk = []
    for i in range(n):
        keep = np.arange(n) != i
        Zi = np.corrcoef(np.hstack([S16_reps[keep], S2_reps[keep]]), rowvar=False)
        jk.append(np.diag(Zi[:N_Q, N_Q:]))
    jk = np.array(jk)
    se = np.sqrt((n - 1) / n * ((jk - jk.mean(axis=0)) ** 2).sum(axis=0))
    return {"R": R, "K": R * np.outer(sig16, sig2), "rho_diag": np.diag(R), "rho_diag_jackknife_se": se}


def shares(blocks16: dict, blocks2: dict, crosses: dict, Vd: np.ndarray) -> dict:
    """Each block's share of each quadrant's sigma_d^2: own blocks add, a cross block subtracts twice its diagonal."""
    tot = np.diag(Vd)
    out = {f"16:{k}": (np.diag(v) / tot).tolist() for k, v in blocks16.items()}
    out.update({f"2D:{k}": (np.diag(v) / tot).tolist() for k, v in blocks2.items()})
    out.update({f"cross:{k}": (-2 * np.diag(v) / tot).tolist() for k, v in crosses.items()})
    return out


# ---------------------------------------------------------------- CLI (the cluster steps read their declared inputs)


def build_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("v0", "v1", "k"):
        s = sub.add_parser(name)
        s.add_argument("--run-dir", type=Path, required=True)
        s.add_argument("--probe", action="store_true", help="v1 only: one band and Flux 0-9, then the price")
        s.add_argument("--dry", action="store_true", help="v1 only: every lookup, no weight array read, nothing written")
        s.add_argument("--own-only", action="store_true",
                       help="k only: K0, K1 and K2 on each side's own matrices; no cross block, z or chi2; nothing written")
    s = sub.add_parser("boot")
    s.add_argument("--run-dir", type=Path, required=True)
    s.add_argument("--replicas", required=True, help="first:last of the bootstrap seeds this lane runs")
    s.add_argument("--native", action="store_true", help="control B0: the unreplaced bootstrap_replica")
    s.add_argument("--threads", type=int, default=32)
    return p.parse_args(argv)


def main(argv=None) -> int:
    import fd_xcov_steps as S                       # the cluster steps, which read the declared files
    a = build_args(argv)
    return {"v0": S.cmd_v0, "v1": S.cmd_v1, "boot": S.cmd_boot, "k": S.cmd_k}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())


def same_block(a, b, tol: float = K_TOL) -> bool:
    """K1's comparison: equal to ``tol`` relative to the larger matrix's largest entry, with no absolute floor (the
    blocks' entries are ~1e-80, below numpy's default atol). Two exactly-zero blocks are the same block (addendum
    X-A2: a band whose universes are identical, e.g. NormDISCC on CC signal, has a zero block on both sides)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        return False
    scale = max(np.abs(a).max(), np.abs(b).max())
    if scale == 0:
        return True
    return bool(np.all(np.abs(a - b) <= tol * scale))


def ratio_test(w2u, w2c, w5u, w5c, sentinel) -> dict:
    """V1 for one weight of one universe: the quotient of the two sides' universe-to-CV ratios on the rows where both
    CV weights are non-zero (sentinel rows excepted) must be one constant to RATIO_TOL; non-finite quotients fail."""
    w2u, w2c, w5u, w5c = (np.asarray(v, float) for v in (w2u, w2c, w5u, w5c))
    use = (w2c != 0) & (w5c != 0) & ~np.asarray(sentinel, bool)
    with np.errstate(divide="ignore", invalid="ignore"):
        q = (w5u[use] / w5c[use]) / (w2u[use] / w2c[use])
    fin = np.isfinite(q)
    med = float(np.median(q[fin])) if fin.any() else float("nan")
    rel = float(np.max(np.abs(q[fin] / med - 1))) if fin.any() else float("inf")
    return {"rows": int(use.sum()), "nonfinite": int((~fin).sum()), "scale": med, "max_rel": rel,
            "pass": bool(rel <= RATIO_TOL and (~fin).sum() == 0 and use.sum() > 0)}


def joint_psd(S16: np.ndarray, S2: np.ndarray, K: np.ndarray, tol: float = PD_REL) -> bool:
    """K2: the joint matrix [[S16, K], [K^T, S2]] is positive semidefinite (smallest eigenvalue >= -tol * largest)."""
    J = np.block([[S16, K], [K.T, S2]])
    lam = np.linalg.eigvalsh((J + J.T) / 2)
    return bool(lam.min() >= -tol * lam.max())


def r_band(d, C16q, C2q, K_rest, R, se, sig16, sig2) -> dict:
    """Information only (route B; the director's rule is unchanged): the reading with route B's diagonal correlations
    moved by -1 and +1 jackknife SE (clipped to [-1, 1]), to show how sensitive a reading is to R's sampling error."""
    out = {}
    for name, sgn in (("minus_se", -1.0), ("plus_se", 1.0)):
        Rm = np.array(R, float, copy=True)
        np.fill_diagonal(Rm, np.clip(np.diag(Rm) + sgn * np.asarray(se), -1.0, 1.0))
        try:
            out[name] = verdict(d, Vd_of(C16q, C2q, K_rest + Rm * np.outer(sig16, sig2)))
        except Stop as e:
            out[name] = {"stop": str(e)}
    return out
