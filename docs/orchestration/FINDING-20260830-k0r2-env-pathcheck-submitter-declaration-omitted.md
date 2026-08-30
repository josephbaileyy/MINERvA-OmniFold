# FINDING 2026-08-30 — the seven k=0 arms died on `env-pathcheck` because the submission never made
# the submitter declaration the guard's own specification requires; the guard was correct

**CITABLE FOR:** the measured terminal state of run `k0-7ac0edec-20260830T000215Z`'s seven arms; the
byte-identical refusal in their `.err` files and its cause; the fact that
`MNV_ENV_SYSTEM_PREFIXES` is absent from the eight `export` lines that
`RECORD-20260830-k0-quarantine-and-seven-arm-submission.md` §5 records as the submission; the three
defects in §5–§7; and the statement that **no code, launcher, or `MANIFEST` pin needs to change to
re-submit**.

**NOT CITABLE FOR:** any gate movement; any claim that Gate 1 round 2 or the 2026-08-30 Step-3 **FIT**
was wrongly graded; any claim that the `F-17(a)` operands were stale at submission (they were not —
five reads, §3); authorization to re-submit, to edit any launcher, to edit
`PACKET-20260823-round5-f2a-f17a-repair.md`, or to add a test; leg 6; the M(ii) family; any member
`k != 0`; covariance construction or adoption; or a publication claim. **Gate 2 remains FAIL and no
scalar-5D covariance is adopted.** Nothing here is authority for compute.

## 0. Why this document exists

The seven arms of the forward-only rehearsal were submitted 2026-08-30T15:46–15:48Z under
`PROPOSAL-20260830-forward-only-rehearsal.md` §9 and recorded in
`RECORD-20260830-k0-quarantine-and-seven-arm-submission.md`. Six tasks then failed in 8–15 s and the
run was cancelled on Joseph's instruction at 16:35:21Z. The producing session (`5d`, personal
account) diagnosed the failure and exhausted its budget before filing; this lane re-measured every
claim from the artifacts and reached a **different cause**. Both the original diagnosis and the
correction are recorded in §4, because the original is the one a reader will otherwise re-derive.

## 1. The terminal state of the run — measured, not inherited

`sacct -X` on `login23`, 2026-08-30T16:35–16:41Z. Cluster times are **PDT**; the `Submit` column
below reads 08:46 for a 15:46Z submission.

| arm | JobId | declared array | outcome |
|---|---|---|---|
| 1 bootstrap | `57742557` | `1-100%32` | tasks 1, 2, 3 **FAILED** `3:0` (12 s, 12 s, 10 s); bracket `[5-100%3]` **CANCELLED by 112498** |
| 2 seedscan split | `57742558` | `1-24%24` | tasks 1, 2 **FAILED** `3:0` (9 s, 8 s); bracket `[3-24%24]` **CANCELLED** |
| 3 detector bkgaware | `57742559` | `0-18` | task 0 **FAILED** `3:0` (15 s); bracket `[2-18]` **CANCELLED** |
| 4 unified-throw run | `57742560` | `1-39` | never started; **CANCELLED** |
| 5 unified-throw block | `57742561` | `1-20` | never started; **CANCELLED** |
| 6 sweep bank | `57742633` | `1-169` | never started; **CANCELLED**. `afterok:57742559` was already unsatisfiable |
| 7 unified-throw combine | `57742635` | single | never started; **CANCELLED**. `afterok:57742560:57742561` unsatisfiable |

**Six tasks ran.** Total compute burned is about one minute. `uid 112498` is `josephrb`; the
cancellation was issued by the producing session over `ssh` on Joseph's explicit instruction, not by
an administrator and not by a watchdog.

Two accounting notes. **The first was filed WRONG on 2026-08-30 and is CORRECTED IN PLACE below,
with the wrong version retained rather than deleted** — the error was this lane's, and it is the kind
a reader would otherwise re-derive.

- **Task 4 of `57742557` was promoted out of the array by the `%32` throttle into its own JobId,
  `57744320`. It is EXPLAINED, not missing.**
  **WHAT THIS ROW SAID WHEN FIRST FILED, and it was false:** *"that does not survive checking —
  `57744320`, and the three sibling ids it named, carry `JobName=allocation`, which is `salloc`'s
  default and not this array's name. They are not this arm's tasks. Task 4's disposition remains
  unexplained."*
  **WHY IT WAS FALSE, and the mechanism is worth more than the fact.** This lane read ONE field,
  `JobName`, and concluded about IDENTITY. Three independent measurements refute it. (i) The
  `Account` column splits exactly along the arms' own accounts: `57744091` and `57744125` are
  `m3246`, the two CPU arms, and `57744293` and `57744320` are `m3246_g`, the two GPU arms — matching
  one-for-one the names the producing session read from `squeue -r -u josephrb` at 16:30Z
  (`uthrow5d_runF`, `uthrow5d_block`, `det5dBKG`, `boot5dG`). (ii) The cancelled bracket is
  `57742557_[5-100%32]`, and **its lower bound of 5 is itself the explanation**: tasks 1–3 ran and
  task 4 is absent from the surviving bracket because it had already been split out. (iii) The rows
  are ours — `User=josephrb`, accounts `m3246`/`m3246_g`.
  **AND AN INSTRUMENT HAZARD, WHICH IS WHY TWO LANES DISAGREED WITHOUT EITHER MIS-QUERYING.** These
  four accounting rows carry **`UID=0`** while displaying `User=josephrb`. So
  `sacct -X -j <ids>` returns them and `sacct -X -u josephrb -j <ids>` returns **nothing**: the `-u`
  filter matches the uid, not the User string. A `-u`-constrained query is not a superset of an
  unconstrained one here, and an absence under `-u` is not evidence the job is not yours.
  `scontrol show job 57742557` returned two `JobId=` records at 16:30Z and returns **zero** now, so
  that corroboration ages out of the scheduler and cannot be re-measured later.
- `sacct -S 08:00 -E now` lists five arms; arms 6 and 7 appear only under an explicit `-j`. A
  window query is not a population query here.

## 2. The refusal, read at its source

All six `.err` files are byte-identical: **1453 bytes, `md5 9fc5fa4d87242f1f3b258b5284c24df6`**,
re-derived by this lane across all six paths. They contain **five `VIOLATION` blocks over three
distinct directories** — the producing session's handoff quoted three, having collapsed to distinct
directories without saying so.

```
[env-pathcheck] VIOLATION: PATH entry is outside the declared environment.
[env-pathcheck]   entry    /global/homes/j/josephrb/.local/bin
[env-pathcheck]   resolves /global/u2/j/josephrb/.local/bin
[env-pathcheck]   Allowed: MNV_ENV_ROOT, MNV_CONDA_PREFIX, or MNV_ENV_SYSTEM_PREFIXES.
```

…repeated for `.nvm/versions/node/v24.18.0/bin`, then `.local/bin` twice more, then `bin`.

**The multiplicity is corroboration, not noise.** A plain non-interactive login PATH measured on
`login23` with no agent in the chain carries `.local/bin` at positions **1, 3 and 20**, `.nvm/…/bin`
at **2**, and `bin` at **21**. The five blocks appear in exactly that order. The refused entries are
Joseph's dotfiles, reachable by any session from any account.

The `.out` files carry one line — `[env-preflight] OK: 14 closure member(s) verified against
mnv_env_manifest.tsv; env root /pscratch/sd/j/josephrb/k0env`. **The environment closure bound
correctly.** Exit 3 comes from `mnv_env_pathcheck` branch (b) via `|| exit $?` at
`nd-unfolding/sbatch_bootstrap_5d_gpu.sh:107`, after the activator returned.

## 3. The cause — a documented submitter obligation that was not performed

`nd-unfolding/lib_mnv_env_pathcheck.sh:37-41` specifies this refusal, verbatim:

> WHAT IS DELIBERATELY *NOT* HERE: anything under $HOME. A user `bin` directory can shadow a tool, so
> `~/.local/bin` and `~/.nvm/.../bin` are refused BY DEFAULT and must be named explicitly by the
> submitter through this variable. That is what "explicitly predeclared" means -- the widening is a
> visible act by whoever submits, not a default this file grants on their behalf.

`PACKET-20260823-round5-f2a-f17a-repair.md:122`, the packet that introduced the guard, gives the
submission preamble including the home entries, and `:218` states *"`MNV_ENV_SYSTEM_PREFIXES` is a
submitter-declared allowlist. The two `$HOME` entries above are predeclared **explicitly** and
deliberately are not defaults."* The packet's own positive control at `:123-127` passes, printing
`[env-pathcheck] OK: 45 search-path entr(ies) checked`.

**`RECORD-20260830-k0-quarantine-and-seven-arm-submission.md` §5 records the submission as eight
`export` lines, and `MNV_ENV_SYSTEM_PREFIXES` is not one of them** (`grep -c` = 0 over the whole
318-line record). This is a positive documentary fact, not an inference from the guard's output.

**The guard did exactly what it is specified to do.** The failure is a procedure omission at the
submission boundary. The `F-17(a)` operands were not stale: the same record's five timestamped reads
hold porcelain **726** and status digest `d429f0f3…8146a` at 15:39:30Z, 15:42:59Z, 15:45:58Z,
15:48:02Z and 15:48:13Z, spanning the first and last `sbatch`.

## 4. What is NOT the cause — the first diagnosis, corrected

The producing session reported the cause as *"one script contradicting itself"*: that
`sbatch_bootstrap_5d_gpu.sh:6`'s `#SBATCH --export=ALL,HOME=…` "exports exactly what it then
refuses" at `:107`, and recommended sanitizing `PATH` inside the launcher before the guard runs. It
has since verified these citations and withdrawn that recommendation. Recorded because it is the
reading the artifacts invite:

- **There is no contradiction.** The guard refuses home entries *pending a declaration the submitter
  is specified to make*. Exporting the environment and requiring the widening to be declared are the
  two halves of one design.
- **`--export=ALL` is not load-bearing.** `ALL` is `sbatch`'s default when `--export` is unset, so
  the flag propagates nothing the job would not already inherit. Read on the target system rather
  than from memory — `man sbatch` on `saul`, Slurm **25.11.7**: *"--export=ALL … Default mode if
  --export is not specified. All of the user's environment will be loaded."* Measured corroboration: two of the
  seven arms, `sbatch_seedscan_split_5d.sh` and `sbatch_uthrow_block_5d.sh`, carry **no**
  `--export=ALL` line, and `ssplit5d` failed with the byte-identical `.err`. Removing the flag
  from all 112 files that carry it repo-wide would not have prevented this.
- **The proposed remedy is the specific act `:37-41` forbids** — the launcher granting the widening
  on the submitter's behalf, invisibly. It would also make the condition permanently unreportable:
  after sanitization the guard can never again observe an undeclared home entry.

## 5. DEFECT 1 — the documented preamble is incomplete against the current dotfiles

`PACKET:122` names `$HOME/.local/bin` and `$HOME/.nvm`. It does **not** name `$HOME/bin`, which is on
the login PATH at position 21 and is the third refused directory. **A submitter who follows the
documented recipe verbatim today still gets a refusal** — one `VIOLATION` block instead of five. The
correct widening is three entries. The packet line needs correcting, or the next submitter reproduces
a weaker form of this failure.

## 6. DEFECT 2 — branch (b) has no test in the direction it acts

This is the substantive finding, and it is worse than "untested", because it reads as coverage.

`nd-unfolding/tests/test_k0_launcher_two_roots.py` **does** execute the guard and assert it passes:
`test_POSITIVE_the_complete_closure_passes_and_execution_REACHES_the_next_line` at `:738` asserts
`[env-pathcheck] OK:` in stdout, and `:731`, `:755`, `:762` assert `VIOLATION` is **absent**.

It cannot fail. `good_env()` at `:269` sets `MNV_ENV_SYSTEM_PREFIXES: self._ambient_prefixes()`, and
`_ambient_prefixes()` at `:231-245` walks the live `PATH`, `PYTHONPATH` and `LD_LIBRARY_PATH` and
predeclares **every** directory it finds. **The fixture derives its allowlist from the same
environment the guard then checks**, so ambient home entries are auto-declared and arm (b) is
unfalsifiable in the positive direction. The fixture's own comment at `:263-266` says it is derived
from the host rather than hardcoded precisely to avoid a different failure — and that choice is what
closes this one.

Arm (a), repository-checkout contamination, has real negative arms:
`test_canonical_checkout_contamination_is_refused_on_ALL_THREE_channels` at `:814` asserts rc 3 and
`REPOSITORY CHECKOUT path`, on all three channels. **Arm (b) has no such arm anywhere in the file.**
There is no assertion that an undeclared, non-checkout entry is refused — which is the branch that
fired six times in production.

This is why Gate 1 passed 18/18 while the launcher could not start. The sharper statement is not
"Gate 1 does not test that a launcher can start": a test exists, executes the guard, and is
structurally incapable of observing the production condition.

## 7. DEFECT 3 — the run pins its tree to the byte and records no environment provenance

`RECORD-20260830` re-reads porcelain and a named status digest at five timestamps, states the digest
recipe explicitly, and rejects three non-interchangeable variants of it. It records **nothing** about
the environment the arms were submitted with beyond the eight `export` lines — no `PATH`, no
`MNV_ENV_SYSTEM_PREFIXES`, and nothing emitted by the job itself. Neither does anything under
`…/runs/k0-7ac0edec-20260830T000215Z/`: a `grep -rl` for `MNV_ENV_SYSTEM_PREFIXES` across the whole
run directory returns only the six `.err` files, which name it in the refusal message.

So the rigor was aimed entirely at git state and never at the surface that actually stopped the run.
**A submitter-declared allowlist that is never recorded is unauditable after the fact.** Had §5's
eight lines not been recorded, the omission in §3 would have been unprovable and this document would
rest on inference from the guard's output alone.

## 8. What follows, and what does not

No code, launcher, or `MANIFEST` pin needs to change for the arms to start. That matters for scoping:
editing a launcher would invalidate existing content pins and trigger the `F-14` / §7.0.7 coupling
and `OI-123` supersession ceremony, and none of that is required here.

**This document authorizes nothing.** A re-submission additionally requires that the canonical
checkout be re-quiesced before a fresh `F-17(a)` operand capture —
`FREEZE-20260830-canonical-quiesce-k0-7ac0edec.md` expired by its own terms at submission
authorization, per `CLOSE-20260830-canonical-quiesce-window-k0-7ac0edec.md` — and it is Joseph's
call. Gate 2 remains **FAIL** on the six clauses of the delegated re-evaluation at `327bc105`, and
nothing here touches any of them.
