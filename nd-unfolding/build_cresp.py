#!/usr/bin/env python3
"""Assigned uncertainties, C_resp (state/measurement-scoping/assigned-uncertainties/C-RESP-SPEC.md): a
calorimetric hadronic-response block for configuration (e)'s 5D result on the 16 H2 reporting cells R00-R15,
from the existing MP-1 S1 species-response data unfolds, for Stage G's declared sensitivity variant.

* products: the 11 MP-1 S1 unfolds (``mp1s1_<species>_{m1,p1}_b-_j-.npz`` and ``mp1s1_zero_b-_j-.npz``), each
  pinned by its own sha256 and by its two input-dump digests, as `unfold_verify.json` recorded them;
* cells: the H2 definition and functional matrix of ``s1_assemble`` (cell integrals sum_f x_f vol_f);
* per species: S1's lateral convention, MAT mean-centred over the two endpoints (``s1_assemble.py:341``), which
  is the half-span outer product d d^T with d = (x(+1) - x(-1)) / 2, so no CV enters;
* ``C_resp`` sums the four primary species of MP-1's frozen design (proton, meson, em, other). Cross-talk, MP-1's
  variant species, is built and reported beside it but not summed;
* ``C_total_resp = C_total + C_resp`` on S1's assembly, whose U must equal this definition's bitwise.

The zero product enters one descriptive number only: the per-species curvature ratio on R00-R15, in MP-1's G3
form. It gates nothing.

MEASURES: the response blocks on the declared inputs. CANNOT AUTHORIZE: adoption into the reported total,
coverage, any claim.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s1_assemble as sa  # noqa: E402

S1_ASSEMBLY_SHA256 = "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4"
PRIMARY = ("proton", "meson", "em", "other")
VARIANT = ("xtalk",)
SIZES = {"proton": 0.035, "meson": 0.05, "em": 0.03, "other": 0.20, "xtalk": 0.20}   # D1, MP-1 S0-PREP section 1
# variant -> (product sha256, input_npz_sha256, bkg_dump_sha256): mp1/s1-receipts/verify/unfold_verify.json
PRODUCTS = {
    "zero": ("f1d5178a86c1aa417d477d205669b642c66760b7e8e65f98b426e1d9d950d195",
             "6ca02c3d8b09dfd168b5184c03d433a7bd65749f5f6fc4cefecdbed7b6ce052f",
             "f09727d04521f77ba101a51eb77f6182305baaad8a342dc59b7a3d86cf37ea66"),
    "proton_m1": ("bfffb8c54df3895ac1f98113027382418789ed43b59224fe3de8d7bc36419091",
                  "42d2c23bc6832b5cd3506fdf5a5b6cd7ddcbf9c4a901a548bf3daa40dd7598c1",
                  "7df9b35f34daa409bbb5d2873cab13a524e0df3ba05d4dc0f2fd6d7556d76789"),
    "proton_p1": ("8cbe49ae8407aafb2a67ecdcb6829717dfb8cd3ce1c0c8afe5469c9457f01390",
                  "38c382d9ad34b1da181130a088fabd8785efb995eab5ab0317c74a91f274c73a",
                  "1073c6e1cbec9f2c1217bd9262a51e36261df167c7a96f9fa7772598c895ba79"),
    "meson_m1": ("6f3fbb50ec9102fe198d08f323c20ddce420457f5f3c2e5b13ed7f541a652a21",
                 "eb2eaf7ed4fae35a36bc82e05e22b5d1c136e10ccd56493c0b1b3295e3da3ffc",
                 "d661f59d97528066a9b58b04413f4056101308e350a3a6bddae2b8b835b0f080"),
    "meson_p1": ("e54b01c1c44445362dc11d23c725fd957927348a91ad5ab2cda6ab25ba0e257c",
                 "de17924ff9cd548c0b6e461fb4da63fab2af8b5ff95fa7837f21f736537bf123",
                 "d06178f5caa1f1c6ba7cca72dcd0282c851ae65be7e20fda110d7ce337159c38"),
    "em_m1": ("a13521a902c855209e4b7faba3d6e199819a7735e234d8385526d36b56de71d2",
              "dcaf079b43e509bd801ef5e52bf0a13c16fc7c3b7131127612719ed47bc72ff9",
              "c68351c9a093d167896f848d6e69d54e58eee2a9e7e777f71c82dae7dbcf005f"),
    "em_p1": ("15d8d224dba91f9f6ed80324e9bdd99403e1c9207b77c7f616fe70124418883c",
              "d0177f1ccc48f3b92424bbd65886b50d4763016ace030fad23b021471022e911",
              "cffdc91f5e4d6a34f450a7b13032256aec8a17b919fd67d2da89241d9ff23a3d"),
    "other_m1": ("6580cbde395d16bd3a2decf34dc1fd7dc06e7c87f1615af86826217115e4536e",
                 "79586e49d5893ee0bd98c2aaf5f8624205ec3e5ba20513d5869aac3225fa8b92",
                 "5f82d64ef0cf8ac294bf34b5ece3391fc6ece6f25e4fc3e3fc8e5bf3c2abe2c2"),
    "other_p1": ("b30f13fb4ea6813e01664c0c3e21c28f1ef7bb14c6dc79bf4a68e390788d799c",
                 "0cf92c3f7bd07f05a353043b34c98d423db06f304dbe05272b26ea58e471f4fa",
                 "f4305dbe1e43912c1adb8ba0b4381226746c40c652ee14c6bef636a0dd7587b9"),
    "xtalk_m1": ("c3d8134b28728af68a1e2d10cf4a38ca0061fe561a67cdb79b4d5742b446c882",
                 "5cbc1f2c4e4c9ab9877170a2701d16233f43ac5bdd37710c3a6988e49d89fd75",
                 "9b7e6f486e23b28d4fac845cf49e4e495aa1928314d506b1d1552d3ab667c38e"),
    "xtalk_p1": ("6e0abe1572bd6624223259dab92017b316702dbb68782d5a4aac7ebe9a8d8ce8",
                 "268f89651bf7885a99736da37dccc30d1719434f970b8b2ee4d37ea30de26021",
                 "9b410d32dedf723fd6d46fbb942580805387f0cb06712b6b3793a666a5bafe2d"),
}
PSD_TOL = 1e-12
RANK_REL = 1e-12
LABELS = {
    "component": "calorimetric hadronic-response sensitivity (MP-1 species bands, D1 sizes); a declared Stage G "
                 "variant, not an adopted component",
    "not_varied": "neutron and muon energy deposits are not shifted (D1: neutrons out); the response of the "
                  "joint tests' null distributions is not covered (MP1-A-full)",
    "xtalk": "cross-talk is built and reported beside C_resp, not summed (MP-1's variant species; MAT marks it "
             "DO NOT USE)",
    "curvature": "descriptive only: MP-1 read a G3 curvature of this form as estimator discreteness at rounding "
                 "scale (S1-REPORT, input-jitter study); no gate",
}


def product_path(d: Path, variant: str) -> Path:
    return d / f"mp1s1_{variant}_b-_j-.npz"


def load_product(path: Path, variant: str) -> np.ndarray:
    """The product's xsec_flat, after its own digest, its input-dump digests and the estimator checks."""
    sha, npz_sha, bkg_sha = PRODUCTS[variant]
    if not path.is_file():
        raise SystemExit(f"{variant}: {path} is missing")
    sa.require_sha(path, sha, variant)
    sa.check_meta(path, "s5p-numerics/1", inputs=False,
                  expect={"input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha, "construction": "data",
                          "truth": "nominal", "bootstrap_seed": None, "jitter_seed": None, "coords": "float32"})
    x = sa.xs(path)
    if x.shape != (int(np.prod(sa.s1.fine_shape())),) or not np.all(np.isfinite(x)):
        raise SystemExit(f"{variant}: xsec_flat shape {x.shape} or non-finite entries")
    return x


def species_block(lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """S1's lateral block on the two endpoints (index 0 = -1 sigma, 1 = +1 sigma), checked against d d^T."""
    C = sa.mat_cov(np.array([lo, hi]))
    d = (hi - lo) / 2.0
    if not np.allclose(C, np.outer(d, d), rtol=1e-12, atol=0.0):
        raise SystemExit("the mean-centred two-endpoint block is not the half-span outer product")
    return C


def rank(C: np.ndarray) -> int:
    e = np.linalg.eigvalsh(C)
    return int(np.sum(e > RANK_REL * max(e.max(), 0.0))) if e.max() > 0 else 0


def require_psd(C: np.ndarray, name: str) -> None:
    if np.abs(C - C.T).max() > PSD_TOL * np.abs(C).max():
        raise SystemExit(f"{name} is not symmetric")
    if np.linalg.eigvalsh(C).min() < -PSD_TOL * np.abs(np.diag(C)).max():
        raise SystemExit(f"{name} is not positive semidefinite")


def curvature_ratio(lo: np.ndarray, zero: np.ndarray, hi: np.ndarray) -> float:
    """MP-1's G3 form on the reporting cells: ||f(+1) + f(-1) - 2 f(0)|| / ||f(+1) - f(-1)||."""
    span = np.linalg.norm(hi - lo)
    return float(np.linalg.norm(hi + lo - 2.0 * zero) / span) if span > 0 else float("inf")


def load_s1(path: Path, U: np.ndarray) -> dict[str, np.ndarray]:
    sa.require_sha(path, S1_ASSEMBLY_SHA256, "S1 assembly")
    z = np.load(path, allow_pickle=False)
    s = {k: np.asarray(z[k]) for k in ("f", "U", "C_e", "C_model_abs", "C_total")}
    if not np.array_equal(s["U"], U.astype(np.float32)):
        raise SystemExit("the S1 assembly's U is not this definition's functional matrix")
    if not np.array_equal(s["C_total"], s["C_e"] + s["C_model_abs"]):
        raise SystemExit("the S1 assembly's C_total is not C_e + C_model_abs")
    if s["f"].shape != (sa.N_CELLS,) or not np.all(s["f"] > 0):
        raise SystemExit("the S1 assembly's f is not 16 positive cell integrals")
    return s


def readout(f: np.ndarray, blocks: dict[str, np.ndarray], C_resp: np.ndarray, s1: dict, C_tr: np.ndarray,
            curv: dict[str, float]) -> dict:
    """Relative quantities only: per cell sigma/f of each block and total, trace shares, spectra and ranks."""
    def rel(C):
        return (np.sqrt(np.clip(np.diag(C), 0, None)) / f).tolist()
    mats = {**{f"C_resp_{s}": C for s, C in blocks.items()}, "C_resp": C_resp, "C_total": s1["C_total"],
            "C_total_resp": C_tr}
    ff = np.outer(f, f)
    return {"cells": [f"R{c:02d}" for c in range(sa.N_CELLS)],
            "relative_sigma": {n: rel(C) for n, C in mats.items()},
            "median_relative_sigma": {n: float(np.median(rel(C))) for n, C in mats.items()},
            "trace_share_of_C_total_resp": {n: float(np.trace(C / ff) / np.trace(C_tr / ff))
                                            for n, C in {**{f"C_resp_{s}": blocks[s] for s in PRIMARY},
                                                         "C_total": s1["C_total"]}.items()},
            "eigen": {n: {"min": float(np.linalg.eigvalsh(C).min()), "max": float(np.linalg.eigvalsh(C).max()),
                          "rank_rel_1e-12": rank(C)} for n, C in mats.items()},
            "curvature_ratio_descriptive": curv}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--definition", type=Path, required=True, help="nd-unfolding/pv-ladder/readouts/h2_definition.json")
    ap.add_argument("--products-dir", type=Path, required=True, help="MP-1 S1 unfolds, mp1s1_<variant>_b-_j-.npz")
    ap.add_argument("--s1-assembly", type=Path, required=True, help="S1's s1_assembly.npz (db000707...)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists() or a.out.with_suffix(".json").exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    U = sa.functional_matrix(sa.fine_map(a.definition))
    s1 = load_s1(a.s1_assembly, U)
    cells = {v: U @ load_product(product_path(a.products_dir, v), v) for v in PRODUCTS}

    blocks, curv = {}, {}
    for s in PRIMARY + VARIANT:
        lo, hi = cells[f"{s}_m1"], cells[f"{s}_p1"]
        blocks[s] = species_block(lo, hi)
        if rank(blocks[s]) > 1:
            raise SystemExit(f"{s}: a two-endpoint block of rank {rank(blocks[s])}")
        curv[s] = curvature_ratio(lo, cells["zero"], hi)
    C_resp = sum(blocks[s] for s in PRIMARY)
    C_tr = s1["C_total"] + C_resp
    for name, C in (("C_resp", C_resp), ("C_total_resp", C_tr)):
        require_psd(C, name)
    if rank(C_resp) > len(PRIMARY):
        raise SystemExit(f"C_resp rank {rank(C_resp)} > {len(PRIMARY)}")
    if rank(C_tr) != sa.N_CELLS:
        raise SystemExit(f"C_total_resp rank {rank(C_tr)} != {sa.N_CELLS}")

    out = {"C_resp": C_resp, "C_total_resp": C_tr, **{f"C_resp_{s}": C for s, C in blocks.items()}}
    meta = {"schema": "cresp-assembly/1", "cells": [f"R{c:02d}" for c in range(sa.N_CELLS)],
            "integral": "sum_f xsec_flat_f * vol_f (cm^2/nucleon)", "primary": list(PRIMARY),
            "variant": list(VARIANT), "sizes": SIZES, "labels": LABELS,
            "inputs_sha256": {**{v: PRODUCTS[v][0] for v in PRODUCTS}, "s1_assembly": S1_ASSEMBLY_SHA256,
                              "definition": sa.DEFINITION_SHA256},
            "code_sha256": {"build_cresp.py": sa.sha256(Path(__file__).resolve()),
                            "s1_assemble.py": sa.sha256(Path(sa.__file__).resolve()),
                            "s5p_stage1_inspect.py": sa.sha256(Path(sa.s1.__file__).resolve())}}
    np.savez_compressed(a.out, **out, meta=json.dumps(meta))
    js = a.out.with_suffix(".json")
    js.write_text(json.dumps({"schema": "cresp-readout/1", "assembly_sha256": sa.sha256(a.out), "meta": meta,
                              **readout(s1["f"], blocks, C_resp, s1, C_tr, curv)}, indent=1) + "\n")
    print(json.dumps({"wrote": [str(a.out), str(js)], "sha256": sa.sha256(a.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
