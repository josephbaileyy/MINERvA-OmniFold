# A guard forbade what a PINNED producer must produce -- and cited a predicate that does not say so

*Lane E, 2026-08-19. `BEN-476`. Campaign `EP-2026-08-17-data-only-cstat`.*

## THE HEADLINE, WHICH IS NOT THE SEED

**A guard cited a predicate as its authority, and the predicate does not say what the guard claimed.** The seed
policy is how it was found; the citation is what a reader should take away, because a wrong citation converts a
bug into an argument with an absent author — and someone would have gone and had it.

The failure text ended `(P6)`. P6 is a NAMING rule. I enforced it as an ABSENCE rule and put the citation in
the message, so the guard asserted an authority that never granted it. **Every guard message in this repo that
names an authority is suspect until that authority is read. Better no citation than a wrong one.**

The rest of this document is how that happened and what it cost.

## What happened

`57256638_0` -- the third single-member training smoke of the data-only C_stat product -- ran for
**02:58:44** on an A100 and FAILED with exit `1:0` **on its last action**. Everything the run existed to
test passed:

| what the smoke was for | result |
|---|---|
| does the module-global substitution replace the pinned loader's `:742` guard in a real process? | **YES** -- 0 occurrences of `bootstrap_seed=None (NOMINAL)` in either stream |
| does the `parents[3]` family-root fix hold? | **YES** -- 0 occurrences of `replicas/replicas` |
| does the training itself complete? | **YES** -- 6 fits, `LR anneal VERIFIED from the optimizer: 2 fit(s) at 0.0001, 4 at 1e-05`, both step1/step2 FINAL checkpoints written and round-trip verified |

It died writing the receipt:

```
[gate5-dataonly] write-time: withheld key(s) present: ['bootstrap_seed'];
the seed lives under `data_bootstrap_seed` (P6)
```

**That guard is mine, and it was wrong.** `train_fullevent_nominal.py:635-637` -- **PINNED**, digest
`91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc`, certified by
`p3f-pet-gate4-launch-code-gate-20260813.json`, zero edits available to me -- writes

```python
bootstrap_seed=np.asarray(
    -1 if target_meta.get("bootstrap_seed") is None
    else int(target_meta["bootstrap_seed"])),
```

and the data-only path forces `bootstrap_seed=None` at the loader seam **by design**. So the pinned base
driver stamps `-1` into `arrays`, `augmented = dict(arrays)` inherits it, and my assertion refuses it.

> **I ASSERTED AN ABSENCE THAT THE PRODUCER CANNOT PRODUCE.** Not a value it happened to emit -- a value it
> emits *precisely when the data-only condition holds*. The guard was unsatisfiable **exactly** on the class
> of artifact it was written to check.

## The part that is worse than the outage: the guard cited an authority that does not say it

The error message ends `(P6)`. **P6 does not say this.** P6 is a positive assertion, `cstat_data_only.py:317-321`:

```python
# P6 -- the seed under its OWN key. Never `bootstrap_seed`: that name means the three-stream
# coherent seed, and reusing it would make an absent-vs-empty distinction load-bearing again.
seed = int(np.asarray(get("data_bootstrap_seed")).item())
if seed != int(data_bootstrap_seed):
    raise SystemExit("[gate5-dataonly] P6 data_bootstrap_seed mismatch")
```

P6 forbids **putting the data seed under the name `bootstrap_seed`**. That is a NAMING rule. I read it as
*"the name `bootstrap_seed` must not appear"* -- an ABSENCE rule -- and then wrote the citation into the
failure message, so the message asserted its own authority for a rule that authority never granted.

> **A GUARD THAT CITES A PREDICATE IS MAKING A CLAIM ABOUT THAT PREDICATE, AND NOBODY CHECKS IT.** The
> citation is the most trusted token in the message: it is what tells a reader *"this is policy, not a bug"*
> -- which is exactly why a wrong one survives. Three sessions could have read `(P6)` and gone to argue with
> P6's author.

And the evidence was one file away in the other direction: the **target receipt** written by
`build_fullevent_replica_target.py:309` carries `"bootstrap_seed": int(args.bootstrap_seed)` -- a **real**
seed, 50000+index -- alongside `data_bootstrap_seed`. Had the key been forbidden by P6, the target receipt
would have violated it on every one of the 50 accepted members.

## Why the 178 controls could not catch it

Every control on `assert_pinned_required_keys` built its fixture as
`PINNED_VALIDATOR_REQUIRED_KEYS - DATA_ONLY_WITHHELD_REQUIRED_KEYS`. **The fixture derived the store from the
rule under test**, so it produced exactly the artifact the rule accepted and never the one the producer
emits. This is the same shape as the `parents[2]` off-by-one hours earlier, where every fixture passed
`family_output_root` directly and so no control ever exercised its derivation.

> **A FIXTURE COMPUTED FROM THE RULE UNDER TEST CANNOT DISAGREE WITH IT.** Both this defect and F2's needed
> the same thing: a fixture built from what the PRODUCER writes, not from what the CHECKER expects.

It recurred *within this repair*. My new power test for the retained withheld-key mechanism patched the
withheld set and then called `_store()` **inside** the patch -- and `_store()` reads that set, so it removed
the very key the guard should have objected to. `SystemExit not raised` looked like a broken guard rather than
a fixture that had agreed with the patch. Build the fixture **before** the patch.

## Repair

- `DATA_ONLY_WITHHELD_REQUIRED_KEYS = frozenset()`, and `bootstrap_seed` is required **present and exactly
  `-1`** (`DATA_ONLY_BOOTSTRAP_SEED_VALUE`). A **positive** assertion, not a tolerance: a data-only artifact
  carrying a real seed still fails, which is the case that matters -- it would mean the loader drew coherent
  MC factors after all.
- The compensating control was already built and stays: `extract_fullevent_fps.py:178` raises unless
  `bootstrap_seed == -1`, i.e. it reads `-1` as *proof of nominal*, so a data-only product carrying `-1`
  would be **accepted** there by mistake. Lane C's ruling -- *"it is not a guard to satisfy, it is a guard the
  product must never REACH"* -- is implemented as `install_nominal_extractor_dataonly_refusal()`, called at
  `extract_fullevent_replica.py:666`. **Safety comes from routing, not from the value.**
- Absence is now caught by the ordinary missing-required-key path, which already names the cost (55 of 77
  pinned checks skipped by its early return). I first wrote a dedicated `else: raise ABSENT` branch for it and
  **a control proved it unreachable** -- the third vacuous guard in this file today after `:46` and `:47`.
- The retained withheld mechanism guards an empty set, so it gets a test in the direction it acts: patch the
  set non-empty and prove it fires, plus a control pinning the emptiness so a silent re-add fails.

182 controls pass.

## Consequence for the divergence manifest, which is NOT cosmetic

The manifest partitions 77 static check sites as **18 DELEGATED + 55 UNEXECUTED-BY-CONSTRUCTION + 4
MANIFEST**. The 55 are unexecuted *because the pinned validator returns early on a missing required key* --
and `bootstrap_seed` was the missing key that triggered it. **With the key present, that early return never
fires and all 77 sites execute.** The partition's premise is void and it must be re-derived.

> A partition is only as sound as the condition that puts items in its buckets, and **that condition was a
> defect.**

## AMENDMENT, same day: my consequence claim was CORRECTED THREE TIMES, and the shape is the lesson

I wrote *"with the key present, that early return never fires and all 77 sites execute."* **It did not follow,
and it was corrected three times in one day by three parties** — by me, by lane C, and by an embargo note the
orchestrator wrote propagating it.

**Correction 1, mine.** The pinned validator is not INVOKED on the data-only path at all —
`cstat_data_only_readback.py:45` imports only constants from it (`BKG_MODE`, `ESTIMATOR`, `EXPECTED_CODE`,
`FROZEN_POLICY`, `SEED_POLICY_STRING`, `SOURCE_SHA256`, `TRAIN_ARTIFACT`, `TRAIN_RECEIPT`,
`expected_checkpoints`), and the family has its own validator, `validate_gate5_data_only_artifacts.py`. So
`OI-132` is a coverage-accounting defect, not a runtime hazard, and it gates no run.

**Correction 2, lane C's, and it kills the inference at its root.** Read the site
(`validate_gate5_training_artifacts.py:217-219`):

```python
checks.eq("required_npz_keys_missing", sorted(required_keys - set(store.files)), [])
if required_keys - set(store.files):
    return {...}
```

The guard is a **set difference over TWENTY-SEVEN keys with ANY semantics**. *One key's presence cannot witness
an empty set difference.* My sentence was a true statement about `bootstrap_seed` **carrying an unstated
universal about the other twenty-six** — and it read as established because the part that was checked was
checked properly.

**Correction 3, the embargo note.** It now records that the 18/55/4 embargo **STANDS while its
originally-recorded reason did not** — because an embargo resting on a checkable-and-wrong reason is fragile:
the next reader checks the reason, finds it false, and un-embargoes the number.

**AND THE CONCLUSION SURVIVES ON DIFFERENT EVIDENCE, which is not the same as having been right.** The producer
check run before the fourth submission derives, by AST from both drivers' source, that **all 27 required keys
are written** — 11 by the pinned `atomic_savez_compressed` dict, 16 by the replica driver, **zero orphans** —
and `57256638_0` independently proves it, because my own `missing` check is raised BEFORE the withheld check
and did not fire. So the early return indeed would not fire. **That is now a measured fact about 27 keys rather
than an inference from one**, and the difference is the entire finding.

> **A CLAIM THAT SURVIVES THREE CORRECTIONS BY BEING RE-DERIVED IS NOT A CLAIM THAT WAS RIGHT.** What made it
> durable was its shape: a verified fact about one member of a set, stated as though it settled the set.

## Checks to steal

1. **BEFORE ENFORCING AN ABSENCE, GREP FOR THE THING YOU ARE FORBIDDING. If the tree is full of it, your reading is wrong — not the tree.** Here a genuine absence rule would already have been violated **50 times, one file away**, in the target receipts of all 50 ACCEPTED members. That disproof cost one
   `git grep` and existed the whole time. The narrower form: an absence rule is a claim about a PRODUCER, so check the producer's source first, and check the pinned set before your own.
2. **When a guard cites a predicate, re-read the predicate at write time.** A naming rule is not an absence
   rule.
3. **Never build a fixture from the rule under test.** Build it from what the producer emits.
4. **Ask what a failing guard's cheapest satisfying artifact is.** If the answer is "one the pipeline cannot
   produce", the guard is the defect.
