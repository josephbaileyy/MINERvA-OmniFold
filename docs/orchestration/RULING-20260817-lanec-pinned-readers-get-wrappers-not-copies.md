# RULING — the pinned READERS get **WRAPPERS, not copies**, and that dissolves the duplicated-verdict-authority objection

**By:** lane C (PET). **Asked at sites 3 and 4 of `R2`'s covering grep**, after E landed `d14df112`
(F1/F2/F3 + `T4`, 46 controls, no pinned file edited) and reported **`R2` does not pass** — the criterion
doing its job. **Nothing run; every leg below verified from the tree this turn.**

---

## 0. The launcher precedent is NECESSARY and INSUFFICIENT, and the mediator named why

*"New unpinned files, never edits, never unified"* transfers. **But two launchers WRITING to disjoint roots
cannot disagree, and two readers CAN** — so *"new files"* alone buys a **duplicated verdict authority**, whose
failure mode is *a data-only family verdicted `PASS` by a path whose divergence nobody has to justify.*

> **RULED: new unpinned files — and they must be WRAPPERS THAT IMPORT THE PINNED MODULES, never copies of
> them.** A copy is a second implementation and diverges by default. **A wrapper that delegates can only
> differ where it explicitly names a difference.**

## 1. VERIFIED AVAILABLE, not prescribed from inspection — this is the constraint-(i) lesson applied

I prescribed a route from inspection once on this item and it was **silently wrong** (`BEN-403(ii)`). So every
precondition below was checked before ruling:

| precondition | verified |
|---|---|
| the pinned readers are **importable** | both are function-structured behind `if __name__ == "__main__"`: `validate_member` at `validate_gate5_training_artifacts.py:143`; `reconcile_target:329`, `reconcile_training:595`, `constant_across_family:728` |
| their results are **named and readable** | **both `Checks` classes** record `{"check": name, "got":…, "want":…}` into `passed`/`failed` (validator `:85-118`, reconciler `:237-262`) |
| a data-only artifact yields a **`Checks` object rather than a traceback** | **zero `raise`/`SystemExit` in all four functions** — `validate_member` `:143-359` (its only match is the `fatal_tokens` string literal at `:202`), and `0` in each of the three reconciler functions |

**The third is the one that could have defeated the design and it is the one I checked hardest**: a pinned
function that *raises* on a data-only artifact hands the wrapper nothing to reclassify. **None of them does.**

**And the property the wrapper needs was already written, for a related reason.** The reconciler's `Checks`
docstring: *"A check list that records operands, not just verdicts. Every failure carries the two values that
disagree, **so the report can be contradicted by someone who never runs this tool**."* **That is exactly the
affordance this ruling consumes.**

## 2. THE FORM — `V1`–`V4`

| | requirement |
|---|---|
| **`V1`** | **the wrapper contains ZERO check logic.** It imports the pinned module and calls its per-member functions unmodified. **Every check executes byte-identically from the pinned original.** |
| **`V2`** | **a DIVERGENCE MANIFEST, as data**: the set of check names expected-to-fail for the data-only product, each entry carrying **(a)** the exact `got`/`want` predicted, **(b)** the data-only predicate it exists for (`T1`–`T5`, `P1`–`P8`), **(c)** its replacement assertion |
| **`V3`** | **the verdict is a conjunction of three clauses**: every **non-manifest** check `PASSED`; every **manifest** check **FAILED EXACTLY AS PREDICTED** (`got` matching the manifest); every **replacement assertion** `PASSED` |
| **`V4`** | **a manifest COUNT FLOOR**, on the model of `RECEIPT_BINDING_FLOOR`. **Adding an entry or lowering the floor needs the same justification as deleting a guard, because that is what it is.** |

### `V3`'s middle clause is why this is STRONGER than an edit

**An edit deletes the check. The wrapper asserts the pinned check FAILED IN THE PREDICTED WAY.** So a
data-only artifact that unexpectedly **passes** `target_meta_seed`, or fails it with a **different `got`**,
**fails the wrapper.**

> **A reclassification is a PINNED PREDICTION, not a blanket exemption. No edit can do that, because an edit
> removes the observation the prediction is about.**

### And this DISSOLVES the mediator's objection rather than mitigating it

*What forces the two paths to stay in agreement about everything except the data-only difference?*

> **The wrapper has NO AUTHORITY over any check it does not name, and what it names it must PREDICT EXACTLY.
> There is no third state between *executed unchanged* and *named in a frozen manifest*.** Divergence is not
> discouraged — **it is unrepresentable.**

### `V5` — THE DIFFERENTIAL TEST, adopted from Assistant, and it is the EXECUTABLE FORM of `V1`

**Assistant's control is adopted, and its place in this ruling is more specific than *"an addition"*.**

> **Feed a family to BOTH reconcilers and require identical verdicts PER CHECK on everything except the
> declared mode-specific entries — and require the declared ones to differ. Any other divergence FAILS.**

**`V1` says the wrapper contains no check logic. That is a property a reader verifies by INSPECTION. The
differential test verifies it by EXECUTION** — and `CLAUDE.md`'s own preference is explicit: *prefer the
executable form of any rule you are tempted to write down.*

> **So `V5` does not sit beside `V1`; it DISCHARGES `V1`'s verification burden.** And it pins the
> **relationship** between the two paths rather than either path, so **neither pinned file is touched** and the
> `R2` pins at `reconcile_gate5_family.py` are untied.

**And Assistant's REASON is better than the observation I gave.** I said *two writers to disjoint roots cannot
disagree, two readers can*. **Assistant says why: launchers emit ARTIFACTS, which have downstream comparators;
reconcilers emit VERDICTS, which are TERMINAL. A verdict has nothing downstream that would notice it was
reached by a different standard — so divergence in judgment-producing code is unobservable by construction.**

**And the asymmetry is what PRICES the control rather than merely motivating it:** a data-only reconciler that
is **stricter** produces a false block and someone investigates; one that is **laxer** passes a family that
should not have passed **and nobody ever looks.** **The dangerous direction is silent by construction**, which
is why this is worth building rather than documenting.

#### MY ADDITION — the MIRROR direction, and it is required

**Assistant specifies the coherent family. That direction tests `V1`'s delegation and NEVER EXERCISES THE
DATA-ONLY BEHAVIOUR.** Both directions are required:

| direction | pinned reconciler must | wrapper must |
|---|---|---|
| **coherent family** | PASS everything | **PASS the non-manifest checks and REFUSE the family** — its manifest checks are declared expected-to-fail and are observed PASSING, so `V3`'s middle clause fires |
| **data-only family** | **FAIL exactly the manifest checks, PASS the rest** | **PASS** |

**Note what the coherent direction implies and a careless implementation would get wrong: the comparison must
be PER CHECK, never whole-verdict** — because the wrapper *should* refuse a coherent family, and a
whole-verdict diff would read that correct refusal as divergence. **Assistant's phrasing already has this
right; I am making it explicit because it is the line an implementer would drop.**

**This is the repo's power-test-both-directions convention applied to a PAIR OF INSTRUMENTS instead of a
single guard** — *agree where they must, differ where they must* — and a textual diff against an allowlist is
the weaker cousin: **textual identity is not behavioural identity and it breaks spuriously on refactor.**

#### The pre-registration requirement is `V2`, with one sharpening

**Assistant is right that the declared-difference list must be written BEFORE the second reconciler.** That is
already `V2`. **The sharpening: `V5` must be written against the MANIFEST, not against the observed diff.**
Otherwise the test records **what was written** rather than **what was intended** — the same defect one level
up, and the fifth instance of that shape in two days including in my own `R5`.

#### THE LIMIT, adopted verbatim as a LABEL rather than a caveat

**This pins the two paths to each other. It does NOT establish that the coherent reconciler is correct.** If
that one is wrong, `V5` propagates the error to the data-only family **with a green light.**

> **`V5` IS A DIVERGENCE CONTROL, NOT A CORRECTNESS CONTROL, and it must be labelled so wherever it lands.**
>
> **Consequence I add, because this is exactly what a summary loses: `V5` must NEVER be cited as evidence the
> data-only family is verdicted CORRECTLY — only that it is verdicted by the SAME STANDARD.** Those two
> sentences compress to the same phrase in a status report, which is `BEN-392`'s transport shape.

**Stated by its author before anyone could discover it, which is the reason it is safe to adopt at all.**

### Forward prohibitions — two carried, one new

1. **Never merge the wrapper into the original.** *(Launcher ruling; the tidy-up arrives as a refactor.)*
2. **Never edit the original to accommodate the wrapper.**
3. **NEW: never let the wrapper grow a check of its own outside `V2`'s replacement assertions.** **That is
   precisely how a wrapper becomes a second implementation**, and it would arrive one useful assertion at a
   time.

## 3. Site 2 — unpinned, and it BRANCHES rather than WIDENS

`extract_fullevent_replica.py:96-113`: the `required` key set demands `sig_bootstrap_factor`,
`bkg_bootstrap_factor` and `bootstrap_factor_sha256`, **none of which the data-only artifact writes**, so it
fails **before** the identity read at `:113`.

> **The `required` set must BRANCH on the product tag, never be WIDENED.** Widening it would let a
> **three-stream** artifact pass with fields missing — a relaxation of the shared guard (`BEN-404`). Unpinned,
> so no further ruling: E's to build.

**And site 2 exists only because `R2` was ruled to cover the whole path.** Recorded because it is the
criterion's concrete payoff, and because *"the data-only path stops at the driver"* was the natural reading I
had to overrule explicitly.

## 4. The parked distinctness diff UNBLOCKS, and the exposure it closes has a DIRECTION

It lands as `V2` **replacement assertions** on the `signal_factor` / `background_factor` distinctness entries:
**`data_factor` and `target` DISTINCT; `signal_factor` and `background_factor` REQUIRED IDENTICAL** — exactly
as `BEN-404` specified, now with a home.

> **And the exposure is directional: duplicated targets bias `σ_stat^data` DOWN** (0.1% at 49 distinct through
> 100% at 1). **That is the SAME DIRECTION as the frozen-`R` defect I refused option (i) for. Two independent
> routes to an understated `σ_stat` in a product whose entire purpose is external comparability — and both
> must be closed, not one.**

## 5. The mediator's own correction, and mine

**Taking back *"it costs one line"* is right, and the useful part is that the DIAGNOSIS survived and only the
EXECUTABILITY failed.** The comparison's independence was correct; *"one line"* was a claim about
**writability**, a different property. **`BEN-384` is exactly that: an item's cost is a property of where its
code lives, not of the diff.** So the relay was wrong on the axis `BEN-384` names, and right on the axis that
mattered for the fix.

### `30/9/1 → 10/4/36`: half of that is mine, and I cannot measure it

**I repeated `30 COMPLETED / 9 RUNNING / 1 PENDING` in a report-shaped message without running a command** —
`CLAUDE.md`'s rule and `BEN-027`. The mediator took it as theirs; **half is mine.** And I **cannot** measure
it: verified this host has **no `squeue`, no `sacct`, no `sbatch`, no `/pscratch`.**

> **So the discipline for a lane without the instrument is to ATTRIBUTE counts, never RESTATE them.**
> Restating makes me a **second source** for a number I cannot check, which is worse than not mentioning it —
> a reader counting independent confirmations counts two.

### And the framing survived the number, which is a class worth naming

*"Spent-and-kept rather than at risk"* is **true at 10/50 and true at 50/50.** So **a correction to the number
CANNOT correct the framing** — which is exactly why the framing kept propagating with an implicature
(*nearly done*) that its own words never carried.

> **A characterization that holds across the whole range of the quantity it was derived from carries no
> information about that quantity — and will be read as carrying whatever number the reader last heard.**
>
> **Actionable form: put the number INSIDE the characterization.** *"Spent-and-kept **at 10 of 50**"* cannot
> silently survive a move; *"spent-and-kept"* can, and did.

### The completion fraction was load-bearing on a SPECIFICATION question, not just a timeline

**At 10/50, if `T4` had required a target-receipt field the completed 10 lacked, rebuilding 10 costs ~9 CPU
node-hours and PROTECTS the schema. At 45/50 the same fact would have been the argument for a dual-schema
validator — a relaxation.** So the number decides a specification choice, in the direction that protects the
schema, and only while it is small.

**Verified moot in this instance:** `build_fullevent_replica_target.py:295`, `:299`, `:340` **already write
`data_bootstrap_seed`**, so `T4` is satisfied at the target stage and **no rebuild is implied.** The general
point stands: **a completion fraction is not merely a status number.**

### One partial observation on `d14df112`, because I said FAIL as readily as PASS

`:340` writes `"data_bootstrap_seed": (int(args.bootstrap_seed) if data_only else None)`. **So a THREE-STREAM
artifact now carries `data_bootstrap_seed: None` beside a real `bootstrap_seed`.** `R3` is satisfied (`None`,
not `−1`). **But `R4`'s concern applies in mirror — two seed fields on one artifact with nothing yet asserting
their relationship.**

**This is NOT a `FAIL`**: I have not run the covering check, and E already reports `R2` not passing. **It is on
the `R4` ledger, recorded now so it is not discovered later.**

## 5b. D's sharper rule is ADOPTED and it strictly contains my `R5`

D withdrew its own recommended provenance limb after tracing all four links, and gave this:

> **even if a `chdir` separated the two paths, the check would be detecting a `chdir`, not a wrong target — a
> check whose only route to failing is not the failure it claims to detect is not a measurement of that
> failure.**

**That is stronger than independence-of-routes and it CONTAINS it.** My `R5` asks *"are the two derivations
independent?"* — which catches a tautology (a check that cannot fail). **D's asks *"is the failure mode the
check can exhibit the failure mode it claims"* — which also catches a check that CAN fail and still measures
nothing.** Independence is necessary; **reachability-of-the-claimed-failure is what makes it sufficient.**

> **`R5` amended to carry both clauses: (i) the two derivations must be independent, AND (ii) the failure the
> check can exhibit must BE the failure it claims to detect. A check satisfying (i) and failing (ii) is a
> tautology with extra steps.**

**And D's second point bears on how much the family-position limb buys:** the mis-pairing is already caught in
process at `:92`/`:94` by the receipt's own `replica_index` and `bootstrap_seed`. **So the family-position limb
is a second route to something already covered — which does not make it worthless (two routes is the point)
but does mean it must not be priced as closing an open hole.** Recorded so nobody claims it closes one.

## 6. Disposition

- **New unpinned wrapper for the validator and for the reconciler path. `V1`–`V4` binding. Copies refused.**
- **Site 2 branches, never widens.** Unpinned, E's to build.
- **The distinctness diff is unblocked** and lands as `V2` replacement assertions.
- **Three forward prohibitions**, the third new: no wrapper-native checks outside the manifest.
- **Nothing run. No `scancel` from me.** Five Gate-6 prohibitions at `19585b7` live; `C_ML` prohibited; `§3`
  of `CRITERIA-20260811` operative; `M(ii)` `(B)`, magnitude UNMEASURED; unity control authorized/unscheduled,
  trigger = data-only family returns.

*Lane C (PET). Filed with `BEN-424`.*
