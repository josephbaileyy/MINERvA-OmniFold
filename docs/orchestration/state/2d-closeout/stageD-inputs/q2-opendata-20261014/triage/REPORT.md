# Triage: does the older 1A processing bias the 2D result? (2026-10-14)

**Answer: NO MATERIAL BIAS EXPECTED. Confidence: high.**

The older 1A processing differs from the current release only outside our selection. Inside it, the selected events
and their kinematics are the same in both copies, for Data and for MC. Re-downloading 1A would change its selected
yield per POT by −0.9 × 10⁻⁵ in Data and −1.8 × 10⁻⁵ in MC. 1A is about 8.8% of the data POT, so the effect on
the combined result is of order 10⁻⁶.

**CITABLE FOR:**
- the event-loop branch audit;
- the full 1A old-against-current comparison of the selected samples, all 253 Data and all 41 MC files;
- the per-playlist yield and proxy comparison.

**NOT CITABLE FOR:**
- an unfolded result;
- any systematic;
- the playlist spread noted in §4, which is a separate observation and is not assessed here.

| field | content |
|---|---|
| `Context` | [`../REPORT.md`](../REPORT.md) (Q2): our 1A, MC and Data, predates MINERvA's 2026-01 re-release and has fewer MINOS-matched reco muons |
| `Who` | A Claude Opus 5.5 subagent of the paper-tighten lane (director) measured this. The director checked `runEventLoopOmniFold.cpp:1701, 1713` at `origin/main` and the cluster `CVUniverse.h:113` (`isMinosMatchTrack == 1 && <ok_branch> == 1`). The director also checked that `yields.json` 1A matches §3 (`data_per_1e19` uses the 357,701 in-phase-space rows; all rows number 360,123) |
| `Compute` | No Slurm job; 0 node-h. Login-node reads; the current release was read over xrootd |
| `Evidence` | [`scripts/`](scripts/), [`outputs/`](outputs/) (`agg_full.json`, whose bare file names were expanded to their full `/pscratch` source paths for the receipt checker; the cluster original has sha256 `239781779f63b8aeeb911421fffd01066d005774ca5e497078cc319c15de79b8`; `yields.json`, file pairs for Data run 6133 and MC run 110001). The full scan is on the cluster at `/pscratch/sd/j/josephrb/tmp-1a-triage-20261014/` |

## 1. Code: which branches decide the selection

Citations are to `runEventLoopOmniFold.cpp` at `b737ed58`. MAT and MAT-MINERvA were read from the cluster checkout,
MAT-MINERvA at `50d76314` and MAT at `35097b65`.

- **MINOS match.** `:1713` calls `reco::HasMINOSMatch`, which goes to `CVUniverse.h:107-114`:
  `isMinosMatchTrack == 1 && MasterAnaDev_minos_trk_is_ok == 1`.
  - `isMinosMatchTrack` exists in both schemas and is identical in both copies.
  - The branches that changed, `muon_is_minos_match_track` and `truth_reco_isMinosMatchTrack`, are never read.
- **Muon kinematics** (`MuonFunctions.h:57-136`):
  - momentum from `MasterAnaDev_leptonE` and `MasterAnaDev_minos_trk_p`;
  - angle from `muon_thetaX/Y`;
  - sign from `minos_trk_qp`.

  `MasterAnaDev_muon_P`, the branch holding the −9999 values, is not read anywhere in the build.
- **Flux.** Only the truth branches `mc_incomingE` and `mc_incoming` are read, together with MAT's flux files.
  `SetNFluxUniverses(100)` (`:1701`). No `mc_wgt_ppfx1_*` or `mc_wgt_Flux_*` branch is read.
- **MINOS-efficiency weight** (`MINOSEfficiencyReweighter.h:29-38`). It reads `minos_trk_p`, `numi_pot`,
  `batch_structure` and `reco_vertex_batch`. All of them, and every truth branch the CV weight uses, are identical on
  MC run 110001.

## 2. Selected samples, old against current (all 1A files)

The production cuts, applied outside the event loop, reproduce production exactly:
- Data: 360,123 rows;
- MC: 1,789,459 rows (1,736,833 signal + 52,626 background);
- POT: matches.

| | Data, old → current | MC, old → current |
|---|---|---|
| selected | 360,123 → 359,967 | 1,789,459 → 1,790,483 |
| POT | 8.9728e19 → 8.9689e19 | 4.0693e20 → 4.0717e20 |
| selected per POT | −0.0009 % | −0.0018 % |
| events where `minos_trk_is_ok` differs, inside the fiducial volume | 34 (663,646 overall) | 0 |
| selected in one copy only, among joined rows | 12 / 10 | 0 / 0 |
| identical kinematics, among events selected in both | ≥ 99.95 % | 100 % |
| `muon_P` = −9999 among the old copy's selected events | 0 | 0 |

**Old Data is degraded the same way as old MC, and only outside the selection.** For example, in Data run 6133:
- `minos_trk_is_ok` is true for 3,066 events in the old copy against 4,349 in the current;
- 28.7% of the old copy's events have `muon_P` = −9999;
- 704 events are selected in both copies, with bit-identical kinematics.

The remaining differences, about 0.1% of rows, come from subruns that were added or dropped together with their POT.

## 3. Per-playlist yields (May per-playlist event-loop outputs)

| | 1A | 1B–1D |
|---|---|---|
| Data per 10¹⁹ POT (in phase space) | 39,865 | 40,002–40,060 (falling to 36,864 by 1P) |
| MC reco per 10¹⁹ POT | 35,557 | 35,620–35,744 |
| efficiency S/T | 0.636 | 0.637–0.639 |

1A is not an outlier in Data, in MC, or in their ratio.

## 4. Rough per-playlist proxy (not an unfold)

The proxy is R = (D/POT_d − B/POT_mc) / (S/POT_mc), bin by bin on a 10 × 10 (p_T, p_∥) grid. It carries Data and
MC-signal statistics only, and no systematics.

- **1A against the rest:** R(1A) = 1.1250 ± 0.0019, against 1.1239 for the other 11 combined (ratio 1.0009).
- **Leave-one-out:** across the 12 playlists the leave-one-out ratios span 0.969–1.062, with 1A near the middle.
- **Shape:** 1A's shape χ² against the rest is 119.5 for 86 bins; the other playlists range from 88 to 391.

**Separate observation, not assessed here.** R varies across playlists from about 1.09 (1G/1L/1M) to 1.19 (1O/1P).
That spread is unrelated to 1A.

## 5. Remedy, not done and not needed for the result

Re-download 1A at the current release:
- 41 MC files, 0.879 TB;
- 253 Data files, 85.1 GB.

That is about 0.96 TB in all, followed by a re-run of the 1A event loop. The expected change is about 10⁻⁵ on 1A.
The reason to do it would be provenance only: a single processing across all 12 playlists.

## 6. Limits

- No per-bin old-against-current histograms were stored for the unmatched rows.
- The beam-angle offset is omitted from the re-applied cuts. This does not affect the comparison, and the counts
  still equal production.
- MAT was read from the cluster checkout. It is not vendored in the repo.
