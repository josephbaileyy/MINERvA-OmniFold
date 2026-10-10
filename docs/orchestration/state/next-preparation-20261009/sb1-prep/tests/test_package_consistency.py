"""The frozen plan, the batch scripts, the cost ledger and the manifest must state one plan.

No ROOT needed:  python3 -m unittest test_package_consistency -v
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
SPEC = json.loads((PKG / "launch" / "launch-spec.json").read_text())
SUBMIT = (PKG / "launch" / "sb1_submit.sh").read_text()


def sbatch_lines(script):
    out = {}
    for line in (PKG / "launch" / script).read_text().splitlines():
        m = re.match(r"#SBATCH --([a-z-]+)(?:=(.*))?$", line)
        if m:
            out[m.group(1)] = m.group(2) if m.group(2) is not None else True
    return out


class Plan(unittest.TestCase):
    def test_every_job_script_requests_what_the_spec_says(self):
        for job in SPEC["jobs"]:
            with self.subTest(job=job["id"]):
                s = sbatch_lines(job["script"])
                self.assertEqual(s["account"], SPEC["cluster"]["account"])
                self.assertEqual(s["constraint"], SPEC["cluster"]["constraint"])
                self.assertEqual(s["qos"], job["qos"])
                self.assertEqual(int(s["nodes"]), job["nodes"])
                self.assertEqual(int(s["cpus-per-task"]), job["cpus_per_task"])
                self.assertIs(s["no-requeue"], True)
                m = re.search(rf"--job-name=sb1_{job['id']} --time=(\S+)", SUBMIT)
                self.assertIsNotNone(m, job["id"])
                self.assertEqual(m.group(1), job["time"])
                text = (PKG / "launch" / job["script"]).read_text()
                self.assertIn(f"OMP_NUM_THREADS={job['omp_num_threads']}", text)

    def test_dependencies_in_the_submit_script_follow_the_spec(self):
        for job in SPEC["jobs"]:
            if not job["depends"]:
                continue
            want = f'--dependency="{job["dependency_type"]}:' + ":".join(
                f"${{{d}}}" for d in job["depends"]) + '"'
            self.assertIn(want, SUBMIT, job["id"])

    def test_the_unfold_argv_in_the_scripts_is_the_spec_argv(self):
        unfold = (PKG / "launch" / "sb1_unfold.sbatch").read_text()
        for tok in ("--iters 5", "--use-weights", "--estimator lgbm", '--universe "${SB1_LATERAL}"',
                    "--seed 42"):
            self.assertIn(tok, unfold)
        cv = (PKG / "launch" / "sb1_cv.sbatch").read_text()
        for tok in ("--iters 5", "--use-weights", "--estimator lgbm", "--bootstrap-seed 1",
                    "--seed 1"):
            self.assertIn(tok, cv)
        ul = next(j for j in SPEC["jobs"] if j["id"] == "UL")["driver_argv"]
        self.assertEqual(ul[ul.index("--universe") + 1], SPEC["universes"]["lateral"])
        # 55677843's own argv (sbatch_unfold_2d_MEFHC_5iter_universes_full_puritynew.sh)
        ref = (PKG.parents[4] / "2d-unfolding" /
               "sbatch_unfold_2d_MEFHC_5iter_universes_full_puritynew.sh").read_text()
        for tok in ("--iters     5", "--use-weights", "--estimator lgbm", "--seed      42",
                    "#SBATCH --cpus-per-task=128", "#SBATCH --qos=regular"):
            self.assertIn(tok, ref)

    def test_the_committed_costs_are_current_and_within_the_ceiling(self):
        now = subprocess.run([sys.executable, PKG / "costs.py"], capture_output=True, text=True,
                             check=True).stdout
        self.assertEqual(json.loads(now), json.loads((PKG / "results" / "costs.json").read_text()))
        c = json.loads(now)
        self.assertLessEqual(c["total_ceiling_node_h"], SPEC["cluster"]["ceiling_node_h"])
        lit = 2 / 256 * 0.75 * 2 + 50 / 60 + 0.5 + 64 / 256 * 0.75 + 64 / 256 * 40 / 60
        self.assertAlmostEqual(c["total_ceiling_node_h"], lit, places=12)

    def test_the_manifest_is_current(self):
        r = subprocess.run([sys.executable, PKG / "make_manifest.py", "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_the_committed_proposal_cannot_admit(self):
        prop = json.loads((PKG / "launch" / "ADMISSION-PROPOSAL.json").read_text())
        self.assertEqual(prop["status"], "PROPOSAL-NOT-AN-AUTHORIZATION")
        self.assertIsNone(prop["authorization"]["path"])
        manifest = json.loads((PKG / "manifest" / "expected-code.json").read_text())
        self.assertEqual(prop["code"]["modules"], manifest["modules"])
        self.assertEqual(sorted(j["id"] for j in prop["jobs"]),
                         sorted(j["id"] for j in SPEC["jobs"]))

    def test_the_schema_names_every_field_the_admission_check_requires(self):
        schema = json.loads((PKG / "manifest" / "admission.schema.json").read_text())
        src = (PKG / "sb1_admit.py").read_text()
        need = re.search(r"NEED = \(([^)]*)\)", src, re.S).group(1)
        fields = re.findall(r'"([a-z_0-9]+)"', need)
        self.assertEqual(sorted(schema["required"]), sorted(fields))


if __name__ == "__main__":
    unittest.main(verbosity=2)
