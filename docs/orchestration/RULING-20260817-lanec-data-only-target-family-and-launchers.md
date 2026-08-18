# RULING — `C_stat^data` gets **its own target family**, and the launchers are **NEW, not edited**

**By:** lane C (PET). **Two rulings requested at the eighth stop, after Joseph ruled *"do it"* and E stopped
before `sbatch`. Nothing is queued.** Verified from the tree this turn; nothing run.

**Eight sites, eight stops. This is the first where the defect was in E's own default rather than in a
specification or someone else's code — and it was invisible until the run was authorized.**

---

## 1. RULING 1 — YES, its own target family. Reuse would make `P3` assert something FALSE

**The background fluctuation lives in the measured target** (`build_negweight_refined_target`:
`bkg_signed = -(w_bkg · pot_scale) · bkg_factor`, refined before the target is written). So reusing the
existing 50 three-stream targets would leave the background Poisson **inside** the family while `P3` asserts
`bkg_bootstrap_factor_full` is unity.

> **`P3` would be asserting something false about the family, in the artifact, under a guard E wrote.** That
> is not an inconsistency to document — it is the receipt-vs-reality class this campaign has refused all day,
> and it would carry **the single largest MC contribution the product exists to exclude.**

**New target family. Confirmed.**

### The target-stage predicates — `T1`–`T5`

Symmetric with `P1`–`P6` where the stage sees the array:

| | assertion |
|---|---|
| **`T1`** | target receipt carries `cstat_product == "data-only-v1"`. **Absence raises.** |
| **`T2`** | `bkg_bootstrap_factor` present, `shape == (n_bkg_full,)`, **explicitly `ones`** — `P3`'s analogue and **the predicate that makes the product honest**, because this is where the background fluctuation would otherwise live. **Asserted, never inferred from absence** (`BEN-405`). |
| **`T3`** | `data_bootstrap_factor` present, `shape == (n_data_full,)`, **equal to its canonical form** — `P4`'s analogue: coherence on the one stream that varies. |
| **`T4`** | seed under its own key `data_bootstrap_seed` — `P6`'s analogue, so `BEN-405`'s `-1` collision stays unreachable. |
| **`T5`** | `sig_bootstrap_factor_full` present, `shape == (n_sig_full,)`, **explicitly `ones`**. Required even though `build_negweight_refined_target` never consumes signal MC, because `:218-220` already reads `bootstrap["sig_bootstrap_factor"]` as evidence — **so the artifact must be self-describing on all three streams rather than silent on one.** |

### TWO EXISTING CHECKS MUST **BRANCH**, NOT RELAX — and one of them the dispatch did not name

**(a) `:215-222`, the three-stream replay.** It raises unless the loader's signal **and background** factors
equal canonical replay. Unity fails both. **Branch on `T1`'s tag and assert `T2`/`T3`/`T5` instead — never
skip.** Same rule as train and extract (`BEN-404`).

**(b) `:205-213`, the normalized-target-sum closure — NOT in the dispatch, and it fails too.** It asserts
`weights.sum() ≈ target_meta["step1_measured_normalization"]` at `rtol=2e-6, atol=1e-2`, i.e. against the
**replica `1e6·R`**. **For `C_stat^data` the target must close against `1e6·R_dataonly`, so this branches as
well.**

> **And note what `:205-213` already is: a TOLERANCED CLOSURE against an independently supplied target, at a
> declared `rtol`.** That is `BEN-408`'s prescribed form, already in the codebase, at the target stage.
> **So the bit-exact-vs-toleranced split is not a novelty I imposed — the target builder distinguishes the
> two predicate kinds already, and `P5`'s defect was departing from a distinction this repo had already
> made.**

*(Rider, `BEN-405`'s class at a second site: `:198-200` reads `bootstrap.get("n_data_full", -1)`. Under the
data-only route the block is empty, so `n_data = n_bkg = -1` and `:201` raises on a row-count mismatch
against `(-2,)`. **Loud, and diagnostic enough — recorded so nobody "improves" the default to something that
would pass.**)*

## 1c. LIVE — `57194055` fails closed at `assert_refined_target_is_replica`. **The fix shape is NECESSARY, INSUFFICIENT, and correctly LOCATED**

`_0`/`_1` FAILED 19:52Z: `ValueError: refined target has bootstrap_seed=None (NOMINAL)` from
`fullevent_fps_dataloader.py:742` via `train_fullevent_replica.py:288`.

### The diagnosis: one field carrying two meanings, for the third time

`assert_refined_target_is_replica` (`:736-747`) reads `target_meta["bootstrap_seed"]` to answer **"is this
target THIS replica's, or the nominal's?"** — an **identity** question. **Our design sets
`bootstrap_seed=None` as the MECHANISM for leaving MC unthinned — a CONSTRUCTION SWITCH.**

> **So `bootstrap_seed` carries two meanings — *which draw produced this* and *were the MC streams thinned* —
> and the guard reads it for the first while the data-only design set it for the second. This is the THIRD
> consequence of that overload** (`BEN-408`: `bootstrap_seed=None` reads as *no bootstrap* and means *all
> three streams off and `R` reverts*; `BEN-405`: the `-1` sentinel).

**The guard's CLAIM is true and the failure is a FALSE POSITIVE**, so `(c)`'s rule governs: **re-target,
never relax.** The naive relaxation — dropping the `None` check — would let **the actual nominal target**
through, and the loader's own cross-seed block at `:1479-1493` is **unreachable** under
`bootstrap_seed=None`, so **the driver assert is the sole binding.**

### The two limbs, and why the sha is load-bearing rather than an extra

| limb | what it establishes |
|---|---|
| `precomputed_target_replica_seed` non-`None` **and** equal | **the CALLER'S INTENT** — it is a *parameter*, not a field in the target's own receipt (`:1480-1493`), so **a driver that supplies the right number for the wrong file passes this limb** |
| consumed path bound to the receipt's `replica_target_sha256` | **the BYTES** — the only limb that makes it a claim about what was actually read |

**`BEN-245`: committed intent is not provenance. Limb 1 alone is intent; limb 2 is what converts it. Both
required — the sha is not belt-and-braces.**

### INSUFFICIENT: it does not satisfy `T4`, and without `T4` it re-creates the overload

**`T4` puts the data-only seed under its own key `data_bootstrap_seed`.** With `T4`, the guard reads identity
from **a field with one meaning** and never consults `bootstrap_seed` at all.

> **Without `T4` the patch makes the guard right about identity while leaving the overloaded field in place —
> so the same collision recurs at the next site that reads it. LAND `T4` WITH THE PATCH, not after.**

### LOCATION: correct, and constrained — the shared assert must NOT be edited

**`assert_refined_target_is_replica` lives in `fullevent_fps_dataloader.py`, the PINNED loader.** So:

> **The fix belongs at the driver (`:288`): BRANCH ON THE PRODUCT TAG — three-stream calls the shared assert
> unchanged, data-only calls a NEW driver-side assert.** Pinned loader untouched; the shared guard keeps its
> exact behaviour for the family it was written for (`BEN-404`).

### And the new assert needs its OWN negative controls — three, not two

**Controls `15 → 18`:** the **nominal** target rejected; a **wrong-replica** target rejected; and
**right-seed-wrong-file** rejected — **the third exists only because the sha limb exists, and it is the one
that would silently pass a fix built on limb 1 alone.** Each by mutating a synthetic store, never by
disabling the check, and power-tested by extraction from the shipped file (`BEN-409`).

### `T4` ACCEPTANCE CRITERION — pre-registered NOW, before the patch exists

**The mediator's question is the right one: does `T4` as landed give identity a SINGLE-MEANING field, or does
`data_bootstrap_seed` merely RELOCATE the overload?** That read is mine as the predicates' owner, and
**writing the criterion before the patch exists is the only way it can fail** (`BEN-403`).

**`T4` PASSES only if all five hold. Each is mechanically checkable; none requires reading intent.**

| | requirement | how it fails |
|---|---|---|
| **`R1`** | **every read of `data_bootstrap_seed` is an IDENTITY comparison** — `grep -n data_bootstrap_seed` over the changed files, classify each occurrence as *identity-read* / *construction-branch* / *write*. **Any construction-branch occurrence FAILS.** | `if data_bootstrap_seed is None: <behave differently>` — the overload, moved |
| **`R2`** | **`bootstrap_seed` is read for identity NOWHERE on the data-only path.** A new field that adds a reader without removing one has not de-overloaded anything | the old field still answers the identity question somewhere |
| **`R3`** | **its absent-form is a value no legal seed can take** — key-presence or `is None`, **never `== -1`, never `>= 0`** (`BEN-405`) | a sentinel that is also a legal value |
| **`R4`** | **either `bootstrap_seed` is ABSENT from the data-only artifact entirely, or an assertion fixes the two fields' relationship.** Two fields that can disagree with nothing raising is a reader's coin-flip | both present, unrelated, nothing checks |
| **`R5`** | **the identity assertion consults `data_bootstrap_seed` AND the sha, not one or the other** — limb 1 is the caller's intent, limb 2 is the bytes | a patch that de-overloads the field and drops the sha leg |

> ### ⚠ `R2` AND `R5` AMENDED 2026-08-17 — both were under-specified, and `R5` was WORTHLESS as written
>
> **`R2` EXTENDS ACROSS THE WHOLE PATH, INCLUDING THE VALIDATOR. Stated explicitly because the natural
> reading stops at the driver and that reading is wrong.**
>
> ***"The data-only path" is not a set of files — it is EVERY SITE THAT READS A FIELD THE DATA-ONLY ARTIFACT
> WRITES.*** `validate_gate5_training_artifacts.py:283` is
> `checks.eq("target_meta_seed", target_meta.get("bootstrap_seed"), seed)` with `seed = SEED_BASE + idx` at
> `:145` — **a SECOND consumer of the overloaded field, downstream of everything E is fixing.** Verified here.
> **And it is the WORSE of the two, because it fails after the FULL training spend rather than at 2m24s** —
> so the cheap failure is the one being fixed and the expensive one is downstream of the diff being scoped.
>
> **Mechanical form, so `R2` cannot be under-scoped again:** `grep -rn 'bootstrap_seed'` over **the whole
> corpus the data-only path touches — driver, loader-callers, target builder, extractor, validator,
> reconciler** — and classify each occurrence. **`R2` passes only at ZERO identity-reads of `bootstrap_seed`
> on that path.** A covering search with a stated corpus (`BEN-235`), applied to my own criterion.
>
> **`R5` IS REWRITTEN, because as written it was satisfiable by a TAUTOLOGY — and by my own standard that
> makes it worth nothing.** Verified: `train_fullevent_nominal.py:379` passes
> `precomputed_target=args.target_npy`; the loader echoes `os.path.abspath(precomputed_target)` to
> `consumed_precomputed_target` at `:1516`; and `:233` computes `got_sha = sha256_file(target_npy)` from the
> same path. **So both provenance legs compare `X` to `X`. The limb I called *load-bearing* — the one that
> converts intent into bytes — currently establishes NOTHING.**
>
> > **`R5` (amended): each provenance leg must compare a value the artifact ECHOES against a value derived by
> > a route THAT DOES NOT PASS THROUGH THE ECHO'S SOURCE.** Admissible second operands are
> > **family-position-derived** — `SEED_BASE + idx`, `campaign/replicas/replica_NN/target`. **Inadmissible:
> > anything derived from the driver's own arguments (`args.target_npy`).** *"Consults the sha"* is NOT the
> > criterion and never was; **independence of the two routes is.**
>
> **And the working form already exists in the file E has to fix anyway:** `:283` derives its operand from the
> member's **directory position**, and `:285-287` derives `target_path` from `campaign/replicas/replica_NN/target`.
> **So the independent route is implemented, demonstrated, and reusable — the fix is to POINT `:283` at
> `data_bootstrap_seed`, not to weaken it.** A good check failing for a bad reason is repaired by correcting
> the field, never the comparison.

**`R4` is the one I expect to be the near miss**, because leaving `bootstrap_seed: None` in the artifact is the
path of least resistance and reads as harmless — and it is exactly the shape that made `{}` indistinguishable
from absent (`BEN-405`). **If both fields ship, the relationship must be asserted, not documented.**

**I will run this against the sha when E reports it, and I will report a FAIL as readily as a PASS** — the
read is worth nothing if the criterion was written to be satisfiable by whatever arrives.

## 1d. THE FIFTH REQUIRED KEY — RULED `(e)`: write `bootstrap_seed = -1`, which is this pipeline's OWN encoding for *no coherent draw*

**Four things settled here. One is a withdrawal of mine, one resolves a disagreement between two greps, one
amends `V3`/`V4`, and the last is the ruling E asked for.**

### (i) MY `BLOCK` WORRY IS WITHDRAWN, and the reason I got it wrong is the day's own class

The mediator measured: `57194054` executes from **`/pscratch/.../gate5-data-only-frozen-d0c42bd`**, `git log -1`
→ `d0c42bdd`, tree **CLEAN**. **The array runs the FROZEN DEPLOYMENT, not the repo. `d14df112` changed nothing
it uses, so there is no mid-flight builder change and no `("code","target_builder")` heterogeneity.**

> **I checked WHEN THE REPO'S builder changed and inferred WHAT THE RUNNING ARRAY USES. That is `BEN-403(ii)`
> again — presence in the repo is not activity in the run — and it is the one axis I could not have checked
> from this host, which is exactly when an inference should have been labelled as one.** The frozen-deployment
> discipline worked; I read past it.

### (ii) THE TWO GREPS DISAGREED BECAUSE THEY DESCRIBED DIFFERENT OBJECTS — and the answer is worse than either

`grep -c data_bootstrap_seed` in the **frozen** builder → **2**; my repo read gave `:295`, `:299`, `:340` →
**3**. **Both correct. Read this turn:**

- **`:294-298` builds a TRANSIENT DICT as the argument to `cdo.assert_data_only_target_streams(...)`, and
  `:299` passes the seed again as a kwarg. NEITHER IS PERSISTED.** The comment says so: *"T1–T5 asserted over
  the block ABOUT TO BE WRITTEN."*
- **`:301` is `write_npy(output, weights)` — the target artifact is a BARE `.npy` of the weight array. It has
  no keys and cannot carry the field at all.**
- **`:340`, the line `d14df112` ADDED, is the RECEIPT write — the first and only PERSISTING occurrence.**

> **So in the frozen build `data_bootstrap_seed` is ASSERTED TWICE AND RECORDED NOWHERE.** The 14 targets were
> *verified* to carry the right data-only seed and carry **no evidence of it.** **That is `BEN-245` in its
> sharpest form: a guard validated a value into existence transiently, and nothing wrote it down — so the
> guard's own conclusion is unfalsifiable afterwards.**
>
> **RULE: a guard that validates a value must ensure the value is PERSISTED, or its conclusion does not
> survive the process.** `CONVENTION-receipt-ingredients` applied to a guard's **operands** rather than to a
> report's numbers.

**And it corrects my own `T4`, which said *"seed under its own key `data_bootstrap_seed`"* without saying
WHERE.** Given a bare-`.npy` artifact, **the receipt is the only possible home, so `T4` is a RECEIPT
predicate** — and the mediator's *"the entire target family fails it, uniformly"* is right, now for a precise
reason rather than a timing one. **I had hypothesised the npz might already satisfy it; there is no npz.**

### (iii) `V3` AND `V4` ARE PUNCTURED AS I WROTE THEM — E is right, and the fix goes one step further

`validate_gate5_training_artifacts.py:217` records `required_npz_keys_missing` with the missing list as `got`,
then **`:218-219` RETURNS EARLY.** **22 static check sites run before it; 55 after.** So on an artifact missing
one required key **those 55 never execute — and `V3`'s *"every non-manifest check PASSED"* is VACUOUSLY
SATISFIED BY 55 UNEVALUATED CHECKS.** `V4`'s floor was on **manifest size**, which the wrapper author writes,
so it cannot see it either. **A wrapper could go green having executed 22 of 77.**

- **`V4` AMENDED, per E: the floor is on EXECUTED checks — `n_passed + n_failed` — not on manifest size.**
- **AND ONE STEP FURTHER, because a floor is AUTHORED and can be set to 22: the executed count must EQUAL the
  count `V5` observes on a coherent member.** That number is **derived from the other path, not written by the
  wrapper's author.** **So `V5` supplies `V4`'s operand and the two controls interlock** — which is `R5`'s
  independence-of-routes principle applied to a count.

> **AND THE GENERAL DEFECT IS MINE AND IT HAS A NAME NOW: `V3` bounded the NUMERATOR — *which checks passed* —
> and never the DENOMINATOR — *how many ran*. A VERDICT PREDICATE MUST BOUND ITS DENOMINATOR.** Third time
> today I specified a numerator: `OI-94`'s data-only denominator, the sd-versus-variance share, and this.
> **Sibling of `BEN-423` (location vs property), distinct axis.**

### (iv) AND MY THIRD PRECONDITION WAS UNVERIFIABLE BY THE SEARCH I USED

E measured what I asserted: **missing key → `KeyError` from numpy; present-but-`None` → `TypeError` from
`int()` at `:224`.** **Neither is a `raise`, so my `grep -c 'raise\|SystemExit'` COULD NOT HAVE SEEN EITHER.**
`BEN-235` on my own precondition check.

> **RESTATED: no per-member function raises, AND every pinned check's operands are PRESENT and TYPED AS THE
> PINNED CODE COERCES THEM.** The second clause is the one with teeth and I did not have it.

### (v) THE RULING — `(e)`, and E was right that the three options were not exhaustive

**`(a)` omit** → 22 of 77, and closing the gap means the wrapper reimplements 55 checks, which `V1` forbids.
**`(b)` `50000+idx`** → asserts a draw that did not happen. Refused, agreed. **`(c)` rebind `required_keys`** →
function-local at `:207`, unreachable without editing a pinned file. **`(d)` write `None`** → key present, then
`:224`'s `int()` throws `TypeError` and the wrapper gets a traceback instead of a `Checks` object. Also fails.

> **`(e)` WRITE `bootstrap_seed = -1`. It is not an invented sentinel: it is THIS PIPELINE'S OWN EXISTING
> ENCODING FOR *no coherent draw*.** `VL130`'s verified Leg-F premises are *"identical inputs, identical
> 2,000,000-row `mc_indices`, **`bootstrap_seed = -1`**"*. **So `-1` already means, in this repo, exactly the
> state the data-only training stage is in.** It is `int`-coercible, so **all 77 checks execute**, and `:224`
> then fails with `got = -1` against `want = 50000+idx` — **an exactly predicted `V2` manifest entry, which is
> precisely what `V3`'s middle clause was built to hold.**

**Three conditions on `(e)`:**

1. **The receipt cites the precedent** (`VL130`'s floor premises), so a reader sees an established encoding
   rather than a convenience.
2. **`R3` does not forbid it, and the distinction is the whole point of `T4`.** `R3` governs
   `data_bootstrap_seed`'s **absent-form**; `bootstrap_seed = -1` is a **positive assertion** — *no draw was
   made* — not an absent-form. **Two fields, two roles.**
3. **`BEN-405`'s collision must be CHECKED, not argued.** `train_fullevent_replica.py:197` absent-defaults to
   `-1`; an artifact carrying `-1` against a caller passing `50000+idx` **raises correctly**, and the vacuous
   pass needs the CALLER to pass `-1`, which the data-only driver does not. **But that is my argument, so
   `R2`'s covering grep is EXTENDED FROM KEY NAMES TO VALUES: no consumer on the data-only path may
   absent-default to `-1`.**

*(And the mediator's parallel-track withdrawal is right and reaches the same place I did from the rebuild side:
`train_fullevent_replica.py:385` stamps `sha256_file(args.target_receipt)` into every artifact and
`validate_gate5_training_artifacts.py:277` checks it — so resubmitting now binds 50 artifacts to receipt bytes
we agree are false. **Zero bytes changed now, 151 A100-h later.**)*

## 1d-bis. ⚠ **`(e)` WITHDRAWN. The field is UNDER-DIMENSIONED, so no value could have worked — and `:178` is a ROUTING constraint, not a value problem**

**E is right and `(e)` is dead. Verified here against `origin/main`:** `extract_fullevent_fps.py:163`
`strap = _npz_get(z, "bootstrap_seed", -1)`, `:178` `if int(strap) != -1: raise SystemExit(… this path
extracts the NOMINAL (fail closed))`. **`-1` is that guard's POSITIVE TEST for *"this is the nominal, not a
replica"*, and writing it into 50 data-only REPLICA artifacts makes every one pass a guard whose entire job is
to refuse replicas.** 18 digest sites, so it cannot be fixed consumer-side.

**And the mediator's closing argument is the right one, accepted verbatim: my `VL130` precedent was sound, and
its own strength is what killed the option.** `-1` already means *"nominal, no draw"* in this repo. **The repo
SPENT `-1` on nominal, and the data-only replicas are replicas that did not draw — a state the encoding has no
room for.**

### WHY ALL FIVE FAILED — the field is UNDER-DIMENSIONED, not overloaded

`bootstrap_seed` encodes a **two-bit state** — *did it draw?* and *which draw?* — **in a one-field encoding
that assumed the bits were correlated:**

| product | drew? | field |
|---|---|---|
| three-stream | **yes** | seed `S` |
| nominal | **no** | `-1` |
| **data-only** | **no on MC, YES on data** | **the corner the projection discards** |

> **So the field is not overloaded, it is UNDER-DIMENSIONED — and no value can fix an under-dimensioned
> encoding.** That is why five candidates failed for five *different* reasons rather than converging on a
> near-miss, and it is the reason behind E's *"the artifact genuinely does not have the property the field
> names."* **We were never looking for a value.**

### AND A FINDING NEITHER E NOR THE MEDIATOR STATED: absence does not save `:178` either

**`:163`'s default is `-1` and `:178` fires on `!= -1`. So an artifact with the field ABSENT also passes** — the
guard cannot distinguish *nominal* from *field absent*. **Both `-1` and absence pass a guard whose job is to
refuse replicas. Only a real seed makes it fire, and that value is false.**

> **So `:178` cannot be satisfied HONESTLY and CORRECTLY by any data-only artifact. It is not a guard to
> satisfy — it is a guard the data-only product must never REACH.**
>
> **REQUIREMENT: the data-only path asserts POSITIVELY that the nominal extractor is never invoked on a
> data-only artifact.** A **routing** assertion, implementable in the **unpinned** `extract_fullevent_replica.py`
> (site 2). **A guard that cannot be satisfied honestly is a routing constraint, not a value problem** — and
> reading it as a value problem is what kept five options alive.

### `V3`'s MIDDLE CLAUSE, SHARPENED BY ITS FIRST REAL FAILURE

Verified: `reconcile_gate5_family.py:628` (`seed = int(r.get("bootstrap_seed", -1))`, then
`c.eq("seed_equals_base_plus_index", seed, SEED_BASE + idx)`) and `:343` — **`got = -1` whether the field was
correctly stamped `-1` OR lost entirely.** So `V3`'s *"failed EXACTLY as predicted"* **cannot discriminate a
correct data-only artifact from a corrupted one there.**

> **`V3` gains a condition: a manifest entry is ADMISSIBLE ONLY IF ITS PREDICTED `got` IS REACHED BY EXACTLY ONE
> ARTIFACT STATE.** The clause's discriminating power is a property of **the predicted VALUE**, not of the
> clause. **A predicted value that many distinct states share is not a prediction.**
>
> **E's `required_npz_keys_missing = ["bootstrap_seed"]` SATISFIES this** — a second missing key changes the
> value. **`-1` does not.** *(This is my own third condition — `R2` extends from key names to VALUES — doing its
> job and returning a `FAIL` on my own amendment.)*

### THE RULING ON E'S PROPOSAL: **neither as posed. `(A)`'s enumeration with `(B)`'s honesty.**

- **DROP the `V1` wrapper claim for this validator, explicitly and loudly.** E's line is right and I adopt it:
  **it would not buy `V1`'s purity with a field whose value is false.** And 55 replacements of 77 is **71%
  reimplementation** — `V1` would be true in form and false in substance.
- **KEEP the obligation `V1` was actually protecting, which is ENUMERATION rather than delegation. Every one of
  the 77 pinned check sites lands in EXACTLY ONE of three declared buckets:**

| bucket | meaning |
|---|---|
| **DELEGATED** | executed by the pinned module, verdict taken as-is |
| **UNEXECUTED-BY-CONSTRUCTION** | blocked by the `:218-219` early return — **each requiring a NAMED replacement** |
| **MANIFEST** | expected-fail with a **discriminating** predicted `got` |

> **No check in zero buckets, and the three counts must SUM TO 77**, checked against the pinned module's static
> check-site count.
>
> **`V1` made DIVERGENCE unrepresentable by delegation; the partition-sums-to-77 makes OMISSION unrepresentable
> by ACCOUNTING.** That is the property worth keeping, and it survives dropping the wrapper claim.

#### A FOURTH BUCKET — `ADDITIONAL` — because the three-bucket partition has no home for the check worth adding

**Prompted by a real gap the mediator surfaced.** `loader` is graded in **both** invariant blocks —
`:853`'s `invariant_paths` over target receipts (`present_t`) and `:878`'s role loop over training artifacts
(`present_r`) — and **the two group sets are never intersected.** So cutting the target and training
deployments at different times leaves **each block internally uniform while the two disagree, and no check
says so.**

> **THE GENERAL RULE: an invariant checked independently WITHIN each of two partitions does not constrain
> their UNION. Splitting a population is safe for per-partition invariants and silently unsafe for any
> invariant that was implicitly about the union — the check's TEXT is unchanged and its CLAIM narrows.**
> `invariant_constant_across_family[code.loader]` read as *"the family has one loader"* and now means *"each
> half has one loader."* **`BEN-406`'s tense class generalised from time to SCOPE.**

**The stated mitigation — cut the training deployment from a checkout whose `fullevent_fps_dataloader.py` is
byte-identical, and record both digests — is right and is a PROCEDURE.** `CLAUDE.md`'s own preference makes it
executable instead:

> **The data-only validator — unpinned, and being written anyway — ASSERTS that the loader digest recorded in
> the target receipts equals the one in the training artifacts.** One cross-block comparison that no pinned
> check performs. **It converts *"stated rather than assumed, because no check will say so"* into a check that
> says so.**

**And that assertion belongs in no existing bucket, which is why the partition gains a fourth:**

| bucket | meaning |
|---|---|
| **ADDITIONAL** | assertions the data-only path adds that **no pinned check performs**, each entry naming **the gap it closes** |

**Four buckets; `DELEGATED + UNEXECUTED + MANIFEST` still sums to 77; `ADDITIONAL` is counted separately and
each entry justified.** Without it the accounting would have had nowhere to put the one check most worth
having.

**And the cost, named rather than avoided: the honest state is ABSENCE, absence costs 55 unexecuted checks, so
the question was never *"how do we avoid that cost"* but *"who pays it and how visibly."* The partition makes it
visible. That is the whole of what this ruling buys.**

## 1e. MIGRATION REFUSED — **REBUILD.** A migrated key satisfies the LETTER of `T4`/`R3` and defeats their PURPOSE

**`cstat_data_only.py:452-457` fails `F1` closed on an absent `data_bootstrap_seed`** — *"absence is never
unity here"* — and the frozen builder `d0c42bdd` lacks `:340`. **So all 50 targets will be rejected at training
time: uniformly rejected rather than uniformly fine.**

**The value is recoverable** — `:309` writes `"bootstrap_seed": int(args.bootstrap_seed)`, which in a data-only
build **is** the data seed — so a script could copy it across and every receipt would satisfy `F1` with no
rebuild. **REFUSED, and E's reasoning is right. Here it is in `R5`'s terms, which makes it sharper:**

> **`F1`'s claim is *"this receipt carries `data_bootstrap_seed`, THEREFORE it was built as a data-only
> target."* That inference is valid only because the key is written BY THE DATA-ONLY BUILD PATH. A migration
> writes it from OUTSIDE the build — so the key's presence would evidence THAT A MIGRATION RAN, and nothing
> else.**
>
> **`F1` is a provenance check, and its power lives in the independence of its two routes: the key comes from
> the build, the claim is about the build. A migration collapses both into one route — the migration itself —
> so `F1` becomes A SELF-COMPARISON.** `R5`'s tautology class, one level up, **disguised as a data migration.**
>
> **And it is worse than proving nothing: `F1` would PASS while asserting something FALSE.** A check that
> converts an open question into a wrong answer is strictly worse than an absent one.

**And it defeats `T4` and `R3` precisely by satisfying them.** `T4` exists so identity is read from a field with
**one meaning**; `R3` so the absent-form is unmistakable. **A migrated key has one NAME and two PROVENANCES,
and nothing in the artifact says which** — so the letter of both is met and the purpose of both is gone.

### E offered migration-by-re-run as a FALLBACK. I am closing it instead of ranking it.

E's condition was that if migration happens at all the key must be written by **the target stage re-running**,
never by a script editing JSON in place, *"or the key stops being cross-process evidence and `F1` should be
deleted rather than satisfied."* **That condition is correct — and a target stage re-running IS a rebuild.**

> **So there is no migration variant to rank: the only acceptable form of it is the thing it was proposed as an
> alternative to. And E's disjunction is the right standing rule, promoted from fallback to absolute: IF
> `data_bootstrap_seed` IS EVER WRITTEN BY ANYTHING OTHER THAN THE TARGET STAGE, `F1` MUST BE DELETED RATHER
> THAN SATISFIED.**

### Conditions on the rebuild

1. **From a frozen checkout at `d14df112` or later, with the checkout's sha recorded in every target receipt** —
   so `code.target_builder` is uniform across all 50 **by construction** rather than by inspection. **Re-freezing
   a deployment is the discipline working, not being bypassed.**
2. **The rebuild must not leave TWO GENERATIONS readable in one root.** Otherwise a resume guard keeps the old
   ones — `BEN-023`'s shape, a guard validating existence rather than completeness. **Two routes exist (a fresh
   root per `L1`'s disjoint-root logic, or explicit removal of the old); I am NOT choosing between them and I do
   not authorize any deletion on scratch.** Stating the requirement, not the disposal.
3. **Unit disclosure, per standing practice: CPU on `shared_milan_ss11`, OUTSIDE Joseph's `151 A100-h` grant.
   ~46.5 CPU node-hours total (50 × 0.93), of which ~15 is RE-WORK** (the 16 built or running). **The re-work
   figure is the one that should travel, because *"34 of 50 unstarted"* is true and reads as though nothing is
   being spent twice.**

**My key: CONCUR — rebuild, migration refused.** *(D authored the migration route and has first refusal on E's
objection; this is one of the two concurrences, not the decision.)*

## 2. RULING 2 — NEW data-only array launchers. Not edits. And the pair must never be unified

**Measured: both array launchers are pinned; the two drivers and the submit wrapper are clean.** So threading
a product flag through the array launchers is **a pinned-file edit — the exact thing this route was designed
to avoid.**

**New launchers, and three reasons rather than one:**

1. **No pinned-file edit.**
2. **The three-stream launchers stay BYTE-IDENTICAL**, so every receipt that pins them remains true. An edit
   would invalidate them for a change that has nothing to do with the three-stream product.
3. **`CLAUDE.md`'s prohibition is satisfied on the right axis.** *"Do not rename or delete a tracked script
   cited in a RUN_LOG, ledger, or receipt"* — **new launchers ADD; they rename and delete nothing.**
   **Confirmed explicitly here so nobody later "tidies" the pair.**

> **AND A FORWARD PROHIBITION, because the tidy-up arrives as a refactor rather than as an edit: the two
> launchers must NOT later be unified into one parametrised launcher.** That would be an edit to a pinned
> file wearing a refactor's clothes, and it would re-open exactly what `(iii)` is blocked for. **115
> `sbatch_*.sh` names are load-bearing provenance; this makes 117.**

## 3. `8a` — the default is NOT flipped, NOT removed, and made IRRELEVANT BY CONSTRUCTION

**Why not make `--cstat-product` required?** It would buy loudness at the price of editing **both pinned array
launchers** to pass `three-stream-v1`. **A required argument purchases the exact pinned edit this route
exists to avoid. Refused, and the trade stated rather than left implicit.**

**The mechanical guard instead, and it needs no flag discipline at all.** All three existing launchers
**hardcode the three-stream output root** — `fullevent_cstat_n50` at `sbatch_gate5_replica_train_array.sh:13,14,32`,
`sbatch_gate5_replica_target_array.sh:13,14,34`, and `submit_gate5_replica_n50.sh:15`. So:

| | requirement |
|---|---|
| **`L1`** | the data-only launchers write to a **DISJOINT family root** (e.g. `fullevent_cstat_data_n50`), and pass `--cstat-product data-only-v1` explicitly |
| **`L2`** | **the drivers assert TAG ⟺ ROOT**: `cstat_product == "data-only-v1"` **iff** the output path's family root is the data-only one. **Mismatch raises.** |

**`L2` is the whole answer to `8a`.** It converts *"the only thing distinguishing them is a field nobody
would think to read"* into **a check that reads it**. And the existing 50 artifacts already occupy the
three-stream root under `atomic_savez_compressed(overwrite=False)`, so a wrong-launcher submission
**collides loudly** instead of silently rebuilding what exists.

### The rule from `8a`, and it unifies with one I already filed

E's framing — *"a safe default is only safe until something starts depending on the unsafe branch being
reachable"* — is right. **Sharper, and it is `BEN-405`'s third rule in the default-value domain:**

> **A DEFAULT'S SAFETY IS A PROPERTY OF THE CALL GRAPH, NOT OF THE VALUE.** *(Compare `BEN-405`: dormancy is
> a fact about today's call graph, not about risk.)*
>
> **Corollary, and it is the actionable half: when a second branch is authorized, every default that
> DISCRIMINATES between the branches stops being a safety property and becomes an unmarked assumption.
> Enumerate them at AUTHORIZATION time, not at submission time.** Here that enumeration was one grep
> (`grep -c cstat-product` over three launchers) and it was available the moment Joseph said *"do it"*.

## 4. On the predeclaration's retirement condition at `1.176×` — the product stands, and the CONDITION is wrong

**Asked for my view. It is substantive and it cuts both ways.**

**The comparability argument stands and is sufficient, and it is DEFINITIONAL rather than magnitude-based.**
Reducible-by-more-MC versus reducible-by-more-data is a real distinction to a global fit **at any ratio**, and
Joseph ruled on exactly that form. **A ratio of `1.176` does not weaken it. If anything a small definitional
correction is EASIER to defend than a large one, because nobody can suspect it of being chosen for its
size.**

**But the predeclaration's retirement condition as written is now WRONG and must be amended rather than
glossed.** *"A measured ratio near 1 would retire this product's stated motivation"* **fires on the expected
case.** Left standing, the product is **retired-on-arrival by its own predeclaration**, and a later reader
will find the condition met and conclude it was built against its own criterion.

> **AMENDMENT REQUIRED BEFORE SUBMISSION: state that the motivation is DEFINITIONAL, that the magnitude limb
> is retired AS A MOTIVATION, and that a ratio near 1 does NOT retire the product.** A predeclaration whose
> retirement condition fires on the expected result is not a predeclaration — it is a prediction nobody
> intends to honour.

**And this is exactly why `BEN-403` matters here: I am amending a stated condition BEFORE seeing the result,
which is the only time such an amendment is legitimate.** After the family lands it would be
indistinguishable from moving a goalpost.

### But the COST changes unit, and that goes to Joseph

**Not a reopening on the merits — a unit disclosure.** The new target family is **50 × 0.93 = ~46 CPU
node-hours** (`PREDECLARATION-20260813`'s measured `56344268`: `00:55:32`, 256 CPU, 1 node, **no GPU**).

> **Joseph authorized `151 A100-hours`. The target family is CPU and is OUTSIDE that unit.** Per the standing
> discipline — **surface any run with its unit** — this is an ADDITION to be surfaced, not absorbed into an
> A100 grant. **~46 CPU node-hours, zero additional A100-hours. It should take him one sentence, and it
> should not be spent on his behalf.**

## 5. Disposition

- **Own target family: CONFIRMED.** `T1`–`T5`; `:215-222` **and** `:205-213` branch on the tag, never relax.
- **New data-only array launchers: CONFIRMED.** No pinned edit; three-stream launchers byte-identical;
  `CLAUDE.md`'s rename/delete rule satisfied because this ADDS. **The pair must never be unified.**
- **`8a`: default unchanged; `L1` disjoint root + `L2` tag⟺root assertion carry the loudness.** A required
  flag is refused because it purchases a pinned edit.
- **Predeclaration: AMEND before submission** (§4). **The product stands.**
- **~46 CPU node-hours go to Joseph as a unit disclosure**, not as a reopening.
- **E is right not to quote a revised number until both rulings landed.** They have.
- **Nothing built, nothing submitted, nothing queued. 151 A100-h authorized and unspent.** Five Gate-6
  prohibitions at `19585b7` live; `C_ML` prohibited; `§3` of `CRITERIA-20260811` operative; `M(ii)` stays
  `(B)`, magnitude UNMEASURED; nothing enters `docs/analysis-note/`.

*Lane C (PET). Filed with `BEN-420`, first filing into a fresh closed ten-block.*
