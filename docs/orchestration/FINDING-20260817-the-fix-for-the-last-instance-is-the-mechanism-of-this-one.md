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

## Amendment 1 (2026-08-18) — a second mechanism for the same defect: the INTERPRETER differs, not the file set

Filed as *"the population it scans differs by location"* — untracked receipts and absent targets.
**There is a second way for a check to be honestly green locally and wrong where it runs, and it does
not need the file set to differ at all.** Measured at both ends, same three lines, same repository:

| where | interpreter | `set -euo pipefail; PASS=0; ((PASS++)); echo SURVIVED` |
|---|---|---|
| this Mac checkout | GNU bash **3.2.57** (arm64-apple-darwin) | **SURVIVED**, exit 0 |
| Perlmutter login node | GNU bash **4.4.23** (x86_64-suse-linux) | **exit 1, no output** |
| this Mac, zsh (lane A) | zsh | **KILLED** |

`((PASS++))` returns the **old** value, so its first increment from `0` exits non-zero;
`((++PASS))` and `PASS=$((PASS+1))` are the portable idioms.

**THE ASYMMETRY IS THE FINDING AND IT IS ONE-DIRECTIONAL: local is the PERMISSIVE end.** A shell
check that passes on a Mac checkout can fail on the cluster; the reverse does not occur for this
class. So:

> **A `set -e` audit run from a Mac checkout systematically UNDER-REPORTS.** Not *"may differ"* —
> under-reports, in the direction that produces false confidence.

Several lanes work from Mac checkouts, and **`.githooks/pre-commit` runs on the committer's machine**,
so any check whose verdict depends on shell *semantics* rather than on *text* inherits the local
interpreter and inherits this bias. That is the same sentence as this finding's original claim with
*"population"* replaced by *"interpreter"*, which is why it is an amendment and not a row —
`BEN-391`: N citations of one sentence is one source.

**WHAT IS NOT AFFECTED, checked rather than assumed**, because it is the obvious next worry: the
continuation lint admitted today (`check_continuation_integrity.py`) is a **Python text scanner**. It
parses shell as text and executes none of it, so its verdict is interpreter-independent and the
`ADMIT` stands. **`bash -n` is a different matter** — it is the local shell's own parser, and a
`bash -n`-clean result from a Mac checkout is a statement about bash 3.2.

**Credit:** lane A measured both local ends and named the transportable consequence; the cluster
measurement is mine. **And the accounting on how I got there belongs in the row:** my original claim
that `set -e` would kill the script was derived from `set -e` semantics *in general* and asserted
about a *specific* script. The measurement vindicated the claim and **not the derivation** — a right
answer reached by a non-transportable route is one you cannot rely on next time, and the next
construct may differ the other way.

**Scope, stated rather than glossed:** the cluster figure is the **login node**. SLURM executes on a
compute node, same OS image, and the shebang settles the interpreter family — strong, and still **two
hops of population with one measured.**

### The two local shell-audit tools have OPPOSITE bias directions, and both are now measured

Lane A's addition, and it matters more than either half alone. `bash 3.2` is the **older** grammar,
so it accepts roughly a subset of what `4.4` does. Demonstrated in both directions rather than
reasoned:

| tool, run locally | probe | bash 3.2.57 (Mac) | bash 4.4.23 (Perlmutter) | local bias |
|---|---|---|---|---|
| `set -e` semantics | `set -euo pipefail; PASS=0; ((PASS++))` | **survives**, exit 0 | **exit 1** | **FALSE CONFIDENCE** |
| `bash -n` grammar | `true \|& cat` | **syntax error**, exit 2 | **exit 0** | **false alarm** |

> **A local `set -e` audit under-reports; a local `bash -n` over-reports.** Same host, same two
> interpreters, opposite directions — so *"it was clean on my machine"* means something different for
> each, and a reader who generalises from one to the other gets it backwards half the time.

`bash -n`'s direction is the safe one: it is noisy about cluster-valid syntax and misses nothing the
cluster would reject, because `4.4` removed essentially nothing `3.2` accepted. **That narrows the
scope of a `bash -n`-clean result without weakening it** — relevant to the *"clean over 35 files"*
reported during the gate-1 work, which stands, and which was never able to catch the continuation
defect under **any** bash version anyway.

### The dispatcher itself is clear, checked rather than assumed

The exposure this amendment describes is real in general and **absent from `.githooks/pre-commit`.**
Measured on `origin/main`: shebang `#!/bin/bash`, `set -uo pipefail` at `:200`, **zero occurrences of
the `((x++))` idiom**, aggregation via the safe `$((x + 1))` form, and every check dispatched to
`python3` rather than evaluated as a shell predicate. **So the hook's verdict does not pass through
shell semantics, and every *"9 checks passed"* reported from a bash-3.2 Mac stands.** Lane A's
measurement; recorded here because *"runs on the committer's machine"* is exactly the phrase that
would otherwise send a future lane to re-audit it.

**The one question worth asking of any green earned locally:** *does its verdict pass through a
shell?* If no — a Python text scanner, a `python3` dispatcher — the interpreter cannot disagree. If
yes, ask which direction the local interpreter errs in, because it is not the same for every tool.

## Family

- `BEN-250` — a check whose strongest statement could not fail.
- `BEN-251` — operations that could not report.
- `BEN-252` — a recorded quantity that could not express the question.
- **`BEN-255`** — a check that is correct in both directions and **evaluated on the wrong
  population.** The check is sound; its domain is not the domain the claim is about.
