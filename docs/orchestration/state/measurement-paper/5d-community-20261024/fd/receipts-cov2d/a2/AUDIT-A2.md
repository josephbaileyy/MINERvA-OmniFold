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
