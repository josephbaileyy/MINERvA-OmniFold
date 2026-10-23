#!/usr/bin/env python3
"""RE-2 J0 readout: the K1 controls, the refined-arm checks and the refinement health, as declared.

    re2_k1.py --runs j0_runs.tsv --checks j0_checks.tsv --out-dir OUT --eu E_U.root --expect-eu-sha256 S \
        --result k1.json

Each check compares the hXSec2D of a J0 output with a reference, on E_U's 205 reported cells
(``hXSec2D > 0``, C order over (pT, p||)):

* PASS when the largest relative difference is at most 1e-8 and both report the same cell set. This is the XR
  frozen-repeat criterion, which RE-1's K1-2D also used. Configuration (a) is LightGBM's non-deterministic
  mode, so equality bit for bit is reported but does not decide.
* A reference given with a sha256 is re-hashed first; a mismatch fails the check.
* ``kind = differs``: a power check. It PASSES when the two differ in at least one reported cell.

Every refined output also has its refinement health read from ``re2Refinement``. It PASSES when the clipped
fraction is at most 0.01 and refined/signed lies in [0.99, 1.01], and the classifier is the declared 400/31
where the run declares a size.

MEASURES: the declared controls. CANNOT AUTHORIZE: a production job (the director binds J1-J8 after J0).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

TOL = 1e-8
CLIP_MAX = 0.01
RATIO_BAND = (0.99, 1.01)


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def xsec(path: Path) -> np.ndarray:
    """hXSec2D [ix, iy] (14 x 16) from a driver ROOT file, or 'xsec' from an RE-1 npz."""
    if path.suffix == ".npz":
        return np.asarray(np.load(path, allow_pickle=False)["xsec"], float)
    import ROOT
    f = ROOT.TFile.Open(str(path))
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open {path}")
    h = f.Get("hXSec2D")
    if not h:
        raise RuntimeError(f"no hXSec2D in {path}")
    out = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)] for i in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return out


def refinement(path: Path) -> dict | None:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    t = f.Get("re2Refinement")
    out = json.loads(t.GetTitle()) if t else None
    f.Close()
    return out


def compare(a: np.ndarray, b: np.ndarray, cells: np.ndarray) -> dict:
    fa, fb = a.ravel(order="C"), b.ravel(order="C")
    rel = np.abs(fa[cells] / fb[cells] - 1.0)
    return {"max_rel": float(rel.max()), "median_rel": float(np.median(rel)),
            "same_cell_set": bool(np.array_equal(np.flatnonzero(fa > 0), cells)
                                  and np.array_equal(np.flatnonzero(fb > 0), cells)),
            "bitwise_224": bool(np.array_equal(fa, fb))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--checks", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--eu", type=Path, required=True)
    ap.add_argument("--expect-eu-sha256", required=True)
    ap.add_argument("--result", type=Path, required=True)
    a = ap.parse_args(argv)
    if sha256_path(a.eu) != a.expect_eu_sha256:
        print("E_U digest differs", file=sys.stderr)
        return 4
    eu = xsec(a.eu)
    cells = np.flatnonzero(eu.ravel(order="C") > 0)
    if cells.size != 205:
        raise RuntimeError(f"E_U reports {cells.size} cells, not 205")
    runs = {r["label"]: r for r in csv.DictReader(open(a.runs), delimiter="\t")}
    out_of = lambda label: a.out_dir / label / "xsec.root"  # noqa: E731
    result = {"schema": "re2-j0-k1/1", "eu_sha256": a.expect_eu_sha256, "code_sha256": sha256_path(Path(__file__)),
              "tolerance": TOL, "checks": [], "health": []}
    for c in csv.DictReader(open(a.checks), delimiter="\t"):
        test = out_of(c["test"])
        ref = out_of(c["ref"][4:]) if c["ref"].startswith("run:") else Path(c["ref"])
        row = {"id": c["id"], "kind": c["kind"], "test": c["test"], "ref": c["ref"]}
        if c.get("ref_sha256"):
            got = sha256_path(ref) if ref.is_file() else None
            row["ref_sha256_ok"] = got == c["ref_sha256"]
        if not test.is_file() or not ref.is_file():
            row.update(verdict="FAIL", reason="missing file")
        else:
            row.update(compare(xsec(test), xsec(ref), cells))
            if c["kind"] == "differs":
                ok = row["max_rel"] > 0.0
            else:
                ok = row["max_rel"] <= TOL and row["same_cell_set"]
            ok = ok and row.get("ref_sha256_ok", True)
            row["verdict"] = "PASS" if ok else "FAIL"
        result["checks"].append(row)
    for label, r in runs.items():
        if "negweight-refined" not in r["args"]:
            continue
        p = out_of(label)
        ev = refinement(p) if p.is_file() else None
        sized = "--refine-n-estimators" in r["args"]
        ok = ev is not None and ev["clipped_fraction"] <= CLIP_MAX and \
            RATIO_BAND[0] <= ev["refined_over_signed"] <= RATIO_BAND[1]
        if ok and sized:
            ok = ev["params"].get("n_estimators") == 400 and ev["params"].get("num_leaves") == 31
        result["health"].append({"label": label, "refinement": ev, "verdict": "PASS" if ok else "FAIL"})
    verdicts = [x["verdict"] for x in result["checks"] + result["health"]]
    result["verdict"] = "PASS" if verdicts and all(v == "PASS" for v in verdicts) else "FAIL"
    a.result.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"], "n_checks": len(result["checks"]),
                      "n_health": len(result["health"]),
                      "failed": [x.get("id", x.get("label")) for x in result["checks"] + result["health"]
                                 if x["verdict"] != "PASS"]}))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
