#!/usr/bin/env python3
"""5D community route, S1 (state/measurement-paper/5d-community-20261024/S1-DECLARATION.md): assemble
configuration (e)'s statistical and systematic covariance on the 16 H2 reporting cells R00-R15, and add the
unscaled model component C_model,5D beside it.

The recipe is the adopted 2D one (Stage C R1-R9, `state/2d-closeout/stageC/production/s5_rollup.py`), carried to
the 5D cells; each choice and its record is in the declaration's section 2:

* cells: ``h2_definition.json`` (sha256 ``b6790761...``) composed on ``s5p_stage1_inspect.coarse_map(H2_EDGES)``;
  the expanded fine map must hash to ``930326a3...``. Cell integrals are sum_f x_f vol_f, as in S2 and C_model,5D;
* ``C_stat``: sample covariance (ddof 1) of the 50 refit-per-replica data bootstrap replicas with jitter (s5p
  study N set A; the numerical component is absorbed, amendment 4);
* every universe band: MAT ``CalcCovMx``, mean-centred, 1/N. ``Flux`` carries the nu-e + IMD constraint weights
  (C04, KI 95) and is centred on the weighted mean. ``Rvp1pi`` is not a band (KI 92);
* the five lateral bands: mean-centred over their two endpoints, so no CV enters (``app:pair``).
  ``Muon_Energy_MINOS`` is first rescaled per pT bin by Phi_CV / Phi_MINOS,u (X01, KI 96), the recorded 2D
  factors, which apply because the 5D flux is the same array on the same pT bins;
* ``C_norm = (0.014 f)(0.014 f)^T``;
* ``C_seed``: the estimator-seed main effect (2D's C08, R7): sample covariance (ddof 1) over seeds 42, 45, 48, 51
  and 54 of the per-seed mean of bootstrap replicas 1-20;
* ``C_model_abs = diag(f) C_model diag(f)`` from the fractional C_model,5D of the H2 definition's builder.

No inflation D, no C_ML and no bounded envelope h. ``C_e = C_stat + sum_b C_b + C_norm + C_seed``;
``C_total = C_e + C_model_abs``.

MEASURES: the assembled blocks on the declared inputs. CANNOT AUTHORIZE: coverage, adoption, any claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s5p_stage1_inspect as s1  # noqa: E402

DEFINITION_SHA256 = "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89"
FINE_MAP_SHA256 = "930326a3a7c0852d4047b5468d8ea3b63d046b896e4a4de1557e29f95102e18c"
X01_SHA256 = "8912376ef2a6cfce8bed515cc945d9d5778cf5c838154a685435c3c7ce25416d"
CONSTRAINT_SHA256 = "e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2"
INPUT_NPZ_SHA256 = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
BKG_SHA256 = "2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955"
CENTRAL_SHA256 = "fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c"  # = data_R = P5 (gate G2)
NORM_FRACTION = 0.014
N_CELLS = 16
SEEDS = (42, 45, 48, 51, 54)
SEED_REPLICAS = tuple(range(1, 21))
STAT_REPLICAS = tuple(range(1, 51))
FLUX, MINOS, DROPPED = "Flux", "Muon_Energy_MINOS", "Rvp1pi"
LATERAL_BANDS = ("BeamAngleX", "BeamAngleY", "MuonResolution", "Muon_Energy_MINERvA", MINOS)
DETECTOR_BANDS = ("GEANT_Neutron", "GEANT_Pion", "GEANT_Proton", "MinosEfficiency")
# universes per band, fixed by the bank listing (declaration section 1): 100 Flux, 33 model bands (Rvp1pi out),
# 4 weight-only detector bands from the detector dump
EXPECT = {FLUX: 100, "2p2h": 3, **{b: 2 for b in DETECTOR_BANDS}}
MODEL_BANDS_2 = ("AGKYxF1pi", "AhtBY", "BhtBY", "CCQEPauliSupViaKF", "CV1uBY", "CV2uBY", "EtaNCEL", "FrAbs_N",
                 "FrAbs_pi", "FrCEx_N", "FrCEx_pi", "FrElas_N", "FrElas_pi", "FrInel_N", "FrPiProd_N", "FrPiProd_pi",
                 "HighQ2", "LowQ2", "MaCCQE", "MaNCEL", "MaRES", "MFP_N", "MFP_pi", "MvRES", "NormDISCC", "NormNCRES",
                 "RDecBR1gamma", "Rvn1pi", "Rvn2pi", "Rvp2pi", "Theta_Delta2Npi", "VecFFCCQEshape")
EXPECT.update({b: 2 for b in MODEL_BANDS_2})


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def require_sha(path: Path, expected: str, what: str) -> None:
    got = sha256(path)
    if got != expected:
        raise SystemExit(f"{what} {path}: sha256 {got} != {expected}")


def load_manifest(path: Path) -> dict[str, str]:
    """``sha256  /absolute/path`` lines (sha256sum format) -> {path: sha256}."""
    out = {}
    for line in path.read_text().splitlines():
        t = line.split(None, 1)
        if len(t) == 2 and len(t[0]) == 64:
            out[t[1].strip()] = t[0]
    return out


def require_listed(path: Path, listed: dict[str, str], what: str) -> None:
    want = listed.get(str(path))
    if want is None:
        raise SystemExit(f"{what} {path} is not in its manifest")
    require_sha(path, want, what)


def xs(path: Path) -> np.ndarray:
    return np.asarray(np.load(path, allow_pickle=False)["xsec_flat"], float)


def fine_map(definition: Path) -> np.ndarray:
    """The 65,856-entry fine-cell -> reporting-cell map (-1 = not reported), checked against both recorded digests."""
    require_sha(definition, DEFINITION_SHA256, "H2 definition")
    expected_map = FINE_MAP_SHA256
    d = json.loads(definition.read_text())
    cmap, n = s1.coarse_map(s1.H2_EDGES)
    m = np.asarray(d["h2_to_reporting_cell"], int)
    if m.size != n or int(d["n_reporting_cells"]) != N_CELLS or sorted(set(m[m >= 0])) != list(range(N_CELLS)):
        raise SystemExit("H2 definition does not map 32 boxes onto R00-R15")
    fm = np.where(cmap >= 0, m[cmap], -1).astype("<i4")
    got = hashlib.sha256(fm.tobytes()).hexdigest()
    if got != expected_map or got != d["fine_map_sha256_int32le"]:
        raise SystemExit(f"fine map sha256 {got} != {expected_map}")
    return fm


def functional_matrix(fm: np.ndarray) -> np.ndarray:
    """Rows R00-R15 over the fine grid: the fine-bin volume where the fine cell belongs to the cell."""
    vol = s1.fine_volume()
    return np.vstack([np.where(fm == c, vol, 0.0) for c in range(N_CELLS)])


def mat_cov(X: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    """MAT MnvVertErrorBand::CalcCovMx: (weighted) mean-centred, normalized by the weight sum (1/N unweighted)."""
    w = np.ones(X.shape[0]) if w is None else np.asarray(w, float)
    mu = (w[:, None] * X).sum(axis=0) / w.sum()
    Z = X - mu
    return (Z.T * w) @ Z / w.sum()


def flux_weights(path: Path) -> np.ndarray:
    """The first 100 ``Flux`` entries of the nu-e + IMD constraint file, in universe order (build_repair.py's rule)."""
    require_sha(path, CONSTRAINT_SHA256, "flux constraint file")
    cons = []
    for line in path.read_text().splitlines():
        t = line.split()
        if len(t) == 3 and t[0] == "Flux":
            cons.append((int(t[1]), float(t[2])))
    w = np.array([v for i, v in sorted(cons) if i < EXPECT[FLUX]])
    if w.size != EXPECT[FLUX] or np.any(w < 0) or w.sum() <= 0:
        raise SystemExit(f"constraint file gives {w.size} usable Flux weights, {EXPECT[FLUX]} needed")
    return w


def pt_index() -> np.ndarray:
    shape = s1.fine_shape()
    return np.unravel_index(np.arange(int(np.prod(shape))), shape)[0]


def x01_scale(path: Path, flux: np.ndarray) -> np.ndarray:
    """The recorded (2, n_pT) MINOS rescale; refuses unless its Phi_CV is the 5D flux bitwise."""
    require_sha(path, X01_SHA256, "X01 factors")
    z = np.load(path, allow_pickle=False)
    if not np.array_equal(np.asarray(z["phi_cv"], float), np.asarray(flux, float)):
        raise SystemExit("X01 factors were made for a different flux than the 5D inputs'")
    scale = np.asarray(z["scale"], float)
    if scale.shape != (2, flux.size):
        raise SystemExit(f"X01 scale shape {scale.shape}")
    return scale


def band_of(path: Path, tag: str) -> tuple[str, int]:
    band, _, idx = path.stem[len(tag) + 1:].rpartition("_")
    return band, int(idx)


def universe_bands(dirs: list[Path], tag: str) -> dict[str, list[Path]]:
    """Group the universe products by band, in universe order, and check the declared set exactly."""
    bands: dict[str, dict[int, Path]] = {}
    for d in dirs:
        for p in sorted(d.glob(f"{tag}_*.npz")):
            if ".partial-" in p.name:
                raise SystemExit(f"an interrupted product is present: {p.name}")
            if p.stem == f"{tag}_CV":
                continue
            band, idx = band_of(p, tag)
            if idx in bands.setdefault(band, {}):
                raise SystemExit(f"two products for {band}:{idx}")
            bands[band][idx] = p
    if DROPPED in bands:
        raise SystemExit(f"{DROPPED} is not a band of this construction (KI 92)")
    got = {b: len(v) for b, v in bands.items()}
    if got != EXPECT:
        missing = sorted(set(EXPECT) - set(got)) + [b for b in EXPECT if b in got and got[b] != EXPECT[b]]
        raise SystemExit(f"universe products differ from the declared set: {missing or sorted(set(got) - set(EXPECT))}")
    for b, v in bands.items():
        if sorted(v) != list(range(EXPECT[b])):
            raise SystemExit(f"{b}: universe indices {sorted(v)}")
    return {b: [v[i] for i in sorted(v)] for b, v in sorted(bands.items())}


def check_meta(path: Path, schema: str, seed: int = 42, inputs: bool = True, expect: dict | None = None) -> dict:
    """The product was made by the declared estimator: config R at 5 iterations, OmniFold capacity None
    (three B0 estimators 100/8 at the seed), Stay-Positive refinement 400/31 at random_state seed + 3."""
    m = json.loads(str(np.load(path, allow_pickle=False)["meta"]))
    est = [(e.get("n_estimators"), e.get("num_leaves"), e.get("random_state")) for e in m.get("estimator_params", [])]
    cp = (m.get("refinement") or {}).get("classifier_params") or {}
    bad = []
    if m.get("schema") != schema:
        bad.append(f"schema {m.get('schema')}")
    if (m.get("config"), m.get("capacity"), m.get("iters"), m.get("estimator_seed")) != ("R", None, 5, seed):
        bad.append(f"config/capacity/iters/seed {(m.get('config'), m.get('capacity'), m.get('iters'), m.get('estimator_seed'))}")
    if est != [(100, 8, seed)] * 3:
        bad.append(f"estimators {est}")
    if (cp.get("n_estimators"), cp.get("num_leaves"), cp.get("random_state")) != (400, 31, seed + 3):
        bad.append(f"refinement {(cp.get('n_estimators'), cp.get('num_leaves'), cp.get('random_state'))}")
    if inputs and (m.get("input_npz_sha256"), m.get("bkg_dump_sha256")) != (INPUT_NPZ_SHA256, BKG_SHA256):
        bad.append("input digests")
    for k, v in (expect or {}).items():
        if m.get(k) != v:
            bad.append(f"{k} {m.get(k)!r} != {v!r}")
    if bad:
        raise SystemExit(f"{path.name}: {'; '.join(bad)}")
    return m


def check_universe(path: Path, band: str, bank_listed: dict[str, str] | None = None,
                   detector_listed: dict[str, str] | None = None) -> dict:
    """check_meta, plus the universe's source: a Flux universe divided by its own flux, a detector band read from
    the detector dump (denom_nd), every other band from the vertical bank (tdw)."""
    m = check_meta(path, "s5p-universe/1")
    keys = set(m.get("bank_weight_sha256") or {})
    want = {"wt", "wr", "bkgw", "denom_nd" if band in DETECTOR_BANDS else "tdw"}
    if keys != want:
        raise SystemExit(f"{path.name}: weight files {sorted(keys)}, expected {sorted(want)}")
    if band == FLUX and not (m.get("flux_universe_file") and "flux_ratio_mean" in (m.get("universe_info") or {})):
        raise SystemExit(f"{path.name}: a Flux universe without its own flux")
    if (m.get("alignment") or {}).get("sentinel_rows") != 2801:
        raise SystemExit(f"{path.name}: alignment evidence missing")
    tag = m.get("universe", "").replace(":", "_")
    for k, sha in (m.get("bank_weight_sha256") or {}).items():
        name = f"{tag}_{k}.npy"
        if band in DETECTOR_BANDS and detector_listed is not None:
            want = detector_listed.get(name)
        elif band not in DETECTOR_BANDS and bank_listed is not None:
            want = bank_listed.get(f"{m.get('bank')}/{name}")
        else:
            continue
        if sha != want:
            raise SystemExit(f"{path.name}: weight file {name} digest {sha} is not the recorded {want}")
    return m


def seed_block(means: np.ndarray) -> np.ndarray:
    """2D's C08: the sample covariance (ddof 1) over seeds of the per-seed replica mean."""
    return np.cov(means, rowvar=False, ddof=1)


def model_abs(f: np.ndarray, C_model: np.ndarray) -> np.ndarray:
    return C_model * np.outer(f, f)


def group_of(block: str) -> str:
    if block.startswith("band:"):
        b = block[5:]
        return "flux" if b == FLUX else ("detector" if b in DETECTOR_BANDS else "interaction")
    return "lateral" if block.startswith("lat:") else block


def summary(f: np.ndarray, blocks: dict, C_e: np.ndarray, C_mabs: np.ndarray, C_total: np.ndarray) -> dict:
    """The readout: per cell, the relative sigma of each component group and of the totals; the spectra."""
    groups: dict[str, np.ndarray] = {}
    for k, v in blocks.items():
        groups[group_of(k)] = groups.get(group_of(k), 0) + v
    rel = {g: (np.sqrt(np.clip(np.diag(C), 0, None)) / f).tolist() for g, C in
           {**groups, "C_e": C_e, "C_model": C_mabs, "C_total": C_total}.items()}
    ev = {n: np.linalg.eigvalsh(C) for n, C in (("C_e", C_e), ("C_total", C_total))}
    return {"cells": [f"R{c:02d}" for c in range(N_CELLS)], "relative_sigma": rel,
            "median_relative_sigma": {g: float(np.median(v)) for g, v in rel.items()},
            "trace_share": {g: float(np.trace(C / np.outer(f, f)) / np.trace(C_total / np.outer(f, f))) for g, C in
                            {**groups, "C_model": C_mabs}.items()},
            "eigen": {n: {"min": float(e.min()), "max": float(e.max()),
                          "rank_rel_1e-12": int(np.sum(e > 1e-12 * e.max()))} for n, e in ev.items()}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--definition", type=Path, required=True, help="nd-unfolding/pv-ladder/readouts/h2_definition.json")
    ap.add_argument("--inputs-npz", type=Path, required=True, help="of_inputs_5d.npz (its flux key only)")
    ap.add_argument("--central", type=Path, required=True, help="the (e) central product data_b-_j-.npz")
    ap.add_argument("--data-dir", type=Path, required=True, help="s5p study N: data_b<b>_j<100+b>.npz")
    ap.add_argument("--seed-dir", type=Path, required=True,
                    help="seed-block products <seed-tag><seed>_b<b>_j<100+b>.npz (s5p_numerics names data products by tag only)")
    ap.add_argument("--seed-tag", required=True)
    ap.add_argument("--universe-dir", type=Path, nargs="+", required=True)
    ap.add_argument("--universe-tag", required=True)
    ap.add_argument("--lateral-dir", type=Path, required=True, help="lat_<band>_<i>_b-_j-.npz")
    ap.add_argument("--x01", type=Path, required=True, help="the 2D repair's minos_rescaled.npz")
    ap.add_argument("--flux-constraint", type=Path, required=True)
    ap.add_argument("--cmodel", type=Path, required=True, help="npz with the fractional 16x16 C_model,5D")
    ap.add_argument("--cmodel-sha256", required=True, help="the digest the C_model builder committed")
    ap.add_argument("--cmodel-key", required=True, help="the fractional matrix's key in the builder's npz")
    ap.add_argument("--cmodel-abs-key", required=True, help="the builder's absolute matrix; diag(f) C diag(f) must reproduce it")
    ap.add_argument("--inventory", type=Path, required=True, help="5d-design stage0/INVENTORY.sha256 (central, set A)")
    ap.add_argument("--manifest", type=Path, required=True, help="sf1 manifest/inputs-sha256.txt (laterals, bank weights)")
    ap.add_argument("--detector-receipt", type=Path, required=True, help="bank_detector/detector-dump.json")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists() or a.out.with_suffix(".json").exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    U = functional_matrix(fine_map(a.definition))
    if sha256(a.inputs_npz) != INPUT_NPZ_SHA256:
        raise SystemExit("of_inputs_5d.npz digest differs")
    flux = np.asarray(np.load(a.inputs_npz, allow_pickle=False)["flux"], float)
    inv, man = load_manifest(a.inventory), load_manifest(a.manifest)
    require_listed(a.detector_receipt, man, "detector-dump receipt")
    det = json.loads(a.detector_receipt.read_text())["files_sha256"]
    require_sha(a.central, CENTRAL_SHA256, "central")
    require_listed(a.central, inv, "central")
    check_meta(a.central, "s5p-numerics/1", expect={"bootstrap_seed": None, "jitter_seed": None})
    f = U @ xs(a.central)
    used = {"central": a.central}

    stat = [a.data_dir / f"data_b{b}_j{100 + b}.npz" for b in STAT_REPLICAS]
    for b, p in zip(STAT_REPLICAS, stat):
        require_listed(p, inv, "bootstrap replica")
        check_meta(p, "s5p-numerics/1", expect={"bootstrap_seed": b, "jitter_seed": 100 + b, "coords": "float64"})
    R = np.array([U @ xs(p) for p in stat])
    blocks = {"stat": np.cov(R, rowvar=False, ddof=1)}

    w = flux_weights(a.flux_constraint)
    for b, ps in universe_bands(a.universe_dir, a.universe_tag).items():
        for p in ps:
            check_universe(p, b, man, det)
            used[p.name] = p
        X = np.array([U @ xs(p) for p in ps])
        blocks[f"band:{b}"] = mat_cov(X, w if b == FLUX else None)

    scale, pti = x01_scale(a.x01, flux), pt_index()
    for b in LATERAL_BANDS:
        ps = [a.lateral_dir / f"lat_{b}_{i}_b-_j-.npz" for i in (0, 1)]
        X = []
        for i, p in enumerate(ps):
            require_listed(p, man, "lateral")
            check_meta(p, "s5p-numerics/1", inputs=False, expect={"bootstrap_seed": None, "jitter_seed": None})
            x = xs(p) * scale[i][pti] if b == MINOS else xs(p)
            X.append(U @ x)
            used[p.name] = p
        blocks[f"lat:{b}"] = mat_cov(np.array(X))

    blocks["normalization"] = np.outer(NORM_FRACTION * f, NORM_FRACTION * f)
    means = []
    for s in SEEDS:
        ps = ([a.data_dir / f"data_b{b}_j{100 + b}.npz" for b in SEED_REPLICAS] if s == 42 else
              [a.seed_dir / f"{a.seed_tag}{s}_b{b}_j{100 + b}.npz" for b in SEED_REPLICAS])
        for b, p in zip(SEED_REPLICAS, ps):
            check_meta(p, "s5p-numerics/1", seed=s, expect={"bootstrap_seed": b, "jitter_seed": 100 + b, "coords": "float64"})
            used[p.name] = p
        means.append(np.mean([U @ xs(p) for p in ps], axis=0))
    blocks["seed"] = seed_block(np.array(means))
    C_e = sum(blocks.values())

    if sha256(a.cmodel) != a.cmodel_sha256:
        raise SystemExit("C_model,5D digest differs from the committed one")
    zc = np.load(a.cmodel, allow_pickle=False)
    C_model = np.asarray(zc[a.cmodel_key], float)
    if C_model.shape != (N_CELLS, N_CELLS) or not np.array_equal(C_model, C_model.T):
        raise SystemExit(f"C_model,5D shape {C_model.shape} or asymmetric")
    C_mabs = model_abs(f, C_model)
    ref = np.asarray(zc[a.cmodel_abs_key], float)
    if ref.shape != C_mabs.shape or not np.allclose(C_mabs, ref, rtol=1e-12, atol=0.0):
        raise SystemExit("diag(f) C_model diag(f) does not reproduce the builder's absolute matrix (f != X_0, or the keys are swapped)")
    C_total = C_e + C_mabs
    for name, C in (("C_e", C_e), ("C_total", C_total)):
        if np.linalg.eigvalsh(C).min() < -1e-12 * np.abs(np.diag(C)).max():
            raise SystemExit(f"{name} is not positive semidefinite")

    out = {"f": f, "U": U.astype(np.float32), "C_e": C_e, "C_model_frac": C_model, "C_model_abs": C_mabs, "C_total": C_total}
    out.update({"C_" + k.replace(":", "_"): v for k, v in blocks.items()})
    meta = {"schema": "s1-assembly/1", "cells": [f"R{c:02d}" for c in range(N_CELLS)],
            "integral": "sum_f xsec_flat_f * vol_f (cm^2/nucleon)", "normalization_fraction": NORM_FRACTION,
            "seeds": list(SEEDS), "stat_replicas": len(stat), "flux_weights": {"sum": float(w.sum()), "n_eff": float(w.sum() ** 2 / (w ** 2).sum())},
            "blocks": sorted(blocks), "not_included": ["inflation D", "C_ML", "bounded envelope h", DROPPED],
            "inputs_sha256": {k: sha256(p) for k, p in sorted(used.items())} | {
                "definition": DEFINITION_SHA256, "x01": X01_SHA256, "constraint": CONSTRAINT_SHA256,
                "cmodel": a.cmodel_sha256, "inputs_npz": INPUT_NPZ_SHA256},
            "code_sha256": {"s1_assemble.py": sha256(Path(__file__).resolve()),
                            "s5p_stage1_inspect.py": sha256(Path(s1.__file__).resolve())}}
    np.savez_compressed(a.out, **out, meta=json.dumps(meta))
    js = a.out.with_suffix(".json")
    js.write_text(json.dumps({"schema": "s1-readout/1", "assembly_sha256": sha256(a.out), "meta": meta,
                              **summary(f, blocks, C_e, C_mabs, C_total)}, indent=1) + "\n")
    print(json.dumps({"wrote": [str(a.out), str(js)], "sha256": sha256(a.out), "blocks": len(blocks)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
