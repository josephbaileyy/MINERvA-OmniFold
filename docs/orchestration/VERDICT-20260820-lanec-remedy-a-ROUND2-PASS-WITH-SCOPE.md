# 2026-08-20 — LANE C's ROUND-2 VERDICT ON REMEDY (A): **PASS-WITH-SCOPE**

**THE SCOPE, in one sentence a later reader cannot widen:** *`nd-unfolding/mii_adopt_unified_5d_stamped.py`
at `be7aec21`, with its coupled changes in `mii_root_payload_classes.py`, `mii_anchor_comparator.py`,
`test_uq_remediation.py` and `tests/test_remedy_a_adopt_wrapper.py`, is a correct, specification-complete and
adequately-powered implementation of remedy (A) **as source code**, and this verifies **nothing whatever about
any product, any execution, or any adoption path** — no line of its ROOT code has ever run against real
PyROOT, and no launcher in this repository calls it.*

**THIS VERDICT DOES NOT EXPIRE B1 STEPS 4-5.** `HANDOFF-20260819-lane-b-member-axis.md:64` is not met and
remains in force. **D2 alone blocks an unqualified PASS**, and the reason is not procedural: the expiry is
about remedy (A) being *effective for the member products steps 4-5 would create*, and it cannot be, because
`sbatch_finalize_5d_bkgaware_gpu.sh:181,186` — the only declared-member adoption path, in the same script whose
`:172` holds the do-not-delete pin — still invokes the **unwrapped** writer. Lifting the pause on this verdict
would produce exactly the identity-less adopted roots the pause exists to prevent, with no `hDiagCombinedOld`,
and would then compose with §11g into `BEN-485`(b).

**THIS VERDICT DOES NOT TOUCH THE 41.44 GB INTERMEDIATE.** No permission to delete, regenerate, re-stage,
move, truncate, archive or release it, and no sentence here may be read as one. `BEN-485`(b) stands as filed;
the pin at `:172` stays live.

## D1 is fixed AT THE CLASS, with one residual ruled safe

The universal coercing reader is **gone** — `_read_scalars` has no call site anywhere (only historical prose in
four documents). Replaced by `_read_int_scalars` (`:398`) and `_read_double_scalar` (`:442`), with `main:546`
reading the anchor through the double reader **and a test asserting that at the call site by parsing `main`'s
body**, not by inferring it from a pass.

**Where the class fix stops, measured with predictions first:** the int reader's guard is `float(raw) != int(raw)`
— **value-based, not type-based.** So an integral-valued `double` (P1: `3.0`) still coerces silently, and
`inf`/`nan` (P2) raise an uncaught `OverflowError`/`ValueError` **naming no key** — cosmetic, but on-theme in a
wrapper whose whole D1 lesson is what a failure *says*. `numpy.float64` is accepted and `float32` refused (P3/P4).
**Unreachable today** — the int reader serves only `LEG_IDENTITY_KEYS`, all genuine `TParameter("int")` — so
**ruled safe on the merits. TRIGGER TO REVISIT: a third call site for `_read_int_scalars`, or any key added to
`LEG_IDENTITY_KEYS`.** The complete fix asserts the object's ROOT class rather than its value, **and the fake
cannot test that** — a concrete instance of the boundary being load-bearing rather than residual.

`bool` is genuinely excluded: `:321` tests `isinstance(..., bool)` **first**, and the `None` check at `:312`
correctly precedes it so an absent key still gets the "unanchored" message.

## The ROOT fake: **KEEP IT WITH A STATED SCOPE** — and one sentence is now FALSE

**Honest instrumentation, not a false-confidence surface.** The repo's rule bites when a stub's answers are
taken *as* the real thing's answers; B does not do that. `_FakeParam` has one substantive method, and
`GetVal()` returning a float is *precisely the contract D1 crossed*, so it models the one producer in question.
The inference drawn is about the **wrapper**, not about ROOT. The module's docstring names the four things it
does not establish, says *"If PyROOT differs, these tests still pass and the wrapper can still be wrong,"* and
labels the deaf fixture *"BEN-106's hazard modelled, not confirmed."* **And it bought measured power: it turned
all five of round 1's survivors from uncatchable into caught.** The alternative was permanent zero coverage on
`_stamp_output` — where this campaign's own precedent puts the damage (`adopt_unified_5d.py:212-219`:
*"provenance stamped"* printed while nine writes failed into a read-only file). **Refusing a double there is not
purity, it is choosing zero coverage over scoped coverage.**

**REQUIRED CORRECTION: `mii_adopt_unified_5d_stamped.py:43` still reads "No ROOT test double is provided"**, and
`:44-48` still claims the three key properties are *"properties of ROOT, not of anything a fake could
demonstrate"* — while the fake **models two of those three**. B edited the function names in that very paragraph
and left the sentence its own change falsified. **This is the caveat-becomes-a-live-falsehood pattern and it is
the exact mechanism by which a later reader misjudges the suite**: they read *"there is no double"* and conclude
50 green tests are double-free pure logic. One line, pinned by no test.

**And B's defence of the fake is half false:** it says `Open`/`Write` are modelled so the wrapper's own
read-then-close and `fo.cd()` disciplines are exercised. The `cd()` half is real; **the read-then-close half is
not exercised at all** — lane C's **N4** removed `f.Close()` from `_read_diagonal` and **all 50 tests stayed
green.**

Hygiene checked independently: the fake installs only inside `_WithFakeROOT`, `__exit__` restores the prior
`sys.modules["ROOT"]`, and after running the module in-process `'ROOT' in sys.modules` is **False** — so it does
not recreate the session-pollution bug `11ab9f82` fixed.

## The refusal no longer accuses anything — emitted strings read, not summaries

Lane C ran the real message. It reports *"the two readings … DISAGREE"*, states `NOTHING HAS BEEN WRITTEN`,
lists three causes **with this wrapper first**, and carries `*** DO NOT DELETE, REGENERATE OR RE-STAGE THE
COMBINED INTERMEDIATE ON THE STRENGTH OF THIS MESSAGE ***` with the 41.44 GB / ~2.087 TiB operands. Both old
strings are absent **and their absence is asserted**.

**`BEN-469`'s test applied — what would a reader DO?** Check the two paths and re-read the wrapper: cheap,
reversible, correct under all three causes. **And the inverse failure was checked too:** a real corruption does
*not* read as routine noise, for a structural reason worth recording — **the prescribed action is correct under
every cause including (3)**, since if the intermediate really did change you would still want it preserved.
*A hedge that cannot induce a wrong action is not a harmful hedge.*

Two non-blocking residuals: **no discriminator** is offered for cause (3) (re-run the child; compare digest/mtime
against the child's log — one line would make the message diagnostic rather than only safe); and **"NOTHING HAS
BEEN WRITTEN" is true of the stamp and false of the product** — the child has already run and `--out`, an ~892 MB
adopted root, exists unstamped.

## B's sharper finding HOLDS, and it is a distinct mechanism → **`BEN-510`**

Verified from the diff, both sides. At `59987fea` the test asserted
`assertIn("not the matrix this product was built from", ...)`; at `be7aec21` it is
`test_a_DISAGREEMENT_is_refused_WITHOUT_BLAMING_AN_INPUT_FILE` asserting `assertNotIn` on that identical string.
**So the accusatory wording was literally a requirement of the green suite: fixing D1's second half was
impossible without deleting an assertion, and the suite would have gone red in defence of the defect.**

**Distinct from `BEN-469`** (read to the end of its row): 469 covers *the content of a diagnostic when a guard
misfires* and asks *"what does my message accuse?"* at **write** time. This asks *"does any test assert the
observable I am about to change?"* at **fix** time. **The check to write down: assert the PROPERTY a failure
message must have, never the SENTENCE it must contain.** Residual noted honestly — B's new tests still assert
substrings, which pins a *safety* property rather than a defect (the legitimate form) but is the same
brittleness pointed in a better direction.

**Id ruled `BEN-510`, opening a fresh closed block `510-519` for lane C.** Freeness derived by BOTH routes
against a freshly fetched remote, agreeing at **391 distinct ids** with an empty `comm -3`. `500-509` was
**deliberately declined**: its sole occupant is the fixture string at `test_ben_filing_owner_check.py:102`, and
taking a block containing a decoy id would make its occupancy permanently ambiguous to every future naive sweep
— the confusion `FINDINGS.md:35` already documents twice. Must cross-reference `BEN-469`, `BEN-040` and
`BEN-485` or it will read as a duplicate of 469.

## Mutation evidence

**Lane C's six new mutations, predictions first, file restored byte-exact after each: 5 of 6 caught** (vs 2 of 8
in round 1). Caught: deleting the non-integral guard; deleting the anchor type assertion; stamp-before-check;
perturbing the anchor by 1e-7; swapping the two offset key *values* (right keys, wrong data). **Survivor: N4**,
the read-then-close discipline — the only new gap.

**B's `mutation_probe_remedy_a.py` independently re-run: 16/16 CAUGHT, exit 0**, every row naming a failing
test, on a `git clone --no-hardlinks` under `$TMPDIR`; source tree untouched. Lane C first ran it against an
incomplete copy and **it refused over a red baseline** — its own fail-closed guard exercised by accident, a
point in its favour.

**Does the probe fix round 1's "8 mutations all on the pure-logic side"?** **It fixes it**, on three checked
grounds: the C-series are drawn from the *other* side of the boundary so the population is no longer selected to
be catchable; it is re-runnable and refuses over a red baseline, so it is an artifact rather than a number; and
it reports `ANCHOR-LOST` when a mutation no longer applies, so a stale mutation degrades to a visible finding
instead of silently counting as caught — *the failure mode most mutation tables have.* **One soundness caveat:**
`verdict = CAUGHT if rc != 0` would score a mutation that merely breaks importability as caught. It did not
matter here (all 16 named a real failing test) but the criterion should be *"a named test failed."*

## Verified vs assumed

**Re-derived by lane C:** the pinned digest computed not relayed; **no `.sh` and no pinned file in the round-2
diff**, so D2 really is untouched; wrapper suite **50 passed**; the two coupled suites **283 passed / 2 skipped**,
both skips pre-existing; `HEAD == origin/main`, so this is live evidence; all of Q1-Q4; the fake's `sys.modules`
hygiene; **D3 read in full — ruling §5(e) is now SATISFIED**, the stale tally citation *replaced* rather than
reworded, and the one surviving `STAMP_COVERAGE` mention in the comparator is a historical note about the
removal, which is correct practice.

**Taken from the mediator and NOT reproduced (ASSUMED):** the symmetric full-suite comparison at `018d39f8`
(5 failed/1913 vs 5 failed/1930) — lane C's own full run timed out on TensorFlow imports. **And it could not
reproduce "one previously-skipped test now runs."** *Mediator's note: that sub-claim was an inference from the
full-suite skip count falling 5 → 4, while lane C observed the two-file scope where both skips are pre-existing.
The two counts are at different scopes and do not disagree — but the inference that a specific test began running
is unproven and should not be repeated.*

**Still assumed and unchangeable here:** that ROOT accepts new `TParameter` keys on `UPDATE`; that a
`RECREATE`d-and-closed file reopens writable; that `TFile.Open` re-points `gDirectory`; that `f.Get(absent)` is
falsy; that `GetNbinsX()` is 10,694 on a real member intermediate. **The fake models the third and fourth and
establishes neither.** The cluster checkout is unreconciled, so every finding is about *this* tree.

## OPEN, in lane C's fix order

1. **D2 — no callers.** The scope-defining item; a frozen-provenance decision, correctly neither B's nor C's.
2. **`:43`'s "No ROOT test double is provided"** — now false, unpinned, one line. Required before the fake's
   honesty is unqualified.
3. **N4** — `_read_diagonal`'s close is uncovered, and B's stated justification for the fake claims otherwise.
4. **Q1's residual** — value-based rather than type-based int guard; `inf`/`nan` give an uncaught traceback.
5. **Q3's two residuals** — no discriminator for cause (3); "NOTHING HAS BEEN WRITTEN" should distinguish stamp
   from product.
6. **`BEN-510`** from block `510-519`, cross-referencing 469 / 040 / 485.
7. Unchanged by design: `RECOMPUTABILITY["sqrt_tr_old"]` still `NOT_RECOMPUTABLE` (correct — no product carries
   `hDiagCombinedOld`); ruling §8 item 2; **the class-table flip's live cost is now in its third day with no
   product able to satisfy it.**

**Read-only discipline held.** Nothing created, edited, moved or deleted; no commit, push, checkout, reset or
stash. All mutation work on copies under `$TMPDIR`.
