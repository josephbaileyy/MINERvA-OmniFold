# Pre-registered acceptance criteria: the temporary-file repair (`T1`-`T14`)

**Owner:** `lane/z-criteria-independent-assessment-20260910` (independent assessor).
**Written BEFORE the implementation exists**, on a briefing that said so explicitly, so that the
later verdict is checkable rather than fitted to whatever arrives. **No remedies are offered here** —
every item below is a requirement or a population, never a fix. That is deliberate and it is what
keeps me eligible to review the result (`offering-a-remedy-spends-my-next-verdict`).

**Approves nothing.** No repair existed at authorship. `R4` suspended, Gate 2 FAIL, nothing
submitted. This does not authorize a `--time` change, a launch, or any spend.

**CITABLE FOR:** the criteria, and the producer/consumer facts in §1 measured at `10eb1bac`.
**NOT CITABLE FOR:** any claim that a repair satisfies them — that requires a separate verdict.

---

## §1 — The subject, measured at `10eb1bac` so the criteria have anchors

**The producer.** `unified_throw_cov._atomic_savez` (`:148-163`):

```python
handle = tempfile.NamedTemporaryFile(
    prefix=os.path.basename(path) + ".", suffix=IN_PROGRESS_SUFFIX,
    dir=os.path.dirname(path), delete=False)
tmp = handle.name; handle.close()
try:
    np.savez_compressed(tmp, **arrays)
    os.replace(tmp, path)
except Exception:
    if os.path.exists(tmp): os.unlink(tmp)
    raise
```

Four facts follow, and they bound what a repair may and may not change:

1. **Publication is already atomic and must stay so.** `os.replace` within `dir=dirname(path)` is a
   same-directory rename, so it is atomic on any single filesystem and no reader can observe a
   partial product. This is the property Joseph's *"preserve atomic publication of completed
   products"* protects.
2. **The temp lands in the product directory**, named `<product>.<random>.tmp.npz`.
3. **The `except` branch cannot be the mitigation for the modelled hazard.** A wall-clock kill
   delivers `SIGKILL`, which runs no handler, no `except`, and no `finally`.
4. **`IN_PROGRESS_SUFFIX = ".tmp.npz"` (`:145`) is exported** so an exclusion is *derived* from the
   producer rather than retyped. Two consumers already do derive it: `unified_throw_cov.py:302`
   and `z_precursor.py:212`.

**The selection surfaces are TWO, not one.** A repair that closes only the first leaves the second:
- the **bare glob** passed by launchers, e.g. `--block-slabs 'uq_5d/block_slabs_5d_sb/block5d_*.npz'`;
  `block5d_knobs.npz.abc123.tmp.npz` matches `block5d_*.npz`;
- the **declared-population** check at `unified_throw_cov.py:294-315`, which already reports
  in-progress temps separately from undeclared members, with their own message.

**The consumer population is wider than the precursor's four arms.** At least nine launchers pass a
slab glob, across `4d`, `5d`, `fps` and `corrected` trees, with at least five distinct product
stems: `block5d_*.npz`, `uthrow5d_slab_*.npz`, `block4d_*.npz`, `uthrow4d_slab_*.npz`,
`blockfps_*.npz`. **Measured 2026-09-11: `find uq_5d -name '*.tmp.npz'` returns 0**, so there is no
stale temp in the live tree today and no cleanup obligation is being created by this repair.

---

## §2 — The criteria

Joseph's requirement, verbatim, is the yardstick: *"incomplete outputs must never match the
consumer's input selection. Preserve atomic publication of completed products, and test interrupted
writes, stale temporary files, and successful completion."* `T1`-`T4` are the four clauses of that
sentence; `T5`-`T14` are what makes each of them provable rather than asserted.

### The four named clauses

**`T1` — Incomplete outputs must not match the consumer's input selection.**
Proven against the **actual glob strings the launchers pass**, enumerated from the launcher text,
not against a pattern retyped in the test. The check must cover **both** selection surfaces in §1
and **every** product stem in the consumer population, or name the stems it does not cover.
*Fails if:* the proof is over one hand-written glob, or over the 5d stems only.

**`T2` — Interrupted writes are tested, and the interruption is manufactured, not asserted.**
The arm must kill a **real child process** with a signal that runs no handler (`SIGKILL`) **while
the write is in progress**, and then assert the state of the directory. An arm that raises an
exception inside the writer tests the `except` branch — which already works and is not the hazard
(§1.3). An arm that hand-creates a file and calls it an interrupted write tests the test author's
model of the producer (`a-fixture-must-agree-with-the-world-not-with-my-code`).
*Fails if:* the interruption is an exception, a mock, or a pre-placed file.

**`T3` — Stale temporary files at selection time are tested.**
The stale temp's **path and name must be produced by `_atomic_savez` itself** (or derived from
`IN_PROGRESS_SUFFIX` and the producer's naming), never hand-spelled. A hand-spelled temp at a
guessed path proves the guard rejects what the author expected the producer to write.
*Fails if:* the fixture contains a literal temp filename that the producer's naming is not asked to
confirm.

**`T4` — Successful completion is tested, and it is the arm that catches the inverted repair.**
The positive control must assert that the completed product **IS selected and loads with its
expected contents** — not merely that no exception was raised, and not merely that a file exists.
This is the arm that catches a repair which fixes *selection* by breaking *publication*: a change
making nothing selectable passes `T1`, `T2` and `T3` and fails only here. `BEN-450` is the template —
a stub that could not tell WRITTEN from BUILT left a deleted `Write()` green.
*Fails if:* the arm asserts existence or absence-of-error rather than contents.

### What makes those four provable

**`T5` — Atomic publication is preserved, and that is asserted, not assumed.**
`os.replace` must remain a **same-filesystem** rename. If the repair moves the temp to a different
directory (a natural way to get it out of the glob), the rename may cross a device boundary, at which
point it is a copy and **atomicity is silently lost** — the exact property `T5` exists to keep. A
repair that relocates the temp must show the destination is on the same filesystem as the product, or
show atomicity by another mechanism.
*Fails if:* the temp's directory changes and nothing establishes same-device.

**`T6` — The exclusion is derived from the producer, and a second spelling is proven to be caught.**
`IN_PROGRESS_SUFFIX` already exists for this. Every consumer that excludes must import it. A test
must show that a *divergent* literal spelling is detected rather than silently stopping to match
(`a-rule-retyped-is-a-second-implementation`).
*Fails if:* any consumer hard-codes `".tmp.npz"`.

**`T7` — Mutation reach is proven, not inferred.**
Deleting the exclusion must make a **named** arm fail, and the failure message must show the mutation
reached the *selection* — not that the suite went red because the harness broke first
(`a-mutation-test-can-be-refused-before-it-reaches-the-guard`). State which arm dies and on which
assertion.
*Fails if:* the mutation's death is reported as "the suite goes red".

**`T8` — The guard must not fire on a correct run.**
A check that refuses whenever a legitimate producer is mid-write, or that refuses a directory merely
because a temp once existed, is not a guard — it is a launcher that refuses itself
(`a-guard-that-fires-on-every-correct-run-is-not-a-guard`; three of four candidate guards in this
tree had that defect). An inertness arm must show the correct path is untouched.
*Fails if:* no arm demonstrates silence on a good run.

**`T9` — Concurrency: a second producer writing the same product must not corrupt either.**
`NamedTemporaryFile` gives distinct random names, so two writers get two temps — but the criterion is
that this is *asserted*, since a repair that makes the temp name deterministic (e.g. a fixed
`.partial` suffix) would remove that safety without any arm noticing.
*Fails if:* the repair makes the temp name deterministic and nothing tests two concurrent writers.

**`T10` — The success path must not accumulate temps.**
`os.replace` consumes the temp, so the current code leaves none. Any repair that writes an additional
sidecar (a marker, a lock, a `.done`) must state who deletes it and prove the steady state is clean.
*Fails if:* a repeated successful run leaves a growing residue.

**`T11` — The distinction between "in progress" and "stale foreign file" must survive.**
`unified_throw_cov.py:297-308` deliberately reports in-progress temps with their **own** message,
separately from undeclared members, because they mean different things operationally: one says the
producer was interrupted, the other says the directory is contaminated. A repair that makes temps
invisible to the glob must not collapse that distinction into silence — an operator needs to know a
task died.
*Fails if:* the interrupted case becomes indistinguishable from a clean directory.

**`T12` — The R5 coupling must be stated with numbers.**
This repair is the precondition for cutting `--time`, which is the live proposal for recovering the
`558.42`-against-`500` refusal. Now measured: the block arm's `--time` of 12:00 is **1.39×** its
observed maximum of **8.6389 h** over 83 rows, and its 252 committed task-hours are the largest single
term in the 543. So a cut is both the most effective lever and the one that most raises wall-kill
probability. **The repair's record must state which `--time` values it makes safe, justified from
observed maxima rather than from the arithmetic needed to fit under the ceiling**
(`i-transcribed-the-disqualifier-then-used-the-number`).
*Fails if:* the record implies a `--time` below the observed maximum is now safe.

**`T13` — No new tracked launcher without reconciling the census.**
`test_uq_remediation.SubstitutionFenceS1` asserts a launcher population of exactly 216 and is
**already failing at 217 on `main`** — a pre-existing failure, confirmed identical at `77a4af38` and
`10eb1bac`. A repair that adds a tracked shell file changes that number again.
*Fails if:* a tracked `.sh` is added and the census expectation is left as it is.

**`T14` — The regression population must be named, and matched.**
Report the runner, the root, the collection flags and both endpoints. `pytest tests` and
`unittest discover` give different collections over this suite; off the cluster, plain `pytest tests`
**aborts the entire directory** on `test_z_build.py`'s `ROOT.__spec__ is None` and runs zero tests, so
`--continue-on-collection-errors` is load-bearing. The baseline is `77a4af38` = **14 failed / 2895
passed / 6 skipped / 1 collection error**, and the delta must be attributable
(`my-recurring-failure-is-asymmetric-comparison`).
*Fails if:* counts are quoted without the runner and the control sha.

---

## §3 — Weighting, since I was asked which arm matters most

I agree with the briefing that the **successful-completion** arm (`T4`) deserves the heaviest weight,
and for the reason given: a repair that makes nothing selectable satisfies the two negative arms
perfectly. But `T4` as usually written — "the run completes without error" — does not catch it.
**Only the contents assertion does.** That is why `T4` is specified as *selected and loads with
expected contents*, and why `T5` sits beside it: the two ways to break publication while fixing
selection are to make the product unselectable and to make its appearance non-atomic, and each needs
its own arm.

Second heaviest is `T2`, because it is the only arm that can be faked without anyone noticing: an
exception-based "interrupted write" reads exactly like a real one in a test name and exercises a
branch that was never in question.
