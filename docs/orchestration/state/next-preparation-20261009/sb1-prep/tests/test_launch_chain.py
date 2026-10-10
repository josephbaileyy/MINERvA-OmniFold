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
             "make_manifest.py", "launch/launch-spec.json", "launch/sb1_submit.sh",
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
        (root / AUTH).parent.mkdir(parents=True, exist_ok=True)
        (root / AUTH).write_text("# FIXTURE authorization for the launch-chain test only\n")
        subprocess.run([sys.executable, root / PKG_REL / "make_manifest.py"], check=True,
                       capture_output=True)
        git(root, "init", "-q")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fixture")
        return root

    @classmethod
    def admission(cls, outroot, **override):
        root = cls.root
        manifest = json.loads((root / PKG_REL / "manifest" / "expected-code.json").read_text())
        head = git(root, "rev-parse", "HEAD")
        adm = {"schema": "sb1-admission/1", "status": "ADMITTED",
               "decision": "FIXTURE: run the fixed SB1 package under its cap",
               "authorization": {"path": AUTH, "sha256": sha(root / AUTH)},
               "checkout": str(root), "code": {"commit": head, "package_commit": head,
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

    def test_the_ledger_adds_charges_and_a_retry(self):
        r = subprocess.run([sys.executable, self.root / PKG_REL / "sb1_verify.py", "ledger",
                            "--admission", self.out / "admission.json",
                            "--sacct", self.out / "H1" / "sacct.psv", "--retry", "UL"],
                           capture_output=True, text=True)
        last = r.stdout.strip().splitlines()[-1]
        st = json.loads((self.tmp / "chain.json").read_text())
        el = {j["opts"]["job-name"]: j["elapsed"] for j in st["jobs"].values()}
        # H1 is still running when its own sacct is taken, so it counts at its ceiling
        want = (2600 + 900) / 3600 + 64 / 256 * (el["sb1_J1"] + el["sb1_C"]) / 3600 \
            + 64 / 256 * el["sb1_H0"] / 3600 + CEILINGS["H1"] + CEILINGS["UL"]
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
        finally:
            link.unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
