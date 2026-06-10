# Known issues, bugs, and code debt — INDEX

One line per issue, pointer to the canonical home for detail. **This file is an
index, not a copy** — update the pointer target, not this file, when an issue
evolves. Add new issues here the moment they are found, so they never get
buried in run-log prose.

## Open code debt

| # | Issue | Status | Detail lives in |
|---|---|---|---|
| 1 | **N-D driver no-`--use-weights` mode is globally low by pot_scale** (unscaled unit MC weights into OmniFold vs POT-scaled binning weights). Exact global correction applied where used. Fix in driver carefully — closure-without-weights is internally consistent as-is. | OPEN (workaround in place) | `VALIDATION_LEDGER.md` (2026-06-09 FPS entry); `nd-unfolding/fps_pilot_compare.py` header |
| 2 | **Coverage 200-toy ROOTs not on disk** — headline coverage numbers documented but not regenerable from the checkout (only the 20-toy stage-1 summary survives). | OPEN (optional regen) | `VALIDATION_LEDGER.md` (Validation Diagnostics) |
| 3 | **PET lateral band is a frozen-cloud transfer**, not per-lateral re-inference (laterals subdominant ~4%). | OPEN (deferred) | `docs/OPEN_ITEMS.md` item 3 |
| 4 | **(E_avail,W) lateral block is transferred from 4D**, spread over W by the CV shape (W-resolved laterals need reco re-inference). | OPEN (deferred) | `docs/OPEN_ITEMS.md` item 4 |
| 5 | **Low-p∥ MINOS sum-ratio gradient persists** after the IsMinosMatchMuon fix (0.6 at p∥=1.5–2 rising to ~1.0 above 20 GeV/c) — likely MINOS geometric acceptance/range-out the MINERvA-101 path does not implement. Matters more for FPS (p∥<1.5 region). | OPEN (understood, not fixed) | `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` §IsMinosMatchMuon |

## Resolved traps that WILL bite again if forgotten

| # | Trap | Detail lives in |
|---|---|---|
| 6 | **Never bare-`hadd` a `_universes_full` omnifile** — ROOT 100 GB TTree rollover aborts mid-merge leaving a partial missing the data+bkg trees. Use `2d-unfolding/uq/hadd_universes_full.py`. | `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` §Event-loop workflow |
| 7 | **Never feed the event loop a combined MEFHC manifest** — it silently applies the first playlist's flux to all 12. Run per playlist, merge after. | same |
| 8 | **`hadd` sums `TParameter<double>`** — POT summing across playlists is correct; a per-file nucleon count would be inflated 12×, hence the fixed tracker constant 3.2353e30. | same |
| 9 | **Pre-2026-04-25 event-loop outputs** use the IsMinosMatchMuon stub (≈10% background) — regenerate before comparing to paper numbers. | same |
| 10 | **eavailW completeness double-count** (2026-06-09, FIXED): OmniFold step-2 already efficiency-corrects; an extra reco-pass completeness division inflated the data ~2×. Caught by the marginal self-validation gate — keep that gate in any new covariance script. | `docs/FUTURE_DIRECTIONS.md` tombstone → `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` (2026-06-09) |
| 11 | **Stale PET `ExtraEnergyClusters_*` input** (FIXED): wrong, mostly-empty branch; point-cloud chain rebuilt from `CVUniverse::GetRecoClusters()`. | `VALIDATION_LEDGER.md` (Known Audit Findings) |
