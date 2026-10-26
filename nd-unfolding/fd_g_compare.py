#!/usr/bin/env python3
"""5D Stage G (state/measurement-paper/5d-community-20261024/FD-G-DECLARATION.md): compare configuration (e)'s data
result on the 16 H2 reporting cells R00-R15 with the five generator predictions, as FD-PLAN section 4 declares and
FD-DIRECTOR-RULINGS.md section 5 rules; approved by Joseph in DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-
scope.md item 2.

On the cells c of a comparison, with X = sum_f x_f vol_f (S1's integration rule):

    d = f - g,   V_g = diag(sum_f sumw2_f vol_f^2),   M = C_total + V_g,
    total:       chi2 = d^T M^-1 d,                                       ndf = n
    shape-only:  chi2 = d^T (M + 100 f f^T)^-1 d,                          ndf = n - 1
    pulls:       z_c = d_c / sqrt(M_cc)

f and C_total are S1's (s1_assembly.npz); C_total includes all three C_model,5D vertices for every comparison (route
item 3; no leave-out applies). The shape-only mode is Stage 0's: a free normalization of variance 100 in units
relative to f (STAGE0-PARTA-DECLARATION.md section 6), i.e. 100 * 11^T on the relative scale. GiBUU is compared on
the eight p_parallel < 4.5 cells only (ndf 8, shape-only 7): its prediction is integrated on those cells alone, so no
GiBUU value on R04-R07 or R12-R15 is formed, printed or written, and no 16-cell GiBUU chi2 exists. Every chi2 is
written beside the name of the matrix it used, its size and its numerical rank.

Controls G0-G4 run first and each refuses (exit 1, nothing written).

MEASURES: arithmetic on the declared inputs. CANNOT AUTHORIZE: any reading of the comparison, a claim, or paper text.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import zipfile
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s1_assemble as sa  # noqa: E402  (sha256, fine_map, functional_matrix, load_manifest; sa.s1 = s5p_stage1_inspect)

N_FINE, N_CELLS = 65856, 16
SHAPE_LAMBDA = 1.0e2                       # Stage 0's free-normalization variance, relative units
TOL = 1e-12
GIBUU_CELLS = (0, 1, 2, 3, 8, 9, 10, 11)   # p_parallel < 4.5; checked against the definition (G3)
PINS = {
    "s1_npz": "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4",
    "s1_json": "81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21",
    "cmodel_json": "3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60",
    "s5p_sums": "1a72cb439120d910ee509fa0be7915924eb36b6a42fda8bda8006a0a92609935",
}
# The five predictions (FD-PLAN section 4): path under the s5p root, file sha256 (also in the s5p archive SHA256SUMS),
# the meta field that names it, the cells it is compared on, and the labels the readout carries.
PREDICTIONS = (
    dict(name="genie_cv", path="gen5d_fluxfix/genie_cv_xsec5d_full.npz",
         sha256="cfa42210dfe9cadc8e9460333316a639bd719c9ae52ab1144be900372a9adcc2",
         meta=("generator", "genie_cv"), cells="all", label="GENIE 2.12.10 CV, no MEC; CH"),
    dict(name="genie_mec", path="gen5d_fluxfix/genie_mec_xsec5d_full.npz",
         sha256="c179855df6e42a5b8bab1f839aae675c53a5150f132649c855356ad75f26790f",
         meta=("generator", "genie_mec"), cells="all", label="GENIE 2.12.10 + Valencia MEC; CH"),
    dict(name="nuwro", path="gen5d_fluxfix/nuwro_cv_xsec5d_full.npz",
         sha256="475a2871304db23efedbd5ab42a32d91c7f1d295b6dd0c907c46aa6d81c48070",
         meta=("generator", "nuwro_cv"), cells="all", label="NuWro 21.09; C12, not CH"),
    dict(name="gibuu", path="gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz",
         sha256="48917692ee1295902db3bec34d6c80e368f020ae7924dabbda7e996c461cca18",
         meta=("generator", "gibuu_cv"), cells="gibuu",
         label="GiBUU 2019; C12, not CH; no events above E_nu = 20 GeV (KNOWN_ISSUES 82), so it is compared on the "
               "eight p_parallel < 4.5 cells only and not shown above p_parallel 4.5 (FD-DIRECTOR-RULINGS.md section 5)"),
    dict(name="mnvtune_v1", path="gen5d/mnvtune_v1_xsec5d.npz",
         sha256="bf7bd27873427d4b1ff9864403b895529931f113440acec3daa28479f958466c",
         meta=("schema", "s5p-mc-truth-pred/1"), cells="all",
         label="MINERvA Tune v1, the analysis MC truth: the unfolding prior, not an independent generator"),
)
COVARIANCE_LABEL = ("C_total = C_e + C_model_abs from S1, with all three C_model,5D vertices (GENIE+MEC, NuWro, "
                    "GiBUU) for every comparison; the NuWro, GENIE+MEC and GiBUU vertices are data shifts built from "
                    "those generators' shapes")


class Stop(SystemExit):
    """A control refused: exit 1, nothing written."""

    def __init__(self, control, why):
        super().__init__(f"FAIL control {control}: {why}")


def report(control, name, ok, why="differs"):
    print(f"{'PASS' if ok else 'FAIL'} control {control} {name}{'' if ok else ': ' + why}", flush=True)
    if not ok:
        raise Stop(control, f"{name}: {why}")


def sa_call(control, fn, *args):
    try:
        return fn(*args)
    except Stop:
        raise
    except SystemExit as e:
        raise Stop(control, str(e.code)) from None


# ---------------------------------------------------------------- statistics


def chi2_sf(x: float, ndf: int) -> float:
    """P(chi2_ndf > x), exactly, for any positive integer ndf.
    Even ndf: exp(-x/2) sum_{i < ndf/2} (x/2)^i / i!.
    Odd ndf:  erfc(sqrt(x/2)) + sqrt(2x/pi) exp(-x/2) sum_{i=1}^{(ndf-1)/2} x^(i-1) / (1 * 3 * ... * (2i - 1))."""
    if ndf <= 0 or int(ndf) != ndf:
        raise ValueError("ndf must be a positive integer")
    if x <= 0:
        return 1.0
    if ndf % 2 == 0:
        h, term, total = x / 2.0, 1.0, 1.0
        for i in range(1, ndf // 2):
            term *= h / i
            total += term
        return float(math.exp(-h) * total) if h < 745 else 0.0
    out = math.erfc(math.sqrt(x / 2.0))
    if ndf > 1 and x / 2.0 < 745:
        term, total = 1.0, 1.0
        for i in range(2, (ndf - 1) // 2 + 1):
            term *= x / (2 * i - 1)
            total += term
        out += math.sqrt(2.0 * x / math.pi) * math.exp(-x / 2.0) * total
    return float(out)


def rank(M: np.ndarray) -> int:
    ev = np.linalg.eigvalsh(M)
    return int(np.sum(ev > TOL * ev.max()))


def compare(f: np.ndarray, g: np.ndarray, Vg: np.ndarray, Ct: np.ndarray, cells: list[int], C_name: str) -> dict:
    """Total and shape-only chi2 and pulls of f against g on ``cells``."""
    idx = np.asarray(cells)
    d = (f - g)[idx]
    M = Ct[np.ix_(idx, idx)] + np.diag(Vg[idx])
    fs = f[idx]
    Ms = M + SHAPE_LAMBDA * np.outer(fs, fs)
    n = len(idx)
    out = {"cells": [f"R{c:02d}" for c in idx], "n_cells": n}
    for key, mat, ndf, name in (("total", M, n, f"{C_name} + V_g"),
                                ("shape_only", Ms, n - 1, f"{C_name} + V_g + 100 f f^T (free normalization)")):
        L = np.linalg.cholesky(mat)
        y = np.linalg.solve(L, d)
        chi2 = float(y @ y)
        out[key] = {"chi2": chi2, "ndf": ndf, "p": chi2_sf(chi2, ndf), "matrix": name,
                    "matrix_size": [n, n], "matrix_rank": rank(mat)}
    z = d / np.sqrt(np.diag(M))
    out["pulls"] = z.tolist()
    out["cells_abs_pull_gt_2"] = [f"R{c:02d}" for c, v in zip(idx, z) if abs(v) > 2]
    out["f"] = fs.tolist()
    out["g"] = g[idx].tolist()
    out["f_minus_g"] = d.tolist()
    out["g_over_f_minus_1"] = (g[idx] / fs - 1).tolist()
    out["sigma_total_over_f"] = (np.sqrt(np.diag(Ct)[idx]) / fs).tolist()
    out["sigma_Vg_over_f"] = (np.sqrt(Vg[idx]) / fs).tolist()
    return out


# ---------------------------------------------------------------- inputs


def npz_headers(path: Path) -> dict:
    """{member: (shape, dtype)} from the .npy headers alone."""
    out = {}
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            with zf.open(name) as fh:
                version = np.lib.format.read_magic(fh)
                reader = np.lib.format.read_array_header_1_0 if version == (1, 0) else np.lib.format.read_array_header_2_0
                shape, _, dtype = reader(fh)
            out[name[:-4] if name.endswith(".npy") else name] = (shape, dtype)
    return out


def prediction_problems(path: Path, spec: dict) -> list[str]:
    bad = []
    h = npz_headers(path)
    for k in ("xsec_flat", "sumw2_flat", "nevt_flat"):
        if h.get(k) != ((N_FINE,), np.dtype("<f8")):
            bad.append(f"{k} {h.get(k)}")
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z["meta_json"])) if "meta_json" in z.files else {}
        for a in sa.s1.AXES:
            key = f"edges_{a}"
            if key not in z.files or not np.array_equal(np.asarray(z[key], float), np.asarray(sa.s1.FINE[a], float)):
                bad.append(f"{key} differs from the fine grid")
        if bad:
            return bad
        x, s2 = np.asarray(z["xsec_flat"], float), np.asarray(z["sumw2_flat"], float)
    field, want = spec["meta"]
    if meta.get(field) != want:
        bad.append(f"meta {field} {meta.get(field)!r} != {want!r}")
    if not (np.all(np.isfinite(x)) and np.all(np.isfinite(s2))):
        bad.append("non-finite entries")
    if np.any(s2 < 0):
        bad.append("negative sumw2")
    return bad


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--definition", type=Path, required=True, help="nd-unfolding/pv-ladder/readouts/h2_definition.json")
    ap.add_argument("--s1-npz", type=Path, required=True, help="s1-20261024/s1_assembly.npz")
    ap.add_argument("--s1-json", type=Path, required=True, help="the committed s1/readout/s1_assembly.json")
    ap.add_argument("--cmodel-json", type=Path, required=True, help="nd-unfolding/pv-ladder/readouts/cmodel_5d.json")
    ap.add_argument("--s5p-sums", type=Path, required=True, help="state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt")
    ap.add_argument("--s5p-root", type=Path, required=True, help="s5p-20260926 (the predictions' root)")
    ap.add_argument("--out-json", type=Path, required=True)
    return ap.parse_args(argv)


def run(a, pins=None, predictions=None) -> int:
    pins = PINS if pins is None else pins
    predictions = PREDICTIONS if predictions is None else predictions
    if a.out_json.exists():
        raise Stop("-", f"refusing to overwrite {a.out_json}")

    # G0. digests: the records, the S1 assembly, the definition and fine map, and each prediction against both its
    # pinned digest and the s5p archive manifest
    for key, path in (("s1_json", a.s1_json), ("cmodel_json", a.cmodel_json), ("s5p_sums", a.s5p_sums),
                      ("s1_npz", a.s1_npz)):
        got = sa.sha256(path)
        if got != pins[key]:
            raise Stop("G0", f"{key} {path}: sha256 {got} != {pins[key]}")
    s1j, cj = json.loads(a.s1_json.read_text()), json.loads(a.cmodel_json.read_text())
    if s1j.get("assembly_sha256") != pins["s1_npz"]:
        raise Stop("G0", "the committed S1 readout names another assembly")
    U = sa.functional_matrix(sa_call("G0", sa.fine_map, a.definition))
    sums = sa.load_manifest(a.s5p_sums)
    for spec in predictions:
        path = a.s5p_root / spec["path"]
        got = sa.sha256(path)
        if got != spec["sha256"] or sums.get(spec["path"]) != spec["sha256"]:
            raise Stop("G0", f"{spec['name']} {path}: sha256 {got}, pinned {spec['sha256']}, manifest "
                             f"{sums.get(spec['path'])}")
    report("G0", f"S1 assembly, definition, 3 records and {len(predictions)} predictions match their digests", True)

    # G1. each prediction's structure
    for spec in predictions:
        bad = prediction_problems(a.s5p_root / spec["path"], spec)
        if bad:
            raise Stop("G1", f"{spec['name']}: {'; '.join(bad)}")
    report("G1", "every prediction carries xsec, sumw2 and nevt on the fine grid, finite, sumw2 >= 0, as named", True)

    # G2. S1's f and C_total
    with np.load(a.s1_npz, allow_pickle=False) as z:
        f = np.asarray(z["f"], float)
        Ce, Ct, Cma = (np.asarray(z[k], float) for k in ("C_e", "C_total", "C_model_abs"))
        U32 = np.asarray(z["U"])
    scale = np.abs(np.diag(Ct)).max()
    checks = {
        "U is S1's float32 functional matrix": np.array_equal(U32, U.astype(np.float32)),
        "f is positive on every cell": bool(f.shape == (N_CELLS,) and np.all(f > 0)),
        "f is cmodel_5d.json's x, P5's integrals (to 1e-12)": np.allclose(f, np.asarray(cj["x"], float), rtol=TOL, atol=0),
        "C_total = C_e + C_model_abs": np.allclose(Ce + Cma, Ct, rtol=TOL, atol=TOL * scale),
        "C_total's relative sigma is the committed one": np.allclose(
            np.sqrt(np.diag(Ct)) / f, np.asarray(s1j["relative_sigma"]["C_total"], float), rtol=TOL, atol=0),
        "C_total is positive definite, rank 16": bool(np.linalg.eigvalsh(Ct / np.outer(f, f)).min() > 0
                                                       and rank(Ct / np.outer(f, f)) == N_CELLS),
    }
    for name, ok in checks.items():
        report("G2", name, bool(ok))

    # G3. GiBUU's cells are the p_parallel < 4.5 boxes
    defn = json.loads(a.definition.read_text())
    lo = sorted(c["id"] for c in defn["reporting_cells"] if c["box"]["pz"][1] <= 4.5)
    report("G3", "GiBUU's eight cells are the p_parallel < 4.5 boxes", lo == list(GIBUU_CELLS), f"they are {lo}")

    # G4. integrate each prediction on its own cells only; positive integrals, non-negative V_g
    results = []
    for spec in predictions:
        cells = list(range(N_CELLS)) if spec["cells"] == "all" else list(GIBUU_CELLS)
        Ucells = U[cells]
        with np.load(a.s5p_root / spec["path"], allow_pickle=False) as z:
            x, s2, nev = (np.asarray(z[k], float) for k in ("xsec_flat", "sumw2_flat", "nevt_flat"))
        g, Vg, nevt = np.zeros(N_CELLS), np.zeros(N_CELLS), np.zeros(N_CELLS)
        g[cells] = Ucells @ x
        Vg[cells] = (Ucells ** 2) @ s2          # sum_f sumw2_f vol_f^2: a row of U holds vol_f on the cell's fine cells
        nevt[cells] = (Ucells != 0).astype(float) @ nev
        if not (np.all(g[cells] > 0) and np.all(Vg[cells] >= 0)):
            raise Stop("G4", f"{spec['name']}: a cell integral is not positive or V_g is negative")
        rec = {"name": spec["name"], "file": spec["path"], "sha256": spec["sha256"], "label": spec["label"],
               "n_mc_events_in_cells": nevt[cells].tolist(), **compare(f, g, Vg, Ct, cells, "C_total")}
        results.append(rec)
    report("G4", "every prediction's integrals are positive on its cells", True)

    readout = {
        "schema": "fd-g-readout/1",
        "labels": {"what": "configuration (e)'s data result on R00-R15 against five generator predictions",
                   "covariance": COVARIANCE_LABEL,
                   "shape_only": "a free normalization of variance 100 relative to f (Stage 0's mode), ndf n - 1",
                   "gibuu": "GiBUU on the eight p_parallel < 4.5 cells only; no GiBUU value above p_parallel 4.5 is "
                            "formed or shown, and no 16-cell GiBUU chi2 is computed",
                   "not": "no reading, claim or paper text (FD-PLAN section 4; DECISION-20261025 item 2)"},
        "cells": [f"R{c:02d}" for c in range(N_CELLS)],
        "controls_passed": ["G0", "G1", "G2", "G3", "G4"],
        "predictions": results,
        "inputs_sha256": {**pins, "definition": sa.DEFINITION_SHA256,
                          **{p["name"]: p["sha256"] for p in predictions}},
        "code_sha256": {"fd_g_compare.py": sa.sha256(Path(__file__).resolve()),
                        "s1_assemble.py": sa.sha256(Path(sa.__file__).resolve()),
                        "s5p_stage1_inspect.py": sa.sha256(Path(sa.s1.__file__).resolve())},
        "argv": [str(x) for x in sys.argv],
    }
    tmp = a.out_json.with_name(a.out_json.name + ".partial")
    tmp.write_text(json.dumps(readout, indent=1) + "\n")
    os.replace(tmp, a.out_json)
    for r in results:
        t, s = r["total"], r["shape_only"]
        print(f"[G] {r['name']:10s} {r['n_cells']:2d} cells: total chi2 {t['chi2']:.2f}/{t['ndf']} p {t['p']:.3g} "
              f"[{t['matrix']}, {t['matrix_size'][0]}x{t['matrix_size'][1]}, rank {t['matrix_rank']}]; "
              f"shape-only chi2 {s['chi2']:.2f}/{s['ndf']} p {s['p']:.3g} [rank {s['matrix_rank']}]", flush=True)
    print(json.dumps({"wrote": str(a.out_json), "sha256": sa.sha256(a.out_json)}), flush=True)
    return 0


def main(argv=None) -> int:
    return run(build_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
