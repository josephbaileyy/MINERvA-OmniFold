# Standard P4 lane — mechanical inventory of recorded-but-unchecked fields and named gates

**Why this file exists.** "Records a value, never checks it" and "names a weak check strongly"
have now appeared five times in this chain: `P4_VERIFIER_PASS` (#21), `code_rev`,
`C_syst_eq_retained_plus_active_relerr`, `complete_support_comparison`, and the
full-total-identity overclaim. Repair-5's sweep was **a pass I performed**, and it missed an
item on its own list. So the list is now an artifact produced by a script, checked in, and
re-runnable — not a judgement I assert I made.

**Generator:** the sweep is grep-level over `p4_lib.py`, `p4_evidence.py`,
`p4_validate_active_lateral.py`, `p4_build_components.py`, `p4_project_4d.py`,
`p4_adopt_standard.py`, `p4_check_receipt.py`, `p4_lateral_replace.py` and the three shell
drivers. **113 fields** written into a product with no same-line comparison, and **28 named
gates**.

> **These counts are now GUARDED, not typed** (repair-7 item 4). The document previously said
> 66 fields / 22 gates while its own generator reported 82 / 24, and the pipeline section said
> 22/324 while the tool said 23/326 — the artifact drifted from its generator *inside the round
> that created it*, and the verifier found it rather than the author. Both sweeps now emit a
> machine-readable `summary()`, the result is committed at
> `state/p4-sweep-snapshots.json`, and `tests/test_p4_sweep_snapshots.py` regenerates and
> compares. **Staleness is now a red test on the author's machine instead of a finding on
> someone else's.** The snapshot also names any NEW unchecked field rather than only counting
> them, because counts alone let one appear as another disappears. Update with
> `python3 tests/test_p4_sweep_snapshots.py --update` and commit the diff, so a number change
> lands in review where it can be seen.
>
> **REPAIR-7 ITEM 4 STATUS, checked 2026-08-09 and PARTLY DEFERRED with a reason.** The item was
> "generate the inventory in CI". **This repository has no CI**: no `.github/workflows`, no
> `.gitlab-ci.yml`, no pre-commit config, no Makefile target — verified by `git ls-files`. So the
> literal form is not deferred by choice, it is unimplementable without first standing up CI, which
> is out of scope for this lane and would be a repo-wide decision.
>
> **What IS implemented is the property the item wanted:** the sweeps emit `summary()`, the result
> is committed at `state/p4-sweep-snapshots.json`, and `tests/test_p4_sweep_snapshots.py`
> regenerates and compares on every suite run — so staleness is a red test rather than a silent
> drift, which is the whole point. It has already caught two real drifts it was not written for: my
> own new fields, and a change made by the PET lane entirely (two new shell files moving the
> pipeline corpus 330 → 332).
>
> **What is genuinely deferred:** enforcement for someone who never runs the suite. Today the guard
> binds an author who runs `pytest`; it does not bind a commit. If CI is ever added, the named fix
> is one job invoking `pytest nd-unfolding/tests/test_p4_sweep_snapshots.py`. Recorded here rather
> than closed silently, because "done" and "done in the only form the repo supports" are different
> claims and the second is the true one.
>
> Current snapshot: **113 fields / 25 gates**; pipeline **23 candidates across 337 shell
> files, 0 live**.

### Reading rule: this is a list of SHAPES, and polarity decides (2026-08-09)

Adding the self-declaring rejection marker put three fields on list A
(`publication_gate_rejects_this`, `non_adoptable_reason`, `adoption_requires`) and that is the
right outcome — the sweep should flag them — but only one of the three is even a gate, and it is
not a defect. The distinction the list cannot draw for you:

- A recorded boolean read only for truthiness is a **defect** when its truthy value means *this
  was verified*. The producer writes a literal, the consumer reads a constant, the gate is
  **fail-open**. That was `identities.pure_addition`, and it was the strictest gate in the chain.
- The same shape is **correct** when the truthy value means *refuse this*. A literal that can
  only ever cause a refusal is **fail-closed**. That is `publication_gate_rejects_this`. The
  failure mode worth guarding is not a wrong value but the key going **absent** — which no
  comparison operator on that line would catch either. Its guard is therefore a both-directions
  test (`tests/test_p4_repair.py::NonAdoptableMarker`), which demonstrates that a marked manifest
  is refused *and* that an unmarked one is not refused on that ground.
- Fields ending `_reason` / `_requires` are prose carried for a human reader and gate nothing.
- **A third category, added the same day:** `diagnose_integral_breach` returns
  `n_deviating_bins`, `frac_positive`, `sigma_from_roundoff_bias`, `sigma_from_half` and
  `corr_reldev_vs_central`, and checks none of them — **on purpose**, because the criterion that
  consumes them is pre-specified in prose at `p4_lib.REPRO_RTOL_INTEGRAL` and applied by a human
  in front of a red gate. A measurement produced for a stated decision rule is not an unchecked
  field; it is the input to a check that deliberately does not live in the same function, so that
  the number cannot be re-interpreted by whoever is looking at it. What makes that defensible
  rather than an excuse is that the rule was written *before* any breach and that both of its
  branches are demonstrated against synthetic round-off and a synthetic coherent shift
  (`tests/test_p4_repair.py::IntegralLegIsADiscriminator`). Absent that test it would be exactly
  the pattern this inventory exists to catch.
- **The same category again, 2026-08-09:** `crosscheck_marginal_vs_independent` returns
  `median_abs_rel`, `p90_abs_rel`, `p99_abs_rel`, `max_abs_rel`, `frac_marginal_above`,
  `signed_mean_rel`, `integral_ratio` and `n_over_*pct`, and checks **none** of them. That is the
  specification: Joseph removed the pass/fail on this comparison on 2026-08-09 because it tested a
  proposition the analysis does not assert. The fields are a reported distribution, not a gate, and
  the function's docstring says so. Distinguishing this from a Pattern-A defect is exactly the
  judgement this inventory is for: *a recorded-and-unchecked field is a defect when something was
  supposed to check it.* Here nothing was, deliberately, and the removal is documented at the call
  site in `p4_project_4d.py`.

That test earned its place immediately: it found that `require_adoptable` sat *after* the
input-identity loop in `p4_adopt_standard.py`, so a marked manifest missing any other key died on
a `KeyError` and the refusal never surfaced. The check now runs before the other gates, which is
what its comment had claimed all along.

## The sweep's own two failure modes, stated up front

Both were found by running it, and both matter for reading the table:

1. **It missed uppercase-initial keys on the first run** — the key-literal regex was
   `"([a-z]...)"`, so `C_syst_eq_retained_plus_active_relerr`, `C_combined_eq_syst_stat_ml_relerr`,
   `M_content_sha256` and `M_shape` were invisible. That is *the exact field the verifier caught
   repair-5 missing*, missed a second time by the tool built to stop missing it. Fixed to
   `[A-Za-z]`; the count went 62 → 66. **A mechanical sweep is only as good as its pattern, and
   the pattern needs its own test.**
2. **It is line-based, so it cannot see a check performed in a loop.** Where a consumer does
   `for k in (...): require(ids[k] <= rtol)`, the field name appears only in the tuple and the
   comparison only in the body. Those show as `SWEEP-FP` below and were hand-verified.

---

## A. Findings that are real and actionable

| Field / gate | State | Mark |
|---|---|---|
| **`verifier_crosscheck`** | **FIXED in repair-6 — now enforced.** *(Was: computed, printed as `MATCH`/`DIFF`, and never enforced.)* `p4_evidence.py:313` builds the five booleans against the independently-observed hashes `OBS`, `:325` prints them, and a grep for `need(`/`require(` on it returns **0**. All five could read `DIFF` and the stage still exits 0 with `EVIDENCE-COMPLETE`. These are the bindings the evidence stage exists to confirm. | **FIX — highest priority; new, not on any prior list** |
| `C_syst_eq_retained_plus_active_relerr` | Recorded by the builder; checked by neither consumer; `C_syst` never recomputed from retained + active. A wrong-but-PSD `C_syst` passes. Recomputable since repair-4 began persisting the retained components. | **FIX** (verifier finding 2) |
| `hasTruthOnlyMisses` / `nTruthOnlyMisses` | Presence-only in both `p4_lib.check_merged_metadata` and `p4_evidence.py`. Zero or mutually inconsistent values pass. | **FIX** (verifier finding 5) — requiring `n > 0` and flag/count consistency needs no new physics; the real files already satisfy it |
| `complete_support_comparison` (gate label) | The gate checks presence, shape and a nonzero support trace. Any finite ratio passes, yet it is recorded in the PASS gate list as *complete*. | **FIX** (verifier finding 6) — drop the claim from the name and the receipt, or give the ratio a bound |
| `migration_policy` | Comparison added in repair-5 but made **conditional on optional fields**, so every caller that omits `band`/`selection_migration_abs` keeps the old presence-only behaviour; and zero-migration bands never validate the policy text. | **FIX** (verifier finding 4) — a repair that can be opted out of by omission is not a repair |
| `support_comparison` (recorded value) | The ratio is recorded and never bounded — the value half of the gate above. | **FIX** with the gate |

## B. Sweep false positives — checked, but not on one line (hand-verified)

`active_only_eq_sum5_relerr`, `C_combined_eq_syst_stat_ml_relerr`,
`full_total_residual_eq_stat_plus_ml_relerr` (checked by the `for _k in (...)` loop in the
validator and adopter) · `stat_sha256`, `ml_sha256` (re-verified in `_bound_block`) ·
`source_blobs` (compared in the dirty-source loop) · `full_phase_space`, `use_weights`
(compared by `require_standard_footing`'s loop over `STANDARD_REQUIRED_FOOTING`) ·
`endpoint_mask_equality` (enforced via the `mask_ok` local before being recorded) · `zombie`,
`recovered` (enforced in a compound `need(... and ...)`) · `central_reproduction_rel`,
`central_rel_tol` (bounded inside `check_projection_nonmutation`) · `selection_migration_abs`
(compared in both the producer and the validator) · `log_bkg_mode` (compared against the
declared footing) · `source_commits` (presence is the correct check — the value is an output).

## C. Waived — diagnostics with no declared expected value

Recorded deliberately for a reader, not as claims. Waiving these is only defensible because
none of them appears in a PASS-gate label: `min_eig`, `max_eig`, `n_bins`, `rel_asymmetry`,
`sqrt_tr_active`, `sqrt_tr_support`, `active_traces`, `component_content_hash`,
`manifest_endpoint_hash`, `merged_hash_list_digest`, `hash_list_digest`, `n_reported`,
`all_syst_bands`, `retained_bands`, `replaced_lateral_bands`, `support_family`,
`support_family_sha256`, `axis_edges`, `grid_nbins`, `corder`, `binary_mtime`,
`candidate_keys`, `candidate_total_key`, `M_shape`.

**Waived with an explicit caveat:** `binary_sha256` — cannot be tied to the artifact it
describes (nothing proves which binary produced a 53.8 GB merged input), which is why it now
carries `binary_sha256_semantics` saying so. `candidate_c5*`, `M_content_sha256`,
`component_manifest_sha256` — recorded for a downstream consumer that **does not exist yet**;
they become FIX items the moment anything reads the projection receipt.

## D. Descriptive strings, not claims

`note`, `reason`, `error`, `bkg_mode_basis`, `binary_sha256_semantics`, `component_manifest`,
`merged_receipt_dir`, `stat_cov`, `ml_cov`, `builder`, `evidence_generator`, `footing_evidence`,
`log_bkg_mode_reason`, `log_sha256`.

---

## E. The 22 named gates

Twelve are library functions whose names match their bodies (`check_symmetric_psd`,
`prove_identity`, `check_component_sum`, `require_exact_bands`, `require_exact_endpoint_tags`,
`require_complete_unfold_set`, `require_standard_footing`, `require_candidate_path`,
`check_projection_nonmutation`, `check_full_total_identity`, `check_declared_migration_policy`,
`check_merged_metadata`).

Ten are PASS labels recorded in the validator receipt. Nine are accurate. **One is not:**
`complete_support_comparison` — see section A. `full_total_identity_recomputed` is accurate as
of repair-5 and was **not** before, which is why the label is in this inventory rather than
assumed correct.

---

## E-bis. A THIRD pattern, found while fixing the first two: **a gate nothing calls**

`p4_lib.check_merged_metadata` is a complete, well-tested fail-closed gate — tree completeness,
POT positivity, census counters, native-miss metadata, migration policy — and a repo-wide grep
for callers returns **only its own tests**. `p4_evidence.py` re-implements the same checks
inline with `need()` instead of invoking it.

So it has been exercised solely by fixtures since it was written. Everything repair-5 and
repair-6 "fixed" in it — the migration-policy comparison, the native-miss comparison — improved
a function **that does not run in production**. That is worth stating plainly rather than
letting the round's diff imply a live repair.

This is a distinct failure mode from the other two and belongs on the shared list:

- Pattern A: *records a value, never checks it.*
- Pattern B: *names a weak check strongly.*
- **Pattern C: a gate that is never invoked.** Coverage looks green, the code reads as
  defence-in-depth, and it protects nothing. It is the natural end state of maintaining a
  library gate and an inline copy side by side — the inline copy is what runs, the library copy
  is what gets improved.

**On BEN-046 vs the code (raised in A+, and correct):** `run_p4_standard.sh:41` still contains
`if [[ -z "${P4_VERIFIER_PASS}" ]]`. BEN-046 is about the *runbook's state table omitting a
standing BLOCK*, not about that gate, and A1 is deliberately OPEN because the token gate is
Joseph's human checkpoint — changing it mid-round would alter the instrument being used to
authorise the round. `329d230` was a renumber and touched only prose. **Neither the ledger row
nor the renumber should be read as a repair of #21.**

**Marked FIX, but deliberately NOT in this round:** collapsing the duplication means changing
`p4_evidence.py`'s accumulate-`need()` semantics into `require()`-raises, which changes when the
evidence stage stops and what it reports on a bad input. That is a behavioural change worth its
own commit and its own verifier pass, not a rider on this one. A detection test would be: assert
every `check_*`/`require_*` in `p4_lib` has at least one non-test caller.

## A++. QUEUED — BEN-070 second site, `p4_validate_active_lateral_fps.py:70`

**Found by the PET lane, verified by Joseph, assigned to this lane, and deliberately NOT started
yet** — it is queued behind the receipts/verifier chain so a shared-library edit cannot collide
with a run in flight.

- **Defect:** line 70 bounds the diagonal with an absolute `-1e-30` while lines **66/67/68 of
  the same function** are all relative. Same shape as the `p4_lib.py` instance repair-6 fixed.
- **Severity, measured by Joseph, not assumed:** the PSD check at line 68 has an effective
  threshold of ~`1e-89` at this product's scale, against line 70's `1e-30` — it **subsumes the
  diagonal check by ~59 orders**. **Latent, not exploitable. The adopted FPS lateral is fine.**
  This is the same "redundant behind a live relative check" conclusion the `p4_lib` instance
  reached, now independently confirmed on the FPS product.
- **Why my sweep missed it:** the file's git history is the FPS repair rounds, not this lane's,
  so it fell outside the module list the sweep enumerates. **The sweep's scope was drawn by
  provenance rather than by prefix** — a `p4_`-prefixed file that this lane owns was not in a
  list this lane generated. Third failure mode of the sweep, after lowercase-only keys and
  line-based blindness to loops.
- **When and how:** after the verifier pass, and **with a mutation test**, not as a bare
  one-liner — the guard has to be shown to reject what the absolute bound accepts, at the real
  ~1e-86 scale, the same way `BEN044_AbsoluteToleranceAtRealScale` does.

### The heuristic this third occurrence earns

Three instances now of **a guard written in different units from its immediate neighbours**:
`p4_lib.check_symmetric_psd` (symmetry and PSD relative, diagonal absolute), this FPS twin
(66/67/68 relative, 70 absolute), and BEN-044's origin (`combine_cstat_bkgsub_100rep.py`, where
`max(max_eig, 1.0)` pinned a relative tolerance to an absolute floor).

**Adopt the PET lane's detector: read a validator's checks AGAINST EACH OTHER, not just against
the data.** A single absolute threshold is ambiguous — it might be right for its quantity. A
threshold that is absolute while its *siblings in the same function* are relative is a defect on
sight, because the author demonstrably knew the relative idiom and did not apply it there. This
is cheaper and more reliable than reasoning about scale from first principles, and it is
mechanically checkable: flag any `require`/`need` in a function where some thresholds are
normalised and at least one is not.

**Note it also predicts severity, which is why all three came out "latent".** If the relative
siblings are the *stronger* check, the absolute one is redundant and the finding is hygiene; if
the absolute one is the only check of its kind in the function, it is live. Ask which before
writing the severity down — twice now the first draft overstated it.

## E-ter. Third mechanical sweep: BEN-035's pipeline exit-status trap

Generator: `nd-unfolding/tools_p4_sweep_pipeline_rc.py`, over **330 tracked shell files**. Flags
three shapes -- a pipeline through `tail/head/grep/...` used as an `if` condition, the same in a
`&&`/`||` chain, and one followed by `rc=$?`.

**Result: 23 candidate instances, and every single one is in a file that sets `set -o pipefail`.**
Under pipefail the first failing element propagates, so the shape is benign there. **There are no
live instances in the tracked shell corpus.**

**Which relocates the finding, and is the useful part.** The trap has now bitten five times, and
the most recent -- `selfcheck_receipts.sh` reporting `pass=10 fail=0` beside ten REJECT lines --
was in an **ad-hoc script that was never committed and had no `pipefail`**. All three tracked P4
drivers set it; my throwaway helper did not. So the danger zone is not the reviewed corpus, it is
the scripts nobody commits and nobody sweeps.

**Rule this earns:** *every* shell script sets `set -o pipefail`, including one-off helpers and
anything written into a scratch directory. A sweep over tracked files cannot see the place this
defect actually lives, which is the same blind spot as A++ (a `p4_`-prefixed file absent from a
list drawn by provenance) -- **twice now a mechanical sweep has been correct about what it looked
at and wrong about what it looked at.**

## E-quater. ATTRIBUTION CORRECTION -- the `code_rev == HEAD` defect was a SPEC defect

Repair-6b's commit message records the receipt-gate `code_rev == HEAD` flaw as mine. **It was
not.** Joseph specified "bind the token to the sha256 of a PASS receipt whose `code_rev` matches
HEAD"; I implemented that faithfully, and the flaw is in the specification, not the
implementation. He corrected the attribution himself.

Recording it because **a finding that misidentifies where a defect entered is worth less later**:
the lesson here is about *spec review* -- an equality against a moving repo-wide pointer looks
precise and is a proxy -- not about implementation care, and a future reader tracing "how did this
get in" needs the right answer. The implementation lesson that IS mine is the second one: my
self-check could not fail.

The same spec flaw was **live in the token gate** (`p4_check_verifier_token.py` rule 4) and fixed
before the verifier pass rather than after, because a push between the PASS and stages 4-6 would
have rejected a valid token and wasted the delegate run.

## F. The pattern is REPO-WIDE, not this lane's — folding in BEN-043 and BEN-044

Both were found in the **PET lane on the same day**, independently, and both are the same
family this lane keeps hitting. That is the argument for one shared list rather than a
per-lane one: two lanes rediscovering "a gate that cannot fail" in parallel is a repo
property, not a coincidence.

**`BEN-044` — an absolute tolerance in a ~1e-80-scale problem.** `combine_cstat_bkgsub_100rep.py`
had symmetry tested as `sym_err > 1e-30` absolutely and PSD as
`min_eig >= -1e-9 * max(max_eig, 1.0)`, where `max(..., 1.0)` pins it absolute. Measured
`max|C| = 8.13e-79` — the thresholds sat ~49 and ~68 orders above what they bound, and an
injected asymmetry of half the largest entry left `sym_err = 1.26e-80`, unflagged.

  **Applied here, and it found one.** `p4_lib.check_symmetric_psd` carried
  `require(... np.all(d >= -1e-30))` — a bare absolute literal against a standard-5D diagonal
  near 1e-79. Now relative (`-psd_atol_ratio * max|C|`), with a reintroduction guard that
  greps the lane for bare literals in `require`/`need` calls.

  **Severity, stated honestly: redundant, not exploitable.** For a symmetric matrix
  `min(diag) >= min(eigenvalue)`, so any negative diagonal is already a negative eigenvalue and
  the **relative** PSD check immediately above it rejects the same corruption first —
  demonstrated in `test_but_the_relative_PSD_check_already_rejected_that_matrix`. The literal
  could not fire, but it was never the only line of defence. Recording it the other way would
  be exactly the overclaim these rounds keep catching.

**`BEN-043` — a checkpoint that is not the model that produced the product.** `save_best_only`
plus an `EarlyStopping` that cannot fire (`patience=10`, `epochs=8`) means the in-memory model
at reweight time is the LAST epoch while the file on disk is the BEST epoch; max relative
deviation 0.866 against an aggregate that agreed to 1e-4.

  **Applied here.** Its rule 1 — *a checkpoint is not provenance unless something asserts it
  reproduces the product* — is the same statement as this lane's legacy-attest defect: a
  receipt is not provenance unless something asserts the producer claim is true. Repair-6
  resolves that the same way BEN-043 implies, by making the claim true by construction
  (re-unfold) rather than by adding a guard over a false one. Its rule 3 — *an aggregate
  cross-check cannot detect a per-event defect* — flags `check_support_comparison`, which
  compares **traces**; a per-bin disagreement that preserves the trace is invisible to it. That
  is a second, independent reason section A marks it FIX.

**Cross-lane tally of the family, now seven:** `P4_VERIFIER_PASS` (#21) · `code_rev` ·
`C_syst_eq_retained_plus_active_relerr` · `complete_support_comparison` · the
full-total-identity overclaim · BEN-043's unasserted checkpoint · BEN-044's absolute tolerance
(plus its own two cited precedents, CLM-011's `atol=1e-8` against ~1e-38 cross sections and
BEN-042's normalisation mismatch).

## G. BEN id allocation

**Take new ids from 060 upward.** Two collisions in one day (041, then 044) because both lanes
fetch, both see the same highest id, and both increment. Sequential allocation from a shared
maximum does not work with concurrent lanes. This lane's finding is **BEN-046**; the two
verifier transcripts still say BEN-044 deliberately — rewriting a committed receipt to match a
later renumber would falsify it.

## H. Standing rule this file establishes

**A field may be recorded without being checked only if it appears in section C or D with a
reason. Anything else is a defect.** And a gate label may not claim more than its body does —
`complete`, `identity`, `verified`, `proven` are all load-bearing words.

---

## A+. Contributed by the PET lane, 2026-08-07 — one instance this sweep's patterns cannot see

Added here rather than kept in a separate list, per Joseph's instruction that the "gates that cannot fail"
inventory be repo-wide and shared. Generator:
`docs/orchestration/audit_gates_that_cannot_fail.py` (624 files, seven detectors, each power-tested against
a reconstruction of the real pre-fix source). Full write-up:
`FINDING-20260807-gates-that-cannot-fail-sweep.md`, ledger **BEN-070**.

**Why it is here and not in your table already: this sweep and that one look for different classes.** Yours
finds *recorded-but-not-compared* and *strong-name-over-weak-check*. Mine adds *unreachable trigger*
(BEN-043), *scale-blind absolute tolerance* (BEN-044), *size-as-completeness* (BEN-023) and *tautological
datum* (BEN-039). The instance below sits in a file your sweep reads — it is simply not the shape your
patterns match.

| Field / gate | State | Mark |
|---|---|---|
| **`p4_lib.py:219` diagonal non-negativity** — `require(np.all(np.isfinite(d)) and np.all(d >= -1e-30), "non-finite/negative diagonal")`. Measured on `products/pet/bkgsub/pet_cstat_bkgsub_5d.npz`: diagonal median `3.867e-86`, min `5.510e-102`, max `8.128e-79`. **The `-1e-30` floor is `2.586e+55x` larger than the median**, so a negative variance of `-1e-40` — itself `2.6e+45x` the median magnitude — PASSES. No physically possible negative variance can fail this check. Diagnostic rather than sloppy: the **same function** validates symmetry as `max\|C-C^T\| / max(1e-300, max\|C\|)` and PSD as `ev[0] >= -psd_atol_ratio * abs(ev[-1])`, both correctly relative and one carrying a div-by-zero floor. The idiom was known, used twice, and the third check written in absolute units. Duplicated at `p4_validate_active_lateral_fps.py:70`. | **FIX — new, on no prior list.** One-line: `-1e-30` → a floor relative to `max(abs(d))` or to `abs(ev[-1])`. Left to this lane; a concurrent edit to a shared library during your repair round is the collision CLAUDE.md warns about. | **FIX** |

### A+ reply from the standard lane, 2026-08-07

**The fix has landed here** — `check_symmetric_psd`'s diagonal bound is now
`-psd_atol_ratio * max|C|`, committed in repair-6 before this contribution was merged. We found
it independently the same day, from BEN-044's rule 1, which is a third convergence. Thank you
for leaving the shared library alone; that was the right call and the collision did not happen.

**One correction to the severity, and it is the same mistake I made writing it up.** "No
physically possible negative variance can fail this check" is true of *that line in isolation*
and overstates what it means for the function. For a **symmetric** matrix
`min(diag) >= min(eigenvalue)`, so any negative diagonal is already a negative eigenvalue — and
the PSD check **immediately above it**, which you correctly note is relative, rejects the same
corruption first. I wrote a test to prove the hole was live; the test failed, because the
matrix I built to demonstrate it was caught by the PSD gate. So the correct severity is
**redundant, not exploitable**: a dead bound behind a live one. Worth fixing under rule 1, not
worth recording as an open exposure. Demonstrated in
`tests/test_p4_guard_mutations.py::BEN044_AbsoluteToleranceAtRealScale`.

**The FPS duplicate at `p4_validate_active_lateral_fps.py:70` is deliberately NOT touched by
this lane**, for the reason you gave in reverse: that file is the FPS lane's, its gates are
freshly green, and `CLAUDE.md` is explicit about not mutating across the boundary. Same
redundancy argument should apply there if the surrounding function is the same shape — worth
checking before spending a fix on it.

**Also, and it affects how A1 reads:** `run_p4_standard.sh:41` still contains
`if [[ -z "${P4_VERIFIER_PASS}" ]]` on `main`. That is consistent with A1 being deliberately OPEN, so this
is confirmation rather than a new finding — but the BEN-046 ledger row reads as resolved while the code is
unchanged, and `329d230` touches only prose. Worth one sentence in the row so a later reader does not take
the renumber for a repair.

**Convergent lesson, independently.** This file records that the sweep "missed uppercase-initial keys on the
first run … a mechanical sweep is only as good as its pattern, and the pattern needs its own test." Mine
failed the same way three times: two detectors were silent on their own known instances (`\btol\b` cannot
match inside `psd_tol`, because `_` is a word character), the first sweep printed **0 hits** from a `--root`
that had resolved to a directory containing none of the code, and mention-vs-use made the loudest hits the
ledger prose describing these very defects. Two lanes, two sweeps, the same three traps — which is the
strongest argument yet that the pattern-needs-a-test rule belongs in the shared list and not in either
lane's notes.

**What neither sweep can reach, and where the rest of the family probably lives.** Three historical
instances have no static signature: BEN-032/025 (a check run over a population that cannot exhibit the
defect — a runtime property), BEN-040 (a fail-closed gate that had never returned PASS on real input — needs
execution history), BEN-042 (a normalised quantity compared against an absolute one across two documents).
A coverage harness recording which guards have ever fired in **either** direction on real inputs would find
all three classes at once, and is the higher-yield next step for whichever lane takes it.
