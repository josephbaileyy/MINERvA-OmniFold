#!/usr/bin/env python3
"""End-to-end test of ess_capture.py on a synthetic experiment, run off the cluster against a real deploy at CODE_PIN.

    python3 test_ess_capture.py --repo <a local clone of the repository> [--keep <dir>]

What it does, in a new temporary directory:
1. a shared clone of --repo checked out at CODE_PIN (the producer's code), and a commit object (not HEAD) that adds a
   synthetic fd_data_product_cpl.json to MAIN_PIN's tree, so the fixture's main pin carries the real H2 definition;
2. a synthetic of_inputs npz and background dump on the real fine grid (every reported cell populated), placed under
   a "protected" directory;
3. the reference product: the deploy's own s5p_numerics.py run on them with the production arguments
   (configuration R, 5 iterations, data construction, base pair) at the fixture's thread count;
4. PASS: ess_capture.py --fixture must exit 0 with the binding equal, every check true, the cell sums equal to f, and
   (A), (B) and the prior summarized for the 16 cells and globally;
5. STOP: the same with a reference whose xsec_flat differs by one ulp in one entry must exit 8, write STOP.json and
   no ess.json;
6. the read guard: with it installed, a plain open() of a protected file raises, an O_NOATIME-flagged os.open of it
   (the flag substituted, as macOS has none) and a plain read under the allowed root do not;
7. --fixture is refused inside Slurm (SLURM_JOB_ID set), and summary() on known numbers.
The O_NOATIME flag is substituted by O_NONBLOCK and the atime comparison is off, both only through --fixture. Off the
cluster there is no ROOT: the driver imports it only for ``ROOT.gROOT.SetBatch`` at module level
(unfold_2d_omnifold_unbinned.py:21-23 @ abdc88c5), so the test puts a stub ROOT module on PYTHONPATH for its
subprocesses; the cluster job imports root_6_28's real ROOT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ess_capture as ec  # noqa: E402

DP_REL = ec.REPO["dp"][0]


STUB = """class _Any:
    def __getattr__(self, k):
        return _Any()

    def __call__(self, *a, **k):
        return _Any()


def __getattr__(name):
    return _Any()
"""


def stub_env(root: Path) -> dict:
    d = root / "stubs"
    if not d.exists():
        d.mkdir()
        (d / "ROOT.py").write_text(STUB)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(d))
    env.pop("SLURM_JOB_ID", None)
    return env


def sh(*cmd, cwd=None, env=None, check=True) -> subprocess.CompletedProcess:
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, env=env, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"{' '.join(map(str, cmd))}: rc {r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r


def sha(path) -> str:
    return ec.sha256_file(path)


def make_deploy(repo: Path, root: Path) -> Path:
    d = root / "deploy"
    sh("git", "clone", "-q", "--shared", "--no-checkout", repo, d)
    sh("git", "-C", d, "-c", "advice.detachedHead=false", "checkout", "-q", ec.CODE_PIN)
    return d


def fixture_main_commit(deploy: Path, dp_bytes: bytes) -> str:
    """A commit whose tree is MAIN_PIN's plus the synthetic data product, made without moving HEAD."""
    env = dict(os.environ, GIT_INDEX_FILE=str(deploy / ".git" / "ess-fixture-index"),
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    sh("git", "-C", deploy, "read-tree", ec.MAIN_PIN, env=env)
    blob = subprocess.run(["git", "-C", str(deploy), "hash-object", "-w", "--stdin"], input=dp_bytes,
                          capture_output=True, check=True).stdout.decode().strip()
    sh("git", "-C", deploy, "update-index", "--add", "--cacheinfo", f"100644,{blob},{DP_REL}", env=env)
    tree = sh("git", "-C", deploy, "write-tree", env=env).stdout.strip()
    commit = sh("git", "-C", deploy, "commit-tree", tree, "-p", ec.MAIN_PIN, "-m", "ess fixture", env=env).stdout.strip()
    os.unlink(deploy / ".git" / "ess-fixture-index")
    return commit


def synthetic_inputs(deploy: Path, prot: Path, n_mc: int = 6000, n_data: int = 4000, n_bkg: int = 400):
    sys.path.insert(0, str(deploy / "nd-unfolding"))
    import s5p_stage1_inspect as s1
    rng = np.random.default_rng(20261110)
    edges = [np.asarray(s1.FINE[a], float) for a in s1.AXES]

    def coords(n, shift=0.0):
        return np.column_stack([rng.uniform(0.0, 1.6, n), rng.uniform(1.5, 10.0, n) + shift,
                                rng.uniform(0.0, 2.2, n), rng.uniform(0.0, 4.0, n),
                                rng.uniform(0.5, 3.2, n)]).astype(np.float32)

    gen = coords(n_mc)
    reco = (gen * rng.normal(1.0, 0.05, gen.shape)).astype(np.float32)
    pass_truth = rng.random(n_mc) < 0.97
    pass_reco = rng.random(n_mc) < 0.8
    w_truth = rng.uniform(0.5, 1.5, n_mc)
    w_reco = w_truth.copy()
    measured = (coords(n_data, 0.2) * rng.normal(1.0, 0.05, (n_data, 5))).astype(np.float32)
    shape = tuple(len(e) - 1 for e in edges)
    sel, _ = np.histogramdd(gen[pass_truth].astype(float), bins=edges, weights=w_truth[pass_truth])
    denom = sel * 1.15
    arrays = {"MCgen": gen, "MCreco": reco, "measured": measured, "pass_reco": pass_reco, "pass_truth": pass_truth,
              "w_truth": w_truth, "w_reco": w_reco, "measured_weights": np.ones(n_data), "denom_nd": denom,
              "flux": rng.uniform(1e-9, 2e-9, shape[0]), "data_pot": np.float64(1.0e20),
              "n_nucleons": np.float64(3.0e30), "nedges": np.int64(5)}
    arrays.update({f"edges_{i}": e for i, e in enumerate(edges)})
    npz = prot / "of_inputs_5d.npz"
    np.savez_compressed(npz, **arrays)
    bkg = prot / "bkg_dump.npz"
    np.savez_compressed(bkg, bkg_reco=coords(n_bkg).astype(np.float32), bkg_w=rng.uniform(0.5, 1.5, n_bkg),
                        bkg_nd=np.zeros(shape), meta=json.dumps({"npz_sha256": sha(npz)}))
    return npz, bkg


def reference_product(py: str, deploy: Path, npz: Path, bkg: Path, out: Path, threads: int, env: dict) -> Path:
    sh(py, deploy / "nd-unfolding" / "s5p_numerics.py", "--npz", npz, "--bkg", bkg,
       "--expect-npz-sha256", sha(npz), "--expect-bkg-sha256", sha(bkg), "--config", "R", "--iters", "5",
       "--construction", "data", "--pairs=-:-", "--tag", "data", "--threads", threads, "--out", out, env=env)
    return out / "data_b-_j-.npz"


def cell_integrals(deploy: Path, xsec_flat: np.ndarray, h2: dict) -> list:
    sys.path.insert(0, str(deploy / "nd-unfolding"))
    import s5p_stage1_inspect as s1
    cmap, _ = s1.coarse_map(s1.H2_EDGES)
    hm = np.asarray(h2["h2_to_reporting_cell"], int)
    fm = np.where(cmap >= 0, hm[cmap], -1)
    vol = s1.fine_volume()
    return [float((xsec_flat * vol)[fm == c].sum()) for c in range(16)]


def run_capture(py, deploy, fixture: dict, root: Path, tag: str, env_extra=None) -> tuple[int, Path, str]:
    fx = root / f"fixture-{tag}.json"
    fx.write_text(json.dumps(fixture))
    out_root = root / f"out-{tag}"
    out_root.mkdir()
    out = out_root / "ess"
    env = dict(stub_env(root), **(env_extra or {}))
    r = subprocess.run([py, str(HERE / "ess_capture.py"), "--deploy", str(deploy), "--out", str(out),
                        "--out-root", str(out_root), "--stage-dir", str(root / f"shm-{tag}"), "--fixture", str(fx)],
                       capture_output=True, text=True, env=env)
    return r.returncode, out, r.stdout + r.stderr


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--keep", type=Path, default=None, help="keep the work directory here (must not exist)")
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args(argv)
    py = sys.executable
    root = Path(tempfile.mkdtemp(prefix="ess-test-")) if a.keep is None else a.keep
    if a.keep is not None:
        root.mkdir(parents=True)
    results = {}
    try:
        deploy = make_deploy(a.repo.resolve(), root)
        prot = root / "protected"
        prot.mkdir()
        npz, bkg = synthetic_inputs(deploy, prot)
        ref = reference_product(py, deploy, npz, bkg, root / "refrun", a.threads, stub_env(root))
        ref_copy = prot / "data_b-_j-.npz"
        shutil.copyfile(ref, ref_copy)
        with np.load(ref_copy, allow_pickle=False) as z:
            xflat, shp, meta = np.array(z["xsec_flat"]), np.array(z["shape"]), str(z["meta"])
        h2_bytes = sh("git", "-C", deploy, "show", f"{ec.MAIN_PIN}:{ec.REPO['h2'][0]}").stdout.encode()
        f = cell_integrals(deploy, xflat, json.loads(h2_bytes))
        assert all(x > 0 for x in f), f"a synthetic reported cell is empty: {f}"
        dp_bytes = (json.dumps({"f": f}) + "\n").encode()
        main_c = fixture_main_commit(deploy, dp_bytes)
        base = {"main_pin": main_c, "threads": a.threads, "protected": [str(prot)], "noatime": os.O_NONBLOCK,
                "check_atime": False,
                "repo": {"h2": list(ec.REPO["h2"]), "dp": [DP_REL, hashlib.sha256(dp_bytes).hexdigest()]},
                "shared": {"npz": [str(npz), sha(npz), npz.stat().st_size],
                           "bkg": [str(bkg), sha(bkg), bkg.stat().st_size],
                           "ref": [str(ref_copy), sha(ref_copy), ref_copy.stat().st_size]}}

        # ---- PASS
        rc, out, log = run_capture(py, deploy, base, root, "pass")
        assert rc == 0, f"PASS run rc {rc}\n{log[-3000:]}"
        e = json.loads((out / "ess.json").read_text())
        assert e["binding"]["xsec_flat_bytes_equal"] and e["binding"]["captured_equals_remade"]
        assert e["meta_compare"]["equal_except_per_run_fields"], e["meta_compare"]
        for k in ("recomputed_xs_bytes_equal", "edges_equal_fine_grid", "event_index_counts_equal",
                  "fine_map_digest_equal", "volume_equal"):
            assert e["checks"][k] is True, (k, e["checks"])
        assert e["checks"]["cell_sum_vs_f_max_rel"] < 1e-9 and e["checks"]["f_vs_data_product_max_rel"] < 1e-12
        assert sorted(e["cells"]) == [f"R{c:02d}" for c in range(16)]
        for c, v in e["cells"].items():
            for kind in ("B_contribution", "A_final_weight", "prior_w_truth"):
                s = v[kind]
                assert s["n"] > 0 and 0 < s["n_eff"] <= s["n"] + 1e-9, (c, kind, s)
                assert s["max_share"] <= 1.0 and s["p99_over_mean"] > 0
            assert abs(v["B_contribution"]["sum"] / f[int(c[1:])] - 1) < 1e-9
        g = e["global"]["reported_16_cells"]
        assert g["A_final_weight"]["n"] == sum(v["A_final_weight"]["n"] for v in e["cells"].values())
        assert not (out / "STOP.json").exists() and not (out / "FAILED.json").exists()
        assert not (root / "shm-pass").exists(), "the staging directory was not removed"
        assert sorted(p.name for p in out.iterdir()) == ["ess.json", "product"]
        assert sorted(p.name for p in (out / "product").iterdir()) == ["data_b-_j-.npz"]
        results["pass"] = {"rc": rc, "n_eff_R00_B": e["cells"]["R00"]["B_contribution"]["n_eff"],
                           "checks": e["checks"], "data_side": e["data_side_refinement"]["reference_meta"]}

        # ---- STOP: a reference one ulp away in one entry
        bad = xflat.copy()
        i = int(np.flatnonzero(bad)[0])
        bad[i] = np.nextafter(bad[i], np.inf)
        ref_bad = prot / "bad" / "data_b-_j-.npz"
        ref_bad.parent.mkdir()
        np.savez_compressed(ref_bad, xsec_flat=bad, shape=shp, meta=meta)
        stop = json.loads(json.dumps(base))
        stop["shared"]["ref"] = [str(ref_bad), sha(ref_bad), ref_bad.stat().st_size]
        rc, out, log = run_capture(py, deploy, stop, root, "stop")
        assert rc == ec.RC_STOP, f"STOP run rc {rc}\n{log[-3000:]}"
        s = json.loads((out / "STOP.json").read_text())
        assert s["binding"]["xsec_flat_bytes_equal"] is False and s["binding"]["n_differ"] == 1
        assert not (out / "ess.json").exists() and "cells" not in s
        results["stop"] = {"rc": rc, "n_differ": s["binding"]["n_differ"]}

        # ---- a pinned digest that does not match: FAILED before any unfold
        wrong = json.loads(json.dumps(base))
        wrong["shared"]["bkg"][1] = "0" * 64
        rc, out, log = run_capture(py, deploy, wrong, root, "wrongpin")
        assert rc == ec.RC_FAILED and (out / "FAILED.json").exists() and not (out / "product").exists(), log[-2000:]
        results["wrong_pin"] = {"rc": rc}

        # ---- the read guard
        allowed = root / "allowed"
        allowed.mkdir()
        (allowed / "x").write_text("x")
        code = ("import os,sys; sys.path.insert(0, sys.argv[1]); import ess_capture as ec\n"
                "ec.install_guard([sys.argv[2]], [sys.argv[3]], os.O_NONBLOCK)\n"
                "p = os.path.join(sys.argv[2], 'bkg_dump.npz')\n"
                "try:\n    open(p, 'rb').read(1); print('PLAIN-READ-ALLOWED')\nexcept PermissionError: print('plain refused')\n"
                "fd = os.open(p, os.O_RDONLY | os.O_NONBLOCK); os.close(fd); print('flagged ok')\n"
                "open(os.path.join(sys.argv[3], 'x')).read(); print('allowed ok')\n")
        r = sh(py, "-c", code, HERE, prot, allowed)
        assert r.stdout.split("\n")[:3] == ["plain refused", "flagged ok", "allowed ok"], r.stdout
        results["guard"] = r.stdout.split("\n")[:3]

        # ---- --fixture inside Slurm
        rc, out, log = run_capture(py, deploy, base, root, "slurm", env_extra={"SLURM_JOB_ID": "1"})
        assert rc == 2 and "refused inside a Slurm job" in log, log
        results["fixture_in_slurm"] = {"rc": rc}

        # ---- summary() on known numbers
        sm = ec.summary(np.array([1.0, 1.0, 2.0]))
        assert abs(sm["n_eff"] - 16 / 6) < 1e-15 and abs(sm["max_share"] - 0.5) < 1e-15
        assert abs(sm["p99_over_mean"] - (1.98 / (4 / 3))) < 1e-12
        results["summary"] = "ok"
        print(json.dumps({"result": "ALL PASS", **results}, indent=1, default=str))
        return 0
    finally:
        if a.keep is None:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
