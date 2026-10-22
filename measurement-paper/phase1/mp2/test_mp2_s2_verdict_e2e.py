"""TEST ONLY (not a study output): mp2_s2_fit.py models + gates, then mp2_s2_verdict.py, end to end on synthetic harmonize outputs.
argv: CODE WORK NCELLS. NCELLS = 0: 3 fine cells in each of the 109 J cells (the full path, then tampered weights, a tampered seal and an overwrite, each refused); NCELLS = 100: random cells (the blind ndf stop, exit 5).
The frozen PARAMS are overridden here to 60 trees / early stop 20 so the test is fast; production never imports this."""
import json
import os
import sys
from pathlib import Path

import numpy as np

CODE, WORK = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(CODE))
import mp2_s2_fit as F  # noqa: E402
import s5p_stage1_inspect as s1  # noqa: E402

F.PARAMS = dict(F.PARAMS, n_estimators=60)
F.EARLY_STOP = 20
F.LOGLOSS_CHECKPOINTS = (10, 30, 60)
F.V1_CAP_REPORT, F.V1_DESCRIPTIVE_MAX = 50, 120
rng = np.random.default_rng(7)
nf = int(np.prod(s1.fine_shape()))
harm = WORK / "harm"
harm.mkdir(parents=True, exist_ok=True)
nT, nG = 60000, 20000
gen = "gibuu_ch"
NC = int(sys.argv[3])
S5C = "/pscratch/sd/j/josephrb/measurement-paper/phase1/mp5/inputs/s5c_contract.json"
if NC > 0:                     # random cells: J cells left empty (the blind-stop case uses NC = 100)
    cells = np.sort(rng.choice(nf, NC, replace=False))
else:                          # 3 fine cells in every supported J cell, so all 109 J pulls are finite
    cm, nc_ = s1.coarse_map(s1.J_EDGES, json.loads(Path(S5C).read_text())["measurement"]["partition_J"]["supported_cells"])
    cells = np.sort(np.concatenate([rng.choice(np.nonzero(cm == j)[0], 3, replace=False) for j in range(nc_)]))
NC = cells.size
fine_T = cells[rng.integers(0, NC, nT)]
fine_G = cells[rng.integers(0, NC, nG)]
feats = F.F_PRIMARY
tz = {f: rng.normal(size=nT) for f in feats}
tz["enu"] = rng.uniform(0, 30, nT)                       # some rows outside GiBUU's 0-20 support
tz.update(w_truth=rng.uniform(0.5, 1.5, nT), tgt=rng.choice([1, 6], nT), fine=fine_T,
          i=np.sort(rng.choice(F.N_MCGEN, nT, replace=False)))
for k in ("v3_n_mult_KE10", "v3_p_mult_KE20", "v3_pi0_count"):
    tz[k] = rng.integers(0, 12, nT).astype(float)
nn = rng.integers(0, 3, nT)
tz["nKE_ev"] = np.repeat(np.arange(nT), nn)
tz["nKE_val"] = rng.exponential(100, tz["nKE_ev"].size)
np.savez(harm / "tune_CH.npz", **tz)
ev = {f: rng.normal(size=nG) + (0.3 if f == "pt" else 0.0) for f in feats}
ev.update(c=rng.uniform(0.5, 1.5, nG), tgt=rng.choice([0, 1, 6], nG, p=[0.01, 0.05, 0.94]), j=np.arange(nG) * 3, fine=fine_G)
for k in ("v3_n_mult_KE10", "v3_p_mult_KE20", "v3_pi0_count"):
    ev[k] = rng.integers(0, 12, nG).astype(float)
gn = rng.integers(0, 3, nG)
ev["nKE_ev"] = np.repeat(np.arange(nG), gn)
ev["nKE_val"] = rng.exponential(100, ev["nKE_ev"].size)
np.savez(harm / f"events_{gen}.npz", **ev)
x = np.bincount(fine_G, ev["c"], nf) * 1e-40
np.savez(harm / f"harmonized_{gen}.npz", xsec_flat=x, sumw2_flat=x * 1e-40, nevt_flat=np.bincount(fine_G, None, nf).astype(float))
rho = rng.uniform(0.5, 2.0, nf)
np.savez_compressed(harm / f"rho_an_{gen}.npz", rho=rho)
(harm / f"hybrid_an_{gen}.json").write_text(json.dumps({"rho_npz": {"path": str(harm / f"rho_an_{gen}.npz"), "sha256": F.sha256(harm / f"rho_an_{gen}.npz")}}))
(harm / "s2_harmonize.json").write_text(json.dumps({"outputs": {f"harmonized_{gen}.npz": F.sha256(harm / f"harmonized_{gen}.npz")}}))
out = WORK / "fit"
fc = str(CODE / "feature_contract_draft.json")
tasks = ",".join(f"{k}:{h}:{f}" for k in range(5) for h in range(2) for f in range(5))
assert F.main(["models", "--gen", gen, "--fset", "primary", "--tasks", tasks, "--harm", str(harm), "--fcontract", fc,
               "--out", str(out), "--threads", "8"]) == 0
rc = F.main(["gates", "--gen", gen, "--fset", "primary", "--harm", str(harm), "--fcontract", fc, "--out", str(out),
             "--threads", "8", "--contract", "/pscratch/sd/j/josephrb/measurement-paper/phase1/mp5/inputs/s5c_contract.json"])
g = json.loads((out / f"gates_{gen}_primary.json").read_text())
sp = Path(g["V2_V3"]["sealed_file"])
print("TEST gates rc", rc, json.dumps(g["verdict"]))
import mp2_s2_verdict as V  # noqa: E402
import shutil  # noqa: E402
VA = ["--gen", gen, "--fset", "primary", "--harm", str(harm), "--contract", S5C]
print("TEST blind-only rc", V.main(VA + ["--fit", str(out), "--blind-only"]), "verdict file written:", (out / f"verdict_v2v3_{gen}_primary.json").exists())
rcv = V.main(VA + ["--fit", str(out)])
print("TEST verdict rc", rcv)


def variant(name):
    """A copy of the fit directory whose gates file points at its own seal, with no verdict file."""
    t = WORK / f"fit_{name}"
    shutil.copytree(out, t)
    vf = t / f"verdict_v2v3_{gen}_primary.json"
    if vf.exists():
        vf.chmod(0o644)
        vf.unlink()
    gj = json.loads((t / f"gates_{gen}_primary.json").read_text())
    gj["V2_V3"]["sealed_file"] = str(t / Path(gj["V2_V3"]["sealed_file"]).name)
    (t / f"gates_{gen}_primary.json").write_text(json.dumps(gj))
    return t, gj


def expect_stop(label, fit_dir):
    try:
        V.main(VA + ["--fit", str(fit_dir)])
    except SystemExit as e:
        ok = str(e).startswith("STOP") or str(e).startswith("refusing")
        print(f"TEST {label}: {'refused' if ok else 'UNEXPECTED EXIT'}: {e}")
        return
    print(f"TEST FAIL: {label} was accepted")


if rcv == 0:
    vd = json.loads((out / f"verdict_v2v3_{gen}_primary.json").read_text())
    print("TEST verdict", json.dumps(vd["verdict"]), "blind", vd["blind"], "corr", vd["J_pull_correlation_across_replicas"])
    r0 = vd["replicas"]["0"]
    print("TEST r0 V2_J", r0["V2_J"]["n_pulls"], "V3 p_d", {k: round(x["p_d"], 4) for k, x in r0["V3"]["distributions"].items()},
          "fail_closed", r0["V3"]["fail_closed"])
    print("TEST V3-n variance tag", r0["V3_statistics"]["neutron_KE_MeV"]["variance"],
          "| seal stat unchanged", {k: v for k, v in vd["sealed"]["stat_before"].items() if k != "atime_ns"}
          == {k: v for k, v in vd["sealed"]["stat_after"].items() if k != "atime_ns"},
          "| files hashed", sorted(vd["inputs"]["sha256_of_files_loaded"]))
    print("TEST output mode", oct((out / f"verdict_v2v3_{gen}_primary.json").stat().st_mode & 0o777))
    expect_stop("second run (overwrite)", out)
    # the overwrite refusal comes before the seal is opened: an unreadable seal is never reached
    t0, gj0 = variant("overwrite_first")
    (t0 / f"verdict_v2v3_{gen}_primary.json").write_text("{}")
    Path(gj0["V2_V3"]["sealed_file"]).chmod(0o000)
    expect_stop("overwrite checked before the (unreadable) seal", t0)
    Path(gj0["V2_V3"]["sealed_file"]).chmod(0o400)
    t2, _ = variant("tamper_w")
    wz = dict(np.load(t2 / f"weights_{gen}_primary.npz"))
    wz["wG_k3"] = wz["wG_k3"] * (1 + 1e-6 * rng.normal(size=wz["wG_k3"].size))
    np.savez(t2 / f"weights_{gen}_primary.npz", **wz)
    expect_stop("weights perturbed 1e-6", t2)
    t4, _ = variant("nan_w")
    wz = dict(np.load(t4 / f"weights_{gen}_primary.npz"))
    wz["wG_k1"] = wz["wG_k1"].copy()
    wz["wG_k1"][7] = np.nan
    np.savez(t4 / f"weights_{gen}_primary.npz", **wz)
    expect_stop("a NaN weight", t4)
    t3, gj3 = variant("tamper_s")
    sp3 = Path(gj3["V2_V3"]["sealed_file"])
    sp3.chmod(0o600)
    sp3.write_text(sp3.read_text().replace('"ndf"', '"ndf" ', 1))
    expect_stop("a one-byte edit to the seal", t3)
    # a NaN planted in each statistic, through chi2_shape: per replica the calls are fine, the 4 frozen V3, then V3-n
    real = V.F.chi2_shape
    for label, call, fields in (("V2-fine chi2", 0, ("chi2", "chi2_ndf")), ("frozen V3 chi2", 1, ("chi2",)),
                                ("frozen V3 z_max", 2, ("max_abs_pull_used",)), ("V3-n chi2", 5, ("chi2",)),
                                ("V3-n z_max", 5, ("max_abs_pull_used",))):
        n = {"i": 0}

        def poisoned(*a, **k):
            r = real(*a, **k)
            if n["i"] == call:
                r = dict(r, **{f: float("nan") for f in fields})
            n["i"] += 1
            return r
        V.F.chi2_shape = poisoned
        tn, _ = variant("nan_" + label.replace(" ", "_").replace("-", "").replace("/", ""))
        expect_stop(f"NaN in {label}", tn)
        V.F.chi2_shape = real
