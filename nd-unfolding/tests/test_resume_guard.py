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

    # ------------------------------------------------------------------------------
    # OI-142. THE GUARD FIRES: a marker with no size/mtime binding is not proof.
    #
    # The test that stood here asserted the OPPOSITE -- that a fieldless marker "must keep
    # working" -- and it was the defect's own pin. Its premise was that such markers come
    # from run_p4_unfold_std.sh, which content-validated before writing. But the premise is
    # about PROVENANCE while the test was over SHAPE, and "neither field present" is also the
    # shape of an empty, truncated or malformed marker. So the exemption readmitted the
    # BEN-023 defect it was written inside the fix for.
    #
    # It is not replaced by "P4 receipts now re-run". They are validated by
    # nd-unfolding/p4_check_receipt.py, which checks every recorded identity and the whole
    # producing closure -- strictly more than this library can -- and that launcher never
    # routed a resume decision through rg_is_complete. See TestTheNarrowingDidNotBreakP4.
    # ------------------------------------------------------------------------------
    def test_a_marker_carrying_neither_size_nor_mtime_is_REFUSED(self, tmp_path):
        """The exact shape OI-142 names, in its most favourable disguise: valid JSON, a real
        `tag`, a real `root_sha256`. None of that is a completion claim about THIS file."""
        (tmp_path / "out.root").write_text("payload")
        (tmp_path / "out.root.done").write_text(
            '{"tag":"x","mode":"produced","root_sha256":"deadbeef"}\n')
        rc, out = sh('rg_is_complete out.root', tmp_path)
        assert rc == 2, f"an unbound marker must be refused with rc=2, got {rc}\n{out}"

    def test_a_TRUNCATED_marker_is_refused(self, tmp_path):
        """Why the honour branch was a defect and not merely a loose rule: this is a real
        stamp cut off mid-write, and under the old rule it was indistinguishable from a
        legitimate P4 receipt -- so it read as a completed step."""
        (tmp_path / "out.npz").write_text("payload")
        (tmp_path / "out.npz.done").write_text('{"output":"out.npz","si')
        rc, _ = sh('rg_is_complete out.npz', tmp_path)
        assert rc == 2

    def test_a_marker_truncated_after_size_but_before_mtime_is_refused(self, tmp_path):
        """One-of-two is refused as well. A recorded size says nothing about a same-size
        rewrite, and here it is not a partial credential -- it is a partial WRITE."""
        rc, out = sh("""echo payload > out.npz
                        rg_mark_complete out.npz
                        SZ="$(rg_stat_size out.npz)"
                        printf '{"output":"out.npz","size":%s' "$SZ" > out.npz.done
                        rg_is_complete out.npz""", tmp_path)
        assert rc == 2, out

    def test_an_mtime_only_marker_is_refused(self, tmp_path):
        rc, _ = sh("""echo payload > out.npz
                      printf '{"output":"out.npz","mtime":%s}' "$(rg_stat_mtime out.npz)" \
                        > out.npz.done
                      rg_is_complete out.npz""", tmp_path)
        assert rc == 2

    # --- and the narrowing does NOT fire on a well-formed marker ---------------------
    def test_a_marker_with_BOTH_bindings_still_passes(self, tmp_path):
        """THE TEST THE NARROWING REQUIRES. A refusal rule that also refused the good case
        would turn every resume in ~90 launchers into a full recompute, and would report
        itself as a correct fix while burning the allocation."""
        rc, out = sh("""echo payload > out.npz
                        rg_mark_complete out.npz
                        grep -q '"size"'  out.npz.done || exit 7
                        grep -q '"mtime"' out.npz.done || exit 8
                        rg_is_complete out.npz""", tmp_path)
        assert rc == 0, f"the ordinary marker must still be honoured\n{out}"

    def test_the_refusal_and_the_stale_case_are_DISTINGUISHABLE(self, tmp_path):
        """rc=1 and rc=2 are different facts. Collapsing them is how the old code came to
        report a never-bound marker as one whose size/mtime had moved."""
        rc_stale, _ = sh("""echo payload > out.npz
                            rg_mark_complete out.npz
                            printf 'truncated' > out.npz
                            rg_is_complete out.npz""", tmp_path)
        assert rc_stale == 1, "a genuinely stale marker is rc=1"
        rc_unbound, _ = sh("""echo p > b.npz
                              printf '{"tag":"x"}' > b.npz.done
                              rg_is_complete b.npz""", tmp_path)
        assert rc_unbound == 2, "an unbound marker is rc=2"


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


@pytest.mark.skipif(not os.path.exists(_LIB), reason="resume_guard.sh not present")
class TestTheRefusalTellsTheTRUTHAndLaundersNothing:
    """OI-142's second half. A refusal that reports the wrong reason, or that lets the
    marker be overwritten on the way out, closes the hole and opens another."""

    def test_the_message_does_not_claim_the_binding_MOVED(self, tmp_path):
        """It never had one. `rg_skip_if_complete` used to print "size/mtime moved since it
        was stamped" for EVERY non-matching marker, which sends an operator looking for a
        mutation that did not happen -- and the true cause (a truncated stamp) then reads as
        benign drift instead of a partial write."""
        (tmp_path / "out.root").write_text("payload")
        (tmp_path / "out.root.done").write_text('{"tag":"x","root_sha256":"dead"}')
        rc, out = sh('rg_skip_if_complete out.root', tmp_path, expect_rc=1)
        assert "NEITHER size nor mtime" in out, out
        assert "moved since it was stamped" not in out, (
            "the false diagnostic is back: this marker never carried either field\n" + out)

    def test_a_P4_LOOKING_receipt_is_routed_to_its_OWN_validator_by_name(self, tmp_path):
        """Refusing is right; refusing without saying where the answer lives sends the
        operator to RESUME_ADOPT_LEGACY=1, which is the defect opted into deliberately."""
        (tmp_path / "out.root").write_text("payload")
        (tmp_path / "out.root.done").write_text(
            '{"tag":"BeamAngleX_0","mode":"produced","root_sha256":"dead"}')
        rc, out = sh('rg_skip_if_complete out.root', tmp_path, expect_rc=1)
        assert "p4_check_receipt.py" in out, out

    def test_the_refused_marker_is_NOT_overwritten(self, tmp_path):
        """The laundering path. If control reached the adopt branches, rg_adopt would stamp a
        generic size/mtime marker OVER the receipt -- manufacturing exactly the pass that was
        just correctly withheld, and destroying whatever the receipt did record."""
        (tmp_path / "out.root").write_text("payload")
        rec = tmp_path / "out.root.done"
        original = '{"tag":"x","mode":"produced","root_sha256":"deadbeef"}'
        rec.write_text(original)
        sh('rg_skip_if_complete out.root', tmp_path, expect_rc=1)
        assert rec.read_text() == original, "the receipt was rewritten"
        # even with the loud legacy opt-in, an EXISTING marker is not ours to replace
        sh('rg_skip_if_complete out.root', tmp_path, expect_rc=1,
           env={"RESUME_ADOPT_LEGACY": "1"})
        assert rec.read_text() == original, (
            "RESUME_ADOPT_LEGACY=1 overwrote a marker it could not read")

    def test_a_validator_cannot_overwrite_an_unreadable_marker_either(self, tmp_path):
        """The adopt-on-validator path is the library's *preferred* route, so it is the one
        most likely to be pointed at a receipt. It must still not rewrite one."""
        (tmp_path / "out.root").write_text("GOOD")
        rec = tmp_path / "out.root.done"
        rec.write_text('{"tag":"x","root_sha256":"dead"}')
        rc, out = sh("""ok(){ grep -q GOOD "$1"; }
                        rg_skip_if_complete out.root ok""", tmp_path, expect_rc=1)
        assert "ADOPT+SKIP" not in out, out
        assert rec.read_text() == '{"tag":"x","root_sha256":"dead"}'


_BACKFILL = os.path.join(_REPO, "lib", "backfill_completion_markers.sh")


@pytest.mark.skipif(not os.path.exists(_BACKFILL), reason="backfill script not present")
class TestBackfillDoesNotClobberAMarkerItCannotRead:
    """The hazard the OI-142 narrowing INTRODUCED, closed in the same change.

    Before the narrowing a fieldless marker made rg_is_complete return 0, so backfill
    counted the file as `already` and moved on. After it, control fell through to
    `rg_adopt` -- which calls rg_mark_complete and overwrites `${f}.done`. A backfill sweep
    over a directory holding P4 endpoint receipts would have replaced each one with a
    generic size+mtime stamp. A narrowing has to be checked for what it lets through NEXT,
    not only for what it now rejects.
    """

    def _run(self, cwd, *args):
        r = subprocess.run(["bash", _BACKFILL, *args], cwd=str(cwd),
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def test_an_existing_unreadable_marker_is_LEFT_ALONE(self, tmp_path):
        (tmp_path / "a.root").write_text("payload")
        rec = tmp_path / "a.root.done"
        original = '{"tag":"BeamAngleX_0","mode":"produced","root_sha256":"deadbeef"}'
        rec.write_text(original)
        # --validator size PASSES on this file, so nothing but the marker check stops the stamp
        rc, out = self._run(tmp_path, "--validator", "size", "--glob", "*.root")
        assert rc == 0, out
        assert rec.read_text() == original, "backfill overwrote a receipt it could not read"
        assert "1 LEFT ALONE" in out, out

    def test_backfill_STILL_STAMPS_an_unmarked_file_that_validates(self, tmp_path):
        """THE TEST THE NARROWING REQUIRES: the tool's entire purpose must survive it. A
        refusal rule that also refused every unmarked artifact would silently turn the
        backfill into a no-op, and it would still exit 0 while doing nothing."""
        (tmp_path / "b.root").write_text("payload")
        rc, out = self._run(tmp_path, "--validator", "size", "--glob", "*.root")
        assert rc == 0, out
        assert (tmp_path / "b.root.done").exists(), out
        assert "ADOPTED" in (tmp_path / "b.root.done").read_text()
        assert "0 LEFT ALONE" in out, out

    def test_a_stale_marker_is_also_left_alone_rather_than_re_stamped(self, tmp_path):
        """Deliberate scope note: `already` still means "marker present and current". A
        marker present but STALE is now reported, not silently refreshed -- re-stamping it
        would erase the evidence that the file changed after being marked complete."""
        (tmp_path / "c.root").write_text("payload")
        r = subprocess.run(["bash", "-c", f'source "{_LIB}"; rg_mark_complete c.root'],
                           cwd=str(tmp_path), capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        (tmp_path / "c.root").write_text("rewritten-and-longer")
        rc, out = self._run(tmp_path, "--validator", "size", "--glob", "*.root")
        assert rc == 0, out
        assert "LEFT ALONE" in out and "no longer describe the file" in out, out


class TestTheNarrowingDidNotBreakP4:
    """P4 receipts are validated by their own validator, and that is not a claim about
    intent -- it is checkable from the source, so it cannot quietly stop being true.

    This is the other half of "a narrowing needs a test that it does not fire": the
    narrowing is only safe because this launcher never depended on the honour branch.
    """

    def _p4(self):
        return open(os.path.join(_REPO, "nd-unfolding", "run_p4_unfold_std.sh")).read()

    def test_the_p4_launcher_never_resumes_through_the_generic_guard(self):
        body = _strip_full_line_comments(self._p4())
        assert "rg_is_complete" not in body, (
            "run_p4_unfold_std.sh now calls rg_is_complete, so the OI-142 narrowing DOES "
            "reach it and its receipts need a legacy=1 credential after all")
        assert "rg_skip_if_complete" not in body

    def test_the_p4_launcher_validates_its_receipts_with_p4_check_receipt(self):
        body = _strip_full_line_comments(self._p4())
        assert "p4_check_receipt.py" in body, (
            "the dedicated receipt validator is no longer invoked, so nothing validates a "
            "P4 receipt now that the generic guard refuses it")

    def test_no_rg_caller_reads_the_p4_endpoint_directory(self):
        """The enumeration OI-142 asked for, kept live. If a launcher ever guards an output
        in the P4 unfolds namespace with rg_*, the refusal stops being harmless and this
        decision has to be revisited."""
        offenders = []
        for rel in _shell_files():
            if rel.startswith("lib/"):
                continue
            t = _strip_full_line_comments(open(os.path.join(_REPO, rel)).read())
            if "active_universe_5d/standard/unfolds" not in t:
                continue
            if re.search(r'(?<!\w)rg_(skip_if_complete|is_complete|require_complete_input)\b', t):
                offenders.append(rel)
        assert not offenders, (
            "these read the P4 endpoint namespace through the generic resume guard, which "
            "OI-142's enumeration found empty:\n  " + "\n  ".join(offenders))


class TestTheFinalizeCombGuardStaysIndependent:
    """`nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh`'s undeclared route checks size and
    mtime DIRECTLY, per Joseph's amended ruling, and OI-142 explicitly says it must stay
    that way. Now that rg_is_complete agrees with it, "simplify this into the shared guard"
    is the obvious and wrong next edit: it would re-delegate a ruling to a function other
    callers may change. Content-anchored deliberately -- the line numbers have moved twice.
    """

    SCRIPT = os.path.join(_REPO, "nd-unfolding", "sbatch_finalize_5d_bkgaware_gpu.sh")

    def _body(self):
        return _strip_full_line_comments(open(self.SCRIPT).read())

    def test_the_comb_guard_does_not_call_rg_is_complete(self):
        assert "rg_is_complete" not in self._body(), (
            "the COMB guard was refactored onto rg_is_complete. OI-142 requires this route "
            "to remain unexposed, and its ruling is not the shared library's default.")

    def test_the_comb_guard_still_checks_BOTH_fields_itself(self):
        body = self._body()
        for needle in ('rg__marker_field "$_comb_marker" size',
                       'rg__marker_field "$_comb_marker" mtime',
                       'rg_stat_size  "${COMB}"', 'rg_stat_mtime "${COMB}"'):
            assert needle in body, f"the direct size/mtime check lost: {needle!r}"

    def test_the_stale_rationale_about_the_honour_branch_was_CORRECTED(self):
        """A comment asserting a live fact about another file is a claim that can rot. This
        one said rg_is_complete "RETURNS SUCCESS" for an unbound marker -- true when written,
        false the moment OI-142 landed, and sitting in the one script whose guard exists
        because of it."""
        text = open(self.SCRIPT).read()
        assert "OI-142" in text, "the correction is not recorded where the claim was made"
        assert "RETURNS SUCCESS for a marker carrying NEITHER size nor" not in text, (
            "the launcher still asserts the honour branch exists in the present tense")


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
            # A FULL-LINE COMMENT is documentation, not a resume guard. Skipping it is a
            # PRECISION fix, not a relaxation: a comment cannot execute, so nothing that could
            # actually skip work stops being detected. Trailing comments on executable lines are
            # deliberately still scanned -- only a line whose first non-space char is `#` is exempt.
            #
            # WHY THIS IS HERE (BEN-132/BEN-135): the guard fired on
            # sbatch_hpss_protect_p3f_fullevent.sh, where the forbidden shape appeared ONLY inside a
            # comment saying the launcher does the opposite. The first repair reworded the LAUNCHER,
            # which broke the sha256 pin that hpss-protect-p3f-complete-56692312.json holds on it --
            # a receipt covering 1.135 TB of digest-verified sole-copy archive. The launcher bytes
            # were restored and the fix moved here, to the side that is not pinned. A test-driven fix
            # applied to the wrong side of a test can break a hash binding; check which side is
            # pinned FIRST.
            if line.lstrip().startswith("#"):
                continue
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


def _strip_full_line_comments(text):
    """Drop lines whose first non-whitespace character is `#`.

    WHY THIS EXISTS, 2026-08-18. The stamp lint below scraped a PROSE MENTION of a guard out of a
    comment and reported the English word "and" as an unstamped output:

        nd-unfolding/lib_member_resume.sh: guarded but never stamped: ['and']

    from `# through to rg_skip_if_complete and was ACCEPTED on size and mtime.` -- a comment
    EXPLAINING a resume defect, which is exactly the kind of comment a resume library should have. A
    regex over raw source cannot tell a call from prose about a call, so the lint's own remedy
    (write down why the guard is there) triggered it.

    ONLY FULL-LINE COMMENTS ARE STRIPPED, deliberately. A trailing-comment strip that cut at the
    first `#` would corrupt real code: `lib_member_resume.sh:126` contains
    `tail="${p#*/nd-unfolding/}"`, where the `#` is parameter expansion, not a comment. Cutting there
    would silently shorten a line the lint is meant to read -- trading a false positive for a false
    negative, which is the worse direction for a guard.
    """
    return "\n".join(l for l in text.split("\n") if not l.lstrip().startswith("#"))


def test_every_guarded_output_has_a_producer_stamp():
    """A resume guard with no matching rg_run/rg_publish/rg_mark_complete would skip
    nothing forever -- every run would redo the work. That is the safe direction, but
    it is still a bug, and it silently burns the allocation."""
    problems = []
    for rel in _shell_files():
        if rel.startswith("lib/"):
            continue
        t = _strip_full_line_comments(open(os.path.join(_REPO, rel)).read())
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


def test_the_comment_strip_did_not_BLIND_the_stamp_lint():
    """THE TEST THE NARROWING REQUIRES: a filter that removes false positives gets a test that it
    still fires on a REAL offender. Without this, `_strip_full_line_comments` could strip everything
    and the lint above would pass vacuously forever -- and a lint that cannot fail is worse than an
    absent one, because it reports green.

    Planted offender: a guarded output with no rg_run/rg_mark_complete/rg_publish/rg_adopt anywhere.
    """
    offender = (
        '#!/usr/bin/env bash\n'
        '# a comment mentioning rg_skip_if_complete and prose must NOT be scraped\n'
        'source lib/resume_guard.sh\n'
        'rg_skip_if_complete "$REAL_OUT" && exit 0\n'
        'python3 produce.py --out "$REAL_OUT"\n'
    )
    stripped = _strip_full_line_comments(offender)
    guarded = set(re.findall(r'rg_skip_if_complete\s+"?([^"\s]+)"?', stripped))
    stamped = set(re.findall(r'rg_(?:run|mark_complete|adopt)\s+"?([^"\s]+)"?', stripped))
    assert guarded == {"$REAL_OUT"}, (
        f"the strip must keep the real call: {guarded}")
    assert "and" not in guarded, "the prose mention must be gone -- that was the false positive"
    assert not stamped, "nothing stamps it, so this file IS an offender"
    assert guarded - stamped == {"$REAL_OUT"}, "and the lint must still report it"


def test_the_strip_preserves_parameter_expansion_containing_a_hash():
    """The false-negative direction. `${p#*/nd-unfolding/}` is code, not a comment; a naive cut at the
    first `#` would truncate the line and hide whatever followed on it."""
    line = 'tail="${p#*/nd-unfolding/}"; rg_skip_if_complete "$OUT"'
    kept = _strip_full_line_comments(line)
    assert kept == line, f"a code line with $#-expansion must survive intact: {kept!r}"
    assert "rg_skip_if_complete" in kept, "and what followed the hash must still be visible"
