#!/usr/bin/env python3
"""Assemble the F2 candidate covariance with the adopted design's own algebra and gates.

    C_F2 = D (sum_V C_b) D + sum_R C_b + sum_A L_b + C_stat + C_ML          (z_assembly.assemble)

Every block is built from the campaign's F2 arm products with the SAME formula the adopted chain
used (traced 2026-09-25, contract amendment 1):

* V and R sweep bands, R detector bands: ``uq_math.mat_covariance`` of the band's universes on the
  support rows (universe-mean centred, 1/N; the CV cancels), as ``analyze_universes_5d.py`` does;
  ``__Normalization_flat`` = outer(0.014 x_cv) as it does.
* A (selection-complete lateral) bands: ``uq_math.mat_covariance`` of the two endpoints
  (``p4_build_components.build_active_bands``).
* C_stat, C_ML: replica-mean centred, 1/(N-1) (``combine_cov_nd.py``).
* g from the F2 unified-throw product via ``z_assembly.derive_variant_diagonals`` and
  ``compute_g`` for the declared centring variant ``cv`` (z_build.py's route).
* Band partition from ``z_contract`` (V = VERT_BANDS, A = LATERAL_BANDS, R = inventory - V - A,
  checked against the declared 27).

The support is the F2 central value's positive cells; every arm is read on those rows and the
throw product's own support must be identical. Gates: z_assembly's inflation gates and
symmetry/PSD, reported, never waived. The product carries the adopted product's keys so the
production projector and the campaign's readers consume it unchanged.

MEASURES: the F2 candidate's covariance construction. CANNOT AUTHORIZE: coverage (Tier S tests the
statistical component only), adoption, or any comparison with the adopted trunk as a grade.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from pathlib import Path

import numpy as np

import uq_math
import z_assembly as assembly
import z_contract as contract

NORM_FRAC = 0.014


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def read_flat(path: str, key: str = "hXSecND_flat") -> np.ndarray:
    if path.endswith(".npz"):
        return np.asarray(np.load(path, allow_pickle=False)["xsec_flat"], float)
    import ROOT

    f = ROOT.TFile.Open(path, "READ")
    h = f.Get(key)
    if not h:
        raise SystemExit(f"{path}: no {key}")
    n = h.GetNbinsX()
    out = np.array([h.GetBinContent(i + 1) for i in range(n)], float)
    f.Close()
    return out


def read_th2(f, key: str, n: int) -> np.ndarray:
    h = f.Get(key)
    if not h or h.GetNbinsX() != n:
        raise SystemExit(f"throw product: {key} missing or not {n}x{n}")
    buf = np.frombuffer(h.GetArray(), dtype=np.float64, count=(n + 2) * (n + 2)).reshape(n + 2, n + 2)
    return np.array(buf[1:-1, 1:-1].T)  # ROOT stores x fastest: element (ix, iy) at iy*(n+2)+ix


def band_cov(files: list[str], rows: np.ndarray) -> np.ndarray:
    X = np.array([read_flat(p)[rows] for p in files])
    return uq_math.mat_covariance(X)


def replica_cov(files: list[str], rows: np.ndarray) -> np.ndarray:
    X = np.array([read_flat(p)[rows] for p in files])
    Z = X - X.mean(0)
    return Z.T @ Z / (X.shape[0] - 1)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--central", required=True)
    ap.add_argument("--sweep-dir", required=True)
    ap.add_argument("--det-dir", required=True)
    ap.add_argument("--lat-dir", required=True)
    ap.add_argument("--boot-dir", required=True)
    ap.add_argument("--split-dir", required=True)
    ap.add_argument("--throw-root", required=True)
    ap.add_argument("--vlist", required=True, help="uq_4d/vertical_run_bkgaware.txt")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")

    x_cv = read_flat(a.central)
    rows = np.flatnonzero(x_cv > 0)
    n = rows.size
    universes: dict[str, list[str]] = {}
    for line in Path(a.vlist).read_text().split():
        band, idx = line.split(":")
        universes.setdefault(band, []).append(f"{a.sweep_dir}/5d_xsec_MEFHC_5iter_lgbm_uni_full_{band}_{idx}.root")
    for band in ("MinosEfficiency", "GEANT_Neutron", "GEANT_Pion", "GEANT_Proton"):
        universes[band] = [f"{a.det_dir}/5d_det_{band}_{i}.root" for i in (0, 1)]
    inventory = sorted([*universes, "__Normalization_flat"])
    residual = tuple(sorted(set(inventory) - set(contract.VERT_BANDS) - set(contract.LATERAL_BANDS)))
    contract.check_band_partition(contract.VERT_BANDS, residual, contract.LATERAL_BANDS,
                                  sorted([*inventory, *contract.LATERAL_BANDS]))
    contract.check_declared_residual(residual)
    missing = [p for fs in universes.values() for p in fs if not Path(p).exists()]
    if missing:
        raise SystemExit(f"missing {len(missing)} universe products, e.g. {missing[:3]}")

    # Accumulate: 45 band matrices of n x n doubles would not fit in memory together.
    vert_sum = np.zeros((n, n)); resid_sum = np.zeros((n, n)); lat_sum = np.zeros((n, n))
    band_trace = {}
    for b, fs in universes.items():
        cb = band_cov(fs, rows)
        band_trace[b] = float(np.trace(cb))
        (vert_sum if b in contract.VERT_BANDS else resid_sum)[...] += cb
        del cb
    cn = np.outer(NORM_FRAC * x_cv[rows], NORM_FRAC * x_cv[rows])
    band_trace["__Normalization_flat"] = float(np.trace(cn))
    resid_sum += cn
    del cn
    for b in contract.LATERAL_BANDS:
        lb = band_cov([f"{a.lat_dir}/5d_lat_{b}_{e}.root" for e in (0, 1)], rows)
        band_trace[b] = float(np.trace(lb))
        lat_sum += lb
        del lb
    boots = sorted(glob.glob(f"{a.boot_dir}/res_boot_*.npz"))
    splits = sorted(glob.glob(f"{a.split_dir}/res_split_*.npz"))
    if len(boots) != 100 or len(splits) != 24:
        raise SystemExit(f"expected 100 bootstrap and 24 split replicas, found {len(boots)} and {len(splits)}")
    parts = {
        "cov_vert_sum": vert_sum,
        "cov_residual_sum": resid_sum,
        "cov_lateral_sum": lat_sum,
        "cov_stat": replica_cov(boots, rows),
        "cov_ml": replica_cov(splits, rows),
    }

    import ROOT

    tf = ROOT.TFile.Open(a.throw_root, "READ")
    mask_h = tf.Get("hCvSupportMask")
    throw_mask = np.array([mask_h.GetBinContent(i + 1) for i in range(mask_h.GetNbinsX())]) > 0
    if not np.array_equal(np.flatnonzero(throw_mask), rows):
        raise SystemExit("throw product support differs from the F2 central value's support")
    ms_h = tf.Get("hJointMeanShift")
    raw = {"diag_c_unified_mean": np.diag(read_th2(tf, "C_unified", n)).copy(),
           "diag_c_blocksum": np.diag(read_th2(tf, "C_blocksum", n)).copy(),
           "joint_mean_shift": np.array([ms_h.GetBinContent(i + 1) for i in range(n)], float)}
    tf.Close()
    operands = assembly.derive_variant_diagonals(**raw)
    g, pinned = assembly.compute_g(operands["v_uni_cv"], operands["v_blk"])
    C = assembly.assemble(g, **parts)
    gates = {"symmetry_psd": assembly.gate_symmetry_psd(C),
             "g_domain": assembly.gate_g_domain(g, pinned, operands["v_blk"]),
             "closure_identity": assembly.gate_closure_identity(C, g, **parts)}
    meta = {"schema": "s5c-f2-covariance/1", "variant": "cv", "candidate": "F2",
            "adoptable": False, "scientific_acceptance": "UNGRADED",
            "sources": {"central": a.central, "central_sha256": sha256_path(Path(a.central)),
                        "throw_root": a.throw_root, "throw_sha256": sha256_path(Path(a.throw_root))},
            "bands": {"vert": list(contract.VERT_BANDS), "residual": list(residual), "lateral": list(contract.LATERAL_BANDS)},
            "n_support": int(n), "gates": gates, "band_trace": band_trace,
            "sqrt_tr": {k: float(np.sqrt(np.trace(v))) for k, v in {**parts, "total": C}.items()}}
    tmp = a.out.with_name(a.out.name + ".partial.npz")
    np.savez(tmp, hCov_combined5d_total_uthrow=C, hXSecND_flat=x_cv, hRowIndex5D=rows,
             hSupportMask=(x_cv > 0).astype(np.int8), hPinnedMask=pinned.astype(np.int8), hInflation_g=g,
             metadata_json=json.dumps(meta, default=str))
    tmp.replace(a.out)
    print(json.dumps({"n_support": n, "sqrt_tr": meta["sqrt_tr"], "gates": gates}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
