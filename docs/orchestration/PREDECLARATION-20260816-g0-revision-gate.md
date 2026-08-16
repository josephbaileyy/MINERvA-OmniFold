# PREDECLARATION 2026-08-16 — the G0 revision gate: an expectation the tree cannot supply about itself

**Written before implementation.** Fixes `BEN-301`: *a digest pin authenticates content against an
expectation stored in the same tree, so it is blind to the tree being stale — both sides go stale together
and agree perfectly.* Measured instance: cluster wrapper `ee269b09` against a cluster pin literal
`ee269b09`, **G0 would have PASSED**, while the tree sat 663 commits behind and the run would have carried
none of `MOVE 2` / `MOVE 3` / `MOVE 4`.

**Approved by the mediator; adjudicated by this lane as part of the `(A′)` outcome. Local work only, no
cluster access, nothing launched.**

---

## 1. THE FOUR ITEMS, and item 3 is the only one that fixes the defect

1. `FF_EXPECT_REV` — **required, no default.** Absent → refusal.
2. Assert the tree is AT that revision: `git -C $REPO rev-parse HEAD` equals it.
3. **Compare each pinned file against `git -C $REPO show $FF_EXPECT_REV:<relpath> | sha256`, i.e. the blob
   at a NAMED REVISION, not a literal stored beside the file.**
4. Extend the pin set to `train_fullevent_nominal.py`.

**Items 1–2 alone would LOOK like a fix while leaving the co-location defect intact**, which is why this is
stated as a ranking and not a list. A tree can be at its own `HEAD` and still be 663 commits stale; only
item 3 makes the expectation something the tree cannot manufacture.

## 2. THE VACUITY GUARD, which is the first thing a later reader will try to remove

**`FF_EXPECT_REV` must match `^[0-9a-f]{40}$`.** `HEAD`, `main`, `@`, `HEAD~0`, a 12-hex abbreviation, a
39-hex string and any uppercase form are all **REFUSED**.

**Without this the gate is exactly repair-9's defect** — *"the token gate's staleness check was VACUOUS, not
weak: a symbolic `code_rev` passed it for every file, forever."* `FF_EXPECT_REV=HEAD` would resolve to the
stale tree's own `HEAD`, every blob would match its own working file, and the gate would pass on precisely
the configuration it exists to refuse. **The same defect, in a second gate, six days later.** Mirrors
`p4_check_verifier_token.py`'s `is_literal_commit_sha`.

## 3. FAIL CLOSED ON ABSENCE — the property, stated as the reason lane B's objection does not apply

Lane B's finding this session is that **prose did not prevent recurrence**: the fixture-degeneracy trap was
documented 440 lines up in the very file that reintroduced it. So "write a rule" is not the fix.

**A prose rule fails silently when unread. A value check fails silently when nobody supplies the value. A
required variable with no default cannot be silently omitted — omission is a refusal.**

That is the property this gate is designed around, and it is not new to the campaign: `BEN-317`'s
`fold_forward_composed_with_annealed_arm` was **`True` on EMPTY input**, which is why replacing it with
`attest_anneal_took_effect` — which raises on empty records — was worth doing at all. **A guard that is
satisfiable by the absence of its own evidence is the defect; a guard that refuses on absence is the fix.**
`FF_EXPECT_REV` having no default is therefore load-bearing and **must not be given one for convenience.**

## 4. WHY THE LOGIC IS IN A PYTHON HELPER AND NOT IN THE LAUNCHER'S BASH

Not a style choice, and it is a testability argument that the repo has already been bitten by.

`G0` uses `declare -A`, which needs bash ≥ 4. **The only bash on the development machine is 3.2.57**, so
`tests/test_foldforward_launcher_guards.sh` SKIPS there — and `LauncherWrapperPinTest`'s own docstring
already records the consequence: **"a pin that only a skipped test checks is a pin that goes stale
silently."** A revision gate whose power test cannot run where the work happens would inherit exactly that.

So: `ff_revision_gate.py` carries the logic and is unit-tested locally against throwaway git repositories;
the launcher keeps a **minimal bash preamble** that authenticates the helper against the revision *before*
invoking it, using only `git show` + `sha256sum` (bash-3.2 compatible, no associative array).

**THE BOOTSTRAP IS NOT FULLY CLOSED AND THAT IS STATED, NOT HIDDEN.** A file that checks pins cannot
authenticate itself: the helper verifies its own blob against the revision, but a modified helper could
simply skip that. The bash preamble closes one level — it checks the helper's digest against the revision
before running it — and the preamble itself is trusted. **The residue is that the preamble is trusted, and
the mitigation is that it is short enough to read in full.** No deeper claim is made.

## 5. THE POWER TEST, and the one control that licenses item 3

Per `BEN-314`, and per the mediator's conditions: built against **throwaway checkouts, never the live
tree** (`BEN-332` — a check whose result depends on local git state), with mutations applied to the
**working tree the gate reads**, not the index (repair-10's staged-copy trap).

**The axis each control licenses (`BEN-342`):**

| control | axis it licenses |
|---|---|
| symbolic revs (`HEAD`, `main`, `@`, `HEAD~0`, 12-hex, 39-hex, uppercase) all REFUSED | **vacuity** — repair-9's defect cannot recur here |
| a well-formed 40-hex sha that is not a commit in this repo → REFUSED | **existence** |
| **tree checked out at an OLDER commit, `FF_EXPECT_REV` naming a NEWER one → REFUSED** | **`BEN-301` staleness — the axis no co-located literal can reach** |
| **and in that SAME state, the old co-located-literal check PASSES** | **that item 3 is the fix and items 1–2 are not.** Without this the claim is unfalsifiable |
| a pinned file dirty relative to the revision → REFUSED | **uncommitted drift** |
| a literal disagreeing with the blob → REFUSED | the literal is **cross-checked, not authoritative** |
| `FF_EXPECT_REV` unset/empty → REFUSED | **fail-closed-on-absence (§3)** |
| clean tree at the named revision, files matching → PASSES | the gate is not simply always-refusing |

**The fourth row is the one that matters.** A gate that refuses a stale tree proves nothing on its own
unless the previous gate is shown to *accept* the same tree — otherwise "the new check is stronger" is a
claim about two implementations rather than a measured difference. Same standard as
`test_A_GLOBALLY_WRONG_BASE_RATE_IS_CAUGHT_HERE_AND_NOT_BY_THE_SIBLING`: **a claim that one guard beats
another is worth exactly the case where they disagree.**

## 6. WHAT THIS IS NOT

- **It does not move the wrapper pin.** This edits the launcher, not the wrapper. Lane B executed `MOVE 4`
  (`e284cdbc`) and the next reader will otherwise wonder; the wrapper's digest is unchanged by this work.
- **It does not repin the DRIVER**, which is receipt-bound (`BEN-270`). Driver/annealed/engine literals are
  untouched; `train_fullevent_nominal.py` is an ADDITION to the set, not a repin of anything.
- **It does not touch the cluster, launch anything, or authorize a run.** The stale cluster tree is a
  separate action under `(A′)` and is not performed here.
- **It does not retro-validate any completed run.** Runs before this print a 4-pin `G0` line and have no
  revision assertion; the log line necessarily changes shape, which is itself a provenance marker in the
  sense `BEN-317` describes — and earlier runs stay unattested on this axis, permanently.
- **No promotion, nothing into `docs/analysis-note/`,** five Gate-6 prohibitions at `19585b7` untouched.

## 7. Related

- `BEN-301` — the finding this implements. `BEN-312` — a pin set that omits an object the run's behaviour
  depends on; item 4 is that, for `train_fullevent_nominal.py`, whose `NOMINAL_SEED_POLICY` is imported
  unconditionally at `closure_powered_truth_reweight.py:224`.
- `BEN-317` — the boolean that was `True` on empty input; §3's precedent.
- `BEN-332` — a check whose result depends on local git state. `BEN-342` — name the axis a control licenses.
- `BEN-314` — power-test the guard. `BEN-318` — share exactly what you are not testing.
- repair-9 (`5fc06b6`) — the vacuous staleness check §2 exists to not repeat.
