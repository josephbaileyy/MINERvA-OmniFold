# FINDING 2026-09-01 — intermittent pscratch read stalls make `A-2(b)` unmeasurable, and the freeze cannot expire while they hold

**CITABLE FOR:** the measurements in §2 and §3, the blocked-leg consequence in §4, and the
method caution in §6.

**NOT CITABLE FOR:** a Gate-1 or Gate-2 clause; a readiness or fitness finding; discharge of
`F-1(b)`; authorization to submit, redeploy, or move any pin; leg 6; any `M(ii)` leg; adoption; or
discharge of any quarantine cause. **Gate 2 remains FAIL.** CAND `1 of 7`, QUOTED `0 of 7`.
**Nothing here authorizes routing around `A-2(b)`.**

## 1. Why this exists

`DECISION-20260901-joseph-authorizes-k0r2-redeploy.md` §3 orders the round-2 `F-1(b)` producer
filing **before** the redeploy, because `FREEZE-20260830-k0-deployment-7ac0edec.md` §1 expires on
exactly that filing and nothing else. The filing cannot be completed. **The obstruction is a
filesystem fault, not a records problem and not a decision anyone is waiting on.** It is recorded
here so the next lane does not re-derive it, and — more importantly — does not re-run the probes
that produced it, which add load to the thing that is already failing.

## 2. THE SIGNATURE — metadata healthy, bulk content reads stall

Measured against the deploy tree `/pscratch/sd/j/josephrb/k0r2/clean` (detached at `7ac0edec`,
read-only working copy) on 2026-09-01, across several Perlmutter login nodes.

**Instant, repeatedly:**

| operation | result |
|---|---|
| `find` over the worktree, `.git` pruned | **1803 files, 0 s** |
| `git ls-files` (index only) | **1804, 0 s** |
| `git rev-parse HEAD` on deploy and canonical | immediate |
| `git cat-file -p HEAD`, `cat-file -s HEAD:VALIDATION_LEDGER.md` | immediate, `167157` |
| `stat`, `ls`, `cat .git/HEAD` | immediate |
| `ls /pscratch`, `ls $HOME` | 0 s on every attempt |

**Hangs and does not return:** `git status --porcelain`, on **both** cluster checkouts.

**So the object store, the index, the ref database and all metadata are healthy.** What fails is
reading worktree file *contents* in bulk — which is exactly and only what `git status` must do to
re-hash entries whose stat data does not match the index.

**Ruled out by measurement, not by argument:** no `fsmonitor`, no `core.untrackedCache`, no
`splitIndex`, no hooks (`.git/hooks` is empty of non-samples), no `objects/info/alternates`, no
`index.lock`, git `2.51.0` on both trees. The read-only mode bits are not the cause: the same
`git status` completes in seconds on a **writable** clone of the same commit with the same 1804
files (the bundle-recovery clone under `k0r2/recovery-*`).

## 3. THE OFFENDING SET — a COMPLETE sweep, and this is not a blind result

Every worktree file was read with `timeout 10 dd`, one at a time, the attempt logged **before** the
read so a hang is distinguishable from a clean pass. **The sweep RAN TO COMPLETION: 1803 attempts,
`READ_ALL_DONE` written.** Ten files timed out:

```
2d-unfolding/uq/classifier_calibration.py
2d-unfolding/sbatch_negweight_cov_analysis.sh
nd-unfolding/tests/test_fps_cli_integration.py
nd-unfolding/active_universe_5d/fps/covariance/fps_reported_mask.json
nd-unfolding/pet_lateral_band.py
nd-unfolding/pet/plot_pet_representation_schematic.py
docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260813.json
docs/orchestration/PROVENANCE-20260822-declaration-v-scalar5d-blocks.md
docs/orchestration/test_measure_m1_m6.py
docs/known-issues/ISSUE-36-eavailw-flux-universe-normalization.md
```

Ordinary small text files — 780 B to a few kB — scattered across four unrelated directories.
**0.55% of the tree.** No size, type or directory pattern.

### It is INTERMITTENT, and an earlier reading of it as a dead storage target was WRONG

On retest the **first two** of those ten read clean, twice each, in 0 s. This lane had reported the
sweep as evidence of a failed Lustre target; that was an overreach on a single measurement and is
corrected here. A dead target would be permanent and reportable; intermittent stalls may simply
clear.

### And it is not static — the retest is WORSE than the sweep

In the sweep, `timeout 10` **fired**, returning `rc=124`. In the retest, on
`nd-unfolding/tests/test_fps_cli_integration.py`, `timeout 20` **does not fire at all** and the read
never returns. **A `timeout` that cannot interrupt its own child means uninterruptible sleep** — the
read is blocked in the kernel, where `SIGTERM` and `SIGKILL` do not apply. That also explains
processes observed stuck on `git status` for **2 h 30 m+** against this tree, belonging to a lane
other than this one.

## 4. THE CONSEQUENCE, stated without a workaround

**`A-2(b)` is `dirty_count` from `git status --porcelain`.** It is a required leg of `F-1(b)`, and
`RECEIPT-20260830-k0-f1b-producer-filing.md` §2 measured it with exactly that command. So:

> **While these stalls hold, the round-2 `F-1(b)` cannot be filed by the precedent route; therefore
> `FREEZE-20260830-k0-deployment-7ac0edec.md` §1 cannot expire; therefore the authorized redeploy
> cannot proceed.**

**No substitute measurement is offered and none should be improvised.** The precedent filing named
its instrument and interpreter explicitly, and swapping the instrument to get past a refusal is the
failure this campaign keeps recording. If a substitute is ever needed it is declared as a
substitute, in a record, with the reason — not slipped into a filing.

**What IS already measured and survives this**, so the next lane does not redo it: A-2(a) is taken —
`.git/HEAD` holds the raw sha `7ac0edec…`, not a `ref:`, therefore **DETACHED** — and bundle-alone
recovery of `7ac0edec` **passes all six declared checks**, including the recovered clone
independently measuring `820 files / 8d036d94…`.

**The irony is worth naming rather than leaving for someone to discover:** a fresh checkout would
very likely dissolve this, so the repair is blocked by the thing it would repair. That is not a
licence to reorder the steps — the far end is a measurement *of the current tree*, and it does not
exist once the tree moves.

## 5. Not only a filing problem

Three entries in §3's list are executable science inputs — `pet_lateral_band.py`,
`test_fps_cli_integration.py`, `fps_reported_mask.json`. **A job that reads a stalled file stalls the
same way**, and a batch task in uninterruptible sleep burns its walltime without failing loudly.
Until this clears, the deploy tree should be treated as **unsafe to launch from**, independently of
the freeze.

## 6. A METHOD CAUTION THAT NEARLY BURNED TWO LANES

**An empty result from a sweep is not a negative result.** The `claude-school` lane ran five cluster
sweeps that returned nothing and were nearly filed as "no wedge found"; all five had been **killed
from outside** and their output files contained only `[killed]`. It retracted its corroboration on
exactly this ground — *"I cannot distinguish 'the read wedged' from 'my process was stopped while
reading'"* — and that retraction is the reason §3 states its completion evidence (1803 attempts and
a terminal marker) rather than just its ten hits.

**Two working rules follow:**

1. **Log the attempt before the operation**, and write a terminal marker at the end. A tally over a
   read that never completed is byte-identical to a tally over a read that found nothing.
2. **Run cluster probes `setsid`-detached, writing to a file on the cluster.** Every one of this
   lane's in-session probes was killed mid-read; only the detached, file-backed ones produced
   results. `saul.nersc.gov` also round-robins across login nodes, so a `ps` check can land on a
   different machine than the work and report a false absence.

**And this lane added to the problem it was diagnosing:** each probe left another wedged
`git status`, twelve of which were its own and have been killed. Contention was self-inflicted; the
underlying stall was not.

## 7. What this finding does NOT do

It does not file `F-1(b)`, expire any freeze, authorize the redeploy, or move any gate. It does not
report the fault to NERSC — §3's intermittency means the ticket-worthy form of the claim is not yet
established. It does not rule on what happens if the stalls persist; that is Joseph's, and the
`OI-123` supersession route in freeze §2 sits at `DECISION-20260830` level, which is his authority
and not this lane's.
