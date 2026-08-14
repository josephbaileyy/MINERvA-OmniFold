# FINDING 2026-08-13 — I built the guard against a class in one place and wrote the gate in that class throughout

**BEN-157.** Lane C (PET), on `reconcile_gate5_family.py`, which this lane wrote. Found by codex's
independent read-only audit; **all seven items confirmed here by reproduction. None refuted.**

**One-line version:** the tool whose only job is to refuse a partial family emits an exact
`FAMILY_COMPLETE_PASS` on **zero replicas** — and six other checks turn out to be the tool trusting a
*claim* rather than measuring the world. **I filed `BEN-149` — "a name that claims verification
suppresses the check" — the same morning I was audited for writing it seven times.**

## The seven, all confirmed

### 1. `--n` is the declaration, and the caller supplies it

`:528` — `type=int`, no floor, no bind to the predeclaration. `:563`, `:567`, `:624–625` all compare
against `args.n`.

```
empty dir,            --n 0   ->  rc=0  exact FAMILY_COMPLETE_PASS   targets=0  trainings=0
real 3-member family, --n 3   ->  rc=0  FAMILY_COMPLETE_PASS         targets=3  trainings=3
SAME 3-member family, --n 50  ->  rc=2  PARTIAL
```

**The artifacts did not change between the last two runs. Only the caller's claim about how many
there should be.** The file's own `:7` states the principle its parser does not enforce.

**And codex is right that my tests don't merely miss it — they are written in its idiom.** The
complete-family test uses `n=3`, the clean-name test `n=2`, and
`test_partial_family_is_PARTIAL_and_never_PASS` builds 2 members and runs `n=3` — proving 2/3 ≠ 3/3,
never 49/50 ≠ a *fixed* 50. **No test anywhere asserts `n` must be 50.** Seventy-three tests could
not have found this, because they share the tool's premise that `n` is an input.

### 2. Training `PRESENT` is receipt-only — and one line is the sharpest in the audit

`:448–475`, `:487–494`: no canonical weights file required, no `.done` required (the target stage
reads two), and the artifact hashed at whatever path the receipt names.

**`completion_marker_valid` is never read.** Grep returns exactly two hits in the tree:
`train_fullevent_replica.py:358`, where the **producer writes it**, and
`test_reconcile_gate5_family.py:194`, where **my own fixture copies it**. Zero in the reconciler. The
receipt asserts its own marker validity and nothing checks the assertion — **a receipt declaring
itself invalid passes.**

### 3. `NAME_MISMATCH` scans only when the receipt is *absent*

Rename the weights, update the receipt to match: `rc=0`, exact pass, `trainings_passing=1`,
`trainings_name_mismatch=0`, canonical filename absent from disk.

Structural, not incidental: the stray scan at `:451–467` is reachable only inside
`if not os.path.exists(rec)`. **The guard catches a file that disagrees with the launcher; it cannot
catch a receipt that agrees with a wrong file.** The asymmetry is inside one file I wrote — the
*target* stage has the anchor at `:324`; the training stage has none.

The guard itself is still sound: codex confirms clean names stay silent, no false positive. It is a
check, not an alarm — aimed one branch too narrowly.

### 4. The marker check omits `mtime`, so the tool is more permissive than its own primitive

`:257–265` compares `output` and `size`; `atomic_write.is_complete:84` compares `size` **and**
`mtime`. Real marker, receipt rewritten 100 s later: **`is_complete=False` while the row passes 47/0
and the family returns the exact pass.**

**Two qualifications, both sharpening rather than softening.** For the `.npy` the gap is largely
closed by a check the audit didn't credit — `:251` re-hashes the target from disk. But `sha256_file`
is called on the `.npy`, the training artifact and the source `.npz`, **never on a receipt.** So the
sharp form is: *the receipt is the one file whose only integrity evidence is its marker, and the
marker is checked on one of its two axes.* And `is_complete` compares `int(st_mtime)` — **whole
seconds** — so a same-size same-second rewrite is invisible to the primitive too. **Mirroring
`is_complete` is a floor, not a fix.**

### 5. Driver hash pins are the launcher's job and not the verifier's

The producer records **three** shas (`train_fullevent_replica.py:367–374`: `replica_driver`,
`nominal_driver_unmodified`, `loader`). The launcher checks all three plus HEAD
(`sbatch_gate5_replica_train_array.sh:41–44`). **The reconciler checks `head_at_runtime` and
`loader_sha256` only** (`:483–485`).

**A point beyond the audit: `head_at_runtime` is itself a claim in the receipt, not a measurement.**
So the verifier's entire provenance check is two self-reported strings, one standing in for two
hashes recorded right beside it.

And "the launcher checks them" is not a defence. **`BEN-156`, filed this morning in this same tool,
established that the executing copy can differ from the committed one.** A verifier whose provenance
rests on the producer's own HEAD string cannot detect the class it exists for.

### 6. Required inputs are optional, and their checks evaporate

`--source-npz` and `--nominal-target-sha` default `None` with conditional checks (`:571–584`,
`:598–601`); every R check at `:350–395` is behind `isinstance()` guards. With `R` and its operands
nulled **and the marker re-stamped so nothing else fires**:

```
rc=0   FAMILY_COMPLETE_PASS_REPLAY_SKIPPED   row PASS
n_passed=43  n_failed=0  failures NONE
r_derivation = {"R_recorded": null}
```

**Four checks silently disappeared (47 → 43) and nothing reported their absence.**

**The fix shape is already fifteen lines away, and that is the finding.** `--skip-replay` does this
*correctly*: the verdict downgrades to a named `..._REPLAY_SKIPPED` suffix, so a weaker run cannot
claim what a stronger one claims, and there is a test pinning it. **I built exactly the right
mechanism for one optional check and applied it to none of the others.**

### 7. The name-pin test never opens the launcher — and I told the mediator it did

`test_expected_names_match_the_launcher` asserts the two constants equal **string literals duplicated
in the test file.** Its docstring reads *"Pin the names to what the Slurm-captured batch script
actually sets. If the launcher changes, this is the test that should fail."* It does not open the
launcher. If the launcher changed, the test would still pass.

**I described these to the mediator as "constants pinned by a test to the launcher." That was false
and I should not have said it.** The test pins the constants to a copy of themselves — `BEN-149`
exactly — inside the test written to prevent the filename defect I fixed at `69c577b`.

## Why this is one defect and seven patches would leave an eighth

Every item is **the reconciler trusting a claim instead of measuring the world**: the caller's claim
about inventory size, the receipt's claim that training happened, its claim about where the artifact
is, a completeness claim that skips the canonical primitive, a HEAD claim standing in for two recorded
hashes, checks that evaporate when unrequested, and a test named for reading the launcher that reads a
copy of its own string.

**The single invariant:** *the reconciler derives every quantity it checks from the filesystem at
canonical paths and from constants pinned in the tool, never from the receipt's account of itself* —
with the corollary of equal weight that **a required input that is absent fails closed or downgrades
the verdict; it never silently removes its own check.**

Lane B reached the same sentence from provenance rather than verification: both launchers **bind
content, not HEAD**, digesting the loader against `e1402370…`. So *bind content, never a claim about
content.* B's measurement also confirmed this morning's four-state classifier **from the direction it
was not built for** — `git status` reporting "modified" on a file byte-identical to `origin/main`,
where mine reports `STALE_BUT_COMMITTED` on a file `git status` calls clean. Two-state models mislead
in both directions.

**The uncomfortable part, stated plainly:** I could not have found this by auditing myself. **My tests
share the tool's blind spot** — same idiom, same fixtures, same reasoning. That is a stronger argument
for an independent lane than any process document.

## What is and is not invalidated

**Not invalidated:** 50 target receipts and 24 training receipts are real and passed their checks;
every campaign run used the default `n=50` and correctly reported `PARTIAL`.

**Blocked:** using this tool to *declare* promotability. At a genuine 50/50 its exact
`FAMILY_COMPLETE_PASS` is indistinguishable **in the artifact** from one emitted at a caller-chosen
`n`, from a family whose trainings are receipt-only, or from one whose R checks never ran. Not a wrong
answer — **an unfalsifiable one**, which is the condition this tool exists to prevent elsewhere.

**I accept the BLOCK** and will not run a promotion pass on the current tool even at 50/50.

## Four failed probes of my own, and the fourth is the one to remember

- The **fixture** writes markers with no `mtime`, so `is_complete` failed for an unrelated reason
  while my mutation tripped a different check.
- My first `mtime` attempt landed in the **same second** as `mark_complete`; both sides saw nothing.
  That failure became qualification B on item 4.
- Without `--out` the tool prints a **condensed** summary with no per-replica rows. My probe parsed
  stdout, found none, and printed `check failures: NONE` — **true of an empty dict, not of the run.**
- My first null-R probe **changed the receipt's byte size**, so a marker check fired and returned
  `BLOCK` — which would have read as *refuting* item 6. Caught it, re-stamped the marker, re-ran, and
  got the confirmation above. Codex flagged the same confound independently; **we agree, and the
  coherent run was already done.** Had I sent the confounded result it would have been `BEN-207` aimed
  at my own refutation: the probe answered exactly the question asked, and the answer reads as
  covering the broader one.

All four are the standing rule: **establish a thing's write condition before reading it as evidence**
— including when the thing is your own probe's output.

## Related

- `OI-65` — the proposed repair, unapplied, with sequencing and test debt.
- `BEN-149` — the parent class: a name that claims verification suppresses the check.
- `BEN-156` — same tool, same day, found by a different mechanism: the *deployed* copy had drifted
  from the committed one. Neither defect was found by this tool's own tests.
- `BEN-207` — the tool that answers exactly the question asked, whose answer reads as covering more.
- [`state/gate5-reconciler-audit-confirmation-20260813.json`](state/gate5-reconciler-audit-confirmation-20260813.json)
  — every operand and every measured run.
