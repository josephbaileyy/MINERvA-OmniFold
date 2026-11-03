"""COV2D, the 2D held-out-tune method-coverage campaign (campaign (c)): its bank, its declared draws, the first-order
composition of a drawn nature, N1's composite, and the clipped Poisson mean
(docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-DECLARATION.md, sections 4 and 9).

* The bank is RE-2 part B's universe block: 38 bands, 175 universes on the universe omnifile $UNI. Flux has 100
  universes, 2p2h 3, every other band 2 (``BANDS``; the tests check it against part B's J2 run list).
* A draw holds one universe of every band, in draw order: the Flux universe first, with probability w_u / sum w (the
  constraint weights the rollup's Flux block uses), then the other bands in sorted order, each universe uniformly. It
  then draws one sign per lateral band and one standard normal for the normalization.
* A nature's per-row array composes to first order in draw order (DECISION-20261102-joseph-1b-redesign.md item 1):
  a_D = a_u1 + sum_{j>=2} (a_uj - a_CV). For one universe it is a_u1 bitwise.
* N1's composite on a row is |a_D| / max_j |a_uj|: 1 where both are 0, +inf where only the peak is 0.
* Negative composites are clipped consistently (DECISION-20261103-joseph-coverage-clip-rule.md item 1, which
  supersedes option (a) of the redesign decision's item 3 for cov2d): a toy's Poisson mean is lambda+ = max(lambda, 0)
  on the full product, row by row on the signal and background trees, and the graded truth's composite weight is
  clipped the same way, row by row on the truth tree (``lam_plus`` for each). The clipped mass is recorded.
* A pass in a cell whose clipped-composition variance ratio, from the clipping probe C2, is below ``WEAKENED_BELOW``
  reads as weakened (the director's ruling on that decision; ``weakened_cells``). ``OUTLIER_CELL`` is the cell C2
  named, where the residual reaches 4.27 sigma_Q in a few draws.

MEASURES: arithmetic on supplied arrays. CANNOT AUTHORIZE: a run, or a verdict.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

FLUX = "Flux"
PAIR_BANDS = (
    "AGKYxF1pi", "AhtBY", "BhtBY", "CCQEPauliSupViaKF", "CV1uBY", "CV2uBY", "EtaNCEL", "FrAbs_N", "FrAbs_pi",
    "FrCEx_N", "FrCEx_pi", "FrElas_N", "FrElas_pi", "FrInel_N", "FrPiProd_N", "FrPiProd_pi", "GEANT_Neutron",
    "GEANT_Pion", "GEANT_Proton", "HighQ2", "LowQ2", "MFP_N", "MFP_pi", "MaCCQE", "MaNCEL", "MaRES",
    "MinosEfficiency", "MvRES", "NormDISCC", "NormNCRES", "RDecBR1gamma", "Rvn1pi", "Rvn2pi", "Rvp2pi",
    "Theta_Delta2Npi", "VecFFCCQEshape",
)
BANDS = {FLUX: 100, "2p2h": 3, **{b: 2 for b in PAIR_BANDS}}
ORDER = (FLUX,) + tuple(sorted(b for b in BANDS if b != FLUX))
N_UNIVERSES = sum(BANDS.values())
LATERAL_BANDS = ("BeamAngleX", "BeamAngleY", "MuonResolution", "Muon_Energy_MINERvA", "Muon_Energy_MINOS")
NORM = 0.014

DRAW_SALT = 20_261_102_3
TOY_SEEDS = {"G18": range(5_720_000, 5_720_300), "AR23": range(5_730_000, 5_730_300)}
REALIZATION_SEED = {"G18": 5_721_000, "AR23": 5_731_000}
NULL_SEED = 5_742_000
N1_BOUND = 10.0
WEAKENED_BELOW = 0.9
OUTLIER_CELL = 216      # flat (p_T, p_par) cell (13, 8): p_T 2.5-4.5, p_par 6-7 GeV/c

CONSTRAINT = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/"
              "sorted_NuEConstraint_FHC_RHC_IMD.txt")
CONSTRAINT_SHA256 = "e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2"


class Refusal(RuntimeError):
    pass


def column(prefix: str, band: str, idx: int) -> str:
    """The universe column on $UNI: w_truth_ / w_reco_ / w_bkg_ <band>_<idx> (no band name needs sanitizing)."""
    return f"{prefix}_{band}_{int(idx)}"


def flux_weights(text: str) -> np.ndarray:
    """The 100 Flux constraint weights from the constraint file's 'Flux <idx> <w>' lines, as the rollup reads them."""
    cons = {}
    for line in text.splitlines():
        t = line.split()
        if len(t) == 3 and t[0] == FLUX:
            cons[int(t[1])] = float(t[2])
    if sorted(cons)[:BANDS[FLUX]] != list(range(BANDS[FLUX])):
        raise Refusal("the constraint file lacks one of Flux 0-99")
    w = np.array([cons[i] for i in range(BANDS[FLUX])])
    if not np.all(np.isfinite(w)) or np.any(w < 0) or w.sum() <= 0:
        raise Refusal("the Flux constraint weights must be finite, non-negative and not all zero")
    return w


@dataclass(frozen=True)
class Draw:
    seed: int
    universes: tuple          # ((band, idx), ...) in draw order
    lateral_signs: tuple      # +-1 per LATERAL_BANDS entry
    norm_z: float


def draw(seed: int, w_flux: np.ndarray) -> Draw:
    rng = np.random.default_rng([int(seed), DRAW_SALT])
    p = np.asarray(w_flux, float) / np.sum(w_flux)
    univ = [(FLUX, int(rng.choice(BANDS[FLUX], p=p)))]
    for band in ORDER[1:]:
        univ.append((band, int(rng.integers(BANDS[band]))))
    signs = tuple(int(s) for s in rng.choice((-1, 1), size=len(LATERAL_BANDS)))
    return Draw(int(seed), tuple(univ), signs, float(rng.standard_normal()))


def declared_draws(truth: str, w_flux: np.ndarray) -> list[Draw]:
    return [draw(s, w_flux) for s in TOY_SEEDS[truth]]


def compose(cv: np.ndarray, univ: list[np.ndarray]) -> np.ndarray:
    """First order in draw order: univ[0] + sum_{j>=1} (univ[j] - cv), accumulated left to right."""
    if not univ:
        raise Refusal("a draw holds at least one universe")
    out = np.array(univ[0], dtype=np.float64, copy=True)
    for a in univ[1:]:
        out += np.asarray(a, np.float64) - cv
    return out


def peak(univ: list[np.ndarray]) -> np.ndarray:
    return np.max(np.abs(np.stack(univ)), axis=0)


def n1_composite(a_d: np.ndarray, pk: np.ndarray) -> np.ndarray:
    """|a_D| / peak: 1 where both are 0, +inf where only the peak is 0; never NaN."""
    num, den = np.abs(a_d), np.asarray(pk, np.float64)
    out = np.ones_like(num)
    pos = den > 0
    out[pos] = num[pos] / den[pos]
    out[(den == 0) & (num > 0)] = math.inf
    return out


def all_draws_bound(cv: np.ndarray, bands: list[np.ndarray]) -> np.ndarray:
    """An upper bound on N1's composite over every draw: (|a_CV| + sum_b D_b) / max_b m_b, with D_b the band's
    largest |a_u - a_CV| and m_b its smallest |a_u|; each element of ``bands`` is (n_universes, rows). The same
    conventions as n1_composite."""
    num = np.abs(cv).astype(np.float64)
    den = np.zeros_like(num)
    for b in bands:
        num += np.max(np.abs(b - cv), axis=0)
        den = np.maximum(den, np.min(np.abs(b), axis=0))
    return n1_composite(num, den)


def lam_plus(lam: np.ndarray) -> tuple[np.ndarray, dict]:
    """lambda+ = max(lambda, 0), and the record: sum lambda, sum of the negative part, rows below 0."""
    lam = np.asarray(lam, np.float64)
    neg = lam < 0
    rec = {"sum_lambda": float(lam.sum()), "sum_lambda_neg": float(lam[neg].sum()), "rows_neg": int(neg.sum())}
    return np.where(neg, 0.0, lam), rec


def weakened_cells(ratio, cells) -> list[int]:
    """The flat cells, of ``cells``, whose clipped-composition variance ratio ``ratio`` (C2's
    ``variance_ratio.option_1_clipped``, one per cell in the same order) is below WEAKENED_BELOW."""
    ratio, cells = np.asarray(ratio, np.float64), np.asarray(cells)
    if ratio.shape != cells.shape or not np.all(np.isfinite(ratio)):
        raise Refusal("one finite variance ratio per cell is required")
    return [int(x) for x in cells[ratio < WEAKENED_BELOW]]


def sha256_file(path: str | Path) -> str:
    """sha256 through an O_NOATIME descriptor, so the read moves no purge clock."""
    import hashlib
    import os
    h = hashlib.sha256()
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOATIME), "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
