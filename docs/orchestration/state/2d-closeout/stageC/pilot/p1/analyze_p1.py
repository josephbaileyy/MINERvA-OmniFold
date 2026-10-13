#!/usr/bin/env python3
"""P1 analysis: per-cell bootstrap sigma of three arms, paired sigma ratios, and the b == 1 control.

  python analyze_p1.py --out-root OUT --result RESULT.json
        [--eu PATH] [--l0 PATH] [--xr-dir DIR] [--p1-sha SHA] [--n 20]

Output layout (the sbatch script must write exactly this):
  OUT/2dc_C_P1_<arm>_<NN>/xsec.root   arm in fixed, joint, bkg; NN = 01..20 (sbatch_pilot.sh layout)
  OUT/2dc_C_P1_unit/xsec.root         the b == 1 control
Arms (all --iters 5 --use-weights --estimator lgbm --seed 42 --bootstrap-seed N, CV omnifile, bkg-mode purity):
  fixed  production driver (sha256 74a4ed69...), default --bootstrap-streams both (fixed purity; VL170 law at seed 42)
  joint  driver_p1.py --bootstrap-streams three (data + signal MC + background, purity from D*, B*)
  bkg    driver_p1.py --bootstrap-streams bkg   (background stream only, purity from D, B*)
  unit   driver_p1.py --bootstrap-streams three --unit-factors --bootstrap-seed 1 --seed 42

Gates. A replica counts only if its file exists and its provenance matches: driverSha256 (production digest for
fixed, the driver_p1 digest for the others), runConfig seed 42, bootstrap_seed N, the arm's
bootstrap_streams, unit_factors false, bkg_mode purity, estimator lgbm, iters 5, use_weights, no universe or
closure; and every output shares one omnifile and mcfile. Any missing or mismatched replica makes that arm
INCONCLUSIVE, and no ratio involving it is computed.

Measured (no pass/fail): over the 205 reported cells (E_U hXSec2D > 0, sha256 4f5a1b6d..., C order (pT, p_par)),
sigma_c = std over the 20 replicas (ddof = 1) per arm; the paired ratios sigma_joint/sigma_fixed and
sigma_bkg/sigma_fixed per cell, each with a leave-one-replica-out jackknife SE (replicas paired by bootstrap
seed: replica k is removed from both arms); the median of each ratio over cells with the jackknife SE of the
median (the median recomputed on each leave-one-out set).

b == 1 check: the unit run against XR-L0 (sha256 75138024...) with the frozen 1e-8 instrument
xr_compare.compare (sha256 9e59c590...), cells = references.json references.E_C.reported_globalid.
PASS iff its verdict is PASS (and the unit run's provenance matches); otherwise FAIL, or INCONCLUSIVE when the
run or a digest is missing.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PROD_SHA = "74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56"
EU_SHA = "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c"
L0_SHA = "751380245dbb27f67616ade8321d73274e0a5c0bb1344275fc3b67db2595aecc"
XRC_SHA = "9e59c590cd33868bd619694ceff68adbed7cc4fa4dc05aeb1b3e76653e2e948b"
EU_DEFAULT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
L0_DEFAULT = "/pscratch/sd/j/josephrb/xr-linux-20261011/L0/a1/XR-L0.root"
XR_DIR_DEFAULT = HERE.parents[3] / "next-preparation-20261009" / "xr-linux" / "xr"
ARMS = {"fixed": "both", "joint": "three", "bkg": "bkg"}
SEED = 42
UNIT_BOOT = 1


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def replica_path(out, arm, n):
    return Path(out, f"2dc_C_P1_{arm}_{n:02d}", "xsec.root")   # sbatch_pilot.sh layout: out/<job name>/xsec.root


def unit_path(out):
    return Path(out, "2dc_C_P1_unit", "xsec.root")


def read_output(path):
    """hXSec2D as a (14, 16) [pT, p_par] array, plus the provenance TNamed records."""
    import ROOT
    f = ROOT.TFile.Open(str(path))
    if not f or f.IsZombie():
        raise OSError(f"cannot open {path}")
    h = f.Get("hXSec2D")
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    x = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(ny)] for i in range(nx)])
    prov = {}
    for name in ("runConfig", "driverSha256", "p1Streams"):
        o = f.Get(name)
        prov[name] = o.GetTitle() if o else None
    f.Close()
    return x, prov


def check_prov(prov, arm, n, p1_sha):
    """List of mismatches (empty = provenance matches)."""
    bad = []
    want_sha = PROD_SHA if arm == "fixed" else p1_sha
    if prov["driverSha256"] != want_sha:
        bad.append(f"driverSha256 {prov['driverSha256']} != {want_sha}")
    try:
        rc = json.loads(prov["runConfig"] or "")
    except ValueError:
        return bad + ["runConfig missing or unreadable"], {}
    want = {"seed": SEED, "bootstrap_seed": n, "bkg_mode": "purity", "estimator": "lgbm", "iters": 5,
            "use_weights": True, "universe": None, "closure": False,
            "bootstrap_streams": "three" if arm == "unit" else ARMS[arm]}
    for k, v in want.items():
        if rc.get(k) != v:
            bad.append(f"runConfig {k}={rc.get(k)!r} != {v!r}")
    if bool(rc.get("unit_factors", False)) != (arm == "unit"):
        bad.append(f"runConfig unit_factors={rc.get('unit_factors')!r}")
    if arm != "fixed":
        try:
            ps = json.loads(prov["p1Streams"] or "")
            if ps.get("bootstrap_seed") != n or ps.get("streams") != want["bootstrap_streams"]:
                bad.append(f"p1Streams {ps}")
        except ValueError:
            bad.append("p1Streams missing")
    return bad, rc


def jackknife_ratio(xa, xb):
    """Per-cell sigma_a/sigma_b and median over cells, each with a leave-one-replica-out jackknife SE."""
    n = xa.shape[0]
    r = xa.std(axis=0, ddof=1) / xb.std(axis=0, ddof=1)
    loo = np.array([np.delete(xa, k, 0).std(axis=0, ddof=1) / np.delete(xb, k, 0).std(axis=0, ddof=1)
                    for k in range(n)])
    se = np.sqrt((n - 1) / n * ((loo - loo.mean(axis=0)) ** 2).sum(axis=0))
    med = float(np.median(r))
    med_loo = np.median(loo, axis=1)
    med_se = float(np.sqrt((n - 1) / n * ((med_loo - med_loo.mean()) ** 2).sum()))
    return {"per_cell_ratio": r.tolist(), "per_cell_jackknife_se": se.tolist(), "median": med,
            "median_jackknife_se": med_se, "mean": float(r.mean()), "q16_q84": np.quantile(r, [0.16, 0.84]).tolist(),
            "median_per_cell_se": float(np.median(se))}


def unit_check(out, l0, xr_dir, cells, p1_sha):
    up = unit_path(out)
    res = {"unit_path": str(up), "ref_path": str(l0)}
    if not up.is_file():
        return dict(res, verdict="INCONCLUSIVE", why="unit run output missing")
    xrc = Path(xr_dir, "xr_compare.py")
    if not xrc.is_file() or sha(xrc) != XRC_SHA:
        return dict(res, verdict="INCONCLUSIVE", why=f"{xrc} missing or sha256 != {XRC_SHA}")
    if not Path(l0).is_file() or sha(l0) != L0_SHA:
        return dict(res, verdict="INCONCLUSIVE", why=f"XR-L0 missing or sha256 != {L0_SHA}")
    _, prov = read_output(up)
    bad, _ = check_prov(prov, "unit", UNIT_BOOT, p1_sha)
    res["provenance_mismatches"] = bad
    res["unit_sha256"] = sha(up)
    if bad:
        return dict(res, verdict="INCONCLUSIVE", why="unit run provenance mismatch")
    spec = importlib.util.spec_from_file_location("xr_compare_frozen", xrc)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    cmp = m.compare(str(up), str(l0), cells)
    res["xr_compare"] = cmp
    res["verdict"] = cmp["verdict"]
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--eu", default=EU_DEFAULT)
    ap.add_argument("--l0", default=L0_DEFAULT)
    ap.add_argument("--xr-dir", default=str(XR_DIR_DEFAULT))
    ap.add_argument("--p1-sha", default=None, help="driver_p1.py digest (default: the sibling driver_p1.py)")
    ap.add_argument("--n", type=int, default=20)
    a = ap.parse_args(argv)
    p1_sha = a.p1_sha or sha(HERE / "driver_p1.py")
    refs = json.loads(Path(a.xr_dir, "manifest", "references.json").read_text())["references"]
    cells_ec = refs["E_C"]["reported_globalid"]
    res = {"schema": "p1-analysis/1", "out_root": a.out_root, "n_replicas": a.n, "seed": SEED,
           "driver_sha256": {"fixed": PROD_SHA, "joint": p1_sha, "bkg": p1_sha, "unit": p1_sha},
           "analyze_p1_sha256": sha(Path(__file__).resolve())}
    if not Path(a.eu).is_file() or sha(a.eu) != EU_SHA:
        res["verdict"] = "INCONCLUSIVE"
        res["why"] = f"E_U {a.eu} missing or sha256 != {EU_SHA}"
        Path(a.result).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
        print(res["why"])
        return 2
    xeu, _ = read_output(a.eu)
    mask = xeu > 0
    cells = np.flatnonzero(mask.ravel(order="C"))
    res["n_cells"] = int(cells.size)
    res["cells_equal_E_C_reported_globalid"] = cells.tolist() == cells_ec
    res["cells"] = cells.tolist()

    data, arms = {}, {}
    files = {}
    for arm in ARMS:
        rows, missing, mism = [], [], {}
        for n in range(1, a.n + 1):
            p = replica_path(a.out_root, arm, n)
            if not p.is_file():
                missing.append(n)
                continue
            x, prov = read_output(p)
            bad, rc = check_prov(prov, arm, n, p1_sha)
            files[(arm, n)] = (rc.get("omnifile"), rc.get("mcfile"))
            if bad:
                mism[n] = bad
                continue
            rows.append(x.ravel(order="C")[cells])
        status = "OK" if not missing and not mism else "INCONCLUSIVE"
        arms[arm] = {"status": status, "missing": missing, "provenance_mismatches": mism, "n_ok": len(rows)}
        if status == "OK":
            X = np.array(rows)
            data[arm] = X
            sd = X.std(axis=0, ddof=1)
            arms[arm].update(sigma=sd.tolist(), rel_sigma_median=float(np.median(sd / xeu.ravel()[cells])),
                             mean_over_replicas_rel_to_EU_median=float(np.median(X.mean(axis=0) / xeu.ravel()[cells])))
    inputs = sorted({v for v in files.values()}, key=str)
    res["inputs_seen"] = [list(v) for v in inputs]
    if len(inputs) > 1:
        for arm in arms:
            arms[arm]["status"] = "INCONCLUSIVE"
        res["why_inputs"] = "replicas do not share one omnifile/mcfile"
        data = {}
    res["arms"] = arms
    res["ratios"] = {}
    for num in ("joint", "bkg"):
        key = f"sigma_{num}_over_sigma_fixed"
        if num in data and "fixed" in data:
            res["ratios"][key] = dict(jackknife_ratio(data[num], data["fixed"]), status="MEASURED")
        else:
            res["ratios"][key] = {"status": "INCONCLUSIVE"}
    res["b_eq_1"] = unit_check(a.out_root, a.l0, a.xr_dir, cells_ec, p1_sha)
    Path(a.result).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"arms": {k: v["status"] for k, v in arms.items()},
                      "ratios": {k: {kk: v.get(kk) for kk in ("status", "median", "median_jackknife_se")}
                                 for k, v in res["ratios"].items()},
                      "b_eq_1": res["b_eq_1"]["verdict"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
