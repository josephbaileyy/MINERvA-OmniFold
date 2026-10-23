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
import os
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
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=reglib.clean_env())


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
        # Stage the registry tables FIRST: the generator reads the index, so a table changed in the working tree
        # (by --repoint, say) must be staged before the renderings are generated from it.
        self.git("add", "docs/orchestration/registry")
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


class CitedLineLookup(unittest.TestCase):
    """reglib.find_cited_line: fixtures find a cited line by its digest, never by a fixed line number."""

    def setUp(self) -> None:
        self.row = reglib.alias_citation((REPO / reglib.ALIASES).read_text(), "a-central-lgbm", "paper-label")
        self.text = (REPO / self.row["source"]).read_text()
        self.n, self.line = reglib.find_cited_line(self.text, self.row["quote"], self.row["line_sha256"])

    def test_found_line_is_the_cited_one(self) -> None:
        self.assertIn(self.row["quote"], self.line)
        self.assertEqual(reglib.line_digest(self.line), self.row["line_sha256"])

    def test_line_added_above_moves_the_hit(self) -> None:
        n, _ = reglib.find_cited_line("% planted\n" + self.text, self.row["quote"], self.row["line_sha256"])
        self.assertEqual(n, self.n + 1)

    def test_edited_line_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            reglib.find_cited_line(self.text.replace(self.line, self.line + " x"), self.row["quote"],
                                   self.row["line_sha256"])

    def test_duplicated_line_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            reglib.find_cited_line(self.text + "\n" + self.line, self.row["quote"], self.row["line_sha256"])


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
        row = reglib.alias_citation((self.f.root / reglib.ALIASES).read_text(), "a-central-lgbm", "paper-label")
        n, line = reglib.find_cited_line((self.f.root / row["source"]).read_text(), row["quote"], row["line_sha256"])
        d = reglib.line_digest(line)
        attr.write_text(attr.read_text() + "docs/orchestration/state/x\\.json\t\te-R-joint-test\t"
                        f"docs/analysis-note/paper_body.tex\t{n}\tconfiguration~(a), the\t{d}\n")
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


class EndToEndCommit(unittest.TestCase):
    """The hook through a REAL `git commit`, in a scratch clone with a linked worktree whose core.hooksPath is the
    branch's .githooks: committing a staged registry file (a) normally and (b) with `commit -a` must leave the
    worktree's index entry count unchanged, commit exactly the expected tree, and leave `git status` working.
    (Git gives the hook GIT_INDEX_FILE -- the worktree's index, or index.lock under -a; a self-test that inherited it
    would overwrite that index.) The clone is made under $TMPDIR; it never touches this repository's .git.
    REGISTRY_E2E_OVERLAY=0 runs the clone's own committed code instead of this checkout's staged code (to show the
    defect on a commit that has it)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        root = Path(cls.tmp.name)
        cls.clone, cls.wt = root / "clone", root / "wt"
        branch = run(["git", "-C", str(REPO), "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
        if branch != "HEAD":
            out = run(["git", "clone", "-q", "--depth", "1", "--branch", branch, f"file://{REPO}", str(cls.clone)])
            assert out.returncode == 0, out.stderr
        else:
            # A detached HEAD (CI checks out a pull request's merge commit) has no branch to clone: fetch the commit.
            sha = run(["git", "-C", str(REPO), "rev-parse", "HEAD"]).stdout.strip()
            for cmd in (["git", "init", "-q", str(cls.clone)],
                        ["git", "-C", str(cls.clone), "fetch", "-q", "--depth", "1", f"file://{REPO}", sha],
                        ["git", "-C", str(cls.clone), "checkout", "-q", "-b", "e2e-base", "FETCH_HEAD"]):
                out = run(cmd)
                assert out.returncode == 0, out.stderr
        cls.g(cls.clone, "config", "user.name", "e2e")
        cls.g(cls.clone, "config", "user.email", "e2e@invalid")
        if os.environ.get("REGISTRY_E2E_OVERLAY", "1") != "0":
            # The code under test is this checkout's STAGED state, laid over the clone's HEAD.
            names = run(["git", "-C", str(REPO), "diff", "--cached", "--name-only", "HEAD"]).stdout.split()
            src = reglib.Index(REPO)
            for rel in names:
                blob = src.read(rel)
                if blob is None:
                    (cls.clone / rel).unlink(missing_ok=True)
                else:
                    (cls.clone / rel).parent.mkdir(parents=True, exist_ok=True)
                    (cls.clone / rel).write_bytes(blob)
            cls.g(cls.clone, "add", "-A")
            if cls.g(cls.clone, "status", "--porcelain").strip():  # nothing staged here: the clone IS the code
                cls.g(cls.clone, "commit", "-q", "--no-verify", "-m", "e2e: overlay the staged code under test")
        cls.g(cls.clone, "worktree", "add", "-q", "-b", "e2e-wt", str(cls.wt))
        cls.g(cls.clone, "config", "core.hooksPath", str(cls.wt / ".githooks"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    @staticmethod
    def g(where: Path, *a: str, env: dict | None = None) -> str:
        out = subprocess.run(["git", "-C", str(where), *a], capture_output=True, text=True, cwd=str(where),
                             env=env or reglib.clean_env())
        if out.returncode:
            raise AssertionError(f"git {' '.join(a)} failed ({out.returncode}): {out.stderr}{out.stdout}")
        return out.stdout

    def commit_and_check(self, label: str, commit_args: list[str], expected_tree: str, n0: int) -> None:
        out = subprocess.run(["git", "-C", str(self.wt), "commit", "-q", "-m", label, *commit_args],
                             capture_output=True, text=True, cwd=str(self.wt), env=reglib.clean_env())
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("checks passed", out.stdout + out.stderr)
        n1 = len(self.g(self.wt, "ls-files", "-z").split("\0")) - 1
        self.assertEqual(n1, n0, f"{label}: index entries {n0} -> {n1}")
        self.assertEqual(self.g(self.wt, "rev-parse", "HEAD^{tree}").strip(), expected_tree)
        status = subprocess.run(["git", "-C", str(self.wt), "status", "--porcelain"], capture_output=True,
                                text=True, cwd=str(self.wt), env=reglib.clean_env())
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(status.stdout, "", f"{label}: git status after the commit: {status.stdout}")

    def test_a_commit_of_a_staged_registry_file(self) -> None:
        f = self.wt / "tools/registry/whatis.py"
        f.write_text(f.read_text() + "# e2e (a)\n")
        self.g(self.wt, "add", "tools/registry/whatis.py")
        n0 = len(self.g(self.wt, "ls-files", "-z").split("\0")) - 1
        tree = self.g(self.wt, "write-tree").strip()
        self.commit_and_check("e2e (a): staged registry file", [], tree, n0)

    def test_b_commit_dash_a_of_a_registry_file(self) -> None:
        f = self.wt / "tools/registry/whatis.py"
        f.write_text(f.read_text() + "# e2e (b)\n")
        n0 = len(self.g(self.wt, "ls-files", "-z").split("\0")) - 1
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
            env = dict(reglib.clean_env(), GIT_INDEX_FILE=str(Path(d) / "index"))
            self.g(self.wt, "read-tree", "HEAD", env=env)
            self.g(self.wt, "add", "-u", env=env)
            tree = self.g(self.wt, "write-tree", env=env).strip()
        self.commit_and_check("e2e (b): commit -a", ["-a"], tree, n0)


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
