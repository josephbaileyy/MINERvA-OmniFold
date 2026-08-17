# DETERMINATION — `OI-82` closed (it was an arithmetic slip, not a third measurement), `OI-60` re-costed (it is blocked on a Gate-2 re-run), `OI-41` given a disposition

**Lane E, 2026-08-17.** Follow-on to
[`DETERMINATION-20260817-pet-ten-items-state-and-oi126-shape.md`](DETERMINATION-20260817-pet-ten-items-state-and-oi126-shape.md),
working the mediator's ordered list. **No batch job. No `sbatch`/`scancel`/`scontrol`. `CODE_ROOT`
not touched. `docs/analysis-note/` untouched, not one character.** One login-node NPZ field read
(seconds, no allocation).

---

## 0. `OI-57` scoped, not closed — the mediator's read settled it and the answer was NO

I closed `OI-57` on the strength of the repair being on `main`, and flagged that I could not check
whether it reaches production because `CODE_ROOT` is prohibited to me. **The mediator ran the command
I wrote down, and the fix is absent:**

```
git -C <CODE_ROOT> merge-base --is-ancestor a764a72 HEAD   ->  NO
grep -c "OI-57" <CODE_ROOT>/.../train_fullevent_replica.py ->  0
last commits touching it there: 56d35af, 670e62d           (a764a72 absent)
CODE_ROOT HEAD: b82ac63
```

The row is now **`CLOSED-ON-MAIN / NOT-IN-PRODUCTION`** with the measurement and the sync as the
remaining action. **A bare `CLOSED` would have asserted something false about the tree that produces
the products** — and this is `a committed hook is not an installed hook` one campaign over.

---

## 1. `OI-82` — **CLOSED. The third value was never a measurement.**

The item: the three PET diagnostics' shared comment gave the annealed fold-forward ratio as
`1.0840529829474115`, while the two committed measurements agree at `1.0840529523112135`
(production `56563761`) and `1.0840529523260116` (trajectory `56818470`) — agreeing with **each
other** to `1.48e-11` while the comment sat `3.064e-8` away, 2,070× further and 30.6× the guards'
own `tol=1e-9`.

**Closed by the exact method the row prescribed** — a login-node read of the annealed NPZ's own
stored fields, `pet_fullevent_nominal_weights.npz`, sha256
`559a1020570929169a83e26dd9eea937bb34d6f4ecb230e332b792165ef6eb3e`:

| quantity | value |
|---|---|
| `fold_forward_sum_w_push_reco` | `1084052.9829474115` |
| `fold_forward_sum_w_reco` | `1000000.0282607947` |
| **`num / den`** | **`1.0840529523112135`** — bit-identical to the production receipt |
| **`num / 1e6`** | **`1.0840529829474115`** — bit-identical to the guards' comment |

**The "third value" is the numerator over a ROUNDED denominator.** `1e6` against
`1000000.0282607947` is `2.826e-8` relative, and the resulting gap measures
`3.063619802290418e-08` against the recorded `3.064e-8` — **to the last digit.**

**So it is an arithmetic slip, not a disagreement between artifacts**, and the row's fear —
*"overwriting a measurement I cannot reproduce is how a third value becomes a fourth"* — is
answered: correcting it **removes** a number rather than adding one.

**CORRECTED, not retired.** `inversion_screen.py`, `leg_mismatch.py` and `push_vs_acceptance.py`
now carry `1.0840529523112135` with the derivation beside it.

**The test pin was handled first, which is what the row's *"do not overwrite blind"* was protecting
against.** A fourth site — `test_pet_diagnostic_artifact_identity_guards.py:62` — pinned the old
number as `FF_08_10_ANNEALED_PER_GUARD_COMMENT`, feeding the "some wrong artifact" rejection axis.
**Editing the comments blind would have left a test asserting a value no longer written anywhere,
i.e. a green test pinning a fiction.** It is now `FF_08_10_ANNEALED` (corrected) **plus**
`FF_08_10_ANNEALED_ARITHMETIC_SLIP`, retained under a name that says what it is and **added as an
extra rejection case** — so the old number is still refused by the guards, and a reader meeting it
elsewhere can identify it instead of filing a fourth value.

**Verification:** identity-guard battery **24 passed**; full `nd-unfolding/tests` **1484 passed, 2
failed**, both pre-existing and environmental (`test_gate2_target_runtime` needs a `/pscratch` path;
`test_pet_fullevent_nominal_launcher` asserts TensorFlow is *not* importable and this laptop has it).
**Established rather than assumed:** neither test references any file I touched (`grep -c` → 0).
`verify_hash_bindings.py` → **ALL BINDINGS INTACT**; none of the three guards is pinned.

**Not re-derived:** the production and trajectory figures are quoted from their receipts. I measured
the NPZ and the arithmetic, not them.

---

## 2. `OI-60` — **NOT "blocked on nothing". It is blocked on a Gate-2 re-run.** `BEN-384`

**I wrote the whole prescribed fix and reverted all of it.** What was written: the loader telemetry
key, the target-stage array-compare, the same comparison in the training stage, the `:215` comment
corrected from "three" to actually three, the receipt's bare `canonical_replay_verified: True` given
a `canonical_replay_streams_compared` scope list (a verdict-only field is unfalsifiable, BEN-077),
and a three-case test — accept / absent / one-element-tampered — **power-tested by disabling the
production check and confirming the test failed `DID NOT RAISE`.** It worked: **6 passed.**

**Then `verify_hash_bindings.py` went from `ALL BINDINGS INTACT` to `*** BINDINGS BROKEN ***`, on
the loader edit alone.** Measured:

```
HEAD  fullevent_fps_dataloader.py  ->  e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1
mine                               ->  ff5862c92aed5fd72e38b86144a455af7bf43d577d105789e51adcd92001f1be
pinned as EXPECTED_LOADER_SHA      ->  pet/run_gate2_target_validator.sh:49
pinned as /code/loader/sha256      ->  g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json
```

**The validator's own header forecloses the escape, and it does so about precisely this class of
change:**

> *"Rather than argue the change was semantically inert for the negweight-refined path — **which is
> exactly the reasoning hash pins exist to reject** — the gate is re-run."*

It records the repo doing this **twice** (2026-08-04, 2026-08-05), re-running rather than
re-digesting, and requires the re-run's weights to come out **bit-identical** to the archived ones.

**Adding a telemetry key that no nominal-path code reads *is* the semantically-inert argument.** So
the precedent lands on it directly: a repin would be prohibited to this lane and **substantively
wrong** — it would make the Gate-2 receipt assert that a loader which did not produce the archived
target did produce it.

**Only the loader is enforced-pinned.** The target builder and the training driver produced no
mismatch, so the blocker is one file — but it is the one where the draw happens, so there is no
placing the export elsewhere.

**Re-cost:** *one key and two comparisons* → **one key, two comparisons, and a Gate-2 re-run (GPU)**.
**Against a residual this row itself calls narrow:** `n_data_full` is exported, the loader hard-raises
on a length mismatch at `:950`, and 16/16 replicas were re-drawn and matched. **Whether a Gate-2
re-run is worth closing a narrow residual is the owner's call and I have not taken it.** The diff
exists and can be reproduced from this section in minutes.

---

## 3. `OI-41` — disposition proposed, not taken

Its next-action is *"correct **future** W-offset citations"*. **No action satisfies that**, so the
item cannot be finished, only outlived. It is a standing convention in an item's clothes, and the
cost is not cosmetic: it sits in a table whose other rows are completable, so every open-item count
is inflated by one in a way no reader can distinguish from real work.

* **(a), preferred** — move it to the conventions set as a one-line rule beside the artifact (*"cite
  the committed fullcloud projection artifact, never the pre-fix subset"*) and close the item. A rule
  about future writing belongs where writers look, not in a to-do list.
* **(b)** — give it a closure condition by enumerating the existing mis-citations (*"the N
  occurrences at X, Y, Z are corrected"*), which makes it finishable. **I did not enumerate them, so
  N is unknown and (b) is uncosted.**

**Not actioned.** Re-filing another lane's item into a different document is the owner's call.

---

## 4. What I did not do

* **No repin, and no Gate-2 re-run** (§2). Nothing submitted; no allocation consumed. **Unit, per the
  standing instruction: the blocking run is GPU** — I did not estimate its A100-hours because I have
  not costed a Gate-2 re-run and will not invent a figure.
* **`CODE_ROOT` untouched**; the one read there was the mediator's.
* **`OI-58` hop 2's stale artifact untouched** — routed to lane C, whose file it is.
* **`OI-96`, `OI-12`, `OI-90`, `OI-61`, `OI-64`(C's) untouched** — gate change, other lane's,
  cross-lane ownership unknown, needs a GPU launcher, and blocked behind the id question
  respectively.
* **`OI-126` still not decided.**
