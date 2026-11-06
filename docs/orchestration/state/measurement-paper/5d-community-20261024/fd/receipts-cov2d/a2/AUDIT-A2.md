# COV2D addendum A2: the audit, and the director's rulings on it

**Received by** the `cov2d` session, 2026-11-05, by SendMessage. These are copied verbatim:
- the director's ruling on A2 §6, which came before the audit;
- the auditor's report (the `coverage-5b-audit` session) on #803 at `1b1ed6b5`;
- the director's ruling on that report.

The answers are A2 §9.

---

## The director's ruling on A2 §6

director: #799 is merged (main 5551cbbe), and A2 (#803) is with coverage-5b-audit. I've ruled on its §6. Put this in A2's text, then send the delta to the auditor:
- **Refusals before any read or product** are not STOPs: an existing directory, quota short of 2× before staging, a dirty deploy. Each is reported to me.
- **A staged copy whose hash differs from its pin IS a STOP.** The declared inputs aren't the pinned ones.
- **A guard verdict STOP on a private copy** is a STOP.
- **A crash, OOM, kill or time-out is INVALID** under §9.13. It isn't a STOP, but it comes to me unrepaired, and any rerun needs my go.

This counts because the declaration's §6 (iii) makes the amendment's definitions binding, with a third STOP ending (c). After the audit and my binding, the A2 cluster test run comes first.

---

## The audit

My A2 audit (#803, 1b1ed6b5) is posted on the PR. The mechanism holds, but §6 needs correcting to the director's ruling before binding.

**D1:**
- "A staged hash off its pin" is a STOP under the ruling, not a refusal. Your stage_copy reads and writes before comparing, so it isn't "before any input is read and any product exists".
- §6 must state the ruling, not "my reading".
- INVALID goes to the director unrepaired, and a rerun needs the director's go.
- What would close it: on a hash mismatch, write the step's record with verdict STOP and the reason, so the count is mechanical. A test and a mutant should go with it.

**D2:** the guard's "before" is taken right after writing a fresh copy, up to 171 GB, on Lustre. Any private-file firing ends (c). What would close it: fsync, then two stats seconds apart must agree before the guard starts; refuse if they don't settle.

**L1:** order() should require pins_checked: true.

**L2:** verify showquota inside a compute allocation in the cluster test.

**Holds:** staging, guards on copies only with values recorded, ROOT's working copy, the emulation's scope, and the deletion ledger.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---

## The director's ruling on the audit

director: the auditor's A2 review is on #803. The mechanism holds. Fix these before I bind:

**D1 (blocking): §6 states my ruling as a ruling,** and makes it mechanical.
- **A staged copy's hash off its pin is a STOP.** stage_copy has already read the input by then. It writes a STOP verdict into the step's record (pseudo_a.json or pseudo_b.json) naming the file, both digests and the step. Don't just raise. Add a test and a REQUIRED mutant.
- **A refusal before any read** (an existing dir, quota under 2×, a dirty deploy) is not a STOP. It is reported to me.
- **A crash, OOM, kill or time-out is INVALID** (§9.13). It comes to me unrepaired and needs my go to rerun.
- Remove "my reading, for the director to confirm"; it's ruled.

**D2: settle before guarding.**
- After writing each private copy: fsync the file and its directory.
- Then require two stats of its atime, at least 5 s apart (or the auditor's spacing), to agree before taking the guard's "before" value.
- If they don't settle within a bounded number of tries, refuse before step A's work. That's a refusal, not a STOP, since nothing has been graded. Record the values.
- Test it with a stand-in that changes atime between the two stats.
- **Why:** a private-file firing ends (c), and today's evidence points to lazy atime on this Lustre.

**The lows, both in:**
- **order()** requires `pins_checked: true` in each PASS record, with a test.
- **showquota on a compute node:** in the A2 cluster test run, add a 1-minute compute allocation (`srun -N1 -t 00:01:00` inside a tiny sbatch, with the TimeLimit check) that runs your quota parser on live output. That's about 0.02 node-h.

Then the delta goes to the auditor, and I bind A2 with a fixed conditional sequence: the cluster test run, then the AR23 rerun, then the universes, then the rest. Each proceeds on the previous PASS record and stops and reports on anything else.

---

## The auditor's re-check (#803 at 9575dd1d, code 928204b0)

COV2D A2 delta (#803 at 9575dd1d, code 928204b0): D1, D2 and L2 close, and L1 closes with one low gap. There is one new blocking finding, which I also missed at 1b1ed6b5. Posted: https://github.com/josephbaileyy/MINERvA-OmniFold/pull/803#issuecomment-6673747406

**N1 (blocking, measured): no single M lets A2's sequence pass step 2.**
- cov2d_submit.sh:10 requires the deploy HEAD == M. :39 runs order --M for every job, and ok() requires each record's "M" == M (cov2d_jobs.py:300-303).
- The committed G18 record (230f6918) and pilot record (b59ffa2d) carry M = cb31611c. A2's deploy is a different commit.
- I ran the real order() at 928204b0 on those records:
  - deploy M = 928204b0: the AR23 rerun is blocked by the pilot record. The first universe job is blocked by both the pilot and G18 records, even with an AR23 PASS at 928204b0.
  - deploy M = cb31611c: the AR23 rerun opens, but that deploy runs the old code without A2's staging. The universe jobs then refuse the new AR23 record.
- The tests use other-commit records only to assert refusal (jobs:346, pseudo_write:254). None tests the cross-commit admission this sequence needs.
- Requirement: a declared rule for which (record, M) pairs order() admits. G18 and pilot at cb31611c and AR23 at A2's commit are admitted; anything else is refused. One real-sequence test, plus a mutant. The director chooses the rule.

**D1, closed:**
- PinMismatch deletes the copy. stage_all returns the STOP, and both steps write verdict STOP with off_pin before any product, exiting 3.
- §6 states the ruling as ruled.

**D2, closed:**
- fsync of the copy, then its directory.
- settle_atime is stat-only: two equal readings 5 s apart, at most 6 pairs, all of them recorded.
- If it never settles, the step writes REFUSED before its work and exits 2.

**L1, closed; the pilot exemption is justified.** cov2d_pilot has no unpinned mode. Low gap: order() reads only pseudo_b.json, and step B checks step A's record for verdict PASS only (cov2d_pseudo_write.py:214-216), not pins_checked. An unpinned A with a pinned B still yields pins_checked: true. It's latent, since production passes no --no-pins.

**L2:** in §6 step 1, as ruled. It closes with that receipt.

**Run here:** test_cov2d_jobs and test_cov2d gave 59 passed and 12 skipped (the skips need the cluster environment). I didn't re-run the harness, and N1 doesn't depend on it.

---

## The director's ruling on N1

director: N1, rule R1. Add a declared PRIOR_RECORDS table in cov2d_jobs, with exactly the two entries: G18's pseudo-data record (cb31611c, 230f6918…) and the pilot record (cb31611c, b59ffa2d…), both from binding 2.
- **What order() admits:** a record whose M equals the deploy's M, or whose path, M and the sha256 of the exact bytes on origin/main all match its table entry. Everything else is refused, including AR23 at cb31611c.
- **The tests:** the ones you listed, on the real committed files.
- **The mutants:** the three REQUIRED ones you listed.
- **The L1 fix** goes in the same delta: step B refuses unless step A recorded `pins_checked: true` whenever B's own pins are checked. Add a test and a mutant.
- **The pilot exemption** is accepted as documented.

Then the harness, the auditor's delta check, and my binding of A2 with the fixed conditional sequence. **After that, freeze A2's code** unless a run STOPs. Keep messages to stage transitions and blockers.
