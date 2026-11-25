#!/usr/bin/env python3
"""EVW5D's tests (EVW5D-DECLARATION.md section 5), run off the cluster against a real deploy at CODE_PIN.

    EVW5D_REPO=<a local clone of the repository> python3 -m pytest -q test_evw5d.py

The session builds, in a new temporary directory, a shared clone of the repository at CODE_PIN (the producer's code),
synthetic inputs on the real fine grid (with truth rows on the top edges and outside the grid), the reference product
made by the deploy's own s5p_numerics.py, and a fixture main commit carrying the synthetic data product, as
nd-unfolding/ess_e/test_ess_capture.py does (its helpers are reused). It then runs evw5d.py end to end: PASS, STOP
(a reference one ulp away), a wrong pin, an existing --out and --fixture inside Slurm. The control functions are also
tested in-process with one fault injected at a time, each fault one that the end-to-end exactness gates would not see.

C-COL runs the deploy's driver on two grids that share their outer edges and differ in every interior edge, and
requires the push weights to be bit for bit equal, and grid B's result to equal grid A's saved weights re-histogrammed
on grid B. ``EVW5D_DIR`` points the suite at another copy of the evw5d directory (the mutation campaign).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

import numpy as np
import pytest

EVW = Path(os.environ.get("EVW5D_DIR", Path(__file__).resolve().parent)).resolve()
ESS_DIR = EVW.parent / "ess_e"
REPO = Path(os.environ.get("EVW5D_REPO", Path(__file__).resolve().parents[2])).resolve()


def _import(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ev = _import("evw5d", EVW / "evw5d.py")
sys.path.insert(0, str(ESS_DIR))
tec = _import("test_ess_capture", ESS_DIR / "test_ess_capture.py")
ec = ev.ess
PY = sys.executable


# ----------------------------------------------------------------------------------------------- the world


def synthetic(deploy: Path, prot: Path, edges=None, tag="", n_mc=6000, n_data=4000, n_bkg=400, seed=20261125):
    """ESS's synthetic inputs, plus truth rows on the top pT and p|| edges and rows outside the grid."""
    sys.path.insert(0, str(deploy / "nd-unfolding"))
    import s5p_stage1_inspect as s1
    rng = np.random.default_rng(seed)
    fine = [np.asarray(s1.FINE[a], float) for a in s1.AXES]
    edges = fine if edges is None else edges

    def coords(n, shift=0.0):
        return np.column_stack([rng.uniform(0.0, 1.6, n), rng.uniform(1.5, 10.0, n) + shift,
                                rng.uniform(0.0, 2.2, n), rng.uniform(0.0, 4.0, n),
                                rng.uniform(0.5, 3.2, n)]).astype(np.float32)

    gen = coords(n_mc)
    gen[0, 0], gen[1, 0], gen[2, 1], gen[3, 4], gen[4, 2] = 4.5, 5.0, 60.0, 150.0, 0.1   # top edges, outside, an edge
    reco = (gen * rng.normal(1.0, 0.05, gen.shape)).astype(np.float32)
    pass_truth = rng.random(n_mc) < 0.97
    pass_truth[:5] = True
    pass_reco = rng.random(n_mc) < 0.8
    w_truth = rng.uniform(0.5, 1.5, n_mc)
    measured = (coords(n_data, 0.2) * rng.normal(1.0, 0.05, (n_data, 5))).astype(np.float32)
    shape = tuple(len(e) - 1 for e in edges)
    sel, _ = np.histogramdd(gen[pass_truth].astype(float), bins=edges, weights=w_truth[pass_truth])
    arrays = {"MCgen": gen, "MCreco": reco, "measured": measured, "pass_reco": pass_reco, "pass_truth": pass_truth,
              "w_truth": w_truth, "w_reco": w_truth * rng.uniform(0.9, 1.1, n_mc), "measured_weights": np.ones(n_data),
              "denom_nd": sel * 1.15, "flux": np.linspace(1.2e-9, 1.8e-9, shape[0]), "data_pot": np.float64(1.0e20),
              "n_nucleons": np.float64(3.0e30), "nedges": np.int64(5)}
    arrays.update({f"edges_{i}": np.asarray(e, float) for i, e in enumerate(edges)})
    npz = prot / f"of_inputs_5d{tag}.npz"
    np.savez_compressed(npz, **arrays)
    bkg = prot / f"bkg_dump{tag}.npz"
    brng = np.random.default_rng(seed + 1)
    np.savez_compressed(bkg, bkg_reco=np.column_stack([brng.uniform(0.0, 1.6, n_bkg), brng.uniform(1.7, 10.2, n_bkg),
                                                       brng.uniform(0.0, 2.2, n_bkg), brng.uniform(0.0, 4.0, n_bkg),
                                                       brng.uniform(0.5, 3.2, n_bkg)]).astype(np.float32),
                        bkg_w=brng.uniform(0.5, 1.5, n_bkg), bkg_nd=np.zeros(shape),
                        meta=json.dumps({"npz_sha256": tec.sha(npz)}))
    return npz, bkg


def run_evw(world, fixture: dict, tag: str, env_extra=None, out=None):
    root = world["root"]
    fx = root / f"fixture-{tag}.json"
    fx.write_text(json.dumps(fixture))
    out_root = root / f"out-{tag}"
    out_root.mkdir(exist_ok=True)
    out = out_root / "evw5d" if out is None else out
    env = dict(tec.stub_env(root), **(env_extra or {}))
    r = subprocess.run([PY, "-B", str(EVW / "evw5d.py"), "--deploy", str(world["deploy"]), "--out", str(out),
                        "--out-root", str(out_root), "--stage-dir", str(root / f"shm-{tag}"), "--fixture", str(fx)],
                       capture_output=True, text=True, env=env)
    return r.returncode, out, r.stdout + r.stderr


@pytest.fixture(scope="session")
def world():
    root = Path(tempfile.mkdtemp(prefix="evw5d-test-"))
    try:
        deploy = tec.make_deploy(REPO, root)
        prot = root / "protected"
        prot.mkdir()
        npz, bkg = synthetic(deploy, prot)
        env = tec.stub_env(root)
        ref = tec.reference_product(PY, deploy, npz, bkg, root / "refrun", 2, env)
        ref_copy = prot / "data_b-_j-.npz"
        shutil.copyfile(ref, ref_copy)
        with np.load(ref_copy, allow_pickle=False) as z:
            xflat, shp, meta = np.array(z["xsec_flat"]), np.array(z["shape"]), str(z["meta"])
        h2_bytes = tec.sh("git", "-C", deploy, "show", f"{ec.MAIN_PIN}:{ec.REPO['h2'][0]}").stdout.encode()
        f = tec.cell_integrals(deploy, xflat, json.loads(h2_bytes))
        assert all(x > 0 for x in f), f"a synthetic reported cell is empty: {f}"
        dp_bytes = (json.dumps({"f": f}) + "\n").encode()
        main_c = tec.fixture_main_commit(deploy, dp_bytes)
        base = {"main_pin": main_c, "threads": 2, "protected": [str(prot)], "noatime": os.O_NONBLOCK,
                "check_atime": False,
                "repo": {"h2": list(ec.REPO["h2"]), "dp": [tec.DP_REL, hashlib.sha256(dp_bytes).hexdigest()]},
                "shared": {"npz": [str(npz), tec.sha(npz), npz.stat().st_size],
                           "bkg": [str(bkg), tec.sha(bkg), bkg.stat().st_size],
                           "ref": [str(ref_copy), tec.sha(ref_copy), ref_copy.stat().st_size]}}
        w = {"root": root, "deploy": deploy, "prot": prot, "npz": npz, "bkg": bkg, "base": base, "f": f,
             "xflat": xflat, "shape": shp, "meta": meta, "ref_copy": ref_copy}
        rc, out, log = run_evw(w, base, "pass")
        w.update(rc=rc, out=out, log=log)
        yield w
    finally:
        shutil.rmtree(root, ignore_errors=True)


@pytest.fixture(scope="session")
def products(world):
    out = world["out"]
    assert world["rc"] == 0, world["log"][-4000:]
    _, t = ev.read_npz(out / "weights.npz")
    _, c = ev.read_npz(out / "constants.npz")
    run = json.loads((out / "run.json").read_text())
    indep = ev.load_indep(world["npz"])
    sys.path.insert(0, str(world["deploy"] / "nd-unfolding"))
    import s5e_trace
    import xsec_nd
    meta = json.loads(str(t["meta"]))
    cj_raw = (out / "constants.json").read_bytes()
    expected_c = {k: v for k, v in c.items() if k != "meta"}
    return {"t": t, "c": c, "run": run, "indep": indep, "flat_index": s5e_trace.flat_index,
            "extract": xsec_nd.extract_cross_section_nd, "meta": meta, "cj_raw": cj_raw,
            "cjson": json.loads(cj_raw), "expected_c": expected_c,
            "pins": {"fine_map": ec.FINE_MAP_SHA256, "npz": world["base"]["shared"]["npz"][1],
                     "bkg": world["base"]["shared"]["bkg"][1], "ref": world["base"]["shared"]["ref"][1],
                     "code_pin": ec.CODE_PIN}}


def acc(out, bound=None, production=False):
    """accepted() with the bundle's own manifest digest as the bound one (the tests' bundles are fixtures)."""
    out = Path(out)
    if bound is None:
        try:
            bound = hashlib.sha256((out / ev.SUMS).read_bytes()).hexdigest()
        except OSError:
            bound = "0" * 64
    return ev.accepted(out, bound, production=production)


def copy_t(t):
    return {k: np.array(v, copy=True) for k, v in t.items()}


# ------------------------------------------------------------------------------------------ end to end


def test_pass_run_exit(world):
    assert world["rc"] == 0, world["log"][-4000:]
    done = json.loads((world["out"] / ev.DONE).read_text())
    assert done["verdict"] == "PASS" and acc(world["out"])


def test_pass_run(world, products):
    out, run = world["out"], products["run"]
    done = json.loads((out / ev.DONE).read_text())
    assert done["verdict"] == "PASS" and done["controls_verdict"] == "PASS" and done["failed_controls"] == []
    assert set(run["gated"]) == {"C-BIND", "C-KEY", "C-ENTRY", "C-GRID", "C-F", "C-FILE", "C-SELF", "C-FLOW",
                                 "C-PINS"}
    for k in run["gated"]:
        assert run["controls"][k]["pass"] is True, (k, run["controls"][k])
    assert acc(out)
    assert ev.listing(out) == sorted(ev.PRODUCTS + (ev.SUMS, ev.DONE))
    assert not (world["root"] / "shm-pass").exists(), "the staging directory was not removed"


def test_completeness_finding_is_reported_not_failed(world, products):
    """The synthetic denominator is 1.15 x the signal: c = 1/1.15 everywhere, a finding, and the verdict PASS."""
    run = products["run"]
    assert run["findings"] == ["C-COMPLETE"]
    comp = run["controls"]["C-COMPLETE"]
    assert comp["finding"] and abs(comp["max_abs_c_minus_1"] - (1 - 1 / 1.15)) < 1e-12
    assert "FINDING: C-COMPLETE" in world["log"]
    assert json.loads((world["out"] / ev.DONE).read_text())["findings"] == ["C-COMPLETE"]


def test_weights_columns_key_and_flow(world, products):
    t, indep = products["t"], products["indep"]
    m = indep["pass_truth"]
    assert sorted(t) == sorted(ev.COLUMNS + ("meta",))
    assert t["entry"].dtype == np.uint32 and np.array_equal(t["entry"], np.flatnonzero(m))
    for k, n in enumerate(ev.TRUTH_COLS):
        assert t[n].dtype == indep["MCgen"].dtype == np.float32 and np.array_equal(t[n], indep["MCgen"][m, k])
    for n in ("w_prior", "wpush", "w_unfolded"):
        assert t[n].dtype == np.float64
    assert np.array_equal(t["w_unfolded"], t["wpush"] * t["w_prior"])
    assert t["fine_index"].dtype == np.int32 and t["reco_partner"].dtype == np.bool_
    c = products["c"]
    assert c["fine_to_cell"].dtype == np.dtype("<i4") and c["xsec_flat"].dtype == np.float64
    assert c["good"].dtype == np.bool_ and c["completeness"].shape == c["denom_nd"].shape == c["ofin"].shape
    assert all(c[f"edges_{i}"].dtype == np.float64 for i in range(5)) and c["volume"].shape == c["xsec_flat"].shape
    flow = products["run"]["controls"]["C-FLOW"]
    assert flow["n_outside_grid"] >= 2, flow             # the pT 5.0 and W 150 rows
    assert products["meta"]["input_npz_sha256"] == world["base"]["shared"]["npz"][1]


def test_gates_measured(products):
    ctl = products["run"]["controls"]
    assert ctl["C-BIND"]["xsec_flat_bytes_equal"] and ctl["C-BIND"]["meta_equal_except_per_run"]
    assert ctl["C-F"]["f_from_result_max_rel"] <= ev.F_RTOL and ctl["C-F"]["f_from_rows_max_rel"] <= ev.F_RTOL
    assert ctl["C-SELF"]["xsec_bit_for_bit"] and ctl["C-SELF"]["independent_formula_max_rel"] <= ev.INDEP_RTOL


def test_stop_on_one_ulp(world):
    bad = world["xflat"].copy()
    i = int(np.flatnonzero(bad)[0])
    bad[i] = np.nextafter(bad[i], np.inf)
    ref_bad = world["prot"] / "bad" / "data_b-_j-.npz"
    ref_bad.parent.mkdir(exist_ok=True)
    np.savez_compressed(ref_bad, xsec_flat=bad, shape=world["shape"], meta=world["meta"])
    fx = json.loads(json.dumps(world["base"]))
    fx["shared"]["ref"] = [str(ref_bad), tec.sha(ref_bad), ref_bad.stat().st_size]
    rc, out, log = run_evw(world, fx, "stop")
    assert rc == ev.RC_STOP, log[-3000:]
    s = json.loads((out / "STOP.json").read_text())
    assert s["C-BIND"]["xsec_flat_bytes_equal"] is False and s["C-BIND"]["n_differ"] == 1
    assert not (out / "weights.npz").exists() and not (out / ev.DONE).exists()


def test_wrong_pin_fails_before_unfold(world):
    fx = json.loads(json.dumps(world["base"]))
    fx["shared"]["bkg"][1] = "0" * 64
    rc, out, log = run_evw(world, fx, "wrongpin")
    assert rc == ev.RC_FAILED and (out / "FAILED.json").exists() and not (out / "product").exists(), log[-2000:]


def test_stop_on_meta(world):
    """The same xsec_flat with a different meta (a non-per-run field) is not the reference: STOP."""
    meta = json.loads(world["meta"])
    meta["iters"] = 6
    ref = world["prot"] / "badmeta" / "data_b-_j-.npz"
    ref.parent.mkdir(exist_ok=True)
    np.savez_compressed(ref, xsec_flat=world["xflat"], shape=world["shape"], meta=json.dumps(meta))
    fx = json.loads(json.dumps(world["base"]))
    fx["shared"]["ref"] = [str(ref), tec.sha(ref), ref.stat().st_size]
    rc, out, log = run_evw(world, fx, "stopmeta")
    assert rc == ev.RC_STOP, log[-3000:]
    s = json.loads((out / "STOP.json").read_text())
    assert s["C-BIND"]["xsec_flat_bytes_equal"] and not s["C-BIND"]["meta_equal_except_per_run"]
    assert s["C-BIND"]["meta_differing_keys"] == ["iters"] and not (out / "weights.npz").exists()


def test_fail_on_f(world):
    """A data product whose f is 1e-13 away: gate 2 fails, the files are written for diagnosis, the verdict FAIL."""
    dp_bytes = (json.dumps({"f": [x * (1 + 1e-13) for x in world["f"]]}) + "\n").encode()
    main_c = tec.fixture_main_commit(world["deploy"], dp_bytes)
    fx = json.loads(json.dumps(world["base"]))
    fx["main_pin"] = main_c
    fx["repo"]["dp"] = [tec.DP_REL, hashlib.sha256(dp_bytes).hexdigest()]
    rc, out, log = run_evw(world, fx, "failf")
    assert rc == ev.RC_FAIL, log[-3000:]
    shutil.copytree(out, world["root"] / "failf-pristine")
    done = json.loads((out / ev.DONE).read_text())
    assert done["verdict"] == "FAIL" and done["failed_controls"] == ["C-F", "C-SELF"], done["failed_controls"]
    assert done["acceptance"]["pass"] and not acc(out)
    (out / ev.DONE).unlink()
    (out / ev.DONE).write_text(json.dumps(dict(done, verdict="PASS")))
    assert not acc(out), "a FAIL run accepted after its verdict was edited"
    (out / ev.DONE).unlink()
    (out / ev.DONE).write_text(json.dumps(dict(done, verdict="PASS", controls_verdict="PASS", failed_controls=[])))
    assert not acc(out), "a FAIL run accepted although run.json records the failure"


def test_fail_on_grid(world):
    """A wrong fine-map pin: C-GRID (and C-FILE's map digest) fail, the verdict FAIL."""
    fx = json.loads(json.dumps(world["base"]))
    fx["fine_map_sha"] = "0" * 64
    rc, out, log = run_evw(world, fx, "failgrid")
    assert rc == ev.RC_FAIL, log[-3000:]
    done = json.loads((out / ev.DONE).read_text())
    assert "C-GRID" in done["failed_controls"] and "C-FILE" in done["failed_controls"]


def test_wrong_deploy_refused(world):
    fx = json.loads(json.dumps(world["base"]))
    fx["code_pin"] = "0" * 40
    rc, out, log = run_evw(world, fx, "wrongdeploy")
    assert rc == ev.RC_FAILED and "is not" in json.loads((out / "FAILED.json").read_text())["verdict"]
    fx = json.loads(json.dumps(world["base"]))
    fx["code_sha"] = dict(ec.CODE_SHA, **{"nd-unfolding/xsec_nd.py": "0" * 64})
    rc, out, log = run_evw(world, fx, "wrongcode")
    assert rc == ev.RC_FAILED and "not the pinned file" in json.loads((out / "FAILED.json").read_text())["verdict"]


def test_existing_out_and_slurm_refused(world):
    rc, _, log = run_evw(world, world["base"], "slurm", env_extra={"SLURM_JOB_ID": "1"})
    assert rc == 2 and "refused inside a Slurm job" in log
    rc, _, log = run_evw(world, world["base"], "again", out=world["out"])
    assert rc == 2 and "exists" in log


def test_out_must_be_under_out_root(world):
    fx = world["root"] / "fixture-outside.json"
    fx.write_text(json.dumps(world["base"]))
    (world["root"] / "out-root-x").mkdir()
    r = subprocess.run([PY, "-B", str(EVW / "evw5d.py"), "--deploy", str(world["deploy"]),
                        "--out", str(world["root"] / "elsewhere" / "evw5d"), "--out-root",
                        str(world["root"] / "out-root-x"), "--stage-dir", str(world["root"] / "shm-x"),
                        "--fixture", str(fx)], capture_output=True, text=True, env=tec.stub_env(world["root"]))
    assert r.returncode == 2 and "not under --out-root" in r.stderr
    assert not (world["root"] / "elsewhere").exists(), "an --out outside --out-root was created"


# ------------------------------------------------------------------------------------- C-COL (binning)


COL_HELPER = r"""
import json, sys
import numpy as np
sys.path.insert(0, sys.argv[1]); import evw5d as ev
d = sys.argv[2]
for p in (d + "/nd-unfolding", d + "/2d-unfolding"):
    sys.path.insert(0, p)
import omnifold_nn_core as onc, s5c_unfold, s5p_numerics
res = {}
for tag, npz, bkg, out in json.loads(sys.argv[3]):
    argv = ["--npz", npz, "--bkg", bkg, "--expect-npz-sha256", ev.ess.sha256_file(npz),
            "--expect-bkg-sha256", ev.ess.sha256_file(bkg), "--config", "R", "--iters", "5",
            "--construction", "data", "--pairs=-:-", "--tag", "data", "--threads", "2", "--out", out]
    inputs, xs, wpush = ev.capture_unfold(s5p_numerics, onc, s5c_unfold, argv)
    np.savez(out + ".npz", wpush=wpush, xs=xs)
print("ok")
"""


def test_col_weights_do_not_depend_on_interior_edges(world, products):
    deploy = world["deploy"]
    sys.path.insert(0, str(deploy / "nd-unfolding"))
    import s5p_stage1_inspect as s1
    fine = [np.asarray(s1.FINE[a], float) for a in s1.AXES]
    grid_b = []
    for e in fine:   # the same outer edges; every interior edge moved or dropped
        inner = (e[1:-1] * 1.0371)[::2]
        grid_b.append(np.concatenate([[e[0]], inner[(inner > e[0]) & (inner < e[-1])], [e[-1]]]))
    assert all(not np.array_equal(a, b) for a, b in zip(fine, grid_b))
    col = world["root"] / "col"
    col.mkdir(exist_ok=True)
    npz_a, bkg_a = synthetic(deploy, col, tag="_a")
    npz_b, bkg_b = synthetic(deploy, col, edges=grid_b, tag="_b")
    runs = [("a", str(npz_a), str(bkg_a), str(col / "a")), ("b", str(npz_b), str(bkg_b), str(col / "b"))]
    r = subprocess.run([PY, "-B", "-c", COL_HELPER, str(EVW), str(deploy), json.dumps(runs)], capture_output=True,
                       text=True, env=tec.stub_env(world["root"]))
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-3000:]
    ra, rb = np.load(col / "a.npz"), np.load(col / "b.npz")
    assert ev.same_bits(ra["wpush"], rb["wpush"]), "the push weights depend on the interior edges"
    # grid A's weights, re-histogrammed on grid B with B's denominator and flux, are B's rerun
    with np.load(npz_b) as zb:
        db = {"edges": grid_b, "denom_nd": zb["denom_nd"], "flux": zb["flux"], "data_pot": zb["data_pot"],
              "n_nucleons": zb["n_nucleons"]}
        m, gen, wt = zb["pass_truth"], zb["MCgen"], zb["w_truth"]
    samp = np.column_stack([gen[m, i] for i in range(gen.shape[1])])
    mp = ev.driver_maps(db, ra["wpush"] * wt[m], wt[m], samp, products["extract"])
    assert ev.same_bits(mp["xs"], rb["xs"])


# ---------------------------------------------------------------------------------------- unit: helpers


def test_same_bits_and_max_rel():
    a = np.array([1.0, 2.0])
    assert ev.same_bits(a, a.copy()) and not ev.same_bits(a, a.astype(np.float32))
    assert not ev.same_bits(np.zeros(2), np.zeros(2, np.int64)), "equal bytes, another dtype"
    assert not ev.same_bits(a, np.array([1.0, np.nextafter(2.0, 3.0)])) and not ev.same_bits(a, a.reshape(2, 1))
    assert ev.max_rel([1.0, 0.0], [1.0, 0.0]) == 0.0 and ev.max_rel([1.0, 1e-300], [1.0, 0.0]) == float("inf")
    assert ev.max_rel([1.0], [1.0, 2.0]) == float("inf") and abs(ev.max_rel([1.5], [1.0]) - 0.5) < 1e-15


def test_check_entries():
    assert ev.check_entries(np.array([0, 3, 7], np.uint32))["pass"]
    assert not ev.check_entries(np.array([0, 3, 3], np.uint32))["pass"]
    r = ev.check_entries(np.array([0, 7, 3], np.uint32))
    assert not r["pass"] and not r["strictly_increasing"] and r["unique"]
    assert not ev.check_entries(np.array([0, 3, 7], np.int64))["pass"]


def test_check_key_each_field(products):
    indep = products["indep"]
    d = {k: indep[k] for k in indep if not k.startswith("edges_") and k != "nedges"}
    d["edges"] = [indep[f"edges_{i}"] for i in range(int(indep["nedges"]))]
    wpush = products["t"]["wpush"]
    assert ev.check_key(d, indep, wpush)["pass"]
    for k in ("MCgen", "MCreco", "w_truth", "w_reco", "denom_nd", "flux"):
        bad = dict(d)
        x = np.array(d[k], copy=True)
        x.flat[7] = np.nextafter(x.flat[7], x.dtype.type(np.inf))
        bad[k] = x
        r = ev.check_key(bad, indep, wpush)
        assert not r["pass"] and not r["equal"][k], k
    for k in ("pass_reco", "pass_truth"):
        bad = dict(d)
        x = np.array(d[k], copy=True)
        x[9] = not x[9]
        bad[k] = x
        assert not ev.check_key(bad, indep, wpush)["equal"][k], k
    for k in ("data_pot", "n_nucleons"):
        bad = dict(d)
        bad[k] = np.nextafter(float(d[k]), np.inf)
        assert not ev.check_key(bad, indep, wpush)["pass"], k
    bad = dict(d)
    bad["edges"] = list(d["edges"])
    bad["edges"][2] = np.array(d["edges"][2], copy=True)
    bad["edges"][2][3] += 1e-12
    assert not ev.check_key(bad, indep, wpush)["equal"]["edges"]
    assert not ev.check_key(d, indep, wpush[:-1])["pass"]
    ind2 = dict(indep, pass_truth=indep["pass_truth"].astype(np.int8))
    assert not ev.check_key(dict(d, pass_truth=ind2["pass_truth"]), ind2, wpush)["pass"]


def test_build_table_refuses_a_non_bool_mask_and_a_wide_entry(products, monkeypatch):
    indep = products["indep"]
    d = {k: indep[k] for k in indep}
    d["edges"] = [indep[f"edges_{i}"] for i in range(int(indep["nedges"]))]
    wpush = products["t"]["wpush"]
    t = ev.build_table(d, wpush, products["flat_index"])
    assert all(ev.same_bits(t[k], products["t"][k]) for k in ev.COLUMNS)
    with pytest.raises(ev.Failed):
        ev.build_table(dict(d, pass_truth=d["pass_truth"].astype(np.int64)), wpush, products["flat_index"])
    monkeypatch.setattr(ev.np, "flatnonzero", lambda m: np.array([2 ** 32]))
    with pytest.raises(ev.Failed):
        ev.build_table(d, wpush, products["flat_index"])


def test_build_table_widens_a_float32_prior_exactly(products):
    indep = products["indep"]
    d = {k: indep[k] for k in indep}
    d["edges"] = [indep[f"edges_{i}"] for i in range(int(indep["nedges"]))]
    d["w_truth"] = indep["w_truth"].astype(np.float32)
    t = ev.build_table(d, products["t"]["wpush"], products["flat_index"])
    m = d["pass_truth"]
    assert t["w_prior"].dtype == np.float64 and np.array_equal(t["w_prior"], d["w_truth"][m].astype(np.float64))
    assert ev.same_bits(t["w_unfolded"], products["t"]["wpush"] * d["w_truth"][m])
    ind32 = dict(indep, w_truth=d["w_truth"])
    r = ev.check_file(t | {"meta": products["t"]["meta"]}, products["c"], ind32, products["t"]["wpush"],
                      products["expected_c"], products["flat_index"], products["meta"], products["cj_raw"],
                      products["cjson"], products["pins"])
    assert r["w_prior"] and r["w_unfolded"] and r["weights_float64"]


def test_build_table_widens_a_float32_push_exactly(products):
    indep = products["indep"]
    d = {k: indep[k] for k in indep}
    d["edges"] = [indep[f"edges_{i}"] for i in range(int(indep["nedges"]))]
    w32 = products["t"]["wpush"].astype(np.float32)
    t = ev.build_table(d, w32, products["flat_index"])
    assert t["wpush"].dtype == np.float64 and np.array_equal(t["wpush"], w32.astype(np.float64))
    assert ev.same_bits(t["w_unfolded"], w32 * d["w_truth"][d["pass_truth"]])


# ---------------------------------------------------------------------------------- unit: C-FILE


def _file(products, t=None, c=None, meta=None, cj_raw=None, wpush=None, expected_c=None):
    p = products
    return ev.check_file(p["t"] if t is None else t, p["c"] if c is None else c, p["indep"],
                         p["t"]["wpush"] if wpush is None else wpush,
                         p["expected_c"] if expected_c is None else expected_c, p["flat_index"],
                         p["meta"] if meta is None else meta, p["cj_raw"] if cj_raw is None else cj_raw, p["cjson"],
                         p["pins"])


def test_check_file_passes_on_the_products(products):
    assert _file(products)["pass"]


def _same_cell_pair(t):
    fi = t["fine_index"]
    vals, counts = np.unique(fi[fi >= 0], return_counts=True)
    cell = vals[counts >= 2][0]
    i, j = np.flatnonzero(fi == cell)[:2]
    return int(i), int(j)


@pytest.mark.parametrize("fault", ["shift_key", "swap_in_cell", "truth_ulp", "w_prior_ulp", "wpush_ulp",
                                   "unfolded_ulp", "flow_row_weight", "reco_flag", "fine_index", "dtype_w",
                                   "dtype_truth", "missing_col", "extra_col"])
def test_check_file_fires(products, fault):
    t = copy_t(products["t"])
    i, j = _same_cell_pair(t)
    flow = int(np.flatnonzero(t["fine_index"] < 0)[0])
    if fault == "shift_key":
        t["entry"][5] += 1
    elif fault == "swap_in_cell":
        for k in ("wpush", "w_unfolded"):
            t[k][[i, j]] = t[k][[j, i]]
    elif fault == "truth_ulp":
        t["truth_eavail"][i] = np.nextafter(t["truth_eavail"][i], np.float32(np.inf))
    elif fault == "w_prior_ulp":
        t["w_prior"][i] = np.nextafter(t["w_prior"][i], np.inf)
    elif fault == "wpush_ulp":
        t["wpush"][i] = np.nextafter(t["wpush"][i], np.inf)
    elif fault == "unfolded_ulp":
        t["w_unfolded"][i] = np.nextafter(t["w_unfolded"][i], np.inf)
    elif fault == "flow_row_weight":
        t["w_unfolded"][flow] *= 2.0
    elif fault == "reco_flag":
        t["reco_partner"][i] = not t["reco_partner"][i]
    elif fault == "fine_index":
        t["fine_index"][i] = t["fine_index"][i] + 1
    elif fault == "dtype_w":
        t["w_prior"] = t["w_prior"].astype(np.float32).astype(np.float64).astype(np.float32)
    elif fault == "dtype_truth":
        t["truth_pt"] = t["truth_pt"].astype(np.float64)
    elif fault == "missing_col":
        del t["reco_partner"]
    elif fault == "extra_col":
        t["run_number"] = np.zeros(1)
    assert not _file(products, t=t)["pass"], fault


@pytest.mark.parametrize("fault", ["flux_ulp", "pot_ulp", "nucleons", "denom", "completeness", "volume", "map",
                                   "edges", "xsec", "missing", "extra"])
def test_check_file_fires_on_constants(products, fault):
    c = copy_t(products["c"])
    key = {"flux_ulp": "flux", "pot_ulp": "data_pot", "nucleons": "n_nucleons", "denom": "denom_nd",
           "completeness": "completeness", "volume": "volume", "edges": "edges_3", "xsec": "xsec_flat"}.get(fault)
    if key is not None:
        c[key] = np.array(c[key], copy=True)
        c[key].flat[0] = np.nextafter(c[key].flat[0], np.inf)
    elif fault == "map":
        c["fine_to_cell"] = np.array(c["fine_to_cell"], copy=True)
        k = int(np.flatnonzero(c["fine_to_cell"] >= 0)[0])
        c["fine_to_cell"][k] = (c["fine_to_cell"][k] + 1) % 16
    elif fault == "missing":
        del c["good"]
    elif fault == "extra":
        c["phi"] = np.float64(1.0)
    assert not _file(products, c=c)["pass"], fault


def test_check_file_fires_on_meta_and_json(products):
    assert not _file(products, meta=dict(products["meta"], n_rows=1))["pass"]
    assert not _file(products, cj_raw=products["cj_raw"].replace(b'"data_pot": ', b'"data_pot": 1'))["pass"]
    t = copy_t(products["t"])
    t["meta"] = np.array(json.dumps(dict(products["meta"], code_pin="0")))
    assert not _file(products, t=t)["pass"]
    c = copy_t(products["c"])
    c["meta"] = np.array(json.dumps(dict(products["meta"], code_pin="0")))
    assert not _file(products, c=c)["pass"]


# ---------------------------------------------------------------------------------- unit: C-SELF and C-F


def _self(products, t=None, c=None, ref=None, f=None):
    p = products
    ref = np.asarray(p["c"]["xsec_flat"]) if ref is None else ref
    f = np.asarray(p["run"]["controls"]["C-F"]["f"]) if f is None else f
    return ev.check_self(p["t"] if t is None else t, p["c"] if c is None else c, ref, f, p["extract"], 5)


def test_check_self_passes(products):
    r = _self(products)
    assert r["pass"] and r["xsec_bit_for_bit"] and r["f_from_file_max_rel"] <= ev.F_RTOL


def test_check_self_result_one_ulp(products):
    ref = np.array(products["c"]["xsec_flat"], copy=True)
    k = int(np.flatnonzero(ref)[0])
    ref[k] = np.nextafter(ref[k], np.inf)
    r = _self(products, ref=ref)
    assert not r["pass"] and not r["xsec_bit_for_bit"]


def test_check_self_independent_formula_alone(products):
    c = copy_t(products["c"])
    c["cm2_per_m2"] = np.float64(1.0e4 * (1 + 1e-12))      # read only by the independent formula
    r = _self(products, c=c)
    assert r["xsec_bit_for_bit"] and not r["pass"] and r["independent_formula_max_rel"] > ev.INDEP_RTOL


def test_check_self_f_alone(products):
    f = np.asarray(products["run"]["controls"]["C-F"]["f"]) * (1 + 1e-13)
    r = _self(products, f=f)
    assert r["xsec_bit_for_bit"] and not r["pass"] and r["f_from_file_max_rel"] > ev.F_RTOL


def test_check_self_rows_alone(products):
    """A row's fine_index moved to another reported cell: only the row-level integral sees it."""
    t = copy_t(products["t"])
    fm = products["c"]["fine_to_cell"]
    fi = t["fine_index"]
    i = int(np.flatnonzero((fi >= 0) & (fm[np.where(fi >= 0, fi, 0)] == 0))[0])
    t["fine_index"][i] = int(np.flatnonzero(fm == 5)[0])
    r = _self(products, t=t)
    assert r["xsec_bit_for_bit"] and r["f_from_file_max_rel"] <= ev.F_RTOL and not r["pass"]
    assert r["f_from_rows_max_rel"] > ev.F_RTOL


def test_check_self_f_file_alone(products):
    """Volumes 5e-14 high: within the volume and formula bounds, beyond gate 2 for the file-level f only."""
    c = copy_t(products["c"])
    c["volume"] = c["volume"] * (1 + 5e-14)
    r = _self(products, c=c)
    assert r["xsec_bit_for_bit"] and r["f_from_rows_max_rel"] <= ev.F_RTOL
    assert r["volume_vs_edges_max_rel"] <= ev.VOLUME_RTOL and r["independent_formula_max_rel"] <= ev.INDEP_RTOL
    assert r["f_from_file_max_rel"] > ev.F_RTOL and not r["pass"]


def test_check_self_volume_alone(products):
    """A saved volume doubled in a cell with no result: only the volume check can see it."""
    c = copy_t(products["c"])
    k = int(np.flatnonzero(np.asarray(c["xsec_flat"]) == 0)[0])
    c["volume"][k] *= 2.0
    r = _self(products, c=c)
    assert r["xsec_bit_for_bit"] and r["f_from_file_max_rel"] <= ev.F_RTOL and r["f_from_rows_max_rel"] <= ev.F_RTOL
    assert r["independent_formula_max_rel"] <= ev.INDEP_RTOL and not r["pass"]


@pytest.mark.parametrize("fault", ["good_inverted", "xsec_zero", "cm2"])
def test_check_self_saved_constants_from_the_builder(products, fault):
    """A builder error on a saved array (C-FILE compares with the builder's own output, so it cannot see it)."""
    c = copy_t(products["c"])
    if fault == "good_inverted":
        c["good"] = ~c["good"]
    elif fault == "xsec_zero":
        c["xsec_flat"] = np.zeros_like(c["xsec_flat"])
    else:
        c["cm2_per_m2"] = np.float64(1.0e4 + 1e-9)
    r = _self(products, c=c)
    assert r["xsec_bit_for_bit"] and not r["pass"], fault


def test_check_file_constants_against_the_input(products):
    """flux changed in both the saved constants and the builder's expectation: only the input comparison sees it."""
    c, exp = copy_t(products["c"]), dict(products["expected_c"])
    for d in (c, exp):
        d["flux"] = np.array(d["flux"], copy=True)
        d["flux"][0] = np.nextafter(d["flux"][0], np.inf)
    r = _file(products, c=c, expected_c=exp)
    assert all(r["constants"].values()) and not r["constants_vs_input"]["flux"] and not r["pass"]
    for key in ("data_pot", "n_nucleons", "denom_nd", "edges_1"):
        c, exp = copy_t(products["c"]), dict(products["expected_c"])
        for d in (c, exp):
            d[key] = np.array(d[key], copy=True)
            d[key].flat[0] = np.nextafter(d[key].flat[0], np.inf)
        assert not _file(products, c=c, expected_c=exp)["pass"], key


@pytest.mark.parametrize("key", ["ofin", "completeness"])
def test_check_self_saved_maps_alone(products, key):
    c = copy_t(products["c"])
    k = int(np.flatnonzero(np.asarray(c[key]).ravel())[0])
    c[key].flat[k] = np.nextafter(c[key].flat[k], np.inf)
    r = _self(products, c=c)
    assert r["xsec_bit_for_bit"] and not r["pass"] and not r[f"{key}_bit_for_bit"]


def test_contributions_skip_zero_denominator_cells():
    fm = np.array([0, 0, 1, -1, -1])
    good = np.array([True, False, True, True, False])
    comp = np.ones(5)
    s, extra = ev.contributions(np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]), np.array([0, 1, 2, 3, -1, 4]), comp,
                                np.array([1.0]), 1.0, 1.0, good, fm, 1)
    assert s[0] == 1e4 and s[1] == 3e4 and s[2:].sum() == 0 and extra["rows_in_reported_cells_with_zero_denominator"] == 1


def test_cell_integrals():
    v = ev.cell_integrals(np.array([1.0, 2.0, 3.0]), np.array([2.0, 1.0, 1.0]), np.array([0, 0, 15]))
    assert v[0] == 4.0 and v[15] == 3.0 and v[1:15].sum() == 0


# ---------------------------------------------------------------------------------- unit: C-FLOW


def _flow(products, t=None, c=None, unf=None, n=None):
    p = products
    t = p["t"] if t is None else t
    if unf is None:
        unf = np.bincount(p["t"]["fine_index"][p["t"]["fine_index"] >= 0],
                          weights=p["t"]["w_unfolded"][p["t"]["fine_index"] >= 0],
                          minlength=int(np.asarray(p["c"]["ofin"]).size))
    n = int(np.count_nonzero(p["indep"]["pass_truth"])) if n is None else n
    return ev.check_flow(t, p["c"] if c is None else c, unf, n)


def test_check_flow(products):
    assert _flow(products)["pass"]
    assert products["run"]["controls"]["C-FLOW"]["unfolded_max_rel"] <= ev.FLOW_RTOL
    assert not _flow(products, n=int(np.count_nonzero(products["indep"]["pass_truth"])) + 1)["pass"]
    t = copy_t(products["t"])
    t["fine_index"][0] = int(np.asarray(products["c"]["ofin"]).size)
    r = _flow(products, t=t)
    assert not r["pass"] and not r["fine_index_in_range"]
    t = copy_t(products["t"])
    flow_row = int(np.flatnonzero(t["fine_index"] < 0)[0])
    t["fine_index"][flow_row] = -2            # a flow row: the sums are unchanged, only the range check sees it
    r = _flow(products, t=t)
    assert not r["pass"] and not r["fine_index_in_range"]
    c = copy_t(products["c"])
    k = int(np.flatnonzero(np.asarray(c["ofin"]).ravel())[0])
    c["ofin"].flat[k] *= 1 + 1e-9
    assert not _flow(products, c=c)["pass"]


def test_check_flow_driver_histogram(products):
    p = products
    fi = p["t"]["fine_index"]
    unf = np.bincount(fi[fi >= 0], weights=p["t"]["w_unfolded"][fi >= 0], minlength=int(np.asarray(p["c"]["ofin"]).size))
    unf[np.flatnonzero(unf)[0]] *= 1 + 1e-9
    r = _flow(products, unf=unf)
    assert not r["pass"] and r["unfolded_max_rel"] > ev.FLOW_RTOL


# ---------------------------------------------------------------------------------- unit: C-COMPLETE


def test_measure_completeness():
    den = np.array([2.0, 4.0, 0.0, 8.0])
    r = ev.measure_completeness(np.array([2.0, 4.0, 0.0, 8.0]), den)
    assert not r["finding"] and r["max_abs_c_minus_1"] == 0.0 and r["n_denominator_positive"] == 3
    r = ev.measure_completeness(np.array([2.0, 4.0 * (1 + 1e-13), 0.0, 8.0]), den)
    assert not r["finding"]
    r = ev.measure_completeness(np.array([2.0, 4.0 * (1 + 3e-12), 0.0, 8.0]), den)
    assert r["finding"] and r["n_cells_beyond_atol"] == 1 and r["max_abs_c_minus_1"] > ev.COMPLETE_ATOL
    assert r["c_one_to_1e-5_in_every_fine_cell"]
    r = ev.measure_completeness(np.array([2.0, 4.0 * (1 + 2e-5), 0.0, 8.0]), den)
    assert r["finding"] and not r["c_one_to_1e-5_in_every_fine_cell"]
    assert not ev.measure_completeness(np.array([2.0, 4.0, 1.0, 8.0]), den)["c_one_to_1e-5_in_every_fine_cell"]
    r = ev.measure_completeness(np.array([2.0, 4.0, 1.0, 8.0]), den)
    assert r["finding"] and r["n_signal_without_denominator"] == 1
    r = ev.measure_completeness(np.array([2.0, 0.0, 0.0, 8.0]), den)
    assert r["finding"] and r["n_denominator_without_signal"] == 1
    assert ev.measure_completeness(np.zeros(2), np.zeros(2))["finding"]
    assert not ev.measure_completeness(np.zeros(2), np.zeros(2))["c_one_to_1e-5_in_every_fine_cell"]


# ---------------------------------------------------------------------------------- unit: acceptance


@pytest.fixture()
def out_copy(world, tmp_path):
    dst = tmp_path / "evw5d"
    shutil.copytree(world["out"], dst)
    assert acc(dst)
    return dst


def test_accepted_byte_change(out_copy):
    p = out_copy / "weights.npz"
    b = bytearray(p.read_bytes())
    b[-1] ^= 1
    p.write_bytes(bytes(b))
    assert not acc(out_copy)


def test_accepted_extra_and_missing(out_copy):
    (out_copy / "extra.txt").write_text("x")
    assert not acc(out_copy)
    (out_copy / "extra.txt").unlink()
    assert acc(out_copy)
    (out_copy / "constants.json").unlink()
    assert not acc(out_copy)


def test_accepted_link(out_copy):
    p = out_copy / "constants.json"
    real = out_copy.parent / "real.json"
    shutil.move(p, real)
    p.symlink_to(real)
    assert not acc(out_copy)


def test_accepted_done_marker(out_copy):
    done = json.loads((out_copy / ev.DONE).read_text())
    (out_copy / ev.DONE).write_text(json.dumps(dict(done, verdict="FAIL")))
    assert not acc(out_copy)
    (out_copy / ev.DONE).write_text(json.dumps(dict(done, sha256sums_sha256="0" * 64)))
    assert not acc(out_copy)
    (out_copy / ev.DONE).write_text(json.dumps(dict(done, schema="evw2d/1")))
    assert not acc(out_copy)
    (out_copy / ev.DONE).unlink()
    assert not acc(out_copy)


def test_accepted_done_link(out_copy):
    real = out_copy.parent / "done.json"
    shutil.move(out_copy / ev.DONE, real)
    (out_copy / ev.DONE).symlink_to(real)
    assert not acc(out_copy)


def test_accepted_crlf_sums(out_copy):
    raw = (out_copy / ev.SUMS).read_bytes()
    (out_copy / ev.SUMS).write_bytes(raw.replace(b"\n", b"\r\n"))
    assert not acc(out_copy)


def test_accepted_bound_digest(out_copy):
    h = hashlib.sha256((out_copy / ev.SUMS).read_bytes()).hexdigest()
    assert ev.accepted(out_copy, h, production=False)
    assert not ev.accepted(out_copy, "0" * 64, production=False)
    assert not ev.accepted(out_copy, h), "a fixture bundle is not a production result"
    assert not ev.accepted(out_copy, None, production=False)


def test_accepted_run_json_cross_check(out_copy):
    """run.json rewritten to record a failure, with SHA256SUMS and the marker re-made to match: refused."""
    run = json.loads((out_copy / "run.json").read_text())
    run["controls"]["C-F"]["pass"] = False
    rj = (json.dumps(run, indent=1) + "\n").encode()
    (out_copy / "run.json").write_bytes(rj)
    digests = ev.parse_sums((out_copy / ev.SUMS).read_text())
    digests["run.json"] = hashlib.sha256(rj).hexdigest()
    sums = ev.sums_text(digests)
    (out_copy / ev.SUMS).write_bytes(sums.encode())
    done = json.loads((out_copy / ev.DONE).read_text())
    done.update(products=digests, sha256sums_sha256=hashlib.sha256(sums.encode()).hexdigest())
    (out_copy / ev.DONE).write_text(json.dumps(done))
    assert ev.acceptance(out_copy, digests)["pass"] and not acc(out_copy)


def test_accepted_sums_file(out_copy):
    s = (out_copy / ev.SUMS).read_text()
    lines = s.splitlines()
    (out_copy / ev.SUMS).write_text("\n".join(lines[:-1]) + "\n")
    assert not acc(out_copy)


def test_parse_sums():
    h = "a" * 64
    assert ev.parse_sums(f"{h}  x\n{h}  y\n") == {"x": h, "y": h}
    assert ev.parse_sums(f"{h}  x\n{h}  x\n") is None
    assert ev.parse_sums(f"{h} x\n") is None
    assert ev.parse_sums(f"{'A' * 64}  x\n") is None
    assert ev.parse_sums(f"{h[:-1]}  x\n") is None
    assert ev.parse_sums(f"{h}  x") is None and ev.parse_sums(f"{h}  x\r\n") is None


def test_acceptance_requires_complete_digest_map(out_copy):
    digests = ev.parse_sums((out_copy / ev.SUMS).read_text())
    assert ev.acceptance(out_copy, digests)["pass"]
    short = {k: v for k, v in digests.items() if k != "run.json"}
    (out_copy / ev.SUMS).write_text(ev.sums_text(short))
    r = ev.acceptance(out_copy, short)
    assert r["sums_parse_exact"] and r["product_set_exact"] and r["rehash_equal"]
    assert not r["pass"] and not r["digest_map_complete"]


# ---------------------------------------------------------------------------------- unit: capture, ESS pin


def test_capture_unfold_refusals():
    onc = types.SimpleNamespace(omnifold_loop=lambda *a, **k: (None, np.ones(3)))
    s5c = types.SimpleNamespace()

    def unfold(inputs, config, seed, threads, iters):
        return np.zeros(2), []
    s5c.unfold = unfold

    def main_once(argv):
        s5c.unfold({"x": 1}, "c", 1, 1, 1)
        onc.omnifold_loop()
        return 0
    inputs, xs, w = ev.capture_unfold(types.SimpleNamespace(main=main_once), onc, s5c, [])
    assert inputs == {"x": 1} and np.array_equal(w, np.ones(3))
    assert onc.omnifold_loop.__name__ == "<lambda>" and s5c.unfold is unfold, "the wrappers were not removed"
    with pytest.raises(ev.Failed):
        ev.capture_unfold(types.SimpleNamespace(main=lambda argv: 3), onc, s5c, [])

    def main_once_rc3(argv):
        main_once(argv)
        return 3
    with pytest.raises(ev.Failed, match="returned 3"):
        ev.capture_unfold(types.SimpleNamespace(main=main_once_rc3), onc, s5c, [])

    def main_twice(argv):
        main_once(argv)
        return main_once(argv)
    with pytest.raises(ev.Failed):
        ev.capture_unfold(types.SimpleNamespace(main=main_twice), onc, s5c, [])

    def main_raises(argv):
        raise RuntimeError("x")
    with pytest.raises(RuntimeError):
        ev.capture_unfold(types.SimpleNamespace(main=main_raises), onc, s5c, [])
    assert s5c.unfold is unfold


def test_ess_tool_pin(tmp_path):
    for sub in ("evw5d", "ess_e"):
        shutil.copytree(EVW.parent / sub, tmp_path / sub, ignore=shutil.ignore_patterns("__pycache__"))
    code = f"import sys; sys.path.insert(0, {str(tmp_path / 'evw5d')!r}); import evw5d; print('imported')"
    r = subprocess.run([PY, "-B", "-c", code], capture_output=True, text=True)
    assert r.returncode == 0 and "imported" in r.stdout, r.stderr
    with open(tmp_path / "ess_e" / "ess_capture.py", "a") as fh:
        fh.write("\n")
    r = subprocess.run([PY, "-B", "-c", code], capture_output=True, text=True)
    assert r.returncode != 0 and "pinned" in r.stderr


# ---------------------------------------------------------------------------------- the job script's refusals


def _git_repo(path: Path, files: dict) -> str:
    path.mkdir(parents=True)
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    for rel, text in files.items():
        (path / rel).parent.mkdir(parents=True, exist_ok=True)
        (path / rel).write_text(text)
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-q", "-m", "t"], check=True, env=env)
    return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


@pytest.fixture()
def job(tmp_path):
    """A fake job environment for sbatch_evw5d.sh: an output root, a deploy and a tool clone (tiny git repos), and a
    squeue that answers the 30:00 limit. Nothing reaches a scheduler; each case refuses before the setup is sourced."""
    tmp_path = Path(os.path.realpath(tmp_path))
    out = tmp_path / "OUT"
    (out / "logs").mkdir(parents=True)
    pin = _git_repo(tmp_path / "deploy", {"setup_salloc_env.sh": "return 1\n"})
    w = (EVW / "evw5d.py").read_text()
    tpin = _git_repo(tmp_path / "tool", {"nd-unfolding/evw5d/evw5d.py": w})
    wsha = hashlib.sha256(w.encode()).hexdigest()
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    (bin_ / "squeue").write_text("#!/bin/bash\necho 30:00\n")
    (bin_ / "squeue").chmod(0o755)
    env = dict(os.environ, PATH=f"{bin_}:{os.environ['PATH']}", SLURM_JOB_ID="4242", SLURM_JOB_NAME="evw5d",
               SLURM_JOB_NUM_NODES="1")
    env.pop("SLURM_ARRAY_JOB_ID", None)
    env.pop("SLURM_ARRAY_TASK_ID", None)

    def set_setup(text):
        (tmp_path / "deploy" / "setup_salloc_env.sh").write_text(text)
        subprocess.run(["git", "-C", str(tmp_path / "deploy"), "-c", "user.name=t", "-c", "user.email=t@t", "commit",
                        "-q", "-am", "setup"], check=True)
        return subprocess.run(["git", "-C", str(tmp_path / "deploy"), "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    state = {"pin": pin}

    def run(out_arg=None, wsha_arg=None, extra_env=None):
        args = [str(tmp_path / "deploy"), state["pin"], str(out if out_arg is None else out_arg), str(tmp_path / "tool"), tpin,
                wsha if wsha_arg is None else wsha_arg]
        return subprocess.run(["bash", str(EVW / "sbatch_evw5d.sh"), *args], capture_output=True, text=True,
                              env=dict(env, **(extra_env or {})))
    def setup(text):
        state["pin"] = set_setup(text)
    return {"run": run, "out": out, "tmp": tmp_path, "wsha": wsha, "setup": setup}


def test_job_refuses_a_linked_log_directory(job):
    target = job["tmp"] / "elsewhere"
    target.mkdir()
    shutil.rmtree(job["out"] / "logs")
    (job["out"] / "logs").symlink_to(target)
    r = job["run"]()
    assert r.returncode == 2 and "refusing: logs" in r.stderr and list(target.iterdir()) == []


def test_job_refuses_an_existing_or_linked_log_file(job):
    victim = job["tmp"] / "victim.txt"
    victim.write_text("keep")
    (job["out"] / "logs" / "job-env-4242.log").symlink_to(victim)
    r = job["run"]()
    assert r.returncode == 2 and "exists" in r.stderr and victim.read_text() == "keep"


def test_job_refuses_a_wrong_writer_digest(job):
    r = job["run"](wsha_arg="0" * 64)
    done = json.loads((job["out"] / "logs" / "DONE-4242").read_text())
    assert r.returncode == 2 and "is not the bound" in done["refused"]


def test_job_refuses_when_git_status_fails(job):
    (job["tmp"] / "tool" / ".git" / "index").write_bytes(b"garbage")
    r = job["run"]()
    done = json.loads((job["out"] / "logs" / "DONE-4242").read_text())
    assert r.returncode == 2 and "tool clone is not a clean checkout" in done["refused"]


def test_job_refuses_a_failed_setup(job):
    r = job["run"]()
    done = json.loads((job["out"] / "logs" / "DONE-4242").read_text())
    assert r.returncode == 2 and "setup_salloc_env.sh returned 1" in done["refused"]



def test_job_refuses_an_array_task_or_more_nodes(job):
    r = job["run"](extra_env={"SLURM_ARRAY_JOB_ID": "77", "SLURM_ARRAY_TASK_ID": "1"})
    done = json.loads((job["out"] / "logs" / "DONE-4242").read_text())
    assert r.returncode == 2 and "an array task" in done["refused"]
    (job["out"] / "logs" / "DONE-4242").unlink()
    r = job["run"](extra_env={"SLURM_JOB_NUM_NODES": "2"})
    done = json.loads((job["out"] / "logs" / "DONE-4242").read_text())
    assert r.returncode == 2 and "not 1" in done["refused"]


# ---------------------------------------------------------------------------------- unit: C-BIND


def _bind_arrays(world):
    _, ref = ev.read_npz(world["ref_copy"])
    return ref


def test_check_bind(world):
    ref = _bind_arrays(world)
    assert ev.check_bind(dict(ref), ref, ref["xsec_flat"])["pass"]
    r = ev.check_bind(dict(ref, shape=ref["shape"].astype(np.float64)), ref, ref["xsec_flat"])
    assert not r["pass"] and not r["shape_bits_equal"] and r["xsec_flat_bytes_equal"]
    r = ev.check_bind(dict(ref, extra=np.zeros(1)), ref, ref["xsec_flat"])
    assert not r["pass"] and not r["members_exact"]
    x = np.array(ref["xsec_flat"], copy=True)
    k = int(np.flatnonzero(x)[0])
    x[k] = np.nextafter(x[k], np.inf)
    r = ev.check_bind(dict(ref), ref, x)
    assert not r["pass"] and not r["captured_equals_remade"] and r["xsec_flat_bytes_equal"]
    r = ev.check_bind(dict(ref, xsec_flat=x), ref, x)
    assert not r["pass"] and r["n_differ"] == 1
    m = json.loads(str(ref["meta"]))
    r = ev.check_bind(dict(ref, meta=np.array(json.dumps(dict(m, slurm_job="9")))), ref, ref["xsec_flat"])
    assert r["pass"], "a per-run field must not matter"
    r = ev.check_bind(dict(ref, meta=np.array("{not json")), ref, ref["xsec_flat"])
    assert not r["pass"] and not r["meta_equal_except_per_run"]


# ---------------------------------------------------------------------------------- unit: builder-side faults


def _pins(world):
    b = world["base"]["shared"]
    return {"fine_map": ec.FINE_MAP_SHA256, "npz": b["npz"][1], "bkg": b["bkg"][1], "ref": b["ref"][1],
            "code_pin": ec.CODE_PIN}


def _file_p(products, world, **kw):
    p = dict(products)
    return ev.check_file(kw.get("t", p["t"]), kw.get("c", p["c"]), p["indep"], p["t"]["wpush"],
                         kw.get("expected_c", p["expected_c"]), p["flat_index"], kw.get("meta", p["meta"]),
                         kw.get("cj_raw", p["cj_raw"]), kw.get("cjson", p["cjson"]), kw.get("pins", _pins(world)))


def test_check_file_with_pins(products, world):
    assert _file_p(products, world)["pass"]
    assert not _file_p(products, world, pins={})["pass"], "the pinned digests are required"


def test_check_file_map_from_a_faulty_builder(products, world):
    c, exp = copy_t(products["c"]), dict(products["expected_c"])
    k = int(np.flatnonzero(c["fine_to_cell"] < 0)[0])         # an unreported fine cell joins R03: no integral moves
    for d in (c, exp):
        d["fine_to_cell"] = np.array(d["fine_to_cell"], copy=True)
        d["fine_to_cell"][k] = 3
    cj = json.loads(products["cj_raw"])
    cj["fine_map_sha256_int32le"] = hashlib.sha256(c["fine_to_cell"].tobytes()).hexdigest()
    raw = (json.dumps(cj, indent=1) + "\n").encode()
    r = _file_p(products, world, c=c, expected_c=exp, cj_raw=raw, cjson=cj)
    assert all(r["constants"].values()) and not r["constants_vs_input"]["fine_to_cell_digest"] and not r["pass"]


@pytest.mark.parametrize("key,pin", [("input_npz_sha256", "npz"), ("bkg_dump_sha256", "bkg"),
                                     ("result_sha256", "ref"), ("code_pin", "code_pin")])
def test_check_file_meta_from_a_faulty_builder(products, world, key, pin):
    meta = dict(products["meta"], **{key: "0" * 40})
    t, c = copy_t(products["t"]), copy_t(products["c"])
    t["meta"] = c["meta"] = np.array(json.dumps(meta))
    cj = dict(json.loads(products["cj_raw"]), **{key: "0" * 40})
    raw = (json.dumps(cj, indent=1) + "\n").encode()
    r = _file_p(products, world, t=t, c=c, meta=meta, cj_raw=raw, cjson=cj)
    assert r["meta_equal"] and r["constants_json_equal"] and not r["constants_vs_input"][f"meta_{key}"]
    assert not r["pass"]


@pytest.mark.parametrize("field", ["f", "flux", "pot", "edges", "units_label"])
def test_check_file_json_from_a_faulty_builder(products, world, field):
    cj = json.loads(products["cj_raw"])
    if field == "f":
        cj["f_cm2_per_nucleon"] = [x * (1 + 1e-12) for x in cj["f_cm2_per_nucleon"]]
    elif field == "flux":
        cj["flux_per_m2_per_POT_by_pt_bin"][0] *= 1 + 1e-12
    elif field == "pot":
        cj["data_pot"] *= 2
    elif field == "edges":
        cj["edges"]["W"][1] += 1e-9
    else:
        cj["flux_m2_per_POT_by_pt_bin"] = cj.pop("flux_per_m2_per_POT_by_pt_bin")
    raw = (json.dumps(cj, indent=1) + "\n").encode()
    r = _file_p(products, world, cj_raw=raw, cjson=cj)
    assert r["constants_json_equal"] and not r["constants_json_vs_arrays"] and not r["pass"], field


def test_check_self_independent_formula_with_a_wrong_extractor(products):
    """The driver's extractor 1e-12 off, and the reference made with it: only the independent formula sees it."""
    def wrong(*a, **k):
        x, g = products["extract"](*a, **k)
        return x * (1 + 1e-12), g
    t, c = products["t"], copy_t(products["c"])
    samp = np.column_stack([t[n] for n in ev.TRUTH_COLS])
    d = {"edges": [c[f"edges_{i}"] for i in range(5)], "denom_nd": c["denom_nd"], "flux": c["flux"],
         "data_pot": c["data_pot"], "n_nucleons": c["n_nucleons"]}
    ref = ev.driver_maps(d, t["w_unfolded"], t["w_prior"], samp, wrong)["xs"].ravel(order="C")
    c["xsec_flat"] = ref
    f = ev.cell_integrals(ref, c["volume"], c["fine_to_cell"])
    r = ev.check_self(t, c, ref, f, wrong, 5)
    assert r["xsec_bit_for_bit"] and r["saved_xsec_equals_reference"] and r["f_from_file_max_rel"] <= ev.F_RTOL
    assert r["independent_formula_max_rel"] > ev.INDEP_RTOL and not r["pass"]


def test_contributions_use_each_pt_bins_flux():
    fm = np.array([0, 1, 2, 3])
    good = np.ones((2, 2), bool)
    s, _ = ev.contributions(np.array([1.0, 1.0, 1.0, 1.0]), np.array([0, 1, 2, 3]), np.ones((2, 2)),
                            np.array([1.0, 4.0]), 1.0, 1.0, good, fm, 2)
    assert list(s[:4]) == [1e4, 1e4, 2.5e3, 2.5e3]


# ---------------------------------------------------------------------------------- unit: accepted(), more


def _done(out_copy):
    return json.loads((out_copy / ev.DONE).read_text())


def _write_done(out_copy, d):
    (out_copy / ev.DONE).unlink()
    (out_copy / ev.DONE).write_text(json.dumps(d))


@pytest.mark.parametrize("edit", ["finding_sizes", "acceptance_field", "acceptance_not_dict", "extra_key",
                                  "products_only", "controls_verdict_only", "failed_controls_only"])
def test_accepted_refuses_each_marker_edit(out_copy, edit):
    d = _done(out_copy)
    if edit == "finding_sizes":
        d["finding_sizes"]["C-COMPLETE"]["max_abs_c_minus_1"] = 0.0
    elif edit == "acceptance_field":
        d["acceptance"]["rehash_equal"] = False
    elif edit == "acceptance_not_dict":
        d["acceptance"] = True
    elif edit == "extra_key":
        d["note"] = "x"
    elif edit == "products_only":
        d["products"] = dict(d["products"], **{"run.json": "0" * 64})
    elif edit == "controls_verdict_only":
        d["controls_verdict"] = "FAIL"
    else:
        d["failed_controls"] = ["C-F"]
    _write_done(out_copy, d)
    assert not acc(out_copy), edit


def test_accepted_linked_root(out_copy):
    link = out_copy.parent / "linked"
    link.symlink_to(out_copy)
    assert acc(out_copy) and not acc(link, bound=hashlib.sha256((out_copy / ev.SUMS).read_bytes()).hexdigest())


# ---------------------------------------------------------------------------------- the Mac launcher


LAUNCH = EVW.parents[1] / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/evw5d-20261125/launch"


def _stubs(tmp: Path, shm: Path, remote: dict | None = None) -> dict:
    """ssh runs its last argument locally (both hops), with /dev/shm mapped to `shm`; scp copies from `remote`."""
    b = tmp / "stubbin"
    b.mkdir()
    (b / "ssh").write_text('#!/bin/bash\nlast="${@: -1}"\nexec bash -c "${last//\\/dev\\/shm/' + str(shm) + '}"\n')
    m = json.dumps(remote or {})
    (b / "scp").write_text("#!/bin/bash\nsrc=\"${@: -2:1}\"; dst=\"${@: -1}\"\n" + sys.executable +
                           " -c 'import json,shutil,sys; m=json.loads(sys.argv[1]); s=sys.argv[2].split(\":\",1)[1]\n"
                           "p=[v+s[len(k):] for k,v in m.items() if s.startswith(k)]\n"
                           "sys.exit(1) if not p else shutil.copy(p[0], sys.argv[3])' '" + m + "' \"$src\" \"$dst\"\n")
    for f in ("ssh", "scp"):
        (b / f).chmod(0o755)
    return dict(os.environ, PATH=f"{b}:{os.environ['PATH']}", EVW5D_PY=sys.executable)


def test_launcher_propagates_a_remote_refusal(tmp_path):
    tmp_path = Path(os.path.realpath(tmp_path))
    ld = tmp_path / "launch"
    ld.mkdir()
    (ld / "evw5d_connect.sh").write_text("#!/bin/bash\necho refused >&2\nrm -f -- \"$1\"\nexit 9\n")
    sha = hashlib.sha256((ld / "evw5d_connect.sh").read_bytes()).hexdigest()
    (ld / "evw5d_launch.sh").write_text((LAUNCH / "evw5d_launch.sh").read_text().replace("__CONNECT_SHA256__", sha))
    shm = tmp_path / "shm"
    shm.mkdir()
    env = _stubs(tmp_path, shm)
    sess = tmp_path / "sess"
    sess.mkdir()
    r = subprocess.run(["bash", str(ld / "evw5d_launch.sh"), "connect", str(sess), "login27"], capture_output=True,
                       text=True, env=env)
    assert r.returncode == 9 and "script rc=9" in r.stdout, r.stdout + r.stderr
    assert list(shm.iterdir()) == [], "the staged copy was left"
    (ld / "evw5d_connect.sh").write_text("#!/bin/bash\nexit 0\n")           # not the approved bytes
    sess2 = tmp_path / "sess2"
    sess2.mkdir()
    r = subprocess.run(["bash", str(ld / "evw5d_launch.sh"), "connect", str(sess2), "login27"], capture_output=True,
                       text=True, env=env)
    assert r.returncode == 8


def launch_tree(tmp: Path) -> Path:
    """A copy of the checkout's layout (nd-unfolding/evw5d, nd-unfolding/ess_e and launch/) with the launcher's
    checker pin filled with the copied evw5d.py's sha256; returns the copied launcher."""
    top = tmp / "top"
    for sub in ("evw5d", "ess_e"):
        shutil.copytree(EVW.parent / sub, top / "nd-unfolding" / sub, ignore=shutil.ignore_patterns("__pycache__"))
    rel = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/evw5d-20261125/launch"
    (top / rel).mkdir(parents=True)
    w = hashlib.sha256((top / "nd-unfolding/evw5d/evw5d.py").read_bytes()).hexdigest()
    text = (LAUNCH / "evw5d_launch.sh").read_text()
    assert text.count("__EVW5D_PY_SHA256__") == 1
    (top / rel / "evw5d_launch.sh").write_text(text.replace("__EVW5D_PY_SHA256__", w))
    return top / rel / "evw5d_launch.sh"


def forge_production(d: Path) -> str:
    """Rewrite a fixture bundle's run.json to carry the production pins (no --fixture), and re-make the manifest and
    the marker to match: a production-shaped bundle for the positive path of the consumer's check."""
    run = json.loads((d / "run.json").read_text())
    run.update(code_pin=ec.CODE_PIN, main_pin=ec.MAIN_PIN, argv=["evw5d.py", "--deploy", "x", "--out", "y"])
    for k in ec.SHARED:
        run["reads"][k]["copy_digest"] = ec.SHARED[k][1]
    rj = (json.dumps(run, indent=1) + "\n").encode()
    (d / "run.json").write_bytes(rj)
    digests = ev.parse_sums((d / ev.SUMS).read_text())
    digests["run.json"] = hashlib.sha256(rj).hexdigest()
    sums = ev.sums_text(digests).encode()
    (d / ev.SUMS).write_bytes(sums)
    fresh = ev.acceptance(d, digests)
    done = json.loads((d / ev.DONE).read_text())
    done.update(products=digests, sha256sums_sha256=hashlib.sha256(sums).hexdigest(), acceptance=fresh)
    (d / ev.DONE).unlink()
    (d / ev.DONE).write_text(json.dumps(done))
    return hashlib.sha256(sums).hexdigest()


def _fetch(launcher, env, d, bound):
    d.mkdir()
    return subprocess.run(["bash", str(launcher), "fetch-products", str(d), bound], capture_output=True, text=True,
                          env=env)


def test_launcher_fetch_products_runs_accepted(world, tmp_path):
    tmp_path = Path(os.path.realpath(tmp_path))
    launcher = launch_tree(tmp_path)
    remote_key = "/pscratch/sd/j/josephrb/evw5d-20261125-r2/evw5d"
    # a production-shaped bundle: fetched, verified and ACCEPTED
    prod = tmp_path / "prod-bundle"
    shutil.copytree(world["out"], prod)
    hp = forge_production(prod)
    assert ev.accepted(prod, hp), "the forged production bundle must pass the consumer's check"
    (tmp_path / "s1").mkdir()
    env = _stubs(tmp_path / "s1", tmp_path, {remote_key: str(prod)})
    r = _fetch(launcher, env, tmp_path / "ok", hp)
    assert r.returncode == 0 and "ACCEPTED" in r.stdout, r.stdout + r.stderr
    r = _fetch(launcher, env, tmp_path / "wrongbound", "0" * 64)
    assert r.returncode == 1 and "REFUSED" in r.stdout
    # the fixture bundle as it is: never a production result
    (tmp_path / "s2").mkdir()
    env2 = _stubs(tmp_path / "s2", tmp_path, {remote_key: str(world["out"])})
    h = hashlib.sha256((world["out"] / ev.SUMS).read_bytes()).hexdigest()
    r = _fetch(launcher, env2, tmp_path / "fixture", h)
    assert r.returncode == 1 and "REFUSED" in r.stdout and "scp weights.npz rc=0" in r.stdout
    # the FAIL bundle of test_fail_on_f
    bad = world["root"] / "failf-pristine"
    assert bad.is_dir(), "test_fail_on_f must run first (file order)"
    (tmp_path / "s3").mkdir()
    env3 = _stubs(tmp_path / "s3", tmp_path, {remote_key: str(bad)})
    r = _fetch(launcher, env3, tmp_path / "fail", hashlib.sha256((bad / ev.SUMS).read_bytes()).hexdigest())
    assert r.returncode == 1 and "REFUSED" in r.stdout
    # a changed checker is refused before it runs
    w = launcher.parents[8] / "nd-unfolding/evw5d/evw5d.py"
    w.write_text(w.read_text() + "\n# changed\n")
    r = _fetch(launcher, env, tmp_path / "changedchecker", hp)
    assert r.returncode == 8 and "not the approved bytes" in r.stdout, r.stdout + r.stderr


def test_launcher_fetch_refuses_an_unfilled_checker_pin(tmp_path):
    d = tmp_path / "x"
    d.mkdir()
    r = subprocess.run(["bash", str(LAUNCH / "evw5d_launch.sh"), "fetch-products", str(d), "a" * 64],
                       capture_output=True, text=True, env=_stubs(tmp_path, tmp_path, {}))
    assert r.returncode == 9 and "not filled in" in r.stdout



# ---------------------------------------------------------------------------------- revision 5 (codex-school r3)


def test_read_npz_refuses_duplicate_members(tmp_path):
    import zipfile as zf
    p = tmp_path / "dup.npz"
    np.savez(p, xsec_flat=np.ones(2), shape=np.array([2]), meta=np.array("{}"))
    with zf.ZipFile(p, "a") as z:
        import io as _io
        b = _io.BytesIO()
        np.save(b, np.zeros(2))
        with pytest.warns(UserWarning):
            z.writestr("xsec_flat.npy", b.getvalue())
    with pytest.raises(ValueError, match="distinct"):
        ev.read_npz(p)
    q = tmp_path / "ok.npz"
    np.savez(q, a=np.ones(1))
    assert sorted(ev.read_npz(q)[1]) == ["a"]


def test_check_bind_meta_is_type_strict(world):
    _, ref = ev.read_npz(world["ref_copy"])
    m = json.loads(str(ref["meta"]))
    assert "amplitude" in m
    bad = dict(m, amplitude=False if m["amplitude"] in (0, 0.0) else m["amplitude"])
    if bad["amplitude"] is not False:
        bad["amplitude"] = int(m["amplitude"]) if float(m["amplitude"]).is_integer() else m["amplitude"]
    r = ev.check_bind(dict(ref, meta=np.array(json.dumps(bad))), ref, ref["xsec_flat"])
    assert not r["pass"] and not r["meta_equal_except_per_run"]
    dup = str(ref["meta"])[:-1] + ', "iters": 5}'
    r = ev.check_bind(dict(ref, meta=np.array(dup)), ref, ref["xsec_flat"])
    assert not r["pass"], "a duplicate key in the meta"


def test_strict_json():
    with pytest.raises(ValueError):
        ev.strict_json('{"a": 1, "a": 2}')
    assert ev.strict_json('{"a": {"b": 1}}') == {"a": {"b": 1}}
    assert ev.canonical({"x": 1}) != ev.canonical({"x": True}) != ev.canonical({"x": 1.0})


def test_accepted_refuses_duplicate_keys_and_coerced_types(out_copy):
    raw = (out_copy / ev.DONE).read_text()
    assert raw.startswith("{")
    (out_copy / ev.DONE).unlink()
    (out_copy / ev.DONE).write_text('{"verdict": "FAIL", ' + raw[1:])
    assert not acc(out_copy), "a duplicate verdict key"
    d = json.loads(raw)
    d["acceptance"]["rehash_equal"] = 1
    _write_done(out_copy, d)
    assert not acc(out_copy), "an int where a bool was written"


@pytest.mark.parametrize("field", ["key", "formula", "axes"])
def test_check_file_schema_statements_from_a_faulty_builder(products, world, field):
    meta, cj = dict(products["meta"]), json.loads(products["cj_raw"])
    if field == "key":
        meta["key"] = cj["key"] = meta["key"].replace("index in the npz's MCgen", "rank among the selected rows")
    elif field == "formula":
        cj["formula"] = cj["formula"].replace("/ (completeness_f *", "* completeness_f / (")
    else:
        meta["truth_axes"] = cj["truth_axes"] = ["pz", "pt", "eavail", "q3", "W"]
    t, c = copy_t(products["t"]), copy_t(products["c"])
    t["meta"] = c["meta"] = np.array(json.dumps(meta))
    raw = (json.dumps(cj, indent=1) + "\n").encode()
    r = _file_p(products, world, t=t, c=c, meta=meta, cj_raw=raw, cjson=cj)
    assert r["meta_equal"] and r["constants_json_equal"] and not r["pass"], field


def test_check_self_independent_formula_isolated(products):
    """Equal and opposite errors in two equal-volume fine cells of one reported cell, in the extractor and the
    reference alike: the result, the saved constants and both f stay within their gates; only the formula sees it."""
    c, t = copy_t(products["c"]), products["t"]
    fm, vol, xs0 = c["fine_to_cell"], c["volume"], np.asarray(c["xsec_flat"])
    pair = None
    for cell in range(16):
        idx = np.flatnonzero((fm == cell) & (xs0 > 0))
        for i in idx:
            same = idx[(vol[idx] == vol[i]) & (idx != i)]
            if same.size:
                pair = (int(i), int(same[0]))
                break
        if pair:
            break
    assert pair, "no two equal-volume populated fine cells in one reported cell"
    i, j = pair
    eps = 1e-11
    delta = eps * min(xs0[i], xs0[j])

    def wrong(*a, **k):
        x, g = products["extract"](*a, **k)
        x = x.copy()
        x.flat[i] += delta
        x.flat[j] -= delta
        return x, g
    samp = np.column_stack([t[n] for n in ev.TRUTH_COLS])
    d = {"edges": [c[f"edges_{q}"] for q in range(5)], "denom_nd": c["denom_nd"], "flux": c["flux"],
         "data_pot": c["data_pot"], "n_nucleons": c["n_nucleons"]}
    ref = ev.driver_maps(d, t["w_unfolded"], t["w_prior"], samp, wrong)["xs"].ravel(order="C")
    c["xsec_flat"] = ref
    f = ev.cell_integrals(ref, c["volume"], c["fine_to_cell"])
    r = ev.check_self(t, c, ref, f, wrong, 5)
    assert r["xsec_bit_for_bit"] and r["saved_xsec_equals_reference"]
    assert r["f_from_file_max_rel"] <= ev.F_RTOL and r["volume_vs_edges_max_rel"] <= ev.VOLUME_RTOL
    assert r["independent_formula_max_rel"] > ev.INDEP_RTOL and not r["pass"], r


# ---------------------------------------------------------------------------------- restored (revision 4's job tests)
# revision 5's rewrite of the fetch test cut these two from the end of the file; the final mutation campaign at
# e01dd8637 found it (SB_SOURCE_CLOBBER and SB_OUT_LINK survived). Restored verbatim from 292b8a8bc.


def test_job_setup_runs_without_noclobber(job):
    """A setup that writes over an existing file must succeed, as it would under ESS (noclobber is the job's own)."""
    existing = job["tmp"] / "existing.txt"
    existing.write_text("old")
    job["setup"](f'echo new > "{existing}"\nreturn 0\n')
    r = job["run"]()
    done = json.loads((job["out"] / "logs" / "DONE-4242").read_text())
    assert existing.read_text() == "new\n", "the setup's own redirect was refused"
    assert "python3 is not root_6_28" in done["refused"], done     # it got past the setup


def test_job_refuses_a_dangling_out_link(job):
    (job["out"] / "evw5d").symlink_to(job["tmp"] / "nowhere")
    r = job["run"]()
    done = json.loads((job["out"] / "logs" / "DONE-4242").read_text())
    assert r.returncode == 2 and "evw5d exists" in done["refused"]


# ---------------------------------------------------------------------------------- after the final campaign


def test_check_file_constants_json_raw_against_meant(products, world):
    """constants.json with one extra field: every operand still equals the arrays, so only the comparison with what
    was meant to be written sees it."""
    cj = dict(json.loads(products["cj_raw"]), note="x")
    raw = (json.dumps(cj, indent=1) + "\n").encode()
    r = _file_p(products, world, cj_raw=raw)
    assert r["constants_json_vs_arrays"] and not r["constants_json_equal"] and not r["pass"]


def test_check_self_cm2_exact_alone(products):
    """The saved 1e4 off by 5e-14 relative: inside the independent formula's 1e-13, outside the exact check."""
    c = copy_t(products["c"])
    c["cm2_per_m2"] = np.float64(1.0e4 * (1 + 5e-14))
    assert c["cm2_per_m2"] != 1.0e4
    r = _self(products, c=c)
    assert r["xsec_bit_for_bit"] and r["independent_formula_max_rel"] <= ev.INDEP_RTOL
    assert not r["cm2_per_m2_exact"] and not r["pass"]


# ---------------------------------------------------------------------------------- the connect's allocation check
# Attempt 1 (job 61997953, 2026-11-25) was cancelled by a false STOP: scontrol shows a PENDING job's node count as a
# range, NumNodes=1-1, and the check compared it with "1". The block below is extracted from the scripts as written
# (template and bound copy) and run against scontrol text in the real format.

SCONTROL = """JobId=61997953 JobName=evw5d
   UserId=josephrb(00000) GroupId=josephrb(00000) MCS_label=N/A
   Priority=69120 Nice=0 Account=m3246 QOS=regular_1
   JobState=PENDING Reason=None Dependency=(null)
   Requeue=0 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
   RunTime=00:00:00 TimeLimit={tl} TimeMin=N/A
   Partition=regular_milan_ss11 AllocNode:Sid=login31:1
   {array}NumNodes={nn} NumCPUs=256 NumTasks=1 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
   OverSubscribe=NO Contiguous=0 Licenses=(null) Network=(null)
"""


def _alloc_block(path: Path) -> str:
    lines = path.read_text().split("\n")
    i = lines.index('sj=$(scontrol show job "$job")')
    j = lines.index("fi", i)
    return "\n".join(lines[i:j + 1])


def _run_alloc(tmp: Path, block: str, text: str) -> tuple[int, str, bool]:
    b = tmp / "bin"
    b.mkdir(exist_ok=True)
    (tmp / "scontrol.txt").write_text(text)
    marker = tmp / "cancelled"
    if marker.exists():
        marker.unlink()
    for name, body in (("scontrol", f'cat "{tmp / "scontrol.txt"}"'), ("scancel", f'touch "{marker}"'),
                       ("sacct", "true"), ("sleep", "true")):
        (b / name).write_text(f"#!/bin/bash\n{body}\n")
        (b / name).chmod(0o755)
    script = "TLIMIT=00:30:00; job=61997953\nfinish() { echo FINISH $1; exit $1; }\n" + block + "\necho PASSED\n"
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                       env=dict(os.environ, PATH=f"{b}:{os.environ['PATH']}"))
    return r.returncode, r.stdout, marker.exists()


@pytest.mark.parametrize("which", ["template", "bound"])
def test_connect_allocation_check(tmp_path, which):
    path = LAUNCH / "evw5d_connect.sh" if which == "template" else LAUNCH / "bound" / "evw5d_connect.sh"
    block = _alloc_block(path)
    assert block == _alloc_block(LAUNCH / "evw5d_connect.sh"), "the bound check differs from the template's"
    cases = [  # (TimeLimit, NumNodes, array line, accepted)
        ("00:30:00", "1-1", "", True),        # attempt 1's pending job, verbatim fields
        ("00:30:00", "1", "", True),          # a placed job
        ("00:30:00", "2-2", "", False),
        ("00:30:00", "1-2", "", False),
        ("00:30:00", "2", "", False),
        ("00:30:00", "11", "", False),
        ("01:00:00", "1-1", "", False),
        ("00:30:00", "1-1", "ArrayJobId=61997953 ArrayTaskId=0 ", False),
    ]
    for tl, nn, arr, ok in cases:
        rc, out, cancelled = _run_alloc(tmp_path, block, SCONTROL.format(tl=tl, nn=nn, array=arr))
        if ok:
            assert rc == 0 and "PASSED" in out and not cancelled, (tl, nn, arr, out)
        else:
            assert rc == 6 and "FINISH 6" in out and cancelled, (tl, nn, arr, out)

