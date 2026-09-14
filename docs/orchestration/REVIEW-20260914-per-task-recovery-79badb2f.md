# Independent review: per-task recovery, `a71087e3..79badb2f`

**Owner:** `lane/z-criteria-independent-assessment-20260910` (independent assessor).
**Subject:** `lane/z-campaign-ownership-20260913` @ `79badb2f5ae0c9aef296b206749a19b4d3d34c06`.
**Kept separate from the `a71087e3` review, per instruction.** That object's verdict —
`REVIEW-20260914-namespace-ownership-a71087e3.md` — is unchanged by this record.

**VERDICT: the delta does what it says. Every claim I could check without the cluster is confirmed,
including the one I was asked to probe hardest and the power question about the shipped defect. One
carried-forward defect: the clause-7 race I found on `a71087e3` PERSISTS here unchanged, and the
recovery path re-enters it.** No new defect found in the delta itself.

**CITABLE FOR:** the executed results below. **NOT CITABLE FOR:** landing, launch, spend, any retry
(each needs Joseph's own approval by the authorization's own terms), or anything on Lustre.
`R4` suspended; Gate 2 FAIL; nothing submitted.

---

## §0 — Ground state

`main` still `9dba1194`; `a71087e3` confirmed an unchanged ancestor of `79badb2f`. Delta = 2 commits,
**8 files, +2016/−45**. Unlike the previous round the four launchers ARE modified, by design (the
requeue refusal).

**Suite counts verified, not relayed:** `test_z_campaign_recovery` **65 OK** (new),
`test_z_campaign_ownership` **89 OK**, `test_z_precursor` **123 OK** — sum **277**, matching exactly.
I did not re-run all eight suites (see §5).

---

## §1 — CARRIED FORWARD: the clause-7 race persists here

My `a71087e3` finding — `verify_task_ownership` reads the CLAIMS before the PRODUCTS, so a sibling
that claims and publishes between the two snapshots is reported unclaimed and an innocent task
refuses — **reproduces identically at `79badb2f`**. Same deterministic probe, same refusal naming
`block5d_flux_5.npz` while that sibling's claim demonstrably exists; same control passing.

The delta does not claim to fix it and is not at fault for it. Two things make it worth restating
here rather than leaving it in the other record:

1. **Recovery re-enters the window.** A recovered attempt runs `verify_task_ownership` again, so
   every recovery is another traversal of the race.
2. **The claim-reading surface grew from two call sites to three** (`z_precursor.py:1788, 1995,
   2055`). I have not assessed the two new sites for the same ordering property; that was not in
   this delta's scope and I am naming it as unassessed rather than implying it is clean.

---

## §2 — The power question: would the new arm have caught the shipped defect?

**Yes. Confirmed by execution, not by reading.** I took the test file from `79badb2f`, placed it in a
worktree at the broken commit `0636a786`, and ran the two new subprocess arms:

```
test_the_CLI_RUNS_AS_A_SUBPROCESS_the_way_an_operator_runs_it   -> FAILED
test_EVERY_operator_subcommand_runs_as_a_SUBPROCESS             -> FAILED (command='campaign-recover')
    AssertionError: 1 != 0 :
      File ".../z_precursor.py", line 2562, in main
        import r5_meter
    ModuleNotFoundError: No module named 'r5_meter'
```

That is the original failure, reproduced exactly, by the arm written to catch it. The self-diagnosis
is also correct and unusually clean: the in-process `main(argv)` arm *could not* have caught it,
because it inherits the test module's `sys.path`. Sixty-three tests passed against a path the
operator does not have — `a-fixture-must-agree-with-the-world-not-with-my-code` in its purest form,
and the fix's own docstring says so.

The scoping of the fix is right: `_add_orchestration_to_path()` on the three operator entry points
only, **deliberately not** the module-level insert, because that would put `docs/orchestration` on
the guarded producer's path where `mnv_import_set_ratchet.py` pins the resolved import set as an
identity. The insert is derived from `__file__`, not hardcoded — OI-136's idiom rather than its
defect.

---

## §3 — The terminality predicate, executed across states

The arm I was asked to probe hardest is the **unclassified** one. Executed against
`confirm_attempt_terminal` with a synthetic `sacct` row per state:

| state | result |
|---|---|
| `COMPLETED` / `FAILED` / `CANCELLED` | ACCEPTS (terminal) |
| `COMPLETING` | REFUSES — live; still holds its allocation and fds |
| `SPECIAL_EXIT` | REFUSES — live; a held requeue can be released |
| `RUNNING` | REFUSES — live |
| `FLUXCAPACITOR` (invented) | **REFUSES — "state(s) this module does not classify"** |
| `REQUEUED` only | REFUSES — no terminal state at all |
| zero rows | REFUSES — "that is a CANNOT-LOOK, not a finished job" |

**The unclassified arm fails closed on a state that does not exist**, which is the property that
matters for a future Slurm release. All four refusal grounds are reachable and distinct, and the
all-`REQUEUED` ground is exactly the shape of the recorded 1,882-`REQUEUED` history that the earlier
"all rows terminal" predicate would have mishandled.

**The `SPECIAL_EXIT` asymmetry is deliberate and I confirm it holds at both ends:**
`z_precursor_admission.TERMINAL_STATES` contains `SPECIAL_EXIT` → `True`;
`z_precursor.ATTEMPT_MAY_STILL_WRITE_STATES` contains it → `True`. Two modules, two different
questions — *can its spend still change* versus *can it still write* — and the answers legitimately
differ. It is stated at the refusal site itself, not only in a header. Intentional, not drift.

---

## §4 — The prohibition, and the non-Z guarantee

**The AST deletion ban has power in BOTH directions — mutation-tested by me, not accepted:**

| | result |
|---|---|
| baseline | OK |
| add `os.unlink(...)` inside `recover_task` | **FAILED** |
| rename a covered function (`resolve_log_names`) | **FAILED** |
| restored | OK |

The second mutation is the one that matters: the ban asserts `checked == recovery_functions`, so it
cannot silently cover less than it claims. Its scoping to the recovery path is also correct and
correctly explained — a module-wide ban fired on `_atomic_write_json` unlinking its **own** temp,
which is right and predates this work.

**The non-Z guarantee holds on all four shipped launchers.** I extracted the guard myself and ran it:

```
                      nonZ(restart=9)   member-axis   Z+requeue   Z first attempt   Z+non-numeric
block / run / combF / dump:  rc=0, stderr EMPTY   rc=0        rc=3        rc=0, stderr EMPTY    rc=3
```

Identical across all four. The empty-stderr property — the whole non-Z guarantee — is confirmed, as
is silence on an ordinary first Z attempt, and a non-numeric restart count refusing rather than
erroring the test itself. Their own `fragment()` extracts the block verbatim from the shipped
launcher and anchors on the full two-condition prefix.

**A correction to my own first attempt at this, recorded because it nearly became a false finding.**
My initial extractor anchored on `if [[ -n "${MNV_Z_PRECURSOR_NS` alone, which also matches the
*later* namespace branch in each launcher; it swept past the guard and captured unrelated code,
producing `rc=127` and non-empty stderr on two launchers. **The launchers were fine and my pattern
was wrong.** I caught it only because the results were inconsistent *across files* — the same
tell that caught a BRE/ERE error earlier in this campaign. A guard extraction must anchor on the
condition that distinguishes it, not on its first clause.

---

## §5 — Withheld, and why

**NERSC access is dead and I confirm it independently:** `ssh saul.nersc.gov` → **rc=255**;
`~/.ssh/nersc-cert.pub` dated **Sep 13 08:42** (24-hour sshproxy credentials);
`~/.ssh/controlmasters/` empty. My multiplexed master had outlived the certificate long enough to
produce the single-client Lustre `O_EXCL` measurement recorded in the `a71087e3` review; it is gone.

**Therefore withheld, and NOT estimated:**
- **`mkdir` `EEXIST` on Lustre.** The delta's evidence directory uses `os.makedirs(exist_ok=False)`,
  which is a **genuinely different primitive** from `open(O_EXCL)` — the peer is right to separate
  them, and my earlier measurement does **not** transfer to it. Unmeasured on any filesystem but
  APFS.
- **Cross-client `O_EXCL`**, which is what a multi-node array actually exercises.
- **`JobRequeue`**, the fact that would settle whether the `#SBATCH --no-requeue` header is needed.
  Taking the reading in the open rather than guessing is the right call.
- The eight-suite `705 / 6 / 2` figure. I verified the three named suites (277) and did not re-run
  the rest; the machine has already killed one full run of mine this week under memory pressure.

**Unassessed rather than clean:** the two new `claimed_task_ids` call sites (§1), and the owner's
open questions 3–7. The disclosed mutation — `recover_task` creating `_campaign/recovery/` and
`_campaign/evidence/` with `exist_ok=True` on a pre-delta campaign, leaving two empty directories
with manifest and records untouched — is consistent with the prohibition and I do not object to it.
