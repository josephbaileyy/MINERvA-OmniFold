"""The launch package end to end: ``sb1_submit.sh`` -> six batch scripts -> ``sb1_verify.py``.

A throwaway committed checkout holds this package, the real driver, ``n2/``, the guard and its shim,
a STUB OmniFold helper (unit weights; nothing is trained) and a fixture authorization record. The
submit script runs unmodified against ``fake_slurm.py`` (queue, then drain in dependency order) and
the synthetic inputs. The scheduler's elapsed, MaxRSS, MaxDiskRead and billing are SET by the test
(``FAKE_SLURM_OVERRIDES``): this checks the plumbing and the verdict rules, never performance.

    PYTHONPATH=$(root-config --libdir) python3.13 -m unittest test_launch_chain -v
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(HERE))
import make_fixture_omnifile as mk  # noqa: E402
from test_sb1_guarded import (DRIVER, GUARD, HELPER, N2, PKG_REL, REPO, STUB_HELPER,  # noqa: E402
                              git)

PKG_FILES = ("sb1_run.py", "branch_select.py", "sb1_hash.py", "sb1_admit.py", "sb1_verify.py",
             "make_manifest.py", "results/costs.json", "launch/ADMISSION-PROPOSAL.json",
             "launch/launch-spec.json", "launch/sb1_submit.sh",
             "launch/sb1_hash.sbatch", "launch/sb1_unfold.sbatch", "launch/sb1_identity.sbatch",
             "launch/sb1_cv.sbatch")
#: Literal ceilings (billing / 256 x limit), stated independently of the code that checks them.
CEILINGS = {"H0": 2 / 256 * 0.75, "UL": 50 / 60, "SL": 0.5, "J1": 64 / 256 * 0.75,
            "C": 64 / 256 * 40 / 60, "H1": 2 / 256 * 0.75}
AUTH = "docs/orchestration/AUTHORIZATION-20991231-sb1-fixture.md"
GOOD = {"sb1_UL": {"ElapsedRaw": 2600, "MaxRSS": "69191672K", "MaxDiskRead": "167271319K"},
        "sb1_SL": {"ElapsedRaw": 900, "MaxRSS": "15000000K", "MaxDiskRead": "2200000K"}}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stat(path):
    st = os.stat(path)
    return {"size": st.st_size, "mtime_ns": st.st_mtime_ns, "ino": st.st_ino}


class Chain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        t = cls.tmp = Path(cls._tmp.name).resolve()
        inputs = t / "inputs"
        inputs.mkdir()
        cls.uni, cls.cv = inputs / "uni.root", inputs / "cv.root"
        mk.write_fixture(str(cls.uni), rows=3000, extra=6)
        mk.write_fixture(str(cls.cv), rows=3000, extra=0, seed=7)
        cls.mc = Path(mk.write_flux(str(inputs / "flux.root")))
        cls.root = cls.make_checkout(t / "code")
        cls.bin = t / "bin"
        cls.bin.mkdir()
        for tool in ("sbatch", "sacct"):
            p = cls.bin / tool
            p.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{HERE / "fake_slurm.py"}" {tool} "$@"\n')
            p.chmod(0o755)
        (t / "env.sh").write_text(f'export PYTHONPATH="{os.environ.get("PYTHONPATH", "")}"\n')
        cls.adm = cls.admission(t / "out")
        cls.chain_submit = cls.run_chain(cls.adm, "chain", GOOD)
        cls.out = t / "out"

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    @classmethod
    def make_checkout(cls, root):
        (root / "nd-unfolding").mkdir(parents=True)
        (root / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
        for rel in (DRIVER, GUARD, f"{N2}/__init__.py", f"{N2}/execution.py",
                    *(f"{PKG_REL}/{p}" for p in PKG_FILES)):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / rel, root / rel)
        shutil.copytree(REPO / "nd-unfolding/mnv_guard_shim", root / "nd-unfolding/mnv_guard_shim",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (root / HELPER).parent.mkdir(parents=True, exist_ok=True)
        (root / HELPER).write_text(STUB_HELPER)
        spec_path = root / PKG_REL / "launch" / "launch-spec.json"
        spec = json.loads(spec_path.read_text())
        spec["inputs"] = {"omnifile_universe": str(cls.uni), "omnifile_cv": str(cls.cv),
                          "mcfile": str(cls.mc)}
        spec["unmatched_references"].update(UL_SL="", C="")
        spec_path.write_text(json.dumps(spec, indent=1) + "\n")
        subprocess.run([sys.executable, root / PKG_REL / "make_manifest.py"], check=True,
                       capture_output=True)
        git(root, "init", "-q")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fixture package")
        cls.pkg_commit = git(root, "rev-parse", "HEAD")
        manifest_sha = sha(root / PKG_REL / "manifest" / "expected-code.json")
        (root / AUTH).parent.mkdir(parents=True, exist_ok=True)
        (root / AUTH).write_text("# FIXTURE authorization for the launch-chain test only\n"
                                 f"package commit {cls.pkg_commit}\nmanifest sha256 {manifest_sha}\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fixture authorization")
        return root

    @classmethod
    def admission(cls, outroot, **override):
        root = cls.root
        manifest = json.loads((root / PKG_REL / "manifest" / "expected-code.json").read_text())
        head = git(root, "rev-parse", "HEAD")
        adm = {"schema": "sb1-admission/1", "status": "ADMITTED",
               "decision": "FIXTURE: run the fixed SB1 package under its cap",
               "authorization": {"path": AUTH, "sha256": sha(root / AUTH)},
               "checkout": str(root), "code": {"commit": head, "package_commit": cls.pkg_commit,
                                               "modules": manifest["modules"]},
               "launch_spec_sha256": sha(root / PKG_REL / "launch" / "launch-spec.json"),
               "inputs_observed": {str(p): stat(p) for p in (cls.uni, cls.cv, cls.mc)},
               "outroot": str(outroot), "ceiling_node_h": 2.0,
               "jobs": [{"id": k, "ceiling_node_h": v} for k, v in CEILINGS.items()],
               "cannot_authorize": ["a production change"]}
        adm.update(override)
        path = cls.tmp / f"admission-{Path(outroot).name}.json"
        path.write_text(json.dumps(adm, indent=1))
        return path

    @classmethod
    def env(cls, state, overrides):
        env = dict(os.environ, PATH=f"{cls.bin}:{os.environ['PATH']}", SB1_SBATCH="sbatch",
                   SB1_ENV_SETUP=str(cls.tmp / "env.sh"), SB1_PY=sys.executable,
                   FAKE_SLURM_STATE=str(cls.tmp / f"{state}.json"),
                   FAKE_SLURM_OVERRIDES=json.dumps(overrides), PYTHONDONTWRITEBYTECODE="1")
        for k in [k for k in env if k.startswith("MNV_GUARD")]:
            env.pop(k)
        return env

    @classmethod
    def run_chain(cls, adm, state, overrides):
        env = cls.env(state, overrides)
        sub = subprocess.run(["bash", cls.root / PKG_REL / "launch" / "sb1_submit.sh", adm],
                             env=env, capture_output=True, text=True)
        if sub.returncode == 0:
            subprocess.run([sys.executable, HERE / "fake_slurm.py", "drain"], env=env, check=True)
        return sub

    def verdict(self, outroot, sacct):
        r = subprocess.run([sys.executable, self.root / PKG_REL / "sb1_verify.py", "verdict",
                            "--outroot", outroot, "--admission", self.out / "admission.json",
                            "--sacct", sacct], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        return json.loads(r.stdout)

    def test_the_chain_runs_and_the_verifier_passes_it(self):
        self.assertEqual(self.chain_submit.returncode, 0, self.chain_submit.stderr[-3000:])
        st = json.loads((self.tmp / "chain.json").read_text())
        states = {j["opts"]["job-name"]: j["state"] for j in st["jobs"].values()}
        self.assertEqual(states, {k: "COMPLETED" for k in
                                  ("sb1_H0", "sb1_UL", "sb1_SL", "sb1_J1", "sb1_C", "sb1_H1")})
        deps = {j["opts"]["job-name"]: j["opts"].get("dependency") for j in st["jobs"].values()}
        ids = json.loads((self.out / "submission.json").read_text())["jobs"]
        self.assertEqual(deps["sb1_SL"], f"afterok:{ids['UL']}")
        self.assertEqual(deps["sb1_H1"], "afterany:" + ":".join(ids[k] for k in
                                                                ("H0", "UL", "SL", "J1", "C")))
        times = {j["opts"]["job-name"]: j["opts"]["time"] for j in st["jobs"].values()}
        self.assertEqual(times, {"sb1_H0": "00:45:00", "sb1_UL": "00:50:00", "sb1_SL": "00:30:00",
                                 "sb1_J1": "00:45:00", "sb1_C": "00:40:00", "sb1_H1": "00:45:00"})
        v = json.loads((self.out / "H1" / "verdict.json").read_text())
        crit = {k: x["verdict"] for k, x in v["criteria"].items()}
        self.assertEqual(crit, {"P": "PASS", "S1": "PASS", "NC": "PASS", "S2": "PASS",
                                "S3": "PASS", "S4": "PASS", "S5": "PASS",
                                "S6": crit["S6"]}, v["criteria"].get("P"))
        self.assertEqual(v["overall"], "PASS")
        self.assertTrue(v["within_ceiling"])

    def mutated(self, name, receipt_edit=None, sacct_edit=None, drop=None):
        dst = self.tmp / f"mut-{name}"
        shutil.copytree(self.out, dst)
        sub = json.loads((dst / "submission.json").read_text())
        for rel, fn in (receipt_edit or {}).items():
            p = dst / rel
            rec = json.loads(p.read_text())
            fn(rec)
            p.write_text(json.dumps(rec))
        if drop:
            (dst / drop).unlink()
        rows = (self.out / "H1" / "sacct.psv").read_text().splitlines()
        if sacct_edit:
            head = rows[0].split("|")
            for i, line in enumerate(rows[1:], 1):
                cells = dict(zip(head, line.split("|")))
                sacct_edit(cells, sub["jobs"])
                rows[i] = "|".join(cells[h] for h in head)
        sacct = dst / "sacct-mut.psv"
        sacct.write_text("\n".join(rows) + "\n")
        return dst, sacct

    def test_too_many_bytes_read_fails_s2(self):
        def edit(c, ids):
            if c["JobID"] == f"{ids['SL']}.batch":
                c["MaxDiskRead"] = "10.5G"                    # 11.27e9 B: over 10 GB
        v = self.verdict(*self.mutated("s2", sacct_edit=edit))
        self.assertEqual((v["criteria"]["S2"]["verdict"], v["overall"]), ("FAIL", "FAIL"))

    def test_a_mib_value_is_not_read_as_kib(self):
        def edit(c, ids):
            if c["JobID"] == f"{ids['SL']}.batch":
                c["MaxRSS"] = "31000M"                         # 32.5e9 B: over 30 GB
        v = self.verdict(*self.mutated("units", sacct_edit=edit))
        self.assertEqual(v["criteria"]["S3"]["verdict"], "FAIL")
        self.assertAlmostEqual(v["criteria"]["S3"]["sl_gb"], 31000 * 1024 ** 2 / 1e9, places=6)

    def test_slow_selective_arm_fails_s4(self):
        def edit(c, ids):
            if c["JobID"] == ids["SL"]:
                c["ElapsedRaw"] = "1301"                       # 0.5004 x 2600
        v = self.verdict(*self.mutated("s4", sacct_edit=edit))
        self.assertEqual((v["criteria"]["S4"]["verdict"], v["overall"]), ("FAIL", "FAIL"))

    def test_a_loader_byte_difference_fails_s1(self):
        def edit(rec):
            rec["loaders"][0]["digests"]["[0]"] = "0" * 64
        v = self.verdict(*self.mutated("s1", receipt_edit={"J1/selective_data.json": edit}))
        self.assertEqual((v["criteria"]["S1"]["verdict"], v["overall"]), ("FAIL", "FAIL"))

    def test_a_missing_receipt_is_inconclusive_not_pass(self):
        v = self.verdict(*self.mutated("missing", drop="SL/receipt.json"))
        self.assertEqual(v["overall"], "INCONCLUSIVE")

    def test_an_input_changed_between_h0_and_h1_is_not_a_pass(self):
        def edit(rec):
            path = next(iter(rec["files"]))
            rec["files"][path]["sha256"] = "1" * 64
        v = self.verdict(*self.mutated("h1", receipt_edit={"H1/hashes.json": edit}))
        self.assertNotEqual(v["criteria"]["P"]["verdict"], "PASS")
        self.assertNotEqual(v["overall"], "PASS")

    def test_a_wrong_executed_digest_is_not_a_pass(self):
        def edit(rec):
            rec["identity"]["executed"][-1]["sha256"] = "2" * 64
        v = self.verdict(*self.mutated("prov", receipt_edit={"SL/receipt.json": edit}))
        self.assertEqual(v["criteria"]["P"]["verdict"], "FAIL")
        self.assertNotEqual(v["overall"], "PASS")

    def test_a_guard_record_from_another_root_is_not_a_pass(self):
        dst = self.tmp / "mut-inventory"
        shutil.copytree(self.out, dst)
        p = dst / "SL" / "inventory.jsonl"
        recs = [json.loads(line) for line in p.read_text().splitlines()]
        recs[0]["repo_origins_outside_expect_root"] = 1
        p.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
        v = self.verdict(dst, self.out / "H1" / "sacct.psv")
        self.assertEqual(v["criteria"]["P"]["verdict"], "FAIL")
        self.assertIn("guard_inventories", v["criteria"]["P"]["problems"])

    def test_the_ledger_adds_charges_and_unfinished_ceilings(self):
        r = subprocess.run([sys.executable, self.root / PKG_REL / "sb1_verify.py", "ledger",
                            "--admission", self.out / "admission.json",
                            "--sacct", self.out / "H1" / "sacct.psv"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        last = r.stdout.strip().splitlines()[-1]
        st = json.loads((self.tmp / "chain.json").read_text())
        el = {j["opts"]["job-name"]: j["elapsed"] for j in st["jobs"].values()}
        # H1 is still running when its own sacct is taken, so it counts at its ceiling
        want = (2600 + 900) / 3600 + 64 / 256 * (el["sb1_J1"] + el["sb1_C"]) / 3600 \
            + 64 / 256 * el["sb1_H0"] / 3600 + CEILINGS["H1"]
        got = float(last.split("=")[1].split()[0])
        self.assertAlmostEqual(got, want, places=3, msg=r.stdout)

    def test_a_proposal_cannot_be_submitted(self):
        adm = self.admission(self.tmp / "out-proposal",
                             status="PROPOSAL-NOT-AN-AUTHORIZATION")
        sub = self.run_chain(adm, "proposal", GOOD)
        self.assertNotEqual(sub.returncode, 0)
        self.assertIn("only an ADMITTED record", sub.stderr)
        self.assertFalse((self.tmp / "out-proposal").exists())
        self.assertFalse((self.tmp / "proposal.json").exists())    # nothing was queued

    def test_draft_fills_only_mechanical_fields_and_checks(self):
        adm = json.loads(self.admission(self.tmp / "out-draft").read_text())
        prop = dict(adm, status="PROPOSAL-NOT-AN-AUTHORIZATION",
                    authorization={"path": None, "sha256": None}, checkout=None, outroot=None,
                    code=dict(adm["code"], commit=None, package_commit=None))
        pp = self.tmp / "proposal.in.json"
        pp.write_text(json.dumps(prop))
        out = self.tmp / "drafted.json"
        r = subprocess.run([sys.executable, self.root / PKG_REL / "sb1_admit.py", "draft",
                            "--proposal", pp, "--authorization", AUTH, "--package-commit",
                            adm["code"]["package_commit"], "--out", out],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(out.read_text())
        self.assertEqual({k: got[k] for k in ("decision", "jobs", "inputs_observed",
                                               "launch_spec_sha256", "ceiling_node_h")},
                         {k: adm[k] for k in ("decision", "jobs", "inputs_observed",
                                               "launch_spec_sha256", "ceiling_node_h")})
        self.assertEqual((got["status"], got["code"]["commit"], got["checkout"]),
                         ("ADMITTED", adm["code"]["commit"], str(self.root)))
        r = subprocess.run([sys.executable, self.root / PKG_REL / "sb1_admit.py", "draft",
                            "--proposal", out, "--authorization", AUTH, "--package-commit",
                            adm["code"]["package_commit"], "--out", self.tmp / "again.json"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 3, "an admitted record is not a proposal")

    def admit(self, adm, root=None):
        root = root or self.root
        r = subprocess.run([sys.executable, root / PKG_REL / "sb1_admit.py", "check",
                            "--admission", adm], capture_output=True, text=True)
        return r.returncode, r.stderr

    def test_the_good_admission_holds(self):
        self.assertEqual(self.admit(self.admission(self.tmp / "out-good"))[0], 0)

    def test_each_admission_guard_refuses(self):
        cases = {
            "checkout": dict(checkout=str(self.tmp)),
            "ancestry": dict(code={**json.loads(self.adm.read_text())["code"],
                                   "package_commit": "0" * 40}),
            "spec": dict(launch_spec_sha256="0" * 64),
            "ceilings": dict(jobs=[{"id": k, "ceiling_node_h": v * (1.1 if k == "UL" else 1)}
                                   for k, v in CEILINGS.items()]),
            "input-stat": dict(inputs_observed={
                p: {**st, "mtime_ns": st["mtime_ns"] + 1}
                for p, st in json.loads(self.adm.read_text())["inputs_observed"].items()}),
            "commit": dict(code={**json.loads(self.adm.read_text())["code"], "commit": "1" * 40}),
        }
        why = {"checkout": "admitted checkout", "ancestry": "not an ancestor",
               "spec": "launch spec differs", "ceilings": "job ceilings",
               "input-stat": "no longer has", "commit": "is not HEAD"}
        for name, over in cases.items():
            with self.subTest(guard=name):
                rc, err = self.admit(self.admission(self.tmp / f"out-{name}", **over))
                self.assertEqual(rc, 3, err)
                self.assertIn(why[name], err)           # refused by this guard, not a later one

    def clone(self, name):
        dst = self.tmp / name
        subprocess.run(["git", "clone", "-q", str(self.root), str(dst)], check=True)
        return dst

    def admission_for(self, root, name, pkg_commit):
        adm = json.loads(self.admission(self.tmp / f"out-{name}").read_text())
        adm["checkout"] = str(root)
        adm["code"].update(commit=git(root, "rev-parse", "HEAD"), package_commit=pkg_commit)
        adm["authorization"]["sha256"] = sha(root / AUTH)
        path = self.tmp / f"admission-{name}-clone.json"
        path.write_text(json.dumps(adm))
        return path

    def test_a_dirty_tree_is_refused(self):
        root = self.clone("dirty-clone")
        with open(root / PKG_REL / "sb1_hash.py", "a") as fh:
            fh.write("# dirty\n")
        rc, err = self.admit(self.admission_for(root, "dirty", self.pkg_commit), root)
        self.assertEqual(rc, 3)
        self.assertIn("tracked files differ", err)

    def test_a_package_changed_after_its_commit_is_refused(self):
        # review c0 finding 1: change the package, regenerate the manifest, commit on top
        root = self.clone("changed-clone")
        with open(root / PKG_REL / "branch_select.py", "a") as fh:
            fh.write("# later edit\n")
        subprocess.run([sys.executable, root / PKG_REL / "make_manifest.py"], check=True,
                       capture_output=True)
        git(root, "commit", "-qam", "later edit")
        rc, err = self.admit(self.admission_for(root, "changed", self.pkg_commit), root)
        self.assertEqual(rc, 3)
        self.assertIn("changed after", err)

    def test_an_authorization_that_does_not_name_the_package_is_refused(self):
        root = self.clone("auth-clone")
        (root / AUTH).write_text("# FIXTURE authorization naming nothing\n")
        git(root, "commit", "-qam", "vague authorization")
        rc, err = self.admit(self.admission_for(root, "vague", self.pkg_commit), root)
        self.assertEqual(rc, 3)
        self.assertIn("does not name the package commit", err)

    def test_an_unadmitted_executed_module_is_not_a_pass(self):
        def edit(rec):
            rec["identity"]["executed"].append({"relpath": "elsewhere.py", "sha256": "3" * 64})
        v = self.verdict(*self.mutated("extra-mod", receipt_edit={"UL/receipt.json": edit}))
        self.assertEqual(v["criteria"]["P"]["verdict"], "FAIL")

    def test_a_receipt_input_stat_unlike_h0_is_not_a_pass(self):
        def edit(rec):
            k = next(iter(rec["inputs_end"]))
            rec["inputs_end"][k]["ino"] += 1
        v = self.verdict(*self.mutated("rstat", receipt_edit={"C/receipt.json": edit}))
        self.assertEqual(v["criteria"]["P"]["verdict"], "FAIL")

    def test_a_control_that_returned_a_loader_fails_nc(self):
        def edit(rec):
            rec["loaders"] = [{"tree": "mc_signal_reco"}]
        v = self.verdict(*self.mutated("nc", receipt_edit={"J1/control_omit.json": edit}))
        self.assertEqual((v["criteria"]["NC"]["verdict"], v["overall"]), ("FAIL", "FAIL"))

    def test_a_killed_selective_arm_is_inconclusive_not_fail(self):
        # review c0 finding 3: a node failure mid-loaders is missing evidence, not a difference
        def edit(rec):
            rec["status"], rec["loaders"] = "running", rec["loaders"][:2]
        v = self.verdict(*self.mutated("killed", receipt_edit={"SL/receipt.json": edit}))
        self.assertEqual((v["criteria"]["S1"]["verdict"], v["overall"]),
                         ("INCONCLUSIVE", "INCONCLUSIVE"))

    def test_a_real_difference_still_fails_when_later_trees_are_missing(self):
        def edit(rec):
            rec["status"], rec["loaders"] = "input-mismatch", rec["loaders"][:3]
            rec["loaders"][2]["digests"]["w_reco"] = "4" * 64
        v = self.verdict(*self.mutated("mismatch", receipt_edit={"SL/receipt.json": edit}))
        self.assertEqual((v["criteria"]["S1"]["verdict"], v["overall"]), ("FAIL", "FAIL"))

    def test_receipts_from_different_environments_are_not_a_pass(self):
        def edit(rec):
            rec["environment"]["sb1_env_setup_sha256"] = "5" * 64
        v = self.verdict(*self.mutated("envsha", receipt_edit={"SL/receipt.json": edit}))
        self.assertEqual(v["criteria"]["P"]["verdict"], "FAIL")
        self.assertIn("env_setup", v["criteria"]["P"]["problems"])

    def test_an_environment_changed_after_submission_stops_the_chain(self):
        env_sh = self.tmp / "env.sh"
        before = env_sh.read_text()
        adm = self.admission(self.tmp / "out-envchange")
        env = self.env("envchange", GOOD)
        sub = subprocess.run(["bash", self.root / PKG_REL / "launch" / "sb1_submit.sh", adm],
                             env=env, capture_output=True, text=True)
        self.assertEqual(sub.returncode, 0, sub.stderr[-2000:])
        try:
            env_sh.write_text(before + "# changed after submission\n")
            subprocess.run([sys.executable, HERE / "fake_slurm.py", "drain"], env=env, check=True)
        finally:
            env_sh.write_text(before)
        st = json.loads((self.tmp / "envchange.json").read_text())
        states = {j["opts"]["job-name"]: j["state"] for j in st["jobs"].values()}
        self.assertEqual(states["sb1_H0"], "FAILED")
        self.assertEqual({states[k] for k in ("sb1_UL", "sb1_SL", "sb1_J1", "sb1_C")},
                         {"CANCELLED"})
        err = next((self.tmp / "out-envchange").glob("sb1_H0_*.err")).read_text()
        self.assertIn("changed since submission", err)

    def test_hostile_authorization_paths_are_refused(self):
        for bad in ("/abs/docs/orchestration/AUTHORIZATION-x.md",
                    "docs/orchestration/../orchestration/../../AUTHORIZATION-x.md",
                    "docs/AUTHORIZATION-x.md", "docs/orchestration/NOTE-x.md", "", ".."):
            with self.subTest(path=bad):
                adm = self.admission(self.tmp / "out-hostile",
                                     authorization={"path": bad, "sha256": sha(self.root / AUTH)})
                r = subprocess.run([sys.executable, self.root / PKG_REL / "sb1_admit.py", "check",
                                    "--admission", adm], capture_output=True, text=True)
                self.assertEqual(r.returncode, 3, r.stderr)
        link = self.root / "docs/orchestration/AUTHORIZATION-link.md"
        link.symlink_to(self.root / AUTH)
        try:
            adm = self.admission(self.tmp / "out-hostile",
                                 authorization={"path": "docs/orchestration/AUTHORIZATION-link.md",
                                                "sha256": sha(self.root / AUTH)})
            r = subprocess.run([sys.executable, self.root / PKG_REL / "sb1_admit.py", "check",
                                "--admission", adm], capture_output=True, text=True)
            self.assertEqual(r.returncode, 3, r.stderr)
            # refused by the path rule itself, not only by the later commit check
            self.assertIn("is not an AUTHORIZATION- or DECISION- record", r.stderr)
        finally:
            link.unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
