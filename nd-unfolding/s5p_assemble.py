#!/usr/bin/env python3
"""s5p Stage 4: assemble a reporting definition's matched central value and total uncertainty.

One declared estimator configuration, one negweight-refined footing. From the committed-code products of
that configuration on the real data it forms, over the REPORTED functionals of one reporting definition
(amendment 1: RD1 = the 109 J cells + the 42 (E_avail,W) cells + the total; RD2 = the 32 H2 cells + the
total; RD3 = the (E_avail,W) cells + the total; cell-integrated cross sections, cm^2/nucleon):

* ``f``: the central value (the configuration's unperturbed data product);
* ``C_stat``: the sample covariance (ddof = 1) of the refit-per-replica data bootstrap replicas (data
  Poisson, MC Poisson(1), template Poisson(1), refinement refit);
* ``C_num``: the sample covariance of the rounding-scale jitters of the data product, used ONLY when the
  Stage-2 absorption rule did not find the numerical component inside the bootstrap (``--numerical explicit``);
* per systematic band b: ``C_b = (1/N_b) sum_u (x_u - f)(x_u - f)^T`` over the band's universes (centred on
  the matched CV, the adopted 'cv' convention), for the vertical/flux bank, the weight-only detector bands and
  the five selection-complete lateral bands;
* ``C_norm = (0.014 f)(0.014 f)^T`` (the flat normalization of the adopted construction);
* ``h``: the unfolding-model (regularization) bounded component, ``h_f = s * max_k |x_k,f - f_f|`` over the
  declared prior-variation vertices k (data unfolded with the MC truth prior reweighted to each vertex), with
  the frozen scale factor s; a DETERMINISTIC bound over the declared model domain, never a covariance.

``C_prob = C_stat [+ C_num] + sum_b C_b + C_norm``; ``sigma_prob = sqrt(diag C_prob)``. The frozen total
intervals are ``f +- (z sigma_prob + h)`` with z = 1 (68%) and 1.96 (95%): a bounded-nuisance interval whose
coverage claim holds for truths inside the model domain. The product stores every block separately so that
nothing is double counted downstream and a user can profile the bounded component.

MEASURES: the assembled blocks of one configuration and reporting definition. CANNOT AUTHORIZE: coverage,
adoption or any inference by itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import s5p_stage1_inspect as s1

NORM_FRACTION = 0.014
DEFINITIONS = ("RD1", "RD2", "RD3")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def functional_matrix(definition: str, stage1: dict, supported: list[int]) -> tuple[np.ndarray, list[str]]:
    """Rows over the fine grid: fine-bin volume where the fine cell belongs to the reporting cell."""
    vol = s1.fine_volume()
    blocks = []
    if definition == "RD1":
        blocks = [("J", *s1.coarse_map(s1.J_EDGES, supported)), ("EW", *s1.ew_map())]
    elif definition == "RD2":
        blocks = [("H2", *s1.coarse_map(s1.H2_EDGES))]
    elif definition == "RD3":
        blocks = [("EW", *s1.ew_map())]
    rows, names = [], []
    for P, cmap, n in blocks:
        rep = np.asarray(stage1["mc"][P]["reported"], bool)
        labels = [f"J{c}" for c in supported] if P == "J" else ([f"H2_{c}" for c in range(n)] if P == "H2" else [f"EW{i}" for i in range(n)])
        for c in range(n):
            if not rep[c]:
                continue
            rows.append(np.where(cmap == c, vol, 0.0))
            names.append(labels[c])
    rows.append(vol)
    names.append("total")
    return np.vstack(rows), names


def xs(path: Path) -> np.ndarray:
    return np.asarray(np.load(path, allow_pickle=False)["xsec_flat"], float)


def band_cov(U: np.ndarray, f: np.ndarray, paths: list[Path]) -> np.ndarray:
    D = np.array([U @ xs(p) - f for p in paths])
    return D.T @ D / len(paths)


def band_of(path: Path, tag: str) -> str:
    stem = path.stem[len(tag) + 1:]
    return stem.rsplit("_", 1)[0]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--definition", choices=DEFINITIONS, required=True)
    ap.add_argument("--stage1", type=Path, required=True)
    ap.add_argument("--s5c-contract", type=Path, required=True)
    ap.add_argument("--central", type=Path, required=True)
    ap.add_argument("--bootstrap", type=Path, nargs="+", required=True)
    ap.add_argument("--jitters", type=Path, nargs="*", default=[])
    ap.add_argument("--numerical", choices=("absorbed", "explicit"), required=True)
    ap.add_argument("--universe-dir", type=Path, nargs="+", required=True, help="directories of s5p_universe products")
    ap.add_argument("--universe-tag", required=True)
    ap.add_argument("--lateral", type=Path, nargs="*", default=[], help="lateral endpoint products named lat_<band>_<i>*.npz")
    ap.add_argument("--priors", type=Path, nargs="*", default=[], help="prior-variation products (the model-domain vertices)")
    ap.add_argument("--envelope-scale", type=float, required=True)
    ap.add_argument("--expect-universes", type=int, required=True, help="the declared universe count (fail closed)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    stage1 = json.loads(a.stage1.read_text())
    supported = json.loads(a.s5c_contract.read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names = functional_matrix(a.definition, stage1, supported)
    f = U @ xs(a.central)
    R = np.array([U @ xs(p) for p in a.bootstrap])
    C_stat = np.cov(R, rowvar=False, ddof=1)
    blocks = {"stat": C_stat}
    if a.numerical == "explicit":
        if len(a.jitters) < 20:
            raise SystemExit("an explicit numerical component needs >= 20 jitters")
        J = np.array([U @ xs(p) for p in a.jitters])
        blocks["numerical"] = np.cov(J, rowvar=False, ddof=1)
    unis = sorted(p for d in a.universe_dir for p in d.glob(f"{a.universe_tag}_*.npz") if not p.stem.endswith("_CV")
                  and "_prior_" not in p.stem)
    if len(unis) != a.expect_universes:
        raise SystemExit(f"{len(unis)} universe products found, {a.expect_universes} declared")
    bands: dict[str, list[Path]] = {}
    for p in unis:
        bands.setdefault(band_of(p, a.universe_tag), []).append(p)
    for p in a.lateral:
        stem = p.stem.removesuffix("_b-_j-")
        if not stem.startswith("lat_"):
            raise SystemExit(f"lateral product {p.name} is not named lat_<band>_<i>")
        bands.setdefault("lat:" + stem[4:].rsplit("_", 1)[0], []).append(p)
    for b, ps in sorted(bands.items()):
        blocks[f"band:{b}"] = band_cov(U, f, ps)
    blocks["normalization"] = np.outer(NORM_FRACTION * f, NORM_FRACTION * f)
    C_prob = sum(blocks.values())
    shifts = np.array([U @ xs(p) - f for p in a.priors]) if a.priors else np.zeros((0, f.size))
    h = a.envelope_scale * (np.abs(shifts).max(axis=0) if shifts.size else np.zeros_like(f))
    sig = np.sqrt(np.clip(np.diag(C_prob), 0, None))
    out = {"f": f, "sigma_prob": sig, "h": h, "C_prob": C_prob, "prior_shifts": shifts,
           "halfwidth68": sig + h, "halfwidth95": 1.96 * sig + h, "U": U.astype(np.float32)}
    for k, v in blocks.items():
        out["C_" + k.replace(":", "_")] = v
    meta = {"schema": "s5p-assembly/1", "definition": a.definition, "functional_names": names, "numerical": a.numerical,
            "envelope_scale": a.envelope_scale, "normalization_fraction": NORM_FRACTION,
            "central": {"path": str(a.central), "sha256": sha256(a.central)},
            "bootstrap_replicas": len(a.bootstrap), "jitters": len(a.jitters),
            "bands": {b: [str(p) for p in ps] for b, ps in sorted(bands.items())},
            "priors": [str(p) for p in a.priors],
            "inputs_sha256": {str(p): sha256(p) for p in [*a.bootstrap, *unis, *a.lateral, *a.priors, *a.jitters]},
            "code_sha256": {"s5p_assemble.py": sha256(Path(__file__).resolve())},
            "interpretation": "C_prob probabilistic (bootstrap + band universes as 1-sigma draws + normalization); h deterministic bounded over the declared prior-variation vertices; total interval f +- (z sigma_prob + h)",
            "summary": {"median_sigma_prob_rel": float(np.median(sig[:-1] / f[:-1])), "median_h_rel": float(np.median(h[:-1] / f[:-1])),
                        "median_halfwidth68_rel": float(np.median((sig + h)[:-1] / f[:-1])),
                        "p90_halfwidth68_rel": float(np.percentile((sig + h)[:-1] / f[:-1], 90))}}
    np.savez_compressed(a.out, **out, meta=json.dumps(meta))
    print(json.dumps(meta["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
