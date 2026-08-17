# FINDING 2026-08-17 — a gate green everywhere anyone looks and red only where it is never run

**BEN-255.** Lane D (verifier) and the mediator session, jointly; halves credited inline. Baseline
receipt: [`state/verify-hash-bindings-cluster-baseline-20260817.json`](state/verify-hash-bindings-cluster-baseline-20260817.json).

## The recursion

```
PRIOR INSTANCE   verify_hash_bindings.py was in neither hook list, so a Gate-4 code binding
                 stayed broken ~18 h across four lanes' commits -- "every one of which printed
                 pre-commit: N checks passed"            (.githooks/pre-commit:194-199, verbatim)

THE REMEDY       wire the check into the hook

THIS INSTANCE    the check now runs on every commit -- in a tree where the mismatching RECEIPTS
                 are untracked and the mismatching TARGETS absent -- so it is honestly green
                 locally and BROKEN on the cluster, for TEN DAYS, every commit printing
                 "pre-commit: 9 checks passed"
```

**The fix for the last instance is the mechanism of this one, and both produce the identical
reassuring string.**

## Why the two verdicts differ, and why both are honest

The population it scans differs by location. Verified locally:

| endpoint | state |
|---|---|
| `.githooks/pre-commit:242` | `run "receipt+shell hash bindings" python3 docs/orchestration/verify_hash_bindings.py` — it *does* run on every commit |
| `…/slurm-56534116_2/STEP1_DYNAMICS.json` (binding **source**) | **untracked** — a scratch product existing only on the cluster |
| `…/std_final5_candidate.root` (binding **target**) | **untracked and absent on disk** locally |

So locally the first mismatch is invisible because its *receipt* does not exist, and the second
because its *target* does not. On the cluster both are present and both fire. **The gate is not
being ignored. It is passing, honestly, on a smaller population.**

**That is worse than being ignored.** A gate that is ignored gets noticed eventually, because
somebody looks at the red. A gate green in every place anyone looks and red only where it is never
run **generates no signal at all.**

## The drift is ten days old and both intervening changes are substantive

The wanted sha `66aa1f8f` dates to `8f2bcb0`, 2026-08-07. `train_fullevent_nominal.py` has changed
twice since: `54a8797` (08-10, *"ADOPT the fit-time LR anneal as production policy"*) and `ce03f2c`
(08-13, *"Option C: extract the annealed estimator to a FACTORY"*). **Not cosmetic drift — the
instrument legitimately moving twice while an old receipt kept pointing where it used to be.**

## The remedy is not "also run it on the cluster"

Both verdicts are honest, and keeping two trees in agreement is a standing cost nobody will pay.

> **The defect is that one command name returns two verdicts, and 265 conditions across 106 files
> never said which one they meant.** Name the population in the condition. That fixes it with no
> ongoing maintenance.

Same shape as `CLAUDE.md`'s *"prefer the executable form of any rule you are tempted to write
down"* — with the addition that **an executable form still has to say where it executes.**

**Live instances, named by their author rather than corrected quietly:** the mediator's
authorization for the data-only ensemble conditions on this gate without naming a population, as
does the step-2 criterion given to lane E. Both need the qualifier.

## The cluster-side baseline, first measured in ten days

```
resolved 1409 bindings (755 unresolvable: data files, off-repo artifacts, binaries)
  1403 OK   |   21 from EXPECTED_*_SHA guards in *.sh (floor 15)
            | 1388 from receipt bindings (floor 140)
  44 canonical-namespace FIELD pins verified (floor 30) over 17 of 22 RECORD-FROZEN receipts
   4 known pre-existing drift (submit-time provenance)
   2 MISMATCH  ->  std_final5_candidate.root  |  train_fullevent_nominal.py
*** BINDINGS BROKEN ***
```

`1403 + 2 + 4 = 1409` — the arithmetic closes against `resolved`. **The differential baseline for
any new change is these two.**

## Two method notes that nearly cost a wrong report

**`pgrep -f <pattern>` matches its own command line.** Checking liveness returned a *different* PID
from the one previously reported, which reads exactly like *"the run died and restarted."* It had
not — the new PID was the `pgrep` itself. Excluding the self-match is the fix; **noticing that a
liveness check can match itself is the transferable part.**

**`BEN-026`, paid twice.** The first invocation piped the gate through `tail -12`, truncating at
write time, on the day the rule was being quoted at others. As it happens those twelve lines
contained both mismatches — **but that could not be known without the untruncated run**, which is
the whole point. The general form worth keeping: **truncating a slow run costs more than the
truncation saves, always, because the re-run pays the full price the truncation was avoiding.**

## Family

- `BEN-250` — a check whose strongest statement could not fail.
- `BEN-251` — operations that could not report.
- `BEN-252` — a recorded quantity that could not express the question.
- **`BEN-255`** — a check that is correct in both directions and **evaluated on the wrong
  population.** The check is sound; its domain is not the domain the claim is about.
