# FINDING 2026-08-28 — what the polishing pass did not touch, and why

Companion to the eight `[polish]` commits on `polish/20260828`. Those commits removed what could be
shown dead. This records the three things that looked like findings and dissolved on inspection, and
the fourteen that are real but are **not polishing work**, so that nobody re-derives either set.

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

**Reads as a defect, not as cruft — escalate rather than delete.**

| site | why it is suspicious |
|---|---|
| `docs/orchestration/whose_row.py:787` | `discovered = True` is set and never read, inside a live pre-commit check. A flag nobody reads is the shape of a check that does not check. |
| `nd-unfolding/pet/pet_vs_gbdt_uncertainty.py:193` | `C_pet_tr = pet_vars["transferred"]` carries the comment *secondary cross-check (GBDT-transferred lateral)*. The cross-check is set up and never performed. |
| `nd-unfolding/unified_throw.py:317,318` | `sig_ptbin` and `td_ptbin` are digitized into pT bins and never applied. |
| `nd-unfolding/unified_throw.py:375` | `cv = np.load(...)` opens the CV archive and drops it. |
| `nd-unfolding/pet/step1_increment_trajectory.py:225` | `w_truth_raw` is read, indexed by `imc`, and discarded in a trajectory step. |

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
