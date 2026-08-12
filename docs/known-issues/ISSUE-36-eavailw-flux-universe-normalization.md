## J28's scope misses a sixth site: `eavailW_covariance.py` divides every flux universe by the CV flux

The J28 fix commit `081ae4a` touches **12 files and `eavailW_covariance.py` is not among them**, and
neither `AUDIT-FINDINGS-20260731.md` nor this file scopes it into J28's blast radius. But it carries
the same defect by the same mechanism:

- `:104` loads `flux_bins` **once**, from the CV histogram `pTmu_reweightedflux_integrated`;
- `:232` passes that same CV array into `extract_cross_section_nd` on **every** call, with no
  per-universe override — contrast a fixed site, `unified_throw_cov_5d.py:67`, which threads
  `d["flux"] if flux is None else flux` precisely so a universe can supply its own `Φu`;
- `:259 def _y_band(sig_u, td_u)` takes weight arrays only — there is no flux parameter to thread;
- `:274-276` runs **all 100 PPFX flux universes** through `_y_band` and forms
  `C_flux = mat_covariance(fX)`, added into `C_syst` at `:277`.

So every flux universe is divided by `Φ_CV` instead of its own `Φu`, which **removes the normalization
spread the flux universes exist to carry** and therefore *understates* `C_flux`. Direction is fixed by
the same identity the re-roll used; magnitude is not, because this is a **code read and has not been
run** — do not quote a number for it. For scale only, the analogous correction in the 5D lane raised
`sqrt_tr_flux_block` by 316.83%.

Nothing quoted today is wrong: `values.tex:53-54` records the (E_avail,W) significances as removed
2026-07-12, and `sec_eavailw.tex:136-138` states compatibility "is not evaluated without the corrected
projected covariance." But that corrected covariance **is** a stated deliverable, and it could not be
built from this script as it stood. Found 2026-08-06 by a fresh-context review of the Step 2
classification and confirmed independently at the mechanism level.

**CODE FIXED 2026-08-06, NO NUMBER PRODUCED — the same footing 081ae4a had for the first five sites**
("the code fix is committed, fail-closed, and mutation-tested … no corrected number exists yet").
`xsec_ew` and `_y_band` now take a `flux` override, and the flux loop resolves a per-universe table via
`flux_universe.resolve_flux_ratio_table` — reusing the helper 081ae4a already shipped rather than
inventing a mechanism. `flux=None` still means the CV flux, which is **correct** for the CV and for
every knob band (a knob does not move the flux integral) and wrong only for a flux universe; same
`d["flux"] if flux is None else flux` shape as `unified_throw_cov_5d.py:67`.

**Fail-closed, no silent CV fallback:** `resolve_flux_ratio_table` refuses to run when neither a bank
nor a `--flux-universe-file` is usable, and `_validate_ratio_table` separately rejects an all-ones table
as "the J28/Task #70 bug, not a valid table". Reproducing the old behaviour now requires an explicit
`--allow-cv-flux-universes`, which prints that it understates `C_flux`.

Guarded by `tests/test_flux_universe_fix.py::EavailWFluxBlockIsPerUniverse` — static, because this
module imports ROOT and reads a 142 GB omnifile, and **proved to have power**:
`test_the_prefix_source_would_fail` reconstructs the pre-fix source and requires all three guards to
fire. The guards use unittest assertions rather than bare `assert`, so `python -O` cannot silently empty
them. `eavailW_covariance.py` was also added to that file's `SyntaxOfTouchedFiles` list.

**Still open:** no `(E_avail,W)` covariance has been rebuilt with the fix — that needs the cluster and
belongs with the `M C_5D M^T` projection `OPEN_ITEMS.md` requires. The script is bound by no receipt or
gate, so this changed no hash binding (verified: ALL BINDINGS INTACT).

