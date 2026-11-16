#!/usr/bin/env python3
"""Synthetic test of t2a_split.py on the REAL committed blocks_<T>.npz with a SYNTHETIC E (not the toys).

The fake score record holds grade fields computed from the synthetic E. The fake null record is
fd_1b_null.null_contents at the module's own seed and chunking with n_mc = N_TEST, the bound function itself, so A3
(rebuilt q equals the record's within se) also checks that the script's one-pass loop consumes exactly the bound
null's draw stream: the rebuilt q must equal the record's EXACTLY. The pins are overridden on the imported module only.
Run: python3 -I test_t2a_split.py <code dir: git archive of b1d56e4f> <blocks_AR23.npz>
"""
import hashlib, importlib.util, json, sys, tempfile
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
CODE, BLOCKS = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
N_TEST = 200_000
for p in (CODE / "nd-unfolding", CODE / "2d-unfolding" / "cov2d"):
    sys.path.insert(0, str(p))
import cov2d as c, cov2d_null as cn, fd_1b_null as nl  # noqa: E401,E402

B = np.load(BLOCKS, allow_pickle=False)
C = B["C_T"]
sigma = np.sqrt(np.diag(C))
bands = {k[len("band__"):]: B[k] for k in B.files if k.startswith("band__")}
laws = cn.laws_at_T(bands, B["minos_x"], B["w_flux"])
gauss = B["C_stat"] + B["C_norm"] + B["C08"] + B["C_model_abs"]
NULL = nl.null_contents(laws, gauss, C, n_mc=N_TEST, seed=c.NULL_SEED)


def build(td: Path, defect=None):
    rng = np.random.default_rng(5)
    E = nl.simulate(laws, gauss, 300, rng) + 0.4 * sigma * rng.normal(size=205)
    seeds = np.array(list(c.TOY_SEEDS["AR23"]), np.int64)
    if defect == "seeds":
        seeds = seeds[::-1].copy()
    np.savez(td / "E_AR23.npz", E=E, seeds=seeds, truth=np.array("AR23"), M=np.array("m"))
    chi2, ndf = nl.chi2_nonnull(E, C)
    Zc = E / sigma
    g = {"ndf": ndf, "chi2_mean_over_ndf": float(chi2.mean() / ndf), "pull_mean": Zc.mean(0).tolist(),
         "pull_sd": Zc.std(0, ddof=1).tolist(), "counts": [int(x) for x in np.sum(np.abs(E) <= sigma, 0)]}
    if defect == "chi2":
        g["chi2_mean_over_ndf"] *= 1 + 1e-2
    if defect == "counts":
        g["counts"][7] += 1
    (td / "score.json").write_text(json.dumps({"grade": g}))
    null = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in NULL.items()}
    if defect == "nullq":
        null["q_joint"] += 3 * null["se_joint"]
    (td / "null.json").write_text(json.dumps({"null": null}))
    e_sha = hashlib.sha256((td / "E_AR23.npz").read_bytes()).hexdigest()
    cap = {"truth": "AR23", "status": "OK", "A0": {"equal": True}, "e_npz_sha256": e_sha if defect != "capsha" else "0" * 64}
    (td / "capture.json").write_text(json.dumps(cap))


def run(defect=None):
    with tempfile.TemporaryDirectory() as t:
        td = Path(t)
        build(td, defect)
        spec = importlib.util.spec_from_file_location("t2a_split", HERE / "t2a_split.py")
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.PINS = {"AR23": {k: hashlib.sha256((td / f).read_bytes()).hexdigest() if f != "blocks" else hashlib.sha256(BLOCKS.read_bytes()).hexdigest()
                           for k, f in (("blocks", "blocks"), ("score", "score.json"), ("null", "null.json"), ("capture", "capture.json"))}}
        m.N_MC = N_TEST
        m.A1_CHI2_TOL = "A5"
        out = td / "t2a_AR23.json"
        rc = m.main(["--truth", "AR23", "--e-npz", str(td / "E_AR23.npz"), "--capture", str(td / "capture.json"),
                     "--blocks", str(BLOCKS), "--score", str(td / "score.json"), "--null", str(td / "null.json"),
                     "--code", str(CODE), "--out", str(out), "--fig", str(td / "fig.png")])
        rec = json.loads((out if rc == 0 else td / "t2a_AR23.STOP.json").read_text())
        return rc, rec, (td / "fig.png").exists()


cases = {None: (0, []), "chi2": (8, ["A1"]), "counts": (8, ["A1"]), "seeds": (8, ["A4"]), "nullq": (8, ["A3"]),
         "capsha": (8, ["E_npz is the capture's, and the capture is OK with A0 equal"])}
bad = 0
for d, (want_rc, want_failed) in cases.items():
    rc, rec, fig = run(d)
    failed = [k for k, v in rec["controls"].items() if not v["pass"]]
    ok = rc == want_rc and failed == want_failed
    extra = ""
    if d is None and rc == 0:
        a3 = rec["controls"]["A3"]["detail"]
        ok &= a3["q_joint_rebuilt"] == NULL["q_joint"]            # the same draw stream: exactly equal
        s = rec["split"]
        ok &= abs(s["ebar_Cplus_ebar"] + s["trace_Cplus_S"] - s["mean_chi2"]) <= 1e-12 * s["mean_chi2"]
        ok &= set(rec["truncated"]) == {"73", "139"} and fig
        ok &= len(rec["by_rank"]["b_k"]) == rec["split"]["ndf"]
        pr = rec["precision"]
        ok &= pr["ndf_evr"] == rec["split"]["ndf"] and set(pr["truncated_counts"]) == {"73", "139"} and len(pr["d_k"]) == rec["split"]["ndf"]
        extra_p = f" precision: max d {pr['max_d']:.2e}, unresolved {pr['n_unresolved']}, counts agree {[v['agree'] for v in pr['truncated_counts'].values()]}"
        extra = extra_p + f" q_rebuilt==q_record:{a3['q_joint_rebuilt'] == NULL['q_joint']} fig:{fig} C_T counts {rec['C_T_counts']['above_1e-4']},{rec['C_T_counts']['above_1e-6']}"
    print(f"{'PASS' if ok else 'FAIL'} defect={d} rc={rc} failed={failed}{extra}")
    bad += not ok
print("ALL PASS" if not bad else f"{bad} FAILED")
sys.exit(1 if bad else 0)
