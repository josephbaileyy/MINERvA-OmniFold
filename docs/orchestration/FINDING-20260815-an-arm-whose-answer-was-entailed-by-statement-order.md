# An arm whose answer was entailed by statement order — and why moving the observation point cannot fix it

**Date:** 2026-08-15 · **Lane:** OI-124 disposition lane (peer session `C`, driven by the mediator)
**Rows:** `BEN-330`, `BEN-331` · **Item:** `OI-124` (disposition (a) taken) · **Subject file:** lane D's

---

## The shape

`P4` of the `OI-120(c)` loader-purity probe perturbed the NPZ key `w_truth` by ×1.05 and required
`event_reco` to come out bit-identical. Job `56975592` recorded it `proxy_hits: 0`,
`arrays_actually_changed: {}` — the proxy was never asked for the key.

The obvious reading is *a perturbation that failed to land*, i.e. a bug in the arm. It is not. In
`build_fullevent_loaders`, `event_reco` is fully assigned by `build_event_features` — **the exact call
where the probe raises `_Captured`** — and the loader has not yet read `w_truth` at that point. So the
arm's predeclared `IDENTICAL` was **entailed by the order of two statements**. No perturbation of
`w_truth`, of any magnitude or structure, could have made that arm fail where it ran.

> **An arm whose predeclared outcome is implied by control flow measures the control flow, not the
> claim.** It cannot pass "by accident" and it cannot fail at all, so it carries zero information —
> and it does so while occupying a row in a receipt that a reader counts as a test.

## What was refuted on the way, and must not be revived

The offered hypothesis was *the trainer consumes the loader's own weights rather than the NPZ's raw
arrays, so the perturbation never reached anything that matters*. **False on both halves.** The loader
**does** read the raw NPZ `w_truth`, and it **does** derive the trainer's weights from it (subset by
`imc`, optionally scaled by the bootstrap `sig_factor`, into `weight=`). The cause is **ordering, not
indirection** — a distinction worth keeping because the two have opposite repairs.

## Why moving the capture point is not the alternative it looks like

The item offered two dispositions: **(a)** retire the arm and keep the ordering argument, or **(b)**
move the probe's capture point past the `w_truth` read. (b) was costed and **it is not a fix at all**:

`event_reco` is **bound exactly once** in the function and never rebound before it reaches the loader's
output. A capture taken later therefore returns a **bit-identical array**. The arm would still be
unable to fail — it would merely fail-to-fail later, and after dragging in the TensorFlow/ROOT
interpreter split that the early stop exists to avoid.

> **Generalisable: you cannot falsify a statement about what was read BEFORE an observation point by
> moving the observation point.** The unfalsifiability is a property of the value's construction, not
> of where you stand when you look at it. When a probe arm is dead, ask whether the deadness is
> *positional* or *structural* before proposing to reposition anything.

The third option — *make the arm perturb harder* — is the trap the item exists to prevent. At that
capture point there is nothing to perturb harder **at**.

## Disposition (a), and why the replacement is stronger than the arm

A perturbation arm **samples**: it shows `event_reco` did not move for the one perturbation tried.
Ordering **proves**: no perturbation of `w_truth` can move `event_reco`, because the value is finished
before the key is read. Retiring `P4` trades a sample of one for a proof over all.

**But a proof about source code is only as durable as the source it was read against**, and per
`BEN-228` a line number is not an argument. So the proof is kept as a **check that re-derives itself
from the current source on every run and records no coordinate at all**:
`test_loader_ordering_reco_before_truth_weight.py`. It parses the loader and requires:

| premise | what it forbids |
|---|---|
| `P-ONCE` | `event_reco` bound more than once — captured object ≠ emitted object, in either direction |
| `P-USED` | the key being absent, which would satisfy an ordering claim **vacuously** |
| `P-ORDER` | any read of `w_truth` at or before the binding |
| `P-ESCAPE` | the NPZ handle passed to a callee, or aliased, before the binding — a helper reading the key unseen |
| `P-LINEAR` | a loop enclosing either statement, which would break source-order ⇒ execution-order |
| `P-FIXED` | the product never reaching the loader's output |

`P-USED` and `P-ESCAPE` are the two that make it a proof rather than a grep. `P-USED` is there because
**an absence-based guard that also passes when the thing is absent is `BEN-250`'s shape** — rename the
key and the ordering claim holds for the wrong reason. `P-ESCAPE` closes the call-graph hole that a
line-range `awk` cannot see: the original diagnosis scanned lines `1121–1241` for the token `w_truth`,
which is blind to a helper called in that window reading the key on the caller's behalf. Derived here
rather than assumed: the handle is not passed to any call before the binding, earliest such pass is
well after it.

## The guard is shipped with its own negative controls

**A guard nobody has seen fail is indistinguishable from a guard that cannot fail** — which is exactly
what `P4` turned out to be, and repeating that here would be comic. So `audit()` runs against five
deliberately corrupted copies of the real loader source, one per premise, and each is **required to
fail**. A sixth test asserts the mutants actually differ from the source and still parse — without it,
a mutation that silently no-ops makes every negative control a test of nothing, which is *"the
perturbation did not perturb"* one level up.

Result: 9 tests, 6 of which are observations of the guard failing. The negative controls ship with the
guard instead of being performed once by hand and narrated.

## Retiring an arm orphans the regressions that used it as a subject

Not anticipated, and worth the row on its own. `BEN-290`'s regression suite had **three** tests whose
subject was `P4` — the only genuinely void arm in the recorded run. Retiring `P4` broke all three with
`KeyError: 'P4'`.

The wrong repair is to delete them. The tri-state defect `BEN-290` found (a `VOID` arm assigned
`False`, the value reserved for `CONTRADICTED`) is a property of **the scoring code**, not of which arm
happens to be void. So each was re-pointed at a **live** arm, synthesising the void condition from it.

> **Before retiring a test subject, grep for what uses it as a fixture.** A regression that can only be
> triggered by an arm the probe no longer runs is a regression that has stopped running — and it stops
> silently, because the suite still passes once you delete the broken tests.

**Verified rather than asserted:** the original one-token bug (`ok = None` → `ok = False`) was
re-introduced into the probe and the suites re-run. **5 RED**, including `BEN-290`'s own
`test_void_arm_does_not_produce_leakage`. Restored, `26 passed`. The detector survived the retirement,
and that is a measurement, not a reading.

## The denominator moved and the result did not

At `143f859` the replay of job `56975592` read `NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4 truth
perturbations`. After retirement the same recorded arms read `... on 3 of 3 live truth perturbations`.

**Three arms, three bit-identical hashes, one control that fired — unchanged.** The retired arm never
contributed to the numerator. `BEN-290` and its finding file quote the `3 of 4` string and are **NOT
edited**: that string is true of that commit. Both strings are pinned in
`test_probe_oi120c_p4_retirement.py` so the pair is greppable from either direction, and the probe's
receipt carries a `VERDICT_DENOMINATOR_NOTE` stating the correspondence.

## The two vocabulary residues, and which one mattered

Left unpatched by `BEN-290`'s one-token fix to keep an unreviewed edit minimal:

1. The all-void branch read *"the loader refused every truth perturbation"* — on a branch reachable
   when the loader refused **nothing** and every arm was `VOID`. **The conclusion (`UNRESOLVED`) was
   right and its stated reason could be false.** That is the harder of the two to catch, because the
   headline is correct and only the explanation is wrong; nothing downstream contradicts it. Now the
   branch reports **counts** — `N VOID … M REFUSED` — so the reason is derived from operands rather
   than asserted (`BEN-077`).
2. The per-arm print labelled a void arm `REFUSED` while its own `observed` column read `VOID` — two
   columns of one line disagreeing in vocabulary. The label is now **derived from** the observed value
   instead of re-stated, which is the class fix rather than the instance fix.

`VOID` and `REFUSED` are different facts about different objects: **VOID is a fact about the probe**
(the perturbation did not change the array); **REFUSED is a fact about the loader** (it rejected the
perturbed input). Reporting the second as the first sends a reader looking for a fail-closed guard that
does not exist. A test pins each direction — narrowing `REFUSED`'s wording must not delete `REFUSED`.

## BEN-331 — a mutation test that never applied its mutation, and reported green

Caught in this session, self-inflicted, and the cheapest instance of the family yet.

The `BEN-290` mutation check above was first run as a compound command that began with a relative-path
`cp`. An **earlier** command in the session had left the shell's working directory inside
`docs/orchestration`, so the `cp` and the mutating `python3` both failed with `No such file or
directory` — and the pytest invocation that followed, which used bare filenames that resolved *from the
new cwd*, ran happily against the **unmutated** probe and printed `17 passed`.

**The transcript reads as a successful negative control.** It says: mutant applied, suite green — i.e.
exactly the report of a regression suite that has been disarmed. Only the interleaved `cp:` errors
above it, which a `tail` would have eaten, showed the mutation never happened.

> **A mutation test must assert the mutant is PRESENT before believing the suite's verdict**, in the
> same command that runs the suite. Here: `grep -c 'MUTANT' "$P"` → `1` before, `0` after restore.

Three properties of this repo made it cheap to trigger and are worth naming:

* **`cd` persists between `Bash` calls but shell state does not**, so a working directory set many
  turns earlier silently re-scopes every relative path in a later command.
* **`set -e` was absent** from the first version, so two failed commands did not stop the third.
* **The failure was structurally invisible to the success signal**: pytest's exit code is about the
  suite, and the suite was fine. Nothing pytest can report distinguishes *"the regression holds"* from
  *"you tested the wrong file."*

This is the handoff's *"six tools reported success over failure in one day"* family, and it is
`BEN-181`/`OI-124`'s own shape one level up: **the perturbation did not perturb.** The probe already
knew to assert that its arrays actually changed before scoring an arm — the harness checking the probe
did not apply the probe's own rule to itself.

## Scope limits

* The ordering guard binds the **tracked** loader in this checkout. Job `56975592` ran against
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, which is at a different commit with uncommitted paths
  (`OI-74`) and was **not read** — no cluster work was authorized or performed by this lane. The guard
  takes `MNV_LOADER` so it can be re-derived against whatever checkout a future run uses; **doing so is
  a precondition of any re-run of this probe, and has not been done.**
* The retirement is about `w_truth` **and only `w_truth`**. `P1`/`P2`/`P3` — `truth_scalars` scaled,
  `truth_scalars` permuted, `part_gen` scaled — remain live, remain real perturbations, and remain the
  actual evidence for the negative result.
* This lane changed lane **D's** probe. **D authored it and reviewed none of this**, as D also reviewed
  none of `BEN-290`'s repair.

## Not established

* Whether any *other* arm in this probe or its siblings is entailed by control flow the same way. Only
  `P4` was examined. The ordering guard is written to be re-pointed (`product`, `truth_key`, `sink_kw`
  are parameters) but has been applied to exactly one pair.
* Whether `w_truth` influences anything on the reco side that it should not **downstream** of the
  loader. That is a different claim from `event_reco` purity, nobody has made it, and the loader
  legitimately derives the trainer's weights from `w_truth` by design — so a probe of it would need a
  predeclaration this campaign does not currently have.
