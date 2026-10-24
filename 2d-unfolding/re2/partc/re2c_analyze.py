#!/usr/bin/env python3
"""RE-2 part C copy of stageC/production/analyze_prod.py (f9e0d8f2...), RE2-DECLARATION-C.md §3.1.

  --arm purity (default)  the original, unchanged: it must reproduce Stage C's six item verdicts (K1-roll)
  --arm refined           part B's outputs: pins, a mode guard, and the identities partb_identities.tsv marks X
                          replaced by part B's readout verdicts (k1_core.json, k1_j7.json, pinned)

What the refined arm changes, and nothing else:
  - outputs are read from part B's out/ under their part-B labels (the name map drops "2dc_P_"), and each must match
    its committed SHA256SUMS digest (run/partb_readout/sums/) or it is treated as missing;
  - provenance expects re2_driver.py 38ff3705... (both the unfolds and the replicas), bkg_mode negweight-refined with
    the 400/31 refinement, and the staged input paths the runs recorded. The staged CV and laterals were deleted under
    B9, so they are not re-read: preflight/inputs.stat (pinned) ties each staged path to the CFS original's digest;
  - the identities against XR-L0, the pilot and the July products (AP-09/10/13/15/18) are read from part B's
    readout; Muon_Energy_MINOS:0 and the S3 MINOS0 pilot check have no refined reference and are recorded as such;
  - s2 does not run (J5 was not bound).

The original docstring follows.

Stage C production checks (DESIGN §7): the controls, the identities, the closure and every product's provenance.
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
REPO = HERE.parents[2]
PROD = REPO / "docs" / "orchestration" / "state" / "2d-closeout" / "stageC" / "production"
PILOT = PROD.parent / "pilot"
RE2RUN = REPO / "docs" / "orchestration" / "state" / "2d-closeout" / "stageF" / "methods" / "re2" / "run"


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
SWEEPS_JSON = PROD.parents[1] / "stageB" / "evidence" / "b-genie-truth" / "sweeps.json"
SWEEPS_JSON_SHA = "15b57de9124f204bf3cdf8cd0660c467783bf633bf0d45bfbd4e2506b19be2e4"
PN = f"{AP.D2}/uq/purity_newomni"
BASE = {"iters": 5, "use_weights": True, "estimator": "lgbm", "bkg_mode": "purity"}

# ---- the refined arm (RE2-DECLARATION-C.md §3.1)
ARM = "purity"
NS_R = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb"
DRV_R_SHA = "38ff37055af026bd11b1c12a431b31eed522d5038c1bcf020cd47c374d2ddf7c"   # re2_driver.py at dbdad2f9
BASE_R = {"iters": 5, "use_weights": True, "estimator": "lgbm", "bkg_mode": "negweight-refined",
          "refine_n_estimators": 400, "refine_num_leaves": 31}
CVOMNI_R = f"{NS_R}/inputs/runEventLoopOmniFold_MEFHC.root"
ACT_R = f"{NS_R}/inputs/laterals"
SUMS_R = RE2RUN / "partb_readout" / "sums"
K1_R = {"core": (RE2RUN / "partb_readout" / "k1_core.json",
                 "7c407e958e5247f76f4eebdf7caa0dbeff504e13d22da6ed92b41ae1e669d86a"),
        "j7": (RE2RUN / "partb_readout" / "k1_j7.json",
               "faa4656d9fb4b38bbc5734bd5fa613ddd09ac6e56b266fd0d40a732d64a1c3b8")}
STAGED_R = (RE2RUN / "partb_readout" / "preflight" / "inputs.stat",
            "89595b3e6c4ee3dddc77841ef53ef78b7f71aa488bdf8dfb2ca02254173da0fc")
CFS_SHA = {"CV": "43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df"}   # = PIN cv_omnifile_cfs
CFS_LAT_SUMS = (f"{ACT}/SHA256SUMS", "73775251f377a35b86c5d9433d1db63d65267525b9261f773064a1e9d17764f6")  # re2b_env.sh
NO_REF = {"verdict": "NO REFINED REFERENCE", "why": "no refined product reproduces this purity reference "
                                                    "(RE2-DECLARATION-B.md §5.1); not part of the item verdict"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def out_of(name):
    if ARM == "refined":
        return out_of_refined(name)
    p = Path(OUT, name, "xsec.root")
    return p if p.is_file() else None


_SUMS = {}


def out_of_refined(name):
    """A part-B output by its Stage C name, only if its sha256 equals the committed part-B digest."""
    if not _SUMS:
        for f in sorted(SUMS_R.glob("SHA256SUMS.J*")):
            for ln in f.read_text().splitlines():
                d, rel = ln.split()
                _SUMS[rel] = d
    label = name[len("2dc_P_"):] if name.startswith("2dc_P_") else name
    p = Path(NS_R, "out", label, "xsec.root")
    want = _SUMS.get(f"{label}/xsec.root")
    return p if want and p.is_file() and sha(p) == want else None


def k1(which):
    """{check id: verdict} from part B's pinned readout; {} if its digest or set verdict is wrong."""
    p, want = K1_R[which]
    if not p.is_file() or sha(p) != want:
        return {}
    d = json.loads(p.read_text())
    if d.get("verdict") != "PASS":
        return {}
    return {c["id"]: c["verdict"] for c in d["checks"]}


def k1_rows(which, ids):
    """The readout rows `ids` as identity-like records; a missing row is INCONCLUSIVE."""
    v = k1(which)
    return {i: {"verdict": v.get(i, "INCONCLUSIVE"), "source": f"{K1_R[which][0].name} {K1_R[which][1][:8]}"}
            for i in ids}


def staged_ok():
    """Each staged path is tied to its CFS original by the pinned DTN record, not by re-reading the deleted copy: its
    recorded sha256 must be the CFS file's (the CV's is pinned here; each lateral's must equal its row of the CFS
    SHA256SUMS, whose own digest is pinned, as the DTN preflight checked)."""
    p, want = STAGED_R
    if not p.is_file() or sha(p) != want:
        return False, "preflight/inputs.stat digest mismatch"
    rows = {ln.split()[4]: ln.split()[0] for ln in p.read_text().splitlines()}
    if rows.get(CVOMNI_R) != CFS_SHA["CV"]:
        return False, "staged CV digest is not the CFS CV's"
    lat = sorted(k for k in rows if k.startswith(ACT_R + "/"))
    if len(lat) != 10:
        return False, f"{len(lat)} staged laterals recorded, 10 expected"
    q, qwant = CFS_LAT_SUMS
    if not Path(q).is_file() or sha(q) != qwant:
        return False, "CFS lateral SHA256SUMS digest mismatch"
    cfs = {ln.split()[1]: ln.split()[0] for ln in Path(q).read_text().splitlines() if ln.strip()}
    bad = [k for k in lat if cfs.get(Path(k).name) != rows[k]]
    if bad:
        return False, f"staged lateral digests differ from the CFS SHA256SUMS rows: {bad}"
    return True, {"cv": rows[CVOMNI_R], "laterals": {k: rows[k] for k in lat}}


def prov(p, driver_sha, want, p1=None):
    """Provenance: driver and helper digests, runConfig keys, and (driver_p1 runs) the p1Streams record."""
    if ARM == "refined":   # one driver makes every part-B output; the mode guard is the refined BASE
        driver_sha = DRV_R_SHA
        want = {**want, **{k: v for k, v in BASE_R.items()}}
        if want.get("omnifile") == CVOMNI:
            want["omnifile"] = CVOMNI_R
        elif str(want.get("omnifile", "")).startswith(ACT + "/"):
            want["omnifile"] = ACT_R + want["omnifile"][len(ACT):]
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
    if ARM == "refined":   # AP-09/10 (X): PB-unit, PB-unit-J0; PB-ER-rep, PB-ER-D2, PB-ER-J0, PB-ER-eff
        e = out_of("ER")
        pe = prov(e, PROD_SHA, BASE | {"omnifile": CVOMNI, "seed": 42, "bootstrap_seed": None, "universe": None,
                                       "branch_select": "all"}) if e else (False, "missing")
        rows = k1_rows("core", ["PB-unit", "PB-unit-J0", "PB-ER-rep", "PB-ER-D2", "PB-ER-J0", "PB-ER-eff"])
        st = staged_ok()
        rep["staged_inputs"] = {"ok": st[0], "record": st[1]}
        rep["unit_readout"] = {"verdict": verdict(rows[i]["verdict"] for i in ("PB-unit", "PB-unit-J0")),
                               "rows": {i: rows[i] for i in ("PB-unit", "PB-unit-J0")},
                               "provenance_ok": pu[0] and st[0], "provenance_bad": pu[1]}
        rep["cv_readout"] = {"verdict": verdict(rows[i]["verdict"] for i in ("PB-ER-rep", "PB-ER-D2", "PB-ER-J0",
                                                                          "PB-ER-eff")),
                             "rows": {i: rows[i] for i in ("PB-ER-rep", "PB-ER-D2", "PB-ER-J0", "PB-ER-eff")},
                             "provenance_ok": pc[0] and pe[0] and st[0],
                             "provenance_bad": {"C0_cv": pc[1], "ER": pe[1]}}
        keys = ("unit_readout", "cv_readout")
    else:
        rep["unit_vs_L0"] = identity(compare, cells, u, l0) | {"provenance_ok": pu[0], "provenance_bad": pu[1]}
        rep["cv_vs_L0"] = identity(compare, cells, c, l0) | {"provenance_ok": pc[0], "provenance_bad": pc[1]}
        keys = ("unit_vs_L0", "cv_vs_L0")
    vs = []
    for k in keys:
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
    if ARM == "refined":   # the laterals' staged copies, tied to the CFS digests (gap 2)
        st = staged_ok()
        rep["staged_inputs"] = {"ok": st[0], "record": st[1]}
        vs.append("PASS" if st[0] else "INCONCLUSIVE")
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
            ctitle = h.GetTitle()
            cfull = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                              for i in range(1, h.GetNbinsX() + 1)]).ravel()
            src = tf.Get("hEffDenSource")
            src = src.GetTitle() if src else ""
            hd = tf.Get("hOFTruthDenom2D")
            den = float(hd.Integral()) if hd else 0.0
            tf.Close()
            cc = cfull[np.array(cells)]
            dev = float(np.max(np.abs(cc - 1)))
            # Not vacuous: without mc_truth_denom the driver writes c = 1 by fiat, titled "Completeness = 1 (closure /
            # fallback)", and clones it into hOFTruthDenom2D (driver :2276-2289). The closure is read only from the
            # measured ratio: its title, the canonical Truth-tree denominator, and a non-empty denominator.
            real = (ctitle.startswith("OmniFold input completeness") and src.startswith("mc_truth_denom")
                    and den > 0)
            r.update({"provenance_ok": ok, "provenance_bad": bad, "closure_max_abs_c_minus_1": dev,
                      "closure_denominator": {"hOFCompleteness2D_title": ctitle, "hEffDenSource": src,
                                              "hOFTruthDenom2D_integral": den},
                      "closure": ("PASS" if dev <= CLOSURE_TOL else "FAIL") if real else "INCONCLUSIVE",
                      "sha256": sha(p)})
            r["verdict"] = ("INCONCLUSIVE" if not ok and r["closure"] != "FAIL" else r["closure"])
        if ARM == "refined" and u == "BeamAngleX_0":   # AP-13 (X): PB-J0-S3_BeamAngleX0
            r["reproduces_j0"] = k1_rows("core", ["PB-J0-S3_BeamAngleX0"])["PB-J0-S3_BeamAngleX0"]
            r["verdict"] = verdict([r["verdict"], r["reproduces_j0"]["verdict"]])
        elif ARM == "refined" and u == "Muon_Energy_MINOS_0":
            r["reproduces_pilot_2dc_C_P3_MINOS0"] = NO_REF
        elif u in ("BeamAngleX_0", "Muon_Energy_MINOS_0"):
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
        if ARM == "refined":   # AP-15 (X): PB-panel-<u> against J2's universe; none for Muon_Energy_MINOS:0
            if u == "Muon_Energy_MINOS:0":
                rep["july_identity_seed42"][u] = NO_REF
                continue
            i = "PB-panel-" + u.replace(":", "_")
            r = k1_rows("j7", [i])[i]
            rep["july_identity_seed42"][u] = r
            vs.append(r["verdict"])
            continue
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
    if ARM == "refined":   # AP-18 (X): PB-J0-S1_001-008, and PB-stream-* for every refined replica
        ids = ([f"PB-J0-S1_{n:03d}" for n in range(1, 9)] + [f"PB-stream-S1_{n:03d}" for n in range(1, 301)]
               if item == "S1" else [f"PB-stream-S4B_s{s}_{n:02d}" for s in SEEDS[1:] for n in range(1, 21)])
        rows = k1_rows("core", ids)
        rep["readout_rows"] = {"n": len(ids), "n_pass": sum(r["verdict"] == "PASS" for r in rows.values()),
                               "not_pass": {i: r for i, r in rows.items() if r["verdict"] != "PASS"}}
        vs += [r["verdict"] for r in rows.values()]
    elif item in ("S1", "S2"):
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
    global OUT, ARM
    args = sys.argv[1:]
    if "--arm" in args:
        i = args.index("--arm")
        ARM = args[i + 1]
        del args[i:i + 2]
        if ARM not in ("purity", "refined"):
            raise SystemExit(f"--arm {ARM}: purity or refined")
    if ARM == "refined" and "--out-root" in args:
        raise SystemExit("--out-root is purity-only; the refined arm reads part B's out/ by its committed digests")
    if ARM == "refined" and args[:1] == ["s2"]:
        raise SystemExit("s2 is not run in the refined arm: J5 was not bound (RE2-BINDING-B)")
    if "--out-root" in args:
        i = args.index("--out-root")
        OUT = args[i + 1]
        del args[i:i + 2]
    what, outp = args[0], args[1]
    fn = {"c0": c0, "s3": s3, "s4ii": s4ii, "s1": lambda: replicas("S1"), "s2": lambda: replicas("S2"),
          "s4i": lambda: replicas("S4i")}[what]
    rep = fn()
    rep["analyze_prod_sha256"] = sha(__file__)
    rep["arm"] = ARM
    rep["out_root"] = OUT if ARM == "purity" else f"{NS_R}/out"
    Path(outp).parent.mkdir(parents=True, exist_ok=True)
    Path(outp).write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n")
    key = {"c0": "C0", "s3": "S3", "s4ii": "S4ii", "s1": "S1", "s2": "S2", "s4i": "S4i"}[what]
    print(json.dumps({key: rep[key], "pins_failed": rep["pins_failed"]}, indent=1))


if __name__ == "__main__":
    main()
