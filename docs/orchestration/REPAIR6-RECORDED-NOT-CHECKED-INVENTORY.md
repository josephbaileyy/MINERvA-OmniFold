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
drivers. **66 fields** written into a product with no same-line comparison, and **22 named
gates**.

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
| **`verifier_crosscheck`** | **Computed, printed as `MATCH`/`DIFF`, and NEVER enforced.** `p4_evidence.py:313` builds the five booleans against the independently-observed hashes `OBS`, `:325` prints them, and a grep for `need(`/`require(` on it returns **0**. All five could read `DIFF` and the stage still exits 0 with `EVIDENCE-COMPLETE`. These are the bindings the evidence stage exists to confirm. | **FIX — highest priority; new, not on any prior list** |
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
