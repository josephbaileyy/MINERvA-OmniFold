# Independent review: the namespace-ownership repair @ `a71087e3`, assessed as an ARRAY

**Owner:** `lane/z-criteria-independent-assessment-20260910` (independent assessor).
**Subject:** `lane/z-campaign-ownership-20260913` @ `a71087e306bcc000997722527893752345ec23e1`.
**Coverage extends to `a71087e3` only.** A later delta (`..79badb2f`) exists and is reviewed
separately, per instruction; nothing here covers it.

**VERDICT: the five integration controls are met, the design is sound, and there is ONE DEFECT —
clause 7 refuses a correctly-bound sibling under a read-ordering race.** It fails closed, so no
wrong result can reach the combine; what it costs is a false refusal at real array width, with a
message that misdirects the operator. Proven deterministically with a control, and observed once in
the wild.

**CITABLE FOR:** the finding in §2, the array measurements in §1, the Lustre measurement in §3.
**NOT CITABLE FOR:** landing, launch, spend, adoption, or any statement about `79badb2f`.
`R4` suspended; Gate 2 FAIL; nothing submitted.

---

## §0 — Ground state, re-measured

`main` = `9dba1194` (which landed the reviewed precursor repairs `77a4af38..41a64f02`).
Delta `9dba1194..a71087e3` = 3 commits, **4 files, +2768/−53**, touching only
`z_precursor.py`, `unified_throw_cov.py` and two test files.

**The launcher byte-identity claim is confirmed** — all six blob hashes are identical to
`9dba1194`: `sbatch_uthrow_block_5d.sh` `85681af3`, `sbatch_uthrow_run_5d_fast.sh` `fe67e4f6`,
`sbatch_uthrow_combine_5d_fast.sh` `f94eaff5`, `sbatch_uthrow_dump_5d.sh` `1f933fa2`,
`unified_throw.py` `a8e06ac2`, `lib_member_resume.sh` `7abfb331`. `git diff --name-only` returns
exactly four paths, so nothing else moved.

**Suite counts verified independently, not relayed:** `test_z_campaign_ownership` **89 OK**,
`test_z_precursor` **123 OK**, `test_z_build_path` **90 OK**, `test_uq_remediation` 237 ran,
`failures=3, errors=2, skipped=2`. Sum **533 passed / 4 failed / 2 skipped** — matching the relay
exactly. The four are pre-existing. *(Reported as **four tests**, not five records: one is
`subTest`-parameterised and emits one record per parameter. That is my own correction from the
previous round, applied here.)*

---

## §1 — The complete ARRAY, which is the framing I was asked to hold

The suite's control-2 arm spawns **seven** concurrent tasks. The declared arrays are larger, and
their throttles differ in a way that matters:

| arm | `#SBATCH --array` | tasks | max concurrent |
|---|---|---|---|
| `block` | `0-20%10` | 21 | 10 |
| `run` | `0-39%40` | 40 | **40 — no effective throttle** |
| `combine` | (single) | 1 | 1 |

So the `run` arm's real concurrency is **40**, not seven. I drove both complete populations through
the subject's own child-spawning harness:

- **`block`, all 21 tasks, in waves of the launcher's own throttle (10 / 10 / 1): PASSES.** Every
  task exits 0, the arm directory ends holding exactly the 21 declared basenames, and
  `claimed_task_ids` returns exactly the 21 declared ids. This composes control 1 with control 2 at
  full width — wave 2 starts after wave 1's siblings have completed, which is the exact condition
  the old predicate got wrong.
- **`run`, all 40 tasks at their real 40-wide concurrency: produced the §2 refusal once, under
  load.** Five repeats at lower load were clean. I do not offer the repeats as a refutation; a
  narrow window looks exactly like that.

---

## §2 — FINDING: clause 7 refuses a correctly-bound sibling (read-ordering race)

### The mechanism, read from the source

In `verify_task_ownership`:

```
:1432   claimed = claimed_task_ids(paths["claims"], arm)      # <- CLAIMS read first
:1439   present = sorted(globmod.glob(plan["arms"][arm]["product_glob"]) ...)   # <- PRODUCTS second
:1449   unclaimed = sorted(present_names - claimed_names)
:1450   require(not unclaimed, ...)
```

A sibling that creates its claim **and** publishes its product between those two reads is absent
from the claims snapshot (taken earlier) and present in the products snapshot (taken later). The
difference is then non-empty and the innocent task refuses.

The clause ordering the docstring defends — 7 before 9 before 10 — is sound and is *not* what is
wrong. The defect is that clause 7 compares two snapshots taken at two different instants.

### Proven deterministically, with a control

I wrapped `claimed_task_ids` so that a correctly-bound sibling completes **in the real order** —
claim first, then publish — but lands inside the window between the subject's two reads. The
wrapper controls only *when*; no subject logic is modified. This is the same manufacture-the-
interleaving discipline the repair's own interrupted-write arm uses for `SIGKILL`.

```
sibling 5 completes BETWEEN the two reads  ->  task 3 REFUSES:
  "arm 'block' ... holds 1 product(s) whose basename this campaign DECLARES but which no task of
   this campaign has CLAIMED: ['block5d_flux_5.npz']. That is a valid product of a DIFFERENT
   campaign sitting at a name this one owns"
  ... and sibling 5's claim EXISTS on disk at that moment (asserted).

CONTROL: same sibling, same claim, same product, completed BEFORE task 3 starts -> task 3 SUCCEEDS.
```

Both arms pass. **Timing is the only variable**, which is what makes this a finding about ordering
rather than about siblings in general.

### Severity, stated exactly

- **It fails CLOSED.** It cannot admit a foreign product; it can only reject a legitimate one. No
  wrong result can reach the combine through this path.
- **What it costs** is an array task dying partway under precisely the conditions this repair was
  built for, and **a message that misdirects**: it tells the operator they are looking at a
  DIFFERENT campaign's product when it is this campaign's own claimed sibling. The reader is sent
  after a foreign campaign that does not exist.
- **The window is entered once per task**, so a 40-wide `run` array runs it 40 times per campaign,
  and any recovery re-entry runs it again.
- It is the **same defect class the repair exists to eliminate** — the old predicate refused
  siblings; this refuses siblings too, through a much narrower window.

**Requirement, not a remedy:** the claims and products reads must be ordered, or re-checked, so
that a sibling completing between them cannot be reported as unclaimed. Which of the available ways
is the author's call — I have deliberately not named one, so that I remain able to review it
(`offering-a-remedy-spends-my-next-verdict`).

### Checked and NOT raised

`campaign_arm_status` reads claims and then per-task existence with the same skew. It is a labelled
**view** — *"this is the view, that is the gate, and neither is the other's evidence"* — so a skew
there misreports for an instant rather than refusing. Not a defect.

---

## §3 — `O_EXCL` on Lustre: partially closed, and I got it before access died

The repair discloses, correctly and unprompted, that `_write_json_exclusive`'s atomicity is
*"NOT MEASURED ON LUSTRE ITSELF"*. I measured it.

`stat -f` on `/pscratch/sd/j/josephrb` returns **`lustre`**. Racing **the exact primitive the code
uses** — `os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)` — with a spin barrier, in a
real Lustre directory:

| processes per trial | trials | create attempts | winners | expected | anomalies |
|---|---|---|---|---|---|
| 12 | 40 | 480 | 40 | 40 | **0** |
| 24 | 60 | 1440 | 60 | 60 | **0** |
| **total** | **100** | **1920** | **100** | **100** | **0** |

**Scope it exactly: this is SINGLE-CLIENT**, one login node. **The cross-client case — which is what
a multi-node Slurm array actually exercises — remains unmeasured.** I had two login nodes racing and
destroyed my own result: the orchestrator's cleanup `rm` deleted the second node's output file while
that node's shell still held the fd. My harness bug, disclosed rather than quietly retried, and by
the time I retried, new connections had stopped working. The probe directory was removed.

**Access is now dead and I confirm it independently:** `ssh saul.nersc.gov` → **rc=255**,
`~/.ssh/nersc-cert.pub` dated **Sep 13 08:42** (24-hour sshproxy credentials),
`~/.ssh/controlmasters/` empty. My multiplexed master outlived the certificate for a while, which is
the only reason the numbers above exist; it is gone. **Withheld for want of the cluster:** the
cross-client `O_EXCL` race, `JobRequeue`, any fresh `sacct` or pscratch read.

---

## §4 — The other four controls, and what I checked

**Control 2's barrier is genuine.** Real `subprocess.Popen` children; each announces itself with a
`ready.*` marker; the parent **asserts** that every marker exists before releasing them —
*"not every child reached the barrier; the concurrency claim would be about a population that never
assembled."* That is the standard I would have demanded. Both variants exist: `publish=True` and
`publish=False`, the latter isolating `O_EXCL` because with no product on disk every loser must
refuse as a duplicate rather than as an overwrite — and the stated reason is **measured**, not
assumed: with publication on, the winner often publishes before the slowest loser arrives.

**Control 2 is not vacuous.** `test_POSITIVE_CONTROL_the_concurrent_children_are_capable_of_refusing`
runs the same script and same barrier with undeclared task ids and requires every child to refuse.

**Control 2's no-collision claim is stated as three independent set identities** rather than a count,
with the reason given: *"a count can be right while two tasks wrote one file and a third wrote
nothing."* A separate arm compares product contents, not just names.

**The clause list correction is real and in the right direction.** The docstring says ten clauses
where the first commit body said nine, and records that step 8 moved in during review without the
list being renumbered — *"an ordered list that silently omits a step is the shape where a reviewer
checks every item and still misses one."*

**The named residual is honest.** The `dump` arm is explicitly NOT repaired, with two measured
reasons — the authorized campaign consumes the existing digest-bound bank rather than re-dumping,
and `do_dump` addresses bank files by **content**, so no (task id → basename) map exists to own. The
statement is placed at the branch as well as in the section header.

**Two questions the repair did NOT silently decide** — I checked, because I was asked to flag it if
it had. A failed or wall-killed task cannot be re-run inside its campaign, and no launcher carries
`--no-requeue`. Both are raised as open questions for Joseph rather than resolved in code, and I
confirm the code does not quietly pick an answer to either. **They are his, and they are live:** the
second one composes with §2, because a requeued task re-enters the same window.
