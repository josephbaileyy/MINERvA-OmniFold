#!/usr/bin/env python3
"""V-HALF-R's binning builder: the candidate binnings C0-C8, from the simulation only (DECLARATION.md §1.2-§1.3 and §6;
AMENDMENT-1 A2-A5, A3.4, A4 and A7.1's T2/T3; V-HALF-R-BINDING-1).

What it does, per candidate:
  - the response populations of AMENDMENT-1 A2 on the candidate's base cells (fine cells of its axes, or the H2 boxes for
    C0), within the fixed mask Ω, from the MC rows: same (w_reco), reco_all (w_reco, any truth), truth_reco (w_reco,
    reco anywhere) and truth_sel (w_truth);
  - A3.4's structural check (C6, C7) before merging;
  - the merge of A4: a bin is low if min(purity, diagonal fraction) < 0.5 or it fails support; joins in A4.2's order,
    with A3.1's strip refusal and A3.4's 80 % veto (C6, C7) and A5's p∥ = 4.5 refusal (C0, C2, C6);
  - the outcome of A7.1 that is known from the binning alone: T2 (floor; two-dimensional resolution, structural or
    final) and T3 (a bin below 0.5 in either fraction or below 1000 in either support sum). A candidate with neither
    proceeds to grading, which this module does not do.
The reproduction mode (A4.5) is h2_definition.merge's rule exactly: purity < τ among supported bins only.

The 80 % veto is read, as the director ruled (2026-11-11), as refusing a join that takes a touched line's largest piece
from at most 0.8 to above it. A line already above 0.8 is a structural failure, which ends its candidate at T2. See
IMPLEMENTATION-NOTES.md, note 1, for the reading and its monotonicity argument.

Inputs: MCgen, MCreco, pass_reco, pass_truth, w_truth and w_reco of the pinned 5D npz, read through O_NOATIME after its
sha256. No data array, unfold product, bias, departure or V-HALF quantity is read.
MEASURES: simulation response on candidate bins. CANNOT AUTHORIZE: a reported binning, a class or any claim.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]
sys.path.insert(0, str(REPO / "nd-unfolding"))
import s5p_stage1_inspect as s1  # noqa: E402

NPZ_SHA256 = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
H2_DEF = REPO / "nd-unfolding/pv-ladder/readouts/h2_definition.json"
H2_DEF_SHA256 = "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89"
MC_KEYS = ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco")
NOATIME = getattr(os, "O_NOATIME", 0)

AXES = s1.AXES
NFINE = {a: len(s1.FINE[a]) - 1 for a in AXES}
CRIT = 0.5            # A4.1: min(purity, diagonal fraction) >= 0.5
SUPPORT_MIN = s1.SUPPORT_MIN   # 1000, in reco_all and in truth_sel
SHARE = 0.2           # A3.4: two pieces of at least 0.2 in every row and column
VETO = 1.0 - SHARE    # A3.4: a join is refused if a touched line's largest piece would exceed 0.8
PZ_SPLIT = s1.FINE["pz"].index(4.5)   # fine p∥ index of the 4.5 GeV/c edge (A5)
FLOOR = {1: 3, 2: 6}  # D:107-111
C0_FLOOR, C0_PER_SIDE = 8, 4

# id: (axes, p∥ edge frozen (A5), two-dimensional rules A3.1 and A3.4)
CANDIDATES = {
    "C1": (("pt",), False, False), "C2": (("pz",), True, False), "C3": (("eavail",), False, False),
    "C4": (("q3",), False, False), "C5": (("W",), False, False), "C6": (("pt", "pz"), True, True),
    "C7": (("eavail", "q3"), False, True), "C8": (("eavail", "W"), False, False),
}


class Stop(Exception):
    """A refusal: the run stops and nothing is built."""


def require(ok, msg):
    if not ok:
        raise Stop(msg)


# ---------------------------------------------------------------------------------------------------- the mask Ω
def h2_definition(path=H2_DEF, expect=H2_DEF_SHA256):
    raw = Path(path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == expect, "h2_definition.json's sha256 differs from the pin")
    return json.loads(raw)


def omega_mask(h2def):
    """Ω over the flat fine grid (A2), and the H2 box of each fine cell; checked against the record's fine map."""
    h2_of_fine, n = s1.coarse_map(s1.H2_EDGES)
    require(n == 32, "the H2 grid is not 32 boxes")
    lut = np.asarray(h2def["h2_to_reporting_cell"], dtype=np.int64)
    fmap = lut[h2_of_fine].astype("<i4")
    require(hashlib.sha256(fmap.tobytes()).hexdigest() == h2def["fine_map_sha256_int32le"],
            "the fine map built from the grid differs from h2_definition.json's")
    return fmap >= 0, h2_of_fine


def fine_axis_index():
    """For each flat fine cell, its index on each of the five axes."""
    return dict(zip(AXES, np.unravel_index(np.arange(int(np.prod([NFINE[a] for a in AXES]))),
                                           tuple(NFINE[a] for a in AXES))))


# ------------------------------------------------------------------------------------------- response populations
class Response:
    """A2's four populations on a set of base cells. Any bin's figures are sums over its cells."""

    def __init__(self, M, reco_all, truth_reco, truth_sel, shape=None):
        self.M = np.asarray(M, float)
        self.reco_all, self.truth_reco, self.truth_sel = (np.asarray(x, float) for x in (reco_all, truth_reco,
                                                                                          truth_sel))
        self.n = self.M.shape[0]
        self.shape = shape or (self.n,)
        self.inside_col = self.M.sum(axis=0)    # reco in the cell, truth in a base cell (pass_truth, in Ω)
        self.inside_row = self.M.sum(axis=1)    # truth in the cell, reco in a base cell (in Ω)

    @classmethod
    def from_events(cls, gen, reco, pass_reco, pass_truth, w_truth, w_reco, base_of_fine, n, shape=None):
        """base_of_fine: the base cell of each flat fine cell, -1 outside Ω (or outside the candidate)."""
        ft, fr = s1.fine_index(np.asarray(gen, float)), s1.fine_index(np.asarray(reco, float))
        bt = np.where(ft >= 0, base_of_fine[np.maximum(ft, 0)], -1)
        br = np.where(fr >= 0, base_of_fine[np.maximum(fr, 0)], -1)
        pr, pt = np.asarray(pass_reco, bool), np.asarray(pass_truth, bool)
        wt, wr = np.asarray(w_truth, float), np.asarray(w_reco, float)
        both = pr & pt & (bt >= 0) & (br >= 0)
        M = np.bincount(bt[both] * n + br[both], weights=wr[both], minlength=n * n).reshape(n, n)
        ra = np.bincount(br[pr & (br >= 0)], weights=wr[pr & (br >= 0)], minlength=n)
        tr = np.bincount(bt[pt & pr & (bt >= 0)], weights=wr[pt & pr & (bt >= 0)], minlength=n)
        ts = np.bincount(bt[pt & (bt >= 0)], weights=wt[pt & (bt >= 0)], minlength=n)
        return cls(M, ra, tr, ts, shape)

    def of(self, cells):
        u = np.asarray(sorted(cells))
        same = self.M[np.ix_(u, u)].sum()
        ra, tr, ts = (float(x[u].sum()) for x in (self.reco_all, self.truth_reco, self.truth_sel))
        purity = same / ra if ra > 0 else 0.0
        diag = same / tr if tr > 0 else 0.0
        return {"purity": purity, "diagonal_fraction": diag, "reco_all": ra, "truth_reco": tr, "truth_sel": ts,
                "supported": bool(ra >= SUPPORT_MIN and ts >= SUPPORT_MIN),
                "in_share": (ra - float(self.inside_col[u].sum())) / ra if ra > 0 else 0.0,
                "out_share": (tr - float(self.inside_row[u].sum())) / tr if tr > 0 else 0.0}


# ---------------------------------------------------------------------------------------------------- geometry
class Grid:
    """Bins of a 1D or 2D candidate: rectangles of fine indices, ((lo, hi), ...) inclusive, one pair per axis."""

    def __init__(self, axes, freeze_pz, two_d_rules, dims=None):
        self.axes, self.freeze_pz, self.two_d = axes, freeze_pz, two_d_rules
        self.dims = tuple(dims) if dims is not None else tuple(NFINE[a] for a in axes)   # dims: tests only

    def start(self):
        return [tuple((i, i) for i in idx) for idx in np.ndindex(*self.dims)]

    def cells(self, b):
        mesh = np.meshgrid(*[np.arange(lo, hi + 1) for lo, hi in b], indexing="ij")
        return np.ravel_multi_index([g.ravel() for g in mesh], self.dims).tolist()

    def first(self, b):
        return int(np.ravel_multi_index(tuple(lo for lo, _ in b), self.dims))

    def join_axis(self, a, b):
        diff = [k for k in range(len(a)) if a[k] != b[k]]
        if len(diff) != 1:
            return None
        k = diff[0]
        (alo, ahi), (blo, bhi) = a[k], b[k]
        return k if ahi + 1 == blo or bhi + 1 == alo else None

    def union(self, a, b, k):
        return tuple((min(a[i][0], b[i][0]), max(a[i][1], b[i][1])) if i == k else a[i] for i in range(len(a)))

    def refused(self, u, k):
        """A5's p∥ edge and A3.1's strips. Returns the reason, or None."""
        if self.freeze_pz and self.axes[k] == "pz" and u[k][0] < PZ_SPLIT <= u[k][1]:
            return "p_par 4.5 edge (A5)"
        if self.two_d and any(lo == 0 and hi == n - 1 for (lo, hi), n in zip(u, self.dims)):
            return "full strip (A3.1)"
        return None

    def describe(self, b):
        return {a: [s1.FINE[a][lo], s1.FINE[a][hi + 1]] for a, (lo, hi) in zip(self.axes, b)}


class Boxes:
    """C0 and the reproduction mode: bins are sets of H2 boxes, joined into boxes on the five axes (H:46-59)."""

    def __init__(self, start_bins, freeze_pz):
        self.start_bins, self.freeze_pz = start_bins, freeze_pz

    def start(self):
        return [tuple(sorted(b)) for b in self.start_bins]

    def cells(self, b):
        return list(b)

    def first(self, b):
        return b[0]

    @staticmethod
    def bits(c):
        return tuple((c >> (4 - k)) & 1 for k in range(5))

    def box_of(self, cells):
        sets = [sorted({self.bits(c)[k] for c in cells}) for k in range(5)]
        return tuple(tuple(x) for x in sets) if int(np.prod([len(x) for x in sets])) == len(cells) else None

    def join_axis(self, a, b):
        ba, bb = self.box_of(a), self.box_of(b)
        if ba is None or bb is None:
            return None
        diff = [k for k in range(5) if ba[k] != bb[k]]
        if len(diff) != 1:
            return None
        k = diff[0]
        return k if not set(ba[k]) & set(bb[k]) else None

    def union(self, a, b, k):
        return tuple(sorted(a + b))

    def refused(self, u, k):
        return "p_par 4.5 edge (A5; D:117)" if self.freeze_pz and AXES[k] == "pz" else None

    def describe(self, b):
        return {"h2_cells": list(b)}


# ------------------------------------------------------------------------------------- A3.4: rows and columns
def lines(grid):
    """The rows and columns of a 2D candidate: (name, [base cells in order along the line])."""
    nx, ny = grid.dims
    out = [(f"row {grid.axes[1]}[{j}]", [int(np.ravel_multi_index((i, j), grid.dims)) for i in range(nx)])
           for j in range(ny)]
    out += [(f"column {grid.axes[0]}[{i}]", [int(np.ravel_multi_index((i, j), grid.dims)) for j in range(ny)])
            for i in range(nx)]
    return out


def structural_failures(resp, grid):
    """A3.4 (1): a line admits the rule only if some cut leaves at least 0.2 of its truth_sel on each side."""
    fails, empty = [], []
    for name, cells in lines(grid):
        w = resp.truth_sel[cells]
        tot = float(w.sum())
        if tot <= 0:
            empty.append(name)
            continue
        left = np.cumsum(w)[:-1]
        if not np.any((left >= SHARE * tot) & (tot - left >= SHARE * tot)):
            fails.append({"line": name, "shares": (w / tot).tolist()})
    return fails, empty


def piece_shares(resp, cells, bin_of):
    tot = float(resp.truth_sel[cells].sum())
    acc = {}
    for c in cells:
        acc[bin_of[c]] = acc.get(bin_of[c], 0.0) + float(resp.truth_sel[c])
    return tot, sorted((v / tot for v in acc.values()), reverse=True) if tot > 0 else []


def veto(resp, grid, line_list, bin_of, union_cells, union_id):
    """A3.4 (2): True if the join (union_cells relabelled union_id) pushes a touched line's largest piece from at most
    0.8 to above it. A line already above 0.8 before the join is a structural failure (A3.4 (1)), which ends the
    candidate; it does not veto joins by itself."""
    trial = dict(bin_of)
    for c in union_cells:
        trial[c] = union_id
    touched = set(union_cells)
    for _, cells in line_list:
        if touched.isdisjoint(cells):
            continue
        tot, after = piece_shares(resp, cells, trial)
        if tot <= 0:
            continue
        _, before = piece_shares(resp, cells, bin_of)
        if before[0] <= VETO < after[0]:
            return True
    return False


def final_two_piece_failures(resp, grid, bin_of):
    """A3.4 (3): every line with signal must hold two pieces of at least 0.2."""
    fails = []
    for name, cells in lines(grid):
        tot, shares = piece_shares(resp, cells, bin_of)
        if tot > 0 and sum(s >= SHARE for s in shares) < 2:
            fails.append({"line": name, "piece_shares": shares})
    return fails


# ---------------------------------------------------------------------------------------------------- the merge
def merge(resp, geom, mode="candidate", tau=0.1, two_d=False, grid=None):
    """A4's merge (mode "candidate") or h2_definition.merge's rule exactly (mode "repro", A4.5)."""
    bins = geom.start()
    steps, flagged = [], []
    line_list = lines(grid) if two_d else []

    def value(b):
        f = resp.of(geom.cells(b))
        return f["purity"] if mode == "repro" else min(f["purity"], f["diagonal_fraction"])

    def low(b):
        f = resp.of(geom.cells(b))
        if mode == "repro":
            return f["supported"] and f["purity"] < tau
        return min(f["purity"], f["diagonal_fraction"]) < CRIT or not f["supported"]

    while True:
        lows = [(value(b), geom.first(b), i) for i, b in enumerate(bins) if low(b) and geom.first(b) not in flagged]
        if not lows:
            break
        v, _, i = min(lows)
        a = bins[i]
        if two_d:
            bin_of = {c: geom.first(b) for b in bins for c in geom.cells(b)}
        cand, refusals = [], []
        for j, b in enumerate(bins):
            if j == i:
                continue
            k = geom.join_axis(a, b)
            if k is None:
                continue
            u = geom.union(a, b, k)
            why = geom.refused(u, k)
            if why is None and two_d and veto(resp, grid, line_list, bin_of, geom.cells(u), -1):
                why = "80 % veto (A3.4)"
            if why is not None:
                refusals.append({"partner": geom.describe(b), "reason": why})
                continue
            cand.append((-value(u), k, geom.first(b), j))
        if not cand:
            flagged.append(geom.first(a))
            steps.append({"bin": geom.describe(a), "value": v, "partner": None, "refused": refusals})
            continue
        q, k, _, j = min(cand)
        u = geom.union(a, bins[j], k)
        steps.append({"bin": geom.describe(a), "value": v, "partner": geom.describe(bins[j]), "axis": k,
                      "union_value": -q, "refused": refusals})
        bins = [b for t, b in enumerate(bins) if t not in (i, j)] + [u]
    return sorted(bins, key=geom.first), steps, flagged


# ------------------------------------------------------------------------------------------------- a candidate
def c0_start(h2def):
    return [tuple(sorted(c["h2_cells"])) for c in h2def["reporting_cells"]]


def outcome(resp, geom, bins, cid, structural, final2d):
    """The failures known from the binning alone (A7.1), each listed."""
    out = []
    if cid == "C0":
        lo = sum(1 for b in bins if geom.box_of(b)[1] == (0,))
        hi = sum(1 for b in bins if geom.box_of(b)[1] == (1,))
        if len(bins) < C0_FLOOR or lo < C0_PER_SIDE or hi < C0_PER_SIDE:
            out.append({"T2": "minimum", "bins": len(bins), "below_4.5": lo, "above_4.5": hi})
    elif len(bins) < FLOOR[len(geom.axes)]:
        out.append({"T2": "minimum", "bins": len(bins)})
    if structural:
        out.append({"T2": "two-dimensional resolution: structural", "lines": structural})
    if final2d:
        out.append({"T2": "two-dimensional resolution: final", "lines": final2d})
    t3 = []
    for b in bins:
        f = resp.of(geom.cells(b))
        bad = [q for q, failed in (("purity", f["purity"] < CRIT), ("diagonal fraction", f["diagonal_fraction"] < CRIT),
                                   ("reco_all", f["reco_all"] < SUPPORT_MIN),
                                   ("truth_sel", f["truth_sel"] < SUPPORT_MIN)) if failed]
        if bad:
            t3.append({"bin": geom.describe(b), "failing": bad})
    if t3:
        out.append({"T3": t3})
    return out


def landmarks_c7(geom, bins):
    """A3.3: where C7's final q3 edges fall relative to 0.8 and 1.2 GeV (a description only)."""
    k = geom.axes.index("q3")
    edges = sorted({s1.FINE["q3"][b[k][0]] for b in bins} - {s1.FINE["q3"][0]})
    return [{"q3_edge": e, "vs_0.8": "equal" if e == 0.8 else ("below" if e < 0.8 else "above"),
             "vs_1.2": "equal" if e == 1.2 else ("below" if e < 1.2 else "above")} for e in edges]


def build(cid, arrays, omega, h2_of_fine, h2def):
    """One candidate's binning and its outcome so far. arrays: the six MC keys."""
    if cid == "C0":
        base = np.where(omega, h2_of_fine, -1)
        resp = Response.from_events(*(arrays[k] for k in MC_KEYS), base_of_fine=base, n=32)
        geom, grid, two_d = Boxes(c0_start(h2def), freeze_pz=True), None, False
    else:
        axes, freeze, two_d = CANDIDATES[cid]
        geom = grid = Grid(axes, freeze, two_d)
        idx = fine_axis_index()
        base = np.ravel_multi_index(tuple(idx[a] for a in axes), grid.dims)
        base = np.where(omega, base, -1)
        resp = Response.from_events(*(arrays[k] for k in MC_KEYS), base_of_fine=base, n=int(np.prod(grid.dims)),
                                    shape=grid.dims)
    structural, empty = structural_failures(resp, grid) if two_d else ([], [])
    bins, steps, flagged = merge(resp, geom, two_d=two_d, grid=grid)
    final2d = final_two_piece_failures(resp, grid, {c: geom.first(b) for b in bins for c in geom.cells(b)}) \
        if two_d else []
    bin_of_base = -np.ones(resp.n, np.int64)
    for r, b in enumerate(bins):
        bin_of_base[geom.cells(b)] = r
    fmap = np.where(base >= 0, bin_of_base[np.maximum(base, 0)], -1).astype("<i4")
    rec = {"candidate": cid, "bins": [dict(geom.describe(b), **resp.of(geom.cells(b))) for b in bins],
           "n_bins": len(bins), "flagged": flagged, "steps": steps, "outcome": outcome(resp, geom, bins, cid,
                                                                                         structural, final2d),
           "empty_lines": empty, "fine_map_sha256_int32le": hashlib.sha256(fmap.tobytes()).hexdigest()}
    rec["status"] = "terminal (binning alone)" if rec["outcome"] else "proceeds to grading"
    if cid == "C7":
        rec["q3_landmarks"] = landmarks_c7(geom, bins)
    return rec, fmap


# -------------------------------------------------------------------------------------------------------- input
def load_mc(npz_path, expect=NPZ_SHA256):
    fd = os.open(npz_path, os.O_RDONLY | NOATIME)
    with os.fdopen(fd, "rb") as fh:
        h = hashlib.sha256()
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
        require(h.hexdigest() == expect, "the npz's sha256 differs from the pin")
        fh.seek(0)
        with np.load(fh, allow_pickle=False) as z:
            require(all(k in z.files for k in MC_KEYS), f"the npz lacks one of {MC_KEYS}")
            arrays = {k: np.asarray(z[k]) for k in MC_KEYS}
    n = arrays["MCgen"].shape[0]
    require(arrays["MCgen"].shape == arrays["MCreco"].shape == (n, len(AXES)), "MCgen or MCreco has the wrong shape")
    require(all(arrays[k].shape == (n,) for k in MC_KEYS[2:]), "a per-row key has the wrong length")
    return arrays


def check_weights(arrays, omega):
    """A3.4: every w_truth a share counts is finite and nonnegative; every w_reco counted is finite."""
    ft = s1.fine_index(np.asarray(arrays["MCgen"], float))
    fr = s1.fine_index(np.asarray(arrays["MCreco"], float))
    t_in = (ft >= 0) & omega[np.maximum(ft, 0)]
    r_in = (fr >= 0) & omega[np.maximum(fr, 0)]
    wt, wr = np.asarray(arrays["w_truth"], float), np.asarray(arrays["w_reco"], float)
    pt, pr = np.asarray(arrays["pass_truth"], bool), np.asarray(arrays["pass_reco"], bool)
    m = pt & t_in
    require(bool(np.all(np.isfinite(wt[m])) and np.all(wt[m] >= 0)), "a counted w_truth is negative or not finite")
    require(bool(np.all(np.isfinite(wr[pr & (t_in | r_in)]))), "a counted w_reco is not finite")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--npz", required=True)
    ap.add_argument("--out", type=Path, required=True, help="a new directory")
    ap.add_argument("--candidates", default="C0,C1,C2,C3,C4,C5,C6,C7,C8")
    a = ap.parse_args(argv)
    if sys.platform.startswith("linux") and not NOATIME:
        print("STOP: O_NOATIME is unavailable on this Linux build")
        return 2
    try:
        h2def = h2_definition()
        omega, h2_of_fine = omega_mask(h2def)
        arrays = load_mc(a.npz)
        check_weights(arrays, omega)
        a.out.mkdir()
        summary = {}
        for cid in a.candidates.split(","):
            require(cid == "C0" or cid in CANDIDATES, f"unknown candidate {cid}")
            rec, fmap = build(cid, arrays, omega, h2_of_fine, h2def)
            with (a.out / f"binning_{cid}.json").open("x") as f:
                json.dump(rec, f, indent=1, sort_keys=True, allow_nan=False)
                f.write("\n")
            np.save(a.out / f"fine_map_{cid}.npy", fmap)
            summary[cid] = {"n_bins": rec["n_bins"], "status": rec["status"],
                            "outcome": [next(iter(o)) + ": " + str(next(iter(o.values())))[:60] for o in rec["outcome"]]}
        print(json.dumps(summary, indent=1))
    except Stop as e:
        print(f"STOP: {e}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
