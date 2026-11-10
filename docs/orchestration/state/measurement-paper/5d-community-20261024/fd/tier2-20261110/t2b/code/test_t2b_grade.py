#!/usr/bin/env python3
"""Synthetic test of t2b_grade.py: fabricated S1, C_model, C_resp, tables, readouts and data product, built so that
every control should pass; then one defect per case must STOP with the named control. The pins are overridden on the
imported module (the script itself has no test switch). Run: python3 -I test_t2b_grade.py <regrade nd-unfolding dir>"""
import hashlib, json, sys, tempfile, importlib.util
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ND = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ND))
import fd_f0_regrade as fr  # noqa: E402

spec = importlib.util.spec_from_file_location("t2b_grade", HERE / "t2b_grade.py")


def build(root: Path, defect=None):
    rng = np.random.default_rng(3)
    files, repo = root / "files", root / "repo"
    files.mkdir(); D = repo / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
    (D / "readout").mkdir(parents=True); (D / "data-product").mkdir(parents=True)
    f = rng.uniform(1, 2, 16) * 1e-39
    ff = np.outer(f, f)
    A = rng.normal(size=(16, 16)) * 0.03
    stat = (A @ A.T + 1e-4 * np.eye(16)) * ff
    if defect == "stat_rank":
        v = rng.normal(size=16); stat = np.outer(v, v) * ff
    other = np.outer(rng.normal(size=16) * 0.02 * f, rng.normal(size=16) * 0.02 * f); other = (other + other.T) / 2 + np.outer(0.03 * f, 0.03 * f)
    seed = np.zeros((16, 16)) if defect != "seed" else 1e-6 * ff
    blocks = {"stat": stat, "seed": seed, "lat:BeamAngleX": np.outer(0.01 * f, 0.01 * f), "normalization": other}
    if defect == "stat_rank":          # keep C_e full rank so only C_stat,rel is deficient
        blocks["interaction"] = 1e-3 * np.eye(16) * ff
    Ce = sum(blocks.values())
    S = rng.normal(size=(3, 16)) * 0.04
    Cmf = S.T @ S; Cma = Cmf * ff; Ct = Ce + Cma
    meta = json.dumps({"blocks": list(blocks)})
    arrs = {"meta": np.array(meta), "f": f, "C_e": Ce, "C_total": Ct, "C_model_frac": Cmf, "C_model_abs": Cma}
    arrs.update({"C_" + k.replace(":", "_"): v for k, v in blocks.items()})
    np.savez(files / "s1_assembly.npz", **arrs)
    np.savez(files / "cmodel_5d.npz", S=S)
    B = rng.normal(size=(16, 16)) * 0.02
    Cx = (B @ B.T) * ff
    np.savez(files / "cresp.npz", C_resp=Cx)
    real = json.loads((Path(__file__).resolve().parents[1] / "../t2scope/data/fd_f1_readout.json").resolve().read_text())
    truths, table = [], {}
    for t in real["truths"]:
        if not t["graded"]:
            continue
        n = t["name"]
        R = rng.normal(size=(1 if t["row"] in (3, 8) else t["n_experiments"], 16)) * 0.05 + 0.01
        table["r_" + n] = R
        if t["row"] in (3, 8):
            b, N = R[0], np.zeros((16, 16))
        else:
            b, N, _ = fr.unweighted(R)
        M0 = fr.leave_out(Ce / ff, S, t["own_vertex"]) + Cx / ff
        g = fr.grade(b, N, M0)
        if defect == "grade" and n == "W2":
            g["chi2"] *= 1 + 1e-9
        bias = b.tolist()
        if defect == "bias" and n == "F1_genie_v3_ar23":
            bias[3] += 1e-6
        truths.append({"name": n, "row": t["row"], "group": t["group"], "own_vertex": t["own_vertex"], "graded": True,
                       "n_experiments": t["n_experiments"], "bias": bias, "noise_sigma": np.sqrt(np.diag(N)).tolist(),
                       "grade": g, "grade_matrix": t.get("grade_matrix")})
    if defect == "f0b_fallback":
        # the F1 table lacks W1; the F0b table carries it
        f0b = {"r_W1": table.pop("r_W1")}
        np.savez(files / "fd_f0b_experiments.npz", **f0b)
    else:
        np.savez(files / "fd_f0b_experiments.npz", r_nominal=table["r_nominal"])
    np.savez(files / "fd_f1_experiments.npz", **table)
    (D / "readout/fd_f1_readout.json").write_text(json.dumps({"truths": truths}))
    (D / "readout/fd_f0b_readout.json").write_text("{}")
    dpf = f.copy()
    if defect == "dp":
        dpf[0] *= 1 + 1e-9
    (D / "data-product/fd_data_product.json").write_text(json.dumps({"f": dpf.tolist(), "matrices": {"C_e": Ce.tolist(), "C_resp": Cx.tolist()}}))
    return files, repo


def run(defect=None):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        files, repo = build(root, defect)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.FETCHED = {n: hashlib.sha256((files / n).read_bytes()).hexdigest() for n in m.FETCHED}
        m.COMMITTED = {p: hashlib.sha256((repo / p).read_bytes()).hexdigest() for p in m.COMMITTED}
        m.REGRADE_SHA = hashlib.sha256((ND / "fd_f0_regrade.py").read_bytes()).hexdigest()
        out = root / "t2b.json"
        rc = m.main(["--files", str(files), "--regrade-nd", str(ND), "--repo", str(repo), "--out", str(out)])
        p = out if rc == 0 else root / "t2b.STOP.json"
        return rc, json.loads(p.read_text())


cases = {"stat_rank": (8, ["B0"]), None: (0, []), "f0b_fallback": (0, []), "seed": (0, []), "bias": (8, ["B1"]), "grade": (8, ["B2"]),
         "dp": (8, ["B3"])}
bad = 0
for d, (want_rc, want_failed) in cases.items():
    rc, rec = run(d)
    failed = [k for k, v in rec["controls"].items() if not v["pass"]]
    ok = rc == want_rc and failed == want_failed
    extra = ""
    if d is None and rc == 0:
        r = rec["records"]
        ok &= len(r) == 16 and all(set(x) >= {"existing", "M1", "M2", "M3"} for x in r.values())
        ok &= all(abs(r[n]["existing"]["chi2"] - r[n]["existing"]["chi2"]) == 0 for n in r)
        extra = f" records={len(r)} M2 chi2(nominal)={r['nominal']['M2']['chi2']:.3f}"
    if d == "seed" and rc == 0:
        ok &= rec["seed_block"]["max_abs_relative"] > 0
    if d is None and rc == 0:
        ok &= rec["seed_block"]["max_abs_relative"] == 0
    if d == "f0b_fallback" and rc == 0:
        ok &= rec["controls"]["B1"]["detail"]["W1"]["table"] == "fd_f0b_experiments.npz"
    print(f"{'PASS' if ok else 'FAIL'} defect={d} rc={rc} failed={failed}{extra}")
    bad += not ok
print("ALL PASS" if not bad else f"{bad} FAILED")
sys.exit(1 if bad else 0)
