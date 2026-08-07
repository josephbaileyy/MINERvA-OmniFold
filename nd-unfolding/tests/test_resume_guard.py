"""Pin the BEN-023 / J35 fix: resume must be gated on completion, never on size.

The defect these guard against is not hypothetical. comb4dCc 55971617 failed on 15/160
missing throws because slabs 31,34-39 were valid-but-partial leftovers of an interrupted
multinode run, while all 40 array tasks reported COMPLETED -- the `[[ -s $OUT ]] && skip`
guard read every one of them as finished.

Two layers here:
  * behavioural tests that drive lib/resume_guard.sh in a scratch directory, including
    the interrupted-producer case the old idiom got wrong;
  * a repo-wide regression scan, which is the part that actually keeps the class dead --
    a fix applied to 60 launchers is worth nothing if the 61st is written the old way.
"""
import os
import re
import subprocess
import textwrap

import pytest

_REPO = os.environ.get("MNV_REPO") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_LIB = os.path.join(_REPO, "lib", "resume_guard.sh")


def sh(body, cwd, expect_rc=None, env=None):
    """Run a snippet with the library sourced. Returns (rc, stdout+stderr)."""
    script = f'set -o pipefail\nsource "{_LIB}"\n' + textwrap.dedent(body)
    e = dict(os.environ)
    e.update(env or {})
    r = subprocess.run(["bash", "-c", script], cwd=cwd, capture_output=True, text=True, env=e)
    out = r.stdout + r.stderr
    if expect_rc is not None:
        assert r.returncode == expect_rc, f"rc={r.returncode} expected {expect_rc}\n{out}"
    return r.returncode, out


@pytest.mark.skipif(not os.path.exists(_LIB), reason="resume_guard.sh not present")
class TestCompletionMarker:
    def test_mark_then_is_complete(self, tmp_path):
        sh('echo payload > out.npz; rg_mark_complete out.npz; rg_is_complete out.npz',
           tmp_path, expect_rc=0)
        assert (tmp_path / "out.npz.done").exists()

    def test_unmarked_output_is_not_complete(self, tmp_path):
        """The whole point: a nonempty file is not evidence of a finished producer."""
        sh('echo payload > out.npz; rg_is_complete out.npz', tmp_path, expect_rc=1)

    def test_marker_is_invalidated_when_the_output_changes(self, tmp_path):
        """A partial rewrite after a successful run must not inherit the old marker."""
        sh('''echo payload > out.npz
              rg_mark_complete out.npz
              rg_is_complete out.npz || exit 9
              printf 'truncated' > out.npz          # a later interrupted rewrite
              rg_is_complete out.npz && exit 8      # must NOT still read as complete
              exit 0''', tmp_path, expect_rc=0)

    def test_marker_survives_an_mtime_only_touch_being_detected(self, tmp_path):
        sh('''echo payload > out.npz
              rg_mark_complete out.npz
              touch -t 203001010000 out.npz
              rg_is_complete out.npz && exit 8
              exit 0''', tmp_path, expect_rc=0)

    def test_p4_style_marker_without_size_binding_is_honoured(self, tmp_path):
        """run_p4_unfold_std.sh receipts predate the size/mtime binding and validated
        content before writing. They must keep working, or the fix breaks the one
        launcher that already had this right."""
        (tmp_path / "out.root").write_text("payload")
        (tmp_path / "out.root.done").write_text(
            '{"tag":"x","mode":"produced","root_sha256":"deadbeef"}\n')
        sh('rg_is_complete out.root', tmp_path, expect_rc=0)


@pytest.mark.skipif(not os.path.exists(_LIB), reason="resume_guard.sh not present")
class TestResumeDecision:
    def test_skips_a_marked_output(self, tmp_path):
        rc, out = sh('echo p > out.npz; rg_mark_complete out.npz; rg_skip_if_complete out.npz',
                     tmp_path, expect_rc=0)
        assert "SKIP" in out

    def test_reruns_an_unmarked_nonempty_output(self, tmp_path):
        """This is the exact inversion of the old behaviour."""
        rc, out = sh('echo p > out.npz; rg_skip_if_complete out.npz', tmp_path, expect_rc=1)
        assert "NO completion marker" in out and "INCOMPLETE" in out

    def test_reruns_when_nothing_exists(self, tmp_path):
        sh('rg_skip_if_complete out.npz', tmp_path, expect_rc=1)

    def test_resume_force_overrides_a_valid_marker(self, tmp_path):
        rc, out = sh('echo p > out.npz; rg_mark_complete out.npz; rg_skip_if_complete out.npz',
                     tmp_path, expect_rc=1, env={"RESUME_FORCE": "1"})
        assert "RESUME_FORCE" in out

    def test_adopt_legacy_is_opt_in_and_loud(self, tmp_path):
        rc, out = sh('echo p > out.npz; rg_skip_if_complete out.npz', tmp_path, expect_rc=0,
                     env={"RESUME_ADOPT_LEGACY": "1"})
        assert "WARNING" in out and "BEN-023" in out
        assert "ADOPTED" in (tmp_path / "out.npz.done").read_text()

    def test_validator_adopts_a_valid_legacy_output(self, tmp_path):
        rc, out = sh('''ok(){ grep -q GOOD "$1"; }
                        echo GOOD > out.npz
                        rg_skip_if_complete out.npz ok''', tmp_path, expect_rc=0)
        assert "ADOPT+SKIP" in out

    def test_validator_refuses_an_invalid_legacy_output(self, tmp_path):
        sh('''ok(){ grep -q GOOD "$1"; }
              echo TRUNCATED > out.npz
              rg_skip_if_complete out.npz ok''', tmp_path, expect_rc=1)


@pytest.mark.skipif(not os.path.exists(_LIB), reason="resume_guard.sh not present")
class TestTransactionalRun:
    def test_rg_run_marks_only_on_success(self, tmp_path):
        sh('rg_run out.npz bash -c "echo done > out.npz"', tmp_path, expect_rc=0)
        assert (tmp_path / "out.npz.done").exists()

    def test_rg_run_leaves_no_marker_when_the_producer_fails(self, tmp_path):
        """The interrupted-job case: a partial output is written, then the producer dies.
        No marker, so the next resume re-runs instead of skipping forever."""
        rc, out = sh('rg_run out.npz bash -c "echo partial > out.npz; exit 137"', tmp_path)
        assert rc == 137, out
        assert (tmp_path / "out.npz").exists(), "partial is expected to remain"
        assert not (tmp_path / "out.npz.done").exists(), "a failed producer must not mark"
        sh('rg_skip_if_complete out.npz', tmp_path, expect_rc=1)

    def test_rg_run_fails_when_the_producer_lies_about_success(self, tmp_path):
        rc, out = sh('rg_run out.npz true', tmp_path)
        assert rc == 4 and "does not exist" in out

    def test_rg_run_clears_a_stale_marker_before_reproducing(self, tmp_path):
        """A crash during the rewrite must not be covered by the previous run's marker."""
        rc, out = sh('''echo v1 > out.npz; rg_mark_complete out.npz
                        rg_run out.npz bash -c "echo partial-v2 > out.npz; exit 1"''', tmp_path)
        assert rc == 1
        assert not (tmp_path / "out.npz.done").exists()

    def test_rg_publish_renames_and_marks(self, tmp_path):
        sh('''TMP="$(rg_tmp_for out.root)"
              echo payload > "$TMP"
              rg_publish "$TMP" out.root''', tmp_path, expect_rc=0)
        assert (tmp_path / "out.root").read_text().strip() == "payload"
        assert (tmp_path / "out.root.done").exists()
        assert not list(tmp_path.glob("*.tmp"))

    def test_require_complete_input_refuses_an_unmarked_upstream(self, tmp_path):
        rc, out = sh('echo p > in.root; rg_require_complete_input in.root "merged ROOT"', tmp_path)
        assert rc == 3 and "no valid completion marker" in out


# ---------------------------------------------------------------------------------
# Repo-wide regression scan. This is the part that keeps the class dead.
# ---------------------------------------------------------------------------------

# Sites where a size test is NOT a completion claim, each for a stated reason.
_ALLOWED = {
    # Already transactional and content-validated -- the in-repo precedent the library
    # was modelled on. Their `-s` is paired with valid_root()/valid_merged() + a receipt.
    "nd-unfolding/run_p4_unfold_std.sh",
    "nd-unfolding/run_p4_merge_audit_std.sh",
    # Builds an input inventory and counts it; the count, not the size, is the gate.
    "nd-unfolding/merge_active_endpoints.sh",
    "nd-unfolding/sbatch_merge_active_array.sh",
    # The library's own documentation of the bad idiom, and its opt-in adopt path.
    "lib/resume_guard.sh",
    "lib/backfill_completion_markers.sh",
}

_BAD_RESUME = re.compile(
    r'\[\[?\s+-s\s+"?[^\]]*\]\]?\s*(&&|;\s*then)', re.M)
_SKIPPY = re.compile(r'\b(skip|SKIP|already on disk|exists)\b')


def _shell_files():
    out = []
    for root, dirs, files in os.walk(_REPO):
        # `.claude/worktrees/` holds transient `git worktree` checkouts that concurrent sessions
        # create for read-only audit lanes (CLAUDE.md requires them). Walking into them makes this
        # sweep assert about OTHER branches' shell scripts, and about copies of files it has already
        # checked in the real tree -- so on 2026-08-07 two live worktrees turned this test red while
        # nothing in the repo had changed, and one of the "violations" was `lib/resume_guard.sh`'s own
        # explanatory `#` comment showing the anti-pattern. Excluding them narrows nothing real: every
        # file in a worktree is a checkout of a tracked file this walk already visits at its true path.
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "worktrees")]
        for fn in files:
            if not fn.endswith(".sh"):
                continue
            p = os.path.join(root, fn)
            if os.path.islink(p):
                continue
            rel = os.path.relpath(p, _REPO)
            # `orchestration` is a symlink to docs/orchestration; skip the alias.
            if rel.split(os.sep)[0] == "orchestration":
                continue
            out.append(rel)
    return sorted(out)


def test_no_shell_file_reintroduces_a_size_only_resume_guard():
    """`[[ -s $OUT ]] && skip` must not come back. Use rg_skip_if_complete."""
    offenders = []
    for rel in _shell_files():
        if rel in _ALLOWED:
            continue
        lines = open(os.path.join(_REPO, rel)).read().splitlines()
        for i, line in enumerate(lines):
            if "cmp -s" in line or re.search(r'!\s+-s', line):
                continue
            if not _BAD_RESUME.search(line):
                continue
            # A size test used as a fail-closed precondition is fine and stays.
            if re.search(r'\|\|\s*\{?\s*(echo|die|:)', line):
                continue
            if _SKIPPY.search(" ".join(lines[i:i + 3])):
                offenders.append(f"{rel}:{i + 1}: {line.strip()[:100]}")
    assert not offenders, (
        "size-as-completion-proof resume guard(s) reintroduced (BEN-023 / J35). Replace with "
        "rg_skip_if_complete from lib/resume_guard.sh, or add a justified entry to _ALLOWED:\n  "
        + "\n  ".join(offenders))


def test_every_rg_caller_sources_the_library_first():
    """A launcher that calls rg_* without sourcing the library dies with
    'command not found' -- under `set -e` that aborts, but in a `&&` list it merely
    returns nonzero, which reads as 'must re-run' and silently disables the resume."""
    problems = []
    for rel in _shell_files():
        if rel.startswith("lib/"):
            continue
        lines = open(os.path.join(_REPO, rel)).read().splitlines()
        use = next((i for i, l in enumerate(lines)
                    if re.search(r'(?<!\w)rg_(skip_if_complete|run|publish|is_complete|'
                                 r'mark_complete|adopt|begin|require_complete_input|tmp_for)\b', l)
                    and "resume_guard.sh" not in l), None)
        if use is None:
            continue
        src = next((i for i, l in enumerate(lines) if "lib/resume_guard.sh" in l), None)
        if src is None:
            problems.append(f"{rel}: calls rg_* but never sources lib/resume_guard.sh")
        elif src > use:
            problems.append(f"{rel}: sources the library at line {src + 1}, "
                            f"after first use at line {use + 1}")
    assert not problems, "\n".join(problems)


def test_every_guarded_output_has_a_producer_stamp():
    """A resume guard with no matching rg_run/rg_publish/rg_mark_complete would skip
    nothing forever -- every run would redo the work. That is the safe direction, but
    it is still a bug, and it silently burns the allocation."""
    problems = []
    for rel in _shell_files():
        if rel.startswith("lib/"):
            continue
        t = open(os.path.join(_REPO, rel)).read()
        guarded = set(re.findall(r'rg_skip_if_complete\s+"?([^"\s]+)"?', t))
        if not guarded:
            continue
        stamped = set(re.findall(
            r'rg_(?:run|mark_complete|adopt)\s+"?([^"\s]+)"?', t))
        stamped |= set(re.findall(r'rg_publish\s+\S+\s+"?([^"\s]+)"?', t))
        norm = lambda s: s.replace("${", "$").replace("}", "")   # noqa: E731
        stamped = {norm(s) for s in stamped}
        missing = [g for g in guarded if norm(g) not in stamped]
        if missing:
            problems.append(f"{rel}: guarded but never stamped: {sorted(missing)}")
    assert not problems, "\n".join(problems)
