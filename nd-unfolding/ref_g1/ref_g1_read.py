#!/usr/bin/env python3
"""REF-G1 reader: R1's calibrated bars, committed before the central difference is formed; then R1, R2, R3 and the
controls (frozen; REF-G1-DECLARATION.md §3-§5, DECISION-20261104-joseph-g1-r1-calibrated-bars.md items 2-6).

  bars  --run DIR --out DIR/bars.json
        From the paired replica and universe differences alone, never the central Delta: C_stat (50 replicas,
        ddof 1), C_flux (S1's weighted Flux estimator over the 100 PPFX universes), C_fixed (S1's estimator on every
        other band, held fixed). T's null is a seeded parametric bootstrap at that composition (10^6 draws): each
        draw re-estimates C_stat from 50 vectors and C_flux from 100 weighted vectors, draws Delta* from
        N(0, C_stat + C_univ), forms C_norm* from Delta* itself, and computes the uncorrected T*. The stat-only
        limit must match (n-1)p/(n-p) F(p, n-p) within Monte Carlo error, or nothing is written. Refuses if the
        read's output already exists beside the bars.
  read  --run DIR --bars DIR/bars.json --bars-sha256 SHA --out DIR/readout.json
        Refuses unless the bars file has that sha256 and was made from these same products. Then forms Delta,
        reads R1 against the bars, prints what the declaration lists beside it, and applies R2, R3 and the controls
        G-CV, G-IBU1, G-cells, G-pair and G-draw. Every value written is dimensionless.

MEASURES: the declared readings on the declared products. CANNOT AUTHORIZE: a reported estimator, a systematic, a
coverage statement or any claim; paper text goes through the paper lane, the PRD read and Joseph (REF-G1 §5).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_g1 as G  # noqa: E402

N_CELLS = 16


class Refused(RuntimeError):
    """A precondition of the reading failed: nothing is written."""


# ------------------------------------------------------------------------------------------- products


def load(path: Path) -> tuple[dict, dict]:
    with np.load(path, allow_pickle=False) as z:
        arrays = {k: np.asarray(z[k]) for k in z.files if k != "meta"}
        meta = json.loads(str(z["meta"])) if "meta" in z.files else {}
    return arrays, meta


def at_k(arrays: dict, k: int, variant: str) -> np.ndarray:
    ks = [int(v) for v in arrays["ks"]]
    if k not in ks:
        raise Refused(f"K = {k} is not in the product's set {ks}")
    return np.asarray(arrays[f"F_{variant}"][ks.index(k)], float)


def ibu_cells(run: Path, unit: str, cfg: dict) -> tuple[np.ndarray, dict]:
    p = run / f"{unit}.npz"
    if not p.exists():
        raise Refused(f"the IBU unit {unit} is missing from {run}")
    arrays, meta = load(p)
    return at_k(arrays, cfg["iterations"]["primary"], cfg["background"]["primary"]), meta


def e_cells(path: Path, U: np.ndarray) -> np.ndarray:
    with np.load(path, allow_pickle=False) as z:
        return U @ np.asarray(z["xsec_flat"], float)


def band_order(tags: list[str]) -> dict[str, list[str]]:
    """BAND -> its universe tags in universe order (s1_assemble.universe_bands' order)."""
    out: dict[str, list[str]] = {}
    for t in tags:
        band, idx = t.split(":")
        out.setdefault(band, []).append(idx)
    return {b: [f"{b}:{i}" for i in sorted(v, key=int)] for b, v in out.items()}


class Paired:
    """The IBU products of one run directory and the (e) products they pair with, as R00-R15 cell integrals."""

    def __init__(self, lib, cfg: dict, run: Path, U: np.ndarray):
        self.lib, self.cfg, self.run, self.U = lib, cfg, run, U
        ep = cfg["e_products"]
        r = cfg["replicas"]
        self.bs = list(range(r["first"], r["last"] + 1))
        self.offset = int(r["jitter_offset"])
        self.replica_paths = {b: Path(ep["replica"].format(b=b, j=self.offset + b)) for b in self.bs}
        self.tags = G.universes(cfg)
        self.universe_paths = {t: Path(ep["universe"].format(tag=t.replace(":", "_"))) for t in self.tags}

    def replica_deltas(self) -> tuple[np.ndarray, list[dict]]:
        rows, metas = [], []
        for b in self.bs:
            x, m = ibu_cells(self.run, f"replica_b{b}", self.cfg)
            rows.append(x - e_cells(self.replica_paths[b], self.U))
            metas.append(m)
        return np.array(rows), metas

    def universe_deltas(self) -> tuple[dict[str, np.ndarray], list[dict]]:
        out, metas = {}, []
        for band, tags in band_order(self.tags).items():
            rows = []
            for t in tags:
                b, i = t.split(":")
                x, m = ibu_cells(self.run, f"universe_{b}_{i}", self.cfg)
                rows.append(x - e_cells(self.universe_paths[t], self.U))
                metas.append(m)
            out[band] = np.array(rows)
        return out, metas

    def digest(self) -> str:
        """sha256 over every IBU and (e) file the bars read, in a fixed order: the read refuses other products."""
        h = hashlib.sha256()
        for b in self.bs:
            for p in (self.run / f"replica_b{b}.npz", self.replica_paths[b]):
                h.update(G.sha256(p).encode())
        for t in self.tags:
            b, i = t.split(":")
            for p in (self.run / f"universe_{b}_{i}.npz", self.universe_paths[t]):
                h.update(G.sha256(p).encode())
        return h.hexdigest()


# ------------------------------------------------------------------------------------------- covariance blocks


def universe_blocks(lib, deltas: dict[str, np.ndarray], wflux: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """C_flux by S1's weighted estimator; C_fixed, the sum of S1's estimator over every other band (s1_assemble.py:
    11-22, mat_cov)."""
    flux = deltas[lib.s1a.FLUX]
    if flux.shape[0] != wflux.size:
        raise Refused(f"{flux.shape[0]} Flux universes against {wflux.size} constraint weights")
    c_flux = lib.s1a.mat_cov(flux, wflux)
    c_fixed = np.zeros((flux.shape[1], flux.shape[1]))
    for band, X in deltas.items():
        if band != lib.s1a.FLUX:
            c_fixed += lib.s1a.mat_cov(X)
    return c_flux, c_fixed


def psd_root(C: np.ndarray) -> np.ndarray:
    lam, V = np.linalg.eigh((C + C.T) / 2)
    return V * np.sqrt(np.clip(lam, 0, None))


def weighted_cov_batch(Y: np.ndarray, w: np.ndarray) -> np.ndarray:
    """S1's mat_cov (MAT CalcCovMx: weighted-mean-centred, over the weight sum) on a batch of draws, Y[m, n, p];
    tested equal to ``s1_assemble.mat_cov`` draw by draw."""
    Z = Y - (w[None, :, None] * Y).sum(axis=1, keepdims=True) / w.sum()
    return np.einsum("mni,n,mnj->mij", Z, w, Z) / w.sum()


def null_t(c_stat: np.ndarray, c_flux: np.ndarray, w_flux: np.ndarray, c_fixed: np.ndarray, n_rep: int, draws: int,
           seed: int, batch: int, norm: float, resample_flux: bool = True) -> np.ndarray:
    """T* under 'no difference' at the realized blocks (decision item 2). Delta* ~ N(0, C_stat + C_flux + C_fixed);
    C_stat* is the ddof-1 covariance of n_rep vectors from N(0, C_stat); C_flux* is S1's weighted estimator over
    w_flux.size vectors from N(0, C_flux); C_norm* = (norm Delta*)(norm Delta*)^T from the draw's own Delta*. T* is
    the production formula, uncorrected. No argument carries the realized Delta."""
    rng = np.random.default_rng(seed)
    p = c_stat.shape[0]
    r_stat, r_flux = psd_root(c_stat), psd_root(c_flux)
    r_true = psd_root(c_stat + c_flux + c_fixed)
    w = np.asarray(w_flux, float)
    out = np.empty(draws)
    for s in range(0, draws, batch):
        m = min(batch, draws - s)
        Z = rng.standard_normal((m, n_rep, p)) @ r_stat.T
        Z -= Z.mean(axis=1, keepdims=True)
        C = np.einsum("mni,mnj->mij", Z, Z) / (n_rep - 1)
        if resample_flux:
            Y = rng.standard_normal((m, w.size, p)) @ r_flux.T
            C += weighted_cov_batch(Y, w)
        else:
            C += c_flux
        C += c_fixed
        D = rng.standard_normal((m, p)) @ r_true.T
        C += (norm ** 2) * np.einsum("mi,mj->mij", D, D)
        out[s:s + m] = np.einsum("mi,mi->m", D, np.linalg.solve(C, D[..., None])[..., 0])
    return out


def hotelling_quantiles(qs, n_rep: int, p: int) -> list[float]:
    from scipy import stats
    return [float((n_rep - 1) * p / (n_rep - p) * stats.f.ppf(q, p, n_rep - p)) for q in qs]


def self_check(c_stat: np.ndarray, n_rep: int, draws: int, seed: int, batch: int, qs, z: float) -> dict:
    """Decision item 4: the stat-only limit of the procedure (no universe block, no C_norm) against the F law. The
    empirical CDF at each law quantile must lie within z binomial standard errors of its level."""
    p = c_stat.shape[0]
    zero = np.zeros_like(c_stat)
    t = null_t(c_stat, zero, np.ones(2), zero, n_rep, draws, seed, batch, 0.0, resample_flux=False)
    law = hotelling_quantiles(qs, n_rep, p)
    rows = []
    for q, ql in zip(qs, law):
        cdf = float(np.mean(t <= ql))
        tol = z * np.sqrt(q * (1 - q) / draws)
        rows.append({"level": q, "law_quantile": ql, "empirical_cdf_at_law_quantile": cdf, "tolerance": tol,
                     "pass": bool(abs(cdf - q) <= tol)})
    return {"law": f"({n_rep}-1)*{p}/({n_rep}-{p}) F({p}, {n_rep - p})", "draws": draws, "seed": seed, "rows": rows,
            "pass": all(r["pass"] for r in rows)}


def bars(lib, cfg: dict, run: Path, out: Path, U: np.ndarray, wflux: np.ndarray) -> dict:
    if (out.parent / "readout.json").exists():
        raise Refused("the central difference has already been read beside these bars: the bars come first")
    rd = cfg["readings"]
    b = rd["bars"]
    paired = Paired(lib, cfg, run, U)
    dR, _ = paired.replica_deltas()
    dU, _ = paired.universe_deltas()
    n_rep = dR.shape[0]
    c_stat = np.cov(dR, rowvar=False, ddof=1)
    c_flux, c_fixed = universe_blocks(lib, dU, wflux)
    sc = self_check(c_stat, n_rep, b["draws"], rd["self_check"]["seed"], b["batch"], b["quantiles"],
                    rd["self_check"]["z"])
    if not sc["pass"]:
        raise Refused(f"the self-check failed: {sc['rows']}")
    t = null_t(c_stat, c_flux, wflux, c_fixed, n_rep, b["draws"], b["seed"], b["batch"], rd["norm_fraction"])
    t_stat = null_t(c_stat, np.zeros_like(c_stat), np.ones(2), np.zeros_like(c_stat), n_rep, b["draws"], b["seed"],
                    b["batch"], rd["norm_fraction"], resample_flux=False)
    rec = {"schema": "ref-g1-bars/1", "quantile_levels": b["quantiles"],
           "bars": [float(np.quantile(t, q)) for q in b["quantiles"]],
           "sensitivity_stat_only_null": [float(np.quantile(t_stat, q)) for q in b["quantiles"]],
           "draws": b["draws"], "seed": b["seed"], "n_replicas": n_rep, "flux_universes": int(wflux.size),
           "fixed_bands": sorted(k for k in dU if k != lib.s1a.FLUX), "norm_fraction": rd["norm_fraction"],
           "self_check": sc, "products_digest": paired.digest(), "reader_sha256": G.sha256(Path(__file__).resolve()),
           "config_sha256": G.sha256(G.CONFIG), "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1) + "\n")
    return rec


# ------------------------------------------------------------------------------------------- readings


def classify_r1(t: float, bar_lo: float, bar_hi: float) -> str:
    return "agree" if t <= bar_lo else ("marginal" if t <= bar_hi else "differ")


def classify_r2(ratio: float, band: tuple[float, float]) -> str:
    lo, hi = band
    return "within" if lo <= ratio <= hi else ("IBU better" if ratio < lo else "IBU worse")


def t_stat(delta: np.ndarray, C: np.ndarray) -> float:
    return float(delta @ np.linalg.solve(C, delta))


def formed(C: np.ndarray, cond_max: float) -> dict:
    lam = np.linalg.eigvalsh((C + C.T) / 2)
    ok = bool(lam.min() > 0 and lam.max() / lam.min() < cond_max)
    return {"positive_definite": bool(lam.min() > 0), "condition": float(lam.max() / lam.min()) if lam.min() > 0 else None,
            "pass": ok, "eigenvalues_relative": (lam / lam.max()).tolist()}


def block_sigma(lib, central: np.ndarray, reps: np.ndarray, univ: dict[str, np.ndarray], wflux: np.ndarray,
                vertices: np.ndarray, norm: float) -> np.ndarray:
    """R3: one estimator's per-cell sigma from the stat, universe, normalisation and model blocks, each by S1's
    estimator; the model block is build_cmodel5d's, s_k = X_k / X_0 - 1 over the three vertices, kappa = 1."""
    C = np.cov(reps, rowvar=False, ddof=1)
    c_flux, c_fixed = universe_blocks(lib, univ, wflux)
    C = C + c_flux + c_fixed + np.outer(norm * central, norm * central)
    s = vertices / central[None, :] - 1.0
    C = C + np.diag(central) @ (s.T @ s) @ np.diag(central)
    return np.sqrt(np.diag(C))


def read(lib, cfg: dict, run: Path, bars_path: Path, bars_sha: str, out: Path, U: np.ndarray,
         wflux: np.ndarray) -> dict:
    if G.sha256(bars_path) != bars_sha:
        raise Refused("the bars file is not the committed one (sha256 differs)")
    bars_rec = json.loads(bars_path.read_text())
    if (bars_rec.get("reader_sha256"), bars_rec.get("config_sha256")) != (G.sha256(Path(__file__).resolve()),
                                                                          G.sha256(G.CONFIG)):
        raise Refused("the bars were made by another reader or configuration")
    rd = cfg["readings"]
    paired = Paired(lib, cfg, run, U)
    if paired.digest() != bars_rec["products_digest"]:
        raise Refused("the bars were computed from other products")
    controls = {}
    dR, rep_meta = paired.replica_deltas()
    dU, uni_meta = paired.universe_deltas()
    controls["G-draw"] = {"pass": all(m.get("g_draw", {}).get("pass") is True for m in rep_meta),
                          "replicas": len(rep_meta)}
    controls["G-pair"] = g_pair(lib, cfg, paired, rep_meta, uni_meta)
    ep = cfg["e_products"]
    x_ibu, _ = ibu_cells(run, "central", cfg)
    x_e = e_cells(Path(ep["central"]), U)
    controls["G-CV"] = g_cv(run)
    controls["G-IBU1"] = g_ibu1(cfg, run)
    controls["G-cells"] = g_cells(cfg, x_e)
    failed = [name for name, c in controls.items() if not c["pass"]]
    if failed:  # §3.3: a failed control stops the run; no Delta is formed and no reading is written
        stop = {"schema": "ref-g1-stop/1", "stopped": True, "stopped_by": failed, "controls": controls,
                "bars_sha256": bars_sha, "reader_sha256": G.sha256(Path(__file__).resolve()),
                "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        (out.parent / "STOP.json").write_text(json.dumps(stop, indent=1) + "\n")
        return stop
    # Delta is formed only here, after the bars' sha256 and provenance and every control were checked
    delta = x_ibu - x_e
    n_rep = dR.shape[0]
    c_stat = np.cov(dR, rowvar=False, ddof=1)
    c_flux, c_fixed = universe_blocks(lib, dU, wflux)
    c_norm = np.outer(rd["norm_fraction"] * delta, rd["norm_fraction"] * delta)
    C = c_stat + c_flux + c_fixed + c_norm
    gate = formed(C, rd["condition_max"])
    lo, hi = bars_rec["bars"]
    r1 = {"formed": gate}
    if gate["pass"]:
        t = t_stat(delta, C)
        r1.update(T=t, bars=[lo, hi], reading=classify_r1(t, lo, hi))
    else:
        r1.update(reading="not formed")
    from scipy import stats
    p = N_CELLS
    h = (n_rep - p - 2) / (n_rep - 1)
    beside = {
        "chi2_bars": [float(stats.chi2.ppf(q, p)) for q in bars_rec["quantile_levels"]],
        "hartlap": {"factor": h, "T": t_stat(delta, c_stat / h + c_flux + c_fixed + c_norm),
                    "F_bars": [h * v for v in hotelling_quantiles(bars_rec["quantile_levels"], n_rep, p)]},
        "sensitivity_stat_only_null": {"T": t_stat(delta, c_stat + c_norm),
                                       "bars": bars_rec["sensitivity_stat_only_null"]},
        "pulls": (delta / np.sqrt(np.diag(C))).tolist(),
        "delta_over_e": (delta / x_e).tolist(),
        "stated_direction": "the null treats the paired universe differences as scatter in Delta; if the two "
                            "estimators respond to systematics alike, the reading leans toward 'agree'",
    }
    beside["every_k_and_variant_delta_over_e"] = every_k(cfg, run, x_e)
    vertices_ibu, vertices_e = [], []
    for v in cfg["vertices"]:
        vi, _ = ibu_cells(run, f"vertex_{v}", cfg)
        ve = e_cells(Path(ep["ladder"].format(name=v)), U)
        vertices_ibu.append(vi)
        vertices_e.append(ve)
    beside["vertex_delta_over_e"] = {v: ((vi - ve) / ve).tolist() for v, vi, ve in zip(cfg["vertices"], vertices_ibu, vertices_e)}
    r2 = reading_r2(cfg, run, U)
    reps_ibu = np.array([ibu_cells(run, f"replica_b{b}", cfg)[0] for b in paired.bs])
    reps_e = np.array([e_cells(paired.replica_paths[b], U) for b in paired.bs])
    univ_ibu, univ_e = {}, {}
    for band, tags in band_order(paired.tags).items():
        univ_ibu[band] = np.array([ibu_cells(run, "universe_" + t.replace(":", "_"), cfg)[0] for t in tags])
        univ_e[band] = np.array([e_cells(paired.universe_paths[t], U) for t in tags])
    s_ibu = block_sigma(lib, x_ibu, reps_ibu, univ_ibu, wflux, np.array(vertices_ibu), rd["norm_fraction"])
    s_e = block_sigma(lib, x_e, reps_e, univ_e, wflux, np.array(vertices_e), rd["norm_fraction"])
    ratio = s_ibu / s_e
    r3 = {"sigma_ibu_over_e": ratio.tolist(), "median": float(np.median(ratio)),
          "note": "(e)'s C_stat absorbs its estimator noise (refit per replica, jitter); IBU has none"}
    rec = {"schema": "ref-g1-readout/1", "bars_sha256": bars_sha, "R1": r1, "printed_beside_R1": beside, "R2": r2,
           "R3": r3, "controls": controls, "controls_pass": all(c["pass"] for c in controls.values()),
           "reader_sha256": G.sha256(Path(__file__).resolve()), "config_sha256": G.sha256(G.CONFIG),
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out.write_text(json.dumps(rec, indent=1) + "\n")
    return rec


def every_k(cfg: dict, run: Path, x_e: np.ndarray) -> dict:
    arrays, _ = load(run / "central.npz")
    out = {}
    for variant in ("fold", "sub"):
        for i, k in enumerate(int(v) for v in arrays["ks"]):
            out[f"{variant}_K{k}"] = ((np.asarray(arrays[f"F_{variant}"][i], float) - x_e) / x_e).tolist()
    return out


def reading_r2(cfg: dict, run: Path, U: np.ndarray) -> dict:
    """At each of F0b's noise-free closure truths: median |f/f_true - 1| over R00-R15, IBU over (e), in IBU-1's
    factor-2 band. (e)'s closures carry estimator-seed noise and IBU's none; a point reading."""
    out = {}
    for name, product in cfg["closures"].items():
        arrays, _ = load(run / f"closure_{name}.npz")
        x_ibu = at_k(arrays, cfg["iterations"]["primary"], cfg["background"]["primary"])
        t_ibu = np.asarray(arrays["X_true"], float)
        with np.load(Path(cfg["e_products"]["closure"].format(product=product)), allow_pickle=False) as z:
            x_e, t_e = U @ np.asarray(z["xsec_flat"], float), U @ np.asarray(z["xtrue_flat"], float)
        m_ibu = float(np.median(np.abs(x_ibu / t_ibu - 1)))
        m_e = float(np.median(np.abs(x_e / t_e - 1)))
        ratio = m_ibu / m_e
        out[name] = {"median_abs_residual_ibu": m_ibu, "median_abs_residual_e": m_e, "ratio": ratio,
                     "reading": classify_r2(ratio, tuple(cfg["readings"]["r2_band"])),
                     "truths_agree_rel": float(np.max(np.abs(t_ibu / t_e - 1)))}
    return out


# ------------------------------------------------------------------------------------------- controls


def g_cv(run: Path) -> dict:
    a, _ = load(run / "central.npz")
    b, _ = load(run / "universe_CV.npz")
    same = all(np.array_equal(a[k], b[k]) for k in ("ks", "F_fold", "F_sub"))
    return {"pass": bool(same)}


def g_ibu1(cfg: dict, run: Path) -> dict:
    ref = Path(cfg["gibu1_reference"]["path"])
    if G.sha256(ref) != cfg["gibu1_reference"]["sha256"]:
        return {"pass": False, "why": "IBU-1's D_N.npz digest differs"}
    a, _ = load(run / "gibu1.npz")
    b, _ = load(ref)
    keys = ("ks", "F_fold", "F_sub")
    same = {k: bool(k in b and np.array_equal(a[k], b[k])) for k in keys}
    return {"pass": all(same.values()), "arrays": same}


def g_cells(cfg: dict, x_e: np.ndarray) -> dict:
    ep = cfg["e_products"]
    p = Path(ep["s1_assembly"])
    if G.sha256(p) != ep["s1_assembly_sha256"]:
        return {"pass": False, "why": "s1_assembly.npz digest differs"}
    with np.load(p, allow_pickle=False) as z:
        f = np.asarray(z["f"], float)
    rel = float(np.max(np.abs(x_e / f - 1)))
    return {"pass": bool(rel <= cfg["readings"]["gcells_rtol"]), "max_rel": rel}


def g_pair(lib, cfg: dict, paired: Paired, rep_meta: list[dict], uni_meta: list[dict]) -> dict:
    """Every (e) file equals its pin in the committed preconditions listing; each replica carries (e)'s bootstrap and
    jitter seeds (s1_assemble.check_meta) and the IBU replica the same ones; each IBU universe read the same weight
    files as the (e) universe it pairs with."""
    listing = json.loads((G.REPO / cfg["listing"]["path"]).read_text())
    pins = {f["path"]: f["pin"] for g in ("e_central", "e_replicas", "e_universes", "e_ladder_unfolds", "e_f0b_closures")
            for f in listing["files"][g]}
    bad = []
    files = [Path(cfg["e_products"]["central"]), *paired.replica_paths.values(), *paired.universe_paths.values(),
             *(Path(cfg["e_products"]["ladder"].format(name=v)) for v in cfg["vertices"]),
             *(Path(cfg["e_products"]["closure"].format(product=p)) for p in cfg["closures"].values())]
    for p in files:
        if pins.get(str(p)) is None or G.sha256(p) != pins[str(p)]:
            bad.append(f"pin {p.name}")
    for b, m in zip(paired.bs, rep_meta):
        try:
            lib.s1a.check_meta(paired.replica_paths[b], "s5p-numerics/1",
                               expect={"bootstrap_seed": b, "jitter_seed": paired.offset + b, "coords": "float64"})
        except SystemExit as e:
            bad.append(str(e))
        if (m.get("bootstrap_seed"), m.get("jitter_seed")) != (b, paired.offset + b):
            bad.append(f"IBU replica_b{b} seeds")
    by_tag = {m.get("universe"): m for m in uni_meta}
    for t in paired.tags:
        try:
            em = lib.s1a.check_universe(paired.universe_paths[t], t.split(":")[0])
        except SystemExit as e:
            bad.append(str(e))
            continue
        im = by_tag.get(t, {})
        if em.get("universe") != t or (im.get("weight_sha256") or {}) != (em.get("bank_weight_sha256") or {}):
            bad.append(f"universe {t} pairing")
    return {"pass": not bad, "problems": bad[:20], "n_problems": len(bad)}


# ------------------------------------------------------------------------------------------- CLI


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bars")
    b.add_argument("--run", type=Path, required=True)
    b.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("read")
    r.add_argument("--run", type=Path, required=True)
    r.add_argument("--bars", type=Path, required=True)
    r.add_argument("--bars-sha256", required=True)
    r.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    cfg = json.loads(G.CONFIG.read_text())
    try:
        if G.sha256(G.REPO / cfg["listing"]["path"]) != cfg["listing"]["sha256"]:
            raise Refused("the preconditions listing digest differs from config.json")
        lib = G.Lib(cfg)
        U = lib.s1a.functional_matrix(lib.s1a.fine_map(G.REPO / cfg["definition"]["path"]))
        fc = Path(cfg["inputs"]["flux_constraint"])
        wflux = lib.s1a.flux_weights(fc)
        if a.cmd == "bars":
            rec = bars(lib, cfg, a.run, a.out, U, wflux)
            print(json.dumps({"bars": rec["bars"], "sha256": G.sha256(a.out), "self_check": rec["self_check"]["pass"]}))
            return 0
        if a.out.parent.resolve() != a.bars.parent.resolve():
            raise Refused("the readout goes beside its bars, so the bars step can see it")
        rec = read(lib, cfg, a.run, a.bars, a.bars_sha256, a.out, U, wflux)
    except (Refused, G.GateFailure) as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 4
    if rec.get("stopped"):
        print(f"STOP: failed controls {rec['stopped_by']}; no reading was formed", file=sys.stderr)
        return 1
    print(json.dumps({"R1": rec["R1"].get("reading"), "controls_pass": rec["controls_pass"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
