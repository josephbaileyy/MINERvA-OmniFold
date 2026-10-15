#!/usr/bin/env python3
"""Stage C production checks (DESIGN §7): the controls, the identities, the closure and every product's provenance.
Every check and threshold is frozen in DESIGN.md before any job.

  python analyze_prod.py c0   <result.json>   controls (G0): b==1 and the production CV, each vs XR-L0 at 1e-8
  python analyze_prod.py s3   <result.json>   laterals (G1): provenance, per-cell closure, P3 reproduction
  python analyze_prod.py s4ii <result.json>   universe panel (G2): provenance, July and null identities
  python analyze_prod.py s1   <result.json>   S1: provenance of 300 replicas, pilot reproduction (joint 1-20)
  python analyze_prod.py s2   <result.json>   S2: provenance of 100 replicas, pilot reproduction (bkg 1-20)
  python analyze_prod.py s4i  <result.json>   S4(i): provenance of 80 replicas
  [--out-root DIR]  read outputs from DIR instead of $NS/out (packaging smoke tests only; recorded in the JSON, and
                    launch.py accepts a c0.json only if its out_root is $NS/out)

NERSC login node, after setup_salloc_env.sh, from the deployed package. Reads $NS/out/<job>/xsec.root and pinned
references; writes one JSON with a verdict per check and an item verdict: PASS, FAIL or INCONCLUSIVE. It never
raises on a scientific outcome. A FAIL or INCONCLUSIVE item verdict is a stop for that line (grant §3).

Reused, not re-implemented (both pinned in manifest.json): the pilot's analyze_pilot.py for the frozen XR
comparison (xr(): xr_compare.compare at TOL 1e-8 over the 205 frozen GlobalIDs), the reference pins, cellvec() and
named(); and p1/analyze_p1.py read_output() for the driver_p1 provenance records (runConfig, p1Streams).
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PILOT = HERE.parent / "pilot"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


AP = _load("analyze_pilot", PILOT / "analyze_pilot.py")
A1 = _load("analyze_p1", PILOT / "p1" / "analyze_p1.py")

NS = "/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015"
OUT = f"{NS}/out"
PILOT_OUT = "/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/out"
PILOT_SUMS = PILOT / "evidence" / "SHA256SUMS.pscratch"   # the pilot's re-measured digests (b82a0e08...)
PILOT_SUMS_SHA = "b82a0e085fab914693291ddc2468a197315987e9c111b8c05491ef4bd3c7f33f"
PROD_SHA = AP.PROD_SHA
HELPER_SHA = AP.HELPER_SHA
P1_SHA = "3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578"
CVOMNI, UOMNI, FLUXU, ACT = AP.CVOMNI, AP.UOMNI, AP.FLUXU, AP.ACT
CLOSURE_TOL = 1e-9          # DESIGN §7: max over the 205 reported cells of |c - 1| for an active-file lateral
SEEDS = [42, 45, 48, 51, 54]
PANEL_U = ["NormDISCC:0", "Flux:23", "MaRES:0", "MaCCQE:0", "2p2h:0", "MinosEfficiency:0", "Muon_Energy_MINOS:0"]
LATERALS = ["BeamAngleX_0", "BeamAngleX_1", "BeamAngleY_0", "BeamAngleY_1", "MuonResolution_0", "MuonResolution_1",
            "Muon_Energy_MINERvA_0", "Muon_Energy_MINERvA_1", "Muon_Energy_MINOS_0", "Muon_Energy_MINOS_1"]
SWEEPS_JSON = HERE.parents[1] / "stageB" / "evidence" / "b-genie-truth" / "sweeps.json"
SWEEPS_JSON_SHA = "15b57de9124f204bf3cdf8cd0660c467783bf633bf0d45bfbd4e2506b19be2e4"
PN = f"{AP.D2}/uq/purity_newomni"
BASE = {"iters": 5, "use_weights": True, "estimator": "lgbm", "bkg_mode": "purity"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def out_of(name):
    p = Path(OUT, name, "xsec.root")
    return p if p.is_file() else None


def prov(p, driver_sha, want, p1=None):
    """Provenance: driver and helper digests, runConfig keys, and (driver_p1 runs) the p1Streams record."""
    n = AP.named(p)
    rc = n["runConfig"] or {}
    bad = {k: rc.get(k) for k, v in want.items() if rc.get(k) != v}
    if n["driverSha256"] != driver_sha:
        bad["driverSha256"] = n["driverSha256"]
    if n["omnifoldHelperSha256"] != HELPER_SHA:
        bad["omnifoldHelperSha256"] = n["omnifoldHelperSha256"]
    if p1 is not None:   # (bootstrap_seed, streams, unit_factors)
        _, pr = A1.read_output(p)
        try:
            ps = json.loads(pr["p1Streams"] or "")
        except ValueError:
            ps = {}
        if ps.get("bootstrap_seed") != p1[0] or ps.get("streams") != p1[1]:
            bad["p1Streams"] = ps
        if bool(rc.get("unit_factors", False)) != p1[2]:
            bad["unit_factors"] = rc.get("unit_factors")
    return not bad, bad


def pilot_ref(name):
    """A pilot output, verified against the pilot's committed SHA256SUMS.pscratch before use."""
    if sha(PILOT_SUMS) != PILOT_SUMS_SHA:
        return None, "pilot SHA256SUMS.pscratch digest mismatch"
    rel = f"out/{name}/xsec.root"
    want = [ln.split()[0] for ln in PILOT_SUMS.read_text().splitlines() if ln.split()[1:] == [rel]]
    p = Path(PILOT_OUT, name, "xsec.root")
    if len(want) != 1 or not p.is_file() or sha(p) != want[0]:
        return None, f"pilot {rel} missing or digest mismatch"
    return p, None


def july(u):
    """A July purity_newomni product ('Band_idx'), verified against sweeps.json before use."""
    if sha(SWEEPS_JSON) != SWEEPS_JSON_SHA:
        return None, "sweeps.json digest mismatch"
    rec = json.loads(SWEEPS_JSON.read_text()).get(f"pn/{u}")
    p = Path(PN, f"2d_xsec_MEFHC_5iter_lgbm_pn_uni_{u}.root")
    if not rec or not p.is_file() or sha(p) != rec["sha256"]:
        return None, f"July {u} missing or digest mismatch"
    return p, None


def identity(compare, cells, new, ref, why_ref=None):
    if new is None:
        return {"verdict": "INCONCLUSIVE", "why": "production output missing"}
    if ref is None:
        return {"verdict": "INCONCLUSIVE", "why": why_ref or "reference missing"}
    r = compare(str(new), str(ref), cells)
    r["new"], r["ref"] = str(new), str(ref)
    return r


def verdict(vs):
    vs = list(vs)
    return "FAIL" if "FAIL" in vs else "INCONCLUSIVE" if ("INCONCLUSIVE" in vs or not vs) else "PASS"


def c0():
    rep = {"item": "C0", "pins_failed": AP.pins()}
    compare, cells = AP.xr()
    l0 = AP.PIN["XR_L0"][0]
    u, c = out_of("2dc_P_C0_unit"), out_of("2dc_P_C0_cv")
    pu = prov(u, P1_SHA, BASE | {"omnifile": CVOMNI, "seed": 42, "bootstrap_seed": 1, "universe": None,
                                 "bootstrap_streams": "three"}, p1=(1, "three", True)) if u else (False, "missing")
    pc = prov(c, PROD_SHA, BASE | {"omnifile": CVOMNI, "seed": 42, "bootstrap_seed": None, "universe": None,
                                   "branch_select": "all"}) if c else (False, "missing")
    rep["unit_vs_L0"] = identity(compare, cells, u, l0) | {"provenance_ok": pu[0], "provenance_bad": pu[1]}
    rep["cv_vs_L0"] = identity(compare, cells, c, l0) | {"provenance_ok": pc[0], "provenance_bad": pc[1]}
    vs = []
    for k in ("unit_vs_L0", "cv_vs_L0"):
        r = rep[k]
        vs.append("INCONCLUSIVE" if (rep["pins_failed"] or not r["provenance_ok"]) and r["verdict"] != "FAIL"
                  else r["verdict"])
    rep["C0"] = verdict(vs)
    return rep


def s3():
    import ROOT
    rep = {"item": "S3", "pins_failed": AP.pins(), "laterals": {}}
    compare, cells = AP.xr()
    vs = []
    for u in LATERALS:
        name = f"2dc_P_S3_{u.replace('_', '')}"
        p = out_of(name)
        f = f"{ACT}/runEventLoopOmniFold_5D_MEFHC_active_{u}.root"
        r = {"job": name}
        if p is None:
            r["verdict"] = "INCONCLUSIVE"
            r["why"] = "output missing"
        else:
            ok, bad = prov(p, PROD_SHA, BASE | {"omnifile": f, "seed": 42, "universe": None, "bootstrap_seed": None,
                                                "branch_select": "all"})
            tf = ROOT.TFile.Open(str(p))
            h = tf.Get("hOFCompleteness2D")
            cfull = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                              for i in range(1, h.GetNbinsX() + 1)]).ravel()
            tf.Close()
            cc = cfull[np.array(cells)]
            dev = float(np.max(np.abs(cc - 1)))
            r.update({"provenance_ok": ok, "provenance_bad": bad, "closure_max_abs_c_minus_1": dev,
                      "closure": "PASS" if dev <= CLOSURE_TOL else "FAIL", "sha256": sha(p)})
            r["verdict"] = ("INCONCLUSIVE" if not ok and r["closure"] != "FAIL" else r["closure"])
        if u in ("BeamAngleX_0", "Muon_Energy_MINOS_0"):
            pn = "2dc_C_P3_BeamAngleX0" if u == "BeamAngleX_0" else "2dc_C_P3_MINOS0"
            ref, why = pilot_ref(pn)
            r["reproduces_pilot_" + pn] = identity(compare, cells, p, ref, why)
            r["verdict"] = verdict([r["verdict"], r["reproduces_pilot_" + pn]["verdict"]])
        rep["laterals"][u] = r
        vs.append(r["verdict"])
    rep["S3"] = verdict(vs + (["INCONCLUSIVE"] if rep["pins_failed"] else []))
    return rep


def s4ii():
    rep = {"item": "S4ii", "pins_failed": AP.pins(), "provenance": {}, "july_identity_seed42": {},
           "null_vs_cv": {}}
    compare, cells = AP.xr()
    vs = []
    for u in PANEL_U:
        tag = u.replace(":", "")
        for s in SEEDS:
            name = f"2dc_P_S4U_{tag}_s{s}"
            p = out_of(name)
            ok, bad = (prov(p, PROD_SHA, BASE | {"omnifile": UOMNI, "universe": u, "seed": s, "bootstrap_seed": None,
                                                  "branch_select": "derived", "flux_universe_file": FLUXU})
                       if p else (False, "missing"))
            rep["provenance"][name] = {"ok": ok, "bad": bad}
            vs.append("PASS" if ok else "INCONCLUSIVE")
        ref, why = july(u.replace(":", "_"))
        r = identity(compare, cells, out_of(f"2dc_P_S4U_{tag}_s42"), ref, why)
        rep["july_identity_seed42"][u] = r
        vs.append(r["verdict"])
    for s in SEEDS:
        cvname = "2dc_P_C0_cv" if s == 42 else f"2dc_P_S4CV_s{s}"
        cv = out_of(cvname)
        if s != 42:
            ok, bad = (prov(cv, PROD_SHA, BASE | {"omnifile": CVOMNI, "seed": s, "bootstrap_seed": None,
                                                   "universe": None, "branch_select": "all"})
                       if cv else (False, "missing"))
            rep["provenance"][cvname] = {"ok": ok, "bad": bad}
            vs.append("PASS" if ok else "INCONCLUSIVE")
        r = identity(compare, cells, out_of(f"2dc_P_S4U_NormDISCC0_s{s}"), cv, "CV output missing")
        rep["null_vs_cv"][f"s{s}"] = r
        vs.append(r["verdict"])
    rep["S4ii"] = verdict(vs + (["INCONCLUSIVE"] if rep["pins_failed"] else []))
    return rep


def replicas(item):
    """S1 / S2 / S4(i): provenance of every replica; S1 and S2 also reproduce the pilot's arm replicas 1-20."""
    rep = {"item": item, "pins_failed": AP.pins(), "provenance": {}, "missing": []}
    if item == "S1":
        spec = [(f"2dc_P_S1_{n:03d}", 42, n, "three") for n in range(1, 301)]
    elif item == "S2":
        spec = [(f"2dc_P_S2_{n:03d}", 42, n, "bkg") for n in range(1, 101)]
    else:
        spec = [(f"2dc_P_S4B_s{s}_{n:02d}", s, n, "three") for s in SEEDS[1:] for n in range(1, 21)]
    vs = []
    for name, s, n, st in spec:
        p = out_of(name)
        if p is None:
            rep["missing"].append(name)
            vs.append("INCONCLUSIVE")
            continue
        ok, bad = prov(p, P1_SHA, BASE | {"omnifile": CVOMNI, "seed": s, "bootstrap_seed": n, "universe": None,
                                          "bootstrap_streams": st}, p1=(n, st, False))
        if not ok:
            rep["provenance"][name] = bad
        vs.append("PASS" if ok else "INCONCLUSIVE")
    rep["n_ok"] = vs.count("PASS")
    rep["n_expected"] = len(spec)
    if item in ("S1", "S2"):
        compare, cells = AP.xr()
        arm = "joint" if item == "S1" else "bkg"
        rep["reproduces_pilot"] = {}
        for n in range(1, 21):
            ref, why = pilot_ref(f"2dc_C_P1_{arm}_{n:02d}")
            r = identity(compare, cells, out_of(f"2dc_P_{item}_{n:03d}"), ref, why)
            rep["reproduces_pilot"][f"{arm}_{n:02d}"] = {k: r.get(k) for k in
                                                          ("verdict", "why", "max_rel_diff_cells", "integral_rel_diff")}
            vs.append(r["verdict"])
    rep[item] = verdict(vs + (["INCONCLUSIVE"] if rep["pins_failed"] else []))
    return rep


def main():
    global OUT
    args = sys.argv[1:]
    if "--out-root" in args:
        i = args.index("--out-root")
        OUT = args[i + 1]
        del args[i:i + 2]
    what, outp = args[0], args[1]
    fn = {"c0": c0, "s3": s3, "s4ii": s4ii, "s1": lambda: replicas("S1"), "s2": lambda: replicas("S2"),
          "s4i": lambda: replicas("S4i")}[what]
    rep = fn()
    rep["analyze_prod_sha256"] = sha(__file__)
    rep["out_root"] = OUT
    Path(outp).parent.mkdir(parents=True, exist_ok=True)
    Path(outp).write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n")
    key = {"c0": "C0", "s3": "S3", "s4ii": "S4ii", "s1": "S1", "s2": "S2", "s4i": "S4i"}[what]
    print(json.dumps({key: rep[key], "pins_failed": rep["pins_failed"]}, indent=1))


if __name__ == "__main__":
    main()
