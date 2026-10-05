"""The predeclared Phase-E distortions of PROTOCOL-20260922 Amendment 1, as named functions.

Two kinds, never mixed inside one function:

* **truth-model distortions D1-D5** -- a per-event WEIGHT that is a function of simulation truth
  only. It is applied to the pseudodata (never the prior) and normalized to unit mean over the
  pseudodata sample (`normalize_unit_mean`); the scored target is the same function applied to all
  of pool T. Each is a fixed function: every constant it needs is in its spec, so the weight of an
  event does not depend on which sample it is in.
* **detector-response distortions R1-R3** -- a TRANSFORM of the pseudodata's reconstructed
  quantities. Truth, weights and the prior are unchanged; the correct unfolded answer is the
  undistorted-response target.

WHAT R1-R3 SCALE, EXACTLY. Reco `E_avail` is `NewEavail()` = 1.17 x (blob_recoil_E_tracker +
blob_recoil_E_ecal - muon fuzz in those planes) (`CVUniverse.h:185-193`); reco `q3` is `RecoQ3()`
= sqrt(Q^2 + q0^2) with q0 = the calorimetric `<tree>_recoil_E`, Q^2 = 2(E_mu + q0)(E_mu -
p_mu cos theta) - m_mu^2 (`CVUniverse.h:208-219`); the stored tokens are the <= 12 highest-energy
reco recoil clusters (`part_reco[..., 0]`, MeV -> GeV).

* R1 (hadronic scale s): every calorimetric energy is multiplied by s -- the blob sums, the fuzz
  subtracted from them and every cluster -- so reco E_avail -> s E_avail EXACTLY, each stored token
  energy -> s E_i, and q0 -> s q0; reco q3 is recomputed from the unchanged muon and the new q0.
* R2 (muon momentum scale s): reco p_T -> s p_T and p_par -> s p_par (p -> s p at fixed angle,
  E_mu = sqrt(p^2 + m_mu^2)); q0 unchanged; reco q3 recomputed. E_avail and tokens unchanged.
* R3 (cluster resolution sigma): each stored token energy E_i -> E_i max(1 + sigma g_i, 0) with
  g_i ~ N(0, 1) independent per (event, token slot), drawn from the event identity (deterministic);
  reco E_avail and q0 are multiplied by rho = sum E_i' / sum E_i over the stored tokens (rho = 1 for
  an event with no stored energy). The <= 12 stored tokens are not all of the energy E_avail sums
  (and are not split by sub-detector), so R3 moves E_avail by the energy-weighted smearing of the
  stored clusters -- an approximation stated wherever R3 is reported.

`q0` is not stored; `recoil_q0` recovers it by inverting RecoQ3 on the stored (p_T, p_par, q3).
Where the inversion has no non-negative root (RecoQ3's Q^2 < 0 clip, so q3 = q0) q0 = q3.

Every distortion is a `Distortion` in `registry()`, with a `content_hash` over its full spec
(family, kind, parameters, and for D5 the digest of the weight table and of its source files).
PET is diagnostic method development; nothing here reads real data.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
CALIBRATION_DIR = HERE / "calibration"
D3_CALIBRATION = CALIBRATION_DIR / "d3_standardization.json"
D5_CALIBRATION = CALIBRATION_DIR / "d5_tables.json"
SPEC_VERSION = "phase-e-distortion/1"

MUON_MASS_GEV = 0.1056583755
N_TOKENS = 12
ENDPOINT_EDGES = (0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0)

# D1: the development injection's own standardization. `clipped_exponential_tilt` standardizes
# with the quantiles of the rows it is given; for the historical development point those were the
# 600,130 truth-passing rows of half A (replayed by B1: phase_b/scalar/results/populations.json,
# `tilt_spec_half_A`, bit-identical to the recorded tilt). D1 freezes them so the tilt is one fixed
# function of true E_avail -- the same on every replicate and on the pool-T target.
D1_P50_GEV = 1.4653696417808533
D1_IQR_GEV = 2.6336711198091507
TILT_CLIP_Z = 3.0

PDG = {"pipm": 211, "pi0": 111, "p": 2212, "n": 2112}


# ------------------------------------------------------------------------------------------- #
# Truth-weight kernels
# ------------------------------------------------------------------------------------------- #
def clipped_exp_tilt(x: np.ndarray, amplitude: float, p50: float, iqr: float,
                     clip_z: float = TILT_CLIP_Z) -> np.ndarray:
    """exp(A * clip((x - p50)/iqr, -clip_z, clip_z)): the historical tilt's form, un-normalized.
    Non-finite x gets z = 0 (weight 1); callers count such rows."""
    x = np.asarray(x, dtype=np.float64)
    z = np.where(np.isfinite(x), (x - float(p50)) / float(iqr), 0.0)
    return np.exp(float(amplitude) * np.clip(z, -float(clip_z), float(clip_z)))


def gaussian_bump(x: np.ndarray, amplitude: float, centre: float, width: float) -> np.ndarray:
    """1 + A exp(-((x - c)/s)^2) (the 3D pipeline's injected-shape form)."""
    x = np.asarray(x, dtype=np.float64)
    return 1.0 + float(amplitude) * np.exp(-(((x - float(centre)) / float(width)) ** 2))


def eavail_over_q3(eavail: np.ndarray, q3: np.ndarray) -> np.ndarray:
    """E_avail / q3, NaN where q3 is non-finite or <= 0 (such rows get weight 1 under D3)."""
    e = np.asarray(eavail, dtype=np.float64)
    q = np.asarray(q3, dtype=np.float64)
    ok = np.isfinite(e) & np.isfinite(q) & (q > 0)
    return np.where(ok, e / np.where(ok, q, 1.0), np.nan)


def multiplicity_weight(n: np.ndarray, factor: float) -> np.ndarray:
    """f^N."""
    return np.power(float(factor), np.asarray(n, dtype=np.float64))


def count_species(pdg: np.ndarray) -> dict[str, np.ndarray]:
    """Per event, the number of stored truth hadrons of each D4 species. ``pdg`` is
    `part_gen[..., 4]` (n, 12), float32 as stored; |pdg| is rounded before comparison."""
    code = np.rint(np.abs(np.asarray(pdg, dtype=np.float64))).astype(np.int64)
    return {name: (code == c).sum(axis=1).astype(np.int16) for name, c in PDG.items()}


def normalize_unit_mean(w: np.ndarray) -> np.ndarray:
    """Weights divided by their mean over the sample they are applied to (fail closed)."""
    w = np.asarray(w, dtype=np.float64)
    m = float(w.mean()) if w.size else float("nan")
    if not (np.isfinite(m) and m > 0) or not np.isfinite(w).all() or (w < 0).any():
        raise ValueError("distortion weights must be finite, non-negative, with positive mean")
    return w / m


# ------------------------------------------------------------------------------------------- #
# D5: generator-ratio tables
# ------------------------------------------------------------------------------------------- #
D5_DIR_DEFAULT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie"
D5_REFERENCE = {"file": "model_tunev1_xsec3d.root", "hist": "hXSec3D", "errors": "histogram"}
D5_GENERATORS = {
    # id: file, histogram, how its relative statistical error is known
    "nuwro": {"file": "nuwro_cv_xsec3d.root", "hist": "hXSec3D", "errors": "histogram",
              "label": "NuWro 21.09 CV"},
    "gibuu": {"file": "gibuu_cv_xsec3d.root", "hist": "hXSec3D", "errors": "histogram",
              "label": "GiBUU CV"},
    "genie_mec": {"file": "genie_mec_cv_xsec3d.root", "hist": "hXSec3D", "errors": "counts",
                  "label": "GENIE 2.12 + Valencia MEC CV"},
    # The FSI files hold the SAME GENIE-CV events reweighted to dial values [-1, 0, +1] sigma
    # (`twkdials`); `_d2` is +1 sigma. Their relative error is that of the CV event counts
    # (`genie_cv_xsec3d.root`, whose histogram equals `_d1` exactly).
    "fsi_frabs": {"file": "genie_fsi_FrAbs_pi_xsec3d.root", "hist": "hXSec3D_d2",
                  "errors": "counts_of:genie_cv_xsec3d.root:hXSec3D",
                  "label": "GENIE FSI FrAbs_pi +1 sigma"},
    "fsi_frinel": {"file": "genie_fsi_FrInel_pi_xsec3d.root", "hist": "hXSec3D_d2",
                   "errors": "counts_of:genie_cv_xsec3d.root:hXSec3D",
                   "label": "GENIE FSI FrInel_pi +1 sigma"},
}
D5_MAX_REL_ERR = 0.30
D5_CLIP = (0.2, 5.0)


def read_th3(path: Path | str, name: str) -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
    """(values, errors, [x, y, z edges]) of a TH3, with uproot if installed, else PyROOT."""
    try:
        import uproot  # type: ignore
        h = uproot.open(str(path))[name]
        return (np.asarray(h.values(), float), np.asarray(h.errors(), float),
                [np.asarray(a.edges(), float) for a in h.axes])
    except ImportError:
        import ROOT  # type: ignore
        f = ROOT.TFile.Open(str(path))
        h = f.Get(name)
        axes = [h.GetXaxis(), h.GetYaxis(), h.GetZaxis()]
        edges = [np.array([ax.GetBinLowEdge(i + 1) for i in range(ax.GetNbins())]
                          + [ax.GetBinUpEdge(ax.GetNbins())]) for ax in axes]
        shape = tuple(ax.GetNbins() for ax in axes)
        v = np.zeros(shape)
        e = np.zeros(shape)
        for i in range(shape[0]):
            for j in range(shape[1]):
                for k in range(shape[2]):
                    v[i, j, k] = h.GetBinContent(i + 1, j + 1, k + 1)
                    e[i, j, k] = h.GetBinError(i + 1, j + 1, k + 1)
        f.Close()
        return v, e, edges


def _widths(edges: list[np.ndarray]) -> np.ndarray:
    return (np.diff(edges[0])[:, None, None] * np.diff(edges[1])[None, :, None]
            * np.diff(edges[2])[None, None, :])


def integer_counts(integrated: np.ndarray, tol: float = 1e-6, max_k: int = 16) -> np.ndarray:
    """Recover the unweighted event counts behind a histogram filled with ONE constant per event
    (GENIE unweighted events x a global normalization).

    The smallest positive bin holds ``k`` events for some small integer k (k = 1 in the files this
    is used on, where hundreds of bins hold a handful of events); the constant is that bin divided
    by the smallest k that makes EVERY bin an integer to ``tol``. Refused if no k <= ``max_k``
    does, because then the histogram is not unweighted counts and 1/sqrt(n) is not its error."""
    x = np.asarray(integrated, dtype=np.float64)
    positive = x[x > 0]
    if positive.size == 0:
        raise ValueError("empty histogram")
    for k in range(1, int(max_k) + 1):
        n = x * k / positive.min()
        if np.abs(n - np.rint(n)).max() <= tol:
            return np.rint(n)
    raise ValueError("histogram is not a constant times integer counts")


def _integrated_with_rel_err(directory: Path, spec: Mapping[str, str]
                             ) -> tuple[np.ndarray, np.ndarray, list[np.ndarray], dict]:
    v, e, edges = read_th3(directory / spec["file"], spec["hist"])
    w = _widths(edges)
    integ = v * w
    info = {"file": spec["file"], "hist": spec["hist"], "errors": spec["errors"],
            "sha256": _sha256(directory / spec["file"])}
    if spec["errors"] == "histogram":
        err = e * w
        if not (err[integ > 0] > 0).all():
            raise ValueError(f"{spec['file']}: histogram errors missing on filled bins")
    elif spec["errors"] == "counts":
        n = integer_counts(integ)
        err = np.where(n > 0, integ / np.sqrt(np.where(n > 0, n, 1.0)), 0.0)
        info["recovered_event_count"] = int(n.sum())
    elif spec["errors"].startswith("counts_of:"):
        _tag, fname, hname = spec["errors"].split(":")
        vc, _ec, edges_c = read_th3(directory / fname, hname)
        if any(not np.array_equal(a, b) for a, b in zip(edges, edges_c)):
            raise ValueError(f"{fname} binning differs from {spec['file']}")
        n = integer_counts(vc * _widths(edges_c))
        err = np.where(n > 0, integ / np.sqrt(np.where(n > 0, n, 1.0)), 0.0)
        info["counts_source_sha256"] = _sha256(directory / fname)
        info["recovered_event_count"] = int(n.sum())
    else:
        raise ValueError(f"unknown error source {spec['errors']!r}")
    return integ, err, edges, info


def _rel(content: float, err2: float) -> float:
    return math.sqrt(err2) / content if content > 0 else math.inf


def merge_column(x: np.ndarray, ex: np.ndarray, t: np.ndarray, et: np.ndarray,
                 max_rel: float = D5_MAX_REL_ERR) -> tuple[list[list[int]], bool]:
    """Merge E_avail bins of ONE (p_T, p_par) column until neither histogram has a relative stat
    error above ``max_rel`` in any group. Rule (deterministic): scan groups from the highest
    E_avail down; the first failing group is merged into its LOWER neighbour (group 0 into group
    1); repeat until nothing fails or one group is left. Returns (groups, resolved)."""
    groups = [[k] for k in range(len(x))]

    def fails(g: list[int]) -> bool:
        return (_rel(float(x[g].sum()), float((ex[g] ** 2).sum())) > max_rel
                or _rel(float(t[g].sum()), float((et[g] ** 2).sum())) > max_rel)

    while len(groups) > 1:
        bad = [i for i in range(len(groups) - 1, -1, -1) if fails(groups[i])]
        if not bad:
            return groups, True
        i = bad[0]
        if i > 0:
            groups[i - 1] = groups[i - 1] + groups[i]
            del groups[i]
        else:
            groups[0] = groups[0] + groups[1]
            del groups[1]
    return groups, not fails(groups[0])


D5_NORMALIZATIONS = ("phase_space", "per_pparallel_slice")


def build_d5_table(generator: str, directory: Path | str = D5_DIR_DEFAULT,
                   normalization: str = "phase_space") -> dict[str, Any]:
    """The D5 weight table for one generator: w = sigma_X / sigma_TuneV1 per 3D bin, as a SHAPE
    ratio (each prediction divided by its own total over the 3D phase space, so the in-PS weights
    average ~1 and events outside the 3D phase space, which keep w = 1, are not shifted by the
    generators' different normalizations), after the stat-error merge along E_avail, clipped to
    [0.2, 5]. A column that cannot be resolved even fully merged gets w = 1.

    ``normalization="per_pparallel_slice"`` is NOT the predeclared D5: each prediction is divided
    by its own total within each p_par slice, which removes the p_par marginal (where the standalone
    predictions fall far below Tune v1 above p_par ~ 8 GeV) and keeps the (p_T, E_avail | p_par)
    shape. It exists as a post-hoc diagnostic of what the predeclared D5 is dominated by."""
    if normalization not in D5_NORMALIZATIONS:
        raise ValueError(f"unknown normalization {normalization!r}")
    directory = Path(directory)
    xs, exs, edges, info_x = _integrated_with_rel_err(directory, D5_GENERATORS[generator])
    ts, ets, edges_t, info_t = _integrated_with_rel_err(directory, D5_REFERENCE)
    if any(not np.array_equal(a, b) for a, b in zip(edges, edges_t)):
        raise ValueError(f"{generator}: binning differs from the Tune v1 reference")
    if normalization == "phase_space":
        tot_x = np.full(xs.shape[1], float(xs.sum()))
        tot_t = np.full(xs.shape[1], float(ts.sum()))
    else:
        tot_x, tot_t = xs.sum(axis=(0, 2)), ts.sum(axis=(0, 2))
    weight = np.ones(xs.shape)
    group_id = np.full(xs.shape, -1, dtype=np.int64)
    unresolved, merged_bins, next_id = [], 0, 0
    for i in range(xs.shape[0]):
        for j in range(xs.shape[1]):
            groups, resolved = merge_column(xs[i, j], exs[i, j], ts[i, j], ets[i, j])
            resolved = resolved and tot_x[j] > 0 and tot_t[j] > 0
            for g in groups:
                group_id[i, j, g] = next_id
                next_id += 1
                if len(g) > 1:
                    merged_bins += len(g)
                if resolved:
                    weight[i, j, g] = ((xs[i, j, g].sum() / tot_x[j])
                                       / (ts[i, j, g].sum() / tot_t[j]))
            if not resolved:
                unresolved.append([i, j])
    raw = weight.copy()
    lo, hi = D5_CLIP
    weight = np.clip(weight, lo, hi)
    table = {
        "generator": generator, "label": D5_GENERATORS[generator]["label"],
        "reference": "MINERvA Tune v1 (model_tunev1_xsec3d.root:hXSec3D)",
        "edges": {"pt": edges[0].tolist(), "pparallel": edges[1].tolist(),
                  "eavail": edges[2].tolist()},
        "weight": weight.tolist(), "group_id": group_id.tolist(),
        "normalization": normalization, "predeclared": normalization == "phase_space",
        "rule": {"ratio": ("shape: (sigma_X/sum sigma_X)/(sigma_T/sum sigma_T), bin-width "
                           "integrated, sums over " + ("the 3D phase space"
                                                       if normalization == "phase_space"
                                                       else "each p_par slice")),
                 "merge": f"along E_avail, top-down into the lower neighbour, until both "
                          f"relative stat errors <= {D5_MAX_REL_ERR}",
                 "clip": list(D5_CLIP), "unresolved_column_weight": 1.0,
                 "outside_3d_phase_space_weight": 1.0},
        "stats": {"bins": int(xs.size), "bins_in_merged_groups": int(merged_bins),
                  "groups": int(next_id), "unresolved_columns": unresolved,
                  "clipped_low": int((raw < lo).sum()), "clipped_high": int((raw > hi).sum()),
                  "weight_min": float(weight.min()), "weight_max": float(weight.max()),
                  "total_x_over_total_tunev1": float(xs.sum() / ts.sum()),
                  "tunev1_mass_fraction_clipped_low": float(ts[raw < lo].sum() / ts.sum()),
                  "pparallel_marginal_shape_ratio": ((xs.sum(axis=(0, 2)) / xs.sum())
                                                     / (ts.sum(axis=(0, 2)) / ts.sum())).tolist()},
        "sources": {"generator": info_x, "reference": info_t, "directory": str(directory)},
    }
    table["table_sha256"] = _canonical_sha(table["weight"])
    return table


def generator_weight(pt: np.ndarray, pz: np.ndarray, eavail: np.ndarray,
                     table: Mapping[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Per-event D5 weight by 3D-bin lookup; (weights, inside_mask). Bins follow
    `np.histogramdd` (lower edge inclusive, the last bin also includes its upper edge). Events
    outside the 3D phase space (or with a non-finite coordinate) get weight 1."""
    w3 = np.asarray(table["weight"], dtype=np.float64)
    idx, inside = [], np.ones(np.asarray(pt).shape, dtype=bool)
    for x, key in ((pt, "pt"), (pz, "pparallel"), (eavail, "eavail")):
        e = np.asarray(table["edges"][key], dtype=np.float64)
        x = np.asarray(x, dtype=np.float64)
        ok = np.isfinite(x) & (x >= e[0]) & (x <= e[-1])
        k = np.clip(np.searchsorted(e, np.where(ok, x, e[0]), side="right") - 1, 0, e.size - 2)
        idx.append(k)
        inside &= ok
    w = np.where(inside, w3[idx[0], idx[1], idx[2]], 1.0)
    return w, inside


# ------------------------------------------------------------------------------------------- #
# Reco kernels
# ------------------------------------------------------------------------------------------- #
def _muon(pt: np.ndarray, ppar: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pt = np.asarray(pt, dtype=np.float64)
    ppar = np.asarray(ppar, dtype=np.float64)
    p = np.hypot(pt, ppar)
    return p, np.sqrt(p * p + MUON_MASS_GEV ** 2), ppar


def reco_q3(pt: np.ndarray, ppar: np.ndarray, q0: np.ndarray) -> np.ndarray:
    """RecoQ3 (CVUniverse.h:208-219) in GeV: Q^2 = 2(E+q0)(E - p cos theta) - m^2 clipped at 0;
    q3 = sqrt(Q^2 + q0^2). p cos theta = p_par (theta is the muon angle to the beam)."""
    _p, e, pl = _muon(pt, ppar)
    q0 = np.asarray(q0, dtype=np.float64)
    q2 = np.maximum(2.0 * (e + q0) * (e - pl) - MUON_MASS_GEV ** 2, 0.0)
    return np.sqrt(q2 + q0 * q0)


def recoil_q0(pt: np.ndarray, ppar: np.ndarray, q3: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Invert RecoQ3 for q0 >= 0: q0^2 + 2 b q0 + (2 E b - m^2 - q3^2) = 0, b = E - p_par.
    Returns (q0, fallback) where fallback marks rows with no non-negative root, set to q0 = q3
    (the Q^2 < 0 clip branch)."""
    _p, e, pl = _muon(pt, ppar)
    q3 = np.asarray(q3, dtype=np.float64)
    b = e - pl
    c = 2.0 * e * b - MUON_MASS_GEV ** 2 - q3 * q3
    disc = b * b - c
    root = -b + np.sqrt(np.maximum(disc, 0.0))
    bad = ~(np.isfinite(root) & (disc >= 0) & (root >= 0))
    return np.where(bad, q3, root), bad


def token_noise(identity: np.ndarray, salt: str = "pet-improvement-20260922-R3") -> np.ndarray:
    """(n, 12) standard normals per event, a pure function of the event identity: 48 bytes of
    blake2b(salt || identity) -> 12 uint32 -> 6 Box-Muller pairs."""
    rows = np.ascontiguousarray(np.asarray(identity, dtype=np.int64))
    prefix = hashlib.sha256(salt.encode()).digest()[:16]
    width = rows.shape[1] * 8
    raw = rows.tobytes()
    blob = b"".join(hashlib.blake2b(prefix + raw[i:i + width], digest_size=48).digest()
                    for i in range(0, len(raw), width))
    u = (np.frombuffer(blob, dtype="<u4").astype(np.float64).reshape(-1, N_TOKENS) + 0.5) / 2.0**32
    u1, u2 = u[:, 0::2], u[:, 1::2]
    r = np.sqrt(-2.0 * np.log(u1))
    out = np.empty_like(u)
    out[:, 0::2] = r * np.cos(2.0 * np.pi * u2)
    out[:, 1::2] = r * np.sin(2.0 * np.pi * u2)
    return out


RECO_KEYS = ("pt", "ppar", "eavail", "q3", "tok_E")


def reco_features(reco: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
    """The identifiability feature set (and more) from a reco mapping."""
    tok = np.asarray(reco["tok_E"], dtype=np.float64)
    return {"pt": np.asarray(reco["pt"], float), "ppar": np.asarray(reco["ppar"], float),
            "eavail": np.asarray(reco["eavail"], float), "q3": np.asarray(reco["q3"], float),
            "tok_sumE": tok.sum(axis=1), "tok_n": (tok != 0).sum(axis=1).astype(np.float64)}


def hadronic_scale(reco: Mapping[str, np.ndarray], scale: float) -> dict[str, np.ndarray]:
    """R1. Operates on pass_reco rows only (the caller selects them)."""
    q0, _bad = recoil_q0(reco["pt"], reco["ppar"], reco["q3"])
    s = float(scale)
    return {"pt": np.asarray(reco["pt"], float).copy(), "ppar": np.asarray(reco["ppar"], float).copy(),
            "eavail": s * np.asarray(reco["eavail"], float),
            "q3": reco_q3(reco["pt"], reco["ppar"], s * q0),
            "tok_E": s * np.asarray(reco["tok_E"], float)}


def muon_scale(reco: Mapping[str, np.ndarray], scale: float) -> dict[str, np.ndarray]:
    """R2. Operates on pass_reco rows only."""
    q0, _bad = recoil_q0(reco["pt"], reco["ppar"], reco["q3"])
    s = float(scale)
    pt, ppar = s * np.asarray(reco["pt"], float), s * np.asarray(reco["ppar"], float)
    return {"pt": pt, "ppar": ppar, "eavail": np.asarray(reco["eavail"], float).copy(),
            "q3": reco_q3(pt, ppar, q0), "tok_E": np.asarray(reco["tok_E"], float).copy()}


def cluster_smear(reco: Mapping[str, np.ndarray], sigma: float, noise: np.ndarray
                  ) -> dict[str, np.ndarray]:
    """R3. ``noise`` is `token_noise(identity)` for the same rows. Operates on pass_reco rows."""
    tok = np.asarray(reco["tok_E"], dtype=np.float64)
    new = tok * np.maximum(1.0 + float(sigma) * np.asarray(noise, float), 0.0)
    s_old, s_new = tok.sum(axis=1), new.sum(axis=1)
    rho = np.where(s_old > 0, s_new / np.where(s_old > 0, s_old, 1.0), 1.0)
    q0, _bad = recoil_q0(reco["pt"], reco["ppar"], reco["q3"])
    return {"pt": np.asarray(reco["pt"], float).copy(), "ppar": np.asarray(reco["ppar"], float).copy(),
            "eavail": rho * np.asarray(reco["eavail"], float),
            "q3": reco_q3(reco["pt"], reco["ppar"], rho * q0), "tok_E": new}


# ------------------------------------------------------------------------------------------- #
# Registry
# ------------------------------------------------------------------------------------------- #
def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _canonical_sha(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj).encode()).hexdigest()


def _sha256(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class Distortion:
    id: str
    family: str
    kind: str                       # "truth_weight" | "reco_transform"
    params: tuple                   # sorted (key, value) pairs; JSON-able values
    description: str
    _table: Any = field(default=None, compare=False, repr=False)

    def spec(self) -> dict[str, Any]:
        return {"version": SPEC_VERSION, "id": self.id, "family": self.family, "kind": self.kind,
                "params": dict(self.params), "description": self.description}

    def content_hash(self) -> str:
        return _canonical_sha(self.spec())

    # -- truth weights -------------------------------------------------------------------- #
    def truth_weight(self, truth: Mapping[str, np.ndarray]) -> np.ndarray:
        """Un-normalized per-event weight from truth arrays: `eavail`, `q3`, `pt`, `ppar`
        and, for D4, the species counts `n_pipm`, `n_pi0`, `n_p`, `n_n`."""
        if self.kind != "truth_weight":
            raise TypeError(f"{self.id} is not a truth distortion")
        p = dict(self.params)
        if self.family == "D1":
            return clipped_exp_tilt(truth["eavail"], p["amplitude"], p["p50"], p["iqr"],
                                    p["clip_z"])
        if self.family == "D2":
            return gaussian_bump(truth["eavail"], p["amplitude"], p["centre_gev"], p["width_gev"])
        if self.family == "D3":
            return clipped_exp_tilt(eavail_over_q3(truth["eavail"], truth["q3"]),
                                    p["amplitude"], p["p50"], p["iqr"], p["clip_z"])
        if self.family == "D4":
            return multiplicity_weight(truth[f"n_{p['species']}"], p["factor"])
        if self.family == "D5":
            if self._table is None:
                raise RuntimeError(f"{self.id}: no weight table loaded")
            return generator_weight(truth["pt"], truth["ppar"], truth["eavail"], self._table)[0]
        raise ValueError(self.family)

    # -- reco transforms ------------------------------------------------------------------ #
    def transform(self, reco: Mapping[str, np.ndarray], noise: np.ndarray | None = None
                  ) -> dict[str, np.ndarray]:
        if self.kind != "reco_transform":
            raise TypeError(f"{self.id} is not a reco distortion")
        p = dict(self.params)
        if self.family == "R1":
            return hadronic_scale(reco, p["scale"])
        if self.family == "R2":
            return muon_scale(reco, p["scale"])
        if self.family == "R3":
            if noise is None:
                raise ValueError("R3 needs token_noise(identity) for the same rows")
            return cluster_smear(reco, p["sigma"], noise)
        raise ValueError(self.family)


def _p(**kw: Any) -> tuple:
    return tuple(sorted(kw.items()))


def load_calibration(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def registry(d3: Mapping[str, Any] | None = None, d5: Mapping[str, Any] | None = None
             ) -> dict[str, Distortion]:
    """Every Amendment-1 distortion, by id. ``d3`` / ``d5`` default to the committed calibration
    files (`calibration/`); a family whose calibration is absent is left out (never guessed)."""
    if d3 is None and D3_CALIBRATION.exists():
        d3 = load_calibration(D3_CALIBRATION)
    if d5 is None and D5_CALIBRATION.exists():
        d5 = load_calibration(D5_CALIBRATION)
    out: dict[str, Distortion] = {}

    def add(d: Distortion) -> None:
        if d.id in out:
            raise ValueError(f"duplicate id {d.id}")
        out[d.id] = d

    for a in (-0.70, -0.35, -0.175, 0.175, 0.35, 0.70):
        add(Distortion(f"D1_{'p' if a > 0 else 'm'}{abs(a):.3f}", "D1", "truth_weight",
                       _p(amplitude=a, p50=D1_P50_GEV, iqr=D1_IQR_GEV, clip_z=TILT_CLIP_Z),
                       "historical clipped exponential tilt in true E_avail (development "
                       "standardization, frozen)"))
    for c, s in ((0.3, 0.15), (1.0, 0.4)):
        add(Distortion(f"D2_bump_c{c:.1f}", "D2", "truth_weight",
                       _p(amplitude=0.5, centre_gev=c, width_gev=s),
                       "Gaussian bump 1 + A exp(-((E_avail - c)/s)^2) in true E_avail"))
    if d3 is not None:
        for a in (0.35, -0.35):
            add(Distortion(f"D3_{'p' if a > 0 else 'm'}{abs(a):.2f}", "D3", "truth_weight",
                           _p(amplitude=a, p50=float(d3["p50"]), iqr=float(d3["iqr"]),
                              clip_z=TILT_CLIP_Z, standardization_sha256=d3["sha256"]),
                           "clipped exponential tilt in the standardized ratio true E_avail / "
                           "true q3 (pool-T quantiles); q3 <= 0 or non-finite -> weight 1"))
    for species in ("pipm", "pi0", "p", "n"):
        tag = {"pipm": "D4a", "pi0": "D4b", "p": "D4c", "n": "D4d"}[species]
        for f, name in ((1.3, "up"), (1.0 / 1.3, "down")):
            add(Distortion(f"{tag}_{species}_{name}", "D4", "truth_weight",
                           _p(species=species, pdg=PDG[species], factor=f),
                           f"f^N, N = stored truth hadrons with |pdg| = {PDG[species]} among the "
                           f"<= {N_TOKENS} highest-energy (part_gen truncation)"))
    if d5 is not None:
        for gen, table in d5["tables"].items():
            add(Distortion(f"D5_{gen}", "D5", "truth_weight",
                           _p(generator=gen, table_sha256=table["table_sha256"],
                              source_sha256=table["sources"]["generator"]["sha256"],
                              reference_sha256=table["sources"]["reference"]["sha256"],
                              clip=tuple(D5_CLIP), max_rel_err=D5_MAX_REL_ERR),
                           f"sigma_X / sigma_TuneV1 per 3D bin, X = {table['label']}",
                           _table=table))
    if d5 is not None:
        for gen, table in d5.get("tables_post_hoc", {}).items():
            add(Distortion(f"D5p_{gen}", "D5", "truth_weight",
                           _p(generator=gen, table_sha256=table["table_sha256"],
                              source_sha256=table["sources"]["generator"]["sha256"],
                              reference_sha256=table["sources"]["reference"]["sha256"],
                              clip=tuple(D5_CLIP), max_rel_err=D5_MAX_REL_ERR,
                              normalization=table["normalization"], predeclared=False),
                           f"POST-HOC, NOT PREDECLARED: D5 with each prediction normalized "
                           f"within each p_par slice, X = {table['label']}",
                           _table=table))
    for s in (1.05, 0.95):
        add(Distortion(f"R1_x{s:.2f}", "R1", "reco_transform", _p(scale=s),
                       "hadronic energy scale: reco E_avail, every stored token energy and q0 "
                       "x s; reco q3 recomputed"))
    for s in (1.01, 0.99):
        add(Distortion(f"R2_x{s:.2f}", "R2", "reco_transform", _p(scale=s),
                       "muon momentum scale: reco p_T, p_par x s; reco q3 recomputed"))
    add(Distortion("R3_s0.10", "R3", "reco_transform", _p(sigma=0.10),
                   "independent 10% Gaussian smearing of each stored token energy; reco E_avail "
                   "and q0 x (sum E'/sum E) over stored tokens; reco q3 recomputed"))
    return out


@dataclass(frozen=True)
class Case:
    """What a pseudodata sample receives: a truth weight, a reco transform, or both."""
    id: str
    truth: Distortion | None
    reco: Distortion | None

    def spec(self) -> dict[str, Any]:
        return {"id": self.id,
                "truth": None if self.truth is None else self.truth.spec(),
                "reco": None if self.reco is None else self.reco.spec(),
                "truth_hash": None if self.truth is None else self.truth.content_hash(),
                "reco_hash": None if self.reco is None else self.reco.content_hash()}

    def content_hash(self) -> str:
        return _canonical_sha(self.spec())


COMBINED_WITH = "D1_p0.350"


def cases(reg: Mapping[str, Distortion] | None = None) -> dict[str, Case]:
    """Every scored case of Amendment 1: each truth distortion alone; each R alone (the null:
    spurious displacement) and each R combined with D1 at +0.35."""
    reg = registry() if reg is None else reg
    out = {}
    for d in reg.values():
        if d.kind == "truth_weight":
            out[d.id] = Case(d.id, d, None)
    for d in reg.values():
        if d.kind == "reco_transform":
            out[d.id] = Case(d.id, None, d)
            out[f"{d.id}+{COMBINED_WITH}"] = Case(f"{d.id}+{COMBINED_WITH}", reg[COMBINED_WITH], d)
    return out
