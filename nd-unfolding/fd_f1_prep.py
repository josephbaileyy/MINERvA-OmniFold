#!/usr/bin/env python3
"""F1 prep (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md section 3): the two GENIE v3 truths as
pv-ladder ratios, and the same ratios in ratio_nd's format.

1. A pvl-config/1 copy of the pv-ladder config whose ``vertices`` are the two F1 predictions only (path and sha256);
   everything else, the rung's npz and recorded central value, the GENIE 2.12 CV reference and stat_max, is the
   committed config's, unchanged.
2. ``pvl_ratios.main`` on it for rung L-5D-PV (imported, unchanged): each truth's gated, k-normalised shape ratio r
   to GENIE CV on the 65,856 fine cells, exactly as the C_model,5D vertices and the NuWro closure were built.
3. A bridge of each r to s5e-shape-ratio/1 (axes 0-4, the fine edges, shape_ratio = r), so the pseudo-experiments'
   ``ratio_nd`` truth (s5e_deform.ratio_weight at amplitude 1) applies the same per-cell r, then rescales the
   in-grid w_truth total by one constant as every ratio_nd truth does.
4. f1-prep-SHA256SUMS over everything written, relative to --out.

Refuses to write into an existing --out, and refuses a prediction whose sha256 is not the one given.

MEASURES: the truths' reweights. CANNOT AUTHORIZE: anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

_ND = Path(__file__).resolve().parent
for _p in (str(_ND), str(_ND / "pv-ladder")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import pvl_lib as L  # noqa: E402
import pvl_ratios  # noqa: E402

RUNG = "L-5D-PV"
TRUTHS = {"genie_v3_g18": "GENIE v3.04.00 G18_10a_02_11b, phi_t-sampled 5D (E_nu < 100 GeV)",
          "genie_v3_ar23": "GENIE v3.04.00 AR23_20i_00_000, phi_t-sampled 5D (E_nu < 100 GeV)"}
BRIDGE_DEFINITION = ("shape_ratio = the pvl-ratio/1 file's r per fine cell (C order on pt, pz, eavail, q3, W): the "
                     "gated shape ratio to GENIE 2.12 CV, k-normalised over the assigned cells, 1 elsewhere")


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def f1_config(base: dict, preds: dict[str, tuple[str, str]]) -> dict:
    if set(preds) != set(TRUTHS):
        raise SystemExit(f"[FAIL] the F1 truths are {sorted(TRUTHS)}, got {sorted(preds)}")
    cfg = json.loads(json.dumps(base))
    cfg["vertices"] = {k: {"label": TRUTHS[k], "path": p, "sha256": s} for k, (p, s) in sorted(preds.items())}
    cfg["pc_vertex"] = None
    cfg["f1"] = "FD-F1-DECLARATION.md: the committed pv-ladder config with the vertices replaced by the F1 truths"
    return cfg


def bridge(ratio: dict, source: Path) -> dict:
    if ratio.get("schema") != L.RATIO_SCHEMA or tuple(ratio["axes"]) != L.AXES5:
        raise SystemExit(f"[FAIL] {source}: not a five-axis pvl-ratio/1 file")
    r = [float(x) for x in ratio["r"]]
    n = 1
    for a in L.AXES5:
        n *= len(L.FINE[a]) - 1
    if len(r) != n or min(r) <= 0:
        raise SystemExit(f"[FAIL] {source}: needs {n} positive r")
    if ratio.get("truth_cut") is not None:
        raise SystemExit(f"[FAIL] {source}: a truth cut has no ratio_nd equivalent")
    return {"schema": "s5e-shape-ratio/1", "label": ratio["label"], "kind": "pvl-ratio-5d",
            "axes": [0, 1, 2, 3, 4], "edges": [list(L.FINE[a]) for a in L.AXES5],
            "definition": BRIDGE_DEFINITION, "shape_ratio": r, "k": ratio["k"],
            "source": {"path": str(source), "sha256": sha256(source)},
            "code_sha256": sha256(Path(__file__).resolve())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--pvl-config", type=Path, default=_ND / "pv-ladder" / "config.json")
    ap.add_argument("--pred", action="append", required=True, metavar="NAME=PATH=SHA256")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to write into the existing {a.out}")
    preds = {}
    for spec in a.pred:
        name, path, want = spec.split("=", 2)
        got = sha256(Path(path))
        if got != want:
            raise SystemExit(f"[FAIL] {name}: {path} sha256 {got} != {want}")
        preds[name] = (path, want)
    cfg = f1_config(json.loads(a.pvl_config.read_text()), preds)
    a.out.mkdir(parents=True)
    cfg_path = a.out / "config-f1.json"
    cfg_path.write_text(json.dumps(cfg, indent=1) + "\n")
    rc = pvl_ratios.main(["--config", str(cfg_path), "--rung", RUNG, "--out", str(a.out / "ratios")])
    if rc:
        return rc
    (a.out / "bridged").mkdir()
    for name in sorted(TRUTHS):
        src = a.out / "ratios" / RUNG / f"{name}.json"
        out = a.out / "bridged" / f"{name}.json"
        out.write_text(json.dumps(bridge(json.loads(src.read_text()), src), indent=1) + "\n")
    files = sorted(p for p in a.out.rglob("*") if p.is_file())
    sums = "".join(f"{sha256(p)}  ./{p.relative_to(a.out)}\n" for p in files)
    (a.out / "f1-prep-SHA256SUMS").write_text(sums)
    print(sums, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
