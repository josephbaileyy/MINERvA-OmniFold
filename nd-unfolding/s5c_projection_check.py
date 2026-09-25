#!/usr/bin/env python3
"""Phase-A exit check: reproduce the adopted (E_avail,W) projection from its stored operands.

Re-runs the production projector ``project_cov_nd.py`` (diagnostic run class, fresh output path) on
the adopted source ``z-cv.npz`` and compares the fresh product with the adopted product
``cov_5d_to_eavailW_publication.root`` content-wise: the projected covariance, the marginal CV, the
row index, and the receipt digests of ``M`` and of the read-back row index. File bytes are not
compared (ROOT embeds timestamps).

MEASURES: whether the stored operands and today's projector reproduce the adopted reporting
product. CANNOT AUTHORIZE: any new adoption, a change to the adopted bytes, or any scientific grade.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def read_product(path: Path) -> dict:
    import ROOT

    f = ROOT.TFile.Open(str(path), "READ")
    out = {}
    cov = [k.GetName() for k in f.GetListOfKeys() if k.GetName().startswith("hCov_proj")]
    if len(cov) != 1:
        raise RuntimeError(f"{path}: expected one hCov_proj*, found {cov}")
    h = f.Get(cov[0])
    n = h.GetNbinsX()
    out["cov"] = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])
    for name in ("hCV_marginal", "hRowIndex"):
        hy = f.Get(name)
        out[name] = np.array([hy.GetBinContent(i + 1) for i in range(hy.GetNbinsX())])
    f.Close()
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--expect-src-sha256", required=True)
    ap.add_argument("--adopted", type=Path, required=True)
    ap.add_argument("--expect-adopted-sha256", required=True)
    ap.add_argument("--adopted-receipt", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    result = {"schema": "s5c-projection-check/1"}
    result["src_sha256"] = sha256_path(a.src)
    result["adopted_sha256"] = sha256_path(a.adopted)
    if result["src_sha256"] != a.expect_src_sha256 or result["adopted_sha256"] != a.expect_adopted_sha256:
        print(json.dumps(result), file=sys.stderr)
        return 4
    fresh = a.out.with_suffix(".root")
    cmd = [sys.executable, str(HERE / "project_cov_nd.py"), "--src-cov", str(a.src),
           "--src-hist", "hCov_combined5d_total_uthrow", "--src-cv", str(a.src),
           "--src-axes", "pt,pz,eavail,q3,W", "--keep-axes", "eavail,W",
           "--run-class", "diagnostic", "--expect-variant", "cv", "--out", str(fresh)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    result["projector_rc"] = proc.returncode
    result["projector_stdout_tail"] = proc.stdout[-2000:]
    result["projector_stderr_tail"] = proc.stderr[-2000:]
    if proc.returncode != 0:
        a.out.write_text(json.dumps(result, indent=1))
        return 5
    new_r = json.loads(Path(str(fresh) + ".receipt.json").read_text())
    old_r = json.loads(a.adopted_receipt.read_text())
    for key in ("M_content_sha256", "row_index_sha256_readback", "n_dst", "src_cells_dropped", "src_reported"):
        result[f"receipt_{key}_equal"] = new_r.get(key) == old_r.get(key)
        result[f"receipt_{key}"] = new_r.get(key)
    new_p, old_p = read_product(fresh), read_product(a.adopted)
    scale = float(np.max(np.abs(old_p["cov"])))
    result["cov_max_abs_diff_over_max"] = float(np.max(np.abs(new_p["cov"] - old_p["cov"]))) / scale
    result["cov_bitwise_equal"] = bool(np.array_equal(new_p["cov"], old_p["cov"]))
    for name in ("hCV_marginal", "hRowIndex"):
        result[f"{name}_bitwise_equal"] = bool(np.array_equal(new_p[name], old_p[name]))
    result["fresh_product"] = str(fresh)
    result["fresh_product_sha256"] = sha256_path(fresh)
    result["reproduced"] = bool(
        result["cov_max_abs_diff_over_max"] <= 1e-12 and result["hRowIndex_bitwise_equal"]
        and result["receipt_M_content_sha256_equal"] and result["receipt_row_index_sha256_readback_equal"])
    a.out.write_text(json.dumps(result, indent=1))
    print(json.dumps({k: result[k] for k in ("reproduced", "cov_max_abs_diff_over_max", "cov_bitwise_equal")}))
    return 0 if result["reproduced"] else 6


if __name__ == "__main__":
    sys.exit(main())
