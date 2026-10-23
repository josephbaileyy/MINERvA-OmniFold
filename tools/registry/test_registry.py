#!/usr/bin/env python3
"""Fixture tests for the results index, the registry checks and the absence-claim check.

    python3 tools/registry/test_registry.py

Each results-index test builds a throwaway git repository holding copies of the real registry TSVs, every source
file they cite, and two real receipts; commits a freshly generated index; then plants ONE file with `git add` and
runs the real CLI (`results_index.py --check --repo <tmp>`) as a subprocess. Discovery is therefore exercised end to
end -- `git ls-files`, the staged blob, the population rule -- not by mutating an in-memory registry.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reglib  # noqa: E402

REPO = reglib.repo_root(HERE)
RI = [sys.executable, str(HERE / "results_index.py")]
SEED_RECEIPTS = ("docs/orchestration/state/s5e/cand/assess_receipt.json",
                 "docs/orchestration/state/s5c/d1/bias_vs_adopted.json")


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=reglib.git_env())


def counts(summary: str) -> dict[str, int]:
    import re
    m = re.search(r"(\d+) included .*?, (\d+) excluded-no-metric", summary)
    return {"included": int(m.group(1)), "excluded-no-metric": int(m.group(2))}


class Fixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        g = self.git
        g("init", "-q")
        g("config", "user.name", "fixture")
        g("config", "user.email", "fixture@invalid")
        src = reglib.Index(REPO)
        need = set(SEED_RECEIPTS) | {reglib.ESTIMATORS, reglib.ALIASES, reglib.ATTRIBUTION, reglib.STATUS,
                                     reglib.UNRESOLVED}
        for t in (reglib.ESTIMATORS,):
            need |= {r["defining_source"] for r in reglib.read_tsv(src, t)}
        for t in (reglib.ALIASES, reglib.ATTRIBUTION, reglib.STATUS, reglib.UNRESOLVED):
            need |= {r["source"] for r in reglib.read_tsv(src, t)}
        for rel in need:
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(src.read(rel))
        g("add", "-A")
        self.write()
        g("commit", "-q", "-m", "fixture base")

    def git(self, *a: str) -> str:
        out = run(["git", "-C", str(self.root), *a])
        if out.returncode:
            raise RuntimeError(out.stderr)
        return out.stdout

    def write(self) -> None:
        out = run(RI + ["--write", "--repo", str(self.root)])
        assert out.returncode == 0, out.stdout + out.stderr
        self.git("add", "docs/orchestration/registry", "docs/analysis-note/records_results_index.tex",
                 "docs/analysis-note/records_estimators.tex")

    def plant(self, rel: str, obj) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(obj, indent=1))
        self.git("add", rel)

    def check(self) -> subprocess.CompletedProcess:
        return run(RI + ["--check", "--repo", str(self.root)])

    def close(self) -> None:
        self.tmp.cleanup()


class ResultsIndexDiscovery(unittest.TestCase):
    def setUp(self) -> None:
        self.f = Fixture()

    def tearDown(self) -> None:
        self.f.close()

    def test_fresh_fixture_passes(self) -> None:
        out = self.f.check()
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("index fresh and complete", out.stdout)

    def test_planted_result_receipt_fails_check_as_unindexed(self) -> None:
        rel = "docs/orchestration/state/new-campaign/assess_receipt.json"
        self.f.plant(rel, {"candidate": "X", "points": {"nominal": {"n": 40, "pooled_cov68": 0.61}}})
        out = self.f.check()
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn(f"UNINDEXED receipt {rel}", out.stdout)
        self.f.write()  # regenerating admits it, as UNATTRIBUTED, with its n and scale
        out = self.f.check()
        self.assertEqual(out.returncode, 0, out.stdout)
        rows = (self.f.root / "docs/orchestration/registry/RESULTS-INDEX.tsv").read_text()
        self.assertIn(f"UNATTRIBUTED\tpoints/nominal\tassessment\t40 (n)\tcoverage68\tpooled_cov68\t0.61", rows)

    def test_planted_receipt_in_receipts_root_is_discovered(self) -> None:
        self.f.plant("docs/orchestration/receipts/x/score.json", {"result": {"coverage": {"0.68": 0.7}}})
        out = self.f.check()
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn("UNINDEXED receipt docs/orchestration/receipts/x/score.json", out.stdout)

    def test_planted_non_result_json_does_not_fail(self) -> None:
        before = counts(self.f.check().stdout)
        self.f.plant("docs/orchestration/state/new-campaign/budget.json",
                     {"schema": "budget/1", "node_hours": 3.5, "closure_reweight_sigma": 0.2, "status": "draft"})
        out = self.f.check()
        self.assertEqual(out.returncode, 0, out.stdout)
        after = counts(out.stdout)
        self.assertEqual(after["excluded-no-metric"], before["excluded-no-metric"] + 1)  # it WAS discovered
        self.assertEqual(after["included"], before["included"])

    def test_result_json_outside_the_roots_is_not_read(self) -> None:
        self.f.plant("nd-unfolding/pet/x/receipt.json", {"pooled_cov68": 0.5})
        out = self.f.check()
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_unstaged_receipt_is_invisible_until_added(self) -> None:
        p = self.f.root / "docs/orchestration/state/late/receipt.json"
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({"pull_sd": 1.1}))
        self.assertEqual(self.f.check().returncode, 0)
        self.f.git("add", "docs/orchestration/state/late/receipt.json")
        self.assertEqual(self.f.check().returncode, 1)

    def test_changed_value_in_an_indexed_receipt_makes_the_index_stale(self) -> None:
        rel = SEED_RECEIPTS[0]
        doc = json.loads((self.f.root / rel).read_text())
        doc["points"]["nominal"]["pooled_cov68"] = 0.5
        self.f.plant(rel, doc)
        out = self.f.check()
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn("STALE docs/orchestration/registry/RESULTS-INDEX.tsv", out.stdout)

    def test_withdrawn_receipt_keeps_its_rows_with_status(self) -> None:
        rel = "docs/orchestration/state/new-campaign/score-WITHDRAWN.json"
        self.f.plant(rel, {"pull_sd": 1.3})
        self.f.write()
        rows = (self.f.root / "docs/orchestration/registry/RESULTS-INDEX.tsv").read_text()
        line = next(l for l in rows.splitlines() if rel in l)
        self.assertIn("\twithdrawn\tfile name\t", line)

    def test_attribution_line_moved_passes_and_is_named(self) -> None:
        rel = "docs/orchestration/state/s5e/cand/dev_receipt.json"  # ATTRIBUTION cites its line 3, "candidate": "R"
        p = self.f.root / rel
        p.write_text("\n" + p.read_text())
        self.f.git("add", rel)
        out = self.f.check()
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("cited line found at 4 (TSV hint 3", out.stdout)
        run([sys.executable, str(HERE / "check_registry.py"), "--repoint", "--repo", str(self.f.root)])
        self.f.git("add", reglib.ATTRIBUTION)
        self.f.write()
        out = self.f.check()
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertNotIn("found at", out.stdout)

    def test_attribution_line_edited_fails(self) -> None:
        rel = "docs/orchestration/state/s5e/cand/dev_receipt.json"
        p = self.f.root / rel
        p.write_text(p.read_text().replace(' "candidate": "R",', ' "candidate": "R", "note": "withdrawn",', 1))
        self.f.git("add", rel)
        out = self.f.check()
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn("TEXT CHANGED", out.stdout)

    def test_attribution_quote_removed_fails(self) -> None:
        rel = "docs/orchestration/state/s5e/cand/dev_receipt.json"
        p = self.f.root / rel
        p.write_text(p.read_text().replace('"candidate": "R",', '"candidate": "Q",'))
        self.f.git("add", rel)
        out = self.f.check()
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn("FAIL ATTRIBUTION row", out.stdout)

    def test_attribution_line_that_does_not_name_the_estimator_fails(self) -> None:
        attr = self.f.root / reglib.ATTRIBUTION
        d = reglib.line_digest((self.f.root / "docs/analysis-note/paper_body.tex").read_text().split("\n")[284])
        attr.write_text(attr.read_text() + "docs/orchestration/state/x\\.json\t\te-R-joint-test\t"
                        f"docs/analysis-note/paper_body.tex\t285\tconfiguration~(a), the\t{d}\n")
        self.f.git("add", reglib.ATTRIBUTION)
        out = self.f.check()
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn("rule 7", out.stdout)

    def test_design_arithmetic_is_labelled_design_projection(self) -> None:
        rel = "docs/orchestration/state/new-campaign/assurance.json"
        self.f.plant(rel, {"status": "DRAFT -- NOT REGISTERED; design arithmetic", "coverage68": 0.7})
        self.f.write()
        rows = (self.f.root / "docs/orchestration/registry/RESULTS-INDEX.tsv").read_text()
        line = next(l for l in rows.splitlines() if rel in l)
        self.assertIn("\tdesign-projection\t", line)

    def test_count_and_parameter_keys_are_not_indexed(self) -> None:
        rel = "docs/orchestration/state/new-campaign/receipt.json"
        self.f.plant(rel, {"M_residual": 35, "closure_reweight_sigma": 0.2, "step2_pull_weights": [1.0, 2.0],
                           "hits68": [30, 31], "pooled_cov68": 0.68})
        self.f.write()
        rows = [l for l in (self.f.root / "docs/orchestration/registry/RESULTS-INDEX.tsv").read_text().splitlines()
                if rel in l]
        keys = sorted(l.split("\t")[5] for l in rows)
        self.assertEqual(keys, ["hits68", "pooled_cov68"])

    def test_key_with_slash_is_an_unambiguous_pointer(self) -> None:
        rel = "docs/orchestration/state/new-campaign/table.json"
        self.f.plant(rel, {"pt/pz": {"closure": 1.01}, "closure_table": {"a/b": 1.0}})
        self.f.write()
        rows = (self.f.root / "docs/orchestration/registry/RESULTS-INDEX.tsv").read_text()
        self.assertIn("\tpt~1pz/closure\n", rows)  # keypath column: "/" inside a key is written ~1
        self.assertNotIn("a~1b", rows)  # a key that is itself a path is never a metric key

    def test_deleting_an_indexed_receipt_is_reported_as_stale(self) -> None:
        self.f.git("rm", "-q", SEED_RECEIPTS[1])
        out = self.f.check()
        self.assertEqual(out.returncode, 1, out.stdout)


class SelfTests(unittest.TestCase):
    def test_registry_self_test(self) -> None:
        out = run([sys.executable, str(HERE / "check_registry.py"), "--self-test"])
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertNotIn("WRONG", out.stdout)

    def test_absence_claims_self_test(self) -> None:
        out = run([sys.executable, str(HERE / "absence_claims.py"), "--self-test"])
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertNotIn("WRONG", out.stdout)


class Resolution(unittest.TestCase):
    def setUp(self) -> None:
        idx = reglib.Index(REPO)
        self.ests = reglib.read_tsv(idx, reglib.ESTIMATORS)
        self.als = reglib.read_tsv(idx, reglib.ALIASES)

    def test_incident_name_resolves_to_the_contract_letter(self) -> None:
        self.assertEqual(set(reglib.resolve("configuration (e)", self.ests, self.als)), {"e-R-joint-test"})
        self.assertEqual(set(reglib.resolve("R", self.ests, self.als)), {"e-R-joint-test"})
        self.assertEqual(set(reglib.resolve("--candidate R", self.ests, self.als)), {"e-R-joint-test"})

    def test_shared_names_are_ambiguous(self) -> None:
        self.assertGreater(len(reglib.resolve("negweight-refined", self.ests, self.als)), 1)
        self.assertGreater(len(reglib.resolve("400/31", self.ests, self.als)), 1)

    def test_learner_name_is_non_identifying(self) -> None:
        hits = reglib.resolve("lgbm", self.ests, self.als)
        self.assertTrue(hits)
        self.assertEqual(reglib.identifying(hits), [])

    def test_unknown_name_does_not_resolve(self) -> None:
        self.assertEqual(reglib.resolve("configuration (q)", self.ests, self.als), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
