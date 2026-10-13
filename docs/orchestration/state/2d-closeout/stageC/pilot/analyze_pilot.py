#!/usr/bin/env python3
"""Stage C pilot analyses P0 (producer bridge), P2 (K1, the July bridge, and P2-EQ) and P3 (active laterals).
Every check and threshold here is frozen in DESIGN.md §3, §5 and §7 before any job. P1 is analysed by
p1/analyze_p1.py and P2-G2 by p2g2/analyze_g2.py.

  python analyze_pilot.py p0 <result.json>
  python analyze_pilot.py p2 <result.json>
  python analyze_pilot.py p3 <result.json>

NERSC login node, after setup_salloc_env.sh, from the deployed package. Reads the job outputs
$NS/out/<job name>/xsec.root and pinned references; writes one JSON. Never raises on a scientific outcome: a missing
output or a failed pin is INCONCLUSIVE.

The 1e-8 comparisons call the frozen XR instrument (state/next-preparation-20261009/xr-linux/xr/xr_compare.py,
sha256 9e59c590..., its compare()), with its frozen 205 reported GlobalIDs (manifest/references.json E_C,
af7d5a19...). The criterion is not re-implemented here.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
NS = "/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013"
OUT = f"{NS}/out"
D2 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
PN = f"{D2}/uq/purity_newomni"
HERE = Path(__file__).resolve().parent
XR = HERE.parents[2] / "next-preparation-20261009" / "xr-linux" / "xr"
PIN = {
    "xr_compare": (XR / "xr_compare.py", "9e59c590cd33868bd619694ceff68adbed7cc4fa4dc05aeb1b3e76653e2e948b"),
    "references": (XR / "manifest" / "references.json",
                   "af7d5a1935176367e3c6cff9c17986e8e4e5c15c91b75d73efb3ccec04b88c89"),
    "XR_L0": ("/pscratch/sd/j/josephrb/xr-linux-20261011/L0/a1/XR-L0.root",
              "751380245dbb27f67616ade8321d73274e0a5c0bb1344275fc3b67db2595aecc"),
    "ML": (f"{D2}/uq/seedscan_lgbm_ml/uq_covariance_ml.root",
           "3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9"),
    "E_U": (f"{D2}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
            "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c"),
    "J_CV": (f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_CV.root",
             "b8457af7897b9d8b186670efad4ab6e294077613d8d17632825490ea653b98cf"),
    "J_NormDISCC_0": (f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_NormDISCC_0.root",
                      "5819b46bf9842de97c4b14418c224e82aa927897883ff4b7428da6cb2cb6cdb0"),
    "J_MaRES_0": (f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_MaRES_0.root",
                  "80e1e04eb13f150edcc398959ff555ce67ece391865d0994c63cecc4d56036dc"),
    "J_Flux_23": (f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_Flux_23.root",
                  "eb8414af4d9c06e4be80fc190ddfbd8734e0470b7f6e30c1790cebe6cb171141"),
    "J_Muon_Energy_MINOS_0": (f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_Muon_Energy_MINOS_0.root",
                              "09828330f8294a544c8c90a58b9577f66f86606c90704608580ecba2672becf5"),
    "J_Muon_Energy_MINOS_1": (f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_Muon_Energy_MINOS_1.root",
                              "444c232016392344dede8369cf4c1f816763a4356a09e543194b9f0670477786"),
    "J_BeamAngleX_0": (f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_BeamAngleX_0.root",
                       "ed548ad9bdbd2dc4b735771ba96708ad7cf294f93cba67b0f4a21db3bf5aec10"),
    "J_BeamAngleX_1": (f"{PN}/2d_xsec_MEFHC_5iter_lgbm_pn_uni_BeamAngleX_1.root",
                       "c8cf088c8c48c72f1bc9a97abaa7c6dba0a014c9ecf31e372d6d0950f89176dc"),
}
PROD_SHA = "74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56"
HELPER_SHA = "e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a"
CVOMNI = "/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root"
UOMNI = f"{D2}/runEventLoopOmniFold_MEFHC_universes_full.root"
FLUXU = f"{D2}/baseline_flux/flux_integral_universes_MEFHC.root"
ACT = "/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged"
K1_SIGMA_ML_TOL = 0.01      # DESIGN §5: max_c |P2 - July|_c / sigma_ML,c for non-null universes


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def pins():
    bad = {k: str(p) for k, (p, want) in PIN.items() if not Path(p).is_file() or sha(p) != want}
    return bad


def xr():
    spec = importlib.util.spec_from_file_location("xr_compare", PIN["xr_compare"][0])
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    if m.TOL != 1e-8:
        raise SystemExit("REFUSE: xr_compare TOL is not 1e-8")
    cells = json.loads(Path(PIN["references"][0]).read_text())["references"]["E_C"]["reported_globalid"]
    return m.compare, cells


def named(path):
    f = ROOT.TFile.Open(str(path))
    out = {}
    for k in ("runConfig", "driverSha256", "omnifoldHelperSha256"):
        o = f.Get(k)
        out[k] = o.GetTitle() if o else None
    f.Close()
    if out["runConfig"]:
        out["runConfig"] = json.loads(out["runConfig"])
    return out


def cellvec(path):
    """hXSec2D over the 205 reported cells (E_U hXSec2D > 0, C order over (pT, p_par))."""
    def a(p):
        f = ROOT.TFile.Open(str(p))
        h = f.Get("hXSec2D")
        x = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                      for i in range(1, h.GetNbinsX() + 1)])
        f.Close()
        return x
    m = (a(PIN["E_U"][0]) > 0).ravel()
    return a(path).ravel()[m]


def sigma_ml():
    f = ROOT.TFile.Open(PIN["ML"][0])
    h = f.Get("hCov2D_reported")
    s = np.sqrt(np.array([h.GetBinContent(i + 1, i + 1) for i in range(h.GetNbinsX())]))
    f.Close()
    return s


def stats(v):
    v = np.asarray(v)
    return {"median": float(np.median(v)), "p84": float(np.percentile(v, 84)), "max": float(np.max(v))}


def out_of(name):
    p = Path(OUT, name, "xsec.root")
    return p if p.is_file() else None


def prov(p, want):
    """want: dict of runConfig keys that must match, plus driver sha."""
    n = named(p)
    rc = n["runConfig"] or {}
    bad = {k: rc.get(k) for k, v in want.items() if rc.get(k) != v}
    ok = n["driverSha256"] == PROD_SHA and n["omnifoldHelperSha256"] == HELPER_SHA and not bad
    return ok, {"driverSha256": n["driverSha256"], "omnifoldHelperSha256": n["omnifoldHelperSha256"],
                "runConfig_mismatch": bad}


def shift(new, ref, sml):
    d = np.abs(cellvec(new) - cellvec(ref))
    return {"over_sigma_ml": stats(d / sml), "rel": stats(d / np.abs(cellvec(ref)))}


def p0():
    rep = {"item": "P0", "pins_failed": pins()}
    compare, cells = xr()
    a, b = out_of("2dc_C_P0_default"), out_of("2dc_C_P0_derived")
    if rep["pins_failed"] or a is None or b is None:
        rep["P0"] = "INCONCLUSIVE"
        rep["why"] = "pins failed or an output is missing"
        return rep
    base = {"omnifile": CVOMNI, "seed": 42, "iters": 5, "use_weights": True, "estimator": "lgbm",
            "bkg_mode": "purity", "universe": None, "bootstrap_seed": None}
    pa, ia = prov(a, base | {"branch_select": "all"})
    pb, ib = prov(b, base | {"branch_select": "derived"})
    rep["provenance"] = {"default": ia, "derived": ib, "ok": pa and pb}
    rep["P0-1_default_vs_L0"] = compare(str(a), PIN["XR_L0"][0], cells)
    rep["P0-2_derived_vs_default"] = compare(str(b), str(a), cells)
    v = (rep["P0-1_default_vs_L0"]["verdict"], rep["P0-2_derived_vs_default"]["verdict"])
    if not rep["provenance"]["ok"] or "INCONCLUSIVE" in v:
        rep["P0"] = "INCONCLUSIVE"
    else:
        rep["P0"] = "PASS" if v == ("PASS", "PASS") else "FAIL"
    return rep


def p2():
    rep = {"item": "P2", "pins_failed": pins()}
    compare, cells = xr()
    sml = sigma_ml()
    runs = {"NormDISCC0": ("NormDISCC:0", "J_NormDISCC_0", "derived", "E1"),
            "MaRES0": ("MaRES:0", "J_MaRES_0", "derived", "E2"),
            "Flux23": ("Flux:23", "J_Flux_23", "derived", "E2"),
            "MINOS0": ("Muon_Energy_MINOS:0", "J_Muon_Energy_MINOS_0", "derived", "E2"),
            "MINOS0def": ("Muon_Energy_MINOS:0", "J_Muon_Energy_MINOS_0", "all", "E2")}
    rep["K1_comparisons"] = {}
    verdicts = []
    for tag, (uni, ref, sel, env) in runs.items():
        p = out_of(f"2dc_C_P2_{tag}")
        if p is None or rep["pins_failed"]:
            rep["K1_comparisons"][tag] = {"verdict": "INCONCLUSIVE", "why": "output missing or pins failed"}
            verdicts.append("INCONCLUSIVE")
            continue
        ok, info = prov(p, {"omnifile": UOMNI, "universe": uni, "seed": 42, "branch_select": sel,
                            "flux_universe_file": FLUXU, "bkg_mode": "purity", "bootstrap_seed": None})
        e1 = compare(str(p), PIN[ref][0], cells)
        r = {"universe": uni, "branch_select": sel, "reference": {"path": PIN[ref][0], "sha256": PIN[ref][1]},
             "provenance": info | {"ok": ok}, "E1_1e-8": e1, "shift": shift(p, PIN[ref][0], sml), "envelope": env}
        if not ok or e1["verdict"] == "INCONCLUSIVE":
            r["verdict"] = "INCONCLUSIVE"
        elif env == "E1":
            r["verdict"] = e1["verdict"]
        else:
            r["verdict"] = "PASS" if r["shift"]["over_sigma_ml"]["max"] <= K1_SIGMA_ML_TOL else "FAIL"
        rep["K1_comparisons"][tag] = r
        verdicts.append(r["verdict"])
    rep["K1"] = ("INCONCLUSIVE" if "INCONCLUSIVE" in verdicts else "FAIL" if "FAIL" in verdicts else "PASS")
    a, b = out_of("2dc_C_P2_MINOS0def"), out_of("2dc_C_P2_MINOS0")
    rep["P2-EQ_derived_vs_default"] = (compare(str(b), str(a), cells) if a and b and not rep["pins_failed"]
                                       else {"verdict": "INCONCLUSIVE", "why": "output missing or pins failed"})
    n = out_of("2dc_C_P2_NormDISCC0")
    if n and not rep["pins_failed"]:
        rep["null_NormDISCC0_vs_July_CV_measured"] = {"E1_1e-8": compare(str(n), PIN["J_CV"][0], cells),
                                                       "shift": shift(n, PIN["J_CV"][0], sml)}
    return rep


def p3():
    rep = {"item": "P3", "pins_failed": pins()}
    sml = sigma_ml()
    sums = {}
    for ln in Path(ACT, "SHA256SUMS").read_text().splitlines():
        h, f = ln.split()
        sums[f] = h
    pairs = {"BeamAngleX0": ("BeamAngleX_0", "J_BeamAngleX_0", "J_BeamAngleX_1"),
             "MINOS0": ("Muon_Energy_MINOS_0", "J_Muon_Energy_MINOS_0", "J_Muon_Energy_MINOS_1")}
    for tag, (u, j0, j1) in pairs.items():
        p = out_of(f"2dc_C_P3_{tag}")
        f = f"{ACT}/runEventLoopOmniFold_5D_MEFHC_active_{u}.root"
        if p is None or rep["pins_failed"]:
            rep[tag] = {"outcome": "INCONCLUSIVE", "why": "output missing or pins failed"}
            continue
        ok, info = prov(p, {"omnifile": f, "universe": None, "seed": 42, "branch_select": "all",
                            "bkg_mode": "purity", "bootstrap_seed": None})
        sb = np.abs(cellvec(PIN[j0][0]) - cellvec(PIN[j1][0])) / 2
        d_july = cellvec(p) - cellvec(PIN[j0][0])
        r = {"active_file": {"path": f, "sha256_SHA256SUMS": sums.get(Path(f).name)}, "provenance": info | {"ok": ok},
             "vs_july_dump": {"over_sigma_ml": stats(np.abs(d_july) / sml),
                              "over_sigma_band_july_pair": stats(np.abs(d_july) / sb),
                              "rel": stats(np.abs(d_july) / cellvec(PIN[j0][0]))}}
        if tag == "MINOS0":
            q = out_of("2dc_C_P2_MINOS0def")
            if q:
                d = cellvec(p) - cellvec(q)
                r["vs_P2_MINOS0def_same_driver_dump"] = {"over_sigma_ml": stats(np.abs(d) / sml),
                                                         "over_sigma_band_july_pair": stats(np.abs(d) / sb),
                                                         "rel": stats(np.abs(d) / cellvec(q))}
        r["outcome"] = "MEASURED" if ok else "INCONCLUSIVE"
        rep[tag] = r
    return rep


def main():
    what, outp = sys.argv[1], sys.argv[2]
    rep = {"p0": p0, "p2": p2, "p3": p3}[what]()
    Path(outp).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in rep.items() if k in ("P0", "K1", "pins_failed")} |
                     {k: v.get("verdict", v.get("outcome")) for k, v in rep.items() if isinstance(v, dict)
                      and ("verdict" in v or "outcome" in v)}, indent=1))


if __name__ == "__main__":
    main()
