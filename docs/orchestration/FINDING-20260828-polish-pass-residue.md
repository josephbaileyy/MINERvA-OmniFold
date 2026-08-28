# FINDING 2026-08-28 — what the polishing pass did not touch, and why

Companion to the `[polish]` commits on `polish/20260828`. Those commits removed what could be shown
dead. This records what looked like a finding and dissolved on inspection, what is real but is **not
polishing work**, and one technique the skill prescribes that this repository defeats — so that
nobody re-derives any of them.

Sections A and B were written after the first eight commits; the corrections inside A, and section D,
were added on 2026-08-28 after the held findings were read rather than inferred.

## A. Fourteen F841 findings held back deliberately

`ruff F841` reports 30 unused locals. Nineteen lines were removed, clearing sixteen findings once the
cascades are counted. The remaining fourteen all have right-hand sides that *do something*, so deleting
the binding is not separable from deleting the effect, and several read as latent defects rather than
cruft. A defect does not belong in a `[polish]` commit.

**Side effect in the call — the binding is dead, the call is not.**

| site | what the right-hand side does |
|---|---|
| `nd-unfolding/pet_conv_check_5d.py:71,73` | `report(...)` prints the tier summary |
| `nd-unfolding/tests/test_reconcile_gate5_family.py:531,1028,1181` | `_family(root, N)` builds the fixture family under test |
| `nd-unfolding/tests/test_pet_bkgsub_input.py:140` | `np.load(...)` asserts the reference archive is present |
| `docs/orchestration/test_generate_live_state_carry_forward.py:388` | `tempfile.TemporaryDirectory()` is the context manager |
| `docs/orchestration/usagectl.py:716` | `strict_int(...)` validates and raises on bad input |

For these the correct edit is to drop the name and keep the call, one site at a time, by someone who
can say what each call is for. Mechanical removal would delete printed output, fixtures, and an input
validation.

**Read as defects, escalated rather than deleted — and all five were read on 2026-08-28. NONE IS A
DEFECT.** The escalation was right; the suspicion was not. One entry below was affirmatively false,
which is why the corrections are recorded per-site rather than as a single retraction.

| site | what it looked like | what it is |
|---|---|---|
| `docs/orchestration/whose_row.py:787` | `discovered = True` set and never read inside a live pre-commit check — the shape of a check that does not check. | Redundant, not blind. `discovered` can only ever be `True` where it would be consulted: `files` is non-empty whenever the caller named files, so the `if not files:` block below is reachable **only** in discovery mode, and its messages are already correct for that mode. Dead binding. |
| `nd-unfolding/pet/pet_vs_gbdt_uncertainty.py:193` | `C_pet_tr = pet_vars["transferred"]`, commented *secondary cross-check (GBDT-transferred lateral)*, with the cross-check never performed. | **FALSE, and the correction matters more than the finding.** The cross-check *is* performed: line 214 computes `pet_fr_var = {nm: frac_unc(C, ...) for nm, C in pet_vars.items()}` over every variant including `transferred`, line 226 folds it into `med_pet_variants`, and line 239 writes `median_frac_pet_transferred` into the output record. Only the named local is redundant. |
| `nd-unfolding/unified_throw.py:317,318` | `sig_ptbin` and `td_ptbin` digitized into pT bins and never applied. | Orphaned by a migration, not a missing step. Flux is applied per universe, not per event: `flux_thrown = flux0 * fr[k]` at line 332 is the live mechanism and needs no per-event bin index. Dead bindings. |
| `nd-unfolding/unified_throw.py:375` | `cv = np.load(...)` opens the CV archive and drops it. | Dead binding whose **call is not dead**: `do_combine` takes its reported mask from the frozen ROOT CV at `args.cv`, so the `np.load` is a leftover, but removing it would silently relax the requirement that `cv.npz` exist. Same class as the `np.load` presence assertions in the table above; it stays until someone can say whether that precondition is wanted. |
| `nd-unfolding/pet/step1_increment_trajectory.py:225` | `w_truth_raw` read, indexed by `imc`, and discarded in a trajectory step. | The script measures the reco leg only — over twenty `mean_w_reco` quantities and no truth-leg quantity anywhere, which its own module docstring states. Dead load. It is also a **hash-pinned producer** (`gate6-leg0-tier-calibration-prepared-20260814.json` and `sbatch_gate6_leg0_tier_calibration_array.sh`), so it may not be edited at all. |

Three of the five — `whose_row.py:787`, `pet_vs_gbdt_uncertainty.py:193`, and
`unified_throw.py:317,318` — have effect-free right-hand sides and were removed as ordinary dead code
once this was established. The other two stay for the reasons in their rows.

**Removed, but worth a second look.** `2d-unfolding/uq/analyze_uq.py` computed `pt_cov` and `pz_cov`
in *both* branches of an `if N > 1` and used neither. The deletion is behaviour-neutral and is in the
pass. That a UQ script builds two covariance matrices and discards them is not.

## B. Three findings from the 2026-08-28 audit that dissolved on inspection

Recorded because each was asserted in `POLISH_AUDIT_20260828.tmp.md` before it was checked, and an
audit finding withdrawn silently is one somebody re-files next quarter.

1. **`nd-unfolding/launcher_argv_probe.py:574` — "the old PATH shims" is not an iteration label.**
   Read in context it describes a *runtime* transition: sourcing `setup_salloc_env.sh` replaces PATH
   shims with shell functions, and the probe asserts the functions survived. It narrates what the
   activation does, not what an edit did. No change.

2. **`nd-unfolding/bkg_channel_split.py:39` — "a pre-change file" resolves two lines up.** The
   docstring names the 2026-07-04 C++ change immediately above. A reader with only the repository can
   cash the reference out, which is the whole test. No change.

3. **`docs/orchestration/VERDICT-20260825-gate2-k0-rehearsal-nine-clauses.md` carries no personal
   path.** The audit reported it alongside the OI-126 probe. Its one match is `.../scratchpad/wt-mutate`
   — already elided, no name, no home directory, no session id. The audit's grep pooled three patterns
   and attributed the probe's leak to both files. Only the probe leaked, and that is fixed.

## C. The encapsulation finding is withdrawn: `_xsec_for_weights` is a seam, not a private

The audit proposed promoting `compare_unified_throw._xsec_for_weights` to a public name, with
`unified_throw_cov.py:73` and `pilot_cv_check_4d.py:17` as encapsulation violations. Grepping the
tree before renaming — the step that decides the rewrite — shows the underscore is not marking a
private:

- `unified_throw_cov_5d.py:89` assigns `base._xsec_for_weights = _xsec_for_weights_5d`. The name is a
  documented monkeypatch point for the 5D td_W-aware kernel.
- `tests/test_uq_remediation.py` swaps `utc._xsec_for_weights` for a fake at six sites and restores it
  in the `finally`.
- `tests/test_flux_universe_fix.py:610,672` matches the **string literal** `"_xsec_for_weights"`: a
  KERNELS table keyed on it, and an AST walk asserting `getattr(n.func, "id", None) ==
  "_xsec_for_weights"`. An alias would not satisfy this; the call sites themselves must keep the name.

So the name is load-bearing in three separate mechanisms, and nothing is encapsulated by it — every
consumer is meant to reach it. Renaming would break a structural test to satisfy a naming convention.
`_engine_reweighter` is the same shape with a heavier constraint: four of its six importers are
hash-bound producers under `docs/orchestration/state/`.

If anything is owed here it is a docstring on `_xsec_for_weights` stating that it is the patch point
and that a test matches its name, so the next reader does not try this rename again. That is Category 3
work and needs the eyes-driven pass, not a mechanical one.

## D. Unreachable branches: the coverage technique does not transfer here

`code-polishing` Category 4 says to find unreachable branches by reading a coverage report for
branches with zero hits. The previous pass could not run one. It was run on 2026-08-28 —
`pytest --cov --cov-branch` over the whole tree, 2,794 passed, 47 failed, 3 skipped in 7 m 38 s — and
the report does not answer the question.

| measurement | value |
|---|---|
| non-test source modules of ≥40 statements | 187 |
| of those, **0 % covered** — no test touches them at all | **93** |
| of those, ≥80 % covered, where a never-taken arm is evidence of anything | 23 |
| never-taken branch arms inside those 23 | 266 |
| mechanically classifiable as `__main__` guards, empty-input defences, error paths, always-entered loops | 148 |
| remaining candidates needing a human read | 118 |

Twelve of the 118 were sampled at random and read: `if n:`, `if index is None:`,
`if len(parts) != 3:`, `if declared < RECEIPT_SCHEMA_SURFACE or declared > RECEIPT_SCHEMA_CURRENT:`
and eight of the same shape. **Zero were unreachable**; every one is a production path that no test
exercises.

That is the structural reason, not a sampling accident. Half this tree is analysis scripts that no
test imports, so their zero coverage measures test exposure rather than reachability; and in the
covered half, the uncovered arms are the error and edge paths tests characteristically skip. Reading
the 118 would be a test-coverage audit wearing a dead-code audit's clothes.

**The by-product is worth more than the search was.** 93 source modules of non-trivial size have no
test coverage at all. That is a real finding, it is not a polishing finding, and it is recorded here
so that the coverage run does not have to be repeated to rediscover it.
