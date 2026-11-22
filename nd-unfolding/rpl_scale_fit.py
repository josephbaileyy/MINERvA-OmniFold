#!/usr/bin/env python3
"""RPL check (i): the per-period muon-momentum scale fit for the run-period step.

Implements check (i) of RPL-DECLARATION.md (bound by RPL-BINDING-1.md at a1a8b161) on the records of RPD-RECO
(FD-RPD-RECO-DECLARATION.md). It runs only after precondition P-RPD: RPD-RECO's passing d1 and d2 records, named by
sha256, with their c0 histogram product.

The statistic. D_G(b) = r_G(b) / r_PA(b) on RPD-RECO's p_par bins and its combined under/overflow bin, with
r = N / P (RPD-RECO section 2, variant 0: the unswapped prediction, signal plus background). The model scales G's data
muon momentum p -> p / (1 + alpha), p_T and p_par together, over the whole measured set, and re-bins it. A row lands in
[lo, hi) after the scale exactly when lo (1 + alpha) <= p_par < hi (1 + alpha), so the code bins each row once against
the edges scaled at every alpha of the declared 0.01 % lattice. The coarse grid (0.5 %) and the fine grid (0.01 %) both
lie on that lattice. chi2(alpha, k) = sum_b (k D_alpha(b) - 1)^2 / sigma_b^2, with k profiled analytically and sigma_b
the paired-bootstrap SD of D(b) at alpha = 0, held fixed. alpha-hat is the vertex of the parabola through the three fine
points nearest the fine minimum. sigma_alpha is the SD of alpha-hat refitted on each of RPD-RECO's 200 replicas.

The replicas. RPD-RECO's aggregate() draws Poisson(1) weights from SeedSequence([20261104, 11, r + 1]) streamed over
signal, background, then data rows, in its playlist order and 65,536-row chunks. This module streams the same samples
through RPD-RECO's own Inputs.samples and makes the same draws in the same order, so each data row carries the same
replica weights as in RPD-RECO's c0 product. Control R0 requires that, at alpha = 0, every playlist's p_par histogram
in every replica equals c0's exactly, and that R-d1.0's s_PB is reproduced to 1e-12 relative (the declared control).

The planted-scale control (audit M2, recheck R5) splits PA's and PB's simulated signal and background rows 50/50 with
SeedSequence([20261110, 17, 1]) into pseudo-data and prediction halves (each sum x 2), scales PB's pseudo-data momentum
by (1 + alpha_true) for alpha_true = +1 % and +3 %, and requires |alpha-hat - alpha_true| <= 3.5 sigma_alpha. Its
replicas are the same RPD-RECO draws those simulated rows carry.

Every control is a STOP that reports the check as not made; no reading is formed after a STOP. NOT CITABLE FOR: the
cause of the step; that the muon-energy band covers, accounts for or absorbs the step; which period is right; any
change to C_PL,5D, a covariance or a result; coverage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence

import numpy as np
from numpy.typing import NDArray

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fd_rpd_reco as R  # noqa: E402  (RPD-RECO's own functions, per the declaration)

Json = dict[str, Any]
FloatArray = NDArray[np.float64]

SCHEMA = "rpl-scale-fit/1"
LATTICE_HALF = 1000  # alpha = j / 10000 for j in [-1000, 1000]: [-10 %, +10 %] in 0.01 % steps
COARSE_STRIDE = 50  # 0.5 %
FINE_HALF = 50  # +-0.5 % around the coarse minimum
P_FIT_MIN = 0.01  # NOT-A-SCALE below this goodness-of-fit probability
BAND_SIGMAS = 2.0
PLANTS = (0.01, 0.03)
PLANT_TOLERANCE = 3.5
PLANT_SPLIT_WORDS = (20261110, 17, 1)
REPRODUCTION_RTOL = 1e-12
NBINS = len(R.PZ_EDGES)  # ten [lo, hi) bins and the combined under/overflow bin, as R.bin_indices
STEP_REGIONS = ((0, 6), (6, 8))  # p_par [1.5, 8) = bins 0..5 and [8, 15) = bins 6..7; the rest is region 2
ALPHAS = np.arange(-LATTICE_HALF, LATTICE_HALF + 1) / 10000.0
READINGS = ("SEEN", "NOT-SEEN-AT-3σ")  # R.step_reading's two values; any other R-d1.0 reading is refused
PUBLISHED_SCALE = "1 % (iii/README.md, quote 3b), printed beside sigma_band"
OUTCOMES = (
    "NO-STEP",
    "AT-SCAN-EDGE",
    "NOT-A-SCALE",
    "SCALE-BEYOND-BAND",
    "SCALE-WITHIN-BAND",
    "SCALE-UNRESOLVED-AGAINST-BAND",
)
DOES_NOT_LICENSE = [
    "the cause of the step",
    "that the muon-energy band covers, accounts for or absorbs the step",
    "which period is right",
    "any change to C_PL,5D, any covariance or any result",
    "coverage",
    "paper use without Joseph's decision",
]
require = R.require
Refused = R.Refused


# ----------------------------------------------------------------------------------------------- the lattice of edges


class Lattice:
    """Breakpoints e (1 + alpha_j) for every edge e and lattice alpha_j, and each pair's position among them."""

    def __init__(self, edges: FloatArray = R.PZ_EDGES):
        self.edges = np.asarray(edges, dtype=float)
        values = self.edges[None, :] * (1.0 + ALPHAS[:, None])  # (alpha, edge)
        self.breakpoints = np.unique(values)
        self.position = np.searchsorted(self.breakpoints, values)
        require(
            bool(np.array_equal(self.breakpoints[self.position], values)),
            "LATTICE",
            "a scaled edge is not among the breakpoints",
        )
        self.size = len(self.breakpoints) + 1

    def index(self, pz: FloatArray) -> NDArray[np.int64]:
        """Interval i holds breakpoints[i - 1] <= pz < breakpoints[i] (0 below the first, size - 1 above the last)."""
        return np.searchsorted(self.breakpoints, pz, side="right").astype(np.int64)

    def bins(self, cumulative: FloatArray, j: int) -> FloatArray:
        """Histogram on the edges scaled by (1 + alpha_j), from cumulative interval sums (leading zero), last axis."""
        positions = self.position[j + LATTICE_HALF]
        upper = cumulative[..., positions + 1]  # rows below each scaled edge
        interior = upper[..., 1:] - upper[..., :-1]
        overflow = cumulative[..., -1:] - interior.sum(axis=-1, keepdims=True)
        return np.concatenate([interior, overflow], axis=-1)


def cumulative(histogram: FloatArray) -> FloatArray:
    """Cumulative interval sums along the last axis, with a leading zero."""
    shape = histogram.shape[:-1] + (1,)
    return np.concatenate([np.zeros(shape), np.cumsum(histogram, axis=-1)], axis=-1)


def direct_bins(pz: FloatArray, weights: FloatArray, alpha: float) -> FloatArray:
    """Rescale p_par by 1 / (1 + alpha) and bin with RPD-RECO's own convention (used off the lattice)."""
    index = R.bin_indices(pz / (1.0 + alpha), R.PZ_EDGES)
    return np.bincount(index, weights=weights, minlength=NBINS).astype(float)


# ---------------------------------------------------------------------------------------- the fit and its estimator


def ratio(n_group: FloatArray, p_group: FloatArray, n_ref: FloatArray, p_ref: FloatArray) -> FloatArray:
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.asarray((n_group / p_group) / (n_ref / p_ref), dtype=float)


def profiled_chi2(d: FloatArray, sigma: FloatArray, used: NDArray[np.bool_]) -> tuple[float, float]:
    """chi2 = sum_b (k d_b - 1)^2 / sigma_b^2 at its minimum over k, and that k."""
    w = 1.0 / sigma[used] ** 2
    x = d[used]
    sxx, sx = float(np.sum(w * x * x)), float(np.sum(w * x))
    require(np.isfinite(sxx) and sxx > 0, "FIT_DEGENERATE", "no finite ratio in the used bins")
    k = sx / sxx
    return float(np.sum(w) - sx * sx / sxx), k


def parabola_vertex(x: FloatArray, y: FloatArray) -> tuple[float, bool]:
    """Vertex of the parabola through three points; (middle point, False) if it is not convex."""
    (x0, x1, x2), (y0, y1, y2) = x, y
    denominator = (x0 - x1) * (x0 - x2) * (x1 - x2)
    a = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / denominator
    b = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)) / denominator
    if not a > 0:
        return float(x1), False
    return float(-b / (2 * a)), True


def scan(chi2_at: Callable[[int], float]) -> Json:
    """The declared coarse-then-fine scan over lattice indices j (alpha = j / 10000)."""
    coarse = list(range(-LATTICE_HALF, LATTICE_HALF + 1, COARSE_STRIDE))
    coarse_values = [chi2_at(j) for j in coarse]
    jc = coarse[int(np.argmin(coarse_values))]
    fine = list(range(max(-LATTICE_HALF, jc - FINE_HALF), min(LATTICE_HALF, jc + FINE_HALF) + 1))
    fine_values = [chi2_at(j) for j in fine]
    i = int(np.argmin(fine_values))
    centre = min(max(i, 1), len(fine) - 2)
    points = np.array(fine[centre - 1 : centre + 2]) / 10000.0
    values = np.array(fine_values[centre - 1 : centre + 2])
    vertex, convex = parabola_vertex(points, values)
    return {
        "alpha_hat": vertex,
        "parabola_convex": convex,
        "coarse_min_alpha": jc / 10000.0,
        "fine_min_alpha": fine[i] / 10000.0,
        "fine_min_chi2": fine_values[i],
        "parabola_points": points.tolist(),
        "parabola_chi2": values.tolist(),
    }


def at_scan_edge(result: Json) -> bool:
    edge = LATTICE_HALF / 10000.0
    return bool(abs(result["coarse_min_alpha"]) >= edge or abs(result["alpha_hat"]) >= edge)


class GroupFit:
    """One fitted group against its reference, with every replica's scaled histograms on the lattice.

    scaled_cumulative: (replica, lattice interval + 1) cumulative sums of the fitted group's rows (all members).
    p_group, n_ref, p_ref: (replica, bin) unscaled sums from the histogram product.
    """

    def __init__(
        self,
        lattice: Lattice,
        scaled_cumulative: FloatArray,
        p_group: FloatArray,
        n_ref: FloatArray,
        p_ref: FloatArray,
    ):
        self.lattice = lattice
        self.c = scaled_cumulative
        self.p_group, self.n_ref, self.p_ref = p_group, n_ref, p_ref
        self.used = (p_group[0] >= R.MIN_PREDICTION) & (p_ref[0] >= R.MIN_PREDICTION)
        nominal = self.d_all(0)
        with np.errstate(invalid="ignore"):
            self.sigma = np.std(nominal[1:], axis=0, ddof=1)
        require(
            bool(np.all(np.isfinite(nominal[:, self.used])) and np.all(self.sigma[self.used] > 0)),
            "BOOTSTRAP_VARIANCE",
            "undefined ratio or bootstrap variance in a used bin at alpha = 0",
        )
        self.ndf = int(self.used.sum()) - 2
        require(self.ndf >= 1, "FIT_NDF", "fewer than three used bins")

    def d_all(self, j: int) -> FloatArray:
        return ratio(self.lattice.bins(self.c, j), self.p_group, self.n_ref, self.p_ref)

    def d(self, replica: int, j: int) -> FloatArray:
        n = self.lattice.bins(self.c[replica], j)
        return ratio(n, self.p_group[replica], self.n_ref[replica], self.p_ref[replica])

    def chi2(self, replica: int, j: int) -> float:
        return profiled_chi2(self.d(replica, j), self.sigma, self.used)[0]

    def fit(
        self,
        nominal_chi2_at: Callable[[float], float] | None = None,
        check: Callable[[], None] | None = None,
    ) -> Json:
        """The nominal scan and the 200 replica refits; check (the wall clock) runs before each of the 201 scans.

        nominal_chi2_at evaluates chi2 at alpha-hat off the lattice; without it the fine-grid minimum stands in.
        """
        from scipy.stats import chi2 as chi2_distribution

        tick = check if check is not None else (lambda: None)
        tick()
        result = scan(lambda j: self.chi2(0, j))
        alpha_hats = []
        for r in range(1, R.BOOTSTRAPS + 1):
            tick()
            alpha_hats.append(scan(lambda j, r=r: self.chi2(r, j))["alpha_hat"])
        refits = np.array(alpha_hats)
        sigma_alpha = float(np.std(refits, ddof=1))
        require(np.isfinite(sigma_alpha) and sigma_alpha > 0, "ALPHA_VARIANCE", "undefined sigma_alpha")
        chi2_hat = nominal_chi2_at(result["alpha_hat"]) if nominal_chi2_at is not None else result["fine_min_chi2"]
        chi2_zero = self.chi2(0, 0)
        return {
            **result,
            "sigma_alpha": sigma_alpha,
            "chi2_alpha0": chi2_zero,
            "chi2_alpha_hat": chi2_hat,
            "ndf": self.ndf,
            "p_alpha_hat": float(chi2_distribution.sf(chi2_hat, self.ndf)),
            "p_alpha0": float(chi2_distribution.sf(chi2_zero, self.ndf)),
            "used_bins": np.flatnonzero(self.used).tolist(),
            "excluded_bins": np.flatnonzero(~self.used).tolist(),
            "sigma_b": self.sigma,
            "replica_alpha_hat_at_scan_edge": int(
                np.sum(np.abs(refits) >= LATTICE_HALF / 10000.0)
            ),
        }


def deciding_band(band: Json) -> float:
    """sigma_band for outcomes 4-6: Muon_Energy_MINOS overall. The MINOS strata and MINERvA are descriptions only."""
    require(band.get("schema") == "rpl-bandsize/1", "BAND", "unexpected band record")
    return float(band["sigma_band"]["Muon_Energy_MINOS"]["overall"])


def classify(d1_pb_reading: str, fit: Json | None, sigma_band: float) -> str:
    """The declared outcome table, in order; exactly one applies."""
    require(d1_pb_reading in READINGS, "D1_READING", f"unexpected R-d1.0 PB reading {d1_pb_reading!r}")
    if d1_pb_reading != "SEEN":
        return "NO-STEP"
    assert fit is not None
    if at_scan_edge(fit):
        return "AT-SCAN-EDGE"
    if fit["p_alpha_hat"] < P_FIT_MIN:
        return "NOT-A-SCALE"
    size, error = abs(fit["alpha_hat"]), BAND_SIGMAS * fit["sigma_alpha"]
    if size - error > sigma_band:
        return "SCALE-BEYOND-BAND"
    if size + error <= sigma_band:
        return "SCALE-WITHIN-BAND"
    return "SCALE-UNRESOLVED-AGAINST-BAND"


# ------------------------------------------------------------------------------------------ the inputs and the stream


class Reader:
    """Digest-pinned, O_NOATIME-staged reads of RPD-RECO's 24 dumps, for RPD-RECO's own Inputs.samples."""

    def __init__(self, config: Json, staged: Path, roots: list[Path]):
        self.dump_root = Path(config["dump_root"])
        self.staged = staged
        self.roots = roots
        self.copies: dict[str, Path] = {}
        self.keys_read: list[dict[str, str]] = []
        pins_path = Path(config["pins"]["path"])
        with R.read_guards(self.roots):
            pins = R.stage_copy(pins_path, staged / "INPUTS.sha256", config["pins"]["sha256"])
        self.pins: dict[str, tuple[Path, str]] = {}
        for line in pins.read_text().splitlines():
            checksum, path = line.split("  ", 1)
            source = Path(path)
            require(source.parent.resolve() == self.dump_root.resolve(), "PIN_ROOT", "pin outside dump root")
            self.pins[source.name] = (source, checksum)
        expected = {f"lat_{p}{s}.npz" for p in R.PLAYLISTS for s in ("", "_bkg")}
        require(set(self.pins) == expected, "PIN_SET", "pin set differs from the 24 declared dumps")

    def key(self, name: str, key: str) -> NDArray[Any]:
        allowed = R.BKG_KEYS if name.endswith("_bkg.npz") else R.MC_KEYS | {"measured"}
        require(key in allowed, "KEY_ALLOWLIST", f"undeclared key {key}")
        if name not in self.copies:
            source, checksum = self.pins[name]
            with R.read_guards(self.roots):
                self.copies[name] = R.stage_copy(source, self.staged / name, checksum)
        with R.read_guards(self.roots), np.load(self.copies[name], allow_pickle=True) as archive:
            require(key in archive.files, "KEY_EXISTS", f"missing {key} in {name}")
            result = np.asarray(archive[key])
        self.keys_read.append({"file": name, "key": key})
        return result


def stream(
    reader: Reader, lattice: Lattice, plant_split: np.random.Generator, check: Callable[[], None]
) -> Json:
    """One pass over RPD-RECO's samples, with RPD-RECO's draws, filling every histogram the fit and its controls use.

    The draws follow R.aggregate exactly: per sample, per 65,536-row chunk, replica 0 is ones and replica r >= 1 is
    generator r - 1's Poisson(1) of the chunk's length. Only the bin assignment differs.
    """
    generators = [
        np.random.default_rng(np.random.SeedSequence([20261104, 11, replica + 1])) for replica in range(R.BOOTSTRAPS)
    ]
    replicas = R.BOOTSTRAPS + 1
    data_lattice = np.zeros((12, replicas, lattice.size))
    data_pz: dict[str, FloatArray] = {}
    pseudo_n_pa = np.zeros((replicas, NBINS))
    pseudo_p = {group: np.zeros((replicas, NBINS)) for group in ("PA", "PB")}
    plant_lattice = {alpha: np.zeros((replicas, lattice.size)) for alpha in PLANTS}
    plant_pz: list[FloatArray] = []  # PB's pseudo-data rows, unscaled, with their nominal weights (x 2): chi2 off the lattice
    plant_weights: list[FloatArray] = []
    rows: Json = {"signal": {}, "background": {}, "data": {}}
    for sample in R.Inputs.samples(reader, data=True):  # type: ignore[arg-type]
        check()
        count = len(sample.values)
        rows[sample.kind][sample.playlist] = count
        pz = sample.values[:, 1]
        index = R.PLAYLISTS.index(sample.playlist)
        group = next(g for g, members in R.GROUPS.items() if sample.playlist in members)
        if sample.kind == "data":
            data_pz[sample.playlist] = pz.copy()
            intervals = lattice.index(pz)
        elif group in ("PA", "PB"):
            pseudo = plant_split.random(count) < 0.5
            bins = R.bin_indices(pz, R.PZ_EDGES)
            planted = {alpha: lattice.index(pz * (1.0 + alpha)) for alpha in PLANTS} if group == "PB" else {}
            if group == "PB":
                plant_pz.append(pz[pseudo])
                plant_weights.append(2.0 * sample.weights[pseudo])
        for start in range(0, count, R.CHUNK_ROWS):
            stop = min(start + R.CHUNK_ROWS, count)
            for replica in range(replicas):
                draw = np.ones(stop - start) if replica == 0 else generators[replica - 1].poisson(1, stop - start)
                weights = sample.weights[start:stop] * draw
                if sample.kind == "data":
                    data_lattice[index, replica] += np.bincount(
                        intervals[start:stop], weights=weights, minlength=lattice.size
                    )
                elif group in ("PA", "PB"):
                    half = pseudo[start:stop]
                    doubled = 2.0 * weights
                    pseudo_p[group][replica] += np.bincount(
                        bins[start:stop][~half], weights=doubled[~half], minlength=NBINS
                    )
                    if group == "PA":
                        pseudo_n_pa[replica] += np.bincount(
                            bins[start:stop][half], weights=doubled[half], minlength=NBINS
                        )
                    else:
                        for alpha in PLANTS:
                            plant_lattice[alpha][replica] += np.bincount(
                                planted[alpha][start:stop][half], weights=doubled[half], minlength=lattice.size
                            )
    return {
        "data_lattice": data_lattice,
        "data_pz": data_pz,
        "pseudo_n_pa": pseudo_n_pa,
        "pseudo_p": pseudo_p,
        "plant_lattice": plant_lattice,
        "plant_rows": (np.concatenate(plant_pz), np.concatenate(plant_weights)),
        "rows": rows,
    }


# --------------------------------------------------------------------------------------------------- the controls


def members(group: str) -> list[int]:
    return [R.PLAYLISTS.index(p) for p in R.GROUPS[group]]


def step_histogram(pz_bins: FloatArray) -> FloatArray:
    """RPD-RECO's three step regions from its p_par bins: [1.5, 8), [8, 15) and the rest."""
    low = pz_bins[..., STEP_REGIONS[0][0] : STEP_REGIONS[0][1]].sum(axis=-1)
    high = pz_bins[..., STEP_REGIONS[1][0] : STEP_REGIONS[1][1]].sum(axis=-1)
    rest = pz_bins.sum(axis=-1) - low - high
    return np.stack([low, high, rest], axis=-1)


def reproduction_control(alpha0_n: FloatArray, product: Json, d1_record: Json) -> Json:
    """R0: the lattice histograms at alpha = 0 equal c0's p_par counts in every replica, and s_PB is reproduced."""
    c0_n = product["pz"]["N"]  # (replica, playlist, bin)
    require(
        alpha0_n.shape == c0_n.shape and bool(np.array_equal(alpha0_n, c0_n)),
        "REPRODUCTION_HISTOGRAMS",
        "the replayed draws do not reproduce c0's p_par counts",
    )
    step_n = np.stack([step_histogram(alpha0_n[:, x]) for x in range(12)], axis=1)
    s_pb = R.group_step(step_n, product["step"]["P"], "PB")
    recorded = d1_record["result"]["R-d1.0"]["PB"]
    relative = abs(float(s_pb[0]) - recorded["s"]) / abs(recorded["s"]) if recorded["s"] != 0 else abs(float(s_pb[0]))
    require(relative <= REPRODUCTION_RTOL, "REPRODUCTION_S_PB", f"s_PB differs by {relative:.3e} relative")
    sigma = float(np.std(s_pb[1:], ddof=1))
    return {
        "histograms_equal": True,
        "s_PB": float(s_pb[0]),
        "s_PB_recorded": recorded["s"],
        "s_PB_relative_difference": relative,
        "sigma_PB": sigma,
        "sigma_PB_recorded": recorded["sigma"],
        "sigma_PB_relative_difference": abs(sigma - recorded["sigma"]) / recorded["sigma"],
        "step_N_equal_c0": bool(np.array_equal(step_n, product["step"]["N"])),
    }


def plant_control(streamed: Json, lattice: Lattice, check: Callable[[], None] | None = None) -> Json:
    """M2: recover each planted scale within 3.5 sigma_alpha (the declared rule, nothing more) on RPL's own pseudo-data.

    chi2 at alpha-hat is evaluated off the lattice on PB's pseudo-data rows, as for the primary fit.
    """
    pz_rows, weight_rows = streamed["plant_rows"]
    p_pb, n_pa, p_pa = streamed["pseudo_p"]["PB"], streamed["pseudo_n_pa"], streamed["pseudo_p"]["PA"]
    results = {}
    for alpha in PLANTS:
        group = GroupFit(lattice, cumulative(streamed["plant_lattice"][alpha]), p_pb, n_pa, p_pa)

        def chi2_at(alpha_hat: float, alpha: float = alpha, group: GroupFit = group) -> float:
            n = direct_bins(pz_rows * (1.0 + alpha), weight_rows, alpha_hat)
            return profiled_chi2(ratio(n, p_pb[0], n_pa[0], p_pa[0]), group.sigma, group.used)[0]

        fit = group.fit(chi2_at, check)
        pull = abs(fit["alpha_hat"] - alpha) / fit["sigma_alpha"]
        results[f"{alpha:+.3f}"] = {
            "alpha_true": alpha,
            "alpha_hat": fit["alpha_hat"],
            "sigma_alpha": fit["sigma_alpha"],
            "pull": pull,
            "at_scan_edge": at_scan_edge(fit),
            "chi2_alpha_hat": fit["chi2_alpha_hat"],
            "fine_min_chi2": fit["fine_min_chi2"],
            "p_alpha_hat": fit["p_alpha_hat"],
            "pass": bool(pull <= PLANT_TOLERANCE),
        }
    require(all(r["pass"] for r in results.values()), "PLANT_RECOVERY", f"a planted scale was not recovered: {results}")
    return results


# ------------------------------------------------------------------------------------------------------- the run


def self_digest(path: Path) -> str:
    """The sha256 of a file read once under O_NOATIME; its identity is then checked through the record chain."""
    flag = R.noatime_flag()
    try:
        descriptor = os.open(path, os.O_RDONLY | flag)
    except OSError as error:
        raise Refused("NOATIME_OPEN", f"{path}: {error}") from error
    with os.fdopen(descriptor, "rb") as stream:
        return hashlib.sha256(stream.read()).hexdigest()


def load_chain(rpd_run: Path, d1_sha: str, d2_sha: str, roots: list[Path], staged: Path) -> tuple[Json, Json]:
    """P-RPD: RPD-RECO's passing d2 and d1 records by sha256, and every earlier record through the predecessor chain.

    Each record names its predecessor's sha256 (R.require_predecessors), so pinning d1 binds c0, step0, d2-predict, p0
    and pins. Every record must pass, share one code and configuration digest, and not be a dry run.
    """
    records: dict[str, Json] = {}
    digests: dict[str, str] = {"d1": d1_sha, "d2": d2_sha}
    for step in reversed(R.STEPS):
        if step not in digests:
            successor = R.STEPS[R.STEPS.index(step) + 1]
            digests[step] = records[successor]["predecessor_sha256"]
            require(isinstance(digests[step], str), "P_RPD", f"{successor} names no predecessor")
            require(self_digest(rpd_run / f"{step}.json") == digests[step], "P_RPD", f"{step} is not d1's chain")
        with R.read_guards(roots):
            copy = R.stage_copy(rpd_run / f"{step}.json", staged / f"rpd-{step}.json", digests[step])
        record = json.loads(copy.read_text())
        require(
            record.get("status") == "PASS" and record.get("step") == step and record.get("dry_run") is False,
            "P_RPD",
            f"RPD-RECO {step} is not a passing record",
        )
        records[step] = record
    require(records["d2"]["predecessor_sha256"] == d1_sha, "P_RPD", "d2 does not follow this d1")
    require(
        len({r["code_sha256"] for r in records.values()}) == 1
        and len({r["config_sha256"] for r in records.values()}) == 1,
        "P_RPD",
        "the chain mixes code or configuration digests",
    )
    require("unit_test_predecessor_only" not in records["c0"]["result"], "P_RPD", "c0 is a unit-test stand-in")
    product = records["c0"]["result"]["product"]
    with R.read_guards(roots):
        histogram_copy = R.stage_copy(rpd_run / product["path"], staged / "rpd-c0.npz", product["sha256"])
    histograms: Json = {}
    with np.load(histogram_copy, allow_pickle=False) as archive:
        for key in archive.files:
            axis, kind = key.split("__")
            if axis in ("pz", "step"):
                histograms.setdefault(axis, {})[kind] = np.asarray(archive[key], dtype=float)
    return records, histograms


def run(arguments: argparse.Namespace, argv: Sequence[str]) -> Json:
    started = time.monotonic()
    out: Path = arguments.out
    R.require_output_root(out)
    require(not out.exists() or not any(out.iterdir()), "OUTPUT_EXISTS", "output directory is not empty")
    out.mkdir(parents=True, exist_ok=True)
    staged = out / "staged"
    staged.mkdir()
    deadline = started + arguments.wall_seconds

    def check() -> None:
        require(time.monotonic() <= deadline, "WALL_CLOCK", "wall budget exhausted")

    roots = [arguments.config.resolve(), arguments.rpd_run.resolve(), arguments.band.resolve()]
    with R.read_guards(roots):
        config_copy = R.stage_copy(arguments.config, staged / "config.json", arguments.config_sha256)
        band_copy = R.stage_copy(arguments.band, staged / "band.json", arguments.band_sha256)
    config = json.loads(config_copy.read_text())
    roots += [Path(config["dump_root"]).resolve(), Path(config["pins"]["path"]).resolve()]
    chain, product = load_chain(arguments.rpd_run, arguments.d1_sha256, arguments.d2_sha256, roots, staged)
    d1, c0, p0 = chain["d1"], chain["c0"], chain["p0"]
    require(c0["config_sha256"] == arguments.config_sha256, "P_RPD", "RPD-RECO ran under a different configuration")
    require(c0["code_sha256"] == R.digest(Path(R.__file__)), "P_RPD", "RPD-RECO's code differs from this checkout's")
    environment = R.runtime_environment()
    require(p0["result"]["environment"] == environment, "ENVIRONMENT", "numerical environment differs from P0's record")
    band = json.loads(band_copy.read_text())
    sigma_band = deciding_band(band)

    lattice = Lattice()
    reader = Reader(config, staged, roots)
    streamed = stream(reader, lattice, np.random.default_rng(np.random.SeedSequence(list(PLANT_SPLIT_WORDS))), check)
    data_cumulative = cumulative(streamed["data_lattice"])  # (playlist, replica, interval + 1)
    alpha0 = np.stack([lattice.bins(data_cumulative[x], 0) for x in range(12)], axis=1)
    controls = {"reproduction": reproduction_control(alpha0, product, d1)}
    check()
    controls["planted_scale"] = plant_control(streamed, lattice, check)
    check()

    n_unscaled, p = alpha0, product["pz"]["P"][:, 0]  # (replica, playlist, bin)
    pa = members("PA")

    def fit_of(fitted: list[int], reference: list[int]) -> Json:
        def chi2_at(alpha: float) -> float:
            n = sum(direct_bins(streamed["data_pz"][R.PLAYLISTS[x]], np.ones(len(streamed["data_pz"][R.PLAYLISTS[x]])), alpha) for x in fitted)
            d = ratio(n, p[0, fitted].sum(axis=0), n_unscaled[0, reference].sum(axis=0), p[0, reference].sum(axis=0))
            return profiled_chi2(d, group.sigma, group.used)[0]

        group = GroupFit(
            lattice,
            data_cumulative[fitted].sum(axis=0),
            p[:, fitted].sum(axis=1),
            n_unscaled[:, reference].sum(axis=1),
            p[:, reference].sum(axis=1),
        )
        names = {"fitted": [R.PLAYLISTS[x] for x in fitted], "reference": [R.PLAYLISTS[x] for x in reference]}
        return {**group.fit(chi2_at, check), **names}

    reading_pb = d1["result"]["R-d1.0"]["PB"]["reading"]
    primary = fit_of(members("PB"), pa) if reading_pb == "SEEN" else None
    outcome = classify(reading_pb, primary, sigma_band)
    descriptive: Json | None = None
    if outcome != "NO-STEP":  # NO-STEP: no fit is read
        # The declaration fixes no reading for a descriptive fit that cannot be formed, so its refusal is a STOP.
        descriptive = {"PC": fit_of(members("PC"), pa)}
        for x, playlist in enumerate(R.PLAYLISTS):
            check()
            descriptive[playlist] = fit_of([x], [y for y in pa if y != x])
    record = {
        "schema": SCHEMA,
        "status": "PASS",
        "outcome": outcome,
        "primary_PB": primary,
        "sigma_band": {
            "Muon_Energy_MINOS_overall": sigma_band,
            "Muon_Energy_MINOS_strata": {
                key: band["sigma_band"]["Muon_Energy_MINOS"][key] for key in ("p_par_lt_8", "p_par_ge_8")
            },
            "Muon_Energy_MINERvA_descriptive": band["sigma_band"]["Muon_Energy_MINERvA"],
            "band_nature": "common to all playlists; a magnitude comparison only, not coverage",
        },
        "published_muon_energy_scale": PUBLISHED_SCALE,
        "descriptive_alpha_hat": descriptive,
        "controls": controls,
        "d1_PB": d1["result"]["R-d1.0"]["PB"],
        "rows": streamed["rows"],
        "input_sha256": {
            "config": arguments.config_sha256,
            "band": arguments.band_sha256,
            "rpd_d1": arguments.d1_sha256,
            "rpd_d2": arguments.d2_sha256,
            "rpd_c0_product": c0["result"]["product"]["sha256"],
            "rpd_chain": {step: R.digest(staged / f"rpd-{step}.json") for step in R.STEPS},
            "dumps": {name: checksum for name, (_path, checksum) in reader.pins.items()},
        },
        "keys_read": reader.keys_read,
        "environment": environment,
        "code_sha256": R.digest(Path(__file__)),
        "rpd_reco_code_sha256": R.digest(Path(R.__file__)),
        "argv": list(argv),
        "seconds": time.monotonic() - started,
        "does_not_license": DOES_NOT_LICENSE,
    }
    R.write_json(out / "rpl-scale-fit.json", record)
    return record


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True, help="RPD-RECO's bound READY configuration")
    parser.add_argument("--config-sha256", required=True)
    parser.add_argument("--rpd-run", type=Path, required=True, help="RPD-RECO's run directory")
    parser.add_argument("--d1-sha256", required=True)
    parser.add_argument("--d2-sha256", required=True)
    parser.add_argument("--band", type=Path, required=True, help="i-bandsize/cluster/band.json")
    parser.add_argument("--band-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--wall-seconds", type=int, required=True)
    arguments = parser.parse_args(argv)
    command = list(argv) if argv is not None else sys.argv[1:]
    out: Path = arguments.out
    try:  # a STOP record goes only into an output directory that is off CFS and new or empty at the start
        R.require_output_root(out)
        stop_writable = not out.exists() or (out.is_dir() and not any(out.iterdir()))
    except (Refused, OSError):  # CFS, or a directory that cannot be inspected: the STOP is printed only
        stop_writable = False
    try:
        for key in R.THREAD_KEYS:
            require(os.environ.get(key) == "1", "THREADS", f"{key} must be 1")
        require(os.getpriority(os.PRIO_PROCESS, 0) == 19, "NICE", "nice level must be 19")
        record = run(arguments, command)
    except (Refused, OSError) as error:
        guard = error.guard if isinstance(error, Refused) else "OS_ERROR"
        if stop_writable:
            try:
                out.mkdir(parents=True, exist_ok=True)
                R.write_json(
                    out / "rpl-scale-fit.STOP.json",
                    {"schema": SCHEMA, "status": "STOP", "guard": guard, "message": str(error), "readings": None},
                )
            except OSError as write_error:  # a read-only or full filesystem: the STOP still exits 4, printed
                print(f"RPL-SCALE-FIT :: STOP record not written: {write_error}")
        print(f"RPL-SCALE-FIT :: STOP {guard}: {error}")
        return 4
    print(f"RPL-SCALE-FIT :: DONE (outcome {record['outcome']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
