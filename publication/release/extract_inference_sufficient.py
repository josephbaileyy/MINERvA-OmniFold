#!/usr/bin/env python3
"""Extract the sufficient inputs of the s5p joint tests into one portable npz plus a JSON manifest.

The frozen evaluator (``nd-unfolding/s5p_joint.py evaluate``) reads ~7,000 cluster products. Every number it
reports is a function of, per null: the per-experiment J-cell vectors F (after the declared lateral,
normalization and numerical terms, i.e. ``s5p_joint.ensemble``), their pseudo seeds, the prediction mu and its
MC variance, the test domain, the variant shift vectors, and globally the frozen metric V, the observed data
vector and the 20 data rounding jitters. This script computes those arrays WITH THE FROZEN CODE of a named deploy
and writes them, so that ``replay_inference.py`` (standalone, numpy/scipy only) can reproduce every p-value and
decision without the products.

It imports ``s5p_joint`` from ``<deploy>/nd-unfolding`` and refuses to run if the import resolves anywhere else
(OI-136). It reads products, writes only ``--out`` and ``--out``.manifest.json, and refuses to overwrite.

MEASURES: nothing new; it re-expresses frozen inputs. CANNOT AUTHORIZE: any decision, resolution or claim.

Usage (login node, from any directory):
    python3 extract_inference_sufficient.py --deploy $NS/deploy/e9372b75 \
        --design <deploy>/docs/orchestration/state/s5p/prod/design.json --v $NS/stage3/V/V-s3v.npz \
        --out <new dir>/inference_sufficient.npz [--group frozen|recovery-union]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def import_frozen(deploy: Path):
    nd = (deploy / "nd-unfolding").resolve()
    sys.path.insert(0, str(nd))
    import s5p_joint as sj  # noqa: E402
    import s5p_inference as si  # noqa: E402
    for mod in (sj, si):
        got = Path(mod.__file__).resolve()
        if got.parent != nd:
            raise SystemExit(f"{mod.__name__} imported from {got}, not from the deploy {nd} (OI-136)")
    return sj, si


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--deploy", type=Path, required=True, help="clean deploy whose nd-unfolding is the frozen code")
    ap.add_argument("--design", type=Path, required=True)
    ap.add_argument("--v", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--group", default="frozen", help="label stored in the manifest (frozen | recovery-union)")
    ap.add_argument("--no-product-digests", action="store_true", help="skip per-product sha256 (testing only)")
    a = ap.parse_args(argv)
    for p in (a.out, Path(str(a.out) + ".manifest.json")):
        if p.exists():
            raise SystemExit(f"refusing to overwrite {p}")
    sj, si = import_frozen(a.deploy)

    design = json.loads(a.design.read_text())
    sj.check_v(design, a.v)
    stage1 = json.loads(Path(design["stage1"]).read_text())
    supported = json.loads(Path(design["s5c_contract"]).read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix(stage1, supported)
    model = sj.Model(design, U)
    V = np.asarray(np.load(a.v, allow_pickle=False)["V"], float)
    coefs = [float(c) for c in design.get("shift_coefficients", [0.0])]

    arrays = {"V": V, "f_data": model.f_data, "jitters": model.jitters, "pz_index": pz_index,
              "U": U, "supported_cells": np.asarray(supported, dtype=np.int64)}
    manifest = {"schema": "s5p-inference-sufficient/1", "group": a.group,
                "deploy": str(a.deploy.resolve()), "s5p_joint_sha256": sha256(sj.__file__),
                "s5p_inference_sha256": sha256(si.__file__), "design": str(a.design), "design_sha256": sha256(a.design),
                "v_sha256": sha256(a.v), "alpha_family": design["alpha_family"], "shift_coefficients": coefs,
                "names": names, "nulls": {}, "power": {}}
    for key, spec in design["nulls"].items():
        files = sj.product_files(spec["calibration_glob"])
        want = sj.calibration_count(spec)
        if len(files) != want:
            raise SystemExit(f"{key}: {len(files)} calibration products, {want} declared")
        mu, var = sj.prediction(spec["prediction"], U)
        dom = np.ones(len(names), bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        F, seeds = sj.ensemble(model, files)
        pspec = design.get("process_shift", {}).get(key)
        D, d_pairs = sj.load_shift(pspec, len(names))
        if D is not None:
            S, sinfo = sj.shift_vector(pspec, D, d_pairs, F, mu, var, V, dom)
            arrays[f"S__{key}"] = S
        else:
            sinfo = {"mode": "none", "reason": pspec["none"]}
        m1 = design.get("m1_shift", {}).get(key)
        if m1 is not None and "none" not in m1:
            d1, _ = sj.load_shift({k: v for k, v in m1.items() if k in ("path", "sha256")}, len(names))
            arrays[f"d1__{key}"] = d1
        arrays.update({f"F__{key}": F, f"seeds__{key}": seeds, f"mu__{key}": mu, f"var__{key}": var,
                       f"dom__{key}": dom})
        manifest["nulls"][key] = {
            "B": int(len(files)), "surrogate_seed0": int(spec["surrogate_seed0"]), "domain": spec.get("domain"),
            "shift": sinfo, "m1": (None if m1 is None or "none" in m1 else
                                   {"kappa": m1["kappa"], "kappa_robust": m1["kappa_robust"], "sha256": m1["sha256"]}),
            "prediction": spec["prediction"], "prediction_sha256": sha256(spec["prediction"]),
            "products": None if a.no_product_digests else [[Path(p).name, sha256(p)] for p in files]}
    for key, spec in design.get("power", {}).items():
        files = sj.product_files(spec["glob"])
        if len(files) < 20:
            manifest["power"][key] = {"n": len(files), "not_extracted": "fewer than 20 products"}
            continue
        Fa, sa = sj.ensemble(model, files)
        arrays[f"Fpow__{key}"] = Fa
        arrays[f"seedspow__{key}"] = sa
        manifest["power"][key] = {"n": int(len(files)), "declared": spec.get("n"), "null": spec.get("null", "MnvTune_v1"),
                                  "surrogate_seed0": int(spec["surrogate_seed0"]),
                                  "products": None if a.no_product_digests else [[Path(p).name, sha256(p)] for p in files]}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, **arrays)
    manifest["npz_sha256"] = sha256(a.out)
    Path(str(a.out) + ".manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps({"out": str(a.out), "npz_sha256": manifest["npz_sha256"],
                      "B": {k: v["B"] for k, v in manifest["nulls"].items()}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
