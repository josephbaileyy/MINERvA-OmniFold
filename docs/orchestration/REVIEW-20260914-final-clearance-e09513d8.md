# Independent review: `68a3da8a..e09513d8` — CLEARANCE, with three flags on the submission step

**Owner:** `lane/z-criteria-independent-assessment-20260910` (independent assessor).
**Subject:** `68a3da8a..e09513d842ad3acc1964c1af740696f02eaed7d9` — 2 commits, 7 files, +334/−42.
`a71087e3` verified unamended (tree `51583946`); `main` `9dba1194`.

# VERDICT: **CLEAR** — no block on this delta.

All four items I was asked to check hold, verified by execution where execution was possible. My own
two-state finding is closed **and pinned in the source**. No new defect in the code.

**Three flags on the SUBMISSION step that follows.** They are **not** blocks on this delta — the code
is clear — but Joseph invited anything bearing on the authorized execution, and the verification
plan as described would not establish what it appears to. Each has a smallest necessary response.

**⚠ THE AUTHORIZATION REACHED ME RELAYED.** "Joseph has authorized deploying `e09513d8` after
independent review clears this range" came through a peer session, not from Joseph. **This record is
that review and it clears; it is not itself the authorization**, and I have not verified the
authorization exists. `R4` suspended; Gate 2 FAIL; nothing submitted.

**Scope honoured:** `a71087e3`, `79badb2f`, `8b89ff36` and `68a3da8a` are closed and not re-derived
here; I reconciled no historical suite totals.

---

## §1 — The four items

**1. The two-state scoping is honest, and the test asserts the EQUALITY rather than the conclusion.**
`test_WHY_STATE_2_IS_NOT_CLOSABLE_the_state_is_IDENTICAL_to_never_started` snapshots the campaign
root and the arm directory by recursive walk — every directory and every file with its size —
captures the never-started state, performs the deletion in the pre-publication state, and asserts
`snapshot() == never_started`. It then instructs the reader to **reopen the residual rather than
delete the arm** if the states ever diverge. That is the right shape: the disposition rests on
indistinguishability, and indistinguishability is the assertion.

*Scope statement, not a finding:* the equality is over **names and sizes**, not mtimes or contents.
I do not think that weakens it — contents are identical because nothing was written, and an mtime is
not a witness a guard could key on, since it moves for legitimate reasons too.

Also verified: the bound is pinned in the source in both states
(`test_the_BOUND_IN_THE_SOURCE_STATES_BOTH_STATES` requires `CLAIM DELETED, PRODUCT PRESENT`,
`CLAIM DELETED, PRODUCT ABSENT`, `AUTHORIZATION BYPASS`, `NOT CLOSABLE BY A GUARD HERE` and
`NOT "JUST RE-RUN IT"`), and the bypass behaviour I measured is itself pinned — the re-run is
asserted to receive `FIRST_ATTEMPT`.

**2. Finding 1's load-bearing middle leg is CONFIRMED BY EXECUTION.** The scoping holds only if
recovery preserves the claim while moving the product. I built the state and measured it:

```
claim preserved across the move: task 4 in claimed_task_ids  before=[4]  after=[4]
product moved out of the arm directory: True
```

So the module's own removal cannot reach `present_names - claimed_names`: the product leaves
`present_names` while its name stays in `claimed_names`, and the difference can only **shrink**. The
premise really was unnameable because it is false — `recover_task` does remove a product from the arm
directory — and the three-part scoping is the correct response. Its `FILESYSTEM_MUTATIONS` entry
`("recover_task", "os.replace", ("product", "target"))` documented the very call that falsified it,
which is the inventory doing its job.

**3. `_confirm_unclaimed` re-reading only the claims holds in the direction claimed.** Re-globbing
would be non-monotone in the dangerous direction: a candidate that vanished between the reads would
be **dropped**, so a genuinely foreign product deleted after being seen would be forgiven. Re-reading
claims only is monotone by (B) — the set can only grow — so the re-read can remove false positives
and never a true one. The docstring now also makes a sharper point I verified: a candidate reaching
this function **is** a product on disk, so the bypass state (claim gone, product never written)
cannot arrive here at all. The two-state bound therefore belongs at premise (B), which is where it is.

**4. The launcher citations resolve at `e09513d8`, checked by content and not only by range.** Seven
bare self-citations in `sbatch_uthrow_block_5d.sh` (479 lines); the other three launchers carry none.
All seven are in range, and each points at content matching its claim — `:13`→`:443` is the `if`;
`:18`/`:27`→`:451` is `BLOCK_DIR="uq_5d/block_slabs_5d"`; `:20`→`:413-414` is the pre-existing-defect
note; `:37`/`:424`→`:409-412` is the withdrawal itself; `:48`→`:411-412` is the `124` figure. Their
own instrument passes (`test_z_precursor.py` 123 OK), and the re-pointings it caught are consistent
with a file whose own notice says a line citation is the most fragile receipt there is.

Two of my earlier findings are now recorded in that file: the marker states the `:409-412`
withdrawal rather than the withdrawn reason, and `:48` records that the `124 receipt-bound slabs`
figure does not reconcile.

**Suites run, not relayed:** `test_z_precursor` **123 OK**, `test_z_campaign_recovery` **65 OK**,
`test_z_campaign_read_ordering` **31 OK**. Per instruction I reconciled no cross-suite totals.

---

## §2 — Three flags on the submission step

Joseph requires automatic requeue disabled explicitly on the actual submission, **with the resulting
job setting verified**. The plan is `sbatch --no-requeue`, then `scontrol show job <id> | grep
Requeue` while the job is pending or running. **The flag choice is right. The verification, as
described, would not establish the setting.** Modelled locally rather than asserted:

**(a) A `grep Requeue` that succeeds proves nothing about the value.** It matches `Requeue=1`
exactly as happily as `Requeue=0` — measured: `printf 'Requeue=1' | grep Requeue` → rc 0.
*Smallest response: assert the value (`Requeue=0`), not the presence of the line, and read the
assertion's status.*

**(b) The pipe destroys `scontrol`'s exit status, so a purged or invalid job id reads as "no match"
rather than "could not look."** Measured: a failing producer piped to `grep` yields **grep's** rc.
With `MinJobAge=300` the record disappears shortly after the job ends, so the difference between
*"verified Requeue=0"* and *"there was nothing to read"* collapses into the same empty output.
*Smallest response: capture `scontrol`'s own status (or its `JobId=` line) before reading the field,
so a missing record is a refusal rather than a pass.*

**(c) The campaign is more than one submission, and the plan verifies one job id.** The launchers
carry `--array=0-7` (dump), `0-20%10` (block), `0-39%40` (run) plus the combine — so up to four
separate `sbatch` invocations. `--no-requeue` is per-submission; verifying one establishes one arm.
An arm submitted without it still has the runtime `SLURM_RESTART_COUNT` refusal (exit 3), so the
failure is closed rather than silent — but the *verified* property would not hold campaign-wide.
*Smallest response: one verification per `sbatch`, and state the expected count so a missing one is
visible.*

All three are the same family as this campaign's own recurring finding — a green check that did not
prove it did the work, and a could-not-look reported as a fact.

---

## §3 — Withheld

Unchanged and not re-attempted; cluster dead (rc=255, sshproxy certificate Sep 13 08:42,
controlmasters empty): **cross-client `O_EXCL`** on Lustre, **`os.mkdir` EEXIST** on Lustre (a
different primitive to which my single-client measurement does not transfer), and **`JobRequeue`** —
which I note the launcher notes now carry as re-measured with a receipt, and which I could not
independently confirm. Questions 3–7 remain Joseph's.
