# EVIDENCE 2026-09-19 — five of `C_Z`'s 45 bands are SEED-PINNED, and the offset hook cannot reach them

**CITABLE FOR:** the measurement below, and the scope limit it places on any cause-3 grade.
**NOT CITABLE FOR:** any grade, adoption or authorization. It changes no criterion and no boundary.
**No compute was spent** beyond metadata reads and one diagonal sum.

## 0. The finding, in one paragraph

The cause-3 campaign varies `MNV_EST_SEED_OFFSET` across the seven hooked launchers and measures how
far `C_Z` moves. **Five of `C_Z`'s 45 bands cannot move, because the hook does not reach the code
that produces them** — and that is deliberate, with a stated reason, in a place the campaign design
never touched. So a MET result is a statement about **~93% of the trace**, not about all of it, and
this record is what makes the remaining ~7% visible rather than silently absorbed.

## 1. Which bands, and where `z_build` gets them

`z_contract.LATERAL_BANDS` = **`BeamAngleX`, `BeamAngleY`, `MuonResolution`,
`Muon_Energy_MINERvA`, `Muon_Energy_MINOS`** — the detector and muon families.

`z_build` reads those five from the **`active`** source as `hCov_active5d_<band>`, *not* from the
`support` family. `support` supplies the 13 vertical and 27 residual bands only. The five active
bands are P4's **replacement** for the support family's versions —
`p4_build_components.py` records them under `replaced_lateral_bands`.

## 2. Where the five come from, and why they are pinned

`p4_build_components.build_active_bands` builds each band from **ten endpoint unfolds** in a
**hardcoded, non-member-scoped** directory:

```python
UDIR = "active_universe_5d/standard/unfolds"          # p4_build_components.py:66
```

Those unfolds are produced by `run_p4_unfold_std.sh`, whose invocation carries a **literal seed**:

```
--iters 5 --use-weights --estimator lgbm --seed 42 --bkg-mode ...   # run_p4_unfold_std.sh:111
```

with the script's own reason at `:6` — *"unfold (NO --universe), FIXED --seed 42 (MAT +/- cancels
CV)."* **Pinning the same seed on both MAT endpoints is what makes the endpoint difference a
systematic shift rather than a shift convolved with estimator noise.** It is a property of the
estimator's design, not an oversight.

## 3. The hook's reach, measured over the whole chain

`MNV_EST_SEED_OFFSET` occurrences, counted file by file:

| file in the active-lateral chain | `MNV_EST_SEED_OFFSET` | literal `--seed 42` |
|---|---:|---:|
| `run_p4_standard.sh` | **0** | 1 |
| `run_p4_unfold_std.sh` | **0** | 2 |
| `run_p4_merge_audit_std.sh` | **0** | 0 |
| `p4_evidence.py` | **0** | 0 |
| `p4_build_components.py` | **0** | 0 |
| `run_active_lateral_unfolds_interactive.sh` (retired predecessor) | **0** | 2 |

**Zero, everywhere.** The offset hook is structurally incapable of reaching these five bands.

⚠ **This is not a contradiction of `DETERMINATION-20260818` item 7 ruling (a)** — *"the LATERAL leg
joins g1 at 42+k"*. That ruling put `unfold_nd_omnifold_unbinned` on the hook **through
`sbatch_unfold_5d_detector_bkgaware_gpu.sh`**, the detector sweep arm, whose outputs flow into the
`support` family. The support family's lateral bands **do** vary with the offset. They are then
**replaced** by P4's pinned versions before `C_Z` is assembled. Two different productions of the
same five families; the campaign varies one and `C_Z` uses the other.

## 4. How much is pinned — measured, not estimated

Diagonal sums read from
`active_universe_5d/standard/candidate/std_final5_candidate.root`, against the pilot receipt's
`inflation.sqrt_tr_after` for `z-cv.npz`:

| quantity | value |
|---|---:|
| `√Tr` of the assembled `C_Z` (cv) | `5.674201e-38` |
| `√Tr` of `hCov_active5d_total` | `1.474286e-38` |
| **share of `√Tr`** | **`0.2598` — 26.0%** |
| **share of the trace** | **`0.0675` — 6.75%** |

| band | `√Tr` | share of the active trace |
|---|---:|---:|
| `Muon_Energy_MINOS` | `1.1294e-38` | `58.7%` |
| `Muon_Energy_MINERvA` | `9.3603e-39` | `40.3%` |
| `BeamAngleY` | `9.4117e-40` | `0.41%` |
| `MuonResolution` | `8.6495e-40` | `0.34%` |
| `BeamAngleX` | `7.3903e-40` | `0.25%` |

**So a cause-3 MET result covers `93.2%` of `Tr C_Z` and is silent about the other `6.75%`**, which
is dominated by the two muon-energy bands.

## 5. What follows, and what does NOT

- **The campaign proceeds unchanged.** Both members read the same `active` source, which is what
  the estimator produces **at any offset**. Using it is faithful execution, not an omission of
  something that would otherwise have varied.
- **The grade's scope is narrower than "the estimator seed does not move `C_Z`"** and must be
  read as *"…does not move the 40 bands the hook reaches, plus `C_stat`, `C_ML` and the throw
  term — 93.2% of the trace."*
- **Putting the five on the hook is a MATERIAL CHANGE TO THE ESTIMATOR and is RESERVED.** It would
  mean unpinning `--seed 42` in `run_p4_unfold_std.sh`, against that script's own stated reason,
  and it would change what the MAT ± endpoint difference measures. **It is not this lane's act, it
  is not attempted, and it is routed to Joseph.**
- **`p4_build_components.py`'s `UDIR` is hardcoded**, so there is no member-local `active` even if
  the seed were unpinned. Both would have to change together.

## 6. Pinned executably

`nd-unfolding/tests/test_lateral_bands_are_seed_pinned.py` asserts the band list, the zero-hook
census over all six files, the literal seed, the hardcoded `UDIR`, and that `z_build` really does
take the lateral bands from `active` — *"if it read them from `support`, they WOULD vary"*. Its
failure message says explicitly that a change here is **not a test failure to silence**: it means
this limitation is obsolete and must be withdrawn, or something else now reads the variable.

**Co-Authored-By: Claude Opus 5 (1M context)**
