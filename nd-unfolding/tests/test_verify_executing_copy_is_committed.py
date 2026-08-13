"""Tests for verify_executing_copy_is_committed.py.

EVERY check is POWER-TESTED in BOTH directions. That matters more than usual here, because the
failure mode this tool exists to catch is a check that passes on the file you were trying to
catch. A drift detector that returns CURRENT for a stale copy is worse than no detector: its PASS
is what a launch decision would rest on.

The critical test is `test_a_previously_committed_version_is_STALE_not_CURRENT`. A boolean
"is this content in the repo?" check passes on exactly that input, which is why this tool has
three states instead of two.

Fixtures build a throwaway git repo per test, so nothing here depends on this repository's own
history and the tests cannot be broken by a future commit.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_PATH = os.path.join(HERE, "..", "pet", "verify_executing_copy_is_committed.py")


def _load():
    spec = importlib.util.spec_from_file_location("verify_executing_copy_is_committed", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["verify_executing_copy_is_committed"] = mod
    spec.loader.exec_module(mod)
    return mod


V = _load()

REL = "pet/thing.py"
V1 = "print('version one')\n"
V2 = "print('version two')\n"


def _run(repo, *args):
    r = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )
    return r.stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """A repo whose HEAD holds V2 at REL, with V1 in its history.

    Two committed versions is the minimum needed to distinguish CURRENT from STALE_BUT_COMMITTED,
    which is the distinction the whole tool turns on.
    """
    d = tmp_path / "repo"
    (d / "pet").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(d)], check=True)
    # Per-invocation identity only; never written to a shared config.
    _run(d, "config", "user.email", "test@example.invalid")
    _run(d, "config", "user.name", "Test")
    target = d / REL
    target.write_text(V1)
    _run(d, "add", REL)
    _run(d, "commit", "-q", "-m", "v1")
    target.write_text(V2)
    _run(d, "add", REL)
    _run(d, "commit", "-q", "-m", "v2")
    return d


@pytest.fixture
def deployed(tmp_path):
    """A directory standing in for scratch: outside the repo, no git tree of its own."""
    d = tmp_path / "scratch"
    d.mkdir()
    return d


# --------------------------------------------------------------------------------------
# blob_oid: it must be git's own oid, or every verdict below is comparing the wrong thing.
# --------------------------------------------------------------------------------------


def test_blob_oid_agrees_with_git_hash_object(repo, tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("some content\n")
    theirs = _run(repo, "hash-object", "--no-filters", str(f))
    assert V.blob_oid(f.read_bytes()) == theirs


def test_blob_oid_differs_for_differing_bytes():
    """The other direction: a hash that agreed on everything would also 'agree' with git."""
    assert V.blob_oid(b"a") != V.blob_oid(b"b")


def test_blob_oid_is_a_pure_function_of_bytes_not_of_path(repo, tmp_path):
    a, b = tmp_path / "a.py", tmp_path / "b.txt"
    a.write_bytes(b"same\n")
    b.write_bytes(b"same\n")
    assert V.blob_oid(a.read_bytes()) == V.blob_oid(b.read_bytes())


# --------------------------------------------------------------------------------------
# The three states, each in both directions.
# --------------------------------------------------------------------------------------


def test_the_current_version_is_CURRENT(repo, deployed):
    p = deployed / "thing.py"
    p.write_text(V2)
    r = V.classify(str(repo), str(p), REL)
    assert r["state"] == V.STATE_CURRENT
    assert r["executing_blob_oid"] == r["head_blob_oid"]


def test_a_previously_committed_version_is_STALE_not_CURRENT(repo, deployed):
    """THE test. A boolean 'is it in the repo?' check passes here, and must not.

    This is the OI-57 / reconciler-drift shape exactly: the deployed bytes are real, committed,
    findable in history -- and superseded.
    """
    p = deployed / "thing.py"
    p.write_text(V1)
    r = V.classify(str(repo), str(p), REL)
    assert r["state"] == V.STATE_STALE
    assert r["state"] != V.STATE_CURRENT
    assert r["executing_blob_oid"] != r["head_blob_oid"]
    # And it must NAME the commit, so the report says which version is running rather than only
    # that it is the wrong one.
    assert r["commits_whose_diff_touches_executing_content"], "stale verdict must cite a commit"
    assert any("v1" in c for c in r["commits_whose_diff_touches_executing_content"])


def test_stale_and_uncommitted_are_DISTINCT_states(repo, deployed):
    """They have different repairs -- re-deploy vs find who hand-edited scratch."""
    stale = deployed / "stale.py"
    stale.write_text(V1)
    edited = deployed / "edited.py"
    edited.write_text(V2 + "# hand patch\n")
    s = V.classify(str(repo), str(stale), REL)
    e = V.classify(str(repo), str(edited), REL)
    assert s["state"] == V.STATE_STALE
    assert e["state"] == V.STATE_UNCOMMITTED
    assert s["state"] != e["state"]


def test_never_committed_content_is_UNCOMMITTED(repo, deployed):
    p = deployed / "thing.py"
    p.write_text("print('never committed anywhere')\n")
    r = V.classify(str(repo), str(p), REL)
    assert r["state"] == V.STATE_UNCOMMITTED
    assert r["commits_whose_diff_touches_executing_content"] == []


def test_a_one_byte_edit_of_the_current_version_is_not_CURRENT(repo, deployed):
    """Rounding-agreement's cousin: near-identical is not identical."""
    p = deployed / "thing.py"
    p.write_text(V2.replace("two", "twp"))
    r = V.classify(str(repo), str(p), REL)
    assert r["state"] == V.STATE_UNCOMMITTED


def test_added_but_uncommitted_blob_is_IN_ODB_UNREACHABLE_not_committed(repo, deployed):
    """Object existence is not provenance.

    `cat-file -e` succeeds on a blob that `git add` put in the object database and no commit
    contains. A tool that used object existence as its test would call this committed.
    """
    staged = repo / REL
    staged.write_text("print('staged only')\n")
    _run(repo, "add", REL)
    _run(repo, "reset", "-q", "HEAD", "--", REL)  # keep the blob, drop it from the index
    p = deployed / "thing.py"
    p.write_text("print('staged only')\n")
    r = V.classify(str(repo), str(p), REL)
    assert V.blob_in_odb(str(repo), r["executing_blob_oid"]) is True
    assert r["state"] == V.STATE_IN_ODB_UNREACHABLE
    assert r["state"] != V.STATE_CURRENT
    assert r["commits_whose_diff_touches_executing_content"] == []


def test_missing_executing_file_is_MISSING_not_a_pass(repo, deployed):
    r = V.classify(str(repo), str(deployed / "absent.py"), REL)
    assert r["state"] == V.STATE_MISSING
    assert r["executing_blob_oid"] is None


def test_path_absent_from_HEAD_does_not_crash_and_is_not_CURRENT(repo, deployed):
    p = deployed / "thing.py"
    p.write_text(V2)
    r = V.classify(str(repo), str(p), "pet/no_such_file.py")
    assert r["head_blob_oid"] is None
    assert r["state"] != V.STATE_CURRENT


# --------------------------------------------------------------------------------------
# Exit codes. "Could not look" must never be confusable with "looked and found drift".
# --------------------------------------------------------------------------------------


def test_exit_0_when_all_current(repo, deployed):
    p = deployed / "thing.py"
    p.write_text(V2)
    assert V.main(["--repo", str(repo), "--pair", f"{p}={REL}"]) == V.EXIT_OK


def test_exit_3_when_stale(repo, deployed):
    p = deployed / "thing.py"
    p.write_text(V1)
    assert V.main(["--repo", str(repo), "--pair", f"{p}={REL}"]) == V.EXIT_DRIFT


def test_one_stale_pair_fails_the_whole_run(repo, deployed):
    ok = deployed / "ok.py"
    ok.write_text(V2)
    bad = deployed / "bad.py"
    bad.write_text(V1)
    rc = V.main(
        ["--repo", str(repo), "--pair", f"{ok}={REL}", "--pair", f"{bad}={REL}"]
    )
    assert rc == V.EXIT_DRIFT


def test_exit_2_not_3_when_repo_is_not_a_git_tree(tmp_path, deployed):
    p = deployed / "thing.py"
    p.write_text(V2)
    rc = V.main(["--repo", str(tmp_path / "not-a-repo"), "--pair", f"{p}={REL}"])
    assert rc == V.EXIT_USAGE
    assert rc != V.EXIT_DRIFT


def test_exit_2_when_no_pairs_given(repo):
    assert V.main(["--repo", str(repo)]) == V.EXIT_USAGE


def test_exit_2_on_malformed_pair(repo):
    assert V.main(["--repo", str(repo), "--pair", "no-equals-sign"]) == V.EXIT_USAGE


def test_malformed_pair_is_rejected_by_the_parser_in_both_directions():
    with pytest.raises(ValueError):
        V.parse_pair("nope")
    with pytest.raises(ValueError):
        V.parse_pair("=rel")
    with pytest.raises(ValueError):
        V.parse_pair("exec=")
    assert V.parse_pair("a=b") == ("a", "b")


# --------------------------------------------------------------------------------------
# The report ships its ingredients (CONVENTION-receipt-ingredients, BEN-077).
# --------------------------------------------------------------------------------------


def test_json_report_carries_the_operands_the_verdict_rests_on(repo, deployed, tmp_path):
    p = deployed / "thing.py"
    p.write_text(V1)
    out = tmp_path / "report.json"
    rc = V.main(["--repo", str(repo), "--pair", f"{p}={REL}", "--json", str(out)])
    assert rc == V.EXIT_DRIFT
    rep = json.loads(out.read_text())
    assert rep["all_current"] is False
    assert rep["n_current"] == 0
    assert rep["n_checked"] == 1
    assert rep["repo_head"] == _run(repo, "rev-parse", "HEAD")
    r = rep["results"][0]
    # Both hashes present, so the verdict can be CONTRADICTED by the report's own operands.
    assert r["executing_blob_oid"] and r["head_blob_oid"]
    assert r["executing_blob_oid"] != r["head_blob_oid"]
    assert r["executing_sha256"]


def test_json_report_on_a_clean_run_says_so(repo, deployed, tmp_path):
    p = deployed / "thing.py"
    p.write_text(V2)
    out = tmp_path / "report.json"
    assert V.main(["--repo", str(repo), "--pair", f"{p}={REL}", "--json", str(out)]) == V.EXIT_OK
    rep = json.loads(out.read_text())
    assert rep["all_current"] is True
    assert rep["states"] == [V.STATE_CURRENT]
